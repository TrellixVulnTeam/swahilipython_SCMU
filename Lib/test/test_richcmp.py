# Tests kila rich comparisons

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
         ashiria support.TestFailed("Number.__cmp__() should sio be called")

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

    __hash__ = Tupu # Vectors cannot be hashed

    eleza __bool__(self):
         ashiria TypeError("Vectors cannot be used kwenye Boolean contexts")

    eleza __cmp__(self, other):
         ashiria support.TestFailed("Vector.__cmp__() should sio be called")

    eleza __repr__(self):
        rudisha "Vector(%r)" % (self.data, )

    eleza __lt__(self, other):
        rudisha Vector([a < b kila a, b kwenye zip(self.data, self.__cast(other))])

    eleza __le__(self, other):
        rudisha Vector([a <= b kila a, b kwenye zip(self.data, self.__cast(other))])

    eleza __eq__(self, other):
        rudisha Vector([a == b kila a, b kwenye zip(self.data, self.__cast(other))])

    eleza __ne__(self, other):
        rudisha Vector([a != b kila a, b kwenye zip(self.data, self.__cast(other))])

    eleza __gt__(self, other):
        rudisha Vector([a > b kila a, b kwenye zip(self.data, self.__cast(other))])

    eleza __ge__(self, other):
        rudisha Vector([a >= b kila a, b kwenye zip(self.data, self.__cast(other))])

    eleza __cast(self, other):
        ikiwa isinstance(other, Vector):
            other = other.data
        ikiwa len(self.data) != len(other):
             ashiria ValueError("Cannot compare vectors of different length")
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
        kila op kwenye opmap[opname]:
            self.assertRaises(error, op, *args)

    eleza checkequal(self, opname, a, b, expres):
        kila op kwenye opmap[opname]:
            realres = op(a, b)
            # can't use assertEqual(realres, expres) here
            self.assertEqual(len(realres), len(expres))
            kila i kwenye range(len(realres)):
                # results are bool, so we can use "is" here
                self.assertKweli(realres[i] ni expres[i])

    eleza test_mixed(self):
        # check that comparisons involving Vector objects
        # which rudisha rich results (i.e. Vectors ukijumuisha itemwise
        # comparison results) work
        a = Vector(range(2))
        b = Vector(range(3))
        # all comparisons should fail kila different length
        kila opname kwenye opmap:
            self.checkfail(ValueError, opname, a, b)

        a = list(range(5))
        b = 5 * [2]
        # try mixed arguments (but sio (a, b) as that won't rudisha a bool vector)
        args = [(a, Vector(b)), (Vector(a), b), (Vector(a), Vector(b))]
        kila (a, b) kwenye args:
            self.checkequal("lt", a, b, [Kweli,  Kweli,  Uongo, Uongo, Uongo])
            self.checkequal("le", a, b, [Kweli,  Kweli,  Kweli,  Uongo, Uongo])
            self.checkequal("eq", a, b, [Uongo, Uongo, Kweli,  Uongo, Uongo])
            self.checkequal("ne", a, b, [Kweli,  Kweli,  Uongo, Kweli,  Kweli ])
            self.checkequal("gt", a, b, [Uongo, Uongo, Uongo, Kweli,  Kweli ])
            self.checkequal("ge", a, b, [Uongo, Uongo, Kweli,  Kweli,  Kweli ])

            kila ops kwenye opmap.values():
                kila op kwenye ops:
                    # calls __bool__, which should fail
                    self.assertRaises(TypeError, bool, op(a, b))

