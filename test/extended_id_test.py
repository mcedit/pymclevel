from pymclevel.schematic import MCSchematic
from pymclevel import MCInfdevOldLevel
from templevel import TempLevel

__author__ = 'Rio'

def test_schematic_extended_ids():
    s = MCSchematic(shape=(1, 1, 5))
    s.Blocks[0,0,0] = 2048
    temp = TempLevel("schematic", createFunc=s.saveToFile)
    s = temp.level
    assert s.Blocks[0,0,0] == 2048


def test_alpha_extended_ids():
    temp = TempLevel("alpha", createFunc=lambda f: MCInfdevOldLevel(f, create=True))
    level = temp.level
    level.createChunk(0, 0)

    level.setBlockAt(0,2,5, 2048)
    level.saveInPlace()
    level.close()

    level = MCInfdevOldLevel(filename=level.filename)

    assert level.blockAt(0,2,5) == 2048

