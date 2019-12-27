# Originally contributed by Sjoerd Mullender.
# Significantly modified by Jeffrey Yasskin <jyasskin at gmail.com>.

"""Fraction, infinite-precision, real numbers."""

kutoka decimal agiza Decimal
agiza math
agiza numbers
agiza operator
agiza re
agiza sys

__all__ = ['Fraction', 'gcd']



eleza gcd(a, b):
    """Calculate the Greatest Common Divisor of a and b.

    Unless b==0, the result will have the same sign as b (so that when
    b is divided by it, the result comes out positive).
    """
    agiza warnings
    warnings.warn('fractions.gcd() is deprecated. Use math.gcd() instead.',
                  DeprecationWarning, 2)
    ikiwa type(a) is int is type(b):
        ikiwa (b or a) < 0:
            rudisha -math.gcd(a, b)
        rudisha math.gcd(a, b)
    rudisha _gcd(a, b)

eleza _gcd(a, b):
    # Supports non-integers for backward compatibility.
    while b:
        a, b = b, a%b
    rudisha a

# Constants related to the hash implementation;  hash(x) is based
# on the reduction of x modulo the prime _PyHASH_MODULUS.
_PyHASH_MODULUS = sys.hash_info.modulus
# Value to be used for rationals that reduce to infinity modulo
# _PyHASH_MODULUS.
_PyHASH_INF = sys.hash_info.inf

_RATIONAL_FORMAT = re.compile(r"""
    \A\s*                      # optional whitespace at the start, then
    (?P<sign>[-+]?)            # an optional sign, then
    (?=\d|\.\d)                # lookahead for digit or .digit
    (?P<num>\d*)               # numerator (possibly empty)
    (?:                        # followed by
       (?:/(?P<denom>\d+))?    # an optional denominator
    |                          # or
       (?:\.(?P<decimal>\d*))? # an optional fractional part
       (?:E(?P<exp>[-+]?\d+))? # and optional exponent
    )
    \s*\Z                      # and optional whitespace to finish
""", re.VERBOSE | re.IGNORECASE)


