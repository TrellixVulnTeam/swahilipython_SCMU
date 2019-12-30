kutoka ctypes agiza *
agiza os
agiza shutil
agiza subprocess
agiza sys
agiza sysconfig
agiza unittest
agiza test.support
kutoka ctypes.util agiza find_library

libc_name = Tupu

eleza setUpModule():
    global libc_name
    ikiwa os.name == "nt":
        libc_name = find_library("c")
    lasivyo sys.platform == "cygwin":
        libc_name = "cygwin1.dll"
    isipokua:
        libc_name = find_library("c")

    ikiwa test.support.verbose:
        andika("libc_name is", libc_name)

kundi LoaderTest(unittest.TestCase):

    unknowndll = "xxrandomnamexx"

    eleza test_load(self):
        ikiwa libc_name ni Tupu:
            self.skipTest('could sio find libc')
        CDLL(libc_name)
        CDLL(os.path.basename(libc_name))
        self.assertRaises(OSError, CDLL, self.unknowndll)

    eleza test_load_version(self):
        ikiwa libc_name ni Tupu:
            self.skipTest('could sio find libc')
        ikiwa os.path.basename(libc_name) != 'libc.so.6':
            self.skipTest('wrong libc path kila test')
        cdll.LoadLibrary("libc.so.6")
        # linux uses version, libc 9 should sio exist
        self.assertRaises(OSError, cdll.LoadLibrary, "libc.so.9")
        self.assertRaises(OSError, cdll.LoadLibrary, self.unknowndll)

    eleza test_find(self):
        kila name kwenye ("c", "m"):
            lib = find_library(name)
            ikiwa lib:
                cdll.LoadLibrary(lib)
                CDLL(lib)

    @unittest.skipUnless(os.name == "nt",
                         'test specific to Windows')
    eleza test_load_library(self):
        # CRT ni no longer directly loadable. See issue23606 kila the
        # discussion about alternative approaches.
        #self.assertIsNotTupu(libc_name)
        ikiwa test.support.verbose:
            andika(find_library("kernel32"))
            andika(find_library("user32"))

        ikiwa os.name == "nt":
            windll.kernel32.GetModuleHandleW
            windll["kernel32"].GetModuleHandleW
            windll.LoadLibrary("kernel32").GetModuleHandleW
            WinDLL("kernel32").GetModuleHandleW
            # embedded null character
            self.assertRaises(ValueError, windll.LoadLibrary, "kernel32\0")

    @unittest.skipUnless(os.name == "nt",
                         'test specific to Windows')
    eleza test_load_ordinal_functions(self):
        agiza _ctypes_test
        dll = WinDLL(_ctypes_test.__file__)
        # We load the same function both via ordinal na name
        func_ord = dll[2]
        func_name = dll.GetString
        # addressof gets the address where the function pointer ni stored
        a_ord = addressof(func_ord)
        a_name = addressof(func_name)
        f_ord_addr = c_void_p.from_address(a_ord).value
        f_name_addr = c_void_p.from_address(a_name).value
        self.assertEqual(hex(f_ord_addr), hex(f_name_addr))

        self.assertRaises(AttributeError, dll.__getitem__, 1234)

    @unittest.skipUnless(os.name == "nt", 'Windows-specific test')
    eleza test_1703286_A(self):
        kutoka _ctypes agiza LoadLibrary, FreeLibrary
        # On winXP 64-bit, advapi32 loads at an address that does
        # NOT fit into a 32-bit integer.  FreeLibrary must be able
        # to accept this address.

        # These are tests kila http://www.python.org/sf/1703286
        handle = LoadLibrary("advapi32")
        FreeLibrary(handle)

    @unittest.skipUnless(os.name == "nt", 'Windows-specific test')
    eleza test_1703286_B(self):
        # Since on winXP 64-bit advapi32 loads like described
        # above, the (arbitrarily selected) CloseEventLog function
        # also has a high address.  'call_function' should accept
        # addresses so large.
        kutoka _ctypes agiza call_function
        advapi32 = windll.advapi32
        # Calling CloseEventLog ukijumuisha a NULL argument should fail,
        # but the call should sio segfault ama so.
        self.assertEqual(0, advapi32.CloseEventLog(Tupu))
        windll.kernel32.GetProcAddress.argtypes = c_void_p, c_char_p
        windll.kernel32.GetProcAddress.restype = c_void_p
        proc = windll.kernel32.GetProcAddress(advapi32._handle,
                                              b"CloseEventLog")
        self.assertKweli(proc)
        # This ni the real test: call the function via 'call_function'
        self.assertEqual(0, call_function(proc, (Tupu,)))

    @unittest.skipUnless(os.name == "nt",
                         'test specific to Windows')
    eleza test_load_dll_with_flags(self):
        _sqlite3 = test.support.import_module("_sqlite3")
        src = _sqlite3.__file__
        ikiwa src.lower().endswith("_d.pyd"):
            ext = "_d.dll"
        isipokua:
            ext = ".dll"

        ukijumuisha test.support.temp_dir() kama tmp:
            # We copy two files na load _sqlite3.dll (formerly .pyd),
            # which has a dependency on sqlite3.dll. Then we test
            # loading it kwenye subprocesses to avoid it starting kwenye memory
            # kila each test.
            target = os.path.join(tmp, "_sqlite3.dll")
            shutil.copy(src, target)
            shutil.copy(os.path.join(os.path.dirname(src), "sqlite3" + ext),
                        os.path.join(tmp, "sqlite3" + ext))

            eleza should_pita(command):
                ukijumuisha self.subTest(command):
                    subprocess.check_output(
                        [sys.executable, "-c",
                         "kutoka ctypes agiza *; agiza nt;" + command],
                        cwd=tmp
                    )

            eleza should_fail(command):
                ukijumuisha self.subTest(command):
                    ukijumuisha self.assertRaises(subprocess.CalledProcessError):
                        subprocess.check_output(
                            [sys.executable, "-c",
                             "kutoka ctypes agiza *; agiza nt;" + command],
                            cwd=tmp, stderr=subprocess.STDOUT,
                        )

            # Default load should sio find this kwenye CWD
            should_fail("WinDLL('_sqlite3.dll')")

            # Relative path (but sio just filename) should succeed
            should_pita("WinDLL('./_sqlite3.dll')")

            # Insecure load flags should succeed
            should_pita("WinDLL('_sqlite3.dll', winmode=0)")

            # Full path load without DLL_LOAD_DIR shouldn't find dependency
            should_fail("WinDLL(nt._getfullpathname('_sqlite3.dll'), " +
                        "winmode=nt._LOAD_LIBRARY_SEARCH_SYSTEM32)")

            # Full path load ukijumuisha DLL_LOAD_DIR should succeed
            should_pita("WinDLL(nt._getfullpathname('_sqlite3.dll'), " +
                        "winmode=nt._LOAD_LIBRARY_SEARCH_SYSTEM32|" +
                        "nt._LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR)")

            # User-specified directory should succeed
            should_pita("agiza os; p = os.add_dll_directory(os.getcwd());" +
                        "WinDLL('_sqlite3.dll'); p.close()")



ikiwa __name__ == "__main__":
    unittest.main()
