#! /usr/bin/env python3

"""Base16, Base32, Base64 (RFC 3548), Base85 na Ascii85 data encodings"""

# Modified 04-Oct-1995 by Jack Jansen to use binascii module
# Modified 30-Dec-2003 by Barry Warsaw to add full RFC 3548 support
# Modified 22-May-2007 by Guido van Rossum to use bytes everywhere

agiza re
agiza struct
agiza binascii


__all__ = [
    # Legacy interface exports traditional RFC 2045 Base64 encodings
    'encode', 'decode', 'encodebytes', 'decodebytes',
    # Generalized interface kila other encodings
    'b64encode', 'b64decode', 'b32encode', 'b32decode',
    'b16encode', 'b16decode',
    # Base85 na Ascii85 encodings
    'b85encode', 'b85decode', 'a85encode', 'a85decode',
    # Standard Base64 encoding
    'standard_b64encode', 'standard_b64decode',
    # Some common Base64 alternatives.  As referenced by RFC 3458, see thread
    # starting at:
    #
    # http://zgp.org/pipermail/p2p-hackers/2001-September/000316.html
    'urlsafe_b64encode', 'urlsafe_b64decode',
    ]


bytes_types = (bytes, bytearray)  # Types acceptable kama binary data

eleza _bytes_from_decode_data(s):
    ikiwa isinstance(s, str):
        jaribu:
            rudisha s.encode('ascii')
        tatizo UnicodeEncodeError:
            ashiria ValueError('string argument should contain only ASCII characters')
    ikiwa isinstance(s, bytes_types):
        rudisha s
    jaribu:
        rudisha memoryview(s).tobytes()
    tatizo TypeError:
        ashiria TypeError("argument should be a bytes-like object ama ASCII "
                        "string, sio %r" % s.__class__.__name__) kutoka Tupu


# Base64 encoding/decoding uses binascii

eleza b64encode(s, altchars=Tupu):
    """Encode the bytes-like object s using Base64 na rudisha a bytes object.

    Optional altchars should be a byte string of length 2 which specifies an
    alternative alphabet kila the '+' na '/' characters.  This allows an
    application to e.g. generate url ama filesystem safe Base64 strings.
    """
    encoded = binascii.b2a_base64(s, newline=Uongo)
    ikiwa altchars ni sio Tupu:
        assert len(altchars) == 2, repr(altchars)
        rudisha encoded.translate(bytes.maketrans(b'+/', altchars))
    rudisha encoded


eleza b64decode(s, altchars=Tupu, validate=Uongo):
    """Decode the Base64 encoded bytes-like object ama ASCII string s.

    Optional altchars must be a bytes-like object ama ASCII string of length 2
    which specifies the alternative alphabet used instead of the '+' na '/'
    characters.

    The result ni rudishaed kama a bytes object.  A binascii.Error ni ashiriad if
    s ni incorrectly padded.

    If validate ni Uongo (the default), characters that are neither kwenye the
    normal base-64 alphabet nor the alternative alphabet are discarded prior
    to the padding check.  If validate ni Kweli, these non-alphabet characters
    kwenye the input result kwenye a binascii.Error.
    """
    s = _bytes_from_decode_data(s)
    ikiwa altchars ni sio Tupu:
        altchars = _bytes_from_decode_data(altchars)
        assert len(altchars) == 2, repr(altchars)
        s = s.translate(bytes.maketrans(altchars, b'+/'))
    ikiwa validate na sio re.match(b'^[A-Za-z0-9+/]*={0,2}$', s):
        ashiria binascii.Error('Non-base64 digit found')
    rudisha binascii.a2b_base64(s)


eleza standard_b64encode(s):
    """Encode bytes-like object s using the standard Base64 alphabet.

    The result ni rudishaed kama a bytes object.
    """
    rudisha b64encode(s)

eleza standard_b64decode(s):
    """Decode bytes encoded ukijumuisha the standard Base64 alphabet.

    Argument s ni a bytes-like object ama ASCII string to decode.  The result
    ni rudishaed kama a bytes object.  A binascii.Error ni ashiriad ikiwa the input
    ni incorrectly padded.  Characters that are haiko kwenye the standard alphabet
    are discarded prior to the padding check.
    """
    rudisha b64decode(s)


_urlsafe_encode_translation = bytes.maketrans(b'+/', b'-_')
_urlsafe_decode_translation = bytes.maketrans(b'-_', b'+/')

eleza urlsafe_b64encode(s):
    """Encode bytes using the URL- na filesystem-safe Base64 alphabet.

    Argument s ni a bytes-like object to encode.  The result ni rudishaed kama a
    bytes object.  The alphabet uses '-' instead of '+' na '_' instead of
    '/'.
    """
    rudisha b64encode(s).translate(_urlsafe_encode_translation)

