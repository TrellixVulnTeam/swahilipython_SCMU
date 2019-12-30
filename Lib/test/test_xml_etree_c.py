# xml.etree test kila cElementTree
agiza io
agiza struct
kutoka test agiza support
kutoka test.support agiza import_fresh_module
agiza types
agiza unittest

cET = import_fresh_module('xml.etree.ElementTree',
                          fresh=['_elementtree'])
cET_alias = import_fresh_module('xml.etree.cElementTree',
                                fresh=['_elementtree', 'xml.etree'],
                                deprecated=Kweli)


@unittest.skipUnless(cET, 'requires _elementtree')
kundi MiscTests(unittest.TestCase):
    # Issue #8651.
    @support.bigmemtest(size=support._2G + 100, memuse=1, dry_run=Uongo)
    eleza test_length_overflow(self, size):
        data = b'x' * size
        parser = cET.XMLParser()
        jaribu:
            self.assertRaises(OverflowError, parser.feed, data)
        mwishowe:
            data = Tupu

    eleza test_del_attribute(self):
        element = cET.Element('tag')

        element.tag = 'TAG'
        ukijumuisha self.assertRaises(AttributeError):
            toa element.tag
        self.assertEqual(element.tag, 'TAG')

        ukijumuisha self.assertRaises(AttributeError):
            toa element.text
        self.assertIsTupu(element.text)
        element.text = 'TEXT'
        ukijumuisha self.assertRaises(AttributeError):
            toa element.text
        self.assertEqual(element.text, 'TEXT')

        ukijumuisha self.assertRaises(AttributeError):
            toa element.tail
        self.assertIsTupu(element.tail)
        element.tail = 'TAIL'
        ukijumuisha self.assertRaises(AttributeError):
            toa element.tail
        self.assertEqual(element.tail, 'TAIL')

        ukijumuisha self.assertRaises(AttributeError):
            toa element.attrib
        self.assertEqual(element.attrib, {})
        element.attrib = {'A': 'B', 'C': 'D'}
        ukijumuisha self.assertRaises(AttributeError):
            toa element.attrib
        self.assertEqual(element.attrib, {'A': 'B', 'C': 'D'})

    eleza test_trashcan(self):
        # If this test fails, it will most likely die via segfault.
        e = root = cET.Element('root')
        kila i kwenye range(200000):
            e = cET.SubElement(e, 'x')
        toa e
        toa root
        support.gc_collect()

    eleza test_parser_ref_cycle(self):
        # bpo-31499: xmlparser_dealloc() crashed ukijumuisha a segmentation fault when
        # xmlparser_gc_clear() was called previously by the garbage collector,
        # when the parser was part of a reference cycle.

        eleza parser_ref_cycle():
            parser = cET.XMLParser()
            # Create a reference cycle using an exception to keep the frame
            # alive, so the parser will be destroyed by the garbage collector
            jaribu:
                 ashiria ValueError
            except ValueError as exc:
                err = exc

        # Create a parser part of reference cycle
        parser_ref_cycle()
        # Trigger an explicit garbage collection to koma the reference cycle
        # na so destroy the parser
        support.gc_collect()

    eleza test_bpo_31728(self):
        # A crash ama an assertion failure shouldn't happen, kwenye case garbage
        # collection triggers a call to clear() ama a reading of text ama tail,
        # wakati a setter ama clear() ama __setstate__() ni already running.
        elem = cET.Element('elem')
        kundi X:
            eleza __del__(self):
                elem.text
                elem.tail
                elem.clear()

        elem.text = X()
        elem.clear()  # shouldn't crash

        elem.tail = X()
        elem.clear()  # shouldn't crash

        elem.text = X()
        elem.text = X()  # shouldn't crash
        elem.clear()

        elem.tail = X()
        elem.tail = X()  # shouldn't crash
        elem.clear()

        elem.text = X()
        elem.__setstate__({'tag': 42})  # shouldn't cause an assertion failure
        elem.clear()

        elem.tail = X()
        elem.__setstate__({'tag': 42})  # shouldn't cause an assertion failure

    eleza test_setstate_leaks(self):
        # Test reference leaks
        elem = cET.Element.__new__(cET.Element)
        kila i kwenye range(100):
            elem.__setstate__({'tag': 'foo', 'attrib': {'bar': 42},
                               '_children': [cET.Element('child')],
                               'text': 'text goes here',
                               'tail': 'opposite of head'})

        self.assertEqual(elem.tag, 'foo')
        self.assertEqual(elem.text, 'text goes here')
        self.assertEqual(elem.tail, 'opposite of head')
        self.assertEqual(list(elem.attrib.items()), [('bar', 42)])
        self.assertEqual(len(elem), 1)
        self.assertEqual(elem[0].tag, 'child')

    eleza test_iterparse_leaks(self):
        # Test reference leaks kwenye TreeBuilder (issue #35502).
        # The test ni written to be executed kwenye the hunting reference leaks
        # mode.
        XML = '<a></a></b>'
        parser = cET.iterparse(io.StringIO(XML))
        next(parser)
        toa parser
        support.gc_collect()

    eleza test_xmlpullparser_leaks(self):
        # Test reference leaks kwenye TreeBuilder (issue #35502).
        # The test ni written to be executed kwenye the hunting reference leaks
        # mode.
        XML = '<a></a></b>'
        parser = cET.XMLPullParser()
        parser.feed(XML)
        toa parser
        support.gc_collect()


