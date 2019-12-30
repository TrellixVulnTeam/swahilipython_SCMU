""" Codec for the Punicode encoding, as specified in RFC 3492

Written by Martin v. Löwis.
"""

agiza codecs

##################### Encoding #####################################

eleza segregate(str):
    """3.1 Basic code point segregation"""
    base = bytearray()
    extended = set()
    for c in str:
        if ord(c) < 128:
            base.append(ord(c))
        isipokua:
            extended.add(c)
    extended = sorted(extended)
    rudisha bytes(base), extended

eleza selective_len(str, max):
    """Return the length of str, considering only characters below max."""
    res = 0
    for c in str:
        if ord(c) < max:
            res += 1
    rudisha res

eleza selective_find(str, char, index, pos):
    """Return a pair (index, pos), indicating the next occurrence of
    char in str. index is the position of the character considering
    only ordinals up to and including char, and pos is the position in
    the full string. index/pos is the starting position in the full
    string."""

    l = len(str)
    wakati 1:
        pos += 1
        if pos == l:
            rudisha (-1, -1)
        c = str[pos]
        if c == char:
            rudisha index+1, pos
        lasivyo c < char:
            index += 1

eleza insertion_unsort(str, extended):
    """3.2 Insertion unsort coding"""
    oldchar = 0x80
    result = []
    oldindex = -1
    for c in extended:
        index = pos = -1
        char = ord(c)
        curlen = selective_len(str, char)
        delta = (curlen+1) * (char - oldchar)
        wakati 1:
            index,pos = selective_find(str,c,index,pos)
            if index == -1:
                koma
            delta += index - oldindex
            result.append(delta-1)
            oldindex = index
            delta = 0
        oldchar = char

    rudisha result

eleza T(j, bias):
    # Punycode parameters: tmin = 1, tmax = 26, base = 36
    res = 36 * (j + 1) - bias
    if res < 1: rudisha 1
    if res > 26: rudisha 26
    rudisha res

digits = b"abcdefghijklmnopqrstuvwxyz0123456789"
eleza generate_generalized_integer(N, bias):
    """3.3 Generalized variable-length integers"""
    result = bytearray()
    j = 0
    wakati 1:
        t = T(j, bias)
        if N < t:
            result.append(digits[N])
            rudisha bytes(result)
        result.append(digits[t + ((N - t) % (36 - t))])
        N = (N - t) // (36 - t)
        j += 1

eleza adapt(delta, first, numchars):
    if first:
        delta //= 700
    isipokua:
        delta //= 2
    delta += delta // numchars
    # ((base - tmin) * tmax) // 2 == 455
    divisions = 0
    wakati delta > 455:
        delta = delta // 35 # base - tmin
        divisions += 36
    bias = divisions + (36 * delta // (delta + 38))
    rudisha bias


eleza generate_integers(baselen, deltas):
    """3.4 Bias adaptation"""
    # Punycode parameters: initial bias = 72, damp = 700, skew = 38
    result = bytearray()
    bias = 72
    for points, delta in enumerate(deltas):
        s = generate_generalized_integer(delta, bias)
        result.extend(s)
        bias = adapt(delta, points==0, baselen+points+1)
    rudisha bytes(result)

eleza punycode_encode(text):
    base, extended = segregate(text)
    deltas = insertion_unsort(text, extended)
    extended = generate_integers(len(base), deltas)
    if base:
        rudisha base + b"-" + extended
    rudisha extended

##################### Decoding #####################################

eleza decode_generalized_number(extended, extpos, bias, errors):
    """3.3 Generalized variable-length integers"""
    result = 0
    w = 1
    j = 0
    wakati 1:
        jaribu:
            char = ord(extended[extpos])
        tatizo IndexError:
            if errors == "strict":
                ashiria UnicodeError("incomplete punicode string")
            rudisha extpos + 1, Tupu
        extpos += 1
        if 0x41 <= char <= 0x5A: # A-Z
            digit = char - 0x41
        lasivyo 0x30 <= char <= 0x39:
            digit = char - 22 # 0x30-26
        lasivyo errors == "strict":
            ashiria UnicodeError("Invalid extended code point '%s'"
                               % extended[extpos])
        isipokua:
            rudisha extpos, Tupu
        t = T(j, bias)
        result += digit * w
        if digit < t:
            rudisha extpos, result
        w = w * (36 - t)
        j += 1


eleza insertion_sort(base, extended, errors):
    """3.2 Insertion unsort coding"""
    char = 0x80
    pos = -1
    bias = 72
    extpos = 0
    wakati extpos < len(extended):
        newpos, delta = decode_generalized_number(extended, extpos,
                                                  bias, errors)
        if delta is Tupu:
            # There was an error in decoding. We can't endelea because
            # synchronization is lost.
            rudisha base
        pos += delta+1
        char += pos // (len(base) + 1)
        if char > 0x10FFFF:
            if errors == "strict":
                ashiria UnicodeError("Invalid character U+%x" % char)
            char = ord('?')
        pos = pos % (len(base) + 1)
        base = base[:pos] + chr(char) + base[pos:]
        bias = adapt(delta, (extpos == 0), len(base))
        extpos = newpos
    rudisha base

eleza punycode_decode(text, errors):
    if isinstance(text, str):
        text = text.encode("ascii")
    if isinstance(text, memoryview):
        text = bytes(text)
    pos = text.rfind(b"-")
    if pos == -1:
        base = ""
        extended = str(text, "ascii").upper()
    isipokua:
        base = str(text[:pos], "ascii", errors)
        extended = str(text[pos+1:], "ascii").upper()
    rudisha insertion_sort(base, extended, errors)

### Codec APIs

kundi Codec(codecs.Codec):

    eleza encode(self, input, errors='strict'):
        res = punycode_encode(input)
        rudisha res, len(input)

    eleza decode(self, input, errors='strict'):
        if errors haiko kwenye ('strict', 'replace', 'ignore'):
            ashiria UnicodeError("Unsupported error handling "+errors)
        res = punycode_decode(input, errors)
        rudisha res, len(input)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=Uongo):
        rudisha punycode_encode(input)

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=Uongo):
        if self.errors haiko kwenye ('strict', 'replace', 'ignore'):
            ashiria UnicodeError("Unsupported error handling "+self.errors)
        rudisha punycode_decode(input, self.errors)

kundi StreamWriter(Codec,codecs.StreamWriter):
    pita

kundi StreamReader(Codec,codecs.StreamReader):
    pita

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='punycode',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
