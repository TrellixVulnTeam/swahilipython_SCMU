agiza unittest
agiza operator
agiza sys
agiza pickle

kutoka test agiza support

kundi G:
    'Sequence using __getitem__'
    eleza __init__(self, seqn):
        self.seqn = seqn
    eleza __getitem__(self, i):
        rudisha self.seqn[i]

kundi I:
    'Sequence using iterator protocol'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        ikiwa self.i >= len(self.seqn): ashiria StopIteration
        v = self.seqn[self.i]
        self.i += 1
        rudisha v

kundi Ig:
    'Sequence using iterator protocol defined ukijumuisha a generator'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        kila val kwenye self.seqn:
            tuma val

kundi X:
    'Missing __getitem__ na __iter__'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __next__(self):
        ikiwa self.i >= len(self.seqn): ashiria StopIteration
        v = self.seqn[self.i]
        self.i += 1
        rudisha v

kundi E:
    'Test propagation of exceptions'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        3 // 0

kundi N:
    'Iterator missing __next__()'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self

kundi PickleTest:
    # Helper to check picklability
    eleza check_pickle(self, itorg, seq):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(list(it), seq)

            it = pickle.loads(d)
            jaribu:
                next(it)
            tatizo StopIteration:
                self.assertUongo(seq[1:])
                endelea
            d = pickle.dumps(it, proto)
            it = pickle.loads(d)
            self.assertEqual(list(it), seq[1:])

kundi EnumerateTestCase(unittest.TestCase, PickleTest):

    enum = enumerate
    seq, res = 'abc', [(0,'a'), (1,'b'), (2,'c')]

    eleza test_basicfunction(self):
        self.assertEqual(type(self.enum(self.seq)), self.enum)
        e = self.enum(self.seq)
        self.assertEqual(iter(e), e)
        self.assertEqual(list(self.enum(self.seq)), self.res)
        self.enum.__doc__

    eleza test_pickle(self):
        self.check_pickle(self.enum(self.seq), self.res)

    eleza test_getitemseqn(self):
        self.assertEqual(list(self.enum(G(self.seq))), self.res)
        e = self.enum(G(''))
        self.assertRaises(StopIteration, next, e)

    eleza test_iteratorseqn(self):
        self.assertEqual(list(self.enum(I(self.seq))), self.res)
        e = self.enum(I(''))
        self.assertRaises(StopIteration, next, e)

    eleza test_iteratorgenerator(self):
        self.assertEqual(list(self.enum(Ig(self.seq))), self.res)
        e = self.enum(Ig(''))
        self.assertRaises(StopIteration, next, e)

    eleza test_noniterable(self):
        self.assertRaises(TypeError, self.enum, X(self.seq))

    eleza test_illformediterable(self):
        self.assertRaises(TypeError, self.enum, N(self.seq))

    eleza test_exception_propagation(self):
        self.assertRaises(ZeroDivisionError, list, self.enum(E(self.seq)))

    eleza test_argumentcheck(self):
        self.assertRaises(TypeError, self.enum) # no arguments
        self.assertRaises(TypeError, self.enum, 1) # wrong type (sio iterable)
        self.assertRaises(TypeError, self.enum, 'abc', 'a') # wrong type
        self.assertRaises(TypeError, self.enum, 'abc', 2, 3) # too many arguments

    @support.cpython_only
    eleza test_tuple_reuse(self):
        # Tests an implementation detail where tuple ni reused
        # whenever nothing isipokua holds a reference to it
        self.assertEqual(len(set(map(id, list(enumerate(self.seq))))), len(self.seq))
        self.assertEqual(len(set(map(id, enumerate(self.seq)))), min(1,len(self.seq)))

kundi MyEnum(enumerate):
    pita

kundi SubclassTestCase(EnumerateTestCase):

    enum = MyEnum

kundi TestEmpty(EnumerateTestCase):

    seq, res = '', []

kundi TestBig(EnumerateTestCase):

    seq = range(10,20000,2)
    res = list(zip(range(20000), seq))

