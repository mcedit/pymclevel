from materials import MCMaterials

pocketMaterials = MCMaterials(defaultName = "Not present in Pocket Edition");
pocketMaterials.name = "Pocket"
pocketMaterials.terrainTexture = "terrain.png"
pm = pocketMaterials
pm.Air = pm.Block(0,
    name="Air",
    texture=(0x80, 0xB0),
    opacity=0,
    )

pm.Stone = pm.Block(1,
    name="Stone",
    texture=(0x10, 0x00),
    )

pm.Grass = pm.Block(2,
    name="Grass",
    texture=((0x30, 0x00), (0x30, 0x00), (0x00, 0x00), (0x20, 0x00), (0x30, 0x00), (0x30, 0x00)),
    )

pm.Dirt = pm.Block(3,
    name="Dirt",
    texture=(0x20, 0x00),
    )

pm.Cobblestone = pm.Block(4,
    name="Cobblestone",
    texture=(0x00, 0x10),
    )

pm.WoodPlanks = pm.Block(5,
    name="Wood Planks",
    texture=(0x40, 0x00),
    )

pm.Sapling = pm.Block(6,
    name="Sapling",
    texture=(0xF0, 0x00),
    opacity=0,
    )

pm.SpruceSapling = pm.Block(6, blockData=1,
    name="Spruce Sapling",
    texture=(0xF0, 0x30),
    opacity=0,
    )

pm.BirchSapling = pm.Block(6, blockData=2,
    name="Birch Sapling",
    texture=(0xF0, 0x40),
    opacity=0,
    )


pm.Bedrock = pm.Block(7,
    name="Bedrock",
    aka="Adminium",
    texture=(0x10, 0x10),
    )

pm.WaterActive = pm.Block(8,
    name="Water (active)",
    texture=(0xF0, 0xD0),
    opacity=3,
    )

pm.WaterStill = pm.Block(9,
    name="Water (still)",
    texture=(0xF0, 0xD0),
    opacity=3,
    )

pm.LavaActive = pm.Block(10,
    name="Lava (active)",
    texture=(0xF0, 0xF0),
    brightness=15,
    )

pm.LavaStill = pm.Block(11,
    name="Lava (still)",
    texture=(0xF0, 0xF0),
    brightness=15,
    )

pm.Sand = pm.Block(12,
    name="Sand",
    texture=(0x20, 0x10),
    )

pm.Gravel = pm.Block(13,
    name="Gravel",
    texture=(0x30, 0x10),
    )

pm.GoldOre = pm.Block(14,
    name="Gold Ore",
    texture=(0x00, 0x20),
    )

pm.IronOre = pm.Block(15,
    name="Iron Ore",
    texture=(0x10, 0x20),
    )

pm.CoalOre = pm.Block(16,
    name="Coal Ore",
    texture=(0x20, 0x20),
    )


pm.Wood = pm.Block(17,
    name="Wood",
    texture=((0x40, 0x10), (0x40, 0x10), (0x50, 0x10), (0x50, 0x10), (0x40, 0x10), (0x40, 0x10)),
    )

pm.Ironwood = pm.Block(17, blockData=1,
    name="Ironwood",
    aka="Redwood",
    texture=((0x40, 0x70), (0x40, 0x70), (0x50, 0x10), (0x50, 0x10), (0x40, 0x70), (0x40, 0x70)),
    )

pm.BirchWood = pm.Block(17, blockData=2,
    name="Birch Wood",
    texture=((0x50, 0x70), (0x50, 0x70), (0x50, 0x10), (0x50, 0x10), (0x50, 0x70), (0x50, 0x70)),
    )


pm.Leaves = pm.Block(18,
    name="Leaves",
    texture=(0x50, 0x30),
    opacity=1,
    color=(99, 188, 76, 128),
    )

pm.PineLeaves = pm.Block(18, blockData=1,
    name="Pine Leaves",
    texture=(0x50, 0x80),
    opacity=1,
    color=(74, 131, 66, 128),
    )

pm.BirchLeaves = pm.Block(18, blockData=2,
    name="Birch Leaves",
    texture=(0x50, 0x30),
    opacity=1,
    color=(89, 151, 76, 128),
    )


pm.LeavesDecaying = pm.Block(18, blockData=0 | 4,
    name="Leaves (Decaying)",
    texture=(0x50, 0x30),
    opacity=1,
    )

pm.PineLeavesDecaying = pm.Block(18, blockData=1 | 4,
    name="Pine Leaves (Decaying)",
    texture=(0x50, 0x80),
    opacity=1,
    )

pm.BirchLeavesDecaying = pm.Block(18, blockData=2 | 4,
    name="Birch Leaves (Decaying)",
    texture=(0x50, 0x30),
    opacity=1,
    )
#repeat flat colors for decaying and bit 0x8 varieties of leaves
pm.flatColors[18, 4:7] = pm.flatColors[18, 0:3]
pm.flatColors[18, 8:15] = pm.flatColors[18, 0:7]
pm.names[18][8:15] = pm.names[18][0:7]

