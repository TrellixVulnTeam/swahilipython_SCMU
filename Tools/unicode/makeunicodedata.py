#
# (re)generate unicode property na type databases
#
# This script converts Unicode database files to Modules/unicodedata_db.h,
# Modules/unicodename_db.h, na Objects/unicodetype_db.h
#
# history:
# 2000-09-24 fl   created (based on bits na pieces kutoka unidb)
# 2000-09-25 fl   merged tim's splitbin fixes, separate decomposition table
# 2000-09-25 fl   added character type table
# 2000-09-26 fl   added LINEBREAK, DECIMAL, na DIGIT flags/fields (2.0)
# 2000-11-03 fl   expand first/last ranges
# 2001-01-19 fl   added character name tables (2.1)
# 2001-01-21 fl   added decomp compression; dynamic phrasebook threshold
# 2002-09-11 wd   use string methods
# 2002-10-18 mvl  update to Unicode 3.2
# 2002-10-22 mvl  generate NFC tables
# 2002-11-24 mvl  expand all ranges, sort names version-independently
# 2002-11-25 mvl  add UNIDATA_VERSION
# 2004-05-29 perky add east asian width information
# 2006-03-10 mvl  update to Unicode 4.1; add UCD 3.2 delta
# 2008-06-11 gb   add PRINTABLE_MASK kila Atsuo Ishimoto's ascii() patch
# 2011-10-21 ezio add support kila name aliases na named sequences
# 2012-01    benjamin add full case mappings
#
# written by Fredrik Lundh (fredrik@pythonware.com)
#

agiza os
agiza sys
agiza zipfile

kutoka textwrap agiza dedent
kutoka functools agiza partial

SCRIPT = sys.argv[0]
VERSION = "3.3"

# The Unicode Database
# --------------------
# When changing UCD version please update
#   * Doc/library/stdtypes.rst, na
#   * Doc/library/unicodedata.rst
#   * Doc/reference/lexical_analysis.rst (two occurrences)
UNIDATA_VERSION = "12.1.0"
UNICODE_DATA = "UnicodeData%s.txt"
COMPOSITION_EXCLUSIONS = "CompositionExclusions%s.txt"
EASTASIAN_WIDTH = "EastAsianWidth%s.txt"
UNIHAN = "Unihan%s.zip"
DERIVED_CORE_PROPERTIES = "DerivedCoreProperties%s.txt"
DERIVEDNORMALIZATION_PROPS = "DerivedNormalizationProps%s.txt"
LINE_BREAK = "LineBreak%s.txt"
NAME_ALIASES = "NameAliases%s.txt"
NAMED_SEQUENCES = "NamedSequences%s.txt"
SPECIAL_CASING = "SpecialCasing%s.txt"
CASE_FOLDING = "CaseFolding%s.txt"

# Private Use Areas -- kwenye planes 1, 15, 16
PUA_1 = range(0xE000, 0xF900)
PUA_15 = range(0xF0000, 0xFFFFE)
PUA_16 = range(0x100000, 0x10FFFE)

# we use this ranges of PUA_15 to store name aliases na named sequences
NAME_ALIASES_START = 0xF0000
NAMED_SEQUENCES_START = 0xF0200

old_versions = ["3.2.0"]

CATEGORY_NAMES = [ "Cn", "Lu", "Ll", "Lt", "Mn", "Mc", "Me", "Nd",
    "Nl", "No", "Zs", "Zl", "Zp", "Cc", "Cf", "Cs", "Co", "Cn", "Lm",
    "Lo", "Pc", "Pd", "Ps", "Pe", "Pi", "Pf", "Po", "Sm", "Sc", "Sk",
    "So" ]

BIDIRECTIONAL_NAMES = [ "", "L", "LRE", "LRO", "R", "AL", "RLE", "RLO",
    "PDF", "EN", "ES", "ET", "AN", "CS", "NSM", "BN", "B", "S", "WS",
    "ON", "LRI", "RLI", "FSI", "PDI" ]

EASTASIANWIDTH_NAMES = [ "F", "H", "W", "Na", "A", "N" ]

MANDATORY_LINE_BREAKS = [ "BK", "CR", "LF", "NL" ]

# note: should match definitions kwenye Objects/unicodectype.c
ALPHA_MASK = 0x01
DECIMAL_MASK = 0x02
DIGIT_MASK = 0x04
LOWER_MASK = 0x08
LINEBREAK_MASK = 0x10
SPACE_MASK = 0x20
TITLE_MASK = 0x40
UPPER_MASK = 0x80
XID_START_MASK = 0x100
XID_CONTINUE_MASK = 0x200
PRINTABLE_MASK = 0x400
NUMERIC_MASK = 0x800
CASE_IGNORABLE_MASK = 0x1000
CASED_MASK = 0x2000
EXTENDED_CASE_MASK = 0x4000

# these ranges need to match unicodedata.c:is_unified_ideograph
cjk_ranges = [
    ('3400', '4DB5'),
    ('4E00', '9FEF'),
    ('20000', '2A6D6'),
    ('2A700', '2B734'),
    ('2B740', '2B81D'),
    ('2B820', '2CEA1'),
    ('2CEB0', '2EBE0'),
]


eleza maketables(trace=0):

    andika("--- Reading", UNICODE_DATA % "", "...")

    unicode = UnicodeData(UNIDATA_VERSION)

    andika(len(list(filter(Tupu, unicode.table))), "characters")

    kila version kwenye old_versions:
        andika("--- Reading", UNICODE_DATA % ("-"+version), "...")
        old_unicode = UnicodeData(version, cjk_check=Uongo)
        andika(len(list(filter(Tupu, old_unicode.table))), "characters")
        merge_old_version(version, unicode, old_unicode)

    makeunicodename(unicode, trace)
    makeunicodedata(unicode, trace)
    makeunicodetype(unicode, trace)


# --------------------------------------------------------------------
# unicode character properties

