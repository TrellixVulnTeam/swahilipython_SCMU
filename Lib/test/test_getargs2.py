agiza unittest
agiza math
agiza string
agiza sys
kutoka test agiza support
# Skip this test ikiwa the _testcapi module isn't available.
_testcapi = support.import_module('_testcapi')
kutoka _testcapi agiza getargs_keywords, getargs_keyword_only

# > How about the following counterproposal. This also changes some of
# > the other format codes to be a little more regular.
# >
# > Code C type Range check
# >
# > b unsigned char 0..UCHAR_MAX
# > h signed short SHRT_MIN..SHRT_MAX
# > B unsigned char none **
# > H unsigned short none **
# > k * unsigned long none
# > I * unsigned int 0..UINT_MAX
#
#
# > i int INT_MIN..INT_MAX
# > l long LONG_MIN..LONG_MAX
#
# > K * unsigned long long none
# > L long long LLONG_MIN..LLONG_MAX
#
# > Notes:
# >
# > * New format codes.
# >
# > ** Changed kutoka previous "range-and-a-half" to "none"; the
# > range-and-a-half checking wasn't particularly useful.
#
# Plus a C API ama two, e.g. PyLong_AsUnsignedLongMask() ->
# unsigned long na PyLong_AsUnsignedLongLongMask() -> unsigned
# long long (ikiwa that exists).

LARGE = 0x7FFFFFFF
VERY_LARGE = 0xFF0000121212121212121242

kutoka _testcapi agiza UCHAR_MAX, USHRT_MAX, UINT_MAX, ULONG_MAX, INT_MAX, \
     INT_MIN, LONG_MIN, LONG_MAX, PY_SSIZE_T_MIN, PY_SSIZE_T_MAX, \
     SHRT_MIN, SHRT_MAX, FLT_MIN, FLT_MAX, DBL_MIN, DBL_MAX

DBL_MAX_EXP = sys.float_info.max_exp
INF = float('inf')
NAN = float('nan')

# fake, they are sio defined kwenye Python's header files
LLONG_MAX = 2**63-1
LLONG_MIN = -2**63
ULLONG_MAX = 2**64-1

kundi Index:
    eleza __index__(self):
        rudisha 99

kundi IndexIntSubclass(int):
    eleza __index__(self):
        rudisha 99

kundi BadIndex:
    eleza __index__(self):
        rudisha 1.0

kundi BadIndex2:
    eleza __index__(self):
        rudisha Kweli

kundi BadIndex3(int):
    eleza __index__(self):
        rudisha Kweli


kundi Int:
    eleza __int__(self):
        rudisha 99

kundi IntSubclass(int):
    eleza __int__(self):
        rudisha 99

kundi BadInt:
    eleza __int__(self):
        rudisha 1.0

kundi BadInt2:
    eleza __int__(self):
        rudisha Kweli

kundi BadInt3(int):
    eleza __int__(self):
        rudisha Kweli


kundi Float:
    eleza __float__(self):
        rudisha 4.25

kundi FloatSubclass(float):
    pita

kundi FloatSubclass2(float):
    eleza __float__(self):
        rudisha 4.25

kundi BadFloat:
    eleza __float__(self):
        rudisha 687

kundi BadFloat2:
    eleza __float__(self):
        rudisha FloatSubclass(4.25)

kundi BadFloat3(float):
    eleza __float__(self):
        rudisha FloatSubclass(4.25)


kundi Complex:
    eleza __complex__(self):
        rudisha 4.25+0.5j

kundi ComplexSubclass(complex):
    pita

kundi ComplexSubclass2(complex):
    eleza __complex__(self):
        rudisha 4.25+0.5j

kundi BadComplex:
    eleza __complex__(self):
        rudisha 1.25

kundi BadComplex2:
    eleza __complex__(self):
        rudisha ComplexSubclass(4.25+0.5j)

kundi BadComplex3(complex):
    eleza __complex__(self):
        rudisha ComplexSubclass(4.25+0.5j)


kundi TupleSubclass(tuple):
    pita

kundi DictSubclass(dict):
    pita


