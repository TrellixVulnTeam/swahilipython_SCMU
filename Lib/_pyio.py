"""
Python implementation of the io module.
"""

agiza os
agiza abc
agiza codecs
agiza errno
agiza stat
agiza sys
# Import _thread instead of threading to reduce startup cost
kutoka _thread agiza allocate_lock kama Lock
ikiwa sys.platform kwenye {'win32', 'cygwin'}:
    kutoka msvcrt agiza setmode kama _setmode
isipokua:
    _setmode = Tupu

agiza io
kutoka io agiza (__all__, SEEK_SET, SEEK_CUR, SEEK_END)

valid_seek_flags = {0, 1, 2}  # Hardwired values
ikiwa hasattr(os, 'SEEK_HOLE') :
    valid_seek_flags.add(os.SEEK_HOLE)
    valid_seek_flags.add(os.SEEK_DATA)

# open() uses st_blksize whenever we can
DEFAULT_BUFFER_SIZE = 8 * 1024  # bytes

# NOTE: Base classes defined here are registered ukijumuisha the "official" ABCs
# defined kwenye io.py. We don't use real inheritance though, because we don't want
# to inherit the C implementations.

# Rebind kila compatibility
BlockingIOError = BlockingIOError

# Does io.IOBase finalizer log the exception ikiwa the close() method fails?
# The exception ni ignored silently by default kwenye release build.
_IOBASE_EMITS_UNRAISABLE = (hasattr(sys, "gettotalrefcount") ama sys.flags.dev_mode)


eleza open(file, mode="r", buffering=-1, encoding=Tupu, errors=Tupu,
         newline=Tupu, closefd=Kweli, opener=Tupu):

    r"""Open file na rudisha a stream.  Raise OSError upon failure.

    file ni either a text ama byte string giving the name (and the path
    ikiwa the file isn't kwenye the current working directory) of the file to
    be opened ama an integer file descriptor of the file to be
    wrapped. (If a file descriptor ni given, it ni closed when the
    returned I/O object ni closed, unless closefd ni set to Uongo.)

    mode ni an optional string that specifies the mode kwenye which the file is
    opened. It defaults to 'r' which means open kila reading kwenye text mode. Other
    common values are 'w' kila writing (truncating the file ikiwa it already
    exists), 'x' kila exclusive creation of a new file, na 'a' kila appending
    (which on some Unix systems, means that all writes append to the end of the
    file regardless of the current seek position). In text mode, ikiwa encoding is
    sio specified the encoding used ni platform dependent. (For reading na
    writing raw bytes use binary mode na leave encoding unspecified.) The
    available modes are:

    ========= ===============================================================
    Character Meaning
    --------- ---------------------------------------------------------------
    'r'       open kila reading (default)
    'w'       open kila writing, truncating the file first
    'x'       create a new file na open it kila writing
    'a'       open kila writing, appending to the end of the file ikiwa it exists
    'b'       binary mode
    't'       text mode (default)
    '+'       open a disk file kila updating (reading na writing)
    'U'       universal newline mode (deprecated)
    ========= ===============================================================

    The default mode ni 'rt' (open kila reading text). For binary random
    access, the mode 'w+b' opens na truncates the file to 0 bytes, while
    'r+b' opens the file without truncation. The 'x' mode implies 'w' na
    raises an `FileExistsError` ikiwa the file already exists.

    Python distinguishes between files opened kwenye binary na text modes,
    even when the underlying operating system doesn't. Files opened in
    binary mode (appending 'b' to the mode argument) rudisha contents as
    bytes objects without any decoding. In text mode (the default, ama when
    't' ni appended to the mode argument), the contents of the file are
    returned kama strings, the bytes having been first decoded using a
    platform-dependent encoding ama using the specified encoding ikiwa given.

    'U' mode ni deprecated na will ashiria an exception kwenye future versions
    of Python.  It has no effect kwenye Python 3.  Use newline to control
    universal newlines mode.

    buffering ni an optional integer used to set the buffering policy.
    Pass 0 to switch buffering off (only allowed kwenye binary mode), 1 to select
    line buffering (only usable kwenye text mode), na an integer > 1 to indicate
    the size of a fixed-size chunk buffer.  When no buffering argument is
    given, the default buffering policy works kama follows:

    * Binary files are buffered kwenye fixed-size chunks; the size of the buffer
      ni chosen using a heuristic trying to determine the underlying device's
      "block size" na falling back on `io.DEFAULT_BUFFER_SIZE`.
      On many systems, the buffer will typically be 4096 ama 8192 bytes long.

    * "Interactive" text files (files kila which isatty() returns Kweli)
      use line buffering.  Other text files use the policy described above
      kila binary files.

    encoding ni the str name of the encoding used to decode ama encode the
    file. This should only be used kwenye text mode. The default encoding is
    platform dependent, but any encoding supported by Python can be
    pitaed.  See the codecs module kila the list of supported encodings.

    errors ni an optional string that specifies how encoding errors are to
    be handled---this argument should sio be used kwenye binary mode. Pass
    'strict' to ashiria a ValueError exception ikiwa there ni an encoding error
    (the default of Tupu has the same effect), ama pita 'ignore' to ignore
    errors. (Note that ignoring encoding errors can lead to data loss.)
    See the documentation kila codecs.register kila a list of the permitted
    encoding error strings.

    newline ni a string controlling how universal newlines works (it only
    applies to text mode). It can be Tupu, '', '\n', '\r', na '\r\n'.  It works
    kama follows:

    * On input, ikiwa newline ni Tupu, universal newlines mode is
      enabled. Lines kwenye the input can end kwenye '\n', '\r', ama '\r\n', na
      these are translated into '\n' before being returned to the
      caller. If it ni '', universal newline mode ni enabled, but line
      endings are returned to the caller untranslated. If it has any of
      the other legal values, input lines are only terminated by the given
      string, na the line ending ni returned to the caller untranslated.

    * On output, ikiwa newline ni Tupu, any '\n' characters written are
      translated to the system default line separator, os.linesep. If
      newline ni '', no translation takes place. If newline ni any of the
      other legal values, any '\n' characters written are translated to
      the given string.

    closedfd ni a bool. If closefd ni Uongo, the underlying file descriptor will
    be kept open when the file ni closed. This does sio work when a file name is
    given na must be Kweli kwenye that case.

    The newly created file ni non-inheritable.

    A custom opener can be used by pitaing a callable kama *opener*. The
    underlying file descriptor kila the file object ni then obtained by calling
    *opener* ukijumuisha (*file*, *flags*). *opener* must rudisha an open file
    descriptor (pitaing os.open kama *opener* results kwenye functionality similar to
    pitaing Tupu).

    open() returns a file object whose type depends on the mode, na
    through which the standard file operations such kama reading na writing
    are performed. When open() ni used to open a file kwenye a text mode ('w',
    'r', 'wt', 'rt', etc.), it returns a TextIOWrapper. When used to open
    a file kwenye a binary mode, the returned kundi varies: kwenye read binary
    mode, it returns a BufferedReader; kwenye write binary na append binary
    modes, it returns a BufferedWriter, na kwenye read/write mode, it returns
    a BufferedRandom.

    It ni also possible to use a string ama bytearray kama a file kila both
    reading na writing. For strings StringIO can be used like a file
    opened kwenye a text mode, na kila bytes a BytesIO can be used like a file
    opened kwenye a binary mode.
    """
    ikiwa sio isinstance(file, int):
        file = os.fspath(file)
    ikiwa sio isinstance(file, (str, bytes, int)):
        ashiria TypeError("invalid file: %r" % file)
    ikiwa sio isinstance(mode, str):
        ashiria TypeError("invalid mode: %r" % mode)
    ikiwa sio isinstance(buffering, int):
        ashiria TypeError("invalid buffering: %r" % buffering)
    ikiwa encoding ni sio Tupu na sio isinstance(encoding, str):
        ashiria TypeError("invalid encoding: %r" % encoding)
    ikiwa errors ni sio Tupu na sio isinstance(errors, str):
        ashiria TypeError("invalid errors: %r" % errors)
    modes = set(mode)
    ikiwa modes - set("axrwb+tU") ama len(mode) > len(modes):
        ashiria ValueError("invalid mode: %r" % mode)
    creating = "x" kwenye modes
    reading = "r" kwenye modes
    writing = "w" kwenye modes
    appending = "a" kwenye modes
    updating = "+" kwenye modes
    text = "t" kwenye modes
    binary = "b" kwenye modes
    ikiwa "U" kwenye modes:
        ikiwa creating ama writing ama appending ama updating:
            ashiria ValueError("mode U cannot be combined ukijumuisha 'x', 'w', 'a', ama '+'")
        agiza warnings
        warnings.warn("'U' mode ni deprecated",
                      DeprecationWarning, 2)
        reading = Kweli
    ikiwa text na binary:
        ashiria ValueError("can't have text na binary mode at once")
    ikiwa creating + reading + writing + appending > 1:
        ashiria ValueError("can't have read/write/append mode at once")
    ikiwa sio (creating ama reading ama writing ama appending):
        ashiria ValueError("must have exactly one of read/write/append mode")
    ikiwa binary na encoding ni sio Tupu:
        ashiria ValueError("binary mode doesn't take an encoding argument")
    ikiwa binary na errors ni sio Tupu:
        ashiria ValueError("binary mode doesn't take an errors argument")
    ikiwa binary na newline ni sio Tupu:
        ashiria ValueError("binary mode doesn't take a newline argument")
    ikiwa binary na buffering == 1:
        agiza warnings
        warnings.warn("line buffering (buffering=1) isn't supported kwenye binary "
                      "mode, the default buffer size will be used",
                      RuntimeWarning, 2)
    raw = FileIO(file,
                 (creating na "x" ama "") +
                 (reading na "r" ama "") +
                 (writing na "w" ama "") +
                 (appending na "a" ama "") +
                 (updating na "+" ama ""),
                 closefd, opener=opener)
    result = raw
    jaribu:
        line_buffering = Uongo
        ikiwa buffering == 1 ama buffering < 0 na raw.isatty():
            buffering = -1
            line_buffering = Kweli
        ikiwa buffering < 0:
            buffering = DEFAULT_BUFFER_SIZE
            jaribu:
                bs = os.fstat(raw.fileno()).st_blksize
            tatizo (OSError, AttributeError):
                pita
            isipokua:
                ikiwa bs > 1:
                    buffering = bs
        ikiwa buffering < 0:
            ashiria ValueError("invalid buffering size")
        ikiwa buffering == 0:
            ikiwa binary:
                rudisha result
            ashiria ValueError("can't have unbuffered text I/O")
        ikiwa updating:
            buffer = BufferedRandom(raw, buffering)
        lasivyo creating ama writing ama appending:
            buffer = BufferedWriter(raw, buffering)
        lasivyo reading:
            buffer = BufferedReader(raw, buffering)
        isipokua:
            ashiria ValueError("unknown mode: %r" % mode)
        result = buffer
        ikiwa binary:
            rudisha result
        text = TextIOWrapper(buffer, encoding, errors, newline, line_buffering)
        result = text
        text.mode = mode
        rudisha result
    tatizo:
        result.close()
        raise

