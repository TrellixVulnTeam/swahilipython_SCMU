#
# Secret Labs' Regular Expression Engine
#
# convert re-style regular expression to sre pattern
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file for information on usage and redistribution.
#

"""Internal support module for sre"""

# XXX: show string offset and offending character for all errors

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
    pass

kundi State:
    # keeps track of state for parsing
    eleza __init__(self):
        self.flags = 0
        self.groupdict = {}
        self.groupwidths = [None]  # group 0
        self.lookbehindgroups = None
    @property
    eleza groups(self):
        rudisha len(self.groupwidths)
    eleza opengroup(self, name=None):
        gid = self.groups
        self.groupwidths.append(None)
        ikiwa self.groups > MAXGROUPS:
            raise error("too many groups")
        ikiwa name is not None:
            ogid = self.groupdict.get(name, None)
            ikiwa ogid is not None:
                raise error("redefinition of group name %r as group %d; "
                            "was group %d" % (name, gid,  ogid))
            self.groupdict[name] = gid
        rudisha gid
    eleza closegroup(self, gid, p):
        self.groupwidths[gid] = p.getwidth()
    eleza checkgroup(self, gid):
        rudisha gid < self.groups and self.groupwidths[gid] is not None

    eleza checklookbehindgroup(self, gid, source):
        ikiwa self.lookbehindgroups is not None:
            ikiwa not self.checkgroup(gid):
                raise source.error('cannot refer to an open group')
            ikiwa gid >= self.lookbehindgroups:
                raise source.error('cannot refer to group defined in the same '
                                   'lookbehind subpattern')

kundi SubPattern:
    # a subpattern, in intermediate form
    eleza __init__(self, state, data=None):
        self.state = state
        ikiwa data is None:
            data = []
        self.data = data
        self.width = None

    eleza dump(self, level=0):
        nl = True
        seqtypes = (tuple, list)
        for op, av in self.data:
            andika(level*"  " + str(op), end='')
            ikiwa op is IN:
                # member sublanguage
                andika()
                for op, a in av:
                    andika((level+1)*"  " + str(op), a)
            elikiwa op is BRANCH:
                andika()
                for i, a in enumerate(av[1]):
                    ikiwa i:
                        andika(level*"  " + "OR")
                    a.dump(level+1)
            elikiwa op is GROUPREF_EXISTS:
                condgroup, item_yes, item_no = av
                andika('', condgroup)
                item_yes.dump(level+1)
                ikiwa item_no:
                    andika(level*"  " + "ELSE")
                    item_no.dump(level+1)
            elikiwa isinstance(av, seqtypes):
                nl = False
                for a in av:
                    ikiwa isinstance(a, SubPattern):
                        ikiwa not nl:
                            andika()
                        a.dump(level+1)
                        nl = True
                    else:
                        ikiwa not nl:
                            andika(' ', end='')
                        andika(a, end='')
                        nl = False
                ikiwa not nl:
                    andika()
            else:
                andika('', av)
    eleza __repr__(self):
        rudisha repr(self.data)
    eleza __len__(self):
        rudisha len(self.data)
    eleza __delitem__(self, index):
        del self.data[index]
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
        # determine the width (min, max) for this subpattern
        ikiwa self.width is not None:
            rudisha self.width
        lo = hi = 0
        for op, av in self.data:
            ikiwa op is BRANCH:
                i = MAXREPEAT - 1
                j = 0
                for av in av[1]:
                    l, h = av.getwidth()
                    i = min(i, l)
                    j = max(j, h)
                lo = lo + i
                hi = hi + j
            elikiwa op is CALL:
                i, j = av.getwidth()
                lo = lo + i
                hi = hi + j
            elikiwa op is SUBPATTERN:
                i, j = av[-1].getwidth()
                lo = lo + i
                hi = hi + j
            elikiwa op in _REPEATCODES:
                i, j = av[2].getwidth()
                lo = lo + i * av[0]
                hi = hi + j * av[1]
            elikiwa op in _UNITCODES:
                lo = lo + 1
                hi = hi + 1
            elikiwa op is GROUPREF:
                i, j = self.state.groupwidths[av]
                lo = lo + i
                hi = hi + j
            elikiwa op is GROUPREF_EXISTS:
                i, j = av[1].getwidth()
                ikiwa av[2] is not None:
                    l, h = av[2].getwidth()
                    i = min(i, l)
                    j = max(j, h)
                else:
                    i = 0
                lo = lo + i
                hi = hi + j
            elikiwa op is SUCCESS:
                break
        self.width = min(lo, MAXREPEAT - 1), min(hi, MAXREPEAT)
        rudisha self.width

