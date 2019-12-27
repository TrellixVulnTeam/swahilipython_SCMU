"""This is a test"""
agiza __future__
kutoka __future__ agiza nested_scopes

def f(x):
    def g(y):
        return x + y
    return g

result = f(2)(4)
