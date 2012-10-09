import os
import numpy
import nbt
from alpha_test import TestAlphaLevel
from templevel import TempLevel, mktemp

__author__ = 'Rio'

class TestAnvil(TestAlphaLevel):
    def setUp(self):
        self.indevlevel = TempLevel("hell.mclevel")
        self.alphalevel = TempLevel("AnvilWorld")

    def testAnvilChunk(self):
        """ Test modifying, saving, and loading the new TAG_Int_Array heightmap
        added with the Anvil format.
        """
        chunk = nbt.load("testfiles/AnvilChunk.dat")

        hm = chunk["Level"]["HeightMap"]
        hm.value[2] = 500
        oldhm = numpy.array(hm.value)

        filename = mktemp("ChangedChunk")
        chunk.save(filename)
        changedChunk = nbt.load(filename)
        os.unlink(filename)

        eq = (changedChunk["Level"]["HeightMap"].value == oldhm)
        assert eq.all()
