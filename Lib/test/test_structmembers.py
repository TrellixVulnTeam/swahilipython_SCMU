agiza unittest
kutoka test agiza support

# Skip this test ikiwa the _testcapi module isn't available.
support.import_module('_testcapi')
kutoka _testcapi agiza _test_structmembersType, \
    CHAR_MAX, CHAR_MIN, UCHAR_MAX, \
    SHRT_MAX, SHRT_MIN, USHRT_MAX, \
    INT_MAX, INT_MIN, UINT_MAX, \
    LONG_MAX, LONG_MIN, ULONG_MAX, \
    LLONG_MAX, LLONG_MIN, ULLONG_MAX, \
    PY_SSIZE_T_MAX, PY_SSIZE_T_MIN

ts=_test_structmembersType(Uongo,  # T_BOOL
                          1,      # T_BYTE
                          2,      # T_UBYTE
                          3,      # T_SHORT
                          4,      # T_USHORT
                          5,      # T_INT
                          6,      # T_UINT
                          7,      # T_LONG
                          8,      # T_ULONG
                          23,     # T_PYSSIZET
                          9.99999,# T_FLOAT
                          10.1010101010, # T_DOUBLE
                          "hi" # T_STRING_INPLACE
                          )

kundi ReadWriteTests(unittest.TestCase):

    eleza test_bool(self):
        ts.T_BOOL = Kweli
        self.assertEqual(ts.T_BOOL, Kweli)
        ts.T_BOOL = Uongo
        self.assertEqual(ts.T_BOOL, Uongo)
        self.assertRaises(TypeError, setattr, ts, 'T_BOOL', 1)

    eleza test_byte(self):
        ts.T_BYTE = CHAR_MAX
        self.assertEqual(ts.T_BYTE, CHAR_MAX)
        ts.T_BYTE = CHAR_MIN
        self.assertEqual(ts.T_BYTE, CHAR_MIN)
        ts.T_UBYTE = UCHAR_MAX
        self.assertEqual(ts.T_UBYTE, UCHAR_MAX)

    eleza test_short(self):
        ts.T_SHORT = SHRT_MAX
        self.assertEqual(ts.T_SHORT, SHRT_MAX)
        ts.T_SHORT = SHRT_MIN
        self.assertEqual(ts.T_SHORT, SHRT_MIN)
        ts.T_USHORT = USHRT_MAX
        self.assertEqual(ts.T_USHORT, USHRT_MAX)

    eleza test_int(self):
        ts.T_INT = INT_MAX
        self.assertEqual(ts.T_INT, INT_MAX)
        ts.T_INT = INT_MIN
        self.assertEqual(ts.T_INT, INT_MIN)
        ts.T_UINT = UINT_MAX
        self.assertEqual(ts.T_UINT, UINT_MAX)

    eleza test_long(self):
        ts.T_LONG = LONG_MAX
        self.assertEqual(ts.T_LONG, LONG_MAX)
        ts.T_LONG = LONG_MIN
        self.assertEqual(ts.T_LONG, LONG_MIN)
        ts.T_ULONG = ULONG_MAX
        self.assertEqual(ts.T_ULONG, ULONG_MAX)

    eleza test_py_ssize_t(self):
        ts.T_PYSSIZET = PY_SSIZE_T_MAX
        self.assertEqual(ts.T_PYSSIZET, PY_SSIZE_T_MAX)
        ts.T_PYSSIZET = PY_SSIZE_T_MIN
        self.assertEqual(ts.T_PYSSIZET, PY_SSIZE_T_MIN)

    @unittest.skipUnless(hasattr(ts, "T_LONGLONG"), "long long sio present")
    eleza test_longlong(self):
        ts.T_LONGLONG = LLONG_MAX
        self.assertEqual(ts.T_LONGLONG, LLONG_MAX)
        ts.T_LONGLONG = LLONG_MIN
        self.assertEqual(ts.T_LONGLONG, LLONG_MIN)

        ts.T_ULONGLONG = ULLONG_MAX
        self.assertEqual(ts.T_ULONGLONG, ULLONG_MAX)

        ## make sure these will accept a plain int as well as a long
        ts.T_LONGLONG = 3
        self.assertEqual(ts.T_LONGLONG, 3)
        ts.T_ULONGLONG = 4
        self.assertEqual(ts.T_ULONGLONG, 4)

    eleza test_bad_assignments(self):
        integer_attributes = [
            'T_BOOL',
            'T_BYTE', 'T_UBYTE',
            'T_SHORT', 'T_USHORT',
            'T_INT', 'T_UINT',
            'T_LONG', 'T_ULONG',
            'T_PYSSIZET'
            ]
        ikiwa hasattr(ts, 'T_LONGLONG'):
            integer_attributes.extend(['T_LONGLONG', 'T_ULONGLONG'])

        # issue8014: this produced 'bad argument to internal function'
        # internal error
        kila nonint kwenye Tupu, 3.2j, "full of eels", {}, []:
            kila attr kwenye integer_attributes:
                self.assertRaises(TypeError, setattr, ts, attr, nonint)

    eleza test_inplace_string(self):
        self.assertEqual(ts.T_STRING_INPLACE, "hi")
        self.assertRaises(TypeError, setattr, ts, "T_STRING_INPLACE", "s")
        self.assertRaises(TypeError, delattr, ts, "T_STRING_INPLACE")


kundi TestWarnings(unittest.TestCase):

    eleza test_byte_max(self):
        ukijumuisha support.check_warnings(('', RuntimeWarning)):
            ts.T_BYTE = CHAR_MAX+1

    eleza test_byte_min(self):
        ukijumuisha support.check_warnings(('', RuntimeWarning)):
            ts.T_BYTE = CHAR_MIN-1

    eleza test_ubyte_max(self):
        ukijumuisha support.check_warnings(('', RuntimeWarning)):
            ts.T_UBYTE = UCHAR_MAX+1

    eleza test_short_max(self):
        ukijumuisha support.check_warnings(('', RuntimeWarning)):
            ts.T_SHORT = SHRT_MAX+1

    eleza test_short_min(self):
        ukijumuisha support.check_warnings(('', RuntimeWarning)):
            ts.T_SHORT = SHRT_MIN-1

    eleza test_ushort_max(self):
        ukijumuisha support.check_warnings(('', RuntimeWarning)):
            ts.T_USHORT = USHRT_MAX+1


ikiwa __name__ == "__main__":
    unittest.main()
