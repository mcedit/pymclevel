'''
from materials import classicMaterials, materials
'''
from numpy import *
NOTEX = 184
#wow, punching this map in would have been much easier in hex
class MCMaterials(object):
    def __repr__(self):
        return "<MCMaterials ({0})>".format(self.name)
        
    def materialNamed(self, name):
        return self.names.index(name);

clothColors = [
    "Red",
    "Orange",
    "Yellow",
    "Light Green",
    "Green",
    "Aqua",
    "Cyan",
    "Blue",
    "Purple",
    "Indigo",
    "Violet",
    "Magenta",
    "Pink",
    "Black",
    "Gray",
    "White",
    ]
classicMaterials = MCMaterials();
classicMaterials.name = "Classic"
classicMaterials.blockTextures = [
            (
                (NOTEX,)*6, "Air",
            ), (
                (1, 1, 1, 1, 1, 1), "Rock", #1: 
            ), (
                (3, 3, 0, 2, 3, 3), "Grass", #2:
            ), (
                (2, 2, 2, 2, 2, 2), "Dirt", #3: 
            ), (
                (16, 16, 16, 16, 16, 16), "Cobblestone", #4: 
            ), (
                (4, 4, 4, 4, 4, 4), "Wood", #5: 
            ), (
                (15, 15, 15, 15, 15, 15), "Sapling",  #6: 
            ), (
                (17, 17, 17, 17, 17, 17), "Adminium", #7: 
            ), (
                (14, 14, 14, 14, 14, 14), "Water", #8: 
            ), (
                (14, 14, 14, 14, 14, 14), "Stationary water", #9: 
            ), (
                (30, 30, 30, 30, 30, 30), "Lava", #10: 
            ), (
                (30, 30, 30, 30, 30, 30), "Stationary lava", #11: 
            ), (
                (18, 18, 18, 18, 18, 18),  "Sand", #12:
            ), (
                (19, 19, 19, 19, 19, 19),  "Gravel", #13:
            ), (
                (32, 32, 32, 32, 32, 32), "Gold ore", #14: 
            ), (
                (33, 33, 33, 33, 33, 33), "Iron ore",#15: 
            ), (
                (34, 34, 34, 34, 34, 34), "Coal ore",#16: 
            ), (
                (20, 20, 21, 21, 20, 20), "Tree trunk",#17: 
            ), (
                (52, 52, 52, 52, 52, 52), "Leaves",#18: 
            ), (
                (48, 48, 48, 48, 48, 48), "Sponge",#19: 
            ), (
                (49, 49, 49, 49, 49, 49), "Glass",#20: 
            )
            ] + list(((64+i,)*6, "{0} Cloth".format(clothColors[i])) for i in range(16)) + [ #21-36:"Cloth",
            (
                (13, 13, 13, 13, 13, 13), "Flower",#37: 
            ), (
                (12, 12, 12, 12, 12, 12), "Rose",#38: 
            ), (
                (29,)*6, "Brown mushroom",#39: 
            ), (
                (28,)*6, "Red mushroom",#40: 
            ), (
                (39, 39, 23, 55, 39, 39), "Solid Gold Block",#41: 
            ), (
                (38, 38, 22, 54, 38, 38), "Solid Iron Block",#42: 
            ), (
                (5, 5, 6, 6, 5, 5), "Double stone stair step",#43: 
            ), (
                (5, 5, 6, 6, 5, 5), "Single stone stair step",#44: 
            ), (
                (7, 7, 7, 7, 7, 7), "Red brick tile",#45: 
            ), (
                (8, 8, 9, 10, 8, 8), "TNT", #46: 
            ), (
                (35, 35, 4, 4, 35, 35), "Bookshelf",#47: 
            ), (
                (36, 36, 36, 36, 36, 36), "Moss covered cobblestone",#48: 
            ), (
                (37, 37, 37, 37, 37, 37), "Obsidian",#49: 
            ), (
                (80, 80, 80, 80, 80, 80), "Torch",#50: 
            ), (
                (63, 63, 63, 63, 63, 63), "Fire",#51:  XXXXX
            ), (
                (14, 14, 14, 14, 14, 14), "Infinite water source",#52: 
            ), (
                (30, 30, 30, 30, 30, 30), "Infinite lava source",#53: 
            ), (
                (26, 26, 26, 27, 25, 25), "Chest",#54: 
            ), (
                (63, 63, 63, 63, 63, 63), "Cog",#55: 
            ), (
                (50, 50, 50, 50, 50, 50), "Diamond Ore",#56: 
            ), (
                (40, 40, 24, 56, 40, 40), "Solid Diamond Block",#57: 
            ), (
                (59, 59, 43, 20, 60, 60), "Crafting Table",#58: 
            ), (
                (95, 95, 95, 95, 95, 95), "Crops",#59: 
            ), (
                (86, 86, 86, 86, 86, 86), "Farmland",#60: 
            ), (
                (45, 45,  1,  1, 44, 44), "Furnace",#61: 
            ), (
                (45, 45,  1,  1, 61, 61), "Lit Furnace",#62: 
            )] + [((NOTEX,)*6, "Not present in Creative") , #63-255: "Bugs",
            ] * 200 #create extras, then cut them off on the next line

