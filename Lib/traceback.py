"""Extract, format and print information about Python stack traces."""

agiza collections
agiza itertools
agiza linecache
agiza sys

__all__ = ['extract_stack', 'extract_tb', 'format_exception',
           'format_exception_only', 'format_list', 'format_stack',
           'format_tb', 'print_exc', 'format_exc', 'print_exception',
           'print_last', 'print_stack', 'print_tb', 'clear_frames',
           'FrameSummary', 'StackSummary', 'TracebackException',
           'walk_stack', 'walk_tb']

#
# Formatting and printing lists of traceback lines.
#

eleza print_list(extracted_list, file=None):
    """Print the list of tuples as returned by extract_tb() or
    extract_stack() as a formatted stack trace to the given file."""
    ikiwa file is None:
        file = sys.stderr
    for item in StackSummary.kutoka_list(extracted_list).format():
        andika(item, file=file, end="")

eleza format_list(extracted_list):
    """Format a list of tuples or FrameSummary objects for printing.

    Given a list of tuples or FrameSummary objects as returned by
    extract_tb() or extract_stack(), rudisha a list of strings ready
    for printing.

    Each string in the resulting list corresponds to the item with the
    same index in the argument list.  Each string ends in a newline;
    the strings may contain internal newlines as well, for those items
    whose source text line is not None.
    """
    rudisha StackSummary.kutoka_list(extracted_list).format()

#
# Printing and Extracting Tracebacks.
#

eleza print_tb(tb, limit=None, file=None):
    """Print up to 'limit' stack trace entries kutoka the traceback 'tb'.

    If 'limit' is omitted or None, all entries are printed.  If 'file'
    is omitted or None, the output goes to sys.stderr; otherwise
    'file' should be an open file or file-like object with a write()
    method.
    """
    print_list(extract_tb(tb, limit=limit), file=file)

eleza format_tb(tb, limit=None):
    """A shorthand for 'format_list(extract_tb(tb, limit))'."""
    rudisha extract_tb(tb, limit=limit).format()

eleza extract_tb(tb, limit=None):
    """
    Return a StackSummary object representing a list of
    pre-processed entries kutoka traceback.

    This is useful for alternate formatting of stack traces.  If
    'limit' is omitted or None, all entries are extracted.  A
    pre-processed stack trace entry is a FrameSummary object
    containing attributes filename, lineno, name, and line
    representing the information that is usually printed for a stack
    trace.  The line is a string with leading and trailing
    whitespace stripped; ikiwa the source is not available it is None.
    """
    rudisha StackSummary.extract(walk_tb(tb), limit=limit)

#
# Exception formatting and output.
#

_cause_message = (
    "\nThe above exception was the direct cause "
    "of the following exception:\n\n")

_context_message = (
    "\nDuring handling of the above exception, "
    "another exception occurred:\n\n")


eleza print_exception(etype, value, tb, limit=None, file=None, chain=True):
    """Print exception up to 'limit' stack trace entries kutoka 'tb' to 'file'.

    This differs kutoka print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) ikiwa type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """
    # format_exception has ignored etype for some time, and code such as cgitb
    # passes in bogus values as a result. For compatibility with such code we
    # ignore it here (rather than in the new TracebackException API).
    ikiwa file is None:
        file = sys.stderr
    for line in TracebackException(
            type(value), value, tb, limit=limit).format(chain=chain):
        andika(line, file=file, end="")


eleza format_exception(etype, value, tb, limit=None, chain=True):
    """Format a stack trace and the exception information.

    The arguments have the same meaning as the corresponding arguments
    to print_exception().  The rudisha value is a list of strings, each
    ending in a newline and some containing internal newlines.  When
    these lines are concatenated and printed, exactly the same text is
    printed as does print_exception().
    """
    # format_exception has ignored etype for some time, and code such as cgitb
    # passes in bogus values as a result. For compatibility with such code we
    # ignore it here (rather than in the new TracebackException API).
    rudisha list(TracebackException(
        type(value), value, tb, limit=limit).format(chain=chain))


