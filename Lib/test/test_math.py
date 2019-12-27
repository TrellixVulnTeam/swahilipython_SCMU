# Python test set -- math module
# XXXX Should not do tests around zero only

kutoka test.support agiza run_unittest, verbose, requires_IEEE_754
kutoka test agiza support
agiza unittest
agiza itertools
agiza decimal
agiza math
agiza os
agiza platform
agiza random
agiza struct
agiza sys


eps = 1E-05
NAN = float('nan')
INF = float('inf')
NINF = float('-inf')
FLOAT_MAX = sys.float_info.max
FLOAT_MIN = sys.float_info.min

# detect evidence of double-rounding: fsum is not always correctly
# rounded on machines that suffer kutoka double rounding.
x, y = 1e16, 2.9999 # use temporary values to defeat peephole optimizer
HAVE_DOUBLE_ROUNDING = (x + y == 1e16 + 4)

# locate file with test values
ikiwa __name__ == '__main__':
    file = sys.argv[0]
else:
    file = __file__
test_dir = os.path.dirname(file) or os.curdir
math_testcases = os.path.join(test_dir, 'math_testcases.txt')
test_file = os.path.join(test_dir, 'cmath_testcases.txt')


eleza to_ulps(x):
    """Convert a non-NaN float x to an integer, in such a way that
    adjacent floats are converted to adjacent integers.  Then
    abs(ulps(x) - ulps(y)) gives the difference in ulps between two
    floats.

    The results kutoka this function will only make sense on platforms
    where native doubles are represented in IEEE 754 binary64 format.

    Note: 0.0 and -0.0 are converted to 0 and -1, respectively.
    """
    n = struct.unpack('<q', struct.pack('<d', x))[0]
    ikiwa n < 0:
        n = ~(n+2**63)
    rudisha n


eleza ulp(x):
    """Return the value of the least significant bit of a
    float x, such that the first float bigger than x is x+ulp(x).
    Then, given an expected result x and a tolerance of n ulps,
    the result y should be such that abs(y-x) <= n * ulp(x).
    The results kutoka this function will only make sense on platforms
    where native doubles are represented in IEEE 754 binary64 format.
    """
    x = abs(float(x))
    ikiwa math.isnan(x) or math.isinf(x):
        rudisha x

    # Find next float up kutoka x.
    n = struct.unpack('<q', struct.pack('<d', x))[0]
    x_next = struct.unpack('<d', struct.pack('<q', n + 1))[0]
    ikiwa math.isinf(x_next):
        # Corner case: x was the largest finite float. Then it's
        # not an exact power of two, so we can take the difference
        # between x and the previous float.
        x_prev = struct.unpack('<d', struct.pack('<q', n - 1))[0]
        rudisha x - x_prev
    else:
        rudisha x_next - x

# Here's a pure Python version of the math.factorial algorithm, for
# documentation and comparison purposes.
#
# Formula:
#
#   factorial(n) = factorial_odd_part(n) << (n - count_set_bits(n))
#
# where
#
#   factorial_odd_part(n) = product_{i >= 0} product_{0 < j <= n >> i; j odd} j
#
# The outer product above is an infinite product, but once i >= n.bit_length,
# (n >> i) < 1 and the corresponding term of the product is empty.  So only the
# finitely many terms for 0 <= i < n.bit_length() contribute anything.
#
# We iterate downwards kutoka i == n.bit_length() - 1 to i == 0.  The inner
# product in the formula above starts at 1 for i == n.bit_length(); for each i
# < n.bit_length() we get the inner product for i kutoka that for i + 1 by
# multiplying by all j in {n >> i+1 < j <= n >> i; j odd}.  In Python terms,
# this set is range((n >> i+1) + 1 | 1, (n >> i) + 1 | 1, 2).

eleza count_set_bits(n):
    """Number of '1' bits in binary expansion of a nonnnegative integer."""
    rudisha 1 + count_set_bits(n & n - 1) ikiwa n else 0

eleza partial_product(start, stop):
    """Product of integers in range(start, stop, 2), computed recursively.
    start and stop should both be odd, with start <= stop.

    """
    numfactors = (stop - start) >> 1
    ikiwa not numfactors:
        rudisha 1
    elikiwa numfactors == 1:
        rudisha start
    else:
        mid = (start + numfactors) | 1
        rudisha partial_product(start, mid) * partial_product(mid, stop)

eleza py_factorial(n):
    """Factorial of nonnegative integer n, via "Binary Split Factorial Formula"
    described at http://www.luschny.de/math/factorial/binarysplitfact.html

    """
    inner = outer = 1
    for i in reversed(range(n.bit_length())):
        inner *= partial_product((n >> i + 1) + 1 | 1, (n >> i) + 1 | 1)
        outer *= inner
    rudisha outer << (n - count_set_bits(n))

eleza ulp_abs_check(expected, got, ulp_tol, abs_tol):
    """Given finite floats `expected` and `got`, check that they're
    approximately equal to within the given number of ulps or the
    given absolute tolerance, whichever is bigger.

    Returns None on success and an error message on failure.
    """
    ulp_error = abs(to_ulps(expected) - to_ulps(got))
    abs_error = abs(expected - got)

    # Succeed ikiwa either abs_error <= abs_tol or ulp_error <= ulp_tol.
    ikiwa abs_error <= abs_tol or ulp_error <= ulp_tol:
        rudisha None
    else:
        fmt = ("error = {:.3g} ({:d} ulps); "
               "permitted error = {:.3g} or {:d} ulps")
        rudisha fmt.format(abs_error, ulp_error, abs_tol, ulp_tol)

eleza parse_mtestfile(fname):
    """Parse a file with test values

    -- starts a comment
    blank lines, or lines containing only a comment, are ignored
    other lines are expected to have the form
      id fn arg -> expected [flag]*

    """
    with open(fname) as fp:
        for line in fp:
            # strip comments, and skip blank lines
            ikiwa '--' in line:
                line = line[:line.index('--')]
            ikiwa not line.strip():
                continue

            lhs, rhs = line.split('->')
            id, fn, arg = lhs.split()
            rhs_pieces = rhs.split()
            exp = rhs_pieces[0]
            flags = rhs_pieces[1:]

            yield (id, fn, float(arg), float(exp), flags)


eleza parse_testfile(fname):
    """Parse a file with test values

    Empty lines or lines starting with -- are ignored
    yields id, fn, arg_real, arg_imag, exp_real, exp_imag
    """
    with open(fname) as fp:
        for line in fp:
            # skip comment lines and blank lines
            ikiwa line.startswith('--') or not line.strip():
                continue

            lhs, rhs = line.split('->')
            id, fn, arg_real, arg_imag = lhs.split()
            rhs_pieces = rhs.split()
            exp_real, exp_imag = rhs_pieces[0], rhs_pieces[1]
            flags = rhs_pieces[2:]

            yield (id, fn,
                   float(arg_real), float(arg_imag),
                   float(exp_real), float(exp_imag),
                   flags)


eleza result_check(expected, got, ulp_tol=5, abs_tol=0.0):
    # Common logic of MathTests.(ftest, test_testcases, test_mtestcases)
    """Compare arguments expected and got, as floats, ikiwa either
    is a float, using a tolerance expressed in multiples of
    ulp(expected) or absolutely (ikiwa given and greater).

    As a convenience, when neither argument is a float, and for
    non-finite floats, exact equality is demanded. Also, nan==nan
    as far as this function is concerned.

    Returns None on success and an error message on failure.
    """

    # Check exactly equal (applies also to strings representing exceptions)
    ikiwa got == expected:
        rudisha None

    failure = "not equal"

    # Turn mixed float and int comparison (e.g. floor()) to all-float
    ikiwa isinstance(expected, float) and isinstance(got, int):
        got = float(got)
    elikiwa isinstance(got, float) and isinstance(expected, int):
        expected = float(expected)

    ikiwa isinstance(expected, float) and isinstance(got, float):
        ikiwa math.isnan(expected) and math.isnan(got):
            # Pass, since both nan
            failure = None
        elikiwa math.isinf(expected) or math.isinf(got):
            # We already know they're not equal, drop through to failure
            pass
        else:
            # Both are finite floats (now). Are they close enough?
            failure = ulp_abs_check(expected, got, ulp_tol, abs_tol)

    # arguments are not equal, and ikiwa numeric, are too far apart
    ikiwa failure is not None:
        fail_fmt = "expected {!r}, got {!r}"
        fail_msg = fail_fmt.format(expected, got)
        fail_msg += ' ({})'.format(failure)
        rudisha fail_msg
    else:
        rudisha None

kundi IntSubclass(int):
    pass

# Class providing an __index__ method.
kundi MyIndexable(object):
    eleza __init__(self, value):
        self.value = value

    eleza __index__(self):
        rudisha self.value

