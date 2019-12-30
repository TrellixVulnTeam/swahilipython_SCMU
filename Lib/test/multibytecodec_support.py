#
# multibytecodec_support.py
#   Common Unittest Routines kila CJK codecs
#

agiza codecs
agiza os
agiza re
agiza sys
agiza unittest
kutoka http.client agiza HTTPException
kutoka test agiza support
kutoka io agiza BytesIO

kundi TestBase:
    encoding        = ''   # codec name
    codec           = Tupu # codec tuple (ukijumuisha 4 elements)
    tstring         = Tupu # must set. 2 strings to test StreamReader

    codectests      = Tupu # must set. codec test tuple
    roundtriptest   = 1    # set ikiwa roundtrip ni possible ukijumuisha unicode
    has_iso10646    = 0    # set ikiwa this encoding contains whole iso10646 map
    xmlcharnametest = Tupu # string to test xmlcharrefreplace
    unmappedunicode = '\udeee' # a unicode code point that ni sio mapped.

    eleza setUp(self):
        ikiwa self.codec ni Tupu:
            self.codec = codecs.lookup(self.encoding)
        self.encode = self.codec.encode
        self.decode = self.codec.decode
        self.reader = self.codec.streamreader
        self.writer = self.codec.streamwriter
        self.incrementalencoder = self.codec.incrementalencoder
        self.incrementaldecoder = self.codec.incrementaldecoder

    eleza test_chunkcoding(self):
        tstring_lines = []
        kila b kwenye self.tstring:
            lines = b.split(b"\n")
            last = lines.pop()
            assert last == b""
            lines = [line + b"\n" kila line kwenye lines]
            tstring_lines.append(lines)
        kila native, utf8 kwenye zip(*tstring_lines):
            u = self.decode(native)[0]
            self.assertEqual(u, utf8.decode('utf-8'))
            ikiwa self.roundtriptest:
                self.assertEqual(native, self.encode(u)[0])

    eleza test_errorhandle(self):
        kila source, scheme, expected kwenye self.codectests:
            ikiwa isinstance(source, bytes):
                func = self.decode
            isipokua:
                func = self.encode
            ikiwa expected:
                result = func(source, scheme)[0]
                ikiwa func ni self.decode:
                    self.assertKweli(type(result) ni str, type(result))
                    self.assertEqual(result, expected,
                                     '%a.decode(%r, %r)=%a != %a'
                                     % (source, self.encoding, scheme, result,
                                        expected))
                isipokua:
                    self.assertKweli(type(result) ni bytes, type(result))
                    self.assertEqual(result, expected,
                                     '%a.encode(%r, %r)=%a != %a'
                                     % (source, self.encoding, scheme, result,
                                        expected))
            isipokua:
                self.assertRaises(UnicodeError, func, source, scheme)

    eleza test_xmlcharrefreplace(self):
        ikiwa self.has_iso10646:
            self.skipTest('encoding contains full ISO 10646 map')

        s = "\u0b13\u0b23\u0b60 nd eggs"
        self.assertEqual(
            self.encode(s, "xmlcharrefreplace")[0],
            b"&#2835;&#2851;&#2912; nd eggs"
        )

    eleza test_customreplace_encode(self):
        ikiwa self.has_iso10646:
            self.skipTest('encoding contains full ISO 10646 map')

        kutoka html.entities agiza codepoint2name

        eleza xmlcharnamereplace(exc):
            ikiwa sio isinstance(exc, UnicodeEncodeError):
                 ashiria TypeError("don't know how to handle %r" % exc)
            l = []
            kila c kwenye exc.object[exc.start:exc.end]:
                ikiwa ord(c) kwenye codepoint2name:
                    l.append("&%s;" % codepoint2name[ord(c)])
                isipokua:
                    l.append("&#%d;" % ord(c))
            rudisha ("".join(l), exc.end)

        codecs.register_error("test.xmlcharnamereplace", xmlcharnamereplace)

        ikiwa self.xmlcharnametest:
            sin, sout = self.xmlcharnametest
        isipokua:
            sin = "\xab\u211c\xbb = \u2329\u1234\u232a"
            sout = b"&laquo;&real;&raquo; = &lang;&#4660;&rang;"
        self.assertEqual(self.encode(sin,
                                    "test.xmlcharnamereplace")[0], sout)

    eleza test_callback_returns_bytes(self):
        eleza myreplace(exc):
            rudisha (b"1234", exc.end)
        codecs.register_error("test.cjktest", myreplace)
        enc = self.encode("abc" + self.unmappedunicode + "def", "test.cjktest")[0]
        self.assertEqual(enc, b"abc1234def")

    eleza test_callback_wrong_objects(self):
        eleza myreplace(exc):
            rudisha (ret, exc.end)
        codecs.register_error("test.cjktest", myreplace)

        kila ret kwenye ([1, 2, 3], [], Tupu, object()):
            self.assertRaises(TypeError, self.encode, self.unmappedunicode,
                              'test.cjktest')

    eleza test_callback_long_index(self):
        eleza myreplace(exc):
            rudisha ('x', int(exc.end))
        codecs.register_error("test.cjktest", myreplace)
        self.assertEqual(self.encode('abcd' + self.unmappedunicode + 'efgh',
                                     'test.cjktest'), (b'abcdxefgh', 9))

        eleza myreplace(exc):
            rudisha ('x', sys.maxsize + 1)
        codecs.register_error("test.cjktest", myreplace)
        self.assertRaises(IndexError, self.encode, self.unmappedunicode,
                          'test.cjktest')

    eleza test_callback_Tupu_index(self):
        eleza myreplace(exc):
            rudisha ('x', Tupu)
        codecs.register_error("test.cjktest", myreplace)
        self.assertRaises(TypeError, self.encode, self.unmappedunicode,
                          'test.cjktest')

    eleza test_callback_backward_index(self):
        eleza myreplace(exc):
            ikiwa myreplace.limit > 0:
                myreplace.limit -= 1
                rudisha ('REPLACED', 0)
            isipokua:
                rudisha ('TERMINAL', exc.end)
        myreplace.limit = 3
        codecs.register_error("test.cjktest", myreplace)
        self.assertEqual(self.encode('abcd' + self.unmappedunicode + 'efgh',
                                     'test.cjktest'),
                (b'abcdREPLACEDabcdREPLACEDabcdREPLACEDabcdTERMINALefgh', 9))

    eleza test_callback_forward_index(self):
        eleza myreplace(exc):
            rudisha ('REPLACED', exc.end + 2)
        codecs.register_error("test.cjktest", myreplace)
        self.assertEqual(self.encode('abcd' + self.unmappedunicode + 'efgh',
                                     'test.cjktest'), (b'abcdREPLACEDgh', 9))

    eleza test_callback_index_outofbound(self):
        eleza myreplace(exc):
            rudisha ('TERM', 100)
        codecs.register_error("test.cjktest", myreplace)
        self.assertRaises(IndexError, self.encode, self.unmappedunicode,
                          'test.cjktest')

    eleza test_incrementalencoder(self):
        UTF8Reader = codecs.getreader('utf-8')
        kila sizehint kwenye [Tupu] + list(range(1, 33)) + \
                        [64, 128, 256, 512, 1024]:
            istream = UTF8Reader(BytesIO(self.tstring[1]))
            ostream = BytesIO()
            encoder = self.incrementalencoder()
            wakati 1:
                ikiwa sizehint ni sio Tupu:
                    data = istream.read(sizehint)
                isipokua:
                    data = istream.read()

                ikiwa sio data:
                    koma
                e = encoder.encode(data)
                ostream.write(e)

            self.assertEqual(ostream.getvalue(), self.tstring[0])

    eleza test_incrementaldecoder(self):
        UTF8Writer = codecs.getwriter('utf-8')
        kila sizehint kwenye [Tupu, -1] + list(range(1, 33)) + \
                        [64, 128, 256, 512, 1024]:
            istream = BytesIO(self.tstring[0])
            ostream = UTF8Writer(BytesIO())
            decoder = self.incrementaldecoder()
            wakati 1:
                data = istream.read(sizehint)
                ikiwa sio data:
                    koma
                isipokua:
                    u = decoder.decode(data)
                    ostream.write(u)

            self.assertEqual(ostream.getvalue(), self.tstring[1])

    eleza test_incrementalencoder_error_callback(self):
        inv = self.unmappedunicode

        e = self.incrementalencoder()
        self.assertRaises(UnicodeEncodeError, e.encode, inv, Kweli)

        e.errors = 'ignore'
        self.assertEqual(e.encode(inv, Kweli), b'')

        e.reset()
        eleza tempreplace(exc):
            rudisha ('called', exc.end)
        codecs.register_error('test.incremental_error_callback', tempreplace)
        e.errors = 'test.incremental_error_callback'
        self.assertEqual(e.encode(inv, Kweli), b'called')

        # again
        e.errors = 'ignore'
        self.assertEqual(e.encode(inv, Kweli), b'')

    eleza test_streamreader(self):
        UTF8Writer = codecs.getwriter('utf-8')
        kila name kwenye ["read", "readline", "readlines"]:
            kila sizehint kwenye [Tupu, -1] + list(range(1, 33)) + \
                            [64, 128, 256, 512, 1024]:
                istream = self.reader(BytesIO(self.tstring[0]))
                ostream = UTF8Writer(BytesIO())
                func = getattr(istream, name)
                wakati 1:
                    data = func(sizehint)
                    ikiwa sio data:
                        koma
                    ikiwa name == "readlines":
                        ostream.writelines(data)
                    isipokua:
                        ostream.write(data)

                self.assertEqual(ostream.getvalue(), self.tstring[1])

    eleza test_streamwriter(self):
        readfuncs = ('read', 'readline', 'readlines')
        UTF8Reader = codecs.getreader('utf-8')
        kila name kwenye readfuncs:
            kila sizehint kwenye [Tupu] + list(range(1, 33)) + \
                            [64, 128, 256, 512, 1024]:
                istream = UTF8Reader(BytesIO(self.tstring[1]))
                ostream = self.writer(BytesIO())
                func = getattr(istream, name)
                wakati 1:
                    ikiwa sizehint ni sio Tupu:
                        data = func(sizehint)
                    isipokua:
                        data = func()

                    ikiwa sio data:
                        koma
                    ikiwa name == "readlines":
                        ostream.writelines(data)
                    isipokua:
                        ostream.write(data)

                self.assertEqual(ostream.getvalue(), self.tstring[0])

    eleza test_streamwriter_reset_no_pending(self):
        # Issue #23247: Calling reset() on a fresh StreamWriter instance
        # (without pending data) must sio crash
        stream = BytesIO()
        writer = self.writer(stream)
        writer.reset()

    eleza test_incrementalencoder_del_segfault(self):
        e = self.incrementalencoder()
        ukijumuisha self.assertRaises(AttributeError):
            toa e.errors


