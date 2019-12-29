# test interactions between int, float, Decimal na Fraction

agiza unittest
agiza random
agiza math
agiza sys
agiza operator

kutoka decimal agiza Decimal kama D
kutoka fractions agiza Fraction kama F

# Constants related to the hash implementation;  hash(x) ni based
# on the reduction of x modulo the prime _PyHASH_MODULUS.
_PyHASH_MODULUS = sys.hash_info.modulus
_PyHASH_INF = sys.hash_info.inf

kundi HashTest(unittest.TestCase):
    eleza check_equal_hash(self, x, y):
        # check both that x na y are equal na that their hashes are equal
        self.assertEqual(hash(x), hash(y),
                         "got different hashes kila {!r} na {!r}".format(x, y))
        self.assertEqual(x, y)

    eleza test_bools(self):
        self.check_equal_hash(Uongo, 0)
        self.check_equal_hash(Kweli, 1)

    eleza test_integers(self):
        # check that equal values hash equal

        # exact integers
        kila i kwenye range(-1000, 1000):
            self.check_equal_hash(i, float(i))
            self.check_equal_hash(i, D(i))
            self.check_equal_hash(i, F(i))

        # the current hash ni based on reduction modulo 2**n-1 kila some
        # n, so pay special attention to numbers of the form 2**n na 2**n-1.
        kila i kwenye range(100):
            n = 2**i - 1
            ikiwa n == int(float(n)):
                self.check_equal_hash(n, float(n))
                self.check_equal_hash(-n, -float(n))
            self.check_equal_hash(n, D(n))
            self.check_equal_hash(n, F(n))
            self.check_equal_hash(-n, D(-n))
            self.check_equal_hash(-n, F(-n))

            n = 2**i
            self.check_equal_hash(n, float(n))
            self.check_equal_hash(-n, -float(n))
            self.check_equal_hash(n, D(n))
            self.check_equal_hash(n, F(n))
            self.check_equal_hash(-n, D(-n))
            self.check_equal_hash(-n, F(-n))

        # random values of various sizes
        kila _ kwenye range(1000):
            e = random.randrange(300)
            n = random.randrange(-10**e, 10**e)
            self.check_equal_hash(n, D(n))
            self.check_equal_hash(n, F(n))
            ikiwa n == int(float(n)):
                self.check_equal_hash(n, float(n))

    eleza test_binary_floats(self):
        # check that floats hash equal to corresponding Fractions na Decimals

        # floats that are distinct but numerically equal should hash the same
        self.check_equal_hash(0.0, -0.0)

        # zeros
        self.check_equal_hash(0.0, D(0))
        self.check_equal_hash(-0.0, D(0))
        self.check_equal_hash(-0.0, D('-0.0'))
        self.check_equal_hash(0.0, F(0))

        # infinities na nans
        self.check_equal_hash(float('inf'), D('inf'))
        self.check_equal_hash(float('-inf'), D('-inf'))

        kila _ kwenye range(1000):
            x = random.random() * math.exp(random.random()*200.0 - 100.0)
            self.check_equal_hash(x, D.kutoka_float(x))
            self.check_equal_hash(x, F.kutoka_float(x))

    eleza test_complex(self):
        # complex numbers ukijumuisha zero imaginary part should hash equal to
        # the corresponding float

        test_values = [0.0, -0.0, 1.0, -1.0, 0.40625, -5136.5,
                       float('inf'), float('-inf')]

        kila zero kwenye -0.0, 0.0:
            kila value kwenye test_values:
                self.check_equal_hash(value, complex(value, zero))

    eleza test_decimals(self):
        # check that Decimal instances that have different representations
        # but equal values give the same hash
        zeros = ['0', '-0', '0.0', '-0.0e10', '000e-10']
        kila zero kwenye zeros:
            self.check_equal_hash(D(zero), D(0))

        self.check_equal_hash(D('1.00'), D(1))
        self.check_equal_hash(D('1.00000'), D(1))
        self.check_equal_hash(D('-1.00'), D(-1))
        self.check_equal_hash(D('-1.00000'), D(-1))
        self.check_equal_hash(D('123e2'), D(12300))
        self.check_equal_hash(D('1230e1'), D(12300))
        self.check_equal_hash(D('12300'), D(12300))
        self.check_equal_hash(D('12300.0'), D(12300))
        self.check_equal_hash(D('12300.00'), D(12300))
        self.check_equal_hash(D('12300.000'), D(12300))

    eleza test_fractions(self):
        # check special case kila fractions where either the numerator
        # ama the denominator ni a multiple of _PyHASH_MODULUS
        self.assertEqual(hash(F(1, _PyHASH_MODULUS)), _PyHASH_INF)
        self.assertEqual(hash(F(-1, 3*_PyHASH_MODULUS)), -_PyHASH_INF)
        self.assertEqual(hash(F(7*_PyHASH_MODULUS, 1)), 0)
        self.assertEqual(hash(F(-_PyHASH_MODULUS, 1)), 0)

    eleza test_hash_normalization(self):
        # Test kila a bug encountered wakati changing long_hash.
        #
        # Given objects x na y, it should be possible kila y's
        # __hash__ method to rudisha hash(x) kwenye order to ensure that
        # hash(x) == hash(y).  But hash(x) ni sio exactly equal to the
        # result of x.__hash__(): there's some internal normalization
        # to make sure that the result fits kwenye a C long, na ni not
        # equal to the invalid hash value -1.  This internal
        # normalization must therefore sio change the result of
        # hash(x) kila any x.

        kundi HalibutProxy:
            eleza __hash__(self):
                rudisha hash('halibut')
            eleza __eq__(self, other):
                rudisha other == 'halibut'

        x = {'halibut', HalibutProxy()}
        self.assertEqual(len(x), 1)

kundi ComparisonTest(unittest.TestCase):
    eleza test_mixed_comparisons(self):

        # ordered list of distinct test values of various types:
        # int, float, Fraction, Decimal
        test_values = [
            float('-inf'),
            D('-1e425000000'),
            -1e308,
            F(-22, 7),
            -3.14,
            -2,
            0.0,
            1e-320,
            Kweli,
            F('1.2'),
            D('1.3'),
            float('1.4'),
            F(275807, 195025),
            D('1.414213562373095048801688724'),
            F(114243, 80782),
            F(473596569, 84615),
            7e200,
            D('infinity'),
            ]
        kila i, first kwenye enumerate(test_values):
            kila second kwenye test_values[i+1:]:
                self.assertLess(first, second)
                self.assertLessEqual(first, second)
                self.assertGreater(second, first)
                self.assertGreaterEqual(second, first)

    eleza test_complex(self):
        # comparisons ukijumuisha complex are special:  equality na inequality
        # comparisons should always succeed, but order comparisons should
        # ashiria TypeError.
        z = 1.0 + 0j
        w = -3.14 + 2.7j

        kila v kwenye 1, 1.0, F(1), D(1), complex(1):
            self.assertEqual(z, v)
            self.assertEqual(v, z)

        kila v kwenye 2, 2.0, F(2), D(2), complex(2):
            self.assertNotEqual(z, v)
            self.assertNotEqual(v, z)
            self.assertNotEqual(w, v)
            self.assertNotEqual(v, w)

        kila v kwenye (1, 1.0, F(1), D(1), complex(1),
                  2, 2.0, F(2), D(2), complex(2), w):
            kila op kwenye operator.le, operator.lt, operator.ge, operator.gt:
                self.assertRaises(TypeError, op, z, v)
                self.assertRaises(TypeError, op, v, z)


ikiwa __name__ == '__main__':
    unittest.main()
