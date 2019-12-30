"""Stuff to parse AIFF-C na AIFF files.

Unless explicitly stated otherwise, the description below ni true
both kila AIFF-C files na AIFF files.

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
big endian order), followed by the data.  The size field does sio include
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
      kwenye AIFF-C files only:
      <compression type> (4 bytes)
      <human-readable version of compression type> ("pstring")
  SSND
      <offset> (4 bytes, sio used by this program)
      <blocksize> (4 bytes, sio used by this program)
      <sound data>

A pstring consists of 1 byte length, a string of characters, na 0 ama 1
byte pad to make the total length even.

Usage.

Reading AIFF files:
  f = aifc.open(file, 'r')
where file ni either the name of a file ama an open file pointer.
The open file pointer must have methods read(), seek(), na close().
In some types of audio files, ikiwa the setpos() method ni sio used,
the seek() method ni sio necessary.

This returns an instance of a kundi ukijumuisha the following public methods:
  getnchannels()  -- returns number of audio channels (1 for
             mono, 2 kila stereo)
  getsampwidth()  -- returns sample width kwenye bytes
  getframerate()  -- returns sampling frequency
  getnframes()    -- returns number of audio frames
  getcomptype()   -- returns compression type ('NONE' kila AIFF files)
  getcompname()   -- returns human-readable version of
             compression type ('not compressed' kila AIFF files)
  getparams() -- returns a namedtuple consisting of all of the
             above kwenye the above order
  getmarkers()    -- get the list of marks kwenye the audio file ama Tupu
             ikiwa there are no marks
  getmark(id) -- get mark ukijumuisha the specified id (raises an error
             ikiwa the mark does sio exist)
  readframes(n)   -- returns at most n frames of audio
  rewind()    -- rewind to the beginning of the audio stream
  setpos(pos) -- seek to the specified position
  tell()      -- rudisha the current position
  close()     -- close the instance (make it unusable)
The position returned by tell(), the position given to setpos() na
the position of marks are all compatible na have nothing to do with
the actual position kwenye the file.
The close() method ni called automatically when the kundi instance
is destroyed.

Writing AIFF files:
  f = aifc.open(file, 'w')
where file ni either the name of a file ama an open file pointer.
The open file pointer must have methods write(), tell(), seek(), na
close().

This returns an instance of a kundi ukijumuisha the following public methods:
  aiff()      -- create an AIFF file (AIFF-C default)
  aifc()      -- create an AIFF-C file
  setnchannels(n) -- set the number of channels
  setsampwidth(n) -- set the sample width
  setframerate(n) -- set the frame rate
  setnframes(n)   -- set the number of frames
  setcomptype(type, name)
          -- set the compression type na the
             human-readable compression type
  setparams(tuple)
          -- set all parameters at once
  setmark(id, pos, name)
          -- add specified mark to the list of marks
  tell()      -- rudisha current position kwenye output file (useful
             kwenye combination ukijumuisha setmark())
  writeframesraw(data)
          -- write audio frames without pathing up the
             file header
  writeframes(data)
          -- write audio frames na patch up the file header
  close()     -- patch up the file header na close the
             output file
You should set the parameters before the first writeframesraw ama
writeframes.  The total number of frames does sio need to be set,
but when it ni set to the correct value, the header does sio have to
be patched up.
It ni best to first set all parameters, perhaps possibly the
compression type, na then write audio frames using writeframesraw.
When all frames have been written, either call writeframes(b'') ama
close() to patch up the sizes kwenye the header.
Marks can be added anytime.  If there are any marks, you must call
close() after all frames have been written.
The close() method ni called automatically when the kundi instance
is destroyed.

When a file ni opened ukijumuisha the extension '.aiff', an AIFF file is
written, otherwise an AIFF-C file ni written.  This default can be
changed by calling aiff() ama aifc() before the first writeframes ama
writeframesraw.
"""

agiza struct
agiza builtins
agiza warnings

__all__ = ["Error", "open", "openfp"]

kundi Error(Exception):
    pita

_AIFC_version = 0xA2805140     # Version 1 of AIFF-C

eleza _read_long(file):
    jaribu:
        rudisha struct.unpack('>l', file.read(4))[0]
    tatizo struct.error:
        ashiria EOFError kutoka Tupu

eleza _read_ulong(file):
    jaribu:
        rudisha struct.unpack('>L', file.read(4))[0]
    tatizo struct.error:
        ashiria EOFError kutoka Tupu

eleza _read_short(file):
    jaribu:
        rudisha struct.unpack('>h', file.read(2))[0]
    tatizo struct.error:
        ashiria EOFError kutoka Tupu

