"""Header value parser implementing various email-related RFC parsing rules.

The parsing methods defined kwenye this module implement various email related
parsing rules.  Principal among them ni RFC 5322, which ni the followon
to RFC 2822 na primarily a clarification of the former.  It also implements
RFC 2047 encoded word decoding.

RFC 5322 goes to considerable trouble to maintain backward compatibility with
RFC 822 kwenye the parse phase, wakati cleaning up the structure on the generation
phase.  This parser supports correct RFC 5322 generation by tagging white space
as folding white space only when folding ni allowed kwenye the non-obsolete rule
sets.  Actually, the parser ni even more generous when accepting input than RFC
5322 mandates, following the spirit of Postel's Law, which RFC 5322 encourages.
Where possible deviations kutoka the standard are annotated on the 'defects'
attribute of tokens that deviate.

The general structure of the parser follows RFC 5322, na uses its terminology
where there ni a direct correspondence.  Where the implementation requires a
somewhat different structure than that used by the formal grammar, new terms
that mimic the closest existing terms are used.  Thus, it really helps to have
a copy of RFC 5322 handy when studying this code.

Input to the parser ni a string that has already been unfolded according to
RFC 5322 rules.  According to the RFC this unfolding ni the very first step, na
this parser leaves the unfolding step to a higher level message parser, which
will have already detected the line komas that need unfolding while
determining the beginning na end of each header.

The output of the parser ni a TokenList object, which ni a list subclass.  A
TokenList ni a recursive data structure.  The terminal nodes of the structure
are Terminal objects, which are subclasses of str.  These do sio correspond
directly to terminal objects kwenye the formal grammar, but are instead more
practical higher level combinations of true terminals.

All TokenList na Terminal objects have a 'value' attribute, which produces the
semantically meaningful value of that part of the parse subtree.  The value of
all whitespace tokens (no matter how many sub-tokens they may contain) ni a
single space, kama per the RFC rules.  This includes 'CFWS', which ni herein
included kwenye the general kundi of whitespace tokens.  There ni one exception to
the rule that whitespace tokens are collapsed into single spaces kwenye values: in
the value of a 'bare-quoted-string' (a quoted-string ukijumuisha no leading ama
trailing whitespace), any whitespace that appeared between the quotation marks
is preserved kwenye the returned value.  Note that kwenye all Terminal strings quoted
pairs are turned into their unquoted values.

All TokenList na Terminal objects also have a string value, which attempts to
be a "canonical" representation of the RFC-compliant form of the substring that
produced the parsed subtree, including minimal use of quoted pair quoting.
Whitespace runs are sio collapsed.

Comment tokens also have a 'content' attribute providing the string found
between the parens (including any nested comments) ukijumuisha whitespace preserved.

All TokenList na Terminal objects have a 'defects' attribute which ni a
possibly empty list all of the defects found wakati creating the token.  Defects
may appear on any token kwenye the tree, na a composite list of all defects kwenye the
subtree ni available through the 'all_defects' attribute of any node.  (For
Terminal notes x.defects == x.all_defects.)

Each object kwenye a parse tree ni called a 'token', na each has a 'token_type'
attribute that gives the name kutoka the RFC 5322 grammar that it represents.
Not all RFC 5322 nodes are produced, na there ni one non-RFC 5322 node that
may be produced: 'ptext'.  A 'ptext' ni a string of printable ascii characters.
It ni returned kwenye place of lists of (ctext/quoted-pair) na
(qtext/quoted-pair).

XXX: provide complete list of token types.
"""

agiza re
agiza sys
agiza urllib   # For urllib.parse.unquote
kutoka string agiza hexdigits
kutoka operator agiza itemgetter
kutoka email agiza _encoded_words kama _ew
kutoka email agiza errors
kutoka email agiza utils

#
# Useful constants na functions
#

WSP = set(' \t')
CFWS_LEADER = WSP | set('(')
SPECIALS = set(r'()<>@,:;.\"[]')
ATOM_ENDS = SPECIALS | WSP
DOT_ATOM_ENDS = ATOM_ENDS - set('.')
# '.', '"', na '(' do sio end phrases kwenye order to support obs-phrase
PHRASE_ENDS = SPECIALS - set('."(')
TSPECIALS = (SPECIALS | set('/?=')) - set('.')
TOKEN_ENDS = TSPECIALS | WSP
ASPECIALS = TSPECIALS | set("*'%")
ATTRIBUTE_ENDS = ASPECIALS | WSP
EXTENDED_ATTRIBUTE_ENDS = ATTRIBUTE_ENDS - set('%')

eleza quote_string(value):
    rudisha '"'+str(value).replace('\\', '\\\\').replace('"', r'\"')+'"'

# Match a RFC 2047 word, looks like =?utf-8?q?someword?=
rfc2047_matcher = re.compile(r'''
   =\?            # literal =?
   [^?]*          # charset
   \?             # literal ?
   [qQbB]         # literal 'q' ama 'b', case insensitive
   \?             # literal ?
  .*?             # encoded word
  \?=             # literal ?=
''', re.VERBOSE | re.MULTILINE)


#
# TokenList na its subclasses
#

kundi TokenList(list):

    token_type = Tupu
    syntactic_koma = Kweli
    ew_combine_allowed = Kweli

    eleza __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.defects = []

    eleza __str__(self):
        rudisha ''.join(str(x) kila x kwenye self)

    eleza __repr__(self):
        rudisha '{}({})'.format(self.__class__.__name__,
                             super().__repr__())

    @property
    eleza value(self):
        rudisha ''.join(x.value kila x kwenye self ikiwa x.value)

    @property
    eleza all_defects(self):
        rudisha sum((x.all_defects kila x kwenye self), self.defects)

    eleza startswith_fws(self):
        rudisha self[0].startswith_fws()

    @property
    eleza as_ew_allowed(self):
        """Kweli ikiwa all top level tokens of this part may be RFC2047 encoded."""
        rudisha all(part.as_ew_allowed kila part kwenye self)

    @property
    eleza comments(self):
        comments = []
        kila token kwenye self:
            comments.extend(token.comments)
        rudisha comments

    eleza fold(self, *, policy):
        rudisha _refold_parse_tree(self, policy=policy)

    eleza pandika(self, indent=''):
        andika(self.ppstr(indent=indent))

    eleza ppstr(self, indent=''):
        rudisha '\n'.join(self._pp(indent=indent))

    eleza _pp(self, indent=''):
        tuma '{}{}/{}('.format(
            indent,
            self.__class__.__name__,
            self.token_type)
        kila token kwenye self:
            ikiwa sio hasattr(token, '_pp'):
                tuma (indent + '    !! invalid element kwenye token '
                                        'list: {!r}'.format(token))
            isipokua:
                tuma kutoka token._pp(indent+'    ')
        ikiwa self.defects:
            extra = ' Defects: {}'.format(self.defects)
        isipokua:
            extra = ''
        tuma '{}){}'.format(indent, extra)


kundi WhiteSpaceTokenList(TokenList):

    @property
    eleza value(self):
        rudisha ' '

    @property
    eleza comments(self):
        rudisha [x.content kila x kwenye self ikiwa x.token_type=='comment']


kundi UnstructuredTokenList(TokenList):
    token_type = 'unstructured'


kundi Phrase(TokenList):
    token_type = 'phrase'

kundi Word(TokenList):
    token_type = 'word'


kundi CFWSList(WhiteSpaceTokenList):
    token_type = 'cfws'


kundi Atom(TokenList):
    token_type = 'atom'


kundi Token(TokenList):
    token_type = 'token'
    encode_as_ew = Uongo


kundi EncodedWord(TokenList):
    token_type = 'encoded-word'
    cte = Tupu
    charset = Tupu
    lang = Tupu


kundi QuotedString(TokenList):

    token_type = 'quoted-string'

    @property
    eleza content(self):
        kila x kwenye self:
            ikiwa x.token_type == 'bare-quoted-string':
                rudisha x.value

    @property
    eleza quoted_value(self):
        res = []
        kila x kwenye self:
            ikiwa x.token_type == 'bare-quoted-string':
                res.append(str(x))
            isipokua:
                res.append(x.value)
        rudisha ''.join(res)

    @property
    eleza stripped_value(self):
        kila token kwenye self:
            ikiwa token.token_type == 'bare-quoted-string':
                rudisha token.value


kundi BareQuotedString(QuotedString):

    token_type = 'bare-quoted-string'

    eleza __str__(self):
        rudisha quote_string(''.join(str(x) kila x kwenye self))

    @property
    eleza value(self):
        rudisha ''.join(str(x) kila x kwenye self)


kundi Comment(WhiteSpaceTokenList):

    token_type = 'comment'

    eleza __str__(self):
        rudisha ''.join(sum([
                            ["("],
                            [self.quote(x) kila x kwenye self],
                            [")"],
                            ], []))

    eleza quote(self, value):
        ikiwa value.token_type == 'comment':
            rudisha str(value)
        rudisha str(value).replace('\\', '\\\\').replace(
                                  '(', r'\(').replace(
                                  ')', r'\)')

    @property
    eleza content(self):
        rudisha ''.join(str(x) kila x kwenye self)

    @property
    eleza comments(self):
        rudisha [self.content]

kundi AddressList(TokenList):

    token_type = 'address-list'

    @property
    eleza addresses(self):
        rudisha [x kila x kwenye self ikiwa x.token_type=='address']

    @property
    eleza mailboxes(self):
        rudisha sum((x.mailboxes
                    kila x kwenye self ikiwa x.token_type=='address'), [])

    @property
    eleza all_mailboxes(self):
        rudisha sum((x.all_mailboxes
                    kila x kwenye self ikiwa x.token_type=='address'), [])


kundi Address(TokenList):

    token_type = 'address'

    @property
    eleza display_name(self):
        ikiwa self[0].token_type == 'group':
            rudisha self[0].display_name

    @property
    eleza mailboxes(self):
        ikiwa self[0].token_type == 'mailbox':
            rudisha [self[0]]
        lasivyo self[0].token_type == 'invalid-mailbox':
            rudisha []
        rudisha self[0].mailboxes

    @property
    eleza all_mailboxes(self):
        ikiwa self[0].token_type == 'mailbox':
            rudisha [self[0]]
        lasivyo self[0].token_type == 'invalid-mailbox':
            rudisha [self[0]]
        rudisha self[0].all_mailboxes

kundi MailboxList(TokenList):

    token_type = 'mailbox-list'

    @property
    eleza mailboxes(self):
        rudisha [x kila x kwenye self ikiwa x.token_type=='mailbox']

    @property
    eleza all_mailboxes(self):
        rudisha [x kila x kwenye self
            ikiwa x.token_type kwenye ('mailbox', 'invalid-mailbox')]


kundi GroupList(TokenList):

    token_type = 'group-list'

    @property
    eleza mailboxes(self):
        ikiwa sio self ama self[0].token_type != 'mailbox-list':
            rudisha []
        rudisha self[0].mailboxes

    @property
    eleza all_mailboxes(self):
        ikiwa sio self ama self[0].token_type != 'mailbox-list':
            rudisha []
        rudisha self[0].all_mailboxes


kundi Group(TokenList):

    token_type = "group"

    @property
    eleza mailboxes(self):
        ikiwa self[2].token_type != 'group-list':
            rudisha []
        rudisha self[2].mailboxes

    @property
    eleza all_mailboxes(self):
        ikiwa self[2].token_type != 'group-list':
            rudisha []
        rudisha self[2].all_mailboxes

    @property
    eleza display_name(self):
        rudisha self[0].display_name


kundi NameAddr(TokenList):

    token_type = 'name-addr'

    @property
    eleza display_name(self):
        ikiwa len(self) == 1:
            rudisha Tupu
        rudisha self[0].display_name

    @property
    eleza local_part(self):
        rudisha self[-1].local_part

    @property
    eleza domain(self):
        rudisha self[-1].domain

    @property
    eleza route(self):
        rudisha self[-1].route

    @property
    eleza addr_spec(self):
        rudisha self[-1].addr_spec


kundi AngleAddr(TokenList):

    token_type = 'angle-addr'

    @property
    eleza local_part(self):
        kila x kwenye self:
            ikiwa x.token_type == 'addr-spec':
                rudisha x.local_part

    @property
    eleza domain(self):
        kila x kwenye self:
            ikiwa x.token_type == 'addr-spec':
                rudisha x.domain

    @property
    eleza route(self):
        kila x kwenye self:
            ikiwa x.token_type == 'obs-route':
                rudisha x.domains

    @property
    eleza addr_spec(self):
        kila x kwenye self:
            ikiwa x.token_type == 'addr-spec':
                ikiwa x.local_part:
                    rudisha x.addr_spec
                isipokua:
                    rudisha quote_string(x.local_part) + x.addr_spec
        isipokua:
            rudisha '<>'


kundi ObsRoute(TokenList):

    token_type = 'obs-route'

    @property
    eleza domains(self):
        rudisha [x.domain kila x kwenye self ikiwa x.token_type == 'domain']


