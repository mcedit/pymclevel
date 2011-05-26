
items_txt = """
:version 18

#            Blocks
# ID  NAME                   FILE         CORDS   DAMAGE
   1  Stone                  terrain.png  1,0
   2  Grass                  terrain.png  3,0
   3  Dirt                   terrain.png  2,0
   4  Cobblestone            terrain.png  0,1
   5  Wooden_Planks          terrain.png  4,0
   6  Sapling                terrain.png  15,0   0
   6  Spruce_Sapling         terrain.png  15,3   1
   6  Birch_Sapling          terrain.png  15,4   2
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
  17  Wood                   terrain.png  4,1    0
  17  Dark_Wood              terrain.png  4,7    1
  17  Birch_Wood             terrain.png  5,7    2
  18  Leaves                 terrain.png  4,3
  19  Sponge                 terrain.png  0,3
  20  Glass                  terrain.png  1,3
  21  Lapis_Lazuli_Ore       terrain.png  0,10
  22  Lapis_Lazuli_Block     terrain.png  0,9
  23  Dispenser              terrain.png  14,2
  24  Sandstone              terrain.png  0,12
  25  Note_Block             terrain.png  10,4
  26  Bed_Block              terrain.png  6,8
  27  Powered_Rail           terrain.png  3,10
  28  Detector_Rail          terrain.png  3,12
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
  44  Stone_Slab             special.png  0,0    0
  44  Sandstone_Slab         special.png  1,2    1
  44  Wooden_Slab            special.png  2,2    2
  44  Stone_Slab             special.png  3,2    3
  45  Brick                  terrain.png  7,0
  46  TNT                    terrain.png  8,0
  47  Bookshelf              terrain.png  3,2
  48  Moss_Stone             terrain.png  4,2
  49  Obsidian               terrain.png  5,2
  50  Torch                  terrain.png  0,5
  51  Fire                   special.png  1,0
  52  Monster_Spawner        terrain.png  1,4
  53  Wooden_Stairs          special.png  3,0
  54  Chest                  terrain.png  11,1
  55  Redstone_Dust          terrain.png  4,5
  56  Diamond_Ore            terrain.png  2,3
  57  Block_of_Diamond       terrain.png  8,1
  58  Workbench              terrain.png  12,3
  59  Crops                  terrain.png  15,5
  60  Farmland               terrain.png  7,5
  61  Furnace                terrain.png  12,2
  62  Lit_Furnace            terrain.png  13,3
  63  Sign_Block             terrain.png  0,0
  64  Wooden_Door_Block      terrain.png  1,6
  65  Ladder                 terrain.png  3,5
  66  Rail                   terrain.png  0,8
  67  Stone_Stairs           special.png  4,0
  68  Wall_Sign              terrain.png  4,0
  69  Lever                  terrain.png  0,6
  70  Stone_Pressure_Plate   special.png  0,1
  71  Iron_Door_Block        terrain.png  2,6
  72  Wooden_Pressure_Plate  special.png  1,1
  73  Redstone_Ore           terrain.png  3,3
  74  Glowing_Redstone_Ore   terrain.png  3,3
  75  Redstone_Torch_(off)   terrain.png  3,7
  76  Redstone_Torch         terrain.png  3,6
  77  Button                 special.png  2,1
  78  Snow_Layer             special.png  3,1
  79  Ice                    terrain.png  3,4
  80  Snow                   terrain.png  2,4
  81  Cactus                 terrain.png  6,4
  82  Clay                   terrain.png  8,4
  83  Sugar_Cane             terrain.png  9,4
  84  Jukebox                terrain.png  10,4
  85  Fence                  special.png  2,0
  86  Pumpkin                terrain.png  7,7
  87  Netherrack             terrain.png  7,6
  88  Soul_Sand              terrain.png  8,6
  89  Glowstone              terrain.png  9,6
  90  Portal                 special.png  4,1
  91  Jack-o'-lantern        terrain.png  8,7
  92  Cake                   special.png  0,2
  93  Repeater_Block_(off)   terrain.png  3,8
  94  Repeater_Block         terrain.png  3,9

#            Items
# ID  NAME                   FILE       CORDS  DAMAGE
 256  Iron_Shovel            items.png  2,5    +250
 257  Iron_Pickaxe           items.png  2,6    +250
 258  Iron_Axe               items.png  2,7    +250
 259  Flint_and_Steel        items.png  5,0    +64
 260  Apple                  items.png  10,0   x1
 261  Bow                    items.png  5,1
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
 281  Bowl                   items.png  7,4    x1
 282  Mushrom_Stew           items.png  8,4    x1
 283  Golden_sword           items.png  4,4    +32
 284  Golden_shovel          items.png  4,5    +32
 285  Golden_pickaxe         items.png  4,6    +32
 286  Golden_axe             items.png  4,7    +32
 287  String                 items.png  8,0
 288  Feather                items.png  8,1
 289  Gunpowder              items.png  8,2
 290  Wooden_Hoe             items.png  0,8    +59
 291  Stone_Hoe              items.png  1,8    +131
 292  Iron_Hoe               items.png  2,8    +250
 293  Diamond_Hoe            items.png  3,8    +1561
 294  Golden_hoe             items.png  4,8    +32
 295  Seeds                  items.png  9,0
 296  Wheat                  items.png  9,1
 297  Bread                  items.png  9,2    x1
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
 319  Raw_Porkchop           items.png  7,5    x1
 320  Porkchop               items.png  8,5    x1
 321  Painting               items.png  10,1   x1
 322  Golden_Apple           items.png  11,0   x1
 323  Sign                   items.png  10,2   x1
 324  Wooden_Door            items.png  11,2   x1
 325  Bucket                 items.png  10,4   x1
 326  Water_Bucket           items.png  11,4   x1
 327  Lava_Bucket            items.png  12,4   x1
 328  Minecart               items.png  7,8    x1
 329  Saddle                 items.png  8,6    x1
 330  Iron_Door              items.png  12,2   x1
 331  Redstone               items.png  8,3
 332  Snowball               items.png  14,0   x16
 333  Boat                   items.png  8,8    x1
 334  Leather                items.png  7,6
 335  Milk                   items.png  13,4
 336  Brick                  items.png  6,1
 337  Clay                   items.png  9,3
 338  Sugar_Cane             items.png  11,1
 339  Paper                  items.png  10,3
 340  Book                   items.png  11,3
 341  Slimeball              items.png  14,1
 342  Minecart_with_Chest    items.png  7,9    x1
 343  Minecart_with_Furnace  items.png  7,10   x1
 344  Egg                    items.png  12,0
 345  Compass                items.png  6,3    x1
 346  Fishing_Rod            items.png  5,4    +64
 347  Clock                  items.png  6,4    x1
 348  Glowstone_Dust         items.png  9,4
 349  Raw_Fish               items.png  9,5    x1
 350  Cooked_Fish            items.png  10,5   x1
 351  Ink_Sack               items.png  14,4   0
 351  Rose_Red               items.png  14,5   1
 351  Cactus_Green           items.png  14,6   2
 351  Coco_Beans             items.png  14,7   3
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
 357  Cookie                 items.png  12,5   x8
2256  Gold_Music_Disk        items.png  0,15   x1
2257  Green_Music_Disk       items.png  1,15   x1

#            Groups
# NAME      ICON  ITEMS
~ Blocks    2     1,2,3,12,24,44~1,13,82,4,48,67,44~3,17,5,53,44~2,47,20,44~0,49,79,80,78,7,45,19,87,88
~ Plants    6     18,81,86,91,6,37,38,39,40
~ Tools     257   269,270,271,290,273,274,275,291,256,257,258,292,277,278,279,293,284,285,286,294,259,346
~ Weapons   267   268,272,267,276,283,261,262,332
~ Armor     303   298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317
~ Food      297   260,322,281,282,295,296,297,319,320,344,349,350,353,354,357
~ Ores      56    16,15,14,56,73,21,263,265,266,264,42,41,57,22,89,348
~ Special   54    8,10,90,58,54,61,23,25,46,52,84,2256,2257,51,50,85,321,323,324,330,355,325,326,327,335,345,347
~ Items     341   280,287,288,289,334,341,318,337,336,338,339,340,352
~ Movement  328   65,66,27,28,328,342,343,333,329
~ Logic     76    331,76,356,69,70,72,77
~ Wool      35    35,351

"""
class ItemType (object):
    def __init__(self, id, name, imagefile = None, imagecoords = None, maxdamage = 0, damagevalue = 0, stacksize = 64):
        self.id=id
        self.name=name
        self.imagefile=imagefile
        self.imagecoords=imagecoords
        self.maxdamage=maxdamage
    def __repr__(self):
        return "ItemType({0}, '{1}')".format(self.id, self.name)
    def __str__(self):
        return "ItemType {0}: {1}".format(self.id, self.name)
    
