agiza unittest
agiza test._test_multiprocessing

agiza sys
kutoka test agiza support

ikiwa support.PGO:
    raise unittest.SkipTest("test is not helpful for PGO")

ikiwa sys.platform == "win32":
    raise unittest.SkipTest("forkserver is not available on Windows")

test._test_multiprocessing.install_tests_in_module_dict(globals(), 'forkserver')

ikiwa __name__ == '__main__':
    unittest.main()
