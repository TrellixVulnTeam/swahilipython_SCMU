# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation.
# All rights reserved.

"""Tokenization help kila Python programs.

generate_tokens(readline) ni a generator that komas a stream of
text into Python tokens.  It accepts a readline-like method which ni called
repeatedly to get the next line of input (or "" kila EOF).  It generates
5-tuples ukijumuisha these members:

    the token type (see token.py)
    the token (a string)
    the starting (row, column) indices of the token (a 2-tuple of ints)
    the ending (row, column) indices of the token (a 2-tuple of ints)
    the original line (string)

It ni designed to match the working of the Python tokenizer exactly, except
that it produces COMMENT tokens kila comments na gives type OP kila all
operators

Older entry points
    tokenize_loop(readline, tokeneater)
    tokenize(readline, tokeneater=printtoken)
are the same, tatizo instead of generating tokens, tokeneater ni a callback
function to which the 5 fields described above are pitaed kama 5 arguments,
each time a new token ni found."""

__author__ = 'Ka-Ping Yee <ping@lfw.org>'
__credits__ = \
    'GvR, ESR, Tim Peters, Thomas Wouters, Fred Drake, Skip Montanaro'

agiza string, re
kutoka codecs agiza BOM_UTF8, lookup
kutoka lib2to3.pgen2.token agiza *

kutoka . agiza token
__all__ = [x kila x kwenye dir(token) ikiwa x[0] != '_'] + ["tokenize",
           "generate_tokens", "untokenize"]
toa token

jaribu:
    bytes
tatizo NameError:
    # Support bytes type kwenye Python <= 2.5, so 2to3 turns itself into
    # valid Python 3 code.
    bytes = str

eleza group(*choices): rudisha '(' + '|'.join(choices) + ')'
eleza any(*choices): rudisha group(*choices) + '*'
eleza maybe(*choices): rudisha group(*choices) + '?'
eleza _combinations(*l):
    rudisha set(
        x + y kila x kwenye l kila y kwenye l + ("",) ikiwa x.casefold() != y.casefold()
    )

Whitespace = r'[ \f\t]*'
Comment = r'#[^\r\n]*'
Ignore = Whitespace + any(r'\\\r?\n' + Whitespace) + maybe(Comment)
Name = r'\w+'

Binnumber = r'0[bB]_?[01]+(?:_[01]+)*'
Hexnumber = r'0[xX]_?[\da-fA-F]+(?:_[\da-fA-F]+)*[lL]?'
Octnumber = r'0[oO]?_?[0-7]+(?:_[0-7]+)*[lL]?'
Decnumber = group(r'[1-9]\d*(?:_\d+)*[lL]?', '0[lL]?')
Intnumber = group(Binnumber, Hexnumber, Octnumber, Decnumber)
Exponent = r'[eE][-+]?\d+(?:_\d+)*'
Pointfloat = group(r'\d+(?:_\d+)*\.(?:\d+(?:_\d+)*)?', r'\.\d+(?:_\d+)*') + maybe(Exponent)
Expfloat = r'\d+(?:_\d+)*' + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Imagnumber = group(r'\d+(?:_\d+)*[jJ]', Floatnumber + r'[jJ]')
Number = group(Imagnumber, Floatnumber, Intnumber)

