import numpy as np
from shapes import BaseShape
from constants import *
import utils
from chunk_builder import build_chunk
from material import Material
from OpenGL.GL import *
import glm
from random import randint

"""
Since it would be silly to render thousands of individual blocks, they are combined into 16x16x16 chunks.
"""
from constants import *
class Chunk:
    def __init__(self, app, position=[0, 0, 0], eulers=[0, 0, 0]):
        self.chunkPos = [position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE, position[2] // CHUNK_SIZE]
        self.position = position
        self.mesh = ChunkMesh(self, app, position, eulers)

    def get_blocks(self):
        """
        Represent chunks as flattened 16x16x16 arrays, where each block is represented as an integer between 0-255
        """
        blocks = np.zeros(CHUNK_SIZE ** 2 * CHUNK_HEIGHT, dtype='uint8')
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                # 0.02 - Scale, higher = smaller hills in the xy direction (less fat)
                # 8 - Amplitude, higher = taller hills, lower valleys
                # 32 - Sea level
                local_height = int(glm.simplex(glm.vec2(self.position[0] + x, self.position[2] + z) * 0.02) * 8 + 64) - self.position[1]
                if local_height < 0:
                    continue
                for y in range(min(local_height, CHUNK_HEIGHT)):
                    if local_height - y <= 1:
                        blocks[utils.flatten_coord(x, y, z)] = 2
                    elif local_height - y <= 3:
                        blocks[utils.flatten_coord(x, y, z)] = 3
                    else:
                        blocks[utils.flatten_coord(x, y, z)] = randint(4, 7)
        return blocks

class ChunkMesh(BaseShape):
    def __init__(self, chunk, app, position, eulers):
        self.chunk = chunk
        self.vertex_count = 0
        self.position = position
        self.blocks = self.chunk.get_blocks()
        super().__init__(app=app, position=position, eulers=eulers, name="chunk")
        self.material = self.app.blockMaterial

    def get_vbo(self):
        vertices = build_chunk(self.app.world.numba_chunks, self.chunk.chunkPos[0], self.chunk.chunkPos[1], self.chunk.chunkPos[2], self.blocks)
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

