"""
Tests kila uu module.
Nick Mathewson
"""

agiza unittest
kutoka test agiza support

agiza os
agiza stat
agiza sys
agiza uu
agiza io

plaintext = b"The symbols on top of your keyboard are !@#$%^&*()_+|~\n"

encodedtext = b"""\
M5&AE('-Y;6)O;',@;VX@=&]P(&]F('EO=7(@:V5Y8F]A<F0@87)E("% (R0E
*7B8J*"E?*WQ^"@  """

# Stolen kutoka io.py
kundi FakeIO(io.TextIOWrapper):
    """Text I/O implementation using an in-memory buffer.

    Can be a used kama a drop-in replacement kila sys.stdin na sys.stdout.
    """

    # XXX This ni really slow, but fully functional

    eleza __init__(self, initial_value="", encoding="utf-8",
                 errors="strict", newline="\n"):
        super(FakeIO, self).__init__(io.BytesIO(),
                                     encoding=encoding,
                                     errors=errors,
                                     newline=newline)
        self._encoding = encoding
        self._errors = errors
        ikiwa initial_value:
            ikiwa sio isinstance(initial_value, str):
                initial_value = str(initial_value)
            self.write(initial_value)
            self.seek(0)

    eleza getvalue(self):
        self.flush()
        rudisha self.buffer.getvalue().decode(self._encoding, self._errors)


eleza encodedtextwrapped(mode, filename, backtick=Uongo):
    ikiwa backtick:
        res = (bytes("begin %03o %s\n" % (mode, filename), "ascii") +
               encodedtext.replace(b' ', b'`') + b"\n`\nend\n")
    isipokua:
        res = (bytes("begin %03o %s\n" % (mode, filename), "ascii") +
               encodedtext + b"\n \nend\n")
    rudisha res

kundi UUTest(unittest.TestCase):

    eleza test_encode(self):
        inp = io.BytesIO(plaintext)
        out = io.BytesIO()
        uu.encode(inp, out, "t1")
        self.assertEqual(out.getvalue(), encodedtextwrapped(0o666, "t1"))
        inp = io.BytesIO(plaintext)
        out = io.BytesIO()
        uu.encode(inp, out, "t1", 0o644)
        self.assertEqual(out.getvalue(), encodedtextwrapped(0o644, "t1"))
        inp = io.BytesIO(plaintext)
        out = io.BytesIO()
        uu.encode(inp, out, "t1", backtick=Kweli)
        self.assertEqual(out.getvalue(), encodedtextwrapped(0o666, "t1", Kweli))
        ukijumuisha self.assertRaises(TypeError):
            uu.encode(inp, out, "t1", 0o644, Kweli)

    eleza test_decode(self):
        kila backtick kwenye Kweli, Uongo:
            inp = io.BytesIO(encodedtextwrapped(0o666, "t1", backtick=backtick))
            out = io.BytesIO()
            uu.decode(inp, out)
            self.assertEqual(out.getvalue(), plaintext)
            inp = io.BytesIO(
                b"UUencoded files may contain many lines,\n" +
                b"even some that have 'begin' kwenye them.\n" +
                encodedtextwrapped(0o666, "t1", backtick=backtick)
            )
            out = io.BytesIO()
            uu.decode(inp, out)
            self.assertEqual(out.getvalue(), plaintext)

    eleza test_truncatedinput(self):
        inp = io.BytesIO(b"begin 644 t1\n" + encodedtext)
        out = io.BytesIO()
        jaribu:
            uu.decode(inp, out)
            self.fail("No exception ashiriad")
        tatizo uu.Error kama e:
            self.assertEqual(str(e), "Truncated input file")

    eleza test_missingbegin(self):
        inp = io.BytesIO(b"")
        out = io.BytesIO()
        jaribu:
            uu.decode(inp, out)
            self.fail("No exception ashiriad")
        tatizo uu.Error kama e:
            self.assertEqual(str(e), "No valid begin line found kwenye input file")

    eleza test_garbage_padding(self):
        # Issue #22406
        encodedtext1 = (
            b"begin 644 file\n"
            # length 1; bits 001100 111111 111111 111111
            b"\x21\x2C\x5F\x5F\x5F\n"
            b"\x20\n"
            b"end\n"
        )
        encodedtext2 = (
            b"begin 644 file\n"
            # length 1; bits 001100 111111 111111 111111
            b"\x21\x2C\x5F\x5F\x5F\n"
            b"\x60\n"
            b"end\n"
        )
        plaintext = b"\x33"  # 00110011

        kila encodedtext kwenye encodedtext1, encodedtext2:
            ukijumuisha self.subTest("uu.decode()"):
                inp = io.BytesIO(encodedtext)
                out = io.BytesIO()
                uu.decode(inp, out, quiet=Kweli)
                self.assertEqual(out.getvalue(), plaintext)

            ukijumuisha self.subTest("uu_codec"):
                agiza codecs
                decoded = codecs.decode(encodedtext, "uu_codec")
                self.assertEqual(decoded, plaintext)