# Tail end of ' string.
Single = r"[^'\\]*(?:\\.[^'\\]*)*'"
# Tail end of " string.
Double = r'[^"\\]*(?:\\.[^"\\]*)*"'
# Tail end of ''' string.
Single3 = r"[^'\\]*(?:(?:\\.|'(?!''))[^'\\]*)*'''"
# Tail end of """ string.
Double3 = r'[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""'
_litprefix = r"(?:[uUrRbBfF]|[rR][fFbB]|[fFbBuU][rR])?"
Triple = group(_litprefix + "'''", _litprefix + '"""')
# Single-line ' ama " string.
String = group(_litprefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'",
               _litprefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"')

# Because of leftmost-then-longest match semantics, be sure to put the
# longest operators first (e.g., ikiwa = came before ==, == would get
# recognized kama two instances of =).
Operator = group(r"\*\*=?", r">>=?", r"<<=?", r"<>", r"!=",
                 r"//=?", r"->",
                 r"[+\-*/%&@|^=<>]=?",
                 r"~")

Bracket = '[][(){}]'
Special = group(r'\r?\n', r'[:;.,`@]')
Funny = group(Operator, Bracket, Special)

PlainToken = group(Number, Funny, String, Name)
Token = Ignore + PlainToken

# First (or only) line of ' ama " string.
ContStr = group(_litprefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*" +
                group("'", r'\\\r?\n'),
                _litprefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*' +
                group('"', r'\\\r?\n'))
PseudoExtras = group(r'\\\r?\n', Comment, Triple)
PseudoToken = Whitespace + group(PseudoExtras, Number, Funny, ContStr, Name)

tokenprog, pseudoprog, single3prog, double3prog = map(
    re.compile, (Token, PseudoToken, Single3, Double3))

_strprefixes = (
    _combinations('r', 'R', 'f', 'F') |
    _combinations('r', 'R', 'b', 'B') |
    {'u', 'U', 'ur', 'uR', 'Ur', 'UR'}
)

endprogs = {"'": re.compile(Single), '"': re.compile(Double),
            "'''": single3prog, '"""': double3prog,
            **{f"{prefix}'''": single3prog kila prefix kwenye _strprefixes},
            **{f'{prefix}"""': double3prog kila prefix kwenye _strprefixes},
            **{prefix: Tupu kila prefix kwenye _strprefixes}}

triple_quoted = (
    {"'''", '"""'} |
    {f"{prefix}'''" kila prefix kwenye _strprefixes} |
    {f'{prefix}"""' kila prefix kwenye _strprefixes}
)
single_quoted = (
    {"'", '"'} |
    {f"{prefix}'" kila prefix kwenye _strprefixes} |
    {f'{prefix}"' kila prefix kwenye _strprefixes}
)

tabsize = 8

kundi TokenError(Exception): pita

kundi StopTokenizing(Exception): pita

eleza printtoken(type, token, xxx_todo_changeme, xxx_todo_changeme1, line): # kila testing
    (srow, scol) = xxx_todo_changeme
    (erow, ecol) = xxx_todo_changeme1
    andika("%d,%d-%d,%d:\t%s\t%s" % \
        (srow, scol, erow, ecol, tok_name[type], repr(token)))

eleza tokenize(readline, tokeneater=printtoken):
    """
    The tokenize() function accepts two parameters: one representing the
    input stream, na one providing an output mechanism kila tokenize().

    The first parameter, readline, must be a callable object which provides
    the same interface kama the readline() method of built-in file objects.
    Each call to the function should rudisha one line of input kama a string.

    The second parameter, tokeneater, must also be a callable object. It is
    called once kila each token, ukijumuisha five arguments, corresponding to the
    tuples generated by generate_tokens().
    """
    jaribu:
        tokenize_loop(readline, tokeneater)
    tatizo StopTokenizing:
        pita

# backwards compatible interface
eleza tokenize_loop(readline, tokeneater):
    kila token_info kwenye generate_tokens(readline):
        tokeneater(*token_info)

kundi Untokenizer:

    eleza __init__(self):
        self.tokens = []
        self.prev_row = 1
        self.prev_col = 0

    eleza add_whitespace(self, start):
        row, col = start
        assert row <= self.prev_row
        col_offset = col - self.prev_col
        ikiwa col_offset:
            self.tokens.append(" " * col_offset)

    eleza untokenize(self, iterable):
        kila t kwenye iterable:
            ikiwa len(t) == 2:
                self.compat(t, iterable)
                koma
            tok_type, token, start, end, line = t
            self.add_whitespace(start)
            self.tokens.append(token)
            self.prev_row, self.prev_col = end
            ikiwa tok_type kwenye (NEWLINE, NL):
                self.prev_row += 1
                self.prev_col = 0
        rudisha "".join(self.tokens)

    eleza compat(self, token, iterable):
        startline = Uongo
        indents = []
        toks_append = self.tokens.append
        toknum, tokval = token
        ikiwa toknum kwenye (NAME, NUMBER):
            tokval += ' '
        ikiwa toknum kwenye (NEWLINE, NL):
            startline = Kweli
        kila tok kwenye iterable:
            toknum, tokval = tok[:2]

            ikiwa toknum kwenye (NAME, NUMBER, ASYNC, AWAIT):
                tokval += ' '

            ikiwa toknum == INDENT:
                indents.append(tokval)
                endelea
            lasivyo toknum == DEDENT:
                indents.pop()
                endelea
            lasivyo toknum kwenye (NEWLINE, NL):
                startline = Kweli
            lasivyo startline na indents:
                toks_append(indents[-1])
                startline = Uongo
            toks_append(tokval)

cookie_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)', re.ASCII)
blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)', re.ASCII)

