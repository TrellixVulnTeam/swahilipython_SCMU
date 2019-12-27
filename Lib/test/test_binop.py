"""Tests for binary operators on subtypes of built-in types."""

agiza unittest
kutoka operator agiza eq, le, ne
kutoka abc agiza ABCMeta

eleza gcd(a, b):
    """Greatest common divisor using Euclid's algorithm."""
    while a:
        a, b = b%a, a
    rudisha b

eleza isint(x):
    """Test whether an object is an instance of int."""
    rudisha isinstance(x, int)

eleza isnum(x):
    """Test whether an object is an instance of a built-in numeric type."""
    for T in int, float, complex:
        ikiwa isinstance(x, T):
            rudisha 1
    rudisha 0

eleza isRat(x):
    """Test whether an object is an instance of the Rat class."""
    rudisha isinstance(x, Rat)

kundi Rat(object):

    """Rational number implemented as a normalized pair of ints."""

    __slots__ = ['_Rat__num', '_Rat__den']

    eleza __init__(self, num=0, den=1):
        """Constructor: Rat([num[, den]]).

        The arguments must be ints, and default to (0, 1)."""
        ikiwa not isint(num):
            raise TypeError("Rat numerator must be int (%r)" % num)
        ikiwa not isint(den):
            raise TypeError("Rat denominator must be int (%r)" % den)
        # But the zero is always on
        ikiwa den == 0:
            raise ZeroDivisionError("zero denominator")
        g = gcd(den, num)
        self.__num = int(num//g)
        self.__den = int(den//g)

    eleza _get_num(self):
        """Accessor function for read-only 'num' attribute of Rat."""
        rudisha self.__num
    num = property(_get_num, None)

    eleza _get_den(self):
        """Accessor function for read-only 'den' attribute of Rat."""
        rudisha self.__den
    den = property(_get_den, None)

    eleza __repr__(self):
        """Convert a Rat to a string resembling a Rat constructor call."""
        rudisha "Rat(%d, %d)" % (self.__num, self.__den)

    eleza __str__(self):
        """Convert a Rat to a string resembling a decimal numeric value."""
        rudisha str(float(self))

    eleza __float__(self):
        """Convert a Rat to a float."""
        rudisha self.__num*1.0/self.__den

    eleza __int__(self):
        """Convert a Rat to an int; self.den must be 1."""
        ikiwa self.__den == 1:
            try:
                rudisha int(self.__num)
            except OverflowError:
                raise OverflowError("%s too large to convert to int" %
                                      repr(self))
        raise ValueError("can't convert %s to int" % repr(self))

    eleza __add__(self, other):
        """Add two Rats, or a Rat and a number."""
        ikiwa isint(other):
            other = Rat(other)
        ikiwa isRat(other):
            rudisha Rat(self.__num*other.__den + other.__num*self.__den,
                       self.__den*other.__den)
        ikiwa isnum(other):
            rudisha float(self) + other
        rudisha NotImplemented

    __radd__ = __add__

    eleza __sub__(self, other):
        """Subtract two Rats, or a Rat and a number."""
        ikiwa isint(other):
            other = Rat(other)
        ikiwa isRat(other):
            rudisha Rat(self.__num*other.__den - other.__num*self.__den,
                       self.__den*other.__den)
        ikiwa isnum(other):
            rudisha float(self) - other
        rudisha NotImplemented

    eleza __rsub__(self, other):
        """Subtract two Rats, or a Rat and a number (reversed args)."""
        ikiwa isint(other):
            other = Rat(other)
        ikiwa isRat(other):
            rudisha Rat(other.__num*self.__den - self.__num*other.__den,
                       self.__den*other.__den)
        ikiwa isnum(other):
            rudisha other - float(self)
        rudisha NotImplemented

    eleza __mul__(self, other):
        """Multiply two Rats, or a Rat and a number."""
        ikiwa isRat(other):
            rudisha Rat(self.__num*other.__num, self.__den*other.__den)
        ikiwa isint(other):
            rudisha Rat(self.__num*other, self.__den)
        ikiwa isnum(other):
            rudisha float(self)*other
        rudisha NotImplemented

    __rmul__ = __mul__

    eleza __truediv__(self, other):
        """Divide two Rats, or a Rat and a number."""
        ikiwa isRat(other):
            rudisha Rat(self.__num*other.__den, self.__den*other.__num)
        ikiwa isint(other):
            rudisha Rat(self.__num, self.__den*other)
        ikiwa isnum(other):
            rudisha float(self) / other
        rudisha NotImplemented

    eleza __rtruediv__(self, other):
        """Divide two Rats, or a Rat and a number (reversed args)."""
        ikiwa isRat(other):
            rudisha Rat(other.__num*self.__den, other.__den*self.__num)
        ikiwa isint(other):
            rudisha Rat(other*self.__den, self.__num)
        ikiwa isnum(other):
            rudisha other / float(self)
        rudisha NotImplemented

    eleza __floordiv__(self, other):
        """Divide two Rats, returning the floored result."""
        ikiwa isint(other):
            other = Rat(other)
        elikiwa not isRat(other):
            rudisha NotImplemented
        x = self/other
        rudisha x.__num // x.__den

    eleza __rfloordiv__(self, other):
        """Divide two Rats, returning the floored result (reversed args)."""
        x = other/self
        rudisha x.__num // x.__den

    eleza __divmod__(self, other):
        """Divide two Rats, returning quotient and remainder."""
        ikiwa isint(other):
            other = Rat(other)
        elikiwa not isRat(other):
            rudisha NotImplemented
        x = self//other
        rudisha (x, self - other * x)

    eleza __rdivmod__(self, other):
        """Divide two Rats, returning quotient and remainder (reversed args)."""
        ikiwa isint(other):
            other = Rat(other)
        elikiwa not isRat(other):
            rudisha NotImplemented
        rudisha divmod(other, self)

    eleza __mod__(self, other):
        """Take one Rat modulo another."""
        rudisha divmod(self, other)[1]

    eleza __rmod__(self, other):
        """Take one Rat modulo another (reversed args)."""
        rudisha divmod(other, self)[1]

    eleza __eq__(self, other):
        """Compare two Rats for equality."""
        ikiwa isint(other):
            rudisha self.__den == 1 and self.__num == other
        ikiwa isRat(other):
            rudisha self.__num == other.__num and self.__den == other.__den
        ikiwa isnum(other):
            rudisha float(self) == other
        rudisha NotImplemented

kundi RatTestCase(unittest.TestCase):
    """Unit tests for Rat kundi and its support utilities."""

    eleza test_gcd(self):
        self.assertEqual(gcd(10, 12), 2)
        self.assertEqual(gcd(10, 15), 5)
        self.assertEqual(gcd(10, 11), 1)
        self.assertEqual(gcd(100, 15), 5)
        self.assertEqual(gcd(-10, 2), -2)
        self.assertEqual(gcd(10, -2), 2)
        self.assertEqual(gcd(-10, -2), -2)
        for i in range(1, 20):
            for j in range(1, 20):
                self.assertTrue(gcd(i, j) > 0)
                self.assertTrue(gcd(-i, j) < 0)
                self.assertTrue(gcd(i, -j) > 0)
                self.assertTrue(gcd(-i, -j) < 0)

    eleza test_constructor(self):
        a = Rat(10, 15)
        self.assertEqual(a.num, 2)
        self.assertEqual(a.den, 3)
        a = Rat(10, -15)
        self.assertEqual(a.num, -2)
        self.assertEqual(a.den, 3)
        a = Rat(-10, 15)
        self.assertEqual(a.num, -2)
        self.assertEqual(a.den, 3)
        a = Rat(-10, -15)
        self.assertEqual(a.num, 2)
        self.assertEqual(a.den, 3)
        a = Rat(7)
        self.assertEqual(a.num, 7)
        self.assertEqual(a.den, 1)
        try:
            a = Rat(1, 0)
        except ZeroDivisionError:
            pass
        else:
            self.fail("Rat(1, 0) didn't raise ZeroDivisionError")
        for bad in "0", 0.0, 0j, (), [], {}, None, Rat, unittest:
            try:
                a = Rat(bad)
            except TypeError:
                pass
            else:
                self.fail("Rat(%r) didn't raise TypeError" % bad)
            try:
                a = Rat(1, bad)
            except TypeError:
                pass
            else:
                self.fail("Rat(1, %r) didn't raise TypeError" % bad)

    eleza test_add(self):
        self.assertEqual(Rat(2, 3) + Rat(1, 3), 1)
        self.assertEqual(Rat(2, 3) + 1, Rat(5, 3))
        self.assertEqual(1 + Rat(2, 3), Rat(5, 3))
        self.assertEqual(1.0 + Rat(1, 2), 1.5)
        self.assertEqual(Rat(1, 2) + 1.0, 1.5)

    eleza test_sub(self):
        self.assertEqual(Rat(7, 2) - Rat(7, 5), Rat(21, 10))
        self.assertEqual(Rat(7, 5) - 1, Rat(2, 5))
        self.assertEqual(1 - Rat(3, 5), Rat(2, 5))
        self.assertEqual(Rat(3, 2) - 1.0, 0.5)
        self.assertEqual(1.0 - Rat(1, 2), 0.5)

    eleza test_mul(self):
        self.assertEqual(Rat(2, 3) * Rat(5, 7), Rat(10, 21))
        self.assertEqual(Rat(10, 3) * 3, 10)
        self.assertEqual(3 * Rat(10, 3), 10)
        self.assertEqual(Rat(10, 5) * 0.5, 1.0)
        self.assertEqual(0.5 * Rat(10, 5), 1.0)

    eleza test_div(self):
        self.assertEqual(Rat(10, 3) / Rat(5, 7), Rat(14, 3))
        self.assertEqual(Rat(10, 3) / 3, Rat(10, 9))
        self.assertEqual(2 / Rat(5), Rat(2, 5))
        self.assertEqual(3.0 * Rat(1, 2), 1.5)
        self.assertEqual(Rat(1, 2) * 3.0, 1.5)

    eleza test_floordiv(self):
        self.assertEqual(Rat(10) // Rat(4), 2)
        self.assertEqual(Rat(10, 3) // Rat(4, 3), 2)
        self.assertEqual(Rat(10) // 4, 2)
        self.assertEqual(10 // Rat(4), 2)

    eleza test_eq(self):
        self.assertEqual(Rat(10), Rat(20, 2))
        self.assertEqual(Rat(10), 10)
        self.assertEqual(10, Rat(10))
        self.assertEqual(Rat(10), 10.0)
        self.assertEqual(10.0, Rat(10))

    eleza test_true_div(self):
        self.assertEqual(Rat(10, 3) / Rat(5, 7), Rat(14, 3))
        self.assertEqual(Rat(10, 3) / 3, Rat(10, 9))
        self.assertEqual(2 / Rat(5), Rat(2, 5))
        self.assertEqual(3.0 * Rat(1, 2), 1.5)
        self.assertEqual(Rat(1, 2) * 3.0, 1.5)
        self.assertEqual(eval('1/2'), 0.5)

    # XXX Ran out of steam; TO DO: divmod, div, future division


kundi OperationLogger:
    """Base kundi for classes with operation logging."""
    eleza __init__(self, logger):
        self.logger = logger
    eleza log_operation(self, *args):
        self.logger(*args)

eleza op_sequence(op, *classes):
    """Return the sequence of operations that results kutoka applying
    the operation `op` to instances of the given classes."""
    log = []
    instances = []
    for c in classes:
        instances.append(c(log.append))

    try:
        op(*instances)
    except TypeError:
        pass
    rudisha log

kundi A(OperationLogger):
    eleza __eq__(self, other):
        self.log_operation('A.__eq__')
        rudisha NotImplemented
    eleza __le__(self, other):
        self.log_operation('A.__le__')
        rudisha NotImplemented
    eleza __ge__(self, other):
        self.log_operation('A.__ge__')
        rudisha NotImplemented

kundi B(OperationLogger, metaclass=ABCMeta):
    eleza __eq__(self, other):
        self.log_operation('B.__eq__')
        rudisha NotImplemented
    eleza __le__(self, other):
        self.log_operation('B.__le__')
        rudisha NotImplemented
    eleza __ge__(self, other):
        self.log_operation('B.__ge__')
        rudisha NotImplemented

kundi C(B):
    eleza __eq__(self, other):
        self.log_operation('C.__eq__')
        rudisha NotImplemented
    eleza __le__(self, other):
        self.log_operation('C.__le__')
        rudisha NotImplemented
    eleza __ge__(self, other):
        self.log_operation('C.__ge__')
        rudisha NotImplemented

kundi V(OperationLogger):
    """Virtual subkundi of B"""
    eleza __eq__(self, other):
        self.log_operation('V.__eq__')
        rudisha NotImplemented
    eleza __le__(self, other):
        self.log_operation('V.__le__')
        rudisha NotImplemented
    eleza __ge__(self, other):
        self.log_operation('V.__ge__')
        rudisha NotImplemented
B.register(V)


kundi OperationOrderTests(unittest.TestCase):
    eleza test_comparison_orders(self):
        self.assertEqual(op_sequence(eq, A, A), ['A.__eq__', 'A.__eq__'])
        self.assertEqual(op_sequence(eq, A, B), ['A.__eq__', 'B.__eq__'])
        self.assertEqual(op_sequence(eq, B, A), ['B.__eq__', 'A.__eq__'])
        # C is a subkundi of B, so C.__eq__ is called first
        self.assertEqual(op_sequence(eq, B, C), ['C.__eq__', 'B.__eq__'])
        self.assertEqual(op_sequence(eq, C, B), ['C.__eq__', 'B.__eq__'])

        self.assertEqual(op_sequence(le, A, A), ['A.__le__', 'A.__ge__'])
        self.assertEqual(op_sequence(le, A, B), ['A.__le__', 'B.__ge__'])
        self.assertEqual(op_sequence(le, B, A), ['B.__le__', 'A.__ge__'])
        self.assertEqual(op_sequence(le, B, C), ['C.__ge__', 'B.__le__'])
        self.assertEqual(op_sequence(le, C, B), ['C.__le__', 'B.__ge__'])

        self.assertTrue(issubclass(V, B))
        self.assertEqual(op_sequence(eq, B, V), ['B.__eq__', 'V.__eq__'])
        self.assertEqual(op_sequence(le, B, V), ['B.__le__', 'V.__ge__'])

kundi SupEq(object):
    """Class that can test equality"""
    eleza __eq__(self, other):
        rudisha True

kundi S(SupEq):
    """Subkundi of SupEq that should fail"""
    __eq__ = None

kundi F(object):
    """Independent kundi that should fall back"""

kundi X(object):
    """Independent kundi that should fail"""
    __eq__ = None

kundi SN(SupEq):
    """Subkundi of SupEq that can test equality, but not non-equality"""
    __ne__ = None

kundi XN:
    """Independent kundi that can test equality, but not non-equality"""
    eleza __eq__(self, other):
        rudisha True
    __ne__ = None

kundi FallbackBlockingTests(unittest.TestCase):
    """Unit tests for None method blocking"""

    eleza test_fallback_rmethod_blocking(self):
        e, f, s, x = SupEq(), F(), S(), X()
        self.assertEqual(e, e)
        self.assertEqual(e, f)
        self.assertEqual(f, e)
        # left operand is checked first
        self.assertEqual(e, x)
        self.assertRaises(TypeError, eq, x, e)
        # S is a subclass, so it's always checked first
        self.assertRaises(TypeError, eq, e, s)
        self.assertRaises(TypeError, eq, s, e)

    eleza test_fallback_ne_blocking(self):
        e, sn, xn = SupEq(), SN(), XN()
        self.assertFalse(e != e)
        self.assertRaises(TypeError, ne, e, sn)
        self.assertRaises(TypeError, ne, sn, e)
        self.assertFalse(e != xn)
        self.assertRaises(TypeError, ne, xn, e)

ikiwa __name__ == "__main__":
    unittest.main()
