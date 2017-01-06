import numpy
import math
import sys

def normalize_input(input):
    #Temporarily assuming a scale of 0-20000 on x and y, 0-5000 on z
    newarray = []
    for group in input:
        newarray.append([(float(x)/20000, float(y)/20000, float(z)/5000) for x, y, z in group])
    return newarray

def gen_mountain(size, grid, point, origin, depth):
    if depth > sys.getrecursionlimit() - 10:
        return
    x, y = point
    ox, oy, oz = origin
    ox *= size
    oy *= size
    dist = numpy.linalg.norm(numpy.array((x, y)) - numpy.array((ox, oy)))
    dist = dist if dist else 0.00000001
    height = ((size * 0.7) - dist * numpy.log(dist)) / (size * 0.7) * oz
    if (grid[y][x] >= height or height <= 0):
        return
    grid[y][x] = height
    if x >= 1:
        gen_mountain(size, grid, (x - 1, y), origin, depth + 1)
    if x < size - 1:
        gen_mountain(size, grid, (x + 1, y), origin, depth + 1)
    if y >= 1:
        gen_mountain(size, grid, (x, y - 1), origin, depth + 1)
    if y < size - 1:
        gen_mountain(size, grid, (x, y + 1), origin, depth + 1)

def gen_group(group, size, grid):
    for g1 in group:
        for g2 in group:
            if g1 != g2:
                x, y, z = g1
                x2, y2, z2 = g2
                if (x == x2 and z == z2 and z > 0.8):
                    y *= size
                    y2 *= size
                    i = min(y, y2)
                    while i < max(y, y2):
                        gen_mountain(size, grid, (int(x * size), int(i)), (x, i / size, z), 0)
                        i += 1
                if (y == y2 and z == z2 and z > 0.8):
                    x *= size
                    x2 *= size
                    i = min(x, x2)
                    while i < max(x, x2):
                        gen_mountain(size, grid, (int(i), int(y * size)), (i / size, y, z), 0)
                        i += 1

def gen_grid(size, input):
    normal = normalize_input(input)
    if len(normal) == 1 and len(normal[0]) == 1:
        normal[0][0] = (0.5, 0.5, 1.1)
    grid = []
    for x in range(size):
        t = []
        for y in range(size):
            t.append(0)
        grid.append(t)
    # print normal
    for group in normal:
        gen_group(group, size, grid) #v2
    for group in normal:
        # if len(group) > 1:
        for g in group:
            x, y, z = g
            gen_mountain(size, grid, (int(x * size), int(y * size)), g, 0)
    return grid

def add_border(size, grid):
    add = [0 for x in range(size)]
    grid.insert(0, add)
    add = [0 for x in range(size)]
    grid.append(add)
    add = [-2.0 for x in range(size + 4)]
    grid.insert(0, add)
    add = [-2.0 for x in range(size + 4)]
    grid.append(add)
    for x in range(1, size + 3):
        grid[x].insert(0, 0)
        grid[x].append(0)
        grid[x].insert(0, -2)
        grid[x].append(-2)
