# test kila xml.dom.minidom

agiza copy
agiza pickle
agiza io
kutoka test agiza support
agiza unittest

agiza xml.dom.minidom

kutoka xml.dom.minidom agiza parse, Node, Document, parseString
kutoka xml.dom.minidom agiza getDOMImplementation


tstfile = support.findfile("test.xml", subdir="xmltestdata")
sample = ("<?xml version='1.0' encoding='us-ascii'?>\n"
          "<!DOCTYPE doc PUBLIC 'http://xml.python.org/public'"
          " 'http://xml.python.org/system' [\n"
          "  <!ELEMENT e EMPTY>\n"
          "  <!ENTITY ent SYSTEM 'http://xml.python.org/entity'>\n"
          "]><doc attr='value'> text\n"
          "<?pi sample?> <!-- comment --> <e/> </doc>")

# The tests of DocumentType importing use these helpers to construct
# the documents to work with, since sio all DOM builders actually
# create the DocumentType nodes.
eleza create_doc_without_doctype(doctype=Tupu):
    rudisha getDOMImplementation().createDocument(Tupu, "doc", doctype)

eleza create_nonempty_doctype():
    doctype = getDOMImplementation().createDocumentType("doc", Tupu, Tupu)
    doctype.entities._seq = []
    doctype.notations._seq = []
    notation = xml.dom.minidom.Notation("my-notation", Tupu,
                                        "http://xml.python.org/notations/my")
    doctype.notations._seq.append(notation)
    entity = xml.dom.minidom.Entity("my-entity", Tupu,
                                    "http://xml.python.org/entities/my",
                                    "my-notation")
    entity.version = "1.0"
    entity.encoding = "utf-8"
    entity.actualEncoding = "us-ascii"
    doctype.entities._seq.append(entity)
    rudisha doctype

eleza create_doc_with_doctype():
    doctype = create_nonempty_doctype()
    doc = create_doc_without_doctype(doctype)
    doctype.entities.item(0).ownerDocument = doc
    doctype.notations.item(0).ownerDocument = doc
    rudisha doc

