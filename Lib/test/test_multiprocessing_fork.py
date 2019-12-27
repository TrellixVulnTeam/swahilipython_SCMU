agiza unittest
agiza test._test_multiprocessing

agiza sys
kutoka test agiza support

ikiwa support.PGO:
    raise unittest.SkipTest("test is not helpful for PGO")

ikiwa sys.platform == "win32":
    raise unittest.SkipTest("fork is not available on Windows")

ikiwa sys.platform == 'darwin':
    raise unittest.SkipTest("test may crash on macOS (bpo-33725)")

test._test_multiprocessing.install_tests_in_module_dict(globals(), 'fork')

ikiwa __name__ == '__main__':
    unittest.main()
