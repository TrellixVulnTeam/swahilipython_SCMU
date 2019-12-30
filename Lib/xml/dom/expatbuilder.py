"""Facility to use the Expat parser to load a minidom instance
kutoka a string ama file.

This avoids all the overhead of SAX na pulldom to gain performance.
"""

# Warning!
#
# This module ni tightly bound to the implementation details of the
# minidom DOM na can't be used ukijumuisha other DOM implementations.  This
# ni due, kwenye part, to a lack of appropriate methods kwenye the DOM (there is
# no way to create Entity na Notation nodes via the DOM Level 2
# interface), na kila performance.  The latter ni the cause of some fairly
# cryptic code.
#
# Performance hacks:
#
#   -  .character_data_handler() has an extra case kwenye which continuing
#      data ni appended to an existing Text node; this can be a
#      speedup since pyexpat can koma up character data into multiple
#      callbacks even though we set the buffer_text attribute on the
#      parser.  This also gives us the advantage that we don't need a
#      separate normalization pita.
#
#   -  Determining that a node exists ni done using an identity comparison
#      ukijumuisha Tupu rather than a truth test; this avoids searching kila na
#      calling any methods on the node object ikiwa it exists.  (A rather
#      nice speedup ni achieved this way kama well!)

kutoka xml.dom agiza xmlbuilder, minidom, Node
kutoka xml.dom agiza EMPTY_NAMESPACE, EMPTY_PREFIX, XMLNS_NAMESPACE
kutoka xml.parsers agiza expat
kutoka xml.dom.minidom agiza _append_child, _set_attribute_node
kutoka xml.dom.NodeFilter agiza NodeFilter

TEXT_NODE = Node.TEXT_NODE
CDATA_SECTION_NODE = Node.CDATA_SECTION_NODE
DOCUMENT_NODE = Node.DOCUMENT_NODE

FILTER_ACCEPT = xmlbuilder.DOMBuilderFilter.FILTER_ACCEPT
FILTER_REJECT = xmlbuilder.DOMBuilderFilter.FILTER_REJECT
FILTER_SKIP = xmlbuilder.DOMBuilderFilter.FILTER_SKIP
FILTER_INTERRUPT = xmlbuilder.DOMBuilderFilter.FILTER_INTERRUPT

theDOMImplementation = minidom.getDOMImplementation()

# Expat typename -> TypeInfo
_typeinfo_map = {
    "CDATA":    minidom.TypeInfo(Tupu, "cdata"),
    "ENUM":     minidom.TypeInfo(Tupu, "enumeration"),
    "ENTITY":   minidom.TypeInfo(Tupu, "entity"),
    "ENTITIES": minidom.TypeInfo(Tupu, "entities"),
    "ID":       minidom.TypeInfo(Tupu, "id"),
    "IDREF":    minidom.TypeInfo(Tupu, "idref"),
    "IDREFS":   minidom.TypeInfo(Tupu, "idrefs"),
    "NMTOKEN":  minidom.TypeInfo(Tupu, "nmtoken"),
    "NMTOKENS": minidom.TypeInfo(Tupu, "nmtokens"),
    }

kundi ElementInfo(object):
    __slots__ = '_attr_info', '_model', 'tagName'

    eleza __init__(self, tagName, model=Tupu):
        self.tagName = tagName
        self._attr_info = []
        self._motoa = model

    eleza __getstate__(self):
        rudisha self._attr_info, self._model, self.tagName

    eleza __setstate__(self, state):
        self._attr_info, self._model, self.tagName = state

    eleza getAttributeType(self, aname):
        kila info kwenye self._attr_info:
            ikiwa info[1] == aname:
                t = info[-2]
                ikiwa t[0] == "(":
                    rudisha _typeinfo_map["ENUM"]
                isipokua:
                    rudisha _typeinfo_map[info[-2]]
        rudisha minidom._no_type

    eleza getAttributeTypeNS(self, namespaceURI, localName):
        rudisha minidom._no_type

    eleza isElementContent(self):
        ikiwa self._model:
            type = self._model[0]
            rudisha type haiko kwenye (expat.model.XML_CTYPE_ANY,
                                expat.model.XML_CTYPE_MIXED)
        isipokua:
            rudisha Uongo

    eleza isEmpty(self):
        ikiwa self._model:
            rudisha self._model[0] == expat.model.XML_CTYPE_EMPTY
        isipokua:
            rudisha Uongo

    eleza isId(self, aname):
        kila info kwenye self._attr_info:
            ikiwa info[1] == aname:
                rudisha info[-2] == "ID"
        rudisha Uongo

    eleza isIdNS(self, euri, ename, auri, aname):
        # sio sure this ni meaningful
        rudisha self.isId((auri, aname))

