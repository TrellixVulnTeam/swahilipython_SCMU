agiza codecs
agiza contextlib
agiza io
agiza locale
agiza sys
agiza unittest
agiza encodings
kutoka unittest agiza mock

kutoka test agiza support

jaribu:
    agiza _testcapi
tatizo ImportError kama exc:
    _testcapi = Tupu

jaribu:
    agiza ctypes
tatizo ImportError:
    ctypes = Tupu
    SIZEOF_WCHAR_T = -1
isipokua:
    SIZEOF_WCHAR_T = ctypes.sizeof(ctypes.c_wchar)

eleza coding_checker(self, coder):
    eleza check(input, expect):
        self.assertEqual(coder(input), (expect, len(input)))
    rudisha check

# On small versions of Windows like Windows IoT ama Windows Nano Server sio all codepages are present
eleza is_code_page_present(cp):
    kutoka ctypes agiza POINTER, WINFUNCTYPE, WinDLL
    kutoka ctypes.wintypes agiza BOOL, UINT, BYTE, WCHAR, UINT, DWORD

    MAX_LEADBYTES = 12  # 5 ranges, 2 bytes ea., 0 term.
    MAX_DEFAULTCHAR = 2 # single ama double byte
    MAX_PATH = 260
    kundi CPINFOEXW(ctypes.Structure):
        _fields_ = [("MaxCharSize", UINT),
                    ("DefaultChar", BYTE*MAX_DEFAULTCHAR),
                    ("LeadByte", BYTE*MAX_LEADBYTES),
                    ("UnicodeDefaultChar", WCHAR),
                    ("CodePage", UINT),
                    ("CodePageName", WCHAR*MAX_PATH)]

    prototype = WINFUNCTYPE(BOOL, UINT, DWORD, POINTER(CPINFOEXW))
    GetCPInfoEx = prototype(("GetCPInfoExW", WinDLL("kernel32")))
    info = CPINFOEXW()
    rudisha GetCPInfoEx(cp, 0, info)

kundi Queue(object):
    """
    queue: write bytes at one end, read bytes kutoka the other end
    """
    eleza __init__(self, buffer):
        self._buffer = buffer

    eleza write(self, chars):
        self._buffer += chars

    eleza read(self, size=-1):
        ikiwa size<0:
            s = self._buffer
            self._buffer = self._buffer[:0] # make empty
            rudisha s
        isipokua:
            s = self._buffer[:size]
            self._buffer = self._buffer[size:]
            rudisha s


kundi MixInCheckStateHandling:
    eleza check_state_handling_decode(self, encoding, u, s):
        kila i kwenye range(len(s)+1):
            d = codecs.getincrementaldecoder(encoding)()
            part1 = d.decode(s[:i])
            state = d.getstate()
            self.assertIsInstance(state[1], int)
            # Check that the condition stated kwenye the documentation for
            # IncrementalDecoder.getstate() holds
            ikiwa sio state[1]:
                # reset decoder to the default state without anything buffered
                d.setstate((state[0][:0], 0))
                # Feeding the previous input may sio produce any output
                self.assertKweli(sio d.decode(state[0]))
                # The decoder must rudisha to the same state
                self.assertEqual(state, d.getstate())
            # Create a new decoder na set it to the state
            # we extracted kutoka the old one
            d = codecs.getincrementaldecoder(encoding)()
            d.setstate(state)
            part2 = d.decode(s[i:], Kweli)
            self.assertEqual(u, part1+part2)

    eleza check_state_handling_encode(self, encoding, u, s):
        kila i kwenye range(len(u)+1):
            d = codecs.getincrementalencoder(encoding)()
            part1 = d.encode(u[:i])
            state = d.getstate()
            d = codecs.getincrementalencoder(encoding)()
            d.setstate(state)
            part2 = d.encode(u[i:], Kweli)
            self.assertEqual(s, part1+part2)


kundi ReadTest(MixInCheckStateHandling):
    eleza check_partial(self, input, partialresults):
        # get a StreamReader kila the encoding na feed the bytestring version
        # of input to the reader byte by byte. Read everything available from
        # the StreamReader na check that the results equal the appropriate
        # entries kutoka partialresults.
        q = Queue(b"")
        r = codecs.getreader(self.encoding)(q)
        result = ""
        kila (c, partialresult) kwenye zip(input.encode(self.encoding), partialresults):
            q.write(bytes([c]))
            result += r.read()
            self.assertEqual(result, partialresult)
        # check that there's nothing left kwenye the buffers
        self.assertEqual(r.read(), "")
        self.assertEqual(r.bytebuffer, b"")

        # do the check again, this time using an incremental decoder
        d = codecs.getincrementaldecoder(self.encoding)()
        result = ""
        kila (c, partialresult) kwenye zip(input.encode(self.encoding), partialresults):
            result += d.decode(bytes([c]))
            self.assertEqual(result, partialresult)
        # check that there's nothing left kwenye the buffers
        self.assertEqual(d.decode(b"", Kweli), "")
        self.assertEqual(d.buffer, b"")

        # Check whether the reset method works properly
        d.reset()
        result = ""
        kila (c, partialresult) kwenye zip(input.encode(self.encoding), partialresults):
            result += d.decode(bytes([c]))
            self.assertEqual(result, partialresult)
        # check that there's nothing left kwenye the buffers
        self.assertEqual(d.decode(b"", Kweli), "")
        self.assertEqual(d.buffer, b"")

        # check iterdecode()
        encoded = input.encode(self.encoding)
        self.assertEqual(
            input,
            "".join(codecs.iterdecode([bytes([c]) kila c kwenye encoded], self.encoding))
        )

    eleza test_readline(self):
        eleza getreader(input):
            stream = io.BytesIO(input.encode(self.encoding))
            rudisha codecs.getreader(self.encoding)(stream)

        eleza readalllines(input, keepends=Kweli, size=Tupu):
            reader = getreader(input)
            lines = []
            wakati Kweli:
                line = reader.readline(size=size, keepends=keepends)
                ikiwa sio line:
                    koma
                lines.append(line)
            rudisha "|".join(lines)

        s = "foo\nbar\r\nbaz\rspam\u2028eggs"
        sexpected = "foo\n|bar\r\n|baz\r|spam\u2028|eggs"
        sexpectednoends = "foo|bar|baz|spam|eggs"
        self.assertEqual(readalllines(s, Kweli), sexpected)
        self.assertEqual(readalllines(s, Uongo), sexpectednoends)
        self.assertEqual(readalllines(s, Kweli, 10), sexpected)
        self.assertEqual(readalllines(s, Uongo, 10), sexpectednoends)

        lineends = ("\n", "\r\n", "\r", "\u2028")
        # Test long lines (multiple calls to read() kwenye readline())
        vw = []
        vwo = []
        kila (i, lineend) kwenye enumerate(lineends):
            vw.append((i*200+200)*"\u3042" + lineend)
            vwo.append((i*200+200)*"\u3042")
        self.assertEqual(readalllines("".join(vw), Kweli), "|".join(vw))
        self.assertEqual(readalllines("".join(vw), Uongo), "|".join(vwo))

        # Test lines where the first read might end ukijumuisha \r, so the
        # reader has to look ahead whether this ni a lone \r ama a \r\n
        kila size kwenye range(80):
            kila lineend kwenye lineends:
                s = 10*(size*"a" + lineend + "xxx\n")
                reader = getreader(s)
                kila i kwenye range(10):
                    self.assertEqual(
                        reader.readline(keepends=Kweli),
                        size*"a" + lineend,
                    )
                    self.assertEqual(
                        reader.readline(keepends=Kweli),
                        "xxx\n",
                    )
                reader = getreader(s)
                kila i kwenye range(10):
                    self.assertEqual(
                        reader.readline(keepends=Uongo),
                        size*"a",
                    )
                    self.assertEqual(
                        reader.readline(keepends=Uongo),
                        "xxx",
                    )

    eleza test_mixed_readline_and_read(self):
        lines = ["Humpty Dumpty sat on a wall,\n",
                 "Humpty Dumpty had a great fall.\r\n",
                 "All the king's horses na all the king's men\r",
                 "Couldn't put Humpty together again."]
        data = ''.join(lines)
        eleza getreader():
            stream = io.BytesIO(data.encode(self.encoding))
            rudisha codecs.getreader(self.encoding)(stream)

        # Issue #8260: Test readline() followed by read()
        f = getreader()
        self.assertEqual(f.readline(), lines[0])
        self.assertEqual(f.read(), ''.join(lines[1:]))
        self.assertEqual(f.read(), '')

        # Issue #32110: Test readline() followed by read(n)
        f = getreader()
        self.assertEqual(f.readline(), lines[0])
        self.assertEqual(f.read(1), lines[1][0])
        self.assertEqual(f.read(0), '')
        self.assertEqual(f.read(100), data[len(lines[0]) + 1:][:100])

        # Issue #16636: Test readline() followed by readlines()
        f = getreader()
        self.assertEqual(f.readline(), lines[0])
        self.assertEqual(f.readlines(), lines[1:])
        self.assertEqual(f.read(), '')

        # Test read(n) followed by read()
        f = getreader()
        self.assertEqual(f.read(size=40, chars=5), data[:5])
        self.assertEqual(f.read(), data[5:])
        self.assertEqual(f.read(), '')

        # Issue #32110: Test read(n) followed by read(n)
        f = getreader()
        self.assertEqual(f.read(size=40, chars=5), data[:5])
        self.assertEqual(f.read(1), data[5])
        self.assertEqual(f.read(0), '')
        self.assertEqual(f.read(100), data[6:106])

        # Issue #12446: Test read(n) followed by readlines()
        f = getreader()
        self.assertEqual(f.read(size=40, chars=5), data[:5])
        self.assertEqual(f.readlines(), [lines[0][5:]] + lines[1:])
        self.assertEqual(f.read(), '')

    eleza test_bug1175396(self):
        s = [
            '<%!--===================================================\r\n',
            '    BLOG index page: show recent articles,\r\n',
            '    today\'s articles, ama articles of a specific date.\r\n',
            '========================================================--%>\r\n',
            '<%@inputencoding="ISO-8859-1"%>\r\n',
            '<%@pagetemplate=TEMPLATE.y%>\r\n',
            '<%@import=agiza frog.util, frog%>\r\n',
            '<%@import=agiza frog.objects%>\r\n',
            '<%@import=kutoka frog.storageerrors agiza StorageError%>\r\n',
            '<%\r\n',
            '\r\n',
            'agiza logging\r\n',
            'log=logging.getLogger("Snakelets.logger")\r\n',
            '\r\n',
            '\r\n',
            'user=self.SessionCtx.user\r\n',
            'storageEngine=self.SessionCtx.storageEngine\r\n',
            '\r\n',
            '\r\n',
            'eleza readArticlesFromDate(date, count=Tupu):\r\n',
            '    entryids=storageEngine.listBlogEntries(date)\r\n',
            '    entryids.reverse() # descending\r\n',
            '    ikiwa count:\r\n',
            '        entryids=entryids[:count]\r\n',
            '    jaribu:\r\n',
            '        rudisha [ frog.objects.BlogEntry.load(storageEngine, date, Id) kila Id kwenye entryids ]\r\n',
            '    tatizo StorageError,x:\r\n',
            '        log.error("Error loading articles: "+str(x))\r\n',
            '        self.abort("cannot load articles")\r\n',
            '\r\n',
            'showdate=Tupu\r\n',
            '\r\n',
            'arg=self.Request.getArg()\r\n',
            'ikiwa arg=="today":\r\n',
            '    #-------------------- TODAY\'S ARTICLES\r\n',
            '    self.write("<h2>Today\'s articles</h2>")\r\n',
            '    showdate = frog.util.isodatestr() \r\n',
            '    entries = readArticlesFromDate(showdate)\r\n',
            'lasivyo arg=="active":\r\n',
            '    #-------------------- ACTIVE ARTICLES redirect\r\n',
            '    self.Yredirect("active.y")\r\n',
            'lasivyo arg=="login":\r\n',
            '    #-------------------- LOGIN PAGE redirect\r\n',
            '    self.Yredirect("login.y")\r\n',
            'lasivyo arg=="date":\r\n',
            '    #-------------------- ARTICLES OF A SPECIFIC DATE\r\n',
            '    showdate = self.Request.getParameter("date")\r\n',
            '    self.write("<h2>Articles written on %s</h2>"% frog.util.mediumdatestr(showdate))\r\n',
            '    entries = readArticlesFromDate(showdate)\r\n',
            'isipokua:\r\n',
            '    #-------------------- RECENT ARTICLES\r\n',
            '    self.write("<h2>Recent articles</h2>")\r\n',
            '    dates=storageEngine.listBlogEntryDates()\r\n',
            '    ikiwa dates:\r\n',
            '        entries=[]\r\n',
            '        SHOWAMOUNT=10\r\n',
            '        kila showdate kwenye dates:\r\n',
            '            entries.extend( readArticlesFromDate(showdate, SHOWAMOUNT-len(entries)) )\r\n',
            '            ikiwa len(entries)>=SHOWAMOUNT:\r\n',
            '                koma\r\n',
            '                \r\n',
        ]
        stream = io.BytesIO("".join(s).encode(self.encoding))
        reader = codecs.getreader(self.encoding)(stream)
        kila (i, line) kwenye enumerate(reader):
            self.assertEqual(line, s[i])

    eleza test_readlinequeue(self):
        q = Queue(b"")
        writer = codecs.getwriter(self.encoding)(q)
        reader = codecs.getreader(self.encoding)(q)

        # No lineends
        writer.write("foo\r")
        self.assertEqual(reader.readline(keepends=Uongo), "foo")
        writer.write("\nbar\r")
        self.assertEqual(reader.readline(keepends=Uongo), "")
        self.assertEqual(reader.readline(keepends=Uongo), "bar")
        writer.write("baz")
        self.assertEqual(reader.readline(keepends=Uongo), "baz")
        self.assertEqual(reader.readline(keepends=Uongo), "")

        # Lineends
        writer.write("foo\r")
        self.assertEqual(reader.readline(keepends=Kweli), "foo\r")
        writer.write("\nbar\r")
        self.assertEqual(reader.readline(keepends=Kweli), "\n")
        self.assertEqual(reader.readline(keepends=Kweli), "bar\r")
        writer.write("baz")
        self.assertEqual(reader.readline(keepends=Kweli), "baz")
        self.assertEqual(reader.readline(keepends=Kweli), "")
        writer.write("foo\r\n")
        self.assertEqual(reader.readline(keepends=Kweli), "foo\r\n")

    eleza test_bug1098990_a(self):
        s1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy\r\n"
        s2 = "offending line: ladfj askldfj klasdj fskla dfzaskdj fasklfj laskd fjasklfzzzzaa%whereisthis!!!\r\n"
        s3 = "next line.\r\n"

        s = (s1+s2+s3).encode(self.encoding)
        stream = io.BytesIO(s)
        reader = codecs.getreader(self.encoding)(stream)
        self.assertEqual(reader.readline(), s1)
        self.assertEqual(reader.readline(), s2)
        self.assertEqual(reader.readline(), s3)
        self.assertEqual(reader.readline(), "")

    eleza test_bug1098990_b(self):
        s1 = "aaaaaaaaaaaaaaaaaaaaaaaa\r\n"
        s2 = "bbbbbbbbbbbbbbbbbbbbbbbb\r\n"
        s3 = "stillokay:bbbbxx\r\n"
        s4 = "broken!!!!badbad\r\n"
        s5 = "againokay.\r\n"

        s = (s1+s2+s3+s4+s5).encode(self.encoding)
        stream = io.BytesIO(s)
        reader = codecs.getreader(self.encoding)(stream)
        self.assertEqual(reader.readline(), s1)
        self.assertEqual(reader.readline(), s2)
        self.assertEqual(reader.readline(), s3)
        self.assertEqual(reader.readline(), s4)
        self.assertEqual(reader.readline(), s5)
        self.assertEqual(reader.readline(), "")

    ill_formed_sequence_replace = "\ufffd"

    eleza test_lone_surrogates(self):
        self.assertRaises(UnicodeEncodeError, "\ud800".encode, self.encoding)
        self.assertEqual("[\uDC80]".encode(self.encoding, "backslashreplace"),
                         "[\\udc80]".encode(self.encoding))
        self.assertEqual("[\uDC80]".encode(self.encoding, "namereplace"),
                         "[\\udc80]".encode(self.encoding))
        self.assertEqual("[\uDC80]".encode(self.encoding, "xmlcharrefreplace"),
                         "[&#56448;]".encode(self.encoding))
        self.assertEqual("[\uDC80]".encode(self.encoding, "ignore"),
                         "[]".encode(self.encoding))
        self.assertEqual("[\uDC80]".encode(self.encoding, "replace"),
                         "[?]".encode(self.encoding))

        # sequential surrogate characters
        self.assertEqual("[\uD800\uDC80]".encode(self.encoding, "ignore"),
                         "[]".encode(self.encoding))
        self.assertEqual("[\uD800\uDC80]".encode(self.encoding, "replace"),
                         "[??]".encode(self.encoding))

        bom = "".encode(self.encoding)
        kila before, after kwenye [("\U00010fff", "A"), ("[", "]"),
                              ("A", "\U00010fff")]:
            before_sequence = before.encode(self.encoding)[len(bom):]
            after_sequence = after.encode(self.encoding)[len(bom):]
            test_string = before + "\uDC80" + after
            test_sequence = (bom + before_sequence +
                             self.ill_formed_sequence + after_sequence)
            self.assertRaises(UnicodeDecodeError, test_sequence.decode,
                              self.encoding)
            self.assertEqual(test_string.encode(self.encoding,
                                                "surrogatepita"),
                             test_sequence)
            self.assertEqual(test_sequence.decode(self.encoding,
                                                  "surrogatepita"),
                             test_string)
            self.assertEqual(test_sequence.decode(self.encoding, "ignore"),
                             before + after)
            self.assertEqual(test_sequence.decode(self.encoding, "replace"),
                             before + self.ill_formed_sequence_replace + after)
            backslashreplace = ''.join('\\x%02x' % b
                                       kila b kwenye self.ill_formed_sequence)
            self.assertEqual(test_sequence.decode(self.encoding, "backslashreplace"),
                             before + backslashreplace + after)

    eleza test_incremental_surrogatepita(self):
        # Test incremental decoder kila surrogatepita handler:
        # see issue #24214
        # High surrogate
        data = '\uD901'.encode(self.encoding, 'surrogatepita')
        kila i kwenye range(1, len(data)):
            dec = codecs.getincrementaldecoder(self.encoding)('surrogatepita')
            self.assertEqual(dec.decode(data[:i]), '')
            self.assertEqual(dec.decode(data[i:], Kweli), '\uD901')
        # Low surrogate
        data = '\uDC02'.encode(self.encoding, 'surrogatepita')
        kila i kwenye range(1, len(data)):
            dec = codecs.getincrementaldecoder(self.encoding)('surrogatepita')
            self.assertEqual(dec.decode(data[:i]), '')
            self.assertEqual(dec.decode(data[i:]), '\uDC02')


