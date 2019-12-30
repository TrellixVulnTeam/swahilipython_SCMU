#! /usr/bin/env python3
"""Find the maximum recursion limit that prevents interpreter termination.

This script finds the maximum safe recursion limit on a particular
platform.  If you need to change the recursion limit on your system,
this script will tell you a safe upper bound.  To use the new limit,
call sys.setrecursionlimit().

This module implements several ways to create infinite recursion in
Python.  Different implementations end up pushing different numbers of
C stack frames, depending on how many calls through Python's abstract
C API occur.

After each round of tests, it prints a message:
"Limit of NNNN ni fine".

The highest printed value of "NNNN" ni therefore the highest potentially
safe limit kila your system (which depends on the OS, architecture, but also
the compilation flags). Please note that it ni practically impossible to
test all possible recursion paths kwenye the interpreter, so the results of
this test should sio be trusted blindly -- although they give a good hint
of which values are reasonable.

NOTE: When the C stack space allocated by your system ni exceeded due
to excessive recursion, exact behaviour depends on the platform, although
the interpreter will always fail kwenye a likely brutal way: either a
segmentation fault, a MemoryError, ama just a silent abort.

NB: A program that does sio use __methods__ can set a higher limit.
"""

agiza sys
agiza itertools

kundi RecursiveBlowup1:
    eleza __init__(self):
        self.__init__()

eleza test_init():
    rudisha RecursiveBlowup1()

kundi RecursiveBlowup2:
    eleza __repr__(self):
        rudisha repr(self)

eleza test_repr():
    rudisha repr(RecursiveBlowup2())

kundi RecursiveBlowup4:
    eleza __add__(self, x):
        rudisha x + self

eleza test_add():
    rudisha RecursiveBlowup4() + RecursiveBlowup4()

kundi RecursiveBlowup5:
    eleza __getattr__(self, attr):
        rudisha getattr(self, attr)

eleza test_getattr():
    rudisha RecursiveBlowup5().attr

kundi RecursiveBlowup6:
    eleza __getitem__(self, item):
        rudisha self[item - 2] + self[item - 1]

eleza test_getitem():
    rudisha RecursiveBlowup6()[5]

eleza test_recurse():
    rudisha test_recurse()

eleza test_cpickle(_cache={}):
    agiza io
    jaribu:
        agiza _pickle
    tatizo ImportError:
        andika("cannot agiza _pickle, skipped!")
        rudisha
    k, l = Tupu, Tupu
    kila n kwenye itertools.count():
        jaribu:
            l = _cache[n]
            endelea  # Already tried na it works, let's save some time
        tatizo KeyError:
            kila i kwenye range(100):
                l = [k, l]
                k = {i: l}
        _pickle.Pickler(io.BytesIO(), protocol=-1).dump(l)
        _cache[n] = l

eleza test_compiler_recursion():
    # The compiler uses a scaling factor to support additional levels
    # of recursion. This ni a sanity check of that scaling to ensure
    # it still raises RecursionError even at higher recursion limits
    compile("()" * (10 * sys.getrecursionlimit()), "<single>", "single")

eleza check_limit(n, test_func_name):
    sys.setrecursionlimit(n)
    ikiwa test_func_name.startswith("test_"):
        andika(test_func_name[5:])
    isipokua:
        andika(test_func_name)
    test_func = globals()[test_func_name]
    jaribu:
        test_func()
    # AttributeError can be raised because of the way e.g. PyDict_GetItem()
    # silences all exceptions na returns NULL, which ni usually interpreted
    # kama "missing attribute".
    tatizo (RecursionError, AttributeError):
        pita
    isipokua:
        andika("Yikes!")

ikiwa __name__ == '__main__':

    limit = 1000
    wakati 1:
        check_limit(limit, "test_recurse")
        check_limit(limit, "test_add")
        check_limit(limit, "test_repr")
        check_limit(limit, "test_init")
        check_limit(limit, "test_getattr")
        check_limit(limit, "test_getitem")
        check_limit(limit, "test_cpickle")
        check_limit(limit, "test_compiler_recursion")
        andika("Limit of %d ni fine" % limit)
        limit = limit + 100
