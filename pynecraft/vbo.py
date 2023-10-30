from OpenGL.GL import *
import numpy as np
from vao import QuadVAO


class VBO:
    def __init__(self):
        self.vbos = {}
        self.vaos = {}
        self.vbos["quad"] = QuadVBO().get_vbo()
        self.vaos["quad"] = QuadVAO().get_vao()
    
class BaseVBO:
    def __init__(self):
        self.vbo = self.get_vbo()

    def get_vbo(self):
        vertices = self.get_vertex_data()
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        return self.vbo

    
    def get_vertex_data(self): ...

    def destroy(self):
        self.vbo.release()

class QuadVBO(BaseVBO):
    def __init__(self):
        super().__init__()
    
    def get_vertex_data(self):
        vertices = (
            1, 1, 0,
            -1, 1, 0,
            -1, -1, 0,
            1, 1, 0,
            -1, -1, 0,
            1, -1, 0
        )
        
        vertices = np.array(vertices, dtype=np.float32)
        return vertices