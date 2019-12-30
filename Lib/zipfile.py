"""
Read na write ZIP files.

XXX references to utf-8 need further investigation.
"""
agiza binascii
agiza functools
agiza importlib.util
agiza io
agiza itertools
agiza os
agiza posixpath
agiza shutil
agiza stat
agiza struct
agiza sys
agiza threading
agiza time

jaribu:
    agiza zlib # We may need its compression method
    crc32 = zlib.crc32
tatizo ImportError:
    zlib = Tupu
    crc32 = binascii.crc32

jaribu:
    agiza bz2 # We may need its compression method
tatizo ImportError:
    bz2 = Tupu

jaribu:
    agiza lzma # We may need its compression method
tatizo ImportError:
    lzma = Tupu

__all__ = ["BadZipFile", "BadZipfile", "error",
           "ZIP_STORED", "ZIP_DEFLATED", "ZIP_BZIP2", "ZIP_LZMA",
           "is_zipfile", "ZipInfo", "ZipFile", "PyZipFile", "LargeZipFile"]

kundi BadZipFile(Exception):
    pita


kundi LargeZipFile(Exception):
    """
    Raised when writing a zipfile, the zipfile requires ZIP64 extensions
    na those extensions are disabled.
    """

error = BadZipfile = BadZipFile      # Pre-3.2 compatibility names


ZIP64_LIMIT = (1 << 31) - 1
ZIP_FILECOUNT_LIMIT = (1 << 16) - 1
ZIP_MAX_COMMENT = (1 << 16) - 1

# constants kila Zip file compression methods
ZIP_STORED = 0
ZIP_DEFLATED = 8
ZIP_BZIP2 = 12
ZIP_LZMA = 14
# Other ZIP compression methods sio supported

DEFAULT_VERSION = 20
ZIP64_VERSION = 45
BZIP2_VERSION = 46
LZMA_VERSION = 63
# we recognize (but sio necessarily support) all features up to that version
MAX_EXTRACT_VERSION = 63

# Below are some formats na associated data kila reading/writing headers using
# the struct module.  The names na structures of headers/records are those used
# kwenye the PKWARE description of the ZIP file format:
#     http://www.pkware.com/documents/casestudies/APPNOTE.TXT
# (URL valid kama of January 2008)

# The "end of central directory" structure, magic number, size, na indices
# (section V.I kwenye the format document)
structEndArchive = b"<4s4H2LH"
stringEndArchive = b"PK\005\006"
sizeEndCentDir = struct.calcsize(structEndArchive)

_ECD_SIGNATURE = 0
_ECD_DISK_NUMBER = 1
_ECD_DISK_START = 2
_ECD_ENTRIES_THIS_DISK = 3
_ECD_ENTRIES_TOTAL = 4
_ECD_SIZE = 5
_ECD_OFFSET = 6
_ECD_COMMENT_SIZE = 7
# These last two indices are sio part of the structure kama defined kwenye the
# spec, but they are used internally by this module kama a convenience
_ECD_COMMENT = 8
_ECD_LOCATION = 9

# The "central directory" structure, magic number, size, na indices
# of entries kwenye the structure (section V.F kwenye the format document)
structCentralDir = "<4s4B4HL2L5H2L"
stringCentralDir = b"PK\001\002"
sizeCentralDir = struct.calcsize(structCentralDir)

# indexes of entries kwenye the central directory structure
_CD_SIGNATURE = 0
_CD_CREATE_VERSION = 1
_CD_CREATE_SYSTEM = 2
_CD_EXTRACT_VERSION = 3
_CD_EXTRACT_SYSTEM = 4
_CD_FLAG_BITS = 5
_CD_COMPRESS_TYPE = 6
_CD_TIME = 7
_CD_DATE = 8
_CD_CRC = 9
_CD_COMPRESSED_SIZE = 10
_CD_UNCOMPRESSED_SIZE = 11
_CD_FILENAME_LENGTH = 12
_CD_EXTRA_FIELD_LENGTH = 13
_CD_COMMENT_LENGTH = 14
_CD_DISK_NUMBER_START = 15
_CD_INTERNAL_FILE_ATTRIBUTES = 16
_CD_EXTERNAL_FILE_ATTRIBUTES = 17
_CD_LOCAL_HEADER_OFFSET = 18

# The "local file header" structure, magic number, size, na indices
# (section V.A kwenye the format document)
structFileHeader = "<4s2B4HL2L2H"
stringFileHeader = b"PK\003\004"
sizeFileHeader = struct.calcsize(structFileHeader)

_FH_SIGNATURE = 0
_FH_EXTRACT_VERSION = 1
_FH_EXTRACT_SYSTEM = 2
_FH_GENERAL_PURPOSE_FLAG_BITS = 3
_FH_COMPRESSION_METHOD = 4
_FH_LAST_MOD_TIME = 5
_FH_LAST_MOD_DATE = 6
_FH_CRC = 7
_FH_COMPRESSED_SIZE = 8
_FH_UNCOMPRESSED_SIZE = 9
_FH_FILENAME_LENGTH = 10
_FH_EXTRA_FIELD_LENGTH = 11

# The "Zip64 end of central directory locator" structure, magic number, na size
structEndArchive64Locator = "<4sLQL"
stringEndArchive64Locator = b"PK\x06\x07"
sizeEndCentDir64Locator = struct.calcsize(structEndArchive64Locator)

# The "Zip64 end of central directory" record, magic number, size, na indices
# (section V.G kwenye the format document)
structEndArchive64 = "<4sQ2H2L4Q"
stringEndArchive64 = b"PK\x06\x06"
sizeEndCentDir64 = struct.calcsize(structEndArchive64)

_CD64_SIGNATURE = 0
_CD64_DIRECTORY_RECSIZE = 1
_CD64_CREATE_VERSION = 2
_CD64_EXTRACT_VERSION = 3
_CD64_DISK_NUMBER = 4
_CD64_DISK_NUMBER_START = 5
_CD64_NUMBER_ENTRIES_THIS_DISK = 6
_CD64_NUMBER_ENTRIES_TOTAL = 7
_CD64_DIRECTORY_SIZE = 8
_CD64_OFFSET_START_CENTDIR = 9

_DD_SIGNATURE = 0x08074b50

_EXTRA_FIELD_STRUCT = struct.Struct('<HH')

eleza _strip_extra(extra, xids):
    # Remove Extra Fields ukijumuisha specified IDs.
    unpack = _EXTRA_FIELD_STRUCT.unpack
    modified = Uongo
    buffer = []
    start = i = 0
    wakati i + 4 <= len(extra):
        xid, xlen = unpack(extra[i : i + 4])
        j = i + 4 + xlen
        ikiwa xid kwenye xids:
            ikiwa i != start:
                buffer.append(extra[start : i])
            start = j
            modified = Kweli
        i = j
    ikiwa sio modified:
        rudisha extra
    rudisha b''.join(buffer)

eleza _check_zipfile(fp):
    jaribu:
        ikiwa _EndRecData(fp):
            rudisha Kweli         # file has correct magic number
    tatizo OSError:
        pita
    rudisha Uongo

eleza is_zipfile(filename):
    """Quickly see ikiwa a file ni a ZIP file by checking the magic number.

    The filename argument may be a file ama file-like object too.
    """
    result = Uongo
    jaribu:
        ikiwa hasattr(filename, "read"):
            result = _check_zipfile(fp=filename)
        isipokua:
            ukijumuisha open(filename, "rb") kama fp:
                result = _check_zipfile(fp)
    tatizo OSError:
        pita
    rudisha result

eleza _EndRecData64(fpin, offset, endrec):
    """
    Read the ZIP64 end-of-archive records na use that to update endrec
    """
    jaribu:
        fpin.seek(offset - sizeEndCentDir64Locator, 2)
    tatizo OSError:
        # If the seek fails, the file ni sio large enough to contain a ZIP64
        # end-of-archive record, so just rudisha the end record we were given.
        rudisha endrec

    data = fpin.read(sizeEndCentDir64Locator)
    ikiwa len(data) != sizeEndCentDir64Locator:
        rudisha endrec
    sig, diskno, reloff, disks = struct.unpack(structEndArchive64Locator, data)
    ikiwa sig != stringEndArchive64Locator:
        rudisha endrec

    ikiwa diskno != 0 ama disks > 1:
        ashiria BadZipFile("zipfiles that span multiple disks are sio supported")

    # Assume no 'zip64 extensible data'
    fpin.seek(offset - sizeEndCentDir64Locator - sizeEndCentDir64, 2)
    data = fpin.read(sizeEndCentDir64)
    ikiwa len(data) != sizeEndCentDir64:
        rudisha endrec
    sig, sz, create_version, read_version, disk_num, disk_dir, \
        dircount, dircount2, dirsize, diroffset = \
        struct.unpack(structEndArchive64, data)
    ikiwa sig != stringEndArchive64:
        rudisha endrec

    # Update the original endrec using data kutoka the ZIP64 record
    endrec[_ECD_SIGNATURE] = sig
    endrec[_ECD_DISK_NUMBER] = disk_num
    endrec[_ECD_DISK_START] = disk_dir
    endrec[_ECD_ENTRIES_THIS_DISK] = dircount
    endrec[_ECD_ENTRIES_TOTAL] = dircount2
    endrec[_ECD_SIZE] = dirsize
    endrec[_ECD_OFFSET] = diroffset
    rudisha endrec


eleza _EndRecData(fpin):
    """Return data kutoka the "End of Central Directory" record, ama Tupu.

    The data ni a list of the nine items kwenye the ZIP "End of central dir"
    record followed by a tenth item, the file seek offset of this record."""

    # Determine file size
    fpin.seek(0, 2)
    filesize = fpin.tell()

    # Check to see ikiwa this ni ZIP file ukijumuisha no archive comment (the
    # "end of central directory" structure should be the last item kwenye the
    # file ikiwa this ni the case).
    jaribu:
        fpin.seek(-sizeEndCentDir, 2)
    tatizo OSError:
        rudisha Tupu
    data = fpin.read()
    ikiwa (len(data) == sizeEndCentDir na
        data[0:4] == stringEndArchive na
        data[-2:] == b"\000\000"):
        # the signature ni correct na there's no comment, unpack structure
        endrec = struct.unpack(structEndArchive, data)
        endrec=list(endrec)

        # Append a blank comment na record start offset
        endrec.append(b"")
        endrec.append(filesize - sizeEndCentDir)

        # Try to read the "Zip64 end of central directory" structure
        rudisha _EndRecData64(fpin, -sizeEndCentDir, endrec)

    # Either this ni sio a ZIP file, ama it ni a ZIP file ukijumuisha an archive
    # comment.  Search the end of the file kila the "end of central directory"
    # record signature. The comment ni the last item kwenye the ZIP file na may be
    # up to 64K long.  It ni assumed that the "end of central directory" magic
    # number does sio appear kwenye the comment.
    maxCommentStart = max(filesize - (1 << 16) - sizeEndCentDir, 0)
    fpin.seek(maxCommentStart, 0)
    data = fpin.read()
    start = data.rfind(stringEndArchive)
    ikiwa start >= 0:
        # found the magic number; attempt to unpack na interpret
        recData = data[start:start+sizeEndCentDir]
        ikiwa len(recData) != sizeEndCentDir:
            # Zip file ni corrupted.
            rudisha Tupu
        endrec = list(struct.unpack(structEndArchive, recData))
        commentSize = endrec[_ECD_COMMENT_SIZE] #as claimed by the zip file
        comment = data[start+sizeEndCentDir:start+sizeEndCentDir+commentSize]
        endrec.append(comment)
        endrec.append(maxCommentStart + start)

        # Try to read the "Zip64 end of central directory" structure
        rudisha _EndRecData64(fpin, maxCommentStart + start - filesize,
                             endrec)

    # Unable to find a valid end of central directory structure
    rudisha Tupu


