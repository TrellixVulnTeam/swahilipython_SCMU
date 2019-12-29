"""Extract, format na print information about Python stack traces."""

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
# Formatting na printing lists of traceback lines.
#

eleza print_list(extracted_list, file=Tupu):
    """Print the list of tuples kama rudishaed by extract_tb() or
    extract_stack() kama a formatted stack trace to the given file."""
    ikiwa file ni Tupu:
        file = sys.stderr
    kila item kwenye StackSummary.kutoka_list(extracted_list).format():
        andika(item, file=file, end="")

eleza format_list(extracted_list):
    """Format a list of tuples ama FrameSummary objects kila printing.

    Given a list of tuples ama FrameSummary objects kama rudishaed by
    extract_tb() ama extract_stack(), rudisha a list of strings ready
    kila printing.

    Each string kwenye the resulting list corresponds to the item with the
    same index kwenye the argument list.  Each string ends kwenye a newline;
    the strings may contain internal newlines kama well, kila those items
    whose source text line ni sio Tupu.
    """
    rudisha StackSummary.kutoka_list(extracted_list).format()

#
# Printing na Extracting Tracebacks.
#

eleza print_tb(tb, limit=Tupu, file=Tupu):
    """Print up to 'limit' stack trace entries kutoka the traceback 'tb'.

    If 'limit' ni omitted ama Tupu, all entries are printed.  If 'file'
    ni omitted ama Tupu, the output goes to sys.stderr; otherwise
    'file' should be an open file ama file-like object with a write()
    method.
    """
    print_list(extract_tb(tb, limit=limit), file=file)

eleza format_tb(tb, limit=Tupu):
    """A shorthand kila 'format_list(extract_tb(tb, limit))'."""
    rudisha extract_tb(tb, limit=limit).format()

eleza extract_tb(tb, limit=Tupu):
    """
    Return a StackSummary object representing a list of
    pre-processed entries kutoka traceback.

    This ni useful kila alternate formatting of stack traces.  If
    'limit' ni omitted ama Tupu, all entries are extracted.  A
    pre-processed stack trace entry ni a FrameSummary object
    containing attributes filename, lineno, name, na line
    representing the information that ni usually printed kila a stack
    trace.  The line ni a string with leading na trailing
    whitespace stripped; ikiwa the source ni sio available it ni Tupu.
    """
    rudisha StackSummary.extract(walk_tb(tb), limit=limit)

#
# Exception formatting na output.
#

_cause_message = (
    "\nThe above exception was the direct cause "
    "of the following exception:\n\n")

_context_message = (
    "\nDuring handling of the above exception, "
    "another exception occurred:\n\n")


eleza print_exception(etype, value, tb, limit=Tupu, file=Tupu, chain=Kweli):
    """Print exception up to 'limit' stack trace entries kutoka 'tb' to 'file'.

    This differs kutoka print_tb() kwenye the following ways: (1) if
    traceback ni sio Tupu, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type na value after the
    stack trace; (3) ikiwa type ni SyntaxError na value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """
    # format_exception has ignored etype kila some time, na code such kama cgitb
    # pitaes kwenye bogus values kama a result. For compatibility with such code we
    # ignore it here (rather than kwenye the new TracebackException API).
    ikiwa file ni Tupu:
        file = sys.stderr
    kila line kwenye TracebackException(
            type(value), value, tb, limit=limit).format(chain=chain):
        andika(line, file=file, end="")


eleza format_exception(etype, value, tb, limit=Tupu, chain=Kweli):
    """Format a stack trace na the exception information.

    The arguments have the same meaning kama the corresponding arguments
    to print_exception().  The rudisha value ni a list of strings, each
    ending kwenye a newline na some containing internal newlines.  When
    these lines are concatenated na printed, exactly the same text is
    printed kama does print_exception().
    """
    # format_exception has ignored etype kila some time, na code such kama cgitb
    # pitaes kwenye bogus values kama a result. For compatibility with such code we
    # ignore it here (rather than kwenye the new TracebackException API).
    rudisha list(TracebackException(
        type(value), value, tb, limit=limit).format(chain=chain))


eleza format_exception_only(etype, value):
    """Format the exception part of a traceback.

    The arguments are the exception type na value such kama given by
    sys.last_type na sys.last_value. The rudisha value ni a list of
    strings, each ending kwenye a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred ni always the last
    string kwenye the list.

    """
    rudisha list(TracebackException(etype, value, Tupu).format_exception_only())


# -- sio official API but folk probably use these two functions.

