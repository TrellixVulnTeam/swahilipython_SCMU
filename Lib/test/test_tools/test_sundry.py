"""Tests kila scripts kwenye the Tools directory.

This file contains extremely basic regression tests kila the scripts found in
the Tools directory of a Python checkout ama tarball which don't have separate
tests of their own, such kama h2py.py.
"""

agiza os
agiza sys
agiza unittest
kutoka test agiza support

kutoka test.test_tools agiza scriptsdir, import_tool, skip_if_missing

skip_if_missing()

kundi TestSundryScripts(unittest.TestCase):
    # At least make sure the rest don't have syntax errors.  When tests are
    # added kila a script it should be added to the whitelist below.

    # scripts that have independent tests.
    whitelist = ['reindent', 'pdeps', 'gprof2html', 'md5sum']
    # scripts that can't be imported without running
    blacklist = ['make_ctype']
    # scripts that use windows-only modules
    windows_only = ['win_add2path']
    # blacklisted kila other reasons
    other = ['analyze_dxp', '2to3']

    skiplist = blacklist + whitelist + windows_only + other

    eleza test_sundry(self):
        old_modules = support.modules_setup()
        jaribu:
            kila fn kwenye os.listdir(scriptsdir):
                ikiwa sio fn.endswith('.py'):
                    endelea

                name = fn[:-3]
                ikiwa name kwenye self.skiplist:
                    endelea

                import_tool(name)
        mwishowe:
            # Unload all modules loaded kwenye this test
            support.modules_cleanup(*old_modules)

    @unittest.skipIf(sys.platform != "win32", "Windows-only test")
    eleza test_sundry_windows(self):
        kila name kwenye self.windows_only:
            import_tool(name)

    eleza test_analyze_dxp_agiza(self):
        ikiwa hasattr(sys, 'getdxp'):
            import_tool('analyze_dxp')
        isipokua:
            with self.assertRaises(RuntimeError):
                import_tool('analyze_dxp')


ikiwa __name__ == '__main__':
    unittest.main()
