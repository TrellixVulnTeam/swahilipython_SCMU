"""Stuff to parse WAVE files.

Usage.

Reading WAVE files:
      f = wave.open(file, 'r')
where file is either the name of a file or an open file pointer.
The open file pointer must have methods read(), seek(), and close().
When the setpos() and rewind() methods are not used, the seek()
method is not  necessary.

This returns an instance of a kundi with the following public methods:
      getnchannels()  -- returns number of audio channels (1 for
                         mono, 2 for stereo)
      getsampwidth()  -- returns sample width in bytes
      getframerate()  -- returns sampling frequency
      getnframes()    -- returns number of audio frames
      getcomptype()   -- returns compression type ('NONE' for linear samples)
      getcompname()   -- returns human-readable version of
                         compression type ('not compressed' linear samples)
      getparams()     -- returns a namedtuple consisting of all of the
                         above in the above order
      getmarkers()    -- returns None (for compatibility with the
                         aifc module)
      getmark(id)     -- raises an error since the mark does not
                         exist (for compatibility with the aifc module)
      readframes(n)   -- returns at most n frames of audio
      rewind()        -- rewind to the beginning of the audio stream
      setpos(pos)     -- seek to the specified position
      tell()          -- rudisha the current position
      close()         -- close the instance (make it unusable)
The position returned by tell() and the position given to setpos()
are compatible and have nothing to do with the actual position in the
file.
The close() method is called automatically when the kundi instance
is destroyed.

Writing WAVE files:
      f = wave.open(file, 'w')
where file is either the name of a file or an open file pointer.
The open file pointer must have methods write(), tell(), seek(), and
close().

This returns an instance of a kundi with the following public methods:
      setnchannels(n) -- set the number of channels
      setsampwidth(n) -- set the sample width
      setframerate(n) -- set the frame rate
      setnframes(n)   -- set the number of frames
      setcomptype(type, name)
                      -- set the compression type and the
                         human-readable compression type
      setparams(tuple)
                      -- set all parameters at once
      tell()          -- rudisha current position in output file
      writeframesraw(data)
                      -- write audio frames without pathing up the
                         file header
      writeframes(data)
                      -- write audio frames and patch up the file header
      close()         -- patch up the file header and close the
                         output file
You should set the parameters before the first writeframesraw or
writeframes.  The total number of frames does not need to be set,
but when it is set to the correct value, the header does not have to
be patched up.
It is best to first set all parameters, perhaps possibly the
compression type, and then write audio frames using writeframesraw.
When all frames have been written, either call writeframes(b'') or
close() to patch up the sizes in the header.
The close() method is called automatically when the kundi instance
is destroyed.
"""

agiza builtins

__all__ = ["open", "openfp", "Error", "Wave_read", "Wave_write"]

kundi Error(Exception):
    pass

WAVE_FORMAT_PCM = 0x0001

_array_fmts = None, 'b', 'h', None, 'i'

agiza audioop
agiza struct
agiza sys
kutoka chunk agiza Chunk
kutoka collections agiza namedtuple
agiza warnings

_wave_params = namedtuple('_wave_params',
                     'nchannels sampwidth framerate nframes comptype compname')

