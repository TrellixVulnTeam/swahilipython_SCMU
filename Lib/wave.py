"""Stuff to parse WAVE files.

Usage.

Reading WAVE files:
      f = wave.open(file, 'r')
where file ni either the name of a file ama an open file pointer.
The open file pointer must have methods read(), seek(), na close().
When the setpos() na rewind() methods are sio used, the seek()
method ni sio  necessary.

This rudishas an instance of a kundi ukijumuisha the following public methods:
      getnchannels()  -- rudishas number of audio channels (1 for
                         mono, 2 kila stereo)
      getsampwidth()  -- rudishas sample width kwenye bytes
      getframerate()  -- rudishas sampling frequency
      getnframes()    -- rudishas number of audio frames
      getcomptype()   -- rudishas compression type ('NONE' kila linear samples)
      getcompname()   -- rudishas human-readable version of
                         compression type ('not compressed' linear samples)
      getparams()     -- rudishas a namedtuple consisting of all of the
                         above kwenye the above order
      getmarkers()    -- rudishas Tupu (kila compatibility ukijumuisha the
                         aifc module)
      getmark(id)     -- ashirias an error since the mark does not
                         exist (kila compatibility ukijumuisha the aifc module)
      readframes(n)   -- rudishas at most n frames of audio
      rewind()        -- rewind to the beginning of the audio stream
      setpos(pos)     -- seek to the specified position
      tell()          -- rudisha the current position
      close()         -- close the instance (make it unusable)
The position rudishaed by tell() na the position given to setpos()
are compatible na have nothing to do ukijumuisha the actual position kwenye the
file.
The close() method ni called automatically when the kundi instance
is destroyed.

Writing WAVE files:
      f = wave.open(file, 'w')
where file ni either the name of a file ama an open file pointer.
The open file pointer must have methods write(), tell(), seek(), na
close().

This rudishas an instance of a kundi ukijumuisha the following public methods:
      setnchannels(n) -- set the number of channels
      setsampwidth(n) -- set the sample width
      setframerate(n) -- set the frame rate
      setnframes(n)   -- set the number of frames
      setcomptype(type, name)
                      -- set the compression type na the
                         human-readable compression type
      setparams(tuple)
                      -- set all parameters at once
      tell()          -- rudisha current position kwenye output file
      writeframesraw(data)
                      -- write audio frames without pathing up the
                         file header
      writeframes(data)
                      -- write audio frames na patch up the file header
      close()         -- patch up the file header na close the
                         output file
You should set the parameters before the first writeframesraw ama
writeframes.  The total number of frames does sio need to be set,
but when it ni set to the correct value, the header does sio have to
be patched up.
It ni best to first set all parameters, perhaps possibly the
compression type, na then write audio frames using writeframesraw.
When all frames have been written, either call writeframes(b'') ama
close() to patch up the sizes kwenye the header.
The close() method ni called automatically when the kundi instance
is destroyed.
"""

agiza builtins

__all__ = ["open", "openfp", "Error", "Wave_read", "Wave_write"]

kundi Error(Exception):
    pita

WAVE_FORMAT_PCM = 0x0001

_array_fmts = Tupu, 'b', 'h', Tupu, 'i'

agiza audioop
agiza struct
agiza sys
kutoka chunk agiza Chunk
kutoka collections agiza namedtuple
agiza warnings

_wave_params = namedtuple('_wave_params',
                     'nchannels sampwidth framerate nframes comptype compname')

