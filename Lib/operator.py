"""
Operator Interface

This module exports a set of functions corresponding to the intrinsic
operators of Python.  For example, operator.add(x, y) is equivalent
to the expression x+y.  The function names are those used for special
methods; variants without leading and trailing '__' are also provided
for convenience.

This is the pure Python implementation of the module.
"""

__all__ = ['abs', 'add', 'and_', 'attrgetter', 'concat', 'contains', 'countOf',
           'delitem', 'eq', 'floordiv', 'ge', 'getitem', 'gt', 'iadd', 'iand',
           'iconcat', 'ifloordiv', 'ilshift', 'imatmul', 'imod', 'imul',
           'index', 'indexOf', 'inv', 'invert', 'ior', 'ipow', 'irshift',
           'is_', 'is_not', 'isub', 'itemgetter', 'itruediv', 'ixor', 'le',
           'length_hint', 'lshift', 'lt', 'matmul', 'methodcaller', 'mod',
           'mul', 'ne', 'neg', 'not_', 'or_', 'pos', 'pow', 'rshift',
           'setitem', 'sub', 'truediv', 'truth', 'xor']

kutoka builtins agiza abs as _abs


# Comparison Operations *******************************************************#

eleza lt(a, b):
    "Same as a < b."
    rudisha a < b

eleza le(a, b):
    "Same as a <= b."
    rudisha a <= b

eleza eq(a, b):
    "Same as a == b."
    rudisha a == b

eleza ne(a, b):
    "Same as a != b."
    rudisha a != b

eleza ge(a, b):
    "Same as a >= b."
    rudisha a >= b

eleza gt(a, b):
    "Same as a > b."
    rudisha a > b

# Logical Operations **********************************************************#

eleza not_(a):
    "Same as not a."
    rudisha not a

eleza truth(a):
    "Return True ikiwa a is true, False otherwise."
    rudisha True ikiwa a else False

eleza is_(a, b):
    "Same as a is b."
    rudisha a is b

eleza is_not(a, b):
    "Same as a is not b."
    rudisha a is not b

# Mathematical/Bitwise Operations *********************************************#

eleza abs(a):
    "Same as abs(a)."
    rudisha _abs(a)

eleza add(a, b):
    "Same as a + b."
    rudisha a + b

eleza and_(a, b):
    "Same as a & b."
    rudisha a & b

eleza floordiv(a, b):
    "Same as a // b."
    rudisha a // b

eleza index(a):
    "Same as a.__index__()."
    rudisha a.__index__()

eleza inv(a):
    "Same as ~a."
    rudisha ~a
invert = inv

eleza lshift(a, b):
    "Same as a << b."
    rudisha a << b

eleza mod(a, b):
    "Same as a % b."
    rudisha a % b

eleza mul(a, b):
    "Same as a * b."
    rudisha a * b

eleza matmul(a, b):
    "Same as a @ b."
    rudisha a @ b

eleza neg(a):
    "Same as -a."
    rudisha -a

eleza or_(a, b):
    "Same as a | b."
    rudisha a | b

eleza pos(a):
    "Same as +a."
    rudisha +a

eleza pow(a, b):
    "Same as a ** b."
    rudisha a ** b

eleza rshift(a, b):
    "Same as a >> b."
    rudisha a >> b

eleza sub(a, b):
    "Same as a - b."
    rudisha a - b

eleza truediv(a, b):
    "Same as a / b."
    rudisha a / b

eleza xor(a, b):
    "Same as a ^ b."
    rudisha a ^ b

# Sequence Operations *********************************************************#

eleza concat(a, b):
    "Same as a + b, for a and b sequences."
    ikiwa not hasattr(a, '__getitem__'):
        msg = "'%s' object can't be concatenated" % type(a).__name__
        raise TypeError(msg)
    rudisha a + b

eleza contains(a, b):
    "Same as b in a (note reversed operands)."
    rudisha b in a

