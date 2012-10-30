import itertools
import shutil
import unittest
import numpy

import mclevel
from infiniteworld import MCInfdevOldLevel
from schematic import MCSchematic
from box import BoundingBox
from templevel import mktemp, TempLevel

__author__ = 'Rio'

class TestAnvilLevelCreate(unittest.TestCase):
    def testCreate(self):
        temppath = mktemp("AnvilCreate")
        self.anvilLevel = MCInfdevOldLevel(filename=temppath, create=True)
        self.anvilLevel.close()
        shutil.rmtree(temppath)


class TestAnvilLevel(unittest.TestCase):
    def setUp(self):
        self.indevLevel = TempLevel("hell.mclevel")
        self.anvilLevel = TempLevel("AnvilWorld")

    def testUnsetProperties(self):
        level = self.anvilLevel.level
        del level.root_tag['Data']['LastPlayed']
        import time
        assert 0 != level.LastPlayed
        level.LastPlayed = time.time() * 1000 - 1000000

    def testGetEntities(self):
        level = self.anvilLevel.level
        print len(level.getEntitiesInBox(level.bounds))

    def testCreateChunks(self):
        level = self.anvilLevel.level

        for ch in list(level.allChunks):
            level.deleteChunk(*ch)
        level.createChunksInBox(BoundingBox((0, 0, 0), (32, 0, 32)))

    def testCopyConvertBlocks(self):
        indevlevel = self.indevLevel.level
        level = self.anvilLevel.level
        cx, cz = level.allChunks.next()
        level.copyBlocksFrom(indevlevel, BoundingBox((0, 0, 0), (256, 128, 256)), (cx * 16, 0, cz * 16))

        convertedSourceBlocks, convertedSourceData = indevlevel.convertBlocksFromLevel(level, indevlevel.Blocks[0:16, 0:16, 0:indevlevel.Height], indevlevel.Data[0:16, 0:16, 0:indevlevel.Height])
        assert (level.getChunk(cx, cz).Blocks[0:16, 0:16, 0:indevlevel.Height] == convertedSourceBlocks).all()

    def testImportSchematic(self):
        level = self.anvilLevel.level
        cx, cz = level.allChunks.next()

        schem = mclevel.fromFile("schematics/CreativeInABox.schematic")
        box = BoundingBox((cx * 16, 64, cz * 16), schem.bounds.size)
        level.copyBlocksFrom(schem, schem.bounds, (0, 64, 0))
        schem = MCSchematic(shape=schem.bounds.size)
        schem.copyBlocksFrom(level, box, (0, 0, 0))
        convertedSourceBlocks, convertedSourceData = schem.convertBlocksFromLevel(level, schem.Blocks, schem.Data)
        assert (level.getChunk(cx, cz).Blocks[0:1, 0:3, 64:65] == convertedSourceBlocks).all()

    def testRecreateChunks(self):
        level = self.anvilLevel.level

        for x, z in itertools.product(xrange(-1, 3), xrange(-1, 2)):
            level.deleteChunk(x, z)
            assert not level.containsChunk(x, z)
            level.createChunk(x, z)

    def testFill(self):
        level = self.anvilLevel.level
        cx, cz = level.allChunks.next()
        box = BoundingBox((cx * 16, 0, cz * 16), (32, level.Height, 32))
        level.fillBlocks(box, level.materials.WoodPlanks)
        level.saveInPlace()
        c = level.getChunk(cx, cz)

        assert (c.Blocks == 5).all()

    def testReplace(self):
        level = self.anvilLevel.level

        level.fillBlocks(BoundingBox((-11, 0, -7), (38, level.Height, 25)), level.materials.WoodPlanks, [level.materials.Dirt, level.materials.Grass])

    def testSaveRelight(self):
        indevlevel = self.indevLevel.level
        level = self.anvilLevel.level

        cx, cz = -3, -1

        level.deleteChunk(cx, cz)

        level.createChunk(cx, cz)
        level.copyBlocksFrom(indevlevel, BoundingBox((0, 0, 0), (32, 64, 32,)), level.bounds.origin)

        level.generateLights()
        level.saveInPlace()

    def testRecompress(self):
        level = self.anvilLevel.level
        cx, cz = level.allChunks.next()

        ch = level.getChunk(cx, cz)
        ch.dirty = True
        ch.Blocks[:] = 6
        ch.Data[:] = 13
        d = {}
        keys = 'Blocks Data SkyLight BlockLight'.split()
        for key in keys:
            d[key] = numpy.array(getattr(ch, key))

        for i in range(5):
            level.saveInPlace()
            ch = level.getChunk(cx, cz)
            ch.dirty = True
            assert (ch.Data == 13).all()
            for key in keys:
                assert (d[key] == getattr(ch, key)).all()

    def testPlayerSpawn(self):
        level = self.anvilLevel.level

        level.setPlayerSpawnPosition((0, 64, 0), "Player")
        level.getPlayerPosition()
        assert len(level.players) != 0