kundi Mailbox(TokenList):

    token_type = 'mailbox'

    @property
    eleza display_name(self):
        ikiwa self[0].token_type == 'name-addr':
            rudisha self[0].display_name

    @property
    eleza local_part(self):
        rudisha self[0].local_part

    @property
    eleza domain(self):
        rudisha self[0].domain

    @property
    eleza route(self):
        ikiwa self[0].token_type == 'name-addr':
            rudisha self[0].route

    @property
    eleza addr_spec(self):
        rudisha self[0].addr_spec


kundi InvalidMailbox(TokenList):

    token_type = 'invalid-mailbox'

    @property
    eleza display_name(self):
        rudisha Tupu

    local_part = domain = route = addr_spec = display_name


kundi Domain(TokenList):

    token_type = 'domain'
    as_ew_allowed = Uongo

    @property
    eleza domain(self):
        rudisha ''.join(super().value.split())


kundi DotAtom(TokenList):
    token_type = 'dot-atom'


kundi DotAtomText(TokenList):
    token_type = 'dot-atom-text'
    as_ew_allowed = Kweli


kundi NoFoldLiteral(TokenList):
    token_type = 'no-fold-literal'
    as_ew_allowed = Uongo


kundi AddrSpec(TokenList):

    token_type = 'addr-spec'
    as_ew_allowed = Uongo

    @property
    eleza local_part(self):
        rudisha self[0].local_part

    @property
    eleza domain(self):
        ikiwa len(self) < 3:
            rudisha Tupu
        rudisha self[-1].domain

    @property
    eleza value(self):
        ikiwa len(self) < 3:
            rudisha self[0].value
        rudisha self[0].value.rstrip()+self[1].value+self[2].value.lstrip()

    @property
    eleza addr_spec(self):
        nameset = set(self.local_part)
        ikiwa len(nameset) > len(nameset-DOT_ATOM_ENDS):
            lp = quote_string(self.local_part)
        isipokua:
            lp = self.local_part
        ikiwa self.domain ni sio Tupu:
            rudisha lp + '@' + self.domain
        rudisha lp


kundi ObsLocalPart(TokenList):

    token_type = 'obs-local-part'
    as_ew_allowed = Uongo


kundi DisplayName(Phrase):

    token_type = 'display-name'
    ew_combine_allowed = Uongo

    @property
    eleza display_name(self):
        res = TokenList(self)
        ikiwa len(res) == 0:
            rudisha res.value
        ikiwa res[0].token_type == 'cfws':
            res.pop(0)
        isipokua:
            ikiwa res[0][0].token_type == 'cfws':
                res[0] = TokenList(res[0][1:])
        ikiwa res[-1].token_type == 'cfws':
            res.pop()
        isipokua:
            ikiwa res[-1][-1].token_type == 'cfws':
                res[-1] = TokenList(res[-1][:-1])
        rudisha res.value

    @property
    eleza value(self):
        quote = Uongo
        ikiwa self.defects:
            quote = Kweli
        isipokua:
            kila x kwenye self:
                ikiwa x.token_type == 'quoted-string':
                    quote = Kweli
        ikiwa len(self) != 0 na quote:
            pre = post = ''
            ikiwa self[0].token_type=='cfws' ama self[0][0].token_type=='cfws':
                pre = ' '
            ikiwa self[-1].token_type=='cfws' ama self[-1][-1].token_type=='cfws':
                post = ' '
            rudisha pre+quote_string(self.display_name)+post
        isipokua:
            rudisha super().value


kundi LocalPart(TokenList):

    token_type = 'local-part'
    as_ew_allowed = Uongo

    @property
    eleza value(self):
        ikiwa self[0].token_type == "quoted-string":
            rudisha self[0].quoted_value
        isipokua:
            rudisha self[0].value

    @property
    eleza local_part(self):
        # Strip whitespace kutoka front, back, na around dots.
        res = [DOT]
        last = DOT
        last_is_tl = Uongo
        kila tok kwenye self[0] + [DOT]:
            ikiwa tok.token_type == 'cfws':
                endelea
            ikiwa (last_is_tl na tok.token_type == 'dot' na
                    last[-1].token_type == 'cfws'):
                res[-1] = TokenList(last[:-1])
            is_tl = isinstance(tok, TokenList)
            ikiwa (is_tl na last.token_type == 'dot' na
                    tok[0].token_type == 'cfws'):
                res.append(TokenList(tok[1:]))
            isipokua:
                res.append(tok)
            last = res[-1]
            last_is_tl = is_tl
        res = TokenList(res[1:-1])
        rudisha res.value


kundi DomainLiteral(TokenList):

    token_type = 'domain-literal'
    as_ew_allowed = Uongo

    @property
    eleza domain(self):
        rudisha ''.join(super().value.split())

    @property
    eleza ip(self):
        kila x kwenye self:
            ikiwa x.token_type == 'ptext':
                rudisha x.value


kundi MIMEVersion(TokenList):

    token_type = 'mime-version'
    major = Tupu
    minor = Tupu


kundi Parameter(TokenList):

    token_type = 'parameter'
    sectioned = Uongo
    extended = Uongo
    charset = 'us-ascii'

    @property
    eleza section_number(self):
        # Because the first token, the attribute (name) eats CFWS, the second
        # token ni always the section ikiwa there ni one.
        rudisha self[1].number ikiwa self.sectioned isipokua 0

    @property
    eleza param_value(self):
        # This ni part of the "handle quoted extended parameters" hack.
        kila token kwenye self:
            ikiwa token.token_type == 'value':
                rudisha token.stripped_value
            ikiwa token.token_type == 'quoted-string':
                kila token kwenye token:
                    ikiwa token.token_type == 'bare-quoted-string':
                        kila token kwenye token:
                            ikiwa token.token_type == 'value':
                                rudisha token.stripped_value
        rudisha ''


kundi InvalidParameter(Parameter):

    token_type = 'invalid-parameter'


kundi Attribute(TokenList):

    token_type = 'attribute'

    @property
    eleza stripped_value(self):
        kila token kwenye self:
            ikiwa token.token_type.endswith('attrtext'):
                rudisha token.value

kundi Section(TokenList):

    token_type = 'section'
    number = Tupu


kundi Value(TokenList):

    token_type = 'value'

    @property
    eleza stripped_value(self):
        token = self[0]
        ikiwa token.token_type == 'cfws':
            token = self[1]
        ikiwa token.token_type.endswith(
                ('quoted-string', 'attribute', 'extended-attribute')):
            rudisha token.stripped_value
        rudisha self.value


kundi MimeParameters(TokenList):

    token_type = 'mime-parameters'
    syntactic_koma = Uongo

    @property
    eleza params(self):
        # The RFC specifically states that the ordering of parameters ni not
        # guaranteed na may be reordered by the transport layer.  So we have
        # to assume the RFC 2231 pieces can come kwenye any order.  However, we
        # output them kwenye the order that we first see a given name, which gives
        # us a stable __str__.
        params = {}  # Using order preserving dict kutoka Python 3.7+
        kila token kwenye self:
            ikiwa sio token.token_type.endswith('parameter'):
                endelea
            ikiwa token[0].token_type != 'attribute':
                endelea
            name = token[0].value.strip()
            ikiwa name haiko kwenye params:
                params[name] = []
            params[name].append((token.section_number, token))
        kila name, parts kwenye params.items():
            parts = sorted(parts, key=itemgetter(0))
            first_param = parts[0][1]
            charset = first_param.charset
            # Our arbitrary error recovery ni to ignore duplicate parameters,
            # to use appearance order ikiwa there are duplicate rfc 2231 parts,
            # na to ignore gaps.  This mimics the error recovery of get_param.
            ikiwa sio first_param.extended na len(parts) > 1:
                ikiwa parts[1][0] == 0:
                    parts[1][1].defects.append(errors.InvalidHeaderDefect(
                        'duplicate parameter name; duplicate(s) ignored'))
                    parts = parts[:1]
                # Else assume the *0* was missing...note that this ni different
                # kutoka get_param, but we registered a defect kila this earlier.
            value_parts = []
            i = 0
            kila section_number, param kwenye parts:
                ikiwa section_number != i:
                    # We could get fancier here na look kila a complete
                    # duplicate extended parameter na ignore the second one
                    # seen.  But we're sio doing that.  The old code didn't.
                    ikiwa sio param.extended:
                        param.defects.append(errors.InvalidHeaderDefect(
                            'duplicate parameter name; duplicate ignored'))
                        endelea
                    isipokua:
                        param.defects.append(errors.InvalidHeaderDefect(
                            "inconsistent RFC2231 parameter numbering"))
                i += 1
                value = param.param_value
                ikiwa param.extended:
                    jaribu:
                        value = urllib.parse.unquote_to_bytes(value)
                    tatizo UnicodeEncodeError:
                        # source had surrogate escaped bytes.  What we do now
                        # ni a bit of an open question.  I'm sio sure this is
                        # the best choice, but it ni what the old algorithm did
                        value = urllib.parse.unquote(value, encoding='latin-1')
                    isipokua:
                        jaribu:
                            value = value.decode(charset, 'surrogateescape')
                        tatizo LookupError:
                            # XXX: there should really be a custom defect for
                            # unknown character set to make it easy to find,
                            # because otherwise unknown charset ni a silent
                            # failure.
                            value = value.decode('us-ascii', 'surrogateescape')
                        ikiwa utils._has_surrogates(value):
                            param.defects.append(errors.UndecodableBytesDefect())
                value_parts.append(value)
            value = ''.join(value_parts)
            tuma name, value

    eleza __str__(self):
        params = []
        kila name, value kwenye self.params:
            ikiwa value:
                params.append('{}={}'.format(name, quote_string(value)))
            isipokua:
                params.append(name)
        params = '; '.join(params)
        rudisha ' ' + params ikiwa params isipokua ''


kundi ParameterizedHeaderValue(TokenList):

    # Set this false so that the value doesn't wind up on a new line even
    # ikiwa it na the parameters would fit there but sio on the first line.
    syntactic_koma = Uongo

    @property
    eleza params(self):
        kila token kwenye reversed(self):
            ikiwa token.token_type == 'mime-parameters':
                rudisha token.params
        rudisha {}


kundi ContentType(ParameterizedHeaderValue):
    token_type = 'content-type'
    as_ew_allowed = Uongo
    maintype = 'text'
    subtype = 'plain'


kundi ContentDisposition(ParameterizedHeaderValue):
    token_type = 'content-disposition'
    as_ew_allowed = Uongo
    content_disposition = Tupu


kundi ContentTransferEncoding(TokenList):
    token_type = 'content-transfer-encoding'
    as_ew_allowed = Uongo
    cte = '7bit'


kundi HeaderLabel(TokenList):
    token_type = 'header-label'
    as_ew_allowed = Uongo


kundi MsgID(TokenList):
    token_type = 'msg-id'
    as_ew_allowed = Uongo

    eleza fold(self, policy):
        # message-id tokens may sio be folded.
        rudisha str(self) + policy.linesep

kundi MessageID(MsgID):
    token_type = 'message-id'


kundi Header(TokenList):
    token_type = 'header'


#
# Terminal classes na instances
#

kundi Terminal(str):

    as_ew_allowed = Kweli
    ew_combine_allowed = Kweli
    syntactic_koma = Kweli

    eleza __new__(cls, value, token_type):
        self = super().__new__(cls, value)
        self.token_type = token_type
        self.defects = []
        rudisha self

    eleza __repr__(self):
        rudisha "{}({})".format(self.__class__.__name__, super().__repr__())

    eleza pandika(self):
        andika(self.__class__.__name__ + '/' + self.token_type)

    @property
    eleza all_defects(self):
        rudisha list(self.defects)

    eleza _pp(self, indent=''):
        rudisha ["{}{}/{}({}){}".format(
            indent,
            self.__class__.__name__,
            self.token_type,
            super().__repr__(),
            '' ikiwa sio self.defects isipokua ' {}'.format(self.defects),
            )]

    eleza pop_trailing_ws(self):
        # This terminates the recursion.
        rudisha Tupu

    @property
    eleza comments(self):
        rudisha []

    eleza __getnewargs__(self):
        return(str(self), self.token_type)


kundi WhiteSpaceTerminal(Terminal):

    @property
    eleza value(self):
        rudisha ' '

    eleza startswith_fws(self):
        rudisha Kweli


kundi ValueTerminal(Terminal):

    @property
    eleza value(self):
        rudisha self

    eleza startswith_fws(self):
        rudisha Uongo


kundi EWWhiteSpaceTerminal(WhiteSpaceTerminal):

    @property
    eleza value(self):
        rudisha ''

    eleza __str__(self):
        rudisha ''


kundi _InvalidEwError(errors.HeaderParseError):
    """Invalid encoded word found wakati parsing headers."""


