'''
from materials import classicMaterials, materials
'''
from numpy import *
NOTEX = (0xB0, 0x80)


class Block(object):
    def __init__(self, materials, blockID, blockData = 0, **kw):
        """
        Defines a blocktype.
        Keyword parameters:
            name: Human-readable name of the block
            brightness: 0-15 (default 0)
            opacity: 0-15 (default 15)
            aka: Additional keywords to use for searching
            color: (r, g, b) tuple. 0-255.  default (0x77, 0x77, 0x77)
            texture: pair of integers 0-255 with pixel coordinates into terrain.png
                can be a 6-let of pairs, one pair for each face, 
                with faces in the order -X +X -Y +Y -Z +Z
                
        """
        object.__init__(self)
        self.materials = materials
        self.name = kw.pop('name', materials.names[blockID][blockData])
         
             
        self.brightness  = kw.pop('brightness', materials.defaultBrightness)
        self.opacity = kw.pop('opacity', materials.defaultOpacity)
        self.aka = kw.pop('aka', "")
        
        self.color = kw.pop('color', materials.flatColors[blockID,blockData])
            
        self.ID = blockID
        self.blockData = blockData
        
    
    def __str__(self):
        return "<Block {name} ({id}:{data}) hasAlternate:{ha}>".format(
            name=self.name,id=self.ID,data=self.blockData,ha=self.hasAlternate)
    
    def __repr__(self):
        return str(self)  
    hasAlternate = False
    wildcard = False
    
    def anySubtype(self):
        bl = Block( self.materials, self.ID, self.blockData )
        bl.wildcard = True
        return bl