classicMaterials.blockTextures = classicMaterials.blockTextures[:256]

classicMaterials.names = [name for (faces, name) in classicMaterials.blockTextures]


classicMaterials.lightEmission = zeros( (256,) );


materials = MCMaterials();
materials.name = "Alpha"
materials.blockTextures = [
            (
                (NOTEX,)*6, "Air", #0: 
            ), (
                (1, 1, 1, 1, 1, 1), "Stone", #1: 
            ), (
                (3, 3, 0, 2, 3, 3), "Grass", #2:
            ), (
                (2, 2, 2, 2, 2, 2), "Dirt", #3: 
            ), (
                (16, 16, 16, 16, 16, 16), "Cobblestone", #4: 
            ), (
                (4, 4, 4, 4, 4, 4), "Wood", #5: 
            ), (
                (15, 15, 15, 15, 15, 15), "Sapling",  #6: 
            ), (
                (17, 17, 17, 17, 17, 17), "Bedrock / Adminium", #7: 
            ), (
                (0xdf, 0xdf, 0xdf, 0xdf, 0xdf, 0xdf), "Water", #8: 
            ), (
                (0xdf, 0xdf, 0xdf, 0xdf, 0xdf, 0xdf), "Stationary water", #9: 
            ), (
                (0xff, 0xff, 0xff, 0xff, 0xff, 0xff), "Lava", #10: 
            ), (
                (0xff, 0xff, 0xff, 0xff, 0xff, 0xff), "Stationary lava", #11: 
            ), (
                (18, 18, 18, 18, 18, 18),  "Sand", #12:
            ), (
                (19, 19, 19, 19, 19, 19),  "Gravel", #13:
            ), (
                (32, 32, 32, 32, 32, 32), "Gold ore", #14: 
            ), (
                (33, 33, 33, 33, 33, 33), "Iron ore",#15: 
            ), (
                (34, 34, 34, 34, 34, 34), "Coal ore",#16: 
            ), (
                (20, 20, 21, 21, 20, 20), "Tree trunk",#17: 
            ), (
                (52, 52, 52, 52, 52, 52), "Leaves",#18: 
            ), (
                (48, 48, 48, 48, 48, 48), "Sponge",#19: 
            ), (
                (49, 49, 49, 49, 49, 49), "Glass",#20: 
            )
            ] + list(((NOTEX,)*6, "Unusable {0} Cloth".format(clothColors[i])) for i in range(14)) + [ #21-34:"Old Cloth",
            (
                (64,)*6,        "White Wool Cloth"
            ), (
                (NOTEX,)*6,     "Unusable White Cloth"
            ), (
                (13, 13, 13, 13, 13, 13), "Flower",#37: 
            ), (
                (12, 12, 12, 12, 12, 12), "Rose",#38: 
            ), (
                (29,)*6, "Brown mushroom",#39: 
            ), (
                (28,)*6, "Red mushroom",#40: 
            ), (
                (39, 39, 23, 55, 39, 39), "Solid Gold Block",#41: 
            ), (
                (38, 38, 22, 54, 38, 38), "Solid Iron Block",#42: 
            ), (
                (5, 5, 6, 6, 5, 5), "Double stone stair step",#43: 
            ), (
                (5, 5, 6, 6, 5, 5), "Single stone stair half step",#44: 
            ), (
                (7, 7, 7, 7, 7, 7), "Red brick tile",#45: 
            ), (
                (8, 8, 9, 10, 8, 8), "TNT", #46: 
            ), (
                (35, 35, 4, 4, 35, 35), "Bookshelf",#47: 
            ), (
                (36, 36, 36, 36, 36, 36), "Moss covered cobblestone",#48: 
            ), (
                (37, 37, 37, 37, 37, 37), "Obsidian",#49: 
            ), (
                (0x50,)*6, "Torch",#50: 
            ), (
                (0x1f,0x1f,0x1f,0x1f,0x1f,0x1f,),   "Fire",#51:  XXXXX
            ), (
                (0x41,0x41,0x41,0x41,0x41,0x41,),   "Mob Spawner",#52: 
            ), (
                (0x4,0x4,0x4,0x4,0x4,0x4,), "Wooden Stair",#53: 
            ), (
                (26, 26, 26, 27, 25, 25), "Chest",#54: 
            ), (
                (0x64,)*6, "Redstone Wire",#55: 
            ), (
                (50, 50, 50, 50, 50, 50), "Diamond Ore",#56: 
            ), (
                (40, 40, 24, 56, 40, 40), "Solid Diamond Block",#57: 
            ), (
                (59, 59, 43, 20, 60, 60), "Crafting Table",#58: 
            ), (
                (95, 95, 95, 95, 95, 95), "Crops",#59: 
            ), (
                (86, 86, 86, 86, 86, 86), "Farmland",#60: 
            ), (
                (45, 45,  1,  1, 44, 44), "Furnace",#61: 
            ), (
                (45, 45,  1,  1, 61, 61), "Lit Furnace",#62:
            ), (
                (NOTEX,)*6,     "Sign", #63
            ), (
                (0x51,)*6,      "Wooden Door" #64
            ), (
                (0x53,)*6,      "Ladder" #65
            ), (
                (0x80,)*6,      "Rail" #66
            ), (
                (0x10,)*6,      "Stone Stair" #67
            ), (
                (NOTEX,)*6,     "Wall Sign" #68
            ), (
                (NOTEX,)*6,     "Lever" #69
            ), (
                (NOTEX,)*6,     "Stone Floor Plate" #70
            ), (
                (0x52,)*6,      "Iron Door" #71
            ), (
                (NOTEX,)*6,     "Wood Floor Plate" #72
            ), (
                (0x33,)*6,      "Redstone Ore" #73:
            ), (
                (0x33,)*6,      "Redstone Ore (glowing)" #74
            ), (
                (0x73,)*6,      "Redstone Torch (off)" #75
            ), (
                (0x63,)*6,      "Redstone Torch (on)" #76
            ), (
                (NOTEX,)*6,     "Stone Button", #77
            ), (
                (0x42,)*6,      "Snow" #78
            ), (
                (0x43,)*6,      "Ice" #79
            ), (
                (0x42,)*6,      "Snow Block" #80  
            ), (
                (0x46, 0x46, 0x47, 0x45, 0x46, 0x46), "Cactus" #81
            ), (
                (0x48, 0x48, 0x48, 0x48, 0x48, 0x48), "Clay" #82
            ), (
                (0x49, 0x49, 0x49, 0x49, 0x49, 0x49), "Reeds" #83
            ), (
                (0x4A, 0x4A, 0x4A, 0x4B, 0x4A, 0x4A), "Jukebox" #84
            ), (
                (NOTEX,)*6, "Fence" #85
            ), (
                (0x77, 0x76, 0x66, 0x76, 0x76, 0x76), "Pumpkin" #86
            ), (
                (0x67,)*6, "Bloodstone" #87
            ), (
                (0x68,)*6, "Slow sand" #88
            ), (
                (0x69,)*6, "Lightstone" #89
            ), (
                (NOTEX,)*6, "Nether Portal" #90
            ), (
                (0x78, 0x76, 0x66, 0x76, 0x76, 0x76), "Glowing Pumpkin" #91
            ),
             
            
            ] + [((NOTEX,)*6, "Future Block!") , ] * 200 #create extras, then cut them off on the next line

