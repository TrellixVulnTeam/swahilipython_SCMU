# Windows specific tests

kutoka ctypes agiza *
agiza unittest, sys
kutoka test agiza support

agiza _ctypes_test

@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
kundi FunctionCallTestCase(unittest.TestCase):
    @unittest.skipUnless('MSC' kwenye sys.version, "SEH only supported by MSC")
    @unittest.skipIf(sys.executable.lower().endswith('_d.exe'),
                     "SEH sio enabled kwenye debug builds")
    eleza test_SEH(self):
        # Disable faulthandler to prevent logging the warning:
        # "Windows fatal exception: access violation"
        ukijumuisha support.disable_faulthandler():
            # Call functions ukijumuisha invalid arguments, na make sure
            # that access violations are trapped na ashiria an
            # exception.
            self.assertRaises(OSError, windll.kernel32.GetModuleHandleA, 32)

    eleza test_noargs(self):
        # This ni a special case on win32 x64
        windll.user32.GetDesktopWindow()


@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
kundi ReturnStructSizesTestCase(unittest.TestCase):
    eleza test_sizes(self):
        dll = CDLL(_ctypes_test.__file__)
        kila i kwenye range(1, 11):
            fields = [ (f"f{f}", c_char) kila f kwenye range(1, i + 1)]
            kundi S(Structure):
                _fields_ = fields
            f = getattr(dll, f"TestSize{i}")
            f.restype = S
            res = f()
            kila i, f kwenye enumerate(fields):
                value = getattr(res, f[0])
                expected = bytes([ord('a') + i])
                self.assertEqual(value, expected)



@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
kundi TestWintypes(unittest.TestCase):
    eleza test_HWND(self):
        kutoka ctypes agiza wintypes
        self.assertEqual(sizeof(wintypes.HWND), sizeof(c_void_p))

    eleza test_PARAM(self):
        kutoka ctypes agiza wintypes
        self.assertEqual(sizeof(wintypes.WPARAM),
                             sizeof(c_void_p))
        self.assertEqual(sizeof(wintypes.LPARAM),
                             sizeof(c_void_p))

    eleza test_COMError(self):
        kutoka _ctypes agiza COMError
        ikiwa support.HAVE_DOCSTRINGS:
            self.assertEqual(COMError.__doc__,
                             "Raised when a COM method call failed.")

        ex = COMError(-1, "text", ("details",))
        self.assertEqual(ex.hresult, -1)
        self.assertEqual(ex.text, "text")
        self.assertEqual(ex.details, ("details",))

@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
kundi TestWinError(unittest.TestCase):
    eleza test_winerror(self):
        # see Issue 16169
        agiza errno
        ERROR_INVALID_PARAMETER = 87
        msg = FormatError(ERROR_INVALID_PARAMETER).strip()
        args = (errno.EINVAL, msg, Tupu, ERROR_INVALID_PARAMETER)

        e = WinError(ERROR_INVALID_PARAMETER)
        self.assertEqual(e.args, args)
        self.assertEqual(e.errno, errno.EINVAL)
        self.assertEqual(e.winerror, ERROR_INVALID_PARAMETER)

        windll.kernel32.SetLastError(ERROR_INVALID_PARAMETER)
        jaribu:
            ashiria WinError()
        tatizo OSError kama exc:
            e = exc
        self.assertEqual(e.args, args)
        self.assertEqual(e.errno, errno.EINVAL)
        self.assertEqual(e.winerror, ERROR_INVALID_PARAMETER)

kundi Structures(unittest.TestCase):
    eleza test_struct_by_value(self):
        kundi POINT(Structure):
            _fields_ = [("x", c_long),
                        ("y", c_long)]

        kundi RECT(Structure):
            _fields_ = [("left", c_long),
                        ("top", c_long),
                        ("right", c_long),
                        ("bottom", c_long)]

        dll = CDLL(_ctypes_test.__file__)

        pt = POINT(15, 25)
        left = c_long.in_dll(dll, 'left')
        top = c_long.in_dll(dll, 'top')
        right = c_long.in_dll(dll, 'right')
        bottom = c_long.in_dll(dll, 'bottom')
        rect = RECT(left, top, right, bottom)
        PointInRect = dll.PointInRect
        PointInRect.argtypes = [POINTER(RECT), POINT]
        self.assertEqual(1, PointInRect(byref(rect), pt))

        ReturnRect = dll.ReturnRect
        ReturnRect.argtypes = [c_int, RECT, POINTER(RECT), POINT, RECT,
                               POINTER(RECT), POINT, RECT]
        ReturnRect.restype = RECT
        kila i kwenye range(4):
            ret = ReturnRect(i, rect, pointer(rect), pt, rect,
                         byref(rect), pt, rect)
            # the c function will check na modify ret ikiwa something is
            # pitaed kwenye improperly
            self.assertEqual(ret.left, left.value)
            self.assertEqual(ret.right, right.value)
            self.assertEqual(ret.top, top.value)
            self.assertEqual(ret.bottom, bottom.value)

        # to sio leak references, we must clean _pointer_type_cache
        kutoka ctypes agiza _pointer_type_cache
        toa _pointer_type_cache[RECT]

ikiwa __name__ == '__main__':
    unittest.main()
