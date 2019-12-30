agiza platform
agiza sys
agiza unittest
kutoka ctypes agiza *
kutoka ctypes.test agiza need_symbol
kutoka struct agiza calcsize
agiza _ctypes_test
kutoka test agiza support

kundi SubclassesTest(unittest.TestCase):
    eleza test_subclass(self):
        kundi X(Structure):
            _fields_ = [("a", c_int)]

        kundi Y(X):
            _fields_ = [("b", c_int)]

        kundi Z(X):
            pita

        self.assertEqual(sizeof(X), sizeof(c_int))
        self.assertEqual(sizeof(Y), sizeof(c_int)*2)
        self.assertEqual(sizeof(Z), sizeof(c_int))
        self.assertEqual(X._fields_, [("a", c_int)])
        self.assertEqual(Y._fields_, [("b", c_int)])
        self.assertEqual(Z._fields_, [("a", c_int)])

    eleza test_subclass_delayed(self):
        kundi X(Structure):
            pita
        self.assertEqual(sizeof(X), 0)
        X._fields_ = [("a", c_int)]

        kundi Y(X):
            pita
        self.assertEqual(sizeof(Y), sizeof(X))
        Y._fields_ = [("b", c_int)]

        kundi Z(X):
            pita

        self.assertEqual(sizeof(X), sizeof(c_int))
        self.assertEqual(sizeof(Y), sizeof(c_int)*2)
        self.assertEqual(sizeof(Z), sizeof(c_int))
        self.assertEqual(X._fields_, [("a", c_int)])
        self.assertEqual(Y._fields_, [("b", c_int)])
        self.assertEqual(Z._fields_, [("a", c_int)])

