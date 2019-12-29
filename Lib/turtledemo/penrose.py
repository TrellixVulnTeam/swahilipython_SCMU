#!/usr/bin/env python3
"""       xturtle-example-suite:

          xtx_kites_and_darts.py

Constructs two aperiodic penrose-tilings,
consisting of kites na darts, by the method
of inflation kwenye six steps.

Starting points are the patterns "sun"
consisting of five kites na "star"
consisting of five darts.

For more information see:
 http://en.wikipedia.org/wiki/Penrose_tiling
 -------------------------------------------
"""
kutoka turtle agiza *
kutoka math agiza cos, pi
kutoka time agiza perf_counter kama clock, sleep

f = (5**0.5-1)/2.0   # (sqrt(5)-1)/2 -- golden ratio
d = 2 * cos(3*pi/10)

eleza kite(l):
    fl = f * l
    lt(36)
    fd(l)
    rt(108)
    fd(fl)
    rt(36)
    fd(fl)
    rt(108)
    fd(l)
    rt(144)

eleza dart(l):
    fl = f * l
    lt(36)
    fd(l)
    rt(144)
    fd(fl)
    lt(36)
    fd(fl)
    rt(144)
    fd(l)
    rt(144)

eleza inflatekite(l, n):
    ikiwa n == 0:
        px, py = pos()
        h, x, y = int(heading()), round(px,3), round(py,3)
        tiledict[(h,x,y)] = Kweli
        rudisha
    fl = f * l
    lt(36)
    inflatedart(fl, n-1)
    fd(l)
    rt(144)
    inflatekite(fl, n-1)
    lt(18)
    fd(l*d)
    rt(162)
    inflatekite(fl, n-1)
    lt(36)
    fd(l)
    rt(180)
    inflatedart(fl, n-1)
    lt(36)

eleza inflatedart(l, n):
    ikiwa n == 0:
        px, py = pos()
        h, x, y = int(heading()), round(px,3), round(py,3)
        tiledict[(h,x,y)] = Uongo
        rudisha
    fl = f * l
    inflatekite(fl, n-1)
    lt(36)
    fd(l)
    rt(180)
    inflatedart(fl, n-1)
    lt(54)
    fd(l*d)
    rt(126)
    inflatedart(fl, n-1)
    fd(l)
    rt(144)

eleza draw(l, n, th=2):
    clear()
    l = l * f**n
    shapesize(l/100.0, l/100.0, th)
    kila k kwenye tiledict:
        h, x, y = k
        setpos(x, y)
        setheading(h)
        ikiwa tiledict[k]:
            shape("kite")
            color("black", (0, 0.75, 0))
        isipokua:
            shape("dart")
            color("black", (0.75, 0, 0))
        stamp()

eleza sun(l, n):
    kila i kwenye range(5):
        inflatekite(l, n)
        lt(72)

eleza star(l,n):
    kila i kwenye range(5):
        inflatedart(l, n)
        lt(72)

eleza makeshapes():
    tracer(0)
    begin_poly()
    kite(100)
    end_poly()
    register_shape("kite", get_poly())
    begin_poly()
    dart(100)
    end_poly()
    register_shape("dart", get_poly())
    tracer(1)

eleza start():
    reset()
    ht()
    pu()
    makeshapes()
    resizemode("user")

eleza test(l=200, n=4, fun=sun, startpos=(0,0), th=2):
    global tiledict
    goto(startpos)
    setheading(0)
    tiledict = {}
    tracer(0)
    fun(l, n)
    draw(l, n, th)
    tracer(1)
    nk = len([x kila x kwenye tiledict ikiwa tiledict[x]])
    nd = len([x kila x kwenye tiledict ikiwa sio tiledict[x]])
    andika("%d kites na %d darts = %d pieces." % (nk, nd, nk+nd))

eleza demo(fun=sun):
    start()
    kila i kwenye range(8):
        a = clock()
        test(300, i, fun)
        b = clock()
        t = b - a
        ikiwa t < 2:
            sleep(2 - t)

eleza main():
    #title("Penrose-tiling with kites na darts.")
    mode("logo")
    bgcolor(0.3, 0.3, 0)
    demo(sun)
    sleep(2)
    demo(star)
    pencolor("black")
    goto(0,-200)
    pencolor(0.7,0.7,1)
    write("Please wait...",
          align="center", font=('Arial Black', 36, 'bold'))
    test(600, 8, startpos=(70, 117))
    rudisha "Done"

ikiwa __name__ == "__main__":
    msg = main()
    mainloop()
