from chunk import Chunk
from constants import *
from numba.typed import Dict
import multiprocessing
import time
from OpenGL.GL import *
import utils
from chunk_builder import flatten_coord, to_uint8, is_empty, add_face, build_chunk

def chunk_provider(chunkX, chunkZ, CHUNK_SIZE, CHUNK_HEIGHT, flatten_coord, to_uint8, is_empty, add_face, build_chunk):
    import glm
    from random import randint
    import numpy as np

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
                                self.gen_queue.remove((result[0], result[1]))
                                self.needs_building[(result[0], result[1])] = (result[2], result[3])
                                
                            def error(err):
                                print(err)

                            res = self.pool.apply_async(chunk_provider, (x, z, CHUNK_SIZE, CHUNK_HEIGHT, flatten_coord, to_uint8, is_empty, add_face, build_chunk), callback=call, error_callback=error)
                        else:
                            res = chunk_provider(x, z, CHUNK_SIZE, CHUNK_HEIGHT, flatten_coord, to_uint8, is_empty, add_face, build_chunk)
                            self.needs_building[(res[0], res[1])] = (res[2], res[3])

                else:
                    self.chunks[(x, z)].draw()