kundi Wave_read:
    """Variables used in this class:

    These variables are available to the user though appropriate
    methods of this class:
    _file -- the open file with methods read(), close(), and seek()
              set through the __init__() method
    _nchannels -- the number of audio channels
              available through the getnchannels() method
    _nframes -- the number of audio frames
              available through the getnframes() method
    _sampwidth -- the number of bytes per audio sample
              available through the getsampwidth() method
    _framerate -- the sampling frequency
              available through the getframerate() method
    _comptype -- the AIFF-C compression type ('NONE' ikiwa AIFF)
              available through the getcomptype() method
    _compname -- the human-readable AIFF-C compression type
              available through the getcomptype() method
    _soundpos -- the position in the audio stream
              available through the tell() method, set through the
              setpos() method

    These variables are used internally only:
    _fmt_chunk_read -- 1 iff the FMT chunk has been read
    _data_seek_needed -- 1 iff positioned correctly in audio
              file for readframes()
    _data_chunk -- instantiation of a chunk kundi for the DATA chunk
    _framesize -- size of one frame in the file
    """

    eleza initfp(self, file):
        self._convert = None
        self._soundpos = 0
        self._file = Chunk(file, bigendian = 0)
        ikiwa self._file.getname() != b'RIFF':
            raise Error('file does not start with RIFF id')
        ikiwa self._file.read(4) != b'WAVE':
            raise Error('not a WAVE file')
        self._fmt_chunk_read = 0
        self._data_chunk = None
        while 1:
            self._data_seek_needed = 1
            try:
                chunk = Chunk(self._file, bigendian = 0)
            except EOFError:
                break
            chunkname = chunk.getname()
            ikiwa chunkname == b'fmt ':
                self._read_fmt_chunk(chunk)
                self._fmt_chunk_read = 1
            elikiwa chunkname == b'data':
                ikiwa not self._fmt_chunk_read:
                    raise Error('data chunk before fmt chunk')
                self._data_chunk = chunk
                self._nframes = chunk.chunksize // self._framesize
                self._data_seek_needed = 0
                break
            chunk.skip()
        ikiwa not self._fmt_chunk_read or not self._data_chunk:
            raise Error('fmt chunk and/or data chunk missing')

    eleza __init__(self, f):
        self._i_opened_the_file = None
        ikiwa isinstance(f, str):
            f = builtins.open(f, 'rb')
            self._i_opened_the_file = f
        # else, assume it is an open file object already
        try:
            self.initfp(f)
        except:
            ikiwa self._i_opened_the_file:
                f.close()
            raise

    eleza __del__(self):
        self.close()

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
        self._data_seek_needed = 1
        self._soundpos = 0

    eleza close(self):
        self._file = None
        file = self._i_opened_the_file
        ikiwa file:
            self._i_opened_the_file = None
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

    eleza getparams(self):
        rudisha _wave_params(self.getnchannels(), self.getsampwidth(),
                       self.getframerate(), self.getnframes(),
                       self.getcomptype(), self.getcompname())

    eleza getmarkers(self):
        rudisha None

    eleza getmark(self, id):
        raise Error('no marks')

    eleza setpos(self, pos):
        ikiwa pos < 0 or pos > self._nframes:
            raise Error('position not in range')
        self._soundpos = pos
        self._data_seek_needed = 1

    eleza readframes(self, nframes):
        ikiwa self._data_seek_needed:
            self._data_chunk.seek(0, 0)
            pos = self._soundpos * self._framesize
            ikiwa pos:
                self._data_chunk.seek(pos, 0)
            self._data_seek_needed = 0
        ikiwa nframes == 0:
            rudisha b''
        data = self._data_chunk.read(nframes * self._framesize)
        ikiwa self._sampwidth != 1 and sys.byteorder == 'big':
            data = audioop.byteswap(data, self._sampwidth)
        ikiwa self._convert and data:
            data = self._convert(data)
        self._soundpos = self._soundpos + len(data) // (self._nchannels * self._sampwidth)
        rudisha data

    #
    # Internal methods.
    #

    eleza _read_fmt_chunk(self, chunk):
        try:
            wFormatTag, self._nchannels, self._framerate, dwAvgBytesPerSec, wBlockAlign = struct.unpack_kutoka('<HHLLH', chunk.read(14))
        except struct.error:
            raise EOFError kutoka None
        ikiwa wFormatTag == WAVE_FORMAT_PCM:
            try:
                sampwidth = struct.unpack_kutoka('<H', chunk.read(2))[0]
            except struct.error:
                raise EOFError kutoka None
            self._sampwidth = (sampwidth + 7) // 8
            ikiwa not self._sampwidth:
                raise Error('bad sample width')
        else:
            raise Error('unknown format: %r' % (wFormatTag,))
        ikiwa not self._nchannels:
            raise Error('bad # of channels')
        self._framesize = self._nchannels * self._sampwidth
        self._comptype = 'NONE'
        self._compname = 'not compressed'

