from blocks import *
import render 
import fpiglet as plotlib
import time
import cProfile, pstats, StringIO
import math


pr = cProfile.Profile()
pr.enable()

plot = plotlib.Plot()

def draw_plane(plane):
    ps = [render.pointren(p) for p in plane.points()]
    c = plane.get_color(ld)
    plot.polygon(ps, color=c, fill=1)
        
    
    

hull1 = cuboid(1,0.5,0.2)
hull1.planes[0].reverse()
print len(hull1.planes)
for p in hull1.planes:
    print p.points()
hull2 = cuboid(3, 0.5, 3)
hull2.set_color((0,0,250))
hull3 = cuboid(1,0.5,0.2)
hull4 = cuboid(0.5,0.5,2.3)
hull5 = cuboid(0.5,0.5,1.3)

hull2.move(fgeo.Vector(-1,-1.3,-0.5))
hull2.planes[0].reverse()
hull3.move(fgeo.Vector(0,0,1.1))
hull3.planes[0].reverse()
hull4.move(fgeo.Vector(-0.5,0,0))
hull4.planes[0].reverse()
hull5.move(fgeo.Vector(1,0,0))
hull5.planes[0].reverse()


p1 = Polyhedron([hull1, hull3, hull4, hull5, hull2])
#p1.move(fgeo.Vector(0.1,0,0))
w = World([p1])
a=0

tt=time.time()
st = fgeo.Vector(3,3,3)
ld = st.unit().mul(-1)
render.ini(gpos=st.coords())
xxx=500
while time.time()-tt<100:
    #c.plot.text('X',c.pointren(Point(2,0,0)))
    #c.plot.text('Y',c.pointren(Point(0,2,0)))
    #c.plot.text('Z',c.pointren(Point(0,0,2)))
    for h in w.get_draw_order(st):
        for e in h.planes:
            if e.is_visible(st):
                draw_plane(e)
    
        
    #c.plot.line(render.pointren((2,0,0)),c.(Point(-2,0,0)))
    #c.plot.line(render.pointren((0,2,0)),c.(Point(0,-2,0)))
    #plot.line(render.pointren((0,0,2)),render.pointren((0,0,-2)))
    plot.update()
    if not a%(2*xxx):
        axis = fgeo.Vector(0.5,0.5,0.5), [fgeo.Vector(1,0,0), fgeo.Vector(0,1,0), fgeo.Vector(0,0,1)][(a/(xxx))%3]
    st.rotate(axis[0], axis[1],  math.pi/xxx)
    ld = st.unit().mul(-1)
    time.sleep(0.003)
    render.ini(gpos=st.coords())
    plot.clear()
    a+=1

pr.disable()
s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print s.getvalue()
