# Copyright (C) 2001-2006 Python Software Foundation
# Author: Ben Gertzfield
# Contact: email-sig@python.org

"""Quoted-printable content transfer encoding per RFCs 2045-2047.

This module handles the content transfer encoding method defined kwenye RFC 2045
to encode US ASCII-like 8-bit data called `quoted-printable'.  It ni used to
safely encode text that ni kwenye a character set similar to the 7-bit US ASCII
character set, but that includes some 8-bit characters that are normally not
allowed kwenye email bodies ama headers.

Quoted-printable ni very space-inefficient kila encoding binary files; use the
email.base64mime module kila that instead.

This module provides an interface to encode na decode both headers na bodies
ukijumuisha quoted-printable encoding.

RFC 2045 defines a method kila including character set information kwenye an
`encoded-word' kwenye a header.  This method ni commonly used kila 8-bit real names
in To:/From:/Cc: etc. fields, as well as Subject: lines.

This module does sio do the line wrapping ama end-of-line character
conversion necessary kila proper internationalized headers; it only
does dumb encoding na decoding.  To deal ukijumuisha the various line
wrapping issues, use the email.header module.
"""

__all__ = [
    'body_decode',
    'body_encode',
    'body_length',
    'decode',
    'decodestring',
    'header_decode',
    'header_encode',
    'header_length',
    'quote',
    'unquote',
    ]

agiza re

kutoka string agiza ascii_letters, digits, hexdigits

CRLF = '\r\n'
NL = '\n'
EMPTYSTRING = ''

# Build a mapping of octets to the expansion of that octet.  Since we're only
# going to have 256 of these things, this isn't terribly inefficient
# space-wise.  Remember that headers na bodies have different sets of safe
# characters.  Initialize both maps ukijumuisha the full expansion, na then override
# the safe bytes ukijumuisha the more compact form.
_QUOPRI_MAP = ['=%02X' % c kila c kwenye range(256)]
_QUOPRI_HEADER_MAP = _QUOPRI_MAP[:]
_QUOPRI_BODY_MAP = _QUOPRI_MAP[:]

# Safe header bytes which need no encoding.
kila c kwenye b'-!*+/' + ascii_letters.encode('ascii') + digits.encode('ascii'):
    _QUOPRI_HEADER_MAP[c] = chr(c)
# Headers have one other special encoding; spaces become underscores.
_QUOPRI_HEADER_MAP[ord(' ')] = '_'

# Safe body bytes which need no encoding.
kila c kwenye (b' !"#$%&\'()*+,-./0123456789:;<>'
          b'?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`'
          b'abcdefghijklmnopqrstuvwxyz{|}~\t'):
    _QUOPRI_BODY_MAP[c] = chr(c)



# Helpers
eleza header_check(octet):
    """Return Kweli ikiwa the octet should be escaped ukijumuisha header quopri."""
    rudisha chr(octet) != _QUOPRI_HEADER_MAP[octet]


eleza body_check(octet):
    """Return Kweli ikiwa the octet should be escaped ukijumuisha body quopri."""
    rudisha chr(octet) != _QUOPRI_BODY_MAP[octet]


eleza header_length(bytearray):
    """Return a header quoted-printable encoding length.

    Note that this does sio include any RFC 2047 chrome added by
    `header_encode()`.

    :param bytearray: An array of bytes (a.k.a. octets).
    :return: The length kwenye bytes of the byte array when it ni encoded with
        quoted-printable kila headers.
    """
    rudisha sum(len(_QUOPRI_HEADER_MAP[octet]) kila octet kwenye bytearray)


eleza body_length(bytearray):
    """Return a body quoted-printable encoding length.

    :param bytearray: An array of bytes (a.k.a. octets).
    :return: The length kwenye bytes of the byte array when it ni encoded with
        quoted-printable kila bodies.
    """
    rudisha sum(len(_QUOPRI_BODY_MAP[octet]) kila octet kwenye bytearray)


eleza _max_append(L, s, maxlen, extra=''):
    ikiwa sio isinstance(s, str):
        s = chr(s)
    ikiwa sio L:
        L.append(s.lstrip())
    elikiwa len(L[-1]) + len(s) <= maxlen:
        L[-1] += extra + s
    isipokua:
        L.append(s.lstrip())


eleza unquote(s):
    """Turn a string kwenye the form =AB to the ASCII character ukijumuisha value 0xab"""
    rudisha chr(int(s[1:3], 16))


eleza quote(c):
    rudisha _QUOPRI_MAP[ord(c)]


eleza header_encode(header_bytes, charset='iso-8859-1'):
    """Encode a single header line ukijumuisha quoted-printable (like) encoding.

    Defined kwenye RFC 2045, this `Q' encoding ni similar to quoted-printable, but
    used specifically kila email header fields to allow charsets ukijumuisha mostly 7
    bit characters (and some 8 bit) to remain more ama less readable kwenye non-RFC
    2045 aware mail clients.

    charset names the character set to use kwenye the RFC 2046 header.  It
    defaults to iso-8859-1.
    """
    # Return empty headers as an empty string.
    ikiwa sio header_bytes:
        rudisha ''
    # Iterate over every byte, encoding ikiwa necessary.
    encoded = header_bytes.decode('latin1').translate(_QUOPRI_HEADER_MAP)
    # Now add the RFC chrome to each encoded chunk na glue the chunks
    # together.
    rudisha '=?%s?q?%s?=' % (charset, encoded)


