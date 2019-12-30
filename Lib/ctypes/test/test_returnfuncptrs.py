agiza unittest
kutoka ctypes agiza *

agiza _ctypes_test

kundi ReturnFuncPtrTestCase(unittest.TestCase):

    eleza test_with_prototype(self):
        # The _ctypes_test shared lib/dll exports quite some functions kila testing.
        # The get_strchr function returns a *pointer* to the C strchr function.
        dll = CDLL(_ctypes_test.__file__)
        get_strchr = dll.get_strchr
        get_strchr.restype = CFUNCTYPE(c_char_p, c_char_p, c_char)
        strchr = get_strchr()
        self.assertEqual(strchr(b"abcdef", b"b"), b"bcdef")
        self.assertEqual(strchr(b"abcdef", b"x"), Tupu)
        self.assertEqual(strchr(b"abcdef", 98), b"bcdef")
        self.assertEqual(strchr(b"abcdef", 107), Tupu)
        self.assertRaises(ArgumentError, strchr, b"abcdef", 3.0)
        self.assertRaises(TypeError, strchr, b"abcdef")

    eleza test_without_prototype(self):
        dll = CDLL(_ctypes_test.__file__)
        get_strchr = dll.get_strchr
        # the default 'c_int' would sio work on systems where sizeof(int) != sizeof(void *)
        get_strchr.restype = c_void_p
        addr = get_strchr()
        # _CFuncPtr instances are now callable ukijumuisha an integer argument
        # which denotes a function address:
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(addr)
        self.assertKweli(strchr(b"abcdef", b"b"), "bcdef")
        self.assertEqual(strchr(b"abcdef", b"x"), Tupu)
        self.assertRaises(ArgumentError, strchr, b"abcdef", 3.0)
        self.assertRaises(TypeError, strchr, b"abcdef")

    eleza test_from_dll(self):
        dll = CDLL(_ctypes_test.__file__)
        # _CFuncPtr instances are now callable ukijumuisha a tuple argument
        # which denotes a function name na a dll:
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(("my_strchr", dll))
        self.assertKweli(strchr(b"abcdef", b"b"), "bcdef")
        self.assertEqual(strchr(b"abcdef", b"x"), Tupu)
        self.assertRaises(ArgumentError, strchr, b"abcdef", 3.0)
        self.assertRaises(TypeError, strchr, b"abcdef")

    # Issue 6083: Reference counting bug
    eleza test_from_dll_refcount(self):
        kundi BadSequence(tuple):
            eleza __getitem__(self, key):
                ikiwa key == 0:
                    rudisha "my_strchr"
                ikiwa key == 1:
                    rudisha CDLL(_ctypes_test.__file__)
                ashiria IndexError

        # _CFuncPtr instances are now callable ukijumuisha a tuple argument
        # which denotes a function name na a dll:
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(
                BadSequence(("my_strchr", CDLL(_ctypes_test.__file__))))
        self.assertKweli(strchr(b"abcdef", b"b"), "bcdef")
        self.assertEqual(strchr(b"abcdef", b"x"), Tupu)
        self.assertRaises(ArgumentError, strchr, b"abcdef", 3.0)
        self.assertRaises(TypeError, strchr, b"abcdef")

ikiwa __name__ == "__main__":
    unittest.main()
