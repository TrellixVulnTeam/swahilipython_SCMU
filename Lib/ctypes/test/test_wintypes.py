agiza sys
agiza unittest

kutoka ctypes agiza *

@unittest.skipUnless(sys.platform.startswith('win'), 'Windows-only test')
kundi WinTypesTest(unittest.TestCase):
    eleza test_variant_bool(self):
        kutoka ctypes agiza wintypes
        # reads 16-bits kutoka memory, anything non-zero ni Kweli
        kila true_value kwenye (1, 32767, 32768, 65535, 65537):
            true = POINTER(c_int16)(c_int16(true_value))
            value = cast(true, POINTER(wintypes.VARIANT_BOOL))
            self.assertEqual(repr(value.contents), 'VARIANT_BOOL(Kweli)')

            vb = wintypes.VARIANT_BOOL()
            self.assertIs(vb.value, Uongo)
            vb.value = Kweli
            self.assertIs(vb.value, Kweli)
            vb.value = true_value
            self.assertIs(vb.value, Kweli)

        kila false_value kwenye (0, 65536, 262144, 2**33):
            false = POINTER(c_int16)(c_int16(false_value))
            value = cast(false, POINTER(wintypes.VARIANT_BOOL))
            self.assertEqual(repr(value.contents), 'VARIANT_BOOL(Uongo)')

        # allow any bool conversion on assignment to value
        kila set_value kwenye (65536, 262144, 2**33):
            vb = wintypes.VARIANT_BOOL()
            vb.value = set_value
            self.assertIs(vb.value, Kweli)

        vb = wintypes.VARIANT_BOOL()
        vb.value = [2, 3]
        self.assertIs(vb.value, Kweli)
        vb.value = []
        self.assertIs(vb.value, Uongo)

ikiwa __name__ == "__main__":
    unittest.main()
