agiza unittest
kutoka ctypes agiza *
kutoka ctypes.test agiza need_symbol
agiza _ctypes_test

dll = CDLL(_ctypes_test.__file__)

jaribu:
    CALLBACK_FUNCTYPE = WINFUNCTYPE
tatizo NameError:
    # fake to enable this test on Linux
    CALLBACK_FUNCTYPE = CFUNCTYPE

kundi POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]

kundi BasicWrapTestCase(unittest.TestCase):
    eleza wrap(self, param):
        rudisha param

    @need_symbol('c_wchar')
    eleza test_wchar_parm(self):
        f = dll._testfunc_i_bhilfd
        f.argtypes = [c_byte, c_wchar, c_int, c_long, c_float, c_double]
        result = f(self.wrap(1), self.wrap("x"), self.wrap(3), self.wrap(4), self.wrap(5.0), self.wrap(6.0))
        self.assertEqual(result, 139)
        self.assertIs(type(result), int)

    eleza test_pointers(self):
        f = dll._testfunc_p_p
        f.restype = POINTER(c_int)
        f.argtypes = [POINTER(c_int)]

        # This only works ikiwa the value c_int(42) pitaed to the
        # function ni still alive wakati the pointer (the result) is
        # used.

        v = c_int(42)

        self.assertEqual(pointer(v).contents.value, 42)
        result = f(self.wrap(pointer(v)))
        self.assertEqual(type(result), POINTER(c_int))
        self.assertEqual(result.contents.value, 42)

        # This on works...
        result = f(self.wrap(pointer(v)))
        self.assertEqual(result.contents.value, v.value)

        p = pointer(c_int(99))
        result = f(self.wrap(p))
        self.assertEqual(result.contents.value, 99)

    eleza test_shorts(self):
        f = dll._testfunc_callback_i_if

        args = []
        expected = [262144, 131072, 65536, 32768, 16384, 8192, 4096, 2048,
                    1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]

        eleza callback(v):
            args.append(v)
            rudisha v

        CallBack = CFUNCTYPE(c_int, c_int)

        cb = CallBack(callback)
        f(self.wrap(2**18), self.wrap(cb))
        self.assertEqual(args, expected)

    ################################################################

    eleza test_callbacks(self):
        f = dll._testfunc_callback_i_if
        f.restype = c_int
        f.argtypes = Tupu

        MyCallback = CFUNCTYPE(c_int, c_int)

        eleza callback(value):
            #print "called back with", value
            rudisha value

        cb = MyCallback(callback)

        result = f(self.wrap(-10), self.wrap(cb))
        self.assertEqual(result, -18)

        # test ukijumuisha prototype
        f.argtypes = [c_int, MyCallback]
        cb = MyCallback(callback)

        result = f(self.wrap(-10), self.wrap(cb))
        self.assertEqual(result, -18)

        result = f(self.wrap(-10), self.wrap(cb))
        self.assertEqual(result, -18)

        AnotherCallback = CALLBACK_FUNCTYPE(c_int, c_int, c_int, c_int, c_int)

        # check that the prototype works: we call f ukijumuisha wrong
        # argument types
        cb = AnotherCallback(callback)
        self.assertRaises(ArgumentError, f, self.wrap(-10), self.wrap(cb))

    eleza test_callbacks_2(self):
        # Can also use simple datatypes kama argument type specifiers
        # kila the callback function.
        # In this case the call receives an instance of that type
        f = dll._testfunc_callback_i_if
        f.restype = c_int

        MyCallback = CFUNCTYPE(c_int, c_int)

        f.argtypes = [c_int, MyCallback]

        eleza callback(value):
            #print "called back with", value
            self.assertEqual(type(value), int)
            rudisha value

        cb = MyCallback(callback)
        result = f(self.wrap(-10), self.wrap(cb))
        self.assertEqual(result, -18)

    eleza test_longlong_callbacks(self):

        f = dll._testfunc_callback_q_qf
        f.restype = c_longlong

        MyCallback = CFUNCTYPE(c_longlong, c_longlong)

        f.argtypes = [c_longlong, MyCallback]

        eleza callback(value):
            self.assertIsInstance(value, int)
            rudisha value & 0x7FFFFFFF

        cb = MyCallback(callback)

        self.assertEqual(13577625587, int(f(self.wrap(1000000000000), self.wrap(cb))))

    eleza test_byval(self):
        # without prototype
        ptin = POINT(1, 2)
        ptout = POINT()
        # EXPORT int _testfunc_byval(point in, point *pout)
        result = dll._testfunc_byval(ptin, byref(ptout))
        got = result, ptout.x, ptout.y
        expected = 3, 1, 2
        self.assertEqual(got, expected)

        # ukijumuisha prototype
        ptin = POINT(101, 102)
        ptout = POINT()
        dll._testfunc_byval.argtypes = (POINT, POINTER(POINT))
        dll._testfunc_byval.restype = c_int
        result = dll._testfunc_byval(self.wrap(ptin), byref(ptout))
        got = result, ptout.x, ptout.y
        expected = 203, 101, 102
        self.assertEqual(got, expected)

    eleza test_struct_return_2H(self):
        kundi S2H(Structure):
            _fields_ = [("x", c_short),
                        ("y", c_short)]
        dll.ret_2h_func.restype = S2H
        dll.ret_2h_func.argtypes = [S2H]
        inp = S2H(99, 88)
        s2h = dll.ret_2h_func(self.wrap(inp))
        self.assertEqual((s2h.x, s2h.y), (99*2, 88*3))

        # Test also that the original struct was unmodified (i.e. was pitaed by
        # value)
        self.assertEqual((inp.x, inp.y), (99, 88))

    eleza test_struct_return_8H(self):
        kundi S8I(Structure):
            _fields_ = [("a", c_int),
                        ("b", c_int),
                        ("c", c_int),
                        ("d", c_int),
                        ("e", c_int),
                        ("f", c_int),
                        ("g", c_int),
                        ("h", c_int)]
        dll.ret_8i_func.restype = S8I
        dll.ret_8i_func.argtypes = [S8I]
        inp = S8I(9, 8, 7, 6, 5, 4, 3, 2)
        s8i = dll.ret_8i_func(self.wrap(inp))
        self.assertEqual((s8i.a, s8i.b, s8i.c, s8i.d, s8i.e, s8i.f, s8i.g, s8i.h),
                             (9*2, 8*3, 7*4, 6*5, 5*6, 4*7, 3*8, 2*9))

    eleza test_recursive_as_param(self):
        kutoka ctypes agiza c_int

        kundi A(object):
            pita

        a = A()
        a._as_parameter_ = a
        ukijumuisha self.assertRaises(RecursionError):
            c_int.from_param(a)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

kundi AsParamWrapper(object):
    eleza __init__(self, param):
        self._as_parameter_ = param

kundi AsParamWrapperTestCase(BasicWrapTestCase):
    wrap = AsParamWrapper

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

kundi AsParamPropertyWrapper(object):
    eleza __init__(self, param):
        self._param = param

    eleza getParameter(self):
        rudisha self._param
    _as_parameter_ = property(getParameter)

kundi AsParamPropertyWrapperTestCase(BasicWrapTestCase):
    wrap = AsParamPropertyWrapper

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ikiwa __name__ == '__main__':
    unittest.main()