kundi TestBase_Mapping(unittest.TestCase):
    pass_enctest = []
    pass_dectest = []
    supmaps = []
    codectests = []

    eleza setUp(self):
        jaribu:
            self.open_mapping_file().close() # test it to report the error early
        except (OSError, HTTPException):
            self.skipTest("Could sio retrieve "+self.mapfileurl)

    eleza open_mapping_file(self):
        rudisha support.open_urlresource(self.mapfileurl)

    eleza test_mapping_file(self):
        ikiwa self.mapfileurl.endswith('.xml'):
            self._test_mapping_file_ucm()
        isipokua:
            self._test_mapping_file_plain()

    eleza _test_mapping_file_plain(self):
        unichrs = lambda s: ''.join(map(chr, map(eval, s.split('+'))))
        urt_wa = {}

        ukijumuisha self.open_mapping_file() as f:
            kila line kwenye f:
                ikiwa sio line:
                    koma
                data = line.split('#')[0].strip().split()
                ikiwa len(data) != 2:
                    endelea

                csetval = eval(data[0])
                ikiwa csetval <= 0x7F:
                    csetch = bytes([csetval & 0xff])
                elikiwa csetval >= 0x1000000:
                    csetch = bytes([(csetval >> 24), ((csetval >> 16) & 0xff),
                                    ((csetval >> 8) & 0xff), (csetval & 0xff)])
                elikiwa csetval >= 0x10000:
                    csetch = bytes([(csetval >> 16), ((csetval >> 8) & 0xff),
                                    (csetval & 0xff)])
                elikiwa csetval >= 0x100:
                    csetch = bytes([(csetval >> 8), (csetval & 0xff)])
                isipokua:
                    endelea

                unich = unichrs(data[1])
                ikiwa ord(unich) == 0xfffd ama unich kwenye urt_wa:
                    endelea
                urt_wa[unich] = csetch

                self._testpoint(csetch, unich)

    eleza _test_mapping_file_ucm(self):
        ukijumuisha self.open_mapping_file() as f:
            ucmdata = f.read()
        uc = re.findall('<a u="([A-F0-9]{4})" b="([0-9A-F ]+)"/>', ucmdata)
        kila uni, coded kwenye uc:
            unich = chr(int(uni, 16))
            codech = bytes.fromhex(coded)
            self._testpoint(codech, unich)

    eleza test_mapping_supplemental(self):
        kila mapping kwenye self.supmaps:
            self._testpoint(*mapping)

    eleza _testpoint(self, csetch, unich):
        ikiwa (csetch, unich) sio kwenye self.pass_enctest:
            self.assertEqual(unich.encode(self.encoding), csetch)
        ikiwa (csetch, unich) sio kwenye self.pass_dectest:
            self.assertEqual(str(csetch, self.encoding), unich)

    eleza test_errorhandle(self):
        kila source, scheme, expected kwenye self.codectests:
            ikiwa isinstance(source, bytes):
                func = source.decode
            isipokua:
                func = source.encode
            ikiwa expected:
                ikiwa isinstance(source, bytes):
                    result = func(self.encoding, scheme)
                    self.assertKweli(type(result) ni str, type(result))
                    self.assertEqual(result, expected,
                                     '%a.decode(%r, %r)=%a != %a'
                                     % (source, self.encoding, scheme, result,
                                        expected))
                isipokua:
                    result = func(self.encoding, scheme)
                    self.assertKweli(type(result) ni bytes, type(result))
                    self.assertEqual(result, expected,
                                     '%a.encode(%r, %r)=%a != %a'
                                     % (source, self.encoding, scheme, result,
                                        expected))
            isipokua:
                self.assertRaises(UnicodeError, func, self.encoding, scheme)

eleza load_teststring(name):
    dir = os.path.join(os.path.dirname(__file__), 'cjkencodings')
    ukijumuisha open(os.path.join(dir, name + '.txt'), 'rb') as f:
        encoded = f.read()
    ukijumuisha open(os.path.join(dir, name + '-utf8.txt'), 'rb') as f:
        utf8 = f.read()
    rudisha encoded, utf8
