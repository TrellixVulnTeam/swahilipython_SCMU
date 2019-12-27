"""
Tests common to tuple, list and UserList.UserList
"""

agiza unittest
agiza sys
agiza pickle
kutoka test agiza support

# Various iterables
# This is used for checking the constructor (here and in test_deque.py)
eleza iterfunc(seqn):
    'Regular generator'
    for i in seqn:
        yield i

kundi Sequence:
    'Sequence using __getitem__'
    eleza __init__(self, seqn):
        self.seqn = seqn
    eleza __getitem__(self, i):
        rudisha self.seqn[i]

kundi IterFunc:
    'Sequence using iterator protocol'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        ikiwa self.i >= len(self.seqn): raise StopIteration
        v = self.seqn[self.i]
        self.i += 1
        rudisha v

kundi IterGen:
    'Sequence using iterator protocol defined with a generator'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        for val in self.seqn:
            yield val

kundi IterNextOnly:
    'Missing __getitem__ and __iter__'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __next__(self):
        ikiwa self.i >= len(self.seqn): raise StopIteration
        v = self.seqn[self.i]
        self.i += 1
        rudisha v

kundi IterNoNext:
    'Iterator missing __next__()'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self

kundi IterGenExc:
    'Test propagation of exceptions'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        3 // 0

kundi IterFuncStop:
    'Test immediate stop'
    eleza __init__(self, seqn):
        pass
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        raise StopIteration

kutoka itertools agiza chain
eleza itermulti(seqn):
    'Test multiple tiers of iterators'
    rudisha chain(map(lambda x:x, iterfunc(IterGen(Sequence(seqn)))))

kundi LyingTuple(tuple):
    eleza __iter__(self):
        yield 1

kundi LyingList(list):
    eleza __iter__(self):
        yield 1

