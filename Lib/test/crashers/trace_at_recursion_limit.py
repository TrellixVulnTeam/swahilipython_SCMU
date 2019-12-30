"""
From http://bugs.python.org/issue6717

A misbehaving trace hook can trigger a segfault by exceeding the recursion
limit.
"""
agiza sys


eleza x():
    pass

eleza g(*args):
    ikiwa Kweli: # change to Kweli to crash interpreter
        jaribu:
            x()
        tatizo:
            pass
    rudisha g

eleza f():
    andika(sys.getrecursionlimit())
    f()

sys.settrace(g)

f()
