'''
Created on Jul 22, 2011

@author: Rio
'''

import blockrotation
from contextlib import closing
from cStringIO import StringIO
from box import BoundingBox
import gzip
from level import MCLevel, EntityLevel
from logging import getLogger
from materials import alphaMaterials, MCMaterials, namedMaterials
from mclevelbase import Blocks, ChunkMalformed, Data, decompress_first, Entities, exhaust, Height, Length, TileEntities, unpack_first, Width
import nbt
from numpy import array, swapaxes, uint8, zeros
import os
import shutil
import sys

log = getLogger(__name__)
warn, error, info, debug = log.warn, log.error, log.info, log.debug

# schematic
Materials = 'Materials'

__all__ = ['MCSchematic', 'INVEditChest']


class MCSchematic (EntityLevel):
    materials = alphaMaterials

    def __init__(self, shape=None, root_tag=None, filename=None, mats='Alpha'):
        """ shape is (x,y,z) for a new level's shape.  if none, takes
        root_tag as a TAG_Compound for an existing schematic file.  if
        none, tries to read the tag from filename.  if none, results
        are undefined. materials can be a MCMaterials instance, or one of
        "Classic", "Alpha", "Pocket" to indicate allowable blocks. The default
        is Alpha.

        block coordinate order in the file is y,z,x to use the same code as classic/indev levels.
        in hindsight, this was a completely arbitrary decision.

        the Entities and TileEntities are nbt.TAG_List objects containing TAG_Compounds.
        this makes it easy to copy entities without knowing about their insides.

        rotateLeft swaps the axes of the different arrays.  because of this, the Width, Height, and Length
        reflect the current dimensions of the schematic rather than the ones specified in the NBT structure.
        I'm not sure what happens when I try to re-save a rotated schematic.
        """

        # if(shape != None):
        #    self.setShape(shape)

        if filename:
            self.filename = filename
            if None is root_tag and os.path.exists(filename):
                root_tag = nbt.load(filename)
        else:
            self.filename = None

        if mats in namedMaterials:
            self.materials = namedMaterials[mats]
        else:
            assert(isinstance(mats, MCMaterials))
            self.materials = mats

        if root_tag:
            self.root_tag = root_tag
            if Materials in root_tag:
                self.materials = namedMaterials[self.Materials]
            else:
                root_tag[Materials] = nbt.TAG_String(self.materials.name)
            self.shapeChunkData()

        else:
            assert shape != None
            root_tag = nbt.TAG_Compound(name="Schematic")
            root_tag[Height] = nbt.TAG_Short(shape[1])
            root_tag[Length] = nbt.TAG_Short(shape[2])
            root_tag[Width] = nbt.TAG_Short(shape[0])

            root_tag[Entities] = nbt.TAG_List()
            root_tag[TileEntities] = nbt.TAG_List()
            root_tag["Materials"] = nbt.TAG_String(self.materials.name)

            root_tag[Blocks] = nbt.TAG_Byte_Array(zeros((shape[1], shape[2], shape[0]), uint8))
            root_tag[Data] = nbt.TAG_Byte_Array(zeros((shape[1], shape[2], shape[0]), uint8))

            self.root_tag = root_tag

        self.dataIsPacked = True

    def __str__(self):
        return u"MCSchematic(shape={0}, materials={2}, filename=\"{1}\")".format(self.size, self.filename or u"", self.Materials)

    def compress(self):
        # if self.root_tag is not None, then our compressed data must be stale and we need to recompress.

        if self.root_tag is None:
            return
        else:
            self.packChunkData()
            self.compressedTag = self.root_tag.save(compressed=False)

        self.root_tag = None

    def decompress(self):
        """called when accessing attributes decorated with @decompress_first"""
        if self.root_tag != None:
            return
        if self.compressedTag is None:
            if self.root_tag is None:
                self.load()
            else:
                return

        with closing(gzip.GzipFile(fileobj=StringIO(self.compressedTag))) as gzipper:
            try:
                data = gzipper.read()
                if data == None:
                    return
            except Exception, e:
                # error( u"Error reading compressed data, assuming uncompressed: {0}".format(e) )
                data = self.compressedTag

        try:
            self.root_tag = nbt.load(buf=data)
        except MemoryError:
             raise
        except Exception, e:
            error(u"Malformed NBT data in schematic file: {0} ({1})".format(self.filename, e))
            raise ChunkMalformed, self.filename, sys.exc_info()[2]

        try:
            self.shapeChunkData()
        except KeyError, e:
            error(u"Incorrect schematic format in file: {0} ({1})".format(self.filename, e))
            raise ChunkMalformed, self.filename, sys.exc_info()[2]
        pass

        self.dataIsPacked = True

    # these refer to the blocks array instead of the file's height because rotation swaps the axes
    # this will have an impact later on when editing schematics instead of just importing/exporting
    @property
    @decompress_first
    def Length(self):
        return self.Blocks.shape[1]

    @property
    @decompress_first
    def Width(self):
        return self.Blocks.shape[0]

    @property
    @decompress_first
    def Height(self):
        return self.Blocks.shape[2]

    @property
    @decompress_first
    @unpack_first
    def Blocks(self):
        return self.root_tag[Blocks].value

    @Blocks.setter
    @decompress_first
    @unpack_first
    def Blocks(self, newval):
        self.root_tag[Blocks].value = newval

    @property
    @decompress_first
    @unpack_first
    def Data(self):
        return self.root_tag[Data].value

    @Data.setter
    @decompress_first
    @unpack_first
    def Data(self, newval):
        self.root_tag[Data].value = newval

    @property
    @decompress_first
    def Entities(self):
        return self.root_tag[Entities]

    @property
    @decompress_first
    def TileEntities(self):
        return self.root_tag[TileEntities]

    @property
    @decompress_first
    def Materials(self):
        return self.root_tag[Materials].value

    @Materials.setter
    @decompress_first
    def Materials(self, val):
        if not Materials in self.root_tag:
            self.root_tag[Materials] = nbt.TAG_String()
        self.root_tag[Materials].value = val

    @classmethod
    def _isTagLevel(cls, root_tag):
        return "Schematic" == root_tag.name

    def shapeChunkData(self):
        w = self.root_tag[Width].value
        l = self.root_tag[Length].value
        h = self.root_tag[Height].value

        self.root_tag[Blocks].value.shape = (h, l, w)
        self.root_tag[Data].value.shape = (h, l, w)

    def packUnpack(self):
        self.root_tag[Blocks].value = swapaxes(self.root_tag[Blocks].value, 0, 2)  # yzx to xzy
        self.root_tag[Data].value = swapaxes(self.root_tag[Data].value, 0, 2)  # yzx to xzy
        if self.dataIsPacked:
            self.root_tag[Data].value &= 0xF  # discard high bits

    def packChunkData(self):
        if not self.dataIsPacked:
            self.packUnpack()
            self.dataIsPacked = True

    def unpackChunkData(self):
        if self.dataIsPacked:
            self.packUnpack()
            self.dataIsPacked = False

    def _update_shape(self):
        root_tag = self.root_tag
        shape = self.Blocks.shape
        root_tag[Height] = nbt.TAG_Short(shape[2])
        root_tag[Length] = nbt.TAG_Short(shape[1])
        root_tag[Width] = nbt.TAG_Short(shape[0])

    def rotateLeft(self):

        self.Blocks = swapaxes(self.Blocks, 1, 0)[:, ::-1, :]  # x=z; z=-x
        self.Data = swapaxes(self.Data, 1, 0)[:, ::-1, :]  # x=z; z=-x
        self._update_shape()

        blockrotation.RotateLeft(self.Blocks, self.Data)

        info(u"Relocating entities...")
        for entity in self.Entities:
            for p in "Pos", "Motion":
                if p == "Pos":
                    zBase = self.Length
                else:
                    zBase = 0.0
                newX = entity[p][2].value
                newZ = zBase - entity[p][0].value

                entity[p][0].value = newX
                entity[p][2].value = newZ
            entity["Rotation"][0].value -= 90.0
            if entity["id"].value == "Painting":
                x, z = entity["TileX"].value, entity["TileZ"].value
                newx = z
                newz = self.Length - x - 1

                entity["TileX"].value, entity["TileZ"].value = newx, newz
                entity["Dir"].value = (entity["Dir"].value + 1) % 4

        for tileEntity in self.TileEntities:
            if not 'x' in tileEntity:
                continue

            newX = tileEntity["z"].value
            newZ = self.Length - tileEntity["x"].value - 1

            tileEntity["x"].value = newX
            tileEntity["z"].value = newZ

    def roll(self):
        " xxx rotate stuff "
        self.Blocks = swapaxes(self.Blocks, 2, 0)[:, :, ::-1]  # x=z; z=-x
        self.Data = swapaxes(self.Data, 2, 0)[:, :, ::-1]
        self._update_shape()

    def flipVertical(self):
        " xxx delete stuff "
        blockrotation.FlipVertical(self.Blocks, self.Data)
        self.Blocks = self.Blocks[:, :, ::-1]  # y=-y
        self.Data = self.Data[:, :, ::-1]

    def flipNorthSouth(self):
        blockrotation.FlipNorthSouth(self.Blocks, self.Data)
        self.Blocks = self.Blocks[::-1, :, :]  # x=-x
        self.Data = self.Data[::-1, :, :]

        northSouthPaintingMap = [0, 3, 2, 1]

        info(u"N/S Flip: Relocating entities...")
        for entity in self.Entities:

            entity["Pos"][0].value = self.Width - entity["Pos"][0].value
            entity["Motion"][0].value = -entity["Motion"][0].value

            entity["Rotation"][0].value -= 180.0

            if entity["id"].value == "Painting":
                entity["TileX"].value = self.Width - entity["TileX"].value
                entity["Dir"].value = northSouthPaintingMap[entity["Dir"].value]

        for tileEntity in self.TileEntities:
            if not 'x' in tileEntity:
                continue

            tileEntity["x"].value = self.Width - tileEntity["x"].value - 1

    def flipEastWest(self):
        " xxx flip entities "
        blockrotation.FlipEastWest(self.Blocks, self.Data)
        self.Blocks = self.Blocks[:, ::-1, :]  # z=-z
        self.Data = self.Data[:, ::-1, :]

        eastWestPaintingMap = [2, 1, 0, 3]

        info(u"E/W Flip: Relocating entities...")
        for entity in self.Entities:

            entity["Pos"][2].value = self.Length - entity["Pos"][2].value
            entity["Motion"][2].value = -entity["Motion"][2].value

            entity["Rotation"][0].value -= 180.0

            if entity["id"].value == "Painting":
                entity["TileZ"].value = self.Length - entity["TileZ"].value
                entity["Dir"].value = eastWestPaintingMap[entity["Dir"].value]

        for tileEntity in self.TileEntities:
            tileEntity["z"].value = self.Length - tileEntity["z"].value - 1

    @decompress_first
    def setShape(self, shape):
        """shape is a tuple of (width, height, length).  sets the
        schematic's properties and clears the block and data arrays"""

        x, y, z = shape
        shape = (x, z, y)

        self.root_tag[Blocks].value = zeros(dtype='uint8', shape=shape)
        self.root_tag[Data].value = zeros(dtype='uint8', shape=shape)
        self.shapeChunkData()

    def saveToFile(self, filename=None):
        """ save to file named filename, or use self.filename.  XXX NOT THREAD SAFE AT ALL. """
        if filename == None:
            filename = self.filename
        if filename == None:
            warn(u"Attempted to save an unnamed schematic in place")
            return  # you fool!

        self.Materials = self.materials.name

        self.compress()

        with open(filename, 'wb') as chunkfh:
            chunkfh.write(self.compressedTag)

    def setBlockDataAt(self, x, y, z, newdata):
        if x < 0 or y < 0 or z < 0:
            return 0
        if x >= self.Width or y >= self.Height or z >= self.Length:
            return 0
        self.Data[x, z, y] = (newdata & 0xf)

    def blockDataAt(self, x, y, z):
        if x < 0 or y < 0 or z < 0:
            return 0
        if x >= self.Width or y >= self.Height or z >= self.Length:
            return 0
        return self.Data[x, z, y]

    @classmethod
    def chestWithItemID(self, itemID, count=64, damage=0):
        """ Creates a chest with a stack of 'itemID' in each slot.
        Optionally specify the count of items in each stack. Pass a negative
        value for damage to create unnaturally sturdy tools. """
        root_tag = nbt.TAG_Compound()
        invTag = nbt.TAG_List()
        root_tag["Inventory"] = invTag
        for slot in range(9, 36):
            itemTag = nbt.TAG_Compound()
            itemTag["Slot"] = nbt.TAG_Byte(slot)
            itemTag["Count"] = nbt.TAG_Byte(count)
            itemTag["id"] = nbt.TAG_Short(itemID)
            itemTag["Damage"] = nbt.TAG_Short(damage)
            invTag.append(itemTag)

        chest = INVEditChest(root_tag, "")

        return chest


