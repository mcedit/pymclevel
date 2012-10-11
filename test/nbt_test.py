from cStringIO import StringIO
import os
from os.path import join
import time
import unittest
import numpy
import nbt
from test.templevel import TempLevel

__author__ = 'Rio'

class TestNBT():

    def testLoad(self):
        "Load an indev level."
        level = nbt.load("testfiles/hell.mclevel")

        """The root tag must have a name, and so must any tag within a TAG_Compound"""
        print level.name

        """Use the [] operator to look up subtags of a TAG_Compound."""
        print level["Environment"]["SurroundingGroundHeight"].value

        """Numeric, string, and bytearray types have a value that can be accessed and changed. """
        print level["Map"]["Blocks"].value

        return level

    def testCreate(self):
        "Create an indev level."

        "The root of an NBT file is always a TAG_Compound."
        level = nbt.TAG_Compound(name="MinecraftLevel")

        "Subtags of a TAG_Compound are automatically named when you use the [] operator."
        level["About"] = nbt.TAG_Compound()
        level["About"]["Author"] = nbt.TAG_String("codewarrior")

        level["Environment"] = nbt.TAG_Compound()
        level["Environment"]["SkyBrightness"] = nbt.TAG_Byte(16)
        level["Environment"]["SurroundingWaterHeight"] = nbt.TAG_Short(32)

        "You can also create and name a tag before adding it to the compound."
        spawn = nbt.TAG_List((nbt.TAG_Short(100), nbt.TAG_Short(45), nbt.TAG_Short(55)))
        spawn.name = "Spawn"

        mapTag = nbt.TAG_Compound()
        mapTag.add(spawn)
        mapTag.name = "Map"
        level.add(mapTag)

        "I think it looks more familiar with [] syntax."

        l, w, h = 128, 128, 128
        mapTag["Height"] = nbt.TAG_Short(h)  # y dimension
        mapTag["Length"] = nbt.TAG_Short(l)  # z dimension
        mapTag["Width"] = nbt.TAG_Short(w)  # x dimension

        "Byte arrays are stored as numpy.uint8 arrays. "

        mapTag["Blocks"] = nbt.TAG_Byte_Array()
        mapTag["Blocks"].value = numpy.zeros(l * w * h, dtype=numpy.uint8)  # create lots of air!

        "The blocks array is indexed (y,z,x) for indev levels, so reshape the blocks"
        mapTag["Blocks"].value.shape = (h, l, w)

        "Replace the bottom layer of the indev level with wood"
        mapTag["Blocks"].value[0, :, :] = 5

        "This is a great way to learn the power of numpy array slicing and indexing."

        mapTag["Data"] = nbt.TAG_Byte_Array()
        mapTag["Data"].value = numpy.zeros(l * w * h, dtype=numpy.uint8)

        return level

    def testModify(self):
        level = self.testCreate()

        "Most of the value types work as expected. Here, we replace the entire tag with a TAG_String"
        level["About"]["Author"] = nbt.TAG_String("YARRR~!")

        "Because the tag type usually doesn't change, "
        "we can replace the string tag's value instead of replacing the entire tag."
        level["About"]["Author"].value = "Stew Pickles"

        "Remove members of a TAG_Compound using del, similar to a python dict."
        del(level["About"])

        "Replace all of the wood blocks with gold using a boolean index array"
        blocks = level["Map"]["Blocks"].value
        blocks[blocks == 5] = 41

    def testSave(self):

        level = self.testCreate()
        level["Environment"]["SurroundingWaterHeight"].value += 6

        "Save the entire TAG structure to a different file."
        TempLevel("atlantis.mclevel", createFunc=level.save)

    def testErrors(self):
        """
        attempt to name elements of a TAG_List
        named list elements are not allowed by the NBT spec,
        so we must discard any names when writing a list.
        """

        level = self.testCreate()
        level["Map"]["Spawn"][0].name = "Torg Potter"
        data = level.save()
        newlevel = nbt.load(buf=data)

        n = newlevel["Map"]["Spawn"][0].name
        if n:
            print "Named list element failed: %s" % n

        """
        attempt to delete non-existent TAG_Compound elements
        this generates a KeyError like a python dict does.
        """
        level = self.testCreate()
        try:
            del level["DEADBEEF"]
        except KeyError:
            pass
        else:
            assert False

    def testSpeed(self):
        d = join("testfiles", "TileTicks_chunks")
        files = [join(d, f) for f in os.listdir(d)]
        startTime = time.time()
        for f in files[:40]:
            n = nbt.load(f)
        print "Duration: ", time.time() - startTime

