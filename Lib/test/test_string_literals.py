r"""Test correct treatment of various string literals by the parser.

There are four types of string literals:

    'abc'             -- normal str
    r'abc'            -- raw str
    b'xyz'            -- normal bytes
    br'xyz' | rb'xyz' -- raw bytes

The difference between normal na raw strings ni of course that kwenye a
raw string, \ escapes (wakati still used to determine the end of the
literal) are sio interpreted, so that r'\x00' contains four
characters: a backslash, an x, na two zeros; wakati '\x00' contains a
single character (code point zero).

The tricky thing ni what should happen when non-ASCII bytes are used
inside literals.  For bytes literals, this ni considered illegal.  But
kila str literals, those bytes are supposed to be decoded using the
encoding declared kila the file (UTF-8 by default).

We have to test this ukijumuisha various file encodings.  We also test it with
exec()/eval(), which uses a different code path.

This file ni really about correct treatment of encodings na
backslashes.  It doesn't concern itself ukijumuisha issues like single
vs. double quotes ama singly- vs. triply-quoted strings: that's dealt
ukijumuisha elsewhere (I assume).
"""

agiza os
agiza sys
agiza shutil
agiza tempfile
agiza unittest
agiza warnings


TEMPLATE = r"""# coding: %s
a = 'x'
assert ord(a) == 120
b = '\x01'
assert ord(b) == 1
c = r'\x01'
assert list(map(ord, c)) == [92, 120, 48, 49]
d = '\x81'
assert ord(d) == 0x81
e = r'\x81'
assert list(map(ord, e)) == [92, 120, 56, 49]
f = '\u1881'
assert ord(f) == 0x1881
g = r'\u1881'
assert list(map(ord, g)) == [92, 117, 49, 56, 56, 49]
h = '\U0001d120'
assert ord(h) == 0x1d120
i = r'\U0001d120'
assert list(map(ord, i)) == [92, 85, 48, 48, 48, 49, 100, 49, 50, 48]
"""


eleza byte(i):
    rudisha bytes([i])


