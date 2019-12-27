"Test stackviewer, coverage 63%."

kutoka idlelib agiza stackviewer
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk

kutoka idlelib.tree agiza TreeNode, ScrolledCanvas
agiza sys


class StackBrowserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        svs = stackviewer.sys
        try:
            abc
        except NameError:
            svs.last_type, svs.last_value, svs.last_traceback = (
                sys.exc_info())

        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        svs = stackviewer.sys
        del svs.last_traceback, svs.last_type, svs.last_value

        cls.root.update_idletasks()
##        for id in cls.root.tk.call('after', 'info'):
##            cls.root.after_cancel(id)  # Need for EditorWindow.
        cls.root.destroy()
        del cls.root

    def test_init(self):
        sb = stackviewer.StackBrowser(self.root)
        isi = self.assertIsInstance
        isi(stackviewer.sc, ScrolledCanvas)
        isi(stackviewer.item, stackviewer.StackTreeItem)
        isi(stackviewer.node, TreeNode)


if __name__ == '__main__':
    unittest.main(verbosity=2)
