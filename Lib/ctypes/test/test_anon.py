agiza unittest
agiza test.support
kutoka ctypes agiza *

kundi AnonTest(unittest.TestCase):

    eleza test_anon(self):
        kundi ANON(Union):
            _fields_ = [("a", c_int),
                        ("b", c_int)]

        kundi Y(Structure):
            _fields_ = [("x", c_int),
                        ("_", ANON),
                        ("y", c_int)]
            _anonymous_ = ["_"]

        self.assertEqual(Y.a.offset, sizeof(c_int))
        self.assertEqual(Y.b.offset, sizeof(c_int))

        self.assertEqual(ANON.a.offset, 0)
        self.assertEqual(ANON.b.offset, 0)

    eleza test_anon_nonseq(self):
        # TypeError: _anonymous_ must be a sequence
        self.assertRaises(TypeError,
                              lambda: type(Structure)("Name",
                                                      (Structure,),
                                                      {"_fields_": [], "_anonymous_": 42}))

    eleza test_anon_nonmember(self):
        # AttributeError: type object 'Name' has no attribute 'x'
        self.assertRaises(AttributeError,
                              lambda: type(Structure)("Name",
                                                      (Structure,),
                                                      {"_fields_": [],
                                                       "_anonymous_": ["x"]}))

    @test.support.cpython_only
    eleza test_issue31490(self):
        # There shouldn't be an assertion failure kwenye case the kundi has an
        # attribute whose name ni specified kwenye _anonymous_ but sio kwenye _fields_.

        # AttributeError: 'x' ni specified kwenye _anonymous_ but sio kwenye _fields_
        ukijumuisha self.assertRaises(AttributeError):
            kundi Name(Structure):
                _fields_ = []
                _anonymous_ = ["x"]
                x = 42

    eleza test_nested(self):
        kundi ANON_S(Structure):
            _fields_ = [("a", c_int)]

        kundi ANON_U(Union):
            _fields_ = [("_", ANON_S),
                        ("b", c_int)]
            _anonymous_ = ["_"]

        kundi Y(Structure):
            _fields_ = [("x", c_int),
                        ("_", ANON_U),
                        ("y", c_int)]
            _anonymous_ = ["_"]

        self.assertEqual(Y.x.offset, 0)
        self.assertEqual(Y.a.offset, sizeof(c_int))
        self.assertEqual(Y.b.offset, sizeof(c_int))
        self.assertEqual(Y._.offset, sizeof(c_int))
        self.assertEqual(Y.y.offset, sizeof(c_int) * 2)

ikiwa __name__ == "__main__":
    unittest.main()