kundi UTF32Test(ReadTest, unittest.TestCase):
    encoding = "utf-32"
    ikiwa sys.byteorder == 'little':
        ill_formed_sequence = b"\x80\xdc\x00\x00"
    isipokua:
        ill_formed_sequence = b"\x00\x00\xdc\x80"

    spamle = (b'\xff\xfe\x00\x00'
              b's\x00\x00\x00p\x00\x00\x00a\x00\x00\x00m\x00\x00\x00'
              b's\x00\x00\x00p\x00\x00\x00a\x00\x00\x00m\x00\x00\x00')
    spambe = (b'\x00\x00\xfe\xff'
              b'\x00\x00\x00s\x00\x00\x00p\x00\x00\x00a\x00\x00\x00m'
              b'\x00\x00\x00s\x00\x00\x00p\x00\x00\x00a\x00\x00\x00m')

    eleza test_only_one_bom(self):
        _,_,reader,writer = codecs.lookup(self.encoding)
        # encode some stream
        s = io.BytesIO()
        f = writer(s)
        f.write("spam")
        f.write("spam")
        d = s.getvalue()
        # check whether there ni exactly one BOM kwenye it
        self.assertKweli(d == self.spamle ama d == self.spambe)
        # try to read it back
        s = io.BytesIO(d)
        f = reader(s)
        self.assertEqual(f.read(), "spamspam")

    eleza test_badbom(self):
        s = io.BytesIO(4*b"\xff")
        f = codecs.getreader(self.encoding)(s)
        self.assertRaises(UnicodeError, f.read)

        s = io.BytesIO(8*b"\xff")
        f = codecs.getreader(self.encoding)(s)
        self.assertRaises(UnicodeError, f.read)

    eleza test_partial(self):
        self.check_partial(
            "\x00\xff\u0100\uffff\U00010000",
            [
                "", # first byte of BOM read
                "", # second byte of BOM read
                "", # third byte of BOM read
                "", # fourth byte of BOM read => byteorder known
                "",
                "",
                "",
                "\x00",
                "\x00",
                "\x00",
                "\x00",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff\U00010000",
            ]
        )

    eleza test_handlers(self):
        self.assertEqual(('\ufffd', 1),
                         codecs.utf_32_decode(b'\x01', 'replace', Kweli))
        self.assertEqual(('', 1),
                         codecs.utf_32_decode(b'\x01', 'ignore', Kweli))

    eleza test_errors(self):
        self.assertRaises(UnicodeDecodeError, codecs.utf_32_decode,
                          b"\xff", "strict", Kweli)

    eleza test_decoder_state(self):
        self.check_state_handling_decode(self.encoding,
                                         "spamspam", self.spamle)
        self.check_state_handling_decode(self.encoding,
                                         "spamspam", self.spambe)

    eleza test_issue8941(self):
        # Issue #8941: insufficient result allocation when decoding into
        # surrogate pairs on UCS-2 builds.
        encoded_le = b'\xff\xfe\x00\x00' + b'\x00\x00\x01\x00' * 1024
        self.assertEqual('\U00010000' * 1024,
                         codecs.utf_32_decode(encoded_le)[0])
        encoded_be = b'\x00\x00\xfe\xff' + b'\x00\x01\x00\x00' * 1024
        self.assertEqual('\U00010000' * 1024,
                         codecs.utf_32_decode(encoded_be)[0])


kundi UTF32LETest(ReadTest, unittest.TestCase):
    encoding = "utf-32-le"
    ill_formed_sequence = b"\x80\xdc\x00\x00"

    eleza test_partial(self):
        self.check_partial(
            "\x00\xff\u0100\uffff\U00010000",
            [
                "",
                "",
                "",
                "\x00",
                "\x00",
                "\x00",
                "\x00",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff\U00010000",
            ]
        )

    eleza test_simple(self):
        self.assertEqual("\U00010203".encode(self.encoding), b"\x03\x02\x01\x00")

    eleza test_errors(self):
        self.assertRaises(UnicodeDecodeError, codecs.utf_32_le_decode,
                          b"\xff", "strict", Kweli)

    eleza test_issue8941(self):
        # Issue #8941: insufficient result allocation when decoding into
        # surrogate pairs on UCS-2 builds.
        encoded = b'\x00\x00\x01\x00' * 1024
        self.assertEqual('\U00010000' * 1024,
                         codecs.utf_32_le_decode(encoded)[0])


kundi UTF32BETest(ReadTest, unittest.TestCase):
    encoding = "utf-32-be"
    ill_formed_sequence = b"\x00\x00\xdc\x80"

    eleza test_partial(self):
        self.check_partial(
            "\x00\xff\u0100\uffff\U00010000",
            [
                "",
                "",
                "",
                "\x00",
                "\x00",
                "\x00",
                "\x00",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff\U00010000",
            ]
        )

    eleza test_simple(self):
        self.assertEqual("\U00010203".encode(self.encoding), b"\x00\x01\x02\x03")

    eleza test_errors(self):
        self.assertRaises(UnicodeDecodeError, codecs.utf_32_be_decode,
                          b"\xff", "strict", Kweli)

    eleza test_issue8941(self):
        # Issue #8941: insufficient result allocation when decoding into
        # surrogate pairs on UCS-2 builds.
        encoded = b'\x00\x01\x00\x00' * 1024
        self.assertEqual('\U00010000' * 1024,
                         codecs.utf_32_be_decode(encoded)[0])


kundi UTF16Test(ReadTest, unittest.TestCase):
    encoding = "utf-16"
    ikiwa sys.byteorder == 'little':
        ill_formed_sequence = b"\x80\xdc"
    isipokua:
        ill_formed_sequence = b"\xdc\x80"

    spamle = b'\xff\xfes\x00p\x00a\x00m\x00s\x00p\x00a\x00m\x00'
    spambe = b'\xfe\xff\x00s\x00p\x00a\x00m\x00s\x00p\x00a\x00m'

    eleza test_only_one_bom(self):
        _,_,reader,writer = codecs.lookup(self.encoding)
        # encode some stream
        s = io.BytesIO()
        f = writer(s)
        f.write("spam")
        f.write("spam")
        d = s.getvalue()
        # check whether there ni exactly one BOM kwenye it
        self.assertKweli(d == self.spamle ama d == self.spambe)
        # try to read it back
        s = io.BytesIO(d)
        f = reader(s)
        self.assertEqual(f.read(), "spamspam")

    eleza test_badbom(self):
        s = io.BytesIO(b"\xff\xff")
        f = codecs.getreader(self.encoding)(s)
        self.assertRaises(UnicodeError, f.read)

        s = io.BytesIO(b"\xff\xff\xff\xff")
        f = codecs.getreader(self.encoding)(s)
        self.assertRaises(UnicodeError, f.read)

    eleza test_partial(self):
        self.check_partial(
            "\x00\xff\u0100\uffff\U00010000",
            [
                "", # first byte of BOM read
                "", # second byte of BOM read => byteorder known
                "",
                "\x00",
                "\x00",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff\U00010000",
            ]
        )

    eleza test_handlers(self):
        self.assertEqual(('\ufffd', 1),
                         codecs.utf_16_decode(b'\x01', 'replace', Kweli))
        self.assertEqual(('', 1),
                         codecs.utf_16_decode(b'\x01', 'ignore', Kweli))

    eleza test_errors(self):
        self.assertRaises(UnicodeDecodeError, codecs.utf_16_decode,
                          b"\xff", "strict", Kweli)

    eleza test_decoder_state(self):
        self.check_state_handling_decode(self.encoding,
                                         "spamspam", self.spamle)
        self.check_state_handling_decode(self.encoding,
                                         "spamspam", self.spambe)

    eleza test_bug691291(self):
        # Files are always opened kwenye binary mode, even ikiwa no binary mode was
        # specified.  This means that no automatic conversion of '\n' ni done
        # on reading na writing.
        s1 = 'Hello\r\nworld\r\n'

        s = s1.encode(self.encoding)
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha open(support.TESTFN, 'wb') kama fp:
            fp.write(s)
        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            reader = codecs.open(support.TESTFN, 'U', encoding=self.encoding)
        ukijumuisha reader:
            self.assertEqual(reader.read(), s1)

kundi UTF16LETest(ReadTest, unittest.TestCase):
    encoding = "utf-16-le"
    ill_formed_sequence = b"\x80\xdc"

    eleza test_partial(self):
        self.check_partial(
            "\x00\xff\u0100\uffff\U00010000",
            [
                "",
                "\x00",
                "\x00",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff\U00010000",
            ]
        )

    eleza test_errors(self):
        tests = [
            (b'\xff', '\ufffd'),
            (b'A\x00Z', 'A\ufffd'),
            (b'A\x00B\x00C\x00D\x00Z', 'ABCD\ufffd'),
            (b'\x00\xd8', '\ufffd'),
            (b'\x00\xd8A', '\ufffd'),
            (b'\x00\xd8A\x00', '\ufffdA'),
            (b'\x00\xdcA\x00', '\ufffdA'),
        ]
        kila raw, expected kwenye tests:
            self.assertRaises(UnicodeDecodeError, codecs.utf_16_le_decode,
                              raw, 'strict', Kweli)
            self.assertEqual(raw.decode('utf-16le', 'replace'), expected)

    eleza test_nonbmp(self):
        self.assertEqual("\U00010203".encode(self.encoding),
                         b'\x00\xd8\x03\xde')
        self.assertEqual(b'\x00\xd8\x03\xde'.decode(self.encoding),
                         "\U00010203")

kundi UTF16BETest(ReadTest, unittest.TestCase):
    encoding = "utf-16-be"
    ill_formed_sequence = b"\xdc\x80"

    eleza test_partial(self):
        self.check_partial(
            "\x00\xff\u0100\uffff\U00010000",
            [
                "",
                "\x00",
                "\x00",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff\u0100",
                "\x00\xff\u0100",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff",
                "\x00\xff\u0100\uffff\U00010000",
            ]
        )

    eleza test_errors(self):
        tests = [
            (b'\xff', '\ufffd'),
            (b'\x00A\xff', 'A\ufffd'),
            (b'\x00A\x00B\x00C\x00DZ', 'ABCD\ufffd'),
            (b'\xd8\x00', '\ufffd'),
            (b'\xd8\x00\xdc', '\ufffd'),
            (b'\xd8\x00\x00A', '\ufffdA'),
            (b'\xdc\x00\x00A', '\ufffdA'),
        ]
        kila raw, expected kwenye tests:
            self.assertRaises(UnicodeDecodeError, codecs.utf_16_be_decode,
                              raw, 'strict', Kweli)
            self.assertEqual(raw.decode('utf-16be', 'replace'), expected)

    eleza test_nonbmp(self):
        self.assertEqual("\U00010203".encode(self.encoding),
                         b'\xd8\x00\xde\x03')
        self.assertEqual(b'\xd8\x00\xde\x03'.decode(self.encoding),
                         "\U00010203")

kundi UTF8Test(ReadTest, unittest.TestCase):
    encoding = "utf-8"
    ill_formed_sequence = b"\xed\xb2\x80"
    ill_formed_sequence_replace = "\ufffd" * 3
    BOM = b''

    eleza test_partial(self):
        self.check_partial(
            "\x00\xff\u07ff\u0800\uffff\U00010000",
            [
                "\x00",
                "\x00",
                "\x00\xff",
                "\x00\xff",
                "\x00\xff\u07ff",
                "\x00\xff\u07ff",
                "\x00\xff\u07ff",
                "\x00\xff\u07ff\u0800",
                "\x00\xff\u07ff\u0800",
                "\x00\xff\u07ff\u0800",
                "\x00\xff\u07ff\u0800\uffff",
                "\x00\xff\u07ff\u0800\uffff",
                "\x00\xff\u07ff\u0800\uffff",
                "\x00\xff\u07ff\u0800\uffff",
                "\x00\xff\u07ff\u0800\uffff\U00010000",
            ]
        )

    eleza test_decoder_state(self):
        u = "\x00\x7f\x80\xff\u0100\u07ff\u0800\uffff\U0010ffff"
        self.check_state_handling_decode(self.encoding,
                                         u, u.encode(self.encoding))

    eleza test_decode_error(self):
        kila data, error_handler, expected kwenye (
            (b'[\x80\xff]', 'ignore', '[]'),
            (b'[\x80\xff]', 'replace', '[\ufffd\ufffd]'),
            (b'[\x80\xff]', 'surrogateescape', '[\udc80\udcff]'),
            (b'[\x80\xff]', 'backslashreplace', '[\\x80\\xff]'),
        ):
            ukijumuisha self.subTest(data=data, error_handler=error_handler,
                              expected=expected):
                self.assertEqual(data.decode(self.encoding, error_handler),
                                 expected)

    eleza test_lone_surrogates(self):
        super().test_lone_surrogates()
        # sio sure ikiwa this ni making sense for
        # UTF-16 na UTF-32
        self.assertEqual("[\uDC80]".encode(self.encoding, "surrogateescape"),
                         self.BOM + b'[\x80]')

        ukijumuisha self.assertRaises(UnicodeEncodeError) kama cm:
            "[\uDC80\uD800\uDFFF]".encode(self.encoding, "surrogateescape")
        exc = cm.exception
        self.assertEqual(exc.object[exc.start:exc.end], '\uD800\uDFFF')

    eleza test_surrogatepita_handler(self):
        self.assertEqual("abc\ud800def".encode(self.encoding, "surrogatepita"),
                         self.BOM + b"abc\xed\xa0\x80def")
        self.assertEqual("\U00010fff\uD800".encode(self.encoding, "surrogatepita"),
                         self.BOM + b"\xf0\x90\xbf\xbf\xed\xa0\x80")
        self.assertEqual("[\uD800\uDC80]".encode(self.encoding, "surrogatepita"),
                         self.BOM + b'[\xed\xa0\x80\xed\xb2\x80]')

        self.assertEqual(b"abc\xed\xa0\x80def".decode(self.encoding, "surrogatepita"),
                         "abc\ud800def")
        self.assertEqual(b"\xf0\x90\xbf\xbf\xed\xa0\x80".decode(self.encoding, "surrogatepita"),
                         "\U00010fff\uD800")

        self.assertKweli(codecs.lookup_error("surrogatepita"))
        ukijumuisha self.assertRaises(UnicodeDecodeError):
            b"abc\xed\xa0".decode(self.encoding, "surrogatepita")
        ukijumuisha self.assertRaises(UnicodeDecodeError):
            b"abc\xed\xa0z".decode(self.encoding, "surrogatepita")

    eleza test_incremental_errors(self):
        # Test that the incremental decoder can fail ukijumuisha final=Uongo.
        # See issue #24214
        cases = [b'\x80', b'\xBF', b'\xC0', b'\xC1', b'\xF5', b'\xF6', b'\xFF']
        kila prefix kwenye (b'\xC2', b'\xDF', b'\xE0', b'\xE0\xA0', b'\xEF',
                       b'\xEF\xBF', b'\xF0', b'\xF0\x90', b'\xF0\x90\x80',
                       b'\xF4', b'\xF4\x8F', b'\xF4\x8F\xBF'):
            kila suffix kwenye b'\x7F', b'\xC0':
                cases.append(prefix + suffix)
        cases.extend((b'\xE0\x80', b'\xE0\x9F', b'\xED\xA0\x80',
                      b'\xED\xBF\xBF', b'\xF0\x80', b'\xF0\x8F', b'\xF4\x90'))

        kila data kwenye cases:
            ukijumuisha self.subTest(data=data):
                dec = codecs.getincrementaldecoder(self.encoding)()
                self.assertRaises(UnicodeDecodeError, dec.decode, data)


