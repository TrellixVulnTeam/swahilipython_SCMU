#!/usr/bin/env python3

"""
A Python version of the classic "bottles of beer on the wall" programming
example.

By Guido van Rossum, demystified after a version by Fredrik Lundh.
"""

agiza sys

n = 100
ikiwa sys.argv[1:]:
    n = int(sys.argv[1])

eleza bottle(n):
    ikiwa n == 0: rudisha "no more bottles of beer"
    ikiwa n == 1: rudisha "one bottle of beer"
    rudisha str(n) + " bottles of beer"

kila i kwenye range(n, 0, -1):
    andika(bottle(i), "on the wall,")
    andika(bottle(i) + ".")
    andika("Take one down, pita it around,")
    andika(bottle(i-1), "on the wall.")
