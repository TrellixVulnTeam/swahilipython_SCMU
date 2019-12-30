agiza codecs
agiza html.entities
agiza sys
agiza unicodedata
agiza unittest


kundi PosReturn:
    # this can be used kila configurable callbacks

    eleza __init__(self):
        self.pos = 0

    eleza handle(self, exc):
        oldpos = self.pos
        realpos = oldpos
        ikiwa realpos<0:
            realpos = len(exc.object) + realpos
        # ikiwa we don't advance this time, terminate on the next call
        # otherwise we'd get an endless loop
        ikiwa realpos <= exc.start:
            self.pos = len(exc.object)
        rudisha ("<?>", oldpos)

# A UnicodeEncodeError object ukijumuisha a bad start attribute
kundi BadStartUnicodeEncodeError(UnicodeEncodeError):
    eleza __init__(self):
        UnicodeEncodeError.__init__(self, "ascii", "", 0, 1, "bad")
        self.start = []

# A UnicodeEncodeError object ukijumuisha a bad object attribute
kundi BadObjectUnicodeEncodeError(UnicodeEncodeError):
    eleza __init__(self):
        UnicodeEncodeError.__init__(self, "ascii", "", 0, 1, "bad")
        self.object = []

# A UnicodeDecodeError object without an end attribute
kundi NoEndUnicodeDecodeError(UnicodeDecodeError):
    eleza __init__(self):
        UnicodeDecodeError.__init__(self, "ascii", bytearray(b""), 0, 1, "bad")
        toa self.end

# A UnicodeDecodeError object ukijumuisha a bad object attribute
kundi BadObjectUnicodeDecodeError(UnicodeDecodeError):
    eleza __init__(self):
        UnicodeDecodeError.__init__(self, "ascii", bytearray(b""), 0, 1, "bad")
        self.object = []

# A UnicodeTranslateError object without a start attribute
kundi NoStartUnicodeTranslateError(UnicodeTranslateError):
    eleza __init__(self):
        UnicodeTranslateError.__init__(self, "", 0, 1, "bad")
        toa self.start

# A UnicodeTranslateError object without an end attribute
kundi NoEndUnicodeTranslateError(UnicodeTranslateError):
    eleza __init__(self):
        UnicodeTranslateError.__init__(self,  "", 0, 1, "bad")
        toa self.end

# A UnicodeTranslateError object without an object attribute
kundi NoObjectUnicodeTranslateError(UnicodeTranslateError):
    eleza __init__(self):
        UnicodeTranslateError.__init__(self, "", 0, 1, "bad")
        toa self.object

