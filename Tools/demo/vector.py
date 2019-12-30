#!/usr/bin/env python3

"""
A demonstration of classes na their special methods kwenye Python.
"""

kundi Vec:
    """A simple vector class.

    Instances of the Vec kundi can be constructed kutoka numbers

    >>> a = Vec(1, 2, 3)
    >>> b = Vec(3, 2, 1)

    added
    >>> a + b
    Vec(4, 4, 4)

    subtracted
    >>> a - b
    Vec(-2, 0, 2)

    na multiplied by a scalar on the left
    >>> 3.0 * a
    Vec(3.0, 6.0, 9.0)

    ama on the right
    >>> a * 3.0
    Vec(3.0, 6.0, 9.0)
    """
    eleza __init__(self, *v):
        self.v = list(v)

    @classmethod
    eleza fromlist(cls, v):
        ikiwa sio isinstance(v, list):
            ashiria TypeError
        inst = cls()
        inst.v = v
        rudisha inst

    eleza __repr__(self):
        args = ', '.join(repr(x) kila x kwenye self.v)
        rudisha 'Vec({})'.format(args)

    eleza __len__(self):
        rudisha len(self.v)

    eleza __getitem__(self, i):
        rudisha self.v[i]

    eleza __add__(self, other):
        # Element-wise addition
        v = [x + y kila x, y kwenye zip(self.v, other.v)]
        rudisha Vec.fromlist(v)

    eleza __sub__(self, other):
        # Element-wise subtraction
        v = [x - y kila x, y kwenye zip(self.v, other.v)]
        rudisha Vec.fromlist(v)

    eleza __mul__(self, scalar):
        # Multiply by scalar
        v = [x * scalar kila x kwenye self.v]
        rudisha Vec.fromlist(v)

    __rmul__ = __mul__


eleza test():
    agiza doctest
    doctest.testmod()

test()
