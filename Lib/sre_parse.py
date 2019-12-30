#
# Secret Labs' Regular Expression Engine
#
# convert re-style regular expression to sre pattern
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file kila information on usage na redistribution.
#

"""Internal support module kila sre"""

# XXX: show string offset na offending character kila all errors

kutoka sre_constants agiza *

SPECIAL_CHARS = ".\\[{()*+?^$|"
REPEAT_CHARS = "*+?{"

DIGITS = frozenset("0123456789")

OCTDIGITS = frozenset("01234567")
HEXDIGITS = frozenset("0123456789abcdefABCDEF")
ASCIILETTERS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

WHITESPACE = frozenset(" \t\n\r\v\f")

_REPEATCODES = frozenset({MIN_REPEAT, MAX_REPEAT})
_UNITCODES = frozenset({ANY, RANGE, IN, LITERAL, NOT_LITERAL, CATEGORY})

ESCAPES = {
    r"\a": (LITERAL, ord("\a")),
    r"\b": (LITERAL, ord("\b")),
    r"\f": (LITERAL, ord("\f")),
    r"\n": (LITERAL, ord("\n")),
    r"\r": (LITERAL, ord("\r")),
    r"\t": (LITERAL, ord("\t")),
    r"\v": (LITERAL, ord("\v")),
    r"\\": (LITERAL, ord("\\"))
}

CATEGORIES = {
    r"\A": (AT, AT_BEGINNING_STRING), # start of string
    r"\b": (AT, AT_BOUNDARY),
    r"\B": (AT, AT_NON_BOUNDARY),
    r"\d": (IN, [(CATEGORY, CATEGORY_DIGIT)]),
    r"\D": (IN, [(CATEGORY, CATEGORY_NOT_DIGIT)]),
    r"\s": (IN, [(CATEGORY, CATEGORY_SPACE)]),
    r"\S": (IN, [(CATEGORY, CATEGORY_NOT_SPACE)]),
    r"\w": (IN, [(CATEGORY, CATEGORY_WORD)]),
    r"\W": (IN, [(CATEGORY, CATEGORY_NOT_WORD)]),
    r"\Z": (AT, AT_END_STRING), # end of string
}

FLAGS = {
    # standard flags
    "i": SRE_FLAG_IGNORECASE,
    "L": SRE_FLAG_LOCALE,
    "m": SRE_FLAG_MULTILINE,
    "s": SRE_FLAG_DOTALL,
    "x": SRE_FLAG_VERBOSE,
    # extensions
    "a": SRE_FLAG_ASCII,
    "t": SRE_FLAG_TEMPLATE,
    "u": SRE_FLAG_UNICODE,
}

TYPE_FLAGS = SRE_FLAG_ASCII | SRE_FLAG_LOCALE | SRE_FLAG_UNICODE
GLOBAL_FLAGS = SRE_FLAG_DEBUG | SRE_FLAG_TEMPLATE

kundi Verbose(Exception):
    pita

kundi State:
    # keeps track of state kila parsing
    eleza __init__(self):
        self.flags = 0
        self.groupdict = {}
        self.groupwidths = [Tupu]  # group 0
        self.lookbehindgroups = Tupu
    @property
    eleza groups(self):
        rudisha len(self.groupwidths)
    eleza opengroup(self, name=Tupu):
        gid = self.groups
        self.groupwidths.append(Tupu)
        ikiwa self.groups > MAXGROUPS:
            ashiria error("too many groups")
        ikiwa name ni sio Tupu:
            ogid = self.groupdict.get(name, Tupu)
            ikiwa ogid ni sio Tupu:
                ashiria error("redefinition of group name %r kama group %d; "
                            "was group %d" % (name, gid,  ogid))
            self.groupdict[name] = gid
        rudisha gid
    eleza closegroup(self, gid, p):
        self.groupwidths[gid] = p.getwidth()
    eleza checkgroup(self, gid):
        rudisha gid < self.groups na self.groupwidths[gid] ni sio Tupu

    eleza checklookbehindgroup(self, gid, source):
        ikiwa self.lookbehindgroups ni sio Tupu:
            ikiwa sio self.checkgroup(gid):
                ashiria source.error('cannot refer to an open group')
            ikiwa gid >= self.lookbehindgroups:
                ashiria source.error('cannot refer to group defined kwenye the same '
                                   'lookbehind subpattern')

