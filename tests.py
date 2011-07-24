'''
Created on Jul 23, 2011

@author: Rio
'''
from mclevel import fromFile, loadWorldNumber, BoundingBox
from infiniteworld import MCInfdevOldLevel
from schematic import MCSchematic

import itertools
import traceback
import unittest
import tempfile
import logging
import shutil
import os
import numpy
from numpy import *
from logging import info
#logging.basicConfig(format=u'%(levelname)s:%(message)s')
#logging.getLogger().level = logging.INFO

class TempLevel(object):
    def __init__(self, filename):
        if not os.path.exists(filename):
            filename = os.path.join("testfiles", filename)
#def tempCopy(filename):
        if os.path.isdir(filename):
            tmpname = tempfile.mkdtemp(os.path.basename(filename))
            os.rmdir(tmpname)
            shutil.copytree(filename, tmpname)
        else:
            fd, tmpname = tempfile.mkstemp(os.path.basename(filename))
            os.close(fd)
            os.unlink(tmpname)
            shutil.copy(filename, tmpname)

        self.tmpname = tmpname
        self.level = fromFile(tmpname)

#def tempRemove(filename):
    def __del__(self):
        self.level.close()
        del self.level
        filename = self.tmpname

        if os.path.isdir(filename):
            shutil.rmtree(filename)
        else:
            os.unlink(filename)

class TestIndevLevel(unittest.TestCase):
    def setUp(self):
        self.srclevel = TempLevel("hell.mclevel")
        self.indevlevel = TempLevel("hueg.mclevel")


    def testCopy(self):
        info("Indev level")
        indevlevel = self.indevlevel.level
        srclevel = self.srclevel.level
        indevlevel.copyBlocksFrom(srclevel, BoundingBox((0, 0, 0), (64, 64, 64,)), (0, 0, 0))
        assert((indevlevel.Blocks[0:64, 0:64, 0:64] == srclevel.Blocks[0:64, 0:64, 0:64]).all())

    def testFill(self):
        indevlevel = self.indevlevel.level
        indevlevel.fillBlocks(BoundingBox((0, 0, 0), (64, 64, 64,)), indevlevel.materials.Sand, [indevlevel.materials.Rock, indevlevel.materials.Dirt])
        indevlevel.saveInPlace()


class TestJavaLevel(unittest.TestCase):
    def setUp(self):
        self.creativelevel = TempLevel("Dojo_64_64_128.dat")
        self.indevlevel = TempLevel("hell.mclevel")

    def testCopy(self):
        indevlevel = self.indevlevel.level
        creativelevel = self.creativelevel.level

        creativelevel.copyBlocksFrom(indevlevel, BoundingBox((0, 0, 0), (64, 64, 64,)), (0, 0, 0))
        assert(numpy.array((indevlevel.Blocks[0:64, 0:64, 0:64]) == (creativelevel.Blocks[0:64, 0:64, 0:64])).all())

        creativelevel.saveInPlace()
        #xxx old survival levels


class TestAlphaLevelCreate(unittest.TestCase):
    def testCreate(self):
        temppath = tempfile.mktemp("AlphaCreate")
        self.alphaLevel = MCInfdevOldLevel(filename=temppath, create=True);

