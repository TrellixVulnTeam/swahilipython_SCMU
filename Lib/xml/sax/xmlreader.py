"""An XML Reader ni the SAX 2 name kila an XML parser. XML Parsers
should be based on this code. """

kutoka . agiza handler

kutoka ._exceptions agiza SAXNotSupportedException, SAXNotRecognizedException


# ===== XMLREADER =====

kundi XMLReader:
    """Interface kila reading an XML document using callbacks.

    XMLReader ni the interface that an XML parser's SAX2 driver must
    implement. This interface allows an application to set na query
    features na properties kwenye the parser, to register event handlers
    kila document processing, na to initiate a document parse.

    All SAX interfaces are assumed to be synchronous: the parse
    methods must sio rudisha until parsing ni complete, na readers
    must wait kila an event-handler callback to rudisha before reporting
    the next event."""

    eleza __init__(self):
        self._cont_handler = handler.ContentHandler()
        self._dtd_handler = handler.DTDHandler()
        self._ent_handler = handler.EntityResolver()
        self._err_handler = handler.ErrorHandler()

    eleza parse(self, source):
        "Parse an XML document kutoka a system identifier ama an InputSource."
        ashiria NotImplementedError("This method must be implemented!")

    eleza getContentHandler(self):
        "Returns the current ContentHandler."
        rudisha self._cont_handler

    eleza setContentHandler(self, handler):
        "Registers a new object to receive document content events."
        self._cont_handler = handler

    eleza getDTDHandler(self):
        "Returns the current DTD handler."
        rudisha self._dtd_handler

    eleza setDTDHandler(self, handler):
        "Register an object to receive basic DTD-related events."
        self._dtd_handler = handler

    eleza getEntityResolver(self):
        "Returns the current EntityResolver."
        rudisha self._ent_handler

    eleza setEntityResolver(self, resolver):
        "Register an object to resolve external entities."
        self._ent_handler = resolver

    eleza getErrorHandler(self):
        "Returns the current ErrorHandler."
        rudisha self._err_handler

    eleza setErrorHandler(self, handler):
        "Register an object to receive error-message events."
        self._err_handler = handler

    eleza setLocale(self, locale):
        """Allow an application to set the locale kila errors na warnings.

        SAX parsers are sio required to provide localization kila errors
        na warnings; ikiwa they cannot support the requested locale,
        however, they must ashiria a SAX exception. Applications may
        request a locale change kwenye the middle of a parse."""
        ashiria SAXNotSupportedException("Locale support sio implemented")

    eleza getFeature(self, name):
        "Looks up na rudishas the state of a SAX2 feature."
        ashiria SAXNotRecognizedException("Feature '%s' sio recognized" % name)

    eleza setFeature(self, name, state):
        "Sets the state of a SAX2 feature."
        ashiria SAXNotRecognizedException("Feature '%s' sio recognized" % name)

    eleza getProperty(self, name):
        "Looks up na rudishas the value of a SAX2 property."
        ashiria SAXNotRecognizedException("Property '%s' sio recognized" % name)

    eleza setProperty(self, name, value):
        "Sets the value of a SAX2 property."
        ashiria SAXNotRecognizedException("Property '%s' sio recognized" % name)

