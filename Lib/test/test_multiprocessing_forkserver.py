agiza unittest
agiza test._test_multiprocessing

agiza sys
kutoka test agiza support

ikiwa support.PGO:
    ashiria unittest.SkipTest("test ni sio helpful kila PGO")

ikiwa sys.platform == "win32":
    ashiria unittest.SkipTest("forkserver ni sio available on Windows")

test._test_multiprocessing.install_tests_in_module_dict(globals(), 'forkserver')

ikiwa __name__ == '__main__':
    unittest.main()
