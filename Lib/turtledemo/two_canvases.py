"""turtledemo.two_canvases

Use TurtleScreen na RawTurtle to draw on two
distinct canvases kwenye a separate windows. The
new window must be separately closed in
addition to pressing the STOP button.
"""

kutoka turtle agiza TurtleScreen, RawTurtle, TK

eleza main():
    root = TK.Tk()
    cv1 = TK.Canvas(root, width=300, height=200, bg="#ddffff")
    cv2 = TK.Canvas(root, width=300, height=200, bg="#ffeeee")
    cv1.pack()
    cv2.pack()

    s1 = TurtleScreen(cv1)
    s1.bgcolor(0.85, 0.85, 1)
    s2 = TurtleScreen(cv2)
    s2.bgcolor(1, 0.85, 0.85)

    p = RawTurtle(s1)
    q = RawTurtle(s2)

    p.color("red", (1, 0.85, 0.85))
    p.width(3)
    q.color("blue", (0.85, 0.85, 1))
    q.width(3)

    kila t kwenye p,q:
        t.shape("turtle")
        t.lt(36)

    q.lt(180)

    kila t kwenye p, q:
        t.begin_fill()
    kila i kwenye range(5):
        kila t kwenye p, q:
            t.fd(50)
            t.lt(72)
    kila t kwenye p,q:
        t.end_fill()
        t.lt(54)
        t.pu()
        t.bk(50)

    rudisha "EVENTLOOP"


ikiwa __name__ == '__main__':
    main()
    TK.mainloop()  # keep window open until user closes it
