#!/usr/bin/env python

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import lookAt
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from panda3d.core import PerspectiveLens
from panda3d.core import CardMaker
from panda3d.core import Light, Spotlight
from panda3d.core import TextNode
from panda3d.core import LVector3
from panda3d.core import Point3
from panda3d.core import TransparencyAttrib
from panda3d.core import GeomVertexReader
from panda3d.core import GeomVertexWriter
import sys
import os
from gen_grid import gen_grid, add_border
from parse_file import parse_file

def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec

def color_point(color, z):
    green = (7.0 / 255, 175.0 / 255, 43.0 / 255)
    brown = (139.0 / 255, 69.0 / 255, 19.0 / 255)
    white = (255.0 / 255, 255.0 / 255, 255.0 / 255)
    if (z < 0.5):
        p = z / 0.5;
        r = (green[0] * (1.0 - p)) + (brown[0] * p)
        g = (green[1] * (1.0 - p)) + (brown[1] * p)
        b = (green[2] * (1.0 - p)) + (brown[2] * p)
    elif (z <= 1.0):
        p = (z - 0.5) / 0.5;
        r = (brown[0] * (1.0 - p)) + (white[0] * p)
        g = (brown[1] * (1.0 - p)) + (white[1] * p)
        b = (brown[2] * (1.0 - p)) + (white[2] * p)
    else:
        r = 1
        g = 1
        b = 1
    # print r, g, b
    color.addData4f(r, g, b, 1.0)

water_vdata = None

def gen_water(size):
    global water_vdata
    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData('water', format, Geom.UHDynamic)
    water_vdata = vdata
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    for y in range(size):
        for x in range(size):
            fx = float(x) / size * 5 - 2.5
            fy = float(y) / size * 5 - 2.5
            z = -0.1
            vertex.addData3(fx, fy, z)
            normal.addData3(normalized(2 * fx - 1, 2 * fy - 1, 2 * z - 1))
            color.addData4f(0, 0, 0.8, 0)
    tris = GeomTriangles(Geom.UHDynamic)

    for y in range(size):
        for x in range(size):
            if (y < size - 1 and x < size - 1):
                tris.addVertices(x + y * size, x + y * size + 1, x + (y + 1) * size)
            if (y > 0 and x > 0):
                tris.addVertices(x + y * size, x + y * size - 1, x + (y - 1) * size)


    land = Geom(vdata)
    land.addPrimitive(tris)
    return land

