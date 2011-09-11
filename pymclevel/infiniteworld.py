'''
Created on Jul 22, 2011

@author: Rio
'''
from mclevelbase import *
from collections import deque;
import time
import zlib
import struct
import shutil
import subprocess
import sys
import urllib
import tempfile

#infinite
Level = 'Level'
BlockData = 'BlockData'
BlockLight = 'BlockLight'
SkyLight = 'SkyLight'
HeightMap = 'HeightMap'
TerrainPopulated = 'TerrainPopulated'
LastUpdate = 'LastUpdate'
xPos = 'xPos'
zPos = 'zPos'

Data = 'Data'
SpawnX = 'SpawnX'
SpawnY = 'SpawnY'
SpawnZ = 'SpawnZ'
LastPlayed = 'LastPlayed'
RandomSeed = 'RandomSeed'
SizeOnDisk = 'SizeOnDisk' #maybe update this?
Time = 'Time'
Player = 'Player'

__all__ = ["ZeroChunk", "InfdevChunk", "MCInfdevOldLevel", "MCAlphaDimension", "ZipSchematic"]

def exhaust(_iter):
    i = 0
    for i in _iter:
        pass
    return i

import re

convert = lambda text: int(text) if text.isdigit() else text
alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
def sort_nicely(l):
    """ Sort the given list in the way that humans expect. 
    """
    l.sort(key=alphanum_key)

# Thank you, Stackoverflow
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, _fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

if sys.platform == "win32":
    appSupportDir = os.path.join(os.environ["APPDATA"], "pymclevel")
elif sys.platform == "darwin":
    appSupportDir = os.path.expanduser("~/Library/Application Support/pymclevel/")
else:
    appSupportDir = os.path.expanduser("~/.pymclevel")

class ServerJarStorage(object):
    defaultCacheDir = os.path.join(appSupportDir, "ServerJarStorage")

    def __init__(self, cacheDir=None):
        if cacheDir is None:
            cacheDir = self.defaultCacheDir

        self.cacheDir = cacheDir

        if not os.path.exists(self.cacheDir):
            os.makedirs(self.cacheDir)
        readme = os.path.join(self.cacheDir, "README.TXT")
        if not os.path.exists(readme):
            with file(readme, "w") as f:
                f.write("""
About this folder:

This folder is used by MCEdit and pymclevel to store different versions of the 
Minecraft Server to use for terrain generation. It should have one or more 
subfolders, one for each version of the server. Each subfolder must hold at
least one file named minecraft_server.jar, and the subfolder's name should 
have the server's version plus the names of any installed mods.

There may already be a subfolder here (for example, "Beta 1.7.3") if you have 
used the Chunk Create feature in MCEdit to create chunks using the server. 

Version numbers can be automatically detected. If you place one or more
minecraft_server.jar files in this folder, they will be placed automatically 
into well-named subfolders the next time you run MCEdit. If a file's name 
begins with "minecraft_server" and ends with ".jar", it will be detected in 
this way.
""")

        self.reloadVersions()

    def reloadVersions(self):
        cacheDirList = os.listdir(self.cacheDir)
        self.versions = list(reversed(sorted([v for v in cacheDirList if os.path.exists(self.jarfileForVersion(v))], key=alphanum_key)))

        for f in cacheDirList:
            p = os.path.join(self.cacheDir, f)
            if f.startswith("minecraft_server") and f.endswith(".jar") and os.path.isfile(p):
                print "Unclassified minecraft_server.jar found in cache dir. Discovering version number..."
                self.cacheNewVersion(p)
                os.remove(p)


        print "Minecraft_Server.jar storage initialized."
        print "Each server is stored in a subdirectory of {0} named with the server's version number".format(self.cacheDir)


        print "Cached servers: ", self.versions


    def downloadCurrentServer(self):
        print "Downloading the latest Minecraft Server..."
        try:
            (filename, headers) = urllib.urlretrieve("http://www.minecraft.net/download/minecraft_server.jar")
        except Exception, e:
            print "Error downloading server: {0!r}".format(e)
            return

        self.cacheNewVersion(filename)

    def cacheNewVersion(self, filename):
        """ Finds the version number from the server jar at filename and copies
        it into the proper subfolder of the server jar cache folder"""

        version = MCServerChunkGenerator._serverVersionFromJarFile(filename)
        print "Found version ", version
        versionDir = os.path.join(self.cacheDir, version)

        i = 1
        versionDir2 = versionDir
        while os.path.exists(versionDir2):
            versionDir2 = versionDir + str(i)
            i += 1

        os.mkdir(versionDir2)

        shutil.copy2(filename, os.path.join(versionDir, "minecraft_server.jar"))

        if version not in self.versions:
            self.versions.append(version)

    def jarfileForVersion(self, v):
        return os.path.join(self.cacheDir, v, "minecraft_server.jar")
    def checksumForVersion(self, v):
        jf = self.jarfileForVersion(v)
        with file(jf, "rb") as f:
            import md5
            return (md5.md5(f.read()).hexdigest())

    @property
    def latestVersion(self):
        if len(self.versions) == 0: return None
        return max(self.versions, key=alphanum_key)

    def getJarfile(self, version=None):
        if len(self.versions) == 0:
            print "No servers found in cache."
            self.downloadCurrentServer()

        version = version or self.latestVersion
        if version not in self.versions: return None
        return self.jarfileForVersion(version)

class JavaNotFound(RuntimeError): pass
class VersionNotFound(RuntimeError): pass

def readProperties(filename):
    with file(filename) as f:
        properties = dict((line.split("=", 2) for line in (l.strip() for l in f) if not line.startswith("#")))

    return properties

def saveProperties(filename, properties):
    with file(filename, "w") as f:
        for k, v in properties.iteritems():
            f.write("{0}={1}\n".format(k, v))

class MCServerChunkGenerator(object):
    """Generates chunks using minecraft_server.jar. Uses a ServerJarStorage to 
    store different versions of minecraft_server.jar in an application support
    folder. 
    
    
    
        from pymclevel import *
        
    Example usage:
        
        gen = MCServerChunkGenerator() # with no arguments, use the newest 
                                       # server version in the cache, or download
                                       # the newest one automatically
        level = loadWorldNamed("MyWorld")
        
        gen.generateChunkInLevel(level, 12, 24)
        
        
    Using an older version:
    
        gen = MCServerChunkGenerator("Beta 1.6.5")
        
    """
    defaultJarStorage = None

    if sys.platform == "win32":
        javaExe = which("java.exe")
    else:
        javaExe = which("java")

    jarStorage = None
    tempWorldCache = {}

    def __init__(self, version=None, jarfile=None, jarStorage=None):

        if self.__class__.defaultJarStorage is None:
            self.__class__.defaultJarStorage = ServerJarStorage()

        self.jarStorage = jarStorage or self.defaultJarStorage

        if self.javaExe is None:
            raise JavaNotFound, "Could not find java. Please check that java is installed correctly. (Could not find java in your PATH environment variable.)"
        if jarfile is None:
            jarfile = self.jarStorage.getJarfile(version)
        if jarfile is None:
            raise VersionNotFound, "Could not find minecraft_server.jar for version {0}. Please make sure that a minecraft_server.jar is placed under {1} in a subfolder named after the server's version number.".format(version or "(latest)", self.jarStorage.cacheDir)
        self.serverJarFile = jarfile
        self.serverVersion = self._serverVersion()

    @classmethod
    def clearWorldCache(cls):
        cls.tempWorldCache = {}

        for tempDir in os.listdir(cls.worldCacheDir):
            t = os.path.join(cls.worldCacheDir, tempDir)
            if os.path.isdir(t):
                shutil.rmtree(t)

    def createReadme(self):
        readme = os.path.join(self.worldCacheDir, "README.TXT")

        if not os.path.exists(readme):
            with file(readme, "w") as f:
                f.write("""
    About this folder:
    
    This folder is used by MCEdit and pymclevel to cache levels during terrain 
    generation. Feel free to delete it for any reason.
    """)

    worldCacheDir = os.path.join(tempfile.gettempdir(), "pymclevel_MCServerChunkGenerator")

    def tempWorldForLevel(self, level):

        #tempDir = tempfile.mkdtemp("mclevel_servergen")
        tempDir = os.path.join(self.worldCacheDir, self.jarStorage.checksumForVersion(self.serverVersion), str(level.RandomSeed))
        propsFile = os.path.join(tempDir, "server.properties")
        if os.path.exists(propsFile):
            properties = readProperties(propsFile)
        else:
            properties = {}

        if level.RandomSeed in self.tempWorldCache:
            tempWorld = self.tempWorldCache[level.RandomSeed]
        else:
            if not os.path.exists(tempDir):
                os.makedirs(tempDir)
                self.createReadme()

            worldName = "world"
            worldName = properties.setdefault("world-name", worldName)

            tempWorldDir = os.path.join(tempDir, worldName)
            tempWorld = MCInfdevOldLevel(tempWorldDir, create=True, random_seed=level.RandomSeed)
            del tempWorld.version # for compatibility with older servers. newer ones will set it again without issue.

            self.tempWorldCache[level.RandomSeed] = tempWorld


        if level.dimNo == 0:
            properties["allow-nether"] = "false"
        else:
            tempWorld = tempWorld.getDimension(level.dimNo)

            properties["allow-nether"] = "true"

        saveProperties(propsFile, properties)

        return (tempWorld, tempDir)

    def generateAtPosition(self, tempWorld, tempDir, cx, cz):
        tempWorld.setPlayerSpawnPosition((cx * 16, 64, cz * 16))
        tempWorld.saveInPlace()
        tempWorld.unloadRegions()

        proc = self.runServer(tempDir)
        self.waitForServer(proc)

        (tempWorld.parentWorld or tempWorld).loadLevelDat() #reload version number

    def copyChunkAtPosition(self, tempWorld, level, cx, cz):
        if level.containsChunk(cx, cz): return
        try:
            tempChunk = tempWorld.getChunk(cx, cz)
        except ChunkNotPresent, e:
            raise ChunkNotPresent, "While generating a world in {0} using server {1} ({2!r})".format(tempWorld, self.serverJarFile, e), sys.exc_traceback

        tempChunk.decompress()
        tempChunk.unpackChunkData()
        root_tag = tempChunk.root_tag

        if not level.containsChunk(cx, cz):
            level.createChunk(cx, cz)

        chunk = level.getChunk(cx, cz)
        chunk.decompress()
        chunk.unpackChunkData()
        chunk.root_tag = root_tag #xxx tag swap, could copy blocks and entities and chunk attrs instead?
        chunk.dirty = True

        chunk.compress()
        tempChunk.compress()


    def generateChunkInLevel(self, level, cx, cz):
        assert isinstance(level, MCInfdevOldLevel)

        tempWorld, tempDir = self.tempWorldForLevel(level)
        self.generateAtPosition(tempWorld, tempDir, cx, cz)
        self.copyChunkAtPosition(tempWorld, level, cx, cz)

    def generateChunksInLevel(self, level, chunks):
        return exhaust(self.generateChunksInLevelIter(level, chunks))

    def generateChunksInLevelIter(self, level, chunks):
        assert isinstance(level, MCInfdevOldLevel)
        tempWorld, tempDir = self.tempWorldForLevel(level)

        startRegionRadius = 7 #more recent servers use 12
        def inBox(cPos):
            x, z = cPos
            return (x > centercx - startRegionRadius
                and x < centercx + startRegionRadius
                and z > centercz - startRegionRadius
                and z < centercz + startRegionRadius)

        startLength = len(chunks)
        while len(chunks):
            centercx, centercz = chunks[0]

            boxedChunks = [cPos for cPos in chunks if inBox(cPos)]
            print "Generating {0} chunks out of {1} starting from {2}".format(len(boxedChunks), len(chunks), (centercx, centercz))
            yield startLength - len(chunks), startLength

            chunks = [c for c in chunks if not inBox(c)]

            self.generateAtPosition(tempWorld, tempDir, centercx, centercz)

            for cx, cz in boxedChunks:
                try:
                    self.copyChunkAtPosition(tempWorld, level, cx, cz)
                except ChunkNotPresent:
                    print "Failed to copy chunk", (cx, cz), "at a delta of ", (centercx - cx, centercz - cz), "from the last generation center."
                    raise


        level.saveInPlace()


    def waitForServer(self, proc):
        """ wait for the server to finish starting up, then stop it. """
        while proc.poll() is None:
            line = proc.stderr.readline()
            if "[INFO] Done" in line:
                proc.stdin.write("stop\n")
                proc.wait()
                break
            if "FAILED TO BIND" in line:
                proc.kill()
                proc.wait()
                raise RuntimeError, "Server Died!"

    def runServer(self, startingDir):
        return self._runServer(startingDir, self.serverJarFile)

    @classmethod
    def _runServer(cls, startingDir, jarfile):
        print "Starting server {0} in {1}".format(jarfile, startingDir)
        proc = subprocess.Popen([cls.javaExe, "-Xmx1024M", "-Xms1024M", "-jar", jarfile],
            executable=cls.javaExe,
            cwd=startingDir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            )
        return proc

    def _serverVersion(self):
        return self._serverVersionFromJarFile(self.serverJarFile)

    @classmethod
    def _serverVersionFromJarFile(cls, jarfile):
        tempdir = tempfile.mkdtemp("mclevel_servergen")
        proc = cls._runServer(tempdir, jarfile)

        version = "Unknown"
        #out, err = proc.communicate()
        #for line in err.split("\n"):

        while proc.poll() is None:
            line = proc.stderr.readline()
            if "Preparing start region" in line: break
            if "Starting minecraft server version" in line:
                version = line.split("Starting minecraft server version")[1].strip()
                break

        if proc.returncode is None:
            try:
                proc.kill()
            except WindowsError:
                pass #access denied, process already terminated

        proc.wait()
        shutil.rmtree(tempdir)

        return version