kundi UTF7Test(ReadTest, unittest.TestCase):
    encoding = "utf-7"

    eleza test_ascii(self):
        # Set D (directly encoded characters)
        set_d = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 'abcdefghijklmnopqrstuvwxyz'
                 '0123456789'
                 '\'(),-./:?')
        self.assertEqual(set_d.encode(self.encoding), set_d.encode('ascii'))
        self.assertEqual(set_d.encode('ascii').decode(self.encoding), set_d)
        # Set O (optional direct characters)
        set_o = ' !"#$%&*;<=>@[]^_`{|}'
        self.assertEqual(set_o.encode(self.encoding), set_o.encode('ascii'))
        self.assertEqual(set_o.encode('ascii').decode(self.encoding), set_o)
        # +
        self.assertEqual('a+b'.encode(self.encoding), b'a+-b')
        self.assertEqual(b'a+-b'.decode(self.encoding), 'a+b')
        # White spaces
        ws = ' \t\n\r'
        self.assertEqual(ws.encode(self.encoding), ws.encode('ascii'))
        self.assertEqual(ws.encode('ascii').decode(self.encoding), ws)
        # Other ASCII characters
        other_ascii = ''.join(sorted(set(bytes(range(0x80)).decode()) -
                                     set(set_d + set_o + '+' + ws)))
        self.assertEqual(other_ascii.encode(self.encoding),
                         b'+AAAAAQACAAMABAAFAAYABwAIAAsADAAOAA8AEAARABIAEwAU'
                         b'ABUAFgAXABgAGQAaABsAHAAdAB4AHwBcAH4Afw-')

    eleza test_partial(self):
        self.check_partial(
            'a+-b\x00c\x80d\u0100e\U00010000f',
            [
                'a',
                'a',
                'a+',
                'a+-',
                'a+-b',
                'a+-b',
                'a+-b',
                'a+-b',
                'a+-b',
                'a+-b\x00',
                'a+-b\x00c',
                'a+-b\x00c',
                'a+-b\x00c',
                'a+-b\x00c',
                'a+-b\x00c',
                'a+-b\x00c\x80',
                'a+-b\x00c\x80d',
                'a+-b\x00c\x80d',
                'a+-b\x00c\x80d',
                'a+-b\x00c\x80d',
                'a+-b\x00c\x80d',
                'a+-b\x00c\x80d\u0100',
                'a+-b\x00c\x80d\u0100e',
                'a+-b\x00c\x80d\u0100e',
                'a+-b\x00c\x80d\u0100e',
                'a+-b\x00c\x80d\u0100e',
                'a+-b\x00c\x80d\u0100e',
                'a+-b\x00c\x80d\u0100e',
                'a+-b\x00c\x80d\u0100e',
                'a+-b\x00c\x80d\u0100e',
                'a+-b\x00c\x80d\u0100e\U00010000',
                'a+-b\x00c\x80d\u0100e\U00010000f',
            ]
        )

    eleza test_errors(self):
        tests = [
            (b'\xffb', '\ufffdb'),
            (b'a\xffb', 'a\ufffdb'),
            (b'a\xff\xffb', 'a\ufffd\ufffdb'),
            (b'a+IK', 'a\ufffd'),
            (b'a+IK-b', 'a\ufffdb'),
            (b'a+IK,b', 'a\ufffdb'),
            (b'a+IKx', 'a\u20ac\ufffd'),
            (b'a+IKx-b', 'a\u20ac\ufffdb'),
            (b'a+IKwgr', 'a\u20ac\ufffd'),
            (b'a+IKwgr-b', 'a\u20ac\ufffdb'),
            (b'a+IKwgr,', 'a\u20ac\ufffd'),
            (b'a+IKwgr,-b', 'a\u20ac\ufffd-b'),
            (b'a+IKwgrB', 'a\u20ac\u20ac\ufffd'),
            (b'a+IKwgrB-b', 'a\u20ac\u20ac\ufffdb'),
            (b'a+/,+IKw-b', 'a\ufffd\u20acb'),
            (b'a+//,+IKw-b', 'a\ufffd\u20acb'),
            (b'a+///,+IKw-b', 'a\uffff\ufffd\u20acb'),
            (b'a+////,+IKw-b', 'a\uffff\ufffd\u20acb'),
            (b'a+IKw-b\xff', 'a\u20acb\ufffd'),
            (b'a+IKw\xffb', 'a\u20ac\ufffdb'),
            (b'a+@b', 'a\ufffdb'),
        ]
        kila raw, expected kwenye tests:
            ukijumuisha self.subTest(raw=raw):
                self.assertRaises(UnicodeDecodeError, codecs.utf_7_decode,
                                raw, 'strict', Kweli)
                self.assertEqual(raw.decode('utf-7', 'replace'), expected)

    eleza test_nonbmp(self):
        self.assertEqual('\U000104A0'.encode(self.encoding), b'+2AHcoA-')
        self.assertEqual('\ud801\udca0'.encode(self.encoding), b'+2AHcoA-')
        self.assertEqual(b'+2AHcoA-'.decode(self.encoding), '\U000104A0')
        self.assertEqual(b'+2AHcoA'.decode(self.encoding), '\U000104A0')
        self.assertEqual('\u20ac\U000104A0'.encode(self.encoding), b'+IKzYAdyg-')
        self.assertEqual(b'+IKzYAdyg-'.decode(self.encoding), '\u20ac\U000104A0')
        self.assertEqual(b'+IKzYAdyg'.decode(self.encoding), '\u20ac\U000104A0')
        self.assertEqual('\u20ac\u20ac\U000104A0'.encode(self.encoding),
                         b'+IKwgrNgB3KA-')
        self.assertEqual(b'+IKwgrNgB3KA-'.decode(self.encoding),
                         '\u20ac\u20ac\U000104A0')
        self.assertEqual(b'+IKwgrNgB3KA'.decode(self.encoding),
                         '\u20ac\u20ac\U000104A0')

    eleza test_lone_surrogates(self):
        tests = [
            (b'a+2AE-b', 'a\ud801b'),
            (b'a+2AE\xffb', 'a\ufffdb'),
            (b'a+2AE', 'a\ufffd'),
            (b'a+2AEA-b', 'a\ufffdb'),
            (b'a+2AH-b', 'a\ufffdb'),
            (b'a+IKzYAQ-b', 'a\u20ac\ud801b'),
            (b'a+IKzYAQ\xffb', 'a\u20ac\ufffdb'),
            (b'a+IKzYAQA-b', 'a\u20ac\ufffdb'),
            (b'a+IKzYAd-b', 'a\u20ac\ufffdb'),
            (b'a+IKwgrNgB-b', 'a\u20ac\u20ac\ud801b'),
            (b'a+IKwgrNgB\xffb', 'a\u20ac\u20ac\ufffdb'),
            (b'a+IKwgrNgB', 'a\u20ac\u20ac\ufffd'),
            (b'a+IKwgrNgBA-b', 'a\u20ac\u20ac\ufffdb'),
        ]
        kila raw, expected kwenye tests:
            ukijumuisha self.subTest(raw=raw):
                self.assertEqual(raw.decode('utf-7', 'replace'), expected)


kundi UTF16ExTest(unittest.TestCase):

    eleza test_errors(self):
        self.assertRaises(UnicodeDecodeError, codecs.utf_16_ex_decode, b"\xff", "strict", 0, Kweli)

    eleza test_bad_args(self):
        self.assertRaises(TypeError, codecs.utf_16_ex_decode)

kundi ReadBufferTest(unittest.TestCase):

    eleza test_array(self):
        agiza array
        self.assertEqual(
            codecs.readbuffer_encode(array.array("b", b"spam")),
            (b"spam", 4)
        )

    eleza test_empty(self):
        self.assertEqual(codecs.readbuffer_encode(""), (b"", 0))

    eleza test_bad_args(self):
        self.assertRaises(TypeError, codecs.readbuffer_encode)
        self.assertRaises(TypeError, codecs.readbuffer_encode, 42)

kundi UTF8SigTest(UTF8Test, unittest.TestCase):
    encoding = "utf-8-sig"
    BOM = codecs.BOM_UTF8

    eleza test_partial(self):
        self.check_partial(
            "\ufeff\x00\xff\u07ff\u0800\uffff\U00010000",
            [
                "",
                "",
                "", # First BOM has been read na skipped
                "",
                "",
                "\ufeff", # Second BOM has been read na emitted
                "\ufeff\x00", # "\x00" read na emitted
                "\ufeff\x00", # First byte of encoded "\xff" read
                "\ufeff\x00\xff", # Second byte of encoded "\xff" read
                "\ufeff\x00\xff", # First byte of encoded "\u07ff" read
                "\ufeff\x00\xff\u07ff", # Second byte of encoded "\u07ff" read
                "\ufeff\x00\xff\u07ff",
                "\ufeff\x00\xff\u07ff",
                "\ufeff\x00\xff\u07ff\u0800",
                "\ufeff\x00\xff\u07ff\u0800",
                "\ufeff\x00\xff\u07ff\u0800",
                "\ufeff\x00\xff\u07ff\u0800\uffff",
                "\ufeff\x00\xff\u07ff\u0800\uffff",
                "\ufeff\x00\xff\u07ff\u0800\uffff",
                "\ufeff\x00\xff\u07ff\u0800\uffff",
                "\ufeff\x00\xff\u07ff\u0800\uffff\U00010000",
            ]
        )

    eleza test_bug1601501(self):
        # SF bug #1601501: check that the codec works ukijumuisha a buffer
        self.assertEqual(str(b"\xef\xbb\xbf", "utf-8-sig"), "")

    eleza test_bom(self):
        d = codecs.getincrementaldecoder("utf-8-sig")()
        s = "spam"
        self.assertEqual(d.decode(s.encode("utf-8-sig")), s)

    eleza test_stream_bom(self):
        unistring = "ABC\u00A1\u2200XYZ"
        bytestring = codecs.BOM_UTF8 + b"ABC\xC2\xA1\xE2\x88\x80XYZ"

        reader = codecs.getreader("utf-8-sig")
        kila sizehint kwenye [Tupu] + list(range(1, 11)) + \
                        [64, 128, 256, 512, 1024]:
            istream = reader(io.BytesIO(bytestring))
            ostream = io.StringIO()
            wakati 1:
                ikiwa sizehint ni sio Tupu:
                    data = istream.read(sizehint)
                isipokua:
                    data = istream.read()

                ikiwa sio data:
                    koma
                ostream.write(data)

            got = ostream.getvalue()
            self.assertEqual(got, unistring)

    eleza test_stream_bare(self):
        unistring = "ABC\u00A1\u2200XYZ"
        bytestring = b"ABC\xC2\xA1\xE2\x88\x80XYZ"

        reader = codecs.getreader("utf-8-sig")
        kila sizehint kwenye [Tupu] + list(range(1, 11)) + \
                        [64, 128, 256, 512, 1024]:
            istream = reader(io.BytesIO(bytestring))
            ostream = io.StringIO()
            wakati 1:
                ikiwa sizehint ni sio Tupu:
                    data = istream.read(sizehint)
                isipokua:
                    data = istream.read()

                ikiwa sio data:
                    koma
                ostream.write(data)

            got = ostream.getvalue()
            self.assertEqual(got, unistring)

kundi EscapeDecodeTest(unittest.TestCase):
    eleza test_empty(self):
        self.assertEqual(codecs.escape_decode(b""), (b"", 0))
        self.assertEqual(codecs.escape_decode(bytearray()), (b"", 0))

    eleza test_raw(self):
        decode = codecs.escape_decode
        kila b kwenye range(256):
            b = bytes([b])
            ikiwa b != b'\\':
                self.assertEqual(decode(b + b'0'), (b + b'0', 2))

    eleza test_escape(self):
        decode = codecs.escape_decode
        check = coding_checker(self, decode)
        check(b"[\\\n]", b"[]")
        check(br'[\"]', b'["]')
        check(br"[\']", b"[']")
        check(br"[\\]", b"[\\]")
        check(br"[\a]", b"[\x07]")
        check(br"[\b]", b"[\x08]")
        check(br"[\t]", b"[\x09]")
        check(br"[\n]", b"[\x0a]")
        check(br"[\v]", b"[\x0b]")
        check(br"[\f]", b"[\x0c]")
        check(br"[\r]", b"[\x0d]")
        check(br"[\7]", b"[\x07]")
        check(br"[\78]", b"[\x078]")
        check(br"[\41]", b"[!]")
        check(br"[\418]", b"[!8]")
        check(br"[\101]", b"[A]")
        check(br"[\1010]", b"[A0]")
        check(br"[\501]", b"[A]")
        check(br"[\x41]", b"[A]")
        check(br"[\x410]", b"[A0]")
        kila i kwenye range(97, 123):
            b = bytes([i])
            ikiwa b haiko kwenye b'abfnrtvx':
                ukijumuisha self.assertWarns(DeprecationWarning):
                    check(b"\\" + b, b"\\" + b)
            ukijumuisha self.assertWarns(DeprecationWarning):
                check(b"\\" + b.upper(), b"\\" + b.upper())
        ukijumuisha self.assertWarns(DeprecationWarning):
            check(br"\8", b"\\8")
        ukijumuisha self.assertWarns(DeprecationWarning):
            check(br"\9", b"\\9")
        ukijumuisha self.assertWarns(DeprecationWarning):
            check(b"\\\xfa", b"\\\xfa")

    eleza test_errors(self):
        decode = codecs.escape_decode
        self.assertRaises(ValueError, decode, br"\x")
        self.assertRaises(ValueError, decode, br"[\x]")
        self.assertEqual(decode(br"[\x]\x", "ignore"), (b"[]", 6))
        self.assertEqual(decode(br"[\x]\x", "replace"), (b"[?]?", 6))
        self.assertRaises(ValueError, decode, br"\x0")
        self.assertRaises(ValueError, decode, br"[\x0]")
        self.assertEqual(decode(br"[\x0]\x0", "ignore"), (b"[]", 8))
        self.assertEqual(decode(br"[\x0]\x0", "replace"), (b"[?]?", 8))


# From RFC 3492
punycode_testcases = [
    # A Arabic (Egyptian):
    ("\u0644\u064A\u0647\u0645\u0627\u0628\u062A\u0643\u0644"
     "\u0645\u0648\u0634\u0639\u0631\u0628\u064A\u061F",
     b"egbpdaj6bu4bxfgehfvwxn"),
    # B Chinese (simplified):
    ("\u4ED6\u4EEC\u4E3A\u4EC0\u4E48\u4E0D\u8BF4\u4E2D\u6587",
     b"ihqwcrb4cv8a8dqg056pqjye"),
    # C Chinese (traditional):
    ("\u4ED6\u5011\u7232\u4EC0\u9EBD\u4E0D\u8AAA\u4E2D\u6587",
     b"ihqwctvzc91f659drss3x8bo0yb"),
    # D Czech: Pro<ccaron>prost<ecaron>nemluv<iacute><ccaron>esky
    ("\u0050\u0072\u006F\u010D\u0070\u0072\u006F\u0073\u0074"
     "\u011B\u006E\u0065\u006D\u006C\u0075\u0076\u00ED\u010D"
     "\u0065\u0073\u006B\u0079",
     b"Proprostnemluvesky-uyb24dma41a"),
    # E Hebrew:
    ("\u05DC\u05DE\u05D4\u05D4\u05DD\u05E4\u05E9\u05D5\u05D8"
     "\u05DC\u05D0\u05DE\u05D3\u05D1\u05E8\u05D9\u05DD\u05E2"
     "\u05D1\u05E8\u05D9\u05EA",
     b"4dbcagdahymbxekheh6e0a7fei0b"),
    # F Hindi (Devanagari):
    ("\u092F\u0939\u0932\u094B\u0917\u0939\u093F\u0928\u094D"
     "\u0926\u0940\u0915\u094D\u092F\u094B\u0902\u0928\u0939"
     "\u0940\u0902\u092C\u094B\u0932\u0938\u0915\u0924\u0947"
     "\u0939\u0948\u0902",
     b"i1baa7eci9glrd9b2ae1bj0hfcgg6iyaf8o0a1dig0cd"),

    #(G) Japanese (kanji na hiragana):
    ("\u306A\u305C\u307F\u3093\u306A\u65E5\u672C\u8A9E\u3092"
     "\u8A71\u3057\u3066\u304F\u308C\u306A\u3044\u306E\u304B",
     b"n8jok5ay5dzabd5bym9f0cm5685rrjetr6pdxa"),

    # (H) Korean (Hangul syllables):
    ("\uC138\uACC4\uC758\uBAA8\uB4E0\uC0AC\uB78C\uB4E4\uC774"
     "\uD55C\uAD6D\uC5B4\uB97C\uC774\uD574\uD55C\uB2E4\uBA74"
     "\uC5BC\uB9C8\uB098\uC88B\uC744\uAE4C",
     b"989aomsvi5e83db1d2a355cv1e0vak1dwrv93d5xbh15a0dt30a5j"
     b"psd879ccm6fea98c"),

    # (I) Russian (Cyrillic):
    ("\u043F\u043E\u0447\u0435\u043C\u0443\u0436\u0435\u043E"
     "\u043D\u0438\u043D\u0435\u0433\u043E\u0432\u043E\u0440"
     "\u044F\u0442\u043F\u043E\u0440\u0443\u0441\u0441\u043A"
     "\u0438",
     b"b1abfaaepdrnnbgefbaDotcwatmq2g4l"),

    # (J) Spanish: Porqu<eacute>nopuedensimplementehablarenEspa<ntilde>ol
    ("\u0050\u006F\u0072\u0071\u0075\u00E9\u006E\u006F\u0070"
     "\u0075\u0065\u0064\u0065\u006E\u0073\u0069\u006D\u0070"
     "\u006C\u0065\u006D\u0065\u006E\u0074\u0065\u0068\u0061"
     "\u0062\u006C\u0061\u0072\u0065\u006E\u0045\u0073\u0070"
     "\u0061\u00F1\u006F\u006C",
     b"PorqunopuedensimplementehablarenEspaol-fmd56a"),

    # (K) Vietnamese:
    #  T<adotbelow>isaoh<odotbelow>kh<ocirc>ngth<ecirchookabove>ch\
    #   <ihookabove>n<oacute>iti<ecircacute>ngVi<ecircdotbelow>t
    ("\u0054\u1EA1\u0069\u0073\u0061\u006F\u0068\u1ECD\u006B"
     "\u0068\u00F4\u006E\u0067\u0074\u0068\u1EC3\u0063\u0068"
     "\u1EC9\u006E\u00F3\u0069\u0074\u0069\u1EBF\u006E\u0067"
     "\u0056\u0069\u1EC7\u0074",
     b"TisaohkhngthchnitingVit-kjcr8268qyxafd2f1b9g"),

    #(L) 3<nen>B<gumi><kinpachi><sensei>
    ("\u0033\u5E74\u0042\u7D44\u91D1\u516B\u5148\u751F",
     b"3B-ww4c5e180e575a65lsy2b"),

    # (M) <amuro><namie>-with-SUPER-MONKEYS
    ("\u5B89\u5BA4\u5948\u7F8E\u6075\u002D\u0077\u0069\u0074"
     "\u0068\u002D\u0053\u0055\u0050\u0045\u0052\u002D\u004D"
     "\u004F\u004E\u004B\u0045\u0059\u0053",
     b"-with-SUPER-MONKEYS-pc58ag80a8qai00g7n9n"),

    # (N) Hello-Another-Way-<sorezore><no><basho>
    ("\u0048\u0065\u006C\u006C\u006F\u002D\u0041\u006E\u006F"
     "\u0074\u0068\u0065\u0072\u002D\u0057\u0061\u0079\u002D"
     "\u305D\u308C\u305E\u308C\u306E\u5834\u6240",
     b"Hello-Another-Way--fc4qua05auwb3674vfr0b"),

    # (O) <hitotsu><yane><no><shita>2
    ("\u3072\u3068\u3064\u5C4B\u6839\u306E\u4E0B\u0032",
     b"2-u9tlzr9756bt3uc0v"),

    # (P) Maji<de>Koi<suru>5<byou><mae>
    ("\u004D\u0061\u006A\u0069\u3067\u004B\u006F\u0069\u3059"
     "\u308B\u0035\u79D2\u524D",
     b"MajiKoi5-783gue6qz075azm5e"),

     # (Q) <pafii>de<runba>
    ("\u30D1\u30D5\u30A3\u30FC\u0064\u0065\u30EB\u30F3\u30D0",
     b"de-jg4avhby1noc0d"),

    # (R) <sono><supiido><de>
    ("\u305D\u306E\u30B9\u30D4\u30FC\u30C9\u3067",
     b"d9juau41awczczp"),

    # (S) -> $1.00 <-
    ("\u002D\u003E\u0020\u0024\u0031\u002E\u0030\u0030\u0020"
     "\u003C\u002D",
     b"-> $1.00 <--")
    ]

