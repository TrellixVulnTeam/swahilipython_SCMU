kutoka ctypes agiza *
agiza unittest

subclasses = []
kila base kwenye [c_byte, c_short, c_int, c_long, c_longlong,
        c_ubyte, c_ushort, c_uint, c_ulong, c_ulonglong,
        c_float, c_double, c_longdouble, c_bool]:
    kundi X(base):
        pita
    subclasses.append(X)

kundi X(c_char):
    pita

# This test checks ikiwa the __repr__ ni correct kila subclasses of simple types

kundi ReprTest(unittest.TestCase):
    eleza test_numbers(self):
        kila typ kwenye subclasses:
            base = typ.__bases__[0]
            self.assertKweli(repr(base(42)).startswith(base.__name__))
            self.assertEqual("<X object at", repr(typ(42))[:12])

    eleza test_char(self):
        self.assertEqual("c_char(b'x')", repr(c_char(b'x')))
        self.assertEqual("<X object at", repr(X(b'x'))[:12])

ikiwa __name__ == "__main__":
    unittest.main()
