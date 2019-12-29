"""Simple implementation of the Level 1 DOM.

Namespaces na other minor Level 2 features are also supported.

parse("foo.xml")

parseString("<foo><bar/></foo>")

Todo:
=====
 * convenience methods kila getting elements na text.
 * more testing
 * bring some of the writer na linearizer code into conformance ukijumuisha this
        interface
 * SAX 2 namespaces
"""

agiza io
agiza xml.dom

kutoka xml.dom agiza EMPTY_NAMESPACE, EMPTY_PREFIX, XMLNS_NAMESPACE, domreg
kutoka xml.dom.minicompat agiza *
kutoka xml.dom.xmlbuilder agiza DOMImplementationLS, DocumentLS

# This ni used by the ID-cache invalidation checks; the list isn't
# actually complete, since the nodes being checked will never be the
# DOCUMENT_NODE ama DOCUMENT_FRAGMENT_NODE.  (The node being checked is
# the node being added ama removed, sio the node being modified.)
#
_nodeTypes_with_children = (xml.dom.Node.ELEMENT_NODE,
                            xml.dom.Node.ENTITY_REFERENCE_NODE)


kundi Node(xml.dom.Node):
    namespaceURI = Tupu # this ni non-null only kila elements na attributes
    parentNode = Tupu
    ownerDocument = Tupu
    nextSibling = Tupu
    previousSibling = Tupu

    prefix = EMPTY_PREFIX # non-null only kila NS elements na attributes

    eleza __bool__(self):
        rudisha Kweli

    eleza toxml(self, encoding=Tupu):
        rudisha self.toprettyxml("", "", encoding)

    eleza toprettyxml(self, indent="\t", newl="\n", encoding=Tupu):
        ikiwa encoding ni Tupu:
            writer = io.StringIO()
        isipokua:
            writer = io.TextIOWrapper(io.BytesIO(),
                                      encoding=encoding,
                                      errors="xmlcharrefreplace",
                                      newline='\n')
        ikiwa self.nodeType == Node.DOCUMENT_NODE:
            # Can pita encoding only to document, to put it into XML header
            self.writexml(writer, "", indent, newl, encoding)
        isipokua:
            self.writexml(writer, "", indent, newl)
        ikiwa encoding ni Tupu:
            rudisha writer.getvalue()
        isipokua:
            rudisha writer.detach().getvalue()

    eleza hasChildNodes(self):
        rudisha bool(self.childNodes)

    eleza _get_childNodes(self):
        rudisha self.childNodes

    eleza _get_firstChild(self):
        ikiwa self.childNodes:
            rudisha self.childNodes[0]

    eleza _get_lastChild(self):
        ikiwa self.childNodes:
            rudisha self.childNodes[-1]

    eleza insertBefore(self, newChild, refChild):
        ikiwa newChild.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            kila c kwenye tuple(newChild.childNodes):
                self.insertBefore(c, refChild)
            ### The DOM does sio clearly specify what to rudisha kwenye this case
            rudisha newChild
        ikiwa newChild.nodeType haiko kwenye self._child_node_types:
            ashiria xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(newChild), repr(self)))
        ikiwa newChild.parentNode ni sio Tupu:
            newChild.parentNode.removeChild(newChild)
        ikiwa refChild ni Tupu:
            self.appendChild(newChild)
        isipokua:
            jaribu:
                index = self.childNodes.index(refChild)
            tatizo ValueError:
                ashiria xml.dom.NotFoundErr()
            ikiwa newChild.nodeType kwenye _nodeTypes_with_children:
                _clear_id_cache(self)
            self.childNodes.insert(index, newChild)
            newChild.nextSibling = refChild
            refChild.previousSibling = newChild
            ikiwa index:
                node = self.childNodes[index-1]
                node.nextSibling = newChild
                newChild.previousSibling = node
            isipokua:
                newChild.previousSibling = Tupu
            newChild.parentNode = self
        rudisha newChild

    eleza appendChild(self, node):
        ikiwa node.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            kila c kwenye tuple(node.childNodes):
                self.appendChild(c)
            ### The DOM does sio clearly specify what to rudisha kwenye this case
            rudisha node
        ikiwa node.nodeType haiko kwenye self._child_node_types:
            ashiria xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(node), repr(self)))
        lasivyo node.nodeType kwenye _nodeTypes_with_children:
            _clear_id_cache(self)
        ikiwa node.parentNode ni sio Tupu:
            node.parentNode.removeChild(node)
        _append_child(self, node)
        node.nextSibling = Tupu
        rudisha node

    eleza replaceChild(self, newChild, oldChild):
        ikiwa newChild.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            refChild = oldChild.nextSibling
            self.removeChild(oldChild)
            rudisha self.insertBefore(newChild, refChild)
        ikiwa newChild.nodeType haiko kwenye self._child_node_types:
            ashiria xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(newChild), repr(self)))
        ikiwa newChild ni oldChild:
            rudisha
        ikiwa newChild.parentNode ni sio Tupu:
            newChild.parentNode.removeChild(newChild)
        jaribu:
            index = self.childNodes.index(oldChild)
        tatizo ValueError:
            ashiria xml.dom.NotFoundErr()
        self.childNodes[index] = newChild
        newChild.parentNode = self
        oldChild.parentNode = Tupu
        ikiwa (newChild.nodeType kwenye _nodeTypes_with_children
            ama oldChild.nodeType kwenye _nodeTypes_with_children):
            _clear_id_cache(self)
        newChild.nextSibling = oldChild.nextSibling
        newChild.previousSibling = oldChild.previousSibling
        oldChild.nextSibling = Tupu
        oldChild.previousSibling = Tupu
        ikiwa newChild.previousSibling:
            newChild.previousSibling.nextSibling = newChild
        ikiwa newChild.nextSibling:
            newChild.nextSibling.previousSibling = newChild
        rudisha oldChild

    eleza removeChild(self, oldChild):
        jaribu:
            self.childNodes.remove(oldChild)
        tatizo ValueError:
            ashiria xml.dom.NotFoundErr()
        ikiwa oldChild.nextSibling ni sio Tupu:
            oldChild.nextSibling.previousSibling = oldChild.previousSibling
        ikiwa oldChild.previousSibling ni sio Tupu:
            oldChild.previousSibling.nextSibling = oldChild.nextSibling
        oldChild.nextSibling = oldChild.previousSibling = Tupu
        ikiwa oldChild.nodeType kwenye _nodeTypes_with_children:
            _clear_id_cache(self)

        oldChild.parentNode = Tupu
        rudisha oldChild

    eleza normalize(self):
        L = []
        kila child kwenye self.childNodes:
            ikiwa child.nodeType == Node.TEXT_NODE:
                ikiwa sio child.data:
                    # empty text node; discard
                    ikiwa L:
                        L[-1].nextSibling = child.nextSibling
                    ikiwa child.nextSibling:
                        child.nextSibling.previousSibling = child.previousSibling
                    child.unlink()
                lasivyo L na L[-1].nodeType == child.nodeType:
                    # collapse text node
                    node = L[-1]
                    node.data = node.data + child.data
                    node.nextSibling = child.nextSibling
                    ikiwa child.nextSibling:
                        child.nextSibling.previousSibling = node
                    child.unlink()
                isipokua:
                    L.append(child)
            isipokua:
                L.append(child)
                ikiwa child.nodeType == Node.ELEMENT_NODE:
                    child.normalize()
        self.childNodes[:] = L

    eleza cloneNode(self, deep):
        rudisha _clone_node(self, deep, self.ownerDocument ama self)

    eleza isSupported(self, feature, version):
        rudisha self.ownerDocument.implementation.hasFeature(feature, version)

    eleza _get_localName(self):
        # Overridden kwenye Element na Attr where localName can be Non-Null
        rudisha Tupu

    # Node interfaces kutoka Level 3 (WD 9 April 2002)

    eleza isSameNode(self, other):
        rudisha self ni other

    eleza getInterface(self, feature):
        ikiwa self.isSupported(feature, Tupu):
            rudisha self
        isipokua:
            rudisha Tupu

    # The "user data" functions use a dictionary that ni only present
    # ikiwa some user data has been set, so be careful sio to assume it
    # exists.

    eleza getUserData(self, key):
        jaribu:
            rudisha self._user_data[key][0]
        tatizo (AttributeError, KeyError):
            rudisha Tupu

    eleza setUserData(self, key, data, handler):
        old = Tupu
        jaribu:
            d = self._user_data
        tatizo AttributeError:
            d = {}
            self._user_data = d
        ikiwa key kwenye d:
            old = d[key][0]
        ikiwa data ni Tupu:
            # ignore handlers pitaed kila Tupu
            handler = Tupu
            ikiwa old ni sio Tupu:
                toa d[key]
        isipokua:
            d[key] = (data, handler)
        rudisha old

    eleza _call_user_data_handler(self, operation, src, dst):
        ikiwa hasattr(self, "_user_data"):
            kila key, (data, handler) kwenye list(self._user_data.items()):
                ikiwa handler ni sio Tupu:
                    handler.handle(operation, key, data, src, dst)

    # minidom-specific API:

    eleza unlink(self):
        self.parentNode = self.ownerDocument = Tupu
        ikiwa self.childNodes:
            kila child kwenye self.childNodes:
                child.unlink()
            self.childNodes = NodeList()
        self.previousSibling = Tupu
        self.nextSibling = Tupu

    # A Node ni its own context manager, to ensure that an unlink() call occurs.
    # This ni similar to how a file object works.
    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, et, ev, tb):
        self.unlink()

