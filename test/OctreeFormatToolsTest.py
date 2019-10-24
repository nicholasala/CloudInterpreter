import unittest, os, shutil
import OctreeFormatTools as oft

class OctreeFormatToolsTest(unittest.TestCase):

    def test_midpoint(self):
        a = 173
        b = 345
        self.assertEqual(259, oft.midpoint(a, b))
        self.assertEqual(259, oft.midpoint(b, a))

    def test_node_exist(self):
        #create links in which only a f and h node are present
        links = int('10000101', 2)
        self.assertTrue(oft.node_exist('a', links))
        self.assertFalse(oft.node_exist('b', links))
        self.assertFalse(oft.node_exist('c', links))
        self.assertFalse(oft.node_exist('d', links))
        self.assertFalse(oft.node_exist('e', links))
        self.assertTrue(oft.node_exist('f', links))
        self.assertFalse(oft.node_exist('g', links))
        self.assertTrue(oft.node_exist('h', links))

    def test_id_generator(self):
        ig = oft.IdGenerator(3)

        for i in range(ord('a'), ord('h')+1):
            self.assertEqual(chr(i), ig.next())

        for i in range(ord('a'), ord('h')+1):
            for j in range(ord('a'), ord('h') + 1):
                self.assertEqual(chr(i)+chr(j), ig.next())

        for i in range(ord('a'), ord('h')+1):
            for j in range(ord('a'), ord('h') + 1):
                for k in range(ord('a'), ord('h') + 1):
                    self.assertEqual(chr(i)+chr(j)+chr(k), ig.next())

        self.assertEqual(None , ig.next())

    # create generator with inexistent file structure and check if exception is thrown
    def test_filestruct_handled(self):
        with open("temp.xyz", "w") as f:
            f.write("-79.20802307 -33.31158066 80.33101654\n"
                    + "-80.33101654 -34.17058182 80.33101654\n"
                    + "-78.67701721 -33.42058182 80.33101654\n")

        with self.assertRaises(Exception):
            oft.Generator("temp.xyz", "xyczrgb").parse()

        os.remove("temp.xyz")

    # check that parse fail if the structure passed didn't match the real file structure
    def test_filestruct_not_matching(self):
        # create file with xyzrgb structure
        with open("temp.xyz", "w") as f:
            f.write("-79.20802307 -33.31158066 -33.31158066 255 255 123\n"
                    + "-80.33101654 -34.17058182 -34.17058182 255 255 123\n"
                    + "-80.33101654 134.17058182 -34.17058182 255 255 123\n"
                    + "180.33101654 34.17058182 80.33101654 255 255 123\n"
                    + "-78.67701721 -33.42058182 -33.42058182 255 255 123\n")

        # create generator for xyzrgbc structure
        gen = oft.Generator("temp.xyz", "xyzrgbc")

        with self.assertRaises(Exception):
            gen.parse()

        os.remove("temp.xyz")
        shutil.rmtree("./tempOctree")

    # verify that the number of points founded through function is_into in the first 8 bounding box, is the same of number of all points in the point cloud
    # this means that is_into function works properly
    def test_is_into_bb(self):
        try:
            with open("temp.xyz", "w") as f:
                f.write("-79.20802307 -33.31158066 -33.31158066 255 255 123\n"
                        +"-80.33101654 -34.17058182 -34.17058182 255 255 123\n"
                        + "-80.33101654 134.17058182 -34.17058182 255 255 123\n"
                        + "180.33101654 34.17058182 80.33101654 255 255 123\n"
                        +"-78.67701721 -33.42058182 -33.42058182 255 255 123\n")

            gen = oft.Generator("temp.xyz", "xyzrgb")
            gen.parse()
            bbmanager = gen.get_bounding_box_manager()
            founded = 0

            with open("temp.xyz", "r") as f:
                for i in range(97, 105):
                    id = chr(i)
                    bb = bbmanager.id_to_bb(id)

                    for line in f.readlines():
                        values = line.split()
                        if bbmanager.is_into(bb, float(values[0]), float(values[1]), float(values[2])):
                            founded = founded + 1

                    f.seek(0,0)

            self.assertEqual(gen.get_number_of_points(), 5)
            self.assertEqual(gen.get_number_of_points(), founded)
        finally:
            os.remove("temp.xyz")
            shutil.rmtree("./tempOctree")

    # check if dimensions of bb returned by id_to_bounding_box are correct
    def test_id_to_bb(self):

        def check_bb(bb, minx, miny, minz, maxx, maxy, maxz):
            self.assertEqual(bb.minx, minx)
            self.assertEqual(bb.miny, miny)
            self.assertEqual(bb.minz, minz)
            self.assertEqual(bb.maxx, maxx)
            self.assertEqual(bb.maxy, maxy)
            self.assertEqual(bb.maxz, maxz)

        bm = oft.BBManager(oft.BoundingBox(0, 0, 0, 8, 8, 8))

        check_bb(bm.id_to_bb("r"), 0, 0, 0, 8, 8, 8)
        check_bb(bm.id_to_bb("ra"), 0, 0, 0, 4, 4, 4)

        check_bb(bm.id_to_bb("a"), 0, 0, 0, 4, 4, 4)
        check_bb(bm.id_to_bb("b"), 4, 0, 0, 8, 4, 4)
        check_bb(bm.id_to_bb("c"), 0, 4, 0, 4, 8, 4)
        check_bb(bm.id_to_bb("d"), 4, 4, 0, 8, 8, 4)
        check_bb(bm.id_to_bb("e"), 0, 0, 4, 4, 4, 8)
        check_bb(bm.id_to_bb("f"), 4, 0, 4, 8, 4, 8)
        check_bb(bm.id_to_bb("g"), 0, 4, 4, 4, 8, 8)
        check_bb(bm.id_to_bb("h"), 4, 4, 4, 8, 8, 8)

        check_bb(bm.id_to_bb("aa"), 0, 0, 0, 2, 2, 2)
        check_bb(bm.id_to_bb("bb"), 6, 0, 0, 8, 2, 2)
        check_bb(bm.id_to_bb("cc"), 0, 6, 0, 2, 8, 2)
        check_bb(bm.id_to_bb("dd"), 6, 6, 0, 8, 8, 2)
        check_bb(bm.id_to_bb("ee"), 0, 0, 6, 2, 2, 8)
        check_bb(bm.id_to_bb("ff"), 6, 0, 6, 8, 2, 8)
        check_bb(bm.id_to_bb("gg"), 0, 6, 6, 2, 8, 8)
        check_bb(bm.id_to_bb("hh"), 6, 6, 6, 8, 8, 8)

        check_bb(bm.id_to_bb("ah"), 2, 2, 2, 4, 4, 4)
        check_bb(bm.id_to_bb("bf"), 6, 0, 2, 8, 2, 4)
        check_bb(bm.id_to_bb("ce"), 0, 4, 2, 2, 6, 4)
        check_bb(bm.id_to_bb("da"), 4, 4, 0, 6, 6, 2)
        check_bb(bm.id_to_bb("eg"), 0, 2, 6, 2, 4, 8)
        check_bb(bm.id_to_bb("fb"), 6, 0, 4, 8, 2, 6)
        check_bb(bm.id_to_bb("gc"), 0, 6, 4, 2, 8, 6)
        check_bb(bm.id_to_bb("hd"), 6, 6, 4, 8, 8, 6)

    # check if the number of points before and after the conversion is the same
    def test_points_number(self):
        def calc_number(vnode):
            n = 0
            for node in vnode.links:
                n = n + calc_number(node)

            return n + oft.NodeLoader(dir).load_node_full_addr(vnode.id).points.shape[0]

        try:
            gen = oft.Generator("less.xyz", "xyzrgb", None, 1000)
            dir = gen.parse()
            visnode = oft.gen_hierarchy(dir)
            self.assertEqual(gen.get_number_of_points(), calc_number(visnode))
        finally:
            shutil.rmtree("./lessOctree")

    # check if the number of points in all nodes is under max number of points
    def test_points_bound(self):
        def check_number(vnode):
            for node in vnode.links:
                check_number(node)

            self.assertLessEqual(oft.NodeLoader(dir).load_node_full_addr(vnode.id).points.shape[0], 1000)

        try:
            gen = oft.Generator("less.xyz", "xyzrgb", None, 1000)
            dir = gen.parse()
            visnode = oft.gen_hierarchy(dir)

            for node in visnode.links:
                check_number(node)
        finally:
            shutil.rmtree("./lessOctree")

    def test_lru(self):
        lru = oft.LRU(3)
        self.assertFalse(lru.exist("a"))

        v1 = oft.VisNode("a", 1)
        v2 = oft.VisNode("b", 2)
        v3 = oft.VisNode("c", 3)
        v4 = oft.VisNode("d", 4)

        lru.store_node(v1)
        self.assertTrue(lru.exist("a"))
        self.assertFalse(lru.exist("b"))

        lru.store_node(v2)
        lru.store_node(v3)
        self.assertTrue(lru.exist("b"))
        self.assertTrue(lru.exist("c"))

        lru.store_node(v4)
        self.assertTrue(lru.exist("d"))
        self.assertFalse(lru.exist("a"))

        self.assertEqual(2, lru.extract_node_points("b"))
        self.assertEqual(3, lru.extract_node_points("c"))
        self.assertEqual(4, lru.extract_node_points("d"))

        with self.assertRaises(Exception):
            lru.extract_node_points("abc")

        lru.store_node(v1)
        self.assertTrue(lru.exist("a"))

if __name__ == '__main__':
    unittest.main()