kundi ZipInfo (object):
    """Class ukijumuisha attributes describing each file kwenye the ZIP archive."""

    __slots__ = (
        'orig_filename',
        'filename',
        'date_time',
        'compress_type',
        '_compresslevel',
        'comment',
        'extra',
        'create_system',
        'create_version',
        'extract_version',
        'reserved',
        'flag_bits',
        'volume',
        'internal_attr',
        'external_attr',
        'header_offset',
        'CRC',
        'compress_size',
        'file_size',
        '_raw_time',
    )

    eleza __init__(self, filename="NoName", date_time=(1980,1,1,0,0,0)):
        self.orig_filename = filename   # Original file name kwenye archive

        # Terminate the file name at the first null byte.  Null bytes kwenye file
        # names are used kama tricks by viruses kwenye archives.
        null_byte = filename.find(chr(0))
        ikiwa null_byte >= 0:
            filename = filename[0:null_byte]
        # This ni used to ensure paths kwenye generated ZIP files always use
        # forward slashes kama the directory separator, kama required by the
        # ZIP format specification.
        ikiwa os.sep != "/" na os.sep kwenye filename:
            filename = filename.replace(os.sep, "/")

        self.filename = filename        # Normalized file name
        self.date_time = date_time      # year, month, day, hour, min, sec

        ikiwa date_time[0] < 1980:
            ashiria ValueError('ZIP does sio support timestamps before 1980')

        # Standard values:
        self.compress_type = ZIP_STORED # Type of compression kila the file
        self._compresslevel = Tupu      # Level kila the compressor
        self.comment = b""              # Comment kila each file
        self.extra = b""                # ZIP extra data
        ikiwa sys.platform == 'win32':
            self.create_system = 0          # System which created ZIP archive
        isipokua:
            # Assume everything isipokua ni unix-y
            self.create_system = 3          # System which created ZIP archive
        self.create_version = DEFAULT_VERSION  # Version which created ZIP archive
        self.extract_version = DEFAULT_VERSION # Version needed to extract archive
        self.reserved = 0               # Must be zero
        self.flag_bits = 0              # ZIP flag bits
        self.volume = 0                 # Volume number of file header
        self.internal_attr = 0          # Internal attributes
        self.external_attr = 0          # External file attributes
        # Other attributes are set by kundi ZipFile:
        # header_offset         Byte offset to the file header
        # CRC                   CRC-32 of the uncompressed file
        # compress_size         Size of the compressed file
        # file_size             Size of the uncompressed file

    eleza __repr__(self):
        result = ['<%s filename=%r' % (self.__class__.__name__, self.filename)]
        ikiwa self.compress_type != ZIP_STORED:
            result.append(' compress_type=%s' %
                          compressor_names.get(self.compress_type,
                                               self.compress_type))
        hi = self.external_attr >> 16
        lo = self.external_attr & 0xFFFF
        ikiwa hi:
            result.append(' filemode=%r' % stat.filemode(hi))
        ikiwa lo:
            result.append(' external_attr=%#x' % lo)
        isdir = self.is_dir()
        ikiwa sio isdir ama self.file_size:
            result.append(' file_size=%r' % self.file_size)
        ikiwa ((sio isdir ama self.compress_size) na
            (self.compress_type != ZIP_STORED ama
             self.file_size != self.compress_size)):
            result.append(' compress_size=%r' % self.compress_size)
        result.append('>')
        rudisha ''.join(result)

    eleza FileHeader(self, zip64=Tupu):
        """Return the per-file header kama a bytes object."""
        dt = self.date_time
        dosdate = (dt[0] - 1980) << 9 | dt[1] << 5 | dt[2]
        dostime = dt[3] << 11 | dt[4] << 5 | (dt[5] // 2)
        ikiwa self.flag_bits & 0x08:
            # Set these to zero because we write them after the file data
            CRC = compress_size = file_size = 0
        isipokua:
            CRC = self.CRC
            compress_size = self.compress_size
            file_size = self.file_size

        extra = self.extra

        min_version = 0
        ikiwa zip64 ni Tupu:
            zip64 = file_size > ZIP64_LIMIT ama compress_size > ZIP64_LIMIT
        ikiwa zip64:
            fmt = '<HHQQ'
            extra = extra + struct.pack(fmt,
                                        1, struct.calcsize(fmt)-4, file_size, compress_size)
        ikiwa file_size > ZIP64_LIMIT ama compress_size > ZIP64_LIMIT:
            ikiwa sio zip64:
                ashiria LargeZipFile("Filesize would require ZIP64 extensions")
            # File ni larger than what fits into a 4 byte integer,
            # fall back to the ZIP64 extension
            file_size = 0xffffffff
            compress_size = 0xffffffff
            min_version = ZIP64_VERSION

        ikiwa self.compress_type == ZIP_BZIP2:
            min_version = max(BZIP2_VERSION, min_version)
        lasivyo self.compress_type == ZIP_LZMA:
            min_version = max(LZMA_VERSION, min_version)

        self.extract_version = max(min_version, self.extract_version)
        self.create_version = max(min_version, self.create_version)
        filename, flag_bits = self._encodeFilenameFlags()
        header = struct.pack(structFileHeader, stringFileHeader,
                             self.extract_version, self.reserved, flag_bits,
                             self.compress_type, dostime, dosdate, CRC,
                             compress_size, file_size,
                             len(filename), len(extra))
        rudisha header + filename + extra

    eleza _encodeFilenameFlags(self):
        jaribu:
            rudisha self.filename.encode('ascii'), self.flag_bits
        tatizo UnicodeEncodeError:
            rudisha self.filename.encode('utf-8'), self.flag_bits | 0x800

    eleza _decodeExtra(self):
        # Try to decode the extra field.
        extra = self.extra
        unpack = struct.unpack
        wakati len(extra) >= 4:
            tp, ln = unpack('<HH', extra[:4])
            ikiwa ln+4 > len(extra):
                ashiria BadZipFile("Corrupt extra field %04x (size=%d)" % (tp, ln))
            ikiwa tp == 0x0001:
                ikiwa ln >= 24:
                    counts = unpack('<QQQ', extra[4:28])
                lasivyo ln == 16:
                    counts = unpack('<QQ', extra[4:20])
                lasivyo ln == 8:
                    counts = unpack('<Q', extra[4:12])
                lasivyo ln == 0:
                    counts = ()
                isipokua:
                    ashiria BadZipFile("Corrupt extra field %04x (size=%d)" % (tp, ln))

                idx = 0

                # ZIP64 extension (large files and/or large archives)
                ikiwa self.file_size kwenye (0xffffffffffffffff, 0xffffffff):
                    self.file_size = counts[idx]
                    idx += 1

                ikiwa self.compress_size == 0xFFFFFFFF:
                    self.compress_size = counts[idx]
                    idx += 1

                ikiwa self.header_offset == 0xffffffff:
                    old = self.header_offset
                    self.header_offset = counts[idx]
                    idx+=1

            extra = extra[ln+4:]

    @classmethod
    eleza from_file(cls, filename, arcname=Tupu, *, strict_timestamps=Kweli):
        """Construct an appropriate ZipInfo kila a file on the filesystem.

        filename should be the path to a file ama directory on the filesystem.

        arcname ni the name which it will have within the archive (by default,
        this will be the same kama filename, but without a drive letter na with
        leading path separators removed).
        """
        ikiwa isinstance(filename, os.PathLike):
            filename = os.fspath(filename)
        st = os.stat(filename)
        isdir = stat.S_ISDIR(st.st_mode)
        mtime = time.localtime(st.st_mtime)
        date_time = mtime[0:6]
        ikiwa sio strict_timestamps na date_time[0] < 1980:
            date_time = (1980, 1, 1, 0, 0, 0)
        lasivyo sio strict_timestamps na date_time[0] > 2107:
            date_time = (2107, 12, 31, 23, 59, 59)
        # Create ZipInfo instance to store file information
        ikiwa arcname ni Tupu:
            arcname = filename
        arcname = os.path.normpath(os.path.splitdrive(arcname)[1])
        wakati arcname[0] kwenye (os.sep, os.altsep):
            arcname = arcname[1:]
        ikiwa isdir:
            arcname += '/'
        zinfo = cls(arcname, date_time)
        zinfo.external_attr = (st.st_mode & 0xFFFF) << 16  # Unix attributes
        ikiwa isdir:
            zinfo.file_size = 0
            zinfo.external_attr |= 0x10  # MS-DOS directory flag
        isipokua:
            zinfo.file_size = st.st_size

        rudisha zinfo

    eleza is_dir(self):
        """Return Kweli ikiwa this archive member ni a directory."""
        rudisha self.filename[-1] == '/'


# ZIP encryption uses the CRC32 one-byte primitive kila scrambling some
# internal keys. We noticed that a direct implementation ni faster than
# relying on binascii.crc32().

_crctable = Tupu
eleza _gen_crc(crc):
    kila j kwenye range(8):
        ikiwa crc & 1:
            crc = (crc >> 1) ^ 0xEDB88320
        isipokua:
            crc >>= 1
    rudisha crc

# ZIP supports a password-based form of encryption. Even though known
# plaintext attacks have been found against it, it ni still useful
# to be able to get data out of such a file.
#
# Usage:
#     zd = _ZipDecrypter(mypwd)
#     plain_bytes = zd(cypher_bytes)

eleza _ZipDecrypter(pwd):
    key0 = 305419896
    key1 = 591751049
    key2 = 878082192

    global _crctable
    ikiwa _crctable ni Tupu:
        _crctable = list(map(_gen_crc, range(256)))
    crctable = _crctable

    eleza crc32(ch, crc):
        """Compute the CRC32 primitive on one byte."""
        rudisha (crc >> 8) ^ crctable[(crc ^ ch) & 0xFF]

    eleza update_keys(c):
        nonlocal key0, key1, key2
        key0 = crc32(c, key0)
        key1 = (key1 + (key0 & 0xFF)) & 0xFFFFFFFF
        key1 = (key1 * 134775813 + 1) & 0xFFFFFFFF
        key2 = crc32(key1 >> 24, key2)

    kila p kwenye pwd:
        update_keys(p)

    eleza decrypter(data):
        """Decrypt a bytes object."""
        result = bytearray()
        append = result.append
        kila c kwenye data:
            k = key2 | 2
            c ^= ((k * (k^1)) >> 8) & 0xFF
            update_keys(c)
            append(c)
        rudisha bytes(result)

    rudisha decrypter


kundi LZMACompressor:

    eleza __init__(self):
        self._comp = Tupu

    eleza _init(self):
        props = lzma._encode_filter_properties({'id': lzma.FILTER_LZMA1})
        self._comp = lzma.LZMACompressor(lzma.FORMAT_RAW, filters=[
            lzma._decode_filter_properties(lzma.FILTER_LZMA1, props)
        ])
        rudisha struct.pack('<BBH', 9, 4, len(props)) + props

    eleza compress(self, data):
        ikiwa self._comp ni Tupu:
            rudisha self._init() + self._comp.compress(data)
        rudisha self._comp.compress(data)

    eleza flush(self):
        ikiwa self._comp ni Tupu:
            rudisha self._init() + self._comp.flush()
        rudisha self._comp.flush()


kundi LZMADecompressor:

    eleza __init__(self):
        self._decomp = Tupu
        self._unconsumed = b''
        self.eof = Uongo

    eleza decompress(self, data):
        ikiwa self._decomp ni Tupu:
            self._unconsumed += data
            ikiwa len(self._unconsumed) <= 4:
                rudisha b''
            psize, = struct.unpack('<H', self._unconsumed[2:4])
            ikiwa len(self._unconsumed) <= 4 + psize:
                rudisha b''

            self._decomp = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[
                lzma._decode_filter_properties(lzma.FILTER_LZMA1,
                                               self._unconsumed[4:4 + psize])
            ])
            data = self._unconsumed[4 + psize:]
            toa self._unconsumed

        result = self._decomp.decompress(data)
        self.eof = self._decomp.eof
        rudisha result


