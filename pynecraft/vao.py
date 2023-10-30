from OpenGL.GL import *
import numpy as np

class BaseVAO:
    def __init__(self):
        self.vao = self.get_vao()

    def get_vao(self): ...
    
    def destroy(self):
        self.vao.release()


class QuadVAO(BaseVAO):
    def __init__(self):
        super().__init__()
    
    def get_vao(self):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        return vao