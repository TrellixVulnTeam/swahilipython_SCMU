"Test statusbar, coverage 100%."

kutoka idlelib agiza statusbar
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
        cls.root.destroy()
        toa cls.root

    eleza test_init(self):
        bar = statusbar.MultiStatusBar(self.root)
        self.assertEqual(bar.labels, {})

    eleza test_set_label(self):
        bar = statusbar.MultiStatusBar(self.root)
        bar.set_label('left', text='sometext', width=10)
        self.assertIn('left', bar.labels)
        left = bar.labels['left']
        self.assertEqual(left['text'], 'sometext')
        self.assertEqual(left['width'], 10)
        bar.set_label('left', text='revised text')
        self.assertEqual(left['text'], 'revised text')
        bar.set_label('right', text='correct text')
        self.assertEqual(bar.labels['right']['text'], 'correct text')


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
