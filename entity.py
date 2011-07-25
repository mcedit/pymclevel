'''
Created on Jul 23, 2011

@author: Rio
'''
from mclevelbase import *

__all__ = "Entity, TileEntity".split(", ")

EntityId = "EntityId"
id = "id"

Motion = "Motion"
Pos = "Pos"
Rotation = "Rotation"

class TileEntity(object):
    knownIDs = "Furnace, Sign, MonsterSpawner, Chest, Music, Trap, RecordPlayer".split(", ")
    @classmethod
    def Create(cls, tileEntityID, **kw):
        tileEntityTag = TAG_Compound()
        tileEntityTag[id] = TAG_String(tileEntityID)
        cls.setpos(tileEntityTag, (0, 0, 0))
        return tileEntityTag

    @classmethod
    def pos(cls, tag):
        return [tag[a].value for a in 'xyz']

    @classmethod
    def setpos(cls, tag, pos):
        for a, p in zip('xyz', pos):
            tag[a] = TAG_Int(p)

    @classmethod
    def copyWithOffset(cls, tileEntity, copyOffset):
        eTag = deepcopy(tileEntity)
        eTag['x'] = TAG_Int(tileEntity['x'].value + copyOffset[0])
        eTag['y'] = TAG_Int(tileEntity['y'].value + copyOffset[1])
        eTag['z'] = TAG_Int(tileEntity['z'].value + copyOffset[2])
        return eTag


class Entity(object):
    @classmethod
    def Create(cls, entityID, **kw):
        entityTag = TAG_Compound()
        entityTag[EntityId] = TAG_String(entityID)
        entityTag[Pos] = [TAG_Int(0) for i in range(3)]
        return entityTag

    @classmethod
    def pos(cls, tag):
        if Pos not in tag:
            raise InvalidEntity, tag
        return [a.value for a in tag[Pos]]

    @classmethod
    def setpos(cls, tag, pos):
        tag["Pos"] = TAG_List([TAG_Int(p) for p in pos])

    @classmethod
    def copyWithOffset(cls, entity, copyOffset):
        eTag = deepcopy(entity)

        positionTags = map(lambda p, co: nbt.TAG_Double(p.value + co), eTag["Pos"], copyOffset)
        eTag["Pos"] = TAG_List(positionTags)

        if eTag["id"].value == "Painting":
            eTag["TileX"].value += copyOffset[0]
            eTag["TileY"].value += copyOffset[1]
            eTag["TileZ"].value += copyOffset[2]

        return eTag

class InvalidEntity(ValueError): pass
class InvalidTileEntity(ValueError): pass
