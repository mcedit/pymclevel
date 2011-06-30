from materials import alphaMaterials
from numpy import array, arange, zeros

def genericRotation(cls):
    rotation = arange(16, dtype='uint8')
    rotation[cls.North] = cls.West
    rotation[cls.West] = cls.South
    rotation[cls.South] = cls.East
    rotation[cls.East] = cls.North
    return rotation

def genericEastWestFlip(cls):
    rotation = arange(16, dtype='uint8')
    rotation[cls.West] = cls.East
    rotation[cls.East] = cls.West
    return rotation

def genericNorthSouthFlip(cls):
    rotation = arange(16, dtype='uint8')
    rotation[cls.South] = cls.North
    rotation[cls.North] = cls.South
    return rotation

rotationClasses = [];

def genericFlipRotation(cls):
    cls.rotateLeft = genericRotation(cls)
    cls.flipEastWest = genericEastWestFlip(cls)
    cls.flipNorthSouth = genericNorthSouthFlip(cls)
    rotationClasses.append(cls)

class Torch:
    blocktypes = [
        alphaMaterials.Torch.ID,
        alphaMaterials.RedstoneTorchOn.ID,
        alphaMaterials.RedstoneTorchOff.ID,
    ]
                          
    South = 1
    North = 2
    West = 3
    East = 4

genericFlipRotation(Torch)

class Ladder:
    blocktypes = [alphaMaterials.Ladder.ID]
    
    East = 2
    West = 3
    North = 4
    South = 5
genericFlipRotation(Ladder)

class Stair:
    blocktypes = [
        alphaMaterials.WoodenStairs.ID,
        alphaMaterials.StoneStairs.ID,
    ]
    
    South = 0
    North = 1
    West = 2
    East = 3
genericFlipRotation(Stair)

class WallSign:
    blocktypes = [alphaMaterials.WallSign.ID]
    
    East = 2
    West = 3
    North = 4
    South = 5
genericFlipRotation(WallSign)
   
class Furnace:
    blocktypes = [
        alphaMaterials.Furnace.ID,
        alphaMaterials.LitFurnace.ID,
    ]
    East = 2
    West = 3
    North = 4
    South = 5
genericFlipRotation(Furnace)

class Dispenser(Furnace):
    blocktypes = [
        alphaMaterials.Dispenser.ID,
    ]          
genericFlipRotation(Dispenser)
    
class Pumpkin:
    blocktypes = [
        alphaMaterials.Pumpkin.ID,
        alphaMaterials.JackOLantern.ID,
    ]
    
    East = 0
    South = 1
    West = 2
    North = 3
genericFlipRotation(Pumpkin)

class Rail:
    blocktypes = [alphaMaterials.Rail.ID]
    
    EastWest = 0
    NorthSouth = 1
    South = 2
    North = 3
    East = 4
    West = 5
    
    Northeast = 6
    Southeast = 7
    Southwest = 8
    Northwest = 9
Rail.rotateLeft = genericRotation(Rail)
Rail.rotateLeft[Rail.Northeast] = Rail.Northwest
Rail.rotateLeft[Rail.Southeast] = Rail.Northeast
Rail.rotateLeft[Rail.Southwest] = Rail.Southeast
Rail.rotateLeft[Rail.Northwest] = Rail.Southwest

Rail.rotateLeft[Rail.NorthSouth] = Rail.EastWest
Rail.rotateLeft[Rail.EastWest] = Rail.NorthSouth

Rail.flipEastWest = genericEastWestFlip(Rail)
Rail.flipEastWest[Rail.Northeast] = Rail.Northwest
Rail.flipEastWest[Rail.Northwest] = Rail.Northeast
Rail.flipEastWest[Rail.Southwest] = Rail.Southeast
Rail.flipEastWest[Rail.Southeast] = Rail.Southwest

Rail.flipNorthSouth = genericNorthSouthFlip(Rail)
Rail.flipNorthSouth[Rail.Northeast] = Rail.Southeast
Rail.flipNorthSouth[Rail.Southeast] = Rail.Northeast
Rail.flipNorthSouth[Rail.Southwest] = Rail.Northwest
Rail.flipNorthSouth[Rail.Northwest] = Rail.Southwest
rotationClasses.append(Rail)

