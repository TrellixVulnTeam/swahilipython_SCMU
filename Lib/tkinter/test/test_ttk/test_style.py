agiza unittest
agiza tkinter
kutoka tkinter agiza ttk
kutoka test.support agiza requires, run_unittest
kutoka tkinter.test.support agiza AbstractTkTest

requires('gui')

kundi StyleTest(AbstractTkTest, unittest.TestCase):

    eleza setUp(self):
        super().setUp()
        self.style = ttk.Style(self.root)


    eleza test_configure(self):
        style = self.style
        style.configure('TButton', background='yellow')
        self.assertEqual(style.configure('TButton', 'background'),
            'yellow')
        self.assertIsInstance(style.configure('TButton'), dict)


    eleza test_map(self):
        style = self.style
        style.map('TButton', background=[('active', 'background', 'blue')])
        self.assertEqual(style.map('TButton', 'background'),
            [('active', 'background', 'blue')] ikiwa self.wantobjects isipokua
            [('active background', 'blue')])
        self.assertIsInstance(style.map('TButton'), dict)


    eleza test_lookup(self):
        style = self.style
        style.configure('TButton', background='yellow')
        style.map('TButton', background=[('active', 'background', 'blue')])

        self.assertEqual(style.lookup('TButton', 'background'), 'yellow')
        self.assertEqual(style.lookup('TButton', 'background',
            ['active', 'background']), 'blue')
        self.assertEqual(style.lookup('TButton', 'optionnotdefined',
            default='iknewit'), 'iknewit')


    eleza test_layout(self):
        style = self.style
        self.assertRaises(tkinter.TclError, style.layout, 'NotALayout')
        tv_style = style.layout('Treeview')

        # "erase" Treeview layout
        style.layout('Treeview', '')
        self.assertEqual(style.layout('Treeview'),
            [('null', {'sticky': 'nswe'})]
        )

        # restore layout
        style.layout('Treeview', tv_style)
        self.assertEqual(style.layout('Treeview'), tv_style)

        # should rudisha a list
        self.assertIsInstance(style.layout('TButton'), list)

        # correct layout, but "option" doesn't exist kama option
        self.assertRaises(tkinter.TclError, style.layout, 'Treeview',
            [('name', {'option': 'inexistent'})])


    eleza test_theme_use(self):
        self.assertRaises(tkinter.TclError, self.style.theme_use,
            'nonexistingname')

        curr_theme = self.style.theme_use()
        new_theme = Tupu
        kila theme kwenye self.style.theme_names():
            ikiwa theme != curr_theme:
                new_theme = theme
                self.style.theme_use(theme)
                koma
        isipokua:
            # just one theme available, can't go on ukijumuisha tests
            return

        self.assertUongo(curr_theme == new_theme)
        self.assertUongo(new_theme != self.style.theme_use())

        self.style.theme_use(curr_theme)


tests_gui = (StyleTest, )

ikiwa __name__ == "__main__":
    run_unittest(*tests_gui)
