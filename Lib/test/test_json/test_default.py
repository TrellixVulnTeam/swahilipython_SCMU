kutoka test.test_json agiza PyTest, CTest


kundi TestDefault:
    eleza test_default(self):
        self.assertEqual(
            self.dumps(type, default=repr),
            self.dumps(repr(type)))


kundi TestPyDefault(TestDefault, PyTest): pita
kundi TestCDefault(TestDefault, CTest): pita
