# Copyright (c) 2004 Python Software Foundation.
# All rights reserved.

# Written by Eric Price <eprice at tjhsst.edu>
#    na Facundo Batista <facundo at taniquetil.com.ar>
#    na Raymond Hettinger <python at rcn.com>
#    na Aahz (aahz at pobox.com)
#    na Tim Peters

"""
These are the test cases kila the Decimal module.

There are two groups of tests, Arithmetic na Behaviour. The former test
the Decimal arithmetic using the tests provided by Mike Cowlishaw. The latter
test the pythonic behaviour according to PEP 327.

Cowlishaw's tests can be downloaded from:

   http://speleotrove.com/decimal/dectest.zip

This test module can be called kutoka command line ukijumuisha one parameter (Arithmetic
or Behaviour) to test each part, ama without parameter to test both parts. If
you're working through IDLE, you can agiza this test module na call test_main()
ukijumuisha the corresponding argument.
"""

agiza math
agiza os, sys
agiza operator
agiza warnings
agiza pickle, copy
agiza unittest
agiza numbers
agiza locale
kutoka test.support agiza (run_unittest, run_doctest, is_resource_enabled,
                          requires_IEEE_754, requires_docstrings)
kutoka test.support agiza (import_fresh_module, TestFailed,
                          run_with_locale, cpython_only)
agiza random
agiza inspect
agiza threading


C = import_fresh_module('decimal', fresh=['_decimal'])
P = import_fresh_module('decimal', blocked=['_decimal'])
orig_sys_decimal = sys.modules['decimal']

# fractions module must agiza the correct decimal module.
cfractions = import_fresh_module('fractions', fresh=['fractions'])
sys.modules['decimal'] = P
pfractions = import_fresh_module('fractions', fresh=['fractions'])
sys.modules['decimal'] = C
fractions = {C:cfractions, P:pfractions}
sys.modules['decimal'] = orig_sys_decimal


# Useful Test Constant
Signals = {
  C: tuple(C.getcontext().flags.keys()) ikiwa C isipokua Tupu,
  P: tuple(P.getcontext().flags.keys())
}
# Signals ordered ukijumuisha respect to precedence: when an operation
# produces multiple signals, signals occurring later kwenye the list
# should be handled before those occurring earlier kwenye the list.
OrderedSignals = {
  C: [C.Clamped, C.Rounded, C.Inexact, C.Subnormal, C.Underflow,
      C.Overflow, C.DivisionByZero, C.InvalidOperation,
      C.FloatOperation] ikiwa C isipokua Tupu,
  P: [P.Clamped, P.Rounded, P.Inexact, P.Subnormal, P.Underflow,
      P.Overflow, P.DivisionByZero, P.InvalidOperation,
      P.FloatOperation]
}
eleza assert_signals(cls, context, attr, expected):
    d = getattr(context, attr)
    cls.assertKweli(all(d[s] ikiwa s kwenye expected isipokua sio d[s] kila s kwenye d))

ROUND_UP = P.ROUND_UP
ROUND_DOWN = P.ROUND_DOWN
ROUND_CEILING = P.ROUND_CEILING
ROUND_FLOOR = P.ROUND_FLOOR
ROUND_HALF_UP = P.ROUND_HALF_UP
ROUND_HALF_DOWN = P.ROUND_HALF_DOWN
ROUND_HALF_EVEN = P.ROUND_HALF_EVEN
ROUND_05UP = P.ROUND_05UP

RoundingModes = [
  ROUND_UP, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR,
  ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_HALF_EVEN,
  ROUND_05UP
]

# Tests are built around these assumed context defaults.
# test_main() restores the original context.
ORIGINAL_CONTEXT = {
  C: C.getcontext().copy() ikiwa C isipokua Tupu,
  P: P.getcontext().copy()
}
eleza init(m):
    ikiwa sio m: return
    DefaultTestContext = m.Context(
       prec=9, rounding=ROUND_HALF_EVEN, traps=dict.fromkeys(Signals[m], 0)
    )
    m.setcontext(DefaultTestContext)

TESTDATADIR = 'decimaltestdata'
ikiwa __name__ == '__main__':
    file = sys.argv[0]
isipokua:
    file = __file__
testdir = os.path.dirname(file) ama os.curdir
directory = testdir + os.sep + TESTDATADIR + os.sep

skip_expected = sio os.path.isdir(directory)

# Make sure it actually raises errors when sio expected na caught kwenye flags
# Slower, since it runs some things several times.
EXTENDEDERRORTEST = Uongo

# Test extra functionality kwenye the C version (-DEXTRA_FUNCTIONALITY).
EXTRA_FUNCTIONALITY = Kweli ikiwa hasattr(C, 'DecClamped') isipokua Uongo
requires_extra_functionality = unittest.skipUnless(
  EXTRA_FUNCTIONALITY, "test requires build ukijumuisha -DEXTRA_FUNCTIONALITY")
skip_if_extra_functionality = unittest.skipIf(
  EXTRA_FUNCTIONALITY, "test requires regular build")


kundi IBMTestCases(unittest.TestCase):
    """Class which tests the Decimal kundi against the IBM test cases."""

    eleza setUp(self):
        self.context = self.decimal.Context()
        self.readcontext = self.decimal.Context()
        self.ignore_list = ['#']

        # List of individual .decTest test ids that correspond to tests that
        # we're skipping kila one reason ama another.
        self.skipped_test_ids = set([
            # Skip implementation-specific scaleb tests.
            'scbx164',
            'scbx165',

            # For some operations (currently exp, ln, log10, power), the decNumber
            # reference implementation imposes additional restrictions on the context
            # na operands.  These restrictions are sio part of the specification;
            # however, the effect of these restrictions does show up kwenye some of the
            # testcases.  We skip testcases that violate these restrictions, since
            # Decimal behaves differently kutoka decNumber kila these testcases so these
            # testcases would otherwise fail.
            'expx901',
            'expx902',
            'expx903',
            'expx905',
            'lnx901',
            'lnx902',
            'lnx903',
            'lnx905',
            'logx901',
            'logx902',
            'logx903',
            'logx905',
            'powx1183',
            'powx1184',
            'powx4001',
            'powx4002',
            'powx4003',
            'powx4005',
            'powx4008',
            'powx4010',
            'powx4012',
            'powx4014',
            ])

        ikiwa self.decimal == C:
            # status has additional Subnormal, Underflow
            self.skipped_test_ids.add('pwsx803')
            self.skipped_test_ids.add('pwsx805')
            # Correct rounding (skipped kila decNumber, too)
            self.skipped_test_ids.add('powx4302')
            self.skipped_test_ids.add('powx4303')
            self.skipped_test_ids.add('powx4342')
            self.skipped_test_ids.add('powx4343')
            # http://bugs.python.org/issue7049
            self.skipped_test_ids.add('pwmx325')
            self.skipped_test_ids.add('pwmx326')

        # Map test directives to setter functions.
        self.ChangeDict = {'precision' : self.change_precision,
                           'rounding' : self.change_rounding_method,
                           'maxexponent' : self.change_max_exponent,
                           'minexponent' : self.change_min_exponent,
                           'clamp' : self.change_clamp}

        # Name adapter to be able to change the Decimal na Context
        # interface without changing the test files kutoka Cowlishaw.
        self.NameAdapter = {'and':'logical_and',
                            'apply':'_apply',
                            'class':'number_class',
                            'comparesig':'compare_signal',
                            'comparetotal':'compare_total',
                            'comparetotmag':'compare_total_mag',
                            'copy':'copy_decimal',
                            'copyabs':'copy_abs',
                            'copynegate':'copy_negate',
                            'copysign':'copy_sign',
                            'divideint':'divide_int',
                            'invert':'logical_invert',
                            'iscanonical':'is_canonical',
                            'isfinite':'is_finite',
                            'isinfinite':'is_infinite',
                            'isnan':'is_nan',
                            'isnormal':'is_normal',
                            'isqnan':'is_qnan',
                            'issigned':'is_signed',
                            'issnan':'is_snan',
                            'issubnormal':'is_subnormal',
                            'iszero':'is_zero',
                            'maxmag':'max_mag',
                            'minmag':'min_mag',
                            'nextminus':'next_minus',
                            'nextplus':'next_plus',
                            'nexttoward':'next_toward',
                            'or':'logical_or',
                            'reduce':'normalize',
                            'remaindernear':'remainder_near',
                            'samequantum':'same_quantum',
                            'squareroot':'sqrt',
                            'toeng':'to_eng_string',
                            'tointegral':'to_integral_value',
                            'tointegralx':'to_integral_exact',
                            'tosci':'to_sci_string',
                            'xor':'logical_xor'}

        # Map test-case names to roundings.
        self.RoundingDict = {'ceiling' : ROUND_CEILING,
                             'down' : ROUND_DOWN,
                             'floor' : ROUND_FLOOR,
                             'half_down' : ROUND_HALF_DOWN,
                             'half_even' : ROUND_HALF_EVEN,
                             'half_up' : ROUND_HALF_UP,
                             'up' : ROUND_UP,
                             '05up' : ROUND_05UP}

        # Map the test cases' error names to the actual errors.
        self.ErrorNames = {'clamped' : self.decimal.Clamped,
                           'conversion_syntax' : self.decimal.InvalidOperation,
                           'division_by_zero' : self.decimal.DivisionByZero,
                           'division_impossible' : self.decimal.InvalidOperation,
                           'division_undefined' : self.decimal.InvalidOperation,
                           'inexact' : self.decimal.Inexact,
                           'invalid_context' : self.decimal.InvalidOperation,
                           'invalid_operation' : self.decimal.InvalidOperation,
                           'overflow' : self.decimal.Overflow,
                           'rounded' : self.decimal.Rounded,
                           'subnormal' : self.decimal.Subnormal,
                           'underflow' : self.decimal.Underflow}

        # The following functions rudisha Kweli/Uongo rather than a
        # Decimal instance.
        self.LogicalFunctions = ('is_canonical',
                                 'is_finite',
                                 'is_infinite',
                                 'is_nan',
                                 'is_normal',
                                 'is_qnan',
                                 'is_signed',
                                 'is_snan',
                                 'is_subnormal',
                                 'is_zero',
                                 'same_quantum')

    eleza read_unlimited(self, v, context):
        """Work around the limitations of the 32-bit _decimal version. The
           guaranteed maximum values kila prec, Emax etc. are 425000000,
           but higher values usually work, tatizo kila rare corner cases.
           In particular, all of the IBM tests pita ukijumuisha maximum values
           of 1070000000."""
        ikiwa self.decimal == C na self.decimal.MAX_EMAX == 425000000:
            self.readcontext._unsafe_setprec(1070000000)
            self.readcontext._unsafe_setemax(1070000000)
            self.readcontext._unsafe_setemin(-1070000000)
            rudisha self.readcontext.create_decimal(v)
        isipokua:
            rudisha self.decimal.Decimal(v, context)

    eleza eval_file(self, file):
        global skip_expected
        ikiwa skip_expected:
            ashiria unittest.SkipTest
        ukijumuisha open(file) kama f:
            kila line kwenye f:
                line = line.replace('\r\n', '').replace('\n', '')
                #print line
                jaribu:
                    t = self.eval_line(line)
                tatizo self.decimal.DecimalException kama exception:
                    #Exception raised where there shouldn't have been one.
                    self.fail('Exception "'+exception.__class__.__name__ + '" raised on line '+line)


    eleza eval_line(self, s):
        ikiwa s.find(' -> ') >= 0 na s[:2] != '--' na sio s.startswith('  --'):
            s = (s.split('->')[0] + '->' +
                 s.split('->')[1].split('--')[0]).strip()
        isipokua:
            s = s.split('--')[0].strip()

        kila ignore kwenye self.ignore_list:
            ikiwa s.find(ignore) >= 0:
                #print s.split()[0], 'NotImplemented--', ignore
                return
        ikiwa sio s:
            return
        lasivyo ':' kwenye s:
            rudisha self.eval_directive(s)
        isipokua:
            rudisha self.eval_equation(s)

    eleza eval_directive(self, s):
        funct, value = (x.strip().lower() kila x kwenye s.split(':'))
        ikiwa funct == 'rounding':
            value = self.RoundingDict[value]
        isipokua:
            jaribu:
                value = int(value)
            tatizo ValueError:
                pita

        funct = self.ChangeDict.get(funct, (lambda *args: Tupu))
        funct(value)

    eleza eval_equation(self, s):

        ikiwa sio TEST_ALL na random.random() < 0.90:
            return

        self.context.clear_flags()

        jaribu:
            Sides = s.split('->')
            L = Sides[0].strip().split()
            id = L[0]
            ikiwa DEBUG:
                andika("Test ", id, end=" ")
            funct = L[1].lower()
            valstemp = L[2:]
            L = Sides[1].strip().split()
            ans = L[0]
            exceptions = L[1:]
        tatizo (TypeError, AttributeError, IndexError):
            ashiria self.decimal.InvalidOperation
        eleza FixQuotes(val):
            val = val.replace("''", 'SingleQuote').replace('""', 'DoubleQuote')
            val = val.replace("'", '').replace('"', '')
            val = val.replace('SingleQuote', "'").replace('DoubleQuote', '"')
            rudisha val

        ikiwa id kwenye self.skipped_test_ids:
            return

        fname = self.NameAdapter.get(funct, funct)
        ikiwa fname == 'rescale':
            return
        funct = getattr(self.context, fname)
        vals = []
        conglomerate = ''
        quote = 0
        theirexceptions = [self.ErrorNames[x.lower()] kila x kwenye exceptions]

        kila exception kwenye Signals[self.decimal]:
            self.context.traps[exception] = 1 #Catch these bugs...
        kila exception kwenye theirexceptions:
            self.context.traps[exception] = 0
        kila i, val kwenye enumerate(valstemp):
            ikiwa val.count("'") % 2 == 1:
                quote = 1 - quote
            ikiwa quote:
                conglomerate = conglomerate + ' ' + val
                endelea
            isipokua:
                val = conglomerate + val
                conglomerate = ''
            v = FixQuotes(val)
            ikiwa fname kwenye ('to_sci_string', 'to_eng_string'):
                ikiwa EXTENDEDERRORTEST:
                    kila error kwenye theirexceptions:
                        self.context.traps[error] = 1
                        jaribu:
                            funct(self.context.create_decimal(v))
                        tatizo error:
                            pita
                        tatizo Signals[self.decimal] kama e:
                            self.fail("Raised %s kwenye %s when %s disabled" % \
                                      (e, s, error))
                        isipokua:
                            self.fail("Did sio ashiria %s kwenye %s" % (error, s))
                        self.context.traps[error] = 0
                v = self.context.create_decimal(v)
            isipokua:
                v = self.read_unlimited(v, self.context)
            vals.append(v)

        ans = FixQuotes(ans)

        ikiwa EXTENDEDERRORTEST na fname haiko kwenye ('to_sci_string', 'to_eng_string'):
            kila error kwenye theirexceptions:
                self.context.traps[error] = 1
                jaribu:
                    funct(*vals)
                tatizo error:
                    pita
                tatizo Signals[self.decimal] kama e:
                    self.fail("Raised %s kwenye %s when %s disabled" % \
                              (e, s, error))
                isipokua:
                    self.fail("Did sio ashiria %s kwenye %s" % (error, s))
                self.context.traps[error] = 0

            # kama above, but add traps cumulatively, to check precedence
            ordered_errors = [e kila e kwenye OrderedSignals[self.decimal] ikiwa e kwenye theirexceptions]
            kila error kwenye ordered_errors:
                self.context.traps[error] = 1
                jaribu:
                    funct(*vals)
                tatizo error:
                    pita
                tatizo Signals[self.decimal] kama e:
                    self.fail("Raised %s kwenye %s; expected %s" %
                              (type(e), s, error))
                isipokua:
                    self.fail("Did sio ashiria %s kwenye %s" % (error, s))
            # reset traps
            kila error kwenye ordered_errors:
                self.context.traps[error] = 0


        ikiwa DEBUG:
            andika("--", self.context)
        jaribu:
            result = str(funct(*vals))
            ikiwa fname kwenye self.LogicalFunctions:
                result = str(int(eval(result))) # 'Kweli', 'Uongo' -> '1', '0'
        tatizo Signals[self.decimal] kama error:
            self.fail("Raised %s kwenye %s" % (error, s))
        tatizo: #Catch any error long enough to state the test case.
            andika("ERROR:", s)
            raise

        myexceptions = self.getexceptions()

        myexceptions.sort(key=repr)
        theirexceptions.sort(key=repr)

        self.assertEqual(result, ans,
                         'Incorrect answer kila ' + s + ' -- got ' + result)

        self.assertEqual(myexceptions, theirexceptions,
              'Incorrect flags set kwenye ' + s + ' -- got ' + str(myexceptions))

    eleza getexceptions(self):
        rudisha [e kila e kwenye Signals[self.decimal] ikiwa self.context.flags[e]]

    eleza change_precision(self, prec):
        ikiwa self.decimal == C na self.decimal.MAX_PREC == 425000000:
            self.context._unsafe_setprec(prec)
        isipokua:
            self.context.prec = prec
    eleza change_rounding_method(self, rounding):
        self.context.rounding = rounding
    eleza change_min_exponent(self, exp):
        ikiwa self.decimal == C na self.decimal.MAX_PREC == 425000000:
            self.context._unsafe_setemin(exp)
        isipokua:
            self.context.Emin = exp
    eleza change_max_exponent(self, exp):
        ikiwa self.decimal == C na self.decimal.MAX_PREC == 425000000:
            self.context._unsafe_setemax(exp)
        isipokua:
            self.context.Emax = exp
    eleza change_clamp(self, clamp):
        self.context.clamp = clamp

kundi CIBMTestCases(IBMTestCases):
    decimal = C
kundi PyIBMTestCases(IBMTestCases):
    decimal = P

# The following classes test the behaviour of Decimal according to PEP 327

kundi ExplicitConstructionTest(unittest.TestCase):
    '''Unit tests kila Explicit Construction cases of Decimal.'''

    eleza test_explicit_empty(self):
        Decimal = self.decimal.Decimal
        self.assertEqual(Decimal(), Decimal("0"))

    eleza test_explicit_from_Tupu(self):
        Decimal = self.decimal.Decimal
        self.assertRaises(TypeError, Decimal, Tupu)

    eleza test_explicit_from_int(self):
        Decimal = self.decimal.Decimal

        #positive
        d = Decimal(45)
        self.assertEqual(str(d), '45')

        #very large positive
        d = Decimal(500000123)
        self.assertEqual(str(d), '500000123')

        #negative
        d = Decimal(-45)
        self.assertEqual(str(d), '-45')

        #zero
        d = Decimal(0)
        self.assertEqual(str(d), '0')

        # single word longs
        kila n kwenye range(0, 32):
            kila sign kwenye (-1, 1):
                kila x kwenye range(-5, 5):
                    i = sign * (2**n + x)
                    d = Decimal(i)
                    self.assertEqual(str(d), str(i))

    eleza test_explicit_from_string(self):
        Decimal = self.decimal.Decimal
        InvalidOperation = self.decimal.InvalidOperation
        localcontext = self.decimal.localcontext

        #empty
        self.assertEqual(str(Decimal('')), 'NaN')

        #int
        self.assertEqual(str(Decimal('45')), '45')

        #float
        self.assertEqual(str(Decimal('45.34')), '45.34')

        #engineer notation
        self.assertEqual(str(Decimal('45e2')), '4.5E+3')

        #just sio a number
        self.assertEqual(str(Decimal('ugly')), 'NaN')

        #leading na trailing whitespace permitted
        self.assertEqual(str(Decimal('1.3E4 \n')), '1.3E+4')
        self.assertEqual(str(Decimal('  -7.89')), '-7.89')
        self.assertEqual(str(Decimal("  3.45679  ")), '3.45679')

        # underscores
        self.assertEqual(str(Decimal('1_3.3e4_0')), '1.33E+41')
        self.assertEqual(str(Decimal('1_0_0_0')), '1000')

        # unicode whitespace
        kila lead kwenye ["", ' ', '\u00a0', '\u205f']:
            kila trail kwenye ["", ' ', '\u00a0', '\u205f']:
                self.assertEqual(str(Decimal(lead + '9.311E+28' + trail)),
                                 '9.311E+28')

        ukijumuisha localcontext() kama c:
            c.traps[InvalidOperation] = Kweli
            # Invalid string
            self.assertRaises(InvalidOperation, Decimal, "xyz")
            # Two arguments max
            self.assertRaises(TypeError, Decimal, "1234", "x", "y")

            # space within the numeric part
            self.assertRaises(InvalidOperation, Decimal, "1\u00a02\u00a03")
            self.assertRaises(InvalidOperation, Decimal, "\u00a01\u00a02\u00a0")

            # unicode whitespace
            self.assertRaises(InvalidOperation, Decimal, "\u00a0")
            self.assertRaises(InvalidOperation, Decimal, "\u00a0\u00a0")

            # embedded NUL
            self.assertRaises(InvalidOperation, Decimal, "12\u00003")

            # underscores don't prevent errors
            self.assertRaises(InvalidOperation, Decimal, "1_2_\u00003")

    @cpython_only
    eleza test_from_legacy_strings(self):
        agiza _testcapi
        Decimal = self.decimal.Decimal
        context = self.decimal.Context()

        s = _testcapi.unicode_legacy_string('9.999999')
        self.assertEqual(str(Decimal(s)), '9.999999')
        self.assertEqual(str(context.create_decimal(s)), '9.999999')

    eleza test_explicit_from_tuples(self):
        Decimal = self.decimal.Decimal

        #zero
        d = Decimal( (0, (0,), 0) )
        self.assertEqual(str(d), '0')

        #int
        d = Decimal( (1, (4, 5), 0) )
        self.assertEqual(str(d), '-45')

        #float
        d = Decimal( (0, (4, 5, 3, 4), -2) )
        self.assertEqual(str(d), '45.34')

        #weird
        d = Decimal( (1, (4, 3, 4, 9, 1, 3, 5, 3, 4), -25) )
        self.assertEqual(str(d), '-4.34913534E-17')

        #inf
        d = Decimal( (0, (), "F") )
        self.assertEqual(str(d), 'Infinity')

        #wrong number of items
        self.assertRaises(ValueError, Decimal, (1, (4, 3, 4, 9, 1)) )

        #bad sign
        self.assertRaises(ValueError, Decimal, (8, (4, 3, 4, 9, 1), 2) )
        self.assertRaises(ValueError, Decimal, (0., (4, 3, 4, 9, 1), 2) )
        self.assertRaises(ValueError, Decimal, (Decimal(1), (4, 3, 4, 9, 1), 2))

        #bad exp
        self.assertRaises(ValueError, Decimal, (1, (4, 3, 4, 9, 1), 'wrong!') )
        self.assertRaises(ValueError, Decimal, (1, (4, 3, 4, 9, 1), 0.) )
        self.assertRaises(ValueError, Decimal, (1, (4, 3, 4, 9, 1), '1') )

        #bad coefficients
        self.assertRaises(ValueError, Decimal, (1, "xyz", 2) )
        self.assertRaises(ValueError, Decimal, (1, (4, 3, 4, Tupu, 1), 2) )
        self.assertRaises(ValueError, Decimal, (1, (4, -3, 4, 9, 1), 2) )
        self.assertRaises(ValueError, Decimal, (1, (4, 10, 4, 9, 1), 2) )
        self.assertRaises(ValueError, Decimal, (1, (4, 3, 4, 'a', 1), 2) )

    eleza test_explicit_from_list(self):
        Decimal = self.decimal.Decimal

        d = Decimal([0, [0], 0])
        self.assertEqual(str(d), '0')

        d = Decimal([1, [4, 3, 4, 9, 1, 3, 5, 3, 4], -25])
        self.assertEqual(str(d), '-4.34913534E-17')

        d = Decimal([1, (4, 3, 4, 9, 1, 3, 5, 3, 4), -25])
        self.assertEqual(str(d), '-4.34913534E-17')

        d = Decimal((1, [4, 3, 4, 9, 1, 3, 5, 3, 4], -25))
        self.assertEqual(str(d), '-4.34913534E-17')

    eleza test_explicit_from_bool(self):
        Decimal = self.decimal.Decimal

        self.assertIs(bool(Decimal(0)), Uongo)
        self.assertIs(bool(Decimal(1)), Kweli)
        self.assertEqual(Decimal(Uongo), Decimal(0))
        self.assertEqual(Decimal(Kweli), Decimal(1))

    eleza test_explicit_from_Decimal(self):
        Decimal = self.decimal.Decimal

        #positive
        d = Decimal(45)
        e = Decimal(d)
        self.assertEqual(str(e), '45')

        #very large positive
        d = Decimal(500000123)
        e = Decimal(d)
        self.assertEqual(str(e), '500000123')

        #negative
        d = Decimal(-45)
        e = Decimal(d)
        self.assertEqual(str(e), '-45')

        #zero
        d = Decimal(0)
        e = Decimal(d)
        self.assertEqual(str(e), '0')

    @requires_IEEE_754
    eleza test_explicit_from_float(self):

        Decimal = self.decimal.Decimal

        r = Decimal(0.1)
        self.assertEqual(type(r), Decimal)
        self.assertEqual(str(r),
                '0.1000000000000000055511151231257827021181583404541015625')
        self.assertKweli(Decimal(float('nan')).is_qnan())
        self.assertKweli(Decimal(float('inf')).is_infinite())
        self.assertKweli(Decimal(float('-inf')).is_infinite())
        self.assertEqual(str(Decimal(float('nan'))),
                         str(Decimal('NaN')))
        self.assertEqual(str(Decimal(float('inf'))),
                         str(Decimal('Infinity')))
        self.assertEqual(str(Decimal(float('-inf'))),
                         str(Decimal('-Infinity')))
        self.assertEqual(str(Decimal(float('-0.0'))),
                         str(Decimal('-0')))
        kila i kwenye range(200):
            x = random.expovariate(0.01) * (random.random() * 2.0 - 1.0)
            self.assertEqual(x, float(Decimal(x))) # roundtrip

    eleza test_explicit_context_create_decimal(self):
        Decimal = self.decimal.Decimal
        InvalidOperation = self.decimal.InvalidOperation
        Rounded = self.decimal.Rounded

        nc = copy.copy(self.decimal.getcontext())
        nc.prec = 3

        # empty
        d = Decimal()
        self.assertEqual(str(d), '0')
        d = nc.create_decimal()
        self.assertEqual(str(d), '0')

        # kutoka Tupu
        self.assertRaises(TypeError, nc.create_decimal, Tupu)

        # kutoka int
        d = nc.create_decimal(456)
        self.assertIsInstance(d, Decimal)
        self.assertEqual(nc.create_decimal(45678),
                         nc.create_decimal('457E+2'))

        # kutoka string
        d = Decimal('456789')
        self.assertEqual(str(d), '456789')
        d = nc.create_decimal('456789')
        self.assertEqual(str(d), '4.57E+5')
        # leading na trailing whitespace should result kwenye a NaN;
        # spaces are already checked kwenye Cowlishaw's test-suite, so
        # here we just check that a trailing newline results kwenye a NaN
        self.assertEqual(str(nc.create_decimal('3.14\n')), 'NaN')

        # kutoka tuples
        d = Decimal( (1, (4, 3, 4, 9, 1, 3, 5, 3, 4), -25) )
        self.assertEqual(str(d), '-4.34913534E-17')
        d = nc.create_decimal( (1, (4, 3, 4, 9, 1, 3, 5, 3, 4), -25) )
        self.assertEqual(str(d), '-4.35E-17')

        # kutoka Decimal
        prevdec = Decimal(500000123)
        d = Decimal(prevdec)
        self.assertEqual(str(d), '500000123')
        d = nc.create_decimal(prevdec)
        self.assertEqual(str(d), '5.00E+8')

        # more integers
        nc.prec = 28
        nc.traps[InvalidOperation] = Kweli

        kila v kwenye [-2**63-1, -2**63, -2**31-1, -2**31, 0,
                   2**31-1, 2**31, 2**63-1, 2**63]:
            d = nc.create_decimal(v)
            self.assertKweli(isinstance(d, Decimal))
            self.assertEqual(int(d), v)

        nc.prec = 3
        nc.traps[Rounded] = Kweli
        self.assertRaises(Rounded, nc.create_decimal, 1234)

        # kutoka string
        nc.prec = 28
        self.assertEqual(str(nc.create_decimal('0E-017')), '0E-17')
        self.assertEqual(str(nc.create_decimal('45')), '45')
        self.assertEqual(str(nc.create_decimal('-Inf')), '-Infinity')
        self.assertEqual(str(nc.create_decimal('NaN123')), 'NaN123')

        # invalid arguments
        self.assertRaises(InvalidOperation, nc.create_decimal, "xyz")
        self.assertRaises(ValueError, nc.create_decimal, (1, "xyz", -25))
        self.assertRaises(TypeError, nc.create_decimal, "1234", "5678")
        # no whitespace na underscore stripping ni done ukijumuisha this method
        self.assertRaises(InvalidOperation, nc.create_decimal, " 1234")
        self.assertRaises(InvalidOperation, nc.create_decimal, "12_34")

        # too many NaN payload digits
        nc.prec = 3
        self.assertRaises(InvalidOperation, nc.create_decimal, 'NaN12345')
        self.assertRaises(InvalidOperation, nc.create_decimal,
                          Decimal('NaN12345'))

        nc.traps[InvalidOperation] = Uongo
        self.assertEqual(str(nc.create_decimal('NaN12345')), 'NaN')
        self.assertKweli(nc.flags[InvalidOperation])

        nc.flags[InvalidOperation] = Uongo
        self.assertEqual(str(nc.create_decimal(Decimal('NaN12345'))), 'NaN')
        self.assertKweli(nc.flags[InvalidOperation])

    eleza test_explicit_context_create_from_float(self):

        Decimal = self.decimal.Decimal

        nc = self.decimal.Context()
        r = nc.create_decimal(0.1)
        self.assertEqual(type(r), Decimal)
        self.assertEqual(str(r), '0.1000000000000000055511151231')
        self.assertKweli(nc.create_decimal(float('nan')).is_qnan())
        self.assertKweli(nc.create_decimal(float('inf')).is_infinite())
        self.assertKweli(nc.create_decimal(float('-inf')).is_infinite())
        self.assertEqual(str(nc.create_decimal(float('nan'))),
                         str(nc.create_decimal('NaN')))
        self.assertEqual(str(nc.create_decimal(float('inf'))),
                         str(nc.create_decimal('Infinity')))
        self.assertEqual(str(nc.create_decimal(float('-inf'))),
                         str(nc.create_decimal('-Infinity')))
        self.assertEqual(str(nc.create_decimal(float('-0.0'))),
                         str(nc.create_decimal('-0')))
        nc.prec = 100
        kila i kwenye range(200):
            x = random.expovariate(0.01) * (random.random() * 2.0 - 1.0)
            self.assertEqual(x, float(nc.create_decimal(x))) # roundtrip

    eleza test_unicode_digits(self):
        Decimal = self.decimal.Decimal

        test_values = {
            '\uff11': '1',
            '\u0660.\u0660\u0663\u0667\u0662e-\u0663' : '0.0000372',
            '-nan\u0c68\u0c6a\u0c66\u0c66' : '-NaN2400',
            }
        kila input, expected kwenye test_values.items():
            self.assertEqual(str(Decimal(input)), expected)

