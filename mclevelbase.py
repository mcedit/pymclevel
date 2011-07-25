'''
Created on Jul 22, 2011

@author: Rio
'''
import os
import traceback
from datetime import datetime
from StringIO import StringIO
from copy import deepcopy
import itertools
from contextlib import closing
import gzip

from numpy import *
from logging import warn, error, info, debug

import nbt
from nbt import *
from box import BoundingBox
from materials import *
import blockrotation
from entity import *


FaceXIncreasing = 0
FaceXDecreasing = 1
FaceYIncreasing = 2
FaceYDecreasing = 3
FaceZIncreasing = 4
FaceZDecreasing = 5
MaxDirections = 6
#String constants for common tag names

Entities = "Entities"
TileEntities = "TileEntities"

Map = "Map"
Width = "Width"
Height = "Height"
Length = "Length"
Blocks = "Blocks"
Data = "Data"
Inventory = 'Inventory'

#entities

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

class PlayerNotFound(Exception): pass
class ChunkNotPresent(Exception): pass
class RegionMalformed(Exception): pass
class ChunkMalformed(ChunkNotPresent): pass

from level import MCLevel
