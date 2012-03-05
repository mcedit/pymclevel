import logging
logger = logging.getLogger(__file__)


try:
    try:
        from _nbt import load, gunzip, TAG_Byte, TAG_Byte_Array, TAG_Compound, TAG_Double, TAG_Float, TAG_Int, TAG_Int_Array, TAG_List, TAG_Long, TAG_Short, TAG_String
        logger.info("Accelerated NBT module loaded.")
    except ImportError:
        logger.info("Import error loading precompiled _nbt extension. Trying pyximport...")
        import numpy
        from pyximport import install
        install(setup_args={'include_dirs': [numpy.get_include()]})
        from _nbt import load, gunzip, TAG_Byte, TAG_Byte_Array, TAG_Compound, TAG_Double, TAG_Float, TAG_Int, TAG_Int_Array, TAG_List, TAG_Long, TAG_Short, TAG_String
        logger.info("Accelerated NBT module loaded via pyximport.")
except ImportError, e:
    logger.info("Exception: ", repr(e))
    logger.info("""Import error loading _nbt extension. NBT acceleration will not be available.

To take advantage of the accelerated NBT module, install both Cython and your system development tools. Use this
command to install Cython:

    easy_install cython
""")
    import sys
    if sys.platform == "darwin":
        logger.info("""You must also install the Xcode development tools, available from the Apple Developer Connection at connect.apple.com""")
    elif sys.platform == "win32":
        logger.info("""You must also install either Visual Studio 2010 or the Windows Platform SDK 7.0 from MSDN somewhere on microsoft.com""")
    else:
        logger.info("""You must also install your system's development tools. On Debian and Ubuntu, this command should work:

    sudo apt-get install gcc
""")
    from pynbt import load, gunzip, TAG_Byte, TAG_Byte_Array, TAG_Compound, TAG_Double, TAG_Float, TAG_Int, TAG_Int_Array, TAG_List, TAG_Long, TAG_Short, TAG_String
    logger.info("Pure-python NBT module loaded.")