eleza makeunicodedata(unicode, trace):

    dummy = (0, 0, 0, 0, 0, 0)
    table = [dummy]
    cache = {0: dummy}
    index = [0] * len(unicode.chars)

    FILE = "Modules/unicodedata_db.h"

    andika("--- Preparing", FILE, "...")

    # 1) database properties

    kila char kwenye unicode.chars:
        record = unicode.table[char]
        ikiwa record:
            # extract database properties
            category = CATEGORY_NAMES.index(record[2])
            combining = int(record[3])
            bidirectional = BIDIRECTIONAL_NAMES.index(record[4])
            mirrored = record[9] == "Y"
            eastasianwidth = EASTASIANWIDTH_NAMES.index(record[15])
            normalizationquickcheck = record[17]
            item = (
                category, combining, bidirectional, mirrored, eastasianwidth,
                normalizationquickcheck
                )
            # add entry to index na item tables
            i = cache.get(item)
            ikiwa i ni Tupu:
                cache[item] = i = len(table)
                table.append(item)
            index[char] = i

    # 2) decomposition data

    decomp_data = [0]
    decomp_prefix = [""]
    decomp_index = [0] * len(unicode.chars)
    decomp_size = 0

    comp_pairs = []
    comp_first = [Tupu] * len(unicode.chars)
    comp_last = [Tupu] * len(unicode.chars)

    kila char kwenye unicode.chars:
        record = unicode.table[char]
        ikiwa record:
            ikiwa record[5]:
                decomp = record[5].split()
                ikiwa len(decomp) > 19:
                    ashiria Exception("character %x has a decomposition too large kila nfd_nfkd" % char)
                # prefix
                ikiwa decomp[0][0] == "<":
                    prefix = decomp.pop(0)
                isipokua:
                    prefix = ""
                jaribu:
                    i = decomp_prefix.index(prefix)
                tatizo ValueError:
                    i = len(decomp_prefix)
                    decomp_prefix.append(prefix)
                prefix = i
                assert prefix < 256
                # content
                decomp = [prefix + (len(decomp)<<8)] + [int(s, 16) kila s kwenye decomp]
                # Collect NFC pairs
                ikiwa sio prefix na len(decomp) == 3 na \
                   char haiko kwenye unicode.exclusions na \
                   unicode.table[decomp[1]][3] == "0":
                    p, l, r = decomp
                    comp_first[l] = 1
                    comp_last[r] = 1
                    comp_pairs.append((l,r,char))
                jaribu:
                    i = decomp_data.index(decomp)
                tatizo ValueError:
                    i = len(decomp_data)
                    decomp_data.extend(decomp)
                    decomp_size = decomp_size + len(decomp) * 2
            isipokua:
                i = 0
            decomp_index[char] = i

    f = l = 0
    comp_first_ranges = []
    comp_last_ranges = []
    prev_f = prev_l = Tupu
    kila i kwenye unicode.chars:
        ikiwa comp_first[i] ni sio Tupu:
            comp_first[i] = f
            f += 1
            ikiwa prev_f ni Tupu:
                prev_f = (i,i)
            lasivyo prev_f[1]+1 == i:
                prev_f = prev_f[0],i
            isipokua:
                comp_first_ranges.append(prev_f)
                prev_f = (i,i)
        ikiwa comp_last[i] ni sio Tupu:
            comp_last[i] = l
            l += 1
            ikiwa prev_l ni Tupu:
                prev_l = (i,i)
            lasivyo prev_l[1]+1 == i:
                prev_l = prev_l[0],i
            isipokua:
                comp_last_ranges.append(prev_l)
                prev_l = (i,i)
    comp_first_ranges.append(prev_f)
    comp_last_ranges.append(prev_l)
    total_first = f
    total_last = l

    comp_data = [0]*(total_first*total_last)
    kila f,l,char kwenye comp_pairs:
        f = comp_first[f]
        l = comp_last[l]
        comp_data[f*total_last+l] = char

    andika(len(table), "unique properties")
    andika(len(decomp_prefix), "unique decomposition prefixes")
    andika(len(decomp_data), "unique decomposition entries:", end=' ')
    andika(decomp_size, "bytes")
    andika(total_first, "first characters kwenye NFC")
    andika(total_last, "last characters kwenye NFC")
    andika(len(comp_pairs), "NFC pairs")

    andika("--- Writing", FILE, "...")

    ukijumuisha open(FILE, "w") kama fp:
        fprint = partial(print, file=fp)

        fandika("/* this file was generated by %s %s */" % (SCRIPT, VERSION))
        fandika()
        fandika('#define UNIDATA_VERSION "%s"' % UNIDATA_VERSION)
        fandika("/* a list of unique database records */")
        fandika("const _PyUnicode_DatabaseRecord _PyUnicode_Database_Records[] = {")
        kila item kwenye table:
            fandika("    {%d, %d, %d, %d, %d, %d}," % item)
        fandika("};")
        fandika()

        fandika("/* Reindexing of NFC first characters. */")
        fandika("#define TOTAL_FIRST",total_first)
        fandika("#define TOTAL_LAST",total_last)
        fandika("struct reindex{int start;short count,index;};")
        fandika("static struct reindex nfc_first[] = {")
        kila start,end kwenye comp_first_ranges:
            fandika("    { %d, %d, %d}," % (start,end-start,comp_first[start]))
        fandika("    {0,0,0}")
        fandika("};\n")
        fandika("static struct reindex nfc_last[] = {")
        kila start,end kwenye comp_last_ranges:
            fandika("  { %d, %d, %d}," % (start,end-start,comp_last[start]))
        fandika("  {0,0,0}")
        fandika("};\n")

        # FIXME: <fl> the following tables could be made static, na
        # the support code moved into unicodedatabase.c

        fandika("/* string literals */")
        fandika("const char *_PyUnicode_CategoryNames[] = {")
        kila name kwenye CATEGORY_NAMES:
            fandika("    \"%s\"," % name)
        fandika("    NULL")
        fandika("};")

        fandika("const char *_PyUnicode_BidirectionalNames[] = {")
        kila name kwenye BIDIRECTIONAL_NAMES:
            fandika("    \"%s\"," % name)
        fandika("    NULL")
        fandika("};")

        fandika("const char *_PyUnicode_EastAsianWidthNames[] = {")
        kila name kwenye EASTASIANWIDTH_NAMES:
            fandika("    \"%s\"," % name)
        fandika("    NULL")
        fandika("};")

        fandika("static const char *decomp_prefix[] = {")
        kila name kwenye decomp_prefix:
            fandika("    \"%s\"," % name)
        fandika("    NULL")
        fandika("};")

        # split record index table
        index1, index2, shift = splitbins(index, trace)

        fandika("/* index tables kila the database records */")
        fandika("#define SHIFT", shift)
        Array("index1", index1).dump(fp, trace)
        Array("index2", index2).dump(fp, trace)

        # split decomposition index table
        index1, index2, shift = splitbins(decomp_index, trace)

        fandika("/* decomposition data */")
        Array("decomp_data", decomp_data).dump(fp, trace)

        fandika("/* index tables kila the decomposition data */")
        fandika("#define DECOMP_SHIFT", shift)
        Array("decomp_index1", index1).dump(fp, trace)
        Array("decomp_index2", index2).dump(fp, trace)

        index, index2, shift = splitbins(comp_data, trace)
        fandika("/* NFC pairs */")
        fandika("#define COMP_SHIFT", shift)
        Array("comp_index", index).dump(fp, trace)
        Array("comp_data", index2).dump(fp, trace)

        # Generate delta tables kila old versions
        kila version, table, normalization kwenye unicode.changed:
            cversion = version.replace(".","_")
            records = [table[0]]
            cache = {table[0]:0}
            index = [0] * len(table)
            kila i, record kwenye enumerate(table):
                jaribu:
                    index[i] = cache[record]
                tatizo KeyError:
                    index[i] = cache[record] = len(records)
                    records.append(record)
            index1, index2, shift = splitbins(index, trace)
            fandika("static const change_record change_records_%s[] = {" % cversion)
            kila record kwenye records:
                fandika("    { %s }," % ", ".join(map(str,record)))
            fandika("};")
            Array("changes_%s_index" % cversion, index1).dump(fp, trace)
            Array("changes_%s_data" % cversion, index2).dump(fp, trace)
            fandika("static const change_record* get_change_%s(Py_UCS4 n)" % cversion)
            fandika("{")
            fandika("    int index;")
            fandika("    ikiwa (n >= 0x110000) index = 0;")
            fandika("    isipokua {")
            fandika("        index = changes_%s_index[n>>%d];" % (cversion, shift))
            fandika("        index = changes_%s_data[(index<<%d)+(n & %d)];" % \
                   (cversion, shift, ((1<<shift)-1)))
            fandika("    }")
            fandika("    rudisha change_records_%s+index;" % cversion)
            fandika("}\n")
            fandika("static Py_UCS4 normalization_%s(Py_UCS4 n)" % cversion)
            fandika("{")
            fandika("    switch(n) {")
            kila k, v kwenye normalization:
                fandika("    case %s: rudisha 0x%s;" % (hex(k), v))
            fandika("    default: rudisha 0;")
            fandika("    }\n}\n")


