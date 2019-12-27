kutoka collections agiza deque
agiza unittest


kundi base_set:
    eleza __init__(self, el):
        self.el = el

kundi myset(base_set):
    eleza __contains__(self, el):
        rudisha self.el == el

kundi seq(base_set):
    eleza __getitem__(self, n):
        rudisha [self.el][n]

kundi TestContains(unittest.TestCase):
    eleza test_common_tests(self):
        a = base_set(1)
        b = myset(1)
        c = seq(1)
        self.assertIn(1, b)
        self.assertNotIn(0, b)
        self.assertIn(1, c)
        self.assertNotIn(0, c)
        self.assertRaises(TypeError, lambda: 1 in a)
        self.assertRaises(TypeError, lambda: 1 not in a)

        # test char in string
        self.assertIn('c', 'abc')
        self.assertNotIn('d', 'abc')

        self.assertIn('', '')
        self.assertIn('', 'abc')

        self.assertRaises(TypeError, lambda: None in 'abc')

    eleza test_builtin_sequence_types(self):
        # a collection of tests on builtin sequence types
        a = range(10)
        for i in a:
            self.assertIn(i, a)
        self.assertNotIn(16, a)
        self.assertNotIn(a, a)

        a = tuple(a)
        for i in a:
            self.assertIn(i, a)
        self.assertNotIn(16, a)
        self.assertNotIn(a, a)

        kundi Deviant1:
            """Behaves strangely when compared

            This kundi is designed to make sure that the contains code
            works when the list is modified during the check.
            """
            aList = list(range(15))
            eleza __eq__(self, other):
                ikiwa other == 12:
                    self.aList.remove(12)
                    self.aList.remove(13)
                    self.aList.remove(14)
                rudisha 0

        self.assertNotIn(Deviant1(), Deviant1.aList)

    eleza test_nonreflexive(self):
        # containment and equality tests involving elements that are
        # not necessarily equal to themselves

        kundi MyNonReflexive(object):
            eleza __eq__(self, other):
                rudisha False
            eleza __hash__(self):
                rudisha 28

        values = float('nan'), 1, None, 'abc', MyNonReflexive()
        constructors = list, tuple, dict.kutokakeys, set, frozenset, deque
        for constructor in constructors:
            container = constructor(values)
            for elem in container:
                self.assertIn(elem, container)
            self.assertTrue(container == constructor(values))
            self.assertTrue(container == container)

    eleza test_block_fallback(self):
        # blocking fallback with __contains__ = None
        kundi ByContains(object):
            eleza __contains__(self, other):
                rudisha False
        c = ByContains()
        kundi BlockContains(ByContains):
            """Is not a container

            This kundi is a perfectly good iterable (as tested by
            list(bc)), as well as inheriting kutoka a perfectly good
            container, but __contains__ = None prevents the usual
            fallback to iteration in the container protocol. That
            is, normally, 0 in bc would fall back to the equivalent
            of any(x==0 for x in bc), but here it's blocked kutoka
            doing so.
            """
            eleza __iter__(self):
                while False:
                    yield None
            __contains__ = None
        bc = BlockContains()
        self.assertFalse(0 in c)
        self.assertFalse(0 in list(bc))
        self.assertRaises(TypeError, lambda: 0 in bc)

ikiwa __name__ == '__main__':
    unittest.main()
