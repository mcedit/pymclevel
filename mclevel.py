# -*- coding: utf-8 -*-
"""
MCLevel interfaces

Sample usage:

import mclevel

# Call mclevel.fromFile to identify and open any of these four file formats:
#
# Classic levels - gzipped serialized java objects.  Returns an instance of MCJavalevel
# Indev levels - gzipped NBT data in a single file.  Returns an MCIndevLevel
# Schematics - gzipped NBT data in a single file.  Returns an MCSchematic.  
#   MCSchematics have the special method rotateLeft which will reorient torches, stairs, and other tiles appropriately.
# Alpha levels - world folder structure containing level.dat and chunk folders.  Single or Multiplayer.
#   Can accept a path to the world folder or a path to the level.dat.  Returns an MCInfdevOldLevel

# Load a Classic level.
level = mclevel.fromFile("server_level.dat"); 

# fromFile identified the file type and returned a MCJavaLevel.  MCJavaLevel doesn't actually know any java. It guessed the
# location of the Blocks array by starting at the end of the file and moving backwards until it only finds valid blocks.
# It also doesn't know the dimensions of the level.  This is why you have to tell them to MCEdit via the filename.
# This works here too:  If the file were 512 wide, 512 long, and 128 high, I'd have to name it "server_level_512_512_128.dat"
#
# This is one area for improvement.

# Classic and Indev levels have all of their blocks in one place.
blocks = level.Blocks

# Sand to glass.
blocks[blocks == level.materials.Sand.ID] = level.materials.Glass.ID

# Save the file with another name.  This only works for non-Alpha levels.
level.saveToFile("server_level_glassy.dat");

# Load an Alpha world
# Loading an Alpha world immediately scans the folder for chunk files.  This takes longer for large worlds.
ourworld = mclevel.fromFile("C:\\Minecraft\\OurWorld");

# Convenience method to load a numbered world from the saves folder.
world1 = mclevel.loadWorldNumber(1);

# Find out which chunks are present. Doing this will scan the chunk folders the
# first time it is used. If you already know where you want to be, skip to 
# world1.getChunk(xPos, zPos)

chunkPositions = list(world1.allChunks)

# allChunks returns an iterator that yields a (xPos, zPos) tuple for each chunk
xPos, zPos = chunkPositions[0];

# retrieve an InfdevChunk object. this object will load and decompress 
# the chunk as needed, and remember whether it needs to be saved or relighted

chunk = world1.getChunk(xPos, zPos)

### Access the data arrays of the chunk like so:
# Take note that the array is indexed x, z, y.  The last index corresponds to 
# height or altitude.

blockType = chunk.Blocks[0,0,64]
chunk.Blocks[0,0,64] = 1

# Access the chunk's Entities and TileEntities as arrays of TAG_Compound as 
# they appear in the save format. 

# Entities usually have Pos, Health, and id
# TileEntities usually have tileX, tileY, tileZ, and id
# For more information, google "Chunk File Format"

for entity in chunk.Entities:
    if entity["id"].value == "Spider":
        entity["Health"].value = 50


# Accessing one byte at a time from the Blocks array is very slow in Python. 
# To get around this, we have methods to access multiple bytes at once.
# The first technique is slicing. You can use slicing to restrict your access
# to certain depth levels, or to extract a column or a larger section from the
# array. Standard python slice notation is used.

# Set the top half of the array to 0. The : says to use the entire array along
# that dimension. The syntax []= indicates we are overwriting part of the array
chunk.Blocks[:,:,64:] = 0

# Using [] without =  creates a 'view' on part of the array.  This is not a 
# copy, it is a reference to a portion of the original array.
midBlocks = chunk.Blocks[:,:,32:64]

# Here's a gotcha:  You can't just write 'midBlocks = 0' since it will replace
# the 'midBlocks' reference itself instead of accessing the array. Instead, do
# this to access and overwrite the array using []= syntax.
midBlocks[:] = 0
 

# The second is masking.  Using a comparison operator ( <, >, ==, etc ) 
# against the Blocks array will return a 'mask' that we can use to specify
# positions in the array.
 
# Create the mask from the result of the equality test.
fireBlocks = ( chunk.Blocks==world.materials.Fire.ID )

# Access Blocks using the mask to set elements. The syntax is the same as 
# using []= with slices
chunk.Blocks[fireBlocks] = world.materials.Leaves.ID

# You can also combine mask arrays using logical operations (&, |, ^) and use
# the mask to access any other array of the same shape.
# Here we turn all trees into birch trees.

# Extract a mask from the Blocks array to find the locations of tree trunks.
# Or | it with another mask to find the locations of leaves.
# Use the combined mask to access the Data array and set those locations to birch

# Note that the Data, BlockLight, and SkyLight arrays have been 
# unpacked from 4-bit arrays to numpy uint8 arrays. This makes them much easier
# to work with.

treeBlocks = ( chunk.Blocks == world.materials.Wood.ID )
treeBlocks |= ( chunk.Blocks == world.materials.Leaves.ID )
chunk.Data[treeBlocks] = 2 # birch


# The chunk doesn't know you've changed any of that data.  Call chunkChanged()
# to let it know. This will mark the chunk for lighting calculation, 
# recompression, and writing to disk. It will also immediately recalculate the 
# chunk's HeightMap and fill the SkyLight only with light falling straight down. 
# These are relatively fast and were added here to aid MCEdit.

chunk.chunkChanged();

# To recalculate all of the dirty lights in the world, call generateLights
world.generateLights();


# Move the player and his spawn
world.setPlayerPosition( (0, 67, 0) ) # add 3 to make sure his head isn't in the ground.
world.setPlayerSpawnPosition( (0, 64, 0) )


# Save the level.dat and any chunks that have been marked for writing to disk
# This also compresses any chunks marked for recompression.
world.saveInPlace();


# Advanced use:
# The getChunkSlices method returns an iterator that returns slices of chunks within the specified range.
# the slices are returned as tuples of (chunk, slices, point)

# chunk:  The InfdevChunk object we're interested in.
# slices:  A 3-tuple of slice objects that can be used to index chunk's data arrays
# point:  A 3-tuple of floats representing the relative position of this subslice within the larger slice.
# 
# Take caution:
# the point tuple is ordered (x,y,z) in accordance with the tuples used to initialize a bounding box
# however, the slices tuple is ordered (x,z,y) for easy indexing into the arrays.

# Here is an old version of MCInfdevOldLevel.fillBlocks in its entirety:

def fillBlocks(self, box, blockType, blockData = 0):
    chunkIterator = self.getChunkSlices(box)
    
    for (chunk, slices, point) in chunkIterator:
        chunk.Blocks[slices] = blockType
        chunk.Data[slices] = blockData
        chunk.chunkChanged();


Copyright 2010 David Rio Vierra
"""

try:
    import psyco
    psyco.full()
except:
    pass
    
import nbt
import operator
import functools
from nbt import *
import struct
import gzip
import StringIO
from numpy import *
import itertools
import traceback
import os;
import sys;
import tempfile

from contextlib import closing
from zipfile import ZipFile, ZIP_STORED, is_zipfile
from collections import deque;

import blockrotation
from materials import classicMaterials, alphaMaterials, namedMaterials, MCMaterials, materialNames

from copy import deepcopy
import time
from datetime import datetime;
from box import BoundingBox

import logging
from logging import log, debug, warn, info, error, critical

FaceXIncreasing = 0
FaceXDecreasing = 1
FaceYIncreasing = 2
FaceYDecreasing = 3
FaceZIncreasing = 4
FaceZDecreasing = 5
MaxDirections = 6

#as it turns out, you can't pass unicode strings to path.expandxxx because it 
#returns the expanded path as a byte array encoded for the filesystem routines, 
# but unicode string formatters and whatnot try to decode it as 'ascii'

# this basically means you can't print them without knowing the filesystem encoding


minecraftDirs = {
    'darwin':os.path.expanduser("~/Library/Application Support/minecraft"),
}
minecraftDir = minecraftDirs.get(sys.platform, os.path.expanduser("~/.minecraft")); #default to Linux save location 
minecraftDir = minecraftDir.decode(sys.getfilesystemencoding());

if sys.platform == "win32":
    #not sure why win32com is needed if the %APPDATA% var is available
    try:      
        import win32com.client
        
        objShell = win32com.client.Dispatch("WScript.Shell")
        minecraftDir = os.path.join(objShell.SpecialFolders("AppData"), u".minecraft")
    except Exception, e:
        print "WScript error {0!r}".format(e)
        appdata = os.environ['APPDATA'].decode(sys.getfilesystemencoding());
        minecraftDir = os.path.join(appdata, ".minecraft")
        
saveFileDir = os.path.join(minecraftDir, u"saves")
 
#if sys.platform == "win32":
#    from win32com.shell import shell, shellcon
#    saveFileDir = shell.SHGetPathFromIDListEx (
#    shell.SHGetSpecialFolderLocation (0, shellcon.CSIDL_APPDATA)
#    )
#    
    
"""
Indev levels:

TAG_Compound "MinecraftLevel"
{
   TAG_Compound "Environment" 
   {
      TAG_Short "SurroundingGroundHeight"// Height of surrounding ground (in blocks)
      TAG_Byte "SurroundingGroundType"   // Block ID of surrounding ground
      TAG_Short "SurroundingWaterHeight" // Height of surrounding water (in blocks)
      TAG_Byte "SurroundingWaterType"    // Block ID of surrounding water
      TAG_Short "CloudHeight"            // Height of the cloud layer (in blocks)
      TAG_Int "CloudColor"               // Hexadecimal value for the color of the clouds
      TAG_Int "SkyColor"                 // Hexadecimal value for the color of the sky
      TAG_Int "FogColor"                 // Hexadecimal value for the color of the fog
      TAG_Byte "SkyBrightness"           // The brightness of the sky, from 0 to 100
   }
   
   TAG_List "Entities"
   {
      TAG_Compound
      {
         // One of these per entity on the map.
         // These can change a lot, and are undocumented.
         // Feel free to play around with them, though.
         // The most interesting one might be the one with ID "LocalPlayer", which contains the player inventory
      }
   }
   
   TAG_Compound "Map"
   {
      // To access a specific block from either byte array, use the following algorithm:
      // Index = x + (y * Depth + z) * Width

      TAG_Short "Width"                  // Width of the level (along X) 
      TAG_Short "Height"                 // Height of the level (along Y) 
      TAG_Short "Length"                 // Length of the level (along Z) 
      TAG_Byte_Array "Blocks"             // An array of Length*Height*Width bytes specifying the block types
      TAG_Byte_Array "Data"              // An array of Length*Height*Width bytes with data for each blocks
      
      TAG_List "Spawn"                   // Default spawn position
      {
         TAG_Short x  // These values are multiplied by 32 before being saved
         TAG_Short y  // That means that the actual values are x/32.0, y/32.0, z/32.0
         TAG_Short z
      }
   }
   
   TAG_Compound "About"
   {
      TAG_String "Name"                  // Level name
      TAG_String "Author"                // Name of the player who made the level
      TAG_Long "CreatedOn"               // Timestamp when the level was first created
   }
}
"""

#String constants for known tag names
MinecraftLevel = "MinecraftLevel"

Environment = "Environment"
SurroundingGroundHeight = "SurroundingGroundHeight"
SurroundingGroundType = "SurroundingGroundType"
SurroundingWaterHeight = "SurroundingWaterHeight"
SurroundingWaterType = "SurroundingWaterType"
CloudHeight = "CloudHeight"
CloudColor = "CloudColor"
SkyColor = "SkyColor"
FogColor = "FogColor"
SkyBrightness = "SkyBrightness"

Entities = "Entities"
TileEntities = "TileEntities"

Map = "Map"
Width = "Width"
Height = "Height"
Length = "Length"
Blocks = "Blocks"
Data = "Data"
Spawn = "Spawn"

#entities
Inventory = 'Inventory'
Motion = "Motion"
Pos = "Pos"
Rotation = "Rotation"

About = "About"
Name = "Name"
Author = "Author"
CreatedOn = "CreatedOn"

#infdev
Level = 'Level'
BlockData = 'BlockData'
BlockLight = 'BlockLight'
SkyLight = 'SkyLight'
HeightMap = 'HeightMap'
TerrainPopulated = 'TerrainPopulated'
LastUpdate = 'LastUpdate'
xPos = 'xPos'
zPos = 'zPos'

Data = 'Data'
SpawnX = 'SpawnX'
SpawnY = 'SpawnY'
SpawnZ = 'SpawnZ'
LastPlayed = 'LastPlayed'
RandomSeed = 'RandomSeed'
SizeOnDisk = 'SizeOnDisk' #maybe update this?
Time = 'Time'
Player = 'Player'

#schematic
Materials = 'Materials'

#decorator for the primitive methods of MCLevel.
def decompress_first(func):
    def dec_first(self, *args, **kw):
        self.decompress();
        return func(self, *args, **kw);
    dec_first.__doc__ = func.__doc__
    return dec_first
def unpack_first(func):
    def upk_first(self, *args, **kw):
        self.unpackChunkData();
        return func(self, *args, **kw);
    upk_first.__doc__ = func.__doc__
    return upk_first
    
class MCLevel(object):
    """ MCLevel is an abstract class providing many routines to the different level types, 
    including a common copyEntitiesFrom built on class-specific routines, and
    a dummy getChunk/allChunks for the finite levels.
    
    MCLevel also provides compress and decompress methods that are used to load
    NBT format levels, and expects subclasses to override shapeChunkData to 
    assign a shape to the Blocks and other arrays. The resulting arrays after 
    reshape must be indexed [x,z,y]
    
    MCLevel subclasses must have Width, Length, and Height attributes.  The first two are always zero for infinite levels.
    Subclasses must also have Blocks, and optionally Data and BlockLight.
    """
    
    ###common to Creative, Survival and Indev. these routines assume
    ###self has Width, Height, Length, and Blocks
   
    materials = classicMaterials;
    
    hasEntities = False;
    compressedTag = None
    root_tag = None
    
    Height = None
    Length = None
    Width = None
    
    players = ["Player"]
    dimNo = 0;
    parentWorld = None
    world = None
    @classmethod
    def isLevel(cls, filename):
        """Tries to find out whether the given filename can be loaded
        by this class.  Returns True or False.
        
        Subclasses should implement _isLevel, _isDataLevel, or _isTagLevel.
        """ 
        if hasattr(cls, "_isLevel"):
            return cls._isLevel(filename);
        
        with file(filename) as f:
            data = f.read();
        
        if hasattr(cls, "_isDataLevel"):
            return cls._isDataLevel(data);
        
        if hasattr(cls, "_isTagLevel"):
            try:
                root_tag = nbt.load(filename, data)
            except:
                return False;
            
            return cls._isTagLevel(root_tag);
        
        return False
            
    def getWorldBounds(self):
        return BoundingBox( (0,0,0), self.size )
    
    @property
    def displayName(self):
        return os.path.basename(self.filename)
        
    @property     
    def size(self):
        "Returns the level's dimensions as a tuple (X,Y,Z)"
        return (self.Width, self.Height, self.Length)
    
    @property
    def bounds(self):
        return BoundingBox( (0,0,0), self.size )
    
    def packChunkData(self):
        """called before compression"""
        pass
    def unpackChunkData(self):
        """called when accessing attributes decorated with @unpack_first"""
        pass
        
    def shapeChunkData(self):
        """called during the default decompress(), should assign a shape to the
        Blocks, Data, Light, SkyLight, HeightMap attributes if present """
        pass
        
    def close(self):
        pass
    
    def compress(self):
        pass
    def decompress(self):
        pass
        
    
    def compressChunk(self, cx, cz): pass
    def entitiesAt(self, x, y, z):
        return None
    def tileEntityAt(self, x, y, z):
        return None
    def addEntity(self, *args): pass
    def addTileEntity(self, *args): pass

    @property
    def loadedChunks(self):
        return itertools.product(xrange(0, self.Width+15>>4), xrange(0, self.Length+15>>4))
    
    @property
    def presentChunks(self):
        """Returns self.allChunks for compatibility""" 
        return self.allChunks #backward compatibility
    
    @property
    def chunkCount(self):
        return (self.Width+15>>4) * (self.Length+15>>4)
        
    @property
    def allChunks(self):
        """Returns a synthetic list of chunk positions (xPos, zPos), to fake 
        being a chunked level format."""
        return self.loadedChunks
        
    def getChunk(self, cx, cz):
        """Synthesize a FakeChunk object representing the chunk at the given
        position. Subclasses override fakeBlocksForChunk and fakeDataForChunk
        to fill in the chunk arrays"""
            
        class FakeChunk:
            def load(self):pass
            def compress(self):pass
            def __init__(self):pass
            def chunkChanged(self):pass
            
            
        f = FakeChunk()
        f.world = self;
        f.chunkPosition = (cx,cz)
        
        f.Blocks = self.fakeBlocksForChunk(cx, cz)
        
        
        f.Data = self.fakeDataForChunk(cx, cz)
        
        whiteLight = zeros_like(f.Blocks);
        whiteLight[:] = 15;
        
        f.BlockLight = whiteLight
        f.SkyLight = whiteLight
        f.Entities = []
        f.TileEntities = []
        
        
        f.root_tag = TAG_Compound();
        
        return f
        
    def getAllChunkSlices(self):
        slices = ( slice(None),slice(None),slice(None), )
        box = self.bounds
        x, y, z = box.origin
        
        for cpos in self.allChunks:    
            xPos, zPos = cpos
            try:
                chunk = self.getChunk(xPos, zPos)
            except (ChunkMalformed, ChunkNotPresent):
                continue
                
            
            yield ( chunk, slices, (xPos * 16 - x, 0, zPos * 16 - z) )
            
              
    def getChunkSlices(self, box):
        """ call this method to iterate through a large slice of the world by 
            visiting each chunk and indexing its data with a subslice.
        
        this returns an iterator, which yields 3-tuples containing:
        +  an InfdevChunk object, 
        +  a x,z,y triplet of slices that can be used to index the InfdevChunk's data arrays, 
        +  a x,y,z triplet representing the relative location of this subslice within the requested world slice.
        
        Note the different order of the coordinates between the 'slices' triplet
        and the 'offset' triplet. x,z,y ordering is used only
        to index arrays, since it reflects the order of the blocks in memory.
        In all other places, including an entity's 'Pos', the order is x,y,z. 
        """
        level = self
        
        #when yielding slices of chunks on the edge of the box, adjust the 
        #slices by an offset
        minxoff, minzoff = box.minx-(box.mincx<<4), box.minz-(box.mincz<<4);
        maxxoff, maxzoff = box.maxx-(box.maxcx<<4)+16, box.maxz-(box.maxcz<<4)+16;
        
    
        for cx in range(box.mincx, box.maxcx):
            localMinX=0
            localMaxX=16
            if cx==box.mincx: 
                localMinX=minxoff
    
            if cx==box.maxcx-1:
                localMaxX=maxxoff
            newMinX = localMinX + (cx << 4) - box.minx
            newMaxX = localMaxX + (cx << 4) - box.minx
            
                            
            for cz in range(box.mincz, box.maxcz):
                localMinZ=0
                localMaxZ=16
                if cz==box.mincz: 
                    localMinZ=minzoff
                if cz==box.maxcz-1:
                    localMaxZ=maxzoff
                newMinZ = localMinZ + (cz << 4) - box.minz
                newMaxZ = localMaxZ + (cz << 4) - box.minz
                try:
                    ch = level.getChunk(cx, cz)
                except ChunkNotPresent, e:
                    continue;
                
                yield           (ch,
                                (slice(localMinX,localMaxX),slice(localMinZ,localMaxZ),slice(box.miny,box.maxy)),  
                                (newMinX, 0, newMinZ))
                
                ch.compress()
                
                
    def containsPoint(self, x, y, z):
        return (x >=0 and x < self.Width and
                y >=0 and y < self.Height and
                z >=0 and z < self.Length )

    def containsChunk(self, cx, cz):
        #w+15 to allow non 16 aligned schematics
        return (cx >=0 and cx < (self.Width+15 >> 4) and
                cz >=0 and cz < (self.Length+15 >> 4))

    def chunkIsLoaded(self, cx, cz):
        return self.containsChunk(cx,cz)
        
    def chunkIsCompressed(self, cx, cz):
        return False
    
    def chunkIsDirty(self, cx, cz):
        return True
        
    
    def fakeBlocksForChunk(self, cx, cz):
        #return a 16x16xH block array for rendering.  Alpha levels can
        #just return the chunk data.  other levels need to reorder the
        #indices and return a slice of the blocks.
        
        cxOff = cx << 4
        czOff = cz << 4
        b = self.Blocks[cxOff:cxOff+16, czOff:czOff+16, 0:self.Height, ];
        #(w, l, h) = b.shape
        #if w<16 or l<16:
        #    b = resize(b, (16,16,h) )
        return b;
    
    def fakeDataForChunk(self, cx, cz):
        #Data is emulated for flexibility
        cxOff = cx << 4
        czOff = cz << 4
        
        if hasattr(self, "Data"):
            return self.Data[cxOff:cxOff+16, czOff:czOff+16, 0:self.Height, ];
            
        else:
            return zeros(shape=(16, 16, self.Height), dtype='uint8')
            
    def skylightAt(self, *args):
        return 15

    def setSkylightAt(self, *args): pass

    def setBlockDataAt(self, x,y,z, newdata): pass     

    def blockDataAt(self, x, y, z): return 0;
    
    def blockLightAt(self, x, y, z): return 15;

    def blockAt(self, x, y, z):
        if x<0 or y<0 or z<0: return 0
        if x>=self.Width or y>=self.Height or z>=self.Length: return 0;
        return self.Blocks[x,z,y]
    
    def setBlockAt(self, x, y, z, blockID):
        if x<0 or y<0 or z<0: return 0
        if x>=self.Width or y>=self.Height or z>=self.Length: return 0;
        self.Blocks[x,z,y] = blockID
    
    

    def blocksInRanges(self, origin, size):
        # origin is (x,y,z), size is (w,h,l)
        (x,y,z) = origin
        (w,h,l) = size
