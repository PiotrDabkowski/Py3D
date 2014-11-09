from geometry import *
from blocks import *
import colorsys
import time
math.cot = lambda x: 1/math.tan(x)
to_hsv = lambda a,b,c: list(colorsys.rgb_to_hsv(a/255.0,b/255.0,c/255.0))
to_rgb = lambda a,b,c: tuple([int(round(e*255)) for e in colorsys.hsv_to_rgb(a,b,c)])

def acos(x):
    if 1<abs(x)<1+TOLERANCE:
        return math.pi if x<0 else 0
    elif abs(x)<=1:
        return math.acos(x)
    raise ValueError('Invalid input for acos')
    

import piglet as plotlib

class Render:
    def __init__(self):
        self.ini()
        #self.plot.on_keydown = self.han_m
        
    def ini(self, look_dir=Vector(1,1,1),
                       up_dir=Vector(0,1,0),
                       hor_range=math.pi/3, #60 degrees
                       ver_range=math.pi/6, #30 degrees
                       hor_len=500,
                       pos=Point(-3,3,-3)):
        '''Bottom left edge is 0'''
        look_dir = -1*(pos.vector()-Vector(0.0,0.0,0.0))
        self.pos = pos
        self.coef = hor_len/(math.tan(hor_range))
        self.look_dir =  look_dir.unit()
        self.up_dir = (up_dir - (self.look_dir*up_dir)*self.look_dir).unit()
        self.right_dir =  (self.look_dir%self.up_dir).unit()
        self.lim_ang = math.atan(((math.tan(hor_range))**2+(math.tan(ver_range))**2)**0.5)

    def move(self, up, right, forward):
        self.pos+=up*self.up_dir+right*self.right_dir+forward*self.look_dir
        #self.ini(pos = self.pos)
    def han_m(self, e):
        c = e['unicode']
        if c=='a':
           print 'a'
           self.move(0,-0.5,0)
        elif c=='d':
            self.move(0,0.5,0)
        elif c=='w':
            self.move(0.5,0,0)
        elif c=='s':
            self.move(-0.5,0,0)
        elif c=='z':
            self.move(0,0,0.5)
        elif c=='x':
            self.move(0,0,-0.5)
            
    def vecren(self, vec):
        '''translates a 3D look vector to 2D coords on the image (0,0) is the
           centre'''
        det = vec*self.look_dir
        if det<=0:
            return False
        look_angle = acos(det/vec.len())
        if look_angle>self.lim_ang:
            return False
        dis = math.tan(look_angle)*self.coef #distance from the centre of the image
        if dis<TOLERANCE:
            return 0,0
        rot_vec = (vec-det*self.look_dir).unit()
        rot_angle = acos(self.right_dir*rot_vec)
        if rot_vec*self.up_dir<0:
            rot_angle = -rot_angle
            
        return dis*math.cos(rot_angle), dis*math.sin(rot_angle)
        
    def pointren(self, point):
        '''translates a 3D point to 2D coords on the image (0,0) is the centre
        '''
        return self.vecren(point-self.pos)
    
    def draw_plane(self, plane):
        if not plane.is_visible(self.pos):
            return None
        color = plane.get_color(self.look_dir)
        xx= [self.pointren(p) for p in plane._b]
        self.plot.polygon(xx, color=color, fill=1)

    
        
        
def is_closer(point, p1, p2):
    '''Checks whether p2 is closer to the point than p1'''
    d = p1._direction
    delta = (point-p1._b[0])*d
    if not delta:
        return True
    elif delta>0:
        for p in p2._b:
            if (point-p)*d>0:
                return True
    else:
        for p in p2._b:
            if (point-p)*d<0:
                return True
    return False
            

def plane_priority(p1, p2):
    if is_closer(point, p1, p2):
        if not is_closer(point, p2, p1):
            return 1
        else:
            return -1
    else:
        if is_closer(point, p2, p1):
            return -1
        else:
            return 1

def plane_order(planes, poinnt):
    #Slooow n**2 :( hope to make it n*log(n)
    global point
    point = poinnt
    return sorted(planes, cmp=plane_priority)
    

    
    

        
        

