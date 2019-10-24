import os, time, pickle, json, random, numpy as np
from enum import Enum

# FUNCTIONS

# calculate midpoint between two points
def midpoint(a, b):
    if a < b:
        return ((b - a) / 2) + a
    else:
        return ((a - b) / 2) + b

# check if id is present in links byte
def node_exist(id, lbyte):
    if type(lbyte) is bytes:
        lbyte = int.from_bytes(lbyte, byteorder='big')

    mask = int('00000001', 2)
    mask = mask << ord('h') - ord(id)
    return lbyte & mask >= 1

# return the directory path
def id_to_path(id):
    path = ""

    for c in id:
        path = path + c + '/'

    return path

# return the file path
def id_to_node(id):
    path = ""

    for c in range(len(id) - 1):
        path = path + id[c] + '/'

    return path + id[len(id) - 1] + ".bin"

def gen_hierarchy(octreeDir):
    def populate(root, id):
        ret = VisNode(id)
        for i in range(ord('a'), ord('a') + 8):
            if node_exist(chr(i), int.from_bytes(root.links, byteorder='big')):
                ret.links.append(populate(nl.load_node_full_addr(id + chr(i)), id + chr(i)))
        return ret


    nl = NodeLoader(octreeDir)
    return populate(nl.load_root(), 'r')

# CLASSES

# xyz: coordinates, rgb: colours, i: intensity, c: class
class FileTypes(Enum):
    XYZ = "xyz"
    XYZRGB = "xyzrgb"
    XYZIRGB = "xyzirgb"
    XYZC = "xyzc"
    XYZRGBC = "xyzrgbc"
    XYZIRGBC = "xyzirgbc"

# Node used for rendering
class VisNode:

    def __init__(self, id, points = None):
        self.id = id
        self.links = []
        self.active = False
        self.points = points

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

# node used for storing
class Node:

    def __init__(self, points, links = b'\x00'):
        self.links = links

        if type(points[0]) is Point:
            pointsnum = len(points)

            def push_point(i):
                self.points[i] = [points[i].x, points[i].y, points[i].z]

            def push_point_color(i):
                self.points[i] = [points[i].x, points[i].y, points[i].z, points[i].r, points[i].g, points[i].b]

            def push_point_class(i):
                self.points[i] = [points[i].x, points[i].y, points[i].z, points[i].c]

            def push_point_color_class(i):
                self.points[i] = [points[i].x, points[i].y, points[i].z, points[i].r, points[i].g, points[i].b, points[i].c]

            store = push_point
            dim = 3

            if points[0].r != None and points[0].g != None and points[0].b != None and points[0].c == None:
                store = push_point_color
                dim = 6
            elif points[0].r == None and points[0].g == None and points[0].b == None and points[0].c != None:
                store = push_point_class
                dim = 4
            elif points[0].r != None and points[0].g != None and points[0].b != None and points[0].c != None:
                store = push_point_color_class
                dim = 7

            self.points = np.zeros((pointsnum, dim))
            for i in range(pointsnum):
                store(i)
        else:
            self.points = points

class NodeLoader:
    def __init__(self, dir):
        self.dir = dir

    def load_node(self, id):
        with open(self.dir + "r/" + id_to_node(id), 'rb') as r:
            return pickle.load(r)

    def load_node_full_addr(self, id):
        with open(self.dir + id_to_node(id), 'rb') as r:
            return pickle.load(r)

    def load_ghost_node(self, id):
        try:
            with open(self.dir + "r/" + id_to_node(id), 'rb') as r:
                return pickle.load(r)
        except:
            return None

    def load_root(self):
        with open(self.dir + "r.bin", 'rb') as r:
            return pickle.load(r)

class Point:

    def __init__(self, x, y, z, r = None, g = None, b = None, c = None):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.g = g
        self.b = b
        self.c = c

class BoundingBox:

    def __init__(self, minx, miny, minz, maxx, maxy, maxz):
        self.minx = minx
        self.miny = miny
        self.minz = minz
        self.maxx = maxx
        self.maxy = maxy
        self.maxz = maxz

    def get_midx(self):
        return midpoint(self.minx, self.maxx)

    def get_midy(self):
        return midpoint(self.miny, self.maxy)

    def get_midz(self):
        return midpoint(self.minz, self.maxz)

    def get_radius(self):
        return (((self.maxx - self.minx) + (self.maxy - self.miny) + (self.maxz - self.minz)) / 3)/2

