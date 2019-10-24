import open3d as o3d
import json
from multiprocessing import Process, Queue, Lock, Array, Value
import OctreeFormatTools as oft
from FrustumManager import FrustumManager

# preparing shared object
torender = Queue()
todelete = Queue()
toload = Queue()
loaded = Queue()
picked = Queue()
cached = Queue()
mvp = Array('d', range(16))
mvp_sem = Value('i', 0)

# mvp (model * vie * projection matrix) lock
mvp_lock = Lock()

####################### LOADER #######################

def loader(octreedir):
    nl = oft.NodeLoader(octreedir)
    loaded.put(nl.load_root().points)
    lru = oft.LRU()

    while True:
        if not toload.empty():
            id = toload.get()

            if lru.exist(id):
                loaded.put(lru.extract_node_points(id))
            else:
                loaded.put(nl.load_node_full_addr(id).points)

        if not cached.empty():
            lru.store_node(cached.get())

####################### TRAVERSAL #######################

def traversal(octreedir, mvp, mvp_sem, max_nodes):
    def load(id):
        toload.put(id)
        in_loading.append(id)
        activate(id, visroot)

    def add(node):
        torender.put(node)

    def remove(node):
        todelete.put(node.id)

    def remove_branch(r, rendered_nodes):
        remove(r)
        r.deactivate()
        rendered_nodes -= 1
        for i in range(len(r.links)):
            if r.links[i].active:
                rendered_nodes = remove_branch(r.links[i], rendered_nodes)

        return rendered_nodes

    def get_visnode(id, r):
        for i in range(len(r.links)):
            if r.links[i].id == id[:len(r.links[i].id)]:
                if len(id) == len(r.links[i].id):
                    return r.links[i]
                else:
                    return get_visnode(id, r.links[i])

        return None

    def activate(id, r):
        for i in range(len(r.links)):
            if r.links[i].id == id[:len(r.links[i].id)]:
                if len(id) == len(r.links[i].id):
                    r.links[i].activate()
                else:
                    activate(id, r.links[i])

    # add or remove nodes to the torender queue. According to frustum values and LOD engine
    def manage_hierarchy(rendered_nodes):
        ids_to_evaluate = []
        bb_to_evaluate = []
        bb_visibility = []

        # function for file ids_to_evaluate list with candidate nodes
        def modify_nodes(r, rendered_nodes):
            v = 0

            # calculate how many bb are completely visible
            for n in r.links:
                if fm.bbox_in_frustum(bbman.id_to_bb(n.id)) == 2:
                    v += 1

            for n in r.links:
                bb = bbman.id_to_bb(n.id)
                visible = fm.bbox_in_frustum(bb)
                dist = fm.dist_from_near(bb.get_midx(), bb.get_midy(), bb.get_midz())

                if visible > 0 and (v <= 0.4 * len(r.links) or dist <= bb.get_radius()) and v != len(r.links) and not n.active:
                    ids_to_evaluate.append(n.id)
                    bb_to_evaluate.append(bb)
                    bb_visibility.append(visible)
                elif n.active and visible == 0:
                    remove(n)
                    n.deactivate()
                    rendered_nodes -= 1
                elif n.active and v == len(r.links):
                    rendered_nodes = remove_branch(n, rendered_nodes)

                rendered_nodes = modify_nodes(n, rendered_nodes)

            return rendered_nodes

        rendered_nodes = modify_nodes(visroot, rendered_nodes)

        # iterate over all nodes to evaluate, get the nodes that has max priority (radius * visibility * (1/distf_from_near)), extract and load this node
        # TODO bisognerebbe verificare se ci sono nodi attivi che hanno una priorità minore di nodi da caricare
        # TODO se questo avviene e la soglia di nodi blocca il caricamento, è necessario rimuovere i nodi con meno priorità ed aggiungere quelli con priorità maggiore
        while len(ids_to_evaluate) > 0 and rendered_nodes<max_nodes:
            priority = -1
            tl = 0

            for i in range(len(ids_to_evaluate)):
                if (bb_to_evaluate[i].get_radius() * bb_visibility[i] * (1 / fm.dist_from_near(bb_to_evaluate[i].get_midx(), bb_to_evaluate[i].get_midy(), bb_to_evaluate[i].get_midz()))) > priority:
                    priority = bb_to_evaluate[i].get_radius() * bb_visibility[i]
                    tl = i

            id = ids_to_evaluate.pop(tl)
            load(id)
            bb_to_evaluate.pop(tl)
            bb_visibility.pop(tl)
            rendered_nodes += 1

        return rendered_nodes

    ###################################################
    # load cloud info from json file
    with open(octreedir + "cloud.json", "r") as infofile:
        info = json.load(infofile)
        bbman = oft.BBManager(oft.BoundingBox(info['minx'], info['miny'], info['minz'], info['maxx'], info['maxy'], info['maxz']))

    # check if classification is present
    classes = None
    if "c" in info['structure']:
        with open(octreedir + "classes.json", "r") as classfile:
            classes = json.load(classfile)

    # waiting the load of root node and then add it to the visualizer
    while loaded.empty():
        pass
    visroot = oft.VisNode('r', loaded.get())
    add(visroot)
    # populate the hierarchy
    visroot.links = oft.gen_hierarchy(octreedir).links
    visroot.activate()

    fm = FrustumManager()
    in_loading = []
    rendered_nodes = 1

    # waiting until mvp (model * view * projection, matrix) values are loaded
    while mvp_sem.value == 0:
        pass

    while True :
        # update frustum values
        mvp_lock.acquire()
        try:
            fm.update_frustum(mvp)
        finally:
            mvp_lock.release()

        # arrange nodes according to the values of frustum
        rendered_nodes = manage_hierarchy(rendered_nodes)

        # add to visualizer one loaded node, only if is still active
        if not loaded.empty():
            vn = get_visnode(in_loading.pop(0), visroot)
            if vn.active == True:
                add(oft.VisNode(vn.id, loaded.get()))
            else:
                loaded.get()

        # check if classifications are found
        if classes is not None:
            while not picked.empty():
                id = picked.get()
                if id == -1:
                    print("Nessun punto individuato")
                else:
                    print("Classe individuata: "+str(classes[str(id)]))

