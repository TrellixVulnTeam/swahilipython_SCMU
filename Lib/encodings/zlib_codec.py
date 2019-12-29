"""Python 'zlib_codec' Codec - zlib compression encoding.

This codec de/encodes from bytes to bytes.

Written by Marc-Andre Lemburg (mal@lemburg.com).
"""

agiza codecs
import zlib # this codec needs the optional zlib module !

### Codec APIs

eleza zlib_encode(input, errors='strict'):
    assert errors == 'strict'
    rudisha (zlib.compress(input), len(input))

eleza zlib_decode(input, errors='strict'):
    assert errors == 'strict'
    rudisha (zlib.decompress(input), len(input))

kundi Codec(codecs.Codec):
    eleza encode(self, input, errors='strict'):
        rudisha zlib_encode(input, errors)
    eleza decode(self, input, errors='strict'):
        rudisha zlib_decode(input, errors)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.compressobj = zlib.compressobj()

    eleza encode(self, input, final=Uongo):
        if final:
            c = self.compressobj.compress(input)
            rudisha c + self.compressobj.flush()
        isipokua:
            rudisha self.compressobj.compress(input)

    eleza reset(self):
        self.compressobj = zlib.compressobj()

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.decompressobj = zlib.decompressobj()

    eleza decode(self, input, final=Uongo):
        if final:
            c = self.decompressobj.decompress(input)
            rudisha c + self.decompressobj.flush()
        isipokua:
            rudisha self.decompressobj.decompress(input)

    eleza reset(self):
        self.decompressobj = zlib.decompressobj()

kundi StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

kundi StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='zlib',
        encode=zlib_encode,
        decode=zlib_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
        _is_text_encoding=Uongo,
    )