kundi Tokenizer:
    eleza __init__(self, string):
        self.istext = isinstance(string, str)
        self.string = string
        ikiwa not self.istext:
            string = str(string, 'latin1')
        self.decoded_string = string
        self.index = 0
        self.next = None
        self.__next()
    eleza __next(self):
        index = self.index
        try:
            char = self.decoded_string[index]
        except IndexError:
            self.next = None
            return
        ikiwa char == "\\":
            index += 1
            try:
                char += self.decoded_string[index]
            except IndexError:
                raise error("bad escape (end of pattern)",
                            self.string, len(self.string) - 1) kutoka None
        self.index = index + 1
        self.next = char
    eleza match(self, char):
        ikiwa char == self.next:
            self.__next()
            rudisha True
        rudisha False
    eleza get(self):
        this = self.next
        self.__next()
        rudisha this
    eleza getwhile(self, n, charset):
        result = ''
        for _ in range(n):
            c = self.next
            ikiwa c not in charset:
                break
            result += c
            self.__next()
        rudisha result
    eleza getuntil(self, terminator, name):
        result = ''
        while True:
            c = self.next
            self.__next()
            ikiwa c is None:
                ikiwa not result:
                    raise self.error("missing " + name)
                raise self.error("missing %s, unterminated name" % terminator,
                                 len(result))
            ikiwa c == terminator:
                ikiwa not result:
                    raise self.error("missing " + name, 1)
                break
            result += c
        rudisha result
    @property
    eleza pos(self):
        rudisha self.index - len(self.next or '')
    eleza tell(self):
        rudisha self.index - len(self.next or '')
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
    ikiwa code and code[0] is IN:
        rudisha code
    try:
        c = escape[1:2]
        ikiwa c == "x":
            # hexadecimal escape (exactly two digits)
            escape += source.getwhile(2, HEXDIGITS)
            ikiwa len(escape) != 4:
                raise source.error("incomplete escape %s" % escape, len(escape))
            rudisha LITERAL, int(escape[2:], 16)
        elikiwa c == "u" and source.istext:
            # unicode escape (exactly four digits)
            escape += source.getwhile(4, HEXDIGITS)
            ikiwa len(escape) != 6:
                raise source.error("incomplete escape %s" % escape, len(escape))
            rudisha LITERAL, int(escape[2:], 16)
        elikiwa c == "U" and source.istext:
            # unicode escape (exactly eight digits)
            escape += source.getwhile(8, HEXDIGITS)
            ikiwa len(escape) != 10:
                raise source.error("incomplete escape %s" % escape, len(escape))
            c = int(escape[2:], 16)
            chr(c) # raise ValueError for invalid code
            rudisha LITERAL, c
        elikiwa c == "N" and source.istext:
            agiza unicodedata
            # named unicode escape e.g. \N{EM DASH}
            ikiwa not source.match('{'):
                raise source.error("missing {")
            charname = source.getuntil('}', 'character name')
            try:
                c = ord(unicodedata.lookup(charname))
            except KeyError:
                raise source.error("undefined character name %r" % charname,
                                   len(charname) + len(r'\N{}'))
            rudisha LITERAL, c
        elikiwa c in OCTDIGITS:
            # octal escape (up to three digits)
            escape += source.getwhile(2, OCTDIGITS)
            c = int(escape[1:], 8)
            ikiwa c > 0o377:
                raise source.error('octal escape value %s outside of '
                                   'range 0-0o377' % escape, len(escape))
            rudisha LITERAL, c
        elikiwa c in DIGITS:
            raise ValueError
        ikiwa len(escape) == 2:
            ikiwa c in ASCIILETTERS:
                raise source.error('bad escape %s' % escape, len(escape))
            rudisha LITERAL, ord(escape[1])
    except ValueError:
        pass
    raise source.error("bad escape %s" % escape, len(escape))

