#
# test_codecmaps_hk.py
#   Codec mapping tests kila HongKong encodings
#

kutoka test agiza multibytecodec_support
agiza unittest

kundi TestBig5HKSCSMap(multibytecodec_support.TestBase_Mapping,
                       unittest.TestCase):
    encoding = 'big5hkscs'
    mapfileurl = 'http://www.pythontest.net/unicode/BIG5HKSCS-2004.TXT'

ikiwa __name__ == "__main__":
    unittest.main()
