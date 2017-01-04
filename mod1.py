#!/usr/bin/env python

import sys
import os
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import Texture, GeomNode
from panda3d.core import TransparencyAttrib
from panda3d.core import GeomVertexReader
from panda3d.core import GeomVertexWriter
from panda3d.core import TextNode
from gen_grid import gen_grid, add_border
from parse_file import parse_file
from generate_models import gen_water, land_from_grid
from color_point import color_point
from add_water import rain_water, add_water

def drain_water(water_grid, water, grid, size):
    water_grid[(size ** 2) / 2 - size / 2][2] -= 0.1

def distribute_water(water_grid, drain, water, grid, size):
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

def reset_flood(water_vdata):
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

def handle_flood(flood_type, water_vdata, water, grid, size):
    vertex = GeomVertexReader(water_vdata, 'vertex')
    vwrite = GeomVertexWriter(water_vdata, 'vertex')
    cwrite = GeomVertexWriter(water_vdata, 'color')
    water_grid = []
    while not vertex.isAtEnd():
        v = vertex.getData3f()
        water_grid.append([v[0], v[1], v[2]])
    if flood_type == 0:
        rain_water(water_grid, water, grid, size)
        distribute_water(water_grid, 0, water, grid, size)
    if flood_type == 1:
        add_water(water_grid, water, grid, size)
        distribute_water(water_grid, 0, water, grid, size)
    if flood_type == '-':
        drain_water(water_grid)
        distribute_water(water_grid, 1, water, grid, size)
    for v in water_grid:
        vwrite.setData3f(v[0], v[1], v[2])
        if (v[2] > 0):
            cwrite.addData4f(0, 0, 0.8, 1)
        else:
            cwrite.addData4f(0, 0, 0.8, 0)

class InputHandler(DirectObject):
    def __init__(self, water_vdata, water, grid, size):
        self.water_vdata = water_vdata
        self.water = water
        self.grid = grid
        self.size = size
        self.floodInterval = None
        self.accept("1", self.rain)
        self.accept("2", self.flood)
        self.accept("0", self.stop)
        self.accept("-", self.drain)
        self.accept("escape", sys.exit)

    def rain(self):
        self.stop()
        self.floodInterval = Func(handle_flood, 0, self.water_vdata, self.water, self.grid, self.size)
        self.floodInterval.start()
        self.floodInterval.loop()

    def flood(self):
        self.stop()
        self.floodInterval = Func(handle_flood, 1, self.water_vdata, self.water, self.grid, self.size)
        self.floodInterval.start()
        self.floodInterval.loop()

    def stop(self):
        if self.floodInterval:
            self.floodInterval.finish()
        reset_flood(self.water_vdata)

    def drain(self):
        if self.floodInterval:
            self.floodInterval.finish()
        self.floodInterval = Func(handle_flood, '-', self.water_vdata, self.water, self.grid, self.size)
        self.floodInterval.start()
        self.floodInterval.loop()

def main(inputfile):
    size = 50
    base = ShowBase()
    snode = GeomNode('land')
    grid = gen_grid(size, parse_file(inputfile))
    add_border(size, grid)
    snode.addGeom(land_from_grid(grid, size + 4))
    land = render.attachNewNode(snode)
    land.setScale(1.02)

    snode = GeomNode('water')
    water_vdata = None
    water_vdata, geom = gen_water(size)
    snode.addGeom(geom)
    water = render.attachNewNode(snode)
    water.setTransparency(TransparencyAttrib.MAlpha)
    water.setAlphaScale(0.9)
    water.setTwoSided(True)
    land.setTwoSided(True)
    t = InputHandler(water_vdata, water, grid, size)
    base.trackball.node().setPos(0, 20, -0.5)
    inputsDisplay = OnscreenText(text="1: Rain\n2: Flood\n0: Reset\n-: Drain",
                               style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.08),
                               align=TextNode.ALeft, scale=.05,
                               parent=base.a2dTopLeft)
    base.run()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        print main(sys.argv[1])
    else:
        print "usage: %s [input file]" % sys.argv[0]