# Define a default pure-Python implementation kila open_code()
# that does sio allow hooks. Warn on first use. Defined kila tests.
eleza _open_code_with_warning(path):
    """Opens the provided file ukijumuisha mode ``'rb'``. This function
    should be used when the intent ni to treat the contents as
    executable code.

    ``path`` should be an absolute path.

    When supported by the runtime, this function can be hooked
    kwenye order to allow embedders more control over code files.
    This functionality ni sio supported on the current runtime.
    """
    agiza warnings
    warnings.warn("_pyio.open_code() may sio be using hooks",
                  RuntimeWarning, 2)
    rudisha open(path, "rb")

jaribu:
    open_code = io.open_code
tatizo AttributeError:
    open_code = _open_code_with_warning


kundi DocDescriptor:
    """Helper kila builtins.open.__doc__
    """
    eleza __get__(self, obj, typ=Tupu):
        rudisha (
            "open(file, mode='r', buffering=-1, encoding=Tupu, "
                 "errors=Tupu, newline=Tupu, closefd=Kweli)\n\n" +
            open.__doc__)

kundi OpenWrapper:
    """Wrapper kila builtins.open

    Trick so that open won't become a bound method when stored
    kama a kundi variable (as dbm.dumb does).

    See initstdio() kwenye Python/pylifecycle.c.
    """
    __doc__ = DocDescriptor()

    eleza __new__(cls, *args, **kwargs):
        rudisha open(*args, **kwargs)


# In normal operation, both `UnsupportedOperation`s should be bound to the
# same object.
jaribu:
    UnsupportedOperation = io.UnsupportedOperation
tatizo AttributeError:
    kundi UnsupportedOperation(OSError, ValueError):
        pita


kundi IOBase(metaclass=abc.ABCMeta):

    """The abstract base kundi kila all I/O classes, acting on streams of
    bytes. There ni no public constructor.

    This kundi provides dummy implementations kila many methods that
    derived classes can override selectively; the default implementations
    represent a file that cannot be read, written ama seeked.

    Even though IOBase does sio declare read ama write because
    their signatures will vary, implementations na clients should
    consider those methods part of the interface. Also, implementations
    may ashiria UnsupportedOperation when operations they do sio support are
    called.

    The basic type used kila binary data read kutoka ama written to a file is
    bytes. Other bytes-like objects are accepted kama method arguments too.
    Text I/O classes work ukijumuisha str data.

    Note that calling any method (even inquiries) on a closed stream is
    undefined. Implementations may ashiria OSError kwenye this case.

    IOBase (and its subclasses) support the iterator protocol, meaning
    that an IOBase object can be iterated over tumaing the lines kwenye a
    stream.

    IOBase also supports the :keyword:`with` statement. In this example,
    fp ni closed after the suite of the ukijumuisha statement ni complete:

    ukijumuisha open('spam.txt', 'r') kama fp:
        fp.write('Spam na eggs!')
    """

    ### Internal ###

    eleza _unsupported(self, name):
        """Internal: ashiria an OSError exception kila unsupported operations."""
        ashiria UnsupportedOperation("%s.%s() sio supported" %
                                   (self.__class__.__name__, name))

    ### Positioning ###

    eleza seek(self, pos, whence=0):
        """Change stream position.

        Change the stream position to byte offset pos. Argument pos is
        interpreted relative to the position indicated by whence.  Values
        kila whence are ints:

        * 0 -- start of stream (the default); offset should be zero ama positive
        * 1 -- current stream position; offset may be negative
        * 2 -- end of stream; offset ni usually negative
        Some operating systems / file systems could provide additional values.

        Return an int indicating the new absolute position.
        """
        self._unsupported("seek")

    eleza tell(self):
        """Return an int indicating the current stream position."""
        rudisha self.seek(0, 1)

    eleza truncate(self, pos=Tupu):
        """Truncate file to size bytes.

        Size defaults to the current IO position kama reported by tell().  Return
        the new size.
        """
        self._unsupported("truncate")

    ### Flush na close ###

    eleza flush(self):
        """Flush write buffers, ikiwa applicable.

        This ni sio implemented kila read-only na non-blocking streams.
        """
        self._checkClosed()
        # XXX Should this rudisha the number of bytes written???

    __closed = Uongo

    eleza close(self):
        """Flush na close the IO object.

        This method has no effect ikiwa the file ni already closed.
        """
        ikiwa sio self.__closed:
            jaribu:
                self.flush()
            mwishowe:
                self.__closed = Kweli

    eleza __del__(self):
        """Destructor.  Calls close()."""
        jaribu:
            closed = self.closed
        tatizo AttributeError:
            # If getting closed fails, then the object ni probably
            # kwenye an unusable state, so ignore.
            return

        ikiwa closed:
            return

        ikiwa _IOBASE_EMITS_UNRAISABLE:
            self.close()
        isipokua:
            # The try/tatizo block ni kwenye case this ni called at program
            # exit time, when it's possible that globals have already been
            # deleted, na then the close() call might fail.  Since
            # there's nothing we can do about such failures na they annoy
            # the end users, we suppress the traceback.
            jaribu:
                self.close()
            tatizo:
                pita

    ### Inquiries ###

    eleza seekable(self):
        """Return a bool indicating whether object supports random access.

        If Uongo, seek(), tell() na truncate() will ashiria OSError.
        This method may need to do a test seek().
        """
        rudisha Uongo

    eleza _checkSeekable(self, msg=Tupu):
        """Internal: ashiria UnsupportedOperation ikiwa file ni sio seekable
        """
        ikiwa sio self.seekable():
            ashiria UnsupportedOperation("File ama stream ni sio seekable."
                                       ikiwa msg ni Tupu isipokua msg)

    eleza readable(self):
        """Return a bool indicating whether object was opened kila reading.

        If Uongo, read() will ashiria OSError.
        """
        rudisha Uongo

    eleza _checkReadable(self, msg=Tupu):
        """Internal: ashiria UnsupportedOperation ikiwa file ni sio readable
        """
        ikiwa sio self.readable():
            ashiria UnsupportedOperation("File ama stream ni sio readable."
                                       ikiwa msg ni Tupu isipokua msg)

    eleza writable(self):
        """Return a bool indicating whether object was opened kila writing.

        If Uongo, write() na truncate() will ashiria OSError.
        """
        rudisha Uongo

    eleza _checkWritable(self, msg=Tupu):
        """Internal: ashiria UnsupportedOperation ikiwa file ni sio writable
        """
        ikiwa sio self.writable():
            ashiria UnsupportedOperation("File ama stream ni sio writable."
                                       ikiwa msg ni Tupu isipokua msg)

    @property
    eleza closed(self):
        """closed: bool.  Kweli iff the file has been closed.

        For backwards compatibility, this ni a property, sio a predicate.
        """
        rudisha self.__closed

    eleza _checkClosed(self, msg=Tupu):
        """Internal: ashiria a ValueError ikiwa file ni closed
        """
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file."
                             ikiwa msg ni Tupu isipokua msg)

    ### Context manager ###

    eleza __enter__(self):  # That's a forward reference
        """Context management protocol.  Returns self (an instance of IOBase)."""
        self._checkClosed()
        rudisha self

    eleza __exit__(self, *args):
        """Context management protocol.  Calls close()"""
        self.close()

    ### Lower-level APIs ###

    # XXX Should these be present even ikiwa unimplemented?

    eleza fileno(self):
        """Returns underlying file descriptor (an int) ikiwa one exists.

        An OSError ni raised ikiwa the IO object does sio use a file descriptor.
        """
        self._unsupported("fileno")

    eleza isatty(self):
        """Return a bool indicating whether this ni an 'interactive' stream.

        Return Uongo ikiwa it can't be determined.
        """
        self._checkClosed()
        rudisha Uongo

    ### Readline[s] na writelines ###

    eleza readline(self, size=-1):
        r"""Read na rudisha a line of bytes kutoka the stream.

        If size ni specified, at most size bytes will be read.
        Size should be an int.

        The line terminator ni always b'\n' kila binary files; kila text
        files, the newlines argument to open can be used to select the line
        terminator(s) recognized.
        """
        # For backwards compatibility, a (slowish) readline().
        ikiwa hasattr(self, "peek"):
            eleza nreadahead():
                readahead = self.peek(1)
                ikiwa sio readahead:
                    rudisha 1
                n = (readahead.find(b"\n") + 1) ama len(readahead)
                ikiwa size >= 0:
                    n = min(n, size)
                rudisha n
        isipokua:
            eleza nreadahead():
                rudisha 1
        ikiwa size ni Tupu:
            size = -1
        isipokua:
            jaribu:
                size_index = size.__index__
            tatizo AttributeError:
                ashiria TypeError(f"{size!r} ni sio an integer")
            isipokua:
                size = size_index()
        res = bytearray()
        wakati size < 0 ama len(res) < size:
            b = self.read(nreadahead())
            ikiwa sio b:
                koma
            res += b
            ikiwa res.endswith(b"\n"):
                koma
        rudisha bytes(res)

    eleza __iter__(self):
        self._checkClosed()
        rudisha self

    eleza __next__(self):
        line = self.readline()
        ikiwa sio line:
            ashiria StopIteration
        rudisha line

    eleza readlines(self, hint=Tupu):
        """Return a list of lines kutoka the stream.

        hint can be specified to control the number of lines read: no more
        lines will be read ikiwa the total size (in bytes/characters) of all
        lines so far exceeds hint.
        """
        ikiwa hint ni Tupu ama hint <= 0:
            rudisha list(self)
        n = 0
        lines = []
        kila line kwenye self:
            lines.append(line)
            n += len(line)
            ikiwa n >= hint:
                koma
        rudisha lines

    eleza writelines(self, lines):
        """Write a list of lines to the stream.

        Line separators are sio added, so it ni usual kila each of the lines
        provided to have a line separator at the end.
        """
        self._checkClosed()
        kila line kwenye lines:
            self.write(line)

io.IOBase.register(IOBase)