eleza countOf(a, b):
    "Return the number of times b occurs in a."
    count = 0
    for i in a:
        ikiwa i == b:
            count += 1
    rudisha count

eleza delitem(a, b):
    "Same as del a[b]."
    del a[b]

eleza getitem(a, b):
    "Same as a[b]."
    rudisha a[b]

eleza indexOf(a, b):
    "Return the first index of b in a."
    for i, j in enumerate(a):
        ikiwa j == b:
            rudisha i
    else:
        raise ValueError('sequence.index(x): x not in sequence')

eleza setitem(a, b, c):
    "Same as a[b] = c."
    a[b] = c

eleza length_hint(obj, default=0):
    """
    Return an estimate of the number of items in obj.
    This is useful for presizing containers when building kutoka an iterable.

    If the object supports len(), the result will be exact. Otherwise, it may
    over- or under-estimate by an arbitrary amount. The result will be an
    integer >= 0.
    """
    ikiwa not isinstance(default, int):
        msg = ("'%s' object cannot be interpreted as an integer" %
               type(default).__name__)
        raise TypeError(msg)

    try:
        rudisha len(obj)
    except TypeError:
        pass

    try:
        hint = type(obj).__length_hint__
    except AttributeError:
        rudisha default

    try:
        val = hint(obj)
    except TypeError:
        rudisha default
    ikiwa val is NotImplemented:
        rudisha default
    ikiwa not isinstance(val, int):
        msg = ('__length_hint__ must be integer, not %s' %
               type(val).__name__)
        raise TypeError(msg)
    ikiwa val < 0:
        msg = '__length_hint__() should rudisha >= 0'
        raise ValueError(msg)
    rudisha val

# Generalized Lookup Objects **************************************************#

kundi attrgetter:
    """
    Return a callable object that fetches the given attribute(s) kutoka its operand.
    After f = attrgetter('name'), the call f(r) returns r.name.
    After g = attrgetter('name', 'date'), the call g(r) returns (r.name, r.date).
    After h = attrgetter('name.first', 'name.last'), the call h(r) returns
    (r.name.first, r.name.last).
    """
    __slots__ = ('_attrs', '_call')

    eleza __init__(self, attr, *attrs):
        ikiwa not attrs:
            ikiwa not isinstance(attr, str):
                raise TypeError('attribute name must be a string')
            self._attrs = (attr,)
            names = attr.split('.')
            eleza func(obj):
                for name in names:
                    obj = getattr(obj, name)
                rudisha obj
            self._call = func
        else:
            self._attrs = (attr,) + attrs
            getters = tuple(map(attrgetter, self._attrs))
            eleza func(obj):
                rudisha tuple(getter(obj) for getter in getters)
            self._call = func

    eleza __call__(self, obj):
        rudisha self._call(obj)

    eleza __repr__(self):
        rudisha '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              ', '.join(map(repr, self._attrs)))

    eleza __reduce__(self):
        rudisha self.__class__, self._attrs

kundi itemgetter:
    """
    Return a callable object that fetches the given item(s) kutoka its operand.
    After f = itemgetter(2), the call f(r) returns r[2].
    After g = itemgetter(2, 5, 3), the call g(r) returns (r[2], r[5], r[3])
    """
    __slots__ = ('_items', '_call')

    eleza __init__(self, item, *items):
        ikiwa not items:
            self._items = (item,)
            eleza func(obj):
                rudisha obj[item]
            self._call = func
        else:
            self._items = items = (item,) + items
            eleza func(obj):
                rudisha tuple(obj[i] for i in items)
            self._call = func

    eleza __call__(self, obj):
        rudisha self._call(obj)

    eleza __repr__(self):
        rudisha '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__name__,
                              ', '.join(map(repr, self._items)))

    eleza __reduce__(self):
        rudisha self.__class__, self._items

