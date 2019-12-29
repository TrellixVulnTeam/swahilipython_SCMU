"""A lexical analyzer kundi kila simple shell-like syntaxes."""

# Module na documentation by Eric S. Raymond, 21 Dec 1998
# Input stacking na error message cleanup added by ESR, March 2000
# push_source() na pop_source() made explicit by ESR, January 2001.
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
    "A lexical analyzer kundi kila simple shell-like syntaxes."
    eleza __init__(self, instream=Tupu, infile=Tupu, posix=Uongo,
                 punctuation_chars=Uongo):
        ikiwa isinstance(instream, str):
            instream = StringIO(instream)
        ikiwa instream ni sio Tupu:
            self.instream = instream
            self.infile = infile
        isipokua:
            self.instream = sys.stdin
            self.infile = Tupu
        self.posix = posix
        ikiwa posix:
            self.eof = Tupu
        isipokua:
            self.eof = ''
        self.commenters = '#'
        self.wordchars = ('abcdfeghijklmnopqrstuvwxyz'
                          'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        ikiwa self.posix:
            self.wordchars += ('ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'
                               'ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ')
        self.whitespace = ' \t\r\n'
        self.whitespace_split = Uongo
        self.quotes = '\'"'
        self.escape = '\\'
        self.escapedquotes = '"'
        self.state = ' '
        self.pushback = deque()
        self.lineno = 1
        self.debug = 0
        self.token = ''
        self.filestack = deque()
        self.source = Tupu
        ikiwa sio punctuation_chars:
            punctuation_chars = ''
        lasivyo punctuation_chars ni Kweli:
            punctuation_chars = '();<>|&'
        self._punctuation_chars = punctuation_chars
        ikiwa punctuation_chars:
            # _pushback_chars ni a push back queue used by lookahead logic
            self._pushback_chars = deque()
            # these chars added because allowed kwenye file names, args, wildcards
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

    eleza push_source(self, newstream, newfile=Tupu):
        "Push an input source onto the lexer's input source stack."
        ikiwa isinstance(newstream, str):
            newstream = StringIO(newstream)
        self.filestack.appendleft((self.infile, self.instream, self.lineno))
        self.infile = newfile
        self.instream = newstream
        self.lineno = 1
        ikiwa self.debug:
            ikiwa newfile ni sio Tupu:
                andika('shlex: pushing to file %s' % (self.infile,))
            isipokua:
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
        ikiwa self.source ni sio Tupu:
            wakati raw == self.source:
                spec = self.sourcehook(self.read_token())
                ikiwa spec:
                    (newfile, newstream) = spec
                    self.push_source(newstream, newfile)
                raw = self.get_token()
        # Maybe we got EOF instead?
        wakati raw == self.eof:
            ikiwa sio self.filestack:
                rudisha self.eof
            isipokua:
                self.pop_source()
                raw = self.get_token()
        # Neither inclusion nor EOF
        ikiwa self.debug >= 1:
            ikiwa raw != self.eof:
                andika("shlex: token=" + repr(raw))
            isipokua:
                andika("shlex: token=EOF")
        rudisha raw

    eleza read_token(self):
        quoted = Uongo
        escapedstate = ' '
        wakati Kweli:
            ikiwa self.punctuation_chars na self._pushback_chars:
                nextchar = self._pushback_chars.pop()
            isipokua:
                nextchar = self.instream.read(1)
            ikiwa nextchar == '\n':
                self.lineno += 1
            ikiwa self.debug >= 3:
                andika("shlex: kwenye state %r I see character: %r" % (self.state,
                                                                  nextchar))
            ikiwa self.state ni Tupu:
                self.token = ''        # past end of file
                koma
            lasivyo self.state == ' ':
                ikiwa sio nextchar:
                    self.state = Tupu  # end of file
                    koma
                lasivyo nextchar kwenye self.whitespace:
                    ikiwa self.debug >= 2:
                        andika("shlex: I see whitespace kwenye whitespace state")
                    ikiwa self.token ama (self.posix na quoted):
                        koma   # emit current token
                    isipokua:
                        endelea
                lasivyo nextchar kwenye self.commenters:
                    self.instream.readline()
                    self.lineno += 1
                lasivyo self.posix na nextchar kwenye self.escape:
                    escapedstate = 'a'
                    self.state = nextchar
                lasivyo nextchar kwenye self.wordchars:
                    self.token = nextchar
                    self.state = 'a'
                lasivyo nextchar kwenye self.punctuation_chars:
                    self.token = nextchar
                    self.state = 'c'
                lasivyo nextchar kwenye self.quotes:
                    ikiwa sio self.posix:
                        self.token = nextchar
                    self.state = nextchar
                lasivyo self.whitespace_split:
                    self.token = nextchar
                    self.state = 'a'
                isipokua:
                    self.token = nextchar
                    ikiwa self.token ama (self.posix na quoted):
                        koma   # emit current token
                    isipokua:
                        endelea
            lasivyo self.state kwenye self.quotes:
                quoted = Kweli
                ikiwa sio nextchar:      # end of file
                    ikiwa self.debug >= 2:
                        andika("shlex: I see EOF kwenye quotes state")
                    # XXX what error should be ashiriad here?
                    ashiria ValueError("No closing quotation")
                ikiwa nextchar == self.state:
                    ikiwa sio self.posix:
                        self.token += nextchar
                        self.state = ' '
                        koma
                    isipokua:
                        self.state = 'a'
                lasivyo (self.posix na nextchar kwenye self.escape na self.state
                      kwenye self.escapedquotes):
                    escapedstate = self.state
                    self.state = nextchar
                isipokua:
                    self.token += nextchar
            lasivyo self.state kwenye self.escape:
                ikiwa sio nextchar:      # end of file
                    ikiwa self.debug >= 2:
                        andika("shlex: I see EOF kwenye escape state")
                    # XXX what error should be ashiriad here?
                    ashiria ValueError("No escaped character")
                # In posix shells, only the quote itself ama the escape
                # character may be escaped within quotes.
                ikiwa (escapedstate kwenye self.quotes and
                        nextchar != self.state na nextchar != escapedstate):
                    self.token += self.state
                self.token += nextchar
                self.state = escapedstate
            lasivyo self.state kwenye ('a', 'c'):
                ikiwa sio nextchar:
                    self.state = Tupu   # end of file
                    koma
                lasivyo nextchar kwenye self.whitespace:
                    ikiwa self.debug >= 2:
                        andika("shlex: I see whitespace kwenye word state")
                    self.state = ' '
                    ikiwa self.token ama (self.posix na quoted):
                        koma   # emit current token
                    isipokua:
                        endelea
                lasivyo nextchar kwenye self.commenters:
                    self.instream.readline()
                    self.lineno += 1
                    ikiwa self.posix:
                        self.state = ' '
                        ikiwa self.token ama (self.posix na quoted):
                            koma   # emit current token
                        isipokua:
                            endelea
                lasivyo self.state == 'c':
                    ikiwa nextchar kwenye self.punctuation_chars:
                        self.token += nextchar
                    isipokua:
                        ikiwa nextchar haiko kwenye self.whitespace:
                            self._pushback_chars.append(nextchar)
                        self.state = ' '
                        koma
                lasivyo self.posix na nextchar kwenye self.quotes:
                    self.state = nextchar
                lasivyo self.posix na nextchar kwenye self.escape:
                    escapedstate = 'a'
                    self.state = nextchar
                lasivyo (nextchar kwenye self.wordchars ama nextchar kwenye self.quotes
                      ama (self.whitespace_split and
                          nextchar haiko kwenye self.punctuation_chars)):
                    self.token += nextchar
                isipokua:
                    ikiwa self.punctuation_chars:
                        self._pushback_chars.append(nextchar)
                    isipokua:
                        self.pushback.appendleft(nextchar)
                    ikiwa self.debug >= 2:
                        andika("shlex: I see punctuation kwenye word state")
                    self.state = ' '
                    ikiwa self.token ama (self.posix na quoted):
                        koma   # emit current token
                    isipokua:
                        endelea
        result = self.token
        self.token = ''
        ikiwa self.posix na sio quoted na result == '':
            result = Tupu
        ikiwa self.debug > 1:
            ikiwa result:
                andika("shlex: raw token=" + repr(result))
            isipokua:
                andika("shlex: raw token=EOF")
        rudisha result

    eleza sourcehook(self, newfile):
        "Hook called on a filename to be sourced."
        ikiwa newfile[0] == '"':
            newfile = newfile[1:-1]
        # This implements cpp-like semantics kila relative-path inclusion.
        ikiwa isinstance(self.infile, str) na sio os.path.isabs(newfile):
            newfile = os.path.join(os.path.dirname(self.infile), newfile)
        rudisha (newfile, open(newfile, "r"))

    eleza error_leader(self, infile=Tupu, lineno=Tupu):
        "Emit a C-compiler-like, Emacs-friendly error-message leader."
        ikiwa infile ni Tupu:
            infile = self.infile
        ikiwa lineno ni Tupu:
            lineno = self.lineno
        rudisha "\"%s\", line %d: " % (infile, lineno)

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        token = self.get_token()
        ikiwa token == self.eof:
            ashiria StopIteration
        rudisha token

eleza split(s, comments=Uongo, posix=Kweli):
    lex = shlex(s, posix=posix)
    lex.whitespace_split = Kweli
    ikiwa sio comments:
        lex.commenters = ''
    rudisha list(lex)


eleza join(split_command):
    """Return a shell-escaped string kutoka *split_command*."""
    rudisha ' '.join(quote(arg) kila arg kwenye split_command)


_find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search

eleza quote(s):
    """Return a shell-escaped version of the string *s*."""
    ikiwa sio s:
        rudisha "''"
    ikiwa _find_unsafe(s) ni Tupu:
        rudisha s

    # use single quotes, na put single quotes into double quotes
    # the string $'b ni then quoted kama '$'"'"'b'
    rudisha "'" + s.replace("'", "'\"'\"'") + "'"


eleza _print_tokens(lexer):
    wakati 1:
        tt = lexer.get_token()
        ikiwa sio tt:
            koma
        andika("Token: " + repr(tt))

ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) == 1:
        _print_tokens(shlex())
    isipokua:
        fn = sys.argv[1]
        ukijumuisha open(fn) kama f:
            _print_tokens(shlex(f, fn))
