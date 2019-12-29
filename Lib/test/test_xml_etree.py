# IMPORTANT: the same tests are run kutoka "test_xml_etree_c" kwenye order
# to ensure consistency between the C implementation na the Python
# implementation.
#
# For this purpose, the module-level "ET" symbol ni temporarily
# monkey-patched when running the "test_xml_etree_c" test suite.

agiza copy
agiza functools
agiza html
agiza io
agiza itertools
agiza locale
agiza operator
agiza os
agiza pickle
agiza sys
agiza textwrap
agiza types
agiza unittest
agiza warnings
agiza weakref

kutoka functools agiza partial
kutoka itertools agiza product, islice
kutoka test agiza support
kutoka test.support agiza TESTFN, findfile, import_fresh_module, gc_collect, swap_attr

# pyET ni the pure-Python implementation.
#
# ET ni pyET kwenye test_xml_etree na ni the C accelerated version in
# test_xml_etree_c.
pyET = Tupu
ET = Tupu

SIMPLE_XMLFILE = findfile("simple.xml", subdir="xmltestdata")
jaribu:
    SIMPLE_XMLFILE.encode("utf-8")
tatizo UnicodeEncodeError:
    ashiria unittest.SkipTest("filename ni sio encodable to utf8")
SIMPLE_NS_XMLFILE = findfile("simple-ns.xml", subdir="xmltestdata")
UTF8_BUG_XMLFILE = findfile("expat224_utf8_bug.xml", subdir="xmltestdata")

SAMPLE_XML = """\
<body>
  <tag class='a'>text</tag>
  <tag class='b' />
  <section>
    <tag class='b' id='inner'>subtext</tag>
  </section>
</body>
"""

SAMPLE_SECTION = """\
<section>
  <tag class='b' id='inner'>subtext</tag>
  <nexttag />
  <nextsection>
    <tag />
  </nextsection>
</section>
"""

SAMPLE_XML_NS = """
<body xmlns="http://effbot.org/ns">
  <tag>text</tag>
  <tag />
  <section>
    <tag>subtext</tag>
  </section>
</body>
"""

SAMPLE_XML_NS_ELEMS = """
<root>
<h:table xmlns:h="hello">
  <h:tr>
    <h:td>Apples</h:td>
    <h:td>Bananas</h:td>
  </h:tr>
</h:table>

<f:table xmlns:f="foo">
  <f:name>African Coffee Table</f:name>
  <f:width>80</f:width>
  <f:length>120</f:length>
</f:table>
</root>
"""

ENTITY_XML = """\
<!DOCTYPE points [
<!ENTITY % user-entities SYSTEM 'user-entities.xml'>
%user-entities;
]>
<document>&entity;</document>
"""

EXTERNAL_ENTITY_XML = """\
<!DOCTYPE points [
<!ENTITY entity SYSTEM "file:///non-existing-file.xml">
]>
<document>&entity;</document>
"""

eleza checkwarnings(*filters, quiet=Uongo):
    eleza decorator(test):
        eleza newtest(*args, **kwargs):
            ukijumuisha support.check_warnings(*filters, quiet=quiet):
                test(*args, **kwargs)
        functools.update_wrapper(newtest, test)
        rudisha newtest
    rudisha decorator


kundi ModuleTest(unittest.TestCase):
    eleza test_sanity(self):
        # Import sanity.

        kutoka xml.etree agiza ElementTree
        kutoka xml.etree agiza ElementInclude
        kutoka xml.etree agiza ElementPath

    eleza test_all(self):
        names = ("xml.etree.ElementTree", "_elementtree")
        support.check__all__(self, ET, names, blacklist=("HTML_EMPTY",))


eleza serialize(elem, to_string=Kweli, encoding='unicode', **options):
    ikiwa encoding != 'unicode':
        file = io.BytesIO()
    isipokua:
        file = io.StringIO()
    tree = ET.ElementTree(elem)
    tree.write(file, encoding=encoding, **options)
    ikiwa to_string:
        rudisha file.getvalue()
    isipokua:
        file.seek(0)
        rudisha file

eleza summarize_list(seq):
    rudisha [elem.tag kila elem kwenye seq]


kundi ElementTestCase:
    @classmethod
    eleza setUpClass(cls):
        cls.modules = {pyET, ET}

    eleza pickleRoundTrip(self, obj, name, dumper, loader, proto):
        save_m = sys.modules[name]
        jaribu:
            sys.modules[name] = dumper
            temp = pickle.dumps(obj, proto)
            sys.modules[name] = loader
            result = pickle.loads(temp)
        tatizo pickle.PicklingError kama pe:
            # pyET must be second, because pyET may be (equal to) ET.
            human = dict([(ET, "cET"), (pyET, "pyET")])
            ashiria support.TestFailed("Failed to round-trip %r kutoka %r to %r"
                                     % (obj,
                                        human.get(dumper, dumper),
                                        human.get(loader, loader))) kutoka pe
        mwishowe:
            sys.modules[name] = save_m
        rudisha result

    eleza assertEqualElements(self, alice, bob):
        self.assertIsInstance(alice, (ET.Element, pyET.Element))
        self.assertIsInstance(bob, (ET.Element, pyET.Element))
        self.assertEqual(len(list(alice)), len(list(bob)))
        kila x, y kwenye zip(alice, bob):
            self.assertEqualElements(x, y)
        properties = operator.attrgetter('tag', 'tail', 'text', 'attrib')
        self.assertEqual(properties(alice), properties(bob))

# --------------------------------------------------------------------
# element tree tests

