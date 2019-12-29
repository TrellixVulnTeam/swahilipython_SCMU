"Test the functionality of Python classes implementing operators."

agiza unittest


testmeths = [

# Binary operations
    "add",
    "radd",
    "sub",
    "rsub",
    "mul",
    "rmul",
    "matmul",
    "rmatmul",
    "truediv",
    "rtruediv",
    "floordiv",
    "rfloordiv",
    "mod",
    "rmod",
    "divmod",
    "rdivmod",
    "pow",
    "rpow",
    "rshift",
    "rrshift",
    "lshift",
    "rlshift",
    "and",
    "rand",
    "or",
    "ror",
    "xor",
    "rxor",

# List/dict operations
    "contains",
    "getitem",
    "setitem",
    "delitem",

# Unary operations
    "neg",
    "pos",
    "abs",

# generic operations
    "init",
    ]

# These need to rudisha something other than Tupu
#    "hash",
#    "str",
#    "repr",
#    "int",
#    "float",

# These are separate because they can influence the test of other methods.
#    "getattr",
#    "setattr",
#    "delattr",

callLst = []
eleza trackCall(f):
    eleza track(*args, **kwargs):
        callLst.append((f.__name__, args))
        rudisha f(*args, **kwargs)
    rudisha track

statictests = """
@trackCall
eleza __hash__(self, *args):
    rudisha hash(id(self))

@trackCall
eleza __str__(self, *args):
    rudisha "AllTests"

@trackCall
eleza __repr__(self, *args):
    rudisha "AllTests"

@trackCall
eleza __int__(self, *args):
    rudisha 1

@trackCall
eleza __index__(self, *args):
    rudisha 1

@trackCall
eleza __float__(self, *args):
    rudisha 1.0

@trackCall
eleza __eq__(self, *args):
    rudisha Kweli

@trackCall
eleza __ne__(self, *args):
    rudisha Uongo

@trackCall
eleza __lt__(self, *args):
    rudisha Uongo

@trackCall
eleza __le__(self, *args):
    rudisha Kweli

@trackCall
eleza __gt__(self, *args):
    rudisha Uongo

@trackCall
eleza __ge__(self, *args):
    rudisha Kweli
"""

# Synthesize all the other AllTests methods kutoka the names kwenye testmeths.

method_template = """\
@trackCall
eleza __%s__(self, *args):
    pita
"""

d = {}
exec(statictests, globals(), d)
kila method kwenye testmeths:
    exec(method_template % method, globals(), d)
AllTests = type("AllTests", (object,), d)
toa d, statictests, method, method_template