materials.blockTextures = materials.blockTextures[:256]



materials.freebieBlocks = set( ( 6, #sapling
                               18, #leaves
                               37, #flower
                               38, #rose
                               39, #red shroom
                               40, #brown shroom
                               50, #torch
                               52, #mob spawner
                               55, #redstone wire
                               59, #crops
                               65, #ladder
                               66, #rail
                               75, #redstone torch dark
                               76, #redstone torch
                               ) );
    
materials.freebieBlocks = array( [ (x in materials.freebieBlocks) for x in range(256) ], dtype='bool');
classicMaterials.freebieBlocks = materials.freebieBlocks;

materials.names = [name for (faces, name) in materials.blockTextures]

materials.lightAbsorption = array([15,15,15,15]*64, uint8); 
#all blocks are solid by default
materials.transparentBlocks = {
                             0:0, #air
                             6:0, #sapling
                             8:3, #water
                             9:3, #stat. water
                             #10:15, #lava
                             #11:15, #stat. lava
                             18:1, #leaves
                             20:0, #glass
                             37:0, #flower
                             38:0, #rose
                             39:0, #red shroom
                             40:0, #brown shroom
                             50:0, #torch
                             52:0, #mob spawner
                             53:0, #wood stairs
                             55:0, #redstone wire
                             59:0, #crops
                             63:0, #sign
                             64:0, #wooden door
                             65:0, #ladder
                             66:0, #rail
                             67:0, #stone stairs
                             68:0, #wall sign
                             69:0, #lever
                             70:0, #stone floor plate
                             71:0, #iron door
                             72:0, #wood floor plate
                             75:0, #redstone torch, dark
                             76:0, #redstone torch
                             77:0, #stone button
                             78:0, #snow
                             79:3, #ice
                             83:0, #reeds
                             85:0, #fence
                             90:0, #nether portal
                             };
