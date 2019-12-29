"""
This module contains the core classes of version 2.0 of SAX kila Python.
This file provides only default classes with absolutely minimum
functionality, kutoka which drivers na applications can be subclassed.

Many of these classes are empty na are included only kama documentation
of the interfaces.

$Id$
"""

version = '2.0beta'

#============================================================================
#
# HANDLER INTERFACES
#
#============================================================================

# ===== ERRORHANDLER =====

kundi ErrorHandler:
    """Basic interface kila SAX error handlers.

    If you create an object that implements this interface, then
    register the object with your XMLReader, the parser will call the
    methods kwenye your object to report all warnings na errors. There
    are three levels of errors available: warnings, (possibly)
    recoverable errors, na unrecoverable errors. All methods take a
    SAXParseException kama the only parameter."""

    eleza error(self, exception):
        "Handle a recoverable error."
        ashiria exception

    eleza fatalError(self, exception):
        "Handle a non-recoverable error."
        ashiria exception

    eleza warning(self, exception):
        "Handle a warning."
        andika(exception)


# ===== CONTENTHANDLER =====

kundi ContentHandler:
    """Interface kila receiving logical document content events.

    This ni the main callback interface kwenye SAX, na the one most
    agizaant to applications. The order of events kwenye this interface
    mirrors the order of the information kwenye the document."""

    eleza __init__(self):
        self._locator = Tupu

    eleza setDocumentLocator(self, locator):
        """Called by the parser to give the application a locator for
        locating the origin of document events.

        SAX parsers are strongly encouraged (though sio absolutely
        required) to supply a locator: ikiwa it does so, it must supply
        the locator to the application by invoking this method before
        invoking any of the other methods kwenye the DocumentHandler
        interface.

        The locator allows the application to determine the end
        position of any document-related event, even ikiwa the parser is
        sio reporting an error. Typically, the application will use
        this information kila reporting its own errors (such as
        character content that does sio match an application's
        business rules). The information rudishaed by the locator is
        probably sio sufficient kila use with a search engine.

        Note that the locator will rudisha correct information only
        during the invocation of the events kwenye this interface. The
        application should sio attempt to use it at any other time."""
        self._locator = locator

    eleza startDocument(self):
        """Receive notification of the beginning of a document.

        The SAX parser will invoke this method only once, before any
        other methods kwenye this interface ama kwenye DTDHandler (tatizo for
        setDocumentLocator)."""

    eleza endDocument(self):
        """Receive notification of the end of a document.

        The SAX parser will invoke this method only once, na it will
        be the last method invoked during the parse. The parser shall
        sio invoke this method until it has either abandoned parsing
        (because of an unrecoverable error) ama reached the end of
        input."""

    eleza startPrefixMapping(self, prefix, uri):
        """Begin the scope of a prefix-URI Namespace mapping.

        The information kutoka this event ni sio necessary kila normal
        Namespace processing: the SAX XML reader will automatically
        replace prefixes kila element na attribute names when the
        http://xml.org/sax/features/namespaces feature ni true (the
        default).

        There are cases, however, when applications need to use
        prefixes kwenye character data ama kwenye attribute values, where they
        cannot safely be expanded automatically; the
        start/endPrefixMapping event supplies the information to the
        application to expand prefixes kwenye those contexts itself, if
        necessary.

        Note that start/endPrefixMapping events are sio guaranteed to
        be properly nested relative to each-other: all
        startPrefixMapping events will occur before the corresponding
        startElement event, na all endPrefixMapping events will occur
        after the corresponding endElement event, but their order is
        sio guaranteed."""

    eleza endPrefixMapping(self, prefix):
        """End the scope of a prefix-URI mapping.

        See startPrefixMapping kila details. This event will always
        occur after the corresponding endElement event, but the order
        of endPrefixMapping events ni sio otherwise guaranteed."""

    eleza startElement(self, name, attrs):
        """Signals the start of an element kwenye non-namespace mode.

        The name parameter contains the raw XML 1.0 name of the
        element type kama a string na the attrs parameter holds an
        instance of the Attributes kundi containing the attributes of
        the element."""

    eleza endElement(self, name):
        """Signals the end of an element kwenye non-namespace mode.

        The name parameter contains the name of the element type, just
        kama with the startElement event."""

    eleza startElementNS(self, name, qname, attrs):
        """Signals the start of an element kwenye namespace mode.

        The name parameter contains the name of the element type kama a
        (uri, localname) tuple, the qname parameter the raw XML 1.0
        name used kwenye the source document, na the attrs parameter
        holds an instance of the Attributes kundi containing the
        attributes of the element.

        The uri part of the name tuple ni Tupu kila elements which have
        no namespace."""

    eleza endElementNS(self, name, qname):
        """Signals the end of an element kwenye namespace mode.

        The name parameter contains the name of the element type, just
        kama with the startElementNS event."""

    eleza characters(self, content):
        """Receive notification of character data.

        The Parser will call this method to report each chunk of
        character data. SAX parsers may rudisha all contiguous
        character data kwenye a single chunk, ama they may split it into
        several chunks; however, all of the characters kwenye any single
        event must come kutoka the same external entity so that the
        Locator provides useful information."""

    eleza ignorableWhitespace(self, whitespace):
        """Receive notification of ignorable whitespace kwenye element content.

        Validating Parsers must use this method to report each chunk
        of ignorable whitespace (see the W3C XML 1.0 recommendation,
        section 2.10): non-validating parsers may also use this method
        ikiwa they are capable of parsing na using content models.

        SAX parsers may rudisha all contiguous whitespace kwenye a single
        chunk, ama they may split it into several chunks; however, all
        of the characters kwenye any single event must come kutoka the same
        external entity, so that the Locator provides useful
        information."""

    eleza processingInstruction(self, target, data):
        """Receive notification of a processing instruction.

        The Parser will invoke this method once kila each processing
        instruction found: note that processing instructions may occur
        before ama after the main document element.

        A SAX parser should never report an XML declaration (XML 1.0,
        section 2.8) ama a text declaration (XML 1.0, section 4.3.1)
        using this method."""

    eleza skippedEntity(self, name):
        """Receive notification of a skipped entity.

        The Parser will invoke this method once kila each entity
        skipped. Non-validating processors may skip entities ikiwa they
        have sio seen the declarations (because, kila example, the
        entity was declared kwenye an external DTD subset). All processors
        may skip external entities, depending on the values of the
        http://xml.org/sax/features/external-general-entities na the
        http://xml.org/sax/features/external-parameter-entities
        properties."""


