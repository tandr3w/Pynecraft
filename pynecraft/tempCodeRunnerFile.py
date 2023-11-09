            chunkX = block[0] // CHUNK_SIZE
            chunkZ = block[2] // CHUNK_SIZE
            if (chunkX, chunkZ) in self.world.chunks:
                self.world.chunks[(chunkX, chunkZ)].blocks[flatten_coord(x % CHUNK_SIZE, y % CHUNK_HEIGHT, z % CHUNK_SIZE)] = 0
                self.world.build_chunk(chunkX, chunkZ)