kundi ElementTreeTest(unittest.TestCase):

    eleza serialize_check(self, elem, expected):
        self.assertEqual(serialize(elem), expected)

    eleza test_interface(self):
        # Test element tree interface.

        eleza check_string(string):
            len(string)
            kila char kwenye string:
                self.assertEqual(len(char), 1,
                        msg="expected one-character string, got %r" % char)
            new_string = string + ""
            new_string = string + " "
            string[:0]

        eleza check_mapping(mapping):
            len(mapping)
            keys = mapping.keys()
            items = mapping.items()
            kila key kwenye keys:
                item = mapping[key]
            mapping["key"] = "value"
            self.assertEqual(mapping["key"], "value",
                    msg="expected value string, got %r" % mapping["key"])

        eleza check_element(element):
            self.assertKweli(ET.iselement(element), msg="not an element")
            direlem = dir(element)
            kila attr kwenye 'tag', 'attrib', 'text', 'tail':
                self.assertKweli(hasattr(element, attr),
                        msg='no %s member' % attr)
                self.assertIn(attr, direlem,
                        msg='no %s visible by dir' % attr)

            check_string(element.tag)
            check_mapping(element.attrib)
            ikiwa element.text ni sio Tupu:
                check_string(element.text)
            ikiwa element.tail ni sio Tupu:
                check_string(element.tail)
            kila elem kwenye element:
                check_element(elem)

        element = ET.Element("tag")
        check_element(element)
        tree = ET.ElementTree(element)
        check_element(tree.getroot())
        element = ET.Element("t\xe4g", key="value")
        tree = ET.ElementTree(element)
        self.assertRegex(repr(element), r"^<Element 't\xe4g' at 0x.*>$")
        element = ET.Element("tag", key="value")

        # Make sure all standard element methods exist.

        eleza check_method(method):
            self.assertKweli(hasattr(method, '__call__'),
                    msg="%s sio callable" % method)

        check_method(element.append)
        check_method(element.extend)
        check_method(element.insert)
        check_method(element.remove)
        check_method(element.getchildren)
        check_method(element.find)
        check_method(element.iterfind)
        check_method(element.findall)
        check_method(element.findtext)
        check_method(element.clear)
        check_method(element.get)
        check_method(element.set)
        check_method(element.keys)
        check_method(element.items)
        check_method(element.iter)
        check_method(element.itertext)
        check_method(element.getiterator)

        # These methods rudisha an iterable. See bug 6472.

        eleza check_iter(it):
            check_method(it.__next__)

        check_iter(element.iterfind("tag"))
        check_iter(element.iterfind("*"))
        check_iter(tree.iterfind("tag"))
        check_iter(tree.iterfind("*"))

        # These aliases are provided:

        self.assertEqual(ET.XML, ET.kutokastring)
        self.assertEqual(ET.PI, ET.ProcessingInstruction)

    eleza test_set_attribute(self):
        element = ET.Element('tag')

        self.assertEqual(element.tag, 'tag')
        element.tag = 'Tag'
        self.assertEqual(element.tag, 'Tag')
        element.tag = 'TAG'
        self.assertEqual(element.tag, 'TAG')

        self.assertIsTupu(element.text)
        element.text = 'Text'
        self.assertEqual(element.text, 'Text')
        element.text = 'TEXT'
        self.assertEqual(element.text, 'TEXT')

        self.assertIsTupu(element.tail)
        element.tail = 'Tail'
        self.assertEqual(element.tail, 'Tail')
        element.tail = 'TAIL'
        self.assertEqual(element.tail, 'TAIL')

        self.assertEqual(element.attrib, {})
        element.attrib = {'a': 'b', 'c': 'd'}
        self.assertEqual(element.attrib, {'a': 'b', 'c': 'd'})
        element.attrib = {'A': 'B', 'C': 'D'}
        self.assertEqual(element.attrib, {'A': 'B', 'C': 'D'})

    eleza test_simpleops(self):
        # Basic method sanity checks.

        elem = ET.XML("<body><tag/></body>")
        self.serialize_check(elem, '<body><tag /></body>')
        e = ET.Element("tag2")
        elem.append(e)
        self.serialize_check(elem, '<body><tag /><tag2 /></body>')
        elem.remove(e)
        self.serialize_check(elem, '<body><tag /></body>')
        elem.insert(0, e)
        self.serialize_check(elem, '<body><tag2 /><tag /></body>')
        elem.remove(e)
        elem.extend([e])
        self.serialize_check(elem, '<body><tag /><tag2 /></body>')
        elem.remove(e)

        element = ET.Element("tag", key="value")
        self.serialize_check(element, '<tag key="value" />') # 1
        subelement = ET.Element("subtag")
        element.append(subelement)
        self.serialize_check(element, '<tag key="value"><subtag /></tag>') # 2
        element.insert(0, subelement)
        self.serialize_check(element,
                '<tag key="value"><subtag /><subtag /></tag>') # 3
        element.remove(subelement)
        self.serialize_check(element, '<tag key="value"><subtag /></tag>') # 4
        element.remove(subelement)
        self.serialize_check(element, '<tag key="value" />') # 5
        ukijumuisha self.assertRaises(ValueError) kama cm:
            element.remove(subelement)
        self.assertEqual(str(cm.exception), 'list.remove(x): x haiko kwenye list')
        self.serialize_check(element, '<tag key="value" />') # 6
        element[0:0] = [subelement, subelement, subelement]
        self.serialize_check(element[1], '<subtag />')
        self.assertEqual(element[1:9], [element[1], element[2]])
        self.assertEqual(element[:9:2], [element[0], element[2]])
        toa element[1:2]
        self.serialize_check(element,
                '<tag key="value"><subtag /><subtag /></tag>')

    eleza test_cdata(self):
        # Test CDATA handling (etc).

        self.serialize_check(ET.XML("<tag>hello</tag>"),
                '<tag>hello</tag>')
        self.serialize_check(ET.XML("<tag>&#104;&#101;&#108;&#108;&#111;</tag>"),
                '<tag>hello</tag>')
        self.serialize_check(ET.XML("<tag><![CDATA[hello]]></tag>"),
                '<tag>hello</tag>')

    eleza test_file_init(self):
        stringfile = io.BytesIO(SAMPLE_XML.encode("utf-8"))
        tree = ET.ElementTree(file=stringfile)
        self.assertEqual(tree.find("tag").tag, 'tag')
        self.assertEqual(tree.find("section/tag").tag, 'tag')

        tree = ET.ElementTree(file=SIMPLE_XMLFILE)
        self.assertEqual(tree.find("element").tag, 'element')
        self.assertEqual(tree.find("element/../empty-element").tag,
                'empty-element')

    eleza test_path_cache(self):
        # Check that the path cache behaves sanely.

        kutoka xml.etree agiza ElementPath

        elem = ET.XML(SAMPLE_XML)
        kila i kwenye range(10): ET.ElementTree(elem).find('./'+str(i))
        cache_len_10 = len(ElementPath._cache)
        kila i kwenye range(10): ET.ElementTree(elem).find('./'+str(i))
        self.assertEqual(len(ElementPath._cache), cache_len_10)
        kila i kwenye range(20): ET.ElementTree(elem).find('./'+str(i))
        self.assertGreater(len(ElementPath._cache), cache_len_10)
        kila i kwenye range(600): ET.ElementTree(elem).find('./'+str(i))
        self.assertLess(len(ElementPath._cache), 500)

    eleza test_copy(self):
        # Test copy handling (etc).

        agiza copy
        e1 = ET.XML("<tag>hello<foo/></tag>")
        e2 = copy.copy(e1)
        e3 = copy.deepcopy(e1)
        e1.find("foo").tag = "bar"
        self.serialize_check(e1, '<tag>hello<bar /></tag>')
        self.serialize_check(e2, '<tag>hello<bar /></tag>')
        self.serialize_check(e3, '<tag>hello<foo /></tag>')

    eleza test_attrib(self):
        # Test attribute handling.

        elem = ET.Element("tag")
        elem.get("key") # 1.1
        self.assertEqual(elem.get("key", "default"), 'default') # 1.2

        elem.set("key", "value")
        self.assertEqual(elem.get("key"), 'value') # 1.3

        elem = ET.Element("tag", key="value")
        self.assertEqual(elem.get("key"), 'value') # 2.1
        self.assertEqual(elem.attrib, {'key': 'value'}) # 2.2

        attrib = {"key": "value"}
        elem = ET.Element("tag", attrib)
        attrib.clear() # check kila aliasing issues
        self.assertEqual(elem.get("key"), 'value') # 3.1
        self.assertEqual(elem.attrib, {'key': 'value'}) # 3.2

        attrib = {"key": "value"}
        elem = ET.Element("tag", **attrib)
        attrib.clear() # check kila aliasing issues
        self.assertEqual(elem.get("key"), 'value') # 4.1
        self.assertEqual(elem.attrib, {'key': 'value'}) # 4.2

        elem = ET.Element("tag", {"key": "other"}, key="value")
        self.assertEqual(elem.get("key"), 'value') # 5.1
        self.assertEqual(elem.attrib, {'key': 'value'}) # 5.2

        elem = ET.Element('test')
        elem.text = "aa"
        elem.set('testa', 'testval')
        elem.set('testb', 'test2')
        self.assertEqual(ET.tostring(elem),
                b'<test testa="testval" testb="test2">aa</test>')
        self.assertEqual(sorted(elem.keys()), ['testa', 'testb'])
        self.assertEqual(sorted(elem.items()),
                [('testa', 'testval'), ('testb', 'test2')])
        self.assertEqual(elem.attrib['testb'], 'test2')
        elem.attrib['testb'] = 'test1'
        elem.attrib['testc'] = 'test2'
        self.assertEqual(ET.tostring(elem),
                b'<test testa="testval" testb="test1" testc="test2">aa</test>')

        elem = ET.Element('test')
        elem.set('a', '\r')
        elem.set('b', '\r\n')
        elem.set('c', '\t\n\r ')
        elem.set('d', '\n\n')
        self.assertEqual(ET.tostring(elem),
                b'<test a="&#10;" b="&#10;" c="&#09;&#10;&#10; " d="&#10;&#10;" />')

    eleza test_makeelement(self):
        # Test makeelement handling.

        elem = ET.Element("tag")
        attrib = {"key": "value"}
        subelem = elem.makeelement("subtag", attrib)
        self.assertIsNot(subelem.attrib, attrib, msg="attrib aliasing")
        elem.append(subelem)
        self.serialize_check(elem, '<tag><subtag key="value" /></tag>')

        elem.clear()
        self.serialize_check(elem, '<tag />')
        elem.append(subelem)
        self.serialize_check(elem, '<tag><subtag key="value" /></tag>')
        elem.extend([subelem, subelem])
        self.serialize_check(elem,
            '<tag><subtag key="value" /><subtag key="value" /><subtag key="value" /></tag>')
        elem[:] = [subelem]
        self.serialize_check(elem, '<tag><subtag key="value" /></tag>')
        elem[:] = tuple([subelem])
        self.serialize_check(elem, '<tag><subtag key="value" /></tag>')

    eleza test_parsefile(self):
        # Test parsing kutoka file.

        tree = ET.parse(SIMPLE_XMLFILE)
        stream = io.StringIO()
        tree.write(stream, encoding='unicode')
        self.assertEqual(stream.getvalue(),
                '<root>\n'
                '   <element key="value">text</element>\n'
                '   <element>text</element>tail\n'
                '   <empty-element />\n'
                '</root>')
        tree = ET.parse(SIMPLE_NS_XMLFILE)
        stream = io.StringIO()
        tree.write(stream, encoding='unicode')
        self.assertEqual(stream.getvalue(),
                '<ns0:root xmlns:ns0="namespace">\n'
                '   <ns0:element key="value">text</ns0:element>\n'
                '   <ns0:element>text</ns0:element>tail\n'
                '   <ns0:empty-element />\n'
                '</ns0:root>')

        ukijumuisha open(SIMPLE_XMLFILE) kama f:
            data = f.read()

        parser = ET.XMLParser()
        self.assertRegex(parser.version, r'^Expat ')
        parser.feed(data)
        self.serialize_check(parser.close(),
                '<root>\n'
                '   <element key="value">text</element>\n'
                '   <element>text</element>tail\n'
                '   <empty-element />\n'
                '</root>')

        target = ET.TreeBuilder()
        parser = ET.XMLParser(target=target)
        parser.feed(data)
        self.serialize_check(parser.close(),
                '<root>\n'
                '   <element key="value">text</element>\n'
                '   <element>text</element>tail\n'
                '   <empty-element />\n'
                '</root>')

    eleza test_parseliteral(self):
        element = ET.XML("<html><body>text</body></html>")
        self.assertEqual(ET.tostring(element, encoding='unicode'),
                '<html><body>text</body></html>')
        element = ET.kutokastring("<html><body>text</body></html>")
        self.assertEqual(ET.tostring(element, encoding='unicode'),
                '<html><body>text</body></html>')
        sequence = ["<html><body>", "text</bo", "dy></html>"]
        element = ET.kutokastringlist(sequence)
        self.assertEqual(ET.tostring(element),
                b'<html><body>text</body></html>')
        self.assertEqual(b"".join(ET.tostringlist(element)),
                b'<html><body>text</body></html>')
        self.assertEqual(ET.tostring(element, "ascii"),
                b"<?xml version='1.0' encoding='ascii'?>\n"
                b"<html><body>text</body></html>")
        _, ids = ET.XMLID("<html><body>text</body></html>")
        self.assertEqual(len(ids), 0)
        _, ids = ET.XMLID("<html><body id='body'>text</body></html>")
        self.assertEqual(len(ids), 1)
        self.assertEqual(ids["body"].tag, 'body')

    eleza test_iterparse(self):
        # Test iterparse interface.

        iterparse = ET.iterparse

        context = iterparse(SIMPLE_XMLFILE)
        action, elem = next(context)
        self.assertEqual((action, elem.tag), ('end', 'element'))
        self.assertEqual([(action, elem.tag) kila action, elem kwenye context], [
                ('end', 'element'),
                ('end', 'empty-element'),
                ('end', 'root'),
            ])
        self.assertEqual(context.root.tag, 'root')

        context = iterparse(SIMPLE_NS_XMLFILE)
        self.assertEqual([(action, elem.tag) kila action, elem kwenye context], [
                ('end', '{namespace}element'),
                ('end', '{namespace}element'),
                ('end', '{namespace}empty-element'),
                ('end', '{namespace}root'),
            ])

        events = ()
        context = iterparse(SIMPLE_XMLFILE, events)
        self.assertEqual([(action, elem.tag) kila action, elem kwenye context], [])

        events = ()
        context = iterparse(SIMPLE_XMLFILE, events=events)
        self.assertEqual([(action, elem.tag) kila action, elem kwenye context], [])

        events = ("start", "end")
        context = iterparse(SIMPLE_XMLFILE, events)
        self.assertEqual([(action, elem.tag) kila action, elem kwenye context], [
                ('start', 'root'),
                ('start', 'element'),
                ('end', 'element'),
                ('start', 'element'),
                ('end', 'element'),
                ('start', 'empty-element'),
                ('end', 'empty-element'),
                ('end', 'root'),
            ])

        events = ("start", "end", "start-ns", "end-ns")
        context = iterparse(SIMPLE_NS_XMLFILE, events)
        self.assertEqual([(action, elem.tag) ikiwa action kwenye ("start", "end")
                                             isipokua (action, elem)
                          kila action, elem kwenye context], [
                ('start-ns', ('', 'namespace')),
                ('start', '{namespace}root'),
                ('start', '{namespace}element'),
                ('end', '{namespace}element'),
                ('start', '{namespace}element'),
                ('end', '{namespace}element'),
                ('start', '{namespace}empty-element'),
                ('end', '{namespace}empty-element'),
                ('end', '{namespace}root'),
                ('end-ns', Tupu),
            ])

        events = ('start-ns', 'end-ns')
        context = iterparse(io.StringIO(r"<root xmlns=''/>"), events)
        res = [action kila action, elem kwenye context]
        self.assertEqual(res, ['start-ns', 'end-ns'])

        events = ("start", "end", "bogus")
        ukijumuisha open(SIMPLE_XMLFILE, "rb") kama f:
            ukijumuisha self.assertRaises(ValueError) kama cm:
                iterparse(f, events)
            self.assertUongo(f.closed)
        self.assertEqual(str(cm.exception), "unknown event 'bogus'")

        ukijumuisha support.check_no_resource_warning(self):
            ukijumuisha self.assertRaises(ValueError) kama cm:
                iterparse(SIMPLE_XMLFILE, events)
            self.assertEqual(str(cm.exception), "unknown event 'bogus'")
            toa cm

        source = io.BytesIO(
            b"<?xml version='1.0' encoding='iso-8859-1'?>\n"
            b"<body xmlns='http://&#233;ffbot.org/ns'\n"
            b"      xmlns:cl\xe9='http://effbot.org/ns'>text</body>\n")
        events = ("start-ns",)
        context = iterparse(source, events)
        self.assertEqual([(action, elem) kila action, elem kwenye context], [
                ('start-ns', ('', 'http://\xe9ffbot.org/ns')),
                ('start-ns', ('cl\xe9', 'http://effbot.org/ns')),
            ])

        source = io.StringIO("<document />junk")
        it = iterparse(source)
        action, elem = next(it)
        self.assertEqual((action, elem.tag), ('end', 'document'))
        ukijumuisha self.assertRaises(ET.ParseError) kama cm:
            next(it)
        self.assertEqual(str(cm.exception),
                'junk after document element: line 1, column 12')

        self.addCleanup(support.unlink, TESTFN)
        ukijumuisha open(TESTFN, "wb") kama f:
            f.write(b"<document />junk")
        it = iterparse(TESTFN)
        action, elem = next(it)
        self.assertEqual((action, elem.tag), ('end', 'document'))
        ukijumuisha support.check_no_resource_warning(self):
            ukijumuisha self.assertRaises(ET.ParseError) kama cm:
                next(it)
            self.assertEqual(str(cm.exception),
                    'junk after document element: line 1, column 12')
            toa cm, it

    eleza test_writefile(self):
        elem = ET.Element("tag")
        elem.text = "text"
        self.serialize_check(elem, '<tag>text</tag>')
        ET.SubElement(elem, "subtag").text = "subtext"
        self.serialize_check(elem, '<tag>text<subtag>subtext</subtag></tag>')

        # Test tag suppression
        elem.tag = Tupu
        self.serialize_check(elem, 'text<subtag>subtext</subtag>')
        elem.insert(0, ET.Comment("comment"))
        self.serialize_check(elem,
                'text<!--comment--><subtag>subtext</subtag>')     # assumes 1.3

        elem[0] = ET.PI("key", "value")
        self.serialize_check(elem, 'text<?key value?><subtag>subtext</subtag>')

    eleza test_custom_builder(self):
        # Test parser w. custom builder.

        ukijumuisha open(SIMPLE_XMLFILE) kama f:
            data = f.read()
        kundi Builder(list):
            eleza start(self, tag, attrib):
                self.append(("start", tag))
            eleza end(self, tag):
                self.append(("end", tag))
            eleza data(self, text):
                pita
        builder = Builder()
        parser = ET.XMLParser(target=builder)
        parser.feed(data)
        self.assertEqual(builder, [
                ('start', 'root'),
                ('start', 'element'),
                ('end', 'element'),
                ('start', 'element'),
                ('end', 'element'),
                ('start', 'empty-element'),
                ('end', 'empty-element'),
                ('end', 'root'),
            ])

        ukijumuisha open(SIMPLE_NS_XMLFILE) kama f:
            data = f.read()
        kundi Builder(list):
            eleza start(self, tag, attrib):
                self.append(("start", tag))
            eleza end(self, tag):
                self.append(("end", tag))
            eleza data(self, text):
                pita
            eleza pi(self, target, data):
                self.append(("pi", target, data))
            eleza comment(self, data):
                self.append(("comment", data))
            eleza start_ns(self, prefix, uri):
                self.append(("start-ns", prefix, uri))
            eleza end_ns(self, prefix):
                self.append(("end-ns", prefix))
        builder = Builder()
        parser = ET.XMLParser(target=builder)
        parser.feed(data)
        self.assertEqual(builder, [
                ('pi', 'pi', 'data'),
                ('comment', ' comment '),
                ('start-ns', '', 'namespace'),
                ('start', '{namespace}root'),
                ('start', '{namespace}element'),
                ('end', '{namespace}element'),
                ('start', '{namespace}element'),
                ('end', '{namespace}element'),
                ('start', '{namespace}empty-element'),
                ('end', '{namespace}empty-element'),
                ('end', '{namespace}root'),
                ('end-ns', ''),
            ])

    eleza test_custom_builder_only_end_ns(self):
        kundi Builder(list):
            eleza end_ns(self, prefix):
                self.append(("end-ns", prefix))

        builder = Builder()
        parser = ET.XMLParser(target=builder)
        parser.feed(textwrap.dedent("""\
            <?pi data?>
            <!-- comment -->
            <root xmlns='namespace' xmlns:p='pns' xmlns:a='ans'>
               <a:element key='value'>text</a:element>
               <p:element>text</p:element>tail
               <empty-element/>
            </root>
            """))
        self.assertEqual(builder, [
                ('end-ns', 'a'),
                ('end-ns', 'p'),
                ('end-ns', ''),
            ])

    # Element.getchildren() na ElementTree.getiterator() are deprecated.
    @checkwarnings(("This method will be removed kwenye future versions.  "
                    "Use .+ instead.",
                    DeprecationWarning))
    eleza test_getchildren(self):
        # Test Element.getchildren()

        ukijumuisha open(SIMPLE_XMLFILE, "rb") kama f:
            tree = ET.parse(f)
        self.assertEqual([summarize_list(elem.getchildren())
                          kila elem kwenye tree.getroot().iter()], [
                ['element', 'element', 'empty-element'],
                [],
                [],
                [],
            ])
        self.assertEqual([summarize_list(elem.getchildren())
                          kila elem kwenye tree.getiterator()], [
                ['element', 'element', 'empty-element'],
                [],
                [],
                [],
            ])

        elem = ET.XML(SAMPLE_XML)
        self.assertEqual(len(elem.getchildren()), 3)
        self.assertEqual(len(elem[2].getchildren()), 1)
        self.assertEqual(elem[:], elem.getchildren())
        child1 = elem[0]
        child2 = elem[2]
        toa elem[1:2]
        self.assertEqual(len(elem.getchildren()), 2)
        self.assertEqual(child1, elem[0])
        self.assertEqual(child2, elem[1])
        elem[0:2] = [child2, child1]
        self.assertEqual(child2, elem[0])
        self.assertEqual(child1, elem[1])
        self.assertNotEqual(child1, elem[0])
        elem.clear()
        self.assertEqual(elem.getchildren(), [])

    eleza test_writestring(self):
        elem = ET.XML("<html><body>text</body></html>")
        self.assertEqual(ET.tostring(elem), b'<html><body>text</body></html>')
        elem = ET.kutokastring("<html><body>text</body></html>")
        self.assertEqual(ET.tostring(elem), b'<html><body>text</body></html>')

    eleza test_tostring_default_namespace(self):
        elem = ET.XML('<body xmlns="http://effbot.org/ns"><tag/></body>')
        self.assertEqual(
            ET.tostring(elem, encoding='unicode'),
            '<ns0:body xmlns:ns0="http://effbot.org/ns"><ns0:tag /></ns0:body>'
        )
        self.assertEqual(
            ET.tostring(elem, encoding='unicode', default_namespace='http://effbot.org/ns'),
            '<body xmlns="http://effbot.org/ns"><tag /></body>'
        )

    eleza test_tostring_default_namespace_different_namespace(self):
        elem = ET.XML('<body xmlns="http://effbot.org/ns"><tag/></body>')
        self.assertEqual(
            ET.tostring(elem, encoding='unicode', default_namespace='foobar'),
            '<ns1:body xmlns="foobar" xmlns:ns1="http://effbot.org/ns"><ns1:tag /></ns1:body>'
        )

    eleza test_tostring_default_namespace_original_no_namespace(self):
        elem = ET.XML('<body><tag/></body>')
        EXPECTED_MSG = '^cannot use non-qualified names ukijumuisha default_namespace option$'
        ukijumuisha self.assertRaisesRegex(ValueError, EXPECTED_MSG):
            ET.tostring(elem, encoding='unicode', default_namespace='foobar')

    eleza test_tostring_no_xml_declaration(self):
        elem = ET.XML('<body><tag/></body>')
        self.assertEqual(
            ET.tostring(elem, encoding='unicode'),
            '<body><tag /></body>'
        )

    eleza test_tostring_xml_declaration(self):
        elem = ET.XML('<body><tag/></body>')
        self.assertEqual(
            ET.tostring(elem, encoding='utf8', xml_declaration=Kweli),
            b"<?xml version='1.0' encoding='utf8'?>\n<body><tag /></body>"
        )

    eleza test_tostring_xml_declaration_unicode_encoding(self):
        elem = ET.XML('<body><tag/></body>')
        preferredencoding = locale.getpreferredencoding()
        self.assertEqual(
            f"<?xml version='1.0' encoding='{preferredencoding}'?>\n<body><tag /></body>",
            ET.tostring(elem, encoding='unicode', xml_declaration=Kweli)
        )

    eleza test_tostring_xml_declaration_cases(self):
        elem = ET.XML('<body><tag>ø</tag></body>')
        preferredencoding = locale.getpreferredencoding()
        TESTCASES = [
        #   (expected_retval,                  encoding, xml_declaration)
            # ... xml_declaration = Tupu
            (b'<body><tag>&#248;</tag></body>', Tupu, Tupu),
            (b'<body><tag>\xc3\xb8</tag></body>', 'UTF-8', Tupu),
            (b'<body><tag>&#248;</tag></body>', 'US-ASCII', Tupu),
            (b"<?xml version='1.0' encoding='ISO-8859-1'?>\n"
             b"<body><tag>\xf8</tag></body>", 'ISO-8859-1', Tupu),
            ('<body><tag>ø</tag></body>', 'unicode', Tupu),

            # ... xml_declaration = Uongo
            (b"<body><tag>&#248;</tag></body>", Tupu, Uongo),
            (b"<body><tag>\xc3\xb8</tag></body>", 'UTF-8', Uongo),
            (b"<body><tag>&#248;</tag></body>", 'US-ASCII', Uongo),
            (b"<body><tag>\xf8</tag></body>", 'ISO-8859-1', Uongo),
            ("<body><tag>ø</tag></body>", 'unicode', Uongo),

            # ... xml_declaration = Kweli
            (b"<?xml version='1.0' encoding='us-ascii'?>\n"
             b"<body><tag>&#248;</tag></body>", Tupu, Kweli),
            (b"<?xml version='1.0' encoding='UTF-8'?>\n"
             b"<body><tag>\xc3\xb8</tag></body>", 'UTF-8', Kweli),
            (b"<?xml version='1.0' encoding='US-ASCII'?>\n"
             b"<body><tag>&#248;</tag></body>", 'US-ASCII', Kweli),
            (b"<?xml version='1.0' encoding='ISO-8859-1'?>\n"
             b"<body><tag>\xf8</tag></body>", 'ISO-8859-1', Kweli),
            (f"<?xml version='1.0' encoding='{preferredencoding}'?>\n"
             "<body><tag>ø</tag></body>", 'unicode', Kweli),

        ]
        kila expected_retval, encoding, xml_declaration kwenye TESTCASES:
            ukijumuisha self.subTest(f'encoding={encoding} '
                              f'xml_declaration={xml_declaration}'):
                self.assertEqual(
                    ET.tostring(
                        elem,
                        encoding=encoding,
                        xml_declaration=xml_declaration
                    ),
                    expected_retval
                )

    eleza test_tostringlist_default_namespace(self):
        elem = ET.XML('<body xmlns="http://effbot.org/ns"><tag/></body>')
        self.assertEqual(
            ''.join(ET.tostringlist(elem, encoding='unicode')),
            '<ns0:body xmlns:ns0="http://effbot.org/ns"><ns0:tag /></ns0:body>'
        )
        self.assertEqual(
            ''.join(ET.tostringlist(elem, encoding='unicode', default_namespace='http://effbot.org/ns')),
            '<body xmlns="http://effbot.org/ns"><tag /></body>'
        )

    eleza test_tostringlist_xml_declaration(self):
        elem = ET.XML('<body><tag/></body>')
        self.assertEqual(
            ''.join(ET.tostringlist(elem, encoding='unicode')),
            '<body><tag /></body>'
        )
        self.assertEqual(
            b''.join(ET.tostringlist(elem, xml_declaration=Kweli)),
            b"<?xml version='1.0' encoding='us-ascii'?>\n<body><tag /></body>"
        )

        preferredencoding = locale.getpreferredencoding()
        stringlist = ET.tostringlist(elem, encoding='unicode', xml_declaration=Kweli)
        self.assertEqual(
            ''.join(stringlist),
            f"<?xml version='1.0' encoding='{preferredencoding}'?>\n<body><tag /></body>"
        )
        self.assertRegex(stringlist[0], r"^<\?xml version='1.0' encoding='.+'?>")
        self.assertEqual(['<body', '>', '<tag', ' />', '</body>'], stringlist[1:])

    eleza test_encoding(self):
        eleza check(encoding, body=''):
            xml = ("<?xml version='1.0' encoding='%s'?><xml>%s</xml>" %
                   (encoding, body))
            self.assertEqual(ET.XML(xml.encode(encoding)).text, body)
            self.assertEqual(ET.XML(xml).text, body)
        check("ascii", 'a')
        check("us-ascii", 'a')
        check("iso-8859-1", '\xbd')
        check("iso-8859-15", '\u20ac')
        check("cp437", '\u221a')
        check("mac-roman", '\u02da')

        eleza xml(encoding):
            rudisha "<?xml version='1.0' encoding='%s'?><xml />" % encoding
        eleza bxml(encoding):
            rudisha xml(encoding).encode(encoding)
        supported_encodings = [
            'ascii', 'utf-8', 'utf-8-sig', 'utf-16', 'utf-16be', 'utf-16le',
            'iso8859-1', 'iso8859-2', 'iso8859-3', 'iso8859-4', 'iso8859-5',
            'iso8859-6', 'iso8859-7', 'iso8859-8', 'iso8859-9', 'iso8859-10',
            'iso8859-13', 'iso8859-14', 'iso8859-15', 'iso8859-16',
            'cp437', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852',
            'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862',
            'cp863', 'cp865', 'cp866', 'cp869', 'cp874', 'cp1006', 'cp1125',
            'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255',
            'cp1256', 'cp1257', 'cp1258',
            'mac-cyrillic', 'mac-greek', 'mac-iceland', 'mac-latin2',
            'mac-roman', 'mac-turkish',
            'iso2022-jp', 'iso2022-jp-1', 'iso2022-jp-2', 'iso2022-jp-2004',
            'iso2022-jp-3', 'iso2022-jp-ext',
            'koi8-r', 'koi8-t', 'koi8-u', 'kz1048',
            'hz', 'ptcp154',
        ]
        kila encoding kwenye supported_encodings:
            self.assertEqual(ET.tostring(ET.XML(bxml(encoding))), b'<xml />')

        unsupported_ascii_compatible_encodings = [
            'big5', 'big5hkscs',
            'cp932', 'cp949', 'cp950',
            'euc-jp', 'euc-jis-2004', 'euc-jisx0213', 'euc-kr',
            'gb2312', 'gbk', 'gb18030',
            'iso2022-kr', 'johab',
            'shift-jis', 'shift-jis-2004', 'shift-jisx0213',
            'utf-7',
        ]
        kila encoding kwenye unsupported_ascii_compatible_encodings:
            self.assertRaises(ValueError, ET.XML, bxml(encoding))

        unsupported_ascii_incompatible_encodings = [
            'cp037', 'cp424', 'cp500', 'cp864', 'cp875', 'cp1026', 'cp1140',
            'utf_32', 'utf_32_be', 'utf_32_le',
        ]
        kila encoding kwenye unsupported_ascii_incompatible_encodings:
            self.assertRaises(ET.ParseError, ET.XML, bxml(encoding))

        self.assertRaises(ValueError, ET.XML, xml('undefined').encode('ascii'))
        self.assertRaises(LookupError, ET.XML, xml('xxx').encode('ascii'))

    eleza test_methods(self):
        # Test serialization methods.

        e = ET.XML("<html><link/><script>1 &lt; 2</script></html>")
        e.tail = "\n"
        self.assertEqual(serialize(e),
                '<html><link /><script>1 &lt; 2</script></html>\n')
        self.assertEqual(serialize(e, method=Tupu),
                '<html><link /><script>1 &lt; 2</script></html>\n')
        self.assertEqual(serialize(e, method="xml"),
                '<html><link /><script>1 &lt; 2</script></html>\n')
        self.assertEqual(serialize(e, method="html"),
                '<html><link><script>1 < 2</script></html>\n')
        self.assertEqual(serialize(e, method="text"), '1 < 2\n')

    eleza test_issue18347(self):
        e = ET.XML('<html><CamelCase>text</CamelCase></html>')
        self.assertEqual(serialize(e),
                '<html><CamelCase>text</CamelCase></html>')
        self.assertEqual(serialize(e, method="html"),
                '<html><CamelCase>text</CamelCase></html>')

    eleza test_entity(self):
        # Test entity handling.

        # 1) good entities

        e = ET.XML("<document title='&#x8230;'>test</document>")
        self.assertEqual(serialize(e, encoding="us-ascii"),
                b'<document title="&#33328;">test</document>')
        self.serialize_check(e, '<document title="\u8230">test</document>')

        # 2) bad entities

        ukijumuisha self.assertRaises(ET.ParseError) kama cm:
            ET.XML("<document>&entity;</document>")
        self.assertEqual(str(cm.exception),
                'undefined entity: line 1, column 10')

        ukijumuisha self.assertRaises(ET.ParseError) kama cm:
            ET.XML(ENTITY_XML)
        self.assertEqual(str(cm.exception),
                'undefined entity &entity;: line 5, column 10')

        # 3) custom entity

        parser = ET.XMLParser()
        parser.entity["entity"] = "text"
        parser.feed(ENTITY_XML)
        root = parser.close()
        self.serialize_check(root, '<document>text</document>')

        # 4) external (SYSTEM) entity

        ukijumuisha self.assertRaises(ET.ParseError) kama cm:
            ET.XML(EXTERNAL_ENTITY_XML)
        self.assertEqual(str(cm.exception),
                'undefined entity &entity;: line 4, column 10')

    eleza test_namespace(self):
        # Test namespace issues.

        # 1) xml namespace

        elem = ET.XML("<tag xml:lang='en' />")
        self.serialize_check(elem, '<tag xml:lang="en" />') # 1.1

        # 2) other "well-known" namespaces

        elem = ET.XML("<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' />")
        self.serialize_check(elem,
            '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" />') # 2.1

        elem = ET.XML("<html:html xmlns:html='http://www.w3.org/1999/xhtml' />")
        self.serialize_check(elem,
            '<html:html xmlns:html="http://www.w3.org/1999/xhtml" />') # 2.2

        elem = ET.XML("<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope' />")
        self.serialize_check(elem,
            '<ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope" />') # 2.3

        # 3) unknown namespaces
        elem = ET.XML(SAMPLE_XML_NS)
        self.serialize_check(elem,
            '<ns0:body xmlns:ns0="http://effbot.org/ns">\n'
            '  <ns0:tag>text</ns0:tag>\n'
            '  <ns0:tag />\n'
            '  <ns0:section>\n'
            '    <ns0:tag>subtext</ns0:tag>\n'
            '  </ns0:section>\n'
            '</ns0:body>')

    eleza test_qname(self):
        # Test QName handling.

        # 1) decorated tags

        elem = ET.Element("{uri}tag")
        self.serialize_check(elem, '<ns0:tag xmlns:ns0="uri" />') # 1.1
        elem = ET.Element(ET.QName("{uri}tag"))
        self.serialize_check(elem, '<ns0:tag xmlns:ns0="uri" />') # 1.2
        elem = ET.Element(ET.QName("uri", "tag"))
        self.serialize_check(elem, '<ns0:tag xmlns:ns0="uri" />') # 1.3
        elem = ET.Element(ET.QName("uri", "tag"))
        subelem = ET.SubElement(elem, ET.QName("uri", "tag1"))
        subelem = ET.SubElement(elem, ET.QName("uri", "tag2"))
        self.serialize_check(elem,
            '<ns0:tag xmlns:ns0="uri"><ns0:tag1 /><ns0:tag2 /></ns0:tag>') # 1.4

        # 2) decorated attributes

        elem.clear()
        elem.attrib["{uri}key"] = "value"
        self.serialize_check(elem,
            '<ns0:tag xmlns:ns0="uri" ns0:key="value" />') # 2.1

        elem.clear()
        elem.attrib[ET.QName("{uri}key")] = "value"
        self.serialize_check(elem,
            '<ns0:tag xmlns:ns0="uri" ns0:key="value" />') # 2.2

        # 3) decorated values are sio converted by default, but the
        # QName wrapper can be used kila values

        elem.clear()
        elem.attrib["{uri}key"] = "{uri}value"
        self.serialize_check(elem,
            '<ns0:tag xmlns:ns0="uri" ns0:key="{uri}value" />') # 3.1

        elem.clear()
        elem.attrib["{uri}key"] = ET.QName("{uri}value")
        self.serialize_check(elem,
            '<ns0:tag xmlns:ns0="uri" ns0:key="ns0:value" />') # 3.2

        elem.clear()
        subelem = ET.Element("tag")
        subelem.attrib["{uri1}key"] = ET.QName("{uri2}value")
        elem.append(subelem)
        elem.append(subelem)
        self.serialize_check(elem,
            '<ns0:tag xmlns:ns0="uri" xmlns:ns1="uri1" xmlns:ns2="uri2">'
            '<tag ns1:key="ns2:value" />'
            '<tag ns1:key="ns2:value" />'
            '</ns0:tag>') # 3.3

        # 4) Direct QName tests

        self.assertEqual(str(ET.QName('ns', 'tag')), '{ns}tag')
        self.assertEqual(str(ET.QName('{ns}tag')), '{ns}tag')
        q1 = ET.QName('ns', 'tag')
        q2 = ET.QName('ns', 'tag')
        self.assertEqual(q1, q2)
        q2 = ET.QName('ns', 'other-tag')
        self.assertNotEqual(q1, q2)
        self.assertNotEqual(q1, 'ns:tag')
        self.assertEqual(q1, '{ns}tag')

    eleza test_doctype_public(self):
        # Test PUBLIC doctype.

        elem = ET.XML('<!DOCTYPE html PUBLIC'
                ' "-//W3C//DTD XHTML 1.0 Transitional//EN"'
                ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
                '<html>text</html>')

    eleza test_xpath_tokenizer(self):
        # Test the XPath tokenizer.
        kutoka xml.etree agiza ElementPath
        eleza check(p, expected, namespaces=Tupu):
            self.assertEqual([op ama tag
                              kila op, tag kwenye ElementPath.xpath_tokenizer(p, namespaces)],
                             expected)

        # tests kutoka the xml specification
        check("*", ['*'])
        check("text()", ['text', '()'])
        check("@name", ['@', 'name'])
        check("@*", ['@', '*'])
        check("para[1]", ['para', '[', '1', ']'])
        check("para[last()]", ['para', '[', 'last', '()', ']'])
        check("*/para", ['*', '/', 'para'])
        check("/doc/chapter[5]/section[2]",
              ['/', 'doc', '/', 'chapter', '[', '5', ']',
               '/', 'section', '[', '2', ']'])
        check("chapter//para", ['chapter', '//', 'para'])
        check("//para", ['//', 'para'])
        check("//olist/item", ['//', 'olist', '/', 'item'])
        check(".", ['.'])
        check(".//para", ['.', '//', 'para'])
        check("..", ['..'])
        check("../@lang", ['..', '/', '@', 'lang'])
        check("chapter[title]", ['chapter', '[', 'title', ']'])
        check("employee[@secretary na @assistant]", ['employee',
              '[', '@', 'secretary', '', 'and', '', '@', 'assistant', ']'])

        # additional tests
        check("@{ns}attr", ['@', '{ns}attr'])
        check("{http://spam}egg", ['{http://spam}egg'])
        check("./spam.egg", ['.', '/', 'spam.egg'])
        check(".//{http://spam}egg", ['.', '//', '{http://spam}egg'])

        # wildcard tags
        check("{ns}*", ['{ns}*'])
        check("{}*", ['{}*'])
        check("{*}tag", ['{*}tag'])
        check("{*}*", ['{*}*'])
        check(".//{*}tag", ['.', '//', '{*}tag'])

        # namespace prefix resolution
        check("./xsd:type", ['.', '/', '{http://www.w3.org/2001/XMLSchema}type'],
              {'xsd': 'http://www.w3.org/2001/XMLSchema'})
        check("type", ['{http://www.w3.org/2001/XMLSchema}type'],
              {'': 'http://www.w3.org/2001/XMLSchema'})
        check("@xsd:type", ['@', '{http://www.w3.org/2001/XMLSchema}type'],
              {'xsd': 'http://www.w3.org/2001/XMLSchema'})
        check("@type", ['@', 'type'],
              {'': 'http://www.w3.org/2001/XMLSchema'})
        check("@{*}type", ['@', '{*}type'],
              {'': 'http://www.w3.org/2001/XMLSchema'})
        check("@{ns}attr", ['@', '{ns}attr'],
              {'': 'http://www.w3.org/2001/XMLSchema',
               'ns': 'http://www.w3.org/2001/XMLSchema'})

    eleza test_processinginstruction(self):
        # Test ProcessingInstruction directly

        self.assertEqual(ET.tostring(ET.ProcessingInstruction('test', 'instruction')),
                b'<?test instruction?>')
        self.assertEqual(ET.tostring(ET.PI('test', 'instruction')),
                b'<?test instruction?>')

        # Issue #2746

        self.assertEqual(ET.tostring(ET.PI('test', '<testing&>')),
                b'<?test <testing&>?>')
        self.assertEqual(ET.tostring(ET.PI('test', '<testing&>\xe3'), 'latin-1'),
                b"<?xml version='1.0' encoding='latin-1'?>\n"
                b"<?test <testing&>\xe3?>")

    eleza test_html_empty_elems_serialization(self):
        # issue 15970
        # kutoka http://www.w3.org/TR/html401/index/elements.html
        kila element kwenye ['AREA', 'BASE', 'BASEFONT', 'BR', 'COL', 'FRAME', 'HR',
                        'IMG', 'INPUT', 'ISINDEX', 'LINK', 'META', 'PARAM']:
            kila elem kwenye [element, element.lower()]:
                expected = '<%s>' % elem
                serialized = serialize(ET.XML('<%s />' % elem), method='html')
                self.assertEqual(serialized, expected)
                serialized = serialize(ET.XML('<%s></%s>' % (elem,elem)),
                                       method='html')
                self.assertEqual(serialized, expected)

    eleza test_dump_attribute_order(self):
        # See BPO 34160
        e = ET.Element('cirriculum', status='public', company='example')
        ukijumuisha support.captured_stdout() kama stdout:
            ET.dump(e)
        self.assertEqual(stdout.getvalue(),
                         '<cirriculum status="public" company="example" />\n')

    eleza test_tree_write_attribute_order(self):
        # See BPO 34160
        root = ET.Element('cirriculum', status='public', company='example')
        self.assertEqual(serialize(root),
                         '<cirriculum status="public" company="example" />')
        self.assertEqual(serialize(root, method='html'),
                '<cirriculum status="public" company="example"></cirriculum>')


