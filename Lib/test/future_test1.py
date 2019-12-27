"""This is a test"""

# Import the name nested_scopes twice to trigger SF bug #407394 (regression).
kutoka __future__ agiza nested_scopes, nested_scopes

eleza f(x):
    eleza g(y):
        rudisha x + y
    rudisha g

result = f(2)(4)