eleza format_exception_only(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The rudisha value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """
    rudisha list(TracebackException(etype, value, None).format_exception_only())


# -- not official API but folk probably use these two functions.

eleza _format_final_exc_line(etype, value):
    valuestr = _some_str(value)
    ikiwa value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = "%s: %s\n" % (etype, valuestr)
    rudisha line

eleza _some_str(value):
    try:
        rudisha str(value)
    except:
        rudisha '<unprintable %s object>' % type(value).__name__

# --

eleza print_exc(limit=None, file=None, chain=True):
    """Shorthand for 'print_exception(*sys.exc_info(), limit, file)'."""
    print_exception(*sys.exc_info(), limit=limit, file=file, chain=chain)

eleza format_exc(limit=None, chain=True):
    """Like print_exc() but rudisha a string."""
    rudisha "".join(format_exception(*sys.exc_info(), limit=limit, chain=chain))

eleza print_last(limit=None, file=None, chain=True):
    """This is a shorthand for 'print_exception(sys.last_type,
    sys.last_value, sys.last_traceback, limit, file)'."""
    ikiwa not hasattr(sys, "last_type"):
        raise ValueError("no last exception")
    print_exception(sys.last_type, sys.last_value, sys.last_traceback,
                    limit, file, chain)

#
# Printing and Extracting Stacks.
#

eleza print_stack(f=None, limit=None, file=None):
    """Print a stack trace kutoka its invocation point.

    The optional 'f' argument can be used to specify an alternate
    stack frame at which to start. The optional 'limit' and 'file'
    arguments have the same meaning as for print_exception().
    """
    ikiwa f is None:
        f = sys._getframe().f_back
    print_list(extract_stack(f, limit=limit), file=file)


eleza format_stack(f=None, limit=None):
    """Shorthand for 'format_list(extract_stack(f, limit))'."""
    ikiwa f is None:
        f = sys._getframe().f_back
    rudisha format_list(extract_stack(f, limit=limit))


eleza extract_stack(f=None, limit=None):
    """Extract the raw traceback kutoka the current stack frame.

    The rudisha value has the same format as for extract_tb().  The
    optional 'f' and 'limit' arguments have the same meaning as for
    print_stack().  Each item in the list is a quadruple (filename,
    line number, function name, text), and the entries are in order
    kutoka oldest to newest stack frame.
    """
    ikiwa f is None:
        f = sys._getframe().f_back
    stack = StackSummary.extract(walk_stack(f), limit=limit)
    stack.reverse()
    rudisha stack


eleza clear_frames(tb):
    "Clear all references to local variables in the frames of a traceback."
    while tb is not None:
        try:
            tb.tb_frame.clear()
        except RuntimeError:
            # Ignore the exception raised ikiwa the frame is still executing.
            pass
        tb = tb.tb_next


kundi FrameSummary:
    """A single frame kutoka a traceback.

    - :attr:`filename` The filename for the frame.
    - :attr:`lineno` The line within filename for the frame that was
      active when the frame was captured.
    - :attr:`name` The name of the function or method that was executing
      when the frame was captured.
    - :attr:`line` The text kutoka the linecache module for the
      of code that was running when the frame was captured.
    - :attr:`locals` Either None ikiwa locals were not supplied, or a dict
      mapping the name to the repr() of the variable.
    """

    __slots__ = ('filename', 'lineno', 'name', '_line', 'locals')

    eleza __init__(self, filename, lineno, name, *, lookup_line=True,
            locals=None, line=None):
        """Construct a FrameSummary.

        :param lookup_line: If True, `linecache` is consulted for the source
            code line. Otherwise, the line will be looked up when first needed.
        :param locals: If supplied the frame locals, which will be captured as
            object representations.
        :param line: If provided, use this instead of looking up the line in
            the linecache.
        """
        self.filename = filename
        self.lineno = lineno
        self.name = name
        self._line = line
        ikiwa lookup_line:
            self.line
        self.locals = {k: repr(v) for k, v in locals.items()} ikiwa locals else None

    eleza __eq__(self, other):
        ikiwa isinstance(other, FrameSummary):
            rudisha (self.filename == other.filename and
                    self.lineno == other.lineno and
                    self.name == other.name and
                    self.locals == other.locals)
        ikiwa isinstance(other, tuple):
            rudisha (self.filename, self.lineno, self.name, self.line) == other
        rudisha NotImplemented

    eleza __getitem__(self, pos):
        rudisha (self.filename, self.lineno, self.name, self.line)[pos]

    eleza __iter__(self):
        rudisha iter([self.filename, self.lineno, self.name, self.line])

    eleza __repr__(self):
        rudisha "<FrameSummary file {filename}, line {lineno} in {name}>".format(
            filename=self.filename, lineno=self.lineno, name=self.name)

    eleza __len__(self):
        rudisha 4

    @property
    eleza line(self):
        ikiwa self._line is None:
            self._line = linecache.getline(self.filename, self.lineno).strip()
        rudisha self._line


