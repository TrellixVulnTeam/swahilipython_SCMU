agiza unittest

# For scope testing.
g = "Global variable"


kundi DictComprehensionTest(unittest.TestCase):

    eleza test_basics(self):
        expected = {0: 10, 1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17,
                    8: 18, 9: 19}
        actual = {k: k + 10 kila k kwenye range(10)}
        self.assertEqual(actual, expected)

        expected = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}
        actual = {k: v kila k kwenye range(10) kila v kwenye range(10) ikiwa k == v}
        self.assertEqual(actual, expected)

    eleza test_scope_isolation(self):
        k = "Local Variable"

        expected = {0: Tupu, 1: Tupu, 2: Tupu, 3: Tupu, 4: Tupu, 5: Tupu,
                    6: Tupu, 7: Tupu, 8: Tupu, 9: Tupu}
        actual = {k: Tupu kila k kwenye range(10)}
        self.assertEqual(actual, expected)
        self.assertEqual(k, "Local Variable")

        expected = {9: 1, 18: 2, 19: 2, 27: 3, 28: 3, 29: 3, 36: 4, 37: 4,
                    38: 4, 39: 4, 45: 5, 46: 5, 47: 5, 48: 5, 49: 5, 54: 6,
                    55: 6, 56: 6, 57: 6, 58: 6, 59: 6, 63: 7, 64: 7, 65: 7,
                    66: 7, 67: 7, 68: 7, 69: 7, 72: 8, 73: 8, 74: 8, 75: 8,
                    76: 8, 77: 8, 78: 8, 79: 8, 81: 9, 82: 9, 83: 9, 84: 9,
                    85: 9, 86: 9, 87: 9, 88: 9, 89: 9}
        actual = {k: v kila v kwenye range(10) kila k kwenye range(v * 9, v * 10)}
        self.assertEqual(k, "Local Variable")
        self.assertEqual(actual, expected)

    eleza test_scope_isolation_kutoka_global(self):
        expected = {0: Tupu, 1: Tupu, 2: Tupu, 3: Tupu, 4: Tupu, 5: Tupu,
                    6: Tupu, 7: Tupu, 8: Tupu, 9: Tupu}
        actual = {g: Tupu kila g kwenye range(10)}
        self.assertEqual(actual, expected)
        self.assertEqual(g, "Global variable")

        expected = {9: 1, 18: 2, 19: 2, 27: 3, 28: 3, 29: 3, 36: 4, 37: 4,
                    38: 4, 39: 4, 45: 5, 46: 5, 47: 5, 48: 5, 49: 5, 54: 6,
                    55: 6, 56: 6, 57: 6, 58: 6, 59: 6, 63: 7, 64: 7, 65: 7,
                    66: 7, 67: 7, 68: 7, 69: 7, 72: 8, 73: 8, 74: 8, 75: 8,
                    76: 8, 77: 8, 78: 8, 79: 8, 81: 9, 82: 9, 83: 9, 84: 9,
                    85: 9, 86: 9, 87: 9, 88: 9, 89: 9}
        actual = {g: v kila v kwenye range(10) kila g kwenye range(v * 9, v * 10)}
        self.assertEqual(g, "Global variable")
        self.assertEqual(actual, expected)

    eleza test_global_visibility(self):
        expected = {0: 'Global variable', 1: 'Global variable',
                    2: 'Global variable', 3: 'Global variable',
                    4: 'Global variable', 5: 'Global variable',
                    6: 'Global variable', 7: 'Global variable',
                    8: 'Global variable', 9: 'Global variable'}
        actual = {k: g kila k kwenye range(10)}
        self.assertEqual(actual, expected)

    eleza test_local_visibility(self):
        v = "Local variable"
        expected = {0: 'Local variable', 1: 'Local variable',
                    2: 'Local variable', 3: 'Local variable',
                    4: 'Local variable', 5: 'Local variable',
                    6: 'Local variable', 7: 'Local variable',
                    8: 'Local variable', 9: 'Local variable'}
        actual = {k: v kila k kwenye range(10)}
        self.assertEqual(actual, expected)
        self.assertEqual(v, "Local variable")

    eleza test_illegal_assignment(self):
        ukijumuisha self.assertRaisesRegex(SyntaxError, "cannot assign"):
            compile("{x: y kila y, x kwenye ((1, 2), (3, 4))} = 5", "<test>",
                    "exec")

        ukijumuisha self.assertRaisesRegex(SyntaxError, "cannot assign"):
            compile("{x: y kila y, x kwenye ((1, 2), (3, 4))} += 5", "<test>",
                    "exec")

    eleza test_evaluation_order(self):
        expected = {
            'H': 'W',
            'e': 'o',
            'l': 'l',
            'o': 'd',
        }

        expected_calls = [
            ('key', 'H'), ('value', 'W'),
            ('key', 'e'), ('value', 'o'),
            ('key', 'l'), ('value', 'r'),
            ('key', 'l'), ('value', 'l'),
            ('key', 'o'), ('value', 'd'),
        ]

        actual_calls = []

        eleza add_call(pos, value):
            actual_calls.append((pos, value))
            rudisha value

        actual = {
            add_call('key', k): add_call('value', v)
            kila k, v kwenye zip('Hello', 'World')
        }

        self.assertEqual(actual, expected)
        self.assertEqual(actual_calls, expected_calls)

ikiwa __name__ == "__main__":
    unittest.main()