kundi RawIOBase(IOBase):

    """Base kundi kila raw binary I/O."""

    # The read() method ni implemented by calling readinto(); derived
    # classes that want to support read() only need to implement
    # readinto() kama a primitive operation.  In general, readinto() can be
    # more efficient than read().

    # (It would be tempting to also provide an implementation of
    # readinto() kwenye terms of read(), kwenye case the latter ni a more suitable
    # primitive operation, but that would lead to nasty recursion kwenye case
    # a subkundi doesn't implement either.)

    eleza read(self, size=-1):
        """Read na rudisha up to size bytes, where size ni an int.

        Returns an empty bytes object on EOF, ama Tupu ikiwa the object is
        set sio to block na has no data to read.
        """
        ikiwa size ni Tupu:
            size = -1
        ikiwa size < 0:
            rudisha self.readall()
        b = bytearray(size.__index__())
        n = self.readinto(b)
        ikiwa n ni Tupu:
            rudisha Tupu
        toa b[n:]
        rudisha bytes(b)

    eleza readall(self):
        """Read until EOF, using multiple read() call."""
        res = bytearray()
        wakati Kweli:
            data = self.read(DEFAULT_BUFFER_SIZE)
            ikiwa sio data:
                koma
            res += data
        ikiwa res:
            rudisha bytes(res)
        isipokua:
            # b'' ama Tupu
            rudisha data

    eleza readinto(self, b):
        """Read bytes into a pre-allocated bytes-like object b.

        Returns an int representing the number of bytes read (0 kila EOF), ama
        Tupu ikiwa the object ni set sio to block na has no data to read.
        """
        self._unsupported("readinto")

    eleza write(self, b):
        """Write the given buffer to the IO stream.

        Returns the number of bytes written, which may be less than the
        length of b kwenye bytes.
        """
        self._unsupported("write")

io.RawIOBase.register(RawIOBase)
kutoka _io agiza FileIO
RawIOBase.register(FileIO)


kundi BufferedIOBase(IOBase):

    """Base kundi kila buffered IO objects.

    The main difference ukijumuisha RawIOBase ni that the read() method
    supports omitting the size argument, na does sio have a default
    implementation that defers to readinto().

    In addition, read(), readinto() na write() may raise
    BlockingIOError ikiwa the underlying raw stream ni kwenye non-blocking
    mode na sio ready; unlike their raw counterparts, they will never
    rudisha Tupu.

    A typical implementation should sio inherit kutoka a RawIOBase
    implementation, but wrap one.
    """

    eleza read(self, size=-1):
        """Read na rudisha up to size bytes, where size ni an int.

        If the argument ni omitted, Tupu, ama negative, reads na
        returns all data until EOF.

        If the argument ni positive, na the underlying raw stream is
        sio 'interactive', multiple raw reads may be issued to satisfy
        the byte count (unless EOF ni reached first).  But for
        interactive raw streams (XXX na kila pipes?), at most one raw
        read will be issued, na a short result does sio imply that
        EOF ni imminent.

        Returns an empty bytes array on EOF.

        Raises BlockingIOError ikiwa the underlying raw stream has no
        data at the moment.
        """
        self._unsupported("read")

    eleza read1(self, size=-1):
        """Read up to size bytes ukijumuisha at most one read() system call,
        where size ni an int.
        """
        self._unsupported("read1")

    eleza readinto(self, b):
        """Read bytes into a pre-allocated bytes-like object b.

        Like read(), this may issue multiple reads to the underlying raw
        stream, unless the latter ni 'interactive'.

        Returns an int representing the number of bytes read (0 kila EOF).

        Raises BlockingIOError ikiwa the underlying raw stream has no
        data at the moment.
        """

        rudisha self._readinto(b, read1=Uongo)

    eleza readinto1(self, b):
        """Read bytes into buffer *b*, using at most one system call

        Returns an int representing the number of bytes read (0 kila EOF).

        Raises BlockingIOError ikiwa the underlying raw stream has no
        data at the moment.
        """

        rudisha self._readinto(b, read1=Kweli)

    eleza _readinto(self, b, read1):
        ikiwa sio isinstance(b, memoryview):
            b = memoryview(b)
        b = b.cast('B')

        ikiwa read1:
            data = self.read1(len(b))
        isipokua:
            data = self.read(len(b))
        n = len(data)

        b[:n] = data

        rudisha n

    eleza write(self, b):
        """Write the given bytes buffer to the IO stream.

        Return the number of bytes written, which ni always the length of b
        kwenye bytes.

        Raises BlockingIOError ikiwa the buffer ni full na the
        underlying raw stream cannot accept more data at the moment.
        """
        self._unsupported("write")

    eleza detach(self):
        """
        Separate the underlying raw stream kutoka the buffer na rudisha it.

        After the raw stream has been detached, the buffer ni kwenye an unusable
        state.
        """
        self._unsupported("detach")

io.BufferedIOBase.register(BufferedIOBase)


kundi _BufferedIOMixin(BufferedIOBase):

    """A mixin implementation of BufferedIOBase ukijumuisha an underlying raw stream.

    This pitaes most requests on to the underlying raw stream.  It
    does *not* provide implementations of read(), readinto() ama
    write().
    """

    eleza __init__(self, raw):
        self._raw = raw

    ### Positioning ###

    eleza seek(self, pos, whence=0):
        new_position = self.raw.seek(pos, whence)
        ikiwa new_position < 0:
            ashiria OSError("seek() returned an invalid position")
        rudisha new_position

    eleza tell(self):
        pos = self.raw.tell()
        ikiwa pos < 0:
            ashiria OSError("tell() returned an invalid position")
        rudisha pos

    eleza truncate(self, pos=Tupu):
        # Flush the stream.  We're mixing buffered I/O ukijumuisha lower-level I/O,
        # na a flush may be necessary to synch both views of the current
        # file state.
        self.flush()

        ikiwa pos ni Tupu:
            pos = self.tell()
        # XXX: Should seek() be used, instead of pitaing the position
        # XXX  directly to truncate?
        rudisha self.raw.truncate(pos)

    ### Flush na close ###

    eleza flush(self):
        ikiwa self.closed:
            ashiria ValueError("flush on closed file")
        self.raw.flush()

    eleza close(self):
        ikiwa self.raw ni sio Tupu na sio self.closed:
            jaribu:
                # may ashiria BlockingIOError ama BrokenPipeError etc
                self.flush()
            mwishowe:
                self.raw.close()

    eleza detach(self):
        ikiwa self.raw ni Tupu:
            ashiria ValueError("raw stream already detached")
        self.flush()
        raw = self._raw
        self._raw = Tupu
        rudisha raw

    ### Inquiries ###

    eleza seekable(self):
        rudisha self.raw.seekable()

    @property
    eleza raw(self):
        rudisha self._raw

    @property
    eleza closed(self):
        rudisha self.raw.closed

    @property
    eleza name(self):
        rudisha self.raw.name

    @property
    eleza mode(self):
        rudisha self.raw.mode

    eleza __getstate__(self):
        ashiria TypeError(f"cannot pickle {self.__class__.__name__!r} object")

    eleza __repr__(self):
        modname = self.__class__.__module__
        clsname = self.__class__.__qualname__
        jaribu:
            name = self.name
        tatizo AttributeError:
            rudisha "<{}.{}>".format(modname, clsname)
        isipokua:
            rudisha "<{}.{} name={!r}>".format(modname, clsname, name)

    ### Lower-level APIs ###

    eleza fileno(self):
        rudisha self.raw.fileno()

    eleza isatty(self):
        rudisha self.raw.isatty()


kundi BytesIO(BufferedIOBase):

    """Buffered I/O implementation using an in-memory bytes buffer."""

    # Initialize _buffer kama soon kama possible since it's used by __del__()
    # which calls close()
    _buffer = Tupu

    eleza __init__(self, initial_bytes=Tupu):
        buf = bytearray()
        ikiwa initial_bytes ni sio Tupu:
            buf += initial_bytes
        self._buffer = buf
        self._pos = 0

    eleza __getstate__(self):
        ikiwa self.closed:
            ashiria ValueError("__getstate__ on closed file")
        rudisha self.__dict__.copy()

    eleza getvalue(self):
        """Return the bytes value (contents) of the buffer
        """
        ikiwa self.closed:
            ashiria ValueError("getvalue on closed file")
        rudisha bytes(self._buffer)

    eleza getbuffer(self):
        """Return a readable na writable view of the buffer.
        """
        ikiwa self.closed:
            ashiria ValueError("getbuffer on closed file")
        rudisha memoryview(self._buffer)

    eleza close(self):
        ikiwa self._buffer ni sio Tupu:
            self._buffer.clear()
        super().close()

    eleza read(self, size=-1):
        ikiwa self.closed:
            ashiria ValueError("read kutoka closed file")
        ikiwa size ni Tupu:
            size = -1
        isipokua:
            jaribu:
                size_index = size.__index__
            tatizo AttributeError:
                ashiria TypeError(f"{size!r} ni sio an integer")
            isipokua:
                size = size_index()
        ikiwa size < 0:
            size = len(self._buffer)
        ikiwa len(self._buffer) <= self._pos:
            rudisha b""
        newpos = min(len(self._buffer), self._pos + size)
        b = self._buffer[self._pos : newpos]
        self._pos = newpos
        rudisha bytes(b)

    eleza read1(self, size=-1):
        """This ni the same kama read.
        """
        rudisha self.read(size)

    eleza write(self, b):
        ikiwa self.closed:
            ashiria ValueError("write to closed file")
        ikiwa isinstance(b, str):
            ashiria TypeError("can't write str to binary stream")
        ukijumuisha memoryview(b) kama view:
            n = view.nbytes  # Size of any bytes-like object
        ikiwa n == 0:
            rudisha 0
        pos = self._pos
        ikiwa pos > len(self._buffer):
            # Inserts null bytes between the current end of the file
            # na the new write position.
            padding = b'\x00' * (pos - len(self._buffer))
            self._buffer += padding
        self._buffer[pos:pos + n] = b
        self._pos += n
        rudisha n

    eleza seek(self, pos, whence=0):
        ikiwa self.closed:
            ashiria ValueError("seek on closed file")
        jaribu:
            pos_index = pos.__index__
        tatizo AttributeError:
            ashiria TypeError(f"{pos!r} ni sio an integer")
        isipokua:
            pos = pos_index()
        ikiwa whence == 0:
            ikiwa pos < 0:
                ashiria ValueError("negative seek position %r" % (pos,))
            self._pos = pos
        lasivyo whence == 1:
            self._pos = max(0, self._pos + pos)
        lasivyo whence == 2:
            self._pos = max(0, len(self._buffer) + pos)
        isipokua:
            ashiria ValueError("unsupported whence value")
        rudisha self._pos

    eleza tell(self):
        ikiwa self.closed:
            ashiria ValueError("tell on closed file")
        rudisha self._pos

    eleza truncate(self, pos=Tupu):
        ikiwa self.closed:
            ashiria ValueError("truncate on closed file")
        ikiwa pos ni Tupu:
            pos = self._pos
        isipokua:
            jaribu:
                pos_index = pos.__index__
            tatizo AttributeError:
                ashiria TypeError(f"{pos!r} ni sio an integer")
            isipokua:
                pos = pos_index()
            ikiwa pos < 0:
                ashiria ValueError("negative truncate position %r" % (pos,))
        toa self._buffer[pos:]
        rudisha pos

    eleza readable(self):
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file.")
        rudisha Kweli

    eleza writable(self):
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file.")
        rudisha Kweli

    eleza seekable(self):
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file.")
        rudisha Kweli