eleza walk_stack(f):
    """Walk a stack yielding the frame and line number for each frame.

    This will follow f.f_back kutoka the given frame. If no frame is given, the
    current stack is used. Usually used with StackSummary.extract.
    """
    ikiwa f is None:
        f = sys._getframe().f_back.f_back
    while f is not None:
        yield f, f.f_lineno
        f = f.f_back


eleza walk_tb(tb):
    """Walk a traceback yielding the frame and line number for each frame.

    This will follow tb.tb_next (and thus is in the opposite order to
    walk_stack). Usually used with StackSummary.extract.
    """
    while tb is not None:
        yield tb.tb_frame, tb.tb_lineno
        tb = tb.tb_next


_RECURSIVE_CUTOFF = 3 # Also hardcoded in traceback.c.

kundi StackSummary(list):
    """A stack of frames."""

    @classmethod
    eleza extract(klass, frame_gen, *, limit=None, lookup_lines=True,
            capture_locals=False):
        """Create a StackSummary kutoka a traceback or stack object.

        :param frame_gen: A generator that yields (frame, lineno) tuples to
            include in the stack.
        :param limit: None to include all frames or the number of frames to
            include.
        :param lookup_lines: If True, lookup lines for each frame immediately,
            otherwise lookup is deferred until the frame is rendered.
        :param capture_locals: If True, the local variables kutoka each frame will
            be captured as object representations into the FrameSummary.
        """
        ikiwa limit is None:
            limit = getattr(sys, 'tracebacklimit', None)
            ikiwa limit is not None and limit < 0:
                limit = 0
        ikiwa limit is not None:
            ikiwa limit >= 0:
                frame_gen = itertools.islice(frame_gen, limit)
            else:
                frame_gen = collections.deque(frame_gen, maxlen=-limit)

        result = klass()
        fnames = set()
        for f, lineno in frame_gen:
            co = f.f_code
            filename = co.co_filename
            name = co.co_name

            fnames.add(filename)
            linecache.lazycache(filename, f.f_globals)
            # Must defer line lookups until we have called checkcache.
            ikiwa capture_locals:
                f_locals = f.f_locals
            else:
                f_locals = None
            result.append(FrameSummary(
                filename, lineno, name, lookup_line=False, locals=f_locals))
        for filename in fnames:
            linecache.checkcache(filename)
        # If immediate lookup was desired, trigger lookups now.
        ikiwa lookup_lines:
            for f in result:
                f.line
        rudisha result

    @classmethod
    eleza kutoka_list(klass, a_list):
        """
        Create a StackSummary object kutoka a supplied list of
        FrameSummary objects or old-style list of tuples.
        """
        # While doing a fast-path check for isinstance(a_list, StackSummary) is
        # appealing, idlelib.run.cleanup_traceback and other similar code may
        # break this by making arbitrary frames plain tuples, so we need to
        # check on a frame by frame basis.
        result = StackSummary()
        for frame in a_list:
            ikiwa isinstance(frame, FrameSummary):
                result.append(frame)
            else:
                filename, lineno, name, line = frame
                result.append(FrameSummary(filename, lineno, name, line=line))
        rudisha result

    eleza format(self):
        """Format the stack ready for printing.

        Returns a list of strings ready for printing.  Each string in the
        resulting list corresponds to a single frame kutoka the stack.
        Each string ends in a newline; the strings may contain internal
        newlines as well, for those items with source text lines.

        For long sequences of the same frame and line, the first few
        repetitions are shown, followed by a summary line stating the exact
        number of further repetitions.
        """
        result = []
        last_file = None
        last_line = None
        last_name = None
        count = 0
        for frame in self:
            ikiwa (last_file is None or last_file != frame.filename or
                last_line is None or last_line != frame.lineno or
                last_name is None or last_name != frame.name):
                ikiwa count > _RECURSIVE_CUTOFF:
                    count -= _RECURSIVE_CUTOFF
                    result.append(
                        f'  [Previous line repeated {count} more '
                        f'time{"s" ikiwa count > 1 else ""}]\n'
                    )
                last_file = frame.filename
                last_line = frame.lineno
                last_name = frame.name
                count = 0
            count += 1
            ikiwa count > _RECURSIVE_CUTOFF:
                continue
            row = []
            row.append('  File "{}", line {}, in {}\n'.format(
                frame.filename, frame.lineno, frame.name))
            ikiwa frame.line:
                row.append('    {}\n'.format(frame.line.strip()))
            ikiwa frame.locals:
                for name, value in sorted(frame.locals.items()):
                    row.append('    {name} = {value}\n'.format(name=name, value=value))
            result.append(''.join(row))
        ikiwa count > _RECURSIVE_CUTOFF:
            count -= _RECURSIVE_CUTOFF
            result.append(
                f'  [Previous line repeated {count} more '
                f'time{"s" ikiwa count > 1 else ""}]\n'
            )
        rudisha result


