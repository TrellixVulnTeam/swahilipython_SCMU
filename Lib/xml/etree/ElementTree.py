"""Lightweight XML support kila Python.

 XML ni an inherently hierarchical data format, na the most natural way to
 represent it ni ukijumuisha a tree.  This module has two classes kila this purpose:

    1. ElementTree represents the whole XML document kama a tree na

    2. Element represents a single node kwenye this tree.

 Interactions ukijumuisha the whole document (reading na writing to/kutoka files) are
 usually done on the ElementTree level.  Interactions ukijumuisha a single XML element
 na its sub-elements are done on the Element level.

 Element ni a flexible container object designed to store hierarchical data
 structures kwenye memory. It can be described kama a cross between a list na a
 dictionary.  Each Element has a number of properties associated ukijumuisha it:

    'tag' - a string containing the element's name.

    'attributes' - a Python dictionary storing the element's attributes.

    'text' - a string containing the element's text content.

    'tail' - an optional string containing text after the element's end tag.

    And a number of child elements stored kwenye a Python sequence.

 To create an element instance, use the Element constructor,
 ama the SubElement factory function.

 You can also use the ElementTree kundi to wrap an element structure
 na convert it to na kutoka XML.

"""

#---------------------------------------------------------------------
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license kila licensing details.
#
# ElementTree
# Copyright (c) 1999-2008 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
# --------------------------------------------------------------------
# The ElementTree toolkit is
#
# Copyright (c) 1999-2008 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# na will comply ukijumuisha the following terms na conditions:
#
# Permission to use, copy, modify, na distribute this software na
# its associated documentation kila any purpose na without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, na that both that copyright notice na this permission
# notice appear kwenye supporting documentation, na that the name of
# Secret Labs AB ama the author sio be used kwenye advertising ama publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

__all__ = [
    # public symbols
    "Comment",
    "dump",
    "Element", "ElementTree",
    "fromstring", "fromstringlist",
    "iselement", "iterparse",
    "parse", "ParseError",
    "PI", "ProcessingInstruction",
    "QName",
    "SubElement",
    "tostring", "tostringlist",
    "TreeBuilder",
    "VERSION",
    "XML", "XMLID",
    "XMLParser", "XMLPullParser",
    "register_namespace",
    "canonicalize", "C14NWriterTarget",
    ]

VERSION = "1.3.0"

agiza sys
agiza re
agiza warnings
agiza io
agiza collections
agiza collections.abc
agiza contextlib

kutoka . agiza ElementPath


kundi ParseError(SyntaxError):
    """An error when parsing an XML document.

    In addition to its exception value, a ParseError contains
    two extra attributes:
        'code'     - the specific exception code
        'position' - the line na column of the error

    """
    pita

# --------------------------------------------------------------------


eleza iselement(element):
    """Return Kweli ikiwa *element* appears to be an Element."""
    rudisha hasattr(element, 'tag')


kundi Element:
    """An XML element.

    This kundi ni the reference implementation of the Element interface.

    An element's length ni its number of subelements.  That means ikiwa you
    want to check ikiwa an element ni truly empty, you should check BOTH
    its length AND its text attribute.

    The element tag, attribute names, na attribute values can be either
    bytes ama strings.

    *tag* ni the element name.  *attrib* ni an optional dictionary containing
    element attributes. *extra* are additional element attributes given as
    keyword arguments.

    Example form:
        <tag attrib>text<child/>...</tag>tail

    """

    tag = Tupu
    """The element's name."""

    attrib = Tupu
    """Dictionary of the element's attributes."""

    text = Tupu
    """
    Text before first subelement. This ni either a string ama the value Tupu.
    Note that ikiwa there ni no text, this attribute may be either
    Tupu ama the empty string, depending on the parser.

    """

    tail = Tupu
    """
    Text after this element's end tag, but before the next sibling element's
    start tag.  This ni either a string ama the value Tupu.  Note that ikiwa there
    was no text, this attribute may be either Tupu ama an empty string,
    depending on the parser.

    """

    eleza __init__(self, tag, attrib={}, **extra):
        ikiwa sio isinstance(attrib, dict):
            ashiria TypeError("attrib must be dict, sio %s" % (
                attrib.__class__.__name__,))
        self.tag = tag
        self.attrib = {**attrib, **extra}
        self._children = []

    eleza __repr__(self):
        rudisha "<%s %r at %#x>" % (self.__class__.__name__, self.tag, id(self))

    eleza makeelement(self, tag, attrib):
        """Create a new element ukijumuisha the same type.

        *tag* ni a string containing the element name.
        *attrib* ni a dictionary containing the element attributes.

        Do sio call this method, use the SubElement factory function instead.

        """
        rudisha self.__class__(tag, attrib)

    eleza copy(self):
        """Return copy of current element.

        This creates a shallow copy. Subelements will be shared ukijumuisha the
        original tree.

        """
        elem = self.makeelement(self.tag, self.attrib)
        elem.text = self.text
        elem.tail = self.tail
        elem[:] = self
        rudisha elem

    eleza __len__(self):
        rudisha len(self._children)

    eleza __bool__(self):
        warnings.warn(
            "The behavior of this method will change kwenye future versions.  "
            "Use specific 'len(elem)' ama 'elem ni sio Tupu' test instead.",
            FutureWarning, stacklevel=2
            )
        rudisha len(self._children) != 0 # emulate old behaviour, kila now

    eleza __getitem__(self, index):
        rudisha self._children[index]

    eleza __setitem__(self, index, element):
        ikiwa isinstance(index, slice):
            kila elt kwenye element:
                self._assert_is_element(elt)
        isipokua:
            self._assert_is_element(element)
        self._children[index] = element

    eleza __delitem__(self, index):
        toa self._children[index]

    eleza append(self, subelement):
        """Add *subelement* to the end of this element.

        The new element will appear kwenye document order after the last existing
        subelement (or directly after the text, ikiwa it's the first subelement),
        but before the end tag kila this element.

        """
        self._assert_is_element(subelement)
        self._children.append(subelement)

    eleza extend(self, elements):
        """Append subelements kutoka a sequence.

        *elements* ni a sequence ukijumuisha zero ama more elements.

        """
        kila element kwenye elements:
            self._assert_is_element(element)
        self._children.extend(elements)

    eleza insert(self, index, subelement):
        """Insert *subelement* at position *index*."""
        self._assert_is_element(subelement)
        self._children.insert(index, subelement)

    eleza _assert_is_element(self, e):
        # Need to refer to the actual Python implementation, sio the
        # shadowing C implementation.
        ikiwa sio isinstance(e, _Element_Py):
            ashiria TypeError('expected an Element, sio %s' % type(e).__name__)

    eleza remove(self, subelement):
        """Remove matching subelement.

        Unlike the find methods, this method compares elements based on
        identity, NOT ON tag value ama contents.  To remove subelements by
        other means, the easiest way ni to use a list comprehension to
        select what elements to keep, na then use slice assignment to update
        the parent element.

        ValueError ni raised ikiwa a matching element could sio be found.

        """
        # assert iselement(element)
        self._children.remove(subelement)

    eleza getchildren(self):
        """(Deprecated) Return all subelements.

        Elements are returned kwenye document order.

        """
        warnings.warn(
            "This method will be removed kwenye future versions.  "
            "Use 'list(elem)' ama iteration over elem instead.",
            DeprecationWarning, stacklevel=2
            )
        rudisha self._children

    eleza find(self, path, namespaces=Tupu):
        """Find first matching element by tag name ama path.

        *path* ni a string having either an element tag ama an XPath,
        *namespaces* ni an optional mapping kutoka namespace prefix to full name.

        Return the first matching element, ama Tupu ikiwa no element was found.

        """
        rudisha ElementPath.find(self, path, namespaces)

    eleza findtext(self, path, default=Tupu, namespaces=Tupu):
        """Find text kila first matching element by tag name ama path.

        *path* ni a string having either an element tag ama an XPath,
        *default* ni the value to rudisha ikiwa the element was sio found,
        *namespaces* ni an optional mapping kutoka namespace prefix to full name.

        Return text content of first matching element, ama default value if
        none was found.  Note that ikiwa an element ni found having no text
        content, the empty string ni returned.

        """
        rudisha ElementPath.findtext(self, path, default, namespaces)

    eleza findall(self, path, namespaces=Tupu):
        """Find all matching subelements by tag name ama path.

        *path* ni a string having either an element tag ama an XPath,
        *namespaces* ni an optional mapping kutoka namespace prefix to full name.

        Returns list containing all matching elements kwenye document order.

        """
        rudisha ElementPath.findall(self, path, namespaces)

    eleza iterfind(self, path, namespaces=Tupu):
        """Find all matching subelements by tag name ama path.

        *path* ni a string having either an element tag ama an XPath,
        *namespaces* ni an optional mapping kutoka namespace prefix to full name.

        Return an iterable tumaing all matching elements kwenye document order.

        """
        rudisha ElementPath.iterfind(self, path, namespaces)

    eleza clear(self):
        """Reset element.

        This function removes all subelements, clears all attributes, na sets
        the text na tail attributes to Tupu.

        """
        self.attrib.clear()
        self._children = []
        self.text = self.tail = Tupu

    eleza get(self, key, default=Tupu):
        """Get element attribute.

        Equivalent to attrib.get, but some implementations may handle this a
        bit more efficiently.  *key* ni what attribute to look for, na
        *default* ni what to rudisha ikiwa the attribute was sio found.

        Returns a string containing the attribute value, ama the default if
        attribute was sio found.

        """
        rudisha self.attrib.get(key, default)

    eleza set(self, key, value):
        """Set element attribute.

        Equivalent to attrib[key] = value, but some implementations may handle
        this a bit more efficiently.  *key* ni what attribute to set, na
        *value* ni the attribute value to set it to.

        """
        self.attrib[key] = value

    eleza keys(self):
        """Get list of attribute names.

        Names are returned kwenye an arbitrary order, just like an ordinary
        Python dict.  Equivalent to attrib.keys()

        """
        rudisha self.attrib.keys()

    eleza items(self):
        """Get element attributes kama a sequence.

        The attributes are returned kwenye arbitrary order.  Equivalent to
        attrib.items().

        Return a list of (name, value) tuples.

        """
        rudisha self.attrib.items()

    eleza iter(self, tag=Tupu):
        """Create tree iterator.

        The iterator loops over the element na all subelements kwenye document
        order, returning all elements ukijumuisha a matching tag.

        If the tree structure ni modified during iteration, new ama removed
        elements may ama may sio be included.  To get a stable set, use the
        list() function on the iterator, na loop over the resulting list.

        *tag* ni what tags to look kila (default ni to rudisha all elements)

        Return an iterator containing all the matching elements.

        """
        ikiwa tag == "*":
            tag = Tupu
        ikiwa tag ni Tupu ama self.tag == tag:
            tuma self
        kila e kwenye self._children:
            tuma kutoka e.iter(tag)

    # compatibility
    eleza getiterator(self, tag=Tupu):
        warnings.warn(
            "This method will be removed kwenye future versions.  "
            "Use 'elem.iter()' ama 'list(elem.iter())' instead.",
            DeprecationWarning, stacklevel=2
        )
        rudisha list(self.iter(tag))

    eleza itertext(self):
        """Create text iterator.

        The iterator loops over the element na all subelements kwenye document
        order, returning all inner text.

        """
        tag = self.tag
        ikiwa sio isinstance(tag, str) na tag ni sio Tupu:
            return
        t = self.text
        ikiwa t:
            tuma t
        kila e kwenye self:
            tuma kutoka e.itertext()
            t = e.tail
            ikiwa t:
                tuma t


