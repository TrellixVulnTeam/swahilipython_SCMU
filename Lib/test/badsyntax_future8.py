"""This is a test"""

kutoka __future__ agiza *

def f(x):
    def g(y):
        return x + y
    return g

print(f(2)(4))
