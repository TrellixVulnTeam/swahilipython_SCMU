agiza unittest
kutoka ctypes agiza *
kutoka binascii agiza hexlify
agiza re

eleza dump(obj):
    # helper function to dump memory contents kwenye hex, ukijumuisha a hyphen
    # between the bytes.
    h = hexlify(memoryview(obj)).decode()
    rudisha re.sub(r"(..)", r"\1-", h)[:-1]


kundi Value(Structure):
    _fields_ = [("val", c_byte)]

kundi Container(Structure):
    _fields_ = [("pvalues", POINTER(Value))]

kundi Test(unittest.TestCase):
    eleza test(self):
        # create an array of 4 values
        val_array = (Value * 4)()

        # create a container, which holds a pointer to the pvalues array.
        c = Container()
        c.pvalues = val_array

        # memory contains 4 NUL bytes now, that's correct
        self.assertEqual("00-00-00-00", dump(val_array))

        # set the values of the array through the pointer:
        kila i kwenye range(4):
            c.pvalues[i].val = i + 1

        values = [c.pvalues[i].val kila i kwenye range(4)]

        # These are the expected results: here s the bug!
        self.assertEqual(
            (values, dump(val_array)),
            ([1, 2, 3, 4], "01-02-03-04")
        )

    eleza test_2(self):

        val_array = (Value * 4)()

        # memory contains 4 NUL bytes now, that's correct
        self.assertEqual("00-00-00-00", dump(val_array))

        ptr = cast(val_array, POINTER(Value))
        # set the values of the array through the pointer:
        kila i kwenye range(4):
            ptr[i].val = i + 1

        values = [ptr[i].val kila i kwenye range(4)]

        # These are the expected results: here s the bug!
        self.assertEqual(
            (values, dump(val_array)),
            ([1, 2, 3, 4], "01-02-03-04")
        )

ikiwa __name__ == "__main__":
    unittest.main()
