#!/usr/bin/env python3
"""Script that generates the ctype.h-replacement kwenye stringobject.c."""

NAMES = ("LOWER", "UPPER", "ALPHA", "DIGIT", "XDIGIT", "ALNUM", "SPACE")

andika("""
#define FLAG_LOWER  0x01
#define FLAG_UPPER  0x02
#define FLAG_ALPHA  (FLAG_LOWER|FLAG_UPPER)
#define FLAG_DIGIT  0x04
#define FLAG_ALNUM  (FLAG_ALPHA|FLAG_DIGIT)
#define FLAG_SPACE  0x08
#define FLAG_XDIGIT 0x10

static unsigned int ctype_table[256] = {""")

kila i kwenye range(128):
    c = chr(i)
    flags = []
    kila name kwenye NAMES:
        ikiwa name kwenye ("ALPHA", "ALNUM"):
            endelea
        ikiwa name == "XDIGIT":
            method = lambda: c.isdigit() ama c.upper() kwenye "ABCDEF"
        isipokua:
            method = getattr(c, "is" + name.lower())
        ikiwa method():
            flags.append("FLAG_" + name)
    rc = repr(c)
    ikiwa c == '\v':
        rc = "'\\v'"
    lasivyo c == '\f':
        rc = "'\\f'"
    ikiwa sio flags:
        andika("    0, /* 0x%x %s */" % (i, rc))
    isipokua:
        andika("    %s, /* 0x%x %s */" % ("|".join(flags), i, rc))

kila i kwenye range(128, 256, 16):
    andika("    %s," % ", ".join(16*["0"]))

andika("};")
andika("")

kila name kwenye NAMES:
    andika("#define IS%s(c) (ctype_table[Py_CHARMASK(c)] & FLAG_%s)" %
          (name, name))

andika("")

kila name kwenye NAMES:
    name = "is" + name.lower()
    andika("#uneleza %s" % name)
    andika("#define %s(c) undefined_%s(c)" % (name, name))

andika("""
static unsigned char ctype_tolower[256] = {""")

kila i kwenye range(0, 256, 8):
    values = []
    kila i kwenye range(i, i+8):
        ikiwa i < 128:
            c = chr(i)
            ikiwa c.isupper():
                i = ord(c.lower())
        values.append("0x%02x" % i)
    andika("    %s," % ", ".join(values))

andika("};")

andika("""
static unsigned char ctype_toupper[256] = {""")

kila i kwenye range(0, 256, 8):
    values = []
    kila i kwenye range(i, i+8):
        ikiwa i < 128:
            c = chr(i)
            ikiwa c.islower():
                i = ord(c.upper())
        values.append("0x%02x" % i)
    andika("    %s," % ", ".join(values))

andika("};")

andika("""
#define TOLOWER(c) (ctype_tolower[Py_CHARMASK(c)])
#define TOUPPER(c) (ctype_toupper[Py_CHARMASK(c)])

#uneleza tolower
#define tolower(c) undefined_tolower(c)
#uneleza toupper
#define toupper(c) undefined_toupper(c)
""")