eleza _read_ushort(file):
    jaribu:
        rudisha struct.unpack('>H', file.read(2))[0]
    tatizo struct.error:
        ashiria EOFError kutoka Tupu

eleza _read_string(file):
    length = ord(file.read(1))
    ikiwa length == 0:
        data = b''
    isipokua:
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
    lasivyo expon == 0x7FFF:
        f = _HUGE_VAL
    isipokua:
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
        ashiria ValueError("string exceeds maximum pstring length")
    f.write(struct.pack('B', len(s)))
    f.write(s)
    ikiwa len(s) & 1 == 0:
        f.write(b'\x00')

eleza _write_float(f, x):
    agiza math
    ikiwa x < 0:
        sign = 0x8000
        x = x * -1
    isipokua:
        sign = 0
    ikiwa x == 0:
        expon = 0
        himant = 0
        lomant = 0
    isipokua:
        fmant, expon = math.frexp(x)
        ikiwa expon > 16384 ama fmant >= 1 ama fmant != fmant: # Infinity ama NaN
            expon = sign|0x7FFF
            himant = 0
            lomant = 0
        isipokua:                   # Finite
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

_aifc_params.nchannels.__doc__ = 'Number of audio channels (1 kila mono, 2 kila stereo)'
_aifc_params.sampwidth.__doc__ = 'Sample width kwenye bytes'
_aifc_params.framerate.__doc__ = 'Sampling frequency'
_aifc_params.nframes.__doc__ = 'Number of audio frames'
_aifc_params.comptype.__doc__ = 'Compression type ("NONE" kila AIFF files)'
_aifc_params.compname.__doc__ = ("""\
A human-readable version of the compression type
('not compressed' kila AIFF files)""")


kundi Aifc_read:
    # Variables used kwenye this class:
    #
    # These variables are available to the user though appropriate
    # methods of this class:
    # _file -- the open file ukijumuisha methods read(), close(), na seek()
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
    # _markers -- the marks kwenye the audio file
    #       available through the getmarkers() na getmark()
    #       methods
    # _soundpos -- the position kwenye the audio stream
    #       available through the tell() method, set through the
    #       setpos() method
    #
    # These variables are used internally only:
    # _version -- the AIFF-C version number
    # _decomp -- the decompressor kutoka builtin module cl
    # _comm_chunk_read -- 1 iff the COMM chunk has been read
    # _aifc -- 1 iff reading an AIFF-C file
    # _ssnd_seek_needed -- 1 iff positioned correctly kwenye audio
    #       file kila readframes()
    # _ssnd_chunk -- instantiation of a chunk kundi kila the SSND chunk
    # _framesize -- size of one frame kwenye the file

    _file = Tupu  # Set here since __del__ checks it

    eleza initfp(self, file):
        self._version = 0
        self._convert = Tupu
        self._markers = []
        self._soundpos = 0
        self._file = file
        chunk = Chunk(file)
        ikiwa chunk.getname() != b'FORM':
            ashiria Error('file does sio start ukijumuisha FORM id')
        formdata = chunk.read(4)
        ikiwa formdata == b'AIFF':
            self._aifc = 0
        lasivyo formdata == b'AIFC':
            self._aifc = 1
        isipokua:
            ashiria Error('not an AIFF ama AIFF-C file')
        self._comm_chunk_read = 0
        self._ssnd_chunk = Tupu
        wakati 1:
            self._ssnd_seek_needed = 1
            jaribu:
                chunk = Chunk(self._file)
            tatizo EOFError:
                koma
            chunkname = chunk.getname()
            ikiwa chunkname == b'COMM':
                self._read_comm_chunk(chunk)
                self._comm_chunk_read = 1
            lasivyo chunkname == b'SSND':
                self._ssnd_chunk = chunk
                dummy = chunk.read(8)
                self._ssnd_seek_needed = 0
            lasivyo chunkname == b'FVER':
                self._version = _read_ulong(chunk)
            lasivyo chunkname == b'MARK':
                self._readmark(chunk)
            chunk.skip()
        ikiwa sio self._comm_chunk_read ama sio self._ssnd_chunk:
            ashiria Error('COMM chunk and/or SSND chunk missing')

    eleza __init__(self, f):
        ikiwa isinstance(f, str):
            file_object = builtins.open(f, 'rb')
            jaribu:
                self.initfp(file_object)
            tatizo:
                file_object.close()
                raise
        isipokua:
            # assume it ni an open file object already
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
        ikiwa file ni sio Tupu:
            self._file = Tupu
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
            rudisha Tupu
        rudisha self._markers

    eleza getmark(self, id):
        kila marker kwenye self._markers:
            ikiwa id == marker[0]:
                rudisha marker
        ashiria Error('marker {0!r} does sio exist'.format(id))

    eleza setpos(self, pos):
        ikiwa pos < 0 ama pos > self._nframes:
            ashiria Error('position haiko kwenye range')
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
        ikiwa self._convert na data:
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
        ikiwa sio hasattr(self, '_adpcmstate'):
            # first time
            self._adpcmstate = Tupu
        data, self._adpcmstate = audioop.adpcm2lin(data, 2, self._adpcmstate)
        rudisha data

    eleza _read_comm_chunk(self, chunk):
        self._nchannels = _read_short(chunk)
        self._nframes = _read_long(chunk)
        self._sampwidth = (_read_short(chunk) + 7) // 8
        self._framerate = int(_read_float(chunk))
        ikiwa self._sampwidth <= 0:
            ashiria Error('bad sample width')
        ikiwa self._nchannels <= 0:
            ashiria Error('bad # of channels')
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
                lasivyo self._comptype kwenye (b'ulaw', b'ULAW'):
                    self._convert = self._ulaw2lin
                lasivyo self._comptype kwenye (b'alaw', b'ALAW'):
                    self._convert = self._alaw2lin
                isipokua:
                    ashiria Error('unsupported compression type')
                self._sampwidth = 2
        isipokua:
            self._comptype = b'NONE'
            self._compname = b'not compressed'

    eleza _readmark(self, chunk):
        nmarkers = _read_short(chunk)
        # Some files appear to contain invalid counts.
        # Cope ukijumuisha this by testing kila EOF.
        jaribu:
            kila i kwenye range(nmarkers):
                id = _read_short(chunk)
                pos = _read_long(chunk)
                name = _read_string(chunk)
                ikiwa pos ama name:
                    # some files appear to have
                    # dummy markers consisting of
                    # a position 0 na name ''
                    self._markers.append((id, pos, name))
        tatizo EOFError:
            w = ('Warning: MARK chunk contains only %s marker%s instead of %s' %
                 (len(self._markers), '' ikiwa len(self._markers) == 1 isipokua 's',
                  nmarkers))
            warnings.warn(w)