#        end = tuple([o+s for o,s in zip(origin,size)])
        return self.Blocks[x:x+w,z:z+l,y:y+h]
    
    def blockReplaceTable(self, blocksToReplace):
        blocktable = zeros( (256, 16), dtype='bool')
        for b in blocksToReplace:
            if b.hasAlternate:
                blocktable[b.ID,b.blockData] = True
            else:
                blocktable[b.ID] = True
                
        return blocktable
        
    def fillBlocks(self, box, blockInfo, blocksToReplace = []):
        
        if box is None: 
            box = self.bounds
        else:
            box = box.intersect(self.bounds)
        
        info( u"Filling blocks in {0} with {1}, replacing{2}".format(box, blockInfo, blocksToReplace) )
        
        slices = map(slice, box.origin, box.maximum)
        
        blocks = self.Blocks[slices[0],slices[2],slices[1]]
        if len(blocksToReplace):
            blocktable = self.blockReplaceTable(blocksToReplace)
            
            if hasattr(self, "Data"):
                data = self.Data[slices[0],slices[2],slices[1]]
                mask = blocktable[blocks,data]
            
                data[mask] = blockInfo.blockData;
            else:
                mask = blocktable[blocks,0]
            
            blocks[mask] = blockInfo.ID;
            
        else:
            blocks[:] = blockInfo.ID;
            if hasattr(self, "Data"):
                self.Data[slices[0],slices[2],slices[1]] = blockInfo.blockData;
               
        #self.saveInPlace();
    classicWoolMask = zeros((256,), dtype='bool')
    classicWoolMask[range(21, 37)] = True;
    
    classicToAlphaWoolTypes = range(21)+[
        0xE, #"Red", (21)
        0x1, #"Orange",
        0x4, #"Yellow",
        0x5, #"Light Green",
        0xD, #"Green",
        0x9, #"Aqua",
        0x3, #"Cyan",
        0xB, #"Blue",
        0xA, #"Purple",
        0xA, #"Indigo",
        0x2, #"Violet",
        0x2, #"Magenta",
        0x6, #"Pink",
        0x7, #"Black",
        0x8, #"Gray",
        0x0, #"White",
    ]
    classicToAlphaWoolTypes = array(classicToAlphaWoolTypes, dtype='uint8')
    
    def convertBlocksFromLevel(self, sourceLevel, blocks, blockData):
        convertedBlocks = sourceLevel.materials.conversionTables[self.materials][blocks]
        if blockData is None:
            blockData = zeros_like(convertedBlocks)
        
        convertedBlockData = array(blockData)

        if sourceLevel.materials is classicMaterials and self.materials is alphaMaterials:
            woolMask = self.classicWoolMask[blocks]
            woolBlocks = blocks[woolMask]
            convertedBlockData[woolMask] = self.classicToAlphaWoolTypes[woolBlocks]
        
        return convertedBlocks, convertedBlockData
            
    def rotateLeft(self):
        self.Blocks = swapaxes(self.Blocks, 1, 0)[:,::-1,:]; #x=z; z=-x
        pass;
        
    def roll(self):
        self.Blocks = swapaxes(self.Blocks, 2, 0)[:,:,::-1]; #x=y; y=-x
        pass    
    
    def flipVertical(self):
        self.Blocks = self.Blocks[:,:,::-1]; #y=-y
        pass    
    
    def flipNorthSouth(self):
        self.Blocks = self.Blocks[::-1,:,:]; #x=-x
        pass    
    
    def flipEastWest(self):
        self.Blocks = self.Blocks[:,::-1,:]; #z=-z
        pass    
    
    
        
    def copyBlocksFromFiniteToFinite(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy):
        # assume destinationPoint is entirely within this level, and the size of sourceBox fits entirely within it.
        sourcex, sourcey, sourcez = map(slice, sourceBox.origin, sourceBox.maximum)
        destCorner2 = map(lambda a,b:a+b, sourceBox.size, destinationPoint)
        destx, desty, destz = map(slice, destinationPoint, destCorner2)
        
        sourceData = None
        if hasattr(sourceLevel, 'Data'):
            sourceData = sourceLevel.Data[sourcex, sourcez, sourcey]
        convertedSourceBlocks, convertedSourceData = self.convertBlocksFromLevel(sourceLevel, sourceLevel.Blocks[sourcex, sourcez, sourcey], sourceData)
         
        
        blocks = self.Blocks[destx, destz, desty]
            
        mask = slice(None, None)
        
        if not (blocksToCopy is None):
            typemask = zeros( (256) , dtype='bool')
            typemask[blocksToCopy] = True;
            mask = typemask[convertedSourceBlocks]
            
        blocks[mask] = convertedSourceBlocks[mask]
        if hasattr(self, 'Data'):
            data = self.Data[destx, destz, desty]
            data[mask] = convertedSourceData[mask]
        
        
    def copyBlocksFromInfinite(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy):
        
        chunkIterator = sourceLevel.getChunkSlices(sourceBox)
        
        
        if blocksToCopy is not None:
            typemask = zeros( (256) , dtype='bool')
            typemask[blocksToCopy] = True;
        
        for (chunk, slices, point) in chunkIterator:
            point = map(lambda a,b:a+b, point, destinationPoint)
            point = point[0], point[2], point[1]
            mask = slice(None, None)
            
            convertedSourceBlocks, convertedSourceData = self.convertBlocksFromLevel(sourceLevel, chunk.Blocks[slices], chunk.Data[slices])
            
            
            destSlices = [slice(p, p+s.stop-s.start) for p,s in zip(point,slices) ]
            
            blocks = self.Blocks[ destSlices ];
            
            if blocksToCopy is not None:
                mask = typemask[convertedSourceBlocks]
                
            blocks[mask] = convertedSourceBlocks[mask]
            
            if hasattr(self, 'Data'):
                data = self.Data[ destSlices ];
                data[mask] = convertedSourceData[mask]
            
                #self.Data[ destSlices ][mask] = chunk.Data[slices][mask]
                
            
            chunk.compress();
            
        
    def adjustCopyParameters(self, sourceLevel, sourceBox, destinationPoint):
    
        # if the destination box is outside the level, it and the source corners are moved inward to fit.
        # ValueError is raised if the source corners are outside sourceLevel
        (x,y,z) = map(int, destinationPoint)
        
        sourceBox = BoundingBox(sourceBox.origin, sourceBox.size)
        
        (lx,ly,lz) = sourceBox.size;
        debug(u"Asked to copy {0} blocks \n\tfrom {1} in {3}\n\tto {2} in {4}" .format (ly*lz*lx,sourceBox, destinationPoint, sourceLevel, self))
        

        #clip the source ranges to this level's edges.  move the destination point as needed.
        #xxx abstract this
        if y<0: 
            sourceBox.origin[1] -=y
            sourceBox.size[1] += y
            y = 0;
        if y+sourceBox.size[1]>self.Height:
            sourceBox.size[1] -=y+sourceBox.size[1]-self.Height
            y=self.Height-sourceBox.size[1]
        
        #for infinite levels, don't clip along those dimensions because the 
        #infinite copy func will just skip missing chunks
        if self.Width != 0:
            if x<0: 
                sourceBox.origin[0] -=x
                sourceBox.size[0] += x
                x = 0;
            if x+sourceBox.size[0]>self.Width:
                sourceBox.size[0] -=x+sourceBox.size[0]-self.Width
                #x=self.Width-sourceBox.size[0]
            
        if self.Length != 0:
            if z<0: 
                sourceBox.origin[2] -=z
                sourceBox.size[2] += z
                z = 0;
            if z+sourceBox.size[2]>self.Length:
                sourceBox.size[2] -=z+sourceBox.size[2]-self.Length
                #z=self.Length-sourceBox.size[2]
        
        destinationPoint = (x,y,z)
        
        return sourceBox, destinationPoint
         
    def copyBlocksFrom(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy = None):
        if (not isinstance(sourceLevel, MCInfdevOldLevel)) and not(
               sourceLevel.containsPoint(*sourceBox.origin) and
               sourceLevel.containsPoint(*map(lambda x:x-1, sourceBox.maximum))):
            raise ValueError, "{0} cannot provide blocks between {1}".format(sourceLevel, sourceBox)     
        
        
        sourceBox, destinationPoint = self.adjustCopyParameters(sourceLevel, sourceBox, destinationPoint)
        
        if min(sourceBox.size) <= 0: 
            print "Empty source box, aborting"
            return;
            
        info( u"Copying {0} blocks from {1} to {2}" .format (sourceBox.volume,sourceBox, destinationPoint) )
       
        if not isinstance(sourceLevel, MCInfdevOldLevel):
            self.copyBlocksFromFiniteToFinite(sourceLevel, sourceBox, destinationPoint, blocksToCopy)
        else:
            self.copyBlocksFromInfinite(sourceLevel, sourceBox, destinationPoint, blocksToCopy)
        
        
        self.copyEntitiesFrom(sourceLevel, sourceBox, destinationPoint)

    def saveInPlace(self):
        self.saveToFile(self.filename);
    @classmethod
    def fromFile(cls, filename, loadInfinite=True):
        ''' The preferred method for loading Minecraft levels of any type.
        pass False to loadInfinite if you'd rather not load infdev levels.
        '''
        info( u"Identifying " + filename )
        
        class LoadingError(RuntimeError): pass
        
        
        if not filename:
            raise IOError, "File not found: "+filename
        if not os.path.exists(filename):
            raise IOError, "File not found: "+filename
        
        if (ZipSchematic._isLevel(filename)):
            info( "Zipfile found, attempting zipped infinite level" )
            lev = ZipSchematic(filename);
            info( "Detected zipped Infdev level" )
            return lev
            
        if (MCInfdevOldLevel._isLevel(filename)):
            info( u"Detected Infdev level.dat" )
            if (loadInfinite):
                return MCInfdevOldLevel(filename=filename);
            else:
                raise ValueError, "Asked to load {0} which is an infinite level, loadInfinite was False".format(os.path.basename(filename));
        
        if os.path.isdir(filename):
            raise ValueError, "Folder {0} was not identified as a Minecraft level.".format(os.path.basename(filename));
            
        f = file(filename, 'rb');
        rawdata = f.read()
        f.close()
        if len(rawdata) < 4:
            raise ValueError, "{0} is too small! ({1}) ".format(filename, len(rawdata))
            
            
        
        
        data = fromstring(rawdata, dtype='uint8')
        if not data.any():
            raise ValueError, "{0} contains only zeroes. This file is damaged beyond repair."
        
        
        if MCJavaLevel._isDataLevel(data):
            info( u"Detected Java-style level" )
            lev = MCJavaLevel(filename, data);
            lev.compressed = False;
            return lev;

        #ungzdata = None
        compressed = True
        unzippedData = None;
        try:
            unzippedData = gunzip(rawdata)
        except Exception,e:
            info( u"Exception during Gzip operation, assuming {0} uncompressed: {1!r}".format(filename, e) )
            if unzippedData is None:
                compressed = False;
                unzippedData = rawdata
        
        data = fromstring(unzippedData, dtype='uint8')
        
        if MCJavaLevel._isDataLevel(data):
            info( u"Detected compressed Java-style level" )
            lev = MCJavaLevel(filename, data);
            lev.compressed = compressed;
            return lev;

        try:
            root_tag = nbt.load(buf=data);
        except Exception, e:
            info( u"Error during NBT load: {0!r}".format(e) )
            info( u"Fallback: Detected compressed flat block array, yzx ordered " )
            try:
                lev = MCJavaLevel(filename, data);
                lev.compressed = compressed;
                return lev;
            except Exception, e2:
                raise LoadingError, ("Multiple errors encountered", e, e2)
                 
        else:
            if(MCIndevLevel._isTagLevel(root_tag)):
                info( u"Detected Indev .mclevel" )
                return MCIndevLevel(root_tag, filename)
            if(MCSchematic._isTagLevel(root_tag)):
                info( u"Detected Schematic." )
                return MCSchematic(root_tag=root_tag, filename=filename)
            
            if (INVEditChest._isTagLevel(root_tag)):
                info( u"Detected INVEdit inventory file" )
                return INVEditChest(root_tag=root_tag, filename=filename);
                
            
        #it must be a plain array of blocks. see if MCJavaLevel handles it.
        
        raise IOError, "Cannot detect file type."
    
    def setPlayerPosition(self, pos, player = "Player"):
        pass;

    def getPlayerPosition(self, player = "Player"):
        return (8,self.Height*0.75,8);
    
    def getPlayerDimension(self, player = "Player"): return 0;
    def setPlayerDimension(self, d, player = "Player"): return;
    
    def setPlayerSpawnPosition(self, pos, player = None):
        pass;

    def playerSpawnPosition(self, player = None):
        return self.getPlayerPosition();

    def setPlayerOrientation(self, yp, player = "Player"):
        pass

    def playerOrientation(self, player = "Player"):
        return (-45.,0.)

    def getEntitiesInRange(self, sourceBox, entities):
        entsInRange = [];
        for entity in entities:
            x,y,z = map(lambda x:x.value, entity[Pos])
            if not (x,y,z) in sourceBox: continue
            entsInRange.append(entity)
            
        return entsInRange
    
    def getTileEntitiesInRange(self, sourceBox, tileEntities):
        entsInRange = [];
        for tileEntity in tileEntities:
            if not 'x' in tileEntity: continue
            
            x,y,z = tileEntity['x'].value, tileEntity['y'].value, tileEntity['z'].value  
            if not (x,y,z) in sourceBox: continue
            entsInRange.append(tileEntity)
            
        return entsInRange
    
    def copyEntityWithOffset(self, entity, copyOffset):
        eTag = deepcopy(entity)
        
        positionTags = map(lambda p, co: nbt.TAG_Double(p.value+co), eTag[Pos], copyOffset)
        eTag[Pos] = nbt.TAG_List(positionTags)
        
        if eTag["id"].value == "Painting":
            eTag["TileX"].value += copyOffset[0]
            eTag["TileY"].value += copyOffset[1]
            eTag["TileZ"].value += copyOffset[2]
            
        return eTag
        
    def copyTileEntityWithOffset(self, tileEntity, copyOffset):
        eTag = deepcopy(tileEntity)
        eTag['x'] = TAG_Int(tileEntity['x'].value+copyOffset[0])
        eTag['y'] = TAG_Int(tileEntity['y'].value+copyOffset[1])
        eTag['z'] = TAG_Int(tileEntity['z'].value+copyOffset[2])
        return eTag
            
    def copyEntitiesFromInfinite(self, sourceLevel, sourceBox, destinationPoint):
        chunkIterator = sourceLevel.getChunkSlices(sourceBox);
        
        for (chunk, slices, point) in chunkIterator:
            #remember, slices are ordered x,z,y so you can subscript them like so:  chunk.Blocks[slices]
            cx,cz = chunk.chunkPosition
            wx,wz = cx<<4, cz<<4
            
            copyOffset = map(lambda x,y:x-y, destinationPoint, sourceBox.origin)
            for entity in chunk.Entities:
                x,y,z = map(lambda x:x.value, entity[Pos])
                
                if x-wx<slices[0].start or x-wx>=slices[0].stop: continue
                if y<slices[2].start or y>=slices[2].stop: continue
                if z-wz<slices[1].start or z-wz>=slices[1].stop: continue
                
                eTag = self.copyEntityWithOffset(entity, copyOffset)
                
                self.addEntity(eTag);
                
            for tileEntity in chunk.TileEntities:
                if not 'x' in tileEntity: continue
            
                x,y,z = tileEntity['x'].value, tileEntity['y'].value, tileEntity['z'].value  
                if x-wx<slices[0].start or x-wx>=slices[0].stop: continue
                if y<slices[2].start or y>=slices[2].stop: continue
                if z-wz<slices[1].start or z-wz>=slices[1].stop: continue
                
                eTag = self.copyTileEntityWithOffset(tileEntity, copyOffset)
                
                self.addTileEntity(eTag)
                
            chunk.compress();
                    
                
    def copyEntitiesFrom(self, sourceLevel, sourceBox, destinationPoint):
        #assume coords have already been adjusted by copyBlocks
        if not self.hasEntities or not sourceLevel.hasEntities: return;
        sourcePoint0 = sourceBox.origin;
        sourcePoint1 = sourceBox.maximum;
        
        if isinstance(sourceLevel, MCInfdevOldLevel):
            self.copyEntitiesFromInfinite(sourceLevel, sourceBox, destinationPoint)
        else:
            entsCopied = 0;
            tileEntsCopied = 0;
            copyOffset = map(lambda x,y:x-y, destinationPoint, sourcePoint0)
            for entity in sourceLevel.getEntitiesInRange(sourceBox, sourceLevel.Entities):
                eTag = self.copyEntityWithOffset(entity, copyOffset)
                
                self.addEntity(eTag)
                entsCopied += 1;
                    
                
            for entity in sourceLevel.getTileEntitiesInRange(sourceBox, sourceLevel.TileEntities):
                if not 'x' in entity: continue
            
                x,y,z = entity['x'].value, entity['y'].value, entity['z'].value  
                
                eTag = deepcopy(entity)
                eTag['x'] = TAG_Int(x+copyOffset[0])
                eTag['y'] = TAG_Int(y+copyOffset[1])
                eTag['z'] = TAG_Int(z+copyOffset[2])
                try:
                    self.addTileEntity(eTag)
                    tileEntsCopied += 1;
                except ChunkNotPresent:
                    pass
            debug( u"Copied {0} entities, {1} tile entities".format(entsCopied, tileEntsCopied) )

        
    def removeEntitiesInBox(self, box):
        
        if not self.hasEntities: return 0;
        newEnts = [];
        for ent in self.Entities:
            if map(lambda x:x.value, ent["Pos"]) in box: 
                continue;
            newEnts.append(ent);
            
        entsRemoved = len(self.Entities) - len(newEnts);
        debug( "Removed {0} entities".format(entsRemoved))
        
        self.Entities.value[:] = newEnts
        
        return entsRemoved
        
    def removeTileEntitiesInBox(self, box):
        
        if not hasattr(self, "TileEntities"): return;
        newEnts = [];
        for ent in self.TileEntities:
            if not "x" in ent: continue
            if map(lambda x:x.value, (ent[a] for a in "xyz")) in box: 
                continue;
            newEnts.append(ent);
            
        entsRemoved = len(self.TileEntities) - len(newEnts);
        debug( "Removed {0} tile entities".format(entsRemoved))
        
        self.TileEntities.value[:] = newEnts
        
        return entsRemoved      
              
    def generateLights(self, dirtyChunks = None):
        pass;
        
    def adjustExtractionParameters(self, box):
        x,y,z = box.origin
        w,h,l = box.size
        destX = destY = destZ = 0;
        
        if y<0: 
            destY -= y
            h += y
            y = 0;
        
        if y >= self.Height: return;
        
        if y+h>=self.Height:
            h -=y+h-self.Height
            y=self.Height-h
        
        if h<=0: return
        
        if self.Width:
            if x < 0:
                w += x
                destX -= x;
                x = 0;
            if x >= self.Width: return;
            
            if x + w >= self.Width:
                w = self.Width - x
            
            if w <= 0: return
            
            if z < 0:
                l += z
                destZ -= z;
                z = 0;
                
            if z >= self.Length: return;
            
            if z + l >= self.Length:
                l = self.Length - z
            
            if l <= 0: return
                  
        box = BoundingBox ( (x,y,z), (w,h,l) )
        
        return box, (destX, destY, destZ)
        
    def extractSchematic(self, box):
        p = self.adjustExtractionParameters(box);
        if p is None: return
        newbox, destPoint = p
        
        tempSchematic = MCSchematic(shape=box.size)
        tempSchematic.materials = self.materials
        tempSchematic.copyBlocksFrom(self, newbox, destPoint)
        
        return tempSchematic
    
    def extractZipSchematic(self, box, zipfilename):
        #converts classic blocks to alpha
        #probably should only apply to alpha levels
        
        p = self.adjustExtractionParameters(box);
        if p is None: return
        sourceBox, destPoint = p
        
        destPoint = (0,0,0)
        
        filename = tempfile.mktemp("schematic")
        
        tempSchematic = MCInfdevOldLevel(filename, create = True);
        
        destBox = BoundingBox(destPoint, sourceBox.size);
        
        if (sourceBox.isChunkAligned):
            #create chunks in the destination area corresponding only to chunks
            #present in the source
            chunks = sourceBox.chunkPositions
            destChunks = destBox.chunkPositions
            chunkIter = itertools.izip(chunks, destChunks)
            
            chunks = ( x[1] for x in chunkIter if self.containsChunk(*x[0]))
            tempSchematic.createChunks(chunks)
            
        else:
            tempSchematic.createChunksInBox(destBox)
        
        tempSchematic.copyBlocksFrom(self, sourceBox, destPoint)
        tempSchematic.saveInPlace(); #lights not needed for this format - crashes minecraft though
        
        schematicDat = TAG_Compound()
        schematicDat.name = "Mega Schematic"
        
        schematicDat["Width"] = TAG_Int(sourceBox.size[0]);
        schematicDat["Height"] = TAG_Int(sourceBox.size[1]);
        schematicDat["Length"] = TAG_Int(sourceBox.size[2]);
        schematicDat.save(os.path.join(filename, "schematic.dat"))
        
        zipdir(filename, zipfilename)
        
        import shutil
        shutil.rmtree(filename)
        
        