# XXX these need to become classes na used kama instances so
# that a program can't change them kwenye a parse tree na screw
# up other parse trees.  Maybe should have  tests kila that, too.
DOT = ValueTerminal('.', 'dot')
ListSeparator = ValueTerminal(',', 'list-separator')
RouteComponentMarker = ValueTerminal('@', 'route-component-marker')

#
# Parser
#

# Parse strings according to RFC822/2047/2822/5322 rules.
#
# This ni a stateless parser.  Each get_XXX function accepts a string na
# returns either a Terminal ama a TokenList representing the RFC object named
# by the method na a string containing the remaining unparsed characters
# kutoka the input.  Thus a parser method consumes the next syntactic construct
# of a given type na returns a token representing the construct plus the
# unparsed remainder of the input string.
#
# For example, ikiwa the first element of a structured header ni a 'phrase',
# then:
#
#     phrase, value = get_phrase(value)
#
# returns the complete phrase kutoka the start of the string value, plus any
# characters left kwenye the string after the phrase ni removed.

_wsp_splitter = re.compile(r'([{}]+)'.format(''.join(WSP))).split
_non_atom_end_matcher = re.compile(r"[^{}]+".format(
    re.escape(''.join(ATOM_ENDS)))).match
_non_printable_finder = re.compile(r"[\x00-\x20\x7F]").findall
_non_token_end_matcher = re.compile(r"[^{}]+".format(
    re.escape(''.join(TOKEN_ENDS)))).match
_non_attribute_end_matcher = re.compile(r"[^{}]+".format(
    re.escape(''.join(ATTRIBUTE_ENDS)))).match
_non_extended_attribute_end_matcher = re.compile(r"[^{}]+".format(
    re.escape(''.join(EXTENDED_ATTRIBUTE_ENDS)))).match

eleza _validate_xtext(xtext):
    """If input token contains ASCII non-printables, register a defect."""

    non_printables = _non_printable_finder(xtext)
    ikiwa non_printables:
        xtext.defects.append(errors.NonPrintableDefect(non_printables))
    ikiwa utils._has_surrogates(xtext):
        xtext.defects.append(errors.UndecodableBytesDefect(
            "Non-ASCII characters found kwenye header token"))

eleza _get_ptext_to_endchars(value, endchars):
    """Scan printables/quoted-pairs until endchars na rudisha unquoted ptext.

    This function turns a run of qcontent, ccontent-without-comments, ama
    dtext-with-quoted-printables into a single string by unquoting any
    quoted printables.  It returns the string, the remaining value, na
    a flag that ni Kweli iff there were any quoted printables decoded.

    """
    fragment, *remainder = _wsp_splitter(value, 1)
    vchars = []
    escape = Uongo
    had_qp = Uongo
    kila pos kwenye range(len(fragment)):
        ikiwa fragment[pos] == '\\':
            ikiwa escape:
                escape = Uongo
                had_qp = Kweli
            isipokua:
                escape = Kweli
                endelea
        ikiwa escape:
            escape = Uongo
        lasivyo fragment[pos] kwenye endchars:
            koma
        vchars.append(fragment[pos])
    isipokua:
        pos = pos + 1
    rudisha ''.join(vchars), ''.join([fragment[pos:]] + remainder), had_qp

eleza get_fws(value):
    """FWS = 1*WSP

    This isn't the RFC definition.  We're using fws to represent tokens where
    folding can be done, but when we are parsing the *un*folding has already
    been done so we don't need to watch out kila CRLF.

    """
    newvalue = value.lstrip()
    fws = WhiteSpaceTerminal(value[:len(value)-len(newvalue)], 'fws')
    rudisha fws, newvalue

eleza get_encoded_word(value):
    """ encoded-word = "=?" charset "?" encoding "?" encoded-text "?="

    """
    ew = EncodedWord()
    ikiwa sio value.startswith('=?'):
        ashiria errors.HeaderParseError(
            "expected encoded word but found {}".format(value))
    tok, *remainder = value[2:].split('?=', 1)
    ikiwa tok == value[2:]:
        ashiria errors.HeaderParseError(
            "expected encoded word but found {}".format(value))
    remstr = ''.join(remainder)
    ikiwa (len(remstr) > 1 na
        remstr[0] kwenye hexdigits na
        remstr[1] kwenye hexdigits na
        tok.count('?') < 2):
        # The ? after the CTE was followed by an encoded word escape (=XX).
        rest, *remainder = remstr.split('?=', 1)
        tok = tok + '?=' + rest
    ikiwa len(tok.split()) > 1:
        ew.defects.append(errors.InvalidHeaderDefect(
            "whitespace inside encoded word"))
    ew.cte = value
    value = ''.join(remainder)
    jaribu:
        text, charset, lang, defects = _ew.decode('=?' + tok + '?=')
    tatizo (ValueError, KeyError):
        ashiria _InvalidEwError(
            "encoded word format invalid: '{}'".format(ew.cte))
    ew.charset = charset
    ew.lang = lang
    ew.defects.extend(defects)
    wakati text:
        ikiwa text[0] kwenye WSP:
            token, text = get_fws(text)
            ew.append(token)
            endelea
        chars, *remainder = _wsp_splitter(text, 1)
        vtext = ValueTerminal(chars, 'vtext')
        _validate_xtext(vtext)
        ew.append(vtext)
        text = ''.join(remainder)
    # Encoded words should be followed by a WS
    ikiwa value na value[0] haiko kwenye WSP:
        ew.defects.append(errors.InvalidHeaderDefect(
            "missing trailing whitespace after encoded-word"))
    rudisha ew, value

eleza get_unstructured(value):
    """unstructured = (*([FWS] vchar) *WSP) / obs-unstruct
       obs-unstruct = *((*LF *CR *(obs-utext) *LF *CR)) / FWS)
       obs-utext = %d0 / obs-NO-WS-CTL / LF / CR

       obs-NO-WS-CTL ni control characters tatizo WSP/CR/LF.

    So, basically, we have printable runs, plus control characters ama nulls in
    the obsolete syntax, separated by whitespace.  Since RFC 2047 uses the
    obsolete syntax kwenye its specification, but requires whitespace on either
    side of the encoded words, I can see no reason to need to separate the
    non-printable-non-whitespace kutoka the printable runs ikiwa they occur, so we
    parse this into xtext tokens separated by WSP tokens.

    Because an 'unstructured' value must by definition constitute the entire
    value, this 'get' routine does sio rudisha a remaining value, only the
    parsed TokenList.

    """
    # XXX: but what about bare CR na LF?  They might signal the start ama
    # end of an encoded word.  YAGNI kila now, since our current parsers
    # will never send us strings ukijumuisha bare CR ama LF.

    unstructured = UnstructuredTokenList()
    wakati value:
        ikiwa value[0] kwenye WSP:
            token, value = get_fws(value)
            unstructured.append(token)
            endelea
        valid_ew = Kweli
        ikiwa value.startswith('=?'):
            jaribu:
                token, value = get_encoded_word(value)
            tatizo _InvalidEwError:
                valid_ew = Uongo
            tatizo errors.HeaderParseError:
                # XXX: Need to figure out how to register defects when
                # appropriate here.
                pita
            isipokua:
                have_ws = Kweli
                ikiwa len(unstructured) > 0:
                    ikiwa unstructured[-1].token_type != 'fws':
                        unstructured.defects.append(errors.InvalidHeaderDefect(
                            "missing whitespace before encoded word"))
                        have_ws = Uongo
                ikiwa have_ws na len(unstructured) > 1:
                    ikiwa unstructured[-2].token_type == 'encoded-word':
                        unstructured[-1] = EWWhiteSpaceTerminal(
                            unstructured[-1], 'fws')
                unstructured.append(token)
                endelea
        tok, *remainder = _wsp_splitter(value, 1)
        # Split kwenye the middle of an atom ikiwa there ni a rfc2047 encoded word
        # which does sio have WSP on both sides. The defect will be registered
        # the next time through the loop.
        # This needs to only be performed when the encoded word ni valid;
        # otherwise, performing it on an invalid encoded word can cause
        # the parser to go kwenye an infinite loop.
        ikiwa valid_ew na rfc2047_matcher.search(tok):
            tok, *remainder = value.partition('=?')
        vtext = ValueTerminal(tok, 'vtext')
        _validate_xtext(vtext)
        unstructured.append(vtext)
        value = ''.join(remainder)
    rudisha unstructured

eleza get_qp_ctext(value):
    r"""ctext = <printable ascii tatizo \ ( )>

    This ni sio the RFC ctext, since we are handling nested comments kwenye comment
    na unquoting quoted-pairs here.  We allow anything tatizo the '()'
    characters, but ikiwa we find any ASCII other than the RFC defined printable
    ASCII, a NonPrintableDefect ni added to the token's defects list.  Since
    quoted pairs are converted to their unquoted values, what ni returned is
    a 'ptext' token.  In this case it ni a WhiteSpaceTerminal, so it's value
    ni ' '.

    """
    ptext, value, _ = _get_ptext_to_endchars(value, '()')
    ptext = WhiteSpaceTerminal(ptext, 'ptext')
    _validate_xtext(ptext)
    rudisha ptext, value

eleza get_qcontent(value):
    """qcontent = qtext / quoted-pair

    We allow anything tatizo the DQUOTE character, but ikiwa we find any ASCII
    other than the RFC defined printable ASCII, a NonPrintableDefect is
    added to the token's defects list.  Any quoted pairs are converted to their
    unquoted values, so what ni returned ni a 'ptext' token.  In this case it
    ni a ValueTerminal.

    """
    ptext, value, _ = _get_ptext_to_endchars(value, '"')
    ptext = ValueTerminal(ptext, 'ptext')
    _validate_xtext(ptext)
    rudisha ptext, value

eleza get_atext(value):
    """atext = <matches _atext_matcher>

    We allow any non-ATOM_ENDS kwenye atext, but add an InvalidATextDefect to
    the token's defects list ikiwa we find non-atext characters.
    """
    m = _non_atom_end_matcher(value)
    ikiwa sio m:
        ashiria errors.HeaderParseError(
            "expected atext but found '{}'".format(value))
    atext = m.group()
    value = value[len(atext):]
    atext = ValueTerminal(atext, 'atext')
    _validate_xtext(atext)
    rudisha atext, value

eleza get_bare_quoted_string(value):
    """bare-quoted-string = DQUOTE *([FWS] qcontent) [FWS] DQUOTE

    A quoted-string without the leading ama trailing white space.  Its
    value ni the text between the quote marks, ukijumuisha whitespace
    preserved na quoted pairs decoded.
    """
    ikiwa value[0] != '"':
        ashiria errors.HeaderParseError(
            "expected '\"' but found '{}'".format(value))
    bare_quoted_string = BareQuotedString()
    value = value[1:]
    ikiwa value na value[0] == '"':
        token, value = get_qcontent(value)
        bare_quoted_string.append(token)
    wakati value na value[0] != '"':
        ikiwa value[0] kwenye WSP:
            token, value = get_fws(value)
        lasivyo value[:2] == '=?':
            jaribu:
                token, value = get_encoded_word(value)
                bare_quoted_string.defects.append(errors.InvalidHeaderDefect(
                    "encoded word inside quoted string"))
            tatizo errors.HeaderParseError:
                token, value = get_qcontent(value)
        isipokua:
            token, value = get_qcontent(value)
        bare_quoted_string.append(token)
    ikiwa sio value:
        bare_quoted_string.defects.append(errors.InvalidHeaderDefect(
            "end of header inside quoted string"))
        rudisha bare_quoted_string, value
    rudisha bare_quoted_string, value[1:]

eleza get_comment(value):
    """comment = "(" *([FWS] ccontent) [FWS] ")"
       ccontent = ctext / quoted-pair / comment

    We handle nested comments here, na quoted-pair kwenye our qp-ctext routine.
    """
    ikiwa value na value[0] != '(':
        ashiria errors.HeaderParseError(
            "expected '(' but found '{}'".format(value))
    comment = Comment()
    value = value[1:]
    wakati value na value[0] != ")":
        ikiwa value[0] kwenye WSP:
            token, value = get_fws(value)
        lasivyo value[0] == '(':
            token, value = get_comment(value)
        isipokua:
            token, value = get_qp_ctext(value)
        comment.append(token)
    ikiwa sio value:
        comment.defects.append(errors.InvalidHeaderDefect(
            "end of header inside comment"))
        rudisha comment, value
    rudisha comment, value[1:]

eleza get_cfws(value):
    """CFWS = (1*([FWS] comment) [FWS]) / FWS

    """
    cfws = CFWSList()
    wakati value na value[0] kwenye CFWS_LEADER:
        ikiwa value[0] kwenye WSP:
            token, value = get_fws(value)
        isipokua:
            token, value = get_comment(value)
        cfws.append(token)
    rudisha cfws, value

eleza get_quoted_string(value):
    """quoted-string = [CFWS] <bare-quoted-string> [CFWS]

    'bare-quoted-string' ni an intermediate kundi defined by this
    parser na sio by the RFC grammar.  It ni the quoted string
    without any attached CFWS.
    """
    quoted_string = QuotedString()
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        quoted_string.append(token)
    token, value = get_bare_quoted_string(value)
    quoted_string.append(token)
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        quoted_string.append(token)
    rudisha quoted_string, value