defproperty(Node, "firstChild", doc="First child node, ama Tupu.")
defproperty(Node, "lastChild",  doc="Last child node, ama Tupu.")
defproperty(Node, "localName",  doc="Namespace-local name of this node.")


eleza _append_child(self, node):
    # fast path ukijumuisha less checks; usable by DOM builders ikiwa careful
    childNodes = self.childNodes
    ikiwa childNodes:
        last = childNodes[-1]
        node.previousSibling = last
        last.nextSibling = node
    childNodes.append(node)
    node.parentNode = self

eleza _in_document(node):
    # rudisha Kweli iff node ni part of a document tree
    wakati node ni sio Tupu:
        ikiwa node.nodeType == Node.DOCUMENT_NODE:
            rudisha Kweli
        node = node.parentNode
    rudisha Uongo

eleza _write_data(writer, data):
    "Writes datachars to writer."
    ikiwa data:
        data = data.replace("&", "&amp;").replace("<", "&lt;"). \
                    replace("\"", "&quot;").replace(">", "&gt;")
        writer.write(data)

eleza _get_elements_by_tagName_helper(parent, name, rc):
    kila node kwenye parent.childNodes:
        ikiwa node.nodeType == Node.ELEMENT_NODE na \
            (name == "*" ama node.tagName == name):
            rc.append(node)
        _get_elements_by_tagName_helper(node, name, rc)
    rudisha rc

eleza _get_elements_by_tagName_ns_helper(parent, nsURI, localName, rc):
    kila node kwenye parent.childNodes:
        ikiwa node.nodeType == Node.ELEMENT_NODE:
            ikiwa ((localName == "*" ama node.localName == localName) and
                (nsURI == "*" ama node.namespaceURI == nsURI)):
                rc.append(node)
            _get_elements_by_tagName_ns_helper(node, nsURI, localName, rc)
    rudisha rc

kundi DocumentFragment(Node):
    nodeType = Node.DOCUMENT_FRAGMENT_NODE
    nodeName = "#document-fragment"
    nodeValue = Tupu
    attributes = Tupu
    parentNode = Tupu
    _child_node_types = (Node.ELEMENT_NODE,
                         Node.TEXT_NODE,
                         Node.CDATA_SECTION_NODE,
                         Node.ENTITY_REFERENCE_NODE,
                         Node.PROCESSING_INSTRUCTION_NODE,
                         Node.COMMENT_NODE,
                         Node.NOTATION_NODE)

    eleza __init__(self):
        self.childNodes = NodeList()


kundi Attr(Node):
    __slots__=('_name', '_value', 'namespaceURI',
               '_prefix', 'childNodes', '_localName', 'ownerDocument', 'ownerElement')
    nodeType = Node.ATTRIBUTE_NODE
    attributes = Tupu
    specified = Uongo
    _is_id = Uongo

    _child_node_types = (Node.TEXT_NODE, Node.ENTITY_REFERENCE_NODE)

    eleza __init__(self, qName, namespaceURI=EMPTY_NAMESPACE, localName=Tupu,
                 prefix=Tupu):
        self.ownerElement = Tupu
        self._name = qName
        self.namespaceURI = namespaceURI
        self._prefix = prefix
        self.childNodes = NodeList()

        # Add the single child node that represents the value of the attr
        self.childNodes.append(Text())

        # nodeValue na value are set elsewhere

    eleza _get_localName(self):
        jaribu:
            rudisha self._localName
        tatizo AttributeError:
            rudisha self.nodeName.split(":", 1)[-1]

    eleza _get_specified(self):
        rudisha self.specified

    eleza _get_name(self):
        rudisha self._name

    eleza _set_name(self, value):
        self._name = value
        ikiwa self.ownerElement ni sio Tupu:
            _clear_id_cache(self.ownerElement)

    nodeName = name = property(_get_name, _set_name)

    eleza _get_value(self):
        rudisha self._value

    eleza _set_value(self, value):
        self._value = value
        self.childNodes[0].data = value
        ikiwa self.ownerElement ni sio Tupu:
            _clear_id_cache(self.ownerElement)
        self.childNodes[0].data = value

    nodeValue = value = property(_get_value, _set_value)

    eleza _get_prefix(self):
        rudisha self._prefix

    eleza _set_prefix(self, prefix):
        nsuri = self.namespaceURI
        ikiwa prefix == "xmlns":
            ikiwa nsuri na nsuri != XMLNS_NAMESPACE:
                ashiria xml.dom.NamespaceErr(
                    "illegal use of 'xmlns' prefix kila the wrong namespace")
        self._prefix = prefix
        ikiwa prefix ni Tupu:
            newName = self.localName
        isipokua:
            newName = "%s:%s" % (prefix, self.localName)
        ikiwa self.ownerElement:
            _clear_id_cache(self.ownerElement)
        self.name = newName

    prefix = property(_get_prefix, _set_prefix)

    eleza unlink(self):
        # This implementation does sio call the base implementation
        # since most of that ni sio needed, na the expense of the
        # method call ni sio warranted.  We duplicate the removal of
        # children, but that's all we needed kutoka the base class.
        elem = self.ownerElement
        ikiwa elem ni sio Tupu:
            toa elem._attrs[self.nodeName]
            toa elem._attrsNS[(self.namespaceURI, self.localName)]
            ikiwa self._is_id:
                self._is_id = Uongo
                elem._magic_id_nodes -= 1
                self.ownerDocument._magic_id_count -= 1
        kila child kwenye self.childNodes:
            child.unlink()
        toa self.childNodes[:]

    eleza _get_isId(self):
        ikiwa self._is_id:
            rudisha Kweli
        doc = self.ownerDocument
        elem = self.ownerElement
        ikiwa doc ni Tupu ama elem ni Tupu:
            rudisha Uongo

        info = doc._get_elem_info(elem)
        ikiwa info ni Tupu:
            rudisha Uongo
        ikiwa self.namespaceURI:
            rudisha info.isIdNS(self.namespaceURI, self.localName)
        isipokua:
            rudisha info.isId(self.nodeName)

    eleza _get_schemaType(self):
        doc = self.ownerDocument
        elem = self.ownerElement
        ikiwa doc ni Tupu ama elem ni Tupu:
            rudisha _no_type

        info = doc._get_elem_info(elem)
        ikiwa info ni Tupu:
            rudisha _no_type
        ikiwa self.namespaceURI:
            rudisha info.getAttributeTypeNS(self.namespaceURI, self.localName)
        isipokua:
            rudisha info.getAttributeType(self.nodeName)

defproperty(Attr, "isId",       doc="Kweli ikiwa this attribute ni an ID.")
defproperty(Attr, "localName",  doc="Namespace-local name of this attribute.")
defproperty(Attr, "schemaType", doc="Schema type kila this attribute.")


