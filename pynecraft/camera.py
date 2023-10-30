import pyrr
import numpy as np
from pyglet.window import key
import glm

FOV = 50
NEAR = 0.1
FAR = 100
SPEED = 0.03
SENSITIVITY = 0.15

class Camera:
    def __init__(self, app, position=(0, 0, 4), yaw=-90, pitch=0):
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
        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

        self.forward = np.array(self.forward, dtype=np.float32)
        self.right = np.array(self.right, dtype=np.float32)
        self.up = np.array(self.up, dtype=np.float32)

    def update(self):
        self.move()
        self.view_matrix = self.get_view_matrix()

    def move(self):
        velocity = SPEED * self.app.delta_time * 100
        # Want to make these move without moving up?
        # Set the z of all the forward, right to 0, and the forward/right of the up to 0 as well. Normalize the other ones.
        if key.W in self.app.held_keys:
            self.position += self.forward * velocity
        if key.S in self.app.held_keys:
            self.position -= self.forward * velocity
        if key.A in self.app.held_keys:
            self.position -= self.right * velocity
        if key.D in self.app.held_keys:
            self.position += self.right * velocity
        if key.SPACE in self.app.held_keys:
            self.position += self.up * velocity
        if key.LSHIFT in self.app.held_keys:
            self.position -= self.up * velocity

    def get_projection_matrix(self):
        return pyrr.matrix44.create_perspective_projection(
            fovy = FOV, aspect = self.aspect_ratio, 
            near = NEAR, far = FAR, dtype=np.float32
        )

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(self.position, self.position + self.forward, self.up, dtype=np.float32)