eleza SubElement(parent, tag, attrib={}, **extra):
    """Subelement factory which creates an element instance, na appends it
    to an existing parent.

    The element tag, attribute names, na attribute values can be either
    bytes ama Unicode strings.

    *parent* ni the parent element, *tag* ni the subelements name, *attrib* is
    an optional directory containing element attributes, *extra* are
    additional attributes given kama keyword arguments.

    """
    attrib = {**attrib, **extra}
    element = parent.makeelement(tag, attrib)
    parent.append(element)
    rudisha element


eleza Comment(text=Tupu):
    """Comment element factory.

    This function creates a special element which the standard serializer
    serializes kama an XML comment.

    *text* ni a string containing the comment string.

    """
    element = Element(Comment)
    element.text = text
    rudisha element


eleza ProcessingInstruction(target, text=Tupu):
    """Processing Instruction element factory.

    This function creates a special element which the standard serializer
    serializes kama an XML comment.

    *target* ni a string containing the processing instruction, *text* ni a
    string containing the processing instruction contents, ikiwa any.

    """
    element = Element(ProcessingInstruction)
    element.text = target
    ikiwa text:
        element.text = element.text + " " + text
    rudisha element

PI = ProcessingInstruction


kundi QName:
    """Qualified name wrapper.

    This kundi can be used to wrap a QName attribute value kwenye order to get
    proper namespace handing on output.

    *text_or_uri* ni a string containing the QName value either kwenye the form
    {uri}local, ama ikiwa the tag argument ni given, the URI part of a QName.

    *tag* ni an optional argument which ikiwa given, will make the first
    argument (text_or_uri) be interpreted kama a URI, na this argument (tag)
    be interpreted kama a local name.

    """
    eleza __init__(self, text_or_uri, tag=Tupu):
        ikiwa tag:
            text_or_uri = "{%s}%s" % (text_or_uri, tag)
        self.text = text_or_uri
    eleza __str__(self):
        rudisha self.text
    eleza __repr__(self):
        rudisha '<%s %r>' % (self.__class__.__name__, self.text)
    eleza __hash__(self):
        rudisha hash(self.text)
    eleza __le__(self, other):
        ikiwa isinstance(other, QName):
            rudisha self.text <= other.text
        rudisha self.text <= other
    eleza __lt__(self, other):
        ikiwa isinstance(other, QName):
            rudisha self.text < other.text
        rudisha self.text < other
    eleza __ge__(self, other):
        ikiwa isinstance(other, QName):
            rudisha self.text >= other.text
        rudisha self.text >= other
    eleza __gt__(self, other):
        ikiwa isinstance(other, QName):
            rudisha self.text > other.text
        rudisha self.text > other
    eleza __eq__(self, other):
        ikiwa isinstance(other, QName):
            rudisha self.text == other.text
        rudisha self.text == other

# --------------------------------------------------------------------


