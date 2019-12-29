#!/usr/bin/env python3
"""      turtle-example-suite:

        tdemo_fractalCurves.py

This program draws two fractal-curve-designs:
(1) A hilbert curve (in a box)
(2) A combination of Koch-curves.

The CurvesTurtle kundi na the fractal-curve-
methods are taken kutoka the PythonCard example
scripts kila turtle-graphics.
"""
kutoka turtle agiza *
kutoka time agiza sleep, perf_counter kama clock

kundi CurvesTurtle(Pen):
    # example derived kutoka
    # Turtle Geomejaribu: The Computer kama a Medium kila Exploring Mathematics
    # by Harold Abelson na Andrea diSessa
    # p. 96-98
    eleza hilbert(self, size, level, parity):
        ikiwa level == 0:
            rudisha
        # rotate na draw first subcurve ukijumuisha opposite parity to big curve
        self.left(parity * 90)
        self.hilbert(size, level - 1, -parity)
        # interface to na draw second subcurve ukijumuisha same parity kama big curve
        self.forward(size)
        self.right(parity * 90)
        self.hilbert(size, level - 1, parity)
        # third subcurve
        self.forward(size)
        self.hilbert(size, level - 1, parity)
        # fourth subcurve
        self.right(parity * 90)
        self.forward(size)
        self.hilbert(size, level - 1, -parity)
        # a final turn ni needed to make the turtle
        # end up facing outward kutoka the large square
        self.left(parity * 90)

    # Visual Modeling ukijumuisha Logo: A Structural Approach to Seeing
    # by James Clayson
    # Koch curve, after Helge von Koch who introduced this geometric figure kwenye 1904
    # p. 146
    eleza fractalgon(self, n, rad, lev, dir):
        agiza math

        # ikiwa dir = 1 turn outward
        # ikiwa dir = -1 turn inward
        edge = 2 * rad * math.sin(math.pi / n)
        self.pu()
        self.fd(rad)
        self.pd()
        self.rt(180 - (90 * (n - 2) / n))
        kila i kwenye range(n):
            self.fractal(edge, lev, dir)
            self.rt(360 / n)
        self.lt(180 - (90 * (n - 2) / n))
        self.pu()
        self.bk(rad)
        self.pd()

    # p. 146
    eleza fractal(self, dist, depth, dir):
        ikiwa depth < 1:
            self.fd(dist)
            rudisha
        self.fractal(dist / 3, depth - 1, dir)
        self.lt(60 * dir)
        self.fractal(dist / 3, depth - 1, dir)
        self.rt(120 * dir)
        self.fractal(dist / 3, depth - 1, dir)
        self.lt(60 * dir)
        self.fractal(dist / 3, depth - 1, dir)

eleza main():
    ft = CurvesTurtle()

    ft.reset()
    ft.speed(0)
    ft.ht()
    ft.getscreen().tracer(1,0)
    ft.pu()

    size = 6
    ft.setpos(-33*size, -32*size)
    ft.pd()

    ta=clock()
    ft.fillcolor("red")
    ft.begin_fill()
    ft.fd(size)

    ft.hilbert(size, 6, 1)

    # frame
    ft.fd(size)
    kila i kwenye range(3):
        ft.lt(90)
        ft.fd(size*(64+i%2))
    ft.pu()
    kila i kwenye range(2):
        ft.fd(size)
        ft.rt(90)
    ft.pd()
    kila i kwenye range(4):
        ft.fd(size*(66+i%2))
        ft.rt(90)
    ft.end_fill()
    tb=clock()
    res =  "Hilbert: %.2fsec. " % (tb-ta)

    sleep(3)

    ft.reset()
    ft.speed(0)
    ft.ht()
    ft.getscreen().tracer(1,0)

    ta=clock()
    ft.color("black", "blue")
    ft.begin_fill()
    ft.fractalgon(3, 250, 4, 1)
    ft.end_fill()
    ft.begin_fill()
    ft.color("red")
    ft.fractalgon(3, 200, 4, -1)
    ft.end_fill()
    tb=clock()
    res +=  "Koch: %.2fsec." % (tb-ta)
    rudisha res

ikiwa __name__  == '__main__':
    msg = main()
    andika(msg)
    mainloop()
