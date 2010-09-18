import mclevel

class mce(object)
    usage = """
    Usage:
       mce <world> clone <sourcePoint> <sourceSize> <destPoint>
       mce <world> fill <blockType> <destPoint> <destSize>
       mce <world> replace <blockType> [with] <withBlockType> <destPoint> <destSize>
       
       mce <world> export <sourcePoint> <sourceSize>
       mce <world> import <filename> <destPoint>
       
       mce <world> player <point>
       mce <world> spawn <point>
       
       mce <world> createChunks <startChunk> <chunkSize>
       mce <world> deleteChunks <startChunk> <chunkSize>
       mce <world> prune <startChunk> <chunkSize>
       mce <world> relight <startChunk> <chunkSize>
       
        
       
    """
    
    def printUsage():
        print usage;
        
