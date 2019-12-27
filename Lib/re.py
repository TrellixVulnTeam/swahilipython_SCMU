#
# Secret Labs' Regular Expression Engine
#
# re-compatible interface for the sre matching engine
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# This version of the SRE library can be redistributed under CNRI's
# Python 1.6 license.  For any other use, please contact Secret Labs
# AB (info@pythonware.com).
#
# Portions of this engine have been developed in cooperation with
# CNRI.  Hewlett-Packard provided funding for 1.6 integration and
# other compatibility work.
#

r"""Support for regular expressions (RE).

This module provides regular expression matching operations similar to
those found in Perl.  It supports both 8-bit and Unicode strings; both
the pattern and the strings being processed can contain null bytes and
characters outside the US ASCII range.

Regular expressions can contain both special and ordinary characters.
Most ordinary characters, like "A", "a", or "0", are the simplest
regular expressions; they simply match themselves.  You can
concatenate ordinary characters, so last matches the string 'last'.

The special characters are:
    "."      Matches any character except a newline.
    "^"      Matches the start of the string.
    "$"      Matches the end of the string or just before the newline at
             the end of the string.
    "*"      Matches 0 or more (greedy) repetitions of the preceding RE.
             Greedy means that it will match as many repetitions as possible.
    "+"      Matches 1 or more (greedy) repetitions of the preceding RE.
    "?"      Matches 0 or 1 (greedy) of the preceding RE.
    *?,+?,?? Non-greedy versions of the previous three special characters.
    {m,n}    Matches kutoka m to n repetitions of the preceding RE.
    {m,n}?   Non-greedy version of the above.
    "\\"     Either escapes special characters or signals a special sequence.
    []       Indicates a set of characters.
             A "^" as the first character indicates a complementing set.
    "|"      A|B, creates an RE that will match either A or B.
    (...)    Matches the RE inside the parentheses.
             The contents can be retrieved or matched later in the string.
    (?aiLmsux) Set the A, I, L, M, S, U, or X flag for the RE (see below).
    (?:...)  Non-grouping version of regular parentheses.
    (?P<name>...) The substring matched by the group is accessible by name.
    (?P=name)     Matches the text matched earlier by the group named name.
    (?#...)  A comment; ignored.
    (?=...)  Matches ikiwa ... matches next, but doesn't consume the string.
    (?!...)  Matches ikiwa ... doesn't match next.
    (?<=...) Matches ikiwa preceded by ... (must be fixed length).
    (?<!...) Matches ikiwa not preceded by ... (must be fixed length).
    (?(id/name)yes|no) Matches yes pattern ikiwa the group with id/name matched,
                       the (optional) no pattern otherwise.

The special sequences consist of "\\" and a character kutoka the list
below.  If the ordinary character is not on the list, then the
resulting RE will match the second character.
    \number  Matches the contents of the group of the same number.
    \A       Matches only at the start of the string.
    \Z       Matches only at the end of the string.
    \b       Matches the empty string, but only at the start or end of a word.
    \B       Matches the empty string, but not at the start or end of a word.
    \d       Matches any decimal digit; equivalent to the set [0-9] in
             bytes patterns or string patterns with the ASCII flag.
             In string patterns without the ASCII flag, it will match the whole
             range of Unicode digits.
    \D       Matches any non-digit character; equivalent to [^\d].
    \s       Matches any whitespace character; equivalent to [ \t\n\r\f\v] in
             bytes patterns or string patterns with the ASCII flag.
             In string patterns without the ASCII flag, it will match the whole
             range of Unicode whitespace characters.
    \S       Matches any non-whitespace character; equivalent to [^\s].
    \w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_]
             in bytes patterns or string patterns with the ASCII flag.
             In string patterns without the ASCII flag, it will match the
             range of Unicode alphanumeric characters (letters plus digits
             plus underscore).
             With LOCALE, it will match the set [0-9_] plus characters defined
             as letters for the current locale.
    \W       Matches the complement of \w.
    \\       Matches a literal backslash.

This module exports the following functions:
    match     Match a regular expression pattern to the beginning of a string.
    fullmatch Match a regular expression pattern to all of a string.
    search    Search a string for the presence of a pattern.
    sub       Substitute occurrences of a pattern found in a string.
    subn      Same as sub, but also rudisha the number of substitutions made.
    split     Split a string by the occurrences of a pattern.
    findall   Find all occurrences of a pattern in a string.
    finditer  Return an iterator yielding a Match object for each match.
    compile   Compile a pattern into a Pattern object.
    purge     Clear the regular expression cache.
    escape    Backslash all non-alphanumerics in a string.

Some of the functions in this module takes flags as optional parameters:
    A  ASCII       For string patterns, make \w, \W, \b, \B, \d, \D
                   match the corresponding ASCII character categories
                   (rather than the whole Unicode categories, which is the
                   default).
                   For bytes patterns, this flag is the only available
                   behaviour and needn't be specified.
    I  IGNORECASE  Perform case-insensitive matching.
    L  LOCALE      Make \w, \W, \b, \B, dependent on the current locale.
    M  MULTILINE   "^" matches the beginning of lines (after a newline)
                   as well as the string.
                   "$" matches the end of lines (before a newline) as well
                   as the end of the string.
    S  DOTALL      "." matches any character at all, including the newline.
    X  VERBOSE     Ignore whitespace and comments for nicer looking RE's.
    U  UNICODE     For compatibility only. Ignored for string patterns (it
                   is the default), and forbidden for bytes patterns.

This module also defines an exception 'error'.

"""

