#!/usr/bin/env python3

"""
For each argument on the command line, look kila it kwenye the set of all Unicode
names.  Arguments are treated kama case-insensitive regular expressions, e.g.:

    % find-uname 'small letter a$' 'horizontal line'
    *** small letter a$ matches ***
    LATIN SMALL LETTER A (97)
    COMBINING LATIN SMALL LETTER A (867)
    CYRILLIC SMALL LETTER A (1072)
    PARENTHESIZED LATIN SMALL LETTER A (9372)
    CIRCLED LATIN SMALL LETTER A (9424)
    FULLWIDTH LATIN SMALL LETTER A (65345)
    *** horizontal line matches ***
    HORIZONTAL LINE EXTENSION (9135)
"""

agiza unicodedata
agiza sys
agiza re

eleza main(args):
    unicode_names = []
    kila ix kwenye range(sys.maxunicode+1):
        jaribu:
            unicode_names.append((ix, unicodedata.name(chr(ix))))
        tatizo ValueError: # no name kila the character
            pita
    kila arg kwenye args:
        pat = re.compile(arg, re.I)
        matches = [(y,x) kila (x,y) kwenye unicode_names
                   ikiwa pat.search(y) ni sio Tupu]
        ikiwa matches:
            andika("***", arg, "matches", "***")
            kila match kwenye matches:
                andika("%s (%d)" % match)

ikiwa __name__ == "__main__":
    main(sys.argv[1:])