kundi BufferedReader(_BufferedIOMixin):

    """BufferedReader(raw[, buffer_size])

    A buffer kila a readable, sequential BaseRawIO object.

    The constructor creates a BufferedReader kila the given readable raw
    stream na buffer_size. If buffer_size ni omitted, DEFAULT_BUFFER_SIZE
    ni used.
    """

    eleza __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        """Create a new buffered reader using the given readable raw IO object.
        """
        ikiwa sio raw.readable():
            ashiria OSError('"raw" argument must be readable.')

        _BufferedIOMixin.__init__(self, raw)
        ikiwa buffer_size <= 0:
            ashiria ValueError("invalid buffer size")
        self.buffer_size = buffer_size
        self._reset_read_buf()
        self._read_lock = Lock()

    eleza readable(self):
        rudisha self.raw.readable()

    eleza _reset_read_buf(self):
        self._read_buf = b""
        self._read_pos = 0

    eleza read(self, size=Tupu):
        """Read size bytes.

        Returns exactly size bytes of data unless the underlying raw IO
        stream reaches EOF ama ikiwa the call would block kwenye non-blocking
        mode. If size ni negative, read until EOF ama until read() would
        block.
        """
        ikiwa size ni sio Tupu na size < -1:
            ashiria ValueError("invalid number of bytes to read")
        ukijumuisha self._read_lock:
            rudisha self._read_unlocked(size)

    eleza _read_unlocked(self, n=Tupu):
        nodata_val = b""
        empty_values = (b"", Tupu)
        buf = self._read_buf
        pos = self._read_pos

        # Special case kila when the number of bytes to read ni unspecified.
        ikiwa n ni Tupu ama n == -1:
            self._reset_read_buf()
            ikiwa hasattr(self.raw, 'readall'):
                chunk = self.raw.readall()
                ikiwa chunk ni Tupu:
                    rudisha buf[pos:] ama Tupu
                isipokua:
                    rudisha buf[pos:] + chunk
            chunks = [buf[pos:]]  # Strip the consumed bytes.
            current_size = 0
            wakati Kweli:
                # Read until EOF ama until read() would block.
                chunk = self.raw.read()
                ikiwa chunk kwenye empty_values:
                    nodata_val = chunk
                    koma
                current_size += len(chunk)
                chunks.append(chunk)
            rudisha b"".join(chunks) ama nodata_val

        # The number of bytes to read ni specified, rudisha at most n bytes.
        avail = len(buf) - pos  # Length of the available buffered data.
        ikiwa n <= avail:
            # Fast path: the data to read ni fully buffered.
            self._read_pos += n
            rudisha buf[pos:pos+n]
        # Slow path: read kutoka the stream until enough bytes are read,
        # ama until an EOF occurs ama until read() would block.
        chunks = [buf[pos:]]
        wanted = max(self.buffer_size, n)
        wakati avail < n:
            chunk = self.raw.read(wanted)
            ikiwa chunk kwenye empty_values:
                nodata_val = chunk
                koma
            avail += len(chunk)
            chunks.append(chunk)
        # n ni more than avail only when an EOF occurred ama when
        # read() would have blocked.
        n = min(n, avail)
        out = b"".join(chunks)
        self._read_buf = out[n:]  # Save the extra data kwenye the buffer.
        self._read_pos = 0
        rudisha out[:n] ikiwa out isipokua nodata_val

    eleza peek(self, size=0):
        """Returns buffered bytes without advancing the position.

        The argument indicates a desired minimal number of bytes; we
        do at most one raw read to satisfy it.  We never rudisha more
        than self.buffer_size.
        """
        ukijumuisha self._read_lock:
            rudisha self._peek_unlocked(size)

    eleza _peek_unlocked(self, n=0):
        want = min(n, self.buffer_size)
        have = len(self._read_buf) - self._read_pos
        ikiwa have < want ama have <= 0:
            to_read = self.buffer_size - have
            current = self.raw.read(to_read)
            ikiwa current:
                self._read_buf = self._read_buf[self._read_pos:] + current
                self._read_pos = 0
        rudisha self._read_buf[self._read_pos:]

    eleza read1(self, size=-1):
        """Reads up to size bytes, ukijumuisha at most one read() system call."""
        # Returns up to size bytes.  If at least one byte ni buffered, we
        # only rudisha buffered bytes.  Otherwise, we do one raw read.
        ikiwa size < 0:
            size = self.buffer_size
        ikiwa size == 0:
            rudisha b""
        ukijumuisha self._read_lock:
            self._peek_unlocked(1)
            rudisha self._read_unlocked(
                min(size, len(self._read_buf) - self._read_pos))

    # Implementing readinto() na readinto1() ni sio strictly necessary (we
    # could rely on the base kundi that provides an implementation kwenye terms of
    # read() na read1()). We do it anyway to keep the _pyio implementation
    # similar to the io implementation (which implements the methods for
    # performance reasons).
    eleza _readinto(self, buf, read1):
        """Read data into *buf* ukijumuisha at most one system call."""

        # Need to create a memoryview object of type 'b', otherwise
        # we may sio be able to assign bytes to it, na slicing it
        # would create a new object.
        ikiwa sio isinstance(buf, memoryview):
            buf = memoryview(buf)
        ikiwa buf.nbytes == 0:
            rudisha 0
        buf = buf.cast('B')

        written = 0
        ukijumuisha self._read_lock:
            wakati written < len(buf):

                # First try to read kutoka internal buffer
                avail = min(len(self._read_buf) - self._read_pos, len(buf))
                ikiwa avail:
                    buf[written:written+avail] = \
                        self._read_buf[self._read_pos:self._read_pos+avail]
                    self._read_pos += avail
                    written += avail
                    ikiwa written == len(buf):
                        koma

                # If remaining space kwenye callers buffer ni larger than
                # internal buffer, read directly into callers buffer
                ikiwa len(buf) - written > self.buffer_size:
                    n = self.raw.readinto(buf[written:])
                    ikiwa sio n:
                        koma # eof
                    written += n

                # Otherwise refill internal buffer - unless we're
                # kwenye read1 mode na already got some data
                lasivyo sio (read1 na written):
                    ikiwa sio self._peek_unlocked(1):
                        koma # eof

                # In readinto1 mode, rudisha kama soon kama we have some data
                ikiwa read1 na written:
                    koma

        rudisha written

    eleza tell(self):
        rudisha _BufferedIOMixin.tell(self) - len(self._read_buf) + self._read_pos

    eleza seek(self, pos, whence=0):
        ikiwa whence haiko kwenye valid_seek_flags:
            ashiria ValueError("invalid whence value")
        ukijumuisha self._read_lock:
            ikiwa whence == 1:
                pos -= len(self._read_buf) - self._read_pos
            pos = _BufferedIOMixin.seek(self, pos, whence)
            self._reset_read_buf()
            rudisha pos

kundi BufferedWriter(_BufferedIOMixin):

    """A buffer kila a writeable sequential RawIO object.

    The constructor creates a BufferedWriter kila the given writeable raw
    stream. If the buffer_size ni sio given, it defaults to
    DEFAULT_BUFFER_SIZE.
    """

    eleza __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        ikiwa sio raw.writable():
            ashiria OSError('"raw" argument must be writable.')

        _BufferedIOMixin.__init__(self, raw)
        ikiwa buffer_size <= 0:
            ashiria ValueError("invalid buffer size")
        self.buffer_size = buffer_size
        self._write_buf = bytearray()
        self._write_lock = Lock()

    eleza writable(self):
        rudisha self.raw.writable()

    eleza write(self, b):
        ikiwa isinstance(b, str):
            ashiria TypeError("can't write str to binary stream")
        ukijumuisha self._write_lock:
            ikiwa self.closed:
                ashiria ValueError("write to closed file")
            # XXX we can implement some more tricks to try na avoid
            # partial writes
            ikiwa len(self._write_buf) > self.buffer_size:
                # We're full, so let's pre-flush the buffer.  (This may
                # ashiria BlockingIOError ukijumuisha characters_written == 0.)
                self._flush_unlocked()
            before = len(self._write_buf)
            self._write_buf.extend(b)
            written = len(self._write_buf) - before
            ikiwa len(self._write_buf) > self.buffer_size:
                jaribu:
                    self._flush_unlocked()
                tatizo BlockingIOError kama e:
                    ikiwa len(self._write_buf) > self.buffer_size:
                        # We've hit the buffer_size. We have to accept a partial
                        # write na cut back our buffer.
                        overage = len(self._write_buf) - self.buffer_size
                        written -= overage
                        self._write_buf = self._write_buf[:self.buffer_size]
                        ashiria BlockingIOError(e.errno, e.strerror, written)
            rudisha written

    eleza truncate(self, pos=Tupu):
        ukijumuisha self._write_lock:
            self._flush_unlocked()
            ikiwa pos ni Tupu:
                pos = self.raw.tell()
            rudisha self.raw.truncate(pos)

    eleza flush(self):
        ukijumuisha self._write_lock:
            self._flush_unlocked()

    eleza _flush_unlocked(self):
        ikiwa self.closed:
            ashiria ValueError("flush on closed file")
        wakati self._write_buf:
            jaribu:
                n = self.raw.write(self._write_buf)
            tatizo BlockingIOError:
                ashiria RuntimeError("self.raw should implement RawIOBase: it "
                                   "should sio ashiria BlockingIOError")
            ikiwa n ni Tupu:
                ashiria BlockingIOError(
                    errno.EAGAIN,
                    "write could sio complete without blocking", 0)
            ikiwa n > len(self._write_buf) ama n < 0:
                ashiria OSError("write() returned incorrect number of bytes")
            toa self._write_buf[:n]

    eleza tell(self):
        rudisha _BufferedIOMixin.tell(self) + len(self._write_buf)

    eleza seek(self, pos, whence=0):
        ikiwa whence haiko kwenye valid_seek_flags:
            ashiria ValueError("invalid whence value")
        ukijumuisha self._write_lock:
            self._flush_unlocked()
            rudisha _BufferedIOMixin.seek(self, pos, whence)

    eleza close(self):
        ukijumuisha self._write_lock:
            ikiwa self.raw ni Tupu ama self.closed:
                return
        # We have to release the lock na call self.flush() (which will
        # probably just re-take the lock) kwenye case flush has been overridden in
        # a subkundi ama the user set self.flush to something. This ni the same
        # behavior kama the C implementation.
        jaribu:
            # may ashiria BlockingIOError ama BrokenPipeError etc
            self.flush()
        mwishowe:
            ukijumuisha self._write_lock:
                self.raw.close()