eleza get_atom(value):
    """atom = [CFWS] 1*atext [CFWS]

    An atom could be an rfc2047 encoded word.
    """
    atom = Atom()
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        atom.append(token)
    ikiwa value na value[0] kwenye ATOM_ENDS:
        ashiria errors.HeaderParseError(
            "expected atom but found '{}'".format(value))
    ikiwa value.startswith('=?'):
        jaribu:
            token, value = get_encoded_word(value)
        tatizo errors.HeaderParseError:
            # XXX: need to figure out how to register defects when
            # appropriate here.
            token, value = get_atext(value)
    isipokua:
        token, value = get_atext(value)
    atom.append(token)
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        atom.append(token)
    rudisha atom, value

eleza get_dot_atom_text(value):
    """ dot-text = 1*atext *("." 1*atext)

    """
    dot_atom_text = DotAtomText()
    ikiwa sio value ama value[0] kwenye ATOM_ENDS:
        ashiria errors.HeaderParseError("expected atom at a start of "
            "dot-atom-text but found '{}'".format(value))
    wakati value na value[0] haiko kwenye ATOM_ENDS:
        token, value = get_atext(value)
        dot_atom_text.append(token)
        ikiwa value na value[0] == '.':
            dot_atom_text.append(DOT)
            value = value[1:]
    ikiwa dot_atom_text[-1] ni DOT:
        ashiria errors.HeaderParseError("expected atom at end of dot-atom-text "
            "but found '{}'".format('.'+value))
    rudisha dot_atom_text, value

eleza get_dot_atom(value):
    """ dot-atom = [CFWS] dot-atom-text [CFWS]

    Any place we can have a dot atom, we could instead have an rfc2047 encoded
    word.
    """
    dot_atom = DotAtom()
    ikiwa value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        dot_atom.append(token)
    ikiwa value.startswith('=?'):
        jaribu:
            token, value = get_encoded_word(value)
        tatizo errors.HeaderParseError:
            # XXX: need to figure out how to register defects when
            # appropriate here.
            token, value = get_dot_atom_text(value)
    isipokua:
        token, value = get_dot_atom_text(value)
    dot_atom.append(token)
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        dot_atom.append(token)
    rudisha dot_atom, value

eleza get_word(value):
    """word = atom / quoted-string

    Either atom ama quoted-string may start ukijumuisha CFWS.  We have to peel off this
    CFWS first to determine which type of word to parse.  Afterward we splice
    the leading CFWS, ikiwa any, into the parsed sub-token.

    If neither an atom ama a quoted-string ni found before the next special, a
    HeaderParseError ni raised.

    The token returned ni either an Atom ama a QuotedString, kama appropriate.
    This means the 'word' level of the formal grammar ni sio represented kwenye the
    parse tree; this ni because having that extra layer when manipulating the
    parse tree ni more confusing than it ni helpful.

    """
    ikiwa value[0] kwenye CFWS_LEADER:
        leader, value = get_cfws(value)
    isipokua:
        leader = Tupu
    ikiwa sio value:
        ashiria errors.HeaderParseError(
            "Expected 'atom' ama 'quoted-string' but found nothing.")
    ikiwa value[0]=='"':
        token, value = get_quoted_string(value)
    lasivyo value[0] kwenye SPECIALS:
        ashiria errors.HeaderParseError("Expected 'atom' ama 'quoted-string' "
                                      "but found '{}'".format(value))
    isipokua:
        token, value = get_atom(value)
    ikiwa leader ni sio Tupu:
        token[:0] = [leader]
    rudisha token, value

eleza get_phrase(value):
    """ phrase = 1*word / obs-phrase
        obs-phrase = word *(word / "." / CFWS)

    This means a phrase can be a sequence of words, periods, na CFWS kwenye any
    order kama long kama it starts ukijumuisha at least one word.  If anything other than
    words ni detected, an ObsoleteHeaderDefect ni added to the token's defect
    list.  We also accept a phrase that starts ukijumuisha CFWS followed by a dot;
    this ni registered kama an InvalidHeaderDefect, since it ni sio supported by
    even the obsolete grammar.

    """
    phrase = Phrase()
    jaribu:
        token, value = get_word(value)
        phrase.append(token)
    tatizo errors.HeaderParseError:
        phrase.defects.append(errors.InvalidHeaderDefect(
            "phrase does sio start ukijumuisha word"))
    wakati value na value[0] haiko kwenye PHRASE_ENDS:
        ikiwa value[0]=='.':
            phrase.append(DOT)
            phrase.defects.append(errors.ObsoleteHeaderDefect(
                "period kwenye 'phrase'"))
            value = value[1:]
        isipokua:
            jaribu:
                token, value = get_word(value)
            tatizo errors.HeaderParseError:
                ikiwa value[0] kwenye CFWS_LEADER:
                    token, value = get_cfws(value)
                    phrase.defects.append(errors.ObsoleteHeaderDefect(
                        "comment found without atom"))
                isipokua:
                    raise
            phrase.append(token)
    rudisha phrase, value

eleza get_local_part(value):
    """ local-part = dot-atom / quoted-string / obs-local-part

    """
    local_part = LocalPart()
    leader = Tupu
    ikiwa value[0] kwenye CFWS_LEADER:
        leader, value = get_cfws(value)
    ikiwa sio value:
        ashiria errors.HeaderParseError(
            "expected local-part but found '{}'".format(value))
    jaribu:
        token, value = get_dot_atom(value)
    tatizo errors.HeaderParseError:
        jaribu:
            token, value = get_word(value)
        tatizo errors.HeaderParseError:
            ikiwa value[0] != '\\' na value[0] kwenye PHRASE_ENDS:
                raise
            token = TokenList()
    ikiwa leader ni sio Tupu:
        token[:0] = [leader]
    local_part.append(token)
    ikiwa value na (value[0]=='\\' ama value[0] haiko kwenye PHRASE_ENDS):
        obs_local_part, value = get_obs_local_part(str(local_part) + value)
        ikiwa obs_local_part.token_type == 'invalid-obs-local-part':
            local_part.defects.append(errors.InvalidHeaderDefect(
                "local-part ni sio dot-atom, quoted-string, ama obs-local-part"))
        isipokua:
            local_part.defects.append(errors.ObsoleteHeaderDefect(
                "local-part ni sio a dot-atom (contains CFWS)"))
        local_part[0] = obs_local_part
    jaribu:
        local_part.value.encode('ascii')
    tatizo UnicodeEncodeError:
        local_part.defects.append(errors.NonASCIILocalPartDefect(
                "local-part contains non-ASCII characters)"))
    rudisha local_part, value

eleza get_obs_local_part(value):
    """ obs-local-part = word *("." word)
    """
    obs_local_part = ObsLocalPart()
    last_non_ws_was_dot = Uongo
    wakati value na (value[0]=='\\' ama value[0] haiko kwenye PHRASE_ENDS):
        ikiwa value[0] == '.':
            ikiwa last_non_ws_was_dot:
                obs_local_part.defects.append(errors.InvalidHeaderDefect(
                    "invalid repeated '.'"))
            obs_local_part.append(DOT)
            last_non_ws_was_dot = Kweli
            value = value[1:]
            endelea
        lasivyo value[0]=='\\':
            obs_local_part.append(ValueTerminal(value[0],
                                                'misplaced-special'))
            value = value[1:]
            obs_local_part.defects.append(errors.InvalidHeaderDefect(
                "'\\' character outside of quoted-string/ccontent"))
            last_non_ws_was_dot = Uongo
            endelea
        ikiwa obs_local_part na obs_local_part[-1].token_type != 'dot':
            obs_local_part.defects.append(errors.InvalidHeaderDefect(
                "missing '.' between words"))
        jaribu:
            token, value = get_word(value)
            last_non_ws_was_dot = Uongo
        tatizo errors.HeaderParseError:
            ikiwa value[0] haiko kwenye CFWS_LEADER:
                raise
            token, value = get_cfws(value)
        obs_local_part.append(token)
    ikiwa (obs_local_part[0].token_type == 'dot' ama
            obs_local_part[0].token_type=='cfws' na
            obs_local_part[1].token_type=='dot'):
        obs_local_part.defects.append(errors.InvalidHeaderDefect(
            "Invalid leading '.' kwenye local part"))
    ikiwa (obs_local_part[-1].token_type == 'dot' ama
            obs_local_part[-1].token_type=='cfws' na
            obs_local_part[-2].token_type=='dot'):
        obs_local_part.defects.append(errors.InvalidHeaderDefect(
            "Invalid trailing '.' kwenye local part"))
    ikiwa obs_local_part.defects:
        obs_local_part.token_type = 'invalid-obs-local-part'
    rudisha obs_local_part, value

eleza get_dtext(value):
    r""" dtext = <printable ascii tatizo \ [ ]> / obs-dtext
        obs-dtext = obs-NO-WS-CTL / quoted-pair

    We allow anything tatizo the excluded characters, but ikiwa we find any
    ASCII other than the RFC defined printable ASCII, a NonPrintableDefect is
    added to the token's defects list.  Quoted pairs are converted to their
    unquoted values, so what ni returned ni a ptext token, kwenye this case a
    ValueTerminal.  If there were quoted-printables, an ObsoleteHeaderDefect is
    added to the returned token's defect list.

    """
    ptext, value, had_qp = _get_ptext_to_endchars(value, '[]')
    ptext = ValueTerminal(ptext, 'ptext')
    ikiwa had_qp:
        ptext.defects.append(errors.ObsoleteHeaderDefect(
            "quoted printable found kwenye domain-literal"))
    _validate_xtext(ptext)
    rudisha ptext, value

eleza _check_for_early_dl_end(value, domain_literal):
    ikiwa value:
        rudisha Uongo
    domain_literal.append(errors.InvalidHeaderDefect(
        "end of input inside domain-literal"))
    domain_literal.append(ValueTerminal(']', 'domain-literal-end'))
    rudisha Kweli

eleza get_domain_literal(value):
    """ domain-literal = [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]

    """
    domain_literal = DomainLiteral()
    ikiwa value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        domain_literal.append(token)
    ikiwa sio value:
        ashiria errors.HeaderParseError("expected domain-literal")
    ikiwa value[0] != '[':
        ashiria errors.HeaderParseError("expected '[' at start of domain-literal "
                "but found '{}'".format(value))
    value = value[1:]
    ikiwa _check_for_early_dl_end(value, domain_literal):
        rudisha domain_literal, value
    domain_literal.append(ValueTerminal('[', 'domain-literal-start'))
    ikiwa value[0] kwenye WSP:
        token, value = get_fws(value)
        domain_literal.append(token)
    token, value = get_dtext(value)
    domain_literal.append(token)
    ikiwa _check_for_early_dl_end(value, domain_literal):
        rudisha domain_literal, value
    ikiwa value[0] kwenye WSP:
        token, value = get_fws(value)
        domain_literal.append(token)
    ikiwa _check_for_early_dl_end(value, domain_literal):
        rudisha domain_literal, value
    ikiwa value[0] != ']':
        ashiria errors.HeaderParseError("expected ']' at end of domain-literal "
                "but found '{}'".format(value))
    domain_literal.append(ValueTerminal(']', 'domain-literal-end'))
    value = value[1:]
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        domain_literal.append(token)
    rudisha domain_literal, value

eleza get_domain(value):
    """ domain = dot-atom / domain-literal / obs-domain
        obs-domain = atom *("." atom))

    """
    domain = Domain()
    leader = Tupu
    ikiwa value[0] kwenye CFWS_LEADER:
        leader, value = get_cfws(value)
    ikiwa sio value:
        ashiria errors.HeaderParseError(
            "expected domain but found '{}'".format(value))
    ikiwa value[0] == '[':
        token, value = get_domain_literal(value)
        ikiwa leader ni sio Tupu:
            token[:0] = [leader]
        domain.append(token)
        rudisha domain, value
    jaribu:
        token, value = get_dot_atom(value)
    tatizo errors.HeaderParseError:
        token, value = get_atom(value)
    ikiwa value na value[0] == '@':
        ashiria errors.HeaderParseError('Invalid Domain')
    ikiwa leader ni sio Tupu:
        token[:0] = [leader]
    domain.append(token)
    ikiwa value na value[0] == '.':
        domain.defects.append(errors.ObsoleteHeaderDefect(
            "domain ni sio a dot-atom (contains CFWS)"))
        ikiwa domain[0].token_type == 'dot-atom':
            domain[:] = domain[0]
        wakati value na value[0] == '.':
            domain.append(DOT)
            token, value = get_atom(value[1:])
            domain.append(token)
    rudisha domain, value

