import numpy as np
from shapes import BaseShape
from constants import *
import utils
from chunk_builder import build_chunk
from OpenGL.GL import *

"""
Since it would be silly to render thousands of individual blocks, they are combined into 16x16x16 chunks.
"""
from random import randint
class Chunk:
    def __init__(self, app, position=[0, 0, 0], eulers=[0, 0, 0]):
        self.mesh = ChunkMesh(self, app, position, eulers)

    def get_blocks(self):
        """
        Represent chunks as flattened 16x16x16 arrays, where each block is represented as an integer between 0-255
        """
        blocks = np.zeros(CHUNK_SIZE ** 3, dtype='uint8')
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                for z in range(CHUNK_SIZE):
                    blocks[utils.flatten_coord(x, y, z)] = randint(1, 200)
        return blocks

    def draw(self):
        self.mesh.draw()

class ChunkMesh(BaseShape):
    def __init__(self, chunk, app, position, eulers):
        self.chunk = chunk
        self.vertex_count = 0
        super().__init__(app=app, position=position, eulers=eulers, name="chunk")

    def get_vbo(self):
        vertices = build_chunk(self.chunk.get_blocks())
        self.vertex_count = len(vertices) // 5
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        return vbo

    def get_vao(self):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        glEnableVertexAttribArray(0)
        glVertexAttribIPointer(0, 3, GL_UNSIGNED_BYTE, 5, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribIPointer(1, 1, GL_UNSIGNED_BYTE, 5, ctypes.c_void_p(3))
        glEnableVertexAttribArray(2)
        glVertexAttribIPointer(2, 1, GL_UNSIGNED_BYTE, 5, ctypes.c_void_p(4))
        return vao

