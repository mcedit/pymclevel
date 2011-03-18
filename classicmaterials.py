from materials import MCMaterials

classicMaterials = MCMaterials(defaultName = "Not present in Classic");
classicMaterials.name = "Classic"
cm = classicMaterials
cm.Air = cm.Block(0, 
    name="Air",
    texture=(0x80,0xB0),
    )

cm.Rock = cm.Block(1, 
    name="Rock",
    texture=(0x10,0x00),
    )

cm.Grass = cm.Block(2, 
    name="Grass",
    texture=((0x30,0x00), (0x30,0x00), (0x00,0x00), (0x20,0x00), (0x30,0x00), (0x30,0x00)),
    )

cm.Dirt = cm.Block(3, 
    name="Dirt",
    texture=(0x20,0x00),
    )

cm.Cobblestone = cm.Block(4, 
    name="Cobblestone",
    texture=(0x00,0x10),
    )

cm.WoodPlanks = cm.Block(5, 
    name="Wood Planks",
    texture=(0x40,0x00),
    )

cm.Sapling = cm.Block(6, 
    name="Sapling",
    texture=(0xF0,0x00),
    )

cm.Adminium = cm.Block(7, 
    name="Adminium",
    texture=(0x10,0x10),
    )

cm.WaterActive = cm.Block(8, 
    name="Water (active)",
    texture=(0xE0,0x00),
    )

cm.WaterStill = cm.Block(9, 
    name="Water (still)",
    texture=(0xE0,0x00),
    )

cm.LavaActive = cm.Block(10, 
    name="Lava (active)",
    texture=(0xE0,0x10),
    )

cm.LavaStill = cm.Block(11, 
    name="Lava (still)",
    texture=(0xE0,0x10),
    )

cm.Sand = cm.Block(12, 
    name="Sand",
    texture=(0x20,0x10),
    )

cm.Gravel = cm.Block(13, 
    name="Gravel",
    texture=(0x30,0x10),
    )

cm.GoldOre = cm.Block(14, 
    name="Gold Ore",
    texture=(0x00,0x20),
    )

cm.IronOre = cm.Block(15, 
    name="Iron Ore",
    texture=(0x10,0x20),
    )

cm.CoalOre = cm.Block(16, 
    name="Coal Ore",
    texture=(0x20,0x20),
    )

cm.Wood = cm.Block(17, 
    name="Wood",
    texture=((0x40,0x10), (0x40,0x10), (0x50,0x10), (0x50,0x10), (0x40,0x10), (0x40,0x10)),
    )

cm.Leaves = cm.Block(18, 
    name="Leaves",
    texture=(0x50,0x30),
    )

cm.Sponge = cm.Block(19, 
    name="Sponge",
    texture=(0x00,0x30),
    )

cm.Glass = cm.Block(20, 
    name="Glass",
    texture=(0x10,0x30),
    )

cm.RedCloth = cm.Block(21, 
    name="Red Cloth",
    texture=(0x00,0x40),
    )

cm.OrangeCloth = cm.Block(22, 
    name="Orange Cloth",
    texture=(0x10,0x40),
    )

cm.YellowCloth = cm.Block(23, 
    name="Yellow Cloth",
    texture=(0x20,0x40),
    )

cm.LightGreenCloth = cm.Block(24, 
    name="Light Green Cloth",
    texture=(0x30,0x40),
    )

cm.GreenCloth = cm.Block(25, 
    name="Green Cloth",
    texture=(0x40,0x40),
    )

cm.AquaCloth = cm.Block(26, 
    name="Aqua Cloth",
    texture=(0x50,0x40),
    )

cm.CyanCloth = cm.Block(27, 
    name="Cyan Cloth",
    texture=(0x60,0x40),
    )

cm.BlueCloth = cm.Block(28, 
    name="Blue Cloth",
    texture=(0x70,0x40),
    )

cm.PurpleCloth = cm.Block(29, 
    name="Purple Cloth",
    texture=(0x80,0x40),
    )

cm.IndigoCloth = cm.Block(30, 
    name="Indigo Cloth",
    texture=(0x90,0x40),
    )

cm.VioletCloth = cm.Block(31, 
    name="Violet Cloth",
    texture=(0xA0,0x40),
    )

cm.MagentaCloth = cm.Block(32, 
    name="Magenta Cloth",
    texture=(0xB0,0x40),
    )

cm.PinkCloth = cm.Block(33, 
    name="Pink Cloth",
    texture=(0xC0,0x40),
    )

cm.BlackCloth = cm.Block(34, 
    name="Black Cloth",
    texture=(0xD0,0x40),
    )