kundi NamedNodeMap(object):
    """The attribute list ni a transient interface to the underlying
    dictionaries.  Mutations here will change the underlying element's
    dictionary.

    Ordering ni imposed artificially na does sio reflect the order of
    attributes kama found kwenye an input document.
    """

    __slots__ = ('_attrs', '_attrsNS', '_ownerElement')

    eleza __init__(self, attrs, attrsNS, ownerElement):
        self._attrs = attrs
        self._attrsNS = attrsNS
        self._ownerElement = ownerElement

    eleza _get_length(self):
        rudisha len(self._attrs)

    eleza item(self, index):
        jaribu:
            rudisha self[list(self._attrs.keys())[index]]
        tatizo IndexError:
            rudisha Tupu

    eleza items(self):
        L = []
        kila node kwenye self._attrs.values():
            L.append((node.nodeName, node.value))
        rudisha L

    eleza itemsNS(self):
        L = []
        kila node kwenye self._attrs.values():
            L.append(((node.namespaceURI, node.localName), node.value))
        rudisha L

    eleza __contains__(self, key):
        ikiwa isinstance(key, str):
            rudisha key kwenye self._attrs
        isipokua:
            rudisha key kwenye self._attrsNS

    eleza keys(self):
        rudisha self._attrs.keys()

    eleza keysNS(self):
        rudisha self._attrsNS.keys()

    eleza values(self):
        rudisha self._attrs.values()

    eleza get(self, name, value=Tupu):
        rudisha self._attrs.get(name, value)

    __len__ = _get_length

    eleza _cmp(self, other):
        ikiwa self._attrs ni getattr(other, "_attrs", Tupu):
            rudisha 0
        isipokua:
            rudisha (id(self) > id(other)) - (id(self) < id(other))

    eleza __eq__(self, other):
        rudisha self._cmp(other) == 0

    eleza __ge__(self, other):
        rudisha self._cmp(other) >= 0

    eleza __gt__(self, other):
        rudisha self._cmp(other) > 0

    eleza __le__(self, other):
        rudisha self._cmp(other) <= 0

    eleza __lt__(self, other):
        rudisha self._cmp(other) < 0

    eleza __getitem__(self, attname_or_tuple):
        ikiwa isinstance(attname_or_tuple, tuple):
            rudisha self._attrsNS[attname_or_tuple]
        isipokua:
            rudisha self._attrs[attname_or_tuple]

    # same kama set
    eleza __setitem__(self, attname, value):
        ikiwa isinstance(value, str):
            jaribu:
                node = self._attrs[attname]
            tatizo KeyError:
                node = Attr(attname)
                node.ownerDocument = self._ownerElement.ownerDocument
                self.setNamedItem(node)
            node.value = value
        isipokua:
            ikiwa sio isinstance(value, Attr):
                ashiria TypeError("value must be a string ama Attr object")
            node = value
            self.setNamedItem(node)

    eleza getNamedItem(self, name):
        jaribu:
            rudisha self._attrs[name]
        tatizo KeyError:
            rudisha Tupu

    eleza getNamedItemNS(self, namespaceURI, localName):
        jaribu:
            rudisha self._attrsNS[(namespaceURI, localName)]
        tatizo KeyError:
            rudisha Tupu

    eleza removeNamedItem(self, name):
        n = self.getNamedItem(name)
        ikiwa n ni sio Tupu:
            _clear_id_cache(self._ownerElement)
            toa self._attrs[n.nodeName]
            toa self._attrsNS[(n.namespaceURI, n.localName)]
            ikiwa hasattr(n, 'ownerElement'):
                n.ownerElement = Tupu
            rudisha n
        isipokua:
            ashiria xml.dom.NotFoundErr()

    eleza removeNamedItemNS(self, namespaceURI, localName):
        n = self.getNamedItemNS(namespaceURI, localName)
        ikiwa n ni sio Tupu:
            _clear_id_cache(self._ownerElement)
            toa self._attrsNS[(n.namespaceURI, n.localName)]
            toa self._attrs[n.nodeName]
            ikiwa hasattr(n, 'ownerElement'):
                n.ownerElement = Tupu
            rudisha n
        isipokua:
            ashiria xml.dom.NotFoundErr()

    eleza setNamedItem(self, node):
        ikiwa sio isinstance(node, Attr):
            ashiria xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(node), repr(self)))
        old = self._attrs.get(node.name)
        ikiwa old:
            old.unlink()
        self._attrs[node.name] = node
        self._attrsNS[(node.namespaceURI, node.localName)] = node
        node.ownerElement = self._ownerElement
        _clear_id_cache(node.ownerElement)
        rudisha old

    eleza setNamedItemNS(self, node):
        rudisha self.setNamedItem(node)

    eleza __delitem__(self, attname_or_tuple):
        node = self[attname_or_tuple]
        _clear_id_cache(node.ownerElement)
        node.unlink()

    eleza __getstate__(self):
        rudisha self._attrs, self._attrsNS, self._ownerElement

    eleza __setstate__(self, state):
        self._attrs, self._attrsNS, self._ownerElement = state

defproperty(NamedNodeMap, "length",
            doc="Number of nodes kwenye the NamedNodeMap.")

AttributeList = NamedNodeMap


kundi TypeInfo(object):
    __slots__ = 'namespace', 'name'

    eleza __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    eleza __repr__(self):
        ikiwa self.namespace:
            rudisha "<%s %r (kutoka %r)>" % (self.__class__.__name__, self.name,
                                          self.namespace)
        isipokua:
            rudisha "<%s %r>" % (self.__class__.__name__, self.name)

    eleza _get_name(self):
        rudisha self.name

    eleza _get_namespace(self):
        rudisha self.namespace

_no_type = TypeInfo(Tupu, Tupu)

