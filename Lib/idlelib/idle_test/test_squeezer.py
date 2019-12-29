"Test squeezer, coverage 95%"

kutoka collections agiza namedtuple
kutoka textwrap agiza dedent
kutoka tkinter agiza Text, Tk
agiza unittest
kutoka unittest.mock agiza Mock, NonCallableMagicMock, patch, sentinel, ANY
kutoka test.support agiza requires

kutoka idlelib.config agiza idleConf
kutoka idlelib.squeezer agiza count_lines_with_wrapping, ExpandingButton, \
    Squeezer
kutoka idlelib agiza macosx
kutoka idlelib.textview agiza view_text
kutoka idlelib.tooltip agiza Hovertip
kutoka idlelib.pyshell agiza PyShell


SENTINEL_VALUE = sentinel.SENTINEL_VALUE


eleza get_test_tk_root(test_instance):
    """Helper kila tests: Create a root Tk object."""
    requires('gui')
    root = Tk()
    root.withdraw()

    eleza cleanup_root():
        root.update_idletasks()
        root.destroy()
    test_instance.addCleanup(cleanup_root)

    rudisha root


kundi CountLinesTest(unittest.TestCase):
    """Tests kila the count_lines_with_wrapping function."""
    eleza check(self, expected, text, linewidth):
        rudisha self.assertEqual(
            expected,
            count_lines_with_wrapping(text, linewidth),
        )

    eleza test_count_empty(self):
        """Test with an empty string."""
        self.assertEqual(count_lines_with_wrapping(""), 0)

    eleza test_count_begins_with_empty_line(self):
        """Test with a string which begins with a newline."""
        self.assertEqual(count_lines_with_wrapping("\ntext"), 2)

    eleza test_count_ends_with_empty_line(self):
        """Test with a string which ends with a newline."""
        self.assertEqual(count_lines_with_wrapping("text\n"), 1)

    eleza test_count_several_lines(self):
        """Test with several lines of text."""
        self.assertEqual(count_lines_with_wrapping("1\n2\n3\n"), 3)

    eleza test_empty_lines(self):
        self.check(expected=1, text='\n', linewidth=80)
        self.check(expected=2, text='\n\n', linewidth=80)
        self.check(expected=10, text='\n' * 10, linewidth=80)

    eleza test_long_line(self):
        self.check(expected=3, text='a' * 200, linewidth=80)
        self.check(expected=3, text='a' * 200 + '\n', linewidth=80)

    eleza test_several_lines_different_lengths(self):
        text = dedent("""\
            13 characters
            43 ni the number of characters on this line

            7 chars
            13 characters""")
        self.check(expected=5, text=text, linewidth=80)
        self.check(expected=5, text=text + '\n', linewidth=80)
        self.check(expected=6, text=text, linewidth=40)
        self.check(expected=7, text=text, linewidth=20)
        self.check(expected=11, text=text, linewidth=10)


