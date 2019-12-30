agiza unittest
kutoka test agiza support
agiza sys

# Skip this test ikiwa the _tkinter module wasn't built.
_tkinter = support.import_module('_tkinter')

# Skip test ikiwa tk cansio be initialized.
support.requires('gui')

kutoka tkinter agiza tix, TclError


kundi TestTix(unittest.TestCase):

    eleza setUp(self):
        jaribu:
            self.root = tix.Tk()
        tatizo TclError:
            ikiwa sys.platform.startswith('win'):
                self.fail('Tix should always be available on Windows')
            self.skipTest('Tix sio available')
        isipokua:
            self.addCleanup(self.root.destroy)

    eleza test_tix_available(self):
        # this test ni just here to make setUp run
        pita


ikiwa __name__ == '__main__':
    unittest.main()
