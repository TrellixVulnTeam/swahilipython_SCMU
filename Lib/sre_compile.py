#
# Secret Labs' Regular Expression Engine
#
# convert template to internal format
#
# Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file kila information on usage na redistribution.
#

"""Internal support module kila sre"""

agiza _sre
agiza sre_parse
kutoka sre_constants agiza *

assert _sre.MAGIC == MAGIC, "SRE module mismatch"

_LITERAL_CODES = {LITERAL, NOT_LITERAL}
_REPEATING_CODES = {REPEAT, MIN_REPEAT, MAX_REPEAT}
_SUCCESS_CODES = {SUCCESS, FAILURE}
_ASSERT_CODES = {ASSERT, ASSERT_NOT}
_UNIT_CODES = _LITERAL_CODES | {ANY, IN}

# Sets of lowercase characters which have the same uppercase.
_equivalences = (
    # LATIN SMALL LETTER I, LATIN SMALL LETTER DOTLESS I
    (0x69, 0x131), # iı
    # LATIN SMALL LETTER S, LATIN SMALL LETTER LONG S
    (0x73, 0x17f), # sſ
    # MICRO SIGN, GREEK SMALL LETTER MU
    (0xb5, 0x3bc), # µμ
    # COMBINING GREEK YPOGEGRAMMENI, GREEK SMALL LETTER IOTA, GREEK PROSGEGRAMMENI
    (0x345, 0x3b9, 0x1fbe), # \u0345ιι
    # GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS, GREEK SMALL LETTER IOTA WITH DIALYTIKA AND OXIA
    (0x390, 0x1fd3), # ΐΐ
    # GREEK SMALL LETTER UPSILON WITH DIALYTIKA AND TONOS, GREEK SMALL LETTER UPSILON WITH DIALYTIKA AND OXIA
    (0x3b0, 0x1fe3), # ΰΰ
    # GREEK SMALL LETTER BETA, GREEK BETA SYMBOL
    (0x3b2, 0x3d0), # βϐ
    # GREEK SMALL LETTER EPSILON, GREEK LUNATE EPSILON SYMBOL
    (0x3b5, 0x3f5), # εϵ
    # GREEK SMALL LETTER THETA, GREEK THETA SYMBOL
    (0x3b8, 0x3d1), # θϑ
    # GREEK SMALL LETTER KAPPA, GREEK KAPPA SYMBOL
    (0x3ba, 0x3f0), # κϰ
    # GREEK SMALL LETTER PI, GREEK PI SYMBOL
    (0x3c0, 0x3d6), # πϖ
    # GREEK SMALL LETTER RHO, GREEK RHO SYMBOL
    (0x3c1, 0x3f1), # ρϱ
    # GREEK SMALL LETTER FINAL SIGMA, GREEK SMALL LETTER SIGMA
    (0x3c2, 0x3c3), # ςσ
    # GREEK SMALL LETTER PHI, GREEK PHI SYMBOL
    (0x3c6, 0x3d5), # φϕ
    # LATIN SMALL LETTER S WITH DOT ABOVE, LATIN SMALL LETTER LONG S WITH DOT ABOVE
    (0x1e61, 0x1e9b), # ṡẛ
    # LATIN SMALL LIGATURE LONG S T, LATIN SMALL LIGATURE ST
    (0xfb05, 0xfb06), # ﬅﬆ
)

# Maps the lowercase code to lowercase codes which have the same uppercase.
_ignorecase_fixes = {i: tuple(j kila j kwenye t ikiwa i != j)
                     kila t kwenye _equivalences kila i kwenye t}

eleza _combine_flags(flags, add_flags, del_flags,
                   TYPE_FLAGS=sre_parse.TYPE_FLAGS):
    ikiwa add_flags & TYPE_FLAGS:
        flags &= ~TYPE_FLAGS
    rudisha (flags | add_flags) & ~del_flags

