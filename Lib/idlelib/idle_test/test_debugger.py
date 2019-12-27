"Test debugger, coverage 19%"

kutoka idlelib agiza debugger
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka tkinter agiza Tk


kundi NameSpaceTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.destroy()
        del cls.root

    eleza test_init(self):
        debugger.NamespaceViewer(self.root, 'Test')


# Other classes are Idb, Debugger, and StackViewer.

ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
