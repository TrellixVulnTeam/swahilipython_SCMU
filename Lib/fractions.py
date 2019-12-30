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
    """Calculate the Greatest Common Divisor of a na b.

    Unless b==0, the result will have the same sign kama b (so that when
    b ni divided by it, the result comes out positive).
    """
    agiza warnings
    warnings.warn('fractions.gcd() ni deprecated. Use math.gcd() instead.',
                  DeprecationWarning, 2)
    ikiwa type(a) ni int ni type(b):
        ikiwa (b ama a) < 0:
            rudisha -math.gcd(a, b)
        rudisha math.gcd(a, b)
    rudisha _gcd(a, b)

eleza _gcd(a, b):
    # Supports non-integers kila backward compatibility.
    wakati b:
        a, b = b, a%b
    rudisha a

# Constants related to the hash implementation;  hash(x) ni based
# on the reduction of x modulo the prime _PyHASH_MODULUS.
_PyHASH_MODULUS = sys.hash_info.modulus
# Value to be used kila rationals that reduce to infinity modulo
# _PyHASH_MODULUS.
_PyHASH_INF = sys.hash_info.inf

_RATIONAL_FORMAT = re.compile(r"""
    \A\s*                      # optional whitespace at the start, then
    (?P<sign>[-+]?)            # an optional sign, then
    (?=\d|\.\d)                # lookahead kila digit ama .digit
    (?P<num>\d*)               # numerator (possibly empty)
    (?:                        # followed by
       (?:/(?P<denom>\d+))?    # an optional denominator
    |                          # ama
       (?:\.(?P<decimal>\d*))? # an optional fractional part
       (?:E(?P<exp>[-+]?\d+))? # na optional exponent
    )
    \s*\Z                      # na optional whitespace to finish
""", re.VERBOSE | re.IGNORECASE)


