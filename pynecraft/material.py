from OpenGL.GL import *
import pyglet

class Material:    
    """
    This class handles the usage and initialization of textures and texture arrays
    """

    def __init__(self, filepath, isArr=False):
        self.isArr = isArr

        # Extract usable data for OpenGL from image
        image = pyglet.image.load(filepath)
        image_width, image_height = image.width, image.height
        self.texture = glGenTextures(1)
        pitch = image.width * len("RGBA")
        img_data = image.get_data("RGBA", pitch)

        if not isArr:
            # Initialize settings for texture
            glPixelStorei(GL_UNPACK_ROW_LENGTH, image_width) # Length of each row of the image
            glPixelStorei(GL_UNPACK_SKIP_ROWS, 0) # Number of rows skipped from the top

            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # Generate texture
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
            glGenerateMipmap(GL_TEXTURE_2D)
        else:
            glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)

            # Create texture array storage
            glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8, image_width, image_height // 8, 8)

            glPixelStorei(GL_UNPACK_ROW_LENGTH, image_width) # Set length of eachc image row

            # Takes in an image containing 8 rows of equal height. Extracts each row, and stores it inside of the texture array
            for x in range(8):
                glPixelStorei(GL_UNPACK_SKIP_ROWS, image_height // 8 * x) # Skip all processed rows to get the next one
                glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, 8-x-1, image_width, image_height // 8, 1, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

            # Initialize settings for texture
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # Generate texture
            glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

    # Selects this texture as the one currently used for rendering
    def use(self):
        glActiveTexture(GL_TEXTURE0)
        if self.isArr:
            glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
        else:
            glBindTexture(GL_TEXTURE_2D, self.texture)

