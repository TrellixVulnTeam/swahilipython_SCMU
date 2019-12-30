agiza sys, unittest
kutoka ctypes agiza *

structures = []
byteswapped_structures = []


ikiwa sys.byteorder == "little":
    SwappedStructure = BigEndianStructure
isipokua:
    SwappedStructure = LittleEndianStructure

kila typ kwenye [c_short, c_int, c_long, c_longlong,
            c_float, c_double,
            c_ushort, c_uint, c_ulong, c_ulonglong]:
    kundi X(Structure):
        _pack_ = 1
        _fields_ = [("pad", c_byte),
                    ("value", typ)]
    kundi Y(SwappedStructure):
        _pack_ = 1
        _fields_ = [("pad", c_byte),
                    ("value", typ)]
    structures.append(X)
    byteswapped_structures.append(Y)

kundi TestStructures(unittest.TestCase):
    eleza test_native(self):
        kila typ kwenye structures:
##            print typ.value
            self.assertEqual(typ.value.offset, 1)
            o = typ()
            o.value = 4
            self.assertEqual(o.value, 4)

    eleza test_swapped(self):
        kila typ kwenye byteswapped_structures:
##            print >> sys.stderr, typ.value
            self.assertEqual(typ.value.offset, 1)
            o = typ()
            o.value = 4
            self.assertEqual(o.value, 4)

ikiwa __name__ == '__main__':
    unittest.main()