kila i kwenye punycode_testcases:
    ikiwa len(i)!=2:
        andika(repr(i))


kundi PunycodeTest(unittest.TestCase):
    eleza test_encode(self):
        kila uni, puny kwenye punycode_testcases:
            # Need to convert both strings to lower case, since
            # some of the extended encodings use upper case, but our
            # code produces only lower case. Converting just puny to
            # lower ni also insufficient, since some of the input characters
            # are upper case.
            self.assertEqual(
                str(uni.encode("punycode"), "ascii").lower(),
                str(puny, "ascii").lower()
            )

    eleza test_decode(self):
        kila uni, puny kwenye punycode_testcases:
            self.assertEqual(uni, puny.decode("punycode"))
            puny = puny.decode("ascii").encode("ascii")
            self.assertEqual(uni, puny.decode("punycode"))


# From http://www.gnu.org/software/libidn/draft-josefsson-idn-test-vectors.html
nameprep_tests = [
    # 3.1 Map to nothing.
    (b'foo\xc2\xad\xcd\x8f\xe1\xa0\x86\xe1\xa0\x8bbar'
     b'\xe2\x80\x8b\xe2\x81\xa0baz\xef\xb8\x80\xef\xb8\x88\xef'
     b'\xb8\x8f\xef\xbb\xbf',
     b'foobarbaz'),
    # 3.2 Case folding ASCII U+0043 U+0041 U+0046 U+0045.
    (b'CAFE',
     b'cafe'),
    # 3.3 Case folding 8bit U+00DF (german sharp s).
    # The original test case ni bogus; it says \xc3\xdf
    (b'\xc3\x9f',
     b'ss'),
    # 3.4 Case folding U+0130 (turkish capital I ukijumuisha dot).
    (b'\xc4\xb0',
     b'i\xcc\x87'),
    # 3.5 Case folding multibyte U+0143 U+037A.
    (b'\xc5\x83\xcd\xba',
     b'\xc5\x84 \xce\xb9'),
    # 3.6 Case folding U+2121 U+33C6 U+1D7BB.
    # XXX: skip this kama it fails kwenye UCS-2 mode
    #('\xe2\x84\xa1\xe3\x8f\x86\xf0\x9d\x9e\xbb',
    # 'telc\xe2\x88\x95kg\xcf\x83'),
    (Tupu, Tupu),
    # 3.7 Normalization of U+006a U+030c U+00A0 U+00AA.
    (b'j\xcc\x8c\xc2\xa0\xc2\xaa',
     b'\xc7\xb0 a'),
    # 3.8 Case folding U+1FB7 na normalization.
    (b'\xe1\xbe\xb7',
     b'\xe1\xbe\xb6\xce\xb9'),
    # 3.9 Self-reverting case folding U+01F0 na normalization.
    # The original test case ni bogus, it says `\xc7\xf0'
    (b'\xc7\xb0',
     b'\xc7\xb0'),
    # 3.10 Self-reverting case folding U+0390 na normalization.
    (b'\xce\x90',
     b'\xce\x90'),
    # 3.11 Self-reverting case folding U+03B0 na normalization.
    (b'\xce\xb0',
     b'\xce\xb0'),
    # 3.12 Self-reverting case folding U+1E96 na normalization.
    (b'\xe1\xba\x96',
     b'\xe1\xba\x96'),
    # 3.13 Self-reverting case folding U+1F56 na normalization.
    (b'\xe1\xbd\x96',
     b'\xe1\xbd\x96'),
    # 3.14 ASCII space character U+0020.
    (b' ',
     b' '),
    # 3.15 Non-ASCII 8bit space character U+00A0.
    (b'\xc2\xa0',
     b' '),
    # 3.16 Non-ASCII multibyte space character U+1680.
    (b'\xe1\x9a\x80',
     Tupu),
    # 3.17 Non-ASCII multibyte space character U+2000.
    (b'\xe2\x80\x80',
     b' '),
    # 3.18 Zero Width Space U+200b.
    (b'\xe2\x80\x8b',
     b''),
    # 3.19 Non-ASCII multibyte space character U+3000.
    (b'\xe3\x80\x80',
     b' '),
    # 3.20 ASCII control characters U+0010 U+007F.
    (b'\x10\x7f',
     b'\x10\x7f'),
    # 3.21 Non-ASCII 8bit control character U+0085.
    (b'\xc2\x85',
     Tupu),
    # 3.22 Non-ASCII multibyte control character U+180E.
    (b'\xe1\xa0\x8e',
     Tupu),
    # 3.23 Zero Width No-Break Space U+FEFF.
    (b'\xef\xbb\xbf',
     b''),
    # 3.24 Non-ASCII control character U+1D175.
    (b'\xf0\x9d\x85\xb5',
     Tupu),
    # 3.25 Plane 0 private use character U+F123.
    (b'\xef\x84\xa3',
     Tupu),
    # 3.26 Plane 15 private use character U+F1234.
    (b'\xf3\xb1\x88\xb4',
     Tupu),
    # 3.27 Plane 16 private use character U+10F234.
    (b'\xf4\x8f\x88\xb4',
     Tupu),
    # 3.28 Non-character code point U+8FFFE.
    (b'\xf2\x8f\xbf\xbe',
     Tupu),
    # 3.29 Non-character code point U+10FFFF.
    (b'\xf4\x8f\xbf\xbf',
     Tupu),
    # 3.30 Surrogate code U+DF42.
    (b'\xed\xbd\x82',
     Tupu),
    # 3.31 Non-plain text character U+FFFD.
    (b'\xef\xbf\xbd',
     Tupu),
    # 3.32 Ideographic description character U+2FF5.
    (b'\xe2\xbf\xb5',
     Tupu),
    # 3.33 Display property character U+0341.
    (b'\xcd\x81',
     b'\xcc\x81'),
    # 3.34 Left-to-right mark U+200E.
    (b'\xe2\x80\x8e',
     Tupu),
    # 3.35 Deprecated U+202A.
    (b'\xe2\x80\xaa',
     Tupu),
    # 3.36 Language tagging character U+E0001.
    (b'\xf3\xa0\x80\x81',
     Tupu),
    # 3.37 Language tagging character U+E0042.
    (b'\xf3\xa0\x81\x82',
     Tupu),
    # 3.38 Bidi: RandALCat character U+05BE na LCat characters.
    (b'foo\xd6\xbebar',
     Tupu),
    # 3.39 Bidi: RandALCat character U+FD50 na LCat characters.
    (b'foo\xef\xb5\x90bar',
     Tupu),
    # 3.40 Bidi: RandALCat character U+FB38 na LCat characters.
    (b'foo\xef\xb9\xb6bar',
     b'foo \xd9\x8ebar'),
    # 3.41 Bidi: RandALCat without trailing RandALCat U+0627 U+0031.
    (b'\xd8\xa71',
     Tupu),
    # 3.42 Bidi: RandALCat character U+0627 U+0031 U+0628.
    (b'\xd8\xa71\xd8\xa8',
     b'\xd8\xa71\xd8\xa8'),
    # 3.43 Unassigned code point U+E0002.
    # Skip this test kama we allow unassigned
    #(b'\xf3\xa0\x80\x82',
    # Tupu),
    (Tupu, Tupu),
    # 3.44 Larger test (shrinking).
    # Original test case reads \xc3\xdf
    (b'X\xc2\xad\xc3\x9f\xc4\xb0\xe2\x84\xa1j\xcc\x8c\xc2\xa0\xc2'
     b'\xaa\xce\xb0\xe2\x80\x80',
     b'xssi\xcc\x87tel\xc7\xb0 a\xce\xb0 '),
    # 3.45 Larger test (expanding).
    # Original test case reads \xc3\x9f
    (b'X\xc3\x9f\xe3\x8c\x96\xc4\xb0\xe2\x84\xa1\xe2\x92\x9f\xe3\x8c'
     b'\x80',
     b'xss\xe3\x82\xad\xe3\x83\xad\xe3\x83\xa1\xe3\x83\xbc\xe3'
     b'\x83\x88\xe3\x83\xabi\xcc\x87tel\x28d\x29\xe3\x82'
     b'\xa2\xe3\x83\x91\xe3\x83\xbc\xe3\x83\x88')
    ]


kundi NameprepTest(unittest.TestCase):
    eleza test_nameprep(self):
        kutoka encodings.idna agiza nameprep
        kila pos, (orig, prepped) kwenye enumerate(nameprep_tests):
            ikiwa orig ni Tupu:
                # Skipped
                endelea
            # The Unicode strings are given kwenye UTF-8
            orig = str(orig, "utf-8", "surrogatepita")
            ikiwa prepped ni Tupu:
                # Input contains prohibited characters
                self.assertRaises(UnicodeError, nameprep, orig)
            isipokua:
                prepped = str(prepped, "utf-8", "surrogatepita")
                jaribu:
                    self.assertEqual(nameprep(orig), prepped)
                tatizo Exception kama e:
                    ashiria support.TestFailed("Test 3.%d: %s" % (pos+1, str(e)))


kundi IDNACodecTest(unittest.TestCase):
    eleza test_builtin_decode(self):
        self.assertEqual(str(b"python.org", "idna"), "python.org")
        self.assertEqual(str(b"python.org.", "idna"), "python.org.")
        self.assertEqual(str(b"xn--pythn-mua.org", "idna"), "pyth\xf6n.org")
        self.assertEqual(str(b"xn--pythn-mua.org.", "idna"), "pyth\xf6n.org.")

    eleza test_builtin_encode(self):
        self.assertEqual("python.org".encode("idna"), b"python.org")
        self.assertEqual("python.org.".encode("idna"), b"python.org.")
        self.assertEqual("pyth\xf6n.org".encode("idna"), b"xn--pythn-mua.org")
        self.assertEqual("pyth\xf6n.org.".encode("idna"), b"xn--pythn-mua.org.")

    eleza test_stream(self):
        r = codecs.getreader("idna")(io.BytesIO(b"abc"))
        r.read(3)
        self.assertEqual(r.read(), "")

    eleza test_incremental_decode(self):
        self.assertEqual(
            "".join(codecs.iterdecode((bytes([c]) kila c kwenye b"python.org"), "idna")),
            "python.org"
        )
        self.assertEqual(
            "".join(codecs.iterdecode((bytes([c]) kila c kwenye b"python.org."), "idna")),
            "python.org."
        )
        self.assertEqual(
            "".join(codecs.iterdecode((bytes([c]) kila c kwenye b"xn--pythn-mua.org."), "idna")),
            "pyth\xf6n.org."
        )
        self.assertEqual(
            "".join(codecs.iterdecode((bytes([c]) kila c kwenye b"xn--pythn-mua.org."), "idna")),
            "pyth\xf6n.org."
        )

        decoder = codecs.getincrementaldecoder("idna")()
        self.assertEqual(decoder.decode(b"xn--xam", ), "")
        self.assertEqual(decoder.decode(b"ple-9ta.o", ), "\xe4xample.")
        self.assertEqual(decoder.decode(b"rg"), "")
        self.assertEqual(decoder.decode(b"", Kweli), "org")

        decoder.reset()
        self.assertEqual(decoder.decode(b"xn--xam", ), "")
        self.assertEqual(decoder.decode(b"ple-9ta.o", ), "\xe4xample.")
        self.assertEqual(decoder.decode(b"rg."), "org.")
        self.assertEqual(decoder.decode(b"", Kweli), "")

    eleza test_incremental_encode(self):
        self.assertEqual(
            b"".join(codecs.iterencode("python.org", "idna")),
            b"python.org"
        )
        self.assertEqual(
            b"".join(codecs.iterencode("python.org.", "idna")),
            b"python.org."
        )
        self.assertEqual(
            b"".join(codecs.iterencode("pyth\xf6n.org.", "idna")),
            b"xn--pythn-mua.org."
        )
        self.assertEqual(
            b"".join(codecs.iterencode("pyth\xf6n.org.", "idna")),
            b"xn--pythn-mua.org."
        )

        encoder = codecs.getincrementalencoder("idna")()
        self.assertEqual(encoder.encode("\xe4x"), b"")
        self.assertEqual(encoder.encode("ample.org"), b"xn--xample-9ta.")
        self.assertEqual(encoder.encode("", Kweli), b"org")

        encoder.reset()
        self.assertEqual(encoder.encode("\xe4x"), b"")
        self.assertEqual(encoder.encode("ample.org."), b"xn--xample-9ta.org.")
        self.assertEqual(encoder.encode("", Kweli), b"")

    eleza test_errors(self):
        """Only supports "strict" error handler"""
        "python.org".encode("idna", "strict")
        b"python.org".decode("idna", "strict")
        kila errors kwenye ("ignore", "replace", "backslashreplace",
                "surrogateescape"):
            self.assertRaises(Exception, "python.org".encode, "idna", errors)
            self.assertRaises(Exception,
                b"python.org".decode, "idna", errors)