class MCMaterials(object):
    defaultBrightness = 0
    defaultOpacity = 15
    defaultTexture = NOTEX
    def __init__(self, defaultName = "Unused Block"):
        object.__init__(self)
        self.defaultName = defaultName
        
        self.blockTextures = zeros((256, 16, 6, 2), dtype='uint8')
        self.blockTextures[:] = self.defaultTexture
        self.names = [[defaultName] * 16 for i in range(256)]
        self.aka = [""] * 256
        self.allBlocks = []
        self.blocksByID = {}
        
        self.lightEmission = zeros(256, dtype='uint8')
        self.lightAbsorption = zeros(256, dtype='uint8')
        self.lightAbsorption[:] = self.defaultOpacity
        self.flatColors = zeros((256, 16, 4), dtype='uint8')
        self.flatColors[:] = (0xc9, 0x77, 0xf0, 0xff)
         
        #flat colors borrowed from c10t.  https://github.com/udoprog/c10t
        defaultColors = array([
            (255, 255, 255, 0), #Air
            (128, 128, 128, 255), #Stone
            (120, 172, 70, 255), #Grass
            (134, 96, 67, 255), #Dirt
            (100, 100, 100, 255), #Cobblestone
            (157, 128, 79, 255), #Wood Planks
            (120, 120, 120, 0), #Sapling
            (84, 84, 84, 255), #Bedrock
            (56, 68, 127, 64), #Water (active)
            (56, 68, 127, 64), #Water (still)
            (255, 90, 0, 255), #Lava (active)
            (255, 90, 0, 255), #Lava (still)
            (218, 210, 158, 255), #Sand
            (136, 126, 126, 255), #Gravel
            (143, 140, 125, 255), #Gold Ore
            (136, 130, 127, 255), #Iron Ore
            (115, 115, 115, 255), #Coal Ore
            (102, 81, 51, 255), #Wood
            (74, 131, 66, 128), #Leaves
            (195, 195, 50, 255), #Sponge
            (255, 255, 255, 48), #Glass
            (102, 112, 134, 255), #Lapis Lazuli Ore
            (29, 71, 165, 255), #Lapis Lazuli Block
            (107, 107, 107, 255), #Dispenser
            (218, 210, 158, 255), #Sandstone
            (100, 67, 50, 255), #Note Block
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (255, 255, 255, 255), #White Wool
            (0xc9, 0x77, 0xf0, 0xff), #Future Block!
            (127, 174, 125, 255), #Flower
            (17, 13, 26, 255), #Rose
            (255, 225, 96, 208), #Brown Mushroom
            (224, 174, 21, 255), #Red Mushroom
            (255, 255, 255, 0), #Block of Gold
            (191, 169, 116, 255), #Block of Iron
            (191, 135, 2, 255), #Double Stone Slab
            (111, 1, 1, 255), #Stone Slab
            (129, 140, 143, 255), #Brick
            (45, 166, 152, 255), #TNT
            (169, 107, 0, 255), #Bookshelf
            (144, 188, 39, 255), #Moss Stone
            (134, 96, 67, 255), #Obsidian
            (188, 188, 188, 255), #Torch
            (221, 221, 221, 255), #Fire
            (0, 0, 0, 0), #Monster Spawner
            (0, 0, 0, 0), #Wooden Stairs
            (255, 200, 140, 0), #Chest
            (120, 120, 120, 128), #Redstone Wire
            (120, 120, 120, 128), #Diamond Ore
            (0, 0, 0, 0), #Block of Diamond
            (0, 0, 0, 0), #Crafting Table
            (120, 120, 120, 255), #Crops
            (0, 0, 0, 0), #Farmland
            (0, 0, 0, 0), #Furnace
            (143, 125, 125, 255), #Lit Furnace
            (163, 145, 145, 255), #Sign
            (181, 140, 64, 32), #Wooden Door
            (255, 0, 0, 176), #Ladder
            (0, 0, 0, 0), #Rail
            (255, 255, 255, 255), #Stone Stairs
            (120, 120, 255, 120), #Wall Sign
            (255, 255, 255, 255), #Lever
            (85, 107, 47, 255), #Stone Floor Plate
            (144, 152, 168, 255), #Iron Door
            (193, 234, 150, 255), #Wood Floor Plate
            (125, 66, 44, 255), #Redstone Ore
            (88, 54, 22, 200), #Redstone Ore (glowing)
            (227, 144, 29, 255), #Redstone Torch (off)
            (194, 115, 115, 255), #Redstone Torch (on)
            (121, 97, 82, 255), #Button
            (255, 188, 94, 255), #Snow Layer
            (60, 13, 106, 127), #Ice
            (60, 13, 106, 127), #Snow
            (228, 205, 206, 255), #Cactus
            (50, 89, 45, 128), #Clay
            (94, 167, 84, 128), #Sugar Cane
            (201, 119, 240, 85), #Jukebox
            (201, 119, 240, 85), #Fence
            (204, 119, 24, 255), #Pumpkin
            (201, 119, 240, 85), #Netherrack
            (201, 119, 240, 85), #Soul Sand
            (255, 238, 0, 255), #Glowstone
            (201, 119, 240, 85), #Nether Portal
            (204, 119, 24, 255), #Jack-o'-Lantern
            (201, 119, 240, 85), #Cake
            (201, 119, 240, 85), #Redstone Repeater (Off)
            (201, 119, 240, 85), #Redstone Repeater (On)
        ])
        self.flatColors[:len(defaultColors),:,:] = array(defaultColors)[:,newaxis,:]
        
    def __repr__(self):
        return "<MCMaterials ({0})>".format(self.name)
        
    def blocksMatching(self, name):
        name = name.lower()
        return [v for v in self.allBlocks if name in v.name.lower() or name in v.aka.lower()]
    
    def blockWithID(self, id, data = 0):
        if (id,data) in self.blocksByID:
            return self.blocksByID[id,data]
        else:
            bl = Block(self, id, blockData=data)
            bl.hasAlternate = True
            return bl
            
    def Block(self, blockID, blockData = 0, **kw):
        block = Block(self, blockID, blockData, **kw)
        
        self.lightEmission[blockID] = block.brightness
        self.lightAbsorption[blockID] = block.opacity
        self.aka[blockID] = block.aka
        
        self.flatColors[blockID, (blockData or slice(None))] = block.color
            
        texture = kw.pop('texture', None)
        
        if texture:
            self.blockTextures[blockID,(blockData or slice(None))] = texture
        
        if blockData is 0:
            self.names[blockID] = [block.name] * 16
        else:
            self.names[blockID][blockData] = block.name
        
        if block.name is not self.defaultName:
            self.allBlocks.append(block)
            
        
        if (blockID, 0) in self.blocksByID:
            self.blocksByID[blockID, 0].hasAlternate = True
            block.hasAlternate = True
        
        self.blocksByID[blockID, blockData] = block
        
        return block 
        
    def __cmp__(self, rhs):
        return (self.ID, self.blockData).__cmp__( (rhs.ID, rhs.blockData) )
        

