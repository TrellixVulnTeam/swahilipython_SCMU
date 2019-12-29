doctests = """
########### Tests borrowed kutoka ama inspired by test_genexps.py ############

Test simple loop ukijumuisha conditional

    >>> sum([i*i kila i kwenye range(100) ikiwa i&1 == 1])
    166650

Test simple nesting

    >>> [(i,j) kila i kwenye range(3) kila j kwenye range(4)]
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]

Test nesting ukijumuisha the inner expression dependent on the outer

    >>> [(i,j) kila i kwenye range(4) kila j kwenye range(i)]
    [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2)]

Make sure the induction variable ni sio exposed

    >>> i = 20
    >>> sum([i*i kila i kwenye range(100)])
    328350

    >>> i
    20

Verify that syntax error's are ashiriad kila listcomps used kama lvalues

    >>> [y kila y kwenye (1,2)] = 10          # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    SyntaxError: ...

    >>> [y kila y kwenye (1,2)] += 10         # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
       ...
    SyntaxError: ...


########### Tests borrowed kutoka ama inspired by test_generators.py ############

Make a nested list comprehension that acts like range()

    >>> eleza frange(n):
    ...     rudisha [i kila i kwenye range(n)]
    >>> frange(10)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Same again, only kama a lambda expression instead of a function definition

    >>> lrange = lambda n:  [i kila i kwenye range(n)]
    >>> lrange(10)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Generators can call other generators:

    >>> eleza grange(n):
    ...     kila x kwenye [i kila i kwenye range(n)]:
    ...         tuma x
    >>> list(grange(5))
    [0, 1, 2, 3, 4]


Make sure that Tupu ni a valid rudisha value

    >>> [Tupu kila i kwenye range(10)]
    [Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, Tupu, Tupu]

########### Tests kila various scoping corner cases ############

Return lambdas that use the iteration variable kama a default argument

    >>> items = [(lambda i=i: i) kila i kwenye range(5)]
    >>> [x() kila x kwenye items]
    [0, 1, 2, 3, 4]

Same again, only this time kama a closure variable

    >>> items = [(lambda: i) kila i kwenye range(5)]
    >>> [x() kila x kwenye items]
    [4, 4, 4, 4, 4]

Another way to test that the iteration variable ni local to the list comp

    >>> items = [(lambda: i) kila i kwenye range(5)]
    >>> i = 20
    >>> [x() kila x kwenye items]
    [4, 4, 4, 4, 4]

And confirm that a closure can jump over the list comp scope

    >>> items = [(lambda: y) kila i kwenye range(5)]
    >>> y = 2
    >>> [x() kila x kwenye items]
    [2, 2, 2, 2, 2]

We also repeat each of the above scoping tests inside a function

    >>> eleza test_func():
    ...     items = [(lambda i=i: i) kila i kwenye range(5)]
    ...     rudisha [x() kila x kwenye items]
    >>> test_func()
    [0, 1, 2, 3, 4]

    >>> eleza test_func():
    ...     items = [(lambda: i) kila i kwenye range(5)]
    ...     rudisha [x() kila x kwenye items]
    >>> test_func()
    [4, 4, 4, 4, 4]

    >>> eleza test_func():
    ...     items = [(lambda: i) kila i kwenye range(5)]
    ...     i = 20
    ...     rudisha [x() kila x kwenye items]
    >>> test_func()
    [4, 4, 4, 4, 4]

    >>> eleza test_func():
    ...     items = [(lambda: y) kila i kwenye range(5)]
    ...     y = 2
    ...     rudisha [x() kila x kwenye items]
    >>> test_func()
    [2, 2, 2, 2, 2]

"""


__test__ = {'doctests' : doctests}

eleza test_main(verbose=Tupu):
    agiza sys
    kutoka test agiza support
    kutoka test agiza test_listcomps
    support.run_doctest(test_listcomps, verbose)

    # verify reference counting
    ikiwa verbose na hasattr(sys, "gettotalrefcount"):
        agiza gc
        counts = [Tupu] * 5
        kila i kwenye range(len(counts)):
            support.run_doctest(test_listcomps, verbose)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        andika(counts)

ikiwa __name__ == "__main__":
    test_main(verbose=Kweli)