kundi Aifc_write:
    # Variables used kwenye this class:
    #
    # These variables are user settable through appropriate methods
    # of this class:
    # _file -- the open file ukijumuisha methods write(), close(), tell(), seek()
    #       set through the __init__() method
    # _comptype -- the AIFF-C compression type ('NONE' kwenye AIFF)
    #       set through the setcomptype() ama setparams() method
    # _compname -- the human-readable AIFF-C compression type
    #       set through the setcomptype() ama setparams() method
    # _nchannels -- the number of audio channels
    #       set through the setnchannels() ama setparams() method
    # _sampwidth -- the number of bytes per audio sample
    #       set through the setsampwidth() ama setparams() method
    # _framerate -- the sampling frequency
    #       set through the setframerate() ama setparams() method
    # _nframes -- the number of audio frames written to the header
    #       set through the setnframes() ama setparams() method
    # _aifc -- whether we're writing an AIFF-C file ama an AIFF file
    #       set through the aifc() method, reset through the
    #       aiff() method
    #
    # These variables are used internally only:
    # _version -- the AIFF-C version number
    # _comp -- the compressor kutoka builtin module cl
    # _nframeswritten -- the number of audio frames actually written
    # _datalength -- the size of the audio samples written to the header
    # _datawritten -- the size of the audio samples actually written

    _file = Tupu  # Set here since __del__ checks it

    eleza __init__(self, f):
        ikiwa isinstance(f, str):
            file_object = builtins.open(f, 'wb')
            jaribu:
                self.initfp(file_object)
            tatizo:
                file_object.close()
                raise

            # treat .aiff file extensions kama non-compressed audio
            ikiwa f.endswith('.aiff'):
                self._aifc = 0
        isipokua:
            # assume it ni an open file object already
            self.initfp(f)

    eleza initfp(self, file):
        self._file = file
        self._version = _AIFC_version
        self._comptype = b'NONE'
        self._compname = b'not compressed'
        self._convert = Tupu
        self._nchannels = 0
        self._sampwidth = 0
        self._framerate = 0
        self._nframes = 0
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._markers = []
        self._marklength = 0
        self._aifc = 1      # AIFF-C ni default

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
            ashiria Error('cannot change parameters after starting to write')
        self._aifc = 0

    eleza aifc(self):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        self._aifc = 1

    eleza setnchannels(self, nchannels):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa nchannels < 1:
            ashiria Error('bad # of channels')
        self._nchannels = nchannels

    eleza getnchannels(self):
        ikiwa sio self._nchannels:
            ashiria Error('number of channels sio set')
        rudisha self._nchannels

    eleza setsampwidth(self, sampwidth):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa sampwidth < 1 ama sampwidth > 4:
            ashiria Error('bad sample width')
        self._sampwidth = sampwidth

    eleza getsampwidth(self):
        ikiwa sio self._sampwidth:
            ashiria Error('sample width sio set')
        rudisha self._sampwidth

    eleza setframerate(self, framerate):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa framerate <= 0:
            ashiria Error('bad frame rate')
        self._framerate = framerate

    eleza getframerate(self):
        ikiwa sio self._framerate:
            ashiria Error('frame rate sio set')
        rudisha self._framerate

    eleza setnframes(self, nframes):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        self._nframes = nframes

    eleza getnframes(self):
        rudisha self._nframeswritten

    eleza setcomptype(self, comptype, compname):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa comptype haiko kwenye (b'NONE', b'ulaw', b'ULAW',
                            b'alaw', b'ALAW', b'G722'):
            ashiria Error('unsupported compression type')
        self._comptype = comptype
        self._compname = compname

    eleza getcomptype(self):
        rudisha self._comptype

    eleza getcompname(self):
        rudisha self._compname

