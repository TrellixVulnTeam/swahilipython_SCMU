agiza functools
agiza unittest
kutoka ctypes agiza *
kutoka ctypes.test agiza need_symbol
agiza _ctypes_test

kundi Callbacks(unittest.TestCase):
    functype = CFUNCTYPE

##    eleza tearDown(self):
##        agiza gc
##        gc.collect()

    eleza callback(self, *args):
        self.got_args = args
        rudisha args[-1]

    eleza check_type(self, typ, arg):
        PROTO = self.functype.__func__(typ, typ)
        result = PROTO(self.callback)(arg)
        ikiwa typ == c_float:
            self.assertAlmostEqual(result, arg, places=5)
        isipokua:
            self.assertEqual(self.got_args, (arg,))
            self.assertEqual(result, arg)

        PROTO = self.functype.__func__(typ, c_byte, typ)
        result = PROTO(self.callback)(-3, arg)
        ikiwa typ == c_float:
            self.assertAlmostEqual(result, arg, places=5)
        isipokua:
            self.assertEqual(self.got_args, (-3, arg))
            self.assertEqual(result, arg)

    ################

    eleza test_byte(self):
        self.check_type(c_byte, 42)
        self.check_type(c_byte, -42)

    eleza test_ubyte(self):
        self.check_type(c_ubyte, 42)

    eleza test_short(self):
        self.check_type(c_short, 42)
        self.check_type(c_short, -42)

    eleza test_ushort(self):
        self.check_type(c_ushort, 42)

    eleza test_int(self):
        self.check_type(c_int, 42)
        self.check_type(c_int, -42)

    eleza test_uint(self):
        self.check_type(c_uint, 42)

    eleza test_long(self):
        self.check_type(c_long, 42)
        self.check_type(c_long, -42)

    eleza test_ulong(self):
        self.check_type(c_ulong, 42)

    eleza test_longlong(self):
        self.check_type(c_longlong, 42)
        self.check_type(c_longlong, -42)

    eleza test_ulonglong(self):
        self.check_type(c_ulonglong, 42)

    eleza test_float(self):
        # only almost equal: double -> float -> double
        agiza math
        self.check_type(c_float, math.e)
        self.check_type(c_float, -math.e)

    eleza test_double(self):
        self.check_type(c_double, 3.14)
        self.check_type(c_double, -3.14)

    eleza test_longdouble(self):
        self.check_type(c_longdouble, 3.14)
        self.check_type(c_longdouble, -3.14)

    eleza test_char(self):
        self.check_type(c_char, b"x")
        self.check_type(c_char, b"a")

    # disabled: would now (correctly) ashiria a RuntimeWarning about
    # a memory leak.  A callback function cansio rudisha a non-integral
    # C type without causing a memory leak.
    @unittest.skip('test disabled')
    eleza test_char_p(self):
        self.check_type(c_char_p, "abc")
        self.check_type(c_char_p, "def")

    eleza test_pyobject(self):
        o = ()
        kutoka sys agiza getrefcount kama grc
        kila o kwenye (), [], object():
            initial = grc(o)
            # This call leaks a reference to 'o'...
            self.check_type(py_object, o)
            before = grc(o)
            # ...but this call doesn't leak any more.  Where ni the refcount?
            self.check_type(py_object, o)
            after = grc(o)
            self.assertEqual((after, o), (before, o))

    eleza test_unsupported_restype_1(self):
        # Only "fundamental" result types are supported kila callback
        # functions, the type must have a non-NULL stgdict->setfunc.
        # POINTER(c_double), kila example, ni sio supported.

        prototype = self.functype.__func__(POINTER(c_double))
        # The type ni checked when the prototype ni called
        self.assertRaises(TypeError, prototype, lambda: Tupu)

    eleza test_unsupported_restype_2(self):
        prototype = self.functype.__func__(object)
        self.assertRaises(TypeError, prototype, lambda: Tupu)

    eleza test_issue_7959(self):
        proto = self.functype.__func__(Tupu)

        kundi X(object):
            eleza func(self): pita
            eleza __init__(self):
                self.v = proto(self.func)

        agiza gc
        kila i kwenye range(32):
            X()
        gc.collect()
        live = [x kila x kwenye gc.get_objects()
                ikiwa isinstance(x, X)]
        self.assertEqual(len(live), 0)

    eleza test_issue12483(self):
        agiza gc
        kundi Nasty:
            eleza __del__(self):
                gc.collect()
        CFUNCTYPE(Tupu)(lambda x=Nasty(): Tupu)


@need_symbol('WINFUNCTYPE')
kundi StdcallCallbacks(Callbacks):
    jaribu:
        functype = WINFUNCTYPE
    tatizo NameError:
        pita

################################################################

