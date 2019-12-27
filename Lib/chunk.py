"""Simple kundi to read IFF chunks.

An IFF chunk (used in formats such as AIFF, TIFF, RMFF (RealMedia File
Format)) has the following structure:

+----------------+
| ID (4 bytes)   |
+----------------+
| size (4 bytes) |
+----------------+
| data           |
| ...            |
+----------------+

The ID is a 4-byte string which identifies the type of chunk.

The size field (a 32-bit value, encoded using big-endian byte order)
gives the size of the whole chunk, including the 8-byte header.

Usually an IFF-type file consists of one or more chunks.  The proposed
usage of the Chunk kundi defined here is to instantiate an instance at
the start of each chunk and read kutoka the instance until it reaches
the end, after which a new instance can be instantiated.  At the end
of the file, creating a new instance will fail with an EOFError
exception.

Usage:
while True:
    try:
        chunk = Chunk(file)
    except EOFError:
        break
    chunktype = chunk.getname()
    while True:
        data = chunk.read(nbytes)
        ikiwa not data:
            pass
        # do something with data

The interface is file-like.  The implemented methods are:
read, close, seek, tell, isatty.
Extra methods are: skip() (called by close, skips to the end of the chunk),
getname() (returns the name (ID) of the chunk)

The __init__ method has one required argument, a file-like object
(including a chunk instance), and one optional argument, a flag which
specifies whether or not chunks are aligned on 2-byte boundaries.  The
default is 1, i.e. aligned.
"""

kundi Chunk:
    eleza __init__(self, file, align=True, bigendian=True, inclheader=False):
        agiza struct
        self.closed = False
        self.align = align      # whether to align to word (2-byte) boundaries
        ikiwa bigendian:
            strflag = '>'
        else:
            strflag = '<'
        self.file = file
        self.chunkname = file.read(4)
        ikiwa len(self.chunkname) < 4:
            raise EOFError
        try:
            self.chunksize = struct.unpack_kutoka(strflag+'L', file.read(4))[0]
        except struct.error:
            raise EOFError kutoka None
        ikiwa inclheader:
            self.chunksize = self.chunksize - 8 # subtract header
        self.size_read = 0
        try:
            self.offset = self.file.tell()
        except (AttributeError, OSError):
            self.seekable = False
        else:
            self.seekable = True

    eleza getname(self):
        """Return the name (ID) of the current chunk."""
        rudisha self.chunkname

    eleza getsize(self):
        """Return the size of the current chunk."""
        rudisha self.chunksize

    eleza close(self):
        ikiwa not self.closed:
            try:
                self.skip()
            finally:
                self.closed = True

    eleza isatty(self):
        ikiwa self.closed:
            raise ValueError("I/O operation on closed file")
        rudisha False

    eleza seek(self, pos, whence=0):
        """Seek to specified position into the chunk.
        Default position is 0 (start of chunk).
        If the file is not seekable, this will result in an error.
        """

        ikiwa self.closed:
            raise ValueError("I/O operation on closed file")
        ikiwa not self.seekable:
            raise OSError("cannot seek")
        ikiwa whence == 1:
            pos = pos + self.size_read
        elikiwa whence == 2:
            pos = pos + self.chunksize
        ikiwa pos < 0 or pos > self.chunksize:
            raise RuntimeError
        self.file.seek(self.offset + pos, 0)
        self.size_read = pos

    eleza tell(self):
        ikiwa self.closed:
            raise ValueError("I/O operation on closed file")
        rudisha self.size_read

    eleza read(self, size=-1):
        """Read at most size bytes kutoka the chunk.
        If size is omitted or negative, read until the end
        of the chunk.
        """

        ikiwa self.closed:
            raise ValueError("I/O operation on closed file")
        ikiwa self.size_read >= self.chunksize:
            rudisha b''
        ikiwa size < 0:
            size = self.chunksize - self.size_read
        ikiwa size > self.chunksize - self.size_read:
            size = self.chunksize - self.size_read
        data = self.file.read(size)
        self.size_read = self.size_read + len(data)
        ikiwa self.size_read == self.chunksize and \
           self.align and \
           (self.chunksize & 1):
            dummy = self.file.read(1)
            self.size_read = self.size_read + len(dummy)
        rudisha data

    eleza skip(self):
        """Skip the rest of the chunk.
        If you are not interested in the contents of the chunk,
        this method should be called so that the file points to
        the start of the next chunk.
        """

        ikiwa self.closed:
            raise ValueError("I/O operation on closed file")
        ikiwa self.seekable:
            try:
                n = self.chunksize - self.size_read
                # maybe fix alignment
                ikiwa self.align and (self.chunksize & 1):
                    n = n + 1
                self.file.seek(n, 1)
                self.size_read = self.size_read + n
                return
            except OSError:
                pass
        while self.size_read < self.chunksize:
            n = min(8192, self.chunksize - self.size_read)
            dummy = self.read(n)
            ikiwa not dummy:
                raise EOFError
