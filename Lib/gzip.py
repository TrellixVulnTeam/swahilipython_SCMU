"""Functions that read na write gzipped files.

The user of the file doesn't have to worry about the compression,
but random access ni sio allowed."""

# based on Andrew Kuchling's minigzip.py distributed ukijumuisha the zlib module

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
         encoding=Tupu, errors=Tupu, newline=Tupu):
    """Open a gzip-compressed file kwenye binary ama text mode.

    The filename argument can be an actual filename (a str ama bytes object), ama
    an existing file object to read kutoka ama write to.

    The mode argument can be "r", "rb", "w", "wb", "x", "xb", "a" ama "ab" for
    binary mode, ama "rt", "wt", "xt" ama "at" kila text mode. The default mode is
    "rb", na the default compresslevel ni 9.

    For binary mode, this function ni equivalent to the GzipFile constructor:
    GzipFile(filename, mode, compresslevel). In this case, the encoding, errors
    na newline arguments must sio be provided.

    For text mode, a GzipFile object ni created, na wrapped kwenye an
    io.TextIOWrapper instance ukijumuisha the specified encoding, error handling
    behavior, na line ending(s).

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

    gz_mode = mode.replace("t", "")
    ikiwa isinstance(filename, (str, bytes, os.PathLike)):
        binary_file = GzipFile(filename, gz_mode, compresslevel)
    lasivyo hasattr(filename, "read") ama hasattr(filename, "write"):
        binary_file = GzipFile(Tupu, gz_mode, compresslevel, filename)
    isipokua:
        ashiria TypeError("filename must be a str ama bytes object, ama a file")

    ikiwa "t" kwenye mode:
        rudisha io.TextIOWrapper(binary_file, encoding, errors, newline)
    isipokua:
        rudisha binary_file

eleza write32u(output, value):
    # The L format writes the bit pattern correctly whether signed
    # ama unsigned.
    output.write(struct.pack("<L", value))

kundi _PaddedFile:
    """Minimal read-only file object that prepends a string to the contents
    of an actual file. Shouldn't be used outside of gzip.py, kama it lacks
    essential functionality."""

    eleza __init__(self, f, prepend=b''):
        self._buffer = prepend
        self._length = len(prepend)
        self.file = f
        self._read = 0

    eleza read(self, size):
        ikiwa self._read ni Tupu:
            rudisha self.file.read(size)
        ikiwa self._read + size <= self._length:
            read = self._read
            self._read += size
            rudisha self._buffer[read:self._read]
        isipokua:
            read = self._read
            self._read = Tupu
            rudisha self._buffer[read:] + \
                   self.file.read(size-self._length+read)

    eleza prepend(self, prepend=b''):
        ikiwa self._read ni Tupu:
            self._buffer = prepend
        isipokua:  # Assume data was read since the last prepend() call
            self._read -= len(prepend)
            return
        self._length = len(self._buffer)
        self._read = 0

    eleza seek(self, off):
        self._read = Tupu
        self._buffer = Tupu
        rudisha self.file.seek(off)

    eleza seekable(self):
        rudisha Kweli  # Allows fast-forwarding even kwenye unseekable streams


kundi BadGzipFile(OSError):
    """Exception raised kwenye some cases kila invalid gzip files."""


kundi GzipFile(_compression.BaseStream):
    """The GzipFile kundi simulates most of the methods of a file object with
    the exception of the truncate() method.

    This kundi only supports opening files kwenye binary mode. If you need to open a
    compressed file kwenye text mode, use the gzip.open() function.

    """

    # Overridden ukijumuisha internal file object to be closed, ikiwa only a filename
    # ni pitaed in
    myfileobj = Tupu

    eleza __init__(self, filename=Tupu, mode=Tupu,
                 compresslevel=_COMPRESS_LEVEL_BEST, fileobj=Tupu, mtime=Tupu):
        """Constructor kila the GzipFile class.

        At least one of fileobj na filename must be given a
        non-trivial value.

        The new kundi instance ni based on fileobj, which can be a regular
        file, an io.BytesIO object, ama any other object which simulates a file.
        It defaults to Tupu, kwenye which case filename ni opened to provide
        a file object.

        When fileobj ni sio Tupu, the filename argument ni only used to be
        included kwenye the gzip file header, which may include the original
        filename of the uncompressed file.  It defaults to the filename of
        fileobj, ikiwa discernible; otherwise, it defaults to the empty string,
        na kwenye this case the original filename ni sio included kwenye the header.

        The mode argument can be any of 'r', 'rb', 'a', 'ab', 'w', 'wb', 'x', ama
        'xb' depending on whether the file will be read ama written.  The default
        ni the mode of fileobj ikiwa discernible; otherwise, the default ni 'rb'.
        A mode of 'r' ni equivalent to one of 'rb', na similarly kila 'w' na
        'wb', 'a' na 'ab', na 'x' na 'xb'.

        The compresslevel argument ni an integer kutoka 0 to 9 controlling the
        level of compression; 1 ni fastest na produces the least compression,
        na 9 ni slowest na produces the most compression. 0 ni no compression
        at all. The default ni 9.

        The mtime argument ni an optional numeric timestamp to be written
        to the last modification time field kwenye the stream when compressing.
        If omitted ama Tupu, the current time ni used.

        """

        ikiwa mode na ('t' kwenye mode ama 'U' kwenye mode):
            ashiria ValueError("Invalid mode: {!r}".format(mode))
        ikiwa mode na 'b' haiko kwenye mode:
            mode += 'b'
        ikiwa fileobj ni Tupu:
            fileobj = self.myfileobj = builtins.open(filename, mode ama 'rb')
        ikiwa filename ni Tupu:
            filename = getattr(fileobj, 'name', '')
            ikiwa sio isinstance(filename, (str, bytes)):
                filename = ''
        isipokua:
            filename = os.fspath(filename)
        ikiwa mode ni Tupu:
            mode = getattr(fileobj, 'mode', 'rb')

        ikiwa mode.startswith('r'):
            self.mode = READ
            raw = _GzipReader(fileobj)
            self._buffer = io.BufferedReader(raw)
            self.name = filename

        lasivyo mode.startswith(('w', 'a', 'x')):
            self.mode = WRITE
            self._init_write(filename)
            self.compress = zlib.compressobj(compresslevel,
                                             zlib.DEFLATED,
                                             -zlib.MAX_WBITS,
                                             zlib.DEF_MEM_LEVEL,
                                             0)
            self._write_mtime = mtime
        isipokua:
            ashiria ValueError("Invalid mode: {!r}".format(mode))

        self.fileobj = fileobj

        ikiwa self.mode == WRITE:
            self._write_gzip_header()

    @property
    eleza filename(self):
        agiza warnings
        warnings.warn("use the name attribute", DeprecationWarning, 2)
        ikiwa self.mode == WRITE na self.name[-3:] != ".gz":
            rudisha self.name + ".gz"
        rudisha self.name

    @property
    eleza mtime(self):
        """Last modification time read kutoka stream, ama Tupu"""
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
        self.offset = 0  # Current file offset kila seek(), tell(), etc

    eleza _write_gzip_header(self):
        self.fileobj.write(b'\037\213')             # magic header
        self.fileobj.write(b'\010')                 # compression method
        jaribu:
            # RFC 1952 requires the FNAME field to be Latin-1. Do not
            # include filenames that cannot be represented that way.
            fname = os.path.basename(self.name)
            ikiwa sio isinstance(fname, bytes):
                fname = fname.encode('latin-1')
            ikiwa fname.endswith(b'.gz'):
                fname = fname[:-3]
        tatizo UnicodeEncodeError:
            fname = b''
        flags = 0
        ikiwa fname:
            flags = FNAME
        self.fileobj.write(chr(flags).encode('latin-1'))
        mtime = self._write_mtime
        ikiwa mtime ni Tupu:
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
            ashiria OSError(errno.EBADF, "write() on read-only GzipFile object")

        ikiwa self.fileobj ni Tupu:
            ashiria ValueError("write() on closed GzipFile object")

        ikiwa isinstance(data, bytes):
            length = len(data)
        isipokua:
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
            ashiria OSError(errno.EBADF, "read() on write-only GzipFile object")
        rudisha self._buffer.read(size)

    eleza read1(self, size=-1):
        """Implements BufferedIOBase.read1()

        Reads up to a buffer's worth of data ikiwa size ni negative."""
        self._check_not_closed()
        ikiwa self.mode != READ:
            agiza errno
            ashiria OSError(errno.EBADF, "read1() on write-only GzipFile object")

        ikiwa size < 0:
            size = io.DEFAULT_BUFFER_SIZE
        rudisha self._buffer.read1(size)

    eleza peek(self, n):
        self._check_not_closed()
        ikiwa self.mode != READ:
            agiza errno
            ashiria OSError(errno.EBADF, "peek() on write-only GzipFile object")
        rudisha self._buffer.peek(n)

    @property
    eleza closed(self):
        rudisha self.fileobj ni Tupu

    eleza close(self):
        fileobj = self.fileobj
        ikiwa fileobj ni Tupu:
            return
        self.fileobj = Tupu
        jaribu:
            ikiwa self.mode == WRITE:
                fileobj.write(self.compress.flush())
                write32u(fileobj, self.crc)
                # self.size may exceed 2 GiB, ama even 4 GiB
                write32u(fileobj, self.size & 0xffffffff)
            lasivyo self.mode == READ:
                self._buffer.close()
        mwishowe:
            myfileobj = self.myfileobj
            ikiwa myfileobj:
                self.myfileobj = Tupu
                myfileobj.close()

    eleza flush(self,zlib_mode=zlib.Z_SYNC_FLUSH):
        self._check_not_closed()
        ikiwa self.mode == WRITE:
            # Ensure the compressor's buffer ni flushed
            self.fileobj.write(self.compress.flush(zlib_mode))
            self.fileobj.flush()

    eleza fileno(self):
        """Invoke the underlying file object's fileno() method.

        This will ashiria AttributeError ikiwa the underlying file object
        doesn't support fileno().
        """
        rudisha self.fileobj.fileno()

    eleza rewind(self):
        '''Return the uncompressed stream file position indicator to the
        beginning of the file'''
        ikiwa self.mode != READ:
            ashiria OSError("Can't rewind kwenye write mode")
        self._buffer.seek(0)

    eleza readable(self):
        rudisha self.mode == READ

    eleza writable(self):
        rudisha self.mode == WRITE

    eleza seekable(self):
        rudisha Kweli

    eleza seek(self, offset, whence=io.SEEK_SET):
        ikiwa self.mode == WRITE:
            ikiwa whence != io.SEEK_SET:
                ikiwa whence == io.SEEK_CUR:
                    offset = self.offset + offset
                isipokua:
                    ashiria ValueError('Seek kutoka end sio supported')
            ikiwa offset < self.offset:
                ashiria OSError('Negative seek kwenye write mode')
            count = offset - self.offset
            chunk = b'\0' * 1024
            kila i kwenye range(count // 1024):
                self.write(chunk)
            self.write(b'\0' * (count % 1024))
        lasivyo self.mode == READ:
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
        self._new_member = Kweli
        self._last_mtime = Tupu

    eleza _init_read(self):
        self._crc = zlib.crc32(b"")
        self._stream_size = 0  # Decompressed size of unconcatenated stream

    eleza _read_exact(self, n):
        '''Read exactly *n* bytes kutoka `self._fp`

        This method ni required because self._fp may be unbuffered,
        i.e. rudisha short reads.
        '''

        data = self._fp.read(n)
        wakati len(data) < n:
            b = self._fp.read(n - len(data))
            ikiwa sio b:
                ashiria EOFError("Compressed file ended before the "
                               "end-of-stream marker was reached")
            data += b
        rudisha data

    eleza _read_gzip_header(self):
        magic = self._fp.read(2)
        ikiwa magic == b'':
            rudisha Uongo

        ikiwa magic != b'\037\213':
            ashiria BadGzipFile('Not a gzipped file (%r)' % magic)

        (method, flag,
         self._last_mtime) = struct.unpack("<BBIxx", self._read_exact(8))
        ikiwa method != 8:
            ashiria BadGzipFile('Unknown compression method')

        ikiwa flag & FEXTRA:
            # Read & discard the extra field, ikiwa present
            extra_len, = struct.unpack("<H", self._read_exact(2))
            self._read_exact(extra_len)
        ikiwa flag & FNAME:
            # Read na discard a null-terminated string containing the filename
            wakati Kweli:
                s = self._fp.read(1)
                ikiwa sio s ama s==b'\000':
                    koma
        ikiwa flag & FCOMMENT:
            # Read na discard a null-terminated string containing a comment
            wakati Kweli:
                s = self._fp.read(1)
                ikiwa sio s ama s==b'\000':
                    koma
        ikiwa flag & FHCRC:
            self._read_exact(2)     # Read & discard the 16-bit header CRC
        rudisha Kweli

    eleza read(self, size=-1):
        ikiwa size < 0:
            rudisha self.readall()
        # size=0 ni special because decompress(max_length=0) ni sio supported
        ikiwa sio size:
            rudisha b""

        # For certain input data, a single
        # call to decompress() may sio return
        # any data. In this case, retry until we get some data ama reach EOF.
        wakati Kweli:
            ikiwa self._decompressor.eof:
                # Ending case: we've come to the end of a member kwenye the file,
                # so finish up this member, na read a new gzip header.
                # Check the CRC na file size, na set the flag so we read
                # a new member
                self._read_eof()
                self._new_member = Kweli
                self._decompressor = self._decomp_factory(
                    **self._decomp_args)

            ikiwa self._new_member:
                # If the _new_member flag ni set, we have to
                # jump to the next member, ikiwa there ni one.
                self._init_read()
                ikiwa sio self._read_gzip_header():
                    self._size = self._pos
                    rudisha b""
                self._new_member = Uongo

            # Read a chunk of data kutoka the file
            buf = self._fp.read(io.DEFAULT_BUFFER_SIZE)

            uncompress = self._decompressor.decompress(buf, size)
            ikiwa self._decompressor.unconsumed_tail != b"":
                self._fp.prepend(self._decompressor.unconsumed_tail)
            lasivyo self._decompressor.unused_data != b"":
                # Prepend the already read bytes to the fileobj so they can
                # be seen by _read_eof() na _read_gzip_header()
                self._fp.prepend(self._decompressor.unused_data)

            ikiwa uncompress != b"":
                koma
            ikiwa buf == b"":
                ashiria EOFError("Compressed file ended before the "
                               "end-of-stream marker was reached")

        self._add_read_data( uncompress )
        self._pos += len(uncompress)
        rudisha uncompress

    eleza _add_read_data(self, data):
        self._crc = zlib.crc32(data, self._crc)
        self._stream_size = self._stream_size + len(data)

    eleza _read_eof(self):
        # We've read to the end of the file
        # We check the that the computed CRC na size of the
        # uncompressed data matches the stored values.  Note that the size
        # stored ni the true file size mod 2**32.
        crc32, isize = struct.unpack("<II", self._read_exact(8))
        ikiwa crc32 != self._crc:
            ashiria BadGzipFile("CRC check failed %s != %s" % (hex(crc32),
                                                             hex(self._crc)))
        lasivyo isize != (self._stream_size & 0xffffffff):
            ashiria BadGzipFile("Incorrect length of data produced")

        # Gzip files can be padded ukijumuisha zeroes na still have archives.
        # Consume all zero bytes na set the file position to the first
        # non-zero byte. See http://www.gzip.org/#faq8
        c = b"\x00"
        wakati c == b"\x00":
            c = self._fp.read(1)
        ikiwa c:
            self._fp.prepend(c)

    eleza _rewind(self):
        super()._rewind()
        self._new_member = Kweli

eleza compress(data, compresslevel=_COMPRESS_LEVEL_BEST, *, mtime=Tupu):
    """Compress data kwenye one shot na rudisha the compressed string.
    Optional argument ni the compression level, kwenye range of 0-9.
    """
    buf = io.BytesIO()
    ukijumuisha GzipFile(fileobj=buf, mode='wb', compresslevel=compresslevel, mtime=mtime) kama f:
        f.write(data)
    rudisha buf.getvalue()

eleza decompress(data):
    """Decompress a gzip compressed string kwenye one shot.
    Return the decompressed string.
    """
    ukijumuisha GzipFile(fileobj=io.BytesIO(data)) kama f:
        rudisha f.read()


eleza main():
    kutoka argparse agiza ArgumentParser
    parser = ArgumentParser(description=
        "A simple command line interface kila the gzip module: act like gzip, "
        "but do sio delete the input file.")
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
    lasivyo args.best:
        compresslevel = _COMPRESS_LEVEL_BEST

    kila arg kwenye args.args:
        ikiwa args.decompress:
            ikiwa arg == "-":
                f = GzipFile(filename="", mode="rb", fileobj=sys.stdin.buffer)
                g = sys.stdout.buffer
            isipokua:
                ikiwa arg[-3:] != ".gz":
                    andika("filename doesn't end kwenye .gz:", repr(arg))
                    endelea
                f = open(arg, "rb")
                g = builtins.open(arg[:-3], "wb")
        isipokua:
            ikiwa arg == "-":
                f = sys.stdin.buffer
                g = GzipFile(filename="", mode="wb", fileobj=sys.stdout.buffer,
                             compresslevel=compresslevel)
            isipokua:
                f = builtins.open(arg, "rb")
                g = open(arg + ".gz", "wb")
        wakati Kweli:
            chunk = f.read(1024)
            ikiwa sio chunk:
                koma
            g.write(chunk)
        ikiwa g ni sio sys.stdout.buffer:
            g.close()
        ikiwa f ni sio sys.stdin.buffer:
            f.close()

ikiwa __name__ == '__main__':
    main()
