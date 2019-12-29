"""Python 'hex_codec' Codec - 2-digit hex content transfer encoding.

This codec de/encodes from bytes to bytes.

Written by Marc-Andre Lemburg (mal@lemburg.com).
"""

agiza codecs
import binascii

### Codec APIs

eleza hex_encode(input, errors='strict'):
    assert errors == 'strict'
    rudisha (binascii.b2a_hex(input), len(input))

eleza hex_decode(input, errors='strict'):
    assert errors == 'strict'
    rudisha (binascii.a2b_hex(input), len(input))

kundi Codec(codecs.Codec):
    eleza encode(self, input, errors='strict'):
        rudisha hex_encode(input, errors)
    eleza decode(self, input, errors='strict'):
        rudisha hex_decode(input, errors)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=Uongo):
        assert self.errors == 'strict'
        rudisha binascii.b2a_hex(input)

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=Uongo):
        assert self.errors == 'strict'
        rudisha binascii.a2b_hex(input)

kundi StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

kundi StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='hex',
        encode=hex_encode,
        decode=hex_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=Uongo,
    )