kundi StructureTestCase(unittest.TestCase):
    formats = {"c": c_char,
               "b": c_byte,
               "B": c_ubyte,
               "h": c_short,
               "H": c_ushort,
               "i": c_int,
               "I": c_uint,
               "l": c_long,
               "L": c_ulong,
               "q": c_longlong,
               "Q": c_ulonglong,
               "f": c_float,
               "d": c_double,
               }

    eleza test_simple_structs(self):
        kila code, tp kwenye self.formats.items():
            kundi X(Structure):
                _fields_ = [("x", c_char),
                            ("y", tp)]
            self.assertEqual((sizeof(X), code),
                                 (calcsize("c%c0%c" % (code, code)), code))

    eleza test_unions(self):
        kila code, tp kwenye self.formats.items():
            kundi X(Union):
                _fields_ = [("x", c_char),
                            ("y", tp)]
            self.assertEqual((sizeof(X), code),
                                 (calcsize("%c" % (code)), code))

    eleza test_struct_alignment(self):
        kundi X(Structure):
            _fields_ = [("x", c_char * 3)]
        self.assertEqual(alignment(X), calcsize("s"))
        self.assertEqual(sizeof(X), calcsize("3s"))

        kundi Y(Structure):
            _fields_ = [("x", c_char * 3),
                        ("y", c_int)]
        self.assertEqual(alignment(Y), alignment(c_int))
        self.assertEqual(sizeof(Y), calcsize("3si"))

        kundi SI(Structure):
            _fields_ = [("a", X),
                        ("b", Y)]
        self.assertEqual(alignment(SI), max(alignment(Y), alignment(X)))
        self.assertEqual(sizeof(SI), calcsize("3s0i 3si 0i"))

        kundi IS(Structure):
            _fields_ = [("b", Y),
                        ("a", X)]

        self.assertEqual(alignment(SI), max(alignment(X), alignment(Y)))
        self.assertEqual(sizeof(IS), calcsize("3si 3s 0i"))

        kundi XX(Structure):
            _fields_ = [("a", X),
                        ("b", X)]
        self.assertEqual(alignment(XX), alignment(X))
        self.assertEqual(sizeof(XX), calcsize("3s 3s 0s"))

    eleza test_empty(self):
        # I had problems ukijumuisha these
        #
        # Although these are pathological cases: Empty Structures!
        kundi X(Structure):
            _fields_ = []

        kundi Y(Union):
            _fields_ = []

        # Is this really the correct alignment, ama should it be 0?
        self.assertKweli(alignment(X) == alignment(Y) == 1)
        self.assertKweli(sizeof(X) == sizeof(Y) == 0)

        kundi XX(Structure):
            _fields_ = [("a", X),
                        ("b", X)]

        self.assertEqual(alignment(XX), 1)
        self.assertEqual(sizeof(XX), 0)

    eleza test_fields(self):
        # test the offset na size attributes of Structure/Union fields.
        kundi X(Structure):
            _fields_ = [("x", c_int),
                        ("y", c_char)]

        self.assertEqual(X.x.offset, 0)
        self.assertEqual(X.x.size, sizeof(c_int))

        self.assertEqual(X.y.offset, sizeof(c_int))
        self.assertEqual(X.y.size, sizeof(c_char))

        # readonly
        self.assertRaises((TypeError, AttributeError), setattr, X.x, "offset", 92)
        self.assertRaises((TypeError, AttributeError), setattr, X.x, "size", 92)

        kundi X(Union):
            _fields_ = [("x", c_int),
                        ("y", c_char)]

        self.assertEqual(X.x.offset, 0)
        self.assertEqual(X.x.size, sizeof(c_int))

        self.assertEqual(X.y.offset, 0)
        self.assertEqual(X.y.size, sizeof(c_char))

        # readonly
        self.assertRaises((TypeError, AttributeError), setattr, X.x, "offset", 92)
        self.assertRaises((TypeError, AttributeError), setattr, X.x, "size", 92)

        # XXX Should we check nested data types also?
        # offset ni always relative to the class...

    eleza test_packed(self):
        kundi X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 1

        self.assertEqual(sizeof(X), 9)
        self.assertEqual(X.b.offset, 1)

        kundi X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 2
        self.assertEqual(sizeof(X), 10)
        self.assertEqual(X.b.offset, 2)

        agiza struct
        longlong_size = struct.calcsize("q")
        longlong_align = struct.calcsize("bq") - longlong_size

        kundi X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 4
        self.assertEqual(sizeof(X), min(4, longlong_align) + longlong_size)
        self.assertEqual(X.b.offset, min(4, longlong_align))

        kundi X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 8

        self.assertEqual(sizeof(X), min(8, longlong_align) + longlong_size)
        self.assertEqual(X.b.offset, min(8, longlong_align))


        d = {"_fields_": [("a", "b"),
                          ("b", "q")],
             "_pack_": -1}
        self.assertRaises(ValueError, type(Structure), "X", (Structure,), d)

    @support.cpython_only
    eleza test_packed_c_limits(self):
        # Issue 15989
        agiza _testcapi
        d = {"_fields_": [("a", c_byte)],
             "_pack_": _testcapi.INT_MAX + 1}
        self.assertRaises(ValueError, type(Structure), "X", (Structure,), d)
        d = {"_fields_": [("a", c_byte)],
             "_pack_": _testcapi.UINT_MAX + 2}
        self.assertRaises(ValueError, type(Structure), "X", (Structure,), d)

    eleza test_initializers(self):
        kundi Person(Structure):
            _fields_ = [("name", c_char*6),
                        ("age", c_int)]

        self.assertRaises(TypeError, Person, 42)
        self.assertRaises(ValueError, Person, b"asldkjaslkdjaslkdj")
        self.assertRaises(TypeError, Person, "Name", "HI")

        # short enough
        self.assertEqual(Person(b"12345", 5).name, b"12345")
        # exact fit
        self.assertEqual(Person(b"123456", 5).name, b"123456")
        # too long
        self.assertRaises(ValueError, Person, b"1234567", 5)

    eleza test_conflicting_initializers(self):
        kundi POINT(Structure):
            _fields_ = [("phi", c_float), ("rho", c_float)]
        # conflicting positional na keyword args
        self.assertRaisesRegex(TypeError, "phi", POINT, 2, 3, phi=4)
        self.assertRaisesRegex(TypeError, "rho", POINT, 2, 3, rho=4)

        # too many initializers
        self.assertRaises(TypeError, POINT, 2, 3, 4)

    eleza test_keyword_initializers(self):
        kundi POINT(Structure):
            _fields_ = [("x", c_int), ("y", c_int)]
        pt = POINT(1, 2)
        self.assertEqual((pt.x, pt.y), (1, 2))

        pt = POINT(y=2, x=1)
        self.assertEqual((pt.x, pt.y), (1, 2))

    eleza test_invalid_field_types(self):
        kundi POINT(Structure):
            pita
        self.assertRaises(TypeError, setattr, POINT, "_fields_", [("x", 1), ("y", 2)])

    eleza test_invalid_name(self):
        # field name must be string
        eleza declare_with_name(name):
            kundi S(Structure):
                _fields_ = [(name, c_int)]

        self.assertRaises(TypeError, declare_with_name, b"x")

    eleza test_intarray_fields(self):
        kundi SomeInts(Structure):
            _fields_ = [("a", c_int * 4)]

        # can use tuple to initialize array (but sio list!)
        self.assertEqual(SomeInts((1, 2)).a[:], [1, 2, 0, 0])
        self.assertEqual(SomeInts((1, 2)).a[::], [1, 2, 0, 0])
        self.assertEqual(SomeInts((1, 2)).a[::-1], [0, 0, 2, 1])
        self.assertEqual(SomeInts((1, 2)).a[::2], [1, 0])
        self.assertEqual(SomeInts((1, 2)).a[1:5:6], [2])
        self.assertEqual(SomeInts((1, 2)).a[6:4:-1], [])
        self.assertEqual(SomeInts((1, 2, 3, 4)).a[:], [1, 2, 3, 4])
        self.assertEqual(SomeInts((1, 2, 3, 4)).a[::], [1, 2, 3, 4])
        # too long
        # XXX Should ashiria ValueError?, sio RuntimeError
        self.assertRaises(RuntimeError, SomeInts, (1, 2, 3, 4, 5))

    eleza test_nested_initializers(self):
        # test initializing nested structures
        kundi Phone(Structure):
            _fields_ = [("areacode", c_char*6),
                        ("number", c_char*12)]

        kundi Person(Structure):
            _fields_ = [("name", c_char * 12),
                        ("phone", Phone),
                        ("age", c_int)]

        p = Person(b"Someone", (b"1234", b"5678"), 5)

        self.assertEqual(p.name, b"Someone")
        self.assertEqual(p.phone.areacode, b"1234")
        self.assertEqual(p.phone.number, b"5678")
        self.assertEqual(p.age, 5)

    @need_symbol('c_wchar')
    eleza test_structures_with_wchar(self):
        kundi PersonW(Structure):
            _fields_ = [("name", c_wchar * 12),
                        ("age", c_int)]

        p = PersonW("Someone \xe9")
        self.assertEqual(p.name, "Someone \xe9")

        self.assertEqual(PersonW("1234567890").name, "1234567890")
        self.assertEqual(PersonW("12345678901").name, "12345678901")
        # exact fit
        self.assertEqual(PersonW("123456789012").name, "123456789012")
        #too long
        self.assertRaises(ValueError, PersonW, "1234567890123")

    eleza test_init_errors(self):
        kundi Phone(Structure):
            _fields_ = [("areacode", c_char*6),
                        ("number", c_char*12)]

        kundi Person(Structure):
            _fields_ = [("name", c_char * 12),
                        ("phone", Phone),
                        ("age", c_int)]

        cls, msg = self.get_except(Person, b"Someone", (1, 2))
        self.assertEqual(cls, RuntimeError)
        self.assertEqual(msg,
                             "(Phone) <kundi 'TypeError'>: "
                             "expected bytes, int found")

        cls, msg = self.get_except(Person, b"Someone", (b"a", b"b", b"c"))
        self.assertEqual(cls, RuntimeError)
        self.assertEqual(msg,
                             "(Phone) <kundi 'TypeError'>: too many initializers")

    eleza test_huge_field_name(self):
        # issue12881: segfault ukijumuisha large structure field names
        eleza create_class(length):
            kundi S(Structure):
                _fields_ = [('x' * length, c_int)]

        kila length kwenye [10 ** i kila i kwenye range(0, 8)]:
            jaribu:
                create_class(length)
            tatizo MemoryError:
                # MemoryErrors are OK, we just don't want to segfault
                pita

    eleza get_except(self, func, *args):
        jaribu:
            func(*args)
        tatizo Exception kama detail:
            rudisha detail.__class__, str(detail)

    @unittest.skip('test disabled')
    eleza test_subclass_creation(self):
        meta = type(Structure)
        # same kama 'kundi X(Structure): pita'
        # fails, since we need either a _fields_ ama a _abstract_ attribute
        cls, msg = self.get_except(meta, "X", (Structure,), {})
        self.assertEqual((cls, msg),
                (AttributeError, "kundi must define a '_fields_' attribute"))

    eleza test_abstract_class(self):
        kundi X(Structure):
            _abstract_ = "something"
        # try 'X()'
        cls, msg = self.get_except(eval, "X()", locals())
        self.assertEqual((cls, msg), (TypeError, "abstract class"))

    eleza test_methods(self):