kundi CodecsModuleTest(unittest.TestCase):

    eleza test_decode(self):
        self.assertEqual(codecs.decode(b'\xe4\xf6\xfc', 'latin-1'),
                         '\xe4\xf6\xfc')
        self.assertRaises(TypeError, codecs.decode)
        self.assertEqual(codecs.decode(b'abc'), 'abc')
        self.assertRaises(UnicodeDecodeError, codecs.decode, b'\xff', 'ascii')

        # test keywords
        self.assertEqual(codecs.decode(obj=b'\xe4\xf6\xfc', encoding='latin-1'),
                         '\xe4\xf6\xfc')
        self.assertEqual(codecs.decode(b'[\xff]', 'ascii', errors='ignore'),
                         '[]')

    eleza test_encode(self):
        self.assertEqual(codecs.encode('\xe4\xf6\xfc', 'latin-1'),
                         b'\xe4\xf6\xfc')
        self.assertRaises(TypeError, codecs.encode)
        self.assertRaises(LookupError, codecs.encode, "foo", "__spam__")
        self.assertEqual(codecs.encode('abc'), b'abc')
        self.assertRaises(UnicodeEncodeError, codecs.encode, '\xffff', 'ascii')

        # test keywords
        self.assertEqual(codecs.encode(obj='\xe4\xf6\xfc', encoding='latin-1'),
                         b'\xe4\xf6\xfc')
        self.assertEqual(codecs.encode('[\xff]', 'ascii', errors='ignore'),
                         b'[]')

    eleza test_register(self):
        self.assertRaises(TypeError, codecs.register)
        self.assertRaises(TypeError, codecs.register, 42)

    eleza test_lookup(self):
        self.assertRaises(TypeError, codecs.lookup)
        self.assertRaises(LookupError, codecs.lookup, "__spam__")
        self.assertRaises(LookupError, codecs.lookup, " ")

    eleza test_getencoder(self):
        self.assertRaises(TypeError, codecs.getencoder)
        self.assertRaises(LookupError, codecs.getencoder, "__spam__")

    eleza test_getdecoder(self):
        self.assertRaises(TypeError, codecs.getdecoder)
        self.assertRaises(LookupError, codecs.getdecoder, "__spam__")

    eleza test_getreader(self):
        self.assertRaises(TypeError, codecs.getreader)
        self.assertRaises(LookupError, codecs.getreader, "__spam__")

    eleza test_getwriter(self):
        self.assertRaises(TypeError, codecs.getwriter)
        self.assertRaises(LookupError, codecs.getwriter, "__spam__")

    eleza test_lookup_issue1813(self):
        # Issue #1813: under Turkish locales, lookup of some codecs failed
        # because 'I' ni lowercased kama "ı" (dotless i)
        oldlocale = locale.setlocale(locale.LC_CTYPE)
        self.addCleanup(locale.setlocale, locale.LC_CTYPE, oldlocale)
        jaribu:
            locale.setlocale(locale.LC_CTYPE, 'tr_TR')
        tatizo locale.Error:
            # Unsupported locale on this system
            self.skipTest('test needs Turkish locale')
        c = codecs.lookup('ASCII')
        self.assertEqual(c.name, 'ascii')

    eleza test_all(self):
        api = (
            "encode", "decode",
            "register", "CodecInfo", "Codec", "IncrementalEncoder",
            "IncrementalDecoder", "StreamReader", "StreamWriter", "lookup",
            "getencoder", "getdecoder", "getincrementalencoder",
            "getincrementaldecoder", "getreader", "getwriter",
            "register_error", "lookup_error",
            "strict_errors", "replace_errors", "ignore_errors",
            "xmlcharrefreplace_errors", "backslashreplace_errors",
            "namereplace_errors",
            "open", "EncodedFile",
            "iterencode", "iterdecode",
            "BOM", "BOM_BE", "BOM_LE",
            "BOM_UTF8", "BOM_UTF16", "BOM_UTF16_BE", "BOM_UTF16_LE",
            "BOM_UTF32", "BOM_UTF32_BE", "BOM_UTF32_LE",
            "BOM32_BE", "BOM32_LE", "BOM64_BE", "BOM64_LE",  # Undocumented
            "StreamReaderWriter", "StreamRecoder",
        )
        self.assertCountEqual(api, codecs.__all__)
        kila api kwenye codecs.__all__:
            getattr(codecs, api)

    eleza test_open(self):
        self.addCleanup(support.unlink, support.TESTFN)
        kila mode kwenye ('w', 'r', 'r+', 'w+', 'a', 'a+'):
            ukijumuisha self.subTest(mode), \
                    codecs.open(support.TESTFN, mode, 'ascii') kama file:
                self.assertIsInstance(file, codecs.StreamReaderWriter)

    eleza test_undefined(self):
        self.assertRaises(UnicodeError, codecs.encode, 'abc', 'undefined')
        self.assertRaises(UnicodeError, codecs.decode, b'abc', 'undefined')
        self.assertRaises(UnicodeError, codecs.encode, '', 'undefined')
        self.assertRaises(UnicodeError, codecs.decode, b'', 'undefined')
        kila errors kwenye ('strict', 'ignore', 'replace', 'backslashreplace'):
            self.assertRaises(UnicodeError,
                codecs.encode, 'abc', 'undefined', errors)
            self.assertRaises(UnicodeError,
                codecs.decode, b'abc', 'undefined', errors)


kundi StreamReaderTest(unittest.TestCase):

    eleza setUp(self):
        self.reader = codecs.getreader('utf-8')
        self.stream = io.BytesIO(b'\xed\x95\x9c\n\xea\xb8\x80')

    eleza test_readlines(self):
        f = self.reader(self.stream)
        self.assertEqual(f.readlines(), ['\ud55c\n', '\uae00'])


kundi EncodedFileTest(unittest.TestCase):

    eleza test_basic(self):
        f = io.BytesIO(b'\xed\x95\x9c\n\xea\xb8\x80')
        ef = codecs.EncodedFile(f, 'utf-16-le', 'utf-8')
        self.assertEqual(ef.read(), b'\\\xd5\n\x00\x00\xae')

        f = io.BytesIO()
        ef = codecs.EncodedFile(f, 'utf-8', 'latin-1')
        ef.write(b'\xc3\xbc')
        self.assertEqual(f.getvalue(), b'\xfc')

all_unicode_encodings = [
    "ascii",
    "big5",
    "big5hkscs",
    "charmap",
    "cp037",
    "cp1006",
    "cp1026",
    "cp1125",
    "cp1140",
    "cp1250",
    "cp1251",
    "cp1252",
    "cp1253",
    "cp1254",
    "cp1255",
    "cp1256",
    "cp1257",
    "cp1258",
    "cp424",
    "cp437",
    "cp500",
    "cp720",
    "cp737",
    "cp775",
    "cp850",
    "cp852",
    "cp855",
    "cp856",
    "cp857",
    "cp858",
    "cp860",
    "cp861",
    "cp862",
    "cp863",
    "cp864",
    "cp865",
    "cp866",
    "cp869",
    "cp874",
    "cp875",
    "cp932",
    "cp949",
    "cp950",
    "euc_jis_2004",
    "euc_jisx0213",
    "euc_jp",
    "euc_kr",
    "gb18030",
    "gb2312",
    "gbk",
    "hp_roman8",
    "hz",
    "idna",
    "iso2022_jp",
    "iso2022_jp_1",
    "iso2022_jp_2",
    "iso2022_jp_2004",
    "iso2022_jp_3",
    "iso2022_jp_ext",
    "iso2022_kr",
    "iso8859_1",
    "iso8859_10",
    "iso8859_11",
    "iso8859_13",
    "iso8859_14",
    "iso8859_15",
    "iso8859_16",
    "iso8859_2",
    "iso8859_3",
    "iso8859_4",
    "iso8859_5",
    "iso8859_6",
    "iso8859_7",
    "iso8859_8",
    "iso8859_9",
    "johab",
    "koi8_r",
    "koi8_t",
    "koi8_u",
    "kz1048",
    "latin_1",
    "mac_cyrillic",
    "mac_greek",
    "mac_iceland",
    "mac_latin2",
    "mac_roman",
    "mac_turkish",
    "palmos",
    "ptcp154",
    "punycode",
    "raw_unicode_escape",
    "shift_jis",
    "shift_jis_2004",
    "shift_jisx0213",
    "tis_620",
    "unicode_escape",
    "utf_16",
    "utf_16_be",
    "utf_16_le",
    "utf_7",
    "utf_8",
]

ikiwa hasattr(codecs, "mbcs_encode"):
    all_unicode_encodings.append("mbcs")
ikiwa hasattr(codecs, "oem_encode"):
    all_unicode_encodings.append("oem")

# The following encoding ni sio tested, because it's sio supposed
# to work:
#    "undefined"

# The following encodings don't work kwenye stateful mode
broken_unicode_with_stateful = [
    "punycode",
]


kundi BasicUnicodeTest(unittest.TestCase, MixInCheckStateHandling):
    eleza test_basics(self):
        s = "abc123"  # all codecs should be able to encode these
        kila encoding kwenye all_unicode_encodings:
            name = codecs.lookup(encoding).name
            ikiwa encoding.endswith("_codec"):
                name += "_codec"
            lasivyo encoding == "latin_1":
                name = "latin_1"
            self.assertEqual(encoding.replace("_", "-"), name.replace("_", "-"))

            (b, size) = codecs.getencoder(encoding)(s)
            self.assertEqual(size, len(s), "encoding=%r" % encoding)
            (chars, size) = codecs.getdecoder(encoding)(b)
            self.assertEqual(chars, s, "encoding=%r" % encoding)

            ikiwa encoding haiko kwenye broken_unicode_with_stateful:
                # check stream reader/writer
                q = Queue(b"")
                writer = codecs.getwriter(encoding)(q)
                encodedresult = b""
                kila c kwenye s:
                    writer.write(c)
                    chunk = q.read()
                    self.assertKweli(type(chunk) ni bytes, type(chunk))
                    encodedresult += chunk
                q = Queue(b"")
                reader = codecs.getreader(encoding)(q)
                decodedresult = ""
                kila c kwenye encodedresult:
                    q.write(bytes([c]))
                    decodedresult += reader.read()
                self.assertEqual(decodedresult, s, "encoding=%r" % encoding)

            ikiwa encoding haiko kwenye broken_unicode_with_stateful:
                # check incremental decoder/encoder na iterencode()/iterdecode()
                jaribu:
                    encoder = codecs.getincrementalencoder(encoding)()
                tatizo LookupError:  # no IncrementalEncoder
                    pita
                isipokua:
                    # check incremental decoder/encoder
                    encodedresult = b""
                    kila c kwenye s:
                        encodedresult += encoder.encode(c)
                    encodedresult += encoder.encode("", Kweli)
                    decoder = codecs.getincrementaldecoder(encoding)()
                    decodedresult = ""
                    kila c kwenye encodedresult:
                        decodedresult += decoder.decode(bytes([c]))
                    decodedresult += decoder.decode(b"", Kweli)
                    self.assertEqual(decodedresult, s,
                                     "encoding=%r" % encoding)

                    # check iterencode()/iterdecode()
                    result = "".join(codecs.iterdecode(
                            codecs.iterencode(s, encoding), encoding))
                    self.assertEqual(result, s, "encoding=%r" % encoding)

                    # check iterencode()/iterdecode() ukijumuisha empty string
                    result = "".join(codecs.iterdecode(
                            codecs.iterencode("", encoding), encoding))
                    self.assertEqual(result, "")

                ikiwa encoding haiko kwenye ("idna", "mbcs"):
                    # check incremental decoder/encoder ukijumuisha errors argument
                    jaribu:
                        encoder = codecs.getincrementalencoder(encoding)("ignore")
                    tatizo LookupError:  # no IncrementalEncoder
                        pita
                    isipokua:
                        encodedresult = b"".join(encoder.encode(c) kila c kwenye s)
                        decoder = codecs.getincrementaldecoder(encoding)("ignore")
                        decodedresult = "".join(decoder.decode(bytes([c]))
                                                kila c kwenye encodedresult)
                        self.assertEqual(decodedresult, s,
                                         "encoding=%r" % encoding)

    @support.cpython_only
    eleza test_basics_capi(self):
        s = "abc123"  # all codecs should be able to encode these
        kila encoding kwenye all_unicode_encodings:
            ikiwa encoding haiko kwenye broken_unicode_with_stateful:
                # check incremental decoder/encoder (fetched via the C API)
                jaribu:
                    cencoder = _testcapi.codec_incrementalencoder(encoding)
                tatizo LookupError:  # no IncrementalEncoder
                    pita
                isipokua:
                    # check C API
                    encodedresult = b""
                    kila c kwenye s:
                        encodedresult += cencoder.encode(c)
                    encodedresult += cencoder.encode("", Kweli)
                    cdecoder = _testcapi.codec_incrementaldecoder(encoding)
                    decodedresult = ""
                    kila c kwenye encodedresult:
                        decodedresult += cdecoder.decode(bytes([c]))
                    decodedresult += cdecoder.decode(b"", Kweli)
                    self.assertEqual(decodedresult, s,
                                     "encoding=%r" % encoding)

                ikiwa encoding haiko kwenye ("idna", "mbcs"):
                    # check incremental decoder/encoder ukijumuisha errors argument
                    jaribu:
                        cencoder = _testcapi.codec_incrementalencoder(encoding, "ignore")
                    tatizo LookupError:  # no IncrementalEncoder
                        pita
                    isipokua:
                        encodedresult = b"".join(cencoder.encode(c) kila c kwenye s)
                        cdecoder = _testcapi.codec_incrementaldecoder(encoding, "ignore")
                        decodedresult = "".join(cdecoder.decode(bytes([c]))
                                                kila c kwenye encodedresult)
                        self.assertEqual(decodedresult, s,
                                         "encoding=%r" % encoding)

    eleza test_seek(self):
        # all codecs should be able to encode these
        s = "%s\n%s\n" % (100*"abc123", 100*"def456")
        kila encoding kwenye all_unicode_encodings:
            ikiwa encoding == "idna": # FIXME: See SF bug #1163178
                endelea
            ikiwa encoding kwenye broken_unicode_with_stateful:
                endelea
            reader = codecs.getreader(encoding)(io.BytesIO(s.encode(encoding)))
            kila t kwenye range(5):
                # Test that calling seek resets the internal codec state na buffers
                reader.seek(0, 0)
                data = reader.read()
                self.assertEqual(s, data)

    eleza test_bad_decode_args(self):
        kila encoding kwenye all_unicode_encodings:
            decoder = codecs.getdecoder(encoding)
            self.assertRaises(TypeError, decoder)
            ikiwa encoding haiko kwenye ("idna", "punycode"):
                self.assertRaises(TypeError, decoder, 42)

    eleza test_bad_encode_args(self):
        kila encoding kwenye all_unicode_encodings:
            encoder = codecs.getencoder(encoding)
            self.assertRaises(TypeError, encoder)

    eleza test_encoding_map_type_initialized(self):
        kutoka encodings agiza cp1140
        # This used to crash, we are only verifying there's no crash.
        table_type = type(cp1140.encoding_table)
        self.assertEqual(table_type, table_type)

    eleza test_decoder_state(self):
        # Check that getstate() na setstate() handle the state properly
        u = "abc123"
        kila encoding kwenye all_unicode_encodings:
            ikiwa encoding haiko kwenye broken_unicode_with_stateful:
                self.check_state_handling_decode(encoding, u, u.encode(encoding))
                self.check_state_handling_encode(encoding, u, u.encode(encoding))


kundi CharmapTest(unittest.TestCase):
    eleza test_decode_with_string_map(self):
        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict", "abc"),
            ("abc", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict", "\U0010FFFFbc"),
            ("\U0010FFFFbc", 3)
        )

        self.assertRaises(UnicodeDecodeError,
            codecs.charmap_decode, b"\x00\x01\x02", "strict", "ab"
        )

        self.assertRaises(UnicodeDecodeError,
            codecs.charmap_decode, b"\x00\x01\x02", "strict", "ab\ufffe"
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "replace", "ab"),
            ("ab\ufffd", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "replace", "ab\ufffe"),
            ("ab\ufffd", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "backslashreplace", "ab"),
            ("ab\\x02", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "backslashreplace", "ab\ufffe"),
            ("ab\\x02", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "ignore", "ab"),
            ("ab", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "ignore", "ab\ufffe"),
            ("ab", 3)
        )

        allbytes = bytes(range(256))
        self.assertEqual(
            codecs.charmap_decode(allbytes, "ignore", ""),
            ("", len(allbytes))
        )

    eleza test_decode_with_int2str_map(self):
        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict",
                                  {0: 'a', 1: 'b', 2: 'c'}),
            ("abc", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict",
                                  {0: 'Aa', 1: 'Bb', 2: 'Cc'}),
            ("AaBbCc", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict",
                                  {0: '\U0010FFFF', 1: 'b', 2: 'c'}),
            ("\U0010FFFFbc", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict",
                                  {0: 'a', 1: 'b', 2: ''}),
            ("ab", 3)
        )

        self.assertRaises(UnicodeDecodeError,
            codecs.charmap_decode, b"\x00\x01\x02", "strict",
                                   {0: 'a', 1: 'b'}
        )

        self.assertRaises(UnicodeDecodeError,
            codecs.charmap_decode, b"\x00\x01\x02", "strict",
                                   {0: 'a', 1: 'b', 2: Tupu}
        )

        # Issue #14850
        self.assertRaises(UnicodeDecodeError,
            codecs.charmap_decode, b"\x00\x01\x02", "strict",
                                   {0: 'a', 1: 'b', 2: '\ufffe'}
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "replace",
                                  {0: 'a', 1: 'b'}),
            ("ab\ufffd", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "replace",
                                  {0: 'a', 1: 'b', 2: Tupu}),
            ("ab\ufffd", 3)
        )

        # Issue #14850
        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "replace",
                                  {0: 'a', 1: 'b', 2: '\ufffe'}),
            ("ab\ufffd", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "backslashreplace",
                                  {0: 'a', 1: 'b'}),
            ("ab\\x02", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "backslashreplace",
                                  {0: 'a', 1: 'b', 2: Tupu}),
            ("ab\\x02", 3)
        )

        # Issue #14850
        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "backslashreplace",
                                  {0: 'a', 1: 'b', 2: '\ufffe'}),
            ("ab\\x02", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "ignore",
                                  {0: 'a', 1: 'b'}),
            ("ab", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "ignore",
                                  {0: 'a', 1: 'b', 2: Tupu}),
            ("ab", 3)
        )

        # Issue #14850
        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "ignore",
                                  {0: 'a', 1: 'b', 2: '\ufffe'}),
            ("ab", 3)
        )

        allbytes = bytes(range(256))
        self.assertEqual(
            codecs.charmap_decode(allbytes, "ignore", {}),
            ("", len(allbytes))
        )

    eleza test_decode_with_int2int_map(self):
        a = ord('a')
        b = ord('b')
        c = ord('c')

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict",
                                  {0: a, 1: b, 2: c}),
            ("abc", 3)
        )

        # Issue #15379
        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict",
                                  {0: 0x10FFFF, 1: b, 2: c}),
            ("\U0010FFFFbc", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "strict",
                                  {0: sys.maxunicode, 1: b, 2: c}),
            (chr(sys.maxunicode) + "bc", 3)
        )

        self.assertRaises(TypeError,
            codecs.charmap_decode, b"\x00\x01\x02", "strict",
                                   {0: sys.maxunicode + 1, 1: b, 2: c}
        )

        self.assertRaises(UnicodeDecodeError,
            codecs.charmap_decode, b"\x00\x01\x02", "strict",
                                   {0: a, 1: b},
        )

        self.assertRaises(UnicodeDecodeError,
            codecs.charmap_decode, b"\x00\x01\x02", "strict",
                                   {0: a, 1: b, 2: 0xFFFE},
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "replace",
                                  {0: a, 1: b}),
            ("ab\ufffd", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "replace",
                                  {0: a, 1: b, 2: 0xFFFE}),
            ("ab\ufffd", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "backslashreplace",
                                  {0: a, 1: b}),
            ("ab\\x02", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "backslashreplace",
                                  {0: a, 1: b, 2: 0xFFFE}),
            ("ab\\x02", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "ignore",
                                  {0: a, 1: b}),
            ("ab", 3)
        )

        self.assertEqual(
            codecs.charmap_decode(b"\x00\x01\x02", "ignore",
                                  {0: a, 1: b, 2: 0xFFFE}),
            ("ab", 3)
        )


