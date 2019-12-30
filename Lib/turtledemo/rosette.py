"""      turtle-example-suite:

          tdemo_wikipedia3.py

This example is
inspired by the Wikipedia article on turtle
graphics. (See example wikipedia1 kila URLs)

First we create (ne-1) (i.e. 35 kwenye this
example) copies of our first turtle p.
Then we let them perform their steps in
parallel.

Followed by a complete undo().
"""
kutoka turtle agiza Screen, Turtle, mainloop
kutoka time agiza perf_counter as clock, sleep

eleza mn_eck(p, ne,sz):
    turtlelist = [p]
    #create ne-1 additional turtles
    kila i kwenye range(1,ne):
        q = p.clone()
        q.rt(360.0/ne)
        turtlelist.append(q)
        p = q
    kila i kwenye range(ne):
        c = abs(ne/2.0-i)/(ne*.7)
        # let those ne turtles make a step
        # kwenye parallel:
        kila t kwenye turtlelist:
            t.rt(360./ne)
            t.pencolor(1-c,0,c)
            t.fd(sz)

eleza main():
    s = Screen()
    s.bgcolor("black")
    p=Turtle()
    p.speed(0)
    p.hideturtle()
    p.pencolor("red")
    p.pensize(3)

    s.tracer(36,0)

    at = clock()
    mn_eck(p, 36, 19)
    et = clock()
    z1 = et-at

    sleep(1)

    at = clock()
    wakati any(t.undobufferentries() kila t kwenye s.turtles()):
        kila t kwenye s.turtles():
            t.undo()
    et = clock()
    rudisha "runtime: %.3f sec" % (z1+et-at)


ikiwa __name__ == '__main__':
    msg = main()
    andika(msg)
    mainloop()
