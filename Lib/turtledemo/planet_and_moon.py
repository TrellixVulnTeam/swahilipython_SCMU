#!/usr/bin/env python3
"""       turtle-example-suite:

        tdemo_planets_and_moon.py

Gravitational system simulation using the
approximation method kutoka Feynman-lectures,
p.9-8, using turtlegraphics.

Example: heavy central body, light planet,
very light moon!
Planet has a circular orbit, moon a stable
orbit around the planet.

You can hold the movement temporarily by
pressing the left mouse button with the
mouse over the scrollbar of the canvas.

"""
kutoka turtle agiza Shape, Turtle, mainloop, Vec2D kama Vec

G = 8

kundi GravSys(object):
    eleza __init__(self):
        self.planets = []
        self.t = 0
        self.dt = 0.01
    eleza init(self):
        kila p kwenye self.planets:
            p.init()
    eleza start(self):
        kila i kwenye range(10000):
            self.t += self.dt
            kila p kwenye self.planets:
                p.step()

kundi Star(Turtle):
    eleza __init__(self, m, x, v, gravSys, shape):
        Turtle.__init__(self, shape=shape)
        self.penup()
        self.m = m
        self.setpos(x)
        self.v = v
        gravSys.planets.append(self)
        self.gravSys = gravSys
        self.resizemode("user")
        self.pendown()
    eleza init(self):
        dt = self.gravSys.dt
        self.a = self.acc()
        self.v = self.v + 0.5*dt*self.a
    eleza acc(self):
        a = Vec(0,0)
        kila planet kwenye self.gravSys.planets:
            ikiwa planet != self:
                v = planet.pos()-self.pos()
                a += (G*planet.m/abs(v)**3)*v
        rudisha a
    eleza step(self):
        dt = self.gravSys.dt
        self.setpos(self.pos() + dt*self.v)
        ikiwa self.gravSys.planets.index(self) != 0:
            self.setheading(self.towards(self.gravSys.planets[0]))
        self.a = self.acc()
        self.v = self.v + dt*self.a

## create compound yellow/blue turtleshape kila planets

eleza main():
    s = Turtle()
    s.reset()
    s.getscreen().tracer(0,0)
    s.ht()
    s.pu()
    s.fd(6)
    s.lt(90)
    s.begin_poly()
    s.circle(6, 180)
    s.end_poly()
    m1 = s.get_poly()
    s.begin_poly()
    s.circle(6,180)
    s.end_poly()
    m2 = s.get_poly()

    planetshape = Shape("compound")
    planetshape.addcomponent(m1,"orange")
    planetshape.addcomponent(m2,"blue")
    s.getscreen().register_shape("planet", planetshape)
    s.getscreen().tracer(1,0)

    ## setup gravitational system
    gs = GravSys()
    sun = Star(1000000, Vec(0,0), Vec(0,-2.5), gs, "circle")
    sun.color("yellow")
    sun.shapesize(1.8)
    sun.pu()
    earth = Star(12500, Vec(210,0), Vec(0,195), gs, "planet")
    earth.pencolor("green")
    earth.shapesize(0.8)
    moon = Star(1, Vec(220,0), Vec(0,295), gs, "planet")
    moon.pencolor("blue")
    moon.shapesize(0.5)
    gs.init()
    gs.start()
    rudisha "Done!"

ikiwa __name__ == '__main__':
    main()
    mainloop()