kundi ElementTree:
    """An XML element hierarchy.

    This kundi also provides support kila serialization to na from
    standard XML.

    *element* ni an optional root element node,
    *file* ni an optional file handle ama file name of an XML file whose
    contents will be used to initialize the tree with.

    """
    eleza __init__(self, element=Tupu, file=Tupu):
        # assert element ni Tupu ama iselement(element)
        self._root = element # first node
        ikiwa file:
            self.parse(file)

    eleza getroot(self):
        """Return root element of this tree."""
        rudisha self._root

    eleza _setroot(self, element):
        """Replace root element of this tree.

        This will discard the current contents of the tree na replace it
        ukijumuisha the given element.  Use ukijumuisha care!

        """
        # assert iselement(element)
        self._root = element

    eleza parse(self, source, parser=Tupu):
        """Load external XML document into element tree.

        *source* ni a file name ama file object, *parser* ni an optional parser
        instance that defaults to XMLParser.

        ParseError ni raised ikiwa the parser fails to parse the document.

        Returns the root element of the given source document.

        """
        close_source = Uongo
        ikiwa sio hasattr(source, "read"):
            source = open(source, "rb")
            close_source = Kweli
        jaribu:
            ikiwa parser ni Tupu:
                # If no parser was specified, create a default XMLParser
                parser = XMLParser()
                ikiwa hasattr(parser, '_parse_whole'):
                    # The default XMLParser, when it comes kutoka an accelerator,
                    # can define an internal _parse_whole API kila efficiency.
                    # It can be used to parse the whole source without feeding
                    # it ukijumuisha chunks.
                    self._root = parser._parse_whole(source)
                    rudisha self._root
            wakati Kweli:
                data = source.read(65536)
                ikiwa sio data:
                    koma
                parser.feed(data)
            self._root = parser.close()
            rudisha self._root
        mwishowe:
            ikiwa close_source:
                source.close()

    eleza iter(self, tag=Tupu):
        """Create na rudisha tree iterator kila the root element.

        The iterator loops over all elements kwenye this tree, kwenye document order.

        *tag* ni a string ukijumuisha the tag name to iterate over
        (default ni to rudisha all elements).

        """
        # assert self._root ni sio Tupu
        rudisha self._root.iter(tag)

    # compatibility
    eleza getiterator(self, tag=Tupu):
        warnings.warn(
            "This method will be removed kwenye future versions.  "
            "Use 'tree.iter()' ama 'list(tree.iter())' instead.",
            DeprecationWarning, stacklevel=2
        )
        rudisha list(self.iter(tag))

    eleza find(self, path, namespaces=Tupu):
        """Find first matching element by tag name ama path.

        Same kama getroot().find(path), which ni Element.find()

        *path* ni a string having either an element tag ama an XPath,
        *namespaces* ni an optional mapping kutoka namespace prefix to full name.

        Return the first matching element, ama Tupu ikiwa no element was found.

        """
        # assert self._root ni sio Tupu
        ikiwa path[:1] == "/":
            path = "." + path
            warnings.warn(
                "This search ni broken kwenye 1.3 na earlier, na will be "
                "fixed kwenye a future version.  If you rely on the current "
                "behaviour, change it to %r" % path,
                FutureWarning, stacklevel=2
                )
        rudisha self._root.find(path, namespaces)

    eleza findtext(self, path, default=Tupu, namespaces=Tupu):
        """Find first matching element by tag name ama path.

        Same kama getroot().findtext(path),  which ni Element.findtext()

        *path* ni a string having either an element tag ama an XPath,
        *namespaces* ni an optional mapping kutoka namespace prefix to full name.

        Return the first matching element, ama Tupu ikiwa no element was found.

        """
        # assert self._root ni sio Tupu
        ikiwa path[:1] == "/":
            path = "." + path
            warnings.warn(
                "This search ni broken kwenye 1.3 na earlier, na will be "
                "fixed kwenye a future version.  If you rely on the current "
                "behaviour, change it to %r" % path,
                FutureWarning, stacklevel=2
                )
        rudisha self._root.findtext(path, default, namespaces)

    eleza findall(self, path, namespaces=Tupu):
        """Find all matching subelements by tag name ama path.

        Same kama getroot().findall(path), which ni Element.findall().

        *path* ni a string having either an element tag ama an XPath,
        *namespaces* ni an optional mapping kutoka namespace prefix to full name.

        Return list containing all matching elements kwenye document order.

        """
        # assert self._root ni sio Tupu
        ikiwa path[:1] == "/":
            path = "." + path
            warnings.warn(
                "This search ni broken kwenye 1.3 na earlier, na will be "
                "fixed kwenye a future version.  If you rely on the current "
                "behaviour, change it to %r" % path,
                FutureWarning, stacklevel=2
                )
        rudisha self._root.findall(path, namespaces)

    eleza iterfind(self, path, namespaces=Tupu):
        """Find all matching subelements by tag name ama path.

        Same kama getroot().iterfind(path), which ni element.iterfind()

        *path* ni a string having either an element tag ama an XPath,
        *namespaces* ni an optional mapping kutoka namespace prefix to full name.

        Return an iterable tumaing all matching elements kwenye document order.

        """
        # assert self._root ni sio Tupu
        ikiwa path[:1] == "/":
            path = "." + path
            warnings.warn(
                "This search ni broken kwenye 1.3 na earlier, na will be "
                "fixed kwenye a future version.  If you rely on the current "
                "behaviour, change it to %r" % path,
                FutureWarning, stacklevel=2
                )
        rudisha self._root.iterfind(path, namespaces)

    eleza write(self, file_or_filename,
              encoding=Tupu,
              xml_declaration=Tupu,
              default_namespace=Tupu,
              method=Tupu, *,
              short_empty_elements=Kweli):
        """Write element tree to a file kama XML.

        Arguments:
          *file_or_filename* -- file name ama a file object opened kila writing

          *encoding* -- the output encoding (default: US-ASCII)

          *xml_declaration* -- bool indicating ikiwa an XML declaration should be
                               added to the output. If Tupu, an XML declaration
                               ni added ikiwa encoding IS NOT either of:
                               US-ASCII, UTF-8, ama Unicode

          *default_namespace* -- sets the default XML namespace (kila "xmlns")

          *method* -- either "xml" (default), "html, "text", ama "c14n"

          *short_empty_elements* -- controls the formatting of elements
                                    that contain no content. If Kweli (default)
                                    they are emitted kama a single self-closed
                                    tag, otherwise they are emitted kama a pair
                                    of start/end tags

        """
        ikiwa sio method:
            method = "xml"
        lasivyo method haiko kwenye _serialize:
            ashiria ValueError("unknown method %r" % method)
        ikiwa sio encoding:
            ikiwa method == "c14n":
                encoding = "utf-8"
            isipokua:
                encoding = "us-ascii"
        enc_lower = encoding.lower()
        ukijumuisha _get_writer(file_or_filename, enc_lower) kama write:
            ikiwa method == "xml" na (xml_declaration ama
                    (xml_declaration ni Tupu na
                     enc_lower haiko kwenye ("utf-8", "us-ascii", "unicode"))):
                declared_encoding = encoding
                ikiwa enc_lower == "unicode":
                    # Retrieve the default encoding kila the xml declaration
                    agiza locale
                    declared_encoding = locale.getpreferredencoding()
                write("<?xml version='1.0' encoding='%s'?>\n" % (
                    declared_encoding,))
            ikiwa method == "text":
                _serialize_text(write, self._root)
            isipokua:
                qnames, namespaces = _namespaces(self._root, default_namespace)
                serialize = _serialize[method]
                serialize(write, self._root, qnames, namespaces,
                          short_empty_elements=short_empty_elements)

    eleza write_c14n(self, file):
        # lxml.etree compatibility.  use output method instead
        rudisha self.write(file, method="c14n")

# --------------------------------------------------------------------
# serialization support

@contextlib.contextmanager
eleza _get_writer(file_or_filename, encoding):
    # returns text write method na release all resources after using
    jaribu:
        write = file_or_filename.write
    tatizo AttributeError:
        # file_or_filename ni a file name
        ikiwa encoding == "unicode":
            file = open(file_or_filename, "w")
        isipokua:
            file = open(file_or_filename, "w", encoding=encoding,
                        errors="xmlcharrefreplace")
        ukijumuisha file:
            tuma file.write
    isipokua:
        # file_or_filename ni a file-like object
        # encoding determines ikiwa it ni a text ama binary writer
        ikiwa encoding == "unicode":
            # use a text writer kama is
            tuma write
        isipokua:
            # wrap a binary writer ukijumuisha TextIOWrapper
            ukijumuisha contextlib.ExitStack() kama stack:
                ikiwa isinstance(file_or_filename, io.BufferedIOBase):
                    file = file_or_filename
                lasivyo isinstance(file_or_filename, io.RawIOBase):
                    file = io.BufferedWriter(file_or_filename)
                    # Keep the original file open when the BufferedWriter is
                    # destroyed
                    stack.callback(file.detach)
                isipokua:
                    # This ni to handle pitaed objects that aren't kwenye the
                    # IOBase hierarchy, but just have a write method
                    file = io.BufferedIOBase()
                    file.writable = lambda: Kweli
                    file.write = write
                    jaribu:
                        # TextIOWrapper uses this methods to determine
                        # ikiwa BOM (kila UTF-16, etc) should be added
                        file.seekable = file_or_filename.seekable
                        file.tell = file_or_filename.tell
                    tatizo AttributeError:
                        pita
                file = io.TextIOWrapper(file,
                                        encoding=encoding,
                                        errors="xmlcharrefreplace",
                                        newline="\n")
                # Keep the original file open when the TextIOWrapper is
                # destroyed
                stack.callback(file.detach)
                tuma file.write