def zipdir(basedir, archivename):
    assert os.path.isdir(basedir)
    with closing(ZipFile(archivename, "w", ZIP_STORED)) as z:
        for root, dirs, files in os.walk(basedir):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
                z.write(absfn, zfn)
                            
fromFile = MCLevel.fromFile

 
def loadWorld(name):
    filename = os.path.join(saveFileDir, name)
    return fromFile(filename)
               
def loadWorldNumber(i):
    filename = u"{0}{1}{2}{3}{1}".format(saveFileDir, os.sep, u"World", i)
    return fromFile(filename)

##class MCEntity:
##    def __init__(self, tag=None):
##        self.id = "Unknown Entity"
##        
##        if(tag):
##            self.id = tag["id"].value;
##            
##        else:
##            self.id = "Unknown Entity"

class MCSchematic (MCLevel):
    materials = alphaMaterials
    hasEntities = True;
    
    
    def __str__(self):
        return u"MCSchematic(shape={0}, filename=\"{1}\")".format( self.size, self.filename or u"")
    
    def compress(self):
        #if self.root_tag is not None, then our compressed data must be stale and we need to recompress.
        
        if self.root_tag is None:
            return;
        else:
            self.packChunkData();
            
            buf = StringIO.StringIO()
            with closing(gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=2)) as gzipper:
                self.root_tag.save(buf=gzipper)
            
            self.compressedTag = buf.getvalue()
            
        self.root_tag = None
        
    def decompress(self):
        """called when accessing attributes decorated with @decompress_first"""
        if self.root_tag != None: return
        if self.compressedTag is None: 
            if self.root_tag is None:
                self.load();
            else:
                return;
        
        with closing(gzip.GzipFile(fileobj=StringIO.StringIO(self.compressedTag))) as gzipper:
            try:
                data = gzipper.read();
                if data == None: return;
            except Exception, e:
                #error( u"Error reading compressed data, assuming uncompressed: {0}".format(e) )
                data = self.compressedTag
            

        try:       
            self.root_tag = nbt.load(buf=fromstring(data, dtype='uint8'));
        except Exception, e:
            error( u"Malformed NBT data in schematic file: {0} ({1})".format(self.filename, e) )
            raise ChunkMalformed, self.filename
            
        try:
            self.shapeChunkData()
        except KeyError, e:
            error( u"Incorrect schematic format in file: {0} ({1})".format(self.filename, e) )
            raise ChunkMalformed, self.filename
        pass
         
        self.dataIsPacked = True; 
    
     
    #these refer to the blocks array instead of the file's height because rotation swaps the axes
    # this will have an impact later on when editing schematics instead of just importing/exporting
    @property
    @decompress_first        
    def Length(self):return self.Blocks.shape[1]

    @property
    @decompress_first        
    def Width(self):return self.Blocks.shape[0]

    @property
    @decompress_first        
    def Height(self):return self.Blocks.shape[2]
    
    
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
            self.root_tag[Materials] = TAG_String()
        self.root_tag[Materials].value = val
    
    @classmethod
    def _isTagLevel(cls, root_tag):
        return "Schematic" == root_tag.name
        
            
    def __init__(self, shape = None, root_tag = None, filename = None, mats = 'Alpha'):
        """ shape is (x,y,z) for a new level's shape.  if none, takes
        root_tag as a TAG_Compound for an existing schematic file.  if
        none, tries to read the tag from filename.  if none, results
        are undefined. materials can be a MCMaterials instance, or
        "Classic" or "Alpha" to indicate allowable blocks. The default is
        Alpha.

        block coordinate order in the file is y,z,x to use the same code as classic/indev levels.  
        in hindsight, this was a completely arbitrary decision.
        
        the Entities and TileEntities are nbt.TAG_List objects containing TAG_Compounds.
        this makes it easy to copy entities without knowing about their insides.
        
        rotateLeft swaps the axes of the different arrays.  because of this, the Width, Height, and Length
        reflect the current dimensions of the schematic rather than the ones specified in the NBT structure.
        I'm not sure what happens when I try to re-save a rotated schematic.
        """

        #if(shape != None):
        #    self.setShape(shape)
        
        
        if filename:
            self.filename = filename
            if None is root_tag:
                try:
                    root_tag = nbt.load(filename)
                except IOError,e:
                    error( u"Failed to load file {0}".format (e) )
                    
        else:
            self.filename = None

        if mats in namedMaterials:
            self.materials = namedMaterials[mats];
        else:
            assert(isinstance(mats, MCMaterials))
            self.materials = mats
 
        if root_tag:
            self.root_tag = root_tag;
            if Materials in root_tag:
                self.materials = namedMaterials[self.Materials]
            else:
                root_tag[Materials] = materialNames[self.materials]
            self.shapeChunkData();
            
        else:
            assert shape != None
            root_tag = TAG_Compound(name="Schematic")
            root_tag[Height] = TAG_Short(shape[1])
            root_tag[Length] = TAG_Short(shape[2])
            root_tag[Width] = TAG_Short(shape[0])
            
            root_tag[Entities] = TAG_List()
            root_tag[TileEntities] = TAG_List()
            root_tag["Materials"] = TAG_String(materialNames[self.materials]);
            
            root_tag[Blocks] = TAG_Byte_Array( zeros( (shape[1], shape[2], shape[0]), uint8 ) )
            root_tag[Data] = TAG_Byte_Array( zeros( (shape[1], shape[2], shape[0]), uint8 ) )
            
            self.root_tag = root_tag;
        
        self.dataIsPacked = True;
            
    def shapeChunkData(self):
        w = self.root_tag[Width].value
        l = self.root_tag[Length].value
        h = self.root_tag[Height].value
        
        self.root_tag[Blocks].value.shape=(h,l,w)
        self.root_tag[Data].value.shape=(h,l,w)
    
   
    def packUnpack(self):
        self.root_tag[Blocks].value = swapaxes(self.root_tag[Blocks].value, 0, 2)#yzx to xzy
        self.root_tag[Data].value = swapaxes(self.root_tag[Data].value, 0, 2)#yzx to xzy
        if self.dataIsPacked:
            self.root_tag[Data].value &= 0xF #discard high bits
        
    def packChunkData(self):
        if not self.dataIsPacked:
            self.packUnpack()
            self.dataIsPacked = True;
            
    def unpackChunkData(self):
        if self.dataIsPacked:
            self.packUnpack()
            self.dataIsPacked = False;
     
    def rotateLeft(self):
        
        self.Blocks = swapaxes(self.Blocks, 1, 0)[:,::-1,:]; #x=z; z=-x
        self.Data = swapaxes(self.Data, 1, 0)[:,::-1,:]; #x=z; z=-x
        
        blockrotation.RotateLeft(self.Blocks, self.Data);
            
        info( u"Relocating entities..." )
        for entity in self.Entities:
            for p in "Pos", "Motion":
                if p == "Pos":
                    zBase = self.Length
                else:
                    zBase = 0.0; 
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
            if not 'x' in tileEntity: continue
            
            newX = tileEntity["z"].value
            newZ = self.Length - tileEntity["x"].value - 1
            
            tileEntity["x"].value = newX
            tileEntity["z"].value = newZ
    
    def roll(self):
        " xxx rotate stuff "
        self.Blocks = swapaxes(self.Blocks, 2, 0)[:,:,::-1]; #x=z; z=-x
        self.Data = swapaxes(self.Data, 2, 0)[:,:,::-1];
        
    
    def flipVertical(self):
        " xxx delete stuff "
        self.Blocks = self.Blocks[:,:,::-1]; #y=-y
        self.Data = self.Data[:,:,::-1]; 
        
    def flipNorthSouth(self):
        blockrotation.FlipNorthSouth(self.Blocks, self.Data);
        self.Blocks = self.Blocks[::-1,:,:]; #x=-x
        self.Data = self.Data[::-1,:,:]; 
        
        northSouthPaintingMap = [0,3,2,1]
        
        info( u"N/S Flip: Relocating entities..." )
        for entity in self.Entities:
        
            entity["Pos"][0].value = self.Width - entity["Pos"][0].value
            entity["Motion"][0].value = -entity["Motion"][0].value
            
            entity["Rotation"][0].value -= 180.0
            
            if entity["id"].value == "Painting":
                entity["TileX"].value = self.Width - entity["TileX"].value
                entity["Dir"].value = northSouthPaintingMap[entity["Dir"].value]
                
        for tileEntity in self.TileEntities:
            if not 'x' in tileEntity: continue
            
            tileEntity["x"].value = self.Width - tileEntity["x"].value - 1
    
    def flipEastWest(self):
        " xxx flip entities "
        blockrotation.FlipEastWest(self.Blocks, self.Data);
        self.Blocks = self.Blocks[:,::-1,:]; #z=-z
        self.Data = self.Data[:,::-1,:]; 
        
        eastWestPaintingMap = [2,1,0,3]
        
        info( u"E/W Flip: Relocating entities..." )
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
        shape = (x,z,y)
        
        
        self.root_tag[Blocks].value = zeros(dtype='uint8',shape=shape)
        self.root_tag[Data].value = zeros(dtype='uint8',shape=shape)
        self.shapeChunkData();
        
    def saveToFile(self, filename = None):
        """ save to file named filename, or use self.filename.  XXX NOT THREAD SAFE AT ALL. """
        if filename == None: filename = self.filename
        if filename == None:
            warn( u"Attempted to save an unnamed schematic in place" )
            return; #you fool!

        self.Materials = materialNames[self.materials]
        
        self.compress();

        with open(filename, 'wb') as chunkfh:
            chunkfh.write(self.compressedTag)
        
       
    def setBlockDataAt(self, x,y,z, newdata):
        if x<0 or y<0 or z<0: return 0
        if x>=self.Width or y>=self.Height or z>=self.Length: return 0;
        self.Data[x,z,y] = (newdata & 0xf);        

    def blockDataAt(self, x, y, z):
        if x<0 or y<0 or z<0: return 0
        if x>=self.Width or y>=self.Height or z>=self.Length: return 0;
        return self.Data[x,z,y];

    def entitiesAt(self, x, y, z):
        entities = [];
        for entityTag in self.Entities:
            if map(lambda x:int(x.value), entityTag[Pos]) == [x,y,z]:
                entities.append(entityTag);
        
        return entities;

    def addEntity(self, entityTag):
        assert isinstance(entityTag, TAG_Compound)
        self.Entities.append(entityTag);
        
    def tileEntityAt(self, x, y, z):
        entities = [];
        for entityTag in self.TileEntities:
            pos = [entityTag[a].value for a in 'xyz']
            if pos == [x,y,z]:
                entities.append(entityTag);

        if len(entities) > 1:
            info("Multiple tile entities found: {0}".format(entities))
        if len(entities) == 0:
            return None
            
        return entities[0];

    def addTileEntity(self, entityTag):
        assert isinstance(entityTag, TAG_Compound)
        self.TileEntities.append(entityTag);

    @classmethod
    def chestWithItemID(self, itemID, count=64, damage=0):
        """ Creates a chest with a stack of 'itemID' in each slot. 
        Optionally specify the count of items in each stack. Pass a negative 
        value for damage to create unnaturally sturdy tools. """
        root_tag = TAG_Compound();
        invTag = TAG_List();
        root_tag["Inventory"] = invTag
        for slot in range(9, 36):
            itemTag = TAG_Compound();
            itemTag["Slot"] = TAG_Byte(slot)
            itemTag["Count"] = TAG_Byte(count)
            itemTag["id"] = TAG_Short(itemID)
            itemTag["Damage"] = TAG_Short(damage)
            invTag.append(itemTag);
            
        chest = INVEditChest(root_tag, "");
    
        return chest;
    
class INVEditChest(MCSchematic):
    Width = 1
    Height = 1
    Length = 1
    Blocks = array([[[alphaMaterials.Chest.ID]]], 'uint8');
    Data = array([[[0]]], 'uint8');
    Entities = TAG_List();
    
    @classmethod
    def _isTagLevel(cls, root_tag):
        return "Inventory" in root_tag;
                
    def __init__(self, root_tag, filename):
        
        if filename:
            self.filename = filename
            if None is root_tag:
                try:
                    root_tag = nbt.load(filename)
                except IOError,e:
                    info( u"Failed to load file {0}".format(e) )
                    raise
        else:
            assert root_tag, "Must have either root_tag or filename"
            self.filename = None
            
        for item in list(root_tag["Inventory"]):
            slot = item["Slot"].value
            if slot < 9 or slot >= 36:
                root_tag["Inventory"].remove(item)
            else:
                item["Slot"].value -= 9 # adjust for different chest slot indexes
                

        self.root_tag = root_tag;
        
        
    @property
    @decompress_first        
    def TileEntities(self):
        chestTag = TAG_Compound();
        chestTag["id"] = TAG_String("Chest")
        chestTag["Items"] = TAG_List(self.root_tag["Inventory"])
        chestTag["x"] = TAG_Int(0);
        chestTag["y"] = TAG_Int(0);
        chestTag["z"] = TAG_Int(0);
        
        return TAG_List([chestTag], name="TileEntities")
    
   
class PlayerNotFound(Exception): pass     
class ChunkNotPresent(Exception): pass
class RegionMalformed(Exception): pass
class ChunkMalformed(ChunkNotPresent): pass

class ZeroChunk(object):
    " a placebo for neighboring-chunk routines "
    def compress(self): pass
    def load(self): pass
    def __init__(self, height=512):
        zeroChunk = zeros((16,16,height), uint8)
        whiteLight = zeroChunk + 15;
        self.Blocks = zeroChunk
        self.BlockLight = whiteLight
        self.SkyLight = whiteLight
        self.Data = zeroChunk
            
    