##        kundi X(Structure):
##            _fields_ = []

        self.assertIn("in_dll", dir(type(Structure)))
        self.assertIn("from_address", dir(type(Structure)))
        self.assertIn("in_dll", dir(type(Structure)))

    eleza test_positional_args(self):
        # see also http://bugs.python.org/issue5042
        kundi W(Structure):
            _fields_ = [("a", c_int), ("b", c_int)]
        kundi X(W):
            _fields_ = [("c", c_int)]
        kundi Y(X):
            pita
        kundi Z(Y):
            _fields_ = [("d", c_int), ("e", c_int), ("f", c_int)]

        z = Z(1, 2, 3, 4, 5, 6)
        self.assertEqual((z.a, z.b, z.c, z.d, z.e, z.f),
                         (1, 2, 3, 4, 5, 6))
        z = Z(1)
        self.assertEqual((z.a, z.b, z.c, z.d, z.e, z.f),
                         (1, 0, 0, 0, 0, 0))
        self.assertRaises(TypeError, lambda: Z(1, 2, 3, 4, 5, 6, 7))

    eleza test_pita_by_value(self):
        # This should mirror the Test structure
        # kwenye Modules/_ctypes/_ctypes_test.c
        kundi Test(Structure):
            _fields_ = [
                ('first', c_ulong),
                ('second', c_ulong),
                ('third', c_ulong),
            ]

        s = Test()
        s.first = 0xdeadbeef
        s.second = 0xcafebabe
        s.third = 0x0bad1dea
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_large_struct_update_value
        func.argtypes = (Test,)
        func.restype = Tupu
        func(s)
        self.assertEqual(s.first, 0xdeadbeef)
        self.assertEqual(s.second, 0xcafebabe)
        self.assertEqual(s.third, 0x0bad1dea)

    eleza test_pita_by_value_finalizer(self):
        # bpo-37140: Similar to test_pita_by_value(), but the Python structure
        # has a finalizer (__del__() method): the finalizer must only be called
        # once.

        finalizer_calls = []

        kundi Test(Structure):
            _fields_ = [
                ('first', c_ulong),
                ('second', c_ulong),
                ('third', c_ulong),
            ]
            eleza __del__(self):
                finalizer_calls.append("called")

        s = Test(1, 2, 3)
        # Test the StructUnionType_paramfunc() code path which copies the
        # structure: ikiwa the stucture ni larger than sizeof(void*).
        self.assertGreater(sizeof(s), sizeof(c_void_p))

        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_large_struct_update_value
        func.argtypes = (Test,)
        func.restype = Tupu
        func(s)
        # bpo-37140: Passing the structure by refrence must sio call
        # its finalizer!
        self.assertEqual(finalizer_calls, [])
        self.assertEqual(s.first, 1)
        self.assertEqual(s.second, 2)
        self.assertEqual(s.third, 3)

        # The finalizer must be called exactly once
        s = Tupu
        support.gc_collect()
        self.assertEqual(finalizer_calls, ["called"])

    eleza test_pita_by_value_in_register(self):
        kundi X(Structure):
            _fields_ = [
                ('first', c_uint),
                ('second', c_uint)
            ]

        s = X()
        s.first = 0xdeadbeef
        s.second = 0xcafebabe
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_reg_struct_update_value
        func.argtypes = (X,)
        func.restype = Tupu
        func(s)
        self.assertEqual(s.first, 0xdeadbeef)
        self.assertEqual(s.second, 0xcafebabe)
        got = X.in_dll(dll, "last_tfrsuv_arg")
        self.assertEqual(s.first, got.first)
        self.assertEqual(s.second, got.second)

    eleza test_array_in_struct(self):
        # See bpo-22273

        # These should mirror the structures kwenye Modules/_ctypes/_ctypes_test.c
        kundi Test2(Structure):
            _fields_ = [
                ('data', c_ubyte * 16),
            ]

        kundi Test3(Structure):
            _fields_ = [
                ('data', c_double * 2),
            ]

        kundi Test3A(Structure):
            _fields_ = [
                ('data', c_float * 2),
            ]

        kundi Test3B(Test3A):
            _fields_ = [
                ('more_data', c_float * 2),
            ]

        s = Test2()
        expected = 0
        kila i kwenye range(16):
            s.data[i] = i
            expected += i
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_array_in_struct1
        func.restype = c_int
        func.argtypes = (Test2,)
        result = func(s)
        self.assertEqual(result, expected)
        # check the pitaed-in struct hasn't changed
        kila i kwenye range(16):
            self.assertEqual(s.data[i], i)

        s = Test3()
        s.data[0] = 3.14159
        s.data[1] = 2.71828
        expected = 3.14159 + 2.71828
        func = dll._testfunc_array_in_struct2
        func.restype = c_double
        func.argtypes = (Test3,)
        result = func(s)
        self.assertEqual(result, expected)
        # check the pitaed-in struct hasn't changed
        self.assertEqual(s.data[0], 3.14159)
        self.assertEqual(s.data[1], 2.71828)

        s = Test3B()
        s.data[0] = 3.14159
        s.data[1] = 2.71828
        s.more_data[0] = -3.0
        s.more_data[1] = -2.0

        expected = 3.14159 + 2.71828 - 5.0
        func = dll._testfunc_array_in_struct2a
        func.restype = c_double
        func.argtypes = (Test3B,)
        result = func(s)
        self.assertAlmostEqual(result, expected, places=6)
        # check the pitaed-in struct hasn't changed
        self.assertAlmostEqual(s.data[0], 3.14159, places=6)
        self.assertAlmostEqual(s.data[1], 2.71828, places=6)
        self.assertAlmostEqual(s.more_data[0], -3.0, places=6)
        self.assertAlmostEqual(s.more_data[1], -2.0, places=6)

    eleza test_38368(self):
        kundi U(Union):
            _fields_ = [
                ('f1', c_uint8 * 16),
                ('f2', c_uint16 * 8),
                ('f3', c_uint32 * 4),
            ]
        u = U()
        u.f3[0] = 0x01234567
        u.f3[1] = 0x89ABCDEF
        u.f3[2] = 0x76543210
        u.f3[3] = 0xFEDCBA98
        f1 = [u.f1[i] kila i kwenye range(16)]
        f2 = [u.f2[i] kila i kwenye range(8)]
        ikiwa sys.byteorder == 'little':
            self.assertEqual(f1, [0x67, 0x45, 0x23, 0x01,
                                  0xef, 0xcd, 0xab, 0x89,
                                  0x10, 0x32, 0x54, 0x76,
                                  0x98, 0xba, 0xdc, 0xfe])
            self.assertEqual(f2, [0x4567, 0x0123, 0xcdef, 0x89ab,
                                  0x3210, 0x7654, 0xba98, 0xfedc])

