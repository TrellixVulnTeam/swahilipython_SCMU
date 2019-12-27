"""Stuff to parse AIFF-C and AIFF files.

Unless explicitly stated otherwise, the description below is true
both for AIFF-C files and AIFF files.

An AIFF-C file has the following structure.

  +-----------------+
  | FORM            |
  +-----------------+
  | <size>          |
  +----+------------+
  |    | AIFC       |
  |    +------------+
  |    | <chunks>   |
  |    |    .       |
  |    |    .       |
  |    |    .       |
  +----+------------+

An AIFF file has the string "AIFF" instead of "AIFC".

A chunk consists of an identifier (4 bytes) followed by a size (4 bytes,
big endian order), followed by the data.  The size field does not include
the size of the 8 byte header.

The following chunk types are recognized.

  FVER
      <version number of AIFF-C defining document> (AIFF-C only).
  MARK
      <# of markers> (2 bytes)
      list of markers:
          <marker ID> (2 bytes, must be > 0)
          <position> (4 bytes)
          <marker name> ("pstring")
  COMM
      <# of channels> (2 bytes)
      <# of sound frames> (4 bytes)
      <size of the samples> (2 bytes)
      <sampling frequency> (10 bytes, IEEE 80-bit extended
          floating point)
      in AIFF-C files only:
      <compression type> (4 bytes)
      <human-readable version of compression type> ("pstring")
  SSND
      <offset> (4 bytes, not used by this program)
      <blocksize> (4 bytes, not used by this program)
      <sound data>

A pstring consists of 1 byte length, a string of characters, and 0 or 1
byte pad to make the total length even.

Usage.

Reading AIFF files:
  f = aifc.open(file, 'r')
where file is either the name of a file or an open file pointer.
The open file pointer must have methods read(), seek(), and close().
In some types of audio files, ikiwa the setpos() method is not used,
the seek() method is not necessary.

This returns an instance of a kundi with the following public methods:
  getnchannels()  -- returns number of audio channels (1 for
             mono, 2 for stereo)
  getsampwidth()  -- returns sample width in bytes
  getframerate()  -- returns sampling frequency
  getnframes()    -- returns number of audio frames
  getcomptype()   -- returns compression type ('NONE' for AIFF files)
  getcompname()   -- returns human-readable version of
             compression type ('not compressed' for AIFF files)
  getparams() -- returns a namedtuple consisting of all of the
             above in the above order
  getmarkers()    -- get the list of marks in the audio file or None
             ikiwa there are no marks
  getmark(id) -- get mark with the specified id (raises an error
             ikiwa the mark does not exist)
  readframes(n)   -- returns at most n frames of audio
  rewind()    -- rewind to the beginning of the audio stream
  setpos(pos) -- seek to the specified position
  tell()      -- rudisha the current position
  close()     -- close the instance (make it unusable)
The position returned by tell(), the position given to setpos() and
the position of marks are all compatible and have nothing to do with
the actual position in the file.
The close() method is called automatically when the kundi instance
is destroyed.

Writing AIFF files:
  f = aifc.open(file, 'w')
where file is either the name of a file or an open file pointer.
The open file pointer must have methods write(), tell(), seek(), and
close().

This returns an instance of a kundi with the following public methods:
  aiff()      -- create an AIFF file (AIFF-C default)
  aifc()      -- create an AIFF-C file
  setnchannels(n) -- set the number of channels
  setsampwidth(n) -- set the sample width
  setframerate(n) -- set the frame rate
  setnframes(n)   -- set the number of frames
  setcomptype(type, name)
          -- set the compression type and the
             human-readable compression type
  setparams(tuple)
          -- set all parameters at once
  setmark(id, pos, name)
          -- add specified mark to the list of marks
  tell()      -- rudisha current position in output file (useful
             in combination with setmark())
  writeframesraw(data)
          -- write audio frames without pathing up the
             file header
  writeframes(data)
          -- write audio frames and patch up the file header
  close()     -- patch up the file header and close the
             output file
You should set the parameters before the first writeframesraw or
writeframes.  The total number of frames does not need to be set,
but when it is set to the correct value, the header does not have to
be patched up.
It is best to first set all parameters, perhaps possibly the
compression type, and then write audio frames using writeframesraw.
When all frames have been written, either call writeframes(b'') or
close() to patch up the sizes in the header.
Marks can be added anytime.  If there are any marks, you must call
close() after all frames have been written.
The close() method is called automatically when the kundi instance
is destroyed.

When a file is opened with the extension '.aiff', an AIFF file is
written, otherwise an AIFF-C file is written.  This default can be
changed by calling aiff() or aifc() before the first writeframes or
writeframesraw.
"""