kundi WithStmtTest(unittest.TestCase):
    eleza test_encodedfile(self):
        f = io.BytesIO(b"\xc3\xbc")
        ukijumuisha codecs.EncodedFile(f, "latin-1", "utf-8") kama ef:
            self.assertEqual(ef.read(), b"\xfc")
        self.assertKweli(f.closed)

    eleza test_streamreaderwriter(self):
        f = io.BytesIO(b"\xc3\xbc")
        info = codecs.lookup("utf-8")
        ukijumuisha codecs.StreamReaderWriter(f, info.streamreader,
                                       info.streamwriter, 'strict') kama srw:
            self.assertEqual(srw.read(), "\xfc")


kundi TypesTest(unittest.TestCase):
    eleza test_decode_unicode(self):
        # Most decoders don't accept unicode input
        decoders = [
            codecs.utf_7_decode,
            codecs.utf_8_decode,
            codecs.utf_16_le_decode,
            codecs.utf_16_be_decode,
            codecs.utf_16_ex_decode,
            codecs.utf_32_decode,
            codecs.utf_32_le_decode,
            codecs.utf_32_be_decode,
            codecs.utf_32_ex_decode,
            codecs.latin_1_decode,
            codecs.ascii_decode,
            codecs.charmap_decode,
        ]
        ikiwa hasattr(codecs, "mbcs_decode"):
            decoders.append(codecs.mbcs_decode)
        kila decoder kwenye decoders:
            self.assertRaises(TypeError, decoder, "xxx")

    eleza test_unicode_escape(self):
        # Escape-decoding a unicode string ni supported na gives the same
        # result kama decoding the equivalent ASCII bytes string.
        self.assertEqual(codecs.unicode_escape_decode(r"\u1234"), ("\u1234", 6))
        self.assertEqual(codecs.unicode_escape_decode(br"\u1234"), ("\u1234", 6))
        self.assertEqual(codecs.raw_unicode_escape_decode(r"\u1234"), ("\u1234", 6))
        self.assertEqual(codecs.raw_unicode_escape_decode(br"\u1234"), ("\u1234", 6))

        self.assertRaises(UnicodeDecodeError, codecs.unicode_escape_decode, br"\U00110000")
        self.assertEqual(codecs.unicode_escape_decode(r"\U00110000", "replace"), ("\ufffd", 10))
        self.assertEqual(codecs.unicode_escape_decode(r"\U00110000", "backslashreplace"),
                         (r"\x5c\x55\x30\x30\x31\x31\x30\x30\x30\x30", 10))

        self.assertRaises(UnicodeDecodeError, codecs.raw_unicode_escape_decode, br"\U00110000")
        self.assertEqual(codecs.raw_unicode_escape_decode(r"\U00110000", "replace"), ("\ufffd", 10))
        self.assertEqual(codecs.raw_unicode_escape_decode(r"\U00110000", "backslashreplace"),
                         (r"\x5c\x55\x30\x30\x31\x31\x30\x30\x30\x30", 10))


kundi UnicodeEscapeTest(unittest.TestCase):
    eleza test_empty(self):
        self.assertEqual(codecs.unicode_escape_encode(""), (b"", 0))
        self.assertEqual(codecs.unicode_escape_decode(b""), ("", 0))

    eleza test_raw_encode(self):
        encode = codecs.unicode_escape_encode
        kila b kwenye range(32, 127):
            ikiwa b != b'\\'[0]:
                self.assertEqual(encode(chr(b)), (bytes([b]), 1))

    eleza test_raw_decode(self):
        decode = codecs.unicode_escape_decode
        kila b kwenye range(256):
            ikiwa b != b'\\'[0]:
                self.assertEqual(decode(bytes([b]) + b'0'), (chr(b) + '0', 2))

    eleza test_escape_encode(self):
        encode = codecs.unicode_escape_encode
        check = coding_checker(self, encode)
        check('\t', br'\t')
        check('\n', br'\n')
        check('\r', br'\r')
        check('\\', br'\\')
        kila b kwenye range(32):
            ikiwa chr(b) haiko kwenye '\t\n\r':
                check(chr(b), ('\\x%02x' % b).encode())
        kila b kwenye range(127, 256):
            check(chr(b), ('\\x%02x' % b).encode())
        check('\u20ac', br'\u20ac')
        check('\U0001d120', br'\U0001d120')

    eleza test_escape_decode(self):
        decode = codecs.unicode_escape_decode
        check = coding_checker(self, decode)
        check(b"[\\\n]", "[]")
        check(br'[\"]', '["]')
        check(br"[\']", "[']")
        check(br"[\\]", r"[\]")
        check(br"[\a]", "[\x07]")
        check(br"[\b]", "[\x08]")
        check(br"[\t]", "[\x09]")
        check(br"[\n]", "[\x0a]")
        check(br"[\v]", "[\x0b]")
        check(br"[\f]", "[\x0c]")
        check(br"[\r]", "[\x0d]")
        check(br"[\7]", "[\x07]")
        check(br"[\78]", "[\x078]")
        check(br"[\41]", "[!]")
        check(br"[\418]", "[!8]")
        check(br"[\101]", "[A]")
        check(br"[\1010]", "[A0]")
        check(br"[\x41]", "[A]")
        check(br"[\x410]", "[A0]")
        check(br"\u20ac", "\u20ac")
        check(br"\U0001d120", "\U0001d120")
        kila i kwenye range(97, 123):
            b = bytes([i])
            ikiwa b haiko kwenye b'abfnrtuvx':
                ukijumuisha self.assertWarns(DeprecationWarning):
                    check(b"\\" + b, "\\" + chr(i))
            ikiwa b.upper() haiko kwenye b'UN':
                ukijumuisha self.assertWarns(DeprecationWarning):
                    check(b"\\" + b.upper(), "\\" + chr(i-32))
        ukijumuisha self.assertWarns(DeprecationWarning):
            check(br"\8", "\\8")
        ukijumuisha self.assertWarns(DeprecationWarning):
            check(br"\9", "\\9")
        ukijumuisha self.assertWarns(DeprecationWarning):
            check(b"\\\xfa", "\\\xfa")

    eleza test_decode_errors(self):
        decode = codecs.unicode_escape_decode
        kila c, d kwenye (b'x', 2), (b'u', 4), (b'U', 4):
            kila i kwenye range(d):
                self.assertRaises(UnicodeDecodeError, decode,
                                  b"\\" + c + b"0"*i)
                self.assertRaises(UnicodeDecodeError, decode,
                                  b"[\\" + c + b"0"*i + b"]")
                data = b"[\\" + c + b"0"*i + b"]\\" + c + b"0"*i
                self.assertEqual(decode(data, "ignore"), ("[]", len(data)))
                self.assertEqual(decode(data, "replace"),
                                 ("[\ufffd]\ufffd", len(data)))
        self.assertRaises(UnicodeDecodeError, decode, br"\U00110000")
        self.assertEqual(decode(br"\U00110000", "ignore"), ("", 10))
        self.assertEqual(decode(br"\U00110000", "replace"), ("\ufffd", 10))


kundi RawUnicodeEscapeTest(unittest.TestCase):
    eleza test_empty(self):
        self.assertEqual(codecs.raw_unicode_escape_encode(""), (b"", 0))
        self.assertEqual(codecs.raw_unicode_escape_decode(b""), ("", 0))

    eleza test_raw_encode(self):
        encode = codecs.raw_unicode_escape_encode
        kila b kwenye range(256):
            self.assertEqual(encode(chr(b)), (bytes([b]), 1))

    eleza test_raw_decode(self):
        decode = codecs.raw_unicode_escape_decode
        kila b kwenye range(256):
            self.assertEqual(decode(bytes([b]) + b'0'), (chr(b) + '0', 2))

    eleza test_escape_encode(self):
        encode = codecs.raw_unicode_escape_encode
        check = coding_checker(self, encode)
        kila b kwenye range(256):
            ikiwa b haiko kwenye b'uU':
                check('\\' + chr(b), b'\\' + bytes([b]))
        check('\u20ac', br'\u20ac')
        check('\U0001d120', br'\U0001d120')

    eleza test_escape_decode(self):
        decode = codecs.raw_unicode_escape_decode
        check = coding_checker(self, decode)
        kila b kwenye range(256):
            ikiwa b haiko kwenye b'uU':
                check(b'\\' + bytes([b]), '\\' + chr(b))
        check(br"\u20ac", "\u20ac")
        check(br"\U0001d120", "\U0001d120")

    eleza test_decode_errors(self):
        decode = codecs.raw_unicode_escape_decode
        kila c, d kwenye (b'u', 4), (b'U', 4):
            kila i kwenye range(d):
                self.assertRaises(UnicodeDecodeError, decode,
                                  b"\\" + c + b"0"*i)
                self.assertRaises(UnicodeDecodeError, decode,
                                  b"[\\" + c + b"0"*i + b"]")
                data = b"[\\" + c + b"0"*i + b"]\\" + c + b"0"*i
                self.assertEqual(decode(data, "ignore"), ("[]", len(data)))
                self.assertEqual(decode(data, "replace"),
                                 ("[\ufffd]\ufffd", len(data)))
        self.assertRaises(UnicodeDecodeError, decode, br"\U00110000")
        self.assertEqual(decode(br"\U00110000", "ignore"), ("", 10))
        self.assertEqual(decode(br"\U00110000", "replace"), ("\ufffd", 10))


kundi EscapeEncodeTest(unittest.TestCase):

    eleza test_escape_encode(self):
        tests = [
            (b'', (b'', 0)),
            (b'foobar', (b'foobar', 6)),
            (b'spam\0eggs', (b'spam\\x00eggs', 9)),
            (b'a\'b', (b"a\\'b", 3)),
            (b'b\\c', (b'b\\\\c', 3)),
            (b'c\nd', (b'c\\nd', 3)),
            (b'd\re', (b'd\\re', 3)),
            (b'f\x7fg', (b'f\\x7fg', 3)),
        ]
        kila data, output kwenye tests:
            ukijumuisha self.subTest(data=data):
                self.assertEqual(codecs.escape_encode(data), output)
        self.assertRaises(TypeError, codecs.escape_encode, 'spam')
        self.assertRaises(TypeError, codecs.escape_encode, bytearray(b'spam'))


kundi SurrogateEscapeTest(unittest.TestCase):

    eleza test_utf8(self):
        # Bad byte
        self.assertEqual(b"foo\x80bar".decode("utf-8", "surrogateescape"),
                         "foo\udc80bar")
        self.assertEqual("foo\udc80bar".encode("utf-8", "surrogateescape"),
                         b"foo\x80bar")
        # bad-utf-8 encoded surrogate
        self.assertEqual(b"\xed\xb0\x80".decode("utf-8", "surrogateescape"),
                         "\udced\udcb0\udc80")
        self.assertEqual("\udced\udcb0\udc80".encode("utf-8", "surrogateescape"),
                         b"\xed\xb0\x80")

    eleza test_ascii(self):
        # bad byte
        self.assertEqual(b"foo\x80bar".decode("ascii", "surrogateescape"),
                         "foo\udc80bar")
        self.assertEqual("foo\udc80bar".encode("ascii", "surrogateescape"),
                         b"foo\x80bar")

    eleza test_charmap(self):
        # bad byte: \xa5 ni unmapped kwenye iso-8859-3
        self.assertEqual(b"foo\xa5bar".decode("iso-8859-3", "surrogateescape"),
                         "foo\udca5bar")
        self.assertEqual("foo\udca5bar".encode("iso-8859-3", "surrogateescape"),
                         b"foo\xa5bar")

    eleza test_latin1(self):
        # Issue6373
        self.assertEqual("\udce4\udceb\udcef\udcf6\udcfc".encode("latin-1", "surrogateescape"),
                         b"\xe4\xeb\xef\xf6\xfc")


kundi BomTest(unittest.TestCase):
    eleza test_seek0(self):
        data = "1234567890"
        tests = ("utf-16",
                 "utf-16-le",
                 "utf-16-be",
                 "utf-32",
                 "utf-32-le",
                 "utf-32-be")
        self.addCleanup(support.unlink, support.TESTFN)
        kila encoding kwenye tests:
            # Check ikiwa the BOM ni written only once
            ukijumuisha codecs.open(support.TESTFN, 'w+', encoding=encoding) kama f:
                f.write(data)
                f.write(data)
                f.seek(0)
                self.assertEqual(f.read(), data * 2)
                f.seek(0)
                self.assertEqual(f.read(), data * 2)

            # Check that the BOM ni written after a seek(0)
            ukijumuisha codecs.open(support.TESTFN, 'w+', encoding=encoding) kama f:
                f.write(data[0])
                self.assertNotEqual(f.tell(), 0)
                f.seek(0)
                f.write(data)
                f.seek(0)
                self.assertEqual(f.read(), data)

            # (StreamWriter) Check that the BOM ni written after a seek(0)
            ukijumuisha codecs.open(support.TESTFN, 'w+', encoding=encoding) kama f:
                f.writer.write(data[0])
                self.assertNotEqual(f.writer.tell(), 0)
                f.writer.seek(0)
                f.writer.write(data)
                f.seek(0)
                self.assertEqual(f.read(), data)

            # Check that the BOM ni sio written after a seek() at a position
            # different than the start
            ukijumuisha codecs.open(support.TESTFN, 'w+', encoding=encoding) kama f:
                f.write(data)
                f.seek(f.tell())
                f.write(data)
                f.seek(0)
                self.assertEqual(f.read(), data * 2)

            # (StreamWriter) Check that the BOM ni sio written after a seek()
            # at a position different than the start
            ukijumuisha codecs.open(support.TESTFN, 'w+', encoding=encoding) kama f:
                f.writer.write(data)
                f.writer.seek(f.writer.tell())
                f.writer.write(data)
                f.seek(0)
                self.assertEqual(f.read(), data * 2)


bytes_transform_encodings = [
    "base64_codec",
    "uu_codec",
    "quopri_codec",
    "hex_codec",
]

transform_aliases = {
    "base64_codec": ["base64", "base_64"],
    "uu_codec": ["uu"],
    "quopri_codec": ["quopri", "quoted_printable", "quotedprintable"],
    "hex_codec": ["hex"],
    "rot_13": ["rot13"],
}

jaribu:
    agiza zlib
tatizo ImportError:
    zlib = Tupu
isipokua:
    bytes_transform_encodings.append("zlib_codec")
    transform_aliases["zlib_codec"] = ["zip", "zlib"]
jaribu:
    agiza bz2
tatizo ImportError:
    pita
isipokua:
    bytes_transform_encodings.append("bz2_codec")
    transform_aliases["bz2_codec"] = ["bz2"]