pm.Sponge = pm.Block(19,
    name="Sponge",
    texture=(0x00, 0x30),
    )

pm.Glass = pm.Block(20,
    name="Glass",
    texture=(0x10, 0x30),
    opacity=0,
    )

pm.LapisLazuliOre = pm.Block(21,
    name="Lapis Lazuli Ore",
    texture=(0x00, 0xA0),
    )

pm.Sandstone = pm.Block(24,
    name="Sandstone",
    texture=((0x00, 0xC0), (0x00, 0xC0), (0x00, 0xB0), (0x00, 0xD0), (0x00, 0xC0), (0x00, 0xC0)),
    )

pm.BlackWoolAlternate = pm.Block(35,
    name="Black Wool (Alternate)",
    texture=(0x10, 0x70),
    color=(0, 0, 0, 0xff)
    )

pm.Flower = pm.Block(37,
    name="Flower",
    texture=(0xD0, 0x00),
    opacity=0,
    )

pm.Rose = pm.Block(38,
    name="Rose",
    texture=(0xC0, 0x00),
    opacity=0,
    )

pm.BrownMushroom = pm.Block(39,
    name="Brown Mushroom",
    texture=(0xD0, 0x10),
    opacity=0,
    brightness=1,
    )

pm.RedMushroom = pm.Block(40,
    name="Red Mushroom",
    texture=(0xC0, 0x10),
    opacity=0,
    )

pm.BlockofGold = pm.Block(41,
    name="Block of Gold",
    texture=(0x70, 0x10),
    )

pm.BlockofIron = pm.Block(42,
    name="Block of Iron",
    texture=(0x60, 0x10),
    )

pm.DoubleStoneSlab = pm.Block(43,
    name="Double Stone Slab",
    texture=((0x50, 0x00), (0x50, 0x00), (0x60, 0x00), (0x60, 0x00), (0x50, 0x00), (0x50, 0x00)),
    )

pm.DoubleSandstoneSlab = pm.Block(43, blockData=1,
    name="Double Sandstone Slab",
    texture=((0x00, 0xC0), (0x00, 0xC0), (0x00, 0xB0), (0x00, 0xD0), (0x00, 0xC0), (0x00, 0xC0)),
    color=pm.Sandstone.color,
    )

pm.DoubleWoodenSlab = pm.Block(43, blockData=2,
    name="Double Wooden Slab",
    texture=(0x40, 0x00),
    color=pm.WoodPlanks.color
    )

pm.DoubleCobblestoneSlab = pm.Block(43, blockData=3,
    name="Double Cobblestone Slab",
    texture=(0x00, 0x10),
    )

pm.DoubleBrickSlab = pm.Block(43, blockData=4,
    name="Double Brick Slab",
    texture=(0x70, 0x00),
    color=pm.WoodPlanks.color
    )

pm.DoubleStoneBrickSlab = pm.Block(43, blockData=5,
    name="Double Stone Brick Slab",
    texture=(0x60, 0x30),
    )

pm.StoneSlab = pm.Block(44,
    name="Stone Slab",
    texture=((0x50, 0x00), (0x50, 0x00), (0x60, 0x00), (0x60, 0x00), (0x50, 0x00), (0x50, 0x00)),
    )

pm.SandstoneSlab = pm.Block(44, blockData=1,
    name="Sandstone Slab",
    texture=((0x00, 0xC0), (0x00, 0xC0), (0x00, 0xB0), (0x00, 0xD0), (0x00, 0xC0), (0x00, 0xC0)),
    color=pm.Sandstone.color,
    )

pm.WoodenSlab = pm.Block(44, blockData=2,
    name="Wooden Slab",
    texture=(0x40, 0x00),
    color=pm.WoodPlanks.color
    )

pm.CobblestoneSlab = pm.Block(44, blockData=3,
    name="Cobblestone Slab",
    texture=(0x00, 0x10),
    )

pm.BrickSlab = pm.Block(44, blockData=4,
    name="Brick Slab",
    texture=(0x70, 0x00),
    )
pm.StoneBrickSlab = pm.Block(44, blockData=5,
    name="Stone Brick Slab",
    texture=(0x60, 0x30),
    )

pm.Brick = pm.Block(45,
    name="Brick",
    texture=(0x70, 0x00),
    )

pm.TNT = pm.Block(46,
    name="TNT",
    texture=((0x80, 0x00), (0x80, 0x00), (0x90, 0x00), (0xA0, 0x00), (0x80, 0x00), (0x80, 0x00)),
    )

pm.Obsidian = pm.Block(49,
    name="Obsidian",
    texture=(0x50, 0x20),
    )

pm.Torch = pm.Block(50,
    name="Torch",
    texture=(0x00, 0x50),
    brightness=14,
    opacity=0,
    )

