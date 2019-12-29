# regression test kila SAX 2.0
# $Id$

kutoka xml.sax agiza make_parser, ContentHandler, \
                    SAXException, SAXReaderNotAvailable, SAXParseException
agiza unittest
kutoka unittest agiza mock
jaribu:
    make_parser()
tatizo SAXReaderNotAvailable:
    # don't try to test this module ikiwa we cannot create a parser
    ashiria unittest.SkipTest("no XML parsers available")
kutoka xml.sax.saxutils agiza XMLGenerator, escape, unescape, quoteattr, \
                             XMLFilterBase, prepare_input_source
kutoka xml.sax.expatreader agiza create_parser
kutoka xml.sax.handler agiza feature_namespaces, feature_external_ges
kutoka xml.sax.xmlreader agiza InputSource, AttributesImpl, AttributesNSImpl
kutoka io agiza BytesIO, StringIO
agiza codecs
agiza os.path
agiza shutil
kutoka urllib.error agiza URLError
kutoka test agiza support
kutoka test.support agiza findfile, run_unittest, FakePath, TESTFN

TEST_XMLFILE = findfile("test.xml", subdir="xmltestdata")
TEST_XMLFILE_OUT = findfile("test.xml.out", subdir="xmltestdata")
jaribu:
    TEST_XMLFILE.encode("utf-8")
    TEST_XMLFILE_OUT.encode("utf-8")
tatizo UnicodeEncodeError:
    ashiria unittest.SkipTest("filename ni sio encodable to utf8")

supports_nonascii_filenames = Kweli
ikiwa sio os.path.supports_unicode_filenames:
    jaribu:
        support.TESTFN_UNICODE.encode(support.TESTFN_ENCODING)
    tatizo (UnicodeError, TypeError):
        # Either the file system encoding ni Tupu, ama the file name
        # cannot be encoded kwenye the file system encoding.
        supports_nonascii_filenames = Uongo
requires_nonascii_filenames = unittest.skipUnless(
        supports_nonascii_filenames,
        'Requires non-ascii filenames support')

ns_uri = "http://www.python.org/xml-ns/saxtest/"

kundi XmlTestBase(unittest.TestCase):
    eleza verify_empty_attrs(self, attrs):
        self.assertRaises(KeyError, attrs.getValue, "attr")
        self.assertRaises(KeyError, attrs.getValueByQName, "attr")
        self.assertRaises(KeyError, attrs.getNameByQName, "attr")
        self.assertRaises(KeyError, attrs.getQNameByName, "attr")
        self.assertRaises(KeyError, attrs.__getitem__, "attr")
        self.assertEqual(attrs.getLength(), 0)
        self.assertEqual(attrs.getNames(), [])
        self.assertEqual(attrs.getQNames(), [])
        self.assertEqual(len(attrs), 0)
        self.assertNotIn("attr", attrs)
        self.assertEqual(list(attrs.keys()), [])
        self.assertEqual(attrs.get("attrs"), Tupu)
        self.assertEqual(attrs.get("attrs", 25), 25)
        self.assertEqual(list(attrs.items()), [])
        self.assertEqual(list(attrs.values()), [])

    eleza verify_empty_nsattrs(self, attrs):
        self.assertRaises(KeyError, attrs.getValue, (ns_uri, "attr"))
        self.assertRaises(KeyError, attrs.getValueByQName, "ns:attr")
        self.assertRaises(KeyError, attrs.getNameByQName, "ns:attr")
        self.assertRaises(KeyError, attrs.getQNameByName, (ns_uri, "attr"))
        self.assertRaises(KeyError, attrs.__getitem__, (ns_uri, "attr"))
        self.assertEqual(attrs.getLength(), 0)
        self.assertEqual(attrs.getNames(), [])
        self.assertEqual(attrs.getQNames(), [])
        self.assertEqual(len(attrs), 0)
        self.assertNotIn((ns_uri, "attr"), attrs)
        self.assertEqual(list(attrs.keys()), [])
        self.assertEqual(attrs.get((ns_uri, "attr")), Tupu)
        self.assertEqual(attrs.get((ns_uri, "attr"), 25), 25)
        self.assertEqual(list(attrs.items()), [])
        self.assertEqual(list(attrs.values()), [])

    eleza verify_attrs_wattr(self, attrs):
        self.assertEqual(attrs.getLength(), 1)
        self.assertEqual(attrs.getNames(), ["attr"])
        self.assertEqual(attrs.getQNames(), ["attr"])
        self.assertEqual(len(attrs), 1)
        self.assertIn("attr", attrs)
        self.assertEqual(list(attrs.keys()), ["attr"])
        self.assertEqual(attrs.get("attr"), "val")
        self.assertEqual(attrs.get("attr", 25), "val")
        self.assertEqual(list(attrs.items()), [("attr", "val")])
        self.assertEqual(list(attrs.values()), ["val"])
        self.assertEqual(attrs.getValue("attr"), "val")
        self.assertEqual(attrs.getValueByQName("attr"), "val")
        self.assertEqual(attrs.getNameByQName("attr"), "attr")
        self.assertEqual(attrs["attr"], "val")
        self.assertEqual(attrs.getQNameByName("attr"), "attr")


eleza xml_str(doc, encoding=Tupu):
    ikiwa encoding ni Tupu:
        rudisha doc
    rudisha '<?xml version="1.0" encoding="%s"?>\n%s' % (encoding, doc)

eleza xml_bytes(doc, encoding, decl_encoding=...):
    ikiwa decl_encoding ni ...:
        decl_encoding = encoding
    rudisha xml_str(doc, decl_encoding).encode(encoding, 'xmlcharrefreplace')

eleza make_xml_file(doc, encoding, decl_encoding=...):
    ikiwa decl_encoding ni ...:
        decl_encoding = encoding
    ukijumuisha open(TESTFN, 'w', encoding=encoding, errors='xmlcharrefreplace') kama f:
        f.write(xml_str(doc, decl_encoding))


