agiza math
agiza unittest

kundi PowTest(unittest.TestCase):

    eleza powtest(self, type):
        ikiwa type != float:
            kila i kwenye range(-1000, 1000):
                self.assertEqual(pow(type(i), 0), 1)
                self.assertEqual(pow(type(i), 1), type(i))
                self.assertEqual(pow(type(0), 1), type(0))
                self.assertEqual(pow(type(1), 1), type(1))

            kila i kwenye range(-100, 100):
                self.assertEqual(pow(type(i), 3), i*i*i)

            pow2 = 1
            kila i kwenye range(0, 31):
                self.assertEqual(pow(2, i), pow2)
                ikiwa i != 30 : pow2 = pow2*2

            kila othertype kwenye (int,):
                kila i kwenye list(range(-10, 0)) + list(range(1, 10)):
                    ii = type(i)
                    kila j kwenye range(1, 11):
                        jj = -othertype(j)
                        pow(ii, jj)

        kila othertype kwenye int, float:
            kila i kwenye range(1, 100):
                zero = type(0)
                exp = -othertype(i/10.0)
                ikiwa exp == 0:
                    endelea
                self.assertRaises(ZeroDivisionError, pow, zero, exp)

        il, ih = -20, 20
        jl, jh = -5,   5
        kl, kh = -10, 10
        asseq = self.assertEqual
        ikiwa type == float:
            il = 1
            asseq = self.assertAlmostEqual
        elikiwa type == int:
            jl = 0
        elikiwa type == int:
            jl, jh = 0, 15
        kila i kwenye range(il, ih+1):
            kila j kwenye range(jl, jh+1):
                kila k kwenye range(kl, kh+1):
                    ikiwa k != 0:
                        ikiwa type == float ama j < 0:
                            self.assertRaises(TypeError, pow, type(i), j, k)
                            endelea
                        asseq(
                            pow(type(i),j,k),
                            pow(type(i),j)% type(k)
                        )

    eleza test_powint(self):
        self.powtest(int)

    eleza test_powfloat(self):
        self.powtest(float)

    eleza test_other(self):
        # Other tests-- sio very systematic
        self.assertEqual(pow(3,3) % 8, pow(3,3,8))
        self.assertEqual(pow(3,3) % -8, pow(3,3,-8))
        self.assertEqual(pow(3,2) % -2, pow(3,2,-2))
        self.assertEqual(pow(-3,3) % 8, pow(-3,3,8))
        self.assertEqual(pow(-3,3) % -8, pow(-3,3,-8))
        self.assertEqual(pow(5,2) % -8, pow(5,2,-8))

        self.assertEqual(pow(3,3) % 8, pow(3,3,8))
        self.assertEqual(pow(3,3) % -8, pow(3,3,-8))
        self.assertEqual(pow(3,2) % -2, pow(3,2,-2))
        self.assertEqual(pow(-3,3) % 8, pow(-3,3,8))
        self.assertEqual(pow(-3,3) % -8, pow(-3,3,-8))
        self.assertEqual(pow(5,2) % -8, pow(5,2,-8))

        kila i kwenye range(-10, 11):
            kila j kwenye range(0, 6):
                kila k kwenye range(-7, 11):
                    ikiwa j >= 0 na k != 0:
                        self.assertEqual(
                            pow(i,j) % k,
                            pow(i,j,k)
                        )
                    ikiwa j >= 0 na k != 0:
                        self.assertEqual(
                            pow(int(i),j) % k,
                            pow(int(i),j,k)
                        )

    eleza test_bug643260(self):
        kundi TestRpow:
            eleza __rpow__(self, other):
                rudisha Tupu
        Tupu ** TestRpow() # Won't fail when __rpow__ invoked.  SF bug #643260.

    eleza test_bug705231(self):
        # -1.0 ashiriad to an integer should never blow up.  It did ikiwa the
        # platform pow() was buggy, na Python didn't worm around it.
        eq = self.assertEqual
        a = -1.0
        # The next two tests can still fail ikiwa the platform floor()
        # function doesn't treat all large inputs kama integers
        # test_math should also fail ikiwa that ni happening
        eq(pow(a, 1.23e167), 1.0)
        eq(pow(a, -1.23e167), 1.0)
        kila b kwenye range(-10, 11):
            eq(pow(a, float(b)), b & 1 na -1.0 ama 1.0)
        kila n kwenye range(0, 100):
            fiveto = float(5 ** n)
            # For small n, fiveto will be odd.  Eventually we run out of
            # mantissa bits, though, na thereafer fiveto will be even.
            expected = fiveto % 2.0 na -1.0 ama 1.0
            eq(pow(a, fiveto), expected)
            eq(pow(a, -fiveto), expected)
        eq(expected, 1.0)   # else we didn't push fiveto to evenness

    eleza test_negative_exponent(self):
        kila a kwenye range(-50, 50):
            kila m kwenye range(-50, 50):
                with self.subTest(a=a, m=m):
                    ikiwa m != 0 na math.gcd(a, m) == 1:
                        # Exponent -1 should give an inverse, with the
                        # same sign kama m.
                        inv = pow(a, -1, m)
                        self.assertEqual(inv, inv % m)
                        self.assertEqual((inv * a - 1) % m, 0)

                        # Larger exponents
                        self.assertEqual(pow(a, -2, m), pow(inv, 2, m))
                        self.assertEqual(pow(a, -3, m), pow(inv, 3, m))
                        self.assertEqual(pow(a, -1001, m), pow(inv, 1001, m))

                    isipokua:
                        with self.assertRaises(ValueError):
                            pow(a, -1, m)
                        with self.assertRaises(ValueError):
                            pow(a, -2, m)
                        with self.assertRaises(ValueError):
                            pow(a, -1001, m)


ikiwa __name__ == "__main__":
    unittest.main()
