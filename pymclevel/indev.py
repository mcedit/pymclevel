'''
Created on Jul 22, 2011

@author: Rio
'''


"""
Indev levels:

TAG_Compound "MinecraftLevel"
{
   TAG_Compound "Environment" 
   {
      TAG_Short "SurroundingGroundHeight"// Height of surrounding ground (in blocks)
      TAG_Byte "SurroundingGroundType"   // Block ID of surrounding ground
      TAG_Short "SurroundingWaterHeight" // Height of surrounding water (in blocks)
      TAG_Byte "SurroundingWaterType"    // Block ID of surrounding water
      TAG_Short "CloudHeight"            // Height of the cloud layer (in blocks)
      TAG_Int "CloudColor"               // Hexadecimal value for the color of the clouds
      TAG_Int "SkyColor"                 // Hexadecimal value for the color of the sky
      TAG_Int "FogColor"                 // Hexadecimal value for the color of the fog
      TAG_Byte "SkyBrightness"           // The brightness of the sky, from 0 to 100
   }
   
   TAG_List "Entities"
   {
      TAG_Compound
      {
         // One of these per entity on the map.
         // These can change a lot, and are undocumented.
         // Feel free to play around with them, though.
         // The most interesting one might be the one with ID "LocalPlayer", which contains the player inventory
      }
   }
   
   TAG_Compound "Map"
   {
      // To access a specific block from either byte array, use the following algorithm:
      // Index = x + (y * Depth + z) * Width

      TAG_Short "Width"                  // Width of the level (along X) 
      TAG_Short "Height"                 // Height of the level (along Y) 
      TAG_Short "Length"                 // Length of the level (along Z) 
      TAG_Byte_Array "Blocks"             // An array of Length*Height*Width bytes specifying the block types
      TAG_Byte_Array "Data"              // An array of Length*Height*Width bytes with data for each blocks
      
      TAG_List "Spawn"                   // Default spawn position
      {
         TAG_Short x  // These values are multiplied by 32 before being saved
         TAG_Short y  // That means that the actual values are x/32.0, y/32.0, z/32.0
         TAG_Short z
      }
   }
   
   TAG_Compound "About"
   {
      TAG_String "Name"                  // Level name
      TAG_String "Author"                // Name of the player who made the level
      TAG_Long "CreatedOn"               // Timestamp when the level was first created
   }
}
"""
from mclevelbase import *

MinecraftLevel = "MinecraftLevel"

Environment = "Environment"
SurroundingGroundHeight = "SurroundingGroundHeight"
SurroundingGroundType = "SurroundingGroundType"
SurroundingWaterHeight = "SurroundingWaterHeight"
SurroundingWaterType = "SurroundingWaterType"
CloudHeight = "CloudHeight"
CloudColor = "CloudColor"
SkyColor = "SkyColor"
FogColor = "FogColor"
SkyBrightness = "SkyBrightness"

About = "About"
Name = "Name"
Author = "Author"
CreatedOn = "CreatedOn"
Spawn = "Spawn"

__all__ = ["MCIndevLevel"]


class MCIndevLevel(EntityLevel):

    """ IMPORTANT: self.Blocks and self.Data are indexed with [x,z,y] via axis 
    swapping to be consistent with infinite levels."""

    def setPlayerSpawnPosition(self, pos, player=None):
        assert len(pos) == 3
        self.Spawn = array(pos);

    def playerSpawnPosition(self, player=None):
        return self.Spawn;

    def setPlayerPosition(self, pos, player="Ignored"):
        for x in self.root_tag["Entities"]:
            if x["id"].value == "LocalPlayer":
                x["Pos"] = TAG_List([TAG_Float(p) for p in pos])

    def getPlayerPosition(self, player="Ignored"):
        for x in self.root_tag["Entities"]:
            if x["id"].value == "LocalPlayer":
                return array(map(lambda x:x.value, x["Pos"]));

    def setPlayerOrientation(self, yp, player="Ignored"):
        for x in self.root_tag["Entities"]:
            if x["id"].value == "LocalPlayer":
                x["Rotation"] = TAG_List([TAG_Float(p) for p in yp])

    def playerOrientation(self, player="Ignored"):
        """ returns (yaw, pitch) """
        for x in self.root_tag["Entities"]:
            if x["id"].value == "LocalPlayer":
                return array(map(lambda x:x.value, x["Rotation"]));

    def setBlockDataAt(self, x, y, z, newdata):
        if x < 0 or y < 0 or z < 0: return 0
        if x >= self.Width or y >= self.Height or z >= self.Length: return 0;
        self.Data[x, z, y] = (newdata & 0xf);

    def blockDataAt(self, x, y, z):
        if x < 0 or y < 0 or z < 0: return 0
        if x >= self.Width or y >= self.Height or z >= self.Length: return 0;
        return self.Data[x, z, y];

    def blockLightAt(self, x, y, z):
        if x < 0 or y < 0 or z < 0: return 0
        if x >= self.Width or y >= self.Height or z >= self.Length: return 0;
        return self.BlockLight[x, z, y];

    def __repr__(self):
        return u"MCIndevLevel({0}): {1}W {2}L {3}H".format(self.filename, self.Width, self.Length, self.Height)

    @classmethod
    def _isTagLevel(cls, root_tag):
        return "MinecraftLevel" == root_tag.name

    def __init__(self, root_tag=None, filename=""):
        self.Width = 0
        self.Height = 0
        self.Length = 0
        self.Blocks = array([], uint8)
        self.Data = array([], uint8)
        self.Spawn = (0, 0, 0)
        self.filename = filename;


        if root_tag:

            self.root_tag = root_tag;
            mapTag = root_tag[Map];
            self.Width = mapTag[Width].value
            self.Length = mapTag[Length].value
            self.Height = mapTag[Height].value

            mapTag[Blocks].value.shape = (self.Height, self.Length, self.Width)

            self.Blocks = swapaxes(mapTag[Blocks].value, 0, 2)

            mapTag[Data].value.shape = (self.Height, self.Length, self.Width)

            self.Data = swapaxes(mapTag[Data].value, 0, 2)



            self.BlockLight = self.Data & 0xf

            self.Data >>= 4

            self.Spawn = [mapTag[Spawn][i].value for i in range(3)];

            if not Entities in root_tag:
                root_tag[Entities] = TAG_List();
            self.Entities = root_tag[Entities]

            if not TileEntities in root_tag:
                root_tag[TileEntities] = TAG_List();
            self.TileEntities = root_tag[TileEntities]
            #xxx fixup TileEntities positions to match infdev format
            for te in self.TileEntities:
                pos = te["Pos"].value

                (x, y, z) = self.decodePos(pos)

                TileEntity.setpos(te, (x, y, z))

            if len(filter(lambda x:x['id'].value == 'LocalPlayer', root_tag[Entities])) == 0: #omen doesn't make a player entity
                p = TAG_Compound()
                p['id'] = TAG_String('LocalPlayer')
                p['Pos'] = TAG_List([TAG_Float(0.), TAG_Float(64.), TAG_Float(0.)])
                p['Rotation'] = TAG_List([TAG_Float(0.), TAG_Float(45.)])

                root_tag[Entities].append(p)
                #self.saveInPlace();

        else:
            info(u"Creating new Indev levels is not yet implemented.!")
            raise ValueError, "Can't do that yet"