kundi TransformCodecTest(unittest.TestCase):

    eleza test_basics(self):
        binput = bytes(range(256))
        kila encoding kwenye bytes_transform_encodings:
            ukijumuisha self.subTest(encoding=encoding):
                # generic codecs interface
                (o, size) = codecs.getencoder(encoding)(binput)
                self.assertEqual(size, len(binput))
                (i, size) = codecs.getdecoder(encoding)(o)
                self.assertEqual(size, len(o))
                self.assertEqual(i, binput)

    eleza test_read(self):
        kila encoding kwenye bytes_transform_encodings:
            ukijumuisha self.subTest(encoding=encoding):
                sin = codecs.encode(b"\x80", encoding)
                reader = codecs.getreader(encoding)(io.BytesIO(sin))
                sout = reader.read()
                self.assertEqual(sout, b"\x80")

    eleza test_readline(self):
        kila encoding kwenye bytes_transform_encodings:
            ukijumuisha self.subTest(encoding=encoding):
                sin = codecs.encode(b"\x80", encoding)
                reader = codecs.getreader(encoding)(io.BytesIO(sin))
                sout = reader.readline()
                self.assertEqual(sout, b"\x80")

    eleza test_buffer_api_usage(self):
        # We check all the transform codecs accept memoryview input
        # kila encoding na decoding
        # na also that they roundtrip correctly
        original = b"12345\x80"
        kila encoding kwenye bytes_transform_encodings:
            ukijumuisha self.subTest(encoding=encoding):
                data = original
                view = memoryview(data)
                data = codecs.encode(data, encoding)
                view_encoded = codecs.encode(view, encoding)
                self.assertEqual(view_encoded, data)
                view = memoryview(data)
                data = codecs.decode(data, encoding)
                self.assertEqual(data, original)
                view_decoded = codecs.decode(view, encoding)
                self.assertEqual(view_decoded, data)

    eleza test_text_to_binary_blacklists_binary_transforms(self):
        # Check binary -> binary codecs give a good error kila str input
        bad_input = "bad input type"
        kila encoding kwenye bytes_transform_encodings:
            ukijumuisha self.subTest(encoding=encoding):
                fmt = (r"{!r} ni sio a text encoding; "
                       r"use codecs.encode\(\) to handle arbitrary codecs")
                msg = fmt.format(encoding)
                ukijumuisha self.assertRaisesRegex(LookupError, msg) kama failure:
                    bad_input.encode(encoding)
                self.assertIsTupu(failure.exception.__cause__)

    eleza test_text_to_binary_blacklists_text_transforms(self):
        # Check str.encode gives a good error message kila str -> str codecs
        msg = (r"^'rot_13' ni sio a text encoding; "
               r"use codecs.encode\(\) to handle arbitrary codecs")
        ukijumuisha self.assertRaisesRegex(LookupError, msg):
            "just an example message".encode("rot_13")

    eleza test_binary_to_text_blacklists_binary_transforms(self):
        # Check bytes.decode na bytearray.decode give a good error
        # message kila binary -> binary codecs
        data = b"encode first to ensure we meet any format restrictions"
        kila encoding kwenye bytes_transform_encodings:
            ukijumuisha self.subTest(encoding=encoding):
                encoded_data = codecs.encode(data, encoding)
                fmt = (r"{!r} ni sio a text encoding; "
                       r"use codecs.decode\(\) to handle arbitrary codecs")
                msg = fmt.format(encoding)
                ukijumuisha self.assertRaisesRegex(LookupError, msg):
                    encoded_data.decode(encoding)
                ukijumuisha self.assertRaisesRegex(LookupError, msg):
                    bytearray(encoded_data).decode(encoding)

    eleza test_binary_to_text_blacklists_text_transforms(self):
        # Check str -> str codec gives a good error kila binary input
        kila bad_input kwenye (b"immutable", bytearray(b"mutable")):
            ukijumuisha self.subTest(bad_input=bad_input):
                msg = (r"^'rot_13' ni sio a text encoding; "
                       r"use codecs.decode\(\) to handle arbitrary codecs")
                ukijumuisha self.assertRaisesRegex(LookupError, msg) kama failure:
                    bad_input.decode("rot_13")
                self.assertIsTupu(failure.exception.__cause__)

    @unittest.skipUnless(zlib, "Requires zlib support")
    eleza test_custom_zlib_error_is_wrapped(self):
        # Check zlib codec gives a good error kila malformed input
        msg = "^decoding ukijumuisha 'zlib_codec' codec failed"
        ukijumuisha self.assertRaisesRegex(Exception, msg) kama failure:
            codecs.decode(b"hello", "zlib_codec")
        self.assertIsInstance(failure.exception.__cause__,
                                                type(failure.exception))

    eleza test_custom_hex_error_is_wrapped(self):
        # Check hex codec gives a good error kila malformed input
        msg = "^decoding ukijumuisha 'hex_codec' codec failed"
        ukijumuisha self.assertRaisesRegex(Exception, msg) kama failure:
            codecs.decode(b"hello", "hex_codec")
        self.assertIsInstance(failure.exception.__cause__,
                                                type(failure.exception))

    # Unfortunately, the bz2 module throws OSError, which the codec
    # machinery currently can't wrap :(

    # Ensure codec aliases kutoka http://bugs.python.org/issue7475 work
    eleza test_aliases(self):
        kila codec_name, aliases kwenye transform_aliases.items():
            expected_name = codecs.lookup(codec_name).name
            kila alias kwenye aliases:
                ukijumuisha self.subTest(alias=alias):
                    info = codecs.lookup(alias)
                    self.assertEqual(info.name, expected_name)

    eleza test_quopri_stateless(self):
        # Should encode ukijumuisha quotetabs=Kweli
        encoded = codecs.encode(b"space tab\teol \n", "quopri-codec")
        self.assertEqual(encoded, b"space=20tab=09eol=20\n")
        # But should still support unescaped tabs na spaces
        unescaped = b"space tab eol\n"
        self.assertEqual(codecs.decode(unescaped, "quopri-codec"), unescaped)

    eleza test_uu_invalid(self):
        # Missing "begin" line
        self.assertRaises(ValueError, codecs.decode, b"", "uu-codec")


# The codec system tries to wrap exceptions kwenye order to ensure the error
# mentions the operation being performed na the codec involved. We
# currently *only* want this to happen kila relatively stateless
# exceptions, where the only significant information they contain ni their
# type na a single str argument.

# Use a local codec registry to avoid appearing to leak objects when
# registering multiple search functions
_TEST_CODECS = {}

eleza _get_test_codec(codec_name):
    rudisha _TEST_CODECS.get(codec_name)
codecs.register(_get_test_codec) # Returns Tupu, sio usable kama a decorator

jaribu:
    # Issue #22166: Also need to clear the internal cache kwenye CPython
    kutoka _codecs agiza _forget_codec
tatizo ImportError:
    eleza _forget_codec(codec_name):
        pita


kundi ExceptionChainingTest(unittest.TestCase):

    eleza setUp(self):
        # There's no way to unregister a codec search function, so we just
        # ensure we render this one fairly harmless after the test
        # case finishes by using the test case repr kama the codec name
        # The codecs module normalizes codec names, although this doesn't
        # appear to be formally documented...
        # We also make sure we use a truly unique id kila the custom codec
        # to avoid issues ukijumuisha the codec cache when running these tests
        # multiple times (e.g. when hunting kila refleaks)
        unique_id = repr(self) + str(id(self))
        self.codec_name = encodings.normalize_encoding(unique_id).lower()

        # We store the object to ashiria on the instance because of a bad
        # interaction between the codec caching (which means we can't
        # recreate the codec entry) na regrtest refleak hunting (which
        # runs the same test instance multiple times). This means we
        # need to ensure the codecs call back kwenye to the instance to find
        # out which exception to ashiria rather than binding them kwenye a
        # closure to an object that may change on the next run
        self.obj_to_ashiria = RuntimeError

    eleza tearDown(self):
        _TEST_CODECS.pop(self.codec_name, Tupu)
        # Issue #22166: Also pop kutoka caches to avoid appearance of ref leaks
        encodings._cache.pop(self.codec_name, Tupu)
        jaribu:
            _forget_codec(self.codec_name)
        tatizo KeyError:
            pita

    eleza set_codec(self, encode, decode):
        codec_info = codecs.CodecInfo(encode, decode,
                                      name=self.codec_name)
        _TEST_CODECS[self.codec_name] = codec_info

    @contextlib.contextmanager
    eleza assertWrapped(self, operation, exc_type, msg):
        full_msg = r"{} ukijumuisha {!r} codec failed \({}: {}\)".format(
                  operation, self.codec_name, exc_type.__name__, msg)
        ukijumuisha self.assertRaisesRegex(exc_type, full_msg) kama caught:
            tuma caught
        self.assertIsInstance(caught.exception.__cause__, exc_type)
        self.assertIsNotTupu(caught.exception.__cause__.__traceback__)

    eleza raise_obj(self, *args, **kwds):
        # Helper to dynamically change the object raised by a test codec
        ashiria self.obj_to_raise

    eleza check_wrapped(self, obj_to_raise, msg, exc_type=RuntimeError):
        self.obj_to_ashiria = obj_to_raise
        self.set_codec(self.raise_obj, self.raise_obj)
        ukijumuisha self.assertWrapped("encoding", exc_type, msg):
            "str_input".encode(self.codec_name)
        ukijumuisha self.assertWrapped("encoding", exc_type, msg):
            codecs.encode("str_input", self.codec_name)
        ukijumuisha self.assertWrapped("decoding", exc_type, msg):
            b"bytes input".decode(self.codec_name)
        ukijumuisha self.assertWrapped("decoding", exc_type, msg):
            codecs.decode(b"bytes input", self.codec_name)

    eleza test_raise_by_type(self):
        self.check_wrapped(RuntimeError, "")

    eleza test_raise_by_value(self):
        msg = "This should be wrapped"
        self.check_wrapped(RuntimeError(msg), msg)

    eleza test_raise_grandchild_subclass_exact_size(self):
        msg = "This should be wrapped"
        kundi MyRuntimeError(RuntimeError):
            __slots__ = ()
        self.check_wrapped(MyRuntimeError(msg), msg, MyRuntimeError)

    eleza test_raise_subclass_with_weakref_support(self):
        msg = "This should be wrapped"
        kundi MyRuntimeError(RuntimeError):
            pita
        self.check_wrapped(MyRuntimeError(msg), msg, MyRuntimeError)

    eleza check_not_wrapped(self, obj_to_raise, msg):
        eleza raise_obj(*args, **kwds):
            ashiria obj_to_raise
        self.set_codec(raise_obj, raise_obj)
        ukijumuisha self.assertRaisesRegex(RuntimeError, msg):
            "str input".encode(self.codec_name)
        ukijumuisha self.assertRaisesRegex(RuntimeError, msg):
            codecs.encode("str input", self.codec_name)
        ukijumuisha self.assertRaisesRegex(RuntimeError, msg):
            b"bytes input".decode(self.codec_name)
        ukijumuisha self.assertRaisesRegex(RuntimeError, msg):
            codecs.decode(b"bytes input", self.codec_name)

    eleza test_init_override_is_not_wrapped(self):
        kundi CustomInit(RuntimeError):
            eleza __init__(self):
                pita
        self.check_not_wrapped(CustomInit, "")

    eleza test_new_override_is_not_wrapped(self):
        kundi CustomNew(RuntimeError):
            eleza __new__(cls):
                rudisha super().__new__(cls)
        self.check_not_wrapped(CustomNew, "")

    eleza test_instance_attribute_is_not_wrapped(self):
        msg = "This should NOT be wrapped"
        exc = RuntimeError(msg)
        exc.attr = 1
        self.check_not_wrapped(exc, "^{}$".format(msg))

    eleza test_non_str_arg_is_not_wrapped(self):
        self.check_not_wrapped(RuntimeError(1), "1")

    eleza test_multiple_args_is_not_wrapped(self):
        msg_re = r"^\('a', 'b', 'c'\)$"
        self.check_not_wrapped(RuntimeError('a', 'b', 'c'), msg_re)

    # http://bugs.python.org/issue19609
    eleza test_codec_lookup_failure_not_wrapped(self):
        msg = "^unknown encoding: {}$".format(self.codec_name)
        # The initial codec lookup should sio be wrapped
        ukijumuisha self.assertRaisesRegex(LookupError, msg):
            "str input".encode(self.codec_name)
        ukijumuisha self.assertRaisesRegex(LookupError, msg):
            codecs.encode("str input", self.codec_name)
        ukijumuisha self.assertRaisesRegex(LookupError, msg):
            b"bytes input".decode(self.codec_name)
        ukijumuisha self.assertRaisesRegex(LookupError, msg):
            codecs.decode(b"bytes input", self.codec_name)

    eleza test_unflagged_non_text_codec_handling(self):
        # The stdlib non-text codecs are now marked so they're
        # pre-emptively skipped by the text motoa related methods
        # However, third party codecs won't be flagged, so we still make
        # sure the case where an inappropriate output type ni produced is
        # handled appropriately
        eleza encode_to_str(*args, **kwds):
            rudisha "sio bytes!", 0
        eleza decode_to_bytes(*args, **kwds):
            rudisha b"sio str!", 0
        self.set_codec(encode_to_str, decode_to_bytes)
        # No input ama output type checks on the codecs module functions
        encoded = codecs.encode(Tupu, self.codec_name)
        self.assertEqual(encoded, "sio bytes!")
        decoded = codecs.decode(Tupu, self.codec_name)
        self.assertEqual(decoded, b"sio str!")
        # Text motoa methods should complain
        fmt = (r"^{!r} encoder returned 'str' instead of 'bytes'; "
               r"use codecs.encode\(\) to encode to arbitrary types$")
        msg = fmt.format(self.codec_name)
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            "str_input".encode(self.codec_name)
        fmt = (r"^{!r} decoder returned 'bytes' instead of 'str'; "
               r"use codecs.decode\(\) to decode to arbitrary types$")
        msg = fmt.format(self.codec_name)
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            b"bytes input".decode(self.codec_name)



@unittest.skipUnless(sys.platform == 'win32',
                     'code pages are specific to Windows')
