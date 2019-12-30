"""Python 'bz2_codec' Codec - bz2 compression encoding.

This codec de/encodes kutoka bytes to bytes na ni therefore usable with
bytes.transform() na bytes.untransform().

Adapted by Raymond Hettinger kutoka zlib_codec.py which was written
by Marc-Andre Lemburg (mal@lemburg.com).
"""

agiza codecs
agiza bz2 # this codec needs the optional bz2 module !

### Codec APIs

eleza bz2_encode(input, errors='strict'):
    assert errors == 'strict'
    rudisha (bz2.compress(input), len(input))

eleza bz2_decode(input, errors='strict'):
    assert errors == 'strict'
    rudisha (bz2.decompress(input), len(input))

kundi Codec(codecs.Codec):
    eleza encode(self, input, errors='strict'):
        rudisha bz2_encode(input, errors)
    eleza decode(self, input, errors='strict'):
        rudisha bz2_decode(input, errors)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.compressobj = bz2.BZ2Compressor()

    eleza encode(self, input, final=Uongo):
        ikiwa final:
            c = self.compressobj.compress(input)
            rudisha c + self.compressobj.flush()
        isipokua:
            rudisha self.compressobj.compress(input)

    eleza reset(self):
        self.compressobj = bz2.BZ2Compressor()

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.decompressobj = bz2.BZ2Decompressor()

    eleza decode(self, input, final=Uongo):
        jaribu:
            rudisha self.decompressobj.decompress(input)
        except EOFError:
            rudisha ''

    eleza reset(self):
        self.decompressobj = bz2.BZ2Decompressor()

kundi StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

kundi StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name="bz2",
        encode=bz2_encode,
        decode=bz2_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=Uongo,
    )
