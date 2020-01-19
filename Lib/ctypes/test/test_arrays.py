agiza unittest
kutoka test.support agiza bigmemtest, _2G
agiza sys
kutoka ctypes agiza *

kutoka ctypes.test agiza need_symbol

formats = "bBhHiIlLqQfd"

formats = c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint, \
          c_long, c_ulonglong, c_float, c_double, c_longdouble

kundi ArrayTestCase(unittest.TestCase):
    eleza test_simple(self):
        # create classes holding simple numeric types, na check
        # various properties.

        init = list(range(15, 25))

        kila fmt kwenye formats:
            alen = len(init)
            int_array = ARRAY(fmt, alen)

            ia = int_array(*init)
            # length of instance ok?
            self.assertEqual(len(ia), alen)

            # slot values ok?
            values = [ia[i] kila i kwenye range(alen)]
            self.assertEqual(values, init)

            # out-of-bounds accesses should be caught
            ukijumuisha self.assertRaises(IndexError): ia[alen]
            ukijumuisha self.assertRaises(IndexError): ia[-alen-1]

            # change the items
            kutoka operator agiza setitem
            new_values = list(range(42, 42+alen))
            [setitem(ia, n, new_values[n]) kila n kwenye range(alen)]
            values = [ia[i] kila i kwenye range(alen)]
            self.assertEqual(values, new_values)

            # are the items initialized to 0?
            ia = int_array()
            values = [ia[i] kila i kwenye range(alen)]
            self.assertEqual(values, [0] * alen)

            # Too many initializers should be caught
            self.assertRaises(IndexError, int_array, *range(alen*2))

        CharArray = ARRAY(c_char, 3)

        ca = CharArray(b"a", b"b", b"c")

        # Should this work? It doesn't:
        # CharArray("abc")
        self.assertRaises(TypeError, CharArray, "abc")

        self.assertEqual(ca[0], b"a")
        self.assertEqual(ca[1], b"b")
        self.assertEqual(ca[2], b"c")
        self.assertEqual(ca[-3], b"a")
        self.assertEqual(ca[-2], b"b")
        self.assertEqual(ca[-1], b"c")

        self.assertEqual(len(ca), 3)

        # cannot delete items
        kutoka operator agiza delitem
        self.assertRaises(TypeError, delitem, ca, 0)

    eleza test_step_overflow(self):
        a = (c_int * 5)()
        a[3::sys.maxsize] = (1,)
        self.assertListEqual(a[3::sys.maxsize], [1])
        a = (c_char * 5)()
        a[3::sys.maxsize] = b"A"
        self.assertEqual(a[3::sys.maxsize], b"A")
        a = (c_wchar * 5)()
        a[3::sys.maxsize] = u"X"
        self.assertEqual(a[3::sys.maxsize], u"X")

    eleza test_numeric_arrays(self):

        alen = 5

        numarray = ARRAY(c_int, alen)

        na = numarray()
        values = [na[i] kila i kwenye range(alen)]
        self.assertEqual(values, [0] * alen)

        na = numarray(*[c_int()] * alen)
        values = [na[i] kila i kwenye range(alen)]
        self.assertEqual(values, [0]*alen)

        na = numarray(1, 2, 3, 4, 5)
        values = [i kila i kwenye na]
        self.assertEqual(values, [1, 2, 3, 4, 5])

        na = numarray(*map(c_int, (1, 2, 3, 4, 5)))
        values = [i kila i kwenye na]
        self.assertEqual(values, [1, 2, 3, 4, 5])

    eleza test_classcache(self):
        self.assertIsNot(ARRAY(c_int, 3), ARRAY(c_int, 4))
        self.assertIs(ARRAY(c_int, 3), ARRAY(c_int, 3))

    eleza test_from_address(self):
        # Failed ukijumuisha 0.9.8, reported by JUrner
        p = create_string_buffer(b"foo")
        sz = (c_char * 3).from_address(addressof(p))
        self.assertEqual(sz[:], b"foo")
        self.assertEqual(sz[::], b"foo")
        self.assertEqual(sz[::-1], b"oof")
        self.assertEqual(sz[::3], b"f")
        self.assertEqual(sz[1:4:2], b"o")
        self.assertEqual(sz.value, b"foo")

    @need_symbol('create_unicode_buffer')
    eleza test_from_addressW(self):
        p = create_unicode_buffer("foo")
        sz = (c_wchar * 3).from_address(addressof(p))
        self.assertEqual(sz[:], "foo")
        self.assertEqual(sz[::], "foo")
        self.assertEqual(sz[::-1], "oof")
        self.assertEqual(sz[::3], "f")
        self.assertEqual(sz[1:4:2], "o")
        self.assertEqual(sz.value, "foo")

    eleza test_cache(self):
        # Array types are cached internally kwenye the _ctypes extension,
        # kwenye a WeakValueDictionary.  Make sure the array type is
        # removed kutoka the cache when the itemtype goes away.  This
        # test will sio fail, but will show a leak kwenye the testsuite.

        # Create a new type:
        kundi my_int(c_int):
            pita
        # Create a new array type based on it:
        t1 = my_int * 1
        t2 = my_int * 1
        self.assertIs(t1, t2)

    eleza test_subclass(self):
        kundi T(Array):
            _type_ = c_int
            _length_ = 13
        kundi U(T):
            pita
        kundi V(U):
            pita
        kundi W(V):
            pita
        kundi X(T):
            _type_ = c_short
        kundi Y(T):
            _length_ = 187

        kila c kwenye [T, U, V, W]:
            self.assertEqual(c._type_, c_int)
            self.assertEqual(c._length_, 13)
            self.assertEqual(c()._type_, c_int)
            self.assertEqual(c()._length_, 13)

        self.assertEqual(X._type_, c_short)
        self.assertEqual(X._length_, 13)
        self.assertEqual(X()._type_, c_short)
        self.assertEqual(X()._length_, 13)

        self.assertEqual(Y._type_, c_int)
        self.assertEqual(Y._length_, 187)
        self.assertEqual(Y()._type_, c_int)
        self.assertEqual(Y()._length_, 187)

    eleza test_bad_subclass(self):
        ukijumuisha self.assertRaises(AttributeError):
            kundi T(Array):
                pita
        ukijumuisha self.assertRaises(AttributeError):
            kundi T(Array):
                _type_ = c_int
        ukijumuisha self.assertRaises(AttributeError):
            kundi T(Array):
                _length_ = 13

    eleza test_bad_length(self):
        ukijumuisha self.assertRaises(ValueError):
            kundi T(Array):
                _type_ = c_int
                _length_ = - sys.maxsize * 2
        ukijumuisha self.assertRaises(ValueError):
            kundi T(Array):
                _type_ = c_int
                _length_ = -1
        ukijumuisha self.assertRaises(TypeError):
            kundi T(Array):
                _type_ = c_int
                _length_ = 1.87
        ukijumuisha self.assertRaises(OverflowError):
            kundi T(Array):
                _type_ = c_int
                _length_ = sys.maxsize * 2

    eleza test_zero_length(self):
        # _length_ can be zero.
        kundi T(Array):
            _type_ = c_int
            _length_ = 0

    eleza test_empty_element_struct(self):
        kundi EmptyStruct(Structure):
            _fields_ = []

        obj = (EmptyStruct * 2)()  # bpo37188: Floating point exception
        self.assertEqual(sizeof(obj), 0)

    eleza test_empty_element_array(self):
        kundi EmptyArray(Array):
            _type_ = c_int
            _length_ = 0

        obj = (EmptyArray * 2)()  # bpo37188: Floating point exception
        self.assertEqual(sizeof(obj), 0)

    eleza test_bpo36504_signed_int_overflow(self):
        # The overflow check kwenye PyCArrayType_new() could cause signed integer
        # overflow.
        ukijumuisha self.assertRaises(OverflowError):
            c_char * sys.maxsize * 2

    @unittest.skipUnless(sys.maxsize > 2**32, 'requires 64bit platform')
    @bigmemtest(size=_2G, memuse=1, dry_run=Uongo)
    eleza test_large_array(self, size):
        c_char * size

ikiwa __name__ == '__main__':
    unittest.main()