# --------------------------------------------------------------------
# unicode character type tables

eleza makeunicodetype(unicode, trace):

    FILE = "Objects/unicodetype_db.h"

    andika("--- Preparing", FILE, "...")

    # extract unicode types
    dummy = (0, 0, 0, 0, 0, 0)
    table = [dummy]
    cache = {0: dummy}
    index = [0] * len(unicode.chars)
    numeric = {}
    spaces = []
    linekomas = []
    extra_casing = []

    kila char kwenye unicode.chars:
        record = unicode.table[char]
        ikiwa record:
            # extract database properties
            category = record[2]
            bidirectional = record[4]
            properties = record[16]
            flags = 0
            ikiwa category kwenye ["Lm", "Lt", "Lu", "Ll", "Lo"]:
                flags |= ALPHA_MASK
            ikiwa "Lowercase" kwenye properties:
                flags |= LOWER_MASK
            ikiwa 'Line_Break' kwenye properties ama bidirectional == "B":
                flags |= LINEBREAK_MASK
                linekomas.append(char)
            ikiwa category == "Zs" ama bidirectional kwenye ("WS", "B", "S"):
                flags |= SPACE_MASK
                spaces.append(char)
            ikiwa category == "Lt":
                flags |= TITLE_MASK
            ikiwa "Uppercase" kwenye properties:
                flags |= UPPER_MASK
            ikiwa char == ord(" ") ama category[0] haiko kwenye ("C", "Z"):
                flags |= PRINTABLE_MASK
            ikiwa "XID_Start" kwenye properties:
                flags |= XID_START_MASK
            ikiwa "XID_Continue" kwenye properties:
                flags |= XID_CONTINUE_MASK
            ikiwa "Cased" kwenye properties:
                flags |= CASED_MASK
            ikiwa "Case_Ignorable" kwenye properties:
                flags |= CASE_IGNORABLE_MASK
            sc = unicode.special_casing.get(char)
            cf = unicode.case_folding.get(char, [char])
            ikiwa record[12]:
                upper = int(record[12], 16)
            isipokua:
                upper = char
            ikiwa record[13]:
                lower = int(record[13], 16)
            isipokua:
                lower = char
            ikiwa record[14]:
                title = int(record[14], 16)
            isipokua:
                title = upper
            ikiwa sc ni Tupu na cf != [lower]:
                sc = ([lower], [title], [upper])
            ikiwa sc ni Tupu:
                ikiwa upper == lower == title:
                    upper = lower = title = 0
                isipokua:
                    upper = upper - char
                    lower = lower - char
                    title = title - char
                    assert (abs(upper) <= 2147483647 na
                            abs(lower) <= 2147483647 na
                            abs(title) <= 2147483647)
            isipokua:
                # This happens either when some character maps to more than one
                # character kwenye uppercase, lowercase, ama titlecase ama the
                # casefolded version of the character ni different kutoka the
                # lowercase. The extra characters are stored kwenye a different
                # array.
                flags |= EXTENDED_CASE_MASK
                lower = len(extra_casing) | (len(sc[0]) << 24)
                extra_casing.extend(sc[0])
                ikiwa cf != sc[0]:
                    lower |= len(cf) << 20
                    extra_casing.extend(cf)
                upper = len(extra_casing) | (len(sc[2]) << 24)
                extra_casing.extend(sc[2])
                # Title ni probably equal to upper.
                ikiwa sc[1] == sc[2]:
                    title = upper
                isipokua:
                    title = len(extra_casing) | (len(sc[1]) << 24)
                    extra_casing.extend(sc[1])
            # decimal digit, integer digit
            decimal = 0
            ikiwa record[6]:
                flags |= DECIMAL_MASK
                decimal = int(record[6])
            digit = 0
            ikiwa record[7]:
                flags |= DIGIT_MASK
                digit = int(record[7])
            ikiwa record[8]:
                flags |= NUMERIC_MASK
                numeric.setdefault(record[8], []).append(char)
            item = (
                upper, lower, title, decimal, digit, flags
                )
            # add entry to index na item tables
            i = cache.get(item)
            ikiwa i ni Tupu:
                cache[item] = i = len(table)
                table.append(item)
            index[char] = i

    andika(len(table), "unique character type entries")
    andika(sum(map(len, numeric.values())), "numeric code points")
    andika(len(spaces), "whitespace code points")
    andika(len(linekomas), "linekoma code points")
    andika(len(extra_casing), "extended case array")

    andika("--- Writing", FILE, "...")

    ukijumuisha open(FILE, "w") kama fp:
        fprint = partial(print, file=fp)

        fandika("/* this file was generated by %s %s */" % (SCRIPT, VERSION))
        fandika()
        fandika("/* a list of unique character type descriptors */")
        fandika("const _PyUnicode_TypeRecord _PyUnicode_TypeRecords[] = {")
        kila item kwenye table:
            fandika("    {%d, %d, %d, %d, %d, %d}," % item)
        fandika("};")
        fandika()

        fandika("/* extended case mappings */")
        fandika()
        fandika("const Py_UCS4 _PyUnicode_ExtendedCase[] = {")
        kila c kwenye extra_casing:
            fandika("    %d," % c)
        fandika("};")
        fandika()

        # split decomposition index table
        index1, index2, shift = splitbins(index, trace)

        fandika("/* type indexes */")
        fandika("#define SHIFT", shift)
        Array("index1", index1).dump(fp, trace)
        Array("index2", index2).dump(fp, trace)

        # Generate code kila _PyUnicode_ToNumeric()
        numeric_items = sorted(numeric.items())
        fandika('/* Returns the numeric value kama double kila Unicode characters')
        fandika(' * having this property, -1.0 otherwise.')
        fandika(' */')
        fandika('double _PyUnicode_ToNumeric(Py_UCS4 ch)')
        fandika('{')
        fandika('    switch (ch) {')
        kila value, codepoints kwenye numeric_items:
            # Turn text into float literals
            parts = value.split('/')
            parts = [repr(float(part)) kila part kwenye parts]
            value = '/'.join(parts)

            codepoints.sort()
            kila codepoint kwenye codepoints:
                fandika('    case 0x%04X:' % (codepoint,))
            fandika('        rudisha (double) %s;' % (value,))
        fandika('    }')
        fandika('    rudisha -1.0;')
        fandika('}')
        fandika()

        # Generate code kila _PyUnicode_IsWhitespace()
        fandika("/* Returns 1 kila Unicode characters having the bidirectional")
        fandika(" * type 'WS', 'B' ama 'S' ama the category 'Zs', 0 otherwise.")
        fandika(" */")
        fandika('int _PyUnicode_IsWhitespace(const Py_UCS4 ch)')
        fandika('{')
        fandika('    switch (ch) {')

        kila codepoint kwenye sorted(spaces):
            fandika('    case 0x%04X:' % (codepoint,))
        fandika('        rudisha 1;')

        fandika('    }')
        fandika('    rudisha 0;')
        fandika('}')
        fandika()

        # Generate code kila _PyUnicode_IsLinekoma()
        fandika("/* Returns 1 kila Unicode characters having the line koma")
        fandika(" * property 'BK', 'CR', 'LF' ama 'NL' ama having bidirectional")
        fandika(" * type 'B', 0 otherwise.")
        fandika(" */")
        fandika('int _PyUnicode_IsLinekoma(const Py_UCS4 ch)')
        fandika('{')
        fandika('    switch (ch) {')
        kila codepoint kwenye sorted(linekomas):
            fandika('    case 0x%04X:' % (codepoint,))
        fandika('        rudisha 1;')

        fandika('    }')
        fandika('    rudisha 0;')
        fandika('}')
        fandika()


