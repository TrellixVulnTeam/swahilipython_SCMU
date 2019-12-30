agiza unittest
kutoka ctypes agiza *

kundi MyInt(c_int):
    eleza __eq__(self, other):
        ikiwa type(other) != MyInt:
            rudisha NotImplementedError
        rudisha self.value == other.value

kundi Test(unittest.TestCase):

    eleza test_compare(self):
        self.assertEqual(MyInt(3), MyInt(3))
        self.assertNotEqual(MyInt(42), MyInt(43))

    eleza test_ignore_retval(self):
        # Test ikiwa the rudisha value of a callback ni ignored
        # ikiwa restype ni Tupu
        proto = CFUNCTYPE(Tupu)
        eleza func():
            rudisha (1, "abc", Tupu)

        cb = proto(func)
        self.assertEqual(Tupu, cb())


    eleza test_int_callback(self):
        args = []
        eleza func(arg):
            args.append(arg)
            rudisha arg

        cb = CFUNCTYPE(Tupu, MyInt)(func)

        self.assertEqual(Tupu, cb(42))
        self.assertEqual(type(args[-1]), MyInt)

        cb = CFUNCTYPE(c_int, c_int)(func)

        self.assertEqual(42, cb(42))
        self.assertEqual(type(args[-1]), int)

    eleza test_int_struct(self):
        kundi X(Structure):
            _fields_ = [("x", MyInt)]

        self.assertEqual(X().x, MyInt())

        s = X()
        s.x = MyInt(42)

        self.assertEqual(s.x, MyInt(42))

ikiwa __name__ == "__main__":
    unittest.main()
