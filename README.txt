Python library for reading Minecraft levels.

Can read Alpha levels, Indev levels, and Creative levels (with help).

Includes a command-line client (mce.py)

Requires numpy.

Read mclevel.py to get started.

See LICENSE.txt for licensing terms.



mce.py is a command-line editor for SMP maps. It can be used interactively from a terminal, accept editing commands on standard input, or run a single editing command from the shell.

Sample usage:

% python mce.py
    Usage:

    Block commands:
       clone <sourcePoint> <sourceSize> <destPoint>
       fill <blockType> [ <point> <size> ]
       replace <blockType> [with] <newBlockType> [ <point> <size> ]

       export <filename> <sourcePoint> <sourceSize>
       import <filename> <destPoint>

    Player commands:
       player [ <player> [ <point> ] ]
       spawn [ <point> ]

    Entity commands:
       removeEntities [ <EntityID> ]

    Chunk commands:
       createChunks <point> <size>
       deleteChunks <point> <size>
       prune <point> <size>
       relight [ <point> <size> ]

    World commands:
       degrief

    Editor commands:
       save
       reload
       load <filename> | <world number>
       quit

    Informational:
       blocks [ <block name> | <block ID> ]
       help [ <command> ]
       
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

