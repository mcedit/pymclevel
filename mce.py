#!/usr/bin/env python
import mclevel
import sys
import os
from box import BoundingBox
from numpy import zeros, bincount
import logging

class UsageError(RuntimeError): pass
class BlockMatchError(RuntimeError): pass
class PlayerNotFound(RuntimeError): pass

class mce(object):
    random_seed = os.getenv('MCE_RANDOM_SEED', None)
    last_played = os.getenv("MCE_LAST_PLAYED", None)
    """
    Usage:
    
    Block commands:
       {commandPrefix}clone <sourcePoint> <sourceSize> <destPoint>
       {commandPrefix}fill <blockType> [ <point> <size> ]
       {commandPrefix}replace <blockType> [with] <newBlockType> [ <point> <size> ]
       
       {commandPrefix}export <filename> <sourcePoint> <sourceSize>
       {commandPrefix}import <filename> <destPoint>
       
       {commandPrefix}analyze
       
    Player commands:
       {commandPrefix}player [ <player> [ <point> ] ]
       {commandPrefix}spawn [ <point> ]
       
    Entity commands:
       {commandPrefix}removeEntities [ <EntityID> ]
    
    Chunk commands:
       {commandPrefix}createChunks <point> <size>
       {commandPrefix}deleteChunks <point> <size>
       {commandPrefix}prune <point> <size>
       {commandPrefix}relight [ <point> <size> ]
       
    World commands:
       {commandPrefix}degrief
       
    Editor commands:
       {commandPrefix}save 
       {commandPrefix}reload 
       {commandPrefix}load <filename> | <world number>
       {commandPrefix}quit 
       
    Informational: 
       {commandPrefix}blocks [ <block name> | <block ID> ]
       {commandPrefix}help [ <command> ]
        
    Points and sizes are space-separated triplets of numbers ordered X Y Z.
    X is position north-south, increasing southward. 
    Y is position up-down, increasing upward. 
    Z is position east-west, increasing westward.
    
    A player's name can be used as a point - it will use the
    position of the player's head. Use the keyword 'delta' after 
    the name to specify a point near the player. 
    
    Example:
       codewarrior delta 0 5 0
       
    This refers to a point 5 blocks above codewarrior's head. 
       
    """
    def commandUsage(self, command):
        " returns usage info for the named command - just give the docstring for the handler func "
        func = getattr(self, "_"+command)
        return func.__doc__
        
    commands = [
        "clone",
        "fill",
        "replace",
        "export",
        "import",
        
        "player",
        "spawn",
        
        "removeentities",
        
        "createchunks",
        "deletechunks",
        "prune",
        "relight",
        
        "degrief",
        
        "save",
        "load",
        "reload",
        
        "quit",
        "exit",
        
        "help",
        "blocks",
        "analyze",
        
        "debug",
        "log",
    ]
    debug = False
    needsSave = False;
    
    def readPoint(self, command, isPoint = True):
        try:
            word = command.pop(0)
            if isPoint and (word in self.level.players):
                x,y,z = self.level.getPlayerPosition(word)
                if len(command) and command[0].lower() == "delta":
                    command.pop(0)
                    try:
                        x += int(command.pop(0))
                        y += int(command.pop(0))
                        z += int(command.pop(0))
                        
                    except ValueError:
                        raise UsageError, "Error decoding point input (expected a number)."
                return (x,y,z)
                
        except IndexError:
            raise UsageError, "Error decoding point input (expected more values)."
            
    
        try:
            try:
                x = float(word)
            except ValueError:
                if isPoint:
                    raise PlayerNotFound, word
                raise
            y = float(command.pop(0))
            z = float(command.pop(0))
        except ValueError:
            raise UsageError, "Error decoding point input (expected a number)."
        except IndexError:
            raise UsageError, "Error decoding point input (expected more values)."
        
        return (x,y,z)
    
    def readBlockType(self, command):
        keyword = command.pop(0)
        
        def blocksMatching(search):
            if search in self.level.materials.names:
                #exact match
                return [search]
            return filter(lambda x:search.lower() in x.lower(), self.level.materials.names)
        
        matches = blocksMatching(keyword)
        blockType = None
        
        if len(matches):
            if len(matches) == 1:
                blockType = self.level.materials.materialNamed(matches[0])

            #eat up more words that possibly specify a block.  stop eating when 0 matching blocks.
            while len(command):
                newMatches = blocksMatching(keyword + " " + command[0]);
                
                
                if len(newMatches) == 1:
                    blockType = self.level.materials.materialNamed(newMatches[0])
                if len(newMatches) > 0:
                    matches = newMatches
                    keyword = keyword + " " + command.pop(0)
                else:
                    break;
            
            
            
        else:
            try:
                blockType = int(keyword);
            except ValueError:
                blockType = None;
        
        if blockType is None:
                print "Ambiguous block specifier: ", keyword 
                if len(matches):
                    print "Matches: "
                    for m in matches:
                        if m == "Future Block!": continue
                        print "{0:3}: {1}".format(self.level.materials.materialNamed(m),m)
                else:
                    print "No blocks matched."
                raise BlockMatchError
        
        return blockType
        
    def _debug(self, command):
        self.debug = not self.debug
        print "Debug", ("disabled", "enabled")[self.debug]
    def _log(self, command):
        """
    log [ <number> ]
    
    Get or set the log threshold. 0 logs everything; 50 only logs major errors.
    """
        if len(command):
            try:
                logging.getLogger().level = int(command[0]);
            except ValueError:
                raise UsageError
        else:
            print "Log level: {0}".format(logging.getLogger().level)
            
    
    def _clone(self, command):
        """
    clone <sourcePoint> <sourceSize> <destPoint>
    
    Clone blocks in a cuboid starting at sourcePoint and extending for 
    sourceSize blocks in each direction. Blocks and entities in the area 
    are cloned at destPoint
    """
        if len(command) == 0:
            self.printUsage("clone")
            return;
            
        sourcePoint = self.readPoint(command)
        sourceSize = self.readPoint(command, isPoint = False)
        destPoint = self.readPoint(command)
    
        destPoint = map(int, destPoint)
        
        box = BoundingBox(sourcePoint, sourceSize)
        tempSchematic = self.level.extractSchematic(box);
        self.level.copyBlocksFrom(tempSchematic, BoundingBox((0,0,0), sourceSize), destPoint);
        
        self.needsSave = True;
        print "Cloned 0 blocks." 
    
    def _fill(self, command):
        """
    fill <blockType> [ <point> <size> ]
    
    Fill blocks with blockType in a cuboid starting at point and 
    extending for size blocks in each direction. Without a 
    destination, fills the whole world. blockType and may be a
    number from 0-255 or a name listed by the 'blocks' command.
    """
        if len(command) == 0:
            self.printUsage("fill")
            return;
        
        blockType = self.readBlockType(command)
        assert blockType >=0 and blockType < 256
        
        if len(command):
            destPoint = self.readPoint(command);
            destSize = self.readPoint(command, isPoint = False);
            box = BoundingBox(destPoint, destSize)
        
        else:
            box = None
                    
        print "Filling with {0}".format(self.level.materials.names[blockType])
        
        self.level.fillBlocks(box, blockType)
        
        
        self.needsSave = True;
        print "Filled {0} blocks.".format("all" if box is None else box.volume)
    
    def _replace(self, command):
        """
    replace <blockType> [with] <newBlockType> [ <point> <size> ]
    
    Replace all blockType blocks with newBlockType in a cuboid 
    starting at point and extending for size blocks in 
    each direction. Without a destination, replaces blocks over
    the whole world. blockType and newBlockType may be numbers 
    from 0-255 or names listed by the 'blocks' command.
    """
        if len(command) == 0:
            self.printUsage("replace")
            return;
        
        blockType = self.readBlockType(command)
        assert blockType >=0 and blockType < 256
        if command[0].lower() == "with": 
            command.pop(0)
        newBlockType = self.readBlockType(command)
        assert newBlockType >=0 and newBlockType < 256
            
        if len(command):
            destPoint = self.readPoint(command);
            destSize = self.readPoint(command, isPoint = False);
            box = BoundingBox(destPoint, destSize)
        
        else:
            box = None

    
        print "Replacing {0} with {1}".format(self.level.materials.names[blockType],
                                              self.level.materials.names[newBlockType])
        
        self.level.fillBlocks(box, newBlockType, blockData = 0, blocksToReplace = [blockType])
        
        self.needsSave = True;
        print "Replaced {0} blocks.".format("all" if box is None else box.volume)

    def _analyze(self, command):
        """
    analyze
    
    Counts all of the block types in every chunk of the world.
    """
        blockCounts = zeros( (256,), 'uint64')
        
        for i, cPos in enumerate(self.level.presentChunks, 1):
            ch = self.level.getChunk(*cPos);
            counts = bincount(ch.Blocks.ravel())
            blockCounts[:counts.shape[0]] += counts
            
            ch.unload();
            if i % 100 == 0:
                print "Chunk {0}...".format( i )
            
        for i in range(256):
            if blockCounts[i]:
                print "{0:30}: {1:10}".format(self.level.materials.names[i], blockCounts[i]);
                
            
    def _export(self, command):
        """
    export <filename> <sourcePoint> <sourceSize>
    
    Exports blocks in the specified region to a file in schematic format.
    This file can be imported with mce or MCEdit.
    """
        if len(command) == 0:
            self.printUsage("export")
            return;
        
        filename = command.pop(0)
        sourcePoint = self.readPoint(command)
        sourceSize = self.readPoint(command, isPoint = False)
    
        
        box = BoundingBox(sourcePoint, sourceSize)
        tempSchematic = self.level.extractSchematic(box);
        
        tempSchematic.saveToFile(filename)
        
        print "Exported {0} blocks.".format(tempSchematic.getWorldBounds().volume) 
    
    def _import(self, command):
        """
    import <filename> <destPoint>
    
    Imports a level or schematic into this world, beginning at destPoint.
    Supported formats include 
    - Classic single-player .mine, 
    - Classic multiplayer server_level.dat,
    - Indev .mclevel
    - Schematic from RedstoneSim, MCEdit, mce
    - .inv from INVEdit (appears as a chest)
    """
        if len(command) == 0:
            self.printUsage("import")
            return;
        
        filename = command.pop(0)
        destPoint = self.readPoint(command)
        
        importLevel = mclevel.fromFile(filename, last_played=self.last_played, random_seed=self.random_seed)
        self.level.copyBlocksFrom(importLevel, importLevel.getWorldBounds(), destPoint);
        
        
        self.needsSave = True;
        print "Imported {0} blocks.".format(importLevel.getWorldBounds().volume) 
    
    def _player(self, command):
        """
    player [ <player> [ <point> ] ]
    
    Move the named player to the specified point.
    Without a point, prints the named player's position.
    Without a player, prints all players and positions.
    
    In a single-player world, the player is named Player.
    """
        if len(command) == 0:
            print "Players: "
            for player in self.level.players:
                print "    {0}: {1}".format(player, self.level.getPlayerPosition(player))
            return;
            
        player = command.pop(0)
        if len(command) == 0:
            print "Player {0}: {1}".format(player, self.level.getPlayerPosition(player))
            return;
            
        point = self.readPoint(command)
        self.level.setPlayerPosition(point, player)
        
        self.needsSave = True;
        print "Moved player {0} to {1}".format(player, point)
    
    def _spawn(self, command):
        """
    spawn [ <point> ]
    
    Move the world's spawn point.
    Without a point, prints the world's spawn point.
    """   
        if len(command):
            point = self.readPoint(command)
            
            self.level.setPlayerSpawnPosition(point);
        
            self.needsSave = True;
            print "Moved spawn point to ", map(int, point)
        else:
            print "Spawn point: ", self.level.playerSpawnPosition(); 
    
    def _removeentities(self, command):
        """
    removeEntities [ [except] [ <EntityID> [ <EntityID> ... ] ] ]
    
    Remove all entities matching one or more entity IDs.
    With the except keyword, removes all entities not 
    matching one or more entity IDs.
    
    Without any IDs, removes all entities in the world.
    
    Known Mob Entity IDs: 
        Mob Monster Creeper Skeleton Spider Giant 
        Zombie Slime Pig Sheep Cow Chicken

    Known Item Entity IDs: Item Arrow Snowball Painting

    Known Vehicle Entity IDs: Minecart Boat
    
    Known Dynamic Tile Entity IDs: PrimedTnt FallingSand
    """
        removedEntities = {};
        
        if len(command):
            if command[0].lower() == "except":
                command.pop(0);
                print "Removing all entities except ", command
                def match(entityID):
                    return not (entityID.lower() in matchWords)
            else:
                print "Removing {0}...".format(", ".join(command))
                def match(entityID):
                    return entityID.lower() in matchWords

            matchWords = map(lambda x:x.lower(), command)

            
        else:
            print "Removing all entities..."
            def match(entity): return True;
            
        for cx,cz in self.level.presentChunks:
            chunk = self.level.getChunk(cx,cz)
            entitiesRemoved = 0;
            
            for entity in list(chunk.Entities):
                entityID = entity["id"].value
                
                if match(entityID):
                    removedEntities[entityID] = removedEntities.get(entityID, 0) + 1;
                    
                    chunk.Entities.remove(entity)
                    entitiesRemoved += 1;
            
            if entitiesRemoved:
                chunk.chunkChanged(False)
                
            chunk.compress();
            chunk.save();
            chunk.unload();
            
        if len(removedEntities) == 0:
            print "No entities to remove."
        else:
            print "Removed entities:"
            for entityID in sorted(removedEntities.keys()):
                print "  {0}: {1:6}".format(entityID, removedEntities[entityID]);
        
        self.needsSave = True;
    
    def _createchunks(self, command):
        """
    createChunks <point> <size>
    
    Creates any chunks not present in the specified region. 
    New chunks are filled with only air. New chunks are written
    to disk immediately.
    """
        if len(command) == 0:
            self.printUsage("createchunks")
            return;
        
        point = self.readPoint(command)
        size = self.readPoint(command, isPoint = False)
       
        box = BoundingBox(point, size)
        
        oldChunkCount = len(self.level.presentChunks)
        self.level.createChunksInBox(box)
        
        print "Created {0} chunks." .format(len(self.level.presentChunks)-oldChunkCount)
        
        self.needsSave = True;

    def _deletechunks(self, command):
        """
    deleteChunks <point> <size>
    
    Removes all chunks contained in the specified region. 
    Chunks are deleted from disk immediately.
    """
        if len(command) == 0:
            self.printUsage("deletechunks")
            return;
        
        point = self.readPoint(command)
        size = self.readPoint(command, isPoint = False)
        
        box = BoundingBox(point, size)
        
        oldChunkCount = len(self.level.presentChunks)
        self.level.deleteChunksInBox(box)
        
        print "Deleted {0} chunks." .format(oldChunkCount-len(self.level.presentChunks))
        
    def _prune(self, command):
        """
    prune <point> <size>
    
    Removes all chunks not contained in the specified region. Useful for enforcing a finite map size.
    Chunks are deleted from disk immediately.
    """
        if len(command) == 0:
            self.printUsage("prune")
            return;
        
        point = self.readPoint(command)
        size = self.readPoint(command, isPoint = False)
        
        box = BoundingBox(point, size)
        
        oldChunkCount = len(self.level.presentChunks)
        
        
        for cx,cz in self.level.presentChunks:
            if cx < box.mincx or cx >= box.maxcx or cz < box.mincz or cz >= box.maxcz:
                self.level.deleteChunk(cx,cz)
                
        print "Pruned {0} chunks." .format(oldChunkCount-len(self.level.presentChunks))
    
    def _relight(self, command):
        """
    relight [ <point> <size> ]
    
    Recalculates lights in the region specified. If omitted, 
    recalculates the entire world.
    """
        if len(command):
            point = self.readPoint(command)
            size = self.readPoint(command, isPoint = False)
           
            box = BoundingBox(point, size)
            chunks = itertools.product(range(box.mincx, box.maxcx),range(box.mincz, box.maxcz))
        
        else:
            chunks = self.level.presentChunks
        self.level.generateLights(chunks)
        
        print "Relit 0 chunks." 
        self.needsSave = True;
    
    def _degrief(self, command):
        """
    degrief [ <height> ]
    
    Reverse a few forms of griefing by removing 
    Adminium, Obsidian, Fire, and Lava wherever 
    they occur above the specified height.
    Without a height, uses height level 32.
    
    Removes natural surface lava.
    
    Also see removeEntities
    """
        box = self.level.getWorldBounds();
        box.miny = 32
        if len(command):
            try:
                box.miny = int(command[0])
            except ValueError:
                pass
                
        print "Removing grief matter and surface lava above height {0}...".format(box.miny)
        
        self.level.fillBlocks(box,
                              self.level.materials.materialNamed("Air"),
                              blocksToReplace=[self.level.materials.materialNamed("Adminium"),
                                self.level.materials.materialNamed("Obsidian"),
                                self.level.materials.materialNamed("Fire"),
                                self.level.materials.materialNamed("Lava"),
                                self.level.materials.materialNamed("Stationary lava"),
                                ]
                              )
        self.needsSave = True;
        
    def _quit(self, command):
        """
    quit [ yes | no ]
    
    Quits the program in interactive mode. 
    Without 'yes' or 'no', prompts to save before quitting. 
    
    In batch mode, an end of file automatically saves the level.
    """
        if len(command) == 0 or not (command[0].lower() in ("yes", "no")): 
            if raw_input("Save before exit? ").lower() in ("yes", "y", "1", "true"):
                self._save(command);
                raise SystemExit;
        if len(command) and command[0].lower == "yes":
            self._save(command);

        raise SystemExit
            
    def _exit(self, command):
        self._quit(command)
        
    def _save(self, command):
        if self.needsSave:
            self.level.generateLights()
            self.level.saveInPlace();
            self.needsSave = False;
            
    def _load(self, command):
        """
    load [ <filename> | <world number> ]
    
    Loads another world, discarding all changes to this world.
    """    
        if len(command) == 0:
            self.printUsage("load")
        self.loadWorld(command[0])
        
    def _reload(self, command):
        self.level = mclevel.fromFile(self.filename, last_played=self.last_played, random_seed=self.random_seed);
        
    def _help(self, command):
        if len(command):
            self.printUsage(command[0])
        else:
            self.printUsage()
    
    def _blocks(self, command):
        """
    blocks [ <block name> | <block ID> ]
    
    Prints block IDs matching the name, or the name matching the ID.
    With nothing, prints a list of all blocks.
    """
    
        print "ID : Block name"
        searchName = None
        if len(command):
            searchName = " ".join(command)
            try:
                searchNumber = int(searchName)
            except ValueError: 
                searchNumber = None
            else:
                print "{0:3}: {1}".format(searchNumber, self.level.materials.names[searchNumber])
                return
                
        for i in range(len(self.level.materials.names)):
            name = self.level.materials.names[i];
            if name == "Future Block!": return;
            if searchName:
                if not (searchName.lower() in name.lower()):
                #don't print blocks that don't match the given name or number
                    continue
                    
            print "{0:3}: {1}".format(i, name)
            
    def printUsage(self, command = ""):
        if command.lower() in self.commands:
            print "Usage: ", self.commandUsage(command.lower());
        else:
            print self.__doc__.format(commandPrefix=("","mcedit <world> ")[not self.batchMode]);
        
        
    def printUsageAndQuit(self):
        self.printUsage();
        raise UsageError;
    
    def loadWorld(self, world):
        level = None
        try:
            worldNum = int(world)
        except ValueError:
            self.level = mclevel.fromFile(world, last_played=self.last_played, random_seed=self.random_seed)
            
            self.filename = self.level.filename
            
            self.shortWorld = os.path.split(self.level.filename)[1];
            if self.shortWorld == "level.dat":
                self.shortWorld = os.path.split(os.path.split(self.level.filename)[0])[1];
        
        else:
            if str(worldNum) == world:
                if worldNum > 0 and worldNum <= 5:
                    self.level = mclevel.loadWorldNumber(worldNum)
                    self.filename = self.level.filename
                    
                    self.shortWorld = "World{0}".format(worldNum)
                
        
    
    level = None  
    shortWorld = "[unknown world]"
    batchMode = False;
    
    def run(self):
        logging.basicConfig(format='%(levelname)s:%(message)s')
        logging.getLogger().level = logging.INFO
    
        appPath = sys.argv.pop(0)
        if len(sys.argv):
            world = sys.argv.pop(0)
            self.loadWorld(world)
        else:
            self.printUsage();
            while True:
                try:
                    world = raw_input("Please enter world number or path to world folder: ")
                    self.loadWorld(world)
                except IOError, e:
                    print "Cannot open {0}: {1}".format(world, e);
                except EOFError, e:
                    print "End of input."
                    raise SystemExit;
                else:
                    break;
        
        
        
            
        if len(sys.argv):
            #process one command from command line
            try:
                self.processCommand(sys.argv)
            except UsageError:
                self.printUsageAndQuit();
            self._save([]);
            
        else:
            #process many commands on standard input, maybe interactively
            command = [""]
            self.batchMode = True;
            while True:
                
                
                try:
                    command = raw_input("{0}> ".format(self.shortWorld))
                    if len(command) == 0: continue
                    print
                    
                    commandWords = command.split()
                    self.processCommand(commandWords)
                except EOFError, e:
                    print "End of file. Saving automatically."
                    self._save([]);
                    raise SystemExit;
                except Exception, e:
                    if self.debug:
                        traceback.print_exc();
                    print e
                    #self.printUsage();
                    
                
    def processCommand(self, command):
        keyword = command.pop(0).lower()
        if not keyword in self.commands:
            raise UsageError, "Command {0} not recognized.".format(keyword)
        func = getattr(self, "_" + keyword)
        
        try:
            func(command)
        except PlayerNotFound, e:
            print "Cannot find player {0}".format(e.args[0])
            self._player([])

        except UsageError, e:
            print e
            if self.debug:
                traceback.print_exc()
            self.printUsage(keyword)
            
        
        
editor = mce();

import traceback
try:
    editor.run();
except Exception, e:
    traceback.print_exc()
    print e
    #editor.printUsage()
    

        
