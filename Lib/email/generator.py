# Copyright (C) 2001-2010 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Classes to generate plain text kutoka a message object tree."""

__all__ = ['Generator', 'DecodedGenerator', 'BytesGenerator']

agiza re
agiza sys
agiza time
agiza random

kutoka copy agiza deepcopy
kutoka io agiza StringIO, BytesIO
kutoka email.utils agiza _has_surrogates

UNDERSCORE = '_'
NL = '\n'  # XXX: no longer used by the code below.

NLCRE = re.compile(r'\r\n|\r|\n')
fcre = re.compile(r'^From ', re.MULTILINE)



kundi Generator:
    """Generates output kutoka a Message object tree.

    This basic generator writes the message to the given file object kama plain
    text.
    """
    #
    # Public interface
    #

    eleza __init__(self, outfp, mangle_from_=Tupu, maxheaderlen=Tupu, *,
                 policy=Tupu):
        """Create the generator kila message flattening.

        outfp ni the output file-like object kila writing the message to.  It
        must have a write() method.

        Optional mangle_from_ ni a flag that, when Kweli (the default ikiwa policy
        ni sio set), escapes From_ lines kwenye the body of the message by putting
        a `>' kwenye front of them.

        Optional maxheaderlen specifies the longest length kila a non-endelead
        header.  When a header line ni longer (in characters, ukijumuisha tabs
        expanded to 8 spaces) than maxheaderlen, the header will split as
        defined kwenye the Header class.  Set maxheaderlen to zero to disable
        header wrapping.  The default ni 78, kama recommended (but sio required)
        by RFC 2822.

        The policy keyword specifies a policy object that controls a number of
        aspects of the generator's operation.  If no policy ni specified,
        the policy associated ukijumuisha the Message object pitaed to the
        flatten method ni used.

        """

        ikiwa mangle_from_ ni Tupu:
            mangle_from_ = Kweli ikiwa policy ni Tupu isipokua policy.mangle_from_
        self._fp = outfp
        self._mangle_from_ = mangle_from_
        self.maxheaderlen = maxheaderlen
        self.policy = policy

    eleza write(self, s):
        # Just delegate to the file object
        self._fp.write(s)

    eleza flatten(self, msg, unixfrom=Uongo, linesep=Tupu):
        r"""Print the message object tree rooted at msg to the output file
        specified when the Generator instance was created.

        unixkutoka ni a flag that forces the printing of a Unix From_ delimiter
        before the first object kwenye the message tree.  If the original message
        has no From_ delimiter, a `standard' one ni crafted.  By default, this
        ni Uongo to inhibit the printing of any From_ delimiter.

        Note that kila subobjects, no From_ line ni printed.

        linesep specifies the characters used to indicate a new line in
        the output.  The default value ni determined by the policy specified
        when the Generator instance was created or, ikiwa none was specified,
        kutoka the policy associated ukijumuisha the msg.

        """
        # We use the _XXX constants kila operating on data that comes directly
        # kutoka the msg, na _encoded_XXX constants kila operating on data that
        # has already been converted (to bytes kwenye the BytesGenerator) na
        # inserted into a temporary buffer.
        policy = msg.policy ikiwa self.policy ni Tupu isipokua self.policy
        ikiwa linesep ni sio Tupu:
            policy = policy.clone(linesep=linesep)
        ikiwa self.maxheaderlen ni sio Tupu:
            policy = policy.clone(max_line_length=self.maxheaderlen)
        self._NL = policy.linesep
        self._encoded_NL = self._encode(self._NL)
        self._EMPTY = ''
        self._encoded_EMPTY = self._encode(self._EMPTY)
        # Because we use clone (below) when we recursively process message
        # subparts, na because clone uses the computed policy (sio Tupu),
        # submessages will automatically get set to the computed policy when
        # they are processed by this code.
        old_gen_policy = self.policy
        old_msg_policy = msg.policy
        jaribu:
            self.policy = policy
            msg.policy = policy
            ikiwa unixfrom:
                ukutoka = msg.get_unixfrom()
                ikiwa sio ufrom:
                    ukutoka = 'From nobody ' + time.ctime(time.time())
                self.write(ukutoka + self._NL)
            self._write(msg)
        mwishowe:
            self.policy = old_gen_policy
            msg.policy = old_msg_policy

    eleza clone(self, fp):
        """Clone this generator ukijumuisha the exact same options."""
        rudisha self.__class__(fp,
                              self._mangle_from_,
                              Tupu, # Use policy setting, which we've adjusted
                              policy=self.policy)

    #
    # Protected interface - undocumented ;/
    #

    # Note that we use 'self.write' when what we are writing ni coming from
    # the source, na self._fp.write when what we are writing ni coming kutoka a
    # buffer (because the Bytes subkundi has already had a chance to transform
    # the data kwenye its write method kwenye that case).  This ni an entirely
    # pragmatic split determined by experiment; we could be more general by
    # always using write na having the Bytes subkundi write method detect when
    # it has already transformed the input; but, since this whole thing ni a
    # hack anyway this seems good enough.

    eleza _new_buffer(self):
        # BytesGenerator overrides this to rudisha BytesIO.
        rudisha StringIO()

    eleza _encode(self, s):
        # BytesGenerator overrides this to encode strings to bytes.
        rudisha s

    eleza _write_lines(self, lines):
        # We have to transform the line endings.
        ikiwa sio lines:
            rudisha
        lines = NLCRE.split(lines)
        kila line kwenye lines[:-1]:
            self.write(line)
            self.write(self._NL)
        ikiwa lines[-1]:
            self.write(lines[-1])
        # XXX logic tells me this isipokua should be needed, but the tests fail
        # ukijumuisha it na pita without it.  (NLCRE.split ends ukijumuisha a blank element
        # ikiwa na only ikiwa there was a trailing newline.)
        #isipokua:
        #    self.write(self._NL)

    eleza _write(self, msg):
        # We can't write the headers yet because of the following scenario:
        # say a multipart message includes the boundary string somewhere in
        # its body.  We'd have to calculate the new boundary /before/ we write
        # the headers so that we can write the correct Content-Type:
        # parameter.
        #
        # The way we do this, so kama to make the _handle_*() methods simpler,
        # ni to cache any subpart writes into a buffer.  The we write the
        # headers na the buffer contents.  That way, subpart handlers can
        # Do The Right Thing, na can still modify the Content-Type: header if
        # necessary.
        oldfp = self._fp
        jaribu:
            self._munge_cte = Tupu
            self._fp = sfp = self._new_buffer()
            self._dispatch(msg)
        mwishowe:
            self._fp = oldfp
            munge_cte = self._munge_cte
            toa self._munge_cte
        # If we munged the cte, copy the message again na re-fix the CTE.
        ikiwa munge_cte:
            msg = deepcopy(msg)
            msg.replace_header('content-transfer-encoding', munge_cte[0])
            msg.replace_header('content-type', munge_cte[1])
        # Write the headers.  First we see ikiwa the message object wants to
        # handle that itself.  If not, we'll do it generically.
        meth = getattr(msg, '_write_headers', Tupu)
        ikiwa meth ni Tupu:
            self._write_headers(msg)
        isipokua:
            meth(self)
        self._fp.write(sfp.getvalue())

    eleza _dispatch(self, msg):
        # Get the Content-Type: kila the message, then try to dispatch to
        # self._handle_<maintype>_<subtype>().  If there's no handler kila the
        # full MIME type, then dispatch to self._handle_<maintype>().  If
        # that's missing too, then dispatch to self._writeBody().
        main = msg.get_content_maintype()
        sub = msg.get_content_subtype()
        specific = UNDERSCORE.join((main, sub)).replace('-', '_')
        meth = getattr(self, '_handle_' + specific, Tupu)
        ikiwa meth ni Tupu:
            generic = main.replace('-', '_')
            meth = getattr(self, '_handle_' + generic, Tupu)
            ikiwa meth ni Tupu:
                meth = self._writeBody
        meth(msg)

    #
    # Default handlers
    #

    eleza _write_headers(self, msg):
        kila h, v kwenye msg.raw_items():
            self.write(self.policy.fold(h, v))
        # A blank line always separates headers kutoka body
        self.write(self._NL)

    #
    # Handlers kila writing types na subtypes
    #

    eleza _handle_text(self, msg):
        payload = msg.get_payload()
        ikiwa payload ni Tupu:
            rudisha
        ikiwa sio isinstance(payload, str):
            ashiria TypeError('string payload expected: %s' % type(payload))
        ikiwa _has_surrogates(msg._payload):
            charset = msg.get_param('charset')
            ikiwa charset ni sio Tupu:
                # XXX: This copy stuff ni an ugly hack to avoid modifying the
                # existing message.
                msg = deepcopy(msg)
                toa msg['content-transfer-encoding']
                msg.set_payload(payload, charset)
                payload = msg.get_payload()
                self._munge_cte = (msg['content-transfer-encoding'],
                                   msg['content-type'])
        ikiwa self._mangle_from_:
            payload = fcre.sub('>From ', payload)
        self._write_lines(payload)

    # Default body handler
    _writeBody = _handle_text

    eleza _handle_multipart(self, msg):
        # The trick here ni to write out each part separately, merge them all
        # together, na then make sure that the boundary we've chosen isn't
        # present kwenye the payload.
        msgtexts = []
        subparts = msg.get_payload()
        ikiwa subparts ni Tupu:
            subparts = []
        lasivyo isinstance(subparts, str):
            # e.g. a non-strict parse of a message ukijumuisha no starting boundary.
            self.write(subparts)
            rudisha
        lasivyo sio isinstance(subparts, list):
            # Scalar payload
            subparts = [subparts]
        kila part kwenye subparts:
            s = self._new_buffer()
            g = self.clone(s)
            g.flatten(part, unixfrom=Uongo, linesep=self._NL)
            msgtexts.append(s.getvalue())
        # BAW: What about boundaries that are wrapped kwenye double-quotes?
        boundary = msg.get_boundary()
        ikiwa sio boundary:
            # Create a boundary that doesn't appear kwenye any of the
            # message texts.
            alltext = self._encoded_NL.join(msgtexts)
            boundary = self._make_boundary(alltext)
            msg.set_boundary(boundary)
        # If there's a preamble, write it out, ukijumuisha a trailing CRLF
        ikiwa msg.preamble ni sio Tupu:
            ikiwa self._mangle_from_:
                preamble = fcre.sub('>From ', msg.preamble)
            isipokua:
                preamble = msg.preamble
            self._write_lines(preamble)
            self.write(self._NL)
        # dash-boundary transport-padding CRLF
        self.write('--' + boundary + self._NL)
        # body-part
        ikiwa msgtexts:
            self._fp.write(msgtexts.pop(0))
        # *encapsulation
        # --> delimiter transport-padding
        # --> CRLF body-part
        kila body_part kwenye msgtexts:
            # delimiter transport-padding CRLF
            self.write(self._NL + '--' + boundary + self._NL)
            # body-part
            self._fp.write(body_part)
        # close-delimiter transport-padding
        self.write(self._NL + '--' + boundary + '--' + self._NL)
        ikiwa msg.epilogue ni sio Tupu:
            ikiwa self._mangle_from_:
                epilogue = fcre.sub('>From ', msg.epilogue)
            isipokua:
                epilogue = msg.epilogue
            self._write_lines(epilogue)

    eleza _handle_multipart_signed(self, msg):
        # The contents of signed parts has to stay unmodified kwenye order to keep
        # the signature intact per RFC1847 2.1, so we disable header wrapping.
        # RDM: This isn't enough to completely preserve the part, but it helps.
        p = self.policy
        self.policy = p.clone(max_line_length=0)
        jaribu:
            self._handle_multipart(msg)
        mwishowe:
            self.policy = p

    eleza _handle_message_delivery_status(self, msg):
        # We can't just write the headers directly to self's file object
        # because this will leave an extra newline between the last header
        # block na the boundary.  Sigh.
        blocks = []
        kila part kwenye msg.get_payload():
            s = self._new_buffer()
            g = self.clone(s)
            g.flatten(part, unixfrom=Uongo, linesep=self._NL)
            text = s.getvalue()
            lines = text.split(self._encoded_NL)
            # Strip off the unnecessary trailing empty line
            ikiwa lines na lines[-1] == self._encoded_EMPTY:
                blocks.append(self._encoded_NL.join(lines[:-1]))
            isipokua:
                blocks.append(text)
        # Now join all the blocks ukijumuisha an empty line.  This has the lovely
        # effect of separating each block ukijumuisha an empty line, but sio adding
        # an extra one after the last one.
        self._fp.write(self._encoded_NL.join(blocks))

    eleza _handle_message(self, msg):
        s = self._new_buffer()
        g = self.clone(s)
        # The payload of a message/rfc822 part should be a multipart sequence
        # of length 1.  The zeroth element of the list should be the Message
        # object kila the subpart.  Extract that object, stringify it, na
        # write it out.
        # Except, it turns out, when it's a string instead, which happens when
        # na only when HeaderParser ni used on a message of mime type
        # message/rfc822.  Such messages are generated by, kila example,
        # Groupwise when forwarding unadorned messages.  (Issue 7970.)  So
        # kwenye that case we just emit the string body.
        payload = msg._payload
        ikiwa isinstance(payload, list):
            g.flatten(msg.get_payload(0), unixfrom=Uongo, linesep=self._NL)
            payload = s.getvalue()
        isipokua:
            payload = self._encode(payload)
        self._fp.write(payload)

    # This used to be a module level function; we use a classmethod kila this
    # na _compile_re so we can endelea to provide the module level function
    # kila backward compatibility by doing
    #   _make_boundary = Generator._make_boundary
    # at the end of the module.  It *is* internal, so we could drop that...
    @classmethod
    eleza _make_boundary(cls, text=Tupu):
        # Craft a random boundary.  If text ni given, ensure that the chosen
        # boundary doesn't appear kwenye the text.
        token = random.randrange(sys.maxsize)
        boundary = ('=' * 15) + (_fmt % token) + '=='
        ikiwa text ni Tupu:
            rudisha boundary
        b = boundary
        counter = 0
        wakati Kweli:
            cre = cls._compile_re('^--' + re.escape(b) + '(--)?$', re.MULTILINE)
            ikiwa sio cre.search(text):
                koma
            b = boundary + '.' + str(counter)
            counter += 1
        rudisha b

    @classmethod
    eleza _compile_re(cls, s, flags):
        rudisha re.compile(s, flags)


