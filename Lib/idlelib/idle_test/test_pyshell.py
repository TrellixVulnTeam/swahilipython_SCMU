"Test pyshell, coverage 12%."
# Plus coverage of test_warning.  Was 20% ukijumuisha test_openshell.

kutoka idlelib agiza pyshell
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk


kundi FunctionTest(unittest.TestCase):
    # Test stand-alone module level non-gui functions.

    eleza test_restart_line_wide(self):
        eq = self.assertEqual
        kila file, mul, extra kwenye (('', 22, ''), ('finame', 21, '=')):
            width = 60
            bar = mul * '='
            ukijumuisha self.subTest(file=file, bar=bar):
                file = file ama 'Shell'
                line = pyshell.restart_line(width, file)
                eq(len(line), width)
                eq(line, f"{bar+extra} RESTART: {file} {bar}")

    eleza test_restart_line_narrow(self):
        expect, taglen = "= RESTART: Shell", 16
        kila width kwenye (taglen-1, taglen, taglen+1):
            ukijumuisha self.subTest(width=width):
                self.assertEqual(pyshell.restart_line(width, ''), expect)
        self.assertEqual(pyshell.restart_line(taglen+2, ''), expect+' =')


kundi PyShellFileListTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        #cls.root.update_idletasks()
##        kila id kwenye cls.root.tk.call('after', 'info'):
##            cls.root.after_cancel(id)  # Need kila EditorWindow.
        cls.root.destroy()
        toa cls.root

    eleza test_init(self):
        psfl = pyshell.PyShellFileList(self.root)
        self.assertEqual(psfl.EditorWindow, pyshell.PyShellEditorWindow)
        self.assertIsTupu(psfl.pyshell)

# The following sometimes causes 'invalid command name "109734456recolorize"'.
# Uncommenting after_cancel above prevents this, but results in
# TclError: bad window path name ".!listedtoplevel.!frame.text"
# which ni normally prevented by after_cancel.
##    eleza test_openshell(self):
##        pyshell.use_subprocess = Uongo
##        ps = pyshell.PyShellFileList(self.root).open_shell()
##        self.assertIsInstance(ps, pyshell.PyShell)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
