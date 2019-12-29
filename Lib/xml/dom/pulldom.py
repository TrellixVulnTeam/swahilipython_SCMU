agiza xml.sax
agiza xml.sax.handler

START_ELEMENT = "START_ELEMENT"
END_ELEMENT = "END_ELEMENT"
COMMENT = "COMMENT"
START_DOCUMENT = "START_DOCUMENT"
END_DOCUMENT = "END_DOCUMENT"
PROCESSING_INSTRUCTION = "PROCESSING_INSTRUCTION"
IGNORABLE_WHITESPACE = "IGNORABLE_WHITESPACE"
CHARACTERS = "CHARACTERS"

kundi PullDOM(xml.sax.ContentHandler):
    _locator = Tupu
    document = Tupu

    eleza __init__(self, documentFactory=Tupu):
        kutoka xml.dom agiza XML_NAMESPACE
        self.documentFactory = documentFactory
        self.firstEvent = [Tupu, Tupu]
        self.lastEvent = self.firstEvent
        self.elementStack = []
        self.push = self.elementStack.append
        jaribu:
            self.pop = self.elementStack.pop
        tatizo AttributeError:
            # use class' pop instead
            pita
        self._ns_contexts = [{XML_NAMESPACE:'xml'}] # contains uri -> prefix dicts
        self._current_context = self._ns_contexts[-1]
        self.pending_events = []

    eleza pop(self):
        result = self.elementStack[-1]
        toa self.elementStack[-1]
        rudisha result

    eleza setDocumentLocator(self, locator):
        self._locator = locator

    eleza startPrefixMapping(self, prefix, uri):
        ikiwa sio hasattr(self, '_xmlns_attrs'):
            self._xmlns_attrs = []
        self._xmlns_attrs.append((prefix ama 'xmlns', uri))
        self._ns_contexts.append(self._current_context.copy())
        self._current_context[uri] = prefix ama Tupu

    eleza endPrefixMapping(self, prefix):
        self._current_context = self._ns_contexts.pop()

    eleza startElementNS(self, name, tagName , attrs):
        # Retrieve xml namespace declaration attributes.
        xmlns_uri = 'http://www.w3.org/2000/xmlns/'
        xmlns_attrs = getattr(self, '_xmlns_attrs', Tupu)
        ikiwa xmlns_attrs ni sio Tupu:
            kila aname, value kwenye xmlns_attrs:
                attrs._attrs[(xmlns_uri, aname)] = value
            self._xmlns_attrs = []
        uri, localname = name
        ikiwa uri:
            # When using namespaces, the reader may ama may not
            # provide us with the original name. If not, create
            # *a* valid tagName kutoka the current context.
            ikiwa tagName ni Tupu:
                prefix = self._current_context[uri]
                ikiwa prefix:
                    tagName = prefix + ":" + localname
                isipokua:
                    tagName = localname
            ikiwa self.document:
                node = self.document.createElementNS(uri, tagName)
            isipokua:
                node = self.buildDocument(uri, tagName)
        isipokua:
            # When the tagname ni sio prefixed, it just appears as
            # localname
            ikiwa self.document:
                node = self.document.createElement(localname)
            isipokua:
                node = self.buildDocument(Tupu, localname)

        kila aname,value kwenye attrs.items():
            a_uri, a_localname = aname
            ikiwa a_uri == xmlns_uri:
                ikiwa a_localname == 'xmlns':
                    qname = a_localname
                isipokua:
                    qname = 'xmlns:' + a_localname
                attr = self.document.createAttributeNS(a_uri, qname)
                node.setAttributeNodeNS(attr)
            elikiwa a_uri:
                prefix = self._current_context[a_uri]
                ikiwa prefix:
                    qname = prefix + ":" + a_localname
                isipokua:
                    qname = a_localname
                attr = self.document.createAttributeNS(a_uri, qname)
                node.setAttributeNodeNS(attr)
            isipokua:
                attr = self.document.createAttribute(a_localname)
                node.setAttributeNode(attr)
            attr.value = value

        self.lastEvent[1] = [(START_ELEMENT, node), Tupu]
        self.lastEvent = self.lastEvent[1]
        self.push(node)

    eleza endElementNS(self, name, tagName):
        self.lastEvent[1] = [(END_ELEMENT, self.pop()), Tupu]
        self.lastEvent = self.lastEvent[1]

    eleza startElement(self, name, attrs):
        ikiwa self.document:
            node = self.document.createElement(name)
        isipokua:
            node = self.buildDocument(Tupu, name)

        kila aname,value kwenye attrs.items():
            attr = self.document.createAttribute(aname)
            attr.value = value
            node.setAttributeNode(attr)

        self.lastEvent[1] = [(START_ELEMENT, node), Tupu]
        self.lastEvent = self.lastEvent[1]
        self.push(node)

    eleza endElement(self, name):
        self.lastEvent[1] = [(END_ELEMENT, self.pop()), Tupu]
        self.lastEvent = self.lastEvent[1]

    eleza comment(self, s):
        ikiwa self.document:
            node = self.document.createComment(s)
            self.lastEvent[1] = [(COMMENT, node), Tupu]
            self.lastEvent = self.lastEvent[1]
        isipokua:
            event = [(COMMENT, s), Tupu]
            self.pending_events.append(event)

    eleza processingInstruction(self, target, data):
        ikiwa self.document:
            node = self.document.createProcessingInstruction(target, data)
            self.lastEvent[1] = [(PROCESSING_INSTRUCTION, node), Tupu]
            self.lastEvent = self.lastEvent[1]
        isipokua:
            event = [(PROCESSING_INSTRUCTION, target, data), Tupu]
            self.pending_events.append(event)

    eleza ignorableWhitespace(self, chars):
        node = self.document.createTextNode(chars)
        self.lastEvent[1] = [(IGNORABLE_WHITESPACE, node), Tupu]
        self.lastEvent = self.lastEvent[1]

    eleza characters(self, chars):
        node = self.document.createTextNode(chars)
        self.lastEvent[1] = [(CHARACTERS, node), Tupu]
        self.lastEvent = self.lastEvent[1]

    eleza startDocument(self):
        ikiwa self.documentFactory ni Tupu:
            agiza xml.dom.minidom
            self.documentFactory = xml.dom.minidom.Document.implementation

    eleza buildDocument(self, uri, tagname):
        # Can't do that kwenye startDocument, since we need the tagname
        # XXX: obtain DocumentType
        node = self.documentFactory.createDocument(uri, tagname, Tupu)
        self.document = node
        self.lastEvent[1] = [(START_DOCUMENT, node), Tupu]
        self.lastEvent = self.lastEvent[1]
        self.push(node)
        # Put everything we have seen so far into the document
        kila e kwenye self.pending_events:
            ikiwa e[0][0] == PROCESSING_INSTRUCTION:
                _,target,data = e[0]
                n = self.document.createProcessingInstruction(target, data)
                e[0] = (PROCESSING_INSTRUCTION, n)
            elikiwa e[0][0] == COMMENT:
                n = self.document.createComment(e[0][1])
                e[0] = (COMMENT, n)
            isipokua:
                ashiria AssertionError("Unknown pending event ",e[0][0])
            self.lastEvent[1] = e
            self.lastEvent = e
        self.pending_events = Tupu
        rudisha node.firstChild

    eleza endDocument(self):
        self.lastEvent[1] = [(END_DOCUMENT, self.document), Tupu]
        self.pop()

    eleza clear(self):
        "clear(): Explicitly release parsing structures"
        self.document = Tupu

