agiza unittest
kutoka test agiza support

agiza sys

agiza random
agiza math
agiza array

# SHIFT should match the value kwenye longintrepr.h kila best testing.
SHIFT = sys.int_info.bits_per_digit
BASE = 2 ** SHIFT
MASK = BASE - 1
KARATSUBA_CUTOFF = 70   # kutoka longobject.c

# Max number of base BASE digits to use kwenye test cases.  Doubling
# this will more than double the runtime.
MAXDIGITS = 15

# build some special values
special = [0, 1, 2, BASE, BASE >> 1, 0x5555555555555555, 0xaaaaaaaaaaaaaaaa]
#  some solid strings of one bits
p2 = 4  # 0 na 1 already added
kila i kwenye range(2*SHIFT):
    special.append(p2 - 1)
    p2 = p2 << 1
toa p2
# add complements & negations
special += [~x kila x kwenye special] + [-x kila x kwenye special]

DBL_MAX = sys.float_info.max
DBL_MAX_EXP = sys.float_info.max_exp
DBL_MIN_EXP = sys.float_info.min_exp
DBL_MANT_DIG = sys.float_info.mant_dig
DBL_MIN_OVERFLOW = 2**DBL_MAX_EXP - 2**(DBL_MAX_EXP - DBL_MANT_DIG - 1)


# Pure Python version of correctly-rounded integer-to-float conversion.
eleza int_to_float(n):
    """
    Correctly-rounded integer-to-float conversion.

    """
    # Constants, depending only on the floating-point format kwenye use.
    # We use an extra 2 bits of precision kila rounding purposes.
    PRECISION = sys.float_info.mant_dig + 2
    SHIFT_MAX = sys.float_info.max_exp - PRECISION
    Q_MAX = 1 << PRECISION
    ROUND_HALF_TO_EVEN_CORRECTION = [0, -1, -2, 1, 0, -1, 2, 1]

    # Reduce to the case where n ni positive.
    ikiwa n == 0:
        rudisha 0.0
    lasivyo n < 0:
        rudisha -int_to_float(-n)

    # Convert n to a 'floating-point' number q * 2**shift, where q ni an
    # integer ukijumuisha 'PRECISION' significant bits.  When shifting n to create q,
    # the least significant bit of q ni treated kama 'sticky'.  That is, the
    # least significant bit of q ni set ikiwa either the corresponding bit of n
    # was already set, ama any one of the bits of n lost kwenye the shift was set.
    shift = n.bit_length() - PRECISION
    q = n << -shift ikiwa shift < 0 isipokua (n >> shift) | bool(n & ~(-1 << shift))

    # Round half to even (actually rounds to the nearest multiple of 4,
    # rounding ties to a multiple of 8).
    q += ROUND_HALF_TO_EVEN_CORRECTION[q & 7]

    # Detect overflow.
    ikiwa shift + (q == Q_MAX) > SHIFT_MAX:
        ashiria OverflowError("integer too large to convert to float")

    # Checks: q ni exactly representable, na q**2**shift doesn't overflow.
    assert q % 4 == 0 na q // 4 <= 2**(sys.float_info.mant_dig)
    assert q * 2**shift <= sys.float_info.max

    # Some circularity here, since float(q) ni doing an int-to-float
    # conversion.  But here q ni of bounded size, na ni exactly representable
    # kama a float.  In a low-level C-like language, this operation would be a
    # simple cast (e.g., kutoka unsigned long long to double).
    rudisha math.ldexp(float(q), shift)


# pure Python version of correctly-rounded true division
eleza truediv(a, b):
    """Correctly-rounded true division kila integers."""
    negative = a^b < 0
    a, b = abs(a), abs(b)

    # exceptions:  division by zero, overflow
    ikiwa sio b:
        ashiria ZeroDivisionError("division by zero")
    ikiwa a >= DBL_MIN_OVERFLOW * b:
        ashiria OverflowError("int/int too large to represent kama a float")

   # find integer d satisfying 2**(d - 1) <= a/b < 2**d
    d = a.bit_length() - b.bit_length()
    ikiwa d >= 0 na a >= 2**d * b ama d < 0 na a * 2**-d >= b:
        d += 1

    # compute 2**-exp * a / b kila suitable exp
    exp = max(d, DBL_MIN_EXP) - DBL_MANT_DIG
    a, b = a << max(-exp, 0), b << max(exp, 0)
    q, r = divmod(a, b)

    # round-half-to-even: fractional part ni r/b, which ni > 0.5 iff
    # 2*r > b, na == 0.5 iff 2*r == b.
    ikiwa 2*r > b ama 2*r == b na q % 2 == 1:
        q += 1

    result = math.ldexp(q, exp)
    rudisha -result ikiwa negative isipokua result