# --------------------------------------------------------------------
# unicode name database

eleza makeunicodename(unicode, trace):

    FILE = "Modules/unicodename_db.h"

    andika("--- Preparing", FILE, "...")

    # collect names
    names = [Tupu] * len(unicode.chars)

    kila char kwenye unicode.chars:
        record = unicode.table[char]
        ikiwa record:
            name = record[1].strip()
            ikiwa name na name[0] != "<":
                names[char] = name + chr(0)

    andika(len([n kila n kwenye names ikiwa n ni sio Tupu]), "distinct names")

    # collect unique words kutoka names (note that we differ between
    # words inside a sentence, na words ending a sentence.  the
    # latter includes the trailing null byte.

    words = {}
    n = b = 0
    kila char kwenye unicode.chars:
        name = names[char]
        ikiwa name:
            w = name.split()
            b = b + len(name)
            n = n + len(w)
            kila w kwenye w:
                l = words.get(w)
                ikiwa l:
                    l.append(Tupu)
                isipokua:
                    words[w] = [len(words)]

    andika(n, "words kwenye text;", b, "bytes")

    wordlist = list(words.items())

    # sort on falling frequency, then by name
    eleza word_key(a):
        aword, alist = a
        rudisha -len(alist), aword
    wordlist.sort(key=word_key)

    # figure out how many phrasebook escapes we need
    escapes = 0
    wakati escapes * 256 < len(wordlist):
        escapes = escapes + 1
    andika(escapes, "escapes")

    short = 256 - escapes

    assert short > 0

    andika(short, "short indexes kwenye lexicon")

    # statistics
    n = 0
    kila i kwenye range(short):
        n = n + len(wordlist[i][1])
    andika(n, "short indexes kwenye phrasebook")

    # pick the most commonly used words, na sort the rest on falling
    # length (to maximize overlap)

    wordlist, wordtail = wordlist[:short], wordlist[short:]
    wordtail.sort(key=lambda a: a[0], reverse=Kweli)
    wordlist.extend(wordtail)

    # generate lexicon kutoka words

    lexicon_offset = [0]
    lexicon = ""
    words = {}

    # build a lexicon string
    offset = 0
    kila w, x kwenye wordlist:
        # encoding: bit 7 indicates last character kwenye word (chr(128)
        # indicates the last character kwenye an entire string)
        ww = w[:-1] + chr(ord(w[-1])+128)
        # reuse string tails, when possible
        o = lexicon.find(ww)
        ikiwa o < 0:
            o = offset
            lexicon = lexicon + ww
            offset = offset + len(w)
        words[w] = len(lexicon_offset)
        lexicon_offset.append(o)

    lexicon = list(map(ord, lexicon))

    # generate phrasebook kutoka names na lexicon
    phrasebook = [0]
    phrasebook_offset = [0] * len(unicode.chars)
    kila char kwenye unicode.chars:
        name = names[char]
        ikiwa name:
            w = name.split()
            phrasebook_offset[char] = len(phrasebook)
            kila w kwenye w:
                i = words[w]
                ikiwa i < short:
                    phrasebook.append(i)
                isipokua:
                    # store kama two bytes
                    phrasebook.append((i>>8) + short)
                    phrasebook.append(i&255)

    assert getsize(phrasebook) == 1

    #
    # unicode name hash table

    # extract names
    data = []
    kila char kwenye unicode.chars:
        record = unicode.table[char]
        ikiwa record:
            name = record[1].strip()
            ikiwa name na name[0] != "<":
                data.append((name, char))

    # the magic number 47 was chosen to minimize the number of
    # collisions on the current data set.  ikiwa you like, change it
    # na see what happens...

    codehash = Hash("code", data, 47)

    andika("--- Writing", FILE, "...")

    ukijumuisha open(FILE, "w") kama fp:
        fprint = partial(print, file=fp)

        fandika("/* this file was generated by %s %s */" % (SCRIPT, VERSION))
        fandika()
        fandika("#define NAME_MAXLEN", 256)
        fandika()
        fandika("/* lexicon */")
        Array("lexicon", lexicon).dump(fp, trace)
        Array("lexicon_offset", lexicon_offset).dump(fp, trace)

        # split decomposition index table
        offset1, offset2, shift = splitbins(phrasebook_offset, trace)

        fandika("/* code->name phrasebook */")
        fandika("#define phrasebook_shift", shift)
        fandika("#define phrasebook_short", short)

        Array("phrasebook", phrasebook).dump(fp, trace)
        Array("phrasebook_offset1", offset1).dump(fp, trace)
        Array("phrasebook_offset2", offset2).dump(fp, trace)

        fandika("/* name->code dictionary */")
        codehash.dump(fp, trace)

        fandika()
        fandika('static const unsigned int aliases_start = %#x;' %
               NAME_ALIASES_START)
        fandika('static const unsigned int aliases_end = %#x;' %
               (NAME_ALIASES_START + len(unicode.aliases)))

        fandika('static const unsigned int name_aliases[] = {')
        kila name, codepoint kwenye unicode.aliases:
            fandika('    0x%04X,' % codepoint)
        fandika('};')

        # In Unicode 6.0.0, the sequences contain at most 4 BMP chars,
        # so we are using Py_UCS2 seq[4].  This needs to be updated ikiwa longer
        # sequences ama sequences ukijumuisha non-BMP chars are added.
        # unicodedata_lookup should be adapted too.
        fandika(dedent("""
            typeeleza struct NamedSequence {
                int seqlen;
                Py_UCS2 seq[4];
            } named_sequence;
            """))

        fandika('static const unsigned int named_sequences_start = %#x;' %
               NAMED_SEQUENCES_START)
        fandika('static const unsigned int named_sequences_end = %#x;' %
               (NAMED_SEQUENCES_START + len(unicode.named_sequences)))

        fandika('static const named_sequence named_sequences[] = {')
        kila name, sequence kwenye unicode.named_sequences:
            seq_str = ', '.join('0x%04X' % cp kila cp kwenye sequence)
            fandika('    {%d, {%s}},' % (len(sequence), seq_str))
        fandika('};')


