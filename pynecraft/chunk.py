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
    def __init__(self, app, position, blocks=[]):
        self.app = app
        self.vertex_count = 0
        self.position = position
        self.blocks = blocks
        self.material = self.app.blockMaterial
        self.vbo = None
        self.vao = None
        self.shader = self.app.shader.shaders["chunk"]
        self.model_matrix = self.get_model_matrix()
        self.chunkPos = [position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE, position[2] // CHUNK_SIZE]

    def build(self, vertices=[]):
        self.vbo = self.get_vbo(vertices)
        self.vao = self.get_vao()

    def get_vbo(self, vertices):
        if not len(vertices):
            vertices = build_chunk(self.chunkPos[0], self.chunkPos[1], self.chunkPos[2], self.blocks)

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


class BlockMarker:
    def __init__(self, app):
        self.app = app
        self.position = [0, 0, 0]
        self.vbo = self.get_vbo()
        self.vao = self.get_vao()
        self.texture = Material("gfx/marker.png", isArr=False)
        self.shader = self.app.shader.shaders["marker"]

    def get_vbo(self):
        vertices = self.get_vertex_data()
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        return self.vbo

    def get_vao(self):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
        return vao

    def get_vertex_data(self):
        vert_list = [
            (-0.01, -0.01, 1, 1, 0, 0),
            (1, -0.01, 1, 1, 0, 0),
            (1, 1, 1, 1, 0, 0),
            (-0.01, 1, 1, 1, 0, 0),
            (-0.01, 1, -0.01, 1, 0, 0),
            (-0.01, -0.01, -0.01, 1, 0, 0),
            (1, -0.01, -0.01, 1, 0, 0),
            (1, 1, -0.01, 1, 0, 0)
        ]
        indices = [(0, 2, 3), (0, 1, 2), (1, 7, 2), (1, 6, 7), (6, 5, 4), (4, 7, 6), (3, 4, 5), (3, 5, 0), (3, 7, 4), (3, 2, 7), (0, 6, 1), (0, 5, 6)]

        vertices = [vert_list[ind] for triangle in indices for ind in triangle]

        tex_coord = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indices = [(0, 2, 3), (0, 1, 2), (0, 2, 3), (0, 1, 2), (0, 3, 2), (2, 3, 0), (2, 3, 0), (2, 0, 1), (0, 2, 3), (0, 1, 2), (3, 1, 2), (3, 0, 1)]
        
        tex_coord_data = [tex_coord[ind] for triangle in tex_coord_indices for ind in triangle]

        for i in range(len(vertices)):
            vertices[i] = vertices[i] + tex_coord_data[i]
    
        vertices = np.array(vertices, dtype=np.float32).flatten()
        
        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = len(vertices) // 8
        return vertices

    def get_model_matrix(self):
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_scale(
                scale=np.array([1.01, 1.01, 1.01]),dtype=np.float32
            )
        )
        return pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )

    def draw(self):
        glBindVertexArray(self.vao)
        glUseProgram(self.shader)
        self.texture.use()

        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_proj"), 1, GL_FALSE, self.app.camera.proj_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_view"), 1, GL_FALSE, self.app.camera.view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_model"), 1, GL_FALSE, self.get_model_matrix())
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)