kundi XMLPullParserTest(unittest.TestCase):

    eleza _feed(self, parser, data, chunk_size=Tupu):
        ikiwa chunk_size ni Tupu:
            parser.feed(data)
        isipokua:
            kila i kwenye range(0, len(data), chunk_size):
                parser.feed(data[i:i+chunk_size])

    eleza assert_events(self, parser, expected, max_events=Tupu):
        self.assertEqual(
            [(event, (elem.tag, elem.text))
             kila event, elem kwenye islice(parser.read_events(), max_events)],
            expected)

    eleza assert_event_tuples(self, parser, expected, max_events=Tupu):
        self.assertEqual(
            list(islice(parser.read_events(), max_events)),
            expected)

    eleza assert_event_tags(self, parser, expected, max_events=Tupu):
        events = islice(parser.read_events(), max_events)
        self.assertEqual([(action, elem.tag) kila action, elem kwenye events],
                         expected)

    eleza test_simple_xml(self):
        kila chunk_size kwenye (Tupu, 1, 5):
            ukijumuisha self.subTest(chunk_size=chunk_size):
                parser = ET.XMLPullParser()
                self.assert_event_tags(parser, [])
                self._feed(parser, "<!-- comment -->\n", chunk_size)
                self.assert_event_tags(parser, [])
                self._feed(parser,
                           "<root>\n  <element key='value'>text</element",
                           chunk_size)
                self.assert_event_tags(parser, [])
                self._feed(parser, ">\n", chunk_size)
                self.assert_event_tags(parser, [('end', 'element')])
                self._feed(parser, "<element>text</element>tail\n", chunk_size)
                self._feed(parser, "<empty-element/>\n", chunk_size)
                self.assert_event_tags(parser, [
                    ('end', 'element'),
                    ('end', 'empty-element'),
                    ])
                self._feed(parser, "</root>\n", chunk_size)
                self.assert_event_tags(parser, [('end', 'root')])
                self.assertIsTupu(parser.close())

    eleza test_feed_while_iterating(self):
        parser = ET.XMLPullParser()
        it = parser.read_events()
        self._feed(parser, "<root>\n  <element key='value'>text</element>\n")
        action, elem = next(it)
        self.assertEqual((action, elem.tag), ('end', 'element'))
        self._feed(parser, "</root>\n")
        action, elem = next(it)
        self.assertEqual((action, elem.tag), ('end', 'root'))
        ukijumuisha self.assertRaises(StopIteration):
            next(it)

    eleza test_simple_xml_with_ns(self):
        parser = ET.XMLPullParser()
        self.assert_event_tags(parser, [])
        self._feed(parser, "<!-- comment -->\n")
        self.assert_event_tags(parser, [])
        self._feed(parser, "<root xmlns='namespace'>\n")
        self.assert_event_tags(parser, [])
        self._feed(parser, "<element key='value'>text</element")
        self.assert_event_tags(parser, [])
        self._feed(parser, ">\n")
        self.assert_event_tags(parser, [('end', '{namespace}element')])
        self._feed(parser, "<element>text</element>tail\n")
        self._feed(parser, "<empty-element/>\n")
        self.assert_event_tags(parser, [
            ('end', '{namespace}element'),
            ('end', '{namespace}empty-element'),
            ])
        self._feed(parser, "</root>\n")
        self.assert_event_tags(parser, [('end', '{namespace}root')])
        self.assertIsTupu(parser.close())

    eleza test_ns_events(self):
        parser = ET.XMLPullParser(events=('start-ns', 'end-ns'))
        self._feed(parser, "<!-- comment -->\n")
        self._feed(parser, "<root xmlns='namespace'>\n")
        self.assertEqual(
            list(parser.read_events()),
            [('start-ns', ('', 'namespace'))])
        self._feed(parser, "<element key='value'>text</element")
        self._feed(parser, ">\n")
        self._feed(parser, "<element>text</element>tail\n")
        self._feed(parser, "<empty-element/>\n")
        self._feed(parser, "</root>\n")
        self.assertEqual(list(parser.read_events()), [('end-ns', Tupu)])
        self.assertIsTupu(parser.close())

    eleza test_ns_events_start(self):
        parser = ET.XMLPullParser(events=('start-ns', 'start', 'end'))
        self._feed(parser, "<tag xmlns='abc' xmlns:p='xyz'>\n")
        self.assert_event_tuples(parser, [
            ('start-ns', ('', 'abc')),
            ('start-ns', ('p', 'xyz')),
        ], max_events=2)
        self.assert_event_tags(parser, [
            ('start', '{abc}tag'),
        ], max_events=1)

        self._feed(parser, "<child />\n")
        self.assert_event_tags(parser, [
            ('start', '{abc}child'),
            ('end', '{abc}child'),
        ])

        self._feed(parser, "</tag>\n")
        parser.close()
        self.assert_event_tags(parser, [
            ('end', '{abc}tag'),
        ])

    eleza test_ns_events_start_end(self):
        parser = ET.XMLPullParser(events=('start-ns', 'start', 'end', 'end-ns'))
        self._feed(parser, "<tag xmlns='abc' xmlns:p='xyz'>\n")
        self.assert_event_tuples(parser, [
            ('start-ns', ('', 'abc')),
            ('start-ns', ('p', 'xyz')),
        ], max_events=2)
        self.assert_event_tags(parser, [
            ('start', '{abc}tag'),
        ], max_events=1)

        self._feed(parser, "<child />\n")
        self.assert_event_tags(parser, [
            ('start', '{abc}child'),
            ('end', '{abc}child'),
        ])

        self._feed(parser, "</tag>\n")
        parser.close()
        self.assert_event_tags(parser, [
            ('end', '{abc}tag'),
        ], max_events=1)
        self.assert_event_tuples(parser, [
            ('end-ns', Tupu),
            ('end-ns', Tupu),
        ])

    eleza test_events(self):
        parser = ET.XMLPullParser(events=())
        self._feed(parser, "<root/>\n")
        self.assert_event_tags(parser, [])

        parser = ET.XMLPullParser(events=('start', 'end'))
        self._feed(parser, "<!-- text here -->\n")
        self.assert_events(parser, [])

        parser = ET.XMLPullParser(events=('start', 'end'))
        self._feed(parser, "<root>\n")
        self.assert_event_tags(parser, [('start', 'root')])
        self._feed(parser, "<element key='value'>text</element")
        self.assert_event_tags(parser, [('start', 'element')])
        self._feed(parser, ">\n")
        self.assert_event_tags(parser, [('end', 'element')])
        self._feed(parser,
                   "<element xmlns='foo'>text<empty-element/></element>tail\n")
        self.assert_event_tags(parser, [
            ('start', '{foo}element'),
            ('start', '{foo}empty-element'),
            ('end', '{foo}empty-element'),
            ('end', '{foo}element'),
            ])
        self._feed(parser, "</root>")
        self.assertIsTupu(parser.close())
        self.assert_event_tags(parser, [('end', 'root')])

        parser = ET.XMLPullParser(events=('start',))
        self._feed(parser, "<!-- comment -->\n")
        self.assert_event_tags(parser, [])
        self._feed(parser, "<root>\n")
        self.assert_event_tags(parser, [('start', 'root')])
        self._feed(parser, "<element key='value'>text</element")
        self.assert_event_tags(parser, [('start', 'element')])
        self._feed(parser, ">\n")
        self.assert_event_tags(parser, [])
        self._feed(parser,
                   "<element xmlns='foo'>text<empty-element/></element>tail\n")
        self.assert_event_tags(parser, [
            ('start', '{foo}element'),
            ('start', '{foo}empty-element'),
            ])
        self._feed(parser, "</root>")
        self.assertIsTupu(parser.close())

    eleza test_events_comment(self):
        parser = ET.XMLPullParser(events=('start', 'comment', 'end'))
        self._feed(parser, "<!-- text here -->\n")
        self.assert_events(parser, [('comment', (ET.Comment, ' text here '))])
        self._feed(parser, "<!-- more text here -->\n")
        self.assert_events(parser, [('comment', (ET.Comment, ' more text here '))])
        self._feed(parser, "<root-tag>text")
        self.assert_event_tags(parser, [('start', 'root-tag')])
        self._feed(parser, "<!-- inner comment-->\n")
        self.assert_events(parser, [('comment', (ET.Comment, ' inner comment'))])
        self._feed(parser, "</root-tag>\n")
        self.assert_event_tags(parser, [('end', 'root-tag')])
        self._feed(parser, "<!-- outer comment -->\n")
        self.assert_events(parser, [('comment', (ET.Comment, ' outer comment '))])

        parser = ET.XMLPullParser(events=('comment',))
        self._feed(parser, "<!-- text here -->\n")
        self.assert_events(parser, [('comment', (ET.Comment, ' text here '))])

    eleza test_events_pi(self):
        parser = ET.XMLPullParser(events=('start', 'pi', 'end'))
        self._feed(parser, "<?pitarget?>\n")
        self.assert_events(parser, [('pi', (ET.PI, 'pitarget'))])
        parser = ET.XMLPullParser(events=('pi',))
        self._feed(parser, "<?pitarget some text ?>\n")
        self.assert_events(parser, [('pi', (ET.PI, 'pitarget some text '))])

    eleza test_events_sequence(self):
        # Test that events can be some sequence that's sio just a tuple ama list
        eventset = {'end', 'start'}
        parser = ET.XMLPullParser(events=eventset)
        self._feed(parser, "<foo>bar</foo>")
        self.assert_event_tags(parser, [('start', 'foo'), ('end', 'foo')])

        kundi DummyIter:
            eleza __init__(self):
                self.events = iter(['start', 'end', 'start-ns'])
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                rudisha next(self.events)

        parser = ET.XMLPullParser(events=DummyIter())
        self._feed(parser, "<foo>bar</foo>")
        self.assert_event_tags(parser, [('start', 'foo'), ('end', 'foo')])

    eleza test_unknown_event(self):
        ukijumuisha self.assertRaises(ValueError):
            ET.XMLPullParser(events=('start', 'end', 'bogus'))


#
# xinclude tests (samples kutoka appendix C of the xinclude specification)

XINCLUDE = {}

