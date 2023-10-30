from OpenGL.GL import *
import numpy as np
import pyrr

class BaseShape:
    def __init__(self, app, position, eulers, name):

        self.app = app
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.vertex_count = 0

        # Each shape type only needs one VBO because the vertices will be the same, only transformations (shader vars) differ. You just have to bind it to use it.
        # Each shape type only needs one VAO and shader as well, you just have to do a cmd while drawing to use them.

        self.vbo = self.app.VBO_obj.vbos[name]
        self.vao = self.app.VBO_obj.vaos[name]
        self.shader = self.app.shader.shaders[name]

        self.model_matrix = self.get_model_matrix()


    def get_model_matrix(self): # The actual transformations of the shape
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis = [0, 1, 0],
                theta = np.radians(self.eulers[1]), 
                dtype = np.float32
            )
        )

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

        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_proj"), 1, GL_FALSE, self.app.camera.proj_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_view"), 1, GL_FALSE, self.app.camera.view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "m_model"), 1, GL_FALSE, self.model_matrix)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

class Quad(BaseShape):
    def __init__(self, app, position, eulers):
        super().__init__(app=app, position=position, eulers=eulers, name="quad")
        self.vertex_count = 6
