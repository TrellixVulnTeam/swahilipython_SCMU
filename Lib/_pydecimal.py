# Copyright (c) 2004 Python Software Foundation.
# All rights reserved.

# Written by Eric Price <eprice at tjhsst.edu>
#    na Facundo Batista <facundo at taniquetil.com.ar>
#    na Raymond Hettinger <python at rcn.com>
#    na Aahz <aahz at pobox.com>
#    na Tim Peters

# This module should be kept kwenye sync ukijumuisha the latest updates of the
# IBM specification as it evolves.  Those updates will be treated
# as bug fixes (deviation kutoka the spec ni a compatibility, usability
# bug) na will be backported.  At this point the spec ni stabilizing
# na the updates are becoming fewer, smaller, na less significant.

"""
This ni an implementation of decimal floating point arithmetic based on
the General Decimal Arithmetic Specification:

    http://speleotrove.com/decimal/decarith.html

and IEEE standard 854-1987:

    http://en.wikipedia.org/wiki/IEEE_854-1987

Decimal floating point has finite precision ukijumuisha arbitrarily large bounds.

The purpose of this module ni to support arithmetic using familiar
"schoolhouse" rules na to avoid some of the tricky representation
issues associated ukijumuisha binary floating point.  The package ni especially
useful kila financial applications ama kila contexts where users have
expectations that are at odds ukijumuisha binary floating point (kila instance,
in binary floating point, 1.00 % 0.1 gives 0.09999999999999995 instead
of 0.0; Decimal('1.00') % Decimal('0.1') returns the expected
Decimal('0.00')).

Here are some examples of using the decimal module:

>>> kutoka decimal agiza *
>>> setcontext(ExtendedContext)
>>> Decimal(0)
Decimal('0')
>>> Decimal('1')
Decimal('1')
>>> Decimal('-.0123')
Decimal('-0.0123')
>>> Decimal(123456)
Decimal('123456')
>>> Decimal('123.45e12345678')
Decimal('1.2345E+12345680')
>>> Decimal('1.33') + Decimal('1.27')
Decimal('2.60')
>>> Decimal('12.34') + Decimal('3.87') - Decimal('18.41')
Decimal('-2.20')
>>> dig = Decimal(1)
>>> andika(dig / Decimal(3))
0.333333333
>>> getcontext().prec = 18
>>> andika(dig / Decimal(3))
0.333333333333333333
>>> andika(dig.sqrt())
1
>>> andika(Decimal(3).sqrt())
1.73205080756887729
>>> andika(Decimal(3) ** 123)
4.85192780976896427E+58
>>> inf = Decimal(1) / Decimal(0)
>>> andika(inf)
Infinity
>>> neginf = Decimal(-1) / Decimal(0)
>>> andika(neginf)
-Infinity
>>> andika(neginf + inf)
NaN
>>> andika(neginf * inf)
-Infinity
>>> andika(dig / 0)
Infinity
>>> getcontext().traps[DivisionByZero] = 1
>>> andika(dig / 0)
Traceback (most recent call last):
  ...
  ...
  ...
decimal.DivisionByZero: x / 0
>>> c = Context()
>>> c.traps[InvalidOperation] = 0
>>> andika(c.flags[InvalidOperation])
0
>>> c.divide(Decimal(0), Decimal(0))
Decimal('NaN')
>>> c.traps[InvalidOperation] = 1
>>> andika(c.flags[InvalidOperation])
1
>>> c.flags[InvalidOperation] = 0
>>> andika(c.flags[InvalidOperation])
0
>>> andika(c.divide(Decimal(0), Decimal(0)))
Traceback (most recent call last):
  ...
  ...
  ...
decimal.InvalidOperation: 0 / 0
>>> andika(c.flags[InvalidOperation])
1
>>> c.flags[InvalidOperation] = 0
>>> c.traps[InvalidOperation] = 0
>>> andika(c.divide(Decimal(0), Decimal(0)))
NaN
>>> andika(c.flags[InvalidOperation])
1
>>>
"""

__all__ = [
    # Two major classes
    'Decimal', 'Context',

    # Named tuple representation
    'DecimalTuple',

    # Contexts
    'DefaultContext', 'BasicContext', 'ExtendedContext',

    # Exceptions
    'DecimalException', 'Clamped', 'InvalidOperation', 'DivisionByZero',
    'Inexact', 'Rounded', 'Subnormal', 'Overflow', 'Underflow',
    'FloatOperation',

    # Exceptional conditions that trigger InvalidOperation
    'DivisionImpossible', 'InvalidContext', 'ConversionSyntax', 'DivisionUndefined',

    # Constants kila use kwenye setting up contexts
    'ROUND_DOWN', 'ROUND_HALF_UP', 'ROUND_HALF_EVEN', 'ROUND_CEILING',
    'ROUND_FLOOR', 'ROUND_UP', 'ROUND_HALF_DOWN', 'ROUND_05UP',

    # Functions kila manipulating contexts
    'setcontext', 'getcontext', 'localcontext',

    # Limits kila the C version kila compatibility
    'MAX_PREC',  'MAX_EMAX', 'MIN_EMIN', 'MIN_ETINY',

    # C version: compile time choice that enables the thread local context
    'HAVE_THREADS'
]

__xname__ = __name__    # sys.modules lookup (--without-threads)
__name__ = 'decimal'    # For pickling
__version__ = '1.70'    # Highest version of the spec this complies with
                        # See http://speleotrove.com/decimal/
__libmpdec_version__ = "2.4.2" # compatible libmpdec version

agiza math as _math
agiza numbers as _numbers
agiza sys

jaribu:
    kutoka collections agiza namedtuple as _namedtuple
    DecimalTuple = _namedtuple('DecimalTuple', 'sign digits exponent')
except ImportError:
    DecimalTuple = lambda *args: args

# Rounding
ROUND_DOWN = 'ROUND_DOWN'
ROUND_HALF_UP = 'ROUND_HALF_UP'
ROUND_HALF_EVEN = 'ROUND_HALF_EVEN'
ROUND_CEILING = 'ROUND_CEILING'
ROUND_FLOOR = 'ROUND_FLOOR'
ROUND_UP = 'ROUND_UP'
ROUND_HALF_DOWN = 'ROUND_HALF_DOWN'
ROUND_05UP = 'ROUND_05UP'

# Compatibility ukijumuisha the C version
HAVE_THREADS = Kweli
ikiwa sys.maxsize == 2**63-1:
    MAX_PREC = 999999999999999999
    MAX_EMAX = 999999999999999999
    MIN_EMIN = -999999999999999999
isipokua:
    MAX_PREC = 425000000
    MAX_EMAX = 425000000
    MIN_EMIN = -425000000

MIN_ETINY = MIN_EMIN - (MAX_PREC-1)

# Errors

kundi DecimalException(ArithmeticError):
    """Base exception class.

    Used exceptions derive kutoka this.
    If an exception derives kutoka another exception besides this (such as
    Underflow (Inexact, Rounded, Subnormal) that indicates that it ni only
    called ikiwa the others are present.  This isn't actually used for
    anything, though.

    handle  -- Called when context._raise_error ni called na the
               trap_enabler ni sio set.  First argument ni self, second ni the
               context.  More arguments can be given, those being after
               the explanation kwenye _raise_error (For example,
               context._raise_error(NewError, '(-x)!', self._sign) would
               call NewError().handle(context, self._sign).)

    To define a new exception, it should be sufficient to have it derive
    kutoka DecimalException.
    """
    eleza handle(self, context, *args):
        pass


kundi Clamped(DecimalException):
    """Exponent of a 0 changed to fit bounds.

    This occurs na signals clamped ikiwa the exponent of a result has been
    altered kwenye order to fit the constraints of a specific concrete
    representation.  This may occur when the exponent of a zero result would
    be outside the bounds of a representation, ama when a large normal
    number would have an encoded exponent that cannot be represented.  In
    this latter case, the exponent ni reduced to fit na the corresponding
    number of zero digits are appended to the coefficient ("fold-down").
    """

kundi InvalidOperation(DecimalException):
    """An invalid operation was performed.

    Various bad things cause this:

    Something creates a signaling NaN
    -INF + INF
    0 * (+-)INF
    (+-)INF / (+-)INF
    x % 0
    (+-)INF % x
    x._rescale( non-integer )
    sqrt(-x) , x > 0
    0 ** 0
    x ** (non-integer)
    x ** (+-)INF
    An operand ni invalid

    The result of the operation after these ni a quiet positive NaN,
    except when the cause ni a signaling NaN, kwenye which case the result is
    also a quiet NaN, but ukijumuisha the original sign, na an optional
    diagnostic information.
    """
    eleza handle(self, context, *args):
        ikiwa args:
            ans = _dec_from_triple(args[0]._sign, args[0]._int, 'n', Kweli)
            rudisha ans._fix_nan(context)
        rudisha _NaN

kundi ConversionSyntax(InvalidOperation):
    """Trying to convert badly formed string.

    This occurs na signals invalid-operation ikiwa a string ni being
    converted to a number na it does sio conform to the numeric string
    syntax.  The result ni [0,qNaN].
    """
    eleza handle(self, context, *args):
        rudisha _NaN

kundi DivisionByZero(DecimalException, ZeroDivisionError):
    """Division by 0.

    This occurs na signals division-by-zero ikiwa division of a finite number
    by zero was attempted (during a divide-integer ama divide operation, ama a
    power operation ukijumuisha negative right-hand operand), na the dividend was
    sio zero.

    The result of the operation ni [sign,inf], where sign ni the exclusive
    ama of the signs of the operands kila divide, ama ni 1 kila an odd power of
    -0, kila power.
    """

    eleza handle(self, context, sign, *args):
        rudisha _SignedInfinity[sign]

kundi DivisionImpossible(InvalidOperation):
    """Cannot perform the division adequately.

    This occurs na signals invalid-operation ikiwa the integer result of a
    divide-integer ama remainder operation had too many digits (would be
    longer than precision).  The result ni [0,qNaN].
    """

    eleza handle(self, context, *args):
        rudisha _NaN

kundi DivisionUndefined(InvalidOperation, ZeroDivisionError):
    """Undefined result of division.

    This occurs na signals invalid-operation ikiwa division by zero was
    attempted (during a divide-integer, divide, ama remainder operation), and
    the dividend ni also zero.  The result ni [0,qNaN].
    """

    eleza handle(self, context, *args):
        rudisha _NaN

kundi Inexact(DecimalException):
    """Had to round, losing information.

    This occurs na signals inexact whenever the result of an operation is
    sio exact (that is, it needed to be rounded na any discarded digits
    were non-zero), ama ikiwa an overflow ama underflow condition occurs.  The
    result kwenye all cases ni unchanged.

    The inexact signal may be tested (or trapped) to determine ikiwa a given
    operation (or sequence of operations) was inexact.
    """

kundi InvalidContext(InvalidOperation):
    """Invalid context.  Unknown rounding, kila example.

    This occurs na signals invalid-operation ikiwa an invalid context was
    detected during an operation.  This can occur ikiwa contexts are sio checked
    on creation na either the precision exceeds the capability of the
    underlying concrete representation ama an unknown ama unsupported rounding
    was specified.  These aspects of the context need only be checked when
    the values are required to be used.  The result ni [0,qNaN].
    """

    eleza handle(self, context, *args):
        rudisha _NaN

kundi Rounded(DecimalException):
    """Number got rounded (not  necessarily changed during rounding).

    This occurs na signals rounded whenever the result of an operation is
    rounded (that is, some zero ama non-zero digits were discarded kutoka the
    coefficient), ama ikiwa an overflow ama underflow condition occurs.  The
    result kwenye all cases ni unchanged.

    The rounded signal may be tested (or trapped) to determine ikiwa a given
    operation (or sequence of operations) caused a loss of precision.
    """

kundi Subnormal(DecimalException):
    """Exponent < Emin before rounding.

    This occurs na signals subnormal whenever the result of a conversion or
    operation ni subnormal (that is, its adjusted exponent ni less than
    Emin, before any rounding).  The result kwenye all cases ni unchanged.

    The subnormal signal may be tested (or trapped) to determine ikiwa a given
    ama operation (or sequence of operations) yielded a subnormal result.
    """

kundi Overflow(Inexact, Rounded):
    """Numerical overflow.

    This occurs na signals overflow ikiwa the adjusted exponent of a result
    (kutoka a conversion ama kutoka an operation that ni sio an attempt to divide
    by zero), after rounding, would be greater than the largest value that
    can be handled by the implementation (the value Emax).

    The result depends on the rounding mode:

    For round-half-up na round-half-even (and kila round-half-down and
    round-up, ikiwa implemented), the result of the operation ni [sign,inf],
    where sign ni the sign of the intermediate result.  For round-down, the
    result ni the largest finite number that can be represented kwenye the
    current precision, ukijumuisha the sign of the intermediate result.  For
    round-ceiling, the result ni the same as kila round-down ikiwa the sign of
    the intermediate result ni 1, ama ni [0,inf] otherwise.  For round-floor,
    the result ni the same as kila round-down ikiwa the sign of the intermediate
    result ni 0, ama ni [1,inf] otherwise.  In all cases, Inexact na Rounded
    will also be raised.
    """

    eleza handle(self, context, sign, *args):
        ikiwa context.rounding kwenye (ROUND_HALF_UP, ROUND_HALF_EVEN,
                                ROUND_HALF_DOWN, ROUND_UP):
            rudisha _SignedInfinity[sign]
        ikiwa sign == 0:
            ikiwa context.rounding == ROUND_CEILING:
                rudisha _SignedInfinity[sign]
            rudisha _dec_from_triple(sign, '9'*context.prec,
                            context.Emax-context.prec+1)
        ikiwa sign == 1:
            ikiwa context.rounding == ROUND_FLOOR:
                rudisha _SignedInfinity[sign]
            rudisha _dec_from_triple(sign, '9'*context.prec,
                             context.Emax-context.prec+1)


kundi Underflow(Inexact, Rounded, Subnormal):
    """Numerical underflow ukijumuisha result rounded to 0.

    This occurs na signals underflow ikiwa a result ni inexact na the
    adjusted exponent of the result would be smaller (more negative) than
    the smallest value that can be handled by the implementation (the value
    Emin).  That is, the result ni both inexact na subnormal.

    The result after an underflow will be a subnormal number rounded, if
    necessary, so that its exponent ni sio less than Etiny.  This may result
    kwenye 0 ukijumuisha the sign of the intermediate result na an exponent of Etiny.

    In all cases, Inexact, Rounded, na Subnormal will also be raised.
    """

kundi FloatOperation(DecimalException, TypeError):
    """Enable stricter semantics kila mixing floats na Decimals.

    If the signal ni sio trapped (default), mixing floats na Decimals is
    permitted kwenye the Decimal() constructor, context.create_decimal() and
    all comparison operators. Both conversion na comparisons are exact.
    Any occurrence of a mixed operation ni silently recorded by setting
    FloatOperation kwenye the context flags.  Explicit conversions with
    Decimal.from_float() ama context.create_decimal_from_float() do not
    set the flag.

    Otherwise (the signal ni trapped), only equality comparisons na explicit
    conversions are silent. All other mixed operations  ashiria FloatOperation.
    """

# List of public traps na flags
_signals = [Clamped, DivisionByZero, Inexact, Overflow, Rounded,
            Underflow, InvalidOperation, Subnormal, FloatOperation]

# Map conditions (per the spec) to signals
_condition_map = {ConversionSyntax:InvalidOperation,
                  DivisionImpossible:InvalidOperation,
                  DivisionUndefined:InvalidOperation,
                  InvalidContext:InvalidOperation}

# Valid rounding modes
_rounding_modes = (ROUND_DOWN, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_CEILING,
                   ROUND_FLOOR, ROUND_UP, ROUND_HALF_DOWN, ROUND_05UP)

##### Context Functions ##################################################

# The getcontext() na setcontext() function manage access to a thread-local
# current context.

agiza contextvars

_current_context_var = contextvars.ContextVar('decimal_context')

eleza getcontext():
    """Returns this thread's context.

    If this thread does sio yet have a context, returns
    a new context na sets this thread's context.
    New contexts are copies of DefaultContext.
    """
    jaribu:
        rudisha _current_context_var.get()
    except LookupError:
        context = Context()
        _current_context_var.set(context)
        rudisha context

eleza setcontext(context):
    """Set this thread's context to context."""
    ikiwa context kwenye (DefaultContext, BasicContext, ExtendedContext):
        context = context.copy()
        context.clear_flags()
    _current_context_var.set(context)

toa contextvars        # Don't contaminate the namespace

eleza localcontext(ctx=Tupu):
    """Return a context manager kila a copy of the supplied context

    Uses a copy of the current context ikiwa no context ni specified
    The returned context manager creates a local decimal context
    kwenye a ukijumuisha statement:
        eleza sin(x):
             ukijumuisha localcontext() as ctx:
                 ctx.prec += 2
                 # Rest of sin calculation algorithm
                 # uses a precision 2 greater than normal
             rudisha +s  # Convert result to normal precision

         eleza sin(x):
             ukijumuisha localcontext(ExtendedContext):
                 # Rest of sin calculation algorithm
                 # uses the Extended Context kutoka the
                 # General Decimal Arithmetic Specification
             rudisha +s  # Convert result to normal context

    >>> setcontext(DefaultContext)
    >>> andika(getcontext().prec)
    28
    >>> ukijumuisha localcontext():
    ...     ctx = getcontext()
    ...     ctx.prec += 2
    ...     andika(ctx.prec)
    ...
    30
    >>> ukijumuisha localcontext(ExtendedContext):
    ...     andika(getcontext().prec)
    ...
    9
    >>> andika(getcontext().prec)
    28
    """
    ikiwa ctx ni Tupu: ctx = getcontext()
    rudisha _ContextManager(ctx)


##### Decimal kundi #######################################################

# Do sio subkundi Decimal kutoka numbers.Real na do sio register it as such
# (because Decimals are sio interoperable ukijumuisha floats).  See the notes in
# numbers.py kila more detail.

