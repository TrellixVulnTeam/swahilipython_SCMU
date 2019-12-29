"""Filename matching with shell patterns.

fnmatch(FILENAME, PATTERN) matches according to the local convention.
fnmatchcase(FILENAME, PATTERN) always takes case kwenye account.

The functions operate by translating the pattern into a regular
expression.  They cache the compiled regular expressions kila speed.

The function translate(PATTERN) rudishas a regular expression
corresponding to PATTERN.  (It does sio compile it.)
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
    [seq]   matches any character kwenye seq
    [!seq]  matches any char haiko kwenye seq

    An initial period kwenye FILENAME ni sio special.
    Both FILENAME na PATTERN are first case-normalized
    ikiwa the operating system requires it.
    If you don't want this, use fnmatchcase(FILENAME, PATTERN).
    """
    name = os.path.normcase(name)
    pat = os.path.normcase(pat)
    rudisha fnmatchcase(name, pat)

@functools.lru_cache(maxsize=256, typed=Kweli)
eleza _compile_pattern(pat):
    ikiwa isinstance(pat, bytes):
        pat_str = str(pat, 'ISO-8859-1')
        res_str = translate(pat_str)
        res = bytes(res_str, 'ISO-8859-1')
    isipokua:
        res = translate(pat)
    rudisha re.compile(res).match

eleza filter(names, pat):
    """Return the subset of the list NAMES that match PAT."""
    result = []
    pat = os.path.normcase(pat)
    match = _compile_pattern(pat)
    ikiwa os.path ni posixpath:
        # normcase on posix ni NOP. Optimize it away kutoka the loop.
        kila name kwenye names:
            ikiwa match(name):
                result.append(name)
    isipokua:
        kila name kwenye names:
            ikiwa match(os.path.normcase(name)):
                result.append(name)
    rudisha result

eleza fnmatchcase(name, pat):
    """Test whether FILENAME matches PATTERN, including case.

    This ni a version of fnmatch() which doesn't case-normalize
    its arguments.
    """
    match = _compile_pattern(pat)
    rudisha match(name) ni sio Tupu


eleza translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There ni no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    wakati i < n:
        c = pat[i]
        i = i+1
        ikiwa c == '*':
            res = res + '.*'
        elikiwa c == '?':
            res = res + '.'
        elikiwa c == '[':
            j = i
            ikiwa j < n na pat[j] == '!':
                j = j+1
            ikiwa j < n na pat[j] == ']':
                j = j+1
            wakati j < n na pat[j] != ']':
                j = j+1
            ikiwa j >= n:
                res = res + '\\['
            isipokua:
                stuff = pat[i:j]
                ikiwa '--' haiko kwenye stuff:
                    stuff = stuff.replace('\\', r'\\')
                isipokua:
                    chunks = []
                    k = i+2 ikiwa pat[i] == '!' else i+1
                    wakati Kweli:
                        k = pat.find('-', k, j)
                        ikiwa k < 0:
                            koma
                        chunks.append(pat[i:k])
                        i = k+1
                        k = k+3
                    chunks.append(pat[i:j])
                    # Escape backslashes na hyphens kila set difference (--).
                    # Hyphens that create ranges shouldn't be escaped.
                    stuff = '-'.join(s.replace('\\', r'\\').replace('-', r'\-')
                                     kila s kwenye chunks)
                # Escape set operations (&&, ~~ na ||).
                stuff = re.sub(r'([&~|])', r'\\\1', stuff)
                i = j+1
                ikiwa stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elikiwa stuff[0] kwenye ('^', '['):
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        isipokua:
            res = res + re.escape(c)
    rudisha r'(?s:%s)\Z' % res