class INVEditChest(MCSchematic):
    Width = 1
    Height = 1
    Length = 1
    Blocks = array([[[alphaMaterials.Chest.ID]]], 'uint8')
    Data = array([[[0]]], 'uint8')
    Entities = nbt.TAG_List()
    Materials = alphaMaterials

    @classmethod
    def _isTagLevel(cls, root_tag):
        return "Inventory" in root_tag

    def __init__(self, root_tag, filename):

        if filename:
            self.filename = filename
            if None is root_tag:
                try:
                    root_tag = nbt.load(filename)
                except IOError, e:
                    info(u"Failed to load file {0}".format(e))
                    raise
        else:
            assert root_tag, "Must have either root_tag or filename"
            self.filename = None

        for item in list(root_tag["Inventory"]):
            slot = item["Slot"].value
            if slot < 9 or slot >= 36:
                root_tag["Inventory"].remove(item)
            else:
                item["Slot"].value -= 9  # adjust for different chest slot indexes

        self.root_tag = root_tag

    @property
    @decompress_first
    def TileEntities(self):
        chestTag = nbt.TAG_Compound()
        chestTag["id"] = nbt.TAG_String("Chest")
        chestTag["Items"] = nbt.TAG_List(self.root_tag["Inventory"])
        chestTag["x"] = nbt.TAG_Int(0)
        chestTag["y"] = nbt.TAG_Int(0)
        chestTag["z"] = nbt.TAG_Int(0)

        return nbt.TAG_List([chestTag], name="TileEntities")


