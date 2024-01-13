            if local_height < 0:
                continue
            for y in range(min(local_height, CHUNK_HEIGHT)):
                if local_height - y <= 1:
                    blocks[flatten_coord(x, y, z)] = 2
                elif local_height - y <= 3:
                    blocks[flatten_coord(x, y, z)] = 3
                else:
                    blocks[flatten_coord(x, y, z)] = randint(4, 7)