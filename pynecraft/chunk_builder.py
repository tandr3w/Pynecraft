from constants import *
import utils
import numpy as np

def is_empty(blocks, x, y, z):
    if x >= 0 and x < CHUNK_SIZE and y >= 0 and y < CHUNK_SIZE and z >= 0 and z < CHUNK_SIZE:
        if blocks[utils.flatten_coord(x, y, z)] == 0:
            return False 
    return True

add_count = 0
def add_face(vertex_data, index, vertices):
    global add_count
    add_count += 1
    for data in vertices:
        vertex_data[index] = data
        index += 1
    return index

def build_chunk(blocks):
    vertex_data = np.empty(CHUNK_SIZE**3 * 36 * 5, dtype=np.float32)
    index = 0

    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                block_type = blocks[utils.flatten_coord(x, y, z)]
                if block_type == 0:
                    continue

                # (x, y, z) for a block is the pos of the bottom left corner
                # Only render faces that are not blocked by other faces

                # Top face
                if is_empty(blocks, x, y+1, z):
                    index = add_face(vertex_data, index, (
                        x, y+1, z, block_type, 0,
                        x, y+1, z+1, block_type, 0,
                        x+1, y+1, z+1, block_type, 0,
                        x, y+1, z, block_type, 0,
                        x+1, y+1, z+1, block_type, 0,
                        x+1, y+1, z, block_type, 0
                    ))

                # Bottom Face
                if is_empty(blocks, x, y-1, z):
                    index = add_face(vertex_data, index, (
                        x, y, z, block_type, 1,
                        x+1, y, z+1, block_type, 1,
                        x, y, z+1, block_type, 1,
                        x, y, z, block_type, 1,
                        x+1, y, z, block_type, 1,
                        x+1, y, z+1, block_type, 1
                    ))

                # Right Face
                if is_empty(blocks, x+1, y, z):
                    index = add_face(vertex_data, index, (
                        x+1, y, z, block_type, 2,
                        x+1, y+1, z, block_type, 2,
                        x+1, y+1, z+1, block_type, 2,
                        x+1, y, z, block_type, 2,
                        x+1, y+1, z+1, block_type, 2,
                        x+1, y, z+1, block_type, 2
                    ))

                # Left Face
                if is_empty(blocks, x-1, y, z):
                    index = add_face(vertex_data, index, (
                        x, y, z, block_type, 3,
                        x, y+1, z+1, block_type, 3,
                        x, y+1, z, block_type, 3,
                        x, y, z, block_type, 3,
                        x, y, z+1, block_type, 3,
                        x, y+1, z+1, block_type, 3,
                    ))

                # Back face
                if is_empty(blocks, x, y, z-1):
                    index = add_face(vertex_data, index, (
                        x, y, z, block_type, 4,
                        x, y+1, z, block_type, 4,
                        x+1, y+1, z, block_type, 4,
                        x, y, z, block_type, 4,
                        x+1, y+1, z, block_type, 4,
                        x+1, y, z, block_type, 4
                    ))

                # Front face
                if is_empty(blocks, x, y, z+1):
                    index = add_face(vertex_data, index, (
                        x, y, z+1, block_type, 5,
                        x+1, y+1, z+1, block_type, 5,
                        x, y+1, z+1, block_type, 5,
                        x, y, z+1, block_type, 5,
                        x+1, y, z+1, block_type, 5,
                        x+1, y+1, z+1, block_type, 5,
                    ))
    return vertex_data[:index + 1]