agiza struct
agiza builtins
agiza warnings

__all__ = ["Error", "open", "openfp"]

kundi Error(Exception):
    pass

_AIFC_version = 0xA2805140     # Version 1 of AIFF-C

eleza _read_long(file):
    try:
        rudisha struct.unpack('>l', file.read(4))[0]
    except struct.error:
        raise EOFError kutoka None

eleza _read_ulong(file):
    try:
        rudisha struct.unpack('>L', file.read(4))[0]
    except struct.error:
        raise EOFError kutoka None

eleza _read_short(file):
    try:
        rudisha struct.unpack('>h', file.read(2))[0]
    except struct.error:
        raise EOFError kutoka None

eleza _read_ushort(file):
    try:
        rudisha struct.unpack('>H', file.read(2))[0]
    except struct.error:
        raise EOFError kutoka None

eleza _read_string(file):
    length = ord(file.read(1))
    ikiwa length == 0:
        data = b''
    else:
        data = file.read(length)
    ikiwa length & 1 == 0:
        dummy = file.read(1)
    rudisha data

_HUGE_VAL = 1.79769313486231e+308 # See <limits.h>

eleza _read_float(f): # 10 bytes
    expon = _read_short(f) # 2 bytes
    sign = 1
    ikiwa expon < 0:
        sign = -1
        expon = expon + 0x8000
    himant = _read_ulong(f) # 4 bytes
    lomant = _read_ulong(f) # 4 bytes
    ikiwa expon == himant == lomant == 0:
        f = 0.0
    elikiwa expon == 0x7FFF:
        f = _HUGE_VAL
    else:
        expon = expon - 16383
        f = (himant * 0x100000000 + lomant) * pow(2.0, expon - 63)
    rudisha sign * f

eleza _write_short(f, x):
    f.write(struct.pack('>h', x))

eleza _write_ushort(f, x):
    f.write(struct.pack('>H', x))

eleza _write_long(f, x):
    f.write(struct.pack('>l', x))

eleza _write_ulong(f, x):
    f.write(struct.pack('>L', x))

eleza _write_string(f, s):
    ikiwa len(s) > 255:
        raise ValueError("string exceeds maximum pstring length")
    f.write(struct.pack('B', len(s)))
    f.write(s)
    ikiwa len(s) & 1 == 0:
        f.write(b'\x00')

eleza _write_float(f, x):
    agiza math
    ikiwa x < 0:
        sign = 0x8000
        x = x * -1
    else:
        sign = 0
    ikiwa x == 0:
        expon = 0
        himant = 0
        lomant = 0
    else:
        fmant, expon = math.frexp(x)
        ikiwa expon > 16384 or fmant >= 1 or fmant != fmant: # Infinity or NaN
            expon = sign|0x7FFF
            himant = 0
            lomant = 0
        else:                   # Finite
            expon = expon + 16382
            ikiwa expon < 0:           # denormalized
                fmant = math.ldexp(fmant, expon)
                expon = 0
            expon = expon | sign
            fmant = math.ldexp(fmant, 32)
            fsmant = math.floor(fmant)
            himant = int(fsmant)
            fmant = math.ldexp(fmant - fsmant, 32)
            fsmant = math.floor(fmant)
            lomant = int(fsmant)
    _write_ushort(f, expon)
    _write_ulong(f, himant)
    _write_ulong(f, lomant)

kutoka chunk agiza Chunk
kutoka collections agiza namedtuple

_aifc_params = namedtuple('_aifc_params',
                          'nchannels sampwidth framerate nframes comptype compname')

_aifc_params.nchannels.__doc__ = 'Number of audio channels (1 for mono, 2 for stereo)'
_aifc_params.sampwidth.__doc__ = 'Sample width in bytes'
_aifc_params.framerate.__doc__ = 'Sampling frequency'
_aifc_params.nframes.__doc__ = 'Number of audio frames'
_aifc_params.comptype.__doc__ = 'Compression type ("NONE" for AIFF files)'
_aifc_params.compname.__doc__ = ("""\
A human-readable version of the compression type
('not compressed' for AIFF files)""")


