import math
from scipy.spatial import ConvexHull as sciConvexHull
import colorsys
from itertools import izip

'''




 |_ Axes: X Horizontal to the right
  \       Y Vertical top
          Z Horizontal towards us

'''

TOLERANCE = 0.0001




class Point:
    def __init__(self, x, y ,z):
        self._coords = x, y, z

    def __cmp__(self, other):
        if (abs(self._coords[0]-other._coords[0])<=TOLERANCE and
            abs(self._coords[1]-other._coords[1])<=TOLERANCE and
            abs(self._coords[2]-other._coords[2])<=TOLERANCE):
            return 0
        return 1
    
    def __add__(self, other):
        if isinstance(other, Vector):
            return Point(self._coords[0]+other._vec[0],
                         self._coords[1]+other._vec[1],
                         self._coords[2]+other._vec[2])
        else:
            raise TypeError('unsupported operand type(s) for +: %s and %s'%(self.__class__.__name__, other.__class__.__name__))
                            
    def __sub__(self, other):
        '''Supports translation by a vector or calculating pos difference between points. Returns a NEW object'''
        if isinstance(other, Vector):
            return Point(self._coords[0]-other._vec[0],
                         self._coords[1]-other._vec[1],
                         self._coords[2]-other._vec[2])
        elif isinstance(other, Point):
            return Vector(self._coords[0]-other._coords[0],
                          self._coords[1]-other._coords[1],
                          self._coords[2]-other._coords[2])
        else:
            raise TypeError('unsupported operand type(s) for -: %s and %s'%(self.__class__.__name__, other.__class__.__name__))

    def __str__(self):
        return 'Point(%.2f, %.2f, %.2f)'%tuple(self._coords)

    def __repr__(self):
        return self.__str__()

    def move(self, vector):
        '''Moves this point by the given vector, returns None'''
        self._coords = (self._coords[0]+vector._vec[0],
                        self._coords[1]+vector._vec[1],
                        self._coords[2]+vector._vec[2])

    def rotate(self, line, angle):
        '''rotates this point about the line by the given angle'''
        velf = self.vector()
        closest_point_on_the_line = (line._direction*velf)*line._direction+line._start
        perp = velf-closest_point_on_the_line
        new_perp = math.cos(angle)*perp
        tang = perp%line._direction
        new_tang = math.sin(angle)*tang
        return closest_point_on_the_line.point()+new_perp+new_tang
        

    def vector(self):
        '''converts point to vector'''
        return Vector(*self._coords)

    def distance(self, point):
        '''Calculates distance from self to other Point'''
        return ((self._coords[0]-point._coords[0])**2+(self._coords[1]-point._coords[1])**2+(self._coords[2]-point._coords[2])**2)**0.5


            
class Vector:
    def __init__(self, x, y, z):
        self._vec = x, y, z
        self._len = None

    def __cmp__(self, other):
        if (abs(self._vec[0]-other._vec[0])<=TOLERANCE and
            abs(self._vec[1]-other._vec[1])<=TOLERANCE and
            abs(self._vec[2]-other._vec[2])<=TOLERANCE):
            return 0
        return 1
            
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self._vec[0]+other._vec[0],
                          self._vec[1]+other._vec[1],
                          self._vec[2]+other._vec[2])
        elif isinstance(other, Point):
            return other.__add__(self)
        else:
            raise TypeError('unsupported operand type(s) for +: %s and %s'%(self.__class__.__name__, other.__class__.__name__))

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self._vec[0]-other._vec[0],
                          self._vec[1]-other._vec[1],
                          self._vec[2]-other._vec[2])
        else:
            raise TypeError('unsupported operand type(s) for -: %s and %s'%(self.__class__.__name__, other.__class__.__name__))

    def point(self):
        return Point(*self._vec)

    def is_along(self, other):
        try:
            if abs(self.__mod__(other).len())<TOLERANCE:
                return True
        except ZeroDivisionError:
            return True
        return False
        
    def len(self):
        '''returns length of the vector'''
        if self._len is None:
            self._len = float((self._vec[0]**2+self._vec[1]**2+self._vec[2]**2)**0.5)
        return self._len

    def unit(self):
        '''Returns unit vector of this vector'''
        l = self.len()
        return Vector(self._vec[0]/l,
                      self._vec[1]/l,
                      self._vec[2]/l)

    def angle(self, other):
        '''Angle between 2 vectors in radians'''
        return math.acos((self*other)/(self.len()*other.len()))

    def reverse(self):
        self._vec = -self._vec[0], -self._vec[1], -self._vec[2]

    def __neg__(self):
        return -1*self
    
    def __mul__(self, other):
        '''DOT product! Or scalar product!'''
        if isinstance(other, Vector):
            return self._vec[0]*other._vec[0]+self._vec[1]*other._vec[1]+self._vec[2]*other._vec[2]
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, long):
            return Vector(other*self._vec[0],
                          other*self._vec[1],
                          other*self._vec[2])
    def __rmul__(self, other):
        return self.__mul__(other)

    def __mod__(self, other):
        '''VECTOR product!'''
        return Vector(self._vec[1]*other._vec[2]-self._vec[2]*other._vec[1],
                      self._vec[2]*other._vec[0]-self._vec[0]*other._vec[2],
                      self._vec[0]*other._vec[1]-self._vec[1]*other._vec[0])
        
    def __str__(self):
        return 'Vector(%.2f, %.2f, %.2f)'%tuple(self._vec)

    def __repr__(self):
        return self.__str__()

