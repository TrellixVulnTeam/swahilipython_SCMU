"""Tests kila distutils.command.bdist_wininst."""
agiza sys
agiza platform
agiza unittest
kutoka test.support agiza run_unittest, check_warnings

kutoka distutils.command.bdist_wininst agiza bdist_wininst
kutoka distutils.tests agiza support

@unittest.skipIf(sys.platform == 'win32' na platform.machine() == 'ARM64',
    'bdist_wininst ni sio supported kwenye this install')
@unittest.skipIf(getattr(bdist_wininst, '_unsupported', Uongo),
    'bdist_wininst ni sio supported kwenye this install')
kundi BuildWinInstTestCase(support.TempdirManager,
                           support.LoggingSilencer,
                           unittest.TestCase):

    eleza test_get_exe_bytes(self):

        # issue5731: command was broken on non-windows platforms
        # this test makes sure it works now kila every platform
        # let's create a command
        pkg_pth, dist = self.create_dist()
        ukijumuisha check_warnings(("", DeprecationWarning)):
            cmd = bdist_wininst(dist)
        cmd.ensure_finalized()

        # let's run the code that finds the right wininst*.exe file
        # na make sure it finds it na returns its content
        # no matter what platform we have
        exe_file = cmd.get_exe_bytes()
        self.assertGreater(len(exe_file), 10)

eleza test_suite():
    rudisha unittest.makeSuite(BuildWinInstTestCase)

ikiwa __name__ == '__main__':
    run_unittest(test_suite())
