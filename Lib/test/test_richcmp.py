# Tests for rich comparisons

agiza unittest
kutoka test agiza support

agiza operator

kundi Number:

    eleza __init__(self, x):
        self.x = x

    eleza __lt__(self, other):
        rudisha self.x < other

    eleza __le__(self, other):
        rudisha self.x <= other

    eleza __eq__(self, other):
        rudisha self.x == other

    eleza __ne__(self, other):
        rudisha self.x != other

    eleza __gt__(self, other):
        rudisha self.x > other

    eleza __ge__(self, other):
        rudisha self.x >= other

    eleza __cmp__(self, other):
        raise support.TestFailed("Number.__cmp__() should not be called")

    eleza __repr__(self):
        rudisha "Number(%r)" % (self.x, )

kundi Vector:

    eleza __init__(self, data):
        self.data = data

    eleza __len__(self):
        rudisha len(self.data)

    eleza __getitem__(self, i):
        rudisha self.data[i]

    eleza __setitem__(self, i, v):
        self.data[i] = v

    __hash__ = None # Vectors cannot be hashed

    eleza __bool__(self):
        raise TypeError("Vectors cannot be used in Boolean contexts")

    eleza __cmp__(self, other):
        raise support.TestFailed("Vector.__cmp__() should not be called")

    eleza __repr__(self):
        rudisha "Vector(%r)" % (self.data, )

    eleza __lt__(self, other):
        rudisha Vector([a < b for a, b in zip(self.data, self.__cast(other))])

    eleza __le__(self, other):
        rudisha Vector([a <= b for a, b in zip(self.data, self.__cast(other))])

    eleza __eq__(self, other):
        rudisha Vector([a == b for a, b in zip(self.data, self.__cast(other))])

    eleza __ne__(self, other):
        rudisha Vector([a != b for a, b in zip(self.data, self.__cast(other))])

    eleza __gt__(self, other):
        rudisha Vector([a > b for a, b in zip(self.data, self.__cast(other))])

    eleza __ge__(self, other):
        rudisha Vector([a >= b for a, b in zip(self.data, self.__cast(other))])

    eleza __cast(self, other):
        ikiwa isinstance(other, Vector):
            other = other.data
        ikiwa len(self.data) != len(other):
            raise ValueError("Cannot compare vectors of different length")
        rudisha other

opmap = {
    "lt": (lambda a,b: a< b, operator.lt, operator.__lt__),
    "le": (lambda a,b: a<=b, operator.le, operator.__le__),
    "eq": (lambda a,b: a==b, operator.eq, operator.__eq__),
    "ne": (lambda a,b: a!=b, operator.ne, operator.__ne__),
    "gt": (lambda a,b: a> b, operator.gt, operator.__gt__),
    "ge": (lambda a,b: a>=b, operator.ge, operator.__ge__)
}

kundi VectorTest(unittest.TestCase):

    eleza checkfail(self, error, opname, *args):
        for op in opmap[opname]:
            self.assertRaises(error, op, *args)

    eleza checkequal(self, opname, a, b, expres):
        for op in opmap[opname]:
            realres = op(a, b)
            # can't use assertEqual(realres, expres) here
            self.assertEqual(len(realres), len(expres))
            for i in range(len(realres)):
                # results are bool, so we can use "is" here
                self.assertTrue(realres[i] is expres[i])

    eleza test_mixed(self):
        # check that comparisons involving Vector objects
        # which rudisha rich results (i.e. Vectors with itemwise
        # comparison results) work
        a = Vector(range(2))
        b = Vector(range(3))
        # all comparisons should fail for different length
        for opname in opmap:
            self.checkfail(ValueError, opname, a, b)

        a = list(range(5))
        b = 5 * [2]
        # try mixed arguments (but not (a, b) as that won't rudisha a bool vector)
        args = [(a, Vector(b)), (Vector(a), b), (Vector(a), Vector(b))]
        for (a, b) in args:
            self.checkequal("lt", a, b, [True,  True,  False, False, False])
            self.checkequal("le", a, b, [True,  True,  True,  False, False])
            self.checkequal("eq", a, b, [False, False, True,  False, False])
            self.checkequal("ne", a, b, [True,  True,  False, True,  True ])
            self.checkequal("gt", a, b, [False, False, False, True,  True ])
            self.checkequal("ge", a, b, [False, False, True,  True,  True ])

            for ops in opmap.values():
                for op in ops:
                    # calls __bool__, which should fail
                    self.assertRaises(TypeError, bool, op(a, b))

