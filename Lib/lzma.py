"""Interface to the liblzma compression library.

This module provides a kundi kila reading na writing compressed files,
classes kila incremental (de)compression, na convenience functions for
one-shot (de)compression.

These classes na functions support both the XZ na legacy LZMA
container formats, kama well kama raw compressed data streams.
"""

__all__ = [
    "CHECK_NONE", "CHECK_CRC32", "CHECK_CRC64", "CHECK_SHA256",
    "CHECK_ID_MAX", "CHECK_UNKNOWN",
    "FILTER_LZMA1", "FILTER_LZMA2", "FILTER_DELTA", "FILTER_X86", "FILTER_IA64",
    "FILTER_ARM", "FILTER_ARMTHUMB", "FILTER_POWERPC", "FILTER_SPARC",
    "FORMAT_AUTO", "FORMAT_XZ", "FORMAT_ALONE", "FORMAT_RAW",
    "MF_HC3", "MF_HC4", "MF_BT2", "MF_BT3", "MF_BT4",
    "MODE_FAST", "MODE_NORMAL", "PRESET_DEFAULT", "PRESET_EXTREME",

    "LZMACompressor", "LZMADecompressor", "LZMAFile", "LZMAError",
    "open", "compress", "decompress", "is_check_supported",
]

agiza builtins
agiza io
agiza os
kutoka _lzma agiza *
kutoka _lzma agiza _encode_filter_properties, _decode_filter_properties
agiza _compression


_MODE_CLOSED   = 0
_MODE_READ     = 1
# Value 2 no longer used
_MODE_WRITE    = 3


kundi LZMAFile(_compression.BaseStream):

    """A file object providing transparent LZMA (de)compression.

    An LZMAFile can act kama a wrapper kila an existing file object, ama
    refer directly to a named file on disk.

    Note that LZMAFile provides a *binary* file interface - data read
    ni returned kama bytes, na data to be written must be given kama bytes.
    """

    eleza __init__(self, filename=Tupu, mode="r", *,
                 format=Tupu, check=-1, preset=Tupu, filters=Tupu):
        """Open an LZMA-compressed file kwenye binary mode.

        filename can be either an actual file name (given kama a str,
        bytes, ama PathLike object), kwenye which case the named file is
        opened, ama it can be an existing file object to read kutoka ama
        write to.

        mode can be "r" kila reading (default), "w" kila (over)writing,
        "x" kila creating exclusively, ama "a" kila appending. These can
        equivalently be given kama "rb", "wb", "xb" na "ab" respectively.

        format specifies the container format to use kila the file.
        If mode ni "r", this defaults to FORMAT_AUTO. Otherwise, the
        default ni FORMAT_XZ.

        check specifies the integrity check to use. This argument can
        only be used when opening a file kila writing. For FORMAT_XZ,
        the default ni CHECK_CRC64. FORMAT_ALONE na FORMAT_RAW do not
        support integrity checks - kila these formats, check must be
        omitted, ama be CHECK_NONE.

        When opening a file kila reading, the *preset* argument ni not
        meaningful, na should be omitted. The *filters* argument should
        also be omitted, tatizo when format ni FORMAT_RAW (in which case
        it ni required).

        When opening a file kila writing, the settings used by the
        compressor can be specified either kama a preset compression
        level (ukijumuisha the *preset* argument), ama kwenye detail kama a custom
        filter chain (ukijumuisha the *filters* argument). For FORMAT_XZ na
        FORMAT_ALONE, the default ni to use the PRESET_DEFAULT preset
        level. For FORMAT_RAW, the caller must always specify a filter
        chain; the raw compressor does sio support preset compression
        levels.

        preset (ikiwa provided) should be an integer kwenye the range 0-9,
        optionally OR-ed ukijumuisha the constant PRESET_EXTREME.

        filters (ikiwa provided) should be a sequence of dicts. Each dict
        should have an entry kila "id" indicating ID of the filter, plus
        additional entries kila options to the filter.
        """
        self._fp = Tupu
        self._closefp = Uongo
        self._mode = _MODE_CLOSED

        ikiwa mode kwenye ("r", "rb"):
            ikiwa check != -1:
                ashiria ValueError("Cannot specify an integrity check "
                                 "when opening a file kila reading")
            ikiwa preset ni sio Tupu:
                ashiria ValueError("Cannot specify a preset compression "
                                 "level when opening a file kila reading")
            ikiwa format ni Tupu:
                format = FORMAT_AUTO
            mode_code = _MODE_READ
        lasivyo mode kwenye ("w", "wb", "a", "ab", "x", "xb"):
            ikiwa format ni Tupu:
                format = FORMAT_XZ
            mode_code = _MODE_WRITE
            self._compressor = LZMACompressor(format=format, check=check,
                                              preset=preset, filters=filters)
            self._pos = 0
        isipokua:
            ashiria ValueError("Invalid mode: {!r}".format(mode))

        ikiwa isinstance(filename, (str, bytes, os.PathLike)):
            ikiwa "b" haiko kwenye mode:
                mode += "b"
            self._fp = builtins.open(filename, mode)
            self._closefp = Kweli
            self._mode = mode_code
        lasivyo hasattr(filename, "read") ama hasattr(filename, "write"):
            self._fp = filename
            self._mode = mode_code
        isipokua:
            ashiria TypeError("filename must be a str, bytes, file ama PathLike object")

        ikiwa self._mode == _MODE_READ:
            raw = _compression.DecompressReader(self._fp, LZMADecompressor,
                trailing_error=LZMAError, format=format, filters=filters)
            self._buffer = io.BufferedReader(raw)

    eleza close(self):
        """Flush na close the file.

        May be called more than once without error. Once the file is
        closed, any other operation on it will ashiria a ValueError.
        """
        ikiwa self._mode == _MODE_CLOSED:
            rudisha
        jaribu:
            ikiwa self._mode == _MODE_READ:
                self._buffer.close()
                self._buffer = Tupu
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

    eleza peek(self, size=-1):
        """Return buffered data without advancing the file position.

        Always returns at least one byte of data, unless at EOF.
        The exact number of bytes returned ni unspecified.
        """
        self._check_can_read()
        # Relies on the undocumented fact that BufferedReader.peek() always
        # returns at least one byte (tatizo at EOF)
        rudisha self._buffer.peek(size)

    eleza read(self, size=-1):
        """Read up to size uncompressed bytes kutoka the file.

        If size ni negative ama omitted, read until EOF ni reached.
        Returns b"" ikiwa the file ni already at EOF.
        """
        self._check_can_read()
        rudisha self._buffer.read(size)

    eleza read1(self, size=-1):
        """Read up to size uncompressed bytes, wakati trying to avoid
        making multiple reads kutoka the underlying stream. Reads up to a
        buffer's worth of data ikiwa size ni negative.

        Returns b"" ikiwa the file ni at EOF.
        """
        self._check_can_read()
        ikiwa size < 0:
            size = io.DEFAULT_BUFFER_SIZE
        rudisha self._buffer.read1(size)

    eleza readline(self, size=-1):
        """Read a line of uncompressed bytes kutoka the file.

        The terminating newline (ikiwa present) ni retained. If size is
        non-negative, no more than size bytes will be read (in which
        case the line may be incomplete). Returns b'' ikiwa already at EOF.
        """
        self._check_can_read()
        rudisha self._buffer.readline(size)

    eleza write(self, data):
        """Write a bytes object to the file.

        Returns the number of uncompressed bytes written, which is
        always len(data). Note that due to buffering, the file on disk
        may sio reflect the data written until close() ni called.
        """
        self._check_can_write()
        compressed = self._compressor.compress(data)
        self._fp.write(compressed)
        self._pos += len(data)
        rudisha len(data)

    eleza seek(self, offset, whence=io.SEEK_SET):
        """Change the file position.

        The new position ni specified by offset, relative to the
        position indicated by whence. Possible values kila whence are:

            0: start of stream (default): offset must sio be negative
            1: current stream position
            2: end of stream; offset must sio be positive

        Returns the new file position.

        Note that seeking ni emulated, so depending on the parameters,
        this operation may be extremely slow.
        """
        self._check_can_seek()
        rudisha self._buffer.seek(offset, whence)

    eleza tell(self):
        """Return the current file position."""
        self._check_not_closed()
        ikiwa self._mode == _MODE_READ:
            rudisha self._buffer.tell()
        rudisha self._pos