kundi LongTest(unittest.TestCase):

    # Get quasi-random long consisting of ndigits digits (in base BASE).
    # quasi == the most-significant digit will sio be 0, na the number
    # ni constructed to contain long strings of 0 na 1 bits.  These are
    # more likely than random bits to provoke digit-boundary errors.
    # The sign of the number ni also random.

    eleza getran(self, ndigits):
        self.assertGreater(ndigits, 0)
        nbits_hi = ndigits * SHIFT
        nbits_lo = nbits_hi - SHIFT + 1
        answer = 0
        nbits = 0
        r = int(random.random() * (SHIFT * 2)) | 1  # force 1 bits to start
        wakati nbits < nbits_lo:
            bits = (r >> 1) + 1
            bits = min(bits, nbits_hi - nbits)
            self.assertKweli(1 <= bits <= SHIFT)
            nbits = nbits + bits
            answer = answer << bits
            ikiwa r & 1:
                answer = answer | ((1 << bits) - 1)
            r = int(random.random() * (SHIFT * 2))
        self.assertKweli(nbits_lo <= nbits <= nbits_hi)
        ikiwa random.random() < 0.5:
            answer = -answer
        rudisha answer

    # Get random long consisting of ndigits random digits (relative to base
    # BASE).  The sign bit ni also random.

    eleza getran2(ndigits):
        answer = 0
        kila i kwenye range(ndigits):
            answer = (answer << SHIFT) | random.randint(0, MASK)
        ikiwa random.random() < 0.5:
            answer = -answer
        rudisha answer

    eleza check_division(self, x, y):
        eq = self.assertEqual
        ukijumuisha self.subTest(x=x, y=y):
            q, r = divmod(x, y)
            q2, r2 = x//y, x%y
            pab, pba = x*y, y*x
            eq(pab, pba, "multiplication does sio commute")
            eq(q, q2, "divmod returns different quotient than /")
            eq(r, r2, "divmod returns different mod than %")
            eq(x, q*y + r, "x != q*y + r after divmod")
            ikiwa y > 0:
                self.assertKweli(0 <= r < y, "bad mod kutoka divmod")
            isipokua:
                self.assertKweli(y < r <= 0, "bad mod kutoka divmod")

    eleza test_division(self):
        digits = list(range(1, MAXDIGITS+1)) + list(range(KARATSUBA_CUTOFF,
                                                      KARATSUBA_CUTOFF + 14))
        digits.append(KARATSUBA_CUTOFF * 3)
        kila lenx kwenye digits:
            x = self.getran(lenx)
            kila leny kwenye digits:
                y = self.getran(leny) ama 1
                self.check_division(x, y)

        # specific numbers chosen to exercise corner cases of the
        # current long division implementation

        # 30-bit cases involving a quotient digit estimate of BASE+1
        self.check_division(1231948412290879395966702881,
                            1147341367131428698)
        self.check_division(815427756481275430342312021515587883,
                       707270836069027745)
        self.check_division(627976073697012820849443363563599041,
                       643588798496057020)
        self.check_division(1115141373653752303710932756325578065,
                       1038556335171453937726882627)
        # 30-bit cases that require the post-subtraction correction step
        self.check_division(922498905405436751940989320930368494,
                       949985870686786135626943396)
        self.check_division(768235853328091167204009652174031844,
                       1091555541180371554426545266)

        # 15-bit cases involving a quotient digit estimate of BASE+1
        self.check_division(20172188947443, 615611397)
        self.check_division(1020908530270155025, 950795710)
        self.check_division(128589565723112408, 736393718)
        self.check_division(609919780285761575, 18613274546784)
        # 15-bit cases that require the post-subtraction correction step
        self.check_division(710031681576388032, 26769404391308)
        self.check_division(1933622614268221, 30212853348836)



    eleza test_karatsuba(self):
        digits = list(range(1, 5)) + list(range(KARATSUBA_CUTOFF,
                                                KARATSUBA_CUTOFF + 10))
        digits.extend([KARATSUBA_CUTOFF * 10, KARATSUBA_CUTOFF * 100])

        bits = [digit * SHIFT kila digit kwenye digits]

        # Test products of long strings of 1 bits -- (2**x-1)*(2**y-1) ==
        # 2**(x+y) - 2**x - 2**y + 1, so the proper result ni easy to check.
        kila abits kwenye bits:
            a = (1 << abits) - 1
            kila bbits kwenye bits:
                ikiwa bbits < abits:
                    endelea
                ukijumuisha self.subTest(abits=abits, bbits=bbits):
                    b = (1 << bbits) - 1
                    x = a * b
                    y = ((1 << (abits + bbits)) -
                         (1 << abits) -
                         (1 << bbits) +
                         1)
                    self.assertEqual(x, y)

    eleza check_bitop_identities_1(self, x):
        eq = self.assertEqual
        ukijumuisha self.subTest(x=x):
            eq(x & 0, 0)
            eq(x | 0, x)
            eq(x ^ 0, x)
            eq(x & -1, x)
            eq(x | -1, -1)
            eq(x ^ -1, ~x)
            eq(x, ~~x)
            eq(x & x, x)
            eq(x | x, x)
            eq(x ^ x, 0)
            eq(x & ~x, 0)
            eq(x | ~x, -1)
            eq(x ^ ~x, -1)
            eq(-x, 1 + ~x)
            eq(-x, ~(x-1))
        kila n kwenye range(2*SHIFT):
            p2 = 2 ** n
            ukijumuisha self.subTest(x=x, n=n, p2=p2):
                eq(x << n >> n, x)
                eq(x // p2, x >> n)
                eq(x * p2, x << n)
                eq(x & -p2, x >> n << n)
                eq(x & -p2, x & ~(p2 - 1))

    eleza check_bitop_identities_2(self, x, y):
        eq = self.assertEqual
        ukijumuisha self.subTest(x=x, y=y):
            eq(x & y, y & x)
            eq(x | y, y | x)
            eq(x ^ y, y ^ x)
            eq(x ^ y ^ x, y)
            eq(x & y, ~(~x | ~y))
            eq(x | y, ~(~x & ~y))
            eq(x ^ y, (x | y) & ~(x & y))
            eq(x ^ y, (x & ~y) | (~x & y))
            eq(x ^ y, (x | y) & (~x | ~y))

    eleza check_bitop_identities_3(self, x, y, z):
        eq = self.assertEqual
        ukijumuisha self.subTest(x=x, y=y, z=z):
            eq((x & y) & z, x & (y & z))
            eq((x | y) | z, x | (y | z))
            eq((x ^ y) ^ z, x ^ (y ^ z))
            eq(x & (y | z), (x & y) | (x & z))
            eq(x | (y & z), (x | y) & (x | z))

    eleza test_bitop_identities(self):
        kila x kwenye special:
            self.check_bitop_identities_1(x)
        digits = range(1, MAXDIGITS+1)
        kila lenx kwenye digits:
            x = self.getran(lenx)
            self.check_bitop_identities_1(x)
            kila leny kwenye digits:
                y = self.getran(leny)
                self.check_bitop_identities_2(x, y)
                self.check_bitop_identities_3(x, y, self.getran((lenx + leny)//2))

    eleza slow_format(self, x, base):
        digits = []
        sign = 0
        ikiwa x < 0:
            sign, x = 1, -x
        wakati x:
            x, r = divmod(x, base)
            digits.append(int(r))
        digits.reverse()
        digits = digits ama [0]
        rudisha '-'[:sign] + \
               {2: '0b', 8: '0o', 10: '', 16: '0x'}[base] + \
               "".join("0123456789abcdef"[i] kila i kwenye digits)

    eleza check_format_1(self, x):
        kila base, mapper kwenye (2, bin), (8, oct), (10, str), (10, repr), (16, hex):
            got = mapper(x)
            ukijumuisha self.subTest(x=x, mapper=mapper.__name__):
                expected = self.slow_format(x, base)
                self.assertEqual(got, expected)
            ukijumuisha self.subTest(got=got):
                self.assertEqual(int(got, 0), x)

    eleza test_format(self):
        kila x kwenye special:
            self.check_format_1(x)
        kila i kwenye range(10):
            kila lenx kwenye range(1, MAXDIGITS+1):
                x = self.getran(lenx)
                self.check_format_1(x)

    eleza test_long(self):
        # Check conversions kutoka string
        LL = [
                ('1' + '0'*20, 10**20),
                ('1' + '0'*100, 10**100)
        ]
        kila s, v kwenye LL:
            kila sign kwenye "", "+", "-":
                kila prefix kwenye "", " ", "\t", "  \t\t  ":
                    ss = prefix + sign + s
                    vv = v
                    ikiwa sign == "-" na v ni sio ValueError:
                        vv = -v
                    jaribu:
                        self.assertEqual(int(ss), vv)
                    tatizo ValueError:
                        pita

        # trailing L should no longer be accepted...
        self.assertRaises(ValueError, int, '123L')
        self.assertRaises(ValueError, int, '123l')
        self.assertRaises(ValueError, int, '0L')
        self.assertRaises(ValueError, int, '-37L')
        self.assertRaises(ValueError, int, '0x32L', 16)
        self.assertRaises(ValueError, int, '1L', 21)
        # ... but it's just a normal digit ikiwa base >= 22
        self.assertEqual(int('1L', 22), 43)

        # tests ukijumuisha base 0
        self.assertEqual(int('000', 0), 0)
        self.assertEqual(int('0o123', 0), 83)
        self.assertEqual(int('0x123', 0), 291)
        self.assertEqual(int('0b100', 0), 4)
        self.assertEqual(int(' 0O123   ', 0), 83)
        self.assertEqual(int(' 0X123  ', 0), 291)
        self.assertEqual(int(' 0B100 ', 0), 4)
        self.assertEqual(int('0', 0), 0)
        self.assertEqual(int('+0', 0), 0)
        self.assertEqual(int('-0', 0), 0)
        self.assertEqual(int('00', 0), 0)
        self.assertRaises(ValueError, int, '08', 0)
        self.assertRaises(ValueError, int, '-012395', 0)

        # invalid bases
        invalid_bases = [-909,
                          2**31-1, 2**31, -2**31, -2**31-1,
                          2**63-1, 2**63, -2**63, -2**63-1,
                          2**100, -2**100,
                          ]
        kila base kwenye invalid_bases:
            self.assertRaises(ValueError, int, '42', base)

        # Invalid unicode string
        # See bpo-34087
        self.assertRaises(ValueError, int, '\u3053\u3093\u306b\u3061\u306f')


    eleza test_conversion(self):

        kundi JustLong:
            # test that __long__ no longer used kwenye 3.x
            eleza __long__(self):
                rudisha 42
        self.assertRaises(TypeError, int, JustLong())

        kundi LongTrunc:
            # __long__ should be ignored kwenye 3.x
            eleza __long__(self):
                rudisha 42
            eleza __trunc__(self):
                rudisha 1729
        self.assertEqual(int(LongTrunc()), 1729)

    eleza check_float_conversion(self, n):
        # Check that int -> float conversion behaviour matches
        # that of the pure Python version above.
        jaribu:
            actual = float(n)
        tatizo OverflowError:
            actual = 'overflow'

        jaribu:
            expected = int_to_float(n)
        tatizo OverflowError:
            expected = 'overflow'

        msg = ("Error kwenye conversion of integer {} to float.  "
               "Got {}, expected {}.".format(n, actual, expected))
        self.assertEqual(actual, expected, msg)

    @support.requires_IEEE_754
    eleza test_float_conversion(self):

        exact_values = [0, 1, 2,
                         2**53-3,
                         2**53-2,
                         2**53-1,
                         2**53,
                         2**53+2,
                         2**54-4,
                         2**54-2,
                         2**54,
                         2**54+4]
        kila x kwenye exact_values:
            self.assertEqual(float(x), x)
            self.assertEqual(float(-x), -x)

        # test round-half-even
        kila x, y kwenye [(1, 0), (2, 2), (3, 4), (4, 4), (5, 4), (6, 6), (7, 8)]:
            kila p kwenye range(15):
                self.assertEqual(int(float(2**p*(2**53+x))), 2**p*(2**53+y))

        kila x, y kwenye [(0, 0), (1, 0), (2, 0), (3, 4), (4, 4), (5, 4), (6, 8),
                     (7, 8), (8, 8), (9, 8), (10, 8), (11, 12), (12, 12),
                     (13, 12), (14, 16), (15, 16)]:
            kila p kwenye range(15):
                self.assertEqual(int(float(2**p*(2**54+x))), 2**p*(2**54+y))

        # behaviour near extremes of floating-point range
        int_dbl_max = int(DBL_MAX)
        top_power = 2**DBL_MAX_EXP
        halfway = (int_dbl_max + top_power)//2
        self.assertEqual(float(int_dbl_max), DBL_MAX)
        self.assertEqual(float(int_dbl_max+1), DBL_MAX)
        self.assertEqual(float(halfway-1), DBL_MAX)
        self.assertRaises(OverflowError, float, halfway)
        self.assertEqual(float(1-halfway), -DBL_MAX)
        self.assertRaises(OverflowError, float, -halfway)
        self.assertRaises(OverflowError, float, top_power-1)
        self.assertRaises(OverflowError, float, top_power)
        self.assertRaises(OverflowError, float, top_power+1)
        self.assertRaises(OverflowError, float, 2*top_power-1)
        self.assertRaises(OverflowError, float, 2*top_power)
        self.assertRaises(OverflowError, float, top_power*top_power)

        kila p kwenye range(100):
            x = 2**p * (2**53 + 1) + 1
            y = 2**p * (2**53 + 2)
            self.assertEqual(int(float(x)), y)

            x = 2**p * (2**53 + 1)
            y = 2**p * 2**53
            self.assertEqual(int(float(x)), y)

        # Compare builtin float conversion ukijumuisha pure Python int_to_float
        # function above.
        test_values = [
            int_dbl_max-1, int_dbl_max, int_dbl_max+1,
            halfway-1, halfway, halfway + 1,
            top_power-1, top_power, top_power+1,
            2*top_power-1, 2*top_power, top_power*top_power,
        ]
        test_values.extend(exact_values)
        kila p kwenye range(-4, 8):
            kila x kwenye range(-128, 128):
                test_values.append(2**(p+53) + x)
        kila value kwenye test_values:
            self.check_float_conversion(value)
            self.check_float_conversion(-value)

    eleza test_float_overflow(self):
        kila x kwenye -2.0, -1.0, 0.0, 1.0, 2.0:
            self.assertEqual(float(int(x)), x)

        shuge = '12345' * 120
        huge = 1 << 30000
        mhuge = -huge
        namespace = {'huge': huge, 'mhuge': mhuge, 'shuge': shuge, 'math': math}
        kila test kwenye ["float(huge)", "float(mhuge)",
                     "complex(huge)", "complex(mhuge)",
                     "complex(huge, 1)", "complex(mhuge, 1)",
                     "complex(1, huge)", "complex(1, mhuge)",
                     "1. + huge", "huge + 1.", "1. + mhuge", "mhuge + 1.",
                     "1. - huge", "huge - 1.", "1. - mhuge", "mhuge - 1.",
                     "1. * huge", "huge * 1.", "1. * mhuge", "mhuge * 1.",
                     "1. // huge", "huge // 1.", "1. // mhuge", "mhuge // 1.",
                     "1. / huge", "huge / 1.", "1. / mhuge", "mhuge / 1.",
                     "1. ** huge", "huge ** 1.", "1. ** mhuge", "mhuge ** 1.",
                     "math.sin(huge)", "math.sin(mhuge)",
                     "math.sqrt(huge)", "math.sqrt(mhuge)", # should do better
                     # math.floor() of an int returns an int now
                     ##"math.floor(huge)", "math.floor(mhuge)",
                     ]:

            self.assertRaises(OverflowError, eval, test, namespace)

        # XXX Perhaps float(shuge) can ashiria OverflowError on some box?
        # The comparison should not.
        self.assertNotEqual(float(shuge), int(shuge),
            "float(shuge) should sio equal int(shuge)")

    eleza test_logs(self):
        LOG10E = math.log10(math.e)

        kila exp kwenye list(range(10)) + [100, 1000, 10000]:
            value = 10 ** exp
            log10 = math.log10(value)
            self.assertAlmostEqual(log10, exp)

            # log10(value) == exp, so log(value) == log10(value)/log10(e) ==
            # exp/LOG10E
            expected = exp / LOG10E
            log = math.log(value)
            self.assertAlmostEqual(log, expected)

        kila bad kwenye -(1 << 10000), -2, 0:
            self.assertRaises(ValueError, math.log, bad)
            self.assertRaises(ValueError, math.log10, bad)

    eleza test_mixed_compares(self):
        eq = self.assertEqual

        # We're mostly concerned ukijumuisha that mixing floats na ints does the
        # right stuff, even when ints are too large to fit kwenye a float.
        # The safest way to check the results ni to use an entirely different
        # method, which we do here via a skeletal rational kundi (which
        # represents all Python ints na floats exactly).
        kundi Rat:
            eleza __init__(self, value):
                ikiwa isinstance(value, int):
                    self.n = value
                    self.d = 1
                lasivyo isinstance(value, float):
                    # Convert to exact rational equivalent.
                    f, e = math.frexp(abs(value))
                    assert f == 0 ama 0.5 <= f < 1.0
                    # |value| = f * 2**e exactly

                    # Suck up CHUNK bits at a time; 28 ni enough so that we suck
                    # up all bits kwenye 2 iterations kila all known binary double-
                    # precision formats, na small enough to fit kwenye an int.
                    CHUNK = 28
                    top = 0
                    # invariant: |value| = (top + f) * 2**e exactly
                    wakati f:
                        f = math.ldexp(f, CHUNK)
                        digit = int(f)
                        assert digit >> CHUNK == 0
                        top = (top << CHUNK) | digit
                        f -= digit
                        assert 0.0 <= f < 1.0
                        e -= CHUNK

                    # Now |value| = top * 2**e exactly.
                    ikiwa e >= 0:
                        n = top << e
                        d = 1
                    isipokua:
                        n = top
                        d = 1 << -e
                    ikiwa value < 0:
                        n = -n
                    self.n = n
                    self.d = d
                    assert float(n) / float(d) == value
                isipokua:
                    ashiria TypeError("can't deal ukijumuisha %r" % value)

            eleza _cmp__(self, other):
                ikiwa sio isinstance(other, Rat):
                    other = Rat(other)
                x, y = self.n * other.d, self.d * other.n
                rudisha (x > y) - (x < y)
            eleza __eq__(self, other):
                rudisha self._cmp__(other) == 0
            eleza __ge__(self, other):
                rudisha self._cmp__(other) >= 0
            eleza __gt__(self, other):
                rudisha self._cmp__(other) > 0
            eleza __le__(self, other):
                rudisha self._cmp__(other) <= 0
            eleza __lt__(self, other):
                rudisha self._cmp__(other) < 0

        cases = [0, 0.001, 0.99, 1.0, 1.5, 1e20, 1e200]
        # 2**48 ni an important boundary kwenye the internals.  2**53 ni an
        # important boundary kila IEEE double precision.
        kila t kwenye 2.0**48, 2.0**50, 2.0**53:
            cases.extend([t - 1.0, t - 0.3, t, t + 0.3, t + 1.0,
                          int(t-1), int(t), int(t+1)])
        cases.extend([0, 1, 2, sys.maxsize, float(sys.maxsize)])
        # 1 << 20000 should exceed all double formats.  int(1e200) ni to
        # check that we get equality ukijumuisha 1e200 above.
        t = int(1e200)
        cases.extend([0, 1, 2, 1 << 20000, t-1, t, t+1])
        cases.extend([-x kila x kwenye cases])
        kila x kwenye cases:
            Rx = Rat(x)
            kila y kwenye cases:
                Ry = Rat(y)
                Rcmp = (Rx > Ry) - (Rx < Ry)
                ukijumuisha self.subTest(x=x, y=y, Rcmp=Rcmp):
                    xycmp = (x > y) - (x < y)
                    eq(Rcmp, xycmp)
                    eq(x == y, Rcmp == 0)
                    eq(x != y, Rcmp != 0)
                    eq(x < y, Rcmp < 0)
                    eq(x <= y, Rcmp <= 0)
                    eq(x > y, Rcmp > 0)
                    eq(x >= y, Rcmp >= 0)

    eleza test__format__(self):
        self.assertEqual(format(123456789, 'd'), '123456789')
        self.assertEqual(format(123456789, 'd'), '123456789')
        self.assertEqual(format(123456789, ','), '123,456,789')
        self.assertEqual(format(123456789, '_'), '123_456_789')

        # sign na aligning are interdependent
        self.assertEqual(format(1, "-"), '1')
        self.assertEqual(format(-1, "-"), '-1')
        self.assertEqual(format(1, "-3"), '  1')
        self.assertEqual(format(-1, "-3"), ' -1')
        self.assertEqual(format(1, "+3"), ' +1')
        self.assertEqual(format(-1, "+3"), ' -1')
        self.assertEqual(format(1, " 3"), '  1')
        self.assertEqual(format(-1, " 3"), ' -1')
        self.assertEqual(format(1, " "), ' 1')
        self.assertEqual(format(-1, " "), '-1')

        # hex
        self.assertEqual(format(3, "x"), "3")
        self.assertEqual(format(3, "X"), "3")
        self.assertEqual(format(1234, "x"), "4d2")
        self.assertEqual(format(-1234, "x"), "-4d2")
        self.assertEqual(format(1234, "8x"), "     4d2")
        self.assertEqual(format(-1234, "8x"), "    -4d2")
        self.assertEqual(format(1234, "x"), "4d2")
        self.assertEqual(format(-1234, "x"), "-4d2")
        self.assertEqual(format(-3, "x"), "-3")
        self.assertEqual(format(-3, "X"), "-3")
        self.assertEqual(format(int('be', 16), "x"), "be")
        self.assertEqual(format(int('be', 16), "X"), "BE")
        self.assertEqual(format(-int('be', 16), "x"), "-be")
        self.assertEqual(format(-int('be', 16), "X"), "-BE")
        self.assertRaises(ValueError, format, 1234567890, ',x')
        self.assertEqual(format(1234567890, '_x'), '4996_02d2')
        self.assertEqual(format(1234567890, '_X'), '4996_02D2')

        # octal
        self.assertEqual(format(3, "o"), "3")
        self.assertEqual(format(-3, "o"), "-3")
        self.assertEqual(format(1234, "o"), "2322")
        self.assertEqual(format(-1234, "o"), "-2322")
        self.assertEqual(format(1234, "-o"), "2322")
        self.assertEqual(format(-1234, "-o"), "-2322")
        self.assertEqual(format(1234, " o"), " 2322")
        self.assertEqual(format(-1234, " o"), "-2322")
        self.assertEqual(format(1234, "+o"), "+2322")
        self.assertEqual(format(-1234, "+o"), "-2322")
        self.assertRaises(ValueError, format, 1234567890, ',o')
        self.assertEqual(format(1234567890, '_o'), '111_4540_1322')

        # binary
        self.assertEqual(format(3, "b"), "11")
        self.assertEqual(format(-3, "b"), "-11")
        self.assertEqual(format(1234, "b"), "10011010010")
        self.assertEqual(format(-1234, "b"), "-10011010010")
        self.assertEqual(format(1234, "-b"), "10011010010")
        self.assertEqual(format(-1234, "-b"), "-10011010010")
        self.assertEqual(format(1234, " b"), " 10011010010")
        self.assertEqual(format(-1234, " b"), "-10011010010")
        self.assertEqual(format(1234, "+b"), "+10011010010")
        self.assertEqual(format(-1234, "+b"), "-10011010010")
        self.assertRaises(ValueError, format, 1234567890, ',b')
        self.assertEqual(format(12345, '_b'), '11_0000_0011_1001')

        # make sure these are errors
        self.assertRaises(ValueError, format, 3, "1.3")  # precision disallowed
        self.assertRaises(ValueError, format, 3, "_c")   # underscore,
        self.assertRaises(ValueError, format, 3, ",c")   # comma, na
        self.assertRaises(ValueError, format, 3, "+c")   # sign sio allowed
                                                         # ukijumuisha 'c'

        self.assertRaisesRegex(ValueError, 'Cansio specify both', format, 3, '_,')
        self.assertRaisesRegex(ValueError, 'Cansio specify both', format, 3, ',_')
        self.assertRaisesRegex(ValueError, 'Cansio specify both', format, 3, '_,d')
        self.assertRaisesRegex(ValueError, 'Cansio specify both', format, 3, ',_d')

        self.assertRaisesRegex(ValueError, "Cansio specify ',' ukijumuisha 's'", format, 3, ',s')
        self.assertRaisesRegex(ValueError, "Cansio specify '_' ukijumuisha 's'", format, 3, '_s')

        # ensure that only int na float type specifiers work
        kila format_spec kwenye ([chr(x) kila x kwenye range(ord('a'), ord('z')+1)] +
                            [chr(x) kila x kwenye range(ord('A'), ord('Z')+1)]):
            ikiwa sio format_spec kwenye 'bcdoxXeEfFgGn%':
                self.assertRaises(ValueError, format, 0, format_spec)
                self.assertRaises(ValueError, format, 1, format_spec)
                self.assertRaises(ValueError, format, -1, format_spec)
                self.assertRaises(ValueError, format, 2**100, format_spec)
                self.assertRaises(ValueError, format, -(2**100), format_spec)

        # ensure that float type specifiers work; format converts
        #  the int to a float
        kila format_spec kwenye 'eEfFgG%':
            kila value kwenye [0, 1, -1, 100, -100, 1234567890, -1234567890]:
                self.assertEqual(format(value, format_spec),
                                 format(float(value), format_spec))

    eleza test_nan_inf(self):
        self.assertRaises(OverflowError, int, float('inf'))
        self.assertRaises(OverflowError, int, float('-inf'))
        self.assertRaises(ValueError, int, float('nan'))

    eleza test_mod_division(self):
        ukijumuisha self.assertRaises(ZeroDivisionError):
            _ = 1 % 0

        self.assertEqual(13 % 10, 3)
        self.assertEqual(-13 % 10, 7)
        self.assertEqual(13 % -10, -7)
        self.assertEqual(-13 % -10, -3)

        self.assertEqual(12 % 4, 0)
        self.assertEqual(-12 % 4, 0)
        self.assertEqual(12 % -4, 0)
        self.assertEqual(-12 % -4, 0)

    eleza test_true_division(self):
        huge = 1 << 40000
        mhuge = -huge
        self.assertEqual(huge / huge, 1.0)
        self.assertEqual(mhuge / mhuge, 1.0)
        self.assertEqual(huge / mhuge, -1.0)
        self.assertEqual(mhuge / huge, -1.0)
        self.assertEqual(1 / huge, 0.0)
        self.assertEqual(1 / huge, 0.0)
        self.assertEqual(1 / mhuge, 0.0)
        self.assertEqual(1 / mhuge, 0.0)
        self.assertEqual((666 * huge + (huge >> 1)) / huge, 666.5)
        self.assertEqual((666 * mhuge + (mhuge >> 1)) / mhuge, 666.5)
        self.assertEqual((666 * huge + (huge >> 1)) / mhuge, -666.5)
        self.assertEqual((666 * mhuge + (mhuge >> 1)) / huge, -666.5)
        self.assertEqual(huge / (huge << 1), 0.5)
        self.assertEqual((1000000 * huge) / huge, 1000000)

        namespace = {'huge': huge, 'mhuge': mhuge}

        kila overflow kwenye ["float(huge)", "float(mhuge)",
                         "huge / 1", "huge / 2", "huge / -1", "huge / -2",
                         "mhuge / 100", "mhuge / 200"]:
            self.assertRaises(OverflowError, eval, overflow, namespace)

        kila underflow kwenye ["1 / huge", "2 / huge", "-1 / huge", "-2 / huge",
                         "100 / mhuge", "200 / mhuge"]:
            result = eval(underflow, namespace)
            self.assertEqual(result, 0.0,
                             "expected underflow to 0 kutoka %r" % underflow)

        kila zero kwenye ["huge / 0", "mhuge / 0"]:
            self.assertRaises(ZeroDivisionError, eval, zero, namespace)

    eleza test_floordiv(self):
        ukijumuisha self.assertRaises(ZeroDivisionError):
            _ = 1 // 0

        self.assertEqual(2 // 3, 0)
        self.assertEqual(2 // -3, -1)
        self.assertEqual(-2 // 3, -1)
        self.assertEqual(-2 // -3, 0)

        self.assertEqual(-11 // -3, 3)
        self.assertEqual(-11 // 3, -4)
        self.assertEqual(11 // -3, -4)
        self.assertEqual(11 // 3, 3)

        self.assertEqual(-12 // -3, 4)
        self.assertEqual(-12 // 3, -4)
        self.assertEqual(12 // -3, -4)
        self.assertEqual(12 // 3, 4)

    eleza check_truediv(self, a, b, skip_small=Kweli):
        """Verify that the result of a/b ni correctly rounded, by
        comparing it ukijumuisha a pure Python implementation of correctly
        rounded division.  b should be nonzero."""

        # skip check kila small a na b: kwenye this case, the current
        # implementation converts the arguments to float directly na
        # then applies a float division.  This can give doubly-rounded
        # results on x87-using machines (particularly 32-bit Linux).
        ikiwa skip_small na max(abs(a), abs(b)) < 2**DBL_MANT_DIG:
            rudisha

        jaribu:
            # use repr so that we can distinguish between -0.0 na 0.0
            expected = repr(truediv(a, b))
        tatizo OverflowError:
            expected = 'overflow'
        tatizo ZeroDivisionError:
            expected = 'zerodivision'

        jaribu:
            got = repr(a / b)
        tatizo OverflowError:
            got = 'overflow'
        tatizo ZeroDivisionError:
            got = 'zerodivision'

        self.assertEqual(expected, got, "Incorrectly rounded division {}/{}: "
                         "expected {}, got {}".format(a, b, expected, got))

    @support.requires_IEEE_754
    eleza test_correctly_rounded_true_division(self):
        # more stringent tests than those above, checking that the
        # result of true division of ints ni always correctly rounded.
        # This test should probably be considered CPython-specific.

        # Exercise all the code paths sio inolving Gb-sized ints.
        # ... divisions involving zero
        self.check_truediv(123, 0)
        self.check_truediv(-456, 0)
        self.check_truediv(0, 3)
        self.check_truediv(0, -3)
        self.check_truediv(0, 0)
        # ... overflow ama underflow by large margin
        self.check_truediv(671 * 12345 * 2**DBL_MAX_EXP, 12345)
        self.check_truediv(12345, 345678 * 2**(DBL_MANT_DIG - DBL_MIN_EXP))
        # ... a much larger ama smaller than b
        self.check_truediv(12345*2**100, 98765)
        self.check_truediv(12345*2**30, 98765*7**81)
        # ... a / b near a boundary: one of 1, 2**DBL_MANT_DIG, 2**DBL_MIN_EXP,
        #                 2**DBL_MAX_EXP, 2**(DBL_MIN_EXP-DBL_MANT_DIG)
        bases = (0, DBL_MANT_DIG, DBL_MIN_EXP,
                 DBL_MAX_EXP, DBL_MIN_EXP - DBL_MANT_DIG)
        kila base kwenye bases:
            kila exp kwenye range(base - 15, base + 15):
                self.check_truediv(75312*2**max(exp, 0), 69187*2**max(-exp, 0))
                self.check_truediv(69187*2**max(exp, 0), 75312*2**max(-exp, 0))

        # overflow corner case
        kila m kwenye [1, 2, 7, 17, 12345, 7**100,
                  -1, -2, -5, -23, -67891, -41**50]:
            kila n kwenye range(-10, 10):
                self.check_truediv(m*DBL_MIN_OVERFLOW + n, m)
                self.check_truediv(m*DBL_MIN_OVERFLOW + n, -m)

        # check detection of inexactness kwenye shifting stage
        kila n kwenye range(250):
            # (2**DBL_MANT_DIG+1)/(2**DBL_MANT_DIG) lies halfway
            # between two representable floats, na would usually be
            # rounded down under round-half-to-even.  The tiniest of
            # additions to the numerator should cause it to be rounded
            # up instead.
            self.check_truediv((2**DBL_MANT_DIG + 1)*12345*2**200 + 2**n,
                           2**DBL_MANT_DIG*12345)

        # 1/2731 ni one of the smallest division cases that's subject
        # to double rounding on IEEE 754 machines working internally with
        # 64-bit precision.  On such machines, the next check would fail,
        # were it sio explicitly skipped kwenye check_truediv.
        self.check_truediv(1, 2731)

        # a particularly bad case kila the old algorithm:  gives an
        # error of close to 3.5 ulps.
        self.check_truediv(295147931372582273023, 295147932265116303360)
        kila i kwenye range(1000):
            self.check_truediv(10**(i+1), 10**i)
            self.check_truediv(10**i, 10**(i+1))

        # test round-half-to-even behaviour, normal result
        kila m kwenye [1, 2, 4, 7, 8, 16, 17, 32, 12345, 7**100,
                  -1, -2, -5, -23, -67891, -41**50]:
            kila n kwenye range(-10, 10):
                self.check_truediv(2**DBL_MANT_DIG*m + n, m)

        # test round-half-to-even, subnormal result
        kila n kwenye range(-20, 20):
            self.check_truediv(n, 2**1076)

        # largeish random divisions: a/b where |a| <= |b| <=
        # 2*|a|; |ans| ni between 0.5 na 1.0, so error should
        # always be bounded by 2**-54 ukijumuisha equality possible only
        # ikiwa the least significant bit of q=ans*2**53 ni zero.
        kila M kwenye [10**10, 10**100, 10**1000]:
            kila i kwenye range(1000):
                a = random.randrange(1, M)
                b = random.randrange(a, 2*a+1)
                self.check_truediv(a, b)
                self.check_truediv(-a, b)
                self.check_truediv(a, -b)
                self.check_truediv(-a, -b)

        # na some (genuinely) random tests
        kila _ kwenye range(10000):
            a_bits = random.randrange(1000)
            b_bits = random.randrange(1, 1000)
            x = random.randrange(2**a_bits)
            y = random.randrange(1, 2**b_bits)
            self.check_truediv(x, y)
            self.check_truediv(x, -y)
            self.check_truediv(-x, y)
            self.check_truediv(-x, -y)

    eleza test_negative_shift_count(self):
        ukijumuisha self.assertRaises(ValueError):
            42 << -3
        ukijumuisha self.assertRaises(ValueError):
            42 << -(1 << 1000)
        ukijumuisha self.assertRaises(ValueError):
            42 >> -3
        ukijumuisha self.assertRaises(ValueError):
            42 >> -(1 << 1000)

    eleza test_lshift_of_zero(self):
        self.assertEqual(0 << 0, 0)
        self.assertEqual(0 << 10, 0)
        ukijumuisha self.assertRaises(ValueError):
            0 << -1
        self.assertEqual(0 << (1 << 1000), 0)
        ukijumuisha self.assertRaises(ValueError):
            0 << -(1 << 1000)

    @support.cpython_only
    eleza test_huge_lshift_of_zero(self):
        # Shouldn't try to allocate memory kila a huge shift. See issue #27870.
        # Other implementations may have a different boundary kila overflow,
        # ama sio ashiria at all.
        self.assertEqual(0 << sys.maxsize, 0)
        self.assertEqual(0 << (sys.maxsize + 1), 0)

    @support.cpython_only
    @support.bigmemtest(sys.maxsize + 1000, memuse=2/15 * 2, dry_run=Uongo)
    eleza test_huge_lshift(self, size):
        self.assertEqual(1 << (sys.maxsize + 1000), 1 << 1000 << sys.maxsize)

    eleza test_huge_rshift(self):
        self.assertEqual(42 >> (1 << 1000), 0)
        self.assertEqual((-42) >> (1 << 1000), -1)

    @support.cpython_only
    @support.bigmemtest(sys.maxsize + 500, memuse=2/15, dry_run=Uongo)
    eleza test_huge_rshift_of_huge(self, size):
        huge = ((1 << 500) + 11) << sys.maxsize
        self.assertEqual(huge >> (sys.maxsize + 1), (1 << 499) + 5)
        self.assertEqual(huge >> (sys.maxsize + 1000), 0)

    eleza test_small_ints(self):
        kila i kwenye range(-5, 257):
            self.assertIs(i, i + 0)
            self.assertIs(i, i * 1)
            self.assertIs(i, i - 0)
            self.assertIs(i, i // 1)
            self.assertIs(i, i & -1)
            self.assertIs(i, i | 0)
            self.assertIs(i, i ^ 0)
            self.assertIs(i, ~~i)
            self.assertIs(i, i**1)
            self.assertIs(i, int(str(i)))
            self.assertIs(i, i<<2>>2, str(i))
        # corner cases
        i = 1 << 70
        self.assertIs(i - i, 0)
        self.assertIs(0 * i, 0)

    eleza test_bit_length(self):
        tiny = 1e-10
        kila x kwenye range(-65000, 65000):
            k = x.bit_length()
            # Check equivalence ukijumuisha Python version
            self.assertEqual(k, len(bin(x).lstrip('-0b')))
            # Behaviour kama specified kwenye the docs
            ikiwa x != 0:
                self.assertKweli(2**(k-1) <= abs(x) < 2**k)
            isipokua:
                self.assertEqual(k, 0)
            # Alternative definition: x.bit_length() == 1 + floor(log_2(x))
            ikiwa x != 0:
                # When x ni an exact power of 2, numeric errors can
                # cause floor(log(x)/log(2)) to be one too small; for
                # small x this can be fixed by adding a small quantity
                # to the quotient before taking the floor.
                self.assertEqual(k, 1 + math.floor(
                        math.log(abs(x))/math.log(2) + tiny))

        self.assertEqual((0).bit_length(), 0)
        self.assertEqual((1).bit_length(), 1)
        self.assertEqual((-1).bit_length(), 1)
        self.assertEqual((2).bit_length(), 2)
        self.assertEqual((-2).bit_length(), 2)
        kila i kwenye [2, 3, 15, 16, 17, 31, 32, 33, 63, 64, 234]:
            a = 2**i
            self.assertEqual((a-1).bit_length(), i)
            self.assertEqual((1-a).bit_length(), i)
            self.assertEqual((a).bit_length(), i+1)
            self.assertEqual((-a).bit_length(), i+1)
            self.assertEqual((a+1).bit_length(), i+1)
            self.assertEqual((-a-1).bit_length(), i+1)

    eleza test_round(self):
        # check round-half-even algorithm. For round to nearest ten;
        # rounding map ni invariant under adding multiples of 20
        test_dict = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0,
                     6:10, 7:10, 8:10, 9:10, 10:10, 11:10, 12:10, 13:10, 14:10,
                     15:20, 16:20, 17:20, 18:20, 19:20}
        kila offset kwenye range(-520, 520, 20):
            kila k, v kwenye test_dict.items():
                got = round(k+offset, -1)
                expected = v+offset
                self.assertEqual(got, expected)
                self.assertIs(type(got), int)

        # larger second argument
        self.assertEqual(round(-150, -2), -200)
        self.assertEqual(round(-149, -2), -100)
        self.assertEqual(round(-51, -2), -100)
        self.assertEqual(round(-50, -2), 0)
        self.assertEqual(round(-49, -2), 0)
        self.assertEqual(round(-1, -2), 0)
        self.assertEqual(round(0, -2), 0)
        self.assertEqual(round(1, -2), 0)
        self.assertEqual(round(49, -2), 0)
        self.assertEqual(round(50, -2), 0)
        self.assertEqual(round(51, -2), 100)
        self.assertEqual(round(149, -2), 100)
        self.assertEqual(round(150, -2), 200)
        self.assertEqual(round(250, -2), 200)
        self.assertEqual(round(251, -2), 300)
        self.assertEqual(round(172500, -3), 172000)
        self.assertEqual(round(173500, -3), 174000)
        self.assertEqual(round(31415926535, -1), 31415926540)
        self.assertEqual(round(31415926535, -2), 31415926500)
        self.assertEqual(round(31415926535, -3), 31415927000)
        self.assertEqual(round(31415926535, -4), 31415930000)
        self.assertEqual(round(31415926535, -5), 31415900000)
        self.assertEqual(round(31415926535, -6), 31416000000)
        self.assertEqual(round(31415926535, -7), 31420000000)
        self.assertEqual(round(31415926535, -8), 31400000000)
        self.assertEqual(round(31415926535, -9), 31000000000)
        self.assertEqual(round(31415926535, -10), 30000000000)
        self.assertEqual(round(31415926535, -11), 0)
        self.assertEqual(round(31415926535, -12), 0)
        self.assertEqual(round(31415926535, -999), 0)

        # should get correct results even kila huge inputs
        kila k kwenye range(10, 100):
            got = round(10**k + 324678, -3)
            expect = 10**k + 325000
            self.assertEqual(got, expect)
            self.assertIs(type(got), int)

        # nonnegative second argument: round(x, n) should just rudisha x
        kila n kwenye range(5):
            kila i kwenye range(100):
                x = random.randrange(-10000, 10000)
                got = round(x, n)
                self.assertEqual(got, x)
                self.assertIs(type(got), int)
        kila huge_n kwenye 2**31-1, 2**31, 2**63-1, 2**63, 2**100, 10**100:
            self.assertEqual(round(8979323, huge_n), 8979323)

        # omitted second argument
        kila i kwenye range(100):
            x = random.randrange(-10000, 10000)
            got = round(x)
            self.assertEqual(got, x)
            self.assertIs(type(got), int)

        # bad second argument
        bad_exponents = ('brian', 2.0, 0j)
        kila e kwenye bad_exponents:
            self.assertRaises(TypeError, round, 3, e)

    eleza test_to_bytes(self):
        eleza check(tests, byteorder, signed=Uongo):
            kila test, expected kwenye tests.items():
                jaribu:
                    self.assertEqual(
                        test.to_bytes(len(expected), byteorder, signed=signed),
                        expected)
                tatizo Exception kama err:
                    ashiria AssertionError(
                        "failed to convert {0} ukijumuisha byteorder={1} na signed={2}"
                        .format(test, byteorder, signed)) kutoka err

        # Convert integers to signed big-endian byte arrays.
        tests1 = {
            0: b'\x00',
            1: b'\x01',
            -1: b'\xff',
            -127: b'\x81',
            -128: b'\x80',
            -129: b'\xff\x7f',
            127: b'\x7f',
            129: b'\x00\x81',
            -255: b'\xff\x01',
            -256: b'\xff\x00',
            255: b'\x00\xff',
            256: b'\x01\x00',
            32767: b'\x7f\xff',
            -32768: b'\xff\x80\x00',
            65535: b'\x00\xff\xff',
            -65536: b'\xff\x00\x00',
            -8388608: b'\x80\x00\x00'
        }
        check(tests1, 'big', signed=Kweli)

        # Convert integers to signed little-endian byte arrays.
        tests2 = {
            0: b'\x00',
            1: b'\x01',
            -1: b'\xff',
            -127: b'\x81',
            -128: b'\x80',
            -129: b'\x7f\xff',
            127: b'\x7f',
            129: b'\x81\x00',
            -255: b'\x01\xff',
            -256: b'\x00\xff',
            255: b'\xff\x00',
            256: b'\x00\x01',
            32767: b'\xff\x7f',
            -32768: b'\x00\x80',
            65535: b'\xff\xff\x00',
            -65536: b'\x00\x00\xff',
            -8388608: b'\x00\x00\x80'
        }
        check(tests2, 'little', signed=Kweli)

        # Convert integers to unsigned big-endian byte arrays.
        tests3 = {
            0: b'\x00',
            1: b'\x01',
            127: b'\x7f',
            128: b'\x80',
            255: b'\xff',
            256: b'\x01\x00',
            32767: b'\x7f\xff',
            32768: b'\x80\x00',
            65535: b'\xff\xff',
            65536: b'\x01\x00\x00'
        }
        check(tests3, 'big', signed=Uongo)

        # Convert integers to unsigned little-endian byte arrays.
        tests4 = {
            0: b'\x00',
            1: b'\x01',
            127: b'\x7f',
            128: b'\x80',
            255: b'\xff',
            256: b'\x00\x01',
            32767: b'\xff\x7f',
            32768: b'\x00\x80',
            65535: b'\xff\xff',
            65536: b'\x00\x00\x01'
        }
        check(tests4, 'little', signed=Uongo)

        self.assertRaises(OverflowError, (256).to_bytes, 1, 'big', signed=Uongo)
        self.assertRaises(OverflowError, (256).to_bytes, 1, 'big', signed=Kweli)
        self.assertRaises(OverflowError, (256).to_bytes, 1, 'little', signed=Uongo)
        self.assertRaises(OverflowError, (256).to_bytes, 1, 'little', signed=Kweli)
        self.assertRaises(OverflowError, (-1).to_bytes, 2, 'big', signed=Uongo)
        self.assertRaises(OverflowError, (-1).to_bytes, 2, 'little', signed=Uongo)
        self.assertEqual((0).to_bytes(0, 'big'), b'')
        self.assertEqual((1).to_bytes(5, 'big'), b'\x00\x00\x00\x00\x01')
        self.assertEqual((0).to_bytes(5, 'big'), b'\x00\x00\x00\x00\x00')
        self.assertEqual((-1).to_bytes(5, 'big', signed=Kweli),
                         b'\xff\xff\xff\xff\xff')
        self.assertRaises(OverflowError, (1).to_bytes, 0, 'big')

    eleza test_from_bytes(self):
        eleza check(tests, byteorder, signed=Uongo):
            kila test, expected kwenye tests.items():
                jaribu:
                    self.assertEqual(
                        int.from_bytes(test, byteorder, signed=signed),
                        expected)
                tatizo Exception kama err:
                    ashiria AssertionError(
                        "failed to convert {0} ukijumuisha byteorder={1!r} na signed={2}"
                        .format(test, byteorder, signed)) kutoka err

        # Convert signed big-endian byte arrays to integers.
        tests1 = {
            b'': 0,
            b'\x00': 0,
            b'\x00\x00': 0,
            b'\x01': 1,
            b'\x00\x01': 1,
            b'\xff': -1,
            b'\xff\xff': -1,
            b'\x81': -127,
            b'\x80': -128,
            b'\xff\x7f': -129,
            b'\x7f': 127,
            b'\x00\x81': 129,
            b'\xff\x01': -255,
            b'\xff\x00': -256,
            b'\x00\xff': 255,
            b'\x01\x00': 256,
            b'\x7f\xff': 32767,
            b'\x80\x00': -32768,
            b'\x00\xff\xff': 65535,
            b'\xff\x00\x00': -65536,
            b'\x80\x00\x00': -8388608
        }
        check(tests1, 'big', signed=Kweli)

        # Convert signed little-endian byte arrays to integers.
        tests2 = {
            b'': 0,
            b'\x00': 0,
            b'\x00\x00': 0,
            b'\x01': 1,
            b'\x00\x01': 256,
            b'\xff': -1,
            b'\xff\xff': -1,
            b'\x81': -127,
            b'\x80': -128,
            b'\x7f\xff': -129,
            b'\x7f': 127,
            b'\x81\x00': 129,
            b'\x01\xff': -255,
            b'\x00\xff': -256,
            b'\xff\x00': 255,
            b'\x00\x01': 256,
            b'\xff\x7f': 32767,
            b'\x00\x80': -32768,
            b'\xff\xff\x00': 65535,
            b'\x00\x00\xff': -65536,
            b'\x00\x00\x80': -8388608
        }
        check(tests2, 'little', signed=Kweli)

        # Convert unsigned big-endian byte arrays to integers.
        tests3 = {
            b'': 0,
            b'\x00': 0,
            b'\x01': 1,
            b'\x7f': 127,
            b'\x80': 128,
            b'\xff': 255,
            b'\x01\x00': 256,
            b'\x7f\xff': 32767,
            b'\x80\x00': 32768,
            b'\xff\xff': 65535,
            b'\x01\x00\x00': 65536,
        }
        check(tests3, 'big', signed=Uongo)

        # Convert integers to unsigned little-endian byte arrays.
        tests4 = {
            b'': 0,
            b'\x00': 0,
            b'\x01': 1,
            b'\x7f': 127,
            b'\x80': 128,
            b'\xff': 255,
            b'\x00\x01': 256,
            b'\xff\x7f': 32767,
            b'\x00\x80': 32768,
            b'\xff\xff': 65535,
            b'\x00\x00\x01': 65536,
        }
        check(tests4, 'little', signed=Uongo)

        kundi myint(int):
            pita

        self.assertIs(type(myint.from_bytes(b'\x00', 'big')), myint)
        self.assertEqual(myint.from_bytes(b'\x01', 'big'), 1)
        self.assertIs(
            type(myint.from_bytes(b'\x00', 'big', signed=Uongo)), myint)
        self.assertEqual(myint.from_bytes(b'\x01', 'big', signed=Uongo), 1)
        self.assertIs(type(myint.from_bytes(b'\x00', 'little')), myint)
        self.assertEqual(myint.from_bytes(b'\x01', 'little'), 1)
        self.assertIs(type(myint.from_bytes(
            b'\x00', 'little', signed=Uongo)), myint)
        self.assertEqual(myint.from_bytes(b'\x01', 'little', signed=Uongo), 1)
        self.assertEqual(
            int.from_bytes([255, 0, 0], 'big', signed=Kweli), -65536)
        self.assertEqual(
            int.from_bytes((255, 0, 0), 'big', signed=Kweli), -65536)
        self.assertEqual(int.from_bytes(
            bytearray(b'\xff\x00\x00'), 'big', signed=Kweli), -65536)
        self.assertEqual(int.from_bytes(
            bytearray(b'\xff\x00\x00'), 'big', signed=Kweli), -65536)
        self.assertEqual(int.from_bytes(
            array.array('B', b'\xff\x00\x00'), 'big', signed=Kweli), -65536)
        self.assertEqual(int.from_bytes(
            memoryview(b'\xff\x00\x00'), 'big', signed=Kweli), -65536)
        self.assertRaises(ValueError, int.from_bytes, [256], 'big')
        self.assertRaises(ValueError, int.from_bytes, [0], 'big\x00')
        self.assertRaises(ValueError, int.from_bytes, [0], 'little\x00')
        self.assertRaises(TypeError, int.from_bytes, "", 'big')
        self.assertRaises(TypeError, int.from_bytes, "\x00", 'big')
        self.assertRaises(TypeError, int.from_bytes, 0, 'big')
        self.assertRaises(TypeError, int.from_bytes, 0, 'big', Kweli)
        self.assertRaises(TypeError, myint.from_bytes, "", 'big')
        self.assertRaises(TypeError, myint.from_bytes, "\x00", 'big')
        self.assertRaises(TypeError, myint.from_bytes, 0, 'big')
        self.assertRaises(TypeError, int.from_bytes, 0, 'big', Kweli)

        kundi myint2(int):
            eleza __new__(cls, value):
                rudisha int.__new__(cls, value + 1)

        i = myint2.from_bytes(b'\x01', 'big')
        self.assertIs(type(i), myint2)
        self.assertEqual(i, 2)

        kundi myint3(int):
            eleza __init__(self, value):
                self.foo = 'bar'

        i = myint3.from_bytes(b'\x01', 'big')
        self.assertIs(type(i), myint3)
        self.assertEqual(i, 1)
        self.assertEqual(getattr(i, 'foo', 'none'), 'bar')

    eleza test_access_to_nonexistent_digit_0(self):
        # http://bugs.python.org/issue14630: A bug kwenye _PyLong_Copy meant that
        # ob_digit[0] was being incorrectly accessed kila instances of a
        # subkundi of int, ukijumuisha value 0.
        kundi Integer(int):
            eleza __new__(cls, value=0):
                self = int.__new__(cls, value)
                self.foo = 'foo'
                rudisha self

        integers = [Integer(0) kila i kwenye range(1000)]
        kila n kwenye map(int, integers):
            self.assertEqual(n, 0)

    eleza test_shift_bool(self):
        # Issue #21422: ensure that bool << int na bool >> int rudisha int
        kila value kwenye (Kweli, Uongo):
            kila shift kwenye (0, 2):
                self.assertEqual(type(value << shift), int)
                self.assertEqual(type(value >> shift), int)

    eleza test_as_integer_ratio(self):
        kundi myint(int):
            pita
        tests = [10, 0, -10, 1, sys.maxsize + 1, Kweli, Uongo, myint(42)]
        kila value kwenye tests:
            numerator, denominator = value.as_integer_ratio()
            self.assertEqual((numerator, denominator), (int(value), 1))
            self.assertEqual(type(numerator), int)
            self.assertEqual(type(denominator), int)


ikiwa __name__ == "__main__":
    unittest.main()