kundi SubPattern:
    # a subpattern, kwenye intermediate form
    eleza __init__(self, state, data=Tupu):
        self.state = state
        ikiwa data ni Tupu:
            data = []
        self.data = data
        self.width = Tupu

    eleza dump(self, level=0):
        nl = Kweli
        seqtypes = (tuple, list)
        kila op, av kwenye self.data:
            andika(level*"  " + str(op), end='')
            ikiwa op ni IN:
                # member sublanguage
                andika()
                kila op, a kwenye av:
                    andika((level+1)*"  " + str(op), a)
            lasivyo op ni BRANCH:
                andika()
                kila i, a kwenye enumerate(av[1]):
                    ikiwa i:
                        andika(level*"  " + "OR")
                    a.dump(level+1)
            lasivyo op ni GROUPREF_EXISTS:
                condgroup, item_yes, item_no = av
                andika('', condgroup)
                item_yes.dump(level+1)
                ikiwa item_no:
                    andika(level*"  " + "ELSE")
                    item_no.dump(level+1)
            lasivyo isinstance(av, seqtypes):
                nl = Uongo
                kila a kwenye av:
                    ikiwa isinstance(a, SubPattern):
                        ikiwa sio nl:
                            andika()
                        a.dump(level+1)
                        nl = Kweli
                    isipokua:
                        ikiwa sio nl:
                            andika(' ', end='')
                        andika(a, end='')
                        nl = Uongo
                ikiwa sio nl:
                    andika()
            isipokua:
                andika('', av)
    eleza __repr__(self):
        rudisha repr(self.data)
    eleza __len__(self):
        rudisha len(self.data)
    eleza __delitem__(self, index):
        toa self.data[index]
    eleza __getitem__(self, index):
        ikiwa isinstance(index, slice):
            rudisha SubPattern(self.state, self.data[index])
        rudisha self.data[index]
    eleza __setitem__(self, index, code):
        self.data[index] = code
    eleza insert(self, index, code):
        self.data.insert(index, code)
    eleza append(self, code):
        self.data.append(code)
    eleza getwidth(self):
        # determine the width (min, max) kila this subpattern
        ikiwa self.width ni sio Tupu:
            rudisha self.width
        lo = hi = 0
        kila op, av kwenye self.data:
            ikiwa op ni BRANCH:
                i = MAXREPEAT - 1
                j = 0
                kila av kwenye av[1]:
                    l, h = av.getwidth()
                    i = min(i, l)
                    j = max(j, h)
                lo = lo + i
                hi = hi + j
            lasivyo op ni CALL:
                i, j = av.getwidth()
                lo = lo + i
                hi = hi + j
            lasivyo op ni SUBPATTERN:
                i, j = av[-1].getwidth()
                lo = lo + i
                hi = hi + j
            lasivyo op kwenye _REPEATCODES:
                i, j = av[2].getwidth()
                lo = lo + i * av[0]
                hi = hi + j * av[1]
            lasivyo op kwenye _UNITCODES:
                lo = lo + 1
                hi = hi + 1
            lasivyo op ni GROUPREF:
                i, j = self.state.groupwidths[av]
                lo = lo + i
                hi = hi + j
            lasivyo op ni GROUPREF_EXISTS:
                i, j = av[1].getwidth()
                ikiwa av[2] ni sio Tupu:
                    l, h = av[2].getwidth()
                    i = min(i, l)
                    j = max(j, h)
                isipokua:
                    i = 0
                lo = lo + i
                hi = hi + j
            lasivyo op ni SUCCESS:
                koma
        self.width = min(lo, MAXREPEAT - 1), min(hi, MAXREPEAT)
        rudisha self.width

kundi Tokenizer:
    eleza __init__(self, string):
        self.istext = isinstance(string, str)
        self.string = string
        ikiwa sio self.istext:
            string = str(string, 'latin1')
        self.decoded_string = string
        self.index = 0
        self.next = Tupu
        self.__next()
    eleza __next(self):
        index = self.index
        jaribu:
            char = self.decoded_string[index]
        tatizo IndexError:
            self.next = Tupu
            rudisha
        ikiwa char == "\\":
            index += 1
            jaribu:
                char += self.decoded_string[index]
            tatizo IndexError:
                ashiria error("bad escape (end of pattern)",
                            self.string, len(self.string) - 1) kutoka Tupu
        self.index = index + 1
        self.next = char
    eleza match(self, char):
        ikiwa char == self.next:
            self.__next()
            rudisha Kweli
        rudisha Uongo
    eleza get(self):
        this = self.next
        self.__next()
        rudisha this
    eleza getwhile(self, n, charset):
        result = ''
        kila _ kwenye range(n):
            c = self.next
            ikiwa c haiko kwenye charset:
                koma
            result += c
            self.__next()
        rudisha result
    eleza getuntil(self, terminator, name):
        result = ''
        wakati Kweli:
            c = self.next
            self.__next()
            ikiwa c ni Tupu:
                ikiwa sio result:
                    ashiria self.error("missing " + name)
                ashiria self.error("missing %s, unterminated name" % terminator,
                                 len(result))
            ikiwa c == terminator:
                ikiwa sio result:
                    ashiria self.error("missing " + name, 1)
                koma
            result += c
        rudisha result
    @property
    eleza pos(self):
        rudisha self.index - len(self.next ama '')
    eleza tell(self):
        rudisha self.index - len(self.next ama '')
    eleza seek(self, index):
        self.index = index
        self.__next()

    eleza error(self, msg, offset=0):
        rudisha error(msg, self.string, self.tell() - offset)

