#
# gb18030.py: Python Unicode Codec kila GB18030
#
# Written by Hye-Shik Chang <perky@FreeBSD.org>
#

agiza _codecs_cn, codecs
agiza _multibytecodec as mbc

codec = _codecs_cn.getcodec('gb18030')

kundi Codec(codecs.Codec):
    encode = codec.encode
    decode = codec.decode

kundi IncrementalEncoder(mbc.MultibyteIncrementalEncoder,
                         codecs.IncrementalEncoder):
    codec = codec

kundi IncrementalDecoder(mbc.MultibyteIncrementalDecoder,
                         codecs.IncrementalDecoder):
    codec = codec

kundi StreamReader(Codec, mbc.MultibyteStreamReader, codecs.StreamReader):
    codec = codec

kundi StreamWriter(Codec, mbc.MultibyteStreamWriter, codecs.StreamWriter):
    codec = codec

eleza getregentry():
    rudisha codecs.CodecInfo(
        name='gb18030',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
