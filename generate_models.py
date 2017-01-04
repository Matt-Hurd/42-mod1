from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import Geom
from panda3d.core import GeomVertexWriter
from panda3d.core import LVector3
from panda3d.core import GeomTriangles
from color_point import color_point

def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec

def gen_water(size):
    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData('water', format, Geom.UHDynamic)
    v = vdata
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    for y in range(size):
        for x in range(size):
            fx = float(x) / size * 5 - 2.5
            fy = float(y) / size * 5 - 2.5
            if y == 0 or x == 0 or y == size - 1 or x == size - 1:
                if x == 0:
                    fx = 1.0 / size * 5 - 2.5
                if x == size - 1:
                    fx = float(size - 2) / size * 5 - 2.5
                if y == 0:
                    fy = 1.0 / size * 5 - 2.5
                if y == size - 1:
                    fy = float(size - 2) / size * 5 - 2.5
                z = -1.0
                color.addData4f(0, 0, 0.8, 1)
            else:
                z = -0.1
                color.addData4f(0, 0, 0.8, 1)
            vertex.addData3(fx, fy, z)
            normal.addData3(normalized(2 * fx - 1, 2 * fy - 1, 2 * z - 1))
    tris = GeomTriangles(Geom.UHDynamic)

    for y in range(size):
        for x in range(size):
            if (y < size - 1 and x < size - 1):
                tris.addVertices(x + y * size, x + y * size + 1, x + (y + 1) * size)
            if (y > 0 and x > 0):
                tris.addVertices(x + y * size, x + y * size - 1, x + (y - 1) * size)


    land = Geom(vdata)
    land.addPrimitive(tris)
    return (vdata, land)

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
