from constants import *

def flatten_coord(x, y, z):
    """
    Converts (x, y, z) representation of blocks into a single integer
    """
    return x + CHUNK_SIZE * z + CHUNK_SIZE**2 * y

def unflatten_coord(coord):
    """
    Converts integer representation of blocks into (x, y, z)
    """
    return (coord % CHUNK_SIZE, coord % CHUNK_SIZE**2, coord // CHUNK_SIZE**2)