eleza open(filename, mode="rb", *,
         format=Tupu, check=-1, preset=Tupu, filters=Tupu,
         encoding=Tupu, errors=Tupu, newline=Tupu):
    """Open an LZMA-compressed file kwenye binary ama text mode.

    filename can be either an actual file name (given kama a str, bytes,
    ama PathLike object), kwenye which case the named file ni opened, ama it
    can be an existing file object to read kutoka ama write to.

    The mode argument can be "r", "rb" (default), "w", "wb", "x", "xb",
    "a", ama "ab" kila binary mode, ama "rt", "wt", "xt", ama "at" kila text
    mode.

    The format, check, preset na filters arguments specify the
    compression settings, kama kila LZMACompressor, LZMADecompressor na
    LZMAFile.

    For binary mode, this function ni equivalent to the LZMAFile
    constructor: LZMAFile(filename, mode, ...). In this case, the
    encoding, errors na newline arguments must sio be provided.

    For text mode, an LZMAFile object ni created, na wrapped kwenye an
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

    lz_mode = mode.replace("t", "")
    binary_file = LZMAFile(filename, lz_mode, format=format, check=check,
                           preset=preset, filters=filters)

    ikiwa "t" kwenye mode:
        rudisha io.TextIOWrapper(binary_file, encoding, errors, newline)
    isipokua:
        rudisha binary_file


eleza compress(data, format=FORMAT_XZ, check=-1, preset=Tupu, filters=Tupu):
    """Compress a block of data.

    Refer to LZMACompressor's docstring kila a description of the
    optional arguments *format*, *check*, *preset* na *filters*.

    For incremental compression, use an LZMACompressor instead.
    """
    comp = LZMACompressor(format, check, preset, filters)
    rudisha comp.compress(data) + comp.flush()


eleza decompress(data, format=FORMAT_AUTO, memlimit=Tupu, filters=Tupu):
    """Decompress a block of data.

    Refer to LZMADecompressor's docstring kila a description of the
    optional arguments *format*, *check* na *filters*.

    For incremental decompression, use an LZMADecompressor instead.
    """
    results = []
    wakati Kweli:
        decomp = LZMADecompressor(format, memlimit, filters)
        jaribu:
            res = decomp.decompress(data)
        tatizo LZMAError:
            ikiwa results:
                koma  # Leftover data ni sio a valid LZMA/XZ stream; ignore it.
            isipokua:
                ashiria  # Error on the first iteration; bail out.
        results.append(res)
        ikiwa sio decomp.eof:
            ashiria LZMAError("Compressed data ended before the "
                            "end-of-stream marker was reached")
        data = decomp.unused_data
        ikiwa sio data:
            koma
    rudisha b"".join(results)
