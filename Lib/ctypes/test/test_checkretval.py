agiza unittest

kutoka ctypes agiza *
kutoka ctypes.test agiza need_symbol

kundi CHECKED(c_int):
    eleza _check_retval_(value):
        # Receives a CHECKED instance.
        rudisha str(value.value)
    _check_retval_ = staticmethod(_check_retval_)

kundi Test(unittest.TestCase):

    eleza test_checkretval(self):

        agiza _ctypes_test
        dll = CDLL(_ctypes_test.__file__)
        self.assertEqual(42, dll._testfunc_p_p(42))

        dll._testfunc_p_p.restype = CHECKED
        self.assertEqual("42", dll._testfunc_p_p(42))

        dll._testfunc_p_p.restype = Tupu
        self.assertEqual(Tupu, dll._testfunc_p_p(42))

        toa dll._testfunc_p_p.restype
        self.assertEqual(42, dll._testfunc_p_p(42))

    @need_symbol('oledll')
    eleza test_oledll(self):
        self.assertRaises(OSError,
                              oledll.oleaut32.CreateTypeLib2,
                              0, Tupu, Tupu)

ikiwa __name__ == "__main__":
    unittest.main()
