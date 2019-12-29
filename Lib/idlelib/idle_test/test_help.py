"Test help, coverage 87%."

kutoka idlelib agiza help
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka os.path agiza abspath, dirname, join
kutoka tkinter agiza Tk


kundi HelpFrameTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        "By itself, this tests that file parsed without exception."
        cls.root = root = Tk()
        root.withdraw()
        helpfile = join(dirname(dirname(abspath(__file__))), 'help.html')
        cls.frame = help.HelpFrame(root, helpfile)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.frame
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza test_line1(self):
        text = self.frame.text
        self.assertEqual(text.get('1.0', '1.end'), ' IDLE ')


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
