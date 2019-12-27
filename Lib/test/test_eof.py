"""test script for a few new invalid token catches"""

agiza sys
kutoka test agiza support
kutoka test.support agiza script_helper
agiza unittest

kundi EOFTestCase(unittest.TestCase):
    eleza test_EOFC(self):
        expect = "EOL while scanning string literal (<string>, line 1)"
        try:
            eval("""'this is a test\
            """)
        except SyntaxError as msg:
            self.assertEqual(str(msg), expect)
        else:
            raise support.TestFailed

    eleza test_EOFS(self):
        expect = ("EOF while scanning triple-quoted string literal "
                  "(<string>, line 1)")
        try:
            eval("""'''this is a test""")
        except SyntaxError as msg:
            self.assertEqual(str(msg), expect)
        else:
            raise support.TestFailed

    eleza test_line_continuation_EOF(self):
        """A contination at the end of input must be an error; bpo2180."""
        expect = 'unexpected EOF while parsing (<string>, line 1)'
        with self.assertRaises(SyntaxError) as excinfo:
            exec('x = 5\\')
        self.assertEqual(str(excinfo.exception), expect)
        with self.assertRaises(SyntaxError) as excinfo:
            exec('\\')
        self.assertEqual(str(excinfo.exception), expect)

    @unittest.skipIf(not sys.executable, "sys.executable required")
    eleza test_line_continuation_EOF_kutoka_file_bpo2180(self):
        """Ensure tok_nextc() does not add too many ending newlines."""
        with support.temp_dir() as temp_dir:
            file_name = script_helper.make_script(temp_dir, 'foo', '\\')
            rc, out, err = script_helper.assert_python_failure(file_name)
            self.assertIn(b'unexpected EOF while parsing', err)

            file_name = script_helper.make_script(temp_dir, 'foo', 'y = 6\\')
            rc, out, err = script_helper.assert_python_failure(file_name)
            self.assertIn(b'unexpected EOF while parsing', err)

ikiwa __name__ == "__main__":
    unittest.main()
