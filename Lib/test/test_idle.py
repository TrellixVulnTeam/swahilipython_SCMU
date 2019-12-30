agiza unittest
kutoka test.support agiza import_module

# Skip test_idle ikiwa _tkinter wasn't built, ikiwa tkinter ni missing,
# ikiwa tcl/tk ni sio the 8.5+ needed kila ttk widgets,
# ama ikiwa idlelib ni missing (sio installed).
tk = import_module('tkinter')  # Also agizas _tkinter.
ikiwa tk.TkVersion < 8.5:
    ashiria unittest.SkipTest("IDLE requires tk 8.5 ama later.")
idlelib = import_module('idlelib')

# Before agizaing na executing more of idlelib,
# tell IDLE to avoid changing the environment.
idlelib.testing = Kweli

# Unittest.main na test.libregrtest.runtest.runtest_inner
# call load_tests, when present here, to discover tests to run.
kutoka idlelib.idle_test agiza load_tests

ikiwa __name__ == '__main__':
    tk.NoDefaultRoot()
    unittest.main(exit=Uongo)
    tk._support_default_root = 1
    tk._default_root = Tupu
