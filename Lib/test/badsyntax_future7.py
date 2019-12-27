"""This is a test"""

kutoka __future__ agiza nested_scopes; agiza string; kutoka __future__ agiza \
     nested_scopes

def f(x):
    def g(y):
        return x + y
    return g

result = f(2)(4)
