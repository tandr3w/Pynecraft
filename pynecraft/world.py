from chunk import Chunk
from constants import *
from numba.typed import Dict
import multiprocessing
import time

class World:
    def __init__(self, app):
        self.app = app
        self.chunks = {}
        self.numba_chunks = Dict()

    def get_chunk(self, x, z):
        loc = (x, z)
        return self.chunks[loc] if loc in self.chunks else None

    def gen_chunk(self, x, z):
        self.chunks[(x, z)] = Chunk(self.app, position=[x*CHUNK_SIZE, 0, z*CHUNK_SIZE])
        self.numba_chunks[(x, z)] = self.chunks[(x, z)].mesh.blocks

    def build_chunk(self, x, z):
        if (x, z) in self.chunks:
            self.chunks[(x, z)].mesh.build()

    def render_chunks(self, position):
        chunk_pos = (int(position[0] // CHUNK_SIZE), int(position[2] // CHUNK_SIZE))
        for x in range(int(chunk_pos[0] - RENDER_DISTANCE), int(chunk_pos[0] + RENDER_DISTANCE + 1)):
            for z in range(int(chunk_pos[1] - RENDER_DISTANCE), int(chunk_pos[1] + RENDER_DISTANCE + 1)):
                if (x, z) not in self.chunks:
                    self.gen_chunk(x, z)
                    self.build_chunk(x, z)
                else:
                    self.chunks[(x, z)].mesh.draw()
