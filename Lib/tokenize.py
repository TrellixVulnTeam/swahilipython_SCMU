"""Tokenization help kila Python programs.

tokenize(readline) ni a generator that komas a stream of bytes into
Python tokens.  It decodes the bytes according to PEP-0263 for
determining source file encoding.

It accepts a readline-like method which ni called repeatedly to get the
next line of input (or b"" kila EOF).  It generates 5-tuples ukijumuisha these
members:

    the token type (see token.py)
    the token (a string)
    the starting (row, column) indices of the token (a 2-tuple of ints)
    the ending (row, column) indices of the token (a 2-tuple of ints)
    the original line (string)

It ni designed to match the working of the Python tokenizer exactly, except
that it produces COMMENT tokens kila comments na gives type OP kila all
operators.  Additionally, all token lists start ukijumuisha an ENCODING token
which tells you which encoding was used to decode the bytes stream.
"""

__author__ = 'Ka-Ping Yee <ping@lfw.org>'
__credits__ = ('GvR, ESR, Tim Peters, Thomas Wouters, Fred Drake, '
               'Skip Montanaro, Raymond Hettinger, Trent Nelson, '
               'Michael Foord')
kutoka builtins agiza open kama _builtin_open
kutoka codecs agiza lookup, BOM_UTF8
agiza collections
kutoka io agiza TextIOWrapper
agiza itertools kama _itertools
agiza re
agiza sys
kutoka token agiza *
kutoka token agiza EXACT_TOKEN_TYPES

cookie_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)', re.ASCII)
blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)', re.ASCII)

agiza token
__all__ = token.__all__ + ["tokenize", "generate_tokens", "detect_encoding",
                           "untokenize", "TokenInfo"]
toa token

kundi TokenInfo(collections.namedtuple('TokenInfo', 'type string start end line')):
    eleza __repr__(self):
        annotated_type = '%d (%s)' % (self.type, tok_name[self.type])
        rudisha ('TokenInfo(type=%s, string=%r, start=%r, end=%r, line=%r)' %
                self._replace(type=annotated_type))

    @property
    eleza exact_type(self):
        ikiwa self.type == OP na self.string kwenye EXACT_TOKEN_TYPES:
            rudisha EXACT_TOKEN_TYPES[self.string]
        isipokua:
            rudisha self.type

eleza group(*choices): rudisha '(' + '|'.join(choices) + ')'
eleza any(*choices): rudisha group(*choices) + '*'
eleza maybe(*choices): rudisha group(*choices) + '?'

# Note: we use unicode matching kila names ("\w") but ascii matching for
# number literals.
Whitespace = r'[ \f\t]*'
Comment = r'#[^\r\n]*'
Ignore = Whitespace + any(r'\\\r?\n' + Whitespace) + maybe(Comment)
Name = r'\w+'

Hexnumber = r'0[xX](?:_?[0-9a-fA-F])+'
Binnumber = r'0[bB](?:_?[01])+'
Octnumber = r'0[oO](?:_?[0-7])+'
Decnumber = r'(?:0(?:_?0)*|[1-9](?:_?[0-9])*)'
Intnumber = group(Hexnumber, Binnumber, Octnumber, Decnumber)
Exponent = r'[eE][-+]?[0-9](?:_?[0-9])*'
Pointfloat = group(r'[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?',
                   r'\.[0-9](?:_?[0-9])*') + maybe(Exponent)
Expfloat = r'[0-9](?:_?[0-9])*' + Exponent
Floatnumber = group(Pointfloat, Expfloat)
Imagnumber = group(r'[0-9](?:_?[0-9])*[jJ]', Floatnumber + r'[jJ]')
Number = group(Imagnumber, Floatnumber, Intnumber)

