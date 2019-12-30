""" Python 'oem' Codec kila Windows

"""
# Import them explicitly to cause an ImportError
# on non-Windows systems
kutoka codecs agiza oem_encode, oem_decode
# kila IncrementalDecoder, IncrementalEncoder, ...
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