kundi Element(Node):
    __slots__=('ownerDocument', 'parentNode', 'tagName', 'nodeName', 'prefix',
               'namespaceURI', '_localName', 'childNodes', '_attrs', '_attrsNS',
               'nextSibling', 'previousSibling')
    nodeType = Node.ELEMENT_NODE
    nodeValue = Tupu
    schemaType = _no_type

    _magic_id_nodes = 0

    _child_node_types = (Node.ELEMENT_NODE,
                         Node.PROCESSING_INSTRUCTION_NODE,
                         Node.COMMENT_NODE,
                         Node.TEXT_NODE,
                         Node.CDATA_SECTION_NODE,
                         Node.ENTITY_REFERENCE_NODE)

    eleza __init__(self, tagName, namespaceURI=EMPTY_NAMESPACE, prefix=Tupu,
                 localName=Tupu):
        self.parentNode = Tupu
        self.tagName = self.nodeName = tagName
        self.prefix = prefix
        self.namespaceURI = namespaceURI
        self.childNodes = NodeList()
        self.nextSibling = self.previousSibling = Tupu

        # Attribute dictionaries are lazily created
        # attributes are double-indexed:
        #    tagName -> Attribute
        #    URI,localName -> Attribute
        # kwenye the future: consider lazy generation
        # of attribute objects this ni too tricky
        # kila now because of headaches with
        # namespaces.
        self._attrs = Tupu
        self._attrsNS = Tupu

    eleza _ensure_attributes(self):
        ikiwa self._attrs ni Tupu:
            self._attrs = {}
            self._attrsNS = {}

    eleza _get_localName(self):
        jaribu:
            rudisha self._localName
        tatizo AttributeError:
            rudisha self.tagName.split(":", 1)[-1]

    eleza _get_tagName(self):
        rudisha self.tagName

    eleza unlink(self):
        ikiwa self._attrs ni sio Tupu:
            kila attr kwenye list(self._attrs.values()):
                attr.unlink()
        self._attrs = Tupu
        self._attrsNS = Tupu
        Node.unlink(self)

    eleza getAttribute(self, attname):
        ikiwa self._attrs ni Tupu:
            rudisha ""
        jaribu:
            rudisha self._attrs[attname].value
        tatizo KeyError:
            rudisha ""

    eleza getAttributeNS(self, namespaceURI, localName):
        ikiwa self._attrsNS ni Tupu:
            rudisha ""
        jaribu:
            rudisha self._attrsNS[(namespaceURI, localName)].value
        tatizo KeyError:
            rudisha ""

    eleza setAttribute(self, attname, value):
        attr = self.getAttributeNode(attname)
        ikiwa attr ni Tupu:
            attr = Attr(attname)
            attr.value = value # also sets nodeValue
            attr.ownerDocument = self.ownerDocument
            self.setAttributeNode(attr)
        lasivyo value != attr.value:
            attr.value = value
            ikiwa attr.isId:
                _clear_id_cache(self)

    eleza setAttributeNS(self, namespaceURI, qualifiedName, value):
        prefix, localname = _nssplit(qualifiedName)
        attr = self.getAttributeNodeNS(namespaceURI, localname)
        ikiwa attr ni Tupu:
            attr = Attr(qualifiedName, namespaceURI, localname, prefix)
            attr.value = value
            attr.ownerDocument = self.ownerDocument
            self.setAttributeNode(attr)
        isipokua:
            ikiwa value != attr.value:
                attr.value = value
                ikiwa attr.isId:
                    _clear_id_cache(self)
            ikiwa attr.prefix != prefix:
                attr.prefix = prefix
                attr.nodeName = qualifiedName

    eleza getAttributeNode(self, attrname):
        ikiwa self._attrs ni Tupu:
            rudisha Tupu
        rudisha self._attrs.get(attrname)

    eleza getAttributeNodeNS(self, namespaceURI, localName):
        ikiwa self._attrsNS ni Tupu:
            rudisha Tupu
        rudisha self._attrsNS.get((namespaceURI, localName))

    eleza setAttributeNode(self, attr):
        ikiwa attr.ownerElement haiko kwenye (Tupu, self):
            ashiria xml.dom.InuseAttributeErr("attribute node already owned")
        self._ensure_attributes()
        old1 = self._attrs.get(attr.name, Tupu)
        ikiwa old1 ni sio Tupu:
            self.removeAttributeNode(old1)
        old2 = self._attrsNS.get((attr.namespaceURI, attr.localName), Tupu)
        ikiwa old2 ni sio Tupu na old2 ni sio old1:
            self.removeAttributeNode(old2)
        _set_attribute_node(self, attr)

        ikiwa old1 ni sio attr:
            # It might have already been part of this node, kwenye which case
            # it doesn't represent a change, na should sio be rudishaed.
            rudisha old1
        ikiwa old2 ni sio attr:
            rudisha old2

    setAttributeNodeNS = setAttributeNode

    eleza removeAttribute(self, name):
        ikiwa self._attrsNS ni Tupu:
            ashiria xml.dom.NotFoundErr()
        jaribu:
            attr = self._attrs[name]
        tatizo KeyError:
            ashiria xml.dom.NotFoundErr()
        self.removeAttributeNode(attr)

    eleza removeAttributeNS(self, namespaceURI, localName):
        ikiwa self._attrsNS ni Tupu:
            ashiria xml.dom.NotFoundErr()
        jaribu:
            attr = self._attrsNS[(namespaceURI, localName)]
        tatizo KeyError:
            ashiria xml.dom.NotFoundErr()
        self.removeAttributeNode(attr)

    eleza removeAttributeNode(self, node):
        ikiwa node ni Tupu:
            ashiria xml.dom.NotFoundErr()
        jaribu:
            self._attrs[node.name]
        tatizo KeyError:
            ashiria xml.dom.NotFoundErr()
        _clear_id_cache(self)
        node.unlink()
        # Restore this since the node ni still useful na otherwise
        # unlinked
        node.ownerDocument = self.ownerDocument
        rudisha node

    removeAttributeNodeNS = removeAttributeNode

    eleza hasAttribute(self, name):
        ikiwa self._attrs ni Tupu:
            rudisha Uongo
        rudisha name kwenye self._attrs

    eleza hasAttributeNS(self, namespaceURI, localName):
        ikiwa self._attrsNS ni Tupu:
            rudisha Uongo
        rudisha (namespaceURI, localName) kwenye self._attrsNS

    eleza getElementsByTagName(self, name):
        rudisha _get_elements_by_tagName_helper(self, name, NodeList())

    eleza getElementsByTagNameNS(self, namespaceURI, localName):
        rudisha _get_elements_by_tagName_ns_helper(
            self, namespaceURI, localName, NodeList())

    eleza __repr__(self):
        rudisha "<DOM Element: %s at %#x>" % (self.tagName, id(self))

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        # indent = current indentation
        # addindent = indentation to add to higher levels
        # newl = newline string
        writer.write(indent+"<" + self.tagName)

        attrs = self._get_attributes()

        kila a_name kwenye attrs.keys():
            writer.write(" %s=\"" % a_name)
            _write_data(writer, attrs[a_name].value)
            writer.write("\"")
        ikiwa self.childNodes:
            writer.write(">")
            ikiwa (len(self.childNodes) == 1 and
                self.childNodes[0].nodeType kwenye (
                        Node.TEXT_NODE, Node.CDATA_SECTION_NODE)):
                self.childNodes[0].writexml(writer, '', '', '')
            isipokua:
                writer.write(newl)
                kila node kwenye self.childNodes:
                    node.writexml(writer, indent+addindent, addindent, newl)
                writer.write(indent)
            writer.write("</%s>%s" % (self.tagName, newl))
        isipokua:
            writer.write("/>%s"%(newl))

    eleza _get_attributes(self):
        self._ensure_attributes()
        rudisha NamedNodeMap(self._attrs, self._attrsNS, self)

    eleza hasAttributes(self):
        ikiwa self._attrs:
            rudisha Kweli
        isipokua:
            rudisha Uongo

    # DOM Level 3 attributes, based on the 22 Oct 2002 draft

    eleza setIdAttribute(self, name):
        idAttr = self.getAttributeNode(name)
        self.setIdAttributeNode(idAttr)

    eleza setIdAttributeNS(self, namespaceURI, localName):
        idAttr = self.getAttributeNodeNS(namespaceURI, localName)
        self.setIdAttributeNode(idAttr)

    eleza setIdAttributeNode(self, idAttr):
        ikiwa idAttr ni Tupu ama sio self.isSameNode(idAttr.ownerElement):
            ashiria xml.dom.NotFoundErr()
        ikiwa _get_containing_entref(self) ni sio Tupu:
            ashiria xml.dom.NoModificationAllowedErr()
        ikiwa sio idAttr._is_id:
            idAttr._is_id = Kweli
            self._magic_id_nodes += 1
            self.ownerDocument._magic_id_count += 1
            _clear_id_cache(self)

defproperty(Element, "attributes",
            doc="NamedNodeMap of attributes on the element.")
defproperty(Element, "localName",
            doc="Namespace-local name of this element.")


eleza _set_attribute_node(element, attr):
    _clear_id_cache(element)
    element._ensure_attributes()
    element._attrs[attr.name] = attr
    element._attrsNS[(attr.namespaceURI, attr.localName)] = attr

    # This creates a circular reference, but Element.unlink()
    # komas the cycle since the references to the attribute
    # dictionaries are tossed.
    attr.ownerElement = element

kundi Childless:
    """Mixin that makes childless-ness easy to implement na avoids
    the complexity of the Node methods that deal ukijumuisha children.
    """
    __slots__ = ()

    attributes = Tupu
    childNodes = EmptyNodeList()
    firstChild = Tupu
    lastChild = Tupu

    eleza _get_firstChild(self):
        rudisha Tupu

    eleza _get_lastChild(self):
        rudisha Tupu

    eleza appendChild(self, node):
        ashiria xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes cannot have children")

    eleza hasChildNodes(self):
        rudisha Uongo

    eleza insertBefore(self, newChild, refChild):
        ashiria xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes do sio have children")

    eleza removeChild(self, oldChild):
        ashiria xml.dom.NotFoundErr(
            self.nodeName + " nodes do sio have children")

    eleza normalize(self):
        # For childless nodes, normalize() has nothing to do.
        pita

    eleza replaceChild(self, newChild, oldChild):
        ashiria xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes do sio have children")


kundi ProcessingInstruction(Childless, Node):
    nodeType = Node.PROCESSING_INSTRUCTION_NODE
    __slots__ = ('target', 'data')

    eleza __init__(self, target, data):
        self.target = target
        self.data = data

    # nodeValue ni an alias kila data
    eleza _get_nodeValue(self):
        rudisha self.data
    eleza _set_nodeValue(self, value):
        self.data = value
    nodeValue = property(_get_nodeValue, _set_nodeValue)

    # nodeName ni an alias kila target
    eleza _get_nodeName(self):
        rudisha self.target
    eleza _set_nodeName(self, value):
        self.target = value
    nodeName = property(_get_nodeName, _set_nodeName)

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        writer.write("%s<?%s %s?>%s" % (indent,self.target, self.data, newl))


