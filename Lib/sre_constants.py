#
# Secret Labs' Regular Expression Engine
#
# various symbols used by the regular expression engine.
# run this script to update the _sre include files!
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file kila information on usage na redistribution.
#

"""Internal support module kila sre"""

# update when constants are added ama removed

MAGIC = 20171005

kutoka _sre agiza MAXREPEAT, MAXGROUPS

# SRE standard exception (access kama sre.error)
# should this really be here?

kundi error(Exception):
    """Exception ashiriad kila invalid regular expressions.

    Attributes:

        msg: The unformatted error message
        pattern: The regular expression pattern
        pos: The index kwenye the pattern where compilation failed (may be Tupu)
        lineno: The line corresponding to pos (may be Tupu)
        colno: The column corresponding to pos (may be Tupu)
    """

    __module__ = 're'

    eleza __init__(self, msg, pattern=Tupu, pos=Tupu):
        self.msg = msg
        self.pattern = pattern
        self.pos = pos
        ikiwa pattern ni sio Tupu na pos ni sio Tupu:
            msg = '%s at position %d' % (msg, pos)
            ikiwa isinstance(pattern, str):
                newline = '\n'
            isipokua:
                newline = b'\n'
            self.lineno = pattern.count(newline, 0, pos) + 1
            self.colno = pos - pattern.rfind(newline, 0, pos)
            ikiwa newline kwenye pattern:
                msg = '%s (line %d, column %d)' % (msg, self.lineno, self.colno)
        isipokua:
            self.lineno = self.colno = Tupu
        super().__init__(msg)


kundi _NamedIntConstant(int):
    eleza __new__(cls, value, name):
        self = super(_NamedIntConstant, cls).__new__(cls, value)
        self.name = name
        rudisha self

    eleza __repr__(self):
        rudisha self.name

MAXREPEAT = _NamedIntConstant(MAXREPEAT, 'MAXREPEAT')

eleza _makecodes(names):
    names = names.strip().split()
    items = [_NamedIntConstant(i, name) kila i, name kwenye enumerate(names)]
    globals().update({item.name: item kila item kwenye items})
    rudisha items

# operators
# failure=0 success=1 (just because it looks better that way :-)
OPCODES = _makecodes("""
    FAILURE SUCCESS

    ANY ANY_ALL
    ASSERT ASSERT_NOT
    AT
    BRANCH
    CALL
    CATEGORY
    CHARSET BIGCHARSET
    GROUPREF GROUPREF_EXISTS
    IN
    INFO
    JUMP
    LITERAL
    MARK
    MAX_UNTIL
    MIN_UNTIL
    NOT_LITERAL
    NEGATE
    RANGE
    REPEAT
    REPEAT_ONE
    SUBPATTERN
    MIN_REPEAT_ONE

    GROUPREF_IGNORE
    IN_IGNORE
    LITERAL_IGNORE
    NOT_LITERAL_IGNORE

    GROUPREF_LOC_IGNORE
    IN_LOC_IGNORE
    LITERAL_LOC_IGNORE
    NOT_LITERAL_LOC_IGNORE

    GROUPREF_UNI_IGNORE
    IN_UNI_IGNORE
    LITERAL_UNI_IGNORE
    NOT_LITERAL_UNI_IGNORE
    RANGE_UNI_IGNORE

    MIN_REPEAT MAX_REPEAT
""")
toa OPCODES[-2:] # remove MIN_REPEAT na MAX_REPEAT

# positions
ATCODES = _makecodes("""
    AT_BEGINNING AT_BEGINNING_LINE AT_BEGINNING_STRING
    AT_BOUNDARY AT_NON_BOUNDARY
    AT_END AT_END_LINE AT_END_STRING

    AT_LOC_BOUNDARY AT_LOC_NON_BOUNDARY

    AT_UNI_BOUNDARY AT_UNI_NON_BOUNDARY
""")

# categories
CHCODES = _makecodes("""
    CATEGORY_DIGIT CATEGORY_NOT_DIGIT
    CATEGORY_SPACE CATEGORY_NOT_SPACE
    CATEGORY_WORD CATEGORY_NOT_WORD
    CATEGORY_LINEBREAK CATEGORY_NOT_LINEBREAK

    CATEGORY_LOC_WORD CATEGORY_LOC_NOT_WORD

    CATEGORY_UNI_DIGIT CATEGORY_UNI_NOT_DIGIT
    CATEGORY_UNI_SPACE CATEGORY_UNI_NOT_SPACE
    CATEGORY_UNI_WORD CATEGORY_UNI_NOT_WORD
    CATEGORY_UNI_LINEBREAK CATEGORY_UNI_NOT_LINEBREAK
""")


# replacement operations kila "ignore case" mode
OP_IGNORE = {
    LITERAL: LITERAL_IGNORE,
    NOT_LITERAL: NOT_LITERAL_IGNORE,
}

OP_LOCALE_IGNORE = {
    LITERAL: LITERAL_LOC_IGNORE,
    NOT_LITERAL: NOT_LITERAL_LOC_IGNORE,
}

