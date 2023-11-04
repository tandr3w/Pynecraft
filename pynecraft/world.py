from chunk import Chunk
from constants import *
from numba.typed import Dict
import multiprocessing
import time

# Needs to return:
# - Try returning the Chunk object
    # Doesn't work? Return the chunk blocks instead, and remove adding that in the class inits
# - Don't use global variables inside the functions
# - return the built chunk vertices array, and remove that from the get_vbo function

def async_proxy(provider, x, y):
    # res = provider.provide_chunk(x, y)
    # time.sleep(0.5)
    # return res
    return 1

class World:
    def __init__(self, app):
        self.app = app
        self.chunks = {}
        self.numba_chunks = Dict()
        self.gen_queue = []
        self.pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    def get_chunk(self, x, z):
        loc = (x, z)
        return self.chunks[loc] if loc in self.chunks else None

    def gen_chunk(self, x, z):
        self.chunks[(x, z)] = Chunk(self.app, position=[x*CHUNK_SIZE, 0, z*CHUNK_SIZE])
        self.numba_chunks[(x, z)] = self.chunks[(x, z)].mesh.blocks

    def build_chunk(self, x, z):
        if (x, z) in self.chunks:
            self.chunks[(x, z)].mesh.build()

    def provide_chunk(x, z):
        print("im called")
        # self.gen_chunk(x, z)
        # self.build_chunk(x, z)
        # return (x, z)
        return 1

    def render_chunks(self, position, isAsync=True):
        chunk_pos = (int(position[0] // CHUNK_SIZE), int(position[2] // CHUNK_SIZE))
        for x in range(int(chunk_pos[0] - RENDER_DISTANCE), int(chunk_pos[0] + RENDER_DISTANCE + 1)):
            for z in range(int(chunk_pos[1] - RENDER_DISTANCE), int(chunk_pos[1] + RENDER_DISTANCE + 1)):
                if (x, z) not in self.chunks:
                    if (x, z) not in self.gen_queue:
                        if isAsync:
                            def callback(posAdded):
                                print("Chunk has been generated!")
                                # # self.chunks[(x, z)] = Chunk(self.app, position=[x*CHUNK_SIZE, 0, z*CHUNK_SIZE])
                                # # self.numba_chunks[(x, z)] = self.chunks[(x, z)].mesh.blocks
                                # self.gen_queue.remove(posAdded)

                            def error_callback(e):
                                print("ERROR!!")
                                print(e)
                            
                            self.gen_queue.append((x, z))
                            res = self.pool.apply_async(async_proxy, (None, x, z), callback=callback, error_callback=error_callback)
                            print("process added")
                        else:
                            self.gen_chunk(x, z)
                            self.build_chunk(x, z)
                            # Rebuild adjacent chunks to cull faces
                            # self.build_chunk(x+1, z)
                            # self.build_chunk(x-1, z)
                            # self.build_chunk(x, z+1)
                            # self.build_chunk(x, z-1)

                else:
                    self.chunks[(x, z)].mesh.draw()
