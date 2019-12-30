# XXX TypeErrors on calling handlers, ama on bad rudisha values kutoka a
# handler, are obscure na unhelpful.

kutoka io agiza BytesIO
agiza os
agiza sys
agiza sysconfig
agiza unittest
agiza traceback

kutoka xml.parsers agiza expat
kutoka xml.parsers.expat agiza errors

kutoka test.support agiza sortdict


kundi SetAttributeTest(unittest.TestCase):
    eleza setUp(self):
        self.parser = expat.ParserCreate(namespace_separator='!')

    eleza test_buffer_text(self):
        self.assertIs(self.parser.buffer_text, Uongo)
        kila x kwenye 0, 1, 2, 0:
            self.parser.buffer_text = x
            self.assertIs(self.parser.buffer_text, bool(x))

    eleza test_namespace_prefixes(self):
        self.assertIs(self.parser.namespace_prefixes, Uongo)
        kila x kwenye 0, 1, 2, 0:
            self.parser.namespace_prefixes = x
            self.assertIs(self.parser.namespace_prefixes, bool(x))

    eleza test_ordered_attributes(self):
        self.assertIs(self.parser.ordered_attributes, Uongo)
        kila x kwenye 0, 1, 2, 0:
            self.parser.ordered_attributes = x
            self.assertIs(self.parser.ordered_attributes, bool(x))

    eleza test_specified_attributes(self):
        self.assertIs(self.parser.specified_attributes, Uongo)
        kila x kwenye 0, 1, 2, 0:
            self.parser.specified_attributes = x
            self.assertIs(self.parser.specified_attributes, bool(x))

    eleza test_invalid_attributes(self):
        ukijumuisha self.assertRaises(AttributeError):
            self.parser.returns_unicode = 1
        ukijumuisha self.assertRaises(AttributeError):
            self.parser.returns_unicode

        # Issue #25019
        self.assertRaises(TypeError, setattr, self.parser, range(0xF), 0)
        self.assertRaises(TypeError, self.parser.__setattr__, range(0xF), 0)
        self.assertRaises(TypeError, getattr, self.parser, range(0xF))


data = b'''\
<?xml version="1.0" encoding="iso-8859-1" standalone="no"?>
<?xml-stylesheet href="stylesheet.css"?>
<!-- comment data -->
<!DOCTYPE quotations SYSTEM "quotations.dtd" [
<!ELEMENT root ANY>
<!ATTLIST root attr1 CDATA #REQUIRED attr2 CDATA #IMPLIED>
<!NOTATION notation SYSTEM "notation.jpeg">
<!ENTITY acirc "&#226;">
<!ENTITY external_entity SYSTEM "entity.file">
<!ENTITY unparsed_entity SYSTEM "entity.file" NDATA notation>
%unparsed_entity;
]>

<root attr1="value1" attr2="value2&#8000;">
<myns:subelement xmlns:myns="http://www.python.org/namespace">
     Contents of subelements
</myns:subelement>
<sub2><![CDATA[contents of CDATA section]]></sub2>
&external_entity;
&skipped_entity;
\xb5
</root>
'''