XINCLUDE["C1.xml"] = """\
<?xml version='1.0'?>
<document xmlns:xi="http://www.w3.org/2001/XInclude">
  <p>120 Mz ni adequate kila an average home user.</p>
  <xi:include href="disclaimer.xml"/>
</document>
"""

XINCLUDE["disclaimer.xml"] = """\
<?xml version='1.0'?>
<disclaimer>
  <p>The opinions represented herein represent those of the individual
  na should sio be interpreted kama official policy endorsed by this
  organization.</p>
</disclaimer>
"""

XINCLUDE["C2.xml"] = """\
<?xml version='1.0'?>
<document xmlns:xi="http://www.w3.org/2001/XInclude">
  <p>This document has been accessed
  <xi:include href="count.txt" parse="text"/> times.</p>
</document>
"""

XINCLUDE["count.txt"] = "324387"

XINCLUDE["C2b.xml"] = """\
<?xml version='1.0'?>
<document xmlns:xi="http://www.w3.org/2001/XInclude">
  <p>This document has been <em>accessed</em>
  <xi:include href="count.txt" parse="text"/> times.</p>
</document>
"""

XINCLUDE["C3.xml"] = """\
<?xml version='1.0'?>
<document xmlns:xi="http://www.w3.org/2001/XInclude">
  <p>The following ni the source of the "data.xml" resource:</p>
  <example><xi:include href="data.xml" parse="text"/></example>
</document>
"""

XINCLUDE["data.xml"] = """\
<?xml version='1.0'?>
<data>
  <item><![CDATA[Brooks & Shields]]></item>
</data>
"""

XINCLUDE["C5.xml"] = """\
<?xml version='1.0'?>
<div xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="example.txt" parse="text">
    <xi:fallback>
      <xi:include href="fallback-example.txt" parse="text">
        <xi:fallback><a href="mailto:bob@example.org">Report error</a></xi:fallback>
      </xi:include>
    </xi:fallback>
  </xi:include>
</div>
"""

XINCLUDE["default.xml"] = """\
<?xml version='1.0'?>
<document xmlns:xi="http://www.w3.org/2001/XInclude">
  <p>Example.</p>
  <xi:include href="{}"/>
</document>
""".format(html.escape(SIMPLE_XMLFILE, Kweli))

#
# badly formatted xi:include tags

XINCLUDE_BAD = {}

XINCLUDE_BAD["B1.xml"] = """\
<?xml version='1.0'?>
<document xmlns:xi="http://www.w3.org/2001/XInclude">
  <p>120 Mz ni adequate kila an average home user.</p>
  <xi:include href="disclaimer.xml" parse="BAD_TYPE"/>
</document>
"""

XINCLUDE_BAD["B2.xml"] = """\
<?xml version='1.0'?>
<div xmlns:xi="http://www.w3.org/2001/XInclude">
    <xi:fallback></xi:fallback>
</div>
"""

kundi XIncludeTest(unittest.TestCase):

    eleza xinclude_loader(self, href, parse="xml", encoding=Tupu):
        jaribu:
            data = XINCLUDE[href]
        tatizo KeyError:
            ashiria OSError("resource sio found")
        ikiwa parse == "xml":
            data = ET.XML(data)
        rudisha data

    eleza none_loader(self, href, parser, encoding=Tupu):
        rudisha Tupu

    eleza _my_loader(self, href, parse):
        # Used to avoid a test-dependency problem where the default loader
        # of ElementInclude uses the pyET parser kila cET tests.
        ikiwa parse == 'xml':
            ukijumuisha open(href, 'rb') kama f:
                rudisha ET.parse(f).getroot()
        isipokua:
            rudisha Tupu

    eleza test_xinclude_default(self):
        kutoka xml.etree agiza ElementInclude
        doc = self.xinclude_loader('default.xml')
        ElementInclude.include(doc, self._my_loader)
        self.assertEqual(serialize(doc),
            '<document>\n'
            '  <p>Example.</p>\n'
            '  <root>\n'
            '   <element key="value">text</element>\n'
            '   <element>text</element>tail\n'
            '   <empty-element />\n'
            '</root>\n'
            '</document>')

    eleza test_xinclude(self):
        kutoka xml.etree agiza ElementInclude

        # Basic inclusion example (XInclude C.1)
        document = self.xinclude_loader("C1.xml")
        ElementInclude.include(document, self.xinclude_loader)
        self.assertEqual(serialize(document),
            '<document>\n'
            '  <p>120 Mz ni adequate kila an average home user.</p>\n'
            '  <disclaimer>\n'
            '  <p>The opinions represented herein represent those of the individual\n'
            '  na should sio be interpreted kama official policy endorsed by this\n'
            '  organization.</p>\n'
            '</disclaimer>\n'
            '</document>') # C1

        # Textual inclusion example (XInclude C.2)
        document = self.xinclude_loader("C2.xml")
        ElementInclude.include(document, self.xinclude_loader)
        self.assertEqual(serialize(document),
            '<document>\n'
            '  <p>This document has been accessed\n'
            '  324387 times.</p>\n'
            '</document>') # C2

        # Textual inclusion after sibling element (based on modified XInclude C.2)
        document = self.xinclude_loader("C2b.xml")
        ElementInclude.include(document, self.xinclude_loader)
        self.assertEqual(serialize(document),
            '<document>\n'
            '  <p>This document has been <em>accessed</em>\n'
            '  324387 times.</p>\n'
            '</document>') # C2b

        # Textual inclusion of XML example (XInclude C.3)
        document = self.xinclude_loader("C3.xml")
        ElementInclude.include(document, self.xinclude_loader)
        self.assertEqual(serialize(document),
            '<document>\n'
            '  <p>The following ni the source of the "data.xml" resource:</p>\n'
            "  <example>&lt;?xml version='1.0'?&gt;\n"
            '&lt;data&gt;\n'
            '  &lt;item&gt;&lt;![CDATA[Brooks &amp; Shields]]&gt;&lt;/item&gt;\n'
            '&lt;/data&gt;\n'
            '</example>\n'
            '</document>') # C3

        # Fallback example (XInclude C.5)
        # Note! Fallback support ni sio yet implemented
        document = self.xinclude_loader("C5.xml")
        ukijumuisha self.assertRaises(OSError) kama cm:
            ElementInclude.include(document, self.xinclude_loader)
        self.assertEqual(str(cm.exception), 'resource sio found')
        self.assertEqual(serialize(document),
            '<div xmlns:ns0="http://www.w3.org/2001/XInclude">\n'
            '  <ns0:include href="example.txt" parse="text">\n'
            '    <ns0:fallback>\n'
            '      <ns0:include href="fallback-example.txt" parse="text">\n'
            '        <ns0:fallback><a href="mailto:bob@example.org">Report error</a></ns0:fallback>\n'
            '      </ns0:include>\n'
            '    </ns0:fallback>\n'
            '  </ns0:include>\n'
            '</div>') # C5

    eleza test_xinclude_failures(self):
        kutoka xml.etree agiza ElementInclude

        # Test failure to locate included XML file.
        document = ET.XML(XINCLUDE["C1.xml"])
        ukijumuisha self.assertRaises(ElementInclude.FatalIncludeError) kama cm:
            ElementInclude.include(document, loader=self.none_loader)
        self.assertEqual(str(cm.exception),
                "cannot load 'disclaimer.xml' kama 'xml'")

        # Test failure to locate included text file.
        document = ET.XML(XINCLUDE["C2.xml"])
        ukijumuisha self.assertRaises(ElementInclude.FatalIncludeError) kama cm:
            ElementInclude.include(document, loader=self.none_loader)
        self.assertEqual(str(cm.exception),
                "cannot load 'count.txt' kama 'text'")

        # Test bad parse type.
        document = ET.XML(XINCLUDE_BAD["B1.xml"])
        ukijumuisha self.assertRaises(ElementInclude.FatalIncludeError) kama cm:
            ElementInclude.include(document, loader=self.none_loader)
        self.assertEqual(str(cm.exception),
                "unknown parse type kwenye xi:include tag ('BAD_TYPE')")

        # Test xi:fallback outside xi:include.
        document = ET.XML(XINCLUDE_BAD["B2.xml"])
        ukijumuisha self.assertRaises(ElementInclude.FatalIncludeError) kama cm:
            ElementInclude.include(document, loader=self.none_loader)
        self.assertEqual(str(cm.exception),
                "xi:fallback tag must be child of xi:include "
                "('{http://www.w3.org/2001/XInclude}fallback')")

# --------------------------------------------------------------------
# reported bugs

