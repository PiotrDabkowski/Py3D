from scipy.spatial import ConvexHull
import plotlib
import random

def ranp(n, xr=450, yr=300):
    return [(xr*(random.random()-0.5), yr*(random.random()-0.5), yr*(random.random()-0.5)) for e in xrange(n)]

p = plotlib.Plot()
o = ranp(300)

c = ConvexHull(o)



