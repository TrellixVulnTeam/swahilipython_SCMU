kutoka test agiza support
agiza random
agiza unittest
kutoka functools agiza cmp_to_key

verbose = support.verbose
nerrors = 0


eleza check(tag, expected, raw, compare=None):
    global nerrors

    ikiwa verbose:
        andika("    checking", tag)

    orig = raw[:]   # save input in case of error
    ikiwa compare:
        raw.sort(key=cmp_to_key(compare))
    else:
        raw.sort()

    ikiwa len(expected) != len(raw):
        andika("error in", tag)
        andika("length mismatch;", len(expected), len(raw))
        andika(expected)
        andika(orig)
        andika(raw)
        nerrors += 1
        return

    for i, good in enumerate(expected):
        maybe = raw[i]
        ikiwa good is not maybe:
            andika("error in", tag)
            andika("out of order at index", i, good, maybe)
            andika(expected)
            andika(orig)
            andika(raw)
            nerrors += 1
            return

kundi TestBase(unittest.TestCase):
    eleza testStressfully(self):
        # Try a variety of sizes at and around powers of 2, and at powers of 10.
        sizes = [0]
        for power in range(1, 10):
            n = 2 ** power
            sizes.extend(range(n-1, n+2))
        sizes.extend([10, 100, 1000])

        kundi Complains(object):
            maybe_complain = True

            eleza __init__(self, i):
                self.i = i

            eleza __lt__(self, other):
                ikiwa Complains.maybe_complain and random.random() < 0.001:
                    ikiwa verbose:
                        andika("        complaining at", self, other)
                    raise RuntimeError
                rudisha self.i < other.i

            eleza __repr__(self):
                rudisha "Complains(%d)" % self.i

        kundi Stable(object):
            eleza __init__(self, key, i):
                self.key = key
                self.index = i

            eleza __lt__(self, other):
                rudisha self.key < other.key

            eleza __repr__(self):
                rudisha "Stable(%d, %d)" % (self.key, self.index)

        for n in sizes:
            x = list(range(n))
            ikiwa verbose:
                andika("Testing size", n)

            s = x[:]
            check("identity", x, s)

            s = x[:]
            s.reverse()
            check("reversed", x, s)

            s = x[:]
            random.shuffle(s)
            check("random permutation", x, s)

            y = x[:]
            y.reverse()
            s = x[:]
            check("reversed via function", y, s, lambda a, b: (b>a)-(b<a))

            ikiwa verbose:
                andika("    Checking against an insane comparison function.")
                andika("        If the implementation isn't careful, this may segfault.")
            s = x[:]
            s.sort(key=cmp_to_key(lambda a, b:  int(random.random() * 3) - 1))
            check("an insane function left some permutation", x, s)

            ikiwa len(x) >= 2:
                eleza bad_key(x):
                    raise RuntimeError
                s = x[:]
                self.assertRaises(RuntimeError, s.sort, key=bad_key)

            x = [Complains(i) for i in x]
            s = x[:]
            random.shuffle(s)
            Complains.maybe_complain = True
            it_complained = False
            try:
                s.sort()
            except RuntimeError:
                it_complained = True
            ikiwa it_complained:
                Complains.maybe_complain = False
                check("exception during sort left some permutation", x, s)

            s = [Stable(random.randrange(10), i) for i in range(n)]
            augmented = [(e, e.index) for e in s]
            augmented.sort()    # forced stable because ties broken by index
            x = [e for e, i in augmented] # a stable sort of s
            check("stability", x, s)

#==============================================================================

kundi TestBugs(unittest.TestCase):

    eleza test_bug453523(self):
        # bug 453523 -- list.sort() crasher.
        # If this fails, the most likely outcome is a core dump.
        # Mutations during a list sort should raise a ValueError.

        kundi C:
            eleza __lt__(self, other):
                ikiwa L and random.random() < 0.75:
                    L.pop()
                else:
                    L.append(3)
                rudisha random.random() < 0.5

        L = [C() for i in range(50)]
        self.assertRaises(ValueError, L.sort)

    eleza test_undetected_mutation(self):
        # Python 2.4a1 did not always detect mutation
        memorywaster = []
        for i in range(20):
            eleza mutating_cmp(x, y):
                L.append(3)
                L.pop()
                rudisha (x > y) - (x < y)
            L = [1,2]
            self.assertRaises(ValueError, L.sort, key=cmp_to_key(mutating_cmp))
            eleza mutating_cmp(x, y):
                L.append(3)
                del L[:]
                rudisha (x > y) - (x < y)
            self.assertRaises(ValueError, L.sort, key=cmp_to_key(mutating_cmp))
            memorywaster = [memorywaster]

