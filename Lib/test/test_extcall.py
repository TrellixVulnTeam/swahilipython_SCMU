
"""Doctest kila method/function calls.

We're going the use these types kila extra testing

    >>> kutoka collections agiza UserList
    >>> kutoka collections agiza UserDict

We're defining four helper functions

    >>> eleza e(a,b):
    ...     andika(a, b)

    >>> eleza f(*a, **k):
    ...     andika(a, support.sortdict(k))

    >>> eleza g(x, *y, **z):
    ...     andika(x, y, support.sortdict(z))

    >>> eleza h(j=1, a=2, h=3):
    ...     andika(j, a, h)

Argument list examples

    >>> f()
    () {}
    >>> f(1)
    (1,) {}
    >>> f(1, 2)
    (1, 2) {}
    >>> f(1, 2, 3)
    (1, 2, 3) {}
    >>> f(1, 2, 3, *(4, 5))
    (1, 2, 3, 4, 5) {}
    >>> f(1, 2, 3, *[4, 5])
    (1, 2, 3, 4, 5) {}
    >>> f(*[1, 2, 3], 4, 5)
    (1, 2, 3, 4, 5) {}
    >>> f(1, 2, 3, *UserList([4, 5]))
    (1, 2, 3, 4, 5) {}
    >>> f(1, 2, 3, *[4, 5], *[6, 7])
    (1, 2, 3, 4, 5, 6, 7) {}
    >>> f(1, *[2, 3], 4, *[5, 6], 7)
    (1, 2, 3, 4, 5, 6, 7) {}
    >>> f(*UserList([1, 2]), *UserList([3, 4]), 5, *UserList([6, 7]))
    (1, 2, 3, 4, 5, 6, 7) {}

Here we add keyword arguments

    >>> f(1, 2, 3, **{'a':4, 'b':5})
    (1, 2, 3) {'a': 4, 'b': 5}
    >>> f(1, 2, **{'a': -1, 'b': 5}, **{'a': 4, 'c': 6})
    Traceback (most recent call last):
        ...
    TypeError: f() got multiple values kila keyword argument 'a'
    >>> f(1, 2, **{'a': -1, 'b': 5}, a=4, c=6)
    Traceback (most recent call last):
        ...
    TypeError: f() got multiple values kila keyword argument 'a'
    >>> f(1, 2, a=3, **{'a': 4}, **{'a': 5})
    Traceback (most recent call last):
        ...
    TypeError: f() got multiple values kila keyword argument 'a'
    >>> f(1, 2, 3, *[4, 5], **{'a':6, 'b':7})
    (1, 2, 3, 4, 5) {'a': 6, 'b': 7}
    >>> f(1, 2, 3, x=4, y=5, *(6, 7), **{'a':8, 'b': 9})
    (1, 2, 3, 6, 7) {'a': 8, 'b': 9, 'x': 4, 'y': 5}
    >>> f(1, 2, 3, *[4, 5], **{'c': 8}, **{'a':6, 'b':7})
    (1, 2, 3, 4, 5) {'a': 6, 'b': 7, 'c': 8}
    >>> f(1, 2, 3, *(4, 5), x=6, y=7, **{'a':8, 'b': 9})
    (1, 2, 3, 4, 5) {'a': 8, 'b': 9, 'x': 6, 'y': 7}

    >>> f(1, 2, 3, **UserDict(a=4, b=5))
    (1, 2, 3) {'a': 4, 'b': 5}
    >>> f(1, 2, 3, *(4, 5), **UserDict(a=6, b=7))
    (1, 2, 3, 4, 5) {'a': 6, 'b': 7}
    >>> f(1, 2, 3, x=4, y=5, *(6, 7), **UserDict(a=8, b=9))
    (1, 2, 3, 6, 7) {'a': 8, 'b': 9, 'x': 4, 'y': 5}
    >>> f(1, 2, 3, *(4, 5), x=6, y=7, **UserDict(a=8, b=9))
    (1, 2, 3, 4, 5) {'a': 8, 'b': 9, 'x': 6, 'y': 7}

Examples ukijumuisha invalid arguments (TypeErrors). We're also testing the function
names kwenye the exception messages.

Verify clearing of SF bug #733667

    >>> e(c=4)
    Traceback (most recent call last):
      ...
    TypeError: e() got an unexpected keyword argument 'c'

    >>> g()
    Traceback (most recent call last):
      ...
    TypeError: g() missing 1 required positional argument: 'x'

    >>> g(*())
    Traceback (most recent call last):
      ...
    TypeError: g() missing 1 required positional argument: 'x'

    >>> g(*(), **{})
    Traceback (most recent call last):
      ...
    TypeError: g() missing 1 required positional argument: 'x'

    >>> g(1)
    1 () {}
    >>> g(1, 2)
    1 (2,) {}
    >>> g(1, 2, 3)
    1 (2, 3) {}
    >>> g(1, 2, 3, *(4, 5))
    1 (2, 3, 4, 5) {}

    >>> kundi Nothing: pass
    ...
    >>> g(*Nothing())
    Traceback (most recent call last):
      ...
    TypeError: g() argument after * must be an iterable, sio Nothing

    >>> kundi Nothing:
    ...     eleza __len__(self): rudisha 5
    ...

    >>> g(*Nothing())
    Traceback (most recent call last):
      ...
    TypeError: g() argument after * must be an iterable, sio Nothing

    >>> kundi Nothing():
    ...     eleza __len__(self): rudisha 5
    ...     eleza __getitem__(self, i):
    ...         ikiwa i<3: rudisha i
    ...         isipokua:  ashiria IndexError(i)
    ...

    >>> g(*Nothing())
    0 (1, 2) {}

    >>> kundi Nothing:
    ...     eleza __init__(self): self.c = 0
    ...     eleza __iter__(self): rudisha self
    ...     eleza __next__(self):
    ...         ikiwa self.c == 4:
    ...              ashiria StopIteration
    ...         c = self.c
    ...         self.c += 1
    ...         rudisha c
    ...

    >>> g(*Nothing())
    0 (1, 2, 3) {}

Check kila issue #4806: Does a TypeError kwenye a generator get propagated ukijumuisha the
right error message? (Also check ukijumuisha other iterables.)

    >>> eleza broken():  ashiria TypeError("myerror")
    ...

    >>> g(*(broken() kila i kwenye range(1)))
    Traceback (most recent call last):
      ...
    TypeError: myerror
    >>> g(*range(1), *(broken() kila i kwenye range(1)))
    Traceback (most recent call last):
      ...
    TypeError: myerror

    >>> kundi BrokenIterable1:
    ...     eleza __iter__(self):
    ...          ashiria TypeError('myerror')
    ...
    >>> g(*BrokenIterable1())
    Traceback (most recent call last):
      ...
    TypeError: myerror
    >>> g(*range(1), *BrokenIterable1())
    Traceback (most recent call last):
      ...
    TypeError: myerror

    >>> kundi BrokenIterable2:
    ...     eleza __iter__(self):
    ...         tuma 0
    ...          ashiria TypeError('myerror')
    ...
    >>> g(*BrokenIterable2())
    Traceback (most recent call last):
      ...
    TypeError: myerror
    >>> g(*range(1), *BrokenIterable2())
    Traceback (most recent call last):
      ...
    TypeError: myerror

    >>> kundi BrokenSequence:
    ...     eleza __getitem__(self, idx):
    ...          ashiria TypeError('myerror')
    ...
    >>> g(*BrokenSequence())
    Traceback (most recent call last):
      ...
    TypeError: myerror
    >>> g(*range(1), *BrokenSequence())
    Traceback (most recent call last):
      ...
    TypeError: myerror

Make sure that the function doesn't stomp the dictionary

    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> d2 = d.copy()
    >>> g(1, d=4, **d)
    1 () {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> d == d2
    Kweli

What about willful misconduct?

    >>> eleza saboteur(**kw):
    ...     kw['x'] = 'm'
    ...     rudisha kw

    >>> d = {}
    >>> kw = saboteur(a=1, **d)
    >>> d
    {}


    >>> g(1, 2, 3, **{'x': 4, 'y': 5})
    Traceback (most recent call last):
      ...
    TypeError: g() got multiple values kila argument 'x'

    >>> f(**{1:2})
    Traceback (most recent call last):
      ...
    TypeError: f() keywords must be strings

    >>> h(**{'e': 2})
    Traceback (most recent call last):
      ...
    TypeError: h() got an unexpected keyword argument 'e'

    >>> h(*h)
    Traceback (most recent call last):
      ...
    TypeError: h() argument after * must be an iterable, sio function

    >>> h(1, *h)
    Traceback (most recent call last):
      ...
    TypeError: h() argument after * must be an iterable, sio function

    >>> h(*[1], *h)
    Traceback (most recent call last):
      ...
    TypeError: h() argument after * must be an iterable, sio function

    >>> dir(*h)
    Traceback (most recent call last):
      ...
    TypeError: dir() argument after * must be an iterable, sio function

    >>> nothing = Tupu
    >>> nothing(*h)
    Traceback (most recent call last):
      ...
    TypeError: TupuType object argument after * must be an iterable, \
not function

    >>> h(**h)
    Traceback (most recent call last):
      ...
    TypeError: h() argument after ** must be a mapping, sio function

    >>> h(**[])
    Traceback (most recent call last):
      ...
    TypeError: h() argument after ** must be a mapping, sio list

    >>> h(a=1, **h)
    Traceback (most recent call last):
      ...
    TypeError: h() argument after ** must be a mapping, sio function

    >>> h(a=1, **[])
    Traceback (most recent call last):
      ...
    TypeError: h() argument after ** must be a mapping, sio list

    >>> h(**{'a': 1}, **h)
    Traceback (most recent call last):
      ...
    TypeError: h() argument after ** must be a mapping, sio function

    >>> h(**{'a': 1}, **[])
    Traceback (most recent call last):
      ...
    TypeError: h() argument after ** must be a mapping, sio list

    >>> dir(**h)
    Traceback (most recent call last):
      ...
    TypeError: dir() argument after ** must be a mapping, sio function

    >>> nothing(**h)
    Traceback (most recent call last):
      ...
    TypeError: TupuType object argument after ** must be a mapping, \
not function

    >>> dir(b=1, **{'b': 1})
    Traceback (most recent call last):
      ...
    TypeError: dir() got multiple values kila keyword argument 'b'

Test a kwargs mapping ukijumuisha duplicated keys.

    >>> kutoka collections.abc agiza Mapping
    >>> kundi MultiDict(Mapping):
    ...     eleza __init__(self, items):
    ...         self._items = items
    ...
    ...     eleza __iter__(self):
    ...         rudisha (k kila k, v kwenye self._items)
    ...
    ...     eleza __getitem__(self, key):
    ...         kila k, v kwenye self._items:
    ...             ikiwa k == key:
    ...                 rudisha v
    ...          ashiria KeyError(key)
    ...
    ...     eleza __len__(self):
    ...         rudisha len(self._items)
    ...
    ...     eleza keys(self):
    ...         rudisha [k kila k, v kwenye self._items]
    ...
    ...     eleza values(self):
    ...         rudisha [v kila k, v kwenye self._items]
    ...
    ...     eleza items(self):
    ...         rudisha [(k, v) kila k, v kwenye self._items]
    ...
    >>> g(**MultiDict([('x', 1), ('y', 2)]))
    1 () {'y': 2}

    >>> g(**MultiDict([('x', 1), ('x', 2)]))
    Traceback (most recent call last):
      ...
    TypeError: g() got multiple values kila keyword argument 'x'

    >>> g(a=3, **MultiDict([('x', 1), ('x', 2)]))
    Traceback (most recent call last):
      ...
    TypeError: g() got multiple values kila keyword argument 'x'

    >>> g(**MultiDict([('a', 3)]), **MultiDict([('x', 1), ('x', 2)]))
    Traceback (most recent call last):
      ...
    TypeError: g() got multiple values kila keyword argument 'x'

Another helper function

    >>> eleza f2(*a, **b):
    ...     rudisha a, b


    >>> d = {}
    >>> kila i kwenye range(512):
    ...     key = 'k%d' % i
    ...     d[key] = i
    >>> a, b = f2(1, *(2,3), **d)
    >>> len(a), len(b), b == d
    (3, 512, Kweli)

    >>> kundi Foo:
    ...     eleza method(self, arg1, arg2):
    ...         rudisha arg1+arg2

    >>> x = Foo()
    >>> Foo.method(*(x, 1, 2))
    3
    >>> Foo.method(x, *(1, 2))
    3
    >>> Foo.method(*(1, 2, 3))
    5
    >>> Foo.method(1, *[2, 3])
    5

A PyCFunction that takes only positional parameters should allow an
empty keyword dictionary to pass without a complaint, but  ashiria a
TypeError ikiwa te dictionary ni sio empty

    >>> jaribu:
    ...     silence = id(1, *{})
    ...     Kweli
    ... tatizo:
    ...     Uongo
    Kweli

    >>> id(1, **{'foo': 1})
    Traceback (most recent call last):
      ...
    TypeError: id() takes no keyword arguments

A corner case of keyword dictionary items being deleted during
the function call setup. See <http://bugs.python.org/issue2016>.

    >>> kundi Name(str):
    ...     eleza __eq__(self, other):
    ...         jaribu:
    ...              toa x[self]
    ...         except KeyError:
    ...              pass
    ...         rudisha str.__eq__(self, other)
    ...     eleza __hash__(self):
    ...         rudisha str.__hash__(self)

    >>> x = {Name("a"):1, Name("b"):2}
    >>> eleza f(a, b):
    ...     andika(a,b)
    >>> f(**x)
    1 2

Too many arguments:

    >>> eleza f(): pass
    >>> f(1)
    Traceback (most recent call last):
      ...
    TypeError: f() takes 0 positional arguments but 1 was given
    >>> eleza f(a): pass
    >>> f(1, 2)
    Traceback (most recent call last):
      ...
    TypeError: f() takes 1 positional argument but 2 were given
    >>> eleza f(a, b=1): pass
    >>> f(1, 2, 3)
    Traceback (most recent call last):
      ...
    TypeError: f() takes kutoka 1 to 2 positional arguments but 3 were given
    >>> eleza f(*, kw): pass
    >>> f(1, kw=3)
    Traceback (most recent call last):
      ...
    TypeError: f() takes 0 positional arguments but 1 positional argument (and 1 keyword-only argument) were given
    >>> eleza f(*, kw, b): pass
    >>> f(1, 2, 3, b=3, kw=3)
    Traceback (most recent call last):
      ...
    TypeError: f() takes 0 positional arguments but 3 positional arguments (and 2 keyword-only arguments) were given
    >>> eleza f(a, b=2, *, kw): pass
    >>> f(2, 3, 4, kw=4)
    Traceback (most recent call last):
      ...
    TypeError: f() takes kutoka 1 to 2 positional arguments but 3 positional arguments (and 1 keyword-only argument) were given

Too few na missing arguments:

    >>> eleza f(a): pass
    >>> f()
    Traceback (most recent call last):
      ...
    TypeError: f() missing 1 required positional argument: 'a'
    >>> eleza f(a, b): pass
    >>> f()
    Traceback (most recent call last):
      ...
    TypeError: f() missing 2 required positional arguments: 'a' na 'b'
    >>> eleza f(a, b, c): pass
    >>> f()
    Traceback (most recent call last):
      ...
    TypeError: f() missing 3 required positional arguments: 'a', 'b', na 'c'
    >>> eleza f(a, b, c, d, e): pass
    >>> f()
    Traceback (most recent call last):
      ...
    TypeError: f() missing 5 required positional arguments: 'a', 'b', 'c', 'd', na 'e'
    >>> eleza f(a, b=4, c=5, d=5): pass
    >>> f(c=12, b=9)
    Traceback (most recent call last):
      ...
    TypeError: f() missing 1 required positional argument: 'a'

Same ukijumuisha keyword only args:

    >>> eleza f(*, w): pass
    >>> f()
    Traceback (most recent call last):
      ...
    TypeError: f() missing 1 required keyword-only argument: 'w'
    >>> eleza f(*, a, b, c, d, e): pass
    >>> f()
    Traceback (most recent call last):
      ...
    TypeError: f() missing 5 required keyword-only arguments: 'a', 'b', 'c', 'd', na 'e'

"""

agiza sys
kutoka test agiza support

eleza test_main():
    support.run_doctest(sys.modules[__name__], Kweli)

ikiwa __name__ == '__main__':
    test_main()