# Produce UTF-8 output
kundi ParseTest(unittest.TestCase):
    kundi Outputter:
        eleza __init__(self):
            self.out = []

        eleza StartElementHandler(self, name, attrs):
            self.out.append('Start element: ' + repr(name) + ' ' +
                            sortdict(attrs))

        eleza EndElementHandler(self, name):
            self.out.append('End element: ' + repr(name))

        eleza CharacterDataHandler(self, data):
            data = data.strip()
            ikiwa data:
                self.out.append('Character data: ' + repr(data))

        eleza ProcessingInstructionHandler(self, target, data):
            self.out.append('PI: ' + repr(target) + ' ' + repr(data))

        eleza StartNamespaceDeclHandler(self, prefix, uri):
            self.out.append('NS decl: ' + repr(prefix) + ' ' + repr(uri))

        eleza EndNamespaceDeclHandler(self, prefix):
            self.out.append('End of NS decl: ' + repr(prefix))

        eleza StartCdataSectionHandler(self):
            self.out.append('Start of CDATA section')

        eleza EndCdataSectionHandler(self):
            self.out.append('End of CDATA section')

        eleza CommentHandler(self, text):
            self.out.append('Comment: ' + repr(text))

        eleza NotationDeclHandler(self, *args):
            name, base, sysid, pubid = args
            self.out.append('Notation declared: %s' %(args,))

        eleza UnparsedEntityDeclHandler(self, *args):
            entityName, base, systemId, publicId, notationName = args
            self.out.append('Unparsed entity decl: %s' %(args,))

        eleza NotStandaloneHandler(self):
            self.out.append('Not standalone')
            rudisha 1

        eleza ExternalEntityRefHandler(self, *args):
            context, base, sysId, pubId = args
            self.out.append('External entity ref: %s' %(args[1:],))
            rudisha 1

        eleza StartDoctypeDeclHandler(self, *args):
            self.out.append(('Start doctype', args))
            rudisha 1

        eleza EndDoctypeDeclHandler(self):
            self.out.append("End doctype")
            rudisha 1

        eleza EntityDeclHandler(self, *args):
            self.out.append(('Entity declaration', args))
            rudisha 1

        eleza XmlDeclHandler(self, *args):
            self.out.append(('XML declaration', args))
            rudisha 1

        eleza ElementDeclHandler(self, *args):
            self.out.append(('Element declaration', args))
            rudisha 1

        eleza AttlistDeclHandler(self, *args):
            self.out.append(('Attribute list declaration', args))
            rudisha 1

        eleza SkippedEntityHandler(self, *args):
            self.out.append(("Skipped entity", args))
            rudisha 1

        eleza DefaultHandler(self, userData):
            pita

        eleza DefaultHandlerExpand(self, userData):
            pita

    handler_names = [
        'StartElementHandler', 'EndElementHandler', 'CharacterDataHandler',
        'ProcessingInstructionHandler', 'UnparsedEntityDeclHandler',
        'NotationDeclHandler', 'StartNamespaceDeclHandler',
        'EndNamespaceDeclHandler', 'CommentHandler',
        'StartCdataSectionHandler', 'EndCdataSectionHandler', 'DefaultHandler',
        'DefaultHandlerExpand', 'NotStandaloneHandler',
        'ExternalEntityRefHandler', 'StartDoctypeDeclHandler',
        'EndDoctypeDeclHandler', 'EntityDeclHandler', 'XmlDeclHandler',
        'ElementDeclHandler', 'AttlistDeclHandler', 'SkippedEntityHandler',
        ]

    eleza _hookup_callbacks(self, parser, handler):
        """
        Set each of the callbacks defined on handler na named in
        self.handler_names on the given parser.
        """
        kila name kwenye self.handler_names:
            setattr(parser, name, getattr(handler, name))

    eleza _verify_parse_output(self, operations):
        expected_operations = [
            ('XML declaration', ('1.0', 'iso-8859-1', 0)),
            'PI: \'xml-stylesheet\' \'href="stylesheet.css"\'',
            "Comment: ' comment data '",
            "Not standalone",
            ("Start doctype", ('quotations', 'quotations.dtd', Tupu, 1)),
            ('Element declaration', ('root', (2, 0, Tupu, ()))),
            ('Attribute list declaration', ('root', 'attr1', 'CDATA', Tupu,
                1)),
            ('Attribute list declaration', ('root', 'attr2', 'CDATA', Tupu,
                0)),
            "Notation declared: ('notation', Tupu, 'notation.jpeg', Tupu)",
            ('Entity declaration', ('acirc', 0, '\xe2', Tupu, Tupu, Tupu, Tupu)),
            ('Entity declaration', ('external_entity', 0, Tupu, Tupu,
                'entity.file', Tupu, Tupu)),
            "Unparsed entity decl: ('unparsed_entity', Tupu, 'entity.file', Tupu, 'notation')",
            "Not standalone",
            "End doctype",
            "Start element: 'root' {'attr1': 'value1', 'attr2': 'value2\u1f40'}",
            "NS decl: 'myns' 'http://www.python.org/namespace'",
            "Start element: 'http://www.python.org/namespace!subelement' {}",
            "Character data: 'Contents of subelements'",
            "End element: 'http://www.python.org/namespace!subelement'",
            "End of NS decl: 'myns'",
            "Start element: 'sub2' {}",
            'Start of CDATA section',
            "Character data: 'contents of CDATA section'",
            'End of CDATA section',
            "End element: 'sub2'",
            "External entity ref: (Tupu, 'entity.file', Tupu)",
            ('Skipped entity', ('skipped_entity', 0)),
            "Character data: '\xb5'",
            "End element: 'root'",
        ]
        kila operation, expected_operation kwenye zip(operations, expected_operations):
            self.assertEqual(operation, expected_operation)

    eleza test_parse_bytes(self):
        out = self.Outputter()
        parser = expat.ParserCreate(namespace_separator='!')
        self._hookup_callbacks(parser, out)

        parser.Parse(data, 1)

        operations = out.out
        self._verify_parse_output(operations)
        # Issue #6697.
        self.assertRaises(AttributeError, getattr, parser, '\uD800')

    eleza test_parse_str(self):
        out = self.Outputter()
        parser = expat.ParserCreate(namespace_separator='!')
        self._hookup_callbacks(parser, out)

        parser.Parse(data.decode('iso-8859-1'), 1)

        operations = out.out
        self._verify_parse_output(operations)

    eleza test_parse_file(self):
        # Try parsing a file
        out = self.Outputter()
        parser = expat.ParserCreate(namespace_separator='!')
        self._hookup_callbacks(parser, out)
        file = BytesIO(data)

        parser.ParseFile(file)

        operations = out.out
        self._verify_parse_output(operations)

    eleza test_parse_again(self):
        parser = expat.ParserCreate()
        file = BytesIO(data)
        parser.ParseFile(file)
        # Issue 6676: ensure a meaningful exception ni raised when attempting
        # to parse more than one XML document per xmlparser instance,
        # a limitation of the Expat library.
        ukijumuisha self.assertRaises(expat.error) kama cm:
            parser.ParseFile(file)
        self.assertEqual(expat.ErrorString(cm.exception.code),
                          expat.errors.XML_ERROR_FINISHED)

