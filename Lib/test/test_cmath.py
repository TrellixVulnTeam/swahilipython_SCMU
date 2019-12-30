kutoka test.support agiza requires_IEEE_754, cpython_only
kutoka test.test_math agiza parse_testfile, test_file
agiza test.test_math as test_math
agiza unittest
agiza cmath, math
kutoka cmath agiza phase, polar, rect, pi
agiza platform
agiza sys


INF = float('inf')
NAN = float('nan')

complex_zeros = [complex(x, y) kila x kwenye [0.0, -0.0] kila y kwenye [0.0, -0.0]]
complex_infinities = [complex(x, y) kila x, y kwenye [
        (INF, 0.0),  # 1st quadrant
        (INF, 2.3),
        (INF, INF),
        (2.3, INF),
        (0.0, INF),
        (-0.0, INF), # 2nd quadrant
        (-2.3, INF),
        (-INF, INF),
        (-INF, 2.3),
        (-INF, 0.0),
        (-INF, -0.0), # 3rd quadrant
        (-INF, -2.3),
        (-INF, -INF),
        (-2.3, -INF),
        (-0.0, -INF),
        (0.0, -INF), # 4th quadrant
        (2.3, -INF),
        (INF, -INF),
        (INF, -2.3),
        (INF, -0.0)
        ]]
complex_nans = [complex(x, y) kila x, y kwenye [
        (NAN, -INF),
        (NAN, -2.3),
        (NAN, -0.0),
        (NAN, 0.0),
        (NAN, 2.3),
        (NAN, INF),
        (-INF, NAN),
        (-2.3, NAN),
        (-0.0, NAN),
        (0.0, NAN),
        (2.3, NAN),
        (INF, NAN)
        ]]

