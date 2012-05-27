import itertools


class BoundingBox (object):
    type = int

    def __init__(self, origin=(0, 0, 0), size=(0, 0, 0)):
        if isinstance(origin, BoundingBox):
            self._origin = list(origin._origin)
            self._size = list(origin._size)
        else:
            self._origin, self._size = list(map(self.type, origin)), list(map(self.type, size))

    def chunkBox(self, level):
        """Returns this box extended to the chunk boundaries of the given level"""
        box = self
        return BoundingBox((box.mincx << 4, 0, box.mincz << 4), (box.maxcx - box.mincx << 4, level.Height, box.maxcz - box.mincz << 4))

    def getMinx(self):
        return self.origin[0]

    def getMiny(self):
        return self.origin[1]

    def getMinz(self):
        return self.origin[2]

    def getMaxx(self):
        return self.origin[0] + self.size[0]

    def getMaxy(self):
        return self.origin[1] + self.size[1]

    def getMaxz(self):
        return self.origin[2] + self.size[2]

    def setMinx(self, x):
        self.size[0] -= x - self.origin[0]
        self.origin[0] = x

    def setMiny(self, y):
        self.size[1] -= y - self.origin[1]
        self.origin[1] = y

    def setMinz(self, z):
        self.size[2] -= z - self.origin[2]
        self.origin[2] = z

    def setMaxx(self, x):
        if x < self.origin[0]:
            x = self.origin[0]

        self.size[0] = x - self.origin[0]

    def setMaxy(self, y):
        if y < self.origin[1]:
            y = self.origin[1]

        self.size[1] = y - self.origin[1]

    def setMaxz(self, z):
        if z < self.origin[2]:
            z = self.origin[2]

        self.size[2] = z - self.origin[2]

    minx = property(getMinx, setMinx)
    miny = property(getMiny, setMiny)
    minz = property(getMinz, setMinz)

    maxx = property(getMaxx, setMaxx)
    maxy = property(getMaxy, setMaxy)
    maxz = property(getMaxz, setMaxz)

    def getMincx(self):
        return self.origin[0] >> 4

    def getMincz(self):
        return self.origin[2] >> 4

    def getMaxcx(self):
        return ((self.origin[0] + self.size[0] - 1) >> 4) + 1

    def getMaxcz(self):
        return ((self.origin[2] + self.size[2] - 1) >> 4) + 1

    mincx = property(getMincx, None, None, "The smallest chunk position contained in this box")
    mincz = property(getMincz, None, None, "The smallest chunk position contained in this box")

    maxcx = property(getMaxcx, None, None, "The largest chunk position contained in this box")
    maxcz = property(getMaxcz, None, None, "The largest chunk position contained in this box")

    def getOrigin(self):
        return self._origin

    def setOrigin(self, o):
        self._origin = list(o)

    def getSize(self):
        return self._size

    def setSize(self, s):
        self._size = list(s)

    origin = property(getOrigin, setOrigin)
    size = property(getSize, setSize)

    def getWidth(self):
        return self._size[0]

    def getHeight(self):
        return self._size[1]

    def getLength(self):
        return self._size[2]

    def setWidth(self, w):
        self.size[0] = max(0, self.type(w))

    def setHeight(self, h):
        self.size[1] = max(0, self.type(h))

    def setLength(self, l):
        self.size[2] = max(0, self.type(l))

    width = property(getWidth, setWidth, None, "The dimension along the X axis")
    height = property(getHeight, setHeight, None, "The dimension along the Y axis")
    length = property(getLength, setLength, None, "The dimension along the Z axis")

    def getMaximum(self):
        return map(lambda a, b: a + b, self._origin, self._size)

    maximum = property(getMaximum, None, None, "The endpoint of the box; origin plus size.")

    def getVolume(self):
        return reduce(lambda a, b: a * b, self.size)

    volume = property(getVolume, None, None, "The volume of the box in blocks")

    @property
    def chunkPositions(self):
        #iterate through all of the chunk positions within this selection box
        return itertools.product(xrange(self.mincx, self.maxcx), xrange(self.mincz, self.maxcz))

    @property
    def positions(self):
        """iterate through all of the positions within this selection box"""
        return itertools.product(
            xrange(self.minx, self.maxx),
            xrange(self.miny, self.maxy),
            xrange(self.minz, self.maxz)
        )

    @property
    def chunkCount(self):
        return (self.maxcx - self.mincx) * (self.maxcz - self.mincz)

    @property
    def isChunkAligned(self):
        return (self.origin[0] & 0xf == 0) and (self.origin[2] & 0xf == 0)

    def intersect(self, box):
        """ return a box containing the area self and box have in common"""
        newbox = BoundingBox()

        if self.minx > box.maxx or self.maxx < box.minx:
            return BoundingBox()
        newbox.minx = max(self.minx, box.minx)
        newbox.maxx = min(self.maxx, box.maxx)

        if self.miny > box.maxy or self.maxy < box.miny:
            return BoundingBox()
        newbox.miny = max(self.miny, box.miny)
        newbox.maxy = min(self.maxy, box.maxy)
        if self.minz > box.maxz or self.maxz < box.minz:
            return BoundingBox()
        newbox.minz = max(self.minz, box.minz)
        newbox.maxz = min(self.maxz, box.maxz)

        #print "Intersect of {0} and {1}: {2}".format(self, box, newbox)
        return newbox

    def union(self, box):
        newbox = BoundingBox()
        newbox.minx = min(self.minx, box.minx)
        newbox.maxx = max(self.maxx, box.maxx)

        newbox.miny = min(self.miny, box.miny)
        newbox.maxy = max(self.maxy, box.maxy)
        newbox.minz = min(self.minz, box.minz)
        newbox.maxz = max(self.maxz, box.maxz)
        return newbox

    def expand(self, dx, dy=None, dz=None):
        if dz is None:
            dz = dx
        if dy is None:
            dy = dx

        box = BoundingBox(self)
        box.minx -= dx
        box.miny -= dy
        box.minz -= dz

        box.maxx += dx
        box.maxy += dy
        box.maxz += dz
        return box

    def __contains__(self, pos):
        x, y, z = pos
        if x < self.minx or x >= self.maxx:
            return False
        if y < self.miny or y >= self.maxy:
            return False
        if z < self.minz or z >= self.maxz:
            return False

        return True

    def __cmp__(self, b):
        return cmp((self.origin, self.size), (b.origin, b.size))

    def __repr__(self):
        return "BoundingBox({0}, {1})".format(self.origin, self.size)


class FloatBox (BoundingBox):
    type = float