kundi SampleCallbacksTestCase(unittest.TestCase):

    eleza test_integrate(self):
        # Derived kutoka some then non-working code, posted by David Foster
        dll = CDLL(_ctypes_test.__file__)

        # The function prototype called by 'integrate': double func(double);
        CALLBACK = CFUNCTYPE(c_double, c_double)

        # The integrate function itself, exposed kutoka the _ctypes_test dll
        integrate = dll.integrate
        integrate.argtypes = (c_double, c_double, CALLBACK, c_long)
        integrate.restype = c_double

        eleza func(x):
            rudisha x**2

        result = integrate(0.0, 1.0, CALLBACK(func), 10)
        diff = abs(result - 1./3.)

        self.assertLess(diff, 0.01, "%s sio less than 0.01" % diff)

    eleza test_issue_8959_a(self):
        kutoka ctypes.util agiza find_library
        libc_path = find_library("c")
        ikiwa sio libc_path:
            self.skipTest('could sio find libc')
        libc = CDLL(libc_path)

        @CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))
        eleza cmp_func(a, b):
            rudisha a[0] - b[0]

        array = (c_int * 5)(5, 1, 99, 7, 33)

        libc.qsort(array, len(array), sizeof(c_int), cmp_func)
        self.assertEqual(array[:], [1, 5, 7, 33, 99])

    @need_symbol('WINFUNCTYPE')
    eleza test_issue_8959_b(self):
        kutoka ctypes.wintypes agiza BOOL, HWND, LPARAM
        global windowCount
        windowCount = 0

        @WINFUNCTYPE(BOOL, HWND, LPARAM)
        eleza EnumWindowsCallbackFunc(hwnd, lParam):
            global windowCount
            windowCount += 1
            rudisha Kweli #Allow windows to keep enumerating

        windll.user32.EnumWindows(EnumWindowsCallbackFunc, 0)

    eleza test_callback_register_int(self):
        # Issue #8275: buggy handling of callback args under Win64
        # NOTE: should be run on release builds kama well
        dll = CDLL(_ctypes_test.__file__)
        CALLBACK = CFUNCTYPE(c_int, c_int, c_int, c_int, c_int, c_int)
        # All this function does ni call the callback ukijumuisha its args squared
        func = dll._testfunc_cbk_reg_int
        func.argtypes = (c_int, c_int, c_int, c_int, c_int, CALLBACK)
        func.restype = c_int

        eleza callback(a, b, c, d, e):
            rudisha a + b + c + d + e

        result = func(2, 3, 4, 5, 6, CALLBACK(callback))
        self.assertEqual(result, callback(2*2, 3*3, 4*4, 5*5, 6*6))

    eleza test_callback_register_double(self):
        # Issue #8275: buggy handling of callback args under Win64
        # NOTE: should be run on release builds kama well
        dll = CDLL(_ctypes_test.__file__)
        CALLBACK = CFUNCTYPE(c_double, c_double, c_double, c_double,
                             c_double, c_double)
        # All this function does ni call the callback ukijumuisha its args squared
        func = dll._testfunc_cbk_reg_double
        func.argtypes = (c_double, c_double, c_double,
                         c_double, c_double, CALLBACK)
        func.restype = c_double

        eleza callback(a, b, c, d, e):
            rudisha a + b + c + d + e

        result = func(1.1, 2.2, 3.3, 4.4, 5.5, CALLBACK(callback))
        self.assertEqual(result,
                         callback(1.1*1.1, 2.2*2.2, 3.3*3.3, 4.4*4.4, 5.5*5.5))

    eleza test_callback_large_struct(self):
        kundi Check: pita

        # This should mirror the structure kwenye Modules/_ctypes/_ctypes_test.c
        kundi X(Structure):
            _fields_ = [
                ('first', c_ulong),
                ('second', c_ulong),
                ('third', c_ulong),
            ]

        eleza callback(check, s):
            check.first = s.first
            check.second = s.second
            check.third = s.third
            # See issue #29565.
            # The structure should be pitaed by value, so
            # any changes to it should sio be reflected kwenye
            # the value pitaed
            s.first = s.second = s.third = 0x0badf00d

        check = Check()
        s = X()
        s.first = 0xdeadbeef
        s.second = 0xcafebabe
        s.third = 0x0bad1dea

        CALLBACK = CFUNCTYPE(Tupu, X)
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_cbk_large_struct
        func.argtypes = (X, CALLBACK)
        func.restype = Tupu
        # the function just calls the callback ukijumuisha the pitaed structure
        func(s, CALLBACK(functools.partial(callback, check)))
        self.assertEqual(check.first, s.first)
        self.assertEqual(check.second, s.second)
        self.assertEqual(check.third, s.third)
        self.assertEqual(check.first, 0xdeadbeef)
        self.assertEqual(check.second, 0xcafebabe)
        self.assertEqual(check.third, 0x0bad1dea)
        # See issue #29565.
        # Ensure that the original struct ni unchanged.
        self.assertEqual(s.first, check.first)
        self.assertEqual(s.second, check.second)
        self.assertEqual(s.third, check.third)

################################################################

ikiwa __name__ == '__main__':
    unittest.main()
