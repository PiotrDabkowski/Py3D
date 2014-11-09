from geometry import *
from scipy.spatial import ConvexHull as sciConvexHull
from itertools import combinations
from math import pi

class ConvexHull:
    def __init__(self, vertices):
        self.vertices = vertices #reduce them!
        scich=sciConvexHull([v._coords for v in vertices])
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
        self.planes = [Plane(*f) for f in self.faces]
        
    def move(self, vec):
        for v in self.vertices:
            v.move(vec)
        self._recalculate_planes()

    def rotate(self, line, angle):
        for v in self.vertices:
            v.rotate(line, angle)
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

def sort_sorted(a, b, is_greater):
    res = []
    i, j = 0, 0
    while i<len(a) and j<len(b):
        if is_greater(a[i], b[j]):
            res.append(b[j])
            j+=1
        else:
            res.append(a[i])
            i+=1
    return res+a[i:]+b[j:]
    
def sort_groups(x, is_greater):
    while len(x)>1:
        s = [x[n:n+2] for n in xrange(0, len(x), 2)]
        n=0
        while n<len(s):
            if len(s[n])>1:
                s[n] = sort_sorted(s[n][0], s[n][1], is_greater)
            else:
                s[n] = s[n][0]
            n+=1
        x = s
    return x[0]


def msort(x, is_greater=lambda a,b: a>b):
    s = [x[n:n+2] for n in xrange(0, len(x), 2)]
    for e in s:
        if len(e)>1 and not is_greater(e[1], e[0]):
            e.reverse()
    return sort_groups(s, is_greater)
    
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
    p = Point(radius,0,0)
    step = 2*pi/num
    y = Line(Point(0,0,0), Vector(0,1,0))
    z = Line(Point(0,0,0), Vector(0,0,1))
    for n in xrange(1, (num-1)/2):
         pd = p.rotate(y, step*n)
         for s in xrange(num):
             vs.append(pd.rotate(z, step*s))
    for n in xrange(1, (num-1)/2):
         pd = p.rotate(y, -step*n)
         for s in xrange(num):
             vs.append(pd.rotate(z, step*s))
    for n in xrange(num):
        vs.append(p.rotate(z, step*n))
    vs.append(p.rotate(y, pi/2))
    vs.append(p.rotate(y, -pi/2))
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
    return [Point(xr*(random.random()-0.5), yr*(random.random()-0.5), yr*(random.random()-0.5)) for e in xrange(n)]