eleza _escape(source, escape, state):
    # handle escape code in expression
    code = CATEGORIES.get(escape)
    ikiwa code:
        rudisha code
    code = ESCAPES.get(escape)
    ikiwa code:
        rudisha code
    try:
        c = escape[1:2]
        ikiwa c == "x":
            # hexadecimal escape
            escape += source.getwhile(2, HEXDIGITS)
            ikiwa len(escape) != 4:
                raise source.error("incomplete escape %s" % escape, len(escape))
            rudisha LITERAL, int(escape[2:], 16)
        elikiwa c == "u" and source.istext:
            # unicode escape (exactly four digits)
            escape += source.getwhile(4, HEXDIGITS)
            ikiwa len(escape) != 6:
                raise source.error("incomplete escape %s" % escape, len(escape))
            rudisha LITERAL, int(escape[2:], 16)
        elikiwa c == "U" and source.istext:
            # unicode escape (exactly eight digits)
            escape += source.getwhile(8, HEXDIGITS)
            ikiwa len(escape) != 10:
                raise source.error("incomplete escape %s" % escape, len(escape))
            c = int(escape[2:], 16)
            chr(c) # raise ValueError for invalid code
            rudisha LITERAL, c
        elikiwa c == "N" and source.istext:
            agiza unicodedata
            # named unicode escape e.g. \N{EM DASH}
            ikiwa not source.match('{'):
                raise source.error("missing {")
            charname = source.getuntil('}', 'character name')
            try:
                c = ord(unicodedata.lookup(charname))
            except KeyError:
                raise source.error("undefined character name %r" % charname,
                                   len(charname) + len(r'\N{}'))
            rudisha LITERAL, c
        elikiwa c == "0":
            # octal escape
            escape += source.getwhile(2, OCTDIGITS)
            rudisha LITERAL, int(escape[1:], 8)
        elikiwa c in DIGITS:
            # octal escape *or* decimal group reference (sigh)
            ikiwa source.next in DIGITS:
                escape += source.get()
                ikiwa (escape[1] in OCTDIGITS and escape[2] in OCTDIGITS and
                    source.next in OCTDIGITS):
                    # got three octal digits; this is an octal escape
                    escape += source.get()
                    c = int(escape[1:], 8)
                    ikiwa c > 0o377:
                        raise source.error('octal escape value %s outside of '
                                           'range 0-0o377' % escape,
                                           len(escape))
                    rudisha LITERAL, c
            # not an octal escape, so this is a group reference
            group = int(escape[1:])
            ikiwa group < state.groups:
                ikiwa not state.checkgroup(group):
                    raise source.error("cannot refer to an open group",
                                       len(escape))
                state.checklookbehindgroup(group, source)
                rudisha GROUPREF, group
            raise source.error("invalid group reference %d" % group, len(escape) - 1)
        ikiwa len(escape) == 2:
            ikiwa c in ASCIILETTERS:
                raise source.error("bad escape %s" % escape, len(escape))
            rudisha LITERAL, ord(escape[1])
    except ValueError:
        pass
    raise source.error("bad escape %s" % escape, len(escape))

eleza _uniq(items):
    rudisha list(dict.kutokakeys(items))

