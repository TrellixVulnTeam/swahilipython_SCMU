'''Test warnings replacement kwenye pyshell.py na run.py.

This file could be expanded to include traceback overrides
(in same two modules). If so, change name.
Revise ikiwa output destination changes (http://bugs.python.org/issue18318).
Make sure warnings module ni left unaltered (http://bugs.python.org/issue18081).
'''
kutoka idlelib agiza run
kutoka idlelib agiza pyshell kama shell
agiza unittest
kutoka test.support agiza captured_stderr
agiza warnings

# Try to capture default showwarning before Idle modules are imported.
showwarning = warnings.showwarning
# But ikiwa we run this file within idle, we are kwenye the middle of the run.main loop
# na default showwarnings has already been replaced.
running_in_idle = 'idle' kwenye showwarning.__name__

# The following was generated kutoka pyshell.idle_formatwarning
# na checked kama matching expectation.
idlemsg = '''
Warning (kutoka warnings module):
  File "test_warning.py", line 99
    Line of code
UserWarning: Test
'''
shellmsg = idlemsg + ">>> "


kundi RunWarnTest(unittest.TestCase):

    @unittest.skipIf(running_in_idle, "Does sio work when run within Idle.")
    eleza test_showwarnings(self):
        self.assertIs(warnings.showwarning, showwarning)
        run.capture_warnings(Kweli)
        self.assertIs(warnings.showwarning, run.idle_showwarning_subproc)
        run.capture_warnings(Uongo)
        self.assertIs(warnings.showwarning, showwarning)

    eleza test_run_show(self):
        with captured_stderr() kama f:
            run.idle_showwarning_subproc(
                    'Test', UserWarning, 'test_warning.py', 99, f, 'Line of code')
            # The following uses .splitlines to erase line-ending differences
            self.assertEqual(idlemsg.splitlines(), f.getvalue().splitlines())


kundi ShellWarnTest(unittest.TestCase):

    @unittest.skipIf(running_in_idle, "Does sio work when run within Idle.")
    eleza test_showwarnings(self):
        self.assertIs(warnings.showwarning, showwarning)
        shell.capture_warnings(Kweli)
        self.assertIs(warnings.showwarning, shell.idle_showwarning)
        shell.capture_warnings(Uongo)
        self.assertIs(warnings.showwarning, showwarning)

    eleza test_idle_formatter(self):
        # Will fail ikiwa format changed without regenerating idlemsg
        s = shell.idle_formatwarning(
                'Test', UserWarning, 'test_warning.py', 99, 'Line of code')
        self.assertEqual(idlemsg, s)

    eleza test_shell_show(self):
        with captured_stderr() kama f:
            shell.idle_showwarning(
                    'Test', UserWarning, 'test_warning.py', 99, f, 'Line of code')
            self.assertEqual(shellmsg.splitlines(), f.getvalue().splitlines())


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