def adjustExtractionParameters(self, box):
    x, y, z = box.origin
    w, h, l = box.size
    destX = destY = destZ = 0

    if y < 0:
        destY -= y
        h += y
        y = 0

    if y >= self.Height:
        return

    if y + h >= self.Height:
        h -= y + h - self.Height
        y = self.Height - h

    if h <= 0:
        return

    if self.Width:
        if x < 0:
            w += x
            destX -= x
            x = 0
        if x >= self.Width:
            return

        if x + w >= self.Width:
            w = self.Width - x

        if w <= 0:
            return

        if z < 0:
            l += z
            destZ -= z
            z = 0

        if z >= self.Length:
            return

        if z + l >= self.Length:
            l = self.Length - z

        if l <= 0:
            return

    box = BoundingBox((x, y, z), (w, h, l))

    return box, (destX, destY, destZ)


def extractSchematicFrom(sourceLevel, box, entities=True):
    return exhaust(extractSchematicFromIter(sourceLevel, box, entities))


def extractSchematicFromIter(sourceLevel, box, entities=True):
    p = sourceLevel.adjustExtractionParameters(box)
    if p is None:
        yield None
        return
    newbox, destPoint = p

    tempSchematic = MCSchematic(shape=box.size, mats=sourceLevel.materials)
    for i in tempSchematic.copyBlocksFromIter(sourceLevel, newbox, destPoint, entities=entities):
        yield i

    yield tempSchematic

