'''
from materials import classicMaterials, materials
'''
from numpy import *
NOTEX = 0xB8

class Block(object):
    def __init__(self, materials, blockID, **kw):
        """
        Defines a blocktype.
        Keyword parameters:
            name: Human-readable name of the block
            brightness: 0-15 (default 0)
            opacity: 0-15 (default 15)
            aka: Additional keywords to use for searching
            color: (r, g, b) tuple. 0-255.  default (0x77, 0x77, 0x77)
        """
        object.__init__(self)
        self.materials = materials
        materials._objects[blockID] = self;
        materials.names[blockID] = kw.pop('name', materials.defaultName)
        materials.lightEmission[blockID] = kw.pop('brightness', materials.defaultBrightness)
        materials.lightAbsorption[blockID] = kw.pop('opacity', materials.defaultOpacity)
        materials.aka[blockID] = kw.pop('aka', "")
        color = kw.pop('color', None)
        if color:
            materials.flatColors[blockID] = color
            
        texture = kw.pop('texture')
        if isinstance(texture, int):
            texture = (texture, )*6
        
        
        materials.blockTextures[blockID] = texture
        
        self.ID = blockID
        
        
class MCMaterials(object):
    defaultBrightness = 0
    defaultOpacity = 15
    
    def __init__(self, defaultTexture, defaultName):
        object.__init__(self)
        self.defaultName = defaultName
        
        self._objects = [None] * 256;
        self.blockTextures = zeros((256, 6), dtype='uint8')
        self.blockTextures[:] = defaultTexture
        self.names = [defaultName] * 256
        self.aka = [""] * 256
        
        self.lightEmission = zeros(256, dtype='uint8')
        self.lightAbsorption = zeros(256, dtype='uint8')
        self.lightAbsorption[:] = self.defaultOpacity
        self.flatColors = zeros((256, 4), dtype='uint8')
        self.flatColors[:] = (0x77, 0x77, 0x77, 0x255)
         
        #flat colors borrowed from c10t.  https://github.com/udoprog/c10t
        defaultColors = array([
            (255,255,255,0),
            (128,128,128,255),
            (120,172,70,255),
            (134,96,67,255),
            (100,100,100,255),
            (157,128,79,255),
            (120,120,120,0),
            (84,84,84,255),
            (56,68,127,64),
            (56,68,127,64),
            (255,90,0,255),
            (255,90,0,255),
            (218,210,158,255),
            (136,126,126,255),
            (143,140,125,255),
            (136,130,127,255),
            (115,115,115,255),
            (102,81,51,255),
            (0x4a,0x83,0x42,0x80),
            (0xc3,0xc3,0x32,0xff),
            (255,255,255,48),
            (102,112,134,255),
            (29,71,165,255),
            (107,107,107,255),
            (218,210,158,255),
            (100,67,50,255),
            (255,255,0,255),
            (255,0,0,255),
            (0x00, 0x00, 0x00, 0x00),
            (0x00, 0x00, 0x00, 0x00),
            (0xff, 0xed, 0x8c, 0xff),
            (0xd9, 0xd9, 0xd9, 0xff),
            (200,200,200,255),
            (200,200,200,255),
            (0x56, 0x23, 0x17, 0xff),
            (0xff, 0x0, 0x0, 0xff),
            (0xbf, 0xa9, 0x74, 0xff),
            (0x7f, 0xae, 0x7d, 0xff),
            (0x11, 0x0d, 0x1a, 0xff),
            (0xff, 0xe1, 0x60,0xd0),
            (0xe0, 0xae, 0x15, 0xff),
            (0xff, 0xff, 0xff, 0x00),
            (0xbf, 0xa9, 0x74, 0xff),
            (0xbf, 0x87, 0x02, 0xff),
            (0x6f, 0x01, 0x01, 0xff),
            (129,140,143,255),
            (45,166,152,255),
            (0xa9, 0x6b, 0x00, 0xff),
            (0x90, 0xbc, 0x27, 0xff),
            (134,96,67,255),
            (0xbc, 0xbc, 0xbc, 0xff),
            (0xdd, 0xdd, 0xdd, 0xff),
            (0x0, 0x0, 0x0, 0x0),
            (0x0, 0x0, 0x0, 0x0),
            (0xff, 0xc8, 0x8c, 0),
            (120, 120, 120, 128),
            (120, 120, 120, 128),
            (0x0, 0x0, 0x0, 0x0),
            (0x0, 0x0, 0x0, 0x0),
            (120,120,120,255),
            (0x0, 0x0, 0x0, 0x0),
            (0x0, 0x0, 0x0, 0x0),
            (143,125,125,0xff),
            (163,145,145,0xff),
            (181,140,64,32),
            (255,0,0,0xb0),
            (0x0, 0x0, 0x0, 0x0),
            (255, 255, 255, 255),
            (120, 120, 255, 120),
            (255, 255, 255, 255),
            (85,107,47,255),
            (0x90, 0x98, 0xa8, 0xff),
            (193,234,150,255),
            (0x7d, 0x42, 0x2c, 0xff),
            (0x58, 0x36, 0x16, 200),
            (0xe3, 0x90, 0x1d, 0xff),
            (0xc2, 0x73, 0x73, 0xff),
            (0x79, 0x61, 0x52, 0xff),
            (0xff, 0xbc, 0x5e, 0xff),
            (0x3c, 0x0d, 0x6a, 0x7f),
            (0x3c, 0x0d, 0x6a, 0x7f),
            (228,205,206,255),
            (50,89,45,128),
            (94,167,84,128),
        ])
        self.flatColors[:len(defaultColors)] = defaultColors
        
    def __repr__(self):
        return "<MCMaterials ({0})>".format(self.name)
        
    def materialNamed(self, name):
        return self.names.index(name);
    
    def Block(self, blockID, **kw):
        return Block(self, blockID, **kw)

