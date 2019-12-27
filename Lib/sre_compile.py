#
# Secret Labs' Regular Expression Engine
#
# convert template to internal format
#
# Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file for information on usage and redistribution.
#

"""Internal support module for sre"""

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
_ignorecase_fixes = {i: tuple(j for j in t ikiwa i != j)
                     for t in _equivalences for i in t}

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
    iscased = None
    tolower = None
    fixes = None
    ikiwa flags & SRE_FLAG_IGNORECASE and not flags & SRE_FLAG_LOCALE:
        ikiwa flags & SRE_FLAG_UNICODE:
            iscased = _sre.unicode_iscased
            tolower = _sre.unicode_tolower
            fixes = _ignorecase_fixes
        else:
            iscased = _sre.ascii_iscased
            tolower = _sre.ascii_tolower
    for op, av in pattern:
        ikiwa op in LITERAL_CODES:
            ikiwa not flags & SRE_FLAG_IGNORECASE:
                emit(op)
                emit(av)
            elikiwa flags & SRE_FLAG_LOCALE:
                emit(OP_LOCALE_IGNORE[op])
                emit(av)
            elikiwa not iscased(av):
                emit(op)
                emit(av)
            else:
                lo = tolower(av)
                ikiwa not fixes:  # ascii
                    emit(OP_IGNORE[op])
                    emit(lo)
                elikiwa lo not in fixes:
                    emit(OP_UNICODE_IGNORE[op])
                    emit(lo)
                else:
                    emit(IN_UNI_IGNORE)
                    skip = _len(code); emit(0)
                    ikiwa op is NOT_LITERAL:
                        emit(NEGATE)
                    for k in (lo,) + fixes[lo]:
                        emit(LITERAL)
                        emit(k)
                    emit(FAILURE)
                    code[skip] = _len(code) - skip
        elikiwa op is IN:
            charset, hascased = _optimize_charset(av, iscased, tolower, fixes)
            ikiwa flags & SRE_FLAG_IGNORECASE and flags & SRE_FLAG_LOCALE:
                emit(IN_LOC_IGNORE)
            elikiwa not hascased:
                emit(IN)
            elikiwa not fixes:  # ascii
                emit(IN_IGNORE)
            else:
                emit(IN_UNI_IGNORE)
            skip = _len(code); emit(0)
            _compile_charset(charset, flags, code)
            code[skip] = _len(code) - skip
        elikiwa op is ANY:
            ikiwa flags & SRE_FLAG_DOTALL:
                emit(ANY_ALL)
            else:
                emit(ANY)
        elikiwa op in REPEATING_CODES:
            ikiwa flags & SRE_FLAG_TEMPLATE:
                raise error("internal: unsupported template operator %r" % (op,))
            ikiwa _simple(av[2]):
                ikiwa op is MAX_REPEAT:
                    emit(REPEAT_ONE)
                else:
                    emit(MIN_REPEAT_ONE)
                skip = _len(code); emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                emit(SUCCESS)
                code[skip] = _len(code) - skip
            else:
                emit(REPEAT)
                skip = _len(code); emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                code[skip] = _len(code) - skip
                ikiwa op is MAX_REPEAT:
                    emit(MAX_UNTIL)
                else:
                    emit(MIN_UNTIL)
        elikiwa op is SUBPATTERN:
            group, add_flags, del_flags, p = av
            ikiwa group:
                emit(MARK)
                emit((group-1)*2)
            # _compile_info(code, p, _combine_flags(flags, add_flags, del_flags))
            _compile(code, p, _combine_flags(flags, add_flags, del_flags))
            ikiwa group:
                emit(MARK)
                emit((group-1)*2+1)
        elikiwa op in SUCCESS_CODES:
            emit(op)
        elikiwa op in ASSERT_CODES:
            emit(op)
            skip = _len(code); emit(0)
            ikiwa av[0] >= 0:
                emit(0) # look ahead
            else:
                lo, hi = av[1].getwidth()
                ikiwa lo != hi:
                    raise error("look-behind requires fixed-width pattern")
                emit(lo) # look behind
            _compile(code, av[1], flags)
            emit(SUCCESS)
            code[skip] = _len(code) - skip
        elikiwa op is CALL:
            emit(op)
            skip = _len(code); emit(0)
            _compile(code, av, flags)
            emit(SUCCESS)
            code[skip] = _len(code) - skip
        elikiwa op is AT:
            emit(op)
            ikiwa flags & SRE_FLAG_MULTILINE:
                av = AT_MULTILINE.get(av, av)
            ikiwa flags & SRE_FLAG_LOCALE:
                av = AT_LOCALE.get(av, av)
            elikiwa flags & SRE_FLAG_UNICODE:
                av = AT_UNICODE.get(av, av)
            emit(av)
        elikiwa op is BRANCH:
            emit(op)
            tail = []
            tailappend = tail.append
            for av in av[1]:
                skip = _len(code); emit(0)
                # _compile_info(code, av, flags)
                _compile(code, av, flags)
                emit(JUMP)
                tailappend(_len(code)); emit(0)
                code[skip] = _len(code) - skip
            emit(FAILURE) # end of branch
            for tail in tail:
                code[tail] = _len(code) - tail
        elikiwa op is CATEGORY:
            emit(op)
            ikiwa flags & SRE_FLAG_LOCALE:
                av = CH_LOCALE[av]
            elikiwa flags & SRE_FLAG_UNICODE:
                av = CH_UNICODE[av]
            emit(av)
        elikiwa op is GROUPREF:
            ikiwa not flags & SRE_FLAG_IGNORECASE:
                emit(op)
            elikiwa flags & SRE_FLAG_LOCALE:
                emit(GROUPREF_LOC_IGNORE)
            elikiwa not fixes:  # ascii
                emit(GROUPREF_IGNORE)
            else:
                emit(GROUPREF_UNI_IGNORE)
            emit(av-1)
        elikiwa op is GROUPREF_EXISTS:
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
            else:
                code[skipyes] = _len(code) - skipyes + 1
        else:
            raise error("internal: unsupported operand type %r" % (op,))