####################### VISUALIZER #######################

def visualizer(octreedir, mvp, mvp_sem):
    # removing point clouds from nodes and return if there was a change or not
    def remove_geometry():
        if not todelete.empty():
            id = todelete.get()
            try:
                index = onrenderid.index(id)
                cached.put(onrender.pop(index))
                vis.remove_geometry(onrenderid.pop(index))
            except:
                pass

    def create_xyz_pcd(node):
        pcd = o3d.geometry.PointCloud()
        pcd.id = node.id
        pcd.points = o3d.utility.Vector3dVector(node.points[:, :3])
        return pcd

    def create_xyzrgb_pcd(node):
        pcd = o3d.geometry.PointCloud()
        pcd.id = node.id
        pcd.points = o3d.utility.Vector3dVector(node.points[:, :3])
        pcd.colors = o3d.utility.Vector3dVector(node.points[:, 3:6])
        return pcd

    def create_xyzc_pcd(node):
        pcd = o3d.geometry.PointCloud()
        pcd.id = node.id
        pcd.points = o3d.utility.Vector3dVector(node.points[:, :3])
        pcd.classes = node.data[:, 3:4]

        c = []
        for i in node.points[:, 3:4]:
            c.append(i)

        pcd.classes = o3d.utility.IntVector(c)
        return pcd

    def create_xyzrgbc_pcd(node):
        pcd = o3d.geometry.PointCloud()
        pcd.id = node.id
        pcd.points = o3d.utility.Vector3dVector(node.points[:, :3])
        pcd.colors = o3d.utility.Vector3dVector(node.points[:, 3:6])

        c = []
        for i in node.points[:, 6:7]:
            c.append(i)

        pcd.classes = o3d.utility.IntVector(c)
        return pcd

    # adding point clouds from nodes and return if there was a change or not
    def add_geometry():
        updated = not torender.empty()

        if updated:
            node = torender.get()
            onrenderid.append(node.id)
            onrender.append(node)
            vis.add_geometry(create_pcd(node))

        return updated

    # update model view projection matrix that is used for frustum culling
    def update_mvp():
        param = ctr.get_mvp_matrix()
        for i in (range(param.shape[0])):
            for j in (range(param.shape[1])):
                mvp[i * 4 + j] = param[i][j]

    def on_geometry_update(vis):
        modify_geometry = True
        old_mvp = []

        # get the old mvp value
        for i in range(len(mvp)):
            old_mvp.append(mvp[i])

        # update m*v*p matrix values
        mvp_lock.acquire()
        try:
            update_mvp()
        finally:
            mvp_lock.release()

        for i in range(len(old_mvp)):
            if old_mvp[i] != mvp[i]:
                modify_geometry = False
                break

        # add or remove geometry to cloud only if there was no interaction with point cloud
        if modify_geometry:
            updated = add_geometry()
            if not updated:
                remove_geometry()

    def on_point_picked(id):
        picked.put(id)

    def on_reset(vis):
        vis.reset_view_point(True)

    ###################################################
    # load cloud info from json file
    with open(octreedir + "cloud.json", "r") as infofile:
        fstruct = json.load(infofile)['structure']

    vis = o3d.visualization.VisualizerWithKeyCallback()

    if fstruct == "xyz":
        create_pcd = create_xyz_pcd
    elif fstruct == "xyzc":
        create_pcd = create_xyzc_pcd
        vis = o3d.visualization.VisualizerWithKeyAndEdit()
        vis.register_onpick_callback(on_point_picked)
    elif fstruct == "xyzrgb":
        create_pcd = create_xyzrgb_pcd
    elif fstruct == "xyzrgbc":
        create_pcd = create_xyzrgbc_pcd
        vis = o3d.visualization.VisualizerWithKeyAndEdit()
        vis.register_onpick_callback(on_point_picked)

    vis.register_key_callback(ord("R"), on_reset)
    vis.register_animation_callback(on_geometry_update)
    vis.create_window()
    onrender = []
    onrenderid = []
    ctr = vis.get_view_control()

    # waiting until the first geometry is added
    mvp_lock.acquire()
    try:
        while add_geometry() == False:
            vis.update_geometry()
            vis.poll_events()
            vis.update_renderer()
    finally:
        mvp_lock.release()

    vis.update_geometry()
    vis.poll_events()
    vis.update_renderer()
    update_mvp()
    mvp_sem.value = 1
    vis.run()
    vis.destroy_window()

def start(octreeDir, max_nodes = 40):
    # preparing processes
    loa = Process(target=loader, args=(octreeDir,))
    vis = Process(target=visualizer, args=(octreeDir, mvp, mvp_sem,))
    tra = Process(target=traversal, args=(octreeDir, mvp, mvp_sem, max_nodes,))
    # starting processes
    loa.start()
    vis.start()
    tra.start()
    # waiting for visualizer
    vis.join()
    # terminate loader and traversal
    loa.terminate()
    tra.terminate()
    loa.join()
    tra.join()


