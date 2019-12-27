"""Simple implementation of the Level 1 DOM.

Namespaces and other minor Level 2 features are also supported.

parse("foo.xml")

parseString("<foo><bar/></foo>")

Todo:
=====
 * convenience methods for getting elements and text.
 * more testing
 * bring some of the writer and linearizer code into conformance with this
        interface
 * SAX 2 namespaces
"""

agiza io
agiza xml.dom

kutoka xml.dom agiza EMPTY_NAMESPACE, EMPTY_PREFIX, XMLNS_NAMESPACE, domreg
kutoka xml.dom.minicompat agiza *
kutoka xml.dom.xmlbuilder agiza DOMImplementationLS, DocumentLS

# This is used by the ID-cache invalidation checks; the list isn't
# actually complete, since the nodes being checked will never be the
# DOCUMENT_NODE or DOCUMENT_FRAGMENT_NODE.  (The node being checked is
# the node being added or removed, not the node being modified.)
#
_nodeTypes_with_children = (xml.dom.Node.ELEMENT_NODE,
                            xml.dom.Node.ENTITY_REFERENCE_NODE)


kundi Node(xml.dom.Node):
    namespaceURI = None # this is non-null only for elements and attributes
    parentNode = None
    ownerDocument = None
    nextSibling = None
    previousSibling = None

    prefix = EMPTY_PREFIX # non-null only for NS elements and attributes

    eleza __bool__(self):
        rudisha True

    eleza toxml(self, encoding=None):
        rudisha self.toprettyxml("", "", encoding)

    eleza toprettyxml(self, indent="\t", newl="\n", encoding=None):
        ikiwa encoding is None:
            writer = io.StringIO()
        else:
            writer = io.TextIOWrapper(io.BytesIO(),
                                      encoding=encoding,
                                      errors="xmlcharrefreplace",
                                      newline='\n')
        ikiwa self.nodeType == Node.DOCUMENT_NODE:
            # Can pass encoding only to document, to put it into XML header
            self.writexml(writer, "", indent, newl, encoding)
        else:
            self.writexml(writer, "", indent, newl)
        ikiwa encoding is None:
            rudisha writer.getvalue()
        else:
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
            for c in tuple(newChild.childNodes):
                self.insertBefore(c, refChild)
            ### The DOM does not clearly specify what to rudisha in this case
            rudisha newChild
        ikiwa newChild.nodeType not in self._child_node_types:
            raise xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(newChild), repr(self)))
        ikiwa newChild.parentNode is not None:
            newChild.parentNode.removeChild(newChild)
        ikiwa refChild is None:
            self.appendChild(newChild)
        else:
            try:
                index = self.childNodes.index(refChild)
            except ValueError:
                raise xml.dom.NotFoundErr()
            ikiwa newChild.nodeType in _nodeTypes_with_children:
                _clear_id_cache(self)
            self.childNodes.insert(index, newChild)
            newChild.nextSibling = refChild
            refChild.previousSibling = newChild
            ikiwa index:
                node = self.childNodes[index-1]
                node.nextSibling = newChild
                newChild.previousSibling = node
            else:
                newChild.previousSibling = None
            newChild.parentNode = self
        rudisha newChild

    eleza appendChild(self, node):
        ikiwa node.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            for c in tuple(node.childNodes):
                self.appendChild(c)
            ### The DOM does not clearly specify what to rudisha in this case
            rudisha node
        ikiwa node.nodeType not in self._child_node_types:
            raise xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(node), repr(self)))
        elikiwa node.nodeType in _nodeTypes_with_children:
            _clear_id_cache(self)
        ikiwa node.parentNode is not None:
            node.parentNode.removeChild(node)
        _append_child(self, node)
        node.nextSibling = None
        rudisha node

    eleza replaceChild(self, newChild, oldChild):
        ikiwa newChild.nodeType == self.DOCUMENT_FRAGMENT_NODE:
            refChild = oldChild.nextSibling
            self.removeChild(oldChild)
            rudisha self.insertBefore(newChild, refChild)
        ikiwa newChild.nodeType not in self._child_node_types:
            raise xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(newChild), repr(self)))
        ikiwa newChild is oldChild:
            return
        ikiwa newChild.parentNode is not None:
            newChild.parentNode.removeChild(newChild)
        try:
            index = self.childNodes.index(oldChild)
        except ValueError:
            raise xml.dom.NotFoundErr()
        self.childNodes[index] = newChild
        newChild.parentNode = self
        oldChild.parentNode = None
        ikiwa (newChild.nodeType in _nodeTypes_with_children
            or oldChild.nodeType in _nodeTypes_with_children):
            _clear_id_cache(self)
        newChild.nextSibling = oldChild.nextSibling
        newChild.previousSibling = oldChild.previousSibling
        oldChild.nextSibling = None
        oldChild.previousSibling = None
        ikiwa newChild.previousSibling:
            newChild.previousSibling.nextSibling = newChild
        ikiwa newChild.nextSibling:
            newChild.nextSibling.previousSibling = newChild
        rudisha oldChild

    eleza removeChild(self, oldChild):
        try:
            self.childNodes.remove(oldChild)
        except ValueError:
            raise xml.dom.NotFoundErr()
        ikiwa oldChild.nextSibling is not None:
            oldChild.nextSibling.previousSibling = oldChild.previousSibling
        ikiwa oldChild.previousSibling is not None:
            oldChild.previousSibling.nextSibling = oldChild.nextSibling
        oldChild.nextSibling = oldChild.previousSibling = None
        ikiwa oldChild.nodeType in _nodeTypes_with_children:
            _clear_id_cache(self)

        oldChild.parentNode = None
        rudisha oldChild

    eleza normalize(self):
        L = []
        for child in self.childNodes:
            ikiwa child.nodeType == Node.TEXT_NODE:
                ikiwa not child.data:
                    # empty text node; discard
                    ikiwa L:
                        L[-1].nextSibling = child.nextSibling
                    ikiwa child.nextSibling:
                        child.nextSibling.previousSibling = child.previousSibling
                    child.unlink()
                elikiwa L and L[-1].nodeType == child.nodeType:
                    # collapse text node
                    node = L[-1]
                    node.data = node.data + child.data
                    node.nextSibling = child.nextSibling
                    ikiwa child.nextSibling:
                        child.nextSibling.previousSibling = node
                    child.unlink()
                else:
                    L.append(child)
            else:
                L.append(child)
                ikiwa child.nodeType == Node.ELEMENT_NODE:
                    child.normalize()
        self.childNodes[:] = L

    eleza cloneNode(self, deep):
        rudisha _clone_node(self, deep, self.ownerDocument or self)

    eleza isSupported(self, feature, version):
        rudisha self.ownerDocument.implementation.hasFeature(feature, version)

    eleza _get_localName(self):
        # Overridden in Element and Attr where localName can be Non-Null
        rudisha None

    # Node interfaces kutoka Level 3 (WD 9 April 2002)

    eleza isSameNode(self, other):
        rudisha self is other

    eleza getInterface(self, feature):
        ikiwa self.isSupported(feature, None):
            rudisha self
        else:
            rudisha None

    # The "user data" functions use a dictionary that is only present
    # ikiwa some user data has been set, so be careful not to assume it
    # exists.

    eleza getUserData(self, key):
        try:
            rudisha self._user_data[key][0]
        except (AttributeError, KeyError):
            rudisha None

    eleza setUserData(self, key, data, handler):
        old = None
        try:
            d = self._user_data
        except AttributeError:
            d = {}
            self._user_data = d
        ikiwa key in d:
            old = d[key][0]
        ikiwa data is None:
            # ignore handlers passed for None
            handler = None
            ikiwa old is not None:
                del d[key]
        else:
            d[key] = (data, handler)
        rudisha old

    eleza _call_user_data_handler(self, operation, src, dst):
        ikiwa hasattr(self, "_user_data"):
            for key, (data, handler) in list(self._user_data.items()):
                ikiwa handler is not None:
                    handler.handle(operation, key, data, src, dst)

    # minidom-specific API:

    eleza unlink(self):
        self.parentNode = self.ownerDocument = None
        ikiwa self.childNodes:
            for child in self.childNodes:
                child.unlink()
            self.childNodes = NodeList()
        self.previousSibling = None
        self.nextSibling = None

    # A Node is its own context manager, to ensure that an unlink() call occurs.
    # This is similar to how a file object works.
    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, et, ev, tb):
        self.unlink()