eleza get_addr_spec(value):
    """ addr-spec = local-part "@" domain

    """
    addr_spec = AddrSpec()
    token, value = get_local_part(value)
    addr_spec.append(token)
    ikiwa sio value ama value[0] != '@':
        addr_spec.defects.append(errors.InvalidHeaderDefect(
            "addr-spec local part ukijumuisha no domain"))
        rudisha addr_spec, value
    addr_spec.append(ValueTerminal('@', 'address-at-symbol'))
    token, value = get_domain(value[1:])
    addr_spec.append(token)
    rudisha addr_spec, value

eleza get_obs_route(value):
    """ obs-route = obs-domain-list ":"
        obs-domain-list = *(CFWS / ",") "@" domain *("," [CFWS] ["@" domain])

        Returns an obs-route token ukijumuisha the appropriate sub-tokens (that is,
        there ni no obs-domain-list kwenye the parse tree).
    """
    obs_route = ObsRoute()
    wakati value na (value[0]==',' ama value[0] kwenye CFWS_LEADER):
        ikiwa value[0] kwenye CFWS_LEADER:
            token, value = get_cfws(value)
            obs_route.append(token)
        lasivyo value[0] == ',':
            obs_route.append(ListSeparator)
            value = value[1:]
    ikiwa sio value ama value[0] != '@':
        ashiria errors.HeaderParseError(
            "expected obs-route domain but found '{}'".format(value))
    obs_route.append(RouteComponentMarker)
    token, value = get_domain(value[1:])
    obs_route.append(token)
    wakati value na value[0]==',':
        obs_route.append(ListSeparator)
        value = value[1:]
        ikiwa sio value:
            koma
        ikiwa value[0] kwenye CFWS_LEADER:
            token, value = get_cfws(value)
            obs_route.append(token)
        ikiwa value[0] == '@':
            obs_route.append(RouteComponentMarker)
            token, value = get_domain(value[1:])
            obs_route.append(token)
    ikiwa sio value:
        ashiria errors.HeaderParseError("end of header wakati parsing obs-route")
    ikiwa value[0] != ':':
        ashiria errors.HeaderParseError( "expected ':' marking end of "
            "obs-route but found '{}'".format(value))
    obs_route.append(ValueTerminal(':', 'end-of-obs-route-marker'))
    rudisha obs_route, value[1:]

eleza get_angle_addr(value):
    """ angle-addr = [CFWS] "<" addr-spec ">" [CFWS] / obs-angle-addr
        obs-angle-addr = [CFWS] "<" obs-route addr-spec ">" [CFWS]

    """
    angle_addr = AngleAddr()
    ikiwa value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        angle_addr.append(token)
    ikiwa sio value ama value[0] != '<':
        ashiria errors.HeaderParseError(
            "expected angle-addr but found '{}'".format(value))
    angle_addr.append(ValueTerminal('<', 'angle-addr-start'))
    value = value[1:]
    # Although it ni sio legal per RFC5322, SMTP uses '<>' kwenye certain
    # circumstances.
    ikiwa value[0] == '>':
        angle_addr.append(ValueTerminal('>', 'angle-addr-end'))
        angle_addr.defects.append(errors.InvalidHeaderDefect(
            "null addr-spec kwenye angle-addr"))
        value = value[1:]
        rudisha angle_addr, value
    jaribu:
        token, value = get_addr_spec(value)
    tatizo errors.HeaderParseError:
        jaribu:
            token, value = get_obs_route(value)
            angle_addr.defects.append(errors.ObsoleteHeaderDefect(
                "obsolete route specification kwenye angle-addr"))
        tatizo errors.HeaderParseError:
            ashiria errors.HeaderParseError(
                "expected addr-spec ama obs-route but found '{}'".format(value))
        angle_addr.append(token)
        token, value = get_addr_spec(value)
    angle_addr.append(token)
    ikiwa value na value[0] == '>':
        value = value[1:]
    isipokua:
        angle_addr.defects.append(errors.InvalidHeaderDefect(
            "missing trailing '>' on angle-addr"))
    angle_addr.append(ValueTerminal('>', 'angle-addr-end'))
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        angle_addr.append(token)
    rudisha angle_addr, value

eleza get_display_name(value):
    """ display-name = phrase

    Because this ni simply a name-rule, we don't rudisha a display-name
    token containing a phrase, but rather a display-name token with
    the content of the phrase.

    """
    display_name = DisplayName()
    token, value = get_phrase(value)
    display_name.extend(token[:])
    display_name.defects = token.defects[:]
    rudisha display_name, value


eleza get_name_addr(value):
    """ name-addr = [display-name] angle-addr

    """
    name_addr = NameAddr()
    # Both the optional display name na the angle-addr can start ukijumuisha cfws.
    leader = Tupu
    ikiwa value[0] kwenye CFWS_LEADER:
        leader, value = get_cfws(value)
        ikiwa sio value:
            ashiria errors.HeaderParseError(
                "expected name-addr but found '{}'".format(leader))
    ikiwa value[0] != '<':
        ikiwa value[0] kwenye PHRASE_ENDS:
            ashiria errors.HeaderParseError(
                "expected name-addr but found '{}'".format(value))
        token, value = get_display_name(value)
        ikiwa sio value:
            ashiria errors.HeaderParseError(
                "expected name-addr but found '{}'".format(token))
        ikiwa leader ni sio Tupu:
            token[0][:0] = [leader]
            leader = Tupu
        name_addr.append(token)
    token, value = get_angle_addr(value)
    ikiwa leader ni sio Tupu:
        token[:0] = [leader]
    name_addr.append(token)
    rudisha name_addr, value

eleza get_mailbox(value):
    """ mailbox = name-addr / addr-spec

    """
    # The only way to figure out ikiwa we are dealing ukijumuisha a name-addr ama an
    # addr-spec ni to try parsing each one.
    mailbox = Mailbox()
    jaribu:
        token, value = get_name_addr(value)
    tatizo errors.HeaderParseError:
        jaribu:
            token, value = get_addr_spec(value)
        tatizo errors.HeaderParseError:
            ashiria errors.HeaderParseError(
                "expected mailbox but found '{}'".format(value))
    ikiwa any(isinstance(x, errors.InvalidHeaderDefect)
                       kila x kwenye token.all_defects):
        mailbox.token_type = 'invalid-mailbox'
    mailbox.append(token)
    rudisha mailbox, value

eleza get_invalid_mailbox(value, endchars):
    """ Read everything up to one of the chars kwenye endchars.

    This ni outside the formal grammar.  The InvalidMailbox TokenList that is
    returned acts like a Mailbox, but the data attributes are Tupu.

    """
    invalid_mailbox = InvalidMailbox()
    wakati value na value[0] haiko kwenye endchars:
        ikiwa value[0] kwenye PHRASE_ENDS:
            invalid_mailbox.append(ValueTerminal(value[0],
                                                 'misplaced-special'))
            value = value[1:]
        isipokua:
            token, value = get_phrase(value)
            invalid_mailbox.append(token)
    rudisha invalid_mailbox, value

eleza get_mailbox_list(value):
    """ mailbox-list = (mailbox *("," mailbox)) / obs-mbox-list
        obs-mbox-list = *([CFWS] ",") mailbox *("," [mailbox / CFWS])

    For this routine we go outside the formal grammar kwenye order to improve error
    handling.  We recognize the end of the mailbox list only at the end of the
    value ama at a ';' (the group terminator).  This ni so that we can turn
    invalid mailboxes into InvalidMailbox tokens na endelea parsing any
    remaining valid mailboxes.  We also allow all mailbox entries to be null,
    na this condition ni handled appropriately at a higher level.

    """
    mailbox_list = MailboxList()
    wakati value na value[0] != ';':
        jaribu:
            token, value = get_mailbox(value)
            mailbox_list.append(token)
        tatizo errors.HeaderParseError:
            leader = Tupu
            ikiwa value[0] kwenye CFWS_LEADER:
                leader, value = get_cfws(value)
                ikiwa sio value ama value[0] kwenye ',;':
                    mailbox_list.append(leader)
                    mailbox_list.defects.append(errors.ObsoleteHeaderDefect(
                        "empty element kwenye mailbox-list"))
                isipokua:
                    token, value = get_invalid_mailbox(value, ',;')
                    ikiwa leader ni sio Tupu:
                        token[:0] = [leader]
                    mailbox_list.append(token)
                    mailbox_list.defects.append(errors.InvalidHeaderDefect(
                        "invalid mailbox kwenye mailbox-list"))
            lasivyo value[0] == ',':
                mailbox_list.defects.append(errors.ObsoleteHeaderDefect(
                    "empty element kwenye mailbox-list"))
            isipokua:
                token, value = get_invalid_mailbox(value, ',;')
                ikiwa leader ni sio Tupu:
                    token[:0] = [leader]
                mailbox_list.append(token)
                mailbox_list.defects.append(errors.InvalidHeaderDefect(
                    "invalid mailbox kwenye mailbox-list"))
        ikiwa value na value[0] haiko kwenye ',;':
            # Crap after mailbox; treat it kama an invalid mailbox.
            # The mailbox info will still be available.
            mailbox = mailbox_list[-1]
            mailbox.token_type = 'invalid-mailbox'
            token, value = get_invalid_mailbox(value, ',;')
            mailbox.extend(token)
            mailbox_list.defects.append(errors.InvalidHeaderDefect(
                "invalid mailbox kwenye mailbox-list"))
        ikiwa value na value[0] == ',':
            mailbox_list.append(ListSeparator)
            value = value[1:]
    rudisha mailbox_list, value


eleza get_group_list(value):
    """ group-list = mailbox-list / CFWS / obs-group-list
        obs-group-list = 1*([CFWS] ",") [CFWS]

    """
    group_list = GroupList()
    ikiwa sio value:
        group_list.defects.append(errors.InvalidHeaderDefect(
            "end of header before group-list"))
        rudisha group_list, value
    leader = Tupu
    ikiwa value na value[0] kwenye CFWS_LEADER:
        leader, value = get_cfws(value)
        ikiwa sio value:
            # This should never happen kwenye email parsing, since CFWS-only ni a
            # legal alternative to group-list kwenye a group, which ni the only
            # place group-list appears.
            group_list.defects.append(errors.InvalidHeaderDefect(
                "end of header kwenye group-list"))
            group_list.append(leader)
            rudisha group_list, value
        ikiwa value[0] == ';':
            group_list.append(leader)
            rudisha group_list, value
    token, value = get_mailbox_list(value)
    ikiwa len(token.all_mailboxes)==0:
        ikiwa leader ni sio Tupu:
            group_list.append(leader)
        group_list.extend(token)
        group_list.defects.append(errors.ObsoleteHeaderDefect(
            "group-list ukijumuisha empty entries"))
        rudisha group_list, value
    ikiwa leader ni sio Tupu:
        token[:0] = [leader]
    group_list.append(token)
    rudisha group_list, value

eleza get_group(value):
    """ group = display-name ":" [group-list] ";" [CFWS]

    """
    group = Group()
    token, value = get_display_name(value)
    ikiwa sio value ama value[0] != ':':
        ashiria errors.HeaderParseError("expected ':' at end of group "
            "display name but found '{}'".format(value))
    group.append(token)
    group.append(ValueTerminal(':', 'group-display-name-terminator'))
    value = value[1:]
    ikiwa value na value[0] == ';':
        group.append(ValueTerminal(';', 'group-terminator'))
        rudisha group, value[1:]
    token, value = get_group_list(value)
    group.append(token)
    ikiwa sio value:
        group.defects.append(errors.InvalidHeaderDefect(
            "end of header kwenye group"))
    lasivyo value[0] != ';':
        ashiria errors.HeaderParseError(
            "expected ';' at end of group but found {}".format(value))
    group.append(ValueTerminal(';', 'group-terminator'))
    value = value[1:]
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        group.append(token)
    rudisha group, value

eleza get_address(value):
    """ address = mailbox / group

    Note that counter-intuitively, an address can be either a single address ama
    a list of addresses (a group).  This ni why the returned Address object has
    a 'mailboxes' attribute which treats a single address kama a list of length
    one.  When you need to differentiate between to two cases, extract the single
    element, which ni either a mailbox ama a group token.

    """
    # The formal grammar isn't very helpful when parsing an address.  mailbox
    # na group, especially when allowing kila obsolete forms, start off very
    # similarly.  It ni only when you reach one of @, <, ama : that you know
    # what you've got.  So, we try each one kwenye turn, starting ukijumuisha the more
    # likely of the two.  We could perhaps make this more efficient by looking
    # kila a phrase na then branching based on the next character, but that
    # would be a premature optimization.
    address = Address()
    jaribu:
        token, value = get_group(value)
    tatizo errors.HeaderParseError:
        jaribu:
            token, value = get_mailbox(value)
        tatizo errors.HeaderParseError:
            ashiria errors.HeaderParseError(
                "expected address but found '{}'".format(value))
    address.append(token)
    rudisha address, value

