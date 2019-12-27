"""Filename matching with shell patterns.

fnmatch(FILENAME, PATTERN) matches according to the local convention.
fnmatchcase(FILENAME, PATTERN) always takes case in account.

The functions operate by translating the pattern into a regular
expression.  They cache the compiled regular expressions for speed.

The function translate(PATTERN) returns a regular expression
corresponding to PATTERN.  (It does not compile it.)
"""
agiza os
agiza posixpath
agiza re
agiza functools

__all__ = ["filter", "fnmatch", "fnmatchcase", "translate"]

eleza fnmatch(name, pat):
    """Test whether FILENAME matches PATTERN.

    Patterns are Unix shell style:

    *       matches everything
    ?       matches any single character
    [seq]   matches any character in seq
    [!seq]  matches any char not in seq

    An initial period in FILENAME is not special.
    Both FILENAME and PATTERN are first case-normalized
    ikiwa the operating system requires it.
    If you don't want this, use fnmatchcase(FILENAME, PATTERN).
    """
    name = os.path.normcase(name)
    pat = os.path.normcase(pat)
    rudisha fnmatchcase(name, pat)

@functools.lru_cache(maxsize=256, typed=True)
eleza _compile_pattern(pat):
    ikiwa isinstance(pat, bytes):
        pat_str = str(pat, 'ISO-8859-1')
        res_str = translate(pat_str)
        res = bytes(res_str, 'ISO-8859-1')
    else:
        res = translate(pat)
    rudisha re.compile(res).match

eleza filter(names, pat):
    """Return the subset of the list NAMES that match PAT."""
    result = []
    pat = os.path.normcase(pat)
    match = _compile_pattern(pat)
    ikiwa os.path is posixpath:
        # normcase on posix is NOP. Optimize it away kutoka the loop.
        for name in names:
            ikiwa match(name):
                result.append(name)
    else:
        for name in names:
            ikiwa match(os.path.normcase(name)):
                result.append(name)
    rudisha result

eleza fnmatchcase(name, pat):
    """Test whether FILENAME matches PATTERN, including case.

    This is a version of fnmatch() which doesn't case-normalize
    its arguments.
    """
    match = _compile_pattern(pat)
    rudisha match(name) is not None


eleza translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i+1
        ikiwa c == '*':
            res = res + '.*'
        elikiwa c == '?':
            res = res + '.'
        elikiwa c == '[':
            j = i
            ikiwa j < n and pat[j] == '!':
                j = j+1
            ikiwa j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            ikiwa j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j]
                ikiwa '--' not in stuff:
                    stuff = stuff.replace('\\', r'\\')
                else:
                    chunks = []
                    k = i+2 ikiwa pat[i] == '!' else i+1
                    while True:
                        k = pat.find('-', k, j)
                        ikiwa k < 0:
                            break
                        chunks.append(pat[i:k])
                        i = k+1
                        k = k+3
                    chunks.append(pat[i:j])
                    # Escape backslashes and hyphens for set difference (--).
                    # Hyphens that create ranges shouldn't be escaped.
                    stuff = '-'.join(s.replace('\\', r'\\').replace('-', r'\-')
                                     for s in chunks)
                # Escape set operations (&&, ~~ and ||).
                stuff = re.sub(r'([&~|])', r'\\\1', stuff)
                i = j+1
                ikiwa stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elikiwa stuff[0] in ('^', '['):
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    rudisha r'(?s:%s)\Z' % res