classicMaterials = MCMaterials(defaultTexture=NOTEX,
                               defaultName = "Not present in Classic");
classicMaterials.name = "Classic"
cm = classicMaterials
cm.Air = cm.Block(0, 
    name="Air",
    texture=0xB8,
    )
cm.Rock = cm.Block(1, 
    name="Rock",
    texture=0x01,
    )
cm.Grass = cm.Block(2, 
    name="Grass",
    texture=(0x03, 0x03, 0x00, 0x02, 0x03, 0x03),
    )
cm.Dirt = cm.Block(3, 
    name="Dirt",
    texture=0x02,
    )
cm.Cobblestone = cm.Block(4, 
    name="Cobblestone",
    texture=0x10,
    )
cm.WoodPlanks = cm.Block(5, 
    name="Wood Planks",
    texture=0x04,
    )
cm.Sapling = cm.Block(6, 
    name="Sapling",
    texture=0x0F,
    )
cm.Adminium = cm.Block(7, 
    name="Adminium",
    texture=0x11,
    )
cm.WaterActive = cm.Block(8, 
    name="Water (active)",
    texture=0x0E,
    )
cm.WaterStill = cm.Block(9, 
    name="Water (still)",
    texture=0x0E,
    )
cm.LavaActive = cm.Block(10, 
    name="Lava (active)",
    texture=0x1E,
    )
cm.LavaStill = cm.Block(11, 
    name="Lava (still)",
    texture=0x1E,
    )
cm.Sand = cm.Block(12, 
    name="Sand",
    texture=0x12,
    )
cm.Gravel = cm.Block(13, 
    name="Gravel",
    texture=0x13,
    )
cm.GoldOre = cm.Block(14, 
    name="Gold Ore",
    texture=0x20,
    )
cm.IronOre = cm.Block(15, 
    name="Iron Ore",
    texture=0x21,
    )
cm.CoalOre = cm.Block(16, 
    name="Coal Ore",
    texture=0x22,
    )
cm.Wood = cm.Block(17, 
    name="Wood",
    texture=(0x14, 0x14, 0x15, 0x15, 0x14, 0x14),
    )
cm.Leaves = cm.Block(18, 
    name="Leaves",
    texture=0x34,
    )
cm.Sponge = cm.Block(19, 
    name="Sponge",
    texture=0x30,
    )
