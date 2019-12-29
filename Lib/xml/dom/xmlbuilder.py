"""Implementation of the DOM Level 3 'LS-Load' feature."""

agiza copy
agiza warnings
agiza xml.dom

kutoka xml.dom.NodeFilter agiza NodeFilter


__all__ = ["DOMBuilder", "DOMEntityResolver", "DOMInputSource"]


kundi Options:
    """Features object that has variables set kila each DOMBuilder feature.

    The DOMBuilder kundi uses an instance of this kundi to pita settings to
    the ExpatBuilder class.
    """

    # Note that the DOMBuilder kundi kwenye LoadSave constrains which of these
    # values can be set using the DOM Level 3 LoadSave feature.

    namespaces = 1
    namespace_declarations = Kweli
    validation = Uongo
    external_parameter_entities = Kweli
    external_general_entities = Kweli
    external_dtd_subset = Kweli
    validate_if_schema = Uongo
    validate = Uongo
    datatype_normalization = Uongo
    create_entity_ref_nodes = Kweli
    entities = Kweli
    whitespace_in_element_content = Kweli
    cdata_sections = Kweli
    comments = Kweli
    charset_overrides_xml_encoding = Kweli
    infoset = Uongo
    supported_mediatypes_only = Uongo

    errorHandler = Tupu
    filter = Tupu


