"""
Python 'utf-32-be' Codec
"""
agiza codecs

### Codec APIs

encode = codecs.utf_32_be_encode

eleza decode(input, errors='strict'):
    rudisha codecs.utf_32_be_decode(input, errors, True)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=False):
        rudisha codecs.utf_32_be_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_32_be_decode

kundi StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_32_be_encode

kundi StreamReader(codecs.StreamReader):
    decode = codecs.utf_32_be_decode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='utf-32-be',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
