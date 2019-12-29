"""Simple kundi to read IFF chunks.

An IFF chunk (used kwenye formats such kama AIFF, TIFF, RMFF (RealMedia File
Format)) has the following structure:

+----------------+
| ID (4 bytes)   |
+----------------+
| size (4 bytes) |
+----------------+
| data           |
| ...            |
+----------------+

The ID ni a 4-byte string which identifies the type of chunk.

The size field (a 32-bit value, encoded using big-endian byte order)
gives the size of the whole chunk, including the 8-byte header.

Usually an IFF-type file consists of one ama more chunks.  The proposed
usage of the Chunk kundi defined here ni to instantiate an instance at
the start of each chunk na read kutoka the instance until it reaches
the end, after which a new instance can be instantiated.  At the end
of the file, creating a new instance will fail ukijumuisha an EOFError
exception.

Usage:
wakati Kweli:
    jaribu:
        chunk = Chunk(file)
    tatizo EOFError:
        koma
    chunktype = chunk.getname()
    wakati Kweli:
        data = chunk.read(nbytes)
        ikiwa sio data:
            pita
        # do something ukijumuisha data

The interface ni file-like.  The implemented methods are:
read, close, seek, tell, isatty.
Extra methods are: skip() (called by close, skips to the end of the chunk),
getname() (rudishas the name (ID) of the chunk)

The __init__ method has one required argument, a file-like object
(including a chunk instance), na one optional argument, a flag which
specifies whether ama sio chunks are aligned on 2-byte boundaries.  The
default ni 1, i.e. aligned.
"""

kundi Chunk:
    eleza __init__(self, file, align=Kweli, bigendian=Kweli, inclheader=Uongo):
        agiza struct
        self.closed = Uongo
        self.align = align      # whether to align to word (2-byte) boundaries
        ikiwa bigendian:
            strflag = '>'
        isipokua:
            strflag = '<'
        self.file = file
        self.chunkname = file.read(4)
        ikiwa len(self.chunkname) < 4:
            ashiria EOFError
        jaribu:
            self.chunksize = struct.unpack_kutoka(strflag+'L', file.read(4))[0]
        tatizo struct.error:
            ashiria EOFError kutoka Tupu
        ikiwa inclheader:
            self.chunksize = self.chunksize - 8 # subtract header
        self.size_read = 0
        jaribu:
            self.offset = self.file.tell()
        tatizo (AttributeError, OSError):
            self.seekable = Uongo
        isipokua:
            self.seekable = Kweli

    eleza getname(self):
        """Return the name (ID) of the current chunk."""
        rudisha self.chunkname

    eleza getsize(self):
        """Return the size of the current chunk."""
        rudisha self.chunksize

    eleza close(self):
        ikiwa sio self.closed:
            jaribu:
                self.skip()
            mwishowe:
                self.closed = Kweli

    eleza isatty(self):
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file")
        rudisha Uongo

    eleza seek(self, pos, whence=0):
        """Seek to specified position into the chunk.
        Default position ni 0 (start of chunk).
        If the file ni sio seekable, this will result kwenye an error.
        """

        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file")
        ikiwa sio self.seekable:
            ashiria OSError("cannot seek")
        ikiwa whence == 1:
            pos = pos + self.size_read
        lasivyo whence == 2:
            pos = pos + self.chunksize
        ikiwa pos < 0 ama pos > self.chunksize:
            ashiria RuntimeError
        self.file.seek(self.offset + pos, 0)
        self.size_read = pos

    eleza tell(self):
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file")
        rudisha self.size_read

    eleza read(self, size=-1):
        """Read at most size bytes kutoka the chunk.
        If size ni omitted ama negative, read until the end
        of the chunk.
        """

        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file")
        ikiwa self.size_read >= self.chunksize:
            rudisha b''
        ikiwa size < 0:
            size = self.chunksize - self.size_read
        ikiwa size > self.chunksize - self.size_read:
            size = self.chunksize - self.size_read
        data = self.file.read(size)
        self.size_read = self.size_read + len(data)
        ikiwa self.size_read == self.chunksize na \
           self.align na \
           (self.chunksize & 1):
            dummy = self.file.read(1)
            self.size_read = self.size_read + len(dummy)
        rudisha data

    eleza skip(self):
        """Skip the rest of the chunk.
        If you are sio interested kwenye the contents of the chunk,
        this method should be called so that the file points to
        the start of the next chunk.
        """

        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file")
        ikiwa self.seekable:
            jaribu:
                n = self.chunksize - self.size_read
                # maybe fix alignment
                ikiwa self.align na (self.chunksize & 1):
                    n = n + 1
                self.file.seek(n, 1)
                self.size_read = self.size_read + n
                rudisha
            tatizo OSError:
                pita
        wakati self.size_read < self.chunksize:
            n = min(8192, self.chunksize - self.size_read)
            dummy = self.read(n)
            ikiwa sio dummy:
                ashiria EOFError