eleza _intern(builder, s):
    rudisha builder._intern_setdefault(s, s)

eleza _parse_ns_name(builder, name):
    assert ' ' kwenye name
    parts = name.split(' ')
    intern = builder._intern_setdefault
    ikiwa len(parts) == 3:
        uri, localname, prefix = parts
        prefix = intern(prefix, prefix)
        qname = "%s:%s" % (prefix, localname)
        qname = intern(qname, qname)
        localname = intern(localname, localname)
    lasivyo len(parts) == 2:
        uri, localname = parts
        prefix = EMPTY_PREFIX
        qname = localname = intern(localname, localname)
    isipokua:
        ashiria ValueError("Unsupported syntax: spaces kwenye URIs sio supported: %r" % name)
    rudisha intern(uri, uri), localname, prefix, qname


kundi ExpatBuilder:
    """Document builder that uses Expat to build a ParsedXML.DOM document
    instance."""

    eleza __init__(self, options=Tupu):
        ikiwa options ni Tupu:
            options = xmlbuilder.Options()
        self._options = options
        ikiwa self._options.filter ni sio Tupu:
            self._filter = FilterVisibilityController(self._options.filter)
        isipokua:
            self._filter = Tupu
            # This *really* doesn't do anything kwenye this case, so
            # override it ukijumuisha something fast & minimal.
            self._finish_start_element = id
        self._parser = Tupu
        self.reset()

    eleza createParser(self):
        """Create a new parser object."""
        rudisha expat.ParserCreate()

    eleza getParser(self):
        """Return the parser object, creating a new one ikiwa needed."""
        ikiwa sio self._parser:
            self._parser = self.createParser()
            self._intern_setdefault = self._parser.intern.setdefault
            self._parser.buffer_text = Kweli
            self._parser.ordered_attributes = Kweli
            self._parser.specified_attributes = Kweli
            self.install(self._parser)
        rudisha self._parser

    eleza reset(self):
        """Free all data structures used during DOM construction."""
        self.document = theDOMImplementation.createDocument(
            EMPTY_NAMESPACE, Tupu, Tupu)
        self.curNode = self.document
        self._elem_info = self.document._elem_info
        self._cdata = Uongo

    eleza install(self, parser):
        """Install the callbacks needed to build the DOM into the parser."""
        # This creates circular references!
        parser.StartDoctypeDeclHandler = self.start_doctype_decl_handler
        parser.StartElementHandler = self.first_element_handler
        parser.EndElementHandler = self.end_element_handler
        parser.ProcessingInstructionHandler = self.pi_handler
        ikiwa self._options.entities:
            parser.EntityDeclHandler = self.entity_decl_handler
        parser.NotationDeclHandler = self.notation_decl_handler
        ikiwa self._options.comments:
            parser.CommentHandler = self.comment_handler
        ikiwa self._options.cdata_sections:
            parser.StartCdataSectionHandler = self.start_cdata_section_handler
            parser.EndCdataSectionHandler = self.end_cdata_section_handler
            parser.CharacterDataHandler = self.character_data_handler_cdata
        isipokua:
            parser.CharacterDataHandler = self.character_data_handler
        parser.ExternalEntityRefHandler = self.external_entity_ref_handler
        parser.XmlDeclHandler = self.xml_decl_handler
        parser.ElementDeclHandler = self.element_decl_handler
        parser.AttlistDeclHandler = self.attlist_decl_handler

    eleza parseFile(self, file):
        """Parse a document kutoka a file object, rudishaing the document
        node."""
        parser = self.getParser()
        first_buffer = Kweli
        jaribu:
            wakati 1:
                buffer = file.read(16*1024)
                ikiwa sio buffer:
                    koma
                parser.Parse(buffer, 0)
                ikiwa first_buffer na self.document.documentElement:
                    self._setup_subset(buffer)
                first_buffer = Uongo
            parser.Parse("", Kweli)
        tatizo ParseEscape:
            pita
        doc = self.document
        self.reset()
        self._parser = Tupu
        rudisha doc

    eleza parseString(self, string):
        """Parse a document kutoka a string, rudishaing the document node."""
        parser = self.getParser()
        jaribu:
            parser.Parse(string, Kweli)
            self._setup_subset(string)
        tatizo ParseEscape:
            pita
        doc = self.document
        self.reset()
        self._parser = Tupu
        rudisha doc

    eleza _setup_subset(self, buffer):
        """Load the internal subset ikiwa there might be one."""
        ikiwa self.document.doctype:
            extractor = InternalSubsetExtractor()
            extractor.parseString(buffer)
            subset = extractor.getSubset()
            self.document.doctype.internalSubset = subset

    eleza start_doctype_decl_handler(self, doctypeName, systemId, publicId,
                                   has_internal_subset):
        doctype = self.document.implementation.createDocumentType(
            doctypeName, publicId, systemId)
        doctype.ownerDocument = self.document
        _append_child(self.document, doctype)
        self.document.doctype = doctype
        ikiwa self._filter na self._filter.acceptNode(doctype) == FILTER_REJECT:
            self.document.doctype = Tupu
            toa self.document.childNodes[-1]
            doctype = Tupu
            self._parser.EntityDeclHandler = Tupu
            self._parser.NotationDeclHandler = Tupu
        ikiwa has_internal_subset:
            ikiwa doctype ni sio Tupu:
                doctype.entities._seq = []
                doctype.notations._seq = []
            self._parser.CommentHandler = Tupu
            self._parser.ProcessingInstructionHandler = Tupu
            self._parser.EndDoctypeDeclHandler = self.end_doctype_decl_handler

    eleza end_doctype_decl_handler(self):
        ikiwa self._options.comments:
            self._parser.CommentHandler = self.comment_handler
        self._parser.ProcessingInstructionHandler = self.pi_handler
        ikiwa sio (self._elem_info ama self._filter):
            self._finish_end_element = id

    eleza pi_handler(self, target, data):
        node = self.document.createProcessingInstruction(target, data)
        _append_child(self.curNode, node)
        ikiwa self._filter na self._filter.acceptNode(node) == FILTER_REJECT:
            self.curNode.removeChild(node)

    eleza character_data_handler_cdata(self, data):
        childNodes = self.curNode.childNodes
        ikiwa self._cdata:
            ikiwa (  self._cdata_endelea
                  na childNodes[-1].nodeType == CDATA_SECTION_NODE):
                childNodes[-1].appendData(data)
                rudisha
            node = self.document.createCDATASection(data)
            self._cdata_endelea = Kweli
        lasivyo childNodes na childNodes[-1].nodeType == TEXT_NODE:
            node = childNodes[-1]
            value = node.data + data
            node.data = value
            rudisha
        isipokua:
            node = minidom.Text()
            node.data = data
            node.ownerDocument = self.document
        _append_child(self.curNode, node)

    eleza character_data_handler(self, data):
        childNodes = self.curNode.childNodes
        ikiwa childNodes na childNodes[-1].nodeType == TEXT_NODE:
            node = childNodes[-1]
            node.data = node.data + data
            rudisha
        node = minidom.Text()
        node.data = node.data + data
        node.ownerDocument = self.document
        _append_child(self.curNode, node)

    eleza entity_decl_handler(self, entityName, is_parameter_entity, value,
                            base, systemId, publicId, notationName):
        ikiwa is_parameter_entity:
            # we don't care about parameter entities kila the DOM
            rudisha
        ikiwa sio self._options.entities:
            rudisha
        node = self.document._create_entity(entityName, publicId,
                                            systemId, notationName)
        ikiwa value ni sio Tupu:
            # internal entity
            # node *should* be readonly, but we'll cheat
            child = self.document.createTextNode(value)
            node.childNodes.append(child)
        self.document.doctype.entities._seq.append(node)
        ikiwa self._filter na self._filter.acceptNode(node) == FILTER_REJECT:
            toa self.document.doctype.entities._seq[-1]

    eleza notation_decl_handler(self, notationName, base, systemId, publicId):
        node = self.document._create_notation(notationName, publicId, systemId)
        self.document.doctype.notations._seq.append(node)
        ikiwa self._filter na self._filter.acceptNode(node) == FILTER_ACCEPT:
            toa self.document.doctype.notations._seq[-1]

    eleza comment_handler(self, data):
        node = self.document.createComment(data)
        _append_child(self.curNode, node)
        ikiwa self._filter na self._filter.acceptNode(node) == FILTER_REJECT:
            self.curNode.removeChild(node)

    eleza start_cdata_section_handler(self):
        self._cdata = Kweli
        self._cdata_endelea = Uongo

    eleza end_cdata_section_handler(self):
        self._cdata = Uongo
        self._cdata_endelea = Uongo

    eleza external_entity_ref_handler(self, context, base, systemId, publicId):
        rudisha 1

    eleza first_element_handler(self, name, attributes):
        ikiwa self._filter ni Tupu na sio self._elem_info:
            self._finish_end_element = id
        self.getParser().StartElementHandler = self.start_element_handler
        self.start_element_handler(name, attributes)

    eleza start_element_handler(self, name, attributes):
        node = self.document.createElement(name)
        _append_child(self.curNode, node)
        self.curNode = node

        ikiwa attributes:
            kila i kwenye range(0, len(attributes), 2):
                a = minidom.Attr(attributes[i], EMPTY_NAMESPACE,
                                 Tupu, EMPTY_PREFIX)
                value = attributes[i+1]
                a.value = value
                a.ownerDocument = self.document
                _set_attribute_node(node, a)

        ikiwa node ni sio self.document.documentElement:
            self._finish_start_element(node)

    eleza _finish_start_element(self, node):
        ikiwa self._filter:
            # To be general, we'd have to call isSameNode(), but this
            # ni sufficient kila minidom:
            ikiwa node ni self.document.documentElement:
                rudisha
            filt = self._filter.startContainer(node)
            ikiwa filt == FILTER_REJECT:
                # ignore this node & all descendents
                Rejecter(self)
            lasivyo filt == FILTER_SKIP:
                # ignore this node, but make it's children become
                # children of the parent node
                Skipper(self)
            isipokua:
                rudisha
            self.curNode = node.parentNode
            node.parentNode.removeChild(node)
            node.unlink()

    # If this ever changes, Namespaces.end_element_handler() needs to
    # be changed to match.
    #
    eleza end_element_handler(self, name):
        curNode = self.curNode
        self.curNode = curNode.parentNode
        self._finish_end_element(curNode)

    eleza _finish_end_element(self, curNode):
        info = self._elem_info.get(curNode.tagName)
        ikiwa info:
            self._handle_white_text_nodes(curNode, info)
        ikiwa self._filter:
            ikiwa curNode ni self.document.documentElement:
                rudisha
            ikiwa self._filter.acceptNode(curNode) == FILTER_REJECT:
                self.curNode.removeChild(curNode)
                curNode.unlink()

    eleza _handle_white_text_nodes(self, node, info):
        ikiwa (self._options.whitespace_in_element_content
            ama sio info.isElementContent()):
            rudisha

        # We have element type information na should remove ignorable
        # whitespace; identify kila text nodes which contain only
        # whitespace.
        L = []
        kila child kwenye node.childNodes:
            ikiwa child.nodeType == TEXT_NODE na sio child.data.strip():
                L.append(child)

        # Remove ignorable whitespace kutoka the tree.
        kila child kwenye L:
            node.removeChild(child)

    eleza element_decl_handler(self, name, model):
        info = self._elem_info.get(name)
        ikiwa info ni Tupu:
            self._elem_info[name] = ElementInfo(name, model)
        isipokua:
            assert info._motoa ni Tupu
            info._motoa = model

    eleza attlist_decl_handler(self, elem, name, type, default, required):
        info = self._elem_info.get(elem)
        ikiwa info ni Tupu:
            info = ElementInfo(elem)
            self._elem_info[elem] = info
        info._attr_info.append(
            [Tupu, name, Tupu, Tupu, default, 0, type, required])

    eleza xml_decl_handler(self, version, encoding, standalone):
        self.document.version = version
        self.document.encoding = encoding
        # This ni still a little ugly, thanks to the pyexpat API. ;-(
        ikiwa standalone >= 0:
            ikiwa standalone:
                self.document.standalone = Kweli
            isipokua:
                self.document.standalone = Uongo


