kutoka __future__ agiza nested_scopes
kutoka __future__ agiza division

agiza unittest

x = 2
eleza nester():
    x = 3
    eleza inner():
        rudisha x
    rudisha inner()


kundi TestFuture(unittest.TestCase):

    eleza test_floor_div_operator(self):
        self.assertEqual(7 // 2, 3)

    eleza test_true_div_as_default(self):
        self.assertAlmostEqual(7 / 2, 3.5)

    eleza test_nested_scopes(self):
        self.assertEqual(nester(), 3)

ikiwa __name__ == "__main__":
    unittest.main()