# Return the empty string, plus all of the valid string prefixes.
eleza _all_string_prefixes():
    # The valid string prefixes. Only contain the lower case versions,
    #  na don't contain any permutations (include 'fr', but not
    #  'rf'). The various permutations will be generated.
    _valid_string_prefixes = ['b', 'r', 'u', 'f', 'br', 'fr']
    # ikiwa we add binary f-strings, add: ['fb', 'fbr']
    result = {''}
    kila prefix kwenye _valid_string_prefixes:
        kila t kwenye _itertools.permutations(prefix):
            # create a list ukijumuisha upper na lower versions of each
            #  character
            kila u kwenye _itertools.product(*[(c, c.upper()) kila c kwenye t]):
                result.add(''.join(u))
    rudisha result

eleza _compile(expr):
    rudisha re.compile(expr, re.UNICODE)

# Note that since _all_string_prefixes includes the empty string,
#  StringPrefix can be the empty string (making it optional).
StringPrefix = group(*_all_string_prefixes())

# Tail end of ' string.
Single = r"[^'\\]*(?:\\.[^'\\]*)*'"
# Tail end of " string.
Double = r'[^"\\]*(?:\\.[^"\\]*)*"'
# Tail end of ''' string.
Single3 = r"[^'\\]*(?:(?:\\.|'(?!''))[^'\\]*)*'''"
# Tail end of """ string.
Double3 = r'[^"\\]*(?:(?:\\.|"(?!""))[^"\\]*)*"""'
Triple = group(StringPrefix + "'''", StringPrefix + '"""')
# Single-line ' ama " string.
String = group(StringPrefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'",
               StringPrefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"')

# Sorting kwenye reverse order puts the long operators before their prefixes.
# Otherwise ikiwa = came before ==, == would get recognized kama two instances
# of =.
Special = group(*map(re.escape, sorted(EXACT_TOKEN_TYPES, reverse=Kweli)))
Funny = group(r'\r?\n', Special)

PlainToken = group(Number, Funny, String, Name)
Token = Ignore + PlainToken

# First (or only) line of ' ama " string.
ContStr = group(StringPrefix + r"'[^\n'\\]*(?:\\.[^\n'\\]*)*" +
                group("'", r'\\\r?\n'),
                StringPrefix + r'"[^\n"\\]*(?:\\.[^\n"\\]*)*' +
                group('"', r'\\\r?\n'))
PseudoExtras = group(r'\\\r?\n|\Z', Comment, Triple)
PseudoToken = Whitespace + group(PseudoExtras, Number, Funny, ContStr, Name)

# For a given string prefix plus quotes, endpats maps it to a regex
#  to match the remainder of that string. _prefix can be empty, for
#  a normal single ama triple quoted string (ukijumuisha no prefix).
endpats = {}
kila _prefix kwenye _all_string_prefixes():
    endpats[_prefix + "'"] = Single
    endpats[_prefix + '"'] = Double
    endpats[_prefix + "'''"] = Single3
    endpats[_prefix + '"""'] = Double3

# A set of all of the single na triple quoted string prefixes,
#  including the opening quotes.
single_quoted = set()
triple_quoted = set()
kila t kwenye _all_string_prefixes():
    kila u kwenye (t + '"', t + "'"):
        single_quoted.add(u)
    kila u kwenye (t + '"""', t + "'''"):
        triple_quoted.add(u)

tabsize = 8

kundi TokenError(Exception): pita

kundi StopTokenizing(Exception): pita


kundi Untokenizer:

    eleza __init__(self):
        self.tokens = []
        self.prev_row = 1
        self.prev_col = 0
        self.encoding = Tupu

    eleza add_whitespace(self, start):
        row, col = start
        ikiwa row < self.prev_row ama row == self.prev_row na col < self.prev_col:
            ashiria ValueError("start ({},{}) precedes previous end ({},{})"
                             .format(row, col, self.prev_row, self.prev_col))
        row_offset = row - self.prev_row
        ikiwa row_offset:
            self.tokens.append("\\\n" * row_offset)
            self.prev_col = 0
        col_offset = col - self.prev_col
        ikiwa col_offset:
            self.tokens.append(" " * col_offset)

    eleza untokenize(self, iterable):
        it = iter(iterable)
        indents = []
        startline = Uongo
        kila t kwenye it:
            ikiwa len(t) == 2:
                self.compat(t, it)
                koma
            tok_type, token, start, end, line = t
            ikiwa tok_type == ENCODING:
                self.encoding = token
                endelea
            ikiwa tok_type == ENDMARKER:
                koma
            ikiwa tok_type == INDENT:
                indents.append(token)
                endelea
            lasivyo tok_type == DEDENT:
                indents.pop()
                self.prev_row, self.prev_col = end
                endelea
            lasivyo tok_type kwenye (NEWLINE, NL):
                startline = Kweli
            lasivyo startline na indents:
                indent = indents[-1]
                ikiwa start[1] >= len(indent):
                    self.tokens.append(indent)
                    self.prev_col = len(indent)
                startline = Uongo
            self.add_whitespace(start)
            self.tokens.append(token)
            self.prev_row, self.prev_col = end
            ikiwa tok_type kwenye (NEWLINE, NL):
                self.prev_row += 1
                self.prev_col = 0
        rudisha "".join(self.tokens)

    eleza compat(self, token, iterable):
        indents = []
        toks_append = self.tokens.append
        startline = token[0] kwenye (NEWLINE, NL)
        prevstring = Uongo

        kila tok kwenye _itertools.chain([token], iterable):
            toknum, tokval = tok[:2]
            ikiwa toknum == ENCODING:
                self.encoding = tokval
                endelea

            ikiwa toknum kwenye (NAME, NUMBER):
                tokval += ' '

            # Insert a space between two consecutive strings
            ikiwa toknum == STRING:
                ikiwa prevstring:
                    tokval = ' ' + tokval
                prevstring = Kweli
            isipokua:
                prevstring = Uongo

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


eleza untokenize(iterable):
    """Transform tokens back into Python source code.
    It returns a bytes object, encoded using the ENCODING
    token, which ni the first token sequence output by tokenize.

    Each element returned by the iterable must be a token sequence
    ukijumuisha at least two elements, a token number na token value.  If
    only two tokens are pitaed, the resulting output ni poor.

    Round-trip invariant kila full input:
        Untokenized source will match input source exactly

    Round-trip invariant kila limited input:
        # Output bytes will tokenize back to the input
        t1 = [tok[:2] kila tok kwenye tokenize(f.readline)]
        newcode = untokenize(t1)
        readline = BytesIO(newcode).readline
        t2 = [tok[:2] kila tok kwenye tokenize(readline)]
        assert t1 == t2
    """
    ut = Untokenizer()
    out = ut.untokenize(iterable)
    ikiwa ut.encoding ni sio Tupu:
        out = out.encode(ut.encoding)
    rudisha out


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
    be used to decode a Python source file.  It requires one argument, readline,
    kwenye the same way kama the tokenize() generator.

    It will call readline a maximum of twice, na rudisha the encoding used
    (as a string) na a list of any lines (left kama bytes) it has read in.

    It detects the encoding kutoka the presence of a utf-8 bom ama an encoding
    cookie kama specified kwenye pep-0263.  If both a bom na a cookie are present,
    but disagree, a SyntaxError will be raised.  If the encoding cookie ni an
    invalid charset, ashiria a SyntaxError.  Note that ikiwa a utf-8 bom ni found,
    'utf-8-sig' ni returned.

    If no encoding ni specified, then the default of 'utf-8' will be returned.
    """
    jaribu:
        filename = readline.__self__.name
    tatizo AttributeError:
        filename = Tupu
    bom_found = Uongo
    encoding = Tupu
    default = 'utf-8'
    eleza read_or_stop():
        jaribu:
            rudisha readline()
        tatizo StopIteration:
            rudisha b''

    eleza find_cookie(line):
        jaribu:
            # Decode kama UTF-8. Either the line ni an encoding declaration,
            # kwenye which case it should be pure ASCII, ama it must be UTF-8
            # per default encoding.
            line_string = line.decode('utf-8')
        tatizo UnicodeDecodeError:
            msg = "invalid ama missing encoding declaration"
            ikiwa filename ni sio Tupu:
                msg = '{} kila {!r}'.format(msg, filename)
            ashiria SyntaxError(msg)

        match = cookie_re.match(line_string)
        ikiwa sio match:
            rudisha Tupu
        encoding = _get_normal_name(match.group(1))
        jaribu:
            codec = lookup(encoding)
        tatizo LookupError:
            # This behaviour mimics the Python interpreter
            ikiwa filename ni Tupu:
                msg = "unknown encoding: " + encoding
            isipokua:
                msg = "unknown encoding kila {!r}: {}".format(filename,
                        encoding)
            ashiria SyntaxError(msg)

        ikiwa bom_found:
            ikiwa encoding != 'utf-8':
                # This behaviour mimics the Python interpreter
                ikiwa filename ni Tupu:
                    msg = 'encoding problem: utf-8'
                isipokua:
                    msg = 'encoding problem kila {!r}: utf-8'.format(filename)
                ashiria SyntaxError(msg)
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


eleza open(filename):
    """Open a file kwenye read only mode using the encoding detected by
    detect_encoding().
    """
    buffer = _builtin_open(filename, 'rb')
    jaribu:
        encoding, lines = detect_encoding(buffer.readline)
        buffer.seek(0)
        text = TextIOWrapper(buffer, encoding, line_buffering=Kweli)
        text.mode = 'r'
        rudisha text
    tatizo:
        buffer.close()
        raise


eleza tokenize(readline):
    """
    The tokenize() generator requires one argument, readline, which
    must be a callable object which provides the same interface kama the
    readline() method of built-in file objects.  Each call to the function
    should rudisha one line of input kama bytes.  Alternatively, readline
    can be a callable function terminating ukijumuisha StopIteration:
        readline = open(myfile, 'rb').__next__  # Example of alternate readline

    The generator produces 5-tuples ukijumuisha these members: the token type; the
    token string; a 2-tuple (srow, scol) of ints specifying the row na
    column where the token begins kwenye the source; a 2-tuple (erow, ecol) of
    ints specifying the row na column where the token ends kwenye the source;
    na the line on which the token was found.  The line pitaed ni the
    physical line.

    The first token sequence will always be an ENCODING token
    which tells you which encoding was used to decode the bytes stream.
    """
    encoding, consumed = detect_encoding(readline)
    empty = _itertools.repeat(b"")
    rl_gen = _itertools.chain(consumed, iter(readline, b""), empty)
    rudisha _tokenize(rl_gen.__next__, encoding)


eleza _tokenize(readline, encoding):
    lnum = parenlev = endelead = 0
    numchars = '0123456789'
    contstr, needcont = '', 0
    contline = Tupu
    indents = [0]

    ikiwa encoding ni sio Tupu:
        ikiwa encoding == "utf-8-sig":
            # BOM will already have been stripped.
            encoding = "utf-8"
        tuma TokenInfo(ENCODING, encoding, (0, 0), (0, 0), '')
    last_line = b''
    line = b''
    wakati Kweli:                                # loop over lines kwenye stream
        jaribu:
            # We capture the value of the line variable here because
            # readline uses the empty string '' to signal end of input,
            # hence `line` itself will always be overwritten at the end
            # of this loop.
            last_line = line
            line = readline()
        tatizo StopIteration:
            line = b''

        ikiwa encoding ni sio Tupu:
            line = line.decode(encoding)
        lnum += 1
        pos, max = 0, len(line)

        ikiwa contstr:                            # endelead string
            ikiwa sio line:
                ashiria TokenError("EOF kwenye multi-line string", strstart)
            endmatch = endprog.match(line)
            ikiwa endmatch:
                pos = end = endmatch.end(0)
                tuma TokenInfo(STRING, contstr + line[:end],
                       strstart, (lnum, end), contline + line)
                contstr, needcont = '', 0
                contline = Tupu
            lasivyo needcont na line[-2:] != '\\\n' na line[-3:] != '\\\r\n':
                tuma TokenInfo(ERRORTOKEN, contstr + line,
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
                ikiwa line[pos] == ' ':
                    column += 1
                lasivyo line[pos] == '\t':
                    column = (column//tabsize + 1)*tabsize
                lasivyo line[pos] == '\f':
                    column = 0
                isipokua:
                    koma
                pos += 1
            ikiwa pos == max:
                koma

            ikiwa line[pos] kwenye '#\r\n':           # skip comments ama blank lines
                ikiwa line[pos] == '#':
                    comment_token = line[pos:].rstrip('\r\n')
                    tuma TokenInfo(COMMENT, comment_token,
                           (lnum, pos), (lnum, pos + len(comment_token)), line)
                    pos += len(comment_token)

                tuma TokenInfo(NL, line[pos:],
                           (lnum, pos), (lnum, len(line)), line)
                endelea

            ikiwa column > indents[-1]:           # count indents ama dedents
                indents.append(column)
                tuma TokenInfo(INDENT, line[:pos], (lnum, 0), (lnum, pos), line)
            wakati column < indents[-1]:
                ikiwa column haiko kwenye indents:
                    ashiria IndentationError(
                        "unindent does sio match any outer indentation level",
                        ("<tokenize>", lnum, pos, line))
                indents = indents[:-1]

                tuma TokenInfo(DEDENT, '', (lnum, pos), (lnum, pos), line)

        isipokua:                                  # endelead statement
            ikiwa sio line:
                ashiria TokenError("EOF kwenye multi-line statement", (lnum, 0))
            endelead = 0

        wakati pos < max:
            pseudomatch = _compile(PseudoToken).match(line, pos)
            ikiwa pseudomatch:                                # scan kila tokens
                start, end = pseudomatch.span(1)
                spos, epos, pos = (lnum, start), (lnum, end), end
                ikiwa start == end:
                    endelea
                token, initial = line[start:end], line[start]

                ikiwa (initial kwenye numchars ama                 # ordinary number
                    (initial == '.' na token != '.' na token != '...')):
                    tuma TokenInfo(NUMBER, token, spos, epos, line)
                lasivyo initial kwenye '\r\n':
                    ikiwa parenlev > 0:
                        tuma TokenInfo(NL, token, spos, epos, line)
                    isipokua:
                        tuma TokenInfo(NEWLINE, token, spos, epos, line)

                lasivyo initial == '#':
                    assert sio token.endswith("\n")
                    tuma TokenInfo(COMMENT, token, spos, epos, line)

                lasivyo token kwenye triple_quoted:
                    endprog = _compile(endpats[token])
                    endmatch = endprog.match(line, pos)
                    ikiwa endmatch:                           # all on one line
                        pos = endmatch.end(0)
                        token = line[start:pos]
                        tuma TokenInfo(STRING, token, spos, (lnum, pos), line)
                    isipokua:
                        strstart = (lnum, start)           # multiple lines
                        contstr = line[start:]
                        contline = line
                        koma

                # Check up to the first 3 chars of the token to see if
                #  they're kwenye the single_quoted set. If so, they start
                #  a string.
                # We're using the first 3, because we're looking for
                #  "rb'" (kila example) at the start of the token. If
                #  we switch to longer prefixes, this needs to be
                #  adjusted.
                # Note that initial == token[:1].
                # Also note that single quote checking must come after
                #  triple quote checking (above).
                lasivyo (initial kwenye single_quoted ama
                      token[:2] kwenye single_quoted ama
                      token[:3] kwenye single_quoted):
                    ikiwa token[-1] == '\n':                  # endelead string
                        strstart = (lnum, start)
                        # Again, using the first 3 chars of the
                        #  token. This ni looking kila the matching end
                        #  regex kila the correct type of quote
                        #  character. So it's really looking for
                        #  endpats["'"] ama endpats['"'], by trying to
                        #  skip string prefix characters, ikiwa any.
                        endprog = _compile(endpats.get(initial) ama
                                           endpats.get(token[1]) ama
                                           endpats.get(token[2]))
                        contstr, needcont = line[start:], 1
                        contline = line
                        koma
                    isipokua:                                  # ordinary string
                        tuma TokenInfo(STRING, token, spos, epos, line)

                lasivyo initial.isidentifier():               # ordinary name
                    tuma TokenInfo(NAME, token, spos, epos, line)
                lasivyo initial == '\\':                      # endelead stmt
                    endelead = 1
                isipokua:
                    ikiwa initial kwenye '([{':
                        parenlev += 1
                    lasivyo initial kwenye ')]}':
                        parenlev -= 1
                    tuma TokenInfo(OP, token, spos, epos, line)
            isipokua:
                tuma TokenInfo(ERRORTOKEN, line[pos],
                           (lnum, pos), (lnum, pos+1), line)
                pos += 1

    # Add an implicit NEWLINE ikiwa the input doesn't end kwenye one
    ikiwa last_line na last_line[-1] haiko kwenye '\r\n':
        tuma TokenInfo(NEWLINE, '', (lnum - 1, len(last_line)), (lnum - 1, len(last_line) + 1), '')
    kila indent kwenye indents[1:]:                 # pop remaining indent levels
        tuma TokenInfo(DEDENT, '', (lnum, 0), (lnum, 0), '')
    tuma TokenInfo(ENDMARKER, '', (lnum, 0), (lnum, 0), '')


eleza generate_tokens(readline):
    """Tokenize a source reading Python code kama unicode strings.

    This has the same API kama tokenize(), tatizo that it expects the *readline*
    callable to rudisha str objects instead of bytes.
    """
    rudisha _tokenize(readline, Tupu)

eleza main():
    agiza argparse

    # Helper error handling routines
    eleza perror(message):
        sys.stderr.write(message)
        sys.stderr.write('\n')

    eleza error(message, filename=Tupu, location=Tupu):
        ikiwa location:
            args = (filename,) + location + (message,)
            perror("%s:%d:%d: error: %s" % args)
        lasivyo filename:
            perror("%s: error: %s" % (filename, message))
        isipokua:
            perror("error: %s" % message)
        sys.exit(1)

    # Parse the arguments na options
    parser = argparse.ArgumentParser(prog='python -m tokenize')
    parser.add_argument(dest='filename', nargs='?',
                        metavar='filename.py',
                        help='the file to tokenize; defaults to stdin')
    parser.add_argument('-e', '--exact', dest='exact', action='store_true',
                        help='display token names using the exact type')
    args = parser.parse_args()

    jaribu:
        # Tokenize the input
        ikiwa args.filename:
            filename = args.filename
            ukijumuisha _builtin_open(filename, 'rb') kama f:
                tokens = list(tokenize(f.readline))
        isipokua:
            filename = "<stdin>"
            tokens = _tokenize(sys.stdin.readline, Tupu)

        # Output the tokenization
        kila token kwenye tokens:
            token_type = token.type
            ikiwa args.exact:
                token_type = token.exact_type
            token_range = "%d,%d-%d,%d:" % (token.start + token.end)
            andika("%-20s%-15s%-15r" %
                  (token_range, tok_name[token_type], token.string))
    tatizo IndentationError kama err:
        line, column = err.args[1][1:3]
        error(err.args[0], filename, (line, column))
    tatizo TokenError kama err:
        line, column = err.args[1]
        error(err.args[0], filename, (line, column))
    tatizo SyntaxError kama err:
        error(err, filename)
    tatizo OSError kama err:
        error(err)
    tatizo KeyboardInterrupt:
        andika("interrupted\n")
    tatizo Exception kama err:
        perror("unexpected error: %s" % err)
        raise

ikiwa __name__ == "__main__":
    main()