kundi IncrementalParser(XMLReader):
    """This interface adds three extra methods to the XMLReader
    interface that allow XML parsers to support incremental
    parsing. Support kila this interface ni optional, since sio all
    underlying XML parsers support this functionality.

    When the parser ni instantiated it ni ready to begin accepting
    data kutoka the feed method immediately. After parsing has been
    finished ukijumuisha a call to close the reset method must be called to
    make the parser ready to accept new data, either kutoka feed or
    using the parse method.

    Note that these methods must _not_ be called during parsing, that
    is, after parse has been called na before it rudishas.

    By default, the kundi also implements the parse method of the XMLReader
    interface using the feed, close na reset methods of the
    IncrementalParser interface kama a convenience to SAX 2.0 driver
    writers."""

    eleza __init__(self, bufsize=2**16):
        self._bufsize = bufsize
        XMLReader.__init__(self)

    eleza parse(self, source):
        kutoka . agiza saxutils
        source = saxutils.prepare_input_source(source)

        self.prepareParser(source)
        file = source.getCharacterStream()
        ikiwa file ni Tupu:
            file = source.getByteStream()
        buffer = file.read(self._bufsize)
        wakati buffer:
            self.feed(buffer)
            buffer = file.read(self._bufsize)
        self.close()

    eleza feed(self, data):
        """This method gives the raw XML data kwenye the data parameter to
        the parser na makes it parse the data, emitting the
        corresponding events. It ni allowed kila XML constructs to be
        split across several calls to feed.

        feed may ashiria SAXException."""
        ashiria NotImplementedError("This method must be implemented!")

    eleza prepareParser(self, source):
        """This method ni called by the parse implementation to allow
        the SAX 2.0 driver to prepare itself kila parsing."""
        ashiria NotImplementedError("prepareParser must be overridden!")

    eleza close(self):
        """This method ni called when the entire XML document has been
        pitaed to the parser through the feed method, to notify the
        parser that there are no more data. This allows the parser to
        do the final checks on the document na empty the internal
        data buffer.

        The parser will sio be ready to parse another document until
        the reset method has been called.

        close may ashiria SAXException."""
        ashiria NotImplementedError("This method must be implemented!")

    eleza reset(self):
        """This method ni called after close has been called to reset
        the parser so that it ni ready to parse new documents. The
        results of calling parse ama feed after close without calling
        reset are undefined."""
        ashiria NotImplementedError("This method must be implemented!")

# ===== LOCATOR =====

kundi Locator:
    """Interface kila associating a SAX event ukijumuisha a document
    location. A locator object will rudisha valid results only during
    calls to DocumentHandler methods; at any other time, the
    results are unpredictable."""

    eleza getColumnNumber(self):
        "Return the column number where the current event ends."
        rudisha -1

    eleza getLineNumber(self):
        "Return the line number where the current event ends."
        rudisha -1

    eleza getPublicId(self):
        "Return the public identifier kila the current event."
        rudisha Tupu

    eleza getSystemId(self):
        "Return the system identifier kila the current event."
        rudisha Tupu

# ===== INPUTSOURCE =====

kundi InputSource:
    """Encapsulation of the information needed by the XMLReader to
    read entities.

    This kundi may include information about the public identifier,
    system identifier, byte stream (possibly ukijumuisha character encoding
    information) and/or the character stream of an entity.

    Applications will create objects of this kundi kila use kwenye the
    XMLReader.parse method na kila rudishaing kutoka
    EntityResolver.resolveEntity.

    An InputSource belongs to the application, the XMLReader ni not
    allowed to modify InputSource objects pitaed to it kutoka the
    application, although it may make copies na modify those."""

    eleza __init__(self, system_id = Tupu):
        self.__system_id = system_id
        self.__public_id = Tupu
        self.__encoding  = Tupu
        self.__bytefile  = Tupu
        self.__charfile  = Tupu

    eleza setPublicId(self, public_id):
        "Sets the public identifier of this InputSource."
        self.__public_id = public_id

    eleza getPublicId(self):
        "Returns the public identifier of this InputSource."
        rudisha self.__public_id

    eleza setSystemId(self, system_id):
        "Sets the system identifier of this InputSource."
        self.__system_id = system_id

    eleza getSystemId(self):
        "Returns the system identifier of this InputSource."
        rudisha self.__system_id

    eleza setEncoding(self, encoding):
        """Sets the character encoding of this InputSource.

        The encoding must be a string acceptable kila an XML encoding
        declaration (see section 4.3.3 of the XML recommendation).

        The encoding attribute of the InputSource ni ignored ikiwa the
        InputSource also contains a character stream."""
        self.__encoding = encoding

    eleza getEncoding(self):
        "Get the character encoding of this InputSource."
        rudisha self.__encoding

    eleza setByteStream(self, bytefile):
        """Set the byte stream (a Python file-like object which does
        sio perform byte-to-character conversion) kila this input
        source.

        The SAX parser will ignore this ikiwa there ni also a character
        stream specified, but it will use a byte stream kwenye preference
        to opening a URI connection itself.

        If the application knows the character encoding of the byte
        stream, it should set it ukijumuisha the setEncoding method."""
        self.__bytefile = bytefile

    eleza getByteStream(self):
        """Get the byte stream kila this input source.

        The getEncoding method will rudisha the character encoding for
        this byte stream, ama Tupu ikiwa unknown."""
        rudisha self.__bytefile

    eleza setCharacterStream(self, charfile):
        """Set the character stream kila this input source. (The stream
        must be a Python 2.0 Unicode-wrapped file-like that performs
        conversion to Unicode strings.)

        If there ni a character stream specified, the SAX parser will
        ignore any byte stream na will sio attempt to open a URI
        connection to the system identifier."""
        self.__charfile = charfile

    eleza getCharacterStream(self):
        "Get the character stream kila this input source."
        rudisha self.__charfile

