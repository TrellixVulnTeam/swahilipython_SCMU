agiza os, string

codecs = {
    'cn': ('gb2312', 'gbk', 'gb18030', 'hz'),
    'tw': ('big5', 'cp950'),
    'hk': ('big5hkscs',),
    'jp': ('cp932', 'shift_jis', 'euc_jp', 'euc_jisx0213', 'shift_jisx0213',
           'euc_jis_2004', 'shift_jis_2004'),
    'kr': ('cp949', 'euc_kr', 'johab'),
    'iso2022': ('iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
                'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                'iso2022_kr'),
}

TEMPLATE = string.Template("""\
#
# $encoding.py: Python Unicode Codec kila $ENCODING
#
# Written by Hye-Shik Chang <perky@FreeBSD.org>
#

agiza _codecs_$owner, codecs
agiza _multibytecodec kama mbc

codec = _codecs_$owner.getcodec('$encoding')

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
        name='$encoding',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
""")

eleza gencodecs(prefix):
    kila loc, encodings kwenye codecs.items():
        kila enc kwenye encodings:
            code = TEMPLATE.substitute(ENCODING=enc.upper(),
                                       encoding=enc.lower(),
                                       owner=loc)
            codecpath = os.path.join(prefix, enc + '.py')
            ukijumuisha open(codecpath, 'w') kama f:
                f.write(code)

ikiwa __name__ == '__main__':
    agiza sys
    gencodecs(sys.argv[1])
