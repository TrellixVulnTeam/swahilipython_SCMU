"""
Python 'utf-32' Codec
"""
agiza codecs, sys

### Codec APIs

encode = codecs.utf_32_encode

eleza decode(input, errors='strict'):
    rudisha codecs.utf_32_decode(input, errors, Kweli)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza __init__(self, errors='strict'):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.encoder = Tupu

    eleza encode(self, input, final=Uongo):
        ikiwa self.encoder ni Tupu:
            result = codecs.utf_32_encode(input, self.errors)[0]
            ikiwa sys.byteorder == 'little':
                self.encoder = codecs.utf_32_le_encode
            isipokua:
                self.encoder = codecs.utf_32_be_encode
            rudisha result
        rudisha self.encoder(input, self.errors)[0]

    eleza reset(self):
        codecs.IncrementalEncoder.reset(self)
        self.encoder = Tupu

    eleza getstate(self):
        # state info we rudisha to the caller:
        # 0: stream ni kwenye natural order kila this platform
        # 2: endianness hasn't been determined yet
        # (we're never writing kwenye unnatural order)
        rudisha (2 ikiwa self.encoder ni Tupu isipokua 0)

    eleza setstate(self, state):
        ikiwa state:
            self.encoder = Tupu
        isipokua:
            ikiwa sys.byteorder == 'little':
                self.encoder = codecs.utf_32_le_encode
            isipokua:
                self.encoder = codecs.utf_32_be_encode

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    eleza __init__(self, errors='strict'):
        codecs.BufferedIncrementalDecoder.__init__(self, errors)
        self.decoder = Tupu

    eleza _buffer_decode(self, input, errors, final):
        ikiwa self.decoder ni Tupu:
            (output, consumed, byteorder) = \
                codecs.utf_32_ex_decode(input, errors, 0, final)
            ikiwa byteorder == -1:
                self.decoder = codecs.utf_32_le_decode
            lasivyo byteorder == 1:
                self.decoder = codecs.utf_32_be_decode
            lasivyo consumed >= 4:
                ashiria UnicodeError("UTF-32 stream does sio start ukijumuisha BOM")
            rudisha (output, consumed)
        rudisha self.decoder(input, self.errors, final)

    eleza reset(self):
        codecs.BufferedIncrementalDecoder.reset(self)
        self.decoder = Tupu

    eleza getstate(self):
        # additional state info kutoka the base kundi must be Tupu here,
        # kama it isn't pitaed along to the caller
        state = codecs.BufferedIncrementalDecoder.getstate(self)[0]
        # additional state info we pita to the caller:
        # 0: stream ni kwenye natural order kila this platform
        # 1: stream ni kwenye unnatural order
        # 2: endianness hasn't been determined yet
        ikiwa self.decoder ni Tupu:
            rudisha (state, 2)
        addstate = int((sys.byteorder == "big") !=
                       (self.decoder ni codecs.utf_32_be_decode))
        rudisha (state, addstate)

    eleza setstate(self, state):
        # state[1] will be ignored by BufferedIncrementalDecoder.setstate()
        codecs.BufferedIncrementalDecoder.setstate(self, state)
        state = state[1]
        ikiwa state == 0:
            self.decoder = (codecs.utf_32_be_decode
                            ikiwa sys.byteorder == "big"
                            isipokua codecs.utf_32_le_decode)
        lasivyo state == 1:
            self.decoder = (codecs.utf_32_le_decode
                            ikiwa sys.byteorder == "big"
                            isipokua codecs.utf_32_be_decode)
        isipokua:
            self.decoder = Tupu

kundi StreamWriter(codecs.StreamWriter):
    eleza __init__(self, stream, errors='strict'):
        self.encoder = Tupu
        codecs.StreamWriter.__init__(self, stream, errors)

    eleza reset(self):
        codecs.StreamWriter.reset(self)
        self.encoder = Tupu

    eleza encode(self, input, errors='strict'):
        ikiwa self.encoder ni Tupu:
            result = codecs.utf_32_encode(input, errors)
            ikiwa sys.byteorder == 'little':
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
            pita

    eleza decode(self, input, errors='strict'):
        (object, consumed, byteorder) = \
            codecs.utf_32_ex_decode(input, errors, 0, Uongo)
        ikiwa byteorder == -1:
            self.decode = codecs.utf_32_le_decode
        lasivyo byteorder == 1:
            self.decode = codecs.utf_32_be_decode
        lasivyo consumed>=4:
            ashiria UnicodeError("UTF-32 stream does sio start ukijumuisha BOM")
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
