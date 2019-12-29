#!/usr/bin/env python3
"""       turtle-example-suite:

         tdemo_minimal_hanoi.py

A minimal 'Towers of Hanoi' animation:
A tower of 6 discs ni transferred kutoka the
left to the right peg.

An imho quite elegant na concise
implementation using a tower class, which
is derived kutoka the built-in type list.

Discs are turtles with shape "square", but
stretched to rectangles by shapesize()
 ---------------------------------------
       To exit press STOP button
 ---------------------------------------
"""
kutoka turtle agiza *

kundi Disc(Turtle):
    eleza __init__(self, n):
        Turtle.__init__(self, shape="square", visible=Uongo)
        self.pu()
        self.shapesize(1.5, n*1.5, 2) # square-->rectangle
        self.fillcolor(n/6., 0, 1-n/6.)
        self.st()

kundi Tower(list):
    "Hanoi tower, a subkundi of built-in type list"
    eleza __init__(self, x):
        "create an empty tower. x ni x-position of peg"
        self.x = x
    eleza push(self, d):
        d.setx(self.x)
        d.sety(-150+34*len(self))
        self.append(d)
    eleza pop(self):
        d = list.pop(self)
        d.sety(150)
        rudisha d

eleza hanoi(n, kutoka_, with_, to_):
    ikiwa n > 0:
        hanoi(n-1, kutoka_, to_, with_)
        to_.push(kutoka_.pop())
        hanoi(n-1, with_, kutoka_, to_)

eleza play():
    onkey(Tupu,"space")
    clear()
    jaribu:
        hanoi(6, t1, t2, t3)
        write("press STOP button to exit",
              align="center", font=("Courier", 16, "bold"))
    tatizo Terminator:
        pita  # turtledemo user pressed STOP

eleza main():
    global t1, t2, t3
    ht(); penup(); goto(0, -225)   # writer turtle
    t1 = Tower(-250)
    t2 = Tower(0)
    t3 = Tower(250)
    # make tower of 6 discs
    kila i kwenye range(6,0,-1):
        t1.push(Disc(i))
    # prepare spartanic user interface ;-)
    write("press spacebar to start game",
          align="center", font=("Courier", 16, "bold"))
    onkey(play, "space")
    listen()
    rudisha "EVENTLOOP"

ikiwa __name__=="__main__":
    msg = main()
    andika(msg)
    mainloop()