kundi Wave_read:
    """Variables used kwenye this class:

    These variables are available to the user though appropriate
    methods of this class:
    _file -- the open file ukijumuisha methods read(), close(), na seek()
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
    _soundpos -- the position kwenye the audio stream
              available through the tell() method, set through the
              setpos() method

    These variables are used internally only:
    _fmt_chunk_read -- 1 iff the FMT chunk has been read
    _data_seek_needed -- 1 iff positioned correctly kwenye audio
              file kila readframes()
    _data_chunk -- instantiation of a chunk kundi kila the DATA chunk
    _framesize -- size of one frame kwenye the file
    """

    eleza initfp(self, file):
        self._convert = Tupu
        self._soundpos = 0
        self._file = Chunk(file, bigendian = 0)
        ikiwa self._file.getname() != b'RIFF':
            ashiria Error('file does sio start ukijumuisha RIFF id')
        ikiwa self._file.read(4) != b'WAVE':
            ashiria Error('not a WAVE file')
        self._fmt_chunk_read = 0
        self._data_chunk = Tupu
        wakati 1:
            self._data_seek_needed = 1
            jaribu:
                chunk = Chunk(self._file, bigendian = 0)
            tatizo EOFError:
                koma
            chunkname = chunk.getname()
            ikiwa chunkname == b'fmt ':
                self._read_fmt_chunk(chunk)
                self._fmt_chunk_read = 1
            lasivyo chunkname == b'data':
                ikiwa sio self._fmt_chunk_read:
                    ashiria Error('data chunk before fmt chunk')
                self._data_chunk = chunk
                self._nframes = chunk.chunksize // self._framesize
                self._data_seek_needed = 0
                koma
            chunk.skip()
        ikiwa sio self._fmt_chunk_read ama sio self._data_chunk:
            ashiria Error('fmt chunk and/or data chunk missing')

    eleza __init__(self, f):
        self._i_opened_the_file = Tupu
        ikiwa isinstance(f, str):
            f = builtins.open(f, 'rb')
            self._i_opened_the_file = f
        # else, assume it ni an open file object already
        jaribu:
            self.initfp(f)
        tatizo:
            ikiwa self._i_opened_the_file:
                f.close()
            ashiria

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
        self._file = Tupu
        file = self._i_opened_the_file
        ikiwa file:
            self._i_opened_the_file = Tupu
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
        rudisha Tupu

    eleza getmark(self, id):
        ashiria Error('no marks')

    eleza setpos(self, pos):
        ikiwa pos < 0 ama pos > self._nframes:
            ashiria Error('position haiko kwenye range')
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
        ikiwa self._sampwidth != 1 na sys.byteorder == 'big':
            data = audioop.byteswap(data, self._sampwidth)
        ikiwa self._convert na data:
            data = self._convert(data)
        self._soundpos = self._soundpos + len(data) // (self._nchannels * self._sampwidth)
        rudisha data

    #
    # Internal methods.
    #

    eleza _read_fmt_chunk(self, chunk):
        jaribu:
            wFormatTag, self._nchannels, self._framerate, dwAvgBytesPerSec, wBlockAlign = struct.unpack_kutoka('<HHLLH', chunk.read(14))
        tatizo struct.error:
            ashiria EOFError kutoka Tupu
        ikiwa wFormatTag == WAVE_FORMAT_PCM:
            jaribu:
                sampwidth = struct.unpack_kutoka('<H', chunk.read(2))[0]
            tatizo struct.error:
                ashiria EOFError kutoka Tupu
            self._sampwidth = (sampwidth + 7) // 8
            ikiwa sio self._sampwidth:
                ashiria Error('bad sample width')
        isipokua:
            ashiria Error('unknown format: %r' % (wFormatTag,))
        ikiwa sio self._nchannels:
            ashiria Error('bad # of channels')
        self._framesize = self._nchannels * self._sampwidth
        self._comptype = 'NONE'
        self._compname = 'not compressed'

