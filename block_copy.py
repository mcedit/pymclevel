from datetime import datetime
import logging
import numpy
from box import BoundingBox
from mclevelbase import exhaust
import materials

log = logging.getLogger(__name__)

def convertBlocks(destLevel, sourceLevel, blocks, blockData):
    return materials.convertBlocks(destLevel.materials, sourceLevel.materials, blocks, blockData)

def sourceMaskFunc(blocksToCopy):
    if blocksToCopy is not None:
        typemask = numpy.zeros(256, dtype='bool')
        typemask[blocksToCopy] = 1

        def maskedSourceMask(sourceBlocks):
            return typemask[sourceBlocks]

        return maskedSourceMask

    def unmaskedSourceMask(_sourceBlocks):
        return slice(None, None)

    return unmaskedSourceMask


def adjustCopyParameters(destLevel, sourceLevel, sourceBox, destinationPoint):
    # if the destination box is outside the level, it and the source corners are moved inward to fit.
    # ValueError is raised if the source corners are outside sourceLevel
    (x, y, z) = map(int, destinationPoint)

    sourceBox = BoundingBox(sourceBox.origin, sourceBox.size)

    (lx, ly, lz) = sourceBox.size
    log.debug(u"Asked to copy {0} blocks \n\tfrom {1} in {3}\n\tto {2} in {4}" .format(ly * lz * lx, sourceBox, destinationPoint, sourceLevel, destLevel))

    # clip the source ranges to this level's edges.  move the destination point as needed.
    # xxx abstract this
    if y < 0:
        sourceBox.origin[1] -= y
        sourceBox.size[1] += y
        y = 0
    if y + sourceBox.size[1] > destLevel.Height:
        sourceBox.size[1] -= y + sourceBox.size[1] - destLevel.Height
        y = destLevel.Height - sourceBox.size[1]

    # for infinite levels, don't clip along those dimensions because the
    # infinite copy func will just skip missing chunks
    if destLevel.Width != 0:
        if x < 0:
            sourceBox.origin[0] -= x
            sourceBox.size[0] += x
            x = 0
        if x + sourceBox.size[0] > destLevel.Width:
            sourceBox.size[0] -= x + sourceBox.size[0] - destLevel.Width
            # x=self.Width-sourceBox.size[0]

    if destLevel.Length != 0:
        if z < 0:
            sourceBox.origin[2] -= z
            sourceBox.size[2] += z
            z = 0
        if z + sourceBox.size[2] > destLevel.Length:
            sourceBox.size[2] -= z + sourceBox.size[2] - destLevel.Length
            # z=self.Length-sourceBox.size[2]

    destinationPoint = (x, y, z)

    return sourceBox, destinationPoint


def copyBlocksFromIter(destLevel, sourceLevel, sourceBox, destinationPoint, blocksToCopy=None, entities=True, create=False):
    """ copy blocks between two infinite levels by looping through the
    destination's chunks. make a sub-box of the source level for each chunk
    and copy block and entities in the sub box to the dest chunk."""

    (lx, ly, lz) = sourceBox.size

    sourceBox, destinationPoint = adjustCopyParameters(destLevel, sourceLevel, sourceBox, destinationPoint)
    # needs work xxx
    log.info(u"Copying {0} blocks from {1} to {2}" .format(ly * lz * lx, sourceBox, destinationPoint))
    startTime = datetime.now()

    destBox = BoundingBox(destinationPoint, sourceBox.size)
    chunkCount = destBox.chunkCount
    i = 0
    sourceMask = sourceMaskFunc(blocksToCopy)

    copyOffset = [d - s for s, d in zip(sourceBox.origin, destinationPoint)]

    # Visit each chunk in the destination area.
    #   Get the region of the source area corresponding to that chunk
    #   Visit each chunk of the region of the source area
    #     Get the slices of the destination chunk
    #     Get the slices of the source chunk
    #     Copy blocks and data

    for destCpos in destBox.chunkPositions:
        cx, cz = destCpos

        destChunkBox = BoundingBox((cx << 4, 0, cz << 4), (16, destLevel.Height, 16)).intersect(destBox)
        destChunkBoxInSourceLevel = BoundingBox([d - o for o, d in zip(copyOffset, destChunkBox.origin)], destChunkBox.size)

        if not destLevel.containsChunk(*destCpos):
            if create and any(sourceLevel.containsChunk(*c) for c in destChunkBoxInSourceLevel.chunkPositions):
                # Only create chunks in the destination level if the source level has chunks covering them.
                destLevel.createChunk(*destCpos)
            else:
                continue

        destChunk = destLevel.getChunk(*destCpos)


        i += 1
        yield (i, chunkCount)
        if i % 100 == 0:
            log.info("Chunk {0}...".format(i))

        for srcCpos in destChunkBoxInSourceLevel.chunkPositions:
            if not sourceLevel.containsChunk(*srcCpos):
                continue

            sourceChunk = sourceLevel.getChunk(*srcCpos)

            sourceChunkBox, sourceSlices = sourceChunk.getChunkSlicesForBox(destChunkBoxInSourceLevel)
            sourceChunkBoxInDestLevel = BoundingBox([d + o for o, d in zip(copyOffset, sourceChunkBox.origin)], sourceChunkBox.size)

            _, destSlices = destChunk.getChunkSlicesForBox(sourceChunkBoxInDestLevel)

            sourceBlocks = sourceChunk.Blocks[sourceSlices]
            sourceData = sourceChunk.Data[sourceSlices]

            mask = sourceMask(sourceBlocks)
            convertedSourceBlocks, convertedSourceData = convertBlocks(destLevel, sourceLevel, sourceBlocks, sourceData)

            destChunk.Blocks[destSlices][mask] = convertedSourceBlocks[mask]
            if convertedSourceData is not None:
                destChunk.Data[destSlices][mask] = convertedSourceData[mask]

        destChunk.chunkChanged()

    for i in destLevel.copyEntitiesFromIter(sourceLevel, sourceBox, destinationPoint, entities):
        yield i

    log.info("Duration: {0}".format(datetime.now() - startTime))

def copyBlocksFrom(destLevel, sourceLevel, sourceBox, destinationPoint, blocksToCopy=None, entities=True, create=False):
    return exhaust(copyBlocksFromIter(destLevel, sourceLevel, sourceBox, destinationPoint, blocksToCopy, entities, create))