kundi Aifc_read:
    # Variables used in this class:
    #
    # These variables are available to the user though appropriate
    # methods of this class:
    # _file -- the open file with methods read(), close(), and seek()
    #       set through the __init__() method
    # _nchannels -- the number of audio channels
    #       available through the getnchannels() method
    # _nframes -- the number of audio frames
    #       available through the getnframes() method
    # _sampwidth -- the number of bytes per audio sample
    #       available through the getsampwidth() method
    # _framerate -- the sampling frequency
    #       available through the getframerate() method
    # _comptype -- the AIFF-C compression type ('NONE' ikiwa AIFF)
    #       available through the getcomptype() method
    # _compname -- the human-readable AIFF-C compression type
    #       available through the getcomptype() method
    # _markers -- the marks in the audio file
    #       available through the getmarkers() and getmark()
    #       methods
    # _soundpos -- the position in the audio stream
    #       available through the tell() method, set through the
    #       setpos() method
    #
    # These variables are used internally only:
    # _version -- the AIFF-C version number
    # _decomp -- the decompressor kutoka builtin module cl
    # _comm_chunk_read -- 1 iff the COMM chunk has been read
    # _aifc -- 1 iff reading an AIFF-C file
    # _ssnd_seek_needed -- 1 iff positioned correctly in audio
    #       file for readframes()
    # _ssnd_chunk -- instantiation of a chunk kundi for the SSND chunk
    # _framesize -- size of one frame in the file

    _file = None  # Set here since __del__ checks it

    eleza initfp(self, file):
        self._version = 0
        self._convert = None
        self._markers = []
        self._soundpos = 0
        self._file = file
        chunk = Chunk(file)
        ikiwa chunk.getname() != b'FORM':
            raise Error('file does not start with FORM id')
        formdata = chunk.read(4)
        ikiwa formdata == b'AIFF':
            self._aifc = 0
        elikiwa formdata == b'AIFC':
            self._aifc = 1
        else:
            raise Error('not an AIFF or AIFF-C file')
        self._comm_chunk_read = 0
        self._ssnd_chunk = None
        while 1:
            self._ssnd_seek_needed = 1
            try:
                chunk = Chunk(self._file)
            except EOFError:
                break
            chunkname = chunk.getname()
            ikiwa chunkname == b'COMM':
                self._read_comm_chunk(chunk)
                self._comm_chunk_read = 1
            elikiwa chunkname == b'SSND':
                self._ssnd_chunk = chunk
                dummy = chunk.read(8)
                self._ssnd_seek_needed = 0
            elikiwa chunkname == b'FVER':
                self._version = _read_ulong(chunk)
            elikiwa chunkname == b'MARK':
                self._readmark(chunk)
            chunk.skip()
        ikiwa not self._comm_chunk_read or not self._ssnd_chunk:
            raise Error('COMM chunk and/or SSND chunk missing')

    eleza __init__(self, f):
        ikiwa isinstance(f, str):
            file_object = builtins.open(f, 'rb')
            try:
                self.initfp(file_object)
            except:
                file_object.close()
                raise
        else:
            # assume it is an open file object already
            self.initfp(f)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.close()

    #
    # User visible methods.
    #
    eleza getfp(self):
        rudisha self._file

    eleza rewind(self):
        self._ssnd_seek_needed = 1
        self._soundpos = 0

    eleza close(self):
        file = self._file
        ikiwa file is not None:
            self._file = None
            file.close()

    eleza tell(self):
        rudisha self._soundpos

    eleza getnchannels(self):
        rudisha self._nchannels

    eleza getnframes(self):
        rudisha self._nframes

    eleza getsampwidth(self):
        rudisha self._sampwidth

    eleza getframerate(self):
        rudisha self._framerate

    eleza getcomptype(self):
        rudisha self._comptype

    eleza getcompname(self):
        rudisha self._compname