# Don't include FILTER_INTERRUPT, since that's checked separately
# where allowed.
_ALLOWED_FILTER_RETURNS = (FILTER_ACCEPT, FILTER_REJECT, FILTER_SKIP)

kundi FilterVisibilityController(object):
    """Wrapper around a DOMBuilderFilter which implements the checks
    to make the whatToShow filter attribute work."""

    __slots__ = 'filter',

    eleza __init__(self, filter):
        self.filter = filter

    eleza startContainer(self, node):
        mask = self._nodetype_mask[node.nodeType]
        ikiwa self.filter.whatToShow & mask:
            val = self.filter.startContainer(node)
            ikiwa val == FILTER_INTERRUPT:
                ashiria ParseEscape
            ikiwa val haiko kwenye _ALLOWED_FILTER_RETURNS:
                ashiria ValueError(
                      "startContainer() rudishaed illegal value: " + repr(val))
            rudisha val
        isipokua:
            rudisha FILTER_ACCEPT

    eleza acceptNode(self, node):
        mask = self._nodetype_mask[node.nodeType]
        ikiwa self.filter.whatToShow & mask:
            val = self.filter.acceptNode(node)
            ikiwa val == FILTER_INTERRUPT:
                ashiria ParseEscape
            ikiwa val == FILTER_SKIP:
                # move all child nodes to the parent, na remove this node
                parent = node.parentNode
                kila child kwenye node.childNodes[:]:
                    parent.appendChild(child)
                # node ni handled by the caller
                rudisha FILTER_REJECT
            ikiwa val haiko kwenye _ALLOWED_FILTER_RETURNS:
                ashiria ValueError(
                      "acceptNode() rudishaed illegal value: " + repr(val))
            rudisha val
        isipokua:
            rudisha FILTER_ACCEPT

    _nodetype_mask = {
        Node.ELEMENT_NODE:                NodeFilter.SHOW_ELEMENT,
        Node.ATTRIBUTE_NODE:              NodeFilter.SHOW_ATTRIBUTE,
        Node.TEXT_NODE:                   NodeFilter.SHOW_TEXT,
        Node.CDATA_SECTION_NODE:          NodeFilter.SHOW_CDATA_SECTION,
        Node.ENTITY_REFERENCE_NODE:       NodeFilter.SHOW_ENTITY_REFERENCE,
        Node.ENTITY_NODE:                 NodeFilter.SHOW_ENTITY,
        Node.PROCESSING_INSTRUCTION_NODE: NodeFilter.SHOW_PROCESSING_INSTRUCTION,
        Node.COMMENT_NODE:                NodeFilter.SHOW_COMMENT,
        Node.DOCUMENT_NODE:               NodeFilter.SHOW_DOCUMENT,
        Node.DOCUMENT_TYPE_NODE:          NodeFilter.SHOW_DOCUMENT_TYPE,
        Node.DOCUMENT_FRAGMENT_NODE:      NodeFilter.SHOW_DOCUMENT_FRAGMENT,
        Node.NOTATION_NODE:               NodeFilter.SHOW_NOTATION,
        }


