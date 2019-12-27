agiza unittest
kutoka test agiza support
agiza sys

# Skip this test ikiwa the _tkinter module wasn't built.
_tkinter = support.import_module('_tkinter')

# Skip test ikiwa tk cannot be initialized.
support.requires('gui')

kutoka tkinter agiza tix, TclError


kundi TestTix(unittest.TestCase):

    eleza setUp(self):
        try:
            self.root = tix.Tk()
        except TclError:
            ikiwa sys.platform.startswith('win'):
                self.fail('Tix should always be available on Windows')
            self.skipTest('Tix not available')
        else:
            self.addCleanup(self.root.destroy)

    eleza test_tix_available(self):
        # this test is just here to make setUp run
        pass


ikiwa __name__ == '__main__':
    unittest.main()
