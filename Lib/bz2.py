"""Interface to the libbzip2 compression library.

This module provides a file interface, classes for incremental
(de)compression, and functions for one-shot (de)compression.
"""

__all__ = ["BZ2File", "BZ2Compressor", "BZ2Decompressor",
           "open", "compress", "decompress"]

__author__ = "Nadeem Vawda <nadeem.vawda@gmail.com>"

kutoka builtins agiza open as _builtin_open
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

    A BZ2File can act as a wrapper for an existing file object, or refer
    directly to a named file on disk.

    Note that BZ2File provides a *binary* file interface - data read is
    returned as bytes, and data to be written should be given as bytes.
    """

    eleza __init__(self, filename, mode="r", buffering=_sentinel, compresslevel=9):
        """Open a bzip2-compressed file.

        If filename is a str, bytes, or PathLike object, it gives the
        name of the file to be opened. Otherwise, it should be a file
        object, which will be used to read or write the compressed data.

        mode can be 'r' for reading (default), 'w' for (over)writing,
        'x' for creating exclusively, or 'a' for appending. These can
        equivalently be given as 'rb', 'wb', 'xb', and 'ab'.

        buffering is ignored since Python 3.0. Its use is deprecated.

        If mode is 'w', 'x' or 'a', compresslevel can be a number between 1
        and 9 specifying the level of compression: 1 produces the least
        compression, and 9 (default) produces the most compression.

        If mode is 'r', the input file may be the concatenation of
        multiple compressed streams.
        """
        # This lock must be recursive, so that BufferedIOBase's
        # writelines() does not deadlock.
        self._lock = RLock()
        self._fp = None
        self._closefp = False
        self._mode = _MODE_CLOSED

        ikiwa buffering is not _sentinel:
            warnings.warn("Use of 'buffering' argument is deprecated and ignored "
                          "since Python 3.0.",
                          DeprecationWarning,
                          stacklevel=2)

        ikiwa not (1 <= compresslevel <= 9):
            raise ValueError("compresslevel must be between 1 and 9")

        ikiwa mode in ("", "r", "rb"):
            mode = "rb"
            mode_code = _MODE_READ
        elikiwa mode in ("w", "wb"):
            mode = "wb"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        elikiwa mode in ("x", "xb"):
            mode = "xb"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        elikiwa mode in ("a", "ab"):
            mode = "ab"
            mode_code = _MODE_WRITE
            self._compressor = BZ2Compressor(compresslevel)
        else:
            raise ValueError("Invalid mode: %r" % (mode,))

        ikiwa isinstance(filename, (str, bytes, os.PathLike)):
            self._fp = _builtin_open(filename, mode)
            self._closefp = True
            self._mode = mode_code
        elikiwa hasattr(filename, "read") or hasattr(filename, "write"):
            self._fp = filename
            self._mode = mode_code
        else:
            raise TypeError("filename must be a str, bytes, file or PathLike object")

        ikiwa self._mode == _MODE_READ:
            raw = _compression.DecompressReader(self._fp,
                BZ2Decompressor, trailing_error=OSError)
            self._buffer = io.BufferedReader(raw)
        else:
            self._pos = 0

    eleza close(self):
        """Flush and close the file.

        May be called more than once without error. Once the file is
        closed, any other operation on it will raise a ValueError.
        """
        with self._lock:
            ikiwa self._mode == _MODE_CLOSED:
                return
            try:
                ikiwa self._mode == _MODE_READ:
                    self._buffer.close()
                elikiwa self._mode == _MODE_WRITE:
                    self._fp.write(self._compressor.flush())
                    self._compressor = None
            finally:
                try:
                    ikiwa self._closefp:
                        self._fp.close()
                finally:
                    self._fp = None
                    self._closefp = False
                    self._mode = _MODE_CLOSED
                    self._buffer = None

    @property
    eleza closed(self):
        """True ikiwa this file is closed."""
        rudisha self._mode == _MODE_CLOSED

    eleza fileno(self):
        """Return the file descriptor for the underlying file."""
        self._check_not_closed()
        rudisha self._fp.fileno()

    eleza seekable(self):
        """Return whether the file supports seeking."""
        rudisha self.readable() and self._buffer.seekable()

    eleza readable(self):
        """Return whether the file was opened for reading."""
        self._check_not_closed()
        rudisha self._mode == _MODE_READ

    eleza writable(self):
        """Return whether the file was opened for writing."""
        self._check_not_closed()
        rudisha self._mode == _MODE_WRITE

    eleza peek(self, n=0):
        """Return buffered data without advancing the file position.

        Always returns at least one byte of data, unless at EOF.
        The exact number of bytes returned is unspecified.
        """
        with self._lock:
            self._check_can_read()
            # Relies on the undocumented fact that BufferedReader.peek()
            # always returns at least one byte (except at EOF), independent
            # of the value of n
            rudisha self._buffer.peek(n)

    eleza read(self, size=-1):
        """Read up to size uncompressed bytes kutoka the file.

        If size is negative or omitted, read until EOF is reached.
        Returns b'' ikiwa the file is already at EOF.
        """
        with self._lock:
            self._check_can_read()
            rudisha self._buffer.read(size)

    eleza read1(self, size=-1):
        """Read up to size uncompressed bytes, while trying to avoid
        making multiple reads kutoka the underlying stream. Reads up to a
        buffer's worth of data ikiwa size is negative.

        Returns b'' ikiwa the file is at EOF.
        """
        with self._lock:
            self._check_can_read()
            ikiwa size < 0:
                size = io.DEFAULT_BUFFER_SIZE
            rudisha self._buffer.read1(size)

    eleza readinto(self, b):
        """Read bytes into b.

        Returns the number of bytes read (0 for EOF).
        """
        with self._lock:
            self._check_can_read()
            rudisha self._buffer.readinto(b)

    eleza readline(self, size=-1):
        """Read a line of uncompressed bytes kutoka the file.

        The terminating newline (ikiwa present) is retained. If size is
        non-negative, no more than size bytes will be read (in which
        case the line may be incomplete). Returns b'' ikiwa already at EOF.
        """
        ikiwa not isinstance(size, int):
            ikiwa not hasattr(size, "__index__"):
                raise TypeError("Integer argument expected")
            size = size.__index__()
        with self._lock:
            self._check_can_read()
            rudisha self._buffer.readline(size)

    eleza readlines(self, size=-1):
        """Read a list of lines of uncompressed bytes kutoka the file.

        size can be specified to control the number of lines read: no
        further lines will be read once the total size of the lines read
        so far equals or exceeds size.
        """
        ikiwa not isinstance(size, int):
            ikiwa not hasattr(size, "__index__"):
                raise TypeError("Integer argument expected")
            size = size.__index__()
        with self._lock:
            self._check_can_read()
            rudisha self._buffer.readlines(size)

    eleza write(self, data):
        """Write a byte string to the file.

        Returns the number of uncompressed bytes written, which is
        always len(data). Note that due to buffering, the file on disk
        may not reflect the data written until close() is called.
        """
        with self._lock:
            self._check_can_write()
            compressed = self._compressor.compress(data)
            self._fp.write(compressed)
            self._pos += len(data)
            rudisha len(data)

    eleza writelines(self, seq):
        """Write a sequence of byte strings to the file.

        Returns the number of uncompressed bytes written.
        seq can be any iterable yielding byte strings.

        Line separators are not added between the written byte strings.
        """
        with self._lock:
            rudisha _compression.BaseStream.writelines(self, seq)

    eleza seek(self, offset, whence=io.SEEK_SET):
        """Change the file position.

        The new position is specified by offset, relative to the
        position indicated by whence. Values for whence are:

            0: start of stream (default); offset must not be negative
            1: current stream position
            2: end of stream; offset must not be positive

        Returns the new file position.

        Note that seeking is emulated, so depending on the parameters,
        this operation may be extremely slow.
        """
        with self._lock:
            self._check_can_seek()
            rudisha self._buffer.seek(offset, whence)

    eleza tell(self):
        """Return the current file position."""
        with self._lock:
            self._check_not_closed()
            ikiwa self._mode == _MODE_READ:
                rudisha self._buffer.tell()
            rudisha self._pos


eleza open(filename, mode="rb", compresslevel=9,
         encoding=None, errors=None, newline=None):
    """Open a bzip2-compressed file in binary or text mode.

    The filename argument can be an actual filename (a str, bytes, or
    PathLike object), or an existing file object to read kutoka or write
    to.

    The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" or
    "ab" for binary mode, or "rt", "wt", "xt" or "at" for text mode.
    The default mode is "rb", and the default compresslevel is 9.

    For binary mode, this function is equivalent to the BZ2File
    constructor: BZ2File(filename, mode, compresslevel). In this case,
    the encoding, errors and newline arguments must not be provided.

    For text mode, a BZ2File object is created, and wrapped in an
    io.TextIOWrapper instance with the specified encoding, error
    handling behavior, and line ending(s).

    """
    ikiwa "t" in mode:
        ikiwa "b" in mode:
            raise ValueError("Invalid mode: %r" % (mode,))
    else:
        ikiwa encoding is not None:
            raise ValueError("Argument 'encoding' not supported in binary mode")
        ikiwa errors is not None:
            raise ValueError("Argument 'errors' not supported in binary mode")
        ikiwa newline is not None:
            raise ValueError("Argument 'newline' not supported in binary mode")

    bz_mode = mode.replace("t", "")
    binary_file = BZ2File(filename, bz_mode, compresslevel=compresslevel)

    ikiwa "t" in mode:
        rudisha io.TextIOWrapper(binary_file, encoding, errors, newline)
    else:
        rudisha binary_file


eleza compress(data, compresslevel=9):
    """Compress a block of data.

    compresslevel, ikiwa given, must be a number between 1 and 9.

    For incremental compression, use a BZ2Compressor object instead.
    """
    comp = BZ2Compressor(compresslevel)
    rudisha comp.compress(data) + comp.flush()


eleza decompress(data):
    """Decompress a block of data.

    For incremental decompression, use a BZ2Decompressor object instead.
    """
    results = []
    while data:
        decomp = BZ2Decompressor()
        try:
            res = decomp.decompress(data)
        except OSError:
            ikiwa results:
                break  # Leftover data is not a valid bzip2 stream; ignore it.
            else:
                raise  # Error on the first iteration; bail out.
        results.append(res)
        ikiwa not decomp.eof:
            raise ValueError("Compressed data ended before the "
                             "end-of-stream marker was reached")
        data = decomp.unused_data
    rudisha b"".join(results)