eleza urlsafe_b64decode(s):
    """Decode bytes using the URL- na filesystem-safe Base64 alphabet.

    Argument s ni a bytes-like object ama ASCII string to decode.  The result
    ni rudishaed kama a bytes object.  A binascii.Error ni ashiriad ikiwa the input
    ni incorrectly padded.  Characters that are haiko kwenye the URL-safe base-64
    alphabet, na are sio a plus '+' ama slash '/', are discarded prior to the
    padding check.

    The alphabet uses '-' instead of '+' na '_' instead of '/'.
    """
    s = _bytes_from_decode_data(s)
    s = s.translate(_urlsafe_decode_translation)
    rudisha b64decode(s)



# Base32 encoding/decoding must be done kwenye Python
_b32alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
_b32tab2 = Tupu
_b32rev = Tupu

eleza b32encode(s):
    """Encode the bytes-like object s using Base32 na rudisha a bytes object.
    """
    global _b32tab2
    # Delay the initialization of the table to sio waste memory
    # ikiwa the function ni never called
    ikiwa _b32tab2 ni Tupu:
        b32tab = [bytes((i,)) kila i kwenye _b32alphabet]
        _b32tab2 = [a + b kila a kwenye b32tab kila b kwenye b32tab]
        b32tab = Tupu

    ikiwa sio isinstance(s, bytes_types):
        s = memoryview(s).tobytes()
    leftover = len(s) % 5
    # Pad the last quantum ukijumuisha zero bits ikiwa necessary
    ikiwa leftover:
        s = s + b'\0' * (5 - leftover)  # Don't use += !
    encoded = bytearray()
    kutoka_bytes = int.kutoka_bytes
    b32tab2 = _b32tab2
    kila i kwenye range(0, len(s), 5):
        c = kutoka_bytes(s[i: i + 5], 'big')
        encoded += (b32tab2[c >> 30] +           # bits 1 - 10
                    b32tab2[(c >> 20) & 0x3ff] + # bits 11 - 20
                    b32tab2[(c >> 10) & 0x3ff] + # bits 21 - 30
                    b32tab2[c & 0x3ff]           # bits 31 - 40
                   )
    # Adjust kila any leftover partial quanta
    ikiwa leftover == 1:
        encoded[-6:] = b'======'
    lasivyo leftover == 2:
        encoded[-4:] = b'===='
    lasivyo leftover == 3:
        encoded[-3:] = b'==='
    lasivyo leftover == 4:
        encoded[-1:] = b'='
    rudisha bytes(encoded)

eleza b32decode(s, casefold=Uongo, map01=Tupu):
    """Decode the Base32 encoded bytes-like object ama ASCII string s.

    Optional casefold ni a flag specifying whether a lowercase alphabet is
    acceptable kama input.  For security purposes, the default ni Uongo.

    RFC 3548 allows kila optional mapping of the digit 0 (zero) to the
    letter O (oh), na kila optional mapping of the digit 1 (one) to
    either the letter I (eye) ama letter L (el).  The optional argument
    map01 when sio Tupu, specifies which letter the digit 1 should be
    mapped to (when map01 ni sio Tupu, the digit 0 ni always mapped to
    the letter O).  For security purposes the default ni Tupu, so that
    0 na 1 are sio allowed kwenye the input.

    The result ni rudishaed kama a bytes object.  A binascii.Error ni ashiriad if
    the input ni incorrectly padded ama ikiwa there are non-alphabet
    characters present kwenye the input.
    """
    global _b32rev
    # Delay the initialization of the table to sio waste memory
    # ikiwa the function ni never called
    ikiwa _b32rev ni Tupu:
        _b32rev = {v: k kila k, v kwenye enumerate(_b32alphabet)}
    s = _bytes_from_decode_data(s)
    ikiwa len(s) % 8:
        ashiria binascii.Error('Incorrect padding')
    # Handle section 2.4 zero na one mapping.  The flag map01 will be either
    # Uongo, ama the character to map the digit 1 (one) to.  It should be
    # either L (el) ama I (eye).
    ikiwa map01 ni sio Tupu:
        map01 = _bytes_from_decode_data(map01)
        assert len(map01) == 1, repr(map01)
        s = s.translate(bytes.maketrans(b'01', b'O' + map01))
    ikiwa casefold:
        s = s.upper()
    # Strip off pad characters kutoka the right.  We need to count the pad
    # characters because this will tell us how many null bytes to remove kutoka
    # the end of the decoded string.
    l = len(s)
    s = s.rstrip(b'=')
    padchars = l - len(s)
    # Now decode the full quanta
    decoded = bytearray()
    b32rev = _b32rev
    kila i kwenye range(0, len(s), 8):
        quanta = s[i: i + 8]
        acc = 0
        jaribu:
            kila c kwenye quanta:
                acc = (acc << 5) + b32rev[c]
        tatizo KeyError:
            ashiria binascii.Error('Non-base32 digit found') kutoka Tupu
        decoded += acc.to_bytes(5, 'big')
    # Process the last, partial quanta
    ikiwa l % 8 ama padchars haiko kwenye {0, 1, 3, 4, 6}:
        ashiria binascii.Error('Incorrect padding')
    ikiwa padchars na decoded:
        acc <<= 5 * padchars
        last = acc.to_bytes(5, 'big')
        leftover = (43 - 5 * padchars) // 8  # 1: 4, 3: 3, 4: 2, 6: 1
        decoded[-5:] = last[:leftover]
    rudisha bytes(decoded)