class ZeroChunk(object):
    " a placebo for neighboring-chunk routines "
    def compress(self): pass
    def load(self): pass
    def __init__(self, height=512):
        zeroChunk = zeros((16, 16, height), uint8)
        whiteLight = zeroChunk + 15;
        self.Blocks = zeroChunk
        self.BlockLight = whiteLight
        self.SkyLight = whiteLight
        self.Data = zeroChunk

class InfdevChunk(EntityLevel):
    """ This is a 16x16xH chunk in an (infinite) world.
    The properties Blocks, Data, SkyLight, BlockLight, and Heightmap 
    are ndarrays containing the respective blocks in the chunk file.
    Each array is indexed [x,z,y].  The Data, Skylight, and BlockLight 
    arrays are automatically unpacked from nibble arrays into byte arrays 
    for better handling.
    """
    @property
    def filename(self):
        if self.world.version:
            cx, cz = self.chunkPosition
            rx, rz = cx >> 5, cz >> 5
            rf = self.world.regionFiles[rx, rz]
            offset = rf.getOffset(cx & 0x1f, cz & 0x1f)
            return u"{region} index {index} sector {sector} format {format}".format(
                region=os.path.basename(self.world.regionFilename(rx, rz)),
                sector=offset >> 8,
                index=4 * ((cx & 0x1f) + ((cz & 0x1f) * 32)),
                format=["???", "gzip", "deflate"][self.compressMode])
        else:
            return self.chunkFilename
    def __init__(self, world, chunkPosition, create=False):
        self.world = world;
        #self.materials = self.world.materials
        self.chunkPosition = chunkPosition;
        self.chunkFilename = world.chunkFilename(*chunkPosition)
        #self.filename = "UNUSED" + world.chunkFilename(*chunkPosition);
        #self.filename = "REGION FILE (chunk {0})".format(chunkPosition)
        self.compressedTag = None
        self.root_tag = None
        self.dirty = False;
        self.needsLighting = False
        if self.world.version:
            self.compressMode = MCRegionFile.VERSION_DEFLATE
        else:
            self.compressMode = MCRegionFile.VERSION_GZIP


        if create:
            self.create();
        else:
            if not world.containsChunk(*chunkPosition):
                raise ChunkNotPresent("Chunk {0} not found", self.chunkPosition)

    @property
    def materials(self):
        return self.world.materials

    @classmethod
    def compressTagGzip(cls, root_tag):
        buf = StringIO()
        with closing(gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=2)) as gzipper:
            root_tag.save(buf=gzipper)

        return buf.getvalue()

    @classmethod
    def compressTagDeflate(cls, root_tag):
        buf = StringIO()
        root_tag.save(buf=buf)
        return deflate(buf.getvalue())

    def _compressChunk(self):
        root_tag = self.root_tag
        if root_tag is None: return

        if self.compressMode == MCRegionFile.VERSION_GZIP:
            self.compressedTag = self.compressTagGzip(root_tag)
        if self.compressMode == MCRegionFile.VERSION_DEFLATE:
            self.compressedTag = self.compressTagDeflate(root_tag)

        self.root_tag = None

    def decompressTagGzip(self, data):
        return nbt.load(buf=gunzip(data))

    def decompressTagDeflate(self, data):
        return nbt.load(buf=inflate(data))

    def _decompressChunk(self):
        data = self.compressedTag

        if self.compressMode == MCRegionFile.VERSION_GZIP:
            self.root_tag = self.decompressTagGzip(data)
        if self.compressMode == MCRegionFile.VERSION_DEFLATE:
            self.root_tag = self.decompressTagDeflate(data)


    def compressedSize(self):
        "return the size of the compressed data for this level, in bytes."
        self.compress();
        if self.compressedTag is None: return 0
        return len(self.compressedTag)


    def sanitizeBlocks(self):
        #change grass to dirt where needed so Minecraft doesn't flip out and die
        grass = self.Blocks == self.materials.Grass.ID
        grass |= self.Blocks == self.materials.Dirt.ID
        badgrass = grass[:, :, 1:] & grass[:, :, :-1]

        self.Blocks[:, :, :-1][badgrass] = self.materials.Dirt.ID

        #remove any thin snow layers immediately above other thin snow layers.
        #minecraft doesn't flip out, but it's almost never intended
        if hasattr(self.materials, "SnowLayer"):
            snowlayer = self.Blocks == self.materials.SnowLayer.ID
            badsnow = snowlayer[:, :, 1:] & snowlayer[:, :, :-1]

            self.Blocks[:, :, 1:][badsnow] = self.materials.Air.ID


    def compress(self):


        if not self.dirty:
            #if we are not dirty, just throw the 
            #uncompressed tag structure away. rely on the OS disk cache.
            self.root_tag = None
        else:
            if self.root_tag is not None:
                self.sanitizeBlocks() #xxx

            self.packChunkData()
            self._compressChunk()

        self.world.chunkDidCompress(self);

    def decompress(self):
        """called when accessing attributes decorated with @decompress_first"""
        if not self in self.world.decompressedChunkQueue:

            if self.root_tag != None: return
            if self.compressedTag is None:
                if self.root_tag is None:
                    self.load();
                else:
                    return;


            try:
                self._decompressChunk()

            except Exception, e:
                error(u"Malformed NBT data in file: {0} ({1})".format(self.filename, e))
                if self.world: self.world.malformedChunk(*self.chunkPosition);
                raise ChunkMalformed, self.filename

            try:
                self.shapeChunkData()
            except KeyError, e:
                error(u"Incorrect chunk format in file: {0} ({1})".format(self.filename, e))
                if self.world: self.world.malformedChunk(*self.chunkPosition);
                raise ChunkMalformed, self.filename

            self.dataIsPacked = True;
        self.world.chunkDidDecompress(self);


    def __str__(self):
        return u"InfdevChunk, coords:{0}, world: {1}, D:{2}, L:{3}".format(self.chunkPosition, self.world.displayName, self.dirty, self.needsLighting)

    def create(self):
        (cx, cz) = self.chunkPosition;
        chunkTag = nbt.TAG_Compound()
        chunkTag.name = ""
        levelTag = nbt.TAG_Compound()
        chunkTag[Level] = levelTag

        levelTag[TerrainPopulated] = TAG_Byte(1)
        levelTag[xPos] = TAG_Int(cx)
        levelTag[zPos] = TAG_Int(cz)

        levelTag[LastUpdate] = TAG_Long(0);

        levelTag[BlockLight] = TAG_Byte_Array()
        levelTag[BlockLight].value = zeros(16 * 16 * self.world.ChunkHeight / 2, uint8)

        levelTag[Blocks] = TAG_Byte_Array()
        levelTag[Blocks].value = zeros(16 * 16 * self.world.ChunkHeight, uint8)

        levelTag[Data] = TAG_Byte_Array()
        levelTag[Data].value = zeros(16 * 16 * self.world.ChunkHeight / 2, uint8)

        levelTag[SkyLight] = TAG_Byte_Array()
        levelTag[SkyLight].value = zeros(16 * 16 * self.world.ChunkHeight / 2, uint8)
        levelTag[SkyLight].value[:] = 255

        if self.world.ChunkHeight <= 128:
            levelTag[HeightMap] = TAG_Byte_Array()
            levelTag[HeightMap].value = zeros(16 * 16, uint8)
        else:
            levelTag[HeightMap] = TAG_Int_Array()
            levelTag[HeightMap].value = zeros(16 * 16, uint32).newbyteorder()


        levelTag[Entities] = TAG_List()
        levelTag[TileEntities] = TAG_List()

        #levelTag["Creator"] = TAG_String("MCEdit-" + release.release);

        #empty lists are seen in the wild with a list.TAG_type for a list of single bytes, 
        #even though these contain TAG_Compounds 

        self.root_tag = chunkTag
        self.shapeChunkData();
        self.dataIsPacked = True;

        self.dirty = True;
        self.save();

    def save(self):
        """ does not recalculate any data or light """
        self.compress()

        if self.dirty:
            debug(u"Saving chunk: {0}".format(self))
            self.world._saveChunk(self)

            debug(u"Saved chunk {0}".format(self))

            self.dirty = False;

    def load(self):
        """ If the chunk is unloaded, calls world._loadChunk to set root_tag and 
        compressedTag, then unpacks the chunk fully"""

        if self.root_tag is None and self.compressedTag is None:
            try:
                self.world._loadChunk(self)
                self.dataIsPacked = True;
                self.shapeChunkData()
                self.unpackChunkData()

            except Exception, e:
                error(u"Incorrect chunk format in file: {0} ({1})".format(self.filename, e))
                if self.world: self.world.malformedChunk(*self.chunkPosition);
                raise ChunkMalformed, self.filename

            self.world.chunkDidLoad(self)
            self.world.chunkDidDecompress(self);

    def unload(self):
        """ Frees the chunk's memory. Will not save to disk. Unloads completely
        if the chunk does not need to be saved."""
        self.compress();

        if not self.dirty:
            self.compressedTag = None;
            self.world.chunkDidUnload(self)

    def isLoaded(self):
        #we're loaded if we have our tag data in ram 
        #and we don't have to go back to the disk for it.
        return not (self.compressedTag is None and self.root_tag is None)

    def isCompressed(self):
        return self.isLoaded() and self.root_tag == None


    def chunkChanged(self, calcLighting=True):
        """ You are required to call this function after you are done modifying
        the chunk. Pass False for calcLighting if you know your changes will 
        not change any lights."""

        if self.compressedTag == None and self.root_tag == None:
            #unloaded chunk
            return;

        self.dirty = True;
        self.needsLighting = calcLighting or self.needsLighting;
        generateHeightMap(self);
        if calcLighting:
            self.genFastLights()

    def genFastLights(self):
        self.SkyLight[:] = 0;
        if self.world.dimNo == -1:
            return #no light in nether

        blocks = self.Blocks;
        la = self.world.materials.lightAbsorption
        skylight = self.SkyLight;
        heightmap = self.HeightMap;

        for x, z in itertools.product(xrange(16), xrange(16)):

            skylight[x, z, heightmap[z, x]:] = 15
            lv = 15;
            for y in reversed(range(heightmap[z, x])):
                lv -= (la[blocks[x, z, y]] or 1)

                if lv <= 0:
                    break;
                skylight[x, z, y] = lv;



    def unpackChunkData(self):
        if not self.dataIsPacked: return
        """ for internal use.  call getChunk and compressChunk to load, compress, and unpack chunks automatically """
        for key in (SkyLight, BlockLight, Data):
            dataArray = self.root_tag[Level][key].value
            s = dataArray.shape
            assert s[2] == self.world.ChunkHeight / 2;
            #unpackedData = insert(dataArray[...,newaxis], 0, 0, 3)  

            unpackedData = zeros((s[0], s[1], s[2] * 2), dtype='uint8')

            unpackedData[:, :, ::2] = dataArray
            unpackedData[:, :, ::2] &= 0xf
            unpackedData[:, :, 1::2] = dataArray
            unpackedData[:, :, 1::2] >>= 4




            self.root_tag[Level][key].value = unpackedData
            self.dataIsPacked = False;

    def packChunkData(self):
        if self.dataIsPacked: return

        if self.root_tag is None:
            warn(u"packChunkData called on unloaded chunk: {0}".format(self.chunkPosition))
            return;
        for key in (SkyLight, BlockLight, Data):
            dataArray = self.root_tag[Level][key].value
            assert dataArray.shape[2] == self.world.ChunkHeight;

            unpackedData = self.root_tag[Level][key].value.reshape(16, 16, self.world.ChunkHeight / 2, 2)
            unpackedData[..., 1] <<= 4
            unpackedData[..., 1] |= unpackedData[..., 0]
            self.root_tag[Level][key].value = array(unpackedData[:, :, :, 1])

            self.dataIsPacked = True;

    def shapeChunkData(self):
        """Applies the chunk shape to all of the data arrays 
        in the chunk tag.  used by chunk creation and loading"""
        chunkTag = self.root_tag

        chunkSize = 16
        chunkTag[Level][Blocks].value.shape = (chunkSize, chunkSize, self.world.ChunkHeight)
        chunkTag[Level][HeightMap].value.shape = (chunkSize, chunkSize);
        chunkTag[Level][SkyLight].value.shape = (chunkSize, chunkSize, self.world.ChunkHeight / 2)
        chunkTag[Level][BlockLight].value.shape = (chunkSize, chunkSize, self.world.ChunkHeight / 2)
        chunkTag[Level]["Data"].value.shape = (chunkSize, chunkSize, self.world.ChunkHeight / 2)
        if TileEntities not in chunkTag[Level]:
            chunkTag[Level][TileEntities] = TAG_List();
        if Entities not in chunkTag[Level]:
            chunkTag[Level][Entities] = TAG_List();

    def removeEntitiesInBox(self, box):
        self.dirty = True;
        return super(InfdevChunk, self).removeEntitiesInBox(box)

    def removeTileEntitiesInBox(self, box):
        self.dirty = True;
        return super(InfdevChunk, self).removeTileEntitiesInBox(box)


    @property
    @decompress_first
    def Blocks(self):
        return self.root_tag[Level][Blocks].value

    @property
    @decompress_first
    @unpack_first
    def Data(self):
        return self.root_tag[Level][Data].value

    @property
    @decompress_first
    def HeightMap(self):
        return self.root_tag[Level][HeightMap].value

    @property
    @decompress_first
    @unpack_first
    def SkyLight(self):
        return self.root_tag[Level][SkyLight].value

    @property
    @decompress_first
    @unpack_first
    def BlockLight(self):
        return self.root_tag[Level][BlockLight].value

    @property
    @decompress_first
    def Entities(self):
        return self.root_tag[Level][Entities]

    @property
    @decompress_first
    def TileEntities(self):
        return self.root_tag[Level][TileEntities]

    @property
    @decompress_first
    def TerrainPopulated(self):
        return self.root_tag[Level]["TerrainPopulated"].value;
    @TerrainPopulated.setter
    @decompress_first
    def TerrainPopulated(self, val):
        """True or False. If False, the game will populate the chunk with 
        ores and vegetation on next load"""
        self.root_tag[Level]["TerrainPopulated"].value = val;