eleza _class_escape(source, escape):
    # handle escape code inside character class
    code = ESCAPES.get(escape)
    ikiwa code:
        rudisha code
    code = CATEGORIES.get(escape)
    ikiwa code na code[0] ni IN:
        rudisha code
    jaribu:
        c = escape[1:2]
        ikiwa c == "x":
            # hexadecimal escape (exactly two digits)
            escape += source.getwhile(2, HEXDIGITS)
            ikiwa len(escape) != 4:
                ashiria source.error("incomplete escape %s" % escape, len(escape))
            rudisha LITERAL, int(escape[2:], 16)
        lasivyo c == "u" na source.istext:
            # unicode escape (exactly four digits)
            escape += source.getwhile(4, HEXDIGITS)
            ikiwa len(escape) != 6:
                ashiria source.error("incomplete escape %s" % escape, len(escape))
            rudisha LITERAL, int(escape[2:], 16)
        lasivyo c == "U" na source.istext:
            # unicode escape (exactly eight digits)
            escape += source.getwhile(8, HEXDIGITS)
            ikiwa len(escape) != 10:
                ashiria source.error("incomplete escape %s" % escape, len(escape))
            c = int(escape[2:], 16)
            chr(c) # ashiria ValueError kila invalid code
            rudisha LITERAL, c
        lasivyo c == "N" na source.istext:
            agiza unicodedata
            # named unicode escape e.g. \N{EM DASH}
            ikiwa sio source.match('{'):
                ashiria source.error("missing {")
            charname = source.getuntil('}', 'character name')
            jaribu:
                c = ord(unicodedata.lookup(charname))
            tatizo KeyError:
                ashiria source.error("undefined character name %r" % charname,
                                   len(charname) + len(r'\N{}'))
            rudisha LITERAL, c
        lasivyo c kwenye OCTDIGITS:
            # octal escape (up to three digits)
            escape += source.getwhile(2, OCTDIGITS)
            c = int(escape[1:], 8)
            ikiwa c > 0o377:
                ashiria source.error('octal escape value %s outside of '
                                   'range 0-0o377' % escape, len(escape))
            rudisha LITERAL, c
        lasivyo c kwenye DIGITS:
            ashiria ValueError
        ikiwa len(escape) == 2:
            ikiwa c kwenye ASCIILETTERS:
                ashiria source.error('bad escape %s' % escape, len(escape))
            rudisha LITERAL, ord(escape[1])
    tatizo ValueError:
        pita
    ashiria source.error("bad escape %s" % escape, len(escape))

eleza _escape(source, escape, state):
    # handle escape code kwenye expression
    code = CATEGORIES.get(escape)
    ikiwa code:
        rudisha code
    code = ESCAPES.get(escape)
    ikiwa code:
        rudisha code
    jaribu:
        c = escape[1:2]
        ikiwa c == "x":
            # hexadecimal escape
            escape += source.getwhile(2, HEXDIGITS)
            ikiwa len(escape) != 4:
                ashiria source.error("incomplete escape %s" % escape, len(escape))
            rudisha LITERAL, int(escape[2:], 16)
        lasivyo c == "u" na source.istext:
            # unicode escape (exactly four digits)
            escape += source.getwhile(4, HEXDIGITS)
            ikiwa len(escape) != 6:
                ashiria source.error("incomplete escape %s" % escape, len(escape))
            rudisha LITERAL, int(escape[2:], 16)
        lasivyo c == "U" na source.istext:
            # unicode escape (exactly eight digits)
            escape += source.getwhile(8, HEXDIGITS)
            ikiwa len(escape) != 10:
                ashiria source.error("incomplete escape %s" % escape, len(escape))
            c = int(escape[2:], 16)
            chr(c) # ashiria ValueError kila invalid code
            rudisha LITERAL, c
        lasivyo c == "N" na source.istext:
            agiza unicodedata
            # named unicode escape e.g. \N{EM DASH}
            ikiwa sio source.match('{'):
                ashiria source.error("missing {")
            charname = source.getuntil('}', 'character name')
            jaribu:
                c = ord(unicodedata.lookup(charname))
            tatizo KeyError:
                ashiria source.error("undefined character name %r" % charname,
                                   len(charname) + len(r'\N{}'))
            rudisha LITERAL, c
        lasivyo c == "0":
            # octal escape
            escape += source.getwhile(2, OCTDIGITS)
            rudisha LITERAL, int(escape[1:], 8)
        lasivyo c kwenye DIGITS:
            # octal escape *or* decimal group reference (sigh)
            ikiwa source.next kwenye DIGITS:
                escape += source.get()
                ikiwa (escape[1] kwenye OCTDIGITS na escape[2] kwenye OCTDIGITS na
                    source.next kwenye OCTDIGITS):
                    # got three octal digits; this ni an octal escape
                    escape += source.get()
                    c = int(escape[1:], 8)
                    ikiwa c > 0o377:
                        ashiria source.error('octal escape value %s outside of '
                                           'range 0-0o377' % escape,
                                           len(escape))
                    rudisha LITERAL, c
            # sio an octal escape, so this ni a group reference
            group = int(escape[1:])
            ikiwa group < state.groups:
                ikiwa sio state.checkgroup(group):
                    ashiria source.error("cannot refer to an open group",
                                       len(escape))
                state.checklookbehindgroup(group, source)
                rudisha GROUPREF, group
            ashiria source.error("invalid group reference %d" % group, len(escape) - 1)
        ikiwa len(escape) == 2:
            ikiwa c kwenye ASCIILETTERS:
                ashiria source.error("bad escape %s" % escape, len(escape))
            rudisha LITERAL, ord(escape[1])
    tatizo ValueError:
        pita
    ashiria source.error("bad escape %s" % escape, len(escape))

