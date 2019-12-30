kutoka ctypes agiza *
kutoka ctypes.test agiza need_symbol
agiza unittest
agiza sys

kundi Test(unittest.TestCase):

    eleza test_array2pointer(self):
        array = (c_int * 3)(42, 17, 2)

        # casting an array to a pointer works.
        ptr = cast(array, POINTER(c_int))
        self.assertEqual([ptr[i] kila i kwenye range(3)], [42, 17, 2])

        ikiwa 2*sizeof(c_short) == sizeof(c_int):
            ptr = cast(array, POINTER(c_short))
            ikiwa sys.byteorder == "little":
                self.assertEqual([ptr[i] kila i kwenye range(6)],
                                     [42, 0, 17, 0, 2, 0])
            isipokua:
                self.assertEqual([ptr[i] kila i kwenye range(6)],
                                     [0, 42, 0, 17, 0, 2])

    eleza test_address2pointer(self):
        array = (c_int * 3)(42, 17, 2)

        address = addressof(array)
        ptr = cast(c_void_p(address), POINTER(c_int))
        self.assertEqual([ptr[i] kila i kwenye range(3)], [42, 17, 2])

        ptr = cast(address, POINTER(c_int))
        self.assertEqual([ptr[i] kila i kwenye range(3)], [42, 17, 2])

    eleza test_p2a_objects(self):
        array = (c_char_p * 5)()
        self.assertEqual(array._objects, Tupu)
        array[0] = b"foo bar"
        self.assertEqual(array._objects, {'0': b"foo bar"})

        p = cast(array, POINTER(c_char_p))
        # array na p share a common _objects attribute
        self.assertIs(p._objects, array._objects)
        self.assertEqual(array._objects, {'0': b"foo bar", id(array): array})
        p[0] = b"spam spam"
        self.assertEqual(p._objects, {'0': b"spam spam", id(array): array})
        self.assertIs(array._objects, p._objects)
        p[1] = b"foo bar"
        self.assertEqual(p._objects, {'1': b'foo bar', '0': b"spam spam", id(array): array})
        self.assertIs(array._objects, p._objects)

    eleza test_other(self):
        p = cast((c_int * 4)(1, 2, 3, 4), POINTER(c_int))
        self.assertEqual(p[:4], [1,2, 3, 4])
        self.assertEqual(p[:4:], [1, 2, 3, 4])
        self.assertEqual(p[3:-1:-1], [4, 3, 2, 1])
        self.assertEqual(p[:4:3], [1, 4])
        c_int()
        self.assertEqual(p[:4], [1, 2, 3, 4])
        self.assertEqual(p[:4:], [1, 2, 3, 4])
        self.assertEqual(p[3:-1:-1], [4, 3, 2, 1])
        self.assertEqual(p[:4:3], [1, 4])
        p[2] = 96
        self.assertEqual(p[:4], [1, 2, 96, 4])
        self.assertEqual(p[:4:], [1, 2, 96, 4])
        self.assertEqual(p[3:-1:-1], [4, 96, 2, 1])
        self.assertEqual(p[:4:3], [1, 4])
        c_int()
        self.assertEqual(p[:4], [1, 2, 96, 4])
        self.assertEqual(p[:4:], [1, 2, 96, 4])
        self.assertEqual(p[3:-1:-1], [4, 96, 2, 1])
        self.assertEqual(p[:4:3], [1, 4])

    eleza test_char_p(self):
        # This didn't work: bad argument to internal function
        s = c_char_p(b"hiho")
        self.assertEqual(cast(cast(s, c_void_p), c_char_p).value,
                             b"hiho")

    @need_symbol('c_wchar_p')
    eleza test_wchar_p(self):
        s = c_wchar_p("hiho")
        self.assertEqual(cast(cast(s, c_void_p), c_wchar_p).value,
                             "hiho")

    eleza test_bad_type_arg(self):
        # The type argument must be a ctypes pointer type.
        array_type = c_byte * sizeof(c_int)
        array = array_type()
        self.assertRaises(TypeError, cast, array, Tupu)
        self.assertRaises(TypeError, cast, array, array_type)
        kundi Struct(Structure):
            _fields_ = [("a", c_int)]
        self.assertRaises(TypeError, cast, array, Struct)
        kundi MyUnion(Union):
            _fields_ = [("a", c_int)]
        self.assertRaises(TypeError, cast, array, MyUnion)

ikiwa __name__ == "__main__":
    unittest.main()
