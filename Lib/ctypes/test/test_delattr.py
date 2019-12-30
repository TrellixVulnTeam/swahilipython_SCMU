agiza unittest
kutoka ctypes agiza *

kundi X(Structure):
    _fields_ = [("foo", c_int)]

kundi TestCase(unittest.TestCase):
    eleza test_simple(self):
        self.assertRaises(TypeError,
                          delattr, c_int(42), "value")

    eleza test_chararray(self):
        self.assertRaises(TypeError,
                          delattr, (c_char * 5)(), "value")

    eleza test_struct(self):
        self.assertRaises(TypeError,
                          delattr, X(), "foo")

ikiwa __name__ == "__main__":
    unittest.main()
