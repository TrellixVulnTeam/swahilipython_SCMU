"""Representing na manipulating email headers via custom objects.

This module provides an implementation of the HeaderRegistry API.
The implementation ni designed to flexibly follow RFC5322 rules.

Eventually HeaderRegistry will be a public API, but it isn't yet,
and will probably change some before that happens.

"""
kutoka types agiza MappingProxyType

kutoka email agiza utils
kutoka email agiza errors
kutoka email agiza _header_value_parser kama parser

kundi Address:

    eleza __init__(self, display_name='', username='', domain='', addr_spec=Tupu):
        """Create an object representing a full email address.

        An address can have a 'display_name', a 'username', na a 'domain'.  In
        addition to specifying the username na domain separately, they may be
        specified together by using the addr_spec keyword *instead of* the
        username na domain keywords.  If an addr_spec string ni specified it
        must be properly quoted according to RFC 5322 rules; an error will be
        raised ikiwa it ni not.

        An Address object has display_name, username, domain, na addr_spec
        attributes, all of which are read-only.  The addr_spec na the string
        value of the object are both quoted according to RFC5322 rules, but
        without any Content Transfer Encoding.

        """
        # This clause ukijumuisha its potential 'raise' may only happen when an
        # application program creates an Address object using an addr_spec
        # keyword.  The email library code itself must always supply username
        # na domain.
        ikiwa addr_spec ni sio Tupu:
            ikiwa username ama domain:
                ashiria TypeError("addrspec specified when username and/or "
                                "domain also specified")
            a_s, rest = parser.get_addr_spec(addr_spec)
            ikiwa rest:
                ashiria ValueError("Invalid addr_spec; only '{}' "
                                 "could be parsed kutoka '{}'".format(
                                    a_s, addr_spec))
            ikiwa a_s.all_defects:
                ashiria a_s.all_defects[0]
            username = a_s.local_part
            domain = a_s.domain
        self._display_name = display_name
        self._username = username
        self._domain = domain

    @property
    eleza display_name(self):
        rudisha self._display_name

    @property
    eleza username(self):
        rudisha self._username

    @property
    eleza domain(self):
        rudisha self._domain

    @property
    eleza addr_spec(self):
        """The addr_spec (username@domain) portion of the address, quoted
        according to RFC 5322 rules, but ukijumuisha no Content Transfer Encoding.
        """
        nameset = set(self.username)
        ikiwa len(nameset) > len(nameset-parser.DOT_ATOM_ENDS):
            lp = parser.quote_string(self.username)
        isipokua:
            lp = self.username
        ikiwa self.domain:
            rudisha lp + '@' + self.domain
        ikiwa sio lp:
            rudisha '<>'
        rudisha lp

    eleza __repr__(self):
        rudisha "{}(display_name={!r}, username={!r}, domain={!r})".format(
                        self.__class__.__name__,
                        self.display_name, self.username, self.domain)

    eleza __str__(self):
        nameset = set(self.display_name)
        ikiwa len(nameset) > len(nameset-parser.SPECIALS):
            disp = parser.quote_string(self.display_name)
        isipokua:
            disp = self.display_name
        ikiwa disp:
            addr_spec = '' ikiwa self.addr_spec=='<>' isipokua self.addr_spec
            rudisha "{} <{}>".format(disp, addr_spec)
        rudisha self.addr_spec

    eleza __eq__(self, other):
        ikiwa type(other) != type(self):
            rudisha Uongo
        rudisha (self.display_name == other.display_name na
                self.username == other.username na
                self.domain == other.domain)


kundi Group:

    eleza __init__(self, display_name=Tupu, addresses=Tupu):
        """Create an object representing an address group.

        An address group consists of a display_name followed by colon na a
        list of addresses (see Address) terminated by a semi-colon.  The Group
        ni created by specifying a display_name na a possibly empty list of
        Address objects.  A Group can also be used to represent a single
        address that ni haiko kwenye a group, which ni convenient when manipulating
        lists that are a combination of Groups na individual Addresses.  In
        this case the display_name should be set to Tupu.  In particular, the
        string representation of a Group whose display_name ni Tupu ni the same
        kama the Address object, ikiwa there ni one na only one Address object in
        the addresses list.

        """
        self._display_name = display_name
        self._addresses = tuple(addresses) ikiwa addresses isipokua tuple()

    @property
    eleza display_name(self):
        rudisha self._display_name

    @property
    eleza addresses(self):
        rudisha self._addresses

    eleza __repr__(self):
        rudisha "{}(display_name={!r}, addresses={!r}".format(
                 self.__class__.__name__,
                 self.display_name, self.addresses)

    eleza __str__(self):
        ikiwa self.display_name ni Tupu na len(self.addresses)==1:
            rudisha str(self.addresses[0])
        disp = self.display_name
        ikiwa disp ni sio Tupu:
            nameset = set(disp)
            ikiwa len(nameset) > len(nameset-parser.SPECIALS):
                disp = parser.quote_string(disp)
        adrstr = ", ".join(str(x) kila x kwenye self.addresses)
        adrstr = ' ' + adrstr ikiwa adrstr isipokua adrstr
        rudisha "{}:{};".format(disp, adrstr)

    eleza __eq__(self, other):
        ikiwa type(other) != type(self):
            rudisha Uongo
        rudisha (self.display_name == other.display_name na
                self.addresses == other.addresses)