kundi NumberTest(unittest.TestCase):

    eleza test_basic(self):
        # Check that comparisons involving Number objects
        # give the same results give as comparing the
        # corresponding ints
        for a in range(3):
            for b in range(3):
                for typea in (int, Number):
                    for typeb in (int, Number):
                        ikiwa typea==typeb==int:
                            continue # the combination int, int is useless
                        ta = typea(a)
                        tb = typeb(b)
                        for ops in opmap.values():
                            for op in ops:
                                realoutcome = op(a, b)
                                testoutcome = op(ta, tb)
                                self.assertEqual(realoutcome, testoutcome)

    eleza checkvalue(self, opname, a, b, expres):
        for typea in (int, Number):
            for typeb in (int, Number):
                ta = typea(a)
                tb = typeb(b)
                for op in opmap[opname]:
                    realres = op(ta, tb)
                    realres = getattr(realres, "x", realres)
                    self.assertTrue(realres is expres)

    eleza test_values(self):
        # check all operators and all comparison results
        self.checkvalue("lt", 0, 0, False)
        self.checkvalue("le", 0, 0, True )
        self.checkvalue("eq", 0, 0, True )
        self.checkvalue("ne", 0, 0, False)
        self.checkvalue("gt", 0, 0, False)
        self.checkvalue("ge", 0, 0, True )

        self.checkvalue("lt", 0, 1, True )
        self.checkvalue("le", 0, 1, True )
        self.checkvalue("eq", 0, 1, False)
        self.checkvalue("ne", 0, 1, True )
        self.checkvalue("gt", 0, 1, False)
        self.checkvalue("ge", 0, 1, False)

        self.checkvalue("lt", 1, 0, False)
        self.checkvalue("le", 1, 0, False)
        self.checkvalue("eq", 1, 0, False)
        self.checkvalue("ne", 1, 0, True )
        self.checkvalue("gt", 1, 0, True )
        self.checkvalue("ge", 1, 0, True )

kundi MiscTest(unittest.TestCase):

    eleza test_misbehavin(self):
        kundi Misb:
            eleza __lt__(self_, other): rudisha 0
            eleza __gt__(self_, other): rudisha 0
            eleza __eq__(self_, other): rudisha 0
            eleza __le__(self_, other): self.fail("This shouldn't happen")
            eleza __ge__(self_, other): self.fail("This shouldn't happen")
            eleza __ne__(self_, other): self.fail("This shouldn't happen")
        a = Misb()
        b = Misb()
        self.assertEqual(a<b, 0)
        self.assertEqual(a==b, 0)
        self.assertEqual(a>b, 0)

    eleza test_not(self):
        # Check that exceptions in __bool__ are properly
        # propagated by the not operator
        agiza operator
        kundi Exc(Exception):
            pass
        kundi Bad:
            eleza __bool__(self):
                raise Exc

        eleza do(bad):
            not bad

        for func in (do, operator.not_):
            self.assertRaises(Exc, func, Bad())

    @support.no_tracing
    eleza test_recursion(self):
        # Check that comparison for recursive objects fails gracefully
        kutoka collections agiza UserList
        a = UserList()
        b = UserList()
        a.append(b)
        b.append(a)
        self.assertRaises(RecursionError, operator.eq, a, b)
        self.assertRaises(RecursionError, operator.ne, a, b)
        self.assertRaises(RecursionError, operator.lt, a, b)
        self.assertRaises(RecursionError, operator.le, a, b)
        self.assertRaises(RecursionError, operator.gt, a, b)
        self.assertRaises(RecursionError, operator.ge, a, b)

        b.append(17)
        # Even recursive lists of different lengths are different,
        # but they cannot be ordered
        self.assertTrue(not (a == b))
        self.assertTrue(a != b)
        self.assertRaises(RecursionError, operator.lt, a, b)
        self.assertRaises(RecursionError, operator.le, a, b)
        self.assertRaises(RecursionError, operator.gt, a, b)
        self.assertRaises(RecursionError, operator.ge, a, b)
        a.append(17)
        self.assertRaises(RecursionError, operator.eq, a, b)
        self.assertRaises(RecursionError, operator.ne, a, b)
        a.insert(0, 11)
        b.insert(0, 12)
        self.assertTrue(not (a == b))
        self.assertTrue(a != b)
        self.assertTrue(a < b)

    eleza test_exception_message(self):
        kundi Spam:
            pass

        tests = [
            (lambda: 42 < None, r"'<' .* of 'int' and 'NoneType'"),
            (lambda: None < 42, r"'<' .* of 'NoneType' and 'int'"),
            (lambda: 42 > None, r"'>' .* of 'int' and 'NoneType'"),
            (lambda: "foo" < None, r"'<' .* of 'str' and 'NoneType'"),
            (lambda: "foo" >= 666, r"'>=' .* of 'str' and 'int'"),
            (lambda: 42 <= None, r"'<=' .* of 'int' and 'NoneType'"),
            (lambda: 42 >= None, r"'>=' .* of 'int' and 'NoneType'"),
            (lambda: 42 < [], r"'<' .* of 'int' and 'list'"),
            (lambda: () > [], r"'>' .* of 'tuple' and 'list'"),
            (lambda: None >= None, r"'>=' .* of 'NoneType' and 'NoneType'"),
            (lambda: Spam() < 42, r"'<' .* of 'Spam' and 'int'"),
            (lambda: 42 < Spam(), r"'<' .* of 'int' and 'Spam'"),
            (lambda: Spam() <= Spam(), r"'<=' .* of 'Spam' and 'Spam'"),
        ]
        for i, test in enumerate(tests):
            with self.subTest(test=i):
                with self.assertRaisesRegex(TypeError, test[1]):
                    test[0]()


