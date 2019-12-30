# Copyright (C) 2001-2007 Python Software Foundation
# Author: Ben Gertzfield, Barry Warsaw
# Contact: email-sig@python.org

__all__ = [
    'Charset',
    'add_alias',
    'add_charset',
    'add_codec',
    ]

kutoka functools agiza partial

agiza email.base64mime
agiza email.quoprimime

kutoka email agiza errors
kutoka email.encoders agiza encode_7or8bit



# Flags kila types of header encodings
QP          = 1 # Quoted-Printable
BASE64      = 2 # Base64
SHORTEST    = 3 # the shorter of QP na base64, but only kila headers

# In "=?charset?q?hello_world?=", the =?, ?q?, na ?= add up to 7
RFC2047_CHROME_LEN = 7

DEFAULT_CHARSET = 'us-ascii'
UNKNOWN8BIT = 'unknown-8bit'
EMPTYSTRING = ''



# Defaults
CHARSETS = {
    # input        header enc  body enc output conv
    'iso-8859-1':  (QP,        QP,      Tupu),
    'iso-8859-2':  (QP,        QP,      Tupu),
    'iso-8859-3':  (QP,        QP,      Tupu),
    'iso-8859-4':  (QP,        QP,      Tupu),
    # iso-8859-5 ni Cyrillic, na sio especially used
    # iso-8859-6 ni Arabic, also sio particularly used
    # iso-8859-7 ni Greek, QP will sio make it readable
    # iso-8859-8 ni Hebrew, QP will sio make it readable
    'iso-8859-9':  (QP,        QP,      Tupu),
    'iso-8859-10': (QP,        QP,      Tupu),
    # iso-8859-11 ni Thai, QP will sio make it readable
    'iso-8859-13': (QP,        QP,      Tupu),
    'iso-8859-14': (QP,        QP,      Tupu),
    'iso-8859-15': (QP,        QP,      Tupu),
    'iso-8859-16': (QP,        QP,      Tupu),
    'windows-1252':(QP,        QP,      Tupu),
    'viscii':      (QP,        QP,      Tupu),
    'us-ascii':    (Tupu,      Tupu,    Tupu),
    'big5':        (BASE64,    BASE64,  Tupu),
    'gb2312':      (BASE64,    BASE64,  Tupu),
    'euc-jp':      (BASE64,    Tupu,    'iso-2022-jp'),
    'shift_jis':   (BASE64,    Tupu,    'iso-2022-jp'),
    'iso-2022-jp': (BASE64,    Tupu,    Tupu),
    'koi8-r':      (BASE64,    BASE64,  Tupu),
    'utf-8':       (SHORTEST,  BASE64, 'utf-8'),
    }

# Aliases kila other commonly-used names kila character sets.  Map
# them to the real ones used kwenye email.
ALIASES = {
    'latin_1': 'iso-8859-1',
    'latin-1': 'iso-8859-1',
    'latin_2': 'iso-8859-2',
    'latin-2': 'iso-8859-2',
    'latin_3': 'iso-8859-3',
    'latin-3': 'iso-8859-3',
    'latin_4': 'iso-8859-4',
    'latin-4': 'iso-8859-4',
    'latin_5': 'iso-8859-9',
    'latin-5': 'iso-8859-9',
    'latin_6': 'iso-8859-10',
    'latin-6': 'iso-8859-10',
    'latin_7': 'iso-8859-13',
    'latin-7': 'iso-8859-13',
    'latin_8': 'iso-8859-14',
    'latin-8': 'iso-8859-14',
    'latin_9': 'iso-8859-15',
    'latin-9': 'iso-8859-15',
    'latin_10':'iso-8859-16',
    'latin-10':'iso-8859-16',
    'cp949':   'ks_c_5601-1987',
    'euc_jp':  'euc-jp',
    'euc_kr':  'euc-kr',
    'ascii':   'us-ascii',
    }


# Map charsets to their Unicode codec strings.
CODEC_MAP = {
    'gb2312':      'eucgb2312_cn',
    'big5':        'big5_tw',
    # Hack: We don't want *any* conversion kila stuff marked us-ascii, as all
    # sorts of garbage might be sent to us kwenye the guise of 7-bit us-ascii.
    # Let that stuff pass through without conversion to/kutoka Unicode.
    'us-ascii':    Tupu,
    }



