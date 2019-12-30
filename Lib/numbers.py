# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Abstract Base Classes (ABCs) kila numbers, according to PEP 3141.

TODO: Fill out more detailed documentation on the operators."""

kutoka abc agiza ABCMeta, abstractmethod

__all__ = ["Number", "Complex", "Real", "Rational", "Integral"]

kundi Number(metaclass=ABCMeta):
    """All numbers inherit kutoka this class.

    If you just want to check ikiwa an argument x ni a number, without
    caring what kind, use isinstance(x, Number).
    """
    __slots__ = ()

    # Concrete numeric types must provide their own hash implementation
    __hash__ = Tupu


## Notes on Decimal
## ----------------
## Decimal has all of the methods specified by the Real abc, but it should
## sio be registered as a Real because decimals do sio interoperate with
## binary floats (i.e.  Decimal('3.14') + 2.71828 ni undefined).  But,
## abstract reals are expected to interoperate (i.e. R1 + R2 should be
## expected to work ikiwa R1 na R2 are both Reals).

kundi Complex(Number):
    """Complex defines the operations that work on the builtin complex type.

    In short, those are: a conversion to complex, .real, .imag, +, -,
    *, /, abs(), .conjugate, ==, na !=.

    If it ni given heterogeneous arguments, na doesn't have special
    knowledge about them, it should fall back to the builtin complex
    type as described below.
    """

    __slots__ = ()

    @abstractmethod
    eleza __complex__(self):
        """Return a builtin complex instance. Called kila complex(self)."""

    eleza __bool__(self):
        """Kweli ikiwa self != 0. Called kila bool(self)."""
        rudisha self != 0

    @property
    @abstractmethod
    eleza real(self):
        """Retrieve the real component of this number.

        This should subkundi Real.
        """
         ashiria NotImplementedError

    @property
    @abstractmethod
    eleza imag(self):
        """Retrieve the imaginary component of this number.

        This should subkundi Real.
        """
         ashiria NotImplementedError

    @abstractmethod
    eleza __add__(self, other):
        """self + other"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __radd__(self, other):
        """other + self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __neg__(self):
        """-self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __pos__(self):
        """+self"""
         ashiria NotImplementedError

    eleza __sub__(self, other):
        """self - other"""
        rudisha self + -other

    eleza __rsub__(self, other):
        """other - self"""
        rudisha -self + other

    @abstractmethod
    eleza __mul__(self, other):
        """self * other"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rmul__(self, other):
        """other * self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __truediv__(self, other):
        """self / other: Should promote to float when necessary."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rtruediv__(self, other):
        """other / self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __pow__(self, exponent):
        """self**exponent; should promote to float ama complex when necessary."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rpow__(self, base):
        """base ** self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __abs__(self):
        """Returns the Real distance kutoka 0. Called kila abs(self)."""
         ashiria NotImplementedError

    @abstractmethod
    eleza conjugate(self):
        """(x+y*i).conjugate() returns (x-y*i)."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __eq__(self, other):
        """self == other"""
         ashiria NotImplementedError

Complex.register(complex)


kundi Real(Complex):
    """To Complex, Real adds the operations that work on real numbers.

    In short, those are: a conversion to float, trunc(), divmod,
    %, <, <=, >, na >=.

    Real also provides defaults kila the derived operations.
    """

    __slots__ = ()

    @abstractmethod
    eleza __float__(self):
        """Any Real can be converted to a native float object.

        Called kila float(self)."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __trunc__(self):
        """trunc(self): Truncates self to an Integral.

        Returns an Integral i such that:
          * i>0 iff self>0;
          * abs(i) <= abs(self);
          * kila any Integral j satisfying the first two conditions,
            abs(i) >= abs(j) [i.e. i has "maximal" abs among those].
        i.e. "truncate towards 0".
        """
         ashiria NotImplementedError

    @abstractmethod
    eleza __floor__(self):
        """Finds the greatest Integral <= self."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __ceil__(self):
        """Finds the least Integral >= self."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __round__(self, ndigits=Tupu):
        """Rounds self to ndigits decimal places, defaulting to 0.

        If ndigits ni omitted ama Tupu, returns an Integral, otherwise
        returns a Real. Rounds half toward even.
        """
         ashiria NotImplementedError

    eleza __divmod__(self, other):
        """divmod(self, other): The pair (self // other, self % other).

        Sometimes this can be computed faster than the pair of
        operations.
        """
        rudisha (self // other, self % other)

    eleza __rdivmod__(self, other):
        """divmod(other, self): The pair (self // other, self % other).

        Sometimes this can be computed faster than the pair of
        operations.
        """
        rudisha (other // self, other % self)

    @abstractmethod
    eleza __floordiv__(self, other):
        """self // other: The floor() of self/other."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rfloordiv__(self, other):
        """other // self: The floor() of other/self."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __mod__(self, other):
        """self % other"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rmod__(self, other):
        """other % self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __lt__(self, other):
        """self < other

        < on Reals defines a total ordering, except perhaps kila NaN."""
         ashiria NotImplementedError

    @abstractmethod
    eleza __le__(self, other):
        """self <= other"""
         ashiria NotImplementedError

    # Concrete implementations of Complex abstract methods.
    eleza __complex__(self):
        """complex(self) == complex(float(self), 0)"""
        rudisha complex(float(self))

    @property
    eleza real(self):
        """Real numbers are their real component."""
        rudisha +self

    @property
    eleza imag(self):
        """Real numbers have no imaginary component."""
        rudisha 0

    eleza conjugate(self):
        """Conjugate ni a no-op kila Reals."""
        rudisha +self

Real.register(float)


kundi Rational(Real):
    """.numerator na .denominator should be kwenye lowest terms."""

    __slots__ = ()

    @property
    @abstractmethod
    eleza numerator(self):
         ashiria NotImplementedError

    @property
    @abstractmethod
    eleza denominator(self):
         ashiria NotImplementedError

    # Concrete implementation of Real's conversion to float.
    eleza __float__(self):
        """float(self) = self.numerator / self.denominator

        It's important that this conversion use the integer's "true"
        division rather than casting one side to float before dividing
        so that ratios of huge integers convert without overflowing.

        """
        rudisha self.numerator / self.denominator


kundi Integral(Rational):
    """Integral adds a conversion to int na the bit-string operations."""

    __slots__ = ()

    @abstractmethod
    eleza __int__(self):
        """int(self)"""
         ashiria NotImplementedError

    eleza __index__(self):
        """Called whenever an index ni needed, such as kwenye slicing"""
        rudisha int(self)

    @abstractmethod
    eleza __pow__(self, exponent, modulus=Tupu):
        """self ** exponent % modulus, but maybe faster.

        Accept the modulus argument ikiwa you want to support the
        3-argument version of pow(). Raise a TypeError ikiwa exponent < 0
        ama any argument isn't Integral. Otherwise, just implement the
        2-argument version described kwenye Complex.
        """
         ashiria NotImplementedError

    @abstractmethod
    eleza __lshift__(self, other):
        """self << other"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rlshift__(self, other):
        """other << self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rshift__(self, other):
        """self >> other"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rrshift__(self, other):
        """other >> self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __and__(self, other):
        """self & other"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rand__(self, other):
        """other & self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __xor__(self, other):
        """self ^ other"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __rxor__(self, other):
        """other ^ self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __or__(self, other):
        """self | other"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __ror__(self, other):
        """other | self"""
         ashiria NotImplementedError

    @abstractmethod
    eleza __invert__(self):
        """~self"""
         ashiria NotImplementedError

    # Concrete implementations of Rational na Real abstract methods.
    eleza __float__(self):
        """float(self) == float(int(self))"""
        rudisha float(int(self))

    @property
    eleza numerator(self):
        """Integers are their own numerators."""
        rudisha +self

    @property
    eleza denominator(self):
        """Integers have a denominator of 1."""
        rudisha 1

Integral.register(int)
