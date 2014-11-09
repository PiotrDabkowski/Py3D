from geometry import *
from blocks import *
import render 
import render2
import piglet as plotlib
import time
import cProfile, pstats, StringIO
pr = cProfile.Profile()
pr.enable()

plot = plotlib.Plot()

def draw_plane(plane):
    ps = [render.pointren(p._coords) for p in plane._b]
    c = plane.get_color(ld)
    plot.polygon(ps, color=c, fill=1)
        
    
    


hull1 = ConvexHull(ranp(10))
hull2 = sphere(1, num=100)
hull2.move(Vector(-1.5,1,1))
y = render2.Render()


p1 = Polyhedron([hull1, hull2])

w = World([p1])
a=0

tt=time.time()
st = Point(3,3,3)
ld = -st.vector().unit()
render.ini(gpos=(3,3,3))
y.ini(pos=st)
xxx=200
while time.time()-tt<12:
    #c.plot.text('X',c.pointren(Point(2,0,0)))
    #c.plot.text('Y',c.pointren(Point(0,2,0)))
    #c.plot.text('Z',c.pointren(Point(0,0,2)))
    for h in w.get_draw_order(st):
        for e in h.planes:
            if e.is_visible(st):
                draw_plane(e)
    
        
    #c.plot.line(c.pointren(Point(2,0,0)),c.pointren(Point(-2,0,0)))
    #c.plot.line(c.pointren(Point(0,2,0)),c.pointren(Point(0,-2,0)))
    #c.plot.line(c.pointren(Point(0,0,2)),c.pointren(Point(0,0,-2)))
    plot.update()
    if not a%(2*xxx):
        axis = Line(Point(0.5,0.5,0.5), [Vector(1,0,0), Vector(0,1,0), Vector(0,0,1)][(a/(xxx))%3])
    st = st.rotate(axis, math.pi/xxx)
    ld = -st.vector().unit()
    time.sleep(0.003)
    render.ini(gpos=st._coords)
    plot.clear()
    a+=1

pr.disable()
s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print s.getvalue()
