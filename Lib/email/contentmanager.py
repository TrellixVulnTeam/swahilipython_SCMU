agiza binascii
agiza email.charset
agiza email.message
agiza email.errors
kutoka email agiza quoprimime

kundi ContentManager:

    eleza __init__(self):
        self.get_handlers = {}
        self.set_handlers = {}

    eleza add_get_handler(self, key, handler):
        self.get_handlers[key] = handler

    eleza get_content(self, msg, *args, **kw):
        content_type = msg.get_content_type()
        ikiwa content_type kwenye self.get_handlers:
            rudisha self.get_handlers[content_type](msg, *args, **kw)
        maintype = msg.get_content_maintype()
        ikiwa maintype kwenye self.get_handlers:
            rudisha self.get_handlers[maintype](msg, *args, **kw)
        ikiwa '' kwenye self.get_handlers:
            rudisha self.get_handlers[''](msg, *args, **kw)
        ashiria KeyError(content_type)

    eleza add_set_handler(self, typekey, handler):
        self.set_handlers[typekey] = handler

    eleza set_content(self, msg, obj, *args, **kw):
        ikiwa msg.get_content_maintype() == 'multipart':
            # XXX: ni this error a good idea ama not?  We can remove it later,
            # but we can't add it later, so do it kila now.
            ashiria TypeError("set_content sio valid on multipart")
        handler = self._find_set_handler(msg, obj)
        msg.clear_content()
        handler(msg, obj, *args, **kw)

    eleza _find_set_handler(self, msg, obj):
        full_path_for_error = Tupu
        kila typ kwenye type(obj).__mro__:
            ikiwa typ kwenye self.set_handlers:
                rudisha self.set_handlers[typ]
            qname = typ.__qualname__
            modname = getattr(typ, '__module__', '')
            full_path = '.'.join((modname, qname)) ikiwa modname isipokua qname
            ikiwa full_path_for_error ni Tupu:
                full_path_for_error = full_path
            ikiwa full_path kwenye self.set_handlers:
                rudisha self.set_handlers[full_path]
            ikiwa qname kwenye self.set_handlers:
                rudisha self.set_handlers[qname]
            name = typ.__name__
            ikiwa name kwenye self.set_handlers:
                rudisha self.set_handlers[name]
        ikiwa Tupu kwenye self.set_handlers:
            rudisha self.set_handlers[Tupu]
        ashiria KeyError(full_path_for_error)


raw_data_manager = ContentManager()


eleza get_text_content(msg, errors='replace'):
    content = msg.get_payload(decode=Kweli)
    charset = msg.get_param('charset', 'ASCII')
    rudisha content.decode(charset, errors=errors)
raw_data_manager.add_get_handler('text', get_text_content)


eleza get_non_text_content(msg):
    rudisha msg.get_payload(decode=Kweli)
kila maintype kwenye 'audio image video application'.split():
    raw_data_manager.add_get_handler(maintype, get_non_text_content)


eleza get_message_content(msg):
    rudisha msg.get_payload(0)
kila subtype kwenye 'rfc822 external-body'.split():
    raw_data_manager.add_get_handler('message/'+subtype, get_message_content)


eleza get_and_fixup_unknown_message_content(msg):
    # If we don't understand a message subtype, we are supposed to treat it as
    # ikiwa it were application/octet-stream, per
    # tools.ietf.org/html/rfc2046#section-5.2.4.  Feedparser doesn't do that,
    # so do our best to fix things up.  Note that it ni *not* appropriate to
    # motoa message/partial content kama Message objects, so they are handled
    # here kama well.  (How to reassemble them ni out of scope kila this comment :)
    rudisha bytes(msg.get_payload(0))
raw_data_manager.add_get_handler('message',
                                 get_and_fixup_unknown_message_content)


eleza _prepare_set(msg, maintype, subtype, headers):
    msg['Content-Type'] = '/'.join((maintype, subtype))
    ikiwa headers:
        ikiwa sio hasattr(headers[0], 'name'):
            mp = msg.policy
            headers = [mp.header_factory(*mp.header_source_parse([header]))
                       kila header kwenye headers]
        jaribu:
            kila header kwenye headers:
                ikiwa header.defects:
                    ashiria header.defects[0]
                msg[header.name] = header
        tatizo email.errors.HeaderDefect kama exc:
            ashiria ValueError("Invalid header: {}".format(
                                header.fold(policy=msg.policy))) kutoka exc


eleza _finalize_set(msg, disposition, filename, cid, params):
    ikiwa disposition ni Tupu na filename ni sio Tupu:
        disposition = 'attachment'
    ikiwa disposition ni sio Tupu:
        msg['Content-Disposition'] = disposition
    ikiwa filename ni sio Tupu:
        msg.set_param('filename',
                      filename,
                      header='Content-Disposition',
                      replace=Kweli)
    ikiwa cid ni sio Tupu:
        msg['Content-ID'] = cid
    ikiwa params ni sio Tupu:
        kila key, value kwenye params.items():
            msg.set_param(key, value)


# XXX: This ni a cleaned-up version of base64mime.body_encode (including a bug
# fix kwenye the calculation of unencoded_bytes_per_line).  It would be nice to
# drop both this na quoprimime.body_encode kwenye favor of enhanced binascii
# routines that accepted a max_line_length parameter.
eleza _encode_base64(data, max_line_length):
    encoded_lines = []
    unencoded_bytes_per_line = max_line_length // 4 * 3
    kila i kwenye range(0, len(data), unencoded_bytes_per_line):
        thisline = data[i:i+unencoded_bytes_per_line]
        encoded_lines.append(binascii.b2a_base64(thisline).decode('ascii'))
    rudisha ''.join(encoded_lines)


