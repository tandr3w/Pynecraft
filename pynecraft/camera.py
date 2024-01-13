import pyrr
import numpy as np
from pyglet.window import key
import glm
from constants import *
import utils
from math import ceil

class Camera:
    def __init__(self, app, position=(0, 70, 0), yaw=0, pitch=0):
        self.app = app
        self.sneaking = False
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = pyrr.vector3.create(x=position[0], y=position[1], z=position[2], dtype=np.float32)
        self.up = pyrr.vector3.create(x=0, y=1, z=0, dtype=np.float32)
        self.right = pyrr.vector3.create(x=1, y=0, z=0, dtype=np.float32)
        self.forward = pyrr.vector3.create(x=0, y=0, z=-1, dtype=np.float32)
        self.yaw = yaw
        self.pitch = pitch
        self.speed = SPEED
        self.curr_gravity_time = 0
        self.GRAVITY_ENABLED = True
        self.NOCLIP_ENABLED = False
        self.fov = DEFAULT_FOV
        self.GRAVITY_SPEED = GRAVITY_SPEED
        self.jumping = False
        self.view_matrix = self.get_view_matrix()
        self.proj_matrix = self.get_projection_matrix()
        self.sprinting = False
        
        # 1 = sprinting, 0 = decreasing
        self.fovTransitionType = 0

    def up_speed(self):
        self.speed += 0.01

    def down_speed(self):
        self.speed -= 0.01

    def rotate(self, rel_x, rel_y):
        self.yaw -= rel_x * SENSITIVITY
        self.pitch += rel_y * SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        # TODO: Understand this part
        self.forward[0] = glm.cos(yaw) * glm.cos(pitch)
        self.forward[1] = glm.sin(pitch)
        self.forward[2] = glm.sin(yaw) * glm.cos(pitch)
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
        if self.NOCLIP_ENABLED:
            return False
        x1 = position[0] - COLLISION_ZONE
        y1 = position[1] - 2 + 2*COLLISION_ZONE
        z1 = position[2] - COLLISION_ZONE
        X1 = position[0] + COLLISION_ZONE
        Y1 = position[1] + COLLISION_ZONE
        Z1 = position[2] + COLLISION_ZONE

        # Convert position to integers
        p = position[:]
        for j in range(3):
            if p[j] < 0:
                p[j] = -ceil(-p[j])
            else:
                p[j] = int(p[j])

        # print(p)

        # Check every block in a 3x4x3 radius around the player for collision (extremely stupid but works)
        for xMod in range(-1, 2):
            for yMod in range(-3, 2):
                for zMod in range(-1, 2):
                    blockX = p[0] + xMod
                    blockY = p[1] + yMod
                    blockZ = p[2] + zMod
                    chunkPos = (blockX // CHUNK_SIZE, blockY // CHUNK_HEIGHT, blockZ // CHUNK_SIZE)
                    if (chunkPos[0], chunkPos[2]) in self.app.world.chunks:
                        if self.app.world.chunks[(chunkPos[0], chunkPos[2])].blocks[utils.flatten_coord(blockX % CHUNK_SIZE, blockY % CHUNK_HEIGHT, blockZ % CHUNK_SIZE)]:
                            # print((blockX, blockY, blockZ))
                            # Create bounding box for block
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
        print(self.position)
        velocity = self.speed * self.app.delta_time * 100
        if not self.sneaking and key.LCTRL in self.app.held_keys and key.W in self.app.held_keys:
            velocity *= SPRINT_BOOST
            self.fovTransitionType = 1
            self.sprinting = True
        else:
            self.fovTransitionType = 0
            self.sprinting = False

        if key.LSHIFT in self.app.held_keys and self.GRAVITY_ENABLED == True:
            self.sprinting = False
            velocity *= 0.5
            self.sneaking = True
        else:
            self.sneaking = False            

        if self.fovTransitionType == 1:
            if self.fov < DEFAULT_FOV + 5:
                self.fov += 1   
        else:
            if self.fov > DEFAULT_FOV:
                self.fov -= 1
            if self.fov < DEFAULT_FOV:
                self.fov += 1

        self.proj_matrix = self.get_projection_matrix()
        self.view_matrix = self.get_view_matrix()

        moveForward = pyrr.vector.normalise(np.array([self.forward[0], self.forward[2]], dtype=np.float32)) * velocity
        moveRight = pyrr.vector.normalise(np.array([self.right[0], self.right[2]], dtype=np.float32)) * velocity
        toMove = [0, 0, 0]
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

        for j in range(3):
            if toMove[j] > velocity:
                toMove[j] = velocity
            if toMove[j] < -velocity:
                toMove[j] = -velocity
        

        if not self.check_collision([self.position[0] + toMove[0], self.position[1], self.position[2]]):
            if self.jumping or (not self.sneaking) or self.check_collision([self.position[0] + toMove[0], self.position[1] - 0.1, self.position[2]]):
                self.position[0] += toMove[0]
        if not self.check_collision([self.position[0], self.position[1] + toMove[1], self.position[2]]):            
            self.position[1] += toMove[1]
        if not self.check_collision([self.position[0], self.position[1], self.position[2] + toMove[2]]):
            if self.jumping or (not self.sneaking) or self.check_collision([self.position[0], self.position[1] - 0.1, self.position[2] + toMove[2]]):
                self.position[2] += toMove[2]

        if self.GRAVITY_ENABLED and self.app.world.firstLoad and (self.position[0]//CHUNK_SIZE, self.position[2]//CHUNK_SIZE) in self.app.world.chunks:
            gravity_drop = self.GRAVITY_SPEED*self.curr_gravity_time*self.app.delta_time
            if self.jumping:
                gravity_drop -= 6*self.app.delta_time
            self.curr_gravity_time += self.app.delta_time
            gravity_drop = min(gravity_drop, 0.9)
            gravity_drop = max(gravity_drop, -0.9)

            if not self.check_collision([self.position[0], self.position[1] - gravity_drop, self.position[2]]):
                self.position[1] -= gravity_drop
            else:
                self.curr_gravity_time = 0
                self.jumping = False


    def get_projection_matrix(self):
        return pyrr.matrix44.create_perspective_projection(
            fovy = self.fov, aspect = self.aspect_ratio, 
            near = NEAR, far = FAR, dtype=np.float32
        )

    def get_view_matrix(self):
        if self.sneaking:
            self.position[1] -= 0.1
            res = pyrr.matrix44.create_look_at(self.position, self.position + self.forward, self.up, dtype=np.float32)
            self.position[1] += 0.1
            return res
        return pyrr.matrix44.create_look_at(self.position, self.position + self.forward, self.up, dtype=np.float32)