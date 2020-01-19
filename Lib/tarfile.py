#!/usr/bin/env python3
#-------------------------------------------------------------------
# tarfile.py
#-------------------------------------------------------------------
# Copyright (C) 2002 Lars Gustaebel <lars@gustaebel.de>
# All rights reserved.
#
# Permission  ni  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  na associated documentation
# files  (the  "Software"),  to   deal  kwenye  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  na to  permit  persons  to  whom the
# Software  ni  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice na this  permission notice shall  be
# included kwenye all copies ama substantial portions of the Software.
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
"""Read kutoka na write to tar format archives.
"""

version     = "0.9.0"
__author__  = "Lars Gust\u00e4bel (lars@gustaebel.de)"
__credits__ = "Gustavo Niemeyer, Niels Gust\u00e4bel, Richard Townsend."

#---------
# Imports
#---------
kutoka builtins agiza open kama bltn_open
agiza sys
agiza os
agiza io
agiza shutil
agiza stat
agiza time
agiza struct
agiza copy
agiza re

jaribu:
    agiza pwd
tatizo ImportError:
    pwd = Tupu
jaribu:
    agiza grp
tatizo ImportError:
    grp = Tupu

# os.symlink on Windows prior to 6.0 raises NotImplementedError
symlink_exception = (AttributeError, NotImplementedError)
jaribu:
    # OSError (winerror=1314) will be raised ikiwa the caller does sio hold the
    # SeCreateSymbolicLinkPrivilege privilege
    symlink_exception += (OSError,)
tatizo NameError:
    pita

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

# File types that will be treated kama a regular file.
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

# Fields kwenye a pax header that are numbers, all other fields
# are treated kama strings.
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
isipokua:
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
    # There are two possible encodings kila a number field, see
    # itn() below.
    ikiwa s[0] kwenye (0o200, 0o377):
        n = 0
        kila i kwenye range(len(s) - 1):
            n <<= 8
            n += s[i + 1]
        ikiwa s[0] == 0o377:
            n = -(256 ** (len(s) - 1) - n)
    isipokua:
        jaribu:
            s = nts(s, "ascii", "strict")
            n = int(s.strip() ama "0", 8)
        tatizo ValueError:
            ashiria InvalidHeaderError("invalid header")
    rudisha n

eleza itn(n, digits=8, format=DEFAULT_FORMAT):
    """Convert a python number to a number field.
    """
    # POSIX 1003.1-1988 requires numbers to be encoded kama a string of
    # octal digits followed by a null-byte, this allows values up to
    # (8**(digits-1))-1. GNU tar allows storing numbers greater than
    # that ikiwa necessary. A leading 0o200 ama 0o377 byte indicate this
    # particular encoding, the following digits-1 bytes are a big-endian
    # base-256 representation. This allows values up to (256**(digits-1))-1.
    # A 0o200 byte indicates a positive number, a 0o377 byte a negative
    # number.
    n = int(n)
    ikiwa 0 <= n < 8 ** (digits - 1):
        s = bytes("%0*o" % (digits - 1, n), "ascii") + NUL
    lasivyo format == GNU_FORMAT na -256 ** (digits - 1) <= n < 256 ** (digits - 1):
        ikiwa n >= 0:
            s = bytearray([0o200])
        isipokua:
            s = bytearray([0o377])
            n = 256 ** digits + n

        kila i kwenye range(digits - 1):
            s.insert(1, n & 0o377)
            n >>= 8
    isipokua:
        ashiria ValueError("overflow kwenye number field")

    rudisha s

eleza calc_chksums(buf):
    """Calculate the checksum kila a member's header by summing up all
       characters tatizo kila the chksum field which ni treated kama if
       it was filled ukijumuisha spaces. According to the GNU tar sources,
       some tars (Sun na NeXT) calculate chksum ukijumuisha signed char,
       which will be different ikiwa there are chars kwenye the buffer with
       the high bit set. So we calculate two checksums, unsigned na
       signed.
    """
    unsigned_chksum = 256 + sum(struct.unpack_from("148B8x356B", buf))
    signed_chksum = 256 + sum(struct.unpack_from("148b8x356b", buf))
    rudisha unsigned_chksum, signed_chksum

eleza copyfileobj(src, dst, length=Tupu, exception=OSError, bufsize=Tupu):
    """Copy length bytes kutoka fileobj src to fileobj dst.
       If length ni Tupu, copy the entire content.
    """
    bufsize = bufsize ama 16 * 1024
    ikiwa length == 0:
        rudisha
    ikiwa length ni Tupu:
        shutil.copyfileobj(src, dst, bufsize)
        rudisha

    blocks, remainder = divmod(length, bufsize)
    kila b kwenye range(blocks):
        buf = src.read(bufsize)
        ikiwa len(buf) < bufsize:
            ashiria exception("unexpected end of data")
        dst.write(buf)

    ikiwa remainder != 0:
        buf = src.read(remainder)
        ikiwa len(buf) < remainder:
            ashiria exception("unexpected end of data")
        dst.write(buf)
    rudisha

eleza _safe_andika(s):
    encoding = getattr(sys.stdout, 'encoding', Tupu)
    ikiwa encoding ni sio Tupu:
        s = s.encode(encoding, 'backslashreplace').decode(encoding)
    andika(s, end=' ')


kundi TarError(Exception):
    """Base exception."""
    pita
kundi ExtractError(TarError):
    """General exception kila extract errors."""
    pita
kundi ReadError(TarError):
    """Exception kila unreadable tar archives."""
    pita
kundi CompressionError(TarError):
    """Exception kila unavailable compression methods."""
    pita
kundi StreamError(TarError):
    """Exception kila unsupported operations on stream-like TarFiles."""
    pita
kundi HeaderError(TarError):
    """Base exception kila header errors."""
    pita
kundi EmptyHeaderError(HeaderError):
    """Exception kila empty headers."""
    pita
kundi TruncatedHeaderError(HeaderError):
    """Exception kila truncated headers."""
    pita
kundi EOFHeaderError(HeaderError):
    """Exception kila end of file headers."""
    pita
kundi InvalidHeaderError(HeaderError):
    """Exception kila invalid headers."""
    pita
kundi SubsequentHeaderError(HeaderError):
    """Exception kila missing na invalid extended headers."""
    pita

#---------------------------
# internal stream interface
#---------------------------
kundi _LowLevelFile:
    """Low-level file object. Supports reading na writing.
       It ni used instead of a regular file object kila streaming
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
    """Class that serves kama an adapter between TarFile na
       a stream-like object.  The stream-like object only
       needs to have a read() ama write() method na ni accessed
       blockwise.  Use of gzip ama bzip2 compression ni possible.
       A stream-like object could be kila example: sys.stdin,
       sys.stdout, a socket, a tape device etc.

       _Stream ni intended to be used only internally.
    """

    eleza __init__(self, name, mode, comptype, fileobj, bufsize):
        """Construct a _Stream object.
        """
        self._extfileobj = Kweli
        ikiwa fileobj ni Tupu:
            fileobj = _LowLevelFile(name, mode)
            self._extfileobj = Uongo

        ikiwa comptype == '*':
            # Enable transparent compression detection kila the
            # stream interface
            fileobj = _StreamProxy(fileobj)
            comptype = fileobj.getcomptype()

        self.name     = name ama ""
        self.mode     = mode
        self.comptype = comptype
        self.fileobj  = fileobj
        self.bufsize  = bufsize
        self.buf      = b""
        self.pos      = 0
        self.closed   = Uongo

        jaribu:
            ikiwa comptype == "gz":
                jaribu:
                    agiza zlib
                tatizo ImportError:
                    ashiria CompressionError("zlib module ni sio available")
                self.zlib = zlib
                self.crc = zlib.crc32(b"")
                ikiwa mode == "r":
                    self._init_read_gz()
                    self.exception = zlib.error
                isipokua:
                    self._init_write_gz()

            lasivyo comptype == "bz2":
                jaribu:
                    agiza bz2
                tatizo ImportError:
                    ashiria CompressionError("bz2 module ni sio available")
                ikiwa mode == "r":
                    self.dbuf = b""
                    self.cmp = bz2.BZ2Decompressor()
                    self.exception = OSError
                isipokua:
                    self.cmp = bz2.BZ2Compressor()

            lasivyo comptype == "xz":
                jaribu:
                    agiza lzma
                tatizo ImportError:
                    ashiria CompressionError("lzma module ni sio available")
                ikiwa mode == "r":
                    self.dbuf = b""
                    self.cmp = lzma.LZMADecompressor()
                    self.exception = lzma.LZMAError
                isipokua:
                    self.cmp = lzma.LZMACompressor()

            lasivyo comptype != "tar":
                ashiria CompressionError("unknown compression type %r" % comptype)

        tatizo:
            ikiwa sio self._extfileobj:
                self.fileobj.close()
            self.closed = Kweli
            raise

    eleza __del__(self):
        ikiwa hasattr(self, "closed") na sio self.closed:
            self.close()

    eleza _init_write_gz(self):
        """Initialize kila writing ukijumuisha gzip compression.
        """
        self.cmp = self.zlib.compressobj(9, self.zlib.DEFLATED,
                                            -self.zlib.MAX_WBITS,
                                            self.zlib.DEF_MEM_LEVEL,
                                            0)
        timestamp = struct.pack("<L", int(time.time()))
        self.__write(b"\037\213\010\010" + timestamp + b"\002\377")
        ikiwa self.name.endswith(".gz"):
            self.name = self.name[:-3]
        # RFC1952 says we must use ISO-8859-1 kila the FNAME field.
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
           ni ready to be written.
        """
        self.buf += s
        wakati len(self.buf) > self.bufsize:
            self.fileobj.write(self.buf[:self.bufsize])
            self.buf = self.buf[self.bufsize:]

    eleza close(self):
        """Close the _Stream object. No operation should be
           done on it afterwards.
        """
        ikiwa self.closed:
            rudisha

        self.closed = Kweli
        jaribu:
            ikiwa self.mode == "w" na self.comptype != "tar":
                self.buf += self.cmp.flush()

            ikiwa self.mode == "w" na self.buf:
                self.fileobj.write(self.buf)
                self.buf = b""
                ikiwa self.comptype == "gz":
                    self.fileobj.write(struct.pack("<L", self.crc))
                    self.fileobj.write(struct.pack("<L", self.pos & 0xffffFFFF))
        mwishowe:
            ikiwa sio self._extfileobj:
                self.fileobj.close()

    eleza _init_read_gz(self):
        """Initialize kila reading a gzip compressed fileobj.
        """
        self.cmp = self.zlib.decompressobj(-self.zlib.MAX_WBITS)
        self.dbuf = b""

        # taken kutoka gzip.GzipFile ukijumuisha some alterations
        ikiwa self.__read(2) != b"\037\213":
            ashiria ReadError("sio a gzip file")
        ikiwa self.__read(1) != b"\010":
            ashiria CompressionError("unsupported compression method")

        flag = ord(self.__read(1))
        self.__read(6)

        ikiwa flag & 4:
            xlen = ord(self.__read(1)) + 256 * ord(self.__read(1))
            self.read(xlen)
        ikiwa flag & 8:
            wakati Kweli:
                s = self.__read(1)
                ikiwa sio s ama s == NUL:
                    koma
        ikiwa flag & 16:
            wakati Kweli:
                s = self.__read(1)
                ikiwa sio s ama s == NUL:
                    koma
        ikiwa flag & 2:
            self.__read(2)

    eleza tell(self):
        """Return the stream's file pointer position.
        """
        rudisha self.pos

    eleza seek(self, pos=0):
        """Set the stream's file pointer to pos. Negative seeking
           ni forbidden.
        """
        ikiwa pos - self.pos >= 0:
            blocks, remainder = divmod(pos - self.pos, self.bufsize)
            kila i kwenye range(blocks):
                self.read(self.bufsize)
            self.read(remainder)
        isipokua:
            ashiria StreamError("seeking backwards ni sio allowed")
        rudisha self.pos

    eleza read(self, size):
        """Return the next size number of bytes kutoka the stream."""
        assert size ni sio Tupu
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
        wakati c < size:
            # Skip underlying buffer to avoid unaligned double buffering.
            ikiwa self.buf:
                buf = self.buf
                self.buf = b""
            isipokua:
                buf = self.fileobj.read(self.bufsize)
                ikiwa sio buf:
                    koma
            jaribu:
                buf = self.cmp.decompress(buf)
            tatizo self.exception:
                ashiria ReadError("invalid compressed data")
            t.append(buf)
            c += len(buf)
        t = b"".join(t)
        self.dbuf = t[size:]
        rudisha t[:size]

    eleza __read(self, size):
        """Return size bytes kutoka stream. If internal buffer ni empty,
           read another block kutoka the stream.
        """
        c = len(self.buf)
        t = [self.buf]
        wakati c < size:
            buf = self.fileobj.read(self.bufsize)
            ikiwa sio buf:
                koma
            t.append(buf)
            c += len(buf)
        t = b"".join(t)
        self.buf = t[size:]
        rudisha t[:size]
