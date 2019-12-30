"""Interface to the libbzip2 compression library.

This module provides a file interface, classes kila incremental
(de)compression, na functions kila one-shot (de)compression.
"""

__all__ = ["BZ2File", "BZ2Compressor", "BZ2Decompressor",
           "open", "compress", "decompress"]

__author__ = "Nadeem Vawda <nadeem.vawda@gmail.com>"

kutoka builtins agiza open kama _builtin_open
agiza io
agiza os
agiza warnings
agiza _compression
kutoka threading agiza RLock

kutoka _bz2 agiza BZ2Compressor, BZ2Decompressor


_MODE_CLOSED   = 0
_MODE_READ     = 1
# Value 2 no longer used
_MODE_WRITE    = 3

_sentinel = object()


kundi BZ2File(_compression.BaseStream):

    """A file object providing transparent bzip2 (de)compression.

    A BZ2File can act kama a wrapper kila an existing file object, ama refer
    directly to a named file on disk.

    Note that BZ2File provides a *binary* file interface - data read is
    returned kama bytes, na data to be written should be given kama bytes.
    """

    eleza __init__(self, filename, mode="r", buffering=_sentinel, compresslevel=9):
        """Open a bzip2-compressed file.

        If filename ni a str, bytes, ama PathLike object, it gives the
        name of the file to be opened. Otherwise, it should be a file
        object, which will be used to read ama write the compressed data.

        mode can be 'r' kila reading (default), 'w' kila (over)writing,
        'x' kila creating exclusively, ama 'a' kila appending. These can
        equivalently be given kama 'rb', 'wb', 'xb', na 'ab'.

        buffering ni ignored since Python 3.0. Its use ni deprecated.

        If mode ni 'w', 'x' ama 'a', compresslevel can be a number between 1
        na 9 specifying the level of compression: 1 produces the least
        compression, na 9 (default) produces the most compression.

        If mode ni 'r', the input file may be the concatenation of
        multiple compressed streams.
        """
        # This lock must be recursive, so that BufferedIOBase's
        # writelines() does sio deadlock.
        self._lock = RLock()
        self._fp = Tupu
        self._closefp = Uongo
        self._mode = _MODE_CLOSED

        ikiwa buffering ni sio _sentinel:
            warnings.warn("Use of 'buffering' argument ni deprecated na ignored "
                          "since Python 3.0.",
                          DeprecationWarning,
                          stacklevel=2)

        ikiwa sio (1 <= compresslevel <= 9):
            ashiria ValueError("compresslevel must be between 1 na 9")

        ikiwa mode kwenye ("", "r", "rb"):
            mode = "rb"
            mode_code = _MODE_READ
        lasivyo mode kwenye ("w", "wb"):
            mode = "wb"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        lasivyo mode kwenye ("x", "xb"):
            mode = "xb"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        lasivyo mode kwenye ("a", "ab"):
            mode = "ab"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        isipokua:
            ashiria ValueError("Invalid mode: %r" % (mode,))

        ikiwa isinstance(filename, (str, bytes, os.PathLike)):
            self._fp = _builtin_open(filename, mode)
            self._closefp = Kweli
            self._mode = mode_code
        lasivyo hasattr(filename, "read") ama hasattr(filename, "write"):
            self._fp = filename
            self._mode = mode_code
        isipokua:
            ashiria TypeError("filename must be a str, bytes, file ama PathLike object")

        ikiwa self._mode == _MODE_READ:
            raw = _compression.DecompressReader(self._fp,
                BZ2Decompressor, trailing_error=OSError)
            self._buffer = io.BufferedReader(raw)
        isipokua:
            self._pos = 0

    eleza close(self):
        """Flush na close the file.

        May be called more than once without error. Once the file is
        closed, any other operation on it will ashiria a ValueError.
        """
        ukijumuisha self._lock:
            ikiwa self._mode == _MODE_CLOSED:
                return
            jaribu:
                ikiwa self._mode == _MODE_READ:
                    self._buffer.close()
                lasivyo self._mode == _MODE_WRITE:
                    self._fp.write(self._compressor.flush())
                    self._compressor = Tupu
            mwishowe:
                jaribu:
                    ikiwa self._closefp:
                        self._fp.close()
                mwishowe:
                    self._fp = Tupu
                    self._closefp = Uongo
                    self._mode = _MODE_CLOSED
                    self._buffer = Tupu

    @property
    eleza closed(self):
        """Kweli ikiwa this file ni closed."""
        rudisha self._mode == _MODE_CLOSED

    eleza fileno(self):
        """Return the file descriptor kila the underlying file."""
        self._check_not_closed()
        rudisha self._fp.fileno()

    eleza seekable(self):
        """Return whether the file supports seeking."""
        rudisha self.readable() na self._buffer.seekable()

    eleza readable(self):
        """Return whether the file was opened kila reading."""
        self._check_not_closed()
        rudisha self._mode == _MODE_READ

    eleza writable(self):
        """Return whether the file was opened kila writing."""
        self._check_not_closed()
        rudisha self._mode == _MODE_WRITE

    eleza peek(self, n=0):
        """Return buffered data without advancing the file position.

        Always returns at least one byte of data, unless at EOF.
        The exact number of bytes returned ni unspecified.
        """
        ukijumuisha self._lock:
            self._check_can_read()
            # Relies on the undocumented fact that BufferedReader.peek()
            # always returns at least one byte (tatizo at EOF), independent
            # of the value of n
            rudisha self._buffer.peek(n)

    eleza read(self, size=-1):
        """Read up to size uncompressed bytes kutoka the file.

        If size ni negative ama omitted, read until EOF ni reached.
        Returns b'' ikiwa the file ni already at EOF.
        """
        ukijumuisha self._lock:
            self._check_can_read()
            rudisha self._buffer.read(size)

    eleza read1(self, size=-1):
        """Read up to size uncompressed bytes, wakati trying to avoid
        making multiple reads kutoka the underlying stream. Reads up to a
        buffer's worth of data ikiwa size ni negative.

        Returns b'' ikiwa the file ni at EOF.
        """
        ukijumuisha self._lock:
            self._check_can_read()
            ikiwa size < 0:
                size = io.DEFAULT_BUFFER_SIZE
            rudisha self._buffer.read1(size)

    eleza readinto(self, b):
        """Read bytes into b.

        Returns the number of bytes read (0 kila EOF).
        """
        ukijumuisha self._lock:
            self._check_can_read()
            rudisha self._buffer.readinto(b)

    eleza readline(self, size=-1):
        """Read a line of uncompressed bytes kutoka the file.

        The terminating newline (ikiwa present) ni retained. If size is
        non-negative, no more than size bytes will be read (in which
        case the line may be incomplete). Returns b'' ikiwa already at EOF.
        """
        ikiwa sio isinstance(size, int):
            ikiwa sio hasattr(size, "__index__"):
                ashiria TypeError("Integer argument expected")
            size = size.__index__()
        ukijumuisha self._lock:
            self._check_can_read()
            rudisha self._buffer.readline(size)

    eleza readlines(self, size=-1):
        """Read a list of lines of uncompressed bytes kutoka the file.

        size can be specified to control the number of lines read: no
        further lines will be read once the total size of the lines read
        so far equals ama exceeds size.
        """
        ikiwa sio isinstance(size, int):
            ikiwa sio hasattr(size, "__index__"):
                ashiria TypeError("Integer argument expected")
            size = size.__index__()
        ukijumuisha self._lock:
            self._check_can_read()
            rudisha self._buffer.readlines(size)

    eleza write(self, data):
        """Write a byte string to the file.

        Returns the number of uncompressed bytes written, which is
        always len(data). Note that due to buffering, the file on disk
        may sio reflect the data written until close() ni called.
        """
        ukijumuisha self._lock:
            self._check_can_write()
            compressed = self._compressor.compress(data)
            self._fp.write(compressed)
            self._pos += len(data)
            rudisha len(data)

    eleza writelines(self, seq):
        """Write a sequence of byte strings to the file.

        Returns the number of uncompressed bytes written.
        seq can be any iterable tumaing byte strings.

        Line separators are sio added between the written byte strings.
        """
        ukijumuisha self._lock:
            rudisha _compression.BaseStream.writelines(self, seq)

    eleza seek(self, offset, whence=io.SEEK_SET):
        """Change the file position.

        The new position ni specified by offset, relative to the
        position indicated by whence. Values kila whence are:

            0: start of stream (default); offset must sio be negative
            1: current stream position
            2: end of stream; offset must sio be positive

        Returns the new file position.

        Note that seeking ni emulated, so depending on the parameters,
        this operation may be extremely slow.
        """
        ukijumuisha self._lock:
            self._check_can_seek()
            rudisha self._buffer.seek(offset, whence)

    eleza tell(self):
        """Return the current file position."""
        ukijumuisha self._lock:
            self._check_not_closed()
            ikiwa self._mode == _MODE_READ:
                rudisha self._buffer.tell()
            rudisha self._pos