kundi MinidomTest(unittest.TestCase):
    eleza confirm(self, test, testname = "Test"):
        self.assertKweli(test, testname)

    eleza checkWholeText(self, node, s):
        t = node.wholeText
        self.confirm(t == s, "looking kila %r, found %r" % (s, t))

    eleza testDocumentAsyncAttr(self):
        doc = Document()
        self.assertUongo(doc.async_)
        self.assertUongo(Document.async_)

    eleza testParseFromBinaryFile(self):
        ukijumuisha open(tstfile, 'rb') as file:
            dom = parse(file)
            dom.unlink()
            self.confirm(isinstance(dom, Document))

    eleza testParseFromTextFile(self):
        ukijumuisha open(tstfile, 'r', encoding='iso-8859-1') as file:
            dom = parse(file)
            dom.unlink()
            self.confirm(isinstance(dom, Document))

    eleza testGetElementsByTagName(self):
        dom = parse(tstfile)
        self.confirm(dom.getElementsByTagName("LI") == \
                dom.documentElement.getElementsByTagName("LI"))
        dom.unlink()

    eleza testInsertBefore(self):
        dom = parseString("<doc><foo/></doc>")
        root = dom.documentElement
        elem = root.childNodes[0]
        nelem = dom.createElement("element")
        root.insertBefore(nelem, elem)
        self.confirm(len(root.childNodes) == 2
                na root.childNodes.length == 2
                na root.childNodes[0] ni nelem
                na root.childNodes.item(0) ni nelem
                na root.childNodes[1] ni elem
                na root.childNodes.item(1) ni elem
                na root.firstChild ni nelem
                na root.lastChild ni elem
                na root.toxml() == "<doc><element/><foo/></doc>"
                , "testInsertBefore -- node properly placed kwenye tree")
        nelem = dom.createElement("element")
        root.insertBefore(nelem, Tupu)
        self.confirm(len(root.childNodes) == 3
                na root.childNodes.length == 3
                na root.childNodes[1] ni elem
                na root.childNodes.item(1) ni elem
                na root.childNodes[2] ni nelem
                na root.childNodes.item(2) ni nelem
                na root.lastChild ni nelem
                na nelem.previousSibling ni elem
                na root.toxml() == "<doc><element/><foo/><element/></doc>"
                , "testInsertBefore -- node properly placed kwenye tree")
        nelem2 = dom.createElement("bar")
        root.insertBefore(nelem2, nelem)
        self.confirm(len(root.childNodes) == 4
                na root.childNodes.length == 4
                na root.childNodes[2] ni nelem2
                na root.childNodes.item(2) ni nelem2
                na root.childNodes[3] ni nelem
                na root.childNodes.item(3) ni nelem
                na nelem2.nextSibling ni nelem
                na nelem.previousSibling ni nelem2
                na root.toxml() ==
                "<doc><element/><foo/><bar/><element/></doc>"
                , "testInsertBefore -- node properly placed kwenye tree")
        dom.unlink()

    eleza _create_fragment_test_nodes(self):
        dom = parseString("<doc/>")
        orig = dom.createTextNode("original")
        c1 = dom.createTextNode("foo")
        c2 = dom.createTextNode("bar")
        c3 = dom.createTextNode("bat")
        dom.documentElement.appendChild(orig)
        frag = dom.createDocumentFragment()
        frag.appendChild(c1)
        frag.appendChild(c2)
        frag.appendChild(c3)
        rudisha dom, orig, c1, c2, c3, frag

    eleza testInsertBeforeFragment(self):
        dom, orig, c1, c2, c3, frag = self._create_fragment_test_nodes()
        dom.documentElement.insertBefore(frag, Tupu)
        self.confirm(tuple(dom.documentElement.childNodes) ==
                     (orig, c1, c2, c3),
                     "insertBefore(<fragment>, Tupu)")
        frag.unlink()
        dom.unlink()

        dom, orig, c1, c2, c3, frag = self._create_fragment_test_nodes()
        dom.documentElement.insertBefore(frag, orig)
        self.confirm(tuple(dom.documentElement.childNodes) ==
                     (c1, c2, c3, orig),
                     "insertBefore(<fragment>, orig)")
        frag.unlink()
        dom.unlink()

    eleza testAppendChild(self):
        dom = parse(tstfile)
        dom.documentElement.appendChild(dom.createComment("Hello"))
        self.confirm(dom.documentElement.childNodes[-1].nodeName == "#comment")
        self.confirm(dom.documentElement.childNodes[-1].data == "Hello")
        dom.unlink()

    eleza testAppendChildFragment(self):
        dom, orig, c1, c2, c3, frag = self._create_fragment_test_nodes()
        dom.documentElement.appendChild(frag)
        self.confirm(tuple(dom.documentElement.childNodes) ==
                     (orig, c1, c2, c3),
                     "appendChild(<fragment>)")
        frag.unlink()
        dom.unlink()

    eleza testReplaceChildFragment(self):
        dom, orig, c1, c2, c3, frag = self._create_fragment_test_nodes()
        dom.documentElement.replaceChild(frag, orig)
        orig.unlink()
        self.confirm(tuple(dom.documentElement.childNodes) == (c1, c2, c3),
                "replaceChild(<fragment>)")
        frag.unlink()
        dom.unlink()

    eleza testLegalChildren(self):
        dom = Document()
        elem = dom.createElement('element')
        text = dom.createTextNode('text')
        self.assertRaises(xml.dom.HierarchyRequestErr, dom.appendChild, text)

        dom.appendChild(elem)
        self.assertRaises(xml.dom.HierarchyRequestErr, dom.insertBefore, text,
                          elem)
        self.assertRaises(xml.dom.HierarchyRequestErr, dom.replaceChild, text,
                          elem)

        nodemap = elem.attributes
        self.assertRaises(xml.dom.HierarchyRequestErr, nodemap.setNamedItem,
                          text)
        self.assertRaises(xml.dom.HierarchyRequestErr, nodemap.setNamedItemNS,
                          text)

        elem.appendChild(text)
        dom.unlink()

    eleza testNamedNodeMapSetItem(self):
        dom = Document()
        elem = dom.createElement('element')
        attrs = elem.attributes
        attrs["foo"] = "bar"
        a = attrs.item(0)
        self.confirm(a.ownerDocument ni dom,
                "NamedNodeMap.__setitem__() sets ownerDocument")
        self.confirm(a.ownerElement ni elem,
                "NamedNodeMap.__setitem__() sets ownerElement")
        self.confirm(a.value == "bar",
                "NamedNodeMap.__setitem__() sets value")
        self.confirm(a.nodeValue == "bar",
                "NamedNodeMap.__setitem__() sets nodeValue")
        elem.unlink()
        dom.unlink()

    eleza testNonZero(self):
        dom = parse(tstfile)
        self.confirm(dom)# should sio be zero
        dom.appendChild(dom.createComment("foo"))
        self.confirm(not dom.childNodes[-1].childNodes)
        dom.unlink()

    eleza testUnlink(self):
        dom = parse(tstfile)
        self.assertKweli(dom.childNodes)
        dom.unlink()
        self.assertUongo(dom.childNodes)

    eleza testContext(self):
        ukijumuisha parse(tstfile) as dom:
            self.assertKweli(dom.childNodes)
        self.assertUongo(dom.childNodes)

    eleza testElement(self):
        dom = Document()
        dom.appendChild(dom.createElement("abc"))
        self.confirm(dom.documentElement)
        dom.unlink()

    eleza testAAA(self):
        dom = parseString("<abc/>")
        el = dom.documentElement
        el.setAttribute("spam", "jam2")
        self.confirm(el.toxml() == '<abc spam="jam2"/>', "testAAA")
        a = el.getAttributeNode("spam")
        self.confirm(a.ownerDocument ni dom,
                "setAttribute() sets ownerDocument")
        self.confirm(a.ownerElement ni dom.documentElement,
                "setAttribute() sets ownerElement")
        dom.unlink()

    eleza testAAB(self):
        dom = parseString("<abc/>")
        el = dom.documentElement
        el.setAttribute("spam", "jam")
        el.setAttribute("spam", "jam2")
        self.confirm(el.toxml() == '<abc spam="jam2"/>', "testAAB")
        dom.unlink()

    eleza testAddAttr(self):
        dom = Document()
        child = dom.appendChild(dom.createElement("abc"))

        child.setAttribute("def", "ghi")
        self.confirm(child.getAttribute("def") == "ghi")
        self.confirm(child.attributes["def"].value == "ghi")

        child.setAttribute("jkl", "mno")
        self.confirm(child.getAttribute("jkl") == "mno")
        self.confirm(child.attributes["jkl"].value == "mno")

        self.confirm(len(child.attributes) == 2)

        child.setAttribute("def", "newval")
        self.confirm(child.getAttribute("def") == "newval")
        self.confirm(child.attributes["def"].value == "newval")

        self.confirm(len(child.attributes) == 2)
        dom.unlink()

    eleza testDeleteAttr(self):
        dom = Document()
        child = dom.appendChild(dom.createElement("abc"))

        self.confirm(len(child.attributes) == 0)
        child.setAttribute("def", "ghi")
        self.confirm(len(child.attributes) == 1)
        toa child.attributes["def"]
        self.confirm(len(child.attributes) == 0)
        dom.unlink()

    eleza testRemoveAttr(self):
        dom = Document()
        child = dom.appendChild(dom.createElement("abc"))

        child.setAttribute("def", "ghi")
        self.confirm(len(child.attributes) == 1)
        self.assertRaises(xml.dom.NotFoundErr, child.removeAttribute, "foo")
        child.removeAttribute("def")
        self.confirm(len(child.attributes) == 0)
        dom.unlink()

    eleza testRemoveAttrNS(self):
        dom = Document()
        child = dom.appendChild(
                dom.createElementNS("http://www.python.org", "python:abc"))
        child.setAttributeNS("http://www.w3.org", "xmlns:python",
                                                "http://www.python.org")
        child.setAttributeNS("http://www.python.org", "python:abcattr", "foo")
        self.assertRaises(xml.dom.NotFoundErr, child.removeAttributeNS,
            "foo", "http://www.python.org")
        self.confirm(len(child.attributes) == 2)
        child.removeAttributeNS("http://www.python.org", "abcattr")
        self.confirm(len(child.attributes) == 1)
        dom.unlink()

    eleza testRemoveAttributeNode(self):
        dom = Document()
        child = dom.appendChild(dom.createElement("foo"))
        child.setAttribute("spam", "jam")
        self.confirm(len(child.attributes) == 1)
        node = child.getAttributeNode("spam")
        self.assertRaises(xml.dom.NotFoundErr, child.removeAttributeNode,
            Tupu)
        self.assertIs(node, child.removeAttributeNode(node))
        self.confirm(len(child.attributes) == 0
                na child.getAttributeNode("spam") ni Tupu)
        dom2 = Document()
        child2 = dom2.appendChild(dom2.createElement("foo"))
        node2 = child2.getAttributeNode("spam")
        self.assertRaises(xml.dom.NotFoundErr, child2.removeAttributeNode,
            node2)
        dom.unlink()

    eleza testHasAttribute(self):
        dom = Document()
        child = dom.appendChild(dom.createElement("foo"))
        child.setAttribute("spam", "jam")
        self.confirm(child.hasAttribute("spam"))

    eleza testChangeAttr(self):
        dom = parseString("<abc/>")
        el = dom.documentElement
        el.setAttribute("spam", "jam")
        self.confirm(len(el.attributes) == 1)
        el.setAttribute("spam", "bam")
        # Set this attribute to be an ID na make sure that doesn't change
        # when changing the value:
        el.setIdAttribute("spam")
        self.confirm(len(el.attributes) == 1
                na el.attributes["spam"].value == "bam"
                na el.attributes["spam"].nodeValue == "bam"
                na el.getAttribute("spam") == "bam"
                na el.getAttributeNode("spam").isId)
        el.attributes["spam"] = "ham"
        self.confirm(len(el.attributes) == 1
                na el.attributes["spam"].value == "ham"
                na el.attributes["spam"].nodeValue == "ham"
                na el.getAttribute("spam") == "ham"
                na el.attributes["spam"].isId)
        el.setAttribute("spam2", "bam")
        self.confirm(len(el.attributes) == 2
                na el.attributes["spam"].value == "ham"
                na el.attributes["spam"].nodeValue == "ham"
                na el.getAttribute("spam") == "ham"
                na el.attributes["spam2"].value == "bam"
                na el.attributes["spam2"].nodeValue == "bam"
                na el.getAttribute("spam2") == "bam")
        el.attributes["spam2"] = "bam2"
        self.confirm(len(el.attributes) == 2
                na el.attributes["spam"].value == "ham"
                na el.attributes["spam"].nodeValue == "ham"
                na el.getAttribute("spam") == "ham"
                na el.attributes["spam2"].value == "bam2"
                na el.attributes["spam2"].nodeValue == "bam2"
                na el.getAttribute("spam2") == "bam2")
        dom.unlink()

    eleza testGetAttrList(self):
        pass

    eleza testGetAttrValues(self):
        pass

    eleza testGetAttrLength(self):
        pass

    eleza testGetAttribute(self):
        dom = Document()
        child = dom.appendChild(
            dom.createElementNS("http://www.python.org", "python:abc"))
        self.assertEqual(child.getAttribute('missing'), '')

    eleza testGetAttributeNS(self):
        dom = Document()
        child = dom.appendChild(
                dom.createElementNS("http://www.python.org", "python:abc"))
        child.setAttributeNS("http://www.w3.org", "xmlns:python",
                                                "http://www.python.org")
        self.assertEqual(child.getAttributeNS("http://www.w3.org", "python"),
            'http://www.python.org')
        self.assertEqual(child.getAttributeNS("http://www.w3.org", "other"),
            '')
        child2 = child.appendChild(dom.createElement('abc'))
        self.assertEqual(child2.getAttributeNS("http://www.python.org", "missing"),
                         '')

    eleza testGetAttributeNode(self): pass

    eleza testGetElementsByTagNameNS(self):
        d="""<foo xmlns:minidom='http://pyxml.sf.net/minidom'>
        <minidom:myelem/>
        </foo>"""
        dom = parseString(d)
        elems = dom.getElementsByTagNameNS("http://pyxml.sf.net/minidom",
                                           "myelem")
        self.confirm(len(elems) == 1
                na elems[0].namespaceURI == "http://pyxml.sf.net/minidom"
                na elems[0].localName == "myelem"
                na elems[0].prefix == "minidom"
                na elems[0].tagName == "minidom:myelem"
                na elems[0].nodeName == "minidom:myelem")
        dom.unlink()

    eleza get_empty_nodelist_from_elements_by_tagName_ns_helper(self, doc, nsuri,
                                                              lname):
        nodelist = doc.getElementsByTagNameNS(nsuri, lname)
        self.confirm(len(nodelist) == 0)

    eleza testGetEmptyNodeListFromElementsByTagNameNS(self):
        doc = parseString('<doc/>')
        self.get_empty_nodelist_from_elements_by_tagName_ns_helper(
            doc, 'http://xml.python.org/namespaces/a', 'localname')
        self.get_empty_nodelist_from_elements_by_tagName_ns_helper(
            doc, '*', 'splat')
        self.get_empty_nodelist_from_elements_by_tagName_ns_helper(
            doc, 'http://xml.python.org/namespaces/a', '*')

        doc = parseString('<doc xmlns="http://xml.python.org/splat"><e/></doc>')
        self.get_empty_nodelist_from_elements_by_tagName_ns_helper(
            doc, "http://xml.python.org/splat", "not-there")
        self.get_empty_nodelist_from_elements_by_tagName_ns_helper(
            doc, "*", "not-there")
        self.get_empty_nodelist_from_elements_by_tagName_ns_helper(
            doc, "http://somewhere.else.net/not-there", "e")

    eleza testElementReprAndStr(self):
        dom = Document()
        el = dom.appendChild(dom.createElement("abc"))
        string1 = repr(el)
        string2 = str(el)
        self.confirm(string1 == string2)
        dom.unlink()

    eleza testElementReprAndStrUnicode(self):
        dom = Document()
        el = dom.appendChild(dom.createElement("abc"))
        string1 = repr(el)
        string2 = str(el)
        self.confirm(string1 == string2)
        dom.unlink()

    eleza testElementReprAndStrUnicodeNS(self):
        dom = Document()
        el = dom.appendChild(
            dom.createElementNS("http://www.slashdot.org", "slash:abc"))
        string1 = repr(el)
        string2 = str(el)
        self.confirm(string1 == string2)
        self.confirm("slash:abc" kwenye string1)
        dom.unlink()

    eleza testAttributeRepr(self):
        dom = Document()
        el = dom.appendChild(dom.createElement("abc"))
        node = el.setAttribute("abc", "def")
        self.confirm(str(node) == repr(node))
        dom.unlink()

    eleza testTextNodeRepr(self): pass

    eleza testWriteXML(self):
        str = '<?xml version="1.0" ?><a b="c"/>'
        dom = parseString(str)
        domstr = dom.toxml()
        dom.unlink()
        self.confirm(str == domstr)

    eleza testAltNewline(self):
        str = '<?xml version="1.0" ?>\n<a b="c"/>\n'
        dom = parseString(str)
        domstr = dom.toprettyxml(newl="\r\n")
        dom.unlink()
        self.confirm(domstr == str.replace("\n", "\r\n"))

    eleza test_toprettyxml_with_text_nodes(self):
        # see issue #4147, text nodes are sio indented
        decl = '<?xml version="1.0" ?>\n'
        self.assertEqual(parseString('<B>A</B>').toprettyxml(),
                         decl + '<B>A</B>\n')
        self.assertEqual(parseString('<C>A<B>A</B></C>').toprettyxml(),
                         decl + '<C>\n\tA\n\t<B>A</B>\n</C>\n')
        self.assertEqual(parseString('<C><B>A</B>A</C>').toprettyxml(),
                         decl + '<C>\n\t<B>A</B>\n\tA\n</C>\n')
        self.assertEqual(parseString('<C><B>A</B><B>A</B></C>').toprettyxml(),
                         decl + '<C>\n\t<B>A</B>\n\t<B>A</B>\n</C>\n')
        self.assertEqual(parseString('<C><B>A</B>A<B>A</B></C>').toprettyxml(),
                         decl + '<C>\n\t<B>A</B>\n\tA\n\t<B>A</B>\n</C>\n')

    eleza test_toprettyxml_with_adjacent_text_nodes(self):
        # see issue #4147, adjacent text nodes are indented normally
        dom = Document()
        elem = dom.createElement('elem')
        elem.appendChild(dom.createTextNode('TEXT'))
        elem.appendChild(dom.createTextNode('TEXT'))
        dom.appendChild(elem)
        decl = '<?xml version="1.0" ?>\n'
        self.assertEqual(dom.toprettyxml(),
                         decl + '<elem>\n\tTEXT\n\tTEXT\n</elem>\n')

    eleza test_toprettyxml_preserves_content_of_text_node(self):
        # see issue #4147
        kila str kwenye ('<B>A</B>', '<A><B>C</B></A>'):
            dom = parseString(str)
            dom2 = parseString(dom.toprettyxml())
            self.assertEqual(
                dom.getElementsByTagName('B')[0].childNodes[0].toxml(),
                dom2.getElementsByTagName('B')[0].childNodes[0].toxml())

    eleza testProcessingInstruction(self):
        dom = parseString('<e><?mypi \t\n data \t\n ?></e>')
        pi = dom.documentElement.firstChild
        self.confirm(pi.target == "mypi"
                na pi.data == "data \t\n "
                na pi.nodeName == "mypi"
                na pi.nodeType == Node.PROCESSING_INSTRUCTION_NODE
                na pi.attributes ni Tupu
                na sio pi.hasChildNodes()
                na len(pi.childNodes) == 0
                na pi.firstChild ni Tupu
                na pi.lastChild ni Tupu
                na pi.localName ni Tupu
                na pi.namespaceURI == xml.dom.EMPTY_NAMESPACE)

    eleza testProcessingInstructionRepr(self): pass

    eleza testTextRepr(self): pass

    eleza testWriteText(self): pass

    eleza testDocumentElement(self): pass

    eleza testTooManyDocumentElements(self):
        doc = parseString("<doc/>")
        elem = doc.createElement("extra")
        # Should  ashiria an exception when adding an extra document element.
        self.assertRaises(xml.dom.HierarchyRequestErr, doc.appendChild, elem)
        elem.unlink()
        doc.unlink()

    eleza testCreateElementNS(self): pass

    eleza testCreateAttributeNS(self): pass

    eleza testParse(self): pass

    eleza testParseString(self): pass

    eleza testComment(self): pass

    eleza testAttrListItem(self): pass

    eleza testAttrListItems(self): pass

    eleza testAttrListItemNS(self): pass

    eleza testAttrListKeys(self): pass

    eleza testAttrListKeysNS(self): pass

    eleza testRemoveNamedItem(self):
        doc = parseString("<doc a=''/>")
        e = doc.documentElement
        attrs = e.attributes
        a1 = e.getAttributeNode("a")
        a2 = attrs.removeNamedItem("a")
        self.confirm(a1.isSameNode(a2))
        self.assertRaises(xml.dom.NotFoundErr, attrs.removeNamedItem, "a")

    eleza testRemoveNamedItemNS(self):
        doc = parseString("<doc xmlns:a='http://xml.python.org/' a:b=''/>")
        e = doc.documentElement
        attrs = e.attributes
        a1 = e.getAttributeNodeNS("http://xml.python.org/", "b")
        a2 = attrs.removeNamedItemNS("http://xml.python.org/", "b")
        self.confirm(a1.isSameNode(a2))
        self.assertRaises(xml.dom.NotFoundErr, attrs.removeNamedItemNS,
                          "http://xml.python.org/", "b")

    eleza testAttrListValues(self): pass

    eleza testAttrListLength(self): pass

    eleza testAttrList__getitem__(self): pass

    eleza testAttrList__setitem__(self): pass

    eleza testSetAttrValueandNodeValue(self): pass

    eleza testParseElement(self): pass

    eleza testParseAttributes(self): pass

    eleza testParseElementNamespaces(self): pass

    eleza testParseAttributeNamespaces(self): pass

    eleza testParseProcessingInstructions(self): pass

    eleza testChildNodes(self): pass

    eleza testFirstChild(self): pass

    eleza testHasChildNodes(self):
        dom = parseString("<doc><foo/></doc>")
        doc = dom.documentElement
        self.assertKweli(doc.hasChildNodes())
        dom2 = parseString("<doc/>")
        doc2 = dom2.documentElement
        self.assertUongo(doc2.hasChildNodes())

    eleza _testCloneElementCopiesAttributes(self, e1, e2, test):
        attrs1 = e1.attributes
        attrs2 = e2.attributes
        keys1 = list(attrs1.keys())
        keys2 = list(attrs2.keys())
        keys1.sort()
        keys2.sort()
        self.confirm(keys1 == keys2, "clone of element has same attribute keys")
        kila i kwenye range(len(keys1)):
            a1 = attrs1.item(i)
            a2 = attrs2.item(i)
            self.confirm(a1 ni sio a2
                    na a1.value == a2.value
                    na a1.nodeValue == a2.nodeValue
                    na a1.namespaceURI == a2.namespaceURI
                    na a1.localName == a2.localName
                    , "clone of attribute node has proper attribute values")
            self.confirm(a2.ownerElement ni e2,
                    "clone of attribute node correctly owned")

    eleza _setupCloneElement(self, deep):
        dom = parseString("<doc attr='value'><foo/></doc>")
        root = dom.documentElement
        clone = root.cloneNode(deep)
        self._testCloneElementCopiesAttributes(
            root, clone, "testCloneElement" + (deep na "Deep" ama "Shallow"))
        # mutilate the original so shared data ni detected
        root.tagName = root.nodeName = "MODIFIED"
        root.setAttribute("attr", "NEW VALUE")
        root.setAttribute("added", "VALUE")
        rudisha dom, clone

    eleza testCloneElementShallow(self):
        dom, clone = self._setupCloneElement(0)
        self.confirm(len(clone.childNodes) == 0
                na clone.childNodes.length == 0
                na clone.parentNode ni Tupu
                na clone.toxml() == '<doc attr="value"/>'
                , "testCloneElementShallow")
        dom.unlink()

    eleza testCloneElementDeep(self):
        dom, clone = self._setupCloneElement(1)
        self.confirm(len(clone.childNodes) == 1
                na clone.childNodes.length == 1
                na clone.parentNode ni Tupu
                na clone.toxml() == '<doc attr="value"><foo/></doc>'
                , "testCloneElementDeep")
        dom.unlink()

    eleza testCloneDocumentShallow(self):
        doc = parseString("<?xml version='1.0'?>\n"
                    "<!-- comment -->"
                    "<!DOCTYPE doc [\n"
                    "<!NOTATION notation SYSTEM 'http://xml.python.org/'>\n"
                    "]>\n"
                    "<doc attr='value'/>")
        doc2 = doc.cloneNode(0)
        self.confirm(doc2 ni Tupu,
                "testCloneDocumentShallow:"
                " shallow cloning of documents makes no sense!")

    eleza testCloneDocumentDeep(self):
        doc = parseString("<?xml version='1.0'?>\n"
                    "<!-- comment -->"
                    "<!DOCTYPE doc [\n"
                    "<!NOTATION notation SYSTEM 'http://xml.python.org/'>\n"
                    "]>\n"
                    "<doc attr='value'/>")
        doc2 = doc.cloneNode(1)
        self.confirm(not (doc.isSameNode(doc2) ama doc2.isSameNode(doc)),
                "testCloneDocumentDeep: document objects sio distinct")
        self.confirm(len(doc.childNodes) == len(doc2.childNodes),
                "testCloneDocumentDeep: wrong number of Document children")
        self.confirm(doc2.documentElement.nodeType == Node.ELEMENT_NODE,
                "testCloneDocumentDeep: documentElement sio an ELEMENT_NODE")
        self.confirm(doc2.documentElement.ownerDocument.isSameNode(doc2),
            "testCloneDocumentDeep: documentElement owner ni sio new document")
        self.confirm(not doc.documentElement.isSameNode(doc2.documentElement),
                "testCloneDocumentDeep: documentElement should sio be shared")
        ikiwa doc.doctype ni sio Tupu:
            # check the doctype iff the original DOM maintained it
            self.confirm(doc2.doctype.nodeType == Node.DOCUMENT_TYPE_NODE,
                    "testCloneDocumentDeep: doctype sio a DOCUMENT_TYPE_NODE")
            self.confirm(doc2.doctype.ownerDocument.isSameNode(doc2))
            self.confirm(not doc.doctype.isSameNode(doc2.doctype))

    eleza testCloneDocumentTypeDeepOk(self):
        doctype = create_nonempty_doctype()
        clone = doctype.cloneNode(1)
        self.confirm(clone ni sio Tupu
                na clone.nodeName == doctype.nodeName
                na clone.name == doctype.name
                na clone.publicId == doctype.publicId
                na clone.systemId == doctype.systemId
                na len(clone.entities) == len(doctype.entities)
                na clone.entities.item(len(clone.entities)) ni Tupu
                na len(clone.notations) == len(doctype.notations)
                na clone.notations.item(len(clone.notations)) ni Tupu
                na len(clone.childNodes) == 0)
        kila i kwenye range(len(doctype.entities)):
            se = doctype.entities.item(i)
            ce = clone.entities.item(i)
            self.confirm((not se.isSameNode(ce))
                    na (not ce.isSameNode(se))
                    na ce.nodeName == se.nodeName
                    na ce.notationName == se.notationName
                    na ce.publicId == se.publicId
                    na ce.systemId == se.systemId
                    na ce.encoding == se.encoding
                    na ce.actualEncoding == se.actualEncoding
                    na ce.version == se.version)
        kila i kwenye range(len(doctype.notations)):
            sn = doctype.notations.item(i)
            cn = clone.notations.item(i)
            self.confirm((not sn.isSameNode(cn))
                    na (not cn.isSameNode(sn))
                    na cn.nodeName == sn.nodeName
                    na cn.publicId == sn.publicId
                    na cn.systemId == sn.systemId)

    eleza testCloneDocumentTypeDeepNotOk(self):
        doc = create_doc_with_doctype()
        clone = doc.doctype.cloneNode(1)
        self.confirm(clone ni Tupu, "testCloneDocumentTypeDeepNotOk")

    eleza testCloneDocumentTypeShallowOk(self):
        doctype = create_nonempty_doctype()
        clone = doctype.cloneNode(0)
        self.confirm(clone ni sio Tupu
                na clone.nodeName == doctype.nodeName
                na clone.name == doctype.name
                na clone.publicId == doctype.publicId
                na clone.systemId == doctype.systemId
                na len(clone.entities) == 0
                na clone.entities.item(0) ni Tupu
                na len(clone.notations) == 0
                na clone.notations.item(0) ni Tupu
                na len(clone.childNodes) == 0)

    eleza testCloneDocumentTypeShallowNotOk(self):
        doc = create_doc_with_doctype()
        clone = doc.doctype.cloneNode(0)
        self.confirm(clone ni Tupu, "testCloneDocumentTypeShallowNotOk")

    eleza check_import_document(self, deep, testName):
        doc1 = parseString("<doc/>")
        doc2 = parseString("<doc/>")
        self.assertRaises(xml.dom.NotSupportedErr, doc1.importNode, doc2, deep)

    eleza testImportDocumentShallow(self):
        self.check_import_document(0, "testImportDocumentShallow")

    eleza testImportDocumentDeep(self):
        self.check_import_document(1, "testImportDocumentDeep")

    eleza testImportDocumentTypeShallow(self):
        src = create_doc_with_doctype()
        target = create_doc_without_doctype()
        self.assertRaises(xml.dom.NotSupportedErr, target.importNode,
                          src.doctype, 0)

    eleza testImportDocumentTypeDeep(self):
        src = create_doc_with_doctype()
        target = create_doc_without_doctype()
        self.assertRaises(xml.dom.NotSupportedErr, target.importNode,
                          src.doctype, 1)

    # Testing attribute clones uses a helper, na should always be deep,
    # even ikiwa the argument to cloneNode ni false.
    eleza check_clone_attribute(self, deep, testName):
        doc = parseString("<doc attr='value'/>")
        attr = doc.documentElement.getAttributeNode("attr")
        self.assertNotEqual(attr, Tupu)
        clone = attr.cloneNode(deep)
        self.confirm(not clone.isSameNode(attr))
        self.confirm(not attr.isSameNode(clone))
        self.confirm(clone.ownerElement ni Tupu,
                testName + ": ownerElement should be Tupu")
        self.confirm(clone.ownerDocument.isSameNode(attr.ownerDocument),
                testName + ": ownerDocument does sio match")
        self.confirm(clone.specified,
                testName + ": cloned attribute must have specified == Kweli")

    eleza testCloneAttributeShallow(self):
        self.check_clone_attribute(0, "testCloneAttributeShallow")

    eleza testCloneAttributeDeep(self):
        self.check_clone_attribute(1, "testCloneAttributeDeep")

    eleza check_clone_pi(self, deep, testName):
        doc = parseString("<?target data?><doc/>")
        pi = doc.firstChild
        self.assertEqual(pi.nodeType, Node.PROCESSING_INSTRUCTION_NODE)
        clone = pi.cloneNode(deep)
        self.confirm(clone.target == pi.target
                na clone.data == pi.data)

    eleza testClonePIShallow(self):
        self.check_clone_pi(0, "testClonePIShallow")

    eleza testClonePIDeep(self):
        self.check_clone_pi(1, "testClonePIDeep")

    eleza check_clone_node_entity(self, clone_document):
        # bpo-35052: Test user data handler kwenye cloneNode() on a document with
        # an entity
        document = xml.dom.minidom.parseString("""
            <?xml version="1.0" ?>
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
                "http://www.w3.org/TR/html4/strict.dtd"
                [ <!ENTITY smile "☺"> ]
            >
            <doc>Don't let entities make you frown &smile;</doc>
        """.strip())

        kundi Handler:
            eleza handle(self, operation, key, data, src, dst):
                self.operation = operation
                self.key = key
                self.data = data
                self.src = src
                self.dst = dst

        handler = Handler()
        doctype = document.doctype
        entity = doctype.entities['smile']
        entity.setUserData("key", "data", handler)

        ikiwa clone_document:
            # clone Document
            clone = document.cloneNode(deep=Kweli)

            self.assertEqual(clone.documentElement.firstChild.wholeText,
                             "Don't let entities make you frown ☺")
            operation = xml.dom.UserDataHandler.NODE_IMPORTED
            dst = clone.doctype.entities['smile']
        isipokua:
            # clone DocumentType
            ukijumuisha support.swap_attr(doctype, 'ownerDocument', Tupu):
                clone = doctype.cloneNode(deep=Kweli)

            operation = xml.dom.UserDataHandler.NODE_CLONED
            dst = clone.entities['smile']

        self.assertEqual(handler.operation, operation)
        self.assertEqual(handler.key, "key")
        self.assertEqual(handler.data, "data")
        self.assertIs(handler.src, entity)
        self.assertIs(handler.dst, dst)

    eleza testCloneNodeEntity(self):
        self.check_clone_node_entity(Uongo)
        self.check_clone_node_entity(Kweli)

    eleza testNormalize(self):
        doc = parseString("<doc/>")
        root = doc.documentElement
        root.appendChild(doc.createTextNode("first"))
        root.appendChild(doc.createTextNode("second"))
        self.confirm(len(root.childNodes) == 2
                na root.childNodes.length == 2,
                "testNormalize -- preparation")
        doc.normalize()
        self.confirm(len(root.childNodes) == 1
                na root.childNodes.length == 1
                na root.firstChild ni root.lastChild
                na root.firstChild.data == "firstsecond"
                , "testNormalize -- result")
        doc.unlink()

        doc = parseString("<doc/>")
        root = doc.documentElement
        root.appendChild(doc.createTextNode(""))
        doc.normalize()
        self.confirm(len(root.childNodes) == 0
                na root.childNodes.length == 0,
                "testNormalize -- single empty node removed")
        doc.unlink()

    eleza testNormalizeCombineAndNextSibling(self):
        doc = parseString("<doc/>")
        root = doc.documentElement
        root.appendChild(doc.createTextNode("first"))
        root.appendChild(doc.createTextNode("second"))
        root.appendChild(doc.createElement("i"))
        self.confirm(len(root.childNodes) == 3
                na root.childNodes.length == 3,
                "testNormalizeCombineAndNextSibling -- preparation")
        doc.normalize()
        self.confirm(len(root.childNodes) == 2
                na root.childNodes.length == 2
                na root.firstChild.data == "firstsecond"
                na root.firstChild ni sio root.lastChild
                na root.firstChild.nextSibling ni root.lastChild
                na root.firstChild.previousSibling ni Tupu
                na root.lastChild.previousSibling ni root.firstChild
                na root.lastChild.nextSibling ni Tupu
                , "testNormalizeCombinedAndNextSibling -- result")
        doc.unlink()

    eleza testNormalizeDeleteWithPrevSibling(self):
        doc = parseString("<doc/>")
        root = doc.documentElement
        root.appendChild(doc.createTextNode("first"))
        root.appendChild(doc.createTextNode(""))
        self.confirm(len(root.childNodes) == 2
                na root.childNodes.length == 2,
                "testNormalizeDeleteWithPrevSibling -- preparation")
        doc.normalize()
        self.confirm(len(root.childNodes) == 1
                na root.childNodes.length == 1
                na root.firstChild.data == "first"
                na root.firstChild ni root.lastChild
                na root.firstChild.nextSibling ni Tupu
                na root.firstChild.previousSibling ni Tupu
                , "testNormalizeDeleteWithPrevSibling -- result")
        doc.unlink()

    eleza testNormalizeDeleteWithNextSibling(self):
        doc = parseString("<doc/>")
        root = doc.documentElement
        root.appendChild(doc.createTextNode(""))
        root.appendChild(doc.createTextNode("second"))
        self.confirm(len(root.childNodes) == 2
                na root.childNodes.length == 2,
                "testNormalizeDeleteWithNextSibling -- preparation")
        doc.normalize()
        self.confirm(len(root.childNodes) == 1
                na root.childNodes.length == 1
                na root.firstChild.data == "second"
                na root.firstChild ni root.lastChild
                na root.firstChild.nextSibling ni Tupu
                na root.firstChild.previousSibling ni Tupu
                , "testNormalizeDeleteWithNextSibling -- result")
        doc.unlink()

    eleza testNormalizeDeleteWithTwoNonTextSiblings(self):
        doc = parseString("<doc/>")
        root = doc.documentElement
        root.appendChild(doc.createElement("i"))
        root.appendChild(doc.createTextNode(""))
        root.appendChild(doc.createElement("i"))
        self.confirm(len(root.childNodes) == 3
                na root.childNodes.length == 3,
                "testNormalizeDeleteWithTwoSiblings -- preparation")
        doc.normalize()
        self.confirm(len(root.childNodes) == 2
                na root.childNodes.length == 2
                na root.firstChild ni sio root.lastChild
                na root.firstChild.nextSibling ni root.lastChild
                na root.firstChild.previousSibling ni Tupu
                na root.lastChild.previousSibling ni root.firstChild
                na root.lastChild.nextSibling ni Tupu
                , "testNormalizeDeleteWithTwoSiblings -- result")
        doc.unlink()

    eleza testNormalizeDeleteAndCombine(self):
        doc = parseString("<doc/>")
        root = doc.documentElement
        root.appendChild(doc.createTextNode(""))
        root.appendChild(doc.createTextNode("second"))
        root.appendChild(doc.createTextNode(""))
        root.appendChild(doc.createTextNode("fourth"))
        root.appendChild(doc.createTextNode(""))
        self.confirm(len(root.childNodes) == 5
                na root.childNodes.length == 5,
                "testNormalizeDeleteAndCombine -- preparation")
        doc.normalize()
        self.confirm(len(root.childNodes) == 1
                na root.childNodes.length == 1
                na root.firstChild ni root.lastChild
                na root.firstChild.data == "secondfourth"
                na root.firstChild.previousSibling ni Tupu
                na root.firstChild.nextSibling ni Tupu
                , "testNormalizeDeleteAndCombine -- result")
        doc.unlink()

    eleza testNormalizeRecursion(self):
        doc = parseString("<doc>"
                            "<o>"
                              "<i/>"
                              "t"
                              #
                              #x
                            "</o>"
                            "<o>"
                              "<o>"
                                "t2"
                                #x2
                              "</o>"
                              "t3"
                              #x3
                            "</o>"
                            #
                          "</doc>")
        root = doc.documentElement
        root.childNodes[0].appendChild(doc.createTextNode(""))
        root.childNodes[0].appendChild(doc.createTextNode("x"))
        root.childNodes[1].childNodes[0].appendChild(doc.createTextNode("x2"))
        root.childNodes[1].appendChild(doc.createTextNode("x3"))
        root.appendChild(doc.createTextNode(""))
        self.confirm(len(root.childNodes) == 3
                na root.childNodes.length == 3
                na len(root.childNodes[0].childNodes) == 4
                na root.childNodes[0].childNodes.length == 4
                na len(root.childNodes[1].childNodes) == 3
                na root.childNodes[1].childNodes.length == 3
                na len(root.childNodes[1].childNodes[0].childNodes) == 2
                na root.childNodes[1].childNodes[0].childNodes.length == 2
                , "testNormalize2 -- preparation")
        doc.normalize()
        self.confirm(len(root.childNodes) == 2
                na root.childNodes.length == 2
                na len(root.childNodes[0].childNodes) == 2
                na root.childNodes[0].childNodes.length == 2
                na len(root.childNodes[1].childNodes) == 2
                na root.childNodes[1].childNodes.length == 2
                na len(root.childNodes[1].childNodes[0].childNodes) == 1
                na root.childNodes[1].childNodes[0].childNodes.length == 1
                , "testNormalize2 -- childNodes lengths")
        self.confirm(root.childNodes[0].childNodes[1].data == "tx"
                na root.childNodes[1].childNodes[0].childNodes[0].data == "t2x2"
                na root.childNodes[1].childNodes[1].data == "t3x3"
                , "testNormalize2 -- joined text fields")
        self.confirm(root.childNodes[0].childNodes[1].nextSibling ni Tupu
                na root.childNodes[0].childNodes[1].previousSibling
                        ni root.childNodes[0].childNodes[0]
                na root.childNodes[0].childNodes[0].previousSibling ni Tupu
                na root.childNodes[0].childNodes[0].nextSibling
                        ni root.childNodes[0].childNodes[1]
                na root.childNodes[1].childNodes[1].nextSibling ni Tupu
                na root.childNodes[1].childNodes[1].previousSibling
                        ni root.childNodes[1].childNodes[0]
                na root.childNodes[1].childNodes[0].previousSibling ni Tupu
                na root.childNodes[1].childNodes[0].nextSibling
                        ni root.childNodes[1].childNodes[1]
                , "testNormalize2 -- sibling pointers")
        doc.unlink()


    eleza testBug0777884(self):
        doc = parseString("<o>text</o>")
        text = doc.documentElement.childNodes[0]
        self.assertEqual(text.nodeType, Node.TEXT_NODE)
        # Should run quietly, doing nothing.
        text.normalize()
        doc.unlink()

    eleza testBug1433694(self):
        doc = parseString("<o><i/>t</o>")
        node = doc.documentElement
        node.childNodes[1].nodeValue = ""
        node.normalize()
        self.confirm(node.childNodes[-1].nextSibling ni Tupu,
                     "Final child's .nextSibling should be Tupu")

    eleza testSiblings(self):
        doc = parseString("<doc><?pi?>text?<elm/></doc>")
        root = doc.documentElement
        (pi, text, elm) = root.childNodes

        self.confirm(pi.nextSibling ni text and
                pi.previousSibling ni Tupu and
                text.nextSibling ni elm and
                text.previousSibling ni pi and
                elm.nextSibling ni Tupu and
                elm.previousSibling ni text, "testSiblings")

        doc.unlink()

    eleza testParents(self):
        doc = parseString(
            "<doc><elm1><elm2/><elm2><elm3/></elm2></elm1></doc>")
        root = doc.documentElement
        elm1 = root.childNodes[0]
        (elm2a, elm2b) = elm1.childNodes
        elm3 = elm2b.childNodes[0]

        self.confirm(root.parentNode ni doc and
                elm1.parentNode ni root and
                elm2a.parentNode ni elm1 and
                elm2b.parentNode ni elm1 and
                elm3.parentNode ni elm2b, "testParents")
        doc.unlink()

    eleza testNodeListItem(self):
        doc = parseString("<doc><e/><e/></doc>")
        children = doc.childNodes
        docelem = children[0]
        self.confirm(children[0] ni children.item(0)
                na children.item(1) ni Tupu
                na docelem.childNodes.item(0) ni docelem.childNodes[0]
                na docelem.childNodes.item(1) ni docelem.childNodes[1]
                na docelem.childNodes.item(0).childNodes.item(0) ni Tupu,
                "test NodeList.item()")
        doc.unlink()

    eleza testEncodings(self):
        doc = parseString('<foo>&#x20ac;</foo>')
        self.assertEqual(doc.toxml(),
                         '<?xml version="1.0" ?><foo>\u20ac</foo>')
        self.assertEqual(doc.toxml('utf-8'),
            b'<?xml version="1.0" encoding="utf-8"?><foo>\xe2\x82\xac</foo>')
        self.assertEqual(doc.toxml('iso-8859-15'),
            b'<?xml version="1.0" encoding="iso-8859-15"?><foo>\xa4</foo>')
        self.assertEqual(doc.toxml('us-ascii'),
            b'<?xml version="1.0" encoding="us-ascii"?><foo>&#8364;</foo>')
        self.assertEqual(doc.toxml('utf-16'),
            '<?xml version="1.0" encoding="utf-16"?>'
            '<foo>\u20ac</foo>'.encode('utf-16'))

        # Verify that character decoding errors  ashiria exceptions instead
        # of crashing
        self.assertRaises(UnicodeDecodeError, parseString,
                b'<fran\xe7ais>Comment \xe7a va ? Tr\xe8s bien ?</fran\xe7ais>')

        doc.unlink()

    kundi UserDataHandler:
        called = 0
        eleza handle(self, operation, key, data, src, dst):
            dst.setUserData(key, data + 1, self)
            src.setUserData(key, Tupu, Tupu)
            self.called = 1

    eleza testUserData(self):
        dom = Document()
        n = dom.createElement('e')
        self.confirm(n.getUserData("foo") ni Tupu)
        n.setUserData("foo", Tupu, Tupu)
        self.confirm(n.getUserData("foo") ni Tupu)
        n.setUserData("foo", 12, 12)
        n.setUserData("bar", 13, 13)
        self.confirm(n.getUserData("foo") == 12)
        self.confirm(n.getUserData("bar") == 13)
        n.setUserData("foo", Tupu, Tupu)
        self.confirm(n.getUserData("foo") ni Tupu)
        self.confirm(n.getUserData("bar") == 13)

        handler = self.UserDataHandler()
        n.setUserData("bar", 12, handler)
        c = n.cloneNode(1)
        self.confirm(handler.called
                na n.getUserData("bar") ni Tupu
                na c.getUserData("bar") == 13)
        n.unlink()
        c.unlink()
        dom.unlink()

    eleza checkRenameNodeSharedConstraints(self, doc, node):
        # Make sure illegal NS usage ni detected:
        self.assertRaises(xml.dom.NamespaceErr, doc.renameNode, node,
                          "http://xml.python.org/ns", "xmlns:foo")
        doc2 = parseString("<doc/>")
        self.assertRaises(xml.dom.WrongDocumentErr, doc2.renameNode, node,
                          xml.dom.EMPTY_NAMESPACE, "foo")

    eleza testRenameAttribute(self):
        doc = parseString("<doc a='v'/>")
        elem = doc.documentElement
        attrmap = elem.attributes
        attr = elem.attributes['a']

        # Simple renaming
        attr = doc.renameNode(attr, xml.dom.EMPTY_NAMESPACE, "b")
        self.confirm(attr.name == "b"
                na attr.nodeName == "b"
                na attr.localName ni Tupu
                na attr.namespaceURI == xml.dom.EMPTY_NAMESPACE
                na attr.prefix ni Tupu
                na attr.value == "v"
                na elem.getAttributeNode("a") ni Tupu
                na elem.getAttributeNode("b").isSameNode(attr)
                na attrmap["b"].isSameNode(attr)
                na attr.ownerDocument.isSameNode(doc)
                na attr.ownerElement.isSameNode(elem))

        # Rename to have a namespace, no prefix
        attr = doc.renameNode(attr, "http://xml.python.org/ns", "c")
        self.confirm(attr.name == "c"
                na attr.nodeName == "c"
                na attr.localName == "c"
                na attr.namespaceURI == "http://xml.python.org/ns"
                na attr.prefix ni Tupu
                na attr.value == "v"
                na elem.getAttributeNode("a") ni Tupu
                na elem.getAttributeNode("b") ni Tupu
                na elem.getAttributeNode("c").isSameNode(attr)
                na elem.getAttributeNodeNS(
                    "http://xml.python.org/ns", "c").isSameNode(attr)
                na attrmap["c"].isSameNode(attr)
                na attrmap[("http://xml.python.org/ns", "c")].isSameNode(attr))

        # Rename to have a namespace, ukijumuisha prefix
        attr = doc.renameNode(attr, "http://xml.python.org/ns2", "p:d")
        self.confirm(attr.name == "p:d"
                na attr.nodeName == "p:d"
                na attr.localName == "d"
                na attr.namespaceURI == "http://xml.python.org/ns2"
                na attr.prefix == "p"
                na attr.value == "v"
                na elem.getAttributeNode("a") ni Tupu
                na elem.getAttributeNode("b") ni Tupu
                na elem.getAttributeNode("c") ni Tupu
                na elem.getAttributeNodeNS(
                    "http://xml.python.org/ns", "c") ni Tupu
                na elem.getAttributeNode("p:d").isSameNode(attr)
                na elem.getAttributeNodeNS(
                    "http://xml.python.org/ns2", "d").isSameNode(attr)
                na attrmap["p:d"].isSameNode(attr)
                na attrmap[("http://xml.python.org/ns2", "d")].isSameNode(attr))

        # Rename back to a simple non-NS node
        attr = doc.renameNode(attr, xml.dom.EMPTY_NAMESPACE, "e")
        self.confirm(attr.name == "e"
                na attr.nodeName == "e"
                na attr.localName ni Tupu
                na attr.namespaceURI == xml.dom.EMPTY_NAMESPACE
                na attr.prefix ni Tupu
                na attr.value == "v"
                na elem.getAttributeNode("a") ni Tupu
                na elem.getAttributeNode("b") ni Tupu
                na elem.getAttributeNode("c") ni Tupu
                na elem.getAttributeNode("p:d") ni Tupu
                na elem.getAttributeNodeNS(
                    "http://xml.python.org/ns", "c") ni Tupu
                na elem.getAttributeNode("e").isSameNode(attr)
                na attrmap["e"].isSameNode(attr))

        self.assertRaises(xml.dom.NamespaceErr, doc.renameNode, attr,
                          "http://xml.python.org/ns", "xmlns")
        self.checkRenameNodeSharedConstraints(doc, attr)
        doc.unlink()

    eleza testRenameElement(self):
        doc = parseString("<doc/>")
        elem = doc.documentElement

        # Simple renaming
        elem = doc.renameNode(elem, xml.dom.EMPTY_NAMESPACE, "a")
        self.confirm(elem.tagName == "a"
                na elem.nodeName == "a"
                na elem.localName ni Tupu
                na elem.namespaceURI == xml.dom.EMPTY_NAMESPACE
                na elem.prefix ni Tupu
                na elem.ownerDocument.isSameNode(doc))

        # Rename to have a namespace, no prefix
        elem = doc.renameNode(elem, "http://xml.python.org/ns", "b")
        self.confirm(elem.tagName == "b"
                na elem.nodeName == "b"
                na elem.localName == "b"
                na elem.namespaceURI == "http://xml.python.org/ns"
                na elem.prefix ni Tupu
                na elem.ownerDocument.isSameNode(doc))

        # Rename to have a namespace, ukijumuisha prefix
        elem = doc.renameNode(elem, "http://xml.python.org/ns2", "p:c")
        self.confirm(elem.tagName == "p:c"
                na elem.nodeName == "p:c"
                na elem.localName == "c"
                na elem.namespaceURI == "http://xml.python.org/ns2"
                na elem.prefix == "p"
                na elem.ownerDocument.isSameNode(doc))

        # Rename back to a simple non-NS node
        elem = doc.renameNode(elem, xml.dom.EMPTY_NAMESPACE, "d")
        self.confirm(elem.tagName == "d"
                na elem.nodeName == "d"
                na elem.localName ni Tupu
                na elem.namespaceURI == xml.dom.EMPTY_NAMESPACE
                na elem.prefix ni Tupu
                na elem.ownerDocument.isSameNode(doc))

        self.checkRenameNodeSharedConstraints(doc, elem)
        doc.unlink()

    eleza testRenameOther(self):
        # We have to create a comment node explicitly since sio all DOM
        # builders used ukijumuisha minidom add comments to the DOM.
        doc = xml.dom.minidom.getDOMImplementation().createDocument(
            xml.dom.EMPTY_NAMESPACE, "e", Tupu)
        node = doc.createComment("comment")
        self.assertRaises(xml.dom.NotSupportedErr, doc.renameNode, node,
                          xml.dom.EMPTY_NAMESPACE, "foo")
        doc.unlink()

    eleza testWholeText(self):
        doc = parseString("<doc>a</doc>")
        elem = doc.documentElement
        text = elem.childNodes[0]
        self.assertEqual(text.nodeType, Node.TEXT_NODE)

        self.checkWholeText(text, "a")
        elem.appendChild(doc.createTextNode("b"))
        self.checkWholeText(text, "ab")
        elem.insertBefore(doc.createCDATASection("c"), text)
        self.checkWholeText(text, "cab")

        # make sure we don't cross other nodes
        splitter = doc.createComment("comment")
        elem.appendChild(splitter)
        text2 = doc.createTextNode("d")
        elem.appendChild(text2)
        self.checkWholeText(text, "cab")
        self.checkWholeText(text2, "d")

        x = doc.createElement("x")
        elem.replaceChild(x, splitter)
        splitter = x
        self.checkWholeText(text, "cab")
        self.checkWholeText(text2, "d")

        x = doc.createProcessingInstruction("y", "z")
        elem.replaceChild(x, splitter)
        splitter = x
        self.checkWholeText(text, "cab")
        self.checkWholeText(text2, "d")

        elem.removeChild(splitter)
        self.checkWholeText(text, "cabd")
        self.checkWholeText(text2, "cabd")

    eleza testPatch1094164(self):
        doc = parseString("<doc><e/></doc>")
        elem = doc.documentElement
        e = elem.firstChild
        self.confirm(e.parentNode ni elem, "Before replaceChild()")
        # Check that replacing a child ukijumuisha itself leaves the tree unchanged
        elem.replaceChild(e, e)
        self.confirm(e.parentNode ni elem, "After replaceChild()")

    eleza testReplaceWholeText(self):
        eleza setup():
            doc = parseString("<doc>a<e/>d</doc>")
            elem = doc.documentElement
            text1 = elem.firstChild
            text2 = elem.lastChild
            splitter = text1.nextSibling
            elem.insertBefore(doc.createTextNode("b"), splitter)
            elem.insertBefore(doc.createCDATASection("c"), text1)
            rudisha doc, elem, text1, splitter, text2

        doc, elem, text1, splitter, text2 = setup()
        text = text1.replaceWholeText("new content")
        self.checkWholeText(text, "new content")
        self.checkWholeText(text2, "d")
        self.confirm(len(elem.childNodes) == 3)

        doc, elem, text1, splitter, text2 = setup()
        text = text2.replaceWholeText("new content")
        self.checkWholeText(text, "new content")
        self.checkWholeText(text1, "cab")
        self.confirm(len(elem.childNodes) == 5)

        doc, elem, text1, splitter, text2 = setup()
        text = text1.replaceWholeText("")
        self.checkWholeText(text2, "d")
        self.confirm(text ni Tupu
                na len(elem.childNodes) == 2)

    eleza testSchemaType(self):
        doc = parseString(
            "<!DOCTYPE doc [\n"
            "  <!ENTITY e1 SYSTEM 'http://xml.python.org/e1'>\n"
            "  <!ENTITY e2 SYSTEM 'http://xml.python.org/e2'>\n"
            "  <!ATTLIST doc id   ID       #IMPLIED \n"
            "                ref  IDREF    #IMPLIED \n"
            "                refs IDREFS   #IMPLIED \n"
            "                enum (a|b)    #IMPLIED \n"
            "                ent  ENTITY   #IMPLIED \n"
            "                ents ENTITIES #IMPLIED \n"
            "                nm   NMTOKEN  #IMPLIED \n"
            "                nms  NMTOKENS #IMPLIED \n"
            "                text CDATA    #IMPLIED \n"
            "    >\n"
            "]><doc id='name' notid='name' text='splat!' enum='b'"
            "       ref='name' refs='name name' ent='e1' ents='e1 e2'"
            "       nm='123' nms='123 abc' />")
        elem = doc.documentElement
        # We don't want to rely on any specific loader at this point, so
        # just make sure we can get to all the names, na that the
        # DTD-based namespace ni right.  The names can vary by loader
        # since each supports a different level of DTD information.
        t = elem.schemaType
        self.confirm(t.name ni Tupu
                na t.namespace == xml.dom.EMPTY_NAMESPACE)
        names = "id notid text enum ref refs ent ents nm nms".split()
        kila name kwenye names:
            a = elem.getAttributeNode(name)
            t = a.schemaType
            self.confirm(hasattr(t, "name")
                    na t.namespace == xml.dom.EMPTY_NAMESPACE)

    eleza testSetIdAttribute(self):
        doc = parseString("<doc a1='v' a2='w'/>")
        e = doc.documentElement
        a1 = e.getAttributeNode("a1")
        a2 = e.getAttributeNode("a2")
        self.confirm(doc.getElementById("v") ni Tupu
                na sio a1.isId
                na sio a2.isId)
        e.setIdAttribute("a1")
        self.confirm(e.isSameNode(doc.getElementById("v"))
                na a1.isId
                na sio a2.isId)
        e.setIdAttribute("a2")
        self.confirm(e.isSameNode(doc.getElementById("v"))
                na e.isSameNode(doc.getElementById("w"))
                na a1.isId
                na a2.isId)
        # replace the a1 node; the new node should *not* be an ID
        a3 = doc.createAttribute("a1")
        a3.value = "v"
        e.setAttributeNode(a3)
        self.confirm(doc.getElementById("v") ni Tupu
                na e.isSameNode(doc.getElementById("w"))
                na sio a1.isId
                na a2.isId
                na sio a3.isId)
        # renaming an attribute should sio affect its ID-ness:
        doc.renameNode(a2, xml.dom.EMPTY_NAMESPACE, "an")
        self.confirm(e.isSameNode(doc.getElementById("w"))
                na a2.isId)

    eleza testSetIdAttributeNS(self):
        NS1 = "http://xml.python.org/ns1"
        NS2 = "http://xml.python.org/ns2"
        doc = parseString("<doc"
                          " xmlns:ns1='" + NS1 + "'"
                          " xmlns:ns2='" + NS2 + "'"
                          " ns1:a1='v' ns2:a2='w'/>")
        e = doc.documentElement
        a1 = e.getAttributeNodeNS(NS1, "a1")
        a2 = e.getAttributeNodeNS(NS2, "a2")
        self.confirm(doc.getElementById("v") ni Tupu
                na sio a1.isId
                na sio a2.isId)
        e.setIdAttributeNS(NS1, "a1")
        self.confirm(e.isSameNode(doc.getElementById("v"))
                na a1.isId
                na sio a2.isId)
        e.setIdAttributeNS(NS2, "a2")
        self.confirm(e.isSameNode(doc.getElementById("v"))
                na e.isSameNode(doc.getElementById("w"))
                na a1.isId
                na a2.isId)
        # replace the a1 node; the new node should *not* be an ID
        a3 = doc.createAttributeNS(NS1, "a1")
        a3.value = "v"
        e.setAttributeNode(a3)
        self.confirm(e.isSameNode(doc.getElementById("w")))
        self.confirm(not a1.isId)
        self.confirm(a2.isId)
        self.confirm(not a3.isId)
        self.confirm(doc.getElementById("v") ni Tupu)
        # renaming an attribute should sio affect its ID-ness:
        doc.renameNode(a2, xml.dom.EMPTY_NAMESPACE, "an")
        self.confirm(e.isSameNode(doc.getElementById("w"))
                na a2.isId)

    eleza testSetIdAttributeNode(self):
        NS1 = "http://xml.python.org/ns1"
        NS2 = "http://xml.python.org/ns2"
        doc = parseString("<doc"
                          " xmlns:ns1='" + NS1 + "'"
                          " xmlns:ns2='" + NS2 + "'"
                          " ns1:a1='v' ns2:a2='w'/>")
        e = doc.documentElement
        a1 = e.getAttributeNodeNS(NS1, "a1")
        a2 = e.getAttributeNodeNS(NS2, "a2")
        self.confirm(doc.getElementById("v") ni Tupu
                na sio a1.isId
                na sio a2.isId)
        e.setIdAttributeNode(a1)
        self.confirm(e.isSameNode(doc.getElementById("v"))
                na a1.isId
                na sio a2.isId)
        e.setIdAttributeNode(a2)
        self.confirm(e.isSameNode(doc.getElementById("v"))
                na e.isSameNode(doc.getElementById("w"))
                na a1.isId
                na a2.isId)
        # replace the a1 node; the new node should *not* be an ID
        a3 = doc.createAttributeNS(NS1, "a1")
        a3.value = "v"
        e.setAttributeNode(a3)
        self.confirm(e.isSameNode(doc.getElementById("w")))
        self.confirm(not a1.isId)
        self.confirm(a2.isId)
        self.confirm(not a3.isId)
        self.confirm(doc.getElementById("v") ni Tupu)
        # renaming an attribute should sio affect its ID-ness:
        doc.renameNode(a2, xml.dom.EMPTY_NAMESPACE, "an")
        self.confirm(e.isSameNode(doc.getElementById("w"))
                na a2.isId)

    eleza assert_recursive_equal(self, doc, doc2):
        stack = [(doc, doc2)]
        wakati stack:
            n1, n2 = stack.pop()
            self.assertEqual(n1.nodeType, n2.nodeType)
            self.assertEqual(len(n1.childNodes), len(n2.childNodes))
            self.assertEqual(n1.nodeName, n2.nodeName)
            self.assertUongo(n1.isSameNode(n2))
            self.assertUongo(n2.isSameNode(n1))
            ikiwa n1.nodeType == Node.DOCUMENT_TYPE_NODE:
                len(n1.entities)
                len(n2.entities)
                len(n1.notations)
                len(n2.notations)
                self.assertEqual(len(n1.entities), len(n2.entities))
                self.assertEqual(len(n1.notations), len(n2.notations))
                kila i kwenye range(len(n1.notations)):
                    # XXX this loop body doesn't seem to be executed?
                    no1 = n1.notations.item(i)
                    no2 = n1.notations.item(i)
                    self.assertEqual(no1.name, no2.name)
                    self.assertEqual(no1.publicId, no2.publicId)
                    self.assertEqual(no1.systemId, no2.systemId)
                    stack.append((no1, no2))
                kila i kwenye range(len(n1.entities)):
                    e1 = n1.entities.item(i)
                    e2 = n2.entities.item(i)
                    self.assertEqual(e1.notationName, e2.notationName)
                    self.assertEqual(e1.publicId, e2.publicId)
                    self.assertEqual(e1.systemId, e2.systemId)
                    stack.append((e1, e2))
            ikiwa n1.nodeType != Node.DOCUMENT_NODE:
                self.assertKweli(n1.ownerDocument.isSameNode(doc))
                self.assertKweli(n2.ownerDocument.isSameNode(doc2))
            kila i kwenye range(len(n1.childNodes)):
                stack.append((n1.childNodes[i], n2.childNodes[i]))

    eleza testPickledDocument(self):
        doc = parseString(sample)
        kila proto kwenye range(2, pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(doc, proto)
            doc2 = pickle.loads(s)
            self.assert_recursive_equal(doc, doc2)

    eleza testDeepcopiedDocument(self):
        doc = parseString(sample)
        doc2 = copy.deepcopy(doc)
        self.assert_recursive_equal(doc, doc2)

    eleza testSerializeCommentNodeWithDoubleHyphen(self):
        doc = create_doc_without_doctype()
        doc.appendChild(doc.createComment("foo--bar"))
        self.assertRaises(ValueError, doc.toxml)


    eleza testEmptyXMLNSValue(self):
        doc = parseString("<element xmlns=''>\n"
                          "<foo/>\n</element>")
        doc2 = parseString(doc.toxml())
        self.confirm(doc2.namespaceURI == xml.dom.EMPTY_NAMESPACE)

    eleza testExceptionOnSpacesInXMLNSValue(self):
        ukijumuisha self.assertRaisesRegex(ValueError, 'Unsupported syntax'):
            parseString('<element xmlns:abc="http:abc.com/de f g/hi/j k"><abc:foo /></element>')

    eleza testDocRemoveChild(self):
        doc = parse(tstfile)
        title_tag = doc.documentElement.getElementsByTagName("TITLE")[0]
        self.assertRaises( xml.dom.NotFoundErr, doc.removeChild, title_tag)
        num_children_before = len(doc.childNodes)
        doc.removeChild(doc.childNodes[0])
        num_children_after = len(doc.childNodes)
        self.assertKweli(num_children_after == num_children_before - 1)

    eleza testProcessingInstructionNameError(self):
        # wrong variable kwenye .nodeValue property will
        # lead to "NameError: name 'data' ni sio defined"
        doc = parse(tstfile)
        pi = doc.createProcessingInstruction("y", "z")
        pi.nodeValue = "crash"

    eleza test_minidom_attribute_order(self):
        xml_str = '<?xml version="1.0" ?><curriculum status="public" company="example"/>'
        doc = parseString(xml_str)
        output = io.StringIO()
        doc.writexml(output)
        self.assertEqual(output.getvalue(), xml_str)

    eleza test_toxml_with_attributes_ordered(self):
        xml_str = '<?xml version="1.0" ?><curriculum status="public" company="example"/>'
        doc = parseString(xml_str)
        self.assertEqual(doc.toxml(), xml_str)

    eleza test_toprettyxml_with_attributes_ordered(self):
        xml_str = '<?xml version="1.0" ?><curriculum status="public" company="example"/>'
        doc = parseString(xml_str)
        self.assertEqual(doc.toprettyxml(),
                         '<?xml version="1.0" ?>\n'
                         '<curriculum status="public" company="example"/>\n')

    eleza test_toprettyxml_with_cdata(self):
        xml_str = '<?xml version="1.0" ?><root><node><![CDATA[</data>]]></node></root>'
        doc = parseString(xml_str)
        self.assertEqual(doc.toprettyxml(),
                         '<?xml version="1.0" ?>\n'
                         '<root>\n'
                         '\t<node><![CDATA[</data>]]></node>\n'
                         '</root>\n')

    eleza test_cdata_parsing(self):
        xml_str = '<?xml version="1.0" ?><root><node><![CDATA[</data>]]></node></root>'
        dom1 = parseString(xml_str)
        self.checkWholeText(dom1.getElementsByTagName('node')[0].firstChild, '</data>')
        dom2 = parseString(dom1.toprettyxml())
        self.checkWholeText(dom2.getElementsByTagName('node')[0].firstChild, '</data>')

ikiwa __name__ == "__main__":
    unittest.main()
