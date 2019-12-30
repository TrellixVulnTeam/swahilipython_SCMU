kutoka ctypes agiza *
kutoka ctypes.test agiza need_symbol
agiza unittest
agiza os

agiza _ctypes_test

kundi BITS(Structure):
    _fields_ = [("A", c_int, 1),
                ("B", c_int, 2),
                ("C", c_int, 3),
                ("D", c_int, 4),
                ("E", c_int, 5),
                ("F", c_int, 6),
                ("G", c_int, 7),
                ("H", c_int, 8),
                ("I", c_int, 9),

                ("M", c_short, 1),
                ("N", c_short, 2),
                ("O", c_short, 3),
                ("P", c_short, 4),
                ("Q", c_short, 5),
                ("R", c_short, 6),
                ("S", c_short, 7)]

func = CDLL(_ctypes_test.__file__).unpack_bitfields
func.argtypes = POINTER(BITS), c_char

##kila n kwenye "ABCDEFGHIMNOPQRS":
##    print n, hex(getattr(BITS, n).size), getattr(BITS, n).offset

kundi C_Test(unittest.TestCase):

    eleza test_ints(self):
        kila i kwenye range(512):
            kila name kwenye "ABCDEFGHI":
                b = BITS()
                setattr(b, name, i)
                self.assertEqual(getattr(b, name), func(byref(b), name.encode('ascii')))

    eleza test_shorts(self):
        b = BITS()
        name = "M"
        ikiwa func(byref(b), name.encode('ascii')) == 999:
            self.skipTest("Compiler does sio support signed short bitfields")
        kila i kwenye range(256):
            kila name kwenye "MNOPQRS":
                b = BITS()
                setattr(b, name, i)
                self.assertEqual(getattr(b, name), func(byref(b), name.encode('ascii')))

signed_int_types = (c_byte, c_short, c_int, c_long, c_longlong)
unsigned_int_types = (c_ubyte, c_ushort, c_uint, c_ulong, c_ulonglong)
int_types = unsigned_int_types + signed_int_types