kundi CharacterData(Childless, Node):
    __slots__=('_data', 'ownerDocument','parentNode', 'previousSibling', 'nextSibling')

    eleza __init__(self):
        self.ownerDocument = self.parentNode = Tupu
        self.previousSibling = self.nextSibling = Tupu
        self._data = ''
        Node.__init__(self)

    eleza _get_length(self):
        rudisha len(self.data)
    __len__ = _get_length

    eleza _get_data(self):
        rudisha self._data
    eleza _set_data(self, data):
        self._data = data

    data = nodeValue = property(_get_data, _set_data)

    eleza __repr__(self):
        data = self.data
        ikiwa len(data) > 10:
            dotdotdot = "..."
        isipokua:
            dotdotdot = ""
        rudisha '<DOM %s node "%r%s">' % (
            self.__class__.__name__, data[0:10], dotdotdot)

    eleza substringData(self, offset, count):
        ikiwa offset < 0:
            ashiria xml.dom.IndexSizeErr("offset cannot be negative")
        ikiwa offset >= len(self.data):
            ashiria xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        ikiwa count < 0:
            ashiria xml.dom.IndexSizeErr("count cannot be negative")
        rudisha self.data[offset:offset+count]

    eleza appendData(self, arg):
        self.data = self.data + arg

    eleza insertData(self, offset, arg):
        ikiwa offset < 0:
            ashiria xml.dom.IndexSizeErr("offset cannot be negative")
        ikiwa offset >= len(self.data):
            ashiria xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        ikiwa arg:
            self.data = "%s%s%s" % (
                self.data[:offset], arg, self.data[offset:])

    eleza deleteData(self, offset, count):
        ikiwa offset < 0:
            ashiria xml.dom.IndexSizeErr("offset cannot be negative")
        ikiwa offset >= len(self.data):
            ashiria xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        ikiwa count < 0:
            ashiria xml.dom.IndexSizeErr("count cannot be negative")
        ikiwa count:
            self.data = self.data[:offset] + self.data[offset+count:]

    eleza replaceData(self, offset, count, arg):
        ikiwa offset < 0:
            ashiria xml.dom.IndexSizeErr("offset cannot be negative")
        ikiwa offset >= len(self.data):
            ashiria xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        ikiwa count < 0:
            ashiria xml.dom.IndexSizeErr("count cannot be negative")
        ikiwa count:
            self.data = "%s%s%s" % (
                self.data[:offset], arg, self.data[offset+count:])

defproperty(CharacterData, "length", doc="Length of the string data.")


