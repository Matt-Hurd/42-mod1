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
from add_water import rain_water, add_water, fill_edges

def drain_water(water_grid, water, grid, size):
    for y in range(1, size - 1):
        for x in range(1, size - 1):
            water_grid[y * size + x][2] -= 0.001

def distribute_water(water_grid, drain, water, grid, size):
    for y in range(1, size - 1):
        for x in range(1, size - 1):
            pos = y * size + x
            if water_grid[pos][2] >= grid[y][x]:
                if x < size - 2:
                    if water_grid[pos][2] > water_grid[pos + 1][2]:
                        t = (water_grid[pos][2] - water_grid[pos + 1][2]) / 2
                        water_grid[pos + 1][2] += t
                        water_grid[pos][2] -= t
                    elif water_grid[pos][2] < water_grid[pos + 1][2]:
                        t = (water_grid[pos + 1][2] - water_grid[pos][2]) / 2
                        water_grid[pos][2] += t
                        water_grid[pos + 1][2] -= t
                if y < size - 2:
                    if water_grid[pos][2] > water_grid[pos + size][2]:
                        t = (water_grid[pos][2] - water_grid[pos + size][2]) / 2
                        water_grid[pos + size][2] += t
                        water_grid[pos][2] -= t
                    elif water_grid[pos][2] < water_grid[pos + size][2]:
                        t = (water_grid[pos + size][2] - water_grid[pos][2]) / 2
                        water_grid[pos][2] += t
                        water_grid[pos + size][2] -= t
                if x > 1:
                    if water_grid[pos][2] > water_grid[pos - 1][2]:
                        t = (water_grid[pos][2] - water_grid[pos - 1][2]) / 2
                        water_grid[pos - 1][2] += t
                        water_grid[pos][2] -= t
                    elif water_grid[pos][2] < water_grid[pos - 1][2]:
                        t = (water_grid[pos - 1][2] - water_grid[pos][2]) / 2
                        water_grid[pos][2] += t
                        water_grid[pos - 1][2] -= t
                if y > 1:
                    if water_grid[pos][2] > water_grid[pos - size][2]:
                        t = (water_grid[pos][2] - water_grid[pos - size][2]) / 2
                        water_grid[pos - size][2] += t
                        water_grid[pos][2] -= t
                    elif water_grid[pos][2] < water_grid[pos - size][2]:
                        t = (water_grid[pos - size][2] - water_grid[pos][2]) / 2
                        water_grid[pos][2] += t
                        water_grid[pos - size][2] -= t

def reset_flood(water_vdata, grid, size):
    vertex = GeomVertexReader(water_vdata, 'vertex')
    vwrite = GeomVertexWriter(water_vdata, 'vertex')
    cwrite = GeomVertexWriter(water_vdata, 'color')
    water_grid = []
    pos = 0
    while not vertex.isAtEnd():
        v = vertex.getData3f()
        water_grid.append([v[0], v[1], v[2]])
    for v in water_grid:
        if pos < size or pos / size >= size - 1 or pos % size == 0 or pos % size == size - 1:
            vwrite.setData3f(v[0], v[1], -0.1)
        else:
            vwrite.setData3f(v[0], v[1], grid[pos / size][pos % size] - 0.01)
        cwrite.addData4f(0, 0, 0.8, 0)
        pos += 1

def handle_flood(flood_type, water_vdata, water, grid, size, rate):
    vertex = GeomVertexReader(water_vdata, 'vertex')
    vwrite = GeomVertexWriter(water_vdata, 'vertex')
    cwrite = GeomVertexWriter(water_vdata, 'color')
    water_grid = []
    while not vertex.isAtEnd():
        v = vertex.getData3f()
        water_grid.append([v[0], v[1], v[2]])
    if flood_type == 0:
        rain_water(water_grid, water, grid, size, rate)
    if flood_type == 1:
        add_water(water_grid, water, grid, size, rate)
    if flood_type == 2:
        fill_edges(water_grid, water, grid, size, rate)
    if flood_type == '-':
        drain_water(water_grid, water, grid, size)
    distribute_water(water_grid, 0, water, grid, size)
    pos = 0
    for v in water_grid:
        vwrite.setData3f(v[0], v[1], v[2])
        depth = max(1.0 - float(v[2] - grid[pos / size][pos % size]) * 40, 0)
        cwrite.addData4f(depth, depth, 0.8 + depth, 0.8 if v[2] >= -1 else 0)
        pos += 1

class InputHandler(DirectObject):
    def __init__(self, water_vdata, water, grid, size):
        self.water_vdata = water_vdata
        self.water = water
        self.grid = grid
        self.size = size
        self.floodInterval = None
        self.rate = 1
        self.accept("1", self.rain)
        self.accept("2", self.flood)
        self.accept("3", self.edges)
        self.accept("0", self.stop)
        self.accept("-", self.drain)
        self.accept("q", self.modify_rate, [0.2])
        self.accept("w", self.modify_rate, [-0.2])
        self.accept("escape", sys.exit)

    def modify_rate(self, value):
        self.rate += value

    def rain(self):
        self.stop()
        self.floodInterval = Func(handle_flood, 0, self.water_vdata, self.water, self.grid, self.size, self.rate)
        self.floodInterval.start()
        self.floodInterval.loop()

    def flood(self):
        self.stop()
        self.floodInterval = Func(handle_flood, 1, self.water_vdata, self.water, self.grid, self.size, self.rate)
        self.floodInterval.start()
        self.floodInterval.loop()

    def edges(self):
        self.stop()
        self.floodInterval = Func(handle_flood, 2, self.water_vdata, self.water, self.grid, self.size, self.rate)
        self.floodInterval.start()
        self.floodInterval.loop()

    def stop(self):
        if self.floodInterval:
            self.floodInterval.finish()
        reset_flood(self.water_vdata, self.grid, self.size)

    def drain(self):
        if self.floodInterval:
            self.floodInterval.finish()
        self.floodInterval = Func(handle_flood, '-', self.water_vdata, self.water, self.grid, self.size, self.rate)
        self.floodInterval.start()
        self.floodInterval.loop()

def main(inputfile):
    size = 100
    base = ShowBase()
    snode = GeomNode('land')
    grid = gen_grid(size, parse_file(inputfile))
    add_border(size, grid)
    size += 4
    snode.addGeom(land_from_grid(grid, size))
    land = render.attachNewNode(snode)
    # land.setScale(1.02)

    snode = GeomNode('water')
    water_vdata = None
    water_vdata, geom = gen_water(size)
    snode.addGeom(geom)
    water = render.attachNewNode(snode)
    water.setTransparency(TransparencyAttrib.MAlpha)
    # water.setAlphaScale(0.9)
    water.setTwoSided(True)
    land.setTwoSided(True)
    t = InputHandler(water_vdata, water, grid, size)
    base.trackball.node().setPos(0, 20, -0.5)
    inputsDisplay = OnscreenText(text="1: Rain\n2: Wave\n3: Edges\n0: Reset\n-: Drain\nq: Increase Rate\nw: Decrease Rate",
                               style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.08),
                               align=TextNode.ALeft, scale=.05,
                               parent=base.a2dTopLeft)
    base.run()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        print main(sys.argv[1])
    else:
        print "usage: %s [input file]" % sys.argv[0]