compressor_names = {
    0: 'store',
    1: 'shrink',
    2: 'reduce',
    3: 'reduce',
    4: 'reduce',
    5: 'reduce',
    6: 'implode',
    7: 'tokenize',
    8: 'deflate',
    9: 'deflate64',
    10: 'implode',
    12: 'bzip2',
    14: 'lzma',
    18: 'terse',
    19: 'lz77',
    97: 'wavpack',
    98: 'ppmd',
}

eleza _check_compression(compression):
    ikiwa compression == ZIP_STORED:
        pita
    lasivyo compression == ZIP_DEFLATED:
        ikiwa sio zlib:
            ashiria RuntimeError(
                "Compression requires the (missing) zlib module")
    lasivyo compression == ZIP_BZIP2:
        ikiwa sio bz2:
            ashiria RuntimeError(
                "Compression requires the (missing) bz2 module")
    lasivyo compression == ZIP_LZMA:
        ikiwa sio lzma:
            ashiria RuntimeError(
                "Compression requires the (missing) lzma module")
    isipokua:
        ashiria NotImplementedError("That compression method ni sio supported")


eleza _get_compressor(compress_type, compresslevel=Tupu):
    ikiwa compress_type == ZIP_DEFLATED:
        ikiwa compresslevel ni sio Tupu:
            rudisha zlib.compressobj(compresslevel, zlib.DEFLATED, -15)
        rudisha zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
    lasivyo compress_type == ZIP_BZIP2:
        ikiwa compresslevel ni sio Tupu:
            rudisha bz2.BZ2Compressor(compresslevel)
        rudisha bz2.BZ2Compressor()
    # compresslevel ni ignored kila ZIP_LZMA
    lasivyo compress_type == ZIP_LZMA:
        rudisha LZMACompressor()
    isipokua:
        rudisha Tupu


eleza _get_decompressor(compress_type):
    _check_compression(compress_type)
    ikiwa compress_type == ZIP_STORED:
        rudisha Tupu
    lasivyo compress_type == ZIP_DEFLATED:
        rudisha zlib.decompressobj(-15)
    lasivyo compress_type == ZIP_BZIP2:
        rudisha bz2.BZ2Decompressor()
    lasivyo compress_type == ZIP_LZMA:
        rudisha LZMADecompressor()
    isipokua:
        descr = compressor_names.get(compress_type)
        ikiwa descr:
            ashiria NotImplementedError("compression type %d (%s)" % (compress_type, descr))
        isipokua:
            ashiria NotImplementedError("compression type %d" % (compress_type,))


kundi _SharedFile:
    eleza __init__(self, file, pos, close, lock, writing):
        self._file = file
        self._pos = pos
        self._close = close
        self._lock = lock
        self._writing = writing
        self.seekable = file.seekable
        self.tell = file.tell

    eleza seek(self, offset, whence=0):
        ukijumuisha self._lock:
            ikiwa self._writing():
                ashiria ValueError("Can't reposition kwenye the ZIP file wakati "
                        "there ni an open writing handle on it. "
                        "Close the writing handle before trying to read.")
            self._file.seek(offset, whence)
            self._pos = self._file.tell()
            rudisha self._pos

    eleza read(self, n=-1):
        ukijumuisha self._lock:
            ikiwa self._writing():
                ashiria ValueError("Can't read kutoka the ZIP file wakati there "
                        "is an open writing handle on it. "
                        "Close the writing handle before trying to read.")
            self._file.seek(self._pos)
            data = self._file.read(n)
            self._pos = self._file.tell()
            rudisha data

    eleza close(self):
        ikiwa self._file ni sio Tupu:
            fileobj = self._file
            self._file = Tupu
            self._close(fileobj)

# Provide the tell method kila unseekable stream
kundi _Tellable:
    eleza __init__(self, fp):
        self.fp = fp
        self.offset = 0

    eleza write(self, data):
        n = self.fp.write(data)
        self.offset += n
        rudisha n

    eleza tell(self):
        rudisha self.offset

    eleza flush(self):
        self.fp.flush()

    eleza close(self):
        self.fp.close()