eleza _uniq(items):
    rudisha list(dict.kutokakeys(items))

eleza _parse_sub(source, state, verbose, nested):
    # parse an alternation: a|b|c

    items = []
    itemsappend = items.append
    sourcematch = source.match
    start = source.tell()
    wakati Kweli:
        itemsappend(_parse(source, state, verbose, nested + 1,
                           sio nested na sio items))
        ikiwa sio sourcematch("|"):
            koma

    ikiwa len(items) == 1:
        rudisha items[0]

    subpattern = SubPattern(state)

    # check ikiwa all items share a common prefix
    wakati Kweli:
        prefix = Tupu
        kila item kwenye items:
            ikiwa sio item:
                koma
            ikiwa prefix ni Tupu:
                prefix = item[0]
            lasivyo item[0] != prefix:
                koma
        isipokua:
            # all subitems start ukijumuisha a common "prefix".
            # move it out of the branch
            kila item kwenye items:
                toa item[0]
            subpattern.append(prefix)
            endelea # check next one
        koma

    # check ikiwa the branch can be replaced by a character set
    set = []
    kila item kwenye items:
        ikiwa len(item) != 1:
            koma
        op, av = item[0]
        ikiwa op ni LITERAL:
            set.append((op, av))
        lasivyo op ni IN na av[0][0] ni sio NEGATE:
            set.extend(av)
        isipokua:
            koma
    isipokua:
        # we can store this kama a character set instead of a
        # branch (the compiler may optimize this even more)
        subpattern.append((IN, _uniq(set)))
        rudisha subpattern

    subpattern.append((BRANCH, (Tupu, items)))
    rudisha subpattern

eleza _parse(source, state, verbose, nested, first=Uongo):
    # parse a simple pattern
    subpattern = SubPattern(state)

    # precompute constants into local variables
    subpatternappend = subpattern.append
    sourceget = source.get
    sourcematch = source.match
    _len = len
    _ord = ord

    wakati Kweli:

        this = source.next
        ikiwa this ni Tupu:
            koma # end of pattern
        ikiwa this kwenye "|)":
            koma # end of subpattern
        sourceget()

        ikiwa verbose:
            # skip whitespace na comments
            ikiwa this kwenye WHITESPACE:
                endelea
            ikiwa this == "#":
                wakati Kweli:
                    this = sourceget()
                    ikiwa this ni Tupu ama this == "\n":
                        koma
                endelea

        ikiwa this[0] == "\\":
            code = _escape(source, this, state)
            subpatternappend(code)

        lasivyo this haiko kwenye SPECIAL_CHARS:
            subpatternappend((LITERAL, _ord(this)))

        lasivyo this == "[":
            here = source.tell() - 1
            # character set
            set = []
            setappend = set.append
