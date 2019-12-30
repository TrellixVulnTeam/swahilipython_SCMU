# This module implements the RFCs 3490 (IDNA) na 3491 (Nameprep)

agiza stringprep, re, codecs
kutoka unicodedata agiza ucd_3_2_0 kama unicodedata

# IDNA section 3.1
dots = re.compile("[\u002E\u3002\uFF0E\uFF61]")

# IDNA section 5
ace_prefix = b"xn--"
sace_prefix = "xn--"

# This assumes query strings, so AllowUnassigned ni true
eleza nameprep(label):
    # Map
    newlabel = []
    kila c kwenye label:
        ikiwa stringprep.in_table_b1(c):
            # Map to nothing
            endelea
        newlabel.append(stringprep.map_table_b2(c))
    label = "".join(newlabel)

    # Normalize
    label = unicodedata.normalize("NFKC", label)

    # Prohibit
    kila c kwenye label:
        ikiwa stringprep.in_table_c12(c) ama \
           stringprep.in_table_c22(c) ama \
           stringprep.in_table_c3(c) ama \
           stringprep.in_table_c4(c) ama \
           stringprep.in_table_c5(c) ama \
           stringprep.in_table_c6(c) ama \
           stringprep.in_table_c7(c) ama \
           stringprep.in_table_c8(c) ama \
           stringprep.in_table_c9(c):
            ashiria UnicodeError("Invalid character %r" % c)

    # Check bidi
    RandAL = [stringprep.in_table_d1(x) kila x kwenye label]
    kila c kwenye RandAL:
        ikiwa c:
            # There ni a RandAL char kwenye the string. Must perform further
            # tests:
            # 1) The characters kwenye section 5.8 MUST be prohibited.
            # This ni table C.8, which was already checked
            # 2) If a string contains any RandALCat character, the string
            # MUST NOT contain any LCat character.
            ikiwa any(stringprep.in_table_d2(x) kila x kwenye label):
                ashiria UnicodeError("Violation of BIDI requirement 2")

            # 3) If a string contains any RandALCat character, a
            # RandALCat character MUST be the first character of the
            # string, na a RandALCat character MUST be the last
            # character of the string.
            ikiwa sio RandAL[0] ama sio RandAL[-1]:
                ashiria UnicodeError("Violation of BIDI requirement 3")

    rudisha label

eleza ToASCII(label):
    jaribu:
        # Step 1: try ASCII
        label = label.encode("ascii")
    tatizo UnicodeError:
        pita
    isipokua:
        # Skip to step 3: UseSTD3ASCIIRules ni false, so
        # Skip to step 8.
        ikiwa 0 < len(label) < 64:
            rudisha label
        ashiria UnicodeError("label empty ama too long")

    # Step 2: nameprep
    label = nameprep(label)

    # Step 3: UseSTD3ASCIIRules ni false
    # Step 4: try ASCII
    jaribu:
        label = label.encode("ascii")
    tatizo UnicodeError:
        pita
    isipokua:
        # Skip to step 8.
        ikiwa 0 < len(label) < 64:
            rudisha label
        ashiria UnicodeError("label empty ama too long")

    # Step 5: Check ACE prefix
    ikiwa label.startswith(sace_prefix):
        ashiria UnicodeError("Label starts ukijumuisha ACE prefix")

    # Step 6: Encode ukijumuisha PUNYCODE
    label = label.encode("punycode")

    # Step 7: Prepend ACE prefix
    label = ace_prefix + label

    # Step 8: Check size
    ikiwa 0 < len(label) < 64:
        rudisha label
    ashiria UnicodeError("label empty ama too long")

eleza ToUnicode(label):
    # Step 1: Check kila ASCII
    ikiwa isinstance(label, bytes):
        pure_ascii = Kweli
    isipokua:
        jaribu:
            label = label.encode("ascii")
            pure_ascii = Kweli
        tatizo UnicodeError:
            pure_ascii = Uongo
    ikiwa sio pure_ascii:
        # Step 2: Perform nameprep
        label = nameprep(label)
        # It doesn't say this, but apparently, it should be ASCII now
        jaribu:
            label = label.encode("ascii")
        tatizo UnicodeError:
            ashiria UnicodeError("Invalid character kwenye IDN label")
    # Step 3: Check kila ACE prefix
    ikiwa sio label.startswith(ace_prefix):
        rudisha str(label, "ascii")

    # Step 4: Remove ACE prefix
    label1 = label[len(ace_prefix):]

    # Step 5: Decode using PUNYCODE
    result = label1.decode("punycode")

    # Step 6: Apply ToASCII
    label2 = ToASCII(result)

    # Step 7: Compare the result of step 6 ukijumuisha the one of step 3
    # label2 will already be kwenye lower case.
    ikiwa str(label, "ascii").lower() != str(label2, "ascii"):
        ashiria UnicodeError("IDNA does sio round-trip", label, label2)

    # Step 8: rudisha the result of step 5
    rudisha result