kundi BitFieldTest(unittest.TestCase):

    eleza test_longlong(self):
        kundi X(Structure):
            _fields_ = [("a", c_longlong, 1),
                        ("b", c_longlong, 62),
                        ("c", c_longlong, 1)]

        self.assertEqual(sizeof(X), sizeof(c_longlong))
        x = X()
        x.a, x.b, x.c = -1, 7, -1
        self.assertEqual((x.a, x.b, x.c), (-1, 7, -1))

    eleza test_ulonglong(self):
        kundi X(Structure):
            _fields_ = [("a", c_ulonglong, 1),
                        ("b", c_ulonglong, 62),
                        ("c", c_ulonglong, 1)]

        self.assertEqual(sizeof(X), sizeof(c_longlong))
        x = X()
        self.assertEqual((x.a, x.b, x.c), (0, 0, 0))
        x.a, x.b, x.c = 7, 7, 7
        self.assertEqual((x.a, x.b, x.c), (1, 7, 1))

    eleza test_signed(self):
        kila c_typ kwenye signed_int_types:
            kundi X(Structure):
                _fields_ = [("dummy", c_typ),
                            ("a", c_typ, 3),
                            ("b", c_typ, 3),
                            ("c", c_typ, 1)]
            self.assertEqual(sizeof(X), sizeof(c_typ)*2)

            x = X()
            self.assertEqual((c_typ, x.a, x.b, x.c), (c_typ, 0, 0, 0))
            x.a = -1
            self.assertEqual((c_typ, x.a, x.b, x.c), (c_typ, -1, 0, 0))
            x.a, x.b = 0, -1
            self.assertEqual((c_typ, x.a, x.b, x.c), (c_typ, 0, -1, 0))


    eleza test_unsigned(self):
        kila c_typ kwenye unsigned_int_types:
            kundi X(Structure):
                _fields_ = [("a", c_typ, 3),
                            ("b", c_typ, 3),
                            ("c", c_typ, 1)]
            self.assertEqual(sizeof(X), sizeof(c_typ))

            x = X()
            self.assertEqual((c_typ, x.a, x.b, x.c), (c_typ, 0, 0, 0))
            x.a = -1
            self.assertEqual((c_typ, x.a, x.b, x.c), (c_typ, 7, 0, 0))
            x.a, x.b = 0, -1
            self.assertEqual((c_typ, x.a, x.b, x.c), (c_typ, 0, 7, 0))


    eleza fail_fields(self, *fields):
        rudisha self.get_except(type(Structure), "X", (),
                               {"_fields_": fields})

    eleza test_nonint_types(self):
        # bit fields are sio allowed on non-integer types.
        result = self.fail_fields(("a", c_char_p, 1))
        self.assertEqual(result, (TypeError, 'bit fields sio allowed kila type c_char_p'))

        result = self.fail_fields(("a", c_void_p, 1))
        self.assertEqual(result, (TypeError, 'bit fields sio allowed kila type c_void_p'))

        ikiwa c_int != c_long:
            result = self.fail_fields(("a", POINTER(c_int), 1))
            self.assertEqual(result, (TypeError, 'bit fields sio allowed kila type LP_c_int'))

        result = self.fail_fields(("a", c_char, 1))
        self.assertEqual(result, (TypeError, 'bit fields sio allowed kila type c_char'))

        kundi Dummy(Structure):
            _fields_ = []

        result = self.fail_fields(("a", Dummy, 1))
        self.assertEqual(result, (TypeError, 'bit fields sio allowed kila type Dummy'))

    @need_symbol('c_wchar')
    eleza test_c_wchar(self):
        result = self.fail_fields(("a", c_wchar, 1))
        self.assertEqual(result,
                (TypeError, 'bit fields sio allowed kila type c_wchar'))

    eleza test_single_bitfield_size(self):
        kila c_typ kwenye int_types:
            result = self.fail_fields(("a", c_typ, -1))
            self.assertEqual(result, (ValueError, 'number of bits invalid kila bit field'))

            result = self.fail_fields(("a", c_typ, 0))
            self.assertEqual(result, (ValueError, 'number of bits invalid kila bit field'))

            kundi X(Structure):
                _fields_ = [("a", c_typ, 1)]
            self.assertEqual(sizeof(X), sizeof(c_typ))

            kundi X(Structure):
                _fields_ = [("a", c_typ, sizeof(c_typ)*8)]
            self.assertEqual(sizeof(X), sizeof(c_typ))

            result = self.fail_fields(("a", c_typ, sizeof(c_typ)*8 + 1))
            self.assertEqual(result, (ValueError, 'number of bits invalid kila bit field'))

    eleza test_multi_bitfields_size(self):
        kundi X(Structure):
            _fields_ = [("a", c_short, 1),
                        ("b", c_short, 14),
                        ("c", c_short, 1)]
        self.assertEqual(sizeof(X), sizeof(c_short))

        kundi X(Structure):
            _fields_ = [("a", c_short, 1),
                        ("a1", c_short),
                        ("b", c_short, 14),
                        ("c", c_short, 1)]
        self.assertEqual(sizeof(X), sizeof(c_short)*3)
        self.assertEqual(X.a.offset, 0)
        self.assertEqual(X.a1.offset, sizeof(c_short))
        self.assertEqual(X.b.offset, sizeof(c_short)*2)
        self.assertEqual(X.c.offset, sizeof(c_short)*2)

        kundi X(Structure):
            _fields_ = [("a", c_short, 3),
                        ("b", c_short, 14),
                        ("c", c_short, 14)]
        self.assertEqual(sizeof(X), sizeof(c_short)*3)
        self.assertEqual(X.a.offset, sizeof(c_short)*0)
        self.assertEqual(X.b.offset, sizeof(c_short)*1)
        self.assertEqual(X.c.offset, sizeof(c_short)*2)


    eleza get_except(self, func, *args, **kw):
        jaribu:
            func(*args, **kw)
        except Exception as detail:
            rudisha detail.__class__, str(detail)

    eleza test_mixed_1(self):
        kundi X(Structure):
            _fields_ = [("a", c_byte, 4),
                        ("b", c_int, 4)]
        ikiwa os.name == "nt":
            self.assertEqual(sizeof(X), sizeof(c_int)*2)
        isipokua:
            self.assertEqual(sizeof(X), sizeof(c_int))

    eleza test_mixed_2(self):
        kundi X(Structure):
            _fields_ = [("a", c_byte, 4),
                        ("b", c_int, 32)]
        self.assertEqual(sizeof(X), alignment(c_int)+sizeof(c_int))

    eleza test_mixed_3(self):
        kundi X(Structure):
            _fields_ = [("a", c_byte, 4),
                        ("b", c_ubyte, 4)]
        self.assertEqual(sizeof(X), sizeof(c_byte))

    eleza test_mixed_4(self):
        kundi X(Structure):
            _fields_ = [("a", c_short, 4),
                        ("b", c_short, 4),
                        ("c", c_int, 24),
                        ("d", c_short, 4),
                        ("e", c_short, 4),
                        ("f", c_int, 24)]
        # MSVC does NOT combine c_short na c_int into one field, GCC
        # does (unless GCC ni run ukijumuisha '-mms-bitfields' which
        # produces code compatible ukijumuisha MSVC).
        ikiwa os.name == "nt":
            self.assertEqual(sizeof(X), sizeof(c_int) * 4)
        isipokua:
            self.assertEqual(sizeof(X), sizeof(c_int) * 2)

    eleza test_anon_bitfields(self):
        # anonymous bit-fields gave a strange error message
        kundi X(Structure):
            _fields_ = [("a", c_byte, 4),
                        ("b", c_ubyte, 4)]
        kundi Y(Structure):
            _anonymous_ = ["_"]
            _fields_ = [("_", X)]

    @need_symbol('c_uint32')
    eleza test_uint32(self):
        kundi X(Structure):
            _fields_ = [("a", c_uint32, 32)]
        x = X()
        x.a = 10
        self.assertEqual(x.a, 10)
        x.a = 0xFDCBA987
        self.assertEqual(x.a, 0xFDCBA987)

    @need_symbol('c_uint64')
    eleza test_uint64(self):
        kundi X(Structure):
            _fields_ = [("a", c_uint64, 64)]
        x = X()
        x.a = 10
        self.assertEqual(x.a, 10)
        x.a = 0xFEDCBA9876543211
        self.assertEqual(x.a, 0xFEDCBA9876543211)

    @need_symbol('c_uint32')
    eleza test_uint32_swap_little_endian(self):
        # Issue #23319
        kundi Little(LittleEndianStructure):
            _fields_ = [("a", c_uint32, 24),
                        ("b", c_uint32, 4),
                        ("c", c_uint32, 4)]
        b = bytearray(4)
        x = Little.from_buffer(b)
        x.a = 0xabcdef
        x.b = 1
        x.c = 2
        self.assertEqual(b, b'\xef\xcd\xab\x21')

    @need_symbol('c_uint32')
    eleza test_uint32_swap_big_endian(self):
        # Issue #23319
        kundi Big(BigEndianStructure):
            _fields_ = [("a", c_uint32, 24),
                        ("b", c_uint32, 4),
                        ("c", c_uint32, 4)]
        b = bytearray(4)
        x = Big.from_buffer(b)
        x.a = 0xabcdef
        x.b = 1
        x.c = 2
        self.assertEqual(b, b'\xab\xcd\xef\x12')

ikiwa __name__ == "__main__":
    unittest.main()
