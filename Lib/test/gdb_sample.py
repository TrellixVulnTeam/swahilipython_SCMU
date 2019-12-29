# Sample script kila use by test_gdb.py

eleza foo(a, b, c):
    bar(a, b, c)

eleza bar(a, b, c):
    baz(a, b, c)

eleza baz(*args):
    id(42)

foo(1, 2, 3)
