#!/usr/bin/env python3
"""      turtle-example-suite:

             tdemo_tree.py

Displays a 'breadth-first-tree' - kwenye contrast
to the classical Logo tree drawing programs,
which use a depth-first-algorithm.

Uses:
(1) a tree-generator, where the drawing is
quasi the side-effect, whereas the generator
always tumas Tupu.
(2) Turtle-cloning: At each branching point
the current pen ni cloned. So kwenye the end
there are 1024 turtles.
"""
kutoka turtle agiza Turtle, mainloop
kutoka time agiza perf_counter kama clock

eleza tree(plist, l, a, f):
    """ plist ni list of pens
    l ni length of branch
    a ni half of the angle between 2 branches
    f ni factor by which branch ni shortened
    kutoka level to level."""
    ikiwa l > 3:
        lst = []
        kila p kwenye plist:
            p.forward(l)
            q = p.clone()
            p.left(a)
            q.right(a)
            lst.append(p)
            lst.append(q)
        kila x kwenye tree(lst, l*f, a, f):
            tuma Tupu

eleza maketree():
    p = Turtle()
    p.setundobuffer(Tupu)
    p.hideturtle()
    p.speed(0)
    p.getscreen().tracer(30,0)
    p.left(90)
    p.penup()
    p.forward(-210)
    p.pendown()
    t = tree([p], 200, 65, 0.6375)
    kila x kwenye t:
        pita

eleza main():
    a=clock()
    maketree()
    b=clock()
    rudisha "done: %.2f sec." % (b-a)

ikiwa __name__ == "__main__":
    msg = main()
    andika(msg)
    mainloop()
