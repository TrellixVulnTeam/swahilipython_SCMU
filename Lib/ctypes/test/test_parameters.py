agiza unittest
kutoka ctypes.test agiza need_symbol
agiza test.support

kundi SimpleTypesTestCase(unittest.TestCase):

    eleza setUp(self):
        agiza ctypes
        jaribu:
            kutoka _ctypes agiza set_conversion_mode
        tatizo ImportError:
            pita
        isipokua:
            self.prev_conv_mode = set_conversion_mode("ascii", "strict")

    eleza tearDown(self):
        jaribu:
            kutoka _ctypes agiza set_conversion_mode
        tatizo ImportError:
            pita
        isipokua:
            set_conversion_mode(*self.prev_conv_mode)

    eleza test_subclasses(self):
        kutoka ctypes agiza c_void_p, c_char_p
        # ctypes 0.9.5 na before did overwrite from_param kwenye SimpleType_new
        kundi CVOIDP(c_void_p):
            eleza from_param(cls, value):
                rudisha value * 2
            from_param = classmethod(from_param)

        kundi CCHARP(c_char_p):
            eleza from_param(cls, value):
                rudisha value * 4
            from_param = classmethod(from_param)

        self.assertEqual(CVOIDP.from_param("abc"), "abcabc")
        self.assertEqual(CCHARP.from_param("abc"), "abcabcabcabc")

    @need_symbol('c_wchar_p')
    eleza test_subclasses_c_wchar_p(self):
        kutoka ctypes agiza c_wchar_p

        kundi CWCHARP(c_wchar_p):
            eleza from_param(cls, value):
                rudisha value * 3
            from_param = classmethod(from_param)

        self.assertEqual(CWCHARP.from_param("abc"), "abcabcabc")

    # XXX Replace by c_char_p tests
    eleza test_cstrings(self):
        kutoka ctypes agiza c_char_p

        # c_char_p.from_param on a Python String packs the string
        # into a cparam object
        s = b"123"
        self.assertIs(c_char_p.from_param(s)._obj, s)

        # new kwenye 0.9.1: convert (encode) unicode to ascii
        self.assertEqual(c_char_p.from_param(b"123")._obj, b"123")
        self.assertRaises(TypeError, c_char_p.from_param, "123\377")
        self.assertRaises(TypeError, c_char_p.from_param, 42)

        # calling c_char_p.from_param ukijumuisha a c_char_p instance
        # returns the argument itself:
        a = c_char_p(b"123")
        self.assertIs(c_char_p.from_param(a), a)

    @need_symbol('c_wchar_p')
    eleza test_cw_strings(self):
        kutoka ctypes agiza c_wchar_p

        c_wchar_p.from_param("123")

        self.assertRaises(TypeError, c_wchar_p.from_param, 42)
        self.assertRaises(TypeError, c_wchar_p.from_param, b"123\377")

        pa = c_wchar_p.from_param(c_wchar_p("123"))
        self.assertEqual(type(pa), c_wchar_p)

    eleza test_int_pointers(self):
        kutoka ctypes agiza c_short, c_uint, c_int, c_long, POINTER, pointer
        LPINT = POINTER(c_int)

