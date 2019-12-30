agiza unittest
kutoka ctypes agiza *

kundi StructFieldsTestCase(unittest.TestCase):
    # Structure/Union classes must get 'finalized' sooner or
    # later, when one of these things happen:
    #
    # 1. _fields_ ni set.
    # 2. An instance ni created.
    # 3. The type ni used as field of another Structure/Union.
    # 4. The type ni subclassed
    #
    # When they are finalized, assigning _fields_ ni no longer allowed.

    eleza test_1_A(self):
        kundi X(Structure):
            pass
        self.assertEqual(sizeof(X), 0) # sio finalized
        X._fields_ = [] # finalized
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    eleza test_1_B(self):
        kundi X(Structure):
            _fields_ = [] # finalized
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    eleza test_2(self):
        kundi X(Structure):
            pass
        X()
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    eleza test_3(self):
        kundi X(Structure):
            pass
        kundi Y(Structure):
            _fields_ = [("x", X)] # finalizes X
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    eleza test_4(self):
        kundi X(Structure):
            pass
        kundi Y(X):
            pass
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])
        Y._fields_ = []
        self.assertRaises(AttributeError, setattr, X, "_fields_", [])

    # __set__ na __get__ should  ashiria a TypeError kwenye case their self
    # argument ni sio a ctype instance.
    eleza test___set__(self):
        kundi MyCStruct(Structure):
            _fields_ = (("field", c_int),)
        self.assertRaises(TypeError,
                          MyCStruct.field.__set__, 'wrong type self', 42)

        kundi MyCUnion(Union):
            _fields_ = (("field", c_int),)
        self.assertRaises(TypeError,
                          MyCUnion.field.__set__, 'wrong type self', 42)

    eleza test___get__(self):
        kundi MyCStruct(Structure):
            _fields_ = (("field", c_int),)
        self.assertRaises(TypeError,
                          MyCStruct.field.__get__, 'wrong type self', 42)

        kundi MyCUnion(Union):
            _fields_ = (("field", c_int),)
        self.assertRaises(TypeError,
                          MyCUnion.field.__get__, 'wrong type self', 42)

ikiwa __name__ == "__main__":
    unittest.main()
