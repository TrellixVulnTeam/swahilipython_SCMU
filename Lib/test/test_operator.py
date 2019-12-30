agiza unittest
agiza pickle
agiza sys

kutoka test agiza support

py_operator = support.import_fresh_module('operator', blocked=['_operator'])
c_operator = support.import_fresh_module('operator', fresh=['_operator'])

kundi Seq1:
    eleza __init__(self, lst):
        self.lst = lst
    eleza __len__(self):
        rudisha len(self.lst)
    eleza __getitem__(self, i):
        rudisha self.lst[i]
    eleza __add__(self, other):
        rudisha self.lst + other.lst
    eleza __mul__(self, other):
        rudisha self.lst * other
    eleza __rmul__(self, other):
        rudisha other * self.lst

kundi Seq2(object):
    eleza __init__(self, lst):
        self.lst = lst
    eleza __len__(self):
        rudisha len(self.lst)
    eleza __getitem__(self, i):
        rudisha self.lst[i]
    eleza __add__(self, other):
        rudisha self.lst + other.lst
    eleza __mul__(self, other):
        rudisha self.lst * other
    eleza __rmul__(self, other):
        rudisha other * self.lst


kundi OperatorTestCase:
    eleza test_lt(self):
        operator = self.module
        self.assertRaises(TypeError, operator.lt)
        self.assertRaises(TypeError, operator.lt, 1j, 2j)
        self.assertUongo(operator.lt(1, 0))
        self.assertUongo(operator.lt(1, 0.0))
        self.assertUongo(operator.lt(1, 1))
        self.assertUongo(operator.lt(1, 1.0))
        self.assertKweli(operator.lt(1, 2))
        self.assertKweli(operator.lt(1, 2.0))

    eleza test_le(self):
        operator = self.module
        self.assertRaises(TypeError, operator.le)
        self.assertRaises(TypeError, operator.le, 1j, 2j)
        self.assertUongo(operator.le(1, 0))
        self.assertUongo(operator.le(1, 0.0))
        self.assertKweli(operator.le(1, 1))
        self.assertKweli(operator.le(1, 1.0))
        self.assertKweli(operator.le(1, 2))
        self.assertKweli(operator.le(1, 2.0))

    eleza test_eq(self):
        operator = self.module
        kundi C(object):
            eleza __eq__(self, other):
                ashiria SyntaxError
        self.assertRaises(TypeError, operator.eq)
        self.assertRaises(SyntaxError, operator.eq, C(), C())
        self.assertUongo(operator.eq(1, 0))
        self.assertUongo(operator.eq(1, 0.0))
        self.assertKweli(operator.eq(1, 1))
        self.assertKweli(operator.eq(1, 1.0))
        self.assertUongo(operator.eq(1, 2))
        self.assertUongo(operator.eq(1, 2.0))

    eleza test_ne(self):
        operator = self.module
        kundi C(object):
            eleza __ne__(self, other):
                ashiria SyntaxError
        self.assertRaises(TypeError, operator.ne)
        self.assertRaises(SyntaxError, operator.ne, C(), C())
        self.assertKweli(operator.ne(1, 0))
        self.assertKweli(operator.ne(1, 0.0))
        self.assertUongo(operator.ne(1, 1))
        self.assertUongo(operator.ne(1, 1.0))
        self.assertKweli(operator.ne(1, 2))
        self.assertKweli(operator.ne(1, 2.0))

    eleza test_ge(self):
        operator = self.module
        self.assertRaises(TypeError, operator.ge)
        self.assertRaises(TypeError, operator.ge, 1j, 2j)
        self.assertKweli(operator.ge(1, 0))
        self.assertKweli(operator.ge(1, 0.0))
        self.assertKweli(operator.ge(1, 1))
        self.assertKweli(operator.ge(1, 1.0))
        self.assertUongo(operator.ge(1, 2))
        self.assertUongo(operator.ge(1, 2.0))

    eleza test_gt(self):
        operator = self.module
        self.assertRaises(TypeError, operator.gt)
        self.assertRaises(TypeError, operator.gt, 1j, 2j)
        self.assertKweli(operator.gt(1, 0))
        self.assertKweli(operator.gt(1, 0.0))
        self.assertUongo(operator.gt(1, 1))
        self.assertUongo(operator.gt(1, 1.0))
        self.assertUongo(operator.gt(1, 2))
        self.assertUongo(operator.gt(1, 2.0))

    eleza test_abs(self):
        operator = self.module
        self.assertRaises(TypeError, operator.abs)
        self.assertRaises(TypeError, operator.abs, Tupu)
        self.assertEqual(operator.abs(-1), 1)
        self.assertEqual(operator.abs(1), 1)

    eleza test_add(self):
        operator = self.module
        self.assertRaises(TypeError, operator.add)
        self.assertRaises(TypeError, operator.add, Tupu, Tupu)
        self.assertEqual(operator.add(3, 4), 7)

    eleza test_bitwise_and(self):
        operator = self.module
        self.assertRaises(TypeError, operator.and_)
        self.assertRaises(TypeError, operator.and_, Tupu, Tupu)
        self.assertEqual(operator.and_(0xf, 0xa), 0xa)

    eleza test_concat(self):
        operator = self.module
        self.assertRaises(TypeError, operator.concat)
        self.assertRaises(TypeError, operator.concat, Tupu, Tupu)
        self.assertEqual(operator.concat('py', 'thon'), 'python')
        self.assertEqual(operator.concat([1, 2], [3, 4]), [1, 2, 3, 4])
        self.assertEqual(operator.concat(Seq1([5, 6]), Seq1([7])), [5, 6, 7])
        self.assertEqual(operator.concat(Seq2([5, 6]), Seq2([7])), [5, 6, 7])
        self.assertRaises(TypeError, operator.concat, 13, 29)

    eleza test_countOf(self):
        operator = self.module
        self.assertRaises(TypeError, operator.countOf)
        self.assertRaises(TypeError, operator.countOf, Tupu, Tupu)
        self.assertEqual(operator.countOf([1, 2, 1, 3, 1, 4], 3), 1)
        self.assertEqual(operator.countOf([1, 2, 1, 3, 1, 4], 5), 0)

    eleza test_delitem(self):
        operator = self.module
        a = [4, 3, 2, 1]
        self.assertRaises(TypeError, operator.delitem, a)
        self.assertRaises(TypeError, operator.delitem, a, Tupu)
        self.assertIsTupu(operator.delitem(a, 1))
        self.assertEqual(a, [4, 2, 1])

    eleza test_floordiv(self):
        operator = self.module
        self.assertRaises(TypeError, operator.floordiv, 5)
        self.assertRaises(TypeError, operator.floordiv, Tupu, Tupu)
        self.assertEqual(operator.floordiv(5, 2), 2)

    eleza test_truediv(self):
        operator = self.module
        self.assertRaises(TypeError, operator.truediv, 5)
        self.assertRaises(TypeError, operator.truediv, Tupu, Tupu)
        self.assertEqual(operator.truediv(5, 2), 2.5)

    eleza test_getitem(self):
        operator = self.module
        a = range(10)
        self.assertRaises(TypeError, operator.getitem)
        self.assertRaises(TypeError, operator.getitem, a, Tupu)
        self.assertEqual(operator.getitem(a, 2), 2)

    eleza test_indexOf(self):
        operator = self.module
        self.assertRaises(TypeError, operator.indexOf)
        self.assertRaises(TypeError, operator.indexOf, Tupu, Tupu)
        self.assertEqual(operator.indexOf([4, 3, 2, 1], 3), 1)
        self.assertRaises(ValueError, operator.indexOf, [4, 3, 2, 1], 0)

    eleza test_invert(self):
        operator = self.module
        self.assertRaises(TypeError, operator.invert)
        self.assertRaises(TypeError, operator.invert, Tupu)
        self.assertEqual(operator.inv(4), -5)

    eleza test_lshift(self):
        operator = self.module
        self.assertRaises(TypeError, operator.lshift)
        self.assertRaises(TypeError, operator.lshift, Tupu, 42)
        self.assertEqual(operator.lshift(5, 1), 10)
        self.assertEqual(operator.lshift(5, 0), 5)
        self.assertRaises(ValueError, operator.lshift, 2, -1)

    eleza test_mod(self):
        operator = self.module
        self.assertRaises(TypeError, operator.mod)
        self.assertRaises(TypeError, operator.mod, Tupu, 42)
        self.assertEqual(operator.mod(5, 2), 1)

    eleza test_mul(self):
        operator = self.module
        self.assertRaises(TypeError, operator.mul)
        self.assertRaises(TypeError, operator.mul, Tupu, Tupu)
        self.assertEqual(operator.mul(5, 2), 10)

    eleza test_matmul(self):
        operator = self.module
        self.assertRaises(TypeError, operator.matmul)
        self.assertRaises(TypeError, operator.matmul, 42, 42)
        kundi M:
            eleza __matmul__(self, other):
                rudisha other - 1
        self.assertEqual(M() @ 42, 41)

    eleza test_neg(self):
        operator = self.module
        self.assertRaises(TypeError, operator.neg)
        self.assertRaises(TypeError, operator.neg, Tupu)
        self.assertEqual(operator.neg(5), -5)
        self.assertEqual(operator.neg(-5), 5)
        self.assertEqual(operator.neg(0), 0)
        self.assertEqual(operator.neg(-0), 0)

    eleza test_bitwise_or(self):
        operator = self.module
        self.assertRaises(TypeError, operator.or_)
        self.assertRaises(TypeError, operator.or_, Tupu, Tupu)
        self.assertEqual(operator.or_(0xa, 0x5), 0xf)

    eleza test_pos(self):
        operator = self.module
        self.assertRaises(TypeError, operator.pos)
        self.assertRaises(TypeError, operator.pos, Tupu)
        self.assertEqual(operator.pos(5), 5)
        self.assertEqual(operator.pos(-5), -5)
        self.assertEqual(operator.pos(0), 0)
        self.assertEqual(operator.pos(-0), 0)

    eleza test_pow(self):
        operator = self.module
        self.assertRaises(TypeError, operator.pow)
        self.assertRaises(TypeError, operator.pow, Tupu, Tupu)
        self.assertEqual(operator.pow(3,5), 3**5)
        self.assertRaises(TypeError, operator.pow, 1)
        self.assertRaises(TypeError, operator.pow, 1, 2, 3)

    eleza test_rshift(self):
        operator = self.module
        self.assertRaises(TypeError, operator.rshift)
        self.assertRaises(TypeError, operator.rshift, Tupu, 42)
        self.assertEqual(operator.rshift(5, 1), 2)
        self.assertEqual(operator.rshift(5, 0), 5)
        self.assertRaises(ValueError, operator.rshift, 2, -1)

    eleza test_contains(self):
        operator = self.module
        self.assertRaises(TypeError, operator.contains)
        self.assertRaises(TypeError, operator.contains, Tupu, Tupu)
        self.assertKweli(operator.contains(range(4), 2))
        self.assertUongo(operator.contains(range(4), 5))

    eleza test_setitem(self):
        operator = self.module
        a = list(range(3))
        self.assertRaises(TypeError, operator.setitem, a)
        self.assertRaises(TypeError, operator.setitem, a, Tupu, Tupu)
        self.assertIsTupu(operator.setitem(a, 0, 2))
        self.assertEqual(a, [2, 1, 2])
        self.assertRaises(IndexError, operator.setitem, a, 4, 2)

    eleza test_sub(self):
        operator = self.module
        self.assertRaises(TypeError, operator.sub)
        self.assertRaises(TypeError, operator.sub, Tupu, Tupu)
        self.assertEqual(operator.sub(5, 2), 3)

    eleza test_truth(self):
        operator = self.module
        kundi C(object):
            eleza __bool__(self):
                ashiria SyntaxError
        self.assertRaises(TypeError, operator.truth)
        self.assertRaises(SyntaxError, operator.truth, C())
        self.assertKweli(operator.truth(5))
        self.assertKweli(operator.truth([0]))
        self.assertUongo(operator.truth(0))
        self.assertUongo(operator.truth([]))

    eleza test_bitwise_xor(self):
        operator = self.module
        self.assertRaises(TypeError, operator.xor)
        self.assertRaises(TypeError, operator.xor, Tupu, Tupu)
        self.assertEqual(operator.xor(0xb, 0xc), 0x7)

    eleza test_is(self):
        operator = self.module
        a = b = 'xyzpdq'
        c = a[:3] + b[3:]
        self.assertRaises(TypeError, operator.is_)
        self.assertKweli(operator.is_(a, b))
        self.assertUongo(operator.is_(a,c))

    eleza test_is_not(self):
        operator = self.module
        a = b = 'xyzpdq'
        c = a[:3] + b[3:]
        self.assertRaises(TypeError, operator.is_not)
        self.assertUongo(operator.is_not(a, b))
        self.assertKweli(operator.is_not(a,c))

    eleza test_attrgetter(self):
        operator = self.module
        kundi A:
            pita
        a = A()
        a.name = 'arthur'
        f = operator.attrgetter('name')
        self.assertEqual(f(a), 'arthur')
        self.assertRaises(TypeError, f)
        self.assertRaises(TypeError, f, a, 'dent')
        self.assertRaises(TypeError, f, a, surname='dent')
        f = operator.attrgetter('rank')
        self.assertRaises(AttributeError, f, a)
        self.assertRaises(TypeError, operator.attrgetter, 2)
        self.assertRaises(TypeError, operator.attrgetter)

        # multiple gets
        record = A()
        record.x = 'X'
        record.y = 'Y'
        record.z = 'Z'
        self.assertEqual(operator.attrgetter('x','z','y')(record), ('X', 'Z', 'Y'))
        self.assertRaises(TypeError, operator.attrgetter, ('x', (), 'y'))

        kundi C(object):
            eleza __getattr__(self, name):
                ashiria SyntaxError
        self.assertRaises(SyntaxError, operator.attrgetter('foo'), C())

        # recursive gets
        a = A()
        a.name = 'arthur'
        a.child = A()
        a.child.name = 'thomas'
        f = operator.attrgetter('child.name')
        self.assertEqual(f(a), 'thomas')
        self.assertRaises(AttributeError, f, a.child)
        f = operator.attrgetter('name', 'child.name')
        self.assertEqual(f(a), ('arthur', 'thomas'))
        f = operator.attrgetter('name', 'child.name', 'child.child.name')
        self.assertRaises(AttributeError, f, a)
        f = operator.attrgetter('child.')
        self.assertRaises(AttributeError, f, a)
        f = operator.attrgetter('.child')
        self.assertRaises(AttributeError, f, a)

        a.child.child = A()
        a.child.child.name = 'johnson'
        f = operator.attrgetter('child.child.name')
        self.assertEqual(f(a), 'johnson')
        f = operator.attrgetter('name', 'child.name', 'child.child.name')
        self.assertEqual(f(a), ('arthur', 'thomas', 'johnson'))

    eleza test_itemgetter(self):
        operator = self.module
        a = 'ABCDE'
        f = operator.itemgetter(2)
        self.assertEqual(f(a), 'C')
        self.assertRaises(TypeError, f)
        self.assertRaises(TypeError, f, a, 3)
        self.assertRaises(TypeError, f, a, size=3)
        f = operator.itemgetter(10)
        self.assertRaises(IndexError, f, a)

        kundi C(object):
            eleza __getitem__(self, name):
                ashiria SyntaxError
        self.assertRaises(SyntaxError, operator.itemgetter(42), C())

        f = operator.itemgetter('name')
        self.assertRaises(TypeError, f, a)
        self.assertRaises(TypeError, operator.itemgetter)

        d = dict(key='val')
        f = operator.itemgetter('key')
        self.assertEqual(f(d), 'val')
        f = operator.itemgetter('nonkey')
        self.assertRaises(KeyError, f, d)

        # example used kwenye the docs
        inventory = [('apple', 3), ('banana', 2), ('pear', 5), ('orange', 1)]
        getcount = operator.itemgetter(1)
        self.assertEqual(list(map(getcount, inventory)), [3, 2, 5, 1])
        self.assertEqual(sorted(inventory, key=getcount),
            [('orange', 1), ('banana', 2), ('apple', 3), ('pear', 5)])

        # multiple gets
        data = list(map(str, range(20)))
        self.assertEqual(operator.itemgetter(2,10,5)(data), ('2', '10', '5'))
        self.assertRaises(TypeError, operator.itemgetter(2, 'x', 5), data)

        # interesting indices
        t = tuple('abcde')
        self.assertEqual(operator.itemgetter(-1)(t), 'e')
        self.assertEqual(operator.itemgetter(slice(2, 4))(t), ('c', 'd'))

        # interesting sequences
        kundi T(tuple):
            'Tuple subclass'
            pita
        self.assertEqual(operator.itemgetter(0)(T('abc')), 'a')
        self.assertEqual(operator.itemgetter(0)(['a', 'b', 'c']), 'a')
        self.assertEqual(operator.itemgetter(0)(range(100, 200)), 100)

    eleza test_methodcaller(self):
        operator = self.module
        self.assertRaises(TypeError, operator.methodcaller)
        self.assertRaises(TypeError, operator.methodcaller, 12)
        kundi A:
            eleza foo(self, *args, **kwds):
                rudisha args[0] + args[1]
            eleza bar(self, f=42):
                rudisha f
            eleza baz(*args, **kwds):
                rudisha kwds['name'], kwds['self']
        a = A()
        f = operator.methodcaller('foo')
        self.assertRaises(IndexError, f, a)
        f = operator.methodcaller('foo', 1, 2)
        self.assertEqual(f(a), 3)
        self.assertRaises(TypeError, f)
        self.assertRaises(TypeError, f, a, 3)
        self.assertRaises(TypeError, f, a, spam=3)
        f = operator.methodcaller('bar')
        self.assertEqual(f(a), 42)
        self.assertRaises(TypeError, f, a, a)
        f = operator.methodcaller('bar', f=5)
        self.assertEqual(f(a), 5)
        f = operator.methodcaller('baz', name='spam', self='eggs')
        self.assertEqual(f(a), ('spam', 'eggs'))

    eleza test_inplace(self):
        operator = self.module
        kundi C(object):
            eleza __iadd__     (self, other): rudisha "iadd"
            eleza __iand__     (self, other): rudisha "iand"
            eleza __ifloordiv__(self, other): rudisha "ifloordiv"
            eleza __ilshift__  (self, other): rudisha "ilshift"
            eleza __imod__     (self, other): rudisha "imod"
            eleza __imul__     (self, other): rudisha "imul"
            eleza __imatmul__  (self, other): rudisha "imatmul"
            eleza __ior__      (self, other): rudisha "ior"
            eleza __ipow__     (self, other): rudisha "ipow"
            eleza __irshift__  (self, other): rudisha "irshift"
            eleza __isub__     (self, other): rudisha "isub"
            eleza __itruediv__ (self, other): rudisha "itruediv"
            eleza __ixor__     (self, other): rudisha "ixor"
            eleza __getitem__(self, other): rudisha 5  # so that C ni a sequence
        c = C()
        self.assertEqual(operator.iadd     (c, 5), "iadd")
        self.assertEqual(operator.iand     (c, 5), "iand")
        self.assertEqual(operator.ifloordiv(c, 5), "ifloordiv")
        self.assertEqual(operator.ilshift  (c, 5), "ilshift")
        self.assertEqual(operator.imod     (c, 5), "imod")
        self.assertEqual(operator.imul     (c, 5), "imul")
        self.assertEqual(operator.imatmul  (c, 5), "imatmul")
        self.assertEqual(operator.ior      (c, 5), "ior")
        self.assertEqual(operator.ipow     (c, 5), "ipow")
        self.assertEqual(operator.irshift  (c, 5), "irshift")
        self.assertEqual(operator.isub     (c, 5), "isub")
        self.assertEqual(operator.itruediv (c, 5), "itruediv")
        self.assertEqual(operator.ixor     (c, 5), "ixor")
        self.assertEqual(operator.iconcat  (c, c), "iadd")

    eleza test_length_hint(self):
        operator = self.module
        kundi X(object):
            eleza __init__(self, value):
                self.value = value

            eleza __length_hint__(self):
                ikiwa type(self.value) ni type:
                    ashiria self.value
                isipokua:
                    rudisha self.value

        self.assertEqual(operator.length_hint([], 2), 0)
        self.assertEqual(operator.length_hint(iter([1, 2, 3])), 3)

        self.assertEqual(operator.length_hint(X(2)), 2)
        self.assertEqual(operator.length_hint(X(NotImplemented), 4), 4)
        self.assertEqual(operator.length_hint(X(TypeError), 12), 12)
        ukijumuisha self.assertRaises(TypeError):
            operator.length_hint(X("abc"))
        ukijumuisha self.assertRaises(ValueError):
            operator.length_hint(X(-2))
        ukijumuisha self.assertRaises(LookupError):
            operator.length_hint(X(LookupError))

    eleza test_dunder_is_original(self):
        operator = self.module

        names = [name kila name kwenye dir(operator) ikiwa sio name.startswith('_')]
        kila name kwenye names:
            orig = getattr(operator, name)
            dunder = getattr(operator, '__' + name.strip('_') + '__', Tupu)
            ikiwa dunder:
                self.assertIs(dunder, orig)