kundi NamespaceSeparatorTest(unittest.TestCase):
    eleza test_legal(self):
        # Tests that make sure we get errors when the namespace_separator value
        # ni illegal, na that we don't kila good values:
        expat.ParserCreate()
        expat.ParserCreate(namespace_separator=Tupu)
        expat.ParserCreate(namespace_separator=' ')

    eleza test_illegal(self):
        jaribu:
            expat.ParserCreate(namespace_separator=42)
            self.fail()
        tatizo TypeError kama e:
            self.assertEqual(str(e),
                "ParserCreate() argument 'namespace_separator' must be str ama Tupu, sio int")

        jaribu:
            expat.ParserCreate(namespace_separator='too long')
            self.fail()
        tatizo ValueError kama e:
            self.assertEqual(str(e),
                'namespace_separator must be at most one character, omitted, ama Tupu')

    eleza test_zero_length(self):
        # ParserCreate() needs to accept a namespace_separator of zero length
        # to satisfy the requirements of RDF applications that are required
        # to simply glue together the namespace URI na the localname.  Though
        # considered a wart of the RDF specifications, it needs to be supported.
        #
        # See XML-SIG mailing list thread starting with
        # http://mail.python.org/pipermail/xml-sig/2001-April/005202.html
        #
        expat.ParserCreate(namespace_separator='') # too short


