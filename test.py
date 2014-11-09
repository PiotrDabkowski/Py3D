from libc.stdlib cimport malloc, free

class Plane:
    def __init__(self, p):
        cdef double *self.pos
        self.pos = <double *>malloc(3*cython.sizeof(double))
        if self.pos is NULL:
            raise MemoryError()
        self.pos[0] = p[0]
        self.pos[1] = p[1]
        self.pos[2] = p[2]

    def get(self):
        return self.pos[0], self.pos[1], self.pos[2]