class InfdevChunk(MCLevel):
    """ This is a 16x16xH chunk in an (infinite) world.
    The properties Blocks, Data, SkyLight, BlockLight, and Heightmap 
    are ndarrays containing the respective blocks in the chunk file.
    Each array is indexed [x,z,y].  The Data, Skylight, and BlockLight 
    arrays are automatically unpacked from nibble arrays into byte arrays 
    for better handling.
    """
    hasEntities = True
    
    @property
    def filename(self):
        if self.world.version:
            cx,cz = self.chunkPosition
            rx,rz = cx>>5,cz>>5
            rf = self.world.regionFiles[rx,rz]
            offset = rf.getOffset(cx&0x1f,cz&0x1f)
            return u"{region} index {index} sector {sector} format {format}".format(
                region=os.path.basename(self.world.regionFilename(rx,rz)), 
                sector=offset>>8, 
                index=4*((cx&0x1f)+((cz&0x1f)*32)), 
                format=["???","gzip","deflate"][self.compressMode])
        else:
            return self.chunkFilename
    def __init__(self, world, chunkPosition, create = False):
        self.world = world;
        #self.materials = self.world.materials
        self.chunkPosition = chunkPosition;
        self.chunkFilename = world.chunkFilename(*chunkPosition)
        #self.filename = "UNUSED" + world.chunkFilename(*chunkPosition);
        #self.filename = "REGION FILE (chunk {0})".format(chunkPosition)
        self.compressedTag = None
        self.root_tag = None
        self.dirty = False;
        self.needsLighting = False
        if self.world.version:
            self.compressMode = MCRegionFile.VERSION_DEFLATE
        else:
            self.compressMode = MCRegionFile.VERSION_GZIP
            
        
        if create:
            self.create();
        else:
            if not world.containsChunk(*chunkPosition):
                raise ChunkNotPresent("Chunk {0} not found", self.chunkPosition)
    
    @property
    def materials(self):
        return self.world.materials
    
    def compressTagGzip(self, root_tag):
        buf = StringIO.StringIO()
        with closing(gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=2)) as gzipper:
            root_tag.save(buf=gzipper)
        
        return buf.getvalue()    
    
    def compressTagDeflate(self, root_tag):
        buf = StringIO.StringIO()
        root_tag.save(buf=buf)
        return deflate(buf.getvalue())
        
    def _compressChunk(self):
        root_tag = self.root_tag
        if root_tag is None: return
        
        if self.compressMode == MCRegionFile.VERSION_GZIP:
            self.compressedTag = self.compressTagGzip(root_tag)
        if self.compressMode == MCRegionFile.VERSION_DEFLATE:
            self.compressedTag = self.compressTagDeflate(root_tag)
        
        self.root_tag = None
        
    def decompressTagGzip(self, data):
        return nbt.load(buf=gunzip(data))
            
    def decompressTagDeflate(self, data):
        return nbt.load(buf=inflate(data))
        
    def _decompressChunk(self):
        data = self.compressedTag
        
        if self.compressMode == MCRegionFile.VERSION_GZIP:
            self.root_tag = self.decompressTagGzip(data)
        if self.compressMode == MCRegionFile.VERSION_DEFLATE:
            self.root_tag = self.decompressTagDeflate(data)
          
    
    def compressedSize(self):
        "return the size of the compressed data for this level, in bytes."
        self.compress();
        if self.compressedTag is None: return 0
        return len(self.compressedTag)
    
    
    def sanitizeBlocks(self):
        #change grass to dirt where needed so Minecraft doesn't flip out and die
        grass = self.Blocks == self.materials.Grass.ID
        badgrass = grass[:,:,1:] & grass[:,:,:-1]
        
        self.Blocks[:,:,:-1][badgrass] = self.materials.Dirt.ID
        
        #remove any thin snow layers immediately above other thin snow layers.
        #minecraft doesn't flip out, but it's almost never intended
        if hasattr(self.materials, "SnowLayer"):
            snowlayer = self.Blocks == self.materials.SnowLayer.ID
            badsnow = snowlayer[:,:,1:] & snowlayer[:,:,:-1]
            
            self.Blocks[:,:,1:][badsnow] = self.materials.Air.ID
        
        
    def compress(self):
        
        
        if not self.dirty: 
            #if we are not dirty, just throw the 
            #uncompressed tag structure away. rely on the OS disk cache.
            self.root_tag = None
        else:
            self.sanitizeBlocks() #xxx
            
            self.packChunkData()
            self._compressChunk()
            
        self.world.chunkDidCompress(self);
    
    def decompress(self):
        """called when accessing attributes decorated with @decompress_first"""
        if not self in self.world.decompressedChunkQueue:
            
            if self.root_tag != None: return
            if self.compressedTag is None: 
                if self.root_tag is None:
                    self.load();
                else:
                    return;
            
                
            try:       
                self._decompressChunk()
            
            except Exception, e:
                error( u"Malformed NBT data in file: {0} ({1})".format(self.filename, e) )
                if self.world: self.world.malformedChunk(*self.chunkPosition);
                raise ChunkMalformed, self.filename
                
            try:
                self.shapeChunkData()
            except KeyError, e:
                error( u"Incorrect chunk format in file: {0} ({1})".format(self.filename, e) )
                if self.world: self.world.malformedChunk(*self.chunkPosition);
                raise ChunkMalformed, self.filename
            
            self.dataIsPacked = True; 
        self.world.chunkDidDecompress(self);
        
        
    def __str__(self):
        return u"InfdevChunk, coords:{0}, world: {1}, D:{2}, L:{3}".format(self.chunkPosition, self.world.displayName,self.dirty, self.needsLighting)

    def create(self):
        (cx,cz) = self.chunkPosition;
        chunkTag = nbt.TAG_Compound()
        chunkTag.name = ""
        levelTag = nbt.TAG_Compound()
        chunkTag[Level] = levelTag
        
        levelTag[TerrainPopulated] = TAG_Byte(1)
        levelTag[xPos] = TAG_Int(cx)
        levelTag[zPos] = TAG_Int(cz)
        
        levelTag[LastUpdate] = TAG_Long(0);
        
        levelTag[BlockLight] = TAG_Byte_Array()
        levelTag[BlockLight].value = zeros(16*16*self.world.ChunkHeight/2, uint8)
        
        levelTag[Blocks] = TAG_Byte_Array()
        levelTag[Blocks].value = zeros(16*16*self.world.ChunkHeight, uint8)
        
        levelTag[Data] = TAG_Byte_Array()
        levelTag[Data].value = zeros(16*16*self.world.ChunkHeight/2, uint8)

        levelTag[SkyLight] = TAG_Byte_Array()
        levelTag[SkyLight].value = zeros(16*16*self.world.ChunkHeight/2, uint8)
        levelTag[SkyLight].value[:] = 255

        if self.world.ChunkHeight <= 128:
            levelTag[HeightMap] = TAG_Byte_Array()
            levelTag[HeightMap].value = zeros(16*16, uint8)
        else:
            levelTag[HeightMap] = TAG_Int_Array()
            levelTag[HeightMap].value = zeros(16*16, uint32).newbyteorder()

            
        levelTag[Entities] = TAG_List() 
        levelTag[TileEntities] = TAG_List()
        
        #levelTag["Creator"] = TAG_String("MCEdit-" + release.release);
        
        #empty lists are seen in the wild with a list.TAG_type for a list of single bytes, 
        #even though these contain TAG_Compounds 
        
        self.root_tag = chunkTag
        self.shapeChunkData();
        self.dataIsPacked = True;
        
        self.dirty = True;
        self.save();
    
    def save(self):
        """ does not recalculate any data or light """
        self.compress()
        
        if self.dirty:
            debug( u"Saving chunk: {0}".format(self) )
            self.world._saveChunk(self)
                
            debug( u"Saved chunk {0}".format( self ) )
            
            self.dirty = False;
            
    def load(self):
        """ If the chunk is unloaded, calls world._loadChunk to set root_tag and 
        compressedTag, then unpacks the chunk fully"""
        
        if self.root_tag is None and self.compressedTag is None:
            try:
                self.world._loadChunk(self)
                self.dataIsPacked = True; 
                self.shapeChunkData()
                self.unpackChunkData()
                
            except Exception, e:
                error( u"Incorrect chunk format in file: {0} ({1})".format(self.filename, e) )
                if self.world: self.world.malformedChunk(*self.chunkPosition);
                raise ChunkMalformed, self.filename
            
            self.world.chunkDidLoad(self) 
            self.world.chunkDidDecompress(self);
                
    def unload(self):
        """ Frees the chunk's memory. Will not save to disk. Unloads completely
        if the chunk does not need to be saved."""
        self.compress();
            
        if not self.dirty:
            self.compressedTag = None;
            self.world.chunkDidUnload(self)
        
    def isLoaded(self):
        #we're loaded if we have our tag data in ram 
        #and we don't have to go back to the disk for it.
        return not (self.compressedTag is None and self.root_tag is None)
    
    def isCompressed(self):
        return self.isLoaded() and self.root_tag == None
                
        
    def chunkChanged(self, calcLighting = True):
        """ You are required to call this function after you are done modifying
        the chunk. Pass False for calcLighting if you know your changes will 
        not change any lights."""
        
        if self.compressedTag == None and self.root_tag == None:
            #unloaded chunk
            return;
            
        self.dirty = True;
        self.needsLighting = calcLighting or self.needsLighting;
        generateHeightMap(self);
        if calcLighting:
            self.genFastLights()
    
    def genFastLights(self):
        self.SkyLight[:] = 0;
        if self.world.dimNo == -1: 
            return #no light in nether
        
        blocks = self.Blocks;
        la = self.world.materials.lightAbsorption
        skylight = self.SkyLight;
        heightmap = self.HeightMap;
        
        for x,z in itertools.product(xrange(16), xrange(16)):
            
            skylight[x,z,heightmap[z,x]:] = 15 
            lv = 15;
            for y in reversed(range(heightmap[z,x])):
                lv -= (la[blocks[x,z,y]] or 1)
                
                if lv <= 0: 
                    break;
                skylight[x,z,y] = lv;
                
               
    
    def unpackChunkData(self):
        if not self.dataIsPacked: return
        """ for internal use.  call getChunk and compressChunk to load, compress, and unpack chunks automatically """
        for key in (SkyLight, BlockLight, Data):
            dataArray = self.root_tag[Level][key].value
            s = dataArray.shape
            assert s[2] == self.world.ChunkHeight/2;
            #unpackedData = insert(dataArray[...,newaxis], 0, 0, 3)  
            
            unpackedData = zeros( (s[0], s[1], s[2]*2), dtype='uint8')
            
            unpackedData[:,:,::2] = dataArray
            unpackedData[:,:,::2] &= 0xf
            unpackedData[:,:,1::2] = dataArray
            unpackedData[:,:,1::2] >>= 4
            
            
            
            
            self.root_tag[Level][key].value=unpackedData
            self.dataIsPacked = False;
            
    def packChunkData(self):
        if self.dataIsPacked: return
        
        if self.root_tag is None:
            warn( u"packChunkData called on unloaded chunk: {0}".format( self.chunkPosition ) )
            return;
        for key in (SkyLight, BlockLight, Data):
            dataArray = self.root_tag[Level][key].value
            assert dataArray.shape[2] == self.world.ChunkHeight;
            
            unpackedData = self.root_tag[Level][key].value.reshape(16,16,self.world.ChunkHeight/2,2)
            unpackedData[...,1] <<=4
            unpackedData[...,1] |= unpackedData[...,0]
            self.root_tag[Level][key].value=array(unpackedData[:,:,:,1])
            
            self.dataIsPacked = True;
        
    def shapeChunkData(self):
        """Applies the chunk shape to all of the data arrays 
        in the chunk tag.  used by chunk creation and loading"""
        chunkTag = self.root_tag
        
        chunkSize = 16
        chunkTag[Level][Blocks].value.shape=(chunkSize, chunkSize, self.world.ChunkHeight)
        chunkTag[Level][HeightMap].value.shape=(chunkSize, chunkSize);            
        chunkTag[Level][SkyLight].value.shape = (chunkSize, chunkSize, self.world.ChunkHeight/2)
        chunkTag[Level][BlockLight].value.shape = (chunkSize, chunkSize, self.world.ChunkHeight/2)
        chunkTag[Level]["Data"].value.shape = (chunkSize, chunkSize, self.world.ChunkHeight/2)
        if not TileEntities in chunkTag[Level]:
            chunkTag[Level][TileEntities] = TAG_List();
        if not Entities in chunkTag[Level]:
            chunkTag[Level][Entities] = TAG_List();
    
    def removeEntitiesInBox(self, box):
        self.dirty = True;
        return MCLevel.removeEntitiesInBox(self, box)
        
    def removeTileEntitiesInBox(self, box):
        self.dirty = True;
        return MCLevel.removeTileEntitiesInBox(self, box)
        
        
    @property
    @decompress_first        
    def Blocks(self):
        return self.root_tag[Level][Blocks].value
    
    @property
    @decompress_first        
    @unpack_first
    def Data(self):
        return self.root_tag[Level][Data].value
    
    @property
    @decompress_first        
    def HeightMap(self):
        return self.root_tag[Level][HeightMap].value
    
    @property
    @decompress_first        
    @unpack_first
    def SkyLight(self):
        return self.root_tag[Level][SkyLight].value
    
    @property
    @decompress_first        
    @unpack_first
    def BlockLight(self):
        return self.root_tag[Level][BlockLight].value
        
    @property
    @decompress_first        
    def Entities(self):
        return self.root_tag[Level][Entities]
        
    @property
    @decompress_first        
    def TileEntities(self):
        return self.root_tag[Level][TileEntities]
    
    @property
    @decompress_first        
    def TerrainPopulated(self):
        return self.root_tag[Level]["TerrainPopulated"].value;
    @TerrainPopulated.setter
    @decompress_first        
    def TerrainPopulated(self, val):
        """True or False. If False, the game will populate the chunk with 
        ores and vegetation on next load"""
        self.root_tag[Level]["TerrainPopulated"].value = val;
    
def generateHeightMap(self):
    if None is self.root_tag: self.load();
    
    blocks = self.Blocks
    heightMap = self.HeightMap
    heightMap[:] = 0;
    
    lightAbsorption = self.world.materials.lightAbsorption[blocks]
    axes = lightAbsorption.nonzero()
    heightMap[axes[1],axes[0]] = axes[2]; #assumes the y-indices come out in increasing order
    heightMap += 1;

        
class dequeset(object):
    def __init__(self):
        self.deque = deque();
        self.set = set();
        
    def __contains__(self, obj):
        return obj in self.set;
    
    def __len__(self):
        return len(self.set);
        
    def append(self, obj):
        self.deque.append(obj);
        self.set.add(obj);
    
    def discard(self, obj):
        if obj in self.set:
            self.deque.remove(obj);
        self.set.discard(obj);
        
        
    def __getitem__(self, idx):
        return self.deque[idx];

from contextlib import contextmanager

@contextmanager
def notclosing(f):
    yield f;

class MCRegionFile(object):
    holdFileOpen = False #if False, reopens and recloses the file on each access
    
            
    @property
    def file(self):
        openfile = lambda:file(self.path, "rb+")
        if MCRegionFile.holdFileOpen:
            if self._file is None:
                self._file = openfile()
            return notclosing(self._file)
        else:
            return openfile()
    
    def close(self):
        if MCRegionFile.holdFileOpen:
            self._file.close()
            self._file = None
            
    def __init__(self, path, regionCoords):
        self.path = path
        self.regionCoords = regionCoords
        self._file = None
        if not os.path.exists(path):
            file(path, "w").close()
        
        with self.file as f:
            
            filesize = os.path.getsize(path)
            if filesize & 0xfff:
                filesize = (filesize | 0xfff)+1
                f.truncate(filesize)
            
            if filesize == 0:
                filesize = self.SECTOR_BYTES*2
                f.truncate(filesize)
                
            
            f.seek(0)
            offsetsData = f.read(self.SECTOR_BYTES)
            modTimesData = f.read(self.SECTOR_BYTES)
            
            self.freeSectors = [True] * (filesize / self.SECTOR_BYTES)
            self.freeSectors[0:2] = False,False
            
            self.offsets = fromstring(offsetsData, dtype='>u4')
            self.modTimes = fromstring(modTimesData, dtype='>u4')
            
        needsRepair = False
        
        for offset in self.offsets:
            sector = offset >> 8
            count = offset & 0xff
            
            for i in xrange(sector, sector+count):
                if i >= len(self.freeSectors): 
                    #raise RegionMalformed, "Region file offset table points to sector {0} (past the end of the file)".format(i)
                    print  "Region file offset table points to sector {0} (past the end of the file)".format(i)
                    needsRepair = True
                    break
                if self.freeSectors[i] is False:
                    needsRepair = True
                self.freeSectors[i] = False
        
        if needsRepair:
            self.repair()
            
        info("Found region file {file} with {used}/{total} sectors used and {chunks} chunks present".format(
             file=os.path.basename(path), used=len(self.freeSectors)-sum(self.freeSectors), total=len(self.freeSectors), chunks=sum(self.offsets>0)))
    
    def repair(self):
        lostAndFound = {}
        _freeSectors = [True] * len(self.freeSectors)
        _freeSectors[0] = _freeSectors[1] = False 
        deleted = 0
        recovered = 0
        info("Beginning repairs on {file} ({chunks} chunks)".format(file=os.path.basename(self.path), chunks=sum(self.offsets>0)))
        rx,rz = self.regionCoords
        for index, offset in enumerate(self.offsets):
            if offset:
                cx = index & 0x1f
                cz = index >> 5
                cx += rx << 5
                cz += rz << 5
                sectorStart = offset >> 8
                sectorCount = offset & 0xff
                try:
                
                    if sectorStart + sectorCount > len(self.freeSectors):
                        raise RegionMalformed,  "Offset {start}:{end} ({offset}) at index {index} pointed outside of the file".format(
                            start=sectorStart, end=sectorStart+sectorCount, index=index, offset=offset)
                        
                    compressedData = self._readChunk(cx,cz)
                    if compressedData is None: 
                        raise RegionMalformed, "Failed to read chunk data for {0}".format((cx,cz))
                    
                    format, data = self.decompressSectors(compressedData)
                    chunkTag = nbt.load(buf=data)
                    lev = chunkTag["Level"]
                    xPos = lev["xPos"].value
                    zPos = lev["zPos"].value
                    overlaps = False
                    
                    for i in xrange(sectorStart, sectorStart+sectorCount):
                        if _freeSectors[i] is False:
                            overlaps = True
                        _freeSectors[i] = False
                        
                        
                    if xPos != cx or zPos != cz or overlaps:
                        lostAndFound[xPos,zPos] = (format, compressedData)
                        
                        if (xPos, zPos) != (cx,cz):
                            raise RegionMalformed, "Chunk {found} was found in the slot reserved for {expected}".format(found=(xPos, zPos), expected=(cx,cz))
                        else:
                            raise RegionMalformed, "Chunk {found} (in slot {expected}) has overlapping sectors with another chunk!".format(found=(xPos, zPos), expected=(cx,cz))
                        
                    
                         
                except Exception, e:
                    info("Unexpected chunk data at sector {sector} ({exc})".format(sector=sectorStart, exc=e))
                    self.setOffset(cx, cz, 0)
                    deleted += 1
                    
        for cPos, (format, foundData) in lostAndFound.iteritems():
            cx,cz = cPos
            if self.getOffset(cx,cz) == 0:
                info("Found chunk {found} and its slot is empty, recovering it".format(found=cPos))
                self._saveChunk(cx,cz, foundData[5:], format)
                recovered += 1
                
        info("Repair complete. Removed {0} chunks, recovered {1} chunks, net {2}".format(deleted, recovered, recovered-deleted))
                        
    def _readChunk(self, cx, cz):
        cx &= 0x1f
        cz &= 0x1f
        offset = self.getOffset(cx,cz)
        if offset == 0: return None
        
        sectorStart = offset >> 8
        numSectors = offset & 0xff
        if numSectors == 0: return None
        
        if sectorStart + numSectors > len(self.freeSectors):
            return None
        
        with self.file as f:
            f.seek(sectorStart * self.SECTOR_BYTES)
            data = f.read(numSectors * self.SECTOR_BYTES)
        assert(len(data) > 0)
        #debug("REGION LOAD {0},{1} sector {2}".format(cx, cz, sectorStart))
        return data
        
    def loadChunk(self, chunk):
        cx,cz = chunk.chunkPosition
        
        data = self._readChunk(cx,cz)
        if data is None: raise ChunkNotPresent, (cx, cz, self)
        chunk.compressedTag = data[5:]
        
        format, data = self.decompressSectors(data)
        chunk.root_tag = nbt.load(buf=data)
        chunk.compressMode = format
        
        
    def decompressSectors(self, data):
        length = struct.unpack_from(">I", data)[0]
        format = struct.unpack_from("B", data, 4)[0]
        data = data[5:length+5]
        if format == self.VERSION_GZIP:
            return (format, gunzip(data))
        if format == self.VERSION_DEFLATE:
            return (format, inflate(data))
        
        raise IOError, "Unknown compress format: {0}".format(format)

        
    def saveChunk(self, chunk):
        cx,cz = chunk.chunkPosition
        data = chunk.compressedTag
        format = chunk.compressMode
        
        self._saveChunk(cx, cz, data, format)
        
    def _saveChunk(self, cx, cz, data, format):
        cx &= 0x1f
        cz &= 0x1f
        offset = self.getOffset(cx,cz)
        sectorNumber = offset >> 8
        sectorsAllocated = offset & 0xff
        
        
        sectorsNeeded = (len(data) + self.CHUNK_HEADER_SIZE) / self.SECTOR_BYTES + 1;
        if sectorsNeeded >= 256: return
        
        if (sectorNumber != 0 and sectorsAllocated >= sectorsNeeded):
            debug("REGION SAVE {0},{1} rewriting {2}b".format(cx, cz, len(data)))
            self.writeSector(sectorNumber, data, format)
        else:
            # we need to allocate new sectors
            
            # mark the sectors previously used for this chunk as free 
            for i in xrange(sectorNumber,sectorNumber+sectorsAllocated):
                self.freeSectors[i] = True
            
            runLength = 0
            try:
                runStart = self.freeSectors.index(True)
                
                for i in range(runStart, len(self.freeSectors)):
                    if runLength:
                        if self.freeSectors[i]:
                            runLength += 1
                        else:
                            runLength = 0
                    elif self.freeSectors[i]:
                        runStart = i
                        runLength = 1
                    
                    if runLength >= sectorsNeeded:
                        break
            except ValueError:
                pass
                
            # we found a free space large enough
            if runLength >= sectorsNeeded:
                debug("REGION SAVE {0},{1}, reusing {2}b".format(cx, cz, len(data)))
                sectorNumber = runStart
                self.setOffset(cx,cz, sectorNumber << 8 | sectorsNeeded)
                self.writeSector(sectorNumber, data, format)
                self.freeSectors[sectorNumber:sectorNumber+sectorsNeeded] = [False]*sectorsNeeded
                
            else:
                # no free space large enough found -- we need to grow the
                # file
                
                debug("REGION SAVE {0},{1}, growing by {2}b".format(cx, cz, len(data)))
                
                with self.file as f:
                    f.seek(0, 2)
                    filesize = f.tell()
                    
                    sectorNumber = len(self.freeSectors)
                    
                    assert sectorNumber * self.SECTOR_BYTES == filesize
                    
                    filesize += sectorsNeeded * self.SECTOR_BYTES
                    f.truncate(filesize)

                self.freeSectors += [False]*sectorsNeeded
                
                self.setOffset(cx,cz, sectorNumber << 8 | sectorsNeeded)
                self.writeSector(sectorNumber, data, format)
                 
            
    def writeSector(self, sectorNumber, data, format):
        with self.file as f:
            debug("REGION: Writing sector {0}".format(sectorNumber) )
        
            f.seek( sectorNumber * self.SECTOR_BYTES )
            f.write(struct.pack(">I", len(data)+1));# // chunk length
            f.write(struct.pack("B", format));# // chunk version number
            f.write(data);# // chunk data
            #f.flush()
    
             
    def getOffset(self, cx, cz):
        cx&=0x1f;
        cz&=0x1f
        return self.offsets[cx+cz*32]
    
    def setOffset(self, cx, cz, offset):
        cx &= 0x1f;
        cz &= 0x1f
        self.offsets[cx+cz*32] = offset
        with self.file as f:
            f.seek(0)
            f.write(self.offsets.tostring())
            
            
            
    SECTOR_BYTES = 4096
    SECTOR_INTS = SECTOR_BYTES / 4
    CHUNK_HEADER_SIZE = 5;
    VERSION_GZIP = 1
    VERSION_DEFLATE = 2
    
    compressMode=VERSION_DEFLATE
    
