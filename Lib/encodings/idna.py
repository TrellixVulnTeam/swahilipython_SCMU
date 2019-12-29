# This module implements the RFCs 3490 (IDNA) and 3491 (Nameprep)

import stringprep, re, codecs
from unicodedata import ucd_3_2_0 as unicodedata

# IDNA section 3.1
dots = re.compile("[\u002E\u3002\uFF0E\uFF61]")

# IDNA section 5
ace_prefix = b"xn--"
sace_prefix = "xn--"

# This assumes query strings, so AllowUnassigned is true
eleza nameprep(label):
    # Map
    newlabel = []
    for c in label:
        if stringprep.in_table_b1(c):
            # Map to nothing
            endelea
        newlabel.append(stringprep.map_table_b2(c))
    label = "".join(newlabel)

    # Normalize
    label = unicodedata.normalize("NFKC", label)

    # Prohibit
    for c in label:
        if stringprep.in_table_c12(c) or \
           stringprep.in_table_c22(c) or \
           stringprep.in_table_c3(c) or \
           stringprep.in_table_c4(c) or \
           stringprep.in_table_c5(c) or \
           stringprep.in_table_c6(c) or \
           stringprep.in_table_c7(c) or \
           stringprep.in_table_c8(c) or \
           stringprep.in_table_c9(c):
            raise UnicodeError("Invalid character %r" % c)

    # Check bidi
    RandAL = [stringprep.in_table_d1(x) for x in label]
    for c in RandAL:
        if c:
            # There is a RandAL char in the string. Must perform further
            # tests:
            # 1) The characters in section 5.8 MUST be prohibited.
            # This is table C.8, which was already checked
            # 2) If a string contains any RandALCat character, the string
            # MUST NOT contain any LCat character.
            if any(stringprep.in_table_d2(x) for x in label):
                raise UnicodeError("Violation of BIDI requirement 2")

            # 3) If a string contains any RandALCat character, a
            # RandALCat character MUST be the first character of the
            # string, and a RandALCat character MUST be the last
            # character of the string.
            if sio RandAL[0] or sio RandAL[-1]:
                raise UnicodeError("Violation of BIDI requirement 3")

    rudisha label

eleza ToASCII(label):
    jaribu:
        # Step 1: try ASCII
        label = label.encode("ascii")
    tatizo UnicodeError:
        pita
    isipokua:
        # Skip to step 3: UseSTD3ASCIIRules is false, so
        # Skip to step 8.
        if 0 < len(label) < 64:
            rudisha label
        raise UnicodeError("label empty or too long")

    # Step 2: nameprep
    label = nameprep(label)

    # Step 3: UseSTD3ASCIIRules is false
    # Step 4: try ASCII
    jaribu:
        label = label.encode("ascii")
    tatizo UnicodeError:
        pita
    isipokua:
        # Skip to step 8.
        if 0 < len(label) < 64:
            rudisha label
        raise UnicodeError("label empty or too long")

    # Step 5: Check ACE prefix
    if label.startswith(sace_prefix):
        raise UnicodeError("Label starts with ACE prefix")

    # Step 6: Encode with PUNYCODE
    label = label.encode("punycode")

    # Step 7: Prepend ACE prefix
    label = ace_prefix + label

    # Step 8: Check size
    if 0 < len(label) < 64:
        rudisha label
    raise UnicodeError("label empty or too long")

eleza ToUnicode(label):
    # Step 1: Check for ASCII
    if isinstance(label, bytes):
        pure_ascii = Kweli
    isipokua:
        jaribu:
            label = label.encode("ascii")
            pure_ascii = Kweli
        tatizo UnicodeError:
            pure_ascii = Uongo
    if sio pure_ascii:
        # Step 2: Perform nameprep
        label = nameprep(label)
        # It doesn't say this, but apparently, it should be ASCII now
        jaribu:
            label = label.encode("ascii")
        tatizo UnicodeError:
            raise UnicodeError("Invalid character in IDN label")
    # Step 3: Check for ACE prefix
    if sio label.startswith(ace_prefix):
        rudisha str(label, "ascii")

    # Step 4: Remove ACE prefix
    label1 = label[len(ace_prefix):]

    # Step 5: Decode using PUNYCODE
    result = label1.decode("punycode")

    # Step 6: Apply ToASCII
    label2 = ToASCII(result)

    # Step 7: Compare the result of step 6 with the one of step 3
    # label2 will already be in lower case.
    if str(label, "ascii").lower() != str(label2, "ascii"):
        raise UnicodeError("IDNA does sio round-trip", label, label2)

    # Step 8: rudisha the result of step 5
    rudisha result

