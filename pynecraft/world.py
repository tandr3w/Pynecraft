from chunk import Chunk
from constants import *
from numba.typed import Dict
import multiprocessing
import time

def func(x, y):
    g = 0
    for i in range(10000):
        g += 1
    return x, y, g
    
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
        self.numba_chunks[(x, z)] = self.chunks[(x, z)].mesh.blocks

    def build_chunk(self, x, z):
        if (x, z) in self.chunks:
            self.chunks[(x, z)].mesh.build()

    def render_chunks(self, position, isAsync=False):
        chunk_pos = (int(position[0] // CHUNK_SIZE), int(position[2] // CHUNK_SIZE))
        for x in range(int(chunk_pos[0] - RENDER_DISTANCE), int(chunk_pos[0] + RENDER_DISTANCE + 1)):
            for z in range(int(chunk_pos[1] - RENDER_DISTANCE), int(chunk_pos[1] + RENDER_DISTANCE + 1)):
                if (x, z) not in self.chunks:
                    if (x, z) not in self.gen_queue:
                        if isAsync:
                            self.gen_queue.add((x, z))
                            def call(x):
                                self.gen_queue.remove((x[0], x[1]))
                                print(x)
                            self.pool.apply_async(func, (x, z,), callback=call)
                            self.chunks[(x, z)] = self.chunks[(0, 0)]
                        else:
                            self.gen_chunk(x, z)
                            self.build_chunk(x, z)

                else:
                    self.chunks[(x, z)].mesh.draw()