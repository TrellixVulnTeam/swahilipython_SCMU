"""
Python 'utf-32' Codec
"""
agiza codecs, sys

### Codec APIs

encode = codecs.utf_32_encode

eleza decode(input, errors='strict'):
    rudisha codecs.utf_32_decode(input, errors, True)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza __init__(self, errors='strict'):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.encoder = None

    eleza encode(self, input, final=False):
        if self.encoder is None:
            result = codecs.utf_32_encode(input, self.errors)[0]
            if sys.byteorder == 'little':
                self.encoder = codecs.utf_32_le_encode
            isipokua:
                self.encoder = codecs.utf_32_be_encode
            rudisha result
        rudisha self.encoder(input, self.errors)[0]

    eleza reset(self):
        codecs.IncrementalEncoder.reset(self)
        self.encoder = None

    eleza getstate(self):
        # state info we rudisha to the caller:
        # 0: stream is in natural order for this platform
        # 2: endianness hasn't been determined yet
        # (we're never writing in unnatural order)
        rudisha (2 if self.encoder is None else 0)

    eleza setstate(self, state):
        if state:
            self.encoder = None
        isipokua:
            if sys.byteorder == 'little':
                self.encoder = codecs.utf_32_le_encode
            isipokua:
                self.encoder = codecs.utf_32_be_encode

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    eleza __init__(self, errors='strict'):
        codecs.BufferedIncrementalDecoder.__init__(self, errors)
        self.decoder = None

    eleza _buffer_decode(self, input, errors, final):
        if self.decoder is None:
            (output, consumed, byteorder) = \
                codecs.utf_32_ex_decode(input, errors, 0, final)
            if byteorder == -1:
                self.decoder = codecs.utf_32_le_decode
            lasivyo byteorder == 1:
                self.decoder = codecs.utf_32_be_decode
            lasivyo consumed >= 4:
                raise UnicodeError("UTF-32 stream does sio start with BOM")
            rudisha (output, consumed)
        rudisha self.decoder(input, self.errors, final)

    eleza reset(self):
        codecs.BufferedIncrementalDecoder.reset(self)
        self.decoder = None

    eleza getstate(self):
        # additional state info from the base kundi must be None here,
        # as it isn't passed along to the caller
        state = codecs.BufferedIncrementalDecoder.getstate(self)[0]
        # additional state info we pass to the caller:
        # 0: stream is in natural order for this platform
        # 1: stream is in unnatural order
        # 2: endianness hasn't been determined yet
        if self.decoder is None:
            rudisha (state, 2)
        addstate = int((sys.byteorder == "big") !=
                       (self.decoder is codecs.utf_32_be_decode))
        rudisha (state, addstate)

    eleza setstate(self, state):
        # state[1] will be ignored by BufferedIncrementalDecoder.setstate()
        codecs.BufferedIncrementalDecoder.setstate(self, state)
        state = state[1]
        if state == 0:
            self.decoder = (codecs.utf_32_be_decode
                            if sys.byteorder == "big"
                            else codecs.utf_32_le_decode)
        lasivyo state == 1:
            self.decoder = (codecs.utf_32_le_decode
                            if sys.byteorder == "big"
                            else codecs.utf_32_be_decode)
        isipokua:
            self.decoder = None

kundi StreamWriter(codecs.StreamWriter):
    eleza __init__(self, stream, errors='strict'):
        self.encoder = None
        codecs.StreamWriter.__init__(self, stream, errors)

    eleza reset(self):
        codecs.StreamWriter.reset(self)
        self.encoder = None

    eleza encode(self, input, errors='strict'):
        if self.encoder is None:
            result = codecs.utf_32_encode(input, errors)
            if sys.byteorder == 'little':
                self.encoder = codecs.utf_32_le_encode
            isipokua:
                self.encoder = codecs.utf_32_be_encode
            rudisha result
        isipokua:
            rudisha self.encoder(input, errors)

kundi StreamReader(codecs.StreamReader):

    eleza reset(self):
        codecs.StreamReader.reset(self)
        jaribu:
            toa self.decode
        tatizo AttributeError:
            pass

    eleza decode(self, input, errors='strict'):
        (object, consumed, byteorder) = \
            codecs.utf_32_ex_decode(input, errors, 0, False)
        if byteorder == -1:
            self.decode = codecs.utf_32_le_decode
        lasivyo byteorder == 1:
            self.decode = codecs.utf_32_be_decode
        lasivyo consumed>=4:
            raise UnicodeError("UTF-32 stream does sio start with BOM")
        rudisha (object, consumed)

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='utf-32',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
