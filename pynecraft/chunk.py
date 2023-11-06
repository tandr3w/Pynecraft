import numpy as np
from constants import *
import utils
from chunk_builder import build_chunk
from material import Material
from OpenGL.GL import *
import glm
from random import randint
import pyrr

"""
Since it would be silly to render thousands of individual blocks, they are combined into 16x16x16 chunks.
"""
from constants import *

class Chunk:
    def __init__(self, app, position):
        self.app = app
        self.vertex_count = 0
        self.position = position
        self.blocks = self.get_blocks()
        self.material = self.app.blockMaterial
        self.material = False
        self.vbo = None
        self.vao = None
        self.shader = self.app.shader.shaders["chunk"]
        self.model_matrix = self.get_model_matrix()
        self.chunkPos = [position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE, position[2] // CHUNK_SIZE]

    def build(self):
        self.vbo = self.get_vbo()
        self.vao = self.get_vao()

    def get_vbo(self):
        vertices = build_chunk(self.app.world.numba_chunks, self.chunkPos[0], self.chunkPos[1], self.chunkPos[2], self.blocks)
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

    def get_model_matrix(self): # The actual transformations of the shape
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        return pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )

    def draw(self):
        # VBOs are connected to the VAOs, and will automatically do so when the VAO is init'ed, which will use the currently bound VBO
        glBindVertexArray(self.vao)
        glUseProgram(self.shader)
        if self.material:
            self.material.use()

        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_proj"), 1, GL_FALSE, self.app.camera.proj_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_view"), 1, GL_FALSE, self.app.camera.view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_model"), 1, GL_FALSE, self.model_matrix)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

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