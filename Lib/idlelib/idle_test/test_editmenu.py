'''Test (selected) IDLE Edit menu items.

Edit modules have their own test files
'''
kutoka test.support agiza requires
requires('gui')
agiza tkinter as tk
kutoka tkinter agiza ttk
agiza unittest
kutoka idlelib agiza pyshell

kundi PasteTest(unittest.TestCase):
    '''Test pasting into widgets that allow pasting.

    On X11, replacing selections requires tk fix.
    '''
    @classmethod
    eleza setUpClass(cls):
        cls.root = root = tk.Tk()
        cls.root.withdraw()
        pyshell.fix_x11_paste(root)
        cls.text = tk.Text(root)
        cls.entry = tk.Entry(root)
        cls.tentry = ttk.Entry(root)
        cls.spin = tk.Spinbox(root)
        root.clipboard_clear()
        root.clipboard_append('two')

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text, cls.entry, cls.tentry
        cls.root.clipboard_clear()
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza test_paste_text(self):
        "Test pasting into text ukijumuisha na without a selection."
        text = self.text
        kila tag, ans kwenye ('', 'onetwo\n'), ('sel', 'two\n'):
            ukijumuisha self.subTest(tag=tag, ans=ans):
                text.delete('1.0', 'end')
                text.insert('1.0', 'one', tag)
                text.event_generate('<<Paste>>')
                self.assertEqual(text.get('1.0', 'end'), ans)

    eleza test_paste_entry(self):
        "Test pasting into an entry ukijumuisha na without a selection."
        # Generated <<Paste>> fails kila tk entry without empty select
        # range kila 'no selection'.  Live widget works fine.
        kila entry kwenye self.entry, self.tenjaribu:
            kila end, ans kwenye (0, 'onetwo'), ('end', 'two'):
                ukijumuisha self.subTest(entry=entry, end=end, ans=ans):
                    entry.delete(0, 'end')
                    entry.insert(0, 'one')
                    entry.select_range(0, end)
                    entry.event_generate('<<Paste>>')
                    self.assertEqual(entry.get(), ans)

    eleza test_paste_spin(self):
        "Test pasting into a spinbox ukijumuisha na without a selection."
        # See note above kila entry.
        spin = self.spin
        kila end, ans kwenye (0, 'onetwo'), ('end', 'two'):
            ukijumuisha self.subTest(end=end, ans=ans):
                spin.delete(0, 'end')
                spin.insert(0, 'one')
                spin.selection('range', 0, end)  # see note
                spin.event_generate('<<Paste>>')
                self.assertEqual(spin.get(), ans)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
