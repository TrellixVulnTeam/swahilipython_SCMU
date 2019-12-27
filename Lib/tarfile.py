#!/usr/bin/env python3
#-------------------------------------------------------------------
# tarfile.py
#-------------------------------------------------------------------
# Copyright (C) 2002 Lars Gustaebel <lars@gustaebel.de>
# All rights reserved.
#
# Permission  is  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  and associated documentation
# files  (the  "Software"),  to   deal  in  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  and to  permit  persons  to  whom the
# Software  is  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice and this  permission notice shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
"""Read kutoka and write to tar format archives.
"""

version     = "0.9.0"
__author__  = "Lars Gust\u00e4bel (lars@gustaebel.de)"
__credits__ = "Gustavo Niemeyer, Niels Gust\u00e4bel, Richard Townsend."

#---------
# Imports
#---------
kutoka builtins agiza open as bltn_open
agiza sys
agiza os
agiza io
agiza shutil
agiza stat
agiza time
agiza struct
agiza copy
agiza re

try:
    agiza pwd
except ImportError:
    pwd = None
try:
    agiza grp
except ImportError:
    grp = None

# os.symlink on Windows prior to 6.0 raises NotImplementedError
symlink_exception = (AttributeError, NotImplementedError)
try:
    # OSError (winerror=1314) will be raised ikiwa the caller does not hold the
    # SeCreateSymbolicLinkPrivilege privilege
    symlink_exception += (OSError,)
except NameError:
    pass

# kutoka tarfile agiza *
__all__ = ["TarFile", "TarInfo", "is_tarfile", "TarError", "ReadError",
           "CompressionError", "StreamError", "ExtractError", "HeaderError",
           "ENCODING", "USTAR_FORMAT", "GNU_FORMAT", "PAX_FORMAT",
           "DEFAULT_FORMAT", "open"]

#---------------------------------------------------------
# tar constants
#---------------------------------------------------------
NUL = b"\0"                     # the null character
BLOCKSIZE = 512                 # length of processing blocks
RECORDSIZE = BLOCKSIZE * 20     # length of records
GNU_MAGIC = b"ustar  \0"        # magic gnu tar string
POSIX_MAGIC = b"ustar\x0000"    # magic posix tar string

LENGTH_NAME = 100               # maximum length of a filename
LENGTH_LINK = 100               # maximum length of a linkname
LENGTH_PREFIX = 155             # maximum length of the prefix field

REGTYPE = b"0"                  # regular file
AREGTYPE = b"\0"                # regular file
LNKTYPE = b"1"                  # link (inside tarfile)
SYMTYPE = b"2"                  # symbolic link
CHRTYPE = b"3"                  # character special device
BLKTYPE = b"4"                  # block special device
DIRTYPE = b"5"                  # directory
FIFOTYPE = b"6"                 # fifo special device
CONTTYPE = b"7"                 # contiguous file

GNUTYPE_LONGNAME = b"L"         # GNU tar longname
GNUTYPE_LONGLINK = b"K"         # GNU tar longlink
GNUTYPE_SPARSE = b"S"           # GNU tar sparse file

XHDTYPE = b"x"                  # POSIX.1-2001 extended header
XGLTYPE = b"g"                  # POSIX.1-2001 global header
SOLARIS_XHDTYPE = b"X"          # Solaris extended header

USTAR_FORMAT = 0                # POSIX.1-1988 (ustar) format
GNU_FORMAT = 1                  # GNU tar format
PAX_FORMAT = 2                  # POSIX.1-2001 (pax) format
DEFAULT_FORMAT = PAX_FORMAT

#---------------------------------------------------------
# tarfile constants
#---------------------------------------------------------
# File types that tarfile supports:
SUPPORTED_TYPES = (REGTYPE, AREGTYPE, LNKTYPE,
                   SYMTYPE, DIRTYPE, FIFOTYPE,
                   CONTTYPE, CHRTYPE, BLKTYPE,
                   GNUTYPE_LONGNAME, GNUTYPE_LONGLINK,
                   GNUTYPE_SPARSE)

# File types that will be treated as a regular file.
REGULAR_TYPES = (REGTYPE, AREGTYPE,
                 CONTTYPE, GNUTYPE_SPARSE)

# File types that are part of the GNU tar format.
GNU_TYPES = (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK,
             GNUTYPE_SPARSE)

# Fields kutoka a pax header that override a TarInfo attribute.
PAX_FIELDS = ("path", "linkpath", "size", "mtime",
              "uid", "gid", "uname", "gname")

# Fields kutoka a pax header that are affected by hdrcharset.
PAX_NAME_FIELDS = {"path", "linkpath", "uname", "gname"}

# Fields in a pax header that are numbers, all other fields
# are treated as strings.
PAX_NUMBER_FIELDS = {
    "atime": float,
    "ctime": float,
    "mtime": float,
    "uid": int,
    "gid": int,
    "size": int
}

#---------------------------------------------------------
# initialization
#---------------------------------------------------------
ikiwa os.name == "nt":
    ENCODING = "utf-8"
else:
    ENCODING = sys.getfilesystemencoding()

#---------------------------------------------------------
# Some useful functions
#---------------------------------------------------------

eleza stn(s, length, encoding, errors):
    """Convert a string to a null-terminated bytes object.
    """
    s = s.encode(encoding, errors)
    rudisha s[:length] + (length - len(s)) * NUL

eleza nts(s, encoding, errors):
    """Convert a null-terminated bytes object to a string.
    """
    p = s.find(b"\0")
    ikiwa p != -1:
        s = s[:p]
    rudisha s.decode(encoding, errors)

eleza nti(s):
    """Convert a number field to a python number.
    """
    # There are two possible encodings for a number field, see
    # itn() below.
    ikiwa s[0] in (0o200, 0o377):
        n = 0
        for i in range(len(s) - 1):
            n <<= 8
            n += s[i + 1]
        ikiwa s[0] == 0o377:
            n = -(256 ** (len(s) - 1) - n)
    else:
        try:
            s = nts(s, "ascii", "strict")
            n = int(s.strip() or "0", 8)
        except ValueError:
            raise InvalidHeaderError("invalid header")
    rudisha n

eleza itn(n, digits=8, format=DEFAULT_FORMAT):
    """Convert a python number to a number field.
    """
    # POSIX 1003.1-1988 requires numbers to be encoded as a string of
    # octal digits followed by a null-byte, this allows values up to
    # (8**(digits-1))-1. GNU tar allows storing numbers greater than
    # that ikiwa necessary. A leading 0o200 or 0o377 byte indicate this
    # particular encoding, the following digits-1 bytes are a big-endian
    # base-256 representation. This allows values up to (256**(digits-1))-1.
    # A 0o200 byte indicates a positive number, a 0o377 byte a negative
    # number.
    n = int(n)
    ikiwa 0 <= n < 8 ** (digits - 1):
        s = bytes("%0*o" % (digits - 1, n), "ascii") + NUL
    elikiwa format == GNU_FORMAT and -256 ** (digits - 1) <= n < 256 ** (digits - 1):
        ikiwa n >= 0:
            s = bytearray([0o200])
        else:
            s = bytearray([0o377])
            n = 256 ** digits + n

        for i in range(digits - 1):
            s.insert(1, n & 0o377)
            n >>= 8
    else:
        raise ValueError("overflow in number field")

    rudisha s

eleza calc_chksums(buf):
    """Calculate the checksum for a member's header by summing up all
       characters except for the chksum field which is treated as if
       it was filled with spaces. According to the GNU tar sources,
       some tars (Sun and NeXT) calculate chksum with signed char,
       which will be different ikiwa there are chars in the buffer with
       the high bit set. So we calculate two checksums, unsigned and
       signed.
    """
    unsigned_chksum = 256 + sum(struct.unpack_kutoka("148B8x356B", buf))
    signed_chksum = 256 + sum(struct.unpack_kutoka("148b8x356b", buf))
    rudisha unsigned_chksum, signed_chksum

eleza copyfileobj(src, dst, length=None, exception=OSError, bufsize=None):
    """Copy length bytes kutoka fileobj src to fileobj dst.
       If length is None, copy the entire content.
    """
    bufsize = bufsize or 16 * 1024
    ikiwa length == 0:
        return
    ikiwa length is None:
        shutil.copyfileobj(src, dst, bufsize)
        return

    blocks, remainder = divmod(length, bufsize)
    for b in range(blocks):
        buf = src.read(bufsize)
        ikiwa len(buf) < bufsize:
            raise exception("unexpected end of data")
        dst.write(buf)

    ikiwa remainder != 0:
        buf = src.read(remainder)
        ikiwa len(buf) < remainder:
            raise exception("unexpected end of data")
        dst.write(buf)
    return

eleza _safe_andika(s):
    encoding = getattr(sys.stdout, 'encoding', None)
    ikiwa encoding is not None:
        s = s.encode(encoding, 'backslashreplace').decode(encoding)
    andika(s, end=' ')


kundi TarError(Exception):
    """Base exception."""
    pass
kundi ExtractError(TarError):
    """General exception for extract errors."""
    pass
kundi ReadError(TarError):
    """Exception for unreadable tar archives."""
    pass
kundi CompressionError(TarError):
    """Exception for unavailable compression methods."""
    pass
kundi StreamError(TarError):
    """Exception for unsupported operations on stream-like TarFiles."""
    pass
kundi HeaderError(TarError):
    """Base exception for header errors."""
    pass
kundi EmptyHeaderError(HeaderError):
    """Exception for empty headers."""
    pass
kundi TruncatedHeaderError(HeaderError):
    """Exception for truncated headers."""
    pass
kundi EOFHeaderError(HeaderError):
    """Exception for end of file headers."""
    pass
kundi InvalidHeaderError(HeaderError):
    """Exception for invalid headers."""
    pass
kundi SubsequentHeaderError(HeaderError):
    """Exception for missing and invalid extended headers."""
    pass

#---------------------------
# internal stream interface
#---------------------------
kundi _LowLevelFile:
    """Low-level file object. Supports reading and writing.
       It is used instead of a regular file object for streaming
       access.
    """

    eleza __init__(self, name, mode):
        mode = {
            "r": os.O_RDONLY,
            "w": os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        }[mode]
        ikiwa hasattr(os, "O_BINARY"):
            mode |= os.O_BINARY
        self.fd = os.open(name, mode, 0o666)

    eleza close(self):
        os.close(self.fd)

    eleza read(self, size):
        rudisha os.read(self.fd, size)

    eleza write(self, s):
        os.write(self.fd, s)

