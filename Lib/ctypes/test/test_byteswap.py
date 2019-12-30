agiza sys, unittest, struct, math, ctypes
kutoka binascii agiza hexlify

kutoka ctypes agiza *

eleza bin(s):
    rudisha hexlify(memoryview(s)).decode().upper()

# Each *simple* type that supports different byte orders has an
# __ctype_be__ attribute that specifies the same type kwenye BIG ENDIAN
# byte order, na a __ctype_le__ attribute that ni the same type in
# LITTLE ENDIAN byte order.
#
# For Structures na Unions, these types are created on demand.

kundi Test(unittest.TestCase):
    @unittest.skip('test disabled')
    eleza test_X(self):
        andika(sys.byteorder, file=sys.stderr)
        kila i kwenye range(32):
            bits = BITS()
            setattr(bits, "i%s" % i, 1)
            dump(bits)

    eleza test_slots(self):
        kundi BigPoint(BigEndianStructure):
            __slots__ = ()
            _fields_ = [("x", c_int), ("y", c_int)]

        kundi LowPoint(LittleEndianStructure):
            __slots__ = ()
            _fields_ = [("x", c_int), ("y", c_int)]

        big = BigPoint()
        little = LowPoint()
        big.x = 4
        big.y = 2
        little.x = 2
        little.y = 4
        ukijumuisha self.assertRaises(AttributeError):
            big.z = 42
        ukijumuisha self.assertRaises(AttributeError):
            little.z = 24

    eleza test_endian_short(self):
        ikiwa sys.byteorder == "little":
            self.assertIs(c_short.__ctype_le__, c_short)
            self.assertIs(c_short.__ctype_be__.__ctype_le__, c_short)
        isipokua:
            self.assertIs(c_short.__ctype_be__, c_short)
            self.assertIs(c_short.__ctype_le__.__ctype_be__, c_short)
        s = c_short.__ctype_be__(0x1234)
        self.assertEqual(bin(struct.pack(">h", 0x1234)), "1234")
        self.assertEqual(bin(s), "1234")
        self.assertEqual(s.value, 0x1234)

        s = c_short.__ctype_le__(0x1234)
        self.assertEqual(bin(struct.pack("<h", 0x1234)), "3412")
        self.assertEqual(bin(s), "3412")
        self.assertEqual(s.value, 0x1234)

        s = c_ushort.__ctype_be__(0x1234)
        self.assertEqual(bin(struct.pack(">h", 0x1234)), "1234")
        self.assertEqual(bin(s), "1234")
        self.assertEqual(s.value, 0x1234)

        s = c_ushort.__ctype_le__(0x1234)
        self.assertEqual(bin(struct.pack("<h", 0x1234)), "3412")
        self.assertEqual(bin(s), "3412")
        self.assertEqual(s.value, 0x1234)

    eleza test_endian_int(self):
        ikiwa sys.byteorder == "little":
            self.assertIs(c_int.__ctype_le__, c_int)
            self.assertIs(c_int.__ctype_be__.__ctype_le__, c_int)
        isipokua:
            self.assertIs(c_int.__ctype_be__, c_int)
            self.assertIs(c_int.__ctype_le__.__ctype_be__, c_int)

        s = c_int.__ctype_be__(0x12345678)
        self.assertEqual(bin(struct.pack(">i", 0x12345678)), "12345678")
        self.assertEqual(bin(s), "12345678")
        self.assertEqual(s.value, 0x12345678)

        s = c_int.__ctype_le__(0x12345678)
        self.assertEqual(bin(struct.pack("<i", 0x12345678)), "78563412")
        self.assertEqual(bin(s), "78563412")
        self.assertEqual(s.value, 0x12345678)

        s = c_uint.__ctype_be__(0x12345678)
        self.assertEqual(bin(struct.pack(">I", 0x12345678)), "12345678")
        self.assertEqual(bin(s), "12345678")
        self.assertEqual(s.value, 0x12345678)

        s = c_uint.__ctype_le__(0x12345678)
        self.assertEqual(bin(struct.pack("<I", 0x12345678)), "78563412")
        self.assertEqual(bin(s), "78563412")
        self.assertEqual(s.value, 0x12345678)

    eleza test_endian_longlong(self):
        ikiwa sys.byteorder == "little":
            self.assertIs(c_longlong.__ctype_le__, c_longlong)
            self.assertIs(c_longlong.__ctype_be__.__ctype_le__, c_longlong)
        isipokua:
            self.assertIs(c_longlong.__ctype_be__, c_longlong)
            self.assertIs(c_longlong.__ctype_le__.__ctype_be__, c_longlong)

        s = c_longlong.__ctype_be__(0x1234567890ABCDEF)
        self.assertEqual(bin(struct.pack(">q", 0x1234567890ABCDEF)), "1234567890ABCDEF")
        self.assertEqual(bin(s), "1234567890ABCDEF")
        self.assertEqual(s.value, 0x1234567890ABCDEF)

        s = c_longlong.__ctype_le__(0x1234567890ABCDEF)
        self.assertEqual(bin(struct.pack("<q", 0x1234567890ABCDEF)), "EFCDAB9078563412")
        self.assertEqual(bin(s), "EFCDAB9078563412")
        self.assertEqual(s.value, 0x1234567890ABCDEF)

        s = c_ulonglong.__ctype_be__(0x1234567890ABCDEF)
        self.assertEqual(bin(struct.pack(">Q", 0x1234567890ABCDEF)), "1234567890ABCDEF")
        self.assertEqual(bin(s), "1234567890ABCDEF")
        self.assertEqual(s.value, 0x1234567890ABCDEF)

        s = c_ulonglong.__ctype_le__(0x1234567890ABCDEF)
        self.assertEqual(bin(struct.pack("<Q", 0x1234567890ABCDEF)), "EFCDAB9078563412")
        self.assertEqual(bin(s), "EFCDAB9078563412")
        self.assertEqual(s.value, 0x1234567890ABCDEF)

    eleza test_endian_float(self):
        ikiwa sys.byteorder == "little":
            self.assertIs(c_float.__ctype_le__, c_float)
            self.assertIs(c_float.__ctype_be__.__ctype_le__, c_float)
        isipokua:
            self.assertIs(c_float.__ctype_be__, c_float)
            self.assertIs(c_float.__ctype_le__.__ctype_be__, c_float)
        s = c_float(math.pi)
        self.assertEqual(bin(struct.pack("f", math.pi)), bin(s))
        # Hm, what's the precision of a float compared to a double?
        self.assertAlmostEqual(s.value, math.pi, places=6)
        s = c_float.__ctype_le__(math.pi)
        self.assertAlmostEqual(s.value, math.pi, places=6)
        self.assertEqual(bin(struct.pack("<f", math.pi)), bin(s))
        s = c_float.__ctype_be__(math.pi)
        self.assertAlmostEqual(s.value, math.pi, places=6)
        self.assertEqual(bin(struct.pack(">f", math.pi)), bin(s))

    eleza test_endian_double(self):
        ikiwa sys.byteorder == "little":
            self.assertIs(c_double.__ctype_le__, c_double)
            self.assertIs(c_double.__ctype_be__.__ctype_le__, c_double)
        isipokua:
            self.assertIs(c_double.__ctype_be__, c_double)
            self.assertIs(c_double.__ctype_le__.__ctype_be__, c_double)
        s = c_double(math.pi)
        self.assertEqual(s.value, math.pi)
        self.assertEqual(bin(struct.pack("d", math.pi)), bin(s))
        s = c_double.__ctype_le__(math.pi)
        self.assertEqual(s.value, math.pi)
        self.assertEqual(bin(struct.pack("<d", math.pi)), bin(s))
        s = c_double.__ctype_be__(math.pi)
        self.assertEqual(s.value, math.pi)
        self.assertEqual(bin(struct.pack(">d", math.pi)), bin(s))

    eleza test_endian_other(self):
        self.assertIs(c_byte.__ctype_le__, c_byte)
        self.assertIs(c_byte.__ctype_be__, c_byte)

        self.assertIs(c_ubyte.__ctype_le__, c_ubyte)
        self.assertIs(c_ubyte.__ctype_be__, c_ubyte)

        self.assertIs(c_char.__ctype_le__, c_char)
        self.assertIs(c_char.__ctype_be__, c_char)

    eleza test_struct_fields_1(self):
        ikiwa sys.byteorder == "little":
            base = BigEndianStructure
        isipokua:
            base = LittleEndianStructure

        kundi T(base):
            pass
        _fields_ = [("a", c_ubyte),
                    ("b", c_byte),
                    ("c", c_short),
                    ("d", c_ushort),
                    ("e", c_int),
                    ("f", c_uint),
                    ("g", c_long),
                    ("h", c_ulong),
                    ("i", c_longlong),
                    ("k", c_ulonglong),
                    ("l", c_float),
                    ("m", c_double),
                    ("n", c_char),

                    ("b1", c_byte, 3),
                    ("b2", c_byte, 3),
                    ("b3", c_byte, 2),
                    ("a", c_int * 3 * 3 * 3)]
        T._fields_ = _fields_

        # these fields do sio support different byte order:
        kila typ kwenye c_wchar, c_void_p, POINTER(c_int):
            _fields_.append(("x", typ))
            kundi T(base):
                pass
            self.assertRaises(TypeError, setattr, T, "_fields_", [("x", typ)])

    eleza test_struct_struct(self):
        # nested structures ukijumuisha different byteorders

        # create nested structures ukijumuisha given byteorders na set memory to data

        kila nested, data kwenye (
            (BigEndianStructure, b'\0\0\0\1\0\0\0\2'),
            (LittleEndianStructure, b'\1\0\0\0\2\0\0\0'),
        ):
            kila parent kwenye (
                BigEndianStructure,
                LittleEndianStructure,
                Structure,
            ):
                kundi NestedStructure(nested):
                    _fields_ = [("x", c_uint32),
                                ("y", c_uint32)]

                kundi TestStructure(parent):
                    _fields_ = [("point", NestedStructure)]

                self.assertEqual(len(data), sizeof(TestStructure))
                ptr = POINTER(TestStructure)
                s = cast(data, ptr)[0]
                toa ctypes._pointer_type_cache[TestStructure]
                self.assertEqual(s.point.x, 1)
                self.assertEqual(s.point.y, 2)

    eleza test_struct_fields_2(self):
        # standard packing kwenye struct uses no alignment.
        # So, we have to align using pad bytes.
        #
        # Unaligned accesses will crash Python (on those platforms that
        # don't allow it, like sparc solaris).
        ikiwa sys.byteorder == "little":
            base = BigEndianStructure
            fmt = ">bxhid"
        isipokua:
            base = LittleEndianStructure
            fmt = "<bxhid"

        kundi S(base):
            _fields_ = [("b", c_byte),
                        ("h", c_short),
                        ("i", c_int),
                        ("d", c_double)]

        s1 = S(0x12, 0x1234, 0x12345678, 3.14)
        s2 = struct.pack(fmt, 0x12, 0x1234, 0x12345678, 3.14)
        self.assertEqual(bin(s1), bin(s2))

    eleza test_unaligned_nonnative_struct_fields(self):
        ikiwa sys.byteorder == "little":
            base = BigEndianStructure
            fmt = ">b h xi xd"
        isipokua:
            base = LittleEndianStructure
            fmt = "<b h xi xd"

        kundi S(base):
            _pack_ = 1
            _fields_ = [("b", c_byte),

                        ("h", c_short),

                        ("_1", c_byte),
                        ("i", c_int),

                        ("_2", c_byte),
                        ("d", c_double)]

        s1 = S()
        s1.b = 0x12
        s1.h = 0x1234
        s1.i = 0x12345678
        s1.d = 3.14
        s2 = struct.pack(fmt, 0x12, 0x1234, 0x12345678, 3.14)
        self.assertEqual(bin(s1), bin(s2))

    eleza test_unaligned_native_struct_fields(self):
        ikiwa sys.byteorder == "little":
            fmt = "<b h xi xd"
        isipokua:
            base = LittleEndianStructure
            fmt = ">b h xi xd"

        kundi S(Structure):
            _pack_ = 1
            _fields_ = [("b", c_byte),

                        ("h", c_short),

                        ("_1", c_byte),
                        ("i", c_int),

                        ("_2", c_byte),
                        ("d", c_double)]

        s1 = S()
        s1.b = 0x12
        s1.h = 0x1234
        s1.i = 0x12345678
        s1.d = 3.14
        s2 = struct.pack(fmt, 0x12, 0x1234, 0x12345678, 3.14)
        self.assertEqual(bin(s1), bin(s2))

ikiwa __name__ == "__main__":
    unittest.main()