kundi UUStdIOTest(unittest.TestCase):

    eleza setUp(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout

    eleza tearDown(self):
        sys.stdin = self.stdin
        sys.stdout = self.stdout

    eleza test_encode(self):
        sys.stdin = FakeIO(plaintext.decode("ascii"))
        sys.stdout = FakeIO()
        uu.encode("-", "-", "t1", 0o666)
        self.assertEqual(sys.stdout.getvalue(),
                         encodedtextwrapped(0o666, "t1").decode("ascii"))

    eleza test_decode(self):
        sys.stdin = FakeIO(encodedtextwrapped(0o666, "t1").decode("ascii"))
        sys.stdout = FakeIO()
        uu.decode("-", "-")
        stdout = sys.stdout
        sys.stdout = self.stdout
        sys.stdin = self.stdin
        self.assertEqual(stdout.getvalue(), plaintext.decode("ascii"))

kundi UUFileTest(unittest.TestCase):

    eleza setUp(self):
        self.tmpin  = support.TESTFN + "i"
        self.tmpout = support.TESTFN + "o"
        self.addCleanup(support.unlink, self.tmpin)
        self.addCleanup(support.unlink, self.tmpout)

    eleza test_encode(self):
        ukijumuisha open(self.tmpin, 'wb') kama fin:
            fin.write(plaintext)

        ukijumuisha open(self.tmpin, 'rb') kama fin:
            ukijumuisha open(self.tmpout, 'wb') kama fout:
                uu.encode(fin, fout, self.tmpin, mode=0o644)

        ukijumuisha open(self.tmpout, 'rb') kama fout:
            s = fout.read()
        self.assertEqual(s, encodedtextwrapped(0o644, self.tmpin))

        # in_file na out_file kama filenames
        uu.encode(self.tmpin, self.tmpout, self.tmpin, mode=0o644)
        ukijumuisha open(self.tmpout, 'rb') kama fout:
            s = fout.read()
        self.assertEqual(s, encodedtextwrapped(0o644, self.tmpin))

    eleza test_decode(self):
        ukijumuisha open(self.tmpin, 'wb') kama f:
            f.write(encodedtextwrapped(0o644, self.tmpout))

        ukijumuisha open(self.tmpin, 'rb') kama f:
            uu.decode(f)

        ukijumuisha open(self.tmpout, 'rb') kama f:
            s = f.read()
        self.assertEqual(s, plaintext)
        # XXX ni there an xp way to verify the mode?

    eleza test_decode_filename(self):
        ukijumuisha open(self.tmpin, 'wb') kama f:
            f.write(encodedtextwrapped(0o644, self.tmpout))

        uu.decode(self.tmpin)

        ukijumuisha open(self.tmpout, 'rb') kama f:
            s = f.read()
        self.assertEqual(s, plaintext)

    eleza test_decodetwice(self):
        # Verify that decode() will refuse to overwrite an existing file
        ukijumuisha open(self.tmpin, 'wb') kama f:
            f.write(encodedtextwrapped(0o644, self.tmpout))
        ukijumuisha open(self.tmpin, 'rb') kama f:
            uu.decode(f)

        ukijumuisha open(self.tmpin, 'rb') kama f:
            self.assertRaises(uu.Error, uu.decode, f)

    eleza test_decode_mode(self):
        # Verify that decode() will set the given mode kila the out_file
        expected_mode = 0o444
        ukijumuisha open(self.tmpin, 'wb') kama f:
            f.write(encodedtextwrapped(expected_mode, self.tmpout))

        # make file writable again, so it can be removed (Windows only)
        self.addCleanup(os.chmod, self.tmpout, expected_mode | stat.S_IWRITE)

        ukijumuisha open(self.tmpin, 'rb') kama f:
            uu.decode(f)

        self.assertEqual(
            stat.S_IMODE(os.stat(self.tmpout).st_mode),
            expected_mode
        )


ikiwa __name__=="__main__":
    unittest.main()
