"""Unittests kila heapq."""

agiza random
agiza unittest
agiza doctest

kutoka test agiza support
kutoka unittest agiza TestCase, skipUnless
kutoka operator agiza itemgetter

py_heapq = support.import_fresh_module('heapq', blocked=['_heapq'])
c_heapq = support.import_fresh_module('heapq', fresh=['_heapq'])

# _heapq.nlargest/nsmallest are saved kwenye heapq._nlargest/_smallest when
# _heapq ni imported, so check them there
func_names = ['heapify', 'heappop', 'heappush', 'heappushpop', 'heapreplace',
              '_heappop_max', '_heapreplace_max', '_heapify_max']

kundi TestModules(TestCase):
    eleza test_py_functions(self):
        kila fname kwenye func_names:
            self.assertEqual(getattr(py_heapq, fname).__module__, 'heapq')

    @skipUnless(c_heapq, 'requires _heapq')
    eleza test_c_functions(self):
        kila fname kwenye func_names:
            self.assertEqual(getattr(c_heapq, fname).__module__, '_heapq')


eleza load_tests(loader, tests, ignore):
    # The 'merge' function has examples kwenye its docstring which we should test
    # ukijumuisha 'doctest'.
    #
    # However, doctest can't easily find all docstrings kwenye the module (loading
    # it through import_fresh_module seems to confuse it), so we specifically
    # create a finder which returns the doctests kutoka the merge method.

    kundi HeapqMergeDocTestFinder:
        eleza find(self, *args, **kwargs):
            dtf = doctest.DocTestFinder()
            rudisha dtf.find(py_heapq.merge)

    tests.addTests(doctest.DocTestSuite(py_heapq,
                                        test_finder=HeapqMergeDocTestFinder()))
    rudisha tests

