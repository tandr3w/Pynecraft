# TODO:
# Clean up all the code
# Fix the face draw thing
# Figure out why the vertices don't fit in the x18 arr
# Textures for chunks

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

class Pynecraft(pyglet.window.Window):

    def update(self, dt):
        self.delta_time = dt

    def __init__(self, win_size=(800, 600)):
        super().__init__(width=win_size[0], height=win_size[1])
        super(Pynecraft, self).set_exclusive_mouse(True)
        self.WIN_SIZE = win_size
        self.init_opengl()
        self.delta_time = 0

        self.camera = Camera(self)
        self.shader = Shader()

        self.scene = []
        self.held_keys = set()

        pyglet.clock.schedule_interval(self.update, 1 / TPS)

        # self.scene.append(Quad(self, [0, 0, 0], [1, 2, 1]))
        self.scene.append(Chunk(self, [0, 0, 0], [0, 0, 0]))

        self.set_exclusive_mouse(True)

    def init_opengl(self):
        glClearColor(0.1, 0.2, 0.2, 1)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST);  
        # glEnable(GL_CULL_FACE);  

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.camera.update()

        for obj in self.scene:
            obj.draw()

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