kundi Wave_write:
    """Variables used in this class:

    These variables are user settable through appropriate methods
    of this class:
    _file -- the open file with methods write(), close(), tell(), seek()
              set through the __init__() method
    _comptype -- the AIFF-C compression type ('NONE' in AIFF)
              set through the setcomptype() or setparams() method
    _compname -- the human-readable AIFF-C compression type
              set through the setcomptype() or setparams() method
    _nchannels -- the number of audio channels
              set through the setnchannels() or setparams() method
    _sampwidth -- the number of bytes per audio sample
              set through the setsampwidth() or setparams() method
    _framerate -- the sampling frequency
              set through the setframerate() or setparams() method
    _nframes -- the number of audio frames written to the header
              set through the setnframes() or setparams() method

    These variables are used internally only:
    _datalength -- the size of the audio samples written to the header
    _nframeswritten -- the number of frames actually written
    _datawritten -- the size of the audio samples actually written
    """

    eleza __init__(self, f):
        self._i_opened_the_file = None
        ikiwa isinstance(f, str):
            f = builtins.open(f, 'wb')
            self._i_opened_the_file = f
        try:
            self.initfp(f)
        except:
            ikiwa self._i_opened_the_file:
                f.close()
            raise

    eleza initfp(self, file):
        self._file = file
        self._convert = None
        self._nchannels = 0
        self._sampwidth = 0
        self._framerate = 0
        self._nframes = 0
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._headerwritten = False

    eleza __del__(self):
        self.close()

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.close()

    #
    # User visible methods.
    #
    eleza setnchannels(self, nchannels):
        ikiwa self._datawritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa nchannels < 1:
            raise Error('bad # of channels')
        self._nchannels = nchannels

    eleza getnchannels(self):
        ikiwa not self._nchannels:
            raise Error('number of channels not set')
        rudisha self._nchannels

    eleza setsampwidth(self, sampwidth):
        ikiwa self._datawritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa sampwidth < 1 or sampwidth > 4:
            raise Error('bad sample width')
        self._sampwidth = sampwidth

    eleza getsampwidth(self):
        ikiwa not self._sampwidth:
            raise Error('sample width not set')
        rudisha self._sampwidth

    eleza setframerate(self, framerate):
        ikiwa self._datawritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa framerate <= 0:
            raise Error('bad frame rate')
        self._framerate = int(round(framerate))

    eleza getframerate(self):
        ikiwa not self._framerate:
            raise Error('frame rate not set')
        rudisha self._framerate

    eleza setnframes(self, nframes):
        ikiwa self._datawritten:
            raise Error('cannot change parameters after starting to write')
        self._nframes = nframes

    eleza getnframes(self):
        rudisha self._nframeswritten

    eleza setcomptype(self, comptype, compname):
        ikiwa self._datawritten:
            raise Error('cannot change parameters after starting to write')
        ikiwa comptype not in ('NONE',):
            raise Error('unsupported compression type')
        self._comptype = comptype
        self._compname = compname

    eleza getcomptype(self):
        rudisha self._comptype

    eleza getcompname(self):
        rudisha self._compname

    eleza setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        ikiwa self._datawritten:
            raise Error('cannot change parameters after starting to write')
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    eleza getparams(self):
        ikiwa not self._nchannels or not self._sampwidth or not self._framerate:
            raise Error('not all parameters set')
        rudisha _wave_params(self._nchannels, self._sampwidth, self._framerate,
              self._nframes, self._comptype, self._compname)

    eleza setmark(self, id, pos, name):
        raise Error('setmark() not supported')

    eleza getmark(self, id):
        raise Error('no marks')

    eleza getmarkers(self):
        rudisha None

    eleza tell(self):
        rudisha self._nframeswritten

    eleza writeframesraw(self, data):
        ikiwa not isinstance(data, (bytes, bytearray)):
            data = memoryview(data).cast('B')
        self._ensure_header_written(len(data))
        nframes = len(data) // (self._sampwidth * self._nchannels)
        ikiwa self._convert:
            data = self._convert(data)
        ikiwa self._sampwidth != 1 and sys.byteorder == 'big':
            data = audioop.byteswap(data, self._sampwidth)
        self._file.write(data)
        self._datawritten += len(data)
        self._nframeswritten = self._nframeswritten + nframes

    eleza writeframes(self, data):
        self.writeframesraw(data)
        ikiwa self._datalength != self._datawritten:
            self._patchheader()

    eleza close(self):
        try:
            ikiwa self._file:
                self._ensure_header_written(0)
                ikiwa self._datalength != self._datawritten:
                    self._patchheader()
                self._file.flush()
        finally:
            self._file = None
            file = self._i_opened_the_file
            ikiwa file:
                self._i_opened_the_file = None
                file.close()

    #
    # Internal methods.
    #

    eleza _ensure_header_written(self, datasize):
        ikiwa not self._headerwritten:
            ikiwa not self._nchannels:
                raise Error('# channels not specified')
            ikiwa not self._sampwidth:
                raise Error('sample width not specified')
            ikiwa not self._framerate:
                raise Error('sampling rate not specified')
            self._write_header(datasize)

    eleza _write_header(self, initlength):
        assert not self._headerwritten
        self._file.write(b'RIFF')
        ikiwa not self._nframes:
            self._nframes = initlength // (self._nchannels * self._sampwidth)
        self._datalength = self._nframes * self._nchannels * self._sampwidth
        try:
            self._form_length_pos = self._file.tell()
        except (AttributeError, OSError):
            self._form_length_pos = None
        self._file.write(struct.pack('<L4s4sLHHLLHH4s',
            36 + self._datalength, b'WAVE', b'fmt ', 16,
            WAVE_FORMAT_PCM, self._nchannels, self._framerate,
            self._nchannels * self._framerate * self._sampwidth,
            self._nchannels * self._sampwidth,
            self._sampwidth * 8, b'data'))
        ikiwa self._form_length_pos is not None:
            self._data_length_pos = self._file.tell()
        self._file.write(struct.pack('<L', self._datalength))
        self._headerwritten = True

    eleza _patchheader(self):
        assert self._headerwritten
        ikiwa self._datawritten == self._datalength:
            return
        curpos = self._file.tell()
        self._file.seek(self._form_length_pos, 0)
        self._file.write(struct.pack('<L', 36 + self._datawritten))
        self._file.seek(self._data_length_pos, 0)
        self._file.write(struct.pack('<L', self._datawritten))
        self._file.seek(curpos, 0)
        self._datalength = self._datawritten

eleza open(f, mode=None):
    ikiwa mode is None:
        ikiwa hasattr(f, 'mode'):
            mode = f.mode
        else:
            mode = 'rb'
    ikiwa mode in ('r', 'rb'):
        rudisha Wave_read(f)
    elikiwa mode in ('w', 'wb'):
        rudisha Wave_write(f)
    else:
        raise Error("mode must be 'r', 'rb', 'w', or 'wb'")

eleza openfp(f, mode=None):
    warnings.warn("wave.openfp is deprecated since Python 3.7. "
                  "Use wave.open instead.", DeprecationWarning, stacklevel=2)
    rudisha open(f, mode=mode)