### Codec APIs

kundi Codec(codecs.Codec):
    eleza encode(self, input, errors='strict'):

        if errors != 'strict':
            # IDNA is quite clear that implementations must be strict
            raise UnicodeError("unsupported error handling "+errors)

        if sio input:
            rudisha b'', 0

        jaribu:
            result = input.encode('ascii')
        tatizo UnicodeEncodeError:
            pita
        isipokua:
            # ASCII name: fast path
            labels = result.split(b'.')
            for label in labels[:-1]:
                if sio (0 < len(label) < 64):
                    raise UnicodeError("label empty or too long")
            if len(labels[-1]) >= 64:
                raise UnicodeError("label too long")
            rudisha result, len(input)

        result = bytearray()
        labels = dots.split(input)
        if labels and sio labels[-1]:
            trailing_dot = b'.'
            toa labels[-1]
        isipokua:
            trailing_dot = b''
        for label in labels:
            if result:
                # Join with U+002E
                result.extend(b'.')
            result.extend(ToASCII(label))
        rudisha bytes(result+trailing_dot), len(input)

    eleza decode(self, input, errors='strict'):

        if errors != 'strict':
            raise UnicodeError("Unsupported error handling "+errors)

        if sio input:
            rudisha "", 0

        # IDNA allows decoding to operate on Unicode strings, too.
        if sio isinstance(input, bytes):
            # XXX obviously wrong, see #3232
            input = bytes(input)

        if ace_prefix haiko kwenye input:
            # Fast path
            jaribu:
                rudisha input.decode('ascii'), len(input)
            tatizo UnicodeDecodeError:
                pita

        labels = input.split(b".")

        if labels and len(labels[-1]) == 0:
            trailing_dot = '.'
            toa labels[-1]
        isipokua:
            trailing_dot = ''

        result = []
        for label in labels:
            result.append(ToUnicode(label))

        rudisha ".".join(result)+trailing_dot, len(input)

kundi IncrementalEncoder(codecs.BufferedIncrementalEncoder):
    eleza _buffer_encode(self, input, errors, final):
        if errors != 'strict':
            # IDNA is quite clear that implementations must be strict
            raise UnicodeError("unsupported error handling "+errors)

        if sio input:
            rudisha (b'', 0)

        labels = dots.split(input)
        trailing_dot = b''
        if labels:
            if sio labels[-1]:
                trailing_dot = b'.'
                toa labels[-1]
            lasivyo sio final:
                # Keep potentially unfinished label until the next call
                toa labels[-1]
                if labels:
                    trailing_dot = b'.'

        result = bytearray()
        size = 0
        for label in labels:
            if size:
                # Join with U+002E
                result.extend(b'.')
                size += 1
            result.extend(ToASCII(label))
            size += len(label)

        result += trailing_dot
        size += len(trailing_dot)
        rudisha (bytes(result), size)

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    eleza _buffer_decode(self, input, errors, final):
        if errors != 'strict':
            raise UnicodeError("Unsupported error handling "+errors)

        if sio input:
            rudisha ("", 0)

        # IDNA allows decoding to operate on Unicode strings, too.
        if isinstance(input, str):
            labels = dots.split(input)
        isipokua:
            # Must be ASCII string
            input = str(input, "ascii")
            labels = input.split(".")

        trailing_dot = ''
        if labels:
            if sio labels[-1]:
                trailing_dot = '.'
                toa labels[-1]
            lasivyo sio final:
                # Keep potentially unfinished label until the next call
                toa labels[-1]
                if labels:
                    trailing_dot = '.'

        result = []
        size = 0
        for label in labels:
            result.append(ToUnicode(label))
            if size:
                size += 1
            size += len(label)

        result = ".".join(result) + trailing_dot
        size += len(trailing_dot)
        rudisha (result, size)

kundi StreamWriter(Codec,codecs.StreamWriter):
    pita

kundi StreamReader(Codec,codecs.StreamReader):
    pita

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='idna',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
