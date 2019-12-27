"""Functions that read and write gzipped files.

The user of the file doesn't have to worry about the compression,
but random access is not allowed."""

# based on Andrew Kuchling's minigzip.py distributed with the zlib module

agiza struct, sys, time, os
agiza zlib
agiza builtins
agiza io
agiza _compression

__all__ = ["BadGzipFile", "GzipFile", "open", "compress", "decompress"]

FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT = 1, 2, 4, 8, 16

READ, WRITE = 1, 2

_COMPRESS_LEVEL_FAST = 1
_COMPRESS_LEVEL_TRADEOFF = 6
_COMPRESS_LEVEL_BEST = 9


eleza open(filename, mode="rb", compresslevel=_COMPRESS_LEVEL_BEST,
         encoding=None, errors=None, newline=None):
    """Open a gzip-compressed file in binary or text mode.

    The filename argument can be an actual filename (a str or bytes object), or
    an existing file object to read kutoka or write to.

    The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" or "ab" for
    binary mode, or "rt", "wt", "xt" or "at" for text mode. The default mode is
    "rb", and the default compresslevel is 9.

    For binary mode, this function is equivalent to the GzipFile constructor:
    GzipFile(filename, mode, compresslevel). In this case, the encoding, errors
    and newline arguments must not be provided.

    For text mode, a GzipFile object is created, and wrapped in an
    io.TextIOWrapper instance with the specified encoding, error handling
    behavior, and line ending(s).

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

    gz_mode = mode.replace("t", "")
    ikiwa isinstance(filename, (str, bytes, os.PathLike)):
        binary_file = GzipFile(filename, gz_mode, compresslevel)
    elikiwa hasattr(filename, "read") or hasattr(filename, "write"):
        binary_file = GzipFile(None, gz_mode, compresslevel, filename)
    else:
        raise TypeError("filename must be a str or bytes object, or a file")

    ikiwa "t" in mode:
        rudisha io.TextIOWrapper(binary_file, encoding, errors, newline)
    else:
        rudisha binary_file

eleza write32u(output, value):
    # The L format writes the bit pattern correctly whether signed
    # or unsigned.
    output.write(struct.pack("<L", value))

kundi _PaddedFile:
    """Minimal read-only file object that prepends a string to the contents
    of an actual file. Shouldn't be used outside of gzip.py, as it lacks
    essential functionality."""

    eleza __init__(self, f, prepend=b''):
        self._buffer = prepend
        self._length = len(prepend)
        self.file = f
        self._read = 0

    eleza read(self, size):
        ikiwa self._read is None:
            rudisha self.file.read(size)
        ikiwa self._read + size <= self._length:
            read = self._read
            self._read += size
            rudisha self._buffer[read:self._read]
        else:
            read = self._read
            self._read = None
            rudisha self._buffer[read:] + \
                   self.file.read(size-self._length+read)

    eleza prepend(self, prepend=b''):
        ikiwa self._read is None:
            self._buffer = prepend
        else:  # Assume data was read since the last prepend() call
            self._read -= len(prepend)
            return
        self._length = len(self._buffer)
        self._read = 0

    eleza seek(self, off):
        self._read = None
        self._buffer = None
        rudisha self.file.seek(off)

    eleza seekable(self):
        rudisha True  # Allows fast-forwarding even in unseekable streams


kundi BadGzipFile(OSError):
    """Exception raised in some cases for invalid gzip files."""


kundi GzipFile(_compression.BaseStream):
    """The GzipFile kundi simulates most of the methods of a file object with
    the exception of the truncate() method.

    This kundi only supports opening files in binary mode. If you need to open a
    compressed file in text mode, use the gzip.open() function.

    """

    # Overridden with internal file object to be closed, ikiwa only a filename
    # is passed in
    myfileobj = None

    eleza __init__(self, filename=None, mode=None,
                 compresslevel=_COMPRESS_LEVEL_BEST, fileobj=None, mtime=None):
        """Constructor for the GzipFile class.

        At least one of fileobj and filename must be given a
        non-trivial value.

        The new kundi instance is based on fileobj, which can be a regular
        file, an io.BytesIO object, or any other object which simulates a file.
        It defaults to None, in which case filename is opened to provide
        a file object.

        When fileobj is not None, the filename argument is only used to be
        included in the gzip file header, which may include the original
        filename of the uncompressed file.  It defaults to the filename of
        fileobj, ikiwa discernible; otherwise, it defaults to the empty string,
        and in this case the original filename is not included in the header.

        The mode argument can be any of 'r', 'rb', 'a', 'ab', 'w', 'wb', 'x', or
        'xb' depending on whether the file will be read or written.  The default
        is the mode of fileobj ikiwa discernible; otherwise, the default is 'rb'.
        A mode of 'r' is equivalent to one of 'rb', and similarly for 'w' and
        'wb', 'a' and 'ab', and 'x' and 'xb'.

        The compresslevel argument is an integer kutoka 0 to 9 controlling the
        level of compression; 1 is fastest and produces the least compression,
        and 9 is slowest and produces the most compression. 0 is no compression
        at all. The default is 9.

        The mtime argument is an optional numeric timestamp to be written
        to the last modification time field in the stream when compressing.
        If omitted or None, the current time is used.

        """

        ikiwa mode and ('t' in mode or 'U' in mode):
            raise ValueError("Invalid mode: {!r}".format(mode))
        ikiwa mode and 'b' not in mode:
            mode += 'b'
        ikiwa fileobj is None:
            fileobj = self.myfileobj = builtins.open(filename, mode or 'rb')
        ikiwa filename is None:
            filename = getattr(fileobj, 'name', '')
            ikiwa not isinstance(filename, (str, bytes)):
                filename = ''
        else:
            filename = os.fspath(filename)
        ikiwa mode is None:
            mode = getattr(fileobj, 'mode', 'rb')

        ikiwa mode.startswith('r'):
            self.mode = READ
            raw = _GzipReader(fileobj)
            self._buffer = io.BufferedReader(raw)
            self.name = filename

        elikiwa mode.startswith(('w', 'a', 'x')):
            self.mode = WRITE
            self._init_write(filename)
            self.compress = zlib.compressobj(compresslevel,
                                             zlib.DEFLATED,
                                             -zlib.MAX_WBITS,
                                             zlib.DEF_MEM_LEVEL,
                                             0)
            self._write_mtime = mtime
        else:
            raise ValueError("Invalid mode: {!r}".format(mode))

        self.fileobj = fileobj

        ikiwa self.mode == WRITE:
            self._write_gzip_header()

    @property
    eleza filename(self):
        agiza warnings
        warnings.warn("use the name attribute", DeprecationWarning, 2)
        ikiwa self.mode == WRITE and self.name[-3:] != ".gz":
            rudisha self.name + ".gz"
        rudisha self.name

    @property
    eleza mtime(self):
        """Last modification time read kutoka stream, or None"""
        rudisha self._buffer.raw._last_mtime

    eleza __repr__(self):
        s = repr(self.fileobj)
        rudisha '<gzip ' + s[1:-1] + ' ' + hex(id(self)) + '>'

    eleza _init_write(self, filename):
        self.name = filename
        self.crc = zlib.crc32(b"")
        self.size = 0
        self.writebuf = []
        self.bufsize = 0
        self.offset = 0  # Current file offset for seek(), tell(), etc

    eleza _write_gzip_header(self):
        self.fileobj.write(b'\037\213')             # magic header
        self.fileobj.write(b'\010')                 # compression method
        try:
            # RFC 1952 requires the FNAME field to be Latin-1. Do not
            # include filenames that cannot be represented that way.
            fname = os.path.basename(self.name)
            ikiwa not isinstance(fname, bytes):
                fname = fname.encode('latin-1')
            ikiwa fname.endswith(b'.gz'):
                fname = fname[:-3]
        except UnicodeEncodeError:
            fname = b''
        flags = 0
        ikiwa fname:
            flags = FNAME
        self.fileobj.write(chr(flags).encode('latin-1'))
        mtime = self._write_mtime
        ikiwa mtime is None:
            mtime = time.time()
        write32u(self.fileobj, int(mtime))
        self.fileobj.write(b'\002')
        self.fileobj.write(b'\377')
        ikiwa fname:
            self.fileobj.write(fname + b'\000')

    eleza write(self,data):
        self._check_not_closed()
        ikiwa self.mode != WRITE:
            agiza errno
            raise OSError(errno.EBADF, "write() on read-only GzipFile object")

        ikiwa self.fileobj is None:
            raise ValueError("write() on closed GzipFile object")

        ikiwa isinstance(data, bytes):
            length = len(data)
        else:
            # accept any data that supports the buffer protocol
            data = memoryview(data)
            length = data.nbytes

        ikiwa length > 0:
            self.fileobj.write(self.compress.compress(data))
            self.size += length
            self.crc = zlib.crc32(data, self.crc)
            self.offset += length

        rudisha length

    eleza read(self, size=-1):
        self._check_not_closed()
        ikiwa self.mode != READ:
            agiza errno
            raise OSError(errno.EBADF, "read() on write-only GzipFile object")
        rudisha self._buffer.read(size)

    eleza read1(self, size=-1):
        """Implements BufferedIOBase.read1()

        Reads up to a buffer's worth of data ikiwa size is negative."""
        self._check_not_closed()
        ikiwa self.mode != READ:
            agiza errno
            raise OSError(errno.EBADF, "read1() on write-only GzipFile object")

        ikiwa size < 0:
            size = io.DEFAULT_BUFFER_SIZE
        rudisha self._buffer.read1(size)

    eleza peek(self, n):
        self._check_not_closed()
        ikiwa self.mode != READ:
            agiza errno
            raise OSError(errno.EBADF, "peek() on write-only GzipFile object")
        rudisha self._buffer.peek(n)

    @property
    eleza closed(self):
        rudisha self.fileobj is None

    eleza close(self):
        fileobj = self.fileobj
        ikiwa fileobj is None:
            return
        self.fileobj = None
        try:
            ikiwa self.mode == WRITE:
                fileobj.write(self.compress.flush())
                write32u(fileobj, self.crc)
                # self.size may exceed 2 GiB, or even 4 GiB
                write32u(fileobj, self.size & 0xffffffff)
            elikiwa self.mode == READ:
                self._buffer.close()
        finally:
            myfileobj = self.myfileobj
            ikiwa myfileobj:
                self.myfileobj = None
                myfileobj.close()

    eleza flush(self,zlib_mode=zlib.Z_SYNC_FLUSH):
        self._check_not_closed()
        ikiwa self.mode == WRITE:
            # Ensure the compressor's buffer is flushed
            self.fileobj.write(self.compress.flush(zlib_mode))
            self.fileobj.flush()

    eleza fileno(self):
        """Invoke the underlying file object's fileno() method.

        This will raise AttributeError ikiwa the underlying file object
        doesn't support fileno().
        """
        rudisha self.fileobj.fileno()

    eleza rewind(self):
        '''Return the uncompressed stream file position indicator to the
        beginning of the file'''
        ikiwa self.mode != READ:
            raise OSError("Can't rewind in write mode")
        self._buffer.seek(0)

    eleza readable(self):
        rudisha self.mode == READ

    eleza writable(self):
        rudisha self.mode == WRITE

    eleza seekable(self):
        rudisha True

    eleza seek(self, offset, whence=io.SEEK_SET):
        ikiwa self.mode == WRITE:
            ikiwa whence != io.SEEK_SET:
                ikiwa whence == io.SEEK_CUR:
                    offset = self.offset + offset
                else:
                    raise ValueError('Seek kutoka end not supported')
            ikiwa offset < self.offset:
                raise OSError('Negative seek in write mode')
            count = offset - self.offset
            chunk = b'\0' * 1024
            for i in range(count // 1024):
                self.write(chunk)
            self.write(b'\0' * (count % 1024))
        elikiwa self.mode == READ:
            self._check_not_closed()
            rudisha self._buffer.seek(offset, whence)

        rudisha self.offset

    eleza readline(self, size=-1):
        self._check_not_closed()
        rudisha self._buffer.readline(size)


kundi _GzipReader(_compression.DecompressReader):
    eleza __init__(self, fp):
        super().__init__(_PaddedFile(fp), zlib.decompressobj,
                         wbits=-zlib.MAX_WBITS)
        # Set flag indicating start of a new member
        self._new_member = True
        self._last_mtime = None

    eleza _init_read(self):
        self._crc = zlib.crc32(b"")
        self._stream_size = 0  # Decompressed size of unconcatenated stream

    eleza _read_exact(self, n):
        '''Read exactly *n* bytes kutoka `self._fp`

        This method is required because self._fp may be unbuffered,
        i.e. rudisha short reads.
        '''

        data = self._fp.read(n)
        while len(data) < n:
            b = self._fp.read(n - len(data))
            ikiwa not b:
                raise EOFError("Compressed file ended before the "
                               "end-of-stream marker was reached")
            data += b
        rudisha data

    eleza _read_gzip_header(self):
        magic = self._fp.read(2)
        ikiwa magic == b'':
            rudisha False

        ikiwa magic != b'\037\213':
            raise BadGzipFile('Not a gzipped file (%r)' % magic)

        (method, flag,
         self._last_mtime) = struct.unpack("<BBIxx", self._read_exact(8))
        ikiwa method != 8:
            raise BadGzipFile('Unknown compression method')

        ikiwa flag & FEXTRA:
            # Read & discard the extra field, ikiwa present
            extra_len, = struct.unpack("<H", self._read_exact(2))
            self._read_exact(extra_len)
        ikiwa flag & FNAME:
            # Read and discard a null-terminated string containing the filename
            while True:
                s = self._fp.read(1)
                ikiwa not s or s==b'\000':
                    break
        ikiwa flag & FCOMMENT:
            # Read and discard a null-terminated string containing a comment
            while True:
                s = self._fp.read(1)
                ikiwa not s or s==b'\000':
                    break
        ikiwa flag & FHCRC:
            self._read_exact(2)     # Read & discard the 16-bit header CRC
        rudisha True

    eleza read(self, size=-1):
        ikiwa size < 0:
            rudisha self.readall()
        # size=0 is special because decompress(max_length=0) is not supported
        ikiwa not size:
            rudisha b""

        # For certain input data, a single
        # call to decompress() may not return
        # any data. In this case, retry until we get some data or reach EOF.
        while True:
            ikiwa self._decompressor.eof:
                # Ending case: we've come to the end of a member in the file,
                # so finish up this member, and read a new gzip header.
                # Check the CRC and file size, and set the flag so we read
                # a new member
                self._read_eof()
                self._new_member = True
                self._decompressor = self._decomp_factory(
                    **self._decomp_args)

            ikiwa self._new_member:
                # If the _new_member flag is set, we have to
                # jump to the next member, ikiwa there is one.
                self._init_read()
                ikiwa not self._read_gzip_header():
                    self._size = self._pos
                    rudisha b""
                self._new_member = False

            # Read a chunk of data kutoka the file
            buf = self._fp.read(io.DEFAULT_BUFFER_SIZE)

            uncompress = self._decompressor.decompress(buf, size)
            ikiwa self._decompressor.unconsumed_tail != b"":
                self._fp.prepend(self._decompressor.unconsumed_tail)
            elikiwa self._decompressor.unused_data != b"":
                # Prepend the already read bytes to the fileobj so they can
                # be seen by _read_eof() and _read_gzip_header()
                self._fp.prepend(self._decompressor.unused_data)

            ikiwa uncompress != b"":
                break
            ikiwa buf == b"":
                raise EOFError("Compressed file ended before the "
                               "end-of-stream marker was reached")

        self._add_read_data( uncompress )
        self._pos += len(uncompress)
        rudisha uncompress

    eleza _add_read_data(self, data):
        self._crc = zlib.crc32(data, self._crc)
        self._stream_size = self._stream_size + len(data)

    eleza _read_eof(self):
        # We've read to the end of the file
        # We check the that the computed CRC and size of the
        # uncompressed data matches the stored values.  Note that the size
        # stored is the true file size mod 2**32.
        crc32, isize = struct.unpack("<II", self._read_exact(8))
        ikiwa crc32 != self._crc:
            raise BadGzipFile("CRC check failed %s != %s" % (hex(crc32),
                                                             hex(self._crc)))
        elikiwa isize != (self._stream_size & 0xffffffff):
            raise BadGzipFile("Incorrect length of data produced")

        # Gzip files can be padded with zeroes and still have archives.
        # Consume all zero bytes and set the file position to the first
        # non-zero byte. See http://www.gzip.org/#faq8
        c = b"\x00"
        while c == b"\x00":
            c = self._fp.read(1)
        ikiwa c:
            self._fp.prepend(c)

    eleza _rewind(self):
        super()._rewind()
        self._new_member = True

eleza compress(data, compresslevel=_COMPRESS_LEVEL_BEST, *, mtime=None):
    """Compress data in one shot and rudisha the compressed string.
    Optional argument is the compression level, in range of 0-9.
    """
    buf = io.BytesIO()
    with GzipFile(fileobj=buf, mode='wb', compresslevel=compresslevel, mtime=mtime) as f:
        f.write(data)
    rudisha buf.getvalue()

eleza decompress(data):
    """Decompress a gzip compressed string in one shot.
    Return the decompressed string.
    """
    with GzipFile(fileobj=io.BytesIO(data)) as f:
        rudisha f.read()


eleza main():
    kutoka argparse agiza ArgumentParser
    parser = ArgumentParser(description=
        "A simple command line interface for the gzip module: act like gzip, "
        "but do not delete the input file.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--fast', action='store_true', help='compress faster')
    group.add_argument('--best', action='store_true', help='compress better')
    group.add_argument("-d", "--decompress", action="store_true",
                        help="act like gunzip instead of gzip")

    parser.add_argument("args", nargs="*", default=["-"], metavar='file')
    args = parser.parse_args()

    compresslevel = _COMPRESS_LEVEL_TRADEOFF
    ikiwa args.fast:
        compresslevel = _COMPRESS_LEVEL_FAST
    elikiwa args.best:
        compresslevel = _COMPRESS_LEVEL_BEST

    for arg in args.args:
        ikiwa args.decompress:
            ikiwa arg == "-":
                f = GzipFile(filename="", mode="rb", fileobj=sys.stdin.buffer)
                g = sys.stdout.buffer
            else:
                ikiwa arg[-3:] != ".gz":
                    andika("filename doesn't end in .gz:", repr(arg))
                    continue
                f = open(arg, "rb")
                g = builtins.open(arg[:-3], "wb")
        else:
            ikiwa arg == "-":
                f = sys.stdin.buffer
                g = GzipFile(filename="", mode="wb", fileobj=sys.stdout.buffer,
                             compresslevel=compresslevel)
            else:
                f = builtins.open(arg, "rb")
                g = open(arg + ".gz", "wb")
        while True:
            chunk = f.read(1024)
            ikiwa not chunk:
                break
            g.write(chunk)
        ikiwa g is not sys.stdout.buffer:
            g.close()
        ikiwa f is not sys.stdin.buffer:
            f.close()

ikiwa __name__ == '__main__':
    main()