# manager of id and bounding box
class BBManager:

    def __init__(self, bb):
        self.bb = bb

    def get_bounding_box(self):
        return self.bb

    # return the boundingbox
    def id_to_bb(self, id):
        ret = self.bb

        for c in id:
            midx = midpoint(ret.maxx, ret.minx)
            midy = midpoint(ret.maxy, ret.miny)
            midz = midpoint(ret.maxz, ret.minz)

            if c in "a":
                ret = BoundingBox(ret.minx, ret.miny, ret.minz, midx, midy, midz)
            elif c in "b":
                ret = BoundingBox(midx, ret.miny, ret.minz, ret.maxx, midy, midz)
            elif c in "c":
                ret = BoundingBox(ret.minx, midy, ret.minz, midx, ret.maxy, midz)
            elif c in "d":
                ret = BoundingBox(midx, midy, ret.minz, ret.maxx, ret.maxy, midz)
            elif c in "e":
                ret = BoundingBox(ret.minx, ret.miny, midz, midx, midy, ret.maxz)
            elif c in "f":
                ret = BoundingBox(midx, ret.miny, midz, ret.maxx, midy, ret.maxz)
            elif c in "g":
                ret = BoundingBox(ret.minx, midy, midz, midx, ret.maxy, ret.maxz)
            elif c in "h":
                ret = BoundingBox(midx, midy, midz, ret.maxx, ret.maxy, ret.maxz)

        return ret

    # identify if point is into boundingbox
    def is_into(self, bbox, x, y, z):
        if bbox.maxx == self.bb.maxx:
            xcond = bbox.minx <= x and bbox.maxx >= x
        else:
            xcond = bbox.minx <= x and bbox.maxx > x

        if xcond == False:
            return False

        if bbox.maxy == self.bb.maxy:
            ycond = bbox.miny <= y and bbox.maxy >= y
        else:
            ycond = bbox.miny <= y and bbox.maxy > y

        if ycond == False:
            return False

        if bbox.maxz == self.bb.maxz:
            zcond = bbox.minz <= z and bbox.maxz >= z
        else:
            zcond = bbox.minz <= z and bbox.maxz > z

        return xcond and ycond and zcond

class IdGenerator:

    def __init__(self, limit):
        self.limit = limit
        self.ids = []
        for i in range(limit):
            self.ids.append(ord('a') - 1)
        self.c = 0

    def next(self):
        if self.c == self.limit:
            return None
        elif self.ids[self.c] < ord('h'):
            self.ids[self.c] = self.ids[self.c] + 1
            return self.__value()
        elif self.ids[self.c] == ord('h'):
            index = self.__end()
            if index != None:
                self.ids[index] = self.ids[index] + 1
                for i in range(index+1, self.c):
                    self.ids[i] = ord('a')
                self.ids[self.c] = ord('a') - 1
                return self.next()
            else:
                self.__reset()
                self.c = self.c + 1
                return self.next()

    def __value(self):
        ret = ""

        for i in range(self.c + 1):
            ret = ret + chr(self.ids[i])

        return ret

    def __end(self):
        index = -1
        for i in range(self.c):
            if self.ids[i] != ord('h'):
                if i > index:
                    index = i

        if index == -1:
            return None
        else:
            return index

    def __reset(self):
        for i in range(self.c + 1):
            self.ids[i] = ord('a')

