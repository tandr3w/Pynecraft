CHUNK_SIZE = 16 # Each chunk will be a CHUNK_SIZE * CHUNK_SIZE square
CHUNK_HEIGHT = 256

TPS = 60

RENDER_DISTANCE = 8 # The square of chunks from [currChunk - 8, currChunk+8] in the x and z directions will be rendered.

WORLD_SEED = 17 # Used for world generation, change to get a new world

# Camera Settings
DEFAULT_FOV = 60
NEAR = 0.1
FAR = 1000 # Maximum distance of rendered blocks
SPEED = 0.03
SENSITIVITY = 0.15 # Mouse sensitivity

COLLISION_ZONE = 0.2 # Added size to player's hitbox during collision

GRAVITY_SPEED = 15 # Blocks / Second^2; original mc uses 13

SPRINT_BOOST = 1.5 # Speed multiplier while sprinting
CROSSHAIR_SIZE = 7

REPEAT_DELAY = 0.2 # How fast blocks are automaticaslly broken/placed
FIRST_REPEAT_DELAY = 0.3 # Delay before blocks start automatically being broken/placed