from numba import njit

import random

@njit
def getRandom():
    return random.random()

@njit
def generate_terrain(CHUNK_SIZE, CHUNK_HEIGHT, chunkX, chunkZ, flatten_coord, blocks, perm, perm_grad_index3, _noise2, _noise3, random):
    # https://www.redblobgames.com/maps/terrain-from-noise/
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            amplitude = [20, 12, 6, 2] # higher = taller hills, lower valleys
            sea_level = 52
            scale = [0.01, 0.02, 0.04, 0.08] # higher = more frequent, less fat hills

            # Mix in different values of amplitude and scale to make more interesting terrain
            local_height = sea_level + 16
            for i in range(len(amplitude)):
                local_height += _noise2((chunkX*CHUNK_SIZE + x) * scale[i], (chunkZ*CHUNK_SIZE + z) * scale[i], perm) * amplitude[i]

            if _noise2((chunkX*CHUNK_SIZE + x) * 0.04, (chunkZ*CHUNK_SIZE + z) * 0.04, perm) > 0:
                local_height //= 1.05 # Randomly lower areas to form plateaus


            local_height = int(local_height)

            if local_height < sea_level:
                local_height = sea_level

            if local_height < 0 or local_height > 128:
                continue

            
            for y in range(min(local_height, CHUNK_HEIGHT)):
                # Generate caves with 3d noise
                if local_height - y >= random()*7 and _noise3((chunkX*CHUNK_SIZE + x)*0.08, y*0.08, (chunkZ*CHUNK_SIZE + z) * 0.08, perm, perm_grad_index3) > 0.25 and y > 0:
                    blocks[flatten_coord(x, y, z)] = 0
                else:
                    if local_height - y >= 3:
                        blocks[flatten_coord(x, y, z)] = 4
                    else:
                        random_height = local_height - random()*2
                        if random_height <= 55:
                            blocks[flatten_coord(x, y, z)] = 1
                        elif random_height <= 56:
                            blocks[flatten_coord(x, y, z)] = 3
                        elif random_height <= 74:
                            blocks[flatten_coord(x, y, z)] = 2
                        elif random_height <= 75:
                            blocks[flatten_coord(x, y, z)] = 3
                        elif random_height <= 78:
                            blocks[flatten_coord(x, y, z)] = 4
                        else:
                            blocks[flatten_coord(x, y, z)] = 5

    return blocks