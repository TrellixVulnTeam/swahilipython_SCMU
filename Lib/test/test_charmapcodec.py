""" Python character mapping codec test

This uses the test codec in testcodec.py and thus also tests the
encodings package lookup scheme.

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright 2000 Guido van Rossum.

"""#"

agiza unittest

agiza codecs

# Register a search function which knows about our codec
eleza codec_search_function(encoding):
    ikiwa encoding == 'testcodec':
        kutoka test agiza testcodec
        rudisha tuple(testcodec.getregentry())
    rudisha None

codecs.register(codec_search_function)

# test codec's name (see test/testcodec.py)
codecname = 'testcodec'

kundi CharmapCodecTest(unittest.TestCase):
    eleza test_constructorx(self):
        self.assertEqual(str(b'abc', codecname), 'abc')
        self.assertEqual(str(b'xdef', codecname), 'abcdef')
        self.assertEqual(str(b'defx', codecname), 'defabc')
        self.assertEqual(str(b'dxf', codecname), 'dabcf')
        self.assertEqual(str(b'dxfx', codecname), 'dabcfabc')

    eleza test_encodex(self):
        self.assertEqual('abc'.encode(codecname), b'abc')
        self.assertEqual('xdef'.encode(codecname), b'abcdef')
        self.assertEqual('defx'.encode(codecname), b'defabc')
        self.assertEqual('dxf'.encode(codecname), b'dabcf')
        self.assertEqual('dxfx'.encode(codecname), b'dabcfabc')

    eleza test_constructory(self):
        self.assertEqual(str(b'ydef', codecname), 'def')
        self.assertEqual(str(b'defy', codecname), 'def')
        self.assertEqual(str(b'dyf', codecname), 'df')
        self.assertEqual(str(b'dyfy', codecname), 'df')

    eleza test_maptoundefined(self):
        self.assertRaises(UnicodeError, str, b'abc\001', codecname)

ikiwa __name__ == "__main__":
    unittest.main()