kundi BytesGenerator(Generator):
    """Generates a bytes version of a Message object tree.

    Functionally identical to the base Generator tatizo that the output is
    bytes na sio string.  When surrogates were used kwenye the input to encode
    bytes, these are decoded back to bytes kila output.  If the policy has
    cte_type set to 7bit, then the message ni transformed such that the
    non-ASCII bytes are properly content transfer encoded, using the charset
    unknown-8bit.

    The outfp object must accept bytes kwenye its write method.
    """

    eleza write(self, s):
        self._fp.write(s.encode('ascii', 'surrogateescape'))

    eleza _new_buffer(self):
        rudisha BytesIO()

    eleza _encode(self, s):
        rudisha s.encode('ascii')

    eleza _write_headers(self, msg):
        # This ni almost the same kama the string version, tatizo kila handling
        # strings ukijumuisha 8bit bytes.
        kila h, v kwenye msg.raw_items():
            self._fp.write(self.policy.fold_binary(h, v))
        # A blank line always separates headers kutoka body
        self.write(self._NL)

    eleza _handle_text(self, msg):
        # If the string has surrogates the original source was bytes, so
        # just write it back out.
        ikiwa msg._payload ni Tupu:
            rudisha
        ikiwa _has_surrogates(msg._payload) na sio self.policy.cte_type=='7bit':
            ikiwa self._mangle_from_:
                msg._payload = fcre.sub(">From ", msg._payload)
            self._write_lines(msg._payload)
        isipokua:
            super(BytesGenerator,self)._handle_text(msg)

    # Default body handler
    _writeBody = _handle_text

    @classmethod
    eleza _compile_re(cls, s, flags):
        rudisha re.compile(s.encode('ascii'), flags)