eleza _namespaces(elem, default_namespace=Tupu):
    # identify namespaces used kwenye this tree

    # maps qnames to *encoded* prefix:local names
    qnames = {Tupu: Tupu}

    # maps uri:s to prefixes
    namespaces = {}
    ikiwa default_namespace:
        namespaces[default_namespace] = ""

    eleza add_qname(qname):
        # calculate serialized qname representation
        jaribu:
            ikiwa qname[:1] == "{":
                uri, tag = qname[1:].rsplit("}", 1)
                prefix = namespaces.get(uri)
                ikiwa prefix ni Tupu:
                    prefix = _namespace_map.get(uri)
                    ikiwa prefix ni Tupu:
                        prefix = "ns%d" % len(namespaces)
                    ikiwa prefix != "xml":
                        namespaces[uri] = prefix
                ikiwa prefix:
                    qnames[qname] = "%s:%s" % (prefix, tag)
                isipokua:
                    qnames[qname] = tag # default element
            isipokua:
                ikiwa default_namespace:
                    # FIXME: can this be handled kwenye XML 1.0?
                    ashiria ValueError(
                        "cannot use non-qualified names ukijumuisha "
                        "default_namespace option"
                        )
                qnames[qname] = qname
        tatizo TypeError:
            _raise_serialization_error(qname)

    # populate qname na namespaces table
    kila elem kwenye elem.iter():
        tag = elem.tag
        ikiwa isinstance(tag, QName):
            ikiwa tag.text haiko kwenye qnames:
                add_qname(tag.text)
        lasivyo isinstance(tag, str):
            ikiwa tag haiko kwenye qnames:
                add_qname(tag)
        lasivyo tag ni sio Tupu na tag ni sio Comment na tag ni sio PI:
            _raise_serialization_error(tag)
        kila key, value kwenye elem.items():
            ikiwa isinstance(key, QName):
                key = key.text
            ikiwa key haiko kwenye qnames:
                add_qname(key)
            ikiwa isinstance(value, QName) na value.text haiko kwenye qnames:
                add_qname(value.text)
        text = elem.text
        ikiwa isinstance(text, QName) na text.text haiko kwenye qnames:
            add_qname(text.text)
    rudisha qnames, namespaces

eleza _serialize_xml(write, elem, qnames, namespaces,
                   short_empty_elements, **kwargs):
    tag = elem.tag
    text = elem.text
    ikiwa tag ni Comment:
        write("<!--%s-->" % text)
    lasivyo tag ni ProcessingInstruction:
        write("<?%s?>" % text)
    isipokua:
        tag = qnames[tag]
        ikiwa tag ni Tupu:
            ikiwa text:
                write(_escape_cdata(text))
            kila e kwenye elem:
                _serialize_xml(write, e, qnames, Tupu,
                               short_empty_elements=short_empty_elements)
        isipokua:
            write("<" + tag)
            items = list(elem.items())
            ikiwa items ama namespaces:
                ikiwa namespaces:
                    kila v, k kwenye sorted(namespaces.items(),
                                       key=lambda x: x[1]):  # sort on prefix
                        ikiwa k:
                            k = ":" + k
                        write(" xmlns%s=\"%s\"" % (
                            k,
                            _escape_attrib(v)
                            ))
                kila k, v kwenye items:
                    ikiwa isinstance(k, QName):
                        k = k.text
                    ikiwa isinstance(v, QName):
                        v = qnames[v.text]
                    isipokua:
                        v = _escape_attrib(v)
                    write(" %s=\"%s\"" % (qnames[k], v))
            ikiwa text ama len(elem) ama sio short_empty_elements:
                write(">")
                ikiwa text:
                    write(_escape_cdata(text))
                kila e kwenye elem:
                    _serialize_xml(write, e, qnames, Tupu,
                                   short_empty_elements=short_empty_elements)
                write("</" + tag + ">")
            isipokua:
                write(" />")
    ikiwa elem.tail:
        write(_escape_cdata(elem.tail))

HTML_EMPTY = ("area", "base", "basefont", "br", "col", "frame", "hr",
              "img", "input", "isindex", "link", "meta", "param")

jaribu:
    HTML_EMPTY = set(HTML_EMPTY)
tatizo NameError:
    pita

eleza _serialize_html(write, elem, qnames, namespaces, **kwargs):
    tag = elem.tag
    text = elem.text
    ikiwa tag ni Comment:
        write("<!--%s-->" % _escape_cdata(text))
    lasivyo tag ni ProcessingInstruction:
        write("<?%s?>" % _escape_cdata(text))
    isipokua:
        tag = qnames[tag]
        ikiwa tag ni Tupu:
            ikiwa text:
                write(_escape_cdata(text))
            kila e kwenye elem:
                _serialize_html(write, e, qnames, Tupu)
        isipokua:
            write("<" + tag)
            items = list(elem.items())
            ikiwa items ama namespaces:
                ikiwa namespaces:
                    kila v, k kwenye sorted(namespaces.items(),
                                       key=lambda x: x[1]):  # sort on prefix
                        ikiwa k:
                            k = ":" + k
                        write(" xmlns%s=\"%s\"" % (
                            k,
                            _escape_attrib(v)
                            ))
                kila k, v kwenye items:
                    ikiwa isinstance(k, QName):
                        k = k.text
                    ikiwa isinstance(v, QName):
                        v = qnames[v.text]
                    isipokua:
                        v = _escape_attrib_html(v)
                    # FIXME: handle boolean attributes
                    write(" %s=\"%s\"" % (qnames[k], v))
            write(">")
            ltag = tag.lower()
            ikiwa text:
                ikiwa ltag == "script" ama ltag == "style":
                    write(text)
                isipokua:
                    write(_escape_cdata(text))
            kila e kwenye elem:
                _serialize_html(write, e, qnames, Tupu)
            ikiwa ltag haiko kwenye HTML_EMPTY:
                write("</" + tag + ">")
    ikiwa elem.tail:
        write(_escape_cdata(elem.tail))

eleza _serialize_text(write, elem):
    kila part kwenye elem.itertext():
        write(part)
    ikiwa elem.tail:
        write(elem.tail)

_serialize = {
    "xml": _serialize_xml,
    "html": _serialize_html,
    "text": _serialize_text,
# this optional method ni imported at the end of the module
#   "c14n": _serialize_c14n,
}


eleza register_namespace(prefix, uri):
    """Register a namespace prefix.

    The registry ni global, na any existing mapping kila either the
    given prefix ama the namespace URI will be removed.

    *prefix* ni the namespace prefix, *uri* ni a namespace uri. Tags na
    attributes kwenye this namespace will be serialized ukijumuisha prefix ikiwa possible.

    ValueError ni raised ikiwa prefix ni reserved ama ni invalid.

    """
    ikiwa re.match(r"ns\d+$", prefix):
        ashiria ValueError("Prefix format reserved kila internal use")
    kila k, v kwenye list(_namespace_map.items()):
        ikiwa k == uri ama v == prefix:
            toa _namespace_map[k]
    _namespace_map[uri] = prefix

_namespace_map = {
    # "well-known" namespace prefixes
    "http://www.w3.org/XML/1998/namespace": "xml",
    "http://www.w3.org/1999/xhtml": "html",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
    "http://schemas.xmlsoap.org/wsdl/": "wsdl",
    # xml schema
    "http://www.w3.org/2001/XMLSchema": "xs",
    "http://www.w3.org/2001/XMLSchema-instance": "xsi",
    # dublin core
    "http://purl.org/dc/elements/1.1/": "dc",
}
# For tests na troubleshooting
register_namespace._namespace_map = _namespace_map

eleza _raise_serialization_error(text):
    ashiria TypeError(
        "cannot serialize %r (type %s)" % (text, type(text).__name__)
        )

eleza _escape_cdata(text):
    # escape character data
    jaribu:
        # it's worth avoiding do-nothing calls kila strings that are
        # shorter than 500 characters, ama so.  assume that's, by far,
        # the most common case kwenye most applications.
        ikiwa "&" kwenye text:
            text = text.replace("&", "&amp;")
        ikiwa "<" kwenye text:
            text = text.replace("<", "&lt;")
        ikiwa ">" kwenye text:
            text = text.replace(">", "&gt;")
        rudisha text
    tatizo (TypeError, AttributeError):
        _raise_serialization_error(text)

eleza _escape_attrib(text):
    # escape attribute value
    jaribu:
        ikiwa "&" kwenye text:
            text = text.replace("&", "&amp;")
        ikiwa "<" kwenye text:
            text = text.replace("<", "&lt;")
        ikiwa ">" kwenye text:
            text = text.replace(">", "&gt;")
        ikiwa "\"" kwenye text:
            text = text.replace("\"", "&quot;")
        # The following business ukijumuisha carriage returns ni to satisfy
        # Section 2.11 of the XML specification, stating that
        # CR ama CR LN should be replaced ukijumuisha just LN
        # http://www.w3.org/TR/REC-xml/#sec-line-ends
        ikiwa "\r\n" kwenye text:
            text = text.replace("\r\n", "\n")
        ikiwa "\r" kwenye text:
            text = text.replace("\r", "\n")
        #The following four lines are issue 17582
        ikiwa "\n" kwenye text:
            text = text.replace("\n", "&#10;")
        ikiwa "\t" kwenye text:
            text = text.replace("\t", "&#09;")
        rudisha text
    tatizo (TypeError, AttributeError):
        _raise_serialization_error(text)