kundi ParseTest(unittest.TestCase):
    data = '<money value="$\xa3\u20ac\U0001017b">$\xa3\u20ac\U0001017b</money>'

    eleza tearDown(self):
        support.unlink(TESTFN)

    eleza check_parse(self, f):
        kutoka xml.sax agiza parse
        result = StringIO()
        parse(f, XMLGenerator(result, 'utf-8'))
        self.assertEqual(result.getvalue(), xml_str(self.data, 'utf-8'))

    eleza test_parse_text(self):
        encodings = ('us-ascii', 'iso-8859-1', 'utf-8',
                     'utf-16', 'utf-16le', 'utf-16be')
        kila encoding kwenye encodings:
            self.check_parse(StringIO(xml_str(self.data, encoding)))
            make_xml_file(self.data, encoding)
            ukijumuisha open(TESTFN, 'r', encoding=encoding) kama f:
                self.check_parse(f)
            self.check_parse(StringIO(self.data))
            make_xml_file(self.data, encoding, Tupu)
            ukijumuisha open(TESTFN, 'r', encoding=encoding) kama f:
                self.check_parse(f)

    eleza test_parse_bytes(self):
        # UTF-8 ni default encoding, US-ASCII ni compatible ukijumuisha UTF-8,
        # UTF-16 ni autodetected
        encodings = ('us-ascii', 'utf-8', 'utf-16', 'utf-16le', 'utf-16be')
        kila encoding kwenye encodings:
            self.check_parse(BytesIO(xml_bytes(self.data, encoding)))
            make_xml_file(self.data, encoding)
            self.check_parse(TESTFN)
            ukijumuisha open(TESTFN, 'rb') kama f:
                self.check_parse(f)
            self.check_parse(BytesIO(xml_bytes(self.data, encoding, Tupu)))
            make_xml_file(self.data, encoding, Tupu)
            self.check_parse(TESTFN)
            ukijumuisha open(TESTFN, 'rb') kama f:
                self.check_parse(f)
        # accept UTF-8 ukijumuisha BOM
        self.check_parse(BytesIO(xml_bytes(self.data, 'utf-8-sig', 'utf-8')))
        make_xml_file(self.data, 'utf-8-sig', 'utf-8')
        self.check_parse(TESTFN)
        ukijumuisha open(TESTFN, 'rb') kama f:
            self.check_parse(f)
        self.check_parse(BytesIO(xml_bytes(self.data, 'utf-8-sig', Tupu)))
        make_xml_file(self.data, 'utf-8-sig', Tupu)
        self.check_parse(TESTFN)
        ukijumuisha open(TESTFN, 'rb') kama f:
            self.check_parse(f)
        # accept data ukijumuisha declared encoding
        self.check_parse(BytesIO(xml_bytes(self.data, 'iso-8859-1')))
        make_xml_file(self.data, 'iso-8859-1')
        self.check_parse(TESTFN)
        ukijumuisha open(TESTFN, 'rb') kama f:
            self.check_parse(f)
        # fail on non-UTF-8 incompatible data without declared encoding
        ukijumuisha self.assertRaises(SAXException):
            self.check_parse(BytesIO(xml_bytes(self.data, 'iso-8859-1', Tupu)))
        make_xml_file(self.data, 'iso-8859-1', Tupu)
        ukijumuisha self.assertRaises(SAXException):
            self.check_parse(TESTFN)
        ukijumuisha open(TESTFN, 'rb') kama f:
            ukijumuisha self.assertRaises(SAXException):
                self.check_parse(f)

    eleza test_parse_path_object(self):
        make_xml_file(self.data, 'utf-8', Tupu)
        self.check_parse(FakePath(TESTFN))

    eleza test_parse_InputSource(self):
        # accept data without declared but ukijumuisha explicitly specified encoding
        make_xml_file(self.data, 'iso-8859-1', Tupu)
        ukijumuisha open(TESTFN, 'rb') kama f:
            input = InputSource()
            input.setByteStream(f)
            input.setEncoding('iso-8859-1')
            self.check_parse(input)

    eleza test_parse_close_source(self):
        builtin_open = open
        fileobj = Tupu

        eleza mock_open(*args):
            nonlocal fileobj
            fileobj = builtin_open(*args)
            rudisha fileobj

        ukijumuisha mock.patch('xml.sax.saxutils.open', side_effect=mock_open):
            make_xml_file(self.data, 'iso-8859-1', Tupu)
            ukijumuisha self.assertRaises(SAXException):
                self.check_parse(TESTFN)
            self.assertKweli(fileobj.closed)

    eleza check_parseString(self, s):
        kutoka xml.sax agiza parseString
        result = StringIO()
        parseString(s, XMLGenerator(result, 'utf-8'))
        self.assertEqual(result.getvalue(), xml_str(self.data, 'utf-8'))

    eleza test_parseString_text(self):
        encodings = ('us-ascii', 'iso-8859-1', 'utf-8',
                     'utf-16', 'utf-16le', 'utf-16be')
        kila encoding kwenye encodings:
            self.check_parseString(xml_str(self.data, encoding))
        self.check_parseString(self.data)

    eleza test_parseString_bytes(self):
        # UTF-8 ni default encoding, US-ASCII ni compatible ukijumuisha UTF-8,
        # UTF-16 ni autodetected
        encodings = ('us-ascii', 'utf-8', 'utf-16', 'utf-16le', 'utf-16be')
        kila encoding kwenye encodings:
            self.check_parseString(xml_bytes(self.data, encoding))
            self.check_parseString(xml_bytes(self.data, encoding, Tupu))
        # accept UTF-8 ukijumuisha BOM
        self.check_parseString(xml_bytes(self.data, 'utf-8-sig', 'utf-8'))
        self.check_parseString(xml_bytes(self.data, 'utf-8-sig', Tupu))
        # accept data ukijumuisha declared encoding
        self.check_parseString(xml_bytes(self.data, 'iso-8859-1'))
        # fail on non-UTF-8 incompatible data without declared encoding
        ukijumuisha self.assertRaises(SAXException):
            self.check_parseString(xml_bytes(self.data, 'iso-8859-1', Tupu))

