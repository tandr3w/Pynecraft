from chunk import Chunk
from constants import *
from numba.typed import Dict

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

    def build_chunk(self, x, y, z):
        if (x, z) in self.chunks:
            self.chunks[(x, z)].mesh.build()