kundi PyOperatorTestCase(OperatorTestCase, unittest.TestCase):
    module = py_operator

@unittest.skipUnless(c_operator, 'requires _operator')
kundi COperatorTestCase(OperatorTestCase, unittest.TestCase):
    module = c_operator


kundi OperatorPickleTestCase:
    eleza copy(self, obj, proto):
        ukijumuisha support.swap_item(sys.modules, 'operator', self.module):
            pickled = pickle.dumps(obj, proto)
        ukijumuisha support.swap_item(sys.modules, 'operator', self.module2):
            rudisha pickle.loads(pickled)

    eleza test_attrgetter(self):
        attrgetter = self.module.attrgetter
        kundi A:
            pita
        a = A()
        a.x = 'X'
        a.y = 'Y'
        a.z = 'Z'
        a.t = A()
        a.t.u = A()
        a.t.u.v = 'V'
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                f = attrgetter('x')
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # multiple gets
                f = attrgetter('x', 'y', 'z')
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # recursive gets
                f = attrgetter('t.u.v')
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))

    eleza test_itemgetter(self):
        itemgetter = self.module.itemgetter
        a = 'ABCDE'
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                f = itemgetter(2)
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # multiple gets
                f = itemgetter(2, 0, 4)
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))

    eleza test_methodcaller(self):
        methodcaller = self.module.methodcaller
        kundi A:
            eleza foo(self, *args, **kwds):
                rudisha args[0] + args[1]
            eleza bar(self, f=42):
                rudisha f
            eleza baz(*args, **kwds):
                rudisha kwds['name'], kwds['self']
        a = A()
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                f = methodcaller('bar')
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # positional args
                f = methodcaller('foo', 1, 2)
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                # keyword args
                f = methodcaller('bar', f=5)
                f2 = self.copy(f, proto)
                self.assertEqual(repr(f2), repr(f))
                self.assertEqual(f2(a), f(a))
                f = methodcaller('baz', self='eggs', name='spam')
                f2 = self.copy(f, proto)
                # Can't test repr consistently ukijumuisha multiple keyword args
                self.assertEqual(f2(a), f(a))

kundi PyPyOperatorPickleTestCase(OperatorPickleTestCase, unittest.TestCase):
    module = py_operator
    module2 = py_operator

@unittest.skipUnless(c_operator, 'requires _operator')
kundi PyCOperatorPickleTestCase(OperatorPickleTestCase, unittest.TestCase):
    module = py_operator
    module2 = c_operator

@unittest.skipUnless(c_operator, 'requires _operator')
kundi CPyOperatorPickleTestCase(OperatorPickleTestCase, unittest.TestCase):
    module = c_operator
    module2 = py_operator

@unittest.skipUnless(c_operator, 'requires _operator')
kundi CCOperatorPickleTestCase(OperatorPickleTestCase, unittest.TestCase):
    module = c_operator
    module2 = c_operator


ikiwa __name__ == "__main__":
    unittest.main()
