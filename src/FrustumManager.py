import math

# implemenation from:
# https://cgvr.cs.uni-bremen.de/teaching/cg_literatur/lighthouse3d_view_frustum_culling/index.html
# http://www.crownandcutlass.com/features/technicaldetails/frustum.html

class FrustumManager:

    def __init__(self):
        self.pl = []
        self.NEARP = 0
        self.FARP = 1
        self.BOTTOM = 2
        self.TOP = 3
        self.LEFT = 4
        self.RIGHT = 5

        for i in range(6):
            self.pl.append(Plane())

    # m: projection matrix * model matrix * view matrix
    def update_frustum(self, m):
        self.pl[self.NEARP].set_coeff(
            m[8] + m[12],
            m[9] + m[13],
            m[10] + m[14],
            m[11] + m[15])
        self.pl[self.FARP].set_coeff(
            -m[8] + m[12],
            -m[9] + m[13],
            -m[10] + m[14],
            -m[11] + m[15])
        self.pl[self.BOTTOM].set_coeff(
            m[4] + m[12],
            m[5] + m[13],
            m[6] + m[14],
            m[7] + m[15])
        self.pl[self.TOP].set_coeff(
            -m[4] + m[12],
            -m[5] + m[13],
            -m[6] + m[14],
            -m[7] + m[15])
        self.pl[self.LEFT].set_coeff(
            m[0] + m[12],
            m[1] + m[13],
            m[2] + m[14],
            m[3] + m[15])
        self.pl[self.RIGHT].set_coeff(
            -m[0] + m[12],
            -m[1] + m[13],
            -m[2] + m[14],
            -m[3] + m[15])

    def dist_from_near(self, x, y, z):
        return self.pl[self.NEARP].distance(x, y, z)

    def point_in_frustum(self, x, y, z):
        for i in range(6):
            if not self.pl[i].is_point_infront(x, y, z):
                return False
        return True

    # function that check if bounding box is into frustum view, returns:
    # 0 bbox is totally out of frustum
    # 1 bbox is partially into frustum
    # 2 bbox is totally into frustum
    def bbox_in_frustum(self, bb):
        points = []
        in_frustum = 0

        points.append([bb.minx, bb.miny, bb.minz])
        points.append([bb.maxx, bb.miny, bb.minz])
        points.append([bb.minx, bb.maxy, bb.minz])
        points.append([bb.minx, bb.miny, bb.maxz])
        points.append([bb.maxx, bb.maxy, bb.minz])
        points.append([bb.minx, bb.maxy, bb.maxz])
        points.append([bb.maxx, bb.miny, bb.maxz])
        points.append([bb.maxx, bb.maxy, bb.maxz])

        points.append([bb.get_midx(), bb.get_midy(), bb.get_midz()])

        for i in range(len(points)):
            if self.point_in_frustum(points[i][0], points[i][1], points[i][2]):
                in_frustum += 1

        if in_frustum == 0:
            return 0
        elif in_frustum < len(points):
            return 1
        else:
            return 2

# Plane equation: Ax + By + Cz + D = 0
class Plane:

    def __init__(self, a=0.0, b=0.0, c=0.0, d=0.0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def set_coeff(self, a, b, c, d):
        l = math.sqrt(a*a + b*b + c*c)
        if l > 0:
            self.a = a/l
            self.b = b/l
            self.c = c/l
            self.d = d/l

    def is_point_infront(self, x, y, z):
        return (self.a*x + self.b*y + self.c*z + self.d) > 0

    def distance(self, x, y, z):
        return abs((self.a * x + self.b * y + self.c * z + self.d) / math.sqrt(self.a*self.a + self.b*self.b + self.c*self.c))