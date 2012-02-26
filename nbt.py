try:
    import os
    try:
        import _nbt
        from _nbt import *
        print "Accelerated NBT module loaded."
    except ImportError:
        print "Import error loading precompiled _nbt extension. Trying pyximport..."
        import numpy
        from pyximport import install
        install(setup_args={'include_dirs': [numpy.get_include()]})
        import _nbt
        from _nbt import *
        print "Accelerated NBT module loaded via pyximport."
except ImportError, e:
    print "Exception: ", repr(e)
    print """Import error loading _nbt extension. NBT acceleration will not be available.

To take advantage of the accelerated NBT module, install both Cython and your system development tools. Use this
command to install Cython:

    easy_install cython
"""
    import sys
    if sys.platform == "darwin":
        print """You must also install the Xcode development tools, available from the Apple Developer Connection at connect.apple.com"""
    elif sys.platform == "win32":
        print """You must also install either Visual Studio 2010 or the Windows Platform SDK 7.0 from MSDN somewhere on microsoft.com"""
    else:
        print """You must also install your system's development tools. On Debian and Ubuntu, this command should work:

    sudo apt-get install gcc
"""
    print
    from pynbt import *
    print "Pure-python NBT module loaded."
