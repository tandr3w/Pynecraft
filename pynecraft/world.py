from chunk import Chunk
from constants import *
from numba.typed import Dict

class World:
    def __init__(self, app):
        self.app = app
        self.chunks = {}
        self.numba_chunks = Dict()

    def get_chunk(self, x, y, z):
        loc = (x, y, z)
        return self.chunks[loc] if loc in self.chunks else None

    def gen_chunk(self, x, y, z):
        self.chunks[(x, y, z)] = Chunk(self.app, position=[x*CHUNK_SIZE, y*CHUNK_SIZE, z*CHUNK_SIZE])
        self.numba_chunks[(x, y, z)] = self.chunks[(x, y, z)].mesh.blocks

    def build_chunk(self, x, y, z):
        if (x, y, z) in self.chunks:
            self.chunks[(x, y, z)].mesh.build()