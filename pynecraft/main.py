# TODO:
# Fix collision, note that when getting the block, if the pos is negative you have to -ceil(-x) instead of int(x)
# Prevent placing in illegal positions (diagonally) - don't save it in prevblock if its not adjacent, instead save the nearest block that is actually adjacent
# More advanced terrain generation
# Swap the textures to not use that lame ass copied solution
# Add main menu
# Add gravity / jumping / singleplayer mode
# Lighting / fog
# Add graphic for which block you are placing
# Add saving / write to disk
# Optimize with Frustum culling?


import pyglet
from pyglet.window import key
from OpenGL.GL import *
from constants import *
import sys
import numpy as np
from camera import Camera
from chunk import Chunk, BlockMarker
from shader import Shader
from world import World
from material import Material
import constants
import utils
from math import ceil

class Pynecraft(pyglet.window.Window):

    def update(self, dt):
        self.delta_time = dt

    def __init__(self, win_size=(800, 600)):
        super().__init__(width=win_size[0], height=win_size[1])
        self.WIN_SIZE = win_size
        self.delta_time = 0

        self.camera = Camera(self)
        self.shader = Shader()

        self.world = World(self)
        self.held_keys = set()
        self.blockMaterial = Material("gfx/tex_array_1.png", isArr=True)
        self.placingBlock = 1

        pyglet.clock.schedule_interval(self.update, 1 / TPS)
        self.set_exclusive(True)

        self.batch = pyglet.graphics.Batch()
        CROSSHAIR_COLOR = (100, 100, 100, 150)
        self.line = pyglet.shapes.Line(self.WIN_SIZE[0]//2 - CROSSHAIR_SIZE, self.WIN_SIZE[1] // 2, self.WIN_SIZE[0]//2 + CROSSHAIR_SIZE, self.WIN_SIZE[1] // 2, width=2, color=CROSSHAIR_COLOR, batch=self.batch)
        self.line2 = pyglet.shapes.Line(self.WIN_SIZE[0]//2, self.WIN_SIZE[1]//2 - CROSSHAIR_SIZE, self.WIN_SIZE[0]//2, self.WIN_SIZE[1] // 2 + CROSSHAIR_SIZE, width=2, color=CROSSHAIR_COLOR, batch=self.batch)

        self.marker = BlockMarker(self)
        self.init_opengl()


    def set_exclusive(self, val):
        super(Pynecraft, self).set_exclusive_mouse(val)
        self.exclusive = val

    def init_opengl(self):
        glClearColor(0.1, 0.2, 0.2, 1)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        
        self.camera.update()
        self.world.render_chunks(self.camera.position, isAsync=True)
        self.batch.draw()
        lookingAt = self.get_selected_block()
        if not lookingAt == None:
            self.marker.position = np.array([int(lookingAt[0]), int(lookingAt[1]), int(lookingAt[2])])
            self.marker.draw()

    def get_selected_block(self):
        if self.world.firstLoad:
            currPos = [self.camera.position[0], self.camera.position[1], self.camera.position[2]]
            prevBlock = None
            for i in range(128):
                currPos = [self.camera.position[0] + self.camera.forward[0] * 0.05 * i, self.camera.position[1] + self.camera.forward[1] * 0.05 * i, self.camera.position[2] + self.camera.forward[2] * 0.05 * i]
                # print(currPos)
                for j in range(3):
                    if currPos[j] < 0:
                        currPos[j] = -ceil(-currPos[j])
                    else:
                        currPos[j] = int(currPos[j])
                block = self.world.get_block(currPos[0], currPos[1], currPos[2])
                if block:
                    return (currPos[0], currPos[1], currPos[2], prevBlock)
                else:
                    prevBlock = (currPos[0], currPos[1], currPos[2])

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
        elif symbol == key._1:
            self.placingBlock = 1
        elif symbol == key._2:
            self.placingBlock = 2
        elif symbol == key._3:
            self.placingBlock = 3
        elif symbol == key._4:
            self.placingBlock = 4
        elif symbol == key._5:
            self.placingBlock = 5
        elif symbol == key._6:
            self.placingBlock = 6
        elif symbol == key._7:
            self.placingBlock = 7

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:
            self.camera.rotate(-dx, dy)
            self.camera.update_camera_vectors()

    def on_mouse_press(self, x, y, button, modifiers):
        block = self.get_selected_block()
        if not block == None:
            if button == pyglet.window.mouse.LEFT:
                if self.exclusive:
                    chunkX = block[0] // CHUNK_SIZE
                    chunkZ = block[2] // CHUNK_SIZE
                    if (chunkX, chunkZ) in self.world.chunks:
                        # print("Breaking!")
                        self.world.chunks[(chunkX, chunkZ)].blocks[utils.flatten_coord(block[0] % CHUNK_SIZE, block[1] % CHUNK_HEIGHT, block[2] % CHUNK_SIZE)] = 0
                        self.world.build_chunk(chunkX, chunkZ)
                else:
                    self.set_exclusive(True)
            elif button == pyglet.window.mouse.RIGHT and self.exclusive:
                if not block[3] == None:
                    chunkX = block[3][0] // CHUNK_SIZE
                    chunkZ = block[3][2] // CHUNK_SIZE
                    if (chunkX, chunkZ) in self.world.chunks:
                        # print("Placing!")
                        if block[3][1] < 255:
                            self.world.chunks[(chunkX, chunkZ)].blocks[utils.flatten_coord(block[3][0] % CHUNK_SIZE, block[3][1], block[3][2] % CHUNK_SIZE)] = self.placingBlock
                            self.world.build_chunk(chunkX, chunkZ) 


if __name__ == '__main__':
    window = Pynecraft()
    pyglet.app.run()