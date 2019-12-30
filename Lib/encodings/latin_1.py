""" Python 'latin-1' Codec


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
agiza codecs

### Codec APIs

kundi Codec(codecs.Codec):

    # Note: Binding these kama C functions will result kwenye the kundi not
    # converting them to methods. This ni intended.
    encode = codecs.latin_1_encode
    decode = codecs.latin_1_decode

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=Uongo):
        rudisha codecs.latin_1_encode(input,self.errors)[0]

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=Uongo):
        rudisha codecs.latin_1_decode(input,self.errors)[0]

kundi StreamWriter(Codec,codecs.StreamWriter):
    pita

kundi StreamReader(Codec,codecs.StreamReader):
    pita

kundi StreamConverter(StreamWriter,StreamReader):

    encode = codecs.latin_1_decode
    decode = codecs.latin_1_encode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='iso8859-1',
        encode=Codec.encode,
        decode=Codec.decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