def generateHeightMap(self):
    self.load();

    blocks = self.Blocks
    heightMap = self.HeightMap
    heightMap[:] = 0;

    lightAbsorption = self.world.materials.lightAbsorption[blocks]
    axes = lightAbsorption.nonzero()
    heightMap[axes[1], axes[0]] = axes[2]; #assumes the y-indices come out in increasing order
    heightMap += 1;


class dequeset(object):
    def __init__(self):
        self.deque = deque();
        self.set = set();

    def __contains__(self, obj):
        return obj in self.set;

    def __len__(self):
        return len(self.set);

    def append(self, obj):
        self.deque.append(obj);
        self.set.add(obj);

    def discard(self, obj):
        if obj in self.set:
            self.deque.remove(obj);
        self.set.discard(obj);


    def __getitem__(self, idx):
        return self.deque[idx];

from contextlib import contextmanager

@contextmanager
def notclosing(f):
    yield f;

class MCRegionFile(object):
    holdFileOpen = False #if False, reopens and recloses the file on each access


    @property
    def file(self):
        openfile = lambda:file(self.path, "rb+")
        if MCRegionFile.holdFileOpen:
            if self._file is None:
                self._file = openfile()
            return notclosing(self._file)
        else:
            return openfile()

    def close(self):
        if MCRegionFile.holdFileOpen:
            self._file.close()
            self._file = None

    def __init__(self, path, regionCoords):
        self.path = path
        self.regionCoords = regionCoords
        self._file = None
        if not os.path.exists(path):
            file(path, "w").close()

        with self.file as f:

            filesize = os.path.getsize(path)
            if filesize & 0xfff:
                filesize = (filesize | 0xfff) + 1
                f.truncate(filesize)

            if filesize == 0:
                filesize = self.SECTOR_BYTES * 2
                f.truncate(filesize)


            f.seek(0)
            offsetsData = f.read(self.SECTOR_BYTES)
            modTimesData = f.read(self.SECTOR_BYTES)

            self.freeSectors = [True] * (filesize / self.SECTOR_BYTES)
            self.freeSectors[0:2] = False, False

            self.offsets = fromstring(offsetsData, dtype='>u4')
            self.modTimes = fromstring(modTimesData, dtype='>u4')

        needsRepair = False

        for offset in self.offsets:
            sector = offset >> 8
            count = offset & 0xff

            for i in xrange(sector, sector + count):
                if i >= len(self.freeSectors):
                    #raise RegionMalformed, "Region file offset table points to sector {0} (past the end of the file)".format(i)
                    print  "Region file offset table points to sector {0} (past the end of the file)".format(i)
                    needsRepair = True
                    break
                if self.freeSectors[i] is False:
                    needsRepair = True
                self.freeSectors[i] = False

        if needsRepair:
            self.repair()

        info("Found region file {file} with {used}/{total} sectors used and {chunks} chunks present".format(
             file=os.path.basename(path), used=len(self.freeSectors) - sum(self.freeSectors), total=len(self.freeSectors), chunks=sum(self.offsets > 0)))

    def repair(self):
        lostAndFound = {}
        _freeSectors = [True] * len(self.freeSectors)
        _freeSectors[0] = _freeSectors[1] = False
        deleted = 0
        recovered = 0
        info("Beginning repairs on {file} ({chunks} chunks)".format(file=os.path.basename(self.path), chunks=sum(self.offsets > 0)))
        rx, rz = self.regionCoords
        for index, offset in enumerate(self.offsets):
            if offset:
                cx = index & 0x1f
                cz = index >> 5
                cx += rx << 5
                cz += rz << 5
                sectorStart = offset >> 8
                sectorCount = offset & 0xff
                try:

                    if sectorStart + sectorCount > len(self.freeSectors):
                        raise RegionMalformed, "Offset {start}:{end} ({offset}) at index {index} pointed outside of the file".format(
                            start=sectorStart, end=sectorStart + sectorCount, index=index, offset=offset)

                    compressedData = self._readChunk(cx, cz)
                    if compressedData is None:
                        raise RegionMalformed, "Failed to read chunk data for {0}".format((cx, cz))

                    format, data = self.decompressSectors(compressedData)
                    chunkTag = nbt.load(buf=data)
                    lev = chunkTag["Level"]
                    xPos = lev["xPos"].value
                    zPos = lev["zPos"].value
                    overlaps = False

                    for i in xrange(sectorStart, sectorStart + sectorCount):
                        if _freeSectors[i] is False:
                            overlaps = True
                        _freeSectors[i] = False


                    if xPos != cx or zPos != cz or overlaps:
                        lostAndFound[xPos, zPos] = (format, compressedData)

                        if (xPos, zPos) != (cx, cz):
                            raise RegionMalformed, "Chunk {found} was found in the slot reserved for {expected}".format(found=(xPos, zPos), expected=(cx, cz))
                        else:
                            raise RegionMalformed, "Chunk {found} (in slot {expected}) has overlapping sectors with another chunk!".format(found=(xPos, zPos), expected=(cx, cz))



                except Exception, e:
                    info("Unexpected chunk data at sector {sector} ({exc})".format(sector=sectorStart, exc=e))
                    self.setOffset(cx, cz, 0)
                    deleted += 1

        for cPos, (format, foundData) in lostAndFound.iteritems():
            cx, cz = cPos
            if self.getOffset(cx, cz) == 0:
                info("Found chunk {found} and its slot is empty, recovering it".format(found=cPos))
                self._saveChunk(cx, cz, foundData[5:], format)
                recovered += 1

        info("Repair complete. Removed {0} chunks, recovered {1} chunks, net {2}".format(deleted, recovered, recovered - deleted))

    def extractAllChunks(self, folder):
        if not os.path.exists(folder):
            os.mkdir(folder)
        for cx, cz in itertools.product(range(32), range(32)):
            sectors = self._readChunk(cx, cz)
            if sectors is not None:
                format, compressedData = self.unpackSectors(sectors)
                data = self._decompressSectors(format, compressedData)
                chunkTag = nbt.load(buf=data)
                lev = chunkTag["Level"]
                xPos = lev["xPos"].value
                zPos = lev["zPos"].value
                gzdata = InfdevChunk.compressTagGzip(chunkTag)
                #print chunkTag.pretty_string()

                with file(os.path.join(folder, "c.{0}.{1}.dat".format(base36(xPos), base36(zPos))), "wb") as f:
                    f.write(gzdata)

    def _readChunk(self, cx, cz):
        cx &= 0x1f
        cz &= 0x1f
        offset = self.getOffset(cx, cz)
        if offset == 0: return None

        sectorStart = offset >> 8
        numSectors = offset & 0xff
        if numSectors == 0: return None

        if sectorStart + numSectors > len(self.freeSectors):
            return None

        with self.file as f:
            f.seek(sectorStart * self.SECTOR_BYTES)
            data = f.read(numSectors * self.SECTOR_BYTES)
        assert(len(data) > 0)
        #debug("REGION LOAD {0},{1} sector {2}".format(cx, cz, sectorStart))
        return data

    def loadChunk(self, chunk):
        cx, cz = chunk.chunkPosition

        data = self._readChunk(cx, cz)
        if data is None: raise ChunkNotPresent, (cx, cz, self)
        chunk.compressedTag = data[5:]

        format, data = self.decompressSectors(data)
        chunk.root_tag = nbt.load(buf=data)
        chunk.compressMode = format

    def unpackSectors(self, data):
        length = struct.unpack_from(">I", data)[0]
        format = struct.unpack_from("B", data, 4)[0]
        data = data[5:length + 5]
        return (format, data)

    def _decompressSectors(self, format, data):
        if format == self.VERSION_GZIP:
            return gunzip(data)
        if format == self.VERSION_DEFLATE:
            return inflate(data)

        raise IOError, "Unknown compress format: {0}".format(format)

    def decompressSectors(self, data):
        format, data = self.unpackSectors(data)
        return format, self._decompressSectors(format, data)


    def saveChunk(self, chunk):
        cx, cz = chunk.chunkPosition
        data = chunk.compressedTag
        format = chunk.compressMode

        self._saveChunk(cx, cz, data, format)

    def _saveChunk(self, cx, cz, data, format):
        cx &= 0x1f
        cz &= 0x1f
        offset = self.getOffset(cx, cz)
        sectorNumber = offset >> 8
        sectorsAllocated = offset & 0xff


        sectorsNeeded = (len(data) + self.CHUNK_HEADER_SIZE) / self.SECTOR_BYTES + 1;
        if sectorsNeeded >= 256: return

        if (sectorNumber != 0 and sectorsAllocated >= sectorsNeeded):
            debug("REGION SAVE {0},{1} rewriting {2}b".format(cx, cz, len(data)))
            self.writeSector(sectorNumber, data, format)
        else:
            # we need to allocate new sectors

            # mark the sectors previously used for this chunk as free 
            for i in xrange(sectorNumber, sectorNumber + sectorsAllocated):
                self.freeSectors[i] = True

            runLength = 0
            try:
                runStart = self.freeSectors.index(True)

                for i in range(runStart, len(self.freeSectors)):
                    if runLength:
                        if self.freeSectors[i]:
                            runLength += 1
                        else:
                            runLength = 0
                    elif self.freeSectors[i]:
                        runStart = i
                        runLength = 1

                    if runLength >= sectorsNeeded:
                        break
            except ValueError:
                pass

            # we found a free space large enough
            if runLength >= sectorsNeeded:
                debug("REGION SAVE {0},{1}, reusing {2}b".format(cx, cz, len(data)))
                sectorNumber = runStart
                self.setOffset(cx, cz, sectorNumber << 8 | sectorsNeeded)
                self.writeSector(sectorNumber, data, format)
                self.freeSectors[sectorNumber:sectorNumber + sectorsNeeded] = [False] * sectorsNeeded

            else:
                # no free space large enough found -- we need to grow the
                # file

                debug("REGION SAVE {0},{1}, growing by {2}b".format(cx, cz, len(data)))

                with self.file as f:
                    f.seek(0, 2)
                    filesize = f.tell()

                    sectorNumber = len(self.freeSectors)

                    assert sectorNumber * self.SECTOR_BYTES == filesize

                    filesize += sectorsNeeded * self.SECTOR_BYTES
                    f.truncate(filesize)

                self.freeSectors += [False] * sectorsNeeded

                self.setOffset(cx, cz, sectorNumber << 8 | sectorsNeeded)
                self.writeSector(sectorNumber, data, format)


    def writeSector(self, sectorNumber, data, format):
        with self.file as f:
            debug("REGION: Writing sector {0}".format(sectorNumber))

            f.seek(sectorNumber * self.SECTOR_BYTES)
            f.write(struct.pack(">I", len(data) + 1));# // chunk length
            f.write(struct.pack("B", format));# // chunk version number
            f.write(data);# // chunk data
            #f.flush()


    def getOffset(self, cx, cz):
        cx &= 0x1f;
        cz &= 0x1f
        return self.offsets[cx + cz * 32]

    def setOffset(self, cx, cz, offset):
        cx &= 0x1f;
        cz &= 0x1f
        self.offsets[cx + cz * 32] = offset
        with self.file as f:
            f.seek(0)
            f.write(self.offsets.tostring())



    SECTOR_BYTES = 4096
    SECTOR_INTS = SECTOR_BYTES / 4
    CHUNK_HEADER_SIZE = 5;
    VERSION_GZIP = 1
    VERSION_DEFLATE = 2

    compressMode = VERSION_DEFLATE

