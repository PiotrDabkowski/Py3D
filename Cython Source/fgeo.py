import colorsys
from libc.math cimport sin as csin
from libc.math cimport cos as ccos


cdef class Vector:
    cdef public double x
    cdef public double y
    cdef public double z
    def __init__(self, vx, vy, vz):
        self.x = vx
        self.y = vy    
        self.z = vz
    
    cpdef coords(self):
        return self.x, self.y, self.z
    
    cpdef sub(self, other):
        return Vector(self.x-other.x, self.y-other.y, self.z-other.z)
    
    cpdef add(self, other):
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)
        
    cpdef mul(self, double con):
        return Vector(self.x*con, self.y*con, self.z*con)
        
    cpdef smul(self, other):
        return self.x*other.x+self.y*other.y+self.z*other.z
    
    cpdef vmul(self, other):
        return Vector(self.y*other.z-self.z*other.y, self.z*other.x-self.x*other.z, self.x*other.y-self.y*other.x)
    
    cpdef double len(self):
        return (self.x*self.x+self.y*self.y+self.z*self.z)**0.5
    
    cpdef unit(self):
        cdef double l = (self.x*self.x+self.y*self.y+self.z*self.z)**0.5
        return Vector(self.x/l, self.y/l, self.z/l)
    
    cpdef make_unit(self):
        cdef double l = (self.x*self.x+self.y*self.y+self.z*self.z)**0.5
        self.x = self.x/l
        self.y = self.y/l
        self.z = self.z/l
        
    cpdef move(self, v):
        self.x = self.x + v.x
        self.y = self.y + v.y
        self.z = self.z + v.z
    
    
    cpdef rotated(self, pvec, dvec, double angle):
        dvec.make_unit()
        closest_point_on_the_line = pvec.add(dvec.mul(dvec.smul((self.sub(pvec)))))
        perp = self.sub(closest_point_on_the_line)
        new_perp = perp.mul(ccos(angle))
        tang = perp.vmul(dvec)
        new_tang = tang.mul(csin(angle))
        return closest_point_on_the_line.add(new_perp).add(new_tang)
    
    cpdef rotate(self, pvec, dvec, double angle):
        dvec.make_unit()
        closest_point_on_the_line = pvec.add(dvec.mul(dvec.smul((self.sub(pvec)))))
        perp = self.sub(closest_point_on_the_line)
        new_perp = perp.mul(ccos(angle))
        tang = perp.vmul(dvec)
        new_tang = tang.mul(csin(angle))
        t = closest_point_on_the_line.add(new_perp).add(new_tang)
        self.x = t.x
        self.y = t.y
        self.z = t.z
        
cdef class Plane:
    #Has to be fast :(
    cdef public double ax
    cdef public double ay
    cdef public double az
    
    cdef public double bx
    cdef public double by
    cdef public double bz
    
    cdef public double cx
    cdef public double cy
    cdef public double cz
    
    cdef public double dx
    cdef public double dy
    cdef public double dz
    
    cdef public double dis
    
    cdef public float ch
    cdef public float cs
    cdef public float cv
    
    def __init__(self, V1, V2, V3):
        self.ax = V1.x
        self.ay = V1.y
        self.az = V1.z
        
        self.bx = V2.x
        self.by = V2.y
        self.bz = V2.z
        
        self.cx = V3.x
        self.cy = V3.y
        self.cz = V3.z
        
        d = V3.sub(V1).vmul(V3.sub(V2))
        d.make_unit()
        self.dx = d.x
        self.dy = d.y
        self.dz = d.z
        
        self.dis = d.smul(V1)
        self.set_color((0,250,0))
    
    cpdef is_visible(self, pvec):
         if self.dx*(pvec.x-self.ax)+self.dy*(pvec.y-self.ay)+self.dz*(pvec.z-self.az)<=0:
             return 1
         return 0

    cpdef points(self):
       return ((self.ax, self.ay, self.az), (self.bx, self.by, self.bz), (self.cx, self.cy, self.cz))
    
    cpdef reverse(self):
        self.dis = -self.dis
        self.dx = -self.dx
        self.dy = -self.dy
        self.dz = -self.dz
    
    cpdef set_color(self, color):
        '''Sets the color of the plane to color. Must be in rgb. Eg: (255, 255, 255) is white.'''
        r = colorsys.rgb_to_hsv(color[0]/255.0,color[1]/255.0,color[2]/255.0)
        self.ch = r[0]
        self.cs = r[1]
        self.cv = r[2]
    
    def get_color(self, light_dir):
        '''Returns the rgb color of the plane when light is shone from light dir'''
        
        return tuple([int(round(e*255)) for e in colorsys.hsv_to_rgb(self.ch,self.cs,self.cv*abs(self.dx*light_dir.x+self.dy*light_dir.y+self.dz*light_dir.z))])
        
    #is_visible
    #reverse
    #intersection_with_line (needed later)
    #set_color
    #get_color