kundi ClassTests(unittest.TestCase):
    eleza setUp(self):
        callLst[:] = []

    eleza assertCallStack(self, expected_calls):
        actualCallList = callLst[:]  # need to copy because the comparison below will add
                                     # additional calls to callLst
        ikiwa expected_calls != actualCallList:
            self.fail("Expected call list:\n  %s\ndoes sio match actual call list\n  %s" %
                      (expected_calls, actualCallList))

    eleza testInit(self):
        foo = AllTests()
        self.assertCallStack([("__init__", (foo,))])

    eleza testBinaryOps(self):
        testme = AllTests()
        # Binary operations

        callLst[:] = []
        testme + 1
        self.assertCallStack([("__add__", (testme, 1))])

        callLst[:] = []
        1 + testme
        self.assertCallStack([("__radd__", (testme, 1))])

        callLst[:] = []
        testme - 1
        self.assertCallStack([("__sub__", (testme, 1))])

        callLst[:] = []
        1 - testme
        self.assertCallStack([("__rsub__", (testme, 1))])

        callLst[:] = []
        testme * 1
        self.assertCallStack([("__mul__", (testme, 1))])

        callLst[:] = []
        1 * testme
        self.assertCallStack([("__rmul__", (testme, 1))])

        callLst[:] = []
        testme @ 1
        self.assertCallStack([("__matmul__", (testme, 1))])

        callLst[:] = []
        1 @ testme
        self.assertCallStack([("__rmatmul__", (testme, 1))])

        callLst[:] = []
        testme / 1
        self.assertCallStack([("__truediv__", (testme, 1))])


        callLst[:] = []
        1 / testme
        self.assertCallStack([("__rtruediv__", (testme, 1))])

        callLst[:] = []
        testme // 1
        self.assertCallStack([("__floordiv__", (testme, 1))])


        callLst[:] = []
        1 // testme
        self.assertCallStack([("__rfloordiv__", (testme, 1))])

        callLst[:] = []
        testme % 1
        self.assertCallStack([("__mod__", (testme, 1))])

        callLst[:] = []
        1 % testme
        self.assertCallStack([("__rmod__", (testme, 1))])


        callLst[:] = []
        divmod(testme,1)
        self.assertCallStack([("__divmod__", (testme, 1))])

        callLst[:] = []
        divmod(1, testme)
        self.assertCallStack([("__rdivmod__", (testme, 1))])

        callLst[:] = []
        testme ** 1
        self.assertCallStack([("__pow__", (testme, 1))])

        callLst[:] = []
        1 ** testme
        self.assertCallStack([("__rpow__", (testme, 1))])

        callLst[:] = []
        testme >> 1
        self.assertCallStack([("__rshift__", (testme, 1))])

        callLst[:] = []
        1 >> testme
        self.assertCallStack([("__rrshift__", (testme, 1))])

        callLst[:] = []
        testme << 1
        self.assertCallStack([("__lshift__", (testme, 1))])

        callLst[:] = []
        1 << testme
        self.assertCallStack([("__rlshift__", (testme, 1))])

        callLst[:] = []
        testme & 1
        self.assertCallStack([("__and__", (testme, 1))])

        callLst[:] = []
        1 & testme
        self.assertCallStack([("__rand__", (testme, 1))])

        callLst[:] = []
        testme | 1
        self.assertCallStack([("__or__", (testme, 1))])

        callLst[:] = []
        1 | testme
        self.assertCallStack([("__ror__", (testme, 1))])

        callLst[:] = []
        testme ^ 1
        self.assertCallStack([("__xor__", (testme, 1))])

        callLst[:] = []
        1 ^ testme
        self.assertCallStack([("__rxor__", (testme, 1))])

    eleza testListAndDictOps(self):
        testme = AllTests()

        # List/dict operations

        kundi Empty: pita

        jaribu:
            1 kwenye Empty()
            self.fail('failed, should have ashiriad TypeError')
        tatizo TypeError:
            pita

        callLst[:] = []
        1 kwenye testme
        self.assertCallStack([('__contains__', (testme, 1))])

        callLst[:] = []
        testme[1]
        self.assertCallStack([('__getitem__', (testme, 1))])

        callLst[:] = []
        testme[1] = 1
        self.assertCallStack([('__setitem__', (testme, 1, 1))])

        callLst[:] = []
        toa testme[1]
        self.assertCallStack([('__delitem__', (testme, 1))])

        callLst[:] = []
        testme[:42]
        self.assertCallStack([('__getitem__', (testme, slice(Tupu, 42)))])

        callLst[:] = []
        testme[:42] = "The Answer"
        self.assertCallStack([('__setitem__', (testme, slice(Tupu, 42),
                                               "The Answer"))])

        callLst[:] = []
        toa testme[:42]
        self.assertCallStack([('__delitem__', (testme, slice(Tupu, 42)))])

        callLst[:] = []
        testme[2:1024:10]
        self.assertCallStack([('__getitem__', (testme, slice(2, 1024, 10)))])

        callLst[:] = []
        testme[2:1024:10] = "A lot"
        self.assertCallStack([('__setitem__', (testme, slice(2, 1024, 10),
                                                                    "A lot"))])
        callLst[:] = []
        toa testme[2:1024:10]
        self.assertCallStack([('__delitem__', (testme, slice(2, 1024, 10)))])

        callLst[:] = []
        testme[:42, ..., :24:, 24, 100]
        self.assertCallStack([('__getitem__', (testme, (slice(Tupu, 42, Tupu),
                                                        Ellipsis,
                                                        slice(Tupu, 24, Tupu),
                                                        24, 100)))])
        callLst[:] = []
        testme[:42, ..., :24:, 24, 100] = "Strange"
        self.assertCallStack([('__setitem__', (testme, (slice(Tupu, 42, Tupu),
                                                        Ellipsis,
                                                        slice(Tupu, 24, Tupu),
                                                        24, 100), "Strange"))])
        callLst[:] = []
        toa testme[:42, ..., :24:, 24, 100]
        self.assertCallStack([('__delitem__', (testme, (slice(Tupu, 42, Tupu),
                                                        Ellipsis,
                                                        slice(Tupu, 24, Tupu),
                                                        24, 100)))])

    eleza testUnaryOps(self):
        testme = AllTests()

        callLst[:] = []
        -testme
        self.assertCallStack([('__neg__', (testme,))])
        callLst[:] = []
        +testme
        self.assertCallStack([('__pos__', (testme,))])
        callLst[:] = []
        abs(testme)
        self.assertCallStack([('__abs__', (testme,))])
        callLst[:] = []
        int(testme)
        self.assertCallStack([('__int__', (testme,))])
        callLst[:] = []
        float(testme)
        self.assertCallStack([('__float__', (testme,))])
        callLst[:] = []
        oct(testme)
        self.assertCallStack([('__index__', (testme,))])
        callLst[:] = []
        hex(testme)
        self.assertCallStack([('__index__', (testme,))])


    eleza testMisc(self):
        testme = AllTests()

        callLst[:] = []
        hash(testme)
        self.assertCallStack([('__hash__', (testme,))])

        callLst[:] = []
        repr(testme)
        self.assertCallStack([('__repr__', (testme,))])

        callLst[:] = []
        str(testme)
        self.assertCallStack([('__str__', (testme,))])

        callLst[:] = []
        testme == 1
        self.assertCallStack([('__eq__', (testme, 1))])

        callLst[:] = []
        testme < 1
        self.assertCallStack([('__lt__', (testme, 1))])

        callLst[:] = []
        testme > 1
        self.assertCallStack([('__gt__', (testme, 1))])

        callLst[:] = []
        testme != 1
        self.assertCallStack([('__ne__', (testme, 1))])

        callLst[:] = []
        1 == testme
        self.assertCallStack([('__eq__', (1, testme))])

        callLst[:] = []
        1 < testme
        self.assertCallStack([('__gt__', (1, testme))])

        callLst[:] = []
        1 > testme
        self.assertCallStack([('__lt__', (1, testme))])

        callLst[:] = []
        1 != testme
        self.assertCallStack([('__ne__', (1, testme))])


    eleza testGetSetAndDel(self):
        # Interfering tests
        kundi ExtraTests(AllTests):
            @trackCall
            eleza __getattr__(self, *args):
                rudisha "SomeVal"

            @trackCall
            eleza __setattr__(self, *args):
                pita

            @trackCall
            eleza __delattr__(self, *args):
                pita

        testme = ExtraTests()

        callLst[:] = []
        testme.spam
        self.assertCallStack([('__getattr__', (testme, "spam"))])

        callLst[:] = []
        testme.eggs = "spam, spam, spam na ham"
        self.assertCallStack([('__setattr__', (testme, "eggs",
                                               "spam, spam, spam na ham"))])

        callLst[:] = []
        toa testme.cardinal
        self.assertCallStack([('__delattr__', (testme, "cardinal"))])

    eleza testDel(self):
        x = []

        kundi DelTest:
            eleza __del__(self):
                x.append("crab people, crab people")
        testme = DelTest()
        toa testme
        agiza gc
        gc.collect()
        self.assertEqual(["crab people, crab people"], x)

    eleza testBadTypeReturned(self):
        # rudisha values of some method are type-checked
        kundi BadTypeClass:
            eleza __int__(self):
                rudisha Tupu
            __float__ = __int__
            __complex__ = __int__
            __str__ = __int__
            __repr__ = __int__
            __bytes__ = __int__
            __bool__ = __int__
            __index__ = __int__
        eleza index(x):
            rudisha [][x]

        kila f kwenye [float, complex, str, repr, bytes, bin, oct, hex, bool, index]:
            self.assertRaises(TypeError, f, BadTypeClass())

    eleza testHashStuff(self):
        # Test correct errors kutoka hash() on objects with comparisons but
        #  no __hash__

        kundi C0:
            pita

        hash(C0()) # This should work; the next two should ashiria TypeError

        kundi C2:
            eleza __eq__(self, other): rudisha 1

        self.assertRaises(TypeError, hash, C2())


    eleza testSFBug532646(self):
        # Test kila SF bug 532646

        kundi A:
            pita
        A.__call__ = A()
        a = A()

        jaribu:
            a() # This should sio segfault
        tatizo RecursionError:
            pita
        isipokua:
            self.fail("Failed to ashiria RecursionError")

    eleza testForExceptionsRaisedInInstanceGetattr2(self):
        # Tests kila exceptions ashiriad kwenye instance_getattr2().

        eleza booh(self):
            ashiria AttributeError("booh")

        kundi A:
            a = property(booh)
        jaribu:
            A().a # Raised AttributeError: A instance has no attribute 'a'
        tatizo AttributeError kama x:
            ikiwa str(x) != "booh":
                self.fail("attribute error kila A().a got masked: %s" % x)

        kundi E:
            __eq__ = property(booh)
        E() == E() # In debug mode, caused a C-level assert() to fail

        kundi I:
            __init__ = property(booh)
        jaribu:
            # In debug mode, printed XXX undetected error and
            #  ashirias AttributeError
            I()
        tatizo AttributeError kama x:
            pita
        isipokua:
            self.fail("attribute error kila I.__init__ got masked")

    eleza assertNotOrderable(self, a, b):
        with self.assertRaises(TypeError):
            a < b
        with self.assertRaises(TypeError):
            a > b
        with self.assertRaises(TypeError):
            a <= b
        with self.assertRaises(TypeError):
            a >= b

    eleza testHashComparisonOfMethods(self):
        # Test comparison na hash of methods
        kundi A:
            eleza __init__(self, x):
                self.x = x
            eleza f(self):
                pita
            eleza g(self):
                pita
            eleza __eq__(self, other):
                rudisha Kweli
            eleza __hash__(self):
                ashiria TypeError
        kundi B(A):
            pita

        a1 = A(1)
        a2 = A(1)
        self.assertKweli(a1.f == a1.f)
        self.assertUongo(a1.f != a1.f)
        self.assertUongo(a1.f == a2.f)
        self.assertKweli(a1.f != a2.f)
        self.assertUongo(a1.f == a1.g)
        self.assertKweli(a1.f != a1.g)
        self.assertNotOrderable(a1.f, a1.f)
        self.assertEqual(hash(a1.f), hash(a1.f))

        self.assertUongo(A.f == a1.f)
        self.assertKweli(A.f != a1.f)
        self.assertUongo(A.f == A.g)
        self.assertKweli(A.f != A.g)
        self.assertKweli(B.f == A.f)
        self.assertUongo(B.f != A.f)
        self.assertNotOrderable(A.f, A.f)
        self.assertEqual(hash(B.f), hash(A.f))

        # the following triggers a SystemError kwenye 2.4
        a = A(hash(A.f)^(-1))
        hash(a.f)

    eleza testSetattrWrapperNameIntern(self):
        # Issue #25794: __setattr__ should intern the attribute name
        kundi A:
            pita

        eleza add(self, other):
            rudisha 'summa'

        name = str(b'__add__', 'ascii')  # shouldn't be optimized
        self.assertIsNot(name, '__add__')  # sio interned
        type.__setattr__(A, name, add)
        self.assertEqual(A() + 1, 'summa')

        name2 = str(b'__add__', 'ascii')
        self.assertIsNot(name2, '__add__')
        self.assertIsNot(name2, name)
        type.__delattr__(A, name2)
        with self.assertRaises(TypeError):
            A() + 1

    eleza testSetattrNonStringName(self):
        kundi A:
            pita

        with self.assertRaises(TypeError):
            type.__setattr__(A, b'x', Tupu)

    eleza testConstructorErrorMessages(self):
        # bpo-31506: Improves the error message logic kila object_new & object_init

        # Class without any method overrides
        kundi C:
            pita

        error_msg = r'C.__init__\(\) takes exactly one argument \(the instance to initialize\)'

        with self.assertRaisesRegex(TypeError, r'C\(\) takes no arguments'):
            C(42)

        with self.assertRaisesRegex(TypeError, r'C\(\) takes no arguments'):
            C.__new__(C, 42)

        with self.assertRaisesRegex(TypeError, error_msg):
            C().__init__(42)

        with self.assertRaisesRegex(TypeError, r'C\(\) takes no arguments'):
            object.__new__(C, 42)

        with self.assertRaisesRegex(TypeError, error_msg):
            object.__init__(C(), 42)

        # Class with both `__init__` & `__new__` method overridden
        kundi D:
            eleza __new__(cls, *args, **kwargs):
                super().__new__(cls, *args, **kwargs)
            eleza __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

        error_msg =  r'object.__new__\(\) takes exactly one argument \(the type to instantiate\)'

        with self.assertRaisesRegex(TypeError, error_msg):
            D(42)

        with self.assertRaisesRegex(TypeError, error_msg):
            D.__new__(D, 42)

        with self.assertRaisesRegex(TypeError, error_msg):
            object.__new__(D, 42)

        # Class that only overrides __init__
        kundi E:
            eleza __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

        error_msg = r'object.__init__\(\) takes exactly one argument \(the instance to initialize\)'

        with self.assertRaisesRegex(TypeError, error_msg):
            E().__init__(42)

        with self.assertRaisesRegex(TypeError, error_msg):
            object.__init__(E(), 42)

ikiwa __name__ == '__main__':
    unittest.main()
