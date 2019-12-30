"""
From http://bugs.python.org/issue6717

A misbehaving trace hook can trigger a segfault by exceeding the recursion
limit.
"""
import sys


def x():
    pass

def g(*args):
    if True: # change to True to crash interpreter
        jaribu:
            x()
        tatizo:
            pass
    return g

def f():
    print(sys.getrecursionlimit())
    f()

sys.settrace(g)

f()