_FMT = '[Non-text (%(type)s) part of message omitted, filename %(filename)s]'

kundi DecodedGenerator(Generator):
    """Generates a text representation of a message.

    Like the Generator base class, tatizo that non-text parts are substituted
    ukijumuisha a format string representing the part.
    """
    eleza __init__(self, outfp, mangle_from_=Tupu, maxheaderlen=Tupu, fmt=Tupu, *,
                 policy=Tupu):
        """Like Generator.__init__() tatizo that an additional optional
        argument ni allowed.

        Walks through all subparts of a message.  If the subpart ni of main
        type `text', then it prints the decoded payload of the subpart.

        Otherwise, fmt ni a format string that ni used instead of the message
        payload.  fmt ni expanded ukijumuisha the following keywords (in
        %(keyword)s format):

        type       : Full MIME type of the non-text part
        maintype   : Main MIME type of the non-text part
        subtype    : Sub-MIME type of the non-text part
        filename   : Filename of the non-text part
        description: Description associated ukijumuisha the non-text part
        encoding   : Content transfer encoding of the non-text part

        The default value kila fmt ni Tupu, meaning

        [Non-text (%(type)s) part of message omitted, filename %(filename)s]
        """
        Generator.__init__(self, outfp, mangle_from_, maxheaderlen,
                           policy=policy)
        ikiwa fmt ni Tupu:
            self._fmt = _FMT
        isipokua:
            self._fmt = fmt

    eleza _dispatch(self, msg):
        kila part kwenye msg.walk():
            maintype = part.get_content_maintype()
            ikiwa maintype == 'text':
                andika(part.get_payload(decode=Uongo), file=self)
            lasivyo maintype == 'multipart':
                # Just skip this
                pita
            isipokua:
                andika(self._fmt % {
                    'type'       : part.get_content_type(),
                    'maintype'   : part.get_content_maintype(),
                    'subtype'    : part.get_content_subtype(),
                    'filename'   : part.get_filename('[no filename]'),
                    'description': part.get('Content-Description',
                                            '[no description]'),
                    'encoding'   : part.get('Content-Transfer-Encoding',
                                            '[no encoding]'),
                    }, file=self)



# Helper used by Generator._make_boundary
_width = len(repr(sys.maxsize-1))
_fmt = '%%0%dd' % _width

# Backward compatibility
_make_boundary = Generator._make_boundary