kundi CommonTest(unittest.TestCase):
    # The type to be tested
    type2test = None

    eleza test_constructors(self):
        l0 = []
        l1 = [0]
        l2 = [0, 1]

        u = self.type2test()
        u0 = self.type2test(l0)
        u1 = self.type2test(l1)
        u2 = self.type2test(l2)

        uu = self.type2test(u)
        uu0 = self.type2test(u0)
        uu1 = self.type2test(u1)
        uu2 = self.type2test(u2)

        v = self.type2test(tuple(u))
        kundi OtherSeq:
            eleza __init__(self, initseq):
                self.__data = initseq
            eleza __len__(self):
                rudisha len(self.__data)
            eleza __getitem__(self, i):
                rudisha self.__data[i]
        s = OtherSeq(u0)
        v0 = self.type2test(s)
        self.assertEqual(len(v0), len(s))

        s = "this is also a sequence"
        vv = self.type2test(s)
        self.assertEqual(len(vv), len(s))

        # Create kutoka various iteratables
        for s in ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            for g in (Sequence, IterFunc, IterGen,
                      itermulti, iterfunc):
                self.assertEqual(self.type2test(g(s)), self.type2test(s))
            self.assertEqual(self.type2test(IterFuncStop(s)), self.type2test())
            self.assertEqual(self.type2test(c for c in "123"), self.type2test("123"))
            self.assertRaises(TypeError, self.type2test, IterNextOnly(s))
            self.assertRaises(TypeError, self.type2test, IterNoNext(s))
            self.assertRaises(ZeroDivisionError, self.type2test, IterGenExc(s))

        # Issue #23757
        self.assertEqual(self.type2test(LyingTuple((2,))), self.type2test((1,)))
        self.assertEqual(self.type2test(LyingList([2])), self.type2test([1]))

    eleza test_truth(self):
        self.assertFalse(self.type2test())
        self.assertTrue(self.type2test([42]))

    eleza test_getitem(self):
        u = self.type2test([0, 1, 2, 3, 4])
        for i in range(len(u)):
            self.assertEqual(u[i], i)
            self.assertEqual(u[int(i)], i)
        for i in range(-len(u), -1):
            self.assertEqual(u[i], len(u)+i)
            self.assertEqual(u[int(i)], len(u)+i)
        self.assertRaises(IndexError, u.__getitem__, -len(u)-1)
        self.assertRaises(IndexError, u.__getitem__, len(u))
        self.assertRaises(ValueError, u.__getitem__, slice(0,10,0))

        u = self.type2test()
        self.assertRaises(IndexError, u.__getitem__, 0)
        self.assertRaises(IndexError, u.__getitem__, -1)

        self.assertRaises(TypeError, u.__getitem__)

        a = self.type2test([10, 11])
        self.assertEqual(a[0], 10)
        self.assertEqual(a[1], 11)
        self.assertEqual(a[-2], 10)
        self.assertEqual(a[-1], 11)
        self.assertRaises(IndexError, a.__getitem__, -3)
        self.assertRaises(IndexError, a.__getitem__, 3)

    eleza test_getslice(self):
        l = [0, 1, 2, 3, 4]
        u = self.type2test(l)

        self.assertEqual(u[0:0], self.type2test())
        self.assertEqual(u[1:2], self.type2test([1]))
        self.assertEqual(u[-2:-1], self.type2test([3]))
        self.assertEqual(u[-1000:1000], u)
        self.assertEqual(u[1000:-1000], self.type2test([]))
        self.assertEqual(u[:], u)
        self.assertEqual(u[1:None], self.type2test([1, 2, 3, 4]))
        self.assertEqual(u[None:3], self.type2test([0, 1, 2]))

        # Extended slices
        self.assertEqual(u[::], u)
        self.assertEqual(u[::2], self.type2test([0, 2, 4]))
        self.assertEqual(u[1::2], self.type2test([1, 3]))
        self.assertEqual(u[::-1], self.type2test([4, 3, 2, 1, 0]))
        self.assertEqual(u[::-2], self.type2test([4, 2, 0]))
        self.assertEqual(u[3::-2], self.type2test([3, 1]))
        self.assertEqual(u[3:3:-2], self.type2test([]))
        self.assertEqual(u[3:2:-2], self.type2test([3]))
        self.assertEqual(u[3:1:-2], self.type2test([3]))
        self.assertEqual(u[3:0:-2], self.type2test([3, 1]))
        self.assertEqual(u[::-100], self.type2test([4]))
        self.assertEqual(u[100:-100:], self.type2test([]))
        self.assertEqual(u[-100:100:], u)
        self.assertEqual(u[100:-100:-1], u[::-1])
        self.assertEqual(u[-100:100:-1], self.type2test([]))
        self.assertEqual(u[-100:100:2], self.type2test([0, 2, 4]))

        # Test extreme cases with long ints
        a = self.type2test([0,1,2,3,4])
        self.assertEqual(a[ -pow(2,128): 3 ], self.type2test([0,1,2]))
        self.assertEqual(a[ 3: pow(2,145) ], self.type2test([3,4]))
        self.assertEqual(a[3::sys.maxsize], self.type2test([3]))

    eleza test_contains(self):
        u = self.type2test([0, 1, 2])
        for i in u:
            self.assertIn(i, u)
        for i in min(u)-1, max(u)+1:
            self.assertNotIn(i, u)

        self.assertRaises(TypeError, u.__contains__)

    eleza test_contains_fake(self):
        kundi AllEq:
            # Sequences must use rich comparison against each item
            # (unless "is" is true, or an earlier item answered)
            # So instances of AllEq must be found in all non-empty sequences.
            eleza __eq__(self, other):
                rudisha True
            __hash__ = None # Can't meet hash invariant requirements
        self.assertNotIn(AllEq(), self.type2test([]))
        self.assertIn(AllEq(), self.type2test([1]))

    eleza test_contains_order(self):
        # Sequences must test in-order.  If a rich comparison has side
        # effects, these will be visible to tests against later members.
        # In this test, the "side effect" is a short-circuiting raise.
        kundi DoNotTestEq(Exception):
            pass
        kundi StopCompares:
            eleza __eq__(self, other):
                raise DoNotTestEq

        checkfirst = self.type2test([1, StopCompares()])
        self.assertIn(1, checkfirst)
        checklast = self.type2test([StopCompares(), 1])
        self.assertRaises(DoNotTestEq, checklast.__contains__, 1)

    eleza test_len(self):
        self.assertEqual(len(self.type2test()), 0)
        self.assertEqual(len(self.type2test([])), 0)
        self.assertEqual(len(self.type2test([0])), 1)
        self.assertEqual(len(self.type2test([0, 1, 2])), 3)

    eleza test_minmax(self):
        u = self.type2test([0, 1, 2])
        self.assertEqual(min(u), 0)
        self.assertEqual(max(u), 2)

    eleza test_addmul(self):
        u1 = self.type2test([0])
        u2 = self.type2test([0, 1])
        self.assertEqual(u1, u1 + self.type2test())
        self.assertEqual(u1, self.type2test() + u1)
        self.assertEqual(u1 + self.type2test([1]), u2)
        self.assertEqual(self.type2test([-1]) + u1, self.type2test([-1, 0]))
        self.assertEqual(self.type2test(), u2*0)
        self.assertEqual(self.type2test(), 0*u2)
        self.assertEqual(self.type2test(), u2*0)
        self.assertEqual(self.type2test(), 0*u2)
        self.assertEqual(u2, u2*1)
        self.assertEqual(u2, 1*u2)
        self.assertEqual(u2, u2*1)
        self.assertEqual(u2, 1*u2)
        self.assertEqual(u2+u2, u2*2)
        self.assertEqual(u2+u2, 2*u2)
        self.assertEqual(u2+u2, u2*2)
        self.assertEqual(u2+u2, 2*u2)
        self.assertEqual(u2+u2+u2, u2*3)
        self.assertEqual(u2+u2+u2, 3*u2)

        kundi subclass(self.type2test):
            pass
        u3 = subclass([0, 1])
        self.assertEqual(u3, u3*1)
        self.assertIsNot(u3, u3*1)

    eleza test_iadd(self):
        u = self.type2test([0, 1])
        u += self.type2test()
        self.assertEqual(u, self.type2test([0, 1]))
        u += self.type2test([2, 3])
        self.assertEqual(u, self.type2test([0, 1, 2, 3]))
        u += self.type2test([4, 5])
        self.assertEqual(u, self.type2test([0, 1, 2, 3, 4, 5]))

        u = self.type2test("spam")
        u += self.type2test("eggs")
        self.assertEqual(u, self.type2test("spameggs"))

    eleza test_imul(self):
        u = self.type2test([0, 1])
        u *= 3
        self.assertEqual(u, self.type2test([0, 1, 0, 1, 0, 1]))
        u *= 0
        self.assertEqual(u, self.type2test([]))

    eleza test_getitemoverwriteiter(self):
        # Verify that __getitem__ overrides are not recognized by __iter__
        kundi T(self.type2test):
            eleza __getitem__(self, key):
                rudisha str(key) + '!!!'
        self.assertEqual(next(iter(T((1,2)))), 1)

    eleza test_repeat(self):
        for m in range(4):
            s = tuple(range(m))
            for n in range(-3, 5):
                self.assertEqual(self.type2test(s*n), self.type2test(s)*n)
            self.assertEqual(self.type2test(s)*(-4), self.type2test([]))
            self.assertEqual(id(s), id(s*1))

    eleza test_bigrepeat(self):
        ikiwa sys.maxsize <= 2147483647:
            x = self.type2test([0])
            x *= 2**16
            self.assertRaises(MemoryError, x.__mul__, 2**16)
            ikiwa hasattr(x, '__imul__'):
                self.assertRaises(MemoryError, x.__imul__, 2**16)

    eleza test_subscript(self):
        a = self.type2test([10, 11])
        self.assertEqual(a.__getitem__(0), 10)
        self.assertEqual(a.__getitem__(1), 11)
        self.assertEqual(a.__getitem__(-2), 10)
        self.assertEqual(a.__getitem__(-1), 11)
        self.assertRaises(IndexError, a.__getitem__, -3)
        self.assertRaises(IndexError, a.__getitem__, 3)
        self.assertEqual(a.__getitem__(slice(0,1)), self.type2test([10]))
        self.assertEqual(a.__getitem__(slice(1,2)), self.type2test([11]))
        self.assertEqual(a.__getitem__(slice(0,2)), self.type2test([10, 11]))
        self.assertEqual(a.__getitem__(slice(0,3)), self.type2test([10, 11]))
        self.assertEqual(a.__getitem__(slice(3,5)), self.type2test([]))
        self.assertRaises(ValueError, a.__getitem__, slice(0, 10, 0))
        self.assertRaises(TypeError, a.__getitem__, 'x')

    eleza test_count(self):
        a = self.type2test([0, 1, 2])*3
        self.assertEqual(a.count(0), 3)
        self.assertEqual(a.count(1), 3)
        self.assertEqual(a.count(3), 0)

        self.assertRaises(TypeError, a.count)

        kundi BadExc(Exception):
            pass

        kundi BadCmp:
            eleza __eq__(self, other):
                ikiwa other == 2:
                    raise BadExc()
                rudisha False

        self.assertRaises(BadExc, a.count, BadCmp())

    eleza test_index(self):
        u = self.type2test([0, 1])
        self.assertEqual(u.index(0), 0)
        self.assertEqual(u.index(1), 1)
        self.assertRaises(ValueError, u.index, 2)

        u = self.type2test([-2, -1, 0, 0, 1, 2])
        self.assertEqual(u.count(0), 2)
        self.assertEqual(u.index(0), 2)
        self.assertEqual(u.index(0, 2), 2)
        self.assertEqual(u.index(-2, -10), 0)
        self.assertEqual(u.index(0, 3), 3)
        self.assertEqual(u.index(0, 3, 4), 3)
        self.assertRaises(ValueError, u.index, 2, 0, -10)

        self.assertRaises(TypeError, u.index)

        kundi BadExc(Exception):
            pass

        kundi BadCmp:
            eleza __eq__(self, other):
                ikiwa other == 2:
                    raise BadExc()
                rudisha False

        a = self.type2test([0, 1, 2, 3])
        self.assertRaises(BadExc, a.index, BadCmp())

        a = self.type2test([-2, -1, 0, 0, 1, 2])
        self.assertEqual(a.index(0), 2)
        self.assertEqual(a.index(0, 2), 2)
        self.assertEqual(a.index(0, -4), 2)
        self.assertEqual(a.index(-2, -10), 0)
        self.assertEqual(a.index(0, 3), 3)
        self.assertEqual(a.index(0, -3), 3)
        self.assertEqual(a.index(0, 3, 4), 3)
        self.assertEqual(a.index(0, -3, -2), 3)
        self.assertEqual(a.index(0, -4*sys.maxsize, 4*sys.maxsize), 2)
        self.assertRaises(ValueError, a.index, 0, 4*sys.maxsize,-4*sys.maxsize)
        self.assertRaises(ValueError, a.index, 2, 0, -10)

    eleza test_pickle(self):
        lst = self.type2test([4, 5, 6, 7])
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            lst2 = pickle.loads(pickle.dumps(lst, proto))
            self.assertEqual(lst2, lst)
            self.assertNotEqual(id(lst2), id(lst))

    eleza test_free_after_iterating(self):
        support.check_free_after_iterating(self, iter, self.type2test)
        support.check_free_after_iterating(self, reversed, self.type2test)
