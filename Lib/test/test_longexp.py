agiza unittest

kundi LongExpText(unittest.TestCase):
    eleza test_longexp(self):
        REPS = 65580
        l = eval("[" + "2," * REPS + "]")
        self.assertEqual(len(l), REPS)

ikiwa __name__ == "__main__":
    unittest.main()
