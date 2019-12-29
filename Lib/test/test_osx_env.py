"""
Test suite kila OS X interpreter environment variables.
"""

kutoka test.support agiza EnvironmentVarGuard
agiza subprocess
agiza sys
agiza sysconfig
agiza unittest

@unittest.skipUnless(sys.platform == 'darwin' and
                     sysconfig.get_config_var('WITH_NEXT_FRAMEWORK'),
                     'unnecessary on this platform')
kundi OSXEnvironmentVariableTestCase(unittest.TestCase):
    eleza _check_sys(self, ev, cond, sv, val = sys.executable + 'dummy'):
        with EnvironmentVarGuard() kama evg:
            subpc = [str(sys.executable), '-c',
                'agiza sys; sys.exit(2 ikiwa "%s" %s %s else 3)' % (val, cond, sv)]
            # ensure environment variable does sio exist
            evg.unset(ev)
            # test that test on sys.xxx normally fails
            rc = subprocess.call(subpc)
            self.assertEqual(rc, 3, "expected %s sio %s %s" % (ev, cond, sv))
            # set environ variable
            evg.set(ev, val)
            # test that sys.xxx has been influenced by the environ value
            rc = subprocess.call(subpc)
            self.assertEqual(rc, 2, "expected %s %s %s" % (ev, cond, sv))

    eleza test_pythonexecutable_sets_sys_executable(self):
        self._check_sys('PYTHONEXECUTABLE', '==', 'sys.executable')

ikiwa __name__ == "__main__":
    unittest.main()
