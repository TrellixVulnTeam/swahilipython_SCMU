""" Routines kila manipulating RFC2047 encoded words.

This ni currently a package-private API, but will be considered kila promotion
to a public API ikiwa there ni demand.

"""

# An ecoded word looks like this:
#
#        =?charset[*lang]?cte?encoded_string?=
#
# kila more information about charset see the charset module.  Here it ni one
# of the preferred MIME charset names (hopefully; you never know when parsing).
# cte (Content Transfer Encoding) ni either 'q' ama 'b' (ignoring case).  In
# theory other letters could be used kila other encodings, but kwenye practice this
# (almost?) never happens.  There could be a public API kila adding entries
# to the CTE tables, but YAGNI kila now.  'q' ni Quoted Printable, 'b' is
# Base64.  The meaning of encoded_string should be obvious.  'lang' ni optional
# kama indicated by the brackets (they are sio part of the syntax) but ni almost
# never encountered kwenye practice.
#
# The general interface kila a CTE decoder ni that it takes the encoded_string
# kama its argument, na returns a tuple (cte_decoded_string, defects).  The
# cte_decoded_string ni the original binary that was encoded using the
# specified cte.  'defects' ni a list of MessageDefect instances indicating any
# problems encountered during conversion.  'charset' na 'lang' are the
# corresponding strings extracted kutoka the EW, case preserved.
#
# The general interface kila a CTE encoder ni that it takes a binary sequence
# kama input na returns the cte_encoded_string, which ni an ascii-only string.
#
# Each decoder must also supply a length function that takes the binary
# sequence kama its argument na returns the length of the resulting encoded
# string.
#
# The main API functions kila the module are decode, which calls the decoder
# referenced by the cte specifier, na encode, which adds the appropriate
# RFC 2047 "chrome" to the encoded string, na can optionally automatically
# select the shortest possible encoding.  See their docstrings below for
# details.

agiza re
agiza base64
agiza binascii
agiza functools
kutoka string agiza ascii_letters, digits
kutoka email agiza errors

__all__ = ['decode_q',
           'encode_q',
           'decode_b',
           'encode_b',
           'len_q',
           'len_b',
           'decode',
           'encode',
           ]

#
# Quoted Printable
#

# regex based decoder.
_q_byte_subber = functools.partial(re.compile(br'=([a-fA-F0-9]{2})').sub,
        lambda m: bytes.fromhex(m.group(1).decode()))

eleza decode_q(encoded):
    encoded = encoded.replace(b'_', b' ')
    rudisha _q_byte_subber(encoded), []


# dict mapping bytes to their encoded form
kundi _QByteMap(dict):

    safe = b'-!*+/' + ascii_letters.encode('ascii') + digits.encode('ascii')

    eleza __missing__(self, key):
        ikiwa key kwenye self.safe:
            self[key] = chr(key)
        isipokua:
            self[key] = "={:02X}".format(key)
        rudisha self[key]

_q_byte_map = _QByteMap()

# In headers spaces are mapped to '_'.
_q_byte_map[ord(' ')] = '_'

eleza encode_q(bstring):
    rudisha ''.join(_q_byte_map[x] kila x kwenye bstring)

eleza len_q(bstring):
    rudisha sum(len(_q_byte_map[x]) kila x kwenye bstring)


#
# Base64
#

eleza decode_b(encoded):
    # First try encoding ukijumuisha validate=Kweli, fixing the padding ikiwa needed.
    # This will succeed only ikiwa encoded includes no invalid characters.
    pad_err = len(encoded) % 4
    missing_padding = b'==='[:4-pad_err] ikiwa pad_err isipokua b''
    jaribu:
        rudisha (
            base64.b64decode(encoded + missing_padding, validate=Kweli),
            [errors.InvalidBase64PaddingDefect()] ikiwa pad_err isipokua [],
        )
    tatizo binascii.Error:
        # Since we had correct padding, this ni likely an invalid char error.
        #
        # The non-alphabet characters are ignored kama far kama padding
        # goes, but we don't know how many there are.  So try without adding
        # padding to see ikiwa it works.
        jaribu:
            rudisha (
                base64.b64decode(encoded, validate=Uongo),
                [errors.InvalidBase64CharactersDefect()],
            )
        tatizo binascii.Error:
            # Add kama much padding kama could possibly be necessary (extra padding
            # ni ignored).
            jaribu:
                rudisha (
                    base64.b64decode(encoded + b'==', validate=Uongo),
                    [errors.InvalidBase64CharactersDefect(),
                     errors.InvalidBase64PaddingDefect()],
                )
            tatizo binascii.Error:
                # This only happens when the encoded string's length ni 1 more
                # than a multiple of 4, which ni invalid.
                #
                # bpo-27397: Just rudisha the encoded string since there's no
                # way to decode.
                rudisha encoded, [errors.InvalidBase64LengthDefect()]

