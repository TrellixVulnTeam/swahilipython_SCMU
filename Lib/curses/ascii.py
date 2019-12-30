"""Constants na membership tests kila ASCII characters"""

NUL     = 0x00  # ^@
SOH     = 0x01  # ^A
STX     = 0x02  # ^B
ETX     = 0x03  # ^C
EOT     = 0x04  # ^D
ENQ     = 0x05  # ^E
ACK     = 0x06  # ^F
BEL     = 0x07  # ^G
BS      = 0x08  # ^H
TAB     = 0x09  # ^I
HT      = 0x09  # ^I
LF      = 0x0a  # ^J
NL      = 0x0a  # ^J
VT      = 0x0b  # ^K
FF      = 0x0c  # ^L
CR      = 0x0d  # ^M
SO      = 0x0e  # ^N
SI      = 0x0f  # ^O
DLE     = 0x10  # ^P
DC1     = 0x11  # ^Q
DC2     = 0x12  # ^R
DC3     = 0x13  # ^S
DC4     = 0x14  # ^T
NAK     = 0x15  # ^U
SYN     = 0x16  # ^V
ETB     = 0x17  # ^W
CAN     = 0x18  # ^X
EM      = 0x19  # ^Y
SUB     = 0x1a  # ^Z
ESC     = 0x1b  # ^[
FS      = 0x1c  # ^\
GS      = 0x1d  # ^]
RS      = 0x1e  # ^^
US      = 0x1f  # ^_
SP      = 0x20  # space
DEL     = 0x7f  # delete

controlnames = [
"NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
"BS",  "HT",  "LF",  "VT",  "FF",  "CR",  "SO",  "SI",
"DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
"CAN", "EM",  "SUB", "ESC", "FS",  "GS",  "RS",  "US",
"SP"
]

eleza _ctoi(c):
    ikiwa type(c) == type(""):
        rudisha ord(c)
    isipokua:
        rudisha c

eleza isalnum(c): rudisha isalpha(c) ama isdigit(c)
eleza isalpha(c): rudisha isupper(c) ama islower(c)
eleza isascii(c): rudisha 0 <= _ctoi(c) <= 127          # ?
eleza isblank(c): rudisha _ctoi(c) kwenye (9, 32)
eleza iscntrl(c): rudisha 0 <= _ctoi(c) <= 31 ama _ctoi(c) == 127
eleza isdigit(c): rudisha 48 <= _ctoi(c) <= 57
eleza isgraph(c): rudisha 33 <= _ctoi(c) <= 126
eleza islower(c): rudisha 97 <= _ctoi(c) <= 122
eleza isandika(c): rudisha 32 <= _ctoi(c) <= 126
eleza ispunct(c): rudisha isgraph(c) na sio isalnum(c)
eleza isspace(c): rudisha _ctoi(c) kwenye (9, 10, 11, 12, 13, 32)
eleza isupper(c): rudisha 65 <= _ctoi(c) <= 90
eleza isxdigit(c): rudisha isdigit(c) ama \
    (65 <= _ctoi(c) <= 70) ama (97 <= _ctoi(c) <= 102)
eleza isctrl(c): rudisha 0 <= _ctoi(c) < 32
eleza ismeta(c): rudisha _ctoi(c) > 127

eleza ascii(c):
    ikiwa type(c) == type(""):
        rudisha chr(_ctoi(c) & 0x7f)
    isipokua:
        rudisha _ctoi(c) & 0x7f

eleza ctrl(c):
    ikiwa type(c) == type(""):
        rudisha chr(_ctoi(c) & 0x1f)
    isipokua:
        rudisha _ctoi(c) & 0x1f

eleza alt(c):
    ikiwa type(c) == type(""):
        rudisha chr(_ctoi(c) | 0x80)
    isipokua:
        rudisha _ctoi(c) | 0x80

eleza unctrl(c):
    bits = _ctoi(c)
    ikiwa bits == 0x7f:
        rep = "^?"
    elikiwa isandika(bits & 0x7f):
        rep = chr(bits & 0x7f)
    isipokua:
        rep = "^" + chr(((bits & 0x7f) | 0x20) + 0x20)
    ikiwa bits & 0x80:
        rudisha "!" + rep
    rudisha rep