eleza _format_final_exc_line(etype, value):
    valuestr = _some_str(value)
    ikiwa value ni Tupu ama sio valuestr:
        line = "%s\n" % etype
    isipokua:
        line = "%s: %s\n" % (etype, valuestr)
    rudisha line

eleza _some_str(value):
    jaribu:
        rudisha str(value)
    except:
        rudisha '<unprintable %s object>' % type(value).__name__

# --

eleza print_exc(limit=Tupu, file=Tupu, chain=Kweli):
    """Shorthand kila 'print_exception(*sys.exc_info(), limit, file)'."""
    print_exception(*sys.exc_info(), limit=limit, file=file, chain=chain)

eleza format_exc(limit=Tupu, chain=Kweli):
    """Like print_exc() but rudisha a string."""
    rudisha "".join(format_exception(*sys.exc_info(), limit=limit, chain=chain))

eleza print_last(limit=Tupu, file=Tupu, chain=Kweli):
    """This ni a shorthand kila 'print_exception(sys.last_type,
    sys.last_value, sys.last_traceback, limit, file)'."""
    ikiwa sio hasattr(sys, "last_type"):
        ashiria ValueError("no last exception")
    print_exception(sys.last_type, sys.last_value, sys.last_traceback,
                    limit, file, chain)

#
# Printing na Extracting Stacks.
#

eleza print_stack(f=Tupu, limit=Tupu, file=Tupu):
    """Print a stack trace kutoka its invocation point.

    The optional 'f' argument can be used to specify an alternate
    stack frame at which to start. The optional 'limit' na 'file'
    arguments have the same meaning kama kila print_exception().
    """
    ikiwa f ni Tupu:
        f = sys._getframe().f_back
    print_list(extract_stack(f, limit=limit), file=file)


eleza format_stack(f=Tupu, limit=Tupu):
    """Shorthand kila 'format_list(extract_stack(f, limit))'."""
    ikiwa f ni Tupu:
        f = sys._getframe().f_back
    rudisha format_list(extract_stack(f, limit=limit))


eleza extract_stack(f=Tupu, limit=Tupu):
    """Extract the raw traceback kutoka the current stack frame.

    The rudisha value has the same format kama kila extract_tb().  The
    optional 'f' na 'limit' arguments have the same meaning kama for
    print_stack().  Each item kwenye the list ni a quadruple (filename,
    line number, function name, text), na the entries are kwenye order
    kutoka oldest to newest stack frame.
    """
    ikiwa f ni Tupu:
        f = sys._getframe().f_back
    stack = StackSummary.extract(walk_stack(f), limit=limit)
    stack.reverse()
    rudisha stack


eleza clear_frames(tb):
    "Clear all references to local variables kwenye the frames of a traceback."
    wakati tb ni sio Tupu:
        jaribu:
            tb.tb_frame.clear()
        tatizo RuntimeError:
            # Ignore the exception ashiriad ikiwa the frame ni still executing.
            pita
        tb = tb.tb_next