# Header Classes #

kundi BaseHeader(str):

    """Base kundi kila message headers.

    Implements generic behavior na provides tools kila subclasses.

    A subkundi must define a classmethod named 'parse' that takes an unfolded
    value string na a dictionary kama its arguments.  The dictionary will
    contain one key, 'defects', initialized to an empty list.  After the call
    the dictionary must contain two additional keys: parse_tree, set to the
    parse tree obtained kutoka parsing the header, na 'decoded', set to the
    string value of the idealized representation of the data kutoka the value.
    (That is, encoded words are decoded, na values that have canonical
    representations are so represented.)

    The defects key ni intended to collect parsing defects, which the message
    parser will subsequently dispose of kama appropriate.  The parser should not,
    insofar kama practical, ashiria any errors.  Defects should be added to the
    list instead.  The standard header parsers register defects kila RFC
    compliance issues, kila obsolete RFC syntax, na kila unrecoverable parsing
    errors.

    The parse method may add additional keys to the dictionary.  In this case
    the subkundi must define an 'init' method, which will be pitaed the
    dictionary kama its keyword arguments.  The method should use (usually by
    setting them kama the value of similarly named attributes) na remove all the
    extra keys added by its parse method, na then use super to call its parent
    kundi ukijumuisha the remaining arguments na keywords.

    The subkundi should also make sure that a 'max_count' attribute ni defined
    that ni either Tupu ama 1. XXX: need to better define this API.

    """

    eleza __new__(cls, name, value):
        kwds = {'defects': []}
        cls.parse(value, kwds)
        ikiwa utils._has_surrogates(kwds['decoded']):
            kwds['decoded'] = utils._sanitize(kwds['decoded'])
        self = str.__new__(cls, kwds['decoded'])
        toa kwds['decoded']
        self.init(name, **kwds)
        rudisha self

    eleza init(self, name, *, parse_tree, defects):
        self._name = name
        self._parse_tree = parse_tree
        self._defects = defects

    @property
    eleza name(self):
        rudisha self._name

    @property
    eleza defects(self):
        rudisha tuple(self._defects)

    eleza __reduce__(self):
        rudisha (
            _reconstruct_header,
            (
                self.__class__.__name__,
                self.__class__.__bases__,
                str(self),
            ),
            self.__dict__)

    @classmethod
    eleza _reconstruct(cls, value):
        rudisha str.__new__(cls, value)

    eleza fold(self, *, policy):
        """Fold header according to policy.

        The parsed representation of the header ni folded according to
        RFC5322 rules, kama modified by the policy.  If the parse tree
        contains surrogateescaped bytes, the bytes are CTE encoded using
        the charset 'unknown-8bit".

        Any non-ASCII characters kwenye the parse tree are CTE encoded using
        charset utf-8. XXX: make this a policy setting.

        The returned value ni an ASCII-only string possibly containing linesep
        characters, na ending ukijumuisha a linesep character.  The string includes
        the header name na the ': ' separator.

        """
        # At some point we need to put fws here ikiwa it was kwenye the source.
        header = parser.Header([
            parser.HeaderLabel([
                parser.ValueTerminal(self.name, 'header-name'),
                parser.ValueTerminal(':', 'header-sep')]),
            ])
        ikiwa self._parse_tree:
            header.append(
                parser.CFWSList([parser.WhiteSpaceTerminal(' ', 'fws')]))
        header.append(self._parse_tree)
        rudisha header.fold(policy=policy)


eleza _reconstruct_header(cls_name, bases, value):
    rudisha type(cls_name, bases, {})._reconstruct(value)


kundi UnstructuredHeader:

    max_count = Tupu
    value_parser = staticmethod(parser.get_unstructured)

    @classmethod
    eleza parse(cls, value, kwds):
        kwds['parse_tree'] = cls.value_parser(value)
        kwds['decoded'] = str(kwds['parse_tree'])