kundi InterningTest(unittest.TestCase):
    eleza test(self):
        # Test the interning machinery.
        p = expat.ParserCreate()
        L = []
        eleza collector(name, *args):
            L.append(name)
        p.StartElementHandler = collector
        p.EndElementHandler = collector
        p.Parse(b"<e> <e/> <e></e> </e>", 1)
        tag = L[0]
        self.assertEqual(len(L), 6)
        kila entry kwenye L:
            # L should have the same string repeated over na over.
            self.assertKweli(tag ni entry)

    eleza test_issue9402(self):
        # create an ExternalEntityParserCreate ukijumuisha buffer text
        kundi ExternalOutputter:
            eleza __init__(self, parser):
                self.parser = parser
                self.parser_result = Tupu

            eleza ExternalEntityRefHandler(self, context, base, sysId, pubId):
                external_parser = self.parser.ExternalEntityParserCreate("")
                self.parser_result = external_parser.Parse(b"", 1)
                rudisha 1

        parser = expat.ParserCreate(namespace_separator='!')
        parser.buffer_text = 1
        out = ExternalOutputter(parser)
        parser.ExternalEntityRefHandler = out.ExternalEntityRefHandler
        parser.Parse(data, 1)
        self.assertEqual(out.parser_result, 1)


kundi BufferTextTest(unittest.TestCase):
    eleza setUp(self):
        self.stuff = []
        self.parser = expat.ParserCreate()
        self.parser.buffer_text = 1
        self.parser.CharacterDataHandler = self.CharacterDataHandler

    eleza check(self, expected, label):
        self.assertEqual(self.stuff, expected,
                "%s\nstuff    = %r\nexpected = %r"
                % (label, self.stuff, map(str, expected)))

    eleza CharacterDataHandler(self, text):
        self.stuff.append(text)

    eleza StartElementHandler(self, name, attrs):
        self.stuff.append("<%s>" % name)
        bt = attrs.get("buffer-text")
        ikiwa bt == "yes":
            self.parser.buffer_text = 1
        lasivyo bt == "no":
            self.parser.buffer_text = 0

    eleza EndElementHandler(self, name):
        self.stuff.append("</%s>" % name)

    eleza CommentHandler(self, data):
        self.stuff.append("<!--%s-->" % data)

    eleza setHandlers(self, handlers=[]):
        kila name kwenye handlers:
            setattr(self.parser, name, getattr(self, name))

    eleza test_default_to_disabled(self):
        parser = expat.ParserCreate()
        self.assertUongo(parser.buffer_text)

    eleza test_buffering_enabled(self):
        # Make sure buffering ni turned on
        self.assertKweli(self.parser.buffer_text)
        self.parser.Parse(b"<a>1<b/>2<c/>3</a>", 1)
        self.assertEqual(self.stuff, ['123'],
                         "buffered text sio properly collapsed")

    eleza test1(self):
        # XXX This test exposes more detail of Expat's text chunking than we
        # XXX like, but it tests what we need to concisely.
        self.setHandlers(["StartElementHandler"])
        self.parser.Parse(b"<a>1<b buffer-text='no'/>2\n3<c buffer-text='yes'/>4\n5</a>", 1)
        self.assertEqual(self.stuff,
                         ["<a>", "1", "<b>", "2", "\n", "3", "<c>", "4\n5"],
                         "buffering control sio reacting kama expected")

    eleza test2(self):
        self.parser.Parse(b"<a>1<b/>&lt;2&gt;<c/>&#32;\n&#x20;3</a>", 1)
        self.assertEqual(self.stuff, ["1<2> \n 3"],
                         "buffered text sio properly collapsed")

    eleza test3(self):
        self.setHandlers(["StartElementHandler"])
        self.parser.Parse(b"<a>1<b/>2<c/>3</a>", 1)
        self.assertEqual(self.stuff, ["<a>", "1", "<b>", "2", "<c>", "3"],
                         "buffered text sio properly split")

    eleza test4(self):
        self.setHandlers(["StartElementHandler", "EndElementHandler"])
        self.parser.CharacterDataHandler = Tupu
        self.parser.Parse(b"<a>1<b/>2<c/>3</a>", 1)
        self.assertEqual(self.stuff,
                         ["<a>", "<b>", "</b>", "<c>", "</c>", "</a>"])

    eleza test5(self):
        self.setHandlers(["StartElementHandler", "EndElementHandler"])
        self.parser.Parse(b"<a>1<b></b>2<c/>3</a>", 1)
        self.assertEqual(self.stuff,
            ["<a>", "1", "<b>", "</b>", "2", "<c>", "</c>", "3", "</a>"])

    eleza test6(self):
        self.setHandlers(["CommentHandler", "EndElementHandler",
                    "StartElementHandler"])
        self.parser.Parse(b"<a>1<b/>2<c></c>345</a> ", 1)
        self.assertEqual(self.stuff,
            ["<a>", "1", "<b>", "</b>", "2", "<c>", "</c>", "345", "</a>"],
            "buffered text sio properly split")

    eleza test7(self):
        self.setHandlers(["CommentHandler", "EndElementHandler",
                    "StartElementHandler"])
        self.parser.Parse(b"<a>1<b/>2<c></c>3<!--abc-->4<!--def-->5</a> ", 1)
        self.assertEqual(self.stuff,
                         ["<a>", "1", "<b>", "</b>", "2", "<c>", "</c>", "3",
                          "<!--abc-->", "4", "<!--def-->", "5", "</a>"],
                         "buffered text sio properly split")


