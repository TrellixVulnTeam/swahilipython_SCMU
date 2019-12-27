"Test autocomplete_w, coverage 11%."

agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk, Text

agiza idlelib.autocomplete_w as acw


kundi AutoCompleteWindowTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.text = Text(cls.root)
        cls.acw = acw.AutoCompleteWindow(cls.text)

    @classmethod
    eleza tearDownClass(cls):
        del cls.text, cls.acw
        cls.root.update_idletasks()
        cls.root.destroy()
        del cls.root

    eleza test_init(self):
        self.assertEqual(self.acw.widget, self.text)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