AXES = Vector(1,0,0), Vector(0,1,0), Vector(0,0,1)


class Line:
    def __init__(self, start, direction):
        self._direction = direction.unit()
        self._start = start.vector() - (self._direction*start.vector())*self._direction

    def _ray_plane_distance(self, other):
        nom = (other._dis-self._start*other._direction)
        if abs(nom)<TOLERANCE:
            return 0
        denom = self._direction*other._direction
        if abs(denom)<TOLERANCE:
            return None
        return nom/float(denom)

    def closest_point(self, point):
        '''Returns a position vector of the point on the line that is closest to the given point'''
        return ((self._direction*point.vector())*self._direction+self._start)#.point()
        
    def __and__(self, other):
        '''Returns intersection with other object (Point, Line or Plane)
          Intersection can be a Point, Line or None.'''
        if isinstance(other, Plane):
            dis = self._ray_plane_distance(other)
            if dis is None:
                return None
            if not dis and abs(self._direction*other._direction)<TOLERANCE:
                return self
            return (self._start+dis*self._direction).point()
        elif isinstance(other, Point):
            if self._direction.is_along(other.vector()-self._start): #Vector product must be 0!
                return other
            return None
        elif isinstance(other, Line):
            raise NotImplemented('')
        else:
            raise TypeError('unsupported operand type(s) for &: %s and %s'%(self.__class__.__name__, other.__class__.__name__))

    def __str__(self):
        return 'Line(%s, %s)'%(str(self._start.point()), str(self._direction))

    def __repr__(self):
        return str(self)
        
        


