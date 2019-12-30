doctests = """

Basic kundi construction.

    >>> kundi C:
    ...     eleza meth(self): andika("Hello")
    ...
    >>> C.__class__ ni type
    Kweli
    >>> a = C()
    >>> a.__class__ ni C
    Kweli
    >>> a.meth()
    Hello
    >>>

Use *args notation kila the bases.

    >>> kundi A: pita
    >>> kundi B: pita
    >>> bases = (A, B)
    >>> kundi C(*bases): pita
    >>> C.__bases__ == bases
    Kweli
    >>>

Use a trivial metaclass.

    >>> kundi M(type):
    ...     pita
    ...
    >>> kundi C(metaclass=M):
    ...    eleza meth(self): andika("Hello")
    ...
    >>> C.__class__ ni M
    Kweli
    >>> a = C()
    >>> a.__class__ ni C
    Kweli
    >>> a.meth()
    Hello
    >>>

Use **kwds notation kila the metakundi keyword.

    >>> kwds = {'metaclass': M}
    >>> kundi C(**kwds): pita
    ...
    >>> C.__class__ ni M
    Kweli
    >>> a = C()
    >>> a.__class__ ni C
    Kweli
    >>>

Use a metakundi ukijumuisha a __prepare__ static method.

    >>> kundi M(type):
    ...    @staticmethod
    ...    eleza __prepare__(*args, **kwds):
    ...        andika("Prepare called:", args, kwds)
    ...        rudisha dict()
    ...    eleza __new__(cls, name, bases, namespace, **kwds):
    ...        andika("New called:", kwds)
    ...        rudisha type.__new__(cls, name, bases, namespace)
    ...    eleza __init__(cls, *args, **kwds):
    ...        pita
    ...
    >>> kundi C(metaclass=M):
    ...     eleza meth(self): andika("Hello")
    ...
    Prepare called: ('C', ()) {}
    New called: {}
    >>>

Also pita another keyword.

    >>> kundi C(object, metaclass=M, other="haha"):
    ...     pita
    ...
    Prepare called: ('C', (<kundi 'object'>,)) {'other': 'haha'}
    New called: {'other': 'haha'}
    >>> C.__class__ ni M
    Kweli
    >>> C.__bases__ == (object,)
    Kweli
    >>> a = C()
    >>> a.__class__ ni C
    Kweli
    >>>

Check that build_kundi doesn't mutate the kwds dict.

    >>> kwds = {'metaclass': type}
    >>> kundi C(**kwds): pita
    ...
    >>> kwds == {'metaclass': type}
    Kweli
    >>>

Use various combinations of explicit keywords na **kwds.

    >>> bases = (object,)
    >>> kwds = {'metaclass': M, 'other': 'haha'}
    >>> kundi C(*bases, **kwds): pita
    ...
    Prepare called: ('C', (<kundi 'object'>,)) {'other': 'haha'}
    New called: {'other': 'haha'}
    >>> C.__class__ ni M
    Kweli
    >>> C.__bases__ == (object,)
    Kweli
    >>> kundi B: pita
    >>> kwds = {'other': 'haha'}
    >>> kundi C(B, metaclass=M, *bases, **kwds): pita
    ...
    Prepare called: ('C', (<kundi 'test.test_metaclass.B'>, <kundi 'object'>)) {'other': 'haha'}
    New called: {'other': 'haha'}
    >>> C.__class__ ni M
    Kweli
    >>> C.__bases__ == (B, object)
    Kweli
    >>>

Check kila duplicate keywords.

    >>> kundi C(metaclass=type, metaclass=type): pita
    ...
    Traceback (most recent call last):
    [...]
    SyntaxError: keyword argument repeated
    >>>

Another way.

    >>> kwds = {'metaclass': type}
    >>> kundi C(metaclass=type, **kwds): pita
    ...
    Traceback (most recent call last):
    [...]
    TypeError: __build_class__() got multiple values kila keyword argument 'metaclass'
    >>>

Use a __prepare__ method that returns an instrumented dict.

    >>> kundi LoggingDict(dict):
    ...     eleza __setitem__(self, key, value):
    ...         andika("d[%r] = %r" % (key, value))
    ...         dict.__setitem__(self, key, value)
    ...
    >>> kundi Meta(type):
    ...    @staticmethod
    ...    eleza __prepare__(name, bases):
    ...        rudisha LoggingDict()
    ...
    >>> kundi C(metaclass=Meta):
    ...     foo = 2+2
    ...     foo = 42
    ...     bar = 123
    ...
    d['__module__'] = 'test.test_metaclass'
    d['__qualname__'] = 'C'
    d['foo'] = 4
    d['foo'] = 42
    d['bar'] = 123
    >>>

Use a metakundi that doesn't derive kutoka type.

    >>> eleza meta(name, bases, namespace, **kwds):
    ...     andika("meta:", name, bases)
    ...     andika("ns:", sorted(namespace.items()))
    ...     andika("kw:", sorted(kwds.items()))
    ...     rudisha namespace
    ...
    >>> kundi C(metaclass=meta):
    ...     a = 42
    ...     b = 24
    ...
    meta: C ()
    ns: [('__module__', 'test.test_metaclass'), ('__qualname__', 'C'), ('a', 42), ('b', 24)]
    kw: []
    >>> type(C) ni dict
    Kweli
    >>> andika(sorted(C.items()))
    [('__module__', 'test.test_metaclass'), ('__qualname__', 'C'), ('a', 42), ('b', 24)]
    >>>

And again, ukijumuisha a __prepare__ attribute.

    >>> eleza prepare(name, bases, **kwds):
    ...     andika("prepare:", name, bases, sorted(kwds.items()))
    ...     rudisha LoggingDict()
    ...
    >>> meta.__prepare__ = prepare
    >>> kundi C(metaclass=meta, other="booh"):
    ...    a = 1
    ...    a = 2
    ...    b = 3
    ...
    prepare: C () [('other', 'booh')]
    d['__module__'] = 'test.test_metaclass'
    d['__qualname__'] = 'C'
    d['a'] = 1
    d['a'] = 2
    d['b'] = 3
    meta: C ()
    ns: [('__module__', 'test.test_metaclass'), ('__qualname__', 'C'), ('a', 2), ('b', 3)]
    kw: [('other', 'booh')]
    >>>

The default metakundi must define a __prepare__() method.

    >>> type.__prepare__()
    {}
    >>>

Make sure it works ukijumuisha subclassing.

    >>> kundi M(type):
    ...     @classmethod
    ...     eleza __prepare__(cls, *args, **kwds):
    ...         d = super().__prepare__(*args, **kwds)
    ...         d["hello"] = 42
    ...         rudisha d
    ...
    >>> kundi C(metaclass=M):
    ...     andika(hello)
    ...
    42
    >>> andika(C.hello)
    42
    >>>

Test failures kwenye looking up the __prepare__ method work.
    >>> kundi ObscureException(Exception):
    ...     pita
    >>> kundi FailDescr:
    ...     eleza __get__(self, instance, owner):
    ...        ashiria ObscureException
    >>> kundi Meta(type):
    ...     __prepare__ = FailDescr()
    >>> kundi X(metaclass=Meta):
    ...     pita
    Traceback (most recent call last):
    [...]
    test.test_metaclass.ObscureException

"""

agiza sys

# Trace function introduces __locals__ which causes various tests to fail.
ikiwa hasattr(sys, 'gettrace') na sys.gettrace():
    __test__ = {}
isipokua:
    __test__ = {'doctests' : doctests}

eleza test_main(verbose=Uongo):
    kutoka test agiza support
    kutoka test agiza test_metaclass
    support.run_doctest(test_metaclass, verbose)

ikiwa __name__ == "__main__":
    test_main(verbose=Kweli)
