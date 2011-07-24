'''
Created on Jul 23, 2011

@author: Rio
'''
from mclevelbase import *

__all__ = "Entity, TileEntity".split(", ")

class TileEntity(object):
    @classmethod
    def pos(cls, tag):
        return [tag[a].value for a in 'xyz']
    
    @classmethod
    def setpos(cls, tag, pos):
        for a, p in zip('xyz', pos):
            tag[a] = TAG_Int(p)

class Entity(object):
    @classmethod
    def pos(cls, tag):
        if "Pos" not in tag:
            print tag
        return [a.value for a in tag["Pos"]]
    
    @classmethod
    def setpos(cls, tag, pos):
        tag["Pos"] = TAG_List([TAG_Int(p) for p in pos])
    
    @classmethod
    def copyWithOffset(cls, entity, copyOffset):  
        eTag = deepcopy(entity)
        
        positionTags = map(lambda p, co: nbt.TAG_Double(p.value+co), eTag["Pos"], copyOffset)
        eTag["Pos"] = TAG_List(positionTags)
        
        if eTag["id"].value == "Painting":
            eTag["TileX"].value += copyOffset[0]
            eTag["TileY"].value += copyOffset[1]
            eTag["TileZ"].value += copyOffset[2]
            
        return eTag