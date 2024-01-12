# TODO:
# Noclip setting
# Only allow sprinting while holding W, and make it last until you release W
# Shifting

# Basic Lighting:
# Ambient Occlusion based on https://0fps.net/2013/07/03/ambient-occlusion-for-minecraft-like-worlds/

# Fog (OpenGL docs)

# More advanced terrain generation

# Add installation instructions & requirements.txt
# Convert images to resources - make it distributable
# Comment and organize code

# Swap the textures to not use that lame ass copied solution
# Add new block types

# Probably not gonna do these:
# Add a save system
# Add an escape menu with options
# Add a hotbar


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
from math import ceil, sqrt

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
        self.placingBlock = 1
        self.exclusive = False

        self.left_held = False
        self.right_held = False

        self.past_repeat = 0
        self.curr_repeat_time = 0

        pyglet.clock.schedule_interval(self.update, 1 / TPS)

        # Intialize crosshair
        self.crosshair_batch = pyglet.graphics.Batch()
        CROSSHAIR_COLOR = (100, 100, 100, 150)
        self.cross = pyglet.shapes.Line(self.WIN_SIZE[0]//2 - CROSSHAIR_SIZE, self.WIN_SIZE[1] // 2, self.WIN_SIZE[0]//2 + CROSSHAIR_SIZE, self.WIN_SIZE[1] // 2, width=2, color=CROSSHAIR_COLOR, batch=self.crosshair_batch)
        self.cross2 = pyglet.shapes.Line(self.WIN_SIZE[0]//2, self.WIN_SIZE[1]//2 - CROSSHAIR_SIZE, self.WIN_SIZE[0]//2, self.WIN_SIZE[1] // 2 + CROSSHAIR_SIZE, width=2, color=CROSSHAIR_COLOR, batch=self.crosshair_batch)


        # Initialize menu
        self.menu_batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.Group(order=0)
        self.foreground = pyglet.graphics.Group(order=1)
        self.textground = pyglet.graphics.Group(order=2)

        self.menu_bg_img = pyglet.image.load('gfx/background.png')
        self.menu_bg = pyglet.sprite.Sprite(self.menu_bg_img, x=0, y=0, batch=self.menu_batch, group=self.background)
        self.menu_bg.update(scale=max(self.WIN_SIZE[0] / self.menu_bg.width, self.WIN_SIZE[1] / self.menu_bg.height))

        self.logo_img = pyglet.image.load('gfx/logo.png')
        self.logo = pyglet.sprite.Sprite(self.logo_img, x=0, y=0, batch=self.menu_batch, group=self.foreground)
        self.logo.update(scale=self.WIN_SIZE[0] / self.logo.width)
        self.logo.update(y=self.WIN_SIZE[1] - self.logo.height)

        self.play_btn_img = pyglet.image.load('gfx/button.png')
        self.play_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-self.logo.height-150, batch=self.menu_batch, group=self.foreground)
        self.play_btn.update(scale_x=(6*self.WIN_SIZE[0]/10) / self.play_btn.width, scale_y=50/self.play_btn.height)

        self.loading_batch = pyglet.graphics.Batch()
        self.loading_bg_img = pyglet.image.load('gfx/loading_bg.png')
        self.loading_bg = pyglet.sprite.Sprite(self.loading_bg_img, x=0, y=0, batch=self.loading_batch, group=self.background)
        self.loading_bg.update(scale=max(self.WIN_SIZE[0] / self.loading_bg.width, self.WIN_SIZE[1] / self.loading_bg.height))

        self.controls_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-self.logo.height-225, batch=self.menu_batch, group=self.foreground)
        self.controls_btn.update(scale_x=(6*self.WIN_SIZE[0]/10) / self.controls_btn.width, scale_y=50/self.controls_btn.height)

        pyglet.font.add_file('assets/minecraftia.ttf')
        pyglet.font.load('Minecraftia')

        self.play_btn_text = pyglet.text.Label('Play',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.play_btn.position[1] + 20,
            anchor_x='center', anchor_y='center')

        self.controls_btn_text = pyglet.text.Label('How To Play',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.controls_btn.position[1] + 20,
            anchor_x='center', anchor_y='center')

        self.help_texts = [
            pyglet.text.Label('CONTROLS',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 50, color=(255, 255, 0, 255),
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press WASD to move',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 100,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Left click to break blocks',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 130,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Right click to place blocks',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 160,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press SPACE to jump',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 190,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press CTRL to sprint',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-220,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press G to toggle gravity',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-250,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press N to toggle noclip',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-280,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Change placed blocks with number keys',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-310,
            anchor_x='center', anchor_y='center')
        ]

        self.help_batch = pyglet.graphics.Batch()
        self.back_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-400, batch=self.help_batch, group=self.foreground)
        self.back_btn.update(scale_x=(6*self.WIN_SIZE[0]/10) / self.back_btn.width, scale_y=50/self.back_btn.height)

        self.back_btn_text = pyglet.text.Label('Back',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.back_btn.position[1] + 20,
            anchor_x='center', anchor_y='center')

        self.loading_texts = []

        for i in range(4):
            self.loading_texts.append(
                pyglet.text.Label('Loading' + "."*i,
                font_name='Minecraftia',
                font_size=24,
                x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]//2,
                anchor_x='center', anchor_y='center')
            )

        self.time_since_animation = 0
        self.animation_counter = 0

        # 0 = menu, 1 = loading / game, 2 = how to play
        self.screen_id = 0

        # Must be loaded last since it changes OpenGL settings
        self.blockMaterial = Material("gfx/tex_array_1.png", isArr=True)

        self.marker = BlockMarker(self)
        self.init_opengl()

    # Check if a pyglet element is clicked
    def is_clicked(self, element, mouseX, mouseY):
        if mouseX > element.position[0] and mouseX < element.position[0] + element.width and mouseY > element.position[1] and mouseY < element.position[1] + element.height:
            return True
        return False

    def set_exclusive(self):
        super(Pynecraft, self).set_exclusive_mouse(False)
        super(Pynecraft, self).set_exclusive_mouse(True)
        self.exclusive = True

    def init_opengl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def break_selected_block(self):
        block = self.get_selected_block()
        if not block == None:
            chunkX = block[0] // CHUNK_SIZE
            chunkZ = block[2] // CHUNK_SIZE
            if (chunkX, chunkZ) in self.world.chunks:
                # print("Breaking!")
                self.world.chunks[(chunkX, chunkZ)].blocks[utils.flatten_coord(block[0] % CHUNK_SIZE, block[1] % CHUNK_HEIGHT, block[2] % CHUNK_SIZE)] = 0
                self.world.build_chunk(chunkX, chunkZ)

    def place_block(self):
        block = self.get_selected_block()
        if not block == None and not block[3] == None:
            chunkX = block[3][0] // CHUNK_SIZE
            chunkZ = block[3][2] // CHUNK_SIZE
            if (chunkX, chunkZ) in self.world.chunks:
                # Don't allow blocks to be placed on diagonals
                # Possibly in the future, check which block placement is closer rather than not allowing placement at all
                if block[3][1] < 255:
                    self.world.chunks[(chunkX, chunkZ)].blocks[utils.flatten_coord(block[3][0] % CHUNK_SIZE, block[3][1], block[3][2] % CHUNK_SIZE)] = self.placingBlock
                    if self.camera.check_collision([self.camera.position[0], self.camera.position[1], self.camera.position[2]]):
                        self.world.chunks[(chunkX, chunkZ)].blocks[utils.flatten_coord(block[3][0] % CHUNK_SIZE, block[3][1], block[3][2] % CHUNK_SIZE)] = 0
                    self.world.build_chunk(chunkX, chunkZ) 

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)

        if self.screen_id == 0:
            # self.crosshair_batch.draw()
            glDisable(GL_DEPTH_TEST)
            self.menu_batch.draw()
            self.play_btn_text.draw()
            self.controls_btn_text.draw()
            glEnable(GL_DEPTH_TEST)

        elif self.screen_id == 1:
            if self.world.firstLoad:
                glClearColor(0.52, 0.81, 0.92, 1)
                self.set_exclusive()
            else:
                glDisable(GL_DEPTH_TEST)
                self.loading_batch.draw()
                self.loading_texts[self.animation_counter].draw()

                # Animate loading text
                self.time_since_animation += self.delta_time
                if self.time_since_animation > 0.5:
                    self.time_since_animation = 0
                    self.animation_counter += 1
                    self.animation_counter %= 4

                glEnable(GL_DEPTH_TEST)

            if self.left_held:
                self.curr_repeat_time += self.delta_time
                if (self.past_repeat < FIRST_REPEAT_DELAY and self.past_repeat + self.curr_repeat_time >= FIRST_REPEAT_DELAY ) or (self.past_repeat >= FIRST_REPEAT_DELAY and self.curr_repeat_time >= REPEAT_DELAY):
                    self.break_selected_block()
                    self.past_repeat += self.curr_repeat_time
                    self.curr_repeat_time = 0

            elif self.right_held:
                self.curr_repeat_time += self.delta_time
                if (self.past_repeat < FIRST_REPEAT_DELAY and self.past_repeat + self.curr_repeat_time >= FIRST_REPEAT_DELAY ) or (self.past_repeat >= FIRST_REPEAT_DELAY and self.curr_repeat_time >= REPEAT_DELAY):
                    self.place_block()
                    self.past_repeat += self.curr_repeat_time
                    self.curr_repeat_time = 0

            self.camera.update()
            self.world.render_chunks(self.camera.position, isAsync=True)
            self.crosshair_batch.draw()
            lookingAt = self.get_selected_block()
            if not lookingAt == None:
                self.marker.position = np.array([int(lookingAt[0]), int(lookingAt[1]), int(lookingAt[2])])
                self.marker.draw()

        elif self.screen_id == 2:
            glDisable(GL_DEPTH_TEST)
            for textline in self.help_texts:
                textline.draw()
            self.help_batch.draw()
            self.back_btn_text.draw()
            glEnable(GL_DEPTH_TEST)


    def get_selected_block(self):
        if self.world.firstLoad:
            floatPos = [self.camera.position[0], self.camera.position[1], self.camera.position[2]]
            currPos = [self.camera.position[0], self.camera.position[1], self.camera.position[2]]
            prevBlock = None
            prevFloat = None

            for i in range(128):
                floatPos = [self.camera.position[0] + self.camera.forward[0] * 0.05 * i, self.camera.position[1] + self.camera.forward[1] * 0.05 * i, self.camera.position[2] + self.camera.forward[2] * 0.05 * i]
                # print(currPos)
                for j in range(3):
                    if currPos[j] < 0:
                        currPos[j] = -ceil(-floatPos[j])
                    else:
                        currPos[j] = int(floatPos[j])
                block = self.world.get_block(currPos[0], currPos[1], currPos[2])
                if block:
                    if prevBlock:
                        # Can't place diagonally -- find the closest center of an adjacent block to prevFloat
                        if abs(prevBlock[0]-currPos[0]) + abs(prevBlock[2]-currPos[2]) + abs(prevBlock[1]-currPos[1]) != 1:
                            minDist = float("inf")
                            adjacent = [(currPos[0]+1, currPos[1], currPos[2]), (currPos[0]-1, currPos[1], currPos[2]),
                                     (currPos[0], currPos[1]+1, currPos[2]), (currPos[0], currPos[1]-1, currPos[2]),
                                     (currPos[0], currPos[1], currPos[2]+1), (currPos[0], currPos[1], currPos[2]-1)]
                            for newPrev in adjacent:
                                # Distance between twowwwwwwww 3d points, add 0.5 to get center of block
                                newDist = sqrt(abs(prevFloat[0]-(newPrev[0]+0.5))**2 + abs(prevFloat[1]-(newPrev[1]+0.5))**2 + abs(prevFloat[2]-(newPrev[2]+0.5))**2)
                                if newDist < minDist:
                                    minDist = newDist
                                    prevBlock = newPrev

                    return (currPos[0], currPos[1], currPos[2], prevBlock)
                else:
                    prevBlock = (currPos[0], currPos[1], currPos[2])
                    prevFloat = (floatPos[0], floatPos[1], floatPos[2])

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        if self.world.firstLoad:
            self.held_keys.add(symbol)

            if symbol == key.EQUAL:
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
            elif symbol == key.G:
                self.camera.GRAVITY_ENABLED = not self.camera.GRAVITY_ENABLED
            elif symbol == key.N:
                self.camera.NOCLIP_ENABLED = not self.camera.NOCLIP_ENABLED
                if self.camera.NOCLIP_ENABLED:
                    self.camera.GRAVITY_ENABLED = False

    def on_key_release(self, symbol, modifiers):
        if self.world.firstLoad:
            self.held_keys.remove(symbol)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive and self.world.firstLoad:
            self.camera.rotate(-dx, dy)
            self.camera.update_camera_vectors()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            if self.screen_id == 0 and self.is_clicked(self.play_btn, x, y):
                # Start game
                self.screen_id = 1

            elif self.screen_id == 0 and self.is_clicked(self.controls_btn, x, y):
                self.screen_id = 2
            
            elif self.screen_id == 2 and self.is_clicked(self.back_btn, x, y):
                self.screen_id = 0

            if self.world.firstLoad:
                self.set_exclusive()
                self.left_held = True
                self.break_selected_block()

        elif button == pyglet.window.mouse.RIGHT and self.exclusive:
            if self.world.firstLoad:
                self.right_held = True
                self.place_block()

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.world.firstLoad:
            return
        if button == pyglet.window.mouse.LEFT:
            self.left_held = False

        elif button == pyglet.window.mouse.RIGHT and self.exclusive:
            self.right_held = False
        
        if self.left_held == False and self.right_held == False:
            self.past_repeat = 0
        
        self.curr_repeat_time = 0


if __name__ == '__main__':
    window = Pynecraft()
    pyglet.app.run()