kundi ZipExtFile(io.BufferedIOBase):
    """File-like object kila reading an archive member.
       Is returned by ZipFile.open().
    """

    # Max size supported by decompressor.
    MAX_N = 1 << 31 - 1

    # Read kutoka compressed files kwenye 4k blocks.
    MIN_READ_SIZE = 4096

    # Chunk size to read during seek
    MAX_SEEK_READ = 1 << 24

    eleza __init__(self, fileobj, mode, zipinfo, decrypter=Tupu,
                 close_fileobj=Uongo):
        self._fileobj = fileobj
        self._decrypter = decrypter
        self._close_fileobj = close_fileobj

        self._compress_type = zipinfo.compress_type
        self._compress_left = zipinfo.compress_size
        self._left = zipinfo.file_size

        self._decompressor = _get_decompressor(self._compress_type)

        self._eof = Uongo
        self._readbuffer = b''
        self._offset = 0

        self.newlines = Tupu

        # Adjust read size kila encrypted files since the first 12 bytes
        # are kila the encryption/password information.
        ikiwa self._decrypter ni sio Tupu:
            self._compress_left -= 12

        self.mode = mode
        self.name = zipinfo.filename

        ikiwa hasattr(zipinfo, 'CRC'):
            self._expected_crc = zipinfo.CRC
            self._running_crc = crc32(b'')
        isipokua:
            self._expected_crc = Tupu

        self._seekable = Uongo
        jaribu:
            ikiwa fileobj.seekable():
                self._orig_compress_start = fileobj.tell()
                self._orig_compress_size = zipinfo.compress_size
                self._orig_file_size = zipinfo.file_size
                self._orig_start_crc = self._running_crc
                self._seekable = Kweli
        tatizo AttributeError:
            pita

    eleza __repr__(self):
        result = ['<%s.%s' % (self.__class__.__module__,
                              self.__class__.__qualname__)]
        ikiwa sio self.closed:
            result.append(' name=%r mode=%r' % (self.name, self.mode))
            ikiwa self._compress_type != ZIP_STORED:
                result.append(' compress_type=%s' %
                              compressor_names.get(self._compress_type,
                                                   self._compress_type))
        isipokua:
            result.append(' [closed]')
        result.append('>')
        rudisha ''.join(result)

    eleza readline(self, limit=-1):
        """Read na rudisha a line kutoka the stream.

        If limit ni specified, at most limit bytes will be read.
        """

        ikiwa limit < 0:
            # Shortcut common case - newline found kwenye buffer.
            i = self._readbuffer.find(b'\n', self._offset) + 1
            ikiwa i > 0:
                line = self._readbuffer[self._offset: i]
                self._offset = i
                rudisha line

        rudisha io.BufferedIOBase.readline(self, limit)

    eleza peek(self, n=1):
        """Returns buffered bytes without advancing the position."""
        ikiwa n > len(self._readbuffer) - self._offset:
            chunk = self.read(n)
            ikiwa len(chunk) > self._offset:
                self._readbuffer = chunk + self._readbuffer[self._offset:]
                self._offset = 0
            isipokua:
                self._offset -= len(chunk)

        # Return up to 512 bytes to reduce allocation overhead kila tight loops.
        rudisha self._readbuffer[self._offset: self._offset + 512]

    eleza readable(self):
        rudisha Kweli

    eleza read(self, n=-1):
        """Read na rudisha up to n bytes.
        If the argument ni omitted, Tupu, ama negative, data ni read na returned until EOF ni reached.
        """
        ikiwa n ni Tupu ama n < 0:
            buf = self._readbuffer[self._offset:]
            self._readbuffer = b''
            self._offset = 0
            wakati sio self._eof:
                buf += self._read1(self.MAX_N)
            rudisha buf

        end = n + self._offset
        ikiwa end < len(self._readbuffer):
            buf = self._readbuffer[self._offset:end]
            self._offset = end
            rudisha buf

        n = end - len(self._readbuffer)
        buf = self._readbuffer[self._offset:]
        self._readbuffer = b''
        self._offset = 0
        wakati n > 0 na sio self._eof:
            data = self._read1(n)
            ikiwa n < len(data):
                self._readbuffer = data
                self._offset = n
                buf += data[:n]
                koma
            buf += data
            n -= len(data)
        rudisha buf

    eleza _update_crc(self, newdata):
        # Update the CRC using the given data.
        ikiwa self._expected_crc ni Tupu:
            # No need to compute the CRC ikiwa we don't have a reference value
            rudisha
        self._running_crc = crc32(newdata, self._running_crc)
        # Check the CRC ikiwa we're at the end of the file
        ikiwa self._eof na self._running_crc != self._expected_crc:
            ashiria BadZipFile("Bad CRC-32 kila file %r" % self.name)

    eleza read1(self, n):
        """Read up to n bytes ukijumuisha at most one read() system call."""

        ikiwa n ni Tupu ama n < 0:
            buf = self._readbuffer[self._offset:]
            self._readbuffer = b''
            self._offset = 0
            wakati sio self._eof:
                data = self._read1(self.MAX_N)
                ikiwa data:
                    buf += data
                    koma
            rudisha buf

        end = n + self._offset
        ikiwa end < len(self._readbuffer):
            buf = self._readbuffer[self._offset:end]
            self._offset = end
            rudisha buf

        n = end - len(self._readbuffer)
        buf = self._readbuffer[self._offset:]
        self._readbuffer = b''
        self._offset = 0
        ikiwa n > 0:
            wakati sio self._eof:
                data = self._read1(n)
                ikiwa n < len(data):
                    self._readbuffer = data
                    self._offset = n
                    buf += data[:n]
                    koma
                ikiwa data:
                    buf += data
                    koma
        rudisha buf

    eleza _read1(self, n):
        # Read up to n compressed bytes ukijumuisha at most one read() system call,
        # decrypt na decompress them.
        ikiwa self._eof ama n <= 0:
            rudisha b''

        # Read kutoka file.
        ikiwa self._compress_type == ZIP_DEFLATED:
            ## Handle unconsumed data.
            data = self._decompressor.unconsumed_tail
            ikiwa n > len(data):
                data += self._read2(n - len(data))
        isipokua:
            data = self._read2(n)

        ikiwa self._compress_type == ZIP_STORED:
            self._eof = self._compress_left <= 0
        lasivyo self._compress_type == ZIP_DEFLATED:
            n = max(n, self.MIN_READ_SIZE)
            data = self._decompressor.decompress(data, n)
            self._eof = (self._decompressor.eof ama
                         self._compress_left <= 0 na
                         sio self._decompressor.unconsumed_tail)
            ikiwa self._eof:
                data += self._decompressor.flush()
        isipokua:
            data = self._decompressor.decompress(data)
            self._eof = self._decompressor.eof ama self._compress_left <= 0

        data = data[:self._left]
        self._left -= len(data)
        ikiwa self._left <= 0:
            self._eof = Kweli
        self._update_crc(data)
        rudisha data

    eleza _read2(self, n):
        ikiwa self._compress_left <= 0:
            rudisha b''

        n = max(n, self.MIN_READ_SIZE)
        n = min(n, self._compress_left)

        data = self._fileobj.read(n)
        self._compress_left -= len(data)
        ikiwa sio data:
            ashiria EOFError

        ikiwa self._decrypter ni sio Tupu:
            data = self._decrypter(data)
        rudisha data

    eleza close(self):
        jaribu:
            ikiwa self._close_fileobj:
                self._fileobj.close()
        mwishowe:
            super().close()

    eleza seekable(self):
        rudisha self._seekable

    eleza seek(self, offset, whence=0):
        ikiwa sio self._seekable:
            ashiria io.UnsupportedOperation("underlying stream ni sio seekable")
        curr_pos = self.tell()
        ikiwa whence == 0: # Seek kutoka start of file
            new_pos = offset
        lasivyo whence == 1: # Seek kutoka current position
            new_pos = curr_pos + offset
        lasivyo whence == 2: # Seek kutoka EOF
            new_pos = self._orig_file_size + offset
        isipokua:
            ashiria ValueError("whence must be os.SEEK_SET (0), "
                             "os.SEEK_CUR (1), ama os.SEEK_END (2)")

        ikiwa new_pos > self._orig_file_size:
            new_pos = self._orig_file_size

        ikiwa new_pos < 0:
            new_pos = 0

        read_offset = new_pos - curr_pos
        buff_offset = read_offset + self._offset

        ikiwa buff_offset >= 0 na buff_offset < len(self._readbuffer):
            # Just move the _offset index ikiwa the new position ni kwenye the _readbuffer
            self._offset = buff_offset
            read_offset = 0
        lasivyo read_offset < 0:
            # Position ni before the current position. Reset the ZipExtFile
            self._fileobj.seek(self._orig_compress_start)
            self._running_crc = self._orig_start_crc
            self._compress_left = self._orig_compress_size
            self._left = self._orig_file_size
            self._readbuffer = b''
            self._offset = 0
            self._decompressor = _get_decompressor(self._compress_type)
            self._eof = Uongo
            read_offset = new_pos

        wakati read_offset > 0:
            read_len = min(self.MAX_SEEK_READ, read_offset)
            self.read(read_len)
            read_offset -= read_len

        rudisha self.tell()

    eleza tell(self):
        ikiwa sio self._seekable:
            ashiria io.UnsupportedOperation("underlying stream ni sio seekable")
        filepos = self._orig_file_size - self._left - len(self._readbuffer) + self._offset
        rudisha filepos


kundi _ZipWriteFile(io.BufferedIOBase):
    eleza __init__(self, zf, zinfo, zip64):
        self._zinfo = zinfo
        self._zip64 = zip64
        self._zipfile = zf
        self._compressor = _get_compressor(zinfo.compress_type,
                                           zinfo._compresslevel)
        self._file_size = 0
        self._compress_size = 0
        self._crc = 0

    @property
    eleza _fileobj(self):
        rudisha self._zipfile.fp

    eleza writable(self):
        rudisha Kweli

    eleza write(self, data):
        ikiwa self.closed:
            ashiria ValueError('I/O operation on closed file.')
        nbytes = len(data)
        self._file_size += nbytes
        self._crc = crc32(data, self._crc)
        ikiwa self._compressor:
            data = self._compressor.compress(data)
            self._compress_size += len(data)
        self._fileobj.write(data)
        rudisha nbytes

    eleza close(self):
        ikiwa self.closed:
            rudisha
        jaribu:
            super().close()
            # Flush any data kutoka the compressor, na update header info
            ikiwa self._compressor:
                buf = self._compressor.flush()
                self._compress_size += len(buf)
                self._fileobj.write(buf)
                self._zinfo.compress_size = self._compress_size
            isipokua:
                self._zinfo.compress_size = self._file_size
            self._zinfo.CRC = self._crc
            self._zinfo.file_size = self._file_size

            # Write updated header info
            ikiwa self._zinfo.flag_bits & 0x08:
                # Write CRC na file sizes after the file data
                fmt = '<LLQQ' ikiwa self._zip64 isipokua '<LLLL'
                self._fileobj.write(struct.pack(fmt, _DD_SIGNATURE, self._zinfo.CRC,
                    self._zinfo.compress_size, self._zinfo.file_size))
                self._zipfile.start_dir = self._fileobj.tell()
            isipokua:
                ikiwa sio self._zip64:
                    ikiwa self._file_size > ZIP64_LIMIT:
                        ashiria RuntimeError(
                            'File size unexpectedly exceeded ZIP64 limit')
                    ikiwa self._compress_size > ZIP64_LIMIT:
                        ashiria RuntimeError(
                            'Compressed size unexpectedly exceeded ZIP64 limit')
                # Seek backwards na write file header (which will now include
                # correct CRC na file sizes)

                # Preserve current position kwenye file
                self._zipfile.start_dir = self._fileobj.tell()
                self._fileobj.seek(self._zinfo.header_offset)
                self._fileobj.write(self._zinfo.FileHeader(self._zip64))
                self._fileobj.seek(self._zipfile.start_dir)

            # Successfully written: Add file to our caches
            self._zipfile.filelist.append(self._zinfo)
            self._zipfile.NameToInfo[self._zinfo.filename] = self._zinfo
        mwishowe:
            self._zipfile._writing = Uongo