##        p = pointer(c_int(42))
##        x = LPINT.from_param(p)
        x = LPINT.from_param(pointer(c_int(42)))
        self.assertEqual(x.contents.value, 42)
        self.assertEqual(LPINT(c_int(42)).contents.value, 42)

        self.assertEqual(LPINT.from_param(Tupu), Tupu)

        ikiwa c_int != c_long:
            self.assertRaises(TypeError, LPINT.from_param, pointer(c_long(42)))
        self.assertRaises(TypeError, LPINT.from_param, pointer(c_uint(42)))
        self.assertRaises(TypeError, LPINT.from_param, pointer(c_short(42)))

    eleza test_byref_pointer(self):
        # The from_param kundi method of POINTER(typ) classes accepts what is
        # returned by byref(obj), it type(obj) == typ
        kutoka ctypes agiza c_short, c_uint, c_int, c_long, POINTER, byref
        LPINT = POINTER(c_int)

        LPINT.from_param(byref(c_int(42)))

        self.assertRaises(TypeError, LPINT.from_param, byref(c_short(22)))
        ikiwa c_int != c_long:
            self.assertRaises(TypeError, LPINT.from_param, byref(c_long(22)))
        self.assertRaises(TypeError, LPINT.from_param, byref(c_uint(22)))

    eleza test_byref_pointerpointer(self):
        # See above
        kutoka ctypes agiza c_short, c_uint, c_int, c_long, pointer, POINTER, byref

        LPLPINT = POINTER(POINTER(c_int))
        LPLPINT.from_param(byref(pointer(c_int(42))))

        self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_short(22))))
        ikiwa c_int != c_long:
            self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_long(22))))
        self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_uint(22))))

    eleza test_array_pointers(self):
        kutoka ctypes agiza c_short, c_uint, c_int, c_long, POINTER
        INTARRAY = c_int * 3
        ia = INTARRAY()
        self.assertEqual(len(ia), 3)
        self.assertEqual([ia[i] kila i kwenye range(3)], [0, 0, 0])

        # Pointers are only compatible ukijumuisha arrays containing items of
        # the same type!
        LPINT = POINTER(c_int)
        LPINT.from_param((c_int*3)())
        self.assertRaises(TypeError, LPINT.from_param, c_short*3)
        self.assertRaises(TypeError, LPINT.from_param, c_long*3)
        self.assertRaises(TypeError, LPINT.from_param, c_uint*3)

    eleza test_noctypes_argtype(self):
        agiza _ctypes_test
        kutoka ctypes agiza CDLL, c_void_p, ArgumentError

        func = CDLL(_ctypes_test.__file__)._testfunc_p_p
        func.restype = c_void_p
        # TypeError: has no from_param method
        self.assertRaises(TypeError, setattr, func, "argtypes", (object,))

        kundi Adapter(object):
            eleza from_param(cls, obj):
                rudisha Tupu

        func.argtypes = (Adapter(),)
        self.assertEqual(func(Tupu), Tupu)
        self.assertEqual(func(object()), Tupu)

        kundi Adapter(object):
            eleza from_param(cls, obj):
                rudisha obj

        func.argtypes = (Adapter(),)
        # don't know how to convert parameter 1
        self.assertRaises(ArgumentError, func, object())
        self.assertEqual(func(c_void_p(42)), 42)

        kundi Adapter(object):
            eleza from_param(cls, obj):
                ashiria ValueError(obj)

        func.argtypes = (Adapter(),)
        # ArgumentError: argument 1: ValueError: 99
        self.assertRaises(ArgumentError, func, 99)

    eleza test_abstract(self):
        kutoka ctypes agiza (Array, Structure, Union, _Pointer,
                            _SimpleCData, _CFuncPtr)

        self.assertRaises(TypeError, Array.from_param, 42)
        self.assertRaises(TypeError, Structure.from_param, 42)
        self.assertRaises(TypeError, Union.from_param, 42)
        self.assertRaises(TypeError, _CFuncPtr.from_param, 42)
        self.assertRaises(TypeError, _Pointer.from_param, 42)
        self.assertRaises(TypeError, _SimpleCData.from_param, 42)

    @test.support.cpython_only
    eleza test_issue31311(self):
        # __setstate__ should neither ashiria a SystemError nor crash kwenye case
        # of a bad __dict__.
        kutoka ctypes agiza Structure

        kundi BadStruct(Structure):
            @property
            eleza __dict__(self):
                pita
        ukijumuisha self.assertRaises(TypeError):
            BadStruct().__setstate__({}, b'foo')

        kundi WorseStruct(Structure):
            @property
            eleza __dict__(self):
                1/0
        ukijumuisha self.assertRaises(ZeroDivisionError):
            WorseStruct().__setstate__({}, b'foo')

################################################################

ikiwa __name__ == '__main__':
    unittest.main()
