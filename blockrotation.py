from materials import alphaMaterials
from numpy import array

def RotateLeft(blocks, data):
    
    # Torches
    torchRotation = array([0, 4, 3, 1, 2, 5,
                           6, 7, 
                           
                           8, 9, 10, 11, 12, 13, 14, 15]);
                           
    torchIndexes = (blocks == alphaMaterials.materialNamed("Torch"))
    torchIndexes |= ( (blocks == alphaMaterials.materialNamed("Redstone Torch (on)")) | 
                      (blocks == alphaMaterials.materialNamed("Redstone Torch (off)")) )
                          
    print "Rotating torches: ", len(torchIndexes.nonzero()[0]);
    data[torchIndexes] = torchRotation[data[torchIndexes]]
    
    
    # Rails
    railRotation = array([1, 0, 4, 5, 3, 2, 9, 6, 
                           7, 8, 
                           
                           10, 11, 12, 13, 14, 15]);
                           
    railIndexes = (blocks == alphaMaterials.materialNamed("Rail"))
    print "Rotating rails: ", len(railIndexes.nonzero()[0]);
    data[railIndexes] = railRotation[data[railIndexes]]
      
      
    # Ladders
    ladderRotation = array([0, 1, 4, 5, 3, 2, 
        
                           6, 7,  #xxx more ladders
                           8, 9, 10, 11, 12, 13, 14, 15]);
                           
    ladderIndexes = (blocks == alphaMaterials.materialNamed("Ladder"))
    print "Rotating ladders: ", len(ladderIndexes.nonzero()[0]);
    data[ladderIndexes] = ladderRotation[data[ladderIndexes]]
    
    
    # Standing signs
    signIndexes = (blocks == alphaMaterials.materialNamed("Sign"))
    print "Rotating signs: ", len(signIndexes.nonzero()[0]);
    data[signIndexes] -= 4
    data[signIndexes] &= 0xf
    
    
    # Wall signs
    wallSignRotation = array([0, 1, 4, 5, 3, 2, 6, 7, 
                              8, 9, 10, 11, 12, 13, 14, 15]);
    
    wallSignIndexes = (blocks == alphaMaterials.materialNamed("Wall Sign"))
    print "Rotating wallsigns: ", len(wallSignIndexes.nonzero()[0]);
    data[wallSignIndexes] = wallSignRotation[data[wallSignIndexes]]
    
    
    # Levers
    leverRotation = array([0, 4, 3, 1, 2, 6, 5, 7,                         
                           8, 12, 11, 9, 10, 14, 13, 15]) #thrown levers
                           
    leverIndexes = (blocks == alphaMaterials.materialNamed("Lever"))
    print "Rotating levers: ", len(leverIndexes.nonzero()[0]);
    data[leverIndexes] = leverRotation[data[leverIndexes]]
    
    
    # Doors
    doorRotation = array([3, 0, 1, 2, 
                          7, 4, 5, 6, #swung door
                          11, 8, 9, 10, #top half
                          15, 12, 13, 14]) #top half swung
                           
    doorIndexes = (blocks == alphaMaterials.materialNamed("Iron Door") ) | (blocks == alphaMaterials.materialNamed("Wooden Door"))
    print "Rotating doors: ", len(doorIndexes.nonzero()[0]);
    data[doorIndexes] = doorRotation[data[doorIndexes]]
    
    
    # Buttons
    buttonRotation = array([0, 4, 3, 1, 2, 5, 6, 7,                         
                            8, 12, 11, 9, 10, 13, 14, 15]) #pressed buttons, unusual
                           
    buttonIndexes = (blocks == alphaMaterials.materialNamed("Stone Button"))
    print "Rotating buttons: ", len(buttonIndexes.nonzero()[0]);
    data[buttonIndexes] = buttonRotation[data[buttonIndexes]]
    
    
    # Stairs
    stairRotation = array([3, 2, 0, 1, 4, 5, 6, 7,                         
                           8, 9, 10, 11, 12, 13, 14, 15])
                           
    stairIndexes = (blocks == alphaMaterials.materialNamed("Wooden Stair")) | (blocks == alphaMaterials.materialNamed("Stone Stair"))
    print "Rotating stairs: ", len(stairIndexes.nonzero()[0]);
    data[stairIndexes] = stairRotation[data[stairIndexes]]
    
    
    
    
    
    
        