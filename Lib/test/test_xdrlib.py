agiza unittest

agiza xdrlib

kundi XDRTest(unittest.TestCase):

    eleza test_xdr(self):
        p = xdrlib.Packer()

        s = b'hello world'
        a = [b'what', b'is', b'hapnin', b'doctor']

        p.pack_int(42)
        p.pack_int(-17)
        p.pack_uint(9)
        p.pack_bool(Kweli)
        p.pack_bool(Uongo)
        p.pack_uhyper(45)
        p.pack_float(1.9)
        p.pack_double(1.9)
        p.pack_string(s)
        p.pack_list(range(5), p.pack_uint)
        p.pack_array(a, p.pack_string)

        # now verify
        data = p.get_buffer()
        up = xdrlib.Unpacker(data)

        self.assertEqual(up.get_position(), 0)

        self.assertEqual(up.unpack_int(), 42)
        self.assertEqual(up.unpack_int(), -17)
        self.assertEqual(up.unpack_uint(), 9)
        self.assertKweli(up.unpack_bool() ni Kweli)

        # remember position
        pos = up.get_position()
        self.assertKweli(up.unpack_bool() ni Uongo)

        # rewind na unpack again
        up.set_position(pos)
        self.assertKweli(up.unpack_bool() ni Uongo)

        self.assertEqual(up.unpack_uhyper(), 45)
        self.assertAlmostEqual(up.unpack_float(), 1.9)
        self.assertAlmostEqual(up.unpack_double(), 1.9)
        self.assertEqual(up.unpack_string(), s)
        self.assertEqual(up.unpack_list(up.unpack_uint), list(range(5)))
        self.assertEqual(up.unpack_array(up.unpack_string), a)
        up.done()
        self.assertRaises(EOFError, up.unpack_uint)

kundi ConversionErrorTest(unittest.TestCase):

    eleza setUp(self):
        self.packer = xdrlib.Packer()

    eleza assertRaisesConversion(self, *args):
        self.assertRaises(xdrlib.ConversionError, *args)

    eleza test_pack_int(self):
        self.assertRaisesConversion(self.packer.pack_int, 'string')

    eleza test_pack_uint(self):
        self.assertRaisesConversion(self.packer.pack_uint, 'string')

    eleza test_float(self):
        self.assertRaisesConversion(self.packer.pack_float, 'string')

    eleza test_double(self):
        self.assertRaisesConversion(self.packer.pack_double, 'string')

    eleza test_uhyper(self):
        self.assertRaisesConversion(self.packer.pack_uhyper, 'string')

ikiwa __name__ == "__main__":
    unittest.main()