eleza _parse_sub(source, state, verbose, nested):
    # parse an alternation: a|b|c

    items = []
    itemsappend = items.append
    sourcematch = source.match
    start = source.tell()
    while True:
        itemsappend(_parse(source, state, verbose, nested + 1,
                           not nested and not items))
        ikiwa not sourcematch("|"):
            break

    ikiwa len(items) == 1:
        rudisha items[0]

    subpattern = SubPattern(state)

    # check ikiwa all items share a common prefix
    while True:
        prefix = None
        for item in items:
            ikiwa not item:
                break
            ikiwa prefix is None:
                prefix = item[0]
            elikiwa item[0] != prefix:
                break
        else:
            # all subitems start with a common "prefix".
            # move it out of the branch
            for item in items:
                del item[0]
            subpattern.append(prefix)
            continue # check next one
        break

    # check ikiwa the branch can be replaced by a character set
    set = []
    for item in items:
        ikiwa len(item) != 1:
            break
        op, av = item[0]
        ikiwa op is LITERAL:
            set.append((op, av))
        elikiwa op is IN and av[0][0] is not NEGATE:
            set.extend(av)
        else:
            break
    else:
        # we can store this as a character set instead of a
        # branch (the compiler may optimize this even more)
        subpattern.append((IN, _uniq(set)))
        rudisha subpattern

    subpattern.append((BRANCH, (None, items)))
    rudisha subpattern

eleza _parse(source, state, verbose, nested, first=False):
    # parse a simple pattern
    subpattern = SubPattern(state)

    # precompute constants into local variables
    subpatternappend = subpattern.append
    sourceget = source.get
    sourcematch = source.match
    _len = len
    _ord = ord

    while True:

        this = source.next
        ikiwa this is None:
            break # end of pattern
        ikiwa this in "|)":
            break # end of subpattern
        sourceget()

        ikiwa verbose:
            # skip whitespace and comments
            ikiwa this in WHITESPACE:
                continue
            ikiwa this == "#":
                while True:
                    this = sourceget()
                    ikiwa this is None or this == "\n":
                        break
                continue

        ikiwa this[0] == "\\":
            code = _escape(source, this, state)
            subpatternappend(code)

        elikiwa this not in SPECIAL_CHARS:
            subpatternappend((LITERAL, _ord(this)))

        elikiwa this == "[":
            here = source.tell() - 1
            # character set
            set = []
            setappend = set.append
