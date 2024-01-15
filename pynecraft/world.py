from chunk import Chunk
from constants import *
from numba.typed import Dict
import multiprocessing
import time
from OpenGL.GL import *
from world_gen import generate_terrain, getRandom
from chunk_builder import flatten_coord, to_uint8, is_empty, add_face, build_chunk

import random

def chunk_provider(chunkX, chunkZ, CHUNK_SIZE, CHUNK_HEIGHT, flatten_coord, to_uint8, is_empty, add_face, build_chunk, generate_terrain, seed, getRandom):
    import glm
    import numpy as np
    from opensimplex.internals import _noise2, _noise3, _init

    perm, perm_grad_index3 = _init(seed)

    blocks = generate_terrain(CHUNK_SIZE, CHUNK_HEIGHT, chunkX, chunkZ, flatten_coord, np.zeros(CHUNK_SIZE ** 2 * CHUNK_HEIGHT, dtype='uint8'), perm, perm_grad_index3, _noise2, _noise3, getRandom)

    return chunkX, chunkZ, blocks, build_chunk(chunkX, 0, chunkZ, blocks)
    

class World:
    def __init__(self, app):
        self.app = app
        self.chunks = {}
        self.pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        self.numba_chunks = Dict()
        self.needs_building = {}
        self.gen_queue = set()
        self.firstLoad = False

    def get_chunk(self, x, z):
        loc = (x, z)
        return self.chunks[loc] if loc in self.chunks else None

    def gen_chunk(self, x, z, blocks=[]):
        self.chunks[(x, z)] = Chunk(self.app, position=[x*CHUNK_SIZE, 0, z*CHUNK_SIZE], blocks=blocks)
        self.numba_chunks[(x, z)] = self.chunks[(x, z)].blocks

    def build_chunk(self, x, z, vertices=[]):
        if (x, z) in self.chunks:
            self.chunks[(x, z)].build(vertices)

    def get_block(self, x, y, z):
        chunkX = x // CHUNK_SIZE
        chunkZ = z // CHUNK_SIZE
        if (chunkX, chunkZ) in self.chunks and y < 255:
            return self.chunks[(chunkX, chunkZ)].blocks[flatten_coord(x % CHUNK_SIZE, y, z % CHUNK_SIZE)]
        return False

    def render_chunks(self, position, isAsync=False):

        # Only allow chunks to be built if all their neighbors have blocks loaded. Otherwise, add the others to the gen queue with blocksOnly = True, and build the current chunk with blocksOnly = True
        # 
        chunk_pos = (int(position[0] // CHUNK_SIZE), int(position[2] // CHUNK_SIZE))
        for x in range(int(chunk_pos[0] - RENDER_DISTANCE), int(chunk_pos[0] + RENDER_DISTANCE + 1)):
            for z in range(int(chunk_pos[1] - RENDER_DISTANCE), int(chunk_pos[1] + RENDER_DISTANCE + 1)):
                if (x, z) not in self.chunks:
                    if (x, z) in self.needs_building:
                        self.gen_chunk(x, z, self.needs_building[(x, z)][0])
                        self.build_chunk(x, z)
                        self.firstLoad = True
                        del self.needs_building[(x, z)]
                    elif (x, z) not in self.gen_queue:
                        if isAsync:
                            self.gen_queue.add((x, z))

                            def call(result):
                                self.needs_building[(result[0], result[1])] = (result[2], result[3])
                                self.gen_queue.remove((result[0], result[1]))
                                
                            def error(err):
                                print(err)

                            res = self.pool.apply_async(chunk_provider, (x, z, CHUNK_SIZE, CHUNK_HEIGHT, flatten_coord, to_uint8, is_empty, add_face, build_chunk, generate_terrain, WORLD_SEED, getRandom), callback=call, error_callback=error)
                        else:
                            res = chunk_provider(x, z, CHUNK_SIZE, CHUNK_HEIGHT, flatten_coord, to_uint8, is_empty, add_face, build_chunk, generate_terrain, WORLD_SEED, getRandom)
                            self.needs_building[(res[0], res[1])] = (res[2], res[3])

                else:
                    self.chunks[(x, z)].draw()