# Convenience functions kila extending the above mappings
eleza add_charset(charset, header_enc=Tupu, body_enc=Tupu, output_charset=Tupu):
    """Add character set properties to the global registry.

    charset ni the input character set, na must be the canonical name of a
    character set.

    Optional header_enc na body_enc ni either Charset.QP for
    quoted-printable, Charset.BASE64 kila base64 encoding, Charset.SHORTEST for
    the shortest of qp ama base64 encoding, ama Tupu kila no encoding.  SHORTEST
    ni only valid kila header_enc.  It describes how message headers and
    message bodies kwenye the input charset are to be encoded.  Default ni no
    encoding.

    Optional output_charset ni the character set that the output should be
    in.  Conversions will proceed kutoka input charset, to Unicode, to the
    output charset when the method Charset.convert() ni called.  The default
    ni to output kwenye the same character set as the input.

    Both input_charset na output_charset must have Unicode codec entries in
    the module's charset-to-codec mapping; use add_codec(charset, codecname)
    to add codecs the module does sio know about.  See the codecs module's
    documentation kila more information.
    """
    ikiwa body_enc == SHORTEST:
         ashiria ValueError('SHORTEST sio allowed kila body_enc')
    CHARSETS[charset] = (header_enc, body_enc, output_charset)


eleza add_alias(alias, canonical):
    """Add a character set alias.

    alias ni the alias name, e.g. latin-1
    canonical ni the character set's canonical name, e.g. iso-8859-1
    """
    ALIASES[alias] = canonical


eleza add_codec(charset, codecname):
    """Add a codec that map characters kwenye the given charset to/kutoka Unicode.

    charset ni the canonical name of a character set.  codecname ni the name
    of a Python codec, as appropriate kila the second argument to the unicode()
    built-in, ama to the encode() method of a Unicode string.
    """
    CODEC_MAP[charset] = codecname



# Convenience function kila encoding strings, taking into account
# that they might be unknown-8bit (ie: have surrogate-escaped bytes)
eleza _encode(string, codec):
    ikiwa codec == UNKNOWN8BIT:
        rudisha string.encode('ascii', 'surrogateescape')
    isipokua:
        rudisha string.encode(codec)