eleza _get_normal_name(orig_enc):
    """Imitates get_normal_name kwenye tokenizer.c."""
    # Only care about the first 12 characters.
    enc = orig_enc[:12].lower().replace("_", "-")
    ikiwa enc == "utf-8" ama enc.startswith("utf-8-"):
        rudisha "utf-8"
    ikiwa enc kwenye ("latin-1", "iso-8859-1", "iso-latin-1") ama \
       enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
        rudisha "iso-8859-1"
    rudisha orig_enc

eleza detect_encoding(readline):
    """
    The detect_encoding() function ni used to detect the encoding that should
    be used to decode a Python source file. It requires one argument, readline,
    kwenye the same way kama the tokenize() generator.

    It will call readline a maximum of twice, na rudisha the encoding used
    (as a string) na a list of any lines (left kama bytes) it has read
    in.

    It detects the encoding kutoka the presence of a utf-8 bom ama an encoding
    cookie kama specified kwenye pep-0263. If both a bom na a cookie are present, but
    disagree, a SyntaxError will be ashiriad. If the encoding cookie ni an invalid
    charset, ashiria a SyntaxError.  Note that ikiwa a utf-8 bom ni found,
    'utf-8-sig' ni rudishaed.

    If no encoding ni specified, then the default of 'utf-8' will be rudishaed.
    """
    bom_found = Uongo
    encoding = Tupu
    default = 'utf-8'
    eleza read_or_stop():
        jaribu:
            rudisha readline()
        tatizo StopIteration:
            rudisha bytes()

    eleza find_cookie(line):
        jaribu:
            line_string = line.decode('ascii')
        tatizo UnicodeDecodeError:
            rudisha Tupu
        match = cookie_re.match(line_string)
        ikiwa sio match:
            rudisha Tupu
        encoding = _get_normal_name(match.group(1))
        jaribu:
            codec = lookup(encoding)
        tatizo LookupError:
            # This behaviour mimics the Python interpreter
            ashiria SyntaxError("unknown encoding: " + encoding)

        ikiwa bom_found:
            ikiwa codec.name != 'utf-8':
                # This behaviour mimics the Python interpreter
                ashiria SyntaxError('encoding problem: utf-8')
            encoding += '-sig'
        rudisha encoding

    first = read_or_stop()
    ikiwa first.startswith(BOM_UTF8):
        bom_found = Kweli
        first = first[3:]
        default = 'utf-8-sig'
    ikiwa sio first:
        rudisha default, []

    encoding = find_cookie(first)
    ikiwa encoding:
        rudisha encoding, [first]
    ikiwa sio blank_re.match(first):
        rudisha default, [first]

    second = read_or_stop()
    ikiwa sio second:
        rudisha default, [first]

    encoding = find_cookie(second)
    ikiwa encoding:
        rudisha encoding, [first, second]

    rudisha default, [first, second]

eleza untokenize(iterable):
    """Transform tokens back into Python source code.

    Each element rudishaed by the iterable must be a token sequence
    ukijumuisha at least two elements, a token number na token value.  If
    only two tokens are pitaed, the resulting output ni poor.

    Round-trip invariant kila full input:
        Untokenized source will match input source exactly

    Round-trip invariant kila limited input:
        # Output text will tokenize the back to the input
        t1 = [tok[:2] kila tok kwenye generate_tokens(f.readline)]
        newcode = untokenize(t1)
        readline = iter(newcode.splitlines(1)).next
        t2 = [tok[:2] kila tokin generate_tokens(readline)]
        assert t1 == t2
    """
    ut = Untokenizer()
    rudisha ut.untokenize(iterable)