kundi FilterCrutch(object):
    __slots__ = '_builder', '_level', '_old_start', '_old_end'

    eleza __init__(self, builder):
        self._level = 0
        self._builder = builder
        parser = builder._parser
        self._old_start = parser.StartElementHandler
        self._old_end = parser.EndElementHandler
        parser.StartElementHandler = self.start_element_handler
        parser.EndElementHandler = self.end_element_handler

kundi Rejecter(FilterCrutch):
    __slots__ = ()

    eleza __init__(self, builder):
        FilterCrutch.__init__(self, builder)
        parser = builder._parser
        kila name kwenye ("ProcessingInstructionHandler",
                     "CommentHandler",
                     "CharacterDataHandler",
                     "StartCdataSectionHandler",
                     "EndCdataSectionHandler",
                     "ExternalEntityRefHandler",
                     ):
            setattr(parser, name, Tupu)

    eleza start_element_handler(self, *args):
        self._level = self._level + 1

    eleza end_element_handler(self, *args):
        ikiwa self._level == 0:
            # restore the old handlers
            parser = self._builder._parser
            self._builder.install(parser)
            parser.StartElementHandler = self._old_start
            parser.EndElementHandler = self._old_end
        isipokua:
            self._level = self._level - 1

kundi Skipper(FilterCrutch):
    __slots__ = ()

    eleza start_element_handler(self, *args):
        node = self._builder.curNode
        self._old_start(*args)
        ikiwa self._builder.curNode ni sio node:
            self._level = self._level + 1

    eleza end_element_handler(self, *args):
        ikiwa self._level == 0:
            # We're popping back out of the node we're skipping, so we
            # shouldn't need to do anything but reset the handlers.
            self._builder._parser.StartElementHandler = self._old_start
            self._builder._parser.EndElementHandler = self._old_end
            self._builder = Tupu
        isipokua:
            self._level = self._level - 1
            self._old_end(*args)


