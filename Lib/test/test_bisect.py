agiza sys
agiza unittest
kutoka test agiza support
kutoka collections agiza UserList

py_bisect = support.import_fresh_module('bisect', blocked=['_bisect'])
c_bisect = support.import_fresh_module('bisect', fresh=['_bisect'])

kundi Range(object):
    """A trivial range()-like object that has an insert() method."""
    eleza __init__(self, start, stop):
        self.start = start
        self.stop = stop
        self.last_insert = Tupu

    eleza __len__(self):
        rudisha self.stop - self.start

    eleza __getitem__(self, idx):
        n = self.stop - self.start
        ikiwa idx < 0:
            idx += n
        ikiwa idx >= n:
            ashiria IndexError(idx)
        rudisha self.start + idx

    eleza insert(self, idx, item):
        self.last_insert = idx, item


kundi TestBisect:
    eleza setUp(self):
        self.precomputedCases = [
            (self.module.bisect_right, [], 1, 0),
            (self.module.bisect_right, [1], 0, 0),
            (self.module.bisect_right, [1], 1, 1),
            (self.module.bisect_right, [1], 2, 1),
            (self.module.bisect_right, [1, 1], 0, 0),
            (self.module.bisect_right, [1, 1], 1, 2),
            (self.module.bisect_right, [1, 1], 2, 2),
            (self.module.bisect_right, [1, 1, 1], 0, 0),
            (self.module.bisect_right, [1, 1, 1], 1, 3),
            (self.module.bisect_right, [1, 1, 1], 2, 3),
            (self.module.bisect_right, [1, 1, 1, 1], 0, 0),
            (self.module.bisect_right, [1, 1, 1, 1], 1, 4),
            (self.module.bisect_right, [1, 1, 1, 1], 2, 4),
            (self.module.bisect_right, [1, 2], 0, 0),
            (self.module.bisect_right, [1, 2], 1, 1),
            (self.module.bisect_right, [1, 2], 1.5, 1),
            (self.module.bisect_right, [1, 2], 2, 2),
            (self.module.bisect_right, [1, 2], 3, 2),
            (self.module.bisect_right, [1, 1, 2, 2], 0, 0),
            (self.module.bisect_right, [1, 1, 2, 2], 1, 2),
            (self.module.bisect_right, [1, 1, 2, 2], 1.5, 2),
            (self.module.bisect_right, [1, 1, 2, 2], 2, 4),
            (self.module.bisect_right, [1, 1, 2, 2], 3, 4),
            (self.module.bisect_right, [1, 2, 3], 0, 0),
            (self.module.bisect_right, [1, 2, 3], 1, 1),
            (self.module.bisect_right, [1, 2, 3], 1.5, 1),
            (self.module.bisect_right, [1, 2, 3], 2, 2),
            (self.module.bisect_right, [1, 2, 3], 2.5, 2),
            (self.module.bisect_right, [1, 2, 3], 3, 3),
            (self.module.bisect_right, [1, 2, 3], 4, 3),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 0, 0),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 1, 1),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 1.5, 1),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2, 3),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2.5, 3),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3, 6),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3.5, 6),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 4, 10),
            (self.module.bisect_right, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 5, 10),

            (self.module.bisect_left, [], 1, 0),
            (self.module.bisect_left, [1], 0, 0),
            (self.module.bisect_left, [1], 1, 0),
            (self.module.bisect_left, [1], 2, 1),
            (self.module.bisect_left, [1, 1], 0, 0),
            (self.module.bisect_left, [1, 1], 1, 0),
            (self.module.bisect_left, [1, 1], 2, 2),
            (self.module.bisect_left, [1, 1, 1], 0, 0),
            (self.module.bisect_left, [1, 1, 1], 1, 0),
            (self.module.bisect_left, [1, 1, 1], 2, 3),
            (self.module.bisect_left, [1, 1, 1, 1], 0, 0),
            (self.module.bisect_left, [1, 1, 1, 1], 1, 0),
            (self.module.bisect_left, [1, 1, 1, 1], 2, 4),
            (self.module.bisect_left, [1, 2], 0, 0),
            (self.module.bisect_left, [1, 2], 1, 0),
            (self.module.bisect_left, [1, 2], 1.5, 1),
            (self.module.bisect_left, [1, 2], 2, 1),
            (self.module.bisect_left, [1, 2], 3, 2),
            (self.module.bisect_left, [1, 1, 2, 2], 0, 0),
            (self.module.bisect_left, [1, 1, 2, 2], 1, 0),
            (self.module.bisect_left, [1, 1, 2, 2], 1.5, 2),
            (self.module.bisect_left, [1, 1, 2, 2], 2, 2),
            (self.module.bisect_left, [1, 1, 2, 2], 3, 4),
            (self.module.bisect_left, [1, 2, 3], 0, 0),
            (self.module.bisect_left, [1, 2, 3], 1, 0),
            (self.module.bisect_left, [1, 2, 3], 1.5, 1),
            (self.module.bisect_left, [1, 2, 3], 2, 1),
            (self.module.bisect_left, [1, 2, 3], 2.5, 2),
            (self.module.bisect_left, [1, 2, 3], 3, 2),
            (self.module.bisect_left, [1, 2, 3], 4, 3),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 0, 0),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 1, 0),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 1.5, 1),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2, 1),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 2.5, 3),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3, 3),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 3.5, 6),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 4, 6),
            (self.module.bisect_left, [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], 5, 10)
        ]

    eleza test_precomputed(self):
        kila func, data, elem, expected kwenye self.precomputedCases:
            self.assertEqual(func(data, elem), expected)
            self.assertEqual(func(UserList(data), elem), expected)

    eleza test_negative_lo(self):
        # Issue 3301
        mod = self.module
        self.assertRaises(ValueError, mod.bisect_left, [1, 2, 3], 5, -1, 3)
        self.assertRaises(ValueError, mod.bisect_right, [1, 2, 3], 5, -1, 3)
        self.assertRaises(ValueError, mod.insort_left, [1, 2, 3], 5, -1, 3)
        self.assertRaises(ValueError, mod.insort_right, [1, 2, 3], 5, -1, 3)

    eleza test_large_range(self):
        # Issue 13496
        mod = self.module
        n = sys.maxsize
        data = range(n-1)
        self.assertEqual(mod.bisect_left(data, n-3), n-3)
        self.assertEqual(mod.bisect_right(data, n-3), n-2)
        self.assertEqual(mod.bisect_left(data, n-3, n-10, n), n-3)
        self.assertEqual(mod.bisect_right(data, n-3, n-10, n), n-2)

    eleza test_large_pyrange(self):
        # Same kama above, but without C-imposed limits on range() parameters
        mod = self.module
        n = sys.maxsize
        data = Range(0, n-1)
        self.assertEqual(mod.bisect_left(data, n-3), n-3)
        self.assertEqual(mod.bisect_right(data, n-3), n-2)
        self.assertEqual(mod.bisect_left(data, n-3, n-10, n), n-3)
        self.assertEqual(mod.bisect_right(data, n-3, n-10, n), n-2)
        x = n - 100
        mod.insort_left(data, x, x - 50, x + 50)
        self.assertEqual(data.last_insert, (x, x))
        x = n - 200
        mod.insort_right(data, x, x - 50, x + 50)
        self.assertEqual(data.last_insert, (x + 1, x))

    eleza test_random(self, n=25):
        kutoka random agiza randrange
        kila i kwenye range(n):
            data = [randrange(0, n, 2) kila j kwenye range(i)]
            data.sort()
            elem = randrange(-1, n+1)
            ip = self.module.bisect_left(data, elem)
            ikiwa ip < len(data):
                self.assertKweli(elem <= data[ip])
            ikiwa ip > 0:
                self.assertKweli(data[ip-1] < elem)
            ip = self.module.bisect_right(data, elem)
            ikiwa ip < len(data):
                self.assertKweli(elem < data[ip])
            ikiwa ip > 0:
                self.assertKweli(data[ip-1] <= elem)

    eleza test_optionalSlicing(self):
        kila func, data, elem, expected kwenye self.precomputedCases:
            kila lo kwenye range(4):
                lo = min(len(data), lo)
                kila hi kwenye range(3,8):
                    hi = min(len(data), hi)
                    ip = func(data, elem, lo, hi)
                    self.assertKweli(lo <= ip <= hi)
                    ikiwa func ni self.module.bisect_left na ip < hi:
                        self.assertKweli(elem <= data[ip])
                    ikiwa func ni self.module.bisect_left na ip > lo:
                        self.assertKweli(data[ip-1] < elem)
                    ikiwa func ni self.module.bisect_right na ip < hi:
                        self.assertKweli(elem < data[ip])
                    ikiwa func ni self.module.bisect_right na ip > lo:
                        self.assertKweli(data[ip-1] <= elem)
                    self.assertEqual(ip, max(lo, min(hi, expected)))

    eleza test_backcompatibility(self):
        self.assertEqual(self.module.bisect, self.module.bisect_right)

    eleza test_keyword_args(self):
        data = [10, 20, 30, 40, 50]
        self.assertEqual(self.module.bisect_left(a=data, x=25, lo=1, hi=3), 2)
        self.assertEqual(self.module.bisect_right(a=data, x=25, lo=1, hi=3), 2)
        self.assertEqual(self.module.bisect(a=data, x=25, lo=1, hi=3), 2)
        self.module.insort_left(a=data, x=25, lo=1, hi=3)
        self.module.insort_right(a=data, x=25, lo=1, hi=3)
        self.module.insort(a=data, x=25, lo=1, hi=3)
        self.assertEqual(data, [10, 20, 25, 25, 25, 30, 40, 50])

