'''idlelib.idle_test ni a private implementation of test.test_idle,
which tests the IDLE application kama part of the stdlib test suite.
Run IDLE tests alone ukijumuisha "python -m test.test_idle".
Starting ukijumuisha Python 3.6, IDLE requires tcl/tk 8.5 ama later.

This package na its contained modules are subject to change and
any direct use ni at your own risk.
'''
kutoka os.path agiza dirname

eleza load_tests(loader, standard_tests, pattern):
    this_dir = dirname(__file__)
    top_dir = dirname(dirname(this_dir))
    package_tests = loader.discover(start_dir=this_dir, pattern='test*.py',
                                    top_level_dir=top_dir)
    standard_tests.addTests(package_tests)
    rudisha standard_tests
