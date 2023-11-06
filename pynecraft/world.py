from chunk import Chunk
from constants import *
from numba.typed import Dict
import multiprocessing
import time
from OpenGL.GL import *
import utils

def chunk_provider(chunkX, chunkZ, CHUNK_SIZE, CHUNK_HEIGHT, flatten_coord):
    import glm
    from random import randint
    import numpy as np

    blocks = np.zeros(CHUNK_SIZE ** 2 * CHUNK_HEIGHT, dtype='uint8')
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            # 0.02 - Scale, higher = smaller hills in the xy direction (less fat)
            # 8 - Amplitude, higher = taller hills, lower valleys
            # 32 - Sea level
            local_height = int(glm.simplex(glm.vec2(chunkX + x, chunkZ + z) * 0.02) * 8 + 64)
            if local_height < 0:
                continue
            for y in range(min(local_height, CHUNK_HEIGHT)):
                if local_height - y <= 1:
                    blocks[flatten_coord(x, y, z)] = 2
                elif local_height - y <= 3:
                    blocks[flatten_coord(x, y, z)] = 3
                else:
                    blocks[flatten_coord(x, y, z)] = randint(4, 7)

    return chunkX, chunkZ, blocks
    
class World:
    def __init__(self, app):
        self.app = app
        self.chunks = {}
        self.pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        self.numba_chunks = Dict()
        self.gen_queue = set()

    def get_chunk(self, x, z):
        loc = (x, z)
        return self.chunks[loc] if loc in self.chunks else None

    def gen_chunk(self, x, z):
        self.chunks[(x, z)] = Chunk(self.app, position=[x*CHUNK_SIZE, 0, z*CHUNK_SIZE])
        self.numba_chunks[(x, z)] = self.chunks[(x, z)].blocks

    def build_chunk(self, x, z):
        if (x, z) in self.chunks:
            self.chunks[(x, z)].build()

    def render_chunks(self, position, isAsync=False):
        chunk_pos = (int(position[0] // CHUNK_SIZE), int(position[2] // CHUNK_SIZE))
        for x in range(int(chunk_pos[0] - RENDER_DISTANCE), int(chunk_pos[0] + RENDER_DISTANCE + 1)):
            for z in range(int(chunk_pos[1] - RENDER_DISTANCE), int(chunk_pos[1] + RENDER_DISTANCE + 1)):
                if (x, z) not in self.chunks:
                    if (x, z) not in self.gen_queue:
                        if isAsync:
                            self.gen_queue.add((x, z))

                            # To generate new VBOs, I guess add to a set of the chunks that need it?

                            def call(x):
                                self.gen_queue.remove((x[0], x[1]))
                                print(x[2])

                            def error(x):
                                print(x)

                            print("Adding to async")
                            res = self.pool.apply_async(chunk_provider, (x, z, CHUNK_SIZE, CHUNK_HEIGHT, utils.flatten_coord), callback=call, error_callback=error)

                            self.chunks[(x, z)] = self.chunks[(0, 0)]

                        else:
                            self.gen_chunk(x, z)
                            self.build_chunk(x, z)

                else:
                    self.chunks[(x, z)].draw()