###
### MATERIALS for the latest version of the game ###
###

materials = MCMaterials(defaultName = "Future Block!");
materials.name = "Alpha"
am = materials
am.Air = am.Block(0, 
    name="Air",
    texture=(0x80,0xB0),
    opacity=0,
    )

am.Stone = am.Block(1, 
    name="Stone",
    texture=(0x10,0x00),
    )

am.Grass = am.Block(2, 
    name="Grass",
    texture=((0x30,0x00), (0x30,0x00), (0x00,0x00), (0x20,0x00), (0x30,0x00), (0x30,0x00)),
    )

am.Dirt = am.Block(3, 
    name="Dirt",
    texture=(0x20,0x00),
    )

am.Cobblestone = am.Block(4, 
    name="Cobblestone",
    texture=(0x00,0x10),
    )

am.WoodPlanks = am.Block(5, 
    name="Wood Planks",
    texture=(0x40,0x00),
    )

am.Sapling = am.Block(6, 
    name="Sapling",
    texture=(0xF0,0x00),
    opacity=0,
    )
    
am.SpruceSapling = am.Block(6, blockData=1,
    name="Spruce Sapling",
    texture=(0xF0,0x30),
    opacity=0,
    )

am.BirchSapling = am.Block(6, blockData=2,
    name="Birch Sapling",
    texture=(0xF0,0x40),
    opacity=0,
    )


am.Bedrock = am.Block(7, 
    name="Bedrock",
    aka="Adminium",
    texture=(0x10,0x10),
    )

am.WaterActive = am.Block(8, 
    name="Water (active)",
    texture=(0xF0,0xD0),
    opacity=3,
    )

am.WaterStill = am.Block(9, 
    name="Water (still)",
    texture=(0xF0,0xD0),
    opacity=3,
    )

am.LavaActive = am.Block(10, 
    name="Lava (active)",
    texture=(0xF0,0xF0),
    brightness=15,
    )

am.LavaStill = am.Block(11, 
    name="Lava (still)",
    texture=(0xF0,0xF0),
    brightness=15,
    )

am.Sand = am.Block(12, 
    name="Sand",
    texture=(0x20,0x10),
    )

am.Gravel = am.Block(13, 
    name="Gravel",
    texture=(0x30,0x10),
    )

am.GoldOre = am.Block(14, 
    name="Gold Ore",
    texture=(0x00,0x20),
    )

am.IronOre = am.Block(15, 
    name="Iron Ore",
    texture=(0x10,0x20),
    )

am.CoalOre = am.Block(16, 
    name="Coal Ore",
    texture=(0x20,0x20),
    )


am.Wood = am.Block(17, 
    name="Wood",
    texture=((0x40,0x10), (0x40,0x10), (0x50,0x10), (0x50,0x10), (0x40,0x10), (0x40,0x10)),
    )

am.Ironwood = am.Block(17, blockData=1, 
    name="Ironwood",
    aka="Redwood",
    texture=((0x40,0x70), (0x40,0x70), (0x50,0x10), (0x50,0x10), (0x40,0x70), (0x40,0x70)),
    )
    
am.BirchWood = am.Block(17, blockData=2, 
    name="Birch Wood",
    texture=((0x50,0x70), (0x50,0x70), (0x50,0x10), (0x50,0x10), (0x50,0x70), (0x50,0x70)),
    )


