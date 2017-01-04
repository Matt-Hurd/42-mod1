import random

def rain_water(water_grid, water, grid, size):
    for y in range(1, size - 1):
        for x in range(1, size - 1):
            if random.random() > 0.995:
                pos = y * size + x
                water_grid[pos][2] += 0.3
                water_grid[pos - 1][2] -= 0.1
                water_grid[pos + 1][2] -= 0.1

def add_water(water_grid, water, grid, size):
    for x in range(size - 2):
        water_grid[x + size + 1][2] = max(grid[1][x + 1], water_grid[x + size + 1][2]) + 0.01
