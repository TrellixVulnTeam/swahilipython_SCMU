"""A lexical analyzer kundi for simple shell-like syntaxes."""

# Module and documentation by Eric S. Raymond, 21 Dec 1998
# Input stacking and error message cleanup added by ESR, March 2000
# push_source() and pop_source() made explicit by ESR, January 2001.
# Posix compliance, split(), string arguments, and
# iterator interface by Gustavo Niemeyer, April 2003.
# changes to tokenize more like Posix shells by Vinay Sajip, July 2016.

agiza os
agiza re
agiza sys
kutoka collections agiza deque

kutoka io agiza StringIO

__all__ = ["shlex", "split", "quote", "join"]

kundi shlex:
    "A lexical analyzer kundi for simple shell-like syntaxes."
    eleza __init__(self, instream=None, infile=None, posix=False,
                 punctuation_chars=False):
        ikiwa isinstance(instream, str):
            instream = StringIO(instream)
        ikiwa instream is not None:
            self.instream = instream
            self.infile = infile
        else:
            self.instream = sys.stdin
            self.infile = None
        self.posix = posix
        ikiwa posix:
            self.eof = None
        else:
            self.eof = ''
        self.commenters = '#'
        self.wordchars = ('abcdfeghijklmnopqrstuvwxyz'
                          'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        ikiwa self.posix:
            self.wordchars += ('ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'
                               'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ')
        self.whitespace = ' \t\r\n'
        self.whitespace_split = False
        self.quotes = '\'"'
        self.escape = '\\'
        self.escapedquotes = '"'
        self.state = ' '
        self.pushback = deque()
        self.lineno = 1
        self.debug = 0
        self.token = ''
        self.filestack = deque()
        self.source = None
        ikiwa not punctuation_chars:
            punctuation_chars = ''
        elikiwa punctuation_chars is True:
            punctuation_chars = '();<>|&'
        self._punctuation_chars = punctuation_chars
        ikiwa punctuation_chars:
            # _pushback_chars is a push back queue used by lookahead logic
            self._pushback_chars = deque()
            # these chars added because allowed in file names, args, wildcards
            self.wordchars += '~-./*?='
            #remove any punctuation chars kutoka wordchars
            t = self.wordchars.maketrans(dict.kutokakeys(punctuation_chars))
            self.wordchars = self.wordchars.translate(t)

    @property
    eleza punctuation_chars(self):
        rudisha self._punctuation_chars

    eleza push_token(self, tok):
        "Push a token onto the stack popped by the get_token method"
        ikiwa self.debug >= 1:
            andika("shlex: pushing token " + repr(tok))
        self.pushback.appendleft(tok)

    eleza push_source(self, newstream, newfile=None):
        "Push an input source onto the lexer's input source stack."
        ikiwa isinstance(newstream, str):
            newstream = StringIO(newstream)
        self.filestack.appendleft((self.infile, self.instream, self.lineno))
        self.infile = newfile
        self.instream = newstream
        self.lineno = 1
        ikiwa self.debug:
            ikiwa newfile is not None:
                andika('shlex: pushing to file %s' % (self.infile,))
            else:
                andika('shlex: pushing to stream %s' % (self.instream,))

    eleza pop_source(self):
        "Pop the input source stack."
        self.instream.close()
        (self.infile, self.instream, self.lineno) = self.filestack.popleft()
        ikiwa self.debug:
            andika('shlex: popping to %s, line %d' \
                  % (self.instream, self.lineno))
        self.state = ' '

    eleza get_token(self):
        "Get a token kutoka the input stream (or kutoka stack ikiwa it's nonempty)"
        ikiwa self.pushback:
            tok = self.pushback.popleft()
            ikiwa self.debug >= 1:
                andika("shlex: popping token " + repr(tok))
            rudisha tok
        # No pushback.  Get a token.
        raw = self.read_token()
        # Handle inclusions
        ikiwa self.source is not None:
            while raw == self.source:
                spec = self.sourcehook(self.read_token())
                ikiwa spec:
                    (newfile, newstream) = spec
                    self.push_source(newstream, newfile)
                raw = self.get_token()
        # Maybe we got EOF instead?
        while raw == self.eof:
            ikiwa not self.filestack:
                rudisha self.eof
            else:
                self.pop_source()
                raw = self.get_token()
        # Neither inclusion nor EOF
        ikiwa self.debug >= 1:
            ikiwa raw != self.eof:
                andika("shlex: token=" + repr(raw))
            else:
                andika("shlex: token=EOF")
        rudisha raw

    eleza read_token(self):
        quoted = False
        escapedstate = ' '
        while True:
            ikiwa self.punctuation_chars and self._pushback_chars:
                nextchar = self._pushback_chars.pop()
            else:
                nextchar = self.instream.read(1)
            ikiwa nextchar == '\n':
                self.lineno += 1
            ikiwa self.debug >= 3:
                andika("shlex: in state %r I see character: %r" % (self.state,
                                                                  nextchar))
            ikiwa self.state is None:
                self.token = ''        # past end of file
                break
            elikiwa self.state == ' ':
                ikiwa not nextchar:
                    self.state = None  # end of file
                    break
                elikiwa nextchar in self.whitespace:
                    ikiwa self.debug >= 2:
                        andika("shlex: I see whitespace in whitespace state")
                    ikiwa self.token or (self.posix and quoted):
                        break   # emit current token
                    else:
                        continue
                elikiwa nextchar in self.commenters:
                    self.instream.readline()
                    self.lineno += 1
                elikiwa self.posix and nextchar in self.escape:
                    escapedstate = 'a'
                    self.state = nextchar
                elikiwa nextchar in self.wordchars:
                    self.token = nextchar
                    self.state = 'a'
                elikiwa nextchar in self.punctuation_chars:
                    self.token = nextchar
                    self.state = 'c'
                elikiwa nextchar in self.quotes:
                    ikiwa not self.posix:
                        self.token = nextchar
                    self.state = nextchar
                elikiwa self.whitespace_split:
                    self.token = nextchar
                    self.state = 'a'
                else:
                    self.token = nextchar
                    ikiwa self.token or (self.posix and quoted):
                        break   # emit current token
                    else:
                        continue
            elikiwa self.state in self.quotes:
                quoted = True
                ikiwa not nextchar:      # end of file
                    ikiwa self.debug >= 2:
                        andika("shlex: I see EOF in quotes state")
                    # XXX what error should be raised here?
                    raise ValueError("No closing quotation")
                ikiwa nextchar == self.state:
                    ikiwa not self.posix:
                        self.token += nextchar
                        self.state = ' '
                        break
                    else:
                        self.state = 'a'
                elikiwa (self.posix and nextchar in self.escape and self.state
                      in self.escapedquotes):
                    escapedstate = self.state
                    self.state = nextchar
                else:
                    self.token += nextchar
            elikiwa self.state in self.escape:
                ikiwa not nextchar:      # end of file
                    ikiwa self.debug >= 2:
                        andika("shlex: I see EOF in escape state")
                    # XXX what error should be raised here?
                    raise ValueError("No escaped character")
                # In posix shells, only the quote itself or the escape
                # character may be escaped within quotes.
                ikiwa (escapedstate in self.quotes and
                        nextchar != self.state and nextchar != escapedstate):
                    self.token += self.state
                self.token += nextchar
                self.state = escapedstate
            elikiwa self.state in ('a', 'c'):
                ikiwa not nextchar:
                    self.state = None   # end of file
                    break
                elikiwa nextchar in self.whitespace:
                    ikiwa self.debug >= 2:
                        andika("shlex: I see whitespace in word state")
                    self.state = ' '
                    ikiwa self.token or (self.posix and quoted):
                        break   # emit current token
                    else:
                        continue
                elikiwa nextchar in self.commenters:
                    self.instream.readline()
                    self.lineno += 1
                    ikiwa self.posix:
                        self.state = ' '
                        ikiwa self.token or (self.posix and quoted):
                            break   # emit current token
                        else:
                            continue
                elikiwa self.state == 'c':
                    ikiwa nextchar in self.punctuation_chars:
                        self.token += nextchar
                    else:
                        ikiwa nextchar not in self.whitespace:
                            self._pushback_chars.append(nextchar)
                        self.state = ' '
                        break
                elikiwa self.posix and nextchar in self.quotes:
                    self.state = nextchar
                elikiwa self.posix and nextchar in self.escape:
                    escapedstate = 'a'
                    self.state = nextchar
                elikiwa (nextchar in self.wordchars or nextchar in self.quotes
                      or (self.whitespace_split and
                          nextchar not in self.punctuation_chars)):
                    self.token += nextchar
                else:
                    ikiwa self.punctuation_chars:
                        self._pushback_chars.append(nextchar)
                    else:
                        self.pushback.appendleft(nextchar)
                    ikiwa self.debug >= 2:
                        andika("shlex: I see punctuation in word state")
                    self.state = ' '
                    ikiwa self.token or (self.posix and quoted):
                        break   # emit current token
                    else:
                        continue
        result = self.token
        self.token = ''
        ikiwa self.posix and not quoted and result == '':
            result = None
        ikiwa self.debug > 1:
            ikiwa result:
                andika("shlex: raw token=" + repr(result))
            else:
                andika("shlex: raw token=EOF")
        rudisha result

    eleza sourcehook(self, newfile):
        "Hook called on a filename to be sourced."
        ikiwa newfile[0] == '"':
            newfile = newfile[1:-1]
        # This implements cpp-like semantics for relative-path inclusion.
        ikiwa isinstance(self.infile, str) and not os.path.isabs(newfile):
            newfile = os.path.join(os.path.dirname(self.infile), newfile)
        rudisha (newfile, open(newfile, "r"))

    eleza error_leader(self, infile=None, lineno=None):
        "Emit a C-compiler-like, Emacs-friendly error-message leader."
        ikiwa infile is None:
            infile = self.infile
        ikiwa lineno is None:
            lineno = self.lineno
        rudisha "\"%s\", line %d: " % (infile, lineno)

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        token = self.get_token()
        ikiwa token == self.eof:
            raise StopIteration
        rudisha token

eleza split(s, comments=False, posix=True):
    lex = shlex(s, posix=posix)
    lex.whitespace_split = True
    ikiwa not comments:
        lex.commenters = ''
    rudisha list(lex)


eleza join(split_command):
    """Return a shell-escaped string kutoka *split_command*."""
    rudisha ' '.join(quote(arg) for arg in split_command)


_find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search

eleza quote(s):
    """Return a shell-escaped version of the string *s*."""
    ikiwa not s:
        rudisha "''"
    ikiwa _find_unsafe(s) is None:
        rudisha s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    rudisha "'" + s.replace("'", "'\"'\"'") + "'"


eleza _print_tokens(lexer):
    while 1:
        tt = lexer.get_token()
        ikiwa not tt:
            break
        andika("Token: " + repr(tt))

ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) == 1:
        _print_tokens(shlex())
    else:
        fn = sys.argv[1]
        with open(fn) as f:
            _print_tokens(shlex(f, fn))