am.Leaves = am.Block(18, 
    name="Leaves",
    texture=(0x50,0x30),
    opacity=1,
    color=(99, 188, 76, 128),
    )

am.PineLeaves = am.Block(18, blockData=1, 
    name="Pine Leaves",
    texture=(0x50,0x80),
    opacity=1,
    color=(74, 131, 66, 128),
    )

am.BirchLeaves = am.Block(18, blockData=2, 
    name="Birch Leaves",
    texture=(0x50,0x30),
    opacity=1,
    color=(89, 151, 76, 128),
    )

am.LeavesDecaying = am.Block(18, blockData=0 | 4, 
    name="Leaves (Decaying)",
    texture=(0x50,0x30),
    opacity=1,
    )

am.PineLeavesDecaying = am.Block(18, blockData=1 | 4, 
    name="Pine Leaves (Decaying)",
    texture=(0x50,0x80),
    opacity=1,
    color=am.PineLeaves.color
    )

am.BirchLeavesDecaying = am.Block(18, blockData=2 | 4, 
    name="Birch Leaves (Decaying)",
    texture=(0x50,0x30),
    opacity=1,
    color=am.BirchLeaves.color
    )    

am.Sponge = am.Block(19, 
    name="Sponge",
    texture=(0x00,0x30),
    )

am.Glass = am.Block(20, 
    name="Glass",
    texture=(0x10,0x30),
    opacity=0,
    )

am.LapisLazuliOre = am.Block(21, 
    name="Lapis Lazuli Ore",
    texture=(0x00,0xA0),
    )

am.LapisLazuliBlock = am.Block(22, 
    name="Lapis Lazuli Block",
    texture=(0x00,0x90),
    )

am.Dispenser = am.Block(23, 
    name="Dispenser",
    texture=((0xE0,0x20), (0xE0,0x20), (0xE0,0x30), (0x10,0x00), (0xD0,0x20), (0xD0,0x20)),
    )

am.Sandstone = am.Block(24, 
    name="Sandstone",
    texture=((0x00,0xC0), (0x00,0xC0), (0x00,0xB0), (0x00,0xD0), (0x00,0xC0), (0x00,0xC0)),
    )

am.NoteBlock = am.Block(25, 
    name="Note Block",
    texture=(0xA0,0x40),
    )

am.Bed = am.Block(26, 
    name="Bed",
    texture=(0x60, 0x80),
    opacity=0,
    )

am.PoweredRail = am.Block(27, 
    name="Powered Rail",
    texture=(0x30, 0xA0),
    opacity=0,
    )
am.blockTextures[am.PoweredRail.ID][8:] = (0x30, 0xB0)

am.DetectorRail = am.Block(28, 
    name="Detector Rail",
    texture=(0x30, 0xC0),
    opacity=0,
    )

am.StickyPiston = am.Block(29, 
    name="Sticky Piston",
    texture=(0xA0, 0x60),
    opacity=15,
    )

am.Web = am.Block(30, 
    name="Web",
    texture=(0xB0, 0x00),
    opacity=0,
    )

am.UnusedShrub = am.Block(31, blockData = 0,
    name="[Unused Shrub]",
    texture=(0x80, 0x30),
    opacity=0,
    )

am.TallGrass = am.Block(31, blockData = 1,
    name="Tall Grass",
    texture=(0x70, 0x20),
    opacity=0,
    )

am.Shrub = am.Block(31, blockData = 2,
    name="Shrub",
    texture=(0x80, 0x30),
    opacity=0,
    )
    
am.DesertShrub2 = am.Block(32, 
    name="Dead Shrub",
    texture=(0x70, 0x30),
    opacity=0,
    )

am.Piston = am.Block(33, 
    name="Piston",
    texture=(0xB0, 0x60),
    opacity=15,
    )

am.PistonHead = am.Block(34, 
    name="Piston Head",
    texture=NOTEX,
    opacity=15,
    )
    