##  eleza getversion(self):
##      rudisha self._version

    eleza getparams(self):
        rudisha _aifc_params(self.getnchannels(), self.getsampwidth(),
                            self.getframerate(), self.getnframes(),
                            self.getcomptype(), self.getcompname())

    eleza getmarkers(self):
        ikiwa len(self._markers) == 0:
            rudisha None
        rudisha self._markers

    eleza getmark(self, id):
        for marker in self._markers:
            ikiwa id == marker[0]:
                rudisha marker
        raise Error('marker {0!r} does not exist'.format(id))

    eleza setpos(self, pos):
        ikiwa pos < 0 or pos > self._nframes:
            raise Error('position not in range')
        self._soundpos = pos
        self._ssnd_seek_needed = 1

    eleza readframes(self, nframes):
        ikiwa self._ssnd_seek_needed:
            self._ssnd_chunk.seek(0)
            dummy = self._ssnd_chunk.read(8)
            pos = self._soundpos * self._framesize
            ikiwa pos:
                self._ssnd_chunk.seek(pos + 8)
            self._ssnd_seek_needed = 0
        ikiwa nframes == 0:
            rudisha b''
        data = self._ssnd_chunk.read(nframes * self._framesize)
        ikiwa self._convert and data:
            data = self._convert(data)
        self._soundpos = self._soundpos + len(data) // (self._nchannels
                                                        * self._sampwidth)
        rudisha data

    #
    # Internal methods.
    #

    eleza _alaw2lin(self, data):
        agiza audioop
        rudisha audioop.alaw2lin(data, 2)

    eleza _ulaw2lin(self, data):
        agiza audioop
        rudisha audioop.ulaw2lin(data, 2)

    eleza _adpcm2lin(self, data):
        agiza audioop
        ikiwa not hasattr(self, '_adpcmstate'):
            # first time
            self._adpcmstate = None
        data, self._adpcmstate = audioop.adpcm2lin(data, 2, self._adpcmstate)
        rudisha data

    eleza _read_comm_chunk(self, chunk):
        self._nchannels = _read_short(chunk)
        self._nframes = _read_long(chunk)
        self._sampwidth = (_read_short(chunk) + 7) // 8
        self._framerate = int(_read_float(chunk))
        ikiwa self._sampwidth <= 0:
            raise Error('bad sample width')
        ikiwa self._nchannels <= 0:
            raise Error('bad # of channels')
        self._framesize = self._nchannels * self._sampwidth
        ikiwa self._aifc:
            #DEBUG: SGI's soundeditor produces a bad size :-(
            kludge = 0
            ikiwa chunk.chunksize == 18:
                kludge = 1
                warnings.warn('Warning: bad COMM chunk size')
                chunk.chunksize = 23
            #DEBUG end
            self._comptype = chunk.read(4)
            #DEBUG start
            ikiwa kludge:
                length = ord(chunk.file.read(1))
                ikiwa length & 1 == 0:
                    length = length + 1
                chunk.chunksize = chunk.chunksize + length
                chunk.file.seek(-1, 1)
            #DEBUG end
            self._compname = _read_string(chunk)
            ikiwa self._comptype != b'NONE':
                ikiwa self._comptype == b'G722':
                    self._convert = self._adpcm2lin
                elikiwa self._comptype in (b'ulaw', b'ULAW'):
                    self._convert = self._ulaw2lin
                elikiwa self._comptype in (b'alaw', b'ALAW'):
                    self._convert = self._alaw2lin
                else:
                    raise Error('unsupported compression type')
                self._sampwidth = 2
        else:
            self._comptype = b'NONE'
            self._compname = b'not compressed'

    eleza _readmark(self, chunk):
        nmarkers = _read_short(chunk)
        # Some files appear to contain invalid counts.
        # Cope with this by testing for EOF.
        try:
            for i in range(nmarkers):
                id = _read_short(chunk)
                pos = _read_long(chunk)
                name = _read_string(chunk)
                ikiwa pos or name:
                    # some files appear to have
                    # dummy markers consisting of
                    # a position 0 and name ''
                    self._markers.append((id, pos, name))
        except EOFError:
            w = ('Warning: MARK chunk contains only %s marker%s instead of %s' %
                 (len(self._markers), '' ikiwa len(self._markers) == 1 else 's',
                  nmarkers))
            warnings.warn(w)

