"""\
A library of useful helper classes to the SAX classes, for the
convenience of application and driver writers.
"""

agiza os, urllib.parse, urllib.request
agiza io
agiza codecs
kutoka . agiza handler
kutoka . agiza xmlreader

eleza __dict_replace(s, d):
    """Replace substrings of a string using a dictionary."""
    for key, value in d.items():
        s = s.replace(key, value)
    rudisha s

eleza escape(data, entities={}):
    """Escape &, <, and > in a string of data.

    You can escape other strings of data by passing a dictionary as
    the optional entities parameter.  The keys and values must all be
    strings; each key will be replaced with its corresponding value.
    """

    # must do ampersand first
    data = data.replace("&", "&amp;")
    data = data.replace(">", "&gt;")
    data = data.replace("<", "&lt;")
    ikiwa entities:
        data = __dict_replace(data, entities)
    rudisha data

eleza unescape(data, entities={}):
    """Unescape &amp;, &lt;, and &gt; in a string of data.

    You can unescape other strings of data by passing a dictionary as
    the optional entities parameter.  The keys and values must all be
    strings; each key will be replaced with its corresponding value.
    """
    data = data.replace("&lt;", "<")
    data = data.replace("&gt;", ">")
    ikiwa entities:
        data = __dict_replace(data, entities)
    # must do ampersand last
    rudisha data.replace("&amp;", "&")

eleza quoteattr(data, entities={}):
    """Escape and quote an attribute value.

    Escape &, <, and > in a string of data, then quote it for use as
    an attribute value.  The \" character will be escaped as well, if
    necessary.

    You can escape other strings of data by passing a dictionary as
    the optional entities parameter.  The keys and values must all be
    strings; each key will be replaced with its corresponding value.
    """
    entities = {**entities, '\n': '&#10;', '\r': '&#13;', '\t':'&#9;'}
    data = escape(data, entities)
    ikiwa '"' in data:
        ikiwa "'" in data:
            data = '"%s"' % data.replace('"', "&quot;")
        else:
            data = "'%s'" % data
    else:
        data = '"%s"' % data
    rudisha data


eleza _gettextwriter(out, encoding):
    ikiwa out is None:
        agiza sys
        rudisha sys.stdout

    ikiwa isinstance(out, io.TextIOBase):
        # use a text writer as is
        rudisha out

    ikiwa isinstance(out, (codecs.StreamWriter, codecs.StreamReaderWriter)):
        # use a codecs stream writer as is
        rudisha out

    # wrap a binary writer with TextIOWrapper
    ikiwa isinstance(out, io.RawIOBase):
        # Keep the original file open when the TextIOWrapper is
        # destroyed
        kundi _wrapper:
            __class__ = out.__class__
            eleza __getattr__(self, name):
                rudisha getattr(out, name)
        buffer = _wrapper()
        buffer.close = lambda: None
    else:
        # This is to handle passed objects that aren't in the
        # IOBase hierarchy, but just have a write method
        buffer = io.BufferedIOBase()
        buffer.writable = lambda: True
        buffer.write = out.write
        try:
            # TextIOWrapper uses this methods to determine
            # ikiwa BOM (for UTF-16, etc) should be added
            buffer.seekable = out.seekable
            buffer.tell = out.tell
        except AttributeError:
            pass
    rudisha io.TextIOWrapper(buffer, encoding=encoding,
                            errors='xmlcharrefreplace',
                            newline='\n',
                            write_through=True)

