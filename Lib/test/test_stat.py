agiza unittest
agiza os
agiza socket
agiza sys
kutoka test.support agiza (TESTFN, import_fresh_module,
                          skip_unless_bind_unix_socket)

c_stat = import_fresh_module('stat', fresh=['_stat'])
py_stat = import_fresh_module('stat', blocked=['_stat'])

kundi TestFilemode:
    statmod = Tupu

    file_flags = {'SF_APPEND', 'SF_ARCHIVED', 'SF_IMMUTABLE', 'SF_NOUNLINK',
                  'SF_SNAPSHOT', 'UF_APPEND', 'UF_COMPRESSED', 'UF_HIDDEN',
                  'UF_IMMUTABLE', 'UF_NODUMP', 'UF_NOUNLINK', 'UF_OPAQUE'}

    formats = {'S_IFBLK', 'S_IFCHR', 'S_IFDIR', 'S_IFIFO', 'S_IFLNK',
               'S_IFREG', 'S_IFSOCK', 'S_IFDOOR', 'S_IFPORT', 'S_IFWHT'}

    format_funcs = {'S_ISBLK', 'S_ISCHR', 'S_ISDIR', 'S_ISFIFO', 'S_ISLNK',
                    'S_ISREG', 'S_ISSOCK', 'S_ISDOOR', 'S_ISPORT', 'S_ISWHT'}

    stat_struct = {
        'ST_MODE': 0,
        'ST_INO': 1,
        'ST_DEV': 2,
        'ST_NLINK': 3,
        'ST_UID': 4,
        'ST_GID': 5,
        'ST_SIZE': 6,
        'ST_ATIME': 7,
        'ST_MTIME': 8,
        'ST_CTIME': 9}

    # permission bit value are defined by POSIX
    permission_bits = {
        'S_ISUID': 0o4000,
        'S_ISGID': 0o2000,
        'S_ENFMT': 0o2000,
        'S_ISVTX': 0o1000,
        'S_IRWXU': 0o700,
        'S_IRUSR': 0o400,
        'S_IREAD': 0o400,
        'S_IWUSR': 0o200,
        'S_IWRITE': 0o200,
        'S_IXUSR': 0o100,
        'S_IEXEC': 0o100,
        'S_IRWXG': 0o070,
        'S_IRGRP': 0o040,
        'S_IWGRP': 0o020,
        'S_IXGRP': 0o010,
        'S_IRWXO': 0o007,
        'S_IROTH': 0o004,
        'S_IWOTH': 0o002,
        'S_IXOTH': 0o001}

    # defined by the Windows API documentation
    file_attributes = {
        'FILE_ATTRIBUTE_ARCHIVE': 32,
        'FILE_ATTRIBUTE_COMPRESSED': 2048,
        'FILE_ATTRIBUTE_DEVICE': 64,
        'FILE_ATTRIBUTE_DIRECTORY': 16,
        'FILE_ATTRIBUTE_ENCRYPTED': 16384,
        'FILE_ATTRIBUTE_HIDDEN': 2,
        'FILE_ATTRIBUTE_INTEGRITY_STREAM': 32768,
        'FILE_ATTRIBUTE_NORMAL': 128,
        'FILE_ATTRIBUTE_NOT_CONTENT_INDEXED': 8192,
        'FILE_ATTRIBUTE_NO_SCRUB_DATA': 131072,
        'FILE_ATTRIBUTE_OFFLINE': 4096,
        'FILE_ATTRIBUTE_READONLY': 1,
        'FILE_ATTRIBUTE_REPARSE_POINT': 1024,
        'FILE_ATTRIBUTE_SPARSE_FILE': 512,
        'FILE_ATTRIBUTE_SYSTEM': 4,
        'FILE_ATTRIBUTE_TEMPORARY': 256,
        'FILE_ATTRIBUTE_VIRTUAL': 65536}

    eleza setUp(self):
        jaribu:
            os.remove(TESTFN)
        tatizo OSError:
            jaribu:
                os.rmdir(TESTFN)
            tatizo OSError:
                pita
    tearDown = setUp

    eleza get_mode(self, fname=TESTFN, lstat=Kweli):
        ikiwa lstat:
            st_mode = os.lstat(fname).st_mode
        isipokua:
            st_mode = os.stat(fname).st_mode
        modestr = self.statmod.filemode(st_mode)
        rudisha st_mode, modestr

    eleza assertS_IS(self, name, mode):
        # test format, lstrip ni kila S_IFIFO
        fmt = getattr(self.statmod, "S_IF" + name.lstrip("F"))
        self.assertEqual(self.statmod.S_IFMT(mode), fmt)
        # test that just one function rudishas true
        testname = "S_IS" + name
        kila funcname kwenye self.format_funcs:
            func = getattr(self.statmod, funcname, Tupu)
            ikiwa func ni Tupu:
                ikiwa funcname == testname:
                    ashiria ValueError(funcname)
                endelea
            ikiwa funcname == testname:
                self.assertKweli(func(mode))
            isipokua:
                self.assertUongo(func(mode))

    eleza test_mode(self):
        ukijumuisha open(TESTFN, 'w'):
            pita
        ikiwa os.name == 'posix':
            os.chmod(TESTFN, 0o700)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr, '-rwx------')
            self.assertS_IS("REG", st_mode)
            self.assertEqual(self.statmod.S_IMODE(st_mode),
                             self.statmod.S_IRWXU)

            os.chmod(TESTFN, 0o070)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr, '----rwx---')
            self.assertS_IS("REG", st_mode)
            self.assertEqual(self.statmod.S_IMODE(st_mode),
                             self.statmod.S_IRWXG)

            os.chmod(TESTFN, 0o007)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr, '-------rwx')
            self.assertS_IS("REG", st_mode)
            self.assertEqual(self.statmod.S_IMODE(st_mode),
                             self.statmod.S_IRWXO)

            os.chmod(TESTFN, 0o444)
            st_mode, modestr = self.get_mode()
            self.assertS_IS("REG", st_mode)
            self.assertEqual(modestr, '-r--r--r--')
            self.assertEqual(self.statmod.S_IMODE(st_mode), 0o444)
        isipokua:
            os.chmod(TESTFN, 0o700)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr[:3], '-rw')
            self.assertS_IS("REG", st_mode)
            self.assertEqual(self.statmod.S_IFMT(st_mode),
                             self.statmod.S_IFREG)

    eleza test_directory(self):
        os.mkdir(TESTFN)
        os.chmod(TESTFN, 0o700)
        st_mode, modestr = self.get_mode()
        self.assertS_IS("DIR", st_mode)
        ikiwa os.name == 'posix':
            self.assertEqual(modestr, 'drwx------')
        isipokua:
            self.assertEqual(modestr[0], 'd')

    @unittest.skipUnless(hasattr(os, 'symlink'), 'os.symlink sio available')
    eleza test_link(self):
        jaribu:
            os.symlink(os.getcwd(), TESTFN)
        tatizo (OSError, NotImplementedError) kama err:
            ashiria unittest.SkipTest(str(err))
        isipokua:
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr[0], 'l')
            self.assertS_IS("LNK", st_mode)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'os.mkfifo sio available')
    eleza test_fifo(self):
        jaribu:
            os.mkfifo(TESTFN, 0o700)
        tatizo PermissionError kama e:
            self.skipTest('os.mkfifo(): %s' % e)
        st_mode, modestr = self.get_mode()
        self.assertEqual(modestr, 'prwx------')
        self.assertS_IS("FIFO", st_mode)

    @unittest.skipUnless(os.name == 'posix', 'requires Posix')
    eleza test_devices(self):
        ikiwa os.path.exists(os.devnull):
            st_mode, modestr = self.get_mode(os.devnull, lstat=Uongo)
            self.assertEqual(modestr[0], 'c')
            self.assertS_IS("CHR", st_mode)
        # Linux block devices, BSD has no block devices anymore
        kila blockdev kwenye ("/dev/sda", "/dev/hda"):
            ikiwa os.path.exists(blockdev):
                st_mode, modestr = self.get_mode(blockdev, lstat=Uongo)
                self.assertEqual(modestr[0], 'b')
                self.assertS_IS("BLK", st_mode)
                koma

    @skip_unless_bind_unix_socket
    eleza test_socket(self):
        ukijumuisha socket.socket(socket.AF_UNIX) kama s:
            s.bind(TESTFN)
            st_mode, modestr = self.get_mode()
            self.assertEqual(modestr[0], 's')
            self.assertS_IS("SOCK", st_mode)

    eleza test_module_attributes(self):
        kila key, value kwenye self.stat_struct.items():
            modvalue = getattr(self.statmod, key)
            self.assertEqual(value, modvalue, key)
        kila key, value kwenye self.permission_bits.items():
            modvalue = getattr(self.statmod, key)
            self.assertEqual(value, modvalue, key)
        kila key kwenye self.file_flags:
            modvalue = getattr(self.statmod, key)
            self.assertIsInstance(modvalue, int)
        kila key kwenye self.formats:
            modvalue = getattr(self.statmod, key)
            self.assertIsInstance(modvalue, int)
        kila key kwenye self.format_funcs:
            func = getattr(self.statmod, key)
            self.assertKweli(callable(func))
            self.assertEqual(func(0), 0)

    @unittest.skipUnless(sys.platform == "win32",
                         "FILE_ATTRIBUTE_* constants are Win32 specific")
    eleza test_file_attribute_constants(self):
        kila key, value kwenye sorted(self.file_attributes.items()):
            self.assertKweli(hasattr(self.statmod, key), key)
            modvalue = getattr(self.statmod, key)
            self.assertEqual(value, modvalue, key)


kundi TestFilemodeCStat(TestFilemode, unittest.TestCase):
    statmod = c_stat


kundi TestFilemodePyStat(TestFilemode, unittest.TestCase):
    statmod = py_stat


ikiwa __name__ == '__main__':
    unittest.main()