kundi TracebackException:
    """An exception ready for rendering.

    The traceback module captures enough attributes kutoka the original exception
    to this intermediary form to ensure that no references are held, while
    still being able to fully print or format it.

    Use `kutoka_exception` to create TracebackException instances kutoka exception
    objects, or the constructor to create TracebackException instances kutoka
    individual components.

    - :attr:`__cause__` A TracebackException of the original *__cause__*.
    - :attr:`__context__` A TracebackException of the original *__context__*.
    - :attr:`__suppress_context__` The *__suppress_context__* value kutoka the
      original exception.
    - :attr:`stack` A `StackSummary` representing the traceback.
    - :attr:`exc_type` The kundi of the original traceback.
    - :attr:`filename` For syntax errors - the filename where the error
      occurred.
    - :attr:`lineno` For syntax errors - the linenumber where the error
      occurred.
    - :attr:`text` For syntax errors - the text where the error
      occurred.
    - :attr:`offset` For syntax errors - the offset into the text where the
      error occurred.
    - :attr:`msg` For syntax errors - the compiler error message.
    """

    eleza __init__(self, exc_type, exc_value, exc_traceback, *, limit=None,
            lookup_lines=True, capture_locals=False, _seen=None):
        # NB: we need to accept exc_traceback, exc_value, exc_traceback to
        # permit backwards compat with the existing API, otherwise we
        # need stub thunk objects just to glue it together.
        # Handle loops in __cause__ or __context__.
        ikiwa _seen is None:
            _seen = set()
        _seen.add(id(exc_value))
        # Gracefully handle (the way Python 2.4 and earlier did) the case of
        # being called with no type or value (None, None, None).
        ikiwa (exc_value and exc_value.__cause__ is not None
            and id(exc_value.__cause__) not in _seen):
            cause = TracebackException(
                type(exc_value.__cause__),
                exc_value.__cause__,
                exc_value.__cause__.__traceback__,
                limit=limit,
                lookup_lines=False,
                capture_locals=capture_locals,
                _seen=_seen)
        else:
            cause = None
        ikiwa (exc_value and exc_value.__context__ is not None
            and id(exc_value.__context__) not in _seen):
            context = TracebackException(
                type(exc_value.__context__),
                exc_value.__context__,
                exc_value.__context__.__traceback__,
                limit=limit,
                lookup_lines=False,
                capture_locals=capture_locals,
                _seen=_seen)
        else:
            context = None
        self.exc_traceback = exc_traceback
        self.__cause__ = cause
        self.__context__ = context
        self.__suppress_context__ = \
            exc_value.__suppress_context__ ikiwa exc_value else False
        # TODO: locals.
        self.stack = StackSummary.extract(
            walk_tb(exc_traceback), limit=limit, lookup_lines=lookup_lines,
            capture_locals=capture_locals)
        self.exc_type = exc_type
        # Capture now to permit freeing resources: only complication is in the
        # unofficial API _format_final_exc_line
        self._str = _some_str(exc_value)
        ikiwa exc_type and issubclass(exc_type, SyntaxError):
            # Handle SyntaxError's specially
            self.filename = exc_value.filename
            self.lineno = str(exc_value.lineno)
            self.text = exc_value.text
            self.offset = exc_value.offset
            self.msg = exc_value.msg
        ikiwa lookup_lines:
            self._load_lines()

    @classmethod
    eleza kutoka_exception(cls, exc, *args, **kwargs):
        """Create a TracebackException kutoka an exception."""
        rudisha cls(type(exc), exc, exc.__traceback__, *args, **kwargs)

    eleza _load_lines(self):
        """Private API. force all lines in the stack to be loaded."""
        for frame in self.stack:
            frame.line
        ikiwa self.__context__:
            self.__context__._load_lines()
        ikiwa self.__cause__:
            self.__cause__._load_lines()

    eleza __eq__(self, other):
        rudisha self.__dict__ == other.__dict__

    eleza __str__(self):
        rudisha self._str

    eleza format_exception_only(self):
        """Format the exception part of the traceback.

        The rudisha value is a generator of strings, each ending in a newline.

        Normally, the generator emits a single string; however, for
        SyntaxError exceptions, it emites several lines that (when
        printed) display detailed information about where the syntax
        error occurred.

        The message indicating which exception occurred is always the last
        string in the output.
        """
        ikiwa self.exc_type is None:
            yield _format_final_exc_line(None, self._str)
            return

        stype = self.exc_type.__qualname__
        smod = self.exc_type.__module__
        ikiwa smod not in ("__main__", "builtins"):
            stype = smod + '.' + stype

        ikiwa not issubclass(self.exc_type, SyntaxError):
            yield _format_final_exc_line(stype, self._str)
            return

        # It was a syntax error; show exactly where the problem was found.
        filename = self.filename or "<string>"
        lineno = str(self.lineno) or '?'
        yield '  File "{}", line {}\n'.format(filename, lineno)

        badline = self.text
        offset = self.offset
        ikiwa badline is not None:
            yield '    {}\n'.format(badline.strip())
            ikiwa offset is not None:
                caretspace = badline.rstrip('\n')
                offset = min(len(caretspace), offset) - 1
                caretspace = caretspace[:offset].lstrip()
                # non-space whitespace (likes tabs) must be kept for alignment
                caretspace = ((c.isspace() and c or ' ') for c in caretspace)
                yield '    {}^\n'.format(''.join(caretspace))
        msg = self.msg or "<no detail available>"
        yield "{}: {}\n".format(stype, msg)

    eleza format(self, *, chain=True):
        """Format the exception.

        If chain is not *True*, *__cause__* and *__context__* will not be formatted.

        The rudisha value is a generator of strings, each ending in a newline and
        some containing internal newlines. `print_exception` is a wrapper around
        this method which just prints the lines to a file.

        The message indicating which exception occurred is always the last
        string in the output.
        """
        ikiwa chain:
            ikiwa self.__cause__ is not None:
                yield kutoka self.__cause__.format(chain=chain)
                yield _cause_message
            elikiwa (self.__context__ is not None and
                not self.__suppress_context__):
                yield kutoka self.__context__.format(chain=chain)
                yield _context_message
        ikiwa self.exc_traceback is not None:
            yield 'Traceback (most recent call last):\n'
        yield kutoka self.stack.format()
        yield kutoka self.format_exception_only()