eleza _encode_text(string, charset, cte, policy):
    lines = string.encode(charset).splitlines()
    linesep = policy.linesep.encode('ascii')
    eleza embedded_body(lines): rudisha linesep.join(lines) + linesep
    eleza normal_body(lines): rudisha b'\n'.join(lines) + b'\n'
    ikiwa cte==Tupu:
        # Use heuristics to decide on the "best" encoding.
        jaribu:
            rudisha '7bit', normal_body(lines).decode('ascii')
        tatizo UnicodeDecodeError:
            pita
        ikiwa (policy.cte_type == '8bit' na
                max(len(x) kila x kwenye lines) <= policy.max_line_length):
            rudisha '8bit', normal_body(lines).decode('ascii', 'surrogateescape')
        sniff = embedded_body(lines[:10])
        sniff_qp = quoprimime.body_encode(sniff.decode('latin-1'),
                                          policy.max_line_length)
        sniff_base64 = binascii.b2a_base64(sniff)
        # This ni a little unfair to qp; it includes lineseps, base64 doesn't.
        ikiwa len(sniff_qp) > len(sniff_base64):
            cte = 'base64'
        isipokua:
            cte = 'quoted-printable'
            ikiwa len(lines) <= 10:
                rudisha cte, sniff_qp
    ikiwa cte == '7bit':
        data = normal_body(lines).decode('ascii')
    lasivyo cte == '8bit':
        data = normal_body(lines).decode('ascii', 'surrogateescape')
    lasivyo cte == 'quoted-printable':
        data = quoprimime.body_encode(normal_body(lines).decode('latin-1'),
                                      policy.max_line_length)
    lasivyo cte == 'base64':
        data = _encode_base64(embedded_body(lines), policy.max_line_length)
    isipokua:
        ashiria ValueError("Unknown content transfer encoding {}".format(cte))
    rudisha cte, data


eleza set_text_content(msg, string, subtype="plain", charset='utf-8', cte=Tupu,
                     disposition=Tupu, filename=Tupu, cid=Tupu,
                     params=Tupu, headers=Tupu):
    _prepare_set(msg, 'text', subtype, headers)
    cte, payload = _encode_text(string, charset, cte, msg.policy)
    msg.set_payload(payload)
    msg.set_param('charset',
                  email.charset.ALIASES.get(charset, charset),
                  replace=Kweli)
    msg['Content-Transfer-Encoding'] = cte
    _finalize_set(msg, disposition, filename, cid, params)
raw_data_manager.add_set_handler(str, set_text_content)


eleza set_message_content(msg, message, subtype="rfc822", cte=Tupu,
                       disposition=Tupu, filename=Tupu, cid=Tupu,
                       params=Tupu, headers=Tupu):
    ikiwa subtype == 'partial':
        ashiria ValueError("message/partial ni sio supported kila Message objects")
    ikiwa subtype == 'rfc822':
        ikiwa cte haiko kwenye (Tupu, '7bit', '8bit', 'binary'):
            # http://tools.ietf.org/html/rfc2046#section-5.2.1 mandate.
            ashiria ValueError(
                "message/rfc822 parts do sio support cte={}".format(cte))
        # 8bit will get coerced on serialization ikiwa policy.cte_type='7bit'.  We
        # may end up claiming 8bit when it isn't needed, but the only negative
        # result of that should be a gateway that needs to coerce to 7bit
        # having to look through the whole embedded message to discover whether
        # ama sio it actually has to do anything.
        cte = '8bit' ikiwa cte ni Tupu isipokua cte
    lasivyo subtype == 'external-body':
        ikiwa cte haiko kwenye (Tupu, '7bit'):
            # http://tools.ietf.org/html/rfc2046#section-5.2.3 mandate.
            ashiria ValueError(
                "message/external-body parts do sio support cte={}".format(cte))
        cte = '7bit'
    lasivyo cte ni Tupu:
        # http://tools.ietf.org/html/rfc2046#section-5.2.4 says all future
        # subtypes should be restricted to 7bit, so assume that.
        cte = '7bit'
    _prepare_set(msg, 'message', subtype, headers)
    msg.set_payload([message])
    msg['Content-Transfer-Encoding'] = cte
    _finalize_set(msg, disposition, filename, cid, params)
raw_data_manager.add_set_handler(email.message.Message, set_message_content)


eleza set_bytes_content(msg, data, maintype, subtype, cte='base64',
                     disposition=Tupu, filename=Tupu, cid=Tupu,
                     params=Tupu, headers=Tupu):
    _prepare_set(msg, maintype, subtype, headers)
    ikiwa cte == 'base64':
        data = _encode_base64(data, max_line_length=msg.policy.max_line_length)
    lasivyo cte == 'quoted-printable':
        # XXX: quoprimime.body_encode won't encode newline characters kwenye data,
        # so we can't use it.  This means max_line_length ni ignored.  Another
        # bug to fix later.  (Note: encoders.quopri ni broken on line ends.)
        data = binascii.b2a_qp(data, istext=Uongo, header=Uongo, quotetabs=Kweli)
        data = data.decode('ascii')
    lasivyo cte == '7bit':
        # Make sure it really ni only ASCII.  The early warning here seems
        # worth the overhead...ikiwa you care write your own content manager :).
        data.encode('ascii')
    lasivyo cte kwenye ('8bit', 'binary'):
        data = data.decode('ascii', 'surrogateescape')
    msg.set_payload(data)
    msg['Content-Transfer-Encoding'] = cte
    _finalize_set(msg, disposition, filename, cid, params)
kila typ kwenye (bytes, bytearray, memoryview):
    raw_data_manager.add_set_handler(typ, set_bytes_content)
