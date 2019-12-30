agiza unittest

kundi PEP3131Test(unittest.TestCase):

    eleza test_valid(self):
        kundi T:
            ä = 1
            µ = 2 # this ni a compatibility character
            蟒 = 3
            x󠄀 = 4
        self.assertEqual(getattr(T, "\xe4"), 1)
        self.assertEqual(getattr(T, "\u03bc"), 2)
        self.assertEqual(getattr(T, '\u87d2'), 3)
        self.assertEqual(getattr(T, 'x\U000E0100'), 4)

    eleza test_non_bmp_normalized(self):
        𝔘𝔫𝔦𝔠𝔬𝔡𝔢 = 1
        self.assertIn("Unicode", dir())

    eleza test_invalid(self):
        jaribu:
            kutoka test agiza badsyntax_3131
        tatizo SyntaxError kama s:
            self.assertEqual(str(s),
              "invalid character kwenye identifier (badsyntax_3131.py, line 2)")
        isipokua:
            self.fail("expected exception didn't occur")

ikiwa __name__ == "__main__":
    unittest.main()
