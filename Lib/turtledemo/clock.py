#!/usr/bin/env python3
# -*- coding: cp1252 -*-
"""       turtle-example-suite:

             tdemo_clock.py

Enhanced clock-program, showing date
and time
  ------------------------------------
   Press STOP to exit the program!
  ------------------------------------
"""
kutoka turtle agiza *
kutoka datetime agiza datetime

eleza jump(distanz, winkel=0):
    penup()
    right(winkel)
    forward(distanz)
    left(winkel)
    pendown()

eleza hand(laenge, spitze):
    fd(laenge*1.15)
    rt(90)
    fd(spitze/2.0)
    lt(120)
    fd(spitze)
    lt(120)
    fd(spitze)
    lt(120)
    fd(spitze/2.0)

eleza make_hand_shape(name, laenge, spitze):
    reset()
    jump(-laenge*0.15)
    begin_poly()
    hand(laenge, spitze)
    end_poly()
    hand_form = get_poly()
    register_shape(name, hand_form)

eleza clockface(radius):
    reset()
    pensize(7)
    kila i kwenye range(60):
        jump(radius)
        ikiwa i % 5 == 0:
            fd(25)
            jump(-radius-25)
        isipokua:
            dot(3)
            jump(-radius)
        rt(6)

eleza setup():
    global second_hand, minute_hand, hour_hand, writer
    mode("logo")
    make_hand_shape("second_hand", 125, 25)
    make_hand_shape("minute_hand",  130, 25)
    make_hand_shape("hour_hand", 90, 25)
    clockface(160)
    second_hand = Turtle()
    second_hand.shape("second_hand")
    second_hand.color("gray20", "gray80")
    minute_hand = Turtle()
    minute_hand.shape("minute_hand")
    minute_hand.color("blue1", "red1")
    hour_hand = Turtle()
    hour_hand.shape("hour_hand")
    hour_hand.color("blue3", "red3")
    kila hand kwenye second_hand, minute_hand, hour_hand:
        hand.resizemode("user")
        hand.shapesize(1, 1, 3)
        hand.speed(0)
    ht()
    writer = Turtle()
    #writer.mode("logo")
    writer.ht()
    writer.pu()
    writer.bk(85)

eleza wochentag(t):
    wochentag = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]
    rudisha wochentag[t.weekday()]

eleza datum(z):
    monat = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "June",
             "July", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]
    j = z.year
    m = monat[z.month - 1]
    t = z.day
    rudisha "%s %d %d" % (m, t, j)

eleza tick():
    t = datetime.today()
    sekunde = t.second + t.microsecond*0.000001
    minute = t.minute + sekunde/60.0
    stunde = t.hour + minute/60.0
    jaribu:
        tracer(Uongo)  # Terminator can occur here
        writer.clear()
        writer.home()
        writer.forward(65)
        writer.write(wochentag(t),
                     align="center", font=("Courier", 14, "bold"))
        writer.back(150)
        writer.write(datum(t),
                     align="center", font=("Courier", 14, "bold"))
        writer.forward(85)
        tracer(Kweli)
        second_hand.setheading(6*sekunde)  # ama here
        minute_hand.setheading(6*minute)
        hour_hand.setheading(30*stunde)
        tracer(Kweli)
        ontimer(tick, 100)
    tatizo Terminator:
        pita  # turtledemo user pressed STOP

eleza main():
    tracer(Uongo)
    setup()
    tracer(Kweli)
    tick()
    rudisha "EVENTLOOP"

ikiwa __name__ == "__main__":
    mode("logo")
    msg = main()
    andika(msg)
    mainloop()
