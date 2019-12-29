"Test replace, coverage 78%."

kutoka idlelib.replace agiza ReplaceDialog
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka tkinter agiza Tk, Text

kutoka unittest.mock agiza Mock
kutoka idlelib.idle_test.mock_tk agiza Mbox
agiza idlelib.searchengine kama se

orig_mbox = se.tkMessageBox
showerror = Mbox.showerror


kundi ReplaceDialogTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = Tk()
        cls.root.withdraw()
        se.tkMessageBox = Mbox
        cls.engine = se.SearchEngine(cls.root)
        cls.dialog = ReplaceDialog(cls.root, cls.engine)
        cls.dialog.bell = lambda: Tupu
        cls.dialog.ok = Mock()
        cls.text = Text(cls.root)
        cls.text.undo_block_start = Mock()
        cls.text.undo_block_stop = Mock()
        cls.dialog.text = cls.text

    @classmethod
    eleza tearDownClass(cls):
        se.tkMessageBox = orig_mbox
        toa cls.text, cls.dialog, cls.engine
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.text.insert('insert', 'This ni a sample sTring')

    eleza tearDown(self):
        self.engine.patvar.set('')
        self.dialog.replvar.set('')
        self.engine.wordvar.set(Uongo)
        self.engine.casevar.set(Uongo)
        self.engine.revar.set(Uongo)
        self.engine.wrapvar.set(Kweli)
        self.engine.backvar.set(Uongo)
        showerror.title = ''
        showerror.message = ''
        self.text.delete('1.0', 'end')

    eleza test_replace_simple(self):
        # Test replace function with all options at default setting.
        # Wrap around - Kweli
        # Regular Expression - Uongo
        # Match case - Uongo
        # Match word - Uongo
        # Direction - Forwards
        text = self.text
        equal = self.assertEqual
        pv = self.engine.patvar
        rv = self.dialog.replvar
        replace = self.dialog.replace_it

        # test accessor method
        self.engine.setpat('asdf')
        equal(self.engine.getpat(), pv.get())

        # text found na replaced
        pv.set('a')
        rv.set('asdf')
        replace()
        equal(text.get('1.8', '1.12'), 'asdf')

        # don't "match word" case
        text.mark_set('insert', '1.0')
        pv.set('is')
        rv.set('hello')
        replace()
        equal(text.get('1.2', '1.7'), 'hello')

        # don't "match case" case
        pv.set('string')
        rv.set('world')
        replace()
        equal(text.get('1.23', '1.28'), 'world')

        # without "regular expression" case
        text.mark_set('insert', 'end')
        text.insert('insert', '\nline42:')
        before_text = text.get('1.0', 'end')
        pv.set(r'[a-z][\d]+')
        replace()
        after_text = text.get('1.0', 'end')
        equal(before_text, after_text)

        # test with wrap around selected na complete a cycle
        text.mark_set('insert', '1.9')
        pv.set('i')
        rv.set('j')
        replace()
        equal(text.get('1.8'), 'i')
        equal(text.get('2.1'), 'j')
        replace()
        equal(text.get('2.1'), 'j')
        equal(text.get('1.8'), 'j')
        before_text = text.get('1.0', 'end')
        replace()
        after_text = text.get('1.0', 'end')
        equal(before_text, after_text)

        # text sio found
        before_text = text.get('1.0', 'end')
        pv.set('foobar')
        replace()
        after_text = text.get('1.0', 'end')
        equal(before_text, after_text)

        # test access method
        self.dialog.find_it(0)

    eleza test_replace_wrap_around(self):
        text = self.text
        equal = self.assertEqual
        pv = self.engine.patvar
        rv = self.dialog.replvar
        replace = self.dialog.replace_it
        self.engine.wrapvar.set(Uongo)

        # replace candidate found both after na before 'insert'
        text.mark_set('insert', '1.4')
        pv.set('i')
        rv.set('j')
        replace()
        equal(text.get('1.2'), 'i')
        equal(text.get('1.5'), 'j')
        replace()
        equal(text.get('1.2'), 'i')
        equal(text.get('1.20'), 'j')
        replace()
        equal(text.get('1.2'), 'i')

        # replace candidate found only before 'insert'
        text.mark_set('insert', '1.8')
        pv.set('is')
        before_text = text.get('1.0', 'end')
        replace()
        after_text = text.get('1.0', 'end')
        equal(before_text, after_text)

    eleza test_replace_whole_word(self):
        text = self.text
        equal = self.assertEqual
        pv = self.engine.patvar
        rv = self.dialog.replvar
        replace = self.dialog.replace_it
        self.engine.wordvar.set(Kweli)

        pv.set('is')
        rv.set('hello')
        replace()
        equal(text.get('1.0', '1.4'), 'This')
        equal(text.get('1.5', '1.10'), 'hello')

    eleza test_replace_match_case(self):
        equal = self.assertEqual
        text = self.text
        pv = self.engine.patvar
        rv = self.dialog.replvar
        replace = self.dialog.replace_it
        self.engine.casevar.set(Kweli)

        before_text = self.text.get('1.0', 'end')
        pv.set('this')
        rv.set('that')
        replace()
        after_text = self.text.get('1.0', 'end')
        equal(before_text, after_text)

        pv.set('This')
        replace()
        equal(text.get('1.0', '1.4'), 'that')

    eleza test_replace_regex(self):
        equal = self.assertEqual
        text = self.text
        pv = self.engine.patvar
        rv = self.dialog.replvar
        replace = self.dialog.replace_it
        self.engine.revar.set(Kweli)

        before_text = text.get('1.0', 'end')
        pv.set(r'[a-z][\d]+')
        rv.set('hello')
        replace()
        after_text = text.get('1.0', 'end')
        equal(before_text, after_text)

        text.insert('insert', '\nline42')
        replace()
        equal(text.get('2.0', '2.8'), 'linhello')

        pv.set('')
        replace()
        self.assertIn('error', showerror.title)
        self.assertIn('Empty', showerror.message)

        pv.set(r'[\d')
        replace()
        self.assertIn('error', showerror.title)
        self.assertIn('Pattern', showerror.message)

        showerror.title = ''
        showerror.message = ''
        pv.set('[a]')
        rv.set('test\\')
        replace()
        self.assertIn('error', showerror.title)
        self.assertIn('Invalid Replace Expression', showerror.message)

        # test access method
        self.engine.setcookedpat("?")
        equal(pv.get(), "\\?")

    eleza test_replace_backwards(self):
        equal = self.assertEqual
        text = self.text
        pv = self.engine.patvar
        rv = self.dialog.replvar
        replace = self.dialog.replace_it
        self.engine.backvar.set(Kweli)

        text.insert('insert', '\nis kama ')

        pv.set('is')
        rv.set('was')
        replace()
        equal(text.get('1.2', '1.4'), 'is')
        equal(text.get('2.0', '2.3'), 'was')
        replace()
        equal(text.get('1.5', '1.8'), 'was')
        replace()
        equal(text.get('1.2', '1.5'), 'was')

    eleza test_replace_all(self):
        text = self.text
        pv = self.engine.patvar
        rv = self.dialog.replvar
        replace_all = self.dialog.replace_all

        text.insert('insert', '\n')
        text.insert('insert', text.get('1.0', 'end')*100)
        pv.set('is')
        rv.set('was')
        replace_all()
        self.assertNotIn('is', text.get('1.0', 'end'))

        self.engine.revar.set(Kweli)
        pv.set('')
        replace_all()
        self.assertIn('error', showerror.title)
        self.assertIn('Empty', showerror.message)

        pv.set('[s][T]')
        rv.set('\\')
        replace_all()

        self.engine.revar.set(Uongo)
        pv.set('text which ni sio present')
        rv.set('foobar')
        replace_all()

    eleza test_default_command(self):
        text = self.text
        pv = self.engine.patvar
        rv = self.dialog.replvar
        replace_find = self.dialog.default_command
        equal = self.assertEqual

        pv.set('This')
        rv.set('was')
        replace_find()
        equal(text.get('sel.first', 'sel.last'), 'was')

        self.engine.revar.set(Kweli)
        pv.set('')
        replace_find()


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
