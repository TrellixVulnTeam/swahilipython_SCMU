# Copyright (C) 2001-2007 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Basic message object kila the email package object model."""

__all__ = ['Message', 'EmailMessage']

agiza re
agiza uu
agiza quopri
kutoka io agiza BytesIO, StringIO

# Intrapackage imports
kutoka email agiza utils
kutoka email agiza errors
kutoka email._policybase agiza Policy, compat32
kutoka email agiza charset kama _charset
kutoka email._encoded_words agiza decode_b
Charset = _charset.Charset

SEMISPACE = '; '

# Regular expression that matches `special' characters kwenye parameters, the
# existence of which force quoting of the parameter value.
tspecials = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')


eleza _splitparam(param):
    # Split header parameters.  BAW: this may be too simple.  It isn't
    # strictly RFC 2045 (section 5.1) compliant, but it catches most headers
    # found kwenye the wild.  We may eventually need a full fledged parser.
    # RDM: we might have a Header here; kila now just stringify it.
    a, sep, b = str(param).partition(';')
    ikiwa sio sep:
        rudisha a.strip(), Tupu
    rudisha a.strip(), b.strip()

eleza _formatparam(param, value=Tupu, quote=Kweli):
    """Convenience function to format na rudisha a key=value pair.

    This will quote the value ikiwa needed ama ikiwa quote ni true.  If value ni a
    three tuple (charset, language, value), it will be encoded according
    to RFC2231 rules.  If it contains non-ascii characters it will likewise
    be encoded according to RFC2231 rules, using the utf-8 charset na
    a null language.
    """
    ikiwa value ni sio Tupu na len(value) > 0:
        # A tuple ni used kila RFC 2231 encoded parameter values where items
        # are (charset, language, value).  charset ni a string, sio a Charset
        # instance.  RFC 2231 encoded values are never quoted, per RFC.
        ikiwa isinstance(value, tuple):
            # Encode kama per RFC 2231
            param += '*'
            value = utils.encode_rfc2231(value[2], value[0], value[1])
            rudisha '%s=%s' % (param, value)
        isipokua:
            jaribu:
                value.encode('ascii')
            tatizo UnicodeEncodeError:
                param += '*'
                value = utils.encode_rfc2231(value, 'utf-8', '')
                rudisha '%s=%s' % (param, value)
        # BAW: Please check this.  I think that ikiwa quote ni set it should
        # force quoting even ikiwa sio necessary.
        ikiwa quote ama tspecials.search(value):
            rudisha '%s="%s"' % (param, utils.quote(value))
        isipokua:
            rudisha '%s=%s' % (param, value)
    isipokua:
        rudisha param

eleza _parseparam(s):
    # RDM This might be a Header, so kila now stringify it.
    s = ';' + str(s)
    plist = []
    wakati s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        wakati end > 0 na (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)
        ikiwa end < 0:
            end = len(s)
        f = s[:end]
        ikiwa '=' kwenye f:
            i = f.index('=')
            f = f[:i].strip().lower() + '=' + f[i+1:].strip()
        plist.append(f.strip())
        s = s[end:]
    rudisha plist


eleza _unquotevalue(value):
    # This ni different than utils.collapse_rfc2231_value() because it doesn't
    # try to convert the value to a unicode.  Message.get_param() na
    # Message.get_params() are both currently defined to rudisha the tuple in
    # the face of RFC 2231 parameters.
    ikiwa isinstance(value, tuple):
        rudisha value[0], value[1], utils.unquote(value[2])
    isipokua:
        rudisha utils.unquote(value)



