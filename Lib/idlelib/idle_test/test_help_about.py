"""Test help_about, coverage 100%.
help_about.build_bits branches on sys.platform='darwin'.
'100% combines coverage on Mac na others.
"""

kutoka idlelib agiza help_about
agiza unittest
kutoka test.support agiza requires, findfile
kutoka tkinter agiza Tk, TclError
kutoka idlelib.idle_test.mock_idle agiza Func
kutoka idlelib.idle_test.mock_tk agiza Mbox_func
kutoka idlelib agiza textview
agiza os.path
kutoka platform agiza python_version

About = help_about.AboutDialog


kundi LiveDialogTest(unittest.TestCase):
    """Simulate user clicking buttons other than [Close].

    Test that invoked textview has text kutoka source.
    """
    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.dialog = About(cls.root, 'About IDLE', _utest=Kweli)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.dialog
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza test_build_bits(self):
        self.assertIn(help_about.build_bits(), ('32', '64'))

    eleza test_dialog_title(self):
        """Test about dialog title"""
        self.assertEqual(self.dialog.title(), 'About IDLE')

    eleza test_dialog_logo(self):
        """Test about dialog logo."""
        path, file = os.path.split(self.dialog.icon_image['file'])
        fn, ext = os.path.splitext(file)
        self.assertEqual(fn, 'idle_48')

    eleza test_printer_buttons(self):
        """Test buttons whose commands use printer function."""
        dialog = self.dialog
        button_sources = [(dialog.py_license, license, 'license'),
                          (dialog.py_copyright, copyright, 'copyright'),
                          (dialog.py_credits, credits, 'credits')]

        kila button, printer, name kwenye button_sources:
            ukijumuisha self.subTest(name=name):
                printer._Printer__setup()
                button.invoke()
                get = dialog._current_textview.viewframe.textframe.text.get
                lines = printer._Printer__lines
                ikiwa len(lines) < 2:
                    self.fail(name + ' full text was sio found')
                self.assertEqual(lines[0], get('1.0', '1.end'))
                self.assertEqual(lines[1], get('2.0', '2.end'))
                dialog._current_textview.destroy()

    eleza test_file_buttons(self):
        """Test buttons that display files."""
        dialog = self.dialog
        button_sources = [(self.dialog.readme, 'README.txt', 'readme'),
                          (self.dialog.idle_news, 'NEWS.txt', 'news'),
                          (self.dialog.idle_credits, 'CREDITS.txt', 'credits')]

        kila button, filename, name kwenye button_sources:
            ukijumuisha  self.subTest(name=name):
                button.invoke()
                fn = findfile(filename, subdir='idlelib')
                get = dialog._current_textview.viewframe.textframe.text.get
                ukijumuisha open(fn, encoding='utf-8') as f:
                    self.assertEqual(f.readline().strip(), get('1.0', '1.end'))
                    f.readline()
                    self.assertEqual(f.readline().strip(), get('3.0', '3.end'))
                dialog._current_textview.destroy()


kundi DefaultTitleTest(unittest.TestCase):
    "Test default title."

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.dialog = About(cls.root, _utest=Kweli)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.dialog
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza test_dialog_title(self):
        """Test about dialog title"""
        self.assertEqual(self.dialog.title(),
                         f'About IDLE {python_version()}'
                         f' ({help_about.build_bits()} bit)')


kundi CloseTest(unittest.TestCase):
    """Simulate user clicking [Close] button"""

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.dialog = About(cls.root, 'About IDLE', _utest=Kweli)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.dialog
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza test_close(self):
        self.assertEqual(self.dialog.winfo_class(), 'Toplevel')
        self.dialog.button_ok.invoke()
        ukijumuisha self.assertRaises(TclError):
            self.dialog.winfo_class()


kundi Dummy_about_dialog():
    # Dummy kundi kila testing file display functions.
    idle_credits = About.show_idle_credits
    idle_readme = About.show_readme
    idle_news = About.show_idle_news
    # Called by the above
    display_file_text = About.display_file_text
    _utest = Kweli


kundi DisplayFileTest(unittest.TestCase):
    """Test functions that display files.

    While somewhat redundant ukijumuisha gui-based test_file_dialog,
    these unit tests run on all buildbots, sio just a few.
    """
    dialog = Dummy_about_dialog()

    @classmethod
    eleza setUpClass(cls):
        cls.orig_error = textview.showerror
        cls.orig_view = textview.view_text
        cls.error = Mbox_func()
        cls.view = Func()
        textview.showerror = cls.error
        textview.view_text = cls.view

    @classmethod
    eleza tearDownClass(cls):
        textview.showerror = cls.orig_error
        textview.view_text = cls.orig_view

    eleza test_file_display(self):
        kila handler kwenye (self.dialog.idle_credits,
                        self.dialog.idle_readme,
                        self.dialog.idle_news):
            self.error.message = ''
            self.view.called = Uongo
            ukijumuisha self.subTest(handler=handler):
                handler()
                self.assertEqual(self.error.message, '')
                self.assertEqual(self.view.called, Kweli)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