kundi UniqueUnstructuredHeader(UnstructuredHeader):

    max_count = 1


kundi DateHeader:

    """Header whose value consists of a single timestamp.

    Provides an additional attribute, datetime, which ni either an aware
    datetime using a timezone, ama a naive datetime ikiwa the timezone
    kwenye the input string ni -0000.  Also accepts a datetime kama input.
    The 'value' attribute ni the normalized form of the timestamp,
    which means it ni the output of format_datetime on the datetime.
    """

    max_count = Tupu

    # This ni used only kila folding, sio kila creating 'decoded'.
    value_parser = staticmethod(parser.get_unstructured)

    @classmethod
    eleza parse(cls, value, kwds):
        ikiwa sio value:
            kwds['defects'].append(errors.HeaderMissingRequiredValue())
            kwds['datetime'] = Tupu
            kwds['decoded'] = ''
            kwds['parse_tree'] = parser.TokenList()
            return
        ikiwa isinstance(value, str):
            value = utils.parsedate_to_datetime(value)
        kwds['datetime'] = value
        kwds['decoded'] = utils.format_datetime(kwds['datetime'])
        kwds['parse_tree'] = cls.value_parser(kwds['decoded'])

    eleza init(self, *args, **kw):
        self._datetime = kw.pop('datetime')
        super().init(*args, **kw)

    @property
    eleza datetime(self):
        rudisha self._datetime


kundi UniqueDateHeader(DateHeader):

    max_count = 1


kundi AddressHeader:

    max_count = Tupu

    @staticmethod
    eleza value_parser(value):
        address_list, value = parser.get_address_list(value)
        assert sio value, 'this should sio happen'
        rudisha address_list

    @classmethod
    eleza parse(cls, value, kwds):
        ikiwa isinstance(value, str):
            # We are translating here kutoka the RFC language (address/mailbox)
            # to our API language (group/address).
            kwds['parse_tree'] = address_list = cls.value_parser(value)
            groups = []
            kila addr kwenye address_list.addresses:
                groups.append(Group(addr.display_name,
                                    [Address(mb.display_name ama '',
                                             mb.local_part ama '',
                                             mb.domain ama '')
                                     kila mb kwenye addr.all_mailboxes]))
            defects = list(address_list.all_defects)
        isipokua:
            # Assume it ni Address/Group stuff
            ikiwa sio hasattr(value, '__iter__'):
                value = [value]
            groups = [Group(Tupu, [item]) ikiwa sio hasattr(item, 'addresses')
                                          isipokua item
                                    kila item kwenye value]
            defects = []
        kwds['groups'] = groups
        kwds['defects'] = defects
        kwds['decoded'] = ', '.join([str(item) kila item kwenye groups])
        ikiwa 'parse_tree' haiko kwenye kwds:
            kwds['parse_tree'] = cls.value_parser(kwds['decoded'])

    eleza init(self, *args, **kw):
        self._groups = tuple(kw.pop('groups'))
        self._addresses = Tupu
        super().init(*args, **kw)

    @property
    eleza groups(self):
        rudisha self._groups

    @property
    eleza addresses(self):
        ikiwa self._addresses ni Tupu:
            self._addresses = tuple(address kila group kwenye self._groups
                                            kila address kwenye group.addresses)
        rudisha self._addresses


kundi UniqueAddressHeader(AddressHeader):

    max_count = 1


kundi SingleAddressHeader(AddressHeader):

    @property
    eleza address(self):
        ikiwa len(self.addresses)!=1:
            ashiria ValueError(("value of single address header {} ni sio "
                "a single address").format(self.name))
        rudisha self.addresses[0]


kundi UniqueSingleAddressHeader(SingleAddressHeader):

    max_count = 1


kundi MIMEVersionHeader:

    max_count = 1

    value_parser = staticmethod(parser.parse_mime_version)

    @classmethod
    eleza parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)
        kwds['major'] = Tupu ikiwa parse_tree.minor ni Tupu isipokua parse_tree.major
        kwds['minor'] = parse_tree.minor
        ikiwa parse_tree.minor ni sio Tupu:
            kwds['version'] = '{}.{}'.format(kwds['major'], kwds['minor'])
        isipokua:
            kwds['version'] = Tupu

    eleza init(self, *args, **kw):
        self._version = kw.pop('version')
        self._major = kw.pop('major')
        self._minor = kw.pop('minor')
        super().init(*args, **kw)

    @property
    eleza major(self):
        rudisha self._major

    @property
    eleza minor(self):
        rudisha self._minor

    @property
    eleza version(self):
        rudisha self._version


