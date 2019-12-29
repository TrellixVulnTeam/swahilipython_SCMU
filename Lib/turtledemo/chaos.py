# File: tdemo_chaos.py
# Author: Gregor Lingl
# Date: 2009-06-24

# A demonstration of chaos

kutoka turtle agiza *

N = 80

eleza f(x):
    rudisha 3.9*x*(1-x)

eleza g(x):
    rudisha 3.9*(x-x**2)

eleza h(x):
    rudisha 3.9*x-3.9*x*x

eleza jumpto(x, y):
    penup(); goto(x,y)

eleza line(x1, y1, x2, y2):
    jumpto(x1, y1)
    pendown()
    goto(x2, y2)

eleza coosys():
    line(-1, 0, N+1, 0)
    line(0, -0.1, 0, 1.1)

eleza plot(fun, start, color):
    pencolor(color)
    x = start
    jumpto(0, x)
    pendown()
    dot(5)
    kila i kwenye range(N):
        x=fun(x)
        goto(i+1,x)
        dot(5)

eleza main():
    reset()
    setworldcoordinates(-1.0,-0.1, N+1, 1.1)
    speed(0)
    hideturtle()
    coosys()
    plot(f, 0.35, "blue")
    plot(g, 0.35, "green")
    plot(h, 0.35, "red")
    # Now zoom in:
    kila s kwenye range(100):
        setworldcoordinates(0.5*s,-0.1, N+1, 1.1)
    rudisha "Done!"

ikiwa __name__ == "__main__":
    main()
    mainloop()