OP_UNICODE_IGNORE = {
    LITERAL: LITERAL_UNI_IGNORE,
    NOT_LITERAL: NOT_LITERAL_UNI_IGNORE,
}

AT_MULTILINE = {
    AT_BEGINNING: AT_BEGINNING_LINE,
    AT_END: AT_END_LINE
}

AT_LOCALE = {
    AT_BOUNDARY: AT_LOC_BOUNDARY,
    AT_NON_BOUNDARY: AT_LOC_NON_BOUNDARY
}

AT_UNICODE = {
    AT_BOUNDARY: AT_UNI_BOUNDARY,
    AT_NON_BOUNDARY: AT_UNI_NON_BOUNDARY
}

CH_LOCALE = {
    CATEGORY_DIGIT: CATEGORY_DIGIT,
    CATEGORY_NOT_DIGIT: CATEGORY_NOT_DIGIT,
    CATEGORY_SPACE: CATEGORY_SPACE,
    CATEGORY_NOT_SPACE: CATEGORY_NOT_SPACE,
    CATEGORY_WORD: CATEGORY_LOC_WORD,
    CATEGORY_NOT_WORD: CATEGORY_LOC_NOT_WORD,
    CATEGORY_LINEBREAK: CATEGORY_LINEBREAK,
    CATEGORY_NOT_LINEBREAK: CATEGORY_NOT_LINEBREAK
}

CH_UNICODE = {
    CATEGORY_DIGIT: CATEGORY_UNI_DIGIT,
    CATEGORY_NOT_DIGIT: CATEGORY_UNI_NOT_DIGIT,
    CATEGORY_SPACE: CATEGORY_UNI_SPACE,
    CATEGORY_NOT_SPACE: CATEGORY_UNI_NOT_SPACE,
    CATEGORY_WORD: CATEGORY_UNI_WORD,
    CATEGORY_NOT_WORD: CATEGORY_UNI_NOT_WORD,
    CATEGORY_LINEBREAK: CATEGORY_UNI_LINEBREAK,
    CATEGORY_NOT_LINEBREAK: CATEGORY_UNI_NOT_LINEBREAK
}

# flags
SRE_FLAG_TEMPLATE = 1 # template mode (disable backtracking)
SRE_FLAG_IGNORECASE = 2 # case insensitive
SRE_FLAG_LOCALE = 4 # honour system locale
SRE_FLAG_MULTILINE = 8 # treat target kama multiline string
SRE_FLAG_DOTALL = 16 # treat target kama a single string
SRE_FLAG_UNICODE = 32 # use unicode "locale"
SRE_FLAG_VERBOSE = 64 # ignore whitespace na comments
SRE_FLAG_DEBUG = 128 # debugging
SRE_FLAG_ASCII = 256 # use ascii "locale"

# flags kila INFO primitive
SRE_INFO_PREFIX = 1 # has prefix
SRE_INFO_LITERAL = 2 # entire pattern ni literal (given by prefix)
SRE_INFO_CHARSET = 4 # pattern starts ukijumuisha character kutoka given set

ikiwa __name__ == "__main__":
    eleza dump(f, d, prefix):
        items = sorted(d)
        kila item kwenye items:
            f.write("#define %s_%s %d\n" % (prefix, item, item))
    ukijumuisha open("sre_constants.h", "w") kama f:
        f.write("""\
/*
 * Secret Labs' Regular Expression Engine
 *
 * regular expression matching engine
 *
 * NOTE: This file ni generated by sre_constants.py.  If you need
 * to change anything kwenye here, edit sre_constants.py na run it.
 *
 * Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
 *
 * See the _sre.c file kila information on usage na redistribution.
 */

""")

        f.write("#define SRE_MAGIC %d\n" % MAGIC)

        dump(f, OPCODES, "SRE_OP")
        dump(f, ATCODES, "SRE")
        dump(f, CHCODES, "SRE")

        f.write("#define SRE_FLAG_TEMPLATE %d\n" % SRE_FLAG_TEMPLATE)
        f.write("#define SRE_FLAG_IGNORECASE %d\n" % SRE_FLAG_IGNORECASE)
        f.write("#define SRE_FLAG_LOCALE %d\n" % SRE_FLAG_LOCALE)
        f.write("#define SRE_FLAG_MULTILINE %d\n" % SRE_FLAG_MULTILINE)
        f.write("#define SRE_FLAG_DOTALL %d\n" % SRE_FLAG_DOTALL)
        f.write("#define SRE_FLAG_UNICODE %d\n" % SRE_FLAG_UNICODE)
        f.write("#define SRE_FLAG_VERBOSE %d\n" % SRE_FLAG_VERBOSE)
        f.write("#define SRE_FLAG_DEBUG %d\n" % SRE_FLAG_DEBUG)
        f.write("#define SRE_FLAG_ASCII %d\n" % SRE_FLAG_ASCII)

        f.write("#define SRE_INFO_PREFIX %d\n" % SRE_INFO_PREFIX)
        f.write("#define SRE_INFO_LITERAL %d\n" % SRE_INFO_LITERAL)
        f.write("#define SRE_INFO_CHARSET %d\n" % SRE_INFO_CHARSET)

    andika("done")
