import pygame
from pygame import gfxdraw
from instant_decorator import instant
import time
import threading
import traceback
from collections import deque
WHITE = 255, 255, 255
BLACK = 0, 0, 0

class deque(deque, object):
	pass
    
class DiplayClosed(Exception): pass

@instant
def start(que, plot_instance, size=(640,480), name='Huwdu', color=BLACK):
    pygame.init()
    surface = pygame.display.set_mode(size)
    surface.fill(color)
    pygame.display.update()
    pygame.display.set_caption(name)
    done=0
    while not done:
        que_handle(que, surface, pygame.display, color)
        for e in pygame.event.get():
            event_post(plot_instance, e)
            if e.type == pygame.QUIT or (e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE):
                done=1
                break
        time.sleep(0.001)
    def end(x): raise DiplayClosed('Display is dead!')
    que.put = end
    pygame.display.quit()
    
    
def event_post(plot_instance, event):
    types = {2: ['on_keydown','key', 'unicode', 'scancode'],
             3: ['on_keyup', 'key', 'scancode'],
             4: ['on_motion', 'pos', 'rel', 'buttons'],
             5: ['on_clickdown', 'pos', 'button'],
             6: ['on_clickup', 'pos', 'button']
             }
    if event.type not in types:
        return None
    info = {name:getattr(event, name) for name in types[event.type][1:]}
    if 'pos' in info: # Convert pos to the required format
        info['pos'] = plot_instance.icp(info['pos'])
    msg = types[event.type][0], info
    if hasattr(plot_instance, msg[0]):
        t = threading.Thread(target=getattr(plot_instance, msg[0]), args=(msg[1],))
        t.daemon = True
        t.start()

tmk = time.time()
fk = 0
fps = 0
def que_handle(que, surface, display, color, error='print'):
    while que:
        try:
            req = que.popleft()
            if isinstance(req, bool):
                if req: #Update!
                    global tmk, fps, fk
                    fk+=1
                    if time.time()-tmk>1:
                        fps = round(fk/(time.time()-tmk),1)
                        tmk=time.time()
                        fk=0
                    font=pygame.font.Font(None,25)
                    scoretext=font.render('FPS: '+str(fps), 1,(0,200,0))
                    surface.blit(scoretext, (0, 0))  
                    display.update()
                else: # Clear!
                    surface.fill(color)
            elif req[0]=='textured_polygon':
                getattr(gfxdraw, req[0])(*tuple([surface]+list(req[1:])))
            else: # pygame.draw function!
                getattr(pygame.draw, req[0])(*tuple([surface]+list(req[1:])))
        except:
            if error=='print':
                print traceback.format_exc()
            elif error=='ignore':
                pass
            else:
                raise


                   
            

class Plot:
    def __init__(self, size=(640,480), name='Huwdu', color=WHITE):
        self._q = deque()
        self._q.put = self._q.append
        self._size = size
        self._name = name
        self._color = color
        self._centre = size[0]/2, size[1]/2
        start(self._q, self, self._size, self._name, self._color)

    def cp(self, p): 
        '''Overwrite it to change orientation shift, etc...
           Remember to change icp as well! (inverse)'''
        return p[0]+self._centre[0], -p[1]+self._centre[1]

    def icp(self, p):
        return p[0]-self._centre[0], self._centre[1]-p[1]

    def update(self):
        self._q.put(True)

    def clear(self):
        self._q.put(False)

    def textured_polygon(self, points, texture, tx, ty):
        self._q.put(('textured_polygon', points, texture, tx, ty))

    def line(self, p1, p2, color=BLACK, thickness=1):
        self._q.put(('line', color, self.cp(p1), self.cp(p2), thickness))                    

    def polygon(self, points, color=BLACK, fill=False, thickness=1):
        self._q.put(('polygon', color, [self.cp(e) for e in points], thickness if not fill else 0))
        



        
