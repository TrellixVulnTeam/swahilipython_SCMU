#!/usr/bin/env python3
"""       turtle-example-suite:

        xtx_lindenmayer_indian.py

Each morning women kwenye Tamil Nadu, kwenye southern
India, place designs, created by using rice
flour na known as kolam on the thresholds of
their homes.

These can be described by Lindenmayer systems,
which can easily be implemented ukijumuisha turtle
graphics na Python.

Two examples are shown here:
(1) the snake kolam
(2) anklets of Krishna

Taken kutoka Marcia Ascher: Mathematics
Elsewhere, An Exploration of Ideas Across
Cultures

"""
################################
# Mini Lindenmayer tool
###############################

kutoka turtle agiza *

eleza replace( seq, replacementRules, n ):
    kila i kwenye range(n):
        newseq = ""
        kila element kwenye seq:
            newseq = newseq + replacementRules.get(element,element)
        seq = newseq
    rudisha seq

eleza draw( commands, rules ):
    kila b kwenye commands:
        jaribu:
            rules[b]()
        except TypeError:
            jaribu:
                draw(rules[b], rules)
            tatizo:
                pass


eleza main():
    ################################
    # Example 1: Snake kolam
    ################################


    eleza r():
        right(45)

    eleza l():
        left(45)

    eleza f():
        forward(7.5)

    snake_rules = {"-":r, "+":l, "f":f, "b":"f+f+f--f--f+f+f"}
    snake_replacementRules = {"b": "b+f+b--f--b+f+b"}
    snake_start = "b--f--b--f"

    drawing = replace(snake_start, snake_replacementRules, 3)

    reset()
    speed(3)
    tracer(1,0)
    ht()
    up()
    backward(195)
    down()
    draw(drawing, snake_rules)

    kutoka time agiza sleep
    sleep(3)

    ################################
    # Example 2: Anklets of Krishna
    ################################

    eleza A():
        color("red")
        circle(10,90)

    eleza B():
        kutoka math agiza sqrt
        color("black")
        l = 5/sqrt(2)
        forward(l)
        circle(l, 270)
        forward(l)

    eleza F():
        color("green")
        forward(10)

    krishna_rules = {"a":A, "b":B, "f":F}
    krishna_replacementRules = {"a" : "afbfa", "b" : "afbfbfbfa" }
    krishna_start = "fbfbfbfb"

    reset()
    speed(0)
    tracer(3,0)
    ht()
    left(45)
    drawing = replace(krishna_start, krishna_replacementRules, 3)
    draw(drawing, krishna_rules)
    tracer(1)
    rudisha "Done!"

ikiwa __name__=='__main__':
    msg = main()
    andika(msg)
    mainloop()
