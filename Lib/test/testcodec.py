""" Test Codecs (used by test_charmapcodec)

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright 2000 Guido van Rossum.

"""#"
agiza codecs

### Codec APIs

kundi Codec(codecs.Codec):

    eleza encode(self,input,errors='strict'):

        rudisha codecs.charmap_encode(input,errors,encoding_map)

    eleza decode(self,input,errors='strict'):

        rudisha codecs.charmap_decode(input,errors,decoding_map)

kundi StreamWriter(Codec,codecs.StreamWriter):
    pass

kundi StreamReader(Codec,codecs.StreamReader):
    pass

### encodings module API

eleza getregentry():

    rudisha (Codec().encode,Codec().decode,StreamReader,StreamWriter)

### Decoding Map

decoding_map = codecs.make_identity_dict(range(256))
decoding_map.update({
        0x78: "abc", # 1-n decoding mapping
        b"abc": 0x0078,# 1-n encoding mapping
        0x01: Tupu,   # decoding mapping to <undefined>
        0x79: "",    # decoding mapping to <remove character>
})

### Encoding Map

encoding_map = {}
kila k,v kwenye decoding_map.items():
    encoding_map[v] = k
