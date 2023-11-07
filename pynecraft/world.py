from chunk import Chunk
from constants import *
from numba.typed import Dict
import multiprocessing
import time
from OpenGL.GL import *
import utils
import chunk_builder

def chunk_provider(chunkX, chunkZ, CHUNK_SIZE, CHUNK_HEIGHT):
    import glm
    from random import randint
    import numpy as np
    from numba import uint8
    
    def flatten_coord(x, y, z):
        return x + CHUNK_SIZE * z + CHUNK_SIZE**2 * y

    def to_uint8(a, b, c, d, e):
        return uint8(a), uint8(b), uint8(c), uint8(d), uint8(e)

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

    def add_face(vertex_data, index, vertices):
        for vertex in vertices:
            for attr in vertex:
                vertex_data[index] = attr
                index += 1
        return index

    blocks = np.zeros(CHUNK_SIZE ** 2 * CHUNK_HEIGHT, dtype='uint8')
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            # 0.02 - Scale, higher = smaller hills in the xy direction (less fat)
            # 8 - Amplitude, higher = taller hills, lower valleys
            # 32 - Sea level
            local_height = int(glm.simplex(glm.vec2(chunkX*CHUNK_SIZE + x, chunkZ*CHUNK_SIZE + z) * 0.02) * 8 + 64)
            if local_height < 0:
                continue
            for y in range(min(local_height, CHUNK_HEIGHT)):
                if local_height - y <= 1:
                    blocks[flatten_coord(x, y, z)] = 2
                elif local_height - y <= 3:
                    blocks[flatten_coord(x, y, z)] = 3
                else:
                    blocks[flatten_coord(x, y, z)] = randint(4, 7)

    def gen_vertices():
        vertex_data = np.empty(CHUNK_SIZE**2 * CHUNK_HEIGHT * 18 * 5, dtype="uint8")
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

    return chunkX, chunkZ, blocks, gen_vertices()
    

class World:
    def __init__(self, app):
        self.app = app
        self.chunks = {}
        self.pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        self.numba_chunks = Dict()
        self.needs_building = {}
        self.gen_queue = set()

    def get_chunk(self, x, z):
        loc = (x, z)
        return self.chunks[loc] if loc in self.chunks else None

    def gen_chunk(self, x, z, blocks=[]):
        self.chunks[(x, z)] = Chunk(self.app, position=[x*CHUNK_SIZE, 0, z*CHUNK_SIZE], blocks=blocks)
        self.numba_chunks[(x, z)] = self.chunks[(x, z)].blocks

    def build_chunk(self, x, z, vertices=[]):
        if (x, z) in self.chunks:
            self.chunks[(x, z)].build(vertices)

    def render_chunks(self, position, isAsync=False):
        chunk_pos = (int(position[0] // CHUNK_SIZE), int(position[2] // CHUNK_SIZE))
        for x in range(int(chunk_pos[0] - RENDER_DISTANCE), int(chunk_pos[0] + RENDER_DISTANCE + 1)):
            for z in range(int(chunk_pos[1] - RENDER_DISTANCE), int(chunk_pos[1] + RENDER_DISTANCE + 1)):
                if (x, z) not in self.chunks:
                    if (x, z) in self.needs_building:
                        self.gen_chunk(x, z, self.needs_building[(x, z)][0])
                        self.build_chunk(x, z)
                        del self.needs_building[(x, z)]
                    elif (x, z) not in self.gen_queue:
                        if isAsync:
                            self.gen_queue.add((x, z))

                            # To generate new VBOs, I guess add to a set of the chunks that need it?

                            def call(result):
                                print("generated")
                                self.gen_queue.remove((result[0], result[1]))
                                self.needs_building[(result[0], result[1])] = (result[2], result[3])
                                
                            def error(err):
                                print(err)

                            res = self.pool.apply_async(chunk_provider, (x, z, CHUNK_SIZE, CHUNK_HEIGHT), callback=call, error_callback=error)
                            print("async applied!")
                        else:
                            self.gen_chunk(x, z)
                            self.build_chunk(x, z)
                else:
                    self.chunks[(x, z)].draw()