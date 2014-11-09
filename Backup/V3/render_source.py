#Contains Fast render Vector and Plane written in Cython
cimport cython
from libc.stdlib cimport malloc, free
from libc.math cimport acos as cacos
from libc.math cimport abs as cabs
from libc.math cimport tan as ctan
from libc.math cimport sin as csin
from libc.math cimport cos as ccos
from libc.math cimport atan as catan

cdef double TOLERANCE = 0.00001
cdef double pi = 3.14159265

def acos(x):
    if 1<cabs(x)<1+TOLERANCE:
        return pi if x<0 else 0
    elif cabs(x)<=1:
        return cacos(x)
    raise ValueError('Invalid input for acos')



cdef double *xpos
xpos = <double *>malloc(3*cython.sizeof(double))
if xpos is NULL:
    raise MemoryError()
            
cdef double *coef_and_lim_ang
coef_and_lim_ang = <double *>malloc(3*cython.sizeof(double))
if coef_and_lim_ang is NULL:
   raise MemoryError()
   
cdef double *look_dir
look_dir = <double *>malloc(3*cython.sizeof(double))
if look_dir is NULL:
   raise MemoryError()
            
cdef double *up_dir
up_dir = <double *>malloc(3*cython.sizeof(double))
if up_dir is NULL:
   raise MemoryError()
    
cdef double *right_dir
right_dir = <double *>malloc(3*cython.sizeof(double))
if right_dir is NULL:
   raise MemoryError()
            

    
cdef double *xvec
xvec = <double *>malloc(3*cython.sizeof(double))
if xvec is NULL:
    raise MemoryError()
    
cdef double *rot_vec
rot_vec = <double *>malloc(3*cython.sizeof(double))
if rot_vec is NULL:
     raise MemoryError()
        
def ini(glook_dir=(1,1,1), gup_dir=(0,1,0), ghor_range=pi/3, gver_range=pi/6, ghor_len=500, gpos=(-3,3,-3)):
        '''Bottom left edge is 0'''
        glook_dir =  -gpos[0], -gpos[1], -gpos[2]
        #pos
        xpos[0] = gpos[0]
        xpos[1] = gpos[1]
        xpos[2] = gpos[2]
        #coef
        coef_and_lim_ang[0] = ghor_len/(ctan(ghor_range))
        #look_dir
        cdef double look_dir_len = (glook_dir[0]**2+glook_dir[1]**2+glook_dir[2]**2)**0.5
        look_dir[0] =  glook_dir[0]/look_dir_len
        look_dir[1] =  glook_dir[1]/look_dir_len
        look_dir[2] =  glook_dir[2]/look_dir_len
        #up_dir
        cdef double normalizer = (look_dir[0]*gup_dir[0]+look_dir[1]*gup_dir[1]+look_dir[2]*gup_dir[2])
        gup_dir = gup_dir[0] - normalizer*look_dir[0], gup_dir[1] - normalizer*look_dir[1], gup_dir[2] - normalizer*look_dir[2]
        cdef double gup_dir_len = (gup_dir[0]**2+gup_dir[1]**2+gup_dir[2]**2)**0.5
        up_dir[0] = gup_dir[0]/gup_dir_len
        up_dir[1] = gup_dir[1]/gup_dir_len
        up_dir[2] = gup_dir[2]/gup_dir_len
        #right_dir
        gright_dir =  (look_dir[1]*up_dir[2]-look_dir[2]*up_dir[1],
                      look_dir[2]*up_dir[0]-look_dir[0]*up_dir[2],
                      look_dir[0]*up_dir[1]-look_dir[1]*up_dir[0])
        cdef double gright_dir_len = (gright_dir[0]**2+gright_dir[1]**2+gright_dir[2]**2)**0.5
        right_dir[0] = gright_dir[0]/gright_dir_len
        right_dir[1] = gright_dir[1]/gright_dir_len
        right_dir[2] = gright_dir[2]/gright_dir_len
        #self.lim_ang
        coef_and_lim_ang[1] = catan(((ctan(ghor_range))**2+(ctan(gver_range))**2)**0.5)            
        