kundi ErrorHandler:
    eleza warning(self, exception):
        andika(exception)
    eleza error(self, exception):
        ashiria exception
    eleza fatalError(self, exception):
        ashiria exception

kundi DOMEventStream:
    eleza __init__(self, stream, parser, bufsize):
        self.stream = stream
        self.parser = parser
        self.bufsize = bufsize
        ikiwa sio hasattr(self.parser, 'feed'):
            self.getEvent = self._slurp
        self.reset()

    eleza reset(self):
        self.pulldom = PullDOM()
        # This content handler relies on namespace support
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 1)
        self.parser.setContentHandler(self.pulldom)

    eleza __getitem__(self, pos):
        agiza warnings
        warnings.warn(
            "DOMEventStream's __getitem__ method ignores 'pos' parameter. "
            "Use iterator protocol instead.",
            DeprecationWarning,
            stacklevel=2
        )
        rc = self.getEvent()
        ikiwa rc:
            rudisha rc
        ashiria IndexError

    eleza __next__(self):
        rc = self.getEvent()
        ikiwa rc:
            rudisha rc
        ashiria StopIteration

    eleza __iter__(self):
        rudisha self

    eleza expandNode(self, node):
        event = self.getEvent()
        parents = [node]
        wakati event:
            token, cur_node = event
            ikiwa cur_node ni node:
                rudisha
            ikiwa token != END_ELEMENT:
                parents[-1].appendChild(cur_node)
            ikiwa token == START_ELEMENT:
                parents.append(cur_node)
            elikiwa token == END_ELEMENT:
                toa parents[-1]
            event = self.getEvent()

    eleza getEvent(self):
        # use IncrementalParser interface, so we get the desired
        # pull effect
        ikiwa sio self.pulldom.firstEvent[1]:
            self.pulldom.lastEvent = self.pulldom.firstEvent
        wakati sio self.pulldom.firstEvent[1]:
            buf = self.stream.read(self.bufsize)
            ikiwa sio buf:
                self.parser.close()
                rudisha Tupu
            self.parser.feed(buf)
        rc = self.pulldom.firstEvent[1][0]
        self.pulldom.firstEvent[1] = self.pulldom.firstEvent[1][1]
        rudisha rc

    eleza _slurp(self):
        """ Fallback replacement kila getEvent() using the
            standard SAX2 interface, which means we slurp the
            SAX events into memory (no performance gain, but
            we are compatible to all SAX parsers).
        """
        self.parser.parse(self.stream)
        self.getEvent = self._emit
        rudisha self._emit()

    eleza _emit(self):
        """ Fallback replacement kila getEvent() that emits
            the events that _slurp() read previously.
        """
        rc = self.pulldom.firstEvent[1][0]
        self.pulldom.firstEvent[1] = self.pulldom.firstEvent[1][1]
        rudisha rc

    eleza clear(self):
        """clear(): Explicitly release parsing objects"""
        self.pulldom.clear()
        toa self.pulldom
        self.parser = Tupu
        self.stream = Tupu