class Items (object):
    items_txt = items_txt
    def __init__(self, filename = None):
        if filename is None:
            items_txt = self.items_txt
        else:
            try:
                with file(filename) as f:
                    items_txt = f.read()
            except Exception, e:
                print "Error reading items.txt: ", e;
                print "Using internal data."
                items_txt = self.items_txt
            
        self.itemtypes = {};
        
        for line in items_txt.split("\n"):
            try:
                line = line.strip()
                if len(line) == 0: continue
                if line[0] == "#": continue;
                if line[0] == "~": continue; #groups
                stacksize = 64
                damagevalue = None
                maxdamage = 0
                
                fields = line.split();
                if len(fields) >= 4:
                    maxdamage = None;
                    id, name, imagefile, imagecoords = fields[0:4]
                    if len(fields) > 4:
                        info = fields[4]
                        if info[0] == 'x':
                            stacksize = int(info[1:])
                        elif info[0] == '+':
                            maxdamage = int(info[1:])
                        else:
                            damagevalue = int(info)
                    id = int(id);
                    name = name.replace("_", " ");
                    imagecoords = imagecoords.split(",");
                    
                    self.itemtypes[(id, damagevalue)] = ItemType(id, name, imagefile, imagecoords, maxdamage, damagevalue, stacksize)
            except Exception, e:
                print "Error reading line:", e
                print "Line: ", line
                print
                
        self.names = dict((item.name, item.id) for item in self.itemtypes.itervalues())
    
    def findItem(self, id=0, damage=None):
        item = self.itemtypes.get((id, damage))
        if item: return item
        
        item = self.itemtypes.get((id, None))
        if item: return item
        
        item = self.itemtypes.get((id, 0))
        if item: return item
        
        raise ItemNotFound, "Item {0}:{1} not found".format(id, damage)

class ItemNotFound(KeyError): pass

items = Items();