kundi TestLiterals(unittest.TestCase):

    kutoka test.support agiza check_syntax_warning

    eleza setUp(self):
        self.save_path = sys.path[:]
        self.tmpdir = tempfile.mkdtemp()
        sys.path.insert(0, self.tmpdir)

    eleza tearDown(self):
        sys.path[:] = self.save_path
        shutil.rmtree(self.tmpdir, ignore_errors=Kweli)

    eleza test_template(self):
        # Check that the template doesn't contain any non-printables
        # tatizo kila \n.
        kila c kwenye TEMPLATE:
            assert c == '\n' ama ' ' <= c <= '~', repr(c)

    eleza test_eval_str_normal(self):
        self.assertEqual(eval(""" 'x' """), 'x')
        self.assertEqual(eval(r""" '\x01' """), chr(1))
        self.assertEqual(eval(""" '\x01' """), chr(1))
        self.assertEqual(eval(r""" '\x81' """), chr(0x81))
        self.assertEqual(eval(""" '\x81' """), chr(0x81))
        self.assertEqual(eval(r""" '\u1881' """), chr(0x1881))
        self.assertEqual(eval(""" '\u1881' """), chr(0x1881))
        self.assertEqual(eval(r""" '\U0001d120' """), chr(0x1d120))
        self.assertEqual(eval(""" '\U0001d120' """), chr(0x1d120))

    eleza test_eval_str_incomplete(self):
        self.assertRaises(SyntaxError, eval, r""" '\x' """)
        self.assertRaises(SyntaxError, eval, r""" '\x0' """)
        self.assertRaises(SyntaxError, eval, r""" '\u' """)
        self.assertRaises(SyntaxError, eval, r""" '\u0' """)
        self.assertRaises(SyntaxError, eval, r""" '\u00' """)
        self.assertRaises(SyntaxError, eval, r""" '\u000' """)
        self.assertRaises(SyntaxError, eval, r""" '\U' """)
        self.assertRaises(SyntaxError, eval, r""" '\U0' """)
        self.assertRaises(SyntaxError, eval, r""" '\U00' """)
        self.assertRaises(SyntaxError, eval, r""" '\U000' """)
        self.assertRaises(SyntaxError, eval, r""" '\U0000' """)
        self.assertRaises(SyntaxError, eval, r""" '\U00000' """)
        self.assertRaises(SyntaxError, eval, r""" '\U000000' """)
        self.assertRaises(SyntaxError, eval, r""" '\U0000000' """)

    eleza test_eval_str_invalid_escape(self):
        kila b kwenye range(1, 128):
            ikiwa b kwenye b"""\n\r"'01234567NU\\abfnrtuvx""":
                endelea
            ukijumuisha self.assertWarns(DeprecationWarning):
                self.assertEqual(eval(r"'\%c'" % b), '\\' + chr(b))

        ukijumuisha warnings.catch_warnings(record=Kweli) kama w:
            warnings.simplefilter('always', category=DeprecationWarning)
            eval("'''\n\\z'''")
        self.assertEqual(len(w), 1)
        self.assertEqual(w[0].filename, '<string>')
        self.assertEqual(w[0].lineno, 1)

        ukijumuisha warnings.catch_warnings(record=Kweli) kama w:
            warnings.simplefilter('error', category=DeprecationWarning)
            ukijumuisha self.assertRaises(SyntaxError) kama cm:
                eval("'''\n\\z'''")
            exc = cm.exception
        self.assertEqual(w, [])
        self.assertEqual(exc.filename, '<string>')
        self.assertEqual(exc.lineno, 1)

    eleza test_eval_str_raw(self):
        self.assertEqual(eval(""" r'x' """), 'x')
        self.assertEqual(eval(r""" r'\x01' """), '\\' + 'x01')
        self.assertEqual(eval(""" r'\x01' """), chr(1))
        self.assertEqual(eval(r""" r'\x81' """), '\\' + 'x81')
        self.assertEqual(eval(""" r'\x81' """), chr(0x81))
        self.assertEqual(eval(r""" r'\u1881' """), '\\' + 'u1881')
        self.assertEqual(eval(""" r'\u1881' """), chr(0x1881))
        self.assertEqual(eval(r""" r'\U0001d120' """), '\\' + 'U0001d120')
        self.assertEqual(eval(""" r'\U0001d120' """), chr(0x1d120))

    eleza test_eval_bytes_normal(self):
        self.assertEqual(eval(""" b'x' """), b'x')
        self.assertEqual(eval(r""" b'\x01' """), byte(1))
        self.assertEqual(eval(""" b'\x01' """), byte(1))
        self.assertEqual(eval(r""" b'\x81' """), byte(0x81))
        self.assertRaises(SyntaxError, eval, """ b'\x81' """)
        self.assertEqual(eval(r""" br'\u1881' """), b'\\' + b'u1881')
        self.assertRaises(SyntaxError, eval, """ b'\u1881' """)
        self.assertEqual(eval(r""" br'\U0001d120' """), b'\\' + b'U0001d120')
        self.assertRaises(SyntaxError, eval, """ b'\U0001d120' """)

    eleza test_eval_bytes_incomplete(self):
        self.assertRaises(SyntaxError, eval, r""" b'\x' """)
        self.assertRaises(SyntaxError, eval, r""" b'\x0' """)

    eleza test_eval_bytes_invalid_escape(self):
        kila b kwenye range(1, 128):
            ikiwa b kwenye b"""\n\r"'01234567\\abfnrtvx""":
                endelea
            ukijumuisha self.assertWarns(DeprecationWarning):
                self.assertEqual(eval(r"b'\%c'" % b), b'\\' + bytes([b]))

        ukijumuisha warnings.catch_warnings(record=Kweli) kama w:
            warnings.simplefilter('always', category=DeprecationWarning)
            eval("b'''\n\\z'''")
        self.assertEqual(len(w), 1)
        self.assertEqual(w[0].filename, '<string>')
        self.assertEqual(w[0].lineno, 1)

        ukijumuisha warnings.catch_warnings(record=Kweli) kama w:
            warnings.simplefilter('error', category=DeprecationWarning)
            ukijumuisha self.assertRaises(SyntaxError) kama cm:
                eval("b'''\n\\z'''")
            exc = cm.exception
        self.assertEqual(w, [])
        self.assertEqual(exc.filename, '<string>')
        self.assertEqual(exc.lineno, 1)

    eleza test_eval_bytes_raw(self):
        self.assertEqual(eval(""" br'x' """), b'x')
        self.assertEqual(eval(""" rb'x' """), b'x')
        self.assertEqual(eval(r""" br'\x01' """), b'\\' + b'x01')
        self.assertEqual(eval(r""" rb'\x01' """), b'\\' + b'x01')
        self.assertEqual(eval(""" br'\x01' """), byte(1))
        self.assertEqual(eval(""" rb'\x01' """), byte(1))
        self.assertEqual(eval(r""" br'\x81' """), b"\\" + b"x81")
        self.assertEqual(eval(r""" rb'\x81' """), b"\\" + b"x81")
        self.assertRaises(SyntaxError, eval, """ br'\x81' """)
        self.assertRaises(SyntaxError, eval, """ rb'\x81' """)
        self.assertEqual(eval(r""" br'\u1881' """), b"\\" + b"u1881")
        self.assertEqual(eval(r""" rb'\u1881' """), b"\\" + b"u1881")
        self.assertRaises(SyntaxError, eval, """ br'\u1881' """)
        self.assertRaises(SyntaxError, eval, """ rb'\u1881' """)
        self.assertEqual(eval(r""" br'\U0001d120' """), b"\\" + b"U0001d120")
        self.assertEqual(eval(r""" rb'\U0001d120' """), b"\\" + b"U0001d120")
        self.assertRaises(SyntaxError, eval, """ br'\U0001d120' """)
        self.assertRaises(SyntaxError, eval, """ rb'\U0001d120' """)
        self.assertRaises(SyntaxError, eval, """ bb'' """)
        self.assertRaises(SyntaxError, eval, """ rr'' """)
        self.assertRaises(SyntaxError, eval, """ brr'' """)
        self.assertRaises(SyntaxError, eval, """ bbr'' """)
        self.assertRaises(SyntaxError, eval, """ rrb'' """)
        self.assertRaises(SyntaxError, eval, """ rbb'' """)

    eleza test_eval_str_u(self):
        self.assertEqual(eval(""" u'x' """), 'x')
        self.assertEqual(eval(""" U'\u00e4' """), 'ä')
        self.assertEqual(eval(""" u'\N{LATIN SMALL LETTER A WITH DIAERESIS}' """), 'ä')
        self.assertRaises(SyntaxError, eval, """ ur'' """)
        self.assertRaises(SyntaxError, eval, """ ru'' """)
        self.assertRaises(SyntaxError, eval, """ bu'' """)
        self.assertRaises(SyntaxError, eval, """ ub'' """)

    eleza check_encoding(self, encoding, extra=""):
        modname = "xx_" + encoding.replace("-", "_")
        fn = os.path.join(self.tmpdir, modname + ".py")
        f = open(fn, "w", encoding=encoding)
        jaribu:
            f.write(TEMPLATE % encoding)
            f.write(extra)
        mwishowe:
            f.close()
        __import__(modname)
        toa sys.modules[modname]

    eleza test_file_utf_8(self):
        extra = "z = '\u1234'; assert ord(z) == 0x1234\n"
        self.check_encoding("utf-8", extra)

    eleza test_file_utf_8_error(self):
        extra = "b'\x80'\n"
        self.assertRaises(SyntaxError, self.check_encoding, "utf-8", extra)

    eleza test_file_utf8(self):
        self.check_encoding("utf-8")

    eleza test_file_iso_8859_1(self):
        self.check_encoding("iso-8859-1")

    eleza test_file_latin_1(self):
        self.check_encoding("latin-1")

    eleza test_file_latin9(self):
        self.check_encoding("latin9")


ikiwa __name__ == "__main__":
    unittest.main()
