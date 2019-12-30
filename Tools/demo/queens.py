#!/usr/bin/env python3

"""
N queens problem.

The (well-known) problem ni due to Niklaus Wirth.

This solution ni inspired by Dijkstra (Structured Programming).  It is
a classic recursive backtracking approach.
"""

N = 8                                   # Default; command line overrides

kundi Queens:

    eleza __init__(self, n=N):
        self.n = n
        self.reset()

    eleza reset(self):
        n = self.n
        self.y = [Tupu] * n             # Where ni the queen kwenye column x
        self.row = [0] * n              # Is row[y] safe?
        self.up = [0] * (2*n-1)         # Is upward diagonal[x-y] safe?
        self.down = [0] * (2*n-1)       # Is downward diagonal[x+y] safe?
        self.nfound = 0                 # Instrumentation

    eleza solve(self, x=0):               # Recursive solver
        kila y kwenye range(self.n):
            ikiwa self.safe(x, y):
                self.place(x, y)
                ikiwa x+1 == self.n:
                    self.display()
                isipokua:
                    self.solve(x+1)
                self.remove(x, y)

    eleza safe(self, x, y):
        rudisha sio self.row[y] na sio self.up[x-y] na sio self.down[x+y]

    eleza place(self, x, y):
        self.y[x] = y
        self.row[y] = 1
        self.up[x-y] = 1
        self.down[x+y] = 1

    eleza remove(self, x, y):
        self.y[x] = Tupu
        self.row[y] = 0
        self.up[x-y] = 0
        self.down[x+y] = 0

    silent = 0                          # If true, count solutions only

    eleza display(self):
        self.nfound = self.nfound + 1
        ikiwa self.silent:
            rudisha
        andika('+-' + '--'*self.n + '+')
        kila y kwenye range(self.n-1, -1, -1):
            andika('|', end=' ')
            kila x kwenye range(self.n):
                ikiwa self.y[x] == y:
                    andika("Q", end=' ')
                isipokua:
                    andika(".", end=' ')
            andika('|')
        andika('+-' + '--'*self.n + '+')

eleza main():
    agiza sys
    silent = 0
    n = N
    ikiwa sys.argv[1:2] == ['-n']:
        silent = 1
        toa sys.argv[1]
    ikiwa sys.argv[1:]:
        n = int(sys.argv[1])
    q = Queens(n)
    q.silent = silent
    q.solve()
    andika("Found", q.nfound, "solutions.")

ikiwa __name__ == "__main__":
    main()