# Test handling of exception kutoka callback:
kundi HandlerExceptionTest(unittest.TestCase):
    eleza StartElementHandler(self, name, attrs):
        ashiria RuntimeError(name)

    eleza check_traceback_entry(self, entry, filename, funcname):
        self.assertEqual(os.path.basename(entry[0]), filename)
        self.assertEqual(entry[2], funcname)

    eleza test_exception(self):
        parser = expat.ParserCreate()
        parser.StartElementHandler = self.StartElementHandler
        jaribu:
            parser.Parse(b"<a><b><c/></b></a>", 1)
            self.fail()
        tatizo RuntimeError kama e:
            self.assertEqual(e.args[0], 'a',
                             "Expected RuntimeError kila element 'a', but" + \
                             " found %r" % e.args[0])
            # Check that the traceback contains the relevant line kwenye pyexpat.c
            entries = traceback.extract_tb(e.__traceback__)
            self.assertEqual(len(entries), 3)
            self.check_traceback_entry(entries[0],
                                       "test_pyexpat.py", "test_exception")
            self.check_traceback_entry(entries[1],
                                       "pyexpat.c", "StartElement")
            self.check_traceback_entry(entries[2],
                                       "test_pyexpat.py", "StartElementHandler")
            ikiwa sysconfig.is_python_build():
                self.assertIn('call_with_frame("StartElement"', entries[1][3])


# Test Current* members:
kundi PositionTest(unittest.TestCase):
    eleza StartElementHandler(self, name, attrs):
        self.check_pos('s')

    eleza EndElementHandler(self, name):
        self.check_pos('e')

    eleza check_pos(self, event):
        pos = (event,
               self.parser.CurrentByteIndex,
               self.parser.CurrentLineNumber,
               self.parser.CurrentColumnNumber)
        self.assertKweli(self.upto < len(self.expected_list),
                        'too many parser events')
        expected = self.expected_list[self.upto]
        self.assertEqual(pos, expected,
                'Expected position %s, got position %s' %(pos, expected))
        self.upto += 1

    eleza test(self):
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.StartElementHandler
        self.parser.EndElementHandler = self.EndElementHandler
        self.upto = 0
        self.expected_list = [('s', 0, 1, 0), ('s', 5, 2, 1), ('s', 11, 3, 2),
                              ('e', 15, 3, 6), ('e', 17, 4, 1), ('e', 22, 5, 0)]

        xml = b'<a>\n <b>\n  <c/>\n </b>\n</a>'
        self.parser.Parse(xml, 1)


kundi sf1296433Test(unittest.TestCase):
    eleza test_parse_only_xml_data(self):
        # http://python.org/sf/1296433
        #
        xml = "<?xml version='1.0' encoding='iso8859'?><s>%s</s>" % ('a' * 1025)
        # this one doesn't crash
        #xml = "<?xml version='1.0'?><s>%s</s>" % ('a' * 10000)

        kundi SpecificException(Exception):
            pita

        eleza handler(text):
            ashiria SpecificException

        parser = expat.ParserCreate()
        parser.CharacterDataHandler = handler

        self.assertRaises(Exception, parser.Parse, xml.encode('iso8859'))