# framework document used by the fragment builder.
# Takes a string kila the doctype, subset string, na namespace attrs string.

_FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID = \
    "http://xml.python.org/entities/fragment-builder/internal"

_FRAGMENT_BUILDER_TEMPLATE = (
    '''\
<!DOCTYPE wrapper
  %%s [
  <!ENTITY fragment-builder-internal
    SYSTEM "%s">
%%s
]>
<wrapper %%s
>&fragment-builder-internal;</wrapper>'''
    % _FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID)


kundi FragmentBuilder(ExpatBuilder):
    """Builder which constructs document fragments given XML source
    text na a context node.

    The context node ni expected to provide information about the
    namespace declarations which are kwenye scope at the start of the
    fragment.
    """

    eleza __init__(self, context, options=Tupu):
        ikiwa context.nodeType == DOCUMENT_NODE:
            self.originalDocument = context
            self.context = context
        isipokua:
            self.originalDocument = context.ownerDocument
            self.context = context
        ExpatBuilder.__init__(self, options)

    eleza reset(self):
        ExpatBuilder.reset(self)
        self.fragment = Tupu

    eleza parseFile(self, file):
        """Parse a document fragment kutoka a file object, rudishaing the
        fragment node."""
        rudisha self.parseString(file.read())

    eleza parseString(self, string):
        """Parse a document fragment kutoka a string, rudishaing the
        fragment node."""
        self._source = string
        parser = self.getParser()
        doctype = self.originalDocument.doctype
        ident = ""
        ikiwa doctype:
            subset = doctype.internalSubset ama self._getDeclarations()
            ikiwa doctype.publicId:
                ident = ('PUBLIC "%s" "%s"'
                         % (doctype.publicId, doctype.systemId))
            lasivyo doctype.systemId:
                ident = 'SYSTEM "%s"' % doctype.systemId
        isipokua:
            subset = ""
        nsattrs = self._getNSattrs() # get ns decls kutoka node's ancestors
        document = _FRAGMENT_BUILDER_TEMPLATE % (ident, subset, nsattrs)
        jaribu:
            parser.Parse(document, 1)
        tatizo:
            self.reset()
            ashiria
        fragment = self.fragment
        self.reset()
