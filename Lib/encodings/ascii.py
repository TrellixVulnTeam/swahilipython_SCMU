""" Python 'ascii' Codec


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
agiza codecs

### Codec APIs

kundi Codec(codecs.Codec):

    # Note: Binding these as C functions will result in the kundi not
    # converting them to methods. This is intended.
    encode = codecs.ascii_encode
    decode = codecs.ascii_decode

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=False):
        rudisha codecs.ascii_encode(input, self.errors)[0]

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=False):
        rudisha codecs.ascii_decode(input, self.errors)[0]

kundi StreamWriter(Codec,codecs.StreamWriter):
    pass

kundi StreamReader(Codec,codecs.StreamReader):
    pass

kundi StreamConverter(StreamWriter,StreamReader):

    encode = codecs.ascii_decode
    decode = codecs.ascii_encode

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='ascii',
        encode=Codec.encode,
        decode=Codec.decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
