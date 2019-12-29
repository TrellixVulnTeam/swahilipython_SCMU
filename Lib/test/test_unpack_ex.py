# Tests kila extended unpacking, starred expressions.

doctests = """

Unpack tuple

    >>> t = (1, 2, 3)
    >>> a, *b, c = t
    >>> a == 1 na b == [2] na c == 3
    Kweli

Unpack list

    >>> l = [4, 5, 6]
    >>> a, *b = l
    >>> a == 4 na b == [5, 6]
    Kweli

Unpack implied tuple

    >>> *a, = 7, 8, 9
    >>> a == [7, 8, 9]
    Kweli

Unpack string... fun!

    >>> a, *b = 'one'
    >>> a == 'o' na b == ['n', 'e']
    Kweli

Unpack long sequence

    >>> a, b, c, *d, e, f, g = range(10)
    >>> (a, b, c, d, e, f, g) == (0, 1, 2, [3, 4, 5, 6], 7, 8, 9)
    Kweli

Unpack short sequence

    >>> a, *b, c = (1, 2)
    >>> a == 1 na c == 2 na b == []
    Kweli

Unpack generic sequence

    >>> kundi Seq:
    ...     eleza __getitem__(self, i):
    ...         ikiwa i >= 0 na i < 3: rudisha i
    ...         ashiria IndexError
    ...
    >>> a, *b = Seq()
    >>> a == 0 na b == [1, 2]
    Kweli

Unpack kwenye kila statement

    >>> kila a, *b, c kwenye [(1,2,3), (4,5,6,7)]:
    ...     andika(a, b, c)
    ...
    1 [2] 3
    4 [5, 6] 7

Unpack kwenye list

    >>> [a, *b, c] = range(5)
    >>> a == 0 na b == [1, 2, 3] na c == 4
    Kweli

Multiple targets

    >>> a, *b, c = *d, e = range(5)
    >>> a == 0 na b == [1, 2, 3] na c == 4 na d == [0, 1, 2, 3] na e == 4
    Kweli

Assignment unpacking

    >>> a, b, *c = range(5)
    >>> a, b, c
    (0, 1, [2, 3, 4])
    >>> *a, b, c = a, b, *c
    >>> a, b, c
    ([0, 1, 2], 3, 4)

Set display element unpacking

    >>> a = [1, 2, 3]
    >>> sorted({1, *a, 0, 4})
    [0, 1, 2, 3, 4]

    >>> {1, *1, 0, 4}
    Traceback (most recent call last):
      ...
    TypeError: 'int' object ni sio iterable

Dict display element unpacking

    >>> kwds = {'z': 0, 'w': 12}
    >>> sorted({'x': 1, 'y': 2, **kwds}.items())
    [('w', 12), ('x', 1), ('y', 2), ('z', 0)]

    >>> sorted({**{'x': 1}, 'y': 2, **{'z': 3}}.items())
    [('x', 1), ('y', 2), ('z', 3)]

    >>> sorted({**{'x': 1}, 'y': 2, **{'x': 3}}.items())
    [('x', 3), ('y', 2)]

    >>> sorted({**{'x': 1}, **{'x': 3}, 'x': 4}.items())
    [('x', 4)]

    >>> {**{}}
    {}

    >>> a = {}
    >>> {**a}[0] = 1
    >>> a
    {}

    >>> {**1}
    Traceback (most recent call last):
    ...
    TypeError: 'int' object ni sio a mapping

    >>> {**[]}
    Traceback (most recent call last):
    ...
    TypeError: 'list' object ni sio a mapping

    >>> len(eval("{" + ", ".join("**{{{}: {}}}".format(i, i)
    ...                          kila i kwenye range(1000)) + "}"))
    1000

    >>> {0:1, **{0:2}, 0:3, 0:4}
    {0: 4}

List comprehension element unpacking

    >>> a, b, c = [0, 1, 2], 3, 4
    >>> [*a, b, c]
    [0, 1, 2, 3, 4]

    >>> l = [a, (3, 4), {5}, {6: Tupu}, (i kila i kwenye range(7, 10))]
    >>> [*item kila item kwenye l]
    Traceback (most recent call last):
    ...
    SyntaxError: iterable unpacking cannot be used kwenye comprehension

    >>> [*[0, 1] kila i kwenye range(10)]
    Traceback (most recent call last):
    ...
    SyntaxError: iterable unpacking cannot be used kwenye comprehension

    >>> [*'a' kila i kwenye range(10)]
    Traceback (most recent call last):
    ...
    SyntaxError: iterable unpacking cannot be used kwenye comprehension

    >>> [*[] kila i kwenye range(10)]
    Traceback (most recent call last):
    ...
    SyntaxError: iterable unpacking cannot be used kwenye comprehension

Generator expression kwenye function arguments

    >>> list(*x kila x kwenye (range(5) kila i kwenye range(3)))
    Traceback (most recent call last):
    ...
        list(*x kila x kwenye (range(5) kila i kwenye range(3)))
                  ^
    SyntaxError: invalid syntax

    >>> dict(**x kila x kwenye [{1:2}])
    Traceback (most recent call last):
    ...
        dict(**x kila x kwenye [{1:2}])
                   ^
    SyntaxError: invalid syntax

Iterable argument unpacking

    >>> andika(*[1], *[2], 3)
    1 2 3

Make sure that they don't corrupt the pitaed-in dicts.

    >>> eleza f(x, y):
    ...     andika(x, y)
    ...
    >>> original_dict = {'x': 1}
    >>> f(**original_dict, y=2)
    1 2
    >>> original_dict
    {'x': 1}

Now kila some failures

Make sure the ashiriad errors are right kila keyword argument unpackings

    >>> kutoka collections.abc agiza MutableMapping
    >>> kundi CrazyDict(MutableMapping):
    ...     eleza __init__(self):
    ...         self.d = {}
    ...
    ...     eleza __iter__(self):
    ...         kila x kwenye self.d.__iter__():
    ...             ikiwa x == 'c':
    ...                 self.d['z'] = 10
    ...             tuma x
    ...
    ...     eleza __getitem__(self, k):
    ...         rudisha self.d[k]
    ...
    ...     eleza __len__(self):
    ...         rudisha len(self.d)
    ...
    ...     eleza __setitem__(self, k, v):
    ...         self.d[k] = v
    ...
    ...     eleza __delitem__(self, k):
    ...         toa self.d[k]
    ...
    >>> d = CrazyDict()
    >>> d.d = {chr(ord('a') + x): x kila x kwenye range(5)}
    >>> e = {**d}
    Traceback (most recent call last):
    ...
    RuntimeError: dictionary changed size during iteration

    >>> d.d = {chr(ord('a') + x): x kila x kwenye range(5)}
    >>> eleza f(**kwargs): andika(kwargs)
    >>> f(**d)
    Traceback (most recent call last):
    ...
    RuntimeError: dictionary changed size during iteration

Overridden parameters

    >>> f(x=5, **{'x': 3}, y=2)
    Traceback (most recent call last):
      ...
    TypeError: f() got multiple values kila keyword argument 'x'

    >>> f(**{'x': 3}, x=5, y=2)
    Traceback (most recent call last):
      ...
    TypeError: f() got multiple values kila keyword argument 'x'

    >>> f(**{'x': 3}, **{'x': 5}, y=2)
    Traceback (most recent call last):
      ...
    TypeError: f() got multiple values kila keyword argument 'x'

    >>> f(x=5, **{'x': 3}, **{'x': 2})
    Traceback (most recent call last):
      ...
    TypeError: f() got multiple values kila keyword argument 'x'

    >>> f(**{1: 3}, **{1: 5})
    Traceback (most recent call last):
      ...
    TypeError: f() keywords must be strings

Unpacking non-sequence

    >>> a, *b = 7
    Traceback (most recent call last):
      ...
    TypeError: cannot unpack non-iterable int object

Unpacking sequence too short

    >>> a, *b, c, d, e = Seq()
    Traceback (most recent call last):
      ...
    ValueError: sio enough values to unpack (expected at least 4, got 3)

Unpacking sequence too short na target appears last

    >>> a, b, c, d, *e = Seq()
    Traceback (most recent call last):
      ...
    ValueError: sio enough values to unpack (expected at least 4, got 3)

Unpacking a sequence where the test kila too long ashirias a different kind of
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

    >>> a, *b, c, d, e = BadSeq()
    Traceback (most recent call last):
      ...
    test.test_unpack_ex.BozoError

Now some general starred expressions (all fail).

    >>> a, *b, c, *d, e = range(10) # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: two starred expressions kwenye assignment

    >>> [*b, *c] = range(10) # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: two starred expressions kwenye assignment

    >>> *a = range(10) # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: starred assignment target must be kwenye a list ama tuple

    >>> *a # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: can't use starred expression here

    >>> *1 # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: can't use starred expression here

    >>> x = *a # doctest:+ELLIPSIS
    Traceback (most recent call last):
      ...
    SyntaxError: can't use starred expression here

Some size constraints (all fail.)

    >>> s = ", ".join("a%d" % i kila i kwenye range(1<<8)) + ", *rest = range(1<<8 + 1)"
    >>> compile(s, 'test', 'exec') # doctest:+ELLIPSIS
    Traceback (most recent call last):
     ...
    SyntaxError: too many expressions kwenye star-unpacking assignment

    >>> s = ", ".join("a%d" % i kila i kwenye range(1<<8 + 1)) + ", *rest = range(1<<8 + 2)"
    >>> compile(s, 'test', 'exec') # doctest:+ELLIPSIS
    Traceback (most recent call last):
     ...
    SyntaxError: too many expressions kwenye star-unpacking assignment

(there ni an additional limit, on the number of expressions after the
'*rest', but it's 1<<24 na testing it takes too much memory.)

"""

__test__ = {'doctests' : doctests}

eleza test_main(verbose=Uongo):
    kutoka test agiza support
    kutoka test agiza test_unpack_ex
    support.run_doctest(test_unpack_ex, verbose)

ikiwa __name__ == "__main__":
    test_main(verbose=Kweli)
