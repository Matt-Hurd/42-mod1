def rain_water(water_grid, water, grid, size):
    for x in range(size * size):
        # if x / size > 0 and x / size < size:
        water_grid[x][2] = max(grid[0][0], water_grid[0][2]) + 0.001

def add_water(water_grid, water, grid, size):
    for x in range(size):
        water_grid[x][2] = max(grid[0][0], water_grid[0][2]) + 0.01