kundi Fraction(numbers.Rational):
    """This kundi implements rational numbers.

    In the two-argument form of the constructor, Fraction(8, 6) will
    produce a rational number equivalent to 4/3. Both arguments must
    be Rational. The numerator defaults to 0 and the denominator
    defaults to 1 so that Fraction(3) == 3 and Fraction() == 0.

    Fractions can also be constructed kutoka:

      - numeric strings similar to those accepted by the
        float constructor (for example, '-2.3' or '1e10')

      - strings of the form '123/456'

      - float and Decimal instances

      - other Rational instances (including integers)

    """

    __slots__ = ('_numerator', '_denominator')

    # We're immutable, so use __new__ not __init__
    eleza __new__(cls, numerator=0, denominator=None, *, _normalize=True):
        """Constructs a Rational.

        Takes a string like '3/2' or '1.5', another Rational instance, a
        numerator/denominator pair, or a float.

        Examples
        --------

        >>> Fraction(10, -8)
        Fraction(-5, 4)
        >>> Fraction(Fraction(1, 7), 5)
        Fraction(1, 35)
        >>> Fraction(Fraction(1, 7), Fraction(2, 3))
        Fraction(3, 14)
        >>> Fraction('314')
        Fraction(314, 1)
        >>> Fraction('-35/4')
        Fraction(-35, 4)
        >>> Fraction('3.1415') # conversion kutoka numeric string
        Fraction(6283, 2000)
        >>> Fraction('-47e-2') # string may include a decimal exponent
        Fraction(-47, 100)
        >>> Fraction(1.47)  # direct construction kutoka float (exact conversion)
        Fraction(6620291452234629, 4503599627370496)
        >>> Fraction(2.25)
        Fraction(9, 4)
        >>> Fraction(Decimal('1.47'))
        Fraction(147, 100)

        """
        self = super(Fraction, cls).__new__(cls)

        ikiwa denominator is None:
            ikiwa type(numerator) is int:
                self._numerator = numerator
                self._denominator = 1
                rudisha self

            elikiwa isinstance(numerator, numbers.Rational):
                self._numerator = numerator.numerator
                self._denominator = numerator.denominator
                rudisha self

            elikiwa isinstance(numerator, (float, Decimal)):
                # Exact conversion
                self._numerator, self._denominator = numerator.as_integer_ratio()
                rudisha self

            elikiwa isinstance(numerator, str):
                # Handle construction kutoka strings.
                m = _RATIONAL_FORMAT.match(numerator)
                ikiwa m is None:
                    raise ValueError('Invalid literal for Fraction: %r' %
                                     numerator)
                numerator = int(m.group('num') or '0')
                denom = m.group('denom')
                ikiwa denom:
                    denominator = int(denom)
                else:
                    denominator = 1
                    decimal = m.group('decimal')
                    ikiwa decimal:
                        scale = 10**len(decimal)
                        numerator = numerator * scale + int(decimal)
                        denominator *= scale
                    exp = m.group('exp')
                    ikiwa exp:
                        exp = int(exp)
                        ikiwa exp >= 0:
                            numerator *= 10**exp
                        else:
                            denominator *= 10**-exp
                ikiwa m.group('sign') == '-':
                    numerator = -numerator

            else:
                raise TypeError("argument should be a string "
                                "or a Rational instance")

        elikiwa type(numerator) is int is type(denominator):
            pass # *very* normal case

        elikiwa (isinstance(numerator, numbers.Rational) and
            isinstance(denominator, numbers.Rational)):
            numerator, denominator = (
                numerator.numerator * denominator.denominator,
                denominator.numerator * numerator.denominator
                )
        else:
            raise TypeError("both arguments should be "
                            "Rational instances")

        ikiwa denominator == 0:
            raise ZeroDivisionError('Fraction(%s, 0)' % numerator)
        ikiwa _normalize:
            ikiwa type(numerator) is int is type(denominator):
                # *very* normal case
                g = math.gcd(numerator, denominator)
                ikiwa denominator < 0:
                    g = -g
            else:
                g = _gcd(numerator, denominator)
            numerator //= g
            denominator //= g
        self._numerator = numerator
        self._denominator = denominator
        rudisha self

    @classmethod
    eleza kutoka_float(cls, f):
        """Converts a finite float to a rational number, exactly.

        Beware that Fraction.kutoka_float(0.3) != Fraction(3, 10).

        """
        ikiwa isinstance(f, numbers.Integral):
            rudisha cls(f)
        elikiwa not isinstance(f, float):
            raise TypeError("%s.kutoka_float() only takes floats, not %r (%s)" %
                            (cls.__name__, f, type(f).__name__))
        rudisha cls(*f.as_integer_ratio())

    @classmethod
    eleza kutoka_decimal(cls, dec):
        """Converts a finite Decimal instance to a rational number, exactly."""
        kutoka decimal agiza Decimal
        ikiwa isinstance(dec, numbers.Integral):
            dec = Decimal(int(dec))
        elikiwa not isinstance(dec, Decimal):
            raise TypeError(
                "%s.kutoka_decimal() only takes Decimals, not %r (%s)" %
                (cls.__name__, dec, type(dec).__name__))
        rudisha cls(*dec.as_integer_ratio())

    eleza as_integer_ratio(self):
        """Return the integer ratio as a tuple.

        Return a tuple of two integers, whose ratio is equal to the
        Fraction and with a positive denominator.
        """
        rudisha (self._numerator, self._denominator)

    eleza limit_denominator(self, max_denominator=1000000):
        """Closest Fraction to self with denominator at most max_denominator.

        >>> Fraction('3.141592653589793').limit_denominator(10)
        Fraction(22, 7)
        >>> Fraction('3.141592653589793').limit_denominator(100)
        Fraction(311, 99)
        >>> Fraction(4321, 8765).limit_denominator(10000)
        Fraction(4321, 8765)

        """
        # Algorithm notes: For any real number x, define a *best upper
        # approximation* to x to be a rational number p/q such that:
        #
        #   (1) p/q >= x, and
        #   (2) ikiwa p/q > r/s >= x then s > q, for any rational r/s.
        #
        # Define *best lower approximation* similarly.  Then it can be
        # proved that a rational number is a best upper or lower
        # approximation to x if, and only if, it is a convergent or
        # semiconvergent of the (unique shortest) continued fraction
        # associated to x.
        #
        # To find a best rational approximation with denominator <= M,
        # we find the best upper and lower approximations with
        # denominator <= M and take whichever of these is closer to x.
        # In the event of a tie, the bound with smaller denominator is
        # chosen.  If both denominators are equal (which can happen
        # only when max_denominator == 1 and self is midway between
        # two integers) the lower bound---i.e., the floor of self, is
        # taken.

        ikiwa max_denominator < 1:
            raise ValueError("max_denominator should be at least 1")
        ikiwa self._denominator <= max_denominator:
            rudisha Fraction(self)

        p0, q0, p1, q1 = 0, 1, 1, 0
        n, d = self._numerator, self._denominator
        while True:
            a = n//d
            q2 = q0+a*q1
            ikiwa q2 > max_denominator:
                break
            p0, q0, p1, q1 = p1, q1, p0+a*p1, q2
            n, d = d, n-a*d

        k = (max_denominator-q0)//q1
        bound1 = Fraction(p0+k*p1, q0+k*q1)
        bound2 = Fraction(p1, q1)
        ikiwa abs(bound2 - self) <= abs(bound1-self):
            rudisha bound2
        else:
            rudisha bound1

    @property
    eleza numerator(a):
        rudisha a._numerator

    @property
    eleza denominator(a):
        rudisha a._denominator

    eleza __repr__(self):
        """repr(self)"""
        rudisha '%s(%s, %s)' % (self.__class__.__name__,
                               self._numerator, self._denominator)

    eleza __str__(self):
        """str(self)"""
        ikiwa self._denominator == 1:
            rudisha str(self._numerator)
        else:
            rudisha '%s/%s' % (self._numerator, self._denominator)

    eleza _operator_fallbacks(monomorphic_operator, fallback_operator):
        """Generates forward and reverse operators given a purely-rational
        operator and a function kutoka the operator module.

        Use this like:
        __op__, __rop__ = _operator_fallbacks(just_rational_op, operator.op)

        In general, we want to implement the arithmetic operations so
        that mixed-mode operations either call an implementation whose
        author knew about the types of both arguments, or convert both
        to the nearest built in type and do the operation there. In
        Fraction, that means that we define __add__ and __radd__ as:

            eleza __add__(self, other):
                # Both types have numerators/denominator attributes,
                # so do the operation directly
                ikiwa isinstance(other, (int, Fraction)):
                    rudisha Fraction(self.numerator * other.denominator +
                                    other.numerator * self.denominator,
                                    self.denominator * other.denominator)
                # float and complex don't have those operations, but we
                # know about those types, so special case them.
                elikiwa isinstance(other, float):
                    rudisha float(self) + other
                elikiwa isinstance(other, complex):
                    rudisha complex(self) + other
                # Let the other type take over.
                rudisha NotImplemented

            eleza __radd__(self, other):
                # radd handles more types than add because there's
                # nothing left to fall back to.
                ikiwa isinstance(other, numbers.Rational):
                    rudisha Fraction(self.numerator * other.denominator +
                                    other.numerator * self.denominator,
                                    self.denominator * other.denominator)
                elikiwa isinstance(other, Real):
                    rudisha float(other) + float(self)
                elikiwa isinstance(other, Complex):
                    rudisha complex(other) + complex(self)
                rudisha NotImplemented


        There are 5 different cases for a mixed-type addition on
        Fraction. I'll refer to all of the above code that doesn't
        refer to Fraction, float, or complex as "boilerplate". 'r'
        will be an instance of Fraction, which is a subtype of
        Rational (r : Fraction <: Rational), and b : B <:
        Complex. The first three involve 'r + b':

            1. If B <: Fraction, int, float, or complex, we handle
               that specially, and all is well.
            2. If Fraction falls back to the boilerplate code, and it
               were to rudisha a value kutoka __add__, we'd miss the
               possibility that B defines a more intelligent __radd__,
               so the boilerplate should rudisha NotImplemented kutoka
               __add__. In particular, we don't handle Rational
               here, even though we could get an exact answer, in case
               the other type wants to do something special.
            3. If B <: Fraction, Python tries B.__radd__ before
               Fraction.__add__. This is ok, because it was
               implemented with knowledge of Fraction, so it can
               handle those instances before delegating to Real or
               Complex.

        The next two situations describe 'b + r'. We assume that b
        didn't know about Fraction in its implementation, and that it
        uses similar boilerplate code:

            4. If B <: Rational, then __radd_ converts both to the
               builtin rational type (hey look, that's us) and
               proceeds.
            5. Otherwise, __radd__ tries to find the nearest common
               base ABC, and fall back to its builtin type. Since this
               kundi doesn't subkundi a concrete type, there's no
               implementation to fall back to, so we need to try as
               hard as possible to rudisha an actual value, or the user
               will get a TypeError.

        """
        eleza forward(a, b):
            ikiwa isinstance(b, (int, Fraction)):
                rudisha monomorphic_operator(a, b)
            elikiwa isinstance(b, float):
                rudisha fallback_operator(float(a), b)
            elikiwa isinstance(b, complex):
                rudisha fallback_operator(complex(a), b)
            else:
                rudisha NotImplemented
        forward.__name__ = '__' + fallback_operator.__name__ + '__'
        forward.__doc__ = monomorphic_operator.__doc__

        eleza reverse(b, a):
            ikiwa isinstance(a, numbers.Rational):
                # Includes ints.
                rudisha monomorphic_operator(a, b)
            elikiwa isinstance(a, numbers.Real):
                rudisha fallback_operator(float(a), float(b))
            elikiwa isinstance(a, numbers.Complex):
                rudisha fallback_operator(complex(a), complex(b))
            else:
                rudisha NotImplemented
        reverse.__name__ = '__r' + fallback_operator.__name__ + '__'
        reverse.__doc__ = monomorphic_operator.__doc__

        rudisha forward, reverse

    eleza _add(a, b):
        """a + b"""
        da, db = a.denominator, b.denominator
        rudisha Fraction(a.numerator * db + b.numerator * da,
                        da * db)

    __add__, __radd__ = _operator_fallbacks(_add, operator.add)

    eleza _sub(a, b):
        """a - b"""
        da, db = a.denominator, b.denominator
        rudisha Fraction(a.numerator * db - b.numerator * da,
                        da * db)

    __sub__, __rsub__ = _operator_fallbacks(_sub, operator.sub)

    eleza _mul(a, b):
        """a * b"""
        rudisha Fraction(a.numerator * b.numerator, a.denominator * b.denominator)

    __mul__, __rmul__ = _operator_fallbacks(_mul, operator.mul)

    eleza _div(a, b):
        """a / b"""
        rudisha Fraction(a.numerator * b.denominator,
                        a.denominator * b.numerator)

    __truediv__, __rtruediv__ = _operator_fallbacks(_div, operator.truediv)

    eleza _floordiv(a, b):
        """a // b"""
        rudisha (a.numerator * b.denominator) // (a.denominator * b.numerator)

    __floordiv__, __rfloordiv__ = _operator_fallbacks(_floordiv, operator.floordiv)

    eleza _divmod(a, b):
        """(a // b, a % b)"""
        da, db = a.denominator, b.denominator
        div, n_mod = divmod(a.numerator * db, da * b.numerator)
        rudisha div, Fraction(n_mod, da * db)

    __divmod__, __rdivmod__ = _operator_fallbacks(_divmod, divmod)

    eleza _mod(a, b):
        """a % b"""
        da, db = a.denominator, b.denominator
        rudisha Fraction((a.numerator * db) % (b.numerator * da), da * db)

    __mod__, __rmod__ = _operator_fallbacks(_mod, operator.mod)

    eleza __pow__(a, b):
        """a ** b

        If b is not an integer, the result will be a float or complex
        since roots are generally irrational. If b is an integer, the
        result will be rational.

        """
        ikiwa isinstance(b, numbers.Rational):
            ikiwa b.denominator == 1:
                power = b.numerator
                ikiwa power >= 0:
                    rudisha Fraction(a._numerator ** power,
                                    a._denominator ** power,
                                    _normalize=False)
                elikiwa a._numerator >= 0:
                    rudisha Fraction(a._denominator ** -power,
                                    a._numerator ** -power,
                                    _normalize=False)
                else:
                    rudisha Fraction((-a._denominator) ** -power,
                                    (-a._numerator) ** -power,
                                    _normalize=False)
            else:
                # A fractional power will generally produce an
                # irrational number.
                rudisha float(a) ** float(b)
        else:
            rudisha float(a) ** b

    eleza __rpow__(b, a):
        """a ** b"""
        ikiwa b._denominator == 1 and b._numerator >= 0:
            # If a is an int, keep it that way ikiwa possible.
            rudisha a ** b._numerator

        ikiwa isinstance(a, numbers.Rational):
            rudisha Fraction(a.numerator, a.denominator) ** b

        ikiwa b._denominator == 1:
            rudisha a ** b._numerator

        rudisha a ** float(b)

    eleza __pos__(a):
        """+a: Coerces a subkundi instance to Fraction"""
        rudisha Fraction(a._numerator, a._denominator, _normalize=False)

    eleza __neg__(a):
        """-a"""
        rudisha Fraction(-a._numerator, a._denominator, _normalize=False)

    eleza __abs__(a):
        """abs(a)"""
        rudisha Fraction(abs(a._numerator), a._denominator, _normalize=False)

    eleza __trunc__(a):
        """trunc(a)"""
        ikiwa a._numerator < 0:
            rudisha -(-a._numerator // a._denominator)
        else:
            rudisha a._numerator // a._denominator

    eleza __floor__(a):
        """math.floor(a)"""
        rudisha a.numerator // a.denominator

    eleza __ceil__(a):
        """math.ceil(a)"""
        # The negations cleverly convince floordiv to rudisha the ceiling.
        rudisha -(-a.numerator // a.denominator)

    eleza __round__(self, ndigits=None):
        """round(self, ndigits)

        Rounds half toward even.
        """
        ikiwa ndigits is None:
            floor, remainder = divmod(self.numerator, self.denominator)
            ikiwa remainder * 2 < self.denominator:
                rudisha floor
            elikiwa remainder * 2 > self.denominator:
                rudisha floor + 1
            # Deal with the half case:
            elikiwa floor % 2 == 0:
                rudisha floor
            else:
                rudisha floor + 1
        shift = 10**abs(ndigits)
        # See _operator_fallbacks.forward to check that the results of
        # these operations will always be Fraction and therefore have
        # round().
        ikiwa ndigits > 0:
            rudisha Fraction(round(self * shift), shift)
        else:
            rudisha Fraction(round(self / shift) * shift)

    eleza __hash__(self):
        """hash(self)"""

        # XXX since this method is expensive, consider caching the result

        # In order to make sure that the hash of a Fraction agrees
        # with the hash of a numerically equal integer, float or
        # Decimal instance, we follow the rules for numeric hashes
        # outlined in the documentation.  (See library docs, 'Built-in
        # Types').

        # dinv is the inverse of self._denominator modulo the prime
        # _PyHASH_MODULUS, or 0 ikiwa self._denominator is divisible by
        # _PyHASH_MODULUS.
        dinv = pow(self._denominator, _PyHASH_MODULUS - 2, _PyHASH_MODULUS)
        ikiwa not dinv:
            hash_ = _PyHASH_INF
        else:
            hash_ = abs(self._numerator) * dinv % _PyHASH_MODULUS
        result = hash_ ikiwa self >= 0 else -hash_
        rudisha -2 ikiwa result == -1 else result

    eleza __eq__(a, b):
        """a == b"""
        ikiwa type(b) is int:
            rudisha a._numerator == b and a._denominator == 1
        ikiwa isinstance(b, numbers.Rational):
            rudisha (a._numerator == b.numerator and
                    a._denominator == b.denominator)
        ikiwa isinstance(b, numbers.Complex) and b.imag == 0:
            b = b.real
        ikiwa isinstance(b, float):
            ikiwa math.isnan(b) or math.isinf(b):
                # comparisons with an infinity or nan should behave in
                # the same way for any finite a, so treat a as zero.
                rudisha 0.0 == b
            else:
                rudisha a == a.kutoka_float(b)
        else:
            # Since a doesn't know how to compare with b, let's give b
            # a chance to compare itself with a.
            rudisha NotImplemented

    eleza _richcmp(self, other, op):
        """Helper for comparison operators, for internal use only.

        Implement comparison between a Rational instance `self`, and
        either another Rational instance or a float `other`.  If
        `other` is not a Rational instance or a float, return
        NotImplemented. `op` should be one of the six standard
        comparison operators.

        """
        # convert other to a Rational instance where reasonable.
        ikiwa isinstance(other, numbers.Rational):
            rudisha op(self._numerator * other.denominator,
                      self._denominator * other.numerator)
        ikiwa isinstance(other, float):
            ikiwa math.isnan(other) or math.isinf(other):
                rudisha op(0.0, other)
            else:
                rudisha op(self, self.kutoka_float(other))
        else:
            rudisha NotImplemented

    eleza __lt__(a, b):
        """a < b"""
        rudisha a._richcmp(b, operator.lt)

    eleza __gt__(a, b):
        """a > b"""
        rudisha a._richcmp(b, operator.gt)

    eleza __le__(a, b):
        """a <= b"""
        rudisha a._richcmp(b, operator.le)

    eleza __ge__(a, b):
        """a >= b"""
        rudisha a._richcmp(b, operator.ge)

    eleza __bool__(a):
        """a != 0"""
        rudisha a._numerator != 0

    # support for pickling, copy, and deepcopy

    eleza __reduce__(self):
        rudisha (self.__class__, (str(self),))

    eleza __copy__(self):
        ikiwa type(self) == Fraction:
            rudisha self     # I'm immutable; therefore I am my own clone
        rudisha self.__class__(self._numerator, self._denominator)

    eleza __deepcopy__(self, memo):
        ikiwa type(self) == Fraction:
            rudisha self     # My components are also immutable
        rudisha self.__class__(self._numerator, self._denominator)