kundi Aifc_write:
    # Variables used in this class:
    #
    # These variables are user settable through appropriate methods
    # of this class:
    # _file -- the open file with methods write(), close(), tell(), seek()
    #       set through the __init__() method
    # _comptype -- the AIFF-C compression type ('NONE' in AIFF)
    #       set through the setcomptype() or setparams() method
    # _compname -- the human-readable AIFF-C compression type
    #       set through the setcomptype() or setparams() method
    # _nchannels -- the number of audio channels
    #       set through the setnchannels() or setparams() method
    # _sampwidth -- the number of bytes per audio sample
    #       set through the setsampwidth() or setparams() method
    # _framerate -- the sampling frequency
    #       set through the setframerate() or setparams() method
    # _nframes -- the number of audio frames written to the header
    #       set through the setnframes() or setparams() method
    # _aifc -- whether we're writing an AIFF-C file or an AIFF file
    #       set through the aifc() method, reset through the
    #       aiff() method
    #
    # These variables are used internally only:
    # _version -- the AIFF-C version number
    # _comp -- the compressor kutoka builtin module cl
    # _nframeswritten -- the number of audio frames actually written
    # _datalength -- the size of the audio samples written to the header
    # _datawritten -- the size of the audio samples actually written

    _file = None  # Set here since __del__ checks it

    eleza __init__(self, f):
        ikiwa isinstance(f, str):
            file_object = builtins.open(f, 'wb')
            try:
                self.initfp(file_object)
            except:
                file_object.close()
                raise

            # treat .aiff file extensions as non-compressed audio
            ikiwa f.endswith('.aiff'):
                self._aifc = 0
        else:
            # assume it is an open file object already
            self.initfp(f)

    eleza initfp(self, file):
        self._file = file
        self._version = _AIFC_version
        self._comptype = b'NONE'
        self._compname = b'not compressed'
        self._convert = None
        self._nchannels = 0
        self._sampwidth = 0
        self._framerate = 0
        self._nframes = 0
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._markers = []
        self._marklength = 0
        self._aifc = 1      # AIFF-C is default

    eleza __del__(self):
        self.close()

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.close()

    #
    # User visible methods.
    #
    eleza aiff(self):
        ikiwa self._nframeswritten:
            raise Error('cannot change parameters after starting to write')
        self._aifc = 0

    eleza aifc(self):
        ikiwa self._nframeswritten:
            raise Error('cannot change parameters after starting to write')
        self._aifc = 1

    eleza setnchannels(self, nchannels):
        ikiwa self._nframeswritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa nchannels < 1:
            raise Error('bad # of channels')
        self._nchannels = nchannels

    eleza getnchannels(self):
        ikiwa not self._nchannels:
            raise Error('number of channels not set')
        rudisha self._nchannels

    eleza setsampwidth(self, sampwidth):
        ikiwa self._nframeswritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa sampwidth < 1 or sampwidth > 4:
            raise Error('bad sample width')
        self._sampwidth = sampwidth

    eleza getsampwidth(self):
        ikiwa not self._sampwidth:
            raise Error('sample width not set')
        rudisha self._sampwidth

    eleza setframerate(self, framerate):
        ikiwa self._nframeswritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa framerate <= 0:
            raise Error('bad frame rate')
        self._framerate = framerate

    eleza getframerate(self):
        ikiwa not self._framerate:
            raise Error('frame rate not set')
        rudisha self._framerate

    eleza setnframes(self, nframes):
        ikiwa self._nframeswritten:
            raise Error('cannot change parameters after starting to write')
        self._nframes = nframes

    eleza getnframes(self):
        rudisha self._nframeswritten

    eleza setcomptype(self, comptype, compname):
        ikiwa self._nframeswritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa comptype not in (b'NONE', b'ulaw', b'ULAW',
                            b'alaw', b'ALAW', b'G722'):
            raise Error('unsupported compression type')
        self._comptype = comptype
        self._compname = compname

    eleza getcomptype(self):
        rudisha self._comptype

    eleza getcompname(self):
        rudisha self._compname