# kundi _Stream

kundi _StreamProxy(object):
    """Small proxy kundi that enables transparent compression
       detection kila the Stream interface (mode 'r|*').
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
        lasivyo self.buf[0:3] == b"BZh" na self.buf[4:10] == b"1AY&SY":
            rudisha "bz2"
        lasivyo self.buf.startswith((b"\x5d\x00\x00\x80", b"\xfd7zXZ")):
            rudisha "xz"
        isipokua:
            rudisha "tar"

    eleza close(self):
        self.fileobj.close()
# kundi StreamProxy

#------------------------
# Extraction file object
#------------------------
kundi _FileInFile(object):
    """A thin wrapper around an existing file object that
       provides a part of its data kama an individual file
       object.
    """

    eleza __init__(self, fileobj, offset, size, blockinfo=Tupu):
        self.fileobj = fileobj
        self.offset = offset
        self.size = size
        self.position = 0
        self.name = getattr(fileobj, "name", Tupu)
        self.closed = Uongo

        ikiwa blockinfo ni Tupu:
            blockinfo = [(0, size)]

        # Construct a map ukijumuisha data na zero blocks.
        self.map_index = 0
        self.map = []
        lastpos = 0
        realpos = self.offset
        kila offset, size kwenye blockinfo:
            ikiwa offset > lastpos:
                self.map.append((Uongo, lastpos, offset, Tupu))
            self.map.append((Kweli, offset, offset + size, realpos))
            realpos += size
            lastpos = offset + size
        ikiwa lastpos < self.size:
            self.map.append((Uongo, lastpos, self.size, Tupu))

    eleza flush(self):
        pita

    eleza readable(self):
        rudisha Kweli

    eleza writable(self):
        rudisha Uongo

    eleza seekable(self):
        rudisha self.fileobj.seekable()

    eleza tell(self):
        """Return the current file position.
        """
        rudisha self.position

    eleza seek(self, position, whence=io.SEEK_SET):
        """Seek to a position kwenye the file.
        """
        ikiwa whence == io.SEEK_SET:
            self.position = min(max(position, 0), self.size)
        lasivyo whence == io.SEEK_CUR:
            ikiwa position < 0:
                self.position = max(self.position + position, 0)
            isipokua:
                self.position = min(self.position + position, self.size)
        lasivyo whence == io.SEEK_END:
            self.position = max(min(self.size + position, self.size), 0)
        isipokua:
            ashiria ValueError("Invalid argument")
        rudisha self.position

    eleza read(self, size=Tupu):
        """Read data kutoka the file.
        """
        ikiwa size ni Tupu:
            size = self.size - self.position
        isipokua:
            size = min(size, self.size - self.position)

        buf = b""
        wakati size > 0:
            wakati Kweli:
                data, start, stop, offset = self.map[self.map_index]
                ikiwa start <= self.position < stop:
                    koma
                isipokua:
                    self.map_index += 1
                    ikiwa self.map_index == len(self.map):
                        self.map_index = 0
            length = min(size, stop - self.position)
            ikiwa data:
                self.fileobj.seek(offset + (self.position - start))
                b = self.fileobj.read(length)
                ikiwa len(b) != length:
                    ashiria ReadError("unexpected end of data")
                buf += b
            isipokua:
                buf += NUL * length
            size -= length
            self.position += length
        rudisha buf

    eleza readinto(self, b):
        buf = self.read(len(b))
        b[:len(buf)] = buf
        rudisha len(buf)

    eleza close(self):
        self.closed = Kweli
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
       TarFile.getmembers() na TarFile.gettarinfo() na are
       usually created internally.
    """

    __slots__ = dict(
        name = 'Name of the archive member.',
        mode = 'Permission bits.',
        uid = 'User ID of the user who originally stored this member.',
        gid = 'Group ID of the user who originally stored this member.',
        size = 'Size kwenye bytes.',
        mtime = 'Time of last modification.',
        chksum = 'Header checksum.',
        type = ('File type. type ni usually one of these constants: '
                'REGTYPE, AREGTYPE, LNKTYPE, SYMTYPE, DIRTYPE, FIFOTYPE, '
                'CONTTYPE, CHRTYPE, BLKTYPE, GNUTYPE_SPARSE.'),
        linkname = ('Name of the target file name, which ni only present '
                    'in TarInfo objects of type LNKTYPE na SYMTYPE.'),
        uname = 'User name.',
        gname = 'Group name.',
        devmajor = 'Device major number.',
        devminor = 'Device minor number.',
        offset = 'The tar header starts here.',
        offset_data = "The file's data starts here.",
        pax_headers = ('A dictionary containing key-value pairs of an '
                       'associated pax extended header.'),
        sparse = 'Sparse member information.',
        tarfile = Tupu,
        _sparse_structs = Tupu,
        _link_target = Tupu,
        )

    eleza __init__(self, name=""):
        """Construct a TarInfo object. name ni the optional name
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

        self.sparse = Tupu      # sparse member information
        self.pax_headers = {}   # pax header information

    @property
    eleza path(self):
        'In pax headers, "name" ni called "path".'
        rudisha self.name

    @path.setter
    eleza path(self, name):
        self.name = name

    @property
    eleza linkpath(self):
        'In pax headers, "linkname" ni called "linkpath".'
        rudisha self.linkname

    @linkpath.setter
    eleza linkpath(self, linkname):
        self.linkname = linkname

    eleza __repr__(self):
        rudisha "<%s %r at %#x>" % (self.__class__.__name__,self.name,id(self))

    eleza get_info(self):
        """Return the TarInfo's attributes kama a dictionary.
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

        ikiwa info["type"] == DIRTYPE na sio ino["name"].endswith("/"):
            info["name"] += "/"

        rudisha info

    eleza tobuf(self, format=DEFAULT_FORMAT, encoding=ENCODING, errors="surrogateescape"):
        """Return a tar header kama a string of 512 byte blocks.
        """
        info = self.get_info()

        ikiwa format == USTAR_FORMAT:
            rudisha self.create_ustar_header(info, encoding, errors)
        lasivyo format == GNU_FORMAT:
            rudisha self.create_gnu_header(info, encoding, errors)
        lasivyo format == PAX_FORMAT:
            rudisha self.create_pax_header(info, encoding)
        isipokua:
            ashiria ValueError("invalid format")

    eleza create_ustar_header(self, info, encoding, errors):
        """Return the object kama a ustar header block.
        """
        info["magic"] = POSIX_MAGIC

        ikiwa len(info["linkname"].encode(encoding, errors)) > LENGTH_LINK:
            ashiria ValueError("linkname ni too long")

        ikiwa len(info["name"].encode(encoding, errors)) > LENGTH_NAME:
            info["prefix"], info["name"] = self._posix_split_name(info["name"], encoding, errors)

        rudisha self._create_header(info, USTAR_FORMAT, encoding, errors)

    eleza create_gnu_header(self, info, encoding, errors):
        """Return the object kama a GNU header block sequence.
        """
        info["magic"] = GNU_MAGIC

        buf = b""
        ikiwa len(info["linkname"].encode(encoding, errors)) > LENGTH_LINK:
            buf += self._create_gnu_long_header(info["linkname"], GNUTYPE_LONGLINK, encoding, errors)

        ikiwa len(info["name"].encode(encoding, errors)) > LENGTH_NAME:
            buf += self._create_gnu_long_header(info["name"], GNUTYPE_LONGNAME, encoding, errors)

        rudisha buf + self._create_header(info, GNU_FORMAT, encoding, errors)

    eleza create_pax_header(self, info, encoding):
        """Return the object kama a ustar header block. If it cannot be
           represented this way, prepend a pax extended header sequence
           ukijumuisha supplement information.
        """
        info["magic"] = POSIX_MAGIC
        pax_headers = self.pax_headers.copy()

        # Test string fields kila values that exceed the field length ama cannot
        # be represented kwenye ASCII encoding.
        kila name, hname, length kwenye (
                ("name", "path", LENGTH_NAME), ("linkname", "linkpath", LENGTH_LINK),
                ("uname", "uname", 32), ("gname", "gname", 32)):

            ikiwa hname kwenye pax_headers:
                # The pax header has priority.
                endelea

            # Try to encode the string kama ASCII.
            jaribu:
                info[name].encode("ascii", "strict")
            tatizo UnicodeEncodeError:
                pax_headers[hname] = info[name]
                endelea

            ikiwa len(info[name]) > length:
                pax_headers[hname] = info[name]

        # Test number fields kila values that exceed the field limit ama values
        # that like to be stored kama float.
        kila name, digits kwenye (("uid", 8), ("gid", 8), ("size", 12), ("mtime", 12)):
            ikiwa name kwenye pax_headers:
                # The pax header has priority. Avoid overflow.
                info[name] = 0
                endelea

            val = info[name]
            ikiwa sio 0 <= val < 8 ** (digits - 1) ama isinstance(val, float):
                pax_headers[name] = str(val)
                info[name] = 0

        # Create a pax extended header ikiwa necessary.
        ikiwa pax_headers:
            buf = self._create_pax_generic_header(pax_headers, XHDTYPE, encoding)
        isipokua:
            buf = b""

        rudisha buf + self._create_header(info, USTAR_FORMAT, "ascii", "replace")

    @classmethod
    eleza create_pax_global_header(cls, pax_headers):
        """Return the object kama a pax global header block sequence.
        """
        rudisha cls._create_pax_generic_header(pax_headers, XGLTYPE, "utf-8")

    eleza _posix_split_name(self, name, encoding, errors):
        """Split a name longer than 100 chars into a prefix
           na a name part.
        """
        components = name.split("/")
        kila i kwenye range(1, len(components)):
            prefix = "/".join(components[:i])
            name = "/".join(components[i:])
            ikiwa len(prefix.encode(encoding, errors)) <= LENGTH_PREFIX na \
                    len(name.encode(encoding, errors)) <= LENGTH_NAME:
                koma
        isipokua:
            ashiria ValueError("name ni too long")

        rudisha prefix, name

    @staticmethod
    eleza _create_header(info, format, encoding, errors):
        """Return a header block. info ni a dictionary ukijumuisha file
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
        """Return the string payload filled ukijumuisha zero bytes
           up to the next 512 byte border.
        """
        blocks, remainder = divmod(len(payload), BLOCKSIZE)
        ikiwa remainder > 0:
            payload += (BLOCKSIZE - remainder) * NUL
        rudisha payload

    @classmethod
    eleza _create_gnu_long_header(cls, name, type, encoding, errors):
        """Return a GNUTYPE_LONGNAME ama GNUTYPE_LONGLINK sequence
           kila name.
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
        """Return a POSIX.1-2008 extended ama global header sequence
           that contains a list of keyword, value pairs. The values
           must be strings.
        """
        # Check ikiwa one of the fields contains surrogate characters na thereby
        # forces hdrcharset=BINARY, see _proc_pax() kila more information.
        binary = Uongo
        kila keyword, value kwenye pax_headers.items():
            jaribu:
                value.encode("utf-8", "strict")
            tatizo UnicodeEncodeError:
                binary = Kweli
                koma

        records = b""
        ikiwa binary:
            # Put the hdrcharset field at the beginning of the header.
            records += b"21 hdrcharset=BINARY\n"

        kila keyword, value kwenye pax_headers.items():
            keyword = keyword.encode("utf-8")
            ikiwa binary:
                # Try to restore the original byte representation of `value'.
                # Needless to say, that the encoding must match the string.
                value = value.encode(encoding, "surrogateescape")
            isipokua:
                value = value.encode("utf-8")

            l = len(keyword) + len(value) + 3   # ' ' + '=' + '\n'
            n = p = 0
            wakati Kweli:
                n = l + len(str(p))
                ikiwa n == p:
                    koma
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
    eleza frombuf(cls, buf, encoding, errors):
        """Construct a TarInfo object kutoka a 512 byte bytes object.
        """
        ikiwa len(buf) == 0:
            ashiria EmptyHeaderError("empty header")
        ikiwa len(buf) != BLOCKSIZE:
            ashiria TruncatedHeaderError("truncated header")
        ikiwa buf.count(NUL) == BLOCKSIZE:
            ashiria EOFHeaderError("end of file header")

        chksum = nti(buf[148:156])
        ikiwa chksum haiko kwenye calc_chksums(buf):
            ashiria InvalidHeaderError("bad checksum")

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

        # Old V7 tar format represents a directory kama a regular
        # file ukijumuisha a trailing slash.
        ikiwa obj.type == AREGTYPE na obj.name.endswith("/"):
            obj.type = DIRTYPE

        # The old GNU sparse format occupies some of the unused
        # space kwenye the buffer kila up to 4 sparse structures.
        # Save them kila later processing kwenye _proc_sparse().
        ikiwa obj.type == GNUTYPE_SPARSE:
            pos = 386
            structs = []
            kila i kwenye range(4):
                jaribu:
                    offset = nti(buf[pos:pos + 12])
                    numbytes = nti(buf[pos + 12:pos + 24])
                tatizo ValueError:
                    koma
                structs.append((offset, numbytes))
                pos += 24
            isextended = bool(buf[482])
            origsize = nti(buf[483:495])
            obj._sparse_structs = (structs, isextended, origsize)

        # Remove redundant slashes kutoka directories.
        ikiwa obj.isdir():
            obj.name = obj.name.rstrip("/")

        # Reconstruct a ustar longname.
        ikiwa prefix na obj.type haiko kwenye GNU_TYPES:
            obj.name = prefix + "/" + obj.name
        rudisha obj

    @classmethod
    eleza fromtarfile(cls, tarfile):
        """Return the next TarInfo object kutoka TarFile object
           tarfile.
        """
        buf = tarfile.fileobj.read(BLOCKSIZE)
        obj = cls.frombuf(buf, tarfile.encoding, tarfile.errors)
        obj.offset = tarfile.fileobj.tell() - BLOCKSIZE
        rudisha obj._proc_member(tarfile)

    #--------------------------------------------------------------------------
    # The following are methods that are called depending on the type of a
    # member. The entry point ni _proc_member() which can be overridden kwenye a
    # subkundi to add custom _proc_*() methods. A _proc_*() method MUST
    # implement the following
    # operations:
    # 1. Set self.offset_data to the position where the data blocks begin,
    #    ikiwa there ni data that follows.
    # 2. Set tarfile.offset to the position where the next member's header will
    #    begin.
    # 3. Return self ama another valid TarInfo object.
    eleza _proc_member(self, tarfile):
        """Choose the right processing method depending on
           the type na call it.
        """
        ikiwa self.type kwenye (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK):
            rudisha self._proc_gnulong(tarfile)
        lasivyo self.type == GNUTYPE_SPARSE:
            rudisha self._proc_sparse(tarfile)
        lasivyo self.type kwenye (XHDTYPE, XGLTYPE, SOLARIS_XHDTYPE):
            rudisha self._proc_pax(tarfile)
        isipokua:
            rudisha self._proc_builtin(tarfile)

    eleza _proc_builtin(self, tarfile):
        """Process a builtin type ama an unknown type which
           will be treated kama a regular file.
        """
        self.offset_data = tarfile.fileobj.tell()
        offset = self.offset_data
        ikiwa self.isreg() ama self.type haiko kwenye SUPPORTED_TYPES:
            # Skip the following data blocks.
            offset += self._block(self.size)
        tarfile.offset = offset

        # Patch the TarInfo object ukijumuisha saved global
        # header information.
        self._apply_pax_info(tarfile.pax_headers, tarfile.encoding, tarfile.errors)

        rudisha self

    eleza _proc_gnulong(self, tarfile):
        """Process the blocks that hold a GNU longname
           ama longlink member.
        """
        buf = tarfile.fileobj.read(self._block(self.size))

        # Fetch the next header na process it.
        jaribu:
            next = self.fromtarfile(tarfile)
        tatizo HeaderError:
            ashiria SubsequentHeaderError("missing ama bad subsequent header")

        # Patch the TarInfo object kutoka the next header with
        # the longname information.
        next.offset = self.offset
        ikiwa self.type == GNUTYPE_LONGNAME:
            next.name = nts(buf, tarfile.encoding, tarfile.errors)
        lasivyo self.type == GNUTYPE_LONGLINK:
            next.linkname = nts(buf, tarfile.encoding, tarfile.errors)

        rudisha next

    eleza _proc_sparse(self, tarfile):
        """Process a GNU sparse header plus extra headers.
        """
        # We already collected some sparse structures kwenye frombuf().
        structs, isextended, origsize = self._sparse_structs
        toa self._sparse_structs

        # Collect sparse structures kutoka extended header blocks.
        wakati isextended:
            buf = tarfile.fileobj.read(BLOCKSIZE)
            pos = 0
            kila i kwenye range(21):
                jaribu:
                    offset = nti(buf[pos:pos + 12])
                    numbytes = nti(buf[pos + 12:pos + 24])
                tatizo ValueError:
                    koma
                ikiwa offset na numbytes:
                    structs.append((offset, numbytes))
                pos += 24
            isextended = bool(buf[504])
        self.sparse = structs

        self.offset_data = tarfile.fileobj.tell()
        tarfile.offset = self.offset_data + self._block(self.size)
        self.size = origsize
        rudisha self

    eleza _proc_pax(self, tarfile):
        """Process an extended ama global header kama described kwenye
           POSIX.1-2008.
        """
        # Read the header information.
        buf = tarfile.fileobj.read(self._block(self.size))

        # A pax header stores supplemental information kila either
        # the following file (extended) ama all following files
        # (global).
        ikiwa self.type == XGLTYPE:
            pax_headers = tarfile.pax_headers
        isipokua:
            pax_headers = tarfile.pax_headers.copy()

        # Check ikiwa the pax header contains a hdrcharset field. This tells us
        # the encoding of the path, linkpath, uname na gname fields. Normally,
        # these fields are UTF-8 encoded but since POSIX.1-2008 tar
        # implementations are allowed to store them kama raw binary strings if
        # the translation to UTF-8 fails.
        match = re.search(br"\d+ hdrcharset=([^\n]+)\n", buf)
        ikiwa match ni sio Tupu:
            pax_headers["hdrcharset"] = match.group(1).decode("utf-8")

        # For the time being, we don't care about anything other than "BINARY".
        # The only other value that ni currently allowed by the standard is
        # "ISO-IR 10646 2000 UTF-8" kwenye other words UTF-8.
        hdrcharset = pax_headers.get("hdrcharset")
        ikiwa hdrcharset == "BINARY":
            encoding = tarfile.encoding
        isipokua:
            encoding = "utf-8"

        # Parse pax header information. A record looks like that:
        # "%d %s=%s\n" % (length, keyword, value). length ni the size
        # of the complete record including the length field itself na
        # the newline. keyword na value are both UTF-8 encoded strings.
        regex = re.compile(br"(\d+) ([^=]+)=")
        pos = 0
        wakati Kweli:
            match = regex.match(buf, pos)
            ikiwa sio match:
                koma

            length, keyword = match.groups()
            length = int(length)
            value = buf[match.end(2) + 1:match.start(1) + length - 1]

            # Normally, we could just use "utf-8" kama the encoding na "strict"
            # kama the error handler, but we better sio take the risk. For
            # example, GNU tar <= 1.23 ni known to store filenames it cannot
            # translate to UTF-8 kama raw strings (unfortunately without a
            # hdrcharset=BINARY header).
            # We first try the strict standard encoding, na ikiwa that fails we
            # fall back on the user's encoding na error handler.
            keyword = self._decode_pax_field(keyword, "utf-8", "utf-8",
                    tarfile.errors)
            ikiwa keyword kwenye PAX_NAME_FIELDS:
                value = self._decode_pax_field(value, encoding, tarfile.encoding,
                        tarfile.errors)
            isipokua:
                value = self._decode_pax_field(value, "utf-8", "utf-8",
                        tarfile.errors)

            pax_headers[keyword] = value
            pos += length

        # Fetch the next header.
        jaribu:
            next = self.fromtarfile(tarfile)
        tatizo HeaderError:
            ashiria SubsequentHeaderError("missing ama bad subsequent header")

        # Process GNU sparse information.
        ikiwa "GNU.sparse.map" kwenye pax_headers:
            # GNU extended sparse format version 0.1.
            self._proc_gnusparse_01(next, pax_headers)

        lasivyo "GNU.sparse.size" kwenye pax_headers:
            # GNU extended sparse format version 0.0.
            self._proc_gnusparse_00(next, pax_headers, buf)

        lasivyo pax_headers.get("GNU.sparse.major") == "1" na pax_headers.get("GNU.sparse.minor") == "0":
            # GNU extended sparse format version 1.0.
            self._proc_gnusparse_10(next, pax_headers, tarfile)

        ikiwa self.type kwenye (XHDTYPE, SOLARIS_XHDTYPE):
            # Patch the TarInfo object ukijumuisha the extended header info.
            next._apply_pax_info(pax_headers, tarfile.encoding, tarfile.errors)
            next.offset = self.offset

            ikiwa "size" kwenye pax_headers:
                # If the extended header replaces the size field,
                # we need to recalculate the offset where the next
                # header starts.
                offset = next.offset_data
                ikiwa next.isreg() ama next.type haiko kwenye SUPPORTED_TYPES:
                    offset += next._block(next.size)
                tarfile.offset = offset

        rudisha next

    eleza _proc_gnusparse_00(self, next, pax_headers, buf):
        """Process a GNU tar extended sparse header, version 0.0.
        """
        offsets = []
        kila match kwenye re.finditer(br"\d+ GNU.sparse.offset=(\d+)\n", buf):
            offsets.append(int(match.group(1)))
        numbytes = []
        kila match kwenye re.finditer(br"\d+ GNU.sparse.numbytes=(\d+)\n", buf):
            numbytes.append(int(match.group(1)))
        next.sparse = list(zip(offsets, numbytes))

    eleza _proc_gnusparse_01(self, next, pax_headers):
        """Process a GNU tar extended sparse header, version 0.1.
        """
        sparse = [int(x) kila x kwenye pax_headers["GNU.sparse.map"].split(",")]
        next.sparse = list(zip(sparse[::2], sparse[1::2]))

    eleza _proc_gnusparse_10(self, next, pax_headers, tarfile):
        """Process a GNU tar extended sparse header, version 1.0.
        """
        fields = Tupu
        sparse = []
        buf = tarfile.fileobj.read(BLOCKSIZE)
        fields, buf = buf.split(b"\n", 1)
        fields = int(fields)
        wakati len(sparse) < fields * 2:
            ikiwa b"\n" haiko kwenye buf:
                buf += tarfile.fileobj.read(BLOCKSIZE)
            number, buf = buf.split(b"\n", 1)
            sparse.append(int(number))
        next.offset_data = tarfile.fileobj.tell()
        next.sparse = list(zip(sparse[::2], sparse[1::2]))

    eleza _apply_pax_info(self, pax_headers, encoding, errors):
        """Replace fields ukijumuisha supplemental information kutoka a previous
           pax extended ama global header.
        """
        kila keyword, value kwenye pax_headers.items():
            ikiwa keyword == "GNU.sparse.name":
                setattr(self, "path", value)
            lasivyo keyword == "GNU.sparse.size":
                setattr(self, "size", int(value))
            lasivyo keyword == "GNU.sparse.realsize":
                setattr(self, "size", int(value))
            lasivyo keyword kwenye PAX_FIELDS:
                ikiwa keyword kwenye PAX_NUMBER_FIELDS:
                    jaribu:
                        value = PAX_NUMBER_FIELDS[keyword](value)
                    tatizo ValueError:
                        value = 0
                ikiwa keyword == "path":
                    value = value.rstrip("/")
                setattr(self, keyword, value)

        self.pax_headers = pax_headers.copy()

    eleza _decode_pax_field(self, value, encoding, fallback_encoding, fallback_errors):
        """Decode a single field kutoka a pax record.
        """
        jaribu:
            rudisha value.decode(encoding, "strict")
        tatizo UnicodeDecodeError:
            rudisha value.decode(fallback_encoding, fallback_errors)

    eleza _block(self, count):
        """Round up a byte count by BLOCKSIZE na rudisha it,
           e.g. _block(834) => 1024.
        """
        blocks, remainder = divmod(count, BLOCKSIZE)
        ikiwa remainder:
            blocks += 1
        rudisha blocks * BLOCKSIZE

    eleza isreg(self):
        'Return Kweli ikiwa the Tarinfo object ni a regular file.'
        rudisha self.type kwenye REGULAR_TYPES

    eleza isfile(self):
        'Return Kweli ikiwa the Tarinfo object ni a regular file.'
        rudisha self.isreg()

    eleza isdir(self):
        'Return Kweli ikiwa it ni a directory.'
        rudisha self.type == DIRTYPE

    eleza issym(self):
        'Return Kweli ikiwa it ni a symbolic link.'
        rudisha self.type == SYMTYPE

    eleza islnk(self):
        'Return Kweli ikiwa it ni a hard link.'
        rudisha self.type == LNKTYPE

    eleza ischr(self):
        'Return Kweli ikiwa it ni a character device.'
        rudisha self.type == CHRTYPE

    eleza isblk(self):
        'Return Kweli ikiwa it ni a block device.'
        rudisha self.type == BLKTYPE

    eleza isfifo(self):
        'Return Kweli ikiwa it ni a FIFO.'
        rudisha self.type == FIFOTYPE

    eleza issparse(self):
        rudisha self.sparse ni sio Tupu

    eleza isdev(self):
        'Return Kweli ikiwa it ni one of character device, block device ama FIFO.'
        rudisha self.type kwenye (CHRTYPE, BLKTYPE, FIFOTYPE)