kundi _Stream:
    """Class that serves as an adapter between TarFile and
       a stream-like object.  The stream-like object only
       needs to have a read() or write() method and is accessed
       blockwise.  Use of gzip or bzip2 compression is possible.
       A stream-like object could be for example: sys.stdin,
       sys.stdout, a socket, a tape device etc.

       _Stream is intended to be used only internally.
    """

    eleza __init__(self, name, mode, comptype, fileobj, bufsize):
        """Construct a _Stream object.
        """
        self._extfileobj = True
        ikiwa fileobj is None:
            fileobj = _LowLevelFile(name, mode)
            self._extfileobj = False

        ikiwa comptype == '*':
            # Enable transparent compression detection for the
            # stream interface
            fileobj = _StreamProxy(fileobj)
            comptype = fileobj.getcomptype()

        self.name     = name or ""
        self.mode     = mode
        self.comptype = comptype
        self.fileobj  = fileobj
        self.bufsize  = bufsize
        self.buf      = b""
        self.pos      = 0
        self.closed   = False

        try:
            ikiwa comptype == "gz":
                try:
                    agiza zlib
                except ImportError:
                    raise CompressionError("zlib module is not available")
                self.zlib = zlib
                self.crc = zlib.crc32(b"")
                ikiwa mode == "r":
                    self._init_read_gz()
                    self.exception = zlib.error
                else:
                    self._init_write_gz()

            elikiwa comptype == "bz2":
                try:
                    agiza bz2
                except ImportError:
                    raise CompressionError("bz2 module is not available")
                ikiwa mode == "r":
                    self.dbuf = b""
                    self.cmp = bz2.BZ2Decompressor()
                    self.exception = OSError
                else:
                    self.cmp = bz2.BZ2Compressor()

            elikiwa comptype == "xz":
                try:
                    agiza lzma
                except ImportError:
                    raise CompressionError("lzma module is not available")
                ikiwa mode == "r":
                    self.dbuf = b""
                    self.cmp = lzma.LZMADecompressor()
                    self.exception = lzma.LZMAError
                else:
                    self.cmp = lzma.LZMACompressor()

            elikiwa comptype != "tar":
                raise CompressionError("unknown compression type %r" % comptype)

        except:
            ikiwa not self._extfileobj:
                self.fileobj.close()
            self.closed = True
            raise

    eleza __del__(self):
        ikiwa hasattr(self, "closed") and not self.closed:
            self.close()

    eleza _init_write_gz(self):
        """Initialize for writing with gzip compression.
        """
        self.cmp = self.zlib.compressobj(9, self.zlib.DEFLATED,
                                            -self.zlib.MAX_WBITS,
                                            self.zlib.DEF_MEM_LEVEL,
                                            0)
        timestamp = struct.pack("<L", int(time.time()))
        self.__write(b"\037\213\010\010" + timestamp + b"\002\377")
        ikiwa self.name.endswith(".gz"):
            self.name = self.name[:-3]
        # RFC1952 says we must use ISO-8859-1 for the FNAME field.
        self.__write(self.name.encode("iso-8859-1", "replace") + NUL)

    eleza write(self, s):
        """Write string s to the stream.
        """
        ikiwa self.comptype == "gz":
            self.crc = self.zlib.crc32(s, self.crc)
        self.pos += len(s)
        ikiwa self.comptype != "tar":
            s = self.cmp.compress(s)
        self.__write(s)

    eleza __write(self, s):
        """Write string s to the stream ikiwa a whole new block
           is ready to be written.
        """
        self.buf += s
        while len(self.buf) > self.bufsize:
            self.fileobj.write(self.buf[:self.bufsize])
            self.buf = self.buf[self.bufsize:]

    eleza close(self):
        """Close the _Stream object. No operation should be
           done on it afterwards.
        """
        ikiwa self.closed:
            return

        self.closed = True
        try:
            ikiwa self.mode == "w" and self.comptype != "tar":
                self.buf += self.cmp.flush()

            ikiwa self.mode == "w" and self.buf:
                self.fileobj.write(self.buf)
                self.buf = b""
                ikiwa self.comptype == "gz":
                    self.fileobj.write(struct.pack("<L", self.crc))
                    self.fileobj.write(struct.pack("<L", self.pos & 0xffffFFFF))
        finally:
            ikiwa not self._extfileobj:
                self.fileobj.close()

    eleza _init_read_gz(self):
        """Initialize for reading a gzip compressed fileobj.
        """
        self.cmp = self.zlib.decompressobj(-self.zlib.MAX_WBITS)
        self.dbuf = b""

        # taken kutoka gzip.GzipFile with some alterations
        ikiwa self.__read(2) != b"\037\213":
            raise ReadError("not a gzip file")
        ikiwa self.__read(1) != b"\010":
            raise CompressionError("unsupported compression method")

        flag = ord(self.__read(1))
        self.__read(6)

        ikiwa flag & 4:
            xlen = ord(self.__read(1)) + 256 * ord(self.__read(1))
            self.read(xlen)
        ikiwa flag & 8:
            while True:
                s = self.__read(1)
                ikiwa not s or s == NUL:
                    break
        ikiwa flag & 16:
            while True:
                s = self.__read(1)
                ikiwa not s or s == NUL:
                    break
        ikiwa flag & 2:
            self.__read(2)

    eleza tell(self):
        """Return the stream's file pointer position.
        """
        rudisha self.pos

    eleza seek(self, pos=0):
        """Set the stream's file pointer to pos. Negative seeking
           is forbidden.
        """
        ikiwa pos - self.pos >= 0:
            blocks, remainder = divmod(pos - self.pos, self.bufsize)
            for i in range(blocks):
                self.read(self.bufsize)
            self.read(remainder)
        else:
            raise StreamError("seeking backwards is not allowed")
        rudisha self.pos

    eleza read(self, size):
        """Return the next size number of bytes kutoka the stream."""
        assert size is not None
        buf = self._read(size)
        self.pos += len(buf)
        rudisha buf

    eleza _read(self, size):
        """Return size bytes kutoka the stream.
        """
        ikiwa self.comptype == "tar":
            rudisha self.__read(size)

        c = len(self.dbuf)
        t = [self.dbuf]
        while c < size:
            # Skip underlying buffer to avoid unaligned double buffering.
            ikiwa self.buf:
                buf = self.buf
                self.buf = b""
            else:
                buf = self.fileobj.read(self.bufsize)
                ikiwa not buf:
                    break
            try:
                buf = self.cmp.decompress(buf)
            except self.exception:
                raise ReadError("invalid compressed data")
            t.append(buf)
            c += len(buf)
        t = b"".join(t)
        self.dbuf = t[size:]
        rudisha t[:size]

    eleza __read(self, size):
        """Return size bytes kutoka stream. If internal buffer is empty,
           read another block kutoka the stream.
        """
        c = len(self.buf)
        t = [self.buf]
        while c < size:
            buf = self.fileobj.read(self.bufsize)
            ikiwa not buf:
                break
            t.append(buf)
            c += len(buf)
        t = b"".join(t)
        self.buf = t[size:]
        rudisha t[:size]
# kundi _Stream

kundi _StreamProxy(object):
    """Small proxy kundi that enables transparent compression
       detection for the Stream interface (mode 'r|*').
    """

    eleza __init__(self, fileobj):
        self.fileobj = fileobj
        self.buf = self.fileobj.read(BLOCKSIZE)

    eleza read(self, size):
        self.read = self.fileobj.read
        rudisha self.buf

    eleza getcomptype(self):
        ikiwa self.buf.startswith(b"\x1f\x8b\x08"):
            rudisha "gz"
        elikiwa self.buf[0:3] == b"BZh" and self.buf[4:10] == b"1AY&SY":
            rudisha "bz2"
        elikiwa self.buf.startswith((b"\x5d\x00\x00\x80", b"\xfd7zXZ")):
            rudisha "xz"
        else:
            rudisha "tar"

    eleza close(self):
        self.fileobj.close()
# kundi StreamProxy

#------------------------
# Extraction file object
#------------------------
kundi _FileInFile(object):
    """A thin wrapper around an existing file object that
       provides a part of its data as an individual file
       object.
    """

    eleza __init__(self, fileobj, offset, size, blockinfo=None):
        self.fileobj = fileobj
        self.offset = offset
        self.size = size
        self.position = 0
        self.name = getattr(fileobj, "name", None)
        self.closed = False

        ikiwa blockinfo is None:
            blockinfo = [(0, size)]

        # Construct a map with data and zero blocks.
        self.map_index = 0
        self.map = []
        lastpos = 0
        realpos = self.offset
        for offset, size in blockinfo:
            ikiwa offset > lastpos:
                self.map.append((False, lastpos, offset, None))
            self.map.append((True, offset, offset + size, realpos))
            realpos += size
            lastpos = offset + size
        ikiwa lastpos < self.size:
            self.map.append((False, lastpos, self.size, None))

    eleza flush(self):
        pass

    eleza readable(self):
        rudisha True

    eleza writable(self):
        rudisha False

    eleza seekable(self):
        rudisha self.fileobj.seekable()

    eleza tell(self):
        """Return the current file position.
        """
        rudisha self.position

    eleza seek(self, position, whence=io.SEEK_SET):
        """Seek to a position in the file.
        """
        ikiwa whence == io.SEEK_SET:
            self.position = min(max(position, 0), self.size)
        elikiwa whence == io.SEEK_CUR:
            ikiwa position < 0:
                self.position = max(self.position + position, 0)
            else:
                self.position = min(self.position + position, self.size)
        elikiwa whence == io.SEEK_END:
            self.position = max(min(self.size + position, self.size), 0)
        else:
            raise ValueError("Invalid argument")
        rudisha self.position

    eleza read(self, size=None):
        """Read data kutoka the file.
        """
        ikiwa size is None:
            size = self.size - self.position
        else:
            size = min(size, self.size - self.position)

        buf = b""
        while size > 0:
            while True:
                data, start, stop, offset = self.map[self.map_index]
                ikiwa start <= self.position < stop:
                    break
                else:
                    self.map_index += 1
                    ikiwa self.map_index == len(self.map):
                        self.map_index = 0
            length = min(size, stop - self.position)
            ikiwa data:
                self.fileobj.seek(offset + (self.position - start))
                b = self.fileobj.read(length)
                ikiwa len(b) != length:
                    raise ReadError("unexpected end of data")
                buf += b
            else:
                buf += NUL * length
            size -= length
            self.position += length
        rudisha buf

    eleza readinto(self, b):
        buf = self.read(len(b))
        b[:len(buf)] = buf
        rudisha len(buf)

    eleza close(self):
        self.closed = True
