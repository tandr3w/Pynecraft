from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader

class Shader():
    """
    Initializes and stores shader programs for each object type
    """
    def __init__(self):
        self.shaders = {}
        self.shaders["chunk"] = self.get_shader("default")
        self.shaders["marker"] = self.get_shader("marker")

    def get_shader(self, shader_name):
        with open(f"shaders/{shader_name}.vert") as f:
            vertex_shader = f.readlines()
        with open(f"shaders/{shader_name}.frag") as f:
            fragment_shader = f.readlines()
        
        shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER), compileShader(fragment_shader, GL_FRAGMENT_SHADER))
        return shader
    