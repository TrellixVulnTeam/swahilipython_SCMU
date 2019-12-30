"""Stuff to parse Sun na NeXT audio files.

An audio file consists of a header followed by the data.  The structure
of the header ni kama follows.

        +---------------+
        | magic word    |
        +---------------+
        | header size   |
        +---------------+
        | data size     |
        +---------------+
        | encoding      |
        +---------------+
        | sample rate   |
        +---------------+
        | # of channels |
        +---------------+
        | info          |
        |               |
        +---------------+

The magic word consists of the 4 characters '.snd'.  Apart kutoka the
info field, all header fields are 4 bytes kwenye size.  They are all
32-bit unsigned integers encoded kwenye big-endian byte order.

The header size really gives the start of the data.
The data size ni the physical size of the data.  From the other
parameters the number of frames can be calculated.
The encoding gives the way kwenye which audio samples are encoded.
Possible values are listed below.
The info field currently consists of an ASCII string giving a
human-readable description of the audio file.  The info field is
padded ukijumuisha NUL bytes to the header size.

Usage.

Reading audio files:
        f = sunau.open(file, 'r')
where file ni either the name of a file ama an open file pointer.
The open file pointer must have methods read(), seek(), na close().
When the setpos() na rewind() methods are sio used, the seek()
method ni sio  necessary.

This returns an instance of a kundi ukijumuisha the following public methods:
        getnchannels()  -- returns number of audio channels (1 for
                           mono, 2 kila stereo)
        getsampwidth()  -- returns sample width kwenye bytes
        getframerate()  -- returns sampling frequency
        getnframes()    -- returns number of audio frames
        getcomptype()   -- returns compression type ('NONE' ama 'ULAW')
        getcompname()   -- returns human-readable version of
                           compression type ('not compressed' matches 'NONE')
        getparams()     -- returns a namedtuple consisting of all of the
                           above kwenye the above order
        getmarkers()    -- returns Tupu (kila compatibility ukijumuisha the
                           aifc module)
        getmark(id)     -- raises an error since the mark does not
                           exist (kila compatibility ukijumuisha the aifc module)
        readframes(n)   -- returns at most n frames of audio
        rewind()        -- rewind to the beginning of the audio stream
        setpos(pos)     -- seek to the specified position
        tell()          -- rudisha the current position
        close()         -- close the instance (make it unusable)
The position returned by tell() na the position given to setpos()
are compatible na have nothing to do ukijumuisha the actual position kwenye the
file.
The close() method ni called automatically when the kundi instance
is destroyed.

Writing audio files:
        f = sunau.open(file, 'w')
where file ni either the name of a file ama an open file pointer.
The open file pointer must have methods write(), tell(), seek(), na
close().

This returns an instance of a kundi ukijumuisha the following public methods:
        setnchannels(n) -- set the number of channels
        setsampwidth(n) -- set the sample width
        setframerate(n) -- set the frame rate
        setnframes(n)   -- set the number of frames
        setcomptype(type, name)
                        -- set the compression type na the
                           human-readable compression type
        setparams(tuple)-- set all parameters at once
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

kutoka collections agiza namedtuple
agiza warnings

_sunau_params = namedtuple('_sunau_params',
                           'nchannels sampwidth framerate nframes comptype compname')

# kutoka <multimedia/audio_filehdr.h>
AUDIO_FILE_MAGIC = 0x2e736e64
AUDIO_FILE_ENCODING_MULAW_8 = 1
AUDIO_FILE_ENCODING_LINEAR_8 = 2
AUDIO_FILE_ENCODING_LINEAR_16 = 3
AUDIO_FILE_ENCODING_LINEAR_24 = 4
AUDIO_FILE_ENCODING_LINEAR_32 = 5
AUDIO_FILE_ENCODING_FLOAT = 6
AUDIO_FILE_ENCODING_DOUBLE = 7
AUDIO_FILE_ENCODING_ADPCM_G721 = 23
AUDIO_FILE_ENCODING_ADPCM_G722 = 24
AUDIO_FILE_ENCODING_ADPCM_G723_3 = 25
AUDIO_FILE_ENCODING_ADPCM_G723_5 = 26
AUDIO_FILE_ENCODING_ALAW_8 = 27

# kutoka <multimedia/audio_hdr.h>
AUDIO_UNKNOWN_SIZE = 0xFFFFFFFF        # ((unsigned)(~0))

_simple_encodings = [AUDIO_FILE_ENCODING_MULAW_8,
                     AUDIO_FILE_ENCODING_LINEAR_8,
                     AUDIO_FILE_ENCODING_LINEAR_16,
                     AUDIO_FILE_ENCODING_LINEAR_24,
                     AUDIO_FILE_ENCODING_LINEAR_32,
                     AUDIO_FILE_ENCODING_ALAW_8]

kundi Error(Exception):
    pita

eleza _read_u32(file):
    x = 0
    kila i kwenye range(4):
        byte = file.read(1)
        ikiwa sio byte:
            ashiria EOFError
        x = x*256 + ord(byte)
    rudisha x

eleza _write_u32(file, x):
    data = []
    kila i kwenye range(4):
        d, m = divmod(x, 256)
        data.insert(0, int(m))
        x = d
    file.write(bytes(data))

kundi Au_read:

    eleza __init__(self, f):
        ikiwa type(f) == type(''):
            agiza builtins
            f = builtins.open(f, 'rb')
            self._opened = Kweli
        isipokua:
            self._opened = Uongo
        self.initfp(f)

    eleza __del__(self):
        ikiwa self._file:
            self.close()

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.close()

    eleza initfp(self, file):
        self._file = file
        self._soundpos = 0
        magic = int(_read_u32(file))
        ikiwa magic != AUDIO_FILE_MAGIC:
            ashiria Error('bad magic number')
        self._hdr_size = int(_read_u32(file))
        ikiwa self._hdr_size < 24:
            ashiria Error('header size too small')
        ikiwa self._hdr_size > 100:
            ashiria Error('header size ridiculously large')
        self._data_size = _read_u32(file)
        ikiwa self._data_size != AUDIO_UNKNOWN_SIZE:
            self._data_size = int(self._data_size)
        self._encoding = int(_read_u32(file))
        ikiwa self._encoding haiko kwenye _simple_encodings:
            ashiria Error('encoding sio (yet) supported')
        ikiwa self._encoding kwenye (AUDIO_FILE_ENCODING_MULAW_8,
                  AUDIO_FILE_ENCODING_ALAW_8):
            self._sampwidth = 2
            self._framesize = 1
        lasivyo self._encoding == AUDIO_FILE_ENCODING_LINEAR_8:
            self._framesize = self._sampwidth = 1
        lasivyo self._encoding == AUDIO_FILE_ENCODING_LINEAR_16:
            self._framesize = self._sampwidth = 2
        lasivyo self._encoding == AUDIO_FILE_ENCODING_LINEAR_24:
            self._framesize = self._sampwidth = 3
        lasivyo self._encoding == AUDIO_FILE_ENCODING_LINEAR_32:
            self._framesize = self._sampwidth = 4
        isipokua:
            ashiria Error('unknown encoding')
        self._framerate = int(_read_u32(file))
        self._nchannels = int(_read_u32(file))
        ikiwa sio self._nchannels:
            ashiria Error('bad # of channels')
        self._framesize = self._framesize * self._nchannels
        ikiwa self._hdr_size > 24:
            self._info = file.read(self._hdr_size - 24)
            self._info, _, _ = self._info.partition(b'\0')
        isipokua:
            self._info = b''
        jaribu:
            self._data_pos = file.tell()
        tatizo (AttributeError, OSError):
            self._data_pos = Tupu

    eleza getfp(self):
        rudisha self._file

    eleza getnchannels(self):
        rudisha self._nchannels

    eleza getsampwidth(self):
        rudisha self._sampwidth

    eleza getframerate(self):
        rudisha self._framerate

    eleza getnframes(self):
        ikiwa self._data_size == AUDIO_UNKNOWN_SIZE:
            rudisha AUDIO_UNKNOWN_SIZE
        ikiwa self._encoding kwenye _simple_encodings:
            rudisha self._data_size // self._framesize
        rudisha 0                # XXX--must do some arithmetic here

    eleza getcomptype(self):
        ikiwa self._encoding == AUDIO_FILE_ENCODING_MULAW_8:
            rudisha 'ULAW'
        lasivyo self._encoding == AUDIO_FILE_ENCODING_ALAW_8:
            rudisha 'ALAW'
        isipokua:
            rudisha 'NONE'

    eleza getcompname(self):
        ikiwa self._encoding == AUDIO_FILE_ENCODING_MULAW_8:
            rudisha 'CCITT G.711 u-law'
        lasivyo self._encoding == AUDIO_FILE_ENCODING_ALAW_8:
            rudisha 'CCITT G.711 A-law'
        isipokua:
            rudisha 'not compressed'

    eleza getparams(self):
        rudisha _sunau_params(self.getnchannels(), self.getsampwidth(),
                  self.getframerate(), self.getnframes(),
                  self.getcomptype(), self.getcompname())

    eleza getmarkers(self):
        rudisha Tupu

    eleza getmark(self, id):
        ashiria Error('no marks')

    eleza readframes(self, nframes):
        ikiwa self._encoding kwenye _simple_encodings:
            ikiwa nframes == AUDIO_UNKNOWN_SIZE:
                data = self._file.read()
            isipokua:
                data = self._file.read(nframes * self._framesize)
            self._soundpos += len(data) // self._framesize
            ikiwa self._encoding == AUDIO_FILE_ENCODING_MULAW_8:
                agiza audioop
                data = audioop.ulaw2lin(data, self._sampwidth)
            rudisha data
        rudisha Tupu             # XXX--not implemented yet

    eleza rewind(self):
        ikiwa self._data_pos ni Tupu:
            ashiria OSError('cannot seek')
        self._file.seek(self._data_pos)
        self._soundpos = 0

    eleza tell(self):
        rudisha self._soundpos

    eleza setpos(self, pos):
        ikiwa pos < 0 ama pos > self.getnframes():
            ashiria Error('position haiko kwenye range')
        ikiwa self._data_pos ni Tupu:
            ashiria OSError('cannot seek')
        self._file.seek(self._data_pos + pos * self._framesize)
        self._soundpos = pos

    eleza close(self):
        file = self._file
        ikiwa file:
            self._file = Tupu
            ikiwa self._opened:
                file.close()

kundi Au_write:

    eleza __init__(self, f):
        ikiwa type(f) == type(''):
            agiza builtins
            f = builtins.open(f, 'wb')
            self._opened = Kweli
        isipokua:
            self._opened = Uongo
        self.initfp(f)

    eleza __del__(self):
        ikiwa self._file:
            self.close()
        self._file = Tupu

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.close()

    eleza initfp(self, file):
        self._file = file
        self._framerate = 0
        self._nchannels = 0
        self._sampwidth = 0
        self._framesize = 0
        self._nframes = AUDIO_UNKNOWN_SIZE
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._info = b''
        self._comptype = 'ULAW' # default ni U-law

    eleza setnchannels(self, nchannels):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa nchannels haiko kwenye (1, 2, 4):
            ashiria Error('only 1, 2, ama 4 channels supported')
        self._nchannels = nchannels

    eleza getnchannels(self):
        ikiwa sio self._nchannels:
            ashiria Error('number of channels sio set')
        rudisha self._nchannels

    eleza setsampwidth(self, sampwidth):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa sampwidth haiko kwenye (1, 2, 3, 4):
            ashiria Error('bad sample width')
        self._sampwidth = sampwidth

    eleza getsampwidth(self):
        ikiwa sio self._framerate:
            ashiria Error('sample width sio specified')
        rudisha self._sampwidth

    eleza setframerate(self, framerate):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        self._framerate = framerate

    eleza getframerate(self):
        ikiwa sio self._framerate:
            ashiria Error('frame rate sio set')
        rudisha self._framerate

    eleza setnframes(self, nframes):
        ikiwa self._nframeswritten:
            ashiria Error('cannot change parameters after starting to write')
        ikiwa nframes < 0:
            ashiria Error('# of frames cannot be negative')
        self._nframes = nframes

    eleza getnframes(self):
        rudisha self._nframeswritten

    eleza setcomptype(self, type, name):
        ikiwa type kwenye ('NONE', 'ULAW'):
            self._comptype = type
        isipokua:
            ashiria Error('unknown compression type')

    eleza getcomptype(self):
        rudisha self._comptype

    eleza getcompname(self):
        ikiwa self._comptype == 'ULAW':
            rudisha 'CCITT G.711 u-law'
        lasivyo self._comptype == 'ALAW':
            rudisha 'CCITT G.711 A-law'
        isipokua:
            rudisha 'not compressed'

    eleza setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    eleza getparams(self):
        rudisha _sunau_params(self.getnchannels(), self.getsampwidth(),
                  self.getframerate(), self.getnframes(),
                  self.getcomptype(), self.getcompname())

    eleza tell(self):
        rudisha self._nframeswritten

    eleza writeframesraw(self, data):
        ikiwa sio isinstance(data, (bytes, bytearray)):
            data = memoryview(data).cast('B')
        self._ensure_header_written()
        ikiwa self._comptype == 'ULAW':
            agiza audioop
            data = audioop.lin2ulaw(data, self._sampwidth)
        nframes = len(data) // self._framesize
        self._file.write(data)
        self._nframeswritten = self._nframeswritten + nframes
        self._datawritten = self._datawritten + len(data)

    eleza writeframes(self, data):
        self.writeframesraw(data)
        ikiwa self._nframeswritten != self._nframes ama \
                  self._datalength != self._datawritten:
            self._patchheader()

    eleza close(self):
        ikiwa self._file:
            jaribu:
                self._ensure_header_written()
                ikiwa self._nframeswritten != self._nframes ama \
                        self._datalength != self._datawritten:
                    self._patchheader()
                self._file.flush()
            mwishowe:
                file = self._file
                self._file = Tupu
                ikiwa self._opened:
                    file.close()

    #
    # private methods
    #

    eleza _ensure_header_written(self):
        ikiwa sio self._nframeswritten:
            ikiwa sio self._nchannels:
                ashiria Error('# of channels sio specified')
            ikiwa sio self._sampwidth:
                ashiria Error('sample width sio specified')
            ikiwa sio self._framerate:
                ashiria Error('frame rate sio specified')
            self._write_header()

    eleza _write_header(self):
        ikiwa self._comptype == 'NONE':
            ikiwa self._sampwidth == 1:
                encoding = AUDIO_FILE_ENCODING_LINEAR_8
                self._framesize = 1
            lasivyo self._sampwidth == 2:
                encoding = AUDIO_FILE_ENCODING_LINEAR_16
                self._framesize = 2
            lasivyo self._sampwidth == 3:
                encoding = AUDIO_FILE_ENCODING_LINEAR_24
                self._framesize = 3
            lasivyo self._sampwidth == 4:
                encoding = AUDIO_FILE_ENCODING_LINEAR_32
                self._framesize = 4
            isipokua:
                ashiria Error('internal error')
        lasivyo self._comptype == 'ULAW':
            encoding = AUDIO_FILE_ENCODING_MULAW_8
            self._framesize = 1
        isipokua:
            ashiria Error('internal error')
        self._framesize = self._framesize * self._nchannels
        _write_u32(self._file, AUDIO_FILE_MAGIC)
        header_size = 25 + len(self._info)
        header_size = (header_size + 7) & ~7
        _write_u32(self._file, header_size)
        ikiwa self._nframes == AUDIO_UNKNOWN_SIZE:
            length = AUDIO_UNKNOWN_SIZE
        isipokua:
            length = self._nframes * self._framesize
        jaribu:
            self._form_length_pos = self._file.tell()
        tatizo (AttributeError, OSError):
            self._form_length_pos = Tupu
        _write_u32(self._file, length)
        self._datalength = length
        _write_u32(self._file, encoding)
        _write_u32(self._file, self._framerate)
        _write_u32(self._file, self._nchannels)
        self._file.write(self._info)
        self._file.write(b'\0'*(header_size - len(self._info) - 24))

    eleza _patchheader(self):
        ikiwa self._form_length_pos ni Tupu:
            ashiria OSError('cannot seek')
        self._file.seek(self._form_length_pos)
        _write_u32(self._file, self._datawritten)
        self._datalength = self._datawritten
        self._file.seek(0, 2)

eleza open(f, mode=Tupu):
    ikiwa mode ni Tupu:
        ikiwa hasattr(f, 'mode'):
            mode = f.mode
        isipokua:
            mode = 'rb'
    ikiwa mode kwenye ('r', 'rb'):
        rudisha Au_read(f)
    lasivyo mode kwenye ('w', 'wb'):
        rudisha Au_write(f)
    isipokua:
        ashiria Error("mode must be 'r', 'rb', 'w', ama 'wb'")

eleza openfp(f, mode=Tupu):
    warnings.warn("sunau.openfp ni deprecated since Python 3.7. "
                  "Use sunau.open instead.", DeprecationWarning, stacklevel=2)
    rudisha open(f, mode=mode)