cm.Glass = cm.Block(20, 
    name="Glass",
    texture=0x31,
    )
cm.RedCloth = cm.Block(21, 
    name="Red Cloth",
    texture=0x40,
    )
cm.OrangeCloth = cm.Block(22, 
    name="Orange Cloth",
    texture=0x41,
    )
cm.YellowCloth = cm.Block(23, 
    name="Yellow Cloth",
    texture=0x42,
    )
cm.LightGreenCloth = cm.Block(24, 
    name="Light Green Cloth",
    texture=0x43,
    )
cm.GreenCloth = cm.Block(25, 
    name="Green Cloth",
    texture=0x44,
    )
cm.AquaCloth = cm.Block(26, 
    name="Aqua Cloth",
    texture=0x45,
    )
cm.CyanCloth = cm.Block(27, 
    name="Cyan Cloth",
    texture=0x46,
    )
cm.BlueCloth = cm.Block(28, 
    name="Blue Cloth",
    texture=0x47,
    )
cm.PurpleCloth = cm.Block(29, 
    name="Purple Cloth",
    texture=0x48,
    )
cm.IndigoCloth = cm.Block(30, 
    name="Indigo Cloth",
    texture=0x49,
    )
cm.VioletCloth = cm.Block(31, 
    name="Violet Cloth",
    texture=0x4A,
    )
cm.MagentaCloth = cm.Block(32, 
    name="Magenta Cloth",
    texture=0x4B,
    )
cm.PinkCloth = cm.Block(33, 
    name="Pink Cloth",
    texture=0x4C,
    )
cm.BlackCloth = cm.Block(34, 
    name="Black Cloth",
    texture=0x4D,
    )
cm.GrayCloth = cm.Block(35, 
    name="Gray Cloth",
    texture=0x4E,
    )
cm.WhiteCloth = cm.Block(36, 
    name="White Cloth",
    texture=0x4F,
    )
cm.Flower = cm.Block(37, 
    name="Flower",
    texture=0x0D,
    )
cm.Rose = cm.Block(38, 
    name="Rose",
    texture=0x0C,
    )
cm.BrownMushroom = cm.Block(39, 
    name="Brown Mushroom",
    texture=0x1D,
    )
cm.RedMushroom = cm.Block(40, 
    name="Red Mushroom",
    texture=0x1C,
    )
cm.BlockOfGold = cm.Block(41, 
    name="Block of Gold",
    texture=(0x27, 0x27, 0x17, 0x37, 0x27, 0x27),
    )
cm.BlockOfIron = cm.Block(42, 
    name="Block of Iron",
    texture=(0x26, 0x26, 0x16, 0x36, 0x26, 0x26),
    )
cm.DoubleStoneSlab = cm.Block(43, 
    name="Double Stone Slab",
    texture=(0x05, 0x05, 0x06, 0x06, 0x05, 0x05),
    )
cm.SingleStoneSlab = cm.Block(44, 
    name="Stone Slab",
    texture=(0x05, 0x05, 0x06, 0x06, 0x05, 0x05),
    )
cm.Brick = cm.Block(45, 
    name="Brick",
    texture=0x07,
    )
cm.TNT = cm.Block(46, 
    name="TNT",
    texture=(0x08, 0x08, 0x09, 0x0A, 0x08, 0x08),
    )
cm.Bookshelf = cm.Block(47, 
    name="Bookshelf",
    texture=(0x23, 0x23, 0x04, 0x04, 0x23, 0x23),
    )
cm.MossStone = cm.Block(48, 
    name="Moss Stone",
    texture=0x24,
    )
cm.Obsidian = cm.Block(49, 
    name="Obsidian",
    texture=0x25,
    )
cm.Torch = cm.Block(50, 
    name="Torch",
    texture=0x50,
    )
cm.Fire = cm.Block(51, 
    name="Fire",
    texture=0x3F,
    )
cm.InfiniteWaterSource = cm.Block(52, 
    name="Infinite water source",
    texture=0x0E,
    )
cm.InfiniteLavaSource = cm.Block(53, 
    name="Infinite lava source",
    texture=0x1E,
    )