defproperty(Node, "firstChild", doc="First child node, or None.")
defproperty(Node, "lastChild",  doc="Last child node, or None.")
defproperty(Node, "localName",  doc="Namespace-local name of this node.")


eleza _append_child(self, node):
    # fast path with less checks; usable by DOM builders ikiwa careful
    childNodes = self.childNodes
    ikiwa childNodes:
        last = childNodes[-1]
        node.previousSibling = last
        last.nextSibling = node
    childNodes.append(node)
    node.parentNode = self

eleza _in_document(node):
    # rudisha True iff node is part of a document tree
    while node is not None:
        ikiwa node.nodeType == Node.DOCUMENT_NODE:
            rudisha True
        node = node.parentNode
    rudisha False

eleza _write_data(writer, data):
    "Writes datachars to writer."
    ikiwa data:
        data = data.replace("&", "&amp;").replace("<", "&lt;"). \
                    replace("\"", "&quot;").replace(">", "&gt;")
        writer.write(data)

eleza _get_elements_by_tagName_helper(parent, name, rc):
    for node in parent.childNodes:
        ikiwa node.nodeType == Node.ELEMENT_NODE and \
            (name == "*" or node.tagName == name):
            rc.append(node)
        _get_elements_by_tagName_helper(node, name, rc)
    rudisha rc

eleza _get_elements_by_tagName_ns_helper(parent, nsURI, localName, rc):
    for node in parent.childNodes:
        ikiwa node.nodeType == Node.ELEMENT_NODE:
            ikiwa ((localName == "*" or node.localName == localName) and
                (nsURI == "*" or node.namespaceURI == nsURI)):
                rc.append(node)
            _get_elements_by_tagName_ns_helper(node, nsURI, localName, rc)
    rudisha rc

kundi DocumentFragment(Node):
    nodeType = Node.DOCUMENT_FRAGMENT_NODE
    nodeName = "#document-fragment"
    nodeValue = None
    attributes = None
    parentNode = None
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
    attributes = None
    specified = False
    _is_id = False

    _child_node_types = (Node.TEXT_NODE, Node.ENTITY_REFERENCE_NODE)

    eleza __init__(self, qName, namespaceURI=EMPTY_NAMESPACE, localName=None,
                 prefix=None):
        self.ownerElement = None
        self._name = qName
        self.namespaceURI = namespaceURI
        self._prefix = prefix
        self.childNodes = NodeList()

        # Add the single child node that represents the value of the attr
        self.childNodes.append(Text())

        # nodeValue and value are set elsewhere

    eleza _get_localName(self):
        try:
            rudisha self._localName
        except AttributeError:
            rudisha self.nodeName.split(":", 1)[-1]

    eleza _get_specified(self):
        rudisha self.specified

    eleza _get_name(self):
        rudisha self._name

    eleza _set_name(self, value):
        self._name = value
        ikiwa self.ownerElement is not None:
            _clear_id_cache(self.ownerElement)

    nodeName = name = property(_get_name, _set_name)

    eleza _get_value(self):
        rudisha self._value

    eleza _set_value(self, value):
        self._value = value
        self.childNodes[0].data = value
        ikiwa self.ownerElement is not None:
            _clear_id_cache(self.ownerElement)
        self.childNodes[0].data = value

    nodeValue = value = property(_get_value, _set_value)

    eleza _get_prefix(self):
        rudisha self._prefix

    eleza _set_prefix(self, prefix):
        nsuri = self.namespaceURI
        ikiwa prefix == "xmlns":
            ikiwa nsuri and nsuri != XMLNS_NAMESPACE:
                raise xml.dom.NamespaceErr(
                    "illegal use of 'xmlns' prefix for the wrong namespace")
        self._prefix = prefix
        ikiwa prefix is None:
            newName = self.localName
        else:
            newName = "%s:%s" % (prefix, self.localName)
        ikiwa self.ownerElement:
            _clear_id_cache(self.ownerElement)
        self.name = newName

    prefix = property(_get_prefix, _set_prefix)

    eleza unlink(self):
        # This implementation does not call the base implementation
        # since most of that is not needed, and the expense of the
        # method call is not warranted.  We duplicate the removal of
        # children, but that's all we needed kutoka the base class.
        elem = self.ownerElement
        ikiwa elem is not None:
            del elem._attrs[self.nodeName]
            del elem._attrsNS[(self.namespaceURI, self.localName)]
            ikiwa self._is_id:
                self._is_id = False
                elem._magic_id_nodes -= 1
                self.ownerDocument._magic_id_count -= 1
        for child in self.childNodes:
            child.unlink()
        del self.childNodes[:]

    eleza _get_isId(self):
        ikiwa self._is_id:
            rudisha True
        doc = self.ownerDocument
        elem = self.ownerElement
        ikiwa doc is None or elem is None:
            rudisha False

        info = doc._get_elem_info(elem)
        ikiwa info is None:
            rudisha False
        ikiwa self.namespaceURI:
            rudisha info.isIdNS(self.namespaceURI, self.localName)
        else:
            rudisha info.isId(self.nodeName)

    eleza _get_schemaType(self):
        doc = self.ownerDocument
        elem = self.ownerElement
        ikiwa doc is None or elem is None:
            rudisha _no_type

        info = doc._get_elem_info(elem)
        ikiwa info is None:
            rudisha _no_type
        ikiwa self.namespaceURI:
            rudisha info.getAttributeTypeNS(self.namespaceURI, self.localName)
        else:
            rudisha info.getAttributeType(self.nodeName)

