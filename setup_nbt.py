    
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("_nbt", ["_nbt.pyx"])]
import numpy

setup(
  name = 'NBT library (Cython implementation)',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules,
  include_dirs = numpy.get_include()
)
