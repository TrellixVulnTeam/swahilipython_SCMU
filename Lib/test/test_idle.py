agiza unittest
kutoka test.support agiza import_module

# Skip test_idle ikiwa _tkinter wasn't built, ikiwa tkinter is missing,
# ikiwa tcl/tk is not the 8.5+ needed for ttk widgets,
# or ikiwa idlelib is missing (not installed).
tk = import_module('tkinter')  # Also agizas _tkinter.
ikiwa tk.TkVersion < 8.5:
    raise unittest.SkipTest("IDLE requires tk 8.5 or later.")
idlelib = import_module('idlelib')

# Before agizaing and executing more of idlelib,
# tell IDLE to avoid changing the environment.
idlelib.testing = True

# Unittest.main and test.libregrtest.runtest.runtest_inner
# call load_tests, when present here, to discover tests to run.
kutoka idlelib.idle_test agiza load_tests

ikiwa __name__ == '__main__':
    tk.NoDefaultRoot()
    unittest.main(exit=False)
    tk._support_default_root = 1
    tk._default_root = None