agiza enum
agiza sre_compile
agiza sre_parse
agiza functools
try:
    agiza _locale
except ImportError:
    _locale = None


# public symbols
__all__ = [
    "match", "fullmatch", "search", "sub", "subn", "split",
    "findall", "finditer", "compile", "purge", "template", "escape",
    "error", "Pattern", "Match", "A", "I", "L", "M", "S", "X", "U",
    "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE",
    "UNICODE",
]

__version__ = "2.2.1"

kundi RegexFlag(enum.IntFlag):
    ASCII = A = sre_compile.SRE_FLAG_ASCII # assume ascii "locale"
    IGNORECASE = I = sre_compile.SRE_FLAG_IGNORECASE # ignore case
    LOCALE = L = sre_compile.SRE_FLAG_LOCALE # assume current 8-bit locale
    UNICODE = U = sre_compile.SRE_FLAG_UNICODE # assume unicode "locale"
    MULTILINE = M = sre_compile.SRE_FLAG_MULTILINE # make anchors look for newline
    DOTALL = S = sre_compile.SRE_FLAG_DOTALL # make dot match newline
    VERBOSE = X = sre_compile.SRE_FLAG_VERBOSE # ignore whitespace and comments
    # sre extensions (experimental, don't rely on these)
    TEMPLATE = T = sre_compile.SRE_FLAG_TEMPLATE # disable backtracking
    DEBUG = sre_compile.SRE_FLAG_DEBUG # dump pattern after compilation

    eleza __repr__(self):
        ikiwa self._name_ is not None:
            rudisha f're.{self._name_}'
        value = self._value_
        members = []
        negative = value < 0
        ikiwa negative:
            value = ~value
        for m in self.__class__:
            ikiwa value & m._value_:
                value &= ~m._value_
                members.append(f're.{m._name_}')
        ikiwa value:
            members.append(hex(value))
        res = '|'.join(members)
        ikiwa negative:
            ikiwa len(members) > 1:
                res = f'~({res})'
            else:
                res = f'~{res}'
        rudisha res
    __str__ = object.__str__

globals().update(RegexFlag.__members__)

# sre exception
error = sre_compile.error

# --------------------------------------------------------------------
# public interface

eleza match(pattern, string, flags=0):
    """Try to apply the pattern at the start of the string, returning
    a Match object, or None ikiwa no match was found."""
    rudisha _compile(pattern, flags).match(string)

eleza fullmatch(pattern, string, flags=0):
    """Try to apply the pattern to all of the string, returning
    a Match object, or None ikiwa no match was found."""
    rudisha _compile(pattern, flags).fullmatch(string)

eleza search(pattern, string, flags=0):
    """Scan through string looking for a match to the pattern, returning
    a Match object, or None ikiwa no match was found."""
    rudisha _compile(pattern, flags).search(string)

eleza sub(pattern, repl, string, count=0, flags=0):
    """Return the string obtained by replacing the leftmost
    non-overlapping occurrences of the pattern in string by the
    replacement repl.  repl can be either a string or a callable;
    ikiwa a string, backslash escapes in it are processed.  If it is
    a callable, it's passed the Match object and must return
    a replacement string to be used."""
    rudisha _compile(pattern, flags).sub(repl, string, count)

eleza subn(pattern, repl, string, count=0, flags=0):
    """Return a 2-tuple containing (new_string, number).
    new_string is the string obtained by replacing the leftmost
    non-overlapping occurrences of the pattern in the source
    string by the replacement repl.  number is the number of
    substitutions that were made. repl can be either a string or a
    callable; ikiwa a string, backslash escapes in it are processed.
    If it is a callable, it's passed the Match object and must
    rudisha a replacement string to be used."""
    rudisha _compile(pattern, flags).subn(repl, string, count)

eleza split(pattern, string, maxsplit=0, flags=0):
    """Split the source string by the occurrences of the pattern,
    returning a list containing the resulting substrings.  If
    capturing parentheses are used in pattern, then the text of all
    groups in the pattern are also returned as part of the resulting
    list.  If maxsplit is nonzero, at most maxsplit splits occur,
    and the remainder of the string is returned as the final element
    of the list."""
    rudisha _compile(pattern, flags).split(string, maxsplit)