##         self._parser = Tupu
        rudisha fragment

    eleza _getDeclarations(self):
        """Re-create the internal subset kutoka the DocumentType node.

        This ni only needed ikiwa we don't already have the
        internalSubset kama a string.
        """
        doctype = self.context.ownerDocument.doctype
        s = ""
        ikiwa doctype:
            kila i kwenye range(doctype.notations.length):
                notation = doctype.notations.item(i)
                ikiwa s:
                    s = s + "\n  "
                s = "%s<!NOTATION %s" % (s, notation.nodeName)
                ikiwa notation.publicId:
                    s = '%s PUBLIC "%s"\n             "%s">' \
                        % (s, notation.publicId, notation.systemId)
                isipokua:
                    s = '%s SYSTEM "%s">' % (s, notation.systemId)
            kila i kwenye range(doctype.entities.length):
                entity = doctype.entities.item(i)
                ikiwa s:
                    s = s + "\n  "
                s = "%s<!ENTITY %s" % (s, entity.nodeName)
                ikiwa entity.publicId:
                    s = '%s PUBLIC "%s"\n             "%s"' \
                        % (s, entity.publicId, entity.systemId)
                lasivyo entity.systemId:
                    s = '%s SYSTEM "%s"' % (s, entity.systemId)
                isipokua:
                    s = '%s "%s"' % (s, entity.firstChild.data)
                ikiwa entity.notationName:
                    s = "%s NOTATION %s" % (s, entity.notationName)
                s = s + ">"
        rudisha s

    eleza _getNSattrs(self):
        rudisha ""

    eleza external_entity_ref_handler(self, context, base, systemId, publicId):
        ikiwa systemId == _FRAGMENT_BUILDER_INTERNAL_SYSTEM_ID:
            # this entref ni the one that we made to put the subtree
            # in; all of our given input ni parsed kwenye here.
            old_document = self.document
            old_cur_node = self.curNode
            parser = self._parser.ExternalEntityParserCreate(context)
            # put the real document back, parse into the fragment to rudisha
            self.document = self.originalDocument
            self.fragment = self.document.createDocumentFragment()
            self.curNode = self.fragment
            jaribu:
                parser.Parse(self._source, 1)
            mwishowe:
                self.curNode = old_cur_node
                self.document = old_document
                self._source = Tupu
            rudisha -1
        isipokua:
            rudisha ExpatBuilder.external_entity_ref_handler(
                self, context, base, systemId, publicId)