base36alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
def decbase36(s):
    return int(s, 36)

def base36(n):
    global base36alphabet

    n = int(n);
    if 0 == n: return '0'
    neg = "";
    if n < 0:
        neg = "-"
        n = -n;

    work = []

    while(n):
        n, digit = divmod(n, 36)
        work.append(base36alphabet[digit])

    return neg + ''.join(reversed(work))


def deflate(data):
    #zobj = zlib.compressobj(6,zlib.DEFLATED,-zlib.MAX_WBITS,zlib.DEF_MEM_LEVEL,0)
    #zdata = zobj.compress(data)
    #zdata += zobj.flush()
    #return zdata
    return zlib.compress(data)
def inflate(data):
    return zlib.decompress(data)

class MCInfdevOldLevel(EntityLevel):
    materials = alphaMaterials;
    isInfinite = True
    parentWorld = None;
    dimNo = 0;
    ChunkHeight = 128


    @property
    def displayName(self):
        #shortname = os.path.basename(self.filename);
        #if shortname == "level.dat":
        shortname = os.path.basename(os.path.dirname(self.filename))

        return shortname

    @classmethod
    def _isLevel(cls, filename):
        if os.path.isdir(filename):
            files = os.listdir(filename);
            if "level.dat" in files or "level.dat_old" in files:
                return True;
        elif os.path.basename(filename) in ("level.dat", "level.dat_old"):
            return True;

        return False

    def getWorldBounds(self):
        if self.chunkCount == 0:
            return BoundingBox((0, 0, 0), (0, 0, 0))

        allChunksArray = array(list(self.allChunks), dtype='int32')
        mincx = min(allChunksArray[:, 0])
        maxcx = max(allChunksArray[:, 0])
        mincz = min(allChunksArray[:, 1])
        maxcz = max(allChunksArray[:, 1])

        origin = (mincx << 4, 0, mincz << 4)
        size = ((maxcx - mincx + 1) << 4, self.Height, (maxcz - mincz + 1) << 4)

        return BoundingBox(origin, size)


    def __str__(self):
        return "MCInfdevOldLevel(\"" + os.path.split(self.worldDir)[1] + "\")"

    def TagProperty(tagName, tagType, defaultValueFunc=lambda self:None):
        def getter(self):
            if tagName not in self.root_tag[Data]:
                self.root_tag[Data][tagName] = tagType(defaultValueFunc(self))
            return self.root_tag[Data][tagName].value

        def setter(self, val):
            self.root_tag[Data][tagName] = tagType(value=val)

        return property(getter, setter)

    SizeOnDisk = TagProperty('SizeOnDisk', TAG_Long)
    RandomSeed = TagProperty('RandomSeed', TAG_Long)
    Time = TagProperty('Time', TAG_Long); """ Age of the world in ticks. 20 ticks per second; 24000 ticks per day."""
    LastPlayed = TagProperty('LastPlayed', TAG_Long, lambda self:long(time.time() * 1000))

    LevelName = TagProperty('LevelName', TAG_String, lambda self:self.displayName)

    _bounds = None
    @property
    def bounds(self):
        if self._bounds is None: self._bounds = self.getWorldBounds();
        return self._bounds

    @property
    def size(self):
        return self.bounds.size

    def close(self):
        for rf in (self.regionFiles or {}).values():
            rf.close();

        self.regionFiles = {}

    def create(self, filename, random_seed, last_played):

        if filename == None:
            raise ValueError, "Can't create an Infinite level without a filename!"
        #create a new level
        root_tag = TAG_Compound();
        root_tag[Data] = TAG_Compound();
        root_tag[Data][SpawnX] = TAG_Int(0)
        root_tag[Data][SpawnY] = TAG_Int(2)
        root_tag[Data][SpawnZ] = TAG_Int(0)

        if last_played is None:
            last_played = long(time.time() * 1000)
        if random_seed is None:
            random_seed = long(random.random() * 0xffffffffffffffffL) - 0x8000000000000000L

        self.root_tag = root_tag;
        root_tag[Data]['version'] = TAG_Int(19132)

        self.LastPlayed = long(last_played)
        self.RandomSeed = long(random_seed)
        self.SizeOnDisk = 0
        self.Time = 1
        self.LevelName = os.path.basename(self.worldDir)

        ### if singleplayer:

        self.createPlayer("Player")

        if not os.path.exists(self.worldDir):
            os.mkdir(self.worldDir)



    def createPlayer(self, playerName):
        if playerName == "Player":
            playerTag = self.root_tag[Data].setdefault(playerName, TAG_Compound())
        else:
            playerTag = TAG_Compound()

        playerTag['Air'] = TAG_Short(300);
        playerTag['AttackTime'] = TAG_Short(0)
        playerTag['DeathTime'] = TAG_Short(0);
        playerTag['Fire'] = TAG_Short(-20);
        playerTag['Health'] = TAG_Short(20);
        playerTag['HurtTime'] = TAG_Short(0);
        playerTag['Score'] = TAG_Int(0);
        playerTag['FallDistance'] = TAG_Float(0)
        playerTag['OnGround'] = TAG_Byte(0)

        playerTag['Inventory'] = TAG_List()

        playerTag['Motion'] = TAG_List([TAG_Double(0) for i in range(3)])
        playerTag['Pos'] = TAG_List([TAG_Double([0.5, 2.8, 0.5][i]) for i in range(3)])
        playerTag['Rotation'] = TAG_List([TAG_Float(0), TAG_Float(0)])

        if playerName != "Player":
            self.playerTagCache.save(self.getPlayerPath(playerName))

    def __init__(self, filename=None, create=False, random_seed=None, last_played=None):
        """
        Load an Alpha level from the given filename. It can point to either
        a level.dat or a folder containing one. If create is True, it will
        also create the world using the random_seed and last_played arguments.
        If they are none, a random 64-bit seed will be selected for RandomSeed
        and long(time.time()*1000) will be used for LastPlayed.
        
        If you try to create an existing world, its level.dat will be replaced.
        """

        self.Length = 0
        self.Width = 0
        self.Height = 128 #subject to change?
        self.playerTagCache = {}

        if not os.path.exists(filename):
            if not create:
                raise IOError, 'File not found'

            self.worldDir = filename
            os.mkdir(self.worldDir)

        if os.path.isdir(filename):
            self.worldDir = filename

        else:
            if os.path.basename(filename) in ("level.dat", "level.dat_old"):
                self.worldDir = os.path.dirname(filename)
            else:
                raise IOError, 'File is not a Minecraft Alpha world'

        self.filename = os.path.join(self.worldDir, "level.dat")
        self.regionDir = os.path.join(self.worldDir, "region")
        if not os.path.exists(self.regionDir):
            os.mkdir(self.regionDir)

        #maps (cx,cz) pairs to InfdevChunks    
        self._loadedChunks = {}
        self._allChunks = None
        self.dimensions = {};
        self.regionFiles = {}

        #used to limit memory usage
        self.loadedChunkQueue = dequeset()
        self.decompressedChunkQueue = dequeset()

        self.loadLevelDat(create, random_seed, last_played);

        #attempt to support yMod
        try:
            self.ChunkHeight = self.root_tag["Data"]["YLimit"].value
            self.Height = self.ChunkHeight
        except:
            pass

        self.playersDir = os.path.join(self.worldDir, "players");

        if os.path.isdir(self.playersDir):
            self.players = [x[:-4] for x in os.listdir(self.playersDir) if x.endswith(".dat")]



        self.preloadDimensions();
        #self.preloadChunkPositions();

    def loadLevelDat(self, create=False, random_seed=None, last_played=None):

        if create:
            self.create(self.filename, random_seed, last_played);
            self.saveInPlace();
        else:
            try:
                self.root_tag = nbt.load(self.filename)
            except Exception, e:
                filename_old = os.path.join(self.worldDir, "level.dat_old")
                info("Error loading level.dat, trying level.dat_old ({0})".format(e))
                try:
                    self.root_tag = nbt.load(filename_old)
                    info("level.dat restored from backup.")
                    self.saveInPlace();
                except Exception, e:
                    traceback.print_exc()
                    print repr(e)
                    info("Error loading level.dat_old. Initializing with defaults.");
                    self.create(self.filename, random_seed, last_played);

    def preloadDimensions(self):
        worldDirs = os.listdir(self.worldDir);

        for dirname in worldDirs :
            if dirname.startswith("DIM"):
                try:
                    dimNo = int(dirname[3:]);
                    info("Found dimension {0}".format(dirname))
                    dim = MCAlphaDimension(self, dimNo);
                    self.dimensions[dimNo] = dim;
                except Exception, e:
                    error(u"Error loading dimension {0}: {1}".format(dirname, e))

    def getDimension(self, dimNo):
        if self.dimNo != 0:
            return self.parentWorld.getDimension(dimNo)

        if dimNo == 0:
            return self

        if dimNo in self.dimensions: return self.dimensions[dimNo]
        dim = MCAlphaDimension(self, dimNo, create=True)
        self.dimensions[dimNo] = dim
        return dim


    def getRegionForChunk(self, cx, cz):
        rx = cx >> 5
        rz = cz >> 5
        return self.getRegionFile(rx, rz)

    def preloadChunkPositions(self):
        if self.version == 19132:
            self.preloadRegions()
        else:
            self.preloadChunkPaths()

    def findRegionFiles(self):
        regionDir = os.path.join(self.worldDir, "region")
        if not os.path.exists(regionDir):
            os.mkdir(regionDir)

        regionFiles = os.listdir(regionDir)
        for filename in regionFiles:
            yield os.path.join(regionDir, filename)

    def loadRegionFile(self, filepath):
        filename = os.path.basename(filepath)
        bits = filename.split('.')
        if len(bits) < 4 or bits[0] != 'r' or bits[3] != "mcr": return None

        try:
            rx, rz = map(int, bits[1:3])
        except ValueError:
            return None

        return MCRegionFile(filepath, (rx, rz))

    def getRegionFile(self, rx, rz):
        regionFile = self.regionFiles.get((rx, rz))
        if regionFile: return regionFile
        regionFile = MCRegionFile(self.regionFilename(rx, rz), (rx, rz))
        self.regionFiles[rx, rz] = regionFile;
        return regionFile

    def unloadRegions(self):
        self.regionFiles = {}
        self._allChunks = None

    def preloadRegions(self):
        info(u"Scanning for regions...")
        self._allChunks = set()

        for filepath in self.findRegionFiles():
            regionFile = self.loadRegionFile(filepath)
            if regionFile is None: continue

            if regionFile.offsets.any():
                rx, rz = regionFile.regionCoords
                self.regionFiles[rx, rz] = regionFile

                for index, offset in enumerate(regionFile.offsets):
                    if offset:
                        cx = index & 0x1f
                        cz = index >> 5

                        cx += rx << 5
                        cz += rz << 5

                        self._allChunks.add((cx, cz))
            else:
                info(u"Removing empty region file {0}".format(filepath))
                regionFile.close()
                os.unlink(regionFile.path)



    def preloadChunkPaths(self):



        info(u"Scanning for chunks...")
        worldDirs = os.listdir(self.worldDir);
        self._allChunks = set()

        for dirname in worldDirs:
            if(dirname in self.dirhashes):
                subdirs = os.listdir(os.path.join(self.worldDir, dirname));
                for subdirname in subdirs:
                    if(subdirname in self.dirhashes):
                        filenames = os.listdir(os.path.join(self.worldDir, dirname, subdirname));
                        #def fullname(filename):
                            #return os.path.join(self.worldDir, dirname, subdirname, filename);

                        #fullpaths = map(fullname, filenames);
                        bits = map(lambda x:x.split('.'), filenames);

                        chunkfilenames = filter(lambda x:(len(x) == 4 and x[0].lower() == 'c' and x[3].lower() == 'dat'), bits)

                        for c in chunkfilenames:
                            try:
                                cx, cz = (decbase36(c[1]), decbase36(c[2]))
                            except Exception, e:
                                info(u'Skipped file {0} ({1})'.format(u'.'.join(c), e))
                                continue

                            self._allChunks.add((cx, cz))

                            #

        info(u"Found {0} chunks.".format(len(self._allChunks)))

    def compress(self):
        self.compressAllChunks();

    def compressAllChunks(self):
        for ch in self._loadedChunks.itervalues():
            ch.compress();

    def compressChunk(self, cx, cz):
        if not (cx, cz) in self._loadedChunks: return; #not an error
        self._loadedChunks[cx, cz].compress()

    decompressedChunkLimit = 2048 # about 320 megabytes
    loadedChunkLimit = 8192 # from 8mb to 800mb depending on chunk contents


    def chunkDidCompress(self, chunk):
        self.decompressedChunkQueue.discard(chunk)

    def chunkDidDecompress(self, chunk):
        if not chunk in self.decompressedChunkQueue:
            self.decompressedChunkQueue.append(chunk);
            if self.decompressedChunkLimit and (len(self.decompressedChunkQueue) > self.decompressedChunkLimit):
                oldestChunk = self.decompressedChunkQueue[0];
                oldestChunk.compress(); #calls chunkDidCompress

    def chunkDidUnload(self, chunk):
        self.loadedChunkQueue.discard(chunk)

    def chunkDidLoad(self, chunk):
        if not chunk in self.loadedChunkQueue:
            self.loadedChunkQueue.append(chunk);
            if self.loadedChunkLimit and (len(self.loadedChunkQueue) > self.loadedChunkLimit):
                oldestChunk = self.loadedChunkQueue[0];
                oldestChunk.unload(); #calls chunkDidUnload

    @property
    @decompress_first
    def version(self):
        if 'version' in self.root_tag['Data']:
            return self.root_tag['Data']['version'].value
        else:
            return None

    @version.setter
    @decompress_first
    def version(self, val):
        if 'version' in self.root_tag['Data']:
            self.root_tag['Data']['version'].value = val


    @version.deleter
    @decompress_first
    def version(self):
        self.root_tag['Data'].pop('version')

    def _loadChunk(self, chunk):
        """ load the chunk data from disk, and set the chunk's compressedTag
         and root_tag"""

        cx, cz = chunk.chunkPosition
        try:
            if self.version:
                regionFile = self.getRegionForChunk(cx, cz)
                regionFile.loadChunk(chunk)

            else:
                with file(chunk.filename, 'rb') as f:
                    cdata = f.read()
                    chunk.compressedTag = cdata
                    data = gunzip(cdata)
                    chunk.root_tag = nbt.load(buf=data)

        except Exception, e:
            raise ChunkMalformed, "Chunk {0} had an error: {1!r}".format(chunk.chunkPosition, e)


    def _saveChunk(self, chunk):
        cx, cz = chunk.chunkPosition
        if self.version:
            regionFile = self.getRegionForChunk(cx, cz)

            regionFile.saveChunk(chunk)
        else:
            dir1 = os.path.dirname(chunk.filename)
            dir2 = os.path.dirname(dir1)

            if not os.path.exists(dir2):
                os.mkdir(dir2)
            if not os.path.exists(dir1):
                os.mkdir(dir1)

            chunk.compress()
            with file(chunk.filename, 'wb') as f:
                f.write(chunk.compressedTag)

    def discardAllChunks(self):
        """ clear lots of memory, fast. """

    def chunkFilenameAt(self, x, y, z):
        cx = x >> 4
        cz = z >> 4
        return self._loadedChunks.get((cx, cz)).filename


    def dirhash(self, n):
        return self.dirhashes[n % 64];

    def _dirhash(self):
        n = self
        n = n % 64;
        s = u"";
        if(n >= 36):
            s += u"1";
            n -= 36;
        s += u"0123456789abcdefghijklmnopqrstuvwxyz"[n]

        return s;

    dirhashes = [_dirhash(n) for n in range(64)];

    def regionFilename(self, rx, rz):
        s = os.path.join(self.regionDir,
                                     "r.%s.%s.mcr" % ((rx), (rz)));
        return s;

    def chunkFilename(self, x, z):
        s = os.path.join(self.worldDir, self.dirhash(x), self.dirhash(z),
                                     "c.%s.%s.dat" % (base36(x), base36(z)));
        return s;

    def extractChunksInBox(self, box, parentFolder):
        for cx, cz in box.chunkPositions:
            if self.containsChunk(cx, cz):
                self.extractChunk(cx, cz, parentFolder)

    def extractChunk(self, cx, cz, parentFolder):
        if not os.path.exists(parentFolder):
            os.mkdir(parentFolder)

        chunkFilename = self.chunkFilename(cx, cz)
        outputFile = os.path.join(parentFolder, os.path.basename(chunkFilename))

        chunk = self.getChunk(cx, cz)
        if chunk.compressMode == MCRegionFile.VERSION_GZIP:
            chunk.compress()
            data = chunk.compressedTag;
        else:
            chunk.decompress()
            data = chunk.compressTagGzip(chunk.root_tag)

        with file(outputFile, "wb") as f:
            f.write(data)


    def blockLightAt(self, x, y, z):
        if y < 0 or y >= self.Height: return 0
        zc = z >> 4
        xc = x >> 4

        xInChunk = x & 0xf;
        zInChunk = z & 0xf;
        ch = self.getChunk(xc, zc)

        return ch.BlockLight[xInChunk, zInChunk, y]


    def setBlockLightAt(self, x, y, z, newLight):
        if y < 0 or y >= self.Height: return 0
        zc = z >> 4
        xc = x >> 4

        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        ch = self.getChunk(xc, zc)
        ch.BlockLight[xInChunk, zInChunk, y] = newLight
        ch.chunkChanged(False)

    def blockDataAt(self, x, y, z):
        if y < 0 or y >= self.Height: return 0
        zc = z >> 4
        xc = x >> 4

        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        try:
            ch = self.getChunk(xc, zc)
        except ChunkNotPresent:
            return 0

        return ch.Data[xInChunk, zInChunk, y]


    def setBlockDataAt(self, x, y, z, newdata):
        if y < 0 or y >= self.Height: return 0
        zc = z >> 4
        xc = x >> 4


        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        try:
            ch = self.getChunk(xc, zc)
        except ChunkNotPresent:
            return 0

        ch.Data[xInChunk, zInChunk, y] = newdata
        ch.chunkChanged(False)

    def blockAt(self, x, y, z):
        """returns 0 for blocks outside the loadable chunks.  automatically loads chunks."""
        if y < 0 or y >= self.Height: return 0

        zc = z >> 4
        xc = x >> 4
        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        try:
            ch = self.getChunk(xc, zc)
        except ChunkNotPresent:
            return 0

        return ch.Blocks[xInChunk, zInChunk, y]

    def setBlockAt(self, x, y, z, blockID):
        """returns 0 for blocks outside the loadable chunks.  automatically loads chunks."""
        if y < 0 or y >= self.Height: return 0

        zc = z >> 4
        xc = x >> 4
        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        try:
            ch = self.getChunk(xc, zc)
        except ChunkNotPresent:
            return 0

        ch.Blocks[xInChunk, zInChunk, y] = blockID
        ch.dirty = True
        ch.needsLighting = True

    def skylightAt(self, x, y, z):

        if y < 0 or y >= self.Height: return 0
        zc = z >> 4
        xc = x >> 4


        xInChunk = x & 0xf;
        zInChunk = z & 0xf

        ch = self.getChunk(xc, zc)

        return ch.SkyLight[xInChunk, zInChunk, y]


    def setSkylightAt(self, x, y, z, lightValue):
        if y < 0 or y >= self.Height: return 0
        zc = z >> 4
        xc = x >> 4

        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        ch = self.getChunk(xc, zc)
        skyLight = ch.SkyLight

        oldValue = skyLight[xInChunk, zInChunk, y]

        ch.chunkChanged(False)
        if oldValue < lightValue:
            skyLight[xInChunk, zInChunk, y] = lightValue
        return oldValue < lightValue

    def heightMapAt(self, x, z):
        zc = z >> 4
        xc = x >> 4
        xInChunk = x & 0xf;
        zInChunk = z & 0xf;

        ch = self.getChunk(xc, zc)

        heightMap = ch.HeightMap

        return heightMap[zInChunk, xInChunk];
        #the heightmap is ordered differently because in minecraft it is a flat array

    @property
    def loadedChunks(self):
        return self._loadedChunks.keys();

    @property
    def chunkCount(self):
        """Returns the number of chunks in the level. May initiate a costly
        chunk scan."""
        if self._allChunks is None:
            self.preloadChunkPositions()
        return len(self._allChunks)

    @property
    def allChunks(self):
        """Iterates over (xPos, zPos) tuples, one for each chunk in the level.
        May initiate a costly chunk scan."""
        if self._allChunks is None:
            self.preloadChunkPositions()
        return self._allChunks.__iter__();



    def _makeChunk(self, cx, cz):
        """return the InfdevChunk object at the given position. because loading
        the chunk is done later, accesses to chunk attributes may 
        raise ChunkMalformed"""

        if not self.containsChunk(cx, cz) :
            raise ChunkNotPresent, (cx, cz);

        if not (cx, cz) in self._loadedChunks:
            self._loadedChunks[cx, cz] = InfdevChunk(self, (cx, cz));

        return self._loadedChunks[cx, cz]

    def chunkIsLoaded(self, cx, cz):
        if (cx, cz) in self._loadedChunks:
            return self._loadedChunks[(cx, cz)].isLoaded()

        return False

    def chunkIsCompressed(self, cx, cz):
        if (cx, cz) in self._loadedChunks:
            return self._loadedChunks[(cx, cz)].isCompressed()

        return False

    def chunkIsDirty(self, cx, cz):
        if (cx, cz) in self._loadedChunks:
            return self._loadedChunks[(cx, cz)].dirty

        return False

    def getChunk(self, cx, cz):
        """ read the chunk from disk, load it, and return it. 
        decompression and unpacking is done lazily."""


        c = self._makeChunk(cx, cz)
        c.load();
        if not (cx, cz) in self._loadedChunks:
            raise ChunkMalformed, "Chunk {0} malformed".format((cx, cz))
            self.world.malformedChunk(*self.chunkPosition);

        return c;

    def markDirtyChunk(self, cx, cz):
        if not (cx, cz) in self._loadedChunks: return
        self._loadedChunks[cx, cz].chunkChanged();

    def markDirtyBox(self, box):
        for cx, cz in box.chunkPositions:
            self.markDirtyChunk(cx, cz)

    def saveInPlace(self):
        for level in self.dimensions.itervalues():
            level.saveInPlace(True);

        dirtyChunkCount = 0;
        if self._loadedChunks:
            for chunk in self._loadedChunks.itervalues():
                if chunk.dirty:
                    dirtyChunkCount += 1;
                chunk.save();

        for path, tag in self.playerTagCache.iteritems():
            tag.saveGzipped(path)

        self.playerTagCache = {}

        self.root_tag.save(self.filename);
        info(u"Saved {0} chunks".format(dirtyChunkCount))

    def generateLights(self, dirtyChunks=None):
        for i in self.generateLightsIter(dirtyChunks):
            pass

    def generateLightsIter(self, dirtyChunks=None):
        """ dirtyChunks may be an iterable yielding (xPos,zPos) tuples
        if none, generate lights for all chunks that need lighting
        """

        startTime = datetime.now();

        if dirtyChunks is None:
            dirtyChunks = (ch for ch in self._loadedChunks.itervalues() if ch.needsLighting)
        else:
            dirtyChunks = (self._makeChunk(*c) for c in dirtyChunks if self.containsChunk(*c))

        dirtyChunks = sorted(dirtyChunks, key=lambda x:x.chunkPosition)


        #at 150k per loaded chunk, 
        maxLightingChunks = 4000

        info(u"Asked to light {0} chunks".format(len(dirtyChunks)))
        chunkLists = [dirtyChunks];
        def reverseChunkPosition(x):
            cx, cz = x.chunkPosition;
            return cz, cx

        def splitChunkLists(chunkLists):
            newChunkLists = []
            for l in chunkLists:

                #list is already sorted on x position, so this splits into left and right

                smallX = l[:len(l) / 2]
                bigX = l[len(l) / 2:]

                #sort halves on z position
                smallX = sorted(smallX, key=reverseChunkPosition)
                bigX = sorted(bigX, key=reverseChunkPosition)

                #add quarters to list

                newChunkLists.append(smallX[:len(smallX) / 2])
                newChunkLists.append(smallX[len(smallX) / 2:])

                newChunkLists.append(bigX[:len(bigX) / 2])
                newChunkLists.append(bigX[len(bigX) / 2:])

            return newChunkLists

        while len(chunkLists[0]) > maxLightingChunks:
            chunkLists = splitChunkLists(chunkLists);

        if len(chunkLists) > 1:
            info(u"Using {0} batches to conserve memory.".format(len(chunkLists)))

        i = 0
        for dc in chunkLists:
            i += 1;
            info(u"Batch {0}/{1}".format(i, len(chunkLists)))
            yield i, len(chunkLists)

            dc = sorted(dc, key=lambda x:x.chunkPosition)

            for j in self._generateLightsIter(dc):
                yield j

            for ch in dc:
                ch.compress();
        timeDelta = datetime.now() - startTime;

        if len(dirtyChunks):
            info(u"Completed in {0}, {1} per chunk".format(timeDelta, dirtyChunks and timeDelta / len(dirtyChunks) or 0))

        return;

    def _generateLightsIter(self, dirtyChunks):
        conserveMemory = False
        la = array(self.materials.lightAbsorption)

            #[d.genFastLights() for d in dirtyChunks]
        dirtyChunks = set(dirtyChunks)


        info(u"Lighting {0} chunks".format(len(dirtyChunks)))
        for i, chunk in enumerate(dirtyChunks):
            try:
                chunk.load();
            except (ChunkNotPresent, ChunkMalformed):
                continue;
            chunk.chunkChanged();
            yield i, len(dirtyChunks) * 14
            assert chunk.dirty and chunk.needsLighting

        for ch in list(dirtyChunks):
            #relight all blocks in neighboring chunks in case their light source disappeared.
            cx, cz = ch.chunkPosition
            for dx, dz in itertools.product((-1, 0, 1), (-1, 0, 1)):
                try:
                    ch = self.getChunk (cx + dx, cz + dz)
                except (ChunkNotPresent, ChunkMalformed):
                    continue
                dirtyChunks.add(ch);

        dirtyChunks = sorted(dirtyChunks, key=lambda x:x.chunkPosition)

        for i, chunk in enumerate(dirtyChunks):
            chunk.BlockLight[:] = self.materials.lightEmission[chunk.Blocks];

            if conserveMemory:
                chunk.compress();

        zeroChunk = ZeroChunk(self.Height)
        zeroChunk.BlockLight[:] = 0;
        zeroChunk.SkyLight[:] = 0;


        la[18] = 0; #for normal light dispersal, leaves absorb the same as empty air.
        startingDirtyChunks = dirtyChunks

        oldLeftEdge = zeros((1, 16, self.Height), 'uint8');
        oldBottomEdge = zeros((16, 1, self.Height), 'uint8');
        oldChunk = zeros((16, 16, self.Height), 'uint8');
        if self.dimNo == -1:
            lights = ("BlockLight",)
        else:
            lights = ("BlockLight", "SkyLight")
        info(u"Dispersing light...")

        for light in lights:
          j = 0
          workTotal = 0
          estimatedTotals = [len(startingDirtyChunks)] * 14
          zerochunkLight = getattr(zeroChunk, light);

          newDirtyChunks = list(startingDirtyChunks);

          for i in range(14):
            if len(newDirtyChunks) == 0: break

            info(u"{0} Pass {1}: {2} chunks".format(light, i, len(newDirtyChunks)));

            """
            propagate light!
            for each of the six cardinal directions, figure a new light value for 
            adjoining blocks by reducing this chunk's light by light absorption and fall off. 
            compare this new light value against the old light value and update with the maximum.
            
            we calculate all chunks one step before moving to the next step, to ensure all gaps at chunk edges are filled.  
            we do an extra cycle because lights sent across edges may lag by one cycle.
            """
            newDirtyChunks = set(newDirtyChunks)
            newDirtyChunks.discard(zeroChunk)

            dirtyChunks = sorted(newDirtyChunks, key=lambda x:x.chunkPosition)

            newDirtyChunks = list();


            for chunk in dirtyChunks:
                #xxx code duplication
                yield (workTotal + j, sum(estimatedTotals))
                j += 1
                (cx, cz) = chunk.chunkPosition
                neighboringChunks = {};
                try:
                    chunk.load();
                except (ChunkNotPresent, ChunkMalformed), e:
                    print "Chunk error during relight, chunk skipped: ", e
                    continue;

                for dir, dx, dz in ((FaceXDecreasing, -1, 0),
                                      (FaceXIncreasing, 1, 0),
                                      (FaceZDecreasing, 0, -1),
                                      (FaceZIncreasing, 0, 1)):
                    try:
                        neighboringChunks[dir] = self.getChunk(cx + dx, cz + dz)
                    except (ChunkNotPresent, ChunkMalformed):
                        neighboringChunks[dir] = zeroChunk;


                chunkLa = la[chunk.Blocks] + 1;
                chunkLight = getattr(chunk, light);
                oldChunk[:] = chunkLight[:]


                nc = neighboringChunks[FaceXDecreasing]
                ncLight = getattr(nc, light);
                oldLeftEdge[:] = ncLight[15:16, :, 0:self.Height] #save the old left edge 

                #left edge
                newlight = (chunkLight[0:1, :, :self.Height] - la[nc.Blocks[15:16, :, 0:self.Height]]) - 1
                newlight[newlight > 15] = 0;

                ncLight[15:16, :, 0:self.Height] = maximum(ncLight[15:16, :, 0:self.Height], newlight)

                #chunk body
                newlight = (chunkLight[1:16, :, 0:self.Height] - chunkLa[0:15, :, 0:self.Height])
                newlight[newlight > 15] = 0; #light went negative;

                chunkLight[0:15, :, 0:self.Height] = maximum(chunkLight[0:15, :, 0:self.Height], newlight)

                #right edge
                nc = neighboringChunks[FaceXIncreasing]
                ncLight = getattr(nc, light);

                newlight = ncLight[0:1, :, :self.Height] - chunkLa[15:16, :, 0:self.Height]
                newlight[newlight > 15] = 0;

                chunkLight[15:16, :, 0:self.Height] = maximum(chunkLight[15:16, :, 0:self.Height], newlight)


                #right edge
                nc = neighboringChunks[FaceXIncreasing]
                ncLight = getattr(nc, light);

                newlight = (chunkLight[15:16, :, 0:self.Height] - la[nc.Blocks[0:1, :, 0:self.Height]]) - 1
                newlight[newlight > 15] = 0;

                ncLight[0:1, :, 0:self.Height] = maximum(ncLight[0:1, :, 0:self.Height], newlight)

                #chunk body
                newlight = (chunkLight[0:15, :, 0:self.Height] - chunkLa[1:16, :, 0:self.Height])
                newlight[newlight > 15] = 0;

                chunkLight[1:16, :, 0:self.Height] = maximum(chunkLight[1:16, :, 0:self.Height], newlight)

                #left edge
                nc = neighboringChunks[FaceXDecreasing]
                ncLight = getattr(nc, light);

                newlight = ncLight[15:16, :, :self.Height] - chunkLa[0:1, :, 0:self.Height]
                newlight[newlight > 15] = 0;

                chunkLight[0:1, :, 0:self.Height] = maximum(chunkLight[0:1, :, 0:self.Height], newlight)

                zerochunkLight[:] = 0;

                #check if the left edge changed and dirty or compress the chunk appropriately
                if (oldLeftEdge != ncLight[15:16, :, :self.Height]).any():
                    #chunk is dirty
                    newDirtyChunks.append(nc)

                #bottom edge
                nc = neighboringChunks[FaceZDecreasing]
                ncLight = getattr(nc, light);
                oldBottomEdge[:] = ncLight[:, 15:16, :self.Height] # save the old bottom edge

                newlight = (chunkLight[:, 0:1, :self.Height] - la[nc.Blocks[:, 15:16, :self.Height]]) - 1
                newlight[newlight > 15] = 0;

                ncLight[:, 15:16, :self.Height] = maximum(ncLight[:, 15:16, :self.Height], newlight)

                #chunk body
                newlight = (chunkLight[:, 1:16, :self.Height] - chunkLa[:, 0:15, :self.Height])
                newlight[newlight > 15] = 0;

                chunkLight[:, 0:15, :self.Height] = maximum(chunkLight[:, 0:15, :self.Height], newlight)

                #top edge
                nc = neighboringChunks[FaceZIncreasing]
                ncLight = getattr(nc, light);

                newlight = ncLight[:, 0:1, :self.Height] - chunkLa[:, 15:16, 0:self.Height]
                newlight[newlight > 15] = 0;

                chunkLight[:, 15:16, 0:self.Height] = maximum(chunkLight[:, 15:16, 0:self.Height], newlight)


                #top edge  
                nc = neighboringChunks[FaceZIncreasing]

                ncLight = getattr(nc, light);

                newlight = (chunkLight[:, 15:16, :self.Height] - la[nc.Blocks[:, 0:1, :self.Height]]) - 1
                newlight[newlight > 15] = 0;

                ncLight[:, 0:1, :self.Height] = maximum(ncLight[:, 0:1, :self.Height], newlight)

                #chunk body
                newlight = (chunkLight[:, 0:15, :self.Height] - chunkLa[:, 1:16, :self.Height])
                newlight[newlight > 15] = 0;

                chunkLight[:, 1:16, :self.Height] = maximum(chunkLight[:, 1:16, :self.Height], newlight)

                #bottom edge
                nc = neighboringChunks[FaceZDecreasing]
                ncLight = getattr(nc, light);

                newlight = ncLight[:, 15:16, :self.Height] - chunkLa[:, 0:1, 0:self.Height]
                newlight[newlight > 15] = 0;

                chunkLight[:, 0:1, 0:self.Height] = maximum(chunkLight[:, 0:1, 0:self.Height], newlight)

                zerochunkLight[:] = 0;

                if (oldBottomEdge != ncLight[:, 15:16, :self.Height]).any():
                    newDirtyChunks.append(nc)

                newlight = (chunkLight[:, :, 0:self.Height - 1] - chunkLa[:, :, 1:self.Height])
                newlight[newlight > 15] = 0;
                chunkLight[:, :, 1:self.Height] = maximum(chunkLight[:, :, 1:self.Height], newlight)

                newlight = (chunkLight[:, :, 1:self.Height] - chunkLa[:, :, 0:self.Height - 1])
                newlight[newlight > 15] = 0;
                chunkLight[:, :, 0:self.Height - 1] = maximum(chunkLight[:, :, 0:self.Height - 1], newlight)
                zerochunkLight[:] = 0;

                if (oldChunk != chunkLight).any():
                    newDirtyChunks.append(chunk);

            workTotal += j
            estimatedTotals[i:] = [j] * (14 - i)
            j = 0

        for ch in startingDirtyChunks:
            ch.needsLighting = False;

    def addEntity(self, entityTag):
        assert isinstance(entityTag, TAG_Compound)
        x, y, z = map(lambda x:int(floor(x)), Entity.pos(entityTag))

        try:
            chunk = self.getChunk(x >> 4, z >> 4)
        except (ChunkNotPresent, ChunkMalformed), e:
            return None
            # raise Error, can't find a chunk?
        chunk.addEntity(entityTag);
        chunk.dirty = True

    def tileEntityAt(self, x, y, z):
        chunk = self.getChunk(x >> 4, z >> 4)
        return chunk.tileEntityAt(x, y, z)


    def addTileEntity(self, tileEntityTag):
        assert isinstance(tileEntityTag, TAG_Compound)
        if not 'x' in tileEntityTag: return
        x, y, z = TileEntity.pos(tileEntityTag)

        try:
            chunk = self.getChunk(x >> 4, z >> 4)
        except (ChunkNotPresent, ChunkMalformed):
            return
            # raise Error, can't find a chunk?
        chunk.addTileEntity(tileEntityTag)
        chunk.dirty = True

    def getEntitiesInBox(self, box):
        entities = []
        for chunk, slices, point in self.getChunkSlices(box):
            entities += chunk.getEntitiesInBox(box)

        return entities

    def removeEntitiesInBox(self, box):
        count = 0;
        for chunk, slices, point in self.getChunkSlices(box):
            count += chunk.removeEntitiesInBox(box);

        info("Removed {0} entities".format(count))
        return count;

    def removeTileEntitiesInBox(self, box):
        count = 0;
        for chunk, slices, point in self.getChunkSlices(box):
            count += chunk.removeTileEntitiesInBox(box);

        info("Removed {0} tile entities".format(count))
        return count;

    def fillBlocks(self, box, blockInfo, blocksToReplace=[]):
        if box is None:
            chunkIterator = self.getAllChunkSlices()
            box = self.bounds
        else:
            chunkIterator = self.getChunkSlices(box)

        #shouldRetainData = (not blockInfo.hasAlternate and not any([b.hasAlternate for b in blocksToReplace]))
        #if shouldRetainData:
        #    info( "Preserving data bytes" )
        shouldRetainData = False #xxx old behavior overwrote blockdata with 0 when e.g. replacing water with lava

        info("Replacing {0} with {1}".format(blocksToReplace, blockInfo))

        changesLighting = True

        if len(blocksToReplace):
            blocktable = self.blockReplaceTable(blocksToReplace)

            newAbsorption = self.materials.lightAbsorption[blockInfo.ID]
            oldAbsorptions = [self.materials.lightAbsorption[b.ID] for b in blocksToReplace]
            changesLighting = False
            for a in oldAbsorptions:
                if a != newAbsorption: changesLighting = True;

            newEmission = self.materials.lightEmission[blockInfo.ID]
            oldEmissions = [self.materials.lightEmission[b.ID] for b in blocksToReplace]
            for a in oldEmissions:
                if a != newEmission: changesLighting = True;


        i = 0;
        skipped = 0
        replaced = 0;

        for (chunk, slices, point) in chunkIterator:
            i += 1;
            if i % 100 == 0:
                info(u"Chunk {0}...".format(i))

            blocks = chunk.Blocks[slices]
            data = chunk.Data[slices]
            mask = slice(None)

            needsLighting = changesLighting;

            if len(blocksToReplace):
                mask = blocktable[blocks, data]

                blockCount = mask.sum()
                replaced += blockCount;

                #don't waste time relighting and copying if the mask is empty
                if blockCount:
                    blocks[:][mask] = blockInfo.ID
                    if not shouldRetainData:
                        data[mask] = blockInfo.blockData
                else:
                    skipped += 1;
                    needsLighting = False;

                def include(tileEntity):
                    p = TileEntity.pos(tileEntity)
                    x, y, z = map(lambda a, b, c:(a - b) - c, p, point, box.origin)
                    return not ((p in box) and mask[x, z, y])

                chunk.TileEntities.value[:] = filter(include, chunk.TileEntities)



            else:
                blocks[:] = blockInfo.ID
                if not shouldRetainData:
                    data[:] = blockInfo.blockData
                chunk.removeTileEntitiesInBox(box)

            chunk.chunkChanged(needsLighting);


        if len(blocksToReplace):
            info(u"Replace: Skipped {0} chunks, replaced {1} blocks".format(skipped, replaced))

    def sourceMaskFunc(self, blocksToCopy):
        if blocksToCopy is not None:
            typemask = zeros((256) , dtype='bool')
            typemask[blocksToCopy] = 1;
            def sourceMask(sourceBlocks):
                return typemask[sourceBlocks]
        else:
            def sourceMask(_sourceBlocks):
                return slice(None, None)
        return sourceMask

    def copyBlocksFromFiniteIter(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy):
        #assumes destination point and bounds have already been checked.
        (sx, sy, sz) = sourceBox.origin

        start = datetime.now();

        sourceMask = self.sourceMaskFunc(blocksToCopy)


        destBox = BoundingBox(destinationPoint, sourceBox.size)

        i = 0;
        chunkCount = float(destBox.chunkCount)

        for (chunk, slices, point) in self.getChunkSlices(destBox):
            i += 1;
            yield (i, chunkCount)

            if i % 100 == 0:
                info("Chunk {0}...".format(i))

            blocks = chunk.Blocks[slices];

            localSourceCorner2 = (
                sx + point[0] + blocks.shape[0],
                sy + blocks.shape[2],
                sz + point[2] + blocks.shape[1],
            )

            sourceBlocks = sourceLevel.Blocks[sx + point[0]:localSourceCorner2[0],
                                              sz + point[2]:localSourceCorner2[2],
                                              sy:localSourceCorner2[1]]
            #sourceBlocks = filterTable[sourceBlocks]
            mask = sourceMask(sourceBlocks)

            #for small level slices, reduce the destination area
            x, z, y = sourceBlocks.shape
            blocks = blocks[0:x, 0:z, 0:y]

            sourceData = None
            if hasattr(sourceLevel, 'Data'):
                #indev or schematic
                sourceData = sourceLevel.Data[sx + point[0]:localSourceCorner2[0],
                                              sz + point[2]:localSourceCorner2[2],
                                              sy:localSourceCorner2[1]]

            data = chunk.Data[slices][0:x, 0:z, 0:y]



            convertedSourceBlocks, convertedSourceData = self.convertBlocksFromLevel(sourceLevel, sourceBlocks, sourceData)

            blocks[mask] = convertedSourceBlocks[mask]
            if convertedSourceData is not None:
                data[mask] = (convertedSourceData[:, :, :])[mask]
                data[mask] &= 0xf;

            chunk.chunkChanged();


        d = datetime.now() - start;
        if i:
            info("Finished {2} chunks in {0} ({1} per chunk)".format(d, d / i, i))

            #chunk.compress(); #xxx find out why this trashes changes to tile entities

    def copyBlocksFromInfiniteIter(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy):
        """ copy blocks between two infinite levels via repeated export/import.  hilariously slow. """

        #assumes destination point and bounds have already been checked.
        destBox = BoundingBox(destinationPoint, sourceBox.size)
        chunkCount = destBox.chunkCount
        i = 0
        sourceMask = self.sourceMaskFunc(blocksToCopy)

        for chunk, slices, point in self.getChunkSlices(destBox):
            i += 1
            yield (i, chunkCount)
            if i % 100 == 0:
                info("Chunk {0}...".format(i))

            dstblocks = chunk.Blocks[slices]
            dstdata = chunk.Data[slices]
            size = [s.stop - s.start for s in slices]
            size[1], size[2] = size[2], size[1]
            sourceSubBox = BoundingBox([p + a for p, a in zip(point, sourceBox.origin)], size)
            for srcchunk, srcslices, srcpoint in sourceLevel.getChunkSlices(sourceSubBox):
                srcpoint = srcpoint[0], srcpoint[2], srcpoint[1]
                sourceBlocks = srcchunk.Blocks[srcslices]
                sourceData = srcchunk.Data[srcslices]
                mask = sourceMask(sourceBlocks)
                convertedSourceBlocks, convertedSourceData = self.convertBlocksFromLevel(sourceLevel, sourceBlocks, sourceData)

                dstslices = [slice(p, p + (s.stop - s.start)) for p, s in zip(srcpoint, srcslices)]
                dstblocks[dstslices][mask] = convertedSourceBlocks[mask]
                if convertedSourceData is not None:
                    dstdata[dstslices][mask] = convertedSourceData[mask]

            chunk.chunkChanged()



    def copyBlocksFrom(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy=None, entities=True):
        for i in self.copyBlocksFromIter(sourceLevel, sourceBox, destinationPoint, blocksToCopy, entities):
            pass

    def copyBlocksFromIter(self, sourceLevel, sourceBox, destinationPoint, blocksToCopy=None, entities=True):
        (x, y, z) = destinationPoint;
        (lx, ly, lz) = sourceBox.size
        #sourcePoint, sourcePoint1 = sourceBox

        sourceBox, destinationPoint = self.adjustCopyParameters(sourceLevel, sourceBox, destinationPoint)
        #needs work xxx
        info(u"Copying {0} blocks from {1} to {2}" .format (ly * lz * lx, sourceBox, destinationPoint))
        startTime = datetime.now()

        if(not isinstance(sourceLevel, MCInfdevOldLevel)):
            for i in self.copyBlocksFromFiniteIter(sourceLevel, sourceBox, destinationPoint, blocksToCopy):
                yield i


        else:
            for i in self.copyBlocksFromInfiniteIter(sourceLevel, sourceBox, destinationPoint, blocksToCopy):
                yield i

        for i in self.copyEntitiesFromIter(sourceLevel, sourceBox, destinationPoint, entities):
            yield i
        info("Duration: {0}".format(datetime.now() - startTime))
        #self.saveInPlace()


    def containsPoint(self, x, y, z):
        if y < 0 or y > 127: return False;
        return self.containsChunk(x >> 4, z >> 4)

    def containsChunk(self, cx, cz):
        if self._allChunks is not None: return (cx, cz) in self._allChunks;
        if (cx, cz) in self._loadedChunks: return True;
        if self.version:
            return (cx, cz) in self.allChunks
        else:
            return os.path.exists(self.chunkFilename(cx, cz))

    def malformedChunk(self, cx, cz):
        debug(u"Forgetting malformed chunk {0} ({1})".format((cx, cz), self.chunkFilename(cx, cz)))
        if (cx, cz) in self._loadedChunks:
            del self._loadedChunks[(cx, cz)]
            self._bounds = None

    def createChunk(self, cx, cz):
        if self.containsChunk(cx, cz): raise ValueError, "{0}:Chunk {1} already present!".format(self, (cx, cz))
        if self._allChunks is not None:
            self._allChunks.add((cx, cz))

        self._loadedChunks[cx, cz] = InfdevChunk(self, (cx, cz), create=True)
        self._bounds = None

    def createChunks(self, chunks):

        i = 0;
        ret = [];
        for cx, cz in chunks:
            i += 1;
            if not self.containsChunk(cx, cz):
                ret.append((cx, cz))
                self.createChunk(cx, cz);
                self.compressChunk(cx, cz);
            assert self.containsChunk(cx, cz), "Just created {0} but it didn't take".format((cx, cz))
            if i % 100 == 0:
                info(u"Chunk {0}...".format(i))

        info("Created {0} chunks.".format(len(ret)))

        return ret;

    def createChunksInBox(self, box):
        info(u"Creating {0} chunks in {1}".format((box.maxcx - box.mincx) * (box.maxcz - box.mincz), ((box.mincx, box.mincz), (box.maxcx, box.maxcz))))
        return self.createChunks(box.chunkPositions);

    def deleteChunk(self, cx, cz):

        if self._allChunks is not None: self._allChunks.discard((cx, cz))

        if (cx, cz) in self._loadedChunks:
            del self._loadedChunks[(cx, cz)]

        if self.version:
            r = cx >> 5, cz >> 5
            rf = self.getRegionFile(*r)
            if rf:
                rf.setOffset(cx & 0x1f , cz & 0x1f, 0)
                if (rf.offsets == 0).all():
                    rf.close()
                    os.unlink(rf.path)
                    del self.regionFiles[r]
        else:
            os.unlink(self.chunkFilename(cx, cz))

        self._bounds = None

    def deleteChunksInBox(self, box):
        info(u"Deleting {0} chunks in {1}".format((box.maxcx - box.mincx) * (box.maxcz - box.mincz), ((box.mincx, box.mincz), (box.maxcx, box.maxcz))))
        i = 0;
        ret = [];
        for cx, cz in itertools.product(xrange(box.mincx, box.maxcx), xrange(box.mincz, box.maxcz)):
            i += 1;
            if self.containsChunk(cx, cz):
                self.deleteChunk(cx, cz);
                ret.append((cx, cz))

            assert not self.containsChunk(cx, cz), "Just deleted {0} but it didn't take".format((cx, cz))

            if i % 100 == 0:
                info(u"Chunk {0}...".format(i))

        return ret


    spawnxyz = ["SpawnX", "SpawnY", "SpawnZ"]

    def playerSpawnPosition(self, player=None):
        """ 
        xxx if player is None then it gets the default spawn position for the world
        if player hasn't used a bed then it gets the default spawn position 
        """
        dataTag = self.root_tag["Data"]
        if player is None:
            playerSpawnTag = dataTag
        else:
            playerSpawnTag = self.getPlayerTag(player)

        return [playerSpawnTag.get(i, dataTag[i]).value for i in self.spawnxyz]

    def setPlayerSpawnPosition(self, pos, player=None):
        """ xxx if player is None then it sets the default spawn position for the world """
        if player is None:
            playerSpawnTag = self.root_tag["Data"]
        else:
            playerSpawnTag = self.getPlayerTag(player)
        for name, val in zip(self.spawnxyz, pos):
            playerSpawnTag[name] = nbt.TAG_Int(val);

    def getPlayerPath(self, player):
        assert player != "Player"
        return os.path.join(self.worldDir, "players", player + ".dat")

    def getPlayerTag(self, player="Player"):
        if player == "Player":
            if player in self.root_tag["Data"]:
                #single-player world
                return self.root_tag["Data"]["Player"];
            raise PlayerNotFound, player
        else:
            playerFilePath = self.getPlayerPath(player)
            if os.path.exists(playerFilePath):
                #multiplayer world, found this player
                playerTag = self.playerTagCache.get(playerFilePath)
                if playerTag is None:
                    playerTag = nbt.loadFile(playerFilePath)
                    self.playerTagCache[playerFilePath] = playerTag
                return playerTag

            else:
                raise PlayerNotFound, "{0}".format(player)
                #return None

    def getPlayerDimension(self, player="Player"):
        playerTag = self.getPlayerTag(player)
        if "Dimension" not in playerTag: return 0;
        return playerTag["Dimension"].value

    def setPlayerDimension(self, d, player="Player"):
        playerTag = self.getPlayerTag(player)
        if "Dimension" not in playerTag: playerTag["Dimension"] = nbt.TAG_Int(0);
        playerTag["Dimension"].value = d;


    def setPlayerPosition(self, pos, player="Player"):
        posList = nbt.TAG_List([nbt.TAG_Double(p) for p in pos]);
        playerTag = self.getPlayerTag(player)

        playerTag["Pos"] = posList

    def getPlayerPosition(self, player="Player"):
        playerTag = self.getPlayerTag(player)
        posList = playerTag["Pos"];

        pos = map(lambda x:x.value, posList);
        return pos;

    def setPlayerOrientation(self, yp, player="Player"):
        self.getPlayerTag(player)["Rotation"] = nbt.TAG_List([nbt.TAG_Float(p) for p in yp])

    def playerOrientation(self, player="Player"):
        """ returns (yaw, pitch) """
        yp = map(lambda x:x.value, self.getPlayerTag(player)["Rotation"]);
        y, p = yp;
        if p == 0: p = 0.000000001;
        if p == 180.0:  p -= 0.000000001;
        yp = y, p;
        return array(yp);

