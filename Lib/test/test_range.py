# Python test set -- built-in functions

agiza unittest
agiza sys
agiza pickle
agiza itertools

# pure Python implementations (3 args only), kila comparison
eleza pyrange(start, stop, step):
    ikiwa (start - stop) // step < 0:
        # replace stop ukijumuisha next element kwenye the sequence of integers
        # that are congruent to start modulo step.
        stop += (start - stop) % step
        wakati start != stop:
            tuma start
            start += step

eleza pyrange_reversed(start, stop, step):
    stop += (start - stop) % step
    rudisha pyrange(stop - step, start - step, -step)


kundi RangeTest(unittest.TestCase):
    eleza assert_iterators_equal(self, xs, ys, test_id, limit=Tupu):
        # check that an iterator xs matches the expected results ys,
        # up to a given limit.
        ikiwa limit ni sio Tupu:
            xs = itertools.islice(xs, limit)
            ys = itertools.islice(ys, limit)
        sentinel = object()
        pairs = itertools.zip_longest(xs, ys, fillvalue=sentinel)
        kila i, (x, y) kwenye enumerate(pairs):
            ikiwa x == y:
                endelea
            elikiwa x == sentinel:
                self.fail('{}: iterator ended unexpectedly '
                          'at position {}; expected {}'.format(test_id, i, y))
            elikiwa y == sentinel:
                self.fail('{}: unexpected excess element {} at '
                          'position {}'.format(test_id, x, i))
            isipokua:
                self.fail('{}: wrong element at position {}; '
                          'expected {}, got {}'.format(test_id, i, y, x))

    eleza test_range(self):
        self.assertEqual(list(range(3)), [0, 1, 2])
        self.assertEqual(list(range(1, 5)), [1, 2, 3, 4])
        self.assertEqual(list(range(0)), [])
        self.assertEqual(list(range(-3)), [])
        self.assertEqual(list(range(1, 10, 3)), [1, 4, 7])
        self.assertEqual(list(range(5, -5, -3)), [5, 2, -1, -4])

        a = 10
        b = 100
        c = 50

        self.assertEqual(list(range(a, a+2)), [a, a+1])
        self.assertEqual(list(range(a+2, a, -1)), [a+2, a+1])
        self.assertEqual(list(range(a+4, a, -2)), [a+4, a+2])

        seq = list(range(a, b, c))
        self.assertIn(a, seq)
        self.assertNotIn(b, seq)
        self.assertEqual(len(seq), 2)

        seq = list(range(b, a, -c))
        self.assertIn(b, seq)
        self.assertNotIn(a, seq)
        self.assertEqual(len(seq), 2)

        seq = list(range(-a, -b, -c))
        self.assertIn(-a, seq)
        self.assertNotIn(-b, seq)
        self.assertEqual(len(seq), 2)

        self.assertRaises(TypeError, range)
        self.assertRaises(TypeError, range, 1, 2, 3, 4)
        self.assertRaises(ValueError, range, 1, 2, 0)

        self.assertRaises(TypeError, range, 0.0, 2, 1)
        self.assertRaises(TypeError, range, 1, 2.0, 1)
        self.assertRaises(TypeError, range, 1, 2, 1.0)
        self.assertRaises(TypeError, range, 1e100, 1e101, 1e101)

        self.assertRaises(TypeError, range, 0, "spam")
        self.assertRaises(TypeError, range, 0, 42, "spam")

        self.assertEqual(len(range(0, sys.maxsize, sys.maxsize-1)), 2)

        r = range(-sys.maxsize, sys.maxsize, 2)
        self.assertEqual(len(r), sys.maxsize)

    eleza test_large_operands(self):
        x = range(10**20, 10**20+10, 3)
        self.assertEqual(len(x), 4)
        self.assertEqual(len(list(x)), 4)

        x = range(10**20+10, 10**20, 3)
        self.assertEqual(len(x), 0)
        self.assertEqual(len(list(x)), 0)
        self.assertUongo(x)

        x = range(10**20, 10**20+10, -3)
        self.assertEqual(len(x), 0)
        self.assertEqual(len(list(x)), 0)
        self.assertUongo(x)

        x = range(10**20+10, 10**20, -3)
        self.assertEqual(len(x), 4)
        self.assertEqual(len(list(x)), 4)
        self.assertKweli(x)

        # Now test range() ukijumuisha longs
        kila x kwenye [range(-2**100),
                  range(0, -2**100),
                  range(0, 2**100, -1)]:
            self.assertEqual(list(x), [])
            self.assertUongo(x)

        a = int(10 * sys.maxsize)
        b = int(100 * sys.maxsize)
        c = int(50 * sys.maxsize)

        self.assertEqual(list(range(a, a+2)), [a, a+1])
        self.assertEqual(list(range(a+2, a, -1)), [a+2, a+1])
        self.assertEqual(list(range(a+4, a, -2)), [a+4, a+2])

        seq = list(range(a, b, c))
        self.assertIn(a, seq)
        self.assertNotIn(b, seq)
        self.assertEqual(len(seq), 2)
        self.assertEqual(seq[0], a)
        self.assertEqual(seq[-1], a+c)

        seq = list(range(b, a, -c))
        self.assertIn(b, seq)
        self.assertNotIn(a, seq)
        self.assertEqual(len(seq), 2)
        self.assertEqual(seq[0], b)
        self.assertEqual(seq[-1], b-c)

        seq = list(range(-a, -b, -c))
        self.assertIn(-a, seq)
        self.assertNotIn(-b, seq)
        self.assertEqual(len(seq), 2)
        self.assertEqual(seq[0], -a)
        self.assertEqual(seq[-1], -a-c)

    eleza test_large_range(self):
        # Check long ranges (len > sys.maxsize)
        # len() ni expected to fail due to limitations of the __len__ protocol
        eleza _range_len(x):
            jaribu:
                length = len(x)
            except OverflowError:
                step = x[1] - x[0]
                length = 1 + ((x[-1] - x[0]) // step)
            rudisha length

        a = -sys.maxsize
        b = sys.maxsize
        expected_len = b - a
        x = range(a, b)
        self.assertIn(a, x)
        self.assertNotIn(b, x)
        self.assertRaises(OverflowError, len, x)
        self.assertKweli(x)
        self.assertEqual(_range_len(x), expected_len)
        self.assertEqual(x[0], a)
        idx = sys.maxsize+1
        self.assertEqual(x[idx], a+idx)
        self.assertEqual(x[idx:idx+1][0], a+idx)
        ukijumuisha self.assertRaises(IndexError):
            x[-expected_len-1]
        ukijumuisha self.assertRaises(IndexError):
            x[expected_len]

        a = 0
        b = 2 * sys.maxsize
        expected_len = b - a
        x = range(a, b)
        self.assertIn(a, x)
        self.assertNotIn(b, x)
        self.assertRaises(OverflowError, len, x)
        self.assertKweli(x)
        self.assertEqual(_range_len(x), expected_len)
        self.assertEqual(x[0], a)
        idx = sys.maxsize+1
        self.assertEqual(x[idx], a+idx)
        self.assertEqual(x[idx:idx+1][0], a+idx)
        ukijumuisha self.assertRaises(IndexError):
            x[-expected_len-1]
        ukijumuisha self.assertRaises(IndexError):
            x[expected_len]

        a = 0
        b = sys.maxsize**10
        c = 2*sys.maxsize
        expected_len = 1 + (b - a) // c
        x = range(a, b, c)
        self.assertIn(a, x)
        self.assertNotIn(b, x)
        self.assertRaises(OverflowError, len, x)
        self.assertKweli(x)
        self.assertEqual(_range_len(x), expected_len)
        self.assertEqual(x[0], a)
        idx = sys.maxsize+1
        self.assertEqual(x[idx], a+(idx*c))
        self.assertEqual(x[idx:idx+1][0], a+(idx*c))
        ukijumuisha self.assertRaises(IndexError):
            x[-expected_len-1]
        ukijumuisha self.assertRaises(IndexError):
            x[expected_len]

        a = sys.maxsize**10
        b = 0
        c = -2*sys.maxsize
        expected_len = 1 + (b - a) // c
        x = range(a, b, c)
        self.assertIn(a, x)
        self.assertNotIn(b, x)
        self.assertRaises(OverflowError, len, x)
        self.assertKweli(x)
        self.assertEqual(_range_len(x), expected_len)
        self.assertEqual(x[0], a)
        idx = sys.maxsize+1
        self.assertEqual(x[idx], a+(idx*c))
        self.assertEqual(x[idx:idx+1][0], a+(idx*c))
        ukijumuisha self.assertRaises(IndexError):
            x[-expected_len-1]
        ukijumuisha self.assertRaises(IndexError):
            x[expected_len]

    eleza test_invalid_invocation(self):
        self.assertRaises(TypeError, range)
        self.assertRaises(TypeError, range, 1, 2, 3, 4)
        self.assertRaises(ValueError, range, 1, 2, 0)
        a = int(10 * sys.maxsize)
        self.assertRaises(ValueError, range, a, a + 1, int(0))
        self.assertRaises(TypeError, range, 1., 1., 1.)
        self.assertRaises(TypeError, range, 1e100, 1e101, 1e101)
        self.assertRaises(TypeError, range, 0, "spam")
        self.assertRaises(TypeError, range, 0, 42, "spam")
        # Exercise various combinations of bad arguments, to check
        # refcounting logic
        self.assertRaises(TypeError, range, 0.0)
        self.assertRaises(TypeError, range, 0, 0.0)
        self.assertRaises(TypeError, range, 0.0, 0)
        self.assertRaises(TypeError, range, 0.0, 0.0)
        self.assertRaises(TypeError, range, 0, 0, 1.0)
        self.assertRaises(TypeError, range, 0, 0.0, 1)
        self.assertRaises(TypeError, range, 0, 0.0, 1.0)
        self.assertRaises(TypeError, range, 0.0, 0, 1)
        self.assertRaises(TypeError, range, 0.0, 0, 1.0)
        self.assertRaises(TypeError, range, 0.0, 0.0, 1)
        self.assertRaises(TypeError, range, 0.0, 0.0, 1.0)

    eleza test_index(self):
        u = range(2)
        self.assertEqual(u.index(0), 0)
        self.assertEqual(u.index(1), 1)
        self.assertRaises(ValueError, u.index, 2)

        u = range(-2, 3)
        self.assertEqual(u.count(0), 1)
        self.assertEqual(u.index(0), 2)
        self.assertRaises(TypeError, u.index)

        kundi BadExc(Exception):
            pass

        kundi BadCmp:
            eleza __eq__(self, other):
                ikiwa other == 2:
                     ashiria BadExc()
                rudisha Uongo

        a = range(4)
        self.assertRaises(BadExc, a.index, BadCmp())

        a = range(-2, 3)
        self.assertEqual(a.index(0), 2)
        self.assertEqual(range(1, 10, 3).index(4), 1)
        self.assertEqual(range(1, -10, -3).index(-5), 2)

        self.assertEqual(range(10**20).index(1), 1)
        self.assertEqual(range(10**20).index(10**20 - 1), 10**20 - 1)

        self.assertRaises(ValueError, range(1, 2**100, 2).index, 2**87)
        self.assertEqual(range(1, 2**100, 2).index(2**87+1), 2**86)

        kundi AlwaysEqual(object):
            eleza __eq__(self, other):
                rudisha Kweli
        always_equal = AlwaysEqual()
        self.assertEqual(range(10).index(always_equal), 0)

    eleza test_user_index_method(self):
        bignum = 2*sys.maxsize
        smallnum = 42

        # User-defined kundi ukijumuisha an __index__ method
        kundi I:
            eleza __init__(self, n):
                self.n = int(n)
            eleza __index__(self):
                rudisha self.n
        self.assertEqual(list(range(I(bignum), I(bignum + 1))), [bignum])
        self.assertEqual(list(range(I(smallnum), I(smallnum + 1))), [smallnum])

        # User-defined kundi ukijumuisha a failing __index__ method
        kundi IX:
            eleza __index__(self):
                 ashiria RuntimeError
        self.assertRaises(RuntimeError, range, IX())

        # User-defined kundi ukijumuisha an invalid __index__ method
        kundi IN:
            eleza __index__(self):
                rudisha "not a number"

        self.assertRaises(TypeError, range, IN())

        # Test use of user-defined classes kwenye slice indices.
        self.assertEqual(range(10)[:I(5)], range(5))

        ukijumuisha self.assertRaises(RuntimeError):
            range(0, 10)[:IX()]

        ukijumuisha self.assertRaises(TypeError):
            range(0, 10)[:IN()]

    eleza test_count(self):
        self.assertEqual(range(3).count(-1), 0)
        self.assertEqual(range(3).count(0), 1)
        self.assertEqual(range(3).count(1), 1)
        self.assertEqual(range(3).count(2), 1)
        self.assertEqual(range(3).count(3), 0)
        self.assertIs(type(range(3).count(-1)), int)
        self.assertIs(type(range(3).count(1)), int)
        self.assertEqual(range(10**20).count(1), 1)
        self.assertEqual(range(10**20).count(10**20), 0)
        self.assertEqual(range(3).index(1), 1)
        self.assertEqual(range(1, 2**100, 2).count(2**87), 0)
        self.assertEqual(range(1, 2**100, 2).count(2**87+1), 1)

        kundi AlwaysEqual(object):
            eleza __eq__(self, other):
                rudisha Kweli
        always_equal = AlwaysEqual()
        self.assertEqual(range(10).count(always_equal), 10)

        self.assertEqual(len(range(sys.maxsize, sys.maxsize+10)), 10)

    eleza test_repr(self):
        self.assertEqual(repr(range(1)), 'range(0, 1)')
        self.assertEqual(repr(range(1, 2)), 'range(1, 2)')
        self.assertEqual(repr(range(1, 2, 3)), 'range(1, 2, 3)')

    eleza test_pickling(self):
        testcases = [(13,), (0, 11), (-22, 10), (20, 3, -1),
                     (13, 21, 3), (-2, 2, 2), (2**65, 2**65+2)]
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila t kwenye testcases:
                ukijumuisha self.subTest(proto=proto, test=t):
                    r = range(*t)
                    self.assertEqual(list(pickle.loads(pickle.dumps(r, proto))),
                                     list(r))

    eleza test_iterator_pickling(self):
        testcases = [(13,), (0, 11), (-22, 10), (20, 3, -1),
                     (13, 21, 3), (-2, 2, 2), (2**65, 2**65+2)]
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila t kwenye testcases:
                it = itorg = iter(range(*t))
                data = list(range(*t))

                d = pickle.dumps(it, proto)
                it = pickle.loads(d)
                self.assertEqual(type(itorg), type(it))
                self.assertEqual(list(it), data)

                it = pickle.loads(d)
                jaribu:
                    next(it)
                except StopIteration:
                    endelea
                d = pickle.dumps(it, proto)
                it = pickle.loads(d)
                self.assertEqual(list(it), data[1:])

    eleza test_exhausted_iterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            r = range(2**65, 2**65+2)
            i = iter(r)
            wakati Kweli:
                r = next(i)
                ikiwa r == 2**65+1:
                    koma
            d = pickle.dumps(i, proto)
            i2 = pickle.loads(d)
            self.assertEqual(list(i), [])
            self.assertEqual(list(i2), [])

    eleza test_large_exhausted_iterator_pickling(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            r = range(20)
            i = iter(r)
            wakati Kweli:
                r = next(i)
                ikiwa r == 19:
                    koma
            d = pickle.dumps(i, proto)
            i2 = pickle.loads(d)
            self.assertEqual(list(i), [])
            self.assertEqual(list(i2), [])

    eleza test_odd_bug(self):
        # This used to  ashiria a "SystemError: NULL result without error"
        # because the range validation step was eating the exception
        # before NULL was returned.
        ukijumuisha self.assertRaises(TypeError):
            range([], 1, -1)

    eleza test_types(self):
        # Non-integer objects *equal* to any of the range's items are supposed
        # to be contained kwenye the range.
        self.assertIn(1.0, range(3))
        self.assertIn(Kweli, range(3))
        self.assertIn(1+0j, range(3))

        kundi C1:
            eleza __eq__(self, other): rudisha Kweli
        self.assertIn(C1(), range(3))

        # Objects are never coerced into other types kila comparison.
        kundi C2:
            eleza __int__(self): rudisha 1
            eleza __index__(self): rudisha 1
        self.assertNotIn(C2(), range(3))
        # ..except ikiwa explicitly told so.
        self.assertIn(int(C2()), range(3))

        # Check that the range.__contains__ optimization ni only
        # used kila ints, sio kila instances of subclasses of int.
        kundi C3(int):
            eleza __eq__(self, other): rudisha Kweli
        self.assertIn(C3(11), range(10))
        self.assertIn(C3(11), list(range(10)))

    eleza test_strided_limits(self):
        r = range(0, 101, 2)
        self.assertIn(0, r)
        self.assertNotIn(1, r)
        self.assertIn(2, r)
        self.assertNotIn(99, r)
        self.assertIn(100, r)
        self.assertNotIn(101, r)

        r = range(0, -20, -1)
        self.assertIn(0, r)
        self.assertIn(-1, r)
        self.assertIn(-19, r)
        self.assertNotIn(-20, r)

        r = range(0, -20, -2)
        self.assertIn(-18, r)
        self.assertNotIn(-19, r)
        self.assertNotIn(-20, r)

    eleza test_empty(self):
        r = range(0)
        self.assertNotIn(0, r)
        self.assertNotIn(1, r)

        r = range(0, -10)
        self.assertNotIn(0, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(1, r)

    eleza test_range_iterators(self):
        # exercise 'fast' iterators, that use a rangeiterobject internally.
        # see issue 7298
        limits = [base + jiggle
                  kila M kwenye (2**32, 2**64)
                  kila base kwenye (-M, -M//2, 0, M//2, M)
                  kila jiggle kwenye (-2, -1, 0, 1, 2)]
        test_ranges = [(start, end, step)
                       kila start kwenye limits
                       kila end kwenye limits
                       kila step kwenye (-2**63, -2**31, -2, -1, 1, 2)]

        kila start, end, step kwenye test_ranges:
            iter1 = range(start, end, step)
            iter2 = pyrange(start, end, step)
            test_id = "range({}, {}, {})".format(start, end, step)
            # check first 100 entries
            self.assert_iterators_equal(iter1, iter2, test_id, limit=100)

            iter1 = reversed(range(start, end, step))
            iter2 = pyrange_reversed(start, end, step)
            test_id = "reversed(range({}, {}, {}))".format(start, end, step)
            self.assert_iterators_equal(iter1, iter2, test_id, limit=100)

    eleza test_range_iterators_invocation(self):
        # verify range iterators instances cannot be created by
        # calling their type
        rangeiter_type = type(iter(range(0)))
        self.assertRaises(TypeError, rangeiter_type, 1, 3, 1)
        long_rangeiter_type = type(iter(range(1 << 1000)))
        self.assertRaises(TypeError, long_rangeiter_type, 1, 3, 1)

    eleza test_slice(self):
        eleza check(start, stop, step=Tupu):
            i = slice(start, stop, step)
            self.assertEqual(list(r[i]), list(r)[i])
            self.assertEqual(len(r[i]), len(list(r)[i]))
        kila r kwenye [range(10),
                  range(0),
                  range(1, 9, 3),
                  range(8, 0, -3),
                  range(sys.maxsize+1, sys.maxsize+10),
                  ]:
            check(0, 2)
            check(0, 20)
            check(1, 2)
            check(20, 30)
            check(-30, -20)
            check(-1, 100, 2)
            check(0, -1)
            check(-1, -3, -1)

    eleza test_contains(self):
        r = range(10)
        self.assertIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(9, -1, -1)
        self.assertIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(0, 10, 2)
        self.assertIn(0, r)
        self.assertNotIn(1, r)
        self.assertNotIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)
        r = range(9, -1, -2)
        self.assertNotIn(0, r)
        self.assertIn(1, r)
        self.assertIn(5.0, r)
        self.assertNotIn(5.1, r)
        self.assertNotIn(-1, r)
        self.assertNotIn(10, r)
        self.assertNotIn("", r)

    eleza test_reverse_iteration(self):
        kila r kwenye [range(10),
                  range(0),
                  range(1, 9, 3),
                  range(8, 0, -3),
                  range(sys.maxsize+1, sys.maxsize+10),
                  ]:
            self.assertEqual(list(reversed(r)), list(r)[::-1])

    eleza test_issue11845(self):
        r = range(*slice(1, 18, 2).indices(20))
        values = {Tupu, 0, 1, -1, 2, -2, 5, -5, 19, -19,
                  20, -20, 21, -21, 30, -30, 99, -99}
        kila i kwenye values:
            kila j kwenye values:
                kila k kwenye values - {0}:
                    r[i:j:k]

    eleza test_comparison(self):
        test_ranges = [range(0), range(0, -1), range(1, 1, 3),
                       range(1), range(5, 6), range(5, 6, 2),
                       range(5, 7, 2), range(2), range(0, 4, 2),
                       range(0, 5, 2), range(0, 6, 2)]
        test_tuples = list(map(tuple, test_ranges))

        # Check that equality of ranges matches equality of the corresponding
        # tuples kila each pair kutoka the test lists above.
        ranges_eq = [a == b kila a kwenye test_ranges kila b kwenye test_ranges]
        tuples_eq = [a == b kila a kwenye test_tuples kila b kwenye test_tuples]
        self.assertEqual(ranges_eq, tuples_eq)

        # Check that != correctly gives the logical negation of ==
        ranges_ne = [a != b kila a kwenye test_ranges kila b kwenye test_ranges]
        self.assertEqual(ranges_ne, [not x kila x kwenye ranges_eq])

        # Equal ranges should have equal hashes.
        kila a kwenye test_ranges:
            kila b kwenye test_ranges:
                ikiwa a == b:
                    self.assertEqual(hash(a), hash(b))

        # Ranges are unequal to other types (even sequence types)
        self.assertIs(range(0) == (), Uongo)
        self.assertIs(() == range(0), Uongo)
        self.assertIs(range(2) == [0, 1], Uongo)

        # Huge integers aren't a problem.
        self.assertEqual(range(0, 2**100 - 1, 2),
                         range(0, 2**100, 2))
        self.assertEqual(hash(range(0, 2**100 - 1, 2)),
                         hash(range(0, 2**100, 2)))
        self.assertNotEqual(range(0, 2**100, 2),
                            range(0, 2**100 + 1, 2))
        self.assertEqual(range(2**200, 2**201 - 2**99, 2**100),
                         range(2**200, 2**201, 2**100))
        self.assertEqual(hash(range(2**200, 2**201 - 2**99, 2**100)),
                         hash(range(2**200, 2**201, 2**100)))
        self.assertNotEqual(range(2**200, 2**201, 2**100),
                            range(2**200, 2**201 + 1, 2**100))

        # Order comparisons are sio implemented kila ranges.
        ukijumuisha self.assertRaises(TypeError):
            range(0) < range(0)
        ukijumuisha self.assertRaises(TypeError):
            range(0) > range(0)
        ukijumuisha self.assertRaises(TypeError):
            range(0) <= range(0)
        ukijumuisha self.assertRaises(TypeError):
            range(0) >= range(0)


    eleza test_attributes(self):
        # test the start, stop na step attributes of range objects
        self.assert_attrs(range(0), 0, 0, 1)
        self.assert_attrs(range(10), 0, 10, 1)
        self.assert_attrs(range(-10), 0, -10, 1)
        self.assert_attrs(range(0, 10, 1), 0, 10, 1)
        self.assert_attrs(range(0, 10, 3), 0, 10, 3)
        self.assert_attrs(range(10, 0, -1), 10, 0, -1)
        self.assert_attrs(range(10, 0, -3), 10, 0, -3)

    eleza assert_attrs(self, rangeobj, start, stop, step):
        self.assertEqual(rangeobj.start, start)
        self.assertEqual(rangeobj.stop, stop)
        self.assertEqual(rangeobj.step, step)

        ukijumuisha self.assertRaises(AttributeError):
            rangeobj.start = 0
        ukijumuisha self.assertRaises(AttributeError):
            rangeobj.stop = 10
        ukijumuisha self.assertRaises(AttributeError):
            rangeobj.step = 1

        ukijumuisha self.assertRaises(AttributeError):
            toa rangeobj.start
        ukijumuisha self.assertRaises(AttributeError):
            toa rangeobj.stop
        ukijumuisha self.assertRaises(AttributeError):
            toa rangeobj.step

ikiwa __name__ == "__main__":
    unittest.main()