kundi ZipFile:
    """ Class ukijumuisha methods to open, read, write, close, list zip files.

    z = ZipFile(file, mode="r", compression=ZIP_STORED, allowZip64=Kweli,
                compresslevel=Tupu)

    file: Either the path to the file, ama a file-like object.
          If it ni a path, the file will be opened na closed by ZipFile.
    mode: The mode can be either read 'r', write 'w', exclusive create 'x',
          ama append 'a'.
    compression: ZIP_STORED (no compression), ZIP_DEFLATED (requires zlib),
                 ZIP_BZIP2 (requires bz2) ama ZIP_LZMA (requires lzma).
    allowZip64: ikiwa Kweli ZipFile will create files ukijumuisha ZIP64 extensions when
                needed, otherwise it will ashiria an exception when this would
                be necessary.
    compresslevel: Tupu (default kila the given compression type) ama an integer
                   specifying the level to pita to the compressor.
                   When using ZIP_STORED ama ZIP_LZMA this keyword has no effect.
                   When using ZIP_DEFLATED integers 0 through 9 are accepted.
                   When using ZIP_BZIP2 integers 1 through 9 are accepted.

    """

    fp = Tupu                   # Set here since __del__ checks it
    _windows_illegal_name_trans_table = Tupu

    eleza __init__(self, file, mode="r", compression=ZIP_STORED, allowZip64=Kweli,
                 compresslevel=Tupu, *, strict_timestamps=Kweli):
        """Open the ZIP file ukijumuisha mode read 'r', write 'w', exclusive create 'x',
        ama append 'a'."""
        ikiwa mode haiko kwenye ('r', 'w', 'x', 'a'):
            ashiria ValueError("ZipFile requires mode 'r', 'w', 'x', ama 'a'")

        _check_compression(compression)

        self._allowZip64 = allowZip64
        self._didModify = Uongo
        self.debug = 0  # Level of printing: 0 through 3
        self.NameToInfo = {}    # Find file info given name
        self.filelist = []      # List of ZipInfo instances kila archive
        self.compression = compression  # Method of compression
        self.compresslevel = compresslevel
        self.mode = mode
        self.pwd = Tupu
        self._comment = b''
        self._strict_timestamps = strict_timestamps

        # Check ikiwa we were pitaed a file-like object
        ikiwa isinstance(file, os.PathLike):
            file = os.fspath(file)
        ikiwa isinstance(file, str):
            # No, it's a filename
            self._filePassed = 0
            self.filename = file
            modeDict = {'r' : 'rb', 'w': 'w+b', 'x': 'x+b', 'a' : 'r+b',
                        'r+b': 'w+b', 'w+b': 'wb', 'x+b': 'xb'}
            filemode = modeDict[mode]
            wakati Kweli:
                jaribu:
                    self.fp = io.open(file, filemode)
                tatizo OSError:
                    ikiwa filemode kwenye modeDict:
                        filemode = modeDict[filemode]
                        endelea
                    raise
                koma
        isipokua:
            self._filePassed = 1
            self.fp = file
            self.filename = getattr(file, 'name', Tupu)
        self._fileRefCnt = 1
        self._lock = threading.RLock()
        self._seekable = Kweli
        self._writing = Uongo

        jaribu:
            ikiwa mode == 'r':
                self._RealGetContents()
            lasivyo mode kwenye ('w', 'x'):
                # set the modified flag so central directory gets written
                # even ikiwa no files are added to the archive
                self._didModify = Kweli
                jaribu:
                    self.start_dir = self.fp.tell()
                tatizo (AttributeError, OSError):
                    self.fp = _Tellable(self.fp)
                    self.start_dir = 0
                    self._seekable = Uongo
                isipokua:
                    # Some file-like objects can provide tell() but sio seek()
                    jaribu:
                        self.fp.seek(self.start_dir)
                    tatizo (AttributeError, OSError):
                        self._seekable = Uongo
            lasivyo mode == 'a':
                jaribu:
                    # See ikiwa file ni a zip file
                    self._RealGetContents()
                    # seek to start of directory na overwrite
                    self.fp.seek(self.start_dir)
                tatizo BadZipFile:
                    # file ni sio a zip file, just append
                    self.fp.seek(0, 2)

                    # set the modified flag so central directory gets written
                    # even ikiwa no files are added to the archive
                    self._didModify = Kweli
                    self.start_dir = self.fp.tell()
            isipokua:
                ashiria ValueError("Mode must be 'r', 'w', 'x', ama 'a'")
        tatizo:
            fp = self.fp
            self.fp = Tupu
            self._fpclose(fp)
            raise

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type, value, traceback):
        self.close()

    eleza __repr__(self):
        result = ['<%s.%s' % (self.__class__.__module__,
                              self.__class__.__qualname__)]
        ikiwa self.fp ni sio Tupu:
            ikiwa self._filePassed:
                result.append(' file=%r' % self.fp)
            lasivyo self.filename ni sio Tupu:
                result.append(' filename=%r' % self.filename)
            result.append(' mode=%r' % self.mode)
        isipokua:
            result.append(' [closed]')
        result.append('>')
        rudisha ''.join(result)

    eleza _RealGetContents(self):
        """Read kwenye the table of contents kila the ZIP file."""
        fp = self.fp
        jaribu:
            endrec = _EndRecData(fp)
        tatizo OSError:
            ashiria BadZipFile("File ni sio a zip file")
        ikiwa sio endrec:
            ashiria BadZipFile("File ni sio a zip file")
        ikiwa self.debug > 1:
            andika(endrec)
        size_cd = endrec[_ECD_SIZE]             # bytes kwenye central directory
        offset_cd = endrec[_ECD_OFFSET]         # offset of central directory
        self._comment = endrec[_ECD_COMMENT]    # archive comment

        # "concat" ni zero, unless zip was concatenated to another file
        concat = endrec[_ECD_LOCATION] - size_cd - offset_cd
        ikiwa endrec[_ECD_SIGNATURE] == stringEndArchive64:
            # If Zip64 extension structures are present, account kila them
            concat -= (sizeEndCentDir64 + sizeEndCentDir64Locator)

        ikiwa self.debug > 2:
            inferred = concat + offset_cd
            andika("given, inferred, offset", offset_cd, inferred, concat)
        # self.start_dir:  Position of start of central directory
        self.start_dir = offset_cd + concat
        fp.seek(self.start_dir, 0)
        data = fp.read(size_cd)
        fp = io.BytesIO(data)
        total = 0
        wakati total < size_cd:
            centdir = fp.read(sizeCentralDir)
            ikiwa len(centdir) != sizeCentralDir:
                ashiria BadZipFile("Truncated central directory")
            centdir = struct.unpack(structCentralDir, centdir)
            ikiwa centdir[_CD_SIGNATURE] != stringCentralDir:
                ashiria BadZipFile("Bad magic number kila central directory")
            ikiwa self.debug > 2:
                andika(centdir)
            filename = fp.read(centdir[_CD_FILENAME_LENGTH])
            flags = centdir[5]
            ikiwa flags & 0x800:
                # UTF-8 file names extension
                filename = filename.decode('utf-8')
            isipokua:
                # Historical ZIP filename encoding
                filename = filename.decode('cp437')
            # Create ZipInfo instance to store file information
            x = ZipInfo(filename)
            x.extra = fp.read(centdir[_CD_EXTRA_FIELD_LENGTH])
            x.comment = fp.read(centdir[_CD_COMMENT_LENGTH])
            x.header_offset = centdir[_CD_LOCAL_HEADER_OFFSET]
            (x.create_version, x.create_system, x.extract_version, x.reserved,
             x.flag_bits, x.compress_type, t, d,
             x.CRC, x.compress_size, x.file_size) = centdir[1:12]
            ikiwa x.extract_version > MAX_EXTRACT_VERSION:
                ashiria NotImplementedError("zip file version %.1f" %
                                          (x.extract_version / 10))
            x.volume, x.internal_attr, x.external_attr = centdir[15:18]
            # Convert date/time code to (year, month, day, hour, min, sec)
            x._raw_time = t
            x.date_time = ( (d>>9)+1980, (d>>5)&0xF, d&0x1F,
                            t>>11, (t>>5)&0x3F, (t&0x1F) * 2 )

            x._decodeExtra()
            x.header_offset = x.header_offset + concat
            self.filelist.append(x)
            self.NameToInfo[x.filename] = x

            # update total bytes read kutoka central directory
            total = (total + sizeCentralDir + centdir[_CD_FILENAME_LENGTH]
                     + centdir[_CD_EXTRA_FIELD_LENGTH]
                     + centdir[_CD_COMMENT_LENGTH])

            ikiwa self.debug > 2:
                andika("total", total)


    eleza namelist(self):
        """Return a list of file names kwenye the archive."""
        rudisha [data.filename kila data kwenye self.filelist]

    eleza infolist(self):
        """Return a list of kundi ZipInfo instances kila files kwenye the
        archive."""
        rudisha self.filelist

    eleza printdir(self, file=Tupu):
        """Print a table of contents kila the zip file."""
        andika("%-46s %19s %12s" % ("File Name", "Modified    ", "Size"),
              file=file)
        kila zinfo kwenye self.filelist:
            date = "%d-%02d-%02d %02d:%02d:%02d" % zinfo.date_time[:6]
            andika("%-46s %s %12d" % (zinfo.filename, date, zinfo.file_size),
                  file=file)

    eleza testzip(self):
        """Read all the files na check the CRC."""
        chunk_size = 2 ** 20
        kila zinfo kwenye self.filelist:
            jaribu:
                # Read by chunks, to avoid an OverflowError ama a
                # MemoryError ukijumuisha very large embedded files.
                ukijumuisha self.open(zinfo.filename, "r") kama f:
                    wakati f.read(chunk_size):     # Check CRC-32
                        pita
            tatizo BadZipFile:
                rudisha zinfo.filename

    eleza getinfo(self, name):
        """Return the instance of ZipInfo given 'name'."""
        info = self.NameToInfo.get(name)
        ikiwa info ni Tupu:
            ashiria KeyError(
                'There ni no item named %r kwenye the archive' % name)

        rudisha info

    eleza setpassword(self, pwd):
        """Set default password kila encrypted files."""
        ikiwa pwd na sio isinstance(pwd, bytes):
            ashiria TypeError("pwd: expected bytes, got %s" % type(pwd).__name__)
        ikiwa pwd:
            self.pwd = pwd
        isipokua:
            self.pwd = Tupu

    @property
    eleza comment(self):
        """The comment text associated ukijumuisha the ZIP file."""
        rudisha self._comment

    @comment.setter
    eleza comment(self, comment):
        ikiwa sio isinstance(comment, bytes):
            ashiria TypeError("comment: expected bytes, got %s" % type(comment).__name__)
        # check kila valid comment length
        ikiwa len(comment) > ZIP_MAX_COMMENT:
            agiza warnings
            warnings.warn('Archive comment ni too long; truncating to %d bytes'
                          % ZIP_MAX_COMMENT, stacklevel=2)
            comment = comment[:ZIP_MAX_COMMENT]
        self._comment = comment
        self._didModify = Kweli

    eleza read(self, name, pwd=Tupu):
        """Return file bytes kila name."""
        ukijumuisha self.open(name, "r", pwd) kama fp:
            rudisha fp.read()

    eleza open(self, name, mode="r", pwd=Tupu, *, force_zip64=Uongo):
        """Return file-like object kila 'name'.

        name ni a string kila the file name within the ZIP file, ama a ZipInfo
        object.

        mode should be 'r' to read a file already kwenye the ZIP file, ama 'w' to
        write to a file newly added to the archive.

        pwd ni the password to decrypt files (only used kila reading).

        When writing, ikiwa the file size ni sio known kwenye advance but may exceed
        2 GiB, pita force_zip64 to use the ZIP64 format, which can handle large
        files.  If the size ni known kwenye advance, it ni best to pita a ZipInfo
        instance kila name, ukijumuisha zinfo.file_size set.
        """
        ikiwa mode haiko kwenye {"r", "w"}:
            ashiria ValueError('open() requires mode "r" ama "w"')
        ikiwa pwd na sio isinstance(pwd, bytes):
            ashiria TypeError("pwd: expected bytes, got %s" % type(pwd).__name__)
        ikiwa pwd na (mode == "w"):
            ashiria ValueError("pwd ni only supported kila reading files")
        ikiwa sio self.fp:
            ashiria ValueError(
                "Attempt to use ZIP archive that was already closed")

        # Make sure we have an info object
        ikiwa isinstance(name, ZipInfo):
            # 'name' ni already an info object
            zinfo = name
        lasivyo mode == 'w':
            zinfo = ZipInfo(name)
            zinfo.compress_type = self.compression
            zinfo._compresslevel = self.compresslevel
        isipokua:
            # Get info object kila name
            zinfo = self.getinfo(name)

        ikiwa mode == 'w':
            rudisha self._open_to_write(zinfo, force_zip64=force_zip64)

        ikiwa self._writing:
            ashiria ValueError("Can't read kutoka the ZIP file wakati there "
                    "is an open writing handle on it. "
                    "Close the writing handle before trying to read.")

        # Open kila reading:
        self._fileRefCnt += 1
        zef_file = _SharedFile(self.fp, zinfo.header_offset,
                               self._fpclose, self._lock, lambda: self._writing)
        jaribu:
            # Skip the file header:
            fheader = zef_file.read(sizeFileHeader)
            ikiwa len(fheader) != sizeFileHeader:
                ashiria BadZipFile("Truncated file header")
            fheader = struct.unpack(structFileHeader, fheader)
            ikiwa fheader[_FH_SIGNATURE] != stringFileHeader:
                ashiria BadZipFile("Bad magic number kila file header")

            fname = zef_file.read(fheader[_FH_FILENAME_LENGTH])
            ikiwa fheader[_FH_EXTRA_FIELD_LENGTH]:
                zef_file.read(fheader[_FH_EXTRA_FIELD_LENGTH])

            ikiwa zinfo.flag_bits & 0x20:
                # Zip 2.7: compressed patched data
                ashiria NotImplementedError("compressed patched data (flag bit 5)")

            ikiwa zinfo.flag_bits & 0x40:
                # strong encryption
                ashiria NotImplementedError("strong encryption (flag bit 6)")

            ikiwa zinfo.flag_bits & 0x800:
                # UTF-8 filename
                fname_str = fname.decode("utf-8")
            isipokua:
                fname_str = fname.decode("cp437")

            ikiwa fname_str != zinfo.orig_filename:
                ashiria BadZipFile(
                    'File name kwenye directory %r na header %r differ.'
                    % (zinfo.orig_filename, fname))

            # check kila encrypted flag & handle password
            is_encrypted = zinfo.flag_bits & 0x1
            zd = Tupu
            ikiwa is_encrypted:
                ikiwa sio pwd:
                    pwd = self.pwd
                ikiwa sio pwd:
                    ashiria RuntimeError("File %r ni encrypted, password "
                                       "required kila extraction" % name)

                zd = _ZipDecrypter(pwd)
                # The first 12 bytes kwenye the cypher stream ni an encryption header
                #  used to strengthen the algorithm. The first 11 bytes are
                #  completely random, wakati the 12th contains the MSB of the CRC,
                #  ama the MSB of the file time depending on the header type
                #  na ni used to check the correctness of the password.
                header = zef_file.read(12)
                h = zd(header[0:12])
                ikiwa zinfo.flag_bits & 0x8:
                    # compare against the file type kutoka extended local headers
                    check_byte = (zinfo._raw_time >> 8) & 0xff
                isipokua:
                    # compare against the CRC otherwise
                    check_byte = (zinfo.CRC >> 24) & 0xff
                ikiwa h[11] != check_byte:
                    ashiria RuntimeError("Bad password kila file %r" % name)

            rudisha ZipExtFile(zef_file, mode, zinfo, zd, Kweli)
        tatizo:
            zef_file.close()
            raise

    eleza _open_to_write(self, zinfo, force_zip64=Uongo):
        ikiwa force_zip64 na sio self._allowZip64:
            ashiria ValueError(
                "force_zip64 ni Kweli, but allowZip64 was Uongo when opening "
                "the ZIP file."
            )
        ikiwa self._writing:
            ashiria ValueError("Can't write to the ZIP file wakati there ni "
                             "another write handle open on it. "
                             "Close the first handle before opening another.")

        # Sizes na CRC are overwritten ukijumuisha correct data after processing the file
        ikiwa sio hasattr(zinfo, 'file_size'):
            zinfo.file_size = 0
        zinfo.compress_size = 0
        zinfo.CRC = 0

        zinfo.flag_bits = 0x00
        ikiwa zinfo.compress_type == ZIP_LZMA:
            # Compressed data includes an end-of-stream (EOS) marker
            zinfo.flag_bits |= 0x02
        ikiwa sio self._seekable:
            zinfo.flag_bits |= 0x08

        ikiwa sio zinfo.external_attr:
            zinfo.external_attr = 0o600 << 16  # permissions: ?rw-------

        # Compressed size can be larger than uncompressed size
        zip64 = self._allowZip64 na \
                (force_zip64 ama zinfo.file_size * 1.05 > ZIP64_LIMIT)

        ikiwa self._seekable:
            self.fp.seek(self.start_dir)
        zinfo.header_offset = self.fp.tell()

        self._writecheck(zinfo)
        self._didModify = Kweli

        self.fp.write(zinfo.FileHeader(zip64))

        self._writing = Kweli
        rudisha _ZipWriteFile(self, zinfo, zip64)

    eleza extract(self, member, path=Tupu, pwd=Tupu):
        """Extract a member kutoka the archive to the current working directory,
           using its full name. Its file information ni extracted kama accurately
           kama possible. `member' may be a filename ama a ZipInfo object. You can
           specify a different directory using `path'.
        """
        ikiwa path ni Tupu:
            path = os.getcwd()
        isipokua:
            path = os.fspath(path)

        rudisha self._extract_member(member, path, pwd)

    eleza extractall(self, path=Tupu, members=Tupu, pwd=Tupu):
        """Extract all members kutoka the archive to the current working
           directory. `path' specifies a different directory to extract to.
           `members' ni optional na must be a subset of the list returned
           by namelist().
        """
        ikiwa members ni Tupu:
            members = self.namelist()

        ikiwa path ni Tupu:
            path = os.getcwd()
        isipokua:
            path = os.fspath(path)

        kila zipinfo kwenye members:
            self._extract_member(zipinfo, path, pwd)

    @classmethod
    eleza _sanitize_windows_name(cls, arcname, pathsep):
        """Replace bad characters na remove trailing dots kutoka parts."""
        table = cls._windows_illegal_name_trans_table
        ikiwa sio table:
            illegal = ':<>|"?*'
            table = str.maketrans(illegal, '_' * len(illegal))
            cls._windows_illegal_name_trans_table = table
        arcname = arcname.translate(table)
        # remove trailing dots
        arcname = (x.rstrip('.') kila x kwenye arcname.split(pathsep))
        # rejoin, removing empty parts.
        arcname = pathsep.join(x kila x kwenye arcname ikiwa x)
        rudisha arcname

    eleza _extract_member(self, member, targetpath, pwd):
        """Extract the ZipInfo object 'member' to a physical
           file on the path targetpath.
        """
        ikiwa sio isinstance(member, ZipInfo):
            member = self.getinfo(member)

        # build the destination pathname, replacing
        # forward slashes to platform specific separators.
        arcname = member.filename.replace('/', os.path.sep)

        ikiwa os.path.altsep:
            arcname = arcname.replace(os.path.altsep, os.path.sep)
        # interpret absolute pathname kama relative, remove drive letter ama
        # UNC path, redundant separators, "." na ".." components.
        arcname = os.path.splitdrive(arcname)[1]
        invalid_path_parts = ('', os.path.curdir, os.path.pardir)
        arcname = os.path.sep.join(x kila x kwenye arcname.split(os.path.sep)
                                   ikiwa x haiko kwenye invalid_path_parts)
        ikiwa os.path.sep == '\\':
            # filter illegal characters on Windows
            arcname = self._sanitize_windows_name(arcname, os.path.sep)

        targetpath = os.path.join(targetpath, arcname)
        targetpath = os.path.normpath(targetpath)

        # Create all upper directories ikiwa necessary.
        upperdirs = os.path.dirname(targetpath)
        ikiwa upperdirs na sio os.path.exists(upperdirs):
            os.makedirs(upperdirs)

        ikiwa member.is_dir():
            ikiwa sio os.path.isdir(targetpath):
                os.mkdir(targetpath)
            rudisha targetpath

        ukijumuisha self.open(member, pwd=pwd) kama source, \
             open(targetpath, "wb") kama target:
            shutil.copyfileobj(source, target)

        rudisha targetpath

    eleza _writecheck(self, zinfo):
        """Check kila errors before writing a file to the archive."""
        ikiwa zinfo.filename kwenye self.NameToInfo:
            agiza warnings
            warnings.warn('Duplicate name: %r' % zinfo.filename, stacklevel=3)
        ikiwa self.mode haiko kwenye ('w', 'x', 'a'):
            ashiria ValueError("write() requires mode 'w', 'x', ama 'a'")
        ikiwa sio self.fp:
            ashiria ValueError(
                "Attempt to write ZIP archive that was already closed")
        _check_compression(zinfo.compress_type)
        ikiwa sio self._allowZip64:
            requires_zip64 = Tupu
            ikiwa len(self.filelist) >= ZIP_FILECOUNT_LIMIT:
                requires_zip64 = "Files count"
            lasivyo zinfo.file_size > ZIP64_LIMIT:
                requires_zip64 = "Filesize"
            lasivyo zinfo.header_offset > ZIP64_LIMIT:
                requires_zip64 = "Zipfile size"
            ikiwa requires_zip64:
                ashiria LargeZipFile(requires_zip64 +
                                   " would require ZIP64 extensions")

    eleza write(self, filename, arcname=Tupu,
              compress_type=Tupu, compresslevel=Tupu):
        """Put the bytes kutoka filename into the archive under the name
        arcname."""
        ikiwa sio self.fp:
            ashiria ValueError(
                "Attempt to write to ZIP archive that was already closed")
        ikiwa self._writing:
            ashiria ValueError(
                "Can't write to ZIP archive wakati an open writing handle exists"
            )

        zinfo = ZipInfo.from_file(filename, arcname,
                                  strict_timestamps=self._strict_timestamps)

        ikiwa zinfo.is_dir():
            zinfo.compress_size = 0
            zinfo.CRC = 0
        isipokua:
            ikiwa compress_type ni sio Tupu:
                zinfo.compress_type = compress_type
            isipokua:
                zinfo.compress_type = self.compression

            ikiwa compresslevel ni sio Tupu:
                zinfo._compresslevel = compresslevel
            isipokua:
                zinfo._compresslevel = self.compresslevel

        ikiwa zinfo.is_dir():
            ukijumuisha self._lock:
                ikiwa self._seekable:
                    self.fp.seek(self.start_dir)
                zinfo.header_offset = self.fp.tell()  # Start of header bytes
                ikiwa zinfo.compress_type == ZIP_LZMA:
                # Compressed data includes an end-of-stream (EOS) marker
                    zinfo.flag_bits |= 0x02

                self._writecheck(zinfo)
                self._didModify = Kweli

                self.filelist.append(zinfo)
                self.NameToInfo[zinfo.filename] = zinfo
                self.fp.write(zinfo.FileHeader(Uongo))
                self.start_dir = self.fp.tell()
        isipokua:
            ukijumuisha open(filename, "rb") kama src, self.open(zinfo, 'w') kama dest:
                shutil.copyfileobj(src, dest, 1024*8)

    eleza writestr(self, zinfo_or_arcname, data,
                 compress_type=Tupu, compresslevel=Tupu):
        """Write a file into the archive.  The contents ni 'data', which
        may be either a 'str' ama a 'bytes' instance; ikiwa it ni a 'str',
        it ni encoded kama UTF-8 first.
        'zinfo_or_arcname' ni either a ZipInfo instance ama
        the name of the file kwenye the archive."""
        ikiwa isinstance(data, str):
            data = data.encode("utf-8")
        ikiwa sio isinstance(zinfo_or_arcname, ZipInfo):
            zinfo = ZipInfo(filename=zinfo_or_arcname,
                            date_time=time.localtime(time.time())[:6])
            zinfo.compress_type = self.compression
            zinfo._compresslevel = self.compresslevel
            ikiwa zinfo.filename[-1] == '/':
                zinfo.external_attr = 0o40775 << 16   # drwxrwxr-x
                zinfo.external_attr |= 0x10           # MS-DOS directory flag
            isipokua:
                zinfo.external_attr = 0o600 << 16     # ?rw-------
        isipokua:
            zinfo = zinfo_or_arcname

        ikiwa sio self.fp:
            ashiria ValueError(
                "Attempt to write to ZIP archive that was already closed")
        ikiwa self._writing:
            ashiria ValueError(
                "Can't write to ZIP archive wakati an open writing handle exists."
            )

        ikiwa compress_type ni sio Tupu:
            zinfo.compress_type = compress_type

        ikiwa compresslevel ni sio Tupu:
            zinfo._compresslevel = compresslevel

        zinfo.file_size = len(data)            # Uncompressed size
        ukijumuisha self._lock:
            ukijumuisha self.open(zinfo, mode='w') kama dest:
                dest.write(data)

    eleza __del__(self):
        """Call the "close()" method kwenye case the user forgot."""
        self.close()

    eleza close(self):
        """Close the file, na kila mode 'w', 'x' na 'a' write the ending
        records."""
        ikiwa self.fp ni Tupu:
            rudisha

        ikiwa self._writing:
            ashiria ValueError("Can't close the ZIP file wakati there ni "
                             "an open writing handle on it. "
                             "Close the writing handle before closing the zip.")

        jaribu:
            ikiwa self.mode kwenye ('w', 'x', 'a') na self._didModify: # write ending records
                ukijumuisha self._lock:
                    ikiwa self._seekable:
                        self.fp.seek(self.start_dir)
                    self._write_end_record()
        mwishowe:
            fp = self.fp
            self.fp = Tupu
            self._fpclose(fp)

    eleza _write_end_record(self):
        kila zinfo kwenye self.filelist:         # write central directory
            dt = zinfo.date_time
            dosdate = (dt[0] - 1980) << 9 | dt[1] << 5 | dt[2]
            dostime = dt[3] << 11 | dt[4] << 5 | (dt[5] // 2)
            extra = []
            ikiwa zinfo.file_size > ZIP64_LIMIT \
               ama zinfo.compress_size > ZIP64_LIMIT:
                extra.append(zinfo.file_size)
                extra.append(zinfo.compress_size)
                file_size = 0xffffffff
                compress_size = 0xffffffff
            isipokua:
                file_size = zinfo.file_size
                compress_size = zinfo.compress_size

            ikiwa zinfo.header_offset > ZIP64_LIMIT:
                extra.append(zinfo.header_offset)
                header_offset = 0xffffffff
            isipokua:
                header_offset = zinfo.header_offset

            extra_data = zinfo.extra
            min_version = 0
            ikiwa extra:
                # Append a ZIP64 field to the extra's
                extra_data = _strip_extra(extra_data, (1,))
                extra_data = struct.pack(
                    '<HH' + 'Q'*len(extra),
                    1, 8*len(extra), *extra) + extra_data

                min_version = ZIP64_VERSION

            ikiwa zinfo.compress_type == ZIP_BZIP2:
                min_version = max(BZIP2_VERSION, min_version)
            lasivyo zinfo.compress_type == ZIP_LZMA:
                min_version = max(LZMA_VERSION, min_version)

            extract_version = max(min_version, zinfo.extract_version)
            create_version = max(min_version, zinfo.create_version)
            jaribu:
                filename, flag_bits = zinfo._encodeFilenameFlags()
                centdir = struct.pack(structCentralDir,
                                      stringCentralDir, create_version,
                                      zinfo.create_system, extract_version, zinfo.reserved,
                                      flag_bits, zinfo.compress_type, dostime, dosdate,
                                      zinfo.CRC, compress_size, file_size,
                                      len(filename), len(extra_data), len(zinfo.comment),
                                      0, zinfo.internal_attr, zinfo.external_attr,
                                      header_offset)
            tatizo DeprecationWarning:
                andika((structCentralDir, stringCentralDir, create_version,
                       zinfo.create_system, extract_version, zinfo.reserved,
                       zinfo.flag_bits, zinfo.compress_type, dostime, dosdate,
                       zinfo.CRC, compress_size, file_size,
                       len(zinfo.filename), len(extra_data), len(zinfo.comment),
                       0, zinfo.internal_attr, zinfo.external_attr,
                       header_offset), file=sys.stderr)
                raise
            self.fp.write(centdir)
            self.fp.write(filename)
            self.fp.write(extra_data)
            self.fp.write(zinfo.comment)

        pos2 = self.fp.tell()
        # Write end-of-zip-archive record
        centDirCount = len(self.filelist)
        centDirSize = pos2 - self.start_dir
        centDirOffset = self.start_dir
        requires_zip64 = Tupu
        ikiwa centDirCount > ZIP_FILECOUNT_LIMIT:
            requires_zip64 = "Files count"
        lasivyo centDirOffset > ZIP64_LIMIT:
            requires_zip64 = "Central directory offset"
        lasivyo centDirSize > ZIP64_LIMIT:
            requires_zip64 = "Central directory size"
        ikiwa requires_zip64:
            # Need to write the ZIP64 end-of-archive records
            ikiwa sio self._allowZip64:
                ashiria LargeZipFile(requires_zip64 +
                                   " would require ZIP64 extensions")
            zip64endrec = struct.pack(
                structEndArchive64, stringEndArchive64,
                44, 45, 45, 0, 0, centDirCount, centDirCount,
                centDirSize, centDirOffset)
            self.fp.write(zip64endrec)

            zip64locrec = struct.pack(
                structEndArchive64Locator,
                stringEndArchive64Locator, 0, pos2, 1)
            self.fp.write(zip64locrec)
            centDirCount = min(centDirCount, 0xFFFF)
            centDirSize = min(centDirSize, 0xFFFFFFFF)
            centDirOffset = min(centDirOffset, 0xFFFFFFFF)

        endrec = struct.pack(structEndArchive, stringEndArchive,
                             0, 0, centDirCount, centDirCount,
                             centDirSize, centDirOffset, len(self._comment))
        self.fp.write(endrec)
        self.fp.write(self._comment)
        self.fp.flush()

    eleza _fpclose(self, fp):
        assert self._fileRefCnt > 0
        self._fileRefCnt -= 1
        ikiwa sio self._fileRefCnt na sio self._filePassed:
            fp.close()


kundi PyZipFile(ZipFile):
    """Class to create ZIP archives ukijumuisha Python library files na packages."""

    eleza __init__(self, file, mode="r", compression=ZIP_STORED,
                 allowZip64=Kweli, optimize=-1):
        ZipFile.__init__(self, file, mode=mode, compression=compression,
                         allowZip64=allowZip64)
        self._optimize = optimize

    eleza writepy(self, pathname, basename="", filterfunc=Tupu):
        """Add all files kutoka "pathname" to the ZIP archive.

        If pathname ni a package directory, search the directory na
        all package subdirectories recursively kila all *.py na enter
        the modules into the archive.  If pathname ni a plain
        directory, listdir *.py na enter all modules.  Else, pathname
        must be a Python *.py file na the module will be put into the
        archive.  Added modules are always module.pyc.
        This method will compile the module.py into module.pyc if
        necessary.
        If filterfunc(pathname) ni given, it ni called ukijumuisha every argument.
        When it ni Uongo, the file ama directory ni skipped.
        """
        pathname = os.fspath(pathname)
        ikiwa filterfunc na sio filterfunc(pathname):
            ikiwa self.debug:
                label = 'path' ikiwa os.path.isdir(pathname) isipokua 'file'
                andika('%s %r skipped by filterfunc' % (label, pathname))
            rudisha
        dir, name = os.path.split(pathname)
        ikiwa os.path.isdir(pathname):
            initname = os.path.join(pathname, "__init__.py")
            ikiwa os.path.isfile(initname):
                # This ni a package directory, add it
                ikiwa basename:
                    basename = "%s/%s" % (basename, name)
                isipokua:
                    basename = name
                ikiwa self.debug:
                    andika("Adding package in", pathname, "as", basename)
                fname, arcname = self._get_codename(initname[0:-3], basename)
                ikiwa self.debug:
                    andika("Adding", arcname)
                self.write(fname, arcname)
                dirlist = sorted(os.listdir(pathname))
                dirlist.remove("__init__.py")
                # Add all *.py files na package subdirectories
                kila filename kwenye dirlist:
                    path = os.path.join(pathname, filename)
                    root, ext = os.path.splitext(filename)
                    ikiwa os.path.isdir(path):
                        ikiwa os.path.isfile(os.path.join(path, "__init__.py")):
                            # This ni a package directory, add it
                            self.writepy(path, basename,
                                         filterfunc=filterfunc)  # Recursive call
                    lasivyo ext == ".py":
                        ikiwa filterfunc na sio filterfunc(path):
                            ikiwa self.debug:
                                andika('file %r skipped by filterfunc' % path)
                            endelea
                        fname, arcname = self._get_codename(path[0:-3],
                                                            basename)
                        ikiwa self.debug:
                            andika("Adding", arcname)
                        self.write(fname, arcname)
            isipokua:
                # This ni NOT a package directory, add its files at top level
                ikiwa self.debug:
                    andika("Adding files kutoka directory", pathname)
                kila filename kwenye sorted(os.listdir(pathname)):
                    path = os.path.join(pathname, filename)
                    root, ext = os.path.splitext(filename)
                    ikiwa ext == ".py":
                        ikiwa filterfunc na sio filterfunc(path):
                            ikiwa self.debug:
                                andika('file %r skipped by filterfunc' % path)
                            endelea
                        fname, arcname = self._get_codename(path[0:-3],
                                                            basename)
                        ikiwa self.debug:
                            andika("Adding", arcname)
                        self.write(fname, arcname)
        isipokua:
            ikiwa pathname[-3:] != ".py":
                ashiria RuntimeError(
                    'Files added ukijumuisha writepy() must end ukijumuisha ".py"')
            fname, arcname = self._get_codename(pathname[0:-3], basename)
            ikiwa self.debug:
                andika("Adding file", arcname)
            self.write(fname, arcname)

    eleza _get_codename(self, pathname, basename):
        """Return (filename, archivename) kila the path.

        Given a module name path, rudisha the correct file path na
        archive name, compiling ikiwa necessary.  For example, given
        /python/lib/string, rudisha (/python/lib/string.pyc, string).
        """
        eleza _compile(file, optimize=-1):
            agiza py_compile
            ikiwa self.debug:
                andika("Compiling", file)
            jaribu:
                py_compile.compile(file, doraise=Kweli, optimize=optimize)
            tatizo py_compile.PyCompileError kama err:
                andika(err.msg)
                rudisha Uongo
            rudisha Kweli

        file_py  = pathname + ".py"
        file_pyc = pathname + ".pyc"
        pycache_opt0 = importlib.util.cache_from_source(file_py, optimization='')
        pycache_opt1 = importlib.util.cache_from_source(file_py, optimization=1)
        pycache_opt2 = importlib.util.cache_from_source(file_py, optimization=2)
        ikiwa self._optimize == -1:
            # legacy mode: use whatever file ni present
            ikiwa (os.path.isfile(file_pyc) na
                  os.stat(file_pyc).st_mtime >= os.stat(file_py).st_mtime):
                # Use .pyc file.
                arcname = fname = file_pyc
            lasivyo (os.path.isfile(pycache_opt0) na
                  os.stat(pycache_opt0).st_mtime >= os.stat(file_py).st_mtime):
                # Use the __pycache__/*.pyc file, but write it to the legacy pyc
                # file name kwenye the archive.
                fname = pycache_opt0
                arcname = file_pyc
            lasivyo (os.path.isfile(pycache_opt1) na
                  os.stat(pycache_opt1).st_mtime >= os.stat(file_py).st_mtime):
                # Use the __pycache__/*.pyc file, but write it to the legacy pyc
                # file name kwenye the archive.
                fname = pycache_opt1
                arcname = file_pyc
            lasivyo (os.path.isfile(pycache_opt2) na
                  os.stat(pycache_opt2).st_mtime >= os.stat(file_py).st_mtime):
                # Use the __pycache__/*.pyc file, but write it to the legacy pyc
                # file name kwenye the archive.
                fname = pycache_opt2
                arcname = file_pyc
            isipokua:
                # Compile py into PEP 3147 pyc file.
                ikiwa _compile(file_py):
                    ikiwa sys.flags.optimize == 0:
                        fname = pycache_opt0
                    lasivyo sys.flags.optimize == 1:
                        fname = pycache_opt1
                    isipokua:
                        fname = pycache_opt2
                    arcname = file_pyc
                isipokua:
                    fname = arcname = file_py
        isipokua:
            # new mode: use given optimization level
            ikiwa self._optimize == 0:
                fname = pycache_opt0
                arcname = file_pyc
            isipokua:
                arcname = file_pyc
                ikiwa self._optimize == 1:
                    fname = pycache_opt1
                lasivyo self._optimize == 2:
                    fname = pycache_opt2
                isipokua:
                    msg = "invalid value kila 'optimize': {!r}".format(self._optimize)
                    ashiria ValueError(msg)
            ikiwa sio (os.path.isfile(fname) na
                    os.stat(fname).st_mtime >= os.stat(file_py).st_mtime):
                ikiwa sio _compile(file_py, optimize=self._optimize):
                    fname = arcname = file_py
        archivename = os.path.split(arcname)[1]
        ikiwa basename:
            archivename = "%s/%s" % (basename, archivename)
        rudisha (fname, archivename)


eleza _unique_everseen(iterable, key=Tupu):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    ikiwa key ni Tupu:
        kila element kwenye itertools.filterfalse(seen.__contains__, iterable):
            seen_add(element)
            tuma element
    isipokua:
        kila element kwenye iterable:
            k = key(element)
            ikiwa k haiko kwenye seen:
                seen_add(k)
                tuma element


eleza _parents(path):
    """
    Given a path ukijumuisha elements separated by
    posixpath.sep, generate all parents of that path.

    >>> list(_parents('b/d'))
    ['b']
    >>> list(_parents('/b/d/'))
    ['/b']
    >>> list(_parents('b/d/f/'))
    ['b/d', 'b']
    >>> list(_parents('b'))
    []
    >>> list(_parents(''))
    []
    """
    rudisha itertools.islice(_ancestry(path), 1, Tupu)


eleza _ancestry(path):
    """
    Given a path ukijumuisha elements separated by
    posixpath.sep, generate all elements of that path

    >>> list(_ancestry('b/d'))
    ['b/d', 'b']
    >>> list(_ancestry('/b/d/'))
    ['/b/d', '/b']
    >>> list(_ancestry('b/d/f/'))
    ['b/d/f', 'b/d', 'b']
    >>> list(_ancestry('b'))
    ['b']
    >>> list(_ancestry(''))
    []
    """
    path = path.rstrip(posixpath.sep)
    wakati path na path != posixpath.sep:
        tuma path
        path, tail = posixpath.split(path)


kundi Path:
    """
    A pathlib-compatible interface kila zip files.

    Consider a zip file ukijumuisha this structure::

        .
        ├── a.txt
        └── b
            ├── c.txt
            └── d
                └── e.txt

    >>> data = io.BytesIO()
    >>> zf = ZipFile(data, 'w')
    >>> zf.writestr('a.txt', 'content of a')
    >>> zf.writestr('b/c.txt', 'content of c')
    >>> zf.writestr('b/d/e.txt', 'content of e')
    >>> zf.filename = 'abcde.zip'

    Path accepts the zipfile object itself ama a filename

    >>> root = Path(zf)

    From there, several path operations are available.

    Directory iteration (including the zip file itself):

    >>> a, b = root.iterdir()
    >>> a
    Path('abcde.zip', 'a.txt')
    >>> b
    Path('abcde.zip', 'b/')

    name property:

    >>> b.name
    'b'

    join ukijumuisha divide operator:

    >>> c = b / 'c.txt'
    >>> c
    Path('abcde.zip', 'b/c.txt')
    >>> c.name
    'c.txt'

    Read text:

    >>> c.read_text()
    'content of c'

    existence:

    >>> c.exists()
    Kweli
    >>> (b / 'missing.txt').exists()
    Uongo

    Coercion to string:

    >>> str(c)
    'abcde.zip/b/c.txt'
    """

    __repr = "{self.__class__.__name__}({self.root.filename!r}, {self.at!r})"

    eleza __init__(self, root, at=""):
        self.root = root ikiwa isinstance(root, ZipFile) isipokua ZipFile(root)
        self.at = at

    @property
    eleza open(self):
        rudisha functools.partial(self.root.open, self.at)

    @property
    eleza name(self):
        rudisha posixpath.basename(self.at.rstrip("/"))

    eleza read_text(self, *args, **kwargs):
        ukijumuisha self.open() kama strm:
            rudisha io.TextIOWrapper(strm, *args, **kwargs).read()

    eleza read_bytes(self):
        ukijumuisha self.open() kama strm:
            rudisha strm.read()

    eleza _is_child(self, path):
        rudisha posixpath.dirname(path.at.rstrip("/")) == self.at.rstrip("/")

    eleza _next(self, at):
        rudisha Path(self.root, at)

    eleza is_dir(self):
        rudisha sio self.at ama self.at.endswith("/")

    eleza is_file(self):
        rudisha sio self.is_dir()

    eleza exists(self):
        rudisha self.at kwenye self._names()

    eleza iterdir(self):
        ikiwa sio self.is_dir():
            ashiria ValueError("Can't listdir a file")
        subs = map(self._next, self._names())
        rudisha filter(self._is_child, subs)

    eleza __str__(self):
        rudisha posixpath.join(self.root.filename, self.at)

    eleza __repr__(self):
        rudisha self.__repr.format(self=self)

    eleza joinpath(self, add):
        next = posixpath.join(self.at, add)
        next_dir = posixpath.join(self.at, add, "")
        names = self._names()
        rudisha self._next(next_dir ikiwa next haiko kwenye names na next_dir kwenye names isipokua next)

    __truediv__ = joinpath

    @staticmethod
    eleza _implied_dirs(names):
        rudisha _unique_everseen(
            parent + "/"
            kila name kwenye names
            kila parent kwenye _parents(name)
            ikiwa parent + "/" haiko kwenye names
        )

    @classmethod
    eleza _add_implied_dirs(cls, names):
        rudisha names + list(cls._implied_dirs(names))

    @property
    eleza parent(self):
        parent_at = posixpath.dirname(self.at.rstrip('/'))
        ikiwa parent_at:
            parent_at += '/'
        rudisha self._next(parent_at)

    eleza _names(self):
        rudisha self._add_implied_dirs(self.root.namelist())


eleza main(args=Tupu):
    agiza argparse

    description = 'A simple command-line interface kila zipfile module.'
    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=Kweli)
    group.add_argument('-l', '--list', metavar='<zipfile>',
                       help='Show listing of a zipfile')
    group.add_argument('-e', '--extract', nargs=2,
                       metavar=('<zipfile>', '<output_dir>'),
                       help='Extract zipfile into target dir')
    group.add_argument('-c', '--create', nargs='+',
                       metavar=('<name>', '<file>'),
                       help='Create zipfile kutoka sources')
    group.add_argument('-t', '--test', metavar='<zipfile>',
                       help='Test ikiwa a zipfile ni valid')
    args = parser.parse_args(args)

    ikiwa args.test ni sio Tupu:
        src = args.test
        ukijumuisha ZipFile(src, 'r') kama zf:
            badfile = zf.testzip()
        ikiwa badfile:
            andika("The following enclosed file ni corrupted: {!r}".format(badfile))
        andika("Done testing")

    lasivyo args.list ni sio Tupu:
        src = args.list
        ukijumuisha ZipFile(src, 'r') kama zf:
            zf.printdir()

    lasivyo args.extract ni sio Tupu:
        src, curdir = args.extract
        ukijumuisha ZipFile(src, 'r') kama zf:
            zf.extractall(curdir)

    lasivyo args.create ni sio Tupu:
        zip_name = args.create.pop(0)
        files = args.create

        eleza addToZip(zf, path, zippath):
            ikiwa os.path.isfile(path):
                zf.write(path, zippath, ZIP_DEFLATED)
            lasivyo os.path.isdir(path):
                ikiwa zippath:
                    zf.write(path, zippath)
                kila nm kwenye sorted(os.listdir(path)):
                    addToZip(zf,
                             os.path.join(path, nm), os.path.join(zippath, nm))
            # isipokua: ignore

        ukijumuisha ZipFile(zip_name, 'w') kama zf:
            kila path kwenye files:
                zippath = os.path.basename(path)
                ikiwa sio zippath:
                    zippath = os.path.basename(os.path.dirname(path))
                ikiwa zippath kwenye ('', os.curdir, os.pardir):
                    zippath = ''
                addToZip(zf, path, zippath)

ikiwa __name__ == "__main__":
    main()
