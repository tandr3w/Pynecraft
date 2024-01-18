# Store seed in save

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
from chunk_builder import flatten_coord
from math import ceil, sqrt
import pyrr

class Pynecraft(pyglet.window.Window):
    """
    Class extending the Pyglet window object, including game initialization, GUIs, and keybinds.
    """
    def update(self, dt):
        """
        self.delta_time represents the time in seconds that have passed since the previous frame.
        """
        self.delta_time = dt

    def __init__(self, win_size=(800, 600)):
        # Create window
        super().__init__(width=win_size[0], height=win_size[1])
        self.WIN_SIZE = win_size
        self.delta_time = 0

        # Update delta time TPS times per second.
        pyglet.clock.schedule_interval(self.update, 1 / TPS)

        # Initialize world & OpenGL objects
        self.camera = Camera(self)
        self.shader = Shader()
        self.world = World(self)
        self.marker = BlockMarker(self)

        self.placingBlock = 1 # Tracks the block that will be placed
        self.exclusive = False # Tracks if the mouse is locked inside the window

        # Variables for handling holding down the mouse to break/place blocks
        self.held_keys = set()
        self.left_held = False
        self.right_held = False
        self.past_repeat = 0
        self.curr_repeat_time = 0

        # Intialize crosshair
        self.crosshair_batch = pyglet.graphics.Batch()
        CROSSHAIR_COLOR = (100, 100, 100, 150)
        self.cross = pyglet.shapes.Line(self.WIN_SIZE[0]//2 - CROSSHAIR_SIZE, self.WIN_SIZE[1] // 2, self.WIN_SIZE[0]//2 + CROSSHAIR_SIZE, self.WIN_SIZE[1] // 2, width=2, color=CROSSHAIR_COLOR, batch=self.crosshair_batch)
        self.cross2 = pyglet.shapes.Line(self.WIN_SIZE[0]//2, self.WIN_SIZE[1]//2 - CROSSHAIR_SIZE, self.WIN_SIZE[0]//2, self.WIN_SIZE[1] // 2 + CROSSHAIR_SIZE, width=2, color=CROSSHAIR_COLOR, batch=self.crosshair_batch)

        # Initialize GUI elements
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

        self.load_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-self.logo.height-225, batch=self.menu_batch, group=self.foreground)
        self.load_btn.update(scale_x=(6*self.WIN_SIZE[0]/10) / self.load_btn.width, scale_y=50/self.load_btn.height)

        self.controls_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-self.logo.height-300, batch=self.menu_batch, group=self.foreground)
        self.controls_btn.update(scale_x=(6*self.WIN_SIZE[0]/10) / self.controls_btn.width, scale_y=50/self.controls_btn.height)

        self.paused_batch = pyglet.graphics.Batch()

        self.resume_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-250, batch=self.paused_batch, group=self.foreground)
        self.resume_btn.update(scale_x=(6*self.WIN_SIZE[0]/10) / self.resume_btn.width, scale_y=50/self.resume_btn.height)

        self.quit_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-325, batch=self.paused_batch, group=self.foreground)
        self.quit_btn.update(scale_x=(6*self.WIN_SIZE[0]/10) / self.quit_btn.width, scale_y=50/self.quit_btn.height)

        self.save_quit_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-400, batch=self.paused_batch, group=self.foreground)
        self.save_quit_btn.update(scale_x=(6*self.WIN_SIZE[0]/10) / self.save_quit_btn.width, scale_y=50/self.save_quit_btn.height)

        pyglet.font.add_file('assets/minecraftia.ttf')
        pyglet.font.load('Minecraftia')

        self.play_btn_text = pyglet.text.Label('New Game',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.play_btn.position[1] + 20,
            anchor_x='center', anchor_y='center')

        self.load_btn_text = pyglet.text.Label('Load Saved',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.load_btn.position[1] + 20,
            anchor_x='center', anchor_y='center')

        self.controls_btn_text = pyglet.text.Label('How To Play',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.controls_btn.position[1] + 20,
            anchor_x='center', anchor_y='center')

        self.resume_btn_text = pyglet.text.Label('Resume',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.resume_btn.position[1] + 20,
            anchor_x='center', anchor_y='center')

        self.quit_btn_text = pyglet.text.Label('Quit Without Saving',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.quit_btn.position[1] + 20,
            anchor_x='center', anchor_y='center')

        self.save_quit_btn_text = pyglet.text.Label('Save and Quit',
            font_name='Minecraftia',
            font_size=16,
            x=self.WIN_SIZE[0]//2, y=self.save_quit_btn.position[1] + 20,
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
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 90,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Left click to break',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 120,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Right click to place blocks',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 150,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press SPACE to jump',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1] - 180,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('CTRL to sprint, SHIFT to sneak',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-210,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press G to toggle gravity',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-240,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press N to toggle noclip',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-270,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Change placed blocks with number keys',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-300,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press ESC to quit',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-330,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press + and - to change speed',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-360,
            anchor_x='center', anchor_y='center'),
            pyglet.text.Label('Press H to open this menu',
            font_name='Minecraftia',
            font_size=12,
            x=self.WIN_SIZE[0]//2, y=self.WIN_SIZE[1]-390,
            anchor_x='center', anchor_y='center')
        ]

        self.help_batch = pyglet.graphics.Batch()
        self.back_btn = pyglet.sprite.Sprite(self.play_btn_img, x=2*self.WIN_SIZE[0]/10, y=self.WIN_SIZE[1]-460, batch=self.help_batch, group=self.foreground)
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

        # For tracking the loading screen animation
        self.time_since_animation = 0
        self.animation_counter = 0

        # 0 = menu, 1 = loading / game, 2 = how to play
        self.screen_id = 0

        self.paused = False

        # Initializes block textures. Must be loaded last since it changes OpenGL settings
        self.blockMaterial = Material("gfx/tex_array_1.png", isArr=True)

        self.init_opengl()

    # Check if a pyglet element is clicked
    def is_clicked(self, element, mouseX, mouseY):
        if mouseX > element.position[0] and mouseX < element.position[0] + element.width and mouseY > element.position[1] and mouseY < element.position[1] + element.height:
            return True
        return False

    # Toggles locking the mouse inside of the game
    def set_exclusive(self, val=True):
        if val == True:
            super(Pynecraft, self).set_exclusive_mouse(False)
            super(Pynecraft, self).set_exclusive_mouse(True)
            self.exclusive = True
        else:
            super(Pynecraft, self).set_exclusive_mouse(False)
            self.exclusive = False

    def init_opengl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def break_selected_block(self):
        block = self.get_selected_block()
        if not block == None:
            # Get the chunk position of the selected blocks
            chunkX = block[0] // CHUNK_SIZE
            chunkZ = block[2] // CHUNK_SIZE
            if (chunkX, chunkZ) in self.world.chunks: # Ensure chunk exists
                self.world.chunks[(chunkX, chunkZ)].blocks[flatten_coord(block[0] % CHUNK_SIZE, block[1] % CHUNK_HEIGHT, block[2] % CHUNK_SIZE)] = 0 # Delete block
                self.world.build_chunk(chunkX, chunkZ) # Rebuild chunk mesh to show in rendering

    def place_block(self):
        block = self.get_selected_block()
        if not block == None and not block[3] == None:
            chunkX = block[3][0] // CHUNK_SIZE
            chunkZ = block[3][2] // CHUNK_SIZE
            if (chunkX, chunkZ) in self.world.chunks:
                # Ensure block is within height limit, or overflow errors will occur
                if block[3][1] < 255 and block[3][1] >= 0:
                    self.world.chunks[(chunkX, chunkZ)].blocks[flatten_coord(block[3][0] % CHUNK_SIZE, block[3][1], block[3][2] % CHUNK_SIZE)] = self.placingBlock

                    # Don't allow placing blocks that would collide with the current player
                    if self.camera.check_collision([self.camera.position[0], self.camera.position[1], self.camera.position[2]]):
                        self.world.chunks[(chunkX, chunkZ)].blocks[flatten_coord(block[3][0] % CHUNK_SIZE, block[3][1], block[3][2] % CHUNK_SIZE)] = 0

                    self.world.build_chunk(chunkX, chunkZ) # Rebuild chunk mesh to show in rendering

    def on_draw(self):
        """
        Called each frame by Pyglet to get the display.
        """
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)

        # Menu screen
        if self.screen_id == 0:
            glDisable(GL_DEPTH_TEST) # Depth testing must be disabled for menu items to render properly
            self.menu_batch.draw()
            self.play_btn_text.draw()
            self.load_btn_text.draw()
            self.controls_btn_text.draw()
            glEnable(GL_DEPTH_TEST)

        # Game / loading screen
        elif self.screen_id == 1:
            if self.world.firstLoad:
                glClearColor(0.52, 0.81, 0.92, 1)
                if not self.paused:
                    self.set_exclusive()
            else:
                # Loading screen
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

            # When mouse is held, automatically break/place blocks
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

            if self.world.firstLoad and not self.paused:
                self.camera.update()

            # Attempt to render all chunks in render distance
            self.world.render_chunks(self.camera.position, isAsync=True)

            glDisable(GL_DEPTH_TEST)
            if self.paused:
                self.paused_batch.draw()
                self.resume_btn_text.draw()
                self.quit_btn_text.draw()
                self.save_quit_btn_text.draw()
            glEnable(GL_DEPTH_TEST)

            self.crosshair_batch.draw() # Draw crosshair

            # Draw marker for the block you're looking at
            lookingAt = self.get_selected_block()

            if not lookingAt == None:
                self.marker.position = np.array([int(lookingAt[0]), int(lookingAt[1]), int(lookingAt[2])])
                self.marker.draw()

        # Help menu
        elif self.screen_id == 2:
            glDisable(GL_DEPTH_TEST)
            for textline in self.help_texts:
                textline.draw()
            self.help_batch.draw()
            self.back_btn_text.draw()
            glEnable(GL_DEPTH_TEST)

    def get_selected_block(self):
        """
        Finds block that the player is looking at
        """
        if self.world.firstLoad and not self.paused:
            floatPos = [self.camera.position[0], self.camera.position[1], self.camera.position[2]]
            currPos = [self.camera.position[0], self.camera.position[1], self.camera.position[2]]
            prevBlock = None
            prevFloat = None

            # Slowly increment the current position using the forward vector to create a pseudo "raycast".
            # When a block is found, return that along with the position of the past empty space the ray intercepted,
            # which is used for placing blocks.
            for i in range(128):
                floatPos = [self.camera.position[0] + self.camera.forward[0] * 0.05 * i, self.camera.position[1] + self.camera.forward[1] * 0.05 * i, self.camera.position[2] + self.camera.forward[2] * 0.05 * i]

                # Get positions of blocks
                # Note that int() can't be used for negatives, as a block represented by (x, y, z) will go to (x+1, y+1, z+1)
                for j in range(3):
                    if floatPos[j] < 0:
                        currPos[j] = -ceil(-floatPos[j])
                    else:
                        currPos[j] = int(floatPos[j])
                block = self.world.get_block(currPos[0], currPos[1], currPos[2])
                if block:
                    if prevBlock:
                        # Can't place blocks diagonally - find the closest center of an adjacent block to prevFloat
                        if abs(prevBlock[0]-currPos[0]) + abs(prevBlock[2]-currPos[2]) + abs(prevBlock[1]-currPos[1]) != 1:
                            minDist = float("inf")
                            adjacent = [(currPos[0]+1, currPos[1], currPos[2]), (currPos[0]-1, currPos[1], currPos[2]),
                                     (currPos[0], currPos[1]+1, currPos[2]), (currPos[0], currPos[1]-1, currPos[2]),
                                     (currPos[0], currPos[1], currPos[2]+1), (currPos[0], currPos[1], currPos[2]-1)]
                            for newPrev in adjacent:
                                # Distance between two 3d points, add 0.5 to get center of block
                                newDist = sqrt(abs(prevFloat[0]-(newPrev[0]+0.5))**2 + abs(prevFloat[1]-(newPrev[1]+0.5))**2 + abs(prevFloat[2]-(newPrev[2]+0.5))**2)
                                if newDist < minDist and not self.world.get_block(newPrev[0], newPrev[1], newPrev[2]):
                                    minDist = newDist
                                    prevBlock = newPrev

                    return (currPos[0], currPos[1], currPos[2], prevBlock)
                else:
                    prevBlock = (currPos[0], currPos[1], currPos[2])
                    prevFloat = (floatPos[0], floatPos[1], floatPos[2])

    def on_key_press(self, symbol, modifiers):
        """
        Pyglet event function.
        """
        if symbol == key.ESCAPE:
            if self.screen_id == 1:
                self.paused = not self.paused
                self.set_exclusive(False)

        # Open help menu
        elif symbol == key.H and not self.paused:
            if self.screen_id == 2:
                if self.world.firstLoad:
                    self.screen_id = 1
                    self.set_exclusive(True)
                else:
                    self.screen_id = 0
            else:
                self.screen_id = 2
                self.set_exclusive(False)

        # Keybinds
        if self.world.firstLoad and not self.paused:
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
                self.camera.curr_gravity_time = 0
            elif symbol == key.N:
                self.camera.NOCLIP_ENABLED = not self.camera.NOCLIP_ENABLED
                if self.camera.NOCLIP_ENABLED:
                    self.camera.GRAVITY_ENABLED = False

    def on_key_release(self, symbol, modifiers):
        """
        Pyglet event function.
        """
        if self.world.firstLoad:
            if symbol in self.held_keys:
                self.held_keys.remove(symbol)

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Pyglet event function.
        """
        if self.exclusive and self.world.firstLoad and not self.paused:
            self.camera.rotate(-dx, dy)
            self.camera.update_camera_vectors()

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Pyglet event function.
        """
        if button == pyglet.window.mouse.LEFT:
            if self.screen_id == 0 and self.is_clicked(self.play_btn, x, y):
                # Start game
                self.screen_id = 1
                self.camera.update_camera_vectors()
                self.camera.view_matrix = self.camera.get_view_matrix()
                self.camera.proj_matrix = self.camera.get_projection_matrix()

            elif self.screen_id == 0 and self.is_clicked(self.load_btn, x, y):
                try:
                    # Load saved game
                    with open("save.txt", "r") as f:

                        # Load player position and settings
                        posX, posY, posZ = map(float, f.readline().split())
                        camYaw, camPitch = map(float, f.readline().split())


                        g_enabled, n_enabled = f.readline().split()

                        loadedSeed = int(f.readline())
                        self.world.seed = loadedSeed

                        self.camera.position = pyrr.vector3.create(x=posX, y=posY, z=posZ, dtype=np.float32)
                        self.camera.yaw = camYaw
                        self.camera.pitch = camPitch
                        if g_enabled == "True":
                            g_enabled = True
                        else:
                            g_enabled = False
                        if n_enabled == "True":
                            n_enabled = True
                        else:
                            n_enabled = False

                        self.camera.GRAVITY_ENABLED = g_enabled
                        self.camera.NOCLIP_ENABLED = n_enabled
                        self.camera.update_camera_vectors()
                        self.camera.view_matrix = self.camera.get_view_matrix()
                        self.camera.proj_matrix = self.camera.get_projection_matrix()

                        # Load chunks
                        while True:
                            nextLine = f.readline()
                            if nextLine == "END": # End of file
                                break
                            else:
                                loadChunkX, loadChunkZ = map(int, nextLine.split())
                                loadBlocks = list(map(int, f.readline().split()))
                                self.world.in_saved[(loadChunkX, loadChunkZ)] = np.array(loadBlocks, dtype="uint8")

                    self.screen_id = 1

                except Exception as e:
                    print(e)
                    print("Err: Saved world corrupted or not found")


            elif self.screen_id == 0 and self.is_clicked(self.controls_btn, x, y):
                self.screen_id = 2
            
            elif self.screen_id == 2 and self.is_clicked(self.back_btn, x, y):
                if self.world.firstLoad:
                    self.screen_id = 1
                else:
                    self.screen_id = 0

            elif self.paused and self.is_clicked(self.resume_btn, x, y):
                self.paused = False
                self.set_exclusive(True)

            elif self.paused and self.is_clicked(self.quit_btn, x, y):
                self.close()

            elif self.paused and self.is_clicked(self.save_quit_btn, x, y):
                with open("save.txt", "w+") as f:
                    # Save player position and settings
                    f.write(" ".join([str(i) for i in self.camera.position]))
                    f.write("\n")
                    f.write(" ".join([str(self.camera.yaw), str(self.camera.pitch)]))
                    f.write("\n")
                    f.write(" ".join([str(self.camera.GRAVITY_ENABLED), str(self.camera.NOCLIP_ENABLED)]))
                    f.write("\n")
                    f.write(str(self.world.seed))
                    f.write("\n")
                    # Save chunks
                    f.write("".join([" ".join([str(i) for i in chunkKey]) + "\n" + " ".join([str(i) for i in self.world.chunks[chunkKey].blocks]) + "\n" for chunkKey in self.world.chunks]))
                    f.write("END") # Marks the end of the file
                self.close()

            elif self.world.firstLoad and not self.paused:
                self.set_exclusive()
                self.left_held = True
                self.break_selected_block()

        elif button == pyglet.window.mouse.RIGHT and self.exclusive and not self.paused:
            if self.world.firstLoad:
                self.right_held = True
                self.place_block()

    def on_mouse_release(self, x, y, button, modifiers):
        """
        Pyglet event function.
        """
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