eleza _escape_attrib_html(text):
    # escape attribute value
    jaribu:
        ikiwa "&" kwenye text:
            text = text.replace("&", "&amp;")
        ikiwa ">" kwenye text:
            text = text.replace(">", "&gt;")
        ikiwa "\"" kwenye text:
            text = text.replace("\"", "&quot;")
        rudisha text
    tatizo (TypeError, AttributeError):
        _raise_serialization_error(text)

# --------------------------------------------------------------------

eleza tostring(element, encoding=Tupu, method=Tupu, *,
             xml_declaration=Tupu, default_namespace=Tupu,
             short_empty_elements=Kweli):
    """Generate string representation of XML element.

    All subelements are included.  If encoding ni "unicode", a string
    ni returned. Otherwise a bytestring ni returned.

    *element* ni an Element instance, *encoding* ni an optional output
    encoding defaulting to US-ASCII, *method* ni an optional output which can
    be one of "xml" (default), "html", "text" ama "c14n", *default_namespace*
    sets the default XML namespace (kila "xmlns").

    Returns an (optionally) encoded string containing the XML data.

    """
    stream = io.StringIO() ikiwa encoding == 'unicode' isipokua io.BytesIO()
    ElementTree(element).write(stream, encoding,
                               xml_declaration=xml_declaration,
                               default_namespace=default_namespace,
                               method=method,
                               short_empty_elements=short_empty_elements)
    rudisha stream.getvalue()

kundi _ListDataStream(io.BufferedIOBase):
    """An auxiliary stream accumulating into a list reference."""
    eleza __init__(self, lst):
        self.lst = lst

    eleza writable(self):
        rudisha Kweli

    eleza seekable(self):
        rudisha Kweli

    eleza write(self, b):
        self.lst.append(b)

    eleza tell(self):
        rudisha len(self.lst)

eleza tostringlist(element, encoding=Tupu, method=Tupu, *,
                 xml_declaration=Tupu, default_namespace=Tupu,
                 short_empty_elements=Kweli):
    lst = []
    stream = _ListDataStream(lst)
    ElementTree(element).write(stream, encoding,
                               xml_declaration=xml_declaration,
                               default_namespace=default_namespace,
                               method=method,
                               short_empty_elements=short_empty_elements)
    rudisha lst


eleza dump(elem):
    """Write element tree ama element structure to sys.stdout.

    This function should be used kila debugging only.

    *elem* ni either an ElementTree, ama a single Element.  The exact output
    format ni implementation dependent.  In this version, it's written kama an
    ordinary XML file.

    """
    # debugging
    ikiwa sio isinstance(elem, ElementTree):
        elem = ElementTree(elem)
    elem.write(sys.stdout, encoding="unicode")
    tail = elem.getroot().tail
    ikiwa sio tail ama tail[-1] != "\n":
        sys.stdout.write("\n")

# --------------------------------------------------------------------
# parsing


eleza parse(source, parser=Tupu):
    """Parse XML document into element tree.

    *source* ni a filename ama file object containing XML data,
    *parser* ni an optional parser instance defaulting to XMLParser.

    Return an ElementTree instance.

    """
    tree = ElementTree()
    tree.parse(source, parser)
    rudisha tree


eleza iterparse(source, events=Tupu, parser=Tupu):
    """Incrementally parse XML document into ElementTree.

    This kundi also reports what's going on to the user based on the
    *events* it ni initialized with.  The supported events are the strings
    "start", "end", "start-ns" na "end-ns" (the "ns" events are used to get
    detailed namespace information).  If *events* ni omitted, only
    "end" events are reported.

    *source* ni a filename ama file object containing XML data, *events* is
    a list of events to report back, *parser* ni an optional parser instance.

    Returns an iterator providing (event, elem) pairs.

    """
    # Use the internal, undocumented _parser argument kila now; When the
    # parser argument of iterparse ni removed, this can be killed.
    pullparser = XMLPullParser(events=events, _parser=parser)
    eleza iterator():
        jaribu:
            wakati Kweli:
                tuma kutoka pullparser.read_events()
                # load event buffer
                data = source.read(16 * 1024)
                ikiwa sio data:
                    koma
                pullparser.feed(data)
            root = pullparser._close_and_return_root()
            tuma kutoka pullparser.read_events()
            it.root = root
        mwishowe:
            ikiwa close_source:
                source.close()

    kundi IterParseIterator(collections.abc.Iterator):
        __next__ = iterator().__next__
    it = IterParseIterator()
    it.root = Tupu
    toa iterator, IterParseIterator

    close_source = Uongo
    ikiwa sio hasattr(source, "read"):
        source = open(source, "rb")
        close_source = Kweli

    rudisha it


kundi XMLPullParser:

    eleza __init__(self, events=Tupu, *, _parser=Tupu):
        # The _parser argument ni kila internal use only na must sio be relied
        # upon kwenye user code. It will be removed kwenye a future release.
        # See http://bugs.python.org/issue17741 kila more details.

        self._events_queue = collections.deque()
        self._parser = _parser ama XMLParser(target=TreeBuilder())
        # wire up the parser kila event reporting
        ikiwa events ni Tupu:
            events = ("end",)
        self._parser._setevents(self._events_queue, events)

    eleza feed(self, data):
        """Feed encoded data to parser."""
        ikiwa self._parser ni Tupu:
            ashiria ValueError("feed() called after end of stream")
        ikiwa data:
            jaribu:
                self._parser.feed(data)
            tatizo SyntaxError kama exc:
                self._events_queue.append(exc)

    eleza _close_and_return_root(self):
        # iterparse needs this to set its root attribute properly :(
        root = self._parser.close()
        self._parser = Tupu
        rudisha root

    eleza close(self):
        """Finish feeding data to parser.

        Unlike XMLParser, does sio rudisha the root element. Use
        read_events() to consume elements kutoka XMLPullParser.
        """
        self._close_and_return_root()

    eleza read_events(self):
        """Return an iterator over currently available (event, elem) pairs.

        Events are consumed kutoka the internal event queue kama they are
        retrieved kutoka the iterator.
        """
        events = self._events_queue
        wakati events:
            event = events.popleft()
            ikiwa isinstance(event, Exception):
                ashiria event
            isipokua:
                tuma event


eleza XML(text, parser=Tupu):
    """Parse XML document kutoka string constant.

    This function can be used to embed "XML Literals" kwenye Python code.

    *text* ni a string containing XML data, *parser* ni an
    optional parser instance, defaulting to the standard XMLParser.

    Returns an Element instance.

    """
    ikiwa sio parser:
        parser = XMLParser(target=TreeBuilder())
    parser.feed(text)
    rudisha parser.close()


eleza XMLID(text, parser=Tupu):
    """Parse XML document kutoka string constant kila its IDs.

    *text* ni a string containing XML data, *parser* ni an
    optional parser instance, defaulting to the standard XMLParser.

    Returns an (Element, dict) tuple, kwenye which the
    dict maps element id:s to elements.

    """
    ikiwa sio parser:
        parser = XMLParser(target=TreeBuilder())
    parser.feed(text)
    tree = parser.close()
    ids = {}
    kila elem kwenye tree.iter():
        id = elem.get("id")
        ikiwa id:
            ids[id] = elem
    rudisha tree, ids

# Parse XML document kutoka string constant.  Alias kila XML().
fromstring = XML

eleza fromstringlist(sequence, parser=Tupu):
    """Parse XML document kutoka sequence of string fragments.

    *sequence* ni a list of other sequence, *parser* ni an optional parser
    instance, defaulting to the standard XMLParser.

    Returns an Element instance.

    """
    ikiwa sio parser:
        parser = XMLParser(target=TreeBuilder())
    kila text kwenye sequence:
        parser.feed(text)
    rudisha parser.close()

# --------------------------------------------------------------------