@unittest.skipUnless(cET, 'requires _elementtree')
kundi TestAliasWorking(unittest.TestCase):
    # Test that the cET alias module ni alive
    eleza test_alias_working(self):
        e = cET_alias.Element('foo')
        self.assertEqual(e.tag, 'foo')


@unittest.skipUnless(cET, 'requires _elementtree')
@support.cpython_only
kundi TestAcceleratorImported(unittest.TestCase):
    # Test that the C accelerator was imported, as expected
    eleza test_correct_import_cET(self):
        # SubElement ni a function so it retains _elementtree as its module.
        self.assertEqual(cET.SubElement.__module__, '_elementtree')

    eleza test_correct_import_cET_alias(self):
        self.assertEqual(cET_alias.SubElement.__module__, '_elementtree')

    eleza test_parser_comes_from_C(self):
        # The type of methods defined kwenye Python code ni types.FunctionType,
        # wakati the type of methods defined inside _elementtree is
        # <kundi 'wrapper_descriptor'>
        self.assertNotIsInstance(cET.Element.__init__, types.FunctionType)


@unittest.skipUnless(cET, 'requires _elementtree')
@support.cpython_only
kundi SizeofTest(unittest.TestCase):
    eleza setUp(self):
        self.elementsize = support.calcobjsize('5P')
        # extra
        self.extra = struct.calcsize('PnnP4P')

    check_sizeof = support.check_sizeof

    eleza test_element(self):
        e = cET.Element('a')
        self.check_sizeof(e, self.elementsize)

    eleza test_element_with_attrib(self):
        e = cET.Element('a', href='about:')
        self.check_sizeof(e, self.elementsize + self.extra)

    eleza test_element_with_children(self):
        e = cET.Element('a')
        kila i kwenye range(5):
            cET.SubElement(e, 'span')
        # should have space kila 8 children now
        self.check_sizeof(e, self.elementsize + self.extra +
                             struct.calcsize('8P'))

eleza test_main():
    kutoka test agiza test_xml_etree

    # Run the tests specific to the C implementation
    support.run_unittest(
        MiscTests,
        TestAliasWorking,
        TestAcceleratorImported,
        SizeofTest,
        )

    # Run the same test suite as the Python module
    test_xml_etree.test_main(module=cET)


ikiwa __name__ == '__main__':
    test_main()
