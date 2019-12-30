""" Python 'undefined' Codec

    This codec will always ashiria a ValueError exception when being
    used. It ni intended kila use by the site.py file to switch off
    automatic string to Unicode coercion.

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""
agiza codecs

### Codec APIs

kundi Codec(codecs.Codec):

    eleza encode(self,input,errors='strict'):
        ashiria UnicodeError("undefined encoding")

    eleza decode(self,input,errors='strict'):
        ashiria UnicodeError("undefined encoding")

kundi IncrementalEncoder(codecs.IncrementalEncoder):
    eleza encode(self, input, final=Uongo):
        ashiria UnicodeError("undefined encoding")

kundi IncrementalDecoder(codecs.IncrementalDecoder):
    eleza decode(self, input, final=Uongo):
        ashiria UnicodeError("undefined encoding")

kundi StreamWriter(Codec,codecs.StreamWriter):
    pita

kundi StreamReader(Codec,codecs.StreamReader):
    pita

### encodings module API

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='undefined',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