kundi Fraction(numbers.Rational):
    """This kundi implements rational numbers.

    In the two-argument form of the constructor, Fraction(8, 6) will
    produce a rational number equivalent to 4/3. Both arguments must
    be Rational. The numerator defaults to 0 na the denominator
    defaults to 1 so that Fraction(3) == 3 na Fraction() == 0.

    Fractions can also be constructed from:

      - numeric strings similar to those accepted by the
        float constructor (kila example, '-2.3' ama '1e10')

      - strings of the form '123/456'

      - float na Decimal instances

      - other Rational instances (including integers)

    """

    __slots__ = ('_numerator', '_denominator')

    # We're immutable, so use __new__ sio __init__
    eleza __new__(cls, numerator=0, denominator=Tupu, *, _normalize=Kweli):
        """Constructs a Rational.

        Takes a string like '3/2' ama '1.5', another Rational instance, a
        numerator/denominator pair, ama a float.

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

        ikiwa denominator ni Tupu:
            ikiwa type(numerator) ni int:
                self._numerator = numerator
                self._denominator = 1
                rudisha self

            lasivyo isinstance(numerator, numbers.Rational):
                self._numerator = numerator.numerator
                self._denominator = numerator.denominator
                rudisha self

            lasivyo isinstance(numerator, (float, Decimal)):
                # Exact conversion
                self._numerator, self._denominator = numerator.as_integer_ratio()
                rudisha self

            lasivyo isinstance(numerator, str):
                # Handle construction kutoka strings.
                m = _RATIONAL_FORMAT.match(numerator)
                ikiwa m ni Tupu:
                    ashiria ValueError('Invalid literal kila Fraction: %r' %
                                     numerator)
                numerator = int(m.group('num') ama '0')
                denom = m.group('denom')
                ikiwa denom:
                    denominator = int(denom)
                isipokua:
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
                        isipokua:
                            denominator *= 10**-exp
                ikiwa m.group('sign') == '-':
                    numerator = -numerator

            isipokua:
                ashiria TypeError("argument should be a string "
                                "or a Rational instance")

        lasivyo type(numerator) ni int ni type(denominator):
            pita # *very* normal case

        lasivyo (isinstance(numerator, numbers.Rational) na
            isinstance(denominator, numbers.Rational)):
            numerator, denominator = (
                numerator.numerator * denominator.denominator,
                denominator.numerator * numerator.denominator
                )
        isipokua:
            ashiria TypeError("both arguments should be "
                            "Rational instances")

        ikiwa denominator == 0:
            ashiria ZeroDivisionError('Fraction(%s, 0)' % numerator)
        ikiwa _normalize:
            ikiwa type(numerator) ni int ni type(denominator):
                # *very* normal case
                g = math.gcd(numerator, denominator)
                ikiwa denominator < 0:
                    g = -g
            isipokua:
                g = _gcd(numerator, denominator)
            numerator //= g
            denominator //= g
        self._numerator = numerator
        self._denominator = denominator
        rudisha self

    @classmethod
    eleza from_float(cls, f):
        """Converts a finite float to a rational number, exactly.

        Beware that Fraction.from_float(0.3) != Fraction(3, 10).

        """
        ikiwa isinstance(f, numbers.Integral):
            rudisha cls(f)
        lasivyo sio isinstance(f, float):
            ashiria TypeError("%s.from_float() only takes floats, sio %r (%s)" %
                            (cls.__name__, f, type(f).__name__))
        rudisha cls(*f.as_integer_ratio())

    @classmethod
    eleza from_decimal(cls, dec):
        """Converts a finite Decimal instance to a rational number, exactly."""
        kutoka decimal agiza Decimal
        ikiwa isinstance(dec, numbers.Integral):
            dec = Decimal(int(dec))
        lasivyo sio isinstance(dec, Decimal):
            ashiria TypeError(
                "%s.from_decimal() only takes Decimals, sio %r (%s)" %
                (cls.__name__, dec, type(dec).__name__))
        rudisha cls(*dec.as_integer_ratio())

    eleza as_integer_ratio(self):
        """Return the integer ratio kama a tuple.

        Return a tuple of two integers, whose ratio ni equal to the
        Fraction na ukijumuisha a positive denominator.
        """
        rudisha (self._numerator, self._denominator)

    eleza limit_denominator(self, max_denominator=1000000):
        """Closest Fraction to self ukijumuisha denominator at most max_denominator.

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
        #   (1) p/q >= x, na
        #   (2) ikiwa p/q > r/s >= x then s > q, kila any rational r/s.
        #
        # Define *best lower approximation* similarly.  Then it can be
        # proved that a rational number ni a best upper ama lower
        # approximation to x if, na only if, it ni a convergent ama
        # semiconvergent of the (unique shortest) endelead fraction
        # associated to x.
        #
        # To find a best rational approximation ukijumuisha denominator <= M,
        # we find the best upper na lower approximations with
        # denominator <= M na take whichever of these ni closer to x.
        # In the event of a tie, the bound ukijumuisha smaller denominator is
        # chosen.  If both denominators are equal (which can happen
        # only when max_denominator == 1 na self ni midway between
        # two integers) the lower bound---i.e., the floor of self, is
        # taken.

        ikiwa max_denominator < 1:
            ashiria ValueError("max_denominator should be at least 1")
        ikiwa self._denominator <= max_denominator:
            rudisha Fraction(self)

        p0, q0, p1, q1 = 0, 1, 1, 0
        n, d = self._numerator, self._denominator
        wakati Kweli:
            a = n//d
            q2 = q0+a*q1
            ikiwa q2 > max_denominator:
                koma
            p0, q0, p1, q1 = p1, q1, p0+a*p1, q2
            n, d = d, n-a*d

        k = (max_denominator-q0)//q1
        bound1 = Fraction(p0+k*p1, q0+k*q1)
        bound2 = Fraction(p1, q1)
        ikiwa abs(bound2 - self) <= abs(bound1-self):
            rudisha bound2
        isipokua:
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
        isipokua:
            rudisha '%s/%s' % (self._numerator, self._denominator)

    eleza _operator_fallbacks(monomorphic_operator, fallback_operator):
        """Generates forward na reverse operators given a purely-rational
        operator na a function kutoka the operator module.

        Use this like:
        __op__, __rop__ = _operator_fallbacks(just_rational_op, operator.op)

        In general, we want to implement the arithmetic operations so
        that mixed-mode operations either call an implementation whose
        author knew about the types of both arguments, ama convert both
        to the nearest built kwenye type na do the operation there. In
        Fraction, that means that we define __add__ na __radd__ as:

            eleza __add__(self, other):
                # Both types have numerators/denominator attributes,
                # so do the operation directly
                ikiwa isinstance(other, (int, Fraction)):
                    rudisha Fraction(self.numerator * other.denominator +
                                    other.numerator * self.denominator,
                                    self.denominator * other.denominator)
                # float na complex don't have those operations, but we
                # know about those types, so special case them.
                lasivyo isinstance(other, float):
                    rudisha float(self) + other
                lasivyo isinstance(other, complex):
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
                lasivyo isinstance(other, Real):
                    rudisha float(other) + float(self)
                lasivyo isinstance(other, Complex):
                    rudisha complex(other) + complex(self)
                rudisha NotImplemented


        There are 5 different cases kila a mixed-type addition on
        Fraction. I'll refer to all of the above code that doesn't
        refer to Fraction, float, ama complex kama "boilerplate". 'r'
        will be an instance of Fraction, which ni a subtype of
        Rational (r : Fraction <: Rational), na b : B <:
        Complex. The first three involve 'r + b':

            1. If B <: Fraction, int, float, ama complex, we handle
               that specially, na all ni well.
            2. If Fraction falls back to the boilerplate code, na it
               were to rudisha a value kutoka __add__, we'd miss the
               possibility that B defines a more intelligent __radd__,
               so the boilerplate should rudisha NotImplemented from
               __add__. In particular, we don't handle Rational
               here, even though we could get an exact answer, kwenye case
               the other type wants to do something special.
            3. If B <: Fraction, Python tries B.__radd__ before
               Fraction.__add__. This ni ok, because it was
               implemented ukijumuisha knowledge of Fraction, so it can
               handle those instances before delegating to Real ama
               Complex.

        The next two situations describe 'b + r'. We assume that b
        didn't know about Fraction kwenye its implementation, na that it
        uses similar boilerplate code:

            4. If B <: Rational, then __radd_ converts both to the
               builtin rational type (hey look, that's us) na
               proceeds.
            5. Otherwise, __radd__ tries to find the nearest common
               base ABC, na fall back to its builtin type. Since this
               kundi doesn't subkundi a concrete type, there's no
               implementation to fall back to, so we need to try as
               hard kama possible to rudisha an actual value, ama the user
               will get a TypeError.

        """
        eleza forward(a, b):
            ikiwa isinstance(b, (int, Fraction)):
                rudisha monomorphic_operator(a, b)
            lasivyo isinstance(b, float):
                rudisha fallback_operator(float(a), b)
            lasivyo isinstance(b, complex):
                rudisha fallback_operator(complex(a), b)
            isipokua:
                rudisha NotImplemented
        forward.__name__ = '__' + fallback_operator.__name__ + '__'
        forward.__doc__ = monomorphic_operator.__doc__

        eleza reverse(b, a):
            ikiwa isinstance(a, numbers.Rational):
                # Includes ints.
                rudisha monomorphic_operator(a, b)
            lasivyo isinstance(a, numbers.Real):
                rudisha fallback_operator(float(a), float(b))
            lasivyo isinstance(a, numbers.Complex):
                rudisha fallback_operator(complex(a), complex(b))
            isipokua:
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

        If b ni sio an integer, the result will be a float ama complex
        since roots are generally irrational. If b ni an integer, the
        result will be rational.

        """
        ikiwa isinstance(b, numbers.Rational):
            ikiwa b.denominator == 1:
                power = b.numerator
                ikiwa power >= 0:
                    rudisha Fraction(a._numerator ** power,
                                    a._denominator ** power,
                                    _normalize=Uongo)
                lasivyo a._numerator >= 0:
                    rudisha Fraction(a._denominator ** -power,
                                    a._numerator ** -power,
                                    _normalize=Uongo)
                isipokua:
                    rudisha Fraction((-a._denominator) ** -power,
                                    (-a._numerator) ** -power,
                                    _normalize=Uongo)
            isipokua:
                # A fractional power will generally produce an
                # irrational number.
                rudisha float(a) ** float(b)
        isipokua:
            rudisha float(a) ** b

    eleza __rpow__(b, a):
        """a ** b"""
        ikiwa b._denominator == 1 na b._numerator >= 0:
            # If a ni an int, keep it that way ikiwa possible.
            rudisha a ** b._numerator

        ikiwa isinstance(a, numbers.Rational):
            rudisha Fraction(a.numerator, a.denominator) ** b

        ikiwa b._denominator == 1:
            rudisha a ** b._numerator

        rudisha a ** float(b)

    eleza __pos__(a):
        """+a: Coerces a subkundi instance to Fraction"""
        rudisha Fraction(a._numerator, a._denominator, _normalize=Uongo)

    eleza __neg__(a):
        """-a"""
        rudisha Fraction(-a._numerator, a._denominator, _normalize=Uongo)

    eleza __abs__(a):
        """abs(a)"""
        rudisha Fraction(abs(a._numerator), a._denominator, _normalize=Uongo)

    eleza __trunc__(a):
        """trunc(a)"""
        ikiwa a._numerator < 0:
            rudisha -(-a._numerator // a._denominator)
        isipokua:
            rudisha a._numerator // a._denominator

    eleza __floor__(a):
        """math.floor(a)"""
        rudisha a.numerator // a.denominator

    eleza __ceil__(a):
        """math.ceil(a)"""
        # The negations cleverly convince floordiv to rudisha the ceiling.
        rudisha -(-a.numerator // a.denominator)

    eleza __round__(self, ndigits=Tupu):
        """round(self, ndigits)

        Rounds half toward even.
        """
        ikiwa ndigits ni Tupu:
            floor, remainder = divmod(self.numerator, self.denominator)
            ikiwa remainder * 2 < self.denominator:
                rudisha floor
            lasivyo remainder * 2 > self.denominator:
                rudisha floor + 1
            # Deal ukijumuisha the half case:
            lasivyo floor % 2 == 0:
                rudisha floor
            isipokua:
                rudisha floor + 1
        shift = 10**abs(ndigits)
        # See _operator_fallbacks.forward to check that the results of
        # these operations will always be Fraction na therefore have
        # round().
        ikiwa ndigits > 0:
            rudisha Fraction(round(self * shift), shift)
        isipokua:
            rudisha Fraction(round(self / shift) * shift)

    eleza __hash__(self):
        """hash(self)"""

        # XXX since this method ni expensive, consider caching the result

        # In order to make sure that the hash of a Fraction agrees
        # ukijumuisha the hash of a numerically equal integer, float ama
        # Decimal instance, we follow the rules kila numeric hashes
        # outlined kwenye the documentation.  (See library docs, 'Built-in
        # Types').

        # dinv ni the inverse of self._denominator modulo the prime
        # _PyHASH_MODULUS, ama 0 ikiwa self._denominator ni divisible by
        # _PyHASH_MODULUS.
        dinv = pow(self._denominator, _PyHASH_MODULUS - 2, _PyHASH_MODULUS)
        ikiwa sio dinv:
            hash_ = _PyHASH_INF
        isipokua:
            hash_ = abs(self._numerator) * dinv % _PyHASH_MODULUS
        result = hash_ ikiwa self >= 0 isipokua -hash_
        rudisha -2 ikiwa result == -1 isipokua result

    eleza __eq__(a, b):
        """a == b"""
        ikiwa type(b) ni int:
            rudisha a._numerator == b na a._denominator == 1
        ikiwa isinstance(b, numbers.Rational):
            rudisha (a._numerator == b.numerator na
                    a._denominator == b.denominator)
        ikiwa isinstance(b, numbers.Complex) na b.imag == 0:
            b = b.real
        ikiwa isinstance(b, float):
            ikiwa math.isnan(b) ama math.isinf(b):
                # comparisons ukijumuisha an infinity ama nan should behave in
                # the same way kila any finite a, so treat a kama zero.
                rudisha 0.0 == b
            isipokua:
                rudisha a == a.from_float(b)
        isipokua:
            # Since a doesn't know how to compare ukijumuisha b, let's give b
            # a chance to compare itself ukijumuisha a.
            rudisha NotImplemented

    eleza _richcmp(self, other, op):
        """Helper kila comparison operators, kila internal use only.

        Implement comparison between a Rational instance `self`, na
        either another Rational instance ama a float `other`.  If
        `other` ni sio a Rational instance ama a float, rudisha
        NotImplemented. `op` should be one of the six standard
        comparison operators.

        """
        # convert other to a Rational instance where reasonable.
        ikiwa isinstance(other, numbers.Rational):
            rudisha op(self._numerator * other.denominator,
                      self._denominator * other.numerator)
        ikiwa isinstance(other, float):
            ikiwa math.isnan(other) ama math.isinf(other):
                rudisha op(0.0, other)
            isipokua:
                rudisha op(self, self.from_float(other))
        isipokua:
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

    # support kila pickling, copy, na deepcopy

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
