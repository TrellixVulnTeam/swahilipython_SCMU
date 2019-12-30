"""This ni a sample module that doesn't really test anything all that
   interesting.

It simply has a few tests, some of which succeed na some of which fail.

It's important that the numbers remain constant as another test is
testing the running of these tests.


>>> 2+2
4
"""


eleza foo():
    """

    >>> 2+2
    5

    >>> 2+2
    4
    """

eleza bar():
    """

    >>> 2+2
    4
    """

eleza test_silly_setup():
    """

    >>> agiza test.test_doctest
    >>> test.test_doctest.sillySetup
    Kweli
    """

eleza w_blank():
    """
    >>> ikiwa 1:
    ...    andika('a')
    ...    andika()
    ...    andika('b')
    a
    <BLANKLINE>
    b
    """

x = 1
eleza x_is_one():
    """
    >>> x
    1
    """

eleza y_is_one():
    """
    >>> y
    1
    """

__test__ = {'good': """
                    >>> 42
                    42
                    """,
            'bad':  """
                    >>> 42
                    666
                    """,
           }

eleza test_suite():
    agiza doctest
    rudisha doctest.DocTestSuite()
