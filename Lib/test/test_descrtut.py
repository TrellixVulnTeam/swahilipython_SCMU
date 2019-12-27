# This contains most of the executable examples kutoka Guido's descr
# tutorial, once at
#
#     http://www.python.org/2.2/descrintro.html
#
# A few examples left implicit in the writeup were fleshed out, a few were
# skipped due to lack of interest (e.g., faking super() by hand isn't
# of much interest anymore), and a few were fiddled to make the output
# deterministic.

kutoka test.support agiza sortdict
agiza pprint

kundi defaultdict(dict):
    eleza __init__(self, default=None):
        dict.__init__(self)
        self.default = default

    eleza __getitem__(self, key):
        try:
            rudisha dict.__getitem__(self, key)
        except KeyError:
            rudisha self.default

    eleza get(self, key, *args):
        ikiwa not args:
            args = (self.default,)
        rudisha dict.get(self, key, *args)

    eleza merge(self, other):
        for key in other:
            ikiwa key not in self:
                self[key] = other[key]

test_1 = """

Here's the new type at work:

    >>> andika(defaultdict)              # show our type
    <kundi 'test.test_descrtut.defaultdict'>
    >>> andika(type(defaultdict))        # its metatype
    <kundi 'type'>
    >>> a = defaultdict(default=0.0)    # create an instance
    >>> andika(a)                        # show the instance
    {}
    >>> andika(type(a))                  # show its type
    <kundi 'test.test_descrtut.defaultdict'>
    >>> andika(a.__class__)              # show its class
    <kundi 'test.test_descrtut.defaultdict'>
    >>> andika(type(a) is a.__class__)   # its type is its class
    True
    >>> a[1] = 3.25                     # modify the instance
    >>> andika(a)                        # show the new value
    {1: 3.25}
    >>> andika(a[1])                     # show the new item
    3.25
    >>> andika(a[0])                     # a non-existent item
    0.0
    >>> a.merge({1:100, 2:200})         # use a dict method
    >>> andika(sortdict(a))              # show the result
    {1: 3.25, 2: 200}
    >>>

We can also use the new type in contexts where classic only allows "real"
dictionaries, such as the locals/globals dictionaries for the exec
statement or the built-in function eval():

    >>> andika(sorted(a.keys()))
    [1, 2]
    >>> a['print'] = print              # need the print function here
    >>> exec("x = 3; andika(x)", a)
    3
    >>> andika(sorted(a.keys(), key=lambda x: (str(type(x)), x)))
    [1, 2, '__builtins__', 'print', 'x']
    >>> andika(a['x'])
    3
    >>>

Now I'll show that defaultdict instances have dynamic instance variables,
just like classic classes:

    >>> a.default = -1
    >>> andika(a["noway"])
    -1
    >>> a.default = -1000
    >>> andika(a["noway"])
    -1000
    >>> 'default' in dir(a)
    True
    >>> a.x1 = 100
    >>> a.x2 = 200
    >>> andika(a.x1)
    100
    >>> d = dir(a)
    >>> 'default' in d and 'x1' in d and 'x2' in d
    True
    >>> andika(sortdict(a.__dict__))
    {'default': -1000, 'x1': 100, 'x2': 200}
    >>>
"""

kundi defaultdict2(dict):
    __slots__ = ['default']

    eleza __init__(self, default=None):
        dict.__init__(self)
        self.default = default

    eleza __getitem__(self, key):
        try:
            rudisha dict.__getitem__(self, key)
        except KeyError:
            rudisha self.default

    eleza get(self, key, *args):
        ikiwa not args:
            args = (self.default,)
        rudisha dict.get(self, key, *args)

    eleza merge(self, other):
        for key in other:
            ikiwa key not in self:
                self[key] = other[key]

test_2 = """

The __slots__ declaration takes a list of instance variables, and reserves
space for exactly these in the instance. When __slots__ is used, other
instance variables cannot be assigned to:

    >>> a = defaultdict2(default=0.0)
    >>> a[1]
    0.0
    >>> a.default = -1
    >>> a[1]
    -1
    >>> a.x1 = 1
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    AttributeError: 'defaultdict2' object has no attribute 'x1'
    >>>

"""

