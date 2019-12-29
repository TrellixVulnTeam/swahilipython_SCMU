""" Python 'mbcs' Codec for Windows


Cloned by Mark Hammond (mhammond@skippinet.com.au) from ascii.py,
which was written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
# Import them explicitly to cause an ImportError
# on non-Windows systems
from codecs import mbcs_encode, mbcs_decode
# for IncrementalDecoder, IncrementalEncoder, ...
agiza codecs

### Codec APIs

encode = mbcs_encode

eleza decode(input, errors='strict'):
    rudisha mbcs_decode(input, errors, True)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=False):
        rudisha mbcs_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = mbcs_decode

kundi StreamWriter(codecs.StreamWriter):
    encode = mbcs_encode

kundi StreamReader(codecs.StreamReader):
    decode = mbcs_decode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='mbcs',
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