kundi ParameterizedMIMEHeader:

    # Mixin that handles the params dict.  Must be subclassed na
    # a property value_parser kila the specific header provided.

    max_count = 1

    @classmethod
    eleza parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)
        ikiwa parse_tree.params ni Tupu:
            kwds['params'] = {}
        isipokua:
            # The MIME RFCs specify that parameter ordering ni arbitrary.
            kwds['params'] = {utils._sanitize(name).lower():
                                    utils._sanitize(value)
                               kila name, value kwenye parse_tree.params}

    eleza init(self, *args, **kw):
        self._params = kw.pop('params')
        super().init(*args, **kw)

    @property
    eleza params(self):
        rudisha MappingProxyType(self._params)


kundi ContentTypeHeader(ParameterizedMIMEHeader):

    value_parser = staticmethod(parser.parse_content_type_header)

    eleza init(self, *args, **kw):
        super().init(*args, **kw)
        self._maintype = utils._sanitize(self._parse_tree.maintype)
        self._subtype = utils._sanitize(self._parse_tree.subtype)

    @property
    eleza maintype(self):
        rudisha self._maintype

    @property
    eleza subtype(self):
        rudisha self._subtype

    @property
    eleza content_type(self):
        rudisha self.maintype + '/' + self.subtype


kundi ContentDispositionHeader(ParameterizedMIMEHeader):

    value_parser = staticmethod(parser.parse_content_disposition_header)

    eleza init(self, *args, **kw):
        super().init(*args, **kw)
        cd = self._parse_tree.content_disposition
        self._content_disposition = cd ikiwa cd ni Tupu isipokua utils._sanitize(cd)

    @property
    eleza content_disposition(self):
        rudisha self._content_disposition


kundi ContentTransferEncodingHeader:

    max_count = 1

    value_parser = staticmethod(parser.parse_content_transfer_encoding_header)

    @classmethod
    eleza parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)

    eleza init(self, *args, **kw):
        super().init(*args, **kw)
        self._cte = utils._sanitize(self._parse_tree.cte)

    @property
    eleza cte(self):
        rudisha self._cte


kundi MessageIDHeader:

    max_count = 1
    value_parser = staticmethod(parser.parse_message_id)

    @classmethod
    eleza parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)


# The header factory #

_default_header_map = {
    'subject':                      UniqueUnstructuredHeader,
    'date':                         UniqueDateHeader,
    'resent-date':                  DateHeader,
    'orig-date':                    UniqueDateHeader,
    'sender':                       UniqueSingleAddressHeader,
    'resent-sender':                SingleAddressHeader,
    'to':                           UniqueAddressHeader,
    'resent-to':                    AddressHeader,
    'cc':                           UniqueAddressHeader,
    'resent-cc':                    AddressHeader,
    'bcc':                          UniqueAddressHeader,
    'resent-bcc':                   AddressHeader,
    'from':                         UniqueAddressHeader,
    'resent-from':                  AddressHeader,
    'reply-to':                     UniqueAddressHeader,
    'mime-version':                 MIMEVersionHeader,
    'content-type':                 ContentTypeHeader,
    'content-disposition':          ContentDispositionHeader,
    'content-transfer-encoding':    ContentTransferEncodingHeader,
    'message-id':                   MessageIDHeader,
    }

kundi HeaderRegisjaribu:

    """A header_factory na header registry."""

    eleza __init__(self, base_class=BaseHeader, default_class=UnstructuredHeader,
                       use_default_map=Kweli):
        """Create a header_factory that works ukijumuisha the Policy API.

        base_class ni the kundi that will be the last kundi kwenye the created
        header class's __bases__ list.  default_class ni the kundi that will be
        used ikiwa "name" (see __call__) does sio appear kwenye the registry.
        use_default_map controls whether ama sio the default mapping of names to
        specialized classes ni copied kwenye to the registry when the factory is
        created.  The default ni Kweli.

        """
        self.registry = {}
        self.base_class = base_class
        self.default_class = default_class
        ikiwa use_default_map:
            self.registry.update(_default_header_map)

    eleza map_to_type(self, name, cls):
        """Register cls kama the specialized kundi kila handling "name" headers.

        """
        self.registry[name.lower()] = cls

    eleza __getitem__(self, name):
        cls = self.registry.get(name.lower(), self.default_class)
        rudisha type('_'+cls.__name__, (cls, self.base_class), {})

    eleza __call__(self, name, value):
        """Create a header instance kila header 'name' kutoka 'value'.

        Creates a header instance by creating a specialized kundi kila parsing
        na representing the specified header by combining the factory
        base_class ukijumuisha a specialized kundi kutoka the registry ama the
        default_class, na pitaing the name na value to the constructed
        class's constructor.

        """
        rudisha self[name](name, value)