import zlib
def deflate(data):
    #zobj = zlib.compressobj(6,zlib.DEFLATED,-zlib.MAX_WBITS,zlib.DEF_MEM_LEVEL,0)
    #zdata = zobj.compress(data)
    #zdata += zobj.flush()
    #return zdata
    return zlib.compress(data)
def inflate(data):
    return zlib.decompress(data)
from nbt import gunzip
       
class MCInfdevOldLevel(MCLevel):
    materials = alphaMaterials;
    hasEntities = True;
    parentWorld = None;
    dimNo = 0;
    ChunkHeight = 128
      
        
    @property
    def displayName(self):
        #shortname = os.path.basename(self.filename);
        #if shortname == "level.dat":
        shortname = os.path.basename(os.path.dirname(self.filename))
            
        return shortname
    
    @classmethod
    def _isLevel(cls, filename):
        if os.path.isdir(filename):
            files = os.listdir(filename);
            if "level.dat" in files or "level.dat_old" in files:
                return True;
        elif os.path.basename(filename) in ("level.dat", "level.dat_old"):
            return True;
            
        return False
    
    def getWorldBounds(self):
        if self.chunkCount == 0:
            return BoundingBox( (0,0,0), (0,0,0) )
            
        allChunksArray = array(list(self.allChunks), dtype='int32')
        mincx = min(allChunksArray[:,0])
        maxcx = max(allChunksArray[:,0])
        mincz = min(allChunksArray[:,1])
        maxcz = max(allChunksArray[:,1])
        
        origin = (mincx << 4, 0, mincz << 4)
        size = ((maxcx-mincx+1) << 4, self.Height, (maxcz-mincz+1) << 4)
        
        return BoundingBox(origin, size)
        
    
    def __str__(self):
        return "MCInfdevOldLevel(" + os.path.split(self.worldDir)[1] + ")"
    
    @property 
    def SizeOnDisk(self):
        return self.root_tag[Data]['SizeOnDisk'].value
    
    @SizeOnDisk.setter
    def SizeOnDisk(self, val):
        if 'SizeOnDisk' not in self.root_tag[Data]:
            self.root_tag[Data]['SizeOnDisk'] = TAG_Long(value=val)
        else:
            self.root_tag[Data]['SizeOnDisk'].value = val
    
    @property 
    def RandomSeed(self):
        return self.root_tag[Data]['RandomSeed'].value
    
    @RandomSeed.setter
    def RandomSeed(self, val):
        self.root_tag[Data]['RandomSeed'].value = val
    
    @property 
    def Time(self):
        """ Age of the world in ticks. 20 ticks per second; 24000 ticks per day."""
        return self.root_tag[Data]['Time'].value
    
    @Time.setter
    def Time(self, val):
        self.root_tag[Data]['Time'].value = val
    
    @property 
    def LastPlayed(self):
        return self.root_tag[Data]['LastPlayed'].value
    
    @LastPlayed.setter
    def LastPlayed(self, val):
        self.root_tag[Data]['LastPlayed'].value = val
    
    @property 
    def LevelName(self):
        if 'LevelName' not in self.root_tag[Data]: 
            return self.displayName
         
        return self.root_tag[Data]['LevelName'].value
    
    @LevelName.setter
    def LevelName(self, val):
        self.root_tag[Data]['LevelName'] = TAG_String(val)
    
    _bounds = None
    @property
    def bounds(self):
        if self._bounds is None: self._bounds = self.getWorldBounds();
        return self._bounds
        
    @property
    def size(self):
        return self.bounds.size
    
    def close(self):
        for rf in (self.regionFiles or {}).values():
                rf.close();
            
        self.regionFiles = {}
        
    def create(self, filename, random_seed, last_played):
        
        if filename == None:
            raise ValueError, "Can't create an Infinite level without a filename!"
        #create a new level
        root_tag = TAG_Compound();
        root_tag[Data] = TAG_Compound();
        root_tag[Data][SpawnX] = TAG_Int(0)
        root_tag[Data][SpawnY] = TAG_Int(2)
        root_tag[Data][SpawnZ] = TAG_Int(0)
        
        if last_played is None:
            last_played = long(time.time()*1000)
        if random_seed is None:
            random_seed = long(random.random() * 0xffffffffffffffffL) - 0x8000000000000000L

        root_tag[Data]['LastPlayed'] = TAG_Long(long(last_played))
        root_tag[Data]['RandomSeed'] = TAG_Long(long(random_seed))
        root_tag[Data]['SizeOnDisk'] = TAG_Long(long(0))
        root_tag[Data]['Time'] = TAG_Long(1)
        
        root_tag[Data]['version'] = TAG_Int(19132)
        root_tag[Data]['LevelName'] = TAG_String(os.path.basename(self.worldDir))
        ### if singleplayer:
        root_tag[Data][Player] = TAG_Compound()
        
        
        root_tag[Data][Player]['Air'] = TAG_Short(300);
        root_tag[Data][Player]['AttackTime'] = TAG_Short(0)
        root_tag[Data][Player]['DeathTime'] = TAG_Short(0);
        root_tag[Data][Player]['Fire'] = TAG_Short(-20);
        root_tag[Data][Player]['Health'] = TAG_Short(20);
        root_tag[Data][Player]['HurtTime'] = TAG_Short(0);
        root_tag[Data][Player]['Score'] = TAG_Int(0);
        root_tag[Data][Player]['FallDistance'] = TAG_Float(0)
        root_tag[Data][Player]['OnGround'] = TAG_Byte(0)

        root_tag[Data][Player]['Inventory'] = TAG_List()

        root_tag[Data][Player]['Motion'] = TAG_List([TAG_Double(0) for i in range(3)])
        root_tag[Data][Player]['Pos'] = TAG_List([TAG_Double([0.5,2.8,0.5][i]) for i in range(3)])
        root_tag[Data][Player]['Rotation'] = TAG_List([TAG_Float(0), TAG_Float(0)])
        
        #root_tag["Creator"] = TAG_String("MCEdit-"+release.release);
        
        if not os.path.exists(self.worldDir):
            os.mkdir(self.worldDir)
        
        self.root_tag = root_tag;
        
    def __init__(self, filename = None, create = False, random_seed=None, last_played=None):
        """
        Load an Alpha level from the given filename. It can point to either
        a level.dat or a folder containing one. If create is True, it will
        also create the world using the random_seed and last_played arguments.
        If they are none, a random 64-bit seed will be selected for RandomSeed
        and long(time.time()*1000) will be used for LastPlayed.
        
        If you try to create an existing world, its level.dat will be replaced.
        """
        
        self.Length = 0
        self.Width = 0
        self.Height = 128 #subject to change?
        self.playerTagCache = {}
    
        if not os.path.exists(filename):
            if not create:
                raise IOError, 'File not found'

            self.worldDir = filename
            os.mkdir(self.worldDir)
            
        if os.path.isdir(filename):
            self.worldDir = filename
            
        else:
            if os.path.basename(filename) in ("level.dat", "level.dat_old"):
                self.worldDir = os.path.dirname(filename)
            else:
                raise IOError, 'File is not a Minecraft Alpha world'
            
        self.filename = os.path.join(self.worldDir, "level.dat")
        self.regionDir = os.path.join(self.worldDir, "region")
        if not os.path.exists(self.regionDir):
            os.mkdir(self.regionDir)
                
        #maps (cx,cz) pairs to InfdevChunks    
        self._loadedChunks = {}
        self._allChunks = None
        self.dimensions = {};
        self.regionFiles = {}
        
        #used to limit memory usage
        self.loadedChunkQueue = dequeset()
        self.decompressedChunkQueue = dequeset()
        
        self.loadLevelDat(create, random_seed, last_played);
        
        #attempt to support yMod
        try:
            self.ChunkHeight = self.root_tag["Data"]["YLimit"].value
            self.Height = self.ChunkHeight
        except:
            pass
            
        self.playersDir = os.path.join(self.worldDir, "players");
        
        if os.path.isdir(self.playersDir):
            self.players = [x[:-4] for x in os.listdir(self.playersDir) if x.endswith(".dat")]
        
         
        
        self.preloadDimensions();
        #self.preloadChunkPositions();
       
    def loadLevelDat(self, create, random_seed, last_played):
        
        if create:
            self.create(self.filename, random_seed, last_played);
            self.saveInPlace();
        else:
            try:
                self.root_tag = nbt.load(self.filename)
            except Exception, e:
                filename_old = os.path.join(self.worldDir, "level.dat_old")
                info( "Error loading level.dat, trying level.dat_old ({0})".format( e ) )
                try:
                    self.root_tag = nbt.load(filename_old)
                    info( "level.dat restored from backup." )
                    self.saveInPlace();
                except Exception, e:
                    traceback.print_exc()
                    print repr(e)
                    info( "Error loading level.dat_old. Initializing with defaults." );
                    self.create(self.filename, random_seed, last_played);
    
    def preloadDimensions(self):
        worldDirs = os.listdir(self.worldDir);
        
        for dirname in worldDirs :
            if dirname.startswith("DIM"):
                try:
                    dimNo = int(dirname[3:]);
                    info( "Found dimension {0}".format(dirname))
                    dim = MCAlphaDimension(filename = os.path.join(self.worldDir, dirname));
                    dim.parentWorld = self;
                    dim.dimNo = dimNo
                    dim.root_tag = self.root_tag;
                    dim.filename = self.filename
                    dim.playersDir = self.playersDir;
                    dim.players = self.players
                    
                    self.dimensions[dimNo] = dim;
                except Exception, e:
                    error( u"Error loading dimension {0}: {1}".format(dirname, e))
                
                    
    def getRegionForChunk(self, cx, cz):
        rx = cx >> 5
        rz = cz >> 5
        rf = self.regionFiles.get( (rx,rz) )
        if rf: return rf
        rf = MCRegionFile(self.regionFilename(rx, rz), (rx,rz))
        self.regionFiles[rx,rz] = rf;
        return rf

    def preloadChunkPositions(self):
        if self.version == 19132:
            self.preloadRegions()
        else:
            self.preloadChunkPaths()
        
    def preloadRegions(self):
        info( u"Scanning for regions..." )
        self._allChunks = set()
        
        regionDir = os.path.join(self.worldDir, "region")
        if not os.path.exists(regionDir):
            os.mkdir(regionDir)
            
        regionFiles = os.listdir(regionDir)
        for filename in regionFiles:
            bits = filename.split('.')
            if len(bits) < 4 or bits[0] != 'r' or bits[3] != "mcr": continue
            
            try:
                rx, rz = map(int, bits[1:3])
            except ValueError:
                continue
            
            regionFile = MCRegionFile(os.path.join(regionDir, filename), (rx,rz))
            
            if regionFile.offsets.any():
                self.regionFiles[rx,rz] = regionFile
                
                for index, offset in enumerate(regionFile.offsets):
                    if offset:
                        cx = index & 0x1f
                        cz = index >> 5
                        
                        cx += rx << 5
                        cz += rz << 5
                        
                        self._allChunks.add( (cx,cz) )
            else:
                info( u"Removing empty region file {0}".format(filename) )
                regionFile.close()
                os.unlink(regionFile.path)
            
            
            
    def preloadChunkPaths(self):
        
        
        
        info( u"Scanning for chunks..." )
        worldDirs = os.listdir(self.worldDir);
        self._allChunks = set()
            
        for dirname in worldDirs:
            if(dirname in self.dirhashes):
                subdirs = os.listdir(os.path.join(self.worldDir, dirname));
                for subdirname in subdirs:
                    if(subdirname in self.dirhashes):
                        filenames = os.listdir(os.path.join(self.worldDir, dirname, subdirname));
                        #def fullname(filename):
                            #return os.path.join(self.worldDir, dirname, subdirname, filename);
                        
                        #fullpaths = map(fullname, filenames);
                        bits = map(lambda x:x.split('.'), filenames);

                        chunkfilenames = filter(lambda x:(len(x) == 4 and x[0].lower() == 'c' and x[3].lower() == 'dat'), bits)
                        
                        for c in chunkfilenames:
                            try:
                                cx, cz = (self.decbase36(c[1]), self.decbase36(c[2]))
                            except Exception, e:
                                info( u'Skipped file {0} ({1})'.format(u'.'.join(c), e) )
                                continue
                            
                            self._allChunks.add( (cx,cz) )
                            
                            #
                            
        info( u"Found {0} chunks.".format(len(self._allChunks)) )

    def compress(self):
        self.compressAllChunks();
        
    def compressAllChunks(self):
        for ch in self._loadedChunks.itervalues():
            ch.compress();
            
    def compressChunk(self, cx, cz):
        if not (cx,cz) in self._loadedChunks: return; #not an error
        self._loadedChunks[cx,cz].compress()
    
    decompressedChunkLimit = 2048 # about 320 megabytes
    loadedChunkLimit = 8192 # from 8mb to 800mb depending on chunk contents
    
            
    def chunkDidCompress(self, chunk):
        self.decompressedChunkQueue.discard(chunk)
    
    def chunkDidDecompress(self, chunk):
        if not chunk in self.decompressedChunkQueue:
            self.decompressedChunkQueue.append(chunk);
            if self.decompressedChunkLimit and (len(self.decompressedChunkQueue) > self.decompressedChunkLimit):
                oldestChunk = self.decompressedChunkQueue[0];
                oldestChunk.compress(); #calls chunkDidCompress
    
    def chunkDidUnload(self, chunk):
        self.loadedChunkQueue.discard(chunk)
        
    def chunkDidLoad(self, chunk):
        if not chunk in self.loadedChunkQueue:
            self.loadedChunkQueue.append(chunk);
            if self.loadedChunkLimit and (len(self.loadedChunkQueue) > self.loadedChunkLimit):
                oldestChunk = self.loadedChunkQueue[0];
                oldestChunk.unload(); #calls chunkDidUnload
    
    @property
    @decompress_first
    def version(self):
        if 'version' in self.root_tag['Data']:
            return self.root_tag['Data']['version'].value
        else:
            return None
            
    
    def _loadChunk(self, chunk):
        """ load the chunk data from disk, and set the chunk's compressedTag
         and root_tag"""
        
        cx,cz = chunk.chunkPosition
        try:
            if self.version:
                regionFile = self.getRegionForChunk(cx,cz)
                regionFile.loadChunk(chunk)
                
            else:
                with file(chunk.filename, 'rb') as f:
                    cdata = f.read()
                    chunk.compressedTag = cdata
                    data = gunzip(cdata)
                    chunk.root_tag = nbt.load(buf=data)
                        
        except Exception, e:
            raise ChunkMalformed, "Chunk {0} had an error: {1!r}".format(chunk.chunkPosition, e)
        
    
    def _saveChunk(self, chunk):
        cx,cz = chunk.chunkPosition
        if self.version:
            regionFile = self.getRegionForChunk(cx,cz)
            
            regionFile.saveChunk(chunk)
        else:
            dir1 = os.path.dirname(chunk.filename)
            dir2 = os.path.dirname(dir1)
            
            if not os.path.exists(dir2):
                os.mkdir(dir2)
            if not os.path.exists(dir1):
                os.mkdir(dir1)
            
            chunk.compress()
            with file(chunk.filename, 'wb') as f:
                f.write(chunk.compressedTag)
            
    def discardAllChunks(self):
        """ clear lots of memory, fast. """
        
    def chunkFilenameAt(self, x, y, z):
        cx = x >> 4
        cz = z >> 4
        return self._loadedChunks.get( (cx, cz) ).filename
    
    base36alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    def decbase36(self, s):
        return int(s, 36)
    
    def base36(self, n):
        n = int(n);
        if 0 == n: return '0'
        neg = "";
        if n < 0:
            neg = "-"
            n = -n;
            
        work = []

        while(n):
            n, digit = divmod(n, 36)
            work.append(self.base36alphabet[digit])
        
        return neg + ''.join(reversed(work))

    def dirhash(self, n):
        return self.dirhashes[n%64];
    
    def _dirhash(n):
        n=n%64;
        s=u"";
        if(n>=36):
            s+=u"1";
            n-=36;
        s+=u"0123456789abcdefghijklmnopqrstuvwxyz"[n]

        return s;
    
    dirhashes = [_dirhash(n) for n in range(64)];
    
    def regionFilename(self, rx, rz):
        s= os.path.join(self.regionDir,
                                     "r.%s.%s.mcr" % ((rx), (rz)));
        return s;
    
    def chunkFilename(self, x, z):
        s= os.path.join(self.worldDir, self.dirhash(x), self.dirhash(z),
                                     "c.%s.%s.dat" % (self.base36(x), self.base36(z)));
        return s;
    
    def extractChunksInBox(self, box, parentFolder):
        for cx,cz in box.chunkPositions:
            if self.containsChunk(cx,cz):
                self.extractChunk(cx,cz, parentFolder)
                
    def extractChunk(self, cx, cz, parentFolder):
        if not os.path.exists(parentFolder):
            os.mkdir(parentFolder)
        
        chunkFilename = self.chunkFilename(cx,cz)
        outputFile = os.path.join(parentFolder, os.path.basename(chunkFilename))
        
        chunk = self.getChunk(cx,cz)
        if chunk.compressMode == MCRegionFile.VERSION_GZIP:
            chunk.compress()
            data = chunk.compressedTag;
        else:
            chunk.decompress()
            data = chunk.compressTagGzip(chunk.root_tag)
        
        with file(outputFile, "wb") as f:
            f.write(data)
            
        
    def blockLightAt(self, x, y, z):
        if y < 0 or y >= self.Height: return 0
        zc=z >> 4
        xc=x >> 4
        
        xInChunk = x&0xf;
        zInChunk = z&0xf;
        ch = self.getChunk(xc,zc)
        
        return ch.BlockLight[xInChunk,zInChunk,y]
        
        
    def setBlockLightAt(self, x, y, z, newLight):
        if y < 0 or y >= self.Height: return 0
        zc=z>>4
        xc=x>>4
        
        xInChunk = x&0xf;
        zInChunk = z&0xf;
        
        ch = self.getChunk(xc,zc)
        ch.BlockLight[xInChunk, zInChunk, y] = newLight
        ch.chunkChanged(False)
        
    def blockDataAt(self, x, y, z):
        if y < 0 or y >= self.Height: return 0
        zc=z>>4
        xc=x>>4
        
        xInChunk = x&0xf;
        zInChunk = z&0xf;
        
        try:
            ch = self.getChunk(xc,zc)
        except ChunkNotPresent:
            return 0
            
        return ch.Data[xInChunk,zInChunk,y]

        
    def setBlockDataAt(self, x,y,z, newdata):
        if y < 0 or y >= self.Height: return 0
        zc=z>>4
        xc=x>>4
        

        xInChunk = x&0xf;
        zInChunk = z&0xf;

        try:
            ch = self.getChunk(xc,zc)
        except ChunkNotPresent:
            return 0
            
        ch.Data[xInChunk, zInChunk, y] = newdata
        ch.chunkChanged(False)
        
    def blockAt(self, x, y, z):
        """returns 0 for blocks outside the loadable chunks.  automatically loads chunks."""
        if y < 0 or y >= self.Height: return 0

        zc=z>>4
        xc=x>>4
        xInChunk = x & 0xf;
        zInChunk = z & 0xf;
        
        try:
            ch = self.getChunk(xc,zc)
        except ChunkNotPresent:
            return 0
            
        return ch.Blocks[xInChunk, zInChunk, y]
        
    def setBlockAt(self, x, y, z, blockID):
        """returns 0 for blocks outside the loadable chunks.  automatically loads chunks."""
        if y < 0 or y >= self.Height: return 0

        zc=z>>4
        xc=x>>4
        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        try:
            ch = self.getChunk(xc,zc)
        except ChunkNotPresent:
            return 0
            
        ch.Blocks[xInChunk, zInChunk, y] = blockID
        ch.chunkChanged(False)

    def skylightAt(self, x, y, z):

        if y < 0 or y >= self.Height: return 0
        zc=z>>4
        xc=x>>4
        

        xInChunk = x & 0xf;
        zInChunk = z & 0xf
        
        ch = self.getChunk(xc,zc)
        
        return ch.SkyLight[xInChunk, zInChunk, y]

        
    def setSkylightAt(self, x, y, z, lightValue):
        if y < 0 or y >= self.Height: return 0
        zc=z>>4
        xc=x>>4
        
        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        ch = self.getChunk(xc,zc)
        skyLight = ch.SkyLight
        
        oldValue = skyLight[xInChunk, zInChunk, y]
            
        ch.chunkChanged(False)
        if oldValue < lightValue: 
            skyLight[xInChunk, zInChunk, y] = lightValue
        return oldValue < lightValue
    
    def heightMapAt(self, x, z):
        zc=z>>4
        xc=x>>4
        xInChunk = x & 0xf;
        zInChunk = z & 0xf;
        
        ch = self.getChunk(xc,zc)
        
        heightMap = ch.HeightMap

        return heightMap[zInChunk,xInChunk]; 
        #the heightmap is ordered differently because in minecraft it is a flat array
    
    @property
    def loadedChunks(self):
        return self._loadedChunks.keys();
    
    @property
    def chunkCount(self):
        """Returns the number of chunks in the level. May initiate a costly
        chunk scan."""
        if self._allChunks is None:
            self.preloadChunkPositions()
        return len(self._allChunks)
           
    @property
    def allChunks(self):
        """Iterates over (xPos, zPos) tuples, one for each chunk in the level.
        May initiate a costly chunk scan."""
        if self._allChunks is None:
            self.preloadChunkPositions()
        return self._allChunks.__iter__();
    
    
    def getChunks(self, chunks = None):
        """ pass a list of chunk coordinate tuples to get a list of InfdevChunks. 
        pass nothing for a list of every chunk in the level. 
        the chunks are automatically loaded."""
        if chunks is None: chunks = self.allChunks;
        return [self.getChunk(cx,cz) for (cx,cz) in chunks if self.containsChunk(cx,cz)]
            
    
    def _makeChunk(self, cx,cz):
        """return the InfdevChunk object at the given position. because loading
        the chunk is done later, accesses to chunk attributes may 
        raise ChunkMalformed"""
        
        if not self.containsChunk(cx,cz):
            raise ChunkNotPresent, (cx,cz);
                
        if not (cx,cz) in self._loadedChunks: 
            self._loadedChunks[cx,cz] = InfdevChunk(self, (cx, cz));
        
        return self._loadedChunks[cx,cz]
    
    def chunkIsLoaded(self, cx, cz):
        if (cx,cz) in self._loadedChunks:
            return self._loadedChunks[(cx,cz)].isLoaded()
                
        return False
    
    def chunkIsCompressed(self, cx, cz):
        if (cx,cz) in self._loadedChunks:
            return self._loadedChunks[(cx,cz)].isCompressed()
                
        return False
    
    def chunkIsDirty(self, cx, cz):
        if (cx,cz) in self._loadedChunks:
            return self._loadedChunks[(cx,cz)].dirty
                
        return False
    
    def getChunk(self, cx, cz):
        """ read the chunk from disk, load it, and return it. 
        decompression and unpacking is done lazily."""
        
        
        c = self._makeChunk(cx,cz)
        c.load();
        if not (cx,cz) in self._loadedChunks:
            raise ChunkMalformed, "Chunk {0} malformed".format((cx,cz))
            self.world.malformedChunk(*self.chunkPosition);
            
        return c;

    def markDirtyChunk(self, cx, cz):
        if not (cx,cz) in self._loadedChunks: return
        self._loadedChunks[cx,cz].chunkChanged();
    
    def markDirtyBox(self, box):
        for cx,cz in box.chunkPositions:
            self.markDirtyChunk(cx,cz)
            
    def saveInPlace(self):
        for level in self.dimensions.itervalues():
            level.saveInPlace(True);

        dirtyChunkCount = 0;
        if self._loadedChunks:
            for chunk in self._loadedChunks.values():
                if chunk.dirty: 
                    dirtyChunkCount += 1;
                chunk.save();
        
        for path, tag in self.playerTagCache.iteritems():
            tag.saveGzipped(path)
        
        self.playerTagCache = {}
        
        self.root_tag.save(self.filename);
        info( u"Saved {0} chunks".format(dirtyChunkCount) )
       
    def generateLights(self, dirtyChunks = None):
        """ dirtyChunks may be an iterable yielding (xPos,zPos) tuples
        if none, generate lights for all chunks that need lighting
        """
            
        startTime = datetime.now();
        
        if dirtyChunks is None:
            dirtyChunks = (ch for ch in self._loadedChunks.itervalues() if ch.needsLighting)
        else:
            dirtyChunks = (self._makeChunk(*c) for c in dirtyChunks if self.containsChunk(*c))
            
        dirtyChunks = sorted(dirtyChunks, key=lambda x:x.chunkPosition)
         
        
        #at 150k per loaded chunk, 
        maxLightingChunks = 4000
        
        info( u"Asked to light {0} chunks".format(len(dirtyChunks)) )
        chunkLists = [dirtyChunks];
        def reverseChunkPosition(x):
            cx,cz = x.chunkPosition;
            return cz,cx
            
        def splitChunkLists(chunkLists):
            newChunkLists = []
            for l in chunkLists:
                
                #list is already sorted on x position, so this splits into left and right
                
                smallX = l[:len(l)/2]
                bigX = l[len(l)/2:]
                
                #sort halves on z position
                smallX = sorted(smallX, key=reverseChunkPosition) 
                bigX = sorted(bigX, key=reverseChunkPosition) 
                
                #add quarters to list
                
                newChunkLists.append(smallX[:len(smallX)/2])
                newChunkLists.append(smallX[len(smallX)/2:])
                
                newChunkLists.append(bigX[:len(bigX)/2])
                newChunkLists.append(bigX[len(bigX)/2:])
                
            return newChunkLists
            
        while len(chunkLists[0]) > maxLightingChunks:
            chunkLists = splitChunkLists(chunkLists);
        
        if len(chunkLists) > 1:
            info( u"Using {0} batches to conserve memory.".format(len(chunkLists)) )
        
        i=0
        for dc in chunkLists:
            i+=1;
            info( u"Batch {0}/{1}".format(i, len(chunkLists)) )
            
            dc = sorted(dc, key=lambda x:x.chunkPosition) 
        
            self._generateLights(dc)
            for ch in dc:
                ch.compress();
        timeDelta = datetime.now()-startTime;
        
        if len(dirtyChunks):
            info( u"Completed in {0}, {1} per chunk".format(timeDelta, dirtyChunks and timeDelta/len(dirtyChunks) or 0) )
            
        return;
        
    def _generateLights(self, dirtyChunks):
        conserveMemory = False
        la = array(self.materials.lightAbsorption)
        
            #[d.genFastLights() for d in dirtyChunks]
        dirtyChunks = set(dirtyChunks)
        
        for ch in list(dirtyChunks): 
            #relight all blocks in neighboring chunks in case their light source disappeared.
            cx,cz = ch.chunkPosition
            for dx,dz in itertools.product( (-1, 0, 1), (-1, 0, 1) ):
                if (cx+dx,cz+dz) in self._loadedChunks:
                    dirtyChunks.add(self._loadedChunks[(cx+dx,cz+dz)]);
        
        dirtyChunks = sorted(dirtyChunks, key=lambda x:x.chunkPosition) 
                   
        info( u"Lighting {0} chunks".format(len(dirtyChunks)) )
        for chunk in dirtyChunks:
            try:
                chunk.load();
            except (ChunkNotPresent, ChunkMalformed):
                continue;
            chunk.chunkChanged();
            
            assert chunk.dirty and chunk.needsLighting
            
            chunk.BlockLight[:] = self.materials.lightEmission[chunk.Blocks];
            
            if conserveMemory:
                chunk.compress();
            
        zeroChunk = ZeroChunk(self.Height)
        zeroChunk.BlockLight[:] = 0;
        zeroChunk.SkyLight[:] = 0;
        
           
        la[18] = 0; #for normal light dispersal, leaves absorb the same as empty air.
        startingDirtyChunks = dirtyChunks
        
        oldLeftEdge = zeros( (1, 16, self.Height), 'uint8');
        oldBottomEdge = zeros( (16, 1, self.Height), 'uint8');
        oldChunk = zeros( (16, 16, self.Height), 'uint8');
        if self.dimNo == -1: 
            lights = ("BlockLight", )
        else:
            lights = ("BlockLight", "SkyLight")
        info( u"Dispersing light..." )
        for light in lights:
          zerochunkLight = getattr(zeroChunk, light); 
          
          newDirtyChunks = list(startingDirtyChunks);
           
          for i in range(14):
            if len(newDirtyChunks) == 0: break
            
            info( u"{0} Pass {1}: {2} chunks".format(light, i, len(newDirtyChunks)) );
            
            """
            propagate light!
            for each of the six cardinal directions, figure a new light value for 
            adjoining blocks by reducing this chunk's light by light absorption and fall off. 
            compare this new light value against the old light value and update with the maximum.
            
            we calculate all chunks one step before moving to the next step, to ensure all gaps at chunk edges are filled.  
            we do an extra cycle because lights sent across edges may lag by one cycle.
            """
            newDirtyChunks = set(newDirtyChunks)
            newDirtyChunks.discard(zeroChunk)
            
            dirtyChunks = sorted(newDirtyChunks, key=lambda x:x.chunkPosition) 
            
            newDirtyChunks = list();
            
            
            for chunk in dirtyChunks:
                #xxx code duplication
                (cx,cz) = chunk.chunkPosition
                neighboringChunks = {};
                try:
                    chunk.load();
                except (ChunkNotPresent, ChunkMalformed), e:
                    print "Chunk error during relight, chunk skipped: ", e
                    continue;
                    
                for dir,dx,dz in ( (FaceXDecreasing,-1,0), 
                                      (FaceXIncreasing,1,0), 
                                      (FaceZDecreasing,0, -1), 
                                      (FaceZIncreasing,0, 1) ):
                    try:
                        neighboringChunks[dir] = self.getChunk(cx+dx,cz+dz)
                    except (ChunkNotPresent, ChunkMalformed):
                        neighboringChunks[dir] = zeroChunk;
                
                
                chunkLa = la[chunk.Blocks]+1;
                chunkLight = getattr(chunk,light);
                oldChunk[:] = chunkLight[:]
                
                
                nc = neighboringChunks[FaceXDecreasing]
                ncLight = getattr(nc,light);
                oldLeftEdge[:] = ncLight[15:16,:,0:self.Height] #save the old left edge 
                
                #left edge
                newlight = (chunkLight[0:1,:,:self.Height]-la[nc.Blocks[15:16,:,0:self.Height]])-1
                newlight[newlight>15]=0;
                
                ncLight[15:16,:,0:self.Height] = maximum(ncLight[15:16,:,0:self.Height], newlight)
                
                #chunk body
                newlight = (chunkLight[1:16,:,0:self.Height]-chunkLa[0:15,:,0:self.Height])
                newlight[newlight>15]=0; #light went negative;
                
                chunkLight[0:15,:,0:self.Height] = maximum(chunkLight[0:15,:,0:self.Height], newlight)
                
                #right edge
                nc = neighboringChunks[FaceXIncreasing]
                ncLight = getattr(nc,light);
                
                newlight = ncLight[0:1,:,:self.Height]-chunkLa[15:16,:,0:self.Height]
                newlight[newlight>15]=0;
                
                chunkLight[15:16,:,0:self.Height] = maximum(chunkLight[15:16,:,0:self.Height], newlight)
                
            
                #right edge
                nc = neighboringChunks[FaceXIncreasing]
                ncLight = getattr(nc,light);
                
                newlight = (chunkLight[15:16,:,0:self.Height]-la[nc.Blocks[0:1,:,0:self.Height]])-1
                newlight[newlight>15]=0;
                
                ncLight[0:1,:,0:self.Height] = maximum(ncLight[0:1,:,0:self.Height], newlight)
                
                #chunk body
                newlight = (chunkLight[0:15,:,0:self.Height]-chunkLa[1:16,:,0:self.Height])
                newlight[newlight>15]=0;
                
                chunkLight[1:16,:,0:self.Height] = maximum(chunkLight[1:16,:,0:self.Height], newlight)
                
                #left edge
                nc = neighboringChunks[FaceXDecreasing]
                ncLight = getattr(nc,light);
                
                newlight = ncLight[15:16,:,:self.Height]-chunkLa[0:1,:,0:self.Height]
                newlight[newlight>15]=0;
                
                chunkLight[0:1,:,0:self.Height] = maximum(chunkLight[0:1,:,0:self.Height], newlight)
               
                zerochunkLight[:] = 0;
                
                #check if the left edge changed and dirty or compress the chunk appropriately
                if (oldLeftEdge != ncLight[15:16,:,:self.Height]).any():
                    #chunk is dirty
                    newDirtyChunks.append(nc)
                
                #bottom edge
                nc = neighboringChunks[FaceZDecreasing]
                ncLight = getattr(nc,light);
                oldBottomEdge[:] = ncLight[:,15:16,:self.Height] # save the old bottom edge
                
                newlight = (chunkLight[:,0:1,:self.Height]-la[nc.Blocks[:,15:16,:self.Height]])-1
                newlight[newlight>15]=0;
                
                ncLight[:,15:16,:self.Height] = maximum(ncLight[:,15:16,:self.Height], newlight)
                
                #chunk body
                newlight = (chunkLight[:,1:16,:self.Height]-chunkLa[:,0:15,:self.Height])
                newlight[newlight>15]=0;
                
                chunkLight[:,0:15,:self.Height] = maximum(chunkLight[:,0:15,:self.Height], newlight)
                
                #top edge
                nc = neighboringChunks[FaceZIncreasing]
                ncLight = getattr(nc,light);
                
                newlight = ncLight[:,0:1,:self.Height]-chunkLa[:,15:16,0:self.Height]
                newlight[newlight>15]=0;
                
                chunkLight[:,15:16,0:self.Height] = maximum(chunkLight[:,15:16,0:self.Height], newlight)
               
                   
                #top edge  
                nc = neighboringChunks[FaceZIncreasing]
                
                ncLight = getattr(nc,light);
                
                newlight = (chunkLight[:,15:16,:self.Height]-la[nc.Blocks[:,0:1,:self.Height]])-1
                newlight[newlight>15]=0;
                
                ncLight[:,0:1,:self.Height] = maximum(ncLight[:,0:1,:self.Height], newlight)
                
                #chunk body
                newlight = (chunkLight[:,0:15,:self.Height]-chunkLa[:,1:16,:self.Height])
                newlight[newlight>15]=0;
                
                chunkLight[:,1:16,:self.Height] = maximum(chunkLight[:,1:16,:self.Height], newlight)
                
                #bottom edge
                nc = neighboringChunks[FaceZDecreasing]
                ncLight = getattr(nc,light);
               
                newlight = ncLight[:,15:16,:self.Height]-chunkLa[:,0:1,0:self.Height]
                newlight[newlight>15]=0;
                
                chunkLight[:,0:1,0:self.Height] = maximum(chunkLight[:,0:1,0:self.Height], newlight)
               
                zerochunkLight[:] = 0;
                
                if (oldBottomEdge != ncLight[:,15:16,:self.Height]).any():
                    newDirtyChunks.append(nc)
                        
                newlight = (chunkLight[:,:,0:self.Height-1]-chunkLa[:,:,1:self.Height])
                newlight[newlight>15]=0;
                chunkLight[:,:,1:self.Height] = maximum(chunkLight[:,:,1:self.Height], newlight)
                
                newlight = (chunkLight[:,:,1:self.Height]-chunkLa[:,:,0:self.Height-1])
                newlight[newlight>15]=0;
                chunkLight[:,:,0:self.Height-1] = maximum(chunkLight[:,:,0:self.Height-1], newlight)
                zerochunkLight[:] = 0;
                
                if (oldChunk != chunkLight).any():
                    newDirtyChunks.append(chunk);
                    
        for ch in startingDirtyChunks:
            ch.needsLighting = False;
                    

    def entitiesAt(self, x, y, z):
        chunk = self.getChunk(x>>4, z>>4)
        entities = [];
        if chunk.Entities is None: return entities;
        for entity in chunk.Entities:
            if map(lambda x:int(x.value), entity[Pos]) == [x,y,z]:
                entities.append(entity);

        return entities;

    def addEntity(self, entity):
        assert isinstance(entity, TAG_Compound)
        x = int(entity[Pos][0].value)
        z = int(entity[Pos][2].value)
        
        try:
            chunk = self.getChunk(x>>4, z>>4)
        except (ChunkNotPresent, ChunkMalformed), e:
            return None
            # raise Error, can't find a chunk?
        chunk.Entities.append(entity);
        chunk.dirty = True
        
    def tileEntityAt(self, x, y, z):
        chunk = self.getChunk(x>>4, z>>4)
        entities = [];
        if chunk.TileEntities is None: return None;
        for entity in chunk.TileEntities:
            pos = [entity[a].value for a in 'xyz']
            if pos == [x,y,z]:
                entities.append(entity);

        if len(entities) > 1:
            info("Multiple tile entities found: {0}".format(entities))
        if len(entities) == 0:
            return None
            
        return entities[0];


    def addTileEntity(self, entity):
        assert isinstance(entity, TAG_Compound)
        if not 'x' in entity: return
        
        x = int(entity['x'].value)
        y = int(entity['y'].value)
        z = int(entity['z'].value)

        try:
            chunk = self.getChunk(x>>4, z>>4)
        except (ChunkNotPresent, ChunkMalformed):
            return 
            # raise Error, can't find a chunk?
        def differentPosition(a):
            return not ((entity is a) or ('x' in a and (a['x'].value == x and a['y'].value == y and a['z'].value == z)))
            
        chunk.TileEntities.value[:] = filter(differentPosition, chunk.TileEntities);
        
        chunk.TileEntities.append(entity);
        chunk.dirty = True
        
    def removeEntitiesInBox(self, box):
        count = 0;
        for chunk, slices, point in self.getChunkSlices(box):
            count += chunk.removeEntitiesInBox(box);
            chunk.compress();
        info( "Removed {0} entities".format(count) )
        return count;
        
    def removeTileEntitiesInBox(self, box):
        count = 0;
        for chunk, slices, point in self.getChunkSlices(box):
            count += chunk.removeTileEntitiesInBox(box);
            chunk.compress();
        info( "Removed {0} tile entities".format(count) )
        return count;
            
    def fillBlocks(self, box, blockInfo, blocksToReplace = []):
        if box is None:
            chunkIterator = self.getAllChunkSlices() 
            box = self.bounds
        else:
            chunkIterator = self.getChunkSlices(box)
        
        #shouldRetainData = (not blockInfo.hasAlternate and not any([b.hasAlternate for b in blocksToReplace]))
        #if shouldRetainData:
        #    info( "Preserving data bytes" )
        shouldRetainData = False #xxx old behavior overwrote blockdata with 0 when e.g. replacing water with lava
        
        info("Replacing {0} with {1}".format(blocksToReplace, blockInfo))
        
        changesLighting = True
            
        if len(blocksToReplace):
            blocktable = self.blockReplaceTable(blocksToReplace)
            
            newAbsorption = self.materials.lightAbsorption[blockInfo.ID]
            oldAbsorptions = [self.materials.lightAbsorption[b.ID] for b in blocksToReplace]
            changesLighting = False
            for a in oldAbsorptions:
                if a != newAbsorption: changesLighting = True;
                
            newEmission = self.materials.lightEmission[blockInfo.ID]
            oldEmissions = [self.materials.lightEmission[b.ID] for b in blocksToReplace]
            for a in oldEmissions:
                if a != newEmission: changesLighting = True;
        
        
        i=0;
        skipped = 0
        replaced = 0;
        
        for (chunk, slices, point) in chunkIterator:
            i+=1;
            if i % 100 == 0:
                info( u"Chunk {0}...".format(i) )
                
            blocks = chunk.Blocks[slices] 
            data = chunk.Data[slices]
            mask = slice(None)
            
            needsLighting = changesLighting;
              
            if len(blocksToReplace):
                mask = blocktable[blocks,data]
            
                blockCount = mask.sum()
                replaced += blockCount;
                
                #don't waste time relighting and copying if the mask is empty
                if blockCount:
                    blocks[:][mask] = blockInfo.ID
                    if not shouldRetainData:
                        data[mask] = blockInfo.blockData
                else:
                    skipped += 1;
                    needsLighting = False;
                    
                def include(tileEntity):
                    p = TileEntity.pos(tileEntity)
                    x,y,z = map(lambda a,b,c:(a-b)-c, p, point, box.origin)
                    return not ((p in box) and mask[x,z,y])
                    
                chunk.TileEntities.value[:] = filter(include, chunk.TileEntities)
                
                 
                    
            else:
                blocks[:] = blockInfo.ID
                if not shouldRetainData:
                    data[:] = blockInfo.blockData
                chunk.removeTileEntitiesInBox(box)
            
            chunk.chunkChanged(needsLighting);
            chunk.compress();
            
        if len(blocksToReplace):
            info( u"Replace: Skipped {0} chunks, replaced {1} blocks".format(skipped, replaced) )
            
    

    def copyBlocksFromFinite(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy):
        #assumes destination point and bounds have already been checked.
        (sx, sy, sz) = sourceBox.origin
        
        #filterTable = self.conversionTableFromLevel(sourceLevel);
        
        start = datetime.now();
        
        if blocksToCopy is not None:
            typemask = zeros( (256) , dtype='bool')
            typemask[blocksToCopy] = 1;
        
        
        destChunks = self.getChunkSlices(BoundingBox(destinationPoint, sourceBox.size))
        i = 0;
        
        for (chunk, slices, point) in destChunks:
            i+= 1;
            if i % 100 == 0:
                info("Chunk {0}...".format(i))
                
            blocks = chunk.Blocks[slices];
            mask = slice(None, None)
            
            localSourceCorner2 = (
                sx+point[0] + blocks.shape[0],
                sy + blocks.shape[2],
                sz+point[2] + blocks.shape[1],
            )
            
            sourceBlocks = sourceLevel.Blocks[sx+point[0]:localSourceCorner2[0],
                                              sz+point[2]:localSourceCorner2[2],
                                              sy:localSourceCorner2[1]]
            #sourceBlocks = filterTable[sourceBlocks]
            
            #for small level slices, reduce the destination area
            x,z,y = sourceBlocks.shape
            blocks = blocks[0:x,0:z,0:y]
            if blocksToCopy is not None:
                mask = typemask[sourceBlocks]

            sourceData = None            
            if hasattr(sourceLevel, 'Data'):
                #indev or schematic
                sourceData = sourceLevel.Data[sx+point[0]:localSourceCorner2[0],
                                              sz+point[2]:localSourceCorner2[2],
                                              sy:localSourceCorner2[1]]
            
            data = chunk.Data[slices][0:x,0:z,0:y]
                
                
                
            convertedSourceBlocks, convertedSourceData = self.convertBlocksFromLevel(sourceLevel, sourceBlocks, sourceData)
                
            blocks[mask] = convertedSourceBlocks[mask]
            if convertedSourceData is not None:
                data[mask] = (convertedSourceData[:,:,:])[mask]
                data[mask] &= 0xf;
                   
            chunk.chunkChanged();
            chunk.compress();
        
        d = datetime.now()-start;
        if i:
            info( "Finished {2} chunks in {0} ({1} per chunk)".format(d, d / i, i) )
        
            #chunk.compress(); #xxx find out why this trashes changes to tile entities
    
    def copyBlocksFromInfinite(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy):
        """ copy blocks between two infinite levels via repeated export/import.  hilariously slow. """
        
        #assumes destination point and bounds have already been checked.
        
        tempSize = 128
        
        def iterateSubsections():
            #tempShape = (tempSize, sourceBox.height, tempSize)
            dx, dy, dz = destinationPoint
            ox, oy, oz = sourceBox.origin
            sx, sy, sz = sourceBox.size
            mx, my, mz = sourceBox.maximum
            for x,z in itertools.product(arange(ox, ox+sx, tempSize), arange(oz, oz+sz, tempSize)):
                box = BoundingBox((x, oy, z), (min(tempSize, mx-x), sy, min(tempSize, mz-z)))
                destPoint = (dx + x - ox, dy, dz + z - oz)
                yield box, destPoint
        
        
        destBox = BoundingBox(destinationPoint, sourceBox.size)
        
        def isChunkBox(box):
            return box.isChunkAligned and box.miny == 0 and box.height == sourceLevel.Height
        
        if isChunkBox(sourceBox) and isChunkBox(destBox):
            print "Copying with chunk alignment!"
            cxoffset = destBox.mincx - sourceBox.mincx
            czoffset = destBox.mincz - sourceBox.mincz
            
            typemask = zeros( (256,), dtype='bool')
            if blocksToCopy:
                typemask[blocksToCopy] = True
                
            changedChunks = deque();
            i=0;
            for cx,cz in sourceBox.chunkPositions:
                i+=1;
                if i % 100 == 0:
                    info("Chunk {0}...".format(i))
                    
                dcx = cx+cxoffset
                dcz = cz+czoffset
                try:
                    sourceChunk = sourceLevel.getChunk(cx, cz);
                    destChunk = self.getChunk(dcx, dcz);
                except (ChunkNotPresent, ChunkMalformed), e:
                    continue;
                else:
                    x = cx<<4
                    z = cz<<4
                    width = sourceBox.maxx-x;
                    length = sourceBox.maxz-z;
                    if width<16 or length<16:
                        slices = (slice(0, width), slice(0, length), slice(None, None));
                    else:
                        slices = (slice(None, None))
                    
                    mask = slice(None, None)
                    if blocksToCopy:
                        mask = typemask[sourceChunk.Blocks[slices]]
                        
                    destChunk.Blocks[slices][mask] = sourceChunk.Blocks[slices][mask]
                    destChunk.Data[slices][mask] = sourceChunk.Data[slices][mask]
                    destChunk.BlockLight[slices][mask] = sourceChunk.BlockLight[slices][mask]
                    destChunk.SkyLight[slices][mask] = sourceChunk.SkyLight[slices][mask]
                    destChunk.copyEntitiesFrom(sourceChunk, sourceBox, destinationPoint);
                    generateHeightMap(destChunk)
                    
                    changedChunks.append(destChunk);
                    
                    destChunk.dirty = True;
                    destChunk.unload(); #also saves the chunk
                    
            #calculate which chunks need lighting after the mass copy. 
            #find non-changed chunks adjacent to changed ones and mark for light
            changedChunkPositions = set([ch.chunkPosition for ch in changedChunks])
            
            for ch in changedChunks:
                cx,cz = ch.chunkPosition
                
                for dx, dz in itertools.product( (-1, 0, 1), (-1, 0, 1) ):
                    ncPos = (cx+dx, cz+dz);
                    if ncPos not in changedChunkPositions:
                        ch = self._loadedChunks.get((cx,cz), None);
                        if ch:
                            ch.needsLighting = True
                
        else:  
            i=0;
            for box, destPoint in iterateSubsections():
                info( "Subsection {0} at {1}".format(i, destPoint) )
                temp = sourceLevel.extractSchematic(box);
                self.copyBlocksFrom(temp, BoundingBox( (0,0,0), box.size ), destPoint, blocksToCopy);
                i+= 1;
            
                    
    def copyBlocksFrom(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy = None):
        (x,y,z) = destinationPoint;
        (lx,ly,lz) = sourceBox.size
        #sourcePoint, sourcePoint1 = sourceBox
        
        sourceBox, destinationPoint = self.adjustCopyParameters(sourceLevel, sourceBox, destinationPoint)
        #needs work xxx
        info( u"Copying {0} blocks from {1} to {2}" .format (ly*lz*lx,sourceBox, destinationPoint) )
        startTime = datetime.now()
        
        if(not isinstance(sourceLevel, MCInfdevOldLevel)):
            self.copyBlocksFromFinite(sourceLevel, sourceBox, destinationPoint, blocksToCopy)
            

        else:
            self.copyBlocksFromInfinite(sourceLevel, sourceBox, destinationPoint, blocksToCopy) 

        self.copyEntitiesFrom(sourceLevel, sourceBox, destinationPoint)
        info( "Duration: {0}".format(datetime.now()-startTime) )
        #self.saveInPlace()
 

    def containsPoint(self, x, y, z):
        if y<0 or y>127: return False;
        return self.containsChunk(x>>4, z>>4)
    
    def containsChunk(self, cx, cz):
        if self._allChunks is not None: return (cx, cz) in self._allChunks;
        if (cx,cz) in self._loadedChunks: return True;
        if self.version:
            return (cx,cz) in self.allChunks
        else:
            return os.path.exists(self.chunkFilename(cx, cz))
    
    def malformedChunk(self, cx, cz):
        debug( u"Forgetting malformed chunk {0} ({1})".format((cx,cz), self.chunkFilename(cx,cz)) )
        if (cx,cz) in self._loadedChunks:
            del self._loadedChunks[(cx,cz)]
            self._bounds = None
            
    def createChunk(self, cx, cz):
        if self.containsChunk(cx,cz): raise ValueError, "{0}:Chunk {1} already present!".format(self, (cx,cz) )
        if self._allChunks is not None: 
            self._allChunks.add( (cx,cz) )
                
        self._loadedChunks[cx,cz] = InfdevChunk(self, (cx,cz), create = True)
        self._bounds = None
    
    def createChunks(self, chunks):
        
        i=0;
        ret = [];
        for cx,cz in chunks:
            i+=1;
            if not self.containsChunk(cx,cz):
                ret.append( (cx,cz) )
                self.createChunk(cx,cz);
                self.compressChunk(cx,cz);
            assert self.containsChunk(cx,cz), "Just created {0} but it didn't take".format((cx,cz))
            if i%100 == 0:
                info( u"Chunk {0}...".format( i ) )
        
        info( "Created {0} chunks.".format(len(ret)) )
        
        return ret;
        
    def createChunksInBox(self, box):
        info( u"Creating {0} chunks in {1}".format((box.maxcx-box.mincx)*( box.maxcz-box.mincz), ((box.mincx, box.mincz), (box.maxcx, box.maxcz))) )
        return self.createChunks(box.chunkPositions);
        
    def deleteChunk(self, cx, cz):
        
        if self._allChunks is not None: self._allChunks.discard( (cx,cz) )
        
        if (cx,cz) in self._loadedChunks: 
            del self._loadedChunks[(cx,cz)]
        
        if self.version:
            r = cx>>5,cz>>5
            rf = self.regionFiles.get(r)
            if rf:
                rf.setOffset(cx&0x1f , cz&0x1f, 0)
                if (rf.offsets == 0).all():
                    rf.close()
                    os.unlink(rf.path)
                    del self.regionFiles[r]
        else:
            os.unlink(self.chunkFilename(cx,cz))
            
        self._bounds = None
        
    def deleteChunksInBox(self, box):
        info( u"Deleting {0} chunks in {1}".format((box.maxcx-box.mincx)*( box.maxcz-box.mincz), ((box.mincx, box.mincz), (box.maxcx, box.maxcz))) )
        i=0;
        ret = [];
        for cx,cz in itertools.product(xrange(box.mincx,box.maxcx), xrange(box.mincz, box.maxcz)):
            i+=1;
            if self.containsChunk(cx,cz):
                self.deleteChunk(cx,cz);
                ret.append( (cx,cz) )
                
            assert not self.containsChunk(cx,cz), "Just deleted {0} but it didn't take".format((cx,cz))
            
            if i%100 == 0:
                info( u"Chunk {0}...".format( i ) )
        
        return ret
    
  
    spawnxyz = ["SpawnX", "SpawnY", "SpawnZ"]
        
    def playerSpawnPosition(self, player = None):
        """ 
        xxx if player is None then it gets the default spawn position for the world
        if player hasn't used a bed then it gets the default spawn position 
        """
        dataTag = self.root_tag["Data"]
        if player is None:
            playerSpawnTag = dataTag
        else:
            playerSpawnTag = self.getPlayerTag(player)
        
        return [playerSpawnTag.get(i, dataTag[i]).value for i in self.spawnxyz]
   
    def setPlayerSpawnPosition(self, pos, player = None):
        """ xxx if player is None then it sets the default spawn position for the world """
        if player is None:
            playerSpawnTag = self.root_tag["Data"]
        else:
            playerSpawnTag = self.getPlayerTag(player)
        for name, val in zip(self.spawnxyz, pos):
            playerSpawnTag[name] = nbt.TAG_Int(val);
    
            
    def getPlayerTag(self, player = "Player"):
        if player == "Player" and player in self.root_tag["Data"]:
            #single-player world
            return self.root_tag["Data"]["Player"];
            
        else:
            playerFilePath = os.path.join(self.worldDir, "players", player + ".dat")
            if os.path.exists(playerFilePath):
                #multiplayer world, found this player
                playerTag = self.playerTagCache.get(playerFilePath)
                if playerTag is None:
                    playerTag = nbt.loadFile(playerFilePath)
                    self.playerTagCache[playerFilePath] = playerTag
                return playerTag
                
            else:
                raise PlayerNotFound, "{0}".format(player)
                #return None
    
    def getPlayerDimension(self, player = "Player"):
        playerTag = self.getPlayerTag(player)
        if "Dimension" not in playerTag: return 0;
        return playerTag["Dimension"].value
    
    def setPlayerDimension(self, d, player = "Player"):
        playerTag = self.getPlayerTag(player)
        if "Dimension" not in playerTag: playerTag["Dimension"] = nbt.TAG_Int(0);
        playerTag["Dimension"].value = d;
        
        
    def setPlayerPosition(self, pos, player = "Player"):
        posList = nbt.TAG_List([nbt.TAG_Double(p) for p in pos]);
        playerTag = self.getPlayerTag(player)
        
        playerTag["Pos"] = posList
        
    def getPlayerPosition(self, player = "Player"):
        playerTag = self.getPlayerTag(player)
        posList = playerTag["Pos"];
        
        pos = map(lambda x:x.value, posList);
        return pos;
            
    def setPlayerOrientation(self, yp, player = "Player"):
        self.getPlayerTag(player)["Rotation"] = nbt.TAG_List([nbt.TAG_Float(p) for p in yp])
    
    def playerOrientation(self, player = "Player"):
        """ returns (yaw, pitch) """
        yp = map(lambda x:x.value, self.getPlayerTag(player)["Rotation"]);
        y,p = yp;
        if p==0: p=0.000000001;
        if p==180.0:  p-=0.000000001;
        yp = y,p;
        return array(yp);

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
            