kundi MathTests(unittest.TestCase):

    eleza ftest(self, name, got, expected, ulp_tol=5, abs_tol=0.0):
        """Compare arguments expected and got, as floats, ikiwa either
        is a float, using a tolerance expressed in multiples of
        ulp(expected) or absolutely, whichever is greater.

        As a convenience, when neither argument is a float, and for
        non-finite floats, exact equality is demanded. Also, nan==nan
        in this function.
        """
        failure = result_check(expected, got, ulp_tol, abs_tol)
        ikiwa failure is not None:
            self.fail("{}: {}".format(name, failure))

    eleza testConstants(self):
        # Ref: Abramowitz & Stegun (Dover, 1965)
        self.ftest('pi', math.pi, 3.141592653589793238462643)
        self.ftest('e', math.e, 2.718281828459045235360287)
        self.assertEqual(math.tau, 2*math.pi)

    eleza testAcos(self):
        self.assertRaises(TypeError, math.acos)
        self.ftest('acos(-1)', math.acos(-1), math.pi)
        self.ftest('acos(0)', math.acos(0), math.pi/2)
        self.ftest('acos(1)', math.acos(1), 0)
        self.assertRaises(ValueError, math.acos, INF)
        self.assertRaises(ValueError, math.acos, NINF)
        self.assertRaises(ValueError, math.acos, 1 + eps)
        self.assertRaises(ValueError, math.acos, -1 - eps)
        self.assertTrue(math.isnan(math.acos(NAN)))

    eleza testAcosh(self):
        self.assertRaises(TypeError, math.acosh)
        self.ftest('acosh(1)', math.acosh(1), 0)
        self.ftest('acosh(2)', math.acosh(2), 1.3169578969248168)
        self.assertRaises(ValueError, math.acosh, 0)
        self.assertRaises(ValueError, math.acosh, -1)
        self.assertEqual(math.acosh(INF), INF)
        self.assertRaises(ValueError, math.acosh, NINF)
        self.assertTrue(math.isnan(math.acosh(NAN)))

    eleza testAsin(self):
        self.assertRaises(TypeError, math.asin)
        self.ftest('asin(-1)', math.asin(-1), -math.pi/2)
        self.ftest('asin(0)', math.asin(0), 0)
        self.ftest('asin(1)', math.asin(1), math.pi/2)
        self.assertRaises(ValueError, math.asin, INF)
        self.assertRaises(ValueError, math.asin, NINF)
        self.assertRaises(ValueError, math.asin, 1 + eps)
        self.assertRaises(ValueError, math.asin, -1 - eps)
        self.assertTrue(math.isnan(math.asin(NAN)))

    eleza testAsinh(self):
        self.assertRaises(TypeError, math.asinh)
        self.ftest('asinh(0)', math.asinh(0), 0)
        self.ftest('asinh(1)', math.asinh(1), 0.88137358701954305)
        self.ftest('asinh(-1)', math.asinh(-1), -0.88137358701954305)
        self.assertEqual(math.asinh(INF), INF)
        self.assertEqual(math.asinh(NINF), NINF)
        self.assertTrue(math.isnan(math.asinh(NAN)))

    eleza testAtan(self):
        self.assertRaises(TypeError, math.atan)
        self.ftest('atan(-1)', math.atan(-1), -math.pi/4)
        self.ftest('atan(0)', math.atan(0), 0)
        self.ftest('atan(1)', math.atan(1), math.pi/4)
        self.ftest('atan(inf)', math.atan(INF), math.pi/2)
        self.ftest('atan(-inf)', math.atan(NINF), -math.pi/2)
        self.assertTrue(math.isnan(math.atan(NAN)))

    eleza testAtanh(self):
        self.assertRaises(TypeError, math.atan)
        self.ftest('atanh(0)', math.atanh(0), 0)
        self.ftest('atanh(0.5)', math.atanh(0.5), 0.54930614433405489)
        self.ftest('atanh(-0.5)', math.atanh(-0.5), -0.54930614433405489)
        self.assertRaises(ValueError, math.atanh, 1)
        self.assertRaises(ValueError, math.atanh, -1)
        self.assertRaises(ValueError, math.atanh, INF)
        self.assertRaises(ValueError, math.atanh, NINF)
        self.assertTrue(math.isnan(math.atanh(NAN)))

    eleza testAtan2(self):
        self.assertRaises(TypeError, math.atan2)
        self.ftest('atan2(-1, 0)', math.atan2(-1, 0), -math.pi/2)
        self.ftest('atan2(-1, 1)', math.atan2(-1, 1), -math.pi/4)
        self.ftest('atan2(0, 1)', math.atan2(0, 1), 0)
        self.ftest('atan2(1, 1)', math.atan2(1, 1), math.pi/4)
        self.ftest('atan2(1, 0)', math.atan2(1, 0), math.pi/2)

        # math.atan2(0, x)
        self.ftest('atan2(0., -inf)', math.atan2(0., NINF), math.pi)
        self.ftest('atan2(0., -2.3)', math.atan2(0., -2.3), math.pi)
        self.ftest('atan2(0., -0.)', math.atan2(0., -0.), math.pi)
        self.assertEqual(math.atan2(0., 0.), 0.)
        self.assertEqual(math.atan2(0., 2.3), 0.)
        self.assertEqual(math.atan2(0., INF), 0.)
        self.assertTrue(math.isnan(math.atan2(0., NAN)))
        # math.atan2(-0, x)
        self.ftest('atan2(-0., -inf)', math.atan2(-0., NINF), -math.pi)
        self.ftest('atan2(-0., -2.3)', math.atan2(-0., -2.3), -math.pi)
        self.ftest('atan2(-0., -0.)', math.atan2(-0., -0.), -math.pi)
        self.assertEqual(math.atan2(-0., 0.), -0.)
        self.assertEqual(math.atan2(-0., 2.3), -0.)
        self.assertEqual(math.atan2(-0., INF), -0.)
        self.assertTrue(math.isnan(math.atan2(-0., NAN)))
        # math.atan2(INF, x)
        self.ftest('atan2(inf, -inf)', math.atan2(INF, NINF), math.pi*3/4)
        self.ftest('atan2(inf, -2.3)', math.atan2(INF, -2.3), math.pi/2)
        self.ftest('atan2(inf, -0.)', math.atan2(INF, -0.0), math.pi/2)
        self.ftest('atan2(inf, 0.)', math.atan2(INF, 0.0), math.pi/2)
        self.ftest('atan2(inf, 2.3)', math.atan2(INF, 2.3), math.pi/2)
        self.ftest('atan2(inf, inf)', math.atan2(INF, INF), math.pi/4)
        self.assertTrue(math.isnan(math.atan2(INF, NAN)))
        # math.atan2(NINF, x)
        self.ftest('atan2(-inf, -inf)', math.atan2(NINF, NINF), -math.pi*3/4)
        self.ftest('atan2(-inf, -2.3)', math.atan2(NINF, -2.3), -math.pi/2)
        self.ftest('atan2(-inf, -0.)', math.atan2(NINF, -0.0), -math.pi/2)
        self.ftest('atan2(-inf, 0.)', math.atan2(NINF, 0.0), -math.pi/2)
        self.ftest('atan2(-inf, 2.3)', math.atan2(NINF, 2.3), -math.pi/2)
        self.ftest('atan2(-inf, inf)', math.atan2(NINF, INF), -math.pi/4)
        self.assertTrue(math.isnan(math.atan2(NINF, NAN)))
        # math.atan2(+finite, x)
        self.ftest('atan2(2.3, -inf)', math.atan2(2.3, NINF), math.pi)
        self.ftest('atan2(2.3, -0.)', math.atan2(2.3, -0.), math.pi/2)
        self.ftest('atan2(2.3, 0.)', math.atan2(2.3, 0.), math.pi/2)
        self.assertEqual(math.atan2(2.3, INF), 0.)
        self.assertTrue(math.isnan(math.atan2(2.3, NAN)))
        # math.atan2(-finite, x)
        self.ftest('atan2(-2.3, -inf)', math.atan2(-2.3, NINF), -math.pi)
        self.ftest('atan2(-2.3, -0.)', math.atan2(-2.3, -0.), -math.pi/2)
        self.ftest('atan2(-2.3, 0.)', math.atan2(-2.3, 0.), -math.pi/2)
        self.assertEqual(math.atan2(-2.3, INF), -0.)
        self.assertTrue(math.isnan(math.atan2(-2.3, NAN)))
        # math.atan2(NAN, x)
        self.assertTrue(math.isnan(math.atan2(NAN, NINF)))
        self.assertTrue(math.isnan(math.atan2(NAN, -2.3)))
        self.assertTrue(math.isnan(math.atan2(NAN, -0.)))
        self.assertTrue(math.isnan(math.atan2(NAN, 0.)))
        self.assertTrue(math.isnan(math.atan2(NAN, 2.3)))
        self.assertTrue(math.isnan(math.atan2(NAN, INF)))
        self.assertTrue(math.isnan(math.atan2(NAN, NAN)))

    eleza testCeil(self):
        self.assertRaises(TypeError, math.ceil)
        self.assertEqual(int, type(math.ceil(0.5)))
        self.ftest('ceil(0.5)', math.ceil(0.5), 1)
        self.ftest('ceil(1.0)', math.ceil(1.0), 1)
        self.ftest('ceil(1.5)', math.ceil(1.5), 2)
        self.ftest('ceil(-0.5)', math.ceil(-0.5), 0)
        self.ftest('ceil(-1.0)', math.ceil(-1.0), -1)
        self.ftest('ceil(-1.5)', math.ceil(-1.5), -1)
        #self.assertEqual(math.ceil(INF), INF)
        #self.assertEqual(math.ceil(NINF), NINF)
        #self.assertTrue(math.isnan(math.ceil(NAN)))

        kundi TestCeil:
            eleza __ceil__(self):
                rudisha 42
        kundi TestNoCeil:
            pass
        self.ftest('ceil(TestCeil())', math.ceil(TestCeil()), 42)
        self.assertRaises(TypeError, math.ceil, TestNoCeil())

        t = TestNoCeil()
        t.__ceil__ = lambda *args: args
        self.assertRaises(TypeError, math.ceil, t)
        self.assertRaises(TypeError, math.ceil, t, 0)

    @requires_IEEE_754
    eleza testCopysign(self):
        self.assertEqual(math.copysign(1, 42), 1.0)
        self.assertEqual(math.copysign(0., 42), 0.0)
        self.assertEqual(math.copysign(1., -42), -1.0)
        self.assertEqual(math.copysign(3, 0.), 3.0)
        self.assertEqual(math.copysign(4., -0.), -4.0)

        self.assertRaises(TypeError, math.copysign)
        # copysign should let us distinguish signs of zeros
        self.assertEqual(math.copysign(1., 0.), 1.)
        self.assertEqual(math.copysign(1., -0.), -1.)
        self.assertEqual(math.copysign(INF, 0.), INF)
        self.assertEqual(math.copysign(INF, -0.), NINF)
        self.assertEqual(math.copysign(NINF, 0.), INF)
        self.assertEqual(math.copysign(NINF, -0.), NINF)
        # and of infinities
        self.assertEqual(math.copysign(1., INF), 1.)
        self.assertEqual(math.copysign(1., NINF), -1.)
        self.assertEqual(math.copysign(INF, INF), INF)
        self.assertEqual(math.copysign(INF, NINF), NINF)
        self.assertEqual(math.copysign(NINF, INF), INF)
        self.assertEqual(math.copysign(NINF, NINF), NINF)
        self.assertTrue(math.isnan(math.copysign(NAN, 1.)))
        self.assertTrue(math.isnan(math.copysign(NAN, INF)))
        self.assertTrue(math.isnan(math.copysign(NAN, NINF)))
        self.assertTrue(math.isnan(math.copysign(NAN, NAN)))
        # copysign(INF, NAN) may be INF or it may be NINF, since
        # we don't know whether the sign bit of NAN is set on any
        # given platform.
        self.assertTrue(math.isinf(math.copysign(INF, NAN)))
        # similarly, copysign(2., NAN) could be 2. or -2.
        self.assertEqual(abs(math.copysign(2., NAN)), 2.)

    eleza testCos(self):
        self.assertRaises(TypeError, math.cos)
        self.ftest('cos(-pi/2)', math.cos(-math.pi/2), 0, abs_tol=ulp(1))
        self.ftest('cos(0)', math.cos(0), 1)
        self.ftest('cos(pi/2)', math.cos(math.pi/2), 0, abs_tol=ulp(1))
        self.ftest('cos(pi)', math.cos(math.pi), -1)
        try:
            self.assertTrue(math.isnan(math.cos(INF)))
            self.assertTrue(math.isnan(math.cos(NINF)))
        except ValueError:
            self.assertRaises(ValueError, math.cos, INF)
            self.assertRaises(ValueError, math.cos, NINF)
        self.assertTrue(math.isnan(math.cos(NAN)))

    eleza testCosh(self):
        self.assertRaises(TypeError, math.cosh)
        self.ftest('cosh(0)', math.cosh(0), 1)
        self.ftest('cosh(2)-2*cosh(1)**2', math.cosh(2)-2*math.cosh(1)**2, -1) # Thanks to Lambert
        self.assertEqual(math.cosh(INF), INF)
        self.assertEqual(math.cosh(NINF), INF)
        self.assertTrue(math.isnan(math.cosh(NAN)))

    eleza testDegrees(self):
        self.assertRaises(TypeError, math.degrees)
        self.ftest('degrees(pi)', math.degrees(math.pi), 180.0)
        self.ftest('degrees(pi/2)', math.degrees(math.pi/2), 90.0)
        self.ftest('degrees(-pi/4)', math.degrees(-math.pi/4), -45.0)
        self.ftest('degrees(0)', math.degrees(0), 0)

    eleza testExp(self):
        self.assertRaises(TypeError, math.exp)
        self.ftest('exp(-1)', math.exp(-1), 1/math.e)
        self.ftest('exp(0)', math.exp(0), 1)
        self.ftest('exp(1)', math.exp(1), math.e)
        self.assertEqual(math.exp(INF), INF)
        self.assertEqual(math.exp(NINF), 0.)
        self.assertTrue(math.isnan(math.exp(NAN)))
        self.assertRaises(OverflowError, math.exp, 1000000)

    eleza testFabs(self):
        self.assertRaises(TypeError, math.fabs)
        self.ftest('fabs(-1)', math.fabs(-1), 1)
        self.ftest('fabs(0)', math.fabs(0), 0)
        self.ftest('fabs(1)', math.fabs(1), 1)

    eleza testFactorial(self):
        self.assertEqual(math.factorial(0), 1)
        self.assertEqual(math.factorial(0.0), 1)
        total = 1
        for i in range(1, 1000):
            total *= i
            self.assertEqual(math.factorial(i), total)
            self.assertEqual(math.factorial(float(i)), total)
            self.assertEqual(math.factorial(i), py_factorial(i))
        self.assertRaises(ValueError, math.factorial, -1)
        self.assertRaises(ValueError, math.factorial, -1.0)
        self.assertRaises(ValueError, math.factorial, -10**100)
        self.assertRaises(ValueError, math.factorial, -1e100)
        self.assertRaises(ValueError, math.factorial, math.pi)

    eleza testFactorialNonIntegers(self):
        self.assertRaises(TypeError, math.factorial, decimal.Decimal(5.2))
        self.assertRaises(TypeError, math.factorial, "5")

    # Other implementations may place different upper bounds.
    @support.cpython_only
    eleza testFactorialHugeInputs(self):
        # Currently raises OverflowError for inputs that are too large
        # to fit into a C long.
        self.assertRaises(OverflowError, math.factorial, 10**100)
        self.assertRaises(OverflowError, math.factorial, 1e100)

    eleza testFloor(self):
        self.assertRaises(TypeError, math.floor)
        self.assertEqual(int, type(math.floor(0.5)))
        self.ftest('floor(0.5)', math.floor(0.5), 0)
        self.ftest('floor(1.0)', math.floor(1.0), 1)
        self.ftest('floor(1.5)', math.floor(1.5), 1)
        self.ftest('floor(-0.5)', math.floor(-0.5), -1)
        self.ftest('floor(-1.0)', math.floor(-1.0), -1)
        self.ftest('floor(-1.5)', math.floor(-1.5), -2)
        # pow() relies on floor() to check for integers
        # This fails on some platforms - so check it here
        self.ftest('floor(1.23e167)', math.floor(1.23e167), 1.23e167)
        self.ftest('floor(-1.23e167)', math.floor(-1.23e167), -1.23e167)
        #self.assertEqual(math.ceil(INF), INF)
        #self.assertEqual(math.ceil(NINF), NINF)
        #self.assertTrue(math.isnan(math.floor(NAN)))

        kundi TestFloor:
            eleza __floor__(self):
                rudisha 42
        kundi TestNoFloor:
            pass
        self.ftest('floor(TestFloor())', math.floor(TestFloor()), 42)
        self.assertRaises(TypeError, math.floor, TestNoFloor())

        t = TestNoFloor()
        t.__floor__ = lambda *args: args
        self.assertRaises(TypeError, math.floor, t)
        self.assertRaises(TypeError, math.floor, t, 0)

    eleza testFmod(self):
        self.assertRaises(TypeError, math.fmod)
        self.ftest('fmod(10, 1)', math.fmod(10, 1), 0.0)
        self.ftest('fmod(10, 0.5)', math.fmod(10, 0.5), 0.0)
        self.ftest('fmod(10, 1.5)', math.fmod(10, 1.5), 1.0)
        self.ftest('fmod(-10, 1)', math.fmod(-10, 1), -0.0)
        self.ftest('fmod(-10, 0.5)', math.fmod(-10, 0.5), -0.0)
        self.ftest('fmod(-10, 1.5)', math.fmod(-10, 1.5), -1.0)
        self.assertTrue(math.isnan(math.fmod(NAN, 1.)))
        self.assertTrue(math.isnan(math.fmod(1., NAN)))
        self.assertTrue(math.isnan(math.fmod(NAN, NAN)))
        self.assertRaises(ValueError, math.fmod, 1., 0.)
        self.assertRaises(ValueError, math.fmod, INF, 1.)
        self.assertRaises(ValueError, math.fmod, NINF, 1.)
        self.assertRaises(ValueError, math.fmod, INF, 0.)
        self.assertEqual(math.fmod(3.0, INF), 3.0)
        self.assertEqual(math.fmod(-3.0, INF), -3.0)
        self.assertEqual(math.fmod(3.0, NINF), 3.0)
        self.assertEqual(math.fmod(-3.0, NINF), -3.0)
        self.assertEqual(math.fmod(0.0, 3.0), 0.0)
        self.assertEqual(math.fmod(0.0, NINF), 0.0)

    eleza testFrexp(self):
        self.assertRaises(TypeError, math.frexp)

        eleza testfrexp(name, result, expected):
            (mant, exp), (emant, eexp) = result, expected
            ikiwa abs(mant-emant) > eps or exp != eexp:
                self.fail('%s returned %r, expected %r'%\
                          (name, result, expected))

        testfrexp('frexp(-1)', math.frexp(-1), (-0.5, 1))
        testfrexp('frexp(0)', math.frexp(0), (0, 0))
        testfrexp('frexp(1)', math.frexp(1), (0.5, 1))
        testfrexp('frexp(2)', math.frexp(2), (0.5, 2))

        self.assertEqual(math.frexp(INF)[0], INF)
        self.assertEqual(math.frexp(NINF)[0], NINF)
        self.assertTrue(math.isnan(math.frexp(NAN)[0]))

    @requires_IEEE_754
    @unittest.skipIf(HAVE_DOUBLE_ROUNDING,
                         "fsum is not exact on machines with double rounding")
    eleza testFsum(self):
        # math.fsum relies on exact rounding for correct operation.
        # There's a known problem with IA32 floating-point that causes
        # inexact rounding in some situations, and will cause the
        # math.fsum tests below to fail; see issue #2937.  On non IEEE
        # 754 platforms, and on IEEE 754 platforms that exhibit the
        # problem described in issue #2937, we simply skip the whole
        # test.

        # Python version of math.fsum, for comparison.  Uses a
        # different algorithm based on frexp, ldexp and integer
        # arithmetic.
        kutoka sys agiza float_info
        mant_dig = float_info.mant_dig
        etiny = float_info.min_exp - mant_dig

        eleza msum(iterable):
            """Full precision summation.  Compute sum(iterable) without any
            intermediate accumulation of error.  Based on the 'lsum' function
            at http://code.activestate.com/recipes/393090/

            """
            tmant, texp = 0, 0
            for x in iterable:
                mant, exp = math.frexp(x)
                mant, exp = int(math.ldexp(mant, mant_dig)), exp - mant_dig
                ikiwa texp > exp:
                    tmant <<= texp-exp
                    texp = exp
                else:
                    mant <<= exp-texp
                tmant += mant
            # Round tmant * 2**texp to a float.  The original recipe
            # used float(str(tmant)) * 2.0**texp for this, but that's
            # a little unsafe because str -> float conversion can't be
            # relied upon to do correct rounding on all platforms.
            tail = max(len(bin(abs(tmant)))-2 - mant_dig, etiny - texp)
            ikiwa tail > 0:
                h = 1 << (tail-1)
                tmant = tmant // (2*h) + bool(tmant & h and tmant & 3*h-1)
                texp += tail
            rudisha math.ldexp(tmant, texp)

        test_values = [
            ([], 0.0),
            ([0.0], 0.0),
            ([1e100, 1.0, -1e100, 1e-100, 1e50, -1.0, -1e50], 1e-100),
            ([2.0**53, -0.5, -2.0**-54], 2.0**53-1.0),
            ([2.0**53, 1.0, 2.0**-100], 2.0**53+2.0),
            ([2.0**53+10.0, 1.0, 2.0**-100], 2.0**53+12.0),
            ([2.0**53-4.0, 0.5, 2.0**-54], 2.0**53-3.0),
            ([1./n for n in range(1, 1001)],
             float.kutokahex('0x1.df11f45f4e61ap+2')),
            ([(-1.)**n/n for n in range(1, 1001)],
             float.kutokahex('-0x1.62a2af1bd3624p-1')),
            ([1.7**(i+1)-1.7**i for i in range(1000)] + [-1.7**1000], -1.0),
            ([1e16, 1., 1e-16], 10000000000000002.0),
            ([1e16-2., 1.-2.**-53, -(1e16-2.), -(1.-2.**-53)], 0.0),
            # exercise code for resizing partials array
            ([2.**n - 2.**(n+50) + 2.**(n+52) for n in range(-1074, 972, 2)] +
             [-2.**1022],
             float.kutokahex('0x1.5555555555555p+970')),
            ]

        for i, (vals, expected) in enumerate(test_values):
            try:
                actual = math.fsum(vals)
            except OverflowError:
                self.fail("test %d failed: got OverflowError, expected %r "
                          "for math.fsum(%.100r)" % (i, expected, vals))
            except ValueError:
                self.fail("test %d failed: got ValueError, expected %r "
                          "for math.fsum(%.100r)" % (i, expected, vals))
            self.assertEqual(actual, expected)

        kutoka random agiza random, gauss, shuffle
        for j in range(1000):
            vals = [7, 1e100, -7, -1e100, -9e-20, 8e-20] * 10
            s = 0
            for i in range(200):
                v = gauss(0, random()) ** 7 - s
                s += v
                vals.append(v)
            shuffle(vals)

            s = msum(vals)
            self.assertEqual(msum(vals), math.fsum(vals))

    eleza testGcd(self):
        gcd = math.gcd
        self.assertEqual(gcd(0, 0), 0)
        self.assertEqual(gcd(1, 0), 1)
        self.assertEqual(gcd(-1, 0), 1)
        self.assertEqual(gcd(0, 1), 1)
        self.assertEqual(gcd(0, -1), 1)
        self.assertEqual(gcd(7, 1), 1)
        self.assertEqual(gcd(7, -1), 1)
        self.assertEqual(gcd(-23, 15), 1)
        self.assertEqual(gcd(120, 84), 12)
        self.assertEqual(gcd(84, -120), 12)
        self.assertEqual(gcd(1216342683557601535506311712,
                             436522681849110124616458784), 32)
        c = 652560
        x = 434610456570399902378880679233098819019853229470286994367836600566
        y = 1064502245825115327754847244914921553977
        a = x * c
        b = y * c
        self.assertEqual(gcd(a, b), c)
        self.assertEqual(gcd(b, a), c)
        self.assertEqual(gcd(-a, b), c)
        self.assertEqual(gcd(b, -a), c)
        self.assertEqual(gcd(a, -b), c)
        self.assertEqual(gcd(-b, a), c)
        self.assertEqual(gcd(-a, -b), c)
        self.assertEqual(gcd(-b, -a), c)
        c = 576559230871654959816130551884856912003141446781646602790216406874
        a = x * c
        b = y * c
        self.assertEqual(gcd(a, b), c)
        self.assertEqual(gcd(b, a), c)
        self.assertEqual(gcd(-a, b), c)
        self.assertEqual(gcd(b, -a), c)
        self.assertEqual(gcd(a, -b), c)
        self.assertEqual(gcd(-b, a), c)
        self.assertEqual(gcd(-a, -b), c)
        self.assertEqual(gcd(-b, -a), c)

        self.assertRaises(TypeError, gcd, 120.0, 84)
        self.assertRaises(TypeError, gcd, 120, 84.0)
        self.assertEqual(gcd(MyIndexable(120), MyIndexable(84)), 12)

    eleza testHypot(self):
        kutoka decimal agiza Decimal
        kutoka fractions agiza Fraction

        hypot = math.hypot

        # Test different numbers of arguments (kutoka zero to five)
        # against a straightforward pure python implementation
        args = math.e, math.pi, math.sqrt(2.0), math.gamma(3.5), math.sin(2.1)
        for i in range(len(args)+1):
            self.assertAlmostEqual(
                hypot(*args[:i]),
                math.sqrt(sum(s**2 for s in args[:i]))
            )

        # Test allowable types (those with __float__)
        self.assertEqual(hypot(12.0, 5.0), 13.0)
        self.assertEqual(hypot(12, 5), 13)
        self.assertEqual(hypot(Decimal(12), Decimal(5)), 13)
        self.assertEqual(hypot(Fraction(12, 32), Fraction(5, 32)), Fraction(13, 32))
        self.assertEqual(hypot(bool(1), bool(0), bool(1), bool(1)), math.sqrt(3))

        # Test corner cases
        self.assertEqual(hypot(0.0, 0.0), 0.0)     # Max input is zero
        self.assertEqual(hypot(-10.5), 10.5)       # Negative input
        self.assertEqual(hypot(), 0.0)             # Negative input
        self.assertEqual(1.0,
            math.copysign(1.0, hypot(-0.0))        # Convert negative zero to positive zero
        )
        self.assertEqual(                          # Handling of moving max to the end
            hypot(1.5, 1.5, 0.5),
            hypot(1.5, 0.5, 1.5),
        )

        # Test handling of bad arguments
        with self.assertRaises(TypeError):         # Reject keyword args
            hypot(x=1)
        with self.assertRaises(TypeError):         # Reject values without __float__
            hypot(1.1, 'string', 2.2)
        int_too_big_for_float = 10 ** (sys.float_info.max_10_exp + 5)
        with self.assertRaises((ValueError, OverflowError)):
            hypot(1, int_too_big_for_float)

        # Any infinity gives positive infinity.
        self.assertEqual(hypot(INF), INF)
        self.assertEqual(hypot(0, INF), INF)
        self.assertEqual(hypot(10, INF), INF)
        self.assertEqual(hypot(-10, INF), INF)
        self.assertEqual(hypot(NAN, INF), INF)
        self.assertEqual(hypot(INF, NAN), INF)
        self.assertEqual(hypot(NINF, NAN), INF)
        self.assertEqual(hypot(NAN, NINF), INF)
        self.assertEqual(hypot(-INF, INF), INF)
        self.assertEqual(hypot(-INF, -INF), INF)
        self.assertEqual(hypot(10, -INF), INF)

        # If no infinity, any NaN gives a NaN.
        self.assertTrue(math.isnan(hypot(NAN)))
        self.assertTrue(math.isnan(hypot(0, NAN)))
        self.assertTrue(math.isnan(hypot(NAN, 10)))
        self.assertTrue(math.isnan(hypot(10, NAN)))
        self.assertTrue(math.isnan(hypot(NAN, NAN)))
        self.assertTrue(math.isnan(hypot(NAN)))

        # Verify scaling for extremely large values
        fourthmax = FLOAT_MAX / 4.0
        for n in range(32):
            self.assertEqual(hypot(*([fourthmax]*n)), fourthmax * math.sqrt(n))

        # Verify scaling for extremely small values
        for exp in range(32):
            scale = FLOAT_MIN / 2.0 ** exp
            self.assertEqual(math.hypot(4*scale, 3*scale), 5*scale)

    eleza testDist(self):
        kutoka decimal agiza Decimal as D
        kutoka fractions agiza Fraction as F

        dist = math.dist
        sqrt = math.sqrt

        # Simple exact cases
        self.assertEqual(dist((1.0, 2.0, 3.0), (4.0, 2.0, -1.0)), 5.0)
        self.assertEqual(dist((1, 2, 3), (4, 2, -1)), 5.0)

        # Test different numbers of arguments (kutoka zero to nine)
        # against a straightforward pure python implementation
        for i in range(9):
            for j in range(5):
                p = tuple(random.uniform(-5, 5) for k in range(i))
                q = tuple(random.uniform(-5, 5) for k in range(i))
                self.assertAlmostEqual(
                    dist(p, q),
                    sqrt(sum((px - qx) ** 2.0 for px, qx in zip(p, q)))
                )

        # Test non-tuple inputs
        self.assertEqual(dist([1.0, 2.0, 3.0], [4.0, 2.0, -1.0]), 5.0)
        self.assertEqual(dist(iter([1.0, 2.0, 3.0]), iter([4.0, 2.0, -1.0])), 5.0)

        # Test allowable types (those with __float__)
        self.assertEqual(dist((14.0, 1.0), (2.0, -4.0)), 13.0)
        self.assertEqual(dist((14, 1), (2, -4)), 13)
        self.assertEqual(dist((D(14), D(1)), (D(2), D(-4))), D(13))
        self.assertEqual(dist((F(14, 32), F(1, 32)), (F(2, 32), F(-4, 32))),
                         F(13, 32))
        self.assertEqual(dist((True, True, False, True, False),
                              (True, False, True, True, False)),
                         sqrt(2.0))

        # Test corner cases
        self.assertEqual(dist((13.25, 12.5, -3.25),
                              (13.25, 12.5, -3.25)),
                         0.0)                      # Distance with self is zero
        self.assertEqual(dist((), ()), 0.0)        # Zero-dimensional case
        self.assertEqual(1.0,                      # Convert negative zero to positive zero
            math.copysign(1.0, dist((-0.0,), (0.0,)))
        )
        self.assertEqual(1.0,                      # Convert negative zero to positive zero
            math.copysign(1.0, dist((0.0,), (-0.0,)))
        )
        self.assertEqual(                          # Handling of moving max to the end
            dist((1.5, 1.5, 0.5), (0, 0, 0)),
            dist((1.5, 0.5, 1.5), (0, 0, 0))
        )

        # Verify tuple subclasses are allowed
        kundi T(tuple):
            pass
        self.assertEqual(dist(T((1, 2, 3)), ((4, 2, -1))), 5.0)

        # Test handling of bad arguments
        with self.assertRaises(TypeError):         # Reject keyword args
            dist(p=(1, 2, 3), q=(4, 5, 6))
        with self.assertRaises(TypeError):         # Too few args
            dist((1, 2, 3))
        with self.assertRaises(TypeError):         # Too many args
            dist((1, 2, 3), (4, 5, 6), (7, 8, 9))
        with self.assertRaises(TypeError):         # Scalars not allowed
            dist(1, 2)
        with self.assertRaises(TypeError):         # Reject values without __float__
            dist((1.1, 'string', 2.2), (1, 2, 3))
        with self.assertRaises(ValueError):        # Check dimension agree
            dist((1, 2, 3, 4), (5, 6, 7))
        with self.assertRaises(ValueError):        # Check dimension agree
            dist((1, 2, 3), (4, 5, 6, 7))
        with self.assertRaises(TypeError):         # Rejects invalid types
            dist("abc", "xyz")
        int_too_big_for_float = 10 ** (sys.float_info.max_10_exp + 5)
        with self.assertRaises((ValueError, OverflowError)):
            dist((1, int_too_big_for_float), (2, 3))
        with self.assertRaises((ValueError, OverflowError)):
            dist((2, 3), (1, int_too_big_for_float))

        # Verify that the one dimensional case is equivalent to abs()
        for i in range(20):
            p, q = random.random(), random.random()
            self.assertEqual(dist((p,), (q,)), abs(p - q))

        # Test special values
        values = [NINF, -10.5, -0.0, 0.0, 10.5, INF, NAN]
        for p in itertools.product(values, repeat=3):
            for q in itertools.product(values, repeat=3):
                diffs = [px - qx for px, qx in zip(p, q)]
                ikiwa any(map(math.isinf, diffs)):
                    # Any infinite difference gives positive infinity.
                    self.assertEqual(dist(p, q), INF)
                elikiwa any(map(math.isnan, diffs)):
                    # If no infinity, any NaN gives a NaN.
                    self.assertTrue(math.isnan(dist(p, q)))

        # Verify scaling for extremely large values
        fourthmax = FLOAT_MAX / 4.0
        for n in range(32):
            p = (fourthmax,) * n
            q = (0.0,) * n
            self.assertEqual(dist(p, q), fourthmax * math.sqrt(n))
            self.assertEqual(dist(q, p), fourthmax * math.sqrt(n))

        # Verify scaling for extremely small values
        for exp in range(32):
            scale = FLOAT_MIN / 2.0 ** exp
            p = (4*scale, 3*scale)
            q = (0.0, 0.0)
            self.assertEqual(math.dist(p, q), 5*scale)
            self.assertEqual(math.dist(q, p), 5*scale)

    eleza testIsqrt(self):
        # Test a variety of inputs, large and small.
        test_values = (
            list(range(1000))
            + list(range(10**6 - 1000, 10**6 + 1000))
            + [2**e + i for e in range(60, 200) for i in range(-40, 40)]
            + [3**9999, 10**5001]
        )

        for value in test_values:
            with self.subTest(value=value):
                s = math.isqrt(value)
                self.assertIs(type(s), int)
                self.assertLessEqual(s*s, value)
                self.assertLess(value, (s+1)*(s+1))

        # Negative values
        with self.assertRaises(ValueError):
            math.isqrt(-1)

        # Integer-like things
        s = math.isqrt(True)
        self.assertIs(type(s), int)
        self.assertEqual(s, 1)

        s = math.isqrt(False)
        self.assertIs(type(s), int)
        self.assertEqual(s, 0)

        kundi IntegerLike(object):
            eleza __init__(self, value):
                self.value = value

            eleza __index__(self):
                rudisha self.value

        s = math.isqrt(IntegerLike(1729))
        self.assertIs(type(s), int)
        self.assertEqual(s, 41)

        with self.assertRaises(ValueError):
            math.isqrt(IntegerLike(-3))

        # Non-integer-like things
        bad_values = [
            3.5, "a string", decimal.Decimal("3.5"), 3.5j,
            100.0, -4.0,
        ]
        for value in bad_values:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    math.isqrt(value)

    eleza testLdexp(self):
        self.assertRaises(TypeError, math.ldexp)
        self.ftest('ldexp(0,1)', math.ldexp(0,1), 0)
        self.ftest('ldexp(1,1)', math.ldexp(1,1), 2)
        self.ftest('ldexp(1,-1)', math.ldexp(1,-1), 0.5)
        self.ftest('ldexp(-1,1)', math.ldexp(-1,1), -2)
        self.assertRaises(OverflowError, math.ldexp, 1., 1000000)
        self.assertRaises(OverflowError, math.ldexp, -1., 1000000)
        self.assertEqual(math.ldexp(1., -1000000), 0.)
        self.assertEqual(math.ldexp(-1., -1000000), -0.)
        self.assertEqual(math.ldexp(INF, 30), INF)
        self.assertEqual(math.ldexp(NINF, -213), NINF)
        self.assertTrue(math.isnan(math.ldexp(NAN, 0)))

        # large second argument
        for n in [10**5, 10**10, 10**20, 10**40]:
            self.assertEqual(math.ldexp(INF, -n), INF)
            self.assertEqual(math.ldexp(NINF, -n), NINF)
            self.assertEqual(math.ldexp(1., -n), 0.)
            self.assertEqual(math.ldexp(-1., -n), -0.)
            self.assertEqual(math.ldexp(0., -n), 0.)
            self.assertEqual(math.ldexp(-0., -n), -0.)
            self.assertTrue(math.isnan(math.ldexp(NAN, -n)))

            self.assertRaises(OverflowError, math.ldexp, 1., n)
            self.assertRaises(OverflowError, math.ldexp, -1., n)
            self.assertEqual(math.ldexp(0., n), 0.)
            self.assertEqual(math.ldexp(-0., n), -0.)
            self.assertEqual(math.ldexp(INF, n), INF)
            self.assertEqual(math.ldexp(NINF, n), NINF)
            self.assertTrue(math.isnan(math.ldexp(NAN, n)))

    eleza testLog(self):
        self.assertRaises(TypeError, math.log)
        self.ftest('log(1/e)', math.log(1/math.e), -1)
        self.ftest('log(1)', math.log(1), 0)
        self.ftest('log(e)', math.log(math.e), 1)
        self.ftest('log(32,2)', math.log(32,2), 5)
        self.ftest('log(10**40, 10)', math.log(10**40, 10), 40)
        self.ftest('log(10**40, 10**20)', math.log(10**40, 10**20), 2)
        self.ftest('log(10**1000)', math.log(10**1000),
                   2302.5850929940457)
        self.assertRaises(ValueError, math.log, -1.5)
        self.assertRaises(ValueError, math.log, -10**1000)
        self.assertRaises(ValueError, math.log, NINF)
        self.assertEqual(math.log(INF), INF)
        self.assertTrue(math.isnan(math.log(NAN)))

    eleza testLog1p(self):
        self.assertRaises(TypeError, math.log1p)
        for n in [2, 2**90, 2**300]:
            self.assertAlmostEqual(math.log1p(n), math.log1p(float(n)))
        self.assertRaises(ValueError, math.log1p, -1)
        self.assertEqual(math.log1p(INF), INF)

    @requires_IEEE_754
    eleza testLog2(self):
        self.assertRaises(TypeError, math.log2)

        # Check some integer values
        self.assertEqual(math.log2(1), 0.0)
        self.assertEqual(math.log2(2), 1.0)
        self.assertEqual(math.log2(4), 2.0)

        # Large integer values
        self.assertEqual(math.log2(2**1023), 1023.0)
        self.assertEqual(math.log2(2**1024), 1024.0)
        self.assertEqual(math.log2(2**2000), 2000.0)

        self.assertRaises(ValueError, math.log2, -1.5)
        self.assertRaises(ValueError, math.log2, NINF)
        self.assertTrue(math.isnan(math.log2(NAN)))

    @requires_IEEE_754
    # log2() is not accurate enough on Mac OS X Tiger (10.4)
    @support.requires_mac_ver(10, 5)
    eleza testLog2Exact(self):
        # Check that we get exact equality for log2 of powers of 2.
        actual = [math.log2(math.ldexp(1.0, n)) for n in range(-1074, 1024)]
        expected = [float(n) for n in range(-1074, 1024)]
        self.assertEqual(actual, expected)

    eleza testLog10(self):
        self.assertRaises(TypeError, math.log10)
        self.ftest('log10(0.1)', math.log10(0.1), -1)
        self.ftest('log10(1)', math.log10(1), 0)
        self.ftest('log10(10)', math.log10(10), 1)
        self.ftest('log10(10**1000)', math.log10(10**1000), 1000.0)
        self.assertRaises(ValueError, math.log10, -1.5)
        self.assertRaises(ValueError, math.log10, -10**1000)
        self.assertRaises(ValueError, math.log10, NINF)
        self.assertEqual(math.log(INF), INF)
        self.assertTrue(math.isnan(math.log10(NAN)))

    eleza testModf(self):
        self.assertRaises(TypeError, math.modf)

        eleza testmodf(name, result, expected):
            (v1, v2), (e1, e2) = result, expected
            ikiwa abs(v1-e1) > eps or abs(v2-e2):
                self.fail('%s returned %r, expected %r'%\
                          (name, result, expected))

        testmodf('modf(1.5)', math.modf(1.5), (0.5, 1.0))
        testmodf('modf(-1.5)', math.modf(-1.5), (-0.5, -1.0))

        self.assertEqual(math.modf(INF), (0.0, INF))
        self.assertEqual(math.modf(NINF), (-0.0, NINF))

        modf_nan = math.modf(NAN)
        self.assertTrue(math.isnan(modf_nan[0]))
        self.assertTrue(math.isnan(modf_nan[1]))

    eleza testPow(self):
        self.assertRaises(TypeError, math.pow)
        self.ftest('pow(0,1)', math.pow(0,1), 0)
        self.ftest('pow(1,0)', math.pow(1,0), 1)
        self.ftest('pow(2,1)', math.pow(2,1), 2)
        self.ftest('pow(2,-1)', math.pow(2,-1), 0.5)
        self.assertEqual(math.pow(INF, 1), INF)
        self.assertEqual(math.pow(NINF, 1), NINF)
        self.assertEqual((math.pow(1, INF)), 1.)
        self.assertEqual((math.pow(1, NINF)), 1.)
        self.assertTrue(math.isnan(math.pow(NAN, 1)))
        self.assertTrue(math.isnan(math.pow(2, NAN)))
        self.assertTrue(math.isnan(math.pow(0, NAN)))
        self.assertEqual(math.pow(1, NAN), 1)

        # pow(0., x)
        self.assertEqual(math.pow(0., INF), 0.)
        self.assertEqual(math.pow(0., 3.), 0.)
        self.assertEqual(math.pow(0., 2.3), 0.)
        self.assertEqual(math.pow(0., 2.), 0.)
        self.assertEqual(math.pow(0., 0.), 1.)
        self.assertEqual(math.pow(0., -0.), 1.)
        self.assertRaises(ValueError, math.pow, 0., -2.)
        self.assertRaises(ValueError, math.pow, 0., -2.3)
        self.assertRaises(ValueError, math.pow, 0., -3.)
        self.assertRaises(ValueError, math.pow, 0., NINF)
        self.assertTrue(math.isnan(math.pow(0., NAN)))

        # pow(INF, x)
        self.assertEqual(math.pow(INF, INF), INF)
        self.assertEqual(math.pow(INF, 3.), INF)
        self.assertEqual(math.pow(INF, 2.3), INF)
        self.assertEqual(math.pow(INF, 2.), INF)
        self.assertEqual(math.pow(INF, 0.), 1.)
        self.assertEqual(math.pow(INF, -0.), 1.)
        self.assertEqual(math.pow(INF, -2.), 0.)
        self.assertEqual(math.pow(INF, -2.3), 0.)
        self.assertEqual(math.pow(INF, -3.), 0.)
        self.assertEqual(math.pow(INF, NINF), 0.)
        self.assertTrue(math.isnan(math.pow(INF, NAN)))

        # pow(-0., x)
        self.assertEqual(math.pow(-0., INF), 0.)
        self.assertEqual(math.pow(-0., 3.), -0.)
        self.assertEqual(math.pow(-0., 2.3), 0.)
        self.assertEqual(math.pow(-0., 2.), 0.)
        self.assertEqual(math.pow(-0., 0.), 1.)
        self.assertEqual(math.pow(-0., -0.), 1.)
        self.assertRaises(ValueError, math.pow, -0., -2.)
        self.assertRaises(ValueError, math.pow, -0., -2.3)
        self.assertRaises(ValueError, math.pow, -0., -3.)
        self.assertRaises(ValueError, math.pow, -0., NINF)
        self.assertTrue(math.isnan(math.pow(-0., NAN)))

        # pow(NINF, x)
        self.assertEqual(math.pow(NINF, INF), INF)
        self.assertEqual(math.pow(NINF, 3.), NINF)
        self.assertEqual(math.pow(NINF, 2.3), INF)
        self.assertEqual(math.pow(NINF, 2.), INF)
        self.assertEqual(math.pow(NINF, 0.), 1.)
        self.assertEqual(math.pow(NINF, -0.), 1.)
        self.assertEqual(math.pow(NINF, -2.), 0.)
        self.assertEqual(math.pow(NINF, -2.3), 0.)
        self.assertEqual(math.pow(NINF, -3.), -0.)
        self.assertEqual(math.pow(NINF, NINF), 0.)
        self.assertTrue(math.isnan(math.pow(NINF, NAN)))

        # pow(-1, x)
        self.assertEqual(math.pow(-1., INF), 1.)
        self.assertEqual(math.pow(-1., 3.), -1.)
        self.assertRaises(ValueError, math.pow, -1., 2.3)
        self.assertEqual(math.pow(-1., 2.), 1.)
        self.assertEqual(math.pow(-1., 0.), 1.)
        self.assertEqual(math.pow(-1., -0.), 1.)
        self.assertEqual(math.pow(-1., -2.), 1.)
        self.assertRaises(ValueError, math.pow, -1., -2.3)
        self.assertEqual(math.pow(-1., -3.), -1.)
        self.assertEqual(math.pow(-1., NINF), 1.)
        self.assertTrue(math.isnan(math.pow(-1., NAN)))

        # pow(1, x)
        self.assertEqual(math.pow(1., INF), 1.)
        self.assertEqual(math.pow(1., 3.), 1.)
        self.assertEqual(math.pow(1., 2.3), 1.)
        self.assertEqual(math.pow(1., 2.), 1.)
        self.assertEqual(math.pow(1., 0.), 1.)
        self.assertEqual(math.pow(1., -0.), 1.)
        self.assertEqual(math.pow(1., -2.), 1.)
        self.assertEqual(math.pow(1., -2.3), 1.)
        self.assertEqual(math.pow(1., -3.), 1.)
        self.assertEqual(math.pow(1., NINF), 1.)
        self.assertEqual(math.pow(1., NAN), 1.)

        # pow(x, 0) should be 1 for any x
        self.assertEqual(math.pow(2.3, 0.), 1.)
        self.assertEqual(math.pow(-2.3, 0.), 1.)
        self.assertEqual(math.pow(NAN, 0.), 1.)
        self.assertEqual(math.pow(2.3, -0.), 1.)
        self.assertEqual(math.pow(-2.3, -0.), 1.)
        self.assertEqual(math.pow(NAN, -0.), 1.)

        # pow(x, y) is invalid ikiwa x is negative and y is not integral
        self.assertRaises(ValueError, math.pow, -1., 2.3)
        self.assertRaises(ValueError, math.pow, -15., -3.1)

        # pow(x, NINF)
        self.assertEqual(math.pow(1.9, NINF), 0.)
        self.assertEqual(math.pow(1.1, NINF), 0.)
        self.assertEqual(math.pow(0.9, NINF), INF)
        self.assertEqual(math.pow(0.1, NINF), INF)
        self.assertEqual(math.pow(-0.1, NINF), INF)
        self.assertEqual(math.pow(-0.9, NINF), INF)
        self.assertEqual(math.pow(-1.1, NINF), 0.)
        self.assertEqual(math.pow(-1.9, NINF), 0.)

        # pow(x, INF)
        self.assertEqual(math.pow(1.9, INF), INF)
        self.assertEqual(math.pow(1.1, INF), INF)
        self.assertEqual(math.pow(0.9, INF), 0.)
        self.assertEqual(math.pow(0.1, INF), 0.)
        self.assertEqual(math.pow(-0.1, INF), 0.)
        self.assertEqual(math.pow(-0.9, INF), 0.)
        self.assertEqual(math.pow(-1.1, INF), INF)
        self.assertEqual(math.pow(-1.9, INF), INF)

        # pow(x, y) should work for x negative, y an integer
        self.ftest('(-2.)**3.', math.pow(-2.0, 3.0), -8.0)
        self.ftest('(-2.)**2.', math.pow(-2.0, 2.0), 4.0)
        self.ftest('(-2.)**1.', math.pow(-2.0, 1.0), -2.0)
        self.ftest('(-2.)**0.', math.pow(-2.0, 0.0), 1.0)
        self.ftest('(-2.)**-0.', math.pow(-2.0, -0.0), 1.0)
        self.ftest('(-2.)**-1.', math.pow(-2.0, -1.0), -0.5)
        self.ftest('(-2.)**-2.', math.pow(-2.0, -2.0), 0.25)
        self.ftest('(-2.)**-3.', math.pow(-2.0, -3.0), -0.125)
        self.assertRaises(ValueError, math.pow, -2.0, -0.5)
        self.assertRaises(ValueError, math.pow, -2.0, 0.5)

        # the following tests have been commented out since they don't
        # really belong here:  the implementation of ** for floats is
        # independent of the implementation of math.pow
        #self.assertEqual(1**NAN, 1)
        #self.assertEqual(1**INF, 1)
        #self.assertEqual(1**NINF, 1)
        #self.assertEqual(1**0, 1)
        #self.assertEqual(1.**NAN, 1)
        #self.assertEqual(1.**INF, 1)
        #self.assertEqual(1.**NINF, 1)
        #self.assertEqual(1.**0, 1)

    eleza testRadians(self):
        self.assertRaises(TypeError, math.radians)
        self.ftest('radians(180)', math.radians(180), math.pi)
        self.ftest('radians(90)', math.radians(90), math.pi/2)
        self.ftest('radians(-45)', math.radians(-45), -math.pi/4)
        self.ftest('radians(0)', math.radians(0), 0)

    @requires_IEEE_754
    eleza testRemainder(self):
        kutoka fractions agiza Fraction

        eleza validate_spec(x, y, r):
            """
            Check that r matches remainder(x, y) according to the IEEE 754
            specification. Assumes that x, y and r are finite and y is nonzero.
            """
            fx, fy, fr = Fraction(x), Fraction(y), Fraction(r)
            # r should not exceed y/2 in absolute value
            self.assertLessEqual(abs(fr), abs(fy/2))
            # x - r should be an exact integer multiple of y
            n = (fx - fr) / fy
            self.assertEqual(n, int(n))
            ikiwa abs(fr) == abs(fy/2):
                # If |r| == |y/2|, n should be even.
                self.assertEqual(n/2, int(n/2))

        # triples (x, y, remainder(x, y)) in hexadecimal form.
        testcases = [
            # Remainders modulo 1, showing the ties-to-even behaviour.
            '-4.0 1 -0.0',
            '-3.8 1  0.8',
            '-3.0 1 -0.0',
            '-2.8 1 -0.8',
            '-2.0 1 -0.0',
            '-1.8 1  0.8',
            '-1.0 1 -0.0',
            '-0.8 1 -0.8',
            '-0.0 1 -0.0',
            ' 0.0 1  0.0',
            ' 0.8 1  0.8',
            ' 1.0 1  0.0',
            ' 1.8 1 -0.8',
            ' 2.0 1  0.0',
            ' 2.8 1  0.8',
            ' 3.0 1  0.0',
            ' 3.8 1 -0.8',
            ' 4.0 1  0.0',

            # Reductions modulo 2*pi
            '0x0.0p+0 0x1.921fb54442d18p+2 0x0.0p+0',
            '0x1.921fb54442d18p+0 0x1.921fb54442d18p+2  0x1.921fb54442d18p+0',
            '0x1.921fb54442d17p+1 0x1.921fb54442d18p+2  0x1.921fb54442d17p+1',
            '0x1.921fb54442d18p+1 0x1.921fb54442d18p+2  0x1.921fb54442d18p+1',
            '0x1.921fb54442d19p+1 0x1.921fb54442d18p+2 -0x1.921fb54442d17p+1',
            '0x1.921fb54442d17p+2 0x1.921fb54442d18p+2 -0x0.0000000000001p+2',
            '0x1.921fb54442d18p+2 0x1.921fb54442d18p+2  0x0p0',
            '0x1.921fb54442d19p+2 0x1.921fb54442d18p+2  0x0.0000000000001p+2',
            '0x1.2d97c7f3321d1p+3 0x1.921fb54442d18p+2  0x1.921fb54442d14p+1',
            '0x1.2d97c7f3321d2p+3 0x1.921fb54442d18p+2 -0x1.921fb54442d18p+1',
            '0x1.2d97c7f3321d3p+3 0x1.921fb54442d18p+2 -0x1.921fb54442d14p+1',
            '0x1.921fb54442d17p+3 0x1.921fb54442d18p+2 -0x0.0000000000001p+3',
            '0x1.921fb54442d18p+3 0x1.921fb54442d18p+2  0x0p0',
            '0x1.921fb54442d19p+3 0x1.921fb54442d18p+2  0x0.0000000000001p+3',
            '0x1.f6a7a2955385dp+3 0x1.921fb54442d18p+2  0x1.921fb54442d14p+1',
            '0x1.f6a7a2955385ep+3 0x1.921fb54442d18p+2  0x1.921fb54442d18p+1',
            '0x1.f6a7a2955385fp+3 0x1.921fb54442d18p+2 -0x1.921fb54442d14p+1',
            '0x1.1475cc9eedf00p+5 0x1.921fb54442d18p+2  0x1.921fb54442d10p+1',
            '0x1.1475cc9eedf01p+5 0x1.921fb54442d18p+2 -0x1.921fb54442d10p+1',

            # Symmetry with respect to signs.
            ' 1  0.c  0.4',
            '-1  0.c -0.4',
            ' 1 -0.c  0.4',
            '-1 -0.c -0.4',
            ' 1.4  0.c -0.4',
            '-1.4  0.c  0.4',
            ' 1.4 -0.c -0.4',
            '-1.4 -0.c  0.4',

            # Huge modulus, to check that the underlying algorithm doesn't
            # rely on 2.0 * modulus being representable.
            '0x1.dp+1023 0x1.4p+1023  0x0.9p+1023',
            '0x1.ep+1023 0x1.4p+1023 -0x0.ap+1023',
            '0x1.fp+1023 0x1.4p+1023 -0x0.9p+1023',
        ]

        for case in testcases:
            with self.subTest(case=case):
                x_hex, y_hex, expected_hex = case.split()
                x = float.kutokahex(x_hex)
                y = float.kutokahex(y_hex)
                expected = float.kutokahex(expected_hex)
                validate_spec(x, y, expected)
                actual = math.remainder(x, y)
                # Cheap way of checking that the floats are
                # as identical as we need them to be.
                self.assertEqual(actual.hex(), expected.hex())

        # Test tiny subnormal modulus: there's potential for
        # getting the implementation wrong here (for example,
        # by assuming that modulus/2 is exactly representable).
        tiny = float.kutokahex('1p-1074')  # min +ve subnormal
        for n in range(-25, 25):
            ikiwa n == 0:
                continue
            y = n * tiny
            for m in range(100):
                x = m * tiny
                actual = math.remainder(x, y)
                validate_spec(x, y, actual)
                actual = math.remainder(-x, y)
                validate_spec(-x, y, actual)

        # Special values.
        # NaNs should propagate as usual.
        for value in [NAN, 0.0, -0.0, 2.0, -2.3, NINF, INF]:
            self.assertIsNaN(math.remainder(NAN, value))
            self.assertIsNaN(math.remainder(value, NAN))

        # remainder(x, inf) is x, for non-nan non-infinite x.
        for value in [-2.3, -0.0, 0.0, 2.3]:
            self.assertEqual(math.remainder(value, INF), value)
            self.assertEqual(math.remainder(value, NINF), value)

        # remainder(x, 0) and remainder(infinity, x) for non-NaN x are invalid
        # operations according to IEEE 754-2008 7.2(f), and should raise.
        for value in [NINF, -2.3, -0.0, 0.0, 2.3, INF]:
            with self.assertRaises(ValueError):
                math.remainder(INF, value)
            with self.assertRaises(ValueError):
                math.remainder(NINF, value)
            with self.assertRaises(ValueError):
                math.remainder(value, 0.0)
            with self.assertRaises(ValueError):
                math.remainder(value, -0.0)

    eleza testSin(self):
        self.assertRaises(TypeError, math.sin)
        self.ftest('sin(0)', math.sin(0), 0)
        self.ftest('sin(pi/2)', math.sin(math.pi/2), 1)
        self.ftest('sin(-pi/2)', math.sin(-math.pi/2), -1)
        try:
            self.assertTrue(math.isnan(math.sin(INF)))
            self.assertTrue(math.isnan(math.sin(NINF)))
        except ValueError:
            self.assertRaises(ValueError, math.sin, INF)
            self.assertRaises(ValueError, math.sin, NINF)
        self.assertTrue(math.isnan(math.sin(NAN)))

    eleza testSinh(self):
        self.assertRaises(TypeError, math.sinh)
        self.ftest('sinh(0)', math.sinh(0), 0)
        self.ftest('sinh(1)**2-cosh(1)**2', math.sinh(1)**2-math.cosh(1)**2, -1)
        self.ftest('sinh(1)+sinh(-1)', math.sinh(1)+math.sinh(-1), 0)
        self.assertEqual(math.sinh(INF), INF)
        self.assertEqual(math.sinh(NINF), NINF)
        self.assertTrue(math.isnan(math.sinh(NAN)))

    eleza testSqrt(self):
        self.assertRaises(TypeError, math.sqrt)
        self.ftest('sqrt(0)', math.sqrt(0), 0)
        self.ftest('sqrt(1)', math.sqrt(1), 1)
        self.ftest('sqrt(4)', math.sqrt(4), 2)
        self.assertEqual(math.sqrt(INF), INF)
        self.assertRaises(ValueError, math.sqrt, -1)
        self.assertRaises(ValueError, math.sqrt, NINF)
        self.assertTrue(math.isnan(math.sqrt(NAN)))

    eleza testTan(self):
        self.assertRaises(TypeError, math.tan)
        self.ftest('tan(0)', math.tan(0), 0)
        self.ftest('tan(pi/4)', math.tan(math.pi/4), 1)
        self.ftest('tan(-pi/4)', math.tan(-math.pi/4), -1)
        try:
            self.assertTrue(math.isnan(math.tan(INF)))
            self.assertTrue(math.isnan(math.tan(NINF)))
        except:
            self.assertRaises(ValueError, math.tan, INF)
            self.assertRaises(ValueError, math.tan, NINF)
        self.assertTrue(math.isnan(math.tan(NAN)))

    eleza testTanh(self):
        self.assertRaises(TypeError, math.tanh)
        self.ftest('tanh(0)', math.tanh(0), 0)
        self.ftest('tanh(1)+tanh(-1)', math.tanh(1)+math.tanh(-1), 0,
                   abs_tol=ulp(1))
        self.ftest('tanh(inf)', math.tanh(INF), 1)
        self.ftest('tanh(-inf)', math.tanh(NINF), -1)
        self.assertTrue(math.isnan(math.tanh(NAN)))

    @requires_IEEE_754
    eleza testTanhSign(self):
        # check that tanh(-0.) == -0. on IEEE 754 systems
        self.assertEqual(math.tanh(-0.), -0.)
        self.assertEqual(math.copysign(1., math.tanh(-0.)),
                         math.copysign(1., -0.))

    eleza test_trunc(self):
        self.assertEqual(math.trunc(1), 1)
        self.assertEqual(math.trunc(-1), -1)
        self.assertEqual(type(math.trunc(1)), int)
        self.assertEqual(type(math.trunc(1.5)), int)
        self.assertEqual(math.trunc(1.5), 1)
        self.assertEqual(math.trunc(-1.5), -1)
        self.assertEqual(math.trunc(1.999999), 1)
        self.assertEqual(math.trunc(-1.999999), -1)
        self.assertEqual(math.trunc(-0.999999), -0)
        self.assertEqual(math.trunc(-100.999), -100)

        kundi TestTrunc(object):
            eleza __trunc__(self):
                rudisha 23

        kundi TestNoTrunc(object):
            pass

        self.assertEqual(math.trunc(TestTrunc()), 23)

        self.assertRaises(TypeError, math.trunc)
        self.assertRaises(TypeError, math.trunc, 1, 2)
        self.assertRaises(TypeError, math.trunc, TestNoTrunc())

    eleza testIsfinite(self):
        self.assertTrue(math.isfinite(0.0))
        self.assertTrue(math.isfinite(-0.0))
        self.assertTrue(math.isfinite(1.0))
        self.assertTrue(math.isfinite(-1.0))
        self.assertFalse(math.isfinite(float("nan")))
        self.assertFalse(math.isfinite(float("inf")))
        self.assertFalse(math.isfinite(float("-inf")))

    eleza testIsnan(self):
        self.assertTrue(math.isnan(float("nan")))
        self.assertTrue(math.isnan(float("-nan")))
        self.assertTrue(math.isnan(float("inf") * 0.))
        self.assertFalse(math.isnan(float("inf")))
        self.assertFalse(math.isnan(0.))
        self.assertFalse(math.isnan(1.))

    eleza testIsinf(self):
        self.assertTrue(math.isinf(float("inf")))
        self.assertTrue(math.isinf(float("-inf")))
        self.assertTrue(math.isinf(1E400))
        self.assertTrue(math.isinf(-1E400))
        self.assertFalse(math.isinf(float("nan")))
        self.assertFalse(math.isinf(0.))
        self.assertFalse(math.isinf(1.))

    @requires_IEEE_754
    eleza test_nan_constant(self):
        self.assertTrue(math.isnan(math.nan))

    @requires_IEEE_754
    eleza test_inf_constant(self):
        self.assertTrue(math.isinf(math.inf))
        self.assertGreater(math.inf, 0.0)
        self.assertEqual(math.inf, float("inf"))
        self.assertEqual(-math.inf, float("-inf"))

    # RED_FLAG 16-Oct-2000 Tim
    # While 2.0 is more consistent about exceptions than previous releases, it
    # still fails this part of the test on some platforms.  For now, we only
    # *run* test_exceptions() in verbose mode, so that this isn't normally
    # tested.
    @unittest.skipUnless(verbose, 'requires verbose mode')
    eleza test_exceptions(self):
        try:
            x = math.exp(-1000000000)
        except:
            # mathmodule.c is failing to weed out underflows kutoka libm, or
            # we've got an fp format with huge dynamic range
            self.fail("underflowing exp() should not have raised "
                        "an exception")
        ikiwa x != 0:
            self.fail("underflowing exp() should have returned 0")

        # If this fails, probably using a strict IEEE-754 conforming libm, and x
        # is +Inf afterwards.  But Python wants overflows detected by default.
        try:
            x = math.exp(1000000000)
        except OverflowError:
            pass
        else:
            self.fail("overflowing exp() didn't trigger OverflowError")

        # If this fails, it could be a puzzle.  One odd possibility is that
        # mathmodule.c's macros are getting confused while comparing
        # Inf (HUGE_VAL) to a NaN, and artificially setting errno to ERANGE
        # as a result (and so raising OverflowError instead).
        try:
            x = math.sqrt(-1.0)
        except ValueError:
            pass
        else:
            self.fail("sqrt(-1) didn't raise ValueError")

    @requires_IEEE_754
    eleza test_testfile(self):
        # Some tests need to be skipped on ancient OS X versions.
        # See issue #27953.
        SKIP_ON_TIGER = {'tan0064'}

        osx_version = None
        ikiwa sys.platform == 'darwin':
            version_txt = platform.mac_ver()[0]
            try:
                osx_version = tuple(map(int, version_txt.split('.')))
            except ValueError:
                pass

        fail_fmt = "{}: {}({!r}): {}"

        failures = []
        for id, fn, ar, ai, er, ei, flags in parse_testfile(test_file):
            # Skip ikiwa either the input or result is complex
            ikiwa ai != 0.0 or ei != 0.0:
                continue
            ikiwa fn in ['rect', 'polar']:
                # no real versions of rect, polar
                continue
            # Skip certain tests on OS X 10.4.
            ikiwa osx_version is not None and osx_version < (10, 5):
                ikiwa id in SKIP_ON_TIGER:
                    continue

            func = getattr(math, fn)

            ikiwa 'invalid' in flags or 'divide-by-zero' in flags:
                er = 'ValueError'
            elikiwa 'overflow' in flags:
                er = 'OverflowError'

            try:
                result = func(ar)
            except ValueError:
                result = 'ValueError'
            except OverflowError:
                result = 'OverflowError'

            # Default tolerances
            ulp_tol, abs_tol = 5, 0.0

            failure = result_check(er, result, ulp_tol, abs_tol)
            ikiwa failure is None:
                continue

            msg = fail_fmt.format(id, fn, ar, failure)
            failures.append(msg)

        ikiwa failures:
            self.fail('Failures in test_testfile:\n  ' +
                      '\n  '.join(failures))

    @requires_IEEE_754
    eleza test_mtestfile(self):
        fail_fmt = "{}: {}({!r}): {}"

        failures = []
        for id, fn, arg, expected, flags in parse_mtestfile(math_testcases):
            func = getattr(math, fn)

            ikiwa 'invalid' in flags or 'divide-by-zero' in flags:
                expected = 'ValueError'
            elikiwa 'overflow' in flags:
                expected = 'OverflowError'

            try:
                got = func(arg)
            except ValueError:
                got = 'ValueError'
            except OverflowError:
                got = 'OverflowError'

            # Default tolerances
            ulp_tol, abs_tol = 5, 0.0

            # Exceptions to the defaults
            ikiwa fn == 'gamma':
                # Experimental results on one platform gave
                # an accuracy of <= 10 ulps across the entire float
                # domain. We weaken that to require 20 ulp accuracy.
                ulp_tol = 20

            elikiwa fn == 'lgamma':
                # we use a weaker accuracy test for lgamma;
                # lgamma only achieves an absolute error of
                # a few multiples of the machine accuracy, in
                # general.
                abs_tol = 1e-15

            elikiwa fn == 'erfc' and arg >= 0.0:
                # erfc has less-than-ideal accuracy for large
                # arguments (x ~ 25 or so), mainly due to the
                # error involved in computing exp(-x*x).
                #
                # Observed between CPython and mpmath at 25 dp:
                #       x <  0 : err <= 2 ulp
                #  0 <= x <  1 : err <= 10 ulp
                #  1 <= x < 10 : err <= 100 ulp
                # 10 <= x < 20 : err <= 300 ulp
                # 20 <= x      : < 600 ulp
                #
                ikiwa arg < 1.0:
                    ulp_tol = 10
                elikiwa arg < 10.0:
                    ulp_tol = 100
                else:
                    ulp_tol = 1000

            failure = result_check(expected, got, ulp_tol, abs_tol)
            ikiwa failure is None:
                continue

            msg = fail_fmt.format(id, fn, arg, failure)
            failures.append(msg)

        ikiwa failures:
            self.fail('Failures in test_mtestfile:\n  ' +
                      '\n  '.join(failures))

    eleza test_prod(self):
        prod = math.prod
        self.assertEqual(prod([]), 1)
        self.assertEqual(prod([], start=5), 5)
        self.assertEqual(prod(list(range(2,8))), 5040)
        self.assertEqual(prod(iter(list(range(2,8)))), 5040)
        self.assertEqual(prod(range(1, 10), start=10), 3628800)

        self.assertEqual(prod([1, 2, 3, 4, 5]), 120)
        self.assertEqual(prod([1.0, 2.0, 3.0, 4.0, 5.0]), 120.0)
        self.assertEqual(prod([1, 2, 3, 4.0, 5.0]), 120.0)
        self.assertEqual(prod([1.0, 2.0, 3.0, 4, 5]), 120.0)

        # Test overflow in fast-path for integers
        self.assertEqual(prod([1, 1, 2**32, 1, 1]), 2**32)
        # Test overflow in fast-path for floats
        self.assertEqual(prod([1.0, 1.0, 2**32, 1, 1]), float(2**32))

        self.assertRaises(TypeError, prod)
        self.assertRaises(TypeError, prod, 42)
        self.assertRaises(TypeError, prod, ['a', 'b', 'c'])
        self.assertRaises(TypeError, prod, ['a', 'b', 'c'], '')
        self.assertRaises(TypeError, prod, [b'a', b'c'], b'')
        values = [bytearray(b'a'), bytearray(b'b')]
        self.assertRaises(TypeError, prod, values, bytearray(b''))
        self.assertRaises(TypeError, prod, [[1], [2], [3]])
        self.assertRaises(TypeError, prod, [{2:3}])
        self.assertRaises(TypeError, prod, [{2:3}]*2, {2:3})
        self.assertRaises(TypeError, prod, [[1], [2], [3]], [])
        with self.assertRaises(TypeError):
            prod([10, 20], [30, 40])     # start is a keyword-only argument

        self.assertEqual(prod([0, 1, 2, 3]), 0)
        self.assertEqual(prod([1, 0, 2, 3]), 0)
        self.assertEqual(prod([1, 2, 3, 0]), 0)

        eleza _naive_prod(iterable, start=1):
            for elem in iterable:
                start *= elem
            rudisha start

        # Big integers

        iterable = range(1, 10000)
        self.assertEqual(prod(iterable), _naive_prod(iterable))
        iterable = range(-10000, -1)
        self.assertEqual(prod(iterable), _naive_prod(iterable))
        iterable = range(-1000, 1000)
        self.assertEqual(prod(iterable), 0)

        # Big floats

        iterable = [float(x) for x in range(1, 1000)]
        self.assertEqual(prod(iterable), _naive_prod(iterable))
        iterable = [float(x) for x in range(-1000, -1)]
        self.assertEqual(prod(iterable), _naive_prod(iterable))
        iterable = [float(x) for x in range(-1000, 1000)]
        self.assertIsNaN(prod(iterable))

        # Float tests

        self.assertIsNaN(prod([1, 2, 3, float("nan"), 2, 3]))
        self.assertIsNaN(prod([1, 0, float("nan"), 2, 3]))
        self.assertIsNaN(prod([1, float("nan"), 0, 3]))
        self.assertIsNaN(prod([1, float("inf"), float("nan"),3]))
        self.assertIsNaN(prod([1, float("-inf"), float("nan"),3]))
        self.assertIsNaN(prod([1, float("nan"), float("inf"),3]))
        self.assertIsNaN(prod([1, float("nan"), float("-inf"),3]))

        self.assertEqual(prod([1, 2, 3, float('inf'),-3,4]), float('-inf'))
        self.assertEqual(prod([1, 2, 3, float('-inf'),-3,4]), float('inf'))

        self.assertIsNaN(prod([1,2,0,float('inf'), -3, 4]))
        self.assertIsNaN(prod([1,2,0,float('-inf'), -3, 4]))
        self.assertIsNaN(prod([1, 2, 3, float('inf'), -3, 0, 3]))
        self.assertIsNaN(prod([1, 2, 3, float('-inf'), -3, 0, 2]))

        # Type preservation

        self.assertEqual(type(prod([1, 2, 3, 4, 5, 6])), int)
        self.assertEqual(type(prod([1, 2.0, 3, 4, 5, 6])), float)
        self.assertEqual(type(prod(range(1, 10000))), int)
        self.assertEqual(type(prod(range(1, 10000), start=1.0)), float)
        self.assertEqual(type(prod([1, decimal.Decimal(2.0), 3, 4, 5, 6])),
                         decimal.Decimal)

    # Custom assertions.

    eleza assertIsNaN(self, value):
        ikiwa not math.isnan(value):
            self.fail("Expected a NaN, got {!r}.".format(value))