eleza _compile_charset(charset, flags, code):
    # compile charset subprogram
    emit = code.append
    for op, av in charset:
        emit(op)
        ikiwa op is NEGATE:
            pass
        elikiwa op is LITERAL:
            emit(av)
        elikiwa op is RANGE or op is RANGE_UNI_IGNORE:
            emit(av[0])
            emit(av[1])
        elikiwa op is CHARSET:
            code.extend(av)
        elikiwa op is BIGCHARSET:
            code.extend(av)
        elikiwa op is CATEGORY:
            ikiwa flags & SRE_FLAG_LOCALE:
                emit(CH_LOCALE[av])
            elikiwa flags & SRE_FLAG_UNICODE:
                emit(CH_UNICODE[av])
            else:
                emit(av)
        else:
            raise error("internal: unsupported set operator %r" % (op,))
    emit(FAILURE)

eleza _optimize_charset(charset, iscased=None, fixup=None, fixes=None):
    # internal: optimize character set
    out = []
    tail = []
    charmap = bytearray(256)
    hascased = False
    for op, av in charset:
        while True:
            try:
                ikiwa op is LITERAL:
                    ikiwa fixup:
                        lo = fixup(av)
                        charmap[lo] = 1
                        ikiwa fixes and lo in fixes:
                            for k in fixes[lo]:
                                charmap[k] = 1
                        ikiwa not hascased and iscased(av):
                            hascased = True
                    else:
                        charmap[av] = 1
                elikiwa op is RANGE:
                    r = range(av[0], av[1]+1)
                    ikiwa fixup:
                        ikiwa fixes:
                            for i in map(fixup, r):
                                charmap[i] = 1
                                ikiwa i in fixes:
                                    for k in fixes[i]:
                                        charmap[k] = 1
                        else:
                            for i in map(fixup, r):
                                charmap[i] = 1
                        ikiwa not hascased:
                            hascased = any(map(iscased, r))
                    else:
                        for i in r:
                            charmap[i] = 1
                elikiwa op is NEGATE:
                    out.append((op, av))
                else:
                    tail.append((op, av))
            except IndexError:
                ikiwa len(charmap) == 256:
                    # character set contains non-UCS1 character codes
                    charmap += b'\0' * 0xff00
                    continue
                # Character set contains non-BMP character codes.
                ikiwa fixup:
                    hascased = True
                    # There are only two ranges of cased non-BMP characters:
                    # 10400-1044F (Deseret) and 118A0-118DF (Warang Citi),
                    # and for both ranges RANGE_UNI_IGNORE works.
                    ikiwa op is RANGE:
                        op = RANGE_UNI_IGNORE
                tail.append((op, av))
            break

    # compress character map
    runs = []
    q = 0
    while True:
        p = charmap.find(1, q)
        ikiwa p < 0:
            break
        ikiwa len(runs) >= 2:
            runs = None
            break
        q = charmap.find(0, p)
        ikiwa q < 0:
            runs.append((p, len(charmap)))
            break
        runs.append((p, q))
    ikiwa runs is not None:
        # use literal/range
        for p, q in runs:
            ikiwa q - p == 1:
                out.append((LITERAL, p))
            else:
                out.append((RANGE, (p, q - 1)))
        out += tail
        # ikiwa the case was changed or new representation is more compact
        ikiwa hascased or len(out) < len(charset):
            rudisha out, hascased
        # else original character set is good enough
        rudisha charset, hascased

    # use bitmap
    ikiwa len(charmap) == 256:
        data = _mk_bitmap(charmap)
        out.append((CHARSET, data))
        out += tail
        rudisha out, hascased

    # To represent a big charset, first a bitmap of all characters in the
    # set is constructed. Then, this bitmap is sliced into chunks of 256
    # characters, duplicate chunks are eliminated, and each chunk is
    # given a number. In the compiled expression, the charset is
    # represented by a 32-bit word sequence, consisting of one word for
    # the number of different chunks, a sequence of 256 bytes (64 words)
    # of chunk numbers indexed by their original chunk position, and a
    # sequence of 256-bit chunks (8 words each).

    # Compression is normally good: in a typical charset, large ranges of
    # Unicode will be either completely excluded (e.g. ikiwa only cyrillic
    # letters are to be matched), or completely included (e.g. ikiwa large
    # subranges of Kanji match). These ranges will be represented by
    # chunks of all one-bits or all zero-bits.

    # Matching can be also done efficiently: the more significant byte of
    # the Unicode character is an index into the chunk number, and the
    # less significant byte is a bit index in the chunk (just like the
    # CHARSET matching).

    charmap = bytes(charmap) # should be hashable
    comps = {}
    mapping = bytearray(256)
    block = 0
    data = bytearray()
    for i in range(0, 65536, 256):
        chunk = charmap[i: i + 256]
        ikiwa chunk in comps:
            mapping[i // 256] = comps[chunk]
        else:
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
            for i in range(len(s), 0, -_CODEBITS)]