test_3 = """

Introspecting instances of built-in types

For instance of built-in types, x.__class__ is now the same as type(x):

    >>> type([])
    <kundi 'list'>
    >>> [].__class__
    <kundi 'list'>
    >>> list
    <kundi 'list'>
    >>> isinstance([], list)
    True
    >>> isinstance([], dict)
    False
    >>> isinstance([], object)
    True
    >>>

You can get the information kutoka the list type:

    >>> pprint.pandika(dir(list))    # like list.__dict__.keys(), but sorted
    ['__add__',
     '__class__',
     '__contains__',
     '__delattr__',
     '__delitem__',
     '__dir__',
     '__doc__',
     '__eq__',
     '__format__',
     '__ge__',
     '__getattribute__',
     '__getitem__',
     '__gt__',
     '__hash__',
     '__iadd__',
     '__imul__',
     '__init__',
     '__init_subclass__',
     '__iter__',
     '__le__',
     '__len__',
     '__lt__',
     '__mul__',
     '__ne__',
     '__new__',
     '__reduce__',
     '__reduce_ex__',
     '__repr__',
     '__reversed__',
     '__rmul__',
     '__setattr__',
     '__setitem__',
     '__sizeof__',
     '__str__',
     '__subclasshook__',
     'append',
     'clear',
     'copy',
     'count',
     'extend',
     'index',
     'insert',
     'pop',
     'remove',
     'reverse',
     'sort']

The new introspection API gives more information than the old one:  in
addition to the regular methods, it also shows the methods that are
normally invoked through special notations, e.g. __iadd__ (+=), __len__
(len), __ne__ (!=). You can invoke any method kutoka this list directly:

    >>> a = ['tic', 'tac']
    >>> list.__len__(a)          # same as len(a)
    2
    >>> a.__len__()              # ditto
    2
    >>> list.append(a, 'toe')    # same as a.append('toe')
    >>> a
    ['tic', 'tac', 'toe']
    >>>

This is just like it is for user-defined classes.
"""

test_4 = """

Static methods and kundi methods

The new introspection API makes it possible to add static methods and class
methods. Static methods are easy to describe: they behave pretty much like
static methods in C++ or Java. Here's an example:

    >>> kundi C:
    ...
    ...     @staticmethod
    ...     eleza foo(x, y):
    ...         andika("staticmethod", x, y)

    >>> C.foo(1, 2)
    staticmethod 1 2
    >>> c = C()
    >>> c.foo(1, 2)
    staticmethod 1 2

Class methods use a similar pattern to declare methods that receive an
implicit first argument that is the *class* for which they are invoked.

    >>> kundi C:
    ...     @classmethod
    ...     eleza foo(cls, y):
    ...         andika("classmethod", cls, y)

    >>> C.foo(1)
    classmethod <kundi 'test.test_descrtut.C'> 1
    >>> c = C()
    >>> c.foo(1)
    classmethod <kundi 'test.test_descrtut.C'> 1

    >>> kundi D(C):
    ...     pass

    >>> D.foo(1)
    classmethod <kundi 'test.test_descrtut.D'> 1
    >>> d = D()
    >>> d.foo(1)
    classmethod <kundi 'test.test_descrtut.D'> 1

This prints "classmethod __main__.D 1" both times; in other words, the
kundi passed as the first argument of foo() is the kundi involved in the
call, not the kundi involved in the definition of foo().

But notice this:

    >>> kundi E(C):
    ...     @classmethod
    ...     eleza foo(cls, y): # override C.foo
    ...         andika("E.foo() called")
    ...         C.foo(y)

    >>> E.foo(1)
    E.foo() called
    classmethod <kundi 'test.test_descrtut.C'> 1
    >>> e = E()
    >>> e.foo(1)
    E.foo() called
    classmethod <kundi 'test.test_descrtut.C'> 1

In this example, the call to C.foo() kutoka E.foo() will see kundi C as its
first argument, not kundi E. This is to be expected, since the call
specifies the kundi C. But it stresses the difference between these class
methods and methods defined in metaclasses (where an upcall to a metamethod
would pass the target kundi as an explicit first argument).
"""

