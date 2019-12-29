""" Python 'utf-16-le' Codec


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
agiza codecs

### Codec APIs

encode = codecs.utf_16_le_encode

eleza decode(input, errors='strict'):
    rudisha codecs.utf_16_le_decode(input, errors, True)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=False):
        rudisha codecs.utf_16_le_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_16_le_decode

kundi StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_16_le_encode

kundi StreamReader(codecs.StreamReader):
    decode = codecs.utf_16_le_decode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='utf-16-le',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
