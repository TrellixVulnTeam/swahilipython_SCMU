# Test specifically-sized containers.

kutoka ctypes agiza *

agiza unittest


kundi SizesTestCase(unittest.TestCase):
    eleza test_8(self):
        self.assertEqual(1, sizeof(c_int8))
        self.assertEqual(1, sizeof(c_uint8))

    eleza test_16(self):
        self.assertEqual(2, sizeof(c_int16))
        self.assertEqual(2, sizeof(c_uint16))

    eleza test_32(self):
        self.assertEqual(4, sizeof(c_int32))
        self.assertEqual(4, sizeof(c_uint32))

    eleza test_64(self):
        self.assertEqual(8, sizeof(c_int64))
        self.assertEqual(8, sizeof(c_uint64))

    eleza test_size_t(self):
        self.assertEqual(sizeof(c_void_p), sizeof(c_size_t))

    eleza test_ssize_t(self):
        self.assertEqual(sizeof(c_void_p), sizeof(c_ssize_t))


ikiwa __name__ == "__main__":
    unittest.main()
