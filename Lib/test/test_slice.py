# tests for slice objects; in particular the indices method.

agiza itertools
agiza operator
agiza sys
agiza unittest
agiza weakref

kutoka pickle agiza loads, dumps
kutoka test agiza support


eleza evaluate_slice_index(arg):
    """
    Helper function to convert a slice argument to an integer, and raise
    TypeError with a suitable message on failure.

    """
    ikiwa hasattr(arg, '__index__'):
        rudisha operator.index(arg)
    else:
        raise TypeError(
            "slice indices must be integers or "
            "None or have an __index__ method")

eleza slice_indices(slice, length):
    """
    Reference implementation for the slice.indices method.

    """
    # Compute step and length as integers.
    length = operator.index(length)
    step = 1 ikiwa slice.step is None else evaluate_slice_index(slice.step)

    # Raise ValueError for negative length or zero step.
    ikiwa length < 0:
        raise ValueError("length should not be negative")
    ikiwa step == 0:
        raise ValueError("slice step cannot be zero")

    # Find lower and upper bounds for start and stop.
    lower = -1 ikiwa step < 0 else 0
    upper = length - 1 ikiwa step < 0 else length

    # Compute start.
    ikiwa slice.start is None:
        start = upper ikiwa step < 0 else lower
    else:
        start = evaluate_slice_index(slice.start)
        start = max(start + length, lower) ikiwa start < 0 else min(start, upper)

    # Compute stop.
    ikiwa slice.stop is None:
        stop = lower ikiwa step < 0 else upper
    else:
        stop = evaluate_slice_index(slice.stop)
        stop = max(stop + length, lower) ikiwa stop < 0 else min(stop, upper)

    rudisha start, stop, step


# Class providing an __index__ method.  Used for testing slice.indices.

kundi MyIndexable(object):
    eleza __init__(self, value):
        self.value = value

    eleza __index__(self):
        rudisha self.value