def applyBit8(array):
    array[8:16] = array[0:8] | 0x8
def applyBit4(array):
    array[4:8] = array[0:4] | 0x4
    array[12:16] = array[8:12] | 0x4
 
applyThrownBit = applyBit8

class PoweredDetectorRail(Rail):
    blocktypes = [alphaMaterials.PoweredRail.ID, alphaMaterials.DetectorRail.ID]
PoweredDetectorRail.rotateLeft = genericRotation(PoweredDetectorRail)

PoweredDetectorRail.rotateLeft[PoweredDetectorRail.NorthSouth] = PoweredDetectorRail.EastWest
PoweredDetectorRail.rotateLeft[PoweredDetectorRail.EastWest] = PoweredDetectorRail.NorthSouth


PoweredDetectorRail.flipEastWest = genericEastWestFlip(PoweredDetectorRail)
PoweredDetectorRail.flipNorthSouth = genericNorthSouthFlip(PoweredDetectorRail)
applyThrownBit(PoweredDetectorRail.rotateLeft)
applyThrownBit(PoweredDetectorRail.flipEastWest)
applyThrownBit(PoweredDetectorRail.flipNorthSouth)
rotationClasses.append(PoweredDetectorRail)

   
class Lever:
    blocktypes = [alphaMaterials.Lever.ID]
    ThrownBit = 0x8
    South = 1
    North = 2
    West = 3
    East = 4
    EastWest = 5
    NorthSouth = 6
Lever.rotateLeft = genericRotation(Lever)
Lever.rotateLeft[Lever.NorthSouth] = Lever.EastWest
Lever.rotateLeft[Lever.EastWest] = Lever.NorthSouth
Lever.flipEastWest = genericEastWestFlip(Lever)
Lever.flipNorthSouth = genericNorthSouthFlip(Lever)
applyThrownBit(Lever.rotateLeft)
applyThrownBit(Lever.flipEastWest)
applyThrownBit(Lever.flipNorthSouth)
rotationClasses.append(Lever)

class Button:
    blocktypes = [alphaMaterials.Button.ID]
    PressedBit = 0x8
    South = 1
    North = 2
    West = 3
    East = 4
Button.rotateLeft = genericRotation(Button)
Button.flipEastWest = genericEastWestFlip(Button)
Button.flipNorthSouth = genericNorthSouthFlip(Button)
applyThrownBit(Button.rotateLeft)
applyThrownBit(Button.flipEastWest)
applyThrownBit(Button.flipNorthSouth)
rotationClasses.append(Button)

class SignPost:
    blocktypes = [alphaMaterials.Sign.ID]
    #west is 0, increasing clockwise
    
    rotateLeft = arange(16, dtype='uint8')
    rotateLeft -= 4
    rotateLeft &= 0xf
    
    flipEastWest = arange(16, dtype='uint8')
    flipNorthSouth = arange(16, dtype='uint8')
    pass

rotationClasses.append(SignPost)

class Door:
    blocktypes = [
        alphaMaterials.IronDoor.ID,
        alphaMaterials.WoodenDoor.ID,
    ]
    TopHalfBit = 0x8
    SwungCCWBit = 0x4
    
    Northeast = 0
    Southeast = 1
    Southwest = 2
    Northwest = 3
    
    rotateLeft = arange(16, dtype='uint8')
    
Door.rotateLeft[Door.Northeast] = Door.Northwest
Door.rotateLeft[Door.Southeast] = Door.Northeast
Door.rotateLeft[Door.Southwest] = Door.Southeast
Door.rotateLeft[Door.Northwest] = Door.Southwest

Door.rotateLeft[4:8] = Door.rotateLeft[0:4] | 0x4
Door.rotateLeft[8:16] = Door.rotateLeft[0:8] | 0x8

#when flipping horizontally, swing the doors so they at least look the same