eleza findall(pattern, string, flags=0):
    """Return a list of all non-overlapping matches in the string.

    If one or more capturing groups are present in the pattern, return
    a list of groups; this will be a list of tuples ikiwa the pattern
    has more than one group.

    Empty matches are included in the result."""
    rudisha _compile(pattern, flags).findall(string)

eleza finditer(pattern, string, flags=0):
    """Return an iterator over all non-overlapping matches in the
    string.  For each match, the iterator returns a Match object.

    Empty matches are included in the result."""
    rudisha _compile(pattern, flags).finditer(string)

eleza compile(pattern, flags=0):
    "Compile a regular expression pattern, returning a Pattern object."
    rudisha _compile(pattern, flags)

eleza purge():
    "Clear the regular expression caches"
    _cache.clear()
    _compile_repl.cache_clear()

eleza template(pattern, flags=0):
    "Compile a template pattern, returning a Pattern object"
    rudisha _compile(pattern, flags|T)

# SPECIAL_CHARS
# closing ')', '}' and ']'
# '-' (a range in character set)
# '&', '~', (extended character set operations)
# '#' (comment) and WHITESPACE (ignored) in verbose mode
_special_chars_map = {i: '\\' + chr(i) for i in b'()[]{}?*+-|^$\\.&~# \t\n\r\v\f'}

eleza escape(pattern):
    """
    Escape special characters in a string.
    """
    ikiwa isinstance(pattern, str):
        rudisha pattern.translate(_special_chars_map)
    else:
        pattern = str(pattern, 'latin1')
        rudisha pattern.translate(_special_chars_map).encode('latin1')

Pattern = type(sre_compile.compile('', 0))
Match = type(sre_compile.compile('', 0).match(''))

# --------------------------------------------------------------------
# internals

_cache = {}  # ordered!

_MAXCACHE = 512
eleza _compile(pattern, flags):
    # internal: compile pattern
    ikiwa isinstance(flags, RegexFlag):
        flags = flags.value
    try:
        rudisha _cache[type(pattern), pattern, flags]
    except KeyError:
        pass
    ikiwa isinstance(pattern, Pattern):
        ikiwa flags:
            raise ValueError(
                "cannot process flags argument with a compiled pattern")
        rudisha pattern
    ikiwa not sre_compile.isstring(pattern):
        raise TypeError("first argument must be string or compiled pattern")
    p = sre_compile.compile(pattern, flags)
    ikiwa not (flags & DEBUG):
        ikiwa len(_cache) >= _MAXCACHE:
            # Drop the oldest item
            try:
                del _cache[next(iter(_cache))]
            except (StopIteration, RuntimeError, KeyError):
                pass
        _cache[type(pattern), pattern, flags] = p
    rudisha p

@functools.lru_cache(_MAXCACHE)
eleza _compile_repl(repl, pattern):
    # internal: compile replacement pattern
    rudisha sre_parse.parse_template(repl, pattern)

eleza _expand(pattern, match, template):
    # internal: Match.expand implementation hook
    template = sre_parse.parse_template(template, pattern)
    rudisha sre_parse.expand_template(template, match)

eleza _subx(pattern, template):
    # internal: Pattern.sub/subn implementation helper
    template = _compile_repl(template, pattern)
    ikiwa not template[0] and len(template[1]) == 1:
        # literal replacement
        rudisha template[1][0]
    eleza filter(match, template=template):
        rudisha sre_parse.expand_template(template, match)
    rudisha filter

# register myself for pickling

agiza copyreg

eleza _pickle(p):
    rudisha _compile, (p.pattern, p.flags)

copyreg.pickle(Pattern, _pickle, _compile)

# --------------------------------------------------------------------
# experimental stuff (see python-dev discussions for details)

kundi Scanner:
    eleza __init__(self, lexicon, flags=0):
        kutoka sre_constants agiza BRANCH, SUBPATTERN
        ikiwa isinstance(flags, RegexFlag):
            flags = flags.value
        self.lexicon = lexicon
        # combine phrases into a compound pattern
        p = []
        s = sre_parse.State()
        s.flags = flags
        for phrase, action in lexicon:
            gid = s.opengroup()
            p.append(sre_parse.SubPattern(s, [
                (SUBPATTERN, (gid, 0, 0, sre_parse.parse(phrase, flags))),
                ]))
            s.closegroup(gid, p[-1])
        p = sre_parse.SubPattern(s, [(BRANCH, (None, p))])
        self.scanner = sre_compile.compile(p)
    eleza scan(self, string):
        result = []
        append = result.append
        match = self.scanner.scanner(string).match
        i = 0
        while True:
            m = match()
            ikiwa not m:
                break
            j = m.end()
            ikiwa i == j:
                break
            action = self.lexicon[m.lastindex-1][1]
            ikiwa callable(action):
                self.match = m
                action = action(self, m.group())
            ikiwa action is not None:
                append(action)
            i = j
        rudisha result, string[i:]