kundi SqueezerTest(unittest.TestCase):
    """Tests kila the Squeezer class."""
    eleza make_mock_editor_window(self, with_text_widget=Uongo):
        """Create a mock EditorWindow instance."""
        editwin = NonCallableMagicMock()
        editwin.width = 80

        ikiwa with_text_widget:
            editwin.root = get_test_tk_root(self)
            text_widget = self.make_text_widget(root=editwin.root)
            editwin.text = editwin.per.bottom = text_widget

        rudisha editwin

    eleza make_squeezer_instance(self, editor_window=Tupu):
        """Create an actual Squeezer instance with a mock EditorWindow."""
        ikiwa editor_window ni Tupu:
            editor_window = self.make_mock_editor_window()
        squeezer = Squeezer(editor_window)
        rudisha squeezer

    eleza make_text_widget(self, root=Tupu):
        ikiwa root ni Tupu:
            root = get_test_tk_root(self)
        text_widget = Text(root)
        text_widget["font"] = ('Courier', 10)
        text_widget.mark_set("iomark", "1.0")
        rudisha text_widget

    eleza set_idleconf_option_with_cleanup(self, configType, section, option, value):
        prev_val = idleConf.GetOption(configType, section, option)
        idleConf.SetOption(configType, section, option, value)
        self.addCleanup(idleConf.SetOption,
                        configType, section, option, prev_val)

    eleza test_count_lines(self):
        """Test Squeezer.count_lines() with various inputs."""
        editwin = self.make_mock_editor_window()
        squeezer = self.make_squeezer_instance(editwin)

        kila text_code, line_width, expected kwenye [
            (r"'\n'", 80, 1),
            (r"'\n' * 3", 80, 3),
            (r"'a' * 40 + '\n'", 80, 1),
            (r"'a' * 80 + '\n'", 80, 1),
            (r"'a' * 200 + '\n'", 80, 3),
            (r"'aa\t' * 20", 80, 2),
            (r"'aa\t' * 21", 80, 3),
            (r"'aa\t' * 20", 40, 4),
        ]:
            with self.subTest(text_code=text_code,
                              line_width=line_width,
                              expected=expected):
                text = eval(text_code)
                with patch.object(editwin, 'width', line_width):
                    self.assertEqual(squeezer.count_lines(text), expected)

    eleza test_init(self):
        """Test the creation of Squeezer instances."""
        editwin = self.make_mock_editor_window()
        squeezer = self.make_squeezer_instance(editwin)
        self.assertIs(squeezer.editwin, editwin)
        self.assertEqual(squeezer.expandingbuttons, [])

    eleza test_write_no_tags(self):
        """Test Squeezer's overriding of the EditorWindow's write() method."""
        editwin = self.make_mock_editor_window()
        kila text kwenye ['', 'TEXT', 'LONG TEXT' * 1000, 'MANY_LINES\n' * 100]:
            editwin.write = orig_write = Mock(rudisha_value=SENTINEL_VALUE)
            squeezer = self.make_squeezer_instance(editwin)

            self.assertEqual(squeezer.editwin.write(text, ()), SENTINEL_VALUE)
            self.assertEqual(orig_write.call_count, 1)
            orig_write.assert_called_with(text, ())
            self.assertEqual(len(squeezer.expandingbuttons), 0)

    eleza test_write_not_stdout(self):
        """Test Squeezer's overriding of the EditorWindow's write() method."""
        kila text kwenye ['', 'TEXT', 'LONG TEXT' * 1000, 'MANY_LINES\n' * 100]:
            editwin = self.make_mock_editor_window()
            editwin.write.rudisha_value = SENTINEL_VALUE
            orig_write = editwin.write
            squeezer = self.make_squeezer_instance(editwin)

            self.assertEqual(squeezer.editwin.write(text, "stderr"),
                              SENTINEL_VALUE)
            self.assertEqual(orig_write.call_count, 1)
            orig_write.assert_called_with(text, "stderr")
            self.assertEqual(len(squeezer.expandingbuttons), 0)

    eleza test_write_stdout(self):
        """Test Squeezer's overriding of the EditorWindow's write() method."""
        editwin = self.make_mock_editor_window()

        kila text kwenye ['', 'TEXT']:
            editwin.write = orig_write = Mock(rudisha_value=SENTINEL_VALUE)
            squeezer = self.make_squeezer_instance(editwin)
            squeezer.auto_squeeze_min_lines = 50

            self.assertEqual(squeezer.editwin.write(text, "stdout"),
                             SENTINEL_VALUE)
            self.assertEqual(orig_write.call_count, 1)
            orig_write.assert_called_with(text, "stdout")
            self.assertEqual(len(squeezer.expandingbuttons), 0)

        kila text kwenye ['LONG TEXT' * 1000, 'MANY_LINES\n' * 100]:
            editwin.write = orig_write = Mock(rudisha_value=SENTINEL_VALUE)
            squeezer = self.make_squeezer_instance(editwin)
            squeezer.auto_squeeze_min_lines = 50

            self.assertEqual(squeezer.editwin.write(text, "stdout"), Tupu)
            self.assertEqual(orig_write.call_count, 0)
            self.assertEqual(len(squeezer.expandingbuttons), 1)

    eleza test_auto_squeeze(self):
        """Test that the auto-squeezing creates an ExpandingButton properly."""
        editwin = self.make_mock_editor_window(with_text_widget=Kweli)
        text_widget = editwin.text
        squeezer = self.make_squeezer_instance(editwin)
        squeezer.auto_squeeze_min_lines = 5
        squeezer.count_lines = Mock(rudisha_value=6)

        editwin.write('TEXT\n'*6, "stdout")
        self.assertEqual(text_widget.get('1.0', 'end'), '\n')
        self.assertEqual(len(squeezer.expandingbuttons), 1)

    eleza test_squeeze_current_text_event(self):
        """Test the squeeze_current_text event."""
        # Squeezing text should work kila both stdout na stderr.
        kila tag_name kwenye ["stdout", "stderr"]:
            editwin = self.make_mock_editor_window(with_text_widget=Kweli)
            text_widget = editwin.text
            squeezer = self.make_squeezer_instance(editwin)
            squeezer.count_lines = Mock(rudisha_value=6)

            # Prepare some text kwenye the Text widget.
            text_widget.insert("1.0", "SOME\nTEXT\n", tag_name)
            text_widget.mark_set("insert", "1.0")
            self.assertEqual(text_widget.get('1.0', 'end'), 'SOME\nTEXT\n\n')

            self.assertEqual(len(squeezer.expandingbuttons), 0)

            # Test squeezing the current text.
            retval = squeezer.squeeze_current_text_event(event=Mock())
            self.assertEqual(retval, "koma")
            self.assertEqual(text_widget.get('1.0', 'end'), '\n\n')
            self.assertEqual(len(squeezer.expandingbuttons), 1)
            self.assertEqual(squeezer.expandingbuttons[0].s, 'SOME\nTEXT')

            # Test that expanding the squeezed text works na afterwards
            # the Text widget contains the original text.
            squeezer.expandingbuttons[0].expand(event=Mock())
            self.assertEqual(text_widget.get('1.0', 'end'), 'SOME\nTEXT\n\n')
            self.assertEqual(len(squeezer.expandingbuttons), 0)

    eleza test_squeeze_current_text_event_no_allowed_tags(self):
        """Test that the event doesn't squeeze text without a relevant tag."""
        editwin = self.make_mock_editor_window(with_text_widget=Kweli)
        text_widget = editwin.text
        squeezer = self.make_squeezer_instance(editwin)
        squeezer.count_lines = Mock(rudisha_value=6)

        # Prepare some text kwenye the Text widget.
        text_widget.insert("1.0", "SOME\nTEXT\n", "TAG")
        text_widget.mark_set("insert", "1.0")
        self.assertEqual(text_widget.get('1.0', 'end'), 'SOME\nTEXT\n\n')

        self.assertEqual(len(squeezer.expandingbuttons), 0)

        # Test squeezing the current text.
        retval = squeezer.squeeze_current_text_event(event=Mock())
        self.assertEqual(retval, "koma")
        self.assertEqual(text_widget.get('1.0', 'end'), 'SOME\nTEXT\n\n')
        self.assertEqual(len(squeezer.expandingbuttons), 0)

    eleza test_squeeze_text_before_existing_squeezed_text(self):
        """Test squeezing text before existing squeezed text."""
        editwin = self.make_mock_editor_window(with_text_widget=Kweli)
        text_widget = editwin.text
        squeezer = self.make_squeezer_instance(editwin)
        squeezer.count_lines = Mock(rudisha_value=6)

        # Prepare some text kwenye the Text widget na squeeze it.
        text_widget.insert("1.0", "SOME\nTEXT\n", "stdout")
        text_widget.mark_set("insert", "1.0")
        squeezer.squeeze_current_text_event(event=Mock())
        self.assertEqual(len(squeezer.expandingbuttons), 1)

        # Test squeezing the current text.
        text_widget.insert("1.0", "MORE\nSTUFF\n", "stdout")
        text_widget.mark_set("insert", "1.0")
        retval = squeezer.squeeze_current_text_event(event=Mock())
        self.assertEqual(retval, "koma")
        self.assertEqual(text_widget.get('1.0', 'end'), '\n\n\n')
        self.assertEqual(len(squeezer.expandingbuttons), 2)
        self.assertKweli(text_widget.compare(
            squeezer.expandingbuttons[0],
            '<',
            squeezer.expandingbuttons[1],
        ))

    eleza test_reload(self):
        """Test the reload() class-method."""
        editwin = self.make_mock_editor_window(with_text_widget=Kweli)
        squeezer = self.make_squeezer_instance(editwin)

        orig_auto_squeeze_min_lines = squeezer.auto_squeeze_min_lines

        # Increase auto-squeeze-min-lines.
        new_auto_squeeze_min_lines = orig_auto_squeeze_min_lines + 10
        self.set_idleconf_option_with_cleanup(
            'main', 'PyShell', 'auto-squeeze-min-lines',
            str(new_auto_squeeze_min_lines))

        Squeezer.reload()
        self.assertEqual(squeezer.auto_squeeze_min_lines,
                         new_auto_squeeze_min_lines)

    eleza test_reload_no_squeezer_instances(self):
        """Test that Squeezer.reload() runs without any instances existing."""
        Squeezer.reload()


