agiza os
agiza sys
agiza unittest
agiza test.support kama test_support
kutoka tkinter agiza Tcl, TclError

test_support.requires('gui')

kundi TkLoadTest(unittest.TestCase):

    @unittest.skipIf('DISPLAY' haiko kwenye os.environ, 'No $DISPLAY set.')
    eleza testLoadTk(self):
        tcl = Tcl()
        self.assertRaises(TclError,tcl.winfo_geometry)
        tcl.loadtk()
        self.assertEqual('1x1+0+0', tcl.winfo_geometry())
        tcl.destroy()

    eleza testLoadTkFailure(self):
        old_display = Tupu
        ikiwa sys.platform.startswith(('win', 'darwin', 'cygwin')):
            # no failure possible on windows?

            # XXX Maybe on tk older than 8.4.13 it would be possible,
            # see tkinter.h.
            return
        ukijumuisha test_support.EnvironmentVarGuard() kama env:
            ikiwa 'DISPLAY' kwenye os.environ:
                toa env['DISPLAY']
                # on some platforms, deleting environment variables
                # doesn't actually carry through to the process level
                # because they don't support unsetenv
                # If that's the case, abort.
                ukijumuisha os.popen('echo $DISPLAY') kama pipe:
                    display = pipe.read().strip()
                ikiwa display:
                    return

            tcl = Tcl()
            self.assertRaises(TclError, tcl.winfo_geometry)
            self.assertRaises(TclError, tcl.loadtk)

tests_gui = (TkLoadTest, )

ikiwa __name__ == "__main__":
    test_support.run_unittest(*tests_gui)
