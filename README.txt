Python library for reading Minecraft levels.

Can read Alpha levels, Indev levels, and Creative levels (with help).

Includes a command-line client (mce.py)

Requires numpy.

Read mclevel.py to get started.




mce.py is a command-line editor for SMP maps. It can be used interactively from a terminal, accept editing commands on standard input, or run a single editing command from the shell.

Sample usage:

% python mce.py
    Usage:
       mce <world> clone <sourcePoint> <sourceSize> <destPoint>
       mce <world> fill <blockType> <destPoint> <destSize>
       mce <world> replace <blockType> [with] <withBlockType> <destPoint> <destS
ize>
       
       mce <world> export <filename> <sourcePoint> <sourceSize>
       mce <world> import <filename> <destPoint>
       
       mce <world> player <player> <point>
       mce <world> spawn <point>
       
       mce <world> createChunks <startChunk> <chunkSize>
       mce <world> deleteChunks <startChunk> <chunkSize>
       mce <world> prune <startChunk> <chunkSize>
       mce <world> relight <startChunk> <chunkSize>
       
    Points and sizes are space-separated triplets of numbers ordered X Y Z.
    X is position north-south, increasing southward. 
    Y is position up-down, increasing upward. 
    Z is position east-west, increasing westward.
    
    A player's name can be used to specify a point. 
    Use the keyword 'delta' to specify a point near a player. e.g.
    
       mce clone codewarrior 5 5 5 codewarrior delta 10 0 0
    
    In this command:
       'codewarrior' is the source point, 
       '5 5 5' is the size of the source box, and 
       'codewarrior delta 10 0 0' means 10 blocks south of me.
       
       
    
Please enter world number or path to world folder: 3
Identifying  C:\Users\Rio\AppData\Roaming\.minecraft\saves\World3\level.dat
Detected Infdev level.dat
Saved 0 chunks
Scanning for chunks...
World3> fill 20 Player delta -10 0 -10 20 20 20

Filled 8000 blocks.
World3> player Player

Player Player: [-1.7053128706213856, 62.620000004768372, 88.666301260713084]

World3> player Player Player delta 0 25 0

Moved player Player to (-1.7053128706213856, 87.620000004768372, 88.666301260713
084)
World3> save

Saved 6 chunks
World3> 