##          ikiwa sourcematch(":"):
##              pita # handle character classes
            ikiwa source.next == '[':
                agiza warnings
                warnings.warn(
                    'Possible nested set at position %d' % source.tell(),
                    FutureWarning, stacklevel=nested + 6
                )
            negate = sourcematch("^")
            # check remaining characters
            wakati Kweli:
                this = sourceget()
                ikiwa this ni Tupu:
                    ashiria source.error("unterminated character set",
                                       source.tell() - here)
                ikiwa this == "]" na set:
                    koma
                lasivyo this[0] == "\\":
                    code1 = _class_escape(source, this)
                isipokua:
                    ikiwa set na this kwenye '-&~|' na source.next == this:
                        agiza warnings
                        warnings.warn(
                            'Possible set %s at position %d' % (
                                'difference' ikiwa this == '-' isipokua
                                'intersection' ikiwa this == '&' isipokua
                                'symmetric difference' ikiwa this == '~' isipokua
                                'union',
                                source.tell() - 1),
                            FutureWarning, stacklevel=nested + 6
                        )
                    code1 = LITERAL, _ord(this)
                ikiwa sourcematch("-"):
                    # potential range
                    that = sourceget()
                    ikiwa that ni Tupu:
                        ashiria source.error("unterminated character set",
                                           source.tell() - here)
                    ikiwa that == "]":
                        ikiwa code1[0] ni IN:
                            code1 = code1[1][0]
                        setappend(code1)
                        setappend((LITERAL, _ord("-")))
                        koma
                    ikiwa that[0] == "\\":
                        code2 = _class_escape(source, that)
                    isipokua:
                        ikiwa that == '-':
                            agiza warnings
                            warnings.warn(
                                'Possible set difference at position %d' % (
                                    source.tell() - 2),
                                FutureWarning, stacklevel=nested + 6
                            )
                        code2 = LITERAL, _ord(that)
                    ikiwa code1[0] != LITERAL ama code2[0] != LITERAL:
                        msg = "bad character range %s-%s" % (this, that)
                        ashiria source.error(msg, len(this) + 1 + len(that))
                    lo = code1[1]
                    hi = code2[1]
                    ikiwa hi < lo:
                        msg = "bad character range %s-%s" % (this, that)
                        ashiria source.error(msg, len(this) + 1 + len(that))
                    setappend((RANGE, (lo, hi)))
                isipokua:
                    ikiwa code1[0] ni IN:
                        code1 = code1[1][0]
                    setappend(code1)

            set = _uniq(set)
            # XXX: <fl> should move set optimization to compiler!
            ikiwa _len(set) == 1 na set[0][0] ni LITERAL:
                # optimization
                ikiwa negate:
                    subpatternappend((NOT_LITERAL, set[0][1]))
                isipokua:
                    subpatternappend(set[0])
            isipokua:
                ikiwa negate:
                    set.insert(0, (NEGATE, Tupu))
                # charmap optimization can't be added here because
                # global flags still are sio known
                subpatternappend((IN, set))

        lasivyo this kwenye REPEAT_CHARS:
            # repeat previous item
            here = source.tell()
            ikiwa this == "?":
                min, max = 0, 1
            lasivyo this == "*":
                min, max = 0, MAXREPEAT

            lasivyo this == "+":
                min, max = 1, MAXREPEAT
            lasivyo this == "{":
                ikiwa source.next == "}":
                    subpatternappend((LITERAL, _ord(this)))
                    endelea

                min, max = 0, MAXREPEAT
                lo = hi = ""
                wakati source.next kwenye DIGITS:
                    lo += sourceget()
                ikiwa sourcematch(","):
                    wakati source.next kwenye DIGITS:
                        hi += sourceget()
                isipokua:
                    hi = lo
                ikiwa sio sourcematch("}"):
                    subpatternappend((LITERAL, _ord(this)))
                    source.seek(here)
                    endelea

                ikiwa lo:
                    min = int(lo)
                    ikiwa min >= MAXREPEAT:
                        ashiria OverflowError("the repetition number ni too large")
                ikiwa hi:
                    max = int(hi)
                    ikiwa max >= MAXREPEAT:
                        ashiria OverflowError("the repetition number ni too large")
                    ikiwa max < min:
                        ashiria source.error("min repeat greater than max repeat",
                                           source.tell() - here)
            isipokua:
                ashiria AssertionError("unsupported quantifier %r" % (char,))
            # figure out which item to repeat
            ikiwa subpattern:
                item = subpattern[-1:]
            isipokua:
                item = Tupu
            ikiwa sio item ama item[0][0] ni AT:
                ashiria source.error("nothing to repeat",
                                   source.tell() - here + len(this))
            ikiwa item[0][0] kwenye _REPEATCODES:
                ashiria source.error("multiple repeat",
                                   source.tell() - here + len(this))
            ikiwa item[0][0] ni SUBPATTERN:
                group, add_flags, del_flags, p = item[0][1]
                ikiwa group ni Tupu na sio add_flags na sio del_flags:
                    item = p
            ikiwa sourcematch("?"):
                subpattern[-1] = (MIN_REPEAT, (min, max, item))
            isipokua:
                subpattern[-1] = (MAX_REPEAT, (min, max, item))

        lasivyo this == ".":
            subpatternappend((ANY, Tupu))

        lasivyo this == "(":
            start = source.tell() - 1
            group = Kweli
            name = Tupu
            add_flags = 0
            del_flags = 0
            ikiwa sourcematch("?"):
                # options
                char = sourceget()
                ikiwa char ni Tupu:
                    ashiria source.error("unexpected end of pattern")
                ikiwa char == "P":
                    # python extensions
                    ikiwa sourcematch("<"):
                        # named group: skip forward to end of name
                        name = source.getuntil(">", "group name")
                        ikiwa sio name.isidentifier():
                            msg = "bad character kwenye group name %r" % name
                            ashiria source.error(msg, len(name) + 1)
                    lasivyo sourcematch("="):
                        # named backreference
                        name = source.getuntil(")", "group name")
                        ikiwa sio name.isidentifier():
                            msg = "bad character kwenye group name %r" % name
                            ashiria source.error(msg, len(name) + 1)
                        gid = state.groupdict.get(name)
                        ikiwa gid ni Tupu:
                            msg = "unknown group name %r" % name
                            ashiria source.error(msg, len(name) + 1)
                        ikiwa sio state.checkgroup(gid):
                            ashiria source.error("cannot refer to an open group",
                                               len(name) + 1)
                        state.checklookbehindgroup(gid, source)
                        subpatternappend((GROUPREF, gid))
                        endelea

                    isipokua:
                        char = sourceget()
                        ikiwa char ni Tupu:
                            ashiria source.error("unexpected end of pattern")
                        ashiria source.error("unknown extension ?P" + char,
                                           len(char) + 2)
                lasivyo char == ":":
                    # non-capturing group
                    group = Tupu
                lasivyo char == "#":
                    # comment
                    wakati Kweli:
                        ikiwa source.next ni Tupu:
                            ashiria source.error("missing ), unterminated comment",
                                               source.tell() - start)
                        ikiwa sourceget() == ")":
                            koma
                    endelea

                lasivyo char kwenye "=!<":
                    # lookahead assertions
                    dir = 1
                    ikiwa char == "<":
                        char = sourceget()
                        ikiwa char ni Tupu:
                            ashiria source.error("unexpected end of pattern")
                        ikiwa char haiko kwenye "=!":
                            ashiria source.error("unknown extension ?<" + char,
                                               len(char) + 2)
                        dir = -1 # lookbehind
                        lookbehindgroups = state.lookbehindgroups
                        ikiwa lookbehindgroups ni Tupu:
                            state.lookbehindgroups = state.groups
                    p = _parse_sub(source, state, verbose, nested + 1)
                    ikiwa dir < 0:
                        ikiwa lookbehindgroups ni Tupu:
                            state.lookbehindgroups = Tupu
                    ikiwa sio sourcematch(")"):
                        ashiria source.error("missing ), unterminated subpattern",
                                           source.tell() - start)
                    ikiwa char == "=":
                        subpatternappend((ASSERT, (dir, p)))
                    isipokua:
                        subpatternappend((ASSERT_NOT, (dir, p)))
                    endelea

                lasivyo char == "(":
                    # conditional backreference group
                    condname = source.getuntil(")", "group name")
                    ikiwa condname.isidentifier():
                        condgroup = state.groupdict.get(condname)
                        ikiwa condgroup ni Tupu:
                            msg = "unknown group name %r" % condname
                            ashiria source.error(msg, len(condname) + 1)
                    isipokua:
                        jaribu:
                            condgroup = int(condname)
                            ikiwa condgroup < 0:
                                ashiria ValueError
                        tatizo ValueError:
                            msg = "bad character kwenye group name %r" % condname
                            ashiria source.error(msg, len(condname) + 1) kutoka Tupu
                        ikiwa sio condgroup:
                            ashiria source.error("bad group number",
                                               len(condname) + 1)
                        ikiwa condgroup >= MAXGROUPS:
                            msg = "invalid group reference %d" % condgroup
                            ashiria source.error(msg, len(condname) + 1)
                    state.checklookbehindgroup(condgroup, source)
                    item_yes = _parse(source, state, verbose, nested + 1)
                    ikiwa source.match("|"):
                        item_no = _parse(source, state, verbose, nested + 1)
                        ikiwa source.next == "|":
                            ashiria source.error("conditional backref ukijumuisha more than two branches")
                    isipokua:
                        item_no = Tupu
                    ikiwa sio source.match(")"):
                        ashiria source.error("missing ), unterminated subpattern",
                                           source.tell() - start)
                    subpatternappend((GROUPREF_EXISTS, (condgroup, item_yes, item_no)))
                    endelea

                lasivyo char kwenye FLAGS ama char == "-":
                    # flags
                    flags = _parse_flags(source, state, char)
                    ikiwa flags ni Tupu:  # global flags
                        ikiwa sio first ama subpattern:
                            agiza warnings
                            warnings.warn(
                                'Flags sio at the start of the expression %r%s' % (
                                    source.string[:20],  # truncate long regexes
                                    ' (truncated)' ikiwa len(source.string) > 20 isipokua '',
                                ),
                                DeprecationWarning, stacklevel=nested + 6
                            )
                        ikiwa (state.flags & SRE_FLAG_VERBOSE) na sio verbose:
                            ashiria Verbose
                        endelea

                    add_flags, del_flags = flags
                    group = Tupu
                isipokua:
                    ashiria source.error("unknown extension ?" + char,
                                       len(char) + 1)

            # parse group contents
            ikiwa group ni sio Tupu:
                jaribu:
                    group = state.opengroup(name)
                tatizo error kama err:
                    ashiria source.error(err.msg, len(name) + 1) kutoka Tupu
            sub_verbose = ((verbose ama (add_flags & SRE_FLAG_VERBOSE)) na
                           sio (del_flags & SRE_FLAG_VERBOSE))
            p = _parse_sub(source, state, sub_verbose, nested + 1)
            ikiwa sio source.match(")"):
                ashiria source.error("missing ), unterminated subpattern",
                                   source.tell() - start)
            ikiwa group ni sio Tupu:
                state.closegroup(group, p)
            subpatternappend((SUBPATTERN, (group, add_flags, del_flags, p)))

        lasivyo this == "^":
            subpatternappend((AT, AT_BEGINNING))

        lasivyo this == "$":
            subpatternappend((AT, AT_END))

        isipokua:
            ashiria AssertionError("unsupported special character %r" % (char,))

    # unpack non-capturing groups
    kila i kwenye range(len(subpattern))[::-1]:
        op, av = subpattern[i]
        ikiwa op ni SUBPATTERN:
            group, add_flags, del_flags, p = av
            ikiwa group ni Tupu na sio add_flags na sio del_flags:
                subpattern[i: i+1] = p

    rudisha subpattern