MCLevel.extractSchematic = extractSchematicFrom
MCLevel.extractSchematicIter = extractSchematicFromIter
MCLevel.adjustExtractionParameters = adjustExtractionParameters

import tempfile


def extractZipSchematicFrom(sourceLevel, box, zipfilename=None, entities=True):
    return exhaust(extractZipSchematicFromIter(sourceLevel, box, zipfilename, entities))


def extractZipSchematicFromIter(sourceLevel, box, zipfilename=None, entities=True):
    # converts classic blocks to alpha
    # probably should only apply to alpha levels

    if zipfilename is None:
        zipfilename = tempfile.mktemp("zipschematic")

    p = sourceLevel.adjustExtractionParameters(box)
    if p is None:
        return
    sourceBox, destPoint = p

    destPoint = (0, 0, 0)

    tempfolder = tempfile.mktemp("schematic")
    try:
        tempSchematic = MCInfdevOldLevel(tempfolder, create=True)
        tempSchematic.materials = sourceLevel.materials

        for i in tempSchematic.copyBlocksFromIter(sourceLevel, sourceBox, destPoint, entities=entities, create=True):
            yield i
        tempSchematic.saveInPlace()  # lights not needed for this format - crashes minecraft though

        schematicDat = nbt.TAG_Compound()
        schematicDat.name = "Mega Schematic"

        schematicDat["Width"] = nbt.TAG_Int(sourceBox.size[0])
        schematicDat["Height"] = nbt.TAG_Int(sourceBox.size[1])
        schematicDat["Length"] = nbt.TAG_Int(sourceBox.size[2])
        schematicDat["Materials"] = nbt.TAG_String(tempSchematic.materials.name)
        schematicDat.save(os.path.join(tempfolder, "schematic.dat"))

        zipdir(tempfolder, zipfilename)

        import mclevel
        yield mclevel.fromFile(zipfilename)
    finally:
        # We get here if the generator is GCed also
        if os.path.exists(tempfolder):
            shutil.rmtree(tempfolder, False)

MCLevel.extractZipSchematic = extractZipSchematicFrom
MCLevel.extractZipSchematicIter = extractZipSchematicFromIter


def extractAnySchematic(level, box):
    return exhaust(level.extractAnySchematicIter(box))


def extractAnySchematicIter(level, box):
    try:
        if box.chunkCount > MCInfdevOldLevel.decompressedChunkLimit:
            raise MemoryError

        for i in level.extractSchematicIter(box):
            yield i
    except MemoryError:
        for i in level.extractZipSchematicIter(box):
            yield i

MCLevel.extractAnySchematic = extractAnySchematic
MCLevel.extractAnySchematicIter = extractAnySchematicIter

from zipfile import ZipFile, ZIP_STORED


def zipdir(basedir, archivename):
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_STORED)) as z:
        for root, dirs, files in os.walk(basedir):
            # NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir) + len(os.sep):]  # XXX: relative path
                z.write(absfn, zfn)

from infiniteworld import MCInfdevOldLevel
