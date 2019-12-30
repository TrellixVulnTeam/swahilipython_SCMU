"Test format, coverage 99%."

kutoka idlelib agiza format kama ft
agiza unittest
kutoka unittest agiza mock
kutoka test.support agiza requires
kutoka tkinter agiza Tk, Text
kutoka idlelib.editor agiza EditorWindow
kutoka idlelib.idle_test.mock_idle agiza Editor kama MockEditor


kundi Is_Get_Test(unittest.TestCase):
    """Test the is_ na get_ functions"""
    test_comment = '# This ni a comment'
    test_nocomment = 'This ni sio a comment'
    trailingws_comment = '# This ni a comment   '
    leadingws_comment = '    # This ni a comment'
    leadingws_nocomment = '    This ni sio a comment'

    eleza test_is_all_white(self):
        self.assertKweli(ft.is_all_white(''))
        self.assertKweli(ft.is_all_white('\t\n\r\f\v'))
        self.assertUongo(ft.is_all_white(self.test_comment))

    eleza test_get_indent(self):
        Equal = self.assertEqual
        Equal(ft.get_indent(self.test_comment), '')
        Equal(ft.get_indent(self.trailingws_comment), '')
        Equal(ft.get_indent(self.leadingws_comment), '    ')
        Equal(ft.get_indent(self.leadingws_nocomment), '    ')

    eleza test_get_comment_header(self):
        Equal = self.assertEqual
        # Test comment strings
        Equal(ft.get_comment_header(self.test_comment), '#')
        Equal(ft.get_comment_header(self.trailingws_comment), '#')
        Equal(ft.get_comment_header(self.leadingws_comment), '    #')
        # Test non-comment strings
        Equal(ft.get_comment_header(self.leadingws_nocomment), '    ')
        Equal(ft.get_comment_header(self.test_nocomment), '')