kundi CMathTests(unittest.TestCase):
    # list of all functions kwenye cmath
    test_functions = [getattr(cmath, fname) kila fname kwenye [
            'acos', 'acosh', 'asin', 'asinh', 'atan', 'atanh',
            'cos', 'cosh', 'exp', 'log', 'log10', 'sin', 'sinh',
            'sqrt', 'tan', 'tanh']]
    # test first na second arguments independently kila 2-argument log
    test_functions.append(lambda x : cmath.log(x, 1729. + 0j))
    test_functions.append(lambda x : cmath.log(14.-27j, x))

    eleza setUp(self):
        self.test_values = open(test_file)

    eleza tearDown(self):
        self.test_values.close()

    eleza assertFloatIdentical(self, x, y):
        """Fail unless floats x na y are identical, kwenye the sense that:
        (1) both x na y are nans, or
        (2) both x na y are infinities, ukijumuisha the same sign, or
        (3) both x na y are zeros, ukijumuisha the same sign, or
        (4) x na y are both finite na nonzero, na x == y

        """
        msg = 'floats {!r} na {!r} are sio identical'

        ikiwa math.isnan(x) ama math.isnan(y):
            ikiwa math.isnan(x) na math.isnan(y):
                return
        elikiwa x == y:
            ikiwa x != 0.0:
                return
            # both zero; check that signs match
            elikiwa math.copysign(1.0, x) == math.copysign(1.0, y):
                return
            isipokua:
                msg += ': zeros have different signs'
        self.fail(msg.format(x, y))

    eleza assertComplexIdentical(self, x, y):
        """Fail unless complex numbers x na y have equal values na signs.

        In particular, ikiwa x na y both have real (or imaginary) part
        zero, but the zeros have different signs, this test will fail.

        """
        self.assertFloatIdentical(x.real, y.real)
        self.assertFloatIdentical(x.imag, y.imag)

    eleza rAssertAlmostEqual(self, a, b, rel_err = 2e-15, abs_err = 5e-323,
                           msg=Tupu):
        """Fail ikiwa the two floating-point numbers are sio almost equal.

        Determine whether floating-point values a na b are equal to within
        a (small) rounding error.  The default values kila rel_err and
        abs_err are chosen to be suitable kila platforms where a float is
        represented by an IEEE 754 double.  They allow an error of between
        9 na 19 ulps.
        """

        # special values testing
        ikiwa math.isnan(a):
            ikiwa math.isnan(b):
                return
            self.fail(msg ama '{!r} should be nan'.format(b))

        ikiwa math.isinf(a):
            ikiwa a == b:
                return
            self.fail(msg ama 'finite result where infinity expected: '
                      'expected {!r}, got {!r}'.format(a, b))

        # ikiwa both a na b are zero, check whether they have the same sign
        # (in theory there are examples where it would be legitimate kila a
        # na b to have opposite signs; kwenye practice these hardly ever
        # occur).
        ikiwa sio a na sio b:
            ikiwa math.copysign(1., a) != math.copysign(1., b):
                self.fail(msg ama 'zero has wrong sign: expected {!r}, '
                          'got {!r}'.format(a, b))

        # ikiwa a-b overflows, ama b ni infinite, rudisha Uongo.  Again, in
        # theory there are examples where a ni within a few ulps of the
        # max representable float, na then b could legitimately be
        # infinite.  In practice these examples are rare.
        jaribu:
            absolute_error = abs(b-a)
        except OverflowError:
            pass
        isipokua:
            # test passes ikiwa either the absolute error ama the relative
            # error ni sufficiently small.  The defaults amount to an
            # error of between 9 ulps na 19 ulps on an IEEE-754 compliant
            # machine.
            ikiwa absolute_error <= max(abs_err, rel_err * abs(a)):
                return
        self.fail(msg or
                  '{!r} na {!r} are sio sufficiently close'.format(a, b))

    eleza test_constants(self):
        e_expected = 2.71828182845904523536
        pi_expected = 3.14159265358979323846
        self.assertAlmostEqual(cmath.pi, pi_expected, places=9,
            msg="cmath.pi ni {}; should be {}".format(cmath.pi, pi_expected))
        self.assertAlmostEqual(cmath.e, e_expected, places=9,
            msg="cmath.e ni {}; should be {}".format(cmath.e, e_expected))

    eleza test_infinity_and_nan_constants(self):
        self.assertEqual(cmath.inf.real, math.inf)
        self.assertEqual(cmath.inf.imag, 0.0)
        self.assertEqual(cmath.infj.real, 0.0)
        self.assertEqual(cmath.infj.imag, math.inf)

        self.assertKweli(math.isnan(cmath.nan.real))
        self.assertEqual(cmath.nan.imag, 0.0)
        self.assertEqual(cmath.nanj.real, 0.0)
        self.assertKweli(math.isnan(cmath.nanj.imag))

        # Check consistency ukijumuisha reprs.
        self.assertEqual(repr(cmath.inf), "inf")
        self.assertEqual(repr(cmath.infj), "infj")
        self.assertEqual(repr(cmath.nan), "nan")
        self.assertEqual(repr(cmath.nanj), "nanj")

    eleza test_user_object(self):
        # Test automatic calling of __complex__ na __float__ by cmath
        # functions

        # some random values to use as test values; we avoid values
        # kila which any of the functions kwenye cmath ni undefined
        # (i.e. 0., 1., -1., 1j, -1j) ama would cause overflow
        cx_arg = 4.419414439 + 1.497100113j
        flt_arg = -6.131677725

        # a variety of non-complex numbers, used to check that
        # non-complex rudisha values kutoka __complex__ give an error
        non_complexes = ["not complex", 1, 5, 2., Tupu,
                         object(), NotImplemented]

        # Now we introduce a variety of classes whose instances might
        # end up being passed to the cmath functions

        # usual case: new-style kundi implementing __complex__
        kundi MyComplex(object):
            eleza __init__(self, value):
                self.value = value
            eleza __complex__(self):
                rudisha self.value

        # old-style kundi implementing __complex__
        kundi MyComplexOS:
            eleza __init__(self, value):
                self.value = value
            eleza __complex__(self):
                rudisha self.value

        # classes kila which __complex__ raises an exception
        kundi SomeException(Exception):
            pass
        kundi MyComplexException(object):
            eleza __complex__(self):
                 ashiria SomeException
        kundi MyComplexExceptionOS:
            eleza __complex__(self):
                 ashiria SomeException

        # some classes sio providing __float__ ama __complex__
        kundi NeitherComplexNorFloat(object):
            pass
        kundi NeitherComplexNorFloatOS:
            pass
        kundi Index:
            eleza __int__(self): rudisha 2
            eleza __index__(self): rudisha 2
        kundi MyInt:
            eleza __int__(self): rudisha 2

        # other possible combinations of __float__ na __complex__
        # that should work
        kundi FloatAndComplex(object):
            eleza __float__(self):
                rudisha flt_arg
            eleza __complex__(self):
                rudisha cx_arg
        kundi FloatAndComplexOS:
            eleza __float__(self):
                rudisha flt_arg
            eleza __complex__(self):
                rudisha cx_arg
        kundi JustFloat(object):
            eleza __float__(self):
                rudisha flt_arg
        kundi JustFloatOS:
            eleza __float__(self):
                rudisha flt_arg

        kila f kwenye self.test_functions:
            # usual usage
            self.assertEqual(f(MyComplex(cx_arg)), f(cx_arg))
            self.assertEqual(f(MyComplexOS(cx_arg)), f(cx_arg))
            # other combinations of __float__ na __complex__
            self.assertEqual(f(FloatAndComplex()), f(cx_arg))
            self.assertEqual(f(FloatAndComplexOS()), f(cx_arg))
            self.assertEqual(f(JustFloat()), f(flt_arg))
            self.assertEqual(f(JustFloatOS()), f(flt_arg))
            self.assertEqual(f(Index()), f(int(Index())))
            # TypeError should be raised kila classes sio providing
            # either __complex__ ama __float__, even ikiwa they provide
            # __int__ ama __index__.  An old-style class
            # currently raises AttributeError instead of a TypeError;
            # this could be considered a bug.
            self.assertRaises(TypeError, f, NeitherComplexNorFloat())
            self.assertRaises(TypeError, f, MyInt())
            self.assertRaises(Exception, f, NeitherComplexNorFloatOS())
            # non-complex rudisha value kutoka __complex__ -> TypeError
            kila bad_complex kwenye non_complexes:
                self.assertRaises(TypeError, f, MyComplex(bad_complex))
                self.assertRaises(TypeError, f, MyComplexOS(bad_complex))
            # exceptions kwenye __complex__ should be propagated correctly
            self.assertRaises(SomeException, f, MyComplexException())
            self.assertRaises(SomeException, f, MyComplexExceptionOS())

    eleza test_input_type(self):
        # ints should be acceptable inputs to all cmath
        # functions, by virtue of providing a __float__ method
        kila f kwenye self.test_functions:
            kila arg kwenye [2, 2.]:
                self.assertEqual(f(arg), f(arg.__float__()))

        # but strings should give a TypeError
        kila f kwenye self.test_functions:
            kila arg kwenye ["a", "long_string", "0", "1j", ""]:
                self.assertRaises(TypeError, f, arg)

    eleza test_cmath_matches_math(self):
        # check that corresponding cmath na math functions are equal
        # kila floats kwenye the appropriate range

        # test_values kwenye (0, 1)
        test_values = [0.01, 0.1, 0.2, 0.5, 0.9, 0.99]

        # test_values kila functions defined on [-1., 1.]
        unit_interval = test_values + [-x kila x kwenye test_values] + \
            [0., 1., -1.]

        # test_values kila log, log10, sqrt
        positive = test_values + [1.] + [1./x kila x kwenye test_values]
        nonnegative = [0.] + positive

        # test_values kila functions defined on the whole real line
        real_line = [0.] + positive + [-x kila x kwenye positive]

        test_functions = {
            'acos' : unit_interval,
            'asin' : unit_interval,
            'atan' : real_line,
            'cos' : real_line,
            'cosh' : real_line,
            'exp' : real_line,
            'log' : positive,
            'log10' : positive,
            'sin' : real_line,
            'sinh' : real_line,
            'sqrt' : nonnegative,
            'tan' : real_line,
            'tanh' : real_line}

        kila fn, values kwenye test_functions.items():
            float_fn = getattr(math, fn)
            complex_fn = getattr(cmath, fn)
            kila v kwenye values:
                z = complex_fn(v)
                self.rAssertAlmostEqual(float_fn(v), z.real)
                self.assertEqual(0., z.imag)

        # test two-argument version of log ukijumuisha various bases
        kila base kwenye [0.5, 2., 10.]:
            kila v kwenye positive:
                z = cmath.log(v, base)
                self.rAssertAlmostEqual(math.log(v, base), z.real)
                self.assertEqual(0., z.imag)

    @requires_IEEE_754
    eleza test_specific_values(self):
        # Some tests need to be skipped on ancient OS X versions.
        # See issue #27953.
        SKIP_ON_TIGER = {'tan0064'}

        osx_version = Tupu
        ikiwa sys.platform == 'darwin':
            version_txt = platform.mac_ver()[0]
            jaribu:
                osx_version = tuple(map(int, version_txt.split('.')))
            except ValueError:
                pass

        eleza rect_complex(z):
            """Wrapped version of rect that accepts a complex number instead of
            two float arguments."""
            rudisha cmath.rect(z.real, z.imag)

        eleza polar_complex(z):
            """Wrapped version of polar that returns a complex number instead of
            two floats."""
            rudisha complex(*polar(z))

        kila id, fn, ar, ai, er, ei, flags kwenye parse_testfile(test_file):
            arg = complex(ar, ai)
            expected = complex(er, ei)

            # Skip certain tests on OS X 10.4.
            ikiwa osx_version ni sio Tupu na osx_version < (10, 5):
                ikiwa id kwenye SKIP_ON_TIGER:
                    endelea

            ikiwa fn == 'rect':
                function = rect_complex
            elikiwa fn == 'polar':
                function = polar_complex
            isipokua:
                function = getattr(cmath, fn)
            ikiwa 'divide-by-zero' kwenye flags ama 'invalid' kwenye flags:
                jaribu:
                    actual = function(arg)
                except ValueError:
                    endelea
                isipokua:
                    self.fail('ValueError sio raised kwenye test '
                          '{}: {}(complex({!r}, {!r}))'.format(id, fn, ar, ai))

            ikiwa 'overflow' kwenye flags:
                jaribu:
                    actual = function(arg)
                except OverflowError:
                    endelea
                isipokua:
                    self.fail('OverflowError sio raised kwenye test '
                          '{}: {}(complex({!r}, {!r}))'.format(id, fn, ar, ai))

            actual = function(arg)

            ikiwa 'ignore-real-sign' kwenye flags:
                actual = complex(abs(actual.real), actual.imag)
                expected = complex(abs(expected.real), expected.imag)
            ikiwa 'ignore-imag-sign' kwenye flags:
                actual = complex(actual.real, abs(actual.imag))
                expected = complex(expected.real, abs(expected.imag))

            # kila the real part of the log function, we allow an
            # absolute error of up to 2e-15.
            ikiwa fn kwenye ('log', 'log10'):
                real_abs_err = 2e-15
            isipokua:
                real_abs_err = 5e-323

            error_message = (
                '{}: {}(complex({!r}, {!r}))\n'
                'Expected: complex({!r}, {!r})\n'
                'Received: complex({!r}, {!r})\n'
                'Received value insufficiently close to expected value.'
                ).format(id, fn, ar, ai,
                     expected.real, expected.imag,
                     actual.real, actual.imag)
            self.rAssertAlmostEqual(expected.real, actual.real,
                                        abs_err=real_abs_err,
                                        msg=error_message)
            self.rAssertAlmostEqual(expected.imag, actual.imag,
                                        msg=error_message)

    eleza check_polar(self, func):
        eleza check(arg, expected):
            got = func(arg)
            kila e, g kwenye zip(expected, got):
                self.rAssertAlmostEqual(e, g)
        check(0, (0., 0.))
        check(1, (1., 0.))
        check(-1, (1., pi))
        check(1j, (1., pi / 2))
        check(-3j, (3., -pi / 2))
        inf = float('inf')
        check(complex(inf, 0), (inf, 0.))
        check(complex(-inf, 0), (inf, pi))
        check(complex(3, inf), (inf, pi / 2))
        check(complex(5, -inf), (inf, -pi / 2))
        check(complex(inf, inf), (inf, pi / 4))
        check(complex(inf, -inf), (inf, -pi / 4))
        check(complex(-inf, inf), (inf, 3 * pi / 4))
        check(complex(-inf, -inf), (inf, -3 * pi / 4))
        nan = float('nan')
        check(complex(nan, 0), (nan, nan))
        check(complex(0, nan), (nan, nan))
        check(complex(nan, nan), (nan, nan))
        check(complex(inf, nan), (inf, nan))
        check(complex(-inf, nan), (inf, nan))
        check(complex(nan, inf), (inf, nan))
        check(complex(nan, -inf), (inf, nan))

    eleza test_polar(self):
        self.check_polar(polar)

    @cpython_only
    eleza test_polar_errno(self):
        # Issue #24489: check a previously set C errno doesn't disturb polar()
        kutoka _testcapi agiza set_errno
        eleza polar_with_errno_set(z):
            set_errno(11)
            jaribu:
                rudisha polar(z)
            mwishowe:
                set_errno(0)
        self.check_polar(polar_with_errno_set)

    eleza test_phase(self):
        self.assertAlmostEqual(phase(0), 0.)
        self.assertAlmostEqual(phase(1.), 0.)
        self.assertAlmostEqual(phase(-1.), pi)
        self.assertAlmostEqual(phase(-1.+1E-300j), pi)
        self.assertAlmostEqual(phase(-1.-1E-300j), -pi)
        self.assertAlmostEqual(phase(1j), pi/2)
        self.assertAlmostEqual(phase(-1j), -pi/2)

        # zeros
        self.assertEqual(phase(complex(0.0, 0.0)), 0.0)
        self.assertEqual(phase(complex(0.0, -0.0)), -0.0)
        self.assertEqual(phase(complex(-0.0, 0.0)), pi)
        self.assertEqual(phase(complex(-0.0, -0.0)), -pi)

        # infinities
        self.assertAlmostEqual(phase(complex(-INF, -0.0)), -pi)
        self.assertAlmostEqual(phase(complex(-INF, -2.3)), -pi)
        self.assertAlmostEqual(phase(complex(-INF, -INF)), -0.75*pi)
        self.assertAlmostEqual(phase(complex(-2.3, -INF)), -pi/2)
        self.assertAlmostEqual(phase(complex(-0.0, -INF)), -pi/2)
        self.assertAlmostEqual(phase(complex(0.0, -INF)), -pi/2)
        self.assertAlmostEqual(phase(complex(2.3, -INF)), -pi/2)
        self.assertAlmostEqual(phase(complex(INF, -INF)), -pi/4)
        self.assertEqual(phase(complex(INF, -2.3)), -0.0)
        self.assertEqual(phase(complex(INF, -0.0)), -0.0)
        self.assertEqual(phase(complex(INF, 0.0)), 0.0)
        self.assertEqual(phase(complex(INF, 2.3)), 0.0)
        self.assertAlmostEqual(phase(complex(INF, INF)), pi/4)
        self.assertAlmostEqual(phase(complex(2.3, INF)), pi/2)
        self.assertAlmostEqual(phase(complex(0.0, INF)), pi/2)
        self.assertAlmostEqual(phase(complex(-0.0, INF)), pi/2)
        self.assertAlmostEqual(phase(complex(-2.3, INF)), pi/2)
        self.assertAlmostEqual(phase(complex(-INF, INF)), 0.75*pi)
        self.assertAlmostEqual(phase(complex(-INF, 2.3)), pi)
        self.assertAlmostEqual(phase(complex(-INF, 0.0)), pi)

        # real ama imaginary part NaN
        kila z kwenye complex_nans:
            self.assertKweli(math.isnan(phase(z)))

    eleza test_abs(self):
        # zeros
        kila z kwenye complex_zeros:
            self.assertEqual(abs(z), 0.0)

        # infinities
        kila z kwenye complex_infinities:
            self.assertEqual(abs(z), INF)

        # real ama imaginary part NaN
        self.assertEqual(abs(complex(NAN, -INF)), INF)
        self.assertKweli(math.isnan(abs(complex(NAN, -2.3))))
        self.assertKweli(math.isnan(abs(complex(NAN, -0.0))))
        self.assertKweli(math.isnan(abs(complex(NAN, 0.0))))
        self.assertKweli(math.isnan(abs(complex(NAN, 2.3))))
        self.assertEqual(abs(complex(NAN, INF)), INF)
        self.assertEqual(abs(complex(-INF, NAN)), INF)
        self.assertKweli(math.isnan(abs(complex(-2.3, NAN))))
        self.assertKweli(math.isnan(abs(complex(-0.0, NAN))))
        self.assertKweli(math.isnan(abs(complex(0.0, NAN))))
        self.assertKweli(math.isnan(abs(complex(2.3, NAN))))
        self.assertEqual(abs(complex(INF, NAN)), INF)
        self.assertKweli(math.isnan(abs(complex(NAN, NAN))))


    @requires_IEEE_754
    eleza test_abs_overflows(self):
        # result overflows
        self.assertRaises(OverflowError, abs, complex(1.4e308, 1.4e308))

    eleza assertCEqual(self, a, b):
        eps = 1E-7
        ikiwa abs(a.real - b[0]) > eps ama abs(a.imag - b[1]) > eps:
            self.fail((a ,b))

    eleza test_rect(self):
        self.assertCEqual(rect(0, 0), (0, 0))
        self.assertCEqual(rect(1, 0), (1., 0))
        self.assertCEqual(rect(1, -pi), (-1., 0))
        self.assertCEqual(rect(1, pi/2), (0, 1.))
        self.assertCEqual(rect(1, -pi/2), (0, -1.))

    eleza test_isfinite(self):
        real_vals = [float('-inf'), -2.3, -0.0,
                     0.0, 2.3, float('inf'), float('nan')]
        kila x kwenye real_vals:
            kila y kwenye real_vals:
                z = complex(x, y)
                self.assertEqual(cmath.isfinite(z),
                                  math.isfinite(x) na math.isfinite(y))

    eleza test_isnan(self):
        self.assertUongo(cmath.isnan(1))
        self.assertUongo(cmath.isnan(1j))
        self.assertUongo(cmath.isnan(INF))
        self.assertKweli(cmath.isnan(NAN))
        self.assertKweli(cmath.isnan(complex(NAN, 0)))
        self.assertKweli(cmath.isnan(complex(0, NAN)))
        self.assertKweli(cmath.isnan(complex(NAN, NAN)))
        self.assertKweli(cmath.isnan(complex(NAN, INF)))
        self.assertKweli(cmath.isnan(complex(INF, NAN)))

    eleza test_isinf(self):
        self.assertUongo(cmath.isinf(1))
        self.assertUongo(cmath.isinf(1j))
        self.assertUongo(cmath.isinf(NAN))
        self.assertKweli(cmath.isinf(INF))
        self.assertKweli(cmath.isinf(complex(INF, 0)))
        self.assertKweli(cmath.isinf(complex(0, INF)))
        self.assertKweli(cmath.isinf(complex(INF, INF)))
        self.assertKweli(cmath.isinf(complex(NAN, INF)))
        self.assertKweli(cmath.isinf(complex(INF, NAN)))

    @requires_IEEE_754
    eleza testTanhSign(self):
        kila z kwenye complex_zeros:
            self.assertComplexIdentical(cmath.tanh(z), z)

    # The algorithm used kila atan na atanh makes use of the system
    # log1p function; If that system function doesn't respect the sign
    # of zero, then atan na atanh will also have difficulties with
    # the sign of complex zeros.
    @requires_IEEE_754
    eleza testAtanSign(self):
        kila z kwenye complex_zeros:
            self.assertComplexIdentical(cmath.atan(z), z)

    @requires_IEEE_754
    eleza testAtanhSign(self):
        kila z kwenye complex_zeros:
            self.assertComplexIdentical(cmath.atanh(z), z)