# kundi TarInfo

kundi TarFile(object):
    """The TarFile Class provides an interface to tar archives.
    """

    debug = 0                   # May be set kutoka 0 (no msgs) to 3 (all msgs)

    dereference = Uongo         # If true, add content of linked file to the
                                # tar file, isipokua the link.

    ignore_zeros = Uongo        # If true, skips empty ama invalid blocks na
                                # endeleas processing.

    errorlevel = 1              # If 0, fatal errors only appear kwenye debug
                                # messages (ikiwa debug >= 0). If > 0, errors
                                # are pitaed to the caller kama exceptions.

    format = DEFAULT_FORMAT     # The format to use when creating an archive.

    encoding = ENCODING         # Encoding kila 8-bit character strings.

    errors = Tupu               # Error handler kila unicode conversion.

    tarinfo = TarInfo           # The default TarInfo kundi to use.

    fileobject = ExFileObject   # The file-object kila extractfile().

    eleza __init__(self, name=Tupu, mode="r", fileobj=Tupu, format=Tupu,
            tarinfo=Tupu, dereference=Tupu, ignore_zeros=Tupu, encoding=Tupu,
            errors="surrogateescape", pax_headers=Tupu, debug=Tupu,
            errorlevel=Tupu, copybufsize=Tupu):
        """Open an (uncompressed) tar archive `name'. `mode' ni either 'r' to
           read kutoka an existing archive, 'a' to append data to an existing
           file ama 'w' to create a new file overwriting an existing one. `mode'
           defaults to 'r'.
           If `fileobj' ni given, it ni used kila reading ama writing data. If it
           can be determined, `mode' ni overridden by `fileobj's mode.
           `fileobj' ni sio closed, when TarFile ni closed.
        """
        modes = {"r": "rb", "a": "r+b", "w": "wb", "x": "xb"}
        ikiwa mode haiko kwenye modes:
            ashiria ValueError("mode must be 'r', 'a', 'w' ama 'x'")
        self.mode = mode
        self._mode = modes[mode]

        ikiwa sio fileobj:
            ikiwa self.mode == "a" na sio os.path.exists(name):
                # Create nonexistent files kwenye append mode.
                self.mode = "w"
                self._mode = "wb"
            fileobj = bltn_open(name, self._mode)
            self._extfileobj = Uongo
        isipokua:
            ikiwa (name ni Tupu na hasattr(fileobj, "name") na
                isinstance(fileobj.name, (str, bytes))):
                name = fileobj.name
            ikiwa hasattr(fileobj, "mode"):
                self._mode = fileobj.mode
            self._extfileobj = Kweli
        self.name = os.path.abspath(name) ikiwa name isipokua Tupu
        self.fileobj = fileobj

        # Init attributes.
        ikiwa format ni sio Tupu:
            self.format = format
        ikiwa tarinfo ni sio Tupu:
            self.tarinfo = tarinfo
        ikiwa dereference ni sio Tupu:
            self.dereference = dereference
        ikiwa ignore_zeros ni sio Tupu:
            self.ignore_zeros = ignore_zeros
        ikiwa encoding ni sio Tupu:
            self.encoding = encoding
        self.errors = errors

        ikiwa pax_headers ni sio Tupu na self.format == PAX_FORMAT:
            self.pax_headers = pax_headers
        isipokua:
            self.pax_headers = {}

        ikiwa debug ni sio Tupu:
            self.debug = debug
        ikiwa errorlevel ni sio Tupu:
            self.errorlevel = errorlevel

        # Init datastructures.
        self.copybufsize = copybufsize
        self.closed = Uongo
        self.members = []       # list of members kama TarInfo objects
        self._loaded = Uongo    # flag ikiwa all members have been read
        self.offset = self.fileobj.tell()
                                # current position kwenye the archive file
        self.inodes = {}        # dictionary caching the inodes of
                                # archive members already added

        jaribu:
            ikiwa self.mode == "r":
                self.firstmember = Tupu
                self.firstmember = self.next()

            ikiwa self.mode == "a":
                # Move to the end of the archive,
                # before the first empty block.
                wakati Kweli:
                    self.fileobj.seek(self.offset)
                    jaribu:
                        tarinfo = self.tarinfo.fromtarfile(self)
                        self.members.append(tarinfo)
                    tatizo EOFHeaderError:
                        self.fileobj.seek(self.offset)
                        koma
                    tatizo HeaderError kama e:
                        ashiria ReadError(str(e))

            ikiwa self.mode kwenye ("a", "w", "x"):
                self._loaded = Kweli

                ikiwa self.pax_headers:
                    buf = self.tarinfo.create_pax_global_header(self.pax_headers.copy())
                    self.fileobj.write(buf)
                    self.offset += len(buf)
        tatizo:
            ikiwa sio self._extfileobj:
                self.fileobj.close()
            self.closed = Kweli
            raise

    #--------------------------------------------------------------------------
    # Below are the classmethods which act kama alternate constructors to the
    # TarFile class. The open() method ni the only one that ni needed for
    # public use; it ni the "super"-constructor na ni able to select an
    # adequate "sub"-constructor kila a particular compression using the mapping
    # kutoka OPEN_METH.
    #
    # This concept allows one to subkundi TarFile without losing the comfort of
    # the super-constructor. A sub-constructor ni registered na made available
    # by adding it to the mapping kwenye OPEN_METH.

    @classmethod
    eleza open(cls, name=Tupu, mode="r", fileobj=Tupu, bufsize=RECORDSIZE, **kwargs):
        """Open a tar archive kila reading, writing ama appending. Return
           an appropriate TarFile class.

           mode:
           'r' ama 'r:*' open kila reading ukijumuisha transparent compression
           'r:'         open kila reading exclusively uncompressed
           'r:gz'       open kila reading ukijumuisha gzip compression
           'r:bz2'      open kila reading ukijumuisha bzip2 compression
           'r:xz'       open kila reading ukijumuisha lzma compression
           'a' ama 'a:'  open kila appending, creating the file ikiwa necessary
           'w' ama 'w:'  open kila writing without compression
           'w:gz'       open kila writing ukijumuisha gzip compression
           'w:bz2'      open kila writing ukijumuisha bzip2 compression
           'w:xz'       open kila writing ukijumuisha lzma compression

           'x' ama 'x:'  create a tarfile exclusively without compression, raise
                        an exception ikiwa the file ni already created
           'x:gz'       create a gzip compressed tarfile, ashiria an exception
                        ikiwa the file ni already created
           'x:bz2'      create a bzip2 compressed tarfile, ashiria an exception
                        ikiwa the file ni already created
           'x:xz'       create an lzma compressed tarfile, ashiria an exception
                        ikiwa the file ni already created

           'r|*'        open a stream of tar blocks ukijumuisha transparent compression
           'r|'         open an uncompressed stream of tar blocks kila reading
           'r|gz'       open a gzip compressed stream of tar blocks
           'r|bz2'      open a bzip2 compressed stream of tar blocks
           'r|xz'       open an lzma compressed stream of tar blocks
           'w|'         open an uncompressed stream kila writing
           'w|gz'       open a gzip compressed stream kila writing
           'w|bz2'      open a bzip2 compressed stream kila writing
           'w|xz'       open an lzma compressed stream kila writing
        """

        ikiwa sio name na sio fileobj:
            ashiria ValueError("nothing to open")

        ikiwa mode kwenye ("r", "r:*"):
            # Find out which *open() ni appropriate kila opening the file.
            eleza not_compressed(comptype):
                rudisha cls.OPEN_METH[comptype] == 'taropen'
            kila comptype kwenye sorted(cls.OPEN_METH, key=not_compressed):
                func = getattr(cls, cls.OPEN_METH[comptype])
                ikiwa fileobj ni sio Tupu:
                    saved_pos = fileobj.tell()
                jaribu:
                    rudisha func(name, "r", fileobj, **kwargs)
                tatizo (ReadError, CompressionError):
                    ikiwa fileobj ni sio Tupu:
                        fileobj.seek(saved_pos)
                    endelea
            ashiria ReadError("file could sio be opened successfully")

        lasivyo ":" kwenye mode:
            filemode, comptype = mode.split(":", 1)
            filemode = filemode ama "r"
            comptype = comptype ama "tar"

            # Select the *open() function according to
            # given compression.
            ikiwa comptype kwenye cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
            isipokua:
                ashiria CompressionError("unknown compression type %r" % comptype)
            rudisha func(name, filemode, fileobj, **kwargs)

        lasivyo "|" kwenye mode:
            filemode, comptype = mode.split("|", 1)
            filemode = filemode ama "r"
            comptype = comptype ama "tar"

            ikiwa filemode haiko kwenye ("r", "w"):
                ashiria ValueError("mode must be 'r' ama 'w'")

            stream = _Stream(name, filemode, comptype, fileobj, bufsize)
            jaribu:
                t = cls(name, filemode, stream, **kwargs)
            tatizo:
                stream.close()
                raise
            t._extfileobj = Uongo
            rudisha t

        lasivyo mode kwenye ("a", "w", "x"):
            rudisha cls.taropen(name, mode, fileobj, **kwargs)

        ashiria ValueError("undiscernible mode")

    @classmethod
    eleza taropen(cls, name, mode="r", fileobj=Tupu, **kwargs):
        """Open uncompressed tar archive name kila reading ama writing.
        """
        ikiwa mode haiko kwenye ("r", "a", "w", "x"):
            ashiria ValueError("mode must be 'r', 'a', 'w' ama 'x'")
        rudisha cls(name, mode, fileobj, **kwargs)

    @classmethod
    eleza gzopen(cls, name, mode="r", fileobj=Tupu, compresslevel=9, **kwargs):
        """Open gzip compressed tar archive name kila reading ama writing.
           Appending ni sio allowed.
        """
        ikiwa mode haiko kwenye ("r", "w", "x"):
            ashiria ValueError("mode must be 'r', 'w' ama 'x'")

        jaribu:
            agiza gzip
            gzip.GzipFile
        tatizo (ImportError, AttributeError):
            ashiria CompressionError("gzip module ni sio available")

        jaribu:
            fileobj = gzip.GzipFile(name, mode + "b", compresslevel, fileobj)
        tatizo OSError:
            ikiwa fileobj ni sio Tupu na mode == 'r':
                ashiria ReadError("sio a gzip file")
            raise

        jaribu:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        tatizo OSError:
            fileobj.close()
            ikiwa mode == 'r':
                ashiria ReadError("sio a gzip file")
            raise
        tatizo:
            fileobj.close()
            raise
        t._extfileobj = Uongo
        rudisha t

    @classmethod
    eleza bz2open(cls, name, mode="r", fileobj=Tupu, compresslevel=9, **kwargs):
        """Open bzip2 compressed tar archive name kila reading ama writing.
           Appending ni sio allowed.
        """
        ikiwa mode haiko kwenye ("r", "w", "x"):
            ashiria ValueError("mode must be 'r', 'w' ama 'x'")

        jaribu:
            agiza bz2
        tatizo ImportError:
            ashiria CompressionError("bz2 module ni sio available")

        fileobj = bz2.BZ2File(fileobj ama name, mode,
                              compresslevel=compresslevel)

        jaribu:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        tatizo (OSError, EOFError):
            fileobj.close()
            ikiwa mode == 'r':
                ashiria ReadError("sio a bzip2 file")
            raise
        tatizo:
            fileobj.close()
            raise
        t._extfileobj = Uongo
        rudisha t

    @classmethod
    eleza xzopen(cls, name, mode="r", fileobj=Tupu, preset=Tupu, **kwargs):
        """Open lzma compressed tar archive name kila reading ama writing.
           Appending ni sio allowed.
        """
        ikiwa mode haiko kwenye ("r", "w", "x"):
            ashiria ValueError("mode must be 'r', 'w' ama 'x'")

        jaribu:
            agiza lzma
        tatizo ImportError:
            ashiria CompressionError("lzma module ni sio available")

        fileobj = lzma.LZMAFile(fileobj ama name, mode, preset=preset)

        jaribu:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        tatizo (lzma.LZMAError, EOFError):
            fileobj.close()
            ikiwa mode == 'r':
                ashiria ReadError("sio an lzma file")
            raise
        tatizo:
            fileobj.close()
            raise
        t._extfileobj = Uongo
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
            rudisha

        self.closed = Kweli
        jaribu:
            ikiwa self.mode kwenye ("a", "w", "x"):
                self.fileobj.write(NUL * (BLOCKSIZE * 2))
                self.offset += (BLOCKSIZE * 2)
                # fill up the end ukijumuisha zero-blocks
                # (like option -b20 kila tar does)
                blocks, remainder = divmod(self.offset, RECORDSIZE)
                ikiwa remainder > 0:
                    self.fileobj.write(NUL * (RECORDSIZE - remainder))
        mwishowe:
            ikiwa sio self._extfileobj:
                self.fileobj.close()

    eleza getmember(self, name):
        """Return a TarInfo object kila member `name'. If `name' can sio be
           found kwenye the archive, KeyError ni raised. If a member occurs more
           than once kwenye the archive, its last occurrence ni assumed to be the
           most up-to-date version.
        """
        tarinfo = self._getmember(name)
        ikiwa tarinfo ni Tupu:
            ashiria KeyError("filename %r sio found" % name)
        rudisha tarinfo

    eleza getmembers(self):
        """Return the members of the archive kama a list of TarInfo objects. The
           list has the same order kama the members kwenye the archive.
        """
        self._check()
        ikiwa sio self._loaded:    # ikiwa we want to obtain a list of
            self._load()        # all members, we first have to
                                # scan the whole archive.
        rudisha self.members

    eleza getnames(self):
        """Return the members of the archive kama a list of their names. It has
           the same order kama the list returned by getmembers().
        """
        rudisha [tarinfo.name kila tarinfo kwenye self.getmembers()]

    eleza gettarinfo(self, name=Tupu, arcname=Tupu, fileobj=Tupu):
        """Create a TarInfo object kutoka the result of os.stat ama equivalent
           on an existing file. The file ni either named by `name', ama
           specified kama a file object `fileobj' ukijumuisha a file descriptor. If
           given, `arcname' specifies an alternative name kila the file kwenye the
           archive, otherwise, the name ni taken kutoka the 'name' attribute of
           'fileobj', ama the 'name' argument. The name should be a text
           string.
        """
        self._check("awx")

        # When fileobj ni given, replace name by
        # fileobj's real name.
        ikiwa fileobj ni sio Tupu:
            name = fileobj.name

        # Building the name of the member kwenye the archive.
        # Backward slashes are converted to forward slashes,
        # Absolute paths are turned to relative paths.
        ikiwa arcname ni Tupu:
            arcname = name
        drv, arcname = os.path.splitdrive(arcname)
        arcname = arcname.replace(os.sep, "/")
        arcname = arcname.lstrip("/")

        # Now, fill the TarInfo object with
        # information specific kila the file.
        tarinfo = self.tarinfo()
        tarinfo.tarfile = self  # Not needed

        # Use os.stat ama os.lstat, depending on ikiwa symlinks shall be resolved.
        ikiwa fileobj ni Tupu:
            ikiwa sio self.dereference:
                statres = os.lstat(name)
            isipokua:
                statres = os.stat(name)
        isipokua:
            statres = os.fstat(fileobj.fileno())
        linkname = ""

        stmd = statres.st_mode
        ikiwa stat.S_ISREG(stmd):
            inode = (statres.st_ino, statres.st_dev)
            ikiwa sio self.dereference na statres.st_nlink > 1 na \
                    inode kwenye self.inodes na arcname != self.inodes[inode]:
                # Is it a hardlink to an already
                # archived file?
                type = LNKTYPE
                linkname = self.inodes[inode]
            isipokua:
                # The inode ni added only ikiwa its valid.
                # For win32 it ni always 0.
                type = REGTYPE
                ikiwa inode[0]:
                    self.inodes[inode] = arcname
        lasivyo stat.S_ISDIR(stmd):
            type = DIRTYPE
        lasivyo stat.S_ISFIFO(stmd):
            type = FIFOTYPE
        lasivyo stat.S_ISLNK(stmd):
            type = SYMTYPE
            linkname = os.readlink(name)
        lasivyo stat.S_ISCHR(stmd):
            type = CHRTYPE
        lasivyo stat.S_ISBLK(stmd):
            type = BLKTYPE
        isipokua:
            rudisha Tupu

        # Fill the TarInfo object ukijumuisha all
        # information we can get.
        tarinfo.name = arcname
        tarinfo.mode = stmd
        tarinfo.uid = statres.st_uid
        tarinfo.gid = statres.st_gid
        ikiwa type == REGTYPE:
            tarinfo.size = statres.st_size
        isipokua:
            tarinfo.size = 0
        tarinfo.mtime = statres.st_mtime
        tarinfo.type = type
        tarinfo.linkname = linkname
        ikiwa pwd:
            jaribu:
                tarinfo.uname = pwd.getpwuid(tarinfo.uid)[0]
            tatizo KeyError:
                pita
        ikiwa grp:
            jaribu:
                tarinfo.gname = grp.getgrgid(tarinfo.gid)[0]
            tatizo KeyError:
                pita

        ikiwa type kwenye (CHRTYPE, BLKTYPE):
            ikiwa hasattr(os, "major") na hasattr(os, "minor"):
                tarinfo.devmajor = os.major(statres.st_rdev)
                tarinfo.devminor = os.minor(statres.st_rdev)
        rudisha tarinfo

    eleza list(self, verbose=Kweli, *, members=Tupu):
        """Print a table of contents to sys.stdout. If `verbose' ni Uongo, only
           the names of the members are printed. If it ni Kweli, an `ls -l'-like
           output ni produced. `members' ni optional na must be a subset of the
           list returned by getmembers().
        """
        self._check()

        ikiwa members ni Tupu:
            members = self
        kila tarinfo kwenye members:
            ikiwa verbose:
                _safe_andika(stat.filemode(tarinfo.mode))
                _safe_andika("%s/%s" % (tarinfo.uname ama tarinfo.uid,
                                       tarinfo.gname ama tarinfo.gid))
                ikiwa tarinfo.ischr() ama tarinfo.isblk():
                    _safe_andika("%10s" %
                            ("%d,%d" % (tarinfo.devmajor, tarinfo.devminor)))
                isipokua:
                    _safe_andika("%10d" % tarinfo.size)
                _safe_andika("%d-%02d-%02d %02d:%02d:%02d" \
                            % time.localtime(tarinfo.mtime)[:6])

            _safe_andika(tarinfo.name + ("/" ikiwa tarinfo.isdir() isipokua ""))

            ikiwa verbose:
                ikiwa tarinfo.issym():
                    _safe_andika("-> " + tarinfo.linkname)
                ikiwa tarinfo.islnk():
                    _safe_andika("link to " + tarinfo.linkname)
            andika()

    eleza add(self, name, arcname=Tupu, recursive=Kweli, *, filter=Tupu):
        """Add the file `name' to the archive. `name' may be any type of file
           (directory, fifo, symbolic link, etc.). If given, `arcname'
           specifies an alternative name kila the file kwenye the archive.
           Directories are added recursively by default. This can be avoided by
           setting `recursive' to Uongo. `filter' ni a function
           that expects a TarInfo object argument na returns the changed
           TarInfo object, ikiwa it returns Tupu the TarInfo object will be
           excluded kutoka the archive.
        """
        self._check("awx")

        ikiwa arcname ni Tupu:
            arcname = name

        # Skip ikiwa somebody tries to archive the archive...
        ikiwa self.name ni sio Tupu na os.path.abspath(name) == self.name:
            self._dbg(2, "tarfile: Skipped %r" % name)
            rudisha

        self._dbg(1, name)

        # Create a TarInfo object kutoka the file.
        tarinfo = self.gettarinfo(name, arcname)

        ikiwa tarinfo ni Tupu:
            self._dbg(1, "tarfile: Unsupported type %r" % name)
            rudisha

        # Change ama exclude the TarInfo object.
        ikiwa filter ni sio Tupu:
            tarinfo = filter(tarinfo)
            ikiwa tarinfo ni Tupu:
                self._dbg(2, "tarfile: Excluded %r" % name)
                rudisha

        # Append the tar header na data to the archive.
        ikiwa tarinfo.isreg():
            ukijumuisha bltn_open(name, "rb") kama f:
                self.addfile(tarinfo, f)

        lasivyo tarinfo.isdir():
            self.addfile(tarinfo)
            ikiwa recursive:
                kila f kwenye sorted(os.listdir(name)):
                    self.add(os.path.join(name, f), os.path.join(arcname, f),
                            recursive, filter=filter)

        isipokua:
            self.addfile(tarinfo)

    eleza addfile(self, tarinfo, fileobj=Tupu):
        """Add the TarInfo object `tarinfo' to the archive. If `fileobj' is
           given, it should be a binary file, na tarinfo.size bytes are read
           kutoka it na added to the archive. You can create TarInfo objects
           directly, ama by using gettarinfo().
        """
        self._check("awx")

        tarinfo = copy.copy(tarinfo)

        buf = tarinfo.tobuf(self.format, self.encoding, self.errors)
        self.fileobj.write(buf)
        self.offset += len(buf)
        bufsize=self.copybufsize
        # If there's data to follow, append it.
        ikiwa fileobj ni sio Tupu:
            copyfileobj(fileobj, self.fileobj, tarinfo.size, bufsize=bufsize)
            blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
            ikiwa remainder > 0:
                self.fileobj.write(NUL * (BLOCKSIZE - remainder))
                blocks += 1
            self.offset += blocks * BLOCKSIZE

        self.members.append(tarinfo)

    eleza extractall(self, path=".", members=Tupu, *, numeric_owner=Uongo):
        """Extract all members kutoka the archive to the current working
           directory na set owner, modification time na permissions on
           directories afterwards. `path' specifies a different directory
           to extract to. `members' ni optional na must be a subset of the
           list returned by getmembers(). If `numeric_owner` ni Kweli, only
           the numbers kila user/group names are used na sio the names.
        """
        directories = []

        ikiwa members ni Tupu:
            members = self

        kila tarinfo kwenye members:
            ikiwa tarinfo.isdir():
                # Extract directories ukijumuisha a safe mode.
                directories.append(tarinfo)
                tarinfo = copy.copy(tarinfo)
                tarinfo.mode = 0o700
            # Do sio set_attrs directories, kama we will do that further down
            self.extract(tarinfo, path, set_attrs=sio tarinfo.isdir(),
                         numeric_owner=numeric_owner)

        # Reverse sort directories.
        directories.sort(key=lambda a: a.name)
        directories.reverse()

        # Set correct owner, mtime na filemode on directories.
        kila tarinfo kwenye directories:
            dirpath = os.path.join(path, tarinfo.name)
            jaribu:
                self.chown(tarinfo, dirpath, numeric_owner=numeric_owner)
                self.utime(tarinfo, dirpath)
                self.chmod(tarinfo, dirpath)
            tatizo ExtractError kama e:
                ikiwa self.errorlevel > 1:
                    raise
                isipokua:
                    self._dbg(1, "tarfile: %s" % e)

    eleza extract(self, member, path="", set_attrs=Kweli, *, numeric_owner=Uongo):
        """Extract a member kutoka the archive to the current working directory,
           using its full name. Its file information ni extracted kama accurately
           kama possible. `member' may be a filename ama a TarInfo object. You can
           specify a different directory using `path'. File attributes (owner,
           mtime, mode) are set unless `set_attrs' ni Uongo. If `numeric_owner`
           ni Kweli, only the numbers kila user/group names are used na sio
           the names.
        """
        self._check("r")

        ikiwa isinstance(member, str):
            tarinfo = self.getmember(member)
        isipokua:
            tarinfo = member

        # Prepare the link target kila makelink().
        ikiwa tarinfo.islnk():
            tarinfo._link_target = os.path.join(path, tarinfo.linkname)

        jaribu:
            self._extract_member(tarinfo, os.path.join(path, tarinfo.name),
                                 set_attrs=set_attrs,
                                 numeric_owner=numeric_owner)
        tatizo OSError kama e:
            ikiwa self.errorlevel > 0:
                raise
            isipokua:
                ikiwa e.filename ni Tupu:
                    self._dbg(1, "tarfile: %s" % e.strerror)
                isipokua:
                    self._dbg(1, "tarfile: %s %r" % (e.strerror, e.filename))
        tatizo ExtractError kama e:
            ikiwa self.errorlevel > 1:
                raise
            isipokua:
                self._dbg(1, "tarfile: %s" % e)

    eleza extractfile(self, member):
        """Extract a member kutoka the archive kama a file object. `member' may be
           a filename ama a TarInfo object. If `member' ni a regular file ama a
           link, an io.BufferedReader object ni returned. Otherwise, Tupu is
           returned.
        """
        self._check("r")

        ikiwa isinstance(member, str):
            tarinfo = self.getmember(member)
        isipokua:
            tarinfo = member

        ikiwa tarinfo.isreg() ama tarinfo.type haiko kwenye SUPPORTED_TYPES:
            # Members ukijumuisha unknown types are treated kama regular files.
            rudisha self.fileobject(self, tarinfo)

        lasivyo tarinfo.islnk() ama tarinfo.issym():
            ikiwa isinstance(self.fileobj, _Stream):
                # A small but ugly workaround kila the case that someone tries
                # to extract a (sym)link kama a file-object kutoka a non-seekable
                # stream of tar blocks.
                ashiria StreamError("cannot extract (sym)link kama file object")
            isipokua:
                # A (sym)link's file object ni its target's file object.
                rudisha self.extractfile(self._find_link_target(tarinfo))
        isipokua:
            # If there's no data associated ukijumuisha the member (directory, chrdev,
            # blkdev, etc.), rudisha Tupu instead of a file object.
            rudisha Tupu

    eleza _extract_member(self, tarinfo, targetpath, set_attrs=Kweli,
                        numeric_owner=Uongo):
        """Extract the TarInfo object tarinfo to a physical
           file called targetpath.
        """
        # Fetch the TarInfo object kila the given name
        # na build the destination pathname, replacing
        # forward slashes to platform specific separators.
        targetpath = targetpath.rstrip("/")
        targetpath = targetpath.replace("/", os.sep)

        # Create all upper directories.
        upperdirs = os.path.dirname(targetpath)
        ikiwa upperdirs na sio os.path.exists(upperdirs):
            # Create directories that are sio part of the archive with
            # default permissions.
            os.makedirs(upperdirs)

        ikiwa tarinfo.islnk() ama tarinfo.issym():
            self._dbg(1, "%s -> %s" % (tarinfo.name, tarinfo.linkname))
        isipokua:
            self._dbg(1, tarinfo.name)

        ikiwa tarinfo.isreg():
            self.makefile(tarinfo, targetpath)
        lasivyo tarinfo.isdir():
            self.makedir(tarinfo, targetpath)
        lasivyo tarinfo.isfifo():
            self.makefifo(tarinfo, targetpath)
        lasivyo tarinfo.ischr() ama tarinfo.isblk():
            self.makedev(tarinfo, targetpath)
        lasivyo tarinfo.islnk() ama tarinfo.issym():
            self.makelink(tarinfo, targetpath)
        lasivyo tarinfo.type haiko kwenye SUPPORTED_TYPES:
            self.makeunknown(tarinfo, targetpath)
        isipokua:
            self.makefile(tarinfo, targetpath)

        ikiwa set_attrs:
            self.chown(tarinfo, targetpath, numeric_owner)
            ikiwa sio tarinfo.issym():
                self.chmod(tarinfo, targetpath)
                self.utime(tarinfo, targetpath)

    #--------------------------------------------------------------------------
    # Below are the different file methods. They are called via
    # _extract_member() when extract() ni called. They can be replaced kwenye a
    # subkundi to implement other functionality.

    eleza makedir(self, tarinfo, targetpath):
        """Make a directory called targetpath.
        """
        jaribu:
            # Use a safe mode kila the directory, the real mode ni set
            # later kwenye _extract_member().
            os.mkdir(targetpath, 0o700)
        tatizo FileExistsError:
            pita

    eleza makefile(self, tarinfo, targetpath):
        """Make a file called targetpath.
        """
        source = self.fileobj
        source.seek(tarinfo.offset_data)
        bufsize = self.copybufsize
        ukijumuisha bltn_open(targetpath, "wb") kama target:
            ikiwa tarinfo.sparse ni sio Tupu:
                kila offset, size kwenye tarinfo.sparse:
                    target.seek(offset)
                    copyfileobj(source, target, size, ReadError, bufsize)
                target.seek(tarinfo.size)
                target.truncate()
            isipokua:
                copyfileobj(source, target, tarinfo.size, ReadError, bufsize)

    eleza makeunknown(self, tarinfo, targetpath):
        """Make a file kutoka a TarInfo object ukijumuisha an unknown type
           at targetpath.
        """
        self.makefile(tarinfo, targetpath)
        self._dbg(1, "tarfile: Unknown file type %r, " \
                     "extracted kama regular file." % tarinfo.type)

    eleza makefifo(self, tarinfo, targetpath):
        """Make a fifo called targetpath.
        """
        ikiwa hasattr(os, "mkfifo"):
            os.mkfifo(targetpath)
        isipokua:
            ashiria ExtractError("fifo sio supported by system")

    eleza makedev(self, tarinfo, targetpath):
        """Make a character ama block device called targetpath.
        """
        ikiwa sio hasattr(os, "mknod") ama sio hasattr(os, "makedev"):
            ashiria ExtractError("special devices sio supported by system")

        mode = tarinfo.mode
        ikiwa tarinfo.isblk():
            mode |= stat.S_IFBLK
        isipokua:
            mode |= stat.S_IFCHR

        os.mknod(targetpath, mode,
                 os.makedev(tarinfo.devmajor, tarinfo.devminor))

    eleza makelink(self, tarinfo, targetpath):
        """Make a (symbolic) link called targetpath. If it cannot be created
          (platform limitation), we try to make a copy of the referenced file
          instead of a link.
        """
        jaribu:
            # For systems that support symbolic na hard links.
            ikiwa tarinfo.issym():
                os.symlink(tarinfo.linkname, targetpath)
            isipokua:
                # See extract().
                ikiwa os.path.exists(tarinfo._link_target):
                    os.link(tarinfo._link_target, targetpath)
                isipokua:
                    self._extract_member(self._find_link_target(tarinfo),
                                         targetpath)
        tatizo symlink_exception:
            jaribu:
                self._extract_member(self._find_link_target(tarinfo),
                                     targetpath)
            tatizo KeyError:
                ashiria ExtractError("unable to resolve link inside archive")

    eleza chown(self, tarinfo, targetpath, numeric_owner):
        """Set owner of targetpath according to tarinfo. If numeric_owner
           ni Kweli, use .gid/.uid instead of .gname/.uname. If numeric_owner
           ni Uongo, fall back to .gid/.uid when the search based on name
           fails.
        """
        ikiwa hasattr(os, "geteuid") na os.geteuid() == 0:
            # We have to be root to do so.
            g = tarinfo.gid
            u = tarinfo.uid
            ikiwa sio numeric_owner:
                jaribu:
                    ikiwa grp:
                        g = grp.getgrnam(tarinfo.gname)[2]
                tatizo KeyError:
                    pita
                jaribu:
                    ikiwa pwd:
                        u = pwd.getpwnam(tarinfo.uname)[2]
                tatizo KeyError:
                    pita
            jaribu:
                ikiwa tarinfo.issym() na hasattr(os, "lchown"):
                    os.lchown(targetpath, u, g)
                isipokua:
                    os.chown(targetpath, u, g)
            tatizo OSError:
                ashiria ExtractError("could sio change owner")

    eleza chmod(self, tarinfo, targetpath):
        """Set file permissions of targetpath according to tarinfo.
        """
        jaribu:
            os.chmod(targetpath, tarinfo.mode)
        tatizo OSError:
            ashiria ExtractError("could sio change mode")

    eleza utime(self, tarinfo, targetpath):
        """Set modification time of targetpath according to tarinfo.
        """
        ikiwa sio hasattr(os, 'utime'):
            rudisha
        jaribu:
            os.utime(targetpath, (tarinfo.mtime, tarinfo.mtime))
        tatizo OSError:
            ashiria ExtractError("could sio change modification time")

    #--------------------------------------------------------------------------
    eleza next(self):
        """Return the next member of the archive kama a TarInfo object, when
           TarFile ni opened kila reading. Return Tupu ikiwa there ni no more
           available.
        """
        self._check("ra")
        ikiwa self.firstmember ni sio Tupu:
            m = self.firstmember
            self.firstmember = Tupu
            rudisha m

        # Advance the file pointer.
        ikiwa self.offset != self.fileobj.tell():
            self.fileobj.seek(self.offset - 1)
            ikiwa sio self.fileobj.read(1):
                ashiria ReadError("unexpected end of data")

        # Read the next block.
        tarinfo = Tupu
        wakati Kweli:
            jaribu:
                tarinfo = self.tarinfo.fromtarfile(self)
            tatizo EOFHeaderError kama e:
                ikiwa self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    endelea
            tatizo InvalidHeaderError kama e:
                ikiwa self.ignore_zeros:
                    self._dbg(2, "0x%X: %s" % (self.offset, e))
                    self.offset += BLOCKSIZE
                    endelea
                lasivyo self.offset == 0:
                    ashiria ReadError(str(e))
            tatizo EmptyHeaderError:
                ikiwa self.offset == 0:
                    ashiria ReadError("empty file")
            tatizo TruncatedHeaderError kama e:
                ikiwa self.offset == 0:
                    ashiria ReadError(str(e))
            tatizo SubsequentHeaderError kama e:
                ashiria ReadError(str(e))
            koma

        ikiwa tarinfo ni sio Tupu:
            self.members.append(tarinfo)
        isipokua:
            self._loaded = Kweli

        rudisha tarinfo

    #--------------------------------------------------------------------------
    # Little helper methods:

    eleza _getmember(self, name, tarinfo=Tupu, normalize=Uongo):
        """Find an archive member by name kutoka bottom to top.
           If tarinfo ni given, it ni used kama the starting point.
        """
        # Ensure that all members have been loaded.
        members = self.getmembers()

        # Limit the member search list up to tarinfo.
        ikiwa tarinfo ni sio Tupu:
            members = members[:members.index(tarinfo)]

        ikiwa normalize:
            name = os.path.normpath(name)

        kila member kwenye reversed(members):
            ikiwa normalize:
                member_name = os.path.normpath(member.name)
            isipokua:
                member_name = member.name

            ikiwa name == member_name:
                rudisha member

    eleza _load(self):
        """Read through the entire archive file na look kila readable
           members.
        """
        wakati Kweli:
            tarinfo = self.next()
            ikiwa tarinfo ni Tupu:
                koma
        self._loaded = Kweli

    eleza _check(self, mode=Tupu):
        """Check ikiwa TarFile ni still open, na ikiwa the operation's mode
           corresponds to TarFile's mode.
        """
        ikiwa self.closed:
            ashiria OSError("%s ni closed" % self.__class__.__name__)
        ikiwa mode ni sio Tupu na self.mode haiko kwenye mode:
            ashiria OSError("bad operation kila mode %r" % self.mode)

    eleza _find_link_target(self, tarinfo):
        """Find the target member of a symlink ama hardlink member kwenye the
           archive.
        """
        ikiwa tarinfo.issym():
            # Always search the entire archive.
            linkname = "/".join(filter(Tupu, (os.path.dirname(tarinfo.name), tarinfo.linkname)))
            limit = Tupu
        isipokua:
            # Search the archive before the link, because a hard link is
            # just a reference to an already archived file.
            linkname = tarinfo.linkname
            limit = tarinfo

        member = self._getmember(linkname, tarinfo=limit, normalize=Kweli)
        ikiwa member ni Tupu:
            ashiria KeyError("linkname %r sio found" % linkname)
        rudisha member

    eleza __iter__(self):
        """Provide an iterator object.
        """
        ikiwa self._loaded:
            tuma kutoka self.members
            rudisha

        # Yield items using TarFile's next() method.
        # When all members have been read, set TarFile kama _loaded.
        index = 0
        # Fix kila SF #1100429: Under rare circumstances it can
        # happen that getmembers() ni called during iteration,
        # which will have already exhausted the next() method.
        ikiwa self.firstmember ni sio Tupu:
            tarinfo = self.next()
            index += 1
            tuma tarinfo

        wakati Kweli:
            ikiwa index < len(self.members):
                tarinfo = self.members[index]
            lasivyo sio self._loaded:
                tarinfo = self.next()
                ikiwa sio tarinfo:
                    self._loaded = Kweli
                    rudisha
            isipokua:
                rudisha
            index += 1
            tuma tarinfo

    eleza _dbg(self, level, msg):
        """Write debugging output to sys.stderr.
        """
        ikiwa level <= self.debug:
            andika(msg, file=sys.stderr)

    eleza __enter__(self):
        self._check()
        rudisha self

    eleza __exit__(self, type, value, traceback):
        ikiwa type ni Tupu:
            self.close()
        isipokua:
            # An exception occurred. We must sio call close() because
            # it would try to write end-of-archive blocks na padding.
            ikiwa sio self._extfileobj:
                self.fileobj.close()
            self.closed = Kweli

