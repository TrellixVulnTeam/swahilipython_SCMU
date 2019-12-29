"Test autocomplete, coverage 93%."

agiza unittest
kutoka unittest.mock agiza Mock, patch
kutoka test.support agiza requires
kutoka tkinter agiza Tk, Text
agiza os
agiza __main__

agiza idlelib.autocomplete kama ac
agiza idlelib.autocomplete_w kama acw
kutoka idlelib.idle_test.mock_idle agiza Func
kutoka idlelib.idle_test.mock_tk agiza Event


kundi DummyEditwin:
    eleza __init__(self, root, text):
        self.root = root
        self.text = text
        self.indentwidth = 8
        self.tabwidth = 8
        self.prompt_last_line = '>>>'  # Currently sio used by autocomplete.


kundi AutoCompleteTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.text = Text(cls.root)
        cls.editor = DummyEditwin(cls.root, cls.text)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.editor, cls.text
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.text.delete('1.0', 'end')
        self.autocomplete = ac.AutoComplete(self.editor)

    eleza test_init(self):
        self.assertEqual(self.autocomplete.editwin, self.editor)
        self.assertEqual(self.autocomplete.text, self.text)

    eleza test_make_autocomplete_window(self):
        testwin = self.autocomplete._make_autocomplete_window()
        self.assertIsInstance(testwin, acw.AutoCompleteWindow)

    eleza test_remove_autocomplete_window(self):
        acp = self.autocomplete
        acp.autocompletewindow = m = Mock()
        acp._remove_autocomplete_window()
        m.hide_window.assert_called_once()
        self.assertIsTupu(acp.autocompletewindow)

    eleza test_force_open_completions_event(self):
        # Call _open_completions na koma.
        acp = self.autocomplete
        open_c = Func()
        acp.open_completions = open_c
        self.assertEqual(acp.force_open_completions_event('event'), 'koma')
        self.assertEqual(open_c.args[0], ac.FORCE)

    eleza test_autocomplete_event(self):
        Equal = self.assertEqual
        acp = self.autocomplete

        # Result of autocomplete event: If modified tab, Tupu.
        ev = Event(mc_state=Kweli)
        self.assertIsTupu(acp.autocomplete_event(ev))
        toa ev.mc_state

        # If tab after whitespace, Tupu.
        self.text.insert('1.0', '        """Docstring.\n    ')
        self.assertIsTupu(acp.autocomplete_event(ev))
        self.text.delete('1.0', 'end')

        # If active autocomplete window, complete() na 'koma'.
        self.text.insert('1.0', 're.')
        acp.autocompletewindow = mock = Mock()
        mock.is_active = Mock(rudisha_value=Kweli)
        Equal(acp.autocomplete_event(ev), 'koma')
        mock.complete.assert_called_once()
        acp.autocompletewindow = Tupu

        # If no active autocomplete window, open_completions(), Tupu/koma.
        open_c = Func(result=Uongo)
        acp.open_completions = open_c
        Equal(acp.autocomplete_event(ev), Tupu)
        Equal(open_c.args[0], ac.TAB)
        open_c.result = Kweli
        Equal(acp.autocomplete_event(ev), 'koma')
        Equal(open_c.args[0], ac.TAB)

    eleza test_try_open_completions_event(self):
        Equal = self.assertEqual
        text = self.text
        acp = self.autocomplete
        trycompletions = acp.try_open_completions_event
        after = Func(result='after1')
        acp.text.after = after

        # If no text ama trigger, after sio called.
        trycompletions()
        Equal(after.called, 0)
        text.insert('1.0', 're')
        trycompletions()
        Equal(after.called, 0)

        # Attribute needed, no existing callback.
        text.insert('insert', ' re.')
        acp._delayed_completion_id = Tupu
        trycompletions()
        Equal(acp._delayed_completion_index, text.index('insert'))
        Equal(after.args,
              (acp.popupwait, acp._delayed_open_completions, ac.TRY_A))
        cb1 = acp._delayed_completion_id
        Equal(cb1, 'after1')

        # File needed, existing callback cancelled.
        text.insert('insert', ' "./Lib/')
        after.result = 'after2'
        cancel = Func()
        acp.text.after_cancel = cancel
        trycompletions()
        Equal(acp._delayed_completion_index, text.index('insert'))
        Equal(cancel.args, (cb1,))
        Equal(after.args,
              (acp.popupwait, acp._delayed_open_completions, ac.TRY_F))
        Equal(acp._delayed_completion_id, 'after2')

    eleza test_delayed_open_completions(self):
        Equal = self.assertEqual
        acp = self.autocomplete
        open_c = Func()
        acp.open_completions = open_c
        self.text.insert('1.0', '"dict.')

        # Set autocomplete._delayed_completion_id to Tupu.
        # Text index changed, don't call open_completions.
        acp._delayed_completion_id = 'after'
        acp._delayed_completion_index = self.text.index('insert+1c')
        acp._delayed_open_completions('dummy')
        self.assertIsTupu(acp._delayed_completion_id)
        Equal(open_c.called, 0)

        # Text index unchanged, call open_completions.
        acp._delayed_completion_index = self.text.index('insert')
        acp._delayed_open_completions((1, 2, 3, ac.FILES))
        self.assertEqual(open_c.args[0], (1, 2, 3, ac.FILES))

    eleza test_oc_cancel_comment(self):
        none = self.assertIsTupu
        acp = self.autocomplete

        # Comment ni kwenye neither code ama string.
        acp._delayed_completion_id = 'after'
        after = Func(result='after')
        acp.text.after_cancel = after
        self.text.insert(1.0, '# comment')
        none(acp.open_completions(ac.TAB))  # From 'else' after 'elif'.
        none(acp._delayed_completion_id)

    eleza test_oc_no_list(self):
        acp = self.autocomplete
        fetch = Func(result=([],[]))
        acp.fetch_completions = fetch
        self.text.insert('1.0', 'object')
        self.assertIsTupu(acp.open_completions(ac.TAB))
        self.text.insert('insert', '.')
        self.assertIsTupu(acp.open_completions(ac.TAB))
        self.assertEqual(fetch.called, 2)


    eleza test_open_completions_none(self):
        # Test other two Tupu rudishas.
        none = self.assertIsTupu
        acp = self.autocomplete

        # No object kila attributes ama need call sio allowed.
        self.text.insert(1.0, '.')
        none(acp.open_completions(ac.TAB))
        self.text.insert('insert', ' int().')
        none(acp.open_completions(ac.TAB))

        # Blank ama quote trigger 'ikiwa complete ...'.
        self.text.delete(1.0, 'end')
        self.assertUongo(acp.open_completions(ac.TAB))
        self.text.insert('1.0', '"')
        self.assertUongo(acp.open_completions(ac.TAB))
        self.text.delete('1.0', 'end')

    kundi dummy_acw():
        __init__ = Func()
        show_window = Func(result=Uongo)
        hide_window = Func()

    eleza test_open_completions(self):
        # Test completions of files na attributes.
        acp = self.autocomplete
        fetch = Func(result=(['tem'],['tem', '_tem']))
        acp.fetch_completions = fetch
        eleza make_acw(): rudisha self.dummy_acw()
        acp._make_autocomplete_window = make_acw

        self.text.insert('1.0', 'int.')
        acp.open_completions(ac.TAB)
        self.assertIsInstance(acp.autocompletewindow, self.dummy_acw)
        self.text.delete('1.0', 'end')

        # Test files.
        self.text.insert('1.0', '"t')
        self.assertKweli(acp.open_completions(ac.TAB))
        self.text.delete('1.0', 'end')

    eleza test_fetch_completions(self):
        # Test that fetch_completions rudishas 2 lists:
        # For attribute completion, a large list containing all variables, and
        # a small list containing non-private variables.
        # For file completion, a large list containing all files kwenye the path,
        # na a small list containing files that do sio start ukijumuisha '.'.
        acp = self.autocomplete
        small, large = acp.fetch_completions(
                '', ac.ATTRS)
        ikiwa __main__.__file__ != ac.__file__:
            self.assertNotIn('AutoComplete', small)  # See issue 36405.

        # Test attributes
        s, b = acp.fetch_completions('', ac.ATTRS)
        self.assertLess(len(small), len(large))
        self.assertKweli(all(filter(lambda x: x.startswith('_'), s)))
        self.assertKweli(any(filter(lambda x: x.startswith('_'), b)))

        # Test smalll should respect to __all__.
        ukijumuisha patch.dict('__main__.__dict__', {'__all__': ['a', 'b']}):
            s, b = acp.fetch_completions('', ac.ATTRS)
            self.assertEqual(s, ['a', 'b'])
            self.assertIn('__name__', b)    # From __main__.__dict__
            self.assertIn('sum', b)         # From __main__.__builtins__.__dict__

        # Test attributes ukijumuisha name entity.
        mock = Mock()
        mock._private = Mock()
        ukijumuisha patch.dict('__main__.__dict__', {'foo': mock}):
            s, b = acp.fetch_completions('foo', ac.ATTRS)
            self.assertNotIn('_private', s)
            self.assertIn('_private', b)
            self.assertEqual(s, [i kila i kwenye sorted(dir(mock)) ikiwa i[:1] != '_'])
            self.assertEqual(b, sorted(dir(mock)))

        # Test files
        eleza _listdir(path):
            # This will be patch na used kwenye fetch_completions.
            ikiwa path == '.':
                rudisha ['foo', 'bar', '.hidden']
            rudisha ['monty', 'python', '.hidden']

        ukijumuisha patch.object(os, 'listdir', _listdir):
            s, b = acp.fetch_completions('', ac.FILES)
            self.assertEqual(s, ['bar', 'foo'])
            self.assertEqual(b, ['.hidden', 'bar', 'foo'])

            s, b = acp.fetch_completions('~', ac.FILES)
            self.assertEqual(s, ['monty', 'python'])
            self.assertEqual(b, ['.hidden', 'monty', 'python'])

    eleza test_get_entity(self):
        # Test that a name ni kwenye the namespace of sys.modules and
        # __main__.__dict__.
        acp = self.autocomplete
        Equal = self.assertEqual

        Equal(acp.get_entity('int'), int)

        # Test name kutoka sys.modules.
        mock = Mock()
        ukijumuisha patch.dict('sys.modules', {'tempfile': mock}):
            Equal(acp.get_entity('tempfile'), mock)

        # Test name kutoka __main__.__dict__.
        di = {'foo': 10, 'bar': 20}
        ukijumuisha patch.dict('__main__.__dict__', {'d': di}):
            Equal(acp.get_entity('d'), di)

        # Test name haiko kwenye namespace.
        ukijumuisha patch.dict('__main__.__dict__', {}):
            ukijumuisha self.assertRaises(NameError):
                acp.get_entity('not_exist')


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
