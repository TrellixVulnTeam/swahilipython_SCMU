agiza unittest, sys

kutoka ctypes agiza *
agiza _ctypes_test

ctype_types = [c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint,
                 c_long, c_ulong, c_longlong, c_ulonglong, c_double, c_float]
python_types = [int, int, int, int, int, int,
                int, int, int, int, float, float]

kundi PointersTestCase(unittest.TestCase):

    eleza test_pointer_crash(self):

        kundi A(POINTER(c_ulong)):
            pita

        POINTER(c_ulong)(c_ulong(22))
        # Pointer can't set contents: has no _type_
        self.assertRaises(TypeError, A, c_ulong(33))

    eleza test_pita_pointers(self):
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_p_p
        ikiwa sizeof(c_longlong) == sizeof(c_void_p):
            func.restype = c_longlong
        isipokua:
            func.restype = c_long

        i = c_int(12345678)
##        func.argtypes = (POINTER(c_int),)
        address = func(byref(i))
        self.assertEqual(c_int.from_address(address).value, 12345678)

        func.restype = POINTER(c_int)
        res = func(pointer(i))
        self.assertEqual(res.contents.value, 12345678)
        self.assertEqual(res[0], 12345678)

    eleza test_change_pointers(self):
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_p_p

        i = c_int(87654)
        func.restype = POINTER(c_int)
        func.argtypes = (POINTER(c_int),)

        res = func(pointer(i))
        self.assertEqual(res[0], 87654)
        self.assertEqual(res.contents.value, 87654)

        # C code: *res = 54345
        res[0] = 54345
        self.assertEqual(i.value, 54345)

        # C code:
        #   int x = 12321;
        #   res = &x
        x = c_int(12321)
        res.contents = x
        self.assertEqual(i.value, 54345)

        x.value = -99
        self.assertEqual(res.contents.value, -99)

    eleza test_callbacks_with_pointers(self):
        # a function type receiving a pointer
        PROTOTYPE = CFUNCTYPE(c_int, POINTER(c_int))

        self.result = []

        eleza func(arg):
            kila i kwenye range(10):
##                andika arg[i],
                self.result.append(arg[i])
##            andika
            rudisha 0
        callback = PROTOTYPE(func)

        dll = CDLL(_ctypes_test.__file__)
        # This function expects a function pointer,
        # na calls this ukijumuisha an integer pointer kama parameter.
        # The int pointer points to a table containing the numbers 1..10
        doit = dll._testfunc_callback_with_pointer

##        i = c_int(42)
##        callback(byref(i))
##        self.assertEqual(i.value, 84)

        doit(callback)
##        andika self.result
        doit(callback)
##        andika self.result

    eleza test_basics(self):
        kutoka operator agiza delitem
        kila ct, pt kwenye zip(ctype_types, python_types):
            i = ct(42)
            p = pointer(i)
##            andika type(p.contents), ct
            self.assertIs(type(p.contents), ct)
            # p.contents ni the same kama p[0]
##            andika p.contents
##            self.assertEqual(p.contents, 42)
##            self.assertEqual(p[0], 42)

            self.assertRaises(TypeError, delitem, p, 0)

    eleza test_from_address(self):
        kutoka array agiza array
        a = array('i', [100, 200, 300, 400, 500])
        addr = a.buffer_info()[0]

        p = POINTER(POINTER(c_int))
##        andika dir(p)
##        andika p.from_address
##        andika p.from_address(addr)[0][0]

    eleza test_other(self):
        kundi Table(Structure):
            _fields_ = [("a", c_int),
                        ("b", c_int),
                        ("c", c_int)]

        pt = pointer(Table(1, 2, 3))

        self.assertEqual(pt.contents.a, 1)
        self.assertEqual(pt.contents.b, 2)
        self.assertEqual(pt.contents.c, 3)

        pt.contents.c = 33

        kutoka ctypes agiza _pointer_type_cache
        toa _pointer_type_cache[Table]

    eleza test_basic(self):
        p = pointer(c_int(42))
        # Although a pointer can be indexed, it has no length
        self.assertRaises(TypeError, len, p)
        self.assertEqual(p[0], 42)
        self.assertEqual(p[0:1], [42])
        self.assertEqual(p.contents.value, 42)

    eleza test_charpp(self):
        """Test that a character pointer-to-pointer ni correctly pitaed"""
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_c_p_p
        func.restype = c_char_p
        argv = (c_char_p * 2)()
        argc = c_int( 2 )
        argv[0] = b'hello'
        argv[1] = b'world'
        result = func( byref(argc), argv )
        self.assertEqual(result, b'world')

    eleza test_bug_1467852(self):
        # http://sourceforge.net/tracker/?func=detail&atid=532154&aid=1467852&group_id=71702
        x = c_int(5)
        dummy = []
        kila i kwenye range(32000):
            dummy.append(c_int(i))
        y = c_int(6)
        p = pointer(x)
        pp = pointer(p)
        q = pointer(y)
        pp[0] = q         # <==
        self.assertEqual(p[0], 6)
    eleza test_c_void_p(self):
        # http://sourceforge.net/tracker/?func=detail&aid=1518190&group_id=5470&atid=105470
        ikiwa sizeof(c_void_p) == 4:
            self.assertEqual(c_void_p(0xFFFFFFFF).value,
                                 c_void_p(-1).value)
            self.assertEqual(c_void_p(0xFFFFFFFFFFFFFFFF).value,
                                 c_void_p(-1).value)
        lasivyo sizeof(c_void_p) == 8:
            self.assertEqual(c_void_p(0xFFFFFFFF).value,
                                 0xFFFFFFFF)
            self.assertEqual(c_void_p(0xFFFFFFFFFFFFFFFF).value,
                                 c_void_p(-1).value)
            self.assertEqual(c_void_p(0xFFFFFFFFFFFFFFFFFFFFFFFF).value,
                                 c_void_p(-1).value)

        self.assertRaises(TypeError, c_void_p, 3.14) # make sure floats are NOT accepted
        self.assertRaises(TypeError, c_void_p, object()) # nor other objects

    eleza test_pointers_bool(self):
        # NULL pointers have a boolean Uongo value, non-NULL pointers Kweli.
        self.assertEqual(bool(POINTER(c_int)()), Uongo)
        self.assertEqual(bool(pointer(c_int())), Kweli)

        self.assertEqual(bool(CFUNCTYPE(Tupu)(0)), Uongo)
        self.assertEqual(bool(CFUNCTYPE(Tupu)(42)), Kweli)

        # COM methods are boolean Kweli:
        ikiwa sys.platform == "win32":
            mth = WINFUNCTYPE(Tupu)(42, "name", (), Tupu)
            self.assertEqual(bool(mth), Kweli)

    eleza test_pointer_type_name(self):
        LargeNamedType = type('T' * 2 ** 25, (Structure,), {})
        self.assertKweli(POINTER(LargeNamedType))

        # to sio leak references, we must clean _pointer_type_cache
        kutoka ctypes agiza _pointer_type_cache
        toa _pointer_type_cache[LargeNamedType]

    eleza test_pointer_type_str_name(self):
        large_string = 'T' * 2 ** 25
        P = POINTER(large_string)
        self.assertKweli(P)

        # to sio leak references, we must clean _pointer_type_cache
        kutoka ctypes agiza _pointer_type_cache
        toa _pointer_type_cache[id(P)]

    eleza test_abstract(self):
        kutoka ctypes agiza _Pointer

        self.assertRaises(TypeError, _Pointer.set_type, 42)


ikiwa __name__ == '__main__':
    unittest.main()
