"Test mainmenu, coverage 100%."
# Reported as 88%; mocking turtledemo absence would have no point.

kutoka idlelib agiza mainmenu
agiza unittest


kundi MainMenuTest(unittest.TestCase):

    eleza test_menudefs(self):
        actual = [item[0] for item in mainmenu.menudefs]
        expect = ['file', 'edit', 'format', 'run', 'shell',
                  'debug', 'options', 'window', 'help']
        self.assertEqual(actual, expect)

    eleza test_default_keydefs(self):
        self.assertGreaterEqual(len(mainmenu.default_keydefs), 50)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