kundi TestBisectPython(TestBisect, unittest.TestCase):
    module = py_bisect

kundi TestBisectC(TestBisect, unittest.TestCase):
    module = c_bisect

#==============================================================================

kundi TestInsort:
    eleza test_vsBuiltinSort(self, n=500):
        kutoka random agiza choice
        kila insorted kwenye (list(), UserList()):
            kila i kwenye range(n):
                digit = choice("0123456789")
                ikiwa digit kwenye "02468":
                    f = self.module.insort_left
                isipokua:
                    f = self.module.insort_right
                f(insorted, digit)
            self.assertEqual(sorted(insorted), insorted)

    eleza test_backcompatibility(self):
        self.assertEqual(self.module.insort, self.module.insort_right)

    eleza test_listDerived(self):
        kundi List(list):
            data = []
            eleza insert(self, index, item):
                self.data.insert(index, item)

        lst = List()
        self.module.insort_left(lst, 10)
        self.module.insort_right(lst, 5)
        self.assertEqual([5, 10], lst.data)

kundi TestInsortPython(TestInsort, unittest.TestCase):
    module = py_bisect

kundi TestInsortC(TestInsort, unittest.TestCase):
    module = c_bisect

#==============================================================================

kundi LenOnly:
    "Dummy sequence kundi defining __len__ but sio __getitem__."
    eleza __len__(self):
        rudisha 10