#kundi _FileInFile

kundi ExFileObject(io.BufferedReader):

    eleza __init__(self, tarfile, tarinfo):
        fileobj = _FileInFile(tarfile.fileobj, tarinfo.offset_data,
                tarinfo.size, tarinfo.sparse)
        super().__init__(fileobj)
#kundi ExFileObject

#------------------
# Exported Classes
#------------------
kundi TarInfo(object):
    """Informational kundi which holds the details about an
       archive member given by a tar header block.
       TarInfo objects are returned by TarFile.getmember(),
       TarFile.getmembers() and TarFile.gettarinfo() and are
       usually created internally.
    """

    __slots__ = dict(
        name = 'Name of the archive member.',
        mode = 'Permission bits.',
        uid = 'User ID of the user who originally stored this member.',
        gid = 'Group ID of the user who originally stored this member.',
        size = 'Size in bytes.',
        mtime = 'Time of last modification.',
        chksum = 'Header checksum.',
        type = ('File type. type is usually one of these constants: '
                'REGTYPE, AREGTYPE, LNKTYPE, SYMTYPE, DIRTYPE, FIFOTYPE, '
                'CONTTYPE, CHRTYPE, BLKTYPE, GNUTYPE_SPARSE.'),
        linkname = ('Name of the target file name, which is only present '
                    'in TarInfo objects of type LNKTYPE and SYMTYPE.'),
        uname = 'User name.',
        gname = 'Group name.',
        devmajor = 'Device major number.',
        devminor = 'Device minor number.',
        offset = 'The tar header starts here.',
        offset_data = "The file's data starts here.",
        pax_headers = ('A dictionary containing key-value pairs of an '
                       'associated pax extended header.'),
        sparse = 'Sparse member information.',
        tarfile = None,
        _sparse_structs = None,
        _link_target = None,
        )

    eleza __init__(self, name=""):
        """Construct a TarInfo object. name is the optional name
           of the member.
        """
        self.name = name        # member name
        self.mode = 0o644       # file permissions
        self.uid = 0            # user id
        self.gid = 0            # group id
        self.size = 0           # file size
        self.mtime = 0          # modification time
        self.chksum = 0         # header checksum
        self.type = REGTYPE     # member type
        self.linkname = ""      # link name
        self.uname = ""         # user name
        self.gname = ""         # group name
        self.devmajor = 0       # device major number
        self.devminor = 0       # device minor number

        self.offset = 0         # the tar header starts here
        self.offset_data = 0    # the file's data starts here

        self.sparse = None      # sparse member information
        self.pax_headers = {}   # pax header information

    @property
    eleza path(self):
        'In pax headers, "name" is called "path".'
        rudisha self.name

    @path.setter
    eleza path(self, name):
        self.name = name

    @property
    eleza linkpath(self):
        'In pax headers, "linkname" is called "linkpath".'
        rudisha self.linkname

    @linkpath.setter
    eleza linkpath(self, linkname):
        self.linkname = linkname

    eleza __repr__(self):
        rudisha "<%s %r at %#x>" % (self.__class__.__name__,self.name,id(self))

    eleza get_info(self):
        """Return the TarInfo's attributes as a dictionary.
        """
        info = {
            "name":     self.name,
            "mode":     self.mode & 0o7777,
            "uid":      self.uid,
            "gid":      self.gid,
            "size":     self.size,
            "mtime":    self.mtime,
            "chksum":   self.chksum,
            "type":     self.type,
            "linkname": self.linkname,
            "uname":    self.uname,
            "gname":    self.gname,
            "devmajor": self.devmajor,
            "devminor": self.devminor
        }

        ikiwa info["type"] == DIRTYPE and not info["name"].endswith("/"):
            info["name"] += "/"

        rudisha info

    eleza tobuf(self, format=DEFAULT_FORMAT, encoding=ENCODING, errors="surrogateescape"):
        """Return a tar header as a string of 512 byte blocks.
        """
        info = self.get_info()

        ikiwa format == USTAR_FORMAT:
            rudisha self.create_ustar_header(info, encoding, errors)
        elikiwa format == GNU_FORMAT:
            rudisha self.create_gnu_header(info, encoding, errors)
        elikiwa format == PAX_FORMAT:
            rudisha self.create_pax_header(info, encoding)
        else:
            raise ValueError("invalid format")

    eleza create_ustar_header(self, info, encoding, errors):
        """Return the object as a ustar header block.
        """
        info["magic"] = POSIX_MAGIC

        ikiwa len(info["linkname"].encode(encoding, errors)) > LENGTH_LINK:
            raise ValueError("linkname is too long")

        ikiwa len(info["name"].encode(encoding, errors)) > LENGTH_NAME:
            info["prefix"], info["name"] = self._posix_split_name(info["name"], encoding, errors)

        rudisha self._create_header(info, USTAR_FORMAT, encoding, errors)

    eleza create_gnu_header(self, info, encoding, errors):
        """Return the object as a GNU header block sequence.
        """
        info["magic"] = GNU_MAGIC

        buf = b""
        ikiwa len(info["linkname"].encode(encoding, errors)) > LENGTH_LINK:
            buf += self._create_gnu_long_header(info["linkname"], GNUTYPE_LONGLINK, encoding, errors)

        ikiwa len(info["name"].encode(encoding, errors)) > LENGTH_NAME:
            buf += self._create_gnu_long_header(info["name"], GNUTYPE_LONGNAME, encoding, errors)

        rudisha buf + self._create_header(info, GNU_FORMAT, encoding, errors)

    eleza create_pax_header(self, info, encoding):
        """Return the object as a ustar header block. If it cannot be
           represented this way, prepend a pax extended header sequence
           with supplement information.
        """
        info["magic"] = POSIX_MAGIC
        pax_headers = self.pax_headers.copy()

        # Test string fields for values that exceed the field length or cannot
        # be represented in ASCII encoding.
        for name, hname, length in (
                ("name", "path", LENGTH_NAME), ("linkname", "linkpath", LENGTH_LINK),
                ("uname", "uname", 32), ("gname", "gname", 32)):

            ikiwa hname in pax_headers:
                # The pax header has priority.
                continue

            # Try to encode the string as ASCII.
            try:
                info[name].encode("ascii", "strict")
            except UnicodeEncodeError:
                pax_headers[hname] = info[name]
                continue

            ikiwa len(info[name]) > length:
                pax_headers[hname] = info[name]

        # Test number fields for values that exceed the field limit or values
        # that like to be stored as float.
        for name, digits in (("uid", 8), ("gid", 8), ("size", 12), ("mtime", 12)):
            ikiwa name in pax_headers:
                # The pax header has priority. Avoid overflow.
                info[name] = 0
                continue

            val = info[name]
            ikiwa not 0 <= val < 8 ** (digits - 1) or isinstance(val, float):
                pax_headers[name] = str(val)
                info[name] = 0

        # Create a pax extended header ikiwa necessary.
        ikiwa pax_headers:
            buf = self._create_pax_generic_header(pax_headers, XHDTYPE, encoding)
        else:
            buf = b""

        rudisha buf + self._create_header(info, USTAR_FORMAT, "ascii", "replace")

    @classmethod
    eleza create_pax_global_header(cls, pax_headers):
        """Return the object as a pax global header block sequence.
        """
        rudisha cls._create_pax_generic_header(pax_headers, XGLTYPE, "utf-8")

    eleza _posix_split_name(self, name, encoding, errors):
        """Split a name longer than 100 chars into a prefix
           and a name part.
        """
        components = name.split("/")
        for i in range(1, len(components)):
            prefix = "/".join(components[:i])
            name = "/".join(components[i:])
            ikiwa len(prefix.encode(encoding, errors)) <= LENGTH_PREFIX and \
                    len(name.encode(encoding, errors)) <= LENGTH_NAME:
                break
        else:
            raise ValueError("name is too long")

        rudisha prefix, name

    @staticmethod
    eleza _create_header(info, format, encoding, errors):
        """Return a header block. info is a dictionary with file
           information, format must be one of the *_FORMAT constants.
        """
        parts = [
            stn(info.get("name", ""), 100, encoding, errors),
            itn(info.get("mode", 0) & 0o7777, 8, format),
            itn(info.get("uid", 0), 8, format),
            itn(info.get("gid", 0), 8, format),
            itn(info.get("size", 0), 12, format),
            itn(info.get("mtime", 0), 12, format),
            b"        ", # checksum field
            info.get("type", REGTYPE),
            stn(info.get("linkname", ""), 100, encoding, errors),
            info.get("magic", POSIX_MAGIC),
            stn(info.get("uname", ""), 32, encoding, errors),
            stn(info.get("gname", ""), 32, encoding, errors),
            itn(info.get("devmajor", 0), 8, format),
            itn(info.get("devminor", 0), 8, format),
            stn(info.get("prefix", ""), 155, encoding, errors)
        ]

        buf = struct.pack("%ds" % BLOCKSIZE, b"".join(parts))
        chksum = calc_chksums(buf[-BLOCKSIZE:])[0]
        buf = buf[:-364] + bytes("%06o\0" % chksum, "ascii") + buf[-357:]
        rudisha buf

    @staticmethod
    eleza _create_payload(payload):
        """Return the string payload filled with zero bytes
           up to the next 512 byte border.
        """
        blocks, remainder = divmod(len(payload), BLOCKSIZE)
        ikiwa remainder > 0:
            payload += (BLOCKSIZE - remainder) * NUL
        rudisha payload

    @classmethod
    eleza _create_gnu_long_header(cls, name, type, encoding, errors):
        """Return a GNUTYPE_LONGNAME or GNUTYPE_LONGLINK sequence
           for name.
        """
        name = name.encode(encoding, errors) + NUL

        info = {}
        info["name"] = "././@LongLink"
        info["type"] = type
        info["size"] = len(name)
        info["magic"] = GNU_MAGIC

        # create extended header + name blocks.
        rudisha cls._create_header(info, USTAR_FORMAT, encoding, errors) + \
                cls._create_payload(name)

    @classmethod
    eleza _create_pax_generic_header(cls, pax_headers, type, encoding):
        """Return a POSIX.1-2008 extended or global header sequence
           that contains a list of keyword, value pairs. The values
           must be strings.
        """
        # Check ikiwa one of the fields contains surrogate characters and thereby
        # forces hdrcharset=BINARY, see _proc_pax() for more information.
        binary = False
        for keyword, value in pax_headers.items():
            try:
                value.encode("utf-8", "strict")
            except UnicodeEncodeError:
                binary = True
                break

        records = b""
        ikiwa binary:
            # Put the hdrcharset field at the beginning of the header.
            records += b"21 hdrcharset=BINARY\n"

        for keyword, value in pax_headers.items():
            keyword = keyword.encode("utf-8")
            ikiwa binary:
                # Try to restore the original byte representation of `value'.
                # Needless to say, that the encoding must match the string.
                value = value.encode(encoding, "surrogateescape")
            else:
                value = value.encode("utf-8")

            l = len(keyword) + len(value) + 3   # ' ' + '=' + '\n'
            n = p = 0
            while True:
                n = l + len(str(p))
                ikiwa n == p:
                    break
                p = n
            records += bytes(str(p), "ascii") + b" " + keyword + b"=" + value + b"\n"

        # We use a hardcoded "././@PaxHeader" name like star does
        # instead of the one that POSIX recommends.
        info = {}
        info["name"] = "././@PaxHeader"
        info["type"] = type
        info["size"] = len(records)
        info["magic"] = POSIX_MAGIC

        # Create pax header + record blocks.
        rudisha cls._create_header(info, USTAR_FORMAT, "ascii", "replace") + \
                cls._create_payload(records)

    @classmethod
    eleza kutokabuf(cls, buf, encoding, errors):
        """Construct a TarInfo object kutoka a 512 byte bytes object.
        """
        ikiwa len(buf) == 0:
            raise EmptyHeaderError("empty header")
        ikiwa len(buf) != BLOCKSIZE:
            raise TruncatedHeaderError("truncated header")
        ikiwa buf.count(NUL) == BLOCKSIZE:
            raise EOFHeaderError("end of file header")

        chksum = nti(buf[148:156])
        ikiwa chksum not in calc_chksums(buf):
            raise InvalidHeaderError("bad checksum")

        obj = cls()
        obj.name = nts(buf[0:100], encoding, errors)
        obj.mode = nti(buf[100:108])
        obj.uid = nti(buf[108:116])
        obj.gid = nti(buf[116:124])
        obj.size = nti(buf[124:136])
        obj.mtime = nti(buf[136:148])
        obj.chksum = chksum
        obj.type = buf[156:157]
        obj.linkname = nts(buf[157:257], encoding, errors)
        obj.uname = nts(buf[265:297], encoding, errors)
        obj.gname = nts(buf[297:329], encoding, errors)
        obj.devmajor = nti(buf[329:337])
        obj.devminor = nti(buf[337:345])
        prefix = nts(buf[345:500], encoding, errors)

        # Old V7 tar format represents a directory as a regular
        # file with a trailing slash.
        ikiwa obj.type == AREGTYPE and obj.name.endswith("/"):
            obj.type = DIRTYPE

        # The old GNU sparse format occupies some of the unused
        # space in the buffer for up to 4 sparse structures.
        # Save them for later processing in _proc_sparse().
        ikiwa obj.type == GNUTYPE_SPARSE:
            pos = 386
            structs = []
            for i in range(4):
                try:
                    offset = nti(buf[pos:pos + 12])
                    numbytes = nti(buf[pos + 12:pos + 24])
                except ValueError:
                    break
                structs.append((offset, numbytes))
                pos += 24
            isextended = bool(buf[482])
            origsize = nti(buf[483:495])
            obj._sparse_structs = (structs, isextended, origsize)

        # Remove redundant slashes kutoka directories.
        ikiwa obj.isdir():
            obj.name = obj.name.rstrip("/")

        # Reconstruct a ustar longname.
        ikiwa prefix and obj.type not in GNU_TYPES:
            obj.name = prefix + "/" + obj.name
        rudisha obj

    @classmethod
    eleza kutokatarfile(cls, tarfile):
        """Return the next TarInfo object kutoka TarFile object
           tarfile.
        """
        buf = tarfile.fileobj.read(BLOCKSIZE)
        obj = cls.kutokabuf(buf, tarfile.encoding, tarfile.errors)
        obj.offset = tarfile.fileobj.tell() - BLOCKSIZE
        rudisha obj._proc_member(tarfile)

    #--------------------------------------------------------------------------
    # The following are methods that are called depending on the type of a
    # member. The entry point is _proc_member() which can be overridden in a
    # subkundi to add custom _proc_*() methods. A _proc_*() method MUST
    # implement the following
    # operations:
    # 1. Set self.offset_data to the position where the data blocks begin,
    #    ikiwa there is data that follows.
    # 2. Set tarfile.offset to the position where the next member's header will
    #    begin.
    # 3. Return self or another valid TarInfo object.
    eleza _proc_member(self, tarfile):
        """Choose the right processing method depending on
           the type and call it.
        """
        ikiwa self.type in (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK):
            rudisha self._proc_gnulong(tarfile)
        elikiwa self.type == GNUTYPE_SPARSE:
            rudisha self._proc_sparse(tarfile)
        elikiwa self.type in (XHDTYPE, XGLTYPE, SOLARIS_XHDTYPE):
            rudisha self._proc_pax(tarfile)
        else:
            rudisha self._proc_builtin(tarfile)

    eleza _proc_builtin(self, tarfile):
        """Process a builtin type or an unknown type which
           will be treated as a regular file.
        """
        self.offset_data = tarfile.fileobj.tell()
        offset = self.offset_data
        ikiwa self.isreg() or self.type not in SUPPORTED_TYPES:
            # Skip the following data blocks.
            offset += self._block(self.size)
        tarfile.offset = offset

        # Patch the TarInfo object with saved global
        # header information.
        self._apply_pax_info(tarfile.pax_headers, tarfile.encoding, tarfile.errors)

        rudisha self

    eleza _proc_gnulong(self, tarfile):
        """Process the blocks that hold a GNU longname
           or longlink member.
        """
        buf = tarfile.fileobj.read(self._block(self.size))

        # Fetch the next header and process it.
        try:
            next = self.kutokatarfile(tarfile)
        except HeaderError:
            raise SubsequentHeaderError("missing or bad subsequent header")

        # Patch the TarInfo object kutoka the next header with
        # the longname information.
        next.offset = self.offset
        ikiwa self.type == GNUTYPE_LONGNAME:
            next.name = nts(buf, tarfile.encoding, tarfile.errors)
        elikiwa self.type == GNUTYPE_LONGLINK:
            next.linkname = nts(buf, tarfile.encoding, tarfile.errors)

        rudisha next

    eleza _proc_sparse(self, tarfile):
        """Process a GNU sparse header plus extra headers.
        """
        # We already collected some sparse structures in kutokabuf().
        structs, isextended, origsize = self._sparse_structs
        del self._sparse_structs

        # Collect sparse structures kutoka extended header blocks.
        while isextended:
            buf = tarfile.fileobj.read(BLOCKSIZE)
            pos = 0
            for i in range(21):
                try:
                    offset = nti(buf[pos:pos + 12])
                    numbytes = nti(buf[pos + 12:pos + 24])
                except ValueError:
                    break
                ikiwa offset and numbytes:
                    structs.append((offset, numbytes))
                pos += 24
            isextended = bool(buf[504])
        self.sparse = structs

        self.offset_data = tarfile.fileobj.tell()
        tarfile.offset = self.offset_data + self._block(self.size)
        self.size = origsize
        rudisha self

    eleza _proc_pax(self, tarfile):
        """Process an extended or global header as described in
           POSIX.1-2008.
        """
        # Read the header information.
        buf = tarfile.fileobj.read(self._block(self.size))

        # A pax header stores supplemental information for either
        # the following file (extended) or all following files
        # (global).
        ikiwa self.type == XGLTYPE:
            pax_headers = tarfile.pax_headers
        else:
            pax_headers = tarfile.pax_headers.copy()

        # Check ikiwa the pax header contains a hdrcharset field. This tells us
        # the encoding of the path, linkpath, uname and gname fields. Normally,
        # these fields are UTF-8 encoded but since POSIX.1-2008 tar
        # implementations are allowed to store them as raw binary strings if
        # the translation to UTF-8 fails.
        match = re.search(br"\d+ hdrcharset=([^\n]+)\n", buf)
        ikiwa match is not None:
            pax_headers["hdrcharset"] = match.group(1).decode("utf-8")

        # For the time being, we don't care about anything other than "BINARY".
        # The only other value that is currently allowed by the standard is
        # "ISO-IR 10646 2000 UTF-8" in other words UTF-8.
        hdrcharset = pax_headers.get("hdrcharset")
        ikiwa hdrcharset == "BINARY":
            encoding = tarfile.encoding
        else:
            encoding = "utf-8"

        # Parse pax header information. A record looks like that:
        # "%d %s=%s\n" % (length, keyword, value). length is the size
        # of the complete record including the length field itself and
        # the newline. keyword and value are both UTF-8 encoded strings.
        regex = re.compile(br"(\d+) ([^=]+)=")
        pos = 0
        while True:
            match = regex.match(buf, pos)
            ikiwa not match:
                break

            length, keyword = match.groups()
            length = int(length)
            value = buf[match.end(2) + 1:match.start(1) + length - 1]

            # Normally, we could just use "utf-8" as the encoding and "strict"
            # as the error handler, but we better not take the risk. For
            # example, GNU tar <= 1.23 is known to store filenames it cannot
            # translate to UTF-8 as raw strings (unfortunately without a
            # hdrcharset=BINARY header).
            # We first try the strict standard encoding, and ikiwa that fails we
            # fall back on the user's encoding and error handler.
            keyword = self._decode_pax_field(keyword, "utf-8", "utf-8",
                    tarfile.errors)
            ikiwa keyword in PAX_NAME_FIELDS:
                value = self._decode_pax_field(value, encoding, tarfile.encoding,
                        tarfile.errors)
            else:
                value = self._decode_pax_field(value, "utf-8", "utf-8",
                        tarfile.errors)

            pax_headers[keyword] = value
            pos += length

        # Fetch the next header.
        try:
            next = self.kutokatarfile(tarfile)
        except HeaderError:
            raise SubsequentHeaderError("missing or bad subsequent header")

        # Process GNU sparse information.
        ikiwa "GNU.sparse.map" in pax_headers:
            # GNU extended sparse format version 0.1.
            self._proc_gnusparse_01(next, pax_headers)

        elikiwa "GNU.sparse.size" in pax_headers:
            # GNU extended sparse format version 0.0.
            self._proc_gnusparse_00(next, pax_headers, buf)

        elikiwa pax_headers.get("GNU.sparse.major") == "1" and pax_headers.get("GNU.sparse.minor") == "0":
            # GNU extended sparse format version 1.0.
            self._proc_gnusparse_10(next, pax_headers, tarfile)

        ikiwa self.type in (XHDTYPE, SOLARIS_XHDTYPE):
            # Patch the TarInfo object with the extended header info.
            next._apply_pax_info(pax_headers, tarfile.encoding, tarfile.errors)
            next.offset = self.offset

            ikiwa "size" in pax_headers:
                # If the extended header replaces the size field,
                # we need to recalculate the offset where the next
                # header starts.
                offset = next.offset_data
                ikiwa next.isreg() or next.type not in SUPPORTED_TYPES:
                    offset += next._block(next.size)
                tarfile.offset = offset

        rudisha next

    eleza _proc_gnusparse_00(self, next, pax_headers, buf):
        """Process a GNU tar extended sparse header, version 0.0.
        """
        offsets = []
        for match in re.finditer(br"\d+ GNU.sparse.offset=(\d+)\n", buf):
            offsets.append(int(match.group(1)))
        numbytes = []
        for match in re.finditer(br"\d+ GNU.sparse.numbytes=(\d+)\n", buf):
            numbytes.append(int(match.group(1)))
        next.sparse = list(zip(offsets, numbytes))

    eleza _proc_gnusparse_01(self, next, pax_headers):
        """Process a GNU tar extended sparse header, version 0.1.
        """
        sparse = [int(x) for x in pax_headers["GNU.sparse.map"].split(",")]
        next.sparse = list(zip(sparse[::2], sparse[1::2]))

    eleza _proc_gnusparse_10(self, next, pax_headers, tarfile):
        """Process a GNU tar extended sparse header, version 1.0.
        """
        fields = None
        sparse = []
        buf = tarfile.fileobj.read(BLOCKSIZE)
        fields, buf = buf.split(b"\n", 1)
        fields = int(fields)
        while len(sparse) < fields * 2:
            ikiwa b"\n" not in buf:
                buf += tarfile.fileobj.read(BLOCKSIZE)
            number, buf = buf.split(b"\n", 1)
            sparse.append(int(number))
        next.offset_data = tarfile.fileobj.tell()
        next.sparse = list(zip(sparse[::2], sparse[1::2]))

    eleza _apply_pax_info(self, pax_headers, encoding, errors):
        """Replace fields with supplemental information kutoka a previous
           pax extended or global header.
        """
        for keyword, value in pax_headers.items():
            ikiwa keyword == "GNU.sparse.name":
                setattr(self, "path", value)
            elikiwa keyword == "GNU.sparse.size":
                setattr(self, "size", int(value))
            elikiwa keyword == "GNU.sparse.realsize":
                setattr(self, "size", int(value))
            elikiwa keyword in PAX_FIELDS:
                ikiwa keyword in PAX_NUMBER_FIELDS:
                    try:
                        value = PAX_NUMBER_FIELDS[keyword](value)
                    except ValueError:
                        value = 0
                ikiwa keyword == "path":
                    value = value.rstrip("/")
                setattr(self, keyword, value)

        self.pax_headers = pax_headers.copy()

    eleza _decode_pax_field(self, value, encoding, fallback_encoding, fallback_errors):
        """Decode a single field kutoka a pax record.
        """
        try:
            rudisha value.decode(encoding, "strict")
        except UnicodeDecodeError:
            rudisha value.decode(fallback_encoding, fallback_errors)

    eleza _block(self, count):
        """Round up a byte count by BLOCKSIZE and rudisha it,
           e.g. _block(834) => 1024.
        """
        blocks, remainder = divmod(count, BLOCKSIZE)
        ikiwa remainder:
            blocks += 1
        rudisha blocks * BLOCKSIZE

    eleza isreg(self):
        'Return True ikiwa the Tarinfo object is a regular file.'
        rudisha self.type in REGULAR_TYPES

    eleza isfile(self):
        'Return True ikiwa the Tarinfo object is a regular file.'
        rudisha self.isreg()

    eleza isdir(self):
        'Return True ikiwa it is a directory.'
        rudisha self.type == DIRTYPE

    eleza issym(self):
        'Return True ikiwa it is a symbolic link.'
        rudisha self.type == SYMTYPE

    eleza islnk(self):
        'Return True ikiwa it is a hard link.'
        rudisha self.type == LNKTYPE

    eleza ischr(self):
        'Return True ikiwa it is a character device.'
        rudisha self.type == CHRTYPE

    eleza isblk(self):
        'Return True ikiwa it is a block device.'
        rudisha self.type == BLKTYPE

    eleza isfifo(self):
        'Return True ikiwa it is a FIFO.'
        rudisha self.type == FIFOTYPE

    eleza issparse(self):
        rudisha self.sparse is not None

    eleza isdev(self):
        'Return True ikiwa it is one of character device, block device or FIFO.'
        rudisha self.type in (CHRTYPE, BLKTYPE, FIFOTYPE)