kundi SAX2DOM(PullDOM):

    eleza startElementNS(self, name, tagName , attrs):
        PullDOM.startElementNS(self, name, tagName, attrs)
        curNode = self.elementStack[-1]
        parentNode = self.elementStack[-2]
        parentNode.appendChild(curNode)

    eleza startElement(self, name, attrs):
        PullDOM.startElement(self, name, attrs)
        curNode = self.elementStack[-1]
        parentNode = self.elementStack[-2]
        parentNode.appendChild(curNode)

    eleza processingInstruction(self, target, data):
        PullDOM.processingInstruction(self, target, data)
        node = self.lastEvent[0][1]
        parentNode = self.elementStack[-1]
        parentNode.appendChild(node)

    eleza ignorableWhitespace(self, chars):
        PullDOM.ignorableWhitespace(self, chars)
        node = self.lastEvent[0][1]
        parentNode = self.elementStack[-1]
        parentNode.appendChild(node)

    eleza characters(self, chars):
        PullDOM.characters(self, chars)
        node = self.lastEvent[0][1]
        parentNode = self.elementStack[-1]
        parentNode.appendChild(node)


default_bufsize = (2 ** 14) - 20

eleza parse(stream_or_string, parser=Tupu, bufsize=Tupu):
    ikiwa bufsize ni Tupu:
        bufsize = default_bufsize
    ikiwa isinstance(stream_or_string, str):
        stream = open(stream_or_string, 'rb')
    isipokua:
        stream = stream_or_string
    ikiwa sio parser:
        parser = xml.sax.make_parser()
    rudisha DOMEventStream(stream, parser, bufsize)

eleza parseString(string, parser=Tupu):
    kutoka io agiza StringIO

    bufsize = len(string)
    buf = StringIO(string)
    ikiwa sio parser:
        parser = xml.sax.make_parser()
    rudisha DOMEventStream(buf, parser, bufsize)