am.WhiteWool = am.Block(35, 
    name="White Wool",
    texture=(0x00, 0x40),
    color=(0xff, 0xff, 0xff, 0xff)
    )

am.OrangeWool = am.Block(35, blockData = 1,
    name="Orange Wool",
    texture=(0x20, 0xD0),
    color=(0xea, 0x7f, 0x37, 0xff)
    )

am.MagentaWool = am.Block(35,  blockData = 2,
    name="Magenta Wool",
    texture=(0x20, 0xC0),
    color=(0xbf, 0x4b, 0xc9, 0xff)
    )
      
am.LightBlueWool = am.Block(35,  blockData = 3,
    name="Light Blue Wool",
    texture=(0x20, 0xB0),
    color=(0x68, 0x8b, 0xd4, 0xff)
    )

am.YellowWool = am.Block(35,  blockData = 4,
    name="Yellow Wool",
    texture=(0x20, 0xA0),
    color=(0xc2, 0xb5, 0x1c, 0xff)
    )

am.LightGreenWool = am.Block(35,  blockData = 5,
    name="Light Green Wool",
    texture=(0x20, 0x90),
    color=(0x3b, 0xbd, 0x30, 0xff)
    )

am.PinkWool = am.Block(35,  blockData = 6,
    name="Pink Wool",
    texture=(0x20, 0x80),
    color=(0xd9, 0x83, 0x9b, 0xff)
    )

am.GrayWool = am.Block(35,  blockData = 7,
    name="Gray Wool",
    texture=(0x20, 0x70),
    color=(0x42, 0x42, 0x42, 0xff)
    )

am.LightGrayWool = am.Block(35,  blockData = 8,
    name="Light Gray Wool",
    texture=(0x10, 0xE0),
    color=(0x9e, 0xa6, 0xa6, 0xff)
    )

am.CyanWool = am.Block(35,  blockData = 9,
    name="Cyan Wool",
    texture=(0x10, 0xD0),
    color=(0x27, 0x75, 0x95, 0xff)
    )

am.PurpleWool = am.Block(35,  blockData = 10,
    name="Purple Wool",
    texture=(0x10, 0xC0),
    color=(0x81, 0x36, 0xc4, 0xff)
    )

am.BlueWool = am.Block(35,  blockData = 11,
    name="Blue Wool",
    texture=(0x10, 0xB0),
    color=(0x27, 0x33, 0xa1, 0xff)
    )

am.BrownWool = am.Block(35,  blockData = 12,
    name="Brown Wool",
    texture=(0x10, 0xA0),
    color=(0x56, 0x33, 0x1c, 0xff)
    )

am.DarkGreenWool = am.Block(35,  blockData = 13,
    name="Dark Green Wool",
    texture=(0x10, 0x90),
    color=(0x38, 0x4d, 0x18, 0xff)
    )

am.RedWool = am.Block(35,  blockData = 14,
    name="Red Wool",
    texture=(0x10, 0x80),
    color=(0xa4, 0x2d, 0x29, 0xff)
    )

am.BlackWool = am.Block(35,  blockData = 15,
    name="Black Wool",
    texture=(0x10, 0x70),
    color = (0, 0, 0, 0xff)
    )


am.Flower = am.Block(37, 
    name="Flower",
    texture=(0xD0,0x00),
    opacity=0,
    )

am.Rose = am.Block(38, 
    name="Rose",
    texture=(0xC0,0x00),
    opacity=0,
    )

am.BrownMushroom = am.Block(39, 
    name="Brown Mushroom",
    texture=(0xD0,0x10),
    opacity=0,
    brightness=1,
    )

am.RedMushroom = am.Block(40, 
    name="Red Mushroom",
    texture=(0xC0,0x10),
    opacity=0,
    )

am.BlockofGold = am.Block(41, 
    name="Block of Gold",
    texture=(0x70,0x10),
    )

am.BlockofIron = am.Block(42, 
    name="Block of Iron",
    texture=(0x60,0x10),
    )

