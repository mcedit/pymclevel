'''
Created on Jul 23, 2011

@author: Rio
'''
#from mclevelbase import *
from nbt import *
import nbt
from copy import deepcopy

__all__ = "Entity, TileEntity".split(", ")

id = "id"

Motion = "Motion"
Pos = "Pos"
Rotation = "Rotation"

class TileEntity(object):
    knownIDs = "Furnace, Sign, MonsterSpawner, Chest, Music, Trap, RecordPlayer".split(", ")
    baseStructures = {
        "Furnace": (
            ("BurnTime", TAG_Short),
            ("CookTime", TAG_Short),
            ("Items", TAG_List),
        ),
        "Sign": (
            ("Items", TAG_List),
        ),
        "MobSpawner": (
            ("Items", TAG_List),
        ),
        "Chest": (
            ("Items", TAG_List),
        ),
        "Music": (
            ("note", TAG_Byte),
        ),
        "Trap": (
            ("Items", TAG_List),
        ),
        "RecordPlayer": (
            ("Record", TAG_Int),
        ),

    }
    maxItems = {
        "Furnace" : 3,
        "Chest" : 27,
        "Trap" : 9,
    }
    @classmethod
    def Create(cls, tileEntityID, **kw):
        tileEntityTag = TAG_Compound()
        tileEntityTag[id] = TAG_String(tileEntityID)
        base = cls.baseStructures.get(tileEntityID, None)
        if base:
            for (name, tag) in base:
                tileEntityTag[name] = tag()

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
        entityTag[id] = TAG_String(entityID)
        Entity.setpos(entityTag, (0, 0, 0))
        return entityTag

    @classmethod
    def pos(cls, tag):
        if Pos not in tag:
            raise InvalidEntity, tag
        return [a.value for a in tag[Pos]]

    @classmethod
    def setpos(cls, tag, pos):
        tag["Pos"] = TAG_List([TAG_Double(p) for p in pos])

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
