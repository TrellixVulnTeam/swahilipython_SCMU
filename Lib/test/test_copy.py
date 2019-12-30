"""Unit tests kila the copy module."""

agiza copy
agiza copyreg
agiza weakref
agiza abc
kutoka operator agiza le, lt, ge, gt, eq, ne

agiza unittest

order_comparisons = le, lt, ge, gt
equality_comparisons = eq, ne
comparisons = order_comparisons + equality_comparisons

kundi TestCopy(unittest.TestCase):

    # Attempt full line coverage of copy.py kutoka top to bottom

    eleza test_exceptions(self):
        self.assertIs(copy.Error, copy.error)
        self.assertKweli(issubclass(copy.Error, Exception))

    # The copy() method

    eleza test_copy_basic(self):
        x = 42
        y = copy.copy(x)
        self.assertEqual(x, y)

    eleza test_copy_copy(self):
        kundi C(object):
            eleza __init__(self, foo):
                self.foo = foo
            eleza __copy__(self):
                rudisha C(self.foo)
        x = C(42)
        y = copy.copy(x)
        self.assertEqual(y.__class__, x.__class__)
        self.assertEqual(y.foo, x.foo)

    eleza test_copy_registry(self):
        kundi C(object):
            eleza __new__(cls, foo):
                obj = object.__new__(cls)
                obj.foo = foo
                rudisha obj
        eleza pickle_C(obj):
            rudisha (C, (obj.foo,))
        x = C(42)
        self.assertRaises(TypeError, copy.copy, x)
        copyreg.pickle(C, pickle_C, C)
        y = copy.copy(x)

    eleza test_copy_reduce_ex(self):
        kundi C(object):
            eleza __reduce_ex__(self, proto):
                c.append(1)
                rudisha ""
            eleza __reduce__(self):
                self.fail("shouldn't call this")
        c = []
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    eleza test_copy_reduce(self):
        kundi C(object):
            eleza __reduce__(self):
                c.append(1)
                rudisha ""
        c = []
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    eleza test_copy_cant(self):
        kundi C(object):
            eleza __getattribute__(self, name):
                ikiwa name.startswith("__reduce"):
                     ashiria AttributeError(name)
                rudisha object.__getattribute__(self, name)
        x = C()
        self.assertRaises(copy.Error, copy.copy, x)

    # Type-specific _copy_xxx() methods

    eleza test_copy_atomic(self):
        kundi Classic:
            pass
        kundi NewStyle(object):
            pass
        eleza f():
            pass
        kundi WithMetaclass(metaclass=abc.ABCMeta):
            pass
        tests = [Tupu, ..., NotImplemented,
                 42, 2**100, 3.14, Kweli, Uongo, 1j,
                 "hello", "hello\u1234", f.__code__,
                 b"world", bytes(range(256)), range(10), slice(1, 10, 2),
                 NewStyle, Classic, max, WithMetaclass]
        kila x kwenye tests:
            self.assertIs(copy.copy(x), x)

    eleza test_copy_list(self):
        x = [1, 2, 3]
        y = copy.copy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        x = []
        y = copy.copy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)

    eleza test_copy_tuple(self):
        x = (1, 2, 3)
        self.assertIs(copy.copy(x), x)
        x = ()
        self.assertIs(copy.copy(x), x)
        x = (1, 2, 3, [])
        self.assertIs(copy.copy(x), x)

    eleza test_copy_dict(self):
        x = {"foo": 1, "bar": 2}
        y = copy.copy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        x = {}
        y = copy.copy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)

    eleza test_copy_set(self):
        x = {1, 2, 3}
        y = copy.copy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        x = set()
        y = copy.copy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)

    eleza test_copy_frozenset(self):
        x = frozenset({1, 2, 3})
        self.assertIs(copy.copy(x), x)
        x = frozenset()
        self.assertIs(copy.copy(x), x)

    eleza test_copy_bytearray(self):
        x = bytearray(b'abc')
        y = copy.copy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        x = bytearray()
        y = copy.copy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)

    eleza test_copy_inst_vanilla(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    eleza test_copy_inst_copy(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __copy__(self):
                rudisha C(self.foo)
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    eleza test_copy_inst_getinitargs(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __getinitargs__(self):
                rudisha (self.foo,)
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    eleza test_copy_inst_getnewargs(self):
        kundi C(int):
            eleza __new__(cls, foo):
                self = int.__new__(cls)
                self.foo = foo
                rudisha self
            eleza __getnewargs__(self):
                rudisha self.foo,
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(42)
        y = copy.copy(x)
        self.assertIsInstance(y, C)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertEqual(y.foo, x.foo)

    eleza test_copy_inst_getnewargs_ex(self):
        kundi C(int):
            eleza __new__(cls, *, foo):
                self = int.__new__(cls)
                self.foo = foo
                rudisha self
            eleza __getnewargs_ex__(self):
                rudisha (), {'foo': self.foo}
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(foo=42)
        y = copy.copy(x)
        self.assertIsInstance(y, C)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertEqual(y.foo, x.foo)

    eleza test_copy_inst_getstate(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __getstate__(self):
                rudisha {"foo": self.foo}
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    eleza test_copy_inst_setstate(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __setstate__(self, state):
                self.foo = state["foo"]
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)

    eleza test_copy_inst_getstate_setstate(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __getstate__(self):
                rudisha self.foo
            eleza __setstate__(self, state):
                self.foo = state
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(42)
        self.assertEqual(copy.copy(x), x)
        # State ukijumuisha boolean value ni false (issue #25718)
        x = C(0.0)
        self.assertEqual(copy.copy(x), x)

    # The deepcopy() method

    eleza test_deepcopy_basic(self):
        x = 42
        y = copy.deepcopy(x)
        self.assertEqual(y, x)

    eleza test_deepcopy_memo(self):
        # Tests of reflexive objects are under type-specific sections below.
        # This tests only repetitions of objects.
        x = []
        x = [x, x]
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y[0], x[0])
        self.assertIs(y[0], y[1])

    eleza test_deepcopy_issubclass(self):
        # XXX Note: there's no way to test the TypeError coming out of
        # issubclass() -- this can only happen when an extension
        # module defines a "type" that doesn't formally inherit from
        # type.
        kundi Meta(type):
            pass
        kundi C(metaclass=Meta):
            pass
        self.assertEqual(copy.deepcopy(C), C)

    eleza test_deepcopy_deepcopy(self):
        kundi C(object):
            eleza __init__(self, foo):
                self.foo = foo
            eleza __deepcopy__(self, memo=Tupu):
                rudisha C(self.foo)
        x = C(42)
        y = copy.deepcopy(x)
        self.assertEqual(y.__class__, x.__class__)
        self.assertEqual(y.foo, x.foo)

    eleza test_deepcopy_registry(self):
        kundi C(object):
            eleza __new__(cls, foo):
                obj = object.__new__(cls)
                obj.foo = foo
                rudisha obj
        eleza pickle_C(obj):
            rudisha (C, (obj.foo,))
        x = C(42)
        self.assertRaises(TypeError, copy.deepcopy, x)
        copyreg.pickle(C, pickle_C, C)
        y = copy.deepcopy(x)

    eleza test_deepcopy_reduce_ex(self):
        kundi C(object):
            eleza __reduce_ex__(self, proto):
                c.append(1)
                rudisha ""
            eleza __reduce__(self):
                self.fail("shouldn't call this")
        c = []
        x = C()
        y = copy.deepcopy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    eleza test_deepcopy_reduce(self):
        kundi C(object):
            eleza __reduce__(self):
                c.append(1)
                rudisha ""
        c = []
        x = C()
        y = copy.deepcopy(x)
        self.assertIs(y, x)
        self.assertEqual(c, [1])

    eleza test_deepcopy_cant(self):
        kundi C(object):
            eleza __getattribute__(self, name):
                ikiwa name.startswith("__reduce"):
                     ashiria AttributeError(name)
                rudisha object.__getattribute__(self, name)
        x = C()
        self.assertRaises(copy.Error, copy.deepcopy, x)

    # Type-specific _deepcopy_xxx() methods

    eleza test_deepcopy_atomic(self):
        kundi Classic:
            pass
        kundi NewStyle(object):
            pass
        eleza f():
            pass
        tests = [Tupu, 42, 2**100, 3.14, Kweli, Uongo, 1j,
                 "hello", "hello\u1234", f.__code__,
                 NewStyle, Classic, max]
        kila x kwenye tests:
            self.assertIs(copy.deepcopy(x), x)

    eleza test_deepcopy_list(self):
        x = [[1, 2], 3]
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    eleza test_deepcopy_reflexive_list(self):
        x = []
        x.append(x)
        y = copy.deepcopy(x)
        kila op kwenye comparisons:
            self.assertRaises(RecursionError, op, y, x)
        self.assertIsNot(y, x)
        self.assertIs(y[0], y)
        self.assertEqual(len(y), 1)

    eleza test_deepcopy_empty_tuple(self):
        x = ()
        y = copy.deepcopy(x)
        self.assertIs(x, y)

    eleza test_deepcopy_tuple(self):
        x = ([1, 2], 3)
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    eleza test_deepcopy_tuple_of_immutables(self):
        x = ((1, 2), 3)
        y = copy.deepcopy(x)
        self.assertIs(x, y)

    eleza test_deepcopy_reflexive_tuple(self):
        x = ([],)
        x[0].append(x)
        y = copy.deepcopy(x)
        kila op kwenye comparisons:
            self.assertRaises(RecursionError, op, y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y[0], x[0])
        self.assertIs(y[0][0], y)

    eleza test_deepcopy_dict(self):
        x = {"foo": [1, 2], "bar": 3}
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(x, y)
        self.assertIsNot(x["foo"], y["foo"])

    eleza test_deepcopy_reflexive_dict(self):
        x = {}
        x['foo'] = x
        y = copy.deepcopy(x)
        kila op kwenye order_comparisons:
            self.assertRaises(TypeError, op, y, x)
        kila op kwenye equality_comparisons:
            self.assertRaises(RecursionError, op, y, x)
        self.assertIsNot(y, x)
        self.assertIs(y['foo'], y)
        self.assertEqual(len(y), 1)

    eleza test_deepcopy_keepalive(self):
        memo = {}
        x = []
        y = copy.deepcopy(x, memo)
        self.assertIs(memo[id(memo)][0], x)

    eleza test_deepcopy_dont_memo_immutable(self):
        memo = {}
        x = [1, 2, 3, 4]
        y = copy.deepcopy(x, memo)
        self.assertEqual(y, x)
        # There's the entry kila the new list, na the keep alive.
        self.assertEqual(len(memo), 2)

        memo = {}
        x = [(1, 2)]
        y = copy.deepcopy(x, memo)
        self.assertEqual(y, x)
        # Tuples ukijumuisha immutable contents are immutable kila deepcopy.
        self.assertEqual(len(memo), 2)

    eleza test_deepcopy_inst_vanilla(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y.foo, x.foo)

    eleza test_deepcopy_inst_deepcopy(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __deepcopy__(self, memo):
                rudisha C(copy.deepcopy(self.foo, memo))
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    eleza test_deepcopy_inst_getinitargs(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __getinitargs__(self):
                rudisha (self.foo,)
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    eleza test_deepcopy_inst_getnewargs(self):
        kundi C(int):
            eleza __new__(cls, foo):
                self = int.__new__(cls)
                self.foo = foo
                rudisha self
            eleza __getnewargs__(self):
                rudisha self.foo,
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertIsInstance(y, C)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertEqual(y.foo, x.foo)
        self.assertIsNot(y.foo, x.foo)

    eleza test_deepcopy_inst_getnewargs_ex(self):
        kundi C(int):
            eleza __new__(cls, *, foo):
                self = int.__new__(cls)
                self.foo = foo
                rudisha self
            eleza __getnewargs_ex__(self):
                rudisha (), {'foo': self.foo}
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C(foo=[42])
        y = copy.deepcopy(x)
        self.assertIsInstance(y, C)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertEqual(y.foo, x.foo)
        self.assertIsNot(y.foo, x.foo)

    eleza test_deepcopy_inst_getstate(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __getstate__(self):
                rudisha {"foo": self.foo}
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    eleza test_deepcopy_inst_setstate(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __setstate__(self, state):
                self.foo = state["foo"]
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    eleza test_deepcopy_inst_getstate_setstate(self):
        kundi C:
            eleza __init__(self, foo):
                self.foo = foo
            eleza __getstate__(self):
                rudisha self.foo
            eleza __setstate__(self, state):
                self.foo = state
            eleza __eq__(self, other):
                rudisha self.foo == other.foo
        x = C([42])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)
        # State ukijumuisha boolean value ni false (issue #25718)
        x = C([])
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y, x)
        self.assertIsNot(y.foo, x.foo)

    eleza test_deepcopy_reflexive_inst(self):
        kundi C:
            pass
        x = C()
        x.foo = x
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIs(y.foo, y)

    eleza test_deepcopy_range(self):
        kundi I(int):
            pass
        x = range(I(10))
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertEqual(y, x)
        self.assertIsNot(y.stop, x.stop)
        self.assertEqual(y.stop, x.stop)
        self.assertIsInstance(y.stop, I)

    # _reconstruct()

    eleza test_reconstruct_string(self):
        kundi C(object):
            eleza __reduce__(self):
                rudisha ""
        x = C()
        y = copy.copy(x)
        self.assertIs(y, x)
        y = copy.deepcopy(x)
        self.assertIs(y, x)

    eleza test_reconstruct_nostate(self):
        kundi C(object):
            eleza __reduce__(self):
                rudisha (C, ())
        x = C()
        x.foo = 42
        y = copy.copy(x)
        self.assertIs(y.__class__, x.__class__)
        y = copy.deepcopy(x)
        self.assertIs(y.__class__, x.__class__)

    eleza test_reconstruct_state(self):
        kundi C(object):
            eleza __reduce__(self):
                rudisha (C, (), self.__dict__)
            eleza __eq__(self, other):
                rudisha self.__dict__ == other.__dict__
        x = C()
        x.foo = [42]
        y = copy.copy(x)
        self.assertEqual(y, x)
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y.foo, x.foo)

    eleza test_reconstruct_state_setstate(self):
        kundi C(object):
            eleza __reduce__(self):
                rudisha (C, (), self.__dict__)
            eleza __setstate__(self, state):
                self.__dict__.update(state)
            eleza __eq__(self, other):
                rudisha self.__dict__ == other.__dict__
        x = C()
        x.foo = [42]
        y = copy.copy(x)
        self.assertEqual(y, x)
        y = copy.deepcopy(x)
        self.assertEqual(y, x)
        self.assertIsNot(y.foo, x.foo)

    eleza test_reconstruct_reflexive(self):
        kundi C(object):
            pass
        x = C()
        x.foo = x
        y = copy.deepcopy(x)
        self.assertIsNot(y, x)
        self.assertIs(y.foo, y)

    # Additions kila Python 2.3 na pickle protocol 2

    eleza test_reduce_4tuple(self):
        kundi C(list):
            eleza __reduce__(self):
                rudisha (C, (), self.__dict__, iter(self))
            eleza __eq__(self, other):
                rudisha (list(self) == list(other) and
                        self.__dict__ == other.__dict__)
        x = C([[1, 2], 3])
        y = copy.copy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIs(x[0], y[0])
        y = copy.deepcopy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    eleza test_reduce_5tuple(self):
        kundi C(dict):
            eleza __reduce__(self):
                rudisha (C, (), self.__dict__, Tupu, self.items())
            eleza __eq__(self, other):
                rudisha (dict(self) == dict(other) and
                        self.__dict__ == other.__dict__)
        x = C([("foo", [1, 2]), ("bar", 3)])
        y = copy.copy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIs(x["foo"], y["foo"])
        y = copy.deepcopy(x)
        self.assertEqual(x, y)
        self.assertIsNot(x, y)
        self.assertIsNot(x["foo"], y["foo"])

    eleza test_copy_slots(self):
        kundi C(object):
            __slots__ = ["foo"]
        x = C()
        x.foo = [42]
        y = copy.copy(x)
        self.assertIs(x.foo, y.foo)

    eleza test_deepcopy_slots(self):
        kundi C(object):
            __slots__ = ["foo"]
        x = C()
        x.foo = [42]
        y = copy.deepcopy(x)
        self.assertEqual(x.foo, y.foo)
        self.assertIsNot(x.foo, y.foo)

    eleza test_deepcopy_dict_subclass(self):
        kundi C(dict):
            eleza __init__(self, d=Tupu):
                ikiwa sio d:
                    d = {}
                self._keys = list(d.keys())
                super().__init__(d)
            eleza __setitem__(self, key, item):
                super().__setitem__(key, item)
                ikiwa key sio kwenye self._keys:
                    self._keys.append(key)
        x = C(d={'foo':0})
        y = copy.deepcopy(x)
        self.assertEqual(x, y)
        self.assertEqual(x._keys, y._keys)
        self.assertIsNot(x, y)
        x['bar'] = 1
        self.assertNotEqual(x, y)
        self.assertNotEqual(x._keys, y._keys)

    eleza test_copy_list_subclass(self):
        kundi C(list):
            pass
        x = C([[1, 2], 3])
        x.foo = [4, 5]
        y = copy.copy(x)
        self.assertEqual(list(x), list(y))
        self.assertEqual(x.foo, y.foo)
        self.assertIs(x[0], y[0])
        self.assertIs(x.foo, y.foo)

    eleza test_deepcopy_list_subclass(self):
        kundi C(list):
            pass
        x = C([[1, 2], 3])
        x.foo = [4, 5]
        y = copy.deepcopy(x)
        self.assertEqual(list(x), list(y))
        self.assertEqual(x.foo, y.foo)
        self.assertIsNot(x[0], y[0])
        self.assertIsNot(x.foo, y.foo)

    eleza test_copy_tuple_subclass(self):
        kundi C(tuple):
            pass
        x = C([1, 2, 3])
        self.assertEqual(tuple(x), (1, 2, 3))
        y = copy.copy(x)
        self.assertEqual(tuple(y), (1, 2, 3))

    eleza test_deepcopy_tuple_subclass(self):
        kundi C(tuple):
            pass
        x = C([[1, 2], 3])
        self.assertEqual(tuple(x), ([1, 2], 3))
        y = copy.deepcopy(x)
        self.assertEqual(tuple(y), ([1, 2], 3))
        self.assertIsNot(x, y)
        self.assertIsNot(x[0], y[0])

    eleza test_getstate_exc(self):
        kundi EvilState(object):
            eleza __getstate__(self):
                 ashiria ValueError("ain't got no stickin' state")
        self.assertRaises(ValueError, copy.copy, EvilState())

    eleza test_copy_function(self):
        self.assertEqual(copy.copy(global_foo), global_foo)
        eleza foo(x, y): rudisha x+y
        self.assertEqual(copy.copy(foo), foo)
        bar = lambda: Tupu
        self.assertEqual(copy.copy(bar), bar)

    eleza test_deepcopy_function(self):
        self.assertEqual(copy.deepcopy(global_foo), global_foo)
        eleza foo(x, y): rudisha x+y
        self.assertEqual(copy.deepcopy(foo), foo)
        bar = lambda: Tupu
        self.assertEqual(copy.deepcopy(bar), bar)

    eleza _check_weakref(self, _copy):
        kundi C(object):
            pass
        obj = C()
        x = weakref.ref(obj)
        y = _copy(x)
        self.assertIs(y, x)
        toa obj
        y = _copy(x)
        self.assertIs(y, x)

    eleza test_copy_weakref(self):
        self._check_weakref(copy.copy)

    eleza test_deepcopy_weakref(self):
        self._check_weakref(copy.deepcopy)

    eleza _check_copy_weakdict(self, _dicttype):
        kundi C(object):
            pass
        a, b, c, d = [C() kila i kwenye range(4)]
        u = _dicttype()
        u[a] = b
        u[c] = d
        v = copy.copy(u)
        self.assertIsNot(v, u)
        self.assertEqual(v, u)
        self.assertEqual(v[a], b)
        self.assertEqual(v[c], d)
        self.assertEqual(len(v), 2)
        toa c, d
        self.assertEqual(len(v), 1)
        x, y = C(), C()
        # The underlying containers are decoupled
        v[x] = y
        self.assertNotIn(x, u)

    eleza test_copy_weakkeydict(self):
        self._check_copy_weakdict(weakref.WeakKeyDictionary)

    eleza test_copy_weakvaluedict(self):
        self._check_copy_weakdict(weakref.WeakValueDictionary)

    eleza test_deepcopy_weakkeydict(self):
        kundi C(object):
            eleza __init__(self, i):
                self.i = i
        a, b, c, d = [C(i) kila i kwenye range(4)]
        u = weakref.WeakKeyDictionary()
        u[a] = b
        u[c] = d
        # Keys aren't copied, values are
        v = copy.deepcopy(u)
        self.assertNotEqual(v, u)
        self.assertEqual(len(v), 2)
        self.assertIsNot(v[a], b)
        self.assertIsNot(v[c], d)
        self.assertEqual(v[a].i, b.i)
        self.assertEqual(v[c].i, d.i)
        toa c
        self.assertEqual(len(v), 1)

    eleza test_deepcopy_weakvaluedict(self):
        kundi C(object):
            eleza __init__(self, i):
                self.i = i
        a, b, c, d = [C(i) kila i kwenye range(4)]
        u = weakref.WeakValueDictionary()
        u[a] = b
        u[c] = d
        # Keys are copied, values aren't
        v = copy.deepcopy(u)
        self.assertNotEqual(v, u)
        self.assertEqual(len(v), 2)
        (x, y), (z, t) = sorted(v.items(), key=lambda pair: pair[0].i)
        self.assertIsNot(x, a)
        self.assertEqual(x.i, a.i)
        self.assertIs(y, b)
        self.assertIsNot(z, c)
        self.assertEqual(z.i, c.i)
        self.assertIs(t, d)
        toa x, y, z, t
        toa d
        self.assertEqual(len(v), 1)

    eleza test_deepcopy_bound_method(self):
        kundi Foo(object):
            eleza m(self):
                pass
        f = Foo()
        f.b = f.m
        g = copy.deepcopy(f)
        self.assertEqual(g.m, g.b)
        self.assertIs(g.b.__self__, g)
        g.b()


eleza global_foo(x, y): rudisha x+y

ikiwa __name__ == "__main__":
    unittest.main()