defproperty(Attr, "isId",       doc="True ikiwa this attribute is an ID.")
defproperty(Attr, "localName",  doc="Namespace-local name of this attribute.")
defproperty(Attr, "schemaType", doc="Schema type for this attribute.")


kundi NamedNodeMap(object):
    """The attribute list is a transient interface to the underlying
    dictionaries.  Mutations here will change the underlying element's
    dictionary.

    Ordering is imposed artificially and does not reflect the order of
    attributes as found in an input document.
    """

    __slots__ = ('_attrs', '_attrsNS', '_ownerElement')

    eleza __init__(self, attrs, attrsNS, ownerElement):
        self._attrs = attrs
        self._attrsNS = attrsNS
        self._ownerElement = ownerElement

    eleza _get_length(self):
        rudisha len(self._attrs)

    eleza item(self, index):
        try:
            rudisha self[list(self._attrs.keys())[index]]
        except IndexError:
            rudisha None

    eleza items(self):
        L = []
        for node in self._attrs.values():
            L.append((node.nodeName, node.value))
        rudisha L

    eleza itemsNS(self):
        L = []
        for node in self._attrs.values():
            L.append(((node.namespaceURI, node.localName), node.value))
        rudisha L

    eleza __contains__(self, key):
        ikiwa isinstance(key, str):
            rudisha key in self._attrs
        else:
            rudisha key in self._attrsNS

    eleza keys(self):
        rudisha self._attrs.keys()

    eleza keysNS(self):
        rudisha self._attrsNS.keys()

    eleza values(self):
        rudisha self._attrs.values()

    eleza get(self, name, value=None):
        rudisha self._attrs.get(name, value)

    __len__ = _get_length

    eleza _cmp(self, other):
        ikiwa self._attrs is getattr(other, "_attrs", None):
            rudisha 0
        else:
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
        else:
            rudisha self._attrs[attname_or_tuple]

    # same as set
    eleza __setitem__(self, attname, value):
        ikiwa isinstance(value, str):
            try:
                node = self._attrs[attname]
            except KeyError:
                node = Attr(attname)
                node.ownerDocument = self._ownerElement.ownerDocument
                self.setNamedItem(node)
            node.value = value
        else:
            ikiwa not isinstance(value, Attr):
                raise TypeError("value must be a string or Attr object")
            node = value
            self.setNamedItem(node)

    eleza getNamedItem(self, name):
        try:
            rudisha self._attrs[name]
        except KeyError:
            rudisha None

    eleza getNamedItemNS(self, namespaceURI, localName):
        try:
            rudisha self._attrsNS[(namespaceURI, localName)]
        except KeyError:
            rudisha None

    eleza removeNamedItem(self, name):
        n = self.getNamedItem(name)
        ikiwa n is not None:
            _clear_id_cache(self._ownerElement)
            del self._attrs[n.nodeName]
            del self._attrsNS[(n.namespaceURI, n.localName)]
            ikiwa hasattr(n, 'ownerElement'):
                n.ownerElement = None
            rudisha n
        else:
            raise xml.dom.NotFoundErr()

    eleza removeNamedItemNS(self, namespaceURI, localName):
        n = self.getNamedItemNS(namespaceURI, localName)
        ikiwa n is not None:
            _clear_id_cache(self._ownerElement)
            del self._attrsNS[(n.namespaceURI, n.localName)]
            del self._attrs[n.nodeName]
            ikiwa hasattr(n, 'ownerElement'):
                n.ownerElement = None
            rudisha n
        else:
            raise xml.dom.NotFoundErr()

    eleza setNamedItem(self, node):
        ikiwa not isinstance(node, Attr):
            raise xml.dom.HierarchyRequestErr(
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
            doc="Number of nodes in the NamedNodeMap.")

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
        else:
            rudisha "<%s %r>" % (self.__class__.__name__, self.name)

    eleza _get_name(self):
        rudisha self.name

    eleza _get_namespace(self):
        rudisha self.namespace

_no_type = TypeInfo(None, None)