##          ikiwa sourcematch(":"):
##              pass # handle character classes
            ikiwa source.next == '[':
                agiza warnings
                warnings.warn(
                    'Possible nested set at position %d' % source.tell(),
                    FutureWarning, stacklevel=nested + 6
                )
            negate = sourcematch("^")
            # check remaining characters
            while True:
                this = sourceget()
                ikiwa this is None:
                    raise source.error("unterminated character set",
                                       source.tell() - here)
                ikiwa this == "]" and set:
                    break
                elikiwa this[0] == "\\":
                    code1 = _class_escape(source, this)
                else:
                    ikiwa set and this in '-&~|' and source.next == this:
                        agiza warnings
                        warnings.warn(
                            'Possible set %s at position %d' % (
                                'difference' ikiwa this == '-' else
                                'intersection' ikiwa this == '&' else
                                'symmetric difference' ikiwa this == '~' else
                                'union',
                                source.tell() - 1),
                            FutureWarning, stacklevel=nested + 6
                        )
                    code1 = LITERAL, _ord(this)
                ikiwa sourcematch("-"):
                    # potential range
                    that = sourceget()
                    ikiwa that is None:
                        raise source.error("unterminated character set",
                                           source.tell() - here)
                    ikiwa that == "]":
                        ikiwa code1[0] is IN:
                            code1 = code1[1][0]
                        setappend(code1)
                        setappend((LITERAL, _ord("-")))
                        break
                    ikiwa that[0] == "\\":
                        code2 = _class_escape(source, that)
                    else:
                        ikiwa that == '-':
                            agiza warnings
                            warnings.warn(
                                'Possible set difference at position %d' % (
                                    source.tell() - 2),
                                FutureWarning, stacklevel=nested + 6
                            )
                        code2 = LITERAL, _ord(that)
                    ikiwa code1[0] != LITERAL or code2[0] != LITERAL:
                        msg = "bad character range %s-%s" % (this, that)
                        raise source.error(msg, len(this) + 1 + len(that))
                    lo = code1[1]
                    hi = code2[1]
                    ikiwa hi < lo:
                        msg = "bad character range %s-%s" % (this, that)
                        raise source.error(msg, len(this) + 1 + len(that))
                    setappend((RANGE, (lo, hi)))
                else:
                    ikiwa code1[0] is IN:
                        code1 = code1[1][0]
                    setappend(code1)

            set = _uniq(set)
            # XXX: <fl> should move set optimization to compiler!
            ikiwa _len(set) == 1 and set[0][0] is LITERAL:
                # optimization
                ikiwa negate:
                    subpatternappend((NOT_LITERAL, set[0][1]))
                else:
                    subpatternappend(set[0])
            else:
                ikiwa negate:
                    set.insert(0, (NEGATE, None))
                # charmap optimization can't be added here because
                # global flags still are not known
                subpatternappend((IN, set))

        elikiwa this in REPEAT_CHARS:
            # repeat previous item
            here = source.tell()
            ikiwa this == "?":
                min, max = 0, 1
            elikiwa this == "*":
                min, max = 0, MAXREPEAT

            elikiwa this == "+":
                min, max = 1, MAXREPEAT
            elikiwa this == "{":
                ikiwa source.next == "}":
                    subpatternappend((LITERAL, _ord(this)))
                    continue

                min, max = 0, MAXREPEAT
                lo = hi = ""
                while source.next in DIGITS:
                    lo += sourceget()
                ikiwa sourcematch(","):
                    while source.next in DIGITS:
                        hi += sourceget()
                else:
                    hi = lo
                ikiwa not sourcematch("}"):
                    subpatternappend((LITERAL, _ord(this)))
                    source.seek(here)
                    continue

                ikiwa lo:
                    min = int(lo)
                    ikiwa min >= MAXREPEAT:
                        raise OverflowError("the repetition number is too large")
                ikiwa hi:
                    max = int(hi)
                    ikiwa max >= MAXREPEAT:
                        raise OverflowError("the repetition number is too large")
                    ikiwa max < min:
                        raise source.error("min repeat greater than max repeat",
                                           source.tell() - here)
            else:
                raise AssertionError("unsupported quantifier %r" % (char,))
            # figure out which item to repeat
            ikiwa subpattern:
                item = subpattern[-1:]
            else:
                item = None
            ikiwa not item or item[0][0] is AT:
                raise source.error("nothing to repeat",
                                   source.tell() - here + len(this))
            ikiwa item[0][0] in _REPEATCODES:
                raise source.error("multiple repeat",
                                   source.tell() - here + len(this))
            ikiwa item[0][0] is SUBPATTERN:
                group, add_flags, del_flags, p = item[0][1]
                ikiwa group is None and not add_flags and not del_flags:
                    item = p
            ikiwa sourcematch("?"):
                subpattern[-1] = (MIN_REPEAT, (min, max, item))
            else:
                subpattern[-1] = (MAX_REPEAT, (min, max, item))

        elikiwa this == ".":
            subpatternappend((ANY, None))

        elikiwa this == "(":
            start = source.tell() - 1
            group = True
            name = None
            add_flags = 0
            del_flags = 0
            ikiwa sourcematch("?"):
                # options
                char = sourceget()
                ikiwa char is None:
                    raise source.error("unexpected end of pattern")
                ikiwa char == "P":
                    # python extensions
                    ikiwa sourcematch("<"):
                        # named group: skip forward to end of name
                        name = source.getuntil(">", "group name")
                        ikiwa not name.isidentifier():
                            msg = "bad character in group name %r" % name
                            raise source.error(msg, len(name) + 1)
                    elikiwa sourcematch("="):
                        # named backreference
                        name = source.getuntil(")", "group name")
                        ikiwa not name.isidentifier():
                            msg = "bad character in group name %r" % name
                            raise source.error(msg, len(name) + 1)
                        gid = state.groupdict.get(name)
                        ikiwa gid is None:
                            msg = "unknown group name %r" % name
                            raise source.error(msg, len(name) + 1)
                        ikiwa not state.checkgroup(gid):
                            raise source.error("cannot refer to an open group",
                                               len(name) + 1)
                        state.checklookbehindgroup(gid, source)
                        subpatternappend((GROUPREF, gid))
                        continue

                    else:
                        char = sourceget()
                        ikiwa char is None:
                            raise source.error("unexpected end of pattern")
                        raise source.error("unknown extension ?P" + char,
                                           len(char) + 2)
                elikiwa char == ":":
                    # non-capturing group
                    group = None
                elikiwa char == "#":
                    # comment
                    while True:
                        ikiwa source.next is None:
                            raise source.error("missing ), unterminated comment",
                                               source.tell() - start)
                        ikiwa sourceget() == ")":
                            break
                    continue

                elikiwa char in "=!<":
                    # lookahead assertions
                    dir = 1
                    ikiwa char == "<":
                        char = sourceget()
                        ikiwa char is None:
                            raise source.error("unexpected end of pattern")
                        ikiwa char not in "=!":
                            raise source.error("unknown extension ?<" + char,
                                               len(char) + 2)
                        dir = -1 # lookbehind
                        lookbehindgroups = state.lookbehindgroups
                        ikiwa lookbehindgroups is None:
                            state.lookbehindgroups = state.groups
                    p = _parse_sub(source, state, verbose, nested + 1)
                    ikiwa dir < 0:
                        ikiwa lookbehindgroups is None:
                            state.lookbehindgroups = None
                    ikiwa not sourcematch(")"):
                        raise source.error("missing ), unterminated subpattern",
                                           source.tell() - start)
                    ikiwa char == "=":
                        subpatternappend((ASSERT, (dir, p)))
                    else:
                        subpatternappend((ASSERT_NOT, (dir, p)))
                    continue

                elikiwa char == "(":
                    # conditional backreference group
                    condname = source.getuntil(")", "group name")
                    ikiwa condname.isidentifier():
                        condgroup = state.groupdict.get(condname)
                        ikiwa condgroup is None:
                            msg = "unknown group name %r" % condname
                            raise source.error(msg, len(condname) + 1)
                    else:
                        try:
                            condgroup = int(condname)
                            ikiwa condgroup < 0:
                                raise ValueError
                        except ValueError:
                            msg = "bad character in group name %r" % condname
                            raise source.error(msg, len(condname) + 1) kutoka None
                        ikiwa not condgroup:
                            raise source.error("bad group number",
                                               len(condname) + 1)
                        ikiwa condgroup >= MAXGROUPS:
                            msg = "invalid group reference %d" % condgroup
                            raise source.error(msg, len(condname) + 1)
                    state.checklookbehindgroup(condgroup, source)
                    item_yes = _parse(source, state, verbose, nested + 1)
                    ikiwa source.match("|"):
                        item_no = _parse(source, state, verbose, nested + 1)
                        ikiwa source.next == "|":
                            raise source.error("conditional backref with more than two branches")
                    else:
                        item_no = None
                    ikiwa not source.match(")"):
                        raise source.error("missing ), unterminated subpattern",
                                           source.tell() - start)
                    subpatternappend((GROUPREF_EXISTS, (condgroup, item_yes, item_no)))
                    continue

                elikiwa char in FLAGS or char == "-":
                    # flags
                    flags = _parse_flags(source, state, char)
                    ikiwa flags is None:  # global flags
                        ikiwa not first or subpattern:
                            agiza warnings
                            warnings.warn(
                                'Flags not at the start of the expression %r%s' % (
                                    source.string[:20],  # truncate long regexes
                                    ' (truncated)' ikiwa len(source.string) > 20 else '',
                                ),
                                DeprecationWarning, stacklevel=nested + 6
                            )
                        ikiwa (state.flags & SRE_FLAG_VERBOSE) and not verbose:
                            raise Verbose
                        continue

                    add_flags, del_flags = flags
                    group = None
                else:
                    raise source.error("unknown extension ?" + char,
                                       len(char) + 1)

            # parse group contents
            ikiwa group is not None:
                try:
                    group = state.opengroup(name)
                except error as err:
                    raise source.error(err.msg, len(name) + 1) kutoka None
            sub_verbose = ((verbose or (add_flags & SRE_FLAG_VERBOSE)) and
                           not (del_flags & SRE_FLAG_VERBOSE))
            p = _parse_sub(source, state, sub_verbose, nested + 1)
            ikiwa not source.match(")"):
                raise source.error("missing ), unterminated subpattern",
                                   source.tell() - start)
            ikiwa group is not None:
                state.closegroup(group, p)
            subpatternappend((SUBPATTERN, (group, add_flags, del_flags, p)))

        elikiwa this == "^":
            subpatternappend((AT, AT_BEGINNING))

        elikiwa this == "$":
            subpatternappend((AT, AT_END))

        else:
            raise AssertionError("unsupported special character %r" % (char,))

    # unpack non-capturing groups
    for i in range(len(subpattern))[::-1]:
        op, av = subpattern[i]
        ikiwa op is SUBPATTERN:
            group, add_flags, del_flags, p = av
            ikiwa group is None and not add_flags and not del_flags:
                subpattern[i: i+1] = p

    rudisha subpattern

