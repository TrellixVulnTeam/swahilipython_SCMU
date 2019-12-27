doctests = """
########### Tests mostly copied kutoka test_listcomps.py ############

Test simple loop with conditional

    >>> sum({i*i for i in range(100) ikiwa i&1 == 1})
    166650

Test simple case

    >>> {2*y + x + 1 for x in (0,) for y in (1,)}
    {3}

Test simple nesting

    >>> list(sorted({(i,j) for i in range(3) for j in range(4)}))
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]

Test nesting with the inner expression dependent on the outer

    >>> list(sorted({(i,j) for i in range(4) for j in range(i)}))
    [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2)]

Make sure the induction variable is not exposed

    >>> i = 20
    >>> sum({i*i for i in range(100)})
    328350

    >>> i
    20

Verify that syntax error's are raised for setcomps used as lvalues

    >>> {y for y in (1,2)} = 10          # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    SyntaxError: ...

    >>> {y for y in (1,2)} += 10         # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    SyntaxError: ...


Make a nested set comprehension that acts like set(range())

    >>> eleza srange(n):
    ...     rudisha {i for i in range(n)}
    >>> list(sorted(srange(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Same again, only as a lambda expression instead of a function definition

    >>> lrange = lambda n:  {i for i in range(n)}
    >>> list(sorted(lrange(10)))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Generators can call other generators:

    >>> eleza grange(n):
    ...     for x in {i for i in range(n)}:
    ...         yield x
    >>> list(sorted(grange(5)))
    [0, 1, 2, 3, 4]


Make sure that None is a valid rudisha value

    >>> {None for i in range(10)}
    {None}

########### Tests for various scoping corner cases ############

Return lambdas that use the iteration variable as a default argument

    >>> items = {(lambda i=i: i) for i in range(5)}
    >>> {x() for x in items} == set(range(5))
    True

Same again, only this time as a closure variable

    >>> items = {(lambda: i) for i in range(5)}
    >>> {x() for x in items}
    {4}

Another way to test that the iteration variable is local to the list comp

    >>> items = {(lambda: i) for i in range(5)}
    >>> i = 20
    >>> {x() for x in items}
    {4}

And confirm that a closure can jump over the list comp scope

    >>> items = {(lambda: y) for i in range(5)}
    >>> y = 2
    >>> {x() for x in items}
    {2}

We also repeat each of the above scoping tests inside a function

    >>> eleza test_func():
    ...     items = {(lambda i=i: i) for i in range(5)}
    ...     rudisha {x() for x in items}
    >>> test_func() == set(range(5))
    True

    >>> eleza test_func():
    ...     items = {(lambda: i) for i in range(5)}
    ...     rudisha {x() for x in items}
    >>> test_func()
    {4}

    >>> eleza test_func():
    ...     items = {(lambda: i) for i in range(5)}
    ...     i = 20
    ...     rudisha {x() for x in items}
    >>> test_func()
    {4}

    >>> eleza test_func():
    ...     items = {(lambda: y) for i in range(5)}
    ...     y = 2
    ...     rudisha {x() for x in items}
    >>> test_func()
    {2}

"""


__test__ = {'doctests' : doctests}

eleza test_main(verbose=None):
    agiza sys
    kutoka test agiza support
    kutoka test agiza test_setcomps
    support.run_doctest(test_setcomps, verbose)

    # verify reference counting
    ikiwa verbose and hasattr(sys, "gettotalrefcount"):
        agiza gc
        counts = [None] * 5
        for i in range(len(counts)):
            support.run_doctest(test_setcomps, verbose)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        andika(counts)

ikiwa __name__ == "__main__":
    test_main(verbose=True)
