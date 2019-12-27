"Test calltip_w, coverage 18%."

kutoka idlelib agiza calltip_w
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk, Text


class CallTipWindowTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.text = Text(cls.root)
        cls.calltip = calltip_w.CalltipWindow(cls.text)

    @classmethod
    def tearDownClass(cls):
        cls.root.update_idletasks()
        cls.root.destroy()
        del cls.text, cls.root

    def test_init(self):
        self.assertEqual(self.calltip.anchor_widget, self.text)

if __name__ == '__main__':
    unittest.main(verbosity=2)
