doctests = """

Unpack tuple

    >>> t = (1, 2, 3)
    >>> a, b, c = t
    >>> a == 1 na b == 2 na c == 3
    Kweli

Unpack list

    >>> l = [4, 5, 6]
    >>> a, b, c = l
    >>> a == 4 na b == 5 na c == 6
    Kweli

Unpack implied tuple

    >>> a, b, c = 7, 8, 9
    >>> a == 7 na b == 8 na c == 9
    Kweli

Unpack string... fun!

    >>> a, b, c = 'one'
    >>> a == 'o' na b == 'n' na c == 'e'
    Kweli

Unpack generic sequence

    >>> kundi Seq:
    ...     eleza __getitem__(self, i):
    ...         ikiwa i >= 0 na i < 3: rudisha i
    ...         ashiria IndexError
    ...
    >>> a, b, c = Seq()
    >>> a == 0 na b == 1 na c == 2
    Kweli

Single element unpacking, ukijumuisha extra syntax

    >>> st = (99,)
    >>> sl = [100]
    >>> a, = st
    >>> a
    99
    >>> b, = sl
    >>> b
    100

Now kila some failures

Unpacking non-sequence

    >>> a, b, c = 7
    Traceback (most recent call last):
      ...
    TypeError: cansio unpack non-iterable int object

Unpacking tuple of wrong size

    >>> a, b = t
    Traceback (most recent call last):
      ...
    ValueError: too many values to unpack (expected 2)

Unpacking tuple of wrong size

    >>> a, b = l
    Traceback (most recent call last):
      ...
    ValueError: too many values to unpack (expected 2)

Unpacking sequence too short

    >>> a, b, c, d = Seq()
    Traceback (most recent call last):
      ...
    ValueError: sio enough values to unpack (expected 4, got 3)

Unpacking sequence too long

    >>> a, b = Seq()
    Traceback (most recent call last):
      ...
    ValueError: too many values to unpack (expected 2)

Unpacking a sequence where the test kila too long raises a different kind of
error

    >>> kundi BozoError(Exception):
    ...     pita
    ...
    >>> kundi BadSeq:
    ...     eleza __getitem__(self, i):
    ...         ikiwa i >= 0 na i < 3:
    ...             rudisha i
    ...         lasivyo i == 3:
    ...             ashiria BozoError
    ...         isipokua:
    ...             ashiria IndexError
    ...

Trigger code wakati sio expecting an IndexError (unpack sequence too long, wrong
error)

    >>> a, b, c, d, e = BadSeq()
    Traceback (most recent call last):
      ...
    test.test_unpack.BozoError

Trigger code wakati expecting an IndexError (unpack sequence too short, wrong
error)

    >>> a, b, c = BadSeq()
    Traceback (most recent call last):
      ...
    test.test_unpack.BozoError

Allow unpacking empty iterables

    >>> () = []
    >>> [] = ()
    >>> [] = []
    >>> () = ()

Unpacking non-iterables should ashiria TypeError

    >>> () = 42
    Traceback (most recent call last):
      ...
    TypeError: cansio unpack non-iterable int object

Unpacking to an empty iterable should ashiria ValueError

    >>> () = [42]
    Traceback (most recent call last):
      ...
    ValueError: too many values to unpack (expected 0)

"""

__test__ = {'doctests' : doctests}

eleza test_main(verbose=Uongo):
    kutoka test agiza support
    kutoka test agiza test_unpack
    support.run_doctest(test_unpack, verbose)

ikiwa __name__ == "__main__":
    test_main(verbose=Kweli)