class MCAlphaDimension (MCInfdevOldLevel):
    def loadLevelDat(self, create, random_seed, last_played):
        pass;
    def preloadDimensions(self):
        pass
        
    dimensionNames = { -1: "Nether" };
    @property
    def displayName(self):
        return u"{0} ({1})".format(self.parentWorld.displayName, self.dimensionNames[self.dimNo])
    
    def saveInPlace(self, saveSelf = False):
        """saving the dimension will save the parent world, which will save any
         other dimensions that need saving.  the intent is that all of them can
         stay loaded at once for fast switching """
         
        if saveSelf:
            MCInfdevOldLevel.saveInPlace(self);
        else:
            self.parentWorld.saveInPlace();

class ZipSchematic (MCInfdevOldLevel):
    def __init__(self, filename):
        tempdir = tempfile.mktemp("schematic")
        zf = ZipFile(filename)
        self.zipfile = zf
        zf.extract("level.dat", tempdir)
        
        MCInfdevOldLevel.__init__(self, tempdir)
        
        self.filename = filename
        
        try:
            schematicDat = os.path.join(tempdir, "schematic.dat")
            with closing(self.zipfile.open("schematic.dat")) as f:
                schematicDat = nbt.load(buf=gunzip(f.read()))
                
                self.Width = schematicDat['Width'].value;
                self.Height = schematicDat['Height'].value;
                self.Length = schematicDat['Length'].value;
        except Exception, e:
            print "Exception reading schematic.dat, skipping: {0!r}".format(e)
            self.Width = 0
            self.Height = 128
            self.Length = 0
            
    def __del__(self):
        self.zipfile.close()
        MCInfdevOldLevel.__del__(self)
        
    @classmethod
    def _isLevel(cls, filename):
        return is_zipfile(filename)
    
    def _loadChunk(self, chunk):
        if self.version:
            return MCInfdevOldLevel._loadChunk(self, chunk)
        else:
            cdata = self.zipfile.read(chunk.chunkFilename)
            chunk.compressedTag = cdata
            chunk.decompress()
        
    def _saveChunk(self, chunk):
        raise NotImplementedError, "Cannot save zipfiles yet!"
        
    def saveInPlace(self):
        raise NotImplementedError, "Cannot save zipfiles yet!"
    
    def containsChunk(self, cx, cz):
        return (cx,cz) in self.allChunks
    
    def preloadRegions(self):
        self.zipfile.extractall(self.worldDir)
        self.regionFiles = {}
        
        MCInfdevOldLevel.preloadRegions(self)
        
    def preloadChunkPaths(self):
        info( u"Scanning for chunks..." )
        self._allChunks = set()
        
        infos = self.zipfile.infolist()
        names = [i.filename.split('/') for i in infos]
        goodnames = [n for n in names if len(n) == 3 and n[0] in self.dirhashes and n[1] in self.dirhashes]
        
        for name in goodnames:
            c = name[2].split('.')
            if len(c) == 4 and c[0].lower() == 'c' and c[3].lower() == 'dat':
                try:
                    cx, cz = (self.decbase36(c[1]), self.decbase36(c[2]))
                except Exception, e:
                    info( 'Skipped file {0} ({1})'.format('.'.join(c), e) )
                    continue
                #self._loadedChunks[ (cx, cz) ] = InfdevChunk(self, (cx, cz));
                self._allChunks.add( (cx,cz) )
                
        info( u"Found {0} chunks.".format(len(self._allChunks)) )
        
        
    def preloadDimensions(self):
        pass
    
    def loadLevelDat(self, create, random_seed, last_played):
        if create:
            raise NotImplementedError, "Cannot save zipfiles yet!"
            
        with closing(self.zipfile.open("level.dat")) as f:
            with closing(gzip.GzipFile(fileobj=StringIO.StringIO(f.read()))) as g:
                self.root_tag = nbt.load(buf=g.read())
            
    def chunkFilename(self, x, z):
        s= "/".join((self.dirhash(x), self.dirhash(z),
                                     "c.%s.%s.dat" % (self.base36(x), self.base36(z))));
        return s;
        
