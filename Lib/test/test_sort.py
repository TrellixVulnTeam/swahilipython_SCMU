kutoka test agiza support
agiza random
agiza unittest
kutoka functools agiza cmp_to_key

verbose = support.verbose
nerrors = 0


eleza check(tag, expected, raw, compare=Tupu):
    global nerrors

    ikiwa verbose:
        andika("    checking", tag)

    orig = raw[:]   # save input kwenye case of error
    ikiwa compare:
        raw.sort(key=cmp_to_key(compare))
    isipokua:
        raw.sort()

    ikiwa len(expected) != len(raw):
        andika("error in", tag)
        andika("length mismatch;", len(expected), len(raw))
        andika(expected)
        andika(orig)
        andika(raw)
        nerrors += 1
        return

    kila i, good kwenye enumerate(expected):
        maybe = raw[i]
        ikiwa good ni sio maybe:
            andika("error in", tag)
            andika("out of order at index", i, good, maybe)
            andika(expected)
            andika(orig)
            andika(raw)
            nerrors += 1
            return

kundi TestBase(unittest.TestCase):
    eleza testStressfully(self):
        # Try a variety of sizes at na around powers of 2, na at powers of 10.
        sizes = [0]
        kila power kwenye range(1, 10):
            n = 2 ** power
            sizes.extend(range(n-1, n+2))
        sizes.extend([10, 100, 1000])

        kundi Complains(object):
            maybe_complain = Kweli

            eleza __init__(self, i):
                self.i = i

            eleza __lt__(self, other):
                ikiwa Complains.maybe_complain na random.random() < 0.001:
                    ikiwa verbose:
                        andika("        complaining at", self, other)
                    ashiria RuntimeError
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

        kila n kwenye sizes:
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
                    ashiria RuntimeError
                s = x[:]
                self.assertRaises(RuntimeError, s.sort, key=bad_key)

            x = [Complains(i) kila i kwenye x]
            s = x[:]
            random.shuffle(s)
            Complains.maybe_complain = Kweli
            it_complained = Uongo
            jaribu:
                s.sort()
            tatizo RuntimeError:
                it_complained = Kweli
            ikiwa it_complained:
                Complains.maybe_complain = Uongo
                check("exception during sort left some permutation", x, s)

            s = [Stable(random.randrange(10), i) kila i kwenye range(n)]
            augmented = [(e, e.index) kila e kwenye s]
            augmented.sort()    # forced stable because ties broken by index
            x = [e kila e, i kwenye augmented] # a stable sort of s
            check("stability", x, s)

#==============================================================================

kundi TestBugs(unittest.TestCase):

    eleza test_bug453523(self):
        # bug 453523 -- list.sort() crasher.
        # If this fails, the most likely outcome ni a core dump.
        # Mutations during a list sort should ashiria a ValueError.

        kundi C:
            eleza __lt__(self, other):
                ikiwa L na random.random() < 0.75:
                    L.pop()
                isipokua:
                    L.append(3)
                rudisha random.random() < 0.5

        L = [C() kila i kwenye range(50)]
        self.assertRaises(ValueError, L.sort)

    eleza test_undetected_mutation(self):
        # Python 2.4a1 did sio always detect mutation
        memorywaster = []
        kila i kwenye range(20):
            eleza mutating_cmp(x, y):
                L.append(3)
                L.pop()
                rudisha (x > y) - (x < y)
            L = [1,2]
            self.assertRaises(ValueError, L.sort, key=cmp_to_key(mutating_cmp))
            eleza mutating_cmp(x, y):
                L.append(3)
                toa L[:]
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
        data = [(random.randrange(100), i) kila i kwenye range(200)]
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
            toa data[:]
            data[:] = range(20)
            rudisha x
        self.assertRaises(ValueError, data.sort, key=k)

    eleza test_key_with_mutating_del(self):
        data = list(range(10))
        kundi SortKiller(object):
            eleza __init__(self, x):
                pita
            eleza __del__(self):
                toa data[:]
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
                    ashiria RuntimeError
            eleza __del__(self):
                toa data[:]
                data[:] = list(range(20))
        self.assertRaises(RuntimeError, data.sort, key=SortKiller)
        ## major honking subtlety: we *can't* do:
        ##
        ## self.assertEqual(data, dup)
        ##
        ## because there ni a reference to a SortKiller kwenye the
        ## traceback na by the time it dies we're outside the call to
        ## .sort() na so the list protection gimmicks are out of
        ## date (this cost some brain cells to figure out...).

    eleza test_reverse(self):
        data = list(range(100))
        random.shuffle(data)
        data.sort(reverse=Kweli)
        self.assertEqual(data, list(range(99,-1,-1)))

    eleza test_reverse_stability(self):
        data = [(random.randrange(100), i) kila i kwenye range(200)]
        copy1 = data[:]
        copy2 = data[:]
        eleza my_cmp(x, y):
            x0, y0 = x[0], y[0]
            rudisha (x0 > y0) - (x0 < y0)
        eleza my_cmp_reversed(x, y):
            x0, y0 = x[0], y[0]
            rudisha (y0 > x0) - (y0 < x0)
        data.sort(key=cmp_to_key(my_cmp), reverse=Kweli)
        copy1.sort(key=cmp_to_key(my_cmp_reversed))
        self.assertEqual(data, copy1)
        copy2.sort(key=lambda x: x[0], reverse=Kweli)
        self.assertEqual(data, copy2)

