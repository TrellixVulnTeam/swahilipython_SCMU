"""
Python 'utf-32-le' Codec
"""
agiza codecs

### Codec APIs

encode = codecs.utf_32_le_encode

eleza decode(input, errors='strict'):
    rudisha codecs.utf_32_le_decode(input, errors, Kweli)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=Uongo):
        rudisha codecs.utf_32_le_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_32_le_decode

kundi StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_32_le_encode

kundi StreamReader(codecs.StreamReader):
    decode = codecs.utf_32_le_decode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='utf-32-le',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
