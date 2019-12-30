kutoka ctypes agiza *
agiza unittest

kundi SimpleTestCase(unittest.TestCase):
    eleza test_cint(self):
        x = c_int()
        self.assertEqual(x._objects, Tupu)
        x.value = 42
        self.assertEqual(x._objects, Tupu)
        x = c_int(99)
        self.assertEqual(x._objects, Tupu)

    eleza test_ccharp(self):
        x = c_char_p()
        self.assertEqual(x._objects, Tupu)
        x.value = b"abc"
        self.assertEqual(x._objects, b"abc")
        x = c_char_p(b"spam")
        self.assertEqual(x._objects, b"spam")

kundi StructureTestCase(unittest.TestCase):
    eleza test_cint_struct(self):
        kundi X(Structure):
            _fields_ = [("a", c_int),
                        ("b", c_int)]

        x = X()
        self.assertEqual(x._objects, Tupu)
        x.a = 42
        x.b = 99
        self.assertEqual(x._objects, Tupu)

    eleza test_ccharp_struct(self):
        kundi X(Structure):
            _fields_ = [("a", c_char_p),
                        ("b", c_char_p)]
        x = X()
        self.assertEqual(x._objects, Tupu)

        x.a = b"spam"
        x.b = b"foo"
        self.assertEqual(x._objects, {"0": b"spam", "1": b"foo"})

    eleza test_struct_struct(self):
        kundi POINT(Structure):
            _fields_ = [("x", c_int), ("y", c_int)]
        kundi RECT(Structure):
            _fields_ = [("ul", POINT), ("lr", POINT)]

        r = RECT()
        r.ul.x = 0
        r.ul.y = 1
        r.lr.x = 2
        r.lr.y = 3
        self.assertEqual(r._objects, Tupu)

        r = RECT()
        pt = POINT(1, 2)
        r.ul = pt
        self.assertEqual(r._objects, {'0': {}})
        r.ul.x = 22
        r.ul.y = 44
        self.assertEqual(r._objects, {'0': {}})
        r.lr = POINT()
        self.assertEqual(r._objects, {'0': {}, '1': {}})

kundi ArrayTestCase(unittest.TestCase):
    eleza test_cint_array(self):
        INTARR = c_int * 3

        ia = INTARR()
        self.assertEqual(ia._objects, Tupu)
        ia[0] = 1
        ia[1] = 2
        ia[2] = 3
        self.assertEqual(ia._objects, Tupu)

        kundi X(Structure):
            _fields_ = [("x", c_int),
                        ("a", INTARR)]

        x = X()
        x.x = 1000
        x.a[0] = 42
        x.a[1] = 96
        self.assertEqual(x._objects, Tupu)
        x.a = ia
        self.assertEqual(x._objects, {'1': {}})

kundi PointerTestCase(unittest.TestCase):
    eleza test_p_cint(self):
        i = c_int(42)
        x = pointer(i)
        self.assertEqual(x._objects, {'1': i})

kundi DeletePointerTestCase(unittest.TestCase):
    @unittest.skip('test disabled')
    eleza test_X(self):
        kundi X(Structure):
            _fields_ = [("p", POINTER(c_char_p))]
        x = X()
        i = c_char_p("abc def")
        kutoka sys agiza getrefcount kama grc
        andika("2?", grc(i))
        x.p = pointer(i)
        andika("3?", grc(i))
        kila i kwenye range(320):
            c_int(99)
            x.p[0]
        andika(x.p[0])
##        toa x
##        andika "2?", grc(i)
##        toa i
        agiza gc
        gc.collect()
        kila i kwenye range(320):
            c_int(99)
            x.p[0]
        andika(x.p[0])
        andika(x.p.contents)
##        andika x._objects

        x.p[0] = "spam spam"
##        andika x.p[0]
        andika("+" * 42)
        andika(x._objects)

kundi PointerToStructure(unittest.TestCase):
    eleza test(self):
        kundi POINT(Structure):
            _fields_ = [("x", c_int), ("y", c_int)]
        kundi RECT(Structure):
            _fields_ = [("a", POINTER(POINT)),
                        ("b", POINTER(POINT))]
        r = RECT()
        p1 = POINT(1, 2)

        r.a = pointer(p1)
        r.b = pointer(p1)
##        kutoka pprint agiza pprint kama pp
##        pp(p1._objects)
##        pp(r._objects)

        r.a[0].x = 42
        r.a[0].y = 99

        # to avoid leaking when tests are run several times
        # clean up the types left kwenye the cache.
        kutoka ctypes agiza _pointer_type_cache
        toa _pointer_type_cache[POINT]

ikiwa __name__ == "__main__":
    unittest.main()