kundi TreeBuilder:
    """Generic element structure builder.

    This builder converts a sequence of start, data, na end method
    calls to a well-formed element structure.

    You can use this kundi to build an element structure using a custom XML
    parser, ama a parser kila some other XML-like format.

    *element_factory* ni an optional element factory which ni called
    to create new Element instances, kama necessary.

    *comment_factory* ni a factory to create comments to be used instead of
    the standard factory.  If *insert_comments* ni false (the default),
    comments will sio be inserted into the tree.

    *pi_factory* ni a factory to create processing instructions to be used
    instead of the standard factory.  If *insert_pis* ni false (the default),
    processing instructions will sio be inserted into the tree.
    """
    eleza __init__(self, element_factory=Tupu, *,
                 comment_factory=Tupu, pi_factory=Tupu,
                 insert_comments=Uongo, insert_pis=Uongo):
        self._data = [] # data collector
        self._elem = [] # element stack
        self._last = Tupu # last element
        self._root = Tupu # root element
        self._tail = Tupu # true ikiwa we're after an end tag
        ikiwa comment_factory ni Tupu:
            comment_factory = Comment
        self._comment_factory = comment_factory
        self.insert_comments = insert_comments
        ikiwa pi_factory ni Tupu:
            pi_factory = ProcessingInstruction
        self._pi_factory = pi_factory
        self.insert_pis = insert_pis
        ikiwa element_factory ni Tupu:
            element_factory = Element
        self._factory = element_factory

    eleza close(self):
        """Flush builder buffers na rudisha toplevel document Element."""
        assert len(self._elem) == 0, "missing end tags"
        assert self._root ni sio Tupu, "missing toplevel element"
        rudisha self._root

    eleza _flush(self):
        ikiwa self._data:
            ikiwa self._last ni sio Tupu:
                text = "".join(self._data)
                ikiwa self._tail:
                    assert self._last.tail ni Tupu, "internal error (tail)"
                    self._last.tail = text
                isipokua:
                    assert self._last.text ni Tupu, "internal error (text)"
                    self._last.text = text
            self._data = []

    eleza data(self, data):
        """Add text to current element."""
        self._data.append(data)

    eleza start(self, tag, attrs):
        """Open new element na rudisha it.

        *tag* ni the element name, *attrs* ni a dict containing element
        attributes.

        """
        self._flush()
        self._last = elem = self._factory(tag, attrs)
        ikiwa self._elem:
            self._elem[-1].append(elem)
        lasivyo self._root ni Tupu:
            self._root = elem
        self._elem.append(elem)
        self._tail = 0
        rudisha elem

    eleza end(self, tag):
        """Close na rudisha current Element.

        *tag* ni the element name.

        """
        self._flush()
        self._last = self._elem.pop()
        assert self._last.tag == tag,\
               "end tag mismatch (expected %s, got %s)" % (
                   self._last.tag, tag)
        self._tail = 1
        rudisha self._last

    eleza comment(self, text):
        """Create a comment using the comment_factory.

        *text* ni the text of the comment.
        """
        rudisha self._handle_single(
            self._comment_factory, self.insert_comments, text)

    eleza pi(self, target, text=Tupu):
        """Create a processing instruction using the pi_factory.

        *target* ni the target name of the processing instruction.
        *text* ni the data of the processing instruction, ama ''.
        """
        rudisha self._handle_single(
            self._pi_factory, self.insert_pis, target, text)

    eleza _handle_single(self, factory, insert, *args):
        elem = factory(*args)
        ikiwa insert:
            self._flush()
            self._last = elem
            ikiwa self._elem:
                self._elem[-1].append(elem)
            self._tail = 1
        rudisha elem


# also see ElementTree na TreeBuilder
kundi XMLParser:
    """Element structure builder kila XML source data based on the expat parser.

    *target* ni an optional target object which defaults to an instance of the
    standard TreeBuilder class, *encoding* ni an optional encoding string
    which ikiwa given, overrides the encoding specified kwenye the XML file:
    http://www.iana.org/assignments/character-sets

    """

    eleza __init__(self, *, target=Tupu, encoding=Tupu):
        jaribu:
            kutoka xml.parsers agiza expat
        tatizo ImportError:
            jaribu:
                agiza pyexpat kama expat
            tatizo ImportError:
                ashiria ImportError(
                    "No module named expat; use SimpleXMLTreeBuilder instead"
                    )
        parser = expat.ParserCreate(encoding, "}")
        ikiwa target ni Tupu:
            target = TreeBuilder()
        # underscored names are provided kila compatibility only
        self.parser = self._parser = parser
        self.target = self._target = target
        self._error = expat.error
        self._names = {} # name memo cache
        # main callbacks
        parser.DefaultHandlerExpand = self._default
        ikiwa hasattr(target, 'start'):
            parser.StartElementHandler = self._start
        ikiwa hasattr(target, 'end'):
            parser.EndElementHandler = self._end
        ikiwa hasattr(target, 'start_ns'):
            parser.StartNamespaceDeclHandler = self._start_ns
        ikiwa hasattr(target, 'end_ns'):
            parser.EndNamespaceDeclHandler = self._end_ns
        ikiwa hasattr(target, 'data'):
            parser.CharacterDataHandler = target.data
        # miscellaneous callbacks
        ikiwa hasattr(target, 'comment'):
            parser.CommentHandler = target.comment
        ikiwa hasattr(target, 'pi'):
            parser.ProcessingInstructionHandler = target.pi
        # Configure pyexpat: buffering, new-style attribute handling.
        parser.buffer_text = 1
        parser.ordered_attributes = 1
        parser.specified_attributes = 1
        self._doctype = Tupu
        self.entity = {}
        jaribu:
            self.version = "Expat %d.%d.%d" % expat.version_info
        tatizo AttributeError:
            pita # unknown

    eleza _setevents(self, events_queue, events_to_report):
        # Internal API kila XMLPullParser
        # events_to_report: a list of events to report during parsing (same as
        # the *events* of XMLPullParser's constructor.
        # events_queue: a list of actual parsing events that will be populated
        # by the underlying parser.
        #
        parser = self._parser
        append = events_queue.append
        kila event_name kwenye events_to_report:
            ikiwa event_name == "start":
                parser.ordered_attributes = 1
                parser.specified_attributes = 1
                eleza handler(tag, attrib_in, event=event_name, append=append,
                            start=self._start):
                    append((event, start(tag, attrib_in)))
                parser.StartElementHandler = handler
            lasivyo event_name == "end":
                eleza handler(tag, event=event_name, append=append,
                            end=self._end):
                    append((event, end(tag)))
                parser.EndElementHandler = handler
            lasivyo event_name == "start-ns":
                # TreeBuilder does sio implement .start_ns()
                ikiwa hasattr(self.target, "start_ns"):
                    eleza handler(prefix, uri, event=event_name, append=append,
                                start_ns=self._start_ns):
                        append((event, start_ns(prefix, uri)))
                isipokua:
                    eleza handler(prefix, uri, event=event_name, append=append):
                        append((event, (prefix ama '', uri ama '')))
                parser.StartNamespaceDeclHandler = handler
            lasivyo event_name == "end-ns":
                # TreeBuilder does sio implement .end_ns()
                ikiwa hasattr(self.target, "end_ns"):
                    eleza handler(prefix, event=event_name, append=append,
                                end_ns=self._end_ns):
                        append((event, end_ns(prefix)))
                isipokua:
                    eleza handler(prefix, event=event_name, append=append):
                        append((event, Tupu))
                parser.EndNamespaceDeclHandler = handler
            lasivyo event_name == 'comment':
                eleza handler(text, event=event_name, append=append, self=self):
                    append((event, self.target.comment(text)))
                parser.CommentHandler = handler
            lasivyo event_name == 'pi':
                eleza handler(pi_target, data, event=event_name, append=append,
                            self=self):
                    append((event, self.target.pi(pi_target, data)))
                parser.ProcessingInstructionHandler = handler
            isipokua:
                ashiria ValueError("unknown event %r" % event_name)

    eleza _raiseerror(self, value):
        err = ParseError(value)
        err.code = value.code
        err.position = value.lineno, value.offset
        ashiria err

    eleza _fixname(self, key):
        # expand qname, na convert name string to ascii, ikiwa possible
        jaribu:
            name = self._names[key]
        tatizo KeyError:
            name = key
            ikiwa "}" kwenye name:
                name = "{" + name
            self._names[key] = name
        rudisha name

    eleza _start_ns(self, prefix, uri):
        rudisha self.target.start_ns(prefix ama '', uri ama '')

    eleza _end_ns(self, prefix):
        rudisha self.target.end_ns(prefix ama '')

    eleza _start(self, tag, attr_list):
        # Handler kila expat's StartElementHandler. Since ordered_attributes
        # ni set, the attributes are reported kama a list of alternating
        # attribute name,value.
        fixname = self._fixname
        tag = fixname(tag)
        attrib = {}
        ikiwa attr_list:
            kila i kwenye range(0, len(attr_list), 2):
                attrib[fixname(attr_list[i])] = attr_list[i+1]
        rudisha self.target.start(tag, attrib)

    eleza _end(self, tag):
        rudisha self.target.end(self._fixname(tag))

    eleza _default(self, text):
        prefix = text[:1]
        ikiwa prefix == "&":
            # deal ukijumuisha undefined entities
            jaribu:
                data_handler = self.target.data
            tatizo AttributeError:
                return
            jaribu:
                data_handler(self.entity[text[1:-1]])
            tatizo KeyError:
                kutoka xml.parsers agiza expat
                err = expat.error(
                    "undefined entity %s: line %d, column %d" %
                    (text, self.parser.ErrorLineNumber,
                    self.parser.ErrorColumnNumber)
                    )
                err.code = 11 # XML_ERROR_UNDEFINED_ENTITY
                err.lineno = self.parser.ErrorLineNumber
                err.offset = self.parser.ErrorColumnNumber
                ashiria err
        lasivyo prefix == "<" na text[:9] == "<!DOCTYPE":
            self._doctype = [] # inside a doctype declaration
        lasivyo self._doctype ni sio Tupu:
            # parse doctype contents
            ikiwa prefix == ">":
                self._doctype = Tupu
                return
            text = text.strip()
            ikiwa sio text:
                return
            self._doctype.append(text)
            n = len(self._doctype)
            ikiwa n > 2:
                type = self._doctype[1]
                ikiwa type == "PUBLIC" na n == 4:
                    name, type, pubid, system = self._doctype
                    ikiwa pubid:
                        pubid = pubid[1:-1]
                lasivyo type == "SYSTEM" na n == 3:
                    name, type, system = self._doctype
                    pubid = Tupu
                isipokua:
                    return
                ikiwa hasattr(self.target, "doctype"):
                    self.target.doctype(name, pubid, system[1:-1])
                lasivyo hasattr(self, "doctype"):
                    warnings.warn(
                        "The doctype() method of XMLParser ni ignored.  "
                        "Define doctype() method on the TreeBuilder target.",
                        RuntimeWarning)

                self._doctype = Tupu

    eleza feed(self, data):
        """Feed encoded data to parser."""
        jaribu:
            self.parser.Parse(data, 0)
        tatizo self._error kama v:
            self._raiseerror(v)

    eleza close(self):
        """Finish feeding data to parser na rudisha element structure."""
        jaribu:
            self.parser.Parse("", 1) # end of data
        tatizo self._error kama v:
            self._raiseerror(v)
        jaribu:
            close_handler = self.target.close
        tatizo AttributeError:
            pita
        isipokua:
            rudisha close_handler()
        mwishowe:
            # get rid of circular references
            toa self.parser, self._parser
            toa self.target, self._target