#==============================================================================

kundi TestDecorateSortUndecorate(unittest.TestCase):

    eleza test_decorated(self):
        data = 'The quick Brown fox Jumped over The lazy Dog'.split()
        copy = data[:]
        random.shuffle(data)
        data.sort(key=str.lower)
        eleza my_cmp(x, y):
            xlower, ylower = x.lower(), y.lower()
            rudisha (xlower > ylower) - (xlower < ylower)
        copy.sort(key=cmp_to_key(my_cmp))

    eleza test_baddecorator(self):
        data = 'The quick Brown fox Jumped over The lazy Dog'.split()
        self.assertRaises(TypeError, data.sort, key=lambda x,y: 0)

    eleza test_stability(self):
        data = [(random.randrange(100), i) for i in range(200)]
        copy = data[:]
        data.sort(key=lambda t: t[0])   # sort on the random first field
        copy.sort()                     # sort using both fields
        self.assertEqual(data, copy)    # should get the same result

    eleza test_key_with_exception(self):
        # Verify that the wrapper has been removed
        data = list(range(-2, 2))
        dup = data[:]
        self.assertRaises(ZeroDivisionError, data.sort, key=lambda x: 1/x)
        self.assertEqual(data, dup)

    eleza test_key_with_mutation(self):
        data = list(range(10))
        eleza k(x):
            del data[:]
            data[:] = range(20)
            rudisha x
        self.assertRaises(ValueError, data.sort, key=k)

    eleza test_key_with_mutating_del(self):
        data = list(range(10))
        kundi SortKiller(object):
            eleza __init__(self, x):
                pass
            eleza __del__(self):
                del data[:]
                data[:] = range(20)
            eleza __lt__(self, other):
                rudisha id(self) < id(other)
        self.assertRaises(ValueError, data.sort, key=SortKiller)

    eleza test_key_with_mutating_del_and_exception(self):
        data = list(range(10))
        ## dup = data[:]
        kundi SortKiller(object):
            eleza __init__(self, x):
                ikiwa x > 2:
                    raise RuntimeError
            eleza __del__(self):
                del data[:]
                data[:] = list(range(20))
        self.assertRaises(RuntimeError, data.sort, key=SortKiller)
        ## major honking subtlety: we *can't* do:
        ##
        ## self.assertEqual(data, dup)
        ##
        ## because there is a reference to a SortKiller in the
        ## traceback and by the time it dies we're outside the call to
        ## .sort() and so the list protection gimmicks are out of
        ## date (this cost some brain cells to figure out...).

    eleza test_reverse(self):
        data = list(range(100))
        random.shuffle(data)
        data.sort(reverse=True)
        self.assertEqual(data, list(range(99,-1,-1)))

    eleza test_reverse_stability(self):
        data = [(random.randrange(100), i) for i in range(200)]
        copy1 = data[:]
        copy2 = data[:]
        eleza my_cmp(x, y):
            x0, y0 = x[0], y[0]
            rudisha (x0 > y0) - (x0 < y0)
        eleza my_cmp_reversed(x, y):
            x0, y0 = x[0], y[0]
            rudisha (y0 > x0) - (y0 < x0)
        data.sort(key=cmp_to_key(my_cmp), reverse=True)
        copy1.sort(key=cmp_to_key(my_cmp_reversed))
        self.assertEqual(data, copy1)
        copy2.sort(key=lambda x: x[0], reverse=True)
        self.assertEqual(data, copy2)