eleza get_address_list(value):
    """ address_list = (address *("," address)) / obs-addr-list
        obs-addr-list = *([CFWS] ",") address *("," [address / CFWS])

    We depart kutoka the formal grammar here by continuing to parse until the end
    of the input, assuming the input to be entirely composed of an
    address-list.  This ni always true kwenye email parsing, na allows us
    to skip invalid addresses to parse additional valid ones.

    """
    address_list = AddressList()
    wakati value:
        jaribu:
            token, value = get_address(value)
            address_list.append(token)
        tatizo errors.HeaderParseError kama err:
            leader = Tupu
            ikiwa value[0] kwenye CFWS_LEADER:
                leader, value = get_cfws(value)
                ikiwa sio value ama value[0] == ',':
                    address_list.append(leader)
                    address_list.defects.append(errors.ObsoleteHeaderDefect(
                        "address-list entry ukijumuisha no content"))
                isipokua:
                    token, value = get_invalid_mailbox(value, ',')
                    ikiwa leader ni sio Tupu:
                        token[:0] = [leader]
                    address_list.append(Address([token]))
                    address_list.defects.append(errors.InvalidHeaderDefect(
                        "invalid address kwenye address-list"))
            lasivyo value[0] == ',':
                address_list.defects.append(errors.ObsoleteHeaderDefect(
                    "empty element kwenye address-list"))
            isipokua:
                token, value = get_invalid_mailbox(value, ',')
                ikiwa leader ni sio Tupu:
                    token[:0] = [leader]
                address_list.append(Address([token]))
                address_list.defects.append(errors.InvalidHeaderDefect(
                    "invalid address kwenye address-list"))
        ikiwa value na value[0] != ',':
            # Crap after address; treat it kama an invalid mailbox.
            # The mailbox info will still be available.
            mailbox = address_list[-1][0]
            mailbox.token_type = 'invalid-mailbox'
            token, value = get_invalid_mailbox(value, ',')
            mailbox.extend(token)
            address_list.defects.append(errors.InvalidHeaderDefect(
                "invalid address kwenye address-list"))
        ikiwa value:  # Must be a , at this point.
            address_list.append(ValueTerminal(',', 'list-separator'))
            value = value[1:]
    rudisha address_list, value


eleza get_no_fold_literal(value):
    """ no-fold-literal = "[" *dtext "]"
    """
    no_fold_literal = NoFoldLiteral()
    ikiwa sio value:
        ashiria errors.HeaderParseError(
            "expected no-fold-literal but found '{}'".format(value))
    ikiwa value[0] != '[':
        ashiria errors.HeaderParseError(
            "expected '[' at the start of no-fold-literal "
            "but found '{}'".format(value))
    no_fold_literal.append(ValueTerminal('[', 'no-fold-literal-start'))
    value = value[1:]
    token, value = get_dtext(value)
    no_fold_literal.append(token)
    ikiwa sio value ama value[0] != ']':
        ashiria errors.HeaderParseError(
            "expected ']' at the end of no-fold-literal "
            "but found '{}'".format(value))
    no_fold_literal.append(ValueTerminal(']', 'no-fold-literal-end'))
    rudisha no_fold_literal, value[1:]

eleza get_msg_id(value):
    """msg-id = [CFWS] "<" id-left '@' id-right  ">" [CFWS]
       id-left = dot-atom-text / obs-id-left
       id-right = dot-atom-text / no-fold-literal / obs-id-right
       no-fold-literal = "[" *dtext "]"
    """
    msg_id = MsgID()
    ikiwa value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        msg_id.append(token)
    ikiwa sio value ama value[0] != '<':
        ashiria errors.HeaderParseError(
            "expected msg-id but found '{}'".format(value))
    msg_id.append(ValueTerminal('<', 'msg-id-start'))
    value = value[1:]
    # Parse id-left.
    jaribu:
        token, value = get_dot_atom_text(value)
    tatizo errors.HeaderParseError:
        jaribu:
            # obs-id-left ni same kama local-part of add-spec.
            token, value = get_obs_local_part(value)
            msg_id.defects.append(errors.ObsoleteHeaderDefect(
                "obsolete id-left kwenye msg-id"))
        tatizo errors.HeaderParseError:
            ashiria errors.HeaderParseError(
                "expected dot-atom-text ama obs-id-left"
                " but found '{}'".format(value))
    msg_id.append(token)
    ikiwa sio value ama value[0] != '@':
        msg_id.defects.append(errors.InvalidHeaderDefect(
            "msg-id ukijumuisha no id-right"))
        # Even though there ni no id-right, ikiwa the local part
        # ends ukijumuisha `>` let's just parse it too na rudisha
        # along ukijumuisha the defect.
        ikiwa value na value[0] == '>':
            msg_id.append(ValueTerminal('>', 'msg-id-end'))
            value = value[1:]
        rudisha msg_id, value
    msg_id.append(ValueTerminal('@', 'address-at-symbol'))
    value = value[1:]
    # Parse id-right.
    jaribu:
        token, value = get_dot_atom_text(value)
    tatizo errors.HeaderParseError:
        jaribu:
            token, value = get_no_fold_literal(value)
        tatizo errors.HeaderParseError kama e:
            jaribu:
                token, value = get_domain(value)
                msg_id.defects.append(errors.ObsoleteHeaderDefect(
                    "obsolete id-right kwenye msg-id"))
            tatizo errors.HeaderParseError:
                ashiria errors.HeaderParseError(
                    "expected dot-atom-text, no-fold-literal ama obs-id-right"
                    " but found '{}'".format(value))
    msg_id.append(token)
    ikiwa value na value[0] == '>':
        value = value[1:]
    isipokua:
        msg_id.defects.append(errors.InvalidHeaderDefect(
            "missing trailing '>' on msg-id"))
    msg_id.append(ValueTerminal('>', 'msg-id-end'))
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        msg_id.append(token)
    rudisha msg_id, value


eleza parse_message_id(value):
    """message-id      =   "Message-ID:" msg-id CRLF
    """
    message_id = MessageID()
    jaribu:
        token, value = get_msg_id(value)
    tatizo errors.HeaderParseError:
        message_id.defects.append(errors.InvalidHeaderDefect(
            "Expected msg-id but found {!r}".format(value)))
    message_id.append(token)
    rudisha message_id

#
# XXX: As I begin to add additional header parsers, I'm realizing we probably
# have two level of parser routines: the get_XXX methods that get a token in
# the grammar, na parse_XXX methods that parse an entire field value.  So
# get_address_list above should really be a parse_ method, kama probably should
# be get_unstructured.
#

eleza parse_mime_version(value):
    """ mime-version = [CFWS] 1*digit [CFWS] "." [CFWS] 1*digit [CFWS]

    """
    # The [CFWS] ni implicit kwenye the RFC 2045 BNF.
    # XXX: This routine ni a bit verbose, should factor out a get_int method.
    mime_version = MIMEVersion()
    ikiwa sio value:
        mime_version.defects.append(errors.HeaderMissingRequiredValue(
            "Missing MIME version number (eg: 1.0)"))
        rudisha mime_version
    ikiwa value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        mime_version.append(token)
        ikiwa sio value:
            mime_version.defects.append(errors.HeaderMissingRequiredValue(
                "Expected MIME version number but found only CFWS"))
    digits = ''
    wakati value na value[0] != '.' na value[0] haiko kwenye CFWS_LEADER:
        digits += value[0]
        value = value[1:]
    ikiwa sio digits.isdigit():
        mime_version.defects.append(errors.InvalidHeaderDefect(
            "Expected MIME major version number but found {!r}".format(digits)))
        mime_version.append(ValueTerminal(digits, 'xtext'))
    isipokua:
        mime_version.major = int(digits)
        mime_version.append(ValueTerminal(digits, 'digits'))
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        mime_version.append(token)
    ikiwa sio value ama value[0] != '.':
        ikiwa mime_version.major ni sio Tupu:
            mime_version.defects.append(errors.InvalidHeaderDefect(
                "Incomplete MIME version; found only major number"))
        ikiwa value:
            mime_version.append(ValueTerminal(value, 'xtext'))
        rudisha mime_version
    mime_version.append(ValueTerminal('.', 'version-separator'))
    value = value[1:]
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        mime_version.append(token)
    ikiwa sio value:
        ikiwa mime_version.major ni sio Tupu:
            mime_version.defects.append(errors.InvalidHeaderDefect(
                "Incomplete MIME version; found only major number"))
        rudisha mime_version
    digits = ''
    wakati value na value[0] haiko kwenye CFWS_LEADER:
        digits += value[0]
        value = value[1:]
    ikiwa sio digits.isdigit():
        mime_version.defects.append(errors.InvalidHeaderDefect(
            "Expected MIME minor version number but found {!r}".format(digits)))
        mime_version.append(ValueTerminal(digits, 'xtext'))
    isipokua:
        mime_version.minor = int(digits)
        mime_version.append(ValueTerminal(digits, 'digits'))
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        mime_version.append(token)
    ikiwa value:
        mime_version.defects.append(errors.InvalidHeaderDefect(
            "Excess non-CFWS text after MIME version"))
        mime_version.append(ValueTerminal(value, 'xtext'))
    rudisha mime_version

eleza get_invalid_parameter(value):
    """ Read everything up to the next ';'.

    This ni outside the formal grammar.  The InvalidParameter TokenList that is
    returned acts like a Parameter, but the data attributes are Tupu.

    """
    invalid_parameter = InvalidParameter()
    wakati value na value[0] != ';':
        ikiwa value[0] kwenye PHRASE_ENDS:
            invalid_parameter.append(ValueTerminal(value[0],
                                                   'misplaced-special'))
            value = value[1:]
        isipokua:
            token, value = get_phrase(value)
            invalid_parameter.append(token)
    rudisha invalid_parameter, value

eleza get_ttext(value):
    """ttext = <matches _ttext_matcher>

    We allow any non-TOKEN_ENDS kwenye ttext, but add defects to the token's
    defects list ikiwa we find non-ttext characters.  We also register defects for
    *any* non-printables even though the RFC doesn't exclude all of them,
    because we follow the spirit of RFC 5322.

    """
    m = _non_token_end_matcher(value)
    ikiwa sio m:
        ashiria errors.HeaderParseError(
            "expected ttext but found '{}'".format(value))
    ttext = m.group()
    value = value[len(ttext):]
    ttext = ValueTerminal(ttext, 'ttext')
    _validate_xtext(ttext)
    rudisha ttext, value

eleza get_token(value):
    """token = [CFWS] 1*ttext [CFWS]

    The RFC equivalent of ttext ni any US-ASCII chars tatizo space, ctls, ama
    tspecials.  We also exclude tabs even though the RFC doesn't.

    The RFC implies the CFWS but ni sio explicit about it kwenye the BNF.

    """
    mtoken = Token()
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        mtoken.append(token)
    ikiwa value na value[0] kwenye TOKEN_ENDS:
        ashiria errors.HeaderParseError(
            "expected token but found '{}'".format(value))
    token, value = get_ttext(value)
    mtoken.append(token)
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        mtoken.append(token)
    rudisha mtoken, value

eleza get_attrtext(value):
    """attrtext = 1*(any non-ATTRIBUTE_ENDS character)

    We allow any non-ATTRIBUTE_ENDS kwenye attrtext, but add defects to the
    token's defects list ikiwa we find non-attrtext characters.  We also register
    defects kila *any* non-printables even though the RFC doesn't exclude all of
    them, because we follow the spirit of RFC 5322.

    """
    m = _non_attribute_end_matcher(value)
    ikiwa sio m:
        ashiria errors.HeaderParseError(
            "expected attrtext but found {!r}".format(value))
    attrtext = m.group()
    value = value[len(attrtext):]
    attrtext = ValueTerminal(attrtext, 'attrtext')
    _validate_xtext(attrtext)
    rudisha attrtext, value

eleza get_attribute(value):
    """ [CFWS] 1*attrtext [CFWS]

    This version of the BNF makes the CFWS explicit, na kama usual we use a
    value terminal kila the actual run of characters.  The RFC equivalent of
    attrtext ni the token characters, ukijumuisha the subtraction of '*', "'", na '%'.
    We include tab kwenye the excluded set just kama we do kila token.

    """
    attribute = Attribute()
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        attribute.append(token)
    ikiwa value na value[0] kwenye ATTRIBUTE_ENDS:
        ashiria errors.HeaderParseError(
            "expected token but found '{}'".format(value))
    token, value = get_attrtext(value)
    attribute.append(token)
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        attribute.append(token)
    rudisha attribute, value

eleza get_extended_attrtext(value):
    """attrtext = 1*(any non-ATTRIBUTE_ENDS character plus '%')

    This ni a special parsing routine so that we get a value that
    includes % escapes kama a single string (which we decode kama a single
    string later).

    """
    m = _non_extended_attribute_end_matcher(value)
    ikiwa sio m:
        ashiria errors.HeaderParseError(
            "expected extended attrtext but found {!r}".format(value))
    attrtext = m.group()
    value = value[len(attrtext):]
    attrtext = ValueTerminal(attrtext, 'extended-attrtext')
    _validate_xtext(attrtext)
    rudisha attrtext, value