kundi CExplicitConstructionTest(ExplicitConstructionTest):
    decimal = C
kundi PyExplicitConstructionTest(ExplicitConstructionTest):
    decimal = P

kundi ImplicitConstructionTest(unittest.TestCase):
    '''Unit tests kila Implicit Construction cases of Decimal.'''

    eleza test_implicit_from_Tupu(self):
        Decimal = self.decimal.Decimal
        self.assertRaises(TypeError, eval, 'Decimal(5) + Tupu', locals())

    eleza test_implicit_from_int(self):
        Decimal = self.decimal.Decimal

        #normal
        self.assertEqual(str(Decimal(5) + 45), '50')
        #exceeding precision
        self.assertEqual(Decimal(5) + 123456789000, Decimal(123456789000))

    eleza test_implicit_from_string(self):
        Decimal = self.decimal.Decimal
        self.assertRaises(TypeError, eval, 'Decimal(5) + "3"', locals())

    eleza test_implicit_from_float(self):
        Decimal = self.decimal.Decimal
        self.assertRaises(TypeError, eval, 'Decimal(5) + 2.2', locals())

    eleza test_implicit_from_Decimal(self):
        Decimal = self.decimal.Decimal
        self.assertEqual(Decimal(5) + Decimal(45), Decimal(50))

    eleza test_rop(self):
        Decimal = self.decimal.Decimal

        # Allow other classes to be trained to interact ukijumuisha Decimals
        kundi E:
            eleza __divmod__(self, other):
                rudisha 'divmod ' + str(other)
            eleza __rdivmod__(self, other):
                rudisha str(other) + ' rdivmod'
            eleza __lt__(self, other):
                rudisha 'lt ' + str(other)
            eleza __gt__(self, other):
                rudisha 'gt ' + str(other)
            eleza __le__(self, other):
                rudisha 'le ' + str(other)
            eleza __ge__(self, other):
                rudisha 'ge ' + str(other)
            eleza __eq__(self, other):
                rudisha 'eq ' + str(other)
            eleza __ne__(self, other):
                rudisha 'ne ' + str(other)

        self.assertEqual(divmod(E(), Decimal(10)), 'divmod 10')
        self.assertEqual(divmod(Decimal(10), E()), '10 rdivmod')
        self.assertEqual(eval('Decimal(10) < E()'), 'gt 10')
        self.assertEqual(eval('Decimal(10) > E()'), 'lt 10')
        self.assertEqual(eval('Decimal(10) <= E()'), 'ge 10')
        self.assertEqual(eval('Decimal(10) >= E()'), 'le 10')
        self.assertEqual(eval('Decimal(10) == E()'), 'eq 10')
        self.assertEqual(eval('Decimal(10) != E()'), 'ne 10')

        # insert operator methods na then exercise them
        oplist = [
            ('+', '__add__', '__radd__'),
            ('-', '__sub__', '__rsub__'),
            ('*', '__mul__', '__rmul__'),
            ('/', '__truediv__', '__rtruediv__'),
            ('%', '__mod__', '__rmod__'),
            ('//', '__floordiv__', '__rfloordiv__'),
            ('**', '__pow__', '__rpow__')
        ]

        kila sym, lop, rop kwenye oplist:
            setattr(E, lop, lambda self, other: 'str' + lop + str(other))
            setattr(E, rop, lambda self, other: str(other) + rop + 'str')
            self.assertEqual(eval('E()' + sym + 'Decimal(10)'),
                             'str' + lop + '10')
            self.assertEqual(eval('Decimal(10)' + sym + 'E()'),
                             '10' + rop + 'str')

kundi CImplicitConstructionTest(ImplicitConstructionTest):
    decimal = C
kundi PyImplicitConstructionTest(ImplicitConstructionTest):
    decimal = P

kundi FormatTest(unittest.TestCase):
    '''Unit tests kila the format function.'''
    eleza test_formatting(self):
        Decimal = self.decimal.Decimal

        # triples giving a format, a Decimal, na the expected result
        test_values = [
            ('e', '0E-15', '0e-15'),
            ('e', '2.3E-15', '2.3e-15'),
            ('e', '2.30E+2', '2.30e+2'), # preserve significant zeros
            ('e', '2.30000E-15', '2.30000e-15'),
            ('e', '1.23456789123456789e40', '1.23456789123456789e+40'),
            ('e', '1.5', '1.5e+0'),
            ('e', '0.15', '1.5e-1'),
            ('e', '0.015', '1.5e-2'),
            ('e', '0.0000000000015', '1.5e-12'),
            ('e', '15.0', '1.50e+1'),
            ('e', '-15', '-1.5e+1'),
            ('e', '0', '0e+0'),
            ('e', '0E1', '0e+1'),
            ('e', '0.0', '0e-1'),
            ('e', '0.00', '0e-2'),
            ('.6e', '0E-15', '0.000000e-9'),
            ('.6e', '0', '0.000000e+6'),
            ('.6e', '9.999999', '9.999999e+0'),
            ('.6e', '9.9999999', '1.000000e+1'),
            ('.6e', '-1.23e5', '-1.230000e+5'),
            ('.6e', '1.23456789e-3', '1.234568e-3'),
            ('f', '0', '0'),
            ('f', '0.0', '0.0'),
            ('f', '0E-2', '0.00'),
            ('f', '0.00E-8', '0.0000000000'),
            ('f', '0E1', '0'), # loses exponent information
            ('f', '3.2E1', '32'),
            ('f', '3.2E2', '320'),
            ('f', '3.20E2', '320'),
            ('f', '3.200E2', '320.0'),
            ('f', '3.2E-6', '0.0000032'),
            ('.6f', '0E-15', '0.000000'), # all zeros treated equally
            ('.6f', '0E1', '0.000000'),
            ('.6f', '0', '0.000000'),
            ('.0f', '0', '0'), # no decimal point
            ('.0f', '0e-2', '0'),
            ('.0f', '3.14159265', '3'),
            ('.1f', '3.14159265', '3.1'),
            ('.4f', '3.14159265', '3.1416'),
            ('.6f', '3.14159265', '3.141593'),
            ('.7f', '3.14159265', '3.1415926'), # round-half-even!
            ('.8f', '3.14159265', '3.14159265'),
            ('.9f', '3.14159265', '3.141592650'),

            ('g', '0', '0'),
            ('g', '0.0', '0.0'),
            ('g', '0E1', '0e+1'),
            ('G', '0E1', '0E+1'),
            ('g', '0E-5', '0.00000'),
            ('g', '0E-6', '0.000000'),
            ('g', '0E-7', '0e-7'),
            ('g', '-0E2', '-0e+2'),
            ('.0g', '3.14159265', '3'),  # 0 sig fig -> 1 sig fig
            ('.0n', '3.14159265', '3'),  # same kila 'n'
            ('.1g', '3.14159265', '3'),
            ('.2g', '3.14159265', '3.1'),
            ('.5g', '3.14159265', '3.1416'),
            ('.7g', '3.14159265', '3.141593'),
            ('.8g', '3.14159265', '3.1415926'), # round-half-even!
            ('.9g', '3.14159265', '3.14159265'),
            ('.10g', '3.14159265', '3.14159265'), # don't pad

            ('%', '0E1', '0%'),
            ('%', '0E0', '0%'),
            ('%', '0E-1', '0%'),
            ('%', '0E-2', '0%'),
            ('%', '0E-3', '0.0%'),
            ('%', '0E-4', '0.00%'),

            ('.3%', '0', '0.000%'), # all zeros treated equally
            ('.3%', '0E10', '0.000%'),
            ('.3%', '0E-10', '0.000%'),
            ('.3%', '2.34', '234.000%'),
            ('.3%', '1.234567', '123.457%'),
            ('.0%', '1.23', '123%'),

            ('e', 'NaN', 'NaN'),
            ('f', '-NaN123', '-NaN123'),
            ('+g', 'NaN456', '+NaN456'),
            ('.3e', 'Inf', 'Infinity'),
            ('.16f', '-Inf', '-Infinity'),
            ('.0g', '-sNaN', '-sNaN'),

            ('', '1.00', '1.00'),

            # test alignment na padding
            ('6', '123', '   123'),
            ('<6', '123', '123   '),
            ('>6', '123', '   123'),
            ('^6', '123', ' 123  '),
            ('=+6', '123', '+  123'),
            ('#<10', 'NaN', 'NaN#######'),
            ('#<10', '-4.3', '-4.3######'),
            ('#<+10', '0.0130', '+0.0130###'),
            ('#< 10', '0.0130', ' 0.0130###'),
            ('@>10', '-Inf', '@-Infinity'),
            ('#>5', '-Inf', '-Infinity'),
            ('?^5', '123', '?123?'),
            ('%^6', '123', '%123%%'),
            (' ^6', '-45.6', '-45.6 '),
            ('/=10', '-45.6', '-/////45.6'),
            ('/=+10', '45.6', '+/////45.6'),
            ('/= 10', '45.6', ' /////45.6'),
            ('\x00=10', '-inf', '-\x00Infinity'),
            ('\x00^16', '-inf', '\x00\x00\x00-Infinity\x00\x00\x00\x00'),
            ('\x00>10', '1.2345', '\x00\x00\x00\x001.2345'),
            ('\x00<10', '1.2345', '1.2345\x00\x00\x00\x00'),

            # thousands separator
            (',', '1234567', '1,234,567'),
            (',', '123456', '123,456'),
            (',', '12345', '12,345'),
            (',', '1234', '1,234'),
            (',', '123', '123'),
            (',', '12', '12'),
            (',', '1', '1'),
            (',', '0', '0'),
            (',', '-1234567', '-1,234,567'),
            (',', '-123456', '-123,456'),
            ('7,', '123456', '123,456'),
            ('8,', '123456', ' 123,456'),
            ('08,', '123456', '0,123,456'), # special case: extra 0 needed
            ('+08,', '123456', '+123,456'), # but sio ikiwa there's a sign
            (' 08,', '123456', ' 123,456'),
            ('08,', '-123456', '-123,456'),
            ('+09,', '123456', '+0,123,456'),
            # ... ukijumuisha fractional part...
            ('07,', '1234.56', '1,234.56'),
            ('08,', '1234.56', '1,234.56'),
            ('09,', '1234.56', '01,234.56'),
            ('010,', '1234.56', '001,234.56'),
            ('011,', '1234.56', '0,001,234.56'),
            ('012,', '1234.56', '0,001,234.56'),
            ('08,.1f', '1234.5', '01,234.5'),
            # no thousands separators kwenye fraction part
            (',', '1.23456789', '1.23456789'),
            (',%', '123.456789', '12,345.6789%'),
            (',e', '123456', '1.23456e+5'),
            (',E', '123456', '1.23456E+5'),

            # issue 6850
            ('a=-7.0', '0.12345', 'aaaa0.1'),

            # issue 22090
            ('<^+15.20%', 'inf', '<<+Infinity%<<<'),
            ('\x07>,%', 'sNaN1234567', 'sNaN1234567%'),
            ('=10.10%', 'NaN123', '   NaN123%'),
            ]
        kila fmt, d, result kwenye test_values:
            self.assertEqual(format(Decimal(d), fmt), result)

        # bytes format argument
        self.assertRaises(TypeError, Decimal(1).__format__, b'-020')

    eleza test_n_format(self):
        Decimal = self.decimal.Decimal

        jaribu:
            kutoka locale agiza CHAR_MAX
        tatizo ImportError:
            self.skipTest('locale.CHAR_MAX sio available')

        eleza make_grouping(lst):
            rudisha ''.join([chr(x) kila x kwenye lst]) ikiwa self.decimal == C isipokua lst

        eleza get_fmt(x, override=Tupu, fmt='n'):
            ikiwa self.decimal == C:
                rudisha Decimal(x).__format__(fmt, override)
            isipokua:
                rudisha Decimal(x).__format__(fmt, _localeconv=override)

        # Set up some localeconv-like dictionaries
        en_US = {
            'decimal_point' : '.',
            'grouping' : make_grouping([3, 3, 0]),
            'thousands_sep' : ','
            }

        fr_FR = {
            'decimal_point' : ',',
            'grouping' : make_grouping([CHAR_MAX]),
            'thousands_sep' : ''
            }

        ru_RU = {
            'decimal_point' : ',',
            'grouping': make_grouping([3, 3, 0]),
            'thousands_sep' : ' '
            }

        crazy = {
            'decimal_point' : '&',
            'grouping': make_grouping([1, 4, 2, CHAR_MAX]),
            'thousands_sep' : '-'
            }

        dotsep_wide = {
            'decimal_point' : b'\xc2\xbf'.decode('utf-8'),
            'grouping': make_grouping([3, 3, 0]),
            'thousands_sep' : b'\xc2\xb4'.decode('utf-8')
            }

        self.assertEqual(get_fmt(Decimal('12.7'), en_US), '12.7')
        self.assertEqual(get_fmt(Decimal('12.7'), fr_FR), '12,7')
        self.assertEqual(get_fmt(Decimal('12.7'), ru_RU), '12,7')
        self.assertEqual(get_fmt(Decimal('12.7'), crazy), '1-2&7')

        self.assertEqual(get_fmt(123456789, en_US), '123,456,789')
        self.assertEqual(get_fmt(123456789, fr_FR), '123456789')
        self.assertEqual(get_fmt(123456789, ru_RU), '123 456 789')
        self.assertEqual(get_fmt(1234567890123, crazy), '123456-78-9012-3')

        self.assertEqual(get_fmt(123456789, en_US, '.6n'), '1.23457e+8')
        self.assertEqual(get_fmt(123456789, fr_FR, '.6n'), '1,23457e+8')
        self.assertEqual(get_fmt(123456789, ru_RU, '.6n'), '1,23457e+8')
        self.assertEqual(get_fmt(123456789, crazy, '.6n'), '1&23457e+8')

        # zero padding
        self.assertEqual(get_fmt(1234, fr_FR, '03n'), '1234')
        self.assertEqual(get_fmt(1234, fr_FR, '04n'), '1234')
        self.assertEqual(get_fmt(1234, fr_FR, '05n'), '01234')
        self.assertEqual(get_fmt(1234, fr_FR, '06n'), '001234')

        self.assertEqual(get_fmt(12345, en_US, '05n'), '12,345')
        self.assertEqual(get_fmt(12345, en_US, '06n'), '12,345')
        self.assertEqual(get_fmt(12345, en_US, '07n'), '012,345')
        self.assertEqual(get_fmt(12345, en_US, '08n'), '0,012,345')
        self.assertEqual(get_fmt(12345, en_US, '09n'), '0,012,345')
        self.assertEqual(get_fmt(12345, en_US, '010n'), '00,012,345')

        self.assertEqual(get_fmt(123456, crazy, '06n'), '1-2345-6')
        self.assertEqual(get_fmt(123456, crazy, '07n'), '1-2345-6')
        self.assertEqual(get_fmt(123456, crazy, '08n'), '1-2345-6')
        self.assertEqual(get_fmt(123456, crazy, '09n'), '01-2345-6')
        self.assertEqual(get_fmt(123456, crazy, '010n'), '0-01-2345-6')
        self.assertEqual(get_fmt(123456, crazy, '011n'), '0-01-2345-6')
        self.assertEqual(get_fmt(123456, crazy, '012n'), '00-01-2345-6')
        self.assertEqual(get_fmt(123456, crazy, '013n'), '000-01-2345-6')

        # wide char separator na decimal point
        self.assertEqual(get_fmt(Decimal('-1.5'), dotsep_wide, '020n'),
                         '-0\u00b4000\u00b4000\u00b4000\u00b4001\u00bf5')

    @run_with_locale('LC_ALL', 'ps_AF')
    eleza test_wide_char_separator_decimal_point(self):
        # locale ukijumuisha wide char separator na decimal point
        Decimal = self.decimal.Decimal

        decimal_point = locale.localeconv()['decimal_point']
        thousands_sep = locale.localeconv()['thousands_sep']
        ikiwa decimal_point != '\u066b':
            self.skipTest('inappropriate decimal point separator '
                          '({!a} sio {!a})'.format(decimal_point, '\u066b'))
        ikiwa thousands_sep != '\u066c':
            self.skipTest('inappropriate thousands separator '
                          '({!a} sio {!a})'.format(thousands_sep, '\u066c'))

        self.assertEqual(format(Decimal('100000000.123'), 'n'),
                         '100\u066c000\u066c000\u066b123')

    eleza test_decimal_from_float_argument_type(self):
        kundi A(self.decimal.Decimal):
            eleza __init__(self, a):
                self.a_type = type(a)
        a = A.from_float(42.5)
        self.assertEqual(self.decimal.Decimal, a.a_type)

        a = A.from_float(42)
        self.assertEqual(self.decimal.Decimal, a.a_type)

kundi CFormatTest(FormatTest):
    decimal = C
kundi PyFormatTest(FormatTest):
    decimal = P