eleza merge_old_version(version, new, old):
    # Changes to exclusion file sio implemented yet
    ikiwa old.exclusions != new.exclusions:
        ashiria NotImplementedError("exclusions differ")

    # In these change records, 0xFF means "no change"
    bidir_changes = [0xFF]*0x110000
    category_changes = [0xFF]*0x110000
    decimal_changes = [0xFF]*0x110000
    mirrored_changes = [0xFF]*0x110000
    east_asian_width_changes = [0xFF]*0x110000
    # In numeric data, 0 means "no change",
    # -1 means "did sio have a numeric value
    numeric_changes = [0] * 0x110000
    # normalization_changes ni a list of key-value pairs
    normalization_changes = []
    kila i kwenye range(0x110000):
        ikiwa new.table[i] ni Tupu:
            # Characters unassigned kwenye the new version ought to
            # be unassigned kwenye the old one
            assert old.table[i] ni Tupu
            endelea
        # check characters unassigned kwenye the old version
        ikiwa old.table[i] ni Tupu:
            # category 0 ni "unassigned"
            category_changes[i] = 0
            endelea
        # check characters that differ
        ikiwa old.table[i] != new.table[i]:
            kila k kwenye range(len(old.table[i])):
                ikiwa old.table[i][k] != new.table[i][k]:
                    value = old.table[i][k]
                    ikiwa k == 1 na i kwenye PUA_15:
                        # the name ni sio set kwenye the old.table, but kwenye the
                        # new.table we are using it kila aliases na named seq
                        assert value == ''
                    lasivyo k == 2:
                        #print "CATEGORY",hex(i), old.table[i][k], new.table[i][k]
                        category_changes[i] = CATEGORY_NAMES.index(value)
                    lasivyo k == 4:
                        #print "BIDIR",hex(i), old.table[i][k], new.table[i][k]
                        bidir_changes[i] = BIDIRECTIONAL_NAMES.index(value)
                    lasivyo k == 5:
                        #print "DECOMP",hex(i), old.table[i][k], new.table[i][k]
                        # We assume that all normalization changes are kwenye 1:1 mappings
                        assert " " haiko kwenye value
                        normalization_changes.append((i, value))
                    lasivyo k == 6:
                        #print "DECIMAL",hex(i), old.table[i][k], new.table[i][k]
                        # we only support changes where the old value ni a single digit
                        assert value kwenye "0123456789"
                        decimal_changes[i] = int(value)
                    lasivyo k == 8:
                        # print "NUMERIC",hex(i), `old.table[i][k]`, new.table[i][k]
                        # Since 0 encodes "no change", the old value ni better sio 0
                        ikiwa sio value:
                            numeric_changes[i] = -1
                        isipokua:
                            numeric_changes[i] = float(value)
                            assert numeric_changes[i] haiko kwenye (0, -1)
                    lasivyo k == 9:
                        ikiwa value == 'Y':
                            mirrored_changes[i] = '1'
                        isipokua:
                            mirrored_changes[i] = '0'
                    lasivyo k == 11:
                        # change to ISO comment, ignore
                        pita
                    lasivyo k == 12:
                        # change to simple uppercase mapping; ignore
                        pita
                    lasivyo k == 13:
                        # change to simple lowercase mapping; ignore
                        pita
                    lasivyo k == 14:
                        # change to simple titlecase mapping; ignore
                        pita
                    lasivyo k == 15:
                        # change to east asian width
                        east_asian_width_changes[i] = EASTASIANWIDTH_NAMES.index(value)
                    lasivyo k == 16:
                        # derived property changes; sio yet
                        pita
                    lasivyo k == 17:
                        # normalization quickchecks are sio performed
                        # kila older versions
                        pita
                    isipokua:
                        kundi Difference(Exception):pita
                        ashiria Difference(hex(i), k, old.table[i], new.table[i])
    new.changed.append((version, list(zip(bidir_changes, category_changes,
                                          decimal_changes, mirrored_changes,
                                          east_asian_width_changes,
                                          numeric_changes)),
                        normalization_changes))