kundi BufferedRWPair(BufferedIOBase):

    """A buffered reader na writer object together.

    A buffered reader object na buffered writer object put together to
    form a sequential IO object that can read na write. This ni typically
    used ukijumuisha a socket ama two-way pipe.

    reader na writer are RawIOBase objects that are readable na
    writeable respectively. If the buffer_size ni omitted it defaults to
    DEFAULT_BUFFER_SIZE.
    """

    # XXX The usefulness of this (compared to having two separate IO
    # objects) ni questionable.

    eleza __init__(self, reader, writer, buffer_size=DEFAULT_BUFFER_SIZE):
        """Constructor.

        The arguments are two RawIO instances.
        """
        ikiwa sio reader.readable():
            ashiria OSError('"reader" argument must be readable.')

        ikiwa sio writer.writable():
            ashiria OSError('"writer" argument must be writable.')

        self.reader = BufferedReader(reader, buffer_size)
        self.writer = BufferedWriter(writer, buffer_size)

    eleza read(self, size=-1):
        ikiwa size ni Tupu:
            size = -1
        rudisha self.reader.read(size)

    eleza readinto(self, b):
        rudisha self.reader.readinto(b)

    eleza write(self, b):
        rudisha self.writer.write(b)

    eleza peek(self, size=0):
        rudisha self.reader.peek(size)

    eleza read1(self, size=-1):
        rudisha self.reader.read1(size)

    eleza readinto1(self, b):
        rudisha self.reader.readinto1(b)

    eleza readable(self):
        rudisha self.reader.readable()

    eleza writable(self):
        rudisha self.writer.writable()

    eleza flush(self):
        rudisha self.writer.flush()

    eleza close(self):
        jaribu:
            self.writer.close()
        mwishowe:
            self.reader.close()

    eleza isatty(self):
        rudisha self.reader.isatty() ama self.writer.isatty()

    @property
    eleza closed(self):
        rudisha self.writer.closed


kundi BufferedRandom(BufferedWriter, BufferedReader):

    """A buffered interface to random access streams.

    The constructor creates a reader na writer kila a seekable stream,
    raw, given kwenye the first argument. If the buffer_size ni omitted it
    defaults to DEFAULT_BUFFER_SIZE.
    """

    eleza __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        raw._checkSeekable()
        BufferedReader.__init__(self, raw, buffer_size)
        BufferedWriter.__init__(self, raw, buffer_size)

    eleza seek(self, pos, whence=0):
        ikiwa whence haiko kwenye valid_seek_flags:
            ashiria ValueError("invalid whence value")
        self.flush()
        ikiwa self._read_buf:
            # Undo read ahead.
            ukijumuisha self._read_lock:
                self.raw.seek(self._read_pos - len(self._read_buf), 1)
        # First do the raw seek, then empty the read buffer, so that
        # ikiwa the raw seek fails, we don't lose buffered data forever.
        pos = self.raw.seek(pos, whence)
        ukijumuisha self._read_lock:
            self._reset_read_buf()
        ikiwa pos < 0:
            ashiria OSError("seek() returned invalid position")
        rudisha pos

    eleza tell(self):
        ikiwa self._write_buf:
            rudisha BufferedWriter.tell(self)
        isipokua:
            rudisha BufferedReader.tell(self)

    eleza truncate(self, pos=Tupu):
        ikiwa pos ni Tupu:
            pos = self.tell()
        # Use seek to flush the read buffer.
        rudisha BufferedWriter.truncate(self, pos)

    eleza read(self, size=Tupu):
        ikiwa size ni Tupu:
            size = -1
        self.flush()
        rudisha BufferedReader.read(self, size)

    eleza readinto(self, b):
        self.flush()
        rudisha BufferedReader.readinto(self, b)

    eleza peek(self, size=0):
        self.flush()
        rudisha BufferedReader.peek(self, size)

    eleza read1(self, size=-1):
        self.flush()
        rudisha BufferedReader.read1(self, size)

    eleza readinto1(self, b):
        self.flush()
        rudisha BufferedReader.readinto1(self, b)

    eleza write(self, b):
        ikiwa self._read_buf:
            # Undo readahead
            ukijumuisha self._read_lock:
                self.raw.seek(self._read_pos - len(self._read_buf), 1)
                self._reset_read_buf()
        rudisha BufferedWriter.write(self, b)


kundi FileIO(RawIOBase):
    _fd = -1
    _created = Uongo
    _readable = Uongo
    _writable = Uongo
    _appending = Uongo
    _seekable = Tupu
    _closefd = Kweli

    eleza __init__(self, file, mode='r', closefd=Kweli, opener=Tupu):
        """Open a file.  The mode can be 'r' (default), 'w', 'x' ama 'a' kila reading,
        writing, exclusive creation ama appending.  The file will be created ikiwa it
        doesn't exist when opened kila writing ama appending; it will be truncated
        when opened kila writing.  A FileExistsError will be raised ikiwa it already
        exists when opened kila creating. Opening a file kila creating implies
        writing so this mode behaves kwenye a similar way to 'w'. Add a '+' to the mode
        to allow simultaneous reading na writing. A custom opener can be used by
        pitaing a callable kama *opener*. The underlying file descriptor kila the file
        object ni then obtained by calling opener ukijumuisha (*name*, *flags*).
        *opener* must rudisha an open file descriptor (pitaing os.open kama *opener*
        results kwenye functionality similar to pitaing Tupu).
        """
        ikiwa self._fd >= 0:
            # Have to close the existing file first.
            jaribu:
                ikiwa self._closefd:
                    os.close(self._fd)
            mwishowe:
                self._fd = -1

        ikiwa isinstance(file, float):
            ashiria TypeError('integer argument expected, got float')
        ikiwa isinstance(file, int):
            fd = file
            ikiwa fd < 0:
                ashiria ValueError('negative file descriptor')
        isipokua:
            fd = -1

        ikiwa sio isinstance(mode, str):
            ashiria TypeError('invalid mode: %s' % (mode,))
        ikiwa sio set(mode) <= set('xrwab+'):
            ashiria ValueError('invalid mode: %s' % (mode,))
        ikiwa sum(c kwenye 'rwax' kila c kwenye mode) != 1 ama mode.count('+') > 1:
            ashiria ValueError('Must have exactly one of create/read/write/append '
                             'mode na at most one plus')

        ikiwa 'x' kwenye mode:
            self._created = Kweli
            self._writable = Kweli
            flags = os.O_EXCL | os.O_CREAT
        lasivyo 'r' kwenye mode:
            self._readable = Kweli
            flags = 0
        lasivyo 'w' kwenye mode:
            self._writable = Kweli
            flags = os.O_CREAT | os.O_TRUNC
        lasivyo 'a' kwenye mode:
            self._writable = Kweli
            self._appending = Kweli
            flags = os.O_APPEND | os.O_CREAT

        ikiwa '+' kwenye mode:
            self._readable = Kweli
            self._writable = Kweli

        ikiwa self._readable na self._writable:
            flags |= os.O_RDWR
        lasivyo self._readable:
            flags |= os.O_RDONLY
        isipokua:
            flags |= os.O_WRONLY

        flags |= getattr(os, 'O_BINARY', 0)

        noinherit_flag = (getattr(os, 'O_NOINHERIT', 0) ama
                          getattr(os, 'O_CLOEXEC', 0))
        flags |= noinherit_flag

        owned_fd = Tupu
        jaribu:
            ikiwa fd < 0:
                ikiwa sio closefd:
                    ashiria ValueError('Cannot use closefd=Uongo ukijumuisha file name')
                ikiwa opener ni Tupu:
                    fd = os.open(file, flags, 0o666)
                isipokua:
                    fd = opener(file, flags)
                    ikiwa sio isinstance(fd, int):
                        ashiria TypeError('expected integer kutoka opener')
                    ikiwa fd < 0:
                        ashiria OSError('Negative file descriptor')
                owned_fd = fd
                ikiwa sio noinherit_flag:
                    os.set_inheritable(fd, Uongo)

            self._closefd = closefd
            fdfstat = os.fstat(fd)
            jaribu:
                ikiwa stat.S_ISDIR(fdfstat.st_mode):
                    ashiria IsADirectoryError(errno.EISDIR,
                                            os.strerror(errno.EISDIR), file)
            tatizo AttributeError:
                # Ignore the AttribueError ikiwa stat.S_ISDIR ama errno.EISDIR
                # don't exist.
                pita
            self._blksize = getattr(fdfstat, 'st_blksize', 0)
            ikiwa self._blksize <= 1:
                self._blksize = DEFAULT_BUFFER_SIZE

            ikiwa _setmode:
                # don't translate newlines (\r\n <=> \n)
                _setmode(fd, os.O_BINARY)

            self.name = file
            ikiwa self._appending:
                # For consistent behaviour, we explicitly seek to the
                # end of file (otherwise, it might be done only on the
                # first write()).
                os.lseek(fd, 0, SEEK_END)
        tatizo:
            ikiwa owned_fd ni sio Tupu:
                os.close(owned_fd)
            raise
        self._fd = fd

    eleza __del__(self):
        ikiwa self._fd >= 0 na self._closefd na sio self.closed:
            agiza warnings
            warnings.warn('unclosed file %r' % (self,), ResourceWarning,
                          stacklevel=2, source=self)
            self.close()

    eleza __getstate__(self):
        ashiria TypeError(f"cannot pickle {self.__class__.__name__!r} object")

    eleza __repr__(self):
        class_name = '%s.%s' % (self.__class__.__module__,
                                self.__class__.__qualname__)
        ikiwa self.closed:
            rudisha '<%s [closed]>' % class_name
        jaribu:
            name = self.name
        tatizo AttributeError:
            rudisha ('<%s fd=%d mode=%r closefd=%r>' %
                    (class_name, self._fd, self.mode, self._closefd))
        isipokua:
            rudisha ('<%s name=%r mode=%r closefd=%r>' %
                    (class_name, name, self.mode, self._closefd))

    eleza _checkReadable(self):
        ikiwa sio self._readable:
            ashiria UnsupportedOperation('File sio open kila reading')

    eleza _checkWritable(self, msg=Tupu):
        ikiwa sio self._writable:
            ashiria UnsupportedOperation('File sio open kila writing')

    eleza read(self, size=Tupu):
        """Read at most size bytes, returned kama bytes.

        Only makes one system call, so less data may be returned than requested
        In non-blocking mode, returns Tupu ikiwa no data ni available.
        Return an empty bytes object at EOF.
        """
        self._checkClosed()
        self._checkReadable()
        ikiwa size ni Tupu ama size < 0:
            rudisha self.readall()
        jaribu:
            rudisha os.read(self._fd, size)
        tatizo BlockingIOError:
            rudisha Tupu

    eleza readall(self):
        """Read all data kutoka the file, returned kama bytes.

        In non-blocking mode, returns kama much kama ni immediately available,
        ama Tupu ikiwa no data ni available.  Return an empty bytes object at EOF.
        """
        self._checkClosed()
        self._checkReadable()
        bufsize = DEFAULT_BUFFER_SIZE
        jaribu:
            pos = os.lseek(self._fd, 0, SEEK_CUR)
            end = os.fstat(self._fd).st_size
            ikiwa end >= pos:
                bufsize = end - pos + 1
        tatizo OSError:
            pita

        result = bytearray()
        wakati Kweli:
            ikiwa len(result) >= bufsize:
                bufsize = len(result)
                bufsize += max(bufsize, DEFAULT_BUFFER_SIZE)
            n = bufsize - len(result)
            jaribu:
                chunk = os.read(self._fd, n)
            tatizo BlockingIOError:
                ikiwa result:
                    koma
                rudisha Tupu
            ikiwa sio chunk: # reached the end of the file
                koma
            result += chunk

        rudisha bytes(result)

    eleza readinto(self, b):
        """Same kama RawIOBase.readinto()."""
        m = memoryview(b).cast('B')
        data = self.read(len(m))
        n = len(data)
        m[:n] = data
        rudisha n

    eleza write(self, b):
        """Write bytes b to file, rudisha number written.

        Only makes one system call, so sio all of the data may be written.
        The number of bytes actually written ni returned.  In non-blocking mode,
        returns Tupu ikiwa the write would block.
        """
        self._checkClosed()
        self._checkWritable()
        jaribu:
            rudisha os.write(self._fd, b)
        tatizo BlockingIOError:
            rudisha Tupu

    eleza seek(self, pos, whence=SEEK_SET):
        """Move to new file position.

        Argument offset ni a byte count.  Optional argument whence defaults to
        SEEK_SET ama 0 (offset kutoka start of file, offset should be >= 0); other values
        are SEEK_CUR ama 1 (move relative to current position, positive ama negative),
        na SEEK_END ama 2 (move relative to end of file, usually negative, although
        many platforms allow seeking beyond the end of a file).

        Note that sio all file objects are seekable.
        """
        ikiwa isinstance(pos, float):
            ashiria TypeError('an integer ni required')
        self._checkClosed()
        rudisha os.lseek(self._fd, pos, whence)

    eleza tell(self):
        """tell() -> int.  Current file position.

        Can ashiria OSError kila non seekable files."""
        self._checkClosed()
        rudisha os.lseek(self._fd, 0, SEEK_CUR)

    eleza truncate(self, size=Tupu):
        """Truncate the file to at most size bytes.

        Size defaults to the current file position, kama returned by tell().
        The current file position ni changed to the value of size.
        """
        self._checkClosed()
        self._checkWritable()
        ikiwa size ni Tupu:
            size = self.tell()
        os.ftruncate(self._fd, size)
        rudisha size

    eleza close(self):
        """Close the file.

        A closed file cannot be used kila further I/O operations.  close() may be
        called more than once without error.
        """
        ikiwa sio self.closed:
            jaribu:
                ikiwa self._closefd:
                    os.close(self._fd)
            mwishowe:
                super().close()

    eleza seekable(self):
        """Kweli ikiwa file supports random-access."""
        self._checkClosed()
        ikiwa self._seekable ni Tupu:
            jaribu:
                self.tell()
            tatizo OSError:
                self._seekable = Uongo
            isipokua:
                self._seekable = Kweli
        rudisha self._seekable

    eleza readable(self):
        """Kweli ikiwa file was opened kwenye a read mode."""
        self._checkClosed()
        rudisha self._readable

    eleza writable(self):
        """Kweli ikiwa file was opened kwenye a write mode."""
        self._checkClosed()
        rudisha self._writable

    eleza fileno(self):
        """Return the underlying file descriptor (an integer)."""
        self._checkClosed()
        rudisha self._fd

    eleza isatty(self):
        """Kweli ikiwa the file ni connected to a TTY device."""
        self._checkClosed()
        rudisha os.isatty(self._fd)

    @property
    eleza closefd(self):
        """Kweli ikiwa the file descriptor will be closed by close()."""
        rudisha self._closefd

    @property
    eleza mode(self):
        """String giving the file mode"""
        ikiwa self._created:
            ikiwa self._readable:
                rudisha 'xb+'
            isipokua:
                rudisha 'xb'
        lasivyo self._appending:
            ikiwa self._readable:
                rudisha 'ab+'
            isipokua:
                rudisha 'ab'
        lasivyo self._readable:
            ikiwa self._writable:
                rudisha 'rb+'
            isipokua:
                rudisha 'rb'
        isipokua:
            rudisha 'wb'


