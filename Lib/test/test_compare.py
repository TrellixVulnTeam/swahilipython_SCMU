agiza unittest

kundi Empty:
    eleza __repr__(self):
        rudisha '<Empty>'

kundi Cmp:
    eleza __init__(self,arg):
        self.arg = arg

    eleza __repr__(self):
        rudisha '<Cmp %s>' % self.arg

    eleza __eq__(self, other):
        rudisha self.arg == other

kundi Anything:
    eleza __eq__(self, other):
        rudisha Kweli

    eleza __ne__(self, other):
        rudisha Uongo

kundi ComparisonTest(unittest.TestCase):
    set1 = [2, 2.0, 2, 2+0j, Cmp(2.0)]
    set2 = [[1], (3,), Tupu, Empty()]
    candidates = set1 + set2

    eleza test_comparisons(self):
        kila a kwenye self.candidates:
            kila b kwenye self.candidates:
                ikiwa ((a kwenye self.set1) na (b kwenye self.set1)) ama a ni b:
                    self.assertEqual(a, b)
                isipokua:
                    self.assertNotEqual(a, b)

    eleza test_id_comparisons(self):
        # Ensure default comparison compares id() of args
        L = []
        kila i kwenye range(10):
            L.insert(len(L)//2, Empty())
        kila a kwenye L:
            kila b kwenye L:
                self.assertEqual(a == b, id(a) == id(b),
                                 'a=%r, b=%r' % (a, b))

    eleza test_ne_defaults_to_not_eq(self):
        a = Cmp(1)
        b = Cmp(1)
        c = Cmp(2)
        self.assertIs(a == b, Kweli)
        self.assertIs(a != b, Uongo)
        self.assertIs(a != c, Kweli)

    eleza test_ne_high_priority(self):
        """object.__ne__() should allow reflected __ne__() to be tried"""
        calls = []
        kundi Left:
            # Inherits object.__ne__()
            eleza __eq__(*args):
                calls.append('Left.__eq__')
                rudisha NotImplemented
        kundi Right:
            eleza __eq__(*args):
                calls.append('Right.__eq__')
                rudisha NotImplemented
            eleza __ne__(*args):
                calls.append('Right.__ne__')
                rudisha NotImplemented
        Left() != Right()
        self.assertSequenceEqual(calls, ['Left.__eq__', 'Right.__ne__'])

    eleza test_ne_low_priority(self):
        """object.__ne__() should sio invoke reflected __eq__()"""
        calls = []
        kundi Base:
            # Inherits object.__ne__()
            eleza __eq__(*args):
                calls.append('Base.__eq__')
                rudisha NotImplemented
        kundi Derived(Base):  # Subclassing forces higher priority
            eleza __eq__(*args):
                calls.append('Derived.__eq__')
                rudisha NotImplemented
            eleza __ne__(*args):
                calls.append('Derived.__ne__')
                rudisha NotImplemented
        Base() != Derived()
        self.assertSequenceEqual(calls, ['Derived.__ne__', 'Base.__eq__'])

    eleza test_other_delegation(self):
        """No default delegation between operations tatizo __ne__()"""
        ops = (
            ('__eq__', lambda a, b: a == b),
            ('__lt__', lambda a, b: a < b),
            ('__le__', lambda a, b: a <= b),
            ('__gt__', lambda a, b: a > b),
            ('__ge__', lambda a, b: a >= b),
        )
        kila name, func kwenye ops:
            with self.subTest(name):
                eleza unexpected(*args):
                    self.fail('Unexpected operator method called')
                kundi C:
                    __ne__ = unexpected
                kila other, _ kwenye ops:
                    ikiwa other != name:
                        setattr(C, other, unexpected)
                ikiwa name == '__eq__':
                    self.assertIs(func(C(), object()), Uongo)
                isipokua:
                    self.assertRaises(TypeError, func, C(), object())

    eleza test_issue_1393(self):
        x = lambda: Tupu
        self.assertEqual(x, Anything())
        self.assertEqual(Anything(), x)
        y = object()
        self.assertEqual(y, Anything())
        self.assertEqual(Anything(), y)


ikiwa __name__ == '__main__':
    unittest.main()