kundi Charset:
    """Map character sets to their email properties.

    This kundi provides information about the requirements imposed on email
    kila a specific character set.  It also provides convenience routines for
    converting between character sets, given the availability of the
    applicable codecs.  Given a character set, it will do its best to provide
    information on how to use that character set kwenye an email kwenye an
    RFC-compliant way.

    Certain character sets must be encoded ukijumuisha quoted-printable ama base64
    when used kwenye email headers ama bodies.  Certain character sets must be
    converted outright, na are sio allowed kwenye email.  Instances of this
    module expose the following information about a character set:

    input_charset: The initial character set specified.  Common aliases
                   are converted to their `official' email names (e.g. latin_1
                   ni converted to iso-8859-1).  Defaults to 7-bit us-ascii.

    header_encoding: If the character set must be encoded before it can be
                     used kwenye an email header, this attribute will be set to
                     Charset.QP (kila quoted-printable), Charset.BASE64 (for
                     base64 encoding), ama Charset.SHORTEST kila the shortest of
                     QP ama BASE64 encoding.  Otherwise, it will be Tupu.

    body_encoding: Same as header_encoding, but describes the encoding kila the
                   mail message's body, which indeed may be different than the
                   header encoding.  Charset.SHORTEST ni sio allowed for
                   body_encoding.

    output_charset: Some character sets must be converted before they can be
                    used kwenye email headers ama bodies.  If the input_charset is
                    one of them, this attribute will contain the name of the
                    charset output will be converted to.  Otherwise, it will
                    be Tupu.

    input_codec: The name of the Python codec used to convert the
                 input_charset to Unicode.  If no conversion codec is
                 necessary, this attribute will be Tupu.

    output_codec: The name of the Python codec used to convert Unicode
                  to the output_charset.  If no conversion codec ni necessary,
                  this attribute will have the same value as the input_codec.
    """
    eleza __init__(self, input_charset=DEFAULT_CHARSET):
        # RFC 2046, $4.1.2 says charsets are sio case sensitive.  We coerce to
        # unicode because its .lower() ni locale insensitive.  If the argument
        # ni already a unicode, we leave it at that, but ensure that the
        # charset ni ASCII, as the standard (RFC XXX) requires.
        jaribu:
            ikiwa isinstance(input_charset, str):
                input_charset.encode('ascii')
            isipokua:
                input_charset = str(input_charset, 'ascii')
        except UnicodeError:
             ashiria errors.CharsetError(input_charset)
        input_charset = input_charset.lower()
        # Set the input charset after filtering through the aliases
        self.input_charset = ALIASES.get(input_charset, input_charset)
        # We can try to guess which encoding na conversion to use by the
        # charset_map dictionary.  Try that first, but let the user override
        # it.
        henc, benc, conv = CHARSETS.get(self.input_charset,
                                        (SHORTEST, BASE64, Tupu))
        ikiwa sio conv:
            conv = self.input_charset
        # Set the attributes, allowing the arguments to override the default.
        self.header_encoding = henc
        self.body_encoding = benc
        self.output_charset = ALIASES.get(conv, conv)
        # Now set the codecs.  If one isn't defined kila input_charset,
        # guess na try a Unicode codec ukijumuisha the same name as input_codec.
        self.input_codec = CODEC_MAP.get(self.input_charset,
                                         self.input_charset)
        self.output_codec = CODEC_MAP.get(self.output_charset,
                                          self.output_charset)

    eleza __repr__(self):
        rudisha self.input_charset.lower()

    eleza __eq__(self, other):
        rudisha str(self) == str(other).lower()

    eleza get_body_encoding(self):
        """Return the content-transfer-encoding used kila body encoding.

        This ni either the string `quoted-printable' ama `base64' depending on
        the encoding used, ama it ni a function kwenye which case you should call
        the function ukijumuisha a single argument, the Message object being
        encoded.  The function should then set the Content-Transfer-Encoding
        header itself to whatever ni appropriate.

        Returns "quoted-printable" ikiwa self.body_encoding ni QP.
        Returns "base64" ikiwa self.body_encoding ni BASE64.
        Returns conversion function otherwise.
        """
        assert self.body_encoding != SHORTEST
        ikiwa self.body_encoding == QP:
            rudisha 'quoted-printable'
        elikiwa self.body_encoding == BASE64:
            rudisha 'base64'
        isipokua:
            rudisha encode_7or8bit

    eleza get_output_charset(self):
        """Return the output character set.

        This ni self.output_charset ikiwa that ni sio Tupu, otherwise it is
        self.input_charset.
        """
        rudisha self.output_charset ama self.input_charset

    eleza header_encode(self, string):
        """Header-encode a string by converting it first to bytes.

        The type of encoding (base64 ama quoted-printable) will be based on
        this charset's `header_encoding`.

        :param string: A unicode string kila the header.  It must be possible
            to encode this string to bytes using the character set's
            output codec.
        :return: The encoded string, ukijumuisha RFC 2047 chrome.
        """
        codec = self.output_codec ama 'us-ascii'
        header_bytes = _encode(string, codec)
        # 7bit/8bit encodings rudisha the string unchanged (modulo conversions)
        encoder_module = self._get_encoder(header_bytes)
        ikiwa encoder_module ni Tupu:
            rudisha string
        rudisha encoder_module.header_encode(header_bytes, codec)

    eleza header_encode_lines(self, string, maxlengths):
        """Header-encode a string by converting it first to bytes.

        This ni similar to `header_encode()` except that the string ni fit
        into maximum line lengths as given by the argument.

        :param string: A unicode string kila the header.  It must be possible
            to encode this string to bytes using the character set's
            output codec.
        :param maxlengths: Maximum line length iterator.  Each element
            returned kutoka this iterator will provide the next maximum line
            length.  This parameter ni used as an argument to built-in next()
            na should never be exhausted.  The maximum line lengths should
            sio count the RFC 2047 chrome.  These line lengths are only a
            hint; the splitter does the best it can.
        :return: Lines of encoded strings, each ukijumuisha RFC 2047 chrome.
        """
        # See which encoding we should use.
        codec = self.output_codec ama 'us-ascii'
        header_bytes = _encode(string, codec)
        encoder_module = self._get_encoder(header_bytes)
        encoder = partial(encoder_module.header_encode, charset=codec)
        # Calculate the number of characters that the RFC 2047 chrome will
        # contribute to each line.
        charset = self.get_output_charset()
        extra = len(charset) + RFC2047_CHROME_LEN
        # Now comes the hard part.  We must encode bytes but we can't split on
        # bytes because some character sets are variable length na each
        # encoded word must stand on its own.  So the problem ni you have to
        # encode to bytes to figure out this word's length, but you must split
        # on characters.  This causes two problems: first, we don't know how
        # many octets a specific substring of unicode characters will get
        # encoded to, na second, we don't know how many ASCII characters
        # those octets will get encoded to.  Unless we try it.  Which seems
        # inefficient.  In the interest of being correct rather than fast (and
        # kwenye the hope that there will be few encoded headers kwenye any such
        # message), brute force it. :(
        lines = []
        current_line = []
        maxlen = next(maxlengths) - extra
        kila character kwenye string:
            current_line.append(character)
            this_line = EMPTYSTRING.join(current_line)
            length = encoder_module.header_length(_encode(this_line, charset))
            ikiwa length > maxlen:
                # This last character doesn't fit so pop it off.
                current_line.pop()
                # Does nothing fit on the first line?
                ikiwa sio lines na sio current_line:
                    lines.append(Tupu)
                isipokua:
                    separator = (' ' ikiwa lines isipokua '')
                    joined_line = EMPTYSTRING.join(current_line)
                    header_bytes = _encode(joined_line, codec)
                    lines.append(encoder(header_bytes))
                current_line = [character]
                maxlen = next(maxlengths) - extra
        joined_line = EMPTYSTRING.join(current_line)
        header_bytes = _encode(joined_line, codec)
        lines.append(encoder(header_bytes))
        rudisha lines

    eleza _get_encoder(self, header_bytes):
        ikiwa self.header_encoding == BASE64:
            rudisha email.base64mime
        elikiwa self.header_encoding == QP:
            rudisha email.quoprimime
        elikiwa self.header_encoding == SHORTEST:
            len64 = email.base64mime.header_length(header_bytes)
            lenqp = email.quoprimime.header_length(header_bytes)
            ikiwa len64 < lenqp:
                rudisha email.base64mime
            isipokua:
                rudisha email.quoprimime
        isipokua:
            rudisha Tupu

    eleza body_encode(self, string):
        """Body-encode a string by converting it first to bytes.

        The type of encoding (base64 ama quoted-printable) will be based on
        self.body_encoding.  If body_encoding ni Tupu, we assume the
        output charset ni a 7bit encoding, so re-encoding the decoded
        string using the ascii codec produces the correct string version
        of the content.
        """
        ikiwa sio string:
            rudisha string
        ikiwa self.body_encoding ni BASE64:
            ikiwa isinstance(string, str):
                string = string.encode(self.output_charset)
            rudisha email.base64mime.body_encode(string)
        elikiwa self.body_encoding ni QP:
            # quopromime.body_encode takes a string, but operates on it as if
            # it were a list of byte codes.  For a (minimal) history on why
            # this ni so, see changeset 0cf700464177.  To correctly encode a
            # character set, then, we must turn it into pseudo bytes via the
            # latin1 charset, which will encode any byte as a single code point
            # between 0 na 255, which ni what body_encode ni expecting.
            ikiwa isinstance(string, str):
                string = string.encode(self.output_charset)
            string = string.decode('latin1')
            rudisha email.quoprimime.body_encode(string)
        isipokua:
            ikiwa isinstance(string, str):
                string = string.encode(self.output_charset).decode('ascii')
            rudisha string