kundi TextIOBase(IOBase):

    """Base kundi kila text I/O.

    This kundi provides a character na line based interface to stream
    I/O. There ni no public constructor.
    """

    eleza read(self, size=-1):
        """Read at most size characters kutoka stream, where size ni an int.

        Read kutoka underlying buffer until we have size characters ama we hit EOF.
        If size ni negative ama omitted, read until EOF.

        Returns a string.
        """
        self._unsupported("read")

    eleza write(self, s):
        """Write string s to stream na returning an int."""
        self._unsupported("write")

    eleza truncate(self, pos=Tupu):
        """Truncate size to pos, where pos ni an int."""
        self._unsupported("truncate")

    eleza readline(self):
        """Read until newline ama EOF.

        Returns an empty string ikiwa EOF ni hit immediately.
        """
        self._unsupported("readline")

    eleza detach(self):
        """
        Separate the underlying buffer kutoka the TextIOBase na rudisha it.

        After the underlying buffer has been detached, the TextIO ni kwenye an
        unusable state.
        """
        self._unsupported("detach")

    @property
    eleza encoding(self):
        """Subclasses should override."""
        rudisha Tupu

    @property
    eleza newlines(self):
        """Line endings translated so far.

        Only line endings translated during reading are considered.

        Subclasses should override.
        """
        rudisha Tupu

    @property
    eleza errors(self):
        """Error setting of the decoder ama encoder.

        Subclasses should override."""
        rudisha Tupu

io.TextIOBase.register(TextIOBase)


kundi IncrementalNewlineDecoder(codecs.IncrementalDecoder):
    r"""Codec used when reading a file kwenye universal newlines mode.  It wraps
    another incremental decoder, translating \r\n na \r into \n.  It also
    records the types of newlines encountered.  When used with
    translate=Uongo, it ensures that the newline sequence ni returned in
    one piece.
    """
    eleza __init__(self, decoder, translate, errors='strict'):
        codecs.IncrementalDecoder.__init__(self, errors=errors)
        self.translate = translate
        self.decoder = decoder
        self.seennl = 0
        self.pendingcr = Uongo

    eleza decode(self, input, final=Uongo):
        # decode input (ukijumuisha the eventual \r kutoka a previous pita)
        ikiwa self.decoder ni Tupu:
            output = input
        isipokua:
            output = self.decoder.decode(input, final=final)
        ikiwa self.pendingcr na (output ama final):
            output = "\r" + output
            self.pendingcr = Uongo

        # retain last \r even when sio translating data:
        # then readline() ni sure to get \r\n kwenye one pita
        ikiwa output.endswith("\r") na sio final:
            output = output[:-1]
            self.pendingcr = Kweli

        # Record which newlines are read
        crlf = output.count('\r\n')
        cr = output.count('\r') - crlf
        lf = output.count('\n') - crlf
        self.seennl |= (lf na self._LF) | (cr na self._CR) \
                    | (crlf na self._CRLF)

        ikiwa self.translate:
            ikiwa crlf:
                output = output.replace("\r\n", "\n")
            ikiwa cr:
                output = output.replace("\r", "\n")

        rudisha output

    eleza getstate(self):
        ikiwa self.decoder ni Tupu:
            buf = b""
            flag = 0
        isipokua:
            buf, flag = self.decoder.getstate()
        flag <<= 1
        ikiwa self.pendingcr:
            flag |= 1
        rudisha buf, flag

    eleza setstate(self, state):
        buf, flag = state
        self.pendingcr = bool(flag & 1)
        ikiwa self.decoder ni sio Tupu:
            self.decoder.setstate((buf, flag >> 1))

    eleza reset(self):
        self.seennl = 0
        self.pendingcr = Uongo
        ikiwa self.decoder ni sio Tupu:
            self.decoder.reset()

    _LF = 1
    _CR = 2
    _CRLF = 4

    @property
    eleza newlines(self):
        rudisha (Tupu,
                "\n",
                "\r",
                ("\r", "\n"),
                "\r\n",
                ("\n", "\r\n"),
                ("\r", "\r\n"),
                ("\r", "\n", "\r\n")
               )[self.seennl]


