"""Test parenmatch, coverage 91%.

This must currently be a gui test because ParenMatch methods use
several text methods sio defined on idlelib.idle_test.mock_tk.Text.
"""
kutoka idlelib.parenmatch agiza ParenMatch
kutoka test.support agiza requires
requires('gui')

agiza unittest
kutoka unittest.mock agiza Mock
kutoka tkinter agiza Tk, Text


kundi DummyEditwin:
    eleza __init__(self, text):
        self.text = text
        self.indentwidth = 8
        self.tabwidth = 8
        self.prompt_last_line = '>>>' # Currently sio used by parenmatch.


kundi ParenMatchTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = Tk()
        cls.root.withdraw()
        cls.text = Text(cls.root)
        cls.editwin = DummyEditwin(cls.text)
        cls.editwin.text_frame = Mock()

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text, cls.editwin
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza tearDown(self):
        self.text.delete('1.0', 'end')

    eleza get_parenmatch(self):
        pm = ParenMatch(self.editwin)
        pm.bell = lambda: Tupu
        rudisha pm

    eleza test_paren_styles(self):
        """
        Test ParenMatch with each style.
        """
        text = self.text
        pm = self.get_parenmatch()
        kila style, range1, range2 kwenye (
                ('opener', ('1.10', '1.11'), ('1.10', '1.11')),
                ('default',('1.10', '1.11'),('1.10', '1.11')),
                ('parens', ('1.14', '1.15'), ('1.15', '1.16')),
                ('expression', ('1.10', '1.15'), ('1.10', '1.16'))):
            with self.subTest(style=style):
                text.delete('1.0', 'end')
                pm.STYLE = style
                text.insert('insert', 'eleza foobar(a, b')

                pm.flash_paren_event('event')
                self.assertIn('<<parenmatch-check-restore>>', text.event_info())
                ikiwa style == 'parens':
                    self.assertTupleEqual(text.tag_nextrange('paren', '1.0'),
                                          ('1.10', '1.11'))
                self.assertTupleEqual(
                        text.tag_prevrange('paren', 'end'), range1)

                text.insert('insert', ')')
                pm.restore_event()
                self.assertNotIn('<<parenmatch-check-restore>>',
                                 text.event_info())
                self.assertEqual(text.tag_prevrange('paren', 'end'), ())

                pm.paren_closed_event('event')
                self.assertTupleEqual(
                        text.tag_prevrange('paren', 'end'), range2)

    eleza test_paren_corner(self):
        """
        Test corner cases kwenye flash_paren_event na paren_closed_event.

        These cases force conditional expression na alternate paths.
        """
        text = self.text
        pm = self.get_parenmatch()

        text.insert('insert', '# this ni a commen)')
        pm.paren_closed_event('event')

        text.insert('insert', '\ndef')
        pm.flash_paren_event('event')
        pm.paren_closed_event('event')

        text.insert('insert', ' a, *arg)')
        pm.paren_closed_event('event')

    eleza test_handle_restore_timer(self):
        pm = self.get_parenmatch()
        pm.restore_event = Mock()
        pm.handle_restore_timer(0)
        self.assertKweli(pm.restore_event.called)
        pm.restore_event.reset_mock()
        pm.handle_restore_timer(1)
        self.assertUongo(pm.restore_event.called)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
