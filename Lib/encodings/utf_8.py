""" Python 'utf-8' Codec


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
agiza codecs

### Codec APIs

encode = codecs.utf_8_encode

eleza decode(input, errors='strict'):
    rudisha codecs.utf_8_decode(input, errors, True)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=False):
        rudisha codecs.utf_8_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_8_decode

kundi StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_8_encode

kundi StreamReader(codecs.StreamReader):
    decode = codecs.utf_8_decode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='utf-8',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
