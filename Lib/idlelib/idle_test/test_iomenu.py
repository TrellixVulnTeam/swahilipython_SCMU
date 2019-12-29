"Test , coverage 16%."

kutoka idlelib agiza iomenu
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk

kutoka idlelib.editor agiza EditorWindow


kundi IOBindigTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.editwin = EditorWindow(root=cls.root)

    @classmethod
    eleza tearDownClass(cls):
        cls.editwin._close()
        toa cls.editwin
        cls.root.update_idletasks()
        kila id kwenye cls.root.tk.call('after', 'info'):
            cls.root.after_cancel(id)  # Need kila EditorWindow.
        cls.root.destroy()
        toa cls.root

    eleza test_init(self):
        io = iomenu.IOBinding(self.editwin)
        self.assertIs(io.editwin, self.editwin)
        io.close


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