eleza _bytes_to_codes(b):
    # Convert block indices to word array
    a = memoryview(b).cast('I')
    assert a.itemsize == _sre.CODESIZE
    assert len(a) * a.itemsize == len(b)
    rudisha a.tolist()

eleza _simple(p):
    # check ikiwa this subpattern is a "simple" operator
    ikiwa len(p) != 1:
        rudisha False
    op, av = p[0]
    ikiwa op is SUBPATTERN:
        rudisha av[0] is None and _simple(av[-1])
    rudisha op in _UNIT_CODES

eleza _generate_overlap_table(prefix):
    """
    Generate an overlap table for the following prefix.
    An overlap table is a table of the same size as the prefix which
    informs about the potential self-overlap for each index in the prefix:
    - ikiwa overlap[i] == 0, prefix[i:] can't overlap prefix[0:...]
    - ikiwa overlap[i] == k with 0 < k <= i, prefix[i-k+1:i+1] overlaps with
      prefix[0:k]
    """
    table = [0] * len(prefix)
    for i in range(1, len(prefix)):
        idx = table[i - 1]
        while prefix[i] != prefix[idx]:
            ikiwa idx == 0:
                table[i] = 0
                break
            idx = table[idx - 1]
        else:
            table[i] = idx + 1
    rudisha table

eleza _get_iscased(flags):
    ikiwa not flags & SRE_FLAG_IGNORECASE:
        rudisha None
    elikiwa flags & SRE_FLAG_UNICODE:
        rudisha _sre.unicode_iscased
    else:
        rudisha _sre.ascii_iscased

