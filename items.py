from logging import getLogger
logger = getLogger(__name__)

items_txt = """
:mc-version Minecraft 1.6.2

# Minecraft 1.5 onwards does not use stitched texture files, so FILE and CORDS
# are deprecated. To keep format consistent, dummy values like none.png 0,0 were
# used for new items.

# Also note MCEdit uses this file for items only (editing chest contents etc),
# not for rendering blocks, so FILE and CORDS are ignored.

#            Blocks
# ID  NAME                   FILE         CORDS   DAMAGE
   1  Stone                  terrain.png  1,0
   2  Grass                  terrain.png  3,0
   3  Dirt                   terrain.png  2,0
   4  Cobblestone            terrain.png  0,1
   5  Oak_Wooden_Planks      terrain.png  4,0    0
   5  Spruce_Wooden_Planks   terrain.png  6,12   1
   5  Birch_Wooden_Planks    terrain.png  6,13   2
   5  Jungle_Wooden_Planks   terrain.png  7,12   3
   6  Oak_Sapling            terrain.png  15,0   0
   6  Spruce_Sapling         terrain.png  15,3   1
   6  Birch_Sapling          terrain.png  15,4   2
   6  Jungle_Sapling         terrain.png  14,1   3
   7  Bedrock                terrain.png  1,1
   8  Water                  terrain.png  15,13
   9  Still_Water            terrain.png  15,13
  10  Lava                   terrain.png  15,15
  11  Still_Lava             terrain.png  15,15
  12  Sand                   terrain.png  2,1
  13  Gravel                 terrain.png  3,1
  14  Gold_Ore               terrain.png  0,2
  15  Iron_Ore               terrain.png  1,2
  16  Coal_Ore               terrain.png  2,2
  17  Oak_Wood               terrain.png  4,1    0
  17  Dark_Wood              terrain.png  4,7    1
  17  Birch_Wood             terrain.png  5,7    2
  17  Jungle_Wood            terrain.png  9,9    3
  18  Oak_Leaves             special.png  15,0   0
  18  Dark_Leaves            special.png  14,1   1
  18  Birch_Leaves           special.png  14,2   2
  18  Jungle_Leaves          special.png  14,3   3
  19  Sponge                 terrain.png  0,3
  20  Glass                  terrain.png  1,3
  21  Lapis_Lazuli_Ore       terrain.png  0,10
  22  Lapis_Lazuli_Block     terrain.png  0,9
  23  Dispenser              terrain.png  14,2
  24  Sandstone              terrain.png  0,12   0
  24  Chiseled_Sandstone     terrain.png  5,14   1
  24  Smooth_Sandstone       terrain.png  6,14   2
  25  Note_Block             terrain.png  10,4
  26  Bed_Block              terrain.png  6,8
  27  Powered_Rail           terrain.png  3,10
  28  Detector_Rail          terrain.png  3,12
  29  Sticky_Piston          terrain.png  10,6
  30  Cobweb                 terrain.png  11,0
  31  Dead_Bush              terrain.png  7,3    0
  31  Tall_Grass             special.png  15,0   1
  31  Fern                   special.png  15,1   2
  32  Dead_Bush              terrain.png  7,3
  33  Piston                 terrain.png  11,6
  34  Piston_(head)          terrain.png  11,6
  35  Wool                   terrain.png  0,4    0
  35  Orange_Wool            terrain.png  2,13   1
  35  Magenta_Wool           terrain.png  2,12   2
  35  Light_Blue_Wool        terrain.png  2,11   3
  35  Yellow_Wool            terrain.png  2,10   4
  35  Lime_Wool              terrain.png  2,9    5
  35  Pink_Wool              terrain.png  2,8    6
  35  Gray_Wool              terrain.png  2,7    7
  35  Light_Gray_Wool        terrain.png  1,14   8
  35  Cyan_Wool              terrain.png  1,13   9
  35  Purple_Wool            terrain.png  1,12   10
  35  Blue_Wool              terrain.png  1,11   11
  35  Brown_Wool             terrain.png  1,10   12
  35  Green_Wool             terrain.png  1,9    13
  35  Red_Wool               terrain.png  1,8    14
  35  Black_Wool             terrain.png  1,7    15
  37  Flower                 terrain.png  13,0
  38  Rose                   terrain.png  12,0
  39  Brown_Mushroom         terrain.png  13,1
  40  Red_Mushroom           terrain.png  12,1
  41  Block_of_Gold          terrain.png  7,1
  42  Block_of_Iron          terrain.png  6,1
  43  Double_Stone_Slab      terrain.png  5,0    0
  43  Double_Sandstone_Slab  terrain.png  0,12   1
  43  Double_Wooden_Slab     terrain.png  4,0    2
  43  Double_Stone_Slab      terrain.png  0,1    3
  43  Double_Brick_Slab         none.png  0,0    4
  43  Double_Stone_Brick_Slab   none.png  0,0    5
  43  Double_Nether_Brick_Slab  none.png  0,0    6
  43  Quartz_Slab               none.png  0,0    7
  43  Smooth_Stone_Slab         none.png  0,0    8
  43  Smooth_Sandstone_Slab     none.png  0,0    9
  43  Tile_Quartz_Slab          none.png  0,0    15
  44  Stone_Slab             special.png  2,2    0
  44  Sandstone_Slab         special.png  8,0    1
  44  Wooden_Slab            special.png  3,0    2
  44  Stone_Slab             special.png  1,0    3
  44  Brick_Slab             special.png  0,0    4
  44  Stone_Brick_Slab       special.png  2,0    5
  44  Nether_Brick_Slab         none.png  0,0    6
  43  Quartz_Slab               none.png  0,0    7
  45  Bricks                 terrain.png  7,0
  46  TNT                    terrain.png  8,0
  47  Bookshelf              terrain.png  3,2
  48  Moss_Stone             terrain.png  4,2
  49  Obsidian               terrain.png  5,2
  50  Torch                  terrain.png  0,5
  51  Fire                   special.png  0,5
  52  Monster_Spawner        terrain.png  1,4
  53  Oak_Wood_Stair         special.png  3,1
  54  Chest                  special.png  0,6
  55  Redstone_Dust          terrain.png  4,5
  56  Diamond_Ore            terrain.png  2,3
  57  Block_of_Diamond       terrain.png  8,1
  58  Workbench              terrain.png  12,3   (x1)
  59  Crops                  terrain.png  15,5
  60  Farmland               terrain.png  7,5
  61  Furnace                terrain.png  12,2
  62  Lit_Furnace            terrain.png  13,3
  63  Sign_Block             terrain.png  0,0
  64  Wooden_Door_Block      terrain.png  1,6
  65  Ladder                 terrain.png  3,5
  66  Rail                   terrain.png  0,8
  67  Stone_Stairs           special.png  1,1
  68  Wall_Sign              terrain.png  4,0
  69  Lever                  terrain.png  0,6
  70  Stone_Pressure_Plate   special.png  2,4
  71  Iron_Door_Block        terrain.png  2,6
  72  Wooden_Pressure_Plate  special.png  3,4
  73  Redstone_Ore           terrain.png  3,3
  74  Glowing_Redstone_Ore   terrain.png  3,3
  75  Redstone_Torch_(off)   terrain.png  3,7
  76  Redstone_Torch         terrain.png  3,6
  77  Stone_Button           special.png  2,3
  78  Snow_Layer             special.png  1,4
  79  Ice                    terrain.png  3,4
  80  Snow                   terrain.png  2,4
  81  Cactus                 terrain.png  6,4
  82  Clay                   terrain.png  8,4
  83  Sugar_cane             terrain.png  9,4
  84  Jukebox                terrain.png  10,4
  85  Fence                  special.png  3,2
  86  Pumpkin                terrain.png  7,7
  87  Netherrack             terrain.png  7,6
  88  Soul_Sand              terrain.png  8,6
  89  Glowstone              terrain.png  9,6
  90  Portal                 special.png  1,5
  91  Jack-o'-lantern        terrain.png  8,7
  92  Cake                   special.png  0,4
  93  Repeater_Block_(off)   terrain.png  3,8
  94  Repeater_Block         terrain.png  3,9
  95  Locked_Chest           special.png  0,2
  96  Trapdoor               terrain.png  4,5
  97  Silverfish_Block       terrain.png  1,0
  98  Stone_Brick            terrain.png  6,3    0
  98  Mossy_Stone_Brick      terrain.png  4,6    1
  98  Cracked_Stone_Brick    terrain.png  5,6    2
  98  Chiseled_Stone_Brick   terrain.png  5,13   3
  99  Brown_Mushroom_Block   terrain.png  13,7
 100  Red_Mushroom_Block     terrain.png  14,7
 101  Iron_Bars              terrain.png  5,5
 102  Glass_Pane             special.png  1,3
 103  Melon                  terrain.png  8,8
 104  Pumpkin_Stem           special.png  15,4
 105  Melon_Stem             special.png  15,4
 106  Vines                  special.png  15,2
 107  Fence_Gate             special.png  4,3
 108  Brick_Stairs           special.png  0,1
 109  Stone_Brick_Stairs     special.png  2,1
 110  Mycelium               terrain.png  13,4
 111  Lily_Pad               special.png  15,3
 112  Nether_Brick           terrain.png  0,14
 113  Nether_Brick_Fence     special.png  7,2
 114  Nether_Brick_Stairs    special.png  7,1
 115  Nether_Wart            terrain.png  2,14
 116  Enchantment_Table      terrain.png  6,11   (x1)
 117  Brewing_Stand          terrain.png  13,9
 118  Cauldron               terrain.png  10,9
 119  End_Portal             special.png  2,5
 120  End_Portal_Frame       terrain.png  15,9
 121  End_Stone              terrain.png  15,10
 122  Dragon_Egg             special.png  0,7
 123  Redstone_Lamp          terrain.png  3,13
 124  Redstone_Lamp_(on)     terrain.png  4,13
 125  Oak_Wooden_D._Slab     terrain.png  4,0    0
 125  Spruce_Wooden_D._Slab  terrain.png  6,12   1
 125  Birch_Wooden_D._Slab   terrain.png  6,13   2
 125  Jungle_Wooden_D._Slab  terrain.png  7,12   3
 126  Oak_Wooden_Slab        special.png  3,0    0
 126  Spruce_Wooden_Slab     special.png  4,0    1
 126  Birch_Wooden_Slab      special.png  5,0    2
 126  Jungle_Wooden_Slab     special.png  6,0    3
 127  Cocoa_Plant            special.png  15,5
 128  Sandstone_Stairs       special.png  8,1
 129  Emerald_Ore            terrain.png  11,10
 130  Ender_Chest            special.png  1,6
 131  Tripwire_Hook          terrain.png  12,10
 132  Tripwire               terrain.png  5,11
 133  Block_of_Emerald       terrain.png  9,1
 134  Spruce_Wood_Stairs     special.png  4,1
 135  Birch_Wood_Stairs      special.png  5,1
 136  Jungle_Wood_Stairs     special.png  6,1
 137  Command_Block          terrain.png  8,11
 138  Beacon                 special.png  2,6
 139  Cobblestone_Wall       special.png  1,2    0
 139  Moss_Stone_Wall        special.png  0,2    1
 140  Flower_Pot             terrain.png  9,11
 141  Carrots                terrain.png  11,12
 142  Potatoes               terrain.png  12,12
 143  Wooden_Button          special.png  3,3
 144  Head                     items.png  0,14
 145  Anvil                  special.png  3,6    0
 145  Slightly_Damaged_Anvil special.png  4,6    1
 145  Very_Damaged_Anvil     special.png  5,6    2
 146  Trapped_Chest                    none.png  0,0
 147  Weighted_Pressure_Plate_(Light)  none.png  0,0
 148  Weighted_Pressure_Plate_(Heavy)  none.png  0,0
 149  Redstone_Comparator_(inactive)   none.png  0,0
 150  Redstone_Comparator_(active)     none.png  0,0
 151  Daylight_Sensor                  none.png  0,0
 152  Block_of_Redstone                none.png  0,0
 153  Nether_Quartz_Ore                none.png  0,0
 154  Hopper                           none.png  0,0
 155  Block_of_Quartz                  none.png  0,0    0
 155  Chiseled_Quartz_Block            none.png  0,0    1
 155  Pillar_Quartz_Block              none.png  0,0    2
 156  Quartz_Stairs                    none.png  0,0
 157  Activator_Rail                   none.png  0,0
 158  Dropper                          none.png  0,0
 159  Stained_Clay                     none.png  0,0
 170  Hay_Block                        none.png  0,0
 171  Carpet                           none.png  0,0
 172  Hardened_Clay                    none.png  0,0
 173  Block_of_Coal                    none.png  0,0

#            Items
# ID  NAME                   FILE       CORDS  DAMAGE
 256  Iron_Shovel            items.png  2,5    +250
 257  Iron_Pickaxe           items.png  2,6    +250
 258  Iron_Axe               items.png  2,7    +250
 259  Flint_and_Steel        items.png  5,0    +64
 260  Apple                  items.png  10,0
 261  Bow                    items.png  5,1    +384
 262  Arrow                  items.png  5,2
 263  Coal                   items.png  7,0    0
 263  Charcoal               items.png  7,0    1
 264  Diamond                items.png  7,3
 265  Iron_Ingot             items.png  7,1
 266  Gold_Ingot             items.png  7,2
 267  Iron_Sword             items.png  2,4    +250
 268  Wooden_Sword           items.png  0,4    +59
 269  Wooden_Shovel          items.png  0,5    +59
 270  Wooden_Pickaxe         items.png  0,6    +59
 271  Wooden_Axe             items.png  0,7    +59
 272  Stone_Sword            items.png  1,4    +131
 273  Stone_Shovel           items.png  1,5    +131
 274  Stone_Pickaxe          items.png  1,6    +131
 275  Stone_Axe              items.png  1,7    +131
 276  Diamond_Sword          items.png  3,4    +1561
 277  Diamond_Shovel         items.png  3,5    +1561
 278  Diamond_Pickaxe        items.png  3,6    +1561
 279  Diamond_Axe            items.png  3,7    +1561
 280  Stick                  items.png  5,3
 281  Bowl                   items.png  7,4
 282  Mushroom_Stew          items.png  8,4    x1
 283  Golden_Sword           items.png  4,4    +32
 284  Golden_Shovel          items.png  4,5    +32
 285  Golden_Pickaxe         items.png  4,6    +32
 286  Golden_Axe             items.png  4,7    +32
 287  String                 items.png  8,0
 288  Feather                items.png  8,1
 289  Gunpowder              items.png  8,2
 290  Wooden_Hoe             items.png  0,8    +59
 291  Stone_Hoe              items.png  1,8    +131
 292  Iron_Hoe               items.png  2,8    +250
 293  Diamond_Hoe            items.png  3,8    +1561
 294  Golden_Hoe             items.png  4,8    +32
 295  Seeds                  items.png  9,0
 296  Wheat                  items.png  9,1
 297  Bread                  items.png  9,2
 298  Leather_Cap            items.png  0,0    +34
 299  Leather_Tunic          items.png  0,1    +48
 300  Leather_Pants          items.png  0,2    +46
 301  Leather_Boots          items.png  0,3    +40
 302  Chainmail_Helmet       items.png  1,0    +68
 303  Chainmail_Chestplate   items.png  1,1    +96
 304  Chainmail_Leggings     items.png  1,2    +92
 305  Chainmail_Boots        items.png  1,3    +80
 306  Iron_Helmet            items.png  2,0    +136
 307  Iron_Chestplate        items.png  2,1    +192
 308  Iron_Leggings          items.png  2,2    +184
 309  Iron_Boots             items.png  2,3    +160
 310  Diamond_Helmet         items.png  3,0    +272
 311  Diamond_Chestplate     items.png  3,1    +384
 312  Diamond_Leggings       items.png  3,2    +368
 313  Diamond_Boots          items.png  3,3    +320
 314  Golden_Helmet          items.png  4,0    +68
 315  Golden_Chestplate      items.png  4,1    +96
 316  Golden_Leggings        items.png  4,2    +92
 317  Golden_Boots           items.png  4,3    +80
 318  Flint                  items.png  6,0
 319  Raw_Porkchop           items.png  7,5
 320  Cooked_Porkchop        items.png  8,5
 321  Painting               items.png  10,1
 322  Golden_Apple           items.png  11,0
 322  Ench._Golden_Apple   special.png  0,3    1
 323  Sign                   items.png  10,2   x16
 324  Wooden_Door            items.png  11,2   x1
 325  Bucket                 items.png  10,4   x16
 326  Water_Bucket           items.png  11,4   x1
 327  Lava_Bucket            items.png  12,4   x1
 328  Minecart               items.png  7,8    x1
 329  Saddle                 items.png  8,6    x1
 330  Iron_Door              items.png  12,2   x1
 331  Redstone               items.png  8,3
 332  Snowball               items.png  14,0   x16
 333  Boat                   items.png  8,8    x1
 334  Leather                items.png  7,6
 335  Milk                   items.png  13,4   x1
 336  Brick                  items.png  6,1
 337  Clay                   items.png  9,3
 338  Sugar_Canes            items.png  11,1
 339  Paper                  items.png  10,3
 340  Book                   items.png  11,3
 341  Slimeball              items.png  14,1
 342  Minecart_with_Chest    items.png  7,9    x1
 343  Minecart_with_Furnace  items.png  7,10   x1
 344  Egg                    items.png  12,0
 345  Compass                items.png  6,3    (x1)
 346  Fishing_Rod            items.png  5,4    +64
 347  Clock                  items.png  6,4    (x1)
 348  Glowstone_Dust         items.png  9,4
 349  Raw_Fish               items.png  9,5
 350  Cooked_Fish            items.png  10,5
 351  Ink_Sack               items.png  14,4   0
 351  Rose_Red               items.png  14,5   1
 351  Cactus_Green           items.png  14,6   2
 351  Cocoa_Beans            items.png  14,7   3
 351  Lapis_Lazuli           items.png  14,8   4
 351  Purple_Dye             items.png  14,9   5
 351  Cyan_Dye               items.png  14,10  6
 351  Light_Gray_Dye         items.png  14,11  7
 351  Gray_Dye               items.png  15,4   8
 351  Pink_Dye               items.png  15,5   9
 351  Lime_Dye               items.png  15,6   10
 351  Dandelion_Yellow       items.png  15,7   11
 351  Light_Blue_Dye         items.png  15,8   12
 351  Magenta_Dye            items.png  15,9   13
 351  Orange_Dye             items.png  15,10  14
 351  Bone_Meal              items.png  15,11  15
 352  Bone                   items.png  12,1
 353  Sugar                  items.png  13,0
 354  Cake                   items.png  13,1   x1
 355  Bed                    items.png  13,2   x1
 356  Redstone_Repeater      items.png  6,5
 357  Cookie                 items.png  12,5
 358  Map                    items.png  12,3   x1
 359  Shears                 items.png  13,5   +238
 360  Melon_Slice            items.png  13,6
 361  Pumpkin_Seeds          items.png  13,3
 362  Melon_Seeds            items.png  14,3
 363  Raw_Beef               items.png  9,6
 364  Steak                  items.png  10,6
 365  Raw_Chicken            items.png  9,7
 366  Cooked_Chicken         items.png  10,7
 367  Rotten_Flesh           items.png  11,5
 368  Ender_Pearl            items.png  11,6
 369  Blaze_Rod              items.png  12,6
 370  Ghast_Tear             items.png  11,7
 371  Gold_Nugget            items.png  12,7
 372  Nether_Wart            items.png  13,7
 373  Potion               special.png  0,14
 374  Glass_Bottle           items.png  12,8
 375  Spider_Eye             items.png  11,8
 376  Fermented_Spider_Eye   items.png  10,8
 377  Blaze_Powder           items.png  13,9
 378  Magma_Cream            items.png  13,10
 379  Brewing_Stand          items.png  12,10  (x1)
 380  Cauldron               items.png  12,9   (x1)
 381  Eye_of_Ender           items.png  11,9
 382  Glistering_Melon       items.png  9,8
 383  Spawn_Egg              items.png  9,9
 384  Bottle_o'_Enchanting   items.png  11,10
 385  Fire_Charge            items.png  14,2
 386  Book_and_Quill         items.png  11,11  x1
 387  Written_Book           items.png  12,11  x1
 388  Emerald                items.png  10,11
 389  Item_Frame             items.png  14,12
 390  Flower_Pot             items.png  13,11
 391  Carrot                 items.png  8,7
 392  Potato                 items.png  7,7
 393  Baked_Potato           items.png  6,7
 394  Poisonous_Potato       items.png  6,8
 395  Empty_Map              items.png  13,12  x1
 396  Golden_Carrot          items.png  6,9
 397  Skeleton_Head          items.png  0,14   0
 397  Wither_Skeleton_Head   items.png  1,14   1
 397  Zombie_Head            items.png  2,14   2
 397  Human_Head             items.png  3,14   3
 397  Creeper_Head           items.png  4,14   4
 398  Carrot_on_a_Stick      items.png  6,6    +25
 399  Nether_Star            items.png  9,11
 400  Pumpkin_Pie            items.png  8,9
 401  Firework_Rocket        items.png  9,12
 402  Firework_Star          items.png  10,12
 403  Enchanted_Book         items.png  15,12
 404  Redstone_Comparator     none.png  0,0
 405  Nether_Brick            none.png  0,0
 406  Nether_Quartz           none.png  0,0
 407  Minecart_with_TNT       none.png  0,0
 408  Minecart_with_Hopper    none.png  0,0
 417  Iron_Horse_Armor        none.png  0,0
 418  Gold_Horse_Armor        none.png  0,0
 419  Diamond_Horse_Armor     none.png  0,0
 420  Lead                    none.png  0,0
 421  Name_Tag                none.png  0,0
2256  C418_-_13              items.png  0,15   x1
2257  C418_-_cat             items.png  1,15   x1
2258  C418_-_blocks          items.png  2,15   x1
2259  C418_-_chirp           items.png  3,15   x1
2260  C418_-_far             items.png  4,15   x1
2261  C418_-_mall            items.png  5,15   x1
2262  C418_-_mellohi         items.png  6,15   x1
2263  C418_-_stal            items.png  7,15   x1
2264  C418_-_strad           items.png  8,15   x1
2265  C418_-_ward            items.png  9,15   x1
2266  C418_-_11              items.png  10,15  x1
2267  C418_-_wait          special.png  0,8    x1

#           Potions
# ID  NAME                    FILE         CORDS  DAMAGE
 373  Water_Bottle            special.png  0,14   0
 373  Awkward_Potion          special.png  1,14   16
 373  Thick_Potion            special.png  1,14   32
 373  Mundane_Potion          special.png  1,14   64
 373  Mundane_Potion          special.png  1,14   8192
 373  Regeneration_(0:45)     special.png  2,14   8193
 373  Regeneration_(2:00)     special.png  2,14   8257
 373  Regeneration_II_(0:22)  special.png  2,14   8225
 373  Swiftness_(3:00)        special.png  3,14   8194
 373  Swiftness_(8:00)        special.png  3,14   8258
 373  Swiftness_II_(1:30)     special.png  3,14   8226
 373  Fire_Resistance_(3:00)  special.png  4,14   8195
 373  Fire_Resistance_(3:00)  special.png  4,14   8227
 373  Fire_Resistance_(8:00)  special.png  4,14   8259
 373  Healing                 special.png  6,14   8197
 373  Healing                 special.png  6,14   8261
 373  Healing_II              special.png  6,14   8229
 373  Strength_(3:00)         special.png  8,14   8201
 373  Strength_(8:00)         special.png  8,14   8265
 373  Strength_II_(1:30)      special.png  8,14   8233
 373  Poison_(0:45)           special.png  5,14   8196
 373  Poison_(2:00)           special.png  5,14   8260
 373  Poison_II_(0:22)        special.png  5,14   8228
 373  Weakness_(1:30)         special.png  7,14   8200
 373  Weakness_(1:30)         special.png  7,14   8332
 373  Weakness_(4:00)         special.png  7,14   8264
 373  Slowness_(1:30)         special.png  9,14   8202
 373  Slowness_(1:30)         special.png  9,14   8234
 373  Slowness_(4:00)         special.png  9,14   8266
 373  Harming                 special.png  10,14  8204
 373  Harming                 special.png  10,14  8268
 373  Harming_II              special.png  10,14  8236
 373  Night_Vision_(3:00)     special.png  11,14  8198
 373  Night_Vision_(8:00)     special.png  11,14  8262
 373  Invisibility_(3:00)     special.png  12,14  8206
 373  Invisibility_(8:00)     special.png  12,14  8270
# Unbrewable:
 373  Regeneration_II_(1:00)  special.png  2,14   8289
 373  Swiftness_II_(4:00)     special.png  3,14   8290
 373  Strength_II_(4:00)      special.png  8,14   8297
 373  Poison_II_(1:00)        special.png  5,14   8292

#           Splash Potions
# ID  NAME                    FILE         CORDS  DAMAGE
 373  Splash_Mundane          special.png  1,13   16384
 373  Regeneration_(0:33)     special.png  2,13   16385
 373  Regeneration_(1:30)     special.png  2,13   16499
 373  Regeneration_II_(0:16)  special.png  2,13   16417
 373  Swiftness_(2:15)        special.png  3,13   16386
 373  Swiftness_(6:00)        special.png  3,13   16450
 373  Swiftness_II_(1:07)     special.png  3,13   16418
 373  Fire_Resistance_(2:15)  special.png  4,13   16387
 373  Fire_Resistance_(2:15)  special.png  4,13   16419
 373  Fire_Resistance_(6:00)  special.png  4,13   16451
 373  Healing                 special.png  6,13   16389
 373  Healing                 special.png  6,13   16453
 373  Healing_II              special.png  6,13   16421
 373  Strength_(2:15)         special.png  8,13   16393
 373  Strength_(6:00)         special.png  8,13   16457
 373  Strength_II_(1:07)      special.png  8,13   16425
 373  Poison_(0:33)           special.png  5,13   16388
 373  Poison_(1:30)           special.png  5,13   16452
 373  Poison_II_(0:16)        special.png  5,13   16420
 373  Weakness_(1:07)         special.png  7,13   16392
 373  Weakness_(1:07)         special.png  7,13   16424
 373  Weakness_(3:00)         special.png  7,13   16456
 373  Slowness_(1:07)         special.png  9,13   16394
 373  Slowness_(1:07)         special.png  9,13   16426
 373  Slowness_(3:00)         special.png  9,13   16458
 373  Harming                 special.png  10,13  16396
 373  Harming                 special.png  10,13  16460
 373  Harming_II              special.png  10,13  16428
 373  Night_Vision_(3:00)     special.png  11,13  16390
 373  Night_Vision_(8:00)     special.png  11,13  16454
 373  Invisibility_(3:00)     special.png  12,13  16398
 373  Invisibility_(8:00)     special.png  12,13  16462
# Unbrewable:
 373  Regeneration_II_(0:45)  special.png  2,13   16481
 373  Swiftness_II_(3:00)     special.png  3,13   16482
 373  Strength_II_(3:00)      special.png  8,13   16489
 373  Poison_II_(0:45)        special.png  5,13   16484

#           Spawn Eggs
# ID  NAME                   FILE         CORDS  DAMAGE
 383  Spawn_Creeper          special.png  0,9    50
 383  Spawn_Skeleton         special.png  1,9    51
 383  Spawn_Spider           special.png  2,9    52
 383  Spawn_Zombie           special.png  3,9    54
 383  Spawn_Slime            special.png  4,9    55
 383  Spawn_Ghast            special.png  0,10   56
 383  Spawn_Zombie_Pigmen    special.png  1,10   57
 383  Spawn_Enderman         special.png  2,10   58
 383  Spawn_Cave_Spider      special.png  3,10   59
 383  Spawn_Silverfish       special.png  4,10   60
 383  Spawn_Blaze            special.png  0,11   61
 383  Spawn_Magma_Cube       special.png  1,11   62
 383  Spawn_Bat              special.png  5,9    65
 383  Spawn_Witch            special.png  5,10   66
 383  Spawn_Pig              special.png  2,11   90
 383  Spawn_Sheep            special.png  3,11   91
 383  Spawn_Cow              special.png  4,11   92
 383  Spawn_Chicken          special.png  0,12   93
 383  Spawn_Squid            special.png  1,12   94
 383  Spawn_Wolf             special.png  2,12   95
 383  Spawn_Mooshroom        special.png  3,12   96
 383  Spawn_Villager         special.png  4,12   120

#           Groups
# NAME      ICON  ITEMS
# Column 1
~ Natural    2     2,3,12,24,128,44~1,13,82,79,80,78
~ Stone      1     1,4,48,67,44~3,139,140,98,109,44~5,44~0,45,108,44~4,101
~ Wood       5     17,5,53,134,135,136,126,47,85,107,20,102,30
~ NetherEnd  87    87,88,89,348,112,114,113,372,121,122
~ Ores       56    16,15,14,56,129,73,21,49,42,41,57,133,22,263~0,265,266,264,388
~ Special    54    46,52,58,54,130,61,23,25,84,116,379,380,138,146~0,321,389,323,324,330,355,65,96,390,397
~ Plants1    81    31~1,31~2,106,111,18,81,86,91,103,110
~ Plants2    6     295,361,362,6,296,338,37,38,39,40,32
~ Transport  328   66,27,28,328,342,343,333,329,398
~ Logic      331   331,76,356,69,70,72,131,77,144,33,29,123,137
~ Wool       35    35~0,35~8,35~7,35~15,35~14,35~12,35~1,35~4,35~5,35~13,35~11,35~3,35~9,35~10,35~2,35~6
~ Dye        351   351~15,351~7,351~8,351~0,351~1,351~3,351~14,351~11,351~10,351~2,351~4,351~12,351~6,351~5,351~13,351~9
# Column 2
~ TierWood   299   298,299,300,301,269,270,271,290,268
~ TierStone  303   302,303,304,305,273,274,275,291,272
~ TierIron   307   306,307,308,309,256,257,258,292,267
~ TierDiam   311   310,311,312,313,277,278,279,293,276
~ TierGold   315   314,315,316,317,284,285,286,294,283
~ Tools      261   50,261,262,259,346,359,345,347,395,358,325,326,327,335,384,385,386,387
~ Food       297   260,322,282,297,360,319,320,363,364,365,366,349,350,354,357,391,396,392,393,394,400
~ Items      318   280,281,318,337,336,353,339,340,332,376,377,382,381
~ Drops      341   344,288,334,287,352,289,367,375,341,368,369,370,371,378,399
~ Music      2257  2256,2257,2258,2259,2260,2261,2262,2263,2264,2265,2266,2267
~ Potion     373   373~0,373~16,373~32,373~8192,373~8193,373~8257,373~8225,373~8289,373~8194,373~8258,373~8226,373~8290,373~8195,373~8259,373~8197,373~8229,373~8201,373~8265,373~8233,373~8297,373~8196,373~8260,373~8228,373~8292,373~8200,373~8264,373~8202,373~8266,373~8204,373~8236,373~8198,373~8262,373~8206,373~8270,373~16384,373~16385,373~16499,373~16417,373~16481,373~16386,373~16450,373~16418,373~16482,373~16387,373~16451,373~16389,373~16421,373~16393,373~16457,373~16425,373~16489,373~16388,373~16452,373~16420,373~16484,373~16392,373~16456,373~16394,373~16458,373~16396,373~16428,373~16390,373~16454,373~16398,373~16462
~ Eggs       383   383~50,383~51,383~52,383~54,383~55,383~56,383~57,383~58,383~59,383~60,383~61,383~62,383~65,383~66,383~90,383~91,383~92,383~93,383~94,383~95,383~96,383~120

#            Enchantments
# EID  NAME                   MAX  ITEMS
+   0  Protection             4    298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317
+   1  Fire_Protection        4    298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317
+   2  Feather_Falling        4    301,305,309,313,317
+   3  Blast_Protection       4    298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317
+   4  Projectile_Protection  4    298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317
+   5  Respiration            3    298,302,306,310,314
+   6  Aqua_Affinity          1    298,302,306,310,314
+  16  Sharpness              5    268,272,267,276,283
+  17  Smite                  5    268,272,267,276,283
+  18  Bane_of_Arthropods     5    268,272,267,276,283
+  19  Knockback              2    268,272,267,276,283
+  20  Fire_Aspect            2    268,272,267,276,283
+  21  Looting                3    268,272,267,276,283
+  32  Efficiency             5    269,270,271,273,274,275,256,257,258,277,278,279,284,285,286
+  33  Silk_Touch             1    269,270,271,273,274,275,256,257,258,277,278,279,284,285,286
+  34  Unbreaking             3    269,270,271,273,274,275,256,257,258,277,278,279,284,285,286
+  35  Fortune                3    269,270,271,273,274,275,256,257,258,277,278,279,284,285,286
+  48  Power                  5    261
+  49  Punch                  2    261
+  50  Flame                  1    261
+  51  Infinity               1    261
"""


