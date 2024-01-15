from constants import *
import numpy as np
from numba import njit, uint8

@njit
def flatten_coord(x, y, z):
    # Converts 3d coordinates into a single integer
    return x + CHUNK_SIZE * z + CHUNK_SIZE**2 * y

@njit
def to_uint8(a, b, c, d, e):
    # Converts python integers into uint8 for use in OpenGL
    return uint8(a), uint8(b), uint8(c), uint8(d), uint8(e)

@njit
def is_empty(chunkX, chunkZ, blocks, x, y, z):
    # Checks if a block exists at a given position
    if x < 0:
        return True
    elif y < 0:
        return True
    elif z < 0:
        return True
    elif x >= CHUNK_SIZE:
        return True
    elif y >= CHUNK_HEIGHT:
        return True
    elif z >= CHUNK_SIZE:
        return True
    elif blocks[flatten_coord(x, y, z)]:
        return False 
    else:
        return True

@njit
def add_face(vertex_data, index, vertices):
    # Utility function for simulating "append" inside a numpy array
    for vertex in vertices:
        for attr in vertex:
            vertex_data[index] = attr
            index += 1
    return index

@njit
def build_chunk(chunkX, chunkY, chunkZ, blocks):
    vertex_data = np.empty(CHUNK_SIZE**2 * CHUNK_HEIGHT * 18 * 5, dtype="uint8") # Initialize array of vertices
    index = 0

    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_HEIGHT):
            for z in range(CHUNK_SIZE):
                block_type = blocks[flatten_coord(x, y, z)]

                if block_type == 0: # Don't render air
                    continue

                # (x, y, z) for a block is the pos of the bottom left corner
                # block_type dictates what block 

                # the 6th value in to_uint8 represents the Face ID

                # Top face
                if is_empty(chunkX, chunkZ, blocks, x, y+1, z): # Only render faces that are not blocked by other faces
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y+1, z, block_type, 0),
                        to_uint8(x, y+1, z+1, block_type, 0),
                        to_uint8(x+1, y+1, z+1, block_type, 0),
                        to_uint8(x, y+1, z, block_type, 0),
                        to_uint8(x+1, y+1, z+1, block_type, 0),
                        to_uint8(x+1, y+1, z, block_type, 0)
                    ))

                # Bottom Face
                if is_empty(chunkX, chunkZ, blocks, x, y-1, z):
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y, z, block_type, 1),
                        to_uint8(x+1, y, z+1, block_type, 1),
                        to_uint8(x, y, z+1, block_type, 1),
                        to_uint8(x, y, z, block_type, 1),
                        to_uint8(x+1, y, z, block_type, 1),
                        to_uint8(x+1, y, z+1, block_type, 1)
                    ))

                # Right Face
                if is_empty(chunkX, chunkZ, blocks, x+1, y, z):
                    index = add_face(vertex_data, index, (
                        to_uint8(x+1, y, z, block_type, 2),
                        to_uint8(x+1, y+1, z, block_type, 2),
                        to_uint8(x+1, y+1, z+1, block_type, 2),
                        to_uint8(x+1, y, z, block_type, 2),
                        to_uint8(x+1, y+1, z+1, block_type, 2),
                        to_uint8(x+1, y, z+1, block_type, 2)
                    ))

                # Left Face
                if is_empty(chunkX, chunkZ, blocks, x-1, y, z):
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y, z, block_type, 3),
                        to_uint8(x, y+1, z+1, block_type, 3),
                        to_uint8(x, y+1, z, block_type, 3),
                        to_uint8(x, y, z, block_type, 3),
                        to_uint8(x, y, z+1, block_type, 3),
                        to_uint8(x, y+1, z+1, block_type, 3),
                    ))

                # Back face
                if is_empty(chunkX, chunkZ, blocks, x, y, z-1):
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y, z, block_type, 4),
                        to_uint8(x, y+1, z, block_type, 4),
                        to_uint8(x+1, y+1, z, block_type, 4),
                        to_uint8(x, y, z, block_type, 4),
                        to_uint8(x+1, y+1, z, block_type, 4),
                        to_uint8(x+1, y, z, block_type, 4)
                    ))

                # Front face
                if is_empty(chunkX, chunkZ, blocks, x, y, z+1):
                    index = add_face(vertex_data, index, (
                        to_uint8(x, y, z+1, block_type, 5),
                        to_uint8(x+1, y+1, z+1, block_type, 5),
                        to_uint8(x, y+1, z+1, block_type, 5),
                        to_uint8(x, y, z+1, block_type, 5),
                        to_uint8(x+1, y, z+1, block_type, 5),
                        to_uint8(x+1, y+1, z+1, block_type, 5),
                    ))
                    
    return vertex_data[:index + 1]