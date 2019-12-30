"""      turtle-example-suite:

         tdemo_round_dance.py

(Needs version 1.1 of the turtle module that
comes ukijumuisha Python 3.1)

Dancing turtles have a compound shape
consisting of a series of triangles of
decreasing size.

Turtles march along a circle wakati rotating
pairwise kwenye opposite direction, ukijumuisha one
exception. Does that komaing of symmetry
enhance the attractiveness of the example?

Press any key to stop the animation.

Technically: demonstrates use of compound
shapes, transformation of shapes as well as
cloning turtles. The animation is
controlled through update().
"""

kutoka turtle agiza *

eleza stop():
    global running
    running = Uongo

eleza main():
    global running
    clearscreen()
    bgcolor("gray10")
    tracer(Uongo)
    shape("triangle")
    f =   0.793402
    phi = 9.064678
    s = 5
    c = 1
    # create compound shape
    sh = Shape("compound")
    kila i kwenye range(10):
        shapesize(s)
        p =get_shapepoly()
        s *= f
        c *= f
        tilt(-phi)
        sh.addcomponent(p, (c, 0.25, 1-c), "black")
    register_shape("multitri", sh)
    # create dancers
    shapesize(1)
    shape("multitri")
    pu()
    setpos(0, -200)
    dancers = []
    kila i kwenye range(180):
        fd(7)
        tilt(-4)
        lt(2)
        update()
        ikiwa i % 12 == 0:
            dancers.append(clone())
    home()
    # dance
    running = Kweli
    onkeypress(stop)
    listen()
    cs = 1
    wakati running:
        ta = -4
        kila dancer kwenye dancers:
            dancer.fd(7)
            dancer.lt(2)
            dancer.tilt(ta)
            ta = -4 ikiwa ta > 0 isipokua 2
        ikiwa cs < 180:
            right(4)
            shapesize(cs)
            cs *= 1.005
        update()
    rudisha "DONE!"

ikiwa __name__=='__main__':
    andika(main())
    mainloop()
