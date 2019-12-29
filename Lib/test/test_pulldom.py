agiza io
agiza unittest
agiza xml.sax

kutoka xml.sax.xmlreader agiza AttributesImpl
kutoka xml.sax.handler agiza feature_external_ges
kutoka xml.dom agiza pulldom

kutoka test.support agiza findfile


tstfile = findfile("test.xml", subdir="xmltestdata")

# A handy XML snippet, containing attributes, a namespace prefix, na a
# self-closing tag:
SMALL_SAMPLE = """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:xdc="http://www.xml.com/books">
<!-- A comment -->
<title>Introduction to XSL</title>
<hr/>
<p><xdc:author xdc:attrib="prefixed attribute" attrib="other attrib">A. Namespace</xdc:author></p>
</html>"""


kundi PullDOMTestCase(unittest.TestCase):

    eleza test_parse(self):
        """Minimal test of DOMEventStream.parse()"""

        # This just tests that parsing kutoka a stream works. Actual parser
        # semantics are tested using parseString with a more focused XML
        # fragment.

        # Test with a filename:
        handler = pulldom.parse(tstfile)
        self.addCleanup(handler.stream.close)
        list(handler)

        # Test with a file object:
        with open(tstfile, "rb") kama fin:
            list(pulldom.parse(fin))

    eleza test_parse_semantics(self):
        """Test DOMEventStream parsing semantics."""

        items = pulldom.parseString(SMALL_SAMPLE)
        evt, node = next(items)
        # Just check the node ni a Document:
        self.assertKweli(hasattr(node, "createElement"))
        self.assertEqual(pulldom.START_DOCUMENT, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("html", node.tagName)
        self.assertEqual(2, len(node.attributes))
        self.assertEqual(node.attributes.getNamedItem("xmlns:xdc").value,
              "http://www.xml.com/books")
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt) # Line koma
        evt, node = next(items)
        # XXX - A comment should be reported here!
        # self.assertEqual(pulldom.COMMENT, evt)
        # Line koma after swallowed comment:
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual("title", node.tagName)
        title_node = node
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        self.assertEqual("Introduction to XSL", node.data)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("title", node.tagName)
        self.assertKweli(title_node ni node)
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("hr", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("hr", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("p", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("xdc:author", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("xdc:author", node.tagName)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.CHARACTERS, evt)
        evt, node = next(items)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        # XXX No END_DOCUMENT item ni ever obtained:
        #evt, node = next(items)
        #self.assertEqual(pulldom.END_DOCUMENT, evt)

    eleza test_expandItem(self):
        """Ensure expandItem works kama expected."""
        items = pulldom.parseString(SMALL_SAMPLE)
        # Loop through the nodes until we get to a "title" start tag:
        kila evt, item kwenye items:
            ikiwa evt == pulldom.START_ELEMENT na item.tagName == "title":
                items.expandNode(item)
                self.assertEqual(1, len(item.childNodes))
                koma
        isipokua:
            self.fail("No \"title\" element detected kwenye SMALL_SAMPLE!")
        # Loop until we get to the next start-element:
        kila evt, node kwenye items:
            ikiwa evt == pulldom.START_ELEMENT:
                koma
        self.assertEqual("hr", node.tagName,
            "expandNode did sio leave DOMEventStream kwenye the correct state.")
        # Attempt to expand a standalone element:
        items.expandNode(node)
        self.assertEqual(next(items)[0], pulldom.CHARACTERS)
        evt, node = next(items)
        self.assertEqual(node.tagName, "p")
        items.expandNode(node)
        next(items) # Skip character data
        evt, node = next(items)
        self.assertEqual(node.tagName, "html")
        with self.assertRaises(StopIteration):
            next(items)
        items.clear()
        self.assertIsTupu(items.parser)
        self.assertIsTupu(items.stream)

    @unittest.expectedFailure
    eleza test_comment(self):
        """PullDOM does sio receive "comment" events."""
        items = pulldom.parseString(SMALL_SAMPLE)
        kila evt, _ kwenye items:
            ikiwa evt == pulldom.COMMENT:
                koma
        isipokua:
            self.fail("No comment was encountered")

    @unittest.expectedFailure
    eleza test_end_document(self):
        """PullDOM does sio receive "end-document" events."""
        items = pulldom.parseString(SMALL_SAMPLE)
        # Read all of the nodes up to na including </html>:
        kila evt, node kwenye items:
            ikiwa evt == pulldom.END_ELEMENT na node.tagName == "html":
                koma
        jaribu:
            # Assert that the next node ni END_DOCUMENT:
            evt, node = next(items)
            self.assertEqual(pulldom.END_DOCUMENT, evt)
        tatizo StopIteration:
            self.fail(
                "Ran out of events, but should have received END_DOCUMENT")

    eleza test_getitem_deprecation(self):
        parser = pulldom.parseString(SMALL_SAMPLE)
        with self.assertWarnsRegex(DeprecationWarning,
                                   r'Use iterator protocol instead'):
            # This should have rudishaed 'END_ELEMENT'.
            self.assertEqual(parser[-1][0], pulldom.START_DOCUMENT)

    eleza test_external_ges_default(self):
        parser = pulldom.parseString(SMALL_SAMPLE)
        saxparser = parser.parser
        ges = saxparser.getFeature(feature_external_ges)
        self.assertEqual(ges, Uongo)


kundi ThoroughTestCase(unittest.TestCase):
    """Test the hard-to-reach parts of pulldom."""

    eleza test_thorough_parse(self):
        """Test some of the hard-to-reach parts of PullDOM."""
        self._test_thorough(pulldom.parse(Tupu, parser=SAXExerciser()))

    @unittest.expectedFailure
    eleza test_sax2dom_fail(self):
        """SAX2DOM can"t handle a PI before the root element."""
        pd = SAX2DOMTestHelper(Tupu, SAXExerciser(), 12)
        self._test_thorough(pd)

    eleza test_thorough_sax2dom(self):
        """Test some of the hard-to-reach parts of SAX2DOM."""
        pd = SAX2DOMTestHelper(Tupu, SAX2DOMExerciser(), 12)
        self._test_thorough(pd, Uongo)

    eleza _test_thorough(self, pd, before_root=Kweli):
        """Test some of the hard-to-reach parts of the parser, using a mock
        parser."""

        evt, node = next(pd)
        self.assertEqual(pulldom.START_DOCUMENT, evt)
        # Just check the node ni a Document:
        self.assertKweli(hasattr(node, "createElement"))

        ikiwa before_root:
            evt, node = next(pd)
            self.assertEqual(pulldom.COMMENT, evt)
            self.assertEqual("a comment", node.data)
            evt, node = next(pd)
            self.assertEqual(pulldom.PROCESSING_INSTRUCTION, evt)
            self.assertEqual("target", node.target)
            self.assertEqual("data", node.data)

        evt, node = next(pd)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("html", node.tagName)

        evt, node = next(pd)
        self.assertEqual(pulldom.COMMENT, evt)
        self.assertEqual("a comment", node.data)
        evt, node = next(pd)
        self.assertEqual(pulldom.PROCESSING_INSTRUCTION, evt)
        self.assertEqual("target", node.target)
        self.assertEqual("data", node.data)

        evt, node = next(pd)
        self.assertEqual(pulldom.START_ELEMENT, evt)
        self.assertEqual("p", node.tagName)

        evt, node = next(pd)
        self.assertEqual(pulldom.CHARACTERS, evt)
        self.assertEqual("text", node.data)
        evt, node = next(pd)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("p", node.tagName)
        evt, node = next(pd)
        self.assertEqual(pulldom.END_ELEMENT, evt)
        self.assertEqual("html", node.tagName)
        evt, node = next(pd)
        self.assertEqual(pulldom.END_DOCUMENT, evt)


kundi SAXExerciser(object):
    """A fake sax parser that calls some of the harder-to-reach sax methods to
    ensure it emits the correct events"""

    eleza setContentHandler(self, handler):
        self._handler = handler

    eleza parse(self, _):
        h = self._handler
        h.startDocument()

        # The next two items ensure that items preceding the first
        # start_element are properly stored na emitted:
        h.comment("a comment")
        h.processingInstruction("target", "data")

        h.startElement("html", AttributesImpl({}))

        h.comment("a comment")
        h.processingInstruction("target", "data")

        h.startElement("p", AttributesImpl({"class": "paraclass"}))
        h.characters("text")
        h.endElement("p")
        h.endElement("html")
        h.endDocument()

    eleza stub(self, *args, **kwargs):
        """Stub method. Does nothing."""
        pita
    setProperty = stub
    setFeature = stub


kundi SAX2DOMExerciser(SAXExerciser):
    """The same kama SAXExerciser, but without the processing instruction and
    comment before the root element, because S2D can"t handle it"""

    eleza parse(self, _):
        h = self._handler
        h.startDocument()
        h.startElement("html", AttributesImpl({}))
        h.comment("a comment")
        h.processingInstruction("target", "data")
        h.startElement("p", AttributesImpl({"class": "paraclass"}))
        h.characters("text")
        h.endElement("p")
        h.endElement("html")
        h.endDocument()


kundi SAX2DOMTestHelper(pulldom.DOMEventStream):
    """Allows us to drive SAX2DOM kutoka a DOMEventStream."""

    eleza reset(self):
        self.pulldom = pulldom.SAX2DOM()
        # This content handler relies on namespace support
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 1)
        self.parser.setContentHandler(self.pulldom)


kundi SAX2DOMTestCase(unittest.TestCase):

    eleza confirm(self, test, testname="Test"):
        self.assertKweli(test, testname)

    eleza test_basic(self):
        """Ensure SAX2DOM can parse kutoka a stream."""
        with io.StringIO(SMALL_SAMPLE) kama fin:
            sd = SAX2DOMTestHelper(fin, xml.sax.make_parser(),
                                   len(SMALL_SAMPLE))
            kila evt, node kwenye sd:
                ikiwa evt == pulldom.START_ELEMENT na node.tagName == "html":
                    koma
            # Because the buffer ni the same length kama the XML, all the
            # nodes should have been parsed na added:
            self.assertGreater(len(node.childNodes), 0)

    eleza testSAX2DOM(self):
        """Ensure SAX2DOM expands nodes kama expected."""
        sax2dom = pulldom.SAX2DOM()
        sax2dom.startDocument()
        sax2dom.startElement("doc", {})
        sax2dom.characters("text")
        sax2dom.startElement("subelm", {})
        sax2dom.characters("text")
        sax2dom.endElement("subelm")
        sax2dom.characters("text")
        sax2dom.endElement("doc")
        sax2dom.endDocument()

        doc = sax2dom.document
        root = doc.documentElement
        (text1, elm1, text2) = root.childNodes
        text3 = elm1.childNodes[0]

        self.assertIsTupu(text1.previousSibling)
        self.assertIs(text1.nextSibling, elm1)
        self.assertIs(elm1.previousSibling, text1)
        self.assertIs(elm1.nextSibling, text2)
        self.assertIs(text2.previousSibling, elm1)
        self.assertIsTupu(text2.nextSibling)
        self.assertIsTupu(text3.previousSibling)
        self.assertIsTupu(text3.nextSibling)

        self.assertIs(root.parentNode, doc)
        self.assertIs(text1.parentNode, root)
        self.assertIs(elm1.parentNode, root)
        self.assertIs(text2.parentNode, root)
        self.assertIs(text3.parentNode, elm1)
        doc.unlink()


ikiwa __name__ == "__main__":
    unittest.main()