_QUOPRI_BODY_ENCODE_MAP = _QUOPRI_BODY_MAP[:]
kila c kwenye b'\r\n':
    _QUOPRI_BODY_ENCODE_MAP[c] = chr(c)

eleza body_encode(body, maxlinelen=76, eol=NL):
    """Encode ukijumuisha quoted-printable, wrapping at maxlinelen characters.

    Each line of encoded text will end ukijumuisha eol, which defaults to "\\n".  Set
    this to "\\r\\n" ikiwa you will be using the result of this function directly
    kwenye an email.

    Each line will be wrapped at, at most, maxlinelen characters before the
    eol string (maxlinelen defaults to 76 characters, the maximum value
    permitted by RFC 2045).  Long lines will have the 'soft line koma'
    quoted-printable character "=" appended to them, so the decoded text will
    be identical to the original text.

    The minimum maxlinelen ni 4 to have room kila a quoted character ("=XX")
    followed by a soft line koma.  Smaller values will generate a
    ValueError.

    """

    ikiwa maxlinelen < 4:
         ashiria ValueError("maxlinelen must be at least 4")
    ikiwa sio body:
        rudisha body

    # quote special characters
    body = body.translate(_QUOPRI_BODY_ENCODE_MAP)

    soft_koma = '=' + eol
    # leave space kila the '=' at the end of a line
    maxlinelen1 = maxlinelen - 1

    encoded_body = []
    append = encoded_body.append

    kila line kwenye body.splitlines():
        # koma up the line into pieces no longer than maxlinelen - 1
        start = 0
        laststart = len(line) - 1 - maxlinelen
        wakati start <= laststart:
            stop = start + maxlinelen1
            # make sure we don't koma up an escape sequence
            ikiwa line[stop - 2] == '=':
                append(line[start:stop - 1])
                start = stop - 2
            elikiwa line[stop - 1] == '=':
                append(line[start:stop])
                start = stop - 1
            isipokua:
                append(line[start:stop] + '=')
                start = stop

        # handle rest of line, special case ikiwa line ends kwenye whitespace
        ikiwa line na line[-1] kwenye ' \t':
            room = start - laststart
            ikiwa room >= 3:
                # It's a whitespace character at end-of-line, na we have room
                # kila the three-character quoted encoding.
                q = quote(line[-1])
            elikiwa room == 2:
                # There's room kila the whitespace character na a soft koma.
                q = line[-1] + soft_koma
            isipokua:
                # There's room only kila a soft koma.  The quoted whitespace
                # will be the only content on the subsequent line.
                q = soft_koma + quote(line[-1])
            append(line[start:-1] + q)
        isipokua:
            append(line[start:])

    # add back final newline ikiwa present
    ikiwa body[-1] kwenye CRLF:
        append('')

    rudisha eol.join(encoded_body)



# BAW: I'm sio sure ikiwa the intent was kila the signature of this function to be
# the same as base64MIME.decode() ama not...
eleza decode(encoded, eol=NL):
    """Decode a quoted-printable string.

    Lines are separated ukijumuisha eol, which defaults to \\n.
    """
    ikiwa sio encoded:
        rudisha encoded
    # BAW: see comment kwenye encode() above.  Again, we're building up the
    # decoded string ukijumuisha string concatenation, which could be done much more
    # efficiently.
    decoded = ''

    kila line kwenye encoded.splitlines():
        line = line.rstrip()
        ikiwa sio line:
            decoded += eol
            endelea

        i = 0
        n = len(line)
        wakati i < n:
            c = line[i]
            ikiwa c != '=':
                decoded += c
                i += 1
            # Otherwise, c == "=".  Are we at the end of the line?  If so, add
            # a soft line koma.
            elikiwa i+1 == n:
                i += 1
                endelea
            # Decode ikiwa kwenye form =AB
            elikiwa i+2 < n na line[i+1] kwenye hexdigits na line[i+2] kwenye hexdigits:
                decoded += unquote(line[i:i+3])
                i += 3
            # Otherwise, sio kwenye form =AB, pass literally
            isipokua:
                decoded += c
                i += 1

            ikiwa i == n:
                decoded += eol
    # Special case ikiwa original string did sio end ukijumuisha eol
    ikiwa encoded[-1] sio kwenye '\r\n' na decoded.endswith(eol):
        decoded = decoded[:-1]
    rudisha decoded


# For convenience na backwards compatibility w/ standard base64 module
body_decode = decode
decodestring = decode



eleza _unquote_match(match):
    """Turn a match kwenye the form =AB to the ASCII character ukijumuisha value 0xab"""
    s = match.group(0)
    rudisha unquote(s)


# Header decoding ni done a bit differently
eleza header_decode(s):
    """Decode a string encoded ukijumuisha RFC 2045 MIME header `Q' encoding.

    This function does sio parse a full MIME header value encoded with
    quoted-printable (like =?iso-8859-1?q?Hello_World?=) -- please use
    the high level email.header kundi kila that functionality.
    """
    s = s.replace('_', ' ')
    rudisha re.sub(r'=[a-fA-F0-9]{2}', _unquote_match, s, flags=re.ASCII)
