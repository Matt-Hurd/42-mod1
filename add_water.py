import random

def rain_water(water_grid, water, grid, size, rate):
    for y in range(2, size - 2):
        for x in range(2, size - 2):
            if random.random() > 0.995:
                pos = y * size + x
                water_grid[pos][2] += 0.81 * rate
                water_grid[pos - 1][2] -= 0.4
                water_grid[pos + 1][2] -= 0.4

def fill_edges(water_grid, water, grid, size, rate):
    for y in range(1, size - 1):
        for x in range(1, size - 1):
            if x == 1 or x == size - 2 or y == 1 or y == size - 2:
                water_grid[x + y * size][2] = max(grid[y][x], water_grid[x + y * size][2]) + 0.003 * rate


def fill_center(water_grid, water, grid, size, rate):
    water_grid[(size ** 2) / 2 + size / 2][2] =  1 * rate

def add_water(water_grid, water, grid, size, rate, pos):
    if pos / 10 < size - 4:
        for x in range(size - 2):
            water_grid[x + size * (pos / 10 + 1) + 1][2] = rate