eleza encode_b(bstring):
    rudisha base64.b64encode(bstring).decode('ascii')

eleza len_b(bstring):
    groups_of_3, leftover = divmod(len(bstring), 3)
    # 4 bytes out kila each 3 bytes (or nonzero fraction thereof) in.
    rudisha groups_of_3 * 4 + (4 ikiwa leftover isipokua 0)


_cte_decoders = {
    'q': decode_q,
    'b': decode_b,
    }

eleza decode(ew):
    """Decode encoded word na rudisha (string, charset, lang, defects) tuple.

    An RFC 2047/2243 encoded word has the form:

        =?charset*lang?cte?encoded_string?=

    where '*lang' may be omitted but the other parts may sio be.

    This function expects exactly such a string (that is, it does sio check the
    syntax na may ashiria errors ikiwa the string ni sio well formed), na returns
    the encoded_string decoded first kutoka its Content Transfer Encoding na
    then kutoka the resulting bytes into unicode using the specified charset.  If
    the cte-decoded string does sio successfully decode using the specified
    character set, a defect ni added to the defects list na the unknown octets
    are replaced by the unicode 'unknown' character \\uFDFF.

    The specified charset na language are returned.  The default kila language,
    which ni rarely ikiwa ever encountered, ni the empty string.

    """
    _, charset, cte, cte_string, _ = ew.split('?')
    charset, _, lang = charset.partition('*')
    cte = cte.lower()
    # Recover the original bytes na do CTE decoding.
    bstring = cte_string.encode('ascii', 'surrogateescape')
    bstring, defects = _cte_decoders[cte](bstring)
    # Turn the CTE decoded bytes into unicode.
    jaribu:
        string = bstring.decode(charset)
    tatizo UnicodeError:
        defects.append(errors.UndecodableBytesDefect("Encoded word "
            "contains bytes sio decodable using {} charset".format(charset)))
        string = bstring.decode(charset, 'surrogateescape')
    tatizo LookupError:
        string = bstring.decode('ascii', 'surrogateescape')
        ikiwa charset.lower() != 'unknown-8bit':
            defects.append(errors.CharsetError("Unknown charset {} "
                "in encoded word; decoded kama unknown bytes".format(charset)))
    rudisha string, charset, lang, defects


_cte_encoders = {
    'q': encode_q,
    'b': encode_b,
    }

_cte_encode_length = {
    'q': len_q,
    'b': len_b,
    }

eleza encode(string, charset='utf-8', encoding=Tupu, lang=''):
    """Encode string using the CTE encoding that produces the shorter result.

    Produces an RFC 2047/2243 encoded word of the form:

        =?charset*lang?cte?encoded_string?=

    where '*lang' ni omitted unless the 'lang' parameter ni given a value.
    Optional argument charset (defaults to utf-8) specifies the charset to use
    to encode the string to binary before CTE encoding it.  Optional argument
    'encoding' ni the cte specifier kila the encoding that should be used ('q'
    ama 'b'); ikiwa it ni Tupu (the default) the encoding which produces the
    shortest encoded sequence ni used, tatizo that 'q' ni preferred ikiwa it ni up
    to five characters longer.  Optional argument 'lang' (default '') gives the
    RFC 2243 language string to specify kwenye the encoded word.

    """
    ikiwa charset == 'unknown-8bit':
        bstring = string.encode('ascii', 'surrogateescape')
    isipokua:
        bstring = string.encode(charset)
    ikiwa encoding ni Tupu:
        qlen = _cte_encode_length['q'](bstring)
        blen = _cte_encode_length['b'](bstring)
        # Bias toward q.  5 ni arbitrary.
        encoding = 'q' ikiwa qlen - blen < 5 isipokua 'b'
    encoded = _cte_encoders[encoding](bstring)
    ikiwa lang:
        lang = '*' + lang
    rudisha "=?{}{}?{}?{}?=".format(charset, lang, encoding, encoded)
