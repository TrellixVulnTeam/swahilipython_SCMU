#
# test_codecencodings_tw.py
#   Codec encoding tests kila ROC encodings.
#

kutoka test agiza multibytecodec_support
agiza unittest

kundi Test_Big5(multibytecodec_support.TestBase, unittest.TestCase):
    encoding = 'big5'
    tstring = multibytecodec_support.load_teststring('big5')
    codectests = (
        # invalid bytes
        (b"abc\x80\x80\xc1\xc4", "strict",  Tupu),
        (b"abc\xc8", "strict",  Tupu),
        (b"abc\x80\x80\xc1\xc4", "replace", "abc\ufffd\ufffd\u8b10"),
        (b"abc\x80\x80\xc1\xc4\xc8", "replace", "abc\ufffd\ufffd\u8b10\ufffd"),
        (b"abc\x80\x80\xc1\xc4", "ignore",  "abc\u8b10"),
    )

ikiwa __name__ == "__main__":
    unittest.main()
