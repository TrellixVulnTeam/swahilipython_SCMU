"""Codec for quoted-printable encoding.

This codec de/encodes from bytes to bytes.
"""

agiza codecs
import quopri
from io import BytesIO

eleza quopri_encode(input, errors='strict'):
    assert errors == 'strict'
    f = BytesIO(input)
    g = BytesIO()
    quopri.encode(f, g, quotetabs=True)
    rudisha (g.getvalue(), len(input))

eleza quopri_decode(input, errors='strict'):
    assert errors == 'strict'
    f = BytesIO(input)
    g = BytesIO()
    quopri.decode(f, g)
    rudisha (g.getvalue(), len(input))

kundi Codec(codecs.Codec):
    eleza encode(self, input, errors='strict'):
        rudisha quopri_encode(input, errors)
    eleza decode(self, input, errors='strict'):
        rudisha quopri_decode(input, errors)

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=False):
        rudisha quopri_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=False):
        rudisha quopri_decode(input, self.errors)[0]

kundi StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes

kundi StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes

# encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='quopri',
        encode=quopri_encode,
        decode=quopri_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=False,
    )
