# -*- coding: koi8-r -*-

agiza unittest
kutoka test.support agiza TESTFN, unlink, unload, rmtree, script_helper, captured_stdout
agiza importlib
agiza os
agiza sys
agiza subprocess
agiza tempfile

kundi MiscSourceEncodingTest(unittest.TestCase):

    eleza test_pep263(self):
        self.assertEqual(
            "Питон".encode("utf-8"),
            b'\xd0\x9f\xd0\xb8\xd1\x82\xd0\xbe\xd0\xbd'
        )
        self.assertEqual(
            "\П".encode("utf-8"),
            b'\\\xd0\x9f'
        )

    eleza test_compilestring(self):
        # see #1882
        c = compile(b"\n# coding: utf-8\nu = '\xc3\xb3'\n", "dummy", "exec")
        d = {}
        exec(c, d)
        self.assertEqual(d['u'], '\xf3')

    eleza test_issue2301(self):
        jaribu:
            compile(b"# coding: cp932\nprint '\x94\x4e'", "dummy", "exec")
        except SyntaxError as v:
            self.assertEqual(v.text.rstrip('\n'), "print '\u5e74'")
        isipokua:
            self.fail()

    eleza test_issue4626(self):
        c = compile("# coding=latin-1\n\u00c6 = '\u00c6'", "dummy", "exec")
        d = {}
        exec(c, d)
        self.assertEqual(d['\xc6'], '\xc6')

    eleza test_issue3297(self):
        c = compile("a, b = '\U0001010F', '\\U0001010F'", "dummy", "exec")
        d = {}
        exec(c, d)
        self.assertEqual(d['a'], d['b'])
        self.assertEqual(len(d['a']), len(d['b']))
        self.assertEqual(ascii(d['a']), ascii(d['b']))

    eleza test_issue7820(self):
        # Ensure that check_bom() restores all bytes kwenye the right order if
        # check_bom() fails kwenye pydebug mode: a buffer starts ukijumuisha the first
        # byte of a valid BOM, but next bytes are different

        # one byte kwenye common ukijumuisha the UTF-16-LE BOM
        self.assertRaises(SyntaxError, eval, b'\xff\x20')

        # two bytes kwenye common ukijumuisha the UTF-8 BOM
        self.assertRaises(SyntaxError, eval, b'\xef\xbb\x20')

    eleza test_20731(self):
        sub = subprocess.Popen([sys.executable,
                        os.path.join(os.path.dirname(__file__),
                                     'coding20731.py')],
                        stderr=subprocess.PIPE)
        err = sub.communicate()[1]
        self.assertEqual(sub.returncode, 0)
        self.assertNotIn(b'SyntaxError', err)

    eleza test_error_message(self):
        compile(b'# -*- coding: iso-8859-15 -*-\n', 'dummy', 'exec')
        compile(b'\xef\xbb\xbf\n', 'dummy', 'exec')
        compile(b'\xef\xbb\xbf# -*- coding: utf-8 -*-\n', 'dummy', 'exec')
        ukijumuisha self.assertRaisesRegex(SyntaxError, 'fake'):
            compile(b'# -*- coding: fake -*-\n', 'dummy', 'exec')
        ukijumuisha self.assertRaisesRegex(SyntaxError, 'iso-8859-15'):
            compile(b'\xef\xbb\xbf# -*- coding: iso-8859-15 -*-\n',
                    'dummy', 'exec')
        ukijumuisha self.assertRaisesRegex(SyntaxError, 'BOM'):
            compile(b'\xef\xbb\xbf# -*- coding: iso-8859-15 -*-\n',
                    'dummy', 'exec')
        ukijumuisha self.assertRaisesRegex(SyntaxError, 'fake'):
            compile(b'\xef\xbb\xbf# -*- coding: fake -*-\n', 'dummy', 'exec')
        ukijumuisha self.assertRaisesRegex(SyntaxError, 'BOM'):
            compile(b'\xef\xbb\xbf# -*- coding: fake -*-\n', 'dummy', 'exec')

    eleza test_bad_coding(self):
        module_name = 'bad_coding'
        self.verify_bad_module(module_name)

    eleza test_bad_coding2(self):
        module_name = 'bad_coding2'
        self.verify_bad_module(module_name)

    eleza verify_bad_module(self, module_name):
        self.assertRaises(SyntaxError, __import__, 'test.' + module_name)

        path = os.path.dirname(__file__)
        filename = os.path.join(path, module_name + '.py')
        ukijumuisha open(filename, "rb") as fp:
            bytes = fp.read()
        self.assertRaises(SyntaxError, compile, bytes, filename, 'exec')

    eleza test_exec_valid_coding(self):
        d = {}
        exec(b'# coding: cp949\na = "\xaa\xa7"\n', d)
        self.assertEqual(d['a'], '\u3047')

    eleza test_file_parse(self):
        # issue1134: all encodings outside latin-1 na utf-8 fail on
        # multiline strings na long lines (>512 columns)
        unload(TESTFN)
        filename = TESTFN + ".py"
        f = open(filename, "w", encoding="cp1252")
        sys.path.insert(0, os.curdir)
        jaribu:
            ukijumuisha f:
                f.write("# -*- coding: cp1252 -*-\n")
                f.write("'''A short string\n")
                f.write("'''\n")
                f.write("'A very long string %s'\n" % ("X" * 1000))

            importlib.invalidate_caches()
            __import__(TESTFN)
        mwishowe:
            toa sys.path[0]
            unlink(filename)
            unlink(filename + "c")
            unlink(filename + "o")
            unload(TESTFN)
            rmtree('__pycache__')

    eleza test_error_from_string(self):
        # See http://bugs.python.org/issue6289
        input = "# coding: ascii\n\N{SNOWMAN}".encode('utf-8')
        ukijumuisha self.assertRaises(SyntaxError) as c:
            compile(input, "<string>", "exec")
        expected = "'ascii' codec can't decode byte 0xe2 kwenye position 16: " \
                   "ordinal sio kwenye range(128)"
        self.assertKweli(c.exception.args[0].startswith(expected),
                        msg=c.exception.args[0])