kundi methodcaller:
    """
    Return a callable object that calls the given method on its operand.
    After f = methodcaller('name'), the call f(r) returns r.name().
    After g = methodcaller('name', 'date', foo=1), the call g(r) returns
    r.name('date', foo=1).
    """
    __slots__ = ('_name', '_args', '_kwargs')

    eleza __init__(self, name, /, *args, **kwargs):
        self._name = name
        ikiwa not isinstance(self._name, str):
            raise TypeError('method name must be a string')
        self._args = args
        self._kwargs = kwargs

    eleza __call__(self, obj):
        rudisha getattr(obj, self._name)(*self._args, **self._kwargs)

    eleza __repr__(self):
        args = [repr(self._name)]
        args.extend(map(repr, self._args))
        args.extend('%s=%r' % (k, v) for k, v in self._kwargs.items())
        rudisha '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__name__,
                              ', '.join(args))

    eleza __reduce__(self):
        ikiwa not self._kwargs:
            rudisha self.__class__, (self._name,) + self._args
        else:
            kutoka functools agiza partial
            rudisha partial(self.__class__, self._name, **self._kwargs), self._args


# In-place Operations *********************************************************#

eleza iadd(a, b):
    "Same as a += b."
    a += b
    rudisha a

eleza iand(a, b):
    "Same as a &= b."
    a &= b
    rudisha a

eleza iconcat(a, b):
    "Same as a += b, for a and b sequences."
    ikiwa not hasattr(a, '__getitem__'):
        msg = "'%s' object can't be concatenated" % type(a).__name__
        raise TypeError(msg)
    a += b
    rudisha a

eleza ifloordiv(a, b):
    "Same as a //= b."
    a //= b
    rudisha a

eleza ilshift(a, b):
    "Same as a <<= b."
    a <<= b
    rudisha a

eleza imod(a, b):
    "Same as a %= b."
    a %= b
    rudisha a

eleza imul(a, b):
    "Same as a *= b."
    a *= b
    rudisha a

eleza imatmul(a, b):
    "Same as a @= b."
    a @= b
    rudisha a

eleza ior(a, b):
    "Same as a |= b."
    a |= b
    rudisha a

eleza ipow(a, b):
    "Same as a **= b."
    a **=b
    rudisha a

eleza irshift(a, b):
    "Same as a >>= b."
    a >>= b
    rudisha a

eleza isub(a, b):
    "Same as a -= b."
    a -= b
    rudisha a

eleza itruediv(a, b):
    "Same as a /= b."
    a /= b
    rudisha a

eleza ixor(a, b):
    "Same as a ^= b."
    a ^= b
    rudisha a


try:
    kutoka _operator agiza *
except ImportError:
    pass
else:
    kutoka _operator agiza __doc__

# All of these "__func__ = func" assignments have to happen after agizaing
# kutoka _operator to make sure they're set to the right function
__lt__ = lt
__le__ = le
__eq__ = eq
__ne__ = ne
__ge__ = ge
__gt__ = gt
__not__ = not_
__abs__ = abs
__add__ = add
__and__ = and_
__floordiv__ = floordiv
__index__ = index
__inv__ = inv
__invert__ = invert
__lshift__ = lshift
__mod__ = mod
__mul__ = mul
__matmul__ = matmul
__neg__ = neg
__or__ = or_
__pos__ = pos
__pow__ = pow
__rshift__ = rshift
__sub__ = sub
__truediv__ = truediv
__xor__ = xor
__concat__ = concat
__contains__ = contains
__delitem__ = delitem
__getitem__ = getitem
__setitem__ = setitem
__iadd__ = iadd
__iand__ = iand
__iconcat__ = iconcat
__ifloordiv__ = ifloordiv
__ilshift__ = ilshift
__imod__ = imod
__imul__ = imul
__imatmul__ = imatmul
__ior__ = ior
__ipow__ = ipow
__irshift__ = irshift
__isub__ = isub
__itruediv__ = itruediv
__ixor__ = ixor