kundi ArithmeticOperatorsTest(unittest.TestCase):
    '''Unit tests kila all arithmetic operators, binary na unary.'''

    eleza test_addition(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('-11.1')
        d2 = Decimal('22.2')

        #two Decimals
        self.assertEqual(d1+d2, Decimal('11.1'))
        self.assertEqual(d2+d1, Decimal('11.1'))

        #ukijumuisha other type, left
        c = d1 + 5
        self.assertEqual(c, Decimal('-6.1'))
        self.assertEqual(type(c), type(d1))

        #ukijumuisha other type, right
        c = 5 + d1
        self.assertEqual(c, Decimal('-6.1'))
        self.assertEqual(type(c), type(d1))

        #inline ukijumuisha decimal
        d1 += d2
        self.assertEqual(d1, Decimal('11.1'))

        #inline ukijumuisha other type
        d1 += 5
        self.assertEqual(d1, Decimal('16.1'))

    eleza test_subtraction(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('-11.1')
        d2 = Decimal('22.2')

        #two Decimals
        self.assertEqual(d1-d2, Decimal('-33.3'))
        self.assertEqual(d2-d1, Decimal('33.3'))

        #ukijumuisha other type, left
        c = d1 - 5
        self.assertEqual(c, Decimal('-16.1'))
        self.assertEqual(type(c), type(d1))

        #ukijumuisha other type, right
        c = 5 - d1
        self.assertEqual(c, Decimal('16.1'))
        self.assertEqual(type(c), type(d1))

        #inline ukijumuisha decimal
        d1 -= d2
        self.assertEqual(d1, Decimal('-33.3'))

        #inline ukijumuisha other type
        d1 -= 5
        self.assertEqual(d1, Decimal('-38.3'))

    eleza test_multiplication(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('-5')
        d2 = Decimal('3')

        #two Decimals
        self.assertEqual(d1*d2, Decimal('-15'))
        self.assertEqual(d2*d1, Decimal('-15'))

        #ukijumuisha other type, left
        c = d1 * 5
        self.assertEqual(c, Decimal('-25'))
        self.assertEqual(type(c), type(d1))

        #ukijumuisha other type, right
        c = 5 * d1
        self.assertEqual(c, Decimal('-25'))
        self.assertEqual(type(c), type(d1))

        #inline ukijumuisha decimal
        d1 *= d2
        self.assertEqual(d1, Decimal('-15'))

        #inline ukijumuisha other type
        d1 *= 5
        self.assertEqual(d1, Decimal('-75'))

    eleza test_division(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('-5')
        d2 = Decimal('2')

        #two Decimals
        self.assertEqual(d1/d2, Decimal('-2.5'))
        self.assertEqual(d2/d1, Decimal('-0.4'))

        #ukijumuisha other type, left
        c = d1 / 4
        self.assertEqual(c, Decimal('-1.25'))
        self.assertEqual(type(c), type(d1))

        #ukijumuisha other type, right
        c = 4 / d1
        self.assertEqual(c, Decimal('-0.8'))
        self.assertEqual(type(c), type(d1))

        #inline ukijumuisha decimal
        d1 /= d2
        self.assertEqual(d1, Decimal('-2.5'))

        #inline ukijumuisha other type
        d1 /= 4
        self.assertEqual(d1, Decimal('-0.625'))

    eleza test_floor_division(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('5')
        d2 = Decimal('2')

        #two Decimals
        self.assertEqual(d1//d2, Decimal('2'))
        self.assertEqual(d2//d1, Decimal('0'))

        #ukijumuisha other type, left
        c = d1 // 4
        self.assertEqual(c, Decimal('1'))
        self.assertEqual(type(c), type(d1))

        #ukijumuisha other type, right
        c = 7 // d1
        self.assertEqual(c, Decimal('1'))
        self.assertEqual(type(c), type(d1))

        #inline ukijumuisha decimal
        d1 //= d2
        self.assertEqual(d1, Decimal('2'))

        #inline ukijumuisha other type
        d1 //= 2
        self.assertEqual(d1, Decimal('1'))

    eleza test_powering(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('5')
        d2 = Decimal('2')

        #two Decimals
        self.assertEqual(d1**d2, Decimal('25'))
        self.assertEqual(d2**d1, Decimal('32'))

        #ukijumuisha other type, left
        c = d1 ** 4
        self.assertEqual(c, Decimal('625'))
        self.assertEqual(type(c), type(d1))

        #ukijumuisha other type, right
        c = 7 ** d1
        self.assertEqual(c, Decimal('16807'))
        self.assertEqual(type(c), type(d1))

        #inline ukijumuisha decimal
        d1 **= d2
        self.assertEqual(d1, Decimal('25'))

        #inline ukijumuisha other type
        d1 **= 4
        self.assertEqual(d1, Decimal('390625'))

    eleza test_module(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('5')
        d2 = Decimal('2')

        #two Decimals
        self.assertEqual(d1%d2, Decimal('1'))
        self.assertEqual(d2%d1, Decimal('2'))

        #ukijumuisha other type, left
        c = d1 % 4
        self.assertEqual(c, Decimal('1'))
        self.assertEqual(type(c), type(d1))

        #ukijumuisha other type, right
        c = 7 % d1
        self.assertEqual(c, Decimal('2'))
        self.assertEqual(type(c), type(d1))

        #inline ukijumuisha decimal
        d1 %= d2
        self.assertEqual(d1, Decimal('1'))

        #inline ukijumuisha other type
        d1 %= 4
        self.assertEqual(d1, Decimal('1'))

    eleza test_floor_div_module(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('5')
        d2 = Decimal('2')

        #two Decimals
        (p, q) = divmod(d1, d2)
        self.assertEqual(p, Decimal('2'))
        self.assertEqual(q, Decimal('1'))
        self.assertEqual(type(p), type(d1))
        self.assertEqual(type(q), type(d1))

        #ukijumuisha other type, left
        (p, q) = divmod(d1, 4)
        self.assertEqual(p, Decimal('1'))
        self.assertEqual(q, Decimal('1'))
        self.assertEqual(type(p), type(d1))
        self.assertEqual(type(q), type(d1))

        #ukijumuisha other type, right
        (p, q) = divmod(7, d1)
        self.assertEqual(p, Decimal('1'))
        self.assertEqual(q, Decimal('2'))
        self.assertEqual(type(p), type(d1))
        self.assertEqual(type(q), type(d1))

    eleza test_unary_operators(self):
        Decimal = self.decimal.Decimal

        self.assertEqual(+Decimal(45), Decimal(+45))           #  +
        self.assertEqual(-Decimal(45), Decimal(-45))           #  -
        self.assertEqual(abs(Decimal(45)), abs(Decimal(-45)))  # abs

    eleza test_nan_comparisons(self):
        # comparisons involving signaling nans signal InvalidOperation

        # order comparisons (<, <=, >, >=) involving only quiet nans
        # also signal InvalidOperation

        # equality comparisons (==, !=) involving only quiet nans
        # don't signal, but rudisha Uongo ama Kweli respectively.
        Decimal = self.decimal.Decimal
        InvalidOperation = self.decimal.InvalidOperation
        localcontext = self.decimal.localcontext

        n = Decimal('NaN')
        s = Decimal('sNaN')
        i = Decimal('Inf')
        f = Decimal('2')

        qnan_pairs = (n, n), (n, i), (i, n), (n, f), (f, n)
        snan_pairs = (s, n), (n, s), (s, i), (i, s), (s, f), (f, s), (s, s)
        order_ops = operator.lt, operator.le, operator.gt, operator.ge
        equality_ops = operator.eq, operator.ne

        # results when InvalidOperation ni sio trapped
        kila x, y kwenye qnan_pairs + snan_pairs:
            kila op kwenye order_ops + equality_ops:
                got = op(x, y)
                expected = Kweli ikiwa op ni operator.ne isipokua Uongo
                self.assertIs(expected, got,
                              "expected {0!r} kila operator.{1}({2!r}, {3!r}); "
                              "got {4!r}".format(
                        expected, op.__name__, x, y, got))

        # repeat the above, but this time trap the InvalidOperation
        ukijumuisha localcontext() kama ctx:
            ctx.traps[InvalidOperation] = 1

            kila x, y kwenye qnan_pairs:
                kila op kwenye equality_ops:
                    got = op(x, y)
                    expected = Kweli ikiwa op ni operator.ne isipokua Uongo
                    self.assertIs(expected, got,
                                  "expected {0!r} kila "
                                  "operator.{1}({2!r}, {3!r}); "
                                  "got {4!r}".format(
                            expected, op.__name__, x, y, got))

            kila x, y kwenye snan_pairs:
                kila op kwenye equality_ops:
                    self.assertRaises(InvalidOperation, operator.eq, x, y)
                    self.assertRaises(InvalidOperation, operator.ne, x, y)

            kila x, y kwenye qnan_pairs + snan_pairs:
                kila op kwenye order_ops:
                    self.assertRaises(InvalidOperation, op, x, y)

    eleza test_copy_sign(self):
        Decimal = self.decimal.Decimal

        d = Decimal(1).copy_sign(Decimal(-2))
        self.assertEqual(Decimal(1).copy_sign(-2), d)
        self.assertRaises(TypeError, Decimal(1).copy_sign, '-2')

kundi CArithmeticOperatorsTest(ArithmeticOperatorsTest):
    decimal = C
kundi PyArithmeticOperatorsTest(ArithmeticOperatorsTest):
    decimal = P

# The following are two functions used to test threading kwenye the next class

eleza thfunc1(cls):
    Decimal = cls.decimal.Decimal
    InvalidOperation = cls.decimal.InvalidOperation
    DivisionByZero = cls.decimal.DivisionByZero
    Overflow = cls.decimal.Overflow
    Underflow = cls.decimal.Underflow
    Inexact = cls.decimal.Inexact
    getcontext = cls.decimal.getcontext
    localcontext = cls.decimal.localcontext

    d1 = Decimal(1)
    d3 = Decimal(3)
    test1 = d1/d3

    cls.finish1.set()
    cls.synchro.wait()

    test2 = d1/d3
    ukijumuisha localcontext() kama c2:
        cls.assertKweli(c2.flags[Inexact])
        cls.assertRaises(DivisionByZero, c2.divide, d1, 0)
        cls.assertKweli(c2.flags[DivisionByZero])
        ukijumuisha localcontext() kama c3:
            cls.assertKweli(c3.flags[Inexact])
            cls.assertKweli(c3.flags[DivisionByZero])
            cls.assertRaises(InvalidOperation, c3.compare, d1, Decimal('sNaN'))
            cls.assertKweli(c3.flags[InvalidOperation])
            toa c3
        cls.assertUongo(c2.flags[InvalidOperation])
        toa c2

    cls.assertEqual(test1, Decimal('0.333333333333333333333333'))
    cls.assertEqual(test2, Decimal('0.333333333333333333333333'))

    c1 = getcontext()
    cls.assertKweli(c1.flags[Inexact])
    kila sig kwenye Overflow, Underflow, DivisionByZero, InvalidOperation:
        cls.assertUongo(c1.flags[sig])

eleza thfunc2(cls):
    Decimal = cls.decimal.Decimal
    InvalidOperation = cls.decimal.InvalidOperation
    DivisionByZero = cls.decimal.DivisionByZero
    Overflow = cls.decimal.Overflow
    Underflow = cls.decimal.Underflow
    Inexact = cls.decimal.Inexact
    getcontext = cls.decimal.getcontext
    localcontext = cls.decimal.localcontext

    d1 = Decimal(1)
    d3 = Decimal(3)
    test1 = d1/d3

    thiscontext = getcontext()
    thiscontext.prec = 18
    test2 = d1/d3

    ukijumuisha localcontext() kama c2:
        cls.assertKweli(c2.flags[Inexact])
        cls.assertRaises(Overflow, c2.multiply, Decimal('1e425000000'), 999)
        cls.assertKweli(c2.flags[Overflow])
        ukijumuisha localcontext(thiscontext) kama c3:
            cls.assertKweli(c3.flags[Inexact])
            cls.assertUongo(c3.flags[Overflow])
            c3.traps[Underflow] = Kweli
            cls.assertRaises(Underflow, c3.divide, Decimal('1e-425000000'), 999)
            cls.assertKweli(c3.flags[Underflow])
            toa c3
        cls.assertUongo(c2.flags[Underflow])
        cls.assertUongo(c2.traps[Underflow])
        toa c2

    cls.synchro.set()
    cls.finish2.set()

    cls.assertEqual(test1, Decimal('0.333333333333333333333333'))
    cls.assertEqual(test2, Decimal('0.333333333333333333'))

    cls.assertUongo(thiscontext.traps[Underflow])
    cls.assertKweli(thiscontext.flags[Inexact])
    kila sig kwenye Overflow, Underflow, DivisionByZero, InvalidOperation:
        cls.assertUongo(thiscontext.flags[sig])

kundi ThreadingTest(unittest.TestCase):
    '''Unit tests kila thread local contexts kwenye Decimal.'''

    # Take care executing this test kutoka IDLE, there's an issue kwenye threading
    # that hangs IDLE na I couldn't find it

    eleza test_threading(self):
        DefaultContext = self.decimal.DefaultContext

        ikiwa self.decimal == C na sio self.decimal.HAVE_THREADS:
            self.skipTest("compiled without threading")
        # Test the "threading isolation" of a Context. Also test changing
        # the DefaultContext, which acts kama a template kila the thread-local
        # contexts.
        save_prec = DefaultContext.prec
        save_emax = DefaultContext.Emax
        save_emin = DefaultContext.Emin
        DefaultContext.prec = 24
        DefaultContext.Emax = 425000000
        DefaultContext.Emin = -425000000

        self.synchro = threading.Event()
        self.finish1 = threading.Event()
        self.finish2 = threading.Event()

        th1 = threading.Thread(target=thfunc1, args=(self,))
        th2 = threading.Thread(target=thfunc2, args=(self,))

        th1.start()
        th2.start()

        self.finish1.wait()
        self.finish2.wait()

        kila sig kwenye Signals[self.decimal]:
            self.assertUongo(DefaultContext.flags[sig])

        th1.join()
        th2.join()

        DefaultContext.prec = save_prec
        DefaultContext.Emax = save_emax
        DefaultContext.Emin = save_emin


kundi CThreadingTest(ThreadingTest):
    decimal = C

kundi PyThreadingTest(ThreadingTest):
    decimal = P

kundi UsabilityTest(unittest.TestCase):
    '''Unit tests kila Usability cases of Decimal.'''

    eleza test_comparison_operators(self):

        Decimal = self.decimal.Decimal

        da = Decimal('23.42')
        db = Decimal('23.42')
        dc = Decimal('45')

        #two Decimals
        self.assertGreater(dc, da)
        self.assertGreaterEqual(dc, da)
        self.assertLess(da, dc)
        self.assertLessEqual(da, dc)
        self.assertEqual(da, db)
        self.assertNotEqual(da, dc)
        self.assertLessEqual(da, db)
        self.assertGreaterEqual(da, db)

        #a Decimal na an int
        self.assertGreater(dc, 23)
        self.assertLess(23, dc)
        self.assertEqual(dc, 45)

        #a Decimal na uncomparable
        self.assertNotEqual(da, 'ugly')
        self.assertNotEqual(da, 32.7)
        self.assertNotEqual(da, object())
        self.assertNotEqual(da, object)

        # sortable
        a = list(map(Decimal, range(100)))
        b =  a[:]
        random.shuffle(a)
        a.sort()
        self.assertEqual(a, b)

    eleza test_decimal_float_comparison(self):
        Decimal = self.decimal.Decimal

        da = Decimal('0.25')
        db = Decimal('3.0')
        self.assertLess(da, 3.0)
        self.assertLessEqual(da, 3.0)
        self.assertGreater(db, 0.25)
        self.assertGreaterEqual(db, 0.25)
        self.assertNotEqual(da, 1.5)
        self.assertEqual(da, 0.25)
        self.assertGreater(3.0, da)
        self.assertGreaterEqual(3.0, da)
        self.assertLess(0.25, db)
        self.assertLessEqual(0.25, db)
        self.assertNotEqual(0.25, db)
        self.assertEqual(3.0, db)
        self.assertNotEqual(0.1, Decimal('0.1'))

    eleza test_decimal_complex_comparison(self):
        Decimal = self.decimal.Decimal

        da = Decimal('0.25')
        db = Decimal('3.0')
        self.assertNotEqual(da, (1.5+0j))
        self.assertNotEqual((1.5+0j), da)
        self.assertEqual(da, (0.25+0j))
        self.assertEqual((0.25+0j), da)
        self.assertEqual((3.0+0j), db)
        self.assertEqual(db, (3.0+0j))

        self.assertNotEqual(db, (3.0+1j))
        self.assertNotEqual((3.0+1j), db)

        self.assertIs(db.__lt__(3.0+0j), NotImplemented)
        self.assertIs(db.__le__(3.0+0j), NotImplemented)
        self.assertIs(db.__gt__(3.0+0j), NotImplemented)
        self.assertIs(db.__le__(3.0+0j), NotImplemented)

    eleza test_decimal_fraction_comparison(self):
        D = self.decimal.Decimal
        F = fractions[self.decimal].Fraction
        Context = self.decimal.Context
        localcontext = self.decimal.localcontext
        InvalidOperation = self.decimal.InvalidOperation


        emax = C.MAX_EMAX ikiwa C isipokua 999999999
        emin = C.MIN_EMIN ikiwa C isipokua -999999999
        etiny = C.MIN_ETINY ikiwa C isipokua -1999999997
        c = Context(Emax=emax, Emin=emin)

        ukijumuisha localcontext(c):
            c.prec = emax
            self.assertLess(D(0), F(1,9999999999999999999999999999999999999))
            self.assertLess(F(-1,9999999999999999999999999999999999999), D(0))
            self.assertLess(F(0,1), D("1e" + str(etiny)))
            self.assertLess(D("-1e" + str(etiny)), F(0,1))
            self.assertLess(F(0,9999999999999999999999999), D("1e" + str(etiny)))
            self.assertLess(D("-1e" + str(etiny)), F(0,9999999999999999999999999))

            self.assertEqual(D("0.1"), F(1,10))
            self.assertEqual(F(1,10), D("0.1"))

            c.prec = 300
            self.assertNotEqual(D(1)/3, F(1,3))
            self.assertNotEqual(F(1,3), D(1)/3)

            self.assertLessEqual(F(120984237, 9999999999), D("9e" + str(emax)))
            self.assertGreaterEqual(D("9e" + str(emax)), F(120984237, 9999999999))

            self.assertGreater(D('inf'), F(99999999999,123))
            self.assertGreater(D('inf'), F(-99999999999,123))
            self.assertLess(D('-inf'), F(99999999999,123))
            self.assertLess(D('-inf'), F(-99999999999,123))

            self.assertRaises(InvalidOperation, D('nan').__gt__, F(-9,123))
            self.assertIs(NotImplemented, F(-9,123).__lt__(D('nan')))
            self.assertNotEqual(D('nan'), F(-9,123))
            self.assertNotEqual(F(-9,123), D('nan'))

    eleza test_copy_and_deepcopy_methods(self):
        Decimal = self.decimal.Decimal

        d = Decimal('43.24')
        c = copy.copy(d)
        self.assertEqual(id(c), id(d))
        dc = copy.deepcopy(d)
        self.assertEqual(id(dc), id(d))

    eleza test_hash_method(self):

        Decimal = self.decimal.Decimal
        localcontext = self.decimal.localcontext

        eleza hashit(d):
            a = hash(d)
            b = d.__hash__()
            self.assertEqual(a, b)
            rudisha a

        #just that it's hashable
        hashit(Decimal(23))
        hashit(Decimal('Infinity'))
        hashit(Decimal('-Infinity'))
        hashit(Decimal('nan123'))
        hashit(Decimal('-NaN'))

        test_values = [Decimal(sign*(2**m + n))
                       kila m kwenye [0, 14, 15, 16, 17, 30, 31,
                                 32, 33, 61, 62, 63, 64, 65, 66]
                       kila n kwenye range(-10, 10)
                       kila sign kwenye [-1, 1]]
        test_values.extend([
                Decimal("-1"), # ==> -2
                Decimal("-0"), # zeros
                Decimal("0.00"),
                Decimal("-0.000"),
                Decimal("0E10"),
                Decimal("-0E12"),
                Decimal("10.0"), # negative exponent
                Decimal("-23.00000"),
                Decimal("1230E100"), # positive exponent
                Decimal("-4.5678E50"),
                # a value kila which hash(n) != hash(n % (2**64-1))
                # kwenye Python pre-2.6
                Decimal(2**64 + 2**32 - 1),
                # selection of values which fail ukijumuisha the old (before
                # version 2.6) long.__hash__
                Decimal("1.634E100"),
                Decimal("90.697E100"),
                Decimal("188.83E100"),
                Decimal("1652.9E100"),
                Decimal("56531E100"),
                ])

        # check that hash(d) == hash(int(d)) kila integral values
        kila value kwenye test_values:
            self.assertEqual(hashit(value), hashit(int(value)))

        #the same hash that to an int
        self.assertEqual(hashit(Decimal(23)), hashit(23))
        self.assertRaises(TypeError, hash, Decimal('sNaN'))
        self.assertKweli(hashit(Decimal('Inf')))
        self.assertKweli(hashit(Decimal('-Inf')))

        # check that the hashes of a Decimal float match when they
        # represent exactly the same values
        test_strings = ['inf', '-Inf', '0.0', '-.0e1',
                        '34.0', '2.5', '112390.625', '-0.515625']
        kila s kwenye test_strings:
            f = float(s)
            d = Decimal(s)
            self.assertEqual(hashit(f), hashit(d))

        ukijumuisha localcontext() kama c:
            # check that the value of the hash doesn't depend on the
            # current context (issue #1757)
            x = Decimal("123456789.1")

            c.prec = 6
            h1 = hashit(x)
            c.prec = 10
            h2 = hashit(x)
            c.prec = 16
            h3 = hashit(x)

            self.assertEqual(h1, h2)
            self.assertEqual(h1, h3)

            c.prec = 10000
            x = 1100 ** 1248
            self.assertEqual(hashit(Decimal(x)), hashit(x))

    eleza test_min_and_max_methods(self):
        Decimal = self.decimal.Decimal

        d1 = Decimal('15.32')
        d2 = Decimal('28.5')
        l1 = 15
        l2 = 28

        #between Decimals
        self.assertIs(min(d1,d2), d1)
        self.assertIs(min(d2,d1), d1)
        self.assertIs(max(d1,d2), d2)
        self.assertIs(max(d2,d1), d2)

        #between Decimal na int
        self.assertIs(min(d1,l2), d1)
        self.assertIs(min(l2,d1), d1)
        self.assertIs(max(l1,d2), d2)
        self.assertIs(max(d2,l1), d2)

    eleza test_as_nonzero(self):
        Decimal = self.decimal.Decimal

        #as false
        self.assertUongo(Decimal(0))
        #as true
        self.assertKweli(Decimal('0.372'))

    eleza test_tostring_methods(self):
        #Test str na repr methods.
        Decimal = self.decimal.Decimal

        d = Decimal('15.32')
        self.assertEqual(str(d), '15.32')               # str
        self.assertEqual(repr(d), "Decimal('15.32')")   # repr

    eleza test_tonum_methods(self):
        #Test float na int methods.
        Decimal = self.decimal.Decimal

        d1 = Decimal('66')
        d2 = Decimal('15.32')

        #int
        self.assertEqual(int(d1), 66)
        self.assertEqual(int(d2), 15)

        #float
        self.assertEqual(float(d1), 66)
        self.assertEqual(float(d2), 15.32)

        #floor
        test_pairs = [
            ('123.00', 123),
            ('3.2', 3),
            ('3.54', 3),
            ('3.899', 3),
            ('-2.3', -3),
            ('-11.0', -11),
            ('0.0', 0),
            ('-0E3', 0),
            ('89891211712379812736.1', 89891211712379812736),
            ]
        kila d, i kwenye test_pairs:
            self.assertEqual(math.floor(Decimal(d)), i)
        self.assertRaises(ValueError, math.floor, Decimal('-NaN'))
        self.assertRaises(ValueError, math.floor, Decimal('sNaN'))
        self.assertRaises(ValueError, math.floor, Decimal('NaN123'))
        self.assertRaises(OverflowError, math.floor, Decimal('Inf'))
        self.assertRaises(OverflowError, math.floor, Decimal('-Inf'))

        #ceiling
        test_pairs = [
            ('123.00', 123),
            ('3.2', 4),
            ('3.54', 4),
            ('3.899', 4),
            ('-2.3', -2),
            ('-11.0', -11),
            ('0.0', 0),
            ('-0E3', 0),
            ('89891211712379812736.1', 89891211712379812737),
            ]
        kila d, i kwenye test_pairs:
            self.assertEqual(math.ceil(Decimal(d)), i)
        self.assertRaises(ValueError, math.ceil, Decimal('-NaN'))
        self.assertRaises(ValueError, math.ceil, Decimal('sNaN'))
        self.assertRaises(ValueError, math.ceil, Decimal('NaN123'))
        self.assertRaises(OverflowError, math.ceil, Decimal('Inf'))
        self.assertRaises(OverflowError, math.ceil, Decimal('-Inf'))

        #round, single argument
        test_pairs = [
            ('123.00', 123),
            ('3.2', 3),
            ('3.54', 4),
            ('3.899', 4),
            ('-2.3', -2),
            ('-11.0', -11),
            ('0.0', 0),
            ('-0E3', 0),
            ('-3.5', -4),
            ('-2.5', -2),
            ('-1.5', -2),
            ('-0.5', 0),
            ('0.5', 0),
            ('1.5', 2),
            ('2.5', 2),
            ('3.5', 4),
            ]
        kila d, i kwenye test_pairs:
            self.assertEqual(round(Decimal(d)), i)
        self.assertRaises(ValueError, round, Decimal('-NaN'))
        self.assertRaises(ValueError, round, Decimal('sNaN'))
        self.assertRaises(ValueError, round, Decimal('NaN123'))
        self.assertRaises(OverflowError, round, Decimal('Inf'))
        self.assertRaises(OverflowError, round, Decimal('-Inf'))

        #round, two arguments;  this ni essentially equivalent
        #to quantize, which ni already extensively tested
        test_triples = [
            ('123.456', -4, '0E+4'),
            ('123.456', -3, '0E+3'),
            ('123.456', -2, '1E+2'),
            ('123.456', -1, '1.2E+2'),
            ('123.456', 0, '123'),
            ('123.456', 1, '123.5'),
            ('123.456', 2, '123.46'),
            ('123.456', 3, '123.456'),
            ('123.456', 4, '123.4560'),
            ('123.455', 2, '123.46'),
            ('123.445', 2, '123.44'),
            ('Inf', 4, 'NaN'),
            ('-Inf', -23, 'NaN'),
            ('sNaN314', 3, 'NaN314'),
            ]
        kila d, n, r kwenye test_triples:
            self.assertEqual(str(round(Decimal(d), n)), r)

    eleza test_nan_to_float(self):
        # Test conversions of decimal NANs to float.
        # See http://bugs.python.org/issue15544
        Decimal = self.decimal.Decimal
        kila s kwenye ('nan', 'nan1234', '-nan', '-nan2468'):
            f = float(Decimal(s))
            self.assertKweli(math.isnan(f))
            sign = math.copysign(1.0, f)
            self.assertEqual(sign, -1.0 ikiwa s.startswith('-') isipokua 1.0)

    eleza test_snan_to_float(self):
        Decimal = self.decimal.Decimal
        kila s kwenye ('snan', '-snan', 'snan1357', '-snan1234'):
            d = Decimal(s)
            self.assertRaises(ValueError, float, d)

    eleza test_eval_round_trip(self):
        Decimal = self.decimal.Decimal

        #ukijumuisha zero
        d = Decimal( (0, (0,), 0) )
        self.assertEqual(d, eval(repr(d)))

        #int
        d = Decimal( (1, (4, 5), 0) )
        self.assertEqual(d, eval(repr(d)))

        #float
        d = Decimal( (0, (4, 5, 3, 4), -2) )
        self.assertEqual(d, eval(repr(d)))

        #weird
        d = Decimal( (1, (4, 3, 4, 9, 1, 3, 5, 3, 4), -25) )
        self.assertEqual(d, eval(repr(d)))

    eleza test_as_tuple(self):
        Decimal = self.decimal.Decimal

        #ukijumuisha zero
        d = Decimal(0)
        self.assertEqual(d.as_tuple(), (0, (0,), 0) )

        #int
        d = Decimal(-45)
        self.assertEqual(d.as_tuple(), (1, (4, 5), 0) )

        #complicated string
        d = Decimal("-4.34913534E-17")
        self.assertEqual(d.as_tuple(), (1, (4, 3, 4, 9, 1, 3, 5, 3, 4), -25) )

        # The '0' coefficient ni implementation specific to decimal.py.
        # It has no meaning kwenye the C-version na ni ignored there.
        d = Decimal("Infinity")
        self.assertEqual(d.as_tuple(), (0, (0,), 'F') )

        #leading zeros kwenye coefficient should be stripped
        d = Decimal( (0, (0, 0, 4, 0, 5, 3, 4), -2) )
        self.assertEqual(d.as_tuple(), (0, (4, 0, 5, 3, 4), -2) )
        d = Decimal( (1, (0, 0, 0), 37) )
        self.assertEqual(d.as_tuple(), (1, (0,), 37))
        d = Decimal( (1, (), 37) )
        self.assertEqual(d.as_tuple(), (1, (0,), 37))

        #leading zeros kwenye NaN diagnostic info should be stripped
        d = Decimal( (0, (0, 0, 4, 0, 5, 3, 4), 'n') )
        self.assertEqual(d.as_tuple(), (0, (4, 0, 5, 3, 4), 'n') )
        d = Decimal( (1, (0, 0, 0), 'N') )
        self.assertEqual(d.as_tuple(), (1, (), 'N') )
        d = Decimal( (1, (), 'n') )
        self.assertEqual(d.as_tuple(), (1, (), 'n') )

        # For infinities, decimal.py has always silently accepted any
        # coefficient tuple.
        d = Decimal( (0, (0,), 'F') )
        self.assertEqual(d.as_tuple(), (0, (0,), 'F'))
        d = Decimal( (0, (4, 5, 3, 4), 'F') )
        self.assertEqual(d.as_tuple(), (0, (0,), 'F'))
        d = Decimal( (1, (0, 2, 7, 1), 'F') )
        self.assertEqual(d.as_tuple(), (1, (0,), 'F'))

    eleza test_as_integer_ratio(self):
        Decimal = self.decimal.Decimal

        # exceptional cases
        self.assertRaises(OverflowError,
                          Decimal.as_integer_ratio, Decimal('inf'))
        self.assertRaises(OverflowError,
                          Decimal.as_integer_ratio, Decimal('-inf'))
        self.assertRaises(ValueError,
                          Decimal.as_integer_ratio, Decimal('-nan'))
        self.assertRaises(ValueError,
                          Decimal.as_integer_ratio, Decimal('snan123'))

        kila exp kwenye range(-4, 2):
            kila coeff kwenye range(1000):
                kila sign kwenye '+', '-':
                    d = Decimal('%s%dE%d' % (sign, coeff, exp))
                    pq = d.as_integer_ratio()
                    p, q = pq

                    # check rudisha type
                    self.assertIsInstance(pq, tuple)
                    self.assertIsInstance(p, int)
                    self.assertIsInstance(q, int)

                    # check normalization:  q should be positive;
                    # p should be relatively prime to q.
                    self.assertGreater(q, 0)
                    self.assertEqual(math.gcd(p, q), 1)

                    # check that p/q actually gives the correct value
                    self.assertEqual(Decimal(p) / Decimal(q), d)

    eleza test_subclassing(self):
        # Different behaviours when subclassing Decimal
        Decimal = self.decimal.Decimal

        kundi MyDecimal(Decimal):
            y = Tupu

        d1 = MyDecimal(1)
        d2 = MyDecimal(2)
        d = d1 + d2
        self.assertIs(type(d), Decimal)

        d = d1.max(d2)
        self.assertIs(type(d), Decimal)

        d = copy.copy(d1)
        self.assertIs(type(d), MyDecimal)
        self.assertEqual(d, d1)

        d = copy.deepcopy(d1)
        self.assertIs(type(d), MyDecimal)
        self.assertEqual(d, d1)

        # Decimal(Decimal)
        d = Decimal('1.0')
        x = Decimal(d)
        self.assertIs(type(x), Decimal)
        self.assertEqual(x, d)

        # MyDecimal(Decimal)
        m = MyDecimal(d)
        self.assertIs(type(m), MyDecimal)
        self.assertEqual(m, d)
        self.assertIs(m.y, Tupu)

        # Decimal(MyDecimal)
        x = Decimal(m)
        self.assertIs(type(x), Decimal)
        self.assertEqual(x, d)

        # MyDecimal(MyDecimal)
        m.y = 9
        x = MyDecimal(m)
        self.assertIs(type(x), MyDecimal)
        self.assertEqual(x, d)
        self.assertIs(x.y, Tupu)

    eleza test_implicit_context(self):
        Decimal = self.decimal.Decimal
        getcontext = self.decimal.getcontext

        # Check results when context given implicitly.  (Issue 2478)
        c = getcontext()
        self.assertEqual(str(Decimal(0).sqrt()),
                         str(c.sqrt(Decimal(0))))

    eleza test_none_args(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context
        localcontext = self.decimal.localcontext
        InvalidOperation = self.decimal.InvalidOperation
        DivisionByZero = self.decimal.DivisionByZero
        Overflow = self.decimal.Overflow
        Underflow = self.decimal.Underflow
        Subnormal = self.decimal.Subnormal
        Inexact = self.decimal.Inexact
        Rounded = self.decimal.Rounded
        Clamped = self.decimal.Clamped

        ukijumuisha localcontext(Context()) kama c:
            c.prec = 7
            c.Emax = 999
            c.Emin = -999

            x = Decimal("111")
            y = Decimal("1e9999")
            z = Decimal("1e-9999")

            ##### Unary functions
            c.clear_flags()
            self.assertEqual(str(x.exp(context=Tupu)), '1.609487E+48')
            self.assertKweli(c.flags[Inexact])
            self.assertKweli(c.flags[Rounded])
            c.clear_flags()
            self.assertRaises(Overflow, y.exp, context=Tupu)
            self.assertKweli(c.flags[Overflow])

            self.assertIs(z.is_normal(context=Tupu), Uongo)
            self.assertIs(z.is_subnormal(context=Tupu), Kweli)

            c.clear_flags()
            self.assertEqual(str(x.ln(context=Tupu)), '4.709530')
            self.assertKweli(c.flags[Inexact])
            self.assertKweli(c.flags[Rounded])
            c.clear_flags()
            self.assertRaises(InvalidOperation, Decimal(-1).ln, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            self.assertEqual(str(x.log10(context=Tupu)), '2.045323')
            self.assertKweli(c.flags[Inexact])
            self.assertKweli(c.flags[Rounded])
            c.clear_flags()
            self.assertRaises(InvalidOperation, Decimal(-1).log10, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            self.assertEqual(str(x.logb(context=Tupu)), '2')
            self.assertRaises(DivisionByZero, Decimal(0).logb, context=Tupu)
            self.assertKweli(c.flags[DivisionByZero])

            c.clear_flags()
            self.assertEqual(str(x.logical_invert(context=Tupu)), '1111000')
            self.assertRaises(InvalidOperation, y.logical_invert, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            self.assertEqual(str(y.next_minus(context=Tupu)), '9.999999E+999')
            self.assertRaises(InvalidOperation, Decimal('sNaN').next_minus, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            self.assertEqual(str(y.next_plus(context=Tupu)), 'Infinity')
            self.assertRaises(InvalidOperation, Decimal('sNaN').next_plus, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            self.assertEqual(str(z.normalize(context=Tupu)), '0')
            self.assertRaises(Overflow, y.normalize, context=Tupu)
            self.assertKweli(c.flags[Overflow])

            self.assertEqual(str(z.number_class(context=Tupu)), '+Subnormal')

            c.clear_flags()
            self.assertEqual(str(z.sqrt(context=Tupu)), '0E-1005')
            self.assertKweli(c.flags[Clamped])
            self.assertKweli(c.flags[Inexact])
            self.assertKweli(c.flags[Rounded])
            self.assertKweli(c.flags[Subnormal])
            self.assertKweli(c.flags[Underflow])
            c.clear_flags()
            self.assertRaises(Overflow, y.sqrt, context=Tupu)
            self.assertKweli(c.flags[Overflow])

            c.capitals = 0
            self.assertEqual(str(z.to_eng_string(context=Tupu)), '1e-9999')
            c.capitals = 1


            ##### Binary functions
            c.clear_flags()
            ans = str(x.compare(Decimal('Nan891287828'), context=Tupu))
            self.assertEqual(ans, 'NaN1287828')
            self.assertRaises(InvalidOperation, x.compare, Decimal('sNaN'), context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.compare_signal(8224, context=Tupu))
            self.assertEqual(ans, '-1')
            self.assertRaises(InvalidOperation, x.compare_signal, Decimal('NaN'), context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.logical_and(101, context=Tupu))
            self.assertEqual(ans, '101')
            self.assertRaises(InvalidOperation, x.logical_and, 123, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.logical_or(101, context=Tupu))
            self.assertEqual(ans, '111')
            self.assertRaises(InvalidOperation, x.logical_or, 123, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.logical_xor(101, context=Tupu))
            self.assertEqual(ans, '10')
            self.assertRaises(InvalidOperation, x.logical_xor, 123, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.max(101, context=Tupu))
            self.assertEqual(ans, '111')
            self.assertRaises(InvalidOperation, x.max, Decimal('sNaN'), context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.max_mag(101, context=Tupu))
            self.assertEqual(ans, '111')
            self.assertRaises(InvalidOperation, x.max_mag, Decimal('sNaN'), context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.min(101, context=Tupu))
            self.assertEqual(ans, '101')
            self.assertRaises(InvalidOperation, x.min, Decimal('sNaN'), context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.min_mag(101, context=Tupu))
            self.assertEqual(ans, '101')
            self.assertRaises(InvalidOperation, x.min_mag, Decimal('sNaN'), context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.remainder_near(101, context=Tupu))
            self.assertEqual(ans, '10')
            self.assertRaises(InvalidOperation, y.remainder_near, 101, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.rotate(2, context=Tupu))
            self.assertEqual(ans, '11100')
            self.assertRaises(InvalidOperation, x.rotate, 101, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.scaleb(7, context=Tupu))
            self.assertEqual(ans, '1.11E+9')
            self.assertRaises(InvalidOperation, x.scaleb, 10000, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            ans = str(x.shift(2, context=Tupu))
            self.assertEqual(ans, '11100')
            self.assertRaises(InvalidOperation, x.shift, 10000, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])


            ##### Ternary functions
            c.clear_flags()
            ans = str(x.fma(2, 3, context=Tupu))
            self.assertEqual(ans, '225')
            self.assertRaises(Overflow, x.fma, Decimal('1e9999'), 3, context=Tupu)
            self.assertKweli(c.flags[Overflow])


            ##### Special cases
            c.rounding = ROUND_HALF_EVEN
            ans = str(Decimal('1.5').to_integral(rounding=Tupu, context=Tupu))
            self.assertEqual(ans, '2')
            c.rounding = ROUND_DOWN
            ans = str(Decimal('1.5').to_integral(rounding=Tupu, context=Tupu))
            self.assertEqual(ans, '1')
            ans = str(Decimal('1.5').to_integral(rounding=ROUND_UP, context=Tupu))
            self.assertEqual(ans, '2')
            c.clear_flags()
            self.assertRaises(InvalidOperation, Decimal('sNaN').to_integral, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.rounding = ROUND_HALF_EVEN
            ans = str(Decimal('1.5').to_integral_value(rounding=Tupu, context=Tupu))
            self.assertEqual(ans, '2')
            c.rounding = ROUND_DOWN
            ans = str(Decimal('1.5').to_integral_value(rounding=Tupu, context=Tupu))
            self.assertEqual(ans, '1')
            ans = str(Decimal('1.5').to_integral_value(rounding=ROUND_UP, context=Tupu))
            self.assertEqual(ans, '2')
            c.clear_flags()
            self.assertRaises(InvalidOperation, Decimal('sNaN').to_integral_value, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.rounding = ROUND_HALF_EVEN
            ans = str(Decimal('1.5').to_integral_exact(rounding=Tupu, context=Tupu))
            self.assertEqual(ans, '2')
            c.rounding = ROUND_DOWN
            ans = str(Decimal('1.5').to_integral_exact(rounding=Tupu, context=Tupu))
            self.assertEqual(ans, '1')
            ans = str(Decimal('1.5').to_integral_exact(rounding=ROUND_UP, context=Tupu))
            self.assertEqual(ans, '2')
            c.clear_flags()
            self.assertRaises(InvalidOperation, Decimal('sNaN').to_integral_exact, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

            c.rounding = ROUND_UP
            ans = str(Decimal('1.50001').quantize(exp=Decimal('1e-3'), rounding=Tupu, context=Tupu))
            self.assertEqual(ans, '1.501')
            c.rounding = ROUND_DOWN
            ans = str(Decimal('1.50001').quantize(exp=Decimal('1e-3'), rounding=Tupu, context=Tupu))
            self.assertEqual(ans, '1.500')
            ans = str(Decimal('1.50001').quantize(exp=Decimal('1e-3'), rounding=ROUND_UP, context=Tupu))
            self.assertEqual(ans, '1.501')
            c.clear_flags()
            self.assertRaises(InvalidOperation, y.quantize, Decimal('1e-10'), rounding=ROUND_UP, context=Tupu)
            self.assertKweli(c.flags[InvalidOperation])

        ukijumuisha localcontext(Context()) kama context:
            context.prec = 7
            context.Emax = 999
            context.Emin = -999
            ukijumuisha localcontext(ctx=Tupu) kama c:
                self.assertEqual(c.prec, 7)
                self.assertEqual(c.Emax, 999)
                self.assertEqual(c.Emin, -999)

    eleza test_conversions_from_int(self):
        # Check that methods taking a second Decimal argument will
        # always accept an integer kwenye place of a Decimal.
        Decimal = self.decimal.Decimal

        self.assertEqual(Decimal(4).compare(3),
                         Decimal(4).compare(Decimal(3)))
        self.assertEqual(Decimal(4).compare_signal(3),
                         Decimal(4).compare_signal(Decimal(3)))
        self.assertEqual(Decimal(4).compare_total(3),
                         Decimal(4).compare_total(Decimal(3)))
        self.assertEqual(Decimal(4).compare_total_mag(3),
                         Decimal(4).compare_total_mag(Decimal(3)))
        self.assertEqual(Decimal(10101).logical_and(1001),
                         Decimal(10101).logical_and(Decimal(1001)))
        self.assertEqual(Decimal(10101).logical_or(1001),
                         Decimal(10101).logical_or(Decimal(1001)))
        self.assertEqual(Decimal(10101).logical_xor(1001),
                         Decimal(10101).logical_xor(Decimal(1001)))
        self.assertEqual(Decimal(567).max(123),
                         Decimal(567).max(Decimal(123)))
        self.assertEqual(Decimal(567).max_mag(123),
                         Decimal(567).max_mag(Decimal(123)))
        self.assertEqual(Decimal(567).min(123),
                         Decimal(567).min(Decimal(123)))
        self.assertEqual(Decimal(567).min_mag(123),
                         Decimal(567).min_mag(Decimal(123)))
        self.assertEqual(Decimal(567).next_toward(123),
                         Decimal(567).next_toward(Decimal(123)))
        self.assertEqual(Decimal(1234).quantize(100),
                         Decimal(1234).quantize(Decimal(100)))
        self.assertEqual(Decimal(768).remainder_near(1234),
                         Decimal(768).remainder_near(Decimal(1234)))
        self.assertEqual(Decimal(123).rotate(1),
                         Decimal(123).rotate(Decimal(1)))
        self.assertEqual(Decimal(1234).same_quantum(1000),
                         Decimal(1234).same_quantum(Decimal(1000)))
        self.assertEqual(Decimal('9.123').scaleb(-100),
                         Decimal('9.123').scaleb(Decimal(-100)))
        self.assertEqual(Decimal(456).shift(-1),
                         Decimal(456).shift(Decimal(-1)))

        self.assertEqual(Decimal(-12).fma(Decimal(45), 67),
                         Decimal(-12).fma(Decimal(45), Decimal(67)))
        self.assertEqual(Decimal(-12).fma(45, 67),
                         Decimal(-12).fma(Decimal(45), Decimal(67)))
        self.assertEqual(Decimal(-12).fma(45, Decimal(67)),
                         Decimal(-12).fma(Decimal(45), Decimal(67)))

kundi CUsabilityTest(UsabilityTest):
    decimal = C
kundi PyUsabilityTest(UsabilityTest):
    decimal = P

kundi PythonAPItests(unittest.TestCase):

    eleza test_abc(self):
        Decimal = self.decimal.Decimal

        self.assertKweli(issubclass(Decimal, numbers.Number))
        self.assertUongo(issubclass(Decimal, numbers.Real))
        self.assertIsInstance(Decimal(0), numbers.Number)
        self.assertNotIsInstance(Decimal(0), numbers.Real)

    eleza test_pickle(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            Decimal = self.decimal.Decimal

            savedecimal = sys.modules['decimal']

            # Round trip
            sys.modules['decimal'] = self.decimal
            d = Decimal('-3.141590000')
            p = pickle.dumps(d, proto)
            e = pickle.loads(p)
            self.assertEqual(d, e)

            ikiwa C:
                # Test interchangeability
                x = C.Decimal('-3.123e81723')
                y = P.Decimal('-3.123e81723')

                sys.modules['decimal'] = C
                sx = pickle.dumps(x, proto)
                sys.modules['decimal'] = P
                r = pickle.loads(sx)
                self.assertIsInstance(r, P.Decimal)
                self.assertEqual(r, y)

                sys.modules['decimal'] = P
                sy = pickle.dumps(y, proto)
                sys.modules['decimal'] = C
                r = pickle.loads(sy)
                self.assertIsInstance(r, C.Decimal)
                self.assertEqual(r, x)

                x = C.Decimal('-3.123e81723').as_tuple()
                y = P.Decimal('-3.123e81723').as_tuple()

                sys.modules['decimal'] = C
                sx = pickle.dumps(x, proto)
                sys.modules['decimal'] = P
                r = pickle.loads(sx)
                self.assertIsInstance(r, P.DecimalTuple)
                self.assertEqual(r, y)

                sys.modules['decimal'] = P
                sy = pickle.dumps(y, proto)
                sys.modules['decimal'] = C
                r = pickle.loads(sy)
                self.assertIsInstance(r, C.DecimalTuple)
                self.assertEqual(r, x)

            sys.modules['decimal'] = savedecimal

    eleza test_int(self):
        Decimal = self.decimal.Decimal

        kila x kwenye range(-250, 250):
            s = '%0.2f' % (x / 100.0)
            # should work the same kama kila floats
            self.assertEqual(int(Decimal(s)), int(float(s)))
            # should work the same kama to_integral kwenye the ROUND_DOWN mode
            d = Decimal(s)
            r = d.to_integral(ROUND_DOWN)
            self.assertEqual(Decimal(int(d)), r)

        self.assertRaises(ValueError, int, Decimal('-nan'))
        self.assertRaises(ValueError, int, Decimal('snan'))
        self.assertRaises(OverflowError, int, Decimal('inf'))
        self.assertRaises(OverflowError, int, Decimal('-inf'))

    eleza test_trunc(self):
        Decimal = self.decimal.Decimal

        kila x kwenye range(-250, 250):
            s = '%0.2f' % (x / 100.0)
            # should work the same kama kila floats
            self.assertEqual(int(Decimal(s)), int(float(s)))
            # should work the same kama to_integral kwenye the ROUND_DOWN mode
            d = Decimal(s)
            r = d.to_integral(ROUND_DOWN)
            self.assertEqual(Decimal(math.trunc(d)), r)

    eleza test_from_float(self):

        Decimal = self.decimal.Decimal

        kundi MyDecimal(Decimal):
            eleza __init__(self, _):
                self.x = 'y'

        self.assertKweli(issubclass(MyDecimal, Decimal))

        r = MyDecimal.from_float(0.1)
        self.assertEqual(type(r), MyDecimal)
        self.assertEqual(str(r),
                '0.1000000000000000055511151231257827021181583404541015625')
        self.assertEqual(r.x, 'y')

        bigint = 12345678901234567890123456789
        self.assertEqual(MyDecimal.from_float(bigint), MyDecimal(bigint))
        self.assertKweli(MyDecimal.from_float(float('nan')).is_qnan())
        self.assertKweli(MyDecimal.from_float(float('inf')).is_infinite())
        self.assertKweli(MyDecimal.from_float(float('-inf')).is_infinite())
        self.assertEqual(str(MyDecimal.from_float(float('nan'))),
                         str(Decimal('NaN')))
        self.assertEqual(str(MyDecimal.from_float(float('inf'))),
                         str(Decimal('Infinity')))
        self.assertEqual(str(MyDecimal.from_float(float('-inf'))),
                         str(Decimal('-Infinity')))
        self.assertRaises(TypeError, MyDecimal.from_float, 'abc')
        kila i kwenye range(200):
            x = random.expovariate(0.01) * (random.random() * 2.0 - 1.0)
            self.assertEqual(x, float(MyDecimal.from_float(x))) # roundtrip

    eleza test_create_decimal_from_float(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context
        Inexact = self.decimal.Inexact

        context = Context(prec=5, rounding=ROUND_DOWN)
        self.assertEqual(
            context.create_decimal_from_float(math.pi),
            Decimal('3.1415')
        )
        context = Context(prec=5, rounding=ROUND_UP)
        self.assertEqual(
            context.create_decimal_from_float(math.pi),
            Decimal('3.1416')
        )
        context = Context(prec=5, traps=[Inexact])
        self.assertRaises(
            Inexact,
            context.create_decimal_from_float,
            math.pi
        )
        self.assertEqual(repr(context.create_decimal_from_float(-0.0)),
                         "Decimal('-0')")
        self.assertEqual(repr(context.create_decimal_from_float(1.0)),
                         "Decimal('1')")
        self.assertEqual(repr(context.create_decimal_from_float(10)),
                         "Decimal('10')")

    eleza test_quantize(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context
        InvalidOperation = self.decimal.InvalidOperation

        c = Context(Emax=99999, Emin=-99999)
        self.assertEqual(
            Decimal('7.335').quantize(Decimal('.01')),
            Decimal('7.34')
        )
        self.assertEqual(
            Decimal('7.335').quantize(Decimal('.01'), rounding=ROUND_DOWN),
            Decimal('7.33')
        )
        self.assertRaises(
            InvalidOperation,
            Decimal("10e99999").quantize, Decimal('1e100000'), context=c
        )

        c = Context()
        d = Decimal("0.871831e800")
        x = d.quantize(context=c, exp=Decimal("1e797"), rounding=ROUND_DOWN)
        self.assertEqual(x, Decimal('8.71E+799'))

    eleza test_complex(self):
        Decimal = self.decimal.Decimal

        x = Decimal("9.8182731e181273")
        self.assertEqual(x.real, x)
        self.assertEqual(x.imag, 0)
        self.assertEqual(x.conjugate(), x)

        x = Decimal("1")
        self.assertEqual(complex(x), complex(float(1)))

        self.assertRaises(AttributeError, setattr, x, 'real', 100)
        self.assertRaises(AttributeError, setattr, x, 'imag', 100)
        self.assertRaises(AttributeError, setattr, x, 'conjugate', 100)
        self.assertRaises(AttributeError, setattr, x, '__complex__', 100)

    eleza test_named_parameters(self):
        D = self.decimal.Decimal
        Context = self.decimal.Context
        localcontext = self.decimal.localcontext
        InvalidOperation = self.decimal.InvalidOperation
        Overflow = self.decimal.Overflow

        xc = Context()
        xc.prec = 1
        xc.Emax = 1
        xc.Emin = -1

        ukijumuisha localcontext() kama c:
            c.clear_flags()

            self.assertEqual(D(9, xc), 9)
            self.assertEqual(D(9, context=xc), 9)
            self.assertEqual(D(context=xc, value=9), 9)
            self.assertEqual(D(context=xc), 0)
            xc.clear_flags()
            self.assertRaises(InvalidOperation, D, "xyz", context=xc)
            self.assertKweli(xc.flags[InvalidOperation])
            self.assertUongo(c.flags[InvalidOperation])

            xc.clear_flags()
            self.assertEqual(D(2).exp(context=xc), 7)
            self.assertRaises(Overflow, D(8).exp, context=xc)
            self.assertKweli(xc.flags[Overflow])
            self.assertUongo(c.flags[Overflow])

            xc.clear_flags()
            self.assertEqual(D(2).ln(context=xc), D('0.7'))
            self.assertRaises(InvalidOperation, D(-1).ln, context=xc)
            self.assertKweli(xc.flags[InvalidOperation])
            self.assertUongo(c.flags[InvalidOperation])

            self.assertEqual(D(0).log10(context=xc), D('-inf'))
            self.assertEqual(D(-1).next_minus(context=xc), -2)
            self.assertEqual(D(-1).next_plus(context=xc), D('-0.9'))
            self.assertEqual(D("9.73").normalize(context=xc), D('1E+1'))
            self.assertEqual(D("9999").to_integral(context=xc), 9999)
            self.assertEqual(D("-2000").to_integral_exact(context=xc), -2000)
            self.assertEqual(D("123").to_integral_value(context=xc), 123)
            self.assertEqual(D("0.0625").sqrt(context=xc), D('0.2'))

            self.assertEqual(D("0.0625").compare(context=xc, other=3), -1)
            xc.clear_flags()
            self.assertRaises(InvalidOperation,
                              D("0").compare_signal, D('nan'), context=xc)
            self.assertKweli(xc.flags[InvalidOperation])
            self.assertUongo(c.flags[InvalidOperation])
            self.assertEqual(D("0.01").max(D('0.0101'), context=xc), D('0.0'))
            self.assertEqual(D("0.01").max(D('0.0101'), context=xc), D('0.0'))
            self.assertEqual(D("0.2").max_mag(D('-0.3'), context=xc),
                             D('-0.3'))
            self.assertEqual(D("0.02").min(D('-0.03'), context=xc), D('-0.0'))
            self.assertEqual(D("0.02").min_mag(D('-0.03'), context=xc),
                             D('0.0'))
            self.assertEqual(D("0.2").next_toward(D('-1'), context=xc), D('0.1'))
            xc.clear_flags()
            self.assertRaises(InvalidOperation,
                              D("0.2").quantize, D('1e10'), context=xc)
            self.assertKweli(xc.flags[InvalidOperation])
            self.assertUongo(c.flags[InvalidOperation])
            self.assertEqual(D("9.99").remainder_near(D('1.5'), context=xc),
                             D('-0.5'))

            self.assertEqual(D("9.9").fma(third=D('0.9'), context=xc, other=7),
                             D('7E+1'))

            self.assertRaises(TypeError, D(1).is_canonical, context=xc)
            self.assertRaises(TypeError, D(1).is_finite, context=xc)
            self.assertRaises(TypeError, D(1).is_infinite, context=xc)
            self.assertRaises(TypeError, D(1).is_nan, context=xc)
            self.assertRaises(TypeError, D(1).is_qnan, context=xc)
            self.assertRaises(TypeError, D(1).is_snan, context=xc)
            self.assertRaises(TypeError, D(1).is_signed, context=xc)
            self.assertRaises(TypeError, D(1).is_zero, context=xc)

            self.assertUongo(D("0.01").is_normal(context=xc))
            self.assertKweli(D("0.01").is_subnormal(context=xc))

            self.assertRaises(TypeError, D(1).adjusted, context=xc)
            self.assertRaises(TypeError, D(1).conjugate, context=xc)
            self.assertRaises(TypeError, D(1).radix, context=xc)

            self.assertEqual(D(-111).logb(context=xc), 2)
            self.assertEqual(D(0).logical_invert(context=xc), 1)
            self.assertEqual(D('0.01').number_class(context=xc), '+Subnormal')
            self.assertEqual(D('0.21').to_eng_string(context=xc), '0.21')

            self.assertEqual(D('11').logical_and(D('10'), context=xc), 0)
            self.assertEqual(D('11').logical_or(D('10'), context=xc), 1)
            self.assertEqual(D('01').logical_xor(D('10'), context=xc), 1)
            self.assertEqual(D('23').rotate(1, context=xc), 3)
            self.assertEqual(D('23').rotate(1, context=xc), 3)
            xc.clear_flags()
            self.assertRaises(Overflow,
                              D('23').scaleb, 1, context=xc)
            self.assertKweli(xc.flags[Overflow])
            self.assertUongo(c.flags[Overflow])
            self.assertEqual(D('23').shift(-1, context=xc), 0)

            self.assertRaises(TypeError, D.from_float, 1.1, context=xc)
            self.assertRaises(TypeError, D(0).as_tuple, context=xc)

            self.assertEqual(D(1).canonical(), 1)
            self.assertRaises(TypeError, D("-1").copy_abs, context=xc)
            self.assertRaises(TypeError, D("-1").copy_negate, context=xc)
            self.assertRaises(TypeError, D(1).canonical, context="x")
            self.assertRaises(TypeError, D(1).canonical, xyz="x")

    eleza test_exception_hierarchy(self):

        decimal = self.decimal
        DecimalException = decimal.DecimalException
        InvalidOperation = decimal.InvalidOperation
        FloatOperation = decimal.FloatOperation
        DivisionByZero = decimal.DivisionByZero
        Overflow = decimal.Overflow
        Underflow = decimal.Underflow
        Subnormal = decimal.Subnormal
        Inexact = decimal.Inexact
        Rounded = decimal.Rounded
        Clamped = decimal.Clamped

        self.assertKweli(issubclass(DecimalException, ArithmeticError))

        self.assertKweli(issubclass(InvalidOperation, DecimalException))
        self.assertKweli(issubclass(FloatOperation, DecimalException))
        self.assertKweli(issubclass(FloatOperation, TypeError))
        self.assertKweli(issubclass(DivisionByZero, DecimalException))
        self.assertKweli(issubclass(DivisionByZero, ZeroDivisionError))
        self.assertKweli(issubclass(Overflow, Rounded))
        self.assertKweli(issubclass(Overflow, Inexact))
        self.assertKweli(issubclass(Overflow, DecimalException))
        self.assertKweli(issubclass(Underflow, Inexact))
        self.assertKweli(issubclass(Underflow, Rounded))
        self.assertKweli(issubclass(Underflow, Subnormal))
        self.assertKweli(issubclass(Underflow, DecimalException))

        self.assertKweli(issubclass(Subnormal, DecimalException))
        self.assertKweli(issubclass(Inexact, DecimalException))
        self.assertKweli(issubclass(Rounded, DecimalException))
        self.assertKweli(issubclass(Clamped, DecimalException))

        self.assertKweli(issubclass(decimal.ConversionSyntax, InvalidOperation))
        self.assertKweli(issubclass(decimal.DivisionImpossible, InvalidOperation))
        self.assertKweli(issubclass(decimal.DivisionUndefined, InvalidOperation))
        self.assertKweli(issubclass(decimal.DivisionUndefined, ZeroDivisionError))
        self.assertKweli(issubclass(decimal.InvalidContext, InvalidOperation))

kundi CPythonAPItests(PythonAPItests):
    decimal = C
kundi PyPythonAPItests(PythonAPItests):
    decimal = P

kundi ContextAPItests(unittest.TestCase):

    eleza test_none_args(self):
        Context = self.decimal.Context
        InvalidOperation = self.decimal.InvalidOperation
        DivisionByZero = self.decimal.DivisionByZero
        Overflow = self.decimal.Overflow

        c1 = Context()
        c2 = Context(prec=Tupu, rounding=Tupu, Emax=Tupu, Emin=Tupu,
                     capitals=Tupu, clamp=Tupu, flags=Tupu, traps=Tupu)
        kila c kwenye [c1, c2]:
            self.assertEqual(c.prec, 28)
            self.assertEqual(c.rounding, ROUND_HALF_EVEN)
            self.assertEqual(c.Emax, 999999)
            self.assertEqual(c.Emin, -999999)
            self.assertEqual(c.capitals, 1)
            self.assertEqual(c.clamp, 0)
            assert_signals(self, c, 'flags', [])
            assert_signals(self, c, 'traps', [InvalidOperation, DivisionByZero,
                                              Overflow])

    @cpython_only
    eleza test_from_legacy_strings(self):
        agiza _testcapi
        c = self.decimal.Context()

        kila rnd kwenye RoundingModes:
            c.rounding = _testcapi.unicode_legacy_string(rnd)
            self.assertEqual(c.rounding, rnd)

        s = _testcapi.unicode_legacy_string('')
        self.assertRaises(TypeError, setattr, c, 'rounding', s)

        s = _testcapi.unicode_legacy_string('ROUND_\x00UP')
        self.assertRaises(TypeError, setattr, c, 'rounding', s)

    eleza test_pickle(self):

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            Context = self.decimal.Context

            savedecimal = sys.modules['decimal']

            # Round trip
            sys.modules['decimal'] = self.decimal
            c = Context()
            e = pickle.loads(pickle.dumps(c, proto))

            self.assertEqual(c.prec, e.prec)
            self.assertEqual(c.Emin, e.Emin)
            self.assertEqual(c.Emax, e.Emax)
            self.assertEqual(c.rounding, e.rounding)
            self.assertEqual(c.capitals, e.capitals)
            self.assertEqual(c.clamp, e.clamp)
            self.assertEqual(c.flags, e.flags)
            self.assertEqual(c.traps, e.traps)

            # Test interchangeability
            combinations = [(C, P), (P, C)] ikiwa C isipokua [(P, P)]
            kila dumper, loader kwenye combinations:
                kila ri, _ kwenye enumerate(RoundingModes):
                    kila fi, _ kwenye enumerate(OrderedSignals[dumper]):
                        kila ti, _ kwenye enumerate(OrderedSignals[dumper]):

                            prec = random.randrange(1, 100)
                            emin = random.randrange(-100, 0)
                            emax = random.randrange(1, 100)
                            caps = random.randrange(2)
                            clamp = random.randrange(2)

                            # One module dumps
                            sys.modules['decimal'] = dumper
                            c = dumper.Context(
                                  prec=prec, Emin=emin, Emax=emax,
                                  rounding=RoundingModes[ri],
                                  capitals=caps, clamp=clamp,
                                  flags=OrderedSignals[dumper][:fi],
                                  traps=OrderedSignals[dumper][:ti]
                            )
                            s = pickle.dumps(c, proto)

                            # The other module loads
                            sys.modules['decimal'] = loader
                            d = pickle.loads(s)
                            self.assertIsInstance(d, loader.Context)

                            self.assertEqual(d.prec, prec)
                            self.assertEqual(d.Emin, emin)
                            self.assertEqual(d.Emax, emax)
                            self.assertEqual(d.rounding, RoundingModes[ri])
                            self.assertEqual(d.capitals, caps)
                            self.assertEqual(d.clamp, clamp)
                            assert_signals(self, d, 'flags', OrderedSignals[loader][:fi])
                            assert_signals(self, d, 'traps', OrderedSignals[loader][:ti])

            sys.modules['decimal'] = savedecimal

    eleza test_equality_with_other_types(self):
        Decimal = self.decimal.Decimal

        self.assertIn(Decimal(10), ['a', 1.0, Decimal(10), (1,2), {}])
        self.assertNotIn(Decimal(10), ['a', 1.0, (1,2), {}])

    eleza test_copy(self):
        # All copies should be deep
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.copy()
        self.assertNotEqual(id(c), id(d))
        self.assertNotEqual(id(c.flags), id(d.flags))
        self.assertNotEqual(id(c.traps), id(d.traps))
        k1 = set(c.flags.keys())
        k2 = set(d.flags.keys())
        self.assertEqual(k1, k2)
        self.assertEqual(c.flags, d.flags)

    eleza test__clamp(self):
        # In Python 3.2, the private attribute `_clamp` was made
        # public (issue 8540), ukijumuisha the old `_clamp` becoming a
        # property wrapping `clamp`.  For the duration of Python 3.2
        # only, the attribute should be gettable/settable via both
        # `clamp` na `_clamp`; kwenye Python 3.3, `_clamp` should be
        # removed.
        Context = self.decimal.Context
        c = Context()
        self.assertRaises(AttributeError, getattr, c, '_clamp')

    eleza test_abs(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.abs(Decimal(-1))
        self.assertEqual(c.abs(-1), d)
        self.assertRaises(TypeError, c.abs, '-1')

    eleza test_add(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.add(Decimal(1), Decimal(1))
        self.assertEqual(c.add(1, 1), d)
        self.assertEqual(c.add(Decimal(1), 1), d)
        self.assertEqual(c.add(1, Decimal(1)), d)
        self.assertRaises(TypeError, c.add, '1', 1)
        self.assertRaises(TypeError, c.add, 1, '1')

    eleza test_compare(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.compare(Decimal(1), Decimal(1))
        self.assertEqual(c.compare(1, 1), d)
        self.assertEqual(c.compare(Decimal(1), 1), d)
        self.assertEqual(c.compare(1, Decimal(1)), d)
        self.assertRaises(TypeError, c.compare, '1', 1)
        self.assertRaises(TypeError, c.compare, 1, '1')

    eleza test_compare_signal(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.compare_signal(Decimal(1), Decimal(1))
        self.assertEqual(c.compare_signal(1, 1), d)
        self.assertEqual(c.compare_signal(Decimal(1), 1), d)
        self.assertEqual(c.compare_signal(1, Decimal(1)), d)
        self.assertRaises(TypeError, c.compare_signal, '1', 1)
        self.assertRaises(TypeError, c.compare_signal, 1, '1')

    eleza test_compare_total(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.compare_total(Decimal(1), Decimal(1))
        self.assertEqual(c.compare_total(1, 1), d)
        self.assertEqual(c.compare_total(Decimal(1), 1), d)
        self.assertEqual(c.compare_total(1, Decimal(1)), d)
        self.assertRaises(TypeError, c.compare_total, '1', 1)
        self.assertRaises(TypeError, c.compare_total, 1, '1')

    eleza test_compare_total_mag(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.compare_total_mag(Decimal(1), Decimal(1))
        self.assertEqual(c.compare_total_mag(1, 1), d)
        self.assertEqual(c.compare_total_mag(Decimal(1), 1), d)
        self.assertEqual(c.compare_total_mag(1, Decimal(1)), d)
        self.assertRaises(TypeError, c.compare_total_mag, '1', 1)
        self.assertRaises(TypeError, c.compare_total_mag, 1, '1')

    eleza test_copy_abs(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.copy_abs(Decimal(-1))
        self.assertEqual(c.copy_abs(-1), d)
        self.assertRaises(TypeError, c.copy_abs, '-1')

    eleza test_copy_decimal(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.copy_decimal(Decimal(-1))
        self.assertEqual(c.copy_decimal(-1), d)
        self.assertRaises(TypeError, c.copy_decimal, '-1')

    eleza test_copy_negate(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.copy_negate(Decimal(-1))
        self.assertEqual(c.copy_negate(-1), d)
        self.assertRaises(TypeError, c.copy_negate, '-1')

    eleza test_copy_sign(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.copy_sign(Decimal(1), Decimal(-2))
        self.assertEqual(c.copy_sign(1, -2), d)
        self.assertEqual(c.copy_sign(Decimal(1), -2), d)
        self.assertEqual(c.copy_sign(1, Decimal(-2)), d)
        self.assertRaises(TypeError, c.copy_sign, '1', -2)
        self.assertRaises(TypeError, c.copy_sign, 1, '-2')

    eleza test_divide(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.divide(Decimal(1), Decimal(2))
        self.assertEqual(c.divide(1, 2), d)
        self.assertEqual(c.divide(Decimal(1), 2), d)
        self.assertEqual(c.divide(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.divide, '1', 2)
        self.assertRaises(TypeError, c.divide, 1, '2')

    eleza test_divide_int(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.divide_int(Decimal(1), Decimal(2))
        self.assertEqual(c.divide_int(1, 2), d)
        self.assertEqual(c.divide_int(Decimal(1), 2), d)
        self.assertEqual(c.divide_int(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.divide_int, '1', 2)
        self.assertRaises(TypeError, c.divide_int, 1, '2')

    eleza test_divmod(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.divmod(Decimal(1), Decimal(2))
        self.assertEqual(c.divmod(1, 2), d)
        self.assertEqual(c.divmod(Decimal(1), 2), d)
        self.assertEqual(c.divmod(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.divmod, '1', 2)
        self.assertRaises(TypeError, c.divmod, 1, '2')

    eleza test_exp(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.exp(Decimal(10))
        self.assertEqual(c.exp(10), d)
        self.assertRaises(TypeError, c.exp, '10')

    eleza test_fma(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.fma(Decimal(2), Decimal(3), Decimal(4))
        self.assertEqual(c.fma(2, 3, 4), d)
        self.assertEqual(c.fma(Decimal(2), 3, 4), d)
        self.assertEqual(c.fma(2, Decimal(3), 4), d)
        self.assertEqual(c.fma(2, 3, Decimal(4)), d)
        self.assertEqual(c.fma(Decimal(2), Decimal(3), 4), d)
        self.assertRaises(TypeError, c.fma, '2', 3, 4)
        self.assertRaises(TypeError, c.fma, 2, '3', 4)
        self.assertRaises(TypeError, c.fma, 2, 3, '4')

        # Issue 12079 kila Context.fma ...
        self.assertRaises(TypeError, c.fma,
                          Decimal('Infinity'), Decimal(0), "not a decimal")
        self.assertRaises(TypeError, c.fma,
                          Decimal(1), Decimal('snan'), 1.222)
        # ... na kila Decimal.fma.
        self.assertRaises(TypeError, Decimal('Infinity').fma,
                          Decimal(0), "not a decimal")
        self.assertRaises(TypeError, Decimal(1).fma,
                          Decimal('snan'), 1.222)

    eleza test_is_finite(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_finite(Decimal(10))
        self.assertEqual(c.is_finite(10), d)
        self.assertRaises(TypeError, c.is_finite, '10')

    eleza test_is_infinite(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_infinite(Decimal(10))
        self.assertEqual(c.is_infinite(10), d)
        self.assertRaises(TypeError, c.is_infinite, '10')

    eleza test_is_nan(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_nan(Decimal(10))
        self.assertEqual(c.is_nan(10), d)
        self.assertRaises(TypeError, c.is_nan, '10')

    eleza test_is_normal(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_normal(Decimal(10))
        self.assertEqual(c.is_normal(10), d)
        self.assertRaises(TypeError, c.is_normal, '10')

    eleza test_is_qnan(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_qnan(Decimal(10))
        self.assertEqual(c.is_qnan(10), d)
        self.assertRaises(TypeError, c.is_qnan, '10')

    eleza test_is_signed(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_signed(Decimal(10))
        self.assertEqual(c.is_signed(10), d)
        self.assertRaises(TypeError, c.is_signed, '10')

    eleza test_is_snan(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_snan(Decimal(10))
        self.assertEqual(c.is_snan(10), d)
        self.assertRaises(TypeError, c.is_snan, '10')

    eleza test_is_subnormal(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_subnormal(Decimal(10))
        self.assertEqual(c.is_subnormal(10), d)
        self.assertRaises(TypeError, c.is_subnormal, '10')

    eleza test_is_zero(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.is_zero(Decimal(10))
        self.assertEqual(c.is_zero(10), d)
        self.assertRaises(TypeError, c.is_zero, '10')

    eleza test_ln(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.ln(Decimal(10))
        self.assertEqual(c.ln(10), d)
        self.assertRaises(TypeError, c.ln, '10')

    eleza test_log10(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.log10(Decimal(10))
        self.assertEqual(c.log10(10), d)
        self.assertRaises(TypeError, c.log10, '10')

    eleza test_logb(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.logb(Decimal(10))
        self.assertEqual(c.logb(10), d)
        self.assertRaises(TypeError, c.logb, '10')

    eleza test_logical_and(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.logical_and(Decimal(1), Decimal(1))
        self.assertEqual(c.logical_and(1, 1), d)
        self.assertEqual(c.logical_and(Decimal(1), 1), d)
        self.assertEqual(c.logical_and(1, Decimal(1)), d)
        self.assertRaises(TypeError, c.logical_and, '1', 1)
        self.assertRaises(TypeError, c.logical_and, 1, '1')

    eleza test_logical_invert(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.logical_invert(Decimal(1000))
        self.assertEqual(c.logical_invert(1000), d)
        self.assertRaises(TypeError, c.logical_invert, '1000')

    eleza test_logical_or(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.logical_or(Decimal(1), Decimal(1))
        self.assertEqual(c.logical_or(1, 1), d)
        self.assertEqual(c.logical_or(Decimal(1), 1), d)
        self.assertEqual(c.logical_or(1, Decimal(1)), d)
        self.assertRaises(TypeError, c.logical_or, '1', 1)
        self.assertRaises(TypeError, c.logical_or, 1, '1')

    eleza test_logical_xor(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.logical_xor(Decimal(1), Decimal(1))
        self.assertEqual(c.logical_xor(1, 1), d)
        self.assertEqual(c.logical_xor(Decimal(1), 1), d)
        self.assertEqual(c.logical_xor(1, Decimal(1)), d)
        self.assertRaises(TypeError, c.logical_xor, '1', 1)
        self.assertRaises(TypeError, c.logical_xor, 1, '1')

    eleza test_max(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.max(Decimal(1), Decimal(2))
        self.assertEqual(c.max(1, 2), d)
        self.assertEqual(c.max(Decimal(1), 2), d)
        self.assertEqual(c.max(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.max, '1', 2)
        self.assertRaises(TypeError, c.max, 1, '2')

    eleza test_max_mag(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.max_mag(Decimal(1), Decimal(2))
        self.assertEqual(c.max_mag(1, 2), d)
        self.assertEqual(c.max_mag(Decimal(1), 2), d)
        self.assertEqual(c.max_mag(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.max_mag, '1', 2)
        self.assertRaises(TypeError, c.max_mag, 1, '2')

    eleza test_min(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.min(Decimal(1), Decimal(2))
        self.assertEqual(c.min(1, 2), d)
        self.assertEqual(c.min(Decimal(1), 2), d)
        self.assertEqual(c.min(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.min, '1', 2)
        self.assertRaises(TypeError, c.min, 1, '2')

    eleza test_min_mag(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.min_mag(Decimal(1), Decimal(2))
        self.assertEqual(c.min_mag(1, 2), d)
        self.assertEqual(c.min_mag(Decimal(1), 2), d)
        self.assertEqual(c.min_mag(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.min_mag, '1', 2)
        self.assertRaises(TypeError, c.min_mag, 1, '2')

    eleza test_minus(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.minus(Decimal(10))
        self.assertEqual(c.minus(10), d)
        self.assertRaises(TypeError, c.minus, '10')

    eleza test_multiply(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.multiply(Decimal(1), Decimal(2))
        self.assertEqual(c.multiply(1, 2), d)
        self.assertEqual(c.multiply(Decimal(1), 2), d)
        self.assertEqual(c.multiply(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.multiply, '1', 2)
        self.assertRaises(TypeError, c.multiply, 1, '2')

    eleza test_next_minus(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.next_minus(Decimal(10))
        self.assertEqual(c.next_minus(10), d)
        self.assertRaises(TypeError, c.next_minus, '10')

    eleza test_next_plus(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.next_plus(Decimal(10))
        self.assertEqual(c.next_plus(10), d)
        self.assertRaises(TypeError, c.next_plus, '10')

    eleza test_next_toward(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.next_toward(Decimal(1), Decimal(2))
        self.assertEqual(c.next_toward(1, 2), d)
        self.assertEqual(c.next_toward(Decimal(1), 2), d)
        self.assertEqual(c.next_toward(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.next_toward, '1', 2)
        self.assertRaises(TypeError, c.next_toward, 1, '2')

    eleza test_normalize(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.normalize(Decimal(10))
        self.assertEqual(c.normalize(10), d)
        self.assertRaises(TypeError, c.normalize, '10')

    eleza test_number_class(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        self.assertEqual(c.number_class(123), c.number_class(Decimal(123)))
        self.assertEqual(c.number_class(0), c.number_class(Decimal(0)))
        self.assertEqual(c.number_class(-45), c.number_class(Decimal(-45)))

    eleza test_plus(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.plus(Decimal(10))
        self.assertEqual(c.plus(10), d)
        self.assertRaises(TypeError, c.plus, '10')

    eleza test_power(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.power(Decimal(1), Decimal(4))
        self.assertEqual(c.power(1, 4), d)
        self.assertEqual(c.power(Decimal(1), 4), d)
        self.assertEqual(c.power(1, Decimal(4)), d)
        self.assertEqual(c.power(Decimal(1), Decimal(4)), d)
        self.assertRaises(TypeError, c.power, '1', 4)
        self.assertRaises(TypeError, c.power, 1, '4')
        self.assertEqual(c.power(modulo=5, b=8, a=2), 1)

    eleza test_quantize(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.quantize(Decimal(1), Decimal(2))
        self.assertEqual(c.quantize(1, 2), d)
        self.assertEqual(c.quantize(Decimal(1), 2), d)
        self.assertEqual(c.quantize(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.quantize, '1', 2)
        self.assertRaises(TypeError, c.quantize, 1, '2')

    eleza test_remainder(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.remainder(Decimal(1), Decimal(2))
        self.assertEqual(c.remainder(1, 2), d)
        self.assertEqual(c.remainder(Decimal(1), 2), d)
        self.assertEqual(c.remainder(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.remainder, '1', 2)
        self.assertRaises(TypeError, c.remainder, 1, '2')

    eleza test_remainder_near(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.remainder_near(Decimal(1), Decimal(2))
        self.assertEqual(c.remainder_near(1, 2), d)
        self.assertEqual(c.remainder_near(Decimal(1), 2), d)
        self.assertEqual(c.remainder_near(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.remainder_near, '1', 2)
        self.assertRaises(TypeError, c.remainder_near, 1, '2')

    eleza test_rotate(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.rotate(Decimal(1), Decimal(2))
        self.assertEqual(c.rotate(1, 2), d)
        self.assertEqual(c.rotate(Decimal(1), 2), d)
        self.assertEqual(c.rotate(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.rotate, '1', 2)
        self.assertRaises(TypeError, c.rotate, 1, '2')

    eleza test_sqrt(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.sqrt(Decimal(10))
        self.assertEqual(c.sqrt(10), d)
        self.assertRaises(TypeError, c.sqrt, '10')

    eleza test_same_quantum(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.same_quantum(Decimal(1), Decimal(2))
        self.assertEqual(c.same_quantum(1, 2), d)
        self.assertEqual(c.same_quantum(Decimal(1), 2), d)
        self.assertEqual(c.same_quantum(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.same_quantum, '1', 2)
        self.assertRaises(TypeError, c.same_quantum, 1, '2')

    eleza test_scaleb(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.scaleb(Decimal(1), Decimal(2))
        self.assertEqual(c.scaleb(1, 2), d)
        self.assertEqual(c.scaleb(Decimal(1), 2), d)
        self.assertEqual(c.scaleb(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.scaleb, '1', 2)
        self.assertRaises(TypeError, c.scaleb, 1, '2')

    eleza test_shift(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.shift(Decimal(1), Decimal(2))
        self.assertEqual(c.shift(1, 2), d)
        self.assertEqual(c.shift(Decimal(1), 2), d)
        self.assertEqual(c.shift(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.shift, '1', 2)
        self.assertRaises(TypeError, c.shift, 1, '2')

    eleza test_subtract(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.subtract(Decimal(1), Decimal(2))
        self.assertEqual(c.subtract(1, 2), d)
        self.assertEqual(c.subtract(Decimal(1), 2), d)
        self.assertEqual(c.subtract(1, Decimal(2)), d)
        self.assertRaises(TypeError, c.subtract, '1', 2)
        self.assertRaises(TypeError, c.subtract, 1, '2')

    eleza test_to_eng_string(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.to_eng_string(Decimal(10))
        self.assertEqual(c.to_eng_string(10), d)
        self.assertRaises(TypeError, c.to_eng_string, '10')

    eleza test_to_sci_string(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.to_sci_string(Decimal(10))
        self.assertEqual(c.to_sci_string(10), d)
        self.assertRaises(TypeError, c.to_sci_string, '10')

    eleza test_to_integral_exact(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.to_integral_exact(Decimal(10))
        self.assertEqual(c.to_integral_exact(10), d)
        self.assertRaises(TypeError, c.to_integral_exact, '10')

    eleza test_to_integral_value(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context

        c = Context()
        d = c.to_integral_value(Decimal(10))
        self.assertEqual(c.to_integral_value(10), d)
        self.assertRaises(TypeError, c.to_integral_value, '10')
        self.assertRaises(TypeError, c.to_integral_value, 10, 'x')

kundi CContextAPItests(ContextAPItests):
    decimal = C
kundi PyContextAPItests(ContextAPItests):
    decimal = P

kundi ContextWithStatement(unittest.TestCase):
    # Can't do these kama docstrings until Python 2.6
    # kama doctest can't handle __future__ statements

    eleza test_localcontext(self):
        # Use a copy of the current context kwenye the block
        getcontext = self.decimal.getcontext
        localcontext = self.decimal.localcontext

        orig_ctx = getcontext()
        ukijumuisha localcontext() kama enter_ctx:
            set_ctx = getcontext()
        final_ctx = getcontext()
        self.assertIs(orig_ctx, final_ctx, 'did sio restore context correctly')
        self.assertIsNot(orig_ctx, set_ctx, 'did sio copy the context')
        self.assertIs(set_ctx, enter_ctx, '__enter__ returned wrong context')

    eleza test_localcontextarg(self):
        # Use a copy of the supplied context kwenye the block
        Context = self.decimal.Context
        getcontext = self.decimal.getcontext
        localcontext = self.decimal.localcontext

        localcontext = self.decimal.localcontext
        orig_ctx = getcontext()
        new_ctx = Context(prec=42)
        ukijumuisha localcontext(new_ctx) kama enter_ctx:
            set_ctx = getcontext()
        final_ctx = getcontext()
        self.assertIs(orig_ctx, final_ctx, 'did sio restore context correctly')
        self.assertEqual(set_ctx.prec, new_ctx.prec, 'did sio set correct context')
        self.assertIsNot(new_ctx, set_ctx, 'did sio copy the context')
        self.assertIs(set_ctx, enter_ctx, '__enter__ returned wrong context')

    eleza test_nested_with_statements(self):
        # Use a copy of the supplied context kwenye the block
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context
        getcontext = self.decimal.getcontext
        localcontext = self.decimal.localcontext
        Clamped = self.decimal.Clamped
        Overflow = self.decimal.Overflow

        orig_ctx = getcontext()
        orig_ctx.clear_flags()
        new_ctx = Context(Emax=384)
        ukijumuisha localcontext() kama c1:
            self.assertEqual(c1.flags, orig_ctx.flags)
            self.assertEqual(c1.traps, orig_ctx.traps)
            c1.traps[Clamped] = Kweli
            c1.Emin = -383
            self.assertNotEqual(orig_ctx.Emin, -383)
            self.assertRaises(Clamped, c1.create_decimal, '0e-999')
            self.assertKweli(c1.flags[Clamped])
            ukijumuisha localcontext(new_ctx) kama c2:
                self.assertEqual(c2.flags, new_ctx.flags)
                self.assertEqual(c2.traps, new_ctx.traps)
                self.assertRaises(Overflow, c2.power, Decimal('3.4e200'), 2)
                self.assertUongo(c2.flags[Clamped])
                self.assertKweli(c2.flags[Overflow])
                toa c2
            self.assertUongo(c1.flags[Overflow])
            toa c1
        self.assertNotEqual(orig_ctx.Emin, -383)
        self.assertUongo(orig_ctx.flags[Clamped])
        self.assertUongo(orig_ctx.flags[Overflow])
        self.assertUongo(new_ctx.flags[Clamped])
        self.assertUongo(new_ctx.flags[Overflow])

    eleza test_with_statements_gc1(self):
        localcontext = self.decimal.localcontext

        ukijumuisha localcontext() kama c1:
            toa c1
            ukijumuisha localcontext() kama c2:
                toa c2
                ukijumuisha localcontext() kama c3:
                    toa c3
                    ukijumuisha localcontext() kama c4:
                        toa c4

    eleza test_with_statements_gc2(self):
        localcontext = self.decimal.localcontext

        ukijumuisha localcontext() kama c1:
            ukijumuisha localcontext(c1) kama c2:
                toa c1
                ukijumuisha localcontext(c2) kama c3:
                    toa c2
                    ukijumuisha localcontext(c3) kama c4:
                        toa c3
                        toa c4

    eleza test_with_statements_gc3(self):
        Context = self.decimal.Context
        localcontext = self.decimal.localcontext
        getcontext = self.decimal.getcontext
        setcontext = self.decimal.setcontext

        ukijumuisha localcontext() kama c1:
            toa c1
            n1 = Context(prec=1)
            setcontext(n1)
            ukijumuisha localcontext(n1) kama c2:
                toa n1
                self.assertEqual(c2.prec, 1)
                toa c2
                n2 = Context(prec=2)
                setcontext(n2)
                toa n2
                self.assertEqual(getcontext().prec, 2)
                n3 = Context(prec=3)
                setcontext(n3)
                self.assertEqual(getcontext().prec, 3)
                ukijumuisha localcontext(n3) kama c3:
                    toa n3
                    self.assertEqual(c3.prec, 3)
                    toa c3
                    n4 = Context(prec=4)
                    setcontext(n4)
                    toa n4
                    self.assertEqual(getcontext().prec, 4)
                    ukijumuisha localcontext() kama c4:
                        self.assertEqual(c4.prec, 4)
                        toa c4

kundi CContextWithStatement(ContextWithStatement):
    decimal = C
kundi PyContextWithStatement(ContextWithStatement):
    decimal = P

kundi ContextFlags(unittest.TestCase):

    eleza test_flags_irrelevant(self):
        # check that the result (numeric result + flags raised) of an
        # arithmetic operation doesn't depend on the current flags
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context
        Inexact = self.decimal.Inexact
        Rounded = self.decimal.Rounded
        Underflow = self.decimal.Underflow
        Clamped = self.decimal.Clamped
        Subnormal = self.decimal.Subnormal

        eleza raise_error(context, flag):
            ikiwa self.decimal == C:
                context.flags[flag] = Kweli
                ikiwa context.traps[flag]:
                    ashiria flag
            isipokua:
                context._raise_error(flag)

        context = Context(prec=9, Emin = -425000000, Emax = 425000000,
                          rounding=ROUND_HALF_EVEN, traps=[], flags=[])

        # operations that ashiria various flags, kwenye the form (function, arglist)
        operations = [
            (context._apply, [Decimal("100E-425000010")]),
            (context.sqrt, [Decimal(2)]),
            (context.add, [Decimal("1.23456789"), Decimal("9.87654321")]),
            (context.multiply, [Decimal("1.23456789"), Decimal("9.87654321")]),
            (context.subtract, [Decimal("1.23456789"), Decimal("9.87654321")]),
            ]

        # try various flags individually, then a whole lot at once
        flagsets = [[Inexact], [Rounded], [Underflow], [Clamped], [Subnormal],
                    [Inexact, Rounded, Underflow, Clamped, Subnormal]]

        kila fn, args kwenye operations:
            # find answer na flags raised using a clean context
            context.clear_flags()
            ans = fn(*args)
            flags = [k kila k, v kwenye context.flags.items() ikiwa v]

            kila extra_flags kwenye flagsets:
                # set flags, before calling operation
                context.clear_flags()
                kila flag kwenye extra_flags:
                    raise_error(context, flag)
                new_ans = fn(*args)

                # flags that we expect to be set after the operation
                expected_flags = list(flags)
                kila flag kwenye extra_flags:
                    ikiwa flag haiko kwenye expected_flags:
                        expected_flags.append(flag)
                expected_flags.sort(key=id)

                # flags we actually got
                new_flags = [k kila k,v kwenye context.flags.items() ikiwa v]
                new_flags.sort(key=id)

                self.assertEqual(ans, new_ans,
                                 "operation produces different answers depending on flags set: " +
                                 "expected %s, got %s." % (ans, new_ans))
                self.assertEqual(new_flags, expected_flags,
                                  "operation raises different flags depending on flags set: " +
                                  "expected %s, got %s" % (expected_flags, new_flags))

    eleza test_flag_comparisons(self):
        Context = self.decimal.Context
        Inexact = self.decimal.Inexact
        Rounded = self.decimal.Rounded

        c = Context()

        # Valid SignalDict
        self.assertNotEqual(c.flags, c.traps)
        self.assertNotEqual(c.traps, c.flags)

        c.flags = c.traps
        self.assertEqual(c.flags, c.traps)
        self.assertEqual(c.traps, c.flags)

        c.flags[Rounded] = Kweli
        c.traps = c.flags
        self.assertEqual(c.flags, c.traps)
        self.assertEqual(c.traps, c.flags)

        d = {}
        d.update(c.flags)
        self.assertEqual(d, c.flags)
        self.assertEqual(c.flags, d)

        d[Inexact] = Kweli
        self.assertNotEqual(d, c.flags)
        self.assertNotEqual(c.flags, d)

        # Invalid SignalDict
        d = {Inexact:Uongo}
        self.assertNotEqual(d, c.flags)
        self.assertNotEqual(c.flags, d)

        d = ["xyz"]
        self.assertNotEqual(d, c.flags)
        self.assertNotEqual(c.flags, d)

    @requires_IEEE_754
    eleza test_float_operation(self):
        Decimal = self.decimal.Decimal
        FloatOperation = self.decimal.FloatOperation
        localcontext = self.decimal.localcontext

        ukijumuisha localcontext() kama c:
            ##### trap ni off by default
            self.assertUongo(c.traps[FloatOperation])

            # implicit conversion sets the flag
            c.clear_flags()
            self.assertEqual(Decimal(7.5), 7.5)
            self.assertKweli(c.flags[FloatOperation])

            c.clear_flags()
            self.assertEqual(c.create_decimal(7.5), 7.5)
            self.assertKweli(c.flags[FloatOperation])

            # explicit conversion does sio set the flag
            c.clear_flags()
            x = Decimal.from_float(7.5)
            self.assertUongo(c.flags[FloatOperation])
            # comparison sets the flag
            self.assertEqual(x, 7.5)
            self.assertKweli(c.flags[FloatOperation])

            c.clear_flags()
            x = c.create_decimal_from_float(7.5)
            self.assertUongo(c.flags[FloatOperation])
            self.assertEqual(x, 7.5)
            self.assertKweli(c.flags[FloatOperation])

            ##### set the trap
            c.traps[FloatOperation] = Kweli

            # implicit conversion raises
            c.clear_flags()
            self.assertRaises(FloatOperation, Decimal, 7.5)
            self.assertKweli(c.flags[FloatOperation])

            c.clear_flags()
            self.assertRaises(FloatOperation, c.create_decimal, 7.5)
            self.assertKweli(c.flags[FloatOperation])

            # explicit conversion ni silent
            c.clear_flags()
            x = Decimal.from_float(7.5)
            self.assertUongo(c.flags[FloatOperation])

            c.clear_flags()
            x = c.create_decimal_from_float(7.5)
            self.assertUongo(c.flags[FloatOperation])

    eleza test_float_comparison(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context
        FloatOperation = self.decimal.FloatOperation
        localcontext = self.decimal.localcontext

        eleza assert_attr(a, b, attr, context, signal=Tupu):
            context.clear_flags()
            f = getattr(a, attr)
            ikiwa signal == FloatOperation:
                self.assertRaises(signal, f, b)
            isipokua:
                self.assertIs(f(b), Kweli)
            self.assertKweli(context.flags[FloatOperation])

        small_d = Decimal('0.25')
        big_d = Decimal('3.0')
        small_f = 0.25
        big_f = 3.0

        zero_d = Decimal('0.0')
        neg_zero_d = Decimal('-0.0')
        zero_f = 0.0
        neg_zero_f = -0.0

        inf_d = Decimal('Infinity')
        neg_inf_d = Decimal('-Infinity')
        inf_f = float('inf')
        neg_inf_f = float('-inf')

        eleza doit(c, signal=Tupu):
            # Order
            kila attr kwenye '__lt__', '__le__':
                assert_attr(small_d, big_f, attr, c, signal)

            kila attr kwenye '__gt__', '__ge__':
                assert_attr(big_d, small_f, attr, c, signal)

            # Equality
            assert_attr(small_d, small_f, '__eq__', c, Tupu)

            assert_attr(neg_zero_d, neg_zero_f, '__eq__', c, Tupu)
            assert_attr(neg_zero_d, zero_f, '__eq__', c, Tupu)

            assert_attr(zero_d, neg_zero_f, '__eq__', c, Tupu)
            assert_attr(zero_d, zero_f, '__eq__', c, Tupu)

            assert_attr(neg_inf_d, neg_inf_f, '__eq__', c, Tupu)
            assert_attr(inf_d, inf_f, '__eq__', c, Tupu)

            # Inequality
            assert_attr(small_d, big_f, '__ne__', c, Tupu)

            assert_attr(Decimal('0.1'), 0.1, '__ne__', c, Tupu)

            assert_attr(neg_inf_d, inf_f, '__ne__', c, Tupu)
            assert_attr(inf_d, neg_inf_f, '__ne__', c, Tupu)

            assert_attr(Decimal('NaN'), float('nan'), '__ne__', c, Tupu)

        eleza test_containers(c, signal=Tupu):
            c.clear_flags()
            s = set([100.0, Decimal('100.0')])
            self.assertEqual(len(s), 1)
            self.assertKweli(c.flags[FloatOperation])

            c.clear_flags()
            ikiwa signal:
                self.assertRaises(signal, sorted, [1.0, Decimal('10.0')])
            isipokua:
                s = sorted([10.0, Decimal('10.0')])
            self.assertKweli(c.flags[FloatOperation])

            c.clear_flags()
            b = 10.0 kwenye [Decimal('10.0'), 1.0]
            self.assertKweli(c.flags[FloatOperation])

            c.clear_flags()
            b = 10.0 kwenye {Decimal('10.0'):'a', 1.0:'b'}
            self.assertKweli(c.flags[FloatOperation])

        nc = Context()
        ukijumuisha localcontext(nc) kama c:
            self.assertUongo(c.traps[FloatOperation])
            doit(c, signal=Tupu)
            test_containers(c, signal=Tupu)

            c.traps[FloatOperation] = Kweli
            doit(c, signal=FloatOperation)
            test_containers(c, signal=FloatOperation)

    eleza test_float_operation_default(self):
        Decimal = self.decimal.Decimal
        Context = self.decimal.Context
        Inexact = self.decimal.Inexact
        FloatOperation= self.decimal.FloatOperation

        context = Context()
        self.assertUongo(context.flags[FloatOperation])
        self.assertUongo(context.traps[FloatOperation])

        context.clear_traps()
        context.traps[Inexact] = Kweli
        context.traps[FloatOperation] = Kweli
        self.assertKweli(context.traps[FloatOperation])
        self.assertKweli(context.traps[Inexact])

kundi CContextFlags(ContextFlags):
    decimal = C
kundi PyContextFlags(ContextFlags):
    decimal = P

kundi SpecialContexts(unittest.TestCase):
    """Test the context templates."""

    eleza test_context_templates(self):
        BasicContext = self.decimal.BasicContext
        ExtendedContext = self.decimal.ExtendedContext
        getcontext = self.decimal.getcontext
        setcontext = self.decimal.setcontext
        InvalidOperation = self.decimal.InvalidOperation
        DivisionByZero = self.decimal.DivisionByZero
        Overflow = self.decimal.Overflow
        Underflow = self.decimal.Underflow
        Clamped = self.decimal.Clamped

        assert_signals(self, BasicContext, 'traps',
            [InvalidOperation, DivisionByZero, Overflow, Underflow, Clamped]
        )

        savecontext = getcontext().copy()
        basic_context_prec = BasicContext.prec
        extended_context_prec = ExtendedContext.prec

        ex = Tupu
        jaribu:
            BasicContext.prec = ExtendedContext.prec = 441
            kila template kwenye BasicContext, ExtendedContext:
                setcontext(template)
                c = getcontext()
                self.assertIsNot(c, template)
                self.assertEqual(c.prec, 441)
        tatizo Exception kama e:
            ex = e.__class__
        mwishowe:
            BasicContext.prec = basic_context_prec
            ExtendedContext.prec = extended_context_prec
            setcontext(savecontext)
            ikiwa ex:
                ashiria ex

    eleza test_default_context(self):
        DefaultContext = self.decimal.DefaultContext
        BasicContext = self.decimal.BasicContext
        ExtendedContext = self.decimal.ExtendedContext
        getcontext = self.decimal.getcontext
        setcontext = self.decimal.setcontext
        InvalidOperation = self.decimal.InvalidOperation
        DivisionByZero = self.decimal.DivisionByZero
        Overflow = self.decimal.Overflow

        self.assertEqual(BasicContext.prec, 9)
        self.assertEqual(ExtendedContext.prec, 9)

        assert_signals(self, DefaultContext, 'traps',
            [InvalidOperation, DivisionByZero, Overflow]
        )

        savecontext = getcontext().copy()
        default_context_prec = DefaultContext.prec

        ex = Tupu
        jaribu:
            c = getcontext()
            saveprec = c.prec

            DefaultContext.prec = 961
            c = getcontext()
            self.assertEqual(c.prec, saveprec)

            setcontext(DefaultContext)
            c = getcontext()
            self.assertIsNot(c, DefaultContext)
            self.assertEqual(c.prec, 961)
        tatizo Exception kama e:
            ex = e.__class__
        mwishowe:
            DefaultContext.prec = default_context_prec
            setcontext(savecontext)
            ikiwa ex:
                ashiria ex

kundi CSpecialContexts(SpecialContexts):
    decimal = C
kundi PySpecialContexts(SpecialContexts):
    decimal = P

kundi ContextInputValidation(unittest.TestCase):

    eleza test_invalid_context(self):
        Context = self.decimal.Context
        DefaultContext = self.decimal.DefaultContext

        c = DefaultContext.copy()

        # prec, Emax
        kila attr kwenye ['prec', 'Emax']:
            setattr(c, attr, 999999)
            self.assertEqual(getattr(c, attr), 999999)
            self.assertRaises(ValueError, setattr, c, attr, -1)
            self.assertRaises(TypeError, setattr, c, attr, 'xyz')

        # Emin
        setattr(c, 'Emin', -999999)
        self.assertEqual(getattr(c, 'Emin'), -999999)
        self.assertRaises(ValueError, setattr, c, 'Emin', 1)
        self.assertRaises(TypeError, setattr, c, 'Emin', (1,2,3))

        self.assertRaises(TypeError, setattr, c, 'rounding', -1)
        self.assertRaises(TypeError, setattr, c, 'rounding', 9)
        self.assertRaises(TypeError, setattr, c, 'rounding', 1.0)
        self.assertRaises(TypeError, setattr, c, 'rounding', 'xyz')

        # capitals, clamp
        kila attr kwenye ['capitals', 'clamp']:
            self.assertRaises(ValueError, setattr, c, attr, -1)
            self.assertRaises(ValueError, setattr, c, attr, 2)
            self.assertRaises(TypeError, setattr, c, attr, [1,2,3])

        # Invalid attribute
        self.assertRaises(AttributeError, setattr, c, 'emax', 100)

        # Invalid signal dict
        self.assertRaises(TypeError, setattr, c, 'flags', [])
        self.assertRaises(KeyError, setattr, c, 'flags', {})
        self.assertRaises(KeyError, setattr, c, 'traps',
                          {'InvalidOperation':0})

        # Attributes cannot be deleted
        kila attr kwenye ['prec', 'Emax', 'Emin', 'rounding', 'capitals', 'clamp',
                     'flags', 'traps']:
            self.assertRaises(AttributeError, c.__delattr__, attr)

        # Invalid attributes
        self.assertRaises(TypeError, getattr, c, 9)
        self.assertRaises(TypeError, setattr, c, 9)

        # Invalid values kwenye constructor
        self.assertRaises(TypeError, Context, rounding=999999)
        self.assertRaises(TypeError, Context, rounding='xyz')
        self.assertRaises(ValueError, Context, clamp=2)
        self.assertRaises(ValueError, Context, capitals=-1)
        self.assertRaises(KeyError, Context, flags=["P"])
        self.assertRaises(KeyError, Context, traps=["Q"])

        # Type error kwenye conversion
        self.assertRaises(TypeError, Context, flags=(0,1))
        self.assertRaises(TypeError, Context, traps=(1,0))

kundi CContextInputValidation(ContextInputValidation):
    decimal = C
kundi PyContextInputValidation(ContextInputValidation):
    decimal = P

kundi ContextSubclassing(unittest.TestCase):

    eleza test_context_subclassing(self):
        decimal = self.decimal
        Decimal = decimal.Decimal
        Context = decimal.Context
        Clamped = decimal.Clamped
        DivisionByZero = decimal.DivisionByZero
        Inexact = decimal.Inexact
        Overflow = decimal.Overflow
        Rounded = decimal.Rounded
        Subnormal = decimal.Subnormal
        Underflow = decimal.Underflow
        InvalidOperation = decimal.InvalidOperation

        kundi MyContext(Context):
            eleza __init__(self, prec=Tupu, rounding=Tupu, Emin=Tupu, Emax=Tupu,
                               capitals=Tupu, clamp=Tupu, flags=Tupu,
                               traps=Tupu):
                Context.__init__(self)
                ikiwa prec ni sio Tupu:
                    self.prec = prec
                ikiwa rounding ni sio Tupu:
                    self.rounding = rounding
                ikiwa Emin ni sio Tupu:
                    self.Emin = Emin
                ikiwa Emax ni sio Tupu:
                    self.Emax = Emax
                ikiwa capitals ni sio Tupu:
                    self.capitals = capitals
                ikiwa clamp ni sio Tupu:
                    self.clamp = clamp
                ikiwa flags ni sio Tupu:
                    ikiwa isinstance(flags, list):
                        flags = {v:(v kwenye flags) kila v kwenye OrderedSignals[decimal] + flags}
                    self.flags = flags
                ikiwa traps ni sio Tupu:
                    ikiwa isinstance(traps, list):
                        traps = {v:(v kwenye traps) kila v kwenye OrderedSignals[decimal] + traps}
                    self.traps = traps

        c = Context()
        d = MyContext()
        kila attr kwenye ('prec', 'rounding', 'Emin', 'Emax', 'capitals', 'clamp',
                     'flags', 'traps'):
            self.assertEqual(getattr(c, attr), getattr(d, attr))

        # prec
        self.assertRaises(ValueError, MyContext, **{'prec':-1})
        c = MyContext(prec=1)
        self.assertEqual(c.prec, 1)
        self.assertRaises(InvalidOperation, c.quantize, Decimal('9e2'), 0)

        # rounding
        self.assertRaises(TypeError, MyContext, **{'rounding':'XYZ'})
        c = MyContext(rounding=ROUND_DOWN, prec=1)
        self.assertEqual(c.rounding, ROUND_DOWN)
        self.assertEqual(c.plus(Decimal('9.9')), 9)

        # Emin
        self.assertRaises(ValueError, MyContext, **{'Emin':5})
        c = MyContext(Emin=-1, prec=1)
        self.assertEqual(c.Emin, -1)
        x = c.add(Decimal('1e-99'), Decimal('2.234e-2000'))
        self.assertEqual(x, Decimal('0.0'))
        kila signal kwenye (Inexact, Underflow, Subnormal, Rounded, Clamped):
            self.assertKweli(c.flags[signal])

        # Emax
        self.assertRaises(ValueError, MyContext, **{'Emax':-1})
        c = MyContext(Emax=1, prec=1)
        self.assertEqual(c.Emax, 1)
        self.assertRaises(Overflow, c.add, Decimal('1e99'), Decimal('2.234e2000'))
        ikiwa self.decimal == C:
            kila signal kwenye (Inexact, Overflow, Rounded):
                self.assertKweli(c.flags[signal])

        # capitals
        self.assertRaises(ValueError, MyContext, **{'capitals':-1})
        c = MyContext(capitals=0)
        self.assertEqual(c.capitals, 0)
        x = c.create_decimal('1E222')
        self.assertEqual(c.to_sci_string(x), '1e+222')

        # clamp
        self.assertRaises(ValueError, MyContext, **{'clamp':2})
        c = MyContext(clamp=1, Emax=99)
        self.assertEqual(c.clamp, 1)
        x = c.plus(Decimal('1e99'))
        self.assertEqual(str(x), '1.000000000000000000000000000E+99')

        # flags
        self.assertRaises(TypeError, MyContext, **{'flags':'XYZ'})
        c = MyContext(flags=[Rounded, DivisionByZero])
        kila signal kwenye (Rounded, DivisionByZero):
            self.assertKweli(c.flags[signal])
        c.clear_flags()
        kila signal kwenye OrderedSignals[decimal]:
            self.assertUongo(c.flags[signal])

        # traps
        self.assertRaises(TypeError, MyContext, **{'traps':'XYZ'})
        c = MyContext(traps=[Rounded, DivisionByZero])
        kila signal kwenye (Rounded, DivisionByZero):
            self.assertKweli(c.traps[signal])
        c.clear_traps()
        kila signal kwenye OrderedSignals[decimal]:
            self.assertUongo(c.traps[signal])

kundi CContextSubclassing(ContextSubclassing):
    decimal = C
kundi PyContextSubclassing(ContextSubclassing):
    decimal = P

@skip_if_extra_functionality
kundi CheckAttributes(unittest.TestCase):

    eleza test_module_attributes(self):

        # Architecture dependent context limits
        self.assertEqual(C.MAX_PREC, P.MAX_PREC)
        self.assertEqual(C.MAX_EMAX, P.MAX_EMAX)
        self.assertEqual(C.MIN_EMIN, P.MIN_EMIN)
        self.assertEqual(C.MIN_ETINY, P.MIN_ETINY)

        self.assertKweli(C.HAVE_THREADS ni Kweli ama C.HAVE_THREADS ni Uongo)
        self.assertKweli(P.HAVE_THREADS ni Kweli ama P.HAVE_THREADS ni Uongo)

        self.assertEqual(C.__version__, P.__version__)

        self.assertEqual(dir(C), dir(P))

    eleza test_context_attributes(self):

        x = [s kila s kwenye dir(C.Context()) ikiwa '__' kwenye s ama sio s.startswith('_')]
        y = [s kila s kwenye dir(P.Context()) ikiwa '__' kwenye s ama sio s.startswith('_')]
        self.assertEqual(set(x) - set(y), set())

    eleza test_decimal_attributes(self):

        x = [s kila s kwenye dir(C.Decimal(9)) ikiwa '__' kwenye s ama sio s.startswith('_')]
        y = [s kila s kwenye dir(C.Decimal(9)) ikiwa '__' kwenye s ama sio s.startswith('_')]
        self.assertEqual(set(x) - set(y), set())

kundi Coverage(unittest.TestCase):

    eleza test_adjusted(self):
        Decimal = self.decimal.Decimal

        self.assertEqual(Decimal('1234e9999').adjusted(), 10002)
        # XXX raise?
        self.assertEqual(Decimal('nan').adjusted(), 0)
        self.assertEqual(Decimal('inf').adjusted(), 0)

    eleza test_canonical(self):
        Decimal = self.decimal.Decimal
        getcontext = self.decimal.getcontext

        x = Decimal(9).canonical()
        self.assertEqual(x, 9)

        c = getcontext()
        x = c.canonical(Decimal(9))
        self.assertEqual(x, 9)

    eleza test_context_repr(self):
        c = self.decimal.DefaultContext.copy()

        c.prec = 425000000
        c.Emax = 425000000
        c.Emin = -425000000
        c.rounding = ROUND_HALF_DOWN
        c.capitals = 0
        c.clamp = 1
        kila sig kwenye OrderedSignals[self.decimal]:
            c.flags[sig] = Uongo
            c.traps[sig] = Uongo

        s = c.__repr__()
        t = "Context(prec=425000000, rounding=ROUND_HALF_DOWN, " \
            "Emin=-425000000, Emax=425000000, capitals=0, clamp=1, " \
            "flags=[], traps=[])"
        self.assertEqual(s, t)

    eleza test_implicit_context(self):
        Decimal = self.decimal.Decimal
        localcontext = self.decimal.localcontext

        ukijumuisha localcontext() kama c:
            c.prec = 1
            c.Emax = 1
            c.Emin = -1

            # abs
            self.assertEqual(abs(Decimal("-10")), 10)
            # add
            self.assertEqual(Decimal("7") + 1, 8)
            # divide
            self.assertEqual(Decimal("10") / 5, 2)
            # divide_int
            self.assertEqual(Decimal("10") // 7, 1)
            # fma
            self.assertEqual(Decimal("1.2").fma(Decimal("0.01"), 1), 1)
            self.assertIs(Decimal("NaN").fma(7, 1).is_nan(), Kweli)
            # three arg power
            self.assertEqual(pow(Decimal(10), 2, 7), 2)
            # exp
            self.assertEqual(Decimal("1.01").exp(), 3)
            # is_normal
            self.assertIs(Decimal("0.01").is_normal(), Uongo)
            # is_subnormal
            self.assertIs(Decimal("0.01").is_subnormal(), Kweli)
            # ln
            self.assertEqual(Decimal("20").ln(), 3)
            # log10
            self.assertEqual(Decimal("20").log10(), 1)
            # logb
            self.assertEqual(Decimal("580").logb(), 2)
            # logical_invert
            self.assertEqual(Decimal("10").logical_invert(), 1)
            # minus
            self.assertEqual(-Decimal("-10"), 10)
            # multiply
            self.assertEqual(Decimal("2") * 4, 8)
            # next_minus
            self.assertEqual(Decimal("10").next_minus(), 9)
            # next_plus
            self.assertEqual(Decimal("10").next_plus(), Decimal('2E+1'))
            # normalize
            self.assertEqual(Decimal("-10").normalize(), Decimal('-1E+1'))
            # number_class
            self.assertEqual(Decimal("10").number_class(), '+Normal')
            # plus
            self.assertEqual(+Decimal("-1"), -1)
            # remainder
            self.assertEqual(Decimal("10") % 7, 3)
            # subtract
            self.assertEqual(Decimal("10") - 7, 3)
            # to_integral_exact
            self.assertEqual(Decimal("1.12345").to_integral_exact(), 1)

            # Boolean functions
            self.assertKweli(Decimal("1").is_canonical())
            self.assertKweli(Decimal("1").is_finite())
            self.assertKweli(Decimal("1").is_finite())
            self.assertKweli(Decimal("snan").is_snan())
            self.assertKweli(Decimal("-1").is_signed())
            self.assertKweli(Decimal("0").is_zero())
            self.assertKweli(Decimal("0").is_zero())

        # Copy
        ukijumuisha localcontext() kama c:
            c.prec = 10000
            x = 1228 ** 1523
            y = -Decimal(x)

            z = y.copy_abs()
            self.assertEqual(z, x)

            z = y.copy_negate()
            self.assertEqual(z, x)

            z = y.copy_sign(Decimal(1))
            self.assertEqual(z, x)

    eleza test_divmod(self):
        Decimal = self.decimal.Decimal
        localcontext = self.decimal.localcontext
        InvalidOperation = self.decimal.InvalidOperation
        DivisionByZero = self.decimal.DivisionByZero

        ukijumuisha localcontext() kama c:
            q, r = divmod(Decimal("10912837129"), 1001)
            self.assertEqual(q, Decimal('10901935'))
            self.assertEqual(r, Decimal('194'))

            q, r = divmod(Decimal("NaN"), 7)
            self.assertKweli(q.is_nan() na r.is_nan())

            c.traps[InvalidOperation] = Uongo
            q, r = divmod(Decimal("NaN"), 7)
            self.assertKweli(q.is_nan() na r.is_nan())

            c.traps[InvalidOperation] = Uongo
            c.clear_flags()
            q, r = divmod(Decimal("inf"), Decimal("inf"))
            self.assertKweli(q.is_nan() na r.is_nan())
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            q, r = divmod(Decimal("inf"), 101)
            self.assertKweli(q.is_infinite() na r.is_nan())
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            q, r = divmod(Decimal(0), 0)
            self.assertKweli(q.is_nan() na r.is_nan())
            self.assertKweli(c.flags[InvalidOperation])

            c.traps[DivisionByZero] = Uongo
            c.clear_flags()
            q, r = divmod(Decimal(11), 0)
            self.assertKweli(q.is_infinite() na r.is_nan())
            self.assertKweli(c.flags[InvalidOperation] na
                            c.flags[DivisionByZero])

    eleza test_power(self):
        Decimal = self.decimal.Decimal
        localcontext = self.decimal.localcontext
        Overflow = self.decimal.Overflow
        Rounded = self.decimal.Rounded

        ukijumuisha localcontext() kama c:
            c.prec = 3
            c.clear_flags()
            self.assertEqual(Decimal("1.0") ** 100, Decimal('1.00'))
            self.assertKweli(c.flags[Rounded])

            c.prec = 1
            c.Emax = 1
            c.Emin = -1
            c.clear_flags()
            c.traps[Overflow] = Uongo
            self.assertEqual(Decimal(10000) ** Decimal("0.5"), Decimal('inf'))
            self.assertKweli(c.flags[Overflow])

    eleza test_quantize(self):
        Decimal = self.decimal.Decimal
        localcontext = self.decimal.localcontext
        InvalidOperation = self.decimal.InvalidOperation

        ukijumuisha localcontext() kama c:
            c.prec = 1
            c.Emax = 1
            c.Emin = -1
            c.traps[InvalidOperation] = Uongo
            x = Decimal(99).quantize(Decimal("1e1"))
            self.assertKweli(x.is_nan())

    eleza test_radix(self):
        Decimal = self.decimal.Decimal
        getcontext = self.decimal.getcontext

        c = getcontext()
        self.assertEqual(Decimal("1").radix(), 10)
        self.assertEqual(c.radix(), 10)

    eleza test_rop(self):
        Decimal = self.decimal.Decimal

        kila attr kwenye ('__radd__', '__rsub__', '__rmul__', '__rtruediv__',
                     '__rdivmod__', '__rmod__', '__rfloordiv__', '__rpow__'):
            self.assertIs(getattr(Decimal("1"), attr)("xyz"), NotImplemented)

    eleza test_round(self):
        # Python3 behavior: round() returns Decimal
        Decimal = self.decimal.Decimal
        localcontext = self.decimal.localcontext

        ukijumuisha localcontext() kama c:
            c.prec = 28

            self.assertEqual(str(Decimal("9.99").__round__()), "10")
            self.assertEqual(str(Decimal("9.99e-5").__round__()), "0")
            self.assertEqual(str(Decimal("1.23456789").__round__(5)), "1.23457")
            self.assertEqual(str(Decimal("1.2345").__round__(10)), "1.2345000000")
            self.assertEqual(str(Decimal("1.2345").__round__(-10)), "0E+10")

            self.assertRaises(TypeError, Decimal("1.23").__round__, "5")
            self.assertRaises(TypeError, Decimal("1.23").__round__, 5, 8)

    eleza test_create_decimal(self):
        c = self.decimal.Context()
        self.assertRaises(ValueError, c.create_decimal, ["%"])

    eleza test_int(self):
        Decimal = self.decimal.Decimal
        localcontext = self.decimal.localcontext

        ukijumuisha localcontext() kama c:
            c.prec = 9999
            x = Decimal(1221**1271) / 10**3923
            self.assertEqual(int(x), 1)
            self.assertEqual(x.to_integral(), 2)

    eleza test_copy(self):
        Context = self.decimal.Context

        c = Context()
        c.prec = 10000
        x = -(1172 ** 1712)

        y = c.copy_abs(x)
        self.assertEqual(y, -x)

        y = c.copy_negate(x)
        self.assertEqual(y, -x)

        y = c.copy_sign(x, 1)
        self.assertEqual(y, -x)

kundi CCoverage(Coverage):
    decimal = C
kundi PyCoverage(Coverage):
    decimal = P

kundi PyFunctionality(unittest.TestCase):
    """Extra functionality kwenye decimal.py"""

    eleza test_py_alternate_formatting(self):
        # triples giving a format, a Decimal, na the expected result
        Decimal = P.Decimal
        localcontext = P.localcontext

        test_values = [
            # Issue 7094: Alternate formatting (specified by #)
            ('.0e', '1.0', '1e+0'),
            ('#.0e', '1.0', '1.e+0'),
            ('.0f', '1.0', '1'),
            ('#.0f', '1.0', '1.'),
            ('g', '1.1', '1.1'),
            ('#g', '1.1', '1.1'),
            ('.0g', '1', '1'),
            ('#.0g', '1', '1.'),
            ('.0%', '1.0', '100%'),
            ('#.0%', '1.0', '100.%'),
            ]
        kila fmt, d, result kwenye test_values:
            self.assertEqual(format(Decimal(d), fmt), result)

kundi PyWhitebox(unittest.TestCase):
    """White box testing kila decimal.py"""

    eleza test_py_exact_power(self):
        # Rarely exercised lines kwenye _power_exact.
        Decimal = P.Decimal
        localcontext = P.localcontext

        ukijumuisha localcontext() kama c:
            c.prec = 8
            x = Decimal(2**16) ** Decimal("-0.5")
            self.assertEqual(x, Decimal('0.00390625'))

            x = Decimal(2**16) ** Decimal("-0.6")
            self.assertEqual(x, Decimal('0.0012885819'))

            x = Decimal("256e7") ** Decimal("-0.5")

            x = Decimal(152587890625) ** Decimal('-0.0625')
            self.assertEqual(x, Decimal("0.2"))

            x = Decimal("152587890625e7") ** Decimal('-0.0625')

            x = Decimal(5**2659) ** Decimal('-0.0625')

            c.prec = 1
            x = Decimal("152587890625") ** Decimal('-0.5')
            c.prec = 201
            x = Decimal(2**578) ** Decimal("-0.5")

    eleza test_py_immutability_operations(self):
        # Do operations na check that it didn't change internal objects.
        Decimal = P.Decimal
        DefaultContext = P.DefaultContext
        setcontext = P.setcontext

        c = DefaultContext.copy()
        c.traps = dict((s, 0) kila s kwenye OrderedSignals[P])
        setcontext(c)

        d1 = Decimal('-25e55')
        b1 = Decimal('-25e55')
        d2 = Decimal('33e+33')
        b2 = Decimal('33e+33')

        eleza checkSameDec(operation, useOther=Uongo):
            ikiwa useOther:
                eval("d1." + operation + "(d2)")
                self.assertEqual(d1._sign, b1._sign)
                self.assertEqual(d1._int, b1._int)
                self.assertEqual(d1._exp, b1._exp)
                self.assertEqual(d2._sign, b2._sign)
                self.assertEqual(d2._int, b2._int)
                self.assertEqual(d2._exp, b2._exp)
            isipokua:
                eval("d1." + operation + "()")
                self.assertEqual(d1._sign, b1._sign)
                self.assertEqual(d1._int, b1._int)
                self.assertEqual(d1._exp, b1._exp)

        Decimal(d1)
        self.assertEqual(d1._sign, b1._sign)
        self.assertEqual(d1._int, b1._int)
        self.assertEqual(d1._exp, b1._exp)

        checkSameDec("__abs__")
        checkSameDec("__add__", Kweli)
        checkSameDec("__divmod__", Kweli)
        checkSameDec("__eq__", Kweli)
        checkSameDec("__ne__", Kweli)
        checkSameDec("__le__", Kweli)
        checkSameDec("__lt__", Kweli)
        checkSameDec("__ge__", Kweli)
        checkSameDec("__gt__", Kweli)
        checkSameDec("__float__")
        checkSameDec("__floordiv__", Kweli)
        checkSameDec("__hash__")
        checkSameDec("__int__")
        checkSameDec("__trunc__")
        checkSameDec("__mod__", Kweli)
        checkSameDec("__mul__", Kweli)
        checkSameDec("__neg__")
        checkSameDec("__bool__")
        checkSameDec("__pos__")
        checkSameDec("__pow__", Kweli)
        checkSameDec("__radd__", Kweli)
        checkSameDec("__rdivmod__", Kweli)
        checkSameDec("__repr__")
        checkSameDec("__rfloordiv__", Kweli)
        checkSameDec("__rmod__", Kweli)
        checkSameDec("__rmul__", Kweli)
        checkSameDec("__rpow__", Kweli)
        checkSameDec("__rsub__", Kweli)
        checkSameDec("__str__")
        checkSameDec("__sub__", Kweli)
        checkSameDec("__truediv__", Kweli)
        checkSameDec("adjusted")
        checkSameDec("as_tuple")
        checkSameDec("compare", Kweli)
        checkSameDec("max", Kweli)
        checkSameDec("min", Kweli)
        checkSameDec("normalize")
        checkSameDec("quantize", Kweli)
        checkSameDec("remainder_near", Kweli)
        checkSameDec("same_quantum", Kweli)
        checkSameDec("sqrt")
        checkSameDec("to_eng_string")
        checkSameDec("to_integral")

    eleza test_py_decimal_id(self):
        Decimal = P.Decimal

        d = Decimal(45)
        e = Decimal(d)
        self.assertEqual(str(e), '45')
        self.assertNotEqual(id(d), id(e))

    eleza test_py_rescale(self):
        # Coverage
        Decimal = P.Decimal
        localcontext = P.localcontext

        ukijumuisha localcontext() kama c:
            x = Decimal("NaN")._rescale(3, ROUND_UP)
            self.assertKweli(x.is_nan())

    eleza test_py__round(self):
        # Coverage
        Decimal = P.Decimal

        self.assertRaises(ValueError, Decimal("3.1234")._round, 0, ROUND_UP)

kundi CFunctionality(unittest.TestCase):
    """Extra functionality kwenye _decimal"""

    @requires_extra_functionality
    eleza test_c_ieee_context(self):
        # issue 8786: Add support kila IEEE 754 contexts to decimal module.
        IEEEContext = C.IEEEContext
        DECIMAL32 = C.DECIMAL32
        DECIMAL64 = C.DECIMAL64
        DECIMAL128 = C.DECIMAL128

        eleza assert_rest(self, context):
            self.assertEqual(context.clamp, 1)
            assert_signals(self, context, 'traps', [])
            assert_signals(self, context, 'flags', [])

        c = IEEEContext(DECIMAL32)
        self.assertEqual(c.prec, 7)
        self.assertEqual(c.Emax, 96)
        self.assertEqual(c.Emin, -95)
        assert_rest(self, c)

        c = IEEEContext(DECIMAL64)
        self.assertEqual(c.prec, 16)
        self.assertEqual(c.Emax, 384)
        self.assertEqual(c.Emin, -383)
        assert_rest(self, c)

        c = IEEEContext(DECIMAL128)
        self.assertEqual(c.prec, 34)
        self.assertEqual(c.Emax, 6144)
        self.assertEqual(c.Emin, -6143)
        assert_rest(self, c)

        # Invalid values
        self.assertRaises(OverflowError, IEEEContext, 2**63)
        self.assertRaises(ValueError, IEEEContext, -1)
        self.assertRaises(ValueError, IEEEContext, 1024)

    @requires_extra_functionality
    eleza test_c_context(self):
        Context = C.Context

        c = Context(flags=C.DecClamped, traps=C.DecRounded)
        self.assertEqual(c._flags, C.DecClamped)
        self.assertEqual(c._traps, C.DecRounded)

    @requires_extra_functionality
    eleza test_constants(self):
        # Condition flags
        cond = (
            C.DecClamped, C.DecConversionSyntax, C.DecDivisionByZero,
            C.DecDivisionImpossible, C.DecDivisionUndefined,
            C.DecFpuError, C.DecInexact, C.DecInvalidContext,
            C.DecInvalidOperation, C.DecMallocError,
            C.DecFloatOperation, C.DecOverflow, C.DecRounded,
            C.DecSubnormal, C.DecUnderflow
        )

        # IEEEContext
        self.assertEqual(C.DECIMAL32, 32)
        self.assertEqual(C.DECIMAL64, 64)
        self.assertEqual(C.DECIMAL128, 128)
        self.assertEqual(C.IEEE_CONTEXT_MAX_BITS, 512)

        # Conditions
        kila i, v kwenye enumerate(cond):
            self.assertEqual(v, 1<<i)

        self.assertEqual(C.DecIEEEInvalidOperation,
                         C.DecConversionSyntax|
                         C.DecDivisionImpossible|
                         C.DecDivisionUndefined|
                         C.DecFpuError|
                         C.DecInvalidContext|
                         C.DecInvalidOperation|
                         C.DecMallocError)

        self.assertEqual(C.DecErrors,
                         C.DecIEEEInvalidOperation|
                         C.DecDivisionByZero)

        self.assertEqual(C.DecTraps,
                         C.DecErrors|C.DecOverflow|C.DecUnderflow)

kundi CWhitebox(unittest.TestCase):
    """Whitebox testing kila _decimal"""

    eleza test_bignum(self):
        # Not exactly whitebox, but too slow ukijumuisha pydecimal.

        Decimal = C.Decimal
        localcontext = C.localcontext

        b1 = 10**35
        b2 = 10**36
        ukijumuisha localcontext() kama c:
            c.prec = 1000000
            kila i kwenye range(5):
                a = random.randrange(b1, b2)
                b = random.randrange(1000, 1200)
                x = a ** b
                y = Decimal(a) ** Decimal(b)
                self.assertEqual(x, y)

    eleza test_invalid_construction(self):
        self.assertRaises(TypeError, C.Decimal, 9, "xyz")

    eleza test_c_input_restriction(self):
        # Too large kila _decimal to be converted exactly
        Decimal = C.Decimal
        InvalidOperation = C.InvalidOperation
        Context = C.Context
        localcontext = C.localcontext

        ukijumuisha localcontext(Context()):
            self.assertRaises(InvalidOperation, Decimal,
                              "1e9999999999999999999")

    eleza test_c_context_repr(self):
        # This test ni _decimal-only because flags are sio printed
        # kwenye the same order.
        DefaultContext = C.DefaultContext
        FloatOperation = C.FloatOperation

        c = DefaultContext.copy()

        c.prec = 425000000
        c.Emax = 425000000
        c.Emin = -425000000
        c.rounding = ROUND_HALF_DOWN
        c.capitals = 0
        c.clamp = 1
        kila sig kwenye OrderedSignals[C]:
            c.flags[sig] = Kweli
            c.traps[sig] = Kweli
        c.flags[FloatOperation] = Kweli
        c.traps[FloatOperation] = Kweli

        s = c.__repr__()
        t = "Context(prec=425000000, rounding=ROUND_HALF_DOWN, " \
            "Emin=-425000000, Emax=425000000, capitals=0, clamp=1, " \
            "flags=[Clamped, InvalidOperation, DivisionByZero, Inexact, " \
                   "FloatOperation, Overflow, Rounded, Subnormal, Underflow], " \
            "traps=[Clamped, InvalidOperation, DivisionByZero, Inexact, " \
                   "FloatOperation, Overflow, Rounded, Subnormal, Underflow])"
        self.assertEqual(s, t)

    eleza test_c_context_errors(self):
        Context = C.Context
        InvalidOperation = C.InvalidOperation
        Overflow = C.Overflow
        FloatOperation = C.FloatOperation
        localcontext = C.localcontext
        getcontext = C.getcontext
        setcontext = C.setcontext
        HAVE_CONFIG_64 = (C.MAX_PREC > 425000000)

        c = Context()

        # SignalDict: input validation
        self.assertRaises(KeyError, c.flags.__setitem__, 801, 0)
        self.assertRaises(KeyError, c.traps.__setitem__, 801, 0)
        self.assertRaises(ValueError, c.flags.__delitem__, Overflow)
        self.assertRaises(ValueError, c.traps.__delitem__, InvalidOperation)
        self.assertRaises(TypeError, setattr, c, 'flags', ['x'])
        self.assertRaises(TypeError, setattr, c,'traps', ['y'])
        self.assertRaises(KeyError, setattr, c, 'flags', {0:1})
        self.assertRaises(KeyError, setattr, c, 'traps', {0:1})

        # Test assignment kutoka a signal dict ukijumuisha the correct length but
        # one invalid key.
        d = c.flags.copy()
        toa d[FloatOperation]
        d["XYZ"] = 91283719
        self.assertRaises(KeyError, setattr, c, 'flags', d)
        self.assertRaises(KeyError, setattr, c, 'traps', d)

        # Input corner cases
        int_max = 2**63-1 ikiwa HAVE_CONFIG_64 isipokua 2**31-1
        gt_max_emax = 10**18 ikiwa HAVE_CONFIG_64 isipokua 10**9

        # prec, Emax, Emin
        kila attr kwenye ['prec', 'Emax']:
            self.assertRaises(ValueError, setattr, c, attr, gt_max_emax)
        self.assertRaises(ValueError, setattr, c, 'Emin', -gt_max_emax)

        # prec, Emax, Emin kwenye context constructor
        self.assertRaises(ValueError, Context, prec=gt_max_emax)
        self.assertRaises(ValueError, Context, Emax=gt_max_emax)
        self.assertRaises(ValueError, Context, Emin=-gt_max_emax)

        # Overflow kwenye conversion
        self.assertRaises(OverflowError, Context, prec=int_max+1)
        self.assertRaises(OverflowError, Context, Emax=int_max+1)
        self.assertRaises(OverflowError, Context, Emin=-int_max-2)
        self.assertRaises(OverflowError, Context, clamp=int_max+1)
        self.assertRaises(OverflowError, Context, capitals=int_max+1)

        # OverflowError, general ValueError
        kila attr kwenye ('prec', 'Emin', 'Emax', 'capitals', 'clamp'):
            self.assertRaises(OverflowError, setattr, c, attr, int_max+1)
            self.assertRaises(OverflowError, setattr, c, attr, -int_max-2)
            ikiwa sys.platform != 'win32':
                self.assertRaises(ValueError, setattr, c, attr, int_max)
                self.assertRaises(ValueError, setattr, c, attr, -int_max-1)

        # OverflowError: _unsafe_setprec, _unsafe_setemin, _unsafe_setemax
        ikiwa C.MAX_PREC == 425000000:
            self.assertRaises(OverflowError, getattr(c, '_unsafe_setprec'),
                              int_max+1)
            self.assertRaises(OverflowError, getattr(c, '_unsafe_setemax'),
                              int_max+1)
            self.assertRaises(OverflowError, getattr(c, '_unsafe_setemin'),
                              -int_max-2)

        # ValueError: _unsafe_setprec, _unsafe_setemin, _unsafe_setemax
        ikiwa C.MAX_PREC == 425000000:
            self.assertRaises(ValueError, getattr(c, '_unsafe_setprec'), 0)
            self.assertRaises(ValueError, getattr(c, '_unsafe_setprec'),
                              1070000001)
            self.assertRaises(ValueError, getattr(c, '_unsafe_setemax'), -1)
            self.assertRaises(ValueError, getattr(c, '_unsafe_setemax'),
                              1070000001)
            self.assertRaises(ValueError, getattr(c, '_unsafe_setemin'),
                              -1070000001)
            self.assertRaises(ValueError, getattr(c, '_unsafe_setemin'), 1)

        # capitals, clamp
        kila attr kwenye ['capitals', 'clamp']:
            self.assertRaises(ValueError, setattr, c, attr, -1)
            self.assertRaises(ValueError, setattr, c, attr, 2)
            self.assertRaises(TypeError, setattr, c, attr, [1,2,3])
            ikiwa HAVE_CONFIG_64:
                self.assertRaises(ValueError, setattr, c, attr, 2**32)
                self.assertRaises(ValueError, setattr, c, attr, 2**32+1)

        # Invalid local context
        self.assertRaises(TypeError, exec, 'ukijumuisha localcontext("xyz"): pita',
                          locals())
        self.assertRaises(TypeError, exec,
                          'ukijumuisha localcontext(context=getcontext()): pita',
                          locals())

        # setcontext
        saved_context = getcontext()
        self.assertRaises(TypeError, setcontext, "xyz")
        setcontext(saved_context)

    eleza test_rounding_strings_interned(self):

        self.assertIs(C.ROUND_UP, P.ROUND_UP)
        self.assertIs(C.ROUND_DOWN, P.ROUND_DOWN)
        self.assertIs(C.ROUND_CEILING, P.ROUND_CEILING)
        self.assertIs(C.ROUND_FLOOR, P.ROUND_FLOOR)
        self.assertIs(C.ROUND_HALF_UP, P.ROUND_HALF_UP)
        self.assertIs(C.ROUND_HALF_DOWN, P.ROUND_HALF_DOWN)
        self.assertIs(C.ROUND_HALF_EVEN, P.ROUND_HALF_EVEN)
        self.assertIs(C.ROUND_05UP, P.ROUND_05UP)

    @requires_extra_functionality
    eleza test_c_context_errors_extra(self):
        Context = C.Context
        InvalidOperation = C.InvalidOperation
        Overflow = C.Overflow
        localcontext = C.localcontext
        getcontext = C.getcontext
        setcontext = C.setcontext
        HAVE_CONFIG_64 = (C.MAX_PREC > 425000000)

        c = Context()

        # Input corner cases
        int_max = 2**63-1 ikiwa HAVE_CONFIG_64 isipokua 2**31-1

        # OverflowError, general ValueError
        self.assertRaises(OverflowError, setattr, c, '_allcr', int_max+1)
        self.assertRaises(OverflowError, setattr, c, '_allcr', -int_max-2)
        ikiwa sys.platform != 'win32':
            self.assertRaises(ValueError, setattr, c, '_allcr', int_max)
            self.assertRaises(ValueError, setattr, c, '_allcr', -int_max-1)

        # OverflowError, general TypeError
        kila attr kwenye ('_flags', '_traps'):
            self.assertRaises(OverflowError, setattr, c, attr, int_max+1)
            self.assertRaises(OverflowError, setattr, c, attr, -int_max-2)
            ikiwa sys.platform != 'win32':
                self.assertRaises(TypeError, setattr, c, attr, int_max)
                self.assertRaises(TypeError, setattr, c, attr, -int_max-1)

        # _allcr
        self.assertRaises(ValueError, setattr, c, '_allcr', -1)
        self.assertRaises(ValueError, setattr, c, '_allcr', 2)
        self.assertRaises(TypeError, setattr, c, '_allcr', [1,2,3])
        ikiwa HAVE_CONFIG_64:
            self.assertRaises(ValueError, setattr, c, '_allcr', 2**32)
            self.assertRaises(ValueError, setattr, c, '_allcr', 2**32+1)

        # _flags, _traps
        kila attr kwenye ['_flags', '_traps']:
            self.assertRaises(TypeError, setattr, c, attr, 999999)
            self.assertRaises(TypeError, setattr, c, attr, 'x')

    eleza test_c_valid_context(self):
        # These tests are kila code coverage kwenye _decimal.
        DefaultContext = C.DefaultContext
        Clamped = C.Clamped
        Underflow = C.Underflow
        Inexact = C.Inexact
        Rounded = C.Rounded
        Subnormal = C.Subnormal

        c = DefaultContext.copy()

        # Exercise all getters na setters
        c.prec = 34
        c.rounding = ROUND_HALF_UP
        c.Emax = 3000
        c.Emin = -3000
        c.capitals = 1
        c.clamp = 0

        self.assertEqual(c.prec, 34)
        self.assertEqual(c.rounding, ROUND_HALF_UP)
        self.assertEqual(c.Emin, -3000)
        self.assertEqual(c.Emax, 3000)
        self.assertEqual(c.capitals, 1)
        self.assertEqual(c.clamp, 0)

        self.assertEqual(c.Etiny(), -3033)
        self.assertEqual(c.Etop(), 2967)

        # Exercise all unsafe setters
        ikiwa C.MAX_PREC == 425000000:
            c._unsafe_setprec(999999999)
            c._unsafe_setemax(999999999)
            c._unsafe_setemin(-999999999)
            self.assertEqual(c.prec, 999999999)
            self.assertEqual(c.Emax, 999999999)
            self.assertEqual(c.Emin, -999999999)

    @requires_extra_functionality
    eleza test_c_valid_context_extra(self):
        DefaultContext = C.DefaultContext

        c = DefaultContext.copy()
        self.assertEqual(c._allcr, 1)
        c._allcr = 0
        self.assertEqual(c._allcr, 0)

    eleza test_c_round(self):
        # Restricted input.
        Decimal = C.Decimal
        InvalidOperation = C.InvalidOperation
        localcontext = C.localcontext
        MAX_EMAX = C.MAX_EMAX
        MIN_ETINY = C.MIN_ETINY
        int_max = 2**63-1 ikiwa C.MAX_PREC > 425000000 isipokua 2**31-1

        ukijumuisha localcontext() kama c:
            c.traps[InvalidOperation] = Kweli
            self.assertRaises(InvalidOperation, Decimal("1.23").__round__,
                              -int_max-1)
            self.assertRaises(InvalidOperation, Decimal("1.23").__round__,
                              int_max)
            self.assertRaises(InvalidOperation, Decimal("1").__round__,
                              int(MAX_EMAX+1))
            self.assertRaises(C.InvalidOperation, Decimal("1").__round__,
                              -int(MIN_ETINY-1))
            self.assertRaises(OverflowError, Decimal("1.23").__round__,
                              -int_max-2)
            self.assertRaises(OverflowError, Decimal("1.23").__round__,
                              int_max+1)

    eleza test_c_format(self):
        # Restricted input
        Decimal = C.Decimal
        HAVE_CONFIG_64 = (C.MAX_PREC > 425000000)

        self.assertRaises(TypeError, Decimal(1).__format__, "=10.10", [], 9)
        self.assertRaises(TypeError, Decimal(1).__format__, "=10.10", 9)
        self.assertRaises(TypeError, Decimal(1).__format__, [])

        self.assertRaises(ValueError, Decimal(1).__format__, "<>=10.10")
        maxsize = 2**63-1 ikiwa HAVE_CONFIG_64 isipokua 2**31-1
        self.assertRaises(ValueError, Decimal("1.23456789").__format__,
                          "=%d.1" % maxsize)

    eleza test_c_integral(self):
        Decimal = C.Decimal
        Inexact = C.Inexact
        localcontext = C.localcontext

        x = Decimal(10)
        self.assertEqual(x.to_integral(), 10)
        self.assertRaises(TypeError, x.to_integral, '10')
        self.assertRaises(TypeError, x.to_integral, 10, 'x')
        self.assertRaises(TypeError, x.to_integral, 10)

        self.assertEqual(x.to_integral_value(), 10)
        self.assertRaises(TypeError, x.to_integral_value, '10')
        self.assertRaises(TypeError, x.to_integral_value, 10, 'x')
        self.assertRaises(TypeError, x.to_integral_value, 10)

        self.assertEqual(x.to_integral_exact(), 10)
        self.assertRaises(TypeError, x.to_integral_exact, '10')
        self.assertRaises(TypeError, x.to_integral_exact, 10, 'x')
        self.assertRaises(TypeError, x.to_integral_exact, 10)

        ukijumuisha localcontext() kama c:
            x = Decimal("99999999999999999999999999.9").to_integral_value(ROUND_UP)
            self.assertEqual(x, Decimal('100000000000000000000000000'))

            x = Decimal("99999999999999999999999999.9").to_integral_exact(ROUND_UP)
            self.assertEqual(x, Decimal('100000000000000000000000000'))

            c.traps[Inexact] = Kweli
            self.assertRaises(Inexact, Decimal("999.9").to_integral_exact, ROUND_UP)

    eleza test_c_funcs(self):
        # Invalid arguments
        Decimal = C.Decimal
        InvalidOperation = C.InvalidOperation
        DivisionByZero = C.DivisionByZero
        getcontext = C.getcontext
        localcontext = C.localcontext

        self.assertEqual(Decimal('9.99e10').to_eng_string(), '99.9E+9')

        self.assertRaises(TypeError, pow, Decimal(1), 2, "3")
        self.assertRaises(TypeError, Decimal(9).number_class, "x", "y")
        self.assertRaises(TypeError, Decimal(9).same_quantum, 3, "x", "y")

        self.assertRaises(
            TypeError,
            Decimal("1.23456789").quantize, Decimal('1e-100000'), []
        )
        self.assertRaises(
            TypeError,
            Decimal("1.23456789").quantize, Decimal('1e-100000'), getcontext()
        )
        self.assertRaises(
            TypeError,
            Decimal("1.23456789").quantize, Decimal('1e-100000'), 10
        )
        self.assertRaises(
            TypeError,
            Decimal("1.23456789").quantize, Decimal('1e-100000'), ROUND_UP, 1000
        )

        ukijumuisha localcontext() kama c:
            c.clear_traps()

            # Invalid arguments
            self.assertRaises(TypeError, c.copy_sign, Decimal(1), "x", "y")
            self.assertRaises(TypeError, c.canonical, 200)
            self.assertRaises(TypeError, c.is_canonical, 200)
            self.assertRaises(TypeError, c.divmod, 9, 8, "x", "y")
            self.assertRaises(TypeError, c.same_quantum, 9, 3, "x", "y")

            self.assertEqual(str(c.canonical(Decimal(200))), '200')
            self.assertEqual(c.radix(), 10)

            c.traps[DivisionByZero] = Kweli
            self.assertRaises(DivisionByZero, Decimal(9).__divmod__, 0)
            self.assertRaises(DivisionByZero, c.divmod, 9, 0)
            self.assertKweli(c.flags[InvalidOperation])

            c.clear_flags()
            c.traps[InvalidOperation] = Kweli
            self.assertRaises(InvalidOperation, Decimal(9).__divmod__, 0)
            self.assertRaises(InvalidOperation, c.divmod, 9, 0)
            self.assertKweli(c.flags[DivisionByZero])

            c.traps[InvalidOperation] = Kweli
            c.prec = 2
            self.assertRaises(InvalidOperation, pow, Decimal(1000), 1, 501)

    eleza test_va_args_exceptions(self):
        Decimal = C.Decimal
        Context = C.Context

        x = Decimal("10001111111")

        kila attr kwenye ['exp', 'is_normal', 'is_subnormal', 'ln', 'log10',
                     'logb', 'logical_invert', 'next_minus', 'next_plus',
                     'normalize', 'number_class', 'sqrt', 'to_eng_string']:
            func = getattr(x, attr)
            self.assertRaises(TypeError, func, context="x")
            self.assertRaises(TypeError, func, "x", context=Tupu)

        kila attr kwenye ['compare', 'compare_signal', 'logical_and',
                     'logical_or', 'max', 'max_mag', 'min', 'min_mag',
                     'remainder_near', 'rotate', 'scaleb', 'shift']:
            func = getattr(x, attr)
            self.assertRaises(TypeError, func, context="x")
            self.assertRaises(TypeError, func, "x", context=Tupu)

        self.assertRaises(TypeError, x.to_integral, rounding=Tupu, context=[])
        self.assertRaises(TypeError, x.to_integral, rounding={}, context=[])
        self.assertRaises(TypeError, x.to_integral, [], [])

        self.assertRaises(TypeError, x.to_integral_value, rounding=Tupu, context=[])
        self.assertRaises(TypeError, x.to_integral_value, rounding={}, context=[])
        self.assertRaises(TypeError, x.to_integral_value, [], [])

        self.assertRaises(TypeError, x.to_integral_exact, rounding=Tupu, context=[])
        self.assertRaises(TypeError, x.to_integral_exact, rounding={}, context=[])
        self.assertRaises(TypeError, x.to_integral_exact, [], [])

        self.assertRaises(TypeError, x.fma, 1, 2, context="x")
        self.assertRaises(TypeError, x.fma, 1, 2, "x", context=Tupu)

        self.assertRaises(TypeError, x.quantize, 1, [], context=Tupu)
        self.assertRaises(TypeError, x.quantize, 1, [], rounding=Tupu)
        self.assertRaises(TypeError, x.quantize, 1, [], [])

        c = Context()
        self.assertRaises(TypeError, c.power, 1, 2, mod="x")
        self.assertRaises(TypeError, c.power, 1, "x", mod=Tupu)
        self.assertRaises(TypeError, c.power, "x", 2, mod=Tupu)

    @requires_extra_functionality
    eleza test_c_context_templates(self):
        self.assertEqual(
            C.BasicContext._traps,
            C.DecIEEEInvalidOperation|C.DecDivisionByZero|C.DecOverflow|
            C.DecUnderflow|C.DecClamped
        )
        self.assertEqual(
            C.DefaultContext._traps,
            C.DecIEEEInvalidOperation|C.DecDivisionByZero|C.DecOverflow
        )

    @requires_extra_functionality
    eleza test_c_signal_dict(self):

        # SignalDict coverage
        Context = C.Context
        DefaultContext = C.DefaultContext

        InvalidOperation = C.InvalidOperation
        DivisionByZero = C.DivisionByZero
        Overflow = C.Overflow
        Subnormal = C.Subnormal
        Underflow = C.Underflow
        Rounded = C.Rounded
        Inexact = C.Inexact
        Clamped = C.Clamped

        DecClamped = C.DecClamped
        DecInvalidOperation = C.DecInvalidOperation
        DecIEEEInvalidOperation = C.DecIEEEInvalidOperation

        eleza assertIsExclusivelySet(signal, signal_dict):
            kila sig kwenye signal_dict:
                ikiwa sig == signal:
                    self.assertKweli(signal_dict[sig])
                isipokua:
                    self.assertUongo(signal_dict[sig])

        c = DefaultContext.copy()

        # Signal dict methods
        self.assertKweli(Overflow kwenye c.traps)
        c.clear_traps()
        kila k kwenye c.traps.keys():
            c.traps[k] = Kweli
        kila v kwenye c.traps.values():
            self.assertKweli(v)
        c.clear_traps()
        kila k, v kwenye c.traps.items():
            self.assertUongo(v)

        self.assertUongo(c.flags.get(Overflow))
        self.assertIs(c.flags.get("x"), Tupu)
        self.assertEqual(c.flags.get("x", "y"), "y")
        self.assertRaises(TypeError, c.flags.get, "x", "y", "z")

        self.assertEqual(len(c.flags), len(c.traps))
        s = sys.getsizeof(c.flags)
        s = sys.getsizeof(c.traps)
        s = c.flags.__repr__()

        # Set flags/traps.
        c.clear_flags()
        c._flags = DecClamped
        self.assertKweli(c.flags[Clamped])

        c.clear_traps()
        c._traps = DecInvalidOperation
        self.assertKweli(c.traps[InvalidOperation])

        # Set flags/traps kutoka dictionary.
        c.clear_flags()
        d = c.flags.copy()
        d[DivisionByZero] = Kweli
        c.flags = d
        assertIsExclusivelySet(DivisionByZero, c.flags)

        c.clear_traps()
        d = c.traps.copy()
        d[Underflow] = Kweli
        c.traps = d
        assertIsExclusivelySet(Underflow, c.traps)

        # Random constructors
        IntSignals = {
          Clamped: C.DecClamped,
          Rounded: C.DecRounded,
          Inexact: C.DecInexact,
          Subnormal: C.DecSubnormal,
          Underflow: C.DecUnderflow,
          Overflow: C.DecOverflow,
          DivisionByZero: C.DecDivisionByZero,
          InvalidOperation: C.DecIEEEInvalidOperation
        }
        IntCond = [
          C.DecDivisionImpossible, C.DecDivisionUndefined, C.DecFpuError,
          C.DecInvalidContext, C.DecInvalidOperation, C.DecMallocError,
          C.DecConversionSyntax,
        ]

        lim = len(OrderedSignals[C])
        kila r kwenye range(lim):
            kila t kwenye range(lim):
                kila round kwenye RoundingModes:
                    flags = random.sample(OrderedSignals[C], r)
                    traps = random.sample(OrderedSignals[C], t)
                    prec = random.randrange(1, 10000)
                    emin = random.randrange(-10000, 0)
                    emax = random.randrange(0, 10000)
                    clamp = random.randrange(0, 2)
                    caps = random.randrange(0, 2)
                    cr = random.randrange(0, 2)
                    c = Context(prec=prec, rounding=round, Emin=emin, Emax=emax,
                                capitals=caps, clamp=clamp, flags=list(flags),
                                traps=list(traps))

                    self.assertEqual(c.prec, prec)
                    self.assertEqual(c.rounding, round)
                    self.assertEqual(c.Emin, emin)
                    self.assertEqual(c.Emax, emax)
                    self.assertEqual(c.capitals, caps)
                    self.assertEqual(c.clamp, clamp)

                    f = 0
                    kila x kwenye flags:
                        f |= IntSignals[x]
                    self.assertEqual(c._flags, f)

                    f = 0
                    kila x kwenye traps:
                        f |= IntSignals[x]
                    self.assertEqual(c._traps, f)

        kila cond kwenye IntCond:
            c._flags = cond
            self.assertKweli(c._flags&DecIEEEInvalidOperation)
            assertIsExclusivelySet(InvalidOperation, c.flags)

        kila cond kwenye IntCond:
            c._traps = cond
            self.assertKweli(c._traps&DecIEEEInvalidOperation)
            assertIsExclusivelySet(InvalidOperation, c.traps)

    eleza test_invalid_override(self):
        Decimal = C.Decimal

        jaribu:
            kutoka locale agiza CHAR_MAX
        tatizo ImportError:
            self.skipTest('locale.CHAR_MAX sio available')

        eleza make_grouping(lst):
            rudisha ''.join([chr(x) kila x kwenye lst])

        eleza get_fmt(x, override=Tupu, fmt='n'):
            rudisha Decimal(x).__format__(fmt, override)

        invalid_grouping = {
            'decimal_point' : ',',
            'grouping' : make_grouping([255, 255, 0]),
            'thousands_sep' : ','
        }
        invalid_dot = {
            'decimal_point' : 'xxxxx',
            'grouping' : make_grouping([3, 3, 0]),
            'thousands_sep' : ','
        }
        invalid_sep = {
            'decimal_point' : '.',
            'grouping' : make_grouping([3, 3, 0]),
            'thousands_sep' : 'yyyyy'
        }

        ikiwa CHAR_MAX == 127: # negative grouping kwenye override
            self.assertRaises(ValueError, get_fmt, 12345,
                              invalid_grouping, 'g')

        self.assertRaises(ValueError, get_fmt, 12345, invalid_dot, 'g')
        self.assertRaises(ValueError, get_fmt, 12345, invalid_sep, 'g')

    eleza test_exact_conversion(self):
        Decimal = C.Decimal
        localcontext = C.localcontext
        InvalidOperation = C.InvalidOperation

        ukijumuisha localcontext() kama c:

            c.traps[InvalidOperation] = Kweli

            # Clamped
            x = "0e%d" % sys.maxsize
            self.assertRaises(InvalidOperation, Decimal, x)

            x = "0e%d" % (-sys.maxsize-1)
            self.assertRaises(InvalidOperation, Decimal, x)

            # Overflow
            x = "1e%d" % sys.maxsize
            self.assertRaises(InvalidOperation, Decimal, x)

            # Underflow
            x = "1e%d" % (-sys.maxsize-1)
            self.assertRaises(InvalidOperation, Decimal, x)

    eleza test_from_tuple(self):
        Decimal = C.Decimal
        localcontext = C.localcontext
        InvalidOperation = C.InvalidOperation
        Overflow = C.Overflow
        Underflow = C.Underflow

        ukijumuisha localcontext() kama c:

            c.traps[InvalidOperation] = Kweli
            c.traps[Overflow] = Kweli
            c.traps[Underflow] = Kweli

            # SSIZE_MAX
            x = (1, (), sys.maxsize)
            self.assertEqual(str(c.create_decimal(x)), '-0E+999999')
            self.assertRaises(InvalidOperation, Decimal, x)

            x = (1, (0, 1, 2), sys.maxsize)
            self.assertRaises(Overflow, c.create_decimal, x)
            self.assertRaises(InvalidOperation, Decimal, x)

            # SSIZE_MIN
            x = (1, (), -sys.maxsize-1)
            self.assertEqual(str(c.create_decimal(x)), '-0E-1000007')
            self.assertRaises(InvalidOperation, Decimal, x)

            x = (1, (0, 1, 2), -sys.maxsize-1)
            self.assertRaises(Underflow, c.create_decimal, x)
            self.assertRaises(InvalidOperation, Decimal, x)

            # OverflowError
            x = (1, (), sys.maxsize+1)
            self.assertRaises(OverflowError, c.create_decimal, x)
            self.assertRaises(OverflowError, Decimal, x)

            x = (1, (), -sys.maxsize-2)
            self.assertRaises(OverflowError, c.create_decimal, x)
            self.assertRaises(OverflowError, Decimal, x)

            # Specials
            x = (1, (), "N")
            self.assertEqual(str(Decimal(x)), '-sNaN')
            x = (1, (0,), "N")
            self.assertEqual(str(Decimal(x)), '-sNaN')
            x = (1, (0, 1), "N")
            self.assertEqual(str(Decimal(x)), '-sNaN1')

    eleza test_sizeof(self):
        Decimal = C.Decimal
        HAVE_CONFIG_64 = (C.MAX_PREC > 425000000)

        self.assertGreater(Decimal(0).__sizeof__(), 0)
        ikiwa HAVE_CONFIG_64:
            x = Decimal(10**(19*24)).__sizeof__()
            y = Decimal(10**(19*25)).__sizeof__()
            self.assertEqual(y, x+8)
        isipokua:
            x = Decimal(10**(9*24)).__sizeof__()
            y = Decimal(10**(9*25)).__sizeof__()
            self.assertEqual(y, x+4)

    eleza test_internal_use_of_overridden_methods(self):
        Decimal = C.Decimal

        # Unsound subtyping
        kundi X(float):
            eleza as_integer_ratio(self):
                rudisha 1
            eleza __abs__(self):
                rudisha self

        kundi Y(float):
            eleza __abs__(self):
                rudisha [1]*200

        kundi I(int):
            eleza bit_length(self):
                rudisha [1]*200

        kundi Z(float):
            eleza as_integer_ratio(self):
                rudisha (I(1), I(1))
            eleza __abs__(self):
                rudisha self

        kila cls kwenye X, Y, Z:
            self.assertEqual(Decimal.from_float(cls(101.1)),
                             Decimal.from_float(101.1))

@requires_docstrings
@unittest.skipUnless(C, "test requires C version")
kundi SignatureTest(unittest.TestCase):
    """Function signatures"""

    eleza test_inspect_module(self):
        kila attr kwenye dir(P):
            ikiwa attr.startswith('_'):
                endelea
            p_func = getattr(P, attr)
            c_func = getattr(C, attr)
            ikiwa (attr == 'Decimal' ama attr == 'Context' ama
                inspect.isfunction(p_func)):
                p_sig = inspect.signature(p_func)
                c_sig = inspect.signature(c_func)

                # parameter names:
                c_names = list(c_sig.parameters.keys())
                p_names = [x kila x kwenye p_sig.parameters.keys() ikiwa not
                           x.startswith('_')]

                self.assertEqual(c_names, p_names,
                                 msg="parameter name mismatch kwenye %s" % p_func)

                c_kind = [x.kind kila x kwenye c_sig.parameters.values()]
                p_kind = [x[1].kind kila x kwenye p_sig.parameters.items() ikiwa not
                          x[0].startswith('_')]

                # parameters:
                ikiwa attr != 'setcontext':
                    self.assertEqual(c_kind, p_kind,
                                     msg="parameter kind mismatch kwenye %s" % p_func)

    eleza test_inspect_types(self):

        POS = inspect._ParameterKind.POSITIONAL_ONLY
        POS_KWD = inspect._ParameterKind.POSITIONAL_OR_KEYWORD

        # Type heuristic (type annotations would help!):
        pdict = {C: {'other': C.Decimal(1),
                     'third': C.Decimal(1),
                     'x': C.Decimal(1),
                     'y': C.Decimal(1),
                     'z': C.Decimal(1),
                     'a': C.Decimal(1),
                     'b': C.Decimal(1),
                     'c': C.Decimal(1),
                     'exp': C.Decimal(1),
                     'modulo': C.Decimal(1),
                     'num': "1",
                     'f': 1.0,
                     'rounding': C.ROUND_HALF_UP,
                     'context': C.getcontext()},
                 P: {'other': P.Decimal(1),
                     'third': P.Decimal(1),
                     'a': P.Decimal(1),
                     'b': P.Decimal(1),
                     'c': P.Decimal(1),
                     'exp': P.Decimal(1),
                     'modulo': P.Decimal(1),
                     'num': "1",
                     'f': 1.0,
                     'rounding': P.ROUND_HALF_UP,
                     'context': P.getcontext()}}

        eleza mkargs(module, sig):
            args = []
            kwargs = {}
            kila name, param kwenye sig.parameters.items():
                ikiwa name == 'self': endelea
                ikiwa param.kind == POS:
                    args.append(pdict[module][name])
                lasivyo param.kind == POS_KWD:
                    kwargs[name] = pdict[module][name]
                isipokua:
                    ashiria TestFailed("unexpected parameter kind")
            rudisha args, kwargs

        eleza tr(s):
            """The C Context docstrings use 'x' kwenye order to prevent confusion
               ukijumuisha the article 'a' kwenye the descriptions."""
            ikiwa s == 'x': rudisha 'a'
            ikiwa s == 'y': rudisha 'b'
            ikiwa s == 'z': rudisha 'c'
            rudisha s

        eleza doit(ty):
            p_type = getattr(P, ty)
            c_type = getattr(C, ty)
            kila attr kwenye dir(p_type):
                ikiwa attr.startswith('_'):
                    endelea
                p_func = getattr(p_type, attr)
                c_func = getattr(c_type, attr)
                ikiwa inspect.isfunction(p_func):
                    p_sig = inspect.signature(p_func)
                    c_sig = inspect.signature(c_func)

                    # parameter names:
                    p_names = list(p_sig.parameters.keys())
                    c_names = [tr(x) kila x kwenye c_sig.parameters.keys()]

                    self.assertEqual(c_names, p_names,
                                     msg="parameter name mismatch kwenye %s" % p_func)

                    p_kind = [x.kind kila x kwenye p_sig.parameters.values()]
                    c_kind = [x.kind kila x kwenye c_sig.parameters.values()]

                    # 'self' parameter:
                    self.assertIs(p_kind[0], POS_KWD)
                    self.assertIs(c_kind[0], POS)

                    # remaining parameters:
                    ikiwa ty == 'Decimal':
                        self.assertEqual(c_kind[1:], p_kind[1:],
                                         msg="parameter kind mismatch kwenye %s" % p_func)
                    isipokua: # Context methods are positional only kwenye the C version.
                        self.assertEqual(len(c_kind), len(p_kind),
                                         msg="parameter kind mismatch kwenye %s" % p_func)

                    # Run the function:
                    args, kwds = mkargs(C, c_sig)
                    jaribu:
                        getattr(c_type(9), attr)(*args, **kwds)
                    tatizo Exception kama err:
                        ashiria TestFailed("invalid signature kila %s: %s %s" % (c_func, args, kwds))

                    args, kwds = mkargs(P, p_sig)
                    jaribu:
                        getattr(p_type(9), attr)(*args, **kwds)
                    tatizo Exception kama err:
                        ashiria TestFailed("invalid signature kila %s: %s %s" % (p_func, args, kwds))

        doit('Decimal')
        doit('Context')


all_tests = [
  CExplicitConstructionTest, PyExplicitConstructionTest,
  CImplicitConstructionTest, PyImplicitConstructionTest,
  CFormatTest,               PyFormatTest,
  CArithmeticOperatorsTest,  PyArithmeticOperatorsTest,
  CThreadingTest,            PyThreadingTest,
  CUsabilityTest,            PyUsabilityTest,
  CPythonAPItests,           PyPythonAPItests,
  CContextAPItests,          PyContextAPItests,
  CContextWithStatement,     PyContextWithStatement,
  CContextFlags,             PyContextFlags,
  CSpecialContexts,          PySpecialContexts,
  CContextInputValidation,   PyContextInputValidation,
  CContextSubclassing,       PyContextSubclassing,
  CCoverage,                 PyCoverage,
  CFunctionality,            PyFunctionality,
  CWhitebox,                 PyWhitebox,
  CIBMTestCases,             PyIBMTestCases,
]

# Delete C tests ikiwa _decimal.so ni sio present.
ikiwa sio C:
    all_tests = all_tests[1::2]
isipokua:
    all_tests.insert(0, CheckAttributes)
    all_tests.insert(1, SignatureTest)


eleza test_main(arith=Tupu, verbose=Tupu, todo_tests=Tupu, debug=Tupu):
    """ Execute the tests.

    Runs all arithmetic tests ikiwa arith ni Kweli ama ikiwa the "decimal" resource
    ni enabled kwenye regrtest.py
    """

    init(C)
    init(P)
    global TEST_ALL, DEBUG
    TEST_ALL = arith ikiwa arith ni sio Tupu isipokua is_resource_enabled('decimal')
    DEBUG = debug

    ikiwa todo_tests ni Tupu:
        test_classes = all_tests
    isipokua:
        test_classes = [CIBMTestCases, PyIBMTestCases]

    # Dynamically build custom test definition kila each file kwenye the test
    # directory na add the definitions to the DecimalTest class.  This
    # procedure insures that new files do sio get skipped.
    kila filename kwenye os.listdir(directory):
        ikiwa '.decTest' haiko kwenye filename ama filename.startswith("."):
            endelea
        head, tail = filename.split('.')
        ikiwa todo_tests ni sio Tupu na head haiko kwenye todo_tests:
            endelea
        tester = lambda self, f=filename: self.eval_file(directory + f)
        setattr(CIBMTestCases, 'test_' + head, tester)
        setattr(PyIBMTestCases, 'test_' + head, tester)
        toa filename, head, tail, tester


    jaribu:
        run_unittest(*test_classes)
        ikiwa todo_tests ni Tupu:
            kutoka doctest agiza IGNORE_EXCEPTION_DETAIL
            savedecimal = sys.modules['decimal']
            ikiwa C:
                sys.modules['decimal'] = C
                run_doctest(C, verbose, optionflags=IGNORE_EXCEPTION_DETAIL)
            sys.modules['decimal'] = P
            run_doctest(P, verbose)
            sys.modules['decimal'] = savedecimal
    mwishowe:
        ikiwa C: C.setcontext(ORIGINAL_CONTEXT[C])
        P.setcontext(ORIGINAL_CONTEXT[P])
        ikiwa sio C:
            warnings.warn('C tests skipped: no module named _decimal.',
                          UserWarning)
        ikiwa sio orig_sys_decimal ni sys.modules['decimal']:
            ashiria TestFailed("Internal error: unbalanced number of changes to "
                             "sys.modules['decimal'].")


ikiwa __name__ == '__main__':
    agiza optparse
    p = optparse.OptionParser("test_decimal.py [--debug] [{--skip | test1 [test2 [...]]}]")
    p.add_option('--debug', '-d', action='store_true', help='shows the test number na context before each test')
    p.add_option('--skip',  '-s', action='store_true', help='skip over 90% of the arithmetic tests')
    (opt, args) = p.parse_args()

    ikiwa opt.skip:
        test_main(arith=Uongo, verbose=Kweli)
    lasivyo args:
        test_main(arith=Kweli, verbose=Kweli, todo_tests=args, debug=opt.debug)
    isipokua:
        test_main(arith=Kweli, verbose=Kweli)
