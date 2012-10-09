import os
from os.path import join
import shutil
import tempfile
import mclevel

__author__ = 'Rio'

def mktemp(suffix):
    td = tempfile.mkdtemp(suffix)
    os.rmdir(td)
    return td


class TempLevel(object):
    def __init__(self, filename, createFunc=None):
        if not os.path.exists(filename):
            filename = join("testfiles", filename)
        tmpname = mktemp(os.path.basename(filename))
        if os.path.exists(filename):
            if os.path.isdir(filename):
                shutil.copytree(filename, tmpname)
            else:
                shutil.copy(filename, tmpname)
        else:
            createFunc(tmpname)
        self.tmpname = tmpname
        self.level = mclevel.fromFile(tmpname)

    def __del__(self):
        self.level.close()
        del self.level
        filename = self.tmpname

        if os.path.isdir(filename):
            shutil.rmtree(filename)
        else:
            os.unlink(filename)