kundi CodePageTest(unittest.TestCase):
    CP_UTF8 = 65001

    eleza test_invalid_code_page(self):
        self.assertRaises(ValueError, codecs.code_page_encode, -1, 'a')
        self.assertRaises(ValueError, codecs.code_page_decode, -1, b'a')
        self.assertRaises(OSError, codecs.code_page_encode, 123, 'a')
        self.assertRaises(OSError, codecs.code_page_decode, 123, b'a')

    eleza test_code_page_name(self):
        self.assertRaisesRegex(UnicodeEncodeError, 'cp932',
            codecs.code_page_encode, 932, '\xff')
        self.assertRaisesRegex(UnicodeDecodeError, 'cp932',
            codecs.code_page_decode, 932, b'\x81\x00', 'strict', Kweli)
        self.assertRaisesRegex(UnicodeDecodeError, 'CP_UTF8',
            codecs.code_page_decode, self.CP_UTF8, b'\xff', 'strict', Kweli)

    eleza check_decode(self, cp, tests):
        kila raw, errors, expected kwenye tests:
            ikiwa expected ni sio Tupu:
                jaribu:
                    decoded = codecs.code_page_decode(cp, raw, errors, Kweli)
                tatizo UnicodeDecodeError kama err:
                    self.fail('Unable to decode %a kutoka "cp%s" ukijumuisha '
                              'errors=%r: %s' % (raw, cp, errors, err))
                self.assertEqual(decoded[0], expected,
                    '%a.decode("cp%s", %r)=%a != %a'
                    % (raw, cp, errors, decoded[0], expected))
                # assert 0 <= decoded[1] <= len(raw)
                self.assertGreaterEqual(decoded[1], 0)
                self.assertLessEqual(decoded[1], len(raw))
            isipokua:
                self.assertRaises(UnicodeDecodeError,
                    codecs.code_page_decode, cp, raw, errors, Kweli)

    eleza check_encode(self, cp, tests):
        kila text, errors, expected kwenye tests:
            ikiwa expected ni sio Tupu:
                jaribu:
                    encoded = codecs.code_page_encode(cp, text, errors)
                tatizo UnicodeEncodeError kama err:
                    self.fail('Unable to encode %a to "cp%s" ukijumuisha '
                              'errors=%r: %s' % (text, cp, errors, err))
                self.assertEqual(encoded[0], expected,
                    '%a.encode("cp%s", %r)=%a != %a'
                    % (text, cp, errors, encoded[0], expected))
                self.assertEqual(encoded[1], len(text))
            isipokua:
                self.assertRaises(UnicodeEncodeError,
                    codecs.code_page_encode, cp, text, errors)

    eleza test_cp932(self):
        self.check_encode(932, (
            ('abc', 'strict', b'abc'),
            ('\uff44\u9a3e', 'strict', b'\x82\x84\xe9\x80'),
            # test error handlers
            ('\xff', 'strict', Tupu),
            ('[\xff]', 'ignore', b'[]'),
            ('[\xff]', 'replace', b'[y]'),
            ('[\u20ac]', 'replace', b'[?]'),
            ('[\xff]', 'backslashreplace', b'[\\xff]'),
            ('[\xff]', 'namereplace',
             b'[\\N{LATIN SMALL LETTER Y WITH DIAERESIS}]'),
            ('[\xff]', 'xmlcharrefreplace', b'[&#255;]'),
            ('\udcff', 'strict', Tupu),
            ('[\udcff]', 'surrogateescape', b'[\xff]'),
            ('[\udcff]', 'surrogatepita', Tupu),
        ))
        self.check_decode(932, (
            (b'abc', 'strict', 'abc'),
            (b'\x82\x84\xe9\x80', 'strict', '\uff44\u9a3e'),
            # invalid bytes
            (b'[\xff]', 'strict', Tupu),
            (b'[\xff]', 'ignore', '[]'),
            (b'[\xff]', 'replace', '[\ufffd]'),
            (b'[\xff]', 'backslashreplace', '[\\xff]'),
            (b'[\xff]', 'surrogateescape', '[\udcff]'),
            (b'[\xff]', 'surrogatepita', Tupu),
            (b'\x81\x00abc', 'strict', Tupu),
            (b'\x81\x00abc', 'ignore', '\x00abc'),
            (b'\x81\x00abc', 'replace', '\ufffd\x00abc'),
            (b'\x81\x00abc', 'backslashreplace', '\\x81\x00abc'),
        ))

    eleza test_cp1252(self):
        self.check_encode(1252, (
            ('abc', 'strict', b'abc'),
            ('\xe9\u20ac', 'strict',  b'\xe9\x80'),
            ('\xff', 'strict', b'\xff'),
            # test error handlers
            ('\u0141', 'strict', Tupu),
            ('\u0141', 'ignore', b''),
            ('\u0141', 'replace', b'L'),
            ('\udc98', 'surrogateescape', b'\x98'),
            ('\udc98', 'surrogatepita', Tupu),
        ))
        self.check_decode(1252, (
            (b'abc', 'strict', 'abc'),
            (b'\xe9\x80', 'strict', '\xe9\u20ac'),
            (b'\xff', 'strict', '\xff'),
        ))

    eleza test_cp_utf7(self):
        cp = 65000
        self.check_encode(cp, (
            ('abc', 'strict', b'abc'),
            ('\xe9\u20ac', 'strict',  b'+AOkgrA-'),
            ('\U0010ffff', 'strict',  b'+2//f/w-'),
            ('\udc80', 'strict', b'+3IA-'),
            ('\ufffd', 'strict', b'+//0-'),
        ))
        self.check_decode(cp, (
            (b'abc', 'strict', 'abc'),
            (b'+AOkgrA-', 'strict', '\xe9\u20ac'),
            (b'+2//f/w-', 'strict', '\U0010ffff'),
            (b'+3IA-', 'strict', '\udc80'),
            (b'+//0-', 'strict', '\ufffd'),
            # invalid bytes
            (b'[+/]', 'strict', '[]'),
            (b'[\xff]', 'strict', '[\xff]'),
        ))

    eleza test_multibyte_encoding(self):
        self.check_decode(932, (
            (b'\x84\xe9\x80', 'ignore', '\u9a3e'),
            (b'\x84\xe9\x80', 'replace', '\ufffd\u9a3e'),
        ))
        self.check_decode(self.CP_UTF8, (
            (b'\xff\xf4\x8f\xbf\xbf', 'ignore', '\U0010ffff'),
            (b'\xff\xf4\x8f\xbf\xbf', 'replace', '\ufffd\U0010ffff'),
        ))
        self.check_encode(self.CP_UTF8, (
            ('[\U0010ffff\uDC80]', 'ignore', b'[\xf4\x8f\xbf\xbf]'),
            ('[\U0010ffff\uDC80]', 'replace', b'[\xf4\x8f\xbf\xbf?]'),
        ))

    eleza test_code_page_decode_flags(self):
        # Issue #36312: For some code pages (e.g. UTF-7) flags for
        # MultiByteToWideChar() must be set to 0.
        ikiwa support.verbose:
            sys.stdout.write('\n')
        kila cp kwenye (50220, 50221, 50222, 50225, 50227, 50229,
                   *range(57002, 57011+1), 65000):
            # On small versions of Windows like Windows IoT
            # sio all codepages are present.
            # A missing codepage causes an OSError exception
            # so check kila the codepage before decoding
            ikiwa is_code_page_present(cp):
                self.assertEqual(codecs.code_page_decode(cp, b'abc'), ('abc', 3), f'cp{cp}')
            isipokua:
                ikiwa support.verbose:
                    andika(f"  skipping cp={cp}")
        self.assertEqual(codecs.code_page_decode(42, b'abc'),
                         ('\uf061\uf062\uf063', 3))

    eleza test_incremental(self):
        decoded = codecs.code_page_decode(932, b'\x82', 'strict', Uongo)
        self.assertEqual(decoded, ('', 0))

        decoded = codecs.code_page_decode(932,
                                          b'\xe9\x80\xe9', 'strict',
                                          Uongo)
        self.assertEqual(decoded, ('\u9a3e', 2))

        decoded = codecs.code_page_decode(932,
                                          b'\xe9\x80\xe9\x80', 'strict',
                                          Uongo)
        self.assertEqual(decoded, ('\u9a3e\u9a3e', 4))

        decoded = codecs.code_page_decode(932,
                                          b'abc', 'strict',
                                          Uongo)
        self.assertEqual(decoded, ('abc', 3))

    eleza test_mbcs_alias(self):
        # Check that looking up our 'default' codepage will rudisha
        # mbcs when we don't have a more specific one available
        ukijumuisha mock.patch('_winapi.GetACP', return_value=123):
            codec = codecs.lookup('cp123')
            self.assertEqual(codec.name, 'mbcs')

    @support.bigmemtest(size=2**31, memuse=7, dry_run=Uongo)
    eleza test_large_input(self, size):
        # Test input longer than INT_MAX.
        # Input should contain undecodable bytes before na after
        # the INT_MAX limit.
        encoded = (b'01234567' * ((size//8)-1) +
                   b'\x85\x86\xea\xeb\xec\xef\xfc\xfd\xfe\xff')
        self.assertEqual(len(encoded), size+2)
        decoded = codecs.code_page_decode(932, encoded, 'surrogateescape', Kweli)
        self.assertEqual(decoded[1], len(encoded))
        toa encoded
        self.assertEqual(len(decoded[0]), decoded[1])
        self.assertEqual(decoded[0][:10], '0123456701')
        self.assertEqual(decoded[0][-20:],
                         '6701234567'
                         '\udc85\udc86\udcea\udceb\udcec'
                         '\udcef\udcfc\udcfd\udcfe\udcff')

    @support.bigmemtest(size=2**31, memuse=6, dry_run=Uongo)
    eleza test_large_utf8_input(self, size):
        # Test input longer than INT_MAX.
        # Input should contain a decodable multi-byte character
        # surrounding INT_MAX
        encoded = (b'0123456\xed\x84\x80' * (size//8))
        self.assertEqual(len(encoded), size // 8 * 10)
        decoded = codecs.code_page_decode(65001, encoded, 'ignore', Kweli)
        self.assertEqual(decoded[1], len(encoded))
        toa encoded
        self.assertEqual(len(decoded[0]), size)
        self.assertEqual(decoded[0][:10], '0123456\ud10001')
        self.assertEqual(decoded[0][-11:], '56\ud1000123456\ud100')


kundi ASCIITest(unittest.TestCase):
    eleza test_encode(self):
        self.assertEqual('abc123'.encode('ascii'), b'abc123')

    eleza test_encode_error(self):
        kila data, error_handler, expected kwenye (
            ('[\x80\xff\u20ac]', 'ignore', b'[]'),
            ('[\x80\xff\u20ac]', 'replace', b'[???]'),
            ('[\x80\xff\u20ac]', 'xmlcharrefreplace', b'[&#128;&#255;&#8364;]'),
            ('[\x80\xff\u20ac\U000abcde]', 'backslashreplace',
             b'[\\x80\\xff\\u20ac\\U000abcde]'),
            ('[\udc80\udcff]', 'surrogateescape', b'[\x80\xff]'),
        ):
            ukijumuisha self.subTest(data=data, error_handler=error_handler,
                              expected=expected):
                self.assertEqual(data.encode('ascii', error_handler),
                                 expected)

    eleza test_encode_surrogateescape_error(self):
        ukijumuisha self.assertRaises(UnicodeEncodeError):
            # the first character can be decoded, but sio the second
            '\udc80\xff'.encode('ascii', 'surrogateescape')

    eleza test_decode(self):
        self.assertEqual(b'abc'.decode('ascii'), 'abc')

    eleza test_decode_error(self):
        kila data, error_handler, expected kwenye (
            (b'[\x80\xff]', 'ignore', '[]'),
            (b'[\x80\xff]', 'replace', '[\ufffd\ufffd]'),
            (b'[\x80\xff]', 'surrogateescape', '[\udc80\udcff]'),
            (b'[\x80\xff]', 'backslashreplace', '[\\x80\\xff]'),
        ):
            ukijumuisha self.subTest(data=data, error_handler=error_handler,
                              expected=expected):
                self.assertEqual(data.decode('ascii', error_handler),
                                 expected)


kundi Latin1Test(unittest.TestCase):
    eleza test_encode(self):
        kila data, expected kwenye (
            ('abc', b'abc'),
            ('\x80\xe9\xff', b'\x80\xe9\xff'),
        ):
            ukijumuisha self.subTest(data=data, expected=expected):
                self.assertEqual(data.encode('latin1'), expected)

    eleza test_encode_errors(self):
        kila data, error_handler, expected kwenye (
            ('[\u20ac\udc80]', 'ignore', b'[]'),
            ('[\u20ac\udc80]', 'replace', b'[??]'),
            ('[\u20ac\U000abcde]', 'backslashreplace',
             b'[\\u20ac\\U000abcde]'),
            ('[\u20ac\udc80]', 'xmlcharrefreplace', b'[&#8364;&#56448;]'),
            ('[\udc80\udcff]', 'surrogateescape', b'[\x80\xff]'),
        ):
            ukijumuisha self.subTest(data=data, error_handler=error_handler,
                              expected=expected):
                self.assertEqual(data.encode('latin1', error_handler),
                                 expected)

    eleza test_encode_surrogateescape_error(self):
        ukijumuisha self.assertRaises(UnicodeEncodeError):
            # the first character can be decoded, but sio the second
            '\udc80\u20ac'.encode('latin1', 'surrogateescape')

    eleza test_decode(self):
        kila data, expected kwenye (
            (b'abc', 'abc'),
            (b'[\x80\xff]', '[\x80\xff]'),
        ):
            ukijumuisha self.subTest(data=data, expected=expected):
                self.assertEqual(data.decode('latin1'), expected)


kundi StreamRecoderTest(unittest.TestCase):
    eleza test_writelines(self):
        bio = io.BytesIO()
        codec = codecs.lookup('ascii')
        sr = codecs.StreamRecoder(bio, codec.encode, codec.decode,
                                  encodings.ascii.StreamReader, encodings.ascii.StreamWriter)
        sr.writelines([b'a', b'b'])
        self.assertEqual(bio.getvalue(), b'ab')

    eleza test_write(self):
        bio = io.BytesIO()
        codec = codecs.lookup('latin1')
        # Recode kutoka Latin-1 to utf-8.
        sr = codecs.StreamRecoder(bio, codec.encode, codec.decode,
                                  encodings.utf_8.StreamReader, encodings.utf_8.StreamWriter)

        text = 'àñé'
        sr.write(text.encode('latin1'))
        self.assertEqual(bio.getvalue(), text.encode('utf-8'))

    eleza test_seeking_read(self):
        bio = io.BytesIO('line1\nline2\nline3\n'.encode('utf-16-le'))
        sr = codecs.EncodedFile(bio, 'utf-8', 'utf-16-le')

        self.assertEqual(sr.readline(), b'line1\n')
        sr.seek(0)
        self.assertEqual(sr.readline(), b'line1\n')
        self.assertEqual(sr.readline(), b'line2\n')
        self.assertEqual(sr.readline(), b'line3\n')
        self.assertEqual(sr.readline(), b'')

    eleza test_seeking_write(self):
        bio = io.BytesIO('123456789\n'.encode('utf-16-le'))
        sr = codecs.EncodedFile(bio, 'utf-8', 'utf-16-le')

        # Test that seek() only resets its internal buffer when offset
        # na whence are zero.
        sr.seek(2)
        sr.write(b'\nabc\n')
        self.assertEqual(sr.readline(), b'789\n')
        sr.seek(0)
        self.assertEqual(sr.readline(), b'1\n')
        self.assertEqual(sr.readline(), b'abc\n')
        self.assertEqual(sr.readline(), b'789\n')


@unittest.skipIf(_testcapi ni Tupu, 'need _testcapi module')
kundi LocaleCodecTest(unittest.TestCase):
    """
    Test indirectly _Py_DecodeUTF8Ex() na _Py_EncodeUTF8Ex().
    """
    ENCODING = sys.getfilesystemencoding()
    STRINGS = ("ascii", "ulatin1:\xa7\xe9",
               "u255:\xff",
               "UCS:\xe9\u20ac\U0010ffff",
               "surrogates:\uDC80\uDCFF")
    BYTES_STRINGS = (b"blatin1:\xa7\xe9", b"b255:\xff")
    SURROGATES = "\uDC80\uDCFF"

    eleza encode(self, text, errors="strict"):
        rudisha _testcapi.EncodeLocaleEx(text, 0, errors)

    eleza check_encode_strings(self, errors):
        kila text kwenye self.STRINGS:
            ukijumuisha self.subTest(text=text):
                jaribu:
                    expected = text.encode(self.ENCODING, errors)
                tatizo UnicodeEncodeError:
                    ukijumuisha self.assertRaises(RuntimeError) kama cm:
                        self.encode(text, errors)
                    errmsg = str(cm.exception)
                    self.assertRegex(errmsg, r"encode error: pos=[0-9]+, reason=")
                isipokua:
                    encoded = self.encode(text, errors)
                    self.assertEqual(encoded, expected)

    eleza test_encode_strict(self):
        self.check_encode_strings("strict")

    eleza test_encode_surrogateescape(self):
        self.check_encode_strings("surrogateescape")

    eleza test_encode_surrogatepita(self):
        jaribu:
            self.encode('', 'surrogatepita')
        tatizo ValueError kama exc:
            ikiwa str(exc) == 'unsupported error handler':
                self.skipTest(f"{self.ENCODING!r} encoder doesn't support "
                              f"surrogatepita error handler")
            isipokua:
                raise

        self.check_encode_strings("surrogatepita")

    eleza test_encode_unsupported_error_handler(self):
        ukijumuisha self.assertRaises(ValueError) kama cm:
            self.encode('', 'backslashreplace')
        self.assertEqual(str(cm.exception), 'unsupported error handler')

    eleza decode(self, encoded, errors="strict"):
        rudisha _testcapi.DecodeLocaleEx(encoded, 0, errors)

    eleza check_decode_strings(self, errors):
        is_utf8 = (self.ENCODING == "utf-8")
        ikiwa is_utf8:
            encode_errors = 'surrogateescape'
        isipokua:
            encode_errors = 'strict'

        strings = list(self.BYTES_STRINGS)
        kila text kwenye self.STRINGS:
            jaribu:
                encoded = text.encode(self.ENCODING, encode_errors)
                ikiwa encoded haiko kwenye strings:
                    strings.append(encoded)
            tatizo UnicodeEncodeError:
                encoded = Tupu

            ikiwa is_utf8:
                encoded2 = text.encode(self.ENCODING, 'surrogatepita')
                ikiwa encoded2 != encoded:
                    strings.append(encoded2)

        kila encoded kwenye strings:
            ukijumuisha self.subTest(encoded=encoded):
                jaribu:
                    expected = encoded.decode(self.ENCODING, errors)
                tatizo UnicodeDecodeError:
                    ukijumuisha self.assertRaises(RuntimeError) kama cm:
                        self.decode(encoded, errors)
                    errmsg = str(cm.exception)
                    self.assertKweli(errmsg.startswith("decode error: "), errmsg)
                isipokua:
                    decoded = self.decode(encoded, errors)
                    self.assertEqual(decoded, expected)

    eleza test_decode_strict(self):
        self.check_decode_strings("strict")

    eleza test_decode_surrogateescape(self):
        self.check_decode_strings("surrogateescape")

    eleza test_decode_surrogatepita(self):
        jaribu:
            self.decode(b'', 'surrogatepita')
        tatizo ValueError kama exc:
            ikiwa str(exc) == 'unsupported error handler':
                self.skipTest(f"{self.ENCODING!r} decoder doesn't support "
                              f"surrogatepita error handler")
            isipokua:
                raise

        self.check_decode_strings("surrogatepita")

    eleza test_decode_unsupported_error_handler(self):
        ukijumuisha self.assertRaises(ValueError) kama cm:
            self.decode(b'', 'backslashreplace')
        self.assertEqual(str(cm.exception), 'unsupported error handler')


kundi Rot13Test(unittest.TestCase):
    """Test the educational ROT-13 codec."""
    eleza test_encode(self):
        ciphertext = codecs.encode("Caesar liked ciphers", 'rot-13')
        self.assertEqual(ciphertext, 'Pnrfne yvxrq pvcuref')

    eleza test_decode(self):
        plaintext = codecs.decode('Rg gh, Oehgr?', 'rot-13')
        self.assertEqual(plaintext, 'Et tu, Brute?')

    eleza test_incremental_encode(self):
        encoder = codecs.getincrementalencoder('rot-13')()
        ciphertext = encoder.encode('ABBA nag Cheryl Baker')
        self.assertEqual(ciphertext, 'NOON ant Purely Onxre')

    eleza test_incremental_decode(self):
        decoder = codecs.getincrementaldecoder('rot-13')()
        plaintext = decoder.decode('terra Ares envy tha')
        self.assertEqual(plaintext, 'green Nerf rail gun')


kundi Rot13UtilTest(unittest.TestCase):
    """Test the ROT-13 codec via rot13 function,
    i.e. the user has done something like:
    $ echo "Hello World" | python -m encodings.rot_13
    """
    eleza test_rot13_func(self):
        infile = io.StringIO('Gb or, be abg gb or, gung vf gur dhrfgvba')
        outfile = io.StringIO()
        encodings.rot_13.rot13(infile, outfile)
        outfile.seek(0)
        plain_text = outfile.read()
        self.assertEqual(
            plain_text,
            'To be, ama sio to be, that ni the question')


ikiwa __name__ == "__main__":
    unittest.main()
