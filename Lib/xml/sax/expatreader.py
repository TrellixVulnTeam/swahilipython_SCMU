"""
SAX driver for the pyexpat C module.  This driver works with
pyexpat.__version__ == '2.22'.
"""

version = "0.20"

kutoka xml.sax._exceptions agiza *
kutoka xml.sax.handler agiza feature_validation, feature_namespaces
kutoka xml.sax.handler agiza feature_namespace_prefixes
kutoka xml.sax.handler agiza feature_external_ges, feature_external_pes
kutoka xml.sax.handler agiza feature_string_interning
kutoka xml.sax.handler agiza property_xml_string, property_interning_dict

# xml.parsers.expat does not raise ImportError in Jython
agiza sys
ikiwa sys.platform[:4] == "java":
    raise SAXReaderNotAvailable("expat not available in Java", None)
del sys

try:
    kutoka xml.parsers agiza expat
except ImportError:
    raise SAXReaderNotAvailable("expat not supported", None)
else:
    ikiwa not hasattr(expat, "ParserCreate"):
        raise SAXReaderNotAvailable("expat not supported", None)
kutoka xml.sax agiza xmlreader, saxutils, handler

AttributesImpl = xmlreader.AttributesImpl
AttributesNSImpl = xmlreader.AttributesNSImpl

# If we're using a sufficiently recent version of Python, we can use
# weak references to avoid cycles between the parser and content
# handler, otherwise we'll just have to pretend.
try:
    agiza _weakref
except ImportError:
    eleza _mkproxy(o):
        rudisha o
else:
    agiza weakref
    _mkproxy = weakref.proxy
    del weakref, _weakref

kundi _ClosedParser:
    pass

# --- ExpatLocator

kundi ExpatLocator(xmlreader.Locator):
    """Locator for use with the ExpatParser class.

    This uses a weak reference to the parser object to avoid creating
    a circular reference between the parser and the content handler.
    """
    eleza __init__(self, parser):
        self._ref = _mkproxy(parser)

    eleza getColumnNumber(self):
        parser = self._ref
        ikiwa parser._parser is None:
            rudisha None
        rudisha parser._parser.ErrorColumnNumber

    eleza getLineNumber(self):
        parser = self._ref
        ikiwa parser._parser is None:
            rudisha 1
        rudisha parser._parser.ErrorLineNumber

    eleza getPublicId(self):
        parser = self._ref
        ikiwa parser is None:
            rudisha None
        rudisha parser._source.getPublicId()

    eleza getSystemId(self):
        parser = self._ref
        ikiwa parser is None:
            rudisha None
        rudisha parser._source.getSystemId()


# --- ExpatParser