# ===== ATTRIBUTESIMPL =====

kundi AttributesImpl:

    eleza __init__(self, attrs):
        """Non-NS-aware implementation.

        attrs should be of the form {name : value}."""
        self._attrs = attrs

    eleza getLength(self):
        rudisha len(self._attrs)

    eleza getType(self, name):
        rudisha "CDATA"

    eleza getValue(self, name):
        rudisha self._attrs[name]

    eleza getValueByQName(self, name):
        rudisha self._attrs[name]

    eleza getNameByQName(self, name):
        ikiwa name haiko kwenye self._attrs:
            ashiria KeyError(name)
        rudisha name

    eleza getQNameByName(self, name):
        ikiwa name haiko kwenye self._attrs:
            ashiria KeyError(name)
        rudisha name

    eleza getNames(self):
        rudisha list(self._attrs.keys())

    eleza getQNames(self):
        rudisha list(self._attrs.keys())

    eleza __len__(self):
        rudisha len(self._attrs)

    eleza __getitem__(self, name):
        rudisha self._attrs[name]

    eleza keys(self):
        rudisha list(self._attrs.keys())

    eleza __contains__(self, name):
        rudisha name kwenye self._attrs

    eleza get(self, name, alternative=Tupu):
        rudisha self._attrs.get(name, alternative)

    eleza copy(self):
        rudisha self.__class__(self._attrs)

    eleza items(self):
        rudisha list(self._attrs.items())

    eleza values(self):
        rudisha list(self._attrs.values())

# ===== ATTRIBUTESNSIMPL =====

kundi AttributesNSImpl(AttributesImpl):

    eleza __init__(self, attrs, qnames):
        """NS-aware implementation.

        attrs should be of the form {(ns_uri, lname): value, ...}.
        qnames of the form {(ns_uri, lname): qname, ...}."""
        self._attrs = attrs
        self._qnames = qnames

    eleza getValueByQName(self, name):
        kila (nsname, qname) kwenye self._qnames.items():
            ikiwa qname == name:
                rudisha self._attrs[nsname]

        ashiria KeyError(name)

    eleza getNameByQName(self, name):
        kila (nsname, qname) kwenye self._qnames.items():
            ikiwa qname == name:
                rudisha nsname

        ashiria KeyError(name)

    eleza getQNameByName(self, name):
        rudisha self._qnames[name]

    eleza getQNames(self):
        rudisha list(self._qnames.values())

    eleza copy(self):
        rudisha self.__class__(self._attrs, self._qnames)


eleza _test():
    XMLReader()
    IncrementalParser()
    Locator()

ikiwa __name__ == "__main__":
    _test()