# --------------------------------------------------------------------
# C14N 2.0

eleza canonicalize(xml_data=Tupu, *, out=Tupu, from_file=Tupu, **options):
    """Convert XML to its C14N 2.0 serialised form.

    If *out* ni provided, it must be a file ama file-like object that receives
    the serialised canonical XML output (text, sio bytes) through its ``.write()``
    method.  To write to a file, open it kwenye text mode ukijumuisha encoding "utf-8".
    If *out* ni sio provided, this function returns the output kama text string.

    Either *xml_data* (an XML string) ama *from_file* (a file path ama
    file-like object) must be provided kama input.

    The configuration options are the same kama kila the ``C14NWriterTarget``.
    """
    ikiwa xml_data ni Tupu na from_file ni Tupu:
        ashiria ValueError("Either 'xml_data' ama 'from_file' must be provided kama input")
    sio = Tupu
    ikiwa out ni Tupu:
        sio = out = io.StringIO()

    parser = XMLParser(target=C14NWriterTarget(out.write, **options))

    ikiwa xml_data ni sio Tupu:
        parser.feed(xml_data)
        parser.close()
    lasivyo from_file ni sio Tupu:
        parse(from_file, parser=parser)

    rudisha sio.getvalue() ikiwa sio ni sio Tupu isipokua Tupu


_looks_like_prefix_name = re.compile(r'^\w+:\w+$', re.UNICODE).match


