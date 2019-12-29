""" Python 'oem' Codec for Windows

"""
# Import them explicitly to cause an ImportError
# on non-Windows systems
from codecs import oem_encode, oem_decode
# for IncrementalDecoder, IncrementalEncoder, ...
agiza codecs

### Codec APIs

encode = oem_encode

eleza decode(input, errors='strict'):
    rudisha oem_decode(input, errors, Kweli)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=Uongo):
        rudisha oem_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = oem_decode

kundi StreamWriter(codecs.StreamWriter):
    encode = oem_encode

kundi StreamReader(codecs.StreamReader):
    decode = oem_decode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='oem',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