kundi Element(Node):
    __slots__=('ownerDocument', 'parentNode', 'tagName', 'nodeName', 'prefix',
               'namespaceURI', '_localName', 'childNodes', '_attrs', '_attrsNS',
               'nextSibling', 'previousSibling')
    nodeType = Node.ELEMENT_NODE
    nodeValue = None
    schemaType = _no_type

    _magic_id_nodes = 0

    _child_node_types = (Node.ELEMENT_NODE,
                         Node.PROCESSING_INSTRUCTION_NODE,
                         Node.COMMENT_NODE,
                         Node.TEXT_NODE,
                         Node.CDATA_SECTION_NODE,
                         Node.ENTITY_REFERENCE_NODE)

    eleza __init__(self, tagName, namespaceURI=EMPTY_NAMESPACE, prefix=None,
                 localName=None):
        self.parentNode = None
        self.tagName = self.nodeName = tagName
        self.prefix = prefix
        self.namespaceURI = namespaceURI
        self.childNodes = NodeList()
        self.nextSibling = self.previousSibling = None

        # Attribute dictionaries are lazily created
        # attributes are double-indexed:
        #    tagName -> Attribute
        #    URI,localName -> Attribute
        # in the future: consider lazy generation
        # of attribute objects this is too tricky
        # for now because of headaches with
        # namespaces.
        self._attrs = None
        self._attrsNS = None

    eleza _ensure_attributes(self):
        ikiwa self._attrs is None:
            self._attrs = {}
            self._attrsNS = {}

    eleza _get_localName(self):
        try:
            rudisha self._localName
        except AttributeError:
            rudisha self.tagName.split(":", 1)[-1]

    eleza _get_tagName(self):
        rudisha self.tagName

    eleza unlink(self):
        ikiwa self._attrs is not None:
            for attr in list(self._attrs.values()):
                attr.unlink()
        self._attrs = None
        self._attrsNS = None
        Node.unlink(self)

    eleza getAttribute(self, attname):
        ikiwa self._attrs is None:
            rudisha ""
        try:
            rudisha self._attrs[attname].value
        except KeyError:
            rudisha ""

    eleza getAttributeNS(self, namespaceURI, localName):
        ikiwa self._attrsNS is None:
            rudisha ""
        try:
            rudisha self._attrsNS[(namespaceURI, localName)].value
        except KeyError:
            rudisha ""

    eleza setAttribute(self, attname, value):
        attr = self.getAttributeNode(attname)
        ikiwa attr is None:
            attr = Attr(attname)
            attr.value = value # also sets nodeValue
            attr.ownerDocument = self.ownerDocument
            self.setAttributeNode(attr)
        elikiwa value != attr.value:
            attr.value = value
            ikiwa attr.isId:
                _clear_id_cache(self)

    eleza setAttributeNS(self, namespaceURI, qualifiedName, value):
        prefix, localname = _nssplit(qualifiedName)
        attr = self.getAttributeNodeNS(namespaceURI, localname)
        ikiwa attr is None:
            attr = Attr(qualifiedName, namespaceURI, localname, prefix)
            attr.value = value
            attr.ownerDocument = self.ownerDocument
            self.setAttributeNode(attr)
        else:
            ikiwa value != attr.value:
                attr.value = value
                ikiwa attr.isId:
                    _clear_id_cache(self)
            ikiwa attr.prefix != prefix:
                attr.prefix = prefix
                attr.nodeName = qualifiedName

    eleza getAttributeNode(self, attrname):
        ikiwa self._attrs is None:
            rudisha None
        rudisha self._attrs.get(attrname)

    eleza getAttributeNodeNS(self, namespaceURI, localName):
        ikiwa self._attrsNS is None:
            rudisha None
        rudisha self._attrsNS.get((namespaceURI, localName))

    eleza setAttributeNode(self, attr):
        ikiwa attr.ownerElement not in (None, self):
            raise xml.dom.InuseAttributeErr("attribute node already owned")
        self._ensure_attributes()
        old1 = self._attrs.get(attr.name, None)
        ikiwa old1 is not None:
            self.removeAttributeNode(old1)
        old2 = self._attrsNS.get((attr.namespaceURI, attr.localName), None)
        ikiwa old2 is not None and old2 is not old1:
            self.removeAttributeNode(old2)
        _set_attribute_node(self, attr)

        ikiwa old1 is not attr:
            # It might have already been part of this node, in which case
            # it doesn't represent a change, and should not be returned.
            rudisha old1
        ikiwa old2 is not attr:
            rudisha old2

    setAttributeNodeNS = setAttributeNode

    eleza removeAttribute(self, name):
        ikiwa self._attrsNS is None:
            raise xml.dom.NotFoundErr()
        try:
            attr = self._attrs[name]
        except KeyError:
            raise xml.dom.NotFoundErr()
        self.removeAttributeNode(attr)

    eleza removeAttributeNS(self, namespaceURI, localName):
        ikiwa self._attrsNS is None:
            raise xml.dom.NotFoundErr()
        try:
            attr = self._attrsNS[(namespaceURI, localName)]
        except KeyError:
            raise xml.dom.NotFoundErr()
        self.removeAttributeNode(attr)

    eleza removeAttributeNode(self, node):
        ikiwa node is None:
            raise xml.dom.NotFoundErr()
        try:
            self._attrs[node.name]
        except KeyError:
            raise xml.dom.NotFoundErr()
        _clear_id_cache(self)
        node.unlink()
        # Restore this since the node is still useful and otherwise
        # unlinked
        node.ownerDocument = self.ownerDocument
        rudisha node

    removeAttributeNodeNS = removeAttributeNode

    eleza hasAttribute(self, name):
        ikiwa self._attrs is None:
            rudisha False
        rudisha name in self._attrs

    eleza hasAttributeNS(self, namespaceURI, localName):
        ikiwa self._attrsNS is None:
            rudisha False
        rudisha (namespaceURI, localName) in self._attrsNS

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

        for a_name in attrs.keys():
            writer.write(" %s=\"" % a_name)
            _write_data(writer, attrs[a_name].value)
            writer.write("\"")
        ikiwa self.childNodes:
            writer.write(">")
            ikiwa (len(self.childNodes) == 1 and
                self.childNodes[0].nodeType in (
                        Node.TEXT_NODE, Node.CDATA_SECTION_NODE)):
                self.childNodes[0].writexml(writer, '', '', '')
            else:
                writer.write(newl)
                for node in self.childNodes:
                    node.writexml(writer, indent+addindent, addindent, newl)
                writer.write(indent)
            writer.write("</%s>%s" % (self.tagName, newl))
        else:
            writer.write("/>%s"%(newl))

    eleza _get_attributes(self):
        self._ensure_attributes()
        rudisha NamedNodeMap(self._attrs, self._attrsNS, self)

    eleza hasAttributes(self):
        ikiwa self._attrs:
            rudisha True
        else:
            rudisha False

    # DOM Level 3 attributes, based on the 22 Oct 2002 draft

    eleza setIdAttribute(self, name):
        idAttr = self.getAttributeNode(name)
        self.setIdAttributeNode(idAttr)

    eleza setIdAttributeNS(self, namespaceURI, localName):
        idAttr = self.getAttributeNodeNS(namespaceURI, localName)
        self.setIdAttributeNode(idAttr)

    eleza setIdAttributeNode(self, idAttr):
        ikiwa idAttr is None or not self.isSameNode(idAttr.ownerElement):
            raise xml.dom.NotFoundErr()
        ikiwa _get_containing_entref(self) is not None:
            raise xml.dom.NoModificationAllowedErr()
        ikiwa not idAttr._is_id:
            idAttr._is_id = True
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
    # breaks the cycle since the references to the attribute
    # dictionaries are tossed.
    attr.ownerElement = element

kundi Childless:
    """Mixin that makes childless-ness easy to implement and avoids
    the complexity of the Node methods that deal with children.
    """
    __slots__ = ()

    attributes = None
    childNodes = EmptyNodeList()
    firstChild = None
    lastChild = None

    eleza _get_firstChild(self):
        rudisha None

    eleza _get_lastChild(self):
        rudisha None

    eleza appendChild(self, node):
        raise xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes cannot have children")

    eleza hasChildNodes(self):
        rudisha False

    eleza insertBefore(self, newChild, refChild):
        raise xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes do not have children")

    eleza removeChild(self, oldChild):
        raise xml.dom.NotFoundErr(
            self.nodeName + " nodes do not have children")

    eleza normalize(self):
        # For childless nodes, normalize() has nothing to do.
        pass

    eleza replaceChild(self, newChild, oldChild):
        raise xml.dom.HierarchyRequestErr(
            self.nodeName + " nodes do not have children")