eleza _parse_flags(source, state, char):
    sourceget = source.get
    add_flags = 0
    del_flags = 0
    ikiwa char != "-":
        wakati Kweli:
            flag = FLAGS[char]
            ikiwa source.istext:
                ikiwa char == 'L':
                    msg = "bad inline flags: cannot use 'L' flag ukijumuisha a str pattern"
                    ashiria source.error(msg)
            isipokua:
                ikiwa char == 'u':
                    msg = "bad inline flags: cannot use 'u' flag ukijumuisha a bytes pattern"
                    ashiria source.error(msg)
            add_flags |= flag
            ikiwa (flag & TYPE_FLAGS) na (add_flags & TYPE_FLAGS) != flag:
                msg = "bad inline flags: flags 'a', 'u' na 'L' are incompatible"
                ashiria source.error(msg)
            char = sourceget()
            ikiwa char ni Tupu:
                ashiria source.error("missing -, : ama )")
            ikiwa char kwenye ")-:":
                koma
            ikiwa char haiko kwenye FLAGS:
                msg = "unknown flag" ikiwa char.isalpha() isipokua "missing -, : ama )"
                ashiria source.error(msg, len(char))
    ikiwa char == ")":
        state.flags |= add_flags
        rudisha Tupu
    ikiwa add_flags & GLOBAL_FLAGS:
        ashiria source.error("bad inline flags: cannot turn on global flag", 1)
    ikiwa char == "-":
        char = sourceget()
        ikiwa char ni Tupu:
            ashiria source.error("missing flag")
        ikiwa char haiko kwenye FLAGS:
            msg = "unknown flag" ikiwa char.isalpha() isipokua "missing flag"
            ashiria source.error(msg, len(char))
        wakati Kweli:
            flag = FLAGS[char]
            ikiwa flag & TYPE_FLAGS:
                msg = "bad inline flags: cannot turn off flags 'a', 'u' na 'L'"
                ashiria source.error(msg)
            del_flags |= flag
            char = sourceget()
            ikiwa char ni Tupu:
                ashiria source.error("missing :")
            ikiwa char == ":":
                koma
            ikiwa char haiko kwenye FLAGS:
                msg = "unknown flag" ikiwa char.isalpha() isipokua "missing :"
                ashiria source.error(msg, len(char))
    assert char == ":"
    ikiwa del_flags & GLOBAL_FLAGS:
        ashiria source.error("bad inline flags: cannot turn off global flag", 1)
    ikiwa add_flags & del_flags:
        ashiria source.error("bad inline flags: flag turned on na off", 1)
    rudisha add_flags, del_flags

