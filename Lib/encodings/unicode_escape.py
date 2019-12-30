""" Python 'unicode-escape' Codec


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
agiza codecs

### Codec APIs

kundi Codec(codecs.Codec):

    # Note: Binding these kama C functions will result kwenye the kundi sio
    # converting them to methods. This ni intended.
    encode = codecs.unicode_escape_encode
    decode = codecs.unicode_escape_decode

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=Uongo):
        rudisha codecs.unicode_escape_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=Uongo):
        rudisha codecs.unicode_escape_decode(input, self.errors)[0]

kundi StreamWriter(Codec,codecs.StreamWriter):
    pita

kundi StreamReader(Codec,codecs.StreamReader):
    pita

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='unicode-escape',
        encode=Codec.encode,
        decode=Codec.decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