kundi TestReversed(unittest.TestCase, PickleTest):

    eleza test_simple(self):
        kundi A:
            eleza __getitem__(self, i):
                ikiwa i < 5:
                    rudisha str(i)
                ashiria StopIteration
            eleza __len__(self):
                rudisha 5
        kila data kwenye ('abc', range(5), tuple(enumerate('abc')), A(),
                    range(1,17,5), dict.fromkeys('abcde')):
            self.assertEqual(list(data)[::-1], list(reversed(data)))
        # don't allow keyword arguments
        self.assertRaises(TypeError, reversed, [], a=1)

    eleza test_range_optimization(self):
        x = range(1)
        self.assertEqual(type(reversed(x)), type(iter(x)))

    eleza test_len(self):
        kila s kwenye ('hello', tuple('hello'), list('hello'), range(5)):
            self.assertEqual(operator.length_hint(reversed(s)), len(s))
            r = reversed(s)
            list(r)
            self.assertEqual(operator.length_hint(r), 0)
        kundi SeqWithWeirdLen:
            called = Uongo
            eleza __len__(self):
                ikiwa sio self.called:
                    self.called = Kweli
                    rudisha 10
                ashiria ZeroDivisionError
            eleza __getitem__(self, index):
                rudisha index
        r = reversed(SeqWithWeirdLen())
        self.assertRaises(ZeroDivisionError, operator.length_hint, r)


    eleza test_gc(self):
        kundi Seq:
            eleza __len__(self):
                rudisha 10
            eleza __getitem__(self, index):
                rudisha index
        s = Seq()
        r = reversed(s)
        s.r = r

    eleza test_args(self):
        self.assertRaises(TypeError, reversed)
        self.assertRaises(TypeError, reversed, [], 'extra')

    @unittest.skipUnless(hasattr(sys, 'getrefcount'), 'test needs sys.getrefcount()')
    eleza test_bug1229429(self):
        # this bug was never kwenye reversed, it was in
        # PyObject_CallMethod, na reversed_new calls that sometimes.
        eleza f():
            pita
        r = f.__reversed__ = object()
        rc = sys.getrefcount(r)
        kila i kwenye range(10):
            jaribu:
                reversed(f)
            tatizo TypeError:
                pita
            isipokua:
                self.fail("non-callable __reversed__ didn't raise!")
        self.assertEqual(rc, sys.getrefcount(r))

    eleza test_objmethods(self):
        # Objects must have __len__() na __getitem__() implemented.
        kundi NoLen(object):
            eleza __getitem__(self, i): rudisha 1
        nl = NoLen()
        self.assertRaises(TypeError, reversed, nl)

        kundi NoGetItem(object):
            eleza __len__(self): rudisha 2
        ngi = NoGetItem()
        self.assertRaises(TypeError, reversed, ngi)

        kundi Blocked(object):
            eleza __getitem__(self, i): rudisha 1
            eleza __len__(self): rudisha 2
            __reversed__ = Tupu
        b = Blocked()
        self.assertRaises(TypeError, reversed, b)

    eleza test_pickle(self):
        kila data kwenye 'abc', range(5), tuple(enumerate('abc')), range(1,17,5):
            self.check_pickle(reversed(data), list(data)[::-1])


kundi EnumerateStartTestCase(EnumerateTestCase):

    eleza test_basicfunction(self):
        e = self.enum(self.seq)
        self.assertEqual(iter(e), e)
        self.assertEqual(list(self.enum(self.seq)), self.res)


kundi TestStart(EnumerateStartTestCase):

    enum = lambda self, i: enumerate(i, start=11)
    seq, res = 'abc', [(11, 'a'), (12, 'b'), (13, 'c')]


kundi TestLongStart(EnumerateStartTestCase):

    enum = lambda self, i: enumerate(i, start=sys.maxsize+1)
    seq, res = 'abc', [(sys.maxsize+1,'a'), (sys.maxsize+2,'b'),
                       (sys.maxsize+3,'c')]


ikiwa __name__ == "__main__":
    unittest.main()