kundi Namespaces:
    """Mix-in kundi kila builders; adds support kila namespaces."""

    eleza _initNamespaces(self):
        # list of (prefix, uri) ns declarations.  Namespace attrs are
        # constructed kutoka this na added to the element's attrs.
        self._ns_ordered_prefixes = []

    eleza createParser(self):
        """Create a new namespace-handling parser."""
        parser = expat.ParserCreate(namespace_separator=" ")
        parser.namespace_prefixes = Kweli
        rudisha parser

    eleza install(self, parser):
        """Insert the namespace-handlers onto the parser."""
        ExpatBuilder.install(self, parser)
        ikiwa self._options.namespace_declarations:
            parser.StartNamespaceDeclHandler = (
                self.start_namespace_decl_handler)

    eleza start_namespace_decl_handler(self, prefix, uri):
        """Push this namespace declaration on our storage."""
        self._ns_ordered_prefixes.append((prefix, uri))

    eleza start_element_handler(self, name, attributes):
        ikiwa ' ' kwenye name:
            uri, localname, prefix, qname = _parse_ns_name(self, name)
        isipokua:
            uri = EMPTY_NAMESPACE
            qname = name
            localname = Tupu
            prefix = EMPTY_PREFIX
        node = minidom.Element(qname, uri, prefix, localname)
        node.ownerDocument = self.document
        _append_child(self.curNode, node)
        self.curNode = node

        ikiwa self._ns_ordered_prefixes:
            kila prefix, uri kwenye self._ns_ordered_prefixes:
                ikiwa prefix:
                    a = minidom.Attr(_intern(self, 'xmlns:' + prefix),
                                     XMLNS_NAMESPACE, prefix, "xmlns")
                isipokua:
                    a = minidom.Attr("xmlns", XMLNS_NAMESPACE,
                                     "xmlns", EMPTY_PREFIX)
                a.value = uri
                a.ownerDocument = self.document
                _set_attribute_node(node, a)
            toa self._ns_ordered_prefixes[:]

        ikiwa attributes:
            node._ensure_attributes()
            _attrs = node._attrs
            _attrsNS = node._attrsNS
            kila i kwenye range(0, len(attributes), 2):
                aname = attributes[i]
                value = attributes[i+1]
                ikiwa ' ' kwenye aname:
                    uri, localname, prefix, qname = _parse_ns_name(self, aname)
                    a = minidom.Attr(qname, uri, localname, prefix)
                    _attrs[qname] = a
                    _attrsNS[(uri, localname)] = a
                isipokua:
                    a = minidom.Attr(aname, EMPTY_NAMESPACE,
                                     aname, EMPTY_PREFIX)
                    _attrs[aname] = a
                    _attrsNS[(EMPTY_NAMESPACE, aname)] = a
                a.ownerDocument = self.document
                a.value = value
                a.ownerElement = node

    ikiwa __debug__:
        # This only adds some asserts to the original
        # end_element_handler(), so we only define this when -O ni not
        # used.  If changing one, be sure to check the other to see if
        # it needs to be changed kama well.
        #
        eleza end_element_handler(self, name):
            curNode = self.curNode
            ikiwa ' ' kwenye name:
                uri, localname, prefix, qname = _parse_ns_name(self, name)
                assert (curNode.namespaceURI == uri
                        na curNode.localName == localname
                        na curNode.prefix == prefix), \
                        "element stack messed up! (namespace)"
            isipokua:
                assert curNode.nodeName == name, \
                       "element stack messed up - bad nodeName"
                assert curNode.namespaceURI == EMPTY_NAMESPACE, \
                       "element stack messed up - bad namespaceURI"
            self.curNode = curNode.parentNode
            self._finish_end_element(curNode)


kundi ExpatBuilderNS(Namespaces, ExpatBuilder):
    """Document builder that supports namespaces."""

    eleza reset(self):
        ExpatBuilder.reset(self)
        self._initNamespaces()


