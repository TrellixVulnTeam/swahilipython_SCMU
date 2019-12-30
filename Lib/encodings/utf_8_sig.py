""" Python 'utf-8-sig' Codec
This work similar to UTF-8 ukijumuisha the following changes:

* On encoding/writing a UTF-8 encoded BOM will be prepended/written kama the
  first three bytes.

* On decoding/reading ikiwa the first three bytes are a UTF-8 encoded BOM, these
  bytes will be skipped.
"""
agiza codecs

### Codec APIs

eleza encode(input, errors='strict'):
    rudisha (codecs.BOM_UTF8 + codecs.utf_8_encode(input, errors)[0],
            len(input))

eleza decode(input, errors='strict'):
    prefix = 0
    ikiwa input[:3] == codecs.BOM_UTF8:
        input = input[3:]
        prefix = 3
    (output, consumed) = codecs.utf_8_decode(input, errors, Kweli)
    rudisha (output, consumed+prefix)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza __init__(self, errors='strict'):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.first = 1

    eleza encode(self, input, final=Uongo):
        ikiwa self.first:
            self.first = 0
            rudisha codecs.BOM_UTF8 + \
                   codecs.utf_8_encode(input, self.errors)[0]
        isipokua:
            rudisha codecs.utf_8_encode(input, self.errors)[0]

    eleza reset(self):
        codecs.IncrementalEncoder.reset(self)
        self.first = 1

    eleza getstate(self):
        rudisha self.first

    eleza setstate(self, state):
        self.first = state

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    eleza __init__(self, errors='strict'):
        codecs.BufferedIncrementalDecoder.__init__(self, errors)
        self.first = 1

    eleza _buffer_decode(self, input, errors, final):
        ikiwa self.first:
            ikiwa len(input) < 3:
                ikiwa codecs.BOM_UTF8.startswith(input):
                    # sio enough data to decide ikiwa this really ni a BOM
                    # => try again on the next call
                    rudisha ("", 0)
                isipokua:
                    self.first = 0
            isipokua:
                self.first = 0
                ikiwa input[:3] == codecs.BOM_UTF8:
                    (output, consumed) = \
                       codecs.utf_8_decode(input[3:], errors, final)
                    rudisha (output, consumed+3)
        rudisha codecs.utf_8_decode(input, errors, final)

    eleza reset(self):
        codecs.BufferedIncrementalDecoder.reset(self)
        self.first = 1

    eleza getstate(self):
        state = codecs.BufferedIncrementalDecoder.getstate(self)
        # state[1] must be 0 here, kama it isn't pitaed along to the caller
        rudisha (state[0], self.first)

    eleza setstate(self, state):
        # state[1] will be ignored by BufferedIncrementalDecoder.setstate()
        codecs.BufferedIncrementalDecoder.setstate(self, state)
        self.first = state[1]

kundi StreamWriter(codecs.StreamWriter):
    eleza reset(self):
        codecs.StreamWriter.reset(self)
        jaribu:
            toa self.encode
        tatizo AttributeError:
            pita

    eleza encode(self, input, errors='strict'):
        self.encode = codecs.utf_8_encode
        rudisha encode(input, errors)

kundi StreamReader(codecs.StreamReader):
    eleza reset(self):
        codecs.StreamReader.reset(self)
        jaribu:
            toa self.decode
        tatizo AttributeError:
            pita

    eleza decode(self, input, errors='strict'):
        ikiwa len(input) < 3:
            ikiwa codecs.BOM_UTF8.startswith(input):
                # sio enough data to decide ikiwa this ni a BOM
                # => try again on the next call
                rudisha ("", 0)
        lasivyo input[:3] == codecs.BOM_UTF8:
            self.decode = codecs.utf_8_decode
            (output, consumed) = codecs.utf_8_decode(input[3:],errors)
            rudisha (output, consumed+3)
        # (else) no BOM present
        self.decode = codecs.utf_8_decode
        rudisha codecs.utf_8_decode(input, errors)

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='utf-8-sig',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