kundi ChardataBufferTest(unittest.TestCase):
    """
    test setting of chardata buffer size
    """

    eleza test_1025_bytes(self):
        self.assertEqual(self.small_buffer_test(1025), 2)

    eleza test_1000_bytes(self):
        self.assertEqual(self.small_buffer_test(1000), 1)

    eleza test_wrong_size(self):
        parser = expat.ParserCreate()
        parser.buffer_text = 1
        ukijumuisha self.assertRaises(ValueError):
            parser.buffer_size = -1
        ukijumuisha self.assertRaises(ValueError):
            parser.buffer_size = 0
        ukijumuisha self.assertRaises((ValueError, OverflowError)):
            parser.buffer_size = sys.maxsize + 1
        ukijumuisha self.assertRaises(TypeError):
            parser.buffer_size = 512.0

    eleza test_unchanged_size(self):
        xml1 = b"<?xml version='1.0' encoding='iso8859'?><s>" + b'a' * 512
        xml2 = b'a'*512 + b'</s>'
        parser = expat.ParserCreate()
        parser.CharacterDataHandler = self.counting_handler
        parser.buffer_size = 512
        parser.buffer_text = 1

        # Feed 512 bytes of character data: the handler should be called
        # once.
        self.n = 0
        parser.Parse(xml1)
        self.assertEqual(self.n, 1)

        # Reassign to buffer_size, but assign the same size.
        parser.buffer_size = parser.buffer_size
        self.assertEqual(self.n, 1)

        # Try parsing rest of the document
        parser.Parse(xml2)
        self.assertEqual(self.n, 2)


    eleza test_disabling_buffer(self):
        xml1 = b"<?xml version='1.0' encoding='iso8859'?><a>" + b'a' * 512
        xml2 = b'b' * 1024
        xml3 = b'c' * 1024 + b'</a>';
        parser = expat.ParserCreate()
        parser.CharacterDataHandler = self.counting_handler
        parser.buffer_text = 1
        parser.buffer_size = 1024
        self.assertEqual(parser.buffer_size, 1024)

        # Parse one chunk of XML
        self.n = 0
        parser.Parse(xml1, 0)
        self.assertEqual(parser.buffer_size, 1024)
        self.assertEqual(self.n, 1)

        # Turn off buffering na parse the next chunk.
        parser.buffer_text = 0
        self.assertUongo(parser.buffer_text)
        self.assertEqual(parser.buffer_size, 1024)
        kila i kwenye range(10):
            parser.Parse(xml2, 0)
        self.assertEqual(self.n, 11)

        parser.buffer_text = 1
        self.assertKweli(parser.buffer_text)
        self.assertEqual(parser.buffer_size, 1024)
        parser.Parse(xml3, 1)
        self.assertEqual(self.n, 12)

    eleza counting_handler(self, text):
        self.n += 1

    eleza small_buffer_test(self, buffer_len):
        xml = b"<?xml version='1.0' encoding='iso8859'?><s>" + b'a' * buffer_len + b'</s>'
        parser = expat.ParserCreate()
        parser.CharacterDataHandler = self.counting_handler
        parser.buffer_size = 1024
        parser.buffer_text = 1

        self.n = 0
        parser.Parse(xml)
        rudisha self.n

    eleza test_change_size_1(self):
        xml1 = b"<?xml version='1.0' encoding='iso8859'?><a><s>" + b'a' * 1024
        xml2 = b'aaa</s><s>' + b'a' * 1025 + b'</s></a>'
        parser = expat.ParserCreate()
        parser.CharacterDataHandler = self.counting_handler
        parser.buffer_text = 1
        parser.buffer_size = 1024
        self.assertEqual(parser.buffer_size, 1024)

        self.n = 0
        parser.Parse(xml1, 0)
        parser.buffer_size *= 2
        self.assertEqual(parser.buffer_size, 2048)
        parser.Parse(xml2, 1)
        self.assertEqual(self.n, 2)

    eleza test_change_size_2(self):
        xml1 = b"<?xml version='1.0' encoding='iso8859'?><a>a<s>" + b'a' * 1023
        xml2 = b'aaa</s><s>' + b'a' * 1025 + b'</s></a>'
        parser = expat.ParserCreate()
        parser.CharacterDataHandler = self.counting_handler
        parser.buffer_text = 1
        parser.buffer_size = 2048
        self.assertEqual(parser.buffer_size, 2048)

        self.n=0
        parser.Parse(xml1, 0)
        parser.buffer_size = parser.buffer_size // 2
        self.assertEqual(parser.buffer_size, 1024)
        parser.Parse(xml2, 1)
        self.assertEqual(self.n, 4)