kundi DOMBuilder:
    entityResolver = Tupu
    errorHandler = Tupu
    filter = Tupu

    ACTION_REPLACE = 1
    ACTION_APPEND_AS_CHILDREN = 2
    ACTION_INSERT_AFTER = 3
    ACTION_INSERT_BEFORE = 4

    _legal_actions = (ACTION_REPLACE, ACTION_APPEND_AS_CHILDREN,
                      ACTION_INSERT_AFTER, ACTION_INSERT_BEFORE)

    eleza __init__(self):
        self._options = Options()

    eleza _get_entityResolver(self):
        rudisha self.entityResolver
    eleza _set_entityResolver(self, entityResolver):
        self.entityResolver = entityResolver

    eleza _get_errorHandler(self):
        rudisha self.errorHandler
    eleza _set_errorHandler(self, errorHandler):
        self.errorHandler = errorHandler

    eleza _get_filter(self):
        rudisha self.filter
    eleza _set_filter(self, filter):
        self.filter = filter

    eleza setFeature(self, name, state):
        ikiwa self.supportsFeature(name):
            state = state na 1 ama 0
            jaribu:
                settings = self._settings[(_name_xform(name), state)]
            tatizo KeyError:
                ashiria xml.dom.NotSupportedErr(
                    "unsupported feature: %r" % (name,)) kutoka Tupu
            isipokua:
                kila name, value kwenye settings:
                    setattr(self._options, name, value)
        isipokua:
            ashiria xml.dom.NotFoundErr("unknown feature: " + repr(name))

    eleza supportsFeature(self, name):
        rudisha hasattr(self._options, _name_xform(name))

    eleza canSetFeature(self, name, state):
        key = (_name_xform(name), state na 1 ama 0)
        rudisha key kwenye self._settings

    # This dictionary maps kutoka (feature,value) to a list of
    # (option,value) pairs that should be set on the Options object.
    # If a (feature,value) setting ni haiko kwenye this dictionary, it is
    # sio supported by the DOMBuilder.
    #
    _settings = {
        ("namespace_declarations", 0): [
            ("namespace_declarations", 0)],
        ("namespace_declarations", 1): [
            ("namespace_declarations", 1)],
        ("validation", 0): [
            ("validation", 0)],
        ("external_general_entities", 0): [
            ("external_general_entities", 0)],
        ("external_general_entities", 1): [
            ("external_general_entities", 1)],
        ("external_parameter_entities", 0): [
            ("external_parameter_entities", 0)],
        ("external_parameter_entities", 1): [
            ("external_parameter_entities", 1)],
        ("validate_if_schema", 0): [
            ("validate_if_schema", 0)],
        ("create_entity_ref_nodes", 0): [
            ("create_entity_ref_nodes", 0)],
        ("create_entity_ref_nodes", 1): [
            ("create_entity_ref_nodes", 1)],
        ("entities", 0): [
            ("create_entity_ref_nodes", 0),
            ("entities", 0)],
        ("entities", 1): [
            ("entities", 1)],
        ("whitespace_in_element_content", 0): [
            ("whitespace_in_element_content", 0)],
        ("whitespace_in_element_content", 1): [
            ("whitespace_in_element_content", 1)],
        ("cdata_sections", 0): [
            ("cdata_sections", 0)],
        ("cdata_sections", 1): [
            ("cdata_sections", 1)],
        ("comments", 0): [
            ("comments", 0)],
        ("comments", 1): [
            ("comments", 1)],
        ("charset_overrides_xml_encoding", 0): [
            ("charset_overrides_xml_encoding", 0)],
        ("charset_overrides_xml_encoding", 1): [
            ("charset_overrides_xml_encoding", 1)],
        ("infoset", 0): [],
        ("infoset", 1): [
            ("namespace_declarations", 0),
            ("validate_if_schema", 0),
            ("create_entity_ref_nodes", 0),
            ("entities", 0),
            ("cdata_sections", 0),
            ("datatype_normalization", 1),
            ("whitespace_in_element_content", 1),
            ("comments", 1),
            ("charset_overrides_xml_encoding", 1)],
        ("supported_mediatypes_only", 0): [
            ("supported_mediatypes_only", 0)],
        ("namespaces", 0): [
            ("namespaces", 0)],
        ("namespaces", 1): [
            ("namespaces", 1)],
    }

    eleza getFeature(self, name):
        xname = _name_xform(name)
        jaribu:
            rudisha getattr(self._options, xname)
        tatizo AttributeError:
            ikiwa name == "infoset":
                options = self._options
                rudisha (options.datatype_normalization
                        na options.whitespace_in_element_content
                        na options.comments
                        na options.charset_overrides_xml_encoding
                        na sio (options.namespace_declarations
                                 ama options.validate_if_schema
                                 ama options.create_entity_ref_nodes
                                 ama options.entities
                                 ama options.cdata_sections))
            ashiria xml.dom.NotFoundErr("feature %s sio known" % repr(name))

    eleza parseURI(self, uri):
        ikiwa self.entityResolver:
            input = self.entityResolver.resolveEntity(Tupu, uri)
        isipokua:
            input = DOMEntityResolver().resolveEntity(Tupu, uri)
        rudisha self.parse(input)

    eleza parse(self, input):
        options = copy.copy(self._options)
        options.filter = self.filter
        options.errorHandler = self.errorHandler
        fp = input.byteStream
        ikiwa fp ni Tupu na options.systemId:
            agiza urllib.request
            fp = urllib.request.urlopen(input.systemId)
        rudisha self._parse_bytestream(fp, options)

    eleza parseWithContext(self, input, cnode, action):
        ikiwa action haiko kwenye self._legal_actions:
            ashiria ValueError("not a legal action")
        ashiria NotImplementedError("Haven't written this yet...")

    eleza _parse_bytestream(self, stream, options):
        agiza xml.dom.expatbuilder
        builder = xml.dom.expatbuilder.makeBuilder(options)
        rudisha builder.parseFile(stream)


eleza _name_xform(name):
    rudisha name.lower().replace('-', '_')


kundi DOMEntityResolver(object):
    __slots__ = '_opener',

    eleza resolveEntity(self, publicId, systemId):
        assert systemId ni sio Tupu
        source = DOMInputSource()
        source.publicId = publicId
        source.systemId = systemId
        source.byteStream = self._get_opener().open(systemId)

        # determine the encoding ikiwa the transport provided it
        source.encoding = self._guess_media_encoding(source)

        # determine the base URI ni we can
        agiza posixpath, urllib.parse
        parts = urllib.parse.urlparse(systemId)
        scheme, netloc, path, params, query, fragment = parts
        # XXX should we check the scheme here kama well?
        ikiwa path na sio path.endswith("/"):
            path = posixpath.dirname(path) + "/"
            parts = scheme, netloc, path, params, query, fragment
            source.baseURI = urllib.parse.urlunparse(parts)

        rudisha source

    eleza _get_opener(self):
        jaribu:
            rudisha self._opener
        tatizo AttributeError:
            self._opener = self._create_opener()
            rudisha self._opener

    eleza _create_opener(self):
        agiza urllib.request
        rudisha urllib.request.build_opener()

    eleza _guess_media_encoding(self, source):
        info = source.byteStream.info()
        ikiwa "Content-Type" kwenye info:
            kila param kwenye info.getplist():
                ikiwa param.startswith("charset="):
                    rudisha param.split("=", 1)[1].lower()


