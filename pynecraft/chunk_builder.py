from constants import *
import utils
import numpy as np
from numba import njit, uint8

@njit
def flatten_coord(x, y, z):
    return x + CHUNK_SIZE * z + CHUNK_SIZE**2 * y

@njit
def to_uint8(a, b, c, d, e, f):
    return uint8(a), uint8(b), uint8(c), uint8(d), uint8(e), uint8(f)

@njit
def is_empty(chunkX, chunkZ, blocks, x, y, z):
    if x < 0:
        # if (chunkX - 1, chunkZ) in world:
        #     if world[(chunkX - 1, chunkZ)][flatten_coord(CHUNK_SIZE - 1, y, z)]:
        #         return False
        return True
    elif y < 0:
        return True
    elif z < 0:
        # if (chunkX, chunkZ - 1) in world:
        #     if world[(chunkX, chunkZ - 1)][flatten_coord(x, y, CHUNK_SIZE - 1)]:
        #         return False
        return True
    elif x >= CHUNK_SIZE:
        # if (chunkX + 1, chunkZ) in world:
        #     if world[(chunkX + 1, chunkZ)][flatten_coord(0, y, z)]:
        #         return False
        return True
    elif y >= CHUNK_HEIGHT:
        return True
    elif z >= CHUNK_SIZE:
        # if (chunkX, chunkZ + 1) in world:
        #     if world[(chunkX, chunkZ + 1)][flatten_coord(x, y, 0)]:
        #         return False
        return True
    elif blocks[flatten_coord(x, y, z)]:
        return False 
    else:
        return True


# 1 = X plane
# 2 = Y plane
# 3 = Z plane
# Checks how many blocks are neighboring each vertex of a face ("occluding it")
@njit
def get_occlusion(chunkX, chunkZ, blocks, pos, plane):
    x, y, z = pos
    if plane == 1:
        return (is_empty(chunkX, chunkZ, blocks, x, y, z-1) + is_empty(chunkX, chunkZ, blocks, x, y-1, z-1) + is_empty(chunkX, chunkZ, blocks, x, y-1, z),
                is_empty(chunkX, chunkZ, blocks, x, y+1, z) + is_empty(chunkX, chunkZ, blocks, x, y+1, z-1) + is_empty(chunkX, chunkZ, blocks, x, y, z-1),
                is_empty(chunkX, chunkZ, blocks, x, y, z+1) + is_empty(chunkX, chunkZ, blocks, x, y+1, z+1) + is_empty(chunkX, chunkZ, blocks, x, y+1, z),
                is_empty(chunkX, chunkZ, blocks, x, y-1, z) + is_empty(chunkX, chunkZ, blocks, x, y-1, z+1) + is_empty(chunkX, chunkZ, blocks, x, y, z+1))
    elif plane == 2:
        return (is_empty(chunkX, chunkZ, blocks, x, y, z-1) + is_empty(chunkX, chunkZ, blocks, x-1, y, z-1) + is_empty(chunkX, chunkZ, blocks, x-1, y, z),
                is_empty(chunkX, chunkZ, blocks, x+1, y, z) + is_empty(chunkX, chunkZ, blocks, x+1, y, z-1) + is_empty(chunkX, chunkZ, blocks, x, y, z-1),
                is_empty(chunkX, chunkZ, blocks, x, y, z+1) + is_empty(chunkX, chunkZ, blocks, x+1, y, z+1) + is_empty(chunkX, chunkZ, blocks, x+1, y, z),
                is_empty(chunkX, chunkZ, blocks, x-1, y, z) + is_empty(chunkX, chunkZ, blocks, x-1, y, z+1) + is_empty(chunkX, chunkZ, blocks, x, y, z+1))
    elif plane == 3:
        return (is_empty(chunkX, chunkZ, blocks, x-1, y, z) + is_empty(chunkX, chunkZ, blocks, x-1, y-1, z) + is_empty(chunkX, chunkZ, blocks, x, y-1, z),
                is_empty(chunkX, chunkZ, blocks, x, y+1, z) + is_empty(chunkX, chunkZ, blocks, x-1, y+1, z) + is_empty(chunkX, chunkZ, blocks, x-1, y, z),
                is_empty(chunkX, chunkZ, blocks, x+1, y, z) + is_empty(chunkX, chunkZ, blocks, x+1, y+1, z) + is_empty(chunkX, chunkZ, blocks, x, y+1, z),
                is_empty(chunkX, chunkZ, blocks, x, y-1, z) + is_empty(chunkX, chunkZ, blocks, x+1, y-1, z) + is_empty(chunkX, chunkZ, blocks, x+1, y, z))
    return 0, 0, 0, 0