kundi MalformedInputTest(unittest.TestCase):
    eleza test1(self):
        xml = b"\0\r\n"
        parser = expat.ParserCreate()
        jaribu:
            parser.Parse(xml, Kweli)
            self.fail()
        tatizo expat.ExpatError kama e:
            self.assertEqual(str(e), 'unclosed token: line 2, column 0')

    eleza test2(self):
        # \xc2\x85 ni UTF-8 encoded U+0085 (NEXT LINE)
        xml = b"<?xml version\xc2\x85='1.0'?>\r\n"
        parser = expat.ParserCreate()
        err_pattern = r'XML declaration sio well-formed: line 1, column \d+'
        ukijumuisha self.assertRaisesRegex(expat.ExpatError, err_pattern):
            parser.Parse(xml, Kweli)

kundi ErrorMessageTest(unittest.TestCase):
    eleza test_codes(self):
        # verify mapping of errors.codes na errors.messages
        self.assertEqual(errors.XML_ERROR_SYNTAX,
                         errors.messages[errors.codes[errors.XML_ERROR_SYNTAX]])

    eleza test_expaterror(self):
        xml = b'<'
        parser = expat.ParserCreate()
        jaribu:
            parser.Parse(xml, Kweli)
            self.fail()
        tatizo expat.ExpatError kama e:
            self.assertEqual(e.code,
                             errors.codes[errors.XML_ERROR_UNCLOSED_TOKEN])


kundi ForeignDTDTests(unittest.TestCase):
    """
    Tests kila the UseForeignDTD method of expat parser objects.
    """
    eleza test_use_foreign_dtd(self):
        """
        If UseForeignDTD ni pitaed Kweli na a document without an external
        entity reference ni parsed, ExternalEntityRefHandler ni first called
        ukijumuisha Tupu kila the public na system ids.
        """
        handler_call_args = []
        eleza resolve_entity(context, base, system_id, public_id):
            handler_call_args.append((public_id, system_id))
            rudisha 1

        parser = expat.ParserCreate()
        parser.UseForeignDTD(Kweli)
        parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_ALWAYS)
        parser.ExternalEntityRefHandler = resolve_entity
        parser.Parse(b"<?xml version='1.0'?><element/>")
        self.assertEqual(handler_call_args, [(Tupu, Tupu)])

        # test UseForeignDTD() ni equal to UseForeignDTD(Kweli)
        handler_call_args[:] = []

        parser = expat.ParserCreate()
        parser.UseForeignDTD()
        parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_ALWAYS)
        parser.ExternalEntityRefHandler = resolve_entity
        parser.Parse(b"<?xml version='1.0'?><element/>")
        self.assertEqual(handler_call_args, [(Tupu, Tupu)])

    eleza test_ignore_use_foreign_dtd(self):
        """
        If UseForeignDTD ni pitaed Kweli na a document ukijumuisha an external
        entity reference ni parsed, ExternalEntityRefHandler ni called with
        the public na system ids kutoka the document.
        """
        handler_call_args = []
        eleza resolve_entity(context, base, system_id, public_id):
            handler_call_args.append((public_id, system_id))
            rudisha 1

        parser = expat.ParserCreate()
        parser.UseForeignDTD(Kweli)
        parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_ALWAYS)
        parser.ExternalEntityRefHandler = resolve_entity
        parser.Parse(
            b"<?xml version='1.0'?><!DOCTYPE foo PUBLIC 'bar' 'baz'><element/>")
        self.assertEqual(handler_call_args, [("bar", "baz")])


ikiwa __name__ == "__main__":
    unittest.main()