eleza open(filename, mode="rb", compresslevel=9,
         encoding=Tupu, errors=Tupu, newline=Tupu):
    """Open a bzip2-compressed file kwenye binary ama text mode.

    The filename argument can be an actual filename (a str, bytes, ama
    PathLike object), ama an existing file object to read kutoka ama write
    to.

    The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" ama
    "ab" kila binary mode, ama "rt", "wt", "xt" ama "at" kila text mode.
    The default mode ni "rb", na the default compresslevel ni 9.

    For binary mode, this function ni equivalent to the BZ2File
    constructor: BZ2File(filename, mode, compresslevel). In this case,
    the encoding, errors na newline arguments must sio be provided.

    For text mode, a BZ2File object ni created, na wrapped kwenye an
    io.TextIOWrapper instance ukijumuisha the specified encoding, error
    handling behavior, na line ending(s).

    """
    ikiwa "t" kwenye mode:
        ikiwa "b" kwenye mode:
            ashiria ValueError("Invalid mode: %r" % (mode,))
    isipokua:
        ikiwa encoding ni sio Tupu:
            ashiria ValueError("Argument 'encoding' sio supported kwenye binary mode")
        ikiwa errors ni sio Tupu:
            ashiria ValueError("Argument 'errors' sio supported kwenye binary mode")
        ikiwa newline ni sio Tupu:
            ashiria ValueError("Argument 'newline' sio supported kwenye binary mode")

    bz_mode = mode.replace("t", "")
    binary_file = BZ2File(filename, bz_mode, compresslevel=compresslevel)

    ikiwa "t" kwenye mode:
        rudisha io.TextIOWrapper(binary_file, encoding, errors, newline)
    isipokua:
        rudisha binary_file


eleza compress(data, compresslevel=9):
    """Compress a block of data.

    compresslevel, ikiwa given, must be a number between 1 na 9.

    For incremental compression, use a BZ2Compressor object instead.
    """
    comp = BZ2Compressor(compresslevel)
    rudisha comp.compress(data) + comp.flush()


eleza decompress(data):
    """Decompress a block of data.

    For incremental decompression, use a BZ2Decompressor object instead.
    """
    results = []
    wakati data:
        decomp = BZ2Decompressor()
        jaribu:
            res = decomp.decompress(data)
        tatizo OSError:
            ikiwa results:
                koma  # Leftover data ni sio a valid bzip2 stream; ignore it.
            isipokua:
                ashiria  # Error on the first iteration; bail out.
        results.append(res)
        ikiwa sio decomp.eof:
            ashiria ValueError("Compressed data ended before the "
                             "end-of-stream marker was reached")
        data = decomp.unused_data
    rudisha b"".join(results)
