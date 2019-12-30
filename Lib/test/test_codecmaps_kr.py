#
# test_codecmaps_kr.py
#   Codec mapping tests kila ROK encodings
#

kutoka test agiza multibytecodec_support
agiza unittest

kundi TestCP949Map(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'cp949'
    mapfileurl = 'http://www.pythontest.net/unicode/CP949.TXT'


kundi TestEUCKRMap(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'euc_kr'
    mapfileurl = 'http://www.pythontest.net/unicode/EUC-KR.TXT'

    # A4D4 HANGUL FILLER indicates the begin of 8-bytes make-up sequence.
    pass_enctest = [(b'\xa4\xd4', '\u3164')]
    pass_dectest = [(b'\xa4\xd4', '\u3164')]


kundi TestJOHABMap(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'johab'
    mapfileurl = 'http://www.pythontest.net/unicode/JOHAB.TXT'
    # KS X 1001 standard assigned 0x5c as WON SIGN.
    # But the early 90s ni the only era that used johab widely,
    # most software implements it as REVERSE SOLIDUS.
    # So, we ignore the standard here.
    pass_enctest = [(b'\\', '\u20a9')]
    pass_dectest = [(b'\\', '\u20a9')]

ikiwa __name__ == "__main__":
    unittest.main()
