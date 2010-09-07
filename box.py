class BoundingBox:
    
    def __init__(self, origin = (0,0,0), size = (0,0,0)):
        self._origin, self._size = list(origin),list(size)
    
    def getMinx(self): return self.origin[0];
    def getMiny(self): return self.origin[1];
    def getMinz(self): return self.origin[2];
    
    def getMaxx(self): return self.origin[0]+self.size[0];
    def getMaxy(self): return self.origin[1]+self.size[1];
    def getMaxz(self): return self.origin[2]+self.size[2];
    
    minx = property(getMinx);
    miny = property(getMiny);
    minz = property(getMinz);
    
    maxx = property(getMaxx);
    maxy = property(getMaxy);
    maxz = property(getMaxz);
    
    def getMincx(self): return self.origin[0]>>4;
    def getMincz(self): return self.origin[2]>>4;
    
    def getMaxcx(self): return ((self.origin[0]+self.size[0]-1)>>4)+1;
    def getMaxcz(self): return ((self.origin[2]+self.size[2]-1)>>4)+1;
    
    mincx = property(getMincx, None, None, "The smallest chunk position contained in this box");
    mincz = property(getMincz, None, None, "The smallest chunk position contained in this box");
    
    maxcx = property(getMaxcx, None, None, "The largest chunk position contained in this box");
    maxcz = property(getMaxcz, None, None, "The largest chunk position contained in this box");
    
    def getOrigin(self): return self._origin;
    def setOrigin(self, o): self._origin = list(o);
    
    def getSize(self): return self._size;
    def setSize(self, s): self._size = list(s);
    
    origin = property(getOrigin, setOrigin)
    size = property(getSize, setSize)
    
    def getWidth(self): return self._size[0];
    def getHeight(self): return self._size[1];
    def getLength(self): return self._size[2];
    
    def setWidth(self, w): self.size[0] = w;
    def setHeight(self, h): self.size[1] = h;
    def setLength(self, l): self.size[2] = l;
    
    width = property(getWidth, setWidth, None, "The dimension along the X axis");
    height = property(getHeight, setHeight, None, "The dimension along the Y axis");
    length = property(getLength, setLength, None, "The dimension along the Z axis");
    
    
    def getMaximum(self): return map(lambda a,b:a+b, self._origin, self._size)
    
    maximum = property(getMaximum, None, None, "The endpoint of the box; origin plus size.")
    
    def getVolume(self): return reduce(int.__mul__, self.size)
    volume = property(getVolume, None, None, "The volume of the box in blocks")
    
    def __contains__(self, pos):
        x,y,z = pos;
        if x<self.minx or x>=self.maxx: return False
        if y<self.miny or y>=self.maxy: return False
        if z<self.minz or z>=self.maxz: return False
        
        return True;
        
    def __repr__(self):
        return "BoundingBox({0}, {1})".format(self.origin, self.size)