eleza generate_tokens(readline):
    """
    The generate_tokens() generator requires one argument, readline, which
    must be a callable object which provides the same interface kama the
    readline() method of built-in file objects. Each call to the function
    should rudisha one line of input kama a string.  Alternately, readline
    can be a callable function terminating ukijumuisha StopIteration:
        readline = open(myfile).next    # Example of alternate readline

    The generator produces 5-tuples ukijumuisha these members: the token type; the
    token string; a 2-tuple (srow, scol) of ints specifying the row na
    column where the token begins kwenye the source; a 2-tuple (erow, ecol) of
    ints specifying the row na column where the token ends kwenye the source;
    na the line on which the token was found. The line pitaed ni the
    physical line.
    """
    lnum = parenlev = endelead = 0
    contstr, needcont = '', 0
    contline = Tupu
    indents = [0]

    # 'stashed' na 'async_*' are used kila async/await parsing
    stashed = Tupu
    async_eleza = Uongo
    async_def_indent = 0
    async_def_nl = Uongo

    wakati 1:                                   # loop over lines kwenye stream
        jaribu:
            line = readline()
        tatizo StopIteration:
            line = ''
        lnum = lnum + 1
        pos, max = 0, len(line)

        ikiwa contstr:                            # endelead string
            ikiwa sio line:
                ashiria TokenError("EOF kwenye multi-line string", strstart)
            endmatch = endprog.match(line)
            ikiwa endmatch:
                pos = end = endmatch.end(0)
                tuma (STRING, contstr + line[:end],
                       strstart, (lnum, end), contline + line)
                contstr, needcont = '', 0
                contline = Tupu
            lasivyo needcont na line[-2:] != '\\\n' na line[-3:] != '\\\r\n':
                tuma (ERRORTOKEN, contstr + line,
                           strstart, (lnum, len(line)), contline)
                contstr = ''
                contline = Tupu
                endelea
            isipokua:
                contstr = contstr + line
                contline = contline + line
                endelea

        lasivyo parenlev == 0 na sio endelead:  # new statement
            ikiwa sio line: koma
            column = 0
            wakati pos < max:                   # measure leading whitespace
                ikiwa line[pos] == ' ': column = column + 1
                lasivyo line[pos] == '\t': column = (column//tabsize + 1)*tabsize
                lasivyo line[pos] == '\f': column = 0
                isipokua: koma
                pos = pos + 1
            ikiwa pos == max: koma

            ikiwa stashed:
                tuma stashed
                stashed = Tupu

            ikiwa line[pos] kwenye '#\r\n':           # skip comments ama blank lines
                ikiwa line[pos] == '#':
                    comment_token = line[pos:].rstrip('\r\n')
                    nl_pos = pos + len(comment_token)
                    tuma (COMMENT, comment_token,
                           (lnum, pos), (lnum, pos + len(comment_token)), line)
                    tuma (NL, line[nl_pos:],
                           (lnum, nl_pos), (lnum, len(line)), line)
                isipokua:
                    tuma ((NL, COMMENT)[line[pos] == '#'], line[pos:],
                           (lnum, pos), (lnum, len(line)), line)
                endelea

            ikiwa column > indents[-1]:           # count indents ama dedents
                indents.append(column)
                tuma (INDENT, line[:pos], (lnum, 0), (lnum, pos), line)
            wakati column < indents[-1]:
                ikiwa column haiko kwenye indents:
                    ashiria IndentationError(
                        "unindent does sio match any outer indentation level",
                        ("<tokenize>", lnum, pos, line))
                indents = indents[:-1]

                ikiwa async_eleza na async_def_indent >= indents[-1]:
                    async_eleza = Uongo
                    async_def_nl = Uongo
                    async_def_indent = 0

                tuma (DEDENT, '', (lnum, pos), (lnum, pos), line)

            ikiwa async_eleza na async_def_nl na async_def_indent >= indents[-1]:
                async_eleza = Uongo
                async_def_nl = Uongo
                async_def_indent = 0

        isipokua:                                  # endelead statement
            ikiwa sio line:
                ashiria TokenError("EOF kwenye multi-line statement", (lnum, 0))
            endelead = 0

        wakati pos < max:
            pseudomatch = pseudoprog.match(line, pos)
            ikiwa pseudomatch:                                # scan kila tokens
                start, end = pseudomatch.span(1)
                spos, epos, pos = (lnum, start), (lnum, end), end
                token, initial = line[start:end], line[start]

                ikiwa initial kwenye string.digits ama \
                   (initial == '.' na token != '.'):      # ordinary number
                    tuma (NUMBER, token, spos, epos, line)
                lasivyo initial kwenye '\r\n':
                    newline = NEWLINE
                    ikiwa parenlev > 0:
                        newline = NL
                    lasivyo async_def:
                        async_def_nl = Kweli
                    ikiwa stashed:
                        tuma stashed
                        stashed = Tupu
                    tuma (newline, token, spos, epos, line)

                lasivyo initial == '#':
                    assert sio token.endswith("\n")
                    ikiwa stashed:
                        tuma stashed
                        stashed = Tupu
                    tuma (COMMENT, token, spos, epos, line)
                lasivyo token kwenye triple_quoted:
                    endprog = endprogs[token]
                    endmatch = endprog.match(line, pos)
                    ikiwa endmatch:                           # all on one line
                        pos = endmatch.end(0)
                        token = line[start:pos]
                        ikiwa stashed:
                            tuma stashed
                            stashed = Tupu
                        tuma (STRING, token, spos, (lnum, pos), line)
                    isipokua:
                        strstart = (lnum, start)           # multiple lines
                        contstr = line[start:]
                        contline = line
                        koma
                lasivyo initial kwenye single_quoted ama \
                    token[:2] kwenye single_quoted ama \
                    token[:3] kwenye single_quoted:
                    ikiwa token[-1] == '\n':                  # endelead string
                        strstart = (lnum, start)
                        endprog = (endprogs[initial] ama endprogs[token[1]] ama
                                   endprogs[token[2]])
                        contstr, needcont = line[start:], 1
                        contline = line
                        koma
                    isipokua:                                  # ordinary string
                        ikiwa stashed:
                            tuma stashed
                            stashed = Tupu
                        tuma (STRING, token, spos, epos, line)
                lasivyo initial.isidentifier():               # ordinary name
                    ikiwa token kwenye ('async', 'await'):
                        ikiwa async_def:
                            tuma (ASYNC ikiwa token == 'async' isipokua AWAIT,
                                   token, spos, epos, line)
                            endelea

                    tok = (NAME, token, spos, epos, line)
                    ikiwa token == 'async' na sio stashed:
                        stashed = tok
                        endelea

                    ikiwa token == 'def':
                        ikiwa (stashed
                                na stashed[0] == NAME
                                na stashed[1] == 'async'):

                            async_eleza = Kweli
                            async_def_indent = indents[-1]

                            tuma (ASYNC, stashed[1],
                                   stashed[2], stashed[3],
                                   stashed[4])
                            stashed = Tupu

                    ikiwa stashed:
                        tuma stashed
                        stashed = Tupu

                    tuma tok
                lasivyo initial == '\\':                      # endelead stmt
                    # This tuma ni new; needed kila better idempotency:
                    ikiwa stashed:
                        tuma stashed
                        stashed = Tupu
                    tuma (NL, token, spos, (lnum, pos), line)
                    endelead = 1
                isipokua:
                    ikiwa initial kwenye '([{': parenlev = parenlev + 1
                    lasivyo initial kwenye ')]}': parenlev = parenlev - 1
                    ikiwa stashed:
                        tuma stashed
                        stashed = Tupu
                    tuma (OP, token, spos, epos, line)
            isipokua:
                tuma (ERRORTOKEN, line[pos],
                           (lnum, pos), (lnum, pos+1), line)
                pos = pos + 1

    ikiwa stashed:
        tuma stashed
        stashed = Tupu

    kila indent kwenye indents[1:]:                 # pop remaining indent levels
        tuma (DEDENT, '', (lnum, 0), (lnum, 0), '')
    tuma (ENDMARKER, '', (lnum, 0), (lnum, 0), '')

ikiwa __name__ == '__main__':                     # testing
    agiza sys
    ikiwa len(sys.argv) > 1: tokenize(open(sys.argv[1]).readline)
    isipokua: tokenize(sys.stdin.readline)