class MCAlphaDimension (MCInfdevOldLevel):
    def __init__(self, parentWorld, dimNo):
        filename = os.path.join(parentWorld.worldDir, "DIM" + str(int(dimNo)))
        MCInfdevOldLevel.__init__(self, filename)
        self.dimNo = dimNo
        self.parentWorld = parentWorld;
        self.filename = parentWorld.filename
        self.playersDir = parentWorld.playersDir;
        self.players = parentWorld.players

    @property
    def root_tag(self): return self.parentWorld.root_tag;


    def __str__(self):
        return "MCAlphaDimension({0}, {1})".format(self.parentWorld, self.dimNo)

    def loadLevelDat(self, create=False, random_seed=None, last_played=None):
        pass;
    def preloadDimensions(self):
        pass
    def create(self, *args, **kw):
        if not os.path.exists(self.worldDir):
            os.mkdir(self.worldDir)

    dimensionNames = { -1: "Nether", 3: "Aether"};
    @property
    def displayName(self):
        return u"{0} ({1})".format(self.parentWorld.displayName, self.dimensionNames[self.dimNo])

    def saveInPlace(self, saveSelf=False):
        """saving the dimension will save the parent world, which will save any
         other dimensions that need saving.  the intent is that all of them can
         stay loaded at once for fast switching """

        if saveSelf:
            MCInfdevOldLevel.saveInPlace(self);
        else:
            self.parentWorld.saveInPlace();