kundi XMLGenerator(handler.ContentHandler):

    eleza __init__(self, out=None, encoding="iso-8859-1", short_empty_elements=False):
        handler.ContentHandler.__init__(self)
        out = _gettextwriter(out, encoding)
        self._write = out.write
        self._flush = out.flush
        self._ns_contexts = [{}] # contains uri -> prefix dicts
        self._current_context = self._ns_contexts[-1]
        self._undeclared_ns_maps = []
        self._encoding = encoding
        self._short_empty_elements = short_empty_elements
        self._pending_start_element = False

    eleza _qname(self, name):
        """Builds a qualified name kutoka a (ns_url, localname) pair"""
        ikiwa name[0]:
            # Per http://www.w3.org/XML/1998/namespace, The 'xml' prefix is
            # bound by definition to http://www.w3.org/XML/1998/namespace.  It
            # does not need to be declared and will not usually be found in
            # self._current_context.
            ikiwa 'http://www.w3.org/XML/1998/namespace' == name[0]:
                rudisha 'xml:' + name[1]
            # The name is in a non-empty namespace
            prefix = self._current_context[name[0]]
            ikiwa prefix:
                # If it is not the default namespace, prepend the prefix
                rudisha prefix + ":" + name[1]
        # Return the unqualified name
        rudisha name[1]

    eleza _finish_pending_start_element(self,endElement=False):
        ikiwa self._pending_start_element:
            self._write('>')
            self._pending_start_element = False

    # ContentHandler methods

    eleza startDocument(self):
        self._write('<?xml version="1.0" encoding="%s"?>\n' %
                        self._encoding)

    eleza endDocument(self):
        self._flush()

    eleza startPrefixMapping(self, prefix, uri):
        self._ns_contexts.append(self._current_context.copy())
        self._current_context[uri] = prefix
        self._undeclared_ns_maps.append((prefix, uri))

    eleza endPrefixMapping(self, prefix):
        self._current_context = self._ns_contexts[-1]
        del self._ns_contexts[-1]

    eleza startElement(self, name, attrs):
        self._finish_pending_start_element()
        self._write('<' + name)
        for (name, value) in attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))
        ikiwa self._short_empty_elements:
            self._pending_start_element = True
        else:
            self._write(">")

    eleza endElement(self, name):
        ikiwa self._pending_start_element:
            self._write('/>')
            self._pending_start_element = False
        else:
            self._write('</%s>' % name)

    eleza startElementNS(self, name, qname, attrs):
        self._finish_pending_start_element()
        self._write('<' + self._qname(name))

        for prefix, uri in self._undeclared_ns_maps:
            ikiwa prefix:
                self._write(' xmlns:%s="%s"' % (prefix, uri))
            else:
                self._write(' xmlns="%s"' % uri)
        self._undeclared_ns_maps = []

        for (name, value) in attrs.items():
            self._write(' %s=%s' % (self._qname(name), quoteattr(value)))
        ikiwa self._short_empty_elements:
            self._pending_start_element = True
        else:
            self._write(">")

    eleza endElementNS(self, name, qname):
        ikiwa self._pending_start_element:
            self._write('/>')
            self._pending_start_element = False
        else:
            self._write('</%s>' % self._qname(name))

    eleza characters(self, content):
        ikiwa content:
            self._finish_pending_start_element()
            ikiwa not isinstance(content, str):
                content = str(content, self._encoding)
            self._write(escape(content))

    eleza ignorableWhitespace(self, content):
        ikiwa content:
            self._finish_pending_start_element()
            ikiwa not isinstance(content, str):
                content = str(content, self._encoding)
            self._write(content)

    eleza processingInstruction(self, target, data):
        self._finish_pending_start_element()
        self._write('<?%s %s?>' % (target, data))