def pointren(point):
        '''translates a 3D point to 2D coords on the image (0,0) is the centre
        '''
        xvec[0] = point[0]-xpos[0]
        xvec[1] = point[1]-xpos[1]
        xvec[2] = point[2]-xpos[2]
        cdef double xvec_len = (xvec[0]**2+xvec[1]**2+xvec[2]**2)**0.5
        
        cdef double det = xvec[0]*look_dir[0]+xvec[1]*look_dir[1]+xvec[2]*look_dir[2]
        if det<=0:
            return False
        cdef double look_angle = acos(det/xvec_len)
        if look_angle>coef_and_lim_ang[1]:
            return False
        cdef double dis = ctan(look_angle)*coef_and_lim_ang[0] #distance from the centre of the image
        if dis<TOLERANCE:
            return (0, 0)
        rot_vec[0] = xvec[0]-det*look_dir[0]
        rot_vec[1] = xvec[1]-det*look_dir[1]
        rot_vec[2] = xvec[2]-det*look_dir[2]
        cdef double rot_vec_len = (rot_vec[0]**2+rot_vec[1]**2+rot_vec[2]**2)**0.5
        rot_vec[0] = rot_vec[0]/rot_vec_len
        rot_vec[1] = rot_vec[1]/rot_vec_len
        rot_vec[2] = rot_vec[2]/rot_vec_len
        
        rot_angle = acos(right_dir[0]*rot_vec[0]+right_dir[1]*rot_vec[1]+right_dir[2]*rot_vec[2])
        if rot_vec[0]*up_dir[0]+rot_vec[1]*up_dir[1]+rot_vec[2]*up_dir[2]<0:
            rot_angle = -rot_angle
            
        return dis*ccos(rot_angle), dis*csin(rot_angle)


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
    
    cdef void make_unit(self):
        cdef double l = (self.x*self.x+self.y*self.y+self.z*self.z)**0.5
        self.x = self.x/l
        self.y = self.y/l
        self.z = self.z/l
        
    cpdef move(self, v):
        self.x = self.x + v.x
        self.y = self.y + v.y
        self.z = self.z + v.z
    
    
    cpdef rotate(self, pvec, dvec, double angle):
        dvec.make_unit()
        closest_point_on_the_line = pvec.add(dvec.mul(dvec.smul((self.sub(pvec)))))
        perp = velf.sub(closest_point_on_the_line)
        new_perp = perp.mul(ccos(angle))
        tang = perp.vmul(dvec)
        new_tang = tang.mul(csin(angle))
        return closest_point_on_the_line.add(new_perp).add(new_tang)
    
    cpdef true_rotate(self, pvec, dvec, double angle):
        dvec.make_unit()
        closest_point_on_the_line = pvec.add(dvec.mul(dvec.smul((self.sub(pvec)))))
        perp = velf.sub(closest_point_on_the_line)
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
    
    def __init__(self, V1, V2, V3):
        self._b  = V1, V2, V3 #Temporary
        self.ax = V1.x
        self.ay = V1.y
        self.az = V1.z
        
        self.bx = V1.x
        self.by = V1.y
        self.bz = V1.z
        
        self.cx = V3.x
        self.cy = V3.y
        self.cz = V3.z
        
        d = V3.sub(V1).vmul(V3.sub(V2))
        self.dx = d[0]
        self.dy = d[1]
        self.dz = d[2]
        
        self.dis = d.smul(V1)
        self.set_color((0,250,0))
    
    cpdef is_visible(self, pvec):
         if self.dx*(pvec.x-self.ax)+self.dy*(pvec.y-self.ay)+self.d.z*(pvec.z-self.az)>=0:
             return 1
         return 0
    
    cpdef reverse(self):
        self.dis = -self.dis
        self.dx = -self.dx
        self.dy = -self.dy
        self.dz = -self.dz
    
    cpdef set_color(self, color):
        '''Sets the color of the plane to color. Must be in rgb. Eg: (255, 255, 255) is white.'''
        self.color = rgb_to_hsv(color[0]/255.0,color[1]/255.0,color[2]/255.0)
    
    def get_color(self, light_dir):
        '''Returns the rgb color of the plane when light is shone from light dir'''
        return tuple([int(round(e*255)) for e in hsv_to_rgb(self.color[0],self.color[1],self.color[2]*abs(self._direction*light_dir))])
        
    #is_visible
    #reverse
    #intersection_with_line (needed later)
    #set_color
    #get_color
    
    
        
        
        
        
    

    
    

        
        

