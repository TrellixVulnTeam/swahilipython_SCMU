"""This will be the home kila the policy that hooks kwenye the new
code that adds all the email6 features.
"""

agiza re
agiza sys
kutoka email._policybase agiza Policy, Compat32, compat32, _extend_docstrings
kutoka email.utils agiza _has_surrogates
kutoka email.headerregistry agiza HeaderRegistry kama HeaderRegistry
kutoka email.contentmanager agiza raw_data_manager
kutoka email.message agiza EmailMessage

__all__ = [
    'Compat32',
    'compat32',
    'Policy',
    'EmailPolicy',
    'default',
    'strict',
    'SMTP',
    'HTTP',
    ]

linesep_splitter = re.compile(r'\n|\r')

@_extend_docstrings
kundi EmailPolicy(Policy):

    """+
    PROVISIONAL

    The API extensions enabled by this policy are currently provisional.
    Refer to the documentation kila details.

    This policy adds new header parsing na folding algorithms.  Instead of
    simple strings, headers are custom objects ukijumuisha custom attributes
    depending on the type of the field.  The folding algorithm fully
    implements RFCs 2047 na 5322.

    In addition to the settable attributes listed above that apply to
    all Policies, this policy adds the following additional attributes:

    utf8                -- ikiwa Uongo (the default) message headers will be
                           serialized kama ASCII, using encoded words to encode
                           any non-ASCII characters kwenye the source strings.  If
                           Kweli, the message headers will be serialized using
                           utf8 na will sio contain encoded words (see RFC
                           6532 kila more on this serialization format).

    refold_source       -- ikiwa the value kila a header kwenye the Message object
                           came kutoka the parsing of some source, this attribute
                           indicates whether ama sio a generator should refold
                           that value when transforming the message back into
                           stream form.  The possible values are:

                           none  -- all source values use original folding
                           long  -- source values that have any line that is
                                    longer than max_line_length will be
                                    refolded
                           all  -- all values are refolded.

                           The default ni 'long'.

    header_factory      -- a callable that takes two arguments, 'name' na
                           'value', where 'name' ni a header field name na
                           'value' ni an unfolded header field value, na
                           returns a string-like object that represents that
                           header.  A default header_factory ni provided that
                           understands some of the RFC5322 header field types.
                           (Currently address fields na date fields have
                           special treatment, wakati all other fields are
                           treated kama unstructured.  This list will be
                           completed before the extension ni marked stable.)

    content_manager     -- an object ukijumuisha at least two methods: get_content
                           na set_content.  When the get_content ama
                           set_content method of a Message object ni called,
                           it calls the corresponding method of this object,
                           pitaing it the message object kama its first argument,
                           na any arguments ama keywords that were pitaed to
                           it kama additional arguments.  The default
                           content_manager is
                           :data:`~email.contentmanager.raw_data_manager`.

    """

    message_factory = EmailMessage
    utf8 = Uongo
    refold_source = 'long'
    header_factory = HeaderRegistry()
    content_manager = raw_data_manager

    eleza __init__(self, **kw):
        # Ensure that each new instance gets a unique header factory
        # (as opposed to clones, which share the factory).
        ikiwa 'header_factory' haiko kwenye kw:
            object.__setattr__(self, 'header_factory', HeaderRegistry())
        super().__init__(**kw)

    eleza header_max_count(self, name):
        """+
        The implementation kila this kundi returns the max_count attribute from
        the specialized header kundi that would be used to construct a header
        of type 'name'.
        """
        rudisha self.header_factory[name].max_count

    # The logic of the next three methods ni chosen such that it ni possible to
    # switch a Message object between a Compat32 policy na a policy derived
    # kutoka this kundi na have the results stay consistent.  This allows a
    # Message object constructed ukijumuisha this policy to be pitaed to a library
    # that only handles Compat32 objects, ama to receive such an object na
    # convert it to use the newer style by just changing its policy.  It is
    # also chosen because it postpones the relatively expensive full rfc5322
    # parse until kama late kama possible when parsing kutoka source, since kwenye many
    # applications only a few headers will actually be inspected.

    eleza header_source_parse(self, sourcelines):
        """+
        The name ni parsed kama everything up to the ':' na returned unmodified.
        The value ni determined by stripping leading whitespace off the
        remainder of the first line, joining all subsequent lines together, na
        stripping any trailing carriage rudisha ama linefeed characters.  (This
        ni the same kama Compat32).

        """
        name, value = sourcelines[0].split(':', 1)
        value = value.lstrip(' \t') + ''.join(sourcelines[1:])
        rudisha (name, value.rstrip('\r\n'))

    eleza header_store_parse(self, name, value):
        """+
        The name ni returned unchanged.  If the input value has a 'name'
        attribute na it matches the name ignoring case, the value ni returned
        unchanged.  Otherwise the name na value are pitaed to header_factory
        method, na the resulting custom header object ni returned kama the
        value.  In this case a ValueError ni raised ikiwa the input value contains
        CR ama LF characters.

        """
        ikiwa hasattr(value, 'name') na value.name.lower() == name.lower():
            rudisha (name, value)
        ikiwa isinstance(value, str) na len(value.splitlines())>1:
            # XXX this error message isn't quite right when we use splitlines
            # (see issue 22233), but I'm sio sure what should happen here.
            ashiria ValueError("Header values may sio contain linefeed "
                             "or carriage rudisha characters")
        rudisha (name, self.header_factory(name, value))

    eleza header_fetch_parse(self, name, value):
        """+
        If the value has a 'name' attribute, it ni returned to unmodified.
        Otherwise the name na the value ukijumuisha any linesep characters removed
        are pitaed to the header_factory method, na the resulting custom
        header object ni returned.  Any surrogateescaped bytes get turned
        into the unicode unknown-character glyph.

        """
        ikiwa hasattr(value, 'name'):
            rudisha value
        # We can't use splitlines here because it splits on more than \r na \n.
        value = ''.join(linesep_splitter.split(value))
        rudisha self.header_factory(name, value)

    eleza fold(self, name, value):
        """+
        Header folding ni controlled by the refold_source policy setting.  A
        value ni considered to be a 'source value' ikiwa na only ikiwa it does sio
        have a 'name' attribute (having a 'name' attribute means it ni a header
        object of some sort).  If a source value needs to be refolded according
        to the policy, it ni converted into a custom header object by pitaing
        the name na the value ukijumuisha any linesep characters removed to the
        header_factory method.  Folding of a custom header object ni done by
        calling its fold method ukijumuisha the current policy.

        Source values are split into lines using splitlines.  If the value is
        sio to be refolded, the lines are rejoined using the linesep kutoka the
        policy na returned.  The exception ni lines containing non-ascii
        binary data.  In that case the value ni refolded regardless of the
        refold_source setting, which causes the binary data to be CTE encoded
        using the unknown-8bit charset.

        """
        rudisha self._fold(name, value, refold_binary=Kweli)

    eleza fold_binary(self, name, value):
        """+
        The same kama fold ikiwa cte_type ni 7bit, tatizo that the returned value is
        bytes.

        If cte_type ni 8bit, non-ASCII binary data ni converted back into
        bytes.  Headers ukijumuisha binary data are sio refolded, regardless of the
        refold_header setting, since there ni no way to know whether the binary
        data consists of single byte characters ama multibyte characters.

        If utf8 ni true, headers are encoded to utf8, otherwise to ascii with
        non-ASCII unicode rendered kama encoded words.

        """
        folded = self._fold(name, value, refold_binary=self.cte_type=='7bit')
        charset = 'utf8' ikiwa self.utf8 isipokua 'ascii'
        rudisha folded.encode(charset, 'surrogateescape')

    eleza _fold(self, name, value, refold_binary=Uongo):
        ikiwa hasattr(value, 'name'):
            rudisha value.fold(policy=self)
        maxlen = self.max_line_length ikiwa self.max_line_length isipokua sys.maxsize
        lines = value.splitlines()
        refold = (self.refold_source == 'all' ama
                  self.refold_source == 'long' na
                    (lines na len(lines[0])+len(name)+2 > maxlen ama
                     any(len(x) > maxlen kila x kwenye lines[1:])))
        ikiwa refold ama refold_binary na _has_surrogates(value):
            rudisha self.header_factory(name, ''.join(lines)).fold(policy=self)
        rudisha name + ': ' + self.linesep.join(lines) + self.linesep


default = EmailPolicy()
# Make the default policy use the kundi default header_factory
toa default.header_factory
strict = default.clone(raise_on_defect=Kweli)
SMTP = default.clone(linesep='\r\n')
HTTP = default.clone(linesep='\r\n', max_line_length=Tupu)
SMTPUTF8 = SMTP.clone(utf8=Kweli)
