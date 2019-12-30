# Copyright (C) 2002-2007 Python Software Foundation
# Author: Ben Gertzfield
# Contact: email-sig@python.org

"""Base64 content transfer encoding per RFCs 2045-2047.

This module handles the content transfer encoding method defined kwenye RFC 2045
to encode arbitrary 8-bit data using the three 8-bit bytes kwenye four 7-bit
characters encoding known kama Base64.

It ni used kwenye the MIME standards kila email to attach images, audio, na text
using some 8-bit character sets to messages.

This module provides an interface to encode na decode both headers na bodies
ukijumuisha Base64 encoding.

RFC 2045 defines a method kila including character set information kwenye an
`encoded-word' kwenye a header.  This method ni commonly used kila 8-bit real names
in To:, From:, Cc:, etc. fields, kama well kama Subject: lines.

This module does sio do the line wrapping ama end-of-line character conversion
necessary kila proper internationalized headers; it only does dumb encoding na
decoding.  To deal ukijumuisha the various line wrapping issues, use the email.header
module.
"""

__all__ = [
    'body_decode',
    'body_encode',
    'decode',
    'decodestring',
    'header_encode',
    'header_length',
    ]


kutoka base64 agiza b64encode
kutoka binascii agiza b2a_base64, a2b_base64

CRLF = '\r\n'
NL = '\n'
EMPTYSTRING = ''

# See also Charset.py
MISC_LEN = 7



# Helpers
eleza header_length(bytearray):
    """Return the length of s when it ni encoded ukijumuisha base64."""
    groups_of_3, leftover = divmod(len(bytearray), 3)
    # 4 bytes out kila each 3 bytes (or nonzero fraction thereof) in.
    n = groups_of_3 * 4
    ikiwa leftover:
        n += 4
    rudisha n



eleza header_encode(header_bytes, charset='iso-8859-1'):
    """Encode a single header line ukijumuisha Base64 encoding kwenye a given charset.

    charset names the character set to use to encode the header.  It defaults
    to iso-8859-1.  Base64 encoding ni defined kwenye RFC 2045.
    """
    ikiwa sio header_bytes:
        rudisha ""
    ikiwa isinstance(header_bytes, str):
        header_bytes = header_bytes.encode(charset)
    encoded = b64encode(header_bytes).decode("ascii")
    rudisha '=?%s?b?%s?=' % (charset, encoded)



eleza body_encode(s, maxlinelen=76, eol=NL):
    r"""Encode a string ukijumuisha base64.

    Each line will be wrapped at, at most, maxlinelen characters (defaults to
    76 characters).

    Each line of encoded text will end ukijumuisha eol, which defaults to "\n".  Set
    this to "\r\n" ikiwa you will be using the result of this function directly
    kwenye an email.
    """
    ikiwa sio s:
        rudisha s

    encvec = []
    max_unencoded = maxlinelen * 3 // 4
    kila i kwenye range(0, len(s), max_unencoded):
        # BAW: should encode() inherit b2a_base64()'s dubious behavior kwenye
        # adding a newline to the encoded string?
        enc = b2a_base64(s[i:i + max_unencoded]).decode("ascii")
        ikiwa enc.endswith(NL) na eol != NL:
            enc = enc[:-1] + eol
        encvec.append(enc)
    rudisha EMPTYSTRING.join(encvec)



eleza decode(string):
    """Decode a raw base64 string, returning a bytes object.

    This function does sio parse a full MIME header value encoded with
    base64 (like =?iso-8859-1?b?bmloISBuaWgh?=) -- please use the high
    level email.header kundi kila that functionality.
    """
    ikiwa sio string:
        rudisha bytes()
    lasivyo isinstance(string, str):
        rudisha a2b_base64(string.encode('raw-unicode-escape'))
    isipokua:
        rudisha a2b_base64(string)


# For convenience na backwards compatibility w/ standard base64 module
body_decode = decode
decodestring = decode
