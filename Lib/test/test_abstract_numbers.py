"""Unit tests kila numbers.py."""

agiza math
agiza operator
agiza unittest
kutoka numbers agiza Complex, Real, Rational, Integral

kundi TestNumbers(unittest.TestCase):
    eleza test_int(self):
        self.assertKweli(issubclass(int, Integral))
        self.assertKweli(issubclass(int, Complex))

        self.assertEqual(7, int(7).real)
        self.assertEqual(0, int(7).imag)
        self.assertEqual(7, int(7).conjugate())
        self.assertEqual(-7, int(-7).conjugate())
        self.assertEqual(7, int(7).numerator)
        self.assertEqual(1, int(7).denominator)

    eleza test_float(self):
        self.assertUongo(issubclass(float, Rational))
        self.assertKweli(issubclass(float, Real))

        self.assertEqual(7.3, float(7.3).real)
        self.assertEqual(0, float(7.3).imag)
        self.assertEqual(7.3, float(7.3).conjugate())
        self.assertEqual(-7.3, float(-7.3).conjugate())

    eleza test_complex(self):
        self.assertUongo(issubclass(complex, Real))
        self.assertKweli(issubclass(complex, Complex))

        c1, c2 = complex(3, 2), complex(4,1)
        # XXX: This ni sio ideal, but see the comment kwenye math_trunc().
        self.assertRaises(TypeError, math.trunc, c1)
        self.assertRaises(TypeError, operator.mod, c1, c2)
        self.assertRaises(TypeError, divmod, c1, c2)
        self.assertRaises(TypeError, operator.floordiv, c1, c2)
        self.assertRaises(TypeError, float, c1)
        self.assertRaises(TypeError, int, c1)


ikiwa __name__ == "__main__":
    unittest.main()
