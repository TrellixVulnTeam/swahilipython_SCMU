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

# These need to rudisha something other than None
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
    rudisha True

@trackCall
eleza __ne__(self, *args):
    rudisha False

@trackCall
eleza __lt__(self, *args):
    rudisha False

@trackCall
eleza __le__(self, *args):
    rudisha True

@trackCall
eleza __gt__(self, *args):
    rudisha False

@trackCall
eleza __ge__(self, *args):
    rudisha True
"""

# Synthesize all the other AllTests methods kutoka the names in testmeths.

method_template = """\
@trackCall
eleza __%s__(self, *args):
    pass
"""

d = {}
exec(statictests, globals(), d)
for method in testmeths:
    exec(method_template % method, globals(), d)
AllTests = type("AllTests", (object,), d)
del d, statictests, method, method_template

kundi ClassTests(unittest.TestCase):
    eleza setUp(self):
        callLst[:] = []

    eleza assertCallStack(self, expected_calls):
        actualCallList = callLst[:]  # need to copy because the comparison below will add
                                     # additional calls to callLst
        ikiwa expected_calls != actualCallList:
            self.fail("Expected call list:\n  %s\ndoes not match actual call list\n  %s" %
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

        kundi Empty: pass

        try:
            1 in Empty()
            self.fail('failed, should have raised TypeError')
        except TypeError:
            pass

        callLst[:] = []
        1 in testme
        self.assertCallStack([('__contains__', (testme, 1))])

        callLst[:] = []
        testme[1]
        self.assertCallStack([('__getitem__', (testme, 1))])

        callLst[:] = []
        testme[1] = 1
        self.assertCallStack([('__setitem__', (testme, 1, 1))])

        callLst[:] = []
        del testme[1]
        self.assertCallStack([('__delitem__', (testme, 1))])

        callLst[:] = []
        testme[:42]
        self.assertCallStack([('__getitem__', (testme, slice(None, 42)))])

        callLst[:] = []
        testme[:42] = "The Answer"
        self.assertCallStack([('__setitem__', (testme, slice(None, 42),
                                               "The Answer"))])

        callLst[:] = []
        del testme[:42]
        self.assertCallStack([('__delitem__', (testme, slice(None, 42)))])

        callLst[:] = []
        testme[2:1024:10]
        self.assertCallStack([('__getitem__', (testme, slice(2, 1024, 10)))])

        callLst[:] = []
        testme[2:1024:10] = "A lot"
        self.assertCallStack([('__setitem__', (testme, slice(2, 1024, 10),
                                                                    "A lot"))])
        callLst[:] = []
        del testme[2:1024:10]
        self.assertCallStack([('__delitem__', (testme, slice(2, 1024, 10)))])

        callLst[:] = []
        testme[:42, ..., :24:, 24, 100]
        self.assertCallStack([('__getitem__', (testme, (slice(None, 42, None),
                                                        Ellipsis,
                                                        slice(None, 24, None),
                                                        24, 100)))])
        callLst[:] = []
        testme[:42, ..., :24:, 24, 100] = "Strange"
        self.assertCallStack([('__setitem__', (testme, (slice(None, 42, None),
                                                        Ellipsis,
                                                        slice(None, 24, None),
                                                        24, 100), "Strange"))])
        callLst[:] = []
        del testme[:42, ..., :24:, 24, 100]
        self.assertCallStack([('__delitem__', (testme, (slice(None, 42, None),
                                                        Ellipsis,
                                                        slice(None, 24, None),
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
                pass

            @trackCall
            eleza __delattr__(self, *args):
                pass

        testme = ExtraTests()

        callLst[:] = []
        testme.spam
        self.assertCallStack([('__getattr__', (testme, "spam"))])

        callLst[:] = []
        testme.eggs = "spam, spam, spam and ham"
        self.assertCallStack([('__setattr__', (testme, "eggs",
                                               "spam, spam, spam and ham"))])

        callLst[:] = []
        del testme.cardinal
        self.assertCallStack([('__delattr__', (testme, "cardinal"))])

    eleza testDel(self):
        x = []

        kundi DelTest:
            eleza __del__(self):
                x.append("crab people, crab people")
        testme = DelTest()
        del testme
        agiza gc
        gc.collect()
        self.assertEqual(["crab people, crab people"], x)

    eleza testBadTypeReturned(self):
        # rudisha values of some method are type-checked
        kundi BadTypeClass:
            eleza __int__(self):
                rudisha None
            __float__ = __int__
            __complex__ = __int__
            __str__ = __int__
            __repr__ = __int__
            __bytes__ = __int__
            __bool__ = __int__
            __index__ = __int__
        eleza index(x):
            rudisha [][x]

        for f in [float, complex, str, repr, bytes, bin, oct, hex, bool, index]:
            self.assertRaises(TypeError, f, BadTypeClass())

    eleza testHashStuff(self):
        # Test correct errors kutoka hash() on objects with comparisons but
        #  no __hash__

        kundi C0:
            pass

        hash(C0()) # This should work; the next two should raise TypeError

        kundi C2:
            eleza __eq__(self, other): rudisha 1

        self.assertRaises(TypeError, hash, C2())


    eleza testSFBug532646(self):
        # Test for SF bug 532646

        kundi A:
            pass
        A.__call__ = A()
        a = A()

        try:
            a() # This should not segfault
        except RecursionError:
            pass
        else:
            self.fail("Failed to raise RecursionError")

    eleza testForExceptionsRaisedInInstanceGetattr2(self):
        # Tests for exceptions raised in instance_getattr2().

        eleza booh(self):
            raise AttributeError("booh")

        kundi A:
            a = property(booh)
        try:
            A().a # Raised AttributeError: A instance has no attribute 'a'
        except AttributeError as x:
            ikiwa str(x) != "booh":
                self.fail("attribute error for A().a got masked: %s" % x)

        kundi E:
            __eq__ = property(booh)
        E() == E() # In debug mode, caused a C-level assert() to fail

        kundi I:
            __init__ = property(booh)
        try:
            # In debug mode, printed XXX undetected error and
            #  raises AttributeError
            I()
        except AttributeError as x:
            pass
        else:
            self.fail("attribute error for I.__init__ got masked")

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
        # Test comparison and hash of methods
        kundi A:
            eleza __init__(self, x):
                self.x = x
            eleza f(self):
                pass
            eleza g(self):
                pass
            eleza __eq__(self, other):
                rudisha True
            eleza __hash__(self):
                raise TypeError
        kundi B(A):
            pass

        a1 = A(1)
        a2 = A(1)
        self.assertTrue(a1.f == a1.f)
        self.assertFalse(a1.f != a1.f)
        self.assertFalse(a1.f == a2.f)
        self.assertTrue(a1.f != a2.f)
        self.assertFalse(a1.f == a1.g)
        self.assertTrue(a1.f != a1.g)
        self.assertNotOrderable(a1.f, a1.f)
        self.assertEqual(hash(a1.f), hash(a1.f))

        self.assertFalse(A.f == a1.f)
        self.assertTrue(A.f != a1.f)
        self.assertFalse(A.f == A.g)
        self.assertTrue(A.f != A.g)
        self.assertTrue(B.f == A.f)
        self.assertFalse(B.f != A.f)
        self.assertNotOrderable(A.f, A.f)
        self.assertEqual(hash(B.f), hash(A.f))

        # the following triggers a SystemError in 2.4
        a = A(hash(A.f)^(-1))
        hash(a.f)

    eleza testSetattrWrapperNameIntern(self):
        # Issue #25794: __setattr__ should intern the attribute name
        kundi A:
            pass

        eleza add(self, other):
            rudisha 'summa'

        name = str(b'__add__', 'ascii')  # shouldn't be optimized
        self.assertIsNot(name, '__add__')  # not interned
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
            pass

        with self.assertRaises(TypeError):
            type.__setattr__(A, b'x', None)

    eleza testConstructorErrorMessages(self):
        # bpo-31506: Improves the error message logic for object_new & object_init

        # Class without any method overrides
        kundi C:
            pass

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