eleza get_extended_attribute(value):
    """ [CFWS] 1*extended_attrtext [CFWS]

    This ni like the non-extended version tatizo we allow % characters, so that
    we can pick up an encoded value kama a single string.

    """
    # XXX: should we have an ExtendedAttribute TokenList?
    attribute = Attribute()
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        attribute.append(token)
    ikiwa value na value[0] kwenye EXTENDED_ATTRIBUTE_ENDS:
        ashiria errors.HeaderParseError(
            "expected token but found '{}'".format(value))
    token, value = get_extended_attrtext(value)
    attribute.append(token)
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        attribute.append(token)
    rudisha attribute, value

eleza get_section(value):
    """ '*' digits

    The formal BNF ni more complicated because leading 0s are sio allowed.  We
    check kila that na add a defect.  We also assume no CFWS ni allowed between
    the '*' na the digits, though the RFC ni sio crystal clear on that.
    The caller should already have dealt ukijumuisha leading CFWS.

    """
    section = Section()
    ikiwa sio value ama value[0] != '*':
        ashiria errors.HeaderParseError("Expected section but found {}".format(
                                        value))
    section.append(ValueTerminal('*', 'section-marker'))
    value = value[1:]
    ikiwa sio value ama sio value[0].isdigit():
        ashiria errors.HeaderParseError("Expected section number but "
                                      "found {}".format(value))
    digits = ''
    wakati value na value[0].isdigit():
        digits += value[0]
        value = value[1:]
    ikiwa digits[0] == '0' na digits != '0':
        section.defects.append(errors.InvalidHeaderError(
                "section number has an invalid leading 0"))
    section.number = int(digits)
    section.append(ValueTerminal(digits, 'digits'))
    rudisha section, value


eleza get_value(value):
    """ quoted-string / attribute

    """
    v = Value()
    ikiwa sio value:
        ashiria errors.HeaderParseError("Expected value but found end of string")
    leader = Tupu
    ikiwa value[0] kwenye CFWS_LEADER:
        leader, value = get_cfws(value)
    ikiwa sio value:
        ashiria errors.HeaderParseError("Expected value but found "
                                      "only {}".format(leader))
    ikiwa value[0] == '"':
        token, value = get_quoted_string(value)
    isipokua:
        token, value = get_extended_attribute(value)
    ikiwa leader ni sio Tupu:
        token[:0] = [leader]
    v.append(token)
    rudisha v, value

eleza get_parameter(value):
    """ attribute [section] ["*"] [CFWS] "=" value

    The CFWS ni implied by the RFC but sio made explicit kwenye the BNF.  This
    simplified form of the BNF kutoka the RFC ni made to conform ukijumuisha the RFC BNF
    through some extra checks.  We do it this way because it makes both error
    recovery na working ukijumuisha the resulting parse tree easier.
    """
    # It ni possible CFWS would also be implicitly allowed between the section
    # na the 'extended-attribute' marker (the '*') , but we've never seen that
    # kwenye the wild na we will therefore ignore the possibility.
    param = Parameter()
    token, value = get_attribute(value)
    param.append(token)
    ikiwa sio value ama value[0] == ';':
        param.defects.append(errors.InvalidHeaderDefect("Parameter contains "
            "name ({}) but no value".format(token)))
        rudisha param, value
    ikiwa value[0] == '*':
        jaribu:
            token, value = get_section(value)
            param.sectioned = Kweli
            param.append(token)
        tatizo errors.HeaderParseError:
            pita
        ikiwa sio value:
            ashiria errors.HeaderParseError("Incomplete parameter")
        ikiwa value[0] == '*':
            param.append(ValueTerminal('*', 'extended-parameter-marker'))
            value = value[1:]
            param.extended = Kweli
    ikiwa value[0] != '=':
        ashiria errors.HeaderParseError("Parameter sio followed by '='")
    param.append(ValueTerminal('=', 'parameter-separator'))
    value = value[1:]
    leader = Tupu
    ikiwa value na value[0] kwenye CFWS_LEADER:
        token, value = get_cfws(value)
        param.append(token)
    remainder = Tupu
    appendto = param
    ikiwa param.extended na value na value[0] == '"':
        # Now kila some serious hackery to handle the common invalid case of
        # double quotes around an extended value.  We also accept (ukijumuisha defect)
        # a value marked kama encoded that isn't really.
        qstring, remainder = get_quoted_string(value)
        inner_value = qstring.stripped_value
        semi_valid = Uongo
        ikiwa param.section_number == 0:
            ikiwa inner_value na inner_value[0] == "'":
                semi_valid = Kweli
            isipokua:
                token, rest = get_attrtext(inner_value)
                ikiwa rest na rest[0] == "'":
                    semi_valid = Kweli
        isipokua:
            jaribu:
                token, rest = get_extended_attrtext(inner_value)
            tatizo:
                pita
            isipokua:
                ikiwa sio rest:
                    semi_valid = Kweli
        ikiwa semi_valid:
            param.defects.append(errors.InvalidHeaderDefect(
                "Quoted string value kila extended parameter ni invalid"))
            param.append(qstring)
            kila t kwenye qstring:
                ikiwa t.token_type == 'bare-quoted-string':
                    t[:] = []
                    appendto = t
                    koma
            value = inner_value
        isipokua:
            remainder = Tupu
            param.defects.append(errors.InvalidHeaderDefect(
                "Parameter marked kama extended but appears to have a "
                "quoted string value that ni non-encoded"))
    ikiwa value na value[0] == "'":
        token = Tupu
    isipokua:
        token, value = get_value(value)
    ikiwa sio param.extended ama param.section_number > 0:
        ikiwa sio value ama value[0] != "'":
            appendto.append(token)
            ikiwa remainder ni sio Tupu:
                assert sio value, value
                value = remainder
            rudisha param, value
        param.defects.append(errors.InvalidHeaderDefect(
            "Apparent initial-extended-value but attribute "
            "was sio marked kama extended ama was sio intial section"))
    ikiwa sio value:
        # Assume the charset/lang ni missing na the token ni the value.
        param.defects.append(errors.InvalidHeaderDefect(
            "Missing required charset/lang delimiters"))
        appendto.append(token)
        ikiwa remainder ni Tupu:
            rudisha param, value
    isipokua:
        ikiwa token ni sio Tupu:
            kila t kwenye token:
                ikiwa t.token_type == 'extended-attrtext':
                    koma
            t.token_type == 'attrtext'
            appendto.append(t)
            param.charset = t.value
        ikiwa value[0] != "'":
            ashiria errors.HeaderParseError("Expected RFC2231 char/lang encoding "
                                          "delimiter, but found {!r}".format(value))
        appendto.append(ValueTerminal("'", 'RFC2231-delimiter'))
        value = value[1:]
        ikiwa value na value[0] != "'":
            token, value = get_attrtext(value)
            appendto.append(token)
            param.lang = token.value
            ikiwa sio value ama value[0] != "'":
                ashiria errors.HeaderParseError("Expected RFC2231 char/lang encoding "
                                  "delimiter, but found {}".format(value))
        appendto.append(ValueTerminal("'", 'RFC2231-delimiter'))
        value = value[1:]
    ikiwa remainder ni sio Tupu:
        # Treat the rest of value kama bare quoted string content.
        v = Value()
        wakati value:
            ikiwa value[0] kwenye WSP:
                token, value = get_fws(value)
            lasivyo value[0] == '"':
                token = ValueTerminal('"', 'DQUOTE')
                value = value[1:]
            isipokua:
                token, value = get_qcontent(value)
            v.append(token)
        token = v
    isipokua:
        token, value = get_value(value)
    appendto.append(token)
    ikiwa remainder ni sio Tupu:
        assert sio value, value
        value = remainder
    rudisha param, value

eleza parse_mime_parameters(value):
    """ parameter *( ";" parameter )

    That BNF ni meant to indicate this routine should only be called after
    finding na handling the leading ';'.  There ni no corresponding rule in
    the formal RFC grammar, but it ni more convenient kila us kila the set of
    parameters to be treated kama its own TokenList.

    This ni 'parse' routine because it consumes the remaining value, but it
    would never be called to parse a full header.  Instead it ni called to
    parse everything after the non-parameter value of a specific MIME header.

    """
    mime_parameters = MimeParameters()
    wakati value:
        jaribu:
            token, value = get_parameter(value)
            mime_parameters.append(token)
        tatizo errors.HeaderParseError kama err:
            leader = Tupu
            ikiwa value[0] kwenye CFWS_LEADER:
                leader, value = get_cfws(value)
            ikiwa sio value:
                mime_parameters.append(leader)
                rudisha mime_parameters
            ikiwa value[0] == ';':
                ikiwa leader ni sio Tupu:
                    mime_parameters.append(leader)
                mime_parameters.defects.append(errors.InvalidHeaderDefect(
                    "parameter entry ukijumuisha no content"))
            isipokua:
                token, value = get_invalid_parameter(value)
                ikiwa leader:
                    token[:0] = [leader]
                mime_parameters.append(token)
                mime_parameters.defects.append(errors.InvalidHeaderDefect(
                    "invalid parameter {!r}".format(token)))
        ikiwa value na value[0] != ';':
            # Junk after the otherwise valid parameter.  Mark it as
            # invalid, but it will have a value.
            param = mime_parameters[-1]
            param.token_type = 'invalid-parameter'
            token, value = get_invalid_parameter(value)
            param.extend(token)
            mime_parameters.defects.append(errors.InvalidHeaderDefect(
                "parameter ukijumuisha invalid trailing text {!r}".format(token)))
        ikiwa value:
            # Must be a ';' at this point.
            mime_parameters.append(ValueTerminal(';', 'parameter-separator'))
            value = value[1:]
    rudisha mime_parameters

eleza _find_mime_parameters(tokenlist, value):
    """Do our best to find the parameters kwenye an invalid MIME header

    """
    wakati value na value[0] != ';':
        ikiwa value[0] kwenye PHRASE_ENDS:
            tokenlist.append(ValueTerminal(value[0], 'misplaced-special'))
            value = value[1:]
        isipokua:
            token, value = get_phrase(value)
            tokenlist.append(token)
    ikiwa sio value:
        rudisha
    tokenlist.append(ValueTerminal(';', 'parameter-separator'))
    tokenlist.append(parse_mime_parameters(value[1:]))

eleza parse_content_type_header(value):
    """ maintype "/" subtype *( ";" parameter )

    The maintype na substype are tokens.  Theoretically they could
    be checked against the official IANA list + x-token, but we
    don't do that.
    """
    ctype = ContentType()
    recover = Uongo
    ikiwa sio value:
        ctype.defects.append(errors.HeaderMissingRequiredValue(
            "Missing content type specification"))
        rudisha ctype
    jaribu:
        token, value = get_token(value)
    tatizo errors.HeaderParseError:
        ctype.defects.append(errors.InvalidHeaderDefect(
            "Expected content maintype but found {!r}".format(value)))
        _find_mime_parameters(ctype, value)
        rudisha ctype
    ctype.append(token)
    # XXX: If we really want to follow the formal grammar we should make
    # mantype na subtype specialized TokenLists here.  Probably sio worth it.
    ikiwa sio value ama value[0] != '/':
        ctype.defects.append(errors.InvalidHeaderDefect(
            "Invalid content type"))
        ikiwa value:
            _find_mime_parameters(ctype, value)
        rudisha ctype
    ctype.maintype = token.value.strip().lower()
    ctype.append(ValueTerminal('/', 'content-type-separator'))
    value = value[1:]
    jaribu:
        token, value = get_token(value)
    tatizo errors.HeaderParseError:
        ctype.defects.append(errors.InvalidHeaderDefect(
            "Expected content subtype but found {!r}".format(value)))
        _find_mime_parameters(ctype, value)
        rudisha ctype
    ctype.append(token)
    ctype.subtype = token.value.strip().lower()
    ikiwa sio value:
        rudisha ctype
    ikiwa value[0] != ';':
        ctype.defects.append(errors.InvalidHeaderDefect(
            "Only parameters are valid after content type, but "
            "found {!r}".format(value)))
        # The RFC requires that a syntactically invalid content-type be treated
        # kama text/plain.  Perhaps we should postel this, but we should probably
        # only do that ikiwa we were checking the subtype value against IANA.
        toa ctype.maintype, ctype.subtype
        _find_mime_parameters(ctype, value)
        rudisha ctype
    ctype.append(ValueTerminal(';', 'parameter-separator'))
    ctype.append(parse_mime_parameters(value[1:]))
    rudisha ctype

