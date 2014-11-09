import wx
from PIL import Image
import threading
import time
'''Get the instance of the Video class and use change_frame to change frames! EASY'''

def get_image():
    # Put your code here to return a PIL image from the camera.
    return Image.open('bar.bmp')

def pil_to_wx(image):
    width, height = image.size
    buffer = image.convert('RGB').tostring()
    bitmap = wx.BitmapFromBuffer(width, height, buffer)
    return bitmap

class Panel(wx.Panel):
    def __init__(self, parent, size):
        self.dialog_init_function=False
        self.dialog_out=False
        super(Panel, self).__init__(parent, -1)
        self.SetSize(size)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.img_now= pil_to_wx(Image.new('RGB',parent.GetSize(),'Black'))
        self.changed=False
        self.update()
        
        
    

    def bind_mouse(self, click, move, release, scroll):
        self.Bind(wx.EVT_LEFT_DOWN, click)
        self.Bind(wx.EVT_MOTION, move)
        self.Bind(wx.EVT_LEFT_UP, release)
        self.Bind(wx.EVT_MOUSEWHEEL, scroll)
        
    def update(self):
        if not self.changed:
           self.changed=True
           self.Refresh()
           self.Update()
        if self.dialog_init_function:
            try:
                #dialog_init_function must be a funtion that takes the parent as arg
                # and returns wx dialog object
                dialog = self.dialog_init_function(self)
                dialog.ShowModal()
                self.dialog_out=dialog.GetValue()
                self.dialog_out = self.dialog_out if self.dialog_out else True
                dialog.Destroy()
                
            except Exception, err:
                print 'Could not open the dialog!', err
            self.dialog_init_function = False
        wx.CallLater(15, self.update)
        
    
    def on_paint(self, event):
          dc = wx.AutoBufferedPaintDC(self)
          dc.DrawBitmap(self.img_now, 0, 0)

    def change_frame(self, image):
        '''image must be PIL or wx image'''
        if isinstance(image, Image.Image):
            self.img_now=pil_to_wx(image)
        else:
            self.img_now=image
        self.changed=False

class Frame(wx.Frame):
    def __init__(self, size):
        style = wx.DEFAULT_FRAME_STYLE &  ~wx.MAXIMIZE_BOX & ~wx.RESIZE_BORDER 
        super(Frame, self).__init__(None, -1, 'GUIF', style=style, )
        self.panel = Panel(self, size)
        self.Fit()
        



class Video:
    def __init__(self, size=(800,700)):
        self.thread=videoThread(autoStart=True, size=size)
        self.frame=self.thread.frame
        self.shown=False
        
    def change_frame(self, image):
        '''changes the frame on the display
        image must be PIL or wx image'''
        self.frame.panel.change_frame(image)
        if not self.shown:
            self.shown=True

    def bind_mouse(self, click, move, release, scroll):
        self.frame.panel.bind_mouse(click, move, release, scroll)

    def dialog(self, func):
        '''Quite complicated...'''
        self.frame.panel.dialog_out=False
        self.frame.panel.dialog_init_function=func

    def get_dialog_output(self):
        while not self.frame.panel.dialog_out:
            time.sleep(0.01)
        return self.frame.panel.dialog_out
        #while not self.frame.panel.dialog_out:
         #   time.sleep(0.02)
        #temp=self.frame.panel.dialog_out
        #self.frame.panel.dialog_out=False
        #return temp

class videoThread(threading.Thread):
      """Run the MainLoop as a thread. Access the frame with self.frame."""
      def __init__(self, autoStart=True, size=(800,700)):
          threading.Thread.__init__(self)
          self.setDaemon(1)
          self.start_orig = self.start
          self.start = self.start_local
          self.frame = None #to be defined in self.run
          self.size=size
          self.lock = threading.Lock()
          self.lock.acquire() #lock until variables are set
          if autoStart:
              self.start() #automatically start thread on init
      def run(self):
          app = wx.App()
          frame = Frame(self.size)
          frame.Center()
          frame.Show()  
          #define frame and release lock
          #The lock is used to make sure that SetData is defined.
          self.frame = frame
          self.lock.release()
  
          app.MainLoop()
  
      def start_local(self):
          self.start_orig()
          #After thread has started, wait until the lock is released
          #before returning so that functions get defined.
          self.lock.acquire()