kundi ProcessingInstruction(Childless, Node):
    nodeType = Node.PROCESSING_INSTRUCTION_NODE
    __slots__ = ('target', 'data')

    eleza __init__(self, target, data):
        self.target = target
        self.data = data

    # nodeValue is an alias for data
    eleza _get_nodeValue(self):
        rudisha self.data
    eleza _set_nodeValue(self, value):
        self.data = value
    nodeValue = property(_get_nodeValue, _set_nodeValue)

    # nodeName is an alias for target
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
        self.ownerDocument = self.parentNode = None
        self.previousSibling = self.nextSibling = None
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
        else:
            dotdotdot = ""
        rudisha '<DOM %s node "%r%s">' % (
            self.__class__.__name__, data[0:10], dotdotdot)

    eleza substringData(self, offset, count):
        ikiwa offset < 0:
            raise xml.dom.IndexSizeErr("offset cannot be negative")
        ikiwa offset >= len(self.data):
            raise xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        ikiwa count < 0:
            raise xml.dom.IndexSizeErr("count cannot be negative")
        rudisha self.data[offset:offset+count]

    eleza appendData(self, arg):
        self.data = self.data + arg

    eleza insertData(self, offset, arg):
        ikiwa offset < 0:
            raise xml.dom.IndexSizeErr("offset cannot be negative")
        ikiwa offset >= len(self.data):
            raise xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        ikiwa arg:
            self.data = "%s%s%s" % (
                self.data[:offset], arg, self.data[offset:])

    eleza deleteData(self, offset, count):
        ikiwa offset < 0:
            raise xml.dom.IndexSizeErr("offset cannot be negative")
        ikiwa offset >= len(self.data):
            raise xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        ikiwa count < 0:
            raise xml.dom.IndexSizeErr("count cannot be negative")
        ikiwa count:
            self.data = self.data[:offset] + self.data[offset+count:]

    eleza replaceData(self, offset, count, arg):
        ikiwa offset < 0:
            raise xml.dom.IndexSizeErr("offset cannot be negative")
        ikiwa offset >= len(self.data):
            raise xml.dom.IndexSizeErr("offset cannot be beyond end of data")
        ikiwa count < 0:
            raise xml.dom.IndexSizeErr("count cannot be negative")
        ikiwa count:
            self.data = "%s%s%s" % (
                self.data[:offset], arg, self.data[offset+count:])

defproperty(CharacterData, "length", doc="Length of the string data.")


kundi Text(CharacterData):
    __slots__ = ()

    nodeType = Node.TEXT_NODE
    nodeName = "#text"
    attributes = None

    eleza splitText(self, offset):
        ikiwa offset < 0 or offset > len(self.data):
            raise xml.dom.IndexSizeErr("illegal offset value")
        newText = self.__class__()
        newText.data = self.data[offset:]
        newText.ownerDocument = self.ownerDocument
        next = self.nextSibling
        ikiwa self.parentNode and self in self.parentNode.childNodes:
            ikiwa next is None:
                self.parentNode.appendChild(newText)
            else:
                self.parentNode.insertBefore(newText, next)
        self.data = self.data[:offset]
        rudisha newText

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        _write_data(writer, "%s%s%s" % (indent, self.data, newl))

    # DOM Level 3 (WD 9 April 2002)

    eleza _get_wholeText(self):
        L = [self.data]
        n = self.previousSibling
        while n is not None:
            ikiwa n.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                L.insert(0, n.data)
                n = n.previousSibling
            else:
                break
        n = self.nextSibling
        while n is not None:
            ikiwa n.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                L.append(n.data)
                n = n.nextSibling
            else:
                break
        rudisha ''.join(L)

    eleza replaceWholeText(self, content):
        # XXX This needs to be seriously changed ikiwa minidom ever
        # supports EntityReference nodes.
        parent = self.parentNode
        n = self.previousSibling
        while n is not None:
            ikiwa n.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                next = n.previousSibling
                parent.removeChild(n)
                n = next
            else:
                break
        n = self.nextSibling
        ikiwa not content:
            parent.removeChild(self)
        while n is not None:
            ikiwa n.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                next = n.nextSibling
                parent.removeChild(n)
                n = next
            else:
                break
        ikiwa content:
            self.data = content
            rudisha self
        else:
            rudisha None

    eleza _get_isWhitespaceInElementContent(self):
        ikiwa self.data.strip():
            rudisha False
        elem = _get_containing_element(self)
        ikiwa elem is None:
            rudisha False
        info = self.ownerDocument._get_elem_info(elem)
        ikiwa info is None:
            rudisha False
        else:
            rudisha info.isElementContent()

defproperty(Text, "isWhitespaceInElementContent",
            doc="True iff this text node contains only whitespace"
                " and is in element content.")
defproperty(Text, "wholeText",
            doc="The text of all logically-adjacent text nodes.")


eleza _get_containing_element(node):
    c = node.parentNode
    while c is not None:
        ikiwa c.nodeType == Node.ELEMENT_NODE:
            rudisha c
        c = c.parentNode
    rudisha None

eleza _get_containing_entref(node):
    c = node.parentNode
    while c is not None:
        ikiwa c.nodeType == Node.ENTITY_REFERENCE_NODE:
            rudisha c
        c = c.parentNode
    rudisha None


kundi Comment(CharacterData):
    nodeType = Node.COMMENT_NODE
    nodeName = "#comment"

    eleza __init__(self, data):
        CharacterData.__init__(self)
        self._data = data

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        ikiwa "--" in self.data:
            raise ValueError("'--' is not allowed in a comment node")
        writer.write("%s<!--%s-->%s" % (indent, self.data, newl))


kundi CDATASection(Text):
    __slots__ = ()

    nodeType = Node.CDATA_SECTION_NODE
    nodeName = "#cdata-section"

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        ikiwa self.data.find("]]>") >= 0:
            raise ValueError("']]>' not allowed in a CDATA section")
        writer.write("<![CDATA[%s]]>" % self.data)


kundi ReadOnlySequentialNamedNodeMap(object):
    __slots__ = '_seq',

    eleza __init__(self, seq=()):
        # seq should be a list or tuple
        self._seq = seq

    eleza __len__(self):
        rudisha len(self._seq)

    eleza _get_length(self):
        rudisha len(self._seq)

    eleza getNamedItem(self, name):
        for n in self._seq:
            ikiwa n.nodeName == name:
                rudisha n

    eleza getNamedItemNS(self, namespaceURI, localName):
        for n in self._seq:
            ikiwa n.namespaceURI == namespaceURI and n.localName == localName:
                rudisha n

    eleza __getitem__(self, name_or_tuple):
        ikiwa isinstance(name_or_tuple, tuple):
            node = self.getNamedItemNS(*name_or_tuple)
        else:
            node = self.getNamedItem(name_or_tuple)
        ikiwa node is None:
            raise KeyError(name_or_tuple)
        rudisha node

    eleza item(self, index):
        ikiwa index < 0:
            rudisha None
        try:
            rudisha self._seq[index]
        except IndexError:
            rudisha None

    eleza removeNamedItem(self, name):
        raise xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance is read-only")

    eleza removeNamedItemNS(self, namespaceURI, localName):
        raise xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance is read-only")

    eleza setNamedItem(self, node):
        raise xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance is read-only")

    eleza setNamedItemNS(self, node):
        raise xml.dom.NoModificationAllowedErr(
            "NamedNodeMap instance is read-only")

    eleza __getstate__(self):
        rudisha [self._seq]

    eleza __setstate__(self, state):
        self._seq = state[0]