eleza _get_literal_prefix(pattern, flags):
    # look for literal prefix
    prefix = []
    prefixappend = prefix.append
    prefix_skip = None
    iscased = _get_iscased(flags)
    for op, av in pattern.data:
        ikiwa op is LITERAL:
            ikiwa iscased and iscased(av):
                break
            prefixappend(av)
        elikiwa op is SUBPATTERN:
            group, add_flags, del_flags, p = av
            flags1 = _combine_flags(flags, add_flags, del_flags)
            ikiwa flags1 & SRE_FLAG_IGNORECASE and flags1 & SRE_FLAG_LOCALE:
                break
            prefix1, prefix_skip1, got_all = _get_literal_prefix(p, flags1)
            ikiwa prefix_skip is None:
                ikiwa group is not None:
                    prefix_skip = len(prefix)
                elikiwa prefix_skip1 is not None:
                    prefix_skip = len(prefix) + prefix_skip1
            prefix.extend(prefix1)
            ikiwa not got_all:
                break
        else:
            break
    else:
        rudisha prefix, prefix_skip, True
    rudisha prefix, prefix_skip, False

eleza _get_charset_prefix(pattern, flags):
    while True:
        ikiwa not pattern.data:
            rudisha None
        op, av = pattern.data[0]
        ikiwa op is not SUBPATTERN:
            break
        group, add_flags, del_flags, pattern = av
        flags = _combine_flags(flags, add_flags, del_flags)
        ikiwa flags & SRE_FLAG_IGNORECASE and flags & SRE_FLAG_LOCALE:
            rudisha None

    iscased = _get_iscased(flags)
    ikiwa op is LITERAL:
        ikiwa iscased and iscased(av):
            rudisha None
        rudisha [(op, av)]
    elikiwa op is BRANCH:
        charset = []
        charsetappend = charset.append
        for p in av[1]:
            ikiwa not p:
                rudisha None
            op, av = p[0]
            ikiwa op is LITERAL and not (iscased and iscased(av)):
                charsetappend((op, av))
            else:
                rudisha None
        rudisha charset
    elikiwa op is IN:
        charset = av
        ikiwa iscased:
            for op, av in charset:
                ikiwa op is LITERAL:
                    ikiwa iscased(av):
                        rudisha None
                elikiwa op is RANGE:
                    ikiwa av[1] > 0xffff:
                        rudisha None
                    ikiwa any(map(iscased, range(av[0], av[1]+1))):
                        rudisha None
        rudisha charset
    rudisha None

eleza _compile_info(code, pattern, flags):
    # internal: compile an info block.  in the current version,
    # this contains min/max pattern width, and an optional literal
    # prefix or a character map
    lo, hi = pattern.getwidth()
    ikiwa hi > MAXCODE:
        hi = MAXCODE
    ikiwa lo == 0:
        code.extend([INFO, 4, 0, lo, hi])
        return
    # look for a literal prefix
    prefix = []
    prefix_skip = 0
    charset = [] # not used
    ikiwa not (flags & SRE_FLAG_IGNORECASE and flags & SRE_FLAG_LOCALE):
        # look for literal prefix
        prefix, prefix_skip, got_all = _get_literal_prefix(pattern, flags)
        # ikiwa no prefix, look for charset prefix
        ikiwa not prefix:
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
        ikiwa prefix_skip is None and got_all:
            mask = mask | SRE_INFO_LITERAL
    elikiwa charset:
        mask = mask | SRE_INFO_CHARSET
    emit(mask)
    # pattern length
    ikiwa lo < MAXCODE:
        emit(lo)
    else:
        emit(MAXCODE)
        prefix = prefix[:MAXCODE]
    emit(min(hi, MAXCODE))
    # add literal prefix
    ikiwa prefix:
        emit(len(prefix)) # length
        ikiwa prefix_skip is None:
            prefix_skip =  len(prefix)
        emit(prefix_skip) # skip
        code.extend(prefix)
        # generate overlap table
        code.extend(_generate_overlap_table(prefix))
    elikiwa charset:
        charset, hascased = _optimize_charset(charset)
        assert not hascased
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
    rudisha '[%s]' % ', '.join('%#0*x' % (_sre.CODESIZE*2+2, x) for x in code)

