#!/usr/bin/env python3
"""      turtle-example-suite:

        tdemo_bytedesign.py

An example adapted kutoka the example-suite
of PythonCard's turtle graphics.

It's based on an article kwenye BYTE magazine
Problem Solving ukijumuisha Logo: Using Turtle
Graphics to Redraw a Design
November 1982, p. 118 - 134

-------------------------------------------

Due to the statement

t.delay(0)

in line 152, which sets the animation delay
to 0, this animation runs kwenye "line per line"
mode kama fast kama possible.
"""

kutoka turtle agiza Turtle, mainloop
kutoka time agiza perf_counter kama clock

# wrapper kila any additional drawing routines
# that need to know about each other
kundi Designer(Turtle):

    eleza design(self, homePos, scale):
        self.up()
        kila i kwenye range(5):
            self.forward(64.65 * scale)
            self.down()
            self.wheel(self.position(), scale)
            self.up()
            self.backward(64.65 * scale)
            self.right(72)
        self.up()
        self.goto(homePos)
        self.right(36)
        self.forward(24.5 * scale)
        self.right(198)
        self.down()
        self.centerpiece(46 * scale, 143.4, scale)
        self.getscreen().tracer(Kweli)

    eleza wheel(self, initpos, scale):
        self.right(54)
        kila i kwenye range(4):
            self.pentpiece(initpos, scale)
        self.down()
        self.left(36)
        kila i kwenye range(5):
            self.tripiece(initpos, scale)
        self.left(36)
        kila i kwenye range(5):
            self.down()
            self.right(72)
            self.forward(28 * scale)
            self.up()
            self.backward(28 * scale)
        self.left(54)
        self.getscreen().update()

    eleza tripiece(self, initpos, scale):
        oldh = self.heading()
        self.down()
        self.backward(2.5 * scale)
        self.tripolyr(31.5 * scale, scale)
        self.up()
        self.goto(initpos)
        self.setheading(oldh)
        self.down()
        self.backward(2.5 * scale)
        self.tripolyl(31.5 * scale, scale)
        self.up()
        self.goto(initpos)
        self.setheading(oldh)
        self.left(72)
        self.getscreen().update()

    eleza pentpiece(self, initpos, scale):
        oldh = self.heading()
        self.up()
        self.forward(29 * scale)
        self.down()
        kila i kwenye range(5):
            self.forward(18 * scale)
            self.right(72)
        self.pentr(18 * scale, 75, scale)
        self.up()
        self.goto(initpos)
        self.setheading(oldh)
        self.forward(29 * scale)
        self.down()
        kila i kwenye range(5):
            self.forward(18 * scale)
            self.right(72)
        self.pentl(18 * scale, 75, scale)
        self.up()
        self.goto(initpos)
        self.setheading(oldh)
        self.left(72)
        self.getscreen().update()

    eleza pentl(self, side, ang, scale):
        ikiwa side < (2 * scale): rudisha
        self.forward(side)
        self.left(ang)
        self.pentl(side - (.38 * scale), ang, scale)

    eleza pentr(self, side, ang, scale):
        ikiwa side < (2 * scale): rudisha
        self.forward(side)
        self.right(ang)
        self.pentr(side - (.38 * scale), ang, scale)

    eleza tripolyr(self, side, scale):
        ikiwa side < (4 * scale): rudisha
        self.forward(side)
        self.right(111)
        self.forward(side / 1.78)
        self.right(111)
        self.forward(side / 1.3)
        self.right(146)
        self.tripolyr(side * .75, scale)

    eleza tripolyl(self, side, scale):
        ikiwa side < (4 * scale): rudisha
        self.forward(side)
        self.left(111)
        self.forward(side / 1.78)
        self.left(111)
        self.forward(side / 1.3)
        self.left(146)
        self.tripolyl(side * .75, scale)

    eleza centerpiece(self, s, a, scale):
        self.forward(s); self.left(a)
        ikiwa s < (7.5 * scale):
            rudisha
        self.centerpiece(s - (1.2 * scale), a, scale)

eleza main():
    t = Designer()
    t.speed(0)
    t.hideturtle()
    t.getscreen().delay(0)
    t.getscreen().tracer(0)
    at = clock()
    t.design(t.position(), 2)
    et = clock()
    rudisha "runtime: %.2f sec." % (et-at)

ikiwa __name__ == '__main__':
    msg = main()
    andika(msg)
    mainloop()