eleza _parse_flags(source, state, char):
    sourceget = source.get
    add_flags = 0
    del_flags = 0
    ikiwa char != "-":
        while True:
            flag = FLAGS[char]
            ikiwa source.istext:
                ikiwa char == 'L':
                    msg = "bad inline flags: cannot use 'L' flag with a str pattern"
                    raise source.error(msg)
            else:
                ikiwa char == 'u':
                    msg = "bad inline flags: cannot use 'u' flag with a bytes pattern"
                    raise source.error(msg)
            add_flags |= flag
            ikiwa (flag & TYPE_FLAGS) and (add_flags & TYPE_FLAGS) != flag:
                msg = "bad inline flags: flags 'a', 'u' and 'L' are incompatible"
                raise source.error(msg)
            char = sourceget()
            ikiwa char is None:
                raise source.error("missing -, : or )")
            ikiwa char in ")-:":
                break
            ikiwa char not in FLAGS:
                msg = "unknown flag" ikiwa char.isalpha() else "missing -, : or )"
                raise source.error(msg, len(char))
    ikiwa char == ")":
        state.flags |= add_flags
        rudisha None
    ikiwa add_flags & GLOBAL_FLAGS:
        raise source.error("bad inline flags: cannot turn on global flag", 1)
    ikiwa char == "-":
        char = sourceget()
        ikiwa char is None:
            raise source.error("missing flag")
        ikiwa char not in FLAGS:
            msg = "unknown flag" ikiwa char.isalpha() else "missing flag"
            raise source.error(msg, len(char))
        while True:
            flag = FLAGS[char]
            ikiwa flag & TYPE_FLAGS:
                msg = "bad inline flags: cannot turn off flags 'a', 'u' and 'L'"
                raise source.error(msg)
            del_flags |= flag
            char = sourceget()
            ikiwa char is None:
                raise source.error("missing :")
            ikiwa char == ":":
                break
            ikiwa char not in FLAGS:
                msg = "unknown flag" ikiwa char.isalpha() else "missing :"
                raise source.error(msg, len(char))
    assert char == ":"
    ikiwa del_flags & GLOBAL_FLAGS:
        raise source.error("bad inline flags: cannot turn off global flag", 1)
    ikiwa add_flags & del_flags:
        raise source.error("bad inline flags: flag turned on and off", 1)
    rudisha add_flags, del_flags