#==============================================================================
eleza check_against_PyObject_RichCompareBool(self, L):
    ## The idea here ni to exploit the fact that unsafe_tuple_compare uses
    ## PyObject_RichCompareBool kila the second elements of tuples. So we have,
    ## kila (most) L, sorted(L) == [y[1] kila y kwenye sorted([(0,x) kila x kwenye L])]
    ## This will work kama long kama __eq__ => sio __lt__ kila all the objects kwenye L,
    ## which holds kila all the types used below.
    ##
    ## Testing this way ensures that the optimized implementation remains consistent
    ## ukijumuisha the naive implementation, even ikiwa changes are made to any of the
    ## richcompares.
    ##
    ## This function tests sorting kila three lists (it randomly shuffles each one):
    ##                        1. L
    ##                        2. [(x,) kila x kwenye L]
    ##                        3. [((x,),) kila x kwenye L]

    random.seed(0)
    random.shuffle(L)
    L_1 = L[:]
    L_2 = [(x,) kila x kwenye L]
    L_3 = [((x,),) kila x kwenye L]
    kila L kwenye [L_1, L_2, L_3]:
        optimized = sorted(L)
        reference = [y[1] kila y kwenye sorted([(0,x) kila x kwenye L])]
        kila (opt, ref) kwenye zip(optimized, reference):
            self.assertIs(opt, ref)
            #note: sio assertEqual! We want to ensure *identical* behavior.

kundi TestOptimizedCompares(unittest.TestCase):
    eleza test_safe_object_compare(self):
        heterogeneous_lists = [[0, 'foo'],
                               [0.0, 'foo'],
                               [('foo',), 'foo']]
        kila L kwenye heterogeneous_lists:
            self.assertRaises(TypeError, L.sort)
            self.assertRaises(TypeError, [(x,) kila x kwenye L].sort)
            self.assertRaises(TypeError, [((x,),) kila x kwenye L].sort)

        float_int_lists = [[1,1.1],
                           [1<<70,1.1],
                           [1.1,1],
                           [1.1,1<<70]]
        kila L kwenye float_int_lists:
            check_against_PyObject_RichCompareBool(self, L)

    eleza test_unsafe_object_compare(self):

        # This test ni by ppperry. It ensures that unsafe_object_compare is
        # verifying ms->key_richcompare == tp->richcompare before comparing.

        kundi WackyComparator(int):
            eleza __lt__(self, other):
                elem.__class__ = WackyList2
                rudisha int.__lt__(self, other)

        kundi WackyList1(list):
            pita

        kundi WackyList2(list):
            eleza __lt__(self, other):
                ashiria ValueError

        L = [WackyList1([WackyComparator(i), i]) kila i kwenye range(10)]
        elem = L[-1]
        ukijumuisha self.assertRaises(ValueError):
            L.sort()

        L = [WackyList1([WackyComparator(i), i]) kila i kwenye range(10)]
        elem = L[-1]
        ukijumuisha self.assertRaises(ValueError):
            [(x,) kila x kwenye L].sort()

        # The following test ni also by ppperry. It ensures that
        # unsafe_object_compare handles Py_NotImplemented appropriately.
        kundi PointlessComparator:
            eleza __lt__(self, other):
                rudisha NotImplemented
        L = [PointlessComparator(), PointlessComparator()]
        self.assertRaises(TypeError, L.sort)
        self.assertRaises(TypeError, [(x,) kila x kwenye L].sort)

        # The following tests go through various types that would trigger
        # ms->key_compare = unsafe_object_compare
        lists = [list(range(100)) + [(1<<70)],
                 [str(x) kila x kwenye range(100)] + ['\uffff'],
                 [bytes(x) kila x kwenye range(100)],
                 [cmp_to_key(lambda x,y: x<y)(x) kila x kwenye range(100)]]
        kila L kwenye lists:
            check_against_PyObject_RichCompareBool(self, L)

    eleza test_unsafe_latin_compare(self):
        check_against_PyObject_RichCompareBool(self, [str(x) for
                                                      x kwenye range(100)])

    eleza test_unsafe_long_compare(self):
        check_against_PyObject_RichCompareBool(self, [x for
                                                      x kwenye range(100)])

    eleza test_unsafe_float_compare(self):
        check_against_PyObject_RichCompareBool(self, [float(x) for
                                                      x kwenye range(100)])

    eleza test_unsafe_tuple_compare(self):
        # This test was suggested by Tim Peters. It verifies that the tuple
        # comparison respects the current tuple compare semantics, which do not
        # guarantee that x < x <=> (x,) < (x,)
        #
        # Note that we don't have to put anything kwenye tuples here, because
        # the check function does a tuple test automatically.

        check_against_PyObject_RichCompareBool(self, [float('nan')]*100)
        check_against_PyObject_RichCompareBool(self, [float('nan') for
                                                      _ kwenye range(100)])

    eleza test_not_all_tuples(self):
        self.assertRaises(TypeError, [(1.0, 1.0), (Uongo, "A"), 6].sort)
        self.assertRaises(TypeError, [('a', 1), (1, 'a')].sort)
        self.assertRaises(TypeError, [(1, 'a'), ('a', 1)].sort)
#==============================================================================

ikiwa __name__ == "__main__":
    unittest.main()