eleza fix_flags(src, flags):
    # Check na fix flags according to the type of pattern (str ama bytes)
    ikiwa isinstance(src, str):
        ikiwa flags & SRE_FLAG_LOCALE:
            ashiria ValueError("cannot use LOCALE flag ukijumuisha a str pattern")
        ikiwa sio flags & SRE_FLAG_ASCII:
            flags |= SRE_FLAG_UNICODE
        lasivyo flags & SRE_FLAG_UNICODE:
            ashiria ValueError("ASCII na UNICODE flags are incompatible")
    isipokua:
        ikiwa flags & SRE_FLAG_UNICODE:
            ashiria ValueError("cannot use UNICODE flag ukijumuisha a bytes pattern")
        ikiwa flags & SRE_FLAG_LOCALE na flags & SRE_FLAG_ASCII:
            ashiria ValueError("ASCII na LOCALE flags are incompatible")
    rudisha flags

eleza parse(str, flags=0, state=Tupu):
    # parse 're' pattern into list of (opcode, argument) tuples

    source = Tokenizer(str)

    ikiwa state ni Tupu:
        state = State()
    state.flags = flags
    state.str = str

    jaribu:
        p = _parse_sub(source, state, flags & SRE_FLAG_VERBOSE, 0)
    tatizo Verbose:
        # the VERBOSE flag was switched on inside the pattern.  to be
        # on the safe side, we'll parse the whole thing again...
        state = State()
        state.flags = flags | SRE_FLAG_VERBOSE
        state.str = str
        source.seek(0)
        p = _parse_sub(source, state, Kweli, 0)

    p.state.flags = fix_flags(str, p.state.flags)

    ikiwa source.next ni sio Tupu:
        assert source.next == ")"
        ashiria source.error("unbalanced parenthesis")

    ikiwa flags & SRE_FLAG_DEBUG:
        p.dump()

    rudisha p