am.DoubleStoneSlab = am.Block(43, 
    name="Double Stone Slab",
    texture=((0x50,0x00), (0x50,0x00), (0x60,0x00), (0x60,0x00), (0x50,0x00), (0x50,0x00)),
    )

am.DoubleSandstoneSlab = am.Block(43, blockData=1,
    name="Double Sandstone Slab",
    texture=((0x00,0xC0), (0x00,0xC0), (0x00,0xB0), (0x00,0xD0), (0x00,0xC0), (0x00,0xC0)),
    color=am.Sandstone.color,
    )

am.DoubleWoodenSlab = am.Block(43, blockData=2,
    name="Double Wooden Slab",
    texture=(0x40,0x00),
    color=am.WoodPlanks.color
    )
    
am.DoubleCobblestoneSlab = am.Block(43, blockData=3,
    name="Double Cobblestone Slab",
    texture=(0x00,0x10),
    )    

am.StoneSlab = am.Block(44, 
    name="Stone Slab",
    texture=((0x50,0x00), (0x50,0x00), (0x60,0x00), (0x60,0x00), (0x50,0x00), (0x50,0x00)),
    )

am.SandstoneSlab = am.Block(44, blockData=1,
    name="Sandstone Slab",
    texture=((0x00,0xC0), (0x00,0xC0), (0x00,0xB0), (0x00,0xD0), (0x00,0xC0), (0x00,0xC0)),
    color=am.Sandstone.color,
    )

am.WoodenSlab = am.Block(44, blockData=2,
    name="Wooden Slab",
    texture=(0x40,0x00),
    color=am.WoodPlanks.color
    )
    
am.CobblestoneSlab = am.Block(44, blockData=3,
    name="Cobblestone Slab",
    texture=(0x00,0x10),
    )    
    
    
am.Brick = am.Block(45, 
    name="Brick",
    texture=(0x70,0x00),
    )

am.TNT = am.Block(46, 
    name="TNT",
    texture=((0x80,0x00), (0x80,0x00), (0x90,0x00), (0xA0,0x00), (0x80,0x00), (0x80,0x00)),
    )

am.Bookshelf = am.Block(47, 
    name="Bookshelf",
    texture=((0x30,0x20), (0x30,0x20), (0x40,0x00), (0x40,0x00), (0x30,0x20), (0x30,0x20)),
    )

am.MossStone = am.Block(48, 
    name="Moss Stone",
    aka="Mossy Cobblestone",
    texture=(0x40,0x20),
    )

am.Obsidian = am.Block(49, 
    name="Obsidian",
    texture=(0x50,0x20),
    )

am.Torch = am.Block(50, 
    name="Torch",
    texture=(0x00,0x50),
    brightness=14,
    opacity=0,
    )

am.Fire = am.Block(51, 
    name="Fire",
    texture=(0xF0,0x10),
    brightness=15,
    )

am.MonsterSpawner = am.Block(52, 
    name="Monster Spawner",
    aka="Mob Cage",
    texture=(0x10,0x40),
    opacity=0,
    )

am.WoodenStairs = am.Block(53, 
    name="Wooden Stairs",
    texture=(0x40,0x00),
    opacity=0,
    )

am.Chest = am.Block(54, 
    name="Chest",
    texture=((0xA0,0x10), (0xA0,0x10), (0xA0,0x10), (0xB0,0x10), (0x90,0x10), (0x90,0x10)),
    )

am.RedstoneWire = am.Block(55, 
    name="Redstone Wire",
    texture=(0x40,0xA0), #note: as of 1.5 the texture is unsaturated like leaves
    opacity=0,
    )

am.DiamondOre = am.Block(56, 
    name="Diamond Ore",
    texture=(0x20,0x30),
    )

am.BlockofDiamond = am.Block(57, 
    name="Block of Diamond",
    texture=(0x80,0x10),
    )

