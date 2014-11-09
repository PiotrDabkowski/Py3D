from PIL import Image
from PIL import ImageDraw
import guif
import math



class Plot:
    def __init__(self, size=(600,400), pos=(0,0), scale_x=1, scale_y=1, centre=True):
        self.__vid = guif.Video(size)
        self.__size = size
        self.__im = Image.new('RGBA', self.__size, 'white')
        self.__draw = ImageDraw.Draw(self.__im)
        self.d = self.__draw
        self.__pos = pos
        if centre:
            self.__pos = -size[0]/2, -size[1]/2
        self.__scale_x = float(scale_x)
        self.__scale_y = float(scale_y)
        self.update()
    
    def update(self):
        self.__vid.change_frame(self.__im)
    
    def clear(self):
        self.__im = Image.new('RGBA', self.__size, 'white')
        self.__draw = ImageDraw.Draw(self.__im)
    
    def line(self, p1, p2, color='black', thickness=1):
        self.__draw.line(list(self.__point_transform(p1))+list(self.__point_transform(p2)), color, thickness)
        
    def polygon(self, points, color='black', fill=False, thickness=1):
        if fill: # Fill inside
            points = [self.__point_transform(p) for p in points]
            self.__draw.polygon(points, color)
        else:
            last = points[-1]
            for point in points:
                self.line(last, point, color, thickness)
                last = point
    
    def circle(self, centre, radius, color='black', full=False, thickness=1):
        (x, y), r= self.__point_transform(centre), radius
        if full:
            self.__draw.ellipse((x-r, y-r, x+r, y+r), color) #Fix scale!
        else:
            n=36
            step = 2*math.pi/n
            points = [(round(centre[0]+radius*math.cos(s*step)), round(centre[1]+radius*math.sin(s*step))) for s in xrange(n)]
            self.polygon(points, color, False, thickness)
    
    def graph(self, func, x_domain, y_domain):
        pass

    def text(self, text, pos, color='black'):
        self.__draw.text(self.__point_transform(pos), text, color)
        self.__update()
    
    def change_view(self, left_bottom_corner, right_top_corner):
        sx, sy = self.__size
        self.__pos = left_bottom_corner
        self.__scale_x = abs(left_bottom_corner[0]-right_top_corner[0])/float(sx)
        self.__scale_y = abs(left_bottom_corner[1]-right_top_corner[1])/float(sy)
        
    def __point_transform(self, point):
        #return point[0], self.__size[1]-point[1]
        return (point[0]-self.__pos[0])/self.__scale_x, (self.__size[1]-point[1]+self.__pos[1])/self.__scale_y


    