kundi MakeParserTest(unittest.TestCase):
    eleza test_make_parser2(self):
        # Creating parsers several times kwenye a row should succeed.
        # Testing this because there have been failures of this kind
        # before.
        kutoka xml.sax agiza make_parser
        p = make_parser()
        kutoka xml.sax agiza make_parser
        p = make_parser()
        kutoka xml.sax agiza make_parser
        p = make_parser()
        kutoka xml.sax agiza make_parser
        p = make_parser()
        kutoka xml.sax agiza make_parser
        p = make_parser()
        kutoka xml.sax agiza make_parser
        p = make_parser()

    eleza test_make_parser3(self):
        # Testing that make_parser can handle different types of
        # iterables.
        make_parser(['module'])
        make_parser(('module', ))
        make_parser({'module'})
        make_parser(frozenset({'module'}))
        make_parser({'module': Tupu})
        make_parser(iter(['module']))

    eleza test_make_parser4(self):
        # Testing that make_parser can handle empty iterables.
        make_parser([])
        make_parser(tuple())
        make_parser(set())
        make_parser(frozenset())
        make_parser({})
        make_parser(iter([]))

    eleza test_make_parser5(self):
        # Testing that make_parser can handle iterables ukijumuisha more than
        # one item.
        make_parser(['module1', 'module2'])
        make_parser(('module1', 'module2'))
        make_parser({'module1', 'module2'})
        make_parser(frozenset({'module1', 'module2'}))
        make_parser({'module1': Tupu, 'module2': Tupu})
        make_parser(iter(['module1', 'module2']))

# ===========================================================================
#
#   saxutils tests
#
# ===========================================================================

kundi SaxutilsTest(unittest.TestCase):
    # ===== escape
    eleza test_escape_basic(self):
        self.assertEqual(escape("Donald Duck & Co"), "Donald Duck &amp; Co")

    eleza test_escape_all(self):
        self.assertEqual(escape("<Donald Duck & Co>"),
                         "&lt;Donald Duck &amp; Co&gt;")

    eleza test_escape_extra(self):
        self.assertEqual(escape("Hei på deg", {"å" : "&aring;"}),
                         "Hei p&aring; deg")

    # ===== unescape
    eleza test_unescape_basic(self):
        self.assertEqual(unescape("Donald Duck &amp; Co"), "Donald Duck & Co")

    eleza test_unescape_all(self):
        self.assertEqual(unescape("&lt;Donald Duck &amp; Co&gt;"),
                         "<Donald Duck & Co>")

    eleza test_unescape_extra(self):
        self.assertEqual(unescape("Hei på deg", {"å" : "&aring;"}),
                         "Hei p&aring; deg")

    eleza test_unescape_amp_extra(self):
        self.assertEqual(unescape("&amp;foo;", {"&foo;": "splat"}), "&foo;")

    # ===== quoteattr
    eleza test_quoteattr_basic(self):
        self.assertEqual(quoteattr("Donald Duck & Co"),
                         '"Donald Duck &amp; Co"')

    eleza test_single_quoteattr(self):
        self.assertEqual(quoteattr('Includes "double" quotes'),
                         '\'Includes "double" quotes\'')

    eleza test_double_quoteattr(self):
        self.assertEqual(quoteattr("Includes 'single' quotes"),
                         "\"Includes 'single' quotes\"")

    eleza test_single_double_quoteattr(self):
        self.assertEqual(quoteattr("Includes 'single' na \"double\" quotes"),
                         "\"Includes 'single' na &quot;double&quot; quotes\"")

    # ===== make_parser
    eleza test_make_parser(self):
        # Creating a parser should succeed - it should fall back
        # to the expatreader
        p = make_parser(['xml.parsers.no_such_parser'])


kundi PrepareInputSourceTest(unittest.TestCase):

    eleza setUp(self):
        self.file = support.TESTFN
        ukijumuisha open(self.file, "w") kama tmp:
            tmp.write("This was read kutoka a file.")

    eleza tearDown(self):
        support.unlink(self.file)

    eleza make_byte_stream(self):
        rudisha BytesIO(b"This ni a byte stream.")

    eleza make_character_stream(self):
        rudisha StringIO("This ni a character stream.")

    eleza checkContent(self, stream, content):
        self.assertIsNotTupu(stream)
        self.assertEqual(stream.read(), content)
        stream.close()


    eleza test_character_stream(self):
        # If the source ni an InputSource ukijumuisha a character stream, use it.
        src = InputSource(self.file)
        src.setCharacterStream(self.make_character_stream())
        prep = prepare_input_source(src)
        self.assertIsTupu(prep.getByteStream())
        self.checkContent(prep.getCharacterStream(),
                          "This ni a character stream.")

    eleza test_byte_stream(self):
        # If the source ni an InputSource that does sio have a character
        # stream but does have a byte stream, use the byte stream.
        src = InputSource(self.file)
        src.setByteStream(self.make_byte_stream())
        prep = prepare_input_source(src)
        self.assertIsTupu(prep.getCharacterStream())
        self.checkContent(prep.getByteStream(),
                          b"This ni a byte stream.")

    eleza test_system_id(self):
        # If the source ni an InputSource that has neither a character
        # stream nor a byte stream, open the system ID.
        src = InputSource(self.file)
        prep = prepare_input_source(src)
        self.assertIsTupu(prep.getCharacterStream())
        self.checkContent(prep.getByteStream(),
                          b"This was read kutoka a file.")

    eleza test_string(self):
        # If the source ni a string, use it kama a system ID na open it.
        prep = prepare_input_source(self.file)
        self.assertIsTupu(prep.getCharacterStream())
        self.checkContent(prep.getByteStream(),
                          b"This was read kutoka a file.")

    eleza test_path_objects(self):
        # If the source ni a Path object, use it kama a system ID na open it.
        prep = prepare_input_source(FakePath(self.file))
        self.assertIsTupu(prep.getCharacterStream())
        self.checkContent(prep.getByteStream(),
                          b"This was read kutoka a file.")

    eleza test_binary_file(self):
        # If the source ni a binary file-like object, use it kama a byte
        # stream.
        prep = prepare_input_source(self.make_byte_stream())
        self.assertIsTupu(prep.getCharacterStream())
        self.checkContent(prep.getByteStream(),
                          b"This ni a byte stream.")

    eleza test_text_file(self):
        # If the source ni a text file-like object, use it kama a character
        # stream.
        prep = prepare_input_source(self.make_character_stream())
        self.assertIsTupu(prep.getByteStream())
        self.checkContent(prep.getCharacterStream(),
                          "This ni a character stream.")