kundi ExpatParser(xmlreader.IncrementalParser, xmlreader.Locator):
    """SAX driver for the pyexpat C module."""

    eleza __init__(self, namespaceHandling=0, bufsize=2**16-20):
        xmlreader.IncrementalParser.__init__(self, bufsize)
        self._source = xmlreader.InputSource()
        self._parser = None
        self._namespaces = namespaceHandling
        self._lex_handler_prop = None
        self._parsing = 0
        self._entity_stack = []
        self._external_ges = 0
        self._interning = None

    # XMLReader methods

    eleza parse(self, source):
        "Parse an XML document kutoka a URL or an InputSource."
        source = saxutils.prepare_input_source(source)

        self._source = source
        try:
            self.reset()
            self._cont_handler.setDocumentLocator(ExpatLocator(self))
            xmlreader.IncrementalParser.parse(self, source)
        except:
            # bpo-30264: Close the source on error to not leak resources:
            # xml.sax.parse() doesn't give access to the underlying parser
            # to the caller
            self._close_source()
            raise

    eleza prepareParser(self, source):
        ikiwa source.getSystemId() is not None:
            self._parser.SetBase(source.getSystemId())

    # Redefined setContentHandler to allow changing handlers during parsing

    eleza setContentHandler(self, handler):
        xmlreader.IncrementalParser.setContentHandler(self, handler)
        ikiwa self._parsing:
            self._reset_cont_handler()

    eleza getFeature(self, name):
        ikiwa name == feature_namespaces:
            rudisha self._namespaces
        elikiwa name == feature_string_interning:
            rudisha self._interning is not None
        elikiwa name in (feature_validation, feature_external_pes,
                      feature_namespace_prefixes):
            rudisha 0
        elikiwa name == feature_external_ges:
            rudisha self._external_ges
        raise SAXNotRecognizedException("Feature '%s' not recognized" % name)

    eleza setFeature(self, name, state):
        ikiwa self._parsing:
            raise SAXNotSupportedException("Cannot set features while parsing")

        ikiwa name == feature_namespaces:
            self._namespaces = state
        elikiwa name == feature_external_ges:
            self._external_ges = state
        elikiwa name == feature_string_interning:
            ikiwa state:
                ikiwa self._interning is None:
                    self._interning = {}
            else:
                self._interning = None
        elikiwa name == feature_validation:
            ikiwa state:
                raise SAXNotSupportedException(
                    "expat does not support validation")
        elikiwa name == feature_external_pes:
            ikiwa state:
                raise SAXNotSupportedException(
                    "expat does not read external parameter entities")
        elikiwa name == feature_namespace_prefixes:
            ikiwa state:
                raise SAXNotSupportedException(
                    "expat does not report namespace prefixes")
        else:
            raise SAXNotRecognizedException(
                "Feature '%s' not recognized" % name)

    eleza getProperty(self, name):
        ikiwa name == handler.property_lexical_handler:
            rudisha self._lex_handler_prop
        elikiwa name == property_interning_dict:
            rudisha self._interning
        elikiwa name == property_xml_string:
            ikiwa self._parser:
                ikiwa hasattr(self._parser, "GetInputContext"):
                    rudisha self._parser.GetInputContext()
                else:
                    raise SAXNotRecognizedException(
                        "This version of expat does not support getting"
                        " the XML string")
            else:
                raise SAXNotSupportedException(
                    "XML string cannot be returned when not parsing")
        raise SAXNotRecognizedException("Property '%s' not recognized" % name)

    eleza setProperty(self, name, value):
        ikiwa name == handler.property_lexical_handler:
            self._lex_handler_prop = value
            ikiwa self._parsing:
                self._reset_lex_handler_prop()
        elikiwa name == property_interning_dict:
            self._interning = value
        elikiwa name == property_xml_string:
            raise SAXNotSupportedException("Property '%s' cannot be set" %
                                           name)
        else:
            raise SAXNotRecognizedException("Property '%s' not recognized" %
                                            name)

    # IncrementalParser methods

    eleza feed(self, data, isFinal = 0):
        ikiwa not self._parsing:
            self.reset()
            self._parsing = 1
            self._cont_handler.startDocument()

        try:
            # The isFinal parameter is internal to the expat reader.
            # If it is set to true, expat will check validity of the entire
            # document. When feeding chunks, they are not normally final -
            # except when invoked kutoka close.
            self._parser.Parse(data, isFinal)
        except expat.error as e:
            exc = SAXParseException(expat.ErrorString(e.code), e, self)
            # FIXME: when to invoke error()?
            self._err_handler.fatalError(exc)

    eleza _close_source(self):
        source = self._source
        try:
            file = source.getCharacterStream()
            ikiwa file is not None:
                file.close()
        finally:
            file = source.getByteStream()
            ikiwa file is not None:
                file.close()

    eleza close(self):
        ikiwa (self._entity_stack or self._parser is None or
            isinstance(self._parser, _ClosedParser)):
            # If we are completing an external entity, do nothing here
            return
        try:
            self.feed("", isFinal = 1)
            self._cont_handler.endDocument()
            self._parsing = 0
            # break cycle created by expat handlers pointing to our methods
            self._parser = None
        finally:
            self._parsing = 0
            ikiwa self._parser is not None:
                # Keep ErrorColumnNumber and ErrorLineNumber after closing.
                parser = _ClosedParser()
                parser.ErrorColumnNumber = self._parser.ErrorColumnNumber
                parser.ErrorLineNumber = self._parser.ErrorLineNumber
                self._parser = parser
            self._close_source()

    eleza _reset_cont_handler(self):
        self._parser.ProcessingInstructionHandler = \
                                    self._cont_handler.processingInstruction
        self._parser.CharacterDataHandler = self._cont_handler.characters

    eleza _reset_lex_handler_prop(self):
        lex = self._lex_handler_prop
        parser = self._parser
        ikiwa lex is None:
            parser.CommentHandler = None
            parser.StartCdataSectionHandler = None
            parser.EndCdataSectionHandler = None
            parser.StartDoctypeDeclHandler = None
            parser.EndDoctypeDeclHandler = None
        else:
            parser.CommentHandler = lex.comment
            parser.StartCdataSectionHandler = lex.startCDATA
            parser.EndCdataSectionHandler = lex.endCDATA
            parser.StartDoctypeDeclHandler = self.start_doctype_decl
            parser.EndDoctypeDeclHandler = lex.endDTD

    eleza reset(self):
        ikiwa self._namespaces:
            self._parser = expat.ParserCreate(self._source.getEncoding(), " ",
                                              intern=self._interning)
            self._parser.namespace_prefixes = 1
            self._parser.StartElementHandler = self.start_element_ns
            self._parser.EndElementHandler = self.end_element_ns
        else:
            self._parser = expat.ParserCreate(self._source.getEncoding(),
                                              intern = self._interning)
            self._parser.StartElementHandler = self.start_element
            self._parser.EndElementHandler = self.end_element

        self._reset_cont_handler()
        self._parser.UnparsedEntityDeclHandler = self.unparsed_entity_decl
        self._parser.NotationDeclHandler = self.notation_decl
        self._parser.StartNamespaceDeclHandler = self.start_namespace_decl
        self._parser.EndNamespaceDeclHandler = self.end_namespace_decl

        self._decl_handler_prop = None
        ikiwa self._lex_handler_prop:
            self._reset_lex_handler_prop()