class TestAlphaLevel(unittest.TestCase):
    def setUp(self):
        #self.alphaLevel = TempLevel("Dojo_64_64_128.dat")
        self.indevlevel = TempLevel("hell.mclevel")
        self.alphalevel = TempLevel("PyTestWorld")


    def testAlphaLevels(self):
        info("Alpha level")

        indevlevel = self.indevlevel.level

        level = self.alphalevel.level
        for ch in list(level.allChunks): level.deleteChunk(*ch)
        level.createChunksInBox(BoundingBox((0, 0, 0), (32, 0, 32)))
        level.copyBlocksFrom(indevlevel, BoundingBox((0, 0, 0), (256, 128, 256)), (-0, 0, 0))

        convertedSourceBlocks, convertedSourceData = indevlevel.convertBlocksFromLevel(level, indevlevel.Blocks[0:16, 0:16, 0:indevlevel.Height], indevlevel.Data[0:16, 0:16, 0:indevlevel.Height])
        assert (level.getChunk(0, 0).Blocks[0:16, 0:16, 0:indevlevel.Height] == convertedSourceBlocks).all()

        schem = fromFile("schematics\\CreativeInABox.schematic");
        level.copyBlocksFrom(schem, BoundingBox((0, 0, 0), (1, 1, 3)), (0, 64, 0));
        schem = MCSchematic(shape=(1, 1, 3))
        schem.copyBlocksFrom(level, BoundingBox((0, 64, 0), (1, 1, 3)), (0, 0, 0));
        convertedSourceBlocks, convertedSourceData = schem.convertBlocksFromLevel(level, schem.Blocks, schem.Data)
        assert (level.getChunk(0, 0).Blocks[0:1, 0:3, 64:65] == convertedSourceBlocks).all()

        try:
            for x, z in itertools.product(xrange(-1, 3), xrange(-1, 2)):
                level.deleteChunk(x, z);
                level.createChunk(x, z)
        except Exception, e:
            traceback.print_exc();
            print e;
        level.fillBlocks(BoundingBox((-11, 0, -7), (38, 128, 25)) , indevlevel.materials.WoodPlanks);
        c = level.getChunk(0, 0)
        assert (c.Blocks == 5).all()
        level.fillBlocks(BoundingBox((-11, 0, -7), (38, 128, 25)) , indevlevel.materials.WoodPlanks, [indevlevel.materials.Dirt, indevlevel.materials.Grass]);
        #print b.shape
        #raise SystemExit
        cx, cz = -3, -1;

        try:
            level.deleteChunk(cx, cz);
        except KeyError:pass
        level.createChunk(cx, cz);
        level.copyBlocksFrom(indevlevel, BoundingBox((0, 0, 0), (64, 64, 64,)), (-96, 32, 0))
        #blocks = zeros((16,16,128), 'uint8');
        #blocks[:,:,:] = level.getChunk(cx, cz).Blocks[:,:,:]
        #level.getChunk(cx, cz).Blocks[:,:,:] = blocks[:,:,:]
        level.generateLights();
        level.saveInPlace();

        level.saveInPlace();


class TestSchematics(unittest.TestCase):
    def setUp(self):
        #self.alphaLevel = TempLevel("Dojo_64_64_128.dat")
        self.indevlevel = TempLevel("hell.mclevel")

    def testCreate(self):
        #info("Schematic from indev")

        size = (64, 64, 64)
        schematic = MCSchematic(shape=size, filename="hell.schematic", mats='Classic');
        level = self.indevlevel.level
        schematic.rotateLeft();
        try:
            schematic.copyBlocksFrom(level, BoundingBox((-32, -32, -32), (64, 64, 64,)), (0, 0, 0))
        except ValueError:
            pass;


        schematic.copyBlocksFrom(level, BoundingBox((0, 0, 0), (64, 64, 64,)), (0, 0, 0))
        assert((schematic.Blocks[0:64, 0:64, 0:64] == level.Blocks[0:64, 0:64, 0:64]).all())
        schematic.compress();

        schematic.copyBlocksFrom(level, BoundingBox((0, 0, 0), (64, 64, 64,)), (-32, -32, -32))
        assert((schematic.Blocks[0:32, 0:32, 0:32] == level.Blocks[32:64, 32:64, 32:64]).all())

        schematic.compress();

        schematic.saveInPlace();

        schem = fromFile("schematics\CreativeInABox.schematic");
        tempSchematic = MCSchematic(shape=(1, 1, 3))
        tempSchematic.copyBlocksFrom(schem, BoundingBox((0, 0, 0), (1, 1, 3)), (0, 0, 0))

        info("Schematic from alpha")
        level = loadWorldNumber(1)
        for cx, cz in itertools.product(xrange(0, 4), xrange(0, 4)):
            try:
                level.createChunk(cx, cz)
            except ValueError:
                pass
        schematic.copyBlocksFrom(level, BoundingBox((0, 0, 0), (64, 64, 64,)), (0, 0, 0))

    def testINVEditChests(self):
        info("INVEdit chest")
        invFile = fromFile("schematics/Chests/TinkerersBox.inv");
        info("Blocks: ", invFile.Blocks)
        info("Data: ", invFile.Data)
        info("Entities: ", invFile.Entities)
        info("TileEntities: ", invFile.TileEntities)
        #raise SystemExit;

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
