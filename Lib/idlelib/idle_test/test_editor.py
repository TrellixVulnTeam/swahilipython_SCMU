"Test editor, coverage 35%."

kutoka idlelib agiza editor
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk

Editor = editor.EditorWindow


kundi EditorWindowTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
        for id in cls.root.tk.call('after', 'info'):
            cls.root.after_cancel(id)
        cls.root.destroy()
        del cls.root

    eleza test_init(self):
        e = Editor(root=self.root)
        self.assertEqual(e.root, self.root)
        e._close()


kundi TestGetLineIndent(unittest.TestCase):
    eleza test_empty_lines(self):
        for tabwidth in [1, 2, 4, 6, 8]:
            for line in ['', '\n']:
                with self.subTest(line=line, tabwidth=tabwidth):
                    self.assertEqual(
                        editor.get_line_indent(line, tabwidth=tabwidth),
                        (0, 0),
                    )

    eleza test_tabwidth_4(self):
        #        (line, (raw, effective))
        tests = (('no spaces', (0, 0)),
                 # Internal space isn't counted.
                 ('    space test', (4, 4)),
                 ('\ttab test', (1, 4)),
                 ('\t\tdouble tabs test', (2, 8)),
                 # Different results when mixing tabs and spaces.
                 ('    \tmixed test', (5, 8)),
                 ('  \t  mixed test', (5, 6)),
                 ('\t    mixed test', (5, 8)),
                 # Spaces not divisible by tabwidth.
                 ('  \tmixed test', (3, 4)),
                 (' \t mixed test', (3, 5)),
                 ('\t  mixed test', (3, 6)),
                 # Only checks spaces and tabs.
                 ('\nnewline test', (0, 0)))

        for line, expected in tests:
            with self.subTest(line=line):
                self.assertEqual(
                    editor.get_line_indent(line, tabwidth=4),
                    expected,
                )

    eleza test_tabwidth_8(self):
        #        (line, (raw, effective))
        tests = (('no spaces', (0, 0)),
                 # Internal space isn't counted.
                 ('        space test', (8, 8)),
                 ('\ttab test', (1, 8)),
                 ('\t\tdouble tabs test', (2, 16)),
                 # Different results when mixing tabs and spaces.
                 ('        \tmixed test', (9, 16)),
                 ('      \t  mixed test', (9, 10)),
                 ('\t        mixed test', (9, 16)),
                 # Spaces not divisible by tabwidth.
                 ('  \tmixed test', (3, 8)),
                 (' \t mixed test', (3, 9)),
                 ('\t  mixed test', (3, 10)),
                 # Only checks spaces and tabs.
                 ('\nnewline test', (0, 0)))

        for line, expected in tests:
            with self.subTest(line=line):
                self.assertEqual(
                    editor.get_line_indent(line, tabwidth=8),
                    expected,
                )


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
