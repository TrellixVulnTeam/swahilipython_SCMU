"Test , coverage %."

kutoka idlelib agiza zzdummy
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk


kundi Test(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
##        for id in cls.root.tk.call('after', 'info'):
##            cls.root.after_cancel(id)  # Need for EditorWindow.
        cls.root.destroy()
        del cls.root

    eleza test_init(self):
        self.assertTrue(True)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