pm.Fire = pm.Block(51,
    name="Fire",
    texture=(0xF0, 0x10),
    brightness=15,
    )

pm.WoodenStairs = pm.Block(53,
    name="Wooden Stairs",
    texture=(0x40, 0x00),
    )

pm.DiamondOre = pm.Block(56,
    name="Diamond Ore",
    texture=(0x20, 0x30),
    )

pm.BlockofDiamond = pm.Block(57,
    name="Block of Diamond",
    texture=(0x80, 0x10),
    )

pm.Farmland = pm.Block(60,
    name="Farmland",
    aka="Soil",
    texture=(0x60, 0x50),
    )

pm.WoodenDoor = pm.Block(64,
    name="Wooden Door",
    texture=(0x10, 0x50),
    opacity=0,
    )

pm.Ladder = pm.Block(65,
    name="Ladder",
    texture=(0x30, 0x50),
    opacity=0,
    )

pm.StoneStairs = pm.Block(67,
    name="Stone Stairs",
    texture=(0x00, 0x10),
    )

pm.IronDoor = pm.Block(71,
    name="Iron Door",
    texture=(0x20, 0x50),
    opacity=0,
    )

pm.RedstoneOre = pm.Block(73,
    name="Redstone Ore",
    texture=(0x30, 0x30),
    )

pm.RedstoneOreGlowing = pm.Block(74,
    name="Redstone Ore (glowing)",
    texture=(0x30, 0x30),
    brightness=9,
    )

pm.SnowLayer = pm.Block(78,
    name="Snow Layer",
    texture=(0x20, 0x40),
    opacity=0,
    )

pm.Ice = pm.Block(79,
    name="Ice",
    texture=(0x30, 0x40),
    opacity=3,
    )

pm.Clay = pm.Block(82,
    name="Clay",
    texture=(0x80, 0x40),
    )

pm.SugarCane = pm.Block(83,
    name="Sugar Cane",
    aka="Reeds, Papyrus",
    texture=(0x90, 0x40),
    opacity=0,
    )

pm.BlackWool = pm.Block(101,
    name="Black Wool",
    texture=(0x10, 0x70),
    color=(0, 0, 0, 0xff)
    )

pm.RedWool = pm.Block(102,
    name="Red Wool",
    texture=(0x10, 0x80),
    color=(0xa4, 0x2d, 0x29, 0xff)
    )

pm.DarkGreenWool = pm.Block(103,
    name="Dark Green Wool",
    texture=(0x10, 0x90),
    color=(0x38, 0x4d, 0x18, 0xff)
    )

pm.BrownWool = pm.Block(104,
    name="Brown Wool",
    texture=(0x10, 0xA0),
    color=(0x56, 0x33, 0x1c, 0xff)
    )


pm.BlueWool = pm.Block(105,
    name="Blue Wool",
    texture=(0x10, 0xB0),
    color=(0x27, 0x33, 0xa1, 0xff)
    )


pm.PurpleWool = pm.Block(106,
    name="Purple Wool",
    texture=(0x10, 0xC0),
    color=(0x81, 0x36, 0xc4, 0xff)
    )

pm.CyanWool = pm.Block(107,
    name="Cyan Wool",
    texture=(0x10, 0xD0),
    color=(0x27, 0x75, 0x95, 0xff)
    )

pm.LightGrayWool = pm.Block(108,
    name="Light Gray Wool",
    texture=(0x10, 0xE0),
    color=(0x9e, 0xa6, 0xa6, 0xff)
    )

pm.GrayWool = pm.Block(109,
    name="Gray Wool",
    texture=(0x20, 0x70),
    color=(0x42, 0x42, 0x42, 0xff)
    )

pm.PinkWool = pm.Block(110,
    name="Pink Wool",
    texture=(0x20, 0x80),
    color=(0xd9, 0x83, 0x9b, 0xff)
    )


pm.LightGreenWool = pm.Block(111,
    name="Light Green Wool",
    texture=(0x20, 0x90),
    color=(0x3b, 0xbd, 0x30, 0xff)
    )

pm.YellowWool = pm.Block(112,
    name="Yellow Wool",
    texture=(0x20, 0xA0),
    color=(0xc2, 0xb5, 0x1c, 0xff)
    )

pm.LightBlueWool = pm.Block(113,
    name="Light Blue Wool",
    texture=(0x20, 0xB0),
    color=(0x68, 0x8b, 0xd4, 0xff)
    )

pm.MagentaWool = pm.Block(114,
    name="Magenta Wool",
    texture=(0x20, 0xC0),
    color=(0xbf, 0x4b, 0xc9, 0xff)
    )

pm.OrangeWool = pm.Block(115,
    name="Orange Wool",
    texture=(0x20, 0xD0),
    color=(0xea, 0x7f, 0x37, 0xff)
    )

pm.AllStairs = [
    pm.WoodenStairs, 
    pm.StoneStairs, 
]

del pm