kundi DictTest(unittest.TestCase):

    eleza test_dicts(self):
        # Verify that __eq__ and __ne__ work for dicts even ikiwa the keys and
        # values don't support anything other than __eq__ and __ne__ (and
        # __hash__).  Complex numbers are a fine example of that.
        agiza random
        imag1a = {}
        for i in range(50):
            imag1a[random.randrange(100)*1j] = random.randrange(100)*1j
        items = list(imag1a.items())
        random.shuffle(items)
        imag1b = {}
        for k, v in items:
            imag1b[k] = v
        imag2 = imag1b.copy()
        imag2[k] = v + 1.0
        self.assertEqual(imag1a, imag1a)
        self.assertEqual(imag1a, imag1b)
        self.assertEqual(imag2, imag2)
        self.assertTrue(imag1a != imag2)
        for opname in ("lt", "le", "gt", "ge"):
            for op in opmap[opname]:
                self.assertRaises(TypeError, op, imag1a, imag2)

kundi ListTest(unittest.TestCase):

    eleza test_coverage(self):
        # exercise all comparisons for lists
        x = [42]
        self.assertIs(x<x, False)
        self.assertIs(x<=x, True)
        self.assertIs(x==x, True)
        self.assertIs(x!=x, False)
        self.assertIs(x>x, False)
        self.assertIs(x>=x, True)
        y = [42, 42]
        self.assertIs(x<y, True)
        self.assertIs(x<=y, True)
        self.assertIs(x==y, False)
        self.assertIs(x!=y, True)
        self.assertIs(x>y, False)
        self.assertIs(x>=y, False)

    eleza test_badentry(self):
        # make sure that exceptions for item comparison are properly
        # propagated in list comparisons
        kundi Exc(Exception):
            pass
        kundi Bad:
            eleza __eq__(self, other):
                raise Exc

        x = [Bad()]
        y = [Bad()]

        for op in opmap["eq"]:
            self.assertRaises(Exc, op, x, y)

    eleza test_goodentry(self):
        # This test exercises the final call to PyObject_RichCompare()
        # in Objects/listobject.c::list_richcompare()
        kundi Good:
            eleza __lt__(self, other):
                rudisha True

        x = [Good()]
        y = [Good()]

        for op in opmap["lt"]:
            self.assertIs(op(x, y), True)


ikiwa __name__ == "__main__":
    unittest.main()