kundi IsCloseTests(test_math.IsCloseTests):
    isclose = cmath.isclose

    eleza test_reject_complex_tolerances(self):
        ukijumuisha self.assertRaises(TypeError):
            self.isclose(1j, 1j, rel_tol=1j)

        ukijumuisha self.assertRaises(TypeError):
            self.isclose(1j, 1j, abs_tol=1j)

        ukijumuisha self.assertRaises(TypeError):
            self.isclose(1j, 1j, rel_tol=1j, abs_tol=1j)

    eleza test_complex_values(self):
        # test complex values that are close to within 12 decimal places
        complex_examples = [(1.0+1.0j, 1.000000000001+1.0j),
                            (1.0+1.0j, 1.0+1.000000000001j),
                            (-1.0+1.0j, -1.000000000001+1.0j),
                            (1.0-1.0j, 1.0-0.999999999999j),
                            ]

        self.assertAllClose(complex_examples, rel_tol=1e-12)
        self.assertAllNotClose(complex_examples, rel_tol=1e-13)

    eleza test_complex_near_zero(self):
        # test values near zero that are near to within three decimal places
        near_zero_examples = [(0.001j, 0),
                              (0.001, 0),
                              (0.001+0.001j, 0),
                              (-0.001+0.001j, 0),
                              (0.001-0.001j, 0),
                              (-0.001-0.001j, 0),
                              ]

        self.assertAllClose(near_zero_examples, abs_tol=1.5e-03)
        self.assertAllNotClose(near_zero_examples, abs_tol=0.5e-03)

        self.assertIsClose(0.001-0.001j, 0.001+0.001j, abs_tol=2e-03)
        self.assertIsNotClose(0.001-0.001j, 0.001+0.001j, abs_tol=1e-03)


ikiwa __name__ == "__main__":
    unittest.main()