kundi Wave_write:
    """Variables used kwenye this class:

    These variables are user settable through appropriate methods
    of this class:
    _file -- the open file ukijumuisha methods write(), close(), tell(), seek()
              set through the __init__() method
    _comptype -- the AIFF-C compression type ('NONE' kwenye AIFF)
              set through the setcomptype() ama setparams() method
    _compname -- the human-readable AIFF-C compression type
              set through the setcomptype() ama setparams() method
    _nchannels -- the number of audio channels
              set through the setnchannels() ama setparams() method
    _sampwidth -- the number of bytes per audio sample
              set through the setsampwidth() ama setparams() method
    _framerate -- the sampling frequency
              set through the setframerate() ama setparams() method
    _nframes -- the number of audio frames written to the header
              set through the setnframes() ama setparams() method

    These variables are used internally only:
    _datalength -- the size of the audio samples written to the header
    _nframeswritten -- the number of frames actually written
    _datawritten -- the size of the audio samples actually written
    """

    eleza __init__(self, f):
        self._i_opened_the_file = Tupu
        ikiwa isinstance(f, str):
            f = builtins.open(f, 'wb')
            self._i_opened_the_file = f
        jaribu:
            self.initfp(f)
        tatizo:
            ikiwa self._i_opened_the_file:
                f.close()
            ashiria

    eleza initfp(self, file):
        self._file = file
        self._convert = Tupu
        self._nchannels = 0
        self._sampwidth = 0
        self._framerate = 0
        self._nframes = 0
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._headerwritten = Uongo

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
            ashiria Error('cannot change parameters after starting to write')
        ikiwa nchannels < 1:
            ashiria Error('bad # of channels')
        self._nchannels = nchannels

    eleza getnchannels(self):
        ikiwa sio self._nchannels:
            ashiria Error('number of channels sio set')
        rudisha self._nchannels

    eleza setsampwidth(self, sampwidth):
        ikiwa self._datawritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa sampwidth < 1 ama sampwidth > 4:
            ashiria Error('bad sample width')
        self._sampwidth = sampwidth

    eleza getsampwidth(self):
        ikiwa sio self._sampwidth:
            ashiria Error('sample width sio set')
        rudisha self._sampwidth

    eleza setframerate(self, framerate):
        ikiwa self._datawritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa framerate <= 0:
            ashiria Error('bad frame rate')
        self._framerate = int(round(framerate))

    eleza getframerate(self):
        ikiwa sio self._framerate:
            ashiria Error('frame rate sio set')
        rudisha self._framerate

    eleza setnframes(self, nframes):
        ikiwa self._datawritten:
            ashiria Error('cannot change parameters after starting to write')
        self._nframes = nframes

    eleza getnframes(self):
        rudisha self._nframeswritten

    eleza setcomptype(self, comptype, compname):
        ikiwa self._datawritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa comptype haiko kwenye ('NONE',):
            ashiria Error('unsupported compression type')
        self._comptype = comptype
        self._compname = compname

    eleza getcomptype(self):
        rudisha self._comptype

    eleza getcompname(self):
        rudisha self._compname

    eleza setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        ikiwa self._datawritten:
            ashiria Error('cannot change parameters after starting to write')
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    eleza getparams(self):
        ikiwa sio self._nchannels ama sio self._sampwidth ama sio self._framerate:
            ashiria Error('not all parameters set')
        rudisha _wave_params(self._nchannels, self._sampwidth, self._framerate,
              self._nframes, self._comptype, self._compname)

    eleza setmark(self, id, pos, name):
        ashiria Error('setmark() sio supported')

    eleza getmark(self, id):
        ashiria Error('no marks')

    eleza getmarkers(self):
        rudisha Tupu

    eleza tell(self):
        rudisha self._nframeswritten

    eleza writeframesraw(self, data):
        ikiwa sio isinstance(data, (bytes, bytearray)):
            data = memoryview(data).cast('B')
        self._ensure_header_written(len(data))
        nframes = len(data) // (self._sampwidth * self._nchannels)
        ikiwa self._convert:
            data = self._convert(data)
        ikiwa self._sampwidth != 1 na sys.byteorder == 'big':
            data = audioop.byteswap(data, self._sampwidth)
        self._file.write(data)
        self._datawritten += len(data)
        self._nframeswritten = self._nframeswritten + nframes

    eleza writeframes(self, data):
        self.writeframesraw(data)
        ikiwa self._datalength != self._datawritten:
            self._patchheader()

    eleza close(self):
        jaribu:
            ikiwa self._file:
                self._ensure_header_written(0)
                ikiwa self._datalength != self._datawritten:
                    self._patchheader()
                self._file.flush()
        mwishowe:
            self._file = Tupu
            file = self._i_opened_the_file
            ikiwa file:
                self._i_opened_the_file = Tupu
                file.close()

    #
    # Internal methods.
    #

    eleza _ensure_header_written(self, datasize):
        ikiwa sio self._headerwritten:
            ikiwa sio self._nchannels:
                ashiria Error('# channels sio specified')
            ikiwa sio self._sampwidth:
                ashiria Error('sample width sio specified')
            ikiwa sio self._framerate:
                ashiria Error('sampling rate sio specified')
            self._write_header(datasize)

    eleza _write_header(self, initlength):
        assert sio self._headerwritten
        self._file.write(b'RIFF')
        ikiwa sio self._nframes:
            self._nframes = initlength // (self._nchannels * self._sampwidth)
        self._datalength = self._nframes * self._nchannels * self._sampwidth
        jaribu:
            self._form_length_pos = self._file.tell()
        tatizo (AttributeError, OSError):
            self._form_length_pos = Tupu
        self._file.write(struct.pack('<L4s4sLHHLLHH4s',
            36 + self._datalength, b'WAVE', b'fmt ', 16,
            WAVE_FORMAT_PCM, self._nchannels, self._framerate,
            self._nchannels * self._framerate * self._sampwidth,
            self._nchannels * self._sampwidth,
            self._sampwidth * 8, b'data'))
        ikiwa self._form_length_pos ni sio Tupu:
            self._data_length_pos = self._file.tell()
        self._file.write(struct.pack('<L', self._datalength))
        self._headerwritten = Kweli

    eleza _patchheader(self):
        assert self._headerwritten
        ikiwa self._datawritten == self._datalength:
            rudisha
        curpos = self._file.tell()
        self._file.seek(self._form_length_pos, 0)
        self._file.write(struct.pack('<L', 36 + self._datawritten))
        self._file.seek(self._data_length_pos, 0)
        self._file.write(struct.pack('<L', self._datawritten))
        self._file.seek(curpos, 0)
        self._datalength = self._datawritten

eleza open(f, mode=Tupu):
    ikiwa mode ni Tupu:
        ikiwa hasattr(f, 'mode'):
            mode = f.mode
        isipokua:
            mode = 'rb'
    ikiwa mode kwenye ('r', 'rb'):
        rudisha Wave_read(f)
    lasivyo mode kwenye ('w', 'wb'):
        rudisha Wave_write(f)
    isipokua:
        ashiria Error("mode must be 'r', 'rb', 'w', ama 'wb'")

eleza openfp(f, mode=Tupu):
    warnings.warn("wave.openfp ni deprecated since Python 3.7. "
                  "Use wave.open instead.", DeprecationWarning, stacklevel=2)
    rudisha open(f, mode=mode)
