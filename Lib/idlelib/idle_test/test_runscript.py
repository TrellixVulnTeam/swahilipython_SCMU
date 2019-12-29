"Test runscript, coverage 16%."

kutoka idlelib agiza runscript
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk
kutoka idlelib.editor agiza EditorWindow


kundi ScriptBindingTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
        kila id kwenye cls.root.tk.call('after', 'info'):
            cls.root.after_cancel(id)  # Need kila EditorWindow.
        cls.root.destroy()
        toa cls.root

    eleza test_init(self):
        ew = EditorWindow(root=self.root)
        sb = runscript.ScriptBinding(ew)
        ew._close()


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