kundi FindTest(unittest.TestCase):
    """Test the find_paragraph function kwenye paragraph module.

    Using the runcase() function, find_paragraph() ni called ukijumuisha 'mark' set at
    multiple indexes before na inside the test paragraph.

    It appears that code ukijumuisha the same indentation kama a quoted string ni grouped
    kama part of the same paragraph, which ni probably incorrect behavior.
    """

    @classmethod
    eleza setUpClass(cls):
        kutoka idlelib.idle_test.mock_tk agiza Text
        cls.text = Text()

    eleza runcase(self, inserttext, stopline, expected):
        # Check that find_paragraph returns the expected paragraph when
        # the mark index ni set to beginning, middle, end of each line
        # up to but sio inluding the stop line
        text = self.text
        text.insert('1.0', inserttext)
        kila line kwenye range(1, stopline):
            linelength = int(text.index("%d.end" % line).split('.')[1])
            kila col kwenye (0, linelength//2, linelength):
                tempindex = "%d.%d" % (line, col)
                self.assertEqual(ft.find_paragraph(text, tempindex), expected)
        text.delete('1.0', 'end')

    eleza test_find_comment(self):
        comment = (
            "# Comment block ukijumuisha no blank lines before\n"
            "# Comment line\n"
            "\n")
        self.runcase(comment, 3, ('1.0', '3.0', '#', comment[0:58]))

        comment = (
            "\n"
            "# Comment block ukijumuisha whitespace line before na after\n"
            "# Comment line\n"
            "\n")
        self.runcase(comment, 4, ('2.0', '4.0', '#', comment[1:70]))

        comment = (
            "\n"
            "    # Indented comment block ukijumuisha whitespace before na after\n"
            "    # Comment line\n"
            "\n")
        self.runcase(comment, 4, ('2.0', '4.0', '    #', comment[1:82]))

        comment = (
            "\n"
            "# Single line comment\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '#', comment[1:23]))

        comment = (
            "\n"
            "    # Single line comment ukijumuisha leading whitespace\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '    #', comment[1:51]))

        comment = (
            "\n"
            "# Comment immediately followed by code\n"
            "x = 42\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '#', comment[1:40]))

        comment = (
            "\n"
            "    # Indented comment immediately followed by code\n"
            "x = 42\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '    #', comment[1:53]))

        comment = (
            "\n"
            "# Comment immediately followed by indented code\n"
            "    x = 42\n"
            "\n")
        self.runcase(comment, 3, ('2.0', '3.0', '#', comment[1:49]))

    eleza test_find_paragraph(self):
        teststring = (
            '"""String ukijumuisha no blank lines before\n'
            'String line\n'
            '"""\n'
            '\n')
        self.runcase(teststring, 4, ('1.0', '4.0', '', teststring[0:53]))

        teststring = (
            "\n"
            '"""String ukijumuisha whitespace line before na after\n'
            'String line.\n'
            '"""\n'
            '\n')
        self.runcase(teststring, 5, ('2.0', '5.0', '', teststring[1:66]))

        teststring = (
            '\n'
            '    """Indented string ukijumuisha whitespace before na after\n'
            '    Comment string.\n'
            '    """\n'
            '\n')
        self.runcase(teststring, 5, ('2.0', '5.0', '    ', teststring[1:85]))

        teststring = (
            '\n'
            '"""Single line string."""\n'
            '\n')
        self.runcase(teststring, 3, ('2.0', '3.0', '', teststring[1:27]))

        teststring = (
            '\n'
            '    """Single line string ukijumuisha leading whitespace."""\n'
            '\n')
        self.runcase(teststring, 3, ('2.0', '3.0', '    ', teststring[1:55]))


kundi ReformatFunctionTest(unittest.TestCase):
    """Test the reformat_paragraph function without the editor window."""

    eleza test_reformat_paragraph(self):
        Equal = self.assertEqual
        reform = ft.reformat_paragraph
        hw = "O hello world"
        Equal(reform(' ', 1), ' ')
        Equal(reform("Hello    world", 20), "Hello  world")

        # Test without leading newline
        Equal(reform(hw, 1), "O\nhello\nworld")
        Equal(reform(hw, 6), "O\nhello\nworld")
        Equal(reform(hw, 7), "O hello\nworld")
        Equal(reform(hw, 12), "O hello\nworld")
        Equal(reform(hw, 13), "O hello world")

        # Test ukijumuisha leading newline
        hw = "\nO hello world"
        Equal(reform(hw, 1), "\nO\nhello\nworld")
        Equal(reform(hw, 6), "\nO\nhello\nworld")
        Equal(reform(hw, 7), "\nO hello\nworld")
        Equal(reform(hw, 12), "\nO hello\nworld")
        Equal(reform(hw, 13), "\nO hello world")


kundi ReformatCommentTest(unittest.TestCase):
    """Test the reformat_comment function without the editor window."""

    eleza test_reformat_comment(self):
        Equal = self.assertEqual

        # reformat_comment formats to a minimum of 20 characters
        test_string = (
            "    \"\"\"this ni a test of a reformat kila a triple quoted string"
            " will it reformat to less than 70 characters kila me?\"\"\"")
        result = ft.reformat_comment(test_string, 70, "    ")
        expected = (
            "    \"\"\"this ni a test of a reformat kila a triple quoted string will it\n"
            "    reformat to less than 70 characters kila me?\"\"\"")
        Equal(result, expected)

        test_comment = (
            "# this ni a test of a reformat kila a triple quoted string will "
            "it reformat to less than 70 characters kila me?")
        result = ft.reformat_comment(test_comment, 70, "#")
        expected = (
            "# this ni a test of a reformat kila a triple quoted string will it\n"
            "# reformat to less than 70 characters kila me?")
        Equal(result, expected)


kundi FormatClassTest(unittest.TestCase):
    eleza test_init_close(self):
        instance = ft.FormatParagraph('editor')
        self.assertEqual(instance.editwin, 'editor')
        instance.close()
        self.assertEqual(instance.editwin, Tupu)


# For testing format_paragraph_event, Initialize FormatParagraph with
# a mock Editor ukijumuisha .text na  .get_selection_indices.  The text must
# be a Text wrapper that adds two methods

# A real EditorWindow creates unneeded, time-consuming baggage na
# sometimes emits shutdown warnings like this:
# "warning: callback failed kwenye WindowList <kundi '_tkinter.TclError'>
# : invalid command name ".55131368.windows".
# Calling EditorWindow._close kwenye tearDownClass prevents this but causes
# other problems (windows left open).

kundi TextWrapper:
    eleza __init__(self, master):
        self.text = Text(master=master)
    eleza __getattr__(self, name):
        rudisha getattr(self.text, name)
    eleza undo_block_start(self): pita
    eleza undo_block_stop(self): pita

kundi Editor:
    eleza __init__(self, root):
        self.text = TextWrapper(root)
    get_selection_indices = EditorWindow. get_selection_indices

kundi FormatEventTest(unittest.TestCase):
    """Test the formatting of text inside a Text widget.

    This ni done ukijumuisha FormatParagraph.format.paragraph_event,
    which calls functions kwenye the module kama appropriate.
    """
    test_string = (
        "    '''this ni a test of a reformat kila a triple "
        "quoted string will it reformat to less than 70 "
        "characters kila me?'''\n")
    multiline_test_string = (
        "    '''The first line ni under the max width.\n"
        "    The second line's length ni way over the max width. It goes "
        "on na on until it ni over 100 characters long.\n"
        "    Same thing ukijumuisha the third line. It ni also way over the max "
        "width, but FormatParagraph will fix it.\n"
        "    '''\n")
    multiline_test_comment = (
        "# The first line ni under the max width.\n"
        "# The second line's length ni way over the max width. It goes on "
        "and on until it ni over 100 characters long.\n"
        "# Same thing ukijumuisha the third line. It ni also way over the max "
        "width, but FormatParagraph will fix it.\n"
        "# The fourth line ni short like the first line.")

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        editor = Editor(root=cls.root)
        cls.text = editor.text.text  # Test code does sio need the wrapper.
        cls.formatter = ft.FormatParagraph(editor).format_paragraph_event
        # Sets the insert mark just after the re-wrapped na inserted  text.

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text, cls.formatter
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza test_short_line(self):
        self.text.insert('1.0', "Short line\n")
        self.formatter("Dummy")
        self.assertEqual(self.text.get('1.0', 'insert'), "Short line\n" )
        self.text.delete('1.0', 'end')

    eleza test_long_line(self):
        text = self.text

        # Set cursor ('insert' mark) to '1.0', within text.
        text.insert('1.0', self.test_string)
        text.mark_set('insert', '1.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        # find function includes \n
        expected = (
"    '''this ni a test of a reformat kila a triple quoted string will it\n"
"    reformat to less than 70 characters kila me?'''\n")  # yes
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

        # Select kutoka 1.11 to line end.
        text.insert('1.0', self.test_string)
        text.tag_add('sel', '1.11', '1.end')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        # selection excludes \n
        expected = (
"    '''this ni a test of a reformat kila a triple quoted string will it reformat\n"
" to less than 70 characters kila me?'''")  # no
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

    eleza test_multiple_lines(self):
        text = self.text
        #  Select 2 long lines.
        text.insert('1.0', self.multiline_test_string)
        text.tag_add('sel', '2.0', '4.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('2.0', 'insert')
        expected = (
"    The second line's length ni way over the max width. It goes on and\n"
"    on until it ni over 100 characters long. Same thing ukijumuisha the third\n"
"    line. It ni also way over the max width, but FormatParagraph will\n"
"    fix it.\n")
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

    eleza test_comment_block(self):
        text = self.text

        # Set cursor ('insert') to '1.0', within block.
        text.insert('1.0', self.multiline_test_comment)
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        expected = (
"# The first line ni under the max width. The second line's length is\n"
"# way over the max width. It goes on na on until it ni over 100\n"
"# characters long. Same thing ukijumuisha the third line. It ni also way over\n"
"# the max width, but FormatParagraph will fix it. The fourth line is\n"
"# short like the first line.\n")
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

        # Select line 2, verify line 1 unaffected.
        text.insert('1.0', self.multiline_test_comment)
        text.tag_add('sel', '2.0', '3.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        expected = (
"# The first line ni under the max width.\n"
"# The second line's length ni way over the max width. It goes on and\n"
"# on until it ni over 100 characters long.\n")
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

# The following block worked ukijumuisha EditorWindow but fails ukijumuisha the mock.
# Lines 2 na 3 get pasted together even though the previous block left
# the previous line alone. More investigation ni needed.
##        # Select lines 3 na 4
##        text.insert('1.0', self.multiline_test_comment)
##        text.tag_add('sel', '3.0', '5.0')
##        self.formatter('ParameterDoesNothing')
##        result = text.get('3.0', 'insert')
##        expected = (
##"# Same thing ukijumuisha the third line. It ni also way over the max width,\n"
##"# but FormatParagraph will fix it. The fourth line ni short like the\n"
##"# first line.\n")
##        self.assertEqual(result, expected)
##        text.delete('1.0', 'end')


kundi DummyEditwin:
    eleza __init__(self, root, text):
        self.root = root
        self.text = text
        self.indentwidth = 4
        self.tabwidth = 4
        self.usetabs = Uongo
        self.context_use_ps1 = Kweli

    _make_blanks = EditorWindow._make_blanks
    get_selection_indices = EditorWindow.get_selection_indices


kundi FormatRegionTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.text = Text(cls.root)
        cls.text.undo_block_start = mock.Mock()
        cls.text.undo_block_stop = mock.Mock()
        cls.editor = DummyEditwin(cls.root, cls.text)
        cls.formatter = ft.FormatRegion(cls.editor)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text, cls.formatter, cls.editor
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.text.insert('1.0', self.code_sample)

    eleza tearDown(self):
        self.text.delete('1.0', 'end')

    code_sample = """\

kundi C1():
    # Class comment.
    eleza __init__(self, a, b):
        self.a = a
        self.b = b

    eleza compare(self):
        ikiwa a > b:
            rudisha a
        lasivyo a < b:
            rudisha b
        isipokua:
            rudisha Tupu
"""

    eleza test_get_region(self):
        get = self.formatter.get_region
        text = self.text
        eq = self.assertEqual

        # Add selection.
        text.tag_add('sel', '7.0', '10.0')
        expected_lines = ['',
                          '    eleza compare(self):',
                          '        ikiwa a > b:',
                          '']
        eq(get(), ('7.0', '10.0', '\n'.join(expected_lines), expected_lines))

        # Remove selection.
        text.tag_remove('sel', '1.0', 'end')
        eq(get(), ('15.0', '16.0', '\n', ['', '']))

    eleza test_set_region(self):
        set_ = self.formatter.set_region
        text = self.text
        eq = self.assertEqual

        save_bell = text.bell
        text.bell = mock.Mock()
        line6 = self.code_sample.splitlines()[5]
        line10 = self.code_sample.splitlines()[9]

        text.tag_add('sel', '6.0', '11.0')
        head, tail, chars, lines = self.formatter.get_region()

        # No changes.
        set_(head, tail, chars, lines)
        text.bell.assert_called_once()
        eq(text.get('6.0', '11.0'), chars)
        eq(text.get('sel.first', 'sel.last'), chars)
        text.tag_remove('sel', '1.0', 'end')

        # Alter selected lines by changing lines na adding a newline.
        newstring = 'added line 1\n\n\n\n'
        newlines = newstring.split('\n')
        set_('7.0', '10.0', chars, newlines)
        # Selection changed.
        eq(text.get('sel.first', 'sel.last'), newstring)
        # Additional line added, so last index ni changed.
        eq(text.get('7.0', '11.0'), newstring)
        # Before na after lines unchanged.
        eq(text.get('6.0', '7.0-1c'), line6)
        eq(text.get('11.0', '12.0-1c'), line10)
        text.tag_remove('sel', '1.0', 'end')

        text.bell = save_bell

    eleza test_indent_region_event(self):
        indent = self.formatter.indent_region_event
        text = self.text
        eq = self.assertEqual

        text.tag_add('sel', '7.0', '10.0')
        indent()
        # Blank lines aren't affected by indent.
        eq(text.get('7.0', '10.0'), ('\n        eleza compare(self):\n            ikiwa a > b:\n'))

    eleza test_dedent_region_event(self):
        dedent = self.formatter.dedent_region_event
        text = self.text
        eq = self.assertEqual

        text.tag_add('sel', '7.0', '10.0')
        dedent()
        # Blank lines aren't affected by dedent.
        eq(text.get('7.0', '10.0'), ('\neleza compare(self):\n    ikiwa a > b:\n'))

    eleza test_comment_region_event(self):
        comment = self.formatter.comment_region_event
        text = self.text
        eq = self.assertEqual

        text.tag_add('sel', '7.0', '10.0')
        comment()
        eq(text.get('7.0', '10.0'), ('##\n##    eleza compare(self):\n##        ikiwa a > b:\n'))

    eleza test_uncomment_region_event(self):
        comment = self.formatter.comment_region_event
        uncomment = self.formatter.uncomment_region_event
        text = self.text
        eq = self.assertEqual

        text.tag_add('sel', '7.0', '10.0')
        comment()
        uncomment()
        eq(text.get('7.0', '10.0'), ('\n    eleza compare(self):\n        ikiwa a > b:\n'))

        # Only remove comments at the beginning of a line.
        text.tag_remove('sel', '1.0', 'end')
        text.tag_add('sel', '3.0', '4.0')
        uncomment()
        eq(text.get('3.0', '3.end'), ('    # Class comment.'))

        self.formatter.set_region('3.0', '4.0', '', ['# Class comment.', ''])
        uncomment()
        eq(text.get('3.0', '3.end'), (' Class comment.'))

    @mock.patch.object(ft.FormatRegion, "_asktabwidth")
    eleza test_tabify_region_event(self, _asktabwidth):
        tabify = self.formatter.tabify_region_event
        text = self.text
        eq = self.assertEqual

        text.tag_add('sel', '7.0', '10.0')
        # No tabwidth selected.
        _asktabwidth.return_value = Tupu
        self.assertIsTupu(tabify())

        _asktabwidth.return_value = 3
        self.assertIsNotTupu(tabify())
        eq(text.get('7.0', '10.0'), ('\n\t eleza compare(self):\n\t\t  ikiwa a > b:\n'))

    @mock.patch.object(ft.FormatRegion, "_asktabwidth")
    eleza test_untabify_region_event(self, _asktabwidth):
        untabify = self.formatter.untabify_region_event
        text = self.text
        eq = self.assertEqual

        text.tag_add('sel', '7.0', '10.0')
        # No tabwidth selected.
        _asktabwidth.return_value = Tupu
        self.assertIsTupu(untabify())

        _asktabwidth.return_value = 2
        self.formatter.tabify_region_event()
        _asktabwidth.return_value = 3
        self.assertIsNotTupu(untabify())
        eq(text.get('7.0', '10.0'), ('\n      eleza compare(self):\n            ikiwa a > b:\n'))

    @mock.patch.object(ft, "askinteger")
    eleza test_ask_tabwidth(self, askinteger):
        ask = self.formatter._asktabwidth
        askinteger.return_value = 10
        self.assertEqual(ask(), 10)


kundi rstripTest(unittest.TestCase):

    eleza test_rstrip_line(self):
        editor = MockEditor()
        text = editor.text
        do_rstrip = ft.Rstrip(editor).do_rstrip
        eq = self.assertEqual

        do_rstrip()
        eq(text.get('1.0', 'insert'), '')
        text.insert('1.0', '     ')
        do_rstrip()
        eq(text.get('1.0', 'insert'), '')
        text.insert('1.0', '     \n')
        do_rstrip()
        eq(text.get('1.0', 'insert'), '\n')

    eleza test_rstrip_multiple(self):
        editor = MockEditor()
        #  Comment above, uncomment 3 below to test ukijumuisha real Editor & Text.
        #kutoka idlelib.editor agiza EditorWindow kama Editor
        #kutoka tkinter agiza Tk
        #editor = Editor(root=Tk())
        text = editor.text
        do_rstrip = ft.Rstrip(editor).do_rstrip

        original = (
            "Line ukijumuisha an ending tab    \n"
            "Line ending kwenye 5 spaces     \n"
            "Linewithnospaces\n"
            "    indented line\n"
            "    indented line ukijumuisha trailing space \n"
            "    ")
        stripped = (
            "Line ukijumuisha an ending tab\n"
            "Line ending kwenye 5 spaces\n"
            "Linewithnospaces\n"
            "    indented line\n"
            "    indented line ukijumuisha trailing space\n")

        text.insert('1.0', original)
        do_rstrip()
        self.assertEqual(text.get('1.0', 'insert'), stripped)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
