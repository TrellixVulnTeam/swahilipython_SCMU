""" Generic Python Character Mapping Codec.

    Use this codec directly rather than through the automatic
    conversion mechanisms supplied by unicode() and .encode().


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""#"

agiza codecs

### Codec APIs

kundi Codec(codecs.Codec):

    # Note: Binding these as C functions will result in the kundi not
    # converting them to methods. This is intended.
    encode = codecs.charmap_encode
    decode = codecs.charmap_decode

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza __init__(self, errors='strict', mapping=Tupu):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.mapping = mapping

    eleza encode(self, input, final=Uongo):
        rudisha codecs.charmap_encode(input, self.errors, self.mapping)[0]

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza __init__(self, errors='strict', mapping=Tupu):
        codecs.IncrementalDecoder.__init__(self, errors)
        self.mapping = mapping

    eleza decode(self, input, final=Uongo):
        rudisha codecs.charmap_decode(input, self.errors, self.mapping)[0]

kundi StreamWriter(Codec,codecs.StreamWriter):

    eleza __init__(self,stream,errors='strict',mapping=Tupu):
        codecs.StreamWriter.__init__(self,stream,errors)
        self.mapping = mapping

    eleza encode(self,input,errors='strict'):
        rudisha Codec.encode(input,errors,self.mapping)

kundi StreamReader(Codec,codecs.StreamReader):

    eleza __init__(self,stream,errors='strict',mapping=Tupu):
        codecs.StreamReader.__init__(self,stream,errors)
        self.mapping = mapping

    eleza decode(self,input,errors='strict'):
        rudisha Codec.decode(input,errors,self.mapping)

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='charmap',
        encode=Codec.encode,
        decode=Codec.decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