eleza _compile(code, pattern, flags):
    # internal: compile a (sub)pattern
    emit = code.append
    _len = len
    LITERAL_CODES = _LITERAL_CODES
    REPEATING_CODES = _REPEATING_CODES
    SUCCESS_CODES = _SUCCESS_CODES
    ASSERT_CODES = _ASSERT_CODES
    iscased = Tupu
    tolower = Tupu
    fixes = Tupu
    ikiwa flags & SRE_FLAG_IGNORECASE na sio flags & SRE_FLAG_LOCALE:
        ikiwa flags & SRE_FLAG_UNICODE:
            iscased = _sre.unicode_iscased
            tolower = _sre.unicode_tolower
            fixes = _ignorecase_fixes
        isipokua:
            iscased = _sre.ascii_iscased
            tolower = _sre.ascii_tolower
    kila op, av kwenye pattern:
        ikiwa op kwenye LITERAL_CODES:
            ikiwa sio flags & SRE_FLAG_IGNORECASE:
                emit(op)
                emit(av)
            lasivyo flags & SRE_FLAG_LOCALE:
                emit(OP_LOCALE_IGNORE[op])
                emit(av)
            lasivyo sio iscased(av):
                emit(op)
                emit(av)
            isipokua:
                lo = tolower(av)
                ikiwa sio fixes:  # ascii
                    emit(OP_IGNORE[op])
                    emit(lo)
                lasivyo lo haiko kwenye fixes:
                    emit(OP_UNICODE_IGNORE[op])
                    emit(lo)
                isipokua:
                    emit(IN_UNI_IGNORE)
                    skip = _len(code); emit(0)
                    ikiwa op ni NOT_LITERAL:
                        emit(NEGATE)
                    kila k kwenye (lo,) + fixes[lo]:
                        emit(LITERAL)
                        emit(k)
                    emit(FAILURE)
                    code[skip] = _len(code) - skip
        lasivyo op ni IN:
            charset, hascased = _optimize_charset(av, iscased, tolower, fixes)
            ikiwa flags & SRE_FLAG_IGNORECASE na flags & SRE_FLAG_LOCALE:
                emit(IN_LOC_IGNORE)
            lasivyo sio hascased:
                emit(IN)
            lasivyo sio fixes:  # ascii
                emit(IN_IGNORE)
            isipokua:
                emit(IN_UNI_IGNORE)
            skip = _len(code); emit(0)
            _compile_charset(charset, flags, code)
            code[skip] = _len(code) - skip
        lasivyo op ni ANY:
            ikiwa flags & SRE_FLAG_DOTALL:
                emit(ANY_ALL)
            isipokua:
                emit(ANY)
        lasivyo op kwenye REPEATING_CODES:
            ikiwa flags & SRE_FLAG_TEMPLATE:
                ashiria error("internal: unsupported template operator %r" % (op,))
            ikiwa _simple(av[2]):
                ikiwa op ni MAX_REPEAT:
                    emit(REPEAT_ONE)
                isipokua:
                    emit(MIN_REPEAT_ONE)
                skip = _len(code); emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                emit(SUCCESS)
                code[skip] = _len(code) - skip
            isipokua:
                emit(REPEAT)
                skip = _len(code); emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                code[skip] = _len(code) - skip
                ikiwa op ni MAX_REPEAT:
                    emit(MAX_UNTIL)
                isipokua:
                    emit(MIN_UNTIL)
        lasivyo op ni SUBPATTERN:
            group, add_flags, del_flags, p = av
            ikiwa group:
                emit(MARK)
                emit((group-1)*2)
            # _compile_info(code, p, _combine_flags(flags, add_flags, del_flags))
            _compile(code, p, _combine_flags(flags, add_flags, del_flags))
            ikiwa group:
                emit(MARK)
                emit((group-1)*2+1)
        lasivyo op kwenye SUCCESS_CODES:
            emit(op)
        lasivyo op kwenye ASSERT_CODES:
            emit(op)
            skip = _len(code); emit(0)
            ikiwa av[0] >= 0:
                emit(0) # look ahead
            isipokua:
                lo, hi = av[1].getwidth()
                ikiwa lo != hi:
                    ashiria error("look-behind requires fixed-width pattern")
                emit(lo) # look behind
            _compile(code, av[1], flags)
            emit(SUCCESS)
            code[skip] = _len(code) - skip
        lasivyo op ni CALL:
            emit(op)
            skip = _len(code); emit(0)
            _compile(code, av, flags)
            emit(SUCCESS)
            code[skip] = _len(code) - skip
        lasivyo op ni AT:
            emit(op)
            ikiwa flags & SRE_FLAG_MULTILINE:
                av = AT_MULTILINE.get(av, av)
            ikiwa flags & SRE_FLAG_LOCALE:
                av = AT_LOCALE.get(av, av)
            lasivyo flags & SRE_FLAG_UNICODE:
                av = AT_UNICODE.get(av, av)
            emit(av)
        lasivyo op ni BRANCH:
            emit(op)
            tail = []
            tailappend = tail.append
            kila av kwenye av[1]:
                skip = _len(code); emit(0)
                # _compile_info(code, av, flags)
                _compile(code, av, flags)
                emit(JUMP)
                tailappend(_len(code)); emit(0)
                code[skip] = _len(code) - skip
            emit(FAILURE) # end of branch
            kila tail kwenye tail:
                code[tail] = _len(code) - tail
        lasivyo op ni CATEGORY:
            emit(op)
            ikiwa flags & SRE_FLAG_LOCALE:
                av = CH_LOCALE[av]
            lasivyo flags & SRE_FLAG_UNICODE:
                av = CH_UNICODE[av]
            emit(av)
        lasivyo op ni GROUPREF:
            ikiwa sio flags & SRE_FLAG_IGNORECASE:
                emit(op)
            lasivyo flags & SRE_FLAG_LOCALE:
                emit(GROUPREF_LOC_IGNORE)
            lasivyo sio fixes:  # ascii
                emit(GROUPREF_IGNORE)
            isipokua:
                emit(GROUPREF_UNI_IGNORE)
            emit(av-1)
        lasivyo op ni GROUPREF_EXISTS:
            emit(op)
            emit(av[0]-1)
            skipyes = _len(code); emit(0)
            _compile(code, av[1], flags)
            ikiwa av[2]:
                emit(JUMP)
                skipno = _len(code); emit(0)
                code[skipyes] = _len(code) - skipyes + 1
                _compile(code, av[2], flags)
                code[skipno] = _len(code) - skipno
            isipokua:
                code[skipyes] = _len(code) - skipyes + 1
        isipokua:
            ashiria error("internal: unsupported operand type %r" % (op,))

