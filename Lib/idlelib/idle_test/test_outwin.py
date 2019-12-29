"Test outwin, coverage 76%."

kutoka idlelib agiza outwin
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk, Text
kutoka idlelib.idle_test.mock_tk agiza Mbox_func
kutoka idlelib.idle_test.mock_idle agiza Func
kutoka unittest agiza mock


kundi OutputWindowTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        root = cls.root = Tk()
        root.withdraw()
        w = cls.window = outwin.OutputWindow(Tupu, Tupu, Tupu, root)
        cls.text = w.text = Text(root)

    @classmethod
    eleza tearDownClass(cls):
        cls.window.close()
        toa cls.text, cls.window
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.text.delete('1.0', 'end')

    eleza test_ispythonsource(self):
        # OutputWindow overrides ispythonsource to always rudisha Uongo.
        w = self.window
        self.assertUongo(w.ispythonsource('test.txt'))
        self.assertUongo(w.ispythonsource(__file__))

    eleza test_window_title(self):
        self.assertEqual(self.window.top.title(), 'Output')

    eleza test_maybesave(self):
        w = self.window
        eq = self.assertEqual
        w.get_saved = Func()

        w.get_saved.result = Uongo
        eq(w.maybesave(), 'no')
        eq(w.get_saved.called, 1)

        w.get_saved.result = Kweli
        eq(w.maybesave(), 'yes')
        eq(w.get_saved.called, 2)
        toa w.get_saved

    eleza test_write(self):
        eq = self.assertEqual
        delete = self.text.delete
        get = self.text.get
        write = self.window.write

        # Test bytes.
        b = b'Test bytes.'
        eq(write(b), len(b))
        eq(get('1.0', '1.end'), b.decode())

        # No new line - insert stays on same line.
        delete('1.0', 'end')
        test_text = 'test text'
        eq(write(test_text), len(test_text))
        eq(get('1.0', '1.end'), 'test text')
        eq(get('insert linestart', 'insert lineend'), 'test text')

        # New line - insert moves to next line.
        delete('1.0', 'end')
        test_text = 'test text\n'
        eq(write(test_text), len(test_text))
        eq(get('1.0', '1.end'), 'test text')
        eq(get('insert linestart', 'insert lineend'), '')

        # Text after new line ni tagged kila second line of Text widget.
        delete('1.0', 'end')
        test_text = 'test text\nLine 2'
        eq(write(test_text), len(test_text))
        eq(get('1.0', '1.end'), 'test text')
        eq(get('2.0', '2.end'), 'Line 2')
        eq(get('insert linestart', 'insert lineend'), 'Line 2')

        # Test tags.
        delete('1.0', 'end')
        test_text = 'test text\n'
        test_text2 = 'Line 2\n'
        eq(write(test_text, tags='mytag'), len(test_text))
        eq(write(test_text2, tags='secondtag'), len(test_text2))
        eq(get('mytag.first', 'mytag.last'), test_text)
        eq(get('secondtag.first', 'secondtag.last'), test_text2)
        eq(get('1.0', '1.end'), test_text.rstrip('\n'))
        eq(get('2.0', '2.end'), test_text2.rstrip('\n'))

    eleza test_writelines(self):
        eq = self.assertEqual
        get = self.text.get
        writelines = self.window.writelines

        writelines(('Line 1\n', 'Line 2\n', 'Line 3\n'))
        eq(get('1.0', '1.end'), 'Line 1')
        eq(get('2.0', '2.end'), 'Line 2')
        eq(get('3.0', '3.end'), 'Line 3')
        eq(get('insert linestart', 'insert lineend'), '')

    eleza test_goto_file_line(self):
        eq = self.assertEqual
        w = self.window
        text = self.text

        w.flist = mock.Mock()
        gfl = w.flist.gotofileline = Func()
        showerror = w.showerror = Mbox_func()

        # No file/line number.
        w.write('Not a file line')
        self.assertIsTupu(w.goto_file_line())
        eq(gfl.called, 0)
        eq(showerror.title, 'No special line')

        # Current file/line number.
        w.write(f'{str(__file__)}: 42: spam\n')
        w.write(f'{str(__file__)}: 21: spam')
        self.assertIsTupu(w.goto_file_line())
        eq(gfl.args, (str(__file__), 21))

        # Previous line has file/line number.
        text.delete('1.0', 'end')
        w.write(f'{str(__file__)}: 42: spam\n')
        w.write('Not a file line')
        self.assertIsTupu(w.goto_file_line())
        eq(gfl.args, (str(__file__), 42))

        toa w.flist.gotofileline, w.showerror


kundi ModuleFunctionTest(unittest.TestCase):

    @classmethod
    eleza setUp(cls):
        outwin.file_line_progs = Tupu

    eleza test_compile_progs(self):
        outwin.compile_progs()
        kila pat, regex kwenye zip(outwin.file_line_pats, outwin.file_line_progs):
            self.assertEqual(regex.pattern, pat)

    @mock.patch('builtins.open')
    eleza test_file_line_helper(self, mock_open):
        flh = outwin.file_line_helper
        test_lines = (
            (r'foo file "testfile1", line 42, bar', ('testfile1', 42)),
            (r'foo testfile2(21) bar', ('testfile2', 21)),
            (r'  testfile3  : 42: foo bar\n', ('  testfile3  ', 42)),
            (r'foo testfile4.py :1: ', ('foo testfile4.py ', 1)),
            ('testfile5: \u19D4\u19D2: ', ('testfile5', 42)),
            (r'testfile6: 42', Tupu),       # only one `:`
            (r'testfile7 42 text', Tupu)    # no separators
            )
        kila line, expected_output kwenye test_lines:
            self.assertEqual(flh(line), expected_output)
            ikiwa expected_output:
                mock_open.assert_called_with(expected_output[0], 'r')


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