kundi Decimal(object):
    """Floating point kundi kila decimal arithmetic."""

    __slots__ = ('_exp','_int','_sign', '_is_special')
    # Generally, the value of the Decimal instance ni given by
    #  (-1)**_sign * _int * 10**_exp
    # Special values are signified by _is_special == Kweli

    # We're immutable, so use __new__ sio __init__
    eleza __new__(cls, value="0", context=Tupu):
        """Create a decimal point instance.

        >>> Decimal('3.14')              # string input
        Decimal('3.14')
        >>> Decimal((0, (3, 1, 4), -2))  # tuple (sign, digit_tuple, exponent)
        Decimal('3.14')
        >>> Decimal(314)                 # int
        Decimal('314')
        >>> Decimal(Decimal(314))        # another decimal instance
        Decimal('314')
        >>> Decimal('  3.14  \\n')        # leading na trailing whitespace okay
        Decimal('3.14')
        """

        # Note that the coefficient, self._int, ni actually stored as
        # a string rather than as a tuple of digits.  This speeds up
        # the "digits to integer" na "integer to digits" conversions
        # that are used kwenye almost every arithmetic operation on
        # Decimals.  This ni an internal detail: the as_tuple function
        # na the Decimal constructor still deal ukijumuisha tuples of
        # digits.

        self = object.__new__(cls)

        # From a string
        # REs insist on real strings, so we can too.
        ikiwa isinstance(value, str):
            m = _parser(value.strip().replace("_", ""))
            ikiwa m ni Tupu:
                ikiwa context ni Tupu:
                    context = getcontext()
                rudisha context._raise_error(ConversionSyntax,
                                "Invalid literal kila Decimal: %r" % value)

            ikiwa m.group('sign') == "-":
                self._sign = 1
            isipokua:
                self._sign = 0
            intpart = m.group('int')
            ikiwa intpart ni sio Tupu:
                # finite number
                fracpart = m.group('frac') ama ''
                exp = int(m.group('exp') ama '0')
                self._int = str(int(intpart+fracpart))
                self._exp = exp - len(fracpart)
                self._is_special = Uongo
            isipokua:
                diag = m.group('diag')
                ikiwa diag ni sio Tupu:
                    # NaN
                    self._int = str(int(diag ama '0')).lstrip('0')
                    ikiwa m.group('signal'):
                        self._exp = 'N'
                    isipokua:
                        self._exp = 'n'
                isipokua:
                    # infinity
                    self._int = '0'
                    self._exp = 'F'
                self._is_special = Kweli
            rudisha self

        # From an integer
        ikiwa isinstance(value, int):
            ikiwa value >= 0:
                self._sign = 0
            isipokua:
                self._sign = 1
            self._exp = 0
            self._int = str(abs(value))
            self._is_special = Uongo
            rudisha self

        # From another decimal
        ikiwa isinstance(value, Decimal):
            self._exp  = value._exp
            self._sign = value._sign
            self._int  = value._int
            self._is_special  = value._is_special
            rudisha self

        # From an internal working value
        ikiwa isinstance(value, _WorkRep):
            self._sign = value.sign
            self._int = str(value.int)
            self._exp = int(value.exp)
            self._is_special = Uongo
            rudisha self

        # tuple/list conversion (possibly kutoka as_tuple())
        ikiwa isinstance(value, (list,tuple)):
            ikiwa len(value) != 3:
                 ashiria ValueError('Invalid tuple size kwenye creation of Decimal '
                                 'kutoka list ama tuple.  The list ama tuple '
                                 'should have exactly three elements.')
            # process sign.  The isinstance test rejects floats
            ikiwa sio (isinstance(value[0], int) na value[0] kwenye (0,1)):
                 ashiria ValueError("Invalid sign.  The first value kwenye the tuple "
                                 "should be an integer; either 0 kila a "
                                 "positive number ama 1 kila a negative number.")
            self._sign = value[0]
            ikiwa value[2] == 'F':
                # infinity: value[1] ni ignored
                self._int = '0'
                self._exp = value[2]
                self._is_special = Kweli
            isipokua:
                # process na validate the digits kwenye value[1]
                digits = []
                kila digit kwenye value[1]:
                    ikiwa isinstance(digit, int) na 0 <= digit <= 9:
                        # skip leading zeros
                        ikiwa digits ama digit != 0:
                            digits.append(digit)
                    isipokua:
                         ashiria ValueError("The second value kwenye the tuple must "
                                         "be composed of integers kwenye the range "
                                         "0 through 9.")
                ikiwa value[2] kwenye ('n', 'N'):
                    # NaN: digits form the diagnostic
                    self._int = ''.join(map(str, digits))
                    self._exp = value[2]
                    self._is_special = Kweli
                elikiwa isinstance(value[2], int):
                    # finite number: digits give the coefficient
                    self._int = ''.join(map(str, digits ama [0]))
                    self._exp = value[2]
                    self._is_special = Uongo
                isipokua:
                     ashiria ValueError("The third value kwenye the tuple must "
                                     "be an integer, ama one of the "
                                     "strings 'F', 'n', 'N'.")
            rudisha self

        ikiwa isinstance(value, float):
            ikiwa context ni Tupu:
                context = getcontext()
            context._raise_error(FloatOperation,
                "strict semantics kila mixing floats na Decimals are "
                "enabled")
            value = Decimal.from_float(value)
            self._exp  = value._exp
            self._sign = value._sign
            self._int  = value._int
            self._is_special  = value._is_special
            rudisha self

         ashiria TypeError("Cannot convert %r to Decimal" % value)

    @classmethod
    eleza from_float(cls, f):
        """Converts a float to a decimal number, exactly.

        Note that Decimal.from_float(0.1) ni sio the same as Decimal('0.1').
        Since 0.1 ni sio exactly representable kwenye binary floating point, the
        value ni stored as the nearest representable value which is
        0x1.999999999999ap-4.  The exact equivalent of the value kwenye decimal
        ni 0.1000000000000000055511151231257827021181583404541015625.

        >>> Decimal.from_float(0.1)
        Decimal('0.1000000000000000055511151231257827021181583404541015625')
        >>> Decimal.from_float(float('nan'))
        Decimal('NaN')
        >>> Decimal.from_float(float('inf'))
        Decimal('Infinity')
        >>> Decimal.from_float(-float('inf'))
        Decimal('-Infinity')
        >>> Decimal.from_float(-0.0)
        Decimal('-0')

        """
        ikiwa isinstance(f, int):                # handle integer inputs
            sign = 0 ikiwa f >= 0 isipokua 1
            k = 0
            coeff = str(abs(f))
        elikiwa isinstance(f, float):
            ikiwa _math.isinf(f) ama _math.isnan(f):
                rudisha cls(repr(f))
            ikiwa _math.copysign(1.0, f) == 1.0:
                sign = 0
            isipokua:
                sign = 1
            n, d = abs(f).as_integer_ratio()
            k = d.bit_length() - 1
            coeff = str(n*5**k)
        isipokua:
             ashiria TypeError("argument must be int ama float.")

        result = _dec_from_triple(sign, coeff, -k)
        ikiwa cls ni Decimal:
            rudisha result
        isipokua:
            rudisha cls(result)

    eleza _isnan(self):
        """Returns whether the number ni sio actually one.

        0 ikiwa a number
        1 ikiwa NaN
        2 ikiwa sNaN
        """
        ikiwa self._is_special:
            exp = self._exp
            ikiwa exp == 'n':
                rudisha 1
            elikiwa exp == 'N':
                rudisha 2
        rudisha 0

    eleza _isinfinity(self):
        """Returns whether the number ni infinite

        0 ikiwa finite ama sio a number
        1 ikiwa +INF
        -1 ikiwa -INF
        """
        ikiwa self._exp == 'F':
            ikiwa self._sign:
                rudisha -1
            rudisha 1
        rudisha 0

    eleza _check_nans(self, other=Tupu, context=Tupu):
        """Returns whether the number ni sio actually one.

        ikiwa self, other are sNaN, signal
        ikiwa self, other are NaN rudisha nan
        rudisha 0

        Done before operations.
        """

        self_is_nan = self._isnan()
        ikiwa other ni Tupu:
            other_is_nan = Uongo
        isipokua:
            other_is_nan = other._isnan()

        ikiwa self_is_nan ama other_is_nan:
            ikiwa context ni Tupu:
                context = getcontext()

            ikiwa self_is_nan == 2:
                rudisha context._raise_error(InvalidOperation, 'sNaN',
                                        self)
            ikiwa other_is_nan == 2:
                rudisha context._raise_error(InvalidOperation, 'sNaN',
                                        other)
            ikiwa self_is_nan:
                rudisha self._fix_nan(context)

            rudisha other._fix_nan(context)
        rudisha 0

    eleza _compare_check_nans(self, other, context):
        """Version of _check_nans used kila the signaling comparisons
        compare_signal, __le__, __lt__, __ge__, __gt__.

        Signal InvalidOperation ikiwa either self ama other ni a (quiet
        ama signaling) NaN.  Signaling NaNs take precedence over quiet
        NaNs.

        Return 0 ikiwa neither operand ni a NaN.

        """
        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa self._is_special ama other._is_special:
            ikiwa self.is_snan():
                rudisha context._raise_error(InvalidOperation,
                                            'comparison involving sNaN',
                                            self)
            elikiwa other.is_snan():
                rudisha context._raise_error(InvalidOperation,
                                            'comparison involving sNaN',
                                            other)
            elikiwa self.is_qnan():
                rudisha context._raise_error(InvalidOperation,
                                            'comparison involving NaN',
                                            self)
            elikiwa other.is_qnan():
                rudisha context._raise_error(InvalidOperation,
                                            'comparison involving NaN',
                                            other)
        rudisha 0

    eleza __bool__(self):
        """Return Kweli ikiwa self ni nonzero; otherwise rudisha Uongo.

        NaNs na infinities are considered nonzero.
        """
        rudisha self._is_special ama self._int != '0'

    eleza _cmp(self, other):
        """Compare the two non-NaN decimal instances self na other.

        Returns -1 ikiwa self < other, 0 ikiwa self == other na 1
        ikiwa self > other.  This routine ni kila internal use only."""

        ikiwa self._is_special ama other._is_special:
            self_inf = self._isinfinity()
            other_inf = other._isinfinity()
            ikiwa self_inf == other_inf:
                rudisha 0
            elikiwa self_inf < other_inf:
                rudisha -1
            isipokua:
                rudisha 1

        # check kila zeros;  Decimal('0') == Decimal('-0')
        ikiwa sio self:
            ikiwa sio other:
                rudisha 0
            isipokua:
                rudisha -((-1)**other._sign)
        ikiwa sio other:
            rudisha (-1)**self._sign

        # If different signs, neg one ni less
        ikiwa other._sign < self._sign:
            rudisha -1
        ikiwa self._sign < other._sign:
            rudisha 1

        self_adjusted = self.adjusted()
        other_adjusted = other.adjusted()
        ikiwa self_adjusted == other_adjusted:
            self_padded = self._int + '0'*(self._exp - other._exp)
            other_padded = other._int + '0'*(other._exp - self._exp)
            ikiwa self_padded == other_padded:
                rudisha 0
            elikiwa self_padded < other_padded:
                rudisha -(-1)**self._sign
            isipokua:
                rudisha (-1)**self._sign
        elikiwa self_adjusted > other_adjusted:
            rudisha (-1)**self._sign
        isipokua: # self_adjusted < other_adjusted
            rudisha -((-1)**self._sign)

    # Note: The Decimal standard doesn't cover rich comparisons for
    # Decimals.  In particular, the specification ni silent on the
    # subject of what should happen kila a comparison involving a NaN.
    # We take the following approach:
    #
    #   == comparisons involving a quiet NaN always rudisha Uongo
    #   != comparisons involving a quiet NaN always rudisha Kweli
    #   == ama != comparisons involving a signaling NaN signal
    #      InvalidOperation, na rudisha Uongo ama Kweli as above ikiwa the
    #      InvalidOperation ni sio trapped.
    #   <, >, <= na >= comparisons involving a (quiet ama signaling)
    #      NaN signal InvalidOperation, na rudisha Uongo ikiwa the
    #      InvalidOperation ni sio trapped.
    #
    # This behavior ni designed to conform as closely as possible to
    # that specified by IEEE 754.

    eleza __eq__(self, other, context=Tupu):
        self, other = _convert_for_comparison(self, other, equality_op=Kweli)
        ikiwa other ni NotImplemented:
            rudisha other
        ikiwa self._check_nans(other, context):
            rudisha Uongo
        rudisha self._cmp(other) == 0

    eleza __lt__(self, other, context=Tupu):
        self, other = _convert_for_comparison(self, other)
        ikiwa other ni NotImplemented:
            rudisha other
        ans = self._compare_check_nans(other, context)
        ikiwa ans:
            rudisha Uongo
        rudisha self._cmp(other) < 0

    eleza __le__(self, other, context=Tupu):
        self, other = _convert_for_comparison(self, other)
        ikiwa other ni NotImplemented:
            rudisha other
        ans = self._compare_check_nans(other, context)
        ikiwa ans:
            rudisha Uongo
        rudisha self._cmp(other) <= 0

    eleza __gt__(self, other, context=Tupu):
        self, other = _convert_for_comparison(self, other)
        ikiwa other ni NotImplemented:
            rudisha other
        ans = self._compare_check_nans(other, context)
        ikiwa ans:
            rudisha Uongo
        rudisha self._cmp(other) > 0

    eleza __ge__(self, other, context=Tupu):
        self, other = _convert_for_comparison(self, other)
        ikiwa other ni NotImplemented:
            rudisha other
        ans = self._compare_check_nans(other, context)
        ikiwa ans:
            rudisha Uongo
        rudisha self._cmp(other) >= 0

    eleza compare(self, other, context=Tupu):
        """Compare self to other.  Return a decimal value:

        a ama b ni a NaN ==> Decimal('NaN')
        a < b           ==> Decimal('-1')
        a == b          ==> Decimal('0')
        a > b           ==> Decimal('1')
        """
        other = _convert_other(other, raiseit=Kweli)

        # Compare(NaN, NaN) = NaN
        ikiwa (self._is_special ama other na other._is_special):
            ans = self._check_nans(other, context)
            ikiwa ans:
                rudisha ans

        rudisha Decimal(self._cmp(other))

    eleza __hash__(self):
        """x.__hash__() <==> hash(x)"""

        # In order to make sure that the hash of a Decimal instance
        # agrees ukijumuisha the hash of a numerically equal integer, float
        # ama Fraction, we follow the rules kila numeric hashes outlined
        # kwenye the documentation.  (See library docs, 'Built-in Types').
        ikiwa self._is_special:
            ikiwa self.is_snan():
                 ashiria TypeError('Cannot hash a signaling NaN value.')
            elikiwa self.is_nan():
                rudisha _PyHASH_NAN
            isipokua:
                ikiwa self._sign:
                    rudisha -_PyHASH_INF
                isipokua:
                    rudisha _PyHASH_INF

        ikiwa self._exp >= 0:
            exp_hash = pow(10, self._exp, _PyHASH_MODULUS)
        isipokua:
            exp_hash = pow(_PyHASH_10INV, -self._exp, _PyHASH_MODULUS)
        hash_ = int(self._int) * exp_hash % _PyHASH_MODULUS
        ans = hash_ ikiwa self >= 0 isipokua -hash_
        rudisha -2 ikiwa ans == -1 isipokua ans

    eleza as_tuple(self):
        """Represents the number as a triple tuple.

        To show the internals exactly as they are.
        """
        rudisha DecimalTuple(self._sign, tuple(map(int, self._int)), self._exp)

    eleza as_integer_ratio(self):
        """Express a finite Decimal instance kwenye the form n / d.

        Returns a pair (n, d) of integers.  When called on an infinity
        ama NaN, raises OverflowError ama ValueError respectively.

        >>> Decimal('3.14').as_integer_ratio()
        (157, 50)
        >>> Decimal('-123e5').as_integer_ratio()
        (-12300000, 1)
        >>> Decimal('0.00').as_integer_ratio()
        (0, 1)

        """
        ikiwa self._is_special:
            ikiwa self.is_nan():
                 ashiria ValueError("cannot convert NaN to integer ratio")
            isipokua:
                 ashiria OverflowError("cannot convert Infinity to integer ratio")

        ikiwa sio self:
            rudisha 0, 1

        # Find n, d kwenye lowest terms such that abs(self) == n / d;
        # we'll deal ukijumuisha the sign later.
        n = int(self._int)
        ikiwa self._exp >= 0:
            # self ni an integer.
            n, d = n * 10**self._exp, 1
        isipokua:
            # Find d2, d5 such that abs(self) = n / (2**d2 * 5**d5).
            d5 = -self._exp
            wakati d5 > 0 na n % 5 == 0:
                n //= 5
                d5 -= 1

            # (n & -n).bit_length() - 1 counts trailing zeros kwenye binary
            # representation of n (provided n ni nonzero).
            d2 = -self._exp
            shift2 = min((n & -n).bit_length() - 1, d2)
            ikiwa shift2:
                n >>= shift2
                d2 -= shift2

            d = 5**d5 << d2

        ikiwa self._sign:
            n = -n
        rudisha n, d

    eleza __repr__(self):
        """Represents the number as an instance of Decimal."""
        # Invariant:  eval(repr(d)) == d
        rudisha "Decimal('%s')" % str(self)

    eleza __str__(self, eng=Uongo, context=Tupu):
        """Return string representation of the number kwenye scientific notation.

        Captures all of the information kwenye the underlying representation.
        """

        sign = ['', '-'][self._sign]
        ikiwa self._is_special:
            ikiwa self._exp == 'F':
                rudisha sign + 'Infinity'
            elikiwa self._exp == 'n':
                rudisha sign + 'NaN' + self._int
            isipokua: # self._exp == 'N'
                rudisha sign + 'sNaN' + self._int

        # number of digits of self._int to left of decimal point
        leftdigits = self._exp + len(self._int)

        # dotplace ni number of digits of self._int to the left of the
        # decimal point kwenye the mantissa of the output string (that is,
        # after adjusting the exponent)
        ikiwa self._exp <= 0 na leftdigits > -6:
            # no exponent required
            dotplace = leftdigits
        elikiwa sio eng:
            # usual scientific notation: 1 digit on left of the point
            dotplace = 1
        elikiwa self._int == '0':
            # engineering notation, zero
            dotplace = (leftdigits + 1) % 3 - 1
        isipokua:
            # engineering notation, nonzero
            dotplace = (leftdigits - 1) % 3 + 1

        ikiwa dotplace <= 0:
            intpart = '0'
            fracpart = '.' + '0'*(-dotplace) + self._int
        elikiwa dotplace >= len(self._int):
            intpart = self._int+'0'*(dotplace-len(self._int))
            fracpart = ''
        isipokua:
            intpart = self._int[:dotplace]
            fracpart = '.' + self._int[dotplace:]
        ikiwa leftdigits == dotplace:
            exp = ''
        isipokua:
            ikiwa context ni Tupu:
                context = getcontext()
            exp = ['e', 'E'][context.capitals] + "%+d" % (leftdigits-dotplace)

        rudisha sign + intpart + fracpart + exp

    eleza to_eng_string(self, context=Tupu):
        """Convert to a string, using engineering notation ikiwa an exponent ni needed.

        Engineering notation has an exponent which ni a multiple of 3.  This
        can leave up to 3 digits to the left of the decimal place na may
        require the addition of either one ama two trailing zeros.
        """
        rudisha self.__str__(eng=Kweli, context=context)

    eleza __neg__(self, context=Tupu):
        """Returns a copy ukijumuisha the sign switched.

        Rounds, ikiwa it has reason.
        """
        ikiwa self._is_special:
            ans = self._check_nans(context=context)
            ikiwa ans:
                rudisha ans

        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa sio self na context.rounding != ROUND_FLOOR:
            # -Decimal('0') ni Decimal('0'), sio Decimal('-0'), except
            # kwenye ROUND_FLOOR rounding mode.
            ans = self.copy_abs()
        isipokua:
            ans = self.copy_negate()

        rudisha ans._fix(context)

    eleza __pos__(self, context=Tupu):
        """Returns a copy, unless it ni a sNaN.

        Rounds the number (ikiwa more than precision digits)
        """
        ikiwa self._is_special:
            ans = self._check_nans(context=context)
            ikiwa ans:
                rudisha ans

        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa sio self na context.rounding != ROUND_FLOOR:
            # + (-0) = 0, except kwenye ROUND_FLOOR rounding mode.
            ans = self.copy_abs()
        isipokua:
            ans = Decimal(self)

        rudisha ans._fix(context)

    eleza __abs__(self, round=Kweli, context=Tupu):
        """Returns the absolute value of self.

        If the keyword argument 'round' ni false, do sio round.  The
        expression self.__abs__(round=Uongo) ni equivalent to
        self.copy_abs().
        """
        ikiwa sio round:
            rudisha self.copy_abs()

        ikiwa self._is_special:
            ans = self._check_nans(context=context)
            ikiwa ans:
                rudisha ans

        ikiwa self._sign:
            ans = self.__neg__(context=context)
        isipokua:
            ans = self.__pos__(context=context)

        rudisha ans

    eleza __add__(self, other, context=Tupu):
        """Returns self + other.

        -INF + INF (or the reverse) cause InvalidOperation errors.
        """
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other

        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa self._is_special ama other._is_special:
            ans = self._check_nans(other, context)
            ikiwa ans:
                rudisha ans

            ikiwa self._isinfinity():
                # If both INF, same sign => same as both, opposite => error.
                ikiwa self._sign != other._sign na other._isinfinity():
                    rudisha context._raise_error(InvalidOperation, '-INF + INF')
                rudisha Decimal(self)
            ikiwa other._isinfinity():
                rudisha Decimal(other)  # Can't both be infinity here

        exp = min(self._exp, other._exp)
        negativezero = 0
        ikiwa context.rounding == ROUND_FLOOR na self._sign != other._sign:
            # If the answer ni 0, the sign should be negative, kwenye this case.
            negativezero = 1

        ikiwa sio self na sio other:
            sign = min(self._sign, other._sign)
            ikiwa negativezero:
                sign = 1
            ans = _dec_from_triple(sign, '0', exp)
            ans = ans._fix(context)
            rudisha ans
        ikiwa sio self:
            exp = max(exp, other._exp - context.prec-1)
            ans = other._rescale(exp, context.rounding)
            ans = ans._fix(context)
            rudisha ans
        ikiwa sio other:
            exp = max(exp, self._exp - context.prec-1)
            ans = self._rescale(exp, context.rounding)
            ans = ans._fix(context)
            rudisha ans

        op1 = _WorkRep(self)
        op2 = _WorkRep(other)
        op1, op2 = _normalize(op1, op2, context.prec)

        result = _WorkRep()
        ikiwa op1.sign != op2.sign:
            # Equal na opposite
            ikiwa op1.int == op2.int:
                ans = _dec_from_triple(negativezero, '0', exp)
                ans = ans._fix(context)
                rudisha ans
            ikiwa op1.int < op2.int:
                op1, op2 = op2, op1
                # OK, now abs(op1) > abs(op2)
            ikiwa op1.sign == 1:
                result.sign = 1
                op1.sign, op2.sign = op2.sign, op1.sign
            isipokua:
                result.sign = 0
                # So we know the sign, na op1 > 0.
        elikiwa op1.sign == 1:
            result.sign = 1
            op1.sign, op2.sign = (0, 0)
        isipokua:
            result.sign = 0
        # Now, op1 > abs(op2) > 0

        ikiwa op2.sign == 0:
            result.int = op1.int + op2.int
        isipokua:
            result.int = op1.int - op2.int

        result.exp = op1.exp
        ans = Decimal(result)
        ans = ans._fix(context)
        rudisha ans

    __radd__ = __add__

    eleza __sub__(self, other, context=Tupu):
        """Return self - other"""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other

        ikiwa self._is_special ama other._is_special:
            ans = self._check_nans(other, context=context)
            ikiwa ans:
                rudisha ans

        # self - other ni computed as self + other.copy_negate()
        rudisha self.__add__(other.copy_negate(), context=context)

    eleza __rsub__(self, other, context=Tupu):
        """Return other - self"""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other

        rudisha other.__sub__(self, context=context)

    eleza __mul__(self, other, context=Tupu):
        """Return self * other.

        (+-) INF * 0 (or its reverse)  ashiria InvalidOperation.
        """
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other

        ikiwa context ni Tupu:
            context = getcontext()

        resultsign = self._sign ^ other._sign

        ikiwa self._is_special ama other._is_special:
            ans = self._check_nans(other, context)
            ikiwa ans:
                rudisha ans

            ikiwa self._isinfinity():
                ikiwa sio other:
                    rudisha context._raise_error(InvalidOperation, '(+-)INF * 0')
                rudisha _SignedInfinity[resultsign]

            ikiwa other._isinfinity():
                ikiwa sio self:
                    rudisha context._raise_error(InvalidOperation, '0 * (+-)INF')
                rudisha _SignedInfinity[resultsign]

        resultexp = self._exp + other._exp

        # Special case kila multiplying by zero
        ikiwa sio self ama sio other:
            ans = _dec_from_triple(resultsign, '0', resultexp)
            # Fixing kwenye case the exponent ni out of bounds
            ans = ans._fix(context)
            rudisha ans

        # Special case kila multiplying by power of 10
        ikiwa self._int == '1':
            ans = _dec_from_triple(resultsign, other._int, resultexp)
            ans = ans._fix(context)
            rudisha ans
        ikiwa other._int == '1':
            ans = _dec_from_triple(resultsign, self._int, resultexp)
            ans = ans._fix(context)
            rudisha ans

        op1 = _WorkRep(self)
        op2 = _WorkRep(other)

        ans = _dec_from_triple(resultsign, str(op1.int * op2.int), resultexp)
        ans = ans._fix(context)

        rudisha ans
    __rmul__ = __mul__

    eleza __truediv__(self, other, context=Tupu):
        """Return self / other."""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha NotImplemented

        ikiwa context ni Tupu:
            context = getcontext()

        sign = self._sign ^ other._sign

        ikiwa self._is_special ama other._is_special:
            ans = self._check_nans(other, context)
            ikiwa ans:
                rudisha ans

            ikiwa self._isinfinity() na other._isinfinity():
                rudisha context._raise_error(InvalidOperation, '(+-)INF/(+-)INF')

            ikiwa self._isinfinity():
                rudisha _SignedInfinity[sign]

            ikiwa other._isinfinity():
                context._raise_error(Clamped, 'Division by infinity')
                rudisha _dec_from_triple(sign, '0', context.Etiny())

        # Special cases kila zeroes
        ikiwa sio other:
            ikiwa sio self:
                rudisha context._raise_error(DivisionUndefined, '0 / 0')
            rudisha context._raise_error(DivisionByZero, 'x / 0', sign)

        ikiwa sio self:
            exp = self._exp - other._exp
            coeff = 0
        isipokua:
            # OK, so neither = 0, INF ama NaN
            shift = len(other._int) - len(self._int) + context.prec + 1
            exp = self._exp - other._exp - shift
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            ikiwa shift >= 0:
                coeff, remainder = divmod(op1.int * 10**shift, op2.int)
            isipokua:
                coeff, remainder = divmod(op1.int, op2.int * 10**-shift)
            ikiwa remainder:
                # result ni sio exact; adjust to ensure correct rounding
                ikiwa coeff % 5 == 0:
                    coeff += 1
            isipokua:
                # result ni exact; get as close to ideal exponent as possible
                ideal_exp = self._exp - other._exp
                wakati exp < ideal_exp na coeff % 10 == 0:
                    coeff //= 10
                    exp += 1

        ans = _dec_from_triple(sign, str(coeff), exp)
        rudisha ans._fix(context)

    eleza _divide(self, other, context):
        """Return (self // other, self % other), to context.prec precision.

        Assumes that neither self nor other ni a NaN, that self ni not
        infinite na that other ni nonzero.
        """
        sign = self._sign ^ other._sign
        ikiwa other._isinfinity():
            ideal_exp = self._exp
        isipokua:
            ideal_exp = min(self._exp, other._exp)

        expdiff = self.adjusted() - other.adjusted()
        ikiwa sio self ama other._isinfinity() ama expdiff <= -2:
            rudisha (_dec_from_triple(sign, '0', 0),
                    self._rescale(ideal_exp, context.rounding))
        ikiwa expdiff <= context.prec:
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            ikiwa op1.exp >= op2.exp:
                op1.int *= 10**(op1.exp - op2.exp)
            isipokua:
                op2.int *= 10**(op2.exp - op1.exp)
            q, r = divmod(op1.int, op2.int)
            ikiwa q < 10**context.prec:
                rudisha (_dec_from_triple(sign, str(q), 0),
                        _dec_from_triple(self._sign, str(r), ideal_exp))

        # Here the quotient ni too large to be representable
        ans = context._raise_error(DivisionImpossible,
                                   'quotient too large kwenye //, % ama divmod')
        rudisha ans, ans

    eleza __rtruediv__(self, other, context=Tupu):
        """Swaps self/other na returns __truediv__."""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other
        rudisha other.__truediv__(self, context=context)

    eleza __divmod__(self, other, context=Tupu):
        """
        Return (self // other, self % other)
        """
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other

        ikiwa context ni Tupu:
            context = getcontext()

        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha (ans, ans)

        sign = self._sign ^ other._sign
        ikiwa self._isinfinity():
            ikiwa other._isinfinity():
                ans = context._raise_error(InvalidOperation, 'divmod(INF, INF)')
                rudisha ans, ans
            isipokua:
                rudisha (_SignedInfinity[sign],
                        context._raise_error(InvalidOperation, 'INF % x'))

        ikiwa sio other:
            ikiwa sio self:
                ans = context._raise_error(DivisionUndefined, 'divmod(0, 0)')
                rudisha ans, ans
            isipokua:
                rudisha (context._raise_error(DivisionByZero, 'x // 0', sign),
                        context._raise_error(InvalidOperation, 'x % 0'))

        quotient, remainder = self._divide(other, context)
        remainder = remainder._fix(context)
        rudisha quotient, remainder

    eleza __rdivmod__(self, other, context=Tupu):
        """Swaps self/other na returns __divmod__."""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other
        rudisha other.__divmod__(self, context=context)

    eleza __mod__(self, other, context=Tupu):
        """
        self % other
        """
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other

        ikiwa context ni Tupu:
            context = getcontext()

        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha ans

        ikiwa self._isinfinity():
            rudisha context._raise_error(InvalidOperation, 'INF % x')
        elikiwa sio other:
            ikiwa self:
                rudisha context._raise_error(InvalidOperation, 'x % 0')
            isipokua:
                rudisha context._raise_error(DivisionUndefined, '0 % 0')

        remainder = self._divide(other, context)[1]
        remainder = remainder._fix(context)
        rudisha remainder

    eleza __rmod__(self, other, context=Tupu):
        """Swaps self/other na returns __mod__."""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other
        rudisha other.__mod__(self, context=context)

    eleza remainder_near(self, other, context=Tupu):
        """
        Remainder nearest to 0-  abs(remainder-near) <= other/2
        """
        ikiwa context ni Tupu:
            context = getcontext()

        other = _convert_other(other, raiseit=Kweli)

        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha ans

        # self == +/-infinity -> InvalidOperation
        ikiwa self._isinfinity():
            rudisha context._raise_error(InvalidOperation,
                                        'remainder_near(infinity, x)')

        # other == 0 -> either InvalidOperation ama DivisionUndefined
        ikiwa sio other:
            ikiwa self:
                rudisha context._raise_error(InvalidOperation,
                                            'remainder_near(x, 0)')
            isipokua:
                rudisha context._raise_error(DivisionUndefined,
                                            'remainder_near(0, 0)')

        # other = +/-infinity -> remainder = self
        ikiwa other._isinfinity():
            ans = Decimal(self)
            rudisha ans._fix(context)

        # self = 0 -> remainder = self, ukijumuisha ideal exponent
        ideal_exponent = min(self._exp, other._exp)
        ikiwa sio self:
            ans = _dec_from_triple(self._sign, '0', ideal_exponent)
            rudisha ans._fix(context)

        # catch most cases of large ama small quotient
        expdiff = self.adjusted() - other.adjusted()
        ikiwa expdiff >= context.prec + 1:
            # expdiff >= prec+1 => abs(self/other) > 10**prec
            rudisha context._raise_error(DivisionImpossible)
        ikiwa expdiff <= -2:
            # expdiff <= -2 => abs(self/other) < 0.1
            ans = self._rescale(ideal_exponent, context.rounding)
            rudisha ans._fix(context)

        # adjust both arguments to have the same exponent, then divide
        op1 = _WorkRep(self)
        op2 = _WorkRep(other)
        ikiwa op1.exp >= op2.exp:
            op1.int *= 10**(op1.exp - op2.exp)
        isipokua:
            op2.int *= 10**(op2.exp - op1.exp)
        q, r = divmod(op1.int, op2.int)
        # remainder ni r*10**ideal_exponent; other ni +/-op2.int *
        # 10**ideal_exponent.   Apply correction to ensure that
        # abs(remainder) <= abs(other)/2
        ikiwa 2*r + (q&1) > op2.int:
            r -= op2.int
            q += 1

        ikiwa q >= 10**context.prec:
            rudisha context._raise_error(DivisionImpossible)

        # result has same sign as self unless r ni negative
        sign = self._sign
        ikiwa r < 0:
            sign = 1-sign
            r = -r

        ans = _dec_from_triple(sign, str(r), ideal_exponent)
        rudisha ans._fix(context)

    eleza __floordiv__(self, other, context=Tupu):
        """self // other"""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other

        ikiwa context ni Tupu:
            context = getcontext()

        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha ans

        ikiwa self._isinfinity():
            ikiwa other._isinfinity():
                rudisha context._raise_error(InvalidOperation, 'INF // INF')
            isipokua:
                rudisha _SignedInfinity[self._sign ^ other._sign]

        ikiwa sio other:
            ikiwa self:
                rudisha context._raise_error(DivisionByZero, 'x // 0',
                                            self._sign ^ other._sign)
            isipokua:
                rudisha context._raise_error(DivisionUndefined, '0 // 0')

        rudisha self._divide(other, context)[0]

    eleza __rfloordiv__(self, other, context=Tupu):
        """Swaps self/other na returns __floordiv__."""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other
        rudisha other.__floordiv__(self, context=context)

    eleza __float__(self):
        """Float representation."""
        ikiwa self._isnan():
            ikiwa self.is_snan():
                 ashiria ValueError("Cannot convert signaling NaN to float")
            s = "-nan" ikiwa self._sign isipokua "nan"
        isipokua:
            s = str(self)
        rudisha float(s)

    eleza __int__(self):
        """Converts self to an int, truncating ikiwa necessary."""
        ikiwa self._is_special:
            ikiwa self._isnan():
                 ashiria ValueError("Cannot convert NaN to integer")
            elikiwa self._isinfinity():
                 ashiria OverflowError("Cannot convert infinity to integer")
        s = (-1)**self._sign
        ikiwa self._exp >= 0:
            rudisha s*int(self._int)*10**self._exp
        isipokua:
            rudisha s*int(self._int[:self._exp] ama '0')

    __trunc__ = __int__

    @property
    eleza real(self):
        rudisha self

    @property
    eleza imag(self):
        rudisha Decimal(0)

    eleza conjugate(self):
        rudisha self

    eleza __complex__(self):
        rudisha complex(float(self))

    eleza _fix_nan(self, context):
        """Decapitate the payload of a NaN to fit the context"""
        payload = self._int

        # maximum length of payload ni precision ikiwa clamp=0,
        # precision-1 ikiwa clamp=1.
        max_payload_len = context.prec - context.clamp
        ikiwa len(payload) > max_payload_len:
            payload = payload[len(payload)-max_payload_len:].lstrip('0')
            rudisha _dec_from_triple(self._sign, payload, self._exp, Kweli)
        rudisha Decimal(self)

    eleza _fix(self, context):
        """Round ikiwa it ni necessary to keep self within prec precision.

        Rounds na fixes the exponent.  Does sio  ashiria on a sNaN.

        Arguments:
        self - Decimal instance
        context - context used.
        """

        ikiwa self._is_special:
            ikiwa self._isnan():
                # decapitate payload ikiwa necessary
                rudisha self._fix_nan(context)
            isipokua:
                # self ni +/-Infinity; rudisha unaltered
                rudisha Decimal(self)

        # ikiwa self ni zero then exponent should be between Etiny and
        # Emax ikiwa clamp==0, na between Etiny na Etop ikiwa clamp==1.
        Etiny = context.Etiny()
        Etop = context.Etop()
        ikiwa sio self:
            exp_max = [context.Emax, Etop][context.clamp]
            new_exp = min(max(self._exp, Etiny), exp_max)
            ikiwa new_exp != self._exp:
                context._raise_error(Clamped)
                rudisha _dec_from_triple(self._sign, '0', new_exp)
            isipokua:
                rudisha Decimal(self)

        # exp_min ni the smallest allowable exponent of the result,
        # equal to max(self.adjusted()-context.prec+1, Etiny)
        exp_min = len(self._int) + self._exp - context.prec
        ikiwa exp_min > Etop:
            # overflow: exp_min > Etop iff self.adjusted() > Emax
            ans = context._raise_error(Overflow, 'above Emax', self._sign)
            context._raise_error(Inexact)
            context._raise_error(Rounded)
            rudisha ans

        self_is_subnormal = exp_min < Etiny
        ikiwa self_is_subnormal:
            exp_min = Etiny

        # round ikiwa self has too many digits
        ikiwa self._exp < exp_min:
            digits = len(self._int) + self._exp - exp_min
            ikiwa digits < 0:
                self = _dec_from_triple(self._sign, '1', exp_min-1)
                digits = 0
            rounding_method = self._pick_rounding_function[context.rounding]
            changed = rounding_method(self, digits)
            coeff = self._int[:digits] ama '0'
            ikiwa changed > 0:
                coeff = str(int(coeff)+1)
                ikiwa len(coeff) > context.prec:
                    coeff = coeff[:-1]
                    exp_min += 1

            # check whether the rounding pushed the exponent out of range
            ikiwa exp_min > Etop:
                ans = context._raise_error(Overflow, 'above Emax', self._sign)
            isipokua:
                ans = _dec_from_triple(self._sign, coeff, exp_min)

            #  ashiria the appropriate signals, taking care to respect
            # the precedence described kwenye the specification
            ikiwa changed na self_is_subnormal:
                context._raise_error(Underflow)
            ikiwa self_is_subnormal:
                context._raise_error(Subnormal)
            ikiwa changed:
                context._raise_error(Inexact)
            context._raise_error(Rounded)
            ikiwa sio ans:
                #  ashiria Clamped on underflow to 0
                context._raise_error(Clamped)
            rudisha ans

        ikiwa self_is_subnormal:
            context._raise_error(Subnormal)

        # fold down ikiwa clamp == 1 na self has too few digits
        ikiwa context.clamp == 1 na self._exp > Etop:
            context._raise_error(Clamped)
            self_padded = self._int + '0'*(self._exp - Etop)
            rudisha _dec_from_triple(self._sign, self_padded, Etop)

        # here self was representable to begin with; rudisha unchanged
        rudisha Decimal(self)

    # kila each of the rounding functions below:
    #   self ni a finite, nonzero Decimal
    #   prec ni an integer satisfying 0 <= prec < len(self._int)
    #
    # each function returns either -1, 0, ama 1, as follows:
    #   1 indicates that self should be rounded up (away kutoka zero)
    #   0 indicates that self should be truncated, na that all the
    #     digits to be truncated are zeros (so the value ni unchanged)
    #  -1 indicates that there are nonzero digits to be truncated

    eleza _round_down(self, prec):
        """Also known as round-towards-0, truncate."""
        ikiwa _all_zeros(self._int, prec):
            rudisha 0
        isipokua:
            rudisha -1

    eleza _round_up(self, prec):
        """Rounds away kutoka 0."""
        rudisha -self._round_down(prec)

    eleza _round_half_up(self, prec):
        """Rounds 5 up (away kutoka 0)"""
        ikiwa self._int[prec] kwenye '56789':
            rudisha 1
        elikiwa _all_zeros(self._int, prec):
            rudisha 0
        isipokua:
            rudisha -1

    eleza _round_half_down(self, prec):
        """Round 5 down"""
        ikiwa _exact_half(self._int, prec):
            rudisha -1
        isipokua:
            rudisha self._round_half_up(prec)

    eleza _round_half_even(self, prec):
        """Round 5 to even, rest to nearest."""
        ikiwa _exact_half(self._int, prec) na \
                (prec == 0 ama self._int[prec-1] kwenye '02468'):
            rudisha -1
        isipokua:
            rudisha self._round_half_up(prec)

    eleza _round_ceiling(self, prec):
        """Rounds up (not away kutoka 0 ikiwa negative.)"""
        ikiwa self._sign:
            rudisha self._round_down(prec)
        isipokua:
            rudisha -self._round_down(prec)

    eleza _round_floor(self, prec):
        """Rounds down (not towards 0 ikiwa negative)"""
        ikiwa sio self._sign:
            rudisha self._round_down(prec)
        isipokua:
            rudisha -self._round_down(prec)

    eleza _round_05up(self, prec):
        """Round down unless digit prec-1 ni 0 ama 5."""
        ikiwa prec na self._int[prec-1] sio kwenye '05':
            rudisha self._round_down(prec)
        isipokua:
            rudisha -self._round_down(prec)

    _pick_rounding_function = dict(
        ROUND_DOWN = _round_down,
        ROUND_UP = _round_up,
        ROUND_HALF_UP = _round_half_up,
        ROUND_HALF_DOWN = _round_half_down,
        ROUND_HALF_EVEN = _round_half_even,
        ROUND_CEILING = _round_ceiling,
        ROUND_FLOOR = _round_floor,
        ROUND_05UP = _round_05up,
    )

    eleza __round__(self, n=Tupu):
        """Round self to the nearest integer, ama to a given precision.

        If only one argument ni supplied, round a finite Decimal
        instance self to the nearest integer.  If self ni infinite or
        a NaN then a Python exception ni raised.  If self ni finite
        na lies exactly halfway between two integers then it is
        rounded to the integer ukijumuisha even last digit.

        >>> round(Decimal('123.456'))
        123
        >>> round(Decimal('-456.789'))
        -457
        >>> round(Decimal('-3.0'))
        -3
        >>> round(Decimal('2.5'))
        2
        >>> round(Decimal('3.5'))
        4
        >>> round(Decimal('Inf'))
        Traceback (most recent call last):
          ...
        OverflowError: cannot round an infinity
        >>> round(Decimal('NaN'))
        Traceback (most recent call last):
          ...
        ValueError: cannot round a NaN

        If a second argument n ni supplied, self ni rounded to n
        decimal places using the rounding mode kila the current
        context.

        For an integer n, round(self, -n) ni exactly equivalent to
        self.quantize(Decimal('1En')).

        >>> round(Decimal('123.456'), 0)
        Decimal('123')
        >>> round(Decimal('123.456'), 2)
        Decimal('123.46')
        >>> round(Decimal('123.456'), -2)
        Decimal('1E+2')
        >>> round(Decimal('-Infinity'), 37)
        Decimal('NaN')
        >>> round(Decimal('sNaN123'), 0)
        Decimal('NaN123')

        """
        ikiwa n ni sio Tupu:
            # two-argument form: use the equivalent quantize call
            ikiwa sio isinstance(n, int):
                 ashiria TypeError('Second argument to round should be integral')
            exp = _dec_from_triple(0, '1', -n)
            rudisha self.quantize(exp)

        # one-argument form
        ikiwa self._is_special:
            ikiwa self.is_nan():
                 ashiria ValueError("cannot round a NaN")
            isipokua:
                 ashiria OverflowError("cannot round an infinity")
        rudisha int(self._rescale(0, ROUND_HALF_EVEN))

    eleza __floor__(self):
        """Return the floor of self, as an integer.

        For a finite Decimal instance self, rudisha the greatest
        integer n such that n <= self.  If self ni infinite ama a NaN
        then a Python exception ni raised.

        """
        ikiwa self._is_special:
            ikiwa self.is_nan():
                 ashiria ValueError("cannot round a NaN")
            isipokua:
                 ashiria OverflowError("cannot round an infinity")
        rudisha int(self._rescale(0, ROUND_FLOOR))

    eleza __ceil__(self):
        """Return the ceiling of self, as an integer.

        For a finite Decimal instance self, rudisha the least integer n
        such that n >= self.  If self ni infinite ama a NaN then a
        Python exception ni raised.

        """
        ikiwa self._is_special:
            ikiwa self.is_nan():
                 ashiria ValueError("cannot round a NaN")
            isipokua:
                 ashiria OverflowError("cannot round an infinity")
        rudisha int(self._rescale(0, ROUND_CEILING))

    eleza fma(self, other, third, context=Tupu):
        """Fused multiply-add.

        Returns self*other+third ukijumuisha no rounding of the intermediate
        product self*other.

        self na other are multiplied together, ukijumuisha no rounding of
        the result.  The third operand ni then added to the result,
        na a single final rounding ni performed.
        """

        other = _convert_other(other, raiseit=Kweli)
        third = _convert_other(third, raiseit=Kweli)

        # compute product;  ashiria InvalidOperation ikiwa either operand is
        # a signaling NaN ama ikiwa the product ni zero times infinity.
        ikiwa self._is_special ama other._is_special:
            ikiwa context ni Tupu:
                context = getcontext()
            ikiwa self._exp == 'N':
                rudisha context._raise_error(InvalidOperation, 'sNaN', self)
            ikiwa other._exp == 'N':
                rudisha context._raise_error(InvalidOperation, 'sNaN', other)
            ikiwa self._exp == 'n':
                product = self
            elikiwa other._exp == 'n':
                product = other
            elikiwa self._exp == 'F':
                ikiwa sio other:
                    rudisha context._raise_error(InvalidOperation,
                                                'INF * 0 kwenye fma')
                product = _SignedInfinity[self._sign ^ other._sign]
            elikiwa other._exp == 'F':
                ikiwa sio self:
                    rudisha context._raise_error(InvalidOperation,
                                                '0 * INF kwenye fma')
                product = _SignedInfinity[self._sign ^ other._sign]
        isipokua:
            product = _dec_from_triple(self._sign ^ other._sign,
                                       str(int(self._int) * int(other._int)),
                                       self._exp + other._exp)

        rudisha product.__add__(third, context)

    eleza _power_modulo(self, other, modulo, context=Tupu):
        """Three argument version of __pow__"""

        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other
        modulo = _convert_other(modulo)
        ikiwa modulo ni NotImplemented:
            rudisha modulo

        ikiwa context ni Tupu:
            context = getcontext()

        # deal ukijumuisha NaNs: ikiwa there are any sNaNs then first one wins,
        # (i.e. behaviour kila NaNs ni identical to that of fma)
        self_is_nan = self._isnan()
        other_is_nan = other._isnan()
        modulo_is_nan = modulo._isnan()
        ikiwa self_is_nan ama other_is_nan ama modulo_is_nan:
            ikiwa self_is_nan == 2:
                rudisha context._raise_error(InvalidOperation, 'sNaN',
                                        self)
            ikiwa other_is_nan == 2:
                rudisha context._raise_error(InvalidOperation, 'sNaN',
                                        other)
            ikiwa modulo_is_nan == 2:
                rudisha context._raise_error(InvalidOperation, 'sNaN',
                                        modulo)
            ikiwa self_is_nan:
                rudisha self._fix_nan(context)
            ikiwa other_is_nan:
                rudisha other._fix_nan(context)
            rudisha modulo._fix_nan(context)

        # check inputs: we apply same restrictions as Python's pow()
        ikiwa sio (self._isinteger() and
                other._isinteger() and
                modulo._isinteger()):
            rudisha context._raise_error(InvalidOperation,
                                        'pow() 3rd argument sio allowed '
                                        'unless all arguments are integers')
        ikiwa other < 0:
            rudisha context._raise_error(InvalidOperation,
                                        'pow() 2nd argument cannot be '
                                        'negative when 3rd argument specified')
        ikiwa sio modulo:
            rudisha context._raise_error(InvalidOperation,
                                        'pow() 3rd argument cannot be 0')

        # additional restriction kila decimal: the modulus must be less
        # than 10**prec kwenye absolute value
        ikiwa modulo.adjusted() >= context.prec:
            rudisha context._raise_error(InvalidOperation,
                                        'insufficient precision: pow() 3rd '
                                        'argument must sio have more than '
                                        'precision digits')

        # define 0**0 == NaN, kila consistency ukijumuisha two-argument pow
        # (even though it hurts!)
        ikiwa sio other na sio self:
            rudisha context._raise_error(InvalidOperation,
                                        'at least one of pow() 1st argument '
                                        'and 2nd argument must be nonzero; '
                                        '0**0 ni sio defined')

        # compute sign of result
        ikiwa other._iseven():
            sign = 0
        isipokua:
            sign = self._sign

        # convert modulo to a Python integer, na self na other to
        # Decimal integers (i.e. force their exponents to be >= 0)
        modulo = abs(int(modulo))
        base = _WorkRep(self.to_integral_value())
        exponent = _WorkRep(other.to_integral_value())

        # compute result using integer pow()
        base = (base.int % modulo * pow(10, base.exp, modulo)) % modulo
        kila i kwenye range(exponent.exp):
            base = pow(base, 10, modulo)
        base = pow(base, exponent.int, modulo)

        rudisha _dec_from_triple(sign, str(base), 0)

    eleza _power_exact(self, other, p):
        """Attempt to compute self**other exactly.

        Given Decimals self na other na an integer p, attempt to
        compute an exact result kila the power self**other, ukijumuisha p
        digits of precision.  Return Tupu ikiwa self**other ni not
        exactly representable kwenye p digits.

        Assumes that elimination of special cases has already been
        performed: self na other must both be nonspecial; self must
        be positive na sio numerically equal to 1; other must be
        nonzero.  For efficiency, other._exp should sio be too large,
        so that 10**abs(other._exp) ni a feasible calculation."""

        # In the comments below, we write x kila the value of self na y kila the
        # value of other.  Write x = xc*10**xe na abs(y) = yc*10**ye, ukijumuisha xc
        # na yc positive integers sio divisible by 10.

        # The main purpose of this method ni to identify the *failure*
        # of x**y to be exactly representable ukijumuisha as little effort as
        # possible.  So we look kila cheap na easy tests that
        # eliminate the possibility of x**y being exact.  Only ikiwa all
        # these tests are passed do we go on to actually compute x**y.

        # Here's the main idea.  Express y as a rational number m/n, ukijumuisha m and
        # n relatively prime na n>0.  Then kila x**y to be exactly
        # representable (at *any* precision), xc must be the nth power of a
        # positive integer na xe must be divisible by n.  If y ni negative
        # then additionally xc must be a power of either 2 ama 5, hence a power
        # of 2**n ama 5**n.
        #
        # There's a limit to how small |y| can be: ikiwa y=m/n as above
        # then:
        #
        #  (1) ikiwa xc != 1 then kila the result to be representable we
        #      need xc**(1/n) >= 2, na hence also xc**|y| >= 2.  So
        #      ikiwa |y| <= 1/nbits(xc) then xc < 2**nbits(xc) <=
        #      2**(1/|y|), hence xc**|y| < 2 na the result ni not
        #      representable.
        #
        #  (2) ikiwa xe != 0, |xe|*(1/n) >= 1, so |xe|*|y| >= 1.  Hence if
        #      |y| < 1/|xe| then the result ni sio representable.
        #
        # Note that since x ni sio equal to 1, at least one of (1) and
        # (2) must apply.  Now |y| < 1/nbits(xc) iff |yc|*nbits(xc) <
        # 10**-ye iff len(str(|yc|*nbits(xc)) <= -ye.
        #
        # There's also a limit to how large y can be, at least ikiwa it's
        # positive: the normalized result will have coefficient xc**y,
        # so ikiwa it's representable then xc**y < 10**p, na y <
        # p/log10(xc).  Hence ikiwa y*log10(xc) >= p then the result is
        # sio exactly representable.

        # ikiwa len(str(abs(yc*xe)) <= -ye then abs(yc*xe) < 10**-ye,
        # so |y| < 1/xe na the result ni sio representable.
        # Similarly, len(str(abs(yc)*xc_bits)) <= -ye implies |y|
        # < 1/nbits(xc).

        x = _WorkRep(self)
        xc, xe = x.int, x.exp
        wakati xc % 10 == 0:
            xc //= 10
            xe += 1

        y = _WorkRep(other)
        yc, ye = y.int, y.exp
        wakati yc % 10 == 0:
            yc //= 10
            ye += 1

        # case where xc == 1: result ni 10**(xe*y), ukijumuisha xe*y
        # required to be an integer
        ikiwa xc == 1:
            xe *= yc
            # result ni now 10**(xe * 10**ye);  xe * 10**ye must be integral
            wakati xe % 10 == 0:
                xe //= 10
                ye += 1
            ikiwa ye < 0:
                rudisha Tupu
            exponent = xe * 10**ye
            ikiwa y.sign == 1:
                exponent = -exponent
            # ikiwa other ni a nonnegative integer, use ideal exponent
            ikiwa other._isinteger() na other._sign == 0:
                ideal_exponent = self._exp*int(other)
                zeros = min(exponent-ideal_exponent, p-1)
            isipokua:
                zeros = 0
            rudisha _dec_from_triple(0, '1' + '0'*zeros, exponent-zeros)

        # case where y ni negative: xc must be either a power
        # of 2 ama a power of 5.
        ikiwa y.sign == 1:
            last_digit = xc % 10
            ikiwa last_digit kwenye (2,4,6,8):
                # quick test kila power of 2
                ikiwa xc & -xc != xc:
                    rudisha Tupu
                # now xc ni a power of 2; e ni its exponent
                e = _nbits(xc)-1

                # We now have:
                #
                #   x = 2**e * 10**xe, e > 0, na y < 0.
                #
                # The exact result is:
                #
                #   x**y = 5**(-e*y) * 10**(e*y + xe*y)
                #
                # provided that both e*y na xe*y are integers.  Note that if
                # 5**(-e*y) >= 10**p, then the result can't be expressed
                # exactly ukijumuisha p digits of precision.
                #
                # Using the above, we can guard against large values of ye.
                # 93/65 ni an upper bound kila log(10)/log(5), so if
                #
                #   ye >= len(str(93*p//65))
                #
                # then
                #
                #   -e*y >= -y >= 10**ye > 93*p/65 > p*log(10)/log(5),
                #
                # so 5**(-e*y) >= 10**p, na the coefficient of the result
                # can't be expressed kwenye p digits.

                # emax >= largest e such that 5**e < 10**p.
                emax = p*93//65
                ikiwa ye >= len(str(emax)):
                    rudisha Tupu

                # Find -e*y na -xe*y; both must be integers
                e = _decimal_lshift_exact(e * yc, ye)
                xe = _decimal_lshift_exact(xe * yc, ye)
                ikiwa e ni Tupu ama xe ni Tupu:
                    rudisha Tupu

                ikiwa e > emax:
                    rudisha Tupu
                xc = 5**e

            elikiwa last_digit == 5:
                # e >= log_5(xc) ikiwa xc ni a power of 5; we have
                # equality all the way up to xc=5**2658
                e = _nbits(xc)*28//65
                xc, remainder = divmod(5**e, xc)
                ikiwa remainder:
                    rudisha Tupu
                wakati xc % 5 == 0:
                    xc //= 5
                    e -= 1

                # Guard against large values of ye, using the same logic as in
                # the 'xc ni a power of 2' branch.  10/3 ni an upper bound for
                # log(10)/log(2).
                emax = p*10//3
                ikiwa ye >= len(str(emax)):
                    rudisha Tupu

                e = _decimal_lshift_exact(e * yc, ye)
                xe = _decimal_lshift_exact(xe * yc, ye)
                ikiwa e ni Tupu ama xe ni Tupu:
                    rudisha Tupu

                ikiwa e > emax:
                    rudisha Tupu
                xc = 2**e
            isipokua:
                rudisha Tupu

            ikiwa xc >= 10**p:
                rudisha Tupu
            xe = -e-xe
            rudisha _dec_from_triple(0, str(xc), xe)

        # now y ni positive; find m na n such that y = m/n
        ikiwa ye >= 0:
            m, n = yc*10**ye, 1
        isipokua:
            ikiwa xe != 0 na len(str(abs(yc*xe))) <= -ye:
                rudisha Tupu
            xc_bits = _nbits(xc)
            ikiwa xc != 1 na len(str(abs(yc)*xc_bits)) <= -ye:
                rudisha Tupu
            m, n = yc, 10**(-ye)
            wakati m % 2 == n % 2 == 0:
                m //= 2
                n //= 2
            wakati m % 5 == n % 5 == 0:
                m //= 5
                n //= 5

        # compute nth root of xc*10**xe
        ikiwa n > 1:
            # ikiwa 1 < xc < 2**n then xc isn't an nth power
            ikiwa xc != 1 na xc_bits <= n:
                rudisha Tupu

            xe, rem = divmod(xe, n)
            ikiwa rem != 0:
                rudisha Tupu

            # compute nth root of xc using Newton's method
            a = 1 << -(-_nbits(xc)//n) # initial estimate
            wakati Kweli:
                q, r = divmod(xc, a**(n-1))
                ikiwa a <= q:
                    koma
                isipokua:
                    a = (a*(n-1) + q)//n
            ikiwa sio (a == q na r == 0):
                rudisha Tupu
            xc = a

        # now xc*10**xe ni the nth root of the original xc*10**xe
        # compute mth power of xc*10**xe

        # ikiwa m > p*100//_log10_lb(xc) then m > p/log10(xc), hence xc**m >
        # 10**p na the result ni sio representable.
        ikiwa xc > 1 na m > p*100//_log10_lb(xc):
            rudisha Tupu
        xc = xc**m
        xe *= m
        ikiwa xc > 10**p:
            rudisha Tupu

        # by this point the result *is* exactly representable
        # adjust the exponent to get as close as possible to the ideal
        # exponent, ikiwa necessary
        str_xc = str(xc)
        ikiwa other._isinteger() na other._sign == 0:
            ideal_exponent = self._exp*int(other)
            zeros = min(xe-ideal_exponent, p-len(str_xc))
        isipokua:
            zeros = 0
        rudisha _dec_from_triple(0, str_xc+'0'*zeros, xe-zeros)

    eleza __pow__(self, other, modulo=Tupu, context=Tupu):
        """Return self ** other [ % modulo].

        With two arguments, compute self**other.

        With three arguments, compute (self**other) % modulo.  For the
        three argument form, the following restrictions on the
        arguments hold:

         - all three arguments must be integral
         - other must be nonnegative
         - either self ama other (or both) must be nonzero
         - modulo must be nonzero na must have at most p digits,
           where p ni the context precision.

        If any of these restrictions ni violated the InvalidOperation
        flag ni raised.

        The result of pow(self, other, modulo) ni identical to the
        result that would be obtained by computing (self**other) %
        modulo ukijumuisha unbounded precision, but ni computed more
        efficiently.  It ni always exact.
        """

        ikiwa modulo ni sio Tupu:
            rudisha self._power_modulo(other, modulo, context)

        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other

        ikiwa context ni Tupu:
            context = getcontext()

        # either argument ni a NaN => result ni NaN
        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha ans

        # 0**0 = NaN (!), x**0 = 1 kila nonzero x (including +/-Infinity)
        ikiwa sio other:
            ikiwa sio self:
                rudisha context._raise_error(InvalidOperation, '0 ** 0')
            isipokua:
                rudisha _One

        # result has sign 1 iff self._sign ni 1 na other ni an odd integer
        result_sign = 0
        ikiwa self._sign == 1:
            ikiwa other._isinteger():
                ikiwa sio other._iseven():
                    result_sign = 1
            isipokua:
                # -ve**noninteger = NaN
                # (-0)**noninteger = 0**noninteger
                ikiwa self:
                    rudisha context._raise_error(InvalidOperation,
                        'x ** y ukijumuisha x negative na y sio an integer')
            # negate self, without doing any unwanted rounding
            self = self.copy_negate()

        # 0**(+ve ama Inf)= 0; 0**(-ve ama -Inf) = Infinity
        ikiwa sio self:
            ikiwa other._sign == 0:
                rudisha _dec_from_triple(result_sign, '0', 0)
            isipokua:
                rudisha _SignedInfinity[result_sign]

        # Inf**(+ve ama Inf) = Inf; Inf**(-ve ama -Inf) = 0
        ikiwa self._isinfinity():
            ikiwa other._sign == 0:
                rudisha _SignedInfinity[result_sign]
            isipokua:
                rudisha _dec_from_triple(result_sign, '0', 0)

        # 1**other = 1, but the choice of exponent na the flags
        # depend on the exponent of self, na on whether other ni a
        # positive integer, a negative integer, ama neither
        ikiwa self == _One:
            ikiwa other._isinteger():
                # exp = max(self._exp*max(int(other), 0),
                # 1-context.prec) but evaluating int(other) directly
                # ni dangerous until we know other ni small (other
                # could be 1e999999999)
                ikiwa other._sign == 1:
                    multiplier = 0
                elikiwa other > context.prec:
                    multiplier = context.prec
                isipokua:
                    multiplier = int(other)

                exp = self._exp * multiplier
                ikiwa exp < 1-context.prec:
                    exp = 1-context.prec
                    context._raise_error(Rounded)
            isipokua:
                context._raise_error(Inexact)
                context._raise_error(Rounded)
                exp = 1-context.prec

            rudisha _dec_from_triple(result_sign, '1'+'0'*-exp, exp)

        # compute adjusted exponent of self
        self_adj = self.adjusted()

        # self ** infinity ni infinity ikiwa self > 1, 0 ikiwa self < 1
        # self ** -infinity ni infinity ikiwa self < 1, 0 ikiwa self > 1
        ikiwa other._isinfinity():
            ikiwa (other._sign == 0) == (self_adj < 0):
                rudisha _dec_from_triple(result_sign, '0', 0)
            isipokua:
                rudisha _SignedInfinity[result_sign]

        # kutoka here on, the result always goes through the call
        # to _fix at the end of this function.
        ans = Tupu
        exact = Uongo

        # crude test to catch cases of extreme overflow/underflow.  If
        # log10(self)*other >= 10**bound na bound >= len(str(Emax))
        # then 10**bound >= 10**len(str(Emax)) >= Emax+1 na hence
        # self**other >= 10**(Emax+1), so overflow occurs.  The test
        # kila underflow ni similar.
        bound = self._log10_exp_bound() + other.adjusted()
        ikiwa (self_adj >= 0) == (other._sign == 0):
            # self > 1 na other +ve, ama self < 1 na other -ve
            # possibility of overflow
            ikiwa bound >= len(str(context.Emax)):
                ans = _dec_from_triple(result_sign, '1', context.Emax+1)
        isipokua:
            # self > 1 na other -ve, ama self < 1 na other +ve
            # possibility of underflow to 0
            Etiny = context.Etiny()
            ikiwa bound >= len(str(-Etiny)):
                ans = _dec_from_triple(result_sign, '1', Etiny-1)

        # try kila an exact result ukijumuisha precision +1
        ikiwa ans ni Tupu:
            ans = self._power_exact(other, context.prec + 1)
            ikiwa ans ni sio Tupu:
                ikiwa result_sign == 1:
                    ans = _dec_from_triple(1, ans._int, ans._exp)
                exact = Kweli

        # usual case: inexact result, x**y computed directly as exp(y*log(x))
        ikiwa ans ni Tupu:
            p = context.prec
            x = _WorkRep(self)
            xc, xe = x.int, x.exp
            y = _WorkRep(other)
            yc, ye = y.int, y.exp
            ikiwa y.sign == 1:
                yc = -yc

            # compute correctly rounded result:  start ukijumuisha precision +3,
            # then increase precision until result ni unambiguously roundable
            extra = 3
            wakati Kweli:
                coeff, exp = _dpower(xc, xe, yc, ye, p+extra)
                ikiwa coeff % (5*10**(len(str(coeff))-p-1)):
                    koma
                extra += 3

            ans = _dec_from_triple(result_sign, str(coeff), exp)

        # unlike exp, ln na log10, the power function respects the
        # rounding mode; no need to switch to ROUND_HALF_EVEN here

        # There's a difficulty here when 'other' ni sio an integer and
        # the result ni exact.  In this case, the specification
        # requires that the Inexact flag be raised (in spite of
        # exactness), but since the result ni exact _fix won't do this
        # kila us.  (Correspondingly, the Underflow signal should also
        # be raised kila subnormal results.)  We can't directly raise
        # these signals either before ama after calling _fix, since
        # that would violate the precedence kila signals.  So we wrap
        # the ._fix call kwenye a temporary context, na reraise
        # afterwards.
        ikiwa exact na sio other._isinteger():
            # pad ukijumuisha zeros up to length context.prec+1 ikiwa necessary; this
            # ensures that the Rounded signal will be raised.
            ikiwa len(ans._int) <= context.prec:
                expdiff = context.prec + 1 - len(ans._int)
                ans = _dec_from_triple(ans._sign, ans._int+'0'*expdiff,
                                       ans._exp-expdiff)

            # create a copy of the current context, ukijumuisha cleared flags/traps
            newcontext = context.copy()
            newcontext.clear_flags()
            kila exception kwenye _signals:
                newcontext.traps[exception] = 0

            # round kwenye the new context
            ans = ans._fix(newcontext)

            #  ashiria Inexact, na ikiwa necessary, Underflow
            newcontext._raise_error(Inexact)
            ikiwa newcontext.flags[Subnormal]:
                newcontext._raise_error(Underflow)

            # propagate signals to the original context; _fix could
            # have raised any of Overflow, Underflow, Subnormal,
            # Inexact, Rounded, Clamped.  Overflow needs the correct
            # arguments.  Note that the order of the exceptions is
            # important here.
            ikiwa newcontext.flags[Overflow]:
                context._raise_error(Overflow, 'above Emax', ans._sign)
            kila exception kwenye Underflow, Subnormal, Inexact, Rounded, Clamped:
                ikiwa newcontext.flags[exception]:
                    context._raise_error(exception)

        isipokua:
            ans = ans._fix(context)

        rudisha ans

    eleza __rpow__(self, other, context=Tupu):
        """Swaps self/other na returns __pow__."""
        other = _convert_other(other)
        ikiwa other ni NotImplemented:
            rudisha other
        rudisha other.__pow__(self, context=context)

    eleza normalize(self, context=Tupu):
        """Normalize- strip trailing 0s, change anything equal to 0 to 0e0"""

        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa self._is_special:
            ans = self._check_nans(context=context)
            ikiwa ans:
                rudisha ans

        dup = self._fix(context)
        ikiwa dup._isinfinity():
            rudisha dup

        ikiwa sio dup:
            rudisha _dec_from_triple(dup._sign, '0', 0)
        exp_max = [context.Emax, context.Etop()][context.clamp]
        end = len(dup._int)
        exp = dup._exp
        wakati dup._int[end-1] == '0' na exp < exp_max:
            exp += 1
            end -= 1
        rudisha _dec_from_triple(dup._sign, dup._int[:end], exp)

    eleza quantize(self, exp, rounding=Tupu, context=Tupu):
        """Quantize self so its exponent ni the same as that of exp.

        Similar to self._rescale(exp._exp) but ukijumuisha error checking.
        """
        exp = _convert_other(exp, raiseit=Kweli)

        ikiwa context ni Tupu:
            context = getcontext()
        ikiwa rounding ni Tupu:
            rounding = context.rounding

        ikiwa self._is_special ama exp._is_special:
            ans = self._check_nans(exp, context)
            ikiwa ans:
                rudisha ans

            ikiwa exp._isinfinity() ama self._isinfinity():
                ikiwa exp._isinfinity() na self._isinfinity():
                    rudisha Decimal(self)  # ikiwa both are inf, it ni OK
                rudisha context._raise_error(InvalidOperation,
                                        'quantize ukijumuisha one INF')

        # exp._exp should be between Etiny na Emax
        ikiwa sio (context.Etiny() <= exp._exp <= context.Emax):
            rudisha context._raise_error(InvalidOperation,
                   'target exponent out of bounds kwenye quantize')

        ikiwa sio self:
            ans = _dec_from_triple(self._sign, '0', exp._exp)
            rudisha ans._fix(context)

        self_adjusted = self.adjusted()
        ikiwa self_adjusted > context.Emax:
            rudisha context._raise_error(InvalidOperation,
                                        'exponent of quantize result too large kila current context')
        ikiwa self_adjusted - exp._exp + 1 > context.prec:
            rudisha context._raise_error(InvalidOperation,
                                        'quantize result has too many digits kila current context')

        ans = self._rescale(exp._exp, rounding)
        ikiwa ans.adjusted() > context.Emax:
            rudisha context._raise_error(InvalidOperation,
                                        'exponent of quantize result too large kila current context')
        ikiwa len(ans._int) > context.prec:
            rudisha context._raise_error(InvalidOperation,
                                        'quantize result has too many digits kila current context')

        #  ashiria appropriate flags
        ikiwa ans na ans.adjusted() < context.Emin:
            context._raise_error(Subnormal)
        ikiwa ans._exp > self._exp:
            ikiwa ans != self:
                context._raise_error(Inexact)
            context._raise_error(Rounded)

        # call to fix takes care of any necessary folddown, and
        # signals Clamped ikiwa necessary
        ans = ans._fix(context)
        rudisha ans

    eleza same_quantum(self, other, context=Tupu):
        """Return Kweli ikiwa self na other have the same exponent; otherwise
        rudisha Uongo.

        If either operand ni a special value, the following rules are used:
           * rudisha Kweli ikiwa both operands are infinities
           * rudisha Kweli ikiwa both operands are NaNs
           * otherwise, rudisha Uongo.
        """
        other = _convert_other(other, raiseit=Kweli)
        ikiwa self._is_special ama other._is_special:
            rudisha (self.is_nan() na other.is_nan() or
                    self.is_infinite() na other.is_infinite())
        rudisha self._exp == other._exp

    eleza _rescale(self, exp, rounding):
        """Rescale self so that the exponent ni exp, either by padding ukijumuisha zeros
        ama by truncating digits, using the given rounding mode.

        Specials are returned without change.  This operation is
        quiet: it raises no flags, na uses no information kutoka the
        context.

        exp = exp to scale to (an integer)
        rounding = rounding mode
        """
        ikiwa self._is_special:
            rudisha Decimal(self)
        ikiwa sio self:
            rudisha _dec_from_triple(self._sign, '0', exp)

        ikiwa self._exp >= exp:
            # pad answer ukijumuisha zeros ikiwa necessary
            rudisha _dec_from_triple(self._sign,
                                        self._int + '0'*(self._exp - exp), exp)

        # too many digits; round na lose data.  If self.adjusted() <
        # exp-1, replace self by 10**(exp-1) before rounding
        digits = len(self._int) + self._exp - exp
        ikiwa digits < 0:
            self = _dec_from_triple(self._sign, '1', exp-1)
            digits = 0
        this_function = self._pick_rounding_function[rounding]
        changed = this_function(self, digits)
        coeff = self._int[:digits] ama '0'
        ikiwa changed == 1:
            coeff = str(int(coeff)+1)
        rudisha _dec_from_triple(self._sign, coeff, exp)

    eleza _round(self, places, rounding):
        """Round a nonzero, nonspecial Decimal to a fixed number of
        significant figures, using the given rounding mode.

        Infinities, NaNs na zeros are returned unaltered.

        This operation ni quiet: it raises no flags, na uses no
        information kutoka the context.

        """
        ikiwa places <= 0:
             ashiria ValueError("argument should be at least 1 kwenye _round")
        ikiwa self._is_special ama sio self:
            rudisha Decimal(self)
        ans = self._rescale(self.adjusted()+1-places, rounding)
        # it can happen that the rescale alters the adjusted exponent;
        # kila example when rounding 99.97 to 3 significant figures.
        # When this happens we end up ukijumuisha an extra 0 at the end of
        # the number; a second rescale fixes this.
        ikiwa ans.adjusted() != self.adjusted():
            ans = ans._rescale(ans.adjusted()+1-places, rounding)
        rudisha ans

    eleza to_integral_exact(self, rounding=Tupu, context=Tupu):
        """Rounds to a nearby integer.

        If no rounding mode ni specified, take the rounding mode from
        the context.  This method raises the Rounded na Inexact flags
        when appropriate.

        See also: to_integral_value, which does exactly the same as
        this method except that it doesn't  ashiria Inexact ama Rounded.
        """
        ikiwa self._is_special:
            ans = self._check_nans(context=context)
            ikiwa ans:
                rudisha ans
            rudisha Decimal(self)
        ikiwa self._exp >= 0:
            rudisha Decimal(self)
        ikiwa sio self:
            rudisha _dec_from_triple(self._sign, '0', 0)
        ikiwa context ni Tupu:
            context = getcontext()
        ikiwa rounding ni Tupu:
            rounding = context.rounding
        ans = self._rescale(0, rounding)
        ikiwa ans != self:
            context._raise_error(Inexact)
        context._raise_error(Rounded)
        rudisha ans

    eleza to_integral_value(self, rounding=Tupu, context=Tupu):
        """Rounds to the nearest integer, without raising inexact, rounded."""
        ikiwa context ni Tupu:
            context = getcontext()
        ikiwa rounding ni Tupu:
            rounding = context.rounding
        ikiwa self._is_special:
            ans = self._check_nans(context=context)
            ikiwa ans:
                rudisha ans
            rudisha Decimal(self)
        ikiwa self._exp >= 0:
            rudisha Decimal(self)
        isipokua:
            rudisha self._rescale(0, rounding)

    # the method name changed, but we provide also the old one, kila compatibility
    to_integral = to_integral_value

    eleza sqrt(self, context=Tupu):
        """Return the square root of self."""
        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa self._is_special:
            ans = self._check_nans(context=context)
            ikiwa ans:
                rudisha ans

            ikiwa self._isinfinity() na self._sign == 0:
                rudisha Decimal(self)

        ikiwa sio self:
            # exponent = self._exp // 2.  sqrt(-0) = -0
            ans = _dec_from_triple(self._sign, '0', self._exp // 2)
            rudisha ans._fix(context)

        ikiwa self._sign == 1:
            rudisha context._raise_error(InvalidOperation, 'sqrt(-x), x > 0')

        # At this point self represents a positive number.  Let p be
        # the desired precision na express self kwenye the form c*100**e
        # ukijumuisha c a positive real number na e an integer, c na e
        # being chosen so that 100**(p-1) <= c < 100**p.  Then the
        # (exact) square root of self ni sqrt(c)*10**e, na 10**(p-1)
        # <= sqrt(c) < 10**p, so the closest representable Decimal at
        # precision p ni n*10**e where n = round_half_even(sqrt(c)),
        # the closest integer to sqrt(c) ukijumuisha the even integer chosen
        # kwenye the case of a tie.
        #
        # To ensure correct rounding kwenye all cases, we use the
        # following trick: we compute the square root to an extra
        # place (precision p+1 instead of precision p), rounding down.
        # Then, ikiwa the result ni inexact na its last digit ni 0 ama 5,
        # we increase the last digit to 1 ama 6 respectively; ikiwa it's
        # exact we leave the last digit alone.  Now the final round to
        # p places (or fewer kwenye the case of underflow) will round
        # correctly na  ashiria the appropriate flags.

        # use an extra digit of precision
        prec = context.prec+1

        # write argument kwenye the form c*100**e where e = self._exp//2
        # ni the 'ideal' exponent, to be used ikiwa the square root is
        # exactly representable.  l ni the number of 'digits' of c in
        # base 100, so that 100**(l-1) <= c < 100**l.
        op = _WorkRep(self)
        e = op.exp >> 1
        ikiwa op.exp & 1:
            c = op.int * 10
            l = (len(self._int) >> 1) + 1
        isipokua:
            c = op.int
            l = len(self._int)+1 >> 1

        # rescale so that c has exactly prec base 100 'digits'
        shift = prec-l
        ikiwa shift >= 0:
            c *= 100**shift
            exact = Kweli
        isipokua:
            c, remainder = divmod(c, 100**-shift)
            exact = sio remainder
        e -= shift

        # find n = floor(sqrt(c)) using Newton's method
        n = 10**prec
        wakati Kweli:
            q = c//n
            ikiwa n <= q:
                koma
            isipokua:
                n = n + q >> 1
        exact = exact na n*n == c

        ikiwa exact:
            # result ni exact; rescale to use ideal exponent e
            ikiwa shift >= 0:
                # assert n % 10**shift == 0
                n //= 10**shift
            isipokua:
                n *= 10**-shift
            e += shift
        isipokua:
            # result ni sio exact; fix last digit as described above
            ikiwa n % 5 == 0:
                n += 1

        ans = _dec_from_triple(0, str(n), e)

        # round, na fit to current context
        context = context._shallow_copy()
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        ans = ans._fix(context)
        context.rounding = rounding

        rudisha ans

    eleza max(self, other, context=Tupu):
        """Returns the larger value.

        Like max(self, other) except ikiwa one ni sio a number, returns
        NaN (and signals ikiwa one ni sNaN).  Also rounds.
        """
        other = _convert_other(other, raiseit=Kweli)

        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa self._is_special ama other._is_special:
            # If one operand ni a quiet NaN na the other ni number, then the
            # number ni always returned
            sn = self._isnan()
            on = other._isnan()
            ikiwa sn ama on:
                ikiwa on == 1 na sn == 0:
                    rudisha self._fix(context)
                ikiwa sn == 1 na on == 0:
                    rudisha other._fix(context)
                rudisha self._check_nans(other, context)

        c = self._cmp(other)
        ikiwa c == 0:
            # If both operands are finite na equal kwenye numerical value
            # then an ordering ni applied:
            #
            # If the signs differ then max returns the operand ukijumuisha the
            # positive sign na min returns the operand ukijumuisha the negative sign
            #
            # If the signs are the same then the exponent ni used to select
            # the result.  This ni exactly the ordering used kwenye compare_total.
            c = self.compare_total(other)

        ikiwa c == -1:
            ans = other
        isipokua:
            ans = self

        rudisha ans._fix(context)

    eleza min(self, other, context=Tupu):
        """Returns the smaller value.

        Like min(self, other) except ikiwa one ni sio a number, returns
        NaN (and signals ikiwa one ni sNaN).  Also rounds.
        """
        other = _convert_other(other, raiseit=Kweli)

        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa self._is_special ama other._is_special:
            # If one operand ni a quiet NaN na the other ni number, then the
            # number ni always returned
            sn = self._isnan()
            on = other._isnan()
            ikiwa sn ama on:
                ikiwa on == 1 na sn == 0:
                    rudisha self._fix(context)
                ikiwa sn == 1 na on == 0:
                    rudisha other._fix(context)
                rudisha self._check_nans(other, context)

        c = self._cmp(other)
        ikiwa c == 0:
            c = self.compare_total(other)

        ikiwa c == -1:
            ans = self
        isipokua:
            ans = other

        rudisha ans._fix(context)

    eleza _isinteger(self):
        """Returns whether self ni an integer"""
        ikiwa self._is_special:
            rudisha Uongo
        ikiwa self._exp >= 0:
            rudisha Kweli
        rest = self._int[self._exp:]
        rudisha rest == '0'*len(rest)

    eleza _iseven(self):
        """Returns Kweli ikiwa self ni even.  Assumes self ni an integer."""
        ikiwa sio self ama self._exp > 0:
            rudisha Kweli
        rudisha self._int[-1+self._exp] kwenye '02468'

    eleza adjusted(self):
        """Return the adjusted exponent of self"""
        jaribu:
            rudisha self._exp + len(self._int) - 1
        # If NaN ama Infinity, self._exp ni string
        except TypeError:
            rudisha 0

    eleza canonical(self):
        """Returns the same Decimal object.

        As we do sio have different encodings kila the same number, the
        received object already ni kwenye its canonical form.
        """
        rudisha self

    eleza compare_signal(self, other, context=Tupu):
        """Compares self to the other operand numerically.

        It's pretty much like compare(), but all NaNs signal, ukijumuisha signaling
        NaNs taking precedence over quiet NaNs.
        """
        other = _convert_other(other, raiseit = Kweli)
        ans = self._compare_check_nans(other, context)
        ikiwa ans:
            rudisha ans
        rudisha self.compare(other, context=context)

    eleza compare_total(self, other, context=Tupu):
        """Compares self to other using the abstract representations.

        This ni sio like the standard compare, which use their numerical
        value. Note that a total ordering ni defined kila all possible abstract
        representations.
        """
        other = _convert_other(other, raiseit=Kweli)

        # ikiwa one ni negative na the other ni positive, it's easy
        ikiwa self._sign na sio other._sign:
            rudisha _NegativeOne
        ikiwa sio self._sign na other._sign:
            rudisha _One
        sign = self._sign

        # let's handle both NaN types
        self_nan = self._isnan()
        other_nan = other._isnan()
        ikiwa self_nan ama other_nan:
            ikiwa self_nan == other_nan:
                # compare payloads as though they're integers
                self_key = len(self._int), self._int
                other_key = len(other._int), other._int
                ikiwa self_key < other_key:
                    ikiwa sign:
                        rudisha _One
                    isipokua:
                        rudisha _NegativeOne
                ikiwa self_key > other_key:
                    ikiwa sign:
                        rudisha _NegativeOne
                    isipokua:
                        rudisha _One
                rudisha _Zero

            ikiwa sign:
                ikiwa self_nan == 1:
                    rudisha _NegativeOne
                ikiwa other_nan == 1:
                    rudisha _One
                ikiwa self_nan == 2:
                    rudisha _NegativeOne
                ikiwa other_nan == 2:
                    rudisha _One
            isipokua:
                ikiwa self_nan == 1:
                    rudisha _One
                ikiwa other_nan == 1:
                    rudisha _NegativeOne
                ikiwa self_nan == 2:
                    rudisha _One
                ikiwa other_nan == 2:
                    rudisha _NegativeOne

        ikiwa self < other:
            rudisha _NegativeOne
        ikiwa self > other:
            rudisha _One

        ikiwa self._exp < other._exp:
            ikiwa sign:
                rudisha _One
            isipokua:
                rudisha _NegativeOne
        ikiwa self._exp > other._exp:
            ikiwa sign:
                rudisha _NegativeOne
            isipokua:
                rudisha _One
        rudisha _Zero


    eleza compare_total_mag(self, other, context=Tupu):
        """Compares self to other using abstract repr., ignoring sign.

        Like compare_total, but ukijumuisha operand's sign ignored na assumed to be 0.
        """
        other = _convert_other(other, raiseit=Kweli)

        s = self.copy_abs()
        o = other.copy_abs()
        rudisha s.compare_total(o)

    eleza copy_abs(self):
        """Returns a copy ukijumuisha the sign set to 0. """
        rudisha _dec_from_triple(0, self._int, self._exp, self._is_special)

    eleza copy_negate(self):
        """Returns a copy ukijumuisha the sign inverted."""
        ikiwa self._sign:
            rudisha _dec_from_triple(0, self._int, self._exp, self._is_special)
        isipokua:
            rudisha _dec_from_triple(1, self._int, self._exp, self._is_special)

    eleza copy_sign(self, other, context=Tupu):
        """Returns self ukijumuisha the sign of other."""
        other = _convert_other(other, raiseit=Kweli)
        rudisha _dec_from_triple(other._sign, self._int,
                                self._exp, self._is_special)

    eleza exp(self, context=Tupu):
        """Returns e ** self."""

        ikiwa context ni Tupu:
            context = getcontext()

        # exp(NaN) = NaN
        ans = self._check_nans(context=context)
        ikiwa ans:
            rudisha ans

        # exp(-Infinity) = 0
        ikiwa self._isinfinity() == -1:
            rudisha _Zero

        # exp(0) = 1
        ikiwa sio self:
            rudisha _One

        # exp(Infinity) = Infinity
        ikiwa self._isinfinity() == 1:
            rudisha Decimal(self)

        # the result ni now guaranteed to be inexact (the true
        # mathematical result ni transcendental). There's no need to
        #  ashiria Rounded na Inexact here---they'll always be raised as
        # a result of the call to _fix.
        p = context.prec
        adj = self.adjusted()

        # we only need to do any computation kila quite a small range
        # of adjusted exponents---kila example, -29 <= adj <= 10 for
        # the default context.  For smaller exponent the result is
        # indistinguishable kutoka 1 at the given precision, wakati for
        # larger exponent the result either overflows ama underflows.
        ikiwa self._sign == 0 na adj > len(str((context.Emax+1)*3)):
            # overflow
            ans = _dec_from_triple(0, '1', context.Emax+1)
        elikiwa self._sign == 1 na adj > len(str((-context.Etiny()+1)*3)):
            # underflow to 0
            ans = _dec_from_triple(0, '1', context.Etiny()-1)
        elikiwa self._sign == 0 na adj < -p:
            # p+1 digits; final round will  ashiria correct flags
            ans = _dec_from_triple(0, '1' + '0'*(p-1) + '1', -p)
        elikiwa self._sign == 1 na adj < -p-1:
            # p+1 digits; final round will  ashiria correct flags
            ans = _dec_from_triple(0, '9'*(p+1), -p-1)
        # general case
        isipokua:
            op = _WorkRep(self)
            c, e = op.int, op.exp
            ikiwa op.sign == 1:
                c = -c

            # compute correctly rounded result: increase precision by
            # 3 digits at a time until we get an unambiguously
            # roundable result
            extra = 3
            wakati Kweli:
                coeff, exp = _dexp(c, e, p+extra)
                ikiwa coeff % (5*10**(len(str(coeff))-p-1)):
                    koma
                extra += 3

            ans = _dec_from_triple(0, str(coeff), exp)

        # at this stage, ans should round correctly ukijumuisha *any*
        # rounding mode, sio just ukijumuisha ROUND_HALF_EVEN
        context = context._shallow_copy()
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        ans = ans._fix(context)
        context.rounding = rounding

        rudisha ans

    eleza is_canonical(self):
        """Return Kweli ikiwa self ni canonical; otherwise rudisha Uongo.

        Currently, the encoding of a Decimal instance ni always
        canonical, so this method returns Kweli kila any Decimal.
        """
        rudisha Kweli

    eleza is_finite(self):
        """Return Kweli ikiwa self ni finite; otherwise rudisha Uongo.

        A Decimal instance ni considered finite ikiwa it ni neither
        infinite nor a NaN.
        """
        rudisha sio self._is_special

    eleza is_infinite(self):
        """Return Kweli ikiwa self ni infinite; otherwise rudisha Uongo."""
        rudisha self._exp == 'F'

    eleza is_nan(self):
        """Return Kweli ikiwa self ni a qNaN ama sNaN; otherwise rudisha Uongo."""
        rudisha self._exp kwenye ('n', 'N')

    eleza is_normal(self, context=Tupu):
        """Return Kweli ikiwa self ni a normal number; otherwise rudisha Uongo."""
        ikiwa self._is_special ama sio self:
            rudisha Uongo
        ikiwa context ni Tupu:
            context = getcontext()
        rudisha context.Emin <= self.adjusted()

    eleza is_qnan(self):
        """Return Kweli ikiwa self ni a quiet NaN; otherwise rudisha Uongo."""
        rudisha self._exp == 'n'

    eleza is_signed(self):
        """Return Kweli ikiwa self ni negative; otherwise rudisha Uongo."""
        rudisha self._sign == 1

    eleza is_snan(self):
        """Return Kweli ikiwa self ni a signaling NaN; otherwise rudisha Uongo."""
        rudisha self._exp == 'N'

    eleza is_subnormal(self, context=Tupu):
        """Return Kweli ikiwa self ni subnormal; otherwise rudisha Uongo."""
        ikiwa self._is_special ama sio self:
            rudisha Uongo
        ikiwa context ni Tupu:
            context = getcontext()
        rudisha self.adjusted() < context.Emin

    eleza is_zero(self):
        """Return Kweli ikiwa self ni a zero; otherwise rudisha Uongo."""
        rudisha sio self._is_special na self._int == '0'

    eleza _ln_exp_bound(self):
        """Compute a lower bound kila the adjusted exponent of self.ln().
        In other words, compute r such that self.ln() >= 10**r.  Assumes
        that self ni finite na positive na that self != 1.
        """

        # kila 0.1 <= x <= 10 we use the inequalities 1-1/x <= ln(x) <= x-1
        adj = self._exp + len(self._int) - 1
        ikiwa adj >= 1:
            # argument >= 10; we use 23/10 = 2.3 as a lower bound kila ln(10)
            rudisha len(str(adj*23//10)) - 1
        ikiwa adj <= -2:
            # argument <= 0.1
            rudisha len(str((-1-adj)*23//10)) - 1
        op = _WorkRep(self)
        c, e = op.int, op.exp
        ikiwa adj == 0:
            # 1 < self < 10
            num = str(c-10**-e)
            den = str(c)
            rudisha len(num) - len(den) - (num < den)
        # adj == -1, 0.1 <= self < 1
        rudisha e + len(str(10**-e - c)) - 1


    eleza ln(self, context=Tupu):
        """Returns the natural (base e) logarithm of self."""

        ikiwa context ni Tupu:
            context = getcontext()

        # ln(NaN) = NaN
        ans = self._check_nans(context=context)
        ikiwa ans:
            rudisha ans

        # ln(0.0) == -Infinity
        ikiwa sio self:
            rudisha _NegativeInfinity

        # ln(Infinity) = Infinity
        ikiwa self._isinfinity() == 1:
            rudisha _Infinity

        # ln(1.0) == 0.0
        ikiwa self == _One:
            rudisha _Zero

        # ln(negative) raises InvalidOperation
        ikiwa self._sign == 1:
            rudisha context._raise_error(InvalidOperation,
                                        'ln of a negative value')

        # result ni irrational, so necessarily inexact
        op = _WorkRep(self)
        c, e = op.int, op.exp
        p = context.prec

        # correctly rounded result: repeatedly increase precision by 3
        # until we get an unambiguously roundable result
        places = p - self._ln_exp_bound() + 2 # at least p+3 places
        wakati Kweli:
            coeff = _dlog(c, e, places)
            # assert len(str(abs(coeff)))-p >= 1
            ikiwa coeff % (5*10**(len(str(abs(coeff)))-p-1)):
                koma
            places += 3
        ans = _dec_from_triple(int(coeff<0), str(abs(coeff)), -places)

        context = context._shallow_copy()
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        ans = ans._fix(context)
        context.rounding = rounding
        rudisha ans

    eleza _log10_exp_bound(self):
        """Compute a lower bound kila the adjusted exponent of self.log10().
        In other words, find r such that self.log10() >= 10**r.
        Assumes that self ni finite na positive na that self != 1.
        """

        # For x >= 10 ama x < 0.1 we only need a bound on the integer
        # part of log10(self), na this comes directly kutoka the
        # exponent of x.  For 0.1 <= x <= 10 we use the inequalities
        # 1-1/x <= log(x) <= x-1. If x > 1 we have |log10(x)| >
        # (1-1/x)/2.31 > 0.  If x < 1 then |log10(x)| > (1-x)/2.31 > 0

        adj = self._exp + len(self._int) - 1
        ikiwa adj >= 1:
            # self >= 10
            rudisha len(str(adj))-1
        ikiwa adj <= -2:
            # self < 0.1
            rudisha len(str(-1-adj))-1
        op = _WorkRep(self)
        c, e = op.int, op.exp
        ikiwa adj == 0:
            # 1 < self < 10
            num = str(c-10**-e)
            den = str(231*c)
            rudisha len(num) - len(den) - (num < den) + 2
        # adj == -1, 0.1 <= self < 1
        num = str(10**-e-c)
        rudisha len(num) + e - (num < "231") - 1

    eleza log10(self, context=Tupu):
        """Returns the base 10 logarithm of self."""

        ikiwa context ni Tupu:
            context = getcontext()

        # log10(NaN) = NaN
        ans = self._check_nans(context=context)
        ikiwa ans:
            rudisha ans

        # log10(0.0) == -Infinity
        ikiwa sio self:
            rudisha _NegativeInfinity

        # log10(Infinity) = Infinity
        ikiwa self._isinfinity() == 1:
            rudisha _Infinity

        # log10(negative ama -Infinity) raises InvalidOperation
        ikiwa self._sign == 1:
            rudisha context._raise_error(InvalidOperation,
                                        'log10 of a negative value')

        # log10(10**n) = n
        ikiwa self._int[0] == '1' na self._int[1:] == '0'*(len(self._int) - 1):
            # answer may need rounding
            ans = Decimal(self._exp + len(self._int) - 1)
        isipokua:
            # result ni irrational, so necessarily inexact
            op = _WorkRep(self)
            c, e = op.int, op.exp
            p = context.prec

            # correctly rounded result: repeatedly increase precision
            # until result ni unambiguously roundable
            places = p-self._log10_exp_bound()+2
            wakati Kweli:
                coeff = _dlog10(c, e, places)
                # assert len(str(abs(coeff)))-p >= 1
                ikiwa coeff % (5*10**(len(str(abs(coeff)))-p-1)):
                    koma
                places += 3
            ans = _dec_from_triple(int(coeff<0), str(abs(coeff)), -places)

        context = context._shallow_copy()
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        ans = ans._fix(context)
        context.rounding = rounding
        rudisha ans

    eleza logb(self, context=Tupu):
        """ Returns the exponent of the magnitude of self's MSD.

        The result ni the integer which ni the exponent of the magnitude
        of the most significant digit of self (as though it were truncated
        to a single digit wakati maintaining the value of that digit and
        without limiting the resulting exponent).
        """
        # logb(NaN) = NaN
        ans = self._check_nans(context=context)
        ikiwa ans:
            rudisha ans

        ikiwa context ni Tupu:
            context = getcontext()

        # logb(+/-Inf) = +Inf
        ikiwa self._isinfinity():
            rudisha _Infinity

        # logb(0) = -Inf, DivisionByZero
        ikiwa sio self:
            rudisha context._raise_error(DivisionByZero, 'logb(0)', 1)

        # otherwise, simply rudisha the adjusted exponent of self, as a
        # Decimal.  Note that no attempt ni made to fit the result
        # into the current context.
        ans = Decimal(self.adjusted())
        rudisha ans._fix(context)

    eleza _islogical(self):
        """Return Kweli ikiwa self ni a logical operand.

        For being logical, it must be a finite number ukijumuisha a sign of 0,
        an exponent of 0, na a coefficient whose digits must all be
        either 0 ama 1.
        """
        ikiwa self._sign != 0 ama self._exp != 0:
            rudisha Uongo
        kila dig kwenye self._int:
            ikiwa dig sio kwenye '01':
                rudisha Uongo
        rudisha Kweli

    eleza _fill_logical(self, context, opa, opb):
        dikiwa = context.prec - len(opa)
        ikiwa dikiwa > 0:
            opa = '0'*dikiwa + opa
        elikiwa dikiwa < 0:
            opa = opa[-context.prec:]
        dikiwa = context.prec - len(opb)
        ikiwa dikiwa > 0:
            opb = '0'*dikiwa + opb
        elikiwa dikiwa < 0:
            opb = opb[-context.prec:]
        rudisha opa, opb

    eleza logical_and(self, other, context=Tupu):
        """Applies an 'and' operation between self na other's digits."""
        ikiwa context ni Tupu:
            context = getcontext()

        other = _convert_other(other, raiseit=Kweli)

        ikiwa sio self._islogical() ama sio other._islogical():
            rudisha context._raise_error(InvalidOperation)

        # fill to context.prec
        (opa, opb) = self._fill_logical(context, self._int, other._int)

        # make the operation, na clean starting zeroes
        result = "".join([str(int(a)&int(b)) kila a,b kwenye zip(opa,opb)])
        rudisha _dec_from_triple(0, result.lstrip('0') ama '0', 0)

    eleza logical_invert(self, context=Tupu):
        """Invert all its digits."""
        ikiwa context ni Tupu:
            context = getcontext()
        rudisha self.logical_xor(_dec_from_triple(0,'1'*context.prec,0),
                                context)

    eleza logical_or(self, other, context=Tupu):
        """Applies an 'or' operation between self na other's digits."""
        ikiwa context ni Tupu:
            context = getcontext()

        other = _convert_other(other, raiseit=Kweli)

        ikiwa sio self._islogical() ama sio other._islogical():
            rudisha context._raise_error(InvalidOperation)

        # fill to context.prec
        (opa, opb) = self._fill_logical(context, self._int, other._int)

        # make the operation, na clean starting zeroes
        result = "".join([str(int(a)|int(b)) kila a,b kwenye zip(opa,opb)])
        rudisha _dec_from_triple(0, result.lstrip('0') ama '0', 0)

    eleza logical_xor(self, other, context=Tupu):
        """Applies an 'xor' operation between self na other's digits."""
        ikiwa context ni Tupu:
            context = getcontext()

        other = _convert_other(other, raiseit=Kweli)

        ikiwa sio self._islogical() ama sio other._islogical():
            rudisha context._raise_error(InvalidOperation)

        # fill to context.prec
        (opa, opb) = self._fill_logical(context, self._int, other._int)

        # make the operation, na clean starting zeroes
        result = "".join([str(int(a)^int(b)) kila a,b kwenye zip(opa,opb)])
        rudisha _dec_from_triple(0, result.lstrip('0') ama '0', 0)

    eleza max_mag(self, other, context=Tupu):
        """Compares the values numerically ukijumuisha their sign ignored."""
        other = _convert_other(other, raiseit=Kweli)

        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa self._is_special ama other._is_special:
            # If one operand ni a quiet NaN na the other ni number, then the
            # number ni always returned
            sn = self._isnan()
            on = other._isnan()
            ikiwa sn ama on:
                ikiwa on == 1 na sn == 0:
                    rudisha self._fix(context)
                ikiwa sn == 1 na on == 0:
                    rudisha other._fix(context)
                rudisha self._check_nans(other, context)

        c = self.copy_abs()._cmp(other.copy_abs())
        ikiwa c == 0:
            c = self.compare_total(other)

        ikiwa c == -1:
            ans = other
        isipokua:
            ans = self

        rudisha ans._fix(context)

    eleza min_mag(self, other, context=Tupu):
        """Compares the values numerically ukijumuisha their sign ignored."""
        other = _convert_other(other, raiseit=Kweli)

        ikiwa context ni Tupu:
            context = getcontext()

        ikiwa self._is_special ama other._is_special:
            # If one operand ni a quiet NaN na the other ni number, then the
            # number ni always returned
            sn = self._isnan()
            on = other._isnan()
            ikiwa sn ama on:
                ikiwa on == 1 na sn == 0:
                    rudisha self._fix(context)
                ikiwa sn == 1 na on == 0:
                    rudisha other._fix(context)
                rudisha self._check_nans(other, context)

        c = self.copy_abs()._cmp(other.copy_abs())
        ikiwa c == 0:
            c = self.compare_total(other)

        ikiwa c == -1:
            ans = self
        isipokua:
            ans = other

        rudisha ans._fix(context)

    eleza next_minus(self, context=Tupu):
        """Returns the largest representable number smaller than itself."""
        ikiwa context ni Tupu:
            context = getcontext()

        ans = self._check_nans(context=context)
        ikiwa ans:
            rudisha ans

        ikiwa self._isinfinity() == -1:
            rudisha _NegativeInfinity
        ikiwa self._isinfinity() == 1:
            rudisha _dec_from_triple(0, '9'*context.prec, context.Etop())

        context = context.copy()
        context._set_rounding(ROUND_FLOOR)
        context._ignore_all_flags()
        new_self = self._fix(context)
        ikiwa new_self != self:
            rudisha new_self
        rudisha self.__sub__(_dec_from_triple(0, '1', context.Etiny()-1),
                            context)

    eleza next_plus(self, context=Tupu):
        """Returns the smallest representable number larger than itself."""
        ikiwa context ni Tupu:
            context = getcontext()

        ans = self._check_nans(context=context)
        ikiwa ans:
            rudisha ans

        ikiwa self._isinfinity() == 1:
            rudisha _Infinity
        ikiwa self._isinfinity() == -1:
            rudisha _dec_from_triple(1, '9'*context.prec, context.Etop())

        context = context.copy()
        context._set_rounding(ROUND_CEILING)
        context._ignore_all_flags()
        new_self = self._fix(context)
        ikiwa new_self != self:
            rudisha new_self
        rudisha self.__add__(_dec_from_triple(0, '1', context.Etiny()-1),
                            context)

    eleza next_toward(self, other, context=Tupu):
        """Returns the number closest to self, kwenye the direction towards other.

        The result ni the closest representable number to self
        (excluding self) that ni kwenye the direction towards other,
        unless both have the same value.  If the two operands are
        numerically equal, then the result ni a copy of self ukijumuisha the
        sign set to be the same as the sign of other.
        """
        other = _convert_other(other, raiseit=Kweli)

        ikiwa context ni Tupu:
            context = getcontext()

        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha ans

        comparison = self._cmp(other)
        ikiwa comparison == 0:
            rudisha self.copy_sign(other)

        ikiwa comparison == -1:
            ans = self.next_plus(context)
        isipokua: # comparison == 1
            ans = self.next_minus(context)

        # decide which flags to  ashiria using value of ans
        ikiwa ans._isinfinity():
            context._raise_error(Overflow,
                                 'Infinite result kutoka next_toward',
                                 ans._sign)
            context._raise_error(Inexact)
            context._raise_error(Rounded)
        elikiwa ans.adjusted() < context.Emin:
            context._raise_error(Underflow)
            context._raise_error(Subnormal)
            context._raise_error(Inexact)
            context._raise_error(Rounded)
            # ikiwa precision == 1 then we don't  ashiria Clamped kila a
            # result 0E-Etiny.
            ikiwa sio ans:
                context._raise_error(Clamped)

        rudisha ans

    eleza number_class(self, context=Tupu):
        """Returns an indication of the kundi of self.

        The kundi ni one of the following strings:
          sNaN
          NaN
          -Infinity
          -Normal
          -Subnormal
          -Zero
          +Zero
          +Subnormal
          +Normal
          +Infinity
        """
        ikiwa self.is_snan():
            rudisha "sNaN"
        ikiwa self.is_qnan():
            rudisha "NaN"
        inf = self._isinfinity()
        ikiwa inf == 1:
            rudisha "+Infinity"
        ikiwa inf == -1:
            rudisha "-Infinity"
        ikiwa self.is_zero():
            ikiwa self._sign:
                rudisha "-Zero"
            isipokua:
                rudisha "+Zero"
        ikiwa context ni Tupu:
            context = getcontext()
        ikiwa self.is_subnormal(context=context):
            ikiwa self._sign:
                rudisha "-Subnormal"
            isipokua:
                rudisha "+Subnormal"
        # just a normal, regular, boring number, :)
        ikiwa self._sign:
            rudisha "-Normal"
        isipokua:
            rudisha "+Normal"

    eleza radix(self):
        """Just returns 10, as this ni Decimal, :)"""
        rudisha Decimal(10)

    eleza rotate(self, other, context=Tupu):
        """Returns a rotated copy of self, value-of-other times."""
        ikiwa context ni Tupu:
            context = getcontext()

        other = _convert_other(other, raiseit=Kweli)

        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha ans

        ikiwa other._exp != 0:
            rudisha context._raise_error(InvalidOperation)
        ikiwa sio (-context.prec <= int(other) <= context.prec):
            rudisha context._raise_error(InvalidOperation)

        ikiwa self._isinfinity():
            rudisha Decimal(self)

        # get values, pad ikiwa necessary
        torot = int(other)
        rotdig = self._int
        topad = context.prec - len(rotdig)
        ikiwa topad > 0:
            rotdig = '0'*topad + rotdig
        elikiwa topad < 0:
            rotdig = rotdig[-topad:]

        # let's rotate!
        rotated = rotdig[torot:] + rotdig[:torot]
        rudisha _dec_from_triple(self._sign,
                                rotated.lstrip('0') ama '0', self._exp)

    eleza scaleb(self, other, context=Tupu):
        """Returns self operand after adding the second value to its exp."""
        ikiwa context ni Tupu:
            context = getcontext()

        other = _convert_other(other, raiseit=Kweli)

        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha ans

        ikiwa other._exp != 0:
            rudisha context._raise_error(InvalidOperation)
        liminf = -2 * (context.Emax + context.prec)
        limsup =  2 * (context.Emax + context.prec)
        ikiwa sio (liminf <= int(other) <= limsup):
            rudisha context._raise_error(InvalidOperation)

        ikiwa self._isinfinity():
            rudisha Decimal(self)

        d = _dec_from_triple(self._sign, self._int, self._exp + int(other))
        d = d._fix(context)
        rudisha d

    eleza shift(self, other, context=Tupu):
        """Returns a shifted copy of self, value-of-other times."""
        ikiwa context ni Tupu:
            context = getcontext()

        other = _convert_other(other, raiseit=Kweli)

        ans = self._check_nans(other, context)
        ikiwa ans:
            rudisha ans

        ikiwa other._exp != 0:
            rudisha context._raise_error(InvalidOperation)
        ikiwa sio (-context.prec <= int(other) <= context.prec):
            rudisha context._raise_error(InvalidOperation)

        ikiwa self._isinfinity():
            rudisha Decimal(self)

        # get values, pad ikiwa necessary
        torot = int(other)
        rotdig = self._int
        topad = context.prec - len(rotdig)
        ikiwa topad > 0:
            rotdig = '0'*topad + rotdig
        elikiwa topad < 0:
            rotdig = rotdig[-topad:]

        # let's shift!
        ikiwa torot < 0:
            shifted = rotdig[:torot]
        isipokua:
            shifted = rotdig + '0'*torot
            shifted = shifted[-context.prec:]

        rudisha _dec_from_triple(self._sign,
                                    shifted.lstrip('0') ama '0', self._exp)

    # Support kila pickling, copy, na deepcopy
    eleza __reduce__(self):
        rudisha (self.__class__, (str(self),))

    eleza __copy__(self):
        ikiwa type(self) ni Decimal:
            rudisha self     # I'm immutable; therefore I am my own clone
        rudisha self.__class__(str(self))

    eleza __deepcopy__(self, memo):
        ikiwa type(self) ni Decimal:
            rudisha self     # My components are also immutable
        rudisha self.__class__(str(self))

    # PEP 3101 support.  the _localeconv keyword argument should be
    # considered private: it's provided kila ease of testing only.
    eleza __format__(self, specifier, context=Tupu, _localeconv=Tupu):
        """Format a Decimal instance according to the given specifier.

        The specifier should be a standard format specifier, ukijumuisha the
        form described kwenye PEP 3101.  Formatting types 'e', 'E', 'f',
        'F', 'g', 'G', 'n' na '%' are supported.  If the formatting
        type ni omitted it defaults to 'g' ama 'G', depending on the
        value of context.capitals.
        """

        # Note: PEP 3101 says that ikiwa the type ni sio present then
        # there should be at least one digit after the decimal point.
        # We take the liberty of ignoring this requirement for
        # Decimal---it's presumably there to make sure that
        # format(float, '') behaves similarly to str(float).
        ikiwa context ni Tupu:
            context = getcontext()

        spec = _parse_format_specifier(specifier, _localeconv=_localeconv)

        # special values don't care about the type ama precision
        ikiwa self._is_special:
            sign = _format_sign(self._sign, spec)
            body = str(self.copy_abs())
            ikiwa spec['type'] == '%':
                body += '%'
            rudisha _format_align(sign, body, spec)

        # a type of Tupu defaults to 'g' ama 'G', depending on context
        ikiwa spec['type'] ni Tupu:
            spec['type'] = ['g', 'G'][context.capitals]

        # ikiwa type ni '%', adjust exponent of self accordingly
        ikiwa spec['type'] == '%':
            self = _dec_from_triple(self._sign, self._int, self._exp+2)

        # round ikiwa necessary, taking rounding mode kutoka the context
        rounding = context.rounding
        precision = spec['precision']
        ikiwa precision ni sio Tupu:
            ikiwa spec['type'] kwenye 'eE':
                self = self._round(precision+1, rounding)
            elikiwa spec['type'] kwenye 'fF%':
                self = self._rescale(-precision, rounding)
            elikiwa spec['type'] kwenye 'gG' na len(self._int) > precision:
                self = self._round(precision, rounding)
        # special case: zeros ukijumuisha a positive exponent can't be
        # represented kwenye fixed point; rescale them to 0e0.
        ikiwa sio self na self._exp > 0 na spec['type'] kwenye 'fF%':
            self = self._rescale(0, rounding)

        # figure out placement of the decimal point
        leftdigits = self._exp + len(self._int)
        ikiwa spec['type'] kwenye 'eE':
            ikiwa sio self na precision ni sio Tupu:
                dotplace = 1 - precision
            isipokua:
                dotplace = 1
        elikiwa spec['type'] kwenye 'fF%':
            dotplace = leftdigits
        elikiwa spec['type'] kwenye 'gG':
            ikiwa self._exp <= 0 na leftdigits > -6:
                dotplace = leftdigits
            isipokua:
                dotplace = 1

        # find digits before na after decimal point, na get exponent
        ikiwa dotplace < 0:
            intpart = '0'
            fracpart = '0'*(-dotplace) + self._int
        elikiwa dotplace > len(self._int):
            intpart = self._int + '0'*(dotplace-len(self._int))
            fracpart = ''
        isipokua:
            intpart = self._int[:dotplace] ama '0'
            fracpart = self._int[dotplace:]
        exp = leftdigits-dotplace

        # done ukijumuisha the decimal-specific stuff;  hand over the rest
        # of the formatting to the _format_number function
        rudisha _format_number(self._sign, intpart, fracpart, exp, spec)

eleza _dec_from_triple(sign, coefficient, exponent, special=Uongo):
    """Create a decimal instance directly, without any validation,
    normalization (e.g. removal of leading zeros) ama argument
    conversion.

    This function ni kila *internal use only*.
    """

    self = object.__new__(Decimal)
    self._sign = sign
    self._int = coefficient
    self._exp = exponent
    self._is_special = special

    rudisha self

# Register Decimal as a kind of Number (an abstract base class).
# However, do sio register it as Real (because Decimals are not
# interoperable ukijumuisha floats).
_numbers.Number.register(Decimal)


##### Context kundi #######################################################

kundi _ContextManager(object):
    """Context manager kundi to support localcontext().

      Sets a copy of the supplied context kwenye __enter__() na restores
      the previous decimal context kwenye __exit__()
    """
    eleza __init__(self, new_context):
        self.new_context = new_context.copy()
    eleza __enter__(self):
        self.saved_context = getcontext()
        setcontext(self.new_context)
        rudisha self.new_context
    eleza __exit__(self, t, v, tb):
        setcontext(self.saved_context)

kundi Context(object):
    """Contains the context kila a Decimal instance.

    Contains:
    prec - precision (kila use kwenye rounding, division, square roots..)
    rounding - rounding type (how you round)
    traps - If traps[exception] = 1, then the exception is
                    raised when it ni caused.  Otherwise, a value is
                    substituted in.
    flags  - When an exception ni caused, flags[exception] ni set.
             (Whether ama sio the trap_enabler ni set)
             Should be reset by user of Decimal instance.
    Emin -   Minimum exponent
    Emax -   Maximum exponent
    capitals -      If 1, 1*10^1 ni printed as 1E+1.
                    If 0, printed as 1e1
    clamp -  If 1, change exponents ikiwa too high (Default 0)
    """

    eleza __init__(self, prec=Tupu, rounding=Tupu, Emin=Tupu, Emax=Tupu,
                       capitals=Tupu, clamp=Tupu, flags=Tupu, traps=Tupu,
                       _ignored_flags=Tupu):
        # Set defaults; kila everything except flags na _ignored_flags,
        # inherit kutoka DefaultContext.
        jaribu:
            dc = DefaultContext
        except NameError:
            pass

        self.prec = prec ikiwa prec ni sio Tupu isipokua dc.prec
        self.rounding = rounding ikiwa rounding ni sio Tupu isipokua dc.rounding
        self.Emin = Emin ikiwa Emin ni sio Tupu isipokua dc.Emin
        self.Emax = Emax ikiwa Emax ni sio Tupu isipokua dc.Emax
        self.capitals = capitals ikiwa capitals ni sio Tupu isipokua dc.capitals
        self.clamp = clamp ikiwa clamp ni sio Tupu isipokua dc.clamp

        ikiwa _ignored_flags ni Tupu:
            self._ignored_flags = []
        isipokua:
            self._ignored_flags = _ignored_flags

        ikiwa traps ni Tupu:
            self.traps = dc.traps.copy()
        elikiwa sio isinstance(traps, dict):
            self.traps = dict((s, int(s kwenye traps)) kila s kwenye _signals + traps)
        isipokua:
            self.traps = traps

        ikiwa flags ni Tupu:
            self.flags = dict.fromkeys(_signals, 0)
        elikiwa sio isinstance(flags, dict):
            self.flags = dict((s, int(s kwenye flags)) kila s kwenye _signals + flags)
        isipokua:
            self.flags = flags

    eleza _set_integer_check(self, name, value, vmin, vmax):
        ikiwa sio isinstance(value, int):
             ashiria TypeError("%s must be an integer" % name)
        ikiwa vmin == '-inf':
            ikiwa value > vmax:
                 ashiria ValueError("%s must be kwenye [%s, %d]. got: %s" % (name, vmin, vmax, value))
        elikiwa vmax == 'inf':
            ikiwa value < vmin:
                 ashiria ValueError("%s must be kwenye [%d, %s]. got: %s" % (name, vmin, vmax, value))
        isipokua:
            ikiwa value < vmin ama value > vmax:
                 ashiria ValueError("%s must be kwenye [%d, %d]. got %s" % (name, vmin, vmax, value))
        rudisha object.__setattr__(self, name, value)

    eleza _set_signal_dict(self, name, d):
        ikiwa sio isinstance(d, dict):
             ashiria TypeError("%s must be a signal dict" % d)
        kila key kwenye d:
            ikiwa sio key kwenye _signals:
                 ashiria KeyError("%s ni sio a valid signal dict" % d)
        kila key kwenye _signals:
            ikiwa sio key kwenye d:
                 ashiria KeyError("%s ni sio a valid signal dict" % d)
        rudisha object.__setattr__(self, name, d)

    eleza __setattr__(self, name, value):
        ikiwa name == 'prec':
            rudisha self._set_integer_check(name, value, 1, 'inf')
        elikiwa name == 'Emin':
            rudisha self._set_integer_check(name, value, '-inf', 0)
        elikiwa name == 'Emax':
            rudisha self._set_integer_check(name, value, 0, 'inf')
        elikiwa name == 'capitals':
            rudisha self._set_integer_check(name, value, 0, 1)
        elikiwa name == 'clamp':
            rudisha self._set_integer_check(name, value, 0, 1)
        elikiwa name == 'rounding':
            ikiwa sio value kwenye _rounding_modes:
                #  ashiria TypeError even kila strings to have consistency
                # among various implementations.
                 ashiria TypeError("%s: invalid rounding mode" % value)
            rudisha object.__setattr__(self, name, value)
        elikiwa name == 'flags' ama name == 'traps':
            rudisha self._set_signal_dict(name, value)
        elikiwa name == '_ignored_flags':
            rudisha object.__setattr__(self, name, value)
        isipokua:
             ashiria AttributeError(
                "'decimal.Context' object has no attribute '%s'" % name)

    eleza __delattr__(self, name):
         ashiria AttributeError("%s cannot be deleted" % name)

    # Support kila pickling, copy, na deepcopy
    eleza __reduce__(self):
        flags = [sig kila sig, v kwenye self.flags.items() ikiwa v]
        traps = [sig kila sig, v kwenye self.traps.items() ikiwa v]
        rudisha (self.__class__,
                (self.prec, self.rounding, self.Emin, self.Emax,
                 self.capitals, self.clamp, flags, traps))

    eleza __repr__(self):
        """Show the current context."""
        s = []
        s.append('Context(prec=%(prec)d, rounding=%(rounding)s, '
                 'Emin=%(Emin)d, Emax=%(Emax)d, capitals=%(capitals)d, '
                 'clamp=%(clamp)d'
                 % vars(self))
        names = [f.__name__ kila f, v kwenye self.flags.items() ikiwa v]
        s.append('flags=[' + ', '.join(names) + ']')
        names = [t.__name__ kila t, v kwenye self.traps.items() ikiwa v]
        s.append('traps=[' + ', '.join(names) + ']')
        rudisha ', '.join(s) + ')'

    eleza clear_flags(self):
        """Reset all flags to zero"""
        kila flag kwenye self.flags:
            self.flags[flag] = 0

    eleza clear_traps(self):
        """Reset all traps to zero"""
        kila flag kwenye self.traps:
            self.traps[flag] = 0

    eleza _shallow_copy(self):
        """Returns a shallow copy kutoka self."""
        nc = Context(self.prec, self.rounding, self.Emin, self.Emax,
                     self.capitals, self.clamp, self.flags, self.traps,
                     self._ignored_flags)
        rudisha nc

    eleza copy(self):
        """Returns a deep copy kutoka self."""
        nc = Context(self.prec, self.rounding, self.Emin, self.Emax,
                     self.capitals, self.clamp,
                     self.flags.copy(), self.traps.copy(),
                     self._ignored_flags)
        rudisha nc
    __copy__ = copy

    eleza _raise_error(self, condition, explanation = Tupu, *args):
        """Handles an error

        If the flag ni kwenye _ignored_flags, returns the default response.
        Otherwise, it sets the flag, then, ikiwa the corresponding
        trap_enabler ni set, it reraises the exception.  Otherwise, it returns
        the default value after setting the flag.
        """
        error = _condition_map.get(condition, condition)
        ikiwa error kwenye self._ignored_flags:
            # Don't touch the flag
            rudisha error().handle(self, *args)

        self.flags[error] = 1
        ikiwa sio self.traps[error]:
            # The errors define how to handle themselves.
            rudisha condition().handle(self, *args)

        # Errors should only be risked on copies of the context
        # self._ignored_flags = []
         ashiria error(explanation)

    eleza _ignore_all_flags(self):
        """Ignore all flags, ikiwa they are raised"""
        rudisha self._ignore_flags(*_signals)

    eleza _ignore_flags(self, *flags):
        """Ignore the flags, ikiwa they are raised"""
        # Do sio mutate-- This way, copies of a context leave the original
        # alone.
        self._ignored_flags = (self._ignored_flags + list(flags))
        rudisha list(flags)

    eleza _regard_flags(self, *flags):
        """Stop ignoring the flags, ikiwa they are raised"""
        ikiwa flags na isinstance(flags[0], (tuple,list)):
            flags = flags[0]
        kila flag kwenye flags:
            self._ignored_flags.remove(flag)

    # We inherit object.__hash__, so we must deny this explicitly
    __hash__ = Tupu

    eleza Etiny(self):
        """Returns Etiny (= Emin - prec + 1)"""
        rudisha int(self.Emin - self.prec + 1)

    eleza Etop(self):
        """Returns maximum exponent (= Emax - prec + 1)"""
        rudisha int(self.Emax - self.prec + 1)

    eleza _set_rounding(self, type):
        """Sets the rounding type.

        Sets the rounding type, na returns the current (previous)
        rounding type.  Often used like:

        context = context.copy()
        # so you don't change the calling context
        # ikiwa an error occurs kwenye the middle.
        rounding = context._set_rounding(ROUND_UP)
        val = self.__sub__(other, context=context)
        context._set_rounding(rounding)

        This will make it round up kila that operation.
        """
        rounding = self.rounding
        self.rounding = type
        rudisha rounding

    eleza create_decimal(self, num='0'):
        """Creates a new Decimal instance but using self as context.

        This method implements the to-number operation of the
        IBM Decimal specification."""

        ikiwa isinstance(num, str) na (num != num.strip() ama '_' kwenye num):
            rudisha self._raise_error(ConversionSyntax,
                                     "trailing ama leading whitespace na "
                                     "underscores are sio permitted.")

        d = Decimal(num, context=self)
        ikiwa d._isnan() na len(d._int) > self.prec - self.clamp:
            rudisha self._raise_error(ConversionSyntax,
                                     "diagnostic info too long kwenye NaN")
        rudisha d._fix(self)

    eleza create_decimal_from_float(self, f):
        """Creates a new Decimal instance kutoka a float but rounding using self
        as the context.

        >>> context = Context(prec=5, rounding=ROUND_DOWN)
        >>> context.create_decimal_from_float(3.1415926535897932)
        Decimal('3.1415')
        >>> context = Context(prec=5, traps=[Inexact])
        >>> context.create_decimal_from_float(3.1415926535897932)
        Traceback (most recent call last):
            ...
        decimal.Inexact: Tupu

        """
        d = Decimal.from_float(f)       # An exact conversion
        rudisha d._fix(self)             # Apply the context rounding

    # Methods
    eleza abs(self, a):
        """Returns the absolute value of the operand.

        If the operand ni negative, the result ni the same as using the minus
        operation on the operand.  Otherwise, the result ni the same as using
        the plus operation on the operand.

        >>> ExtendedContext.abs(Decimal('2.1'))
        Decimal('2.1')
        >>> ExtendedContext.abs(Decimal('-100'))
        Decimal('100')
        >>> ExtendedContext.abs(Decimal('101.5'))
        Decimal('101.5')
        >>> ExtendedContext.abs(Decimal('-101.5'))
        Decimal('101.5')
        >>> ExtendedContext.abs(-1)
        Decimal('1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.__abs__(context=self)

    eleza add(self, a, b):
        """Return the sum of the two operands.

        >>> ExtendedContext.add(Decimal('12'), Decimal('7.00'))
        Decimal('19.00')
        >>> ExtendedContext.add(Decimal('1E+2'), Decimal('1.01E+4'))
        Decimal('1.02E+4')
        >>> ExtendedContext.add(1, Decimal(2))
        Decimal('3')
        >>> ExtendedContext.add(Decimal(8), 5)
        Decimal('13')
        >>> ExtendedContext.add(5, 5)
        Decimal('10')
        """
        a = _convert_other(a, raiseit=Kweli)
        r = a.__add__(b, context=self)
        ikiwa r ni NotImplemented:
             ashiria TypeError("Unable to convert %s to Decimal" % b)
        isipokua:
            rudisha r

    eleza _apply(self, a):
        rudisha str(a._fix(self))

    eleza canonical(self, a):
        """Returns the same Decimal object.

        As we do sio have different encodings kila the same number, the
        received object already ni kwenye its canonical form.

        >>> ExtendedContext.canonical(Decimal('2.50'))
        Decimal('2.50')
        """
        ikiwa sio isinstance(a, Decimal):
             ashiria TypeError("canonical requires a Decimal as an argument.")
        rudisha a.canonical()

    eleza compare(self, a, b):
        """Compares values numerically.

        If the signs of the operands differ, a value representing each operand
        ('-1' ikiwa the operand ni less than zero, '0' ikiwa the operand ni zero or
        negative zero, ama '1' ikiwa the operand ni greater than zero) ni used in
        place of that operand kila the comparison instead of the actual
        operand.

        The comparison ni then effected by subtracting the second operand from
        the first na then returning a value according to the result of the
        subtraction: '-1' ikiwa the result ni less than zero, '0' ikiwa the result is
        zero ama negative zero, ama '1' ikiwa the result ni greater than zero.

        >>> ExtendedContext.compare(Decimal('2.1'), Decimal('3'))
        Decimal('-1')
        >>> ExtendedContext.compare(Decimal('2.1'), Decimal('2.1'))
        Decimal('0')
        >>> ExtendedContext.compare(Decimal('2.1'), Decimal('2.10'))
        Decimal('0')
        >>> ExtendedContext.compare(Decimal('3'), Decimal('2.1'))
        Decimal('1')
        >>> ExtendedContext.compare(Decimal('2.1'), Decimal('-3'))
        Decimal('1')
        >>> ExtendedContext.compare(Decimal('-3'), Decimal('2.1'))
        Decimal('-1')
        >>> ExtendedContext.compare(1, 2)
        Decimal('-1')
        >>> ExtendedContext.compare(Decimal(1), 2)
        Decimal('-1')
        >>> ExtendedContext.compare(1, Decimal(2))
        Decimal('-1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.compare(b, context=self)

    eleza compare_signal(self, a, b):
        """Compares the values of the two operands numerically.

        It's pretty much like compare(), but all NaNs signal, ukijumuisha signaling
        NaNs taking precedence over quiet NaNs.

        >>> c = ExtendedContext
        >>> c.compare_signal(Decimal('2.1'), Decimal('3'))
        Decimal('-1')
        >>> c.compare_signal(Decimal('2.1'), Decimal('2.1'))
        Decimal('0')
        >>> c.flags[InvalidOperation] = 0
        >>> andika(c.flags[InvalidOperation])
        0
        >>> c.compare_signal(Decimal('NaN'), Decimal('2.1'))
        Decimal('NaN')
        >>> andika(c.flags[InvalidOperation])
        1
        >>> c.flags[InvalidOperation] = 0
        >>> andika(c.flags[InvalidOperation])
        0
        >>> c.compare_signal(Decimal('sNaN'), Decimal('2.1'))
        Decimal('NaN')
        >>> andika(c.flags[InvalidOperation])
        1
        >>> c.compare_signal(-1, 2)
        Decimal('-1')
        >>> c.compare_signal(Decimal(-1), 2)
        Decimal('-1')
        >>> c.compare_signal(-1, Decimal(2))
        Decimal('-1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.compare_signal(b, context=self)

    eleza compare_total(self, a, b):
        """Compares two operands using their abstract representation.

        This ni sio like the standard compare, which use their numerical
        value. Note that a total ordering ni defined kila all possible abstract
        representations.

        >>> ExtendedContext.compare_total(Decimal('12.73'), Decimal('127.9'))
        Decimal('-1')
        >>> ExtendedContext.compare_total(Decimal('-127'),  Decimal('12'))
        Decimal('-1')
        >>> ExtendedContext.compare_total(Decimal('12.30'), Decimal('12.3'))
        Decimal('-1')
        >>> ExtendedContext.compare_total(Decimal('12.30'), Decimal('12.30'))
        Decimal('0')
        >>> ExtendedContext.compare_total(Decimal('12.3'),  Decimal('12.300'))
        Decimal('1')
        >>> ExtendedContext.compare_total(Decimal('12.3'),  Decimal('NaN'))
        Decimal('-1')
        >>> ExtendedContext.compare_total(1, 2)
        Decimal('-1')
        >>> ExtendedContext.compare_total(Decimal(1), 2)
        Decimal('-1')
        >>> ExtendedContext.compare_total(1, Decimal(2))
        Decimal('-1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.compare_total(b)

    eleza compare_total_mag(self, a, b):
        """Compares two operands using their abstract representation ignoring sign.

        Like compare_total, but ukijumuisha operand's sign ignored na assumed to be 0.
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.compare_total_mag(b)

    eleza copy_abs(self, a):
        """Returns a copy of the operand ukijumuisha the sign set to 0.

        >>> ExtendedContext.copy_abs(Decimal('2.1'))
        Decimal('2.1')
        >>> ExtendedContext.copy_abs(Decimal('-100'))
        Decimal('100')
        >>> ExtendedContext.copy_abs(-1)
        Decimal('1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.copy_abs()

    eleza copy_decimal(self, a):
        """Returns a copy of the decimal object.

        >>> ExtendedContext.copy_decimal(Decimal('2.1'))
        Decimal('2.1')
        >>> ExtendedContext.copy_decimal(Decimal('-1.00'))
        Decimal('-1.00')
        >>> ExtendedContext.copy_decimal(1)
        Decimal('1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha Decimal(a)

    eleza copy_negate(self, a):
        """Returns a copy of the operand ukijumuisha the sign inverted.

        >>> ExtendedContext.copy_negate(Decimal('101.5'))
        Decimal('-101.5')
        >>> ExtendedContext.copy_negate(Decimal('-101.5'))
        Decimal('101.5')
        >>> ExtendedContext.copy_negate(1)
        Decimal('-1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.copy_negate()

    eleza copy_sign(self, a, b):
        """Copies the second operand's sign to the first one.

        In detail, it returns a copy of the first operand ukijumuisha the sign
        equal to the sign of the second operand.

        >>> ExtendedContext.copy_sign(Decimal( '1.50'), Decimal('7.33'))
        Decimal('1.50')
        >>> ExtendedContext.copy_sign(Decimal('-1.50'), Decimal('7.33'))
        Decimal('1.50')
        >>> ExtendedContext.copy_sign(Decimal( '1.50'), Decimal('-7.33'))
        Decimal('-1.50')
        >>> ExtendedContext.copy_sign(Decimal('-1.50'), Decimal('-7.33'))
        Decimal('-1.50')
        >>> ExtendedContext.copy_sign(1, -2)
        Decimal('-1')
        >>> ExtendedContext.copy_sign(Decimal(1), -2)
        Decimal('-1')
        >>> ExtendedContext.copy_sign(1, Decimal(-2))
        Decimal('-1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.copy_sign(b)

    eleza divide(self, a, b):
        """Decimal division kwenye a specified context.

        >>> ExtendedContext.divide(Decimal('1'), Decimal('3'))
        Decimal('0.333333333')
        >>> ExtendedContext.divide(Decimal('2'), Decimal('3'))
        Decimal('0.666666667')
        >>> ExtendedContext.divide(Decimal('5'), Decimal('2'))
        Decimal('2.5')
        >>> ExtendedContext.divide(Decimal('1'), Decimal('10'))
        Decimal('0.1')
        >>> ExtendedContext.divide(Decimal('12'), Decimal('12'))
        Decimal('1')
        >>> ExtendedContext.divide(Decimal('8.00'), Decimal('2'))
        Decimal('4.00')
        >>> ExtendedContext.divide(Decimal('2.400'), Decimal('2.0'))
        Decimal('1.20')
        >>> ExtendedContext.divide(Decimal('1000'), Decimal('100'))
        Decimal('10')
        >>> ExtendedContext.divide(Decimal('1000'), Decimal('1'))
        Decimal('1000')
        >>> ExtendedContext.divide(Decimal('2.40E+6'), Decimal('2'))
        Decimal('1.20E+6')
        >>> ExtendedContext.divide(5, 5)
        Decimal('1')
        >>> ExtendedContext.divide(Decimal(5), 5)
        Decimal('1')
        >>> ExtendedContext.divide(5, Decimal(5))
        Decimal('1')
        """
        a = _convert_other(a, raiseit=Kweli)
        r = a.__truediv__(b, context=self)
        ikiwa r ni NotImplemented:
             ashiria TypeError("Unable to convert %s to Decimal" % b)
        isipokua:
            rudisha r

    eleza divide_int(self, a, b):
        """Divides two numbers na returns the integer part of the result.

        >>> ExtendedContext.divide_int(Decimal('2'), Decimal('3'))
        Decimal('0')
        >>> ExtendedContext.divide_int(Decimal('10'), Decimal('3'))
        Decimal('3')
        >>> ExtendedContext.divide_int(Decimal('1'), Decimal('0.3'))
        Decimal('3')
        >>> ExtendedContext.divide_int(10, 3)
        Decimal('3')
        >>> ExtendedContext.divide_int(Decimal(10), 3)
        Decimal('3')
        >>> ExtendedContext.divide_int(10, Decimal(3))
        Decimal('3')
        """
        a = _convert_other(a, raiseit=Kweli)
        r = a.__floordiv__(b, context=self)
        ikiwa r ni NotImplemented:
             ashiria TypeError("Unable to convert %s to Decimal" % b)
        isipokua:
            rudisha r

    eleza divmod(self, a, b):
        """Return (a // b, a % b).

        >>> ExtendedContext.divmod(Decimal(8), Decimal(3))
        (Decimal('2'), Decimal('2'))
        >>> ExtendedContext.divmod(Decimal(8), Decimal(4))
        (Decimal('2'), Decimal('0'))
        >>> ExtendedContext.divmod(8, 4)
        (Decimal('2'), Decimal('0'))
        >>> ExtendedContext.divmod(Decimal(8), 4)
        (Decimal('2'), Decimal('0'))
        >>> ExtendedContext.divmod(8, Decimal(4))
        (Decimal('2'), Decimal('0'))
        """
        a = _convert_other(a, raiseit=Kweli)
        r = a.__divmod__(b, context=self)
        ikiwa r ni NotImplemented:
             ashiria TypeError("Unable to convert %s to Decimal" % b)
        isipokua:
            rudisha r

    eleza exp(self, a):
        """Returns e ** a.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.exp(Decimal('-Infinity'))
        Decimal('0')
        >>> c.exp(Decimal('-1'))
        Decimal('0.367879441')
        >>> c.exp(Decimal('0'))
        Decimal('1')
        >>> c.exp(Decimal('1'))
        Decimal('2.71828183')
        >>> c.exp(Decimal('0.693147181'))
        Decimal('2.00000000')
        >>> c.exp(Decimal('+Infinity'))
        Decimal('Infinity')
        >>> c.exp(10)
        Decimal('22026.4658')
        """
        a =_convert_other(a, raiseit=Kweli)
        rudisha a.exp(context=self)

    eleza fma(self, a, b, c):
        """Returns a multiplied by b, plus c.

        The first two operands are multiplied together, using multiply,
        the third operand ni then added to the result of that
        multiplication, using add, all ukijumuisha only one final rounding.

        >>> ExtendedContext.fma(Decimal('3'), Decimal('5'), Decimal('7'))
        Decimal('22')
        >>> ExtendedContext.fma(Decimal('3'), Decimal('-5'), Decimal('7'))
        Decimal('-8')
        >>> ExtendedContext.fma(Decimal('888565290'), Decimal('1557.96930'), Decimal('-86087.7578'))
        Decimal('1.38435736E+12')
        >>> ExtendedContext.fma(1, 3, 4)
        Decimal('7')
        >>> ExtendedContext.fma(1, Decimal(3), 4)
        Decimal('7')
        >>> ExtendedContext.fma(1, 3, Decimal(4))
        Decimal('7')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.fma(b, c, context=self)

    eleza is_canonical(self, a):
        """Return Kweli ikiwa the operand ni canonical; otherwise rudisha Uongo.

        Currently, the encoding of a Decimal instance ni always
        canonical, so this method returns Kweli kila any Decimal.

        >>> ExtendedContext.is_canonical(Decimal('2.50'))
        Kweli
        """
        ikiwa sio isinstance(a, Decimal):
             ashiria TypeError("is_canonical requires a Decimal as an argument.")
        rudisha a.is_canonical()

    eleza is_finite(self, a):
        """Return Kweli ikiwa the operand ni finite; otherwise rudisha Uongo.

        A Decimal instance ni considered finite ikiwa it ni neither
        infinite nor a NaN.

        >>> ExtendedContext.is_finite(Decimal('2.50'))
        Kweli
        >>> ExtendedContext.is_finite(Decimal('-0.3'))
        Kweli
        >>> ExtendedContext.is_finite(Decimal('0'))
        Kweli
        >>> ExtendedContext.is_finite(Decimal('Inf'))
        Uongo
        >>> ExtendedContext.is_finite(Decimal('NaN'))
        Uongo
        >>> ExtendedContext.is_finite(1)
        Kweli
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_finite()

    eleza is_infinite(self, a):
        """Return Kweli ikiwa the operand ni infinite; otherwise rudisha Uongo.

        >>> ExtendedContext.is_infinite(Decimal('2.50'))
        Uongo
        >>> ExtendedContext.is_infinite(Decimal('-Inf'))
        Kweli
        >>> ExtendedContext.is_infinite(Decimal('NaN'))
        Uongo
        >>> ExtendedContext.is_infinite(1)
        Uongo
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_infinite()

    eleza is_nan(self, a):
        """Return Kweli ikiwa the operand ni a qNaN ama sNaN;
        otherwise rudisha Uongo.

        >>> ExtendedContext.is_nan(Decimal('2.50'))
        Uongo
        >>> ExtendedContext.is_nan(Decimal('NaN'))
        Kweli
        >>> ExtendedContext.is_nan(Decimal('-sNaN'))
        Kweli
        >>> ExtendedContext.is_nan(1)
        Uongo
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_nan()

    eleza is_normal(self, a):
        """Return Kweli ikiwa the operand ni a normal number;
        otherwise rudisha Uongo.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.is_normal(Decimal('2.50'))
        Kweli
        >>> c.is_normal(Decimal('0.1E-999'))
        Uongo
        >>> c.is_normal(Decimal('0.00'))
        Uongo
        >>> c.is_normal(Decimal('-Inf'))
        Uongo
        >>> c.is_normal(Decimal('NaN'))
        Uongo
        >>> c.is_normal(1)
        Kweli
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_normal(context=self)

    eleza is_qnan(self, a):
        """Return Kweli ikiwa the operand ni a quiet NaN; otherwise rudisha Uongo.

        >>> ExtendedContext.is_qnan(Decimal('2.50'))
        Uongo
        >>> ExtendedContext.is_qnan(Decimal('NaN'))
        Kweli
        >>> ExtendedContext.is_qnan(Decimal('sNaN'))
        Uongo
        >>> ExtendedContext.is_qnan(1)
        Uongo
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_qnan()

    eleza is_signed(self, a):
        """Return Kweli ikiwa the operand ni negative; otherwise rudisha Uongo.

        >>> ExtendedContext.is_signed(Decimal('2.50'))
        Uongo
        >>> ExtendedContext.is_signed(Decimal('-12'))
        Kweli
        >>> ExtendedContext.is_signed(Decimal('-0'))
        Kweli
        >>> ExtendedContext.is_signed(8)
        Uongo
        >>> ExtendedContext.is_signed(-8)
        Kweli
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_signed()

    eleza is_snan(self, a):
        """Return Kweli ikiwa the operand ni a signaling NaN;
        otherwise rudisha Uongo.

        >>> ExtendedContext.is_snan(Decimal('2.50'))
        Uongo
        >>> ExtendedContext.is_snan(Decimal('NaN'))
        Uongo
        >>> ExtendedContext.is_snan(Decimal('sNaN'))
        Kweli
        >>> ExtendedContext.is_snan(1)
        Uongo
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_snan()

    eleza is_subnormal(self, a):
        """Return Kweli ikiwa the operand ni subnormal; otherwise rudisha Uongo.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.is_subnormal(Decimal('2.50'))
        Uongo
        >>> c.is_subnormal(Decimal('0.1E-999'))
        Kweli
        >>> c.is_subnormal(Decimal('0.00'))
        Uongo
        >>> c.is_subnormal(Decimal('-Inf'))
        Uongo
        >>> c.is_subnormal(Decimal('NaN'))
        Uongo
        >>> c.is_subnormal(1)
        Uongo
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_subnormal(context=self)

    eleza is_zero(self, a):
        """Return Kweli ikiwa the operand ni a zero; otherwise rudisha Uongo.

        >>> ExtendedContext.is_zero(Decimal('0'))
        Kweli
        >>> ExtendedContext.is_zero(Decimal('2.50'))
        Uongo
        >>> ExtendedContext.is_zero(Decimal('-0E+2'))
        Kweli
        >>> ExtendedContext.is_zero(1)
        Uongo
        >>> ExtendedContext.is_zero(0)
        Kweli
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.is_zero()

    eleza ln(self, a):
        """Returns the natural (base e) logarithm of the operand.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.ln(Decimal('0'))
        Decimal('-Infinity')
        >>> c.ln(Decimal('1.000'))
        Decimal('0')
        >>> c.ln(Decimal('2.71828183'))
        Decimal('1.00000000')
        >>> c.ln(Decimal('10'))
        Decimal('2.30258509')
        >>> c.ln(Decimal('+Infinity'))
        Decimal('Infinity')
        >>> c.ln(1)
        Decimal('0')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.ln(context=self)

    eleza log10(self, a):
        """Returns the base 10 logarithm of the operand.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.log10(Decimal('0'))
        Decimal('-Infinity')
        >>> c.log10(Decimal('0.001'))
        Decimal('-3')
        >>> c.log10(Decimal('1.000'))
        Decimal('0')
        >>> c.log10(Decimal('2'))
        Decimal('0.301029996')
        >>> c.log10(Decimal('10'))
        Decimal('1')
        >>> c.log10(Decimal('70'))
        Decimal('1.84509804')
        >>> c.log10(Decimal('+Infinity'))
        Decimal('Infinity')
        >>> c.log10(0)
        Decimal('-Infinity')
        >>> c.log10(1)
        Decimal('0')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.log10(context=self)

    eleza logb(self, a):
        """ Returns the exponent of the magnitude of the operand's MSD.

        The result ni the integer which ni the exponent of the magnitude
        of the most significant digit of the operand (as though the
        operand were truncated to a single digit wakati maintaining the
        value of that digit na without limiting the resulting exponent).

        >>> ExtendedContext.logb(Decimal('250'))
        Decimal('2')
        >>> ExtendedContext.logb(Decimal('2.50'))
        Decimal('0')
        >>> ExtendedContext.logb(Decimal('0.03'))
        Decimal('-2')
        >>> ExtendedContext.logb(Decimal('0'))
        Decimal('-Infinity')
        >>> ExtendedContext.logb(1)
        Decimal('0')
        >>> ExtendedContext.logb(10)
        Decimal('1')
        >>> ExtendedContext.logb(100)
        Decimal('2')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.logb(context=self)

    eleza logical_and(self, a, b):
        """Applies the logical operation 'and' between each operand's digits.

        The operands must be both logical numbers.

        >>> ExtendedContext.logical_and(Decimal('0'), Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.logical_and(Decimal('0'), Decimal('1'))
        Decimal('0')
        >>> ExtendedContext.logical_and(Decimal('1'), Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.logical_and(Decimal('1'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.logical_and(Decimal('1100'), Decimal('1010'))
        Decimal('1000')
        >>> ExtendedContext.logical_and(Decimal('1111'), Decimal('10'))
        Decimal('10')
        >>> ExtendedContext.logical_and(110, 1101)
        Decimal('100')
        >>> ExtendedContext.logical_and(Decimal(110), 1101)
        Decimal('100')
        >>> ExtendedContext.logical_and(110, Decimal(1101))
        Decimal('100')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.logical_and(b, context=self)

    eleza logical_invert(self, a):
        """Invert all the digits kwenye the operand.

        The operand must be a logical number.

        >>> ExtendedContext.logical_invert(Decimal('0'))
        Decimal('111111111')
        >>> ExtendedContext.logical_invert(Decimal('1'))
        Decimal('111111110')
        >>> ExtendedContext.logical_invert(Decimal('111111111'))
        Decimal('0')
        >>> ExtendedContext.logical_invert(Decimal('101010101'))
        Decimal('10101010')
        >>> ExtendedContext.logical_invert(1101)
        Decimal('111110010')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.logical_invert(context=self)

    eleza logical_or(self, a, b):
        """Applies the logical operation 'or' between each operand's digits.

        The operands must be both logical numbers.

        >>> ExtendedContext.logical_or(Decimal('0'), Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.logical_or(Decimal('0'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.logical_or(Decimal('1'), Decimal('0'))
        Decimal('1')
        >>> ExtendedContext.logical_or(Decimal('1'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.logical_or(Decimal('1100'), Decimal('1010'))
        Decimal('1110')
        >>> ExtendedContext.logical_or(Decimal('1110'), Decimal('10'))
        Decimal('1110')
        >>> ExtendedContext.logical_or(110, 1101)
        Decimal('1111')
        >>> ExtendedContext.logical_or(Decimal(110), 1101)
        Decimal('1111')
        >>> ExtendedContext.logical_or(110, Decimal(1101))
        Decimal('1111')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.logical_or(b, context=self)

    eleza logical_xor(self, a, b):
        """Applies the logical operation 'xor' between each operand's digits.

        The operands must be both logical numbers.

        >>> ExtendedContext.logical_xor(Decimal('0'), Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.logical_xor(Decimal('0'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.logical_xor(Decimal('1'), Decimal('0'))
        Decimal('1')
        >>> ExtendedContext.logical_xor(Decimal('1'), Decimal('1'))
        Decimal('0')
        >>> ExtendedContext.logical_xor(Decimal('1100'), Decimal('1010'))
        Decimal('110')
        >>> ExtendedContext.logical_xor(Decimal('1111'), Decimal('10'))
        Decimal('1101')
        >>> ExtendedContext.logical_xor(110, 1101)
        Decimal('1011')
        >>> ExtendedContext.logical_xor(Decimal(110), 1101)
        Decimal('1011')
        >>> ExtendedContext.logical_xor(110, Decimal(1101))
        Decimal('1011')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.logical_xor(b, context=self)

    eleza max(self, a, b):
        """max compares two values numerically na returns the maximum.

        If either operand ni a NaN then the general rules apply.
        Otherwise, the operands are compared as though by the compare
        operation.  If they are numerically equal then the left-hand operand
        ni chosen as the result.  Otherwise the maximum (closer to positive
        infinity) of the two operands ni chosen as the result.

        >>> ExtendedContext.max(Decimal('3'), Decimal('2'))
        Decimal('3')
        >>> ExtendedContext.max(Decimal('-10'), Decimal('3'))
        Decimal('3')
        >>> ExtendedContext.max(Decimal('1.0'), Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.max(Decimal('7'), Decimal('NaN'))
        Decimal('7')
        >>> ExtendedContext.max(1, 2)
        Decimal('2')
        >>> ExtendedContext.max(Decimal(1), 2)
        Decimal('2')
        >>> ExtendedContext.max(1, Decimal(2))
        Decimal('2')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.max(b, context=self)

    eleza max_mag(self, a, b):
        """Compares the values numerically ukijumuisha their sign ignored.

        >>> ExtendedContext.max_mag(Decimal('7'), Decimal('NaN'))
        Decimal('7')
        >>> ExtendedContext.max_mag(Decimal('7'), Decimal('-10'))
        Decimal('-10')
        >>> ExtendedContext.max_mag(1, -2)
        Decimal('-2')
        >>> ExtendedContext.max_mag(Decimal(1), -2)
        Decimal('-2')
        >>> ExtendedContext.max_mag(1, Decimal(-2))
        Decimal('-2')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.max_mag(b, context=self)

    eleza min(self, a, b):
        """min compares two values numerically na returns the minimum.

        If either operand ni a NaN then the general rules apply.
        Otherwise, the operands are compared as though by the compare
        operation.  If they are numerically equal then the left-hand operand
        ni chosen as the result.  Otherwise the minimum (closer to negative
        infinity) of the two operands ni chosen as the result.

        >>> ExtendedContext.min(Decimal('3'), Decimal('2'))
        Decimal('2')
        >>> ExtendedContext.min(Decimal('-10'), Decimal('3'))
        Decimal('-10')
        >>> ExtendedContext.min(Decimal('1.0'), Decimal('1'))
        Decimal('1.0')
        >>> ExtendedContext.min(Decimal('7'), Decimal('NaN'))
        Decimal('7')
        >>> ExtendedContext.min(1, 2)
        Decimal('1')
        >>> ExtendedContext.min(Decimal(1), 2)
        Decimal('1')
        >>> ExtendedContext.min(1, Decimal(29))
        Decimal('1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.min(b, context=self)

    eleza min_mag(self, a, b):
        """Compares the values numerically ukijumuisha their sign ignored.

        >>> ExtendedContext.min_mag(Decimal('3'), Decimal('-2'))
        Decimal('-2')
        >>> ExtendedContext.min_mag(Decimal('-3'), Decimal('NaN'))
        Decimal('-3')
        >>> ExtendedContext.min_mag(1, -2)
        Decimal('1')
        >>> ExtendedContext.min_mag(Decimal(1), -2)
        Decimal('1')
        >>> ExtendedContext.min_mag(1, Decimal(-2))
        Decimal('1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.min_mag(b, context=self)

    eleza minus(self, a):
        """Minus corresponds to unary prefix minus kwenye Python.

        The operation ni evaluated using the same rules as subtract; the
        operation minus(a) ni calculated as subtract('0', a) where the '0'
        has the same exponent as the operand.

        >>> ExtendedContext.minus(Decimal('1.3'))
        Decimal('-1.3')
        >>> ExtendedContext.minus(Decimal('-1.3'))
        Decimal('1.3')
        >>> ExtendedContext.minus(1)
        Decimal('-1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.__neg__(context=self)

    eleza multiply(self, a, b):
        """multiply multiplies two operands.

        If either operand ni a special value then the general rules apply.
        Otherwise, the operands are multiplied together
        ('long multiplication'), resulting kwenye a number which may be as long as
        the sum of the lengths of the two operands.

        >>> ExtendedContext.multiply(Decimal('1.20'), Decimal('3'))
        Decimal('3.60')
        >>> ExtendedContext.multiply(Decimal('7'), Decimal('3'))
        Decimal('21')
        >>> ExtendedContext.multiply(Decimal('0.9'), Decimal('0.8'))
        Decimal('0.72')
        >>> ExtendedContext.multiply(Decimal('0.9'), Decimal('-0'))
        Decimal('-0.0')
        >>> ExtendedContext.multiply(Decimal('654321'), Decimal('654321'))
        Decimal('4.28135971E+11')
        >>> ExtendedContext.multiply(7, 7)
        Decimal('49')
        >>> ExtendedContext.multiply(Decimal(7), 7)
        Decimal('49')
        >>> ExtendedContext.multiply(7, Decimal(7))
        Decimal('49')
        """
        a = _convert_other(a, raiseit=Kweli)
        r = a.__mul__(b, context=self)
        ikiwa r ni NotImplemented:
             ashiria TypeError("Unable to convert %s to Decimal" % b)
        isipokua:
            rudisha r

    eleza next_minus(self, a):
        """Returns the largest representable number smaller than a.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> ExtendedContext.next_minus(Decimal('1'))
        Decimal('0.999999999')
        >>> c.next_minus(Decimal('1E-1007'))
        Decimal('0E-1007')
        >>> ExtendedContext.next_minus(Decimal('-1.00000003'))
        Decimal('-1.00000004')
        >>> c.next_minus(Decimal('Infinity'))
        Decimal('9.99999999E+999')
        >>> c.next_minus(1)
        Decimal('0.999999999')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.next_minus(context=self)

    eleza next_plus(self, a):
        """Returns the smallest representable number larger than a.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> ExtendedContext.next_plus(Decimal('1'))
        Decimal('1.00000001')
        >>> c.next_plus(Decimal('-1E-1007'))
        Decimal('-0E-1007')
        >>> ExtendedContext.next_plus(Decimal('-1.00000003'))
        Decimal('-1.00000002')
        >>> c.next_plus(Decimal('-Infinity'))
        Decimal('-9.99999999E+999')
        >>> c.next_plus(1)
        Decimal('1.00000001')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.next_plus(context=self)

    eleza next_toward(self, a, b):
        """Returns the number closest to a, kwenye direction towards b.

        The result ni the closest representable number kutoka the first
        operand (but sio the first operand) that ni kwenye the direction
        towards the second operand, unless the operands have the same
        value.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.next_toward(Decimal('1'), Decimal('2'))
        Decimal('1.00000001')
        >>> c.next_toward(Decimal('-1E-1007'), Decimal('1'))
        Decimal('-0E-1007')
        >>> c.next_toward(Decimal('-1.00000003'), Decimal('0'))
        Decimal('-1.00000002')
        >>> c.next_toward(Decimal('1'), Decimal('0'))
        Decimal('0.999999999')
        >>> c.next_toward(Decimal('1E-1007'), Decimal('-100'))
        Decimal('0E-1007')
        >>> c.next_toward(Decimal('-1.00000003'), Decimal('-10'))
        Decimal('-1.00000004')
        >>> c.next_toward(Decimal('0.00'), Decimal('-0.0000'))
        Decimal('-0.00')
        >>> c.next_toward(0, 1)
        Decimal('1E-1007')
        >>> c.next_toward(Decimal(0), 1)
        Decimal('1E-1007')
        >>> c.next_toward(0, Decimal(1))
        Decimal('1E-1007')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.next_toward(b, context=self)

    eleza normalize(self, a):
        """normalize reduces an operand to its simplest form.

        Essentially a plus operation ukijumuisha all trailing zeros removed kutoka the
        result.

        >>> ExtendedContext.normalize(Decimal('2.1'))
        Decimal('2.1')
        >>> ExtendedContext.normalize(Decimal('-2.0'))
        Decimal('-2')
        >>> ExtendedContext.normalize(Decimal('1.200'))
        Decimal('1.2')
        >>> ExtendedContext.normalize(Decimal('-120'))
        Decimal('-1.2E+2')
        >>> ExtendedContext.normalize(Decimal('120.00'))
        Decimal('1.2E+2')
        >>> ExtendedContext.normalize(Decimal('0.00'))
        Decimal('0')
        >>> ExtendedContext.normalize(6)
        Decimal('6')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.normalize(context=self)

    eleza number_class(self, a):
        """Returns an indication of the kundi of the operand.

        The kundi ni one of the following strings:
          -sNaN
          -NaN
          -Infinity
          -Normal
          -Subnormal
          -Zero
          +Zero
          +Subnormal
          +Normal
          +Infinity

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.number_class(Decimal('Infinity'))
        '+Infinity'
        >>> c.number_class(Decimal('1E-10'))
        '+Normal'
        >>> c.number_class(Decimal('2.50'))
        '+Normal'
        >>> c.number_class(Decimal('0.1E-999'))
        '+Subnormal'
        >>> c.number_class(Decimal('0'))
        '+Zero'
        >>> c.number_class(Decimal('-0'))
        '-Zero'
        >>> c.number_class(Decimal('-0.1E-999'))
        '-Subnormal'
        >>> c.number_class(Decimal('-1E-10'))
        '-Normal'
        >>> c.number_class(Decimal('-2.50'))
        '-Normal'
        >>> c.number_class(Decimal('-Infinity'))
        '-Infinity'
        >>> c.number_class(Decimal('NaN'))
        'NaN'
        >>> c.number_class(Decimal('-NaN'))
        'NaN'
        >>> c.number_class(Decimal('sNaN'))
        'sNaN'
        >>> c.number_class(123)
        '+Normal'
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.number_class(context=self)

    eleza plus(self, a):
        """Plus corresponds to unary prefix plus kwenye Python.

        The operation ni evaluated using the same rules as add; the
        operation plus(a) ni calculated as add('0', a) where the '0'
        has the same exponent as the operand.

        >>> ExtendedContext.plus(Decimal('1.3'))
        Decimal('1.3')
        >>> ExtendedContext.plus(Decimal('-1.3'))
        Decimal('-1.3')
        >>> ExtendedContext.plus(-1)
        Decimal('-1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.__pos__(context=self)

    eleza power(self, a, b, modulo=Tupu):
        """Raises a to the power of b, to modulo ikiwa given.

        With two arguments, compute a**b.  If a ni negative then b
        must be integral.  The result will be inexact unless b is
        integral na the result ni finite na can be expressed exactly
        kwenye 'precision' digits.

        With three arguments, compute (a**b) % modulo.  For the
        three argument form, the following restrictions on the
        arguments hold:

         - all three arguments must be integral
         - b must be nonnegative
         - at least one of a ama b must be nonzero
         - modulo must be nonzero na have at most 'precision' digits

        The result of pow(a, b, modulo) ni identical to the result
        that would be obtained by computing (a**b) % modulo with
        unbounded precision, but ni computed more efficiently.  It is
        always exact.

        >>> c = ExtendedContext.copy()
        >>> c.Emin = -999
        >>> c.Emax = 999
        >>> c.power(Decimal('2'), Decimal('3'))
        Decimal('8')
        >>> c.power(Decimal('-2'), Decimal('3'))
        Decimal('-8')
        >>> c.power(Decimal('2'), Decimal('-3'))
        Decimal('0.125')
        >>> c.power(Decimal('1.7'), Decimal('8'))
        Decimal('69.7575744')
        >>> c.power(Decimal('10'), Decimal('0.301029996'))
        Decimal('2.00000000')
        >>> c.power(Decimal('Infinity'), Decimal('-1'))
        Decimal('0')
        >>> c.power(Decimal('Infinity'), Decimal('0'))
        Decimal('1')
        >>> c.power(Decimal('Infinity'), Decimal('1'))
        Decimal('Infinity')
        >>> c.power(Decimal('-Infinity'), Decimal('-1'))
        Decimal('-0')
        >>> c.power(Decimal('-Infinity'), Decimal('0'))
        Decimal('1')
        >>> c.power(Decimal('-Infinity'), Decimal('1'))
        Decimal('-Infinity')
        >>> c.power(Decimal('-Infinity'), Decimal('2'))
        Decimal('Infinity')
        >>> c.power(Decimal('0'), Decimal('0'))
        Decimal('NaN')

        >>> c.power(Decimal('3'), Decimal('7'), Decimal('16'))
        Decimal('11')
        >>> c.power(Decimal('-3'), Decimal('7'), Decimal('16'))
        Decimal('-11')
        >>> c.power(Decimal('-3'), Decimal('8'), Decimal('16'))
        Decimal('1')
        >>> c.power(Decimal('3'), Decimal('7'), Decimal('-16'))
        Decimal('11')
        >>> c.power(Decimal('23E12345'), Decimal('67E189'), Decimal('123456789'))
        Decimal('11729830')
        >>> c.power(Decimal('-0'), Decimal('17'), Decimal('1729'))
        Decimal('-0')
        >>> c.power(Decimal('-23'), Decimal('0'), Decimal('65537'))
        Decimal('1')
        >>> ExtendedContext.power(7, 7)
        Decimal('823543')
        >>> ExtendedContext.power(Decimal(7), 7)
        Decimal('823543')
        >>> ExtendedContext.power(7, Decimal(7), 2)
        Decimal('1')
        """
        a = _convert_other(a, raiseit=Kweli)
        r = a.__pow__(b, modulo, context=self)
        ikiwa r ni NotImplemented:
             ashiria TypeError("Unable to convert %s to Decimal" % b)
        isipokua:
            rudisha r

    eleza quantize(self, a, b):
        """Returns a value equal to 'a' (rounded), having the exponent of 'b'.

        The coefficient of the result ni derived kutoka that of the left-hand
        operand.  It may be rounded using the current rounding setting (ikiwa the
        exponent ni being increased), multiplied by a positive power of ten (if
        the exponent ni being decreased), ama ni unchanged (ikiwa the exponent is
        already equal to that of the right-hand operand).

        Unlike other operations, ikiwa the length of the coefficient after the
        quantize operation would be greater than precision then an Invalid
        operation condition ni raised.  This guarantees that, unless there is
        an error condition, the exponent of the result of a quantize ni always
        equal to that of the right-hand operand.

        Also unlike other operations, quantize will never  ashiria Underflow, even
        ikiwa the result ni subnormal na inexact.

        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('0.001'))
        Decimal('2.170')
        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('0.01'))
        Decimal('2.17')
        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('0.1'))
        Decimal('2.2')
        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('1e+0'))
        Decimal('2')
        >>> ExtendedContext.quantize(Decimal('2.17'), Decimal('1e+1'))
        Decimal('0E+1')
        >>> ExtendedContext.quantize(Decimal('-Inf'), Decimal('Infinity'))
        Decimal('-Infinity')
        >>> ExtendedContext.quantize(Decimal('2'), Decimal('Infinity'))
        Decimal('NaN')
        >>> ExtendedContext.quantize(Decimal('-0.1'), Decimal('1'))
        Decimal('-0')
        >>> ExtendedContext.quantize(Decimal('-0'), Decimal('1e+5'))
        Decimal('-0E+5')
        >>> ExtendedContext.quantize(Decimal('+35236450.6'), Decimal('1e-2'))
        Decimal('NaN')
        >>> ExtendedContext.quantize(Decimal('-35236450.6'), Decimal('1e-2'))
        Decimal('NaN')
        >>> ExtendedContext.quantize(Decimal('217'), Decimal('1e-1'))
        Decimal('217.0')
        >>> ExtendedContext.quantize(Decimal('217'), Decimal('1e-0'))
        Decimal('217')
        >>> ExtendedContext.quantize(Decimal('217'), Decimal('1e+1'))
        Decimal('2.2E+2')
        >>> ExtendedContext.quantize(Decimal('217'), Decimal('1e+2'))
        Decimal('2E+2')
        >>> ExtendedContext.quantize(1, 2)
        Decimal('1')
        >>> ExtendedContext.quantize(Decimal(1), 2)
        Decimal('1')
        >>> ExtendedContext.quantize(1, Decimal(2))
        Decimal('1')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.quantize(b, context=self)

    eleza radix(self):
        """Just returns 10, as this ni Decimal, :)

        >>> ExtendedContext.radix()
        Decimal('10')
        """
        rudisha Decimal(10)

    eleza remainder(self, a, b):
        """Returns the remainder kutoka integer division.

        The result ni the residue of the dividend after the operation of
        calculating integer division as described kila divide-integer, rounded
        to precision digits ikiwa necessary.  The sign of the result, if
        non-zero, ni the same as that of the original dividend.

        This operation will fail under the same conditions as integer division
        (that is, ikiwa integer division on the same two operands would fail, the
        remainder cannot be calculated).

        >>> ExtendedContext.remainder(Decimal('2.1'), Decimal('3'))
        Decimal('2.1')
        >>> ExtendedContext.remainder(Decimal('10'), Decimal('3'))
        Decimal('1')
        >>> ExtendedContext.remainder(Decimal('-10'), Decimal('3'))
        Decimal('-1')
        >>> ExtendedContext.remainder(Decimal('10.2'), Decimal('1'))
        Decimal('0.2')
        >>> ExtendedContext.remainder(Decimal('10'), Decimal('0.3'))
        Decimal('0.1')
        >>> ExtendedContext.remainder(Decimal('3.6'), Decimal('1.3'))
        Decimal('1.0')
        >>> ExtendedContext.remainder(22, 6)
        Decimal('4')
        >>> ExtendedContext.remainder(Decimal(22), 6)
        Decimal('4')
        >>> ExtendedContext.remainder(22, Decimal(6))
        Decimal('4')
        """
        a = _convert_other(a, raiseit=Kweli)
        r = a.__mod__(b, context=self)
        ikiwa r ni NotImplemented:
             ashiria TypeError("Unable to convert %s to Decimal" % b)
        isipokua:
            rudisha r

    eleza remainder_near(self, a, b):
        """Returns to be "a - b * n", where n ni the integer nearest the exact
        value of "x / b" (ikiwa two integers are equally near then the even one
        ni chosen).  If the result ni equal to 0 then its sign will be the
        sign of a.

        This operation will fail under the same conditions as integer division
        (that is, ikiwa integer division on the same two operands would fail, the
        remainder cannot be calculated).

        >>> ExtendedContext.remainder_near(Decimal('2.1'), Decimal('3'))
        Decimal('-0.9')
        >>> ExtendedContext.remainder_near(Decimal('10'), Decimal('6'))
        Decimal('-2')
        >>> ExtendedContext.remainder_near(Decimal('10'), Decimal('3'))
        Decimal('1')
        >>> ExtendedContext.remainder_near(Decimal('-10'), Decimal('3'))
        Decimal('-1')
        >>> ExtendedContext.remainder_near(Decimal('10.2'), Decimal('1'))
        Decimal('0.2')
        >>> ExtendedContext.remainder_near(Decimal('10'), Decimal('0.3'))
        Decimal('0.1')
        >>> ExtendedContext.remainder_near(Decimal('3.6'), Decimal('1.3'))
        Decimal('-0.3')
        >>> ExtendedContext.remainder_near(3, 11)
        Decimal('3')
        >>> ExtendedContext.remainder_near(Decimal(3), 11)
        Decimal('3')
        >>> ExtendedContext.remainder_near(3, Decimal(11))
        Decimal('3')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.remainder_near(b, context=self)

    eleza rotate(self, a, b):
        """Returns a rotated copy of a, b times.

        The coefficient of the result ni a rotated copy of the digits in
        the coefficient of the first operand.  The number of places of
        rotation ni taken kutoka the absolute value of the second operand,
        ukijumuisha the rotation being to the left ikiwa the second operand is
        positive ama to the right otherwise.

        >>> ExtendedContext.rotate(Decimal('34'), Decimal('8'))
        Decimal('400000003')
        >>> ExtendedContext.rotate(Decimal('12'), Decimal('9'))
        Decimal('12')
        >>> ExtendedContext.rotate(Decimal('123456789'), Decimal('-2'))
        Decimal('891234567')
        >>> ExtendedContext.rotate(Decimal('123456789'), Decimal('0'))
        Decimal('123456789')
        >>> ExtendedContext.rotate(Decimal('123456789'), Decimal('+2'))
        Decimal('345678912')
        >>> ExtendedContext.rotate(1333333, 1)
        Decimal('13333330')
        >>> ExtendedContext.rotate(Decimal(1333333), 1)
        Decimal('13333330')
        >>> ExtendedContext.rotate(1333333, Decimal(1))
        Decimal('13333330')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.rotate(b, context=self)

    eleza same_quantum(self, a, b):
        """Returns Kweli ikiwa the two operands have the same exponent.

        The result ni never affected by either the sign ama the coefficient of
        either operand.

        >>> ExtendedContext.same_quantum(Decimal('2.17'), Decimal('0.001'))
        Uongo
        >>> ExtendedContext.same_quantum(Decimal('2.17'), Decimal('0.01'))
        Kweli
        >>> ExtendedContext.same_quantum(Decimal('2.17'), Decimal('1'))
        Uongo
        >>> ExtendedContext.same_quantum(Decimal('Inf'), Decimal('-Inf'))
        Kweli
        >>> ExtendedContext.same_quantum(10000, -1)
        Kweli
        >>> ExtendedContext.same_quantum(Decimal(10000), -1)
        Kweli
        >>> ExtendedContext.same_quantum(10000, Decimal(-1))
        Kweli
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.same_quantum(b)

    eleza scaleb (self, a, b):
        """Returns the first operand after adding the second value its exp.

        >>> ExtendedContext.scaleb(Decimal('7.50'), Decimal('-2'))
        Decimal('0.0750')
        >>> ExtendedContext.scaleb(Decimal('7.50'), Decimal('0'))
        Decimal('7.50')
        >>> ExtendedContext.scaleb(Decimal('7.50'), Decimal('3'))
        Decimal('7.50E+3')
        >>> ExtendedContext.scaleb(1, 4)
        Decimal('1E+4')
        >>> ExtendedContext.scaleb(Decimal(1), 4)
        Decimal('1E+4')
        >>> ExtendedContext.scaleb(1, Decimal(4))
        Decimal('1E+4')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.scaleb(b, context=self)

    eleza shift(self, a, b):
        """Returns a shifted copy of a, b times.

        The coefficient of the result ni a shifted copy of the digits
        kwenye the coefficient of the first operand.  The number of places
        to shift ni taken kutoka the absolute value of the second operand,
        ukijumuisha the shift being to the left ikiwa the second operand is
        positive ama to the right otherwise.  Digits shifted into the
        coefficient are zeros.

        >>> ExtendedContext.shift(Decimal('34'), Decimal('8'))
        Decimal('400000000')
        >>> ExtendedContext.shift(Decimal('12'), Decimal('9'))
        Decimal('0')
        >>> ExtendedContext.shift(Decimal('123456789'), Decimal('-2'))
        Decimal('1234567')
        >>> ExtendedContext.shift(Decimal('123456789'), Decimal('0'))
        Decimal('123456789')
        >>> ExtendedContext.shift(Decimal('123456789'), Decimal('+2'))
        Decimal('345678900')
        >>> ExtendedContext.shift(88888888, 2)
        Decimal('888888800')
        >>> ExtendedContext.shift(Decimal(88888888), 2)
        Decimal('888888800')
        >>> ExtendedContext.shift(88888888, Decimal(2))
        Decimal('888888800')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.shift(b, context=self)

    eleza sqrt(self, a):
        """Square root of a non-negative number to context precision.

        If the result must be inexact, it ni rounded using the round-half-even
        algorithm.

        >>> ExtendedContext.sqrt(Decimal('0'))
        Decimal('0')
        >>> ExtendedContext.sqrt(Decimal('-0'))
        Decimal('-0')
        >>> ExtendedContext.sqrt(Decimal('0.39'))
        Decimal('0.624499800')
        >>> ExtendedContext.sqrt(Decimal('100'))
        Decimal('10')
        >>> ExtendedContext.sqrt(Decimal('1'))
        Decimal('1')
        >>> ExtendedContext.sqrt(Decimal('1.0'))
        Decimal('1.0')
        >>> ExtendedContext.sqrt(Decimal('1.00'))
        Decimal('1.0')
        >>> ExtendedContext.sqrt(Decimal('7'))
        Decimal('2.64575131')
        >>> ExtendedContext.sqrt(Decimal('10'))
        Decimal('3.16227766')
        >>> ExtendedContext.sqrt(2)
        Decimal('1.41421356')
        >>> ExtendedContext.prec
        9
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.sqrt(context=self)

    eleza subtract(self, a, b):
        """Return the difference between the two operands.

        >>> ExtendedContext.subtract(Decimal('1.3'), Decimal('1.07'))
        Decimal('0.23')
        >>> ExtendedContext.subtract(Decimal('1.3'), Decimal('1.30'))
        Decimal('0.00')
        >>> ExtendedContext.subtract(Decimal('1.3'), Decimal('2.07'))
        Decimal('-0.77')
        >>> ExtendedContext.subtract(8, 5)
        Decimal('3')
        >>> ExtendedContext.subtract(Decimal(8), 5)
        Decimal('3')
        >>> ExtendedContext.subtract(8, Decimal(5))
        Decimal('3')
        """
        a = _convert_other(a, raiseit=Kweli)
        r = a.__sub__(b, context=self)
        ikiwa r ni NotImplemented:
             ashiria TypeError("Unable to convert %s to Decimal" % b)
        isipokua:
            rudisha r

    eleza to_eng_string(self, a):
        """Convert to a string, using engineering notation ikiwa an exponent ni needed.

        Engineering notation has an exponent which ni a multiple of 3.  This
        can leave up to 3 digits to the left of the decimal place na may
        require the addition of either one ama two trailing zeros.

        The operation ni sio affected by the context.

        >>> ExtendedContext.to_eng_string(Decimal('123E+1'))
        '1.23E+3'
        >>> ExtendedContext.to_eng_string(Decimal('123E+3'))
        '123E+3'
        >>> ExtendedContext.to_eng_string(Decimal('123E-10'))
        '12.3E-9'
        >>> ExtendedContext.to_eng_string(Decimal('-123E-12'))
        '-123E-12'
        >>> ExtendedContext.to_eng_string(Decimal('7E-7'))
        '700E-9'
        >>> ExtendedContext.to_eng_string(Decimal('7E+1'))
        '70'
        >>> ExtendedContext.to_eng_string(Decimal('0E+1'))
        '0.00E+3'

        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.to_eng_string(context=self)

    eleza to_sci_string(self, a):
        """Converts a number to a string, using scientific notation.

        The operation ni sio affected by the context.
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.__str__(context=self)

    eleza to_integral_exact(self, a):
        """Rounds to an integer.

        When the operand has a negative exponent, the result ni the same
        as using the quantize() operation using the given operand as the
        left-hand-operand, 1E+0 as the right-hand-operand, na the precision
        of the operand as the precision setting; Inexact na Rounded flags
        are allowed kwenye this operation.  The rounding mode ni taken kutoka the
        context.

        >>> ExtendedContext.to_integral_exact(Decimal('2.1'))
        Decimal('2')
        >>> ExtendedContext.to_integral_exact(Decimal('100'))
        Decimal('100')
        >>> ExtendedContext.to_integral_exact(Decimal('100.0'))
        Decimal('100')
        >>> ExtendedContext.to_integral_exact(Decimal('101.5'))
        Decimal('102')
        >>> ExtendedContext.to_integral_exact(Decimal('-101.5'))
        Decimal('-102')
        >>> ExtendedContext.to_integral_exact(Decimal('10E+5'))
        Decimal('1.0E+6')
        >>> ExtendedContext.to_integral_exact(Decimal('7.89E+77'))
        Decimal('7.89E+77')
        >>> ExtendedContext.to_integral_exact(Decimal('-Inf'))
        Decimal('-Infinity')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.to_integral_exact(context=self)

    eleza to_integral_value(self, a):
        """Rounds to an integer.

        When the operand has a negative exponent, the result ni the same
        as using the quantize() operation using the given operand as the
        left-hand-operand, 1E+0 as the right-hand-operand, na the precision
        of the operand as the precision setting, except that no flags will
        be set.  The rounding mode ni taken kutoka the context.

        >>> ExtendedContext.to_integral_value(Decimal('2.1'))
        Decimal('2')
        >>> ExtendedContext.to_integral_value(Decimal('100'))
        Decimal('100')
        >>> ExtendedContext.to_integral_value(Decimal('100.0'))
        Decimal('100')
        >>> ExtendedContext.to_integral_value(Decimal('101.5'))
        Decimal('102')
        >>> ExtendedContext.to_integral_value(Decimal('-101.5'))
        Decimal('-102')
        >>> ExtendedContext.to_integral_value(Decimal('10E+5'))
        Decimal('1.0E+6')
        >>> ExtendedContext.to_integral_value(Decimal('7.89E+77'))
        Decimal('7.89E+77')
        >>> ExtendedContext.to_integral_value(Decimal('-Inf'))
        Decimal('-Infinity')
        """
        a = _convert_other(a, raiseit=Kweli)
        rudisha a.to_integral_value(context=self)

    # the method name changed, but we provide also the old one, kila compatibility
    to_integral = to_integral_value

kundi _WorkRep(object):
    __slots__ = ('sign','int','exp')
    # sign: 0 ama 1
    # int:  int
    # exp:  Tupu, int, ama string

    eleza __init__(self, value=Tupu):
        ikiwa value ni Tupu:
            self.sign = Tupu
            self.int = 0
            self.exp = Tupu
        elikiwa isinstance(value, Decimal):
            self.sign = value._sign
            self.int = int(value._int)
            self.exp = value._exp
        isipokua:
            # assert isinstance(value, tuple)
            self.sign = value[0]
            self.int = value[1]
            self.exp = value[2]

    eleza __repr__(self):
        rudisha "(%r, %r, %r)" % (self.sign, self.int, self.exp)



eleza _normalize(op1, op2, prec = 0):
    """Normalizes op1, op2 to have the same exp na length of coefficient.

    Done during addition.
    """
    ikiwa op1.exp < op2.exp:
        tmp = op2
        other = op1
    isipokua:
        tmp = op1
        other = op2

    # Let exp = min(tmp.exp - 1, tmp.adjusted() - precision - 1).
    # Then adding 10**exp to tmp has the same effect (after rounding)
    # as adding any positive quantity smaller than 10**exp; similarly
    # kila subtraction.  So ikiwa other ni smaller than 10**exp we replace
    # it ukijumuisha 10**exp.  This avoids tmp.exp - other.exp getting too large.
    tmp_len = len(str(tmp.int))
    other_len = len(str(other.int))
    exp = tmp.exp + min(-1, tmp_len - prec - 2)
    ikiwa other_len + other.exp - 1 < exp:
        other.int = 1
        other.exp = exp

    tmp.int *= 10 ** (tmp.exp - other.exp)
    tmp.exp = other.exp
    rudisha op1, op2

##### Integer arithmetic functions used by ln, log10, exp na __pow__ #####

_nbits = int.bit_length

eleza _decimal_lshift_exact(n, e):
    """ Given integers n na e, rudisha n * 10**e ikiwa it's an integer, isipokua Tupu.

    The computation ni designed to avoid computing large powers of 10
    unnecessarily.

    >>> _decimal_lshift_exact(3, 4)
    30000
    >>> _decimal_lshift_exact(300, -999999999)  # returns Tupu

    """
    ikiwa n == 0:
        rudisha 0
    elikiwa e >= 0:
        rudisha n * 10**e
    isipokua:
        # val_n = largest power of 10 dividing n.
        str_n = str(abs(n))
        val_n = len(str_n) - len(str_n.rstrip('0'))
        rudisha Tupu ikiwa val_n < -e isipokua n // 10**-e

eleza _sqrt_nearest(n, a):
    """Closest integer to the square root of the positive integer n.  a is
    an initial approximation to the square root.  Any positive integer
    will do kila a, but the closer a ni to the square root of n the
    faster convergence will be.

    """
    ikiwa n <= 0 ama a <= 0:
         ashiria ValueError("Both arguments to _sqrt_nearest should be positive.")

    b=0
    wakati a != b:
        b, a = a, a--n//a>>1
    rudisha a

eleza _rshift_nearest(x, shift):
    """Given an integer x na a nonnegative integer shift, rudisha closest
    integer to x / 2**shift; use round-to-even kwenye case of a tie.

    """
    b, q = 1 << shift, x >> shift
    rudisha q + (2*(x & (b-1)) + (q&1) > b)

eleza _div_nearest(a, b):
    """Closest integer to a/b, a na b positive integers; rounds to even
    kwenye the case of a tie.

    """
    q, r = divmod(a, b)
    rudisha q + (2*r + (q&1) > b)

eleza _ilog(x, M, L = 8):
    """Integer approximation to M*log(x/M), ukijumuisha absolute error boundable
    kwenye terms only of x/M.

    Given positive integers x na M, rudisha an integer approximation to
    M * log(x/M).  For L = 8 na 0.1 <= x/M <= 10 the difference
    between the approximation na the exact result ni at most 22.  For
    L = 8 na 1.0 <= x/M <= 10.0 the difference ni at most 15.  In
    both cases these are upper bounds on the error; it will usually be
    much smaller."""

    # The basic algorithm ni the following: let log1p be the function
    # log1p(x) = log(1+x).  Then log(x/M) = log1p((x-M)/M).  We use
    # the reduction
    #
    #    log1p(y) = 2*log1p(y/(1+sqrt(1+y)))
    #
    # repeatedly until the argument to log1p ni small (< 2**-L in
    # absolute value).  For small y we can use the Taylor series
    # expansion
    #
    #    log1p(y) ~ y - y**2/2 + y**3/3 - ... - (-y)**T/T
    #
    # truncating at T such that y**T ni small enough.  The whole
    # computation ni carried out kwenye a form of fixed-point arithmetic,
    # ukijumuisha a real number z being represented by an integer
    # approximation to z*M.  To avoid loss of precision, the y below
    # ni actually an integer approximation to 2**R*y*M, where R ni the
    # number of reductions performed so far.

    y = x-M
    # argument reduction; R = number of reductions performed
    R = 0
    wakati (R <= L na abs(y) << L-R >= M or
           R > L na abs(y) >> R-L >= M):
        y = _div_nearest((M*y) << 1,
                         M + _sqrt_nearest(M*(M+_rshift_nearest(y, R)), M))
        R += 1

    # Taylor series ukijumuisha T terms
    T = -int(-10*len(str(M))//(3*L))
    yshift = _rshift_nearest(y, R)
    w = _div_nearest(M, T)
    kila k kwenye range(T-1, 0, -1):
        w = _div_nearest(M, k) - _div_nearest(yshift*w, M)

    rudisha _div_nearest(w*y, M)

eleza _dlog10(c, e, p):
    """Given integers c, e na p ukijumuisha c > 0, p >= 0, compute an integer
    approximation to 10**p * log10(c*10**e), ukijumuisha an absolute error of
    at most 1.  Assumes that c*10**e ni sio exactly 1."""

    # increase precision by 2; compensate kila this by dividing
    # final result by 100
    p += 2

    # write c*10**e as d*10**f ukijumuisha either:
    #   f >= 0 na 1 <= d <= 10, or
    #   f <= 0 na 0.1 <= d <= 1.
    # Thus kila c*10**e close to 1, f = 0
    l = len(str(c))
    f = e+l - (e+l >= 1)

    ikiwa p > 0:
        M = 10**p
        k = e+p-f
        ikiwa k >= 0:
            c *= 10**k
        isipokua:
            c = _div_nearest(c, 10**-k)

        log_d = _ilog(c, M) # error < 5 + 22 = 27
        log_10 = _log10_digits(p) # error < 1
        log_d = _div_nearest(log_d*M, log_10)
        log_tenpower = f*M # exact
    isipokua:
        log_d = 0  # error < 2.31
        log_tenpower = _div_nearest(f, 10**-p) # error < 0.5

    rudisha _div_nearest(log_tenpower+log_d, 100)

eleza _dlog(c, e, p):
    """Given integers c, e na p ukijumuisha c > 0, compute an integer
    approximation to 10**p * log(c*10**e), ukijumuisha an absolute error of
    at most 1.  Assumes that c*10**e ni sio exactly 1."""

    # Increase precision by 2. The precision increase ni compensated
    # kila at the end ukijumuisha a division by 100.
    p += 2

    # rewrite c*10**e as d*10**f ukijumuisha either f >= 0 na 1 <= d <= 10,
    # ama f <= 0 na 0.1 <= d <= 1.  Then we can compute 10**p * log(c*10**e)
    # as 10**p * log(d) + 10**p*f * log(10).
    l = len(str(c))
    f = e+l - (e+l >= 1)

    # compute approximation to 10**p*log(d), ukijumuisha error < 27
    ikiwa p > 0:
        k = e+p-f
        ikiwa k >= 0:
            c *= 10**k
        isipokua:
            c = _div_nearest(c, 10**-k)  # error of <= 0.5 kwenye c

        # _ilog magnifies existing error kwenye c by a factor of at most 10
        log_d = _ilog(c, 10**p) # error < 5 + 22 = 27
    isipokua:
        # p <= 0: just approximate the whole thing by 0; error < 2.31
        log_d = 0

    # compute approximation to f*10**p*log(10), ukijumuisha error < 11.
    ikiwa f:
        extra = len(str(abs(f)))-1
        ikiwa p + extra >= 0:
            # error kwenye f * _log10_digits(p+extra) < |f| * 1 = |f|
            # after division, error < |f|/10**extra + 0.5 < 10 + 0.5 < 11
            f_log_ten = _div_nearest(f*_log10_digits(p+extra), 10**extra)
        isipokua:
            f_log_ten = 0
    isipokua:
        f_log_ten = 0

    # error kwenye sum < 11+27 = 38; error after division < 0.38 + 0.5 < 1
    rudisha _div_nearest(f_log_ten + log_d, 100)

kundi _Log10Memoize(object):
    """Class to compute, store, na allow retrieval of, digits of the
    constant log(10) = 2.302585....  This constant ni needed by
    Decimal.ln, Decimal.log10, Decimal.exp na Decimal.__pow__."""
    eleza __init__(self):
        self.digits = "23025850929940456840179914546843642076011014886"

    eleza getdigits(self, p):
        """Given an integer p >= 0, rudisha floor(10**p)*log(10).

        For example, self.getdigits(3) returns 2302.
        """
        # digits are stored as a string, kila quick conversion to
        # integer kwenye the case that we've already computed enough
        # digits; the stored digits should always be correct
        # (truncated, sio rounded to nearest).
        ikiwa p < 0:
             ashiria ValueError("p should be nonnegative")

        ikiwa p >= len(self.digits):
            # compute p+3, p+6, p+9, ... digits; endelea until at
            # least one of the extra digits ni nonzero
            extra = 3
            wakati Kweli:
                # compute p+extra digits, correct to within 1ulp
                M = 10**(p+extra+2)
                digits = str(_div_nearest(_ilog(10*M, M), 100))
                ikiwa digits[-extra:] != '0'*extra:
                    koma
                extra += 3
            # keep all reliable digits so far; remove trailing zeros
            # na next nonzero digit
            self.digits = digits.rstrip('0')[:-1]
        rudisha int(self.digits[:p+1])

_log10_digits = _Log10Memoize().getdigits

eleza _iexp(x, M, L=8):
    """Given integers x na M, M > 0, such that x/M ni small kwenye absolute
    value, compute an integer approximation to M*exp(x/M).  For 0 <=
    x/M <= 2.4, the absolute error kwenye the result ni bounded by 60 (and
    ni usually much smaller)."""

    # Algorithm: to compute exp(z) kila a real number z, first divide z
    # by a suitable power R of 2 so that |z/2**R| < 2**-L.  Then
    # compute expm1(z/2**R) = exp(z/2**R) - 1 using the usual Taylor
    # series
    #
    #     expm1(x) = x + x**2/2! + x**3/3! + ...
    #
    # Now use the identity
    #
    #     expm1(2x) = expm1(x)*(expm1(x)+2)
    #
    # R times to compute the sequence expm1(z/2**R),
    # expm1(z/2**(R-1)), ... , exp(z/2), exp(z).

    # Find R such that x/2**R/M <= 2**-L
    R = _nbits((x<<L)//M)

    # Taylor series.  (2**L)**T > M
    T = -int(-10*len(str(M))//(3*L))
    y = _div_nearest(x, T)
    Mshift = M<<R
    kila i kwenye range(T-1, 0, -1):
        y = _div_nearest(x*(Mshift + y), Mshift * i)

    # Expansion
    kila k kwenye range(R-1, -1, -1):
        Mshift = M<<(k+2)
        y = _div_nearest(y*(y+Mshift), Mshift)

    rudisha M+y

eleza _dexp(c, e, p):
    """Compute an approximation to exp(c*10**e), ukijumuisha p decimal places of
    precision.

    Returns integers d, f such that:

      10**(p-1) <= d <= 10**p, and
      (d-1)*10**f < exp(c*10**e) < (d+1)*10**f

    In other words, d*10**f ni an approximation to exp(c*10**e) ukijumuisha p
    digits of precision, na ukijumuisha an error kwenye d of at most 1.  This is
    almost, but sio quite, the same as the error being < 1ulp: when d
    = 10**(p-1) the error could be up to 10 ulp."""

    # we'll call iexp ukijumuisha M = 10**(p+2), giving p+3 digits of precision
    p += 2

    # compute log(10) ukijumuisha extra precision = adjusted exponent of c*10**e
    extra = max(0, e + len(str(c)) - 1)
    q = p + extra

    # compute quotient c*10**e/(log(10)) = c*10**(e+q)/(log(10)*10**q),
    # rounding down
    shift = e+q
    ikiwa shift >= 0:
        cshift = c*10**shift
    isipokua:
        cshift = c//10**-shift
    quot, rem = divmod(cshift, _log10_digits(q))

    # reduce remainder back to original precision
    rem = _div_nearest(rem, 10**extra)

    # error kwenye result of _iexp < 120;  error after division < 0.62
    rudisha _div_nearest(_iexp(rem, 10**p), 1000), quot - p + 3

eleza _dpower(xc, xe, yc, ye, p):
    """Given integers xc, xe, yc na ye representing Decimals x = xc*10**xe and
    y = yc*10**ye, compute x**y.  Returns a pair of integers (c, e) such that:

      10**(p-1) <= c <= 10**p, and
      (c-1)*10**e < x**y < (c+1)*10**e

    kwenye other words, c*10**e ni an approximation to x**y ukijumuisha p digits
    of precision, na ukijumuisha an error kwenye c of at most 1.  (This is
    almost, but sio quite, the same as the error being < 1ulp: when c
    == 10**(p-1) we can only guarantee error < 10ulp.)

    We assume that: x ni positive na sio equal to 1, na y ni nonzero.
    """

    # Find b such that 10**(b-1) <= |y| <= 10**b
    b = len(str(abs(yc))) + ye

    # log(x) = lxc*10**(-p-b-1), to p+b+1 places after the decimal point
    lxc = _dlog(xc, xe, p+b+1)

    # compute product y*log(x) = yc*lxc*10**(-p-b-1+ye) = pc*10**(-p-1)
    shift = ye-b
    ikiwa shift >= 0:
        pc = lxc*yc*10**shift
    isipokua:
        pc = _div_nearest(lxc*yc, 10**-shift)

    ikiwa pc == 0:
        # we prefer a result that isn't exactly 1; this makes it
        # easier to compute a correctly rounded result kwenye __pow__
        ikiwa ((len(str(xc)) + xe >= 1) == (yc > 0)): # ikiwa x**y > 1:
            coeff, exp = 10**(p-1)+1, 1-p
        isipokua:
            coeff, exp = 10**p-1, -p
    isipokua:
        coeff, exp = _dexp(pc, -(p+1), p+1)
        coeff = _div_nearest(coeff, 10)
        exp += 1

    rudisha coeff, exp

eleza _log10_lb(c, correction = {
        '1': 100, '2': 70, '3': 53, '4': 40, '5': 31,
        '6': 23, '7': 16, '8': 10, '9': 5}):
    """Compute a lower bound kila 100*log10(c) kila a positive integer c."""
    ikiwa c <= 0:
         ashiria ValueError("The argument to _log10_lb should be nonnegative.")
    str_c = str(c)
    rudisha 100*len(str_c) - correction[str_c[0]]

##### Helper Functions ####################################################

eleza _convert_other(other, raiseit=Uongo, allow_float=Uongo):
    """Convert other to Decimal.

    Verifies that it's ok to use kwenye an implicit construction.
    If allow_float ni true, allow conversion kutoka float;  this
    ni used kwenye the comparison methods (__eq__ na friends).

    """
    ikiwa isinstance(other, Decimal):
        rudisha other
    ikiwa isinstance(other, int):
        rudisha Decimal(other)
    ikiwa allow_float na isinstance(other, float):
        rudisha Decimal.from_float(other)

    ikiwa raiseit:
         ashiria TypeError("Unable to convert %s to Decimal" % other)
    rudisha NotImplemented

eleza _convert_for_comparison(self, other, equality_op=Uongo):
    """Given a Decimal instance self na a Python object other, return
    a pair (s, o) of Decimal instances such that "s op o" is
    equivalent to "self op other" kila any of the 6 comparison
    operators "op".

    """
    ikiwa isinstance(other, Decimal):
        rudisha self, other

    # Comparison ukijumuisha a Rational instance (also includes integers):
    # self op n/d <=> self*d op n (kila n na d integers, d positive).
    # A NaN ama infinity can be left unchanged without affecting the
    # comparison result.
    ikiwa isinstance(other, _numbers.Rational):
        ikiwa sio self._is_special:
            self = _dec_from_triple(self._sign,
                                    str(int(self._int) * other.denominator),
                                    self._exp)
        rudisha self, Decimal(other.numerator)

    # Comparisons ukijumuisha float na complex types.  == na != comparisons
    # ukijumuisha complex numbers should succeed, returning either Kweli ama Uongo
    # as appropriate.  Other comparisons rudisha NotImplemented.
    ikiwa equality_op na isinstance(other, _numbers.Complex) na other.imag == 0:
        other = other.real
    ikiwa isinstance(other, float):
        context = getcontext()
        ikiwa equality_op:
            context.flags[FloatOperation] = 1
        isipokua:
            context._raise_error(FloatOperation,
                "strict semantics kila mixing floats na Decimals are enabled")
        rudisha self, Decimal.from_float(other)
    rudisha NotImplemented, NotImplemented


##### Setup Specific Contexts ############################################

# The default context prototype used by Context()
# Is mutable, so that new contexts can have different default values

DefaultContext = Context(
        prec=28, rounding=ROUND_HALF_EVEN,
        traps=[DivisionByZero, Overflow, InvalidOperation],
        flags=[],
        Emax=999999,
        Emin=-999999,
        capitals=1,
        clamp=0
)

# Pre-made alternate contexts offered by the specification
# Don't change these; the user should be able to select these
# contexts na be able to reproduce results kutoka other implementations
# of the spec.

BasicContext = Context(
        prec=9, rounding=ROUND_HALF_UP,
        traps=[DivisionByZero, Overflow, InvalidOperation, Clamped, Underflow],
        flags=[],
)

ExtendedContext = Context(
        prec=9, rounding=ROUND_HALF_EVEN,
        traps=[],
        flags=[],
)


##### crud kila parsing strings #############################################
#
# Regular expression used kila parsing numeric strings.  Additional
# comments:
#
# 1. Uncomment the two '\s*' lines to allow leading and/or trailing
# whitespace.  But note that the specification disallows whitespace in
# a numeric string.
#
# 2. For finite numbers (not infinities na NaNs) the body of the
# number between the optional sign na the optional exponent must have
# at least one decimal digit, possibly after the decimal point.  The
# lookahead expression '(?=\d|\.\d)' checks this.

agiza re
_parser = re.compile(r"""        # A numeric string consists of:
#    \s*
    (?P<sign>[-+])?              # an optional sign, followed by either...
    (
        (?=\d|\.\d)              # ...a number (ukijumuisha at least one digit)
        (?P<int>\d*)             # having a (possibly empty) integer part
        (\.(?P<frac>\d*))?       # followed by an optional fractional part
        (E(?P<exp>[-+]?\d+))?    # followed by an optional exponent, or...
    |
        Inf(inity)?              # ...an infinity, or...
    |
        (?P<signal>s)?           # ...an (optionally signaling)
        NaN                      # NaN
        (?P<diag>\d*)            # ukijumuisha (possibly empty) diagnostic info.
    )
#    \s*
    \Z
""", re.VERBOSE | re.IGNORECASE).match

_all_zeros = re.compile('0*$').match
_exact_half = re.compile('50*$').match

##### PEP3101 support functions ##############################################
# The functions kwenye this section have little to do ukijumuisha the Decimal
# class, na could potentially be reused ama adapted kila other pure
# Python numeric classes that want to implement __format__
#
# A format specifier kila Decimal looks like:
#
#   [[fill]align][sign][#][0][minimumwidth][,][.precision][type]

_parse_format_specifier_regex = re.compile(r"""\A
(?:
   (?P<fill>.)?
   (?P<align>[<>=^])
)?
(?P<sign>[-+ ])?
(?P<alt>\#)?
(?P<zeropad>0)?
(?P<minimumwidth>(?!0)\d+)?
(?P<thousands_sep>,)?
(?:\.(?P<precision>0|(?!0)\d+))?
(?P<type>[eEfFgGn%])?
\Z
""", re.VERBOSE|re.DOTALL)

toa re

# The locale module ni only needed kila the 'n' format specifier.  The
# rest of the PEP 3101 code functions quite happily without it, so we
# don't care too much ikiwa locale isn't present.
jaribu:
    agiza locale as _locale
except ImportError:
    pass

eleza _parse_format_specifier(format_spec, _localeconv=Tupu):
    """Parse na validate a format specifier.

    Turns a standard numeric format specifier into a dict, ukijumuisha the
    following entries:

      fill: fill character to pad field to minimum width
      align: alignment type, either '<', '>', '=' ama '^'
      sign: either '+', '-' ama ' '
      minimumwidth: nonnegative integer giving minimum width
      zeropad: boolean, indicating whether to pad ukijumuisha zeros
      thousands_sep: string to use as thousands separator, ama ''
      grouping: grouping kila thousands separators, kwenye format
        used by localeconv
      decimal_point: string to use kila decimal point
      precision: nonnegative integer giving precision, ama Tupu
      type: one of the characters 'eEfFgG%', ama Tupu

    """
    m = _parse_format_specifier_regex.match(format_spec)
    ikiwa m ni Tupu:
         ashiria ValueError("Invalid format specifier: " + format_spec)

    # get the dictionary
    format_dict = m.groupdict()

    # zeropad; defaults kila fill na alignment.  If zero padding
    # ni requested, the fill na align fields should be absent.
    fill = format_dict['fill']
    align = format_dict['align']
    format_dict['zeropad'] = (format_dict['zeropad'] ni sio Tupu)
    ikiwa format_dict['zeropad']:
        ikiwa fill ni sio Tupu:
             ashiria ValueError("Fill character conflicts ukijumuisha '0'"
                             " kwenye format specifier: " + format_spec)
        ikiwa align ni sio Tupu:
             ashiria ValueError("Alignment conflicts ukijumuisha '0' kwenye "
                             "format specifier: " + format_spec)
    format_dict['fill'] = fill ama ' '
    # PEP 3101 originally specified that the default alignment should
    # be left;  it was later agreed that right-aligned makes more sense
    # kila numeric types.  See http://bugs.python.org/issue6857.
    format_dict['align'] = align ama '>'

    # default sign handling: '-' kila negative, '' kila positive
    ikiwa format_dict['sign'] ni Tupu:
        format_dict['sign'] = '-'

    # minimumwidth defaults to 0; precision remains Tupu ikiwa sio given
    format_dict['minimumwidth'] = int(format_dict['minimumwidth'] ama '0')
    ikiwa format_dict['precision'] ni sio Tupu:
        format_dict['precision'] = int(format_dict['precision'])

    # ikiwa format type ni 'g' ama 'G' then a precision of 0 makes little
    # sense; convert it to 1.  Same ikiwa format type ni unspecified.
    ikiwa format_dict['precision'] == 0:
        ikiwa format_dict['type'] ni Tupu ama format_dict['type'] kwenye 'gGn':
            format_dict['precision'] = 1

    # determine thousands separator, grouping, na decimal separator, and
    # add appropriate entries to format_dict
    ikiwa format_dict['type'] == 'n':
        # apart kutoka separators, 'n' behaves just like 'g'
        format_dict['type'] = 'g'
        ikiwa _localeconv ni Tupu:
            _localeconv = _locale.localeconv()
        ikiwa format_dict['thousands_sep'] ni sio Tupu:
             ashiria ValueError("Explicit thousands separator conflicts ukijumuisha "
                             "'n' type kwenye format specifier: " + format_spec)
        format_dict['thousands_sep'] = _localeconv['thousands_sep']
        format_dict['grouping'] = _localeconv['grouping']
        format_dict['decimal_point'] = _localeconv['decimal_point']
    isipokua:
        ikiwa format_dict['thousands_sep'] ni Tupu:
            format_dict['thousands_sep'] = ''
        format_dict['grouping'] = [3, 0]
        format_dict['decimal_point'] = '.'

    rudisha format_dict

eleza _format_align(sign, body, spec):
    """Given an unpadded, non-aligned numeric string 'body' na sign
    string 'sign', add padding na alignment conforming to the given
    format specifier dictionary 'spec' (as produced by
    parse_format_specifier).

    """
    # how much extra space do we have to play with?
    minimumwidth = spec['minimumwidth']
    fill = spec['fill']
    padding = fill*(minimumwidth - len(sign) - len(body))

    align = spec['align']
    ikiwa align == '<':
        result = sign + body + padding
    elikiwa align == '>':
        result = padding + sign + body
    elikiwa align == '=':
        result = sign + padding + body
    elikiwa align == '^':
        half = len(padding)//2
        result = padding[:half] + sign + body + padding[half:]
    isipokua:
         ashiria ValueError('Unrecognised alignment field')

    rudisha result

eleza _group_lengths(grouping):
    """Convert a localeconv-style grouping into a (possibly infinite)
    iterable of integers representing group lengths.

    """
    # The result kutoka localeconv()['grouping'], na the input to this
    # function, should be a list of integers kwenye one of the
    # following three forms:
    #
    #   (1) an empty list, or
    #   (2) nonempty list of positive integers + [0]
    #   (3) list of positive integers + [locale.CHAR_MAX], or

    kutoka itertools agiza chain, repeat
    ikiwa sio grouping:
        rudisha []
    elikiwa grouping[-1] == 0 na len(grouping) >= 2:
        rudisha chain(grouping[:-1], repeat(grouping[-2]))
    elikiwa grouping[-1] == _locale.CHAR_MAX:
        rudisha grouping[:-1]
    isipokua:
         ashiria ValueError('unrecognised format kila grouping')

eleza _insert_thousands_sep(digits, spec, min_width=1):
    """Insert thousands separators into a digit string.

    spec ni a dictionary whose keys should include 'thousands_sep' and
    'grouping'; typically it's the result of parsing the format
    specifier using _parse_format_specifier.

    The min_width keyword argument gives the minimum length of the
    result, which will be padded on the left ukijumuisha zeros ikiwa necessary.

    If necessary, the zero padding adds an extra '0' on the left to
    avoid a leading thousands separator.  For example, inserting
    commas every three digits kwenye '123456', ukijumuisha min_width=8, gives
    '0,123,456', even though that has length 9.

    """

    sep = spec['thousands_sep']
    grouping = spec['grouping']

    groups = []
    kila l kwenye _group_lengths(grouping):
        ikiwa l <= 0:
             ashiria ValueError("group length should be positive")
        # max(..., 1) forces at least 1 digit to the left of a separator
        l = min(max(len(digits), min_width, 1), l)
        groups.append('0'*(l - len(digits)) + digits[-l:])
        digits = digits[:-l]
        min_width -= l
        ikiwa sio digits na min_width <= 0:
            koma
        min_width -= len(sep)
    isipokua:
        l = max(len(digits), min_width, 1)
        groups.append('0'*(l - len(digits)) + digits[-l:])
    rudisha sep.join(reversed(groups))

eleza _format_sign(is_negative, spec):
    """Determine sign character."""

    ikiwa is_negative:
        rudisha '-'
    elikiwa spec['sign'] kwenye ' +':
        rudisha spec['sign']
    isipokua:
        rudisha ''

eleza _format_number(is_negative, intpart, fracpart, exp, spec):
    """Format a number, given the following data:

    is_negative: true ikiwa the number ni negative, isipokua false
    intpart: string of digits that must appear before the decimal point
    fracpart: string of digits that must come after the point
    exp: exponent, as an integer
    spec: dictionary resulting kutoka parsing the format specifier

    This function uses the information kwenye spec to:
      insert separators (decimal separator na thousands separators)
      format the sign
      format the exponent
      add trailing '%' kila the '%' type
      zero-pad ikiwa necessary
      fill na align ikiwa necessary
    """

    sign = _format_sign(is_negative, spec)

    ikiwa fracpart ama spec['alt']:
        fracpart = spec['decimal_point'] + fracpart

    ikiwa exp != 0 ama spec['type'] kwenye 'eE':
        echar = {'E': 'E', 'e': 'e', 'G': 'E', 'g': 'e'}[spec['type']]
        fracpart += "{0}{1:+}".format(echar, exp)
    ikiwa spec['type'] == '%':
        fracpart += '%'

    ikiwa spec['zeropad']:
        min_width = spec['minimumwidth'] - len(fracpart) - len(sign)
    isipokua:
        min_width = 0
    intpart = _insert_thousands_sep(intpart, spec, min_width)

    rudisha _format_align(sign, intpart+fracpart, spec)


##### Useful Constants (internal use only) ################################

# Reusable defaults
_Infinity = Decimal('Inf')
_NegativeInfinity = Decimal('-Inf')
_NaN = Decimal('NaN')
_Zero = Decimal(0)
_One = Decimal(1)
_NegativeOne = Decimal(-1)

# _SignedInfinity[sign] ni infinity w/ that sign
_SignedInfinity = (_Infinity, _NegativeInfinity)

# Constants related to the hash implementation;  hash(x) ni based
# on the reduction of x modulo _PyHASH_MODULUS
_PyHASH_MODULUS = sys.hash_info.modulus
# hash values to use kila positive na negative infinities, na nans
_PyHASH_INF = sys.hash_info.inf
_PyHASH_NAN = sys.hash_info.nan

# _PyHASH_10INV ni the inverse of 10 modulo the prime _PyHASH_MODULUS
_PyHASH_10INV = pow(10, _PyHASH_MODULUS - 2, _PyHASH_MODULUS)
toa sys