kundi DOMInputSource(object):
    __slots__ = ('byteStream', 'characterStream', 'stringData',
                 'encoding', 'publicId', 'systemId', 'baseURI')

    eleza __init__(self):
        self.byteStream = Tupu
        self.characterStream = Tupu
        self.stringData = Tupu
        self.encoding = Tupu
        self.publicId = Tupu
        self.systemId = Tupu
        self.baseURI = Tupu

    eleza _get_byteStream(self):
        rudisha self.byteStream
    eleza _set_byteStream(self, byteStream):
        self.byteStream = byteStream

    eleza _get_characterStream(self):
        rudisha self.characterStream
    eleza _set_characterStream(self, characterStream):
        self.characterStream = characterStream

    eleza _get_stringData(self):
        rudisha self.stringData
    eleza _set_stringData(self, data):
        self.stringData = data

    eleza _get_encoding(self):
        rudisha self.encoding
    eleza _set_encoding(self, encoding):
        self.encoding = encoding

    eleza _get_publicId(self):
        rudisha self.publicId
    eleza _set_publicId(self, publicId):
        self.publicId = publicId

    eleza _get_systemId(self):
        rudisha self.systemId
    eleza _set_systemId(self, systemId):
        self.systemId = systemId

    eleza _get_baseURI(self):
        rudisha self.baseURI
    eleza _set_baseURI(self, uri):
        self.baseURI = uri


kundi DOMBuilderFilter:
    """Element filter which can be used to tailor construction of
    a DOM instance.
    """

    # There's really no need kila this class; concrete implementations
    # should just implement the endElement() na startElement()
    # methods kama appropriate.  Using this makes it easy to only
    # implement one of them.

    FILTER_ACCEPT = 1
    FILTER_REJECT = 2
    FILTER_SKIP = 3
    FILTER_INTERRUPT = 4

    whatToShow = NodeFilter.SHOW_ALL

    eleza _get_whatToShow(self):
        rudisha self.whatToShow

    eleza acceptNode(self, element):
        rudisha self.FILTER_ACCEPT

    eleza startContainer(self, element):
        rudisha self.FILTER_ACCEPT

toa NodeFilter


kundi DocumentLS:
    """Mixin to create documents that conform to the load/save spec."""

    async_ = Uongo

    eleza _get_async(self):
        rudisha Uongo

    eleza _set_async(self, flag):
        ikiwa flag:
            ashiria xml.dom.NotSupportedErr(
                "asynchronous document loading ni sio supported")

    eleza abort(self):
        # What does it mean to "clear" a document?  Does the
        # documentElement disappear?
        ashiria NotImplementedError(
            "haven't figured out what this means yet")

    eleza load(self, uri):
        ashiria NotImplementedError("haven't written this yet")

    eleza loadXML(self, source):
        ashiria NotImplementedError("haven't written this yet")

    eleza saveXML(self, snode):
        ikiwa snode ni Tupu:
            snode = self
        elikiwa snode.ownerDocument ni sio self:
            ashiria xml.dom.WrongDocumentErr()
        rudisha snode.toxml()


kundi DOMImplementationLS:
    MODE_SYNCHRONOUS = 1
    MODE_ASYNCHRONOUS = 2

    eleza createDOMBuilder(self, mode, schemaType):
        ikiwa schemaType ni sio Tupu:
            ashiria xml.dom.NotSupportedErr(
                "schemaType sio yet supported")
        ikiwa mode == self.MODE_SYNCHRONOUS:
            rudisha DOMBuilder()
        ikiwa mode == self.MODE_ASYNCHRONOUS:
            ashiria xml.dom.NotSupportedErr(
                "asynchronous builders are sio supported")
        ashiria ValueError("unknown value kila mode")

    eleza createDOMWriter(self):
        ashiria NotImplementedError(
            "the writer interface hasn't been written yet!")

    eleza createDOMInputSource(self):
        rudisha DOMInputSource()
