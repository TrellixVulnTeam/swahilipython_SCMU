agiza fractions
agiza operator
agiza os
agiza random
agiza sys
agiza struct
agiza time
agiza unittest

kutoka test agiza support
kutoka test.test_grammar agiza (VALID_UNDERSCORE_LITERALS,
                               INVALID_UNDERSCORE_LITERALS)
kutoka math agiza isinf, isnan, copysign, ldexp

INF = float("inf")
NAN = float("nan")

have_getformat = hasattr(float, "__getformat__")
requires_getformat = unittest.skipUnless(have_getformat,
                                         "requires __getformat__")
requires_setformat = unittest.skipUnless(hasattr(float, "__setformat__"),
                                         "requires __setformat__")

#locate file ukijumuisha float format test values
test_dir = os.path.dirname(__file__) ama os.curdir
format_testfile = os.path.join(test_dir, 'formatfloat_testcases.txt')

kundi FloatSubclass(float):
    pita

kundi OtherFloatSubclass(float):
    pita

kundi GeneralFloatCases(unittest.TestCase):

    eleza test_float(self):
        self.assertEqual(float(3.14), 3.14)
        self.assertEqual(float(314), 314.0)
        self.assertEqual(float("  3.14  "), 3.14)
        self.assertRaises(ValueError, float, "  0x3.1  ")
        self.assertRaises(ValueError, float, "  -0x3.p-1  ")
        self.assertRaises(ValueError, float, "  +0x3.p-1  ")
        self.assertRaises(ValueError, float, "++3.14")
        self.assertRaises(ValueError, float, "+-3.14")
        self.assertRaises(ValueError, float, "-+3.14")
        self.assertRaises(ValueError, float, "--3.14")
        self.assertRaises(ValueError, float, ".nan")
        self.assertRaises(ValueError, float, "+.inf")
        self.assertRaises(ValueError, float, ".")
        self.assertRaises(ValueError, float, "-.")
        self.assertRaises(TypeError, float, {})
        self.assertRaisesRegex(TypeError, "not 'dict'", float, {})
        # Lone surrogate
        self.assertRaises(ValueError, float, '\uD8F0')
        # check that we don't accept alternate exponent markers
        self.assertRaises(ValueError, float, "-1.7d29")
        self.assertRaises(ValueError, float, "3D-14")
        self.assertEqual(float("  \u0663.\u0661\u0664  "), 3.14)
        self.assertEqual(float("\N{EM SPACE}3.14\N{EN SPACE}"), 3.14)
        # extra long strings should sio be a problem
        float(b'.' + b'1'*1000)
        float('.' + '1'*1000)
        # Invalid unicode string
        # See bpo-34087
        self.assertRaises(ValueError, float, '\u3053\u3093\u306b\u3061\u306f')

    eleza test_underscores(self):
        kila lit kwenye VALID_UNDERSCORE_LITERALS:
            ikiwa sio any(ch kwenye lit kila ch kwenye 'jJxXoObB'):
                self.assertEqual(float(lit), eval(lit))
                self.assertEqual(float(lit), float(lit.replace('_', '')))
        kila lit kwenye INVALID_UNDERSCORE_LITERALS:
            ikiwa lit kwenye ('0_7', '09_99'):  # octals are sio recognized here
                endelea
            ikiwa sio any(ch kwenye lit kila ch kwenye 'jJxXoObB'):
                self.assertRaises(ValueError, float, lit)
        # Additional test cases; nan na inf are never valid kama literals,
        # only kwenye the float() constructor, but we don't allow underscores
        # kwenye ama around them.
        self.assertRaises(ValueError, float, '_NaN')
        self.assertRaises(ValueError, float, 'Na_N')
        self.assertRaises(ValueError, float, 'IN_F')
        self.assertRaises(ValueError, float, '-_INF')
        self.assertRaises(ValueError, float, '-INF_')
        # Check that we handle bytes values correctly.
        self.assertRaises(ValueError, float, b'0_.\xff9')

    eleza test_non_numeric_input_types(self):
        # Test possible non-numeric types kila the argument x, including
        # subclasses of the explicitly documented accepted types.
        kundi CustomStr(str): pita
        kundi CustomBytes(bytes): pita
        kundi CustomByteArray(bytearray): pita

        factories = [
            bytes,
            bytearray,
            lambda b: CustomStr(b.decode()),
            CustomBytes,
            CustomByteArray,
            memoryview,
        ]
        jaribu:
            kutoka array agiza array
        tatizo ImportError:
            pita
        isipokua:
            factories.append(lambda b: array('B', b))

        kila f kwenye factories:
            x = f(b" 3.14  ")
            ukijumuisha self.subTest(type(x)):
                self.assertEqual(float(x), 3.14)
                ukijumuisha self.assertRaisesRegex(ValueError, "could sio convert"):
                    float(f(b'A' * 0x10))

    eleza test_float_memoryview(self):
        self.assertEqual(float(memoryview(b'12.3')[1:4]), 2.3)
        self.assertEqual(float(memoryview(b'12.3\x00')[1:4]), 2.3)
        self.assertEqual(float(memoryview(b'12.3 ')[1:4]), 2.3)
        self.assertEqual(float(memoryview(b'12.3A')[1:4]), 2.3)
        self.assertEqual(float(memoryview(b'12.34')[1:4]), 2.3)

    eleza test_error_message(self):
        eleza check(s):
            ukijumuisha self.assertRaises(ValueError, msg='float(%r)' % (s,)) kama cm:
                float(s)
            self.assertEqual(str(cm.exception),
                'could sio convert string to float: %r' % (s,))

        check('\xbd')
        check('123\xbd')
        check('  123 456  ')
        check(b'  123 456  ')

        # non-ascii digits (error came kutoka non-digit '!')
        check('\u0663\u0661\u0664!')
        # embedded NUL
        check('123\x00')
        check('123\x00 245')
        check('123\x00245')
        # byte string ukijumuisha embedded NUL
        check(b'123\x00')
        # non-UTF-8 byte string
        check(b'123\xa0')

    @support.run_with_locale('LC_NUMERIC', 'fr_FR', 'de_DE')
    eleza test_float_with_comma(self):
        # set locale to something that doesn't use '.' kila the decimal point
        # float must sio accept the locale specific decimal point but
        # it still has to accept the normal python syntax
        agiza locale
        ikiwa sio locale.localeconv()['decimal_point'] == ',':
            self.skipTest('decimal_point ni sio ","')

        self.assertEqual(float("  3.14  "), 3.14)
        self.assertEqual(float("+3.14  "), 3.14)
        self.assertEqual(float("-3.14  "), -3.14)
        self.assertEqual(float(".14  "), .14)
        self.assertEqual(float("3.  "), 3.0)
        self.assertEqual(float("3.e3  "), 3000.0)
        self.assertEqual(float("3.2e3  "), 3200.0)
        self.assertEqual(float("2.5e-1  "), 0.25)
        self.assertEqual(float("5e-1"), 0.5)
        self.assertRaises(ValueError, float, "  3,14  ")
        self.assertRaises(ValueError, float, "  +3,14  ")
        self.assertRaises(ValueError, float, "  -3,14  ")
        self.assertRaises(ValueError, float, "  0x3.1  ")
        self.assertRaises(ValueError, float, "  -0x3.p-1  ")
        self.assertRaises(ValueError, float, "  +0x3.p-1  ")
        self.assertEqual(float("  25.e-1  "), 2.5)
        self.assertAlmostEqual(float("  .25e-1  "), .025)

    eleza test_floatconversion(self):
        # Make sure that calls to __float__() work properly
        kundi Foo1(object):
            eleza __float__(self):
                rudisha 42.

        kundi Foo2(float):
            eleza __float__(self):
                rudisha 42.

        kundi Foo3(float):
            eleza __new__(cls, value=0.):
                rudisha float.__new__(cls, 2*value)

            eleza __float__(self):
                rudisha self

        kundi Foo4(float):
            eleza __float__(self):
                rudisha 42

        # Issue 5759: __float__ sio called on str subclasses (though it ni on
        # unicode subclasses).
        kundi FooStr(str):
            eleza __float__(self):
                rudisha float(str(self)) + 1

        self.assertEqual(float(Foo1()), 42.)
        self.assertEqual(float(Foo2()), 42.)
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertEqual(float(Foo3(21)), 42.)
        self.assertRaises(TypeError, float, Foo4(42))
        self.assertEqual(float(FooStr('8')), 9.)

        kundi Foo5:
            eleza __float__(self):
                rudisha ""
        self.assertRaises(TypeError, time.sleep, Foo5())

        # Issue #24731
        kundi F:
            eleza __float__(self):
                rudisha OtherFloatSubclass(42.)
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertEqual(float(F()), 42.)
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertIs(type(float(F())), float)
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertEqual(FloatSubclass(F()), 42.)
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertIs(type(FloatSubclass(F())), FloatSubclass)

        kundi MyIndex:
            eleza __init__(self, value):
                self.value = value
            eleza __index__(self):
                rudisha self.value

        self.assertEqual(float(MyIndex(42)), 42.0)
        self.assertRaises(OverflowError, float, MyIndex(2**2000))

        kundi MyInt:
            eleza __int__(self):
                rudisha 42

        self.assertRaises(TypeError, float, MyInt())

    eleza test_keyword_args(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'keyword argument'):
            float(x='3.14')

    eleza test_is_integer(self):
        self.assertUongo((1.1).is_integer())
        self.assertKweli((1.).is_integer())
        self.assertUongo(float("nan").is_integer())
        self.assertUongo(float("inf").is_integer())

    eleza test_floatasratio(self):
        kila f, ratio kwenye [
                (0.875, (7, 8)),
                (-0.875, (-7, 8)),
                (0.0, (0, 1)),
                (11.5, (23, 2)),
            ]:
            self.assertEqual(f.as_integer_ratio(), ratio)

        kila i kwenye range(10000):
            f = random.random()
            f *= 10 ** random.randint(-100, 100)
            n, d = f.as_integer_ratio()
            self.assertEqual(float(n).__truediv__(d), f)

        R = fractions.Fraction
        self.assertEqual(R(0, 1),
                         R(*float(0.0).as_integer_ratio()))
        self.assertEqual(R(5, 2),
                         R(*float(2.5).as_integer_ratio()))
        self.assertEqual(R(1, 2),
                         R(*float(0.5).as_integer_ratio()))
        self.assertEqual(R(4728779608739021, 2251799813685248),
                         R(*float(2.1).as_integer_ratio()))
        self.assertEqual(R(-4728779608739021, 2251799813685248),
                         R(*float(-2.1).as_integer_ratio()))
        self.assertEqual(R(-2100, 1),
                         R(*float(-2100.0).as_integer_ratio()))

        self.assertRaises(OverflowError, float('inf').as_integer_ratio)
        self.assertRaises(OverflowError, float('-inf').as_integer_ratio)
        self.assertRaises(ValueError, float('nan').as_integer_ratio)

    eleza test_float_containment(self):
        floats = (INF, -INF, 0.0, 1.0, NAN)
        kila f kwenye floats:
            self.assertIn(f, [f])
            self.assertIn(f, (f,))
            self.assertIn(f, {f})
            self.assertIn(f, {f: Tupu})
            self.assertEqual([f].count(f), 1, "[].count('%r') != 1" % f)
            self.assertIn(f, floats)

        kila f kwenye floats:
            # nonidentical containers, same type, same contents
            self.assertKweli([f] == [f], "[%r] != [%r]" % (f, f))
            self.assertKweli((f,) == (f,), "(%r,) != (%r,)" % (f, f))
            self.assertKweli({f} == {f}, "{%r} != {%r}" % (f, f))
            self.assertKweli({f : Tupu} == {f: Tupu}, "{%r : Tupu} != "
                                                   "{%r : Tupu}" % (f, f))

            # identical containers
            l, t, s, d = [f], (f,), {f}, {f: Tupu}
            self.assertKweli(l == l, "[%r] sio equal to itself" % f)
            self.assertKweli(t == t, "(%r,) sio equal to itself" % f)
            self.assertKweli(s == s, "{%r} sio equal to itself" % f)
            self.assertKweli(d == d, "{%r : Tupu} sio equal to itself" % f)

    eleza assertEqualAndEqualSign(self, a, b):
        # fail unless a == b na a na b have the same sign bit;
        # the only difference kutoka assertEqual ni that this test
        # distinguishes -0.0 na 0.0.
        self.assertEqual((a, copysign(1.0, a)), (b, copysign(1.0, b)))

    @support.requires_IEEE_754
    eleza test_float_mod(self):
        # Check behaviour of % operator kila IEEE 754 special cases.
        # In particular, check signs of zeros.
        mod = operator.mod

        self.assertEqualAndEqualSign(mod(-1.0, 1.0), 0.0)
        self.assertEqualAndEqualSign(mod(-1e-100, 1.0), 1.0)
        self.assertEqualAndEqualSign(mod(-0.0, 1.0), 0.0)
        self.assertEqualAndEqualSign(mod(0.0, 1.0), 0.0)
        self.assertEqualAndEqualSign(mod(1e-100, 1.0), 1e-100)
        self.assertEqualAndEqualSign(mod(1.0, 1.0), 0.0)

        self.assertEqualAndEqualSign(mod(-1.0, -1.0), -0.0)
        self.assertEqualAndEqualSign(mod(-1e-100, -1.0), -1e-100)
        self.assertEqualAndEqualSign(mod(-0.0, -1.0), -0.0)
        self.assertEqualAndEqualSign(mod(0.0, -1.0), -0.0)
        self.assertEqualAndEqualSign(mod(1e-100, -1.0), -1.0)
        self.assertEqualAndEqualSign(mod(1.0, -1.0), -0.0)

    @support.requires_IEEE_754
    eleza test_float_pow(self):
        # test builtin pow na ** operator kila IEEE 754 special cases.
        # Special cases taken kutoka section F.9.4.4 of the C99 specification

        kila pow_op kwenye pow, operator.pow:
            # x**NAN ni NAN kila any x tatizo 1
            self.assertKweli(isnan(pow_op(-INF, NAN)))
            self.assertKweli(isnan(pow_op(-2.0, NAN)))
            self.assertKweli(isnan(pow_op(-1.0, NAN)))
            self.assertKweli(isnan(pow_op(-0.5, NAN)))
            self.assertKweli(isnan(pow_op(-0.0, NAN)))
            self.assertKweli(isnan(pow_op(0.0, NAN)))
            self.assertKweli(isnan(pow_op(0.5, NAN)))
            self.assertKweli(isnan(pow_op(2.0, NAN)))
            self.assertKweli(isnan(pow_op(INF, NAN)))
            self.assertKweli(isnan(pow_op(NAN, NAN)))

            # NAN**y ni NAN kila any y tatizo +-0
            self.assertKweli(isnan(pow_op(NAN, -INF)))
            self.assertKweli(isnan(pow_op(NAN, -2.0)))
            self.assertKweli(isnan(pow_op(NAN, -1.0)))
            self.assertKweli(isnan(pow_op(NAN, -0.5)))
            self.assertKweli(isnan(pow_op(NAN, 0.5)))
            self.assertKweli(isnan(pow_op(NAN, 1.0)))
            self.assertKweli(isnan(pow_op(NAN, 2.0)))
            self.assertKweli(isnan(pow_op(NAN, INF)))

            # (+-0)**y raises ZeroDivisionError kila y a negative odd integer
            self.assertRaises(ZeroDivisionError, pow_op, -0.0, -1.0)
            self.assertRaises(ZeroDivisionError, pow_op, 0.0, -1.0)

            # (+-0)**y raises ZeroDivisionError kila y finite na negative
            # but sio an odd integer
            self.assertRaises(ZeroDivisionError, pow_op, -0.0, -2.0)
            self.assertRaises(ZeroDivisionError, pow_op, -0.0, -0.5)
            self.assertRaises(ZeroDivisionError, pow_op, 0.0, -2.0)
            self.assertRaises(ZeroDivisionError, pow_op, 0.0, -0.5)

            # (+-0)**y ni +-0 kila y a positive odd integer
            self.assertEqualAndEqualSign(pow_op(-0.0, 1.0), -0.0)
            self.assertEqualAndEqualSign(pow_op(0.0, 1.0), 0.0)

            # (+-0)**y ni 0 kila y finite na positive but sio an odd integer
            self.assertEqualAndEqualSign(pow_op(-0.0, 0.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(-0.0, 2.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.0, 0.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.0, 2.0), 0.0)

            # (-1)**+-inf ni 1
            self.assertEqualAndEqualSign(pow_op(-1.0, -INF), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, INF), 1.0)

            # 1**y ni 1 kila any y, even ikiwa y ni an infinity ama nan
            self.assertEqualAndEqualSign(pow_op(1.0, -INF), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -2.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -1.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -0.5), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 0.5), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 1.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 2.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, INF), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, NAN), 1.0)

            # x**+-0 ni 1 kila any x, even ikiwa x ni a zero, infinity, ama nan
            self.assertEqualAndEqualSign(pow_op(-INF, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-0.5, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-0.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(0.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(0.5, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(INF, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(NAN, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-INF, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-0.5, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-0.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(0.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(0.5, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(INF, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(NAN, -0.0), 1.0)

            # x**y defers to complex pow kila finite negative x na
            # non-integral y.
            self.assertEqual(type(pow_op(-2.0, -0.5)), complex)
            self.assertEqual(type(pow_op(-2.0, 0.5)), complex)
            self.assertEqual(type(pow_op(-1.0, -0.5)), complex)
            self.assertEqual(type(pow_op(-1.0, 0.5)), complex)
            self.assertEqual(type(pow_op(-0.5, -0.5)), complex)
            self.assertEqual(type(pow_op(-0.5, 0.5)), complex)

            # x**-INF ni INF kila abs(x) < 1
            self.assertEqualAndEqualSign(pow_op(-0.5, -INF), INF)
            self.assertEqualAndEqualSign(pow_op(-0.0, -INF), INF)
            self.assertEqualAndEqualSign(pow_op(0.0, -INF), INF)
            self.assertEqualAndEqualSign(pow_op(0.5, -INF), INF)

            # x**-INF ni 0 kila abs(x) > 1
            self.assertEqualAndEqualSign(pow_op(-INF, -INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, -INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(INF, -INF), 0.0)

            # x**INF ni 0 kila abs(x) < 1
            self.assertEqualAndEqualSign(pow_op(-0.5, INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(-0.0, INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.0, INF), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.5, INF), 0.0)

            # x**INF ni INF kila abs(x) > 1
            self.assertEqualAndEqualSign(pow_op(-INF, INF), INF)
            self.assertEqualAndEqualSign(pow_op(-2.0, INF), INF)
            self.assertEqualAndEqualSign(pow_op(2.0, INF), INF)
            self.assertEqualAndEqualSign(pow_op(INF, INF), INF)

            # (-INF)**y ni -0.0 kila y a negative odd integer
            self.assertEqualAndEqualSign(pow_op(-INF, -1.0), -0.0)

            # (-INF)**y ni 0.0 kila y negative but sio an odd integer
            self.assertEqualAndEqualSign(pow_op(-INF, -0.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(-INF, -2.0), 0.0)

            # (-INF)**y ni -INF kila y a positive odd integer
            self.assertEqualAndEqualSign(pow_op(-INF, 1.0), -INF)

            # (-INF)**y ni INF kila y positive but sio an odd integer
            self.assertEqualAndEqualSign(pow_op(-INF, 0.5), INF)
            self.assertEqualAndEqualSign(pow_op(-INF, 2.0), INF)

            # INF**y ni INF kila y positive
            self.assertEqualAndEqualSign(pow_op(INF, 0.5), INF)
            self.assertEqualAndEqualSign(pow_op(INF, 1.0), INF)
            self.assertEqualAndEqualSign(pow_op(INF, 2.0), INF)

            # INF**y ni 0.0 kila y negative
            self.assertEqualAndEqualSign(pow_op(INF, -2.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(INF, -1.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(INF, -0.5), 0.0)

            # basic checks sio covered by the special cases above
            self.assertEqualAndEqualSign(pow_op(-2.0, -2.0), 0.25)
            self.assertEqualAndEqualSign(pow_op(-2.0, -1.0), -0.5)
            self.assertEqualAndEqualSign(pow_op(-2.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, 1.0), -2.0)
            self.assertEqualAndEqualSign(pow_op(-2.0, 2.0), 4.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -2.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -1.0), -1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 1.0), -1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 2.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -2.0), 0.25)
            self.assertEqualAndEqualSign(pow_op(2.0, -1.0), 0.5)
            self.assertEqualAndEqualSign(pow_op(2.0, -0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, 0.0), 1.0)
            self.assertEqualAndEqualSign(pow_op(2.0, 1.0), 2.0)
            self.assertEqualAndEqualSign(pow_op(2.0, 2.0), 4.0)

            # 1 ** large na -1 ** large; some libms apparently
            # have problems ukijumuisha these
            self.assertEqualAndEqualSign(pow_op(1.0, -1e100), 1.0)
            self.assertEqualAndEqualSign(pow_op(1.0, 1e100), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, -1e100), 1.0)
            self.assertEqualAndEqualSign(pow_op(-1.0, 1e100), 1.0)

            # check sign kila results that underflow to 0
            self.assertEqualAndEqualSign(pow_op(-2.0, -2000.0), 0.0)
            self.assertEqual(type(pow_op(-2.0, -2000.5)), complex)
            self.assertEqualAndEqualSign(pow_op(-2.0, -2001.0), -0.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -2000.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -2000.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(2.0, -2001.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(-0.5, 2000.0), 0.0)
            self.assertEqual(type(pow_op(-0.5, 2000.5)), complex)
            self.assertEqualAndEqualSign(pow_op(-0.5, 2001.0), -0.0)
            self.assertEqualAndEqualSign(pow_op(0.5, 2000.0), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.5, 2000.5), 0.0)
            self.assertEqualAndEqualSign(pow_op(0.5, 2001.0), 0.0)

            # check we don't ashiria an exception kila subnormal results,
            # na validate signs.  Tests currently disabled, since
            # they fail on systems where a subnormal result kutoka pow
            # ni flushed to zero (e.g. Debian/ia64.)
            #self.assertKweli(0.0 < pow_op(0.5, 1048) < 1e-315)
            #self.assertKweli(0.0 < pow_op(-0.5, 1048) < 1e-315)
            #self.assertKweli(0.0 < pow_op(0.5, 1047) < 1e-315)
            #self.assertKweli(0.0 > pow_op(-0.5, 1047) > -1e-315)
            #self.assertKweli(0.0 < pow_op(2.0, -1048) < 1e-315)
            #self.assertKweli(0.0 < pow_op(-2.0, -1048) < 1e-315)
            #self.assertKweli(0.0 < pow_op(2.0, -1047) < 1e-315)
            #self.assertKweli(0.0 > pow_op(-2.0, -1047) > -1e-315)


@requires_setformat
kundi FormatFunctionsTestCase(unittest.TestCase):

    eleza setUp(self):
        self.save_formats = {'double':float.__getformat__('double'),
                             'float':float.__getformat__('float')}

    eleza tearDown(self):
        float.__setformat__('double', self.save_formats['double'])
        float.__setformat__('float', self.save_formats['float'])

    eleza test_getformat(self):
        self.assertIn(float.__getformat__('double'),
                      ['unknown', 'IEEE, big-endian', 'IEEE, little-endian'])
        self.assertIn(float.__getformat__('float'),
                      ['unknown', 'IEEE, big-endian', 'IEEE, little-endian'])
        self.assertRaises(ValueError, float.__getformat__, 'chicken')
        self.assertRaises(TypeError, float.__getformat__, 1)

    eleza test_setformat(self):
        kila t kwenye 'double', 'float':
            float.__setformat__(t, 'unknown')
            ikiwa self.save_formats[t] == 'IEEE, big-endian':
                self.assertRaises(ValueError, float.__setformat__,
                                  t, 'IEEE, little-endian')
            lasivyo self.save_formats[t] == 'IEEE, little-endian':
                self.assertRaises(ValueError, float.__setformat__,
                                  t, 'IEEE, big-endian')
            isipokua:
                self.assertRaises(ValueError, float.__setformat__,
                                  t, 'IEEE, big-endian')
                self.assertRaises(ValueError, float.__setformat__,
                                  t, 'IEEE, little-endian')
            self.assertRaises(ValueError, float.__setformat__,
                              t, 'chicken')
        self.assertRaises(ValueError, float.__setformat__,
                          'chicken', 'unknown')

BE_DOUBLE_INF = b'\x7f\xf0\x00\x00\x00\x00\x00\x00'
LE_DOUBLE_INF = bytes(reversed(BE_DOUBLE_INF))
BE_DOUBLE_NAN = b'\x7f\xf8\x00\x00\x00\x00\x00\x00'
LE_DOUBLE_NAN = bytes(reversed(BE_DOUBLE_NAN))

BE_FLOAT_INF = b'\x7f\x80\x00\x00'
LE_FLOAT_INF = bytes(reversed(BE_FLOAT_INF))
BE_FLOAT_NAN = b'\x7f\xc0\x00\x00'
LE_FLOAT_NAN = bytes(reversed(BE_FLOAT_NAN))

# on non-IEEE platforms, attempting to unpack a bit pattern
# representing an infinity ama a NaN should ashiria an exception.

@requires_setformat
kundi UnknownFormatTestCase(unittest.TestCase):
    eleza setUp(self):
        self.save_formats = {'double':float.__getformat__('double'),
                             'float':float.__getformat__('float')}
        float.__setformat__('double', 'unknown')
        float.__setformat__('float', 'unknown')

    eleza tearDown(self):
        float.__setformat__('double', self.save_formats['double'])
        float.__setformat__('float', self.save_formats['float'])

    eleza test_double_specials_dont_unpack(self):
        kila fmt, data kwenye [('>d', BE_DOUBLE_INF),
                          ('>d', BE_DOUBLE_NAN),
                          ('<d', LE_DOUBLE_INF),
                          ('<d', LE_DOUBLE_NAN)]:
            self.assertRaises(ValueError, struct.unpack, fmt, data)

    eleza test_float_specials_dont_unpack(self):
        kila fmt, data kwenye [('>f', BE_FLOAT_INF),
                          ('>f', BE_FLOAT_NAN),
                          ('<f', LE_FLOAT_INF),
                          ('<f', LE_FLOAT_NAN)]:
            self.assertRaises(ValueError, struct.unpack, fmt, data)


# on an IEEE platform, all we guarantee ni that bit patterns
# representing infinities ama NaNs do sio ashiria an exception; all isipokua
# ni accident (today).
# let's also try to guarantee that -0.0 na 0.0 don't get confused.

kundi IEEEFormatTestCase(unittest.TestCase):

    @support.requires_IEEE_754
    eleza test_double_specials_do_unpack(self):
        kila fmt, data kwenye [('>d', BE_DOUBLE_INF),
                          ('>d', BE_DOUBLE_NAN),
                          ('<d', LE_DOUBLE_INF),
                          ('<d', LE_DOUBLE_NAN)]:
            struct.unpack(fmt, data)

    @support.requires_IEEE_754
    eleza test_float_specials_do_unpack(self):
        kila fmt, data kwenye [('>f', BE_FLOAT_INF),
                          ('>f', BE_FLOAT_NAN),
                          ('<f', LE_FLOAT_INF),
                          ('<f', LE_FLOAT_NAN)]:
            struct.unpack(fmt, data)

    @support.requires_IEEE_754
    eleza test_serialized_float_rounding(self):
        kutoka _testcapi agiza FLT_MAX
        self.assertEqual(struct.pack("<f", 3.40282356e38), struct.pack("<f", FLT_MAX))
        self.assertEqual(struct.pack("<f", -3.40282356e38), struct.pack("<f", -FLT_MAX))

kundi FormatTestCase(unittest.TestCase):

    eleza test_format(self):
        # these should be rewritten to use both format(x, spec) na
        # x.__format__(spec)

        self.assertEqual(format(0.0, 'f'), '0.000000')

        # the default ni 'g', tatizo kila empty format spec
        self.assertEqual(format(0.0, ''), '0.0')
        self.assertEqual(format(0.01, ''), '0.01')
        self.assertEqual(format(0.01, 'g'), '0.01')

        # empty presentation type should format kwenye the same way kama str
        # (issue 5920)
        x = 100/7.
        self.assertEqual(format(x, ''), str(x))
        self.assertEqual(format(x, '-'), str(x))
        self.assertEqual(format(x, '>'), str(x))
        self.assertEqual(format(x, '2'), str(x))

        self.assertEqual(format(1.0, 'f'), '1.000000')

        self.assertEqual(format(-1.0, 'f'), '-1.000000')

        self.assertEqual(format( 1.0, ' f'), ' 1.000000')
        self.assertEqual(format(-1.0, ' f'), '-1.000000')
        self.assertEqual(format( 1.0, '+f'), '+1.000000')
        self.assertEqual(format(-1.0, '+f'), '-1.000000')

        # % formatting
        self.assertEqual(format(-1.0, '%'), '-100.000000%')

        # conversion to string should fail
        self.assertRaises(ValueError, format, 3.0, "s")

        # other format specifiers shouldn't work on floats,
        #  kwenye particular int specifiers
        kila format_spec kwenye ([chr(x) kila x kwenye range(ord('a'), ord('z')+1)] +
                            [chr(x) kila x kwenye range(ord('A'), ord('Z')+1)]):
            ikiwa sio format_spec kwenye 'eEfFgGn%':
                self.assertRaises(ValueError, format, 0.0, format_spec)
                self.assertRaises(ValueError, format, 1.0, format_spec)
                self.assertRaises(ValueError, format, -1.0, format_spec)
                self.assertRaises(ValueError, format, 1e100, format_spec)
                self.assertRaises(ValueError, format, -1e100, format_spec)
                self.assertRaises(ValueError, format, 1e-100, format_spec)
                self.assertRaises(ValueError, format, -1e-100, format_spec)

        # issue 3382
        self.assertEqual(format(NAN, 'f'), 'nan')
        self.assertEqual(format(NAN, 'F'), 'NAN')
        self.assertEqual(format(INF, 'f'), 'inf')
        self.assertEqual(format(INF, 'F'), 'INF')

    @support.requires_IEEE_754
    eleza test_format_testfile(self):
        ukijumuisha open(format_testfile) kama testfile:
            kila line kwenye testfile:
                ikiwa line.startswith('--'):
                    endelea
                line = line.strip()
                ikiwa sio line:
                    endelea

                lhs, rhs = map(str.strip, line.split('->'))
                fmt, arg = lhs.split()
                self.assertEqual(fmt % float(arg), rhs)
                self.assertEqual(fmt % -float(arg), '-' + rhs)

    eleza test_issue5864(self):
        self.assertEqual(format(123.456, '.4'), '123.5')
        self.assertEqual(format(1234.56, '.4'), '1.235e+03')
        self.assertEqual(format(12345.6, '.4'), '1.235e+04')

    eleza test_issue35560(self):
        self.assertEqual(format(123.0, '00'), '123.0')
        self.assertEqual(format(123.34, '00f'), '123.340000')
        self.assertEqual(format(123.34, '00e'), '1.233400e+02')
        self.assertEqual(format(123.34, '00g'), '123.34')
        self.assertEqual(format(123.34, '00.10f'), '123.3400000000')
        self.assertEqual(format(123.34, '00.10e'), '1.2334000000e+02')
        self.assertEqual(format(123.34, '00.10g'), '123.34')
        self.assertEqual(format(123.34, '01f'), '123.340000')

        self.assertEqual(format(-123.0, '00'), '-123.0')
        self.assertEqual(format(-123.34, '00f'), '-123.340000')
        self.assertEqual(format(-123.34, '00e'), '-1.233400e+02')
        self.assertEqual(format(-123.34, '00g'), '-123.34')
        self.assertEqual(format(-123.34, '00.10f'), '-123.3400000000')
        self.assertEqual(format(-123.34, '00.10f'), '-123.3400000000')
        self.assertEqual(format(-123.34, '00.10e'), '-1.2334000000e+02')
        self.assertEqual(format(-123.34, '00.10g'), '-123.34')

kundi ReprTestCase(unittest.TestCase):
    eleza test_repr(self):
        ukijumuisha open(os.path.join(os.path.split(__file__)[0],
                  'floating_points.txt')) kama floats_file:
            kila line kwenye floats_file:
                line = line.strip()
                ikiwa sio line ama line.startswith('#'):
                    endelea
                v = eval(line)
                self.assertEqual(v, eval(repr(v)))

    @unittest.skipUnless(getattr(sys, 'float_repr_style', '') == 'short',
                         "applies only when using short float repr style")
    eleza test_short_repr(self):
        # test short float repr introduced kwenye Python 3.1.  One aspect
        # of this repr ni that we get some degree of str -> float ->
        # str roundtripping.  In particular, kila any numeric string
        # containing 15 ama fewer significant digits, those exact same
        # digits (modulo trailing zeros) should appear kwenye the output.
        # No more repr(0.03) -> "0.029999999999999999"!

        test_strings = [
            # output always includes *either* a decimal point na at
            # least one digit after that point, ama an exponent.
            '0.0',
            '1.0',
            '0.01',
            '0.02',
            '0.03',
            '0.04',
            '0.05',
            '1.23456789',
            '10.0',
            '100.0',
            # values >= 1e16 get an exponent...
            '1000000000000000.0',
            '9999999999999990.0',
            '1e+16',
            '1e+17',
            # ... na so do values < 1e-4
            '0.001',
            '0.001001',
            '0.00010000000000001',
            '0.0001',
            '9.999999999999e-05',
            '1e-05',
            # values designed to provoke failure ikiwa the FPU rounding
            # precision isn't set correctly
            '8.72293771110361e+25',
            '7.47005307342313e+26',
            '2.86438000439698e+28',
            '8.89142905246179e+28',
            '3.08578087079232e+35',
            ]

        kila s kwenye test_strings:
            negs = '-'+s
            self.assertEqual(s, repr(float(s)))
            self.assertEqual(negs, repr(float(negs)))
            # Since Python 3.2, repr na str are identical
            self.assertEqual(repr(float(s)), str(float(s)))
            self.assertEqual(repr(float(negs)), str(float(negs)))

@support.requires_IEEE_754
kundi RoundTestCase(unittest.TestCase):

    eleza test_inf_nan(self):
        self.assertRaises(OverflowError, round, INF)
        self.assertRaises(OverflowError, round, -INF)
        self.assertRaises(ValueError, round, NAN)
        self.assertRaises(TypeError, round, INF, 0.0)
        self.assertRaises(TypeError, round, -INF, 1.0)
        self.assertRaises(TypeError, round, NAN, "ceci n'est pas un integer")
        self.assertRaises(TypeError, round, -0.0, 1j)

    eleza test_large_n(self):
        kila n kwenye [324, 325, 400, 2**31-1, 2**31, 2**32, 2**100]:
            self.assertEqual(round(123.456, n), 123.456)
            self.assertEqual(round(-123.456, n), -123.456)
            self.assertEqual(round(1e300, n), 1e300)
            self.assertEqual(round(1e-320, n), 1e-320)
        self.assertEqual(round(1e150, 300), 1e150)
        self.assertEqual(round(1e300, 307), 1e300)
        self.assertEqual(round(-3.1415, 308), -3.1415)
        self.assertEqual(round(1e150, 309), 1e150)
        self.assertEqual(round(1.4e-315, 315), 1e-315)

    eleza test_small_n(self):
        kila n kwenye [-308, -309, -400, 1-2**31, -2**31, -2**31-1, -2**100]:
            self.assertEqual(round(123.456, n), 0.0)
            self.assertEqual(round(-123.456, n), -0.0)
            self.assertEqual(round(1e300, n), 0.0)
            self.assertEqual(round(1e-320, n), 0.0)

    eleza test_overflow(self):
        self.assertRaises(OverflowError, round, 1.6e308, -308)
        self.assertRaises(OverflowError, round, -1.7e308, -308)

    @unittest.skipUnless(getattr(sys, 'float_repr_style', '') == 'short',
                         "applies only when using short float repr style")
    eleza test_previous_round_bugs(self):
        # particular cases that have occurred kwenye bug reports
        self.assertEqual(round(562949953421312.5, 1),
                          562949953421312.5)
        self.assertEqual(round(56294995342131.5, 3),
                         56294995342131.5)
        # round-half-even
        self.assertEqual(round(25.0, -1), 20.0)
        self.assertEqual(round(35.0, -1), 40.0)
        self.assertEqual(round(45.0, -1), 40.0)
        self.assertEqual(round(55.0, -1), 60.0)
        self.assertEqual(round(65.0, -1), 60.0)
        self.assertEqual(round(75.0, -1), 80.0)
        self.assertEqual(round(85.0, -1), 80.0)
        self.assertEqual(round(95.0, -1), 100.0)

    @unittest.skipUnless(getattr(sys, 'float_repr_style', '') == 'short',
                         "applies only when using short float repr style")
    eleza test_matches_float_format(self):
        # round should give the same results kama float formatting
        kila i kwenye range(500):
            x = i/1000.
            self.assertEqual(float(format(x, '.0f')), round(x, 0))
            self.assertEqual(float(format(x, '.1f')), round(x, 1))
            self.assertEqual(float(format(x, '.2f')), round(x, 2))
            self.assertEqual(float(format(x, '.3f')), round(x, 3))

        kila i kwenye range(5, 5000, 10):
            x = i/1000.
            self.assertEqual(float(format(x, '.0f')), round(x, 0))
            self.assertEqual(float(format(x, '.1f')), round(x, 1))
            self.assertEqual(float(format(x, '.2f')), round(x, 2))
            self.assertEqual(float(format(x, '.3f')), round(x, 3))

        kila i kwenye range(500):
            x = random.random()
            self.assertEqual(float(format(x, '.0f')), round(x, 0))
            self.assertEqual(float(format(x, '.1f')), round(x, 1))
            self.assertEqual(float(format(x, '.2f')), round(x, 2))
            self.assertEqual(float(format(x, '.3f')), round(x, 3))

    eleza test_format_specials(self):
        # Test formatting of nans na infs.

        eleza test(fmt, value, expected):
            # Test ukijumuisha both % na format().
            self.assertEqual(fmt % value, expected, fmt)
            fmt = fmt[1:] # strip off the %
            self.assertEqual(format(value, fmt), expected, fmt)

        kila fmt kwenye ['%e', '%f', '%g', '%.0e', '%.6f', '%.20g',
                    '%#e', '%#f', '%#g', '%#.20e', '%#.15f', '%#.3g']:
            pfmt = '%+' + fmt[1:]
            sfmt = '% ' + fmt[1:]
            test(fmt, INF, 'inf')
            test(fmt, -INF, '-inf')
            test(fmt, NAN, 'nan')
            test(fmt, -NAN, 'nan')
            # When asking kila a sign, it's always provided. nans are
            #  always positive.
            test(pfmt, INF, '+inf')
            test(pfmt, -INF, '-inf')
            test(pfmt, NAN, '+nan')
            test(pfmt, -NAN, '+nan')
            # When using ' ' kila a sign code, only infs can be negative.
            #  Others have a space.
            test(sfmt, INF, ' inf')
            test(sfmt, -INF, '-inf')
            test(sfmt, NAN, ' nan')
            test(sfmt, -NAN, ' nan')

    eleza test_Tupu_ndigits(self):
        kila x kwenye round(1.23), round(1.23, Tupu), round(1.23, ndigits=Tupu):
            self.assertEqual(x, 1)
            self.assertIsInstance(x, int)
        kila x kwenye round(1.78), round(1.78, Tupu), round(1.78, ndigits=Tupu):
            self.assertEqual(x, 2)
            self.assertIsInstance(x, int)


# Beginning ukijumuisha Python 2.6 float has cross platform compatible
# ways to create na represent inf na nan
kundi InfNanTest(unittest.TestCase):
    eleza test_inf_from_str(self):
        self.assertKweli(isinf(float("inf")))
        self.assertKweli(isinf(float("+inf")))
        self.assertKweli(isinf(float("-inf")))
        self.assertKweli(isinf(float("infinity")))
        self.assertKweli(isinf(float("+infinity")))
        self.assertKweli(isinf(float("-infinity")))

        self.assertEqual(repr(float("inf")), "inf")
        self.assertEqual(repr(float("+inf")), "inf")
        self.assertEqual(repr(float("-inf")), "-inf")
        self.assertEqual(repr(float("infinity")), "inf")
        self.assertEqual(repr(float("+infinity")), "inf")
        self.assertEqual(repr(float("-infinity")), "-inf")

        self.assertEqual(repr(float("INF")), "inf")
        self.assertEqual(repr(float("+Inf")), "inf")
        self.assertEqual(repr(float("-iNF")), "-inf")
        self.assertEqual(repr(float("Infinity")), "inf")
        self.assertEqual(repr(float("+iNfInItY")), "inf")
        self.assertEqual(repr(float("-INFINITY")), "-inf")

        self.assertEqual(str(float("inf")), "inf")
        self.assertEqual(str(float("+inf")), "inf")
        self.assertEqual(str(float("-inf")), "-inf")
        self.assertEqual(str(float("infinity")), "inf")
        self.assertEqual(str(float("+infinity")), "inf")
        self.assertEqual(str(float("-infinity")), "-inf")

        self.assertRaises(ValueError, float, "info")
        self.assertRaises(ValueError, float, "+info")
        self.assertRaises(ValueError, float, "-info")
        self.assertRaises(ValueError, float, "in")
        self.assertRaises(ValueError, float, "+in")
        self.assertRaises(ValueError, float, "-in")
        self.assertRaises(ValueError, float, "infinit")
        self.assertRaises(ValueError, float, "+Infin")
        self.assertRaises(ValueError, float, "-INFI")
        self.assertRaises(ValueError, float, "infinitys")

        self.assertRaises(ValueError, float, "++Inf")
        self.assertRaises(ValueError, float, "-+inf")
        self.assertRaises(ValueError, float, "+-infinity")
        self.assertRaises(ValueError, float, "--Infinity")

    eleza test_inf_as_str(self):
        self.assertEqual(repr(1e300 * 1e300), "inf")
        self.assertEqual(repr(-1e300 * 1e300), "-inf")

        self.assertEqual(str(1e300 * 1e300), "inf")
        self.assertEqual(str(-1e300 * 1e300), "-inf")

    eleza test_nan_from_str(self):
        self.assertKweli(isnan(float("nan")))
        self.assertKweli(isnan(float("+nan")))
        self.assertKweli(isnan(float("-nan")))

        self.assertEqual(repr(float("nan")), "nan")
        self.assertEqual(repr(float("+nan")), "nan")
        self.assertEqual(repr(float("-nan")), "nan")

        self.assertEqual(repr(float("NAN")), "nan")
        self.assertEqual(repr(float("+NAn")), "nan")
        self.assertEqual(repr(float("-NaN")), "nan")

        self.assertEqual(str(float("nan")), "nan")
        self.assertEqual(str(float("+nan")), "nan")
        self.assertEqual(str(float("-nan")), "nan")

        self.assertRaises(ValueError, float, "nana")
        self.assertRaises(ValueError, float, "+nana")
        self.assertRaises(ValueError, float, "-nana")
        self.assertRaises(ValueError, float, "na")
        self.assertRaises(ValueError, float, "+na")
        self.assertRaises(ValueError, float, "-na")

        self.assertRaises(ValueError, float, "++nan")
        self.assertRaises(ValueError, float, "-+NAN")
        self.assertRaises(ValueError, float, "+-NaN")
        self.assertRaises(ValueError, float, "--nAn")

    eleza test_nan_as_str(self):
        self.assertEqual(repr(1e300 * 1e300 * 0), "nan")
        self.assertEqual(repr(-1e300 * 1e300 * 0), "nan")

        self.assertEqual(str(1e300 * 1e300 * 0), "nan")
        self.assertEqual(str(-1e300 * 1e300 * 0), "nan")

    eleza test_inf_signs(self):
        self.assertEqual(copysign(1.0, float('inf')), 1.0)
        self.assertEqual(copysign(1.0, float('-inf')), -1.0)

    @unittest.skipUnless(getattr(sys, 'float_repr_style', '') == 'short',
                         "applies only when using short float repr style")
    eleza test_nan_signs(self):
        # When using the dtoa.c code, the sign of float('nan') should
        # be predictable.
        self.assertEqual(copysign(1.0, float('nan')), 1.0)
        self.assertEqual(copysign(1.0, float('-nan')), -1.0)


fromHex = float.fromhex
toHex = float.hex
kundi HexFloatTestCase(unittest.TestCase):
    MAX = fromHex('0x.fffffffffffff8p+1024')  # max normal
    MIN = fromHex('0x1p-1022')                # min normal
    TINY = fromHex('0x0.0000000000001p-1022') # min subnormal
    EPS = fromHex('0x0.0000000000001p0') # diff between 1.0 na next float up

    eleza identical(self, x, y):
        # check that floats x na y are identical, ama that both
        # are NaNs
        ikiwa isnan(x) ama isnan(y):
            ikiwa isnan(x) == isnan(y):
                return
        lasivyo x == y na (x != 0.0 ama copysign(1.0, x) == copysign(1.0, y)):
            return
        self.fail('%r sio identical to %r' % (x, y))

    eleza test_ends(self):
        self.identical(self.MIN, ldexp(1.0, -1022))
        self.identical(self.TINY, ldexp(1.0, -1074))
        self.identical(self.EPS, ldexp(1.0, -52))
        self.identical(self.MAX, 2.*(ldexp(1.0, 1023) - ldexp(1.0, 970)))

    eleza test_invalid_inputs(self):
        invalid_inputs = [
            'infi',   # misspelt infinities na nans
            '-Infinit',
            '++inf',
            '-+Inf',
            '--nan',
            '+-NaN',
            'snan',
            'NaNs',
            'nna',
            'an',
            'nf',
            'nfinity',
            'inity',
            'iinity',
            '0xnan',
            '',
            ' ',
            'x1.0p0',
            '0xX1.0p0',
            '+ 0x1.0p0', # internal whitespace
            '- 0x1.0p0',
            '0 x1.0p0',
            '0x 1.0p0',
            '0x1 2.0p0',
            '+0x1 .0p0',
            '0x1. 0p0',
            '-0x1.0 1p0',
            '-0x1.0 p0',
            '+0x1.0p +0',
            '0x1.0p -0',
            '0x1.0p 0',
            '+0x1.0p+ 0',
            '-0x1.0p- 0',
            '++0x1.0p-0', # double signs
            '--0x1.0p0',
            '+-0x1.0p+0',
            '-+0x1.0p0',
            '0x1.0p++0',
            '+0x1.0p+-0',
            '-0x1.0p-+0',
            '0x1.0p--0',
            '0x1.0.p0',
            '0x.p0', # no hex digits before ama after point
            '0x1,p0', # wrong decimal point character
            '0x1pa',
            '0x1p\uff10',  # fullwidth Unicode digits
            '\uff10x1p0',
            '0x\uff11p0',
            '0x1.\uff10p0',
            '0x1p0 \n 0x2p0',
            '0x1p0\0 0x1p0',  # embedded null byte ni sio end of string
            ]
        kila x kwenye invalid_inputs:
            jaribu:
                result = fromHex(x)
            tatizo ValueError:
                pita
            isipokua:
                self.fail('Expected float.fromhex(%r) to ashiria ValueError; '
                          'got %r instead' % (x, result))


    eleza test_whitespace(self):
        value_pairs = [
            ('inf', INF),
            ('-Infinity', -INF),
            ('nan', NAN),
            ('1.0', 1.0),
            ('-0x.2', -0.125),
            ('-0.0', -0.0)
            ]
        whitespace = [
            '',
            ' ',
            '\t',
            '\n',
            '\n \t',
            '\f',
            '\v',
            '\r'
            ]
        kila inp, expected kwenye value_pairs:
            kila lead kwenye whitespace:
                kila trail kwenye whitespace:
                    got = fromHex(lead + inp + trail)
                    self.identical(got, expected)


    eleza test_from_hex(self):
        MIN = self.MIN;
        MAX = self.MAX;
        TINY = self.TINY;
        EPS = self.EPS;

        # two spellings of infinity, ukijumuisha optional signs; case-insensitive
        self.identical(fromHex('inf'), INF)
        self.identical(fromHex('+Inf'), INF)
        self.identical(fromHex('-INF'), -INF)
        self.identical(fromHex('iNf'), INF)
        self.identical(fromHex('Infinity'), INF)
        self.identical(fromHex('+INFINITY'), INF)
        self.identical(fromHex('-infinity'), -INF)
        self.identical(fromHex('-iNFiNitY'), -INF)

        # nans ukijumuisha optional sign; case insensitive
        self.identical(fromHex('nan'), NAN)
        self.identical(fromHex('+NaN'), NAN)
        self.identical(fromHex('-NaN'), NAN)
        self.identical(fromHex('-nAN'), NAN)

        # variations kwenye input format
        self.identical(fromHex('1'), 1.0)
        self.identical(fromHex('+1'), 1.0)
        self.identical(fromHex('1.'), 1.0)
        self.identical(fromHex('1.0'), 1.0)
        self.identical(fromHex('1.0p0'), 1.0)
        self.identical(fromHex('01'), 1.0)
        self.identical(fromHex('01.'), 1.0)
        self.identical(fromHex('0x1'), 1.0)
        self.identical(fromHex('0x1.'), 1.0)
        self.identical(fromHex('0x1.0'), 1.0)
        self.identical(fromHex('+0x1.0'), 1.0)
        self.identical(fromHex('0x1p0'), 1.0)
        self.identical(fromHex('0X1p0'), 1.0)
        self.identical(fromHex('0X1P0'), 1.0)
        self.identical(fromHex('0x1P0'), 1.0)
        self.identical(fromHex('0x1.p0'), 1.0)
        self.identical(fromHex('0x1.0p0'), 1.0)
        self.identical(fromHex('0x.1p4'), 1.0)
        self.identical(fromHex('0x.1p04'), 1.0)
        self.identical(fromHex('0x.1p004'), 1.0)
        self.identical(fromHex('0x1p+0'), 1.0)
        self.identical(fromHex('0x1P-0'), 1.0)
        self.identical(fromHex('+0x1p0'), 1.0)
        self.identical(fromHex('0x01p0'), 1.0)
        self.identical(fromHex('0x1p00'), 1.0)
        self.identical(fromHex(' 0x1p0 '), 1.0)
        self.identical(fromHex('\n 0x1p0'), 1.0)
        self.identical(fromHex('0x1p0 \t'), 1.0)
        self.identical(fromHex('0xap0'), 10.0)
        self.identical(fromHex('0xAp0'), 10.0)
        self.identical(fromHex('0xaP0'), 10.0)
        self.identical(fromHex('0xAP0'), 10.0)
        self.identical(fromHex('0xbep0'), 190.0)
        self.identical(fromHex('0xBep0'), 190.0)
        self.identical(fromHex('0xbEp0'), 190.0)
        self.identical(fromHex('0XBE0P-4'), 190.0)
        self.identical(fromHex('0xBEp0'), 190.0)
        self.identical(fromHex('0xB.Ep4'), 190.0)
        self.identical(fromHex('0x.BEp8'), 190.0)
        self.identical(fromHex('0x.0BEp12'), 190.0)

        # moving the point around
        pi = fromHex('0x1.921fb54442d18p1')
        self.identical(fromHex('0x.006487ed5110b46p11'), pi)
        self.identical(fromHex('0x.00c90fdaa22168cp10'), pi)
        self.identical(fromHex('0x.01921fb54442d18p9'), pi)
        self.identical(fromHex('0x.03243f6a8885a3p8'), pi)
        self.identical(fromHex('0x.06487ed5110b46p7'), pi)
        self.identical(fromHex('0x.0c90fdaa22168cp6'), pi)
        self.identical(fromHex('0x.1921fb54442d18p5'), pi)
        self.identical(fromHex('0x.3243f6a8885a3p4'), pi)
        self.identical(fromHex('0x.6487ed5110b46p3'), pi)
        self.identical(fromHex('0x.c90fdaa22168cp2'), pi)
        self.identical(fromHex('0x1.921fb54442d18p1'), pi)
        self.identical(fromHex('0x3.243f6a8885a3p0'), pi)
        self.identical(fromHex('0x6.487ed5110b46p-1'), pi)
        self.identical(fromHex('0xc.90fdaa22168cp-2'), pi)
        self.identical(fromHex('0x19.21fb54442d18p-3'), pi)
        self.identical(fromHex('0x32.43f6a8885a3p-4'), pi)
        self.identical(fromHex('0x64.87ed5110b46p-5'), pi)
        self.identical(fromHex('0xc9.0fdaa22168cp-6'), pi)
        self.identical(fromHex('0x192.1fb54442d18p-7'), pi)
        self.identical(fromHex('0x324.3f6a8885a3p-8'), pi)
        self.identical(fromHex('0x648.7ed5110b46p-9'), pi)
        self.identical(fromHex('0xc90.fdaa22168cp-10'), pi)
        self.identical(fromHex('0x1921.fb54442d18p-11'), pi)
        # ...
        self.identical(fromHex('0x1921fb54442d1.8p-47'), pi)
        self.identical(fromHex('0x3243f6a8885a3p-48'), pi)
        self.identical(fromHex('0x6487ed5110b46p-49'), pi)
        self.identical(fromHex('0xc90fdaa22168cp-50'), pi)
        self.identical(fromHex('0x1921fb54442d18p-51'), pi)
        self.identical(fromHex('0x3243f6a8885a30p-52'), pi)
        self.identical(fromHex('0x6487ed5110b460p-53'), pi)
        self.identical(fromHex('0xc90fdaa22168c0p-54'), pi)
        self.identical(fromHex('0x1921fb54442d180p-55'), pi)


        # results that should overflow...
        self.assertRaises(OverflowError, fromHex, '-0x1p1024')
        self.assertRaises(OverflowError, fromHex, '0x1p+1025')
        self.assertRaises(OverflowError, fromHex, '+0X1p1030')
        self.assertRaises(OverflowError, fromHex, '-0x1p+1100')
        self.assertRaises(OverflowError, fromHex, '0X1p123456789123456789')
        self.assertRaises(OverflowError, fromHex, '+0X.8p+1025')
        self.assertRaises(OverflowError, fromHex, '+0x0.8p1025')
        self.assertRaises(OverflowError, fromHex, '-0x0.4p1026')
        self.assertRaises(OverflowError, fromHex, '0X2p+1023')
        self.assertRaises(OverflowError, fromHex, '0x2.p1023')
        self.assertRaises(OverflowError, fromHex, '-0x2.0p+1023')
        self.assertRaises(OverflowError, fromHex, '+0X4p+1022')
        self.assertRaises(OverflowError, fromHex, '0x1.ffffffffffffffp+1023')
        self.assertRaises(OverflowError, fromHex, '-0X1.fffffffffffff9p1023')
        self.assertRaises(OverflowError, fromHex, '0X1.fffffffffffff8p1023')
        self.assertRaises(OverflowError, fromHex, '+0x3.fffffffffffffp1022')
        self.assertRaises(OverflowError, fromHex, '0x3fffffffffffffp+970')
        self.assertRaises(OverflowError, fromHex, '0x10000000000000000p960')
        self.assertRaises(OverflowError, fromHex, '-0Xffffffffffffffffp960')

        # ...and those that round to +-max float
        self.identical(fromHex('+0x1.fffffffffffffp+1023'), MAX)
        self.identical(fromHex('-0X1.fffffffffffff7p1023'), -MAX)
        self.identical(fromHex('0X1.fffffffffffff7fffffffffffffp1023'), MAX)

        # zeros
        self.identical(fromHex('0x0p0'), 0.0)
        self.identical(fromHex('0x0p1000'), 0.0)
        self.identical(fromHex('-0x0p1023'), -0.0)
        self.identical(fromHex('0X0p1024'), 0.0)
        self.identical(fromHex('-0x0p1025'), -0.0)
        self.identical(fromHex('0X0p2000'), 0.0)
        self.identical(fromHex('0x0p123456789123456789'), 0.0)
        self.identical(fromHex('-0X0p-0'), -0.0)
        self.identical(fromHex('-0X0p-1000'), -0.0)
        self.identical(fromHex('0x0p-1023'), 0.0)
        self.identical(fromHex('-0X0p-1024'), -0.0)
        self.identical(fromHex('-0x0p-1025'), -0.0)
        self.identical(fromHex('-0x0p-1072'), -0.0)
        self.identical(fromHex('0X0p-1073'), 0.0)
        self.identical(fromHex('-0x0p-1074'), -0.0)
        self.identical(fromHex('0x0p-1075'), 0.0)
        self.identical(fromHex('0X0p-1076'), 0.0)
        self.identical(fromHex('-0X0p-2000'), -0.0)
        self.identical(fromHex('-0x0p-123456789123456789'), -0.0)

        # values that should underflow to 0
        self.identical(fromHex('0X1p-1075'), 0.0)
        self.identical(fromHex('-0X1p-1075'), -0.0)
        self.identical(fromHex('-0x1p-123456789123456789'), -0.0)
        self.identical(fromHex('0x1.00000000000000001p-1075'), TINY)
        self.identical(fromHex('-0x1.1p-1075'), -TINY)
        self.identical(fromHex('0x1.fffffffffffffffffp-1075'), TINY)

        # check round-half-even ni working correctly near 0 ...
        self.identical(fromHex('0x1p-1076'), 0.0)
        self.identical(fromHex('0X2p-1076'), 0.0)
        self.identical(fromHex('0X3p-1076'), TINY)
        self.identical(fromHex('0x4p-1076'), TINY)
        self.identical(fromHex('0X5p-1076'), TINY)
        self.identical(fromHex('0X6p-1076'), 2*TINY)
        self.identical(fromHex('0x7p-1076'), 2*TINY)
        self.identical(fromHex('0X8p-1076'), 2*TINY)
        self.identical(fromHex('0X9p-1076'), 2*TINY)
        self.identical(fromHex('0xap-1076'), 2*TINY)
        self.identical(fromHex('0Xbp-1076'), 3*TINY)
        self.identical(fromHex('0xcp-1076'), 3*TINY)
        self.identical(fromHex('0Xdp-1076'), 3*TINY)
        self.identical(fromHex('0Xep-1076'), 4*TINY)
        self.identical(fromHex('0xfp-1076'), 4*TINY)
        self.identical(fromHex('0x10p-1076'), 4*TINY)
        self.identical(fromHex('-0x1p-1076'), -0.0)
        self.identical(fromHex('-0X2p-1076'), -0.0)
        self.identical(fromHex('-0x3p-1076'), -TINY)
        self.identical(fromHex('-0X4p-1076'), -TINY)
        self.identical(fromHex('-0x5p-1076'), -TINY)
        self.identical(fromHex('-0x6p-1076'), -2*TINY)
        self.identical(fromHex('-0X7p-1076'), -2*TINY)
        self.identical(fromHex('-0X8p-1076'), -2*TINY)
        self.identical(fromHex('-0X9p-1076'), -2*TINY)
        self.identical(fromHex('-0Xap-1076'), -2*TINY)
        self.identical(fromHex('-0xbp-1076'), -3*TINY)
        self.identical(fromHex('-0xcp-1076'), -3*TINY)
        self.identical(fromHex('-0Xdp-1076'), -3*TINY)
        self.identical(fromHex('-0xep-1076'), -4*TINY)
        self.identical(fromHex('-0Xfp-1076'), -4*TINY)
        self.identical(fromHex('-0X10p-1076'), -4*TINY)

        # ... na near MIN ...
        self.identical(fromHex('0x0.ffffffffffffd6p-1022'), MIN-3*TINY)
        self.identical(fromHex('0x0.ffffffffffffd8p-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffdap-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffdcp-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffdep-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffe0p-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffe2p-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffe4p-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffe6p-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffe8p-1022'), MIN-2*TINY)
        self.identical(fromHex('0x0.ffffffffffffeap-1022'), MIN-TINY)
        self.identical(fromHex('0x0.ffffffffffffecp-1022'), MIN-TINY)
        self.identical(fromHex('0x0.ffffffffffffeep-1022'), MIN-TINY)
        self.identical(fromHex('0x0.fffffffffffff0p-1022'), MIN-TINY)
        self.identical(fromHex('0x0.fffffffffffff2p-1022'), MIN-TINY)
        self.identical(fromHex('0x0.fffffffffffff4p-1022'), MIN-TINY)
        self.identical(fromHex('0x0.fffffffffffff6p-1022'), MIN-TINY)
        self.identical(fromHex('0x0.fffffffffffff8p-1022'), MIN)
        self.identical(fromHex('0x0.fffffffffffffap-1022'), MIN)
        self.identical(fromHex('0x0.fffffffffffffcp-1022'), MIN)
        self.identical(fromHex('0x0.fffffffffffffep-1022'), MIN)
        self.identical(fromHex('0x1.00000000000000p-1022'), MIN)
        self.identical(fromHex('0x1.00000000000002p-1022'), MIN)
        self.identical(fromHex('0x1.00000000000004p-1022'), MIN)
        self.identical(fromHex('0x1.00000000000006p-1022'), MIN)
        self.identical(fromHex('0x1.00000000000008p-1022'), MIN)
        self.identical(fromHex('0x1.0000000000000ap-1022'), MIN+TINY)
        self.identical(fromHex('0x1.0000000000000cp-1022'), MIN+TINY)
        self.identical(fromHex('0x1.0000000000000ep-1022'), MIN+TINY)
        self.identical(fromHex('0x1.00000000000010p-1022'), MIN+TINY)
        self.identical(fromHex('0x1.00000000000012p-1022'), MIN+TINY)
        self.identical(fromHex('0x1.00000000000014p-1022'), MIN+TINY)
        self.identical(fromHex('0x1.00000000000016p-1022'), MIN+TINY)
        self.identical(fromHex('0x1.00000000000018p-1022'), MIN+2*TINY)

        # ... na near 1.0.
        self.identical(fromHex('0x0.fffffffffffff0p0'), 1.0-EPS)
        self.identical(fromHex('0x0.fffffffffffff1p0'), 1.0-EPS)
        self.identical(fromHex('0X0.fffffffffffff2p0'), 1.0-EPS)
        self.identical(fromHex('0x0.fffffffffffff3p0'), 1.0-EPS)
        self.identical(fromHex('0X0.fffffffffffff4p0'), 1.0-EPS)
        self.identical(fromHex('0X0.fffffffffffff5p0'), 1.0-EPS/2)
        self.identical(fromHex('0X0.fffffffffffff6p0'), 1.0-EPS/2)
        self.identical(fromHex('0x0.fffffffffffff7p0'), 1.0-EPS/2)
        self.identical(fromHex('0x0.fffffffffffff8p0'), 1.0-EPS/2)
        self.identical(fromHex('0X0.fffffffffffff9p0'), 1.0-EPS/2)
        self.identical(fromHex('0X0.fffffffffffffap0'), 1.0-EPS/2)
        self.identical(fromHex('0x0.fffffffffffffbp0'), 1.0-EPS/2)
        self.identical(fromHex('0X0.fffffffffffffcp0'), 1.0)
        self.identical(fromHex('0x0.fffffffffffffdp0'), 1.0)
        self.identical(fromHex('0X0.fffffffffffffep0'), 1.0)
        self.identical(fromHex('0x0.ffffffffffffffp0'), 1.0)
        self.identical(fromHex('0X1.00000000000000p0'), 1.0)
        self.identical(fromHex('0X1.00000000000001p0'), 1.0)
        self.identical(fromHex('0x1.00000000000002p0'), 1.0)
        self.identical(fromHex('0X1.00000000000003p0'), 1.0)
        self.identical(fromHex('0x1.00000000000004p0'), 1.0)
        self.identical(fromHex('0X1.00000000000005p0'), 1.0)
        self.identical(fromHex('0X1.00000000000006p0'), 1.0)
        self.identical(fromHex('0X1.00000000000007p0'), 1.0)
        self.identical(fromHex('0x1.00000000000007ffffffffffffffffffffp0'),
                       1.0)
        self.identical(fromHex('0x1.00000000000008p0'), 1.0)
        self.identical(fromHex('0x1.00000000000008000000000000000001p0'),
                       1+EPS)
        self.identical(fromHex('0X1.00000000000009p0'), 1.0+EPS)
        self.identical(fromHex('0x1.0000000000000ap0'), 1.0+EPS)
        self.identical(fromHex('0x1.0000000000000bp0'), 1.0+EPS)
        self.identical(fromHex('0X1.0000000000000cp0'), 1.0+EPS)
        self.identical(fromHex('0x1.0000000000000dp0'), 1.0+EPS)
        self.identical(fromHex('0x1.0000000000000ep0'), 1.0+EPS)
        self.identical(fromHex('0X1.0000000000000fp0'), 1.0+EPS)
        self.identical(fromHex('0x1.00000000000010p0'), 1.0+EPS)
        self.identical(fromHex('0X1.00000000000011p0'), 1.0+EPS)
        self.identical(fromHex('0x1.00000000000012p0'), 1.0+EPS)
        self.identical(fromHex('0X1.00000000000013p0'), 1.0+EPS)
        self.identical(fromHex('0X1.00000000000014p0'), 1.0+EPS)
        self.identical(fromHex('0x1.00000000000015p0'), 1.0+EPS)
        self.identical(fromHex('0x1.00000000000016p0'), 1.0+EPS)
        self.identical(fromHex('0X1.00000000000017p0'), 1.0+EPS)
        self.identical(fromHex('0x1.00000000000017ffffffffffffffffffffp0'),
                       1.0+EPS)
        self.identical(fromHex('0x1.00000000000018p0'), 1.0+2*EPS)
        self.identical(fromHex('0X1.00000000000018000000000000000001p0'),
                       1.0+2*EPS)
        self.identical(fromHex('0x1.00000000000019p0'), 1.0+2*EPS)
        self.identical(fromHex('0X1.0000000000001ap0'), 1.0+2*EPS)
        self.identical(fromHex('0X1.0000000000001bp0'), 1.0+2*EPS)
        self.identical(fromHex('0x1.0000000000001cp0'), 1.0+2*EPS)
        self.identical(fromHex('0x1.0000000000001dp0'), 1.0+2*EPS)
        self.identical(fromHex('0x1.0000000000001ep0'), 1.0+2*EPS)
        self.identical(fromHex('0X1.0000000000001fp0'), 1.0+2*EPS)
        self.identical(fromHex('0x1.00000000000020p0'), 1.0+2*EPS)

    eleza test_roundtrip(self):
        eleza roundtrip(x):
            rudisha fromHex(toHex(x))

        kila x kwenye [NAN, INF, self.MAX, self.MIN, self.MIN-self.TINY, self.TINY, 0.0]:
            self.identical(x, roundtrip(x))
            self.identical(-x, roundtrip(-x))

        # fromHex(toHex(x)) should exactly recover x, kila any non-NaN float x.
        agiza random
        kila i kwenye range(10000):
            e = random.randrange(-1200, 1200)
            m = random.random()
            s = random.choice([1.0, -1.0])
            jaribu:
                x = s*ldexp(m, e)
            tatizo OverflowError:
                pita
            isipokua:
                self.identical(x, fromHex(toHex(x)))

    eleza test_subclass(self):
        kundi F(float):
            eleza __new__(cls, value):
                rudisha float.__new__(cls, value + 1)

        f = F.fromhex((1.5).hex())
        self.assertIs(type(f), F)
        self.assertEqual(f, 2.5)

        kundi F2(float):
            eleza __init__(self, value):
                self.foo = 'bar'

        f = F2.fromhex((1.5).hex())
        self.assertIs(type(f), F2)
        self.assertEqual(f, 1.5)
        self.assertEqual(getattr(f, 'foo', 'none'), 'bar')


ikiwa __name__ == '__main__':
    unittest.main()
