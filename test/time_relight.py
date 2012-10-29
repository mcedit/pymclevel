import mclevel
from timeit import timeit

#import logging
#logging.basicConfig(level=logging.INFO)

path = "testfiles\\AnvilWorld"
world = mclevel.fromFile(path)

print "Relight: %d chunks in %.02f seconds" % (world.chunkCount, timeit(lambda: world.generateLights(world.allChunks), number=1))