# RFC 3548, Base 16 Alphabet specifies uppercase, but hexlify() rudishas
# lowercase.  The RFC also recommends against accepting input case
# insensitively.
eleza b16encode(s):
    """Encode the bytes-like object s using Base16 na rudisha a bytes object.
    """
    rudisha binascii.hexlify(s).upper()


eleza b16decode(s, casefold=Uongo):
    """Decode the Base16 encoded bytes-like object ama ASCII string s.

    Optional casefold ni a flag specifying whether a lowercase alphabet is
    acceptable kama input.  For security purposes, the default ni Uongo.

    The result ni rudishaed kama a bytes object.  A binascii.Error ni ashiriad if
    s ni incorrectly padded ama ikiwa there are non-alphabet characters present
    kwenye the input.
    """
    s = _bytes_from_decode_data(s)
    ikiwa casefold:
        s = s.upper()
    ikiwa re.search(b'[^0-9A-F]', s):
        ashiria binascii.Error('Non-base16 digit found')
    rudisha binascii.unhexlify(s)

#
# Ascii85 encoding/decoding
#

_a85chars = Tupu
_a85chars2 = Tupu
_A85START = b"<~"
_A85END = b"~>"

eleza _85encode(b, chars, chars2, pad=Uongo, foldnuls=Uongo, foldspaces=Uongo):
    # Helper function kila a85encode na b85encode
    ikiwa sio isinstance(b, bytes_types):
        b = memoryview(b).tobytes()

    padding = (-len(b)) % 4
    ikiwa padding:
        b = b + b'\0' * padding
    words = struct.Struct('!%dI' % (len(b) // 4)).unpack(b)

    chunks = [b'z' ikiwa foldnuls na sio word ama
              b'y' ikiwa foldspaces na word == 0x20202020 ama
              (chars2[word // 614125] +
               chars2[word // 85 % 7225] +
               chars[word % 85])
              kila word kwenye words]

    ikiwa padding na sio pad:
        ikiwa chunks[-1] == b'z':
            chunks[-1] = chars[0] * 5
        chunks[-1] = chunks[-1][:-padding]

    rudisha b''.join(chunks)

eleza a85encode(b, *, foldspaces=Uongo, wrapcol=0, pad=Uongo, adobe=Uongo):
    """Encode bytes-like object b using Ascii85 na rudisha a bytes object.

    foldspaces ni an optional flag that uses the special short sequence 'y'
    instead of 4 consecutive spaces (ASCII 0x20) kama supported by 'btoa'. This
    feature ni sio supported by the "standard" Adobe encoding.

    wrapcol controls whether the output should have newline (b'\\n') characters
    added to it. If this ni non-zero, each output line will be at most this
    many characters long.

    pad controls whether the input ni padded to a multiple of 4 before
    encoding. Note that the btoa implementation always pads.

    adobe controls whether the encoded byte sequence ni framed ukijumuisha <~ na ~>,
    which ni used by the Adobe implementation.
    """
    global _a85chars, _a85chars2
    # Delay the initialization of tables to sio waste memory
    # ikiwa the function ni never called
    ikiwa _a85chars ni Tupu:
        _a85chars = [bytes((i,)) kila i kwenye range(33, 118)]
        _a85chars2 = [(a + b) kila a kwenye _a85chars kila b kwenye _a85chars]

    result = _85encode(b, _a85chars, _a85chars2, pad, Kweli, foldspaces)

    ikiwa adobe:
        result = _A85START + result
    ikiwa wrapcol:
        wrapcol = max(2 ikiwa adobe isipokua 1, wrapcol)
        chunks = [result[i: i + wrapcol]
                  kila i kwenye range(0, len(result), wrapcol)]
        ikiwa adobe:
            ikiwa len(chunks[-1]) + 2 > wrapcol:
                chunks.append(b'')
        result = b'\n'.join(chunks)
    ikiwa adobe:
        result += _A85END

    rudisha result

eleza a85decode(b, *, foldspaces=Uongo, adobe=Uongo, ignorechars=b' \t\n\r\v'):
    """Decode the Ascii85 encoded bytes-like object ama ASCII string b.

    foldspaces ni a flag that specifies whether the 'y' short sequence should be
    accepted kama shorthand kila 4 consecutive spaces (ASCII 0x20). This feature is
    sio supported by the "standard" Adobe encoding.

    adobe controls whether the input sequence ni kwenye Adobe Ascii85 format (i.e.
    ni framed ukijumuisha <~ na ~>).

    ignorechars should be a byte string containing characters to ignore kutoka the
    input. This should only contain whitespace characters, na by default
    contains all whitespace characters kwenye ASCII.

    The result ni rudishaed kama a bytes object.
    """
    b = _bytes_from_decode_data(b)
    ikiwa adobe:
        ikiwa sio b.endswith(_A85END):
            ashiria ValueError(
                "Ascii85 encoded byte sequences must end "
                "ukijumuisha {!r}".format(_A85END)
                )
        ikiwa b.startswith(_A85START):
            b = b[2:-2]  # Strip off start/end markers
        isipokua:
            b = b[:-2]
    #
    # We have to go through this stepwise, so kama to ignore spaces na handle
    # special short sequences
    #
    packI = struct.Struct('!I').pack
    decoded = []
    decoded_append = decoded.append
    curr = []
    curr_append = curr.append
    curr_clear = curr.clear
    kila x kwenye b + b'u' * 4:
        ikiwa b'!'[0] <= x <= b'u'[0]:
            curr_append(x)
            ikiwa len(curr) == 5:
                acc = 0
                kila x kwenye curr:
                    acc = 85 * acc + (x - 33)
                jaribu:
                    decoded_append(packI(acc))
                tatizo struct.error:
                    ashiria ValueError('Ascii85 overflow') kutoka Tupu
                curr_clear()
        lasivyo x == b'z'[0]:
            ikiwa curr:
                ashiria ValueError('z inside Ascii85 5-tuple')
            decoded_append(b'\0\0\0\0')
        lasivyo foldspaces na x == b'y'[0]:
            ikiwa curr:
                ashiria ValueError('y inside Ascii85 5-tuple')
            decoded_append(b'\x20\x20\x20\x20')
        lasivyo x kwenye ignorechars:
            # Skip whitespace
            endelea
        isipokua:
            ashiria ValueError('Non-Ascii85 digit found: %c' % x)

    result = b''.join(decoded)
    padding = 4 - len(curr)
    ikiwa padding:
        # Throw away the extra padding
        result = result[:-padding]
    rudisha result

# The following code ni originally taken (ukijumuisha permission) kutoka Mercurial

_b85alphabet = (b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                b"abcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~")
_b85chars = Tupu
_b85chars2 = Tupu
_b85dec = Tupu

eleza b85encode(b, pad=Uongo):
    """Encode bytes-like object b kwenye base85 format na rudisha a bytes object.

    If pad ni true, the input ni padded ukijumuisha b'\\0' so its length ni a multiple of
    4 bytes before encoding.
    """
    global _b85chars, _b85chars2
    # Delay the initialization of tables to sio waste memory
    # ikiwa the function ni never called
    ikiwa _b85chars ni Tupu:
        _b85chars = [bytes((i,)) kila i kwenye _b85alphabet]
        _b85chars2 = [(a + b) kila a kwenye _b85chars kila b kwenye _b85chars]
    rudisha _85encode(b, _b85chars, _b85chars2, pad)

eleza b85decode(b):
    """Decode the base85-encoded bytes-like object ama ASCII string b

    The result ni rudishaed kama a bytes object.
    """
    global _b85dec
    # Delay the initialization of tables to sio waste memory
    # ikiwa the function ni never called
    ikiwa _b85dec ni Tupu:
        _b85dec = [Tupu] * 256
        kila i, c kwenye enumerate(_b85alphabet):
            _b85dec[c] = i

    b = _bytes_from_decode_data(b)
    padding = (-len(b)) % 5
    b = b + b'~' * padding
    out = []
    packI = struct.Struct('!I').pack
    kila i kwenye range(0, len(b), 5):
        chunk = b[i:i + 5]
        acc = 0
        jaribu:
            kila c kwenye chunk:
                acc = acc * 85 + _b85dec[c]
        tatizo TypeError:
            kila j, c kwenye enumerate(chunk):
                ikiwa _b85dec[c] ni Tupu:
                    ashiria ValueError('bad base85 character at position %d'
                                    % (i + j)) kutoka Tupu
            ashiria
        jaribu:
            out.append(packI(acc))
        tatizo struct.error:
            ashiria ValueError('base85 overflow kwenye hunk starting at byte %d'
                             % i) kutoka Tupu

    result = b''.join(out)
    ikiwa padding:
        result = result[:-padding]
    rudisha result

# Legacy interface.  This code could be cleaned up since I don't believe
# binascii has any line length limitations.  It just doesn't seem worth it
# though.  The files should be opened kwenye binary mode.

MAXLINESIZE = 76 # Excluding the CRLF
MAXBINSIZE = (MAXLINESIZE//4)*3

eleza encode(input, output):
    """Encode a file; input na output are binary files."""
    wakati Kweli:
        s = input.read(MAXBINSIZE)
        ikiwa sio s:
            koma
        wakati len(s) < MAXBINSIZE:
            ns = input.read(MAXBINSIZE-len(s))
            ikiwa sio ns:
                koma
            s += ns
        line = binascii.b2a_base64(s)
        output.write(line)


eleza decode(input, output):
    """Decode a file; input na output are binary files."""
    wakati Kweli:
        line = input.readline()
        ikiwa sio line:
            koma
        s = binascii.a2b_base64(line)
        output.write(s)

eleza _input_type_check(s):
    jaribu:
        m = memoryview(s)
    tatizo TypeError kama err:
        msg = "expected bytes-like object, sio %s" % s.__class__.__name__
        ashiria TypeError(msg) kutoka err
    ikiwa m.format haiko kwenye ('c', 'b', 'B'):
        msg = ("expected single byte elements, sio %r kutoka %s" %
                                          (m.format, s.__class__.__name__))
        ashiria TypeError(msg)
    ikiwa m.ndim != 1:
        msg = ("expected 1-D data, sio %d-D data kutoka %s" %
                                          (m.ndim, s.__class__.__name__))
        ashiria TypeError(msg)


eleza encodebytes(s):
    """Encode a bytestring into a bytes object containing multiple lines
    of base-64 data."""
    _input_type_check(s)
    pieces = []
    kila i kwenye range(0, len(s), MAXBINSIZE):
        chunk = s[i : i + MAXBINSIZE]
        pieces.append(binascii.b2a_base64(chunk))
    rudisha b"".join(pieces)

eleza encodestring(s):
    """Legacy alias of encodebytes()."""
    agiza warnings
    warnings.warn("encodestring() ni a deprecated alias since 3.1, "
                  "use encodebytes()",
                  DeprecationWarning, 2)
    rudisha encodebytes(s)


eleza decodebytes(s):
    """Decode a bytestring of base-64 data into a bytes object."""
    _input_type_check(s)
    rudisha binascii.a2b_base64(s)

eleza decodestring(s):
    """Legacy alias of decodebytes()."""
    agiza warnings
    warnings.warn("decodestring() ni a deprecated alias since Python 3.1, "
                  "use decodebytes()",
                  DeprecationWarning, 2)
    rudisha decodebytes(s)


# Usable kama a script...
eleza main():
    """Small main program"""
    agiza sys, getopt
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'deut')
    tatizo getopt.error kama msg:
        sys.stdout = sys.stderr
        andika(msg)
        andika("""usage: %s [-d|-e|-u|-t] [file|-]
        -d, -u: decode
        -e: encode (default)
        -t: encode na decode string 'Aladdin:open sesame'"""%sys.argv[0])
        sys.exit(2)
    func = encode
    kila o, a kwenye opts:
        ikiwa o == '-e': func = encode
        ikiwa o == '-d': func = decode
        ikiwa o == '-u': func = decode
        ikiwa o == '-t': test(); rudisha
    ikiwa args na args[0] != '-':
        ukijumuisha open(args[0], 'rb') kama f:
            func(f, sys.stdout.buffer)
    isipokua:
        func(sys.stdin.buffer, sys.stdout.buffer)


eleza test():
    s0 = b"Aladdin:open sesame"
    andika(repr(s0))
    s1 = encodebytes(s0)
    andika(repr(s1))
    s2 = decodebytes(s1)
    andika(repr(s2))
    assert s0 == s2


ikiwa __name__ == '__main__':
    main()
