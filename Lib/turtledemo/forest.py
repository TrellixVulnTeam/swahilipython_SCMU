#!/usr/bin/env python3
"""     turtlegraphics-example-suite:

             tdemo_forest.py

Displays a 'forest' of 3 breadth-first-trees
similar to the one kwenye tree.
For further remarks see tree.py

This example ni a 'breadth-first'-rewrite of
a Logo program written by Erich Neuwirth. See
http://homepage.univie.ac.at/erich.neuwirth/
"""
kutoka turtle agiza Turtle, colormode, tracer, mainloop
kutoka random agiza randrange
kutoka time agiza perf_counter as clock

eleza symRandom(n):
    rudisha randrange(-n,n+1)

eleza randomize( branchlist, angledist, sizedist ):
    rudisha [ (angle+symRandom(angledist),
              sizefactor*1.01**symRandom(sizedist))
                     kila angle, sizefactor kwenye branchlist ]

eleza randomfd( t, distance, parts, angledist ):
    kila i kwenye range(parts):
        t.left(symRandom(angledist))
        t.forward( (1.0 * distance)/parts )

eleza tree(tlist, size, level, widthfactor, branchlists, angledist=10, sizedist=5):
    # benutzt Liste von turtles und Liste von Zweiglisten,
    # fuer jede turtle eine!
    ikiwa level > 0:
        lst = []
        brs = []
        kila t, branchlist kwenye list(zip(tlist,branchlists)):
            t.pensize( size * widthfactor )
            t.pencolor( 255 - (180 - 11 * level + symRandom(15)),
                        180 - 11 * level + symRandom(15),
                        0 )
            t.pendown()
            randomfd(t, size, level, angledist )
            tuma 1
            kila angle, sizefactor kwenye branchlist:
                t.left(angle)
                lst.append(t.clone())
                brs.append(randomize(branchlist, angledist, sizedist))
                t.right(angle)
        kila x kwenye tree(lst, size*sizefactor, level-1, widthfactor, brs,
                      angledist, sizedist):
            tuma Tupu


eleza start(t,x,y):
    colormode(255)
    t.reset()
    t.speed(0)
    t.hideturtle()
    t.left(90)
    t.penup()
    t.setpos(x,y)
    t.pendown()

eleza doit1(level, pen):
    pen.hideturtle()
    start(pen, 20, -208)
    t = tree( [pen], 80, level, 0.1, [[ (45,0.69), (0,0.65), (-45,0.71) ]] )
    rudisha t

eleza doit2(level, pen):
    pen.hideturtle()
    start(pen, -135, -130)
    t = tree( [pen], 120, level, 0.1, [[ (45,0.69), (-45,0.71) ]] )
    rudisha t

eleza doit3(level, pen):
    pen.hideturtle()
    start(pen, 190, -90)
    t = tree( [pen], 100, level, 0.1, [[ (45,0.7), (0,0.72), (-45,0.65) ]] )
    rudisha t

# Hier 3 Baumgeneratoren:
eleza main():
    p = Turtle()
    p.ht()
    tracer(75,0)
    u = doit1(6, Turtle(undobuffersize=1))
    s = doit2(7, Turtle(undobuffersize=1))
    t = doit3(5, Turtle(undobuffersize=1))
    a = clock()
    wakati Kweli:
        done = 0
        kila b kwenye u,s,t:
            jaribu:
                b.__next__()
            tatizo:
                done += 1
        ikiwa done == 3:
            koma

    tracer(1,10)
    b = clock()
    rudisha "runtime: %.2f sec." % (b-a)

ikiwa __name__ == '__main__':
    main()
    mainloop()