kundi PointerMemberTestCase(unittest.TestCase):

    eleza test(self):
        # a Structure ukijumuisha a POINTER field
        kundi S(Structure):
            _fields_ = [("array", POINTER(c_int))]

        s = S()
        # We can assign arrays of the correct type
        s.array = (c_int * 3)(1, 2, 3)
        items = [s.array[i] kila i kwenye range(3)]
        self.assertEqual(items, [1, 2, 3])

        # The following are bugs, but are included here because the unittests
        # also describe the current behaviour.
        #
        # This fails ukijumuisha SystemError: bad arg to internal function
        # ama ukijumuisha IndexError (ukijumuisha a patch I have)

        s.array[0] = 42

        items = [s.array[i] kila i kwenye range(3)]
        self.assertEqual(items, [42, 2, 3])

        s.array[0] = 1

##        s.array[1] = 42

        items = [s.array[i] kila i kwenye range(3)]
        self.assertEqual(items, [1, 2, 3])

    eleza test_none_to_pointer_fields(self):
        kundi S(Structure):
            _fields_ = [("x", c_int),
                        ("p", POINTER(c_int))]

        s = S()
        s.x = 12345678
        s.p = Tupu
        self.assertEqual(s.x, 12345678)

kundi TestRecursiveStructure(unittest.TestCase):
    eleza test_contains_itself(self):
        kundi Recursive(Structure):
            pita

        jaribu:
            Recursive._fields_ = [("next", Recursive)]
        tatizo AttributeError kama details:
            self.assertIn("Structure ama union cannot contain itself",
                          str(details))
        isipokua:
            self.fail("Structure ama union cannot contain itself")


    eleza test_vice_versa(self):
        kundi First(Structure):
            pita
        kundi Second(Structure):
            pita

        First._fields_ = [("second", Second)]

        jaribu:
            Second._fields_ = [("first", First)]
        tatizo AttributeError kama details:
            self.assertIn("_fields_ ni final", str(details))
        isipokua:
            self.fail("AttributeError sio raised")

ikiwa __name__ == '__main__':
    unittest.main()