class ItemType (object):
    def __init__(self, id, name, imagefile=None, imagecoords=None, maxdamage=0, damagevalue=0, stacksize=64):
        self.id = id
        self.name = name
        self.imagefile = imagefile
        self.imagecoords = imagecoords
        self.maxdamage = maxdamage
        self.damagevalue = damagevalue
        self.stacksize = stacksize

    def __repr__(self):
        return "ItemType({0}, '{1}')".format(self.id, self.name)

    def __str__(self):
        return "ItemType {0}: {1}".format(self.id, self.name)


class Items (object):
    items_txt = items_txt

    def __init__(self, filename=None):
        if filename is None:
            items_txt = self.items_txt
        else:
            try:
                with file(filename) as f:
                    items_txt = f.read()
            except Exception, e:
                logger.info("Error reading '%s': %s", filename, e)
                logger.info("Using internal data.")
                items_txt = self.items_txt

        self.itemtypes = {}
        self.itemgroups = []

        for line in items_txt.split("\n"):
            try:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line[0] == "#":  # comment
                    continue
                if line[0] == "+":  # enchantment
                    continue
                if line[0] == "~":  # category
                    fields = line.split()
                    name, icon, items = fields[1:4]
                    items = items.split(",")
                    self.itemgroups.append((name, icon, items))
                    continue

                stacksize = 64
                damagevalue = None
                maxdamage = 0

                fields = line.split()
                if len(fields) >= 4:
                    maxdamage = None
                    id, name, imagefile, imagecoords = fields[0:4]
                    if len(fields) > 4:
                        info = fields[4]
                        if info[0] == '(':
                            info = info[1:-1]
                        if info[0] == 'x':
                            stacksize = int(info[1:])
                        elif info[0] == '+':
                            maxdamage = int(info[1:])
                        else:
                            damagevalue = int(info)
                    id = int(id)
                    name = name.replace("_", " ")
                    imagecoords = imagecoords.split(",")

                    self.itemtypes[(id, damagevalue)] = ItemType(id, name, imagefile, imagecoords, maxdamage, damagevalue, stacksize)
            except Exception, e:
                print "Error reading line:", e
                print "Line: ", line
                print

        self.names = dict((item.name, item.id) for item in self.itemtypes.itervalues())

    def findItem(self, id=0, damage=None):
        item = self.itemtypes.get((id, damage))
        if item:
            return item

        item = self.itemtypes.get((id, None))
        if item:
            return item

        item = self.itemtypes.get((id, 0))
        if item:
            return item

        return ItemType(id, "Unknown Item {0}:{1}".format(id, damage), damagevalue=damage)
        #raise ItemNotFound, "Item {0}:{1} not found".format(id, damage)


class ItemNotFound(KeyError):
    pass

items = Items()