kundi Message:
    """Basic message object.

    A message object ni defined kama something that has a bunch of RFC 2822
    headers na a payload.  It may optionally have an envelope header
    (a.k.a. Unix-From ama From_ header).  If the message ni a container (i.e. a
    multipart ama a message/rfc822), then the payload ni a list of Message
    objects, otherwise it ni a string.

    Message objects implement part of the `mapping' interface, which assumes
    there ni exactly one occurrence of the header per message.  Some headers
    do kwenye fact appear multiple times (e.g. Received) na kila those headers,
    you must use the explicit API to set ama get all the headers.  Not all of
    the mapping methods are implemented.
    """
    eleza __init__(self, policy=compat32):
        self.policy = policy
        self._headers = []
        self._unixkutoka = Tupu
        self._payload = Tupu
        self._charset = Tupu
        # Defaults kila multipart messages
        self.preamble = self.epilogue = Tupu
        self.defects = []
        # Default content type
        self._default_type = 'text/plain'

    eleza __str__(self):
        """Return the entire formatted message kama a string.
        """
        rudisha self.as_string()

    eleza as_string(self, unixfrom=Uongo, maxheaderlen=0, policy=Tupu):
        """Return the entire formatted message kama a string.

        Optional 'unixfrom', when true, means include the Unix From_ envelope
        header.  For backward compatibility reasons, ikiwa maxheaderlen is
        sio specified it defaults to 0, so you must override it explicitly
        ikiwa you want a different maxheaderlen.  'policy' ni pitaed to the
        Generator instance used to serialize the mesasge; ikiwa it ni not
        specified the policy associated ukijumuisha the message instance ni used.

        If the message object contains binary data that ni sio encoded
        according to RFC standards, the non-compliant data will be replaced by
        unicode "unknown character" code points.
        """
        kutoka email.generator agiza Generator
        policy = self.policy ikiwa policy ni Tupu isipokua policy
        fp = StringIO()
        g = Generator(fp,
                      mangle_from_=Uongo,
                      maxheaderlen=maxheaderlen,
                      policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        rudisha fp.getvalue()

    eleza __bytes__(self):
        """Return the entire formatted message kama a bytes object.
        """
        rudisha self.as_bytes()

    eleza as_bytes(self, unixfrom=Uongo, policy=Tupu):
        """Return the entire formatted message kama a bytes object.

        Optional 'unixfrom', when true, means include the Unix From_ envelope
        header.  'policy' ni pitaed to the BytesGenerator instance used to
        serialize the message; ikiwa sio specified the policy associated with
        the message instance ni used.
        """
        kutoka email.generator agiza BytesGenerator
        policy = self.policy ikiwa policy ni Tupu isipokua policy
        fp = BytesIO()
        g = BytesGenerator(fp, mangle_from_=Uongo, policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        rudisha fp.getvalue()

    eleza is_multipart(self):
        """Return Kweli ikiwa the message consists of multiple parts."""
        rudisha isinstance(self._payload, list)

    #
    # Unix From_ line
    #
    eleza set_unixfrom(self, unixfrom):
        self._unixkutoka = unixfrom

    eleza get_unixfrom(self):
        rudisha self._unixfrom

    #
    # Payload manipulation.
    #
    eleza attach(self, payload):
        """Add the given payload to the current payload.

        The current payload will always be a list of objects after this method
        ni called.  If you want to set the payload to a scalar object, use
        set_payload() instead.
        """
        ikiwa self._payload ni Tupu:
            self._payload = [payload]
        isipokua:
            jaribu:
                self._payload.append(payload)
            tatizo AttributeError:
                ashiria TypeError("Attach ni sio valid on a message ukijumuisha a"
                                " non-multipart payload")

    eleza get_payload(self, i=Tupu, decode=Uongo):
        """Return a reference to the payload.

        The payload will either be a list object ama a string.  If you mutate
        the list object, you modify the message's payload kwenye place.  Optional
        i returns that index into the payload.

        Optional decode ni a flag indicating whether the payload should be
        decoded ama not, according to the Content-Transfer-Encoding header
        (default ni Uongo).

        When Kweli na the message ni sio a multipart, the payload will be
        decoded ikiwa this header's value ni `quoted-printable' ama `base64'.  If
        some other encoding ni used, ama the header ni missing, ama ikiwa the
        payload has bogus data (i.e. bogus base64 ama uuencoded data), the
        payload ni returned as-is.

        If the message ni a multipart na the decode flag ni Kweli, then Tupu
        ni returned.
        """
        # Here ni the logic table kila this code, based on the email5.0.0 code:
        #   i     decode  is_multipart  result
        # ------  ------  ------------  ------------------------------
        #  Tupu   Kweli    Kweli          Tupu
        #   i     Kweli    Kweli          Tupu
        #  Tupu   Uongo   Kweli          _payload (a list)
        #   i     Uongo   Kweli          _payload element i (a Message)
        #   i     Uongo   Uongo         error (sio a list)
        #   i     Kweli    Uongo         error (sio a list)
        #  Tupu   Uongo   Uongo         _payload
        #  Tupu   Kweli    Uongo         _payload decoded (bytes)
        # Note that Barry planned to factor out the 'decode' case, but that
        # isn't so easy now that we handle the 8 bit data, which needs to be
        # converted kwenye both the decode na non-decode path.
        ikiwa self.is_multipart():
            ikiwa decode:
                rudisha Tupu
            ikiwa i ni Tupu:
                rudisha self._payload
            isipokua:
                rudisha self._payload[i]
        # For backward compatibility, Use isinstance na this error message
        # instead of the more logical is_multipart test.
        ikiwa i ni sio Tupu na sio isinstance(self._payload, list):
            ashiria TypeError('Expected list, got %s' % type(self._payload))
        payload = self._payload
        # cte might be a Header, so kila now stringify it.
        cte = str(self.get('content-transfer-encoding', '')).lower()
        # payload may be bytes here.
        ikiwa isinstance(payload, str):
            ikiwa utils._has_surrogates(payload):
                bpayload = payload.encode('ascii', 'surrogateescape')
                ikiwa sio decode:
                    jaribu:
                        payload = bpayload.decode(self.get_param('charset', 'ascii'), 'replace')
                    tatizo LookupError:
                        payload = bpayload.decode('ascii', 'replace')
            lasivyo decode:
                jaribu:
                    bpayload = payload.encode('ascii')
                tatizo UnicodeError:
                    # This won't happen kila RFC compliant messages (messages
                    # containing only ASCII code points kwenye the unicode input).
                    # If it does happen, turn the string into bytes kwenye a way
                    # guaranteed sio to fail.
                    bpayload = payload.encode('raw-unicode-escape')
        ikiwa sio decode:
            rudisha payload
        ikiwa cte == 'quoted-printable':
            rudisha quopri.decodestring(bpayload)
        lasivyo cte == 'base64':
            # XXX: this ni a bit of a hack; decode_b should probably be factored
            # out somewhere, but I haven't figured out where yet.
            value, defects = decode_b(b''.join(bpayload.splitlines()))
            kila defect kwenye defects:
                self.policy.handle_defect(self, defect)
            rudisha value
        lasivyo cte kwenye ('x-uuencode', 'uuencode', 'uue', 'x-uue'):
            in_file = BytesIO(bpayload)
            out_file = BytesIO()
            jaribu:
                uu.decode(in_file, out_file, quiet=Kweli)
                rudisha out_file.getvalue()
            tatizo uu.Error:
                # Some decoding problem
                rudisha bpayload
        ikiwa isinstance(payload, str):
            rudisha bpayload
        rudisha payload

    eleza set_payload(self, payload, charset=Tupu):
        """Set the payload to the given value.

        Optional charset sets the message's default character set.  See
        set_charset() kila details.
        """
        ikiwa hasattr(payload, 'encode'):
            ikiwa charset ni Tupu:
                self._payload = payload
                return
            ikiwa sio isinstance(charset, Charset):
                charset = Charset(charset)
            payload = payload.encode(charset.output_charset)
        ikiwa hasattr(payload, 'decode'):
            self._payload = payload.decode('ascii', 'surrogateescape')
        isipokua:
            self._payload = payload
        ikiwa charset ni sio Tupu:
            self.set_charset(charset)

    eleza set_charset(self, charset):
        """Set the charset of the payload to a given character set.

        charset can be a Charset instance, a string naming a character set, ama
        Tupu.  If it ni a string it will be converted to a Charset instance.
        If charset ni Tupu, the charset parameter will be removed kutoka the
        Content-Type field.  Anything isipokua will generate a TypeError.

        The message will be assumed to be of type text/* encoded with
        charset.input_charset.  It will be converted to charset.output_charset
        na encoded properly, ikiwa needed, when generating the plain text
        representation of the message.  MIME headers (MIME-Version,
        Content-Type, Content-Transfer-Encoding) will be added kama needed.
        """
        ikiwa charset ni Tupu:
            self.del_param('charset')
            self._charset = Tupu
            return
        ikiwa sio isinstance(charset, Charset):
            charset = Charset(charset)
        self._charset = charset
        ikiwa 'MIME-Version' haiko kwenye self:
            self.add_header('MIME-Version', '1.0')
        ikiwa 'Content-Type' haiko kwenye self:
            self.add_header('Content-Type', 'text/plain',
                            charset=charset.get_output_charset())
        isipokua:
            self.set_param('charset', charset.get_output_charset())
        ikiwa charset != charset.get_output_charset():
            self._payload = charset.body_encode(self._payload)
        ikiwa 'Content-Transfer-Encoding' haiko kwenye self:
            cte = charset.get_body_encoding()
            jaribu:
                cte(self)
            tatizo TypeError:
                # This 'if' ni kila backward compatibility, it allows unicode
                # through even though that won't work correctly ikiwa the
                # message ni serialized.
                payload = self._payload
                ikiwa payload:
                    jaribu:
                        payload = payload.encode('ascii', 'surrogateescape')
                    tatizo UnicodeError:
                        payload = payload.encode(charset.output_charset)
                self._payload = charset.body_encode(payload)
                self.add_header('Content-Transfer-Encoding', cte)

    eleza get_charset(self):
        """Return the Charset instance associated ukijumuisha the message's payload.
        """
        rudisha self._charset

    #
    # MAPPING INTERFACE (partial)
    #
    eleza __len__(self):
        """Return the total number of headers, including duplicates."""
        rudisha len(self._headers)

    eleza __getitem__(self, name):
        """Get a header value.

        Return Tupu ikiwa the header ni missing instead of raising an exception.

        Note that ikiwa the header appeared multiple times, exactly which
        occurrence gets returned ni undefined.  Use get_all() to get all
        the values matching a header field name.
        """
        rudisha self.get(name)

    eleza __setitem__(self, name, val):
        """Set the value of a header.

        Note: this does sio overwrite an existing header ukijumuisha the same field
        name.  Use __delitem__() first to delete any existing headers.
        """
        max_count = self.policy.header_max_count(name)
        ikiwa max_count:
            lname = name.lower()
            found = 0
            kila k, v kwenye self._headers:
                ikiwa k.lower() == lname:
                    found += 1
                    ikiwa found >= max_count:
                        ashiria ValueError("There may be at most {} {} headers "
                                         "in a message".format(max_count, name))
        self._headers.append(self.policy.header_store_parse(name, val))

    eleza __delitem__(self, name):
        """Delete all occurrences of a header, ikiwa present.

        Does sio ashiria an exception ikiwa the header ni missing.
        """
        name = name.lower()
        newheaders = []
        kila k, v kwenye self._headers:
            ikiwa k.lower() != name:
                newheaders.append((k, v))
        self._headers = newheaders

    eleza __contains__(self, name):
        rudisha name.lower() kwenye [k.lower() kila k, v kwenye self._headers]

    eleza __iter__(self):
        kila field, value kwenye self._headers:
            tuma field

    eleza keys(self):
        """Return a list of all the message's header field names.

        These will be sorted kwenye the order they appeared kwenye the original
        message, ama were added to the message, na may contain duplicates.
        Any fields deleted na re-inserted are always appended to the header
        list.
        """
        rudisha [k kila k, v kwenye self._headers]

    eleza values(self):
        """Return a list of all the message's header values.

        These will be sorted kwenye the order they appeared kwenye the original
        message, ama were added to the message, na may contain duplicates.
        Any fields deleted na re-inserted are always appended to the header
        list.
        """
        rudisha [self.policy.header_fetch_parse(k, v)
                kila k, v kwenye self._headers]

    eleza items(self):
        """Get all the message's header fields na values.

        These will be sorted kwenye the order they appeared kwenye the original
        message, ama were added to the message, na may contain duplicates.
        Any fields deleted na re-inserted are always appended to the header
        list.
        """
        rudisha [(k, self.policy.header_fetch_parse(k, v))
                kila k, v kwenye self._headers]

    eleza get(self, name, failobj=Tupu):
        """Get a header value.

        Like __getitem__() but rudisha failobj instead of Tupu when the field
        ni missing.
        """
        name = name.lower()
        kila k, v kwenye self._headers:
            ikiwa k.lower() == name:
                rudisha self.policy.header_fetch_parse(k, v)
        rudisha failobj

    #
    # "Internal" methods (public API, but only intended kila use by a parser
    # ama generator, sio normal application code.
    #

    eleza set_raw(self, name, value):
        """Store name na value kwenye the motoa without modification.

        This ni an "internal" API, intended only kila use by a parser.
        """
        self._headers.append((name, value))

    eleza raw_items(self):
        """Return the (name, value) header pairs without modification.

        This ni an "internal" API, intended only kila use by a generator.
        """
        rudisha iter(self._headers.copy())

    #
    # Additional useful stuff
    #

    eleza get_all(self, name, failobj=Tupu):
        """Return a list of all the values kila the named field.

        These will be sorted kwenye the order they appeared kwenye the original
        message, na may contain duplicates.  Any fields deleted na
        re-inserted are always appended to the header list.

        If no such fields exist, failobj ni returned (defaults to Tupu).
        """
        values = []
        name = name.lower()
        kila k, v kwenye self._headers:
            ikiwa k.lower() == name:
                values.append(self.policy.header_fetch_parse(k, v))
        ikiwa sio values:
            rudisha failobj
        rudisha values

    eleza add_header(self, _name, _value, **_params):
        """Extended header setting.

        name ni the header field to add.  keyword arguments can be used to set
        additional parameters kila the header field, ukijumuisha underscores converted
        to dashes.  Normally the parameter will be added kama key="value" unless
        value ni Tupu, kwenye which case only the key will be added.  If a
        parameter value contains non-ASCII characters it can be specified kama a
        three-tuple of (charset, language, value), kwenye which case it will be
        encoded according to RFC2231 rules.  Otherwise it will be encoded using
        the utf-8 charset na a language of ''.

        Examples:

        msg.add_header('content-disposition', 'attachment', filename='bud.gif')
        msg.add_header('content-disposition', 'attachment',
                       filename=('utf-8', '', Fußballer.ppt'))
        msg.add_header('content-disposition', 'attachment',
                       filename='Fußballer.ppt'))
        """
        parts = []
        kila k, v kwenye _params.items():
            ikiwa v ni Tupu:
                parts.append(k.replace('_', '-'))
            isipokua:
                parts.append(_formatparam(k.replace('_', '-'), v))
        ikiwa _value ni sio Tupu:
            parts.insert(0, _value)
        self[_name] = SEMISPACE.join(parts)

    eleza replace_header(self, _name, _value):
        """Replace a header.

        Replace the first matching header found kwenye the message, retaining
        header order na case.  If no matching header was found, a KeyError is
        raised.
        """
        _name = _name.lower()
        kila i, (k, v) kwenye zip(range(len(self._headers)), self._headers):
            ikiwa k.lower() == _name:
                self._headers[i] = self.policy.header_store_parse(k, _value)
                koma
        isipokua:
            ashiria KeyError(_name)

    #
    # Use these three methods instead of the three above.
    #

    eleza get_content_type(self):
        """Return the message's content type.

        The returned string ni coerced to lower case of the form
        `maintype/subtype'.  If there was no Content-Type header kwenye the
        message, the default type kama given by get_default_type() will be
        returned.  Since according to RFC 2045, messages always have a default
        type this will always rudisha a value.

        RFC 2045 defines a message's default type to be text/plain unless it
        appears inside a multipart/digest container, kwenye which case it would be
        message/rfc822.
        """
        missing = object()
        value = self.get('content-type', missing)
        ikiwa value ni missing:
            # This should have no parameters
            rudisha self.get_default_type()
        ctype = _splitparam(value)[0].lower()
        # RFC 2045, section 5.2 says ikiwa its invalid, use text/plain
        ikiwa ctype.count('/') != 1:
            rudisha 'text/plain'
        rudisha ctype

    eleza get_content_maintype(self):
        """Return the message's main content type.

        This ni the `maintype' part of the string returned by
        get_content_type().
        """
        ctype = self.get_content_type()
        rudisha ctype.split('/')[0]

    eleza get_content_subtype(self):
        """Returns the message's sub-content type.

        This ni the `subtype' part of the string returned by
        get_content_type().
        """
        ctype = self.get_content_type()
        rudisha ctype.split('/')[1]

    eleza get_default_type(self):
        """Return the `default' content type.

        Most messages have a default content type of text/plain, tatizo for
        messages that are subparts of multipart/digest containers.  Such
        subparts have a default content type of message/rfc822.
        """
        rudisha self._default_type

    eleza set_default_type(self, ctype):
        """Set the `default' content type.

        ctype should be either "text/plain" ama "message/rfc822", although this
        ni sio enforced.  The default content type ni sio stored kwenye the
        Content-Type header.
        """
        self._default_type = ctype

    eleza _get_params_preserve(self, failobj, header):
        # Like get_params() but preserves the quoting of values.  BAW:
        # should this be part of the public interface?
        missing = object()
        value = self.get(header, missing)
        ikiwa value ni missing:
            rudisha failobj
        params = []
        kila p kwenye _parseparam(value):
            jaribu:
                name, val = p.split('=', 1)
                name = name.strip()
                val = val.strip()
            tatizo ValueError:
                # Must have been a bare attribute
                name = p.strip()
                val = ''
            params.append((name, val))
        params = utils.decode_params(params)
        rudisha params

    eleza get_params(self, failobj=Tupu, header='content-type', unquote=Kweli):
        """Return the message's Content-Type parameters, kama a list.

        The elements of the returned list are 2-tuples of key/value pairs, as
        split on the `=' sign.  The left hand side of the `=' ni the key,
        wakati the right hand side ni the value.  If there ni no `=' sign in
        the parameter the value ni the empty string.  The value ni as
        described kwenye the get_param() method.

        Optional failobj ni the object to rudisha ikiwa there ni no Content-Type
        header.  Optional header ni the header to search instead of
        Content-Type.  If unquote ni Kweli, the value ni unquoted.
        """
        missing = object()
        params = self._get_params_preserve(missing, header)
        ikiwa params ni missing:
            rudisha failobj
        ikiwa unquote:
            rudisha [(k, _unquotevalue(v)) kila k, v kwenye params]
        isipokua:
            rudisha params

    eleza get_param(self, param, failobj=Tupu, header='content-type',
                  unquote=Kweli):
        """Return the parameter value ikiwa found kwenye the Content-Type header.

        Optional failobj ni the object to rudisha ikiwa there ni no Content-Type
        header, ama the Content-Type header has no such parameter.  Optional
        header ni the header to search instead of Content-Type.

        Parameter keys are always compared case insensitively.  The return
        value can either be a string, ama a 3-tuple ikiwa the parameter was RFC
        2231 encoded.  When it's a 3-tuple, the elements of the value are of
        the form (CHARSET, LANGUAGE, VALUE).  Note that both CHARSET na
        LANGUAGE can be Tupu, kwenye which case you should consider VALUE to be
        encoded kwenye the us-ascii charset.  You can usually ignore LANGUAGE.
        The parameter value (either the returned string, ama the VALUE item in
        the 3-tuple) ni always unquoted, unless unquote ni set to Uongo.

        If your application doesn't care whether the parameter was RFC 2231
        encoded, it can turn the rudisha value into a string kama follows:

            rawparam = msg.get_param('foo')
            param = email.utils.collapse_rfc2231_value(rawparam)

        """
        ikiwa header haiko kwenye self:
            rudisha failobj
        kila k, v kwenye self._get_params_preserve(failobj, header):
            ikiwa k.lower() == param.lower():
                ikiwa unquote:
                    rudisha _unquotevalue(v)
                isipokua:
                    rudisha v
        rudisha failobj

    eleza set_param(self, param, value, header='Content-Type', requote=Kweli,
                  charset=Tupu, language='', replace=Uongo):
        """Set a parameter kwenye the Content-Type header.

        If the parameter already exists kwenye the header, its value will be
        replaced ukijumuisha the new value.

        If header ni Content-Type na has sio yet been defined kila this
        message, it will be set to "text/plain" na the new parameter na
        value will be appended kama per RFC 2045.

        An alternate header can be specified kwenye the header argument, na all
        parameters will be quoted kama necessary unless requote ni Uongo.

        If charset ni specified, the parameter will be encoded according to RFC
        2231.  Optional language specifies the RFC 2231 language, defaulting
        to the empty string.  Both charset na language should be strings.
        """
        ikiwa sio isinstance(value, tuple) na charset:
            value = (charset, language, value)

        ikiwa header haiko kwenye self na header.lower() == 'content-type':
            ctype = 'text/plain'
        isipokua:
            ctype = self.get(header)
        ikiwa sio self.get_param(param, header=header):
            ikiwa sio ctype:
                ctype = _formatparam(param, value, requote)
            isipokua:
                ctype = SEMISPACE.join(
                    [ctype, _formatparam(param, value, requote)])
        isipokua:
            ctype = ''
            kila old_param, old_value kwenye self.get_params(header=header,
                                                        unquote=requote):
                append_param = ''
                ikiwa old_param.lower() == param.lower():
                    append_param = _formatparam(param, value, requote)
                isipokua:
                    append_param = _formatparam(old_param, old_value, requote)
                ikiwa sio ctype:
                    ctype = append_param
                isipokua:
                    ctype = SEMISPACE.join([ctype, append_param])
        ikiwa ctype != self.get(header):
            ikiwa replace:
                self.replace_header(header, ctype)
            isipokua:
                toa self[header]
                self[header] = ctype

    eleza del_param(self, param, header='content-type', requote=Kweli):
        """Remove the given parameter completely kutoka the Content-Type header.

        The header will be re-written kwenye place without the parameter ama its
        value. All values will be quoted kama necessary unless requote is
        Uongo.  Optional header specifies an alternative to the Content-Type
        header.
        """
        ikiwa header haiko kwenye self:
            return
        new_ctype = ''
        kila p, v kwenye self.get_params(header=header, unquote=requote):
            ikiwa p.lower() != param.lower():
                ikiwa sio new_ctype:
                    new_ctype = _formatparam(p, v, requote)
                isipokua:
                    new_ctype = SEMISPACE.join([new_ctype,
                                                _formatparam(p, v, requote)])
        ikiwa new_ctype != self.get(header):
            toa self[header]
            self[header] = new_ctype

    eleza set_type(self, type, header='Content-Type', requote=Kweli):
        """Set the main type na subtype kila the Content-Type header.

        type must be a string kwenye the form "maintype/subtype", otherwise a
        ValueError ni raised.

        This method replaces the Content-Type header, keeping all the
        parameters kwenye place.  If requote ni Uongo, this leaves the existing
        header's quoting kama is.  Otherwise, the parameters will be quoted (the
        default).

        An alternative header can be specified kwenye the header argument.  When
        the Content-Type header ni set, we'll always also add a MIME-Version
        header.
        """
        # BAW: should we be strict?
        ikiwa sio type.count('/') == 1:
            ashiria ValueError
        # Set the Content-Type, you get a MIME-Version
        ikiwa header.lower() == 'content-type':
            toa self['mime-version']
            self['MIME-Version'] = '1.0'
        ikiwa header haiko kwenye self:
            self[header] = type
            return
        params = self.get_params(header=header, unquote=requote)
        toa self[header]
        self[header] = type
        # Skip the first param; it's the old type.
        kila p, v kwenye params[1:]:
            self.set_param(p, v, header, requote)

    eleza get_filename(self, failobj=Tupu):
        """Return the filename associated ukijumuisha the payload ikiwa present.

        The filename ni extracted kutoka the Content-Disposition header's
        `filename' parameter, na it ni unquoted.  If that header ni missing
        the `filename' parameter, this method falls back to looking kila the
        `name' parameter.
        """
        missing = object()
        filename = self.get_param('filename', missing, 'content-disposition')
        ikiwa filename ni missing:
            filename = self.get_param('name', missing, 'content-type')
        ikiwa filename ni missing:
            rudisha failobj
        rudisha utils.collapse_rfc2231_value(filename).strip()

    eleza get_boundary(self, failobj=Tupu):
        """Return the boundary associated ukijumuisha the payload ikiwa present.

        The boundary ni extracted kutoka the Content-Type header's `boundary'
        parameter, na it ni unquoted.
        """
        missing = object()
        boundary = self.get_param('boundary', missing)
        ikiwa boundary ni missing:
            rudisha failobj
        # RFC 2046 says that boundaries may begin but sio end kwenye w/s
        rudisha utils.collapse_rfc2231_value(boundary).rstrip()

    eleza set_boundary(self, boundary):
        """Set the boundary parameter kwenye Content-Type to 'boundary'.

        This ni subtly different than deleting the Content-Type header na
        adding a new one ukijumuisha a new boundary parameter via add_header().  The
        main difference ni that using the set_boundary() method preserves the
        order of the Content-Type header kwenye the original message.

        HeaderParseError ni raised ikiwa the message has no Content-Type header.
        """
        missing = object()
        params = self._get_params_preserve(missing, 'content-type')
        ikiwa params ni missing:
            # There was no Content-Type header, na we don't know what type
            # to set it to, so ashiria an exception.
            ashiria errors.HeaderParseError('No Content-Type header found')
        newparams = []
        foundp = Uongo
        kila pk, pv kwenye params:
            ikiwa pk.lower() == 'boundary':
                newparams.append(('boundary', '"%s"' % boundary))
                foundp = Kweli
            isipokua:
                newparams.append((pk, pv))
        ikiwa sio foundp:
            # The original Content-Type header had no boundary attribute.
            # Tack one on the end.  BAW: should we ashiria an exception
            # instead???
            newparams.append(('boundary', '"%s"' % boundary))
        # Replace the existing Content-Type header ukijumuisha the new value
        newheaders = []
        kila h, v kwenye self._headers:
            ikiwa h.lower() == 'content-type':
                parts = []
                kila k, v kwenye newparams:
                    ikiwa v == '':
                        parts.append(k)
                    isipokua:
                        parts.append('%s=%s' % (k, v))
                val = SEMISPACE.join(parts)
                newheaders.append(self.policy.header_store_parse(h, val))

            isipokua:
                newheaders.append((h, v))
        self._headers = newheaders

    eleza get_content_charset(self, failobj=Tupu):
        """Return the charset parameter of the Content-Type header.

        The returned string ni always coerced to lower case.  If there ni no
        Content-Type header, ama ikiwa that header has no charset parameter,
        failobj ni returned.
        """
        missing = object()
        charset = self.get_param('charset', missing)
        ikiwa charset ni missing:
            rudisha failobj
        ikiwa isinstance(charset, tuple):
            # RFC 2231 encoded, so decode it, na it better end up kama ascii.
            pcharset = charset[0] ama 'us-ascii'
            jaribu:
                # LookupError will be raised ikiwa the charset isn't known to
                # Python.  UnicodeError will be raised ikiwa the encoded text
                # contains a character haiko kwenye the charset.
                as_bytes = charset[2].encode('raw-unicode-escape')
                charset = str(as_bytes, pcharset)
            tatizo (LookupError, UnicodeError):
                charset = charset[2]
        # charset characters must be kwenye us-ascii range
        jaribu:
            charset.encode('us-ascii')
        tatizo UnicodeError:
            rudisha failobj
        # RFC 2046, $4.1.2 says charsets are sio case sensitive
        rudisha charset.lower()

    eleza get_charsets(self, failobj=Tupu):
        """Return a list containing the charset(s) used kwenye this message.

        The returned list of items describes the Content-Type headers'
        charset parameter kila this message na all the subparts kwenye its
        payload.

        Each item will either be a string (the value of the charset parameter
        kwenye the Content-Type header of that part) ama the value of the
        'failobj' parameter (defaults to Tupu), ikiwa the part does sio have a
        main MIME type of "text", ama the charset ni sio defined.

        The list will contain one string kila each part of the message, plus
        one kila the container message (i.e. self), so that a non-multipart
        message will still rudisha a list of length 1.
        """
        rudisha [part.get_content_charset(failobj) kila part kwenye self.walk()]

    eleza get_content_disposition(self):
        """Return the message's content-disposition ikiwa it exists, ama Tupu.

        The rudisha values can be either 'inline', 'attachment' ama Tupu
        according to the rfc2183.
        """
        value = self.get('content-disposition')
        ikiwa value ni Tupu:
            rudisha Tupu
        c_d = _splitparam(value)[0].lower()
        rudisha c_d

    # I.e. eleza walk(self): ...
    kutoka email.iterators agiza walk


kundi MIMEPart(Message):

    eleza __init__(self, policy=Tupu):
        ikiwa policy ni Tupu:
            kutoka email.policy agiza default
            policy = default
        Message.__init__(self, policy)


    eleza as_string(self, unixfrom=Uongo, maxheaderlen=Tupu, policy=Tupu):
        """Return the entire formatted message kama a string.

        Optional 'unixfrom', when true, means include the Unix From_ envelope
        header.  maxheaderlen ni retained kila backward compatibility ukijumuisha the
        base Message class, but defaults to Tupu, meaning that the policy value
        kila max_line_length controls the header maximum length.  'policy' is
        pitaed to the Generator instance used to serialize the mesasge; ikiwa it
        ni sio specified the policy associated ukijumuisha the message instance is
        used.
        """
        policy = self.policy ikiwa policy ni Tupu isipokua policy
        ikiwa maxheaderlen ni Tupu:
            maxheaderlen = policy.max_line_length
        rudisha super().as_string(maxheaderlen=maxheaderlen, policy=policy)

    eleza __str__(self):
        rudisha self.as_string(policy=self.policy.clone(utf8=Kweli))

    eleza is_attachment(self):
        c_d = self.get('content-disposition')
        rudisha Uongo ikiwa c_d ni Tupu isipokua c_d.content_disposition == 'attachment'

    eleza _find_body(self, part, preferencelist):
        ikiwa part.is_attachment():
            return
        maintype, subtype = part.get_content_type().split('/')
        ikiwa maintype == 'text':
            ikiwa subtype kwenye preferencelist:
                tuma (preferencelist.index(subtype), part)
            return
        ikiwa maintype != 'multipart':
            return
        ikiwa subtype != 'related':
            kila subpart kwenye part.iter_parts():
                tuma kutoka self._find_body(subpart, preferencelist)
            return
        ikiwa 'related' kwenye preferencelist:
            tuma (preferencelist.index('related'), part)
        candidate = Tupu
        start = part.get_param('start')
        ikiwa start:
            kila subpart kwenye part.iter_parts():
                ikiwa subpart['content-id'] == start:
                    candidate = subpart
                    koma
        ikiwa candidate ni Tupu:
            subparts = part.get_payload()
            candidate = subparts[0] ikiwa subparts isipokua Tupu
        ikiwa candidate ni sio Tupu:
            tuma kutoka self._find_body(candidate, preferencelist)

    eleza get_body(self, preferencelist=('related', 'html', 'plain')):
        """Return best candidate mime part kila display kama 'body' of message.

        Do a depth first search, starting ukijumuisha self, looking kila the first part
        matching each of the items kwenye preferencelist, na rudisha the part
        corresponding to the first item that has a match, ama Tupu ikiwa no items
        have a match.  If 'related' ni sio included kwenye preferencelist, consider
        the root part of any multipart/related encountered kama a candidate
        match.  Ignore parts ukijumuisha 'Content-Disposition: attachment'.
        """
        best_prio = len(preferencelist)
        body = Tupu
        kila prio, part kwenye self._find_body(self, preferencelist):
            ikiwa prio < best_prio:
                best_prio = prio
                body = part
                ikiwa prio == 0:
                    koma
        rudisha body

    _body_types = {('text', 'plain'),
                   ('text', 'html'),
                   ('multipart', 'related'),
                   ('multipart', 'alternative')}
    eleza iter_attachments(self):
        """Return an iterator over the non-main parts of a multipart.

        Skip the first of each occurrence of text/plain, text/html,
        multipart/related, ama multipart/alternative kwenye the multipart (unless
        they have a 'Content-Disposition: attachment' header) na include all
        remaining subparts kwenye the returned iterator.  When applied to a
        multipart/related, rudisha all parts tatizo the root part.  Return an
        empty iterator when applied to a multipart/alternative ama a
        non-multipart.
        """
        maintype, subtype = self.get_content_type().split('/')
        ikiwa maintype != 'multipart' ama subtype == 'alternative':
            return
        payload = self.get_payload()
        # Certain malformed messages can have content type set to `multipart/*`
        # but still have single part body, kwenye which case payload.copy() can
        # fail ukijumuisha AttributeError.
        jaribu:
            parts = payload.copy()
        tatizo AttributeError:
            # payload ni sio a list, it ni most probably a string.
            return

        ikiwa maintype == 'multipart' na subtype == 'related':
            # For related, we treat everything but the root kama an attachment.
            # The root may be indicated by 'start'; ikiwa there's no start ama we
            # can't find the named start, treat the first subpart kama the root.
            start = self.get_param('start')
            ikiwa start:
                found = Uongo
                attachments = []
                kila part kwenye parts:
                    ikiwa part.get('content-id') == start:
                        found = Kweli
                    isipokua:
                        attachments.append(part)
                ikiwa found:
                    tuma kutoka attachments
                    return
            parts.pop(0)
            tuma kutoka parts
            return
        # Otherwise we more ama less invert the remaining logic kwenye get_body.
        # This only really works kwenye edge cases (ex: non-text related ama
        # alternatives) ikiwa the sending agent sets content-disposition.
        seen = []   # Only skip the first example of each candidate type.
        kila part kwenye parts:
            maintype, subtype = part.get_content_type().split('/')
            ikiwa ((maintype, subtype) kwenye self._body_types na
                    sio part.is_attachment() na subtype haiko kwenye seen):
                seen.append(subtype)
                endelea
            tuma part

    eleza iter_parts(self):
        """Return an iterator over all immediate subparts of a multipart.

        Return an empty iterator kila a non-multipart.
        """
        ikiwa self.get_content_maintype() == 'multipart':
            tuma kutoka self.get_payload()

    eleza get_content(self, *args, content_manager=Tupu, **kw):
        ikiwa content_manager ni Tupu:
            content_manager = self.policy.content_manager
        rudisha content_manager.get_content(self, *args, **kw)

    eleza set_content(self, *args, content_manager=Tupu, **kw):
        ikiwa content_manager ni Tupu:
            content_manager = self.policy.content_manager
        content_manager.set_content(self, *args, **kw)

    eleza _make_multipart(self, subtype, disallowed_subtypes, boundary):
        ikiwa self.get_content_maintype() == 'multipart':
            existing_subtype = self.get_content_subtype()
            disallowed_subtypes = disallowed_subtypes + (subtype,)
            ikiwa existing_subtype kwenye disallowed_subtypes:
                ashiria ValueError("Cannot convert {} to {}".format(
                    existing_subtype, subtype))
        keep_headers = []
        part_headers = []
        kila name, value kwenye self._headers:
            ikiwa name.lower().startswith('content-'):
                part_headers.append((name, value))
            isipokua:
                keep_headers.append((name, value))
        ikiwa part_headers:
            # There ni existing content, move it to the first subpart.
            part = type(self)(policy=self.policy)
            part._headers = part_headers
            part._payload = self._payload
            self._payload = [part]
        isipokua:
            self._payload = []
        self._headers = keep_headers
        self['Content-Type'] = 'multipart/' + subtype
        ikiwa boundary ni sio Tupu:
            self.set_param('boundary', boundary)

    eleza make_related(self, boundary=Tupu):
        self._make_multipart('related', ('alternative', 'mixed'), boundary)

    eleza make_alternative(self, boundary=Tupu):
        self._make_multipart('alternative', ('mixed',), boundary)

    eleza make_mixed(self, boundary=Tupu):
        self._make_multipart('mixed', (), boundary)

    eleza _add_multipart(self, _subtype, *args, _disp=Tupu, **kw):
        ikiwa (self.get_content_maintype() != 'multipart' ama
                self.get_content_subtype() != _subtype):
            getattr(self, 'make_' + _subtype)()
        part = type(self)(policy=self.policy)
        part.set_content(*args, **kw)
        ikiwa _disp na 'content-disposition' haiko kwenye part:
            part['Content-Disposition'] = _disp
        self.attach(part)

    eleza add_related(self, *args, **kw):
        self._add_multipart('related', *args, _disp='inline', **kw)

    eleza add_alternative(self, *args, **kw):
        self._add_multipart('alternative', *args, **kw)

    eleza add_attachment(self, *args, **kw):
        self._add_multipart('mixed', *args, _disp='attachment', **kw)

    eleza clear(self):
        self._headers = []
        self._payload = Tupu

    eleza clear_content(self):
        self._headers = [(n, v) kila n, v kwenye self._headers
                         ikiwa sio n.lower().startswith('content-')]
        self._payload = Tupu


kundi EmailMessage(MIMEPart):

    eleza set_content(self, *args, **kw):
        super().set_content(*args, **kw)
        ikiwa 'MIME-Version' haiko kwenye self:
            self['MIME-Version'] = '1.0'
