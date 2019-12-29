agiza sys
kutoka test agiza list_tests
kutoka test.support agiza cpython_only
agiza pickle
agiza unittest

kundi ListTest(list_tests.CommonTest):
    type2test = list

    eleza test_basic(self):
        self.assertEqual(list([]), [])
        l0_3 = [0, 1, 2, 3]
        l0_3_bis = list(l0_3)
        self.assertEqual(l0_3, l0_3_bis)
        self.assertKweli(l0_3 ni sio l0_3_bis)
        self.assertEqual(list(()), [])
        self.assertEqual(list((0, 1, 2, 3)), [0, 1, 2, 3])
        self.assertEqual(list(''), [])
        self.assertEqual(list('spam'), ['s', 'p', 'a', 'm'])
        self.assertEqual(list(x kila x kwenye range(10) ikiwa x % 2),
                         [1, 3, 5, 7, 9])

        ikiwa sys.maxsize == 0x7fffffff:
            # This test can currently only work on 32-bit machines.
            # XXX If/when PySequence_Length() rudishas a ssize_t, it should be
            # XXX re-enabled.
            # Verify clearing of bug #556025.
            # This assumes that the max data size (sys.maxint) == max
            # address size this also assumes that the address size ni at
            # least 4 bytes with 8 byte addresses, the bug ni sio well
            # tested
            #
            # Note: This test ni expected to SEGV under Cygwin 1.3.12 or
            # earlier due to a newlib bug.  See the following mailing list
            # thread kila the details:

            #     http://sources.redhat.com/ml/newlib/2002/msg00369.html
            self.assertRaises(MemoryError, list, range(sys.maxsize // 2))

        # This code used to segfault kwenye Py2.4a3
        x = []
        x.extend(-y kila y kwenye x)
        self.assertEqual(x, [])

    eleza test_keyword_args(self):
        with self.assertRaisesRegex(TypeError, 'keyword argument'):
            list(sequence=[])

    eleza test_truth(self):
        super().test_truth()
        self.assertKweli(not [])
        self.assertKweli([42])

    eleza test_identity(self):
        self.assertKweli([] ni sio [])

    eleza test_len(self):
        super().test_len()
        self.assertEqual(len([]), 0)
        self.assertEqual(len([0]), 1)
        self.assertEqual(len([0, 1, 2]), 3)

    eleza test_overflow(self):
        lst = [4, 5, 6, 7]
        n = int((sys.maxsize*2+2) // len(lst))
        eleza mul(a, b): rudisha a * b
        eleza imul(a, b): a *= b
        self.assertRaises((MemoryError, OverflowError), mul, lst, n)
        self.assertRaises((MemoryError, OverflowError), imul, lst, n)

    eleza test_repr_large(self):
        # Check the repr of large list objects
        eleza check(n):
            l = [0] * n
            s = repr(l)
            self.assertEqual(s,
                '[' + ', '.join(['0'] * n) + ']')
        check(10)       # check our checking code
        check(1000000)

    eleza test_iterator_pickle(self):
        orig = self.type2test([4, 5, 6, 7])
        data = [10, 11, 12, 13, 14, 15]
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            # initial iterator
            itorig = iter(orig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data)

            # running iterator
            next(itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data[1:])

            # empty iterator
            kila i kwenye range(1, len(orig)):
                next(itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data[len(orig):])

            # exhausted iterator
            self.assertRaises(StopIteration, next, itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a[:] = data
            self.assertEqual(list(it), [])

    eleza test_reversed_pickle(self):
        orig = self.type2test([4, 5, 6, 7])
        data = [10, 11, 12, 13, 14, 15]
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            # initial iterator
            itorig = reversed(orig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data[len(orig)-1::-1])

            # running iterator
            next(itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), data[len(orig)-2::-1])

            # empty iterator
            kila i kwenye range(1, len(orig)):
                next(itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a[:] = data
            self.assertEqual(type(it), type(itorig))
            self.assertEqual(list(it), [])

            # exhausted iterator
            self.assertRaises(StopIteration, next, itorig)
            d = pickle.dumps((itorig, orig), proto)
            it, a = pickle.loads(d)
            a[:] = data
            self.assertEqual(list(it), [])

    eleza test_no_comdat_folding(self):
        # Issue 8847: In the PGO build, the MSVC linker's COMDAT folding
        # optimization causes failures kwenye code that relies on distinct
        # function addresses.
        kundi L(list): pita
        with self.assertRaises(TypeError):
            (3,) + L([1,2])

    @cpython_only
    eleza test_preallocation(self):
        iterable = [0] * 10
        iter_size = sys.getsizeof(iterable)

        self.assertEqual(iter_size, sys.getsizeof(list([0] * 10)))
        self.assertEqual(iter_size, sys.getsizeof(list(range(10))))

ikiwa __name__ == "__main__":
    unittest.main()