eleza fix_flags(src, flags):
    # Check and fix flags according to the type of pattern (str or bytes)
    ikiwa isinstance(src, str):
        ikiwa flags & SRE_FLAG_LOCALE:
            raise ValueError("cannot use LOCALE flag with a str pattern")
        ikiwa not flags & SRE_FLAG_ASCII:
            flags |= SRE_FLAG_UNICODE
        elikiwa flags & SRE_FLAG_UNICODE:
            raise ValueError("ASCII and UNICODE flags are incompatible")
    else:
        ikiwa flags & SRE_FLAG_UNICODE:
            raise ValueError("cannot use UNICODE flag with a bytes pattern")
        ikiwa flags & SRE_FLAG_LOCALE and flags & SRE_FLAG_ASCII:
            raise ValueError("ASCII and LOCALE flags are incompatible")
    rudisha flags

eleza parse(str, flags=0, state=None):
    # parse 're' pattern into list of (opcode, argument) tuples

    source = Tokenizer(str)

    ikiwa state is None:
        state = State()
    state.flags = flags
    state.str = str

    try:
        p = _parse_sub(source, state, flags & SRE_FLAG_VERBOSE, 0)
    except Verbose:
        # the VERBOSE flag was switched on inside the pattern.  to be
        # on the safe side, we'll parse the whole thing again...
        state = State()
        state.flags = flags | SRE_FLAG_VERBOSE
        state.str = str
        source.seek(0)
        p = _parse_sub(source, state, True, 0)

    p.state.flags = fix_flags(str, p.state.flags)

    ikiwa source.next is not None:
        assert source.next == ")"
        raise source.error("unbalanced parenthesis")

    ikiwa flags & SRE_FLAG_DEBUG:
        p.dump()

    rudisha p