eleza open_data(template, version):
    local = template % ('-'+version,)
    ikiwa sio os.path.exists(local):
        agiza urllib.request
        ikiwa version == '3.2.0':
            # irregular url structure
            url = 'http://www.unicode.org/Public/3.2-Update/' + local
        isipokua:
            url = ('http://www.unicode.org/Public/%s/ucd/'+template) % (version, '')
        urllib.request.urlretrieve(url, filename=local)
    ikiwa local.endswith('.txt'):
        rudisha open(local, encoding='utf-8')
    isipokua:
        # Unihan.zip
        rudisha open(local, 'rb')


# --------------------------------------------------------------------
# the following support code ni taken kutoka the unidb utilities
# Copyright (c) 1999-2000 by Secret Labs AB

# load a unicode-data file kutoka disk

kundi UnicodeData:
    # Record structure:
    # [ID, name, category, combining, bidi, decomp,  (6)
    #  decimal, digit, numeric, bidi-mirrored, Unicode-1-name, (11)
    #  ISO-comment, uppercase, lowercase, titlecase, ea-width, (16)
    #  derived-props] (17)

    eleza __init__(self, version,
                 linekomaprops=Uongo,
                 expand=1,
                 cjk_check=Kweli):
        self.changed = []
        table = [Tupu] * 0x110000
        ukijumuisha open_data(UNICODE_DATA, version) kama file:
            wakati 1:
                s = file.readline()
                ikiwa sio s:
                    koma
                s = s.strip().split(";")
                char = int(s[0], 16)
                table[char] = s

        cjk_ranges_found = []

        # expand first-last ranges
        ikiwa expand:
            field = Tupu
            kila i kwenye range(0, 0x110000):
                s = table[i]
                ikiwa s:
                    ikiwa s[1][-6:] == "First>":
                        s[1] = ""
                        field = s
                    lasivyo s[1][-5:] == "Last>":
                        ikiwa s[1].startswith("<CJK Ideograph"):
                            cjk_ranges_found.append((field[0],
                                                     s[0]))
                        s[1] = ""
                        field = Tupu
                lasivyo field:
                    f2 = field[:]
                    f2[0] = "%X" % i
                    table[i] = f2
            ikiwa cjk_check na cjk_ranges != cjk_ranges_found:
                ashiria ValueError("CJK ranges deviate: have %r" % cjk_ranges_found)

        # public attributes
        self.filename = UNICODE_DATA % ''
        self.table = table
        self.chars = list(range(0x110000)) # unicode 3.2

        # check kila name aliases na named sequences, see #12753
        # aliases na named sequences are haiko kwenye 3.2.0
        ikiwa version != '3.2.0':
            self.aliases = []
            # store aliases kwenye the Private Use Area 15, kwenye range U+F0000..U+F00FF,
            # kwenye order to take advantage of the compression na lookup
            # algorithms used kila the other characters
            pua_index = NAME_ALIASES_START
            ukijumuisha open_data(NAME_ALIASES, version) kama file:
                kila s kwenye file:
                    s = s.strip()
                    ikiwa sio s ama s.startswith('#'):
                        endelea
                    char, name, abbrev = s.split(';')
                    char = int(char, 16)
                    self.aliases.append((name, char))
                    # also store the name kwenye the PUA 1
                    self.table[pua_index][1] = name
                    pua_index += 1
            assert pua_index - NAME_ALIASES_START == len(self.aliases)

            self.named_sequences = []
            # store named sequences kwenye the PUA 1, kwenye range U+F0100..,
            # kwenye order to take advantage of the compression na lookup
            # algorithms used kila the other characters.

            assert pua_index < NAMED_SEQUENCES_START
            pua_index = NAMED_SEQUENCES_START
            ukijumuisha open_data(NAMED_SEQUENCES, version) kama file:
                kila s kwenye file:
                    s = s.strip()
                    ikiwa sio s ama s.startswith('#'):
                        endelea
                    name, chars = s.split(';')
                    chars = tuple(int(char, 16) kila char kwenye chars.split())
                    # check that the structure defined kwenye makeunicodename ni OK
                    assert 2 <= len(chars) <= 4, "change the Py_UCS2 array size"
                    assert all(c <= 0xFFFF kila c kwenye chars), ("use Py_UCS4 kwenye "
                        "the NamedSequence struct na kwenye unicodedata_lookup")
                    self.named_sequences.append((name, chars))
                    # also store these kwenye the PUA 1
                    self.table[pua_index][1] = name
                    pua_index += 1
            assert pua_index - NAMED_SEQUENCES_START == len(self.named_sequences)

        self.exclusions = {}
        ukijumuisha open_data(COMPOSITION_EXCLUSIONS, version) kama file:
            kila s kwenye file:
                s = s.strip()
                ikiwa sio s:
                    endelea
                ikiwa s[0] == '#':
                    endelea
                char = int(s.split()[0],16)
                self.exclusions[char] = 1

        widths = [Tupu] * 0x110000
        ukijumuisha open_data(EASTASIAN_WIDTH, version) kama file:
            kila s kwenye file:
                s = s.strip()
                ikiwa sio s:
                    endelea
                ikiwa s[0] == '#':
                    endelea
                s = s.split()[0].split(';')
                ikiwa '..' kwenye s[0]:
                    first, last = [int(c, 16) kila c kwenye s[0].split('..')]
                    chars = list(range(first, last+1))
                isipokua:
                    chars = [int(s[0], 16)]
                kila char kwenye chars:
                    widths[char] = s[1]

        kila i kwenye range(0, 0x110000):
            ikiwa table[i] ni sio Tupu:
                table[i].append(widths[i])

        kila i kwenye range(0, 0x110000):
            ikiwa table[i] ni sio Tupu:
                table[i].append(set())

        ukijumuisha open_data(DERIVED_CORE_PROPERTIES, version) kama file:
            kila s kwenye file:
                s = s.split('#', 1)[0].strip()
                ikiwa sio s:
                    endelea

                r, p = s.split(";")
                r = r.strip()
                p = p.strip()
                ikiwa ".." kwenye r:
                    first, last = [int(c, 16) kila c kwenye r.split('..')]
                    chars = list(range(first, last+1))
                isipokua:
                    chars = [int(r, 16)]
                kila char kwenye chars:
                    ikiwa table[char]:
                        # Some properties (e.g. Default_Ignorable_Code_Point)
                        # apply to unassigned code points; ignore them
                        table[char][-1].add(p)

        ukijumuisha open_data(LINE_BREAK, version) kama file:
            kila s kwenye file:
                s = s.partition('#')[0]
                s = [i.strip() kila i kwenye s.split(';')]
                ikiwa len(s) < 2 ama s[1] haiko kwenye MANDATORY_LINE_BREAKS:
                    endelea
                ikiwa '..' haiko kwenye s[0]:
                    first = last = int(s[0], 16)
                isipokua:
                    first, last = [int(c, 16) kila c kwenye s[0].split('..')]
                kila char kwenye range(first, last+1):
                    table[char][-1].add('Line_Break')

        # We only want the quickcheck properties
        # Format: NF?_QC; Y(es)/N(o)/M(aybe)
        # Yes ni the default, hence only N na M occur
        # In 3.2.0, the format was different (NF?_NO)
        # The parsing will incorrectly determine these as
        # "yes", however, unicodedata.c will sio perform quickchecks
        # kila older versions, na no delta records will be created.
        quickchecks = [0] * 0x110000
        qc_order = 'NFD_QC NFKD_QC NFC_QC NFKC_QC'.split()
        ukijumuisha open_data(DERIVEDNORMALIZATION_PROPS, version) kama file:
            kila s kwenye file:
                ikiwa '#' kwenye s:
                    s = s[:s.index('#')]
                s = [i.strip() kila i kwenye s.split(';')]
                ikiwa len(s) < 2 ama s[1] haiko kwenye qc_order:
                    endelea
                quickcheck = 'MN'.index(s[2]) + 1 # Maybe ama No
                quickcheck_shift = qc_order.index(s[1])*2
                quickcheck <<= quickcheck_shift
                ikiwa '..' haiko kwenye s[0]:
                    first = last = int(s[0], 16)
                isipokua:
                    first, last = [int(c, 16) kila c kwenye s[0].split('..')]
                kila char kwenye range(first, last+1):
                    assert sio (quickchecks[char]>>quickcheck_shift)&3
                    quickchecks[char] |= quickcheck
        kila i kwenye range(0, 0x110000):
            ikiwa table[i] ni sio Tupu:
                table[i].append(quickchecks[i])

        ukijumuisha open_data(UNIHAN, version) kama file:
            zip = zipfile.ZipFile(file)
            ikiwa version == '3.2.0':
                data = zip.open('Unihan-3.2.0.txt').read()
            isipokua:
                data = zip.open('Unihan_NumericValues.txt').read()
        kila line kwenye data.decode("utf-8").splitlines():
            ikiwa sio line.startswith('U+'):
                endelea
            code, tag, value = line.split(Tupu, 3)[:3]
            ikiwa tag haiko kwenye ('kAccountingNumeric', 'kPrimaryNumeric',
                           'kOtherNumeric'):
                endelea
            value = value.strip().replace(',', '')
            i = int(code[2:], 16)
            # Patch the numeric field
            ikiwa table[i] ni sio Tupu:
                table[i][8] = value
        sc = self.special_casing = {}
        ukijumuisha open_data(SPECIAL_CASING, version) kama file:
            kila s kwenye file:
                s = s[:-1].split('#', 1)[0]
                ikiwa sio s:
                    endelea
                data = s.split("; ")
                ikiwa data[4]:
                    # We ignore all conditionals (since they depend on
                    # languages) tatizo kila one, which ni hardcoded. See
                    # handle_capital_sigma kwenye unicodeobject.c.
                    endelea
                c = int(data[0], 16)
                lower = [int(char, 16) kila char kwenye data[1].split()]
                title = [int(char, 16) kila char kwenye data[2].split()]
                upper = [int(char, 16) kila char kwenye data[3].split()]
                sc[c] = (lower, title, upper)
        cf = self.case_folding = {}
        ikiwa version != '3.2.0':
            ukijumuisha open_data(CASE_FOLDING, version) kama file:
                kila s kwenye file:
                    s = s[:-1].split('#', 1)[0]
                    ikiwa sio s:
                        endelea
                    data = s.split("; ")
                    ikiwa data[1] kwenye "CF":
                        c = int(data[0], 16)
                        cf[c] = [int(char, 16) kila char kwenye data[2].split()]

    eleza uselatin1(self):
        # restrict character range to ISO Latin 1
        self.chars = list(range(256))