cm.Chest = cm.Block(54, 
    name="Chest",
    texture=(0x1A, 0x1A, 0x1A, 0x1B, 0x19, 0x19),
    )
cm.Cog = cm.Block(55, 
    name="Cog",
    texture=0x3F,
    )
cm.DiamondOre = cm.Block(56, 
    name="Diamond Ore",
    texture=0x32,
    )
cm.BlockOfDiamond = cm.Block(57, 
    name="Block Of Diamond",
    texture=(0x28, 0x28, 0x18, 0x38, 0x28, 0x28),
    )
cm.CraftingTable = cm.Block(58, 
    name="Crafting Table",
    texture=(0x3B, 0x3B, 0x2B, 0x14, 0x3C, 0x3C),
    )
cm.Crops = cm.Block(59, 
    name="Crops",
    texture=0x5F,
    )
cm.Farmland = cm.Block(60, 
    name="Farmland",
    texture=0x56,
    )
cm.Furnace = cm.Block(61, 
    name="Furnace",
    texture=(0x2D, 0x2D, 0x01, 0x01, 0x2C, 0x2C),
    )
cm.LitFurnace = cm.Block(62, 
    name="Lit Furnace",
    texture=(0x2D, 0x2D, 0x01, 0x01, 0x3D, 0x3D),
    )

###
### MATERIALS for the latest version of the game ###
###

materials = MCMaterials(defaultTexture = NOTEX,
                        defaultName = "Future Block!");
materials.name = "Alpha"
am = materials
am.Air = am.Block(0, 
    name="Air",
    texture=0xB8,
    opacity=0,
    )
am.Stone = am.Block(1, 
    name="Stone",
    texture=0x01,
    )
am.Grass = am.Block(2, 
    name="Grass",
    texture=(0x03, 0x03, 0x00, 0x02, 0x03, 0x03),
    )
am.Dirt = am.Block(3, 
    name="Dirt",
    texture=0x02,
    )
am.Cobblestone = am.Block(4, 
    name="Cobblestone",
    texture=0x10,
    )
am.WoodPlanks = am.Block(5, 
    name="Wood Planks",
    texture=0x04,
    )
am.Sapling = am.Block(6, 
    name="Sapling",
    texture=0x0F,
    opacity=0,
    )
am.Bedrock = am.Block(7, 
    name="Bedrock",
    texture=0x11,
    )
am.WaterActive = am.Block(8, 
    name="Water (active)",
    texture=0xDF,
    opacity=3,
    )
am.WaterStill = am.Block(9, 
    name="Water (still)",
    texture=0xDF,
    opacity=3,
    )
am.LavaActive = am.Block(10, 
    name="Lava (active)",
    texture=0xFF,
    brightness=15,
    )
am.LavaStill = am.Block(11, 
    name="Lava (still)",
    texture=0xFF,
    brightness=15,
    )
am.Sand = am.Block(12, 
    name="Sand",
    texture=0x12,
    )
am.Gravel = am.Block(13, 
    name="Gravel",
    texture=0x13,
    )
am.GoldOre = am.Block(14, 
    name="Gold Ore",
    texture=0x20,
    )
am.IronOre = am.Block(15, 
    name="Iron Ore",
    texture=0x21,
    )
am.CoalOre = am.Block(16, 
    name="Coal Ore",
    texture=0x22,
    )
am.Wood = am.Block(17, 
    name="Wood",
    texture=(0x14, 0x14, 0x15, 0x15, 0x14, 0x14),
    )
am.Leaves = am.Block(18, 
    name="Leaves",
    texture=0x35,
    opacity=1,
    )
am.Sponge = am.Block(19, 
    name="Sponge",
    texture=0x30,
    )
am.Glass = am.Block(20, 
    name="Glass",
    texture=0x31,
    opacity=0,
    )
am.LapisLazuliOre = am.Block(21, 
    name="Lapis Lazuli Ore",
    texture=0xA0,
    )
am.LapisLazuliBlock = am.Block(22, 
    name="Lapis Lazuli Block",
    texture=0x90,
    )