am.CraftingTable = am.Block(58, 
    name="Crafting Table",
    aka="Workbench",
    texture=((0xB0,0x30), (0xB0,0x30), (0xB0,0x20), (0x40,0x10), (0xC0,0x30), (0xC0,0x30)),
    )

am.Crops = am.Block(59, 
    name="Crops",
    aka="Wheat",
    texture=(0xF0,0x50),
    opacity=0,
    )

am.Farmland = am.Block(60, 
    name="Farmland",
    aka="Soil",
    texture=(0x60,0x50),
    )

am.Furnace = am.Block(61, 
    name="Furnace",
    texture=((0xD0,0x20), (0xD0,0x20), (0x10,0x00), (0x10,0x00), (0xC0,0x20), (0xC0,0x20)),
    )

am.LitFurnace = am.Block(62, 
    name="Lit Furnace",
    texture=((0xD0,0x20), (0xD0,0x20), (0x10,0x00), (0x10,0x00), (0xD0,0x30), (0xD0,0x30)),
    brightness=14,
    )

am.Sign = am.Block(63, 
    name="Sign",
    texture=(0x80,0xB0),
    opacity=0,
    )

am.WoodenDoor = am.Block(64, 
    name="Wooden Door",
    texture=(0x10,0x50),
    opacity=0,
    )

am.Ladder = am.Block(65, 
    name="Ladder",
    texture=(0x30,0x50),
    opacity=0,
    )

am.Rail = am.Block(66, 
    name="Rail",
    aka="Minecart Track",
    texture=(0x00,0x80),
    opacity=0,
    )

am.StoneStairs = am.Block(67, 
    name="Stone Stairs",
    texture=(0x00,0x10),
    opacity=0,
    )

am.WallSign = am.Block(68, 
    name="Wall Sign",
    texture=(0x80,0xB0),
    opacity=0,
    )

am.Lever = am.Block(69, 
    name="Lever",
    aka="Switch",
    texture=(0x80,0xB0),
    opacity=0,
    )

am.StoneFloorPlate = am.Block(70, 
    name="Stone Floor Plate",
    texture=(0x80,0xB0),
    opacity=0,
    )

am.IronDoor = am.Block(71, 
    name="Iron Door",
    texture=(0x20,0x50),
    opacity=0,
    )

am.WoodFloorPlate = am.Block(72, 
    name="Wood Floor Plate",
    texture=(0x80,0xB0),
    opacity=0,
    )

am.RedstoneOre = am.Block(73, 
    name="Redstone Ore",
    texture=(0x30,0x30),
    )

am.RedstoneOreGlowing = am.Block(74, 
    name="Redstone Ore (glowing)",
    texture=(0x30,0x30),
    brightness=9,
    )

am.RedstoneTorchOff = am.Block(75, 
    name="Redstone Torch (off)",
    texture=(0x30,0x70),
    opacity=0,
    )

am.RedstoneTorchOn = am.Block(76, 
    name="Redstone Torch (on)",
    texture=(0x30,0x60),
    opacity=0,
    brightness=7,
    )

am.Button = am.Block(77, 
    name="Button",
    texture=(0x80,0xB0),
    opacity=0,
    )

am.SnowLayer = am.Block(78, 
    name="Snow Layer",
    texture=(0x20,0x40),
    opacity=0,
    )

am.Ice = am.Block(79, 
    name="Ice",
    texture=(0x30,0x40),
    opacity=3,
    )

am.Snow = am.Block(80, 
    name="Snow",
    texture=(0x20,0x40),
    )

am.Cactus = am.Block(81, 
    name="Cactus",
    texture=((0x60,0x40), (0x60,0x40), (0x70,0x40), (0x50,0x40), (0x60,0x40), (0x60,0x40)),
    )

am.Clay = am.Block(82, 
    name="Clay",
    texture=(0x80,0x40),
    )

am.SugarCane = am.Block(83, 
    name="Sugar Cane",
    aka="Reeds, Papyrus",
    texture=(0x90,0x40),
    opacity=0,
    )

