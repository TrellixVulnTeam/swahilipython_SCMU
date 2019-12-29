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
        self.assertRaises(TypeError, lambda: 1 kwenye a)
        self.assertRaises(TypeError, lambda: 1 haiko kwenye a)

        # test char kwenye string
        self.assertIn('c', 'abc')
        self.assertNotIn('d', 'abc')

        self.assertIn('', '')
        self.assertIn('', 'abc')

        self.assertRaises(TypeError, lambda: Tupu kwenye 'abc')

    eleza test_builtin_sequence_types(self):
        # a collection of tests on builtin sequence types
        a = range(10)
        kila i kwenye a:
            self.assertIn(i, a)
        self.assertNotIn(16, a)
        self.assertNotIn(a, a)

        a = tuple(a)
        kila i kwenye a:
            self.assertIn(i, a)
        self.assertNotIn(16, a)
        self.assertNotIn(a, a)

        kundi Deviant1:
            """Behaves strangely when compared

            This kundi ni designed to make sure that the contains code
            works when the list ni modified during the check.
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
        # containment na equality tests involving elements that are
        # sio necessarily equal to themselves

        kundi MyNonReflexive(object):
            eleza __eq__(self, other):
                rudisha Uongo
            eleza __hash__(self):
                rudisha 28

        values = float('nan'), 1, Tupu, 'abc', MyNonReflexive()
        constructors = list, tuple, dict.kutokakeys, set, frozenset, deque
        kila constructor kwenye constructors:
            container = constructor(values)
            kila elem kwenye container:
                self.assertIn(elem, container)
            self.assertKweli(container == constructor(values))
            self.assertKweli(container == container)

    eleza test_block_fallback(self):
        # blocking fallback with __contains__ = Tupu
        kundi ByContains(object):
            eleza __contains__(self, other):
                rudisha Uongo
        c = ByContains()
        kundi BlockContains(ByContains):
            """Is sio a container

            This kundi ni a perfectly good iterable (as tested by
            list(bc)), kama well kama inheriting kutoka a perfectly good
            container, but __contains__ = Tupu prevents the usual
            fallback to iteration kwenye the container protocol. That
            is, normally, 0 kwenye bc would fall back to the equivalent
            of any(x==0 kila x kwenye bc), but here it's blocked kutoka
            doing so.
            """
            eleza __iter__(self):
                wakati Uongo:
                    tuma Tupu
            __contains__ = Tupu
        bc = BlockContains()
        self.assertUongo(0 kwenye c)
        self.assertUongo(0 kwenye list(bc))
        self.assertRaises(TypeError, lambda: 0 kwenye bc)

ikiwa __name__ == '__main__':
    unittest.main()
