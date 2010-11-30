#!/usr/bin/env python
import mclevel
import sys
import os
from box import BoundingBox
import numpy
from numpy import zeros, bincount
import logging
import itertools
import traceback
import shlex
import operator
from math import floor
try:
    import readline
except:
    pass
    
class UsageError(RuntimeError): pass
class BlockMatchError(RuntimeError): pass
class PlayerNotFound(RuntimeError): pass

class mce(object):
    """
    Usage:
    
    Block commands:
       {commandPrefix}clone <sourceBox> <destPoint> [noair] [nowater]
       {commandPrefix}fill <blockType> [ <box> ]
       {commandPrefix}replace <blockType> [with] <newBlockType> [ <box> ]
       
       {commandPrefix}export <filename> <sourceBox>
       {commandPrefix}import <filename> <destPoint> [noair] [nowater]
       
       {commandPrefix}createChest <point> <item> [ <count> ]
       {commandPrefix}analyze
       
    Player commands:
       {commandPrefix}player [ <player> [ <point> ] ]
       {commandPrefix}spawn [ <point> ]
       
    Entity commands:
       {commandPrefix}removeEntities [ <EntityID> ]
       {commandPrefix}dumpSigns [ <filename> ]
       
    Chunk commands:
       {commandPrefix}createChunks <box>
       {commandPrefix}deleteChunks <box>
       {commandPrefix}prune <box>
       {commandPrefix}relight [ <box> ]
       
    World commands:
       {commandPrefix}create <filename>
       {commandPrefix}degrief 
       {commandPrefix}time [ <time> ]
       {commandPrefix}worldsize       
       {commandPrefix}heightmap <filename>
       {commandPrefix}randomseed [ <seed> ]
       
    Editor commands:
       {commandPrefix}save 
       {commandPrefix}reload 
       {commandPrefix}load <filename> | <world number>
       {commandPrefix}execute <filename>
       {commandPrefix}quit 
       
    Informational: 
       {commandPrefix}blocks [ <block name> | <block ID> ]
       {commandPrefix}help [ <command> ]
        
    **IMPORTANT**
       {commandPrefix}box 
       
       Type 'box' to learn how to specify points and areas.
       
       
    """
    random_seed = os.getenv('MCE_RANDOM_SEED', None)
    last_played = os.getenv("MCE_LAST_PLAYED", None)
    def commandUsage(self, command):
        " returns usage info for the named command - just give the docstring for the handler func "
        func = getattr(self, "_"+command)
        return func.__doc__
        
    commands = [
        "clone",
        "fill",
        "replace",
        
        "export",
        "execute",
        "import",
        
        "createchest",
        
        "player",
        "spawn",
        
        "removeentities",
        "dumpsigns",
        
        "createchunks",
        "deletechunks",
        "prune",
        "relight",
        
        "create",
        "degrief",
        "time",
        "worldsize",
        "heightmap",
        "randomseed",
        
        "save",
        "load",
        "reload",
        "dimension",
        
        "quit",
        "exit",
        
        "help",
        "blocks",
        "analyze",
        
        "debug",
        "log",
        "box",
    ]
    debug = False
    needsSave = False;
    
    def readInt(self, command):
        try:
            val = int(command.pop(0))
        except ValueError:
            raise UsageError, "Cannot understand numeric input"
        return val
    
    def prettySplit(self, command):
        cmdstring = " ".join(command);
        
        lex = shlex.shlex(cmdstring);
        lex.whitespace_split = True;
        lex.whitespace += "(),"
            
        command[:] = list(lex)
        
    def readBox(self, command):
        self.prettySplit(command)
        
        sourcePoint = self.readIntPoint(command)
        if command[0].lower() == "to":
            command.pop(0)
            sourcePoint2 = self.readIntPoint(command)
            sourceSize = map(operator.sub, sourcePoint2, sourcePoint)
        else:
            sourceSize = self.readIntPoint(command, isPoint = False)
        if len([p for p in sourceSize if p <= 0]):
            raise UsageError, "Box size cannot be zero or negative"
        box = BoundingBox(sourcePoint, sourceSize)
        return box
    
    def readIntPoint(self, command, isPoint = True):
        point = self.readPoint(command, isPoint)
        point = map(int, map(floor, point))
        return point
        
    def readPoint(self, command, isPoint = True):
        self.prettySplit(command)
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
                blockType = blockType & 0xff
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
    
    def readBlocksToCopy(self, command):
        blocksToCopy = range(256);
        while len(command):
            word = command.pop();
            if word == "noair":
                blocksToCopy.remove(0);
            if word == "nowater":
                blocksToCopy.remove(8);
                blocksToCopy.remove(9);
                
        return blocksToCopy
        
    def _box(self, command):
        """
        Boxes:
        
    Many commands require a <box> as arguments. A box can be specified with
    a point and a size:
        (12, 5, 15), (5, 5, 5)
    
    or with two points, making sure to put the keyword "to" between them:
        (12, 5, 15) to (17, 10, 20)
        
    The commas and parentheses are not important. 
    You may add them for improved readability.
    
    
        Points:
        
    Points and sizes are triplets of numbers ordered X Y Z.
    X is position north-south, increasing southward. 
    Y is position up-down, increasing upward. 
    Z is position east-west, increasing westward.
    
    
        Players:
    
    A player's name can be used as a point - it will use the
    position of the player's head. Use the keyword 'delta' after 
    the name to specify a point near the player. 
    
    Example:
       codewarrior delta 0 5 0
       
    This refers to a point 5 blocks above codewarrior's head. 
    
    """
        raise UsageError;
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
                raise UsageError, "Cannot understand numeric input."
        else:
            print "Log level: {0}".format(logging.getLogger().level)
            
    
    def _clone(self, command):
        """
    clone <sourceBox> <destPoint> [noair] [nowater]
    
    Clone blocks in a cuboid starting at sourcePoint and extending for 
    sourceSize blocks in each direction. Blocks and entities in the area 
    are cloned at destPoint.
    """
        if len(command) == 0:
            self.printUsage("clone")
            return;
            
        box = self.readBox(command);
        
        destPoint = self.readPoint(command)
        
        destPoint = map(int, map(floor, destPoint))
        blocksToCopy = self.readBlocksToCopy(command);
        
        tempSchematic = self.level.extractSchematic(box);
        self.level.copyBlocksFrom(tempSchematic, BoundingBox((0,0,0), box.origin), destPoint, blocksToCopy);
        
        self.needsSave = True;
        print "Cloned 0 blocks." 
    
    def _fill(self, command):
        """
    fill <blockType> [ <box> ]
    
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
            box = self.readBox(command)
        else:
            box = None
                    
        print "Filling with {0}".format(self.level.materials.names[blockType])
        
        self.level.fillBlocks(box, blockType)
        
        
        self.needsSave = True;
        print "Filled {0} blocks.".format("all" if box is None else box.volume)
    
    def _replace(self, command):
        """
    replace <blockType> [with] <newBlockType> [ <box> ]
    
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
            box = self.readBox(command)
        else:
            box = None

    
        print "Replacing {0} with {1}".format(self.level.materials.names[blockType],
                                              self.level.materials.names[newBlockType])
        
        self.level.fillBlocks(box, newBlockType, blockData = 0, blocksToReplace = [blockType])
        
        self.needsSave = True;
        print "Done."

    def _createchest(self, command):
        """
    createChest <point> <item> [ <count> ]
    
    Create a chest filled with the specified item. 
    Stacks are 64 if count is not given.
    """
        point = map(lambda x: int(floor(float(x))), self.readPoint(command))
        itemID = self.readInt(command)
        count = 64;
        if len(command):
            count = self.readInt(command)
            
        chest = mclevel.MCSchematic.chestWithItemID(itemID, count);
        self.level.copyBlocksFrom(chest, chest.bounds, point);
        self.needsSave = True;
        
    def _analyze(self, command):
        """
    analyze
    
    Counts all of the block types in every chunk of the world.
    Also updates the level's 'SizeOnDisk' field, correcting its size in the
    world select menu.  
    """
        blockCounts = zeros( (256,), 'uint64')
        sizeOnDisk = 0;
        
        print "Analyzing {0} chunks...".format(len(self.level.allChunks))
        
        for i, cPos in enumerate(self.level.allChunks, 1):
            ch = self.level.getChunk(*cPos);
            counts = bincount(ch.Blocks.ravel())
            blockCounts[:counts.shape[0]] += counts
            sizeOnDisk += ch.compressedSize();
            ch.unload();
            if i % 100 == 0:
                print "Chunk {0}...".format( i )
            
        for i in range(256):
            if blockCounts[i]:
                print "{0:30}: {1:10}".format(self.level.materials.names[i], blockCounts[i]);
        
        print "Size on disk: {0:.3}MB".format(sizeOnDisk / 1048576.0)
        self.level.SizeOnDisk = sizeOnDisk
        self.needsSave = True
            
    def _export(self, command):
        """
    export <filename> <sourceBox>
    
    Exports blocks in the specified region to a file in schematic format.
    This file can be imported with mce or MCEdit.
    """
        if len(command) == 0:
            self.printUsage("export")
            return;
        
        filename = command.pop(0)
        box = self.readBox(command)
        
        tempSchematic = self.level.extractSchematic(box);
        
        tempSchematic.saveToFile(filename)
        
        print "Exported {0} blocks.".format(tempSchematic.bounds.volume) 
    
    def _import(self, command):
        """
    import <filename> <destPoint> [noair] [nowater]
    
    Imports a level or schematic into this world, beginning at destPoint.
    Supported formats include 
    - Alpha single or multiplayer world folder containing level.dat,
    - Zipfile containing Alpha world folder,
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
        blocksToCopy = self.readBlocksToCopy(command)
        
        importLevel = mclevel.fromFile(filename)
        
        destBox = BoundingBox(destPoint, importLevel.size)
        self.level.createChunksInBox(destBox);
        
        self.level.copyBlocksFrom(importLevel, importLevel.bounds, destPoint, blocksToCopy);
        
        
        self.needsSave = True;
        print "Imported {0} blocks.".format(importLevel.bounds.volume) 
    
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
            point = map(int, map(floor, point))
            
            self.level.setPlayerSpawnPosition(point);
        
            self.needsSave = True;
            print "Moved spawn point to ", point
        else:
            print "Spawn point: ", self.level.playerSpawnPosition(); 
    
    def _dumpsigns(self, command):
        """
    dumpSigns [ <filename> ]
    
    Saves the text and location of every sign in the world to a text file. 
    With no filename, saves signs to <worldname>.signs
    
    Output is newline-delimited. 5 lines per sign. Coordinates are 
    on the first line, followed by four lines of sign text. For example:
    
        [229, 118, -15]
        "To boldy go
        where no man
        has gone
        before."
        
    Coordinates are ordered the same as point inputs: 
        [North/South, Down/Up, East/West]
        
    """
        if len(command):
            filename = command[0]
        else:
            filename = self.level.displayName + ".signs"
        
        outFile = file(filename, "w");
        
        print "Dumping signs..."
        signCount = 0;
        
        for i, cPos in enumerate(self.level.allChunks):
            try:
                chunk = self.level.getChunk(*cPos);
            except mclevel.ChunkMalformed:
                continue;
                
            for tileEntity in chunk.TileEntities:
                if tileEntity["id"].value == "Sign":
                    signCount += 1;
                    
                    outFile.write(str(map(lambda x:tileEntity[x].value, "xyz")) + "\n");
                    for i in range(4):
                        outFile.write(tileEntity["Text{0}".format(i+1)].value + "\n");
                    
            if i % 100 == 0:
                print "Chunk {0}...".format(i)
            
            chunk.unload();
        
        print "Dumped {0} signs to {1}".format(signCount, filename);
        
        outFile.close();
        
    def _removeentities(self, command):
        """
    removeEntities [ [except] [ <EntityID> [ <EntityID> ... ] ] ]
    
    Remove all entities matching one or more entity IDs.
    With the except keyword, removes all entities not 
    matching one or more entity IDs.
    
    Without any IDs, removes all entities in the world,
    except for Paintings.
    
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
            print "Removing all entities except Painting..."
            def match(entityID): return entityID != "Painting";
            
        for cx,cz in self.level.allChunks:
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
    createChunks <box>
    
    Creates any chunks not present in the specified region. 
    New chunks are filled with only air. New chunks are written
    to disk immediately.
    """
        if len(command) == 0:
            self.printUsage("createchunks")
            return;
        
        box = self.readBox(command)
        
        chunksCreated = self.level.createChunksInBox(box)
        
        print "Created {0} chunks." .format(len(chunksCreated))
        
        self.needsSave = True;

    def _deletechunks(self, command):
        """
    deleteChunks <box>
    
    Removes all chunks contained in the specified region. 
    Chunks are deleted from disk immediately.
    """
        if len(command) == 0:
            self.printUsage("deletechunks")
            return;
        
        box = self.readBox(command)
        
        deletedChunks = self.level.deleteChunksInBox(box)
        
        print "Deleted {0} chunks." .format(len(deletedChunks))
        
    def _prune(self, command):
        """
    prune <box>
    
    Removes all chunks not contained in the specified region. Useful for enforcing a finite map size.
    Chunks are deleted from disk immediately.
    """
        if len(command) == 0:
            self.printUsage("prune")
            return;
        
        box = self.readBox(command)
        
        i=0;
        for cx,cz in self.level.allChunks:
            if cx < box.mincx or cx >= box.maxcx or cz < box.mincz or cz >= box.maxcz:
                self.level.deleteChunk(cx,cz)
                i+=1;
                
        print "Pruned {0} chunks." .format(i)
    
    def _relight(self, command):
        """
    relight [ <box> ]
    
    Recalculates lights in the region specified. If omitted, 
    recalculates the entire world.
    """
        if len(command):
            box = self.readBox(command)
            chunks = itertools.product(range(box.mincx, box.maxcx),range(box.mincz, box.maxcz))
        
        else:
            chunks = self.level.allChunks
            
        self.level.generateLights(chunks)
        
        print "Relit 0 chunks." 
        self.needsSave = True;
    
    def _create(self, command):
        """
    create [ <filename> ]
    
    Create and load a new Minecraft Alpha world. This world will have no 
    chunks and a random terrain seed. If run from the shell, filename is not
    needed because you already specified a filename earlier in the command.
    For example: 
        
        mce.py MyWorld create
        
    """
        if len(command) < 1:
            raise UsageError, "Expected a filename"
        
        filename = command[0];
        if not os.path.exists(filename):
            os.mkdir(filename);

        if not os.path.isdir(filename):
            raise IOError, "{0} already exists".format(filename)
        
        if mclevel.MCInfdevOldLevel.isLevel(filename):
            raise IOError, "{0} is already a Minecraft Alpha world".format(filename)
        
        level = mclevel.MCInfdevOldLevel(filename, create = True);
        
        self.level = level;
        
                
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
        box = self.level.bounds;
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
    
    def _time(self, command):
        """
    time [time of day]
    
    Set or display the time of day. Acceptable values are "morning", "noon", 
    "evening", "midnight", or a time of day such as 8:02, 12:30 PM, or 16:45.
    """
        ticks = self.level.Time
        timeOfDay = ticks % 24000;
        ageInTicks = ticks - timeOfDay;
        if len(command) == 0:
            
            days = ageInTicks / 24000
            hours = timeOfDay / 1000;
            clockHours = (hours + 6) % 24
            
            ampm = ("AM", "PM")[clockHours > 11]
            
            minutes = (timeOfDay % 1000) / 60;
            
            print "It is {0}:{1:02} {2} on Day {3}".format(clockHours%12 or 12, minutes, ampm, days)
        else:
            times = { "morning":6, "noon":12, "evening":18, "midnight":24 }
            word = command[0];
            minutes = 0;
            
            if word in times:
                hours = times[word]
            else:
                try:
                    if ":" in word:
                        h, m = word.split(":")
                        hours = int(h)
                        minutes = int(m)
                    else:
                        hours = int(word)
                except Exception, e:
                    raise UsageError, ("Cannot interpret time, ", e);
                    
                if len(command) > 1:
                    if command[1].lower() == "pm":
                        hours += 12;
                
            ticks = ageInTicks + hours * 1000 + minutes * 1000 / 60 - 6000;
            if ticks < 0: ticks += 18000
            
            ampm = ("AM", "PM")[hours > 11 and hours < 24]
            print "Changed time to {0}:{1:02} {2}".format(hours%12 or 12, minutes, ampm)
            self.level.Time = ticks
            self.needsSave = True;
    
    def _randomseed(self, command):
        """
    randomseed [ <seed> ]
    
    Set or display the world's random seed, a 64-bit integer that uniquely
    defines the world's terrain.
    """
        if len(command):
            try:
                seed = long(command[0]);
            except ValueError:
                raise UsageError, "Expected a long integer."
            
            self.level.RandomSeed = seed;
            
        else:
            print "Random Seed: ", self.level.RandomSeed
    
    def _worldsize(self, command):
        """
    worldsize
    
    Computes and prints the dimensions of the world.  For infinite worlds, 
    also prints the most negative corner.
    """
        bounds = self.level.bounds;
        if isinstance(self.level, mclevel.MCInfdevOldLevel):
            print "\nWorld size: \n  {0[0]:7} north to south\n  {0[2]:7} east to west\n".format(bounds.size);
            print "Smallest and largest points: ({0[0]},{0[2]}), ({1[0]},{1[2]})".format(bounds.origin, bounds.maximum);
            
        else:
            print "\nWorld size: \n  {0[0]:7} wide\n  {0[1]:7} tall\n  {0[2]:7} long\n".format(bounds.size);
            
    def _heightmap(self,command):
        """
    heightmap <filename>

    Takes a png and imports it as the terrain starting at chunk 0,0.
    Data is internally converted to greyscale and scaled to the maximum height.
    The game will fill the terrain with trees and mineral deposits the next
    time you play the level.

    Please please please try out a small test image before using a big source.
    Using the levels tool to get a good heightmap is an art, not a science.
    A smaller map lets you experiment and get it right before having to blow
    all night generating the really big map.

    Requires the PIL library.
    """
        if len(command) == 0:
            self.printUsage("heightmap")
            return

        if raw_input(
     "This will destroy a large portion of the map and may take a long time.  Did you really want to do this?"
     ).lower() in ("yes", "y", "1", "true"):
         
            
            from PIL import Image
            import datetime

            filename = command.pop(0)

            imgobj = Image.open(filename)
            
            greyimg = imgobj.convert("L") #luminance
            
            imgarray = numpy.asarray(greyimg)
            
            width, height = greyimg.size
            
            imgarray = imgarray / 2; #scale to 0-127
            
            water_level = 64  
            
            xchunks = (height+15)/16
            zchunks = (width+15)/16

            start = datetime.datetime.now()
            for cx in range(xchunks):
                for cz in range(zchunks):
                    try:
                        self.level.createChunk(cx,cz)
                    except:
                        pass
                    c = self.level.getChunk(cx,cz)
                    for x in range(16):
                        for z in range(16):
                            if z+(cz*16) < width-1 and x+(cx*16) < height-1:
                                #world dimension X goes north-south
                                #first array axis goes up-down
                                
                                h = imgarray[x+(cx*16),z+(cz*16)]
                                
                                c.Blocks[x,z,h+1:] = 0 #air
                                c.Blocks[x,z,h:h+1] = 2 #grass
                                c.Blocks[x,z,h-4:h] = 3 #dirt
                                c.Blocks[x,z,:h-4] = 1 #rock

                                if h < water_level:
                                    c.Blocks[x,z,h+1:water_level] = 9 #water
                                if h < water_level+2:
                                    c.Blocks[x,z,h-2:h+1] = 12 #sand if it's near water level
                                    
                                c.Blocks[x,z,0] = 7 #bedrock
                                
                    c.chunkChanged()
                    c.TerrainPopulated = False
                    #the quick lighting from chunkChanged has already lit this simple terrain completely
                    c.needsLighting = False 
                    
                    print "%s Just did chunk %d,%d" % (datetime.datetime.now().strftime("[%H:%M:%S]"),cx,cz)

            print "Done with mapping!"
            self.needsSave = True;
            stop = datetime.datetime.now()
            print "Took %s." % str(stop-start)
            
            spawnz = width / 2
            spawnx = height / 2;
            spawny = imgarray[spawnx, spawnz];
            print "You probably want to change your spawn point. I suggest {0}".format( (spawnx, spawny, spawnz) )
            
    def _execute(self, command):
		"""
    execute <filename>
    Execute all commands in a file and save.
    """
		if len(command) == 0:
			print "You must give the file with commands to execute"
		else:
			commandFile = open(command[0],"r")
			commandsFromFile = commandFile.readlines()
			for commandFromFile in commandsFromFile:
				print commandFromFile
				self.processCommand(commandFromFile.split())
			self._save("")
		
    def _quit(self, command):
        """
    quit [ yes | no ]
    
    Quits the program. 
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
        self.level = mclevel.fromFile(self.filename);
    
    def _dimension(self, command):
        """
    dimension [ <dim> ]
    
    Load another dimension, a sub-world of this level. Without options, lists
    all of the dimensions found in this world. <dim> can be a number or one of 
    these keywords: 
        nether, hell, slip: DIM-1
        earth, overworld, parent: parent world
    """
        
        if len(command):
            if command[0].lower() in ("earth", "overworld", "parent"):
                if self.level.parentWorld:
                    self.level = self.level.parentWorld
                    return;
                else:
                    print "You are already on earth."
                    return;
                    
            elif command[0].lower() in ("hell", "nether", "slip"):
                dimNo = -1
            else:
                dimNo = self.readInt(command);
                
            if dimNo in self.level.dimensions:
                self.level = self.level.dimensions[dimNo]
                return;
        
        if self.level.parentWorld:
            print "Parent world: {0} ('dimension parent' to return)".format(self.level.parentWorld.displayName);
            
        if len(self.level.dimensions):
            print "Dimensions in {0}:".format(self.level.displayName)
            for k in self.level.dimensions:
                print "{0}: {1}".format(k, mclevel.MCAlphaDimension.dimensionNames.get(k, "Unknown"));
        
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
            print self.__doc__.format(commandPrefix=("","mce.py <world> ")[not self.batchMode]);
        
        
    def printUsageAndQuit(self):
        self.printUsage();
        raise UsageError;
    
    def loadWorld(self, world):
        try:
            worldNum = int(world)
        except ValueError:
            self.level = mclevel.fromFile(world)
            
            self.filename = self.level.filename
            
            
            
        else:
            if str(worldNum) == world:
                if worldNum > 0 and worldNum <= 5:
                    self.level = mclevel.loadWorldNumber(worldNum)
                    self.filename = self.level.filename
                    
                    
                
        
    
    level = None  
    
    batchMode = False;

    def run(self):
        logging.basicConfig(format='%(levelname)s:%(message)s')
        logging.getLogger().level = logging.INFO
    
        appPath = sys.argv.pop(0)
        
        if len(sys.argv):
            world = sys.argv.pop(0)
            if len(sys.argv) and sys.argv[0].lower() == "create":
                #accept the syntax, "mce world3 create"
                self._create([world]);
                print "Created world {0}".format(world);
                
                sys.exit(0)
            else:
                self.loadWorld(world)
        else:
            self.batchMode = True;
            self.printUsage();
            while True:
                try:
                    world = raw_input("Please enter world number or path to world folder: ")
                    self.loadWorld(world)
                except EOFError, e:
                    print "End of input."
                    raise SystemExit;
                except Exception, e:
                    print "Cannot open {0}: {1}".format(world, e);
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
                    command = raw_input("{0}> ".format(self.level.displayName))
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
                    print 'Exception during command: {0!r}'.format(e);
                    print "Use 'debug' to enable tracebacks."
                    
                    #self.printUsage();
                    
                
    def processCommand(self, command):
        keyword = command.pop(0).lower()
        if not keyword in self.commands:
            matches = filter(lambda x:x.startswith(keyword), self.commands);
            if len(matches) == 1:
                keyword = matches[0];
            elif len(matches):
                print "Ambiguous command. Matches: "
                for k in matches:
                    print "  ",k;
                return;
            else:
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
            

def main(argv):
    profile = os.getenv("MCE_PROFILE", None)
    editor = mce()
    if profile:
        print "Profiling enabled"
        import cProfile
        cProfile.runctx('editor.run()', locals(), globals(), profile)
    else:
        editor.run()

    return 0
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
        
