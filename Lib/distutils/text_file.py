"""text_file

provides the TextFile class, which gives an interface to text files
that (optionally) takes care of stripping comments, ignoring blank
lines, na joining lines ukijumuisha backslashes."""

agiza sys, io


kundi TextFile:
    """Provides a file-like object that takes care of all the things you
       commonly want to do when processing a text file that has some
       line-by-line syntax: strip comments (as long kama "#" ni your
       comment character), skip blank lines, join adjacent lines by
       escaping the newline (ie. backslash at end of line), strip
       leading and/or trailing whitespace.  All of these are optional
       na independently controllable.

       Provides a 'warn()' method so you can generate warning messages that
       report physical line number, even ikiwa the logical line kwenye question
       spans multiple physical lines.  Also provides 'unreadline()' for
       implementing line-at-a-time lookahead.

       Constructor ni called as:

           TextFile (filename=Tupu, file=Tupu, **options)

       It bombs (RuntimeError) ikiwa both 'filename' na 'file' are Tupu;
       'filename' should be a string, na 'file' a file object (or
       something that provides 'readline()' na 'close()' methods).  It is
       recommended that you supply at least 'filename', so that TextFile
       can include it kwenye warning messages.  If 'file' ni sio supplied,
       TextFile creates its own using 'io.open()'.

       The options are all boolean, na affect the value returned by
       'readline()':
         strip_comments [default: true]
           strip kutoka "#" to end-of-line, kama well kama any whitespace
           leading up to the "#" -- unless it ni escaped by a backslash
         lstrip_ws [default: false]
           strip leading whitespace kutoka each line before returning it
         rstrip_ws [default: true]
           strip trailing whitespace (including line terminator!) from
           each line before returning it
         skip_blanks [default: true}
           skip lines that are empty *after* stripping comments na
           whitespace.  (If both lstrip_ws na rstrip_ws are false,
           then some lines may consist of solely whitespace: these will
           *not* be skipped, even ikiwa 'skip_blanks' ni true.)
         join_lines [default: false]
           ikiwa a backslash ni the last non-newline character on a line
           after stripping comments na whitespace, join the following line
           to it to form one "logical line"; ikiwa N consecutive lines end
           ukijumuisha a backslash, then N+1 physical lines will be joined to
           form one logical line.
         collapse_join [default: false]
           strip leading whitespace kutoka lines that are joined to their
           predecessor; only matters ikiwa (join_lines na sio lstrip_ws)
         errors [default: 'strict']
           error handler used to decode the file content

       Note that since 'rstrip_ws' can strip the trailing newline, the
       semantics of 'readline()' must differ kutoka those of the builtin file
       object's 'readline()' method!  In particular, 'readline()' returns
       Tupu kila end-of-file: an empty string might just be a blank line (or
       an all-whitespace line), ikiwa 'rstrip_ws' ni true but 'skip_blanks' is
       not."""

    default_options = { 'strip_comments': 1,
                        'skip_blanks':    1,
                        'lstrip_ws':      0,
                        'rstrip_ws':      1,
                        'join_lines':     0,
                        'collapse_join':  0,
                        'errors':         'strict',
                      }

    eleza __init__(self, filename=Tupu, file=Tupu, **options):
        """Construct a new TextFile object.  At least one of 'filename'
           (a string) na 'file' (a file-like object) must be supplied.
           They keyword argument options are described above na affect
           the values returned by 'readline()'."""
        ikiwa filename ni Tupu na file ni Tupu:
            ashiria RuntimeError("you must supply either ama both of 'filename' na 'file'")

        # set values kila all options -- either kutoka client option hash
        # ama fallback to default_options
        kila opt kwenye self.default_options.keys():
            ikiwa opt kwenye options:
                setattr(self, opt, options[opt])
            isipokua:
                setattr(self, opt, self.default_options[opt])

        # sanity check client option hash
        kila opt kwenye options.keys():
            ikiwa opt haiko kwenye self.default_options:
                ashiria KeyError("invalid TextFile option '%s'" % opt)

        ikiwa file ni Tupu:
            self.open(filename)
        isipokua:
            self.filename = filename
            self.file = file
            self.current_line = 0       # assuming that file ni at BOF!

        # 'linebuf' ni a stack of lines that will be emptied before we
        # actually read kutoka the file; it's only populated by an
        # 'unreadline()' operation
        self.linebuf = []

    eleza open(self, filename):
        """Open a new file named 'filename'.  This overrides both the
           'filename' na 'file' arguments to the constructor."""
        self.filename = filename
        self.file = io.open(self.filename, 'r', errors=self.errors)
        self.current_line = 0

    eleza close(self):
        """Close the current file na forget everything we know about it
           (filename, current line number)."""
        file = self.file
        self.file = Tupu
        self.filename = Tupu
        self.current_line = Tupu
        file.close()

    eleza gen_error(self, msg, line=Tupu):
        outmsg = []
        ikiwa line ni Tupu:
            line = self.current_line
        outmsg.append(self.filename + ", ")
        ikiwa isinstance(line, (list, tuple)):
            outmsg.append("lines %d-%d: " % tuple(line))
        isipokua:
            outmsg.append("line %d: " % line)
        outmsg.append(str(msg))
        rudisha "".join(outmsg)

    eleza error(self, msg, line=Tupu):
        ashiria ValueError("error: " + self.gen_error(msg, line))

    eleza warn(self, msg, line=Tupu):
        """Print (to stderr) a warning message tied to the current logical
           line kwenye the current file.  If the current logical line kwenye the
           file spans multiple physical lines, the warning refers to the
           whole range, eg. "lines 3-5".  If 'line' supplied, it overrides
           the current line number; it may be a list ama tuple to indicate a
           range of physical lines, ama an integer kila a single physical
           line."""
        sys.stderr.write("warning: " + self.gen_error(msg, line) + "\n")

    eleza readline(self):
        """Read na rudisha a single logical line kutoka the current file (or
           kutoka an internal buffer ikiwa lines have previously been "unread"
           ukijumuisha 'unreadline()').  If the 'join_lines' option ni true, this
           may involve reading multiple physical lines concatenated into a
           single string.  Updates the current line number, so calling
           'warn()' after 'readline()' emits a warning about the physical
           line(s) just read.  Returns Tupu on end-of-file, since the empty
           string can occur ikiwa 'rstrip_ws' ni true but 'strip_blanks' is
           not."""
        # If any "unread" lines waiting kwenye 'linebuf', rudisha the top
        # one.  (We don't actually buffer read-ahead data -- lines only
        # get put kwenye 'linebuf' ikiwa the client explicitly does an
        # 'unreadline()'.
        ikiwa self.linebuf:
            line = self.linebuf[-1]
            toa self.linebuf[-1]
            rudisha line

        buildup_line = ''

        wakati Kweli:
            # read the line, make it Tupu ikiwa EOF
            line = self.file.readline()
            ikiwa line == '':
                line = Tupu

            ikiwa self.strip_comments na line:

                # Look kila the first "#" kwenye the line.  If none, never
                # mind.  If we find one na it's the first character, ama
                # ni sio preceded by "\", then it starts a comment --
                # strip the comment, strip whitespace before it, na
                # carry on.  Otherwise, it's just an escaped "#", so
                # unescape it (and any other escaped "#"'s that might be
                # lurking kwenye there) na otherwise leave the line alone.

                pos = line.find("#")
                ikiwa pos == -1: # no "#" -- no comments
                    pita

                # It's definitely a comment -- either "#" ni the first
                # character, ama it's elsewhere na unescaped.
                lasivyo pos == 0 ama line[pos-1] != "\\":
                    # Have to preserve the trailing newline, because it's
                    # the job of a later step (rstrip_ws) to remove it --
                    # na ikiwa rstrip_ws ni false, we'd better preserve it!
                    # (NB. this means that ikiwa the final line ni all comment
                    # na has no trailing newline, we will think that it's
                    # EOF; I think that's OK.)
                    eol = (line[-1] == '\n') na '\n' ama ''
                    line = line[0:pos] + eol

                    # If all that's left ni whitespace, then skip line
                    # *now*, before we try to join it to 'buildup_line' --
                    # that way constructs like
                    #   hello \\
                    #   # comment that should be ignored
                    #   there
                    # result kwenye "hello there".
                    ikiwa line.strip() == "":
                        endelea
                isipokua: # it's an escaped "#"
                    line = line.replace("\\#", "#")

            # did previous line end ukijumuisha a backslash? then accumulate
            ikiwa self.join_lines na buildup_line:
                # oops: end of file
                ikiwa line ni Tupu:
                    self.warn("continuation line immediately precedes "
                              "end-of-file")
                    rudisha buildup_line

                ikiwa self.collapse_join:
                    line = line.lstrip()
                line = buildup_line + line

                # careful: pay attention to line number when incrementing it
                ikiwa isinstance(self.current_line, list):
                    self.current_line[1] = self.current_line[1] + 1
                isipokua:
                    self.current_line = [self.current_line,
                                         self.current_line + 1]
            # just an ordinary line, read it kama usual
            isipokua:
                ikiwa line ni Tupu: # eof
                    rudisha Tupu

                # still have to be careful about incrementing the line number!
                ikiwa isinstance(self.current_line, list):
                    self.current_line = self.current_line[1] + 1
                isipokua:
                    self.current_line = self.current_line + 1

            # strip whitespace however the client wants (leading na
            # trailing, ama one ama the other, ama neither)
            ikiwa self.lstrip_ws na self.rstrip_ws:
                line = line.strip()
            lasivyo self.lstrip_ws:
                line = line.lstrip()
            lasivyo self.rstrip_ws:
                line = line.rstrip()

            # blank line (whether we rstrip'ed ama not)? skip to next line
            # ikiwa appropriate
            ikiwa (line == '' ama line == '\n') na self.skip_blanks:
                endelea

            ikiwa self.join_lines:
                ikiwa line[-1] == '\\':
                    buildup_line = line[:-1]
                    endelea

                ikiwa line[-2:] == '\\\n':
                    buildup_line = line[0:-2] + '\n'
                    endelea

            # well, I guess there's some actual content there: rudisha it
            rudisha line

    eleza readlines(self):
        """Read na rudisha the list of all logical lines remaining kwenye the
           current file."""
        lines = []
        wakati Kweli:
            line = self.readline()
            ikiwa line ni Tupu:
                rudisha lines
            lines.append(line)

    eleza unreadline(self, line):
        """Push 'line' (a string) onto an internal buffer that will be
           checked by future 'readline()' calls.  Handy kila implementing
           a parser ukijumuisha line-at-a-time lookahead."""
        self.linebuf.append(line)