class Plane:
    def __init__(self, *args):
        '''Init with 3 points 2 lines or Direction vector and a point.
        Note: When you look at the visible plane you must give the points in the counter clockwise direction.
              Otherwise is_visible will not work!
        '''
        if len(args)==2:
            if isinstance(args[0], Line) and isinstance(args[1], Line):
                raise NotImplementedError
            elif isinstance(args[0], Point) and isinstance(args[1], Vector):
                a1 = args[1].unit()
                self._dis, self._direction = args[0].vector()*a1, a1
                self._p= args[0]
            elif isinstance(args[0], Vector) and isinstance(args[1], Point):
                a0 = args[0].unit()
                self._dis, self._direction = args[1].vector()*a0, a0
                self._p = args[1]
            else:
                raise TypeError('Invalid input args!')
            
        elif len(args)>=3 and all([isinstance(a, Point) for a in args]):
            try:
                self._direction = ((args[2]-args[1])%(args[1]-args[0])).unit()
            except ZeroDivisionError:
                raise ValueError('There is no unique plane for this combination of points! (They lie on a single line)')
            self._dis = self._direction*args[0].vector()
            self._closest_axis = self._find_closest_axis()
            self._relevant_coords = tuple([e for e in xrange(3) if e!=self._closest_axis])
            self._b = args # Points forming a boundary
            self._xyb = tuple([(e._coords[self._relevant_coords[0]], e._coords[self._relevant_coords[1]]) for e in args]) #Boundary in xy coords only
            self._p = args[1] #Point on the plane
        else:
            raise TypeError('Invalid input args!')

    def _find_closest_axis(self):
        m = -10
        for i, e in enumerate(AXES):
            cand = e*self._direction
            if cand>m:
                m = cand
                winner = i
        return winner

    def is_inboundary(self, point):
        '''We assume that the point is on the plane'''
        point = point[self._relevant_coords[0]], point[self._relevant_coords[1]]
        return is_inpoly(point, self._xyb)

    def is_crossing(self, line):
        '''returns True if the line crosses the plane through the region in the boundary _b
           False otherwise. Plane has to be created with a list of points!'''
        cross = line.__and__(self)
        if isinstance(cross, Point) and self.is_inboundary(cross):
            return cross
        return False        
                
    def __and__(self, other):
        '''Returns intersection with other object (Point, Line or Plane)
          Intersection can be a Point, Line or None.'''
        if isinstance(other, Plane):  #has to be fast!!!!
            line_dir = self._direction%other._direction
            if abs(line_dir.len())<TOLERANCE:
                if abs(self._dis-other._dis)<TOLERANCE:
                    return self
                return None
            #Calculating common point.... quite tricky!
            if self._closest_axis==0:
                if other._closest_axis==1: # Cant be 0 and 1
                    sx, sy = 0,1
                else:  # 1 is safe maybe 2.
                    sx, sy = 0,2
            elif self._closest_axis==1:
                if other._closest_axis==0: # Must be 2
                    sx, sy = 0,1
                else: # 0
                    sx, sy = 1,2
            else:
                if other._closest_axis==0: # Must be 1
                    sx, sy = 0,2
                else: #0
                    sx, sy = 1,2
            p = [0,0,0]
            svx, svy = self._direction._vec[sx], self._direction._vec[sy]
            ovx, ovy = other._direction._vec[sx], other._direction._vec[sy]
            det = float(svx*ovy - svy*ovx)
            p[sx] = (ovy*self._dis-svy*other._dis)/det
            p[sy] = (-ovx*self._dis+svx*other._dis)/det
            return (Point(*p), line_dir)
        elif isinstance(other, Point):
            if abs(other.vector()*self._direction-self._dis)<TOLERANCE: 
                return other
            return None
        elif isinstance(other, Line):
            return other.__add__(self)
        else:
            raise TypeError('unsupported operand type(s) for &: %s and %s'%(self.__class__.__name__, other.__class__.__name__))

    def reverse(self):
        '''Reverses the perpendicular direction vector'''
        self._dis, self._direction = -self._dis, -1*self._direction

    def is_visible(self, point):
        if (point-self._p)*self._direction<0:
            return True
        return False

    def set_color(self, color):
        '''Sets the color of the plane to color. Must be in rgb. Eg: (255, 255, 255) is white.'''
        self.color = colorsys.rgb_to_hsv(color[0]/255.0,color[1]/255.0,color[2]/255.0)
    
    def get_color(self, light_dir):
        '''Returns the rgb color of the plane when light is shone from light dir'''
        return [int(round(e*255)) for e in colorsys.hsv_to_rgb(self.color[0],self.color[1],self.color[2]*abs(self._direction*light_dir))]
    
    def __str__(self):
        def changer(x):
            if abs(x[0])<TOLERANCE:
                return ''
            elif x[0]==1:
                return ' + '+x[1]
            elif x[0]==-1:
                return ' - '+x[1]
            elif x[0]>0:
                return ' + %.2f%s'%x
            return ' - %.2f%s'%(abs(x[0]),x[1])
        c =  ''.join([changer(i) for i in zip(self._direction._vec, ['X','Y','Z'])]).strip('+- ')
        c+=' = %.2f'%self._dis
        return c
    
    def __repr__(self):
        return self.__str__()
    

def is_inpoly(xy, poly):
    x, y = xy
    n = len(poly)
    inside =False
    p1x,p1y = poly[0]
    for i in xrange(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside




class ConvexHull:
    def __init__(self, vertices):
        self.vertices = vertices
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
    
    
        


import random
def ranp(n, xr=450, yr=300):
    return [Point(xr*(random.random()-0.5), yr*(random.random()-0.5), yr*(random.random()-0.5)) for e in xrange(n)]




c = ConvexHull(ranp(20))

































                







                
                










                