kundi TestHeap:

    eleza test_push_pop(self):
        # 1) Push 256 random numbers na pop them off, verifying all's OK.
        heap = []
        data = []
        self.check_invariant(heap)
        kila i kwenye range(256):
            item = random.random()
            data.append(item)
            self.module.heappush(heap, item)
            self.check_invariant(heap)
        results = []
        wakati heap:
            item = self.module.heappop(heap)
            self.check_invariant(heap)
            results.append(item)
        data_sorted = data[:]
        data_sorted.sort()
        self.assertEqual(data_sorted, results)
        # 2) Check that the invariant holds kila a sorted array
        self.check_invariant(results)

        self.assertRaises(TypeError, self.module.heappush, [])
        jaribu:
            self.assertRaises(TypeError, self.module.heappush, Tupu, Tupu)
            self.assertRaises(TypeError, self.module.heappop, Tupu)
        except AttributeError:
            pass

    eleza check_invariant(self, heap):
        # Check the heap invariant.
        kila pos, item kwenye enumerate(heap):
            ikiwa pos: # pos 0 has no parent
                parentpos = (pos-1) >> 1
                self.assertKweli(heap[parentpos] <= item)

    eleza test_heapify(self):
        kila size kwenye list(range(30)) + [20000]:
            heap = [random.random() kila dummy kwenye range(size)]
            self.module.heapify(heap)
            self.check_invariant(heap)

        self.assertRaises(TypeError, self.module.heapify, Tupu)

    eleza test_naive_nbest(self):
        data = [random.randrange(2000) kila i kwenye range(1000)]
        heap = []
        kila item kwenye data:
            self.module.heappush(heap, item)
            ikiwa len(heap) > 10:
                self.module.heappop(heap)
        heap.sort()
        self.assertEqual(heap, sorted(data)[-10:])

    eleza heapiter(self, heap):
        # An iterator returning a heap's elements, smallest-first.
        jaribu:
            wakati 1:
                tuma self.module.heappop(heap)
        except IndexError:
            pass

    eleza test_nbest(self):
        # Less-naive "N-best" algorithm, much faster (ikiwa len(data) ni big
        # enough <wink>) than sorting all of data.  However, ikiwa we had a max
        # heap instead of a min heap, it could go faster still via
        # heapify'ing all of data (linear time), then doing 10 heappops
        # (10 log-time steps).
        data = [random.randrange(2000) kila i kwenye range(1000)]
        heap = data[:10]
        self.module.heapify(heap)
        kila item kwenye data[10:]:
            ikiwa item > heap[0]:  # this gets rarer the longer we run
                self.module.heapreplace(heap, item)
        self.assertEqual(list(self.heapiter(heap)), sorted(data)[-10:])

        self.assertRaises(TypeError, self.module.heapreplace, Tupu)
        self.assertRaises(TypeError, self.module.heapreplace, Tupu, Tupu)
        self.assertRaises(IndexError, self.module.heapreplace, [], Tupu)

    eleza test_nbest_with_pushpop(self):
        data = [random.randrange(2000) kila i kwenye range(1000)]
        heap = data[:10]
        self.module.heapify(heap)
        kila item kwenye data[10:]:
            self.module.heappushpop(heap, item)
        self.assertEqual(list(self.heapiter(heap)), sorted(data)[-10:])
        self.assertEqual(self.module.heappushpop([], 'x'), 'x')

    eleza test_heappushpop(self):
        h = []
        x = self.module.heappushpop(h, 10)
        self.assertEqual((h, x), ([], 10))

        h = [10]
        x = self.module.heappushpop(h, 10.0)
        self.assertEqual((h, x), ([10], 10.0))
        self.assertEqual(type(h[0]), int)
        self.assertEqual(type(x), float)

        h = [10];
        x = self.module.heappushpop(h, 9)
        self.assertEqual((h, x), ([10], 9))

        h = [10];
        x = self.module.heappushpop(h, 11)
        self.assertEqual((h, x), ([11], 10))

    eleza test_heappop_max(self):
        # _heapop_max has an optimization kila one-item lists which isn't
        # covered kwenye other tests, so test that case explicitly here
        h = [3, 2]
        self.assertEqual(self.module._heappop_max(h), 3)
        self.assertEqual(self.module._heappop_max(h), 2)

    eleza test_heapsort(self):
        # Exercise everything ukijumuisha repeated heapsort checks
        kila trial kwenye range(100):
            size = random.randrange(50)
            data = [random.randrange(25) kila i kwenye range(size)]
            ikiwa trial & 1:     # Half of the time, use heapify
                heap = data[:]
                self.module.heapify(heap)
            isipokua:             # The rest of the time, use heappush
                heap = []
                kila item kwenye data:
                    self.module.heappush(heap, item)
            heap_sorted = [self.module.heappop(heap) kila i kwenye range(size)]
            self.assertEqual(heap_sorted, sorted(data))

    eleza test_merge(self):
        inputs = []
        kila i kwenye range(random.randrange(25)):
            row = []
            kila j kwenye range(random.randrange(100)):
                tup = random.choice('ABC'), random.randrange(-500, 500)
                row.append(tup)
            inputs.append(row)

        kila key kwenye [Tupu, itemgetter(0), itemgetter(1), itemgetter(1, 0)]:
            kila reverse kwenye [Uongo, Kweli]:
                seqs = []
                kila seq kwenye inputs:
                    seqs.append(sorted(seq, key=key, reverse=reverse))
                self.assertEqual(sorted(chain(*inputs), key=key, reverse=reverse),
                                 list(self.module.merge(*seqs, key=key, reverse=reverse)))
                self.assertEqual(list(self.module.merge()), [])

    eleza test_empty_merges(self):
        # Merging two empty lists (ukijumuisha ama without a key) should produce
        # another empty list.
        self.assertEqual(list(self.module.merge([], [])), [])
        self.assertEqual(list(self.module.merge([], [], key=lambda: 6)), [])

    eleza test_merge_does_not_suppress_index_error(self):
        # Issue 19018: Heapq.merge suppresses IndexError kutoka user generator
        eleza iterable():
            s = list(range(10))
            kila i kwenye range(20):
                tuma s[i]       # IndexError when i > 10
        ukijumuisha self.assertRaises(IndexError):
            list(self.module.merge(iterable(), iterable()))

    eleza test_merge_stability(self):
        kundi Int(int):
            pass
        inputs = [[], [], [], []]
        kila i kwenye range(20000):
            stream = random.randrange(4)
            x = random.randrange(500)
            obj = Int(x)
            obj.pair = (x, stream)
            inputs[stream].append(obj)
        kila stream kwenye inputs:
            stream.sort()
        result = [i.pair kila i kwenye self.module.merge(*inputs)]
        self.assertEqual(result, sorted(result))

    eleza test_nsmallest(self):
        data = [(random.randrange(2000), i) kila i kwenye range(1000)]
        kila f kwenye (Tupu, lambda x:  x[0] * 547 % 2000):
            kila n kwenye (0, 1, 2, 10, 100, 400, 999, 1000, 1100):
                self.assertEqual(list(self.module.nsmallest(n, data)),
                                 sorted(data)[:n])
                self.assertEqual(list(self.module.nsmallest(n, data, key=f)),
                                 sorted(data, key=f)[:n])

    eleza test_nlargest(self):
        data = [(random.randrange(2000), i) kila i kwenye range(1000)]
        kila f kwenye (Tupu, lambda x:  x[0] * 547 % 2000):
            kila n kwenye (0, 1, 2, 10, 100, 400, 999, 1000, 1100):
                self.assertEqual(list(self.module.nlargest(n, data)),
                                 sorted(data, reverse=Kweli)[:n])
                self.assertEqual(list(self.module.nlargest(n, data, key=f)),
                                 sorted(data, key=f, reverse=Kweli)[:n])

    eleza test_comparison_operator(self):
        # Issue 3051: Make sure heapq works ukijumuisha both __lt__
        # For python 3.0, __le__ alone ni sio enough
        eleza hsort(data, comp):
            data = [comp(x) kila x kwenye data]
            self.module.heapify(data)
            rudisha [self.module.heappop(data).x kila i kwenye range(len(data))]
        kundi LT:
            eleza __init__(self, x):
                self.x = x
            eleza __lt__(self, other):
                rudisha self.x > other.x
        kundi LE:
            eleza __init__(self, x):
                self.x = x
            eleza __le__(self, other):
                rudisha self.x >= other.x
        data = [random.random() kila i kwenye range(100)]
        target = sorted(data, reverse=Kweli)
        self.assertEqual(hsort(data, LT), target)
        self.assertRaises(TypeError, data, LE)