am.Dispenser = am.Block(23, 
    name="Dispenser",
    texture=(0x2E, 0x2E, 0x3E, 0x01, 0x2D, 0x2D),
    )
am.Sandstone = am.Block(24, 
    name="Sandstone",
    texture=(0xC0, 0xC0, 0xB0, 0xD0, 0xC0, 0xC0),
    )
am.NoteBlock = am.Block(25, 
    name="Note Block",
    texture=0x4A,
    )
am.Wool = am.Block(35, 
    name="Wool",
    texture=0x40,
    )
am.Flower = am.Block(37, 
    name="Flower",
    texture=0x0D,
    opacity=0,
    )
am.Rose = am.Block(38, 
    name="Rose",
    texture=0x0C,
    opacity=0,
    )
am.BrownMushroom = am.Block(39, 
    name="Brown Mushroom",
    texture=0x1D,
    opacity=0,
    brightness=1,
    )
am.RedMushroom = am.Block(40, 
    name="Red Mushroom",
    texture=0x1C,
    opacity=0,
    )
am.BlockofGold = am.Block(41, 
    name="Block of Gold",
    texture=0x17,
    )
am.BlockofIron = am.Block(42, 
    name="Block of Iron",
    texture=0x16,
    )
am.DoubleStoneSlab = am.Block(43, 
    name="Double Stone Slab",
    texture=(0x05, 0x05, 0x06, 0x06, 0x05, 0x05),
    )
am.StoneSlab = am.Block(44, 
    name="Stone Slab",
    texture=(0x05, 0x05, 0x06, 0x06, 0x05, 0x05),
    )
am.Brick = am.Block(45, 
    name="Brick",
    texture=0x07,
    )
am.TNT = am.Block(46, 
    name="TNT",
    texture=(0x08, 0x08, 0x09, 0x0A, 0x08, 0x08),
    )
am.Bookshelf = am.Block(47, 
    name="Bookshelf",
    texture=(0x23, 0x23, 0x04, 0x04, 0x23, 0x23),
    )
am.MossStone = am.Block(48, 
    name="Moss Stone",
    texture=0x24,
    )
am.Obsidian = am.Block(49, 
    name="Obsidian",
    texture=0x25,
    )
am.Torch = am.Block(50, 
    name="Torch",
    texture=0x50,
    brightness=14,
    opacity=0,
    )
am.Fire = am.Block(51, 
    name="Fire",
    texture=0x1F,
    brightness=15,
    )
am.MonsterSpawner = am.Block(52, 
    name="Monster Spawner",
    texture=0x41,
    opacity=0,
    )
am.WoodenStairs = am.Block(53, 
    name="Wooden Stairs",
    texture=0x04,
    opacity=0,
    )
am.Chest = am.Block(54, 
    name="Chest",
    texture=(0x1A, 0x1A, 0x1A, 0x1B, 0x19, 0x19),
    )
am.RedstoneWire = am.Block(55, 
    name="Redstone Wire",
    texture=0x64,
    opacity=0,
    )
am.DiamondOre = am.Block(56, 
    name="Diamond Ore",
    texture=0x32,
    )
am.BlockofDiamond = am.Block(57, 
    name="Block of Diamond",
    texture=0x18,
    )
am.CraftingTable = am.Block(58, 
    name="Crafting Table",
    texture=(0x3B, 0x3B, 0x2B, 0x14, 0x3C, 0x3C),
    )
am.Crops = am.Block(59, 
    name="Crops",
    texture=0x5F,
    opacity=0,
    )
am.Farmland = am.Block(60, 
    name="Farmland",
    texture=0x56,
    )
am.Furnace = am.Block(61, 
    name="Furnace",
    texture=(0x2D, 0x2D, 0x01, 0x01, 0x2C, 0x2C),
    )
am.LitFurnace = am.Block(62, 
    name="Lit Furnace",
    texture=(0x2D, 0x2D, 0x01, 0x01, 0x3D, 0x3D),
    brightness=14,
    )
am.Sign = am.Block(63, 
    name="Sign",
    texture=0xB8,
    opacity=0,
    )
am.WoodenDoor = am.Block(64, 
    name="Wooden Door",
    texture=0x51,
    opacity=0,
    )