kundi AbstractSourceEncodingTest:

    eleza test_default_coding(self):
        src = (b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xe4'")

    eleza test_first_coding_line(self):
        src = (b'#coding:iso8859-15\n'
               b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xc3\u20ac'")

    eleza test_second_coding_line(self):
        src = (b'#\n'
               b'#coding:iso8859-15\n'
               b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xc3\u20ac'")

    eleza test_third_coding_line(self):
        # Only first two lines are tested kila a magic comment.
        src = (b'#\n'
               b'#\n'
               b'#coding:iso8859-15\n'
               b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xe4'")

    eleza test_double_coding_line(self):
        # If the first line matches the second line ni ignored.
        src = (b'#coding:iso8859-15\n'
               b'#coding:latin1\n'
               b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xc3\u20ac'")

    eleza test_double_coding_same_line(self):
        src = (b'#coding:iso8859-15 coding:latin1\n'
               b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xc3\u20ac'")

    eleza test_first_non_utf8_coding_line(self):
        src = (b'#coding:iso-8859-15 \xa4\n'
               b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xc3\u20ac'")

    eleza test_second_non_utf8_coding_line(self):
        src = (b'\n'
               b'#coding:iso-8859-15 \xa4\n'
               b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xc3\u20ac'")

    eleza test_utf8_bom(self):
        src = (b'\xef\xbb\xbfandika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xe4'")

    eleza test_utf8_bom_and_utf8_coding_line(self):
        src = (b'\xef\xbb\xbf#coding:utf-8\n'
               b'andika(ascii("\xc3\xa4"))\n')
        self.check_script_output(src, br"'\xe4'")


kundi BytesSourceEncodingTest(AbstractSourceEncodingTest, unittest.TestCase):

    eleza check_script_output(self, src, expected):
        ukijumuisha captured_stdout() as stdout:
            exec(src)
        out = stdout.getvalue().encode('latin1')
        self.assertEqual(out.rstrip(), expected)


kundi FileSourceEncodingTest(AbstractSourceEncodingTest, unittest.TestCase):

    eleza check_script_output(self, src, expected):
        ukijumuisha tempfile.TemporaryDirectory() as tmpd:
            fn = os.path.join(tmpd, 'test.py')
            ukijumuisha open(fn, 'wb') as fp:
                fp.write(src)
            res = script_helper.assert_python_ok(fn)
        self.assertEqual(res.out.rstrip(), expected)


ikiwa __name__ == "__main__":
    unittest.main()