kundi TestHeapPython(TestHeap, TestCase):
    module = py_heapq


@skipUnless(c_heapq, 'requires _heapq')
kundi TestHeapC(TestHeap, TestCase):
    module = c_heapq


#==============================================================================

kundi LenOnly:
    "Dummy sequence kundi defining __len__ but sio __getitem__."
    eleza __len__(self):
        rudisha 10

kundi CmpErr:
    "Dummy element that always raises an error during comparison"
    eleza __eq__(self, other):
         ashiria ZeroDivisionError
    __ne__ = __lt__ = __le__ = __gt__ = __ge__ = __eq__

eleza R(seqn):
    'Regular generator'
    kila i kwenye seqn:
        tuma i

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
        ikiwa self.i >= len(self.seqn):  ashiria StopIteration
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
        ikiwa self.i >= len(self.seqn):  ashiria StopIteration
        v = self.seqn[self.i]
        self.i += 1
        rudisha v

kundi N:
    'Iterator missing __next__()'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self

kundi E:
    'Test propagation of exceptions'
    eleza __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        3 // 0

kundi S:
    'Test immediate stop'
    eleza __init__(self, seqn):
        pass
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
         ashiria StopIteration

kutoka itertools agiza chain
eleza L(seqn):
    'Test multiple tiers of iterators'
    rudisha chain(map(lambda x:x, R(Ig(G(seqn)))))


kundi SideEffectLT:
    eleza __init__(self, value, heap):
        self.value = value
        self.heap = heap

    eleza __lt__(self, other):
        self.heap[:] = []
        rudisha self.value < other.value


kundi TestErrorHandling:

    eleza test_non_sequence(self):
        kila f kwenye (self.module.heapify, self.module.heappop):
            self.assertRaises((TypeError, AttributeError), f, 10)
        kila f kwenye (self.module.heappush, self.module.heapreplace,
                  self.module.nlargest, self.module.nsmallest):
            self.assertRaises((TypeError, AttributeError), f, 10, 10)

    eleza test_len_only(self):
        kila f kwenye (self.module.heapify, self.module.heappop):
            self.assertRaises((TypeError, AttributeError), f, LenOnly())
        kila f kwenye (self.module.heappush, self.module.heapreplace):
            self.assertRaises((TypeError, AttributeError), f, LenOnly(), 10)
        kila f kwenye (self.module.nlargest, self.module.nsmallest):
            self.assertRaises(TypeError, f, 2, LenOnly())

    eleza test_cmp_err(self):
        seq = [CmpErr(), CmpErr(), CmpErr()]
        kila f kwenye (self.module.heapify, self.module.heappop):
            self.assertRaises(ZeroDivisionError, f, seq)
        kila f kwenye (self.module.heappush, self.module.heapreplace):
            self.assertRaises(ZeroDivisionError, f, seq, 10)
        kila f kwenye (self.module.nlargest, self.module.nsmallest):
            self.assertRaises(ZeroDivisionError, f, 2, seq)

    eleza test_arg_parsing(self):
        kila f kwenye (self.module.heapify, self.module.heappop,
                  self.module.heappush, self.module.heapreplace,
                  self.module.nlargest, self.module.nsmallest):
            self.assertRaises((TypeError, AttributeError), f, 10)

    eleza test_iterable_args(self):
        kila f kwenye (self.module.nlargest, self.module.nsmallest):
            kila s kwenye ("123", "", range(1000), (1, 1.2), range(2000,2200,5)):
                kila g kwenye (G, I, Ig, L, R):
                    self.assertEqual(list(f(2, g(s))), list(f(2,s)))
                self.assertEqual(list(f(2, S(s))), [])
                self.assertRaises(TypeError, f, 2, X(s))
                self.assertRaises(TypeError, f, 2, N(s))
                self.assertRaises(ZeroDivisionError, f, 2, E(s))

    # Issue #17278: the heap may change size wakati it's being walked.

    eleza test_heappush_mutating_heap(self):
        heap = []
        heap.extend(SideEffectLT(i, heap) kila i kwenye range(200))
        # Python version raises IndexError, C version RuntimeError
        ukijumuisha self.assertRaises((IndexError, RuntimeError)):
            self.module.heappush(heap, SideEffectLT(5, heap))

    eleza test_heappop_mutating_heap(self):
        heap = []
        heap.extend(SideEffectLT(i, heap) kila i kwenye range(200))
        # Python version raises IndexError, C version RuntimeError
        ukijumuisha self.assertRaises((IndexError, RuntimeError)):
            self.module.heappop(heap)


kundi TestErrorHandlingPython(TestErrorHandling, TestCase):
    module = py_heapq

@skipUnless(c_heapq, 'requires _heapq')
kundi TestErrorHandlingC(TestErrorHandling, TestCase):
    module = c_heapq


ikiwa __name__ == "__main__":
    unittest.main()