kundi TextIOWrapper(TextIOBase):

    r"""Character na line based layer over a BufferedIOBase object, buffer.

    encoding gives the name of the encoding that the stream will be
    decoded ama encoded with. It defaults to locale.getpreferredencoding(Uongo).

    errors determines the strictness of encoding na decoding (see the
    codecs.register) na defaults to "strict".

    newline can be Tupu, '', '\n', '\r', ama '\r\n'.  It controls the
    handling of line endings. If it ni Tupu, universal newlines is
    enabled.  With this enabled, on input, the lines endings '\n', '\r',
    ama '\r\n' are translated to '\n' before being returned to the
    caller. Conversely, on output, '\n' ni translated to the system
    default line separator, os.linesep. If newline ni any other of its
    legal values, that newline becomes the newline when the file ni read
    na it ni returned untranslated. On output, '\n' ni converted to the
    newline.

    If line_buffering ni Kweli, a call to flush ni implied when a call to
    write contains a newline character.
    """

    _CHUNK_SIZE = 2048

    # Initialize _buffer kama soon kama possible since it's used by __del__()
    # which calls close()
    _buffer = Tupu

    # The write_through argument has no effect here since this
    # implementation always writes through.  The argument ni present only
    # so that the signature can match the signature of the C version.
    eleza __init__(self, buffer, encoding=Tupu, errors=Tupu, newline=Tupu,
                 line_buffering=Uongo, write_through=Uongo):
        self._check_newline(newline)
        ikiwa encoding ni Tupu:
            jaribu:
                encoding = os.device_encoding(buffer.fileno())
            tatizo (AttributeError, UnsupportedOperation):
                pita
            ikiwa encoding ni Tupu:
                jaribu:
                    agiza locale
                tatizo ImportError:
                    # Importing locale may fail ikiwa Python ni being built
                    encoding = "ascii"
                isipokua:
                    encoding = locale.getpreferredencoding(Uongo)

        ikiwa sio isinstance(encoding, str):
            ashiria ValueError("invalid encoding: %r" % encoding)

        ikiwa sio codecs.lookup(encoding)._is_text_encoding:
            msg = ("%r ni sio a text encoding; "
                   "use codecs.open() to handle arbitrary codecs")
            ashiria LookupError(msg % encoding)

        ikiwa errors ni Tupu:
            errors = "strict"
        isipokua:
            ikiwa sio isinstance(errors, str):
                ashiria ValueError("invalid errors: %r" % errors)

        self._buffer = buffer
        self._decoded_chars = ''  # buffer kila text returned kutoka decoder
        self._decoded_chars_used = 0  # offset into _decoded_chars kila read()
        self._snapshot = Tupu  # info kila reconstructing decoder state
        self._seekable = self._telling = self.buffer.seekable()
        self._has_read1 = hasattr(self.buffer, 'read1')
        self._configure(encoding, errors, newline,
                        line_buffering, write_through)

    eleza _check_newline(self, newline):
        ikiwa newline ni sio Tupu na sio isinstance(newline, str):
            ashiria TypeError("illegal newline type: %r" % (type(newline),))
        ikiwa newline haiko kwenye (Tupu, "", "\n", "\r", "\r\n"):
            ashiria ValueError("illegal newline value: %r" % (newline,))

    eleza _configure(self, encoding=Tupu, errors=Tupu, newline=Tupu,
                   line_buffering=Uongo, write_through=Uongo):
        self._encoding = encoding
        self._errors = errors
        self._encoder = Tupu
        self._decoder = Tupu
        self._b2cratio = 0.0

        self._readuniversal = sio newline
        self._readtranslate = newline ni Tupu
        self._readnl = newline
        self._writetranslate = newline != ''
        self._writenl = newline ama os.linesep

        self._line_buffering = line_buffering
        self._write_through = write_through

        # don't write a BOM kwenye the middle of a file
        ikiwa self._seekable na self.writable():
            position = self.buffer.tell()
            ikiwa position != 0:
                jaribu:
                    self._get_encoder().setstate(0)
                tatizo LookupError:
                    # Sometimes the encoder doesn't exist
                    pita

    # self._snapshot ni either Tupu, ama a tuple (dec_flags, next_input)
    # where dec_flags ni the second (integer) item of the decoder state
    # na next_input ni the chunk of input bytes that comes next after the
    # snapshot point.  We use this to reconstruct decoder states kwenye tell().

    # Naming convention:
    #   - "bytes_..." kila integer variables that count input bytes
    #   - "chars_..." kila integer variables that count decoded characters

    eleza __repr__(self):
        result = "<{}.{}".format(self.__class__.__module__,
                                 self.__class__.__qualname__)
        jaribu:
            name = self.name
        tatizo AttributeError:
            pita
        isipokua:
            result += " name={0!r}".format(name)
        jaribu:
            mode = self.mode
        tatizo AttributeError:
            pita
        isipokua:
            result += " mode={0!r}".format(mode)
        rudisha result + " encoding={0!r}>".format(self.encoding)

    @property
    eleza encoding(self):
        rudisha self._encoding

    @property
    eleza errors(self):
        rudisha self._errors

    @property
    eleza line_buffering(self):
        rudisha self._line_buffering

    @property
    eleza write_through(self):
        rudisha self._write_through

    @property
    eleza buffer(self):
        rudisha self._buffer

    eleza reconfigure(self, *,
                    encoding=Tupu, errors=Tupu, newline=Ellipsis,
                    line_buffering=Tupu, write_through=Tupu):
        """Reconfigure the text stream ukijumuisha new parameters.

        This also flushes the stream.
        """
        ikiwa (self._decoder ni sio Tupu
                na (encoding ni sio Tupu ama errors ni sio Tupu
                     ama newline ni sio Ellipsis)):
            ashiria UnsupportedOperation(
                "It ni sio possible to set the encoding ama newline of stream "
                "after the first read")

        ikiwa errors ni Tupu:
            ikiwa encoding ni Tupu:
                errors = self._errors
            isipokua:
                errors = 'strict'
        lasivyo sio isinstance(errors, str):
            ashiria TypeError("invalid errors: %r" % errors)

        ikiwa encoding ni Tupu:
            encoding = self._encoding
        isipokua:
            ikiwa sio isinstance(encoding, str):
                ashiria TypeError("invalid encoding: %r" % encoding)

        ikiwa newline ni Ellipsis:
            newline = self._readnl
        self._check_newline(newline)

        ikiwa line_buffering ni Tupu:
            line_buffering = self.line_buffering
        ikiwa write_through ni Tupu:
            write_through = self.write_through

        self.flush()
        self._configure(encoding, errors, newline,
                        line_buffering, write_through)

    eleza seekable(self):
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file.")
        rudisha self._seekable

    eleza readable(self):
        rudisha self.buffer.readable()

    eleza writable(self):
        rudisha self.buffer.writable()

    eleza flush(self):
        self.buffer.flush()
        self._telling = self._seekable

    eleza close(self):
        ikiwa self.buffer ni sio Tupu na sio self.closed:
            jaribu:
                self.flush()
            mwishowe:
                self.buffer.close()

    @property
    eleza closed(self):
        rudisha self.buffer.closed

    @property
    eleza name(self):
        rudisha self.buffer.name

    eleza fileno(self):
        rudisha self.buffer.fileno()

    eleza isatty(self):
        rudisha self.buffer.isatty()

    eleza write(self, s):
        'Write data, where s ni a str'
        ikiwa self.closed:
            ashiria ValueError("write to closed file")
        ikiwa sio isinstance(s, str):
            ashiria TypeError("can't write %s to text stream" %
                            s.__class__.__name__)
        length = len(s)
        haslf = (self._writetranslate ama self._line_buffering) na "\n" kwenye s
        ikiwa haslf na self._writetranslate na self._writenl != "\n":
            s = s.replace("\n", self._writenl)
        encoder = self._encoder ama self._get_encoder()
        # XXX What ikiwa we were just reading?
        b = encoder.encode(s)
        self.buffer.write(b)
        ikiwa self._line_buffering na (haslf ama "\r" kwenye s):
            self.flush()
        self._set_decoded_chars('')
        self._snapshot = Tupu
        ikiwa self._decoder:
            self._decoder.reset()
        rudisha length

    eleza _get_encoder(self):
        make_encoder = codecs.getincrementalencoder(self._encoding)
        self._encoder = make_encoder(self._errors)
        rudisha self._encoder

    eleza _get_decoder(self):
        make_decoder = codecs.getincrementaldecoder(self._encoding)
        decoder = make_decoder(self._errors)
        ikiwa self._readuniversal:
            decoder = IncrementalNewlineDecoder(decoder, self._readtranslate)
        self._decoder = decoder
        rudisha decoder

    # The following three methods implement an ADT kila _decoded_chars.
    # Text returned kutoka the decoder ni buffered here until the client
    # requests it by calling our read() ama readline() method.
    eleza _set_decoded_chars(self, chars):
        """Set the _decoded_chars buffer."""
        self._decoded_chars = chars
        self._decoded_chars_used = 0

    eleza _get_decoded_chars(self, n=Tupu):
        """Advance into the _decoded_chars buffer."""
        offset = self._decoded_chars_used
        ikiwa n ni Tupu:
            chars = self._decoded_chars[offset:]
        isipokua:
            chars = self._decoded_chars[offset:offset + n]
        self._decoded_chars_used += len(chars)
        rudisha chars

    eleza _rewind_decoded_chars(self, n):
        """Rewind the _decoded_chars buffer."""
        ikiwa self._decoded_chars_used < n:
            ashiria AssertionError("rewind decoded_chars out of bounds")
        self._decoded_chars_used -= n

    eleza _read_chunk(self):
        """
        Read na decode the next chunk of data kutoka the BufferedReader.
        """

        # The rudisha value ni Kweli unless EOF was reached.  The decoded
        # string ni placed kwenye self._decoded_chars (replacing its previous
        # value).  The entire input chunk ni sent to the decoder, though
        # some of it may remain buffered kwenye the decoder, yet to be
        # converted.

        ikiwa self._decoder ni Tupu:
            ashiria ValueError("no decoder")

        ikiwa self._telling:
            # To prepare kila tell(), we need to snapshot a point kwenye the
            # file where the decoder's input buffer ni empty.

            dec_buffer, dec_flags = self._decoder.getstate()
            # Given this, we know there was a valid snapshot point
            # len(dec_buffer) bytes ago ukijumuisha decoder state (b'', dec_flags).

        # Read a chunk, decode it, na put the result kwenye self._decoded_chars.
        ikiwa self._has_read1:
            input_chunk = self.buffer.read1(self._CHUNK_SIZE)
        isipokua:
            input_chunk = self.buffer.read(self._CHUNK_SIZE)
        eof = sio input_chunk
        decoded_chars = self._decoder.decode(input_chunk, eof)
        self._set_decoded_chars(decoded_chars)
        ikiwa decoded_chars:
            self._b2cratio = len(input_chunk) / len(self._decoded_chars)
        isipokua:
            self._b2cratio = 0.0

        ikiwa self._telling:
            # At the snapshot point, len(dec_buffer) bytes before the read,
            # the next input to be decoded ni dec_buffer + input_chunk.
            self._snapshot = (dec_flags, dec_buffer + input_chunk)

        rudisha sio eof

    eleza _pack_cookie(self, position, dec_flags=0,
                           bytes_to_feed=0, need_eof=0, chars_to_skip=0):
        # The meaning of a tell() cookie is: seek to position, set the
        # decoder flags to dec_flags, read bytes_to_feed bytes, feed them
        # into the decoder ukijumuisha need_eof kama the EOF flag, then skip
        # chars_to_skip characters of the decoded result.  For most simple
        # decoders, tell() will often just give a byte offset kwenye the file.
        rudisha (position | (dec_flags<<64) | (bytes_to_feed<<128) |
               (chars_to_skip<<192) | bool(need_eof)<<256)

    eleza _unpack_cookie(self, bigint):
        rest, position = divmod(bigint, 1<<64)
        rest, dec_flags = divmod(rest, 1<<64)
        rest, bytes_to_feed = divmod(rest, 1<<64)
        need_eof, chars_to_skip = divmod(rest, 1<<64)
        rudisha position, dec_flags, bytes_to_feed, need_eof, chars_to_skip

    eleza tell(self):
        ikiwa sio self._seekable:
            ashiria UnsupportedOperation("underlying stream ni sio seekable")
        ikiwa sio self._telling:
            ashiria OSError("telling position disabled by next() call")
        self.flush()
        position = self.buffer.tell()
        decoder = self._decoder
        ikiwa decoder ni Tupu ama self._snapshot ni Tupu:
            ikiwa self._decoded_chars:
                # This should never happen.
                ashiria AssertionError("pending decoded text")
            rudisha position

        # Skip backward to the snapshot point (see _read_chunk).
        dec_flags, next_input = self._snapshot
        position -= len(next_input)

        # How many decoded characters have been used up since the snapshot?
        chars_to_skip = self._decoded_chars_used
        ikiwa chars_to_skip == 0:
            # We haven't moved kutoka the snapshot point.
            rudisha self._pack_cookie(position, dec_flags)

        # Starting kutoka the snapshot position, we will walk the decoder
        # forward until it gives us enough decoded characters.
        saved_state = decoder.getstate()
        jaribu:
            # Fast search kila an acceptable start point, close to our
            # current pos.
            # Rationale: calling decoder.decode() has a large overhead
            # regardless of chunk size; we want the number of such calls to
            # be O(1) kwenye most situations (common decoders, sensible input).
            # Actually, it will be exactly 1 kila fixed-size codecs (all
            # 8-bit codecs, also UTF-16 na UTF-32).
            skip_bytes = int(self._b2cratio * chars_to_skip)
            skip_back = 1
            assert skip_bytes <= len(next_input)
            wakati skip_bytes > 0:
                decoder.setstate((b'', dec_flags))
                # Decode up to temptative start point
                n = len(decoder.decode(next_input[:skip_bytes]))
                ikiwa n <= chars_to_skip:
                    b, d = decoder.getstate()
                    ikiwa sio b:
                        # Before pos na no bytes buffered kwenye decoder => OK
                        dec_flags = d
                        chars_to_skip -= n
                        koma
                    # Skip back by buffered amount na reset heuristic
                    skip_bytes -= len(b)
                    skip_back = 1
                isipokua:
                    # We're too far ahead, skip back a bit
                    skip_bytes -= skip_back
                    skip_back = skip_back * 2
            isipokua:
                skip_bytes = 0
                decoder.setstate((b'', dec_flags))

            # Note our initial start point.
            start_pos = position + skip_bytes
            start_flags = dec_flags
            ikiwa chars_to_skip == 0:
                # We haven't moved kutoka the start point.
                rudisha self._pack_cookie(start_pos, start_flags)

            # Feed the decoder one byte at a time.  As we go, note the
            # nearest "safe start point" before the current location
            # (a point where the decoder has nothing buffered, so seek()
            # can safely start kutoka there na advance to this location).
            bytes_fed = 0
            need_eof = 0
            # Chars decoded since `start_pos`
            chars_decoded = 0
            kila i kwenye range(skip_bytes, len(next_input)):
                bytes_fed += 1
                chars_decoded += len(decoder.decode(next_input[i:i+1]))
                dec_buffer, dec_flags = decoder.getstate()
                ikiwa sio dec_buffer na chars_decoded <= chars_to_skip:
                    # Decoder buffer ni empty, so this ni a safe start point.
                    start_pos += bytes_fed
                    chars_to_skip -= chars_decoded
                    start_flags, bytes_fed, chars_decoded = dec_flags, 0, 0
                ikiwa chars_decoded >= chars_to_skip:
                    koma
            isipokua:
                # We didn't get enough decoded data; signal EOF to get more.
                chars_decoded += len(decoder.decode(b'', final=Kweli))
                need_eof = 1
                ikiwa chars_decoded < chars_to_skip:
                    ashiria OSError("can't reconstruct logical file position")

            # The returned cookie corresponds to the last safe start point.
            rudisha self._pack_cookie(
                start_pos, start_flags, bytes_fed, need_eof, chars_to_skip)
        mwishowe:
            decoder.setstate(saved_state)

    eleza truncate(self, pos=Tupu):
        self.flush()
        ikiwa pos ni Tupu:
            pos = self.tell()
        rudisha self.buffer.truncate(pos)

    eleza detach(self):
        ikiwa self.buffer ni Tupu:
            ashiria ValueError("buffer ni already detached")
        self.flush()
        buffer = self._buffer
        self._buffer = Tupu
        rudisha buffer

    eleza seek(self, cookie, whence=0):
        eleza _reset_encoder(position):
            """Reset the encoder (merely useful kila proper BOM handling)"""
            jaribu:
                encoder = self._encoder ama self._get_encoder()
            tatizo LookupError:
                # Sometimes the encoder doesn't exist
                pita
            isipokua:
                ikiwa position != 0:
                    encoder.setstate(0)
                isipokua:
                    encoder.reset()

        ikiwa self.closed:
            ashiria ValueError("tell on closed file")
        ikiwa sio self._seekable:
            ashiria UnsupportedOperation("underlying stream ni sio seekable")
        ikiwa whence == SEEK_CUR:
            ikiwa cookie != 0:
                ashiria UnsupportedOperation("can't do nonzero cur-relative seeks")
            # Seeking to the current position should attempt to
            # sync the underlying buffer ukijumuisha the current position.
            whence = 0
            cookie = self.tell()
        lasivyo whence == SEEK_END:
            ikiwa cookie != 0:
                ashiria UnsupportedOperation("can't do nonzero end-relative seeks")
            self.flush()
            position = self.buffer.seek(0, whence)
            self._set_decoded_chars('')
            self._snapshot = Tupu
            ikiwa self._decoder:
                self._decoder.reset()
            _reset_encoder(position)
            rudisha position
        ikiwa whence != 0:
            ashiria ValueError("unsupported whence (%r)" % (whence,))
        ikiwa cookie < 0:
            ashiria ValueError("negative seek position %r" % (cookie,))
        self.flush()

        # The strategy of seek() ni to go back to the safe start point
        # na replay the effect of read(chars_to_skip) kutoka there.
        start_pos, dec_flags, bytes_to_feed, need_eof, chars_to_skip = \
            self._unpack_cookie(cookie)

        # Seek back to the safe start point.
        self.buffer.seek(start_pos)
        self._set_decoded_chars('')
        self._snapshot = Tupu

        # Restore the decoder to its state kutoka the safe start point.
        ikiwa cookie == 0 na self._decoder:
            self._decoder.reset()
        lasivyo self._decoder ama dec_flags ama chars_to_skip:
            self._decoder = self._decoder ama self._get_decoder()
            self._decoder.setstate((b'', dec_flags))
            self._snapshot = (dec_flags, b'')

        ikiwa chars_to_skip:
            # Just like _read_chunk, feed the decoder na save a snapshot.
            input_chunk = self.buffer.read(bytes_to_feed)
            self._set_decoded_chars(
                self._decoder.decode(input_chunk, need_eof))
            self._snapshot = (dec_flags, input_chunk)

            # Skip chars_to_skip of the decoded characters.
            ikiwa len(self._decoded_chars) < chars_to_skip:
                ashiria OSError("can't restore logical file position")
            self._decoded_chars_used = chars_to_skip

        _reset_encoder(cookie)
        rudisha cookie

    eleza read(self, size=Tupu):
        self._checkReadable()
        ikiwa size ni Tupu:
            size = -1
        isipokua:
            jaribu:
                size_index = size.__index__
            tatizo AttributeError:
                ashiria TypeError(f"{size!r} ni sio an integer")
            isipokua:
                size = size_index()
        decoder = self._decoder ama self._get_decoder()
        ikiwa size < 0:
            # Read everything.
            result = (self._get_decoded_chars() +
                      decoder.decode(self.buffer.read(), final=Kweli))
            self._set_decoded_chars('')
            self._snapshot = Tupu
            rudisha result
        isipokua:
            # Keep reading chunks until we have size characters to return.
            eof = Uongo
            result = self._get_decoded_chars(size)
            wakati len(result) < size na sio eof:
                eof = sio self._read_chunk()
                result += self._get_decoded_chars(size - len(result))
            rudisha result

    eleza __next__(self):
        self._telling = Uongo
        line = self.readline()
        ikiwa sio line:
            self._snapshot = Tupu
            self._telling = self._seekable
            ashiria StopIteration
        rudisha line

    eleza readline(self, size=Tupu):
        ikiwa self.closed:
            ashiria ValueError("read kutoka closed file")
        ikiwa size ni Tupu:
            size = -1
        isipokua:
            jaribu:
                size_index = size.__index__
            tatizo AttributeError:
                ashiria TypeError(f"{size!r} ni sio an integer")
            isipokua:
                size = size_index()

        # Grab all the decoded text (we will rewind any extra bits later).
        line = self._get_decoded_chars()

        start = 0
        # Make the decoder ikiwa it doesn't already exist.
        ikiwa sio self._decoder:
            self._get_decoder()

        pos = endpos = Tupu
        wakati Kweli:
            ikiwa self._readtranslate:
                # Newlines are already translated, only search kila \n
                pos = line.find('\n', start)
                ikiwa pos >= 0:
                    endpos = pos + 1
                    koma
                isipokua:
                    start = len(line)

            lasivyo self._readuniversal:
                # Universal newline search. Find any of \r, \r\n, \n
                # The decoder ensures that \r\n are sio split kwenye two pieces

                # In C we'd look kila these kwenye parallel of course.
                nlpos = line.find("\n", start)
                crpos = line.find("\r", start)
                ikiwa crpos == -1:
                    ikiwa nlpos == -1:
                        # Nothing found
                        start = len(line)
                    isipokua:
                        # Found \n
                        endpos = nlpos + 1
                        koma
                lasivyo nlpos == -1:
                    # Found lone \r
                    endpos = crpos + 1
                    koma
                lasivyo nlpos < crpos:
                    # Found \n
                    endpos = nlpos + 1
                    koma
                lasivyo nlpos == crpos + 1:
                    # Found \r\n
                    endpos = crpos + 2
                    koma
                isipokua:
                    # Found \r
                    endpos = crpos + 1
                    koma
            isipokua:
                # non-universal
                pos = line.find(self._readnl)
                ikiwa pos >= 0:
                    endpos = pos + len(self._readnl)
                    koma

            ikiwa size >= 0 na len(line) >= size:
                endpos = size  # reached length size
                koma

            # No line ending seen yet - get more data'
            wakati self._read_chunk():
                ikiwa self._decoded_chars:
                    koma
            ikiwa self._decoded_chars:
                line += self._get_decoded_chars()
            isipokua:
                # end of file
                self._set_decoded_chars('')
                self._snapshot = Tupu
                rudisha line

        ikiwa size >= 0 na endpos > size:
            endpos = size  # don't exceed size

        # Rewind _decoded_chars to just after the line ending we found.
        self._rewind_decoded_chars(len(line) - endpos)
        rudisha line[:endpos]

    @property
    eleza newlines(self):
        rudisha self._decoder.newlines ikiwa self._decoder isipokua Tupu


