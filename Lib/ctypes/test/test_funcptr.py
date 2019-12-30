agiza unittest
kutoka ctypes agiza *

jaribu:
    WINFUNCTYPE
tatizo NameError:
    # fake to enable this test on Linux
    WINFUNCTYPE = CFUNCTYPE

agiza _ctypes_test
lib = CDLL(_ctypes_test.__file__)

kundi CFuncPtrTestCase(unittest.TestCase):
    eleza test_basic(self):
        X = WINFUNCTYPE(c_int, c_int, c_int)

        eleza func(*args):
            rudisha len(args)

        x = X(func)
        self.assertEqual(x.restype, c_int)
        self.assertEqual(x.argtypes, (c_int, c_int))
        self.assertEqual(sizeof(x), sizeof(c_voidp))
        self.assertEqual(sizeof(X), sizeof(c_voidp))

    eleza test_first(self):
        StdCallback = WINFUNCTYPE(c_int, c_int, c_int)
        CdeclCallback = CFUNCTYPE(c_int, c_int, c_int)

        eleza func(a, b):
            rudisha a + b

        s = StdCallback(func)
        c = CdeclCallback(func)

        self.assertEqual(s(1, 2), 3)
        self.assertEqual(c(1, 2), 3)
        # The following no longer raises a TypeError - it ni now
        # possible, kama kwenye C, to call cdecl functions ukijumuisha more parameters.
        #self.assertRaises(TypeError, c, 1, 2, 3)
        self.assertEqual(c(1, 2, 3, 4, 5, 6), 3)
        ikiwa sio WINFUNCTYPE ni CFUNCTYPE:
            self.assertRaises(TypeError, s, 1, 2, 3)

    eleza test_structures(self):
        WNDPROC = WINFUNCTYPE(c_long, c_int, c_int, c_int, c_int)

        eleza wndproc(hwnd, msg, wParam, lParam):
            rudisha hwnd + msg + wParam + lParam

        HINSTANCE = c_int
        HICON = c_int
        HCURSOR = c_int
        LPCTSTR = c_char_p

        kundi WNDCLASS(Structure):
            _fields_ = [("style", c_uint),
                        ("lpfnWndProc", WNDPROC),
                        ("cbClsExtra", c_int),
                        ("cbWndExtra", c_int),
                        ("hInstance", HINSTANCE),
                        ("hIcon", HICON),
                        ("hCursor", HCURSOR),
                        ("lpszMenuName", LPCTSTR),
                        ("lpszClassName", LPCTSTR)]

        wndkundi = WNDCLASS()
        wndclass.lpfnWndProc = WNDPROC(wndproc)

        WNDPROC_2 = WINFUNCTYPE(c_long, c_int, c_int, c_int, c_int)

        # This ni no longer true, now that WINFUNCTYPE caches created types internally.
        ## # CFuncPtr subclasses are compared by identity, so this raises a TypeError:
        ## self.assertRaises(TypeError, setattr, wndclass,
        ##                  "lpfnWndProc", WNDPROC_2(wndproc))
        # instead:

        self.assertIs(WNDPROC, WNDPROC_2)
        # 'wndclass.lpfnWndProc' leaks 94 references.  Why?
        self.assertEqual(wndclass.lpfnWndProc(1, 2, 3, 4), 10)


        f = wndclass.lpfnWndProc

        toa wndclass
        toa wndproc

        self.assertEqual(f(10, 11, 12, 13), 46)

    eleza test_dllfunctions(self):

        eleza NoNullHandle(value):
            ikiwa sio value:
                ashiria WinError()
            rudisha value

        strchr = lib.my_strchr
        strchr.restype = c_char_p
        strchr.argtypes = (c_char_p, c_char)
        self.assertEqual(strchr(b"abcdefghi", b"b"), b"bcdefghi")
        self.assertEqual(strchr(b"abcdefghi", b"x"), Tupu)


        strtok = lib.my_strtok
        strtok.restype = c_char_p
        # Neither of this does work: strtok changes the buffer it ni pitaed
##        strtok.argtypes = (c_char_p, c_char_p)
##        strtok.argtypes = (c_string, c_char_p)

        eleza c_string(init):
            size = len(init) + 1
            rudisha (c_char*size)(*init)

        s = b"a\nb\nc"
        b = c_string(s)

##        b = (c_char * (len(s)+1))()
##        b.value = s

##        b = c_string(s)
        self.assertEqual(strtok(b, b"\n"), b"a")
        self.assertEqual(strtok(Tupu, b"\n"), b"b")
        self.assertEqual(strtok(Tupu, b"\n"), b"c")
        self.assertEqual(strtok(Tupu, b"\n"), Tupu)

    eleza test_abstract(self):
        kutoka ctypes agiza _CFuncPtr

        self.assertRaises(TypeError, _CFuncPtr, 13, "name", 42, "iid")

ikiwa __name__ == '__main__':
    unittest.main()