eleza parse_template(source, state):
    # parse 're' replacement string into list of literals and
    # group references
    s = Tokenizer(source)
    sget = s.get
    groups = []
    literals = []
    literal = []
    lappend = literal.append
    eleza addgroup(index, pos):
        ikiwa index > state.groups:
            raise s.error("invalid group reference %d" % index, pos)
        ikiwa literal:
            literals.append(''.join(literal))
            del literal[:]
        groups.append((len(literals), index))
        literals.append(None)
    groupindex = state.groupindex
    while True:
        this = sget()
        ikiwa this is None:
            break # end of replacement string
        ikiwa this[0] == "\\":
            # group
            c = this[1]
            ikiwa c == "g":
                name = ""
                ikiwa not s.match("<"):
                    raise s.error("missing <")
                name = s.getuntil(">", "group name")
                ikiwa name.isidentifier():
                    try:
                        index = groupindex[name]
                    except KeyError:
                        raise IndexError("unknown group name %r" % name)
                else:
                    try:
                        index = int(name)
                        ikiwa index < 0:
                            raise ValueError
                    except ValueError:
                        raise s.error("bad character in group name %r" % name,
                                      len(name) + 1) kutoka None
                    ikiwa index >= MAXGROUPS:
                        raise s.error("invalid group reference %d" % index,
                                      len(name) + 1)
                addgroup(index, len(name) + 1)
            elikiwa c == "0":
                ikiwa s.next in OCTDIGITS:
                    this += sget()
                    ikiwa s.next in OCTDIGITS:
                        this += sget()
                lappend(chr(int(this[1:], 8) & 0xff))
            elikiwa c in DIGITS:
                isoctal = False
                ikiwa s.next in DIGITS:
                    this += sget()
                    ikiwa (c in OCTDIGITS and this[2] in OCTDIGITS and
                        s.next in OCTDIGITS):
                        this += sget()
                        isoctal = True
                        c = int(this[1:], 8)
                        ikiwa c > 0o377:
                            raise s.error('octal escape value %s outside of '
                                          'range 0-0o377' % this, len(this))
                        lappend(chr(c))
                ikiwa not isoctal:
                    addgroup(int(this[1:]), len(this) - 1)
            else:
                try:
                    this = chr(ESCAPES[this][1])
                except KeyError:
                    ikiwa c in ASCIILETTERS:
                        raise s.error('bad escape %s' % this, len(this))
                lappend(this)
        else:
            lappend(this)
    ikiwa literal:
        literals.append(''.join(literal))
    ikiwa not isinstance(source, str):
        # The tokenizer implicitly decodes bytes objects as latin-1, we must
        # therefore re-encode the final representation.
        literals = [None ikiwa s is None else s.encode('latin-1') for s in literals]
    rudisha groups, literals

eleza expand_template(template, match):
    g = match.group
    empty = match.string[:0]
    groups, literals = template
    literals = literals[:]
    try:
        for index, group in groups:
            literals[index] = g(group) or empty
    except IndexError:
        raise error("invalid group reference %d" % index)
    rudisha empty.join(literals)
