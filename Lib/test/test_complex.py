agiza unittest
kutoka test agiza support
kutoka test.test_grammar agiza (VALID_UNDERSCORE_LITERALS,
                               INVALID_UNDERSCORE_LITERALS)

kutoka random agiza random
kutoka math agiza atan2, isnan, copysign
agiza operator

INF = float("inf")
NAN = float("nan")
# These tests ensure that complex math does the right thing

kundi ComplexTest(unittest.TestCase):

    eleza assertAlmostEqual(self, a, b):
        ikiwa isinstance(a, complex):
            ikiwa isinstance(b, complex):
                unittest.TestCase.assertAlmostEqual(self, a.real, b.real)
                unittest.TestCase.assertAlmostEqual(self, a.imag, b.imag)
            isipokua:
                unittest.TestCase.assertAlmostEqual(self, a.real, b)
                unittest.TestCase.assertAlmostEqual(self, a.imag, 0.)
        isipokua:
            ikiwa isinstance(b, complex):
                unittest.TestCase.assertAlmostEqual(self, a, b.real)
                unittest.TestCase.assertAlmostEqual(self, 0., b.imag)
            isipokua:
                unittest.TestCase.assertAlmostEqual(self, a, b)

    eleza assertCloseAbs(self, x, y, eps=1e-9):
        """Return true iff floats x na y "are close"."""
        # put the one ukijumuisha larger magnitude second
        ikiwa abs(x) > abs(y):
            x, y = y, x
        ikiwa y == 0:
            rudisha abs(x) < eps
        ikiwa x == 0:
            rudisha abs(y) < eps
        # check that relative difference < eps
        self.assertKweli(abs((x-y)/y) < eps)

    eleza assertFloatsAreIdentical(self, x, y):
        """assert that floats x na y are identical, kwenye the sense that:
        (1) both x na y are nans, ama
        (2) both x na y are infinities, ukijumuisha the same sign, ama
        (3) both x na y are zeros, ukijumuisha the same sign, ama
        (4) x na y are both finite na nonzero, na x == y

        """
        msg = 'floats {!r} na {!r} are sio identical'

        ikiwa isnan(x) ama isnan(y):
            ikiwa isnan(x) na isnan(y):
                return
        lasivyo x == y:
            ikiwa x != 0.0:
                return
            # both zero; check that signs match
            lasivyo copysign(1.0, x) == copysign(1.0, y):
                return
            isipokua:
                msg += ': zeros have different signs'
        self.fail(msg.format(x, y))

    eleza assertClose(self, x, y, eps=1e-9):
        """Return true iff complexes x na y "are close"."""
        self.assertCloseAbs(x.real, y.real, eps)
        self.assertCloseAbs(x.imag, y.imag, eps)

    eleza check_div(self, x, y):
        """Compute complex z=x*y, na check that z/x==y na z/y==x."""
        z = x * y
        ikiwa x != 0:
            q = z / x
            self.assertClose(q, y)
            q = z.__truediv__(x)
            self.assertClose(q, y)
        ikiwa y != 0:
            q = z / y
            self.assertClose(q, x)
            q = z.__truediv__(y)
            self.assertClose(q, x)

    eleza test_truediv(self):
        simple_real = [float(i) kila i kwenye range(-5, 6)]
        simple_complex = [complex(x, y) kila x kwenye simple_real kila y kwenye simple_real]
        kila x kwenye simple_complex:
            kila y kwenye simple_complex:
                self.check_div(x, y)

        # A naive complex division algorithm (such kama kwenye 2.0) ni very prone to
        # nonsense errors kila these (overflows na underflows).
        self.check_div(complex(1e200, 1e200), 1+0j)
        self.check_div(complex(1e-200, 1e-200), 1+0j)

        # Just kila fun.
        kila i kwenye range(100):
            self.check_div(complex(random(), random()),
                           complex(random(), random()))

        self.assertRaises(ZeroDivisionError, complex.__truediv__, 1+1j, 0+0j)
        self.assertRaises(OverflowError, pow, 1e200+1j, 1e200+1j)

        self.assertAlmostEqual(complex.__truediv__(2+0j, 1+1j), 1-1j)
        self.assertRaises(ZeroDivisionError, complex.__truediv__, 1+1j, 0+0j)

        kila denom_real, denom_imag kwenye [(0, NAN), (NAN, 0), (NAN, NAN)]:
            z = complex(0, 0) / complex(denom_real, denom_imag)
            self.assertKweli(isnan(z.real))
            self.assertKweli(isnan(z.imag))

    eleza test_floordiv(self):
        self.assertRaises(TypeError, complex.__floordiv__, 3+0j, 1.5+0j)
        self.assertRaises(TypeError, complex.__floordiv__, 3+0j, 0+0j)

    eleza test_richcompare(self):
        self.assertIs(complex.__eq__(1+1j, 1<<10000), Uongo)
        self.assertIs(complex.__lt__(1+1j, Tupu), NotImplemented)
        self.assertIs(complex.__eq__(1+1j, 1+1j), Kweli)
        self.assertIs(complex.__eq__(1+1j, 2+2j), Uongo)
        self.assertIs(complex.__ne__(1+1j, 1+1j), Uongo)
        self.assertIs(complex.__ne__(1+1j, 2+2j), Kweli)
        kila i kwenye range(1, 100):
            f = i / 100.0
            self.assertIs(complex.__eq__(f+0j, f), Kweli)
            self.assertIs(complex.__ne__(f+0j, f), Uongo)
            self.assertIs(complex.__eq__(complex(f, f), f), Uongo)
            self.assertIs(complex.__ne__(complex(f, f), f), Kweli)
        self.assertIs(complex.__lt__(1+1j, 2+2j), NotImplemented)
        self.assertIs(complex.__le__(1+1j, 2+2j), NotImplemented)
        self.assertIs(complex.__gt__(1+1j, 2+2j), NotImplemented)
        self.assertIs(complex.__ge__(1+1j, 2+2j), NotImplemented)
        self.assertRaises(TypeError, operator.lt, 1+1j, 2+2j)
        self.assertRaises(TypeError, operator.le, 1+1j, 2+2j)
        self.assertRaises(TypeError, operator.gt, 1+1j, 2+2j)
        self.assertRaises(TypeError, operator.ge, 1+1j, 2+2j)
        self.assertIs(operator.eq(1+1j, 1+1j), Kweli)
        self.assertIs(operator.eq(1+1j, 2+2j), Uongo)
        self.assertIs(operator.ne(1+1j, 1+1j), Uongo)
        self.assertIs(operator.ne(1+1j, 2+2j), Kweli)

    eleza test_richcompare_boundaries(self):
        eleza check(n, deltas, is_equal, imag = 0.0):
            kila delta kwenye deltas:
                i = n + delta
                z = complex(i, imag)
                self.assertIs(complex.__eq__(z, i), is_equal(delta))
                self.assertIs(complex.__ne__(z, i), sio is_equal(delta))
        # For IEEE-754 doubles the following should hold:
        #    x kwenye [2 ** (52 + i), 2 ** (53 + i + 1)] -> x mod 2 ** i == 0
        # where the interval ni representable, of course.
        kila i kwenye range(1, 10):
            pow = 52 + i
            mult = 2 ** i
            check(2 ** pow, range(1, 101), lambda delta: delta % mult == 0)
            check(2 ** pow, range(1, 101), lambda delta: Uongo, float(i))
        check(2 ** 53, range(-100, 0), lambda delta: Kweli)

    eleza test_mod(self):
        # % ni no longer supported on complex numbers
        self.assertRaises(TypeError, (1+1j).__mod__, 0+0j)
        self.assertRaises(TypeError, lambda: (3.33+4.43j) % 0)
        self.assertRaises(TypeError, (1+1j).__mod__, 4.3j)

    eleza test_divmod(self):
        self.assertRaises(TypeError, divmod, 1+1j, 1+0j)
        self.assertRaises(TypeError, divmod, 1+1j, 0+0j)

    eleza test_pow(self):
        self.assertAlmostEqual(pow(1+1j, 0+0j), 1.0)
        self.assertAlmostEqual(pow(0+0j, 2+0j), 0.0)
        self.assertRaises(ZeroDivisionError, pow, 0+0j, 1j)
        self.assertAlmostEqual(pow(1j, -1), 1/1j)
        self.assertAlmostEqual(pow(1j, 200), 1)
        self.assertRaises(ValueError, pow, 1+1j, 1+1j, 1+1j)

        a = 3.33+4.43j
        self.assertEqual(a ** 0j, 1)
        self.assertEqual(a ** 0.+0.j, 1)

        self.assertEqual(3j ** 0j, 1)
        self.assertEqual(3j ** 0, 1)

        jaribu:
            0j ** a
        tatizo ZeroDivisionError:
            pita
        isipokua:
            self.fail("should fail 0.0 to negative ama complex power")

        jaribu:
            0j ** (3-2j)
        tatizo ZeroDivisionError:
            pita
        isipokua:
            self.fail("should fail 0.0 to negative ama complex power")

        # The following ni used to exercise certain code paths
        self.assertEqual(a ** 105, a ** 105)
        self.assertEqual(a ** -105, a ** -105)
        self.assertEqual(a ** -30, a ** -30)

        self.assertEqual(0.0j ** 0, 1)

        b = 5.1+2.3j
        self.assertRaises(ValueError, pow, a, b, 0)

    eleza test_boolcontext(self):
        kila i kwenye range(100):
            self.assertKweli(complex(random() + 1e-6, random() + 1e-6))
        self.assertKweli(sio complex(0.0, 0.0))

    eleza test_conjugate(self):
        self.assertClose(complex(5.3, 9.8).conjugate(), 5.3-9.8j)

    eleza test_constructor(self):
        kundi OS:
            eleza __init__(self, value): self.value = value
            eleza __complex__(self): rudisha self.value
        kundi NS(object):
            eleza __init__(self, value): self.value = value
            eleza __complex__(self): rudisha self.value
        self.assertEqual(complex(OS(1+10j)), 1+10j)
        self.assertEqual(complex(NS(1+10j)), 1+10j)
        self.assertRaises(TypeError, complex, OS(Tupu))
        self.assertRaises(TypeError, complex, NS(Tupu))
        self.assertRaises(TypeError, complex, {})
        self.assertRaises(TypeError, complex, NS(1.5))
        self.assertRaises(TypeError, complex, NS(1))

        self.assertAlmostEqual(complex("1+10j"), 1+10j)
        self.assertAlmostEqual(complex(10), 10+0j)
        self.assertAlmostEqual(complex(10.0), 10+0j)
        self.assertAlmostEqual(complex(10), 10+0j)
        self.assertAlmostEqual(complex(10+0j), 10+0j)
        self.assertAlmostEqual(complex(1,10), 1+10j)
        self.assertAlmostEqual(complex(1,10), 1+10j)
        self.assertAlmostEqual(complex(1,10.0), 1+10j)
        self.assertAlmostEqual(complex(1,10), 1+10j)
        self.assertAlmostEqual(complex(1,10), 1+10j)
        self.assertAlmostEqual(complex(1,10.0), 1+10j)
        self.assertAlmostEqual(complex(1.0,10), 1+10j)
        self.assertAlmostEqual(complex(1.0,10), 1+10j)
        self.assertAlmostEqual(complex(1.0,10.0), 1+10j)
        self.assertAlmostEqual(complex(3.14+0j), 3.14+0j)
        self.assertAlmostEqual(complex(3.14), 3.14+0j)
        self.assertAlmostEqual(complex(314), 314.0+0j)
        self.assertAlmostEqual(complex(314), 314.0+0j)
        self.assertAlmostEqual(complex(3.14+0j, 0j), 3.14+0j)
        self.assertAlmostEqual(complex(3.14, 0.0), 3.14+0j)
        self.assertAlmostEqual(complex(314, 0), 314.0+0j)
        self.assertAlmostEqual(complex(314, 0), 314.0+0j)
        self.assertAlmostEqual(complex(0j, 3.14j), -3.14+0j)
        self.assertAlmostEqual(complex(0.0, 3.14j), -3.14+0j)
        self.assertAlmostEqual(complex(0j, 3.14), 3.14j)
        self.assertAlmostEqual(complex(0.0, 3.14), 3.14j)
        self.assertAlmostEqual(complex("1"), 1+0j)
        self.assertAlmostEqual(complex("1j"), 1j)
        self.assertAlmostEqual(complex(),  0)
        self.assertAlmostEqual(complex("-1"), -1)
        self.assertAlmostEqual(complex("+1"), +1)
        self.assertAlmostEqual(complex("(1+2j)"), 1+2j)
        self.assertAlmostEqual(complex("(1.3+2.2j)"), 1.3+2.2j)
        self.assertAlmostEqual(complex("3.14+1J"), 3.14+1j)
        self.assertAlmostEqual(complex(" ( +3.14-6J )"), 3.14-6j)
        self.assertAlmostEqual(complex(" ( +3.14-J )"), 3.14-1j)
        self.assertAlmostEqual(complex(" ( +3.14+j )"), 3.14+1j)
        self.assertAlmostEqual(complex("J"), 1j)
        self.assertAlmostEqual(complex("( j )"), 1j)
        self.assertAlmostEqual(complex("+J"), 1j)
        self.assertAlmostEqual(complex("( -j)"), -1j)
        self.assertAlmostEqual(complex('1e-500'), 0.0 + 0.0j)
        self.assertAlmostEqual(complex('-1e-500j'), 0.0 - 0.0j)
        self.assertAlmostEqual(complex('-1e-500+1e-500j'), -0.0 + 0.0j)

        kundi complex2(complex): pita
        self.assertAlmostEqual(complex(complex2(1+1j)), 1+1j)
        self.assertAlmostEqual(complex(real=17, imag=23), 17+23j)
        self.assertAlmostEqual(complex(real=17+23j), 17+23j)
        self.assertAlmostEqual(complex(real=17+23j, imag=23), 17+46j)
        self.assertAlmostEqual(complex(real=1+2j, imag=3+4j), -3+5j)

        # check that the sign of a zero kwenye the real ama imaginary part
        # ni preserved when constructing kutoka two floats.  (These checks
        # are harmless on systems without support kila signed zeros.)
        eleza split_zeros(x):
            """Function that produces different results kila 0. na -0."""
            rudisha atan2(x, -1.)

        self.assertEqual(split_zeros(complex(1., 0.).imag), split_zeros(0.))
        self.assertEqual(split_zeros(complex(1., -0.).imag), split_zeros(-0.))
        self.assertEqual(split_zeros(complex(0., 1.).real), split_zeros(0.))
        self.assertEqual(split_zeros(complex(-0., 1.).real), split_zeros(-0.))

        c = 3.14 + 1j
        self.assertKweli(complex(c) ni c)
        toa c

        self.assertRaises(TypeError, complex, "1", "1")
        self.assertRaises(TypeError, complex, 1, "1")

        # SF bug 543840:  complex(string) accepts strings ukijumuisha \0
        # Fixed kwenye 2.3.
        self.assertRaises(ValueError, complex, '1+1j\0j')

        self.assertRaises(TypeError, int, 5+3j)
        self.assertRaises(TypeError, int, 5+3j)
        self.assertRaises(TypeError, float, 5+3j)
        self.assertRaises(ValueError, complex, "")
        self.assertRaises(TypeError, complex, Tupu)
        self.assertRaisesRegex(TypeError, "not 'TupuType'", complex, Tupu)
        self.assertRaises(ValueError, complex, "\0")
        self.assertRaises(ValueError, complex, "3\09")
        self.assertRaises(TypeError, complex, "1", "2")
        self.assertRaises(TypeError, complex, "1", 42)
        self.assertRaises(TypeError, complex, 1, "2")
        self.assertRaises(ValueError, complex, "1+")
        self.assertRaises(ValueError, complex, "1+1j+1j")
        self.assertRaises(ValueError, complex, "--")
        self.assertRaises(ValueError, complex, "(1+2j")
        self.assertRaises(ValueError, complex, "1+2j)")
        self.assertRaises(ValueError, complex, "1+(2j)")
        self.assertRaises(ValueError, complex, "(1+2j)123")
        self.assertRaises(ValueError, complex, "x")
        self.assertRaises(ValueError, complex, "1j+2")
        self.assertRaises(ValueError, complex, "1e1ej")
        self.assertRaises(ValueError, complex, "1e++1ej")
        self.assertRaises(ValueError, complex, ")1+2j(")
        self.assertRaisesRegex(
            TypeError,
            "first argument must be a string ama a number, sio 'dict'",
            complex, {1:2}, 1)
        self.assertRaisesRegex(
            TypeError,
            "second argument must be a number, sio 'dict'",
            complex, 1, {1:2})
        # the following three are accepted by Python 2.6
        self.assertRaises(ValueError, complex, "1..1j")
        self.assertRaises(ValueError, complex, "1.11.1j")
        self.assertRaises(ValueError, complex, "1e1.1j")

        # check that complex accepts long unicode strings
        self.assertEqual(type(complex("1"*500)), complex)
        # check whitespace processing
        self.assertEqual(complex('\N{EM SPACE}(\N{EN SPACE}1+1j ) '), 1+1j)
        # Invalid unicode string
        # See bpo-34087
        self.assertRaises(ValueError, complex, '\u3053\u3093\u306b\u3061\u306f')

        kundi EvilExc(Exception):
            pita

        kundi evilcomplex:
            eleza __complex__(self):
                ashiria EvilExc

        self.assertRaises(EvilExc, complex, evilcomplex())

        kundi float2:
            eleza __init__(self, value):
                self.value = value
            eleza __float__(self):
                rudisha self.value

        self.assertAlmostEqual(complex(float2(42.)), 42)
        self.assertAlmostEqual(complex(real=float2(17.), imag=float2(23.)), 17+23j)
        self.assertRaises(TypeError, complex, float2(Tupu))

        kundi MyIndex:
            eleza __init__(self, value):
                self.value = value
            eleza __index__(self):
                rudisha self.value

        self.assertAlmostEqual(complex(MyIndex(42)), 42.0+0.0j)
        self.assertAlmostEqual(complex(123, MyIndex(42)), 123.0+42.0j)
        self.assertRaises(OverflowError, complex, MyIndex(2**2000))
        self.assertRaises(OverflowError, complex, 123, MyIndex(2**2000))

        kundi MyInt:
            eleza __int__(self):
                rudisha 42

        self.assertRaises(TypeError, complex, MyInt())
        self.assertRaises(TypeError, complex, 123, MyInt())

        kundi complex0(complex):
            """Test usage of __complex__() when inheriting kutoka 'complex'"""
            eleza __complex__(self):
                rudisha 42j

        kundi complex1(complex):
            """Test usage of __complex__() ukijumuisha a __new__() method"""
            eleza __new__(self, value=0j):
                rudisha complex.__new__(self, 2*value)
            eleza __complex__(self):
                rudisha self

        kundi complex2(complex):
            """Make sure that __complex__() calls fail ikiwa anything other than a
            complex ni returned"""
            eleza __complex__(self):
                rudisha Tupu

        self.assertEqual(complex(complex0(1j)), 42j)
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertEqual(complex(complex1(1j)), 2j)
        self.assertRaises(TypeError, complex, complex2(1j))

    @support.requires_IEEE_754
    eleza test_constructor_special_numbers(self):
        kundi complex2(complex):
            pita
        kila x kwenye 0.0, -0.0, INF, -INF, NAN:
            kila y kwenye 0.0, -0.0, INF, -INF, NAN:
                ukijumuisha self.subTest(x=x, y=y):
                    z = complex(x, y)
                    self.assertFloatsAreIdentical(z.real, x)
                    self.assertFloatsAreIdentical(z.imag, y)
                    z = complex2(x, y)
                    self.assertIs(type(z), complex2)
                    self.assertFloatsAreIdentical(z.real, x)
                    self.assertFloatsAreIdentical(z.imag, y)
                    z = complex(complex2(x, y))
                    self.assertIs(type(z), complex)
                    self.assertFloatsAreIdentical(z.real, x)
                    self.assertFloatsAreIdentical(z.imag, y)
                    z = complex2(complex(x, y))
                    self.assertIs(type(z), complex2)
                    self.assertFloatsAreIdentical(z.real, x)
                    self.assertFloatsAreIdentical(z.imag, y)

    eleza test_underscores(self):
        # check underscores
        kila lit kwenye VALID_UNDERSCORE_LITERALS:
            ikiwa sio any(ch kwenye lit kila ch kwenye 'xXoObB'):
                self.assertEqual(complex(lit), eval(lit))
                self.assertEqual(complex(lit), complex(lit.replace('_', '')))
        kila lit kwenye INVALID_UNDERSCORE_LITERALS:
            ikiwa lit kwenye ('0_7', '09_99'):  # octals are sio recognized here
                endelea
            ikiwa sio any(ch kwenye lit kila ch kwenye 'xXoObB'):
                self.assertRaises(ValueError, complex, lit)

    eleza test_hash(self):
        kila x kwenye range(-30, 30):
            self.assertEqual(hash(x), hash(complex(x, 0)))
            x /= 3.0    # now check against floating point
            self.assertEqual(hash(x), hash(complex(x, 0.)))

    eleza test_abs(self):
        nums = [complex(x/3., y/7.) kila x kwenye range(-9,9) kila y kwenye range(-9,9)]
        kila num kwenye nums:
            self.assertAlmostEqual((num.real**2 + num.imag**2)  ** 0.5, abs(num))

    eleza test_repr_str(self):
        eleza test(v, expected, test_fn=self.assertEqual):
            test_fn(repr(v), expected)
            test_fn(str(v), expected)

        test(1+6j, '(1+6j)')
        test(1-6j, '(1-6j)')

        test(-(1+0j), '(-1+-0j)', test_fn=self.assertNotEqual)

        test(complex(1., INF), "(1+infj)")
        test(complex(1., -INF), "(1-infj)")
        test(complex(INF, 1), "(inf+1j)")
        test(complex(-INF, INF), "(-inf+infj)")
        test(complex(NAN, 1), "(nan+1j)")
        test(complex(1, NAN), "(1+nanj)")
        test(complex(NAN, NAN), "(nan+nanj)")

        test(complex(0, INF), "infj")
        test(complex(0, -INF), "-infj")
        test(complex(0, NAN), "nanj")

        self.assertEqual(1-6j,complex(repr(1-6j)))
        self.assertEqual(1+6j,complex(repr(1+6j)))
        self.assertEqual(-6j,complex(repr(-6j)))
        self.assertEqual(6j,complex(repr(6j)))

    @support.requires_IEEE_754
    eleza test_negative_zero_repr_str(self):
        eleza test(v, expected, test_fn=self.assertEqual):
            test_fn(repr(v), expected)
            test_fn(str(v), expected)

        test(complex(0., 1.),   "1j")
        test(complex(-0., 1.),  "(-0+1j)")
        test(complex(0., -1.),  "-1j")
        test(complex(-0., -1.), "(-0-1j)")

        test(complex(0., 0.),   "0j")
        test(complex(0., -0.),  "-0j")
        test(complex(-0., 0.),  "(-0+0j)")
        test(complex(-0., -0.), "(-0-0j)")

    eleza test_neg(self):
        self.assertEqual(-(1+6j), -1-6j)

    eleza test_file(self):
        a = 3.33+4.43j
        b = 5.1+2.3j

        fo = Tupu
        jaribu:
            fo = open(support.TESTFN, "w")
            andika(a, b, file=fo)
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), ("%s %s\n" % (a, b)))
        mwishowe:
            ikiwa (fo ni sio Tupu) na (sio fo.closed):
                fo.close()
            support.unlink(support.TESTFN)

    eleza test_getnewargs(self):
        self.assertEqual((1+2j).__getnewargs__(), (1.0, 2.0))
        self.assertEqual((1-2j).__getnewargs__(), (1.0, -2.0))
        self.assertEqual((2j).__getnewargs__(), (0.0, 2.0))
        self.assertEqual((-0j).__getnewargs__(), (0.0, -0.0))
        self.assertEqual(complex(0, INF).__getnewargs__(), (0.0, INF))
        self.assertEqual(complex(INF, 0).__getnewargs__(), (INF, 0.0))

    @support.requires_IEEE_754
    eleza test_plus_minus_0j(self):
        # test that -0j na 0j literals are sio identified
        z1, z2 = 0j, -0j
        self.assertEqual(atan2(z1.imag, -1.), atan2(0., -1.))
        self.assertEqual(atan2(z2.imag, -1.), atan2(-0., -1.))

    @support.requires_IEEE_754
    eleza test_negated_imaginary_literal(self):
        z0 = -0j
        z1 = -7j
        z2 = -1e1000j
        # Note: In versions of Python < 3.2, a negated imaginary literal
        # accidentally ended up ukijumuisha real part 0.0 instead of -0.0, thanks to a
        # modification during CST -> AST translation (see issue #9011).  That's
        # fixed kwenye Python 3.2.
        self.assertFloatsAreIdentical(z0.real, -0.0)
        self.assertFloatsAreIdentical(z0.imag, -0.0)
        self.assertFloatsAreIdentical(z1.real, -0.0)
        self.assertFloatsAreIdentical(z1.imag, -7.0)
        self.assertFloatsAreIdentical(z2.real, -0.0)
        self.assertFloatsAreIdentical(z2.imag, -INF)

    @support.requires_IEEE_754
    eleza test_overflow(self):
        self.assertEqual(complex("1e500"), complex(INF, 0.0))
        self.assertEqual(complex("-1e500j"), complex(0.0, -INF))
        self.assertEqual(complex("-1e500+1.8e308j"), complex(-INF, INF))

    @support.requires_IEEE_754
    eleza test_repr_roundtrip(self):
        vals = [0.0, 1e-500, 1e-315, 1e-200, 0.0123, 3.1415, 1e50, INF, NAN]
        vals += [-v kila v kwenye vals]

        # complex(repr(z)) should recover z exactly, even kila complex
        # numbers involving an infinity, nan, ama negative zero
        kila x kwenye vals:
            kila y kwenye vals:
                z = complex(x, y)
                roundtrip = complex(repr(z))
                self.assertFloatsAreIdentical(z.real, roundtrip.real)
                self.assertFloatsAreIdentical(z.imag, roundtrip.imag)

        # ikiwa we predefine some constants, then eval(repr(z)) should
        # also work, tatizo that it might change the sign of zeros
        inf, nan = float('inf'), float('nan')
        infj, nanj = complex(0.0, inf), complex(0.0, nan)
        kila x kwenye vals:
            kila y kwenye vals:
                z = complex(x, y)
                roundtrip = eval(repr(z))
                # adding 0.0 has no effect beside changing -0.0 to 0.0
                self.assertFloatsAreIdentical(0.0 + z.real,
                                              0.0 + roundtrip.real)
                self.assertFloatsAreIdentical(0.0 + z.imag,
                                              0.0 + roundtrip.imag)

    eleza test_format(self):
        # empty format string ni same kama str()
        self.assertEqual(format(1+3j, ''), str(1+3j))
        self.assertEqual(format(1.5+3.5j, ''), str(1.5+3.5j))
        self.assertEqual(format(3j, ''), str(3j))
        self.assertEqual(format(3.2j, ''), str(3.2j))
        self.assertEqual(format(3+0j, ''), str(3+0j))
        self.assertEqual(format(3.2+0j, ''), str(3.2+0j))

        # empty presentation type should still be analogous to str,
        # even when format string ni nonempty (issue #5920).
        self.assertEqual(format(3.2+0j, '-'), str(3.2+0j))
        self.assertEqual(format(3.2+0j, '<'), str(3.2+0j))
        z = 4/7. - 100j/7.
        self.assertEqual(format(z, ''), str(z))
        self.assertEqual(format(z, '-'), str(z))
        self.assertEqual(format(z, '<'), str(z))
        self.assertEqual(format(z, '10'), str(z))
        z = complex(0.0, 3.0)
        self.assertEqual(format(z, ''), str(z))
        self.assertEqual(format(z, '-'), str(z))
        self.assertEqual(format(z, '<'), str(z))
        self.assertEqual(format(z, '2'), str(z))
        z = complex(-0.0, 2.0)
        self.assertEqual(format(z, ''), str(z))
        self.assertEqual(format(z, '-'), str(z))
        self.assertEqual(format(z, '<'), str(z))
        self.assertEqual(format(z, '3'), str(z))

        self.assertEqual(format(1+3j, 'g'), '1+3j')
        self.assertEqual(format(3j, 'g'), '0+3j')
        self.assertEqual(format(1.5+3.5j, 'g'), '1.5+3.5j')

        self.assertEqual(format(1.5+3.5j, '+g'), '+1.5+3.5j')
        self.assertEqual(format(1.5-3.5j, '+g'), '+1.5-3.5j')
        self.assertEqual(format(1.5-3.5j, '-g'), '1.5-3.5j')
        self.assertEqual(format(1.5+3.5j, ' g'), ' 1.5+3.5j')
        self.assertEqual(format(1.5-3.5j, ' g'), ' 1.5-3.5j')
        self.assertEqual(format(-1.5+3.5j, ' g'), '-1.5+3.5j')
        self.assertEqual(format(-1.5-3.5j, ' g'), '-1.5-3.5j')

        self.assertEqual(format(-1.5-3.5e-20j, 'g'), '-1.5-3.5e-20j')
        self.assertEqual(format(-1.5-3.5j, 'f'), '-1.500000-3.500000j')
        self.assertEqual(format(-1.5-3.5j, 'F'), '-1.500000-3.500000j')
        self.assertEqual(format(-1.5-3.5j, 'e'), '-1.500000e+00-3.500000e+00j')
        self.assertEqual(format(-1.5-3.5j, '.2e'), '-1.50e+00-3.50e+00j')
        self.assertEqual(format(-1.5-3.5j, '.2E'), '-1.50E+00-3.50E+00j')
        self.assertEqual(format(-1.5e10-3.5e5j, '.2G'), '-1.5E+10-3.5E+05j')

        self.assertEqual(format(1.5+3j, '<20g'),  '1.5+3j              ')
        self.assertEqual(format(1.5+3j, '*<20g'), '1.5+3j**************')
        self.assertEqual(format(1.5+3j, '>20g'),  '              1.5+3j')
        self.assertEqual(format(1.5+3j, '^20g'),  '       1.5+3j       ')
        self.assertEqual(format(1.5+3j, '<20'),   '(1.5+3j)            ')
        self.assertEqual(format(1.5+3j, '>20'),   '            (1.5+3j)')
        self.assertEqual(format(1.5+3j, '^20'),   '      (1.5+3j)      ')
        self.assertEqual(format(1.123-3.123j, '^20.2'), '     (1.1-3.1j)     ')

        self.assertEqual(format(1.5+3j, '20.2f'), '          1.50+3.00j')
        self.assertEqual(format(1.5+3j, '>20.2f'), '          1.50+3.00j')
        self.assertEqual(format(1.5+3j, '<20.2f'), '1.50+3.00j          ')
        self.assertEqual(format(1.5e20+3j, '<20.2f'), '150000000000000000000.00+3.00j')
        self.assertEqual(format(1.5e20+3j, '>40.2f'), '          150000000000000000000.00+3.00j')
        self.assertEqual(format(1.5e20+3j, '^40,.2f'), '  150,000,000,000,000,000,000.00+3.00j  ')
        self.assertEqual(format(1.5e21+3j, '^40,.2f'), ' 1,500,000,000,000,000,000,000.00+3.00j ')
        self.assertEqual(format(1.5e21+3000j, ',.2f'), '1,500,000,000,000,000,000,000.00+3,000.00j')

        # Issue 7094: Alternate formatting (specified by #)
        self.assertEqual(format(1+1j, '.0e'), '1e+00+1e+00j')
        self.assertEqual(format(1+1j, '#.0e'), '1.e+00+1.e+00j')
        self.assertEqual(format(1+1j, '.0f'), '1+1j')
        self.assertEqual(format(1+1j, '#.0f'), '1.+1.j')
        self.assertEqual(format(1.1+1.1j, 'g'), '1.1+1.1j')
        self.assertEqual(format(1.1+1.1j, '#g'), '1.10000+1.10000j')

        # Alternate doesn't make a difference kila these, they format the same ukijumuisha ama without it
        self.assertEqual(format(1+1j, '.1e'),  '1.0e+00+1.0e+00j')
        self.assertEqual(format(1+1j, '#.1e'), '1.0e+00+1.0e+00j')
        self.assertEqual(format(1+1j, '.1f'),  '1.0+1.0j')
        self.assertEqual(format(1+1j, '#.1f'), '1.0+1.0j')

        # Misc. other alternate tests
        self.assertEqual(format((-1.5+0.5j), '#f'), '-1.500000+0.500000j')
        self.assertEqual(format((-1.5+0.5j), '#.0f'), '-2.+0.j')
        self.assertEqual(format((-1.5+0.5j), '#e'), '-1.500000e+00+5.000000e-01j')
        self.assertEqual(format((-1.5+0.5j), '#.0e'), '-2.e+00+5.e-01j')
        self.assertEqual(format((-1.5+0.5j), '#g'), '-1.50000+0.500000j')
        self.assertEqual(format((-1.5+0.5j), '.0g'), '-2+0.5j')
        self.assertEqual(format((-1.5+0.5j), '#.0g'), '-2.+0.5j')

        # zero padding ni invalid
        self.assertRaises(ValueError, (1.5+0.5j).__format__, '010f')

        # '=' alignment ni invalid
        self.assertRaises(ValueError, (1.5+3j).__format__, '=20')

        # integer presentation types are an error
        kila t kwenye 'bcdoxX':
            self.assertRaises(ValueError, (1.5+0.5j).__format__, t)

        # make sure everything works kwenye ''.format()
        self.assertEqual('*{0:.3f}*'.format(3.14159+2.71828j), '*3.142+2.718j*')

        # issue 3382
        self.assertEqual(format(complex(NAN, NAN), 'f'), 'nan+nanj')
        self.assertEqual(format(complex(1, NAN), 'f'), '1.000000+nanj')
        self.assertEqual(format(complex(NAN, 1), 'f'), 'nan+1.000000j')
        self.assertEqual(format(complex(NAN, -1), 'f'), 'nan-1.000000j')
        self.assertEqual(format(complex(NAN, NAN), 'F'), 'NAN+NANj')
        self.assertEqual(format(complex(1, NAN), 'F'), '1.000000+NANj')
        self.assertEqual(format(complex(NAN, 1), 'F'), 'NAN+1.000000j')
        self.assertEqual(format(complex(NAN, -1), 'F'), 'NAN-1.000000j')
        self.assertEqual(format(complex(INF, INF), 'f'), 'inf+infj')
        self.assertEqual(format(complex(1, INF), 'f'), '1.000000+infj')
        self.assertEqual(format(complex(INF, 1), 'f'), 'inf+1.000000j')
        self.assertEqual(format(complex(INF, -1), 'f'), 'inf-1.000000j')
        self.assertEqual(format(complex(INF, INF), 'F'), 'INF+INFj')
        self.assertEqual(format(complex(1, INF), 'F'), '1.000000+INFj')
        self.assertEqual(format(complex(INF, 1), 'F'), 'INF+1.000000j')
        self.assertEqual(format(complex(INF, -1), 'F'), 'INF-1.000000j')

eleza test_main():
    support.run_unittest(ComplexTest)

ikiwa __name__ == "__main__":
    test_main()