#==============================================================================
eleza check_against_PyObject_RichCompareBool(self, L):
    ## The idea here is to exploit the fact that unsafe_tuple_compare uses
    ## PyObject_RichCompareBool for the second elements of tuples. So we have,
    ## for (most) L, sorted(L) == [y[1] for y in sorted([(0,x) for x in L])]
    ## This will work as long as __eq__ => not __lt__ for all the objects in L,
    ## which holds for all the types used below.
    ##
    ## Testing this way ensures that the optimized implementation remains consistent
    ## with the naive implementation, even ikiwa changes are made to any of the
    ## richcompares.
    ##
    ## This function tests sorting for three lists (it randomly shuffles each one):
    ##                        1. L
    ##                        2. [(x,) for x in L]
    ##                        3. [((x,),) for x in L]

    random.seed(0)
    random.shuffle(L)
    L_1 = L[:]
    L_2 = [(x,) for x in L]
    L_3 = [((x,),) for x in L]
    for L in [L_1, L_2, L_3]:
        optimized = sorted(L)
        reference = [y[1] for y in sorted([(0,x) for x in L])]
        for (opt, ref) in zip(optimized, reference):
            self.assertIs(opt, ref)
            #note: not assertEqual! We want to ensure *identical* behavior.

kundi TestOptimizedCompares(unittest.TestCase):
    eleza test_safe_object_compare(self):
        heterogeneous_lists = [[0, 'foo'],
                               [0.0, 'foo'],
                               [('foo',), 'foo']]
        for L in heterogeneous_lists:
            self.assertRaises(TypeError, L.sort)
            self.assertRaises(TypeError, [(x,) for x in L].sort)
            self.assertRaises(TypeError, [((x,),) for x in L].sort)

        float_int_lists = [[1,1.1],
                           [1<<70,1.1],
                           [1.1,1],
                           [1.1,1<<70]]
        for L in float_int_lists:
            check_against_PyObject_RichCompareBool(self, L)

    eleza test_unsafe_object_compare(self):

        # This test is by ppperry. It ensures that unsafe_object_compare is
        # verifying ms->key_richcompare == tp->richcompare before comparing.

        kundi WackyComparator(int):
            eleza __lt__(self, other):
                elem.__class__ = WackyList2
                rudisha int.__lt__(self, other)

        kundi WackyList1(list):
            pass

        kundi WackyList2(list):
            eleza __lt__(self, other):
                raise ValueError

        L = [WackyList1([WackyComparator(i), i]) for i in range(10)]
        elem = L[-1]
        with self.assertRaises(ValueError):
            L.sort()

        L = [WackyList1([WackyComparator(i), i]) for i in range(10)]
        elem = L[-1]
        with self.assertRaises(ValueError):
            [(x,) for x in L].sort()

        # The following test is also by ppperry. It ensures that
        # unsafe_object_compare handles Py_NotImplemented appropriately.
        kundi PointlessComparator:
            eleza __lt__(self, other):
                rudisha NotImplemented
        L = [PointlessComparator(), PointlessComparator()]
        self.assertRaises(TypeError, L.sort)
        self.assertRaises(TypeError, [(x,) for x in L].sort)

        # The following tests go through various types that would trigger
        # ms->key_compare = unsafe_object_compare
        lists = [list(range(100)) + [(1<<70)],
                 [str(x) for x in range(100)] + ['\uffff'],
                 [bytes(x) for x in range(100)],
                 [cmp_to_key(lambda x,y: x<y)(x) for x in range(100)]]
        for L in lists:
            check_against_PyObject_RichCompareBool(self, L)

    eleza test_unsafe_latin_compare(self):
        check_against_PyObject_RichCompareBool(self, [str(x) for
                                                      x in range(100)])

    eleza test_unsafe_long_compare(self):
        check_against_PyObject_RichCompareBool(self, [x for
                                                      x in range(100)])

    eleza test_unsafe_float_compare(self):
        check_against_PyObject_RichCompareBool(self, [float(x) for
                                                      x in range(100)])

    eleza test_unsafe_tuple_compare(self):
        # This test was suggested by Tim Peters. It verifies that the tuple
        # comparison respects the current tuple compare semantics, which do not
        # guarantee that x < x <=> (x,) < (x,)
        #
        # Note that we don't have to put anything in tuples here, because
        # the check function does a tuple test automatically.

        check_against_PyObject_RichCompareBool(self, [float('nan')]*100)
        check_against_PyObject_RichCompareBool(self, [float('nan') for
                                                      _ in range(100)])

    eleza test_not_all_tuples(self):
        self.assertRaises(TypeError, [(1.0, 1.0), (False, "A"), 6].sort)
        self.assertRaises(TypeError, [('a', 1), (1, 'a')].sort)
        self.assertRaises(TypeError, [(1, 'a'), ('a', 1)].sort)
#==============================================================================

ikiwa __name__ == "__main__":
    unittest.main()