kundi StringIO(TextIOWrapper):
    """Text I/O implementation using an in-memory buffer.

    The initial_value argument sets the value of object.  The newline
    argument ni like the one of TextIOWrapper's constructor.
    """

    eleza __init__(self, initial_value="", newline="\n"):
        super(StringIO, self).__init__(BytesIO(),
                                       encoding="utf-8",
                                       errors="surrogatepita",
                                       newline=newline)
        # Issue #5645: make universal newlines semantics the same kama kwenye the
        # C version, even under Windows.
        ikiwa newline ni Tupu:
            self._writetranslate = Uongo
        ikiwa initial_value ni sio Tupu:
            ikiwa sio isinstance(initial_value, str):
                ashiria TypeError("initial_value must be str ama Tupu, sio {0}"
                                .format(type(initial_value).__name__))
            self.write(initial_value)
            self.seek(0)

    eleza getvalue(self):
        self.flush()
        decoder = self._decoder ama self._get_decoder()
        old_state = decoder.getstate()
        decoder.reset()
        jaribu:
            rudisha decoder.decode(self.buffer.getvalue(), final=Kweli)
        mwishowe:
            decoder.setstate(old_state)

    eleza __repr__(self):
        # TextIOWrapper tells the encoding kwenye its repr. In StringIO,
        # that's an implementation detail.
        rudisha object.__repr__(self)

    @property
    eleza errors(self):
        rudisha Tupu

    @property
    eleza encoding(self):
        rudisha Tupu

    eleza detach(self):
        # This doesn't make sense on StringIO.
        self._unsupported("detach")
