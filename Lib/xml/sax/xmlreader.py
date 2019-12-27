"""An XML Reader is the SAX 2 name for an XML parser. XML Parsers
should be based on this code. """

kutoka . agiza handler

kutoka ._exceptions agiza SAXNotSupportedException, SAXNotRecognizedException


# ===== XMLREADER =====

kundi XMLReader:
    """Interface for reading an XML document using callbacks.

    XMLReader is the interface that an XML parser's SAX2 driver must
    implement. This interface allows an application to set and query
    features and properties in the parser, to register event handlers
    for document processing, and to initiate a document parse.

    All SAX interfaces are assumed to be synchronous: the parse
    methods must not rudisha until parsing is complete, and readers
    must wait for an event-handler callback to rudisha before reporting
    the next event."""

    eleza __init__(self):
        self._cont_handler = handler.ContentHandler()
        self._dtd_handler = handler.DTDHandler()
        self._ent_handler = handler.EntityResolver()
        self._err_handler = handler.ErrorHandler()

    eleza parse(self, source):
        "Parse an XML document kutoka a system identifier or an InputSource."
        raise NotImplementedError("This method must be implemented!")

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
        """Allow an application to set the locale for errors and warnings.

        SAX parsers are not required to provide localization for errors
        and warnings; ikiwa they cannot support the requested locale,
        however, they must raise a SAX exception. Applications may
        request a locale change in the middle of a parse."""
        raise SAXNotSupportedException("Locale support not implemented")

    eleza getFeature(self, name):
        "Looks up and returns the state of a SAX2 feature."
        raise SAXNotRecognizedException("Feature '%s' not recognized" % name)

    eleza setFeature(self, name, state):
        "Sets the state of a SAX2 feature."
        raise SAXNotRecognizedException("Feature '%s' not recognized" % name)

    eleza getProperty(self, name):
        "Looks up and returns the value of a SAX2 property."
        raise SAXNotRecognizedException("Property '%s' not recognized" % name)

    eleza setProperty(self, name, value):
        "Sets the value of a SAX2 property."
        raise SAXNotRecognizedException("Property '%s' not recognized" % name)

kundi IncrementalParser(XMLReader):
    """This interface adds three extra methods to the XMLReader
    interface that allow XML parsers to support incremental
    parsing. Support for this interface is optional, since not all
    underlying XML parsers support this functionality.

    When the parser is instantiated it is ready to begin accepting
    data kutoka the feed method immediately. After parsing has been
    finished with a call to close the reset method must be called to
    make the parser ready to accept new data, either kutoka feed or
    using the parse method.

    Note that these methods must _not_ be called during parsing, that
    is, after parse has been called and before it returns.

    By default, the kundi also implements the parse method of the XMLReader
    interface using the feed, close and reset methods of the
    IncrementalParser interface as a convenience to SAX 2.0 driver
    writers."""

    eleza __init__(self, bufsize=2**16):
        self._bufsize = bufsize
        XMLReader.__init__(self)

    eleza parse(self, source):
        kutoka . agiza saxutils
        source = saxutils.prepare_input_source(source)

        self.prepareParser(source)
        file = source.getCharacterStream()
        ikiwa file is None:
            file = source.getByteStream()
        buffer = file.read(self._bufsize)
        while buffer:
            self.feed(buffer)
            buffer = file.read(self._bufsize)
        self.close()

    eleza feed(self, data):
        """This method gives the raw XML data in the data parameter to
        the parser and makes it parse the data, emitting the
        corresponding events. It is allowed for XML constructs to be
        split across several calls to feed.

        feed may raise SAXException."""
        raise NotImplementedError("This method must be implemented!")

    eleza prepareParser(self, source):
        """This method is called by the parse implementation to allow
        the SAX 2.0 driver to prepare itself for parsing."""
        raise NotImplementedError("prepareParser must be overridden!")

    eleza close(self):
        """This method is called when the entire XML document has been
        passed to the parser through the feed method, to notify the
        parser that there are no more data. This allows the parser to
        do the final checks on the document and empty the internal
        data buffer.

        The parser will not be ready to parse another document until
        the reset method has been called.

        close may raise SAXException."""
        raise NotImplementedError("This method must be implemented!")

    eleza reset(self):
        """This method is called after close has been called to reset
        the parser so that it is ready to parse new documents. The
        results of calling parse or feed after close without calling
        reset are undefined."""
        raise NotImplementedError("This method must be implemented!")

# ===== LOCATOR =====

kundi Locator:
    """Interface for associating a SAX event with a document
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
        "Return the public identifier for the current event."
        rudisha None

    eleza getSystemId(self):
        "Return the system identifier for the current event."
        rudisha None

# ===== INPUTSOURCE =====

kundi InputSource:
    """Encapsulation of the information needed by the XMLReader to
    read entities.

    This kundi may include information about the public identifier,
    system identifier, byte stream (possibly with character encoding
    information) and/or the character stream of an entity.

    Applications will create objects of this kundi for use in the
    XMLReader.parse method and for returning kutoka
    EntityResolver.resolveEntity.

    An InputSource belongs to the application, the XMLReader is not
    allowed to modify InputSource objects passed to it kutoka the
    application, although it may make copies and modify those."""

    eleza __init__(self, system_id = None):
        self.__system_id = system_id
        self.__public_id = None
        self.__encoding  = None
        self.__bytefile  = None
        self.__charfile  = None

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

        The encoding must be a string acceptable for an XML encoding
        declaration (see section 4.3.3 of the XML recommendation).

        The encoding attribute of the InputSource is ignored ikiwa the
        InputSource also contains a character stream."""
        self.__encoding = encoding

    eleza getEncoding(self):
        "Get the character encoding of this InputSource."
        rudisha self.__encoding

    eleza setByteStream(self, bytefile):
        """Set the byte stream (a Python file-like object which does
        not perform byte-to-character conversion) for this input
        source.

        The SAX parser will ignore this ikiwa there is also a character
        stream specified, but it will use a byte stream in preference
        to opening a URI connection itself.

        If the application knows the character encoding of the byte
        stream, it should set it with the setEncoding method."""
        self.__bytefile = bytefile

    eleza getByteStream(self):
        """Get the byte stream for this input source.

        The getEncoding method will rudisha the character encoding for
        this byte stream, or None ikiwa unknown."""
        rudisha self.__bytefile

    eleza setCharacterStream(self, charfile):
        """Set the character stream for this input source. (The stream
        must be a Python 2.0 Unicode-wrapped file-like that performs
        conversion to Unicode strings.)

        If there is a character stream specified, the SAX parser will
        ignore any byte stream and will not attempt to open a URI
        connection to the system identifier."""
        self.__charfile = charfile

    eleza getCharacterStream(self):
        "Get the character stream for this input source."
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
        ikiwa name not in self._attrs:
            raise KeyError(name)
        rudisha name

    eleza getQNameByName(self, name):
        ikiwa name not in self._attrs:
            raise KeyError(name)
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
        rudisha name in self._attrs

    eleza get(self, name, alternative=None):
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
        for (nsname, qname) in self._qnames.items():
            ikiwa qname == name:
                rudisha self._attrs[nsname]

        raise KeyError(name)

    eleza getNameByQName(self, name):
        for (nsname, qname) in self._qnames.items():
            ikiwa qname == name:
                rudisha nsname

        raise KeyError(name)

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
