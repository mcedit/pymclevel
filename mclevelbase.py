'''
Created on Jul 22, 2011

@author: Rio
'''

from contextlib import contextmanager
from logging import getLogger
import os

log = getLogger(__name__)
warn, error, info, debug = log.warn, log.error, log.info, log.debug

@contextmanager
def notclosing(f):
    yield f


class PlayerNotFound(Exception):
    pass


class ChunkNotPresent(Exception):
    pass


class RegionMalformed(Exception):
    pass


class ChunkMalformed(ChunkNotPresent):
    pass


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
    # try to use win32 api to get the AppData folder since python doesn't populate os.environ with unicode strings.

    try:
        import win32com.client
        objShell = win32com.client.Dispatch("WScript.Shell")
        appDataDir = objShell.SpecialFolders("AppData")
    except Exception, e:
        print "Error while getting AppData folder using WScript.Shell.SpecialFolders: {0!r}".format(e)
        try:
            from win32com.shell import shell, shellcon
            appDataDir = shell.SHGetPathFromIDListEx(
                shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_APPDATA)
            )
        except Exception, e:
            print "Error while getting AppData folder using SHGetSpecialFolderLocation: {0!r}".format(e)

            appDataDir = os.environ['APPDATA'].decode(sys.getfilesystemencoding())

    minecraftDir = os.path.join(appDataDir, u".minecraft")

elif sys.platform == "darwin":
    appDataDir = os.path.expanduser(u"~/Library/Application Support")

    minecraftDir = os.path.join(appDataDir, u"minecraft")
    minecraftDir.decode(sys.getfilesystemencoding())
else:
    appDataDir = os.path.expanduser(u"~")
    minecraftDir = os.path.expanduser(u"~/.minecraft")


saveFileDir = os.path.join(minecraftDir, u"saves")


if sys.platform == "win32":
    appSupportDir = os.path.join(appDataDir, u"pymclevel")
elif sys.platform == "darwin":
    appSupportDir = os.path.expanduser(u"~/Library/Application Support/pymclevel/")
else:
    appSupportDir = os.path.expanduser(u"~/.pymclevel")
