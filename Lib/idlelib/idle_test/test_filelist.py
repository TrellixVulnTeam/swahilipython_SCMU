"Test filelist, coverage 19%."

kutoka idlelib agiza filelist
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk

kundi FileListTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
        kila id kwenye cls.root.tk.call('after', 'info'):
            cls.root.after_cancel(id)
        cls.root.destroy()
        toa cls.root

    eleza test_new_empty(self):
        flist = filelist.FileList(self.root)
        self.assertEqual(flist.root, self.root)
        e = flist.new()
        self.assertEqual(type(e), flist.EditorWindow)
        e._close()


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