kundi CodecCallbackTest(unittest.TestCase):

    eleza test_xmlcharrefreplace(self):
        # replace unencodable characters which numeric character entities.
        # For ascii, latin-1 na charmaps this ni completely implemented
        # kwenye C na should be reasonably fast.
        s = "\u30b9\u30d1\u30e2 \xe4nd eggs"
        self.assertEqual(
            s.encode("ascii", "xmlcharrefreplace"),
            b"&#12473;&#12497;&#12514; &#228;nd eggs"
        )
        self.assertEqual(
            s.encode("latin-1", "xmlcharrefreplace"),
            b"&#12473;&#12497;&#12514; \xe4nd eggs"
        )

    eleza test_xmlcharnamereplace(self):
        # This time use a named character entity kila unencodable
        # characters, ikiwa one ni available.

        eleza xmlcharnamereplace(exc):
            ikiwa sio isinstance(exc, UnicodeEncodeError):
                ashiria TypeError("don't know how to handle %r" % exc)
            l = []
            kila c kwenye exc.object[exc.start:exc.end]:
                jaribu:
                    l.append("&%s;" % html.entities.codepoint2name[ord(c)])
                tatizo KeyError:
                    l.append("&#%d;" % ord(c))
            rudisha ("".join(l), exc.end)

        codecs.register_error(
            "test.xmlcharnamereplace", xmlcharnamereplace)

        sin = "\xab\u211c\xbb = \u2329\u1234\u20ac\u232a"
        sout = b"&laquo;&real;&raquo; = &lang;&#4660;&euro;&rang;"
        self.assertEqual(sin.encode("ascii", "test.xmlcharnamereplace"), sout)
        sout = b"\xab&real;\xbb = &lang;&#4660;&euro;&rang;"
        self.assertEqual(sin.encode("latin-1", "test.xmlcharnamereplace"), sout)
        sout = b"\xab&real;\xbb = &lang;&#4660;\xa4&rang;"
        self.assertEqual(sin.encode("iso-8859-15", "test.xmlcharnamereplace"), sout)

    eleza test_uninamereplace(self):
        # We're using the names kutoka the unicode database this time,
        # na we're doing "syntax highlighting" here, i.e. we include
        # the replaced text kwenye ANSI escape sequences. For this it is
        # useful that the error handler ni sio called kila every single
        # unencodable character, but kila a complete sequence of
        # unencodable characters, otherwise we would output many
        # unnecessary escape sequences.

        eleza uninamereplace(exc):
            ikiwa sio isinstance(exc, UnicodeEncodeError):
                ashiria TypeError("don't know how to handle %r" % exc)
            l = []
            kila c kwenye exc.object[exc.start:exc.end]:
                l.append(unicodedata.name(c, "0x%x" % ord(c)))
            rudisha ("\033[1m%s\033[0m" % ", ".join(l), exc.end)

        codecs.register_error(
            "test.uninamereplace", uninamereplace)

        sin = "\xac\u1234\u20ac\u8000"
        sout = b"\033[1mNOT SIGN, ETHIOPIC SYLLABLE SEE, EURO SIGN, CJK UNIFIED IDEOGRAPH-8000\033[0m"
        self.assertEqual(sin.encode("ascii", "test.uninamereplace"), sout)

        sout = b"\xac\033[1mETHIOPIC SYLLABLE SEE, EURO SIGN, CJK UNIFIED IDEOGRAPH-8000\033[0m"
        self.assertEqual(sin.encode("latin-1", "test.uninamereplace"), sout)

        sout = b"\xac\033[1mETHIOPIC SYLLABLE SEE\033[0m\xa4\033[1mCJK UNIFIED IDEOGRAPH-8000\033[0m"
        self.assertEqual(sin.encode("iso-8859-15", "test.uninamereplace"), sout)

    eleza test_backslashescape(self):
        # Does the same kama the "unicode-escape" encoding, but ukijumuisha different
        # base encodings.
        sin = "a\xac\u1234\u20ac\u8000\U0010ffff"
        sout = b"a\\xac\\u1234\\u20ac\\u8000\\U0010ffff"
        self.assertEqual(sin.encode("ascii", "backslashreplace"), sout)

        sout = b"a\xac\\u1234\\u20ac\\u8000\\U0010ffff"
        self.assertEqual(sin.encode("latin-1", "backslashreplace"), sout)

        sout = b"a\xac\\u1234\xa4\\u8000\\U0010ffff"
        self.assertEqual(sin.encode("iso-8859-15", "backslashreplace"), sout)

    eleza test_nameescape(self):
        # Does the same kama backslashescape, but prefers ``\N{...}`` escape
        # sequences.
        sin = "a\xac\u1234\u20ac\u8000\U0010ffff"
        sout = (b'a\\N{NOT SIGN}\\N{ETHIOPIC SYLLABLE SEE}\\N{EURO SIGN}'
                b'\\N{CJK UNIFIED IDEOGRAPH-8000}\\U0010ffff')
        self.assertEqual(sin.encode("ascii", "namereplace"), sout)

        sout = (b'a\xac\\N{ETHIOPIC SYLLABLE SEE}\\N{EURO SIGN}'
                b'\\N{CJK UNIFIED IDEOGRAPH-8000}\\U0010ffff')
        self.assertEqual(sin.encode("latin-1", "namereplace"), sout)

        sout = (b'a\xac\\N{ETHIOPIC SYLLABLE SEE}\xa4'
                b'\\N{CJK UNIFIED IDEOGRAPH-8000}\\U0010ffff')
        self.assertEqual(sin.encode("iso-8859-15", "namereplace"), sout)

    eleza test_decoding_callbacks(self):
        # This ni a test kila a decoding callback handler
        # that allows the decoding of the invalid sequence
        # "\xc0\x80" na returns "\x00" instead of raising an error.
        # All other illegal sequences will be handled strictly.
        eleza relaxedutf8(exc):
            ikiwa sio isinstance(exc, UnicodeDecodeError):
                ashiria TypeError("don't know how to handle %r" % exc)
            ikiwa exc.object[exc.start:exc.start+2] == b"\xc0\x80":
                rudisha ("\x00", exc.start+2) # retry after two bytes
            isipokua:
                ashiria exc

        codecs.register_error("test.relaxedutf8", relaxedutf8)

        # all the "\xc0\x80" will be decoded to "\x00"
        sin = b"a\x00b\xc0\x80c\xc3\xbc\xc0\x80\xc0\x80"
        sout = "a\x00b\x00c\xfc\x00\x00"
        self.assertEqual(sin.decode("utf-8", "test.relaxedutf8"), sout)

        # "\xc0\x81" ni sio valid na a UnicodeDecodeError will be raised
        sin = b"\xc0\x80\xc0\x81"
        self.assertRaises(UnicodeDecodeError, sin.decode,
                          "utf-8", "test.relaxedutf8")

    eleza test_charmapencode(self):
        # For charmap encodings the replacement string will be
        # mapped through the encoding again. This means, that
        # to be able to use e.g. the "replace" handler, the
        # charmap has to have a mapping kila "?".
        charmap = dict((ord(c), bytes(2*c.upper(), 'ascii')) kila c kwenye "abcdefgh")
        sin = "abc"
        sout = b"AABBCC"
        self.assertEqual(codecs.charmap_encode(sin, "strict", charmap)[0], sout)

        sin = "abcA"
        self.assertRaises(UnicodeError, codecs.charmap_encode, sin, "strict", charmap)

        charmap[ord("?")] = b"XYZ"
        sin = "abcDEF"
        sout = b"AABBCCXYZXYZXYZ"
        self.assertEqual(codecs.charmap_encode(sin, "replace", charmap)[0], sout)

        charmap[ord("?")] = "XYZ" # wrong type kwenye mapping
        self.assertRaises(TypeError, codecs.charmap_encode, sin, "replace", charmap)

    eleza test_callbacks(self):
        eleza handler1(exc):
            r = range(exc.start, exc.end)
            ikiwa isinstance(exc, UnicodeEncodeError):
                l = ["<%d>" % ord(exc.object[pos]) kila pos kwenye r]
            lasivyo isinstance(exc, UnicodeDecodeError):
                l = ["<%d>" % exc.object[pos] kila pos kwenye r]
            isipokua:
                ashiria TypeError("don't know how to handle %r" % exc)
            rudisha ("[%s]" % "".join(l), exc.end)

        codecs.register_error("test.handler1", handler1)

        eleza handler2(exc):
            ikiwa sio isinstance(exc, UnicodeDecodeError):
                ashiria TypeError("don't know how to handle %r" % exc)
            l = ["<%d>" % exc.object[pos] kila pos kwenye range(exc.start, exc.end)]
            rudisha ("[%s]" % "".join(l), exc.end+1) # skip one character

        codecs.register_error("test.handler2", handler2)

        s = b"\x00\x81\x7f\x80\xff"

        self.assertEqual(
            s.decode("ascii", "test.handler1"),
            "\x00[<129>]\x7f[<128>][<255>]"
        )
        self.assertEqual(
            s.decode("ascii", "test.handler2"),
            "\x00[<129>][<128>]"
        )

        self.assertEqual(
            b"\\u3042\\u3xxx".decode("unicode-escape", "test.handler1"),
            "\u3042[<92><117><51>]xxx"
        )

        self.assertEqual(
            b"\\u3042\\u3xx".decode("unicode-escape", "test.handler1"),
            "\u3042[<92><117><51>]xx"
        )

        self.assertEqual(
            codecs.charmap_decode(b"abc", "test.handler1", {ord("a"): "z"})[0],
            "z[<98>][<99>]"
        )

        self.assertEqual(
            "g\xfc\xdfrk".encode("ascii", "test.handler1"),
            b"g[<252><223>]rk"
        )

        self.assertEqual(
            "g\xfc\xdf".encode("ascii", "test.handler1"),
            b"g[<252><223>]"
        )

    eleza test_longstrings(self):
        # test long strings to check kila memory overflow problems
        errors = [ "strict", "ignore", "replace", "xmlcharrefreplace",
                   "backslashreplace", "namereplace"]
        # register the handlers under different names,
        # to prevent the codec kutoka recognizing the name
        kila err kwenye errors:
            codecs.register_error("test." + err, codecs.lookup_error(err))
        l = 1000
        errors += [ "test." + err kila err kwenye errors ]
        kila uni kwenye [ s*l kila s kwenye ("x", "\u3042", "a\xe4") ]:
            kila enc kwenye ("ascii", "latin-1", "iso-8859-1", "iso-8859-15",
                        "utf-8", "utf-7", "utf-16", "utf-32"):
                kila err kwenye errors:
                    jaribu:
                        uni.encode(enc, err)
                    tatizo UnicodeError:
                        pita

    eleza check_exceptionobjectargs(self, exctype, args, msg):
        # Test UnicodeError subclasses: construction, attribute assignment na __str__ conversion
        # check ukijumuisha one missing argument
        self.assertRaises(TypeError, exctype, *args[:-1])
        # check ukijumuisha one argument too much
        self.assertRaises(TypeError, exctype, *(args + ["too much"]))
        # check ukijumuisha one argument of the wrong type
        wrongargs = [ "spam", b"eggs", b"spam", 42, 1.0, Tupu ]
        kila i kwenye range(len(args)):
            kila wrongarg kwenye wrongargs:
                ikiwa type(wrongarg) ni type(args[i]):
                    endelea
                # build argument array
                callargs = []
                kila j kwenye range(len(args)):
                    ikiwa i==j:
                        callargs.append(wrongarg)
                    isipokua:
                        callargs.append(args[i])
                self.assertRaises(TypeError, exctype, *callargs)

        # check ukijumuisha the correct number na type of arguments
        exc = exctype(*args)
        self.assertEqual(str(exc), msg)

    eleza test_unicodeencodeerror(self):
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "g\xfcrk", 1, 2, "ouch"],
            "'ascii' codec can't encode character '\\xfc' kwenye position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "g\xfcrk", 1, 4, "ouch"],
            "'ascii' codec can't encode characters kwenye position 1-3: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "\xfcx", 0, 1, "ouch"],
            "'ascii' codec can't encode character '\\xfc' kwenye position 0: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "\u0100x", 0, 1, "ouch"],
            "'ascii' codec can't encode character '\\u0100' kwenye position 0: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "\uffffx", 0, 1, "ouch"],
            "'ascii' codec can't encode character '\\uffff' kwenye position 0: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeEncodeError,
            ["ascii", "\U00010000x", 0, 1, "ouch"],
            "'ascii' codec can't encode character '\\U00010000' kwenye position 0: ouch"
        )

    eleza test_unicodedecodeerror(self):
        self.check_exceptionobjectargs(
            UnicodeDecodeError,
            ["ascii", bytearray(b"g\xfcrk"), 1, 2, "ouch"],
            "'ascii' codec can't decode byte 0xfc kwenye position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeDecodeError,
            ["ascii", bytearray(b"g\xfcrk"), 1, 3, "ouch"],
            "'ascii' codec can't decode bytes kwenye position 1-2: ouch"
        )

    eleza test_unicodetranslateerror(self):
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\xfcrk", 1, 2, "ouch"],
            "can't translate character '\\xfc' kwenye position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\u0100rk", 1, 2, "ouch"],
            "can't translate character '\\u0100' kwenye position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\uffffrk", 1, 2, "ouch"],
            "can't translate character '\\uffff' kwenye position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\U00010000rk", 1, 2, "ouch"],
            "can't translate character '\\U00010000' kwenye position 1: ouch"
        )
        self.check_exceptionobjectargs(
            UnicodeTranslateError,
            ["g\xfcrk", 1, 3, "ouch"],
            "can't translate characters kwenye position 1-2: ouch"
        )

    eleza test_badandgoodstrictexceptions(self):
        # "strict" complains about a non-exception pitaed kwenye
        self.assertRaises(
            TypeError,
            codecs.strict_errors,
            42
        )
        # "strict" complains about the wrong exception type
        self.assertRaises(
            Exception,
            codecs.strict_errors,
            Exception("ouch")
        )

        # If the correct exception ni pitaed in, "strict" raises it
        self.assertRaises(
            UnicodeEncodeError,
            codecs.strict_errors,
            UnicodeEncodeError("ascii", "\u3042", 0, 1, "ouch")
        )
        self.assertRaises(
            UnicodeDecodeError,
            codecs.strict_errors,
            UnicodeDecodeError("ascii", bytearray(b"\xff"), 0, 1, "ouch")
        )
        self.assertRaises(
            UnicodeTranslateError,
            codecs.strict_errors,
            UnicodeTranslateError("\u3042", 0, 1, "ouch")
        )

    eleza test_badandgoodignoreexceptions(self):
        # "ignore" complains about a non-exception pitaed kwenye
        self.assertRaises(
           TypeError,
           codecs.ignore_errors,
           42
        )
        # "ignore" complains about the wrong exception type
        self.assertRaises(
           TypeError,
           codecs.ignore_errors,
           UnicodeError("ouch")
        )
        # If the correct exception ni pitaed in, "ignore" returns an empty replacement
        self.assertEqual(
            codecs.ignore_errors(
                UnicodeEncodeError("ascii", "a\u3042b", 1, 2, "ouch")),
            ("", 2)
        )
        self.assertEqual(
            codecs.ignore_errors(
                UnicodeDecodeError("ascii", bytearray(b"a\xffb"), 1, 2, "ouch")),
            ("", 2)
        )
        self.assertEqual(
            codecs.ignore_errors(
                UnicodeTranslateError("a\u3042b", 1, 2, "ouch")),
            ("", 2)
        )

    eleza test_badandgoodreplaceexceptions(self):
        # "replace" complains about a non-exception pitaed kwenye
        self.assertRaises(
           TypeError,
           codecs.replace_errors,
           42
        )
        # "replace" complains about the wrong exception type
        self.assertRaises(
           TypeError,
           codecs.replace_errors,
           UnicodeError("ouch")
        )
        self.assertRaises(
            TypeError,
            codecs.replace_errors,
            BadObjectUnicodeEncodeError()
        )
        self.assertRaises(
            TypeError,
            codecs.replace_errors,
            BadObjectUnicodeDecodeError()
        )
        # With the correct exception, "replace" returns an "?" ama "\ufffd" replacement
        self.assertEqual(
            codecs.replace_errors(
                UnicodeEncodeError("ascii", "a\u3042b", 1, 2, "ouch")),
            ("?", 2)
        )
        self.assertEqual(
            codecs.replace_errors(
                UnicodeDecodeError("ascii", bytearray(b"a\xffb"), 1, 2, "ouch")),
            ("\ufffd", 2)
        )
        self.assertEqual(
            codecs.replace_errors(
                UnicodeTranslateError("a\u3042b", 1, 2, "ouch")),
            ("\ufffd", 2)
        )

    eleza test_badandgoodxmlcharrefreplaceexceptions(self):
        # "xmlcharrefreplace" complains about a non-exception pitaed kwenye
        self.assertRaises(
           TypeError,
           codecs.xmlcharrefreplace_errors,
           42
        )
        # "xmlcharrefreplace" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           codecs.xmlcharrefreplace_errors,
           UnicodeError("ouch")
        )
        # "xmlcharrefreplace" can only be used kila encoding
        self.assertRaises(
            TypeError,
            codecs.xmlcharrefreplace_errors,
            UnicodeDecodeError("ascii", bytearray(b"\xff"), 0, 1, "ouch")
        )
        self.assertRaises(
            TypeError,
            codecs.xmlcharrefreplace_errors,
            UnicodeTranslateError("\u3042", 0, 1, "ouch")
        )
        # Use the correct exception
        cs = (0, 1, 9, 10, 99, 100, 999, 1000, 9999, 10000, 99999, 100000,
              999999, 1000000)
        cs += (0xd800, 0xdfff)
        s = "".join(chr(c) kila c kwenye cs)
        self.assertEqual(
            codecs.xmlcharrefreplace_errors(
                UnicodeEncodeError("ascii", "a" + s + "b",
                                   1, 1 + len(s), "ouch")
            ),
            ("".join("&#%d;" % c kila c kwenye cs), 1 + len(s))
        )

    eleza test_badandgoodbackslashreplaceexceptions(self):
        # "backslashreplace" complains about a non-exception pitaed kwenye
        self.assertRaises(
           TypeError,
           codecs.backslashreplace_errors,
           42
        )
        # "backslashreplace" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           codecs.backslashreplace_errors,
           UnicodeError("ouch")
        )
        # Use the correct exception
        tests = [
            ("\u3042", "\\u3042"),
            ("\n", "\\x0a"),
            ("a", "\\x61"),
            ("\x00", "\\x00"),
            ("\xff", "\\xff"),
            ("\u0100", "\\u0100"),
            ("\uffff", "\\uffff"),
            ("\U00010000", "\\U00010000"),
            ("\U0010ffff", "\\U0010ffff"),
            # Lone surrogates
            ("\ud800", "\\ud800"),
            ("\udfff", "\\udfff"),
            ("\ud800\udfff", "\\ud800\\udfff"),
        ]
        kila s, r kwenye tests:
            ukijumuisha self.subTest(str=s):
                self.assertEqual(
                    codecs.backslashreplace_errors(
                        UnicodeEncodeError("ascii", "a" + s + "b",
                                           1, 1 + len(s), "ouch")),
                    (r, 1 + len(s))
                )
                self.assertEqual(
                    codecs.backslashreplace_errors(
                        UnicodeTranslateError("a" + s + "b",
                                              1, 1 + len(s), "ouch")),
                    (r, 1 + len(s))
                )
        tests = [
            (b"a", "\\x61"),
            (b"\n", "\\x0a"),
            (b"\x00", "\\x00"),
            (b"\xff", "\\xff"),
        ]
        kila b, r kwenye tests:
            ukijumuisha self.subTest(bytes=b):
                self.assertEqual(
                    codecs.backslashreplace_errors(
                        UnicodeDecodeError("ascii", bytearray(b"a" + b + b"b"),
                                           1, 2, "ouch")),
                    (r, 2)
                )

    eleza test_badandgoodnamereplaceexceptions(self):
        # "namereplace" complains about a non-exception pitaed kwenye
        self.assertRaises(
           TypeError,
           codecs.namereplace_errors,
           42
        )
        # "namereplace" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           codecs.namereplace_errors,
           UnicodeError("ouch")
        )
        # "namereplace" can only be used kila encoding
        self.assertRaises(
            TypeError,
            codecs.namereplace_errors,
            UnicodeDecodeError("ascii", bytearray(b"\xff"), 0, 1, "ouch")
        )
        self.assertRaises(
            TypeError,
            codecs.namereplace_errors,
            UnicodeTranslateError("\u3042", 0, 1, "ouch")
        )
        # Use the correct exception
        tests = [
            ("\u3042", "\\N{HIRAGANA LETTER A}"),
            ("\x00", "\\x00"),
            ("\ufbf9", "\\N{ARABIC LIGATURE UIGHUR KIRGHIZ YEH WITH "
                       "HAMZA ABOVE WITH ALEF MAKSURA ISOLATED FORM}"),
            ("\U000e007f", "\\N{CANCEL TAG}"),
            ("\U0010ffff", "\\U0010ffff"),
            # Lone surrogates
            ("\ud800", "\\ud800"),
            ("\udfff", "\\udfff"),
            ("\ud800\udfff", "\\ud800\\udfff"),
        ]
        kila s, r kwenye tests:
            ukijumuisha self.subTest(str=s):
                self.assertEqual(
                    codecs.namereplace_errors(
                        UnicodeEncodeError("ascii", "a" + s + "b",
                                           1, 1 + len(s), "ouch")),
                    (r, 1 + len(s))
                )

    eleza test_badandgoodsurrogateescapeexceptions(self):
        surrogateescape_errors = codecs.lookup_error('surrogateescape')
        # "surrogateescape" complains about a non-exception pitaed kwenye
        self.assertRaises(
           TypeError,
           surrogateescape_errors,
           42
        )
        # "surrogateescape" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           surrogateescape_errors,
           UnicodeError("ouch")
        )
        # "surrogateescape" can sio be used kila translating
        self.assertRaises(
            TypeError,
            surrogateescape_errors,
            UnicodeTranslateError("\udc80", 0, 1, "ouch")
        )
        # Use the correct exception
        kila s kwenye ("a", "\udc7f", "\udd00"):
            ukijumuisha self.subTest(str=s):
                self.assertRaises(
                    UnicodeEncodeError,
                    surrogateescape_errors,
                    UnicodeEncodeError("ascii", s, 0, 1, "ouch")
                )
        self.assertEqual(
            surrogateescape_errors(
                UnicodeEncodeError("ascii", "a\udc80b", 1, 2, "ouch")),
            (b"\x80", 2)
        )
        self.assertRaises(
            UnicodeDecodeError,
            surrogateescape_errors,
            UnicodeDecodeError("ascii", bytearray(b"a"), 0, 1, "ouch")
        )
        self.assertEqual(
            surrogateescape_errors(
                UnicodeDecodeError("ascii", bytearray(b"a\x80b"), 1, 2, "ouch")),
            ("\udc80", 2)
        )

    eleza test_badandgoodsurrogatepitaexceptions(self):
        surrogatepita_errors = codecs.lookup_error('surrogatepita')
        # "surrogatepita" complains about a non-exception pitaed kwenye
        self.assertRaises(
           TypeError,
           surrogatepita_errors,
           42
        )
        # "surrogatepita" complains about the wrong exception types
        self.assertRaises(
           TypeError,
           surrogatepita_errors,
           UnicodeError("ouch")
        )
        # "surrogatepita" can sio be used kila translating
        self.assertRaises(
            TypeError,
            surrogatepita_errors,
            UnicodeTranslateError("\ud800", 0, 1, "ouch")
        )
        # Use the correct exception
        kila enc kwenye ("utf-8", "utf-16le", "utf-16be", "utf-32le", "utf-32be"):
            ukijumuisha self.subTest(encoding=enc):
                self.assertRaises(
                    UnicodeEncodeError,
                    surrogatepita_errors,
                    UnicodeEncodeError(enc, "a", 0, 1, "ouch")
                )
                self.assertRaises(
                    UnicodeDecodeError,
                    surrogatepita_errors,
                    UnicodeDecodeError(enc, "a".encode(enc), 0, 1, "ouch")
                )
        kila s kwenye ("\ud800", "\udfff", "\ud800\udfff"):
            ukijumuisha self.subTest(str=s):
                self.assertRaises(
                    UnicodeEncodeError,
                    surrogatepita_errors,
                    UnicodeEncodeError("ascii", s, 0, len(s), "ouch")
                )
        tests = [
            ("utf-8", "\ud800", b'\xed\xa0\x80', 3),
            ("utf-16le", "\ud800", b'\x00\xd8', 2),
            ("utf-16be", "\ud800", b'\xd8\x00', 2),
            ("utf-32le", "\ud800", b'\x00\xd8\x00\x00', 4),
            ("utf-32be", "\ud800", b'\x00\x00\xd8\x00', 4),
            ("utf-8", "\udfff", b'\xed\xbf\xbf', 3),
            ("utf-16le", "\udfff", b'\xff\xdf', 2),
            ("utf-16be", "\udfff", b'\xdf\xff', 2),
            ("utf-32le", "\udfff", b'\xff\xdf\x00\x00', 4),
            ("utf-32be", "\udfff", b'\x00\x00\xdf\xff', 4),
            ("utf-8", "\ud800\udfff", b'\xed\xa0\x80\xed\xbf\xbf', 3),
            ("utf-16le", "\ud800\udfff", b'\x00\xd8\xff\xdf', 2),
            ("utf-16be", "\ud800\udfff", b'\xd8\x00\xdf\xff', 2),
            ("utf-32le", "\ud800\udfff", b'\x00\xd8\x00\x00\xff\xdf\x00\x00', 4),
            ("utf-32be", "\ud800\udfff", b'\x00\x00\xd8\x00\x00\x00\xdf\xff', 4),
        ]
        kila enc, s, b, n kwenye tests:
            ukijumuisha self.subTest(encoding=enc, str=s, bytes=b):
                self.assertEqual(
                    surrogatepita_errors(
                        UnicodeEncodeError(enc, "a" + s + "b",
                                           1, 1 + len(s), "ouch")),
                    (b, 1 + len(s))
                )
                self.assertEqual(
                    surrogatepita_errors(
                        UnicodeDecodeError(enc, bytearray(b"a" + b[:n] + b"b"),
                                           1, 1 + n, "ouch")),
                    (s[:1], 1 + n)
                )

    eleza test_badhandlerresults(self):
        results = ( 42, "foo", (1,2,3), ("foo", 1, 3), ("foo", Tupu), ("foo",), ("foo", 1, 3), ("foo", Tupu), ("foo",) )
        encs = ("ascii", "latin-1", "iso-8859-1", "iso-8859-15")

        kila res kwenye results:
            codecs.register_error("test.badhandler", lambda x: res)
            kila enc kwenye encs:
                self.assertRaises(
                    TypeError,
                    "\u3042".encode,
                    enc,
                    "test.badhandler"
                )
            kila (enc, bytes) kwenye (
                ("ascii", b"\xff"),
                ("utf-8", b"\xff"),
                ("utf-7", b"+x-"),
            ):
                self.assertRaises(
                    TypeError,
                    bytes.decode,
                    enc,
                    "test.badhandler"
                )

    eleza test_lookup(self):
        self.assertEqual(codecs.strict_errors, codecs.lookup_error("strict"))
        self.assertEqual(codecs.ignore_errors, codecs.lookup_error("ignore"))
        self.assertEqual(codecs.strict_errors, codecs.lookup_error("strict"))
        self.assertEqual(
            codecs.xmlcharrefreplace_errors,
            codecs.lookup_error("xmlcharrefreplace")
        )
        self.assertEqual(
            codecs.backslashreplace_errors,
            codecs.lookup_error("backslashreplace")
        )
        self.assertEqual(
            codecs.namereplace_errors,
            codecs.lookup_error("namereplace")
        )

    eleza test_unencodablereplacement(self):
        eleza unencrepl(exc):
            ikiwa isinstance(exc, UnicodeEncodeError):
                rudisha ("\u4242", exc.end)
            isipokua:
                ashiria TypeError("don't know how to handle %r" % exc)
        codecs.register_error("test.unencreplhandler", unencrepl)
        kila enc kwenye ("ascii", "iso-8859-1", "iso-8859-15"):
            self.assertRaises(
                UnicodeEncodeError,
                "\u4242".encode,
                enc,
                "test.unencreplhandler"
            )

    eleza test_badregistercall(self):
        # enhance coverage of:
        # Modules/_codecsmodule.c::register_error()
        # Python/codecs.c::PyCodec_RegisterError()
        self.assertRaises(TypeError, codecs.register_error, 42)
        self.assertRaises(TypeError, codecs.register_error, "test.dummy", 42)

    eleza test_badlookupcall(self):
        # enhance coverage of:
        # Modules/_codecsmodule.c::lookup_error()
        self.assertRaises(TypeError, codecs.lookup_error)

    eleza test_unknownhandler(self):
        # enhance coverage of:
        # Modules/_codecsmodule.c::lookup_error()
        self.assertRaises(LookupError, codecs.lookup_error, "test.unknown")

    eleza test_xmlcharrefvalues(self):
        # enhance coverage of:
        # Python/codecs.c::PyCodec_XMLCharRefReplaceErrors()
        # na inline implementations
        v = (1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000,
             500000, 1000000)
        s = "".join([chr(x) kila x kwenye v])
        codecs.register_error("test.xmlcharrefreplace", codecs.xmlcharrefreplace_errors)
        kila enc kwenye ("ascii", "iso-8859-15"):
            kila err kwenye ("xmlcharrefreplace", "test.xmlcharrefreplace"):
                s.encode(enc, err)

    eleza test_decodehelper(self):
        # enhance coverage of:
        # Objects/unicodeobject.c::unicode_decode_call_errorhandler()
        # na callers
        self.assertRaises(LookupError, b"\xff".decode, "ascii", "test.unknown")

        eleza baddecodereturn1(exc):
            rudisha 42
        codecs.register_error("test.baddecodereturn1", baddecodereturn1)
        self.assertRaises(TypeError, b"\xff".decode, "ascii", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\".decode, "unicode-escape", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\x0".decode, "unicode-escape", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\x0y".decode, "unicode-escape", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\Uffffeeee".decode, "unicode-escape", "test.baddecodereturn1")
        self.assertRaises(TypeError, b"\\uyyyy".decode, "raw-unicode-escape", "test.baddecodereturn1")

        eleza baddecodereturn2(exc):
            rudisha ("?", Tupu)
        codecs.register_error("test.baddecodereturn2", baddecodereturn2)
        self.assertRaises(TypeError, b"\xff".decode, "ascii", "test.baddecodereturn2")

        handler = PosReturn()
        codecs.register_error("test.posreturn", handler.handle)

        # Valid negative position
        handler.pos = -1
        self.assertEqual(b"\xff0".decode("ascii", "test.posreturn"), "<?>0")

        # Valid negative position
        handler.pos = -2
        self.assertEqual(b"\xff0".decode("ascii", "test.posreturn"), "<?><?>")

        # Negative position out of bounds
        handler.pos = -3
        self.assertRaises(IndexError, b"\xff0".decode, "ascii", "test.posreturn")

        # Valid positive position
        handler.pos = 1
        self.assertEqual(b"\xff0".decode("ascii", "test.posreturn"), "<?>0")

        # Largest valid positive position (one beyond end of input)
        handler.pos = 2
        self.assertEqual(b"\xff0".decode("ascii", "test.posreturn"), "<?>")

        # Invalid positive position
        handler.pos = 3
        self.assertRaises(IndexError, b"\xff0".decode, "ascii", "test.posreturn")

        # Restart at the "0"
        handler.pos = 6
        self.assertEqual(b"\\uyyyy0".decode("raw-unicode-escape", "test.posreturn"), "<?>0")

        kundi D(dict):
            eleza __getitem__(self, key):
                ashiria ValueError
        self.assertRaises(UnicodeError, codecs.charmap_decode, b"\xff", "strict", {0xff: Tupu})
        self.assertRaises(ValueError, codecs.charmap_decode, b"\xff", "strict", D())
        self.assertRaises(TypeError, codecs.charmap_decode, b"\xff", "strict", {0xff: sys.maxunicode+1})

    eleza test_encodehelper(self):
        # enhance coverage of:
        # Objects/unicodeobject.c::unicode_encode_call_errorhandler()
        # na callers
        self.assertRaises(LookupError, "\xff".encode, "ascii", "test.unknown")

        eleza badencodereturn1(exc):
            rudisha 42
        codecs.register_error("test.badencodereturn1", badencodereturn1)
        self.assertRaises(TypeError, "\xff".encode, "ascii", "test.badencodereturn1")

        eleza badencodereturn2(exc):
            rudisha ("?", Tupu)
        codecs.register_error("test.badencodereturn2", badencodereturn2)
        self.assertRaises(TypeError, "\xff".encode, "ascii", "test.badencodereturn2")

        handler = PosReturn()
        codecs.register_error("test.posreturn", handler.handle)

        # Valid negative position
        handler.pos = -1
        self.assertEqual("\xff0".encode("ascii", "test.posreturn"), b"<?>0")

        # Valid negative position
        handler.pos = -2
        self.assertEqual("\xff0".encode("ascii", "test.posreturn"), b"<?><?>")

        # Negative position out of bounds
        handler.pos = -3
        self.assertRaises(IndexError, "\xff0".encode, "ascii", "test.posreturn")

        # Valid positive position
        handler.pos = 1
        self.assertEqual("\xff0".encode("ascii", "test.posreturn"), b"<?>0")

        # Largest valid positive position (one beyond end of input
        handler.pos = 2
        self.assertEqual("\xff0".encode("ascii", "test.posreturn"), b"<?>")

        # Invalid positive position
        handler.pos = 3
        self.assertRaises(IndexError, "\xff0".encode, "ascii", "test.posreturn")

        handler.pos = 0

        kundi D(dict):
            eleza __getitem__(self, key):
                ashiria ValueError
        kila err kwenye ("strict", "replace", "xmlcharrefreplace",
                    "backslashreplace", "namereplace", "test.posreturn"):
            self.assertRaises(UnicodeError, codecs.charmap_encode, "\xff", err, {0xff: Tupu})
            self.assertRaises(ValueError, codecs.charmap_encode, "\xff", err, D())
            self.assertRaises(TypeError, codecs.charmap_encode, "\xff", err, {0xff: 300})

    eleza test_translatehelper(self):
        # enhance coverage of:
        # Objects/unicodeobject.c::unicode_encode_call_errorhandler()
        # na callers
        # (Unfortunately the errors argument ni sio directly accessible
        # kutoka Python, so we can't test that much)
        kundi D(dict):
            eleza __getitem__(self, key):
                ashiria ValueError
        #self.assertRaises(ValueError, "\xff".translate, D())
        self.assertRaises(ValueError, "\xff".translate, {0xff: sys.maxunicode+1})
        self.assertRaises(TypeError, "\xff".translate, {0xff: ()})

    eleza test_bug828737(self):
        charmap = {
            ord("&"): "&amp;",
            ord("<"): "&lt;",
            ord(">"): "&gt;",
            ord('"'): "&quot;",
        }

        kila n kwenye (1, 10, 100, 1000):
            text = 'abc<def>ghi'*n
            text.translate(charmap)

    eleza test_mutatingdecodehandler(self):
        baddata = [
            ("ascii", b"\xff"),
            ("utf-7", b"++"),
            ("utf-8",  b"\xff"),
            ("utf-16", b"\xff"),
            ("utf-32", b"\xff"),
            ("unicode-escape", b"\\u123g"),
            ("raw-unicode-escape", b"\\u123g"),
        ]

        eleza replacing(exc):
            ikiwa isinstance(exc, UnicodeDecodeError):
                exc.object = 42
                rudisha ("\u4242", 0)
            isipokua:
                ashiria TypeError("don't know how to handle %r" % exc)
        codecs.register_error("test.replacing", replacing)

        kila (encoding, data) kwenye baddata:
            ukijumuisha self.assertRaises(TypeError):
                data.decode(encoding, "test.replacing")

        eleza mutating(exc):
            ikiwa isinstance(exc, UnicodeDecodeError):
                exc.object = b""
                rudisha ("\u4242", 0)
            isipokua:
                ashiria TypeError("don't know how to handle %r" % exc)
        codecs.register_error("test.mutating", mutating)
        # If the decoder doesn't pick up the modified input the following
        # will lead to an endless loop
        kila (encoding, data) kwenye baddata:
            self.assertEqual(data.decode(encoding, "test.mutating"), "\u4242")

    # issue32583
    eleza test_crashing_decode_handler(self):
        # better generating one more character to fill the extra space slot
        # so kwenye debug build it can steadily fail
        eleza forward_shorter_than_end(exc):
            ikiwa isinstance(exc, UnicodeDecodeError):
                # size one character, 0 < forward < exc.end
                rudisha ('\ufffd', exc.start+1)
            isipokua:
                ashiria TypeError("don't know how to handle %r" % exc)
        codecs.register_error(
            "test.forward_shorter_than_end", forward_shorter_than_end)

        self.assertEqual(
            b'\xd8\xd8\xd8\xd8\xd8\x00\x00\x00'.decode(
                'utf-16-le', 'test.forward_shorter_than_end'),
            '\ufffd\ufffd\ufffd\ufffd\xd8\x00'
        )
        self.assertEqual(
            b'\xd8\xd8\xd8\xd8\x00\xd8\x00\x00'.decode(
                'utf-16-be', 'test.forward_shorter_than_end'),
            '\ufffd\ufffd\ufffd\ufffd\xd8\x00'
        )
        self.assertEqual(
            b'\x11\x11\x11\x11\x11\x00\x00\x00\x00\x00\x00'.decode(
                'utf-32-le', 'test.forward_shorter_than_end'),
            '\ufffd\ufffd\ufffd\u1111\x00'
        )
        self.assertEqual(
            b'\x11\x11\x11\x00\x00\x11\x11\x00\x00\x00\x00'.decode(
                'utf-32-be', 'test.forward_shorter_than_end'),
            '\ufffd\ufffd\ufffd\u1111\x00'
        )

        eleza replace_with_long(exc):
            ikiwa isinstance(exc, UnicodeDecodeError):
                exc.object = b"\x00" * 8
                rudisha ('\ufffd', exc.start)
            isipokua:
                ashiria TypeError("don't know how to handle %r" % exc)
        codecs.register_error("test.replace_with_long", replace_with_long)

        self.assertEqual(
            b'\x00'.decode('utf-16', 'test.replace_with_long'),
            '\ufffd\x00\x00\x00\x00'
        )
        self.assertEqual(
            b'\x00'.decode('utf-32', 'test.replace_with_long'),
            '\ufffd\x00\x00'
        )


    eleza test_fake_error_class(self):
        handlers = [
            codecs.strict_errors,
            codecs.ignore_errors,
            codecs.replace_errors,
            codecs.backslashreplace_errors,
            codecs.namereplace_errors,
            codecs.xmlcharrefreplace_errors,
            codecs.lookup_error('surrogateescape'),
            codecs.lookup_error('surrogatepita'),
        ]
        kila cls kwenye UnicodeEncodeError, UnicodeDecodeError, UnicodeTranslateError:
            kundi FakeUnicodeError(str):
                __class__ = cls
            kila handler kwenye handlers:
                ukijumuisha self.subTest(handler=handler, error_class=cls):
                    self.assertRaises(TypeError, handler, FakeUnicodeError())
            kundi FakeUnicodeError(Exception):
                __class__ = cls
            kila handler kwenye handlers:
                ukijumuisha self.subTest(handler=handler, error_class=cls):
                    ukijumuisha self.assertRaises((TypeError, FakeUnicodeError)):
                        handler(FakeUnicodeError())


ikiwa __name__ == "__main__":
    unittest.main()