# ===== DTDHandler =====

kundi DTDHandler:
    """Handle DTD events.

    This interface specifies only those DTD events required kila basic
    parsing (unparsed entities na attributes)."""

    eleza notationDecl(self, name, publicId, systemId):
        "Handle a notation declaration event."

    eleza unparsedEntityDecl(self, name, publicId, systemId, ndata):
        "Handle an unparsed entity declaration event."


# ===== ENTITYRESOLVER =====

kundi EntityResolver:
    """Basic interface kila resolving entities. If you create an object
    implementing this interface, then register the object with your
    Parser, the parser will call the method kwenye your object to
    resolve all external entities. Note that DefaultHandler implements
    this interface with the default behaviour."""

    eleza resolveEntity(self, publicId, systemId):
        """Resolve the system identifier of an entity na rudisha either
        the system identifier to read kutoka kama a string, ama an InputSource
        to read kutoka."""
        rudisha systemId


#============================================================================
#
# CORE FEATURES
#
#============================================================================

feature_namespaces = "http://xml.org/sax/features/namespaces"
# true: Perform Namespace processing (default).
# false: Optionally do sio perform Namespace processing
#        (implies namespace-prefixes).
# access: (parsing) read-only; (not parsing) read/write

feature_namespace_prefixes = "http://xml.org/sax/features/namespace-prefixes"
# true: Report the original prefixed names na attributes used kila Namespace
#       declarations.
# false: Do sio report attributes used kila Namespace declarations, and
#        optionally do sio report original prefixed names (default).
# access: (parsing) read-only; (not parsing) read/write

feature_string_interning = "http://xml.org/sax/features/string-interning"
# true: All element names, prefixes, attribute names, Namespace URIs, and
#       local names are interned using the built-in intern function.
# false: Names are sio necessarily interned, although they may be (default).
# access: (parsing) read-only; (not parsing) read/write

feature_validation = "http://xml.org/sax/features/validation"
# true: Report all validation errors (implies external-general-entities and
#       external-parameter-entities).
# false: Do sio report validation errors.
# access: (parsing) read-only; (not parsing) read/write

feature_external_ges = "http://xml.org/sax/features/external-general-entities"
# true: Include all external general (text) entities.
# false: Do sio include external general entities.
# access: (parsing) read-only; (not parsing) read/write

feature_external_pes = "http://xml.org/sax/features/external-parameter-entities"
# true: Include all external parameter entities, including the external
#       DTD subset.
# false: Do sio include any external parameter entities, even the external
#        DTD subset.
# access: (parsing) read-only; (not parsing) read/write

all_features = [feature_namespaces,
                feature_namespace_prefixes,
                feature_string_interning,
                feature_validation,
                feature_external_ges,
                feature_external_pes]


#============================================================================
#
# CORE PROPERTIES
#
#============================================================================

property_lexical_handler = "http://xml.org/sax/properties/lexical-handler"
# data type: xml.sax.sax2lib.LexicalHandler
# description: An optional extension handler kila lexical events like comments.
# access: read/write

property_declaration_handler = "http://xml.org/sax/properties/declaration-handler"
# data type: xml.sax.sax2lib.DeclHandler
# description: An optional extension handler kila DTD-related events other
#              than notations na unparsed entities.
# access: read/write

property_dom_node = "http://xml.org/sax/properties/dom-node"
# data type: org.w3c.dom.Node
# description: When parsing, the current DOM node being visited ikiwa this is
#              a DOM iterator; when sio parsing, the root DOM node for
#              iteration.
# access: (parsing) read-only; (not parsing) read/write

property_xml_string = "http://xml.org/sax/properties/xml-string"
# data type: String
# description: The literal string of characters that was the source for
#              the current event.
# access: read-only

property_encoding = "http://www.python.org/sax/properties/encoding"
# data type: String
# description: The name of the encoding to assume kila input data.
# access: write: set the encoding, e.g. established by a higher-level
#                protocol. May change during parsing (e.g. after
#                processing a META tag)
#         read:  rudisha the current encoding (possibly established through
#                auto-detection.
# initial value: UTF-8
#

property_interning_dict = "http://www.python.org/sax/properties/interning-dict"
# data type: Dictionary
# description: The dictionary used to intern common strings kwenye the document
# access: write: Request that the parser uses a specific dictionary, to
#                allow interning across different documents
#         read:  rudisha the current interning dictionary, ama Tupu
#

all_properties = [property_lexical_handler,
                  property_dom_node,
                  property_declaration_handler,
                  property_xml_string,
                  property_encoding,
                  property_interning_dict]