eleza parse_content_disposition_header(value):
    """ disposition-type *( ";" parameter )

    """
    disp_header = ContentDisposition()
    ikiwa sio value:
        disp_header.defects.append(errors.HeaderMissingRequiredValue(
            "Missing content disposition"))
        rudisha disp_header
    jaribu:
        token, value = get_token(value)
    tatizo errors.HeaderParseError:
        disp_header.defects.append(errors.InvalidHeaderDefect(
            "Expected content disposition but found {!r}".format(value)))
        _find_mime_parameters(disp_header, value)
        rudisha disp_header
    disp_header.append(token)
    disp_header.content_disposition = token.value.strip().lower()
    ikiwa sio value:
        rudisha disp_header
    ikiwa value[0] != ';':
        disp_header.defects.append(errors.InvalidHeaderDefect(
            "Only parameters are valid after content disposition, but "
            "found {!r}".format(value)))
        _find_mime_parameters(disp_header, value)
        rudisha disp_header
    disp_header.append(ValueTerminal(';', 'parameter-separator'))
    disp_header.append(parse_mime_parameters(value[1:]))
    rudisha disp_header

eleza parse_content_transfer_encoding_header(value):
    """ mechanism

    """
    # We should probably validate the values, since the list ni fixed.
    cte_header = ContentTransferEncoding()
    ikiwa sio value:
        cte_header.defects.append(errors.HeaderMissingRequiredValue(
            "Missing content transfer encoding"))
        rudisha cte_header
    jaribu:
        token, value = get_token(value)
    tatizo errors.HeaderParseError:
        cte_header.defects.append(errors.InvalidHeaderDefect(
            "Expected content transfer encoding but found {!r}".format(value)))
    isipokua:
        cte_header.append(token)
        cte_header.cte = token.value.strip().lower()
    ikiwa sio value:
        rudisha cte_header
    wakati value:
        cte_header.defects.append(errors.InvalidHeaderDefect(
            "Extra text after content transfer encoding"))
        ikiwa value[0] kwenye PHRASE_ENDS:
            cte_header.append(ValueTerminal(value[0], 'misplaced-special'))
            value = value[1:]
        isipokua:
            token, value = get_phrase(value)
            cte_header.append(token)
    rudisha cte_header


#
# Header folding
#
# Header folding ni complex, ukijumuisha lots of rules na corner cases.  The
# following code does its best to obey the rules na handle the corner
# cases, but you can be sure there are few bugs:)
#
# This folder generally canonicalizes kama it goes, preferring the stringified
# version of each token.  The tokens contain information that supports the
# folder, including which tokens can be encoded kwenye which ways.
#
# Folded text ni accumulated kwenye a simple list of strings ('lines'), each
# one of which should be less than policy.max_line_length ('maxlen').
#

eleza _steal_trailing_WSP_if_exists(lines):
    wsp = ''
    ikiwa lines na lines[-1] na lines[-1][-1] kwenye WSP:
        wsp = lines[-1][-1]
        lines[-1] = lines[-1][:-1]
    rudisha wsp

eleza _refold_parse_tree(parse_tree, *, policy):
    """Return string of contents of parse_tree folded according to RFC rules.

    """
    # max_line_length 0/Tupu means no limit, ie: infinitely long.
    maxlen = policy.max_line_length ama sys.maxsize
    encoding = 'utf-8' ikiwa policy.utf8 isipokua 'us-ascii'
    lines = ['']
    last_ew = Tupu
    wrap_as_ew_blocked = 0
    want_encoding = Uongo
    end_ew_not_allowed = Terminal('', 'wrap_as_ew_blocked')
    parts = list(parse_tree)
    wakati parts:
        part = parts.pop(0)
        ikiwa part ni end_ew_not_allowed:
            wrap_as_ew_blocked -= 1
            endelea
        tstr = str(part)
        ikiwa part.token_type == 'ptext' na set(tstr) & SPECIALS:
            # Encode ikiwa tstr contains special characters.
            want_encoding = Kweli
        jaribu:
            tstr.encode(encoding)
            charset = encoding
        tatizo UnicodeEncodeError:
            ikiwa any(isinstance(x, errors.UndecodableBytesDefect)
                   kila x kwenye part.all_defects):
                charset = 'unknown-8bit'
            isipokua:
                # If policy.utf8 ni false this should really be taken kutoka a
                # 'charset' property on the policy.
                charset = 'utf-8'
            want_encoding = Kweli
        ikiwa part.token_type == 'mime-parameters':
            # Mime parameter folding (using RFC2231) ni extra special.
            _fold_mime_parameters(part, lines, maxlen, encoding)
            endelea
        ikiwa want_encoding na sio wrap_as_ew_blocked:
            ikiwa sio part.as_ew_allowed:
                want_encoding = Uongo
                last_ew = Tupu
                ikiwa part.syntactic_koma:
                    encoded_part = part.fold(policy=policy)[:-len(policy.linesep)]
                    ikiwa policy.linesep haiko kwenye encoded_part:
                        # It fits on a single line
                        ikiwa len(encoded_part) > maxlen - len(lines[-1]):
                            # But sio on this one, so start a new one.
                            newline = _steal_trailing_WSP_if_exists(lines)
                            # XXX what ikiwa encoded_part has no leading FWS?
                            lines.append(newline)
                        lines[-1] += encoded_part
                        endelea
                # Either this ni sio a major syntactic koma, so we don't
                # want it on a line by itself even ikiwa it fits, ama it
                # doesn't fit on a line by itself.  Either way, fall through
                # to unpacking the subparts na wrapping them.
            ikiwa sio hasattr(part, 'encode'):
                # It's sio a Terminal, do each piece individually.
                parts = list(part) + parts
            isipokua:
                # It's a terminal, wrap it kama an encoded word, possibly
                # combining it ukijumuisha previously encoded words ikiwa allowed.
                last_ew = _fold_as_ew(tstr, lines, maxlen, last_ew,
                                      part.ew_combine_allowed, charset)
            want_encoding = Uongo
            endelea
        ikiwa len(tstr) <= maxlen - len(lines[-1]):
            lines[-1] += tstr
            endelea
        # This part ni too long to fit.  The RFC wants us to koma at
        # "major syntactic komas", so unless we don't consider this
        # to be one, check ikiwa it will fit on the next line by itself.
        ikiwa (part.syntactic_koma na
                len(tstr) + 1 <= maxlen):
            newline = _steal_trailing_WSP_if_exists(lines)
            ikiwa newline ama part.startswith_fws():
                lines.append(newline + tstr)
                last_ew = Tupu
                endelea
        ikiwa sio hasattr(part, 'encode'):
            # It's sio a terminal, try folding the subparts.
            newparts = list(part)
            ikiwa sio part.as_ew_allowed:
                wrap_as_ew_blocked += 1
                newparts.append(end_ew_not_allowed)
            parts = newparts + parts
            endelea
        ikiwa part.as_ew_allowed na sio wrap_as_ew_blocked:
            # It doesn't need CTE encoding, but encode it anyway so we can
            # wrap it.
            parts.insert(0, part)
            want_encoding = Kweli
            endelea
        # We can't figure out how to wrap, it, so give up.
        newline = _steal_trailing_WSP_if_exists(lines)
        ikiwa newline ama part.startswith_fws():
            lines.append(newline + tstr)
        isipokua:
            # We can't fold it onto the next line either...
            lines[-1] += tstr
    rudisha policy.linesep.join(lines) + policy.linesep

eleza _fold_as_ew(to_encode, lines, maxlen, last_ew, ew_combine_allowed, charset):
    """Fold string to_encode into lines kama encoded word, combining ikiwa allowed.
    Return the new value kila last_ew, ama Tupu ikiwa ew_combine_allowed ni Uongo.

    If there ni already an encoded word kwenye the last line of lines (indicated by
    a non-Tupu value kila last_ew) na ew_combine_allowed ni true, decode the
    existing ew, combine it ukijumuisha to_encode, na re-encode.  Otherwise, encode
    to_encode.  In either case, split to_encode kama necessary so that the
    encoded segments fit within maxlen.

    """
    ikiwa last_ew ni sio Tupu na ew_combine_allowed:
        to_encode = str(
            get_unstructured(lines[-1][last_ew:] + to_encode))
        lines[-1] = lines[-1][:last_ew]
    ikiwa to_encode[0] kwenye WSP:
        # We're joining this to non-encoded text, so don't encode
        # the leading blank.
        leading_wsp = to_encode[0]
        to_encode = to_encode[1:]
        ikiwa (len(lines[-1]) == maxlen):
            lines.append(_steal_trailing_WSP_if_exists(lines))
        lines[-1] += leading_wsp
    trailing_wsp = ''
    ikiwa to_encode[-1] kwenye WSP:
        # Likewise kila the trailing space.
        trailing_wsp = to_encode[-1]
        to_encode = to_encode[:-1]
    new_last_ew = len(lines[-1]) ikiwa last_ew ni Tupu isipokua last_ew

    encode_as = 'utf-8' ikiwa charset == 'us-ascii' isipokua charset

    # The RFC2047 chrome takes up 7 characters plus the length
    # of the charset name.
    chrome_len = len(encode_as) + 7

    ikiwa (chrome_len + 1) >= maxlen:
        ashiria errors.HeaderParseError(
            "max_line_length ni too small to fit an encoded word")

    wakati to_encode:
        remaining_space = maxlen - len(lines[-1])
        text_space = remaining_space - chrome_len
        ikiwa text_space <= 0:
            lines.append(' ')
            endelea

        to_encode_word = to_encode[:text_space]
        encoded_word = _ew.encode(to_encode_word, charset=encode_as)
        excess = len(encoded_word) - remaining_space
        wakati excess > 0:
            # Since the chunk to encode ni guaranteed to fit into less than 100 characters,
            # shrinking it by one at a time shouldn't take long.
            to_encode_word = to_encode_word[:-1]
            encoded_word = _ew.encode(to_encode_word, charset=encode_as)
            excess = len(encoded_word) - remaining_space
        lines[-1] += encoded_word
        to_encode = to_encode[len(to_encode_word):]

        ikiwa to_encode:
            lines.append(' ')
            new_last_ew = len(lines[-1])
    lines[-1] += trailing_wsp
    rudisha new_last_ew ikiwa ew_combine_allowed isipokua Tupu

eleza _fold_mime_parameters(part, lines, maxlen, encoding):
    """Fold TokenList 'part' into the 'lines' list kama mime parameters.

    Using the decoded list of parameters na values, format them according to
    the RFC rules, including using RFC2231 encoding ikiwa the value cannot be
    expressed kwenye 'encoding' and/or the parameter+value ni too long to fit
    within 'maxlen'.

    """
    # Special case kila RFC2231 encoding: start kutoka decoded values na use
    # RFC2231 encoding iff needed.
    #
    # Note that the 1 na 2s being added to the length calculations are
    # accounting kila the possibly-needed spaces na semicolons we'll be adding.
    #
    kila name, value kwenye part.params:
        # XXX What ikiwa this ';' puts us over maxlen the first time through the
        # loop?  We should split the header value onto a newline kwenye that case,
        # but to do that we need to recognize the need earlier ama reparse the
        # header, so I'm going to ignore that bug kila now.  It'll only put us
        # one character over.
        ikiwa sio lines[-1].rstrip().endswith(';'):
            lines[-1] += ';'
        charset = encoding
        error_handler = 'strict'
        jaribu:
            value.encode(encoding)
            encoding_required = Uongo
        tatizo UnicodeEncodeError:
            encoding_required = Kweli
            ikiwa utils._has_surrogates(value):
                charset = 'unknown-8bit'
                error_handler = 'surrogateescape'
            isipokua:
                charset = 'utf-8'
        ikiwa encoding_required:
            encoded_value = urllib.parse.quote(
                value, safe='', errors=error_handler)
            tstr = "{}*={}''{}".format(name, charset, encoded_value)
        isipokua:
            tstr = '{}={}'.format(name, quote_string(value))
        ikiwa len(lines[-1]) + len(tstr) + 1 < maxlen:
            lines[-1] = lines[-1] + ' ' + tstr
            endelea
        lasivyo len(tstr) + 2 <= maxlen:
            lines.append(' ' + tstr)
            endelea
        # We need multiple sections.  We are allowed to mix encoded na
        # non-encoded sections, but we aren't going to.  We'll encode them all.
        section = 0
        extra_chrome = charset + "''"
        wakati value:
            chrome_len = len(name) + len(str(section)) + 3 + len(extra_chrome)
            ikiwa maxlen <= chrome_len + 3:
                # We need room kila the leading blank, the trailing semicolon,
                # na at least one character of the value.  If we don't
                # have that, we'd be stuck, so kwenye that case fall back to
                # the RFC standard width.
                maxlen = 78
            splitpoint = maxchars = maxlen - chrome_len - 2
            wakati Kweli:
                partial = value[:splitpoint]
                encoded_value = urllib.parse.quote(
                    partial, safe='', errors=error_handler)
                ikiwa len(encoded_value) <= maxchars:
                    koma
                splitpoint -= 1
            lines.append(" {}*{}*={}{}".format(
                name, section, extra_chrome, encoded_value))
            extra_chrome = ''
            section += 1
            value = value[splitpoint:]
            ikiwa value:
                lines[-1] += ';'
