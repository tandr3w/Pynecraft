import pyrr
import numpy as np
from pyglet.window import key
import glm
from constants import *
import utils

FOV = 50
NEAR = 0.1
FAR = 100
SPEED = 0.03
SENSITIVITY = 0.15
COLLISION_ZONE = 0.2

class Camera:
    def __init__(self, app, position=(0, 40, 0), yaw=0, pitch=0):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = pyrr.vector3.create(x=position[0], y=position[1], z=position[2], dtype=np.float32)
        self.up = pyrr.vector3.create(x=0, y=1, z=0, dtype=np.float32)
        self.right = pyrr.vector3.create(x=1, y=0, z=0, dtype=np.float32)
        self.forward = pyrr.vector3.create(x=0, y=0, z=-1, dtype=np.float32)
        self.yaw = yaw
        self.pitch = pitch
        self.view_matrix = self.get_view_matrix()
        self.proj_matrix = self.get_projection_matrix()

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

    def check_collision(self, position):
        return False # Disabled for now
        x, y, z = position
        for p in ([x+COLLISION_ZONE, y + COLLISION_ZONE, z+COLLISION_ZONE], [x-COLLISION_ZONE, y + COLLISION_ZONE, z-COLLISION_ZONE], [x+COLLISION_ZONE, y-1, z+COLLISION_ZONE], [x-COLLISION_ZONE, y-1, z-COLLISION_ZONE]):
            chunkPos = ((p[0]) // CHUNK_SIZE, (p[1]) // CHUNK_SIZE, (p[2]) // CHUNK_SIZE)
            if chunkPos in self.app.world.chunks:
                if self.app.world.chunks[chunkPos].mesh.blocks[utils.flatten_coord(int(p[0]) % CHUNK_SIZE, int(p[1]) % CHUNK_SIZE, int(p[2]) % CHUNK_SIZE)]:
                        return True
        return False

    def move(self):
        velocity = SPEED * self.app.delta_time * 100
        # Want to make these move without moving up?
        # Set the z of all the forward, right to 0, and the forward/right of the up to 0 as well. Normalize the other ones.
        toMove = [0, 0, 0]
        moveForward = pyrr.vector.normalise(np.array([self.forward[0], self.forward[2]], dtype=np.float32)) * velocity
        moveRight = pyrr.vector.normalise(np.array([self.right[0], self.right[2]], dtype=np.float32)) * velocity
        if key.W in self.app.held_keys:
            toMove[0] += moveForward[0]
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[0] -= moveForward[0]
            toMove[2] += moveForward[1]
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[2] -= moveForward[1]
        if key.S in self.app.held_keys:
            toMove[0] -= moveForward[0]
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[0] += moveForward[0]
            toMove[2] -= moveForward[1]
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[2] += moveForward[1]
        if key.A in self.app.held_keys:
            toMove[0] -= moveRight[0]
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[0] += moveRight[0]
            toMove[2] -= moveRight[1]
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[2] += moveRight[1]
        if key.D in self.app.held_keys:
            toMove[0] += moveRight[0]
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[0] -= moveRight[0]
            toMove[2] += moveRight[1]
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[2] -= moveRight[1]
        if key.SPACE in self.app.held_keys:
            toMove[1] += velocity
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[1] -= velocity
        if key.LSHIFT in self.app.held_keys:
            toMove[1] -= velocity
            if self.check_collision([self.position[0] + toMove[0], self.position[1] + toMove[1], self.position[2] + toMove[2]]):
                toMove[1] += velocity

        self.position[0] += toMove[0]
        self.position[1] += toMove[1]
        self.position[2] += toMove[2]

    def get_projection_matrix(self):
        return pyrr.matrix44.create_perspective_projection(
            fovy = FOV, aspect = self.aspect_ratio, 
            near = NEAR, far = FAR, dtype=np.float32
        )

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(self.position, self.position + self.forward, self.up, dtype=np.float32)