# kundi TarInfo

kundi TarFile(object):
    """The TarFile Class provides an interface to tar archives.
    """

    debug = 0                   # May be set kutoka 0 (no msgs) to 3 (all msgs)

    dereference = False         # If true, add content of linked file to the
                                # tar file, else the link.

    ignore_zeros = False        # If true, skips empty or invalid blocks and
                                # continues processing.

    errorlevel = 1              # If 0, fatal errors only appear in debug
                                # messages (ikiwa debug >= 0). If > 0, errors
                                # are passed to the caller as exceptions.

    format = DEFAULT_FORMAT     # The format to use when creating an archive.

    encoding = ENCODING         # Encoding for 8-bit character strings.

    errors = None               # Error handler for unicode conversion.

    tarinfo = TarInfo           # The default TarInfo kundi to use.

    fileobject = ExFileObject   # The file-object for extractfile().

    eleza __init__(self, name=None, mode="r", fileobj=None, format=None,
            tarinfo=None, dereference=None, ignore_zeros=None, encoding=None,
            errors="surrogateescape", pax_headers=None, debug=None,
            errorlevel=None, copybufsize=None):
        """Open an (uncompressed) tar archive `name'. `mode' is either 'r' to
           read kutoka an existing archive, 'a' to append data to an existing
           file or 'w' to create a new file overwriting an existing one. `mode'
           defaults to 'r'.
           If `fileobj' is given, it is used for reading or writing data. If it
           can be determined, `mode' is overridden by `fileobj's mode.
           `fileobj' is not closed, when TarFile is closed.
        """
        modes = {"r": "rb", "a": "r+b", "w": "wb", "x": "xb"}
        ikiwa mode not in modes:
            raise ValueError("mode must be 'r', 'a', 'w' or 'x'")
        self.mode = mode
        self._mode = modes[mode]

        ikiwa not fileobj:
            ikiwa self.mode == "a" and not os.path.exists(name):
                # Create nonexistent files in append mode.
                self.mode = "w"
                self._mode = "wb"
            fileobj = bltn_open(name, self._mode)
            self._extfileobj = False
        else:
            ikiwa (name is None and hasattr(fileobj, "name") and
                isinstance(fileobj.name, (str, bytes))):
                name = fileobj.name
            ikiwa hasattr(fileobj, "mode"):
                self._mode = fileobj.mode
            self._extfileobj = True
        self.name = os.path.abspath(name) ikiwa name else None
        self.fileobj = fileobj

        # Init attributes.
        ikiwa format is not None:
            self.format = format
        ikiwa tarinfo is not None:
            self.tarinfo = tarinfo
        ikiwa dereference is not None:
            self.dereference = dereference
        ikiwa ignore_zeros is not None:
            self.ignore_zeros = ignore_zeros
        ikiwa encoding is not None:
            self.encoding = encoding
        self.errors = errors

        ikiwa pax_headers is not None and self.format == PAX_FORMAT:
            self.pax_headers = pax_headers
        else:
            self.pax_headers = {}

        ikiwa debug is not None:
            self.debug = debug
        ikiwa errorlevel is not None:
            self.errorlevel = errorlevel

        # Init datastructures.
        self.copybufsize = copybufsize
        self.closed = False
        self.members = []       # list of members as TarInfo objects
        self._loaded = False    # flag ikiwa all members have been read
        self.offset = self.fileobj.tell()
                                # current position in the archive file
        self.inodes = {}        # dictionary caching the inodes of
                                # archive members already added

        try:
            ikiwa self.mode == "r":
                self.firstmember = None
                self.firstmember = self.next()

            ikiwa self.mode == "a":
                # Move to the end of the archive,
                # before the first empty block.
                while True:
                    self.fileobj.seek(self.offset)
                    try:
                        tarinfo = self.tarinfo.kutokatarfile(self)
                        self.members.append(tarinfo)
                    except EOFHeaderError:
                        self.fileobj.seek(self.offset)
                        break
                    except HeaderError as e:
                        raise ReadError(str(e))

            ikiwa self.mode in ("a", "w", "x"):
                self._loaded = True

                ikiwa self.pax_headers:
                    buf = self.tarinfo.create_pax_global_header(self.pax_headers.copy())
                    self.fileobj.write(buf)
                    self.offset += len(buf)
        except:
            ikiwa not self._extfileobj:
                self.fileobj.close()
            self.closed = True
            raise

    #--------------------------------------------------------------------------
    # Below are the classmethods which act as alternate constructors to the
    # TarFile class. The open() method is the only one that is needed for
    # public use; it is the "super"-constructor and is able to select an
    # adequate "sub"-constructor for a particular compression using the mapping
    # kutoka OPEN_METH.
    #
    # This concept allows one to subkundi TarFile without losing the comfort of
    # the super-constructor. A sub-constructor is registered and made available
    # by adding it to the mapping in OPEN_METH.

    @classmethod
    eleza open(cls, name=None, mode="r", fileobj=None, bufsize=RECORDSIZE, **kwargs):
        """Open a tar archive for reading, writing or appending. Return
           an appropriate TarFile class.

           mode:
           'r' or 'r:*' open for reading with transparent compression
           'r:'         open for reading exclusively uncompressed
           'r:gz'       open for reading with gzip compression
           'r:bz2'      open for reading with bzip2 compression
           'r:xz'       open for reading with lzma compression
           'a' or 'a:'  open for appending, creating the file ikiwa necessary
           'w' or 'w:'  open for writing without compression
           'w:gz'       open for writing with gzip compression
           'w:bz2'      open for writing with bzip2 compression
           'w:xz'       open for writing with lzma compression

           'x' or 'x:'  create a tarfile exclusively without compression, raise
                        an exception ikiwa the file is already created
           'x:gz'       create a gzip compressed tarfile, raise an exception
                        ikiwa the file is already created
           'x:bz2'      create a bzip2 compressed tarfile, raise an exception
                        ikiwa the file is already created
           'x:xz'       create an lzma compressed tarfile, raise an exception
                        ikiwa the file is already created

           'r|*'        open a stream of tar blocks with transparent compression
           'r|'         open an uncompressed stream of tar blocks for reading
           'r|gz'       open a gzip compressed stream of tar blocks
           'r|bz2'      open a bzip2 compressed stream of tar blocks
           'r|xz'       open an lzma compressed stream of tar blocks
           'w|'         open an uncompressed stream for writing
           'w|gz'       open a gzip compressed stream for writing
           'w|bz2'      open a bzip2 compressed stream for writing
           'w|xz'       open an lzma compressed stream for writing
        """

        ikiwa not name and not fileobj:
            raise ValueError("nothing to open")

        ikiwa mode in ("r", "r:*"):
            # Find out which *open() is appropriate for opening the file.
            eleza not_compressed(comptype):
                rudisha cls.OPEN_METH[comptype] == 'taropen'
            for comptype in sorted(cls.OPEN_METH, key=not_compressed):
                func = getattr(cls, cls.OPEN_METH[comptype])
                ikiwa fileobj is not None:
                    saved_pos = fileobj.tell()
                try:
                    rudisha func(name, "r", fileobj, **kwargs)
                except (ReadError, CompressionError):
                    ikiwa fileobj is not None:
                        fileobj.seek(saved_pos)
                    continue
            raise ReadError("file could not be opened successfully")

        elikiwa ":" in mode:
            filemode, comptype = mode.split(":", 1)
            filemode = filemode or "r"
            comptype = comptype or "tar"

            # Select the *open() function according to
            # given compression.
            ikiwa comptype in cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
            else:
                raise CompressionError("unknown compression type %r" % comptype)
            rudisha func(name, filemode, fileobj, **kwargs)

        elikiwa "|" in mode:
            filemode, comptype = mode.split("|", 1)
            filemode = filemode or "r"
            comptype = comptype or "tar"

            ikiwa filemode not in ("r", "w"):
                raise ValueError("mode must be 'r' or 'w'")

            stream = _Stream(name, filemode, comptype, fileobj, bufsize)
            try:
                t = cls(name, filemode, stream, **kwargs)
            except:
                stream.close()
                raise
            t._extfileobj = False
            rudisha t

        elikiwa mode in ("a", "w", "x"):
            rudisha cls.taropen(name, mode, fileobj, **kwargs)

        raise ValueError("undiscernible mode")

    @classmethod
    eleza taropen(cls, name, mode="r", fileobj=None, **kwargs):
        """Open uncompressed tar archive name for reading or writing.
        """
        ikiwa mode not in ("r", "a", "w", "x"):
            raise ValueError("mode must be 'r', 'a', 'w' or 'x'")
        rudisha cls(name, mode, fileobj, **kwargs)

    @classmethod
    eleza gzopen(cls, name, mode="r", fileobj=None, compresslevel=9, **kwargs):
        """Open gzip compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        ikiwa mode not in ("r", "w", "x"):
            raise ValueError("mode must be 'r', 'w' or 'x'")

        try:
            agiza gzip
            gzip.GzipFile
        except (ImportError, AttributeError):
            raise CompressionError("gzip module is not available")

        try:
            fileobj = gzip.GzipFile(name, mode + "b", compresslevel, fileobj)
        except OSError:
            ikiwa fileobj is not None and mode == 'r':
                raise ReadError("not a gzip file")
            raise

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except OSError:
            fileobj.close()
            ikiwa mode == 'r':
                raise ReadError("not a gzip file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        rudisha t

    @classmethod
    eleza bz2open(cls, name, mode="r", fileobj=None, compresslevel=9, **kwargs):
        """Open bzip2 compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        ikiwa mode not in ("r", "w", "x"):
            raise ValueError("mode must be 'r', 'w' or 'x'")

        try:
            agiza bz2
        except ImportError:
            raise CompressionError("bz2 module is not available")

        fileobj = bz2.BZ2File(fileobj or name, mode,
                              compresslevel=compresslevel)

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except (OSError, EOFError):
            fileobj.close()
            ikiwa mode == 'r':
                raise ReadError("not a bzip2 file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        rudisha t

    @classmethod
    eleza xzopen(cls, name, mode="r", fileobj=None, preset=None, **kwargs):
        """Open lzma compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        ikiwa mode not in ("r", "w", "x"):
            raise ValueError("mode must be 'r', 'w' or 'x'")

        try:
            agiza lzma
        except ImportError:
            raise CompressionError("lzma module is not available")

        fileobj = lzma.LZMAFile(fileobj or name, mode, preset=preset)

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except (lzma.LZMAError, EOFError):
            fileobj.close()
            ikiwa mode == 'r':
                raise ReadError("not an lzma file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        rudisha t

    # All *open() methods are registered here.
    OPEN_METH = {
        "tar": "taropen",   # uncompressed tar
        "gz":  "gzopen",    # gzip compressed tar
        "bz2": "bz2open",   # bzip2 compressed tar
        "xz":  "xzopen"     # lzma compressed tar
    }

    #--------------------------------------------------------------------------
    # The public methods which TarFile provides:

    eleza close(self):
        """Close the TarFile. In write-mode, two finishing zero blocks are
           appended to the archive.
        """
        ikiwa self.closed:
            return

        self.closed = True
        try:
            ikiwa self.mode in ("a", "w", "x"):
                self.fileobj.write(NUL * (BLOCKSIZE * 2))
                self.offset += (BLOCKSIZE * 2)
                # fill up the end with zero-blocks
                # (like option -b20 for tar does)
                blocks, remainder = divmod(self.offset, RECORDSIZE)
                ikiwa remainder > 0:
                    self.fileobj.write(NUL * (RECORDSIZE - remainder))
        finally:
            ikiwa not self._extfileobj:
                self.fileobj.close()

    eleza getmember(self, name):
        """Return a TarInfo object for member `name'. If `name' can not be
           found in the archive, KeyError is raised. If a member occurs more
           than once in the archive, its last occurrence is assumed to be the
           most up-to-date version.
        """
        tarinfo = self._getmember(name)
        ikiwa tarinfo is None:
            raise KeyError("filename %r not found" % name)
        rudisha tarinfo

    eleza getmembers(self):
        """Return the members of the archive as a list of TarInfo objects. The
           list has the same order as the members in the archive.
        """
        self._check()
        ikiwa not self._loaded:    # ikiwa we want to obtain a list of
            self._load()        # all members, we first have to
                                # scan the whole archive.
        rudisha self.members

    eleza getnames(self):
        """Return the members of the archive as a list of their names. It has
           the same order as the list returned by getmembers().
        """
        rudisha [tarinfo.name for tarinfo in self.getmembers()]

    eleza gettarinfo(self, name=None, arcname=None, fileobj=None):
        """Create a TarInfo object kutoka the result of os.stat or equivalent
           on an existing file. The file is either named by `name', or
           specified as a file object `fileobj' with a file descriptor. If
           given, `arcname' specifies an alternative name for the file in the
           archive, otherwise, the name is taken kutoka the 'name' attribute of
           'fileobj', or the 'name' argument. The name should be a text
           string.
        """
        self._check("awx")

        # When fileobj is given, replace name by
        # fileobj's real name.
        ikiwa fileobj is not None:
            name = fileobj.name

        # Building the name of the member in the archive.
        # Backward slashes are converted to forward slashes,
        # Absolute paths are turned to relative paths.
        ikiwa arcname is None:
            arcname = name
        drv, arcname = os.path.splitdrive(arcname)
        arcname = arcname.replace(os.sep, "/")
        arcname = arcname.lstrip("/")

        # Now, fill the TarInfo object with
        # information specific for the file.
        tarinfo = self.tarinfo()
        tarinfo.tarfile = self  # Not needed

        # Use os.stat or os.lstat, depending on ikiwa symlinks shall be resolved.
        ikiwa fileobj is None:
            ikiwa not self.dereference:
                statres = os.lstat(name)
            else:
                statres = os.stat(name)
        else:
            statres = os.fstat(fileobj.fileno())
        linkname = ""

        stmd = statres.st_mode
        ikiwa stat.S_ISREG(stmd):
            inode = (statres.st_ino, statres.st_dev)
            ikiwa not self.dereference and statres.st_nlink > 1 and \
                    inode in self.inodes and arcname != self.inodes[inode]:
                # Is it a hardlink to an already
                # archived file?
                type = LNKTYPE
                linkname = self.inodes[inode]
            else:
                # The inode is added only ikiwa its valid.
                # For win32 it is always 0.
                type = REGTYPE
                ikiwa inode[0]:
                    self.inodes[inode] = arcname
        elikiwa stat.S_ISDIR(stmd):
            type = DIRTYPE
        elikiwa stat.S_ISFIFO(stmd):
            type = FIFOTYPE
        elikiwa stat.S_ISLNK(stmd):
            type = SYMTYPE
            linkname = os.readlink(name)
        elikiwa stat.S_ISCHR(stmd):
            type = CHRTYPE
        elikiwa stat.S_ISBLK(stmd):
            type = BLKTYPE
        else:
            rudisha None

        # Fill the TarInfo object with all
        # information we can get.
        tarinfo.name = arcname
        tarinfo.mode = stmd
        tarinfo.uid = statres.st_uid
        tarinfo.gid = statres.st_gid
        ikiwa type == REGTYPE:
            tarinfo.size = statres.st_size
        else:
            tarinfo.size = 0
        tarinfo.mtime = statres.st_mtime
        tarinfo.type = type
        tarinfo.linkname = linkname
        ikiwa pwd:
            try:
                tarinfo.uname = pwd.getpwuid(tarinfo.uid)[0]
            except KeyError:
                pass
        ikiwa grp:
            try:
                tarinfo.gname = grp.getgrgid(tarinfo.gid)[0]
            except KeyError:
                pass

        ikiwa type in (CHRTYPE, BLKTYPE):
            ikiwa hasattr(os, "major") and hasattr(os, "minor"):
                tarinfo.devmajor = os.major(statres.st_rdev)
                tarinfo.devminor = os.minor(statres.st_rdev)
        rudisha tarinfo

    eleza list(self, verbose=True, *, members=None):
        """Print a table of contents to sys.stdout. If `verbose' is False, only
           the names of the members are printed. If it is True, an `ls -l'-like
           output is produced. `members' is optional and must be a subset of the
           list returned by getmembers().
        """
        self._check()

        ikiwa members is None:
            members = self
        for tarinfo in members:
            ikiwa verbose:
                _safe_andika(stat.filemode(tarinfo.mode))
                _safe_andika("%s/%s" % (tarinfo.uname or tarinfo.uid,
                                       tarinfo.gname or tarinfo.gid))
                ikiwa tarinfo.ischr() or tarinfo.isblk():
                    _safe_andika("%10s" %
                            ("%d,%d" % (tarinfo.devmajor, tarinfo.devminor)))
                else:
                    _safe_andika("%10d" % tarinfo.size)
                _safe_andika("%d-%02d-%02d %02d:%02d:%02d" \
                            % time.localtime(tarinfo.mtime)[:6])

            _safe_andika(tarinfo.name + ("/" ikiwa tarinfo.isdir() else ""))

            ikiwa verbose:
                ikiwa tarinfo.issym():
                    _safe_andika("-> " + tarinfo.linkname)
                ikiwa tarinfo.islnk():
                    _safe_andika("link to " + tarinfo.linkname)
            andika()

    eleza add(self, name, arcname=None, recursive=True, *, filter=None):
        """Add the file `name' to the archive. `name' may be any type of file
           (directory, fifo, symbolic link, etc.). If given, `arcname'
           specifies an alternative name for the file in the archive.
           Directories are added recursively by default. This can be avoided by
           setting `recursive' to False. `filter' is a function
           that expects a TarInfo object argument and returns the changed
           TarInfo object, ikiwa it returns None the TarInfo object will be
           excluded kutoka the archive.
        """
        self._check("awx")

        ikiwa arcname is None:
            arcname = name

        # Skip ikiwa somebody tries to archive the archive...
        ikiwa self.name is not None and os.path.abspath(name) == self.name:
            self._dbg(2, "tarfile: Skipped %r" % name)
            return

        self._dbg(1, name)

        # Create a TarInfo object kutoka the file.
        tarinfo = self.gettarinfo(name, arcname)

        ikiwa tarinfo is None:
            self._dbg(1, "tarfile: Unsupported type %r" % name)
            return

        # Change or exclude the TarInfo object.
        ikiwa filter is not None:
            tarinfo = filter(tarinfo)
            ikiwa tarinfo is None:
                self._dbg(2, "tarfile: Excluded %r" % name)
                return

        # Append the tar header and data to the archive.
        ikiwa tarinfo.isreg():
            with bltn_open(name, "rb") as f:
                self.addfile(tarinfo, f)

        elikiwa tarinfo.isdir():
            self.addfile(tarinfo)
            ikiwa recursive:
                for f in sorted(os.listdir(name)):
                    self.add(os.path.join(name, f), os.path.join(arcname, f),
                            recursive, filter=filter)

        else:
            self.addfile(tarinfo)

    eleza addfile(self, tarinfo, fileobj=None):
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' is
           given, it should be a binary file, and tarinfo.size bytes are read
           kutoka it and added to the archive. You can create TarInfo objects
           directly, or by using gettarinfo().
        """
        self._check("awx")

        tarinfo = copy.copy(tarinfo)

        buf = tarinfo.tobuf(self.format, self.encoding, self.errors)
        self.fileobj.write(buf)
        self.offset += len(buf)
        bufsize=self.copybufsize
        # If there's data to follow, append it.
        ikiwa fileobj is not None:
            copyfileobj(fileobj, self.fileobj, tarinfo.size, bufsize=bufsize)
            blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
            ikiwa remainder > 0:
                self.fileobj.write(NUL * (BLOCKSIZE - remainder))
                blocks += 1
            self.offset += blocks * BLOCKSIZE

        self.members.append(tarinfo)

    eleza extractall(self, path=".", members=None, *, numeric_owner=False):
        """Extract all members kutoka the archive to the current working
           directory and set owner, modification time and permissions on
           directories afterwards. `path' specifies a different directory
           to extract to. `members' is optional and must be a subset of the
           list returned by getmembers(). If `numeric_owner` is True, only
           the numbers for user/group names are used and not the names.
        """
        directories = []

        ikiwa members is None:
            members = self

        for tarinfo in members:
            ikiwa tarinfo.isdir():
                # Extract directories with a safe mode.
                directories.append(tarinfo)
                tarinfo = copy.copy(tarinfo)
                tarinfo.mode = 0o700
            # Do not set_attrs directories, as we will do that further down
            self.extract(tarinfo, path, set_attrs=not tarinfo.isdir(),
                         numeric_owner=numeric_owner)

        # Reverse sort directories.
        directories.sort(key=lambda a: a.name)
        directories.reverse()

        # Set correct owner, mtime and filemode on directories.
        for tarinfo in directories:
            dirpath = os.path.join(path, tarinfo.name)
            try:
                self.chown(tarinfo, dirpath, numeric_owner=numeric_owner)
                self.utime(tarinfo, dirpath)
                self.chmod(tarinfo, dirpath)
            except ExtractError as e:
                ikiwa self.errorlevel > 1:
                    raise
                else:
                    self._dbg(1, "tarfile: %s" % e)

    eleza extract(self, member, path="", set_attrs=True, *, numeric_owner=False):
        """Extract a member kutoka the archive to the current working directory,
           using its full name. Its file information is extracted as accurately
           as possible. `member' may be a filename or a TarInfo object. You can
           specify a different directory using `path'. File attributes (owner,
           mtime, mode) are set unless `set_attrs' is False. If `numeric_owner`
           is True, only the numbers for user/group names are used and not
           the names.
        """
        self._check("r")

        ikiwa isinstance(member, str):
            tarinfo = self.getmember(member)
        else:
            tarinfo = member

        # Prepare the link target for makelink().
        ikiwa tarinfo.islnk():
            tarinfo._link_target = os.path.join(path, tarinfo.linkname)

        try:
            self._extract_member(tarinfo, os.path.join(path, tarinfo.name),
                                 set_attrs=set_attrs,
                                 numeric_owner=numeric_owner)
        except OSError as e:
            ikiwa self.errorlevel > 0:
                raise
            else:
                ikiwa e.filename is None:
                    self._dbg(1, "tarfile: %s" % e.strerror)
                else:
                    self._dbg(1, "tarfile: %s %r" % (e.strerror, e.filename))
        except ExtractError as e:
            ikiwa self.errorlevel > 1:
                raise
            else:
                self._dbg(1, "tarfile: %s" % e)

    eleza extractfile(self, member):
        """Extract a member kutoka the archive as a file object. `member' may be
           a filename or a TarInfo object. If `member' is a regular file or a
           link, an io.BufferedReader object is returned. Otherwise, None is
           returned.
        """
        self._check("r")

        ikiwa isinstance(member, str):
            tarinfo = self.getmember(member)
        else:
            tarinfo = member

        ikiwa tarinfo.isreg() or tarinfo.type not in SUPPORTED_TYPES:
            # Members with unknown types are treated as regular files.
            rudisha self.fileobject(self, tarinfo)

        elikiwa tarinfo.islnk() or tarinfo.issym():
            ikiwa isinstance(self.fileobj, _Stream):
                # A small but ugly workaround for the case that someone tries
                # to extract a (sym)link as a file-object kutoka a non-seekable
                # stream of tar blocks.
                raise StreamError("cannot extract (sym)link as file object")
            else:
                # A (sym)link's file object is its target's file object.
                rudisha self.extractfile(self._find_link_target(tarinfo))
        else:
            # If there's no data associated with the member (directory, chrdev,
            # blkdev, etc.), rudisha None instead of a file object.
            rudisha None

    eleza _extract_member(self, tarinfo, targetpath, set_attrs=True,
                        numeric_owner=False):
        """Extract the TarInfo object tarinfo to a physical
           file called targetpath.
        """
        # Fetch the TarInfo object for the given name
        # and build the destination pathname, replacing
        # forward slashes to platform specific separators.
        targetpath = targetpath.rstrip("/")
        targetpath = targetpath.replace("/", os.sep)

        # Create all upper directories.
        upperdirs = os.path.dirname(targetpath)
        ikiwa upperdirs and not os.path.exists(upperdirs):
            # Create directories that are not part of the archive with
            # default permissions.
            os.makedirs(upperdirs)

        ikiwa tarinfo.islnk() or tarinfo.issym():
            self._dbg(1, "%s -> %s" % (tarinfo.name, tarinfo.linkname))
        else:
            self._dbg(1, tarinfo.name)

        ikiwa tarinfo.isreg():
            self.makefile(tarinfo, targetpath)
        elikiwa tarinfo.isdir():
            self.makedir(tarinfo, targetpath)
        elikiwa tarinfo.isfifo():
            self.makefifo(tarinfo, targetpath)
        elikiwa tarinfo.ischr() or tarinfo.isblk():
            self.makedev(tarinfo, targetpath)
        elikiwa tarinfo.islnk() or tarinfo.issym():
            self.makelink(tarinfo, targetpath)
        elikiwa tarinfo.type not in SUPPORTED_TYPES:
            self.makeunknown(tarinfo, targetpath)
        else:
            self.makefile(tarinfo, targetpath)

        ikiwa set_attrs:
            self.chown(tarinfo, targetpath, numeric_owner)
            ikiwa not tarinfo.issym():
                self.chmod(tarinfo, targetpath)
                self.utime(tarinfo, targetpath)

    #--------------------------------------------------------------------------
    # Below are the different file methods. They are called via
    # _extract_member() when extract() is called. They can be replaced in a
    # subkundi to implement other functionality.

    eleza makedir(self, tarinfo, targetpath):
        """Make a directory called targetpath.
        """
        try:
            # Use a safe mode for the directory, the real mode is set
            # later in _extract_member().
            os.mkdir(targetpath, 0o700)
        except FileExistsError:
            pass

    eleza makefile(self, tarinfo, targetpath):
        """Make a file called targetpath.
        """
        source = self.fileobj
        source.seek(tarinfo.offset_data)
        bufsize = self.copybufsize
        with bltn_open(targetpath, "wb") as target:
            ikiwa tarinfo.sparse is not None:
                for offset, size in tarinfo.sparse:
                    target.seek(offset)
                    copyfileobj(source, target, size, ReadError, bufsize)
                target.seek(tarinfo.size)
                target.truncate()
            else:
                copyfileobj(source, target, tarinfo.size, ReadError, bufsize)

    eleza makeunknown(self, tarinfo, targetpath):
        """Make a file kutoka a TarInfo object with an unknown type
           at targetpath.
        """
        self.makefile(tarinfo, targetpath)
        self._dbg(1, "tarfile: Unknown file type %r, " \
                     "extracted as regular file." % tarinfo.type)

    eleza makefifo(self, tarinfo, targetpath):
        """Make a fifo called targetpath.
        """
        ikiwa hasattr(os, "mkfifo"):
            os.mkfifo(targetpath)
        else:
            raise ExtractError("fifo not supported by system")

    eleza makedev(self, tarinfo, targetpath):
        """Make a character or block device called targetpath.
        """
        ikiwa not hasattr(os, "mknod") or not hasattr(os, "makedev"):
            raise ExtractError("special devices not supported by system")

        mode = tarinfo.mode
        ikiwa tarinfo.isblk():
            mode |= stat.S_IFBLK
        else:
            mode |= stat.S_IFCHR

        os.mknod(targetpath, mode,
                 os.makedev(tarinfo.devmajor, tarinfo.devminor))

    eleza makelink(self, tarinfo, targetpath):
        """Make a (symbolic) link called targetpath. If it cannot be created
          (platform limitation), we try to make a copy of the referenced file
          instead of a link.
        """
        try:
            # For systems that support symbolic and hard links.
            ikiwa tarinfo.issym():
                os.symlink(tarinfo.linkname, targetpath)
            else:
                # See extract().
                ikiwa os.path.exists(tarinfo._link_target):
                    os.link(tarinfo._link_target, targetpath)
                else:
                    self._extract_member(self._find_link_target(tarinfo),
                                         targetpath)
        except symlink_exception:
            try:
                self._extract_member(self._find_link_target(tarinfo),
                                     targetpath)
            except KeyError:
                raise ExtractError("unable to resolve link inside archive")

    eleza chown(self, tarinfo, targetpath, numeric_owner):
        """Set owner of targetpath according to tarinfo. If numeric_owner
           is True, use .gid/.uid instead of .gname/.uname. If numeric_owner
           is False, fall back to .gid/.uid when the search based on name
           fails.
        """
        ikiwa hasattr(os, "geteuid") and os.geteuid() == 0:
            # We have to be root to do so.
            g = tarinfo.gid
            u = tarinfo.uid
            ikiwa not numeric_owner:
                try:
                    ikiwa grp:
                        g = grp.getgrnam(tarinfo.gname)[2]
                except KeyError:
                    pass
                try:
                    ikiwa pwd:
                        u = pwd.getpwnam(tarinfo.uname)[2]
                except KeyError:
                    pass
            try:
                ikiwa tarinfo.issym() and hasattr(os, "lchown"):
                    os.lchown(targetpath, u, g)
                else:
                    os.chown(targetpath, u, g)
            except OSError:
                raise ExtractError("could not change owner")

    eleza chmod(self, tarinfo, targetpath):
        """Set file permissions of targetpath according to tarinfo.
        """
        try:
            os.chmod(targetpath, tarinfo.mode)
        except OSError:
            raise ExtractError("could not change mode")

    eleza utime(self, tarinfo, targetpath):
        """Set modification time of targetpath according to tarinfo.
        """
        ikiwa not hasattr(os, 'utime'):
            return
        try:
            os.utime(targetpath, (tarinfo.mtime, tarinfo.mtime))
        except OSError:
            raise ExtractError("could not change modification time")

    #--------------------------------------------------------------------------
    eleza next(self):
        """Return the next member of the archive as a TarInfo object, when
           TarFile is opened for reading. Return None ikiwa there is no more
           available.
        """
        self._check("ra")
        ikiwa self.firstmember is not None:
            m = self.firstmember
            self.firstmember = None
            rudisha m

        # Advance the file pointer.
        ikiwa self.offset != self.fileobj.tell():
            self.fileobj.seek(self.offset - 1)
            ikiwa not self.fileobj.read(1):
                raise ReadError("unexpected end of data")

        # Read the next block.
        tarinfo = None
        while True:
            try:
                tarinfo = self.tarinfo.kutokatarfile(self)
            except EOFHeaderError as e:
                ikiwa self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    continue
            except InvalidHeaderError as e:
                ikiwa self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    continue
                elikiwa self.offset == 0:
                    raise ReadError(str(e))
            except EmptyHeaderError:
                ikiwa self.offset == 0:
                    raise ReadError("empty file")
            except TruncatedHeaderError as e:
                ikiwa self.offset == 0:
                    raise ReadError(str(e))
            except SubsequentHeaderError as e:
                raise ReadError(str(e))
            break

        ikiwa tarinfo is not None:
            self.members.append(tarinfo)
        else:
            self._loaded = True

        rudisha tarinfo

    #--------------------------------------------------------------------------
    # Little helper methods:

    eleza _getmember(self, name, tarinfo=None, normalize=False):
        """Find an archive member by name kutoka bottom to top.
           If tarinfo is given, it is used as the starting point.
        """
        # Ensure that all members have been loaded.
        members = self.getmembers()

        # Limit the member search list up to tarinfo.
        ikiwa tarinfo is not None:
            members = members[:members.index(tarinfo)]

        ikiwa normalize:
            name = os.path.normpath(name)

        for member in reversed(members):
            ikiwa normalize:
                member_name = os.path.normpath(member.name)
            else:
                member_name = member.name

            ikiwa name == member_name:
                rudisha member

    eleza _load(self):
        """Read through the entire archive file and look for readable
           members.
        """
        while True:
            tarinfo = self.next()
            ikiwa tarinfo is None:
                break
        self._loaded = True

    eleza _check(self, mode=None):
        """Check ikiwa TarFile is still open, and ikiwa the operation's mode
           corresponds to TarFile's mode.
        """
        ikiwa self.closed:
            raise OSError("%s is closed" % self.__class__.__name__)
        ikiwa mode is not None and self.mode not in mode:
            raise OSError("bad operation for mode %r" % self.mode)

    eleza _find_link_target(self, tarinfo):
        """Find the target member of a symlink or hardlink member in the
           archive.
        """
        ikiwa tarinfo.issym():
            # Always search the entire archive.
            linkname = "/".join(filter(None, (os.path.dirname(tarinfo.name), tarinfo.linkname)))
            limit = None
        else:
            # Search the archive before the link, because a hard link is
            # just a reference to an already archived file.
            linkname = tarinfo.linkname
            limit = tarinfo

        member = self._getmember(linkname, tarinfo=limit, normalize=True)
        ikiwa member is None:
            raise KeyError("linkname %r not found" % linkname)
        rudisha member

    eleza __iter__(self):
        """Provide an iterator object.
        """
        ikiwa self._loaded:
            yield kutoka self.members
            return

        # Yield items using TarFile's next() method.
        # When all members have been read, set TarFile as _loaded.
        index = 0
        # Fix for SF #1100429: Under rare circumstances it can
        # happen that getmembers() is called during iteration,
        # which will have already exhausted the next() method.
        ikiwa self.firstmember is not None:
            tarinfo = self.next()
            index += 1
            yield tarinfo

        while True:
            ikiwa index < len(self.members):
                tarinfo = self.members[index]
            elikiwa not self._loaded:
                tarinfo = self.next()
                ikiwa not tarinfo:
                    self._loaded = True
                    return
            else:
                return
            index += 1
            yield tarinfo

    eleza _dbg(self, level, msg):
        """Write debugging output to sys.stderr.
        """
        ikiwa level <= self.debug:
            andika(msg, file=sys.stderr)

    eleza __enter__(self):
        self._check()
        rudisha self

    eleza __exit__(self, type, value, traceback):
        ikiwa type is None:
            self.close()
        else:
            # An exception occurred. We must not call close() because
            # it would try to write end-of-archive blocks and padding.
            ikiwa not self._extfileobj:
                self.fileobj.close()
            self.closed = True

#--------------------
# exported functions
#--------------------
eleza is_tarfile(name):
    """Return True ikiwa name points to a tar archive that we
       are able to handle, else rudisha False.
    """
    try:
        t = open(name)
        t.close()
        rudisha True
    except TarError:
        rudisha False

open = TarFile.open


eleza main():
    agiza argparse

    description = 'A simple command-line interface for tarfile module.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Verbose output')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--list', metavar='<tarfile>',
                       help='Show listing of a tarfile')
    group.add_argument('-e', '--extract', nargs='+',
                       metavar=('<tarfile>', '<output_dir>'),
                       help='Extract tarfile into target dir')
    group.add_argument('-c', '--create', nargs='+',
                       metavar=('<name>', '<file>'),
                       help='Create tarfile kutoka sources')
    group.add_argument('-t', '--test', metavar='<tarfile>',
                       help='Test ikiwa a tarfile is valid')
    args = parser.parse_args()

    ikiwa args.test is not None:
        src = args.test
        ikiwa is_tarfile(src):
            with open(src, 'r') as tar:
                tar.getmembers()
                andika(tar.getmembers(), file=sys.stderr)
            ikiwa args.verbose:
                andika('{!r} is a tar archive.'.format(src))
        else:
            parser.exit(1, '{!r} is not a tar archive.\n'.format(src))

    elikiwa args.list is not None:
        src = args.list
        ikiwa is_tarfile(src):
            with TarFile.open(src, 'r:*') as tf:
                tf.list(verbose=args.verbose)
        else:
            parser.exit(1, '{!r} is not a tar archive.\n'.format(src))

    elikiwa args.extract is not None:
        ikiwa len(args.extract) == 1:
            src = args.extract[0]
            curdir = os.curdir
        elikiwa len(args.extract) == 2:
            src, curdir = args.extract
        else:
            parser.exit(1, parser.format_help())

        ikiwa is_tarfile(src):
            with TarFile.open(src, 'r:*') as tf:
                tf.extractall(path=curdir)
            ikiwa args.verbose:
                ikiwa curdir == '.':
                    msg = '{!r} file is extracted.'.format(src)
                else:
                    msg = ('{!r} file is extracted '
                           'into {!r} directory.').format(src, curdir)
                andika(msg)
        else:
            parser.exit(1, '{!r} is not a tar archive.\n'.format(src))

    elikiwa args.create is not None:
        tar_name = args.create.pop(0)
        _, ext = os.path.splitext(tar_name)
        compressions = {
            # gz
            '.gz': 'gz',
            '.tgz': 'gz',
            # xz
            '.xz': 'xz',
            '.txz': 'xz',
            # bz2
            '.bz2': 'bz2',
            '.tbz': 'bz2',
            '.tbz2': 'bz2',
            '.tb2': 'bz2',
        }
        tar_mode = 'w:' + compressions[ext] ikiwa ext in compressions else 'w'
        tar_files = args.create

        with TarFile.open(tar_name, tar_mode) as tf:
            for file_name in tar_files:
                tf.add(file_name)

        ikiwa args.verbose:
            andika('{!r} file created.'.format(tar_name))

ikiwa __name__ == '__main__':
    main()