test_5 = """

Attributes defined by get/set methods


    >>> kundi property(object):
    ...
    ...     eleza __init__(self, get, set=None):
    ...         self.__get = get
    ...         self.__set = set
    ...
    ...     eleza __get__(self, inst, type=None):
    ...         rudisha self.__get(inst)
    ...
    ...     eleza __set__(self, inst, value):
    ...         ikiwa self.__set is None:
    ...             raise AttributeError("this attribute is read-only")
    ...         rudisha self.__set(inst, value)

Now let's define a kundi with an attribute x defined by a pair of methods,
getx() and setx():

    >>> kundi C(object):
    ...
    ...     eleza __init__(self):
    ...         self.__x = 0
    ...
    ...     eleza getx(self):
    ...         rudisha self.__x
    ...
    ...     eleza setx(self, x):
    ...         ikiwa x < 0: x = 0
    ...         self.__x = x
    ...
    ...     x = property(getx, setx)

Here's a small demonstration:

    >>> a = C()
    >>> a.x = 10
    >>> andika(a.x)
    10
    >>> a.x = -10
    >>> andika(a.x)
    0
    >>>

Hmm -- property is builtin now, so let's try it that way too.

    >>> del property  # unmask the builtin
    >>> property
    <kundi 'property'>

    >>> kundi C(object):
    ...     eleza __init__(self):
    ...         self.__x = 0
    ...     eleza getx(self):
    ...         rudisha self.__x
    ...     eleza setx(self, x):
    ...         ikiwa x < 0: x = 0
    ...         self.__x = x
    ...     x = property(getx, setx)


    >>> a = C()
    >>> a.x = 10
    >>> andika(a.x)
    10
    >>> a.x = -10
    >>> andika(a.x)
    0
    >>>
"""

test_6 = """

Method resolution order

This example is implicit in the writeup.

>>> kundi A:    # implicit new-style class
...     eleza save(self):
...         andika("called A.save()")
>>> kundi B(A):
...     pass
>>> kundi C(A):
...     eleza save(self):
...         andika("called C.save()")
>>> kundi D(B, C):
...     pass

>>> D().save()
called C.save()

>>> kundi A(object):  # explicit new-style class
...     eleza save(self):
...         andika("called A.save()")
>>> kundi B(A):
...     pass
>>> kundi C(A):
...     eleza save(self):
...         andika("called C.save()")
>>> kundi D(B, C):
...     pass

>>> D().save()
called C.save()
"""

kundi A(object):
    eleza m(self):
        rudisha "A"

kundi B(A):
    eleza m(self):
        rudisha "B" + super(B, self).m()

kundi C(A):
    eleza m(self):
        rudisha "C" + super(C, self).m()

kundi D(C, B):
    eleza m(self):
        rudisha "D" + super(D, self).m()


test_7 = """

Cooperative methods and "super"

>>> andika(D().m()) # "DCBA"
DCBA
"""

test_8 = """

Backwards incompatibilities

>>> kundi A:
...     eleza foo(self):
...         andika("called A.foo()")

>>> kundi B(A):
...     pass

>>> kundi C(A):
...     eleza foo(self):
...         B.foo(self)

>>> C().foo()
called A.foo()

>>> kundi C(A):
...     eleza foo(self):
...         A.foo(self)
>>> C().foo()
called A.foo()
"""

__test__ = {"tut1": test_1,
            "tut2": test_2,
            "tut3": test_3,
            "tut4": test_4,
            "tut5": test_5,
            "tut6": test_6,
            "tut7": test_7,
            "tut8": test_8}

# Magic test name that regrtest.py invokes *after* agizaing this module.
# This worms around a bootstrap problem.
# Note that doctest and regrtest both look in sys.argv for a "-v" argument,
# so this works as expected in both ways of running regrtest.
eleza test_main(verbose=None):
    # Obscure:  agiza this module as test.test_descrtut instead of as
    # plain test_descrtut because the name of this module works its way
    # into the doctest examples, and unless the full test.test_descrtut
    # business is used the name can change depending on how the test is
    # invoked.
    kutoka test agiza support, test_descrtut
    support.run_doctest(test_descrtut, verbose)

# This part isn't needed for regrtest, but for running the test directly.
ikiwa __name__ == "__main__":
    test_main(1)