bn = materials.materialNamed
la = materials.lightAbsorption
la[0] = 0;
for i in materials.transparentBlocks:
    la[i] = materials.transparentBlocks[i];
materials.transparentBlocks = materials.lightAbsorption < 15
classicMaterials.transparentBlocks = materials.transparentBlocks
classicMaterials.lightAbsorption = materials.lightAbsorption


materials.lightEmission = zeros(256, uint8)
le = materials.lightEmission 
le[bn("Torch")] = 14
le[bn("Lit Furnace")] = 14
le[bn("Fire")] = 15
le[bn("Lava")] = 15
le[bn("Stationary lava")] = 15
le[bn("Redstone Torch (on)")] = 7
le[bn("Redstone Ore (glowing)")] = 9
le[bn("Brown mushroom")] = 1
le[bn("Lightstone")] = 15
le[bn("Nether Portal")] = 11
le[bn("Glowing Pumpkin")] = 15


classicMaterials.lightEmission = materials.lightEmission


namedMaterials = {
    'Classic':classicMaterials,
    'Alpha':materials,
}

materialNames = dict( (k,v) for v,k in namedMaterials.iteritems() )


#filters certain block types in old maps to types available in /game/
blockFilterClassicToAlpha = array(range(len(materials.blockTextures)), uint8)
b = blockFilterClassicToAlpha
b[8]=9; #water to still water
b[10]=11; #lava to still lava
b[36]=35; # the new white cloth
#b[19]=35; # sponge - unavailable
b[55]=35; # cog - 55 is now red wire
b[52]=9; # infinite water source - now mob spawner
b[53]=11; # infinite lava source - now wooden stair

for i in range(21, 35): blockFilterClassicToAlpha[i] = 35; # recolor all cloth to white

blockFilterAlphaToClassic = array(range(len(materials.blockTextures)), uint8)
b = blockFilterAlphaToClassic
b[50:255] = 36 # change all blocks from torch (50) on up to grey cloth

del b;
### xxx add filter tables for indev blocks

nullConversionTable = array(range(256), uint8) 

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

materials.blockTextures = array([map(texCoords, faces) for (faces, name) in materials.blockTextures], dtype='float32')
classicMaterials.blockTextures = array([map(texCoords, faces) for (faces, name) in classicMaterials.blockTextures], dtype='float32')

alphaMaterials = materials;