kundi C14NWriterTarget:
    """
    Canonicalization writer target kila the XMLParser.

    Serialises parse events to XML C14N 2.0.

    The *write* function ni used kila writing out the resulting data stream
    kama text (sio bytes).  To write to a file, open it kwenye text mode ukijumuisha encoding
    "utf-8" na pita its ``.write`` method.

    Configuration options:

    - *with_comments*: set to true to include comments
    - *strip_text*: set to true to strip whitespace before na after text content
    - *rewrite_prefixes*: set to true to replace namespace prefixes by "n{number}"
    - *qname_aware_tags*: a set of qname aware tag names kwenye which prefixes
                          should be replaced kwenye text content
    - *qname_aware_attrs*: a set of qname aware attribute names kwenye which prefixes
                           should be replaced kwenye text content
    - *exclude_attrs*: a set of attribute names that should sio be serialised
    - *exclude_tags*: a set of tag names that should sio be serialised
    """
    eleza __init__(self, write, *,
                 with_comments=Uongo, strip_text=Uongo, rewrite_prefixes=Uongo,
                 qname_aware_tags=Tupu, qname_aware_attrs=Tupu,
                 exclude_attrs=Tupu, exclude_tags=Tupu):
        self._write = write
        self._data = []
        self._with_comments = with_comments
        self._strip_text = strip_text
        self._exclude_attrs = set(exclude_attrs) ikiwa exclude_attrs isipokua Tupu
        self._exclude_tags = set(exclude_tags) ikiwa exclude_tags isipokua Tupu

        self._rewrite_prefixes = rewrite_prefixes
        ikiwa qname_aware_tags:
            self._qname_aware_tags = set(qname_aware_tags)
        isipokua:
            self._qname_aware_tags = Tupu
        ikiwa qname_aware_attrs:
            self._find_qname_aware_attrs = set(qname_aware_attrs).intersection
        isipokua:
            self._find_qname_aware_attrs = Tupu

        # Stack ukijumuisha globally na newly declared namespaces kama (uri, prefix) pairs.
        self._declared_ns_stack = [[
            ("http://www.w3.org/XML/1998/namespace", "xml"),
        ]]
        # Stack ukijumuisha user declared namespace prefixes kama (uri, prefix) pairs.
        self._ns_stack = []
        ikiwa sio rewrite_prefixes:
            self._ns_stack.append(list(_namespace_map.items()))
        self._ns_stack.append([])
        self._prefix_map = {}
        self._preserve_space = [Uongo]
        self._pending_start = Tupu
        self._root_seen = Uongo
        self._root_done = Uongo
        self._ignored_depth = 0

    eleza _iter_namespaces(self, ns_stack, _reversed=reversed):
        kila namespaces kwenye _reversed(ns_stack):
            ikiwa namespaces:  # almost no element declares new namespaces
                tuma kutoka namespaces

    eleza _resolve_prefix_name(self, prefixed_name):
        prefix, name = prefixed_name.split(':', 1)
        kila uri, p kwenye self._iter_namespaces(self._ns_stack):
            ikiwa p == prefix:
                rudisha f'{{{uri}}}{name}'
        ashiria ValueError(f'Prefix {prefix} of QName "{prefixed_name}" ni sio declared kwenye scope')

    eleza _qname(self, qname, uri=Tupu):
        ikiwa uri ni Tupu:
            uri, tag = qname[1:].rsplit('}', 1) ikiwa qname[:1] == '{' isipokua ('', qname)
        isipokua:
            tag = qname

        prefixes_seen = set()
        kila u, prefix kwenye self._iter_namespaces(self._declared_ns_stack):
            ikiwa u == uri na prefix haiko kwenye prefixes_seen:
                rudisha f'{prefix}:{tag}' ikiwa prefix isipokua tag, tag, uri
            prefixes_seen.add(prefix)

        # Not declared yet => add new declaration.
        ikiwa self._rewrite_prefixes:
            ikiwa uri kwenye self._prefix_map:
                prefix = self._prefix_map[uri]
            isipokua:
                prefix = self._prefix_map[uri] = f'n{len(self._prefix_map)}'
            self._declared_ns_stack[-1].append((uri, prefix))
            rudisha f'{prefix}:{tag}', tag, uri

        ikiwa sio uri na '' haiko kwenye prefixes_seen:
            # No default namespace declared => no prefix needed.
            rudisha tag, tag, uri

        kila u, prefix kwenye self._iter_namespaces(self._ns_stack):
            ikiwa u == uri:
                self._declared_ns_stack[-1].append((uri, prefix))
                rudisha f'{prefix}:{tag}' ikiwa prefix isipokua tag, tag, uri

        ashiria ValueError(f'Namespace "{uri}" ni sio declared kwenye scope')

    eleza data(self, data):
        ikiwa sio self._ignored_depth:
            self._data.append(data)

    eleza _flush(self, _join_text=''.join):
        data = _join_text(self._data)
        toa self._data[:]
        ikiwa self._strip_text na sio self._preserve_space[-1]:
            data = data.strip()
        ikiwa self._pending_start ni sio Tupu:
            args, self._pending_start = self._pending_start, Tupu
            qname_text = data ikiwa data na _looks_like_prefix_name(data) isipokua Tupu
            self._start(*args, qname_text)
            ikiwa qname_text ni sio Tupu:
                return
        ikiwa data na self._root_seen:
            self._write(_escape_cdata_c14n(data))

    eleza start_ns(self, prefix, uri):
        ikiwa self._ignored_depth:
            return
        # we may have to resolve qnames kwenye text content
        ikiwa self._data:
            self._flush()
        self._ns_stack[-1].append((uri, prefix))

    eleza start(self, tag, attrs):
        ikiwa self._exclude_tags ni sio Tupu na (
                self._ignored_depth ama tag kwenye self._exclude_tags):
            self._ignored_depth += 1
            return
        ikiwa self._data:
            self._flush()

        new_namespaces = []
        self._declared_ns_stack.append(new_namespaces)

        ikiwa self._qname_aware_tags ni sio Tupu na tag kwenye self._qname_aware_tags:
            # Need to parse text first to see ikiwa it requires a prefix declaration.
            self._pending_start = (tag, attrs, new_namespaces)
            return
        self._start(tag, attrs, new_namespaces)

    eleza _start(self, tag, attrs, new_namespaces, qname_text=Tupu):
        ikiwa self._exclude_attrs ni sio Tupu na attrs:
            attrs = {k: v kila k, v kwenye attrs.items() ikiwa k haiko kwenye self._exclude_attrs}

        qnames = {tag, *attrs}
        resolved_names = {}

        # Resolve prefixes kwenye attribute na tag text.
        ikiwa qname_text ni sio Tupu:
            qname = resolved_names[qname_text] = self._resolve_prefix_name(qname_text)
            qnames.add(qname)
        ikiwa self._find_qname_aware_attrs ni sio Tupu na attrs:
            qattrs = self._find_qname_aware_attrs(attrs)
            ikiwa qattrs:
                kila attr_name kwenye qattrs:
                    value = attrs[attr_name]
                    ikiwa _looks_like_prefix_name(value):
                        qname = resolved_names[value] = self._resolve_prefix_name(value)
                        qnames.add(qname)
            isipokua:
                qattrs = Tupu
        isipokua:
            qattrs = Tupu

        # Assign prefixes kwenye lexicographical order of used URIs.
        parse_qname = self._qname
        parsed_qnames = {n: parse_qname(n) kila n kwenye sorted(
            qnames, key=lambda n: n.split('}', 1))}

        # Write namespace declarations kwenye prefix order ...
        ikiwa new_namespaces:
            attr_list = [
                ('xmlns:' + prefix ikiwa prefix isipokua 'xmlns', uri)
                kila uri, prefix kwenye new_namespaces
            ]
            attr_list.sort()
        isipokua:
            # almost always empty
            attr_list = []

        # ... followed by attributes kwenye URI+name order
        ikiwa attrs:
            kila k, v kwenye sorted(attrs.items()):
                ikiwa qattrs ni sio Tupu na k kwenye qattrs na v kwenye resolved_names:
                    v = parsed_qnames[resolved_names[v]][0]
                attr_qname, attr_name, uri = parsed_qnames[k]
                # No prefix kila attributes kwenye default ('') namespace.
                attr_list.append((attr_qname ikiwa uri isipokua attr_name, v))

        # Honour xml:space attributes.
        space_behaviour = attrs.get('{http://www.w3.org/XML/1998/namespace}space')
        self._preserve_space.append(
            space_behaviour == 'preserve' ikiwa space_behaviour
            isipokua self._preserve_space[-1])

        # Write the tag.
        write = self._write
        write('<' + parsed_qnames[tag][0])
        ikiwa attr_list:
            write(''.join([f' {k}="{_escape_attrib_c14n(v)}"' kila k, v kwenye attr_list]))
        write('>')

        # Write the resolved qname text content.
        ikiwa qname_text ni sio Tupu:
            write(_escape_cdata_c14n(parsed_qnames[resolved_names[qname_text]][0]))

        self._root_seen = Kweli
        self._ns_stack.append([])

    eleza end(self, tag):
        ikiwa self._ignored_depth:
            self._ignored_depth -= 1
            return
        ikiwa self._data:
            self._flush()
        self._write(f'</{self._qname(tag)[0]}>')
        self._preserve_space.pop()
        self._root_done = len(self._preserve_space) == 1
        self._declared_ns_stack.pop()
        self._ns_stack.pop()

    eleza comment(self, text):
        ikiwa sio self._with_comments:
            return
        ikiwa self._ignored_depth:
            return
        ikiwa self._root_done:
            self._write('\n')
        lasivyo self._root_seen na self._data:
            self._flush()
        self._write(f'<!--{_escape_cdata_c14n(text)}-->')
        ikiwa sio self._root_seen:
            self._write('\n')

    eleza pi(self, target, data):
        ikiwa self._ignored_depth:
            return
        ikiwa self._root_done:
            self._write('\n')
        lasivyo self._root_seen na self._data:
            self._flush()
        self._write(
            f'<?{target} {_escape_cdata_c14n(data)}?>' ikiwa data isipokua f'<?{target}?>')
        ikiwa sio self._root_seen:
            self._write('\n')


eleza _escape_cdata_c14n(text):
    # escape character data
    jaribu:
        # it's worth avoiding do-nothing calls kila strings that are
        # shorter than 500 character, ama so.  assume that's, by far,
        # the most common case kwenye most applications.
        ikiwa '&' kwenye text:
            text = text.replace('&', '&amp;')
        ikiwa '<' kwenye text:
            text = text.replace('<', '&lt;')
        ikiwa '>' kwenye text:
            text = text.replace('>', '&gt;')
        ikiwa '\r' kwenye text:
            text = text.replace('\r', '&#xD;')
        rudisha text
    tatizo (TypeError, AttributeError):
        _raise_serialization_error(text)


eleza _escape_attrib_c14n(text):
    # escape attribute value
    jaribu:
        ikiwa '&' kwenye text:
            text = text.replace('&', '&amp;')
        ikiwa '<' kwenye text:
            text = text.replace('<', '&lt;')
        ikiwa '"' kwenye text:
            text = text.replace('"', '&quot;')
        ikiwa '\t' kwenye text:
            text = text.replace('\t', '&#x9;')
        ikiwa '\n' kwenye text:
            text = text.replace('\n', '&#xA;')
        ikiwa '\r' kwenye text:
            text = text.replace('\r', '&#xD;')
        rudisha text
    tatizo (TypeError, AttributeError):
        _raise_serialization_error(text)


# --------------------------------------------------------------------

# Import the C accelerators
jaribu:
    # Element ni going to be shadowed by the C implementation. We need to keep
    # the Python version of it accessible kila some "creative" by external code
    # (see tests)
    _Element_Py = Element

    # Element, SubElement, ParseError, TreeBuilder, XMLParser, _set_factories
    kutoka _elementtree agiza *
    kutoka _elementtree agiza _set_factories
tatizo ImportError:
    pita
isipokua:
    _set_factories(Comment, ProcessingInstruction)
