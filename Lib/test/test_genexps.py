doctests = """

Test simple loop with conditional

    >>> sum(i*i for i in range(100) ikiwa i&1 == 1)
    166650

Test simple nesting

    >>> list((i,j) for i in range(3) for j in range(4) )
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]

Test nesting with the inner expression dependent on the outer

    >>> list((i,j) for i in range(4) for j in range(i) )
    [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2)]

Make sure the induction variable is not exposed

    >>> i = 20
    >>> sum(i*i for i in range(100))
    328350
    >>> i
    20

Test first class

    >>> g = (i*i for i in range(4))
    >>> type(g)
    <kundi 'generator'>
    >>> list(g)
    [0, 1, 4, 9]

Test direct calls to next()

    >>> g = (i*i for i in range(3))
    >>> next(g)
    0
    >>> next(g)
    1
    >>> next(g)
    4
    >>> next(g)
    Traceback (most recent call last):
      File "<pyshell#21>", line 1, in -toplevel-
        next(g)
    StopIteration

Does it stay stopped?

    >>> next(g)
    Traceback (most recent call last):
      File "<pyshell#21>", line 1, in -toplevel-
        next(g)
    StopIteration
    >>> list(g)
    []

Test running gen when defining function is out of scope

    >>> eleza f(n):
    ...     rudisha (i*i for i in range(n))
    >>> list(f(10))
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

    >>> eleza f(n):
    ...     rudisha ((i,j) for i in range(3) for j in range(n))
    >>> list(f(4))
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]
    >>> eleza f(n):
    ...     rudisha ((i,j) for i in range(3) for j in range(4) ikiwa j in range(n))
    >>> list(f(4))
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]
    >>> list(f(2))
    [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

Verify that parenthesis are required in a statement

    >>> eleza f(n):
    ...     rudisha i*i for i in range(n)
    Traceback (most recent call last):
       ...
    SyntaxError: invalid syntax

Verify that parenthesis are required when used as a keyword argument value

    >>> dict(a = i for i in range(10))
    Traceback (most recent call last):
       ...
    SyntaxError: invalid syntax

Verify that parenthesis are required when used as a keyword argument value

    >>> dict(a = (i for i in range(10))) #doctest: +ELLIPSIS
    {'a': <generator object <genexpr> at ...>}

Verify early binding for the outermost for-expression

    >>> x=10
    >>> g = (i*i for i in range(x))
    >>> x = 5
    >>> list(g)
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

Verify that the outermost for-expression makes an immediate check
for iterability

    >>> (i for i in 6)
    Traceback (most recent call last):
      File "<pyshell#4>", line 1, in -toplevel-
        (i for i in 6)
    TypeError: 'int' object is not iterable

Verify late binding for the outermost if-expression

    >>> include = (2,4,6,8)
    >>> g = (i*i for i in range(10) ikiwa i in include)
    >>> include = (1,3,5,7,9)
    >>> list(g)
    [1, 9, 25, 49, 81]

Verify late binding for the innermost for-expression

    >>> g = ((i,j) for i in range(3) for j in range(x))
    >>> x = 4
    >>> list(g)
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]

Verify re-use of tuples (a side benefit of using genexps over listcomps)

    >>> tupleids = list(map(id, ((i,i) for i in range(10))))
    >>> int(max(tupleids) - min(tupleids))
    0

Verify that syntax error's are raised for genexps used as lvalues

    >>> (y for y in (1,2)) = 10
    Traceback (most recent call last):
       ...
    SyntaxError: cannot assign to generator expression

    >>> (y for y in (1,2)) += 10
    Traceback (most recent call last):
       ...
    SyntaxError: cannot assign to generator expression


########### Tests borrowed kutoka or inspired by test_generators.py ############

Make a generator that acts like range()

    >>> yrange = lambda n:  (i for i in range(n))
    >>> list(yrange(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Generators always rudisha to the most recent caller:

    >>> eleza creator():
    ...     r = yrange(5)
    ...     andika("creator", next(r))
    ...     rudisha r
    >>> eleza caller():
    ...     r = creator()
    ...     for i in r:
    ...             andika("caller", i)
    >>> caller()
    creator 0
    caller 1
    caller 2
    caller 3
    caller 4

Generators can call other generators:

    >>> eleza zrange(n):
    ...     for i in yrange(n):
    ...         yield i
    >>> list(zrange(5))
    [0, 1, 2, 3, 4]


Verify that a gen exp cannot be resumed while it is actively running:

    >>> g = (next(me) for i in range(10))
    >>> me = g
    >>> next(me)
    Traceback (most recent call last):
      File "<pyshell#30>", line 1, in -toplevel-
        next(me)
      File "<pyshell#28>", line 1, in <generator expression>
        g = (next(me) for i in range(10))
    ValueError: generator already executing

Verify exception propagation

    >>> g = (10 // i for i in (5, 0, 2))
    >>> next(g)
    2
    >>> next(g)
    Traceback (most recent call last):
      File "<pyshell#37>", line 1, in -toplevel-
        next(g)
      File "<pyshell#35>", line 1, in <generator expression>
        g = (10 // i for i in (5, 0, 2))
    ZeroDivisionError: integer division or modulo by zero
    >>> next(g)
    Traceback (most recent call last):
      File "<pyshell#38>", line 1, in -toplevel-
        next(g)
    StopIteration

Make sure that None is a valid rudisha value

    >>> list(None for i in range(10))
    [None, None, None, None, None, None, None, None, None, None]

Check that generator attributes are present

    >>> g = (i*i for i in range(3))
    >>> expected = set(['gi_frame', 'gi_running'])
    >>> set(attr for attr in dir(g) ikiwa not attr.startswith('__')) >= expected
    True

    >>> kutoka test.support agiza HAVE_DOCSTRINGS
    >>> andika(g.__next__.__doc__ ikiwa HAVE_DOCSTRINGS else 'Implement next(self).')
    Implement next(self).
    >>> agiza types
    >>> isinstance(g, types.GeneratorType)
    True

Check the __iter__ slot is defined to rudisha self

    >>> iter(g) is g
    True

Verify that the running flag is set properly

    >>> g = (me.gi_running for i in (0,1))
    >>> me = g
    >>> me.gi_running
    0
    >>> next(me)
    1
    >>> me.gi_running
    0

Verify that genexps are weakly referencable

    >>> agiza weakref
    >>> g = (i*i for i in range(4))
    >>> wr = weakref.ref(g)
    >>> wr() is g
    True
    >>> p = weakref.proxy(g)
    >>> list(p)
    [0, 1, 4, 9]


"""

agiza sys

# Trace function can throw off the tuple reuse test.
ikiwa hasattr(sys, 'gettrace') and sys.gettrace():
    __test__ = {}
else:
    __test__ = {'doctests' : doctests}

eleza test_main(verbose=None):
    kutoka test agiza support
    kutoka test agiza test_genexps
    support.run_doctest(test_genexps, verbose)

    # verify reference counting
    ikiwa verbose and hasattr(sys, "gettotalrefcount"):
        agiza gc
        counts = [None] * 5
        for i in range(len(counts)):
            support.run_doctest(test_genexps, verbose)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        andika(counts)

ikiwa __name__ == "__main__":
    test_main(verbose=True)
