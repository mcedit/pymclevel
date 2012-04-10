import logging
logger = logging.getLogger(__file__)

try:
    try:
        from _nbt import (
            load,
            gunzip,
            TAG_Byte,
            TAG_Byte_Array,
            TAG_Compound,
            TAG_Double,
            TAG_Float,
            TAG_Int,
            TAG_Int_Array,
            TAG_List,
            TAG_Long,
            TAG_Short,
            TAG_String
        )
        logger.info('Accelerated NBT module loaded.')
    except ImportError:
        import numpy
        from pyximport import install
        try:
            install(setup_args={
                'include_dirs': [
                    numpy.get_include()
                ]
            })
        except TypeError:
            logger.info(
                'The version of pyximport available does not support '
                '`include_dirs`, which is required.'
            )
        from _nbt import (
            load,
            gunzip,
            TAG_Byte,
            TAG_Byte_Array,
            TAG_Compound,
            TAG_Double,
            TAG_Float,
            TAG_Int,
            TAG_Int_Array,
            TAG_List,
            TAG_Long,
            TAG_Short,
            TAG_String
        )
except ImportError, e:
    logger.info('Accelerated NBT module unavailable, using native library.')
    from pynbt import (
        load,
        gunzip,
        TAG_Byte,
        TAG_Byte_Array,
        TAG_Compound,
        TAG_Double,
        TAG_Float,
        TAG_Int,
        TAG_Int_Array,
        TAG_List,
        TAG_Long,
        TAG_Short,
        TAG_String
    )
