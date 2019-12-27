#
# test_codecmaps_cn.py
#   Codec mapping tests for PRC encodings
#

kutoka test agiza multibytecodec_support
agiza unittest

kundi TestGB2312Map(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'gb2312'
    mapfileurl = 'http://www.pythontest.net/unicode/EUC-CN.TXT'

kundi TestGBKMap(multibytecodec_support.TestBase_Mapping,
                   unittest.TestCase):
    encoding = 'gbk'
    mapfileurl = 'http://www.pythontest.net/unicode/CP936.TXT'

kundi TestGB18030Map(multibytecodec_support.TestBase_Mapping,
                     unittest.TestCase):
    encoding = 'gb18030'
    mapfileurl = 'http://www.pythontest.net/unicode/gb-18030-2000.xml'


ikiwa __name__ == "__main__":
    unittest.main()