kundi IsCloseTests(unittest.TestCase):
    isclose = math.isclose  # subclasses should override this

    eleza assertIsClose(self, a, b, *args, **kwargs):
        self.assertTrue(self.isclose(a, b, *args, **kwargs),
                        msg="%s and %s should be close!" % (a, b))

    eleza assertIsNotClose(self, a, b, *args, **kwargs):
        self.assertFalse(self.isclose(a, b, *args, **kwargs),
                         msg="%s and %s should not be close!" % (a, b))

    eleza assertAllClose(self, examples, *args, **kwargs):
        for a, b in examples:
            self.assertIsClose(a, b, *args, **kwargs)

    eleza assertAllNotClose(self, examples, *args, **kwargs):
        for a, b in examples:
            self.assertIsNotClose(a, b, *args, **kwargs)

    eleza test_negative_tolerances(self):
        # ValueError should be raised ikiwa either tolerance is less than zero
        with self.assertRaises(ValueError):
            self.assertIsClose(1, 1, rel_tol=-1e-100)
        with self.assertRaises(ValueError):
            self.assertIsClose(1, 1, rel_tol=1e-100, abs_tol=-1e10)

    eleza test_identical(self):
        # identical values must test as close
        identical_examples = [(2.0, 2.0),
                              (0.1e200, 0.1e200),
                              (1.123e-300, 1.123e-300),
                              (12345, 12345.0),
                              (0.0, -0.0),
                              (345678, 345678)]
        self.assertAllClose(identical_examples, rel_tol=0.0, abs_tol=0.0)

    eleza test_eight_decimal_places(self):
        # examples that are close to 1e-8, but not 1e-9
        eight_decimal_places_examples = [(1e8, 1e8 + 1),
                                         (-1e-8, -1.000000009e-8),
                                         (1.12345678, 1.12345679)]
        self.assertAllClose(eight_decimal_places_examples, rel_tol=1e-8)
        self.assertAllNotClose(eight_decimal_places_examples, rel_tol=1e-9)

    eleza test_near_zero(self):
        # values close to zero
        near_zero_examples = [(1e-9, 0.0),
                              (-1e-9, 0.0),
                              (-1e-150, 0.0)]
        # these should not be close to any rel_tol
        self.assertAllNotClose(near_zero_examples, rel_tol=0.9)
        # these should be close to abs_tol=1e-8
        self.assertAllClose(near_zero_examples, abs_tol=1e-8)

    eleza test_identical_infinite(self):
        # these are close regardless of tolerance -- i.e. they are equal
        self.assertIsClose(INF, INF)
        self.assertIsClose(INF, INF, abs_tol=0.0)
        self.assertIsClose(NINF, NINF)
        self.assertIsClose(NINF, NINF, abs_tol=0.0)

    eleza test_inf_ninf_nan(self):
        # these should never be close (following IEEE 754 rules for equality)
        not_close_examples = [(NAN, NAN),
                              (NAN, 1e-100),
                              (1e-100, NAN),
                              (INF, NAN),
                              (NAN, INF),
                              (INF, NINF),
                              (INF, 1.0),
                              (1.0, INF),
                              (INF, 1e308),
                              (1e308, INF)]
        # use largest reasonable tolerance
        self.assertAllNotClose(not_close_examples, abs_tol=0.999999999999999)

    eleza test_zero_tolerance(self):
        # test with zero tolerance
        zero_tolerance_close_examples = [(1.0, 1.0),
                                         (-3.4, -3.4),
                                         (-1e-300, -1e-300)]
        self.assertAllClose(zero_tolerance_close_examples, rel_tol=0.0)

        zero_tolerance_not_close_examples = [(1.0, 1.000000000000001),
                                             (0.99999999999999, 1.0),
                                             (1.0e200, .999999999999999e200)]
        self.assertAllNotClose(zero_tolerance_not_close_examples, rel_tol=0.0)

    eleza test_asymmetry(self):
        # test the asymmetry example kutoka PEP 485
        self.assertAllClose([(9, 10), (10, 9)], rel_tol=0.1)

    eleza test_integers(self):
        # test with integer values
        integer_examples = [(100000001, 100000000),
                            (123456789, 123456788)]

        self.assertAllClose(integer_examples, rel_tol=1e-8)
        self.assertAllNotClose(integer_examples, rel_tol=1e-9)

    eleza test_decimals(self):
        # test with Decimal values
        kutoka decimal agiza Decimal

        decimal_examples = [(Decimal('1.00000001'), Decimal('1.0')),
                            (Decimal('1.00000001e-20'), Decimal('1.0e-20')),
                            (Decimal('1.00000001e-100'), Decimal('1.0e-100')),
                            (Decimal('1.00000001e20'), Decimal('1.0e20'))]
        self.assertAllClose(decimal_examples, rel_tol=1e-8)
        self.assertAllNotClose(decimal_examples, rel_tol=1e-9)

    eleza test_fractions(self):
        # test with Fraction values
        kutoka fractions agiza Fraction

        fraction_examples = [
            (Fraction(1, 100000000) + 1, Fraction(1)),
            (Fraction(100000001), Fraction(100000000)),
            (Fraction(10**8 + 1, 10**28), Fraction(1, 10**20))]
        self.assertAllClose(fraction_examples, rel_tol=1e-8)
        self.assertAllNotClose(fraction_examples, rel_tol=1e-9)

    eleza testPerm(self):
        perm = math.perm
        factorial = math.factorial
        # Test ikiwa factorial definition is satisfied
        for n in range(100):
            for k in range(n + 1):
                self.assertEqual(perm(n, k),
                                 factorial(n) // factorial(n - k))

        # Test for Pascal's identity
        for n in range(1, 100):
            for k in range(1, n):
                self.assertEqual(perm(n, k), perm(n - 1, k - 1) * k + perm(n - 1, k))

        # Test corner cases
        for n in range(1, 100):
            self.assertEqual(perm(n, 0), 1)
            self.assertEqual(perm(n, 1), n)
            self.assertEqual(perm(n, n), factorial(n))

        # Test one argument form
        for n in range(20):
            self.assertEqual(perm(n), factorial(n))
            self.assertEqual(perm(n, None), factorial(n))

        # Raises TypeError ikiwa any argument is non-integer or argument count is
        # not 1 or 2
        self.assertRaises(TypeError, perm, 10, 1.0)
        self.assertRaises(TypeError, perm, 10, decimal.Decimal(1.0))
        self.assertRaises(TypeError, perm, 10, "1")
        self.assertRaises(TypeError, perm, 10.0, 1)
        self.assertRaises(TypeError, perm, decimal.Decimal(10.0), 1)
        self.assertRaises(TypeError, perm, "10", 1)

        self.assertRaises(TypeError, perm)
        self.assertRaises(TypeError, perm, 10, 1, 3)
        self.assertRaises(TypeError, perm)

        # Raises Value error ikiwa not k or n are negative numbers
        self.assertRaises(ValueError, perm, -1, 1)
        self.assertRaises(ValueError, perm, -2**1000, 1)
        self.assertRaises(ValueError, perm, 1, -1)
        self.assertRaises(ValueError, perm, 1, -2**1000)

        # Returns zero ikiwa k is greater than n
        self.assertEqual(perm(1, 2), 0)
        self.assertEqual(perm(1, 2**1000), 0)

        n = 2**1000
        self.assertEqual(perm(n, 0), 1)
        self.assertEqual(perm(n, 1), n)
        self.assertEqual(perm(n, 2), n * (n-1))
        ikiwa support.check_impl_detail(cpython=True):
            self.assertRaises(OverflowError, perm, n, n)

        for n, k in (True, True), (True, False), (False, False):
            self.assertEqual(perm(n, k), 1)
            self.assertIs(type(perm(n, k)), int)
        self.assertEqual(perm(IntSubclass(5), IntSubclass(2)), 20)
        self.assertEqual(perm(MyIndexable(5), MyIndexable(2)), 20)
        for k in range(3):
            self.assertIs(type(perm(IntSubclass(5), IntSubclass(k))), int)
            self.assertIs(type(perm(MyIndexable(5), MyIndexable(k))), int)

    eleza testComb(self):
        comb = math.comb
        factorial = math.factorial
        # Test ikiwa factorial definition is satisfied
        for n in range(100):
            for k in range(n + 1):
                self.assertEqual(comb(n, k), factorial(n)
                    // (factorial(k) * factorial(n - k)))

        # Test for Pascal's identity
        for n in range(1, 100):
            for k in range(1, n):
                self.assertEqual(comb(n, k), comb(n - 1, k - 1) + comb(n - 1, k))

        # Test corner cases
        for n in range(100):
            self.assertEqual(comb(n, 0), 1)
            self.assertEqual(comb(n, n), 1)

        for n in range(1, 100):
            self.assertEqual(comb(n, 1), n)
            self.assertEqual(comb(n, n - 1), n)

        # Test Symmetry
        for n in range(100):
            for k in range(n // 2):
                self.assertEqual(comb(n, k), comb(n, n - k))

        # Raises TypeError ikiwa any argument is non-integer or argument count is
        # not 2
        self.assertRaises(TypeError, comb, 10, 1.0)
        self.assertRaises(TypeError, comb, 10, decimal.Decimal(1.0))
        self.assertRaises(TypeError, comb, 10, "1")
        self.assertRaises(TypeError, comb, 10.0, 1)
        self.assertRaises(TypeError, comb, decimal.Decimal(10.0), 1)
        self.assertRaises(TypeError, comb, "10", 1)

        self.assertRaises(TypeError, comb, 10)
        self.assertRaises(TypeError, comb, 10, 1, 3)
        self.assertRaises(TypeError, comb)

        # Raises Value error ikiwa not k or n are negative numbers
        self.assertRaises(ValueError, comb, -1, 1)
        self.assertRaises(ValueError, comb, -2**1000, 1)
        self.assertRaises(ValueError, comb, 1, -1)
        self.assertRaises(ValueError, comb, 1, -2**1000)

        # Returns zero ikiwa k is greater than n
        self.assertEqual(comb(1, 2), 0)
        self.assertEqual(comb(1, 2**1000), 0)

        n = 2**1000
        self.assertEqual(comb(n, 0), 1)
        self.assertEqual(comb(n, 1), n)
        self.assertEqual(comb(n, 2), n * (n-1) // 2)
        self.assertEqual(comb(n, n), 1)
        self.assertEqual(comb(n, n-1), n)
        self.assertEqual(comb(n, n-2), n * (n-1) // 2)
        ikiwa support.check_impl_detail(cpython=True):
            self.assertRaises(OverflowError, comb, n, n//2)

        for n, k in (True, True), (True, False), (False, False):
            self.assertEqual(comb(n, k), 1)
            self.assertIs(type(comb(n, k)), int)
        self.assertEqual(comb(IntSubclass(5), IntSubclass(2)), 10)
        self.assertEqual(comb(MyIndexable(5), MyIndexable(2)), 10)
        for k in range(3):
            self.assertIs(type(comb(IntSubclass(5), IntSubclass(k))), int)
            self.assertIs(type(comb(MyIndexable(5), MyIndexable(k))), int)


eleza test_main():
    kutoka doctest agiza DocFileSuite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MathTests))
    suite.addTest(unittest.makeSuite(IsCloseTests))
    suite.addTest(DocFileSuite("ieee754.txt"))
    run_unittest(suite)

ikiwa __name__ == '__main__':
    test_main()
