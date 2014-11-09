import fgeo
from scipy.spatial import ConvexHull as sciConvexHull
from itertools import combinations, izip
from math import pi
from sorting import *

class ConvexHull:
    def __init__(self, vertices):
        self.vertices = vertices #reduce them!
        scich=sciConvexHull([v.coords() for v in vertices])
        self.faces = [[self.vertices[i] for i in f] for f in scich.simplices]
        self._recalculate_planes()
        for f, p in izip(self.faces, self.planes):
            for v in self.vertices:
                if v not in f:
                    break
            if p.is_visible(v):
                f.reverse()
        self._recalculate_planes()

    def _recalculate_planes(self):
        self.planes = [fgeo.Plane(*f) for f in self.faces]
        if hasattr(self, '_color'):
            for p in self.planes:
                p.set_color(self._color)
                
    def move(self, vec):
        for v in self.vertices:
            v.move(vec)
        self._recalculate_planes()

    def set_color(self, color):
        self._color = color
        self._recalculate_planes()
        

    def rotate(self, pvec, dvec, angle):
        for v in self.vertices:
            v.rotate(pvec, dvec, angle)
        self._recalculate_planes()


def separating_plane(ch1, ch2):
    for i, p  in enumerate(ch1.planes):
        for v in ch2.vertices:
            if not p.is_visible(v):
                break
        else:
            return 0, i
    for i, p in enumerate(ch2.planes):
        for v in ch1.vertices:
            if not p.is_visible(v):
                break
        else:
            return 1, i
    raise Exception('Hulls seem to intersect!')


    
class Polyhedron:
    def __init__(self, convex_hulls):
        self.convex_hulls = convex_hulls
        self.seps = {}
        for a, b in combinations(self.convex_hulls, 2):
            ob, i = separating_plane(a, b)
            if ob:
                self.seps[a,b] = b, i
                self.seps[b,a] = b, i
            else:
                self.seps[a,b] = a, i
                self.seps[b,a] = a, i

    def move(self, vec):
        for c in self.convex_hulls:
            c.move(vec)
        self._recalculate_seps()

    def rotate(self, line, angle):
        pass

    def set_color(self, color):
        for c in self.convex_hulls:
            c.set_color(color)
            
    def _is_greater(self, c1, c2):
        ch, i = self.seps[c1,c2]
        if ch.planes[i].is_visible(self._point):
            if ch is c1:
                return False
            return True
        else:
            if ch is c1:
                return True
            return False
        
    def return_sorted(self, point):
        '''point is a view point'''
        self._point = point
        return msort(self.convex_hulls, is_greater=self._is_greater)
        
def sphere(radius, num=21):
    vs = []
    p = fgeo.Vector(radius,0,0)
    step = 2*pi/num
    y = fgeo.Vector(0,0,0), fgeo.Vector(0,1,0)
    z = fgeo.Vector(0,0,0), fgeo.Vector(0,0,1)
    for n in xrange(1, (num-1)/2):
         pd = p.rotated(y[0], y[1], step*n)
         for s in xrange(num):
             vs.append(pd.rotated(z[0], z[1], step*s))
    for n in xrange(1, (num-1)/2):
         pd = p.rotated(y[0], y[1], -step*n)
         for s in xrange(num):
             vs.append(pd.rotated(z[0], z[1], step*s))
    for n in xrange(num):
        vs.append(p.rotated(z[0], z[1], step*n))
    vs.append(p.rotated(y[0],y[1], pi/2))
    vs.append(p.rotated(y[0], y[1], -pi/2))
    return ConvexHull(vs)
     
    
    
def cuboid(x,y,z):
    vs = [fgeo.Vector(0,0,0), 
            fgeo.Vector(x,0,0), fgeo.Vector(0,y,0), fgeo.Vector(0,0,z),
            fgeo.Vector(x,0,z), fgeo.Vector(x,y,0), fgeo.Vector(0,y,z),
            fgeo.Vector(x,y,z)]
    return ConvexHull(vs)
 

class World:
    def __init__(self, polys):
        self.polys = polys
        
    def _is_greater(self, c1, c2):
        r, nr = separating_plane(c1, c2)
        if not r:
            if c1.planes[nr].is_visible(self._point):
                return False
            return True
        if c2.planes[nr].is_visible(self._point):
            return True
        return False
            
    def get_draw_order(self, point):
        self._point = point
        return sort_groups([poly.return_sorted(point) for poly in self.polys], is_greater=self._is_greater)
       

    
import random
def ranp(n, xr=1.5, yr=1.5, zr=1.5):
    return [fgeo.Vector(xr*(random.random()-0.5), yr*(random.random()-0.5), yr*(random.random()-0.5)) for e in xrange(n)]