class Generator:
    #TODO rgb float gia' in file

    # adreess of file, structure of file, classes, float rgb value
    def __init__(self, fileaddr, type, classes = None, maxpn = 80000, frgb = False):
        self.fileaddr = fileaddr
        self.type = type
        self.cloudname = fileaddr.split("/")[len(fileaddr.split("/")) - 1]
        self.dir = fileaddr.split(".")[0] + "Octree/"
        self.MAXPOINTSN = maxpn
        self.ROOTPOINTSN = 20000
        self.classes = classes

    def parse(self):
        print("Octree-format generator started")
        start = time.time()

        if self.type in FileTypes.XYZ.value:
            self.create_point = self.__xyz_point
        elif self.type in FileTypes.XYZRGB.value:
            self.create_point = self.__xyzrgb_point
        elif self.type in FileTypes.XYZIRGB.value:
            self.create_point = self.__xyzirgb_point
        elif self.type in FileTypes.XYZC.value:
            self.create_point = self.__xyzc_point
        elif self.type in FileTypes.XYZRGBC.value:
            self.create_point = self.__xyzrgbc_point
        elif self.type in FileTypes.XYZIRGBC.value:
            self.create_point = self.__xyzirgbc_point
        else:
            raise Exception('File structure not supported, known structures are: xyz, xyzrgb, xyzirgb, xyzrgbc, xyzirgbc')

        os.mkdir(self.dir)
        os.mkdir(self.dir + "r")

        with open(self.fileaddr, "r") as f:
            self.__beginning(f)
            self.__calc_bb_and_numpoints(f)
            self.__beginning(f)

        # create first level (root node is zero level)
        # TODO un giorno (s1 = Process(target=self.__store_nodes, args=('a', 4, self.dir + "/r/", create_point)) s1.start()) forse sarò multithread, ma non è questo il giorno
        ids = self.__gen_first_level()

        # create levels
        self.__gen_sublevels(ids)

        self.__create_info()
        if "c" in self.type:
            self.__create_class_info()
        print("Generated directory: " + self.dir)
        print("PointCloud number of points: " + str(self.pointsnum))
        print("Conversion finished in " + str(int(time.time() - start)) + " seconds")
        return self.dir

    # generate the first level of octree-based structure, reading from file
    def __gen_first_level(self):
        dir = self.dir + "r/"
        links = int('00000000', 2)
        rootp = []
        ids = []
        with open(self.fileaddr, "r") as f:
            for i in range(ord('a'), ord('a') + 8):
                links = links << 1
                id = chr(i)
                file = dir + id + ".bin"
                bb = self.bbmanager.id_to_bb(id)
                nodep = []

                for line in f.readlines():
                    values = line.split()
                    if self.bbmanager.is_into(bb, float(values[0]), float(values[1]), float(values[2])):
                        nodep.append(self.create_point(values))

                # rate value of root points still remain in root
                if len(nodep) > 0:
                    rate = (self.ROOTPOINTSN/8) / len(nodep)
                    if rate < 1.0:
                        limit = int(0.03 * len(nodep))
                        indices = random.sample(range(len(nodep)), limit)
                        nodep = np.array(nodep)
                        rootp.extend(nodep[indices])
                        nodep = np.delete(nodep, indices, axis=0)
                        self.__store_node(file, Node(nodep))
                        links = links + 1
                        if len(nodep) > self.MAXPOINTSN:
                            ids.append(id)
                    else:
                        rootp.extend(nodep)

                self.__beginning(f)

        # save root node
        self.__store_node(dir + "../r.bin", Node(rootp, links.to_bytes(1, byteorder='big')))
        # return ids that need to be unpacked
        return ids

    # generate levelsnum levels of octree-based structure
    def __gen_sublevels(self, ids, rootid = ""):

        for id in ids:
            self.__gen_sublevels(self.__gen_sublevel(rootid + id, NodeLoader(self.dir).load_node(rootid + id)), rootid + id)

    # generate level of octree-based structure, reading from .bin node files
    def __gen_sublevel(self, rootid, root):
        os.mkdir(self.dir + "r/" + id_to_path(rootid))
        dirneeded = False
        links = int.from_bytes(root.links, byteorder='big')
        ids = []

        for n in range(8):
            mask = np.full((root.points.shape[0]), False)
            itomove = []
            bb = self.bbmanager.id_to_bb(rootid + chr(ord('a') + n))

            for i in range(root.points.shape[0]):
                if self.bbmanager.is_into(bb, root.points[i][0], root.points[i][1], root.points[i][2]):
                    mask[i] = True
                    itomove.append(i)

            # rate value of root points still remain in root
            links = links << 1
            if len(itomove) > 0:
                rate = (self.MAXPOINTSN/8) / len(itomove)
                if rate < 1.0:
                    limit = int(rate * len(itomove))
                    dirneeded = True

                    # modify mask removing rate of not needed points
                    for j in random.sample(itomove, limit):
                        mask[j] = False

                    nodep = root.points[mask]
                    root.points = np.delete(root.points, itomove[limit:], axis=0)
                    self.__store_node(self.dir + "r/" + id_to_node(rootid+chr(ord('a')+n)), Node(nodep))
                    links = links + 1
                    if len(nodep) > self.MAXPOINTSN:
                        ids.append(chr(ord('a')+n))

        # update and save root node
        root.links = links.to_bytes(1, byteorder='big')
        self.__store_node(self.dir + "r/" + id_to_node(rootid), root)
        # remove empty directory
        if not dirneeded:
            os.rmdir(self.dir + "r/" + id_to_path(rootid))
        # return ids that need to be unpacked
        return ids

    # save node through pickle
    def __store_node(self, addr, node):
        with open(addr, 'wb') as fn:
            pickle.dump(node, fn)

    # go to the beginning of file, identify and skip the possible initial line with (for example) the number of points in the cloud
    def __beginning(self, f):
        f.seek(0, 0)
        if len(f.readline().split()) != 1:
            f.seek(0, 0)

    # calculate bounding box of point cloud and number of points
    def __calc_bb_and_numpoints(self, f):
        values = f.readline().split()
        x = float(values[0])
        y = float(values[1])
        z = float(values[2])
        self.pointsnum = 1

        minx = x
        maxx = x
        miny = y
        maxy = y
        minz = z
        maxz = z

        for line in f.readlines():
            self.pointsnum = self.pointsnum + 1
            values = line.split()

            if minx > float(values[0]):
                minx = float(values[0])
            elif maxx < float(values[0]):
                maxx = float(values[0])

            if miny > float(values[1]):
                miny = float(values[1])
            elif maxy < float(values[1]):
                maxy = float(values[1])

            if minz > float(values[2]):
                minz = float(values[2])
            elif maxz < float(values[2]):
                maxz = float(values[2])

        self.bbmanager = BBManager(BoundingBox(minx, miny, minz, maxx, maxy, maxz))

    def __create_info(self):
        cloud = {
            "name": self.cloudname,
            "pointsnum": self.pointsnum,
            "structure": self.type.replace("i", ""),
            "minx": self.bbmanager.bb.minx,
            "miny": self.bbmanager.bb.miny,
            "minz": self.bbmanager.bb.minz,
            "maxx": self.bbmanager.bb.maxx,
            "maxy": self.bbmanager.bb.maxy,
            "maxz": self.bbmanager.bb.maxz
        }

        with open(self.dir+'/cloud.json', 'w') as infofile:
            json.dump(cloud, infofile)

    def __create_class_info(self):
        if self.classes is not None:
            with open(self.dir+'/classes.json', 'w') as classfile:
                json.dump(self.classes, classfile)

    def __xyz_point(self, values):
        return Point(float(values[0]), float(values[1]), float(values[2]))

    def __xyzrgb_point(self, values):
        return Point(float(values[0]), float(values[1]), float(values[2]), float(values[3])/255.0, float(values[4])/255.0, float(values[5])/255.0)

    def __xyzirgb_point(self, values):
        return Point(float(values[0]), float(values[1]), float(values[2]), float(values[4])/255.0, float(values[5])/255.0, float(values[6])/255.0)

    def __xyzc_point(self, values):
        return Point(float(values[0]), float(values[1]), float(values[2]), None, None, None, float(values[3]))

    def __xyzrgbc_point(self, values):
        return Point(float(values[0]), float(values[1]), float(values[2]), float(values[3])/255.0, float(values[4])/255.0, float(values[5])/255.0, float(values[6]))

    def __xyzirgbc_point(self, values):
        return Point(float(values[0]), float(values[1]), float(values[2]), float(values[4])/255.0, float(values[5])/255.0, float(values[6])/255.0, float(values[7]))

    def get_generated_dir(self):
        return self.dir

    def get_bounding_box_manager(self):
        return self.bbmanager

    def get_number_of_points(self):
        return self.pointsnum

class LRU:

    def __init__(self, max = 128):
        self.ids = []
        self.points = []
        self.max = max

    def exist(self, id):
        return id in self.ids

    # programmer must check if node exist before calling this function
    def extract_node_points(self, id):
        index = self.ids.index(id)
        self.ids.pop(index)
        points = self.points.pop(index)
        # move extracted node to the end of queue
        self.ids.append(id)
        self.points.append(points)
        return points

    def store_node(self, node):
        self.ids.append(node.id)
        self.points.append(node.points)

        # If the cache reached maximum, remove the last recently used node
        if len(self.ids) > self.max:
            self.ids.pop(0)
            self.points.pop(0)