##  eleza setversion(self, version):
##      ikiwa self._nframeswritten:
##          raise Error, 'cannot change parameters after starting to write'
##      self._version = version

    eleza setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        ikiwa self._nframeswritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa comptype not in (b'NONE', b'ulaw', b'ULAW',
                            b'alaw', b'ALAW', b'G722'):
            raise Error('unsupported compression type')
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    eleza getparams(self):
        ikiwa not self._nchannels or not self._sampwidth or not self._framerate:
            raise Error('not all parameters set')
        rudisha _aifc_params(self._nchannels, self._sampwidth, self._framerate,
                            self._nframes, self._comptype, self._compname)

    eleza setmark(self, id, pos, name):
        ikiwa id <= 0:
            raise Error('marker ID must be > 0')
        ikiwa pos < 0:
            raise Error('marker position must be >= 0')
        ikiwa not isinstance(name, bytes):
            raise Error('marker name must be bytes')
        for i in range(len(self._markers)):
            ikiwa id == self._markers[i][0]:
                self._markers[i] = id, pos, name
                return
        self._markers.append((id, pos, name))

    eleza getmark(self, id):
        for marker in self._markers:
            ikiwa id == marker[0]:
                rudisha marker
        raise Error('marker {0!r} does not exist'.format(id))

    eleza getmarkers(self):
        ikiwa len(self._markers) == 0:
            rudisha None
        rudisha self._markers

    eleza tell(self):
        rudisha self._nframeswritten

    eleza writeframesraw(self, data):
        ikiwa not isinstance(data, (bytes, bytearray)):
            data = memoryview(data).cast('B')
        self._ensure_header_written(len(data))
        nframes = len(data) // (self._sampwidth * self._nchannels)
        ikiwa self._convert:
            data = self._convert(data)
        self._file.write(data)
        self._nframeswritten = self._nframeswritten + nframes
        self._datawritten = self._datawritten + len(data)

    eleza writeframes(self, data):
        self.writeframesraw(data)
        ikiwa self._nframeswritten != self._nframes or \
              self._datalength != self._datawritten:
            self._patchheader()

    eleza close(self):
        ikiwa self._file is None:
            return
        try:
            self._ensure_header_written(0)
            ikiwa self._datawritten & 1:
                # quick pad to even size
                self._file.write(b'\x00')
                self._datawritten = self._datawritten + 1
            self._writemarkers()
            ikiwa self._nframeswritten != self._nframes or \
                  self._datalength != self._datawritten or \
                  self._marklength:
                self._patchheader()
        finally:
            # Prevent ref cycles
            self._convert = None
            f = self._file
            self._file = None
            f.close()

    #
    # Internal methods.
    #

    eleza _lin2alaw(self, data):
        agiza audioop
        rudisha audioop.lin2alaw(data, 2)

    eleza _lin2ulaw(self, data):
        agiza audioop
        rudisha audioop.lin2ulaw(data, 2)

    eleza _lin2adpcm(self, data):
        agiza audioop
        ikiwa not hasattr(self, '_adpcmstate'):
            self._adpcmstate = None
        data, self._adpcmstate = audioop.lin2adpcm(data, 2, self._adpcmstate)
        rudisha data

    eleza _ensure_header_written(self, datasize):
        ikiwa not self._nframeswritten:
            ikiwa self._comptype in (b'ULAW', b'ulaw', b'ALAW', b'alaw', b'G722'):
                ikiwa not self._sampwidth:
                    self._sampwidth = 2
                ikiwa self._sampwidth != 2:
                    raise Error('sample width must be 2 when compressing '
                                'with ulaw/ULAW, alaw/ALAW or G7.22 (ADPCM)')
            ikiwa not self._nchannels:
                raise Error('# channels not specified')
            ikiwa not self._sampwidth:
                raise Error('sample width not specified')
            ikiwa not self._framerate:
                raise Error('sampling rate not specified')
            self._write_header(datasize)

    eleza _init_compression(self):
        ikiwa self._comptype == b'G722':
            self._convert = self._lin2adpcm
        elikiwa self._comptype in (b'ulaw', b'ULAW'):
            self._convert = self._lin2ulaw
        elikiwa self._comptype in (b'alaw', b'ALAW'):
            self._convert = self._lin2alaw

    eleza _write_header(self, initlength):
        ikiwa self._aifc and self._comptype != b'NONE':
            self._init_compression()
        self._file.write(b'FORM')
        ikiwa not self._nframes:
            self._nframes = initlength // (self._nchannels * self._sampwidth)
        self._datalength = self._nframes * self._nchannels * self._sampwidth
        ikiwa self._datalength & 1:
            self._datalength = self._datalength + 1
        ikiwa self._aifc:
            ikiwa self._comptype in (b'ulaw', b'ULAW', b'alaw', b'ALAW'):
                self._datalength = self._datalength // 2
                ikiwa self._datalength & 1:
                    self._datalength = self._datalength + 1
            elikiwa self._comptype == b'G722':
                self._datalength = (self._datalength + 3) // 4
                ikiwa self._datalength & 1:
                    self._datalength = self._datalength + 1
        try:
            self._form_length_pos = self._file.tell()
        except (AttributeError, OSError):
            self._form_length_pos = None
        commlength = self._write_form_length(self._datalength)
        ikiwa self._aifc:
            self._file.write(b'AIFC')
            self._file.write(b'FVER')
            _write_ulong(self._file, 4)
            _write_ulong(self._file, self._version)
        else:
            self._file.write(b'AIFF')
        self._file.write(b'COMM')
        _write_ulong(self._file, commlength)
        _write_short(self._file, self._nchannels)
        ikiwa self._form_length_pos is not None:
            self._nframes_pos = self._file.tell()
        _write_ulong(self._file, self._nframes)
        ikiwa self._comptype in (b'ULAW', b'ulaw', b'ALAW', b'alaw', b'G722'):
            _write_short(self._file, 8)
        else:
            _write_short(self._file, self._sampwidth * 8)
        _write_float(self._file, self._framerate)
        ikiwa self._aifc:
            self._file.write(self._comptype)
            _write_string(self._file, self._compname)
        self._file.write(b'SSND')
        ikiwa self._form_length_pos is not None:
            self._ssnd_length_pos = self._file.tell()
        _write_ulong(self._file, self._datalength + 8)
        _write_ulong(self._file, 0)
        _write_ulong(self._file, 0)

    eleza _write_form_length(self, datalength):
        ikiwa self._aifc:
            commlength = 18 + 5 + len(self._compname)
            ikiwa commlength & 1:
                commlength = commlength + 1
            verslength = 12
        else:
            commlength = 18
            verslength = 0
        _write_ulong(self._file, 4 + verslength + self._marklength + \
                     8 + commlength + 16 + datalength)
        rudisha commlength

    eleza _patchheader(self):
        curpos = self._file.tell()
        ikiwa self._datawritten & 1:
            datalength = self._datawritten + 1
            self._file.write(b'\x00')
        else:
            datalength = self._datawritten
        ikiwa datalength == self._datalength and \
              self._nframes == self._nframeswritten and \
              self._marklength == 0:
            self._file.seek(curpos, 0)
            return
        self._file.seek(self._form_length_pos, 0)
        dummy = self._write_form_length(datalength)
        self._file.seek(self._nframes_pos, 0)
        _write_ulong(self._file, self._nframeswritten)
        self._file.seek(self._ssnd_length_pos, 0)
        _write_ulong(self._file, datalength + 8)
        self._file.seek(curpos, 0)
        self._nframes = self._nframeswritten
        self._datalength = datalength

    eleza _writemarkers(self):
        ikiwa len(self._markers) == 0:
            return
        self._file.write(b'MARK')
        length = 2
        for marker in self._markers:
            id, pos, name = marker
            length = length + len(name) + 1 + 6
            ikiwa len(name) & 1 == 0:
                length = length + 1
        _write_ulong(self._file, length)
        self._marklength = length + 8
        _write_short(self._file, len(self._markers))
        for marker in self._markers:
            id, pos, name = marker
            _write_short(self._file, id)
            _write_ulong(self._file, pos)
            _write_string(self._file, name)

