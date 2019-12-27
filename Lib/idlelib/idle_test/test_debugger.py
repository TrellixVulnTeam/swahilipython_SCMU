"Test debugger, coverage 19%"

kutoka idlelib agiza debugger
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka tkinter agiza Tk


class NameSpaceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        del cls.root

    def test_init(self):
        debugger.NamespaceViewer(self.root, 'Test')


# Other classes are Idb, Debugger, and StackViewer.

if __name__ == '__main__':
    unittest.main(verbosity=2)
