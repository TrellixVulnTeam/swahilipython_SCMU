"""Tests kila Lib/fractions.py."""

kutoka decimal agiza Decimal
kutoka test.support agiza requires_IEEE_754
agiza math
agiza numbers
agiza operator
agiza fractions
agiza sys
agiza unittest
agiza warnings
kutoka copy agiza copy, deepcopy
kutoka pickle agiza dumps, loads
F = fractions.Fraction
gcd = fractions.gcd

kundi DummyFloat(object):
    """Dummy float kundi kila testing comparisons ukijumuisha Fractions"""

    eleza __init__(self, value):
        ikiwa sio isinstance(value, float):
            ashiria TypeError("DummyFloat can only be initialized kutoka float")
        self.value = value

    eleza _richcmp(self, other, op):
        ikiwa isinstance(other, numbers.Rational):
            rudisha op(F.kutoka_float(self.value), other)
        lasivyo isinstance(other, DummyFloat):
            rudisha op(self.value, other.value)
        isipokua:
            rudisha NotImplemented

    eleza __eq__(self, other): rudisha self._richcmp(other, operator.eq)
    eleza __le__(self, other): rudisha self._richcmp(other, operator.le)
    eleza __lt__(self, other): rudisha self._richcmp(other, operator.lt)
    eleza __ge__(self, other): rudisha self._richcmp(other, operator.ge)
    eleza __gt__(self, other): rudisha self._richcmp(other, operator.gt)

    # shouldn't be calling __float__ at all when doing comparisons
    eleza __float__(self):
        assert Uongo, "__float__ should sio be invoked kila comparisons"

    # same goes kila subtraction
    eleza __sub__(self, other):
        assert Uongo, "__sub__ should sio be invoked kila comparisons"
    __rsub__ = __sub__


kundi DummyRational(object):
    """Test comparison of Fraction ukijumuisha a naive rational implementation."""

    eleza __init__(self, num, den):
        g = math.gcd(num, den)
        self.num = num // g
        self.den = den // g

    eleza __eq__(self, other):
        ikiwa isinstance(other, fractions.Fraction):
            rudisha (self.num == other._numerator na
                    self.den == other._denominator)
        isipokua:
            rudisha NotImplemented

    eleza __lt__(self, other):
        rudisha(self.num * other._denominator < self.den * other._numerator)

    eleza __gt__(self, other):
        rudisha(self.num * other._denominator > self.den * other._numerator)

    eleza __le__(self, other):
        rudisha(self.num * other._denominator <= self.den * other._numerator)

    eleza __ge__(self, other):
        rudisha(self.num * other._denominator >= self.den * other._numerator)

    # this kundi ni kila testing comparisons; conversion to float
    # should never be used kila a comparison, since it loses accuracy
    eleza __float__(self):
        assert Uongo, "__float__ should sio be invoked"

kundi DummyFraction(fractions.Fraction):
    """Dummy Fraction subkundi kila copy na deepcopy testing."""

kundi GcdTest(unittest.TestCase):

    eleza testMisc(self):
        # fractions.gcd() ni deprecated
        ukijumuisha self.assertWarnsRegex(DeprecationWarning, r'fractions\.gcd'):
            gcd(1, 1)
        ukijumuisha warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'fractions\.gcd',
                                    DeprecationWarning)
            self.assertEqual(0, gcd(0, 0))
            self.assertEqual(1, gcd(1, 0))
            self.assertEqual(-1, gcd(-1, 0))
            self.assertEqual(1, gcd(0, 1))
            self.assertEqual(-1, gcd(0, -1))
            self.assertEqual(1, gcd(7, 1))
            self.assertEqual(-1, gcd(7, -1))
            self.assertEqual(1, gcd(-23, 15))
            self.assertEqual(12, gcd(120, 84))
            self.assertEqual(-12, gcd(84, -120))
            self.assertEqual(gcd(120.0, 84), 12.0)
            self.assertEqual(gcd(120, 84.0), 12.0)
            self.assertEqual(gcd(F(120), F(84)), F(12))
            self.assertEqual(gcd(F(120, 77), F(84, 55)), F(12, 385))


eleza _components(r):
    rudisha (r.numerator, r.denominator)