Door.flipEastWest = arange(16, dtype='uint8')
Door.flipEastWest[Door.Northeast] = Door.Northwest
Door.flipEastWest[Door.Northwest] = Door.Northeast
Door.flipEastWest[Door.Southwest] = Door.Southeast
Door.flipEastWest[Door.Southeast] = Door.Southwest
Door.flipEastWest[4:8] = Door.flipEastWest[0:4]
Door.flipEastWest[0:4] = Door.flipEastWest[4:8] | 0x4
Door.flipEastWest[8:16] = Door.flipEastWest[0:8] | 0x8

Door.flipNorthSouth = arange(16, dtype='uint8')
Door.flipNorthSouth[Door.Northeast] = Door.Southeast
Door.flipNorthSouth[Door.Northwest] = Door.Southwest
Door.flipNorthSouth[Door.Southwest] = Door.Northwest
Door.flipNorthSouth[Door.Southeast] = Door.Northeast
Door.flipNorthSouth[4:8] = Door.flipNorthSouth[0:4]
Door.flipNorthSouth[0:4] = Door.flipNorthSouth[4:8] | 0x4
Door.flipNorthSouth[8:16] = Door.flipNorthSouth[0:8] | 0x8

rotationClasses.append(Door)


class RedstoneRepeater:
    blocktypes = [
        alphaMaterials.RedstoneRepeaterOff.ID,
        alphaMaterials.RedstoneRepeaterOn.ID,
        
    ]
    
    East = 0
    South = 1
    West = 2
    North = 3
    
genericFlipRotation(RedstoneRepeater)

#high bits of the repeater indicate repeater delay, and should be preserved
RedstoneRepeater.rotateLeft[4:8] = RedstoneRepeater.rotateLeft[0:4] | 0x4
RedstoneRepeater.rotateLeft[8:16] = RedstoneRepeater.rotateLeft[0:8] | 0x8

RedstoneRepeater.flipEastWest[4:8] = RedstoneRepeater.flipEastWest[0:4] | 0x4
RedstoneRepeater.flipEastWest[8:16] = RedstoneRepeater.flipEastWest[0:8] | 0x8

RedstoneRepeater.flipNorthSouth[4:8] = RedstoneRepeater.flipNorthSouth[0:4] | 0x4
RedstoneRepeater.flipNorthSouth[8:16] = RedstoneRepeater.flipNorthSouth[0:8] | 0x8


applyOpenedBit = applyBit4

class Trapdoor:
    blocktypes = [alphaMaterials.Trapdoor.ID]
    
    West = 0
    East = 1
    South = 2
    North = 3

genericFlipRotation(Trapdoor)
applyOpenedBit(Trapdoor.rotateLeft)
applyOpenedBit(Trapdoor.flipEastWest)
applyOpenedBit(Trapdoor.flipNorthSouth)

applyPistonBit = applyBit8
class PistonBody:
    blocktypes = [alphaMaterials.StickyPiston.ID, alphaMaterials.Piston.ID]
    
    East = 2
    West = 3
    North = 4
    South = 5
genericFlipRotation(PistonBody)
applyPistonBit(PistonBody.rotateLeft)
applyPistonBit(PistonBody.flipEastWest)
applyPistonBit(PistonBody.flipNorthSouth)
    
class PistonHead(PistonBody):
    blocktypes = [alphaMaterials.PistonHead.ID]
rotationClasses.append(PistonHead)    
    
def masterRotationTable(rotationFunc):
    # compute a 256x16 table mapping each possible blocktype/data combination to 
    # the resulting data when the block is rotated
    table = zeros( (256, 16), dtype='uint8')
    table[:] = arange(16, dtype='uint8')
    for cls in rotationClasses:
        for blocktype in cls.blocktypes:
            table[blocktype] = rotationFunc(cls)
            
    return table 
    
class BlockRotation:
    rotateLeft = masterRotationTable(lambda cls:cls.rotateLeft);
    flipEastWest = masterRotationTable(lambda cls:cls.flipEastWest);
    flipNorthSouth = masterRotationTable(lambda cls:cls.flipNorthSouth);
    
       
    
def FlipNorthSouth(blocks, data):
    data[:] = BlockRotation.flipNorthSouth[blocks, data]
    
def FlipEastWest(blocks, data):
    data[:] = BlockRotation.flipEastWest[blocks, data]

    
def RotateLeft(blocks, data):
    data[:] = BlockRotation.rotateLeft[blocks, data]