from zipfile import ZipFile, is_zipfile
import tempfile

class ZipSchematic (MCInfdevOldLevel):
    def __init__(self, filename):
        tempdir = tempfile.mktemp("schematic")
        zf = ZipFile(filename)
        self.zipfile = zf
        zf.extract("level.dat", tempdir)

        MCInfdevOldLevel.__init__(self, tempdir)

        self.filename = filename

        try:
            schematicDat = os.path.join(tempdir, "schematic.dat")
            with closing(self.zipfile.open("schematic.dat")) as f:
                schematicDat = nbt.load(buf=gunzip(f.read()))

                self.Width = schematicDat['Width'].value;
                self.Height = schematicDat['Height'].value;
                self.Length = schematicDat['Length'].value;
        except Exception, e:
            print "Exception reading schematic.dat, skipping: {0!r}".format(e)
            self.Width = 0
            self.Height = 128
            self.Length = 0
        if "Materials" in schematicDat:
            self.materials = namedMaterials[schematicDat["Materials"].value]

    def __del__(self):
        self.zipfile.close()
        MCInfdevOldLevel.__del__(self)

    def getWorldBounds(self):
        return BoundingBox((0, 0, 0), (self.Width, self.Height, self.Length))

    @classmethod
    def _isLevel(cls, filename):
        return is_zipfile(filename)

    def _loadChunk(self, chunk):
        if self.version:
            return MCInfdevOldLevel._loadChunk(self, chunk)
        else:
            cdata = self.zipfile.read(chunk.chunkFilename)
            chunk.compressedTag = cdata
            chunk.decompress()

    def _saveChunk(self, chunk):
        raise NotImplementedError, "Cannot save zipfiles yet!"

    def saveInPlace(self):
        raise NotImplementedError, "Cannot save zipfiles yet!"
    def saveToFile(self, filename):
        shutil.copy(self.filename, filename)

    def containsChunk(self, cx, cz):
        return (cx, cz) in self.allChunks

    def preloadRegions(self):
        self.zipfile.extractall(self.worldDir)
        self.regionFiles = {}

        MCInfdevOldLevel.preloadRegions(self)

    def preloadChunkPaths(self):
        info(u"Scanning for chunks...")
        self._allChunks = set()

        infos = self.zipfile.infolist()
        names = [i.filename.split('/') for i in infos]
        goodnames = [n for n in names if len(n) == 3 and n[0] in self.dirhashes and n[1] in self.dirhashes]

        for name in goodnames:
            c = name[2].split('.')
            if len(c) == 4 and c[0].lower() == 'c' and c[3].lower() == 'dat':
                try:
                    cx, cz = (decbase36(c[1]), decbase36(c[2]))
                except Exception, e:
                    info('Skipped file {0} ({1})'.format('.'.join(c), e))
                    continue
                #self._loadedChunks[ (cx, cz) ] = InfdevChunk(self, (cx, cz));
                self._allChunks.add((cx, cz))

        info(u"Found {0} chunks.".format(len(self._allChunks)))


    def preloadDimensions(self):
        pass

    def loadLevelDat(self, create=False, random_seed=None, last_played=None):
        if create:
            raise NotImplementedError, "Cannot save zipfiles yet!"

        with closing(self.zipfile.open("level.dat")) as f:
            with closing(gzip.GzipFile(fileobj=StringIO(f.read()))) as g:
                self.root_tag = nbt.load(buf=g.read())

    def chunkFilename(self, x, z):
        s = "/".join((self.dirhash(x), self.dirhash(z),
                                     "c.%s.%s.dat" % (base36(x), base36(z))));
        return s;
