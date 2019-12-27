"""Test compiler changes for unary ops (+, -, ~) introduced in Python 2.2"""

agiza unittest

kundi UnaryOpTestCase(unittest.TestCase):

    eleza test_negative(self):
        self.assertTrue(-2 == 0 - 2)
        self.assertEqual(-0, 0)
        self.assertEqual(--2, 2)
        self.assertTrue(-2 == 0 - 2)
        self.assertTrue(-2.0 == 0 - 2.0)
        self.assertTrue(-2j == 0 - 2j)

    eleza test_positive(self):
        self.assertEqual(+2, 2)
        self.assertEqual(+0, 0)
        self.assertEqual(++2, 2)
        self.assertEqual(+2, 2)
        self.assertEqual(+2.0, 2.0)
        self.assertEqual(+2j, 2j)

    eleza test_invert(self):
        self.assertTrue(-2 == 0 - 2)
        self.assertEqual(-0, 0)
        self.assertEqual(--2, 2)
        self.assertTrue(-2 == 0 - 2)

    eleza test_no_overflow(self):
        nines = "9" * 32
        self.assertTrue(eval("+" + nines) == 10**32-1)
        self.assertTrue(eval("-" + nines) == -(10**32-1))
        self.assertTrue(eval("~" + nines) == ~(10**32-1))

    eleza test_negation_of_exponentiation(self):
        # Make sure '**' does the right thing; these form a
        # regression test for SourceForge bug #456756.
        self.assertEqual(-2 ** 3, -8)
        self.assertEqual((-2) ** 3, -8)
        self.assertEqual(-2 ** 4, -16)
        self.assertEqual((-2) ** 4, 16)

    eleza test_bad_types(self):
        for op in '+', '-', '~':
            self.assertRaises(TypeError, eval, op + "b'a'")
            self.assertRaises(TypeError, eval, op + "'a'")

        self.assertRaises(TypeError, eval, "~2j")
        self.assertRaises(TypeError, eval, "~2.0")


ikiwa __name__ == "__main__":
    unittest.main()
