# TODO:
# Make chunks 256 tall (entire height)
# Add dynamic chunk rendering (don't render if there's a world limit)
# More advanced terrain generation
# Add breaking / placing blocks
# Add gravity
# Pack data?
# Use JIT with numba to make it faster
# Get rid of pyrr since it's slow
# Lighting
# Optimize with Frustum culling?

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

        pyglet.clock.schedule_interval(self.update, 1 / TPS)
        super(Pynecraft, self).set_exclusive_mouse(True)

        for x in range(-1, 2):
            for z in range(-1, 2):
                for y in range(1, 4):
                    self.world.gen_chunk(x, y, z)

        for chunk in self.world.chunks: # Build VBOs for all the chunks
            self.world.chunks[chunk].mesh.build()
        
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

        for chunk in self.world.chunks:
            self.world.chunks[chunk].mesh.draw()

    def on_key_press(self, symbol, modifiers):
        self.held_keys.add(symbol)        
        if symbol == key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        self.held_keys.remove(symbol)
        if symbol == key.ESCAPE:
            self.close()

    def on_mouse_motion(self, x, y, dx, dy):
        self.camera.rotate(-dx, dy)
        self.camera.update_camera_vectors()

window = Pynecraft()
pyglet.app.run()