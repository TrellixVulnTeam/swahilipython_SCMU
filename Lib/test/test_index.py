agiza unittest
kutoka test agiza support
agiza operator
maxsize = support.MAX_Py_ssize_t

kundi newstyle:
    eleza __index__(self):
        rudisha self.ind

kundi TrapInt(int):
    eleza __index__(self):
        rudisha int(self)

kundi BaseTestCase(unittest.TestCase):
    eleza setUp(self):
        self.o = newstyle()
        self.n = newstyle()

    eleza test_basic(self):
        self.o.ind = -2
        self.n.ind = 2
        self.assertEqual(operator.index(self.o), -2)
        self.assertEqual(operator.index(self.n), 2)

    eleza test_slice(self):
        self.o.ind = 1
        self.n.ind = 2
        slc = slice(self.o, self.o, self.o)
        check_slc = slice(1, 1, 1)
        self.assertEqual(slc.indices(self.o), check_slc.indices(1))
        slc = slice(self.n, self.n, self.n)
        check_slc = slice(2, 2, 2)
        self.assertEqual(slc.indices(self.n), check_slc.indices(2))

    eleza test_wrappers(self):
        self.o.ind = 4
        self.n.ind = 5
        self.assertEqual(6 .__index__(), 6)
        self.assertEqual(-7 .__index__(), -7)
        self.assertEqual(self.o.__index__(), 4)
        self.assertEqual(self.n.__index__(), 5)
        self.assertEqual(Kweli.__index__(), 1)
        self.assertEqual(Uongo.__index__(), 0)

    eleza test_subclasses(self):
        r = list(range(10))
        self.assertEqual(r[TrapInt(5):TrapInt(10)], r[5:10])
        self.assertEqual(slice(TrapInt()).indices(0), (0,0,1))

    eleza test_error(self):
        self.o.ind = 'dumb'
        self.n.ind = 'bad'
        self.assertRaises(TypeError, operator.index, self.o)
        self.assertRaises(TypeError, operator.index, self.n)
        self.assertRaises(TypeError, slice(self.o).indices, 0)
        self.assertRaises(TypeError, slice(self.n).indices, 0)

    eleza test_int_subclass_with_index(self):
        # __index__ should be used when computing indices, even kila int
        # subclasses.  See issue #17576.
        kundi MyInt(int):
            eleza __index__(self):
                rudisha int(str(self)) + 1

        my_int = MyInt(7)
        direct_index = my_int.__index__()
        operator_index = operator.index(my_int)
        self.assertEqual(direct_index, 8)
        self.assertEqual(operator_index, 7)
        # Both results should be of exact type int.
        self.assertIs(type(direct_index), int)
        #self.assertIs(type(operator_index), int)

    eleza test_index_returns_int_subclass(self):
        kundi BadInt:
            eleza __index__(self):
                rudisha Kweli

        kundi BadInt2(int):
            eleza __index__(self):
                rudisha Kweli

        bad_int = BadInt()
        ukijumuisha self.assertWarns(DeprecationWarning):
            n = operator.index(bad_int)
        self.assertEqual(n, 1)

        bad_int = BadInt2()
        n = operator.index(bad_int)
        self.assertEqual(n, 0)


kundi SeqTestCase:
    # This test case isn't run directly. It just defines common tests
    # to the different sequence types below
    eleza setUp(self):
        self.o = newstyle()
        self.n = newstyle()
        self.o2 = newstyle()
        self.n2 = newstyle()

    eleza test_index(self):
        self.o.ind = -2
        self.n.ind = 2
        self.assertEqual(self.seq[self.n], self.seq[2])
        self.assertEqual(self.seq[self.o], self.seq[-2])

    eleza test_slice(self):
        self.o.ind = 1
        self.o2.ind = 3
        self.n.ind = 2
        self.n2.ind = 4
        self.assertEqual(self.seq[self.o:self.o2], self.seq[1:3])
        self.assertEqual(self.seq[self.n:self.n2], self.seq[2:4])

    eleza test_slice_bug7532(self):
        seqlen = len(self.seq)
        self.o.ind = int(seqlen * 1.5)
        self.n.ind = seqlen + 2
        self.assertEqual(self.seq[self.o:], self.seq[0:0])
        self.assertEqual(self.seq[:self.o], self.seq)
        self.assertEqual(self.seq[self.n:], self.seq[0:0])
        self.assertEqual(self.seq[:self.n], self.seq)
        self.o2.ind = -seqlen - 2
        self.n2.ind = -int(seqlen * 1.5)
        self.assertEqual(self.seq[self.o2:], self.seq)
        self.assertEqual(self.seq[:self.o2], self.seq[0:0])
        self.assertEqual(self.seq[self.n2:], self.seq)
        self.assertEqual(self.seq[:self.n2], self.seq[0:0])

    eleza test_repeat(self):
        self.o.ind = 3
        self.n.ind = 2
        self.assertEqual(self.seq * self.o, self.seq * 3)
        self.assertEqual(self.seq * self.n, self.seq * 2)
        self.assertEqual(self.o * self.seq, self.seq * 3)
        self.assertEqual(self.n * self.seq, self.seq * 2)

    eleza test_wrappers(self):
        self.o.ind = 4
        self.n.ind = 5
        self.assertEqual(self.seq.__getitem__(self.o), self.seq[4])
        self.assertEqual(self.seq.__mul__(self.o), self.seq * 4)
        self.assertEqual(self.seq.__rmul__(self.o), self.seq * 4)
        self.assertEqual(self.seq.__getitem__(self.n), self.seq[5])
        self.assertEqual(self.seq.__mul__(self.n), self.seq * 5)
        self.assertEqual(self.seq.__rmul__(self.n), self.seq * 5)

    eleza test_subclasses(self):
        self.assertEqual(self.seq[TrapInt()], self.seq[0])

    eleza test_error(self):
        self.o.ind = 'dumb'
        self.n.ind = 'bad'
        indexobj = lambda x, obj: obj.seq[x]
        self.assertRaises(TypeError, indexobj, self.o, self)
        self.assertRaises(TypeError, indexobj, self.n, self)
        sliceobj = lambda x, obj: obj.seq[x:]
        self.assertRaises(TypeError, sliceobj, self.o, self)
        self.assertRaises(TypeError, sliceobj, self.n, self)