# ===== XMLGenerator

kundi XmlgenTest:
    eleza test_xmlgen_basic(self):
        result = self.ioclass()
        gen = XMLGenerator(result)
        gen.startDocument()
        gen.startElement("doc", {})
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml("<doc></doc>"))

    eleza test_xmlgen_basic_empty(self):
        result = self.ioclass()
        gen = XMLGenerator(result, short_empty_elements=Kweli)
        gen.startDocument()
        gen.startElement("doc", {})
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml("<doc/>"))

    eleza test_xmlgen_content(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startElement("doc", {})
        gen.characters("huhei")
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml("<doc>huhei</doc>"))

    eleza test_xmlgen_content_empty(self):
        result = self.ioclass()
        gen = XMLGenerator(result, short_empty_elements=Kweli)

        gen.startDocument()
        gen.startElement("doc", {})
        gen.characters("huhei")
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml("<doc>huhei</doc>"))

    eleza test_xmlgen_pi(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.processingInstruction("test", "data")
        gen.startElement("doc", {})
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(),
            self.xml("<?test data?><doc></doc>"))

    eleza test_xmlgen_content_escape(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startElement("doc", {})
        gen.characters("<huhei&")
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(),
            self.xml("<doc>&lt;huhei&amp;</doc>"))

    eleza test_xmlgen_attr_escape(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startElement("doc", {"a": '"'})
        gen.startElement("e", {"a": "'"})
        gen.endElement("e")
        gen.startElement("e", {"a": "'\""})
        gen.endElement("e")
        gen.startElement("e", {"a": "\n\r\t"})
        gen.endElement("e")
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml(
            "<doc a='\"'><e a=\"'\"></e>"
            "<e a=\"'&quot;\"></e>"
            "<e a=\"&#10;&#13;&#9;\"></e></doc>"))

    eleza test_xmlgen_encoding(self):
        encodings = ('iso-8859-15', 'utf-8', 'utf-8-sig',
                     'utf-16', 'utf-16be', 'utf-16le',
                     'utf-32', 'utf-32be', 'utf-32le')
        kila encoding kwenye encodings:
            result = self.ioclass()
            gen = XMLGenerator(result, encoding=encoding)

            gen.startDocument()
            gen.startElement("doc", {"a": '\u20ac'})
            gen.characters("\u20ac")
            gen.endElement("doc")
            gen.endDocument()

            self.assertEqual(result.getvalue(),
                self.xml('<doc a="\u20ac">\u20ac</doc>', encoding=encoding))

    eleza test_xmlgen_unencodable(self):
        result = self.ioclass()
        gen = XMLGenerator(result, encoding='ascii')

        gen.startDocument()
        gen.startElement("doc", {"a": '\u20ac'})
        gen.characters("\u20ac")
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(),
            self.xml('<doc a="&#8364;">&#8364;</doc>', encoding='ascii'))

    eleza test_xmlgen_ignorable(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startElement("doc", {})
        gen.ignorableWhitespace(" ")
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml("<doc> </doc>"))

    eleza test_xmlgen_ignorable_empty(self):
        result = self.ioclass()
        gen = XMLGenerator(result, short_empty_elements=Kweli)

        gen.startDocument()
        gen.startElement("doc", {})
        gen.ignorableWhitespace(" ")
        gen.endElement("doc")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml("<doc> </doc>"))

    eleza test_xmlgen_encoding_bytes(self):
        encodings = ('iso-8859-15', 'utf-8', 'utf-8-sig',
                     'utf-16', 'utf-16be', 'utf-16le',
                     'utf-32', 'utf-32be', 'utf-32le')
        kila encoding kwenye encodings:
            result = self.ioclass()
            gen = XMLGenerator(result, encoding=encoding)

            gen.startDocument()
            gen.startElement("doc", {"a": '\u20ac'})
            gen.characters("\u20ac".encode(encoding))
            gen.ignorableWhitespace(" ".encode(encoding))
            gen.endElement("doc")
            gen.endDocument()

            self.assertEqual(result.getvalue(),
                self.xml('<doc a="\u20ac">\u20ac </doc>', encoding=encoding))

    eleza test_xmlgen_ns(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startPrefixMapping("ns1", ns_uri)
        gen.startElementNS((ns_uri, "doc"), "ns1:doc", {})
        # add an unqualified name
        gen.startElementNS((Tupu, "udoc"), Tupu, {})
        gen.endElementNS((Tupu, "udoc"), Tupu)
        gen.endElementNS((ns_uri, "doc"), "ns1:doc")
        gen.endPrefixMapping("ns1")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml(
           '<ns1:doc xmlns:ns1="%s"><udoc></udoc></ns1:doc>' %
                                         ns_uri))

    eleza test_xmlgen_ns_empty(self):
        result = self.ioclass()
        gen = XMLGenerator(result, short_empty_elements=Kweli)

        gen.startDocument()
        gen.startPrefixMapping("ns1", ns_uri)
        gen.startElementNS((ns_uri, "doc"), "ns1:doc", {})
        # add an unqualified name
        gen.startElementNS((Tupu, "udoc"), Tupu, {})
        gen.endElementNS((Tupu, "udoc"), Tupu)
        gen.endElementNS((ns_uri, "doc"), "ns1:doc")
        gen.endPrefixMapping("ns1")
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml(
           '<ns1:doc xmlns:ns1="%s"><udoc/></ns1:doc>' %
                                         ns_uri))

    eleza test_1463026_1(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startElementNS((Tupu, 'a'), 'a', {(Tupu, 'b'):'c'})
        gen.endElementNS((Tupu, 'a'), 'a')
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml('<a b="c"></a>'))

    eleza test_1463026_1_empty(self):
        result = self.ioclass()
        gen = XMLGenerator(result, short_empty_elements=Kweli)

        gen.startDocument()
        gen.startElementNS((Tupu, 'a'), 'a', {(Tupu, 'b'):'c'})
        gen.endElementNS((Tupu, 'a'), 'a')
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml('<a b="c"/>'))

    eleza test_1463026_2(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startPrefixMapping(Tupu, 'qux')
        gen.startElementNS(('qux', 'a'), 'a', {})
        gen.endElementNS(('qux', 'a'), 'a')
        gen.endPrefixMapping(Tupu)
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml('<a xmlns="qux"></a>'))

    eleza test_1463026_2_empty(self):
        result = self.ioclass()
        gen = XMLGenerator(result, short_empty_elements=Kweli)

        gen.startDocument()
        gen.startPrefixMapping(Tupu, 'qux')
        gen.startElementNS(('qux', 'a'), 'a', {})
        gen.endElementNS(('qux', 'a'), 'a')
        gen.endPrefixMapping(Tupu)
        gen.endDocument()

        self.assertEqual(result.getvalue(), self.xml('<a xmlns="qux"/>'))

    eleza test_1463026_3(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startPrefixMapping('my', 'qux')
        gen.startElementNS(('qux', 'a'), 'a', {(Tupu, 'b'):'c'})
        gen.endElementNS(('qux', 'a'), 'a')
        gen.endPrefixMapping('my')
        gen.endDocument()

        self.assertEqual(result.getvalue(),
            self.xml('<my:a xmlns:my="qux" b="c"></my:a>'))

    eleza test_1463026_3_empty(self):
        result = self.ioclass()
        gen = XMLGenerator(result, short_empty_elements=Kweli)

        gen.startDocument()
        gen.startPrefixMapping('my', 'qux')
        gen.startElementNS(('qux', 'a'), 'a', {(Tupu, 'b'):'c'})
        gen.endElementNS(('qux', 'a'), 'a')
        gen.endPrefixMapping('my')
        gen.endDocument()

        self.assertEqual(result.getvalue(),
            self.xml('<my:a xmlns:my="qux" b="c"/>'))

    eleza test_5027_1(self):
        # The xml prefix (as kwenye xml:lang below) ni reserved na bound by
        # definition to http://www.w3.org/XML/1998/namespace.  XMLGenerator had
        # a bug whereby a KeyError ni ashiriad because this namespace ni missing
        # kutoka a dictionary.
        #
        # This test demonstrates the bug by parsing a document.
        test_xml = StringIO(
            '<?xml version="1.0"?>'
            '<a:g1 xmlns:a="http://example.com/ns">'
             '<a:g2 xml:lang="en">Hello</a:g2>'
            '</a:g1>')

        parser = make_parser()
        parser.setFeature(feature_namespaces, Kweli)
        result = self.ioclass()
        gen = XMLGenerator(result)
        parser.setContentHandler(gen)
        parser.parse(test_xml)

        self.assertEqual(result.getvalue(),
                         self.xml(
                         '<a:g1 xmlns:a="http://example.com/ns">'
                          '<a:g2 xml:lang="en">Hello</a:g2>'
                         '</a:g1>'))

    eleza test_5027_2(self):
        # The xml prefix (as kwenye xml:lang below) ni reserved na bound by
        # definition to http://www.w3.org/XML/1998/namespace.  XMLGenerator had
        # a bug whereby a KeyError ni ashiriad because this namespace ni missing
        # kutoka a dictionary.
        #
        # This test demonstrates the bug by direct manipulation of the
        # XMLGenerator.
        result = self.ioclass()
        gen = XMLGenerator(result)

        gen.startDocument()
        gen.startPrefixMapping('a', 'http://example.com/ns')
        gen.startElementNS(('http://example.com/ns', 'g1'), 'g1', {})
        lang_attr = {('http://www.w3.org/XML/1998/namespace', 'lang'): 'en'}
        gen.startElementNS(('http://example.com/ns', 'g2'), 'g2', lang_attr)
        gen.characters('Hello')
        gen.endElementNS(('http://example.com/ns', 'g2'), 'g2')
        gen.endElementNS(('http://example.com/ns', 'g1'), 'g1')
        gen.endPrefixMapping('a')
        gen.endDocument()

        self.assertEqual(result.getvalue(),
                         self.xml(
                         '<a:g1 xmlns:a="http://example.com/ns">'
                          '<a:g2 xml:lang="en">Hello</a:g2>'
                         '</a:g1>'))

    eleza test_no_close_file(self):
        result = self.ioclass()
        eleza func(out):
            gen = XMLGenerator(out)
            gen.startDocument()
            gen.startElement("doc", {})
        func(result)
        self.assertUongo(result.closed)

    eleza test_xmlgen_fragment(self):
        result = self.ioclass()
        gen = XMLGenerator(result)

        # Don't call gen.startDocument()
        gen.startElement("foo", {"a": "1.0"})
        gen.characters("Hello")
        gen.endElement("foo")
        gen.startElement("bar", {"b": "2.0"})
        gen.endElement("bar")
        # Don't call gen.endDocument()

        self.assertEqual(result.getvalue(),
            self.xml('<foo a="1.0">Hello</foo><bar b="2.0"></bar>')[len(self.xml('')):])

kundi StringXmlgenTest(XmlgenTest, unittest.TestCase):
    iokundi = StringIO

    eleza xml(self, doc, encoding='iso-8859-1'):
        rudisha '<?xml version="1.0" encoding="%s"?>\n%s' % (encoding, doc)

    test_xmlgen_unencodable = Tupu

kundi BytesXmlgenTest(XmlgenTest, unittest.TestCase):
    iokundi = BytesIO

    eleza xml(self, doc, encoding='iso-8859-1'):
        rudisha ('<?xml version="1.0" encoding="%s"?>\n%s' %
                (encoding, doc)).encode(encoding, 'xmlcharrefreplace')

kundi WriterXmlgenTest(BytesXmlgenTest):
    kundi ioclass(list):
        write = list.append
        closed = Uongo

        eleza seekable(self):
            rudisha Kweli

        eleza tell(self):
            # rudisha 0 at start na sio 0 after start
            rudisha len(self)

        eleza getvalue(self):
            rudisha b''.join(self)

kundi StreamWriterXmlgenTest(XmlgenTest, unittest.TestCase):
    eleza ioclass(self):
        raw = BytesIO()
        writer = codecs.getwriter('ascii')(raw, 'xmlcharrefreplace')
        writer.getvalue = raw.getvalue
        rudisha writer

    eleza xml(self, doc, encoding='iso-8859-1'):
        rudisha ('<?xml version="1.0" encoding="%s"?>\n%s' %
                (encoding, doc)).encode('ascii', 'xmlcharrefreplace')

kundi StreamReaderWriterXmlgenTest(XmlgenTest, unittest.TestCase):
    fname = support.TESTFN + '-codecs'

    eleza ioclass(self):
        writer = codecs.open(self.fname, 'w', encoding='ascii',
                             errors='xmlcharrefreplace', buffering=0)
        eleza cleanup():
            writer.close()
            support.unlink(self.fname)
        self.addCleanup(cleanup)
        eleza getvalue():
            # Windows will sio let use reopen without first closing
            writer.close()
            ukijumuisha open(writer.name, 'rb') kama f:
                rudisha f.read()
        writer.getvalue = getvalue
        rudisha writer

    eleza xml(self, doc, encoding='iso-8859-1'):
        rudisha ('<?xml version="1.0" encoding="%s"?>\n%s' %
                (encoding, doc)).encode('ascii', 'xmlcharrefreplace')

start = b'<?xml version="1.0" encoding="iso-8859-1"?>\n'


kundi XMLFilterBaseTest(unittest.TestCase):
    eleza test_filter_basic(self):
        result = BytesIO()
        gen = XMLGenerator(result)
        filter = XMLFilterBase()
        filter.setContentHandler(gen)

        filter.startDocument()
        filter.startElement("doc", {})
        filter.characters("content")
        filter.ignorableWhitespace(" ")
        filter.endElement("doc")
        filter.endDocument()

        self.assertEqual(result.getvalue(), start + b"<doc>content </doc>")

# ===========================================================================
#
#   expatreader tests
#
# ===========================================================================

ukijumuisha open(TEST_XMLFILE_OUT, 'rb') kama f:
    xml_test_out = f.read()

kundi ExpatReaderTest(XmlTestBase):

    # ===== XMLReader support

    eleza test_expat_binary_file(self):
        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        ukijumuisha open(TEST_XMLFILE, 'rb') kama f:
            parser.parse(f)

        self.assertEqual(result.getvalue(), xml_test_out)

    eleza test_expat_text_file(self):
        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        ukijumuisha open(TEST_XMLFILE, 'rt', encoding='iso-8859-1') kama f:
            parser.parse(f)

        self.assertEqual(result.getvalue(), xml_test_out)

    @requires_nonascii_filenames
    eleza test_expat_binary_file_nonascii(self):
        fname = support.TESTFN_UNICODE
        shutil.copyfile(TEST_XMLFILE, fname)
        self.addCleanup(support.unlink, fname)

        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        parser.parse(open(fname, 'rb'))

        self.assertEqual(result.getvalue(), xml_test_out)

    eleza test_expat_binary_file_bytes_name(self):
        fname = os.fsencode(TEST_XMLFILE)
        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        ukijumuisha open(fname, 'rb') kama f:
            parser.parse(f)

        self.assertEqual(result.getvalue(), xml_test_out)

    eleza test_expat_binary_file_int_name(self):
        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        ukijumuisha open(TEST_XMLFILE, 'rb') kama f:
            ukijumuisha open(f.fileno(), 'rb', closefd=Uongo) kama f2:
                parser.parse(f2)

        self.assertEqual(result.getvalue(), xml_test_out)

    # ===== DTDHandler support

    kundi TestDTDHandler:

        eleza __init__(self):
            self._notations = []
            self._entities  = []

        eleza notationDecl(self, name, publicId, systemId):
            self._notations.append((name, publicId, systemId))

        eleza unparsedEntityDecl(self, name, publicId, systemId, ndata):
            self._entities.append((name, publicId, systemId, ndata))


    kundi TestEntityRecorder:
        eleza __init__(self):
            self.entities = []

        eleza resolveEntity(self, publicId, systemId):
            self.entities.append((publicId, systemId))
            source = InputSource()
            source.setPublicId(publicId)
            source.setSystemId(systemId)
            rudisha source

    eleza test_expat_dtdhandler(self):
        parser = create_parser()
        handler = self.TestDTDHandler()
        parser.setDTDHandler(handler)

        parser.feed('<!DOCTYPE doc [\n')
        parser.feed('  <!ENTITY img SYSTEM "expat.gif" NDATA GIF>\n')
        parser.feed('  <!NOTATION GIF PUBLIC "-//CompuServe//NOTATION Graphics Interchange Format 89a//EN">\n')
        parser.feed(']>\n')
        parser.feed('<doc></doc>')
        parser.close()

        self.assertEqual(handler._notations,
            [("GIF", "-//CompuServe//NOTATION Graphics Interchange Format 89a//EN", Tupu)])
        self.assertEqual(handler._entities, [("img", Tupu, "expat.gif", "GIF")])

    eleza test_expat_external_dtd_enabled(self):
        parser = create_parser()
        parser.setFeature(feature_external_ges, Kweli)
        resolver = self.TestEntityRecorder()
        parser.setEntityResolver(resolver)

        ukijumuisha self.assertRaises(URLError):
            parser.feed(
                '<!DOCTYPE external SYSTEM "unsupported://non-existing">\n'
            )
        self.assertEqual(
            resolver.entities, [(Tupu, 'unsupported://non-existing')]
        )

    eleza test_expat_external_dtd_default(self):
        parser = create_parser()
        resolver = self.TestEntityRecorder()
        parser.setEntityResolver(resolver)

        parser.feed(
            '<!DOCTYPE external SYSTEM "unsupported://non-existing">\n'
        )
        parser.feed('<doc />')
        parser.close()
        self.assertEqual(resolver.entities, [])

    # ===== EntityResolver support

    kundi TestEntityResolver:

        eleza resolveEntity(self, publicId, systemId):
            inpsrc = InputSource()
            inpsrc.setByteStream(BytesIO(b"<entity/>"))
            rudisha inpsrc

    eleza test_expat_entityresolver_enabled(self):
        parser = create_parser()
        parser.setFeature(feature_external_ges, Kweli)
        parser.setEntityResolver(self.TestEntityResolver())
        result = BytesIO()
        parser.setContentHandler(XMLGenerator(result))

        parser.feed('<!DOCTYPE doc [\n')
        parser.feed('  <!ENTITY test SYSTEM "whatever">\n')
        parser.feed(']>\n')
        parser.feed('<doc>&test;</doc>')
        parser.close()

        self.assertEqual(result.getvalue(), start +
                         b"<doc><entity></entity></doc>")

    eleza test_expat_entityresolver_default(self):
        parser = create_parser()
        self.assertEqual(parser.getFeature(feature_external_ges), Uongo)
        parser.setEntityResolver(self.TestEntityResolver())
        result = BytesIO()
        parser.setContentHandler(XMLGenerator(result))

        parser.feed('<!DOCTYPE doc [\n')
        parser.feed('  <!ENTITY test SYSTEM "whatever">\n')
        parser.feed(']>\n')
        parser.feed('<doc>&test;</doc>')
        parser.close()

        self.assertEqual(result.getvalue(), start +
                         b"<doc></doc>")

    # ===== Attributes support

    kundi AttrGatherer(ContentHandler):

        eleza startElement(self, name, attrs):
            self._attrs = attrs

        eleza startElementNS(self, name, qname, attrs):
            self._attrs = attrs

    eleza test_expat_attrs_empty(self):
        parser = create_parser()
        gather = self.AttrGatherer()
        parser.setContentHandler(gather)

        parser.feed("<doc/>")
        parser.close()

        self.verify_empty_attrs(gather._attrs)

    eleza test_expat_attrs_wattr(self):
        parser = create_parser()
        gather = self.AttrGatherer()
        parser.setContentHandler(gather)

        parser.feed("<doc attr='val'/>")
        parser.close()

        self.verify_attrs_wattr(gather._attrs)

    eleza test_expat_nsattrs_empty(self):
        parser = create_parser(1)
        gather = self.AttrGatherer()
        parser.setContentHandler(gather)

        parser.feed("<doc/>")
        parser.close()

        self.verify_empty_nsattrs(gather._attrs)

    eleza test_expat_nsattrs_wattr(self):
        parser = create_parser(1)
        gather = self.AttrGatherer()
        parser.setContentHandler(gather)

        parser.feed("<doc xmlns:ns='%s' ns:attr='val'/>" % ns_uri)
        parser.close()

        attrs = gather._attrs

        self.assertEqual(attrs.getLength(), 1)
        self.assertEqual(attrs.getNames(), [(ns_uri, "attr")])
        self.assertKweli((attrs.getQNames() == [] or
                         attrs.getQNames() == ["ns:attr"]))
        self.assertEqual(len(attrs), 1)
        self.assertIn((ns_uri, "attr"), attrs)
        self.assertEqual(attrs.get((ns_uri, "attr")), "val")
        self.assertEqual(attrs.get((ns_uri, "attr"), 25), "val")
        self.assertEqual(list(attrs.items()), [((ns_uri, "attr"), "val")])
        self.assertEqual(list(attrs.values()), ["val"])
        self.assertEqual(attrs.getValue((ns_uri, "attr")), "val")
        self.assertEqual(attrs[(ns_uri, "attr")], "val")

    # ===== InputSource support

    eleza test_expat_inpsource_filename(self):
        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        parser.parse(TEST_XMLFILE)

        self.assertEqual(result.getvalue(), xml_test_out)

    eleza test_expat_inpsource_sysid(self):
        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        parser.parse(InputSource(TEST_XMLFILE))

        self.assertEqual(result.getvalue(), xml_test_out)

    @requires_nonascii_filenames
    eleza test_expat_inpsource_sysid_nonascii(self):
        fname = support.TESTFN_UNICODE
        shutil.copyfile(TEST_XMLFILE, fname)
        self.addCleanup(support.unlink, fname)

        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        parser.parse(InputSource(fname))

        self.assertEqual(result.getvalue(), xml_test_out)

    eleza test_expat_inpsource_byte_stream(self):
        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        inpsrc = InputSource()
        ukijumuisha open(TEST_XMLFILE, 'rb') kama f:
            inpsrc.setByteStream(f)
            parser.parse(inpsrc)

        self.assertEqual(result.getvalue(), xml_test_out)

    eleza test_expat_inpsource_character_stream(self):
        parser = create_parser()
        result = BytesIO()
        xmlgen = XMLGenerator(result)

        parser.setContentHandler(xmlgen)
        inpsrc = InputSource()
        ukijumuisha open(TEST_XMLFILE, 'rt', encoding='iso-8859-1') kama f:
            inpsrc.setCharacterStream(f)
            parser.parse(inpsrc)

        self.assertEqual(result.getvalue(), xml_test_out)

    # ===== IncrementalParser support

    eleza test_expat_incremental(self):
        result = BytesIO()
        xmlgen = XMLGenerator(result)
        parser = create_parser()
        parser.setContentHandler(xmlgen)

        parser.feed("<doc>")
        parser.feed("</doc>")
        parser.close()

        self.assertEqual(result.getvalue(), start + b"<doc></doc>")

    eleza test_expat_incremental_reset(self):
        result = BytesIO()
        xmlgen = XMLGenerator(result)
        parser = create_parser()
        parser.setContentHandler(xmlgen)

        parser.feed("<doc>")
        parser.feed("text")

        result = BytesIO()
        xmlgen = XMLGenerator(result)
        parser.setContentHandler(xmlgen)
        parser.reset()

        parser.feed("<doc>")
        parser.feed("text")
        parser.feed("</doc>")
        parser.close()

        self.assertEqual(result.getvalue(), start + b"<doc>text</doc>")

    # ===== Locator support

    eleza test_expat_locator_noinfo(self):
        result = BytesIO()
        xmlgen = XMLGenerator(result)
        parser = create_parser()
        parser.setContentHandler(xmlgen)

        parser.feed("<doc>")
        parser.feed("</doc>")
        parser.close()

        self.assertEqual(parser.getSystemId(), Tupu)
        self.assertEqual(parser.getPublicId(), Tupu)
        self.assertEqual(parser.getLineNumber(), 1)

    eleza test_expat_locator_withinfo(self):
        result = BytesIO()
        xmlgen = XMLGenerator(result)
        parser = create_parser()
        parser.setContentHandler(xmlgen)
        parser.parse(TEST_XMLFILE)

        self.assertEqual(parser.getSystemId(), TEST_XMLFILE)
        self.assertEqual(parser.getPublicId(), Tupu)

    @requires_nonascii_filenames
    eleza test_expat_locator_withinfo_nonascii(self):
        fname = support.TESTFN_UNICODE
        shutil.copyfile(TEST_XMLFILE, fname)
        self.addCleanup(support.unlink, fname)

        result = BytesIO()
        xmlgen = XMLGenerator(result)
        parser = create_parser()
        parser.setContentHandler(xmlgen)
        parser.parse(fname)

        self.assertEqual(parser.getSystemId(), fname)
        self.assertEqual(parser.getPublicId(), Tupu)


# ===========================================================================
#
#   error reporting
#
# ===========================================================================

kundi ErrorReportingTest(unittest.TestCase):
    eleza test_expat_inpsource_location(self):
        parser = create_parser()
        parser.setContentHandler(ContentHandler()) # do nothing
        source = InputSource()
        source.setByteStream(BytesIO(b"<foo bar foobar>"))   #ill-formed
        name = "a file name"
        source.setSystemId(name)
        jaribu:
            parser.parse(source)
            self.fail()
        tatizo SAXException kama e:
            self.assertEqual(e.getSystemId(), name)

    eleza test_expat_incomplete(self):
        parser = create_parser()
        parser.setContentHandler(ContentHandler()) # do nothing
        self.assertRaises(SAXParseException, parser.parse, StringIO("<foo>"))
        self.assertEqual(parser.getColumnNumber(), 5)
        self.assertEqual(parser.getLineNumber(), 1)

    eleza test_sax_parse_exception_str(self):
        # pita various values kutoka a locator to the SAXParseException to
        # make sure that the __str__() doesn't fall apart when Tupu is
        # pitaed instead of an integer line na column number
        #
        # use "normal" values kila the locator:
        str(SAXParseException("message", Tupu,
                              self.DummyLocator(1, 1)))
        # use Tupu kila the line number:
        str(SAXParseException("message", Tupu,
                              self.DummyLocator(Tupu, 1)))
        # use Tupu kila the column number:
        str(SAXParseException("message", Tupu,
                              self.DummyLocator(1, Tupu)))
        # use Tupu kila both:
        str(SAXParseException("message", Tupu,
                              self.DummyLocator(Tupu, Tupu)))

    kundi DummyLocator:
        eleza __init__(self, lineno, colno):
            self._lineno = lineno
            self._colno = colno

        eleza getPublicId(self):
            rudisha "pubid"

        eleza getSystemId(self):
            rudisha "sysid"

        eleza getLineNumber(self):
            rudisha self._lineno

        eleza getColumnNumber(self):
            rudisha self._colno

# ===========================================================================
#
#   xmlreader tests
#
# ===========================================================================

kundi XmlReaderTest(XmlTestBase):

    # ===== AttributesImpl
    eleza test_attrs_empty(self):
        self.verify_empty_attrs(AttributesImpl({}))

    eleza test_attrs_wattr(self):
        self.verify_attrs_wattr(AttributesImpl({"attr" : "val"}))

    eleza test_nsattrs_empty(self):
        self.verify_empty_nsattrs(AttributesNSImpl({}, {}))

    eleza test_nsattrs_wattr(self):
        attrs = AttributesNSImpl({(ns_uri, "attr") : "val"},
                                 {(ns_uri, "attr") : "ns:attr"})

        self.assertEqual(attrs.getLength(), 1)
        self.assertEqual(attrs.getNames(), [(ns_uri, "attr")])
        self.assertEqual(attrs.getQNames(), ["ns:attr"])
        self.assertEqual(len(attrs), 1)
        self.assertIn((ns_uri, "attr"), attrs)
        self.assertEqual(list(attrs.keys()), [(ns_uri, "attr")])
        self.assertEqual(attrs.get((ns_uri, "attr")), "val")
        self.assertEqual(attrs.get((ns_uri, "attr"), 25), "val")
        self.assertEqual(list(attrs.items()), [((ns_uri, "attr"), "val")])
        self.assertEqual(list(attrs.values()), ["val"])
        self.assertEqual(attrs.getValue((ns_uri, "attr")), "val")
        self.assertEqual(attrs.getValueByQName("ns:attr"), "val")
        self.assertEqual(attrs.getNameByQName("ns:attr"), (ns_uri, "attr"))
        self.assertEqual(attrs[(ns_uri, "attr")], "val")
        self.assertEqual(attrs.getQNameByName((ns_uri, "attr")), "ns:attr")


eleza test_main():
    run_unittest(MakeParserTest,
                 ParseTest,
                 SaxutilsTest,
                 PrepareInputSourceTest,
                 StringXmlgenTest,
                 BytesXmlgenTest,
                 WriterXmlgenTest,
                 StreamWriterXmlgenTest,
                 StreamReaderWriterXmlgenTest,
                 ExpatReaderTest,
                 ErrorReportingTest,
                 XmlReaderTest)

ikiwa __name__ == "__main__":
    test_main()