kundi FragmentBuilderNS(Namespaces, FragmentBuilder):
    """Fragment builder that supports namespaces."""

    eleza reset(self):
        FragmentBuilder.reset(self)
        self._initNamespaces()

    eleza _getNSattrs(self):
        """Return string of namespace attributes kutoka this element na
        ancestors."""
        # XXX This needs to be re-written to walk the ancestors of the
        # context to build up the namespace information kutoka
        # declarations, elements, na attributes found kwenye context.
        # Otherwise we have to store a bunch more data on the DOM
        # (though that *might* be more reliable -- sio clear).
        attrs = ""
        context = self.context
        L = []
        wakati context:
            ikiwa hasattr(context, '_ns_prefix_uri'):
                kila prefix, uri kwenye context._ns_prefix_uri.items():
                    # add every new NS decl kutoka context to L na attrs string
                    ikiwa prefix kwenye L:
                        endelea
                    L.append(prefix)
                    ikiwa prefix:
                        declname = "xmlns:" + prefix
                    isipokua:
                        declname = "xmlns"
                    ikiwa attrs:
                        attrs = "%s\n    %s='%s'" % (attrs, declname, uri)
                    isipokua:
                        attrs = " %s='%s'" % (declname, uri)
            context = context.parentNode
        rudisha attrs


kundi ParseEscape(Exception):
    """Exception ashiriad to short-circuit parsing kwenye InternalSubsetExtractor."""
    pita

kundi InternalSubsetExtractor(ExpatBuilder):
    """XML processor which can rip out the internal document type subset."""

    subset = Tupu

    eleza getSubset(self):
        """Return the internal subset kama a string."""
        rudisha self.subset

    eleza parseFile(self, file):
        jaribu:
            ExpatBuilder.parseFile(self, file)
        tatizo ParseEscape:
            pita

    eleza parseString(self, string):
        jaribu:
            ExpatBuilder.parseString(self, string)
        tatizo ParseEscape:
            pita

    eleza install(self, parser):
        parser.StartDoctypeDeclHandler = self.start_doctype_decl_handler
        parser.StartElementHandler = self.start_element_handler

    eleza start_doctype_decl_handler(self, name, publicId, systemId,
                                   has_internal_subset):
        ikiwa has_internal_subset:
            parser = self.getParser()
            self.subset = []
            parser.DefaultHandler = self.subset.append
            parser.EndDoctypeDeclHandler = self.end_doctype_decl_handler
        isipokua:
            ashiria ParseEscape()

    eleza end_doctype_decl_handler(self):
        s = ''.join(self.subset).replace('\r\n', '\n').replace('\r', '\n')
        self.subset = s
        ashiria ParseEscape()

    eleza start_element_handler(self, name, attrs):
        ashiria ParseEscape()


eleza parse(file, namespaces=Kweli):
    """Parse a document, rudishaing the resulting Document node.

    'file' may be either a file name ama an open file object.
    """
    ikiwa namespaces:
        builder = ExpatBuilderNS()
    isipokua:
        builder = ExpatBuilder()

    ikiwa isinstance(file, str):
        ukijumuisha open(file, 'rb') kama fp:
            result = builder.parseFile(fp)
    isipokua:
        result = builder.parseFile(file)
    rudisha result


eleza parseString(string, namespaces=Kweli):
    """Parse a document kutoka a string, rudishaing the resulting
    Document node.
    """
    ikiwa namespaces:
        builder = ExpatBuilderNS()
    isipokua:
        builder = ExpatBuilder()
    rudisha builder.parseString(string)


eleza parseFragment(file, context, namespaces=Kweli):
    """Parse a fragment of a document, given the context kutoka which it
    was originally extracted.  context should be the parent of the
    node(s) which are kwenye the fragment.

    'file' may be either a file name ama an open file object.
    """
    ikiwa namespaces:
        builder = FragmentBuilderNS(context)
    isipokua:
        builder = FragmentBuilder(context)

    ikiwa isinstance(file, str):
        ukijumuisha open(file, 'rb') kama fp:
            result = builder.parseFile(fp)
    isipokua:
        result = builder.parseFile(file)
    rudisha result


eleza parseFragmentString(string, context, namespaces=Kweli):
    """Parse a fragment of a document kutoka a string, given the context
    kutoka which it was originally extracted.  context should be the
    parent of the node(s) which are kwenye the fragment.
    """
    ikiwa namespaces:
        builder = FragmentBuilderNS(context)
    isipokua:
        builder = FragmentBuilder(context)
    rudisha builder.parseString(string)


eleza makeBuilder(options):
    """Create a builder based on an Options object."""
    ikiwa options.namespaces:
        rudisha ExpatBuilderNS(options)
    isipokua:
        rudisha ExpatBuilder(options)
