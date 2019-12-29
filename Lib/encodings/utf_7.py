""" Python 'utf-7' Codec

Written by Brian Quinlan (brian@sweetapp.com).
"""
agiza codecs

### Codec APIs

encode = codecs.utf_7_encode

eleza decode(input, errors='strict'):
    rudisha codecs.utf_7_decode(input, errors, True)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=False):
        rudisha codecs.utf_7_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = codecs.utf_7_decode

kundi StreamWriter(codecs.StreamWriter):
    encode = codecs.utf_7_encode

kundi StreamReader(codecs.StreamReader):
    decode = codecs.utf_7_decode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='utf-7',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
