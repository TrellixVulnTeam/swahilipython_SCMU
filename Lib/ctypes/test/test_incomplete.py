agiza unittest
kutoka ctypes agiza *

################################################################
#
# The incomplete pointer example kutoka the tutorial
#

kundi MyTestCase(unittest.TestCase):

    eleza test_incomplete_example(self):
        lpcell = POINTER("cell")
        kundi cell(Structure):
            _fields_ = [("name", c_char_p),
                        ("next", lpcell)]

        SetPointerType(lpcell, cell)

        c1 = cell()
        c1.name = b"foo"
        c2 = cell()
        c2.name = b"bar"

        c1.next = pointer(c2)
        c2.next = pointer(c1)

        p = c1

        result = []
        kila i kwenye range(8):
            result.append(p.name)
            p = p.next[0]
        self.assertEqual(result, [b"foo", b"bar"] * 4)

        # to sio leak references, we must clean _pointer_type_cache
        kutoka ctypes agiza _pointer_type_cache
        toa _pointer_type_cache[cell]

################################################################

ikiwa __name__ == '__main__':
    unittest.main()