#         self._parser.DefaultHandler =
#         self._parser.DefaultHandlerExpand =
#         self._parser.NotStandaloneHandler =
        self._parser.ExternalEntityRefHandler = self.external_entity_ref
        try:
            self._parser.SkippedEntityHandler = self.skipped_entity_handler
        except AttributeError:
            # This pyexpat does not support SkippedEntity
            pass
        self._parser.SetParamEntityParsing(
            expat.XML_PARAM_ENTITY_PARSING_UNLESS_STANDALONE)

        self._parsing = 0
        self._entity_stack = []

    # Locator methods

    eleza getColumnNumber(self):
        ikiwa self._parser is None:
            rudisha None
        rudisha self._parser.ErrorColumnNumber

    eleza getLineNumber(self):
        ikiwa self._parser is None:
            rudisha 1
        rudisha self._parser.ErrorLineNumber

    eleza getPublicId(self):
        rudisha self._source.getPublicId()

    eleza getSystemId(self):
        rudisha self._source.getSystemId()

    # event handlers
    eleza start_element(self, name, attrs):
        self._cont_handler.startElement(name, AttributesImpl(attrs))

    eleza end_element(self, name):
        self._cont_handler.endElement(name)

    eleza start_element_ns(self, name, attrs):
        pair = name.split()
        ikiwa len(pair) == 1:
            # no namespace
            pair = (None, name)
        elikiwa len(pair) == 3:
            pair = pair[0], pair[1]
        else:
            # default namespace
            pair = tuple(pair)

        newattrs = {}
        qnames = {}
        for (aname, value) in attrs.items():
            parts = aname.split()
            length = len(parts)
            ikiwa length == 1:
                # no namespace
                qname = aname
                apair = (None, aname)
            elikiwa length == 3:
                qname = "%s:%s" % (parts[2], parts[1])
                apair = parts[0], parts[1]
            else:
                # default namespace
                qname = parts[1]
                apair = tuple(parts)

            newattrs[apair] = value
            qnames[apair] = qname

        self._cont_handler.startElementNS(pair, None,
                                          AttributesNSImpl(newattrs, qnames))

    eleza end_element_ns(self, name):
        pair = name.split()
        ikiwa len(pair) == 1:
            pair = (None, name)
        elikiwa len(pair) == 3:
            pair = pair[0], pair[1]
        else:
            pair = tuple(pair)

        self._cont_handler.endElementNS(pair, None)

    # this is not used (call directly to ContentHandler)
    eleza processing_instruction(self, target, data):
        self._cont_handler.processingInstruction(target, data)

    # this is not used (call directly to ContentHandler)
    eleza character_data(self, data):
        self._cont_handler.characters(data)

    eleza start_namespace_decl(self, prefix, uri):
        self._cont_handler.startPrefixMapping(prefix, uri)

    eleza end_namespace_decl(self, prefix):
        self._cont_handler.endPrefixMapping(prefix)

    eleza start_doctype_decl(self, name, sysid, pubid, has_internal_subset):
        self._lex_handler_prop.startDTD(name, pubid, sysid)

    eleza unparsed_entity_decl(self, name, base, sysid, pubid, notation_name):
        self._dtd_handler.unparsedEntityDecl(name, pubid, sysid, notation_name)

    eleza notation_decl(self, name, base, sysid, pubid):
        self._dtd_handler.notationDecl(name, pubid, sysid)

    eleza external_entity_ref(self, context, base, sysid, pubid):
        ikiwa not self._external_ges:
            rudisha 1

        source = self._ent_handler.resolveEntity(pubid, sysid)
        source = saxutils.prepare_input_source(source,
                                               self._source.getSystemId() or
                                               "")

        self._entity_stack.append((self._parser, self._source))
        self._parser = self._parser.ExternalEntityParserCreate(context)
        self._source = source

        try:
            xmlreader.IncrementalParser.parse(self, source)
        except:
            rudisha 0  # FIXME: save error info here?

        (self._parser, self._source) = self._entity_stack[-1]
        del self._entity_stack[-1]
        rudisha 1

    eleza skipped_entity_handler(self, name, is_pe):
        ikiwa is_pe:
            # The SAX spec requires to report skipped PEs with a '%'
            name = '%'+name
        self._cont_handler.skippedEntity(name)

# ---

eleza create_parser(*args, **kwargs):
    rudisha ExpatParser(*args, **kwargs)

# ---

ikiwa __name__ == "__main__":
    agiza xml.sax.saxutils
    p = create_parser()
    p.setContentHandler(xml.sax.saxutils.XMLGenerator())
    p.setErrorHandler(xml.sax.ErrorHandler())
    p.parse("http://www.ibiblio.org/xml/examples/shakespeare/hamlet.xml")