class MCIndevLevel(MCLevel):
    
    """ IMPORTANT: self.Blocks and self.Data are indexed with [x,z,y] via axis 
    swapping to be consistent with infinite levels."""
    hasEntities = True
        
    def setPlayerSpawnPosition(self, pos, player = None):
        assert len(pos) == 3
        self.Spawn = array(pos);

    def playerSpawnPosition(self, player = None):
        return self.Spawn;
        
    def setPlayerPosition(self, pos, player = "Ignored"):
        for x in self.root_tag["Entities"]:
            if x["id"].value == "LocalPlayer":
                x["Pos"] = nbt.TAG_List([nbt.TAG_Float(p) for p in pos])
    
    def getPlayerPosition(self, player = "Ignored"):
        for x in self.root_tag["Entities"]:
            if x["id"].value == "LocalPlayer":
                return array(map(lambda x:x.value, x["Pos"]));
                
    def setPlayerOrientation(self, yp, player = "Ignored"):
        for x in self.root_tag["Entities"]:
            if x["id"].value == "LocalPlayer":
                x["Rotation"] = nbt.TAG_List([nbt.TAG_Float(p) for p in yp])

    def playerOrientation(self, player = "Ignored"):
        """ returns (yaw, pitch) """
        for x in self.root_tag["Entities"]:
            if x["id"].value == "LocalPlayer":
                return array(map(lambda x:x.value, x["Rotation"]));
    
    def setBlockDataAt(self, x,y,z, newdata):
        if x<0 or y<0 or z<0: return 0
        if x>=self.Width or y>=self.Height or z>=self.Length: return 0;
        self.Data[x,z,y] = (newdata & 0xf);        

    def blockDataAt(self, x, y, z):
        if x<0 or y<0 or z<0: return 0
        if x>=self.Width or y>=self.Height or z>=self.Length: return 0;
        return self.Data[x,z,y];
    
    def blockLightAt(self, x, y, z):
        if x<0 or y<0 or z<0: return 0
        if x>=self.Width or y>=self.Height or z>=self.Length: return 0;
        return self.BlockLight[x,z,y];
    
    def __repr__(self):
        return u"MCIndevLevel({0}): {1}W {2}L {3}H".format(self.filename, self.Width, self.Length, self.Height)
        
    @classmethod
    def _isTagLevel(cls, root_tag):
        return "MinecraftLevel" == root_tag.name
           
    def __init__(self, root_tag = None, filename = ""):
        self.Width = 0
        self.Height = 0
        self.Length = 0
        self.Blocks = array([], uint8)
        self.Data = array([], uint8)
        self.Spawn = (0,0,0)
        self.filename = filename;
        
        
        if root_tag:
        
            self.root_tag = root_tag;
            mapTag = root_tag[Map];
            self.Width = mapTag[Width].value
            self.Length = mapTag[Length].value
            self.Height = mapTag[Height].value
            
            mapTag[Blocks].value.shape = (self.Height, self.Length, self.Width)
            
            self.Blocks = swapaxes(mapTag[Blocks].value, 0, 2)
            
            mapTag[Data].value.shape = (self.Height, self.Length, self.Width)
            
            self.Data = swapaxes(mapTag[Data].value, 0, 2)
            

            
            self.BlockLight = self.Data & 0xf
            
            self.Data >>= 4
            
            self.Spawn = [mapTag[Spawn][i].value for i in range(3)];
            
            if not Entities in root_tag: 
                root_tag[Entities] = TAG_List();
            self.Entities = root_tag[Entities]

            if not TileEntities in root_tag: 
                root_tag[TileEntities] = TAG_List();
            self.TileEntities = root_tag[TileEntities]
            

            if len(filter(lambda x:x['id'].value=='LocalPlayer', root_tag[Entities])) == 0: #omen doesn't make a player entity
                p=TAG_Compound()
                p['id'] = TAG_String('LocalPlayer')
                p['Pos'] = TAG_List([TAG_Float(0.), TAG_Float(64.), TAG_Float(0.)])
                p['Rotation'] = TAG_List([TAG_Float(0.), TAG_Float(45.)])
                
                root_tag[Entities].append(p)
                #self.saveInPlace();
                
        else:
            info( u"Creating new Indev levels is not yet implemented.!" )
            raise ValueError, "Can't do that yet"
