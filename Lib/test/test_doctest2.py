"""A module to test whether doctest recognizes some 2.2 features,
like static na kundi methods.

>>> andika('yup')  # 1
yup

We include some (random) encoded (utf-8) text kwenye the text surrounding
the example.  It should be ignored:

ЉЊЈЁЂ

"""

agiza sys
agiza unittest
kutoka test agiza support
ikiwa sys.flags.optimize >= 2:
    ashiria unittest.SkipTest("Cannot test docstrings ukijumuisha -O2")

kundi C(object):
    """Class C.

    >>> andika(C())  # 2
    42


    We include some (random) encoded (utf-8) text kwenye the text surrounding
    the example.  It should be ignored:

        ЉЊЈЁЂ

    """

    eleza __init__(self):
        """C.__init__.

        >>> andika(C()) # 3
        42
        """

    eleza __str__(self):
        """
        >>> andika(C()) # 4
        42
        """
        rudisha "42"

    kundi D(object):
        """A nested D class.

        >>> andika("In D!")   # 5
        In D!
        """

        eleza nested(self):
            """
            >>> andika(3) # 6
            3
            """

    eleza getx(self):
        """
        >>> c = C()    # 7
        >>> c.x = 12   # 8
        >>> andika(c.x)  # 9
        -12
        """
        rudisha -self._x

    eleza setx(self, value):
        """
        >>> c = C()     # 10
        >>> c.x = 12    # 11
        >>> andika(c.x)   # 12
        -12
        """
        self._x = value

    x = property(getx, setx, doc="""\
        >>> c = C()    # 13
        >>> c.x = 12   # 14
        >>> andika(c.x)  # 15
        -12
        """)

    @staticmethod
    eleza statm():
        """
        A static method.

        >>> andika(C.statm())    # 16
        666
        >>> andika(C().statm())  # 17
        666
        """
        rudisha 666

    @classmethod
    eleza clsm(cls, val):
        """
        A kundi method.

        >>> andika(C.clsm(22))    # 18
        22
        >>> andika(C().clsm(23))  # 19
        23
        """
        rudisha val

eleza test_main():
    kutoka test agiza test_doctest2
    EXPECTED = 19
    f, t = support.run_doctest(test_doctest2)
    ikiwa t != EXPECTED:
        ashiria support.TestFailed("expected %d tests to run, sio %d" %
                                      (EXPECTED, t))

# Pollute the namespace ukijumuisha a bunch of imported functions na classes,
# to make sure they don't get tested.
kutoka doctest agiza *

ikiwa __name__ == '__main__':
    test_main()