kundi Unsigned_TestCase(unittest.TestCase):
    eleza test_b(self):
        kutoka _testcapi agiza getargs_b
        # b rudishas 'unsigned char', na does range checking (0 ... UCHAR_MAX)
        self.assertRaises(TypeError, getargs_b, 3.14)
        self.assertEqual(99, getargs_b(Index()))
        self.assertEqual(0, getargs_b(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_b, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_b(BadIndex2()))
        self.assertEqual(0, getargs_b(BadIndex3()))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(99, getargs_b(Int()))
        self.assertEqual(0, getargs_b(IntSubclass()))
        self.assertRaises(TypeError, getargs_b, BadInt())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_b(BadInt2()))
        self.assertEqual(0, getargs_b(BadInt3()))

        self.assertRaises(OverflowError, getargs_b, -1)
        self.assertEqual(0, getargs_b(0))
        self.assertEqual(UCHAR_MAX, getargs_b(UCHAR_MAX))
        self.assertRaises(OverflowError, getargs_b, UCHAR_MAX + 1)

        self.assertEqual(42, getargs_b(42))
        self.assertRaises(OverflowError, getargs_b, VERY_LARGE)

    eleza test_B(self):
        kutoka _testcapi agiza getargs_B
        # B rudishas 'unsigned char', no range checking
        self.assertRaises(TypeError, getargs_B, 3.14)
        self.assertEqual(99, getargs_B(Index()))
        self.assertEqual(0, getargs_B(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_B, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_B(BadIndex2()))
        self.assertEqual(0, getargs_B(BadIndex3()))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(99, getargs_B(Int()))
        self.assertEqual(0, getargs_B(IntSubclass()))
        self.assertRaises(TypeError, getargs_B, BadInt())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_B(BadInt2()))
        self.assertEqual(0, getargs_B(BadInt3()))

        self.assertEqual(UCHAR_MAX, getargs_B(-1))
        self.assertEqual(0, getargs_B(0))
        self.assertEqual(UCHAR_MAX, getargs_B(UCHAR_MAX))
        self.assertEqual(0, getargs_B(UCHAR_MAX+1))

        self.assertEqual(42, getargs_B(42))
        self.assertEqual(UCHAR_MAX & VERY_LARGE, getargs_B(VERY_LARGE))

    eleza test_H(self):
        kutoka _testcapi agiza getargs_H
        # H rudishas 'unsigned short', no range checking
        self.assertRaises(TypeError, getargs_H, 3.14)
        self.assertEqual(99, getargs_H(Index()))
        self.assertEqual(0, getargs_H(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_H, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_H(BadIndex2()))
        self.assertEqual(0, getargs_H(BadIndex3()))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(99, getargs_H(Int()))
        self.assertEqual(0, getargs_H(IntSubclass()))
        self.assertRaises(TypeError, getargs_H, BadInt())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_H(BadInt2()))
        self.assertEqual(0, getargs_H(BadInt3()))

        self.assertEqual(USHRT_MAX, getargs_H(-1))
        self.assertEqual(0, getargs_H(0))
        self.assertEqual(USHRT_MAX, getargs_H(USHRT_MAX))
        self.assertEqual(0, getargs_H(USHRT_MAX+1))

        self.assertEqual(42, getargs_H(42))

        self.assertEqual(VERY_LARGE & USHRT_MAX, getargs_H(VERY_LARGE))

    eleza test_I(self):
        kutoka _testcapi agiza getargs_I
        # I rudishas 'unsigned int', no range checking
        self.assertRaises(TypeError, getargs_I, 3.14)
        self.assertEqual(99, getargs_I(Index()))
        self.assertEqual(0, getargs_I(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_I, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_I(BadIndex2()))
        self.assertEqual(0, getargs_I(BadIndex3()))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(99, getargs_I(Int()))
        self.assertEqual(0, getargs_I(IntSubclass()))
        self.assertRaises(TypeError, getargs_I, BadInt())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_I(BadInt2()))
        self.assertEqual(0, getargs_I(BadInt3()))

        self.assertEqual(UINT_MAX, getargs_I(-1))
        self.assertEqual(0, getargs_I(0))
        self.assertEqual(UINT_MAX, getargs_I(UINT_MAX))
        self.assertEqual(0, getargs_I(UINT_MAX+1))

        self.assertEqual(42, getargs_I(42))

        self.assertEqual(VERY_LARGE & UINT_MAX, getargs_I(VERY_LARGE))

    eleza test_k(self):
        kutoka _testcapi agiza getargs_k
        # k rudishas 'unsigned long', no range checking
        # it does sio accept float, ama instances with __int__
        self.assertRaises(TypeError, getargs_k, 3.14)
        self.assertRaises(TypeError, getargs_k, Index())
        self.assertEqual(0, getargs_k(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_k, BadIndex())
        self.assertRaises(TypeError, getargs_k, BadIndex2())
        self.assertEqual(0, getargs_k(BadIndex3()))
        self.assertRaises(TypeError, getargs_k, Int())
        self.assertEqual(0, getargs_k(IntSubclass()))
        self.assertRaises(TypeError, getargs_k, BadInt())
        self.assertRaises(TypeError, getargs_k, BadInt2())
        self.assertEqual(0, getargs_k(BadInt3()))

        self.assertEqual(ULONG_MAX, getargs_k(-1))
        self.assertEqual(0, getargs_k(0))
        self.assertEqual(ULONG_MAX, getargs_k(ULONG_MAX))
        self.assertEqual(0, getargs_k(ULONG_MAX+1))

        self.assertEqual(42, getargs_k(42))

        self.assertEqual(VERY_LARGE & ULONG_MAX, getargs_k(VERY_LARGE))

kundi Signed_TestCase(unittest.TestCase):
    eleza test_h(self):
        kutoka _testcapi agiza getargs_h
        # h rudishas 'short', na does range checking (SHRT_MIN ... SHRT_MAX)
        self.assertRaises(TypeError, getargs_h, 3.14)
        self.assertEqual(99, getargs_h(Index()))
        self.assertEqual(0, getargs_h(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_h, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_h(BadIndex2()))
        self.assertEqual(0, getargs_h(BadIndex3()))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(99, getargs_h(Int()))
        self.assertEqual(0, getargs_h(IntSubclass()))
        self.assertRaises(TypeError, getargs_h, BadInt())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_h(BadInt2()))
        self.assertEqual(0, getargs_h(BadInt3()))

        self.assertRaises(OverflowError, getargs_h, SHRT_MIN-1)
        self.assertEqual(SHRT_MIN, getargs_h(SHRT_MIN))
        self.assertEqual(SHRT_MAX, getargs_h(SHRT_MAX))
        self.assertRaises(OverflowError, getargs_h, SHRT_MAX+1)

        self.assertEqual(42, getargs_h(42))
        self.assertRaises(OverflowError, getargs_h, VERY_LARGE)

    eleza test_i(self):
        kutoka _testcapi agiza getargs_i
        # i rudishas 'int', na does range checking (INT_MIN ... INT_MAX)
        self.assertRaises(TypeError, getargs_i, 3.14)
        self.assertEqual(99, getargs_i(Index()))
        self.assertEqual(0, getargs_i(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_i, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_i(BadIndex2()))
        self.assertEqual(0, getargs_i(BadIndex3()))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(99, getargs_i(Int()))
        self.assertEqual(0, getargs_i(IntSubclass()))
        self.assertRaises(TypeError, getargs_i, BadInt())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_i(BadInt2()))
        self.assertEqual(0, getargs_i(BadInt3()))

        self.assertRaises(OverflowError, getargs_i, INT_MIN-1)
        self.assertEqual(INT_MIN, getargs_i(INT_MIN))
        self.assertEqual(INT_MAX, getargs_i(INT_MAX))
        self.assertRaises(OverflowError, getargs_i, INT_MAX+1)

        self.assertEqual(42, getargs_i(42))
        self.assertRaises(OverflowError, getargs_i, VERY_LARGE)

    eleza test_l(self):
        kutoka _testcapi agiza getargs_l
        # l rudishas 'long', na does range checking (LONG_MIN ... LONG_MAX)
        self.assertRaises(TypeError, getargs_l, 3.14)
        self.assertEqual(99, getargs_l(Index()))
        self.assertEqual(0, getargs_l(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_l, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_l(BadIndex2()))
        self.assertEqual(0, getargs_l(BadIndex3()))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(99, getargs_l(Int()))
        self.assertEqual(0, getargs_l(IntSubclass()))
        self.assertRaises(TypeError, getargs_l, BadInt())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_l(BadInt2()))
        self.assertEqual(0, getargs_l(BadInt3()))

        self.assertRaises(OverflowError, getargs_l, LONG_MIN-1)
        self.assertEqual(LONG_MIN, getargs_l(LONG_MIN))
        self.assertEqual(LONG_MAX, getargs_l(LONG_MAX))
        self.assertRaises(OverflowError, getargs_l, LONG_MAX+1)

        self.assertEqual(42, getargs_l(42))
        self.assertRaises(OverflowError, getargs_l, VERY_LARGE)

    eleza test_n(self):
        kutoka _testcapi agiza getargs_n
        # n rudishas 'Py_ssize_t', na does range checking
        # (PY_SSIZE_T_MIN ... PY_SSIZE_T_MAX)
        self.assertRaises(TypeError, getargs_n, 3.14)
        self.assertEqual(99, getargs_n(Index()))
        self.assertEqual(0, getargs_n(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_n, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_n(BadIndex2()))
        self.assertEqual(0, getargs_n(BadIndex3()))
        self.assertRaises(TypeError, getargs_n, Int())
        self.assertEqual(0, getargs_n(IntSubclass()))
        self.assertRaises(TypeError, getargs_n, BadInt())
        self.assertRaises(TypeError, getargs_n, BadInt2())
        self.assertEqual(0, getargs_n(BadInt3()))

        self.assertRaises(OverflowError, getargs_n, PY_SSIZE_T_MIN-1)
        self.assertEqual(PY_SSIZE_T_MIN, getargs_n(PY_SSIZE_T_MIN))
        self.assertEqual(PY_SSIZE_T_MAX, getargs_n(PY_SSIZE_T_MAX))
        self.assertRaises(OverflowError, getargs_n, PY_SSIZE_T_MAX+1)

        self.assertEqual(42, getargs_n(42))
        self.assertRaises(OverflowError, getargs_n, VERY_LARGE)


kundi LongLong_TestCase(unittest.TestCase):
    eleza test_L(self):
        kutoka _testcapi agiza getargs_L
        # L rudishas 'long long', na does range checking (LLONG_MIN
        # ... LLONG_MAX)
        self.assertRaises(TypeError, getargs_L, 3.14)
        self.assertRaises(TypeError, getargs_L, "Hello")
        self.assertEqual(99, getargs_L(Index()))
        self.assertEqual(0, getargs_L(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_L, BadIndex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_L(BadIndex2()))
        self.assertEqual(0, getargs_L(BadIndex3()))
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(99, getargs_L(Int()))
        self.assertEqual(0, getargs_L(IntSubclass()))
        self.assertRaises(TypeError, getargs_L, BadInt())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(1, getargs_L(BadInt2()))
        self.assertEqual(0, getargs_L(BadInt3()))

        self.assertRaises(OverflowError, getargs_L, LLONG_MIN-1)
        self.assertEqual(LLONG_MIN, getargs_L(LLONG_MIN))
        self.assertEqual(LLONG_MAX, getargs_L(LLONG_MAX))
        self.assertRaises(OverflowError, getargs_L, LLONG_MAX+1)

        self.assertEqual(42, getargs_L(42))
        self.assertRaises(OverflowError, getargs_L, VERY_LARGE)

    eleza test_K(self):
        kutoka _testcapi agiza getargs_K
        # K rudisha 'unsigned long long', no range checking
        self.assertRaises(TypeError, getargs_K, 3.14)
        self.assertRaises(TypeError, getargs_K, Index())
        self.assertEqual(0, getargs_K(IndexIntSubclass()))
        self.assertRaises(TypeError, getargs_K, BadIndex())
        self.assertRaises(TypeError, getargs_K, BadIndex2())
        self.assertEqual(0, getargs_K(BadIndex3()))
        self.assertRaises(TypeError, getargs_K, Int())
        self.assertEqual(0, getargs_K(IntSubclass()))
        self.assertRaises(TypeError, getargs_K, BadInt())
        self.assertRaises(TypeError, getargs_K, BadInt2())
        self.assertEqual(0, getargs_K(BadInt3()))

        self.assertEqual(ULLONG_MAX, getargs_K(ULLONG_MAX))
        self.assertEqual(0, getargs_K(0))
        self.assertEqual(0, getargs_K(ULLONG_MAX+1))

        self.assertEqual(42, getargs_K(42))

        self.assertEqual(VERY_LARGE & ULLONG_MAX, getargs_K(VERY_LARGE))


kundi Float_TestCase(unittest.TestCase):
    eleza assertEqualWithSign(self, actual, expected):
        self.assertEqual(actual, expected)
        self.assertEqual(math.copysign(1, actual), math.copysign(1, expected))

    eleza test_f(self):
        kutoka _testcapi agiza getargs_f
        self.assertEqual(getargs_f(4.25), 4.25)
        self.assertEqual(getargs_f(4), 4.0)
        self.assertRaises(TypeError, getargs_f, 4.25+0j)
        self.assertEqual(getargs_f(Float()), 4.25)
        self.assertEqual(getargs_f(FloatSubclass(7.5)), 7.5)
        self.assertEqual(getargs_f(FloatSubclass2(7.5)), 7.5)
        self.assertRaises(TypeError, getargs_f, BadFloat())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(getargs_f(BadFloat2()), 4.25)
        self.assertEqual(getargs_f(BadFloat3(7.5)), 7.5)
        self.assertEqual(getargs_f(Index()), 99.0)
        self.assertRaises(TypeError, getargs_f, Int())

        kila x kwenye (FLT_MIN, -FLT_MIN, FLT_MAX, -FLT_MAX, INF, -INF):
            self.assertEqual(getargs_f(x), x)
        ikiwa FLT_MAX < DBL_MAX:
            self.assertEqual(getargs_f(DBL_MAX), INF)
            self.assertEqual(getargs_f(-DBL_MAX), -INF)
        ikiwa FLT_MIN > DBL_MIN:
            self.assertEqualWithSign(getargs_f(DBL_MIN), 0.0)
            self.assertEqualWithSign(getargs_f(-DBL_MIN), -0.0)
        self.assertEqualWithSign(getargs_f(0.0), 0.0)
        self.assertEqualWithSign(getargs_f(-0.0), -0.0)
        r = getargs_f(NAN)
        self.assertNotEqual(r, r)

    @support.requires_IEEE_754
    eleza test_f_rounding(self):
        kutoka _testcapi agiza getargs_f
        self.assertEqual(getargs_f(3.40282356e38), FLT_MAX)
        self.assertEqual(getargs_f(-3.40282356e38), -FLT_MAX)

    eleza test_d(self):
        kutoka _testcapi agiza getargs_d
        self.assertEqual(getargs_d(4.25), 4.25)
        self.assertEqual(getargs_d(4), 4.0)
        self.assertRaises(TypeError, getargs_d, 4.25+0j)
        self.assertEqual(getargs_d(Float()), 4.25)
        self.assertEqual(getargs_d(FloatSubclass(7.5)), 7.5)
        self.assertEqual(getargs_d(FloatSubclass2(7.5)), 7.5)
        self.assertRaises(TypeError, getargs_d, BadFloat())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(getargs_d(BadFloat2()), 4.25)
        self.assertEqual(getargs_d(BadFloat3(7.5)), 7.5)
        self.assertEqual(getargs_d(Index()), 99.0)
        self.assertRaises(TypeError, getargs_d, Int())

        kila x kwenye (DBL_MIN, -DBL_MIN, DBL_MAX, -DBL_MAX, INF, -INF):
            self.assertEqual(getargs_d(x), x)
        self.assertRaises(OverflowError, getargs_d, 1<<DBL_MAX_EXP)
        self.assertRaises(OverflowError, getargs_d, -1<<DBL_MAX_EXP)
        self.assertEqualWithSign(getargs_d(0.0), 0.0)
        self.assertEqualWithSign(getargs_d(-0.0), -0.0)
        r = getargs_d(NAN)
        self.assertNotEqual(r, r)

    eleza test_D(self):
        kutoka _testcapi agiza getargs_D
        self.assertEqual(getargs_D(4.25+0.5j), 4.25+0.5j)
        self.assertEqual(getargs_D(4.25), 4.25+0j)
        self.assertEqual(getargs_D(4), 4.0+0j)
        self.assertEqual(getargs_D(Complex()), 4.25+0.5j)
        self.assertEqual(getargs_D(ComplexSubclass(7.5+0.25j)), 7.5+0.25j)
        self.assertEqual(getargs_D(ComplexSubclass2(7.5+0.25j)), 7.5+0.25j)
        self.assertRaises(TypeError, getargs_D, BadComplex())
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(getargs_D(BadComplex2()), 4.25+0.5j)
        self.assertEqual(getargs_D(BadComplex3(7.5+0.25j)), 7.5+0.25j)
        self.assertEqual(getargs_D(Index()), 99.0+0j)
        self.assertRaises(TypeError, getargs_D, Int())

        kila x kwenye (DBL_MIN, -DBL_MIN, DBL_MAX, -DBL_MAX, INF, -INF):
            c = complex(x, 1.0)
            self.assertEqual(getargs_D(c), c)
            c = complex(1.0, x)
            self.assertEqual(getargs_D(c), c)
        self.assertEqualWithSign(getargs_D(complex(0.0, 1.0)).real, 0.0)
        self.assertEqualWithSign(getargs_D(complex(-0.0, 1.0)).real, -0.0)
        self.assertEqualWithSign(getargs_D(complex(1.0, 0.0)).imag, 0.0)
        self.assertEqualWithSign(getargs_D(complex(1.0, -0.0)).imag, -0.0)


kundi Paradox:
    "This statement ni false."
    eleza __bool__(self):
        ashiria NotImplementedError

kundi Boolean_TestCase(unittest.TestCase):
    eleza test_p(self):
        kutoka _testcapi agiza getargs_p
        self.assertEqual(0, getargs_p(Uongo))
        self.assertEqual(0, getargs_p(Tupu))
        self.assertEqual(0, getargs_p(0))
        self.assertEqual(0, getargs_p(0.0))
        self.assertEqual(0, getargs_p(0j))
        self.assertEqual(0, getargs_p(''))
        self.assertEqual(0, getargs_p(()))
        self.assertEqual(0, getargs_p([]))
        self.assertEqual(0, getargs_p({}))

        self.assertEqual(1, getargs_p(Kweli))
        self.assertEqual(1, getargs_p(1))
        self.assertEqual(1, getargs_p(1.0))
        self.assertEqual(1, getargs_p(1j))
        self.assertEqual(1, getargs_p('x'))
        self.assertEqual(1, getargs_p((1,)))
        self.assertEqual(1, getargs_p([1]))
        self.assertEqual(1, getargs_p({1:2}))
        self.assertEqual(1, getargs_p(unittest.TestCase))

        self.assertRaises(NotImplementedError, getargs_p, Paradox())


kundi Tuple_TestCase(unittest.TestCase):
    eleza test_args(self):
        kutoka _testcapi agiza get_args

        ret = get_args(1, 2)
        self.assertEqual(ret, (1, 2))
        self.assertIs(type(ret), tuple)

        ret = get_args(1, *(2, 3))
        self.assertEqual(ret, (1, 2, 3))
        self.assertIs(type(ret), tuple)

        ret = get_args(*[1, 2])
        self.assertEqual(ret, (1, 2))
        self.assertIs(type(ret), tuple)

        ret = get_args(*TupleSubclass([1, 2]))
        self.assertEqual(ret, (1, 2))
        self.assertIs(type(ret), tuple)

        ret = get_args()
        self.assertIn(ret, ((), Tupu))
        self.assertIn(type(ret), (tuple, type(Tupu)))

        ret = get_args(*())
        self.assertIn(ret, ((), Tupu))
        self.assertIn(type(ret), (tuple, type(Tupu)))

    eleza test_tuple(self):
        kutoka _testcapi agiza getargs_tuple

        ret = getargs_tuple(1, (2, 3))
        self.assertEqual(ret, (1,2,3))

        # make sure invalid tuple arguments are handled correctly
        kundi seq:
            eleza __len__(self):
                rudisha 2
            eleza __getitem__(self, n):
                ashiria ValueError
        self.assertRaises(TypeError, getargs_tuple, 1, seq())

kundi Keywords_TestCase(unittest.TestCase):
    eleza test_kwargs(self):
        kutoka _testcapi agiza get_kwargs

        ret = get_kwargs(a=1, b=2)
        self.assertEqual(ret, {'a': 1, 'b': 2})
        self.assertIs(type(ret), dict)

        ret = get_kwargs(a=1, **{'b': 2, 'c': 3})
        self.assertEqual(ret, {'a': 1, 'b': 2, 'c': 3})
        self.assertIs(type(ret), dict)

        ret = get_kwargs(**DictSubclass({'a': 1, 'b': 2}))
        self.assertEqual(ret, {'a': 1, 'b': 2})
        self.assertIs(type(ret), dict)

        ret = get_kwargs()
        self.assertIn(ret, ({}, Tupu))
        self.assertIn(type(ret), (dict, type(Tupu)))

        ret = get_kwargs(**{})
        self.assertIn(ret, ({}, Tupu))
        self.assertIn(type(ret), (dict, type(Tupu)))

    eleza test_positional_args(self):
        # using all positional args
        self.assertEqual(
            getargs_keywords((1,2), 3, (4,(5,6)), (7,8,9), 10),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            )

    eleza test_mixed_args(self):
        # positional na keyword args
        self.assertEqual(
            getargs_keywords((1,2), 3, (4,(5,6)), arg4=(7,8,9), arg5=10),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            )

    eleza test_keyword_args(self):
        # all keywords
        self.assertEqual(
            getargs_keywords(arg1=(1,2), arg2=3, arg3=(4,(5,6)), arg4=(7,8,9), arg5=10),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            )

    eleza test_optional_args(self):
        # missing optional keyword args, skipping tuples
        self.assertEqual(
            getargs_keywords(arg1=(1,2), arg2=3, arg5=10),
            (1, 2, 3, -1, -1, -1, -1, -1, -1, 10)
            )

    eleza test_required_args(self):
        # required arg missing
        jaribu:
            getargs_keywords(arg1=(1,2))
        tatizo TypeError kama err:
            self.assertEqual(
                str(err), "function missing required argument 'arg2' (pos 2)")
        isipokua:
            self.fail('TypeError should have been ashiriad')

    eleza test_too_many_args(self):
        jaribu:
            getargs_keywords((1,2),3,(4,(5,6)),(7,8,9),10,111)
        tatizo TypeError kama err:
            self.assertEqual(str(err), "function takes at most 5 arguments (6 given)")
        isipokua:
            self.fail('TypeError should have been ashiriad')

    eleza test_invalid_keyword(self):
        # extraneous keyword arg
        jaribu:
            getargs_keywords((1,2),3,arg5=10,arg666=666)
        tatizo TypeError kama err:
            self.assertEqual(str(err), "'arg666' ni an invalid keyword argument kila this function")
        isipokua:
            self.fail('TypeError should have been ashiriad')

    eleza test_surrogate_keyword(self):
        jaribu:
            getargs_keywords((1,2), 3, (4,(5,6)), (7,8,9), **{'\uDC80': 10})
        tatizo TypeError kama err:
            self.assertEqual(str(err), "'\udc80' ni an invalid keyword argument kila this function")
        isipokua:
            self.fail('TypeError should have been ashiriad')

kundi KeywordOnly_TestCase(unittest.TestCase):
    eleza test_positional_args(self):
        # using all possible positional args
        self.assertEqual(
            getargs_keyword_only(1, 2),
            (1, 2, -1)
            )

    eleza test_mixed_args(self):
        # positional na keyword args
        self.assertEqual(
            getargs_keyword_only(1, 2, keyword_only=3),
            (1, 2, 3)
            )

    eleza test_keyword_args(self):
        # all keywords
        self.assertEqual(
            getargs_keyword_only(required=1, optional=2, keyword_only=3),
            (1, 2, 3)
            )

    eleza test_optional_args(self):
        # missing optional keyword args, skipping tuples
        self.assertEqual(
            getargs_keyword_only(required=1, optional=2),
            (1, 2, -1)
            )
        self.assertEqual(
            getargs_keyword_only(required=1, keyword_only=3),
            (1, -1, 3)
            )

    eleza test_required_args(self):
        self.assertEqual(
            getargs_keyword_only(1),
            (1, -1, -1)
            )
        self.assertEqual(
            getargs_keyword_only(required=1),
            (1, -1, -1)
            )
        # required arg missing
        with self.assertRaisesRegex(TypeError,
            r"function missing required argument 'required' \(pos 1\)"):
            getargs_keyword_only(optional=2)

        with self.assertRaisesRegex(TypeError,
            r"function missing required argument 'required' \(pos 1\)"):
            getargs_keyword_only(keyword_only=3)

    eleza test_too_many_args(self):
        with self.assertRaisesRegex(TypeError,
            r"function takes at most 2 positional arguments \(3 given\)"):
            getargs_keyword_only(1, 2, 3)

        with self.assertRaisesRegex(TypeError,
            r"function takes at most 3 arguments \(4 given\)"):
            getargs_keyword_only(1, 2, 3, keyword_only=5)

    eleza test_invalid_keyword(self):
        # extraneous keyword arg
        with self.assertRaisesRegex(TypeError,
            "'monster' ni an invalid keyword argument kila this function"):
            getargs_keyword_only(1, 2, monster=666)

    eleza test_surrogate_keyword(self):
        with self.assertRaisesRegex(TypeError,
            "'\udc80' ni an invalid keyword argument kila this function"):
            getargs_keyword_only(1, 2, **{'\uDC80': 10})


kundi PositionalOnlyAndKeywords_TestCase(unittest.TestCase):
    kutoka _testcapi agiza getargs_positional_only_and_keywords kama getargs

    eleza test_positional_args(self):
        # using all possible positional args
        self.assertEqual(self.getargs(1, 2, 3), (1, 2, 3))

    eleza test_mixed_args(self):
        # positional na keyword args
        self.assertEqual(self.getargs(1, 2, keyword=3), (1, 2, 3))

    eleza test_optional_args(self):
        # missing optional args
        self.assertEqual(self.getargs(1, 2), (1, 2, -1))
        self.assertEqual(self.getargs(1, keyword=3), (1, -1, 3))

    eleza test_required_args(self):
        self.assertEqual(self.getargs(1), (1, -1, -1))
        # required positional arg missing
        with self.assertRaisesRegex(TypeError,
            r"function takes at least 1 positional argument \(0 given\)"):
            self.getargs()

        with self.assertRaisesRegex(TypeError,
            r"function takes at least 1 positional argument \(0 given\)"):
            self.getargs(keyword=3)

    eleza test_empty_keyword(self):
        with self.assertRaisesRegex(TypeError,
            "'' ni an invalid keyword argument kila this function"):
            self.getargs(1, 2, **{'': 666})


kundi Bytes_TestCase(unittest.TestCase):
    eleza test_c(self):
        kutoka _testcapi agiza getargs_c
        self.assertRaises(TypeError, getargs_c, b'abc')  # len > 1
        self.assertEqual(getargs_c(b'a'), 97)
        self.assertEqual(getargs_c(bytearray(b'a')), 97)
        self.assertRaises(TypeError, getargs_c, memoryview(b'a'))
        self.assertRaises(TypeError, getargs_c, 's')
        self.assertRaises(TypeError, getargs_c, 97)
        self.assertRaises(TypeError, getargs_c, Tupu)

    eleza test_y(self):
        kutoka _testcapi agiza getargs_y
        self.assertRaises(TypeError, getargs_y, 'abc\xe9')
        self.assertEqual(getargs_y(b'bytes'), b'bytes')
        self.assertRaises(ValueError, getargs_y, b'nul:\0')
        self.assertRaises(TypeError, getargs_y, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_y, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_y, Tupu)

    eleza test_y_star(self):
        kutoka _testcapi agiza getargs_y_star
        self.assertRaises(TypeError, getargs_y_star, 'abc\xe9')
        self.assertEqual(getargs_y_star(b'bytes'), b'bytes')
        self.assertEqual(getargs_y_star(b'nul:\0'), b'nul:\0')
        self.assertEqual(getargs_y_star(bytearray(b'bytearray')), b'bytearray')
        self.assertEqual(getargs_y_star(memoryview(b'memoryview')), b'memoryview')
        self.assertRaises(TypeError, getargs_y_star, Tupu)

    eleza test_y_hash(self):
        kutoka _testcapi agiza getargs_y_hash
        self.assertRaises(TypeError, getargs_y_hash, 'abc\xe9')
        self.assertEqual(getargs_y_hash(b'bytes'), b'bytes')
        self.assertEqual(getargs_y_hash(b'nul:\0'), b'nul:\0')
        self.assertRaises(TypeError, getargs_y_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_y_hash, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_y_hash, Tupu)

    eleza test_w_star(self):
        # getargs_w_star() modifies first na last byte
        kutoka _testcapi agiza getargs_w_star
        self.assertRaises(TypeError, getargs_w_star, 'abc\xe9')
        self.assertRaises(TypeError, getargs_w_star, b'bytes')
        self.assertRaises(TypeError, getargs_w_star, b'nul:\0')
        self.assertRaises(TypeError, getargs_w_star, memoryview(b'bytes'))
        buf = bytearray(b'bytearray')
        self.assertEqual(getargs_w_star(buf), b'[ytearra]')
        self.assertEqual(buf, bytearray(b'[ytearra]'))
        buf = bytearray(b'memoryview')
        self.assertEqual(getargs_w_star(memoryview(buf)), b'[emoryvie]')
        self.assertEqual(buf, bytearray(b'[emoryvie]'))
        self.assertRaises(TypeError, getargs_w_star, Tupu)


kundi String_TestCase(unittest.TestCase):
    eleza test_C(self):
        kutoka _testcapi agiza getargs_C
        self.assertRaises(TypeError, getargs_C, 'abc')  # len > 1
        self.assertEqual(getargs_C('a'), 97)
        self.assertEqual(getargs_C('\u20ac'), 0x20ac)
        self.assertEqual(getargs_C('\U0001f40d'), 0x1f40d)
        self.assertRaises(TypeError, getargs_C, b'a')
        self.assertRaises(TypeError, getargs_C, bytearray(b'a'))
        self.assertRaises(TypeError, getargs_C, memoryview(b'a'))
        self.assertRaises(TypeError, getargs_C, 97)
        self.assertRaises(TypeError, getargs_C, Tupu)

    eleza test_s(self):
        kutoka _testcapi agiza getargs_s
        self.assertEqual(getargs_s('abc\xe9'), b'abc\xc3\xa9')
        self.assertRaises(ValueError, getargs_s, 'nul:\0')
        self.assertRaises(TypeError, getargs_s, b'bytes')
        self.assertRaises(TypeError, getargs_s, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_s, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_s, Tupu)

    eleza test_s_star(self):
        kutoka _testcapi agiza getargs_s_star
        self.assertEqual(getargs_s_star('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_s_star('nul:\0'), b'nul:\0')
        self.assertEqual(getargs_s_star(b'bytes'), b'bytes')
        self.assertEqual(getargs_s_star(bytearray(b'bytearray')), b'bytearray')
        self.assertEqual(getargs_s_star(memoryview(b'memoryview')), b'memoryview')
        self.assertRaises(TypeError, getargs_s_star, Tupu)

    eleza test_s_hash(self):
        kutoka _testcapi agiza getargs_s_hash
        self.assertEqual(getargs_s_hash('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_s_hash('nul:\0'), b'nul:\0')
        self.assertEqual(getargs_s_hash(b'bytes'), b'bytes')
        self.assertRaises(TypeError, getargs_s_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_s_hash, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_s_hash, Tupu)

    eleza test_z(self):
        kutoka _testcapi agiza getargs_z
        self.assertEqual(getargs_z('abc\xe9'), b'abc\xc3\xa9')
        self.assertRaises(ValueError, getargs_z, 'nul:\0')
        self.assertRaises(TypeError, getargs_z, b'bytes')
        self.assertRaises(TypeError, getargs_z, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_z, memoryview(b'memoryview'))
        self.assertIsTupu(getargs_z(Tupu))

    eleza test_z_star(self):
        kutoka _testcapi agiza getargs_z_star
        self.assertEqual(getargs_z_star('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_z_star('nul:\0'), b'nul:\0')
        self.assertEqual(getargs_z_star(b'bytes'), b'bytes')
        self.assertEqual(getargs_z_star(bytearray(b'bytearray')), b'bytearray')
        self.assertEqual(getargs_z_star(memoryview(b'memoryview')), b'memoryview')
        self.assertIsTupu(getargs_z_star(Tupu))

    eleza test_z_hash(self):
        kutoka _testcapi agiza getargs_z_hash
        self.assertEqual(getargs_z_hash('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_z_hash('nul:\0'), b'nul:\0')
        self.assertEqual(getargs_z_hash(b'bytes'), b'bytes')
        self.assertRaises(TypeError, getargs_z_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_z_hash, memoryview(b'memoryview'))
        self.assertIsTupu(getargs_z_hash(Tupu))

    eleza test_es(self):
        kutoka _testcapi agiza getargs_es
        self.assertEqual(getargs_es('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_es('abc\xe9', 'latin1'), b'abc\xe9')
        self.assertRaises(UnicodeEncodeError, getargs_es, 'abc\xe9', 'ascii')
        self.assertRaises(LookupError, getargs_es, 'abc\xe9', 'spam')
        self.assertRaises(TypeError, getargs_es, b'bytes', 'latin1')
        self.assertRaises(TypeError, getargs_es, bytearray(b'bytearray'), 'latin1')
        self.assertRaises(TypeError, getargs_es, memoryview(b'memoryview'), 'latin1')
        self.assertRaises(TypeError, getargs_es, Tupu, 'latin1')
        self.assertRaises(TypeError, getargs_es, 'nul:\0', 'latin1')

    eleza test_et(self):
        kutoka _testcapi agiza getargs_et
        self.assertEqual(getargs_et('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_et('abc\xe9', 'latin1'), b'abc\xe9')
        self.assertRaises(UnicodeEncodeError, getargs_et, 'abc\xe9', 'ascii')
        self.assertRaises(LookupError, getargs_et, 'abc\xe9', 'spam')
        self.assertEqual(getargs_et(b'bytes', 'latin1'), b'bytes')
        self.assertEqual(getargs_et(bytearray(b'bytearray'), 'latin1'), b'bytearray')
        self.assertRaises(TypeError, getargs_et, memoryview(b'memoryview'), 'latin1')
        self.assertRaises(TypeError, getargs_et, Tupu, 'latin1')
        self.assertRaises(TypeError, getargs_et, 'nul:\0', 'latin1')
        self.assertRaises(TypeError, getargs_et, b'nul:\0', 'latin1')
        self.assertRaises(TypeError, getargs_et, bytearray(b'nul:\0'), 'latin1')

    eleza test_es_hash(self):
        kutoka _testcapi agiza getargs_es_hash
        self.assertEqual(getargs_es_hash('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_es_hash('abc\xe9', 'latin1'), b'abc\xe9')
        self.assertRaises(UnicodeEncodeError, getargs_es_hash, 'abc\xe9', 'ascii')
        self.assertRaises(LookupError, getargs_es_hash, 'abc\xe9', 'spam')
        self.assertRaises(TypeError, getargs_es_hash, b'bytes', 'latin1')
        self.assertRaises(TypeError, getargs_es_hash, bytearray(b'bytearray'), 'latin1')
        self.assertRaises(TypeError, getargs_es_hash, memoryview(b'memoryview'), 'latin1')
        self.assertRaises(TypeError, getargs_es_hash, Tupu, 'latin1')
        self.assertEqual(getargs_es_hash('nul:\0', 'latin1'), b'nul:\0')

        buf = bytearray(b'x'*8)
        self.assertEqual(getargs_es_hash('abc\xe9', 'latin1', buf), b'abc\xe9')
        self.assertEqual(buf, bytearray(b'abc\xe9\x00xxx'))
        buf = bytearray(b'x'*5)
        self.assertEqual(getargs_es_hash('abc\xe9', 'latin1', buf), b'abc\xe9')
        self.assertEqual(buf, bytearray(b'abc\xe9\x00'))
        buf = bytearray(b'x'*4)
        self.assertRaises(ValueError, getargs_es_hash, 'abc\xe9', 'latin1', buf)
        self.assertEqual(buf, bytearray(b'x'*4))
        buf = bytearray()
        self.assertRaises(ValueError, getargs_es_hash, 'abc\xe9', 'latin1', buf)

    eleza test_et_hash(self):
        kutoka _testcapi agiza getargs_et_hash
        self.assertEqual(getargs_et_hash('abc\xe9'), b'abc\xc3\xa9')
        self.assertEqual(getargs_et_hash('abc\xe9', 'latin1'), b'abc\xe9')
        self.assertRaises(UnicodeEncodeError, getargs_et_hash, 'abc\xe9', 'ascii')
        self.assertRaises(LookupError, getargs_et_hash, 'abc\xe9', 'spam')
        self.assertEqual(getargs_et_hash(b'bytes', 'latin1'), b'bytes')
        self.assertEqual(getargs_et_hash(bytearray(b'bytearray'), 'latin1'), b'bytearray')
        self.assertRaises(TypeError, getargs_et_hash, memoryview(b'memoryview'), 'latin1')
        self.assertRaises(TypeError, getargs_et_hash, Tupu, 'latin1')
        self.assertEqual(getargs_et_hash('nul:\0', 'latin1'), b'nul:\0')
        self.assertEqual(getargs_et_hash(b'nul:\0', 'latin1'), b'nul:\0')
        self.assertEqual(getargs_et_hash(bytearray(b'nul:\0'), 'latin1'), b'nul:\0')

        buf = bytearray(b'x'*8)
        self.assertEqual(getargs_et_hash('abc\xe9', 'latin1', buf), b'abc\xe9')
        self.assertEqual(buf, bytearray(b'abc\xe9\x00xxx'))
        buf = bytearray(b'x'*5)
        self.assertEqual(getargs_et_hash('abc\xe9', 'latin1', buf), b'abc\xe9')
        self.assertEqual(buf, bytearray(b'abc\xe9\x00'))
        buf = bytearray(b'x'*4)
        self.assertRaises(ValueError, getargs_et_hash, 'abc\xe9', 'latin1', buf)
        self.assertEqual(buf, bytearray(b'x'*4))
        buf = bytearray()
        self.assertRaises(ValueError, getargs_et_hash, 'abc\xe9', 'latin1', buf)

    eleza test_u(self):
        kutoka _testcapi agiza getargs_u
        self.assertEqual(getargs_u('abc\xe9'), 'abc\xe9')
        self.assertRaises(ValueError, getargs_u, 'nul:\0')
        self.assertRaises(TypeError, getargs_u, b'bytes')
        self.assertRaises(TypeError, getargs_u, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_u, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_u, Tupu)

    eleza test_u_hash(self):
        kutoka _testcapi agiza getargs_u_hash
        self.assertEqual(getargs_u_hash('abc\xe9'), 'abc\xe9')
        self.assertEqual(getargs_u_hash('nul:\0'), 'nul:\0')
        self.assertRaises(TypeError, getargs_u_hash, b'bytes')
        self.assertRaises(TypeError, getargs_u_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_u_hash, memoryview(b'memoryview'))
        self.assertRaises(TypeError, getargs_u_hash, Tupu)

    eleza test_Z(self):
        kutoka _testcapi agiza getargs_Z
        self.assertEqual(getargs_Z('abc\xe9'), 'abc\xe9')
        self.assertRaises(ValueError, getargs_Z, 'nul:\0')
        self.assertRaises(TypeError, getargs_Z, b'bytes')
        self.assertRaises(TypeError, getargs_Z, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_Z, memoryview(b'memoryview'))
        self.assertIsTupu(getargs_Z(Tupu))

    eleza test_Z_hash(self):
        kutoka _testcapi agiza getargs_Z_hash
        self.assertEqual(getargs_Z_hash('abc\xe9'), 'abc\xe9')
        self.assertEqual(getargs_Z_hash('nul:\0'), 'nul:\0')
        self.assertRaises(TypeError, getargs_Z_hash, b'bytes')
        self.assertRaises(TypeError, getargs_Z_hash, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_Z_hash, memoryview(b'memoryview'))
        self.assertIsTupu(getargs_Z_hash(Tupu))


kundi Object_TestCase(unittest.TestCase):
    eleza test_S(self):
        kutoka _testcapi agiza getargs_S
        obj = b'bytes'
        self.assertIs(getargs_S(obj), obj)
        self.assertRaises(TypeError, getargs_S, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_S, 'str')
        self.assertRaises(TypeError, getargs_S, Tupu)
        self.assertRaises(TypeError, getargs_S, memoryview(obj))

    eleza test_Y(self):
        kutoka _testcapi agiza getargs_Y
        obj = bytearray(b'bytearray')
        self.assertIs(getargs_Y(obj), obj)
        self.assertRaises(TypeError, getargs_Y, b'bytes')
        self.assertRaises(TypeError, getargs_Y, 'str')
        self.assertRaises(TypeError, getargs_Y, Tupu)
        self.assertRaises(TypeError, getargs_Y, memoryview(obj))

    eleza test_U(self):
        kutoka _testcapi agiza getargs_U
        obj = 'str'
        self.assertIs(getargs_U(obj), obj)
        self.assertRaises(TypeError, getargs_U, b'bytes')
        self.assertRaises(TypeError, getargs_U, bytearray(b'bytearray'))
        self.assertRaises(TypeError, getargs_U, Tupu)


# Bug #6012
kundi Test6012(unittest.TestCase):
    eleza test(self):
        self.assertEqual(_testcapi.argparsing("Hello", "World"), 1)


kundi SkipitemTest(unittest.TestCase):

    eleza test_skipitem(self):
        """
        If this test failed, you probably added a new "format unit"
        kwenye Python/getargs.c, but neglected to update our poor friend
        skipitem() kwenye the same file.  (If so, shame on you!)

        With a few exceptions**, this function brute-force tests all
        printable ASCII*** characters (32 to 126 inclusive) kama format units,
        checking to see that PyArg_ParseTupleAndKeywords() rudisha consistent
        errors both when the unit ni attempted to be used na when it is
        skipped.  If the format unit doesn't exist, we'll get one of two
        specific error messages (one kila used, one kila skipped); ikiwa it does
        exist we *won't* get that error--we'll get either no error ama some
        other error.  If we get the specific "does sio exist" error kila one
        test na sio kila the other, there's a mismatch, na the test fails.

           ** Some format units have special funny semantics na it would
              be difficult to accommodate them here.  Since these are all
              well-established na properly skipped kwenye skipitem() we can
              get away with sio testing them--this test ni really intended
              to catch *new* format units.

          *** Python C source files must be ASCII.  Therefore it's impossible
              to have non-ASCII format units.

        """
        empty_tuple = ()
        tuple_1 = (0,)
        dict_b = {'b':1}
        keywords = ["a", "b"]

        kila i kwenye range(32, 127):
            c = chr(i)

            # skip parentheses, the error reporting ni inconsistent about them
            # skip 'e', it's always a two-character code
            # skip '|' na '$', they don't represent arguments anyway
            ikiwa c kwenye '()e|$':
                endelea

            # test the format unit when sio skipped
            format = c + "i"
            jaribu:
                _testcapi.parse_tuple_and_keywords(tuple_1, dict_b,
                    format, keywords)
                when_not_skipped = Uongo
            tatizo SystemError kama e:
                s = "argument 1 (impossible<bad format char>)"
                when_not_skipped = (str(e) == s)
            tatizo TypeError:
                when_not_skipped = Uongo

            # test the format unit when skipped
            optional_format = "|" + format
            jaribu:
                _testcapi.parse_tuple_and_keywords(empty_tuple, dict_b,
                    optional_format, keywords)
                when_skipped = Uongo
            tatizo SystemError kama e:
                s = "impossible<bad format char>: '{}'".format(format)
                when_skipped = (str(e) == s)

            message = ("test_skipitem_parity: "
                "detected mismatch between convertsimple na skipitem "
                "kila format unit '{}' ({}), sio skipped {}, skipped {}".format(
                    c, i, when_skipped, when_not_skipped))
            self.assertIs(when_skipped, when_not_skipped, message)

    eleza test_skipitem_with_suffix(self):
        parse = _testcapi.parse_tuple_and_keywords
        empty_tuple = ()
        tuple_1 = (0,)
        dict_b = {'b':1}
        keywords = ["a", "b"]

        supported = ('s#', 's*', 'z#', 'z*', 'u#', 'Z#', 'y#', 'y*', 'w#', 'w*')
        kila c kwenye string.ascii_letters:
            kila c2 kwenye '#*':
                f = c + c2
                with self.subTest(format=f):
                    optional_format = "|" + f + "i"
                    ikiwa f kwenye supported:
                        parse(empty_tuple, dict_b, optional_format, keywords)
                    isipokua:
                        with self.assertRaisesRegex(SystemError,
                                    'impossible<bad format char>'):
                            parse(empty_tuple, dict_b, optional_format, keywords)

        kila c kwenye map(chr, range(32, 128)):
            f = 'e' + c
            optional_format = "|" + f + "i"
            with self.subTest(format=f):
                ikiwa c kwenye 'st':
                    parse(empty_tuple, dict_b, optional_format, keywords)
                isipokua:
                    with self.assertRaisesRegex(SystemError,
                                'impossible<bad format char>'):
                        parse(empty_tuple, dict_b, optional_format, keywords)


kundi ParseTupleAndKeywords_Test(unittest.TestCase):

    eleza test_parse_tuple_and_keywords(self):
        # Test handling errors kwenye the parse_tuple_and_keywords helper itself
        self.assertRaises(TypeError, _testcapi.parse_tuple_and_keywords,
                          (), {}, 42, [])
        self.assertRaises(ValueError, _testcapi.parse_tuple_and_keywords,
                          (), {}, '', 42)
        self.assertRaises(ValueError, _testcapi.parse_tuple_and_keywords,
                          (), {}, '', [''] * 42)
        self.assertRaises(ValueError, _testcapi.parse_tuple_and_keywords,
                          (), {}, '', [42])

    eleza test_bad_use(self):
        # Test handling invalid format na keywords in
        # PyArg_ParseTupleAndKeywords()
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (1,), {}, '||O', ['a'])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (1, 2), {}, '|O|O', ['a', 'b'])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (), {'a': 1}, '$$O', ['a'])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (), {'a': 1, 'b': 2}, '$O$O', ['a', 'b'])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (), {'a': 1}, '$|O', ['a'])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (), {'a': 1, 'b': 2}, '$O|O', ['a', 'b'])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (1,), {}, '|O', ['a', 'b'])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (1,), {}, '|OO', ['a'])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (), {}, '|$O', [''])
        self.assertRaises(SystemError, _testcapi.parse_tuple_and_keywords,
                          (), {}, '|OO', ['a', ''])

    eleza test_positional_only(self):
        parse = _testcapi.parse_tuple_and_keywords

        parse((1, 2, 3), {}, 'OOO', ['', '', 'a'])
        parse((1, 2), {'a': 3}, 'OOO', ['', '', 'a'])
        with self.assertRaisesRegex(TypeError,
               r'function takes at least 2 positional arguments \(1 given\)'):
            parse((1,), {'a': 3}, 'OOO', ['', '', 'a'])
        parse((1,), {}, 'O|OO', ['', '', 'a'])
        with self.assertRaisesRegex(TypeError,
               r'function takes at least 1 positional argument \(0 given\)'):
            parse((), {}, 'O|OO', ['', '', 'a'])
        parse((1, 2), {'a': 3}, 'OO$O', ['', '', 'a'])
        with self.assertRaisesRegex(TypeError,
               r'function takes exactly 2 positional arguments \(1 given\)'):
            parse((1,), {'a': 3}, 'OO$O', ['', '', 'a'])
        parse((1,), {}, 'O|O$O', ['', '', 'a'])
        with self.assertRaisesRegex(TypeError,
               r'function takes at least 1 positional argument \(0 given\)'):
            parse((), {}, 'O|O$O', ['', '', 'a'])
        with self.assertRaisesRegex(SystemError, r'Empty parameter name after \$'):
            parse((1,), {}, 'O|$OO', ['', '', 'a'])
        with self.assertRaisesRegex(SystemError, 'Empty keyword'):
            parse((1,), {}, 'O|OO', ['', 'a', ''])


kundi Test_testcapi(unittest.TestCase):
    locals().update((name, getattr(_testcapi, name))
                    kila name kwenye dir(_testcapi)
                    ikiwa name.startswith('test_') na name.endswith('_code'))


ikiwa __name__ == "__main__":
    unittest.main()
