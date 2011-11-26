try:
    import os
    os.environ['DISTUTILS_USE_SDK'] = "1"
    from pyximport import install; install()
    from _nbt import *
except ImportError, e:
    print "Import error loading _nbt extension", repr(e)
    import traceback; traceback.print_exc()
    from pynbt import *
    