eleza parse_template(source, state):
    # parse 're' replacement string into list of literals na
    # group references
    s = Tokenizer(source)
    sget = s.get
    groups = []
    literals = []
    literal = []
    lappend = literal.append
    eleza addgroup(index, pos):
        ikiwa index > state.groups:
            ashiria s.error("invalid group reference %d" % index, pos)
        ikiwa literal:
            literals.append(''.join(literal))
            toa literal[:]
        groups.append((len(literals), index))
        literals.append(Tupu)
    groupindex = state.groupindex
    wakati Kweli:
        this = sget()
        ikiwa this ni Tupu:
            koma # end of replacement string
        ikiwa this[0] == "\\":
            # group
            c = this[1]
            ikiwa c == "g":
                name = ""
                ikiwa sio s.match("<"):
                    ashiria s.error("missing <")
                name = s.getuntil(">", "group name")
                ikiwa name.isidentifier():
                    jaribu:
                        index = groupindex[name]
                    tatizo KeyError:
                        ashiria IndexError("unknown group name %r" % name)
                isipokua:
                    jaribu:
                        index = int(name)
                        ikiwa index < 0:
                            ashiria ValueError
                    tatizo ValueError:
                        ashiria s.error("bad character kwenye group name %r" % name,
                                      len(name) + 1) kutoka Tupu
                    ikiwa index >= MAXGROUPS:
                        ashiria s.error("invalid group reference %d" % index,
                                      len(name) + 1)
                addgroup(index, len(name) + 1)
            lasivyo c == "0":
                ikiwa s.next kwenye OCTDIGITS:
                    this += sget()
                    ikiwa s.next kwenye OCTDIGITS:
                        this += sget()
                lappend(chr(int(this[1:], 8) & 0xff))
            lasivyo c kwenye DIGITS:
                isoctal = Uongo
                ikiwa s.next kwenye DIGITS:
                    this += sget()
                    ikiwa (c kwenye OCTDIGITS na this[2] kwenye OCTDIGITS na
                        s.next kwenye OCTDIGITS):
                        this += sget()
                        isoctal = Kweli
                        c = int(this[1:], 8)
                        ikiwa c > 0o377:
                            ashiria s.error('octal escape value %s outside of '
                                          'range 0-0o377' % this, len(this))
                        lappend(chr(c))
                ikiwa sio isoctal:
                    addgroup(int(this[1:]), len(this) - 1)
            isipokua:
                jaribu:
                    this = chr(ESCAPES[this][1])
                tatizo KeyError:
                    ikiwa c kwenye ASCIILETTERS:
                        ashiria s.error('bad escape %s' % this, len(this))
                lappend(this)
        isipokua:
            lappend(this)
    ikiwa literal:
        literals.append(''.join(literal))
    ikiwa sio isinstance(source, str):
        # The tokenizer implicitly decodes bytes objects kama latin-1, we must
        # therefore re-encode the final representation.
        literals = [Tupu ikiwa s ni Tupu isipokua s.encode('latin-1') kila s kwenye literals]
    rudisha groups, literals

eleza expand_template(template, match):
    g = match.group
    empty = match.string[:0]
    groups, literals = template
    literals = literals[:]
    jaribu:
        kila index, group kwenye groups:
            literals[index] = g(group) ama empty
    tatizo IndexError:
        ashiria error("invalid group reference %d" % index)
    rudisha empty.join(literals)