#            self.SurroundingGroundHeight = root_tag[Environment][SurroundingGroundHeight].value
#            self.SurroundingGroundType = root_tag[Environment][SurroundingGroundType].value
#            self.SurroundingWaterHeight = root_tag[Environment][SurroundingGroundHeight].value
#            self.SurroundingWaterType = root_tag[Environment][SurroundingWaterType].value
#            self.CloudHeight = root_tag[Environment][CloudHeight].value
#            self.CloudColor = root_tag[Environment][CloudColor].value
#            self.SkyColor = root_tag[Environment][SkyColor].value
#            self.FogColor = root_tag[Environment][FogColor].value
#            self.SkyBrightness = root_tag[Environment][SkyBrightness].value
#            self.TimeOfDay = root_tag[Environment]["TimeOfDay"].value
#
#              
#            self.Name = self.root_tag[About][Name].value
#            self.Author = self.root_tag[About][Author].value
#            self.CreatedOn = self.root_tag[About][CreatedOn].value

                    
    
    def rotateLeft(self):
        MCLevel.rotateLeft(self);
        
        self.Data = swapaxes(self.Data, 1, 0)[:,::-1,:]; #x=y; y=-x
        
        torchRotation = array([0, 4, 3, 1, 2, 5,
                               6, 7, 
                               
                               8, 9, 10, 11, 12, 13, 14, 15]);
                               
        torchIndexes = (self.Blocks == self.materials.Torch.ID)
        info( u"Rotating torches: {0}".format( len(torchIndexes.nonzero()[0]) ) )
        self.Data[torchIndexes] = torchRotation[self.Data[torchIndexes]]
        
        
    def saveToFile(self, filename = None):
        if filename == None: filename = self.filename;
        if filename == None:
            warn( u"Attempted to save an unnamed file in place" )
            return; #you fool!
        
        self.Data <<= 4;
        self.Data |= (self.BlockLight & 0xf)
        
        self.Blocks = swapaxes(self.Blocks, 0, 2)
        self.Data = swapaxes(self.Data, 0, 2)
            
        mapTag = nbt.TAG_Compound( name=Map );
        mapTag[Width] = nbt.TAG_Short(self.Width);
        mapTag[Height] = nbt.TAG_Short(self.Height);
        mapTag[Length] = nbt.TAG_Short(self.Length);
        mapTag[Blocks] = nbt.TAG_Byte_Array(self.Blocks);
        mapTag[Data]   = nbt.TAG_Byte_Array(self.Data);
        
        self.Blocks = swapaxes(self.Blocks, 0, 2)
        self.Data = swapaxes(self.Data, 0, 2)
        
        mapTag[Spawn]  = nbt.TAG_List([nbt.TAG_Short(i) for i in self.Spawn])

        self.root_tag[Map] = mapTag;
        self.root_tag[Map]
        #output_file = gzip.open(self.filename, "wb", compresslevel=1)
        try:
            os.rename(filename, filename + ".old");
        except Exception,e:
            pass
            
        try:
            self.root_tag.saveGzipped(filename);
        except:
            os.rename(filename + ".old", filename);
            
        try: os.remove(filename + ".old");
        except Exception,e:
            pass
        
        self.BlockLight = self.Data & 0xf
            
        self.Data >>= 4
              

import re

class MCSharpLevel(MCLevel):
    """ int magic = convert(data.readShort());
        logger.trace("Magic number: {}", magic);
        if (magic != 1874)
            throw new IOException("Only version 1 MCSharp levels supported (magic number was "+magic+")");

        int width = convert(data.readShort());
        int height = convert(data.readShort());
        int depth = convert(data.readShort());
        logger.trace("Width: {}", width);
        logger.trace("Depth: {}", depth);
        logger.trace("Height: {}", height);

        int spawnX = convert(data.readShort());
        int spawnY = convert(data.readShort());
        int spawnZ = convert(data.readShort());

        int spawnRotation = data.readUnsignedByte();
        int spawnPitch = data.readUnsignedByte();

        int visitRanks = data.readUnsignedByte();
        int buildRanks = data.readUnsignedByte();

        byte[][][] blocks = new byte[width][height][depth];
        int i = 0;
        BlockManager manager = BlockManager.getBlockManager();
        for(int z = 0;z<depth;z++) {
            for(int y = 0;y<height;y++) {
                byte[] row = new byte[height];
                data.readFully(row);
                for(int x = 0;x<width;x++) {
                    blocks[x][y][z] = translateBlock(row[x]);
                }
            }
        }

        lvl.setBlocks(blocks, new byte[width][height][depth], width, height, depth);
        lvl.setSpawnPosition(new Position(spawnX, spawnY, spawnZ));
        lvl.setSpawnRotation(new Rotation(spawnRotation, spawnPitch));
        lvl.setEnvironment(new Environment());

        return lvl;
    }"""
    
class MCJavaLevel(MCLevel):
    
    def setBlockDataAt(self, *args): pass
    def blockDataAt(self, *args): return 0;
    @property 
    def Height(self):
        return self.Blocks.shape[2];
    @property 
    def Length(self):
        return self.Blocks.shape[1];
    @property 
    def Width(self):
        return self.Blocks.shape[0];
    
    
    def guessSize(self, data):
        if(data.shape[0] <= (32 * 32 * 64)*2):
            warn( u"Can't guess the size of a {0} byte level".format(data.shape[0]) )
            raise IOError, "MCJavaLevel attempted for smaller than 64 blocks cubed"
        if(data.shape[0] > (32 * 32 * 64)*2):
            Width = 64
            Length = 64
            Height = 64
        if(data.shape[0] > (64 * 64 * 64)*2):
            Width = 128
            Length = 128
            Height = 64
        if(data.shape[0] > (128 * 128 * 64)*2):
            Width = 256
            Length = 256
            Height = 64
        if(data.shape[0] > (256 * 256 * 64)*2): #could also be 256*256*256
            Width = 512
            Length = 512
            Height = 64
        if(data.shape[0] > 512 * 512 * 64 * 2): # just to load shadowmarch castle
            Width = 512
            Length = 512
            Height = 256
        return (Width, Length, Height)
        
    @classmethod
    def _isDataLevel(cls, data):
        return (data[0] == 0x27 and
                data[1] == 0x1B and
                data[2] == 0xb7 and
                data[3] == 0x88)
            
    def __init__(self, filename, data):
        self.filename = filename;
        self.filedata = data;
        #try to take x,z,y from the filename
        r=re.search('(\d+).*?(\d+).*?(\d+)', os.path.basename(filename))
        if r and len(r.groups()) == 3:
            (w, l, h) = map(int, r.groups())
            if w*l*h > data.shape[0]:
                info( "Not enough blocks for size " + str( (w,l,h) ) )
                w,l,h = self.guessSize(data);
        else:
            w,l,h = self.guessSize(data);
            
        info( u"MCJavaLevel created for potential level of size " + str( (w,l,h) ) )
            
        blockCount = h*l*w
        if blockCount > data.shape[0]: 
            raise ValueError,  "Level file does not contain enough blocks! Try putting the size into the filename, e.g. server_level_{w}_{l}_{h}.dat".format(w=w,l=l,h=h);
        
        
        blockOffset = data.shape[0]-blockCount
        blocks = data[blockOffset:blockOffset+blockCount]
        
        maxBlockType = 64 #maximum allowed in classic
        while(max(blocks[-4096:]) > maxBlockType):
            #guess the block array by starting at the end of the file
            #and sliding the blockCount-sized window back until it
            #looks like every block has a valid blockNumber
            blockOffset -=1;
            blocks = data[blockOffset:blockOffset+blockCount]
        
            if blockOffset <= -data.shape[0]:
                raise IOError, "Can't find a valid array of blocks <= #%d" % maxBlockType
        
        self.Blocks = blocks;
        self.blockOffset = blockOffset;
        blocks.shape = (w,l,h);
        blocks.strides = (1, w, w*l);

            
    def saveInPlace(self):

        s = StringIO.StringIO()
        if self.compressed:
            g = gzip.GzipFile(fileobj=s, mode='wb');
        else:
            g = s;

        g.write(self.filedata.tostring());
        g.flush();
        g.close()

        try:
            os.rename(self.filename, self.filename + ".old");
        except Exception,e:
            pass;
        
        try:        
            with open(self.filename, 'wb') as f:
                f.write(s.getvalue());
        except Exception, e:
            info( u"Error while saving java level in place: {0}".format( e ) )
            try:os.remove(self.filename);
            except: pass
            os.rename(self.filename + ".old", self.filename);

        try:
            os.remove(self.filename + ".old");
        except Exception,e:
            pass;
            
###xxxxx CHECK RESULTS
def testJavaLevels():
    print "Java level"
    indevlevel = MCLevel.fromFile("hell.mclevel")
    
    creativelevel = MCLevel.fromFile("Dojo_64_64_128.dat");
    creativelevel.copyBlocksFrom(indevlevel, BoundingBox((0,0,0), (64,64,64,)), (0,0,0) )
    assert(all(indevlevel.Blocks[0:64,0:64,0:64] == creativelevel.Blocks[0:64,0:64,0:64])) 
    
    creativelevel.saveInPlace()
    #xxx old survival levels

def testIndevLevels():
    print "Indev level"
    
    srclevel = MCLevel.fromFile("hell.mclevel")
    indevlevel = MCLevel.fromFile("hueg.mclevel")
    indevlevel.copyBlocksFrom(srclevel, BoundingBox((0,0,0), (64,64,64,)), (0,0,0) ) 
    assert(all(indevlevel.Blocks[0:64,0:64,0:64] == srclevel.Blocks[0:64,0:64,0:64])) 
    indevlevel.fillBlocks(BoundingBox((0,0,0), (64,64,64,)), indevlevel.materials.Sand, [indevlevel.materials.Stone, indevlevel.materials.Dirt])
    indevlevel.saveInPlace()
    
def testAlphaLevels():
    print "Alpha level"
    indevlevel = MCLevel.fromFile("hell.mclevel")
    
    level = MCInfdevOldLevel(filename="d:\Testworld");
    for ch in list(level.allChunks): level.deleteChunk(*ch)
    level.createChunksInBox( BoundingBox((0,0,0), (32, 0, 32)) )
    level.copyBlocksFrom(indevlevel, BoundingBox((0,0,0), (256, 128, 256)), (-0, 0, 0)) 
    
    convertedSourceBlocks, convertedSourceData = indevlevel.convertBlocksFromLevel(level, indevlevel.Blocks[0:16,0:16,0:indevlevel.Height], indevlevel.Data[0:16,0:16,0:indevlevel.Height])
    assert all(level.getChunk(0,0).Blocks[0:16,0:16,0:indevlevel.Height] == convertedSourceBlocks)
    
    schem = MCLevel.fromFile("schematics\\CreativeInABox.schematic");
    level.copyBlocksFrom(schem, BoundingBox((0,0,0), (1,1,3)), (0, 64, 0));
    schem = MCSchematic( shape=(1,1,3) )
    schem.copyBlocksFrom(level, BoundingBox((0, 64, 0), (1, 1, 3)), (0,0,0));
    convertedSourceBlocks, convertedSourceData = schem.convertBlocksFromLevel(level, schem.Blocks, schem.Data)
    assert all(level.getChunk(0,0).Blocks[0:1,0:3,64:65] == convertedSourceBlocks)
    
    try:
        for x,z in itertools.product(xrange(-1,3),xrange(-1,2)):
            level.deleteChunk(x, z);
            level.createChunk(x, z)
    except Exception, e:
        traceback.print_exc();
        print e;
    level.fillBlocks( BoundingBox((-11, 0, -7), (38, 128, 25)) , indevlevel.materials.WoodPlanks);
    c = level.getChunk( 0, 0)
    assert all(c.Blocks == 5)
    level.fillBlocks( BoundingBox((-11, 0, -7), (38, 128, 25)) , indevlevel.materials.WoodPlanks, [indevlevel.materials.Dirt, indevlevel.materials.Grass]);
    #print b.shape
    #raise SystemExit
    cx, cz = -3,-1;
    
    try:
        level.deleteChunk(cx, cz);
    except KeyError:pass
    level.createChunk(cx, cz);
    level.copyBlocksFrom(indevlevel, BoundingBox((0,0,0), (64,64,64,)), (-96, 32, 0)) 
    #blocks = zeros((16,16,128), 'uint8');
    #blocks[:,:,:] = level.getChunk(cx, cz).Blocks[:,:,:]
    #level.getChunk(cx, cz).Blocks[:,:,:] = blocks[:,:,:]
    level.generateLights();
    level.saveInPlace();
    
    level.saveInPlace();
    
    
def testSchematics():
    print "Schematic from indev"
    
    size=(64,64,64)
    schematic = MCSchematic(shape=size, filename = "hell.schematic", mats='Classic');
    level = MCLevel.fromFile("hell.mclevel")
    schematic.rotateLeft();
    try:
        schematic.copyBlocksFrom(level, BoundingBox((-32,-32,-32), (64,64,64,)), (0,0,0) )
    except ValueError:
        pass;
    
    
    schematic.copyBlocksFrom(level, BoundingBox((0,0,0), (64,64,64,)), (0,0,0) )
    assert(all(schematic.Blocks[0:64,0:64,0:64] == level.Blocks[0:64,0:64,0:64])) 
    schematic.compress();
    
    schematic.copyBlocksFrom(level, BoundingBox((0,0,0), (64,64,64,)), (-32, -32, -32))
    assert(all(schematic.Blocks[0:32,0:32,0:32] == level.Blocks[32:64,32:64,32:64])) 
    
    schematic.compress();
    
    schematic.saveInPlace();
    
    schem = MCLevel.fromFile("schematics\CreativeInABox.schematic");
    tempSchematic = MCSchematic(shape=(1,1,3))
    tempSchematic.copyBlocksFrom(schem, BoundingBox((0,0,0), (1,1,3)), (0,0,0))
    
    print "Schematic from alpha"
    level = loadWorldNumber(1)
    for cx,cz in itertools.product(xrange(0, 4), xrange(0, 4) ):
        try:
            level.createChunk(cx,cz)
        except ValueError:
            pass
    schematic.copyBlocksFrom(level, BoundingBox((0,0,0), (64,64,64,)), (0,0,0) )

def testINVEditChests():
    print "INVEdit chest"
    invFile = MCLevel.fromFile("schematics/Chests/BuildersBox.inv");
    print "Blocks: ", invFile.Blocks                      
    print "Data: ", invFile.Data                      
    print "Entities: ", invFile.Entities                      
    print "TileEntities: ", invFile.TileEntities                      
    #raise SystemExit;
    
def testmain():
    testINVEditChests();
    testSchematics();
    testIndevLevels();
    testAlphaLevels();
    testJavaLevels();
    
#import cProfile   
if __name__=="__main__":
    #cProfile.run('testmain()');
    logging.basicConfig(format='%(levelname)s:%(message)s')
    logging.getLogger().level = logging.INFO
    
    testmain();
