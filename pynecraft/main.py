# TODO:
# Revert back to old version! Make sure to copy this to do list tho
# Do not generate a new VBO and VAO for each new chunk since the format stays the same. Simply add the vertices to the buffer.

# Optimize with Frustum culling?
# Swap the textures to not use that lame ass copied solution
# Add breaking / placing blocks
# More advanced terrain generation
# Fix collision
# Add gravity
# Get rid of pyrr since it's slow
# Lighting
# Pack data?
# Add dynamic chunk rendering.
    # - simplify the functions and objects, make the chunk object pickleable
    # - merge chunk, chunkmesh, and baseshape. You don't need all of them.
    # - test to see if making async processes is actually just slower than generating the chunk


import pyglet
from pyglet.window import key
from OpenGL.GL import *
from constants import *
import sys
import numpy as np
from camera import Camera
from shapes import Quad
from chunk import Chunk
from shader import Shader
from world import World
from material import Material
import constants

class Pynecraft(pyglet.window.Window):

    def update(self, dt):
        self.delta_time = dt

    def __init__(self, win_size=(800, 600)):
        super().__init__(width=win_size[0], height=win_size[1])
        self.WIN_SIZE = win_size
        self.init_opengl()
        self.delta_time = 0

        self.camera = Camera(self)
        self.shader = Shader()

        self.world = World(self)
        self.held_keys = set()
        self.blockMaterial = Material("gfx/tex_array_1.png", isArr=True)

        pyglet.clock.schedule_interval(self.update, 1 / TPS)
        super(Pynecraft, self).set_exclusive_mouse(True)

    def init_opengl(self):
        glClearColor(0.1, 0.2, 0.2, 1)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST);  
        glEnable(GL_CULL_FACE);  

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.camera.update()
        self.world.render_chunks(self.camera.position)

    def on_key_press(self, symbol, modifiers):
        self.held_keys.add(symbol)
        if symbol == key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        self.held_keys.remove(symbol)
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.EQUAL:
            self.camera.up_speed()
        elif symbol == key.MINUS:
            self.camera.down_speed()

    def on_mouse_motion(self, x, y, dx, dy):
        self.camera.rotate(-dx, dy)
        self.camera.update_camera_vectors()

if __name__ == '__main__':
    window = Pynecraft()
    pyglet.app.run()