cm.GrayCloth = cm.Block(35, 
    name="Gray Cloth",
    texture=(0xE0,0x40),
    )

cm.WhiteCloth = cm.Block(36, 
    name="White Cloth",
    texture=(0xF0,0x40),
    )

cm.Flower = cm.Block(37, 
    name="Flower",
    texture=(0xD0,0x00),
    )

cm.Rose = cm.Block(38, 
    name="Rose",
    texture=(0xC0,0x00),
    )

cm.BrownMushroom = cm.Block(39, 
    name="Brown Mushroom",
    texture=(0xD0,0x10),
    )

cm.RedMushroom = cm.Block(40, 
    name="Red Mushroom",
    texture=(0xC0,0x10),
    )

cm.BlockOfGold = cm.Block(41, 
    name="Block of Gold",
    texture=((0x70,0x20), (0x70,0x20), (0x70,0x10), (0x70,0x30), (0x70,0x20), (0x70,0x20)),
    )

cm.BlockOfIron = cm.Block(42, 
    name="Block of Iron",
    texture=((0x60,0x20), (0x60,0x20), (0x60,0x10), (0x60,0x30), (0x60,0x20), (0x60,0x20)),
    )

cm.DoubleStoneSlab = cm.Block(43, 
    name="Double Stone Slab",
    texture=((0x50,0x00), (0x50,0x00), (0x60,0x00), (0x60,0x00), (0x50,0x00), (0x50,0x00)),
    )

cm.SingleStoneSlab = cm.Block(44, 
    name="Stone Slab",
    texture=((0x50,0x00), (0x50,0x00), (0x60,0x00), (0x60,0x00), (0x50,0x00), (0x50,0x00)),
    )

cm.Brick = cm.Block(45, 
    name="Brick",
    texture=(0x70,0x00),
    )

cm.TNT = cm.Block(46, 
    name="TNT",
    texture=((0x80,0x00), (0x80,0x00), (0x90,0x00), (0xA0,0x00), (0x80,0x00), (0x80,0x00)),
    )

cm.Bookshelf = cm.Block(47, 
    name="Bookshelf",
    texture=((0x30,0x20), (0x30,0x20), (0x40,0x00), (0x40,0x00), (0x30,0x20), (0x30,0x20)),
    )

cm.MossStone = cm.Block(48, 
    name="Moss Stone",
    texture=(0x40,0x20),
    )

cm.Obsidian = cm.Block(49, 
    name="Obsidian",
    texture=(0x50,0x20),
    )

cm.Torch = cm.Block(50, 
    name="Torch",
    texture=(0x00,0x50),
    )

cm.Fire = cm.Block(51, 
    name="Fire",
    texture=(0xF0,0x30),
    )

cm.InfiniteWaterSource = cm.Block(52, 
    name="Infinite water source",
    texture=(0xE0,0x00),
    )

cm.InfiniteLavaSource = cm.Block(53, 
    name="Infinite lava source",
    texture=(0xE0,0x10),
    )

cm.Chest = cm.Block(54, 
    name="Chest",
    texture=((0xA0,0x10), (0xA0,0x10), (0xA0,0x10), (0xB0,0x10), (0x90,0x10), (0x90,0x10)),
    )

cm.Cog = cm.Block(55, 
    name="Cog",
    texture=(0xF0,0x30),
    )

cm.DiamondOre = cm.Block(56, 
    name="Diamond Ore",
    texture=(0x20,0x30),
    )

cm.BlockOfDiamond = cm.Block(57, 
    name="Block Of Diamond",
    texture=((0x80,0x20), (0x80,0x20), (0x80,0x10), (0x80,0x30), (0x80,0x20), (0x80,0x20)),
    )

cm.CraftingTable = cm.Block(58, 
    name="Crafting Table",
    texture=((0xB0,0x30), (0xB0,0x30), (0xB0,0x20), (0x40,0x10), (0xC0,0x30), (0xC0,0x30)),
    )

cm.Crops = cm.Block(59, 
    name="Crops",
    texture=(0xF0,0x50),
    )

cm.Farmland = cm.Block(60, 
    name="Farmland",
    texture=(0x60,0x50),
    )

cm.Furnace = cm.Block(61, 
    name="Furnace",
    texture=((0xD0,0x20), (0xD0,0x20), (0x10,0x00), (0x10,0x00), (0xC0,0x20), (0xC0,0x20)),
    )

cm.LitFurnace = cm.Block(62, 
    name="Lit Furnace",
    texture=((0xD0,0x20), (0xD0,0x20), (0x10,0x00), (0x10,0x00), (0xD0,0x30), (0xD0,0x30)),
    )

del cm

