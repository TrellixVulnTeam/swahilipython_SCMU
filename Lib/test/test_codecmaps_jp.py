#
# test_codecmaps_jp.py
#   Codec mapping tests kila Japanese encodings
#

kutoka test agiza multibytecodec_support
agiza unittest

kundi TestCP932Map(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'cp932'
    mapfileurl = 'http://www.pythontest.net/unicode/CP932.TXT'
    supmaps = [
        (b'\x80', '\u0080'),
        (b'\xa0', '\uf8f0'),
        (b'\xfd', '\uf8f1'),
        (b'\xfe', '\uf8f2'),
        (b'\xff', '\uf8f3'),
    ]
    kila i kwenye range(0xa1, 0xe0):
        supmaps.append((bytes([i]), chr(i+0xfec0)))


kundi TestEUCJPCOMPATMap(multibytecodec_support.TestBase_Mapping,
                         unittest.TestCase):
    encoding = 'euc_jp'
    mapfilename = 'EUC-JP.TXT'
    mapfileurl = 'http://www.pythontest.net/unicode/EUC-JP.TXT'


kundi TestSJISCOMPATMap(multibytecodec_support.TestBase_Mapping,
                        unittest.TestCase):
    encoding = 'shift_jis'
    mapfilename = 'SHIFTJIS.TXT'
    mapfileurl = 'http://www.pythontest.net/unicode/SHIFTJIS.TXT'
    pita_enctest = [
        (b'\x81_', '\\'),
    ]
    pita_dectest = [
        (b'\\', '\xa5'),
        (b'~', '\u203e'),
        (b'\x81_', '\\'),
    ]

kundi TestEUCJISX0213Map(multibytecodec_support.TestBase_Mapping,
                         unittest.TestCase):
    encoding = 'euc_jisx0213'
    mapfilename = 'EUC-JISX0213.TXT'
    mapfileurl = 'http://www.pythontest.net/unicode/EUC-JISX0213.TXT'


kundi TestSJISX0213Map(multibytecodec_support.TestBase_Mapping,
                       unittest.TestCase):
    encoding = 'shift_jisx0213'
    mapfilename = 'SHIFT_JISX0213.TXT'
    mapfileurl = 'http://www.pythontest.net/unicode/SHIFT_JISX0213.TXT'


ikiwa __name__ == "__main__":
    unittest.main()