##  eleza setversion(self, version):
##      ikiwa self._nframeswritten:
##          ashiria Error, 'cannot change parameters after starting to write'
##      self._version = version

    eleza setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa comptype haiko kwenye (b'NONE', b'ulaw', b'ULAW',
                            b'alaw', b'ALAW', b'G722'):
            ashiria Error('unsupported compression type')
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    eleza getparams(self):
        ikiwa sio self._nchannels ama sio self._sampwidth ama sio self._framerate:
            ashiria Error('not all parameters set')
        rudisha _aifc_params(self._nchannels, self._sampwidth, self._framerate,
                            self._nframes, self._comptype, self._compname)

    eleza setmark(self, id, pos, name):
        ikiwa id <= 0:
            ashiria Error('marker ID must be > 0')
        ikiwa pos < 0:
            ashiria Error('marker position must be >= 0')
        ikiwa sio isinstance(name, bytes):
            ashiria Error('marker name must be bytes')
        kila i kwenye range(len(self._markers)):
            ikiwa id == self._markers[i][0]:
                self._markers[i] = id, pos, name
                return
        self._markers.append((id, pos, name))

    eleza getmark(self, id):
        kila marker kwenye self._markers:
            ikiwa id == marker[0]:
                rudisha marker
        ashiria Error('marker {0!r} does sio exist'.format(id))

    eleza getmarkers(self):
        ikiwa len(self._markers) == 0:
            rudisha Tupu
        rudisha self._markers

    eleza tell(self):
        rudisha self._nframeswritten

    eleza writeframesraw(self, data):
        ikiwa sio isinstance(data, (bytes, bytearray)):
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
        ikiwa self._nframeswritten != self._nframes ama \
              self._datalength != self._datawritten:
            self._patchheader()

    eleza close(self):
        ikiwa self._file ni Tupu:
            return
        jaribu:
            self._ensure_header_written(0)
            ikiwa self._datawritten & 1:
                # quick pad to even size
                self._file.write(b'\x00')
                self._datawritten = self._datawritten + 1
            self._writemarkers()
            ikiwa self._nframeswritten != self._nframes ama \
                  self._datalength != self._datawritten ama \
                  self._marklength:
                self._patchheader()
        mwishowe:
            # Prevent ref cycles
            self._convert = Tupu
            f = self._file
            self._file = Tupu
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
        ikiwa sio hasattr(self, '_adpcmstate'):
            self._adpcmstate = Tupu
        data, self._adpcmstate = audioop.lin2adpcm(data, 2, self._adpcmstate)
        rudisha data

    eleza _ensure_header_written(self, datasize):
        ikiwa sio self._nframeswritten:
            ikiwa self._comptype kwenye (b'ULAW', b'ulaw', b'ALAW', b'alaw', b'G722'):
                ikiwa sio self._sampwidth:
                    self._sampwidth = 2
                ikiwa self._sampwidth != 2:
                    ashiria Error('sample width must be 2 when compressing '
                                'ukijumuisha ulaw/ULAW, alaw/ALAW ama G7.22 (ADPCM)')
            ikiwa sio self._nchannels:
                ashiria Error('# channels sio specified')
            ikiwa sio self._sampwidth:
                ashiria Error('sample width sio specified')
            ikiwa sio self._framerate:
                ashiria Error('sampling rate sio specified')
            self._write_header(datasize)

    eleza _init_compression(self):
        ikiwa self._comptype == b'G722':
            self._convert = self._lin2adpcm
        lasivyo self._comptype kwenye (b'ulaw', b'ULAW'):
            self._convert = self._lin2ulaw
        lasivyo self._comptype kwenye (b'alaw', b'ALAW'):
            self._convert = self._lin2alaw

    eleza _write_header(self, initlength):
        ikiwa self._aifc na self._comptype != b'NONE':
            self._init_compression()
        self._file.write(b'FORM')
        ikiwa sio self._nframes:
            self._nframes = initlength // (self._nchannels * self._sampwidth)
        self._datalength = self._nframes * self._nchannels * self._sampwidth
        ikiwa self._datalength & 1:
            self._datalength = self._datalength + 1
        ikiwa self._aifc:
            ikiwa self._comptype kwenye (b'ulaw', b'ULAW', b'alaw', b'ALAW'):
                self._datalength = self._datalength // 2
                ikiwa self._datalength & 1:
                    self._datalength = self._datalength + 1
            lasivyo self._comptype == b'G722':
                self._datalength = (self._datalength + 3) // 4
                ikiwa self._datalength & 1:
                    self._datalength = self._datalength + 1
        jaribu:
            self._form_length_pos = self._file.tell()
        tatizo (AttributeError, OSError):
            self._form_length_pos = Tupu
        commlength = self._write_form_length(self._datalength)
        ikiwa self._aifc:
            self._file.write(b'AIFC')
            self._file.write(b'FVER')
            _write_ulong(self._file, 4)
            _write_ulong(self._file, self._version)
        isipokua:
            self._file.write(b'AIFF')
        self._file.write(b'COMM')
        _write_ulong(self._file, commlength)
        _write_short(self._file, self._nchannels)
        ikiwa self._form_length_pos ni sio Tupu:
            self._nframes_pos = self._file.tell()
        _write_ulong(self._file, self._nframes)
        ikiwa self._comptype kwenye (b'ULAW', b'ulaw', b'ALAW', b'alaw', b'G722'):
            _write_short(self._file, 8)
        isipokua:
            _write_short(self._file, self._sampwidth * 8)
        _write_float(self._file, self._framerate)
        ikiwa self._aifc:
            self._file.write(self._comptype)
            _write_string(self._file, self._compname)
        self._file.write(b'SSND')
        ikiwa self._form_length_pos ni sio Tupu:
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
        isipokua:
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
        isipokua:
            datalength = self._datawritten
        ikiwa datalength == self._datalength na \
              self._nframes == self._nframeswritten na \
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
        kila marker kwenye self._markers:
            id, pos, name = marker
            length = length + len(name) + 1 + 6
            ikiwa len(name) & 1 == 0:
                length = length + 1
        _write_ulong(self._file, length)
        self._marklength = length + 8
        _write_short(self._file, len(self._markers))
        kila marker kwenye self._markers:
            id, pos, name = marker
            _write_short(self._file, id)
            _write_ulong(self._file, pos)
            _write_string(self._file, name)

eleza open(f, mode=Tupu):
    ikiwa mode ni Tupu:
        ikiwa hasattr(f, 'mode'):
            mode = f.mode
        isipokua:
            mode = 'rb'
    ikiwa mode kwenye ('r', 'rb'):
        rudisha Aifc_read(f)
    lasivyo mode kwenye ('w', 'wb'):
        rudisha Aifc_write(f)
    isipokua:
        ashiria Error("mode must be 'r', 'rb', 'w', ama 'wb'")

eleza openfp(f, mode=Tupu):
    warnings.warn("aifc.openfp ni deprecated since Python 3.7. "
                  "Use aifc.open instead.", DeprecationWarning, stacklevel=2)
    rudisha open(f, mode=mode)

ikiwa __name__ == '__main__':
    agiza sys
    ikiwa sio sys.argv[1:]:
        sys.argv.append('/usr/demos/data/audio/bach.aiff')
    fn = sys.argv[1]
    ukijumuisha open(fn, 'r') kama f:
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
            ukijumuisha open(gn, 'w') kama g:
                g.setparams(f.getparams())
                wakati 1:
                    data = f.readframes(1024)
                    ikiwa sio data:
                        koma
                    g.writeframes(data)
            andika("Done.")