eleza _compile_charset(charset, flags, code):
    # compile charset subprogram
    emit = code.append
    kila op, av kwenye charset:
        emit(op)
        ikiwa op ni NEGATE:
            pita
        lasivyo op ni LITERAL:
            emit(av)
        lasivyo op ni RANGE ama op ni RANGE_UNI_IGNORE:
            emit(av[0])
            emit(av[1])
        lasivyo op ni CHARSET:
            code.extend(av)
        lasivyo op ni BIGCHARSET:
            code.extend(av)
        lasivyo op ni CATEGORY:
            ikiwa flags & SRE_FLAG_LOCALE:
                emit(CH_LOCALE[av])
            lasivyo flags & SRE_FLAG_UNICODE:
                emit(CH_UNICODE[av])
            isipokua:
                emit(av)
        isipokua:
            ashiria error("internal: unsupported set operator %r" % (op,))
    emit(FAILURE)

eleza _optimize_charset(charset, iscased=Tupu, fixup=Tupu, fixes=Tupu):
    # internal: optimize character set
    out = []
    tail = []
    charmap = bytearray(256)
    hascased = Uongo
    kila op, av kwenye charset:
        wakati Kweli:
            jaribu:
                ikiwa op ni LITERAL:
                    ikiwa fixup:
                        lo = fixup(av)
                        charmap[lo] = 1
                        ikiwa fixes na lo kwenye fixes:
                            kila k kwenye fixes[lo]:
                                charmap[k] = 1
                        ikiwa sio hascased na iscased(av):
                            hascased = Kweli
                    isipokua:
                        charmap[av] = 1
                lasivyo op ni RANGE:
                    r = range(av[0], av[1]+1)
                    ikiwa fixup:
                        ikiwa fixes:
                            kila i kwenye map(fixup, r):
                                charmap[i] = 1
                                ikiwa i kwenye fixes:
                                    kila k kwenye fixes[i]:
                                        charmap[k] = 1
                        isipokua:
                            kila i kwenye map(fixup, r):
                                charmap[i] = 1
                        ikiwa sio hascased:
                            hascased = any(map(iscased, r))
                    isipokua:
                        kila i kwenye r:
                            charmap[i] = 1
                lasivyo op ni NEGATE:
                    out.append((op, av))
                isipokua:
                    tail.append((op, av))
            tatizo IndexError:
                ikiwa len(charmap) == 256:
                    # character set contains non-UCS1 character codes
                    charmap += b'\0' * 0xff00
                    endelea
                # Character set contains non-BMP character codes.
                ikiwa fixup:
                    hascased = Kweli
                    # There are only two ranges of cased non-BMP characters:
                    # 10400-1044F (Deseret) na 118A0-118DF (Warang Citi),
                    # na kila both ranges RANGE_UNI_IGNORE works.
                    ikiwa op ni RANGE:
                        op = RANGE_UNI_IGNORE
                tail.append((op, av))
            koma

    # compress character map
    runs = []
    q = 0
    wakati Kweli:
        p = charmap.find(1, q)
        ikiwa p < 0:
            koma
        ikiwa len(runs) >= 2:
            runs = Tupu
            koma
        q = charmap.find(0, p)
        ikiwa q < 0:
            runs.append((p, len(charmap)))
            koma
        runs.append((p, q))
    ikiwa runs ni sio Tupu:
        # use literal/range
        kila p, q kwenye runs:
            ikiwa q - p == 1:
                out.append((LITERAL, p))
            isipokua:
                out.append((RANGE, (p, q - 1)))
        out += tail
        # ikiwa the case was changed ama new representation ni more compact
        ikiwa hascased ama len(out) < len(charset):
            rudisha out, hascased
        # isipokua original character set ni good enough
        rudisha charset, hascased

    # use bitmap
    ikiwa len(charmap) == 256:
        data = _mk_bitmap(charmap)
        out.append((CHARSET, data))
        out += tail
        rudisha out, hascased

    # To represent a big charset, first a bitmap of all characters kwenye the
    # set ni constructed. Then, this bitmap ni sliced into chunks of 256
    # characters, duplicate chunks are eliminated, na each chunk is
    # given a number. In the compiled expression, the charset is
    # represented by a 32-bit word sequence, consisting of one word for
    # the number of different chunks, a sequence of 256 bytes (64 words)
    # of chunk numbers indexed by their original chunk position, na a
    # sequence of 256-bit chunks (8 words each).

    # Compression ni normally good: kwenye a typical charset, large ranges of
    # Unicode will be either completely excluded (e.g. ikiwa only cyrillic
    # letters are to be matched), ama completely included (e.g. ikiwa large
    # subranges of Kanji match). These ranges will be represented by
    # chunks of all one-bits ama all zero-bits.

    # Matching can be also done efficiently: the more significant byte of
    # the Unicode character ni an index into the chunk number, na the
    # less significant byte ni a bit index kwenye the chunk (just like the
    # CHARSET matching).

    charmap = bytes(charmap) # should be hashable
    comps = {}
    mapping = bytearray(256)
    block = 0
    data = bytearray()
    kila i kwenye range(0, 65536, 256):
        chunk = charmap[i: i + 256]
        ikiwa chunk kwenye comps:
            mapping[i // 256] = comps[chunk]
        isipokua:
            mapping[i // 256] = comps[chunk] = block
            block += 1
            data += chunk
    data = _mk_bitmap(data)
    data[0:0] = [block] + _bytes_to_codes(mapping)
    out.append((BIGCHARSET, data))
    out += tail
    rudisha out, hascased

_CODEBITS = _sre.CODESIZE * 8
MAXCODE = (1 << _CODEBITS) - 1
_BITS_TRANS = b'0' + b'1' * 255
eleza _mk_bitmap(bits, _CODEBITS=_CODEBITS, _int=int):
    s = bits.translate(_BITS_TRANS)[::-1]
    rudisha [_int(s[i - _CODEBITS: i], 2)
            kila i kwenye range(len(s), 0, -_CODEBITS)]

eleza _bytes_to_codes(b):
    # Convert block indices to word array
    a = memoryview(b).cast('I')
    assert a.itemsize == _sre.CODESIZE
    assert len(a) * a.itemsize == len(b)
    rudisha a.tolist()

eleza _simple(p):
    # check ikiwa this subpattern ni a "simple" operator
    ikiwa len(p) != 1:
        rudisha Uongo
    op, av = p[0]
    ikiwa op ni SUBPATTERN:
        rudisha av[0] ni Tupu na _simple(av[-1])
    rudisha op kwenye _UNIT_CODES

eleza _generate_overlap_table(prefix):
    """
    Generate an overlap table kila the following prefix.
    An overlap table ni a table of the same size kama the prefix which
    informs about the potential self-overlap kila each index kwenye the prefix:
    - ikiwa overlap[i] == 0, prefix[i:] can't overlap prefix[0:...]
    - ikiwa overlap[i] == k ukijumuisha 0 < k <= i, prefix[i-k+1:i+1] overlaps with
      prefix[0:k]
    """
    table = [0] * len(prefix)
    kila i kwenye range(1, len(prefix)):
        idx = table[i - 1]
        wakati prefix[i] != prefix[idx]:
            ikiwa idx == 0:
                table[i] = 0
                koma
            idx = table[idx - 1]
        isipokua:
            table[i] = idx + 1
    rudisha table

eleza _get_iscased(flags):
    ikiwa sio flags & SRE_FLAG_IGNORECASE:
        rudisha Tupu
    lasivyo flags & SRE_FLAG_UNICODE:
        rudisha _sre.unicode_iscased
    isipokua:
        rudisha _sre.ascii_iscased

eleza _get_literal_prefix(pattern, flags):
    # look kila literal prefix
    prefix = []
    prefixappend = prefix.append
    prefix_skip = Tupu
    iscased = _get_iscased(flags)
    kila op, av kwenye pattern.data:
        ikiwa op ni LITERAL:
            ikiwa iscased na iscased(av):
                koma
            prefixappend(av)
        lasivyo op ni SUBPATTERN:
            group, add_flags, del_flags, p = av
            flags1 = _combine_flags(flags, add_flags, del_flags)
            ikiwa flags1 & SRE_FLAG_IGNORECASE na flags1 & SRE_FLAG_LOCALE:
                koma
            prefix1, prefix_skip1, got_all = _get_literal_prefix(p, flags1)
            ikiwa prefix_skip ni Tupu:
                ikiwa group ni sio Tupu:
                    prefix_skip = len(prefix)
                lasivyo prefix_skip1 ni sio Tupu:
                    prefix_skip = len(prefix) + prefix_skip1
            prefix.extend(prefix1)
            ikiwa sio got_all:
                koma
        isipokua:
            koma
    isipokua:
        rudisha prefix, prefix_skip, Kweli
    rudisha prefix, prefix_skip, Uongo

eleza _get_charset_prefix(pattern, flags):
    wakati Kweli:
        ikiwa sio pattern.data:
            rudisha Tupu
        op, av = pattern.data[0]
        ikiwa op ni sio SUBPATTERN:
            koma
        group, add_flags, del_flags, pattern = av
        flags = _combine_flags(flags, add_flags, del_flags)
        ikiwa flags & SRE_FLAG_IGNORECASE na flags & SRE_FLAG_LOCALE:
            rudisha Tupu

    iscased = _get_iscased(flags)
    ikiwa op ni LITERAL:
        ikiwa iscased na iscased(av):
            rudisha Tupu
        rudisha [(op, av)]
    lasivyo op ni BRANCH:
        charset = []
        charsetappend = charset.append
        kila p kwenye av[1]:
            ikiwa sio p:
                rudisha Tupu
            op, av = p[0]
            ikiwa op ni LITERAL na sio (iscased na iscased(av)):
                charsetappend((op, av))
            isipokua:
                rudisha Tupu
        rudisha charset
    lasivyo op ni IN:
        charset = av
        ikiwa iscased:
            kila op, av kwenye charset:
                ikiwa op ni LITERAL:
                    ikiwa iscased(av):
                        rudisha Tupu
                lasivyo op ni RANGE:
                    ikiwa av[1] > 0xffff:
                        rudisha Tupu
                    ikiwa any(map(iscased, range(av[0], av[1]+1))):
                        rudisha Tupu
        rudisha charset
    rudisha Tupu

eleza _compile_info(code, pattern, flags):
    # internal: compile an info block.  kwenye the current version,
    # this contains min/max pattern width, na an optional literal
    # prefix ama a character map
    lo, hi = pattern.getwidth()
    ikiwa hi > MAXCODE:
        hi = MAXCODE
    ikiwa lo == 0:
        code.extend([INFO, 4, 0, lo, hi])
        rudisha
    # look kila a literal prefix
    prefix = []
    prefix_skip = 0
    charset = [] # sio used
    ikiwa sio (flags & SRE_FLAG_IGNORECASE na flags & SRE_FLAG_LOCALE):
        # look kila literal prefix
        prefix, prefix_skip, got_all = _get_literal_prefix(pattern, flags)
        # ikiwa no prefix, look kila charset prefix
        ikiwa sio prefix:
            charset = _get_charset_prefix(pattern, flags)
##     ikiwa prefix:
##         andika("*** PREFIX", prefix, prefix_skip)
##     ikiwa charset:
##         andika("*** CHARSET", charset)
    # add an info block
    emit = code.append
    emit(INFO)
    skip = len(code); emit(0)
    # literal flag
    mask = 0
    ikiwa prefix:
        mask = SRE_INFO_PREFIX
        ikiwa prefix_skip ni Tupu na got_all:
            mask = mask | SRE_INFO_LITERAL
    lasivyo charset:
        mask = mask | SRE_INFO_CHARSET
    emit(mask)
    # pattern length
    ikiwa lo < MAXCODE:
        emit(lo)
    isipokua:
        emit(MAXCODE)
        prefix = prefix[:MAXCODE]
    emit(min(hi, MAXCODE))
    # add literal prefix
    ikiwa prefix:
        emit(len(prefix)) # length
        ikiwa prefix_skip ni Tupu:
            prefix_skip =  len(prefix)
        emit(prefix_skip) # skip
        code.extend(prefix)
        # generate overlap table
        code.extend(_generate_overlap_table(prefix))
    lasivyo charset:
        charset, hascased = _optimize_charset(charset)
        assert sio hascased
        _compile_charset(charset, flags, code)
    code[skip] = len(code) - skip

eleza isstring(obj):
    rudisha isinstance(obj, (str, bytes))

eleza _code(p, flags):

    flags = p.state.flags | flags
    code = []

    # compile info block
    _compile_info(code, p, flags)

    # compile the pattern
    _compile(code, p.data, flags)

    code.append(SUCCESS)

    rudisha code

eleza _hex_code(code):
    rudisha '[%s]' % ', '.join('%#0*x' % (_sre.CODESIZE*2+2, x) kila x kwenye code)

eleza dis(code):
    agiza sys

    labels = set()
    level = 0
    offset_width = len(str(len(code) - 1))

    eleza dis_(start, end):
        eleza print_(*args, to=Tupu):
            ikiwa to ni sio Tupu:
                labels.add(to)
                args += ('(to %d)' % (to,),)
            andika('%*d%s ' % (offset_width, start, ':' ikiwa start kwenye labels isipokua '.'),
                  end='  '*(level-1))
            andika(*args)

        eleza print_2(*args):
            andika(end=' '*(offset_width + 2*level))
            andika(*args)

        nonlocal level
        level += 1
        i = start
        wakati i < end:
            start = i
            op = code[i]
            i += 1
            op = OPCODES[op]
            ikiwa op kwenye (SUCCESS, FAILURE, ANY, ANY_ALL,
                      MAX_UNTIL, MIN_UNTIL, NEGATE):
                print_(op)
            lasivyo op kwenye (LITERAL, NOT_LITERAL,
                        LITERAL_IGNORE, NOT_LITERAL_IGNORE,
                        LITERAL_UNI_IGNORE, NOT_LITERAL_UNI_IGNORE,
                        LITERAL_LOC_IGNORE, NOT_LITERAL_LOC_IGNORE):
                arg = code[i]
                i += 1
                print_(op, '%#02x (%r)' % (arg, chr(arg)))
            lasivyo op ni AT:
                arg = code[i]
                i += 1
                arg = str(ATCODES[arg])
                assert arg[:3] == 'AT_'
                print_(op, arg[3:])
            lasivyo op ni CATEGORY:
                arg = code[i]
                i += 1
                arg = str(CHCODES[arg])
                assert arg[:9] == 'CATEGORY_'
                print_(op, arg[9:])
            lasivyo op kwenye (IN, IN_IGNORE, IN_UNI_IGNORE, IN_LOC_IGNORE):
                skip = code[i]
                print_(op, skip, to=i+skip)
                dis_(i+1, i+skip)
                i += skip
            lasivyo op kwenye (RANGE, RANGE_UNI_IGNORE):
                lo, hi = code[i: i+2]
                i += 2
                print_(op, '%#02x %#02x (%r-%r)' % (lo, hi, chr(lo), chr(hi)))
            lasivyo op ni CHARSET:
                print_(op, _hex_code(code[i: i + 256//_CODEBITS]))
                i += 256//_CODEBITS
            lasivyo op ni BIGCHARSET:
                arg = code[i]
                i += 1
                mapping = list(b''.join(x.to_bytes(_sre.CODESIZE, sys.byteorder)
                                        kila x kwenye code[i: i + 256//_sre.CODESIZE]))
                print_(op, arg, mapping)
                i += 256//_sre.CODESIZE
                level += 1
                kila j kwenye range(arg):
                    print_2(_hex_code(code[i: i + 256//_CODEBITS]))
                    i += 256//_CODEBITS
                level -= 1
            lasivyo op kwenye (MARK, GROUPREF, GROUPREF_IGNORE, GROUPREF_UNI_IGNORE,
                        GROUPREF_LOC_IGNORE):
                arg = code[i]
                i += 1
                print_(op, arg)
            lasivyo op ni JUMP:
                skip = code[i]
                print_(op, skip, to=i+skip)
                i += 1
            lasivyo op ni BRANCH:
                skip = code[i]
                print_(op, skip, to=i+skip)
                wakati skip:
                    dis_(i+1, i+skip)
                    i += skip
                    start = i
                    skip = code[i]
                    ikiwa skip:
                        print_('branch', skip, to=i+skip)
                    isipokua:
                        print_(FAILURE)
                i += 1
            lasivyo op kwenye (REPEAT, REPEAT_ONE, MIN_REPEAT_ONE):
                skip, min, max = code[i: i+3]
                ikiwa max == MAXREPEAT:
                    max = 'MAXREPEAT'
                print_(op, skip, min, max, to=i+skip)
                dis_(i+3, i+skip)
                i += skip
            lasivyo op ni GROUPREF_EXISTS:
                arg, skip = code[i: i+2]
                print_(op, arg, skip, to=i+skip)
                i += 2
            lasivyo op kwenye (ASSERT, ASSERT_NOT):
                skip, arg = code[i: i+2]
                print_(op, skip, arg, to=i+skip)
                dis_(i+2, i+skip)
                i += skip
            lasivyo op ni INFO:
                skip, flags, min, max = code[i: i+4]
                ikiwa max == MAXREPEAT:
                    max = 'MAXREPEAT'
                print_(op, skip, bin(flags), min, max, to=i+skip)
                start = i+4
                ikiwa flags & SRE_INFO_PREFIX:
                    prefix_len, prefix_skip = code[i+4: i+6]
                    print_2('  prefix_skip', prefix_skip)
                    start = i + 6
                    prefix = code[start: start+prefix_len]
                    print_2('  prefix',
                            '[%s]' % ', '.join('%#02x' % x kila x kwenye prefix),
                            '(%r)' % ''.join(map(chr, prefix)))
                    start += prefix_len
                    print_2('  overlap', code[start: start+prefix_len])
                    start += prefix_len
                ikiwa flags & SRE_INFO_CHARSET:
                    level += 1
                    print_2('in')
                    dis_(start, i+skip)
                    level -= 1
                i += skip
            isipokua:
                ashiria ValueError(op)

        level -= 1

    dis_(0, len(code))


eleza compile(p, flags=0):
    # internal: convert pattern list to internal format

    ikiwa isstring(p):
        pattern = p
        p = sre_parse.parse(p, flags)
    isipokua:
        pattern = Tupu

    code = _code(p, flags)

    ikiwa flags & SRE_FLAG_DEBUG:
        andika()
        dis(code)

    # map kwenye either direction
    groupindex = p.state.groupdict
    indexgroup = [Tupu] * p.state.groups
    kila k, i kwenye groupindex.items():
        indexgroup[i] = k

    rudisha _sre.compile(
        pattern, flags | p.state.flags, code,
        p.state.groups-1,
        groupindex, tuple(indexgroup)
        )
