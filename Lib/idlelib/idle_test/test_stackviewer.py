"Test stackviewer, coverage 63%."

kutoka idlelib agiza stackviewer
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk

kutoka idlelib.tree agiza TreeNode, ScrolledCanvas
agiza sys


kundi StackBrowserTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
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
    eleza tearDownClass(cls):
        svs = stackviewer.sys
        del svs.last_traceback, svs.last_type, svs.last_value

        cls.root.update_idletasks()
##        for id in cls.root.tk.call('after', 'info'):
##            cls.root.after_cancel(id)  # Need for EditorWindow.
        cls.root.destroy()
        del cls.root

    eleza test_init(self):
        sb = stackviewer.StackBrowser(self.root)
        isi = self.assertIsInstance
        isi(stackviewer.sc, ScrolledCanvas)
        isi(stackviewer.item, stackviewer.StackTreeItem)
        isi(stackviewer.node, TreeNode)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