eleza open(f, mode=None):
    ikiwa mode is None:
        ikiwa hasattr(f, 'mode'):
            mode = f.mode
        else:
            mode = 'rb'
    ikiwa mode in ('r', 'rb'):
        rudisha Aifc_read(f)
    elikiwa mode in ('w', 'wb'):
        rudisha Aifc_write(f)
    else:
        raise Error("mode must be 'r', 'rb', 'w', or 'wb'")

eleza openfp(f, mode=None):
    warnings.warn("aifc.openfp is deprecated since Python 3.7. "
                  "Use aifc.open instead.", DeprecationWarning, stacklevel=2)
    rudisha open(f, mode=mode)

ikiwa __name__ == '__main__':
    agiza sys
    ikiwa not sys.argv[1:]:
        sys.argv.append('/usr/demos/data/audio/bach.aiff')
    fn = sys.argv[1]
    with open(fn, 'r') as f:
        andika("Reading", fn)
        andika("nchannels =", f.getnchannels())
        andika("nframes   =", f.getnframes())
        andika("sampwidth =", f.getsampwidth())
        andika("framerate =", f.getframerate())
        andika("comptype  =", f.getcomptype())
        andika("compname  =", f.getcompname())
        ikiwa sys.argv[2:]:
            gn = sys.argv[2]
            andika("Writing", gn)
            with open(gn, 'w') as g:
                g.setparams(f.getparams())
                while 1:
                    data = f.readframes(1024)
                    ikiwa not data:
                        break
                    g.writeframes(data)
            andika("Done.")
