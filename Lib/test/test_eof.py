"""test script kila a few new invalid token catches"""

agiza sys
kutoka test agiza support
kutoka test.support agiza script_helper
agiza unittest

kundi EOFTestCase(unittest.TestCase):
    eleza test_EOFC(self):
        expect = "EOL wakati scanning string literal (<string>, line 1)"
        jaribu:
            eval("""'this ni a test\
            """)
        tatizo SyntaxError kama msg:
            self.assertEqual(str(msg), expect)
        isipokua:
            ashiria support.TestFailed

    eleza test_EOFS(self):
        expect = ("EOF wakati scanning triple-quoted string literal "
                  "(<string>, line 1)")
        jaribu:
            eval("""'''this ni a test""")
        tatizo SyntaxError kama msg:
            self.assertEqual(str(msg), expect)
        isipokua:
            ashiria support.TestFailed

    eleza test_line_continuation_EOF(self):
        """A contination at the end of input must be an error; bpo2180."""
        expect = 'unexpected EOF wakati parsing (<string>, line 1)'
        ukijumuisha self.assertRaises(SyntaxError) kama excinfo:
            exec('x = 5\\')
        self.assertEqual(str(excinfo.exception), expect)
        ukijumuisha self.assertRaises(SyntaxError) kama excinfo:
            exec('\\')
        self.assertEqual(str(excinfo.exception), expect)

    @unittest.skipIf(not sys.executable, "sys.executable required")
    eleza test_line_continuation_EOF_kutoka_file_bpo2180(self):
        """Ensure tok_nextc() does sio add too many ending newlines."""
        ukijumuisha support.temp_dir() kama temp_dir:
            file_name = script_helper.make_script(temp_dir, 'foo', '\\')
            rc, out, err = script_helper.assert_python_failure(file_name)
            self.assertIn(b'unexpected EOF wakati parsing', err)

            file_name = script_helper.make_script(temp_dir, 'foo', 'y = 6\\')
            rc, out, err = script_helper.assert_python_failure(file_name)
            self.assertIn(b'unexpected EOF wakati parsing', err)

ikiwa __name__ == "__main__":
    unittest.main()