kundi GetOnly:
    "Dummy sequence kundi defining __getitem__ but sio __len__."
    eleza __getitem__(self, ndx):
        rudisha 10

kundi CmpErr:
    "Dummy element that always raises an error during comparison"
    eleza __lt__(self, other):
        ashiria ZeroDivisionError
    __gt__ = __lt__
    __le__ = __lt__
    __ge__ = __lt__
    __eq__ = __lt__
    __ne__ = __lt__

kundi TestErrorHandling:
    eleza test_non_sequence(self):
        kila f kwenye (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(TypeError, f, 10, 10)

    eleza test_len_only(self):
        kila f kwenye (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(TypeError, f, LenOnly(), 10)

    eleza test_get_only(self):
        kila f kwenye (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(TypeError, f, GetOnly(), 10)

    eleza test_cmp_err(self):
        seq = [CmpErr(), CmpErr(), CmpErr()]
        kila f kwenye (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(ZeroDivisionError, f, seq, 10)

    eleza test_arg_parsing(self):
        kila f kwenye (self.module.bisect_left, self.module.bisect_right,
                  self.module.insort_left, self.module.insort_right):
            self.assertRaises(TypeError, f, 10)

kundi TestErrorHandlingPython(TestErrorHandling, unittest.TestCase):
    module = py_bisect

kundi TestErrorHandlingC(TestErrorHandling, unittest.TestCase):
    module = c_bisect

#==============================================================================

kundi TestDocExample:
    eleza test_grades(self):
        eleza grade(score, komapoints=[60, 70, 80, 90], grades='FDCBA'):
            i = self.module.bisect(komapoints, score)
            rudisha grades[i]

        result = [grade(score) kila score kwenye [33, 99, 77, 70, 89, 90, 100]]
        self.assertEqual(result, ['F', 'A', 'C', 'C', 'B', 'A', 'A'])

    eleza test_colors(self):
        data = [('red', 5), ('blue', 1), ('yellow', 8), ('black', 0)]
        data.sort(key=lambda r: r[1])
        keys = [r[1] kila r kwenye data]
        bisect_left = self.module.bisect_left
        self.assertEqual(data[bisect_left(keys, 0)], ('black', 0))
        self.assertEqual(data[bisect_left(keys, 1)], ('blue', 1))
        self.assertEqual(data[bisect_left(keys, 5)], ('red', 5))
        self.assertEqual(data[bisect_left(keys, 8)], ('yellow', 8))

kundi TestDocExamplePython(TestDocExample, unittest.TestCase):
    module = py_bisect

kundi TestDocExampleC(TestDocExample, unittest.TestCase):
    module = c_bisect

#------------------------------------------------------------------------------

ikiwa __name__ == "__main__":
    unittest.main()