eleza dis(code):
    agiza sys

    labels = set()
    level = 0
    offset_width = len(str(len(code) - 1))

    eleza dis_(start, end):
        eleza print_(*args, to=None):
            ikiwa to is not None:
                labels.add(to)
                args += ('(to %d)' % (to,),)
            andika('%*d%s ' % (offset_width, start, ':' ikiwa start in labels else '.'),
                  end='  '*(level-1))
            andika(*args)

        eleza print_2(*args):
            andika(end=' '*(offset_width + 2*level))
            andika(*args)

        nonlocal level
        level += 1
        i = start
        while i < end:
            start = i
            op = code[i]
            i += 1
            op = OPCODES[op]
            ikiwa op in (SUCCESS, FAILURE, ANY, ANY_ALL,
                      MAX_UNTIL, MIN_UNTIL, NEGATE):
                print_(op)
            elikiwa op in (LITERAL, NOT_LITERAL,
                        LITERAL_IGNORE, NOT_LITERAL_IGNORE,
                        LITERAL_UNI_IGNORE, NOT_LITERAL_UNI_IGNORE,
                        LITERAL_LOC_IGNORE, NOT_LITERAL_LOC_IGNORE):
                arg = code[i]
                i += 1
                print_(op, '%#02x (%r)' % (arg, chr(arg)))
            elikiwa op is AT:
                arg = code[i]
                i += 1
                arg = str(ATCODES[arg])
                assert arg[:3] == 'AT_'
                print_(op, arg[3:])
            elikiwa op is CATEGORY:
                arg = code[i]
                i += 1
                arg = str(CHCODES[arg])
                assert arg[:9] == 'CATEGORY_'
                print_(op, arg[9:])
            elikiwa op in (IN, IN_IGNORE, IN_UNI_IGNORE, IN_LOC_IGNORE):
                skip = code[i]
                print_(op, skip, to=i+skip)
                dis_(i+1, i+skip)
                i += skip
            elikiwa op in (RANGE, RANGE_UNI_IGNORE):
                lo, hi = code[i: i+2]
                i += 2
                print_(op, '%#02x %#02x (%r-%r)' % (lo, hi, chr(lo), chr(hi)))
            elikiwa op is CHARSET:
                print_(op, _hex_code(code[i: i + 256//_CODEBITS]))
                i += 256//_CODEBITS
            elikiwa op is BIGCHARSET:
                arg = code[i]
                i += 1
                mapping = list(b''.join(x.to_bytes(_sre.CODESIZE, sys.byteorder)
                                        for x in code[i: i + 256//_sre.CODESIZE]))
                print_(op, arg, mapping)
                i += 256//_sre.CODESIZE
                level += 1
                for j in range(arg):
                    print_2(_hex_code(code[i: i + 256//_CODEBITS]))
                    i += 256//_CODEBITS
                level -= 1
            elikiwa op in (MARK, GROUPREF, GROUPREF_IGNORE, GROUPREF_UNI_IGNORE,
                        GROUPREF_LOC_IGNORE):
                arg = code[i]
                i += 1
                print_(op, arg)
            elikiwa op is JUMP:
                skip = code[i]
                print_(op, skip, to=i+skip)
                i += 1
            elikiwa op is BRANCH:
                skip = code[i]
                print_(op, skip, to=i+skip)
                while skip:
                    dis_(i+1, i+skip)
                    i += skip
                    start = i
                    skip = code[i]
                    ikiwa skip:
                        print_('branch', skip, to=i+skip)
                    else:
                        print_(FAILURE)
                i += 1
            elikiwa op in (REPEAT, REPEAT_ONE, MIN_REPEAT_ONE):
                skip, min, max = code[i: i+3]
                ikiwa max == MAXREPEAT:
                    max = 'MAXREPEAT'
                print_(op, skip, min, max, to=i+skip)
                dis_(i+3, i+skip)
                i += skip
            elikiwa op is GROUPREF_EXISTS:
                arg, skip = code[i: i+2]
                print_(op, arg, skip, to=i+skip)
                i += 2
            elikiwa op in (ASSERT, ASSERT_NOT):
                skip, arg = code[i: i+2]
                print_(op, skip, arg, to=i+skip)
                dis_(i+2, i+skip)
                i += skip
            elikiwa op is INFO:
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
                            '[%s]' % ', '.join('%#02x' % x for x in prefix),
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
            else:
                raise ValueError(op)

        level -= 1

    dis_(0, len(code))


eleza compile(p, flags=0):
    # internal: convert pattern list to internal format

    ikiwa isstring(p):
        pattern = p
        p = sre_parse.parse(p, flags)
    else:
        pattern = None

    code = _code(p, flags)

    ikiwa flags & SRE_FLAG_DEBUG:
        andika()
        dis(code)

    # map in either direction
    groupindex = p.state.groupdict
    indexgroup = [None] * p.state.groups
    for k, i in groupindex.items():
        indexgroup[i] = k

    rudisha _sre.compile(
        pattern, flags | p.state.flags, code,
        p.state.groups-1,
        groupindex, tuple(indexgroup)
        )
