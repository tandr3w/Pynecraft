from OpenGL.GL import *
import pyglet

class Material:    
    def __init__(self, filepath, isArr=False):
        image = pyglet.image.load(filepath)
        image_width, image_height = image.width, image.height
        self.texture = glGenTextures(1)
        pitch = image.width * len("RGBA")
        img_data = image.get_data("RGBA", pitch)
        if not isArr:
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
            glGenerateMipmap(GL_TEXTURE_2D)
        else:
            glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
            glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8, image_width, image_height // 8, 8)

            glPixelStorei(GL_UNPACK_ROW_LENGTH, image_width)

            for x in range(8):
                glPixelStorei(GL_UNPACK_SKIP_ROWS, image_height // 8 * x)
                glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, 8-x-1, image_width, image_height // 8, 1, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))
