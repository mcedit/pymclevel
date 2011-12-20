'''
Created on Jul 22, 2011

@author: Rio
'''
import os
import traceback
from datetime import datetime
from cStringIO import StringIO
from copy import deepcopy
import itertools
from contextlib import closing, contextmanager
import gzip

from numpy import *
import logging

import nbt
from nbt import *
from box import BoundingBox, FloatBox
from materials import *
import blockrotation
from entity import *

from faces import *
#String constants for common tag names

log = logging.getLogger(__name__)
warn, error, info, debug = log.warn, log.error, log.info, log.debug

Entities = "Entities"
TileEntities = "TileEntities"

Map = "Map"
Width = "Width"
Height = "Height"
Length = "Length"
Blocks = "Blocks"
Data = "Data"
Inventory = 'Inventory'


@contextmanager
def notclosing(f):
    yield f;
    
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


def exhaust(_iter):
    """Functions named ending in "Iter" return an iterable object that does
    long-running work and yields progress information on each call. exhaust()
    is used to implement the non-Iter equivalents"""
    i = None
    for i in _iter:
        pass
    return i


# we need to decode file paths from environment variables or else we get an error
# if they are formatted or joined to a unicode string
import sys

if sys.platform == "win32":
    #not sure why win32com is needed if the %APPDATA% var is available
    
    try:
        import win32com.client
        objShell = win32com.client.Dispatch("WScript.Shell")
        appDataDir = objShell.SpecialFolders("AppData")
    except Exception, e:
        print "Error while getting AppData folder using WScript.Shell.SpecialFolders: {0!r}".format(e)
        try:
            from win32com.shell import shell, shellcon
            appDataDir = shell.SHGetPathFromIDListEx (
                shell.SHGetSpecialFolderLocation (0, shellcon.CSIDL_APPDATA)
            )
        except Exception, e:
            print "Error while getting AppData folder using SHGetSpecialFolderLocation: {0!r}".format(e)
            
            appDataDir = os.environ['APPDATA'].decode(sys.getfilesystemencoding());
            
    minecraftDir = os.path.join(appDataDir, u".minecraft")

elif sys.platform == "darwin":
    appDataDir = os.path.expanduser(u"~/Library/Application Support")
    
    minecraftDir = os.path.join(appDataDir, u"minecraft")
    minecraftDir.decode(sys.getfilesystemencoding());
else:
    appDataDir = os.path.expanduser(u"~")
    minecraftDir = os.path.expanduser(u"~/.minecraft")
    

saveFileDir = os.path.join(minecraftDir, u"saves")