am.Jukebox = am.Block(84, 
    name="Jukebox",
    texture=((0xA0,0x40), (0xA0,0x40), (0xA0,0x40), (0xB0,0x40), (0xA0,0x40), (0xA0,0x40)),
    )

am.Fence = am.Block(85, 
    name="Fence",
    texture=(0x80,0xB0),
    opacity=0,
    )

am.Pumpkin = am.Block(86, 
    name="Pumpkin",
    texture=((0x70,0x70), (0x60,0x70), (0x60,0x60), (0x60,0x70), (0x60,0x70), (0x60,0x70)),
    color=(0xcc, 0x77, 0x18, 0xFF)
    )

am.Netherrack = am.Block(87, 
    name="Netherrack",
    aka="Bloodstone",
    texture=(0x70,0x60),
    )

am.SoulSand = am.Block(88, 
    name="Soul Sand",
    aka="Slow Sand",
    texture=(0x80,0x60),
    )

am.Glowstone = am.Block(89, 
    name="Glowstone",
    texture=(0x90,0x60),
    brightness=15,
    color=(0xFF, 0xEE, 0x00, 0xFF)
    )

am.NetherPortal = am.Block(90, 
    name="Nether Portal",
    texture=(0x80,0xB0),
    opacity=0,
    brightness=11,
    )

am.JackOLantern = am.Block(91, 
    name="Jack-o'-Lantern",
    texture=((0x80,0x70), (0x60,0x70), (0x60,0x60), (0x60,0x70), (0x60,0x70), (0x60,0x70)),
    brightness=15,
    color=(0xcc, 0x77, 0x18, 0xFF)
    )

am.Cake = am.Block(92, 
    name="Cake",
    texture=((0xA0,0x70), (0xA0,0x70), (0x90,0x70), (0xC0,0x70), (0xA0,0x70), (0xA0,0x70)),
    opacity=0,
    )

am.RedstoneRepeaterOff = am.Block(93, 
    name="Redstone Repeater (Off)",
    texture=(0x30, 0x80),
    opacity=0,
    )

am.RedstoneRepeaterOn = am.Block(94, 
    name="Redstone Repeater (On)",
    texture=(0x30, 0x90),
    opacity=0,
    )

am.AprilFoolsChest = am.Block(95, 
    name="April Fools Chest",
    texture=((0xA0,0x10), (0xA0,0x10), (0xA0,0x10), (0xB0,0x10), (0x90,0x10), (0x90,0x10)),
    )
    
am.Trapdoor = am.Block(96, 
    name="Trapdoor",
    texture=(0x10,0x50),
    opacity=0,
    )
    
del am

from classicmaterials import classicMaterials

classicMaterials.lightAbsorption = materials.lightAbsorption

classicMaterials.lightEmission = materials.lightEmission


namedMaterials = dict( (i.name, i) for i in (materials, classicMaterials) )


materialNames = dict( (k,v) for v,k in namedMaterials.iteritems() )


#filters certain block types in old maps to types available in /game/
blockFilterClassicToAlpha = arange(256, dtype=uint8)

b = blockFilterClassicToAlpha
b[8]=9; #water to still water
b[10]=11; #lava to still lava
b[36]=35; # the new white cloth
b[52]=9; # infinite water source - now mob spawner
b[53]=11; # infinite lava source - now wooden stair
b[55]=35; # cog - 55 is now red wire
del b;

for i in range(21, 35): blockFilterClassicToAlpha[i] = 35; # recolor all cloth to white

blockFilterAlphaToClassic = arange(256, dtype=uint8)
blockFilterAlphaToClassic[50:255] = 36 # change all blocks from torch (50) on up to grey cloth


### xxx add filter tables for indev blocks

nullConversionTable = arange(256, dtype=uint8) 


materials.conversionTables = {
        materials:  nullConversionTable,
        classicMaterials: blockFilterAlphaToClassic,
    }

classicMaterials.conversionTables = {
        materials: blockFilterClassicToAlpha,
        classicMaterials: nullConversionTable,
        
    };


alphaMaterials = materials;