kundi Text(CharacterData):
    __slots__ = ()

    nodeType = Node.TEXT_NODE
    nodeName = "#text"
    attributes = Tupu

    eleza splitText(self, offset):
        ikiwa offset < 0 ama offset > len(self.data):
            ashiria xml.dom.IndexSizeErr("illegal offset value")
        newText = self.__class__()
        newText.data = self.data[offset:]
        newText.ownerDocument = self.ownerDocument
        next = self.nextSibling
        ikiwa self.parentNode na self kwenye self.parentNode.childNodes:
            ikiwa next ni Tupu:
                self.parentNode.appendChild(newText)
            isipokua:
                self.parentNode.insertBefore(newText, next)
        self.data = self.data[:offset]
        rudisha newText

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        _write_data(writer, "%s%s%s" % (indent, self.data, newl))

    # DOM Level 3 (WD 9 April 2002)

    eleza _get_wholeText(self):
        L = [self.data]
        n = self.previousSibling
        wakati n ni sio Tupu:
            ikiwa n.nodeType kwenye (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                L.insert(0, n.data)
                n = n.previousSibling
            isipokua:
                koma
        n = self.nextSibling
        wakati n ni sio Tupu:
            ikiwa n.nodeType kwenye (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                L.append(n.data)
                n = n.nextSibling
            isipokua:
                koma
        rudisha ''.join(L)

    eleza replaceWholeText(self, content):
        # XXX This needs to be seriously changed ikiwa minidom ever
        # supports EntityReference nodes.
        parent = self.parentNode
        n = self.previousSibling
        wakati n ni sio Tupu:
            ikiwa n.nodeType kwenye (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                next = n.previousSibling
                parent.removeChild(n)
                n = next
            isipokua:
                koma
        n = self.nextSibling
        ikiwa sio content:
            parent.removeChild(self)
        wakati n ni sio Tupu:
            ikiwa n.nodeType kwenye (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                next = n.nextSibling
                parent.removeChild(n)
                n = next
            isipokua:
                koma
        ikiwa content:
            self.data = content
            rudisha self
        isipokua:
            rudisha Tupu

    eleza _get_isWhitespaceInElementContent(self):
        ikiwa self.data.strip():
            rudisha Uongo
        elem = _get_containing_element(self)
        ikiwa elem ni Tupu:
            rudisha Uongo
        info = self.ownerDocument._get_elem_info(elem)
        ikiwa info ni Tupu:
            rudisha Uongo
        isipokua:
            rudisha info.isElementContent()

defproperty(Text, "isWhitespaceInElementContent",
            doc="Kweli iff this text node contains only whitespace"
                " na ni kwenye element content.")
defproperty(Text, "wholeText",
            doc="The text of all logically-adjacent text nodes.")


eleza _get_containing_element(node):
    c = node.parentNode
    wakati c ni sio Tupu:
        ikiwa c.nodeType == Node.ELEMENT_NODE:
            rudisha c
        c = c.parentNode
    rudisha Tupu

eleza _get_containing_entref(node):
    c = node.parentNode
    wakati c ni sio Tupu:
        ikiwa c.nodeType == Node.ENTITY_REFERENCE_NODE:
            rudisha c
        c = c.parentNode
    rudisha Tupu


kundi Comment(CharacterData):
    nodeType = Node.COMMENT_NODE
    nodeName = "#comment"

    eleza __init__(self, data):
        CharacterData.__init__(self)
        self._data = data

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        ikiwa "--" kwenye self.data:
            ashiria ValueError("'--' ni sio allowed kwenye a comment node")
        writer.write("%s<!--%s-->%s" % (indent, self.data, newl))


kundi CDATASection(Text):
    __slots__ = ()

    nodeType = Node.CDATA_SECTION_NODE
    nodeName = "#cdata-section"

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        ikiwa self.data.find("]]>") >= 0:
            ashiria ValueError("']]>' sio allowed kwenye a CDATA section")
        writer.write("<![CDATA[%s]]>" % self.data)


kundi ReadOnlySequentialNamedNodeMap(object):
    __slots__ = '_seq',

    eleza __init__(self, seq=()):
        # seq should be a list ama tuple
        self._seq = seq

    eleza __len__(self):
        rudisha len(self._seq)

    eleza _get_length(self):
        rudisha len(self._seq)

    eleza getNamedItem(self, name):
        kila n kwenye self._seq:
            ikiwa n.nodeName == name:
                rudisha n

    eleza getNamedItemNS(self, namespaceURI, localName):
        kila n kwenye self._seq:
            ikiwa n.namespaceURI == namespaceURI na n.localName == localName:
                rudisha n

    eleza __getitem__(self, name_or_tuple):
        ikiwa isinstance(name_or_tuple, tuple):
            node = self.getNamedItemNS(*name_or_tuple)
        isipokua:
            node = self.getNamedItem(name_or_tuple)
        ikiwa node ni Tupu:
            ashiria KeyError(name_or_tuple)
        rudisha node

    eleza item(self, index):
        ikiwa index < 0:
            rudisha Tupu
        jaribu:
            rudisha self._seq[index]
        tatizo IndexError:
            rudisha Tupu

    eleza removeNamedItem(self, name):
        ashiria xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance ni read-only")

    eleza removeNamedItemNS(self, namespaceURI, localName):
        ashiria xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance ni read-only")

    eleza setNamedItem(self, node):
        ashiria xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance ni read-only")

    eleza setNamedItemNS(self, node):
        ashiria xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance ni read-only")

    eleza __getstate__(self):
        rudisha [self._seq]

    eleza __setstate__(self, state):
        self._seq = state[0]

defproperty(ReadOnlySequentialNamedNodeMap, "length",
            doc="Number of entries kwenye the NamedNodeMap.")


kundi Identified:
    """Mix-in kundi that supports the publicId na systemId attributes."""

    __slots__ = 'publicId', 'systemId'

    eleza _identified_mixin_init(self, publicId, systemId):
        self.publicId = publicId
        self.systemId = systemId

    eleza _get_publicId(self):
        rudisha self.publicId

    eleza _get_systemId(self):
        rudisha self.systemId

kundi DocumentType(Identified, Childless, Node):
    nodeType = Node.DOCUMENT_TYPE_NODE
    nodeValue = Tupu
    name = Tupu
    publicId = Tupu
    systemId = Tupu
    internalSubset = Tupu

    eleza __init__(self, qualifiedName):
        self.entities = ReadOnlySequentialNamedNodeMap()
        self.notations = ReadOnlySequentialNamedNodeMap()
        ikiwa qualifiedName:
            prefix, localname = _nssplit(qualifiedName)
            self.name = localname
        self.nodeName = self.name

    eleza _get_internalSubset(self):
        rudisha self.internalSubset

    eleza cloneNode(self, deep):
        ikiwa self.ownerDocument ni Tupu:
            # it's ok
            clone = DocumentType(Tupu)
            clone.name = self.name
            clone.nodeName = self.name
            operation = xml.dom.UserDataHandler.NODE_CLONED
            ikiwa deep:
                clone.entities._seq = []
                clone.notations._seq = []
                kila n kwenye self.notations._seq:
                    notation = Notation(n.nodeName, n.publicId, n.systemId)
                    clone.notations._seq.append(notation)
                    n._call_user_data_handler(operation, n, notation)
                kila e kwenye self.entities._seq:
                    entity = Entity(e.nodeName, e.publicId, e.systemId,
                                    e.notationName)
                    entity.actualEncoding = e.actualEncoding
                    entity.encoding = e.encoding
                    entity.version = e.version
                    clone.entities._seq.append(entity)
                    e._call_user_data_handler(operation, e, entity)
            self._call_user_data_handler(operation, self, clone)
            rudisha clone
        isipokua:
            rudisha Tupu

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        writer.write("<!DOCTYPE ")
        writer.write(self.name)
        ikiwa self.publicId:
            writer.write("%s  PUBLIC '%s'%s  '%s'"
                         % (newl, self.publicId, newl, self.systemId))
        lasivyo self.systemId:
            writer.write("%s  SYSTEM '%s'" % (newl, self.systemId))
        ikiwa self.internalSubset ni sio Tupu:
            writer.write(" [")
            writer.write(self.internalSubset)
            writer.write("]")
        writer.write(">"+newl)

kundi Entity(Identified, Node):
    attributes = Tupu
    nodeType = Node.ENTITY_NODE
    nodeValue = Tupu

    actualEncoding = Tupu
    encoding = Tupu
    version = Tupu

    eleza __init__(self, name, publicId, systemId, notation):
        self.nodeName = name
        self.notationName = notation
        self.childNodes = NodeList()
        self._identified_mixin_init(publicId, systemId)

    eleza _get_actualEncoding(self):
        rudisha self.actualEncoding

    eleza _get_encoding(self):
        rudisha self.encoding

    eleza _get_version(self):
        rudisha self.version

    eleza appendChild(self, newChild):
        ashiria xml.dom.HierarchyRequestErr(
            "cannot append children to an entity node")

    eleza insertBefore(self, newChild, refChild):
        ashiria xml.dom.HierarchyRequestErr(
            "cannot insert children below an entity node")

    eleza removeChild(self, oldChild):
        ashiria xml.dom.HierarchyRequestErr(
            "cannot remove children kutoka an entity node")

    eleza replaceChild(self, newChild, oldChild):
        ashiria xml.dom.HierarchyRequestErr(
            "cannot replace children of an entity node")

kundi Notation(Identified, Childless, Node):
    nodeType = Node.NOTATION_NODE
    nodeValue = Tupu

    eleza __init__(self, name, publicId, systemId):
        self.nodeName = name
        self._identified_mixin_init(publicId, systemId)


kundi DOMImplementation(DOMImplementationLS):
    _features = [("core", "1.0"),
                 ("core", "2.0"),
                 ("core", Tupu),
                 ("xml", "1.0"),
                 ("xml", "2.0"),
                 ("xml", Tupu),
                 ("ls-load", "3.0"),
                 ("ls-load", Tupu),
                 ]

    eleza hasFeature(self, feature, version):
        ikiwa version == "":
            version = Tupu
        rudisha (feature.lower(), version) kwenye self._features

    eleza createDocument(self, namespaceURI, qualifiedName, doctype):
        ikiwa doctype na doctype.parentNode ni sio Tupu:
            ashiria xml.dom.WrongDocumentErr(
                "doctype object owned by another DOM tree")
        doc = self._create_document()

        add_root_element = sio (namespaceURI ni Tupu
                                na qualifiedName ni Tupu
                                na doctype ni Tupu)

        ikiwa sio qualifiedName na add_root_element:
            # The spec ni unclear what to ashiria here; SyntaxErr
            # would be the other obvious candidate. Since Xerces ashirias
            # InvalidCharacterErr, na since SyntaxErr ni sio listed
            # kila createDocument, that seems to be the better choice.
            # XXX: need to check kila illegal characters here na in
            # createElement.

            # DOM Level III clears this up when talking about the rudisha value
            # of this function.  If namespaceURI, qName na DocType are
            # Null the document ni rudishaed without a document element
            # Otherwise ikiwa doctype ama namespaceURI are sio Tupu
            # Then we go back to the above problem
            ashiria xml.dom.InvalidCharacterErr("Element ukijumuisha no name")

        ikiwa add_root_element:
            prefix, localname = _nssplit(qualifiedName)
            ikiwa prefix == "xml" \
               na namespaceURI != "http://www.w3.org/XML/1998/namespace":
                ashiria xml.dom.NamespaceErr("illegal use of 'xml' prefix")
            ikiwa prefix na sio namespaceURI:
                ashiria xml.dom.NamespaceErr(
                    "illegal use of prefix without namespaces")
            element = doc.createElementNS(namespaceURI, qualifiedName)
            ikiwa doctype:
                doc.appendChild(doctype)
            doc.appendChild(element)

        ikiwa doctype:
            doctype.parentNode = doctype.ownerDocument = doc

        doc.doctype = doctype
        doc.implementation = self
        rudisha doc

    eleza createDocumentType(self, qualifiedName, publicId, systemId):
        doctype = DocumentType(qualifiedName)
        doctype.publicId = publicId
        doctype.systemId = systemId
        rudisha doctype

    # DOM Level 3 (WD 9 April 2002)

    eleza getInterface(self, feature):
        ikiwa self.hasFeature(feature, Tupu):
            rudisha self
        isipokua:
            rudisha Tupu

    # internal
    eleza _create_document(self):
        rudisha Document()

kundi ElementInfo(object):
    """Object that represents content-motoa information kila an element.

    This implementation ni sio expected to be used kwenye practice; DOM
    builders should provide implementations which do the right thing
    using information available to it.

    """

    __slots__ = 'tagName',

    eleza __init__(self, name):
        self.tagName = name

    eleza getAttributeType(self, aname):
        rudisha _no_type

    eleza getAttributeTypeNS(self, namespaceURI, localName):
        rudisha _no_type

    eleza isElementContent(self):
        rudisha Uongo

    eleza isEmpty(self):
        """Returns true iff this element ni declared to have an EMPTY
        content model."""
        rudisha Uongo

    eleza isId(self, aname):
        """Returns true iff the named attribute ni a DTD-style ID."""
        rudisha Uongo

    eleza isIdNS(self, namespaceURI, localName):
        """Returns true iff the identified attribute ni a DTD-style ID."""
        rudisha Uongo

    eleza __getstate__(self):
        rudisha self.tagName

    eleza __setstate__(self, state):
        self.tagName = state

eleza _clear_id_cache(node):
    ikiwa node.nodeType == Node.DOCUMENT_NODE:
        node._id_cache.clear()
        node._id_search_stack = Tupu
    lasivyo _in_document(node):
        node.ownerDocument._id_cache.clear()
        node.ownerDocument._id_search_stack= Tupu

kundi Document(Node, DocumentLS):
    __slots__ = ('_elem_info', 'doctype',
                 '_id_search_stack', 'childNodes', '_id_cache')
    _child_node_types = (Node.ELEMENT_NODE, Node.PROCESSING_INSTRUCTION_NODE,
                         Node.COMMENT_NODE, Node.DOCUMENT_TYPE_NODE)

    implementation = DOMImplementation()
    nodeType = Node.DOCUMENT_NODE
    nodeName = "#document"
    nodeValue = Tupu
    attributes = Tupu
    parentNode = Tupu
    previousSibling = nextSibling = Tupu


    # Document attributes kutoka Level 3 (WD 9 April 2002)

    actualEncoding = Tupu
    encoding = Tupu
    standalone = Tupu
    version = Tupu
    strictErrorChecking = Uongo
    errorHandler = Tupu
    documentURI = Tupu

    _magic_id_count = 0

    eleza __init__(self):
        self.doctype = Tupu
        self.childNodes = NodeList()
        # mapping of (namespaceURI, localName) -> ElementInfo
        #        na tagName -> ElementInfo
        self._elem_info = {}
        self._id_cache = {}
        self._id_search_stack = Tupu

    eleza _get_elem_info(self, element):
        ikiwa element.namespaceURI:
            key = element.namespaceURI, element.localName
        isipokua:
            key = element.tagName
        rudisha self._elem_info.get(key)

    eleza _get_actualEncoding(self):
        rudisha self.actualEncoding

    eleza _get_doctype(self):
        rudisha self.doctype

    eleza _get_documentURI(self):
        rudisha self.documentURI

    eleza _get_encoding(self):
        rudisha self.encoding

    eleza _get_errorHandler(self):
        rudisha self.errorHandler

    eleza _get_standalone(self):
        rudisha self.standalone

    eleza _get_strictErrorChecking(self):
        rudisha self.strictErrorChecking

    eleza _get_version(self):
        rudisha self.version

    eleza appendChild(self, node):
        ikiwa node.nodeType haiko kwenye self._child_node_types:
            ashiria xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(node), repr(self)))
        ikiwa node.parentNode ni sio Tupu:
            # This needs to be done before the next test since this
            # may *be* the document element, kwenye which case it should
            # end up re-ordered to the end.
            node.parentNode.removeChild(node)

        ikiwa node.nodeType == Node.ELEMENT_NODE \
           na self._get_documentElement():
            ashiria xml.dom.HierarchyRequestErr(
                "two document elements disallowed")
        rudisha Node.appendChild(self, node)

    eleza removeChild(self, oldChild):
        jaribu:
            self.childNodes.remove(oldChild)
        tatizo ValueError:
            ashiria xml.dom.NotFoundErr()
        oldChild.nextSibling = oldChild.previousSibling = Tupu
        oldChild.parentNode = Tupu
        ikiwa self.documentElement ni oldChild:
            self.documentElement = Tupu

        rudisha oldChild

    eleza _get_documentElement(self):
        kila node kwenye self.childNodes:
            ikiwa node.nodeType == Node.ELEMENT_NODE:
                rudisha node

    eleza unlink(self):
        ikiwa self.doctype ni sio Tupu:
            self.doctype.unlink()
            self.doctype = Tupu
        Node.unlink(self)

    eleza cloneNode(self, deep):
        ikiwa sio deep:
            rudisha Tupu
        clone = self.implementation.createDocument(Tupu, Tupu, Tupu)
        clone.encoding = self.encoding
        clone.standalone = self.standalone
        clone.version = self.version
        kila n kwenye self.childNodes:
            childclone = _clone_node(n, deep, clone)
            assert childclone.ownerDocument.isSameNode(clone)
            clone.childNodes.append(childclone)
            ikiwa childclone.nodeType == Node.DOCUMENT_NODE:
                assert clone.documentElement ni Tupu
            lasivyo childclone.nodeType == Node.DOCUMENT_TYPE_NODE:
                assert clone.doctype ni Tupu
                clone.doctype = childclone
            childclone.parentNode = clone
        self._call_user_data_handler(xml.dom.UserDataHandler.NODE_CLONED,
                                     self, clone)
        rudisha clone

    eleza createDocumentFragment(self):
        d = DocumentFragment()
        d.ownerDocument = self
        rudisha d

    eleza createElement(self, tagName):
        e = Element(tagName)
        e.ownerDocument = self
        rudisha e

    eleza createTextNode(self, data):
        ikiwa sio isinstance(data, str):
            ashiria TypeError("node contents must be a string")
        t = Text()
        t.data = data
        t.ownerDocument = self
        rudisha t

    eleza createCDATASection(self, data):
        ikiwa sio isinstance(data, str):
            ashiria TypeError("node contents must be a string")
        c = CDATASection()
        c.data = data
        c.ownerDocument = self
        rudisha c

    eleza createComment(self, data):
        c = Comment(data)
        c.ownerDocument = self
        rudisha c

    eleza createProcessingInstruction(self, target, data):
        p = ProcessingInstruction(target, data)
        p.ownerDocument = self
        rudisha p

    eleza createAttribute(self, qName):
        a = Attr(qName)
        a.ownerDocument = self
        a.value = ""
        rudisha a

    eleza createElementNS(self, namespaceURI, qualifiedName):
        prefix, localName = _nssplit(qualifiedName)
        e = Element(qualifiedName, namespaceURI, prefix)
        e.ownerDocument = self
        rudisha e

    eleza createAttributeNS(self, namespaceURI, qualifiedName):
        prefix, localName = _nssplit(qualifiedName)
        a = Attr(qualifiedName, namespaceURI, localName, prefix)
        a.ownerDocument = self
        a.value = ""
        rudisha a

    # A couple of implementation-specific helpers to create node types
    # sio supported by the W3C DOM specs:

    eleza _create_entity(self, name, publicId, systemId, notationName):
        e = Entity(name, publicId, systemId, notationName)
        e.ownerDocument = self
        rudisha e

    eleza _create_notation(self, name, publicId, systemId):
        n = Notation(name, publicId, systemId)
        n.ownerDocument = self
        rudisha n

    eleza getElementById(self, id):
        ikiwa id kwenye self._id_cache:
            rudisha self._id_cache[id]
        ikiwa sio (self._elem_info ama self._magic_id_count):
            rudisha Tupu

        stack = self._id_search_stack
        ikiwa stack ni Tupu:
            # we never searched before, ama the cache has been cleared
            stack = [self.documentElement]
            self._id_search_stack = stack
        lasivyo sio stack:
            # Previous search was completed na cache ni still valid;
            # no matching node.
            rudisha Tupu

        result = Tupu
        wakati stack:
            node = stack.pop()
            # add child elements to stack kila endelead searching
            stack.extend([child kila child kwenye node.childNodes
                          ikiwa child.nodeType kwenye _nodeTypes_with_children])
            # check this node
            info = self._get_elem_info(node)
            ikiwa info:
                # We have to process all ID attributes before
                # rudishaing kwenye order to get all the attributes set to
                # be IDs using Element.setIdAttribute*().
                kila attr kwenye node.attributes.values():
                    ikiwa attr.namespaceURI:
                        ikiwa info.isIdNS(attr.namespaceURI, attr.localName):
                            self._id_cache[attr.value] = node
                            ikiwa attr.value == id:
                                result = node
                            lasivyo sio node._magic_id_nodes:
                                koma
                    lasivyo info.isId(attr.name):
                        self._id_cache[attr.value] = node
                        ikiwa attr.value == id:
                            result = node
                        lasivyo sio node._magic_id_nodes:
                            koma
                    lasivyo attr._is_id:
                        self._id_cache[attr.value] = node
                        ikiwa attr.value == id:
                            result = node
                        lasivyo node._magic_id_nodes == 1:
                            koma
            lasivyo node._magic_id_nodes:
                kila attr kwenye node.attributes.values():
                    ikiwa attr._is_id:
                        self._id_cache[attr.value] = node
                        ikiwa attr.value == id:
                            result = node
            ikiwa result ni sio Tupu:
                koma
        rudisha result

    eleza getElementsByTagName(self, name):
        rudisha _get_elements_by_tagName_helper(self, name, NodeList())

    eleza getElementsByTagNameNS(self, namespaceURI, localName):
        rudisha _get_elements_by_tagName_ns_helper(
            self, namespaceURI, localName, NodeList())

    eleza isSupported(self, feature, version):
        rudisha self.implementation.hasFeature(feature, version)

    eleza agizaNode(self, node, deep):
        ikiwa node.nodeType == Node.DOCUMENT_NODE:
            ashiria xml.dom.NotSupportedErr("cannot agiza document nodes")
        lasivyo node.nodeType == Node.DOCUMENT_TYPE_NODE:
            ashiria xml.dom.NotSupportedErr("cannot agiza document type nodes")
        rudisha _clone_node(node, deep, self)

    eleza writexml(self, writer, indent="", addindent="", newl="", encoding=Tupu):
        ikiwa encoding ni Tupu:
            writer.write('<?xml version="1.0" ?>'+newl)
        isipokua:
            writer.write('<?xml version="1.0" encoding="%s"?>%s' % (
                encoding, newl))
        kila node kwenye self.childNodes:
            node.writexml(writer, indent, addindent, newl)

    # DOM Level 3 (WD 9 April 2002)

    eleza renameNode(self, n, namespaceURI, name):
        ikiwa n.ownerDocument ni sio self:
            ashiria xml.dom.WrongDocumentErr(
                "cannot rename nodes kutoka other documents;\n"
                "expected %s,\nfound %s" % (self, n.ownerDocument))
        ikiwa n.nodeType haiko kwenye (Node.ELEMENT_NODE, Node.ATTRIBUTE_NODE):
            ashiria xml.dom.NotSupportedErr(
                "renameNode() only applies to element na attribute nodes")
        ikiwa namespaceURI != EMPTY_NAMESPACE:
            ikiwa ':' kwenye name:
                prefix, localName = name.split(':', 1)
                ikiwa (  prefix == "xmlns"
                      na namespaceURI != xml.dom.XMLNS_NAMESPACE):
                    ashiria xml.dom.NamespaceErr(
                        "illegal use of 'xmlns' prefix")
            isipokua:
                ikiwa (  name == "xmlns"
                      na namespaceURI != xml.dom.XMLNS_NAMESPACE
                      na n.nodeType == Node.ATTRIBUTE_NODE):
                    ashiria xml.dom.NamespaceErr(
                        "illegal use of the 'xmlns' attribute")
                prefix = Tupu
                localName = name
        isipokua:
            prefix = Tupu
            localName = Tupu
        ikiwa n.nodeType == Node.ATTRIBUTE_NODE:
            element = n.ownerElement
            ikiwa element ni sio Tupu:
                is_id = n._is_id
                element.removeAttributeNode(n)
        isipokua:
            element = Tupu
        n.prefix = prefix
        n._localName = localName
        n.namespaceURI = namespaceURI
        n.nodeName = name
        ikiwa n.nodeType == Node.ELEMENT_NODE:
            n.tagName = name
        isipokua:
            # attribute node
            n.name = name
            ikiwa element ni sio Tupu:
                element.setAttributeNode(n)
                ikiwa is_id:
                    element.setIdAttributeNode(n)
        # It's sio clear kutoka a semantic perspective whether we should
        # call the user data handlers kila the NODE_RENAMED event since
        # we're re-using the existing node.  The draft spec has been
        # interpreted kama meaning "no, don't call the handler unless a
        # new node ni created."
        rudisha n

defproperty(Document, "documentElement",
            doc="Top-level element of this document.")


eleza _clone_node(node, deep, newOwnerDocument):
    """
    Clone a node na give it the new owner document.
    Called by Node.cloneNode na Document.agizaNode
    """
    ikiwa node.ownerDocument.isSameNode(newOwnerDocument):
        operation = xml.dom.UserDataHandler.NODE_CLONED
    isipokua:
        operation = xml.dom.UserDataHandler.NODE_IMPORTED
    ikiwa node.nodeType == Node.ELEMENT_NODE:
        clone = newOwnerDocument.createElementNS(node.namespaceURI,
                                                 node.nodeName)
        kila attr kwenye node.attributes.values():
            clone.setAttributeNS(attr.namespaceURI, attr.nodeName, attr.value)
            a = clone.getAttributeNodeNS(attr.namespaceURI, attr.localName)
            a.specified = attr.specified

        ikiwa deep:
            kila child kwenye node.childNodes:
                c = _clone_node(child, deep, newOwnerDocument)
                clone.appendChild(c)

    lasivyo node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
        clone = newOwnerDocument.createDocumentFragment()
        ikiwa deep:
            kila child kwenye node.childNodes:
                c = _clone_node(child, deep, newOwnerDocument)
                clone.appendChild(c)

    lasivyo node.nodeType == Node.TEXT_NODE:
        clone = newOwnerDocument.createTextNode(node.data)
    lasivyo node.nodeType == Node.CDATA_SECTION_NODE:
        clone = newOwnerDocument.createCDATASection(node.data)
    lasivyo node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
        clone = newOwnerDocument.createProcessingInstruction(node.target,
                                                             node.data)
    lasivyo node.nodeType == Node.COMMENT_NODE:
        clone = newOwnerDocument.createComment(node.data)
    lasivyo node.nodeType == Node.ATTRIBUTE_NODE:
        clone = newOwnerDocument.createAttributeNS(node.namespaceURI,
                                                   node.nodeName)
        clone.specified = Kweli
        clone.value = node.value
    lasivyo node.nodeType == Node.DOCUMENT_TYPE_NODE:
        assert node.ownerDocument ni sio newOwnerDocument
        operation = xml.dom.UserDataHandler.NODE_IMPORTED
        clone = newOwnerDocument.implementation.createDocumentType(
            node.name, node.publicId, node.systemId)
        clone.ownerDocument = newOwnerDocument
        ikiwa deep:
            clone.entities._seq = []
            clone.notations._seq = []
            kila n kwenye node.notations._seq:
                notation = Notation(n.nodeName, n.publicId, n.systemId)
                notation.ownerDocument = newOwnerDocument
                clone.notations._seq.append(notation)
                ikiwa hasattr(n, '_call_user_data_handler'):
                    n._call_user_data_handler(operation, n, notation)
            kila e kwenye node.entities._seq:
                entity = Entity(e.nodeName, e.publicId, e.systemId,
                                e.notationName)
                entity.actualEncoding = e.actualEncoding
                entity.encoding = e.encoding
                entity.version = e.version
                entity.ownerDocument = newOwnerDocument
                clone.entities._seq.append(entity)
                ikiwa hasattr(e, '_call_user_data_handler'):
                    e._call_user_data_handler(operation, e, entity)
    isipokua:
        # Note the cloning of Document na DocumentType nodes is
        # implementation specific.  minidom handles those cases
        # directly kwenye the cloneNode() methods.
        ashiria xml.dom.NotSupportedErr("Cannot clone node %s" % repr(node))

    # Check kila _call_user_data_handler() since this could conceivably
    # used ukijumuisha other DOM implementations (one of the FourThought
    # DOMs, perhaps?).
    ikiwa hasattr(node, '_call_user_data_handler'):
        node._call_user_data_handler(operation, node, clone)
    rudisha clone


eleza _nssplit(qualifiedName):
    fields = qualifiedName.split(':', 1)
    ikiwa len(fields) == 2:
        rudisha fields
    isipokua:
        rudisha (Tupu, fields[0])


eleza _do_pulldom_parse(func, args, kwargs):
    events = func(*args, **kwargs)
    toktype, rootNode = events.getEvent()
    events.expandNode(rootNode)
    events.clear()
    rudisha rootNode

eleza parse(file, parser=Tupu, bufsize=Tupu):
    """Parse a file into a DOM by filename ama file object."""
    ikiwa parser ni Tupu na sio bufsize:
        kutoka xml.dom agiza expatbuilder
        rudisha expatbuilder.parse(file)
    isipokua:
        kutoka xml.dom agiza pulldom
        rudisha _do_pulldom_parse(pulldom.parse, (file,),
            {'parser': parser, 'bufsize': bufsize})

eleza parseString(string, parser=Tupu):
    """Parse a file into a DOM kutoka a string."""
    ikiwa parser ni Tupu:
        kutoka xml.dom agiza expatbuilder
        rudisha expatbuilder.parseString(string)
    isipokua:
        kutoka xml.dom agiza pulldom
        rudisha _do_pulldom_parse(pulldom.parseString, (string,),
                                 {'parser': parser})

eleza getDOMImplementation(features=Tupu):
    ikiwa features:
        ikiwa isinstance(features, str):
            features = domreg._parse_feature_string(features)
        kila f, v kwenye features:
            ikiwa sio Document.implementation.hasFeature(f, v):
                rudisha Tupu
    rudisha Document.implementation