@njit
def add_face(vertex_data, index, vertices):
    for vertex in vertices:
        for attr in vertex:
            vertex_data[index] = attr
            index += 1
    return index

@njit
def build_chunk(chunkX, chunkY, chunkZ, blocks):
    vertex_data = np.empty(CHUNK_SIZE**2 * CHUNK_HEIGHT * 18 * 6, dtype="uint8")
    index = 0

    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_HEIGHT):
            for z in range(CHUNK_SIZE):
                block_type = blocks[flatten_coord(x, y, z)]
                if block_type == 0:
                    continue

                # (x, y, z) for a block is the pos of the bottom left corner
                # Only render faces that are not blocked by other faces

                # Top face
                if is_empty(chunkX, chunkZ, blocks, x, y+1, z):
                    occ = get_occlusion(chunkX, chunkZ, blocks, (x, y+1, z), 2)
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y+1, z, block_type, 0, occ[0]),
                        to_uint8(x, y+1, z+1, block_type, 0, occ[3]),
                        to_uint8(x+1, y+1, z+1, block_type, 0, occ[2]),
                        to_uint8(x, y+1, z, block_type, 0, occ[0]),
                        to_uint8(x+1, y+1, z+1, block_type, 0, occ[2]),
                        to_uint8(x+1, y+1, z, block_type, 0, occ[1])
                    ))

                # Bottom Face
                if is_empty(chunkX, chunkZ, blocks, x, y-1, z):
                    occ = get_occlusion(chunkX, chunkZ, blocks, (x, y-1, z), 2)
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y, z, block_type, 1, occ[0]),
                        to_uint8(x+1, y, z+1, block_type, 1, occ[2]),
                        to_uint8(x, y, z+1, block_type, 1, occ[3]),
                        to_uint8(x, y, z, block_type, 1, occ[0]),
                        to_uint8(x+1, y, z, block_type, 1, occ[1]),
                        to_uint8(x+1, y, z+1, block_type, 1, occ[2])
                    ))

                # Right Face
                if is_empty(chunkX, chunkZ, blocks, x+1, y, z):
                    occ = get_occlusion(chunkX, chunkZ, blocks, (x+1, y, z), 1)
                    index = add_face(vertex_data, index, (
                        to_uint8(x+1, y, z, block_type, 2, occ[0]),
                        to_uint8(x+1, y+1, z, block_type, 2, occ[1]),
                        to_uint8(x+1, y+1, z+1, block_type, 2, occ[2]),
                        to_uint8(x+1, y, z, block_type, 2, occ[0]),
                        to_uint8(x+1, y+1, z+1, block_type, 2, occ[2]),
                        to_uint8(x+1, y, z+1, block_type, 2, occ[3])
                    ))

                # Left Face
                if is_empty(chunkX, chunkZ, blocks, x-1, y, z):
                    occ = get_occlusion(chunkX, chunkZ, blocks, (x-1, y, z), 1)
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y, z, block_type, 3, occ[0]),
                        to_uint8(x, y+1, z+1, block_type, 3, occ[2]),
                        to_uint8(x, y+1, z, block_type, 3, occ[1]),
                        to_uint8(x, y, z, block_type, 3, occ[0]),
                        to_uint8(x, y, z+1, block_type, 3, occ[3]),
                        to_uint8(x, y+1, z+1, block_type, 3, occ[2]),
                    ))

                # Back face
                if is_empty(chunkX, chunkZ, blocks, x, y, z-1):
                    occ = get_occlusion(chunkX, chunkZ, blocks, (x, y, z-1), 3)
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y, z, block_type, 4, occ[0]),
                        to_uint8(x, y+1, z, block_type, 4, occ[1]),
                        to_uint8(x+1, y+1, z, block_type, 4, occ[2]),
                        to_uint8(x, y, z, block_type, 4, occ[0]),
                        to_uint8(x+1, y+1, z, block_type, 4, occ[2]),
                        to_uint8(x+1, y, z, block_type, 4, occ[3])
                    ))

                # Front face
                if is_empty(chunkX, chunkZ, blocks, x, y, z+1):
                    occ = get_occlusion(chunkX, chunkZ, blocks, (x, y, z+1), 3)
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y, z+1, block_type, 5, occ[0]),
                        to_uint8(x+1, y+1, z+1, block_type, 5, occ[2]),
                        to_uint8(x, y+1, z+1, block_type, 5, occ[1]),
                        to_uint8(x, y, z+1, block_type, 5, occ[0]),
                        to_uint8(x+1, y, z+1, block_type, 5, occ[3]),
                        to_uint8(x+1, y+1, z+1, block_type, 5, occ[2]),
                    ))
                    
    return vertex_data[:index + 1]