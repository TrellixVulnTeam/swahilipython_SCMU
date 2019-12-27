agiza unittest
kutoka test.support agiza import_module

ctypes_test = import_module('ctypes.test')

load_tests = ctypes_test.load_tests

ikiwa __name__ == "__main__":
    unittest.main()
