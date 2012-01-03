try:
    import os
    try:
        import _nbt
        from _nbt import *
    except ImportError:
        print "Import error loading precompiled _nbt extension. Trying pyximport..."
        import numpy
        from pyximport import install; install(setup_args={'include_dirs':[numpy.get_include()]})
        import _nbt
        from _nbt import *
except ImportError, e:
    print "Import error loading _nbt extension", repr(e)
    import traceback; traceback.print_exc()
    from pynbt import *
    