kundi BugsTest(unittest.TestCase):

    eleza test_bug_xmltoolkit21(self):
        # marshaller gives obscure errors kila non-string values

        eleza check(elem):
            ukijumuisha self.assertRaises(TypeError) kama cm:
                serialize(elem)
            self.assertEqual(str(cm.exception),
                    'cannot serialize 123 (type int)')

        elem = ET.Element(123)
        check(elem) # tag

        elem = ET.Element("elem")
        elem.text = 123
        check(elem) # text

        elem = ET.Element("elem")
        elem.tail = 123
        check(elem) # tail

        elem = ET.Element("elem")
        elem.set(123, "123")
        check(elem) # attribute key

        elem = ET.Element("elem")
        elem.set("123", 123)
        check(elem) # attribute value

    eleza test_bug_xmltoolkit25(self):
        # typo kwenye ElementTree.findtext

        elem = ET.XML(SAMPLE_XML)
        tree = ET.ElementTree(elem)
        self.assertEqual(tree.findtext("tag"), 'text')
        self.assertEqual(tree.findtext("section/tag"), 'subtext')

    eleza test_bug_xmltoolkit28(self):
        # .//tag causes exceptions

        tree = ET.XML("<doc><table><tbody/></table></doc>")
        self.assertEqual(summarize_list(tree.findall(".//thead")), [])
        self.assertEqual(summarize_list(tree.findall(".//tbody")), ['tbody'])

    eleza test_bug_xmltoolkitX1(self):
        # dump() doesn't flush the output buffer

        tree = ET.XML("<doc><table><tbody/></table></doc>")
        ukijumuisha support.captured_stdout() kama stdout:
            ET.dump(tree)
            self.assertEqual(stdout.getvalue(), '<doc><table><tbody /></table></doc>\n')

    eleza test_bug_xmltoolkit39(self):
        # non-ascii element na attribute names doesn't work

        tree = ET.XML(b"<?xml version='1.0' encoding='iso-8859-1'?><t\xe4g />")
        self.assertEqual(ET.tostring(tree, "utf-8"), b'<t\xc3\xa4g />')

        tree = ET.XML(b"<?xml version='1.0' encoding='iso-8859-1'?>"
                      b"<tag \xe4ttr='v&#228;lue' />")
        self.assertEqual(tree.attrib, {'\xe4ttr': 'v\xe4lue'})
        self.assertEqual(ET.tostring(tree, "utf-8"),
                b'<tag \xc3\xa4ttr="v\xc3\xa4lue" />')

        tree = ET.XML(b"<?xml version='1.0' encoding='iso-8859-1'?>"
                      b'<t\xe4g>text</t\xe4g>')
        self.assertEqual(ET.tostring(tree, "utf-8"),
                b'<t\xc3\xa4g>text</t\xc3\xa4g>')

        tree = ET.Element("t\u00e4g")
        self.assertEqual(ET.tostring(tree, "utf-8"), b'<t\xc3\xa4g />')

        tree = ET.Element("tag")
        tree.set("\u00e4ttr", "v\u00e4lue")
        self.assertEqual(ET.tostring(tree, "utf-8"),
                b'<tag \xc3\xa4ttr="v\xc3\xa4lue" />')

    eleza test_bug_xmltoolkit54(self):
        # problems handling internally defined entities

        e = ET.XML("<!DOCTYPE doc [<!ENTITY ldots '&#x8230;'>]>"
                   '<doc>&ldots;</doc>')
        self.assertEqual(serialize(e, encoding="us-ascii"),
                b'<doc>&#33328;</doc>')
        self.assertEqual(serialize(e), '<doc>\u8230</doc>')

    eleza test_bug_xmltoolkit55(self):
        # make sure we're reporting the first error, sio the last

        ukijumuisha self.assertRaises(ET.ParseError) kama cm:
            ET.XML(b"<!DOCTYPE doc SYSTEM 'doc.dtd'>"
                   b'<doc>&ldots;&ndots;&rdots;</doc>')
        self.assertEqual(str(cm.exception),
                'undefined entity &ldots;: line 1, column 36')

    eleza test_bug_xmltoolkit60(self):
        # Handle crash kwenye stream source.

        kundi ExceptionFile:
            eleza read(self, x):
                ashiria OSError

        self.assertRaises(OSError, ET.parse, ExceptionFile())

    eleza test_bug_xmltoolkit62(self):
        # Don't crash when using custom entities.

        ENTITIES = {'rsquo': '\u2019', 'lsquo': '\u2018'}
        parser = ET.XMLParser()
        parser.entity.update(ENTITIES)
        parser.feed("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE patent-application-publication SYSTEM "pap-v15-2001-01-31.dtd" []>
<patent-application-publication>
<subdoc-abstract>
<paragraph id="A-0001" lvl="0">A new cultivar of Begonia plant named &lsquo;BCT9801BEG&rsquo;.</paragraph>
</subdoc-abstract>
</patent-application-publication>""")
        t = parser.close()
        self.assertEqual(t.find('.//paragraph').text,
            'A new cultivar of Begonia plant named \u2018BCT9801BEG\u2019.')

    @unittest.skipIf(sys.gettrace(), "Skips under coverage.")
    eleza test_bug_xmltoolkit63(self):
        # Check reference leak.
        eleza xmltoolkit63():
            tree = ET.TreeBuilder()
            tree.start("tag", {})
            tree.data("text")
            tree.end("tag")

        xmltoolkit63()
        count = sys.getrefcount(Tupu)
        kila i kwenye range(1000):
            xmltoolkit63()
        self.assertEqual(sys.getrefcount(Tupu), count)

    eleza test_bug_200708_newline(self):
        # Preserve newlines kwenye attributes.

        e = ET.Element('SomeTag', text="eleza _f():\n  rudisha 3\n")
        self.assertEqual(ET.tostring(e),
                b'<SomeTag text="eleza _f():&#10;  rudisha 3&#10;" />')
        self.assertEqual(ET.XML(ET.tostring(e)).get("text"),
                'eleza _f():\n  rudisha 3\n')
        self.assertEqual(ET.tostring(ET.XML(ET.tostring(e))),
                b'<SomeTag text="eleza _f():&#10;  rudisha 3&#10;" />')

    eleza test_bug_200708_close(self):
        # Test default builder.
        parser = ET.XMLParser() # default
        parser.feed("<element>some text</element>")
        self.assertEqual(parser.close().tag, 'element')

        # Test custom builder.
        kundi EchoTarget:
            eleza close(self):
                rudisha ET.Element("element") # simulate root
        parser = ET.XMLParser(target=EchoTarget())
        parser.feed("<element>some text</element>")
        self.assertEqual(parser.close().tag, 'element')

    eleza test_bug_200709_default_namespace(self):
        e = ET.Element("{default}elem")
        s = ET.SubElement(e, "{default}elem")
        self.assertEqual(serialize(e, default_namespace="default"), # 1
                '<elem xmlns="default"><elem /></elem>')

        e = ET.Element("{default}elem")
        s = ET.SubElement(e, "{default}elem")
        s = ET.SubElement(e, "{not-default}elem")
        self.assertEqual(serialize(e, default_namespace="default"), # 2
            '<elem xmlns="default" xmlns:ns1="not-default">'
            '<elem />'
            '<ns1:elem />'
            '</elem>')

        e = ET.Element("{default}elem")
        s = ET.SubElement(e, "{default}elem")
        s = ET.SubElement(e, "elem") # unprefixed name
        ukijumuisha self.assertRaises(ValueError) kama cm:
            serialize(e, default_namespace="default") # 3
        self.assertEqual(str(cm.exception),
                'cannot use non-qualified names ukijumuisha default_namespace option')

    eleza test_bug_200709_register_namespace(self):
        e = ET.Element("{http://namespace.invalid/does/not/exist/}title")
        self.assertEqual(ET.tostring(e),
            b'<ns0:title xmlns:ns0="http://namespace.invalid/does/not/exist/" />')
        ET.register_namespace("foo", "http://namespace.invalid/does/not/exist/")
        e = ET.Element("{http://namespace.invalid/does/not/exist/}title")
        self.assertEqual(ET.tostring(e),
            b'<foo:title xmlns:foo="http://namespace.invalid/does/not/exist/" />')

        # And the Dublin Core namespace ni kwenye the default list:

        e = ET.Element("{http://purl.org/dc/elements/1.1/}title")
        self.assertEqual(ET.tostring(e),
            b'<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/" />')

    eleza test_bug_200709_element_comment(self):
        # Not sure ikiwa this can be fixed, really (since the serializer needs
        # ET.Comment, sio cET.comment).

        a = ET.Element('a')
        a.append(ET.Comment('foo'))
        self.assertEqual(a[0].tag, ET.Comment)

        a = ET.Element('a')
        a.append(ET.PI('foo'))
        self.assertEqual(a[0].tag, ET.PI)

    eleza test_bug_200709_element_insert(self):
        a = ET.Element('a')
        b = ET.SubElement(a, 'b')
        c = ET.SubElement(a, 'c')
        d = ET.Element('d')
        a.insert(0, d)
        self.assertEqual(summarize_list(a), ['d', 'b', 'c'])
        a.insert(-1, d)
        self.assertEqual(summarize_list(a), ['d', 'b', 'd', 'c'])

    eleza test_bug_200709_iter_comment(self):
        a = ET.Element('a')
        b = ET.SubElement(a, 'b')
        comment_b = ET.Comment("TEST-b")
        b.append(comment_b)
        self.assertEqual(summarize_list(a.iter(ET.Comment)), [ET.Comment])

    # --------------------------------------------------------------------
    # reported on bugs.python.org

    eleza test_bug_1534630(self):
        bob = ET.TreeBuilder()
        e = bob.data("data")
        e = bob.start("tag", {})
        e = bob.end("tag")
        e = bob.close()
        self.assertEqual(serialize(e), '<tag />')

    eleza test_issue6233(self):
        e = ET.XML(b"<?xml version='1.0' encoding='utf-8'?>"
                   b'<body>t\xc3\xa3g</body>')
        self.assertEqual(ET.tostring(e, 'ascii'),
                b"<?xml version='1.0' encoding='ascii'?>\n"
                b'<body>t&#227;g</body>')
        e = ET.XML(b"<?xml version='1.0' encoding='iso-8859-1'?>"
                   b'<body>t\xe3g</body>')
        self.assertEqual(ET.tostring(e, 'ascii'),
                b"<?xml version='1.0' encoding='ascii'?>\n"
                b'<body>t&#227;g</body>')

    eleza test_issue3151(self):
        e = ET.XML('<prefix:localname xmlns:prefix="${stuff}"/>')
        self.assertEqual(e.tag, '{${stuff}}localname')
        t = ET.ElementTree(e)
        self.assertEqual(ET.tostring(e), b'<ns0:localname xmlns:ns0="${stuff}" />')

    eleza test_issue6565(self):
        elem = ET.XML("<body><tag/></body>")
        self.assertEqual(summarize_list(elem), ['tag'])
        newelem = ET.XML(SAMPLE_XML)
        elem[:] = newelem[:]
        self.assertEqual(summarize_list(elem), ['tag', 'tag', 'section'])

    eleza test_issue10777(self):
        # Registering a namespace twice caused a "dictionary changed size during
        # iteration" bug.

        ET.register_namespace('test10777', 'http://myuri/')
        ET.register_namespace('test10777', 'http://myuri/')

    eleza test_lost_text(self):
        # Issue #25902: Borrowed text can disappear
        kundi Text:
            eleza __bool__(self):
                e.text = 'changed'
                rudisha Kweli

        e = ET.Element('tag')
        e.text = Text()
        i = e.itertext()
        t = next(i)
        self.assertIsInstance(t, Text)
        self.assertIsInstance(e.text, str)
        self.assertEqual(e.text, 'changed')

    eleza test_lost_tail(self):
        # Issue #25902: Borrowed tail can disappear
        kundi Text:
            eleza __bool__(self):
                e[0].tail = 'changed'
                rudisha Kweli

        e = ET.Element('root')
        e.append(ET.Element('tag'))
        e[0].tail = Text()
        i = e.itertext()
        t = next(i)
        self.assertIsInstance(t, Text)
        self.assertIsInstance(e[0].tail, str)
        self.assertEqual(e[0].tail, 'changed')

    eleza test_lost_elem(self):
        # Issue #25902: Borrowed element can disappear
        kundi Tag:
            eleza __eq__(self, other):
                e[0] = ET.Element('changed')
                next(i)
                rudisha Kweli

        e = ET.Element('root')
        e.append(ET.Element(Tag()))
        e.append(ET.Element('tag'))
        i = e.iter('tag')
        jaribu:
            t = next(i)
        tatizo ValueError:
            self.skipTest('generators are sio reentrant')
        self.assertIsInstance(t.tag, Tag)
        self.assertIsInstance(e[0].tag, str)
        self.assertEqual(e[0].tag, 'changed')

    eleza check_expat224_utf8_bug(self, text):
        xml = b'<a b="%s"/>' % text
        root = ET.XML(xml)
        self.assertEqual(root.get('b'), text.decode('utf-8'))

    eleza test_expat224_utf8_bug(self):
        # bpo-31170: Expat 2.2.3 had a bug kwenye its UTF-8 decoder.
        # Check that Expat 2.2.4 fixed the bug.
        #
        # Test buffer bounds at odd na even positions.

        text = b'\xc3\xa0' * 1024
        self.check_expat224_utf8_bug(text)

        text = b'x' + b'\xc3\xa0' * 1024
        self.check_expat224_utf8_bug(text)

    eleza test_expat224_utf8_bug_file(self):
        ukijumuisha open(UTF8_BUG_XMLFILE, 'rb') kama fp:
            raw = fp.read()
        root = ET.kutokastring(raw)
        xmlattr = root.get('b')

        # "Parse" manually the XML file to extract the value of the 'b'
        # attribute of the <a b='xxx' /> XML element
        text = raw.decode('utf-8').strip()
        text = text.replace('\r\n', ' ')
        text = text[6:-4]
        self.assertEqual(root.get('b'), text)



# --------------------------------------------------------------------


kundi BasicElementTest(ElementTestCase, unittest.TestCase):

    eleza test___init__(self):
        tag = "foo"
        attrib = { "zix": "wyp" }

        element_foo = ET.Element(tag, attrib)

        # traits of an element
        self.assertIsInstance(element_foo, ET.Element)
        self.assertIn("tag", dir(element_foo))
        self.assertIn("attrib", dir(element_foo))
        self.assertIn("text", dir(element_foo))
        self.assertIn("tail", dir(element_foo))

        # string attributes have expected values
        self.assertEqual(element_foo.tag, tag)
        self.assertIsTupu(element_foo.text)
        self.assertIsTupu(element_foo.tail)

        # attrib ni a copy
        self.assertIsNot(element_foo.attrib, attrib)
        self.assertEqual(element_foo.attrib, attrib)

        # attrib isn't linked
        attrib["bar"] = "baz"
        self.assertIsNot(element_foo.attrib, attrib)
        self.assertNotEqual(element_foo.attrib, attrib)

    eleza test___copy__(self):
        element_foo = ET.Element("foo", { "zix": "wyp" })
        element_foo.append(ET.Element("bar", { "baz": "qix" }))

        element_foo2 = copy.copy(element_foo)

        # elements are sio the same
        self.assertIsNot(element_foo2, element_foo)

        # string attributes are equal
        self.assertEqual(element_foo2.tag, element_foo.tag)
        self.assertEqual(element_foo2.text, element_foo.text)
        self.assertEqual(element_foo2.tail, element_foo.tail)

        # number of children ni the same
        self.assertEqual(len(element_foo2), len(element_foo))

        # children are the same
        kila (child1, child2) kwenye itertools.zip_longest(element_foo, element_foo2):
            self.assertIs(child1, child2)

        # attrib ni a copy
        self.assertEqual(element_foo2.attrib, element_foo.attrib)

    eleza test___deepcopy__(self):
        element_foo = ET.Element("foo", { "zix": "wyp" })
        element_foo.append(ET.Element("bar", { "baz": "qix" }))

        element_foo2 = copy.deepcopy(element_foo)

        # elements are sio the same
        self.assertIsNot(element_foo2, element_foo)

        # string attributes are equal
        self.assertEqual(element_foo2.tag, element_foo.tag)
        self.assertEqual(element_foo2.text, element_foo.text)
        self.assertEqual(element_foo2.tail, element_foo.tail)

        # number of children ni the same
        self.assertEqual(len(element_foo2), len(element_foo))

        # children are sio the same
        kila (child1, child2) kwenye itertools.zip_longest(element_foo, element_foo2):
            self.assertIsNot(child1, child2)

        # attrib ni a copy
        self.assertIsNot(element_foo2.attrib, element_foo.attrib)
        self.assertEqual(element_foo2.attrib, element_foo.attrib)

        # attrib isn't linked
        element_foo.attrib["bar"] = "baz"
        self.assertIsNot(element_foo2.attrib, element_foo.attrib)
        self.assertNotEqual(element_foo2.attrib, element_foo.attrib)

    eleza test_augmentation_type_errors(self):
        e = ET.Element('joe')
        self.assertRaises(TypeError, e.append, 'b')
        self.assertRaises(TypeError, e.extend, [ET.Element('bar'), 'foo'])
        self.assertRaises(TypeError, e.insert, 0, 'foo')
        e[:] = [ET.Element('bar')]
        ukijumuisha self.assertRaises(TypeError):
            e[0] = 'foo'
        ukijumuisha self.assertRaises(TypeError):
            e[:] = [ET.Element('bar'), 'foo']

        ikiwa hasattr(e, '__setstate__'):
            state = {
                'tag': 'tag',
                '_children': [Tupu],  # non-Element
                'attrib': 'attr',
                'tail': 'tail',
                'text': 'text',
            }
            self.assertRaises(TypeError, e.__setstate__, state)

        ikiwa hasattr(e, '__deepcopy__'):
            kundi E(ET.Element):
                eleza __deepcopy__(self, memo):
                    rudisha Tupu  # non-Element
            e[:] = [E('bar')]
            self.assertRaises(TypeError, copy.deepcopy, e)

    eleza test_cyclic_gc(self):
        kundi Dummy:
            pita

        # Test the shortest cycle: d->element->d
        d = Dummy()
        d.dummyref = ET.Element('joe', attr=d)
        wref = weakref.ref(d)
        toa d
        gc_collect()
        self.assertIsTupu(wref())

        # A longer cycle: d->e->e2->d
        e = ET.Element('joe')
        d = Dummy()
        d.dummyref = e
        wref = weakref.ref(d)
        e2 = ET.SubElement(e, 'foo', attr=d)
        toa d, e, e2
        gc_collect()
        self.assertIsTupu(wref())

        # A cycle between Element objects kama children of one another
        # e1->e2->e3->e1
        e1 = ET.Element('e1')
        e2 = ET.Element('e2')
        e3 = ET.Element('e3')
        e3.append(e1)
        e2.append(e3)
        e1.append(e2)
        wref = weakref.ref(e1)
        toa e1, e2, e3
        gc_collect()
        self.assertIsTupu(wref())

    eleza test_weakref(self):
        flag = Uongo
        eleza wref_cb(w):
            nonlocal flag
            flag = Kweli
        e = ET.Element('e')
        wref = weakref.ref(e, wref_cb)
        self.assertEqual(wref().tag, 'e')
        toa e
        self.assertEqual(flag, Kweli)
        self.assertEqual(wref(), Tupu)

    eleza test_get_keyword_args(self):
        e1 = ET.Element('foo' , x=1, y=2, z=3)
        self.assertEqual(e1.get('x', default=7), 1)
        self.assertEqual(e1.get('w', default=7), 7)

    eleza test_pickle(self):
        # issue #16076: the C implementation wasn't pickleable.
        kila proto kwenye range(2, pickle.HIGHEST_PROTOCOL + 1):
            kila dumper, loader kwenye product(self.modules, repeat=2):
                e = dumper.Element('foo', bar=42)
                e.text = "text goes here"
                e.tail = "opposite of head"
                dumper.SubElement(e, 'child').append(dumper.Element('grandchild'))
                e.append(dumper.Element('child'))
                e.findall('.//grandchild')[0].set('attr', 'other value')

                e2 = self.pickleRoundTrip(e, 'xml.etree.ElementTree',
                                          dumper, loader, proto)

                self.assertEqual(e2.tag, 'foo')
                self.assertEqual(e2.attrib['bar'], 42)
                self.assertEqual(len(e2), 2)
                self.assertEqualElements(e, e2)

    eleza test_pickle_issue18997(self):
        kila proto kwenye range(2, pickle.HIGHEST_PROTOCOL + 1):
            kila dumper, loader kwenye product(self.modules, repeat=2):
                XMLTEXT = """<?xml version="1.0"?>
                    <group><dogs>4</dogs>
                    </group>"""
                e1 = dumper.kutokastring(XMLTEXT)
                ikiwa hasattr(e1, '__getstate__'):
                    self.assertEqual(e1.__getstate__()['tag'], 'group')
                e2 = self.pickleRoundTrip(e1, 'xml.etree.ElementTree',
                                          dumper, loader, proto)
                self.assertEqual(e2.tag, 'group')
                self.assertEqual(e2[0].tag, 'dogs')


kundi BadElementTest(ElementTestCase, unittest.TestCase):
    eleza test_extend_mutable_list(self):
        kundi X:
            @property
            eleza __class__(self):
                L[:] = [ET.Element('baz')]
                rudisha ET.Element
        L = [X()]
        e = ET.Element('foo')
        jaribu:
            e.extend(L)
        tatizo TypeError:
            pita

        kundi Y(X, ET.Element):
            pita
        L = [Y('x')]
        e = ET.Element('foo')
        e.extend(L)

    eleza test_extend_mutable_list2(self):
        kundi X:
            @property
            eleza __class__(self):
                toa L[:]
                rudisha ET.Element
        L = [X(), ET.Element('baz')]
        e = ET.Element('foo')
        jaribu:
            e.extend(L)
        tatizo TypeError:
            pita

        kundi Y(X, ET.Element):
            pita
        L = [Y('bar'), ET.Element('baz')]
        e = ET.Element('foo')
        e.extend(L)

    eleza test_remove_with_mutating(self):
        kundi X(ET.Element):
            eleza __eq__(self, o):
                toa e[:]
                rudisha Uongo
        e = ET.Element('foo')
        e.extend([X('bar')])
        self.assertRaises(ValueError, e.remove, ET.Element('baz'))

        e = ET.Element('foo')
        e.extend([ET.Element('bar')])
        self.assertRaises(ValueError, e.remove, X('baz'))

    eleza test_recursive_repr(self):
        # Issue #25455
        e = ET.Element('foo')
        ukijumuisha swap_attr(e, 'tag', e):
            ukijumuisha self.assertRaises(RuntimeError):
                repr(e)  # Should sio crash

    eleza test_element_get_text(self):
        # Issue #27863
        kundi X(str):
            eleza __del__(self):
                jaribu:
                    elem.text
                tatizo NameError:
                    pita

        b = ET.TreeBuilder()
        b.start('tag', {})
        b.data('ABCD')
        b.data(X('EFGH'))
        b.data('IJKL')
        b.end('tag')

        elem = b.close()
        self.assertEqual(elem.text, 'ABCDEFGHIJKL')

    eleza test_element_get_tail(self):
        # Issue #27863
        kundi X(str):
            eleza __del__(self):
                jaribu:
                    elem[0].tail
                tatizo NameError:
                    pita

        b = ET.TreeBuilder()
        b.start('root', {})
        b.start('tag', {})
        b.end('tag')
        b.data('ABCD')
        b.data(X('EFGH'))
        b.data('IJKL')
        b.end('root')

        elem = b.close()
        self.assertEqual(elem[0].tail, 'ABCDEFGHIJKL')

    eleza test_subscr(self):
        # Issue #27863
        kundi X:
            eleza __index__(self):
                toa e[:]
                rudisha 1

        e = ET.Element('elem')
        e.append(ET.Element('child'))
        e[:X()]  # shouldn't crash

        e.append(ET.Element('child'))
        e[0:10:X()]  # shouldn't crash

    eleza test_ass_subscr(self):
        # Issue #27863
        kundi X:
            eleza __index__(self):
                e[:] = []
                rudisha 1

        e = ET.Element('elem')
        kila _ kwenye range(10):
            e.insert(0, ET.Element('child'))

        e[0:10:X()] = []  # shouldn't crash

    eleza test_treebuilder_start(self):
        # Issue #27863
        eleza element_factory(x, y):
            rudisha []
        b = ET.TreeBuilder(element_factory=element_factory)

        b.start('tag', {})
        b.data('ABCD')
        self.assertRaises(AttributeError, b.start, 'tag2', {})
        toa b
        gc_collect()

    eleza test_treebuilder_end(self):
        # Issue #27863
        eleza element_factory(x, y):
            rudisha []
        b = ET.TreeBuilder(element_factory=element_factory)

        b.start('tag', {})
        b.data('ABCD')
        self.assertRaises(AttributeError, b.end, 'tag')
        toa b
        gc_collect()


kundi MutatingElementPath(str):
    eleza __new__(cls, elem, *args):
        self = str.__new__(cls, *args)
        self.elem = elem
        rudisha self
    eleza __eq__(self, o):
        toa self.elem[:]
        rudisha Kweli
MutatingElementPath.__hash__ = str.__hash__

kundi BadElementPath(str):
    eleza __eq__(self, o):
        ashiria 1/0
BadElementPath.__hash__ = str.__hash__

kundi BadElementPathTest(ElementTestCase, unittest.TestCase):
    eleza setUp(self):
        super().setUp()
        kutoka xml.etree agiza ElementPath
        self.path_cache = ElementPath._cache
        ElementPath._cache = {}

    eleza tearDown(self):
        kutoka xml.etree agiza ElementPath
        ElementPath._cache = self.path_cache
        super().tearDown()

    eleza test_find_with_mutating(self):
        e = ET.Element('foo')
        e.extend([ET.Element('bar')])
        e.find(MutatingElementPath(e, 'x'))

    eleza test_find_with_error(self):
        e = ET.Element('foo')
        e.extend([ET.Element('bar')])
        jaribu:
            e.find(BadElementPath('x'))
        tatizo ZeroDivisionError:
            pita

    eleza test_findtext_with_mutating(self):
        e = ET.Element('foo')
        e.extend([ET.Element('bar')])
        e.findtext(MutatingElementPath(e, 'x'))

    eleza test_findtext_with_error(self):
        e = ET.Element('foo')
        e.extend([ET.Element('bar')])
        jaribu:
            e.findtext(BadElementPath('x'))
        tatizo ZeroDivisionError:
            pita

    eleza test_findall_with_mutating(self):
        e = ET.Element('foo')
        e.extend([ET.Element('bar')])
        e.findall(MutatingElementPath(e, 'x'))

    eleza test_findall_with_error(self):
        e = ET.Element('foo')
        e.extend([ET.Element('bar')])
        jaribu:
            e.findall(BadElementPath('x'))
        tatizo ZeroDivisionError:
            pita


kundi ElementTreeTypeTest(unittest.TestCase):
    eleza test_istype(self):
        self.assertIsInstance(ET.ParseError, type)
        self.assertIsInstance(ET.QName, type)
        self.assertIsInstance(ET.ElementTree, type)
        self.assertIsInstance(ET.Element, type)
        self.assertIsInstance(ET.TreeBuilder, type)
        self.assertIsInstance(ET.XMLParser, type)

    eleza test_Element_subclass_trivial(self):
        kundi MyElement(ET.Element):
            pita

        mye = MyElement('foo')
        self.assertIsInstance(mye, ET.Element)
        self.assertIsInstance(mye, MyElement)
        self.assertEqual(mye.tag, 'foo')

        # test that attribute assignment works (issue 14849)
        mye.text = "joe"
        self.assertEqual(mye.text, "joe")

    eleza test_Element_subclass_constructor(self):
        kundi MyElement(ET.Element):
            eleza __init__(self, tag, attrib={}, **extra):
                super(MyElement, self).__init__(tag + '__', attrib, **extra)

        mye = MyElement('foo', {'a': 1, 'b': 2}, c=3, d=4)
        self.assertEqual(mye.tag, 'foo__')
        self.assertEqual(sorted(mye.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4)])

    eleza test_Element_subclass_new_method(self):
        kundi MyElement(ET.Element):
            eleza newmethod(self):
                rudisha self.tag

        mye = MyElement('joe')
        self.assertEqual(mye.newmethod(), 'joe')

    eleza test_Element_subclass_find(self):
        kundi MyElement(ET.Element):
            pita

        e = ET.Element('foo')
        e.text = 'text'
        sub = MyElement('bar')
        sub.text = 'subtext'
        e.append(sub)
        self.assertEqual(e.findtext('bar'), 'subtext')
        self.assertEqual(e.find('bar').tag, 'bar')
        found = list(e.findall('bar'))
        self.assertEqual(len(found), 1, found)
        self.assertEqual(found[0].tag, 'bar')


kundi ElementFindTest(unittest.TestCase):
    eleza test_find_simple(self):
        e = ET.XML(SAMPLE_XML)
        self.assertEqual(e.find('tag').tag, 'tag')
        self.assertEqual(e.find('section/tag').tag, 'tag')
        self.assertEqual(e.find('./tag').tag, 'tag')

        e[2] = ET.XML(SAMPLE_SECTION)
        self.assertEqual(e.find('section/nexttag').tag, 'nexttag')

        self.assertEqual(e.findtext('./tag'), 'text')
        self.assertEqual(e.findtext('section/tag'), 'subtext')

        # section/nexttag ni found but has no text
        self.assertEqual(e.findtext('section/nexttag'), '')
        self.assertEqual(e.findtext('section/nexttag', 'default'), '')

        # tog doesn't exist na 'default' kicks in
        self.assertIsTupu(e.findtext('tog'))
        self.assertEqual(e.findtext('tog', 'default'), 'default')

        # Issue #16922
        self.assertEqual(ET.XML('<tag><empty /></tag>').findtext('empty'), '')

    eleza test_find_xpath(self):
        LINEAR_XML = '''
        <body>
            <tag class='a'/>
            <tag class='b'/>
            <tag class='c'/>
            <tag class='d'/>
        </body>'''
        e = ET.XML(LINEAR_XML)

        # Test kila numeric indexing na last()
        self.assertEqual(e.find('./tag[1]').attrib['class'], 'a')
        self.assertEqual(e.find('./tag[2]').attrib['class'], 'b')
        self.assertEqual(e.find('./tag[last()]').attrib['class'], 'd')
        self.assertEqual(e.find('./tag[last()-1]').attrib['class'], 'c')
        self.assertEqual(e.find('./tag[last()-2]').attrib['class'], 'b')

        self.assertRaisesRegex(SyntaxError, 'XPath', e.find, './tag[0]')
        self.assertRaisesRegex(SyntaxError, 'XPath', e.find, './tag[-1]')
        self.assertRaisesRegex(SyntaxError, 'XPath', e.find, './tag[last()-0]')
        self.assertRaisesRegex(SyntaxError, 'XPath', e.find, './tag[last()+1]')

    eleza test_findall(self):
        e = ET.XML(SAMPLE_XML)
        e[2] = ET.XML(SAMPLE_SECTION)
        self.assertEqual(summarize_list(e.findall('.')), ['body'])
        self.assertEqual(summarize_list(e.findall('tag')), ['tag', 'tag'])
        self.assertEqual(summarize_list(e.findall('tog')), [])
        self.assertEqual(summarize_list(e.findall('tog/foo')), [])
        self.assertEqual(summarize_list(e.findall('*')),
            ['tag', 'tag', 'section'])
        self.assertEqual(summarize_list(e.findall('.//tag')),
            ['tag'] * 4)
        self.assertEqual(summarize_list(e.findall('section/tag')), ['tag'])
        self.assertEqual(summarize_list(e.findall('section//tag')), ['tag'] * 2)
        self.assertEqual(summarize_list(e.findall('section/*')),
            ['tag', 'nexttag', 'nextsection'])
        self.assertEqual(summarize_list(e.findall('section//*')),
            ['tag', 'nexttag', 'nextsection', 'tag'])
        self.assertEqual(summarize_list(e.findall('section/.//*')),
            ['tag', 'nexttag', 'nextsection', 'tag'])
        self.assertEqual(summarize_list(e.findall('*/*')),
            ['tag', 'nexttag', 'nextsection'])
        self.assertEqual(summarize_list(e.findall('*//*')),
            ['tag', 'nexttag', 'nextsection', 'tag'])
        self.assertEqual(summarize_list(e.findall('*/tag')), ['tag'])
        self.assertEqual(summarize_list(e.findall('*/./tag')), ['tag'])
        self.assertEqual(summarize_list(e.findall('./tag')), ['tag'] * 2)
        self.assertEqual(summarize_list(e.findall('././tag')), ['tag'] * 2)

        self.assertEqual(summarize_list(e.findall('.//tag[@class]')),
            ['tag'] * 3)
        self.assertEqual(summarize_list(e.findall('.//tag[@class="a"]')),
            ['tag'])
        self.assertEqual(summarize_list(e.findall('.//tag[@class="b"]')),
            ['tag'] * 2)
        self.assertEqual(summarize_list(e.findall('.//tag[@id]')),
            ['tag'])
        self.assertEqual(summarize_list(e.findall('.//section[tag]')),
            ['section'])
        self.assertEqual(summarize_list(e.findall('.//section[element]')), [])
        self.assertEqual(summarize_list(e.findall('../tag')), [])
        self.assertEqual(summarize_list(e.findall('section/../tag')),
            ['tag'] * 2)
        self.assertEqual(e.findall('section//'), e.findall('section//*'))

        self.assertEqual(summarize_list(e.findall(".//section[tag='subtext']")),
            ['section'])
        self.assertEqual(summarize_list(e.findall(".//section[tag ='subtext']")),
            ['section'])
        self.assertEqual(summarize_list(e.findall(".//section[tag= 'subtext']")),
            ['section'])
        self.assertEqual(summarize_list(e.findall(".//section[tag = 'subtext']")),
            ['section'])
        self.assertEqual(summarize_list(e.findall(".//section[ tag = 'subtext' ]")),
            ['section'])

        self.assertEqual(summarize_list(e.findall(".//tag[.='subtext']")),
                         ['tag'])
        self.assertEqual(summarize_list(e.findall(".//tag[. ='subtext']")),
                         ['tag'])
        self.assertEqual(summarize_list(e.findall('.//tag[.= "subtext"]')),
                         ['tag'])
        self.assertEqual(summarize_list(e.findall('.//tag[ . = "subtext" ]')),
                         ['tag'])
        self.assertEqual(summarize_list(e.findall(".//tag[. = 'subtext']")),
                         ['tag'])
        self.assertEqual(summarize_list(e.findall(".//tag[. = 'subtext ']")),
                         [])
        self.assertEqual(summarize_list(e.findall(".//tag[.= ' subtext']")),
                         [])

        # duplicate section => 2x tag matches
        e[1] = e[2]
        self.assertEqual(summarize_list(e.findall(".//section[tag = 'subtext']")),
                         ['section', 'section'])
        self.assertEqual(summarize_list(e.findall(".//tag[. = 'subtext']")),
                         ['tag', 'tag'])

    eleza test_test_find_with_ns(self):
        e = ET.XML(SAMPLE_XML_NS)
        self.assertEqual(summarize_list(e.findall('tag')), [])
        self.assertEqual(
            summarize_list(e.findall("{http://effbot.org/ns}tag")),
            ['{http://effbot.org/ns}tag'] * 2)
        self.assertEqual(
            summarize_list(e.findall(".//{http://effbot.org/ns}tag")),
            ['{http://effbot.org/ns}tag'] * 3)

    eleza test_findall_different_nsmaps(self):
        root = ET.XML('''
            <a xmlns:x="X" xmlns:y="Y">
                <x:b><c/></x:b>
                <b/>
                <c><x:b/><b/></c><y:b/>
            </a>''')
        nsmap = {'xx': 'X'}
        self.assertEqual(len(root.findall(".//xx:b", namespaces=nsmap)), 2)
        self.assertEqual(len(root.findall(".//b", namespaces=nsmap)), 2)
        nsmap = {'xx': 'Y'}
        self.assertEqual(len(root.findall(".//xx:b", namespaces=nsmap)), 1)
        self.assertEqual(len(root.findall(".//b", namespaces=nsmap)), 2)
        nsmap = {'xx': 'X', '': 'Y'}
        self.assertEqual(len(root.findall(".//xx:b", namespaces=nsmap)), 2)
        self.assertEqual(len(root.findall(".//b", namespaces=nsmap)), 1)

    eleza test_findall_wildcard(self):
        root = ET.XML('''
            <a xmlns:x="X" xmlns:y="Y">
                <x:b><c/></x:b>
                <b/>
                <c><x:b/><b/></c><y:b/>
            </a>''')
        root.append(ET.Comment('test'))

        self.assertEqual(summarize_list(root.findall("{*}b")),
                         ['{X}b', 'b', '{Y}b'])
        self.assertEqual(summarize_list(root.findall("{*}c")),
                         ['c'])
        self.assertEqual(summarize_list(root.findall("{X}*")),
                         ['{X}b'])
        self.assertEqual(summarize_list(root.findall("{Y}*")),
                         ['{Y}b'])
        self.assertEqual(summarize_list(root.findall("{}*")),
                         ['b', 'c'])
        self.assertEqual(summarize_list(root.findall("{}b")),  # only kila consistency
                         ['b'])
        self.assertEqual(summarize_list(root.findall("{}b")),
                         summarize_list(root.findall("b")))
        self.assertEqual(summarize_list(root.findall("{*}*")),
                         ['{X}b', 'b', 'c', '{Y}b'])
        # This ni an unfortunate difference, but that's how find('*') works.
        self.assertEqual(summarize_list(root.findall("{*}*") + [root[-1]]),
                         summarize_list(root.findall("*")))

        self.assertEqual(summarize_list(root.findall(".//{*}b")),
                         ['{X}b', 'b', '{X}b', 'b', '{Y}b'])
        self.assertEqual(summarize_list(root.findall(".//{*}c")),
                         ['c', 'c'])
        self.assertEqual(summarize_list(root.findall(".//{X}*")),
                         ['{X}b', '{X}b'])
        self.assertEqual(summarize_list(root.findall(".//{Y}*")),
                         ['{Y}b'])
        self.assertEqual(summarize_list(root.findall(".//{}*")),
                         ['c', 'b', 'c', 'b'])
        self.assertEqual(summarize_list(root.findall(".//{}b")),  # only kila consistency
                         ['b', 'b'])
        self.assertEqual(summarize_list(root.findall(".//{}b")),
                         summarize_list(root.findall(".//b")))

    eleza test_bad_find(self):
        e = ET.XML(SAMPLE_XML)
        ukijumuisha self.assertRaisesRegex(SyntaxError, 'cannot use absolute path'):
            e.findall('/tag')

    eleza test_find_through_ElementTree(self):
        e = ET.XML(SAMPLE_XML)
        self.assertEqual(ET.ElementTree(e).find('tag').tag, 'tag')
        self.assertEqual(ET.ElementTree(e).findtext('tag'), 'text')
        self.assertEqual(summarize_list(ET.ElementTree(e).findall('tag')),
            ['tag'] * 2)
        # this produces a warning
        msg = ("This search ni broken kwenye 1.3 na earlier, na will be fixed "
               "in a future version.  If you rely on the current behaviour, "
               "change it to '.+'")
        ukijumuisha self.assertWarnsRegex(FutureWarning, msg):
            it = ET.ElementTree(e).findall('//tag')
        self.assertEqual(summarize_list(it), ['tag'] * 3)


kundi ElementIterTest(unittest.TestCase):
    eleza _ilist(self, elem, tag=Tupu):
        rudisha summarize_list(elem.iter(tag))

    eleza test_basic(self):
        doc = ET.XML("<html><body>this ni a <i>paragraph</i>.</body>..</html>")
        self.assertEqual(self._ilist(doc), ['html', 'body', 'i'])
        self.assertEqual(self._ilist(doc.find('body')), ['body', 'i'])
        self.assertEqual(next(doc.iter()).tag, 'html')
        self.assertEqual(''.join(doc.itertext()), 'this ni a paragraph...')
        self.assertEqual(''.join(doc.find('body').itertext()),
            'this ni a paragraph.')
        self.assertEqual(next(doc.itertext()), 'this ni a ')

        # iterparse should rudisha an iterator
        sourcefile = serialize(doc, to_string=Uongo)
        self.assertEqual(next(ET.iterparse(sourcefile))[0], 'end')

        # With an explicit parser too (issue #9708)
        sourcefile = serialize(doc, to_string=Uongo)
        parser = ET.XMLParser(target=ET.TreeBuilder())
        self.assertEqual(next(ET.iterparse(sourcefile, parser=parser))[0],
                         'end')

        tree = ET.ElementTree(Tupu)
        self.assertRaises(AttributeError, tree.iter)

        # Issue #16913
        doc = ET.XML("<root>a&amp;<sub>b&amp;</sub>c&amp;</root>")
        self.assertEqual(''.join(doc.itertext()), 'a&b&c&')

    eleza test_corners(self):
        # single root, no subelements
        a = ET.Element('a')
        self.assertEqual(self._ilist(a), ['a'])

        # one child
        b = ET.SubElement(a, 'b')
        self.assertEqual(self._ilist(a), ['a', 'b'])

        # one child na one grandchild
        c = ET.SubElement(b, 'c')
        self.assertEqual(self._ilist(a), ['a', 'b', 'c'])

        # two children, only first ukijumuisha grandchild
        d = ET.SubElement(a, 'd')
        self.assertEqual(self._ilist(a), ['a', 'b', 'c', 'd'])

        # replace first child by second
        a[0] = a[1]
        toa a[1]
        self.assertEqual(self._ilist(a), ['a', 'd'])

    eleza test_iter_by_tag(self):
        doc = ET.XML('''
            <document>
                <house>
                    <room>bedroom1</room>
                    <room>bedroom2</room>
                </house>
                <shed>nothing here
                </shed>
                <house>
                    <room>bedroom8</room>
                </house>
            </document>''')

        self.assertEqual(self._ilist(doc, 'room'), ['room'] * 3)
        self.assertEqual(self._ilist(doc, 'house'), ['house'] * 2)

        # test that iter also accepts 'tag' kama a keyword arg
        self.assertEqual(
            summarize_list(doc.iter(tag='room')),
            ['room'] * 3)

        # make sure both tag=Tupu na tag='*' rudisha all tags
        all_tags = ['document', 'house', 'room', 'room',
                    'shed', 'house', 'room']
        self.assertEqual(summarize_list(doc.iter()), all_tags)
        self.assertEqual(self._ilist(doc), all_tags)
        self.assertEqual(self._ilist(doc, '*'), all_tags)

    # Element.getiterator() ni deprecated.
    @checkwarnings(("This method will be removed kwenye future versions.  "
                    "Use .+ instead.", DeprecationWarning))
    eleza test_getiterator(self):
        doc = ET.XML('''
            <document>
                <house>
                    <room>bedroom1</room>
                    <room>bedroom2</room>
                </house>
                <shed>nothing here
                </shed>
                <house>
                    <room>bedroom8</room>
                </house>
            </document>''')

        self.assertEqual(summarize_list(doc.getiterator('room')),
                         ['room'] * 3)
        self.assertEqual(summarize_list(doc.getiterator('house')),
                         ['house'] * 2)

        # test that getiterator also accepts 'tag' kama a keyword arg
        self.assertEqual(
            summarize_list(doc.getiterator(tag='room')),
            ['room'] * 3)

        # make sure both tag=Tupu na tag='*' rudisha all tags
        all_tags = ['document', 'house', 'room', 'room',
                    'shed', 'house', 'room']
        self.assertEqual(summarize_list(doc.getiterator()), all_tags)
        self.assertEqual(summarize_list(doc.getiterator(Tupu)), all_tags)
        self.assertEqual(summarize_list(doc.getiterator('*')), all_tags)

    eleza test_copy(self):
        a = ET.Element('a')
        it = a.iter()
        ukijumuisha self.assertRaises(TypeError):
            copy.copy(it)

    eleza test_pickle(self):
        a = ET.Element('a')
        it = a.iter()
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises((TypeError, pickle.PicklingError)):
                pickle.dumps(it, proto)


kundi TreeBuilderTest(unittest.TestCase):
    sample1 = ('<!DOCTYPE html PUBLIC'
        ' "-//W3C//DTD XHTML 1.0 Transitional//EN"'
        ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        '<html>text<div>subtext</div>tail</html>')

    sample2 = '''<toplevel>sometext</toplevel>'''

    eleza _check_sample1_element(self, e):
        self.assertEqual(e.tag, 'html')
        self.assertEqual(e.text, 'text')
        self.assertEqual(e.tail, Tupu)
        self.assertEqual(e.attrib, {})
        children = list(e)
        self.assertEqual(len(children), 1)
        child = children[0]
        self.assertEqual(child.tag, 'div')
        self.assertEqual(child.text, 'subtext')
        self.assertEqual(child.tail, 'tail')
        self.assertEqual(child.attrib, {})

    eleza test_dummy_builder(self):
        kundi BaseDummyBuilder:
            eleza close(self):
                rudisha 42

        kundi DummyBuilder(BaseDummyBuilder):
            data = start = end = lambda *a: Tupu

        parser = ET.XMLParser(target=DummyBuilder())
        parser.feed(self.sample1)
        self.assertEqual(parser.close(), 42)

        parser = ET.XMLParser(target=BaseDummyBuilder())
        parser.feed(self.sample1)
        self.assertEqual(parser.close(), 42)

        parser = ET.XMLParser(target=object())
        parser.feed(self.sample1)
        self.assertIsTupu(parser.close())

    eleza test_treebuilder_comment(self):
        b = ET.TreeBuilder()
        self.assertEqual(b.comment('ctext').tag, ET.Comment)
        self.assertEqual(b.comment('ctext').text, 'ctext')

        b = ET.TreeBuilder(comment_factory=ET.Comment)
        self.assertEqual(b.comment('ctext').tag, ET.Comment)
        self.assertEqual(b.comment('ctext').text, 'ctext')

        b = ET.TreeBuilder(comment_factory=len)
        self.assertEqual(b.comment('ctext'), len('ctext'))

    eleza test_treebuilder_pi(self):
        b = ET.TreeBuilder()
        self.assertEqual(b.pi('target', Tupu).tag, ET.PI)
        self.assertEqual(b.pi('target', Tupu).text, 'target')

        b = ET.TreeBuilder(pi_factory=ET.PI)
        self.assertEqual(b.pi('target').tag, ET.PI)
        self.assertEqual(b.pi('target').text, "target")
        self.assertEqual(b.pi('pitarget', ' text ').tag, ET.PI)
        self.assertEqual(b.pi('pitarget', ' text ').text, "pitarget  text ")

        b = ET.TreeBuilder(pi_factory=lambda target, text: (len(target), text))
        self.assertEqual(b.pi('target'), (len('target'), Tupu))
        self.assertEqual(b.pi('pitarget', ' text '), (len('pitarget'), ' text '))

    eleza test_late_tail(self):
        # Issue #37399: The tail of an ignored comment could overwrite the text before it.
        kundi TreeBuilderSubclass(ET.TreeBuilder):
            pita

        xml = "<a>text<!-- comment -->tail</a>"
        a = ET.kutokastring(xml)
        self.assertEqual(a.text, "texttail")

        parser = ET.XMLParser(target=TreeBuilderSubclass())
        parser.feed(xml)
        a = parser.close()
        self.assertEqual(a.text, "texttail")

        xml = "<a>text<?pi data?>tail</a>"
        a = ET.kutokastring(xml)
        self.assertEqual(a.text, "texttail")

        xml = "<a>text<?pi data?>tail</a>"
        parser = ET.XMLParser(target=TreeBuilderSubclass())
        parser.feed(xml)
        a = parser.close()
        self.assertEqual(a.text, "texttail")

    eleza test_late_tail_mix_pi_comments(self):
        # Issue #37399: The tail of an ignored comment could overwrite the text before it.
        # Test appending tails to comments/pis.
        kundi TreeBuilderSubclass(ET.TreeBuilder):
            pita

        xml = "<a>text<?pi1?> <!-- comment -->\n<?pi2?>tail</a>"
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=Kweli))
        parser.feed(xml)
        a = parser.close()
        self.assertEqual(a[0].text, ' comment ')
        self.assertEqual(a[0].tail, '\ntail')
        self.assertEqual(a.text, "text ")

        parser = ET.XMLParser(target=TreeBuilderSubclass(insert_comments=Kweli))
        parser.feed(xml)
        a = parser.close()
        self.assertEqual(a[0].text, ' comment ')
        self.assertEqual(a[0].tail, '\ntail')
        self.assertEqual(a.text, "text ")

        xml = "<a>text<!-- comment -->\n<?pi data?>tail</a>"
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_pis=Kweli))
        parser.feed(xml)
        a = parser.close()
        self.assertEqual(a[0].text, 'pi data')
        self.assertEqual(a[0].tail, 'tail')
        self.assertEqual(a.text, "text\n")

        parser = ET.XMLParser(target=TreeBuilderSubclass(insert_pis=Kweli))
        parser.feed(xml)
        a = parser.close()
        self.assertEqual(a[0].text, 'pi data')
        self.assertEqual(a[0].tail, 'tail')
        self.assertEqual(a.text, "text\n")

    eleza test_treebuilder_elementfactory_none(self):
        parser = ET.XMLParser(target=ET.TreeBuilder(element_factory=Tupu))
        parser.feed(self.sample1)
        e = parser.close()
        self._check_sample1_element(e)

    eleza test_subclass(self):
        kundi MyTreeBuilder(ET.TreeBuilder):
            eleza foobar(self, x):
                rudisha x * 2

        tb = MyTreeBuilder()
        self.assertEqual(tb.foobar(10), 20)

        parser = ET.XMLParser(target=tb)
        parser.feed(self.sample1)

        e = parser.close()
        self._check_sample1_element(e)

    eleza test_subclass_comment_pi(self):
        kundi MyTreeBuilder(ET.TreeBuilder):
            eleza foobar(self, x):
                rudisha x * 2

        tb = MyTreeBuilder(comment_factory=ET.Comment, pi_factory=ET.PI)
        self.assertEqual(tb.foobar(10), 20)

        parser = ET.XMLParser(target=tb)
        parser.feed(self.sample1)
        parser.feed('<!-- a comment--><?and a pi?>')

        e = parser.close()
        self._check_sample1_element(e)

    eleza test_element_factory(self):
        lst = []
        eleza myfactory(tag, attrib):
            nonlocal lst
            lst.append(tag)
            rudisha ET.Element(tag, attrib)

        tb = ET.TreeBuilder(element_factory=myfactory)
        parser = ET.XMLParser(target=tb)
        parser.feed(self.sample2)
        parser.close()

        self.assertEqual(lst, ['toplevel'])

    eleza _check_element_factory_class(self, cls):
        tb = ET.TreeBuilder(element_factory=cls)

        parser = ET.XMLParser(target=tb)
        parser.feed(self.sample1)
        e = parser.close()
        self.assertIsInstance(e, cls)
        self._check_sample1_element(e)

    eleza test_element_factory_subclass(self):
        kundi MyElement(ET.Element):
            pita
        self._check_element_factory_class(MyElement)

    eleza test_element_factory_pure_python_subclass(self):
        # Mimick SimpleTAL's behaviour (issue #16089): both versions of
        # TreeBuilder should be able to cope ukijumuisha a subkundi of the
        # pure Python Element class.
        base = ET._Element_Py
        # Not kutoka a C extension
        self.assertEqual(base.__module__, 'xml.etree.ElementTree')
        # Force some multiple inheritance ukijumuisha a C kundi to make things
        # more interesting.
        kundi MyElement(base, ValueError):
            pita
        self._check_element_factory_class(MyElement)

    eleza test_doctype(self):
        kundi DoctypeParser:
            _doctype = Tupu

            eleza doctype(self, name, pubid, system):
                self._doctype = (name, pubid, system)

            eleza close(self):
                rudisha self._doctype

        parser = ET.XMLParser(target=DoctypeParser())
        parser.feed(self.sample1)

        self.assertEqual(parser.close(),
            ('html', '-//W3C//DTD XHTML 1.0 Transitional//EN',
             'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'))

    eleza test_builder_lookup_errors(self):
        kundi RaisingBuilder:
            eleza __init__(self, ashiria_in=Tupu, what=ValueError):
                self.ashiria_in = ashiria_in
                self.what = what

            eleza __getattr__(self, name):
                ikiwa name == self.ashiria_in:
                    ashiria self.what(self.ashiria_in)
                eleza handle(*args):
                    pita
                rudisha handle

        ET.XMLParser(target=RaisingBuilder())
        # cET also checks kila 'close' na 'doctype', PyET does it only at need
        kila event kwenye ('start', 'data', 'end', 'comment', 'pi'):
            ukijumuisha self.assertRaisesRegex(ValueError, event):
                ET.XMLParser(target=RaisingBuilder(event))

        ET.XMLParser(target=RaisingBuilder(what=AttributeError))
        kila event kwenye ('start', 'data', 'end', 'comment', 'pi'):
            parser = ET.XMLParser(target=RaisingBuilder(event, what=AttributeError))
            parser.feed(self.sample1)
            self.assertIsTupu(parser.close())


kundi XMLParserTest(unittest.TestCase):
    sample1 = b'<file><line>22</line></file>'
    sample2 = (b'<!DOCTYPE html PUBLIC'
        b' "-//W3C//DTD XHTML 1.0 Transitional//EN"'
        b' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        b'<html>text</html>')
    sample3 = ('<?xml version="1.0" encoding="iso-8859-1"?>\n'
        '<money value="$\xa3\u20ac\U0001017b">$\xa3\u20ac\U0001017b</money>')

    eleza _check_sample_element(self, e):
        self.assertEqual(e.tag, 'file')
        self.assertEqual(e[0].tag, 'line')
        self.assertEqual(e[0].text, '22')

    eleza test_constructor_args(self):
        parser2 = ET.XMLParser(encoding='utf-8',
                               target=ET.TreeBuilder())
        parser2.feed(self.sample1)
        self._check_sample_element(parser2.close())

    eleza test_subclass(self):
        kundi MyParser(ET.XMLParser):
            pita
        parser = MyParser()
        parser.feed(self.sample1)
        self._check_sample_element(parser.close())

    eleza test_doctype_warning(self):
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', DeprecationWarning)
            parser = ET.XMLParser()
            parser.feed(self.sample2)
            parser.close()

    eleza test_subclass_doctype(self):
        _doctype = Tupu
        kundi MyParserWithDoctype(ET.XMLParser):
            eleza doctype(self, *args, **kwargs):
                nonlocal _doctype
                _doctype = (args, kwargs)

        parser = MyParserWithDoctype()
        ukijumuisha self.assertWarnsRegex(RuntimeWarning, 'doctype'):
            parser.feed(self.sample2)
        parser.close()
        self.assertIsTupu(_doctype)

        _doctype = _doctype2 = Tupu
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', DeprecationWarning)
            warnings.simplefilter('error', RuntimeWarning)
            kundi DoctypeParser:
                eleza doctype(self, name, pubid, system):
                    nonlocal _doctype2
                    _doctype2 = (name, pubid, system)

            parser = MyParserWithDoctype(target=DoctypeParser())
            parser.feed(self.sample2)
            parser.close()
            self.assertIsTupu(_doctype)
            self.assertEqual(_doctype2,
                ('html', '-//W3C//DTD XHTML 1.0 Transitional//EN',
                 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'))

    eleza test_inherited_doctype(self):
        '''Ensure that ordinary usage ni sio deprecated (Issue 19176)'''
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', DeprecationWarning)
            warnings.simplefilter('error', RuntimeWarning)
            kundi MyParserWithoutDoctype(ET.XMLParser):
                pita
            parser = MyParserWithoutDoctype()
            parser.feed(self.sample2)
            parser.close()

    eleza test_parse_string(self):
        parser = ET.XMLParser(target=ET.TreeBuilder())
        parser.feed(self.sample3)
        e = parser.close()
        self.assertEqual(e.tag, 'money')
        self.assertEqual(e.attrib['value'], '$\xa3\u20ac\U0001017b')
        self.assertEqual(e.text, '$\xa3\u20ac\U0001017b')


kundi NamespaceParseTest(unittest.TestCase):
    eleza test_find_with_namespace(self):
        nsmap = {'h': 'hello', 'f': 'foo'}
        doc = ET.kutokastring(SAMPLE_XML_NS_ELEMS)

        self.assertEqual(len(doc.findall('{hello}table', nsmap)), 1)
        self.assertEqual(len(doc.findall('.//{hello}td', nsmap)), 2)
        self.assertEqual(len(doc.findall('.//{foo}name', nsmap)), 1)


kundi ElementSlicingTest(unittest.TestCase):
    eleza _elem_tags(self, elemlist):
        rudisha [e.tag kila e kwenye elemlist]

    eleza _subelem_tags(self, elem):
        rudisha self._elem_tags(list(elem))

    eleza _make_elem_with_children(self, numchildren):
        """Create an Element ukijumuisha a tag 'a', ukijumuisha the given amount of children
           named 'a0', 'a1' ... na so on.

        """
        e = ET.Element('a')
        kila i kwenye range(numchildren):
            ET.SubElement(e, 'a%s' % i)
        rudisha e

    eleza test_getslice_single_index(self):
        e = self._make_elem_with_children(10)

        self.assertEqual(e[1].tag, 'a1')
        self.assertEqual(e[-2].tag, 'a8')

        self.assertRaises(IndexError, lambda: e[12])
        self.assertRaises(IndexError, lambda: e[-12])

    eleza test_getslice_range(self):
        e = self._make_elem_with_children(6)

        self.assertEqual(self._elem_tags(e[3:]), ['a3', 'a4', 'a5'])
        self.assertEqual(self._elem_tags(e[3:6]), ['a3', 'a4', 'a5'])
        self.assertEqual(self._elem_tags(e[3:16]), ['a3', 'a4', 'a5'])
        self.assertEqual(self._elem_tags(e[3:5]), ['a3', 'a4'])
        self.assertEqual(self._elem_tags(e[3:-1]), ['a3', 'a4'])
        self.assertEqual(self._elem_tags(e[:2]), ['a0', 'a1'])

    eleza test_getslice_steps(self):
        e = self._make_elem_with_children(10)

        self.assertEqual(self._elem_tags(e[8:10:1]), ['a8', 'a9'])
        self.assertEqual(self._elem_tags(e[::3]), ['a0', 'a3', 'a6', 'a9'])
        self.assertEqual(self._elem_tags(e[::8]), ['a0', 'a8'])
        self.assertEqual(self._elem_tags(e[1::8]), ['a1', 'a9'])
        self.assertEqual(self._elem_tags(e[3::sys.maxsize]), ['a3'])
        self.assertEqual(self._elem_tags(e[3::sys.maxsize<<64]), ['a3'])

    eleza test_getslice_negative_steps(self):
        e = self._make_elem_with_children(4)

        self.assertEqual(self._elem_tags(e[::-1]), ['a3', 'a2', 'a1', 'a0'])
        self.assertEqual(self._elem_tags(e[::-2]), ['a3', 'a1'])
        self.assertEqual(self._elem_tags(e[3::-sys.maxsize]), ['a3'])
        self.assertEqual(self._elem_tags(e[3::-sys.maxsize-1]), ['a3'])
        self.assertEqual(self._elem_tags(e[3::-sys.maxsize<<64]), ['a3'])

    eleza test_delslice(self):
        e = self._make_elem_with_children(4)
        toa e[0:2]
        self.assertEqual(self._subelem_tags(e), ['a2', 'a3'])

        e = self._make_elem_with_children(4)
        toa e[0:]
        self.assertEqual(self._subelem_tags(e), [])

        e = self._make_elem_with_children(4)
        toa e[::-1]
        self.assertEqual(self._subelem_tags(e), [])

        e = self._make_elem_with_children(4)
        toa e[::-2]
        self.assertEqual(self._subelem_tags(e), ['a0', 'a2'])

        e = self._make_elem_with_children(4)
        toa e[1::2]
        self.assertEqual(self._subelem_tags(e), ['a0', 'a2'])

        e = self._make_elem_with_children(2)
        toa e[::2]
        self.assertEqual(self._subelem_tags(e), ['a1'])

    eleza test_setslice_single_index(self):
        e = self._make_elem_with_children(4)
        e[1] = ET.Element('b')
        self.assertEqual(self._subelem_tags(e), ['a0', 'b', 'a2', 'a3'])

        e[-2] = ET.Element('c')
        self.assertEqual(self._subelem_tags(e), ['a0', 'b', 'c', 'a3'])

        ukijumuisha self.assertRaises(IndexError):
            e[5] = ET.Element('d')
        ukijumuisha self.assertRaises(IndexError):
            e[-5] = ET.Element('d')
        self.assertEqual(self._subelem_tags(e), ['a0', 'b', 'c', 'a3'])

    eleza test_setslice_range(self):
        e = self._make_elem_with_children(4)
        e[1:3] = [ET.Element('b%s' % i) kila i kwenye range(2)]
        self.assertEqual(self._subelem_tags(e), ['a0', 'b0', 'b1', 'a3'])

        e = self._make_elem_with_children(4)
        e[1:3] = [ET.Element('b')]
        self.assertEqual(self._subelem_tags(e), ['a0', 'b', 'a3'])

        e = self._make_elem_with_children(4)
        e[1:3] = [ET.Element('b%s' % i) kila i kwenye range(3)]
        self.assertEqual(self._subelem_tags(e), ['a0', 'b0', 'b1', 'b2', 'a3'])

    eleza test_setslice_steps(self):
        e = self._make_elem_with_children(6)
        e[1:5:2] = [ET.Element('b%s' % i) kila i kwenye range(2)]
        self.assertEqual(self._subelem_tags(e), ['a0', 'b0', 'a2', 'b1', 'a4', 'a5'])

        e = self._make_elem_with_children(6)
        ukijumuisha self.assertRaises(ValueError):
            e[1:5:2] = [ET.Element('b')]
        ukijumuisha self.assertRaises(ValueError):
            e[1:5:2] = [ET.Element('b%s' % i) kila i kwenye range(3)]
        ukijumuisha self.assertRaises(ValueError):
            e[1:5:2] = []
        self.assertEqual(self._subelem_tags(e), ['a0', 'a1', 'a2', 'a3', 'a4', 'a5'])

        e = self._make_elem_with_children(4)
        e[1::sys.maxsize] = [ET.Element('b')]
        self.assertEqual(self._subelem_tags(e), ['a0', 'b', 'a2', 'a3'])
        e[1::sys.maxsize<<64] = [ET.Element('c')]
        self.assertEqual(self._subelem_tags(e), ['a0', 'c', 'a2', 'a3'])

    eleza test_setslice_negative_steps(self):
        e = self._make_elem_with_children(4)
        e[2:0:-1] = [ET.Element('b%s' % i) kila i kwenye range(2)]
        self.assertEqual(self._subelem_tags(e), ['a0', 'b1', 'b0', 'a3'])

        e = self._make_elem_with_children(4)
        ukijumuisha self.assertRaises(ValueError):
            e[2:0:-1] = [ET.Element('b')]
        ukijumuisha self.assertRaises(ValueError):
            e[2:0:-1] = [ET.Element('b%s' % i) kila i kwenye range(3)]
        ukijumuisha self.assertRaises(ValueError):
            e[2:0:-1] = []
        self.assertEqual(self._subelem_tags(e), ['a0', 'a1', 'a2', 'a3'])

        e = self._make_elem_with_children(4)
        e[1::-sys.maxsize] = [ET.Element('b')]
        self.assertEqual(self._subelem_tags(e), ['a0', 'b', 'a2', 'a3'])
        e[1::-sys.maxsize-1] = [ET.Element('c')]
        self.assertEqual(self._subelem_tags(e), ['a0', 'c', 'a2', 'a3'])
        e[1::-sys.maxsize<<64] = [ET.Element('d')]
        self.assertEqual(self._subelem_tags(e), ['a0', 'd', 'a2', 'a3'])


kundi IOTest(unittest.TestCase):
    eleza test_encoding(self):
        # Test encoding issues.
        elem = ET.Element("tag")
        elem.text = "abc"
        self.assertEqual(serialize(elem), '<tag>abc</tag>')
        kila enc kwenye ("utf-8", "us-ascii"):
            ukijumuisha self.subTest(enc):
                self.assertEqual(serialize(elem, encoding=enc),
                        b'<tag>abc</tag>')
                self.assertEqual(serialize(elem, encoding=enc.upper()),
                        b'<tag>abc</tag>')
        kila enc kwenye ("iso-8859-1", "utf-16", "utf-32"):
            ukijumuisha self.subTest(enc):
                self.assertEqual(serialize(elem, encoding=enc),
                        ("<?xml version='1.0' encoding='%s'?>\n"
                         "<tag>abc</tag>" % enc).encode(enc))
                upper = enc.upper()
                self.assertEqual(serialize(elem, encoding=upper),
                        ("<?xml version='1.0' encoding='%s'?>\n"
                         "<tag>abc</tag>" % upper).encode(enc))

        elem = ET.Element("tag")
        elem.text = "<&\"\'>"
        self.assertEqual(serialize(elem), '<tag>&lt;&amp;"\'&gt;</tag>')
        self.assertEqual(serialize(elem, encoding="utf-8"),
                b'<tag>&lt;&amp;"\'&gt;</tag>')
        self.assertEqual(serialize(elem, encoding="us-ascii"),
                b'<tag>&lt;&amp;"\'&gt;</tag>')
        kila enc kwenye ("iso-8859-1", "utf-16", "utf-32"):
            self.assertEqual(serialize(elem, encoding=enc),
                    ("<?xml version='1.0' encoding='%s'?>\n"
                     "<tag>&lt;&amp;\"'&gt;</tag>" % enc).encode(enc))

        elem = ET.Element("tag")
        elem.attrib["key"] = "<&\"\'>"
        self.assertEqual(serialize(elem), '<tag key="&lt;&amp;&quot;\'&gt;" />')
        self.assertEqual(serialize(elem, encoding="utf-8"),
                b'<tag key="&lt;&amp;&quot;\'&gt;" />')
        self.assertEqual(serialize(elem, encoding="us-ascii"),
                b'<tag key="&lt;&amp;&quot;\'&gt;" />')
        kila enc kwenye ("iso-8859-1", "utf-16", "utf-32"):
            self.assertEqual(serialize(elem, encoding=enc),
                    ("<?xml version='1.0' encoding='%s'?>\n"
                     "<tag key=\"&lt;&amp;&quot;'&gt;\" />" % enc).encode(enc))

        elem = ET.Element("tag")
        elem.text = '\xe5\xf6\xf6<>'
        self.assertEqual(serialize(elem), '<tag>\xe5\xf6\xf6&lt;&gt;</tag>')
        self.assertEqual(serialize(elem, encoding="utf-8"),
                b'<tag>\xc3\xa5\xc3\xb6\xc3\xb6&lt;&gt;</tag>')
        self.assertEqual(serialize(elem, encoding="us-ascii"),
                b'<tag>&#229;&#246;&#246;&lt;&gt;</tag>')
        kila enc kwenye ("iso-8859-1", "utf-16", "utf-32"):
            self.assertEqual(serialize(elem, encoding=enc),
                    ("<?xml version='1.0' encoding='%s'?>\n"
                     "<tag>åöö&lt;&gt;</tag>" % enc).encode(enc))

        elem = ET.Element("tag")
        elem.attrib["key"] = '\xe5\xf6\xf6<>'
        self.assertEqual(serialize(elem), '<tag key="\xe5\xf6\xf6&lt;&gt;" />')
        self.assertEqual(serialize(elem, encoding="utf-8"),
                b'<tag key="\xc3\xa5\xc3\xb6\xc3\xb6&lt;&gt;" />')
        self.assertEqual(serialize(elem, encoding="us-ascii"),
                b'<tag key="&#229;&#246;&#246;&lt;&gt;" />')
        kila enc kwenye ("iso-8859-1", "utf-16", "utf-16le", "utf-16be", "utf-32"):
            self.assertEqual(serialize(elem, encoding=enc),
                    ("<?xml version='1.0' encoding='%s'?>\n"
                     "<tag key=\"åöö&lt;&gt;\" />" % enc).encode(enc))

    eleza test_write_to_filename(self):
        self.addCleanup(support.unlink, TESTFN)
        tree = ET.ElementTree(ET.XML('''<site />'''))
        tree.write(TESTFN)
        ukijumuisha open(TESTFN, 'rb') kama f:
            self.assertEqual(f.read(), b'''<site />''')

    eleza test_write_to_text_file(self):
        self.addCleanup(support.unlink, TESTFN)
        tree = ET.ElementTree(ET.XML('''<site />'''))
        ukijumuisha open(TESTFN, 'w', encoding='utf-8') kama f:
            tree.write(f, encoding='unicode')
            self.assertUongo(f.closed)
        ukijumuisha open(TESTFN, 'rb') kama f:
            self.assertEqual(f.read(), b'''<site />''')

    eleza test_write_to_binary_file(self):
        self.addCleanup(support.unlink, TESTFN)
        tree = ET.ElementTree(ET.XML('''<site />'''))
        ukijumuisha open(TESTFN, 'wb') kama f:
            tree.write(f)
            self.assertUongo(f.closed)
        ukijumuisha open(TESTFN, 'rb') kama f:
            self.assertEqual(f.read(), b'''<site />''')

    eleza test_write_to_binary_file_with_bom(self):
        self.addCleanup(support.unlink, TESTFN)
        tree = ET.ElementTree(ET.XML('''<site />'''))
        # test BOM writing to buffered file
        ukijumuisha open(TESTFN, 'wb') kama f:
            tree.write(f, encoding='utf-16')
            self.assertUongo(f.closed)
        ukijumuisha open(TESTFN, 'rb') kama f:
            self.assertEqual(f.read(),
                    '''<?xml version='1.0' encoding='utf-16'?>\n'''
                    '''<site />'''.encode("utf-16"))
        # test BOM writing to non-buffered file
        ukijumuisha open(TESTFN, 'wb', buffering=0) kama f:
            tree.write(f, encoding='utf-16')
            self.assertUongo(f.closed)
        ukijumuisha open(TESTFN, 'rb') kama f:
            self.assertEqual(f.read(),
                    '''<?xml version='1.0' encoding='utf-16'?>\n'''
                    '''<site />'''.encode("utf-16"))

    eleza test_read_kutoka_stringio(self):
        tree = ET.ElementTree()
        stream = io.StringIO('''<?xml version="1.0"?><site></site>''')
        tree.parse(stream)
        self.assertEqual(tree.getroot().tag, 'site')

    eleza test_write_to_stringio(self):
        tree = ET.ElementTree(ET.XML('''<site />'''))
        stream = io.StringIO()
        tree.write(stream, encoding='unicode')
        self.assertEqual(stream.getvalue(), '''<site />''')

    eleza test_read_kutoka_bytesio(self):
        tree = ET.ElementTree()
        raw = io.BytesIO(b'''<?xml version="1.0"?><site></site>''')
        tree.parse(raw)
        self.assertEqual(tree.getroot().tag, 'site')

    eleza test_write_to_bytesio(self):
        tree = ET.ElementTree(ET.XML('''<site />'''))
        raw = io.BytesIO()
        tree.write(raw)
        self.assertEqual(raw.getvalue(), b'''<site />''')

    kundi dummy:
        pita

    eleza test_read_kutoka_user_text_reader(self):
        stream = io.StringIO('''<?xml version="1.0"?><site></site>''')
        reader = self.dummy()
        reader.read = stream.read
        tree = ET.ElementTree()
        tree.parse(reader)
        self.assertEqual(tree.getroot().tag, 'site')

    eleza test_write_to_user_text_writer(self):
        tree = ET.ElementTree(ET.XML('''<site />'''))
        stream = io.StringIO()
        writer = self.dummy()
        writer.write = stream.write
        tree.write(writer, encoding='unicode')
        self.assertEqual(stream.getvalue(), '''<site />''')

    eleza test_read_kutoka_user_binary_reader(self):
        raw = io.BytesIO(b'''<?xml version="1.0"?><site></site>''')
        reader = self.dummy()
        reader.read = raw.read
        tree = ET.ElementTree()
        tree.parse(reader)
        self.assertEqual(tree.getroot().tag, 'site')
        tree = ET.ElementTree()

    eleza test_write_to_user_binary_writer(self):
        tree = ET.ElementTree(ET.XML('''<site />'''))
        raw = io.BytesIO()
        writer = self.dummy()
        writer.write = raw.write
        tree.write(writer)
        self.assertEqual(raw.getvalue(), b'''<site />''')

    eleza test_write_to_user_binary_writer_with_bom(self):
        tree = ET.ElementTree(ET.XML('''<site />'''))
        raw = io.BytesIO()
        writer = self.dummy()
        writer.write = raw.write
        writer.seekable = lambda: Kweli
        writer.tell = raw.tell
        tree.write(writer, encoding="utf-16")
        self.assertEqual(raw.getvalue(),
                '''<?xml version='1.0' encoding='utf-16'?>\n'''
                '''<site />'''.encode("utf-16"))

    eleza test_tostringlist_invariant(self):
        root = ET.kutokastring('<tag>foo</tag>')
        self.assertEqual(
            ET.tostring(root, 'unicode'),
            ''.join(ET.tostringlist(root, 'unicode')))
        self.assertEqual(
            ET.tostring(root, 'utf-16'),
            b''.join(ET.tostringlist(root, 'utf-16')))

    eleza test_short_empty_elements(self):
        root = ET.kutokastring('<tag>a<x />b<y></y>c</tag>')
        self.assertEqual(
            ET.tostring(root, 'unicode'),
            '<tag>a<x />b<y />c</tag>')
        self.assertEqual(
            ET.tostring(root, 'unicode', short_empty_elements=Kweli),
            '<tag>a<x />b<y />c</tag>')
        self.assertEqual(
            ET.tostring(root, 'unicode', short_empty_elements=Uongo),
            '<tag>a<x></x>b<y></y>c</tag>')


kundi ParseErrorTest(unittest.TestCase):
    eleza test_subclass(self):
        self.assertIsInstance(ET.ParseError(), SyntaxError)

    eleza _get_error(self, s):
        jaribu:
            ET.kutokastring(s)
        tatizo ET.ParseError kama e:
            rudisha e

    eleza test_error_position(self):
        self.assertEqual(self._get_error('foo').position, (1, 0))
        self.assertEqual(self._get_error('<tag>&foo;</tag>').position, (1, 5))
        self.assertEqual(self._get_error('foobar<').position, (1, 6))

    eleza test_error_code(self):
        agiza xml.parsers.expat.errors kama ERRORS
        self.assertEqual(self._get_error('foo').code,
                ERRORS.codes[ERRORS.XML_ERROR_SYNTAX])


kundi KeywordArgsTest(unittest.TestCase):
    # Test various issues ukijumuisha keyword arguments pitaed to ET.Element
    # constructor na methods
    eleza test_issue14818(self):
        x = ET.XML("<a>foo</a>")
        self.assertEqual(x.find('a', Tupu),
                         x.find(path='a', namespaces=Tupu))
        self.assertEqual(x.findtext('a', Tupu, Tupu),
                         x.findtext(path='a', default=Tupu, namespaces=Tupu))
        self.assertEqual(x.findall('a', Tupu),
                         x.findall(path='a', namespaces=Tupu))
        self.assertEqual(list(x.iterfind('a', Tupu)),
                         list(x.iterfind(path='a', namespaces=Tupu)))

        self.assertEqual(ET.Element('a').attrib, {})
        elements = [
            ET.Element('a', dict(href="#", id="foo")),
            ET.Element('a', attrib=dict(href="#", id="foo")),
            ET.Element('a', dict(href="#"), id="foo"),
            ET.Element('a', href="#", id="foo"),
            ET.Element('a', dict(href="#", id="foo"), href="#", id="foo"),
        ]
        kila e kwenye elements:
            self.assertEqual(e.tag, 'a')
            self.assertEqual(e.attrib, dict(href="#", id="foo"))

        e2 = ET.SubElement(elements[0], 'foobar', attrib={'key1': 'value1'})
        self.assertEqual(e2.attrib['key1'], 'value1')

        ukijumuisha self.assertRaisesRegex(TypeError, 'must be dict, sio str'):
            ET.Element('a', "I'm sio a dict")
        ukijumuisha self.assertRaisesRegex(TypeError, 'must be dict, sio str'):
            ET.Element('a', attrib="I'm sio a dict")

# --------------------------------------------------------------------

kundi NoAcceleratorTest(unittest.TestCase):
    eleza setUp(self):
        ikiwa sio pyET:
            ashiria unittest.SkipTest('only kila the Python version')

    # Test that the C accelerator was sio imported kila pyET
    eleza test_correct_import_pyET(self):
        # The type of methods defined kwenye Python code ni types.FunctionType,
        # wakati the type of methods defined inside _elementtree is
        # <kundi 'wrapper_descriptor'>
        self.assertIsInstance(pyET.Element.__init__, types.FunctionType)
        self.assertIsInstance(pyET.XMLParser.__init__, types.FunctionType)


# --------------------------------------------------------------------

eleza c14n_roundtrip(xml, **options):
    rudisha pyET.canonicalize(xml, **options)


kundi C14NTest(unittest.TestCase):
    maxDiff = Tupu

    #
    # simple roundtrip tests (kutoka c14n.py)

    eleza test_simple_roundtrip(self):
        # Basics
        self.assertEqual(c14n_roundtrip("<doc/>"), '<doc></doc>')
        self.assertEqual(c14n_roundtrip("<doc xmlns='uri'/>"), # FIXME
                '<doc xmlns="uri"></doc>')
        self.assertEqual(c14n_roundtrip("<prefix:doc xmlns:prefix='uri'/>"),
            '<prefix:doc xmlns:prefix="uri"></prefix:doc>')
        self.assertEqual(c14n_roundtrip("<doc xmlns:prefix='uri'><prefix:bar/></doc>"),
            '<doc><prefix:bar xmlns:prefix="uri"></prefix:bar></doc>')
        self.assertEqual(c14n_roundtrip("<elem xmlns:wsu='http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd' xmlns:SOAP-ENV='http://schemas.xmlsoap.org/soap/envelope/' />"),
            '<elem></elem>')

        # C14N spec
        self.assertEqual(c14n_roundtrip("<doc>Hello, world!<!-- Comment 1 --></doc>"),
            '<doc>Hello, world!</doc>')
        self.assertEqual(c14n_roundtrip("<value>&#x32;</value>"),
            '<value>2</value>')
        self.assertEqual(c14n_roundtrip('<compute><![CDATA[value>"0" && value<"10" ?"valid":"error"]]></compute>'),
            '<compute>value&gt;"0" &amp;&amp; value&lt;"10" ?"valid":"error"</compute>')
        self.assertEqual(c14n_roundtrip('''<compute expr='value>"0" &amp;&amp; value&lt;"10" ?"valid":"error"'>valid</compute>'''),
            '<compute expr="value>&quot;0&quot; &amp;&amp; value&lt;&quot;10&quot; ?&quot;valid&quot;:&quot;error&quot;">valid</compute>')
        self.assertEqual(c14n_roundtrip("<norm attr=' &apos;   &#x20;&#13;&#xa;&#9;   &apos; '/>"),
            '<norm attr=" \'    &#xD;&#xA;&#x9;   \' "></norm>')
        self.assertEqual(c14n_roundtrip("<normNames attr='   A   &#x20;&#13;&#xa;&#9;   B   '/>"),
            '<normNames attr="   A    &#xD;&#xA;&#x9;   B   "></normNames>')
        self.assertEqual(c14n_roundtrip("<normId id=' &apos;   &#x20;&#13;&#xa;&#9;   &apos; '/>"),
            '<normId id=" \'    &#xD;&#xA;&#x9;   \' "></normId>')

        # fragments kutoka PJ's tests
        #self.assertEqual(c14n_roundtrip("<doc xmlns:x='http://example.com/x' xmlns='http://example.com/default'><b y:a1='1' xmlns='http://example.com/default' a3='3' xmlns:y='http://example.com/y' y:a2='2'/></doc>"),
        #'<doc xmlns:x="http://example.com/x"><b xmlns:y="http://example.com/y" a3="3" y:a1="1" y:a2="2"></b></doc>')

    eleza test_c14n_exclusion(self):
        xml = textwrap.dedent("""\
        <root xmlns:x="http://example.com/x">
            <a x:attr="attrx">
                <b>abtext</b>
            </a>
            <b>btext</b>
            <c>
                <x:d>dtext</x:d>
            </c>
        </root>
        """)
        self.assertEqual(
            c14n_roundtrip(xml, strip_text=Kweli),
            '<root>'
            '<a xmlns:x="http://example.com/x" x:attr="attrx"><b>abtext</b></a>'
            '<b>btext</b>'
            '<c><x:d xmlns:x="http://example.com/x">dtext</x:d></c>'
            '</root>')
        self.assertEqual(
            c14n_roundtrip(xml, strip_text=Kweli, exclude_attrs=['{http://example.com/x}attr']),
            '<root>'
            '<a><b>abtext</b></a>'
            '<b>btext</b>'
            '<c><x:d xmlns:x="http://example.com/x">dtext</x:d></c>'
            '</root>')
        self.assertEqual(
            c14n_roundtrip(xml, strip_text=Kweli, exclude_tags=['{http://example.com/x}d']),
            '<root>'
            '<a xmlns:x="http://example.com/x" x:attr="attrx"><b>abtext</b></a>'
            '<b>btext</b>'
            '<c></c>'
            '</root>')
        self.assertEqual(
            c14n_roundtrip(xml, strip_text=Kweli, exclude_attrs=['{http://example.com/x}attr'],
                           exclude_tags=['{http://example.com/x}d']),
            '<root>'
            '<a><b>abtext</b></a>'
            '<b>btext</b>'
            '<c></c>'
            '</root>')
        self.assertEqual(
            c14n_roundtrip(xml, strip_text=Kweli, exclude_tags=['a', 'b']),
            '<root>'
            '<c><x:d xmlns:x="http://example.com/x">dtext</x:d></c>'
            '</root>')
        self.assertEqual(
            c14n_roundtrip(xml, exclude_tags=['a', 'b']),
            '<root>\n'
            '    \n'
            '    \n'
            '    <c>\n'
            '        <x:d xmlns:x="http://example.com/x">dtext</x:d>\n'
            '    </c>\n'
            '</root>')
        self.assertEqual(
            c14n_roundtrip(xml, strip_text=Kweli, exclude_tags=['{http://example.com/x}d', 'b']),
            '<root>'
            '<a xmlns:x="http://example.com/x" x:attr="attrx"></a>'
            '<c></c>'
            '</root>')
        self.assertEqual(
            c14n_roundtrip(xml, exclude_tags=['{http://example.com/x}d', 'b']),
            '<root>\n'
            '    <a xmlns:x="http://example.com/x" x:attr="attrx">\n'
            '        \n'
            '    </a>\n'
            '    \n'
            '    <c>\n'
            '        \n'
            '    </c>\n'
            '</root>')

    #
    # basic method=c14n tests kutoka the c14n 2.0 specification.  uses
    # test files under xmltestdata/c14n-20.

    # note that this uses generated C14N versions of the standard ET.write
    # output, sio roundtripped C14N (see above).

    eleza test_xml_c14n2(self):
        datadir = findfile("c14n-20", subdir="xmltestdata")
        full_path = partial(os.path.join, datadir)

        files = [filename[:-4] kila filename kwenye sorted(os.listdir(datadir))
                 ikiwa filename.endswith('.xml')]
        input_files = [
            filename kila filename kwenye files
            ikiwa filename.startswith('in')
        ]
        configs = {
            filename: {
                # <c14n2:PrefixRewrite>sequential</c14n2:PrefixRewrite>
                option.tag.split('}')[-1]: ((option.text ama '').strip(), option)
                kila option kwenye ET.parse(full_path(filename) + ".xml").getroot()
            }
            kila filename kwenye files
            ikiwa filename.startswith('c14n')
        }

        tests = {
            input_file: [
                (filename, configs[filename.rsplit('_', 1)[-1]])
                kila filename kwenye files
                ikiwa filename.startswith(f'out_{input_file}_')
                na filename.rsplit('_', 1)[-1] kwenye configs
            ]
            kila input_file kwenye input_files
        }

        # Make sure we found all test cases.
        self.assertEqual(30, len([
            output_file kila output_files kwenye tests.values()
            kila output_file kwenye output_files]))

        eleza get_option(config, option_name, default=Tupu):
            rudisha config.get(option_name, (default, ()))[0]

        kila input_file, output_files kwenye tests.items():
            kila output_file, config kwenye output_files:
                keep_comments = get_option(
                    config, 'IgnoreComments') == 'true'  # no, it's right :)
                strip_text = get_option(
                    config, 'TrimTextNodes') == 'true'
                rewrite_prefixes = get_option(
                    config, 'PrefixRewrite') == 'sequential'
                ikiwa 'QNameAware' kwenye config:
                    qattrs = [
                        f"{{{el.get('NS')}}}{el.get('Name')}"
                        kila el kwenye config['QNameAware'][1].findall(
                            '{http://www.w3.org/2010/xml-c14n2}QualifiedAttr')
                    ]
                    qtags = [
                        f"{{{el.get('NS')}}}{el.get('Name')}"
                        kila el kwenye config['QNameAware'][1].findall(
                            '{http://www.w3.org/2010/xml-c14n2}Element')
                    ]
                isipokua:
                    qtags = qattrs = Tupu

                # Build subtest description kutoka config.
                config_descr = ','.join(
                    f"{name}={value ama ','.join(c.tag.split('}')[-1] kila c kwenye children)}"
                    kila name, (value, children) kwenye sorted(config.items())
                )

                ukijumuisha self.subTest(f"{output_file}({config_descr})"):
                    ikiwa input_file == 'inNsRedecl' na sio rewrite_prefixes:
                        self.skipTest(
                            f"Redeclared namespace handling ni sio supported kwenye {output_file}")
                    ikiwa input_file == 'inNsSuperfluous' na sio rewrite_prefixes:
                        self.skipTest(
                            f"Redeclared namespace handling ni sio supported kwenye {output_file}")
                    ikiwa 'QNameAware' kwenye config na config['QNameAware'][1].find(
                            '{http://www.w3.org/2010/xml-c14n2}XPathElement') ni sio Tupu:
                        self.skipTest(
                            f"QName rewriting kwenye XPath text ni sio supported kwenye {output_file}")

                    f = full_path(input_file + ".xml")
                    ikiwa input_file == 'inC14N5':
                        # Hack: avoid setting up external entity resolution kwenye the parser.
                        ukijumuisha open(full_path('world.txt'), 'rb') kama entity_file:
                            ukijumuisha open(f, 'rb') kama f:
                                f = io.BytesIO(f.read().replace(b'&ent2;', entity_file.read()))

                    text = ET.canonicalize(
                        kutoka_file=f,
                        with_comments=keep_comments,
                        strip_text=strip_text,
                        rewrite_prefixes=rewrite_prefixes,
                        qname_aware_tags=qtags, qname_aware_attrs=qattrs)

                    ukijumuisha open(full_path(output_file + ".xml"), 'r', encoding='utf8') kama f:
                        expected = f.read()
                        ikiwa input_file == 'inC14N3':
                            # FIXME: cET resolves default attributes but ET does not!
                            expected = expected.replace(' attr="default"', '')
                            text = text.replace(' attr="default"', '')
                    self.assertEqual(expected, text)

# --------------------------------------------------------------------


eleza test_main(module=Tupu):
    # When invoked without a module, runs the Python ET tests by loading pyET.
    # Otherwise, uses the given module kama the ET.
    global pyET
    pyET = import_fresh_module('xml.etree.ElementTree',
                               blocked=['_elementtree'])
    ikiwa module ni Tupu:
        module = pyET

    global ET
    ET = module

    test_classes = [
        ModuleTest,
        ElementSlicingTest,
        BasicElementTest,
        BadElementTest,
        BadElementPathTest,
        ElementTreeTest,
        IOTest,
        ParseErrorTest,
        XIncludeTest,
        ElementTreeTypeTest,
        ElementFindTest,
        ElementIterTest,
        TreeBuilderTest,
        XMLParserTest,
        XMLPullParserTest,
        BugsTest,
        KeywordArgsTest,
        C14NTest,
        ]

    # These tests will only run kila the pure-Python version that doesn't agiza
    # _elementtree. We can't use skipUnless here, because pyET ni filled kwenye only
    # after the module ni loaded.
    ikiwa pyET ni sio ET:
        test_classes.extend([
            NoAcceleratorTest,
            ])

    # Provide default namespace mapping na path cache.
    kutoka xml.etree agiza ElementPath
    nsmap = ET.register_namespace._namespace_map
    # Copy the default namespace mapping
    nsmap_copy = nsmap.copy()
    # Copy the path cache (should be empty)
    path_cache = ElementPath._cache
    ElementPath._cache = path_cache.copy()
    # Align the Comment/PI factories.
    ikiwa hasattr(ET, '_set_factories'):
        old_factories = ET._set_factories(ET.Comment, ET.PI)
    isipokua:
        old_factories = Tupu

    jaribu:
        support.run_unittest(*test_classes)
    mwishowe:
        kutoka xml.etree agiza ElementPath
        # Restore mapping na path cache
        nsmap.clear()
        nsmap.update(nsmap_copy)
        ElementPath._cache = path_cache
        ikiwa old_factories ni sio Tupu:
            ET._set_factories(*old_factories)
        # don't interfere ukijumuisha subsequent tests
        ET = pyET = Tupu


ikiwa __name__ == '__main__':
    test_main()