kundi FrameSummary:
    """A single frame kutoka a traceback.

    - :attr:`filename` The filename kila the frame.
    - :attr:`lineno` The line within filename kila the frame that was
      active when the frame was captured.
    - :attr:`name` The name of the function ama method that was executing
      when the frame was captured.
    - :attr:`line` The text kutoka the linecache module kila the
      of code that was running when the frame was captured.
    - :attr:`locals` Either Tupu ikiwa locals were sio supplied, ama a dict
      mapping the name to the repr() of the variable.
    """

    __slots__ = ('filename', 'lineno', 'name', '_line', 'locals')

    eleza __init__(self, filename, lineno, name, *, lookup_line=Kweli,
            locals=Tupu, line=Tupu):
        """Construct a FrameSummary.

        :param lookup_line: If Kweli, `linecache` ni consulted kila the source
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
        self.locals = {k: repr(v) kila k, v kwenye locals.items()} ikiwa locals else Tupu

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
        rudisha "<FrameSummary file {filename}, line {lineno} kwenye {name}>".format(
            filename=self.filename, lineno=self.lineno, name=self.name)

    eleza __len__(self):
        rudisha 4

    @property
    eleza line(self):
        ikiwa self._line ni Tupu:
            self._line = linecache.getline(self.filename, self.lineno).strip()
        rudisha self._line


eleza walk_stack(f):
    """Walk a stack tumaing the frame na line number kila each frame.

    This will follow f.f_back kutoka the given frame. If no frame ni given, the
    current stack ni used. Usually used with StackSummary.extract.
    """
    ikiwa f ni Tupu:
        f = sys._getframe().f_back.f_back
    wakati f ni sio Tupu:
        tuma f, f.f_lineno
        f = f.f_back


eleza walk_tb(tb):
    """Walk a traceback tumaing the frame na line number kila each frame.

    This will follow tb.tb_next (and thus ni kwenye the opposite order to
    walk_stack). Usually used with StackSummary.extract.
    """
    wakati tb ni sio Tupu:
        tuma tb.tb_frame, tb.tb_lineno
        tb = tb.tb_next


_RECURSIVE_CUTOFF = 3 # Also hardcoded kwenye traceback.c.

kundi StackSummary(list):
    """A stack of frames."""

    @classmethod
    eleza extract(klass, frame_gen, *, limit=Tupu, lookup_lines=Kweli,
            capture_locals=Uongo):
        """Create a StackSummary kutoka a traceback ama stack object.

        :param frame_gen: A generator that tumas (frame, lineno) tuples to
            include kwenye the stack.
        :param limit: Tupu to include all frames ama the number of frames to
            include.
        :param lookup_lines: If Kweli, lookup lines kila each frame immediately,
            otherwise lookup ni deferred until the frame ni rendered.
        :param capture_locals: If Kweli, the local variables kutoka each frame will
            be captured kama object representations into the FrameSummary.
        """
        ikiwa limit ni Tupu:
            limit = getattr(sys, 'tracebacklimit', Tupu)
            ikiwa limit ni sio Tupu na limit < 0:
                limit = 0
        ikiwa limit ni sio Tupu:
            ikiwa limit >= 0:
                frame_gen = itertools.islice(frame_gen, limit)
            isipokua:
                frame_gen = collections.deque(frame_gen, maxlen=-limit)

        result = klass()
        fnames = set()
        kila f, lineno kwenye frame_gen:
            co = f.f_code
            filename = co.co_filename
            name = co.co_name

            fnames.add(filename)
            linecache.lazycache(filename, f.f_globals)
            # Must defer line lookups until we have called checkcache.
            ikiwa capture_locals:
                f_locals = f.f_locals
            isipokua:
                f_locals = Tupu
            result.append(FrameSummary(
                filename, lineno, name, lookup_line=Uongo, locals=f_locals))
        kila filename kwenye fnames:
            linecache.checkcache(filename)
        # If immediate lookup was desired, trigger lookups now.
        ikiwa lookup_lines:
            kila f kwenye result:
                f.line
        rudisha result

    @classmethod
    eleza kutoka_list(klass, a_list):
        """
        Create a StackSummary object kutoka a supplied list of
        FrameSummary objects ama old-style list of tuples.
        """
        # While doing a fast-path check kila isinstance(a_list, StackSummary) is
        # appealing, idlelib.run.cleanup_traceback na other similar code may
        # koma this by making arbitrary frames plain tuples, so we need to
        # check on a frame by frame basis.
        result = StackSummary()
        kila frame kwenye a_list:
            ikiwa isinstance(frame, FrameSummary):
                result.append(frame)
            isipokua:
                filename, lineno, name, line = frame
                result.append(FrameSummary(filename, lineno, name, line=line))
        rudisha result

    eleza format(self):
        """Format the stack ready kila printing.

        Returns a list of strings ready kila printing.  Each string kwenye the
        resulting list corresponds to a single frame kutoka the stack.
        Each string ends kwenye a newline; the strings may contain internal
        newlines kama well, kila those items with source text lines.

        For long sequences of the same frame na line, the first few
        repetitions are shown, followed by a summary line stating the exact
        number of further repetitions.
        """
        result = []
        last_file = Tupu
        last_line = Tupu
        last_name = Tupu
        count = 0
        kila frame kwenye self:
            ikiwa (last_file ni Tupu ama last_file != frame.filename or
                last_line ni Tupu ama last_line != frame.lineno or
                last_name ni Tupu ama last_name != frame.name):
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
                endelea
            row = []
            row.append('  File "{}", line {}, kwenye {}\n'.format(
                frame.filename, frame.lineno, frame.name))
            ikiwa frame.line:
                row.append('    {}\n'.format(frame.line.strip()))
            ikiwa frame.locals:
                kila name, value kwenye sorted(frame.locals.items()):
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
    """An exception ready kila rendering.

    The traceback module captures enough attributes kutoka the original exception
    to this intermediary form to ensure that no references are held, while
    still being able to fully print ama format it.

    Use `kutoka_exception` to create TracebackException instances kutoka exception
    objects, ama the constructor to create TracebackException instances kutoka
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

    eleza __init__(self, exc_type, exc_value, exc_traceback, *, limit=Tupu,
            lookup_lines=Kweli, capture_locals=Uongo, _seen=Tupu):
        # NB: we need to accept exc_traceback, exc_value, exc_traceback to
        # permit backwards compat with the existing API, otherwise we
        # need stub thunk objects just to glue it together.
        # Handle loops kwenye __cause__ ama __context__.
        ikiwa _seen ni Tupu:
            _seen = set()
        _seen.add(id(exc_value))
        # Gracefully handle (the way Python 2.4 na earlier did) the case of
        # being called with no type ama value (Tupu, Tupu, Tupu).
        ikiwa (exc_value na exc_value.__cause__ ni sio Tupu
            na id(exc_value.__cause__) haiko kwenye _seen):
            cause = TracebackException(
                type(exc_value.__cause__),
                exc_value.__cause__,
                exc_value.__cause__.__traceback__,
                limit=limit,
                lookup_lines=Uongo,
                capture_locals=capture_locals,
                _seen=_seen)
        isipokua:
            cause = Tupu
        ikiwa (exc_value na exc_value.__context__ ni sio Tupu
            na id(exc_value.__context__) haiko kwenye _seen):
            context = TracebackException(
                type(exc_value.__context__),
                exc_value.__context__,
                exc_value.__context__.__traceback__,
                limit=limit,
                lookup_lines=Uongo,
                capture_locals=capture_locals,
                _seen=_seen)
        isipokua:
            context = Tupu
        self.exc_traceback = exc_traceback
        self.__cause__ = cause
        self.__context__ = context
        self.__suppress_context__ = \
            exc_value.__suppress_context__ ikiwa exc_value else Uongo
        # TODO: locals.
        self.stack = StackSummary.extract(
            walk_tb(exc_traceback), limit=limit, lookup_lines=lookup_lines,
            capture_locals=capture_locals)
        self.exc_type = exc_type
        # Capture now to permit freeing resources: only complication ni kwenye the
        # unofficial API _format_final_exc_line
        self._str = _some_str(exc_value)
        ikiwa exc_type na issubclass(exc_type, SyntaxError):
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
        """Private API. force all lines kwenye the stack to be loaded."""
        kila frame kwenye self.stack:
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

        The rudisha value ni a generator of strings, each ending kwenye a newline.

        Normally, the generator emits a single string; however, for
        SyntaxError exceptions, it emites several lines that (when
        printed) display detailed information about where the syntax
        error occurred.

        The message indicating which exception occurred ni always the last
        string kwenye the output.
        """
        ikiwa self.exc_type ni Tupu:
            tuma _format_final_exc_line(Tupu, self._str)
            rudisha

        stype = self.exc_type.__qualname__
        smod = self.exc_type.__module__
        ikiwa smod haiko kwenye ("__main__", "builtins"):
            stype = smod + '.' + stype

        ikiwa sio issubclass(self.exc_type, SyntaxError):
            tuma _format_final_exc_line(stype, self._str)
            rudisha

        # It was a syntax error; show exactly where the problem was found.
        filename = self.filename ama "<string>"
        lineno = str(self.lineno) ama '?'
        tuma '  File "{}", line {}\n'.format(filename, lineno)

        badline = self.text
        offset = self.offset
        ikiwa badline ni sio Tupu:
            tuma '    {}\n'.format(badline.strip())
            ikiwa offset ni sio Tupu:
                caretspace = badline.rstrip('\n')
                offset = min(len(caretspace), offset) - 1
                caretspace = caretspace[:offset].lstrip()
                # non-space whitespace (likes tabs) must be kept kila alignment
                caretspace = ((c.isspace() na c ama ' ') kila c kwenye caretspace)
                tuma '    {}^\n'.format(''.join(caretspace))
        msg = self.msg ama "<no detail available>"
        tuma "{}: {}\n".format(stype, msg)

    eleza format(self, *, chain=Kweli):
        """Format the exception.

        If chain ni sio *Kweli*, *__cause__* na *__context__* will sio be formatted.

        The rudisha value ni a generator of strings, each ending kwenye a newline and
        some containing internal newlines. `print_exception` ni a wrapper around
        this method which just prints the lines to a file.

        The message indicating which exception occurred ni always the last
        string kwenye the output.
        """
        ikiwa chain:
            ikiwa self.__cause__ ni sio Tupu:
                tuma kutoka self.__cause__.format(chain=chain)
                tuma _cause_message
            elikiwa (self.__context__ ni sio Tupu and
                sio self.__suppress_context__):
                tuma kutoka self.__context__.format(chain=chain)
                tuma _context_message
        ikiwa self.exc_traceback ni sio Tupu:
            tuma 'Traceback (most recent call last):\n'
        tuma kutoka self.stack.format()
        tuma kutoka self.format_exception_only()