kundi SliceTest(unittest.TestCase):

    eleza test_constructor(self):
        self.assertRaises(TypeError, slice)
        self.assertRaises(TypeError, slice, 1, 2, 3, 4)

    eleza test_repr(self):
        self.assertEqual(repr(slice(1, 2, 3)), "slice(1, 2, 3)")

    eleza test_hash(self):
        # Verify clearing of SF bug #800796
        self.assertRaises(TypeError, hash, slice(5))
        with self.assertRaises(TypeError):
            slice(5).__hash__()

    eleza test_cmp(self):
        s1 = slice(1, 2, 3)
        s2 = slice(1, 2, 3)
        s3 = slice(1, 2, 4)
        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s3)
        self.assertNotEqual(s1, None)
        self.assertNotEqual(s1, (1, 2, 3))
        self.assertNotEqual(s1, "")

        kundi Exc(Exception):
            pass

        kundi BadCmp(object):
            eleza __eq__(self, other):
                raise Exc

        s1 = slice(BadCmp())
        s2 = slice(BadCmp())
        self.assertEqual(s1, s1)
        self.assertRaises(Exc, lambda: s1 == s2)

        s1 = slice(1, BadCmp())
        s2 = slice(1, BadCmp())
        self.assertEqual(s1, s1)
        self.assertRaises(Exc, lambda: s1 == s2)

        s1 = slice(1, 2, BadCmp())
        s2 = slice(1, 2, BadCmp())
        self.assertEqual(s1, s1)
        self.assertRaises(Exc, lambda: s1 == s2)

    eleza test_members(self):
        s = slice(1)
        self.assertEqual(s.start, None)
        self.assertEqual(s.stop, 1)
        self.assertEqual(s.step, None)

        s = slice(1, 2)
        self.assertEqual(s.start, 1)
        self.assertEqual(s.stop, 2)
        self.assertEqual(s.step, None)

        s = slice(1, 2, 3)
        self.assertEqual(s.start, 1)
        self.assertEqual(s.stop, 2)
        self.assertEqual(s.step, 3)

        kundi AnyClass:
            pass

        obj = AnyClass()
        s = slice(obj)
        self.assertTrue(s.stop is obj)

    eleza check_indices(self, slice, length):
        try:
            actual = slice.indices(length)
        except ValueError:
            actual = "valueerror"
        try:
            expected = slice_indices(slice, length)
        except ValueError:
            expected = "valueerror"
        self.assertEqual(actual, expected)

        ikiwa length >= 0 and slice.step != 0:
            actual = range(*slice.indices(length))
            expected = range(length)[slice]
            self.assertEqual(actual, expected)

    eleza test_indices(self):
        self.assertEqual(slice(None           ).indices(10), (0, 10,  1))
        self.assertEqual(slice(None,  None,  2).indices(10), (0, 10,  2))
        self.assertEqual(slice(1,     None,  2).indices(10), (1, 10,  2))
        self.assertEqual(slice(None,  None, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(None,  None, -2).indices(10), (9, -1, -2))
        self.assertEqual(slice(3,     None, -2).indices(10), (3, -1, -2))
        # issue 3004 tests
        self.assertEqual(slice(None, -9).indices(10), (0, 1, 1))
        self.assertEqual(slice(None, -10).indices(10), (0, 0, 1))
        self.assertEqual(slice(None, -11).indices(10), (0, 0, 1))
        self.assertEqual(slice(None, -10, -1).indices(10), (9, 0, -1))
        self.assertEqual(slice(None, -11, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(None, -12, -1).indices(10), (9, -1, -1))
        self.assertEqual(slice(None, 9).indices(10), (0, 9, 1))
        self.assertEqual(slice(None, 10).indices(10), (0, 10, 1))
        self.assertEqual(slice(None, 11).indices(10), (0, 10, 1))
        self.assertEqual(slice(None, 8, -1).indices(10), (9, 8, -1))
        self.assertEqual(slice(None, 9, -1).indices(10), (9, 9, -1))
        self.assertEqual(slice(None, 10, -1).indices(10), (9, 9, -1))

        self.assertEqual(
            slice(-100,  100     ).indices(10),
            slice(None).indices(10)
        )
        self.assertEqual(
            slice(100,  -100,  -1).indices(10),
            slice(None, None, -1).indices(10)
        )
        self.assertEqual(slice(-100, 100, 2).indices(10), (0, 10,  2))

        self.assertEqual(list(range(10))[::sys.maxsize - 1], [0])

        # Check a variety of start, stop, step and length values, including
        # values exceeding sys.maxsize (see issue #14794).
        vals = [None, -2**100, -2**30, -53, -7, -1, 0, 1, 7, 53, 2**30, 2**100]
        lengths = [0, 1, 7, 53, 2**30, 2**100]
        for slice_args in itertools.product(vals, repeat=3):
            s = slice(*slice_args)
            for length in lengths:
                self.check_indices(s, length)
        self.check_indices(slice(0, 10, 1), -3)

        # Negative length should raise ValueError
        with self.assertRaises(ValueError):
            slice(None).indices(-1)

        # Zero step should raise ValueError
        with self.assertRaises(ValueError):
            slice(0, 10, 0).indices(5)

        # Using a start, stop or step or length that can't be interpreted as an
        # integer should give a TypeError ...
        with self.assertRaises(TypeError):
            slice(0.0, 10, 1).indices(5)
        with self.assertRaises(TypeError):
            slice(0, 10.0, 1).indices(5)
        with self.assertRaises(TypeError):
            slice(0, 10, 1.0).indices(5)
        with self.assertRaises(TypeError):
            slice(0, 10, 1).indices(5.0)

        # ... but it should be fine to use a custom kundi that provides index.
        self.assertEqual(slice(0, 10, 1).indices(5), (0, 5, 1))
        self.assertEqual(slice(MyIndexable(0), 10, 1).indices(5), (0, 5, 1))
        self.assertEqual(slice(0, MyIndexable(10), 1).indices(5), (0, 5, 1))
        self.assertEqual(slice(0, 10, MyIndexable(1)).indices(5), (0, 5, 1))
        self.assertEqual(slice(0, 10, 1).indices(MyIndexable(5)), (0, 5, 1))

    eleza test_setslice_without_getslice(self):
        tmp = []
        kundi X(object):
            eleza __setitem__(self, i, k):
                tmp.append((i, k))

        x = X()
        x[1:2] = 42
        self.assertEqual(tmp, [(slice(1, 2), 42)])

    eleza test_pickle(self):
        s = slice(10, 20, 3)
        for protocol in (0,1,2):
            t = loads(dumps(s, protocol))
            self.assertEqual(s, t)
            self.assertEqual(s.indices(15), t.indices(15))
            self.assertNotEqual(id(s), id(t))

    eleza test_cycle(self):
        kundi myobj(): pass
        o = myobj()
        o.s = slice(o)
        w = weakref.ref(o)
        o = None
        support.gc_collect()
        self.assertIsNone(w())

ikiwa __name__ == "__main__":
    unittest.main()