am.Ladder = am.Block(65, 
    name="Ladder",
    texture=0x53,
    opacity=0,
    )
am.Rail = am.Block(66, 
    name="Rail",
    texture=0x80,
    opacity=0,
    )
am.StoneStairs = am.Block(67, 
    name="Stone Stairs",
    texture=0x10,
    opacity=0,
    )
am.WallSign = am.Block(68, 
    name="Wall Sign",
    texture=0xB8,
    opacity=0,
    )
am.Lever = am.Block(69, 
    name="Lever",
    texture=0xB8,
    opacity=0,
    )
am.StoneFloorPlate = am.Block(70, 
    name="Stone Floor Plate",
    texture=0xB8,
    opacity=0,
    )
am.IronDoor = am.Block(71, 
    name="Iron Door",
    texture=0x52,
    opacity=0,
    )
am.WoodFloorPlate = am.Block(72, 
    name="Wood Floor Plate",
    texture=0xB8,
    opacity=0,
    )
am.RedstoneOre = am.Block(73, 
    name="Redstone Ore",
    texture=0x33,
    )
am.RedstoneOreGlowing = am.Block(74, 
    name="Redstone Ore (glowing)",
    texture=0x33,
    brightness=9,
    )
am.RedstoneTorchOff = am.Block(75, 
    name="Redstone Torch (off)",
    texture=0x73,
    opacity=0,
    )
am.RedstoneTorchOn = am.Block(76, 
    name="Redstone Torch (on)",
    texture=0x63,
    opacity=0,
    brightness=7,
    )
am.Button = am.Block(77, 
    name="Button",
    texture=0xB8,
    opacity=0,
    )
am.SnowLayer = am.Block(78, 
    name="Snow Layer",
    texture=0x42,
    opacity=0,
    )
am.Ice = am.Block(79, 
    name="Ice",
    texture=0x43,
    opacity=3,
    )
am.Snow = am.Block(80, 
    name="Snow",
    texture=0x42,
    )
am.Cactus = am.Block(81, 
    name="Cactus",
    texture=(0x46, 0x46, 0x47, 0x45, 0x46, 0x46),
    )
am.Clay = am.Block(82, 
    name="Clay",
    texture=0x48,
    )
am.SugarCane = am.Block(83, 
    name="Sugar Cane",
    texture=0x49,
    opacity=0,
    )
am.Jukebox = am.Block(84, 
    name="Jukebox",
    texture=(0x4A, 0x4A, 0x4A, 0x4B, 0x4A, 0x4A),
    )
am.Fence = am.Block(85, 
    name="Fence",
    texture=0xB8,
    opacity=0,
    )
am.Pumpkin = am.Block(86, 
    name="Pumpkin",
    texture=(0x77, 0x76, 0x66, 0x76, 0x76, 0x76),
    )
am.Netherrack = am.Block(87, 
    name="Netherrack",
    texture=0x67,
    )
am.SoulSand = am.Block(88, 
    name="Soul Sand",
    texture=0x68,
    )
am.Glowstone = am.Block(89, 
    name="Glowstone",
    texture=0x69,
    brightness=15,
    )
am.NetherPortal = am.Block(90, 
    name="Nether Portal",
    texture=0xB8,
    opacity=0,
    brightness=11,
    )
am.JackOLantern = am.Block(91, 
    name="Jack-o'-Lantern",
    texture=(0x78, 0x76, 0x66, 0x76, 0x76, 0x76),
    brightness=15,
    )
am.Cake = am.Block(92, 
    name="Cake",
    texture=(0x7A, 0x7A, 0x79, 0x7C, 0x7A, 0x7A),
    )

del am

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

#precalculate coords
def texCoords(idx):
    
    return ( (idx & 0xf) << 4 , (idx & 0xf0) ) 

materials.blockTextures = array([map(texCoords, faces) for (faces) in materials.blockTextures], dtype='float32')
classicMaterials.blockTextures = array([map(texCoords, faces) for (faces) in classicMaterials.blockTextures], dtype='float32')

alphaMaterials = materials;
