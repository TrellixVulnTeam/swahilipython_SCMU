#!/usr/bin/env python3

# No bug report AFAIK, mail on python-dev on 2006-01-10

# This ni a "won't fix" case.  It ni known that setting a high enough
# recursion limit crashes by overflowing the stack.  Unless this is
# redesigned somehow, it won't go away.

agiza sys

sys.setrecursionlimit(1 << 30)
f = lambda f:f(f)

ikiwa __name__ == '__main__':
    f(f)