kundi FractionTest(unittest.TestCase):

    eleza assertTypedEquals(self, expected, actual):
        """Asserts that both the types na values are the same."""
        self.assertEqual(type(expected), type(actual))
        self.assertEqual(expected, actual)

    eleza assertTypedTupleEquals(self, expected, actual):
        """Asserts that both the types na values kwenye the tuples are the same."""
        self.assertTupleEqual(expected, actual)
        self.assertListEqual(list(map(type, expected)), list(map(type, actual)))

    eleza assertRaisesMessage(self, exc_type, message,
                            callable, *args, **kwargs):
        """Asserts that callable(*args, **kwargs) ashirias exc_type(message)."""
        jaribu:
            callable(*args, **kwargs)
        tatizo exc_type kama e:
            self.assertEqual(message, str(e))
        isipokua:
            self.fail("%s sio ashiriad" % exc_type.__name__)

    eleza testInit(self):
        self.assertEqual((0, 1), _components(F()))
        self.assertEqual((7, 1), _components(F(7)))
        self.assertEqual((7, 3), _components(F(F(7, 3))))

        self.assertEqual((-1, 1), _components(F(-1, 1)))
        self.assertEqual((-1, 1), _components(F(1, -1)))
        self.assertEqual((1, 1), _components(F(-2, -2)))
        self.assertEqual((1, 2), _components(F(5, 10)))
        self.assertEqual((7, 15), _components(F(7, 15)))
        self.assertEqual((10**23, 1), _components(F(10**23)))

        self.assertEqual((3, 77), _components(F(F(3, 7), 11)))
        self.assertEqual((-9, 5), _components(F(2, F(-10, 9))))
        self.assertEqual((2486, 2485), _components(F(F(22, 7), F(355, 113))))

        self.assertRaisesMessage(ZeroDivisionError, "Fraction(12, 0)",
                                 F, 12, 0)
        self.assertRaises(TypeError, F, 1.5 + 3j)

        self.assertRaises(TypeError, F, "3/2", 3)
        self.assertRaises(TypeError, F, 3, 0j)
        self.assertRaises(TypeError, F, 3, 1j)
        self.assertRaises(TypeError, F, 1, 2, 3)

    @requires_IEEE_754
    eleza testInitFromFloat(self):
        self.assertEqual((5, 2), _components(F(2.5)))
        self.assertEqual((0, 1), _components(F(-0.0)))
        self.assertEqual((3602879701896397, 36028797018963968),
                         _components(F(0.1)))
        # bug 16469: error types should be consistent ukijumuisha float -> int
        self.assertRaises(ValueError, F, float('nan'))
        self.assertRaises(OverflowError, F, float('inf'))
        self.assertRaises(OverflowError, F, float('-inf'))

    eleza testInitFromDecimal(self):
        self.assertEqual((11, 10),
                         _components(F(Decimal('1.1'))))
        self.assertEqual((7, 200),
                         _components(F(Decimal('3.5e-2'))))
        self.assertEqual((0, 1),
                         _components(F(Decimal('.000e20'))))
        # bug 16469: error types should be consistent ukijumuisha decimal -> int
        self.assertRaises(ValueError, F, Decimal('nan'))
        self.assertRaises(ValueError, F, Decimal('snan'))
        self.assertRaises(OverflowError, F, Decimal('inf'))
        self.assertRaises(OverflowError, F, Decimal('-inf'))

    eleza testFromString(self):
        self.assertEqual((5, 1), _components(F("5")))
        self.assertEqual((3, 2), _components(F("3/2")))
        self.assertEqual((3, 2), _components(F(" \n  +3/2")))
        self.assertEqual((-3, 2), _components(F("-3/2  ")))
        self.assertEqual((13, 2), _components(F("    013/02 \n  ")))
        self.assertEqual((16, 5), _components(F(" 3.2 ")))
        self.assertEqual((-16, 5), _components(F(" -3.2 ")))
        self.assertEqual((-3, 1), _components(F(" -3. ")))
        self.assertEqual((3, 5), _components(F(" .6 ")))
        self.assertEqual((1, 3125), _components(F("32.e-5")))
        self.assertEqual((1000000, 1), _components(F("1E+06")))
        self.assertEqual((-12300, 1), _components(F("-1.23e4")))
        self.assertEqual((0, 1), _components(F(" .0e+0\t")))
        self.assertEqual((0, 1), _components(F("-0.000e0")))

        self.assertRaisesMessage(
            ZeroDivisionError, "Fraction(3, 0)",
            F, "3/0")
        self.assertRaisesMessage(
            ValueError, "Invalid literal kila Fraction: '3/'",
            F, "3/")
        self.assertRaisesMessage(
            ValueError, "Invalid literal kila Fraction: '/2'",
            F, "/2")
        self.assertRaisesMessage(
            ValueError, "Invalid literal kila Fraction: '3 /2'",
            F, "3 /2")
        self.assertRaisesMessage(
            # Denominators don't need a sign.
            ValueError, "Invalid literal kila Fraction: '3/+2'",
            F, "3/+2")
        self.assertRaisesMessage(
            # Imitate float's parsing.
            ValueError, "Invalid literal kila Fraction: '+ 3/2'",
            F, "+ 3/2")
        self.assertRaisesMessage(
            # Avoid treating '.' kama a regex special character.
            ValueError, "Invalid literal kila Fraction: '3a2'",
            F, "3a2")
        self.assertRaisesMessage(
            # Don't accept combinations of decimals na rationals.
            ValueError, "Invalid literal kila Fraction: '3/7.2'",
            F, "3/7.2")
        self.assertRaisesMessage(
            # Don't accept combinations of decimals na rationals.
            ValueError, "Invalid literal kila Fraction: '3.2/7'",
            F, "3.2/7")
        self.assertRaisesMessage(
            # Allow 3. na .3, but sio .
            ValueError, "Invalid literal kila Fraction: '.'",
            F, ".")

    eleza testImmutable(self):
        r = F(7, 3)
        r.__init__(2, 15)
        self.assertEqual((7, 3), _components(r))

        self.assertRaises(AttributeError, setattr, r, 'numerator', 12)
        self.assertRaises(AttributeError, setattr, r, 'denominator', 6)
        self.assertEqual((7, 3), _components(r))

        # But ikiwa you _really_ need to:
        r._numerator = 4
        r._denominator = 2
        self.assertEqual((4, 2), _components(r))
        # Which komas some agizaant operations:
        self.assertNotEqual(F(4, 2), r)

    eleza testFromFloat(self):
        self.assertRaises(TypeError, F.kutoka_float, 3+4j)
        self.assertEqual((10, 1), _components(F.kutoka_float(10)))
        bigint = 1234567890123456789
        self.assertEqual((bigint, 1), _components(F.kutoka_float(bigint)))
        self.assertEqual((0, 1), _components(F.kutoka_float(-0.0)))
        self.assertEqual((10, 1), _components(F.kutoka_float(10.0)))
        self.assertEqual((-5, 2), _components(F.kutoka_float(-2.5)))
        self.assertEqual((99999999999999991611392, 1),
                         _components(F.kutoka_float(1e23)))
        self.assertEqual(float(10**23), float(F.kutoka_float(1e23)))
        self.assertEqual((3602879701896397, 1125899906842624),
                         _components(F.kutoka_float(3.2)))
        self.assertEqual(3.2, float(F.kutoka_float(3.2)))

        inf = 1e1000
        nan = inf - inf
        # bug 16469: error types should be consistent ukijumuisha float -> int
        self.assertRaisesMessage(
            OverflowError, "cannot convert Infinity to integer ratio",
            F.kutoka_float, inf)
        self.assertRaisesMessage(
            OverflowError, "cannot convert Infinity to integer ratio",
            F.kutoka_float, -inf)
        self.assertRaisesMessage(
            ValueError, "cannot convert NaN to integer ratio",
            F.kutoka_float, nan)

    eleza testFromDecimal(self):
        self.assertRaises(TypeError, F.kutoka_decimal, 3+4j)
        self.assertEqual(F(10, 1), F.kutoka_decimal(10))
        self.assertEqual(F(0), F.kutoka_decimal(Decimal("-0")))
        self.assertEqual(F(5, 10), F.kutoka_decimal(Decimal("0.5")))
        self.assertEqual(F(5, 1000), F.kutoka_decimal(Decimal("5e-3")))
        self.assertEqual(F(5000), F.kutoka_decimal(Decimal("5e3")))
        self.assertEqual(1 - F(1, 10**30),
                         F.kutoka_decimal(Decimal("0." + "9" * 30)))

        # bug 16469: error types should be consistent ukijumuisha decimal -> int
        self.assertRaisesMessage(
            OverflowError, "cannot convert Infinity to integer ratio",
            F.kutoka_decimal, Decimal("inf"))
        self.assertRaisesMessage(
            OverflowError, "cannot convert Infinity to integer ratio",
            F.kutoka_decimal, Decimal("-inf"))
        self.assertRaisesMessage(
            ValueError, "cannot convert NaN to integer ratio",
            F.kutoka_decimal, Decimal("nan"))
        self.assertRaisesMessage(
            ValueError, "cannot convert NaN to integer ratio",
            F.kutoka_decimal, Decimal("snan"))

    eleza test_as_integer_ratio(self):
        self.assertEqual(F(4, 6).as_integer_ratio(), (2, 3))
        self.assertEqual(F(-4, 6).as_integer_ratio(), (-2, 3))
        self.assertEqual(F(4, -6).as_integer_ratio(), (-2, 3))
        self.assertEqual(F(0, 6).as_integer_ratio(), (0, 1))

    eleza testLimitDenominator(self):
        rpi = F('3.1415926535897932')
        self.assertEqual(rpi.limit_denominator(10000), F(355, 113))
        self.assertEqual(-rpi.limit_denominator(10000), F(-355, 113))
        self.assertEqual(rpi.limit_denominator(113), F(355, 113))
        self.assertEqual(rpi.limit_denominator(112), F(333, 106))
        self.assertEqual(F(201, 200).limit_denominator(100), F(1))
        self.assertEqual(F(201, 200).limit_denominator(101), F(102, 101))
        self.assertEqual(F(0).limit_denominator(10000), F(0))
        kila i kwenye (0, -1):
            self.assertRaisesMessage(
                ValueError, "max_denominator should be at least 1",
                F(1).limit_denominator, i)

    eleza testConversions(self):
        self.assertTypedEquals(-1, math.trunc(F(-11, 10)))
        self.assertTypedEquals(1, math.trunc(F(11, 10)))
        self.assertTypedEquals(-2, math.floor(F(-11, 10)))
        self.assertTypedEquals(-1, math.ceil(F(-11, 10)))
        self.assertTypedEquals(-1, math.ceil(F(-10, 10)))
        self.assertTypedEquals(-1, int(F(-11, 10)))
        self.assertTypedEquals(0, round(F(-1, 10)))
        self.assertTypedEquals(0, round(F(-5, 10)))
        self.assertTypedEquals(-2, round(F(-15, 10)))
        self.assertTypedEquals(-1, round(F(-7, 10)))

        self.assertEqual(Uongo, bool(F(0, 1)))
        self.assertEqual(Kweli, bool(F(3, 2)))
        self.assertTypedEquals(0.1, float(F(1, 10)))

        # Check that __float__ isn't implemented by converting the
        # numerator na denominator to float before dividing.
        self.assertRaises(OverflowError, float, int('2'*400+'7'))
        self.assertAlmostEqual(2.0/3,
                               float(F(int('2'*400+'7'), int('3'*400+'1'))))

        self.assertTypedEquals(0.1+0j, complex(F(1,10)))

    eleza testRound(self):
        self.assertTypedEquals(F(-200), round(F(-150), -2))
        self.assertTypedEquals(F(-200), round(F(-250), -2))
        self.assertTypedEquals(F(30), round(F(26), -1))
        self.assertTypedEquals(F(-2, 10), round(F(-15, 100), 1))
        self.assertTypedEquals(F(-2, 10), round(F(-25, 100), 1))

    eleza testArithmetic(self):
        self.assertEqual(F(1, 2), F(1, 10) + F(2, 5))
        self.assertEqual(F(-3, 10), F(1, 10) - F(2, 5))
        self.assertEqual(F(1, 25), F(1, 10) * F(2, 5))
        self.assertEqual(F(1, 4), F(1, 10) / F(2, 5))
        self.assertTypedEquals(2, F(9, 10) // F(2, 5))
        self.assertTypedEquals(10**23, F(10**23, 1) // F(1))
        self.assertEqual(F(5, 6), F(7, 3) % F(3, 2))
        self.assertEqual(F(2, 3), F(-7, 3) % F(3, 2))
        self.assertEqual((F(1), F(5, 6)), divmod(F(7, 3), F(3, 2)))
        self.assertEqual((F(-2), F(2, 3)), divmod(F(-7, 3), F(3, 2)))
        self.assertEqual(F(8, 27), F(2, 3) ** F(3))
        self.assertEqual(F(27, 8), F(2, 3) ** F(-3))
        self.assertTypedEquals(2.0, F(4) ** F(1, 2))
        self.assertEqual(F(1, 1), +F(1, 1))
        z = pow(F(-1), F(1, 2))
        self.assertAlmostEqual(z.real, 0)
        self.assertEqual(z.imag, 1)
        # Regression test kila #27539.
        p = F(-1, 2) ** 0
        self.assertEqual(p, F(1, 1))
        self.assertEqual(p.numerator, 1)
        self.assertEqual(p.denominator, 1)
        p = F(-1, 2) ** -1
        self.assertEqual(p, F(-2, 1))
        self.assertEqual(p.numerator, -2)
        self.assertEqual(p.denominator, 1)
        p = F(-1, 2) ** -2
        self.assertEqual(p, F(4, 1))
        self.assertEqual(p.numerator, 4)
        self.assertEqual(p.denominator, 1)

    eleza testLargeArithmetic(self):
        self.assertTypedEquals(
            F(10101010100808080808080808101010101010000000000000000,
              1010101010101010101010101011111111101010101010101010101010101),
            F(10**35+1, 10**27+1) % F(10**27+1, 10**35-1)
        )
        self.assertTypedEquals(
            F(7, 1901475900342344102245054808064),
            F(-2**100, 3) % F(5, 2**100)
        )
        self.assertTypedTupleEquals(
            (9999999999999999,
             F(10101010100808080808080808101010101010000000000000000,
               1010101010101010101010101011111111101010101010101010101010101)),
            divmod(F(10**35+1, 10**27+1), F(10**27+1, 10**35-1))
        )
        self.assertTypedEquals(
            -2 ** 200 // 15,
            F(-2**100, 3) // F(5, 2**100)
        )
        self.assertTypedEquals(
            1,
            F(5, 2**100) // F(3, 2**100)
        )
        self.assertTypedEquals(
            (1, F(2, 2**100)),
            divmod(F(5, 2**100), F(3, 2**100))
        )
        self.assertTypedTupleEquals(
            (-2 ** 200 // 15,
             F(7, 1901475900342344102245054808064)),
            divmod(F(-2**100, 3), F(5, 2**100))
        )

    eleza testMixedArithmetic(self):
        self.assertTypedEquals(F(11, 10), F(1, 10) + 1)
        self.assertTypedEquals(1.1, F(1, 10) + 1.0)
        self.assertTypedEquals(1.1 + 0j, F(1, 10) + (1.0 + 0j))
        self.assertTypedEquals(F(11, 10), 1 + F(1, 10))
        self.assertTypedEquals(1.1, 1.0 + F(1, 10))
        self.assertTypedEquals(1.1 + 0j, (1.0 + 0j) + F(1, 10))

        self.assertTypedEquals(F(-9, 10), F(1, 10) - 1)
        self.assertTypedEquals(-0.9, F(1, 10) - 1.0)
        self.assertTypedEquals(-0.9 + 0j, F(1, 10) - (1.0 + 0j))
        self.assertTypedEquals(F(9, 10), 1 - F(1, 10))
        self.assertTypedEquals(0.9, 1.0 - F(1, 10))
        self.assertTypedEquals(0.9 + 0j, (1.0 + 0j) - F(1, 10))

        self.assertTypedEquals(F(1, 10), F(1, 10) * 1)
        self.assertTypedEquals(0.1, F(1, 10) * 1.0)
        self.assertTypedEquals(0.1 + 0j, F(1, 10) * (1.0 + 0j))
        self.assertTypedEquals(F(1, 10), 1 * F(1, 10))
        self.assertTypedEquals(0.1, 1.0 * F(1, 10))
        self.assertTypedEquals(0.1 + 0j, (1.0 + 0j) * F(1, 10))

        self.assertTypedEquals(F(1, 10), F(1, 10) / 1)
        self.assertTypedEquals(0.1, F(1, 10) / 1.0)
        self.assertTypedEquals(0.1 + 0j, F(1, 10) / (1.0 + 0j))
        self.assertTypedEquals(F(10, 1), 1 / F(1, 10))
        self.assertTypedEquals(10.0, 1.0 / F(1, 10))
        self.assertTypedEquals(10.0 + 0j, (1.0 + 0j) / F(1, 10))

        self.assertTypedEquals(0, F(1, 10) // 1)
        self.assertTypedEquals(0.0, F(1, 10) // 1.0)
        self.assertTypedEquals(10, 1 // F(1, 10))
        self.assertTypedEquals(10**23, 10**22 // F(1, 10))
        self.assertTypedEquals(1.0 // 0.1, 1.0 // F(1, 10))

        self.assertTypedEquals(F(1, 10), F(1, 10) % 1)
        self.assertTypedEquals(0.1, F(1, 10) % 1.0)
        self.assertTypedEquals(F(0, 1), 1 % F(1, 10))
        self.assertTypedEquals(1.0 % 0.1, 1.0 % F(1, 10))
        self.assertTypedEquals(0.1, F(1, 10) % float('inf'))
        self.assertTypedEquals(float('-inf'), F(1, 10) % float('-inf'))
        self.assertTypedEquals(float('inf'), F(-1, 10) % float('inf'))
        self.assertTypedEquals(-0.1, F(-1, 10) % float('-inf'))

        self.assertTypedTupleEquals((0, F(1, 10)), divmod(F(1, 10), 1))
        self.assertTypedTupleEquals(divmod(0.1, 1.0), divmod(F(1, 10), 1.0))
        self.assertTypedTupleEquals((10, F(0)), divmod(1, F(1, 10)))
        self.assertTypedTupleEquals(divmod(1.0, 0.1), divmod(1.0, F(1, 10)))
        self.assertTypedTupleEquals(divmod(0.1, float('inf')), divmod(F(1, 10), float('inf')))
        self.assertTypedTupleEquals(divmod(0.1, float('-inf')), divmod(F(1, 10), float('-inf')))
        self.assertTypedTupleEquals(divmod(-0.1, float('inf')), divmod(F(-1, 10), float('inf')))
        self.assertTypedTupleEquals(divmod(-0.1, float('-inf')), divmod(F(-1, 10), float('-inf')))

        # ** has more interesting conversion rules.
        self.assertTypedEquals(F(100, 1), F(1, 10) ** -2)
        self.assertTypedEquals(F(100, 1), F(10, 1) ** 2)
        self.assertTypedEquals(0.1, F(1, 10) ** 1.0)
        self.assertTypedEquals(0.1 + 0j, F(1, 10) ** (1.0 + 0j))
        self.assertTypedEquals(4 , 2 ** F(2, 1))
        z = pow(-1, F(1, 2))
        self.assertAlmostEqual(0, z.real)
        self.assertEqual(1, z.imag)
        self.assertTypedEquals(F(1, 4) , 2 ** F(-2, 1))
        self.assertTypedEquals(2.0 , 4 ** F(1, 2))
        self.assertTypedEquals(0.25, 2.0 ** F(-2, 1))
        self.assertTypedEquals(1.0 + 0j, (1.0 + 0j) ** F(1, 10))
        self.assertRaises(ZeroDivisionError, operator.pow,
                          F(0, 1), -2)

    eleza testMixingWithDecimal(self):
        # Decimal refuses mixed arithmetic (but sio mixed comparisons)
        self.assertRaises(TypeError, operator.add,
                          F(3,11), Decimal('3.1415926'))
        self.assertRaises(TypeError, operator.add,
                          Decimal('3.1415926'), F(3,11))

    eleza testComparisons(self):
        self.assertKweli(F(1, 2) < F(2, 3))
        self.assertUongo(F(1, 2) < F(1, 2))
        self.assertKweli(F(1, 2) <= F(2, 3))
        self.assertKweli(F(1, 2) <= F(1, 2))
        self.assertUongo(F(2, 3) <= F(1, 2))
        self.assertKweli(F(1, 2) == F(1, 2))
        self.assertUongo(F(1, 2) == F(1, 3))
        self.assertUongo(F(1, 2) != F(1, 2))
        self.assertKweli(F(1, 2) != F(1, 3))

    eleza testComparisonsDummyRational(self):
        self.assertKweli(F(1, 2) == DummyRational(1, 2))
        self.assertKweli(DummyRational(1, 2) == F(1, 2))
        self.assertUongo(F(1, 2) == DummyRational(3, 4))
        self.assertUongo(DummyRational(3, 4) == F(1, 2))

        self.assertKweli(F(1, 2) < DummyRational(3, 4))
        self.assertUongo(F(1, 2) < DummyRational(1, 2))
        self.assertUongo(F(1, 2) < DummyRational(1, 7))
        self.assertUongo(F(1, 2) > DummyRational(3, 4))
        self.assertUongo(F(1, 2) > DummyRational(1, 2))
        self.assertKweli(F(1, 2) > DummyRational(1, 7))
        self.assertKweli(F(1, 2) <= DummyRational(3, 4))
        self.assertKweli(F(1, 2) <= DummyRational(1, 2))
        self.assertUongo(F(1, 2) <= DummyRational(1, 7))
        self.assertUongo(F(1, 2) >= DummyRational(3, 4))
        self.assertKweli(F(1, 2) >= DummyRational(1, 2))
        self.assertKweli(F(1, 2) >= DummyRational(1, 7))

        self.assertKweli(DummyRational(1, 2) < F(3, 4))
        self.assertUongo(DummyRational(1, 2) < F(1, 2))
        self.assertUongo(DummyRational(1, 2) < F(1, 7))
        self.assertUongo(DummyRational(1, 2) > F(3, 4))
        self.assertUongo(DummyRational(1, 2) > F(1, 2))
        self.assertKweli(DummyRational(1, 2) > F(1, 7))
        self.assertKweli(DummyRational(1, 2) <= F(3, 4))
        self.assertKweli(DummyRational(1, 2) <= F(1, 2))
        self.assertUongo(DummyRational(1, 2) <= F(1, 7))
        self.assertUongo(DummyRational(1, 2) >= F(3, 4))
        self.assertKweli(DummyRational(1, 2) >= F(1, 2))
        self.assertKweli(DummyRational(1, 2) >= F(1, 7))

    eleza testComparisonsDummyFloat(self):
        x = DummyFloat(1./3.)
        y = F(1, 3)
        self.assertKweli(x != y)
        self.assertKweli(x < y ama x > y)
        self.assertUongo(x == y)
        self.assertUongo(x <= y na x >= y)
        self.assertKweli(y != x)
        self.assertKweli(y < x ama y > x)
        self.assertUongo(y == x)
        self.assertUongo(y <= x na y >= x)

    eleza testMixedLess(self):
        self.assertKweli(2 < F(5, 2))
        self.assertUongo(2 < F(4, 2))
        self.assertKweli(F(5, 2) < 3)
        self.assertUongo(F(4, 2) < 2)

        self.assertKweli(F(1, 2) < 0.6)
        self.assertUongo(F(1, 2) < 0.4)
        self.assertKweli(0.4 < F(1, 2))
        self.assertUongo(0.5 < F(1, 2))

        self.assertUongo(float('inf') < F(1, 2))
        self.assertKweli(float('-inf') < F(0, 10))
        self.assertUongo(float('nan') < F(-3, 7))
        self.assertKweli(F(1, 2) < float('inf'))
        self.assertUongo(F(17, 12) < float('-inf'))
        self.assertUongo(F(144, -89) < float('nan'))

    eleza testMixedLessEqual(self):
        self.assertKweli(0.5 <= F(1, 2))
        self.assertUongo(0.6 <= F(1, 2))
        self.assertKweli(F(1, 2) <= 0.5)
        self.assertUongo(F(1, 2) <= 0.4)
        self.assertKweli(2 <= F(4, 2))
        self.assertUongo(2 <= F(3, 2))
        self.assertKweli(F(4, 2) <= 2)
        self.assertUongo(F(5, 2) <= 2)

        self.assertUongo(float('inf') <= F(1, 2))
        self.assertKweli(float('-inf') <= F(0, 10))
        self.assertUongo(float('nan') <= F(-3, 7))
        self.assertKweli(F(1, 2) <= float('inf'))
        self.assertUongo(F(17, 12) <= float('-inf'))
        self.assertUongo(F(144, -89) <= float('nan'))

    eleza testBigFloatComparisons(self):
        # Because 10**23 can't be represented exactly kama a float:
        self.assertUongo(F(10**23) == float(10**23))
        # The first test demonstrates why these are agizaant.
        self.assertUongo(1e23 < float(F(math.trunc(1e23) + 1)))
        self.assertKweli(1e23 < F(math.trunc(1e23) + 1))
        self.assertUongo(1e23 <= F(math.trunc(1e23) - 1))
        self.assertKweli(1e23 > F(math.trunc(1e23) - 1))
        self.assertUongo(1e23 >= F(math.trunc(1e23) + 1))

    eleza testBigComplexComparisons(self):
        self.assertUongo(F(10**23) == complex(10**23))
        self.assertRaises(TypeError, operator.gt, F(10**23), complex(10**23))
        self.assertRaises(TypeError, operator.le, F(10**23), complex(10**23))

        x = F(3, 8)
        z = complex(0.375, 0.0)
        w = complex(0.375, 0.2)
        self.assertKweli(x == z)
        self.assertUongo(x != z)
        self.assertUongo(x == w)
        self.assertKweli(x != w)
        kila op kwenye operator.lt, operator.le, operator.gt, operator.ge:
            self.assertRaises(TypeError, op, x, z)
            self.assertRaises(TypeError, op, z, x)
            self.assertRaises(TypeError, op, x, w)
            self.assertRaises(TypeError, op, w, x)

    eleza testMixedEqual(self):
        self.assertKweli(0.5 == F(1, 2))
        self.assertUongo(0.6 == F(1, 2))
        self.assertKweli(F(1, 2) == 0.5)
        self.assertUongo(F(1, 2) == 0.4)
        self.assertKweli(2 == F(4, 2))
        self.assertUongo(2 == F(3, 2))
        self.assertKweli(F(4, 2) == 2)
        self.assertUongo(F(5, 2) == 2)
        self.assertUongo(F(5, 2) == float('nan'))
        self.assertUongo(float('nan') == F(3, 7))
        self.assertUongo(F(5, 2) == float('inf'))
        self.assertUongo(float('-inf') == F(2, 5))

    eleza testStringification(self):
        self.assertEqual("Fraction(7, 3)", repr(F(7, 3)))
        self.assertEqual("Fraction(6283185307, 2000000000)",
                         repr(F('3.1415926535')))
        self.assertEqual("Fraction(-1, 100000000000000000000)",
                         repr(F(1, -10**20)))
        self.assertEqual("7/3", str(F(7, 3)))
        self.assertEqual("7", str(F(7, 1)))

    eleza testHash(self):
        hmod = sys.hash_info.modulus
        hinf = sys.hash_info.inf
        self.assertEqual(hash(2.5), hash(F(5, 2)))
        self.assertEqual(hash(10**50), hash(F(10**50)))
        self.assertNotEqual(hash(float(10**23)), hash(F(10**23)))
        self.assertEqual(hinf, hash(F(1, hmod)))
        # Check that __hash__ produces the same value kama hash(), for
        # consistency ukijumuisha int na Decimal.  (See issue #10356.)
        self.assertEqual(hash(F(-1)), F(-1).__hash__())

    eleza testApproximatePi(self):
        # Algorithm borrowed kutoka
        # http://docs.python.org/lib/decimal-recipes.html
        three = F(3)
        lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
        wakati abs(s - lasts) > F(1, 10**9):
            lasts = s
            n, na = n+na, na+8
            d, da = d+da, da+32
            t = (t * n) / d
            s += t
        self.assertAlmostEqual(math.pi, s)

    eleza testApproximateCos1(self):
        # Algorithm borrowed kutoka
        # http://docs.python.org/lib/decimal-recipes.html
        x = F(1)
        i, lasts, s, fact, num, sign = 0, 0, F(1), 1, 1, 1
        wakati abs(s - lasts) > F(1, 10**9):
            lasts = s
            i += 2
            fact *= i * (i-1)
            num *= x * x
            sign *= -1
            s += num / fact * sign
        self.assertAlmostEqual(math.cos(1), s)

    eleza test_copy_deepcopy_pickle(self):
        r = F(13, 7)
        dr = DummyFraction(13, 7)
        self.assertEqual(r, loads(dumps(r)))
        self.assertEqual(id(r), id(copy(r)))
        self.assertEqual(id(r), id(deepcopy(r)))
        self.assertNotEqual(id(dr), id(copy(dr)))
        self.assertNotEqual(id(dr), id(deepcopy(dr)))
        self.assertTypedEquals(dr, copy(dr))
        self.assertTypedEquals(dr, deepcopy(dr))

    eleza test_slots(self):
        # Issue 4998
        r = F(13, 7)
        self.assertRaises(AttributeError, setattr, r, 'a', 10)

ikiwa __name__ == '__main__':
    unittest.main()
