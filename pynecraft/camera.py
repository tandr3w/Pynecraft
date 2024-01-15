import pyrr
import numpy as np
from pyglet.window import key
import glm
from constants import *
from chunk_builder import flatten_coord
from math import ceil

class Camera:
    def __init__(self, app, position=(0, 70, 0), yaw=0, pitch=0):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]

        # Player position and movement vectors
        self.position = pyrr.vector3.create(x=position[0], y=position[1], z=position[2], dtype=np.float32)
        self.up = pyrr.vector3.create(x=0, y=1, z=0, dtype=np.float32)
        self.right = pyrr.vector3.create(x=1, y=0, z=0, dtype=np.float32)
        self.forward = pyrr.vector3.create(x=0, y=0, z=-1, dtype=np.float32)
        self.yaw = yaw
        self.pitch = pitch

        self.curr_gravity_time = 0 # The current time that the player has been falling for.

        # Player states
        self.jumping = False
        self.sprinting = False
        self.sneaking = False
        self.GRAVITY_ENABLED = True
        self.NOCLIP_ENABLED = False
        self.fov = DEFAULT_FOV
        self.speed = SPEED

        # 1 = sprinting, 0 = standing. Gradually shifts FOV based on value.
        self.fovTransitionType = 0

        self.view_matrix = self.get_view_matrix()
        self.proj_matrix = self.get_projection_matrix()

    def up_speed(self):
        self.speed += 0.01

    def down_speed(self):
        self.speed -= 0.01

    def rotate(self, rel_x, rel_y):
        """
        Changes pitch and yaw of the camera based on how much the mouse has moved
        rel_x: mouse movement since last frame in the X direction
        rel_y: mouse movement since last frame in the Y direction
        """
        self.yaw -= rel_x * SENSITIVITY
        self.pitch += rel_y * SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        """
        Uses trigonometry to calculate movement vectors from the pitch and yaw
        self.forward[x, y, z]: Stores how the position would change when moving forward in each axis
        self.right[x, y, z]: Stores how the position would change when moving right in each axis
        self.up[x, y, z]: Stores how the position would change when moving up in each axis
        """
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward[0] = glm.cos(yaw) * glm.cos(pitch)
        self.forward[1] = glm.sin(pitch)
        self.forward[2] = glm.sin(yaw) * glm.cos(pitch)

        # Ensure all vector values are within the range [-1, 1]
        self.forward = pyrr.vector.normalise(self.forward)
        self.right = pyrr.vector.normalise(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = pyrr.vector.normalise(glm.cross(self.right, self.forward))

        self.forward = np.array(self.forward, dtype=np.float32)
        self.right = np.array(self.right, dtype=np.float32)
        self.up = np.array(self.up, dtype=np.float32)

    def update(self):
        self.move()
        self.view_matrix = self.get_view_matrix()

    # Used for collision, checks if two intervals overlap
    def overlap(self, v1, V1, v2, V2):
        return v1 <= v2 <= V1 or v1 <= V2 <= V1 or v2 <= v1 <= V2 or v2 <= V1 <= V2

    def check_collision(self, position):
        """
        Creates bounding boxes for the player and all neighboring blocks, then checks if they are colliding
        """
        if self.NOCLIP_ENABLED:
            return False
        x1 = position[0] - COLLISION_ZONE
        y1 = position[1] - 1.9 + 2*COLLISION_ZONE
        z1 = position[2] - COLLISION_ZONE
        X1 = position[0] + COLLISION_ZONE
        Y1 = position[1] + COLLISION_ZONE
        Z1 = position[2] + COLLISION_ZONE

        # Convert position to integers, rounded to the lower number
        p = position[:]
        for j in range(3):
            if p[j] < 0:
                p[j] = -ceil(-p[j])
            else:
                p[j] = int(p[j])

        # Check every block in a 3x4x3 radius around the player for collision (extremely stupid but works)
        for xMod in range(-1, 2):
            for yMod in range(-3, 2):
                for zMod in range(-1, 2):
                    blockX = p[0] + xMod
                    blockY = p[1] + yMod
                    blockZ = p[2] + zMod

                    chunkPos = (blockX // CHUNK_SIZE, blockY // CHUNK_HEIGHT, blockZ // CHUNK_SIZE)

                    if (chunkPos[0], chunkPos[2]) in self.app.world.chunks:
                        if self.app.world.chunks[(chunkPos[0], chunkPos[2])].blocks[flatten_coord(blockX % CHUNK_SIZE, blockY % CHUNK_HEIGHT, blockZ % CHUNK_SIZE)]: # Block exists and is not air

                            x2 = blockX
                            y2 = blockY
                            z2 = blockZ
                            X2 = blockX + 1
                            Y2 = blockY + 1
                            Z2 = blockZ + 1

                            if self.overlap(x1, X1, x2, X2) and self.overlap(y1, Y1, y2, Y2) and self.overlap(z1, Z1, z2, Z2):
                                return True
                    else:
                        return True
        return False

    def move(self):
        velocity = self.speed * self.app.delta_time * 100

        # Check if the user is sprinting.
        if key.LCTRL in self.app.held_keys and key.W in self.app.held_keys or (self.sprinting and key.W in self.app.held_keys):            
            velocity *= SPRINT_BOOST
            self.fovTransitionType = 1
            self.sprinting = True
        else:
            self.fovTransitionType = 0
            self.sprinting = False

        # Check if the user is sneaking
        if key.LSHIFT in self.app.held_keys and self.GRAVITY_ENABLED == True:
            self.sprinting = False
            velocity *= 0.5
            self.sneaking = True
        else:
            self.sneaking = False            

        # Gradually changes FOV based on whether the user is sprinting or not
        if self.fovTransitionType == 1:
            # User is sprinting; increase FOV
            if self.fov < DEFAULT_FOV + 5:
                self.fov += 1   
        else:
            # User is not sprinting: move towards resetting FOV to default
            if self.fov > DEFAULT_FOV:
                self.fov -= 1
            if self.fov < DEFAULT_FOV:
                self.fov += 1

        # Matrices need to be updated to reflect any changes in FOV
        self.proj_matrix = self.get_projection_matrix()
        self.view_matrix = self.get_view_matrix()

        # When walking, the y values of self.forward and self.right are ignored.
        moveForward = pyrr.vector.normalise(np.array([self.forward[0], self.forward[2]], dtype=np.float32)) * velocity
        moveRight = pyrr.vector.normalise(np.array([self.right[0], self.right[2]], dtype=np.float32)) * velocity

        toMove = [0, 0, 0] # Stores how much movement the combination of keys held would casue

        if key.W in self.app.held_keys:
            toMove[0] += moveForward[0]
            toMove[2] += moveForward[1]

        if key.S in self.app.held_keys:
            toMove[0] -= moveForward[0]
            toMove[2] -= moveForward[1]

        if key.A in self.app.held_keys:
            toMove[0] -= moveRight[0]
            toMove[2] -= moveRight[1]

        if key.D in self.app.held_keys:
            toMove[0] += moveRight[0]
            toMove[2] += moveRight[1]

        if key.SPACE in self.app.held_keys:
            if self.GRAVITY_ENABLED:
                self.jumping = True
            else:
                toMove[1] += velocity

        if not self.GRAVITY_ENABLED:
            if key.LSHIFT in self.app.held_keys:
                toMove[1] -= velocity

        # Ensure the combined movement can't go too fast
        for j in range(3):
            if toMove[j] > velocity:
                toMove[j] = velocity
            if toMove[j] < -velocity:
                toMove[j] = -velocity
        
        # Move the player in the X direction only if it wouldn't cause a collision.
        if not self.check_collision([self.position[0] + toMove[0], self.position[1], self.position[2]]):
            if self.jumping or (not self.sneaking) or self.check_collision([self.position[0] + toMove[0], self.position[1] - 0.1, self.position[2]]): # If the player is sneaking and not jumping, also don't move the player if it would cause the block below them to be air.
                self.position[0] += toMove[0]

        # Move the player in the Y direction only if it wouldn't cause a collision.
        if not self.check_collision([self.position[0], self.position[1] + toMove[1], self.position[2]]):            
            self.position[1] += toMove[1]

        # Move the player in the Z direction only if it wouldn't cause a collision.
        if not self.check_collision([self.position[0], self.position[1], self.position[2] + toMove[2]]):
            if self.jumping or (not self.sneaking) or self.check_collision([self.position[0], self.position[1] - 0.1, self.position[2] + toMove[2]]):
                self.position[2] += toMove[2]

        # Calculate gravity using a quadratic function
        if self.GRAVITY_ENABLED and self.app.world.firstLoad and (self.position[0]//CHUNK_SIZE, self.position[2]//CHUNK_SIZE) in self.app.world.chunks:
            gravity_drop = GRAVITY_SPEED*self.curr_gravity_time*self.app.delta_time
            if self.jumping:
                gravity_drop -= 5.8*self.app.delta_time
            self.curr_gravity_time += self.app.delta_time

            # Prevent moving at over 1 block per frame, as that would result in clipping
            gravity_drop = min(gravity_drop, 0.9)
            gravity_drop = max(gravity_drop, -0.9)

            # If it would not cause a collision, move the player downwards based on gravity
            if not self.check_collision([self.position[0], self.position[1] - gravity_drop, self.position[2]]):
                self.position[1] -= gravity_drop
            else:
                # If there is a collision, reset the falling time and stop jumping.
                self.curr_gravity_time = 0
                self.jumping = False

    def get_projection_matrix(self):
        """
        Transforms world coordinates to be in relation to the camera's perspective
        """
        return pyrr.matrix44.create_perspective_projection(
            fovy = self.fov, aspect = self.aspect_ratio, 
            near = NEAR, far = FAR, dtype=np.float32
        )

    def get_view_matrix(self):
        """
        Transforms coordinates of the camera's perspective to be in relation to the user's screen
        """
        if self.sneaking:
            self.position[1] -= 0.1
            res = pyrr.matrix44.create_look_at(self.position, self.position + self.forward, self.up, dtype=np.float32)
            self.position[1] += 0.1
            return res
        return pyrr.matrix44.create_look_at(self.position, self.position + self.forward, self.up, dtype=np.float32)