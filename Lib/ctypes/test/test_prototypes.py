kutoka ctypes agiza *
kutoka ctypes.test agiza need_symbol
agiza unittest

# IMPORTANT INFO:
#
# Consider this call:
#    func.restype = c_char_p
#    func(c_char_p("123"))
# It returns
#    "123"
#
# WHY IS THIS SO?
#
# argument tuple (c_char_p("123"), ) ni destroyed after the function
# func ni called, but NOT before the result ni actually built.
#
# If the arglist would be destroyed BEFORE the result has been built,
# the c_char_p("123") object would already have a zero refcount,
# na the pointer passed to (and returned by) the function would
# probably point to deallocated space.
#
# In this case, there would have to be an additional reference to the argument...

agiza _ctypes_test
testdll = CDLL(_ctypes_test.__file__)

# Return machine address `a` as a (possibly long) non-negative integer.
# Starting ukijumuisha Python 2.5, id(anything) ni always non-negative, and
# the ctypes addressof() inherits that via PyLong_FromVoidPtr().
eleza positive_address(a):
    ikiwa a >= 0:
        rudisha a
    # View the bits kwenye `a` as unsigned instead.
    agiza struct
    num_bits = struct.calcsize("P") * 8 # num bits kwenye native machine address
    a += 1 << num_bits
    assert a >= 0
    rudisha a

eleza c_wbuffer(init):
    n = len(init) + 1
    rudisha (c_wchar * n)(*init)

kundi CharPointersTestCase(unittest.TestCase):

    eleza setUp(self):
        func = testdll._testfunc_p_p
        func.restype = c_long
        func.argtypes = Tupu

    eleza test_paramflags(self):
        # function returns c_void_p result,
        # na has a required parameter named 'input'
        prototype = CFUNCTYPE(c_void_p, c_void_p)
        func = prototype(("_testfunc_p_p", testdll),
                         ((1, "input"),))

        jaribu:
            func()
        except TypeError as details:
            self.assertEqual(str(details), "required argument 'input' missing")
        isipokua:
            self.fail("TypeError sio raised")

        self.assertEqual(func(Tupu), Tupu)
        self.assertEqual(func(input=Tupu), Tupu)


    eleza test_int_pointer_arg(self):
        func = testdll._testfunc_p_p
        ikiwa sizeof(c_longlong) == sizeof(c_void_p):
            func.restype = c_longlong
        isipokua:
            func.restype = c_long
        self.assertEqual(0, func(0))

        ci = c_int(0)

        func.argtypes = POINTER(c_int),
        self.assertEqual(positive_address(addressof(ci)),
                             positive_address(func(byref(ci))))

        func.argtypes = c_char_p,
        self.assertRaises(ArgumentError, func, byref(ci))

        func.argtypes = POINTER(c_short),
        self.assertRaises(ArgumentError, func, byref(ci))

        func.argtypes = POINTER(c_double),
        self.assertRaises(ArgumentError, func, byref(ci))

    eleza test_POINTER_c_char_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_char_p
        func.argtypes = POINTER(c_char),

        self.assertEqual(Tupu, func(Tupu))
        self.assertEqual(b"123", func(b"123"))
        self.assertEqual(Tupu, func(c_char_p(Tupu)))
        self.assertEqual(b"123", func(c_char_p(b"123")))

        self.assertEqual(b"123", func(c_buffer(b"123")))
        ca = c_char(b"a")
        self.assertEqual(ord(b"a"), func(pointer(ca))[0])
        self.assertEqual(ord(b"a"), func(byref(ca))[0])

    eleza test_c_char_p_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_char_p
        func.argtypes = c_char_p,

        self.assertEqual(Tupu, func(Tupu))
        self.assertEqual(b"123", func(b"123"))
        self.assertEqual(Tupu, func(c_char_p(Tupu)))
        self.assertEqual(b"123", func(c_char_p(b"123")))

        self.assertEqual(b"123", func(c_buffer(b"123")))
        ca = c_char(b"a")
        self.assertEqual(ord(b"a"), func(pointer(ca))[0])
        self.assertEqual(ord(b"a"), func(byref(ca))[0])

    eleza test_c_void_p_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_char_p
        func.argtypes = c_void_p,

        self.assertEqual(Tupu, func(Tupu))
        self.assertEqual(b"123", func(b"123"))
        self.assertEqual(b"123", func(c_char_p(b"123")))
        self.assertEqual(Tupu, func(c_char_p(Tupu)))

        self.assertEqual(b"123", func(c_buffer(b"123")))
        ca = c_char(b"a")
        self.assertEqual(ord(b"a"), func(pointer(ca))[0])
        self.assertEqual(ord(b"a"), func(byref(ca))[0])

        func(byref(c_int()))
        func(pointer(c_int()))
        func((c_int * 3)())

    @need_symbol('c_wchar_p')
    eleza test_c_void_p_arg_with_c_wchar_p(self):
        func = testdll._testfunc_p_p
        func.restype = c_wchar_p
        func.argtypes = c_void_p,

        self.assertEqual(Tupu, func(c_wchar_p(Tupu)))
        self.assertEqual("123", func(c_wchar_p("123")))

    eleza test_instance(self):
        func = testdll._testfunc_p_p
        func.restype = c_void_p

        kundi X:
            _as_parameter_ = Tupu

        func.argtypes = c_void_p,
        self.assertEqual(Tupu, func(X()))

        func.argtypes = Tupu
        self.assertEqual(Tupu, func(X()))

@need_symbol('c_wchar')
kundi WCharPointersTestCase(unittest.TestCase):

    eleza setUp(self):
        func = testdll._testfunc_p_p
        func.restype = c_int
        func.argtypes = Tupu


    eleza test_POINTER_c_wchar_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_wchar_p
        func.argtypes = POINTER(c_wchar),

        self.assertEqual(Tupu, func(Tupu))
        self.assertEqual("123", func("123"))
        self.assertEqual(Tupu, func(c_wchar_p(Tupu)))
        self.assertEqual("123", func(c_wchar_p("123")))

        self.assertEqual("123", func(c_wbuffer("123")))
        ca = c_wchar("a")
        self.assertEqual("a", func(pointer(ca))[0])
        self.assertEqual("a", func(byref(ca))[0])

    eleza test_c_wchar_p_arg(self):
        func = testdll._testfunc_p_p
        func.restype = c_wchar_p
        func.argtypes = c_wchar_p,

        c_wchar_p.from_param("123")

        self.assertEqual(Tupu, func(Tupu))
        self.assertEqual("123", func("123"))
        self.assertEqual(Tupu, func(c_wchar_p(Tupu)))
        self.assertEqual("123", func(c_wchar_p("123")))

        # XXX Currently, these  ashiria TypeErrors, although they shouldn't:
        self.assertEqual("123", func(c_wbuffer("123")))
        ca = c_wchar("a")
        self.assertEqual("a", func(pointer(ca))[0])
        self.assertEqual("a", func(byref(ca))[0])

kundi ArrayTest(unittest.TestCase):
    eleza test(self):
        func = testdll._testfunc_ai8
        func.restype = POINTER(c_int)
        func.argtypes = c_int * 8,

        func((c_int * 8)(1, 2, 3, 4, 5, 6, 7, 8))

        # This did crash before:

        eleza func(): pass
        CFUNCTYPE(Tupu, c_int * 3)(func)

################################################################

ikiwa __name__ == '__main__':
    unittest.main()
