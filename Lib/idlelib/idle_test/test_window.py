"Test window, coverage 47%."

kutoka idlelib agiza window
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk


kundi WindowListTest(unittest.TestCase):

    eleza test_init(self):
        wl = window.WindowList()
        self.assertEqual(wl.dict, {})
        self.assertEqual(wl.callbacks, [])

    # Further tests need mock Window.


kundi ListedToplevelTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        window.registry = set()
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        window.registry = window.WindowList()
        cls.root.update_idletasks()
##        kila id kwenye cls.root.tk.call('after', 'info'):
##            cls.root.after_cancel(id)  # Need kila EditorWindow.
        cls.root.destroy()
        toa cls.root

    eleza test_init(self):

        win = window.ListedToplevel(self.root)
        self.assertIn(win, window.registry)
        self.assertEqual(win.focused_widget, win)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