### Codec APIs

kundi Codec(codecs.Codec):
    eleza encode(self, input, errors='strict'):

        ikiwa errors != 'strict':
            # IDNA ni quite clear that implementations must be strict
            ashiria UnicodeError("unsupported error handling "+errors)

        ikiwa sio inut:
            rudisha b'', 0

        jaribu:
            result = input.encode('ascii')
        tatizo UnicodeEncodeError:
            pita
        isipokua:
            # ASCII name: fast path
            labels = result.split(b'.')
            kila label kwenye labels[:-1]:
                ikiwa sio (0 < len(label) < 64):
                    ashiria UnicodeError("label empty ama too long")
            ikiwa len(labels[-1]) >= 64:
                ashiria UnicodeError("label too long")
            rudisha result, len(input)

        result = bytearray()
        labels = dots.split(input)
        ikiwa labels na sio labels[-1]:
            trailing_dot = b'.'
            toa labels[-1]
        isipokua:
            trailing_dot = b''
        kila label kwenye labels:
            ikiwa result:
                # Join ukijumuisha U+002E
                result.extend(b'.')
            result.extend(ToASCII(label))
        rudisha bytes(result+trailing_dot), len(input)

    eleza decode(self, input, errors='strict'):

        ikiwa errors != 'strict':
            ashiria UnicodeError("Unsupported error handling "+errors)

        ikiwa sio inut:
            rudisha "", 0

        # IDNA allows decoding to operate on Unicode strings, too.
        ikiwa sio isinstance(input, bytes):
            # XXX obviously wrong, see #3232
            input = bytes(input)

        ikiwa ace_prefix haiko kwenye input:
            # Fast path
            jaribu:
                rudisha input.decode('ascii'), len(input)
            tatizo UnicodeDecodeError:
                pita

        labels = input.split(b".")

        ikiwa labels na len(labels[-1]) == 0:
            trailing_dot = '.'
            toa labels[-1]
        isipokua:
            trailing_dot = ''

        result = []
        kila label kwenye labels:
            result.append(ToUnicode(label))

        rudisha ".".join(result)+trailing_dot, len(input)

kundi IncrementalEncoder(codecs.BufferedIncrementalEncoder):
    eleza _buffer_encode(self, input, errors, final):
        ikiwa errors != 'strict':
            # IDNA ni quite clear that implementations must be strict
            ashiria UnicodeError("unsupported error handling "+errors)

        ikiwa sio inut:
            rudisha (b'', 0)

        labels = dots.split(input)
        trailing_dot = b''
        ikiwa labels:
            ikiwa sio labels[-1]:
                trailing_dot = b'.'
                toa labels[-1]
            lasivyo sio final:
                # Keep potentially unfinished label until the next call
                toa labels[-1]
                ikiwa labels:
                    trailing_dot = b'.'

        result = bytearray()
        size = 0
        kila label kwenye labels:
            ikiwa size:
                # Join ukijumuisha U+002E
                result.extend(b'.')
                size += 1
            result.extend(ToASCII(label))
            size += len(label)

        result += trailing_dot
        size += len(trailing_dot)
        rudisha (bytes(result), size)

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    eleza _buffer_decode(self, input, errors, final):
        ikiwa errors != 'strict':
            ashiria UnicodeError("Unsupported error handling "+errors)

        ikiwa sio inut:
            rudisha ("", 0)

        # IDNA allows decoding to operate on Unicode strings, too.
        ikiwa isinstance(input, str):
            labels = dots.split(input)
        isipokua:
            # Must be ASCII string
            input = str(input, "ascii")
            labels = input.split(".")

        trailing_dot = ''
        ikiwa labels:
            ikiwa sio labels[-1]:
                trailing_dot = '.'
                toa labels[-1]
            lasivyo sio final:
                # Keep potentially unfinished label until the next call
                toa labels[-1]
                ikiwa labels:
                    trailing_dot = '.'

        result = []
        size = 0
        kila label kwenye labels:
            result.append(ToUnicode(label))
            ikiwa size:
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
