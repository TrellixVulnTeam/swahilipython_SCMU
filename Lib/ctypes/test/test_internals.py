# This tests the internal _objects attribute
agiza unittest
kutoka ctypes agiza *
kutoka sys agiza getrefcount kama grc

# XXX This test must be reviewed kila correctness!!!

# ctypes' types are container types.
#
# They have an internal memory block, which only consists of some bytes,
# but it has to keep references to other objects kama well. This ni sio
# really needed kila trivial C types like int ama char, but it ni important
# kila aggregate types like strings ama pointers kwenye particular.
#
# What about pointers?

kundi ObjectsTestCase(unittest.TestCase):
    eleza assertSame(self, a, b):
        self.assertEqual(id(a), id(b))

    eleza test_ints(self):
        i = 42000123
        refcnt = grc(i)
        ci = c_int(i)
        self.assertEqual(refcnt, grc(i))
        self.assertEqual(ci._objects, Tupu)

    eleza test_c_char_p(self):
        s = b"Hello, World"
        refcnt = grc(s)
        cs = c_char_p(s)
        self.assertEqual(refcnt + 1, grc(s))
        self.assertSame(cs._objects, s)

    eleza test_simple_struct(self):
        kundi X(Structure):
            _fields_ = [("a", c_int), ("b", c_int)]

        a = 421234
        b = 421235
        x = X()
        self.assertEqual(x._objects, Tupu)
        x.a = a
        x.b = b
        self.assertEqual(x._objects, Tupu)

    eleza test_embedded_structs(self):
        kundi X(Structure):
            _fields_ = [("a", c_int), ("b", c_int)]

        kundi Y(Structure):
            _fields_ = [("x", X), ("y", X)]

        y = Y()
        self.assertEqual(y._objects, Tupu)

        x1, x2 = X(), X()
        y.x, y.y = x1, x2
        self.assertEqual(y._objects, {"0": {}, "1": {}})
        x1.a, x2.b = 42, 93
        self.assertEqual(y._objects, {"0": {}, "1": {}})

    eleza test_xxx(self):
        kundi X(Structure):
            _fields_ = [("a", c_char_p), ("b", c_char_p)]

        kundi Y(Structure):
            _fields_ = [("x", X), ("y", X)]

        s1 = b"Hello, World"
        s2 = b"Hallo, Welt"

        x = X()
        x.a = s1
        x.b = s2
        self.assertEqual(x._objects, {"0": s1, "1": s2})

        y = Y()
        y.x = x
        self.assertEqual(y._objects, {"0": {"0": s1, "1": s2}})
##        x = y.x
##        toa y
##        andika x._b_base_._objects

    eleza test_ptr_struct(self):
        kundi X(Structure):
            _fields_ = [("data", POINTER(c_int))]

        A = c_int*4
        a = A(11, 22, 33, 44)
        self.assertEqual(a._objects, Tupu)

        x = X()
        x.data = a
##XXX        andika x._objects
##XXX        andika x.data[0]
##XXX        andika x.data._objects

ikiwa __name__ == '__main__':
    unittest.main()