defproperty(ReadOnlySequentialNamedNodeMap, "length",
            doc="Number of entries in the NamedNodeMap.")


kundi Identified:
    """Mix-in kundi that supports the publicId and systemId attributes."""

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
    nodeValue = None
    name = None
    publicId = None
    systemId = None
    internalSubset = None

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
        ikiwa self.ownerDocument is None:
            # it's ok
            clone = DocumentType(None)
            clone.name = self.name
            clone.nodeName = self.name
            operation = xml.dom.UserDataHandler.NODE_CLONED
            ikiwa deep:
                clone.entities._seq = []
                clone.notations._seq = []
                for n in self.notations._seq:
                    notation = Notation(n.nodeName, n.publicId, n.systemId)
                    clone.notations._seq.append(notation)
                    n._call_user_data_handler(operation, n, notation)
                for e in self.entities._seq:
                    entity = Entity(e.nodeName, e.publicId, e.systemId,
                                    e.notationName)
                    entity.actualEncoding = e.actualEncoding
                    entity.encoding = e.encoding
                    entity.version = e.version
                    clone.entities._seq.append(entity)
                    e._call_user_data_handler(operation, e, entity)
            self._call_user_data_handler(operation, self, clone)
            rudisha clone
        else:
            rudisha None

    eleza writexml(self, writer, indent="", addindent="", newl=""):
        writer.write("<!DOCTYPE ")
        writer.write(self.name)
        ikiwa self.publicId:
            writer.write("%s  PUBLIC '%s'%s  '%s'"
                         % (newl, self.publicId, newl, self.systemId))
        elikiwa self.systemId:
            writer.write("%s  SYSTEM '%s'" % (newl, self.systemId))
        ikiwa self.internalSubset is not None:
            writer.write(" [")
            writer.write(self.internalSubset)
            writer.write("]")
        writer.write(">"+newl)

kundi Entity(Identified, Node):
    attributes = None
    nodeType = Node.ENTITY_NODE
    nodeValue = None

    actualEncoding = None
    encoding = None
    version = None

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
        raise xml.dom.HierarchyRequestErr(
            "cannot append children to an entity node")

    eleza insertBefore(self, newChild, refChild):
        raise xml.dom.HierarchyRequestErr(
            "cannot insert children below an entity node")

    eleza removeChild(self, oldChild):
        raise xml.dom.HierarchyRequestErr(
            "cannot remove children kutoka an entity node")

    eleza replaceChild(self, newChild, oldChild):
        raise xml.dom.HierarchyRequestErr(
            "cannot replace children of an entity node")

kundi Notation(Identified, Childless, Node):
    nodeType = Node.NOTATION_NODE
    nodeValue = None

    eleza __init__(self, name, publicId, systemId):
        self.nodeName = name
        self._identified_mixin_init(publicId, systemId)