kundi ListTestCase(SeqTestCase, unittest.TestCase):
    seq = [0,10,20,30,40,50]

    eleza test_setdelitem(self):
        self.o.ind = -2
        self.n.ind = 2
        lst = list('ab!cdefghi!j')
        toa lst[self.o]
        toa lst[self.n]
        lst[self.o] = 'X'
        lst[self.n] = 'Y'
        self.assertEqual(lst, list('abYdefghXj'))

        lst = [5, 6, 7, 8, 9, 10, 11]
        lst.__setitem__(self.n, "here")
        self.assertEqual(lst, [5, 6, "here", 8, 9, 10, 11])
        lst.__delitem__(self.n)
        self.assertEqual(lst, [5, 6, 8, 9, 10, 11])

    eleza test_inplace_repeat(self):
        self.o.ind = 2
        self.n.ind = 3
        lst = [6, 4]
        lst *= self.o
        self.assertEqual(lst, [6, 4, 6, 4])
        lst *= self.n
        self.assertEqual(lst, [6, 4, 6, 4] * 3)

        lst = [5, 6, 7, 8, 9, 11]
        l2 = lst.__imul__(self.n)
        self.assertIs(l2, lst)
        self.assertEqual(lst, [5, 6, 7, 8, 9, 11] * 3)


kundi NewSeq:

    eleza __init__(self, iterable):
        self._list = list(iterable)

    eleza __repr__(self):
        rudisha repr(self._list)

    eleza __eq__(self, other):
        rudisha self._list == other

    eleza __len__(self):
        rudisha len(self._list)

    eleza __mul__(self, n):
        rudisha self.__class__(self._list*n)
    __rmul__ = __mul__

    eleza __getitem__(self, index):
        rudisha self._list[index]


kundi TupleTestCase(SeqTestCase, unittest.TestCase):
    seq = (0,10,20,30,40,50)

kundi ByteArrayTestCase(SeqTestCase, unittest.TestCase):
    seq = bytearray(b"this ni a test")

kundi BytesTestCase(SeqTestCase, unittest.TestCase):
    seq = b"this ni a test"

kundi StringTestCase(SeqTestCase, unittest.TestCase):
    seq = "this ni a test"

kundi NewSeqTestCase(SeqTestCase, unittest.TestCase):
    seq = NewSeq((0,10,20,30,40,50))



kundi RangeTestCase(unittest.TestCase):

    eleza test_range(self):
        n = newstyle()
        n.ind = 5
        self.assertEqual(range(1, 20)[n], 6)
        self.assertEqual(range(1, 20).__getitem__(n), 6)


kundi OverflowTestCase(unittest.TestCase):

    eleza setUp(self):
        self.pos = 2**100
        self.neg = -self.pos

    eleza test_large_longs(self):
        self.assertEqual(self.pos.__index__(), self.pos)
        self.assertEqual(self.neg.__index__(), self.neg)

    eleza test_getitem(self):
        kundi GetItem:
            eleza __len__(self):
                assert Uongo, "__len__ should sio be invoked"
            eleza __getitem__(self, key):
                rudisha key
        x = GetItem()
        self.assertEqual(x[self.pos], self.pos)
        self.assertEqual(x[self.neg], self.neg)
        self.assertEqual(x[self.neg:self.pos].indices(maxsize),
                         (0, maxsize, 1))
        self.assertEqual(x[self.neg:self.pos:1].indices(maxsize),
                         (0, maxsize, 1))

    eleza test_sequence_repeat(self):
        self.assertRaises(OverflowError, lambda: "a" * self.pos)
        self.assertRaises(OverflowError, lambda: "a" * self.neg)


ikiwa __name__ == "__main__":
    unittest.main()