#--------------------
# exported functions
#--------------------
eleza is_tarfile(name):
    """Return Kweli ikiwa name points to a tar archive that we
       are able to handle, isipokua rudisha Uongo.
    """
    jaribu:
        t = open(name)
        t.close()
        rudisha Kweli
    tatizo TarError:
        rudisha Uongo

open = TarFile.open


eleza main():
    agiza argparse

    description = 'A simple command-line interface kila tarfile module.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--verbose', action='store_true', default=Uongo,
                        help='Verbose output')
    group = parser.add_mutually_exclusive_group(required=Kweli)
    group.add_argument('-l', '--list', metavar='<tarfile>',
                       help='Show listing of a tarfile')
    group.add_argument('-e', '--extract', nargs='+',
                       metavar=('<tarfile>', '<output_dir>'),
                       help='Extract tarfile into target dir')
    group.add_argument('-c', '--create', nargs='+',
                       metavar=('<name>', '<file>'),
                       help='Create tarfile kutoka sources')
    group.add_argument('-t', '--test', metavar='<tarfile>',
                       help='Test ikiwa a tarfile ni valid')
    args = parser.parse_args()

    ikiwa args.test ni sio Tupu:
        src = args.test
        ikiwa is_tarfile(src):
            ukijumuisha open(src, 'r') kama tar:
                tar.getmembers()
                andika(tar.getmembers(), file=sys.stderr)
            ikiwa args.verbose:
                andika('{!r} ni a tar archive.'.format(src))
        isipokua:
            parser.exit(1, '{!r} ni sio a tar archive.\n'.format(src))

    lasivyo args.list ni sio Tupu:
        src = args.list
        ikiwa is_tarfile(src):
            ukijumuisha TarFile.open(src, 'r:*') kama tf:
                tf.list(verbose=args.verbose)
        isipokua:
            parser.exit(1, '{!r} ni sio a tar archive.\n'.format(src))

    lasivyo args.extract ni sio Tupu:
        ikiwa len(args.extract) == 1:
            src = args.extract[0]
            curdir = os.curdir
        lasivyo len(args.extract) == 2:
            src, curdir = args.extract
        isipokua:
            parser.exit(1, parser.format_help())

        ikiwa is_tarfile(src):
            ukijumuisha TarFile.open(src, 'r:*') kama tf:
                tf.extractall(path=curdir)
            ikiwa args.verbose:
                ikiwa curdir == '.':
                    msg = '{!r} file ni extracted.'.format(src)
                isipokua:
                    msg = ('{!r} file ni extracted '
                           'into {!r} directory.').format(src, curdir)
                andika(msg)
        isipokua:
            parser.exit(1, '{!r} ni sio a tar archive.\n'.format(src))

    lasivyo args.create ni sio Tupu:
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
        tar_mode = 'w:' + compressions[ext] ikiwa ext kwenye compressions isipokua 'w'
        tar_files = args.create

        ukijumuisha TarFile.open(tar_name, tar_mode) kama tf:
            kila file_name kwenye tar_files:
                tf.add(file_name)

        ikiwa args.verbose:
            andika('{!r} file created.'.format(tar_name))

ikiwa __name__ == '__main__':
    main()
