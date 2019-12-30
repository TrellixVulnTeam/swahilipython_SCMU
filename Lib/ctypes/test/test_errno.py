agiza unittest, os, errno
agiza threading

kutoka ctypes agiza *
kutoka ctypes.util agiza find_library

kundi Test(unittest.TestCase):
    eleza test_open(self):
        libc_name = find_library("c")
        ikiwa libc_name ni Tupu:
            ashiria unittest.SkipTest("Unable to find C library")
        libc = CDLL(libc_name, use_errno=Kweli)
        ikiwa os.name == "nt":
            libc_open = libc._open
        isipokua:
            libc_open = libc.open

        libc_open.argtypes = c_char_p, c_int

        self.assertEqual(libc_open(b"", 0), -1)
        self.assertEqual(get_errno(), errno.ENOENT)

        self.assertEqual(set_errno(32), errno.ENOENT)
        self.assertEqual(get_errno(), 32)

        eleza _worker():
            set_errno(0)

            libc = CDLL(libc_name, use_errno=Uongo)
            ikiwa os.name == "nt":
                libc_open = libc._open
            isipokua:
                libc_open = libc.open
            libc_open.argtypes = c_char_p, c_int
            self.assertEqual(libc_open(b"", 0), -1)
            self.assertEqual(get_errno(), 0)

        t = threading.Thread(target=_worker)
        t.start()
        t.join()

        self.assertEqual(get_errno(), 32)
        set_errno(0)

    @unittest.skipUnless(os.name == "nt", 'Test specific to Windows')
    eleza test_GetLastError(self):
        dll = WinDLL("kernel32", use_last_error=Kweli)
        GetModuleHandle = dll.GetModuleHandleA
        GetModuleHandle.argtypes = [c_wchar_p]

        self.assertEqual(0, GetModuleHandle("foo"))
        self.assertEqual(get_last_error(), 126)

        self.assertEqual(set_last_error(32), 126)
        self.assertEqual(get_last_error(), 32)

        eleza _worker():
            set_last_error(0)

            dll = WinDLL("kernel32", use_last_error=Uongo)
            GetModuleHandle = dll.GetModuleHandleW
            GetModuleHandle.argtypes = [c_wchar_p]
            GetModuleHandle("bar")

            self.assertEqual(get_last_error(), 0)

        t = threading.Thread(target=_worker)
        t.start()
        t.join()

        self.assertEqual(get_last_error(), 32)

        set_last_error(0)

ikiwa __name__ == "__main__":
    unittest.main()
