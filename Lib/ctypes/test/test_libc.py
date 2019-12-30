agiza unittest

kutoka ctypes agiza *
agiza _ctypes_test

lib = CDLL(_ctypes_test.__file__)

eleza three_way_cmp(x, y):
    """Return -1 ikiwa x < y, 0 ikiwa x == y na 1 ikiwa x > y"""
    rudisha (x > y) - (x < y)

kundi LibTest(unittest.TestCase):
    eleza test_sqrt(self):
        lib.my_sqrt.argtypes = c_double,
        lib.my_sqrt.restype = c_double
        self.assertEqual(lib.my_sqrt(4.0), 2.0)
        agiza math
        self.assertEqual(lib.my_sqrt(2.0), math.sqrt(2.0))

    eleza test_qsort(self):
        comparefunc = CFUNCTYPE(c_int, POINTER(c_char), POINTER(c_char))
        lib.my_qsort.argtypes = c_void_p, c_size_t, c_size_t, comparefunc
        lib.my_qsort.restype = Tupu

        eleza sort(a, b):
            rudisha three_way_cmp(a[0], b[0])

        chars = create_string_buffer(b"spam, spam, na spam")
        lib.my_qsort(chars, len(chars)-1, sizeof(c_char), comparefunc(sort))
        self.assertEqual(chars.raw, b"   ,,aaaadmmmnpppsss\x00")

ikiwa __name__ == "__main__":
    unittest.main()