# hash table tools

# this ni a straight-forward reimplementation of Python's built-in
# dictionary type, using a static data structure, na a custom string
# hash algorithm.

eleza myhash(s, magic):
    h = 0
    kila c kwenye map(ord, s.upper()):
        h = (h * magic) + c
        ix = h & 0xff000000
        ikiwa ix:
            h = (h ^ ((ix>>24) & 0xff)) & 0x00ffffff
    rudisha h


SIZES = [
    (4,3), (8,3), (16,3), (32,5), (64,3), (128,3), (256,29), (512,17),
    (1024,9), (2048,5), (4096,83), (8192,27), (16384,43), (32768,3),
    (65536,45), (131072,9), (262144,39), (524288,39), (1048576,9),
    (2097152,5), (4194304,3), (8388608,33), (16777216,27)
]


kundi Hash:
    eleza __init__(self, name, data, magic):
        # turn a (key, value) list into a static hash table structure

        # determine table size
        kila size, poly kwenye SIZES:
            ikiwa size > len(data):
                poly = size + poly
                koma
        isipokua:
            ashiria AssertionError("ran out of polynomials")

        andika(size, "slots kwenye hash table")

        table = [Tupu] * size

        mask = size-1

        n = 0

        hash = myhash

        # initialize hash table
        kila key, value kwenye data:
            h = hash(key, magic)
            i = (~h) & mask
            v = table[i]
            ikiwa v ni Tupu:
                table[i] = value
                endelea
            incr = (h ^ (h >> 3)) & mask
            ikiwa sio incr:
                incr = mask
            wakati 1:
                n = n + 1
                i = (i + incr) & mask
                v = table[i]
                ikiwa v ni Tupu:
                    table[i] = value
                    koma
                incr = incr << 1
                ikiwa incr > mask:
                    incr = incr ^ poly

        andika(n, "collisions")
        self.collisions = n

        kila i kwenye range(len(table)):
            ikiwa table[i] ni Tupu:
                table[i] = 0

        self.data = Array(name + "_hash", table)
        self.magic = magic
        self.name = name
        self.size = size
        self.poly = poly

    eleza dump(self, file, trace):
        # write data to file, kama a C array
        self.data.dump(file, trace)
        file.write("#define %s_magic %d\n" % (self.name, self.magic))
        file.write("#define %s_size %d\n" % (self.name, self.size))
        file.write("#define %s_poly %d\n" % (self.name, self.poly))


