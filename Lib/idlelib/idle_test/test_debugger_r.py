"Test debugger_r, coverage 30%."

kutoka idlelib agiza debugger_r
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk


kundi Test(unittest.TestCase):

##    @classmethod
##    eleza setUpClass(cls):
##        requires('gui')
##        cls.root = Tk()
##
##    @classmethod
##    eleza tearDownClass(cls):
##        cls.root.destroy()
##        del cls.root

    eleza test_init(self):
        self.assertTrue(True)  # Get coverage of agiza


# Classes GUIProxy, IdbAdapter, FrameProxy, CodeProxy, DictProxy,
# GUIAdapter, IdbProxy plus 7 module functions.

ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
