from materials import alphaMaterials
from numpy import array

def RotateLeft(blocks, data):
    torchRotation = array([0, 4, 3, 1, 2, 5,
                           6, 7, 
                           
                           8, 9, 10, 11, 12, 13, 14, 15]);
                           
    torchIndexes = (blocks == alphaMaterials.materialNamed("Torch"))
    torchIndexes |= ( (blocks == alphaMaterials.materialNamed("Redstone Torch (on)")) | 
                      (blocks == alphaMaterials.materialNamed("Redstone Torch (off)")) )
                          
    print "Rotating torches: ", len(torchIndexes.nonzero()[0]);
    data[torchIndexes] = torchRotation[data[torchIndexes]]
    
    
    railRotation = array([1, 0, 4, 5, 3, 2, 9, 6, 
                           7, 8, 
                           
                           10, 11, 12, 13, 14, 15]);
                           
    railIndexes = (blocks == alphaMaterials.materialNamed("Rail"))
    print "Rotating rails: ", len(railIndexes.nonzero()[0]);
    data[railIndexes] = railRotation[data[railIndexes]]
        
    ladderRotation = array([0, 1, 4, 5, 3, 2, 
        
                           6, 7,  #xxx more ladders
                           8, 9, 10, 11, 12, 13, 14, 15]);
                           
    ladderIndexes = (blocks == alphaMaterials.materialNamed("Ladder"))
    print "Rotating ladders: ", len(ladderIndexes.nonzero()[0]);
    data[ladderIndexes] = ladderRotation[data[ladderIndexes]]
    
    signIndexes = (blocks == alphaMaterials.materialNamed("Sign"))
    print "Rotating signs: ", len(signIndexes.nonzero()[0]);
    data[signIndexes] -= 4
    data[signIndexes] &= 0xf
    
    wallSignRotation = array([0, 1, 4, 5, 3, 2, 6, 7, 
                              8, 9, 10, 11, 12, 13, 14, 15]);
    
    wallSignIndexes = (blocks == alphaMaterials.materialNamed("Wall Sign"))
    print "Rotating wallsigns: ", len(wallSignIndexes.nonzero()[0]);
    data[wallSignIndexes] = wallSignRotation[data[wallSignIndexes]]
        