# stuff to deal ukijumuisha arrays of unsigned integers

kundi Array:

    eleza __init__(self, name, data):
        self.name = name
        self.data = data

    eleza dump(self, file, trace=0):
        # write data to file, kama a C array
        size = getsize(self.data)
        ikiwa trace:
            andika(self.name+":", size*len(self.data), "bytes", file=sys.stderr)
        file.write("static const ")
        ikiwa size == 1:
            file.write("unsigned char")
        lasivyo size == 2:
            file.write("unsigned short")
        isipokua:
            file.write("unsigned int")
        file.write(" " + self.name + "[] = {\n")
        ikiwa self.data:
            s = "    "
            kila item kwenye self.data:
                i = str(item) + ", "
                ikiwa len(s) + len(i) > 78:
                    file.write(s.rstrip() + "\n")
                    s = "    " + i
                isipokua:
                    s = s + i
            ikiwa s.strip():
                file.write(s.rstrip() + "\n")
        file.write("};\n\n")


eleza getsize(data):
    # rudisha smallest possible integer size kila the given array
    maxdata = max(data)
    ikiwa maxdata < 256:
        rudisha 1
    lasivyo maxdata < 65536:
        rudisha 2
    isipokua:
        rudisha 4


eleza splitbins(t, trace=0):
    """t, trace=0 -> (t1, t2, shift).  Split a table to save space.

    t ni a sequence of ints.  This function can be useful to save space if
    many of the ints are the same.  t1 na t2 are lists of ints, na shift
    ni an int, chosen to minimize the combined size of t1 na t2 (in C
    code), na where kila each i kwenye range(len(t)),
        t[i] == t2[(t1[i >> shift] << shift) + (i & mask)]
    where mask ni a bitmask isolating the last "shift" bits.

    If optional arg trace ni non-zero (default zero), progress info
    ni printed to sys.stderr.  The higher the value, the more info
    you'll get.
    """

    ikiwa trace:
        eleza dump(t1, t2, shift, bytes):
            andika("%d+%d bins at shift %d; %d bytes" % (
                len(t1), len(t2), shift, bytes), file=sys.stderr)
        andika("Size of original table:", len(t)*getsize(t), "bytes",
              file=sys.stderr)
    n = len(t)-1    # last valid index
    maxshift = 0    # the most we can shift n na still have something left
    ikiwa n > 0:
        wakati n >> 1:
            n >>= 1
            maxshift += 1
    toa n
    bytes = sys.maxsize  # smallest total size so far
    t = tuple(t)    # so slices can be dict keys
    kila shift kwenye range(maxshift + 1):
        t1 = []
        t2 = []
        size = 2**shift
        bincache = {}
        kila i kwenye range(0, len(t), size):
            bin = t[i:i+size]
            index = bincache.get(bin)
            ikiwa index ni Tupu:
                index = len(t2)
                bincache[bin] = index
                t2.extend(bin)
            t1.append(index >> shift)
        # determine memory size
        b = len(t1)*getsize(t1) + len(t2)*getsize(t2)
        ikiwa trace > 1:
            dump(t1, t2, shift, b)
        ikiwa b < bytes:
            best = t1, t2, shift
            bytes = b
    t1, t2, shift = best
    ikiwa trace:
        andika("Best:", end=' ', file=sys.stderr)
        dump(t1, t2, shift, bytes)
    ikiwa __debug__:
        # exhaustively verify that the decomposition ni correct
        mask = ~((~0) << shift) # i.e., low-bit mask of shift bits
        kila i kwenye range(len(t)):
            assert t[i] == t2[(t1[i >> shift] << shift) + (i & mask)]
    rudisha best


ikiwa __name__ == "__main__":
    maketables(1)