kundi NumberTest(unittest.TestCase):

    eleza test_basic(self):
        # Check that comparisons involving Number objects
        # give the same results give as comparing the
        # corresponding ints
        kila a kwenye range(3):
            kila b kwenye range(3):
                kila typea kwenye (int, Number):
                    kila typeb kwenye (int, Number):
                        ikiwa typea==typeb==int:
                            endelea # the combination int, int ni useless
                        ta = typea(a)
                        tb = typeb(b)
                        kila ops kwenye opmap.values():
                            kila op kwenye ops:
                                realoutcome = op(a, b)
                                testoutcome = op(ta, tb)
                                self.assertEqual(realoutcome, testoutcome)

    eleza checkvalue(self, opname, a, b, expres):
        kila typea kwenye (int, Number):
            kila typeb kwenye (int, Number):
                ta = typea(a)
                tb = typeb(b)
                kila op kwenye opmap[opname]:
                    realres = op(ta, tb)
                    realres = getattr(realres, "x", realres)
                    self.assertKweli(realres ni expres)

    eleza test_values(self):
        # check all operators na all comparison results
        self.checkvalue("lt", 0, 0, Uongo)
        self.checkvalue("le", 0, 0, Kweli )
        self.checkvalue("eq", 0, 0, Kweli )
        self.checkvalue("ne", 0, 0, Uongo)
        self.checkvalue("gt", 0, 0, Uongo)
        self.checkvalue("ge", 0, 0, Kweli )

        self.checkvalue("lt", 0, 1, Kweli )
        self.checkvalue("le", 0, 1, Kweli )
        self.checkvalue("eq", 0, 1, Uongo)
        self.checkvalue("ne", 0, 1, Kweli )
        self.checkvalue("gt", 0, 1, Uongo)
        self.checkvalue("ge", 0, 1, Uongo)

        self.checkvalue("lt", 1, 0, Uongo)
        self.checkvalue("le", 1, 0, Uongo)
        self.checkvalue("eq", 1, 0, Uongo)
        self.checkvalue("ne", 1, 0, Kweli )
        self.checkvalue("gt", 1, 0, Kweli )
        self.checkvalue("ge", 1, 0, Kweli )

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
        # Check that exceptions kwenye __bool__ are properly
        # propagated by the sio operator
        agiza operator
        kundi Exc(Exception):
            pass
        kundi Bad:
            eleza __bool__(self):
                 ashiria Exc

        eleza do(bad):
            sio bad

        kila func kwenye (do, operator.not_):
            self.assertRaises(Exc, func, Bad())

    @support.no_tracing
    eleza test_recursion(self):
        # Check that comparison kila recursive objects fails gracefully
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
        self.assertKweli(not (a == b))
        self.assertKweli(a != b)
        self.assertRaises(RecursionError, operator.lt, a, b)
        self.assertRaises(RecursionError, operator.le, a, b)
        self.assertRaises(RecursionError, operator.gt, a, b)
        self.assertRaises(RecursionError, operator.ge, a, b)
        a.append(17)
        self.assertRaises(RecursionError, operator.eq, a, b)
        self.assertRaises(RecursionError, operator.ne, a, b)
        a.insert(0, 11)
        b.insert(0, 12)
        self.assertKweli(not (a == b))
        self.assertKweli(a != b)
        self.assertKweli(a < b)

    eleza test_exception_message(self):
        kundi Spam:
            pass

        tests = [
            (lambda: 42 < Tupu, r"'<' .* of 'int' na 'TupuType'"),
            (lambda: Tupu < 42, r"'<' .* of 'TupuType' na 'int'"),
            (lambda: 42 > Tupu, r"'>' .* of 'int' na 'TupuType'"),
            (lambda: "foo" < Tupu, r"'<' .* of 'str' na 'TupuType'"),
            (lambda: "foo" >= 666, r"'>=' .* of 'str' na 'int'"),
            (lambda: 42 <= Tupu, r"'<=' .* of 'int' na 'TupuType'"),
            (lambda: 42 >= Tupu, r"'>=' .* of 'int' na 'TupuType'"),
            (lambda: 42 < [], r"'<' .* of 'int' na 'list'"),
            (lambda: () > [], r"'>' .* of 'tuple' na 'list'"),
            (lambda: Tupu >= Tupu, r"'>=' .* of 'TupuType' na 'TupuType'"),
            (lambda: Spam() < 42, r"'<' .* of 'Spam' na 'int'"),
            (lambda: 42 < Spam(), r"'<' .* of 'int' na 'Spam'"),
            (lambda: Spam() <= Spam(), r"'<=' .* of 'Spam' na 'Spam'"),
        ]
        kila i, test kwenye enumerate(tests):
            ukijumuisha self.subTest(test=i):
                ukijumuisha self.assertRaisesRegex(TypeError, test[1]):
                    test[0]()


kundi DictTest(unittest.TestCase):

    eleza test_dicts(self):
        # Verify that __eq__ na __ne__ work kila dicts even ikiwa the keys and
        # values don't support anything other than __eq__ na __ne__ (and
        # __hash__).  Complex numbers are a fine example of that.
        agiza random
        imag1a = {}
        kila i kwenye range(50):
            imag1a[random.randrange(100)*1j] = random.randrange(100)*1j
        items = list(imag1a.items())
        random.shuffle(items)
        imag1b = {}
        kila k, v kwenye items:
            imag1b[k] = v
        imag2 = imag1b.copy()
        imag2[k] = v + 1.0
        self.assertEqual(imag1a, imag1a)
        self.assertEqual(imag1a, imag1b)
        self.assertEqual(imag2, imag2)
        self.assertKweli(imag1a != imag2)
        kila opname kwenye ("lt", "le", "gt", "ge"):
            kila op kwenye opmap[opname]:
                self.assertRaises(TypeError, op, imag1a, imag2)

kundi ListTest(unittest.TestCase):

    eleza test_coverage(self):
        # exercise all comparisons kila lists
        x = [42]
        self.assertIs(x<x, Uongo)
        self.assertIs(x<=x, Kweli)
        self.assertIs(x==x, Kweli)
        self.assertIs(x!=x, Uongo)
        self.assertIs(x>x, Uongo)
        self.assertIs(x>=x, Kweli)
        y = [42, 42]
        self.assertIs(x<y, Kweli)
        self.assertIs(x<=y, Kweli)
        self.assertIs(x==y, Uongo)
        self.assertIs(x!=y, Kweli)
        self.assertIs(x>y, Uongo)
        self.assertIs(x>=y, Uongo)

    eleza test_badentry(self):
        # make sure that exceptions kila item comparison are properly
        # propagated kwenye list comparisons
        kundi Exc(Exception):
            pass
        kundi Bad:
            eleza __eq__(self, other):
                 ashiria Exc

        x = [Bad()]
        y = [Bad()]

        kila op kwenye opmap["eq"]:
            self.assertRaises(Exc, op, x, y)

    eleza test_goodentry(self):
        # This test exercises the final call to PyObject_RichCompare()
        # kwenye Objects/listobject.c::list_richcompare()
        kundi Good:
            eleza __lt__(self, other):
                rudisha Kweli

        x = [Good()]
        y = [Good()]

        kila op kwenye opmap["lt"]:
            self.assertIs(op(x, y), Kweli)


ikiwa __name__ == "__main__":
    unittest.main()
