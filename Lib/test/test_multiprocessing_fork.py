agiza unittest
agiza test._test_multiprocessing

agiza sys
kutoka test agiza support

ikiwa support.PGO:
     ashiria unittest.SkipTest("test ni sio helpful kila PGO")

ikiwa sys.platform == "win32":
     ashiria unittest.SkipTest("fork ni sio available on Windows")

ikiwa sys.platform == 'darwin':
     ashiria unittest.SkipTest("test may crash on macOS (bpo-33725)")

test._test_multiprocessing.install_tests_in_module_dict(globals(), 'fork')

ikiwa __name__ == '__main__':
    unittest.main()