def land_from_grid(grid, size):
    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData('square', format, Geom.UHDynamic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    for y in range(size):
        for x in range(size):
            fx = float(x) / size * 5 - 2.5
            fy = float(y) / size * 5 - 2.5
            z = grid[y][x]
            vertex.addData3(fx, fy, z)
            normal.addData3(normalized(2 * fx - 1, 2 * fy - 1, 2 * z - 1))
            color_point(color, z)
    tris = GeomTriangles(Geom.UHDynamic)

    for y in range(size):
        for x in range(size):
            if (y < size - 1 and x < size - 1):
                tris.addVertices(x + y * size, x + y * size + 1, x + (y + 1) * size)
            if (y > 0 and x > 0):
                tris.addVertices(x + y * size, x + y * size - 1, x + (y - 1) * size)


    land = Geom(vdata)
    land.addPrimitive(tris)
    return land

def drain_water(water_grid):
    global water, grid, water_vdata, size
    water_grid[(size ** 2) / 2 - size / 2][2] -= 0.1

def rain_water(water_grid):
    global water, grid, water_vdata, size
    for x in range(size * size):
        water_grid[x][2] = max(grid[0][0], water_grid[0][2]) + 0.001

def add_water(water_grid):
    global water, grid, water_vdata, size
    for x in range(size):
        water_grid[x][2] = max(grid[0][0], water_grid[0][2]) + 0.01

def distribute_water(water_grid, drain):
    global water, grid, water_vdata, size
    for x in range(size * size):
        '''water_grid[x] == grid[x / size][x % size]'''
        if (x + 1) % size != 0 and (drain or water_grid[x][2] > grid[(x + 1) / size][(x + 1) % size]):
            if water_grid[x][2] > water_grid[x + 1][2]:
                t = (water_grid[x][2] - water_grid[x + 1][2]) / 2
                water_grid[x + 1][2] += t
                water_grid[x][2] -= t
            elif water_grid[x][2] < water_grid[x + 1][2]:
                t = (water_grid[x + 1][2] - water_grid[x][2]) / 2
                water_grid[x][2] += t
                water_grid[x + 1][2] -= t
        if x / size < size - 1 and water_grid[x][2] > grid[(x + size) / size][(x) % size]:
            if water_grid[x][2] > water_grid[x + size][2]:
                t = (water_grid[x][2] - water_grid[x + size][2]) / 2
                water_grid[x + size][2] += t
                water_grid[x][2] -= t
            elif water_grid[x][2] < water_grid[x + size][2]:
                t = (water_grid[x + size][2] - water_grid[x][2]) / 2
                water_grid[x][2] += t
                water_grid[x + size][2] -= t

def reset_flood():
    global water_vdata
    vertex = GeomVertexReader(water_vdata, 'vertex')
    vwrite = GeomVertexWriter(water_vdata, 'vertex')
    cwrite = GeomVertexWriter(water_vdata, 'color')
    water_grid = []
    while not vertex.isAtEnd():
        v = vertex.getData3f()
        water_grid.append([v[0], v[1], v[2]])
    for v in water_grid:
        vwrite.setData3f(v[0], v[1], -0.1)
        cwrite.addData4f(0, 0, 0.8, 0)

def handle_flood(flood_type):
    global water_vdata
    vertex = GeomVertexReader(water_vdata, 'vertex')
    vwrite = GeomVertexWriter(water_vdata, 'vertex')
    cwrite = GeomVertexWriter(water_vdata, 'color')
    water_grid = []
    while not vertex.isAtEnd():
        v = vertex.getData3f()
        water_grid.append([v[0], v[1], v[2]])
    if flood_type == 0:
        rain_water(water_grid)
        distribute_water(water_grid, 0)
    if flood_type == 1:
        add_water(water_grid)
        distribute_water(water_grid, 0)
    if flood_type == '-':
        drain_water(water_grid)
        distribute_water(water_grid, 1)
    for v in water_grid:
        vwrite.setData3f(v[0], v[1], v[2])
        if (v[2] > 0):
            cwrite.addData4f(0, 0, 0.8, 1)
        else:
            cwrite.addData4f(0, 0, 0.8, 0)

class MyTapper(DirectObject):
    def __init__(self):
        self.accept("1", self.rain)
        self.accept("2", self.flood)
        self.accept("0", self.stop)
        self.accept("-", self.drain)
        self.floodInterval = None

    def rain(self):
        self.stop()
        self.floodInterval = Func(handle_flood, 0)
        self.floodInterval.start()
        self.floodInterval.loop()

    def flood(self):
        self.stop()
        self.floodInterval = Func(handle_flood, 1)
        self.floodInterval.start()
        self.floodInterval.loop()

    def stop(self):
        if self.floodInterval:
            self.floodInterval.finish()
        reset_flood()

    def drain(self):
        if self.floodInterval:
            self.floodInterval.finish()
        self.floodInterval = Func(handle_flood, '-')
        self.floodInterval.start()
        self.floodInterval.loop()

water = None
land = None
grid = None
size = 50
def main(inputfile):
    global water, land, grid, size
    base = ShowBase()
    snode = GeomNode('land')
    grid = gen_grid(size, parse_file(inputfile))
    # add_border(size, grid)
    snode.addGeom(land_from_grid(grid, size))
    land = render.attachNewNode(snode)
    # land.setScale(1.03)

    snode = GeomNode('water')
    snode.addGeom(gen_water(size))
    water = render.attachNewNode(snode)
    water.setTransparency(TransparencyAttrib.MAlpha)
    water.setAlphaScale(0.9)
    water.setTwoSided(True)
    land.setTwoSided(True)
    t = MyTapper()
    base.trackball.node().setPos(0, 20, -0.5)
    base.run()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        print main(sys.argv[1])
    else:
        print "usage: %s [input file]" % sys.argv[0]