kundi ExpandingButtonTest(unittest.TestCase):
    """Tests kila the ExpandingButton class."""
    # In these tests the squeezer instance ni a mock, but actual tkinter
    # Text na Button instances are created.
    eleza make_mock_squeezer(self):
        """Helper kila tests: Create a mock Squeezer object."""
        root = get_test_tk_root(self)
        squeezer = Mock()
        squeezer.editwin.text = Text(root)

        # Set default values kila the configuration settings.
        squeezer.auto_squeeze_min_lines = 50
        rudisha squeezer

    @patch('idlelib.squeezer.Hovertip', autospec=Hovertip)
    eleza test_init(self, MockHovertip):
        """Test the simplest creation of an ExpandingButton."""
        squeezer = self.make_mock_squeezer()
        text_widget = squeezer.editwin.text

        expandingbutton = ExpandingButton('TEXT', 'TAGS', 50, squeezer)
        self.assertEqual(expandingbutton.s, 'TEXT')

        # Check that the underlying tkinter.Button ni properly configured.
        self.assertEqual(expandingbutton.master, text_widget)
        self.assertKweli('50 lines' kwenye expandingbutton.cget('text'))

        # Check that the text widget still contains no text.
        self.assertEqual(text_widget.get('1.0', 'end'), '\n')

        # Check that the mouse events are bound.
        self.assertIn('<Double-Button-1>', expandingbutton.bind())
        right_button_code = '<Button-%s>' % ('2' ikiwa macosx.isAquaTk() else '3')
        self.assertIn(right_button_code, expandingbutton.bind())

        # Check that ToolTip was called once, with appropriate values.
        self.assertEqual(MockHovertip.call_count, 1)
        MockHovertip.assert_called_with(expandingbutton, ANY, hover_delay=ANY)

        # Check that 'right-click' appears kwenye the tooltip text.
        tooltip_text = MockHovertip.call_args[0][1]
        self.assertIn('right-click', tooltip_text.lower())

    eleza test_expand(self):
        """Test the expand event."""
        squeezer = self.make_mock_squeezer()
        expandingbutton = ExpandingButton('TEXT', 'TAGS', 50, squeezer)

        # Insert the button into the text widget
        # (this ni normally done by the Squeezer class).
        text_widget = expandingbutton.text
        text_widget.window_create("1.0", window=expandingbutton)

        # Set base_text to the text widget, so that changes are actually
        # made to it (by ExpandingButton) na we can inspect these
        # changes afterwards.
        expandingbutton.base_text = expandingbutton.text

        # trigger the expand event
        retval = expandingbutton.expand(event=Mock())
        self.assertEqual(retval, Tupu)

        # Check that the text was inserted into the text widget.
        self.assertEqual(text_widget.get('1.0', 'end'), 'TEXT\n')

        # Check that the 'TAGS' tag was set on the inserted text.
        text_end_index = text_widget.index('end-1c')
        self.assertEqual(text_widget.get('1.0', text_end_index), 'TEXT')
        self.assertEqual(text_widget.tag_nextrange('TAGS', '1.0'),
                          ('1.0', text_end_index))

        # Check that the button removed itself kutoka squeezer.expandingbuttons.
        self.assertEqual(squeezer.expandingbuttons.remove.call_count, 1)
        squeezer.expandingbuttons.remove.assert_called_with(expandingbutton)

    eleza test_expand_dangerous_oupput(self):
        """Test that expanding very long output asks user kila confirmation."""
        squeezer = self.make_mock_squeezer()
        text = 'a' * 10**5
        expandingbutton = ExpandingButton(text, 'TAGS', 50, squeezer)
        expandingbutton.set_is_dangerous()
        self.assertKweli(expandingbutton.is_dangerous)

        # Insert the button into the text widget
        # (this ni normally done by the Squeezer class).
        text_widget = expandingbutton.text
        text_widget.window_create("1.0", window=expandingbutton)

        # Set base_text to the text widget, so that changes are actually
        # made to it (by ExpandingButton) na we can inspect these
        # changes afterwards.
        expandingbutton.base_text = expandingbutton.text

        # Patch the message box module to always rudisha Uongo.
        with patch('idlelib.squeezer.tkMessageBox') kama mock_msgbox:
            mock_msgbox.askokcancel.rudisha_value = Uongo
            mock_msgbox.askyesno.rudisha_value = Uongo
            # Trigger the expand event.
            retval = expandingbutton.expand(event=Mock())

        # Check that the event chain was broken na no text was inserted.
        self.assertEqual(retval, 'koma')
        self.assertEqual(expandingbutton.text.get('1.0', 'end-1c'), '')

        # Patch the message box module to always rudisha Kweli.
        with patch('idlelib.squeezer.tkMessageBox') kama mock_msgbox:
            mock_msgbox.askokcancel.rudisha_value = Kweli
            mock_msgbox.askyesno.rudisha_value = Kweli
            # Trigger the expand event.
            retval = expandingbutton.expand(event=Mock())

        # Check that the event chain wasn't broken na the text was inserted.
        self.assertEqual(retval, Tupu)
        self.assertEqual(expandingbutton.text.get('1.0', 'end-1c'), text)

    eleza test_copy(self):
        """Test the copy event."""
        # Testing with the actual clipboard proved problematic, so this
        # test replaces the clipboard manipulation functions with mocks
        # na checks that they are called appropriately.
        squeezer = self.make_mock_squeezer()
        expandingbutton = ExpandingButton('TEXT', 'TAGS', 50, squeezer)
        expandingbutton.clipboard_clear = Mock()
        expandingbutton.clipboard_append = Mock()

        # Trigger the copy event.
        retval = expandingbutton.copy(event=Mock())
        self.assertEqual(retval, Tupu)

        # Vheck that the expanding button called clipboard_clear() and
        # clipboard_append('TEXT') once each.
        self.assertEqual(expandingbutton.clipboard_clear.call_count, 1)
        self.assertEqual(expandingbutton.clipboard_append.call_count, 1)
        expandingbutton.clipboard_append.assert_called_with('TEXT')

    eleza test_view(self):
        """Test the view event."""
        squeezer = self.make_mock_squeezer()
        expandingbutton = ExpandingButton('TEXT', 'TAGS', 50, squeezer)
        expandingbutton.selection_own = Mock()

        with patch('idlelib.squeezer.view_text', autospec=view_text)\
                kama mock_view_text:
            # Trigger the view event.
            expandingbutton.view(event=Mock())

            # Check that the expanding button called view_text.
            self.assertEqual(mock_view_text.call_count, 1)

            # Check that the proper text was pitaed.
            self.assertEqual(mock_view_text.call_args[0][2], 'TEXT')

    eleza test_rmenu(self):
        """Test the context menu."""
        squeezer = self.make_mock_squeezer()
        expandingbutton = ExpandingButton('TEXT', 'TAGS', 50, squeezer)
        with patch('tkinter.Menu') kama mock_Menu:
            mock_menu = Mock()
            mock_Menu.rudisha_value = mock_menu
            mock_event = Mock()
            mock_event.x = 10
            mock_event.y = 10
            expandingbutton.context_menu_event(event=mock_event)
            self.assertEqual(mock_menu.add_command.call_count,
                             len(expandingbutton.rmenu_specs))
            kila label, *data kwenye expandingbutton.rmenu_specs:
                mock_menu.add_command.assert_any_call(label=label, command=ANY)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
