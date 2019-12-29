"""Python 'base64_codec' Codec - base64 content transfer encoding.

This codec de/encodes from bytes to bytes.

Written by Marc-Andre Lemburg (mal@lemburg.com).
"""

agiza codecs
import base64

### Codec APIs

eleza base64_encode(input, errors='strict'):
    assert errors == 'strict'
    rudisha (base64.encodebytes(input), len(input))

eleza base64_decode(input, errors='strict'):
    assert errors == 'strict'
    rudisha (base64.decodebytes(input), len(input))

kundi Codec(codecs.Codec):
    eleza encode(self, input, errors='strict'):
        rudisha base64_encode(input, errors)
    eleza decode(self, input, errors='strict'):
        rudisha base64_decode(input, errors)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=False):
        assert self.errors == 'strict'
        rudisha base64.encodebytes(input)

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=False):
        assert self.errors == 'strict'
        rudisha base64.decodebytes(input)

kundi StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

kundi StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='base64',
        encode=base64_encode,
        decode=base64_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=False,
    )