kundi DOMImplementation(DOMImplementationLS):
    _features = [("core", "1.0"),
                 ("core", "2.0"),
                 ("core", None),
                 ("xml", "1.0"),
                 ("xml", "2.0"),
                 ("xml", None),
                 ("ls-load", "3.0"),
                 ("ls-load", None),
                 ]

    eleza hasFeature(self, feature, version):
        ikiwa version == "":
            version = None
        rudisha (feature.lower(), version) in self._features

    eleza createDocument(self, namespaceURI, qualifiedName, doctype):
        ikiwa doctype and doctype.parentNode is not None:
            raise xml.dom.WrongDocumentErr(
                "doctype object owned by another DOM tree")
        doc = self._create_document()

        add_root_element = not (namespaceURI is None
                                and qualifiedName is None
                                and doctype is None)

        ikiwa not qualifiedName and add_root_element:
            # The spec is unclear what to raise here; SyntaxErr
            # would be the other obvious candidate. Since Xerces raises
            # InvalidCharacterErr, and since SyntaxErr is not listed
            # for createDocument, that seems to be the better choice.
            # XXX: need to check for illegal characters here and in
            # createElement.

            # DOM Level III clears this up when talking about the rudisha value
            # of this function.  If namespaceURI, qName and DocType are
            # Null the document is returned without a document element
            # Otherwise ikiwa doctype or namespaceURI are not None
            # Then we go back to the above problem
            raise xml.dom.InvalidCharacterErr("Element with no name")

        ikiwa add_root_element:
            prefix, localname = _nssplit(qualifiedName)
            ikiwa prefix == "xml" \
               and namespaceURI != "http://www.w3.org/XML/1998/namespace":
                raise xml.dom.NamespaceErr("illegal use of 'xml' prefix")
            ikiwa prefix and not namespaceURI:
                raise xml.dom.NamespaceErr(
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
        ikiwa self.hasFeature(feature, None):
            rudisha self
        else:
            rudisha None

    # internal
    eleza _create_document(self):
        rudisha Document()

kundi ElementInfo(object):
    """Object that represents content-model information for an element.

    This implementation is not expected to be used in practice; DOM
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
        rudisha False

    eleza isEmpty(self):
        """Returns true iff this element is declared to have an EMPTY
        content model."""
        rudisha False

    eleza isId(self, aname):
        """Returns true iff the named attribute is a DTD-style ID."""
        rudisha False

    eleza isIdNS(self, namespaceURI, localName):
        """Returns true iff the identified attribute is a DTD-style ID."""
        rudisha False

    eleza __getstate__(self):
        rudisha self.tagName

    eleza __setstate__(self, state):
        self.tagName = state

eleza _clear_id_cache(node):
    ikiwa node.nodeType == Node.DOCUMENT_NODE:
        node._id_cache.clear()
        node._id_search_stack = None
    elikiwa _in_document(node):
        node.ownerDocument._id_cache.clear()
        node.ownerDocument._id_search_stack= None

kundi Document(Node, DocumentLS):
    __slots__ = ('_elem_info', 'doctype',
                 '_id_search_stack', 'childNodes', '_id_cache')
    _child_node_types = (Node.ELEMENT_NODE, Node.PROCESSING_INSTRUCTION_NODE,
                         Node.COMMENT_NODE, Node.DOCUMENT_TYPE_NODE)

    implementation = DOMImplementation()
    nodeType = Node.DOCUMENT_NODE
    nodeName = "#document"
    nodeValue = None
    attributes = None
    parentNode = None
    previousSibling = nextSibling = None


    # Document attributes kutoka Level 3 (WD 9 April 2002)

    actualEncoding = None
    encoding = None
    standalone = None
    version = None
    strictErrorChecking = False
    errorHandler = None
    documentURI = None

    _magic_id_count = 0

    eleza __init__(self):
        self.doctype = None
        self.childNodes = NodeList()
        # mapping of (namespaceURI, localName) -> ElementInfo
        #        and tagName -> ElementInfo
        self._elem_info = {}
        self._id_cache = {}
        self._id_search_stack = None

    eleza _get_elem_info(self, element):
        ikiwa element.namespaceURI:
            key = element.namespaceURI, element.localName
        else:
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
        ikiwa node.nodeType not in self._child_node_types:
            raise xml.dom.HierarchyRequestErr(
                "%s cannot be child of %s" % (repr(node), repr(self)))
        ikiwa node.parentNode is not None:
            # This needs to be done before the next test since this
            # may *be* the document element, in which case it should
            # end up re-ordered to the end.
            node.parentNode.removeChild(node)

        ikiwa node.nodeType == Node.ELEMENT_NODE \
           and self._get_documentElement():
            raise xml.dom.HierarchyRequestErr(
                "two document elements disallowed")
        rudisha Node.appendChild(self, node)

    eleza removeChild(self, oldChild):
        try:
            self.childNodes.remove(oldChild)
        except ValueError:
            raise xml.dom.NotFoundErr()
        oldChild.nextSibling = oldChild.previousSibling = None
        oldChild.parentNode = None
        ikiwa self.documentElement is oldChild:
            self.documentElement = None

        rudisha oldChild

    eleza _get_documentElement(self):
        for node in self.childNodes:
            ikiwa node.nodeType == Node.ELEMENT_NODE:
                rudisha node

    eleza unlink(self):
        ikiwa self.doctype is not None:
            self.doctype.unlink()
            self.doctype = None
        Node.unlink(self)

    eleza cloneNode(self, deep):
        ikiwa not deep:
            rudisha None
        clone = self.implementation.createDocument(None, None, None)
        clone.encoding = self.encoding
        clone.standalone = self.standalone
        clone.version = self.version
        for n in self.childNodes:
            childclone = _clone_node(n, deep, clone)
            assert childclone.ownerDocument.isSameNode(clone)
            clone.childNodes.append(childclone)
            ikiwa childclone.nodeType == Node.DOCUMENT_NODE:
                assert clone.documentElement is None
            elikiwa childclone.nodeType == Node.DOCUMENT_TYPE_NODE:
                assert clone.doctype is None
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
        ikiwa not isinstance(data, str):
            raise TypeError("node contents must be a string")
        t = Text()
        t.data = data
        t.ownerDocument = self
        rudisha t

    eleza createCDATASection(self, data):
        ikiwa not isinstance(data, str):
            raise TypeError("node contents must be a string")
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
    # not supported by the W3C DOM specs:

    eleza _create_entity(self, name, publicId, systemId, notationName):
        e = Entity(name, publicId, systemId, notationName)
        e.ownerDocument = self
        rudisha e

    eleza _create_notation(self, name, publicId, systemId):
        n = Notation(name, publicId, systemId)
        n.ownerDocument = self
        rudisha n

    eleza getElementById(self, id):
        ikiwa id in self._id_cache:
            rudisha self._id_cache[id]
        ikiwa not (self._elem_info or self._magic_id_count):
            rudisha None

        stack = self._id_search_stack
        ikiwa stack is None:
            # we never searched before, or the cache has been cleared
            stack = [self.documentElement]
            self._id_search_stack = stack
        elikiwa not stack:
            # Previous search was completed and cache is still valid;
            # no matching node.
            rudisha None

        result = None
        while stack:
            node = stack.pop()
            # add child elements to stack for continued searching
            stack.extend([child for child in node.childNodes
                          ikiwa child.nodeType in _nodeTypes_with_children])
            # check this node
            info = self._get_elem_info(node)
            ikiwa info:
                # We have to process all ID attributes before
                # returning in order to get all the attributes set to
                # be IDs using Element.setIdAttribute*().
                for attr in node.attributes.values():
                    ikiwa attr.namespaceURI:
                        ikiwa info.isIdNS(attr.namespaceURI, attr.localName):
                            self._id_cache[attr.value] = node
                            ikiwa attr.value == id:
                                result = node
                            elikiwa not node._magic_id_nodes:
                                break
                    elikiwa info.isId(attr.name):
                        self._id_cache[attr.value] = node
                        ikiwa attr.value == id:
                            result = node
                        elikiwa not node._magic_id_nodes:
                            break
                    elikiwa attr._is_id:
                        self._id_cache[attr.value] = node
                        ikiwa attr.value == id:
                            result = node
                        elikiwa node._magic_id_nodes == 1:
                            break
            elikiwa node._magic_id_nodes:
                for attr in node.attributes.values():
                    ikiwa attr._is_id:
                        self._id_cache[attr.value] = node
                        ikiwa attr.value == id:
                            result = node
            ikiwa result is not None:
                break
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
            raise xml.dom.NotSupportedErr("cannot agiza document nodes")
        elikiwa node.nodeType == Node.DOCUMENT_TYPE_NODE:
            raise xml.dom.NotSupportedErr("cannot agiza document type nodes")
        rudisha _clone_node(node, deep, self)

    eleza writexml(self, writer, indent="", addindent="", newl="", encoding=None):
        ikiwa encoding is None:
            writer.write('<?xml version="1.0" ?>'+newl)
        else:
            writer.write('<?xml version="1.0" encoding="%s"?>%s' % (
                encoding, newl))
        for node in self.childNodes:
            node.writexml(writer, indent, addindent, newl)

    # DOM Level 3 (WD 9 April 2002)

    eleza renameNode(self, n, namespaceURI, name):
        ikiwa n.ownerDocument is not self:
            raise xml.dom.WrongDocumentErr(
                "cannot rename nodes kutoka other documents;\n"
                "expected %s,\nfound %s" % (self, n.ownerDocument))
        ikiwa n.nodeType not in (Node.ELEMENT_NODE, Node.ATTRIBUTE_NODE):
            raise xml.dom.NotSupportedErr(
                "renameNode() only applies to element and attribute nodes")
        ikiwa namespaceURI != EMPTY_NAMESPACE:
            ikiwa ':' in name:
                prefix, localName = name.split(':', 1)
                ikiwa (  prefix == "xmlns"
                      and namespaceURI != xml.dom.XMLNS_NAMESPACE):
                    raise xml.dom.NamespaceErr(
                        "illegal use of 'xmlns' prefix")
            else:
                ikiwa (  name == "xmlns"
                      and namespaceURI != xml.dom.XMLNS_NAMESPACE
                      and n.nodeType == Node.ATTRIBUTE_NODE):
                    raise xml.dom.NamespaceErr(
                        "illegal use of the 'xmlns' attribute")
                prefix = None
                localName = name
        else:
            prefix = None
            localName = None
        ikiwa n.nodeType == Node.ATTRIBUTE_NODE:
            element = n.ownerElement
            ikiwa element is not None:
                is_id = n._is_id
                element.removeAttributeNode(n)
        else:
            element = None
        n.prefix = prefix
        n._localName = localName
        n.namespaceURI = namespaceURI
        n.nodeName = name
        ikiwa n.nodeType == Node.ELEMENT_NODE:
            n.tagName = name
        else:
            # attribute node
            n.name = name
            ikiwa element is not None:
                element.setAttributeNode(n)
                ikiwa is_id:
                    element.setIdAttributeNode(n)
        # It's not clear kutoka a semantic perspective whether we should
        # call the user data handlers for the NODE_RENAMED event since
        # we're re-using the existing node.  The draft spec has been
        # interpreted as meaning "no, don't call the handler unless a
        # new node is created."
        rudisha n

defproperty(Document, "documentElement",
            doc="Top-level element of this document.")


eleza _clone_node(node, deep, newOwnerDocument):
    """
    Clone a node and give it the new owner document.
    Called by Node.cloneNode and Document.agizaNode
    """
    ikiwa node.ownerDocument.isSameNode(newOwnerDocument):
        operation = xml.dom.UserDataHandler.NODE_CLONED
    else:
        operation = xml.dom.UserDataHandler.NODE_IMPORTED
    ikiwa node.nodeType == Node.ELEMENT_NODE:
        clone = newOwnerDocument.createElementNS(node.namespaceURI,
                                                 node.nodeName)
        for attr in node.attributes.values():
            clone.setAttributeNS(attr.namespaceURI, attr.nodeName, attr.value)
            a = clone.getAttributeNodeNS(attr.namespaceURI, attr.localName)
            a.specified = attr.specified

        ikiwa deep:
            for child in node.childNodes:
                c = _clone_node(child, deep, newOwnerDocument)
                clone.appendChild(c)

    elikiwa node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
        clone = newOwnerDocument.createDocumentFragment()
        ikiwa deep:
            for child in node.childNodes:
                c = _clone_node(child, deep, newOwnerDocument)
                clone.appendChild(c)

    elikiwa node.nodeType == Node.TEXT_NODE:
        clone = newOwnerDocument.createTextNode(node.data)
    elikiwa node.nodeType == Node.CDATA_SECTION_NODE:
        clone = newOwnerDocument.createCDATASection(node.data)
    elikiwa node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
        clone = newOwnerDocument.createProcessingInstruction(node.target,
                                                             node.data)
    elikiwa node.nodeType == Node.COMMENT_NODE:
        clone = newOwnerDocument.createComment(node.data)
    elikiwa node.nodeType == Node.ATTRIBUTE_NODE:
        clone = newOwnerDocument.createAttributeNS(node.namespaceURI,
                                                   node.nodeName)
        clone.specified = True
        clone.value = node.value
    elikiwa node.nodeType == Node.DOCUMENT_TYPE_NODE:
        assert node.ownerDocument is not newOwnerDocument
        operation = xml.dom.UserDataHandler.NODE_IMPORTED
        clone = newOwnerDocument.implementation.createDocumentType(
            node.name, node.publicId, node.systemId)
        clone.ownerDocument = newOwnerDocument
        ikiwa deep:
            clone.entities._seq = []
            clone.notations._seq = []
            for n in node.notations._seq:
                notation = Notation(n.nodeName, n.publicId, n.systemId)
                notation.ownerDocument = newOwnerDocument
                clone.notations._seq.append(notation)
                ikiwa hasattr(n, '_call_user_data_handler'):
                    n._call_user_data_handler(operation, n, notation)
            for e in node.entities._seq:
                entity = Entity(e.nodeName, e.publicId, e.systemId,
                                e.notationName)
                entity.actualEncoding = e.actualEncoding
                entity.encoding = e.encoding
                entity.version = e.version
                entity.ownerDocument = newOwnerDocument
                clone.entities._seq.append(entity)
                ikiwa hasattr(e, '_call_user_data_handler'):
                    e._call_user_data_handler(operation, e, entity)
    else:
        # Note the cloning of Document and DocumentType nodes is
        # implementation specific.  minidom handles those cases
        # directly in the cloneNode() methods.
        raise xml.dom.NotSupportedErr("Cannot clone node %s" % repr(node))

    # Check for _call_user_data_handler() since this could conceivably
    # used with other DOM implementations (one of the FourThought
    # DOMs, perhaps?).
    ikiwa hasattr(node, '_call_user_data_handler'):
        node._call_user_data_handler(operation, node, clone)
    rudisha clone


eleza _nssplit(qualifiedName):
    fields = qualifiedName.split(':', 1)
    ikiwa len(fields) == 2:
        rudisha fields
    else:
        rudisha (None, fields[0])


eleza _do_pulldom_parse(func, args, kwargs):
    events = func(*args, **kwargs)
    toktype, rootNode = events.getEvent()
    events.expandNode(rootNode)
    events.clear()
    rudisha rootNode

eleza parse(file, parser=None, bufsize=None):
    """Parse a file into a DOM by filename or file object."""
    ikiwa parser is None and not bufsize:
        kutoka xml.dom agiza expatbuilder
        rudisha expatbuilder.parse(file)
    else:
        kutoka xml.dom agiza pulldom
        rudisha _do_pulldom_parse(pulldom.parse, (file,),
            {'parser': parser, 'bufsize': bufsize})

eleza parseString(string, parser=None):
    """Parse a file into a DOM kutoka a string."""
    ikiwa parser is None:
        kutoka xml.dom agiza expatbuilder
        rudisha expatbuilder.parseString(string)
    else:
        kutoka xml.dom agiza pulldom
        rudisha _do_pulldom_parse(pulldom.parseString, (string,),
                                 {'parser': parser})

eleza getDOMImplementation(features=None):
    ikiwa features:
        ikiwa isinstance(features, str):
            features = domreg._parse_feature_string(features)
        for f, v in features:
            ikiwa not Document.implementation.hasFeature(f, v):
                rudisha None
    rudisha Document.implementation