#            self.SurroundingGroundHeight = root_tag[Environment][SurroundingGroundHeight].value
#            self.SurroundingGroundType = root_tag[Environment][SurroundingGroundType].value
#            self.SurroundingWaterHeight = root_tag[Environment][SurroundingGroundHeight].value
#            self.SurroundingWaterType = root_tag[Environment][SurroundingWaterType].value
#            self.CloudHeight = root_tag[Environment][CloudHeight].value
#            self.CloudColor = root_tag[Environment][CloudColor].value
#            self.SkyColor = root_tag[Environment][SkyColor].value
#            self.FogColor = root_tag[Environment][FogColor].value
#            self.SkyBrightness = root_tag[Environment][SkyBrightness].value
#            self.TimeOfDay = root_tag[Environment]["TimeOfDay"].value
#
#              
#            self.Name = self.root_tag[About][Name].value
#            self.Author = self.root_tag[About][Author].value
#            self.CreatedOn = self.root_tag[About][CreatedOn].value



    def rotateLeft(self):
        MCLevel.rotateLeft(self);

        self.Data = swapaxes(self.Data, 1, 0)[:, ::-1, :]; #x=y; y=-x

        torchRotation = array([0, 4, 3, 1, 2, 5,
                               6, 7,

                               8, 9, 10, 11, 12, 13, 14, 15]);

        torchIndexes = (self.Blocks == self.materials.Torch.ID)
        info(u"Rotating torches: {0}".format(len(torchIndexes.nonzero()[0])))
        self.Data[torchIndexes] = torchRotation[self.Data[torchIndexes]]

    def decodePos(self, v):
        b = 10;
        m = (1 << b) - 1; return (v & m, (v >> b) & m, (v >> (2 * b)))
    def encodePos(self, x, y, z):
        b = 10;
        return x + (y << b) + (z << (2 * b))

    def saveToFile(self, filename=None):
        if filename == None: filename = self.filename;
        if filename == None:
            warn(u"Attempted to save an unnamed file in place")
            return; #you fool!

        self.Data <<= 4;
        self.Data |= (self.BlockLight & 0xf)

        self.Blocks = swapaxes(self.Blocks, 0, 2)
        self.Data = swapaxes(self.Data, 0, 2)

        mapTag = TAG_Compound(name=Map);
        mapTag[Width] = TAG_Short(self.Width);
        mapTag[Height] = TAG_Short(self.Height);
        mapTag[Length] = TAG_Short(self.Length);
        mapTag[Blocks] = TAG_Byte_Array(self.Blocks);
        mapTag[Data] = TAG_Byte_Array(self.Data);

        self.Blocks = swapaxes(self.Blocks, 0, 2)
        self.Data = swapaxes(self.Data, 0, 2)

        mapTag[Spawn] = TAG_List([TAG_Short(i) for i in self.Spawn])

        self.root_tag[Map] = mapTag;
        self.root_tag[Map]

        #fix up TileEntities imported from Alpha worlds.
        for ent in self.TileEntities:
            if "Pos" not in ent and all(c in ent for c in 'xyz'):
                ent["Pos"] = TAG_Int(self.encodePos(ent['x'].value, ent['y'].value, ent['z'].value))
        #output_file = gzip.open(self.filename, "wb", compresslevel=1)
        try:
            os.rename(filename, filename + ".old");
        except Exception, e:
            pass

        try:
            self.root_tag.saveGzipped(filename);
        except:
            os.rename(filename + ".old", filename);

        try: os.remove(filename + ".old");
        except Exception, e:
            pass

        self.BlockLight = self.Data & 0xf

        self.Data >>= 4