kundi XMLFilterBase(xmlreader.XMLReader):
    """This kundi is designed to sit between an XMLReader and the
    client application's event handlers.  By default, it does nothing
    but pass requests up to the reader and events on to the handlers
    unmodified, but subclasses can override specific methods to modify
    the event stream or the configuration requests as they pass
    through."""

    eleza __init__(self, parent = None):
        xmlreader.XMLReader.__init__(self)
        self._parent = parent

    # ErrorHandler methods

    eleza error(self, exception):
        self._err_handler.error(exception)

    eleza fatalError(self, exception):
        self._err_handler.fatalError(exception)

    eleza warning(self, exception):
        self._err_handler.warning(exception)

    # ContentHandler methods

    eleza setDocumentLocator(self, locator):
        self._cont_handler.setDocumentLocator(locator)

    eleza startDocument(self):
        self._cont_handler.startDocument()

    eleza endDocument(self):
        self._cont_handler.endDocument()

    eleza startPrefixMapping(self, prefix, uri):
        self._cont_handler.startPrefixMapping(prefix, uri)

    eleza endPrefixMapping(self, prefix):
        self._cont_handler.endPrefixMapping(prefix)

    eleza startElement(self, name, attrs):
        self._cont_handler.startElement(name, attrs)

    eleza endElement(self, name):
        self._cont_handler.endElement(name)

    eleza startElementNS(self, name, qname, attrs):
        self._cont_handler.startElementNS(name, qname, attrs)

    eleza endElementNS(self, name, qname):
        self._cont_handler.endElementNS(name, qname)

    eleza characters(self, content):
        self._cont_handler.characters(content)

    eleza ignorableWhitespace(self, chars):
        self._cont_handler.ignorableWhitespace(chars)

    eleza processingInstruction(self, target, data):
        self._cont_handler.processingInstruction(target, data)

    eleza skippedEntity(self, name):
        self._cont_handler.skippedEntity(name)

    # DTDHandler methods

    eleza notationDecl(self, name, publicId, systemId):
        self._dtd_handler.notationDecl(name, publicId, systemId)

    eleza unparsedEntityDecl(self, name, publicId, systemId, ndata):
        self._dtd_handler.unparsedEntityDecl(name, publicId, systemId, ndata)

    # EntityResolver methods

    eleza resolveEntity(self, publicId, systemId):
        rudisha self._ent_handler.resolveEntity(publicId, systemId)

    # XMLReader methods

    eleza parse(self, source):
        self._parent.setContentHandler(self)
        self._parent.setErrorHandler(self)
        self._parent.setEntityResolver(self)
        self._parent.setDTDHandler(self)
        self._parent.parse(source)

    eleza setLocale(self, locale):
        self._parent.setLocale(locale)

    eleza getFeature(self, name):
        rudisha self._parent.getFeature(name)

    eleza setFeature(self, name, state):
        self._parent.setFeature(name, state)

    eleza getProperty(self, name):
        rudisha self._parent.getProperty(name)

    eleza setProperty(self, name, value):
        self._parent.setProperty(name, value)

    # XMLFilter methods

    eleza getParent(self):
        rudisha self._parent

    eleza setParent(self, parent):
        self._parent = parent

# --- Utility functions

eleza prepare_input_source(source, base=""):
    """This function takes an InputSource and an optional base URL and
    returns a fully resolved InputSource object ready for reading."""

    ikiwa isinstance(source, os.PathLike):
        source = os.fspath(source)
    ikiwa isinstance(source, str):
        source = xmlreader.InputSource(source)
    elikiwa hasattr(source, "read"):
        f = source
        source = xmlreader.InputSource()
        ikiwa isinstance(f.read(0), str):
            source.setCharacterStream(f)
        else:
            source.setByteStream(f)
        ikiwa hasattr(f, "name") and isinstance(f.name, str):
            source.setSystemId(f.name)

    ikiwa source.getCharacterStream() is None and source.getByteStream() is None:
        sysid = source.getSystemId()
        basehead = os.path.dirname(os.path.normpath(base))
        sysidfilename = os.path.join(basehead, sysid)
        ikiwa os.path.isfile(sysidfilename):
            source.setSystemId(sysidfilename)
            f = open(sysidfilename, "rb")
        else:
            source.setSystemId(urllib.parse.urljoin(base, sysid))
            f = urllib.request.urlopen(source.getSystemId())

        source.setByteStream(f)

    rudisha source
