agiza sys
agiza os
agiza io
kutoka hashlib agiza sha256
kutoka contextlib agiza contextmanager
kutoka random agiza Random
agiza pathlib

agiza unittest
agiza unittest.mock
agiza tarfile

kutoka test agiza support
kutoka test.support agiza script_helper, requires_hashdigest

# Check for our compression modules.
try:
    agiza gzip
except ImportError:
    gzip = None
try:
    agiza bz2
except ImportError:
    bz2 = None
try:
    agiza lzma
except ImportError:
    lzma = None

eleza sha256sum(data):
    rudisha sha256(data).hexdigest()

TEMPDIR = os.path.abspath(support.TESTFN) + "-tardir"
tarextdir = TEMPDIR + '-extract-test'
tarname = support.findfile("testtar.tar")
gzipname = os.path.join(TEMPDIR, "testtar.tar.gz")
bz2name = os.path.join(TEMPDIR, "testtar.tar.bz2")
xzname = os.path.join(TEMPDIR, "testtar.tar.xz")
tmpname = os.path.join(TEMPDIR, "tmp.tar")
dotlessname = os.path.join(TEMPDIR, "testtar")

sha256_regtype = (
    "e09e4bc8b3c9d9177e77256353b36c159f5f040531bbd4b024a8f9b9196c71ce"
)
sha256_sparse = (
    "4f05a776071146756345ceee937b33fc5644f5a96b9780d1c7d6a32cdf164d7b"
)


kundi TarTest:
    tarname = tarname
    suffix = ''
    open = io.FileIO
    taropen = tarfile.TarFile.taropen

    @property
    eleza mode(self):
        rudisha self.prefix + self.suffix

@support.requires_gzip
kundi GzipTest:
    tarname = gzipname
    suffix = 'gz'
    open = gzip.GzipFile ikiwa gzip else None
    taropen = tarfile.TarFile.gzopen

@support.requires_bz2
kundi Bz2Test:
    tarname = bz2name
    suffix = 'bz2'
    open = bz2.BZ2File ikiwa bz2 else None
    taropen = tarfile.TarFile.bz2open

@support.requires_lzma
kundi LzmaTest:
    tarname = xzname
    suffix = 'xz'
    open = lzma.LZMAFile ikiwa lzma else None
    taropen = tarfile.TarFile.xzopen


kundi ReadTest(TarTest):

    prefix = "r:"

    eleza setUp(self):
        self.tar = tarfile.open(self.tarname, mode=self.mode,
                                encoding="iso8859-1")

    eleza tearDown(self):
        self.tar.close()


kundi UstarReadTest(ReadTest, unittest.TestCase):

    eleza test_fileobj_regular_file(self):
        tarinfo = self.tar.getmember("ustar/regtype")
        with self.tar.extractfile(tarinfo) as fobj:
            data = fobj.read()
            self.assertEqual(len(data), tarinfo.size,
                    "regular file extraction failed")
            self.assertEqual(sha256sum(data), sha256_regtype,
                    "regular file extraction failed")

    eleza test_fileobj_readlines(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        tarinfo = self.tar.getmember("ustar/regtype")
        with open(os.path.join(TEMPDIR, "ustar/regtype"), "r") as fobj1:
            lines1 = fobj1.readlines()

        with self.tar.extractfile(tarinfo) as fobj:
            fobj2 = io.TextIOWrapper(fobj)
            lines2 = fobj2.readlines()
            self.assertEqual(lines1, lines2,
                    "fileobj.readlines() failed")
            self.assertEqual(len(lines2), 114,
                    "fileobj.readlines() failed")
            self.assertEqual(lines2[83],
                    "I will gladly admit that Python is not the fastest "
                    "running scripting language.\n",
                    "fileobj.readlines() failed")

    eleza test_fileobj_iter(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        tarinfo = self.tar.getmember("ustar/regtype")
        with open(os.path.join(TEMPDIR, "ustar/regtype"), "r") as fobj1:
            lines1 = fobj1.readlines()
        with self.tar.extractfile(tarinfo) as fobj2:
            lines2 = list(io.TextIOWrapper(fobj2))
            self.assertEqual(lines1, lines2,
                    "fileobj.__iter__() failed")

    eleza test_fileobj_seek(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        with open(os.path.join(TEMPDIR, "ustar/regtype"), "rb") as fobj:
            data = fobj.read()

        tarinfo = self.tar.getmember("ustar/regtype")
        with self.tar.extractfile(tarinfo) as fobj:
            text = fobj.read()
            fobj.seek(0)
            self.assertEqual(0, fobj.tell(),
                         "seek() to file's start failed")
            fobj.seek(2048, 0)
            self.assertEqual(2048, fobj.tell(),
                         "seek() to absolute position failed")
            fobj.seek(-1024, 1)
            self.assertEqual(1024, fobj.tell(),
                         "seek() to negative relative position failed")
            fobj.seek(1024, 1)
            self.assertEqual(2048, fobj.tell(),
                         "seek() to positive relative position failed")
            s = fobj.read(10)
            self.assertEqual(s, data[2048:2058],
                         "read() after seek failed")
            fobj.seek(0, 2)
            self.assertEqual(tarinfo.size, fobj.tell(),
                         "seek() to file's end failed")
            self.assertEqual(fobj.read(), b"",
                         "read() at file's end did not rudisha empty string")
            fobj.seek(-tarinfo.size, 2)
            self.assertEqual(0, fobj.tell(),
                         "relative seek() to file's end failed")
            fobj.seek(512)
            s1 = fobj.readlines()
            fobj.seek(512)
            s2 = fobj.readlines()
            self.assertEqual(s1, s2,
                         "readlines() after seek failed")
            fobj.seek(0)
            self.assertEqual(len(fobj.readline()), fobj.tell(),
                         "tell() after readline() failed")
            fobj.seek(512)
            self.assertEqual(len(fobj.readline()) + 512, fobj.tell(),
                         "tell() after seek() and readline() failed")
            fobj.seek(0)
            line = fobj.readline()
            self.assertEqual(fobj.read(), data[len(line):],
                         "read() after readline() failed")

    eleza test_fileobj_text(self):
        with self.tar.extractfile("ustar/regtype") as fobj:
            fobj = io.TextIOWrapper(fobj)
            data = fobj.read().encode("iso8859-1")
            self.assertEqual(sha256sum(data), sha256_regtype)
            try:
                fobj.seek(100)
            except AttributeError:
                # Issue #13815: seek() complained about a missing
                # flush() method.
                self.fail("seeking failed in text mode")

    # Test ikiwa symbolic and hard links are resolved by extractfile().  The
    # test link members each point to a regular member whose data is
    # supposed to be exported.
    eleza _test_fileobj_link(self, lnktype, regtype):
        with self.tar.extractfile(lnktype) as a, \
             self.tar.extractfile(regtype) as b:
            self.assertEqual(a.name, b.name)

    eleza test_fileobj_link1(self):
        self._test_fileobj_link("ustar/lnktype", "ustar/regtype")

    eleza test_fileobj_link2(self):
        self._test_fileobj_link("./ustar/linktest2/lnktype",
                                "ustar/linktest1/regtype")

    eleza test_fileobj_symlink1(self):
        self._test_fileobj_link("ustar/symtype", "ustar/regtype")

    eleza test_fileobj_symlink2(self):
        self._test_fileobj_link("./ustar/linktest2/symtype",
                                "ustar/linktest1/regtype")

    eleza test_issue14160(self):
        self._test_fileobj_link("symtype2", "ustar/regtype")

kundi GzipUstarReadTest(GzipTest, UstarReadTest):
    pass

kundi Bz2UstarReadTest(Bz2Test, UstarReadTest):
    pass

kundi LzmaUstarReadTest(LzmaTest, UstarReadTest):
    pass


kundi ListTest(ReadTest, unittest.TestCase):

    # Override setUp to use default encoding (UTF-8)
    eleza setUp(self):
        self.tar = tarfile.open(self.tarname, mode=self.mode)

    eleza test_list(self):
        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
        with support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=False)
        out = tio.detach().getvalue()
        self.assertIn(b'ustar/conttype', out)
        self.assertIn(b'ustar/regtype', out)
        self.assertIn(b'ustar/lnktype', out)
        self.assertIn(b'ustar' + (b'/12345' * 40) + b'67/longname', out)
        self.assertIn(b'./ustar/linktest2/symtype', out)
        self.assertIn(b'./ustar/linktest2/lnktype', out)
        # Make sure it puts trailing slash for directory
        self.assertIn(b'ustar/dirtype/', out)
        self.assertIn(b'ustar/dirtype-with-size/', out)
        # Make sure it is able to print unencodable characters
        eleza conv(b):
            s = b.decode(self.tar.encoding, 'surrogateescape')
            rudisha s.encode('ascii', 'backslashreplace')
        self.assertIn(conv(b'ustar/umlauts-\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
        self.assertIn(conv(b'misc/regtype-hpux-signed-chksum-'
                           b'\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
        self.assertIn(conv(b'misc/regtype-old-v7-signed-chksum-'
                           b'\xc4\xd6\xdc\xe4\xf6\xfc\xdf'), out)
        self.assertIn(conv(b'pax/bad-pax-\xe4\xf6\xfc'), out)
        self.assertIn(conv(b'pax/hdrcharset-\xe4\xf6\xfc'), out)
        # Make sure it prints files separated by one newline without any
        # 'ls -l'-like accessories ikiwa verbose flag is not being used
        # ...
        # ustar/conttype
        # ustar/regtype
        # ...
        self.assertRegex(out, br'ustar/conttype ?\r?\n'
                              br'ustar/regtype ?\r?\n')
        # Make sure it does not print the source of link without verbose flag
        self.assertNotIn(b'link to', out)
        self.assertNotIn(b'->', out)

    eleza test_list_verbose(self):
        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
        with support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=True)
        out = tio.detach().getvalue()
        # Make sure it prints files separated by one newline with 'ls -l'-like
        # accessories ikiwa verbose flag is being used
        # ...
        # ?rw-r--r-- tarfile/tarfile     7011 2003-01-06 07:19:43 ustar/conttype
        # ?rw-r--r-- tarfile/tarfile     7011 2003-01-06 07:19:43 ustar/regtype
        # ...
        self.assertRegex(out, (br'\?rw-r--r-- tarfile/tarfile\s+7011 '
                               br'\d{4}-\d\d-\d\d\s+\d\d:\d\d:\d\d '
                               br'ustar/\w+type ?\r?\n') * 2)
        # Make sure it prints the source of link with verbose flag
        self.assertIn(b'ustar/symtype -> regtype', out)
        self.assertIn(b'./ustar/linktest2/symtype -> ../linktest1/regtype', out)
        self.assertIn(b'./ustar/linktest2/lnktype link to '
                      b'./ustar/linktest1/regtype', out)
        self.assertIn(b'gnu' + (b'/123' * 125) + b'/longlink link to gnu' +
                      (b'/123' * 125) + b'/longname', out)
        self.assertIn(b'pax' + (b'/123' * 125) + b'/longlink link to pax' +
                      (b'/123' * 125) + b'/longname', out)

    eleza test_list_members(self):
        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
        eleza members(tar):
            for tarinfo in tar.getmembers():
                ikiwa 'reg' in tarinfo.name:
                    yield tarinfo
        with support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=False, members=members(self.tar))
        out = tio.detach().getvalue()
        self.assertIn(b'ustar/regtype', out)
        self.assertNotIn(b'ustar/conttype', out)


kundi GzipListTest(GzipTest, ListTest):
    pass


kundi Bz2ListTest(Bz2Test, ListTest):
    pass


kundi LzmaListTest(LzmaTest, ListTest):
    pass


kundi CommonReadTest(ReadTest):

    eleza test_empty_tarfile(self):
        # Test for issue6123: Allow opening empty archives.
        # This test checks ikiwa tarfile.open() is able to open an empty tar
        # archive successfully. Note that an empty tar archive is not the
        # same as an empty file!
        with tarfile.open(tmpname, self.mode.replace("r", "w")):
            pass
        try:
            tar = tarfile.open(tmpname, self.mode)
            tar.getnames()
        except tarfile.ReadError:
            self.fail("tarfile.open() failed on empty archive")
        else:
            self.assertListEqual(tar.getmembers(), [])
        finally:
            tar.close()

    eleza test_non_existent_tarfile(self):
        # Test for issue11513: prevent non-existent gzipped tarfiles raising
        # multiple exceptions.
        with self.assertRaisesRegex(FileNotFoundError, "xxx"):
            tarfile.open("xxx", self.mode)

    eleza test_null_tarfile(self):
        # Test for issue6123: Allow opening empty archives.
        # This test guarantees that tarfile.open() does not treat an empty
        # file as an empty tar archive.
        with open(tmpname, "wb"):
            pass
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname, self.mode)
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname)

    eleza test_ignore_zeros(self):
        # Test TarFile's ignore_zeros option.
        # generate 512 pseudorandom bytes
        data = Random(0).getrandbits(512*8).to_bytes(512, 'big')
        for char in (b'\0', b'a'):
            # Test ikiwa EOFHeaderError ('\0') and InvalidHeaderError ('a')
            # are ignored correctly.
            with self.open(tmpname, "w") as fobj:
                fobj.write(char * 1024)
                tarinfo = tarfile.TarInfo("foo")
                tarinfo.size = len(data)
                fobj.write(tarinfo.tobuf())
                fobj.write(data)

            tar = tarfile.open(tmpname, mode="r", ignore_zeros=True)
            try:
                self.assertListEqual(tar.getnames(), ["foo"],
                    "ignore_zeros=True should have skipped the %r-blocks" %
                    char)
            finally:
                tar.close()

    eleza test_premature_end_of_archive(self):
        for size in (512, 600, 1024, 1200):
            with tarfile.open(tmpname, "w:") as tar:
                t = tarfile.TarInfo("foo")
                t.size = 1024
                tar.addfile(t, io.BytesIO(b"a" * 1024))

            with open(tmpname, "r+b") as fobj:
                fobj.truncate(size)

            with tarfile.open(tmpname) as tar:
                with self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    for t in tar:
                        pass

            with tarfile.open(tmpname) as tar:
                t = tar.next()

                with self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    tar.extract(t, TEMPDIR)

                with self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    tar.extractfile(t).read()

kundi MiscReadTestBase(CommonReadTest):
    eleza requires_name_attribute(self):
        pass

    eleza test_no_name_argument(self):
        self.requires_name_attribute()
        with open(self.tarname, "rb") as fobj:
            self.assertIsInstance(fobj.name, str)
            with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
                self.assertIsInstance(tar.name, str)
                self.assertEqual(tar.name, os.path.abspath(fobj.name))

    eleza test_no_name_attribute(self):
        with open(self.tarname, "rb") as fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        self.assertRaises(AttributeError, getattr, fobj, "name")
        tar = tarfile.open(fileobj=fobj, mode=self.mode)
        self.assertIsNone(tar.name)

    eleza test_empty_name_attribute(self):
        with open(self.tarname, "rb") as fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        fobj.name = ""
        with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
            self.assertIsNone(tar.name)

    eleza test_int_name_attribute(self):
        # Issue 21044: tarfile.open() should handle fileobj with an integer
        # 'name' attribute.
        fd = os.open(self.tarname, os.O_RDONLY)
        with open(fd, 'rb') as fobj:
            self.assertIsInstance(fobj.name, int)
            with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
                self.assertIsNone(tar.name)

    eleza test_bytes_name_attribute(self):
        self.requires_name_attribute()
        tarname = os.fsencode(self.tarname)
        with open(tarname, 'rb') as fobj:
            self.assertIsInstance(fobj.name, bytes)
            with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
                self.assertIsInstance(tar.name, bytes)
                self.assertEqual(tar.name, os.path.abspath(fobj.name))

    eleza test_pathlike_name(self):
        tarname = pathlib.Path(self.tarname)
        with tarfile.open(tarname, mode=self.mode) as tar:
            self.assertIsInstance(tar.name, str)
            self.assertEqual(tar.name, os.path.abspath(os.fspath(tarname)))
        with self.taropen(tarname) as tar:
            self.assertIsInstance(tar.name, str)
            self.assertEqual(tar.name, os.path.abspath(os.fspath(tarname)))
        with tarfile.TarFile.open(tarname, mode=self.mode) as tar:
            self.assertIsInstance(tar.name, str)
            self.assertEqual(tar.name, os.path.abspath(os.fspath(tarname)))
        ikiwa self.suffix == '':
            with tarfile.TarFile(tarname, mode='r') as tar:
                self.assertIsInstance(tar.name, str)
                self.assertEqual(tar.name, os.path.abspath(os.fspath(tarname)))

    eleza test_illegal_mode_arg(self):
        with open(tmpname, 'wb'):
            pass
        with self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, 'q')
        with self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, 'rw')
        with self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, '')

    eleza test_fileobj_with_offset(self):
        # Skip the first member and store values kutoka the second member
        # of the testtar.
        tar = tarfile.open(self.tarname, mode=self.mode)
        try:
            tar.next()
            t = tar.next()
            name = t.name
            offset = t.offset
            with tar.extractfile(t) as f:
                data = f.read()
        finally:
            tar.close()

        # Open the testtar and seek to the offset of the second member.
        with self.open(self.tarname) as fobj:
            fobj.seek(offset)

            # Test ikiwa the tarfile starts with the second member.
            with tar.open(self.tarname, mode="r:", fileobj=fobj) as tar:
                t = tar.next()
                self.assertEqual(t.name, name)
                # Read to the end of fileobj and test ikiwa seeking back to the
                # beginning works.
                tar.getmembers()
                self.assertEqual(tar.extractfile(t).read(), data,
                        "seek back did not work")

    eleza test_fail_comp(self):
        # For Gzip and Bz2 Tests: fail with a ReadError on an uncompressed file.
        self.assertRaises(tarfile.ReadError, tarfile.open, tarname, self.mode)
        with open(tarname, "rb") as fobj:
            self.assertRaises(tarfile.ReadError, tarfile.open,
                              fileobj=fobj, mode=self.mode)

    eleza test_v7_dirtype(self):
        # Test old style dirtype member (bug #1336623):
        # Old V7 tars create directory members using an AREGTYPE
        # header with a "/" appended to the filename field.
        tarinfo = self.tar.getmember("misc/dirtype-old-v7")
        self.assertEqual(tarinfo.type, tarfile.DIRTYPE,
                "v7 dirtype failed")

    eleza test_xstar_type(self):
        # The xstar format stores extra atime and ctime fields inside the
        # space reserved for the prefix field. The prefix field must be
        # ignored in this case, otherwise it will mess up the name.
        try:
            self.tar.getmember("misc/regtype-xstar")
        except KeyError:
            self.fail("failed to find misc/regtype-xstar (mangled prefix?)")

    eleza test_check_members(self):
        for tarinfo in self.tar:
            self.assertEqual(int(tarinfo.mtime), 0o7606136617,
                    "wrong mtime for %s" % tarinfo.name)
            ikiwa not tarinfo.name.startswith("ustar/"):
                continue
            self.assertEqual(tarinfo.uname, "tarfile",
                    "wrong uname for %s" % tarinfo.name)

    eleza test_find_members(self):
        self.assertEqual(self.tar.getmembers()[-1].name, "misc/eof",
                "could not find all members")

    @unittest.skipUnless(hasattr(os, "link"),
                         "Missing hardlink implementation")
    @support.skip_unless_symlink
    eleza test_extract_hardlink(self):
        # Test hardlink extraction (e.g. bug #857297).
        with tarfile.open(tarname, errorlevel=1, encoding="iso8859-1") as tar:
            tar.extract("ustar/regtype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/regtype"))

            tar.extract("ustar/lnktype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/lnktype"))
            with open(os.path.join(TEMPDIR, "ustar/lnktype"), "rb") as f:
                data = f.read()
            self.assertEqual(sha256sum(data), sha256_regtype)

            tar.extract("ustar/symtype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/symtype"))
            with open(os.path.join(TEMPDIR, "ustar/symtype"), "rb") as f:
                data = f.read()
            self.assertEqual(sha256sum(data), sha256_regtype)

    eleza test_extractall(self):
        # Test ikiwa extractall() correctly restores directory permissions
        # and times (see issue1735).
        tar = tarfile.open(tarname, encoding="iso8859-1")
        DIR = os.path.join(TEMPDIR, "extractall")
        os.mkdir(DIR)
        try:
            directories = [t for t in tar ikiwa t.isdir()]
            tar.extractall(DIR, directories)
            for tarinfo in directories:
                path = os.path.join(DIR, tarinfo.name)
                ikiwa sys.platform != "win32":
                    # Win32 has no support for fine grained permissions.
                    self.assertEqual(tarinfo.mode & 0o777,
                                     os.stat(path).st_mode & 0o777)
                eleza format_mtime(mtime):
                    ikiwa isinstance(mtime, float):
                        rudisha "{} ({})".format(mtime, mtime.hex())
                    else:
                        rudisha "{!r} (int)".format(mtime)
                file_mtime = os.path.getmtime(path)
                errmsg = "tar mtime {0} != file time {1} of path {2!a}".format(
                    format_mtime(tarinfo.mtime),
                    format_mtime(file_mtime),
                    path)
                self.assertEqual(tarinfo.mtime, file_mtime, errmsg)
        finally:
            tar.close()
            support.rmtree(DIR)

    eleza test_extract_directory(self):
        dirtype = "ustar/dirtype"
        DIR = os.path.join(TEMPDIR, "extractdir")
        os.mkdir(DIR)
        try:
            with tarfile.open(tarname, encoding="iso8859-1") as tar:
                tarinfo = tar.getmember(dirtype)
                tar.extract(tarinfo, path=DIR)
                extracted = os.path.join(DIR, dirtype)
                self.assertEqual(os.path.getmtime(extracted), tarinfo.mtime)
                ikiwa sys.platform != "win32":
                    self.assertEqual(os.stat(extracted).st_mode & 0o777, 0o755)
        finally:
            support.rmtree(DIR)

    eleza test_extractall_pathlike_name(self):
        DIR = pathlib.Path(TEMPDIR) / "extractall"
        with support.temp_dir(DIR), \
             tarfile.open(tarname, encoding="iso8859-1") as tar:
            directories = [t for t in tar ikiwa t.isdir()]
            tar.extractall(DIR, directories)
            for tarinfo in directories:
                path = DIR / tarinfo.name
                self.assertEqual(os.path.getmtime(path), tarinfo.mtime)

    eleza test_extract_pathlike_name(self):
        dirtype = "ustar/dirtype"
        DIR = pathlib.Path(TEMPDIR) / "extractall"
        with support.temp_dir(DIR), \
             tarfile.open(tarname, encoding="iso8859-1") as tar:
            tarinfo = tar.getmember(dirtype)
            tar.extract(tarinfo, path=DIR)
            extracted = DIR / dirtype
            self.assertEqual(os.path.getmtime(extracted), tarinfo.mtime)

    eleza test_init_close_fobj(self):
        # Issue #7341: Close the internal file object in the TarFile
        # constructor in case of an error. For the test we rely on
        # the fact that opening an empty file raises a ReadError.
        empty = os.path.join(TEMPDIR, "empty")
        with open(empty, "wb") as fobj:
            fobj.write(b"")

        try:
            tar = object.__new__(tarfile.TarFile)
            try:
                tar.__init__(empty)
            except tarfile.ReadError:
                self.assertTrue(tar.fileobj.closed)
            else:
                self.fail("ReadError not raised")
        finally:
            support.unlink(empty)

    eleza test_parallel_iteration(self):
        # Issue #16601: Restarting iteration over tarfile continued
        # kutoka where it left off.
        with tarfile.open(self.tarname) as tar:
            for m1, m2 in zip(tar, tar):
                self.assertEqual(m1.offset, m2.offset)
                self.assertEqual(m1.get_info(), m2.get_info())

kundi MiscReadTest(MiscReadTestBase, unittest.TestCase):
    test_fail_comp = None

kundi GzipMiscReadTest(GzipTest, MiscReadTestBase, unittest.TestCase):
    pass

kundi Bz2MiscReadTest(Bz2Test, MiscReadTestBase, unittest.TestCase):
    eleza requires_name_attribute(self):
        self.skipTest("BZ2File have no name attribute")

kundi LzmaMiscReadTest(LzmaTest, MiscReadTestBase, unittest.TestCase):
    eleza requires_name_attribute(self):
        self.skipTest("LZMAFile have no name attribute")


kundi StreamReadTest(CommonReadTest, unittest.TestCase):

    prefix="r|"

    eleza test_read_through(self):
        # Issue #11224: A poorly designed _FileInFile.read() method
        # caused seeking errors with stream tar files.
        for tarinfo in self.tar:
            ikiwa not tarinfo.isreg():
                continue
            with self.tar.extractfile(tarinfo) as fobj:
                while True:
                    try:
                        buf = fobj.read(512)
                    except tarfile.StreamError:
                        self.fail("simple read-through using "
                                  "TarFile.extractfile() failed")
                    ikiwa not buf:
                        break

    eleza test_fileobj_regular_file(self):
        tarinfo = self.tar.next() # get "regtype" (can't use getmember)
        with self.tar.extractfile(tarinfo) as fobj:
            data = fobj.read()
        self.assertEqual(len(data), tarinfo.size,
                "regular file extraction failed")
        self.assertEqual(sha256sum(data), sha256_regtype,
                "regular file extraction failed")

    eleza test_provoke_stream_error(self):
        tarinfos = self.tar.getmembers()
        with self.tar.extractfile(tarinfos[0]) as f: # read the first member
            self.assertRaises(tarfile.StreamError, f.read)

    eleza test_compare_members(self):
        tar1 = tarfile.open(tarname, encoding="iso8859-1")
        try:
            tar2 = self.tar

            while True:
                t1 = tar1.next()
                t2 = tar2.next()
                ikiwa t1 is None:
                    break
                self.assertIsNotNone(t2, "stream.next() failed.")

                ikiwa t2.islnk() or t2.issym():
                    with self.assertRaises(tarfile.StreamError):
                        tar2.extractfile(t2)
                    continue

                v1 = tar1.extractfile(t1)
                v2 = tar2.extractfile(t2)
                ikiwa v1 is None:
                    continue
                self.assertIsNotNone(v2, "stream.extractfile() failed")
                self.assertEqual(v1.read(), v2.read(),
                        "stream extraction failed")
        finally:
            tar1.close()

kundi GzipStreamReadTest(GzipTest, StreamReadTest):
    pass

kundi Bz2StreamReadTest(Bz2Test, StreamReadTest):
    pass

kundi LzmaStreamReadTest(LzmaTest, StreamReadTest):
    pass


kundi DetectReadTest(TarTest, unittest.TestCase):
    eleza _testfunc_file(self, name, mode):
        try:
            tar = tarfile.open(name, mode)
        except tarfile.ReadError as e:
            self.fail()
        else:
            tar.close()

    eleza _testfunc_fileobj(self, name, mode):
        try:
            with open(name, "rb") as f:
                tar = tarfile.open(name, mode, fileobj=f)
        except tarfile.ReadError as e:
            self.fail()
        else:
            tar.close()

    eleza _test_modes(self, testfunc):
        ikiwa self.suffix:
            with self.assertRaises(tarfile.ReadError):
                tarfile.open(tarname, mode="r:" + self.suffix)
            with self.assertRaises(tarfile.ReadError):
                tarfile.open(tarname, mode="r|" + self.suffix)
            with self.assertRaises(tarfile.ReadError):
                tarfile.open(self.tarname, mode="r:")
            with self.assertRaises(tarfile.ReadError):
                tarfile.open(self.tarname, mode="r|")
        testfunc(self.tarname, "r")
        testfunc(self.tarname, "r:" + self.suffix)
        testfunc(self.tarname, "r:*")
        testfunc(self.tarname, "r|" + self.suffix)
        testfunc(self.tarname, "r|*")

    eleza test_detect_file(self):
        self._test_modes(self._testfunc_file)

    eleza test_detect_fileobj(self):
        self._test_modes(self._testfunc_fileobj)

kundi GzipDetectReadTest(GzipTest, DetectReadTest):
    pass

kundi Bz2DetectReadTest(Bz2Test, DetectReadTest):
    eleza test_detect_stream_bz2(self):
        # Originally, tarfile's stream detection looked for the string
        # "BZh91" at the start of the file. This is incorrect because
        # the '9' represents the blocksize (900,000 bytes). If the file was
        # compressed using another blocksize autodetection fails.
        with open(tarname, "rb") as fobj:
            data = fobj.read()

        # Compress with blocksize 100,000 bytes, the file starts with "BZh11".
        with bz2.BZ2File(tmpname, "wb", compresslevel=1) as fobj:
            fobj.write(data)

        self._testfunc_file(tmpname, "r|*")

kundi LzmaDetectReadTest(LzmaTest, DetectReadTest):
    pass


kundi MemberReadTest(ReadTest, unittest.TestCase):

    eleza _test_member(self, tarinfo, chksum=None, **kwargs):
        ikiwa chksum is not None:
            with self.tar.extractfile(tarinfo) as f:
                self.assertEqual(sha256sum(f.read()), chksum,
                        "wrong sha256sum for %s" % tarinfo.name)

        kwargs["mtime"] = 0o7606136617
        kwargs["uid"] = 1000
        kwargs["gid"] = 100
        ikiwa "old-v7" not in tarinfo.name:
            # V7 tar can't handle alphabetic owners.
            kwargs["uname"] = "tarfile"
            kwargs["gname"] = "tarfile"
        for k, v in kwargs.items():
            self.assertEqual(getattr(tarinfo, k), v,
                    "wrong value in %s field of %s" % (k, tarinfo.name))

    eleza test_find_regtype(self):
        tarinfo = self.tar.getmember("ustar/regtype")
        self._test_member(tarinfo, size=7011, chksum=sha256_regtype)

    eleza test_find_conttype(self):
        tarinfo = self.tar.getmember("ustar/conttype")
        self._test_member(tarinfo, size=7011, chksum=sha256_regtype)

    eleza test_find_dirtype(self):
        tarinfo = self.tar.getmember("ustar/dirtype")
        self._test_member(tarinfo, size=0)

    eleza test_find_dirtype_with_size(self):
        tarinfo = self.tar.getmember("ustar/dirtype-with-size")
        self._test_member(tarinfo, size=255)

    eleza test_find_lnktype(self):
        tarinfo = self.tar.getmember("ustar/lnktype")
        self._test_member(tarinfo, size=0, linkname="ustar/regtype")

    eleza test_find_symtype(self):
        tarinfo = self.tar.getmember("ustar/symtype")
        self._test_member(tarinfo, size=0, linkname="regtype")

    eleza test_find_blktype(self):
        tarinfo = self.tar.getmember("ustar/blktype")
        self._test_member(tarinfo, size=0, devmajor=3, devminor=0)

    eleza test_find_chrtype(self):
        tarinfo = self.tar.getmember("ustar/chrtype")
        self._test_member(tarinfo, size=0, devmajor=1, devminor=3)

    eleza test_find_fifotype(self):
        tarinfo = self.tar.getmember("ustar/fifotype")
        self._test_member(tarinfo, size=0)

    eleza test_find_sparse(self):
        tarinfo = self.tar.getmember("ustar/sparse")
        self._test_member(tarinfo, size=86016, chksum=sha256_sparse)

    eleza test_find_gnusparse(self):
        tarinfo = self.tar.getmember("gnu/sparse")
        self._test_member(tarinfo, size=86016, chksum=sha256_sparse)

    eleza test_find_gnusparse_00(self):
        tarinfo = self.tar.getmember("gnu/sparse-0.0")
        self._test_member(tarinfo, size=86016, chksum=sha256_sparse)

    eleza test_find_gnusparse_01(self):
        tarinfo = self.tar.getmember("gnu/sparse-0.1")
        self._test_member(tarinfo, size=86016, chksum=sha256_sparse)

    eleza test_find_gnusparse_10(self):
        tarinfo = self.tar.getmember("gnu/sparse-1.0")
        self._test_member(tarinfo, size=86016, chksum=sha256_sparse)

    eleza test_find_umlauts(self):
        tarinfo = self.tar.getmember("ustar/umlauts-"
                                     "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
        self._test_member(tarinfo, size=7011, chksum=sha256_regtype)

    eleza test_find_ustar_longname(self):
        name = "ustar/" + "12345/" * 39 + "1234567/longname"
        self.assertIn(name, self.tar.getnames())

    eleza test_find_regtype_oldv7(self):
        tarinfo = self.tar.getmember("misc/regtype-old-v7")
        self._test_member(tarinfo, size=7011, chksum=sha256_regtype)

    eleza test_find_pax_umlauts(self):
        self.tar.close()
        self.tar = tarfile.open(self.tarname, mode=self.mode,
                                encoding="iso8859-1")
        tarinfo = self.tar.getmember("pax/umlauts-"
                                     "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
        self._test_member(tarinfo, size=7011, chksum=sha256_regtype)


kundi LongnameTest:

    eleza test_read_longname(self):
        # Test reading of longname (bug #1471427).
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        try:
            tarinfo = self.tar.getmember(longname)
        except KeyError:
            self.fail("longname not found")
        self.assertNotEqual(tarinfo.type, tarfile.DIRTYPE,
                "read longname as dirtype")

    eleza test_read_longlink(self):
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        longlink = self.subdir + "/" + "123/" * 125 + "longlink"
        try:
            tarinfo = self.tar.getmember(longlink)
        except KeyError:
            self.fail("longlink not found")
        self.assertEqual(tarinfo.linkname, longname, "linkname wrong")

    eleza test_truncated_longname(self):
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        tarinfo = self.tar.getmember(longname)
        offset = tarinfo.offset
        self.tar.fileobj.seek(offset)
        fobj = io.BytesIO(self.tar.fileobj.read(3 * 512))
        with self.assertRaises(tarfile.ReadError):
            tarfile.open(name="foo.tar", fileobj=fobj)

    eleza test_header_offset(self):
        # Test ikiwa the start offset of the TarInfo object includes
        # the preceding extended header.
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        offset = self.tar.getmember(longname).offset
        with open(tarname, "rb") as fobj:
            fobj.seek(offset)
            tarinfo = tarfile.TarInfo.kutokabuf(fobj.read(512),
                                              "iso8859-1", "strict")
            self.assertEqual(tarinfo.type, self.longnametype)


kundi GNUReadTest(LongnameTest, ReadTest, unittest.TestCase):

    subdir = "gnu"
    longnametype = tarfile.GNUTYPE_LONGNAME

    # Since 3.2 tarfile is supposed to accurately restore sparse members and
    # produce files with holes. This is what we actually want to test here.
    # Unfortunately, not all platforms/filesystems support sparse files, and
    # even on platforms that do it is non-trivial to make reliable assertions
    # about holes in files. Therefore, we first do one basic test which works
    # an all platforms, and after that a test that will work only on
    # platforms/filesystems that prove to support sparse files.
    eleza _test_sparse_file(self, name):
        self.tar.extract(name, TEMPDIR)
        filename = os.path.join(TEMPDIR, name)
        with open(filename, "rb") as fobj:
            data = fobj.read()
        self.assertEqual(sha256sum(data), sha256_sparse,
                "wrong sha256sum for %s" % name)

        ikiwa self._fs_supports_holes():
            s = os.stat(filename)
            self.assertLess(s.st_blocks * 512, s.st_size)

    eleza test_sparse_file_old(self):
        self._test_sparse_file("gnu/sparse")

    eleza test_sparse_file_00(self):
        self._test_sparse_file("gnu/sparse-0.0")

    eleza test_sparse_file_01(self):
        self._test_sparse_file("gnu/sparse-0.1")

    eleza test_sparse_file_10(self):
        self._test_sparse_file("gnu/sparse-1.0")

    @staticmethod
    eleza _fs_supports_holes():
        # Return True ikiwa the platform knows the st_blocks stat attribute and
        # uses st_blocks units of 512 bytes, and ikiwa the filesystem is able to
        # store holes of 4 KiB in files.
        #
        # The function returns False ikiwa page size is larger than 4 KiB.
        # For example, ppc64 uses pages of 64 KiB.
        ikiwa sys.platform.startswith("linux"):
            # Linux evidentially has 512 byte st_blocks units.
            name = os.path.join(TEMPDIR, "sparse-test")
            with open(name, "wb") as fobj:
                # Seek to "punch a hole" of 4 KiB
                fobj.seek(4096)
                fobj.write(b'x' * 4096)
                fobj.truncate()
            s = os.stat(name)
            support.unlink(name)
            rudisha (s.st_blocks * 512 < s.st_size)
        else:
            rudisha False


kundi PaxReadTest(LongnameTest, ReadTest, unittest.TestCase):

    subdir = "pax"
    longnametype = tarfile.XHDTYPE

    eleza test_pax_global_headers(self):
        tar = tarfile.open(tarname, encoding="iso8859-1")
        try:
            tarinfo = tar.getmember("pax/regtype1")
            self.assertEqual(tarinfo.uname, "foo")
            self.assertEqual(tarinfo.gname, "bar")
            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")

            tarinfo = tar.getmember("pax/regtype2")
            self.assertEqual(tarinfo.uname, "")
            self.assertEqual(tarinfo.gname, "bar")
            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")

            tarinfo = tar.getmember("pax/regtype3")
            self.assertEqual(tarinfo.uname, "tarfile")
            self.assertEqual(tarinfo.gname, "tarfile")
            self.assertEqual(tarinfo.pax_headers.get("VENDOR.umlauts"),
                             "\xc4\xd6\xdc\xe4\xf6\xfc\xdf")
        finally:
            tar.close()

    eleza test_pax_number_fields(self):
        # All following number fields are read kutoka the pax header.
        tar = tarfile.open(tarname, encoding="iso8859-1")
        try:
            tarinfo = tar.getmember("pax/regtype4")
            self.assertEqual(tarinfo.size, 7011)
            self.assertEqual(tarinfo.uid, 123)
            self.assertEqual(tarinfo.gid, 123)
            self.assertEqual(tarinfo.mtime, 1041808783.0)
            self.assertEqual(type(tarinfo.mtime), float)
            self.assertEqual(float(tarinfo.pax_headers["atime"]), 1041808783.0)
            self.assertEqual(float(tarinfo.pax_headers["ctime"]), 1041808783.0)
        finally:
            tar.close()


kundi WriteTestBase(TarTest):
    # Put all write tests in here that are supposed to be tested
    # in all possible mode combinations.

    eleza test_fileobj_no_close(self):
        fobj = io.BytesIO()
        with tarfile.open(fileobj=fobj, mode=self.mode) as tar:
            tar.addfile(tarfile.TarInfo("foo"))
        self.assertFalse(fobj.closed, "external fileobjs must never closed")
        # Issue #20238: Incomplete gzip output with mode="w:gz"
        data = fobj.getvalue()
        del tar
        support.gc_collect()
        self.assertFalse(fobj.closed)
        self.assertEqual(data, fobj.getvalue())

    eleza test_eof_marker(self):
        # Make sure an end of archive marker is written (two zero blocks).
        # tarfile insists on aligning archives to a 20 * 512 byte recordsize.
        # So, we create an archive that has exactly 10240 bytes without the
        # marker, and has 20480 bytes once the marker is written.
        with tarfile.open(tmpname, self.mode) as tar:
            t = tarfile.TarInfo("foo")
            t.size = tarfile.RECORDSIZE - tarfile.BLOCKSIZE
            tar.addfile(t, io.BytesIO(b"a" * t.size))

        with self.open(tmpname, "rb") as fobj:
            self.assertEqual(len(fobj.read()), tarfile.RECORDSIZE * 2)


kundi WriteTest(WriteTestBase, unittest.TestCase):

    prefix = "w:"

    eleza test_100_char_name(self):
        # The name field in a tar header stores strings of at most 100 chars.
        # If a string is shorter than 100 chars it has to be padded with '\0',
        # which implies that a string of exactly 100 chars is stored without
        # a trailing '\0'.
        name = "0123456789" * 10
        tar = tarfile.open(tmpname, self.mode)
        try:
            t = tarfile.TarInfo(name)
            tar.addfile(t)
        finally:
            tar.close()

        tar = tarfile.open(tmpname)
        try:
            self.assertEqual(tar.getnames()[0], name,
                    "failed to store 100 char filename")
        finally:
            tar.close()

    eleza test_tar_size(self):
        # Test for bug #1013882.
        tar = tarfile.open(tmpname, self.mode)
        try:
            path = os.path.join(TEMPDIR, "file")
            with open(path, "wb") as fobj:
                fobj.write(b"aaa")
            tar.add(path)
        finally:
            tar.close()
        self.assertGreater(os.path.getsize(tmpname), 0,
                "tarfile is empty")

    # The test_*_size tests test for bug #1167128.
    eleza test_file_size(self):
        tar = tarfile.open(tmpname, self.mode)
        try:
            path = os.path.join(TEMPDIR, "file")
            with open(path, "wb"):
                pass
            tarinfo = tar.gettarinfo(path)
            self.assertEqual(tarinfo.size, 0)

            with open(path, "wb") as fobj:
                fobj.write(b"aaa")
            tarinfo = tar.gettarinfo(path)
            self.assertEqual(tarinfo.size, 3)
        finally:
            tar.close()

    eleza test_directory_size(self):
        path = os.path.join(TEMPDIR, "directory")
        os.mkdir(path)
        try:
            tar = tarfile.open(tmpname, self.mode)
            try:
                tarinfo = tar.gettarinfo(path)
                self.assertEqual(tarinfo.size, 0)
            finally:
                tar.close()
        finally:
            support.rmdir(path)

    # mock the following:
    #  os.listdir: so we know that files are in the wrong order
    eleza test_ordered_recursion(self):
        path = os.path.join(TEMPDIR, "directory")
        os.mkdir(path)
        open(os.path.join(path, "1"), "a").close()
        open(os.path.join(path, "2"), "a").close()
        try:
            tar = tarfile.open(tmpname, self.mode)
            try:
                with unittest.mock.patch('os.listdir') as mock_listdir:
                    mock_listdir.return_value = ["2", "1"]
                    tar.add(path)
                paths = []
                for m in tar.getmembers():
                    paths.append(os.path.split(m.name)[-1])
                self.assertEqual(paths, ["directory", "1", "2"]);
            finally:
                tar.close()
        finally:
            support.unlink(os.path.join(path, "1"))
            support.unlink(os.path.join(path, "2"))
            support.rmdir(path)

    eleza test_gettarinfo_pathlike_name(self):
        with tarfile.open(tmpname, self.mode) as tar:
            path = pathlib.Path(TEMPDIR) / "file"
            with open(path, "wb") as fobj:
                fobj.write(b"aaa")
            tarinfo = tar.gettarinfo(path)
            tarinfo2 = tar.gettarinfo(os.fspath(path))
            self.assertIsInstance(tarinfo.name, str)
            self.assertEqual(tarinfo.name, tarinfo2.name)
            self.assertEqual(tarinfo.size, 3)

    @unittest.skipUnless(hasattr(os, "link"),
                         "Missing hardlink implementation")
    eleza test_link_size(self):
        link = os.path.join(TEMPDIR, "link")
        target = os.path.join(TEMPDIR, "link_target")
        with open(target, "wb") as fobj:
            fobj.write(b"aaa")
        try:
            os.link(target, link)
        except PermissionError as e:
            self.skipTest('os.link(): %s' % e)
        try:
            tar = tarfile.open(tmpname, self.mode)
            try:
                # Record the link target in the inodes list.
                tar.gettarinfo(target)
                tarinfo = tar.gettarinfo(link)
                self.assertEqual(tarinfo.size, 0)
            finally:
                tar.close()
        finally:
            support.unlink(target)
            support.unlink(link)

    @support.skip_unless_symlink
    eleza test_symlink_size(self):
        path = os.path.join(TEMPDIR, "symlink")
        os.symlink("link_target", path)
        try:
            tar = tarfile.open(tmpname, self.mode)
            try:
                tarinfo = tar.gettarinfo(path)
                self.assertEqual(tarinfo.size, 0)
            finally:
                tar.close()
        finally:
            support.unlink(path)

    eleza test_add_self(self):
        # Test for #1257255.
        dstname = os.path.abspath(tmpname)
        tar = tarfile.open(tmpname, self.mode)
        try:
            self.assertEqual(tar.name, dstname,
                    "archive name must be absolute")
            tar.add(dstname)
            self.assertEqual(tar.getnames(), [],
                    "added the archive to itself")

            with support.change_cwd(TEMPDIR):
                tar.add(dstname)
            self.assertEqual(tar.getnames(), [],
                    "added the archive to itself")
        finally:
            tar.close()

    eleza test_filter(self):
        tempdir = os.path.join(TEMPDIR, "filter")
        os.mkdir(tempdir)
        try:
            for name in ("foo", "bar", "baz"):
                name = os.path.join(tempdir, name)
                support.create_empty_file(name)

            eleza filter(tarinfo):
                ikiwa os.path.basename(tarinfo.name) == "bar":
                    return
                tarinfo.uid = 123
                tarinfo.uname = "foo"
                rudisha tarinfo

            tar = tarfile.open(tmpname, self.mode, encoding="iso8859-1")
            try:
                tar.add(tempdir, arcname="empty_dir", filter=filter)
            finally:
                tar.close()

            # Verify that filter is a keyword-only argument
            with self.assertRaises(TypeError):
                tar.add(tempdir, "empty_dir", True, None, filter)

            tar = tarfile.open(tmpname, "r")
            try:
                for tarinfo in tar:
                    self.assertEqual(tarinfo.uid, 123)
                    self.assertEqual(tarinfo.uname, "foo")
                self.assertEqual(len(tar.getmembers()), 3)
            finally:
                tar.close()
        finally:
            support.rmtree(tempdir)

    # Guarantee that stored pathnames are not modified. Don't
    # remove ./ or ../ or double slashes. Still make absolute
    # pathnames relative.
    # For details see bug #6054.
    eleza _test_pathname(self, path, cmp_path=None, dir=False):
        # Create a tarfile with an empty member named path
        # and compare the stored name with the original.
        foo = os.path.join(TEMPDIR, "foo")
        ikiwa not dir:
            support.create_empty_file(foo)
        else:
            os.mkdir(foo)

        tar = tarfile.open(tmpname, self.mode)
        try:
            tar.add(foo, arcname=path)
        finally:
            tar.close()

        tar = tarfile.open(tmpname, "r")
        try:
            t = tar.next()
        finally:
            tar.close()

        ikiwa not dir:
            support.unlink(foo)
        else:
            support.rmdir(foo)

        self.assertEqual(t.name, cmp_path or path.replace(os.sep, "/"))


    @support.skip_unless_symlink
    eleza test_extractall_symlinks(self):
        # Test ikiwa extractall works properly when tarfile contains symlinks
        tempdir = os.path.join(TEMPDIR, "testsymlinks")
        temparchive = os.path.join(TEMPDIR, "testsymlinks.tar")
        os.mkdir(tempdir)
        try:
            source_file = os.path.join(tempdir,'source')
            target_file = os.path.join(tempdir,'symlink')
            with open(source_file,'w') as f:
                f.write('something\n')
            os.symlink(source_file, target_file)
            with tarfile.open(temparchive, 'w') as tar:
                tar.add(source_file)
                tar.add(target_file)
            # Let's extract it to the location which contains the symlink
            with tarfile.open(temparchive) as tar:
                # this should not raise OSError: [Errno 17] File exists
                try:
                    tar.extractall(path=tempdir)
                except OSError:
                    self.fail("extractall failed with symlinked files")
        finally:
            support.unlink(temparchive)
            support.rmtree(tempdir)

    eleza test_pathnames(self):
        self._test_pathname("foo")
        self._test_pathname(os.path.join("foo", ".", "bar"))
        self._test_pathname(os.path.join("foo", "..", "bar"))
        self._test_pathname(os.path.join(".", "foo"))
        self._test_pathname(os.path.join(".", "foo", "."))
        self._test_pathname(os.path.join(".", "foo", ".", "bar"))
        self._test_pathname(os.path.join(".", "foo", "..", "bar"))
        self._test_pathname(os.path.join(".", "foo", "..", "bar"))
        self._test_pathname(os.path.join("..", "foo"))
        self._test_pathname(os.path.join("..", "foo", ".."))
        self._test_pathname(os.path.join("..", "foo", ".", "bar"))
        self._test_pathname(os.path.join("..", "foo", "..", "bar"))

        self._test_pathname("foo" + os.sep + os.sep + "bar")
        self._test_pathname("foo" + os.sep + os.sep, "foo", dir=True)

    eleza test_abs_pathnames(self):
        ikiwa sys.platform == "win32":
            self._test_pathname("C:\\foo", "foo")
        else:
            self._test_pathname("/foo", "foo")
            self._test_pathname("///foo", "foo")

    eleza test_cwd(self):
        # Test adding the current working directory.
        with support.change_cwd(TEMPDIR):
            tar = tarfile.open(tmpname, self.mode)
            try:
                tar.add(".")
            finally:
                tar.close()

            tar = tarfile.open(tmpname, "r")
            try:
                for t in tar:
                    ikiwa t.name != ".":
                        self.assertTrue(t.name.startswith("./"), t.name)
            finally:
                tar.close()

    eleza test_open_nonwritable_fileobj(self):
        for exctype in OSError, EOFError, RuntimeError:
            kundi BadFile(io.BytesIO):
                first = True
                eleza write(self, data):
                    ikiwa self.first:
                        self.first = False
                        raise exctype

            f = BadFile()
            with self.assertRaises(exctype):
                tar = tarfile.open(tmpname, self.mode, fileobj=f,
                                   format=tarfile.PAX_FORMAT,
                                   pax_headers={'non': 'empty'})
            self.assertFalse(f.closed)

kundi GzipWriteTest(GzipTest, WriteTest):
    pass

kundi Bz2WriteTest(Bz2Test, WriteTest):
    pass

kundi LzmaWriteTest(LzmaTest, WriteTest):
    pass


kundi StreamWriteTest(WriteTestBase, unittest.TestCase):

    prefix = "w|"
    decompressor = None

    eleza test_stream_padding(self):
        # Test for bug #1543303.
        tar = tarfile.open(tmpname, self.mode)
        tar.close()
        ikiwa self.decompressor:
            dec = self.decompressor()
            with open(tmpname, "rb") as fobj:
                data = fobj.read()
            data = dec.decompress(data)
            self.assertFalse(dec.unused_data, "found trailing data")
        else:
            with self.open(tmpname) as fobj:
                data = fobj.read()
        self.assertEqual(data.count(b"\0"), tarfile.RECORDSIZE,
                        "incorrect zero padding")

    @unittest.skipUnless(sys.platform != "win32" and hasattr(os, "umask"),
                         "Missing umask implementation")
    eleza test_file_mode(self):
        # Test for issue #8464: Create files with correct
        # permissions.
        ikiwa os.path.exists(tmpname):
            support.unlink(tmpname)

        original_umask = os.umask(0o022)
        try:
            tar = tarfile.open(tmpname, self.mode)
            tar.close()
            mode = os.stat(tmpname).st_mode & 0o777
            self.assertEqual(mode, 0o644, "wrong file permissions")
        finally:
            os.umask(original_umask)

kundi GzipStreamWriteTest(GzipTest, StreamWriteTest):
    pass

kundi Bz2StreamWriteTest(Bz2Test, StreamWriteTest):
    decompressor = bz2.BZ2Decompressor ikiwa bz2 else None

kundi LzmaStreamWriteTest(LzmaTest, StreamWriteTest):
    decompressor = lzma.LZMADecompressor ikiwa lzma else None


kundi GNUWriteTest(unittest.TestCase):
    # This testcase checks for correct creation of GNU Longname
    # and Longlink extended headers (cp. bug #812325).

    eleza _length(self, s):
        blocks = len(s) // 512 + 1
        rudisha blocks * 512

    eleza _calc_size(self, name, link=None):
        # Initial tar header
        count = 512

        ikiwa len(name) > tarfile.LENGTH_NAME:
            # GNU longname extended header + longname
            count += 512
            count += self._length(name)
        ikiwa link is not None and len(link) > tarfile.LENGTH_LINK:
            # GNU longlink extended header + longlink
            count += 512
            count += self._length(link)
        rudisha count

    eleza _test(self, name, link=None):
        tarinfo = tarfile.TarInfo(name)
        ikiwa link:
            tarinfo.linkname = link
            tarinfo.type = tarfile.LNKTYPE

        tar = tarfile.open(tmpname, "w")
        try:
            tar.format = tarfile.GNU_FORMAT
            tar.addfile(tarinfo)

            v1 = self._calc_size(name, link)
            v2 = tar.offset
            self.assertEqual(v1, v2, "GNU longname/longlink creation failed")
        finally:
            tar.close()

        tar = tarfile.open(tmpname)
        try:
            member = tar.next()
            self.assertIsNotNone(member,
                    "unable to read longname member")
            self.assertEqual(tarinfo.name, member.name,
                    "unable to read longname member")
            self.assertEqual(tarinfo.linkname, member.linkname,
                    "unable to read longname member")
        finally:
            tar.close()

    eleza test_longname_1023(self):
        self._test(("longnam/" * 127) + "longnam")

    eleza test_longname_1024(self):
        self._test(("longnam/" * 127) + "longname")

    eleza test_longname_1025(self):
        self._test(("longnam/" * 127) + "longname_")

    eleza test_longlink_1023(self):
        self._test("name", ("longlnk/" * 127) + "longlnk")

    eleza test_longlink_1024(self):
        self._test("name", ("longlnk/" * 127) + "longlink")

    eleza test_longlink_1025(self):
        self._test("name", ("longlnk/" * 127) + "longlink_")

    eleza test_longnamelink_1023(self):
        self._test(("longnam/" * 127) + "longnam",
                   ("longlnk/" * 127) + "longlnk")

    eleza test_longnamelink_1024(self):
        self._test(("longnam/" * 127) + "longname",
                   ("longlnk/" * 127) + "longlink")

    eleza test_longnamelink_1025(self):
        self._test(("longnam/" * 127) + "longname_",
                   ("longlnk/" * 127) + "longlink_")


kundi CreateTest(WriteTestBase, unittest.TestCase):

    prefix = "x:"

    file_path = os.path.join(TEMPDIR, "spameggs42")

    eleza setUp(self):
        support.unlink(tmpname)

    @classmethod
    eleza setUpClass(cls):
        with open(cls.file_path, "wb") as fobj:
            fobj.write(b"aaa")

    @classmethod
    eleza tearDownClass(cls):
        support.unlink(cls.file_path)

    eleza test_create(self):
        with tarfile.open(tmpname, self.mode) as tobj:
            tobj.add(self.file_path)

        with self.taropen(tmpname) as tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    eleza test_create_existing(self):
        with tarfile.open(tmpname, self.mode) as tobj:
            tobj.add(self.file_path)

        with self.assertRaises(FileExistsError):
            tobj = tarfile.open(tmpname, self.mode)

        with self.taropen(tmpname) as tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    eleza test_create_taropen(self):
        with self.taropen(tmpname, "x") as tobj:
            tobj.add(self.file_path)

        with self.taropen(tmpname) as tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    eleza test_create_existing_taropen(self):
        with self.taropen(tmpname, "x") as tobj:
            tobj.add(self.file_path)

        with self.assertRaises(FileExistsError):
            with self.taropen(tmpname, "x"):
                pass

        with self.taropen(tmpname) as tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn("spameggs42", names[0])

    eleza test_create_pathlike_name(self):
        with tarfile.open(pathlib.Path(tmpname), self.mode) as tobj:
            self.assertIsInstance(tobj.name, str)
            self.assertEqual(tobj.name, os.path.abspath(tmpname))
            tobj.add(pathlib.Path(self.file_path))
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

        with self.taropen(tmpname) as tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    eleza test_create_taropen_pathlike_name(self):
        with self.taropen(pathlib.Path(tmpname), "x") as tobj:
            self.assertIsInstance(tobj.name, str)
            self.assertEqual(tobj.name, os.path.abspath(tmpname))
            tobj.add(pathlib.Path(self.file_path))
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

        with self.taropen(tmpname) as tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])


kundi GzipCreateTest(GzipTest, CreateTest):
    pass


kundi Bz2CreateTest(Bz2Test, CreateTest):
    pass


kundi LzmaCreateTest(LzmaTest, CreateTest):
    pass


kundi CreateWithXModeTest(CreateTest):

    prefix = "x"

    test_create_taropen = None
    test_create_existing_taropen = None


@unittest.skipUnless(hasattr(os, "link"), "Missing hardlink implementation")
kundi HardlinkTest(unittest.TestCase):
    # Test the creation of LNKTYPE (hardlink) members in an archive.

    eleza setUp(self):
        self.foo = os.path.join(TEMPDIR, "foo")
        self.bar = os.path.join(TEMPDIR, "bar")

        with open(self.foo, "wb") as fobj:
            fobj.write(b"foo")

        try:
            os.link(self.foo, self.bar)
        except PermissionError as e:
            self.skipTest('os.link(): %s' % e)

        self.tar = tarfile.open(tmpname, "w")
        self.tar.add(self.foo)

    eleza tearDown(self):
        self.tar.close()
        support.unlink(self.foo)
        support.unlink(self.bar)

    eleza test_add_twice(self):
        # The same name will be added as a REGTYPE every
        # time regardless of st_nlink.
        tarinfo = self.tar.gettarinfo(self.foo)
        self.assertEqual(tarinfo.type, tarfile.REGTYPE,
                "add file as regular failed")

    eleza test_add_hardlink(self):
        tarinfo = self.tar.gettarinfo(self.bar)
        self.assertEqual(tarinfo.type, tarfile.LNKTYPE,
                "add file as hardlink failed")

    eleza test_dereference_hardlink(self):
        self.tar.dereference = True
        tarinfo = self.tar.gettarinfo(self.bar)
        self.assertEqual(tarinfo.type, tarfile.REGTYPE,
                "dereferencing hardlink failed")


kundi PaxWriteTest(GNUWriteTest):

    eleza _test(self, name, link=None):
        # See GNUWriteTest.
        tarinfo = tarfile.TarInfo(name)
        ikiwa link:
            tarinfo.linkname = link
            tarinfo.type = tarfile.LNKTYPE

        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT)
        try:
            tar.addfile(tarinfo)
        finally:
            tar.close()

        tar = tarfile.open(tmpname)
        try:
            ikiwa link:
                l = tar.getmembers()[0].linkname
                self.assertEqual(link, l, "PAX longlink creation failed")
            else:
                n = tar.getmembers()[0].name
                self.assertEqual(name, n, "PAX longname creation failed")
        finally:
            tar.close()

    eleza test_pax_global_header(self):
        pax_headers = {
                "foo": "bar",
                "uid": "0",
                "mtime": "1.23",
                "test": "\xe4\xf6\xfc",
                "\xe4\xf6\xfc": "test"}

        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT,
                pax_headers=pax_headers)
        try:
            tar.addfile(tarfile.TarInfo("test"))
        finally:
            tar.close()

        # Test ikiwa the global header was written correctly.
        tar = tarfile.open(tmpname, encoding="iso8859-1")
        try:
            self.assertEqual(tar.pax_headers, pax_headers)
            self.assertEqual(tar.getmembers()[0].pax_headers, pax_headers)
            # Test ikiwa all the fields are strings.
            for key, val in tar.pax_headers.items():
                self.assertIsNot(type(key), bytes)
                self.assertIsNot(type(val), bytes)
                ikiwa key in tarfile.PAX_NUMBER_FIELDS:
                    try:
                        tarfile.PAX_NUMBER_FIELDS[key](val)
                    except (TypeError, ValueError):
                        self.fail("unable to convert pax header field")
        finally:
            tar.close()

    eleza test_pax_extended_header(self):
        # The fields kutoka the pax header have priority over the
        # TarInfo.
        pax_headers = {"path": "foo", "uid": "123"}

        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT,
                           encoding="iso8859-1")
        try:
            t = tarfile.TarInfo()
            t.name = "\xe4\xf6\xfc" # non-ASCII
            t.uid = 8**8 # too large
            t.pax_headers = pax_headers
            tar.addfile(t)
        finally:
            tar.close()

        tar = tarfile.open(tmpname, encoding="iso8859-1")
        try:
            t = tar.getmembers()[0]
            self.assertEqual(t.pax_headers, pax_headers)
            self.assertEqual(t.name, "foo")
            self.assertEqual(t.uid, 123)
        finally:
            tar.close()


kundi UnicodeTest:

    eleza test_iso8859_1_filename(self):
        self._test_unicode_filename("iso8859-1")

    eleza test_utf7_filename(self):
        self._test_unicode_filename("utf7")

    eleza test_utf8_filename(self):
        self._test_unicode_filename("utf-8")

    eleza _test_unicode_filename(self, encoding):
        tar = tarfile.open(tmpname, "w", format=self.format,
                           encoding=encoding, errors="strict")
        try:
            name = "\xe4\xf6\xfc"
            tar.addfile(tarfile.TarInfo(name))
        finally:
            tar.close()

        tar = tarfile.open(tmpname, encoding=encoding)
        try:
            self.assertEqual(tar.getmembers()[0].name, name)
        finally:
            tar.close()

    eleza test_unicode_filename_error(self):
        tar = tarfile.open(tmpname, "w", format=self.format,
                           encoding="ascii", errors="strict")
        try:
            tarinfo = tarfile.TarInfo()

            tarinfo.name = "\xe4\xf6\xfc"
            self.assertRaises(UnicodeError, tar.addfile, tarinfo)

            tarinfo.name = "foo"
            tarinfo.uname = "\xe4\xf6\xfc"
            self.assertRaises(UnicodeError, tar.addfile, tarinfo)
        finally:
            tar.close()

    eleza test_unicode_argument(self):
        tar = tarfile.open(tarname, "r",
                           encoding="iso8859-1", errors="strict")
        try:
            for t in tar:
                self.assertIs(type(t.name), str)
                self.assertIs(type(t.linkname), str)
                self.assertIs(type(t.uname), str)
                self.assertIs(type(t.gname), str)
        finally:
            tar.close()

    eleza test_uname_unicode(self):
        t = tarfile.TarInfo("foo")
        t.uname = "\xe4\xf6\xfc"
        t.gname = "\xe4\xf6\xfc"

        tar = tarfile.open(tmpname, mode="w", format=self.format,
                           encoding="iso8859-1")
        try:
            tar.addfile(t)
        finally:
            tar.close()

        tar = tarfile.open(tmpname, encoding="iso8859-1")
        try:
            t = tar.getmember("foo")
            self.assertEqual(t.uname, "\xe4\xf6\xfc")
            self.assertEqual(t.gname, "\xe4\xf6\xfc")

            ikiwa self.format != tarfile.PAX_FORMAT:
                tar.close()
                tar = tarfile.open(tmpname, encoding="ascii")
                t = tar.getmember("foo")
                self.assertEqual(t.uname, "\udce4\udcf6\udcfc")
                self.assertEqual(t.gname, "\udce4\udcf6\udcfc")
        finally:
            tar.close()


kundi UstarUnicodeTest(UnicodeTest, unittest.TestCase):

    format = tarfile.USTAR_FORMAT

    # Test whether the utf-8 encoded version of a filename exceeds the 100
    # bytes name field limit (every occurrence of '\xff' will be expanded to 2
    # bytes).
    eleza test_unicode_name1(self):
        self._test_ustar_name("0123456789" * 10)
        self._test_ustar_name("0123456789" * 10 + "0", ValueError)
        self._test_ustar_name("0123456789" * 9 + "01234567\xff")
        self._test_ustar_name("0123456789" * 9 + "012345678\xff", ValueError)

    eleza test_unicode_name2(self):
        self._test_ustar_name("0123456789" * 9 + "012345\xff\xff")
        self._test_ustar_name("0123456789" * 9 + "0123456\xff\xff", ValueError)

    # Test whether the utf-8 encoded version of a filename exceeds the 155
    # bytes prefix + '/' + 100 bytes name limit.
    eleza test_unicode_longname1(self):
        self._test_ustar_name("0123456789" * 15 + "01234/" + "0123456789" * 10)
        self._test_ustar_name("0123456789" * 15 + "0123/4" + "0123456789" * 10, ValueError)
        self._test_ustar_name("0123456789" * 15 + "012\xff/" + "0123456789" * 10)
        self._test_ustar_name("0123456789" * 15 + "0123\xff/" + "0123456789" * 10, ValueError)

    eleza test_unicode_longname2(self):
        self._test_ustar_name("0123456789" * 15 + "01\xff/2" + "0123456789" * 10, ValueError)
        self._test_ustar_name("0123456789" * 15 + "01\xff\xff/" + "0123456789" * 10, ValueError)

    eleza test_unicode_longname3(self):
        self._test_ustar_name("0123456789" * 15 + "01\xff\xff/2" + "0123456789" * 10, ValueError)
        self._test_ustar_name("0123456789" * 15 + "01234/" + "0123456789" * 9 + "01234567\xff")
        self._test_ustar_name("0123456789" * 15 + "01234/" + "0123456789" * 9 + "012345678\xff", ValueError)

    eleza test_unicode_longname4(self):
        self._test_ustar_name("0123456789" * 15 + "01234/" + "0123456789" * 9 + "012345\xff\xff")
        self._test_ustar_name("0123456789" * 15 + "01234/" + "0123456789" * 9 + "0123456\xff\xff", ValueError)

    eleza _test_ustar_name(self, name, exc=None):
        with tarfile.open(tmpname, "w", format=self.format, encoding="utf-8") as tar:
            t = tarfile.TarInfo(name)
            ikiwa exc is None:
                tar.addfile(t)
            else:
                self.assertRaises(exc, tar.addfile, t)

        ikiwa exc is None:
            with tarfile.open(tmpname, "r", encoding="utf-8") as tar:
                for t in tar:
                    self.assertEqual(name, t.name)
                    break

    # Test the same as above for the 100 bytes link field.
    eleza test_unicode_link1(self):
        self._test_ustar_link("0123456789" * 10)
        self._test_ustar_link("0123456789" * 10 + "0", ValueError)
        self._test_ustar_link("0123456789" * 9 + "01234567\xff")
        self._test_ustar_link("0123456789" * 9 + "012345678\xff", ValueError)

    eleza test_unicode_link2(self):
        self._test_ustar_link("0123456789" * 9 + "012345\xff\xff")
        self._test_ustar_link("0123456789" * 9 + "0123456\xff\xff", ValueError)

    eleza _test_ustar_link(self, name, exc=None):
        with tarfile.open(tmpname, "w", format=self.format, encoding="utf-8") as tar:
            t = tarfile.TarInfo("foo")
            t.linkname = name
            ikiwa exc is None:
                tar.addfile(t)
            else:
                self.assertRaises(exc, tar.addfile, t)

        ikiwa exc is None:
            with tarfile.open(tmpname, "r", encoding="utf-8") as tar:
                for t in tar:
                    self.assertEqual(name, t.linkname)
                    break


kundi GNUUnicodeTest(UnicodeTest, unittest.TestCase):

    format = tarfile.GNU_FORMAT

    eleza test_bad_pax_header(self):
        # Test for issue #8633. GNU tar <= 1.23 creates raw binary fields
        # without a hdrcharset=BINARY header.
        for encoding, name in (
                ("utf-8", "pax/bad-pax-\udce4\udcf6\udcfc"),
                ("iso8859-1", "pax/bad-pax-\xe4\xf6\xfc"),):
            with tarfile.open(tarname, encoding=encoding,
                              errors="surrogateescape") as tar:
                try:
                    t = tar.getmember(name)
                except KeyError:
                    self.fail("unable to read bad GNU tar pax header")


kundi PAXUnicodeTest(UnicodeTest, unittest.TestCase):

    format = tarfile.PAX_FORMAT

    # PAX_FORMAT ignores encoding in write mode.
    test_unicode_filename_error = None

    eleza test_binary_header(self):
        # Test a POSIX.1-2008 compatible header with a hdrcharset=BINARY field.
        for encoding, name in (
                ("utf-8", "pax/hdrcharset-\udce4\udcf6\udcfc"),
                ("iso8859-1", "pax/hdrcharset-\xe4\xf6\xfc"),):
            with tarfile.open(tarname, encoding=encoding,
                              errors="surrogateescape") as tar:
                try:
                    t = tar.getmember(name)
                except KeyError:
                    self.fail("unable to read POSIX.1-2008 binary header")


kundi AppendTestBase:
    # Test append mode (cp. patch #1652681).

    eleza setUp(self):
        self.tarname = tmpname
        ikiwa os.path.exists(self.tarname):
            support.unlink(self.tarname)

    eleza _create_testtar(self, mode="w:"):
        with tarfile.open(tarname, encoding="iso8859-1") as src:
            t = src.getmember("ustar/regtype")
            t.name = "foo"
            with src.extractfile(t) as f:
                with tarfile.open(self.tarname, mode) as tar:
                    tar.addfile(t, f)

    eleza test_append_compressed(self):
        self._create_testtar("w:" + self.suffix)
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname, "a")

kundi AppendTest(AppendTestBase, unittest.TestCase):
    test_append_compressed = None

    eleza _add_testfile(self, fileobj=None):
        with tarfile.open(self.tarname, "a", fileobj=fileobj) as tar:
            tar.addfile(tarfile.TarInfo("bar"))

    eleza _test(self, names=["bar"], fileobj=None):
        with tarfile.open(self.tarname, fileobj=fileobj) as tar:
            self.assertEqual(tar.getnames(), names)

    eleza test_non_existing(self):
        self._add_testfile()
        self._test()

    eleza test_empty(self):
        tarfile.open(self.tarname, "w:").close()
        self._add_testfile()
        self._test()

    eleza test_empty_fileobj(self):
        fobj = io.BytesIO(b"\0" * 1024)
        self._add_testfile(fobj)
        fobj.seek(0)
        self._test(fileobj=fobj)

    eleza test_fileobj(self):
        self._create_testtar()
        with open(self.tarname, "rb") as fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        self._add_testfile(fobj)
        fobj.seek(0)
        self._test(names=["foo", "bar"], fileobj=fobj)

    eleza test_existing(self):
        self._create_testtar()
        self._add_testfile()
        self._test(names=["foo", "bar"])

    # Append mode is supposed to fail ikiwa the tarfile to append to
    # does not end with a zero block.
    eleza _test_error(self, data):
        with open(self.tarname, "wb") as fobj:
            fobj.write(data)
        self.assertRaises(tarfile.ReadError, self._add_testfile)

    eleza test_null(self):
        self._test_error(b"")

    eleza test_incomplete(self):
        self._test_error(b"\0" * 13)

    eleza test_premature_eof(self):
        data = tarfile.TarInfo("foo").tobuf()
        self._test_error(data)

    eleza test_trailing_garbage(self):
        data = tarfile.TarInfo("foo").tobuf()
        self._test_error(data + b"\0" * 13)

    eleza test_invalid(self):
        self._test_error(b"a" * 512)

kundi GzipAppendTest(GzipTest, AppendTestBase, unittest.TestCase):
    pass

kundi Bz2AppendTest(Bz2Test, AppendTestBase, unittest.TestCase):
    pass

kundi LzmaAppendTest(LzmaTest, AppendTestBase, unittest.TestCase):
    pass


kundi LimitsTest(unittest.TestCase):

    eleza test_ustar_limits(self):
        # 100 char name
        tarinfo = tarfile.TarInfo("0123456789" * 10)
        tarinfo.tobuf(tarfile.USTAR_FORMAT)

        # 101 char name that cannot be stored
        tarinfo = tarfile.TarInfo("0123456789" * 10 + "0")
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # 256 char name with a slash at pos 156
        tarinfo = tarfile.TarInfo("123/" * 62 + "longname")
        tarinfo.tobuf(tarfile.USTAR_FORMAT)

        # 256 char name that cannot be stored
        tarinfo = tarfile.TarInfo("1234567/" * 31 + "longname")
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # 512 char name
        tarinfo = tarfile.TarInfo("123/" * 126 + "longname")
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # 512 char linkname
        tarinfo = tarfile.TarInfo("longlink")
        tarinfo.linkname = "123/" * 126 + "longname"
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # uid > 8 digits
        tarinfo = tarfile.TarInfo("name")
        tarinfo.uid = 0o10000000
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

    eleza test_gnu_limits(self):
        tarinfo = tarfile.TarInfo("123/" * 126 + "longname")
        tarinfo.tobuf(tarfile.GNU_FORMAT)

        tarinfo = tarfile.TarInfo("longlink")
        tarinfo.linkname = "123/" * 126 + "longname"
        tarinfo.tobuf(tarfile.GNU_FORMAT)

        # uid >= 256 ** 7
        tarinfo = tarfile.TarInfo("name")
        tarinfo.uid = 0o4000000000000000000
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.GNU_FORMAT)

    eleza test_pax_limits(self):
        tarinfo = tarfile.TarInfo("123/" * 126 + "longname")
        tarinfo.tobuf(tarfile.PAX_FORMAT)

        tarinfo = tarfile.TarInfo("longlink")
        tarinfo.linkname = "123/" * 126 + "longname"
        tarinfo.tobuf(tarfile.PAX_FORMAT)

        tarinfo = tarfile.TarInfo("name")
        tarinfo.uid = 0o4000000000000000000
        tarinfo.tobuf(tarfile.PAX_FORMAT)


kundi MiscTest(unittest.TestCase):

    eleza test_char_fields(self):
        self.assertEqual(tarfile.stn("foo", 8, "ascii", "strict"),
                         b"foo\0\0\0\0\0")
        self.assertEqual(tarfile.stn("foobar", 3, "ascii", "strict"),
                         b"foo")
        self.assertEqual(tarfile.nts(b"foo\0\0\0\0\0", "ascii", "strict"),
                         "foo")
        self.assertEqual(tarfile.nts(b"foo\0bar\0", "ascii", "strict"),
                         "foo")

    eleza test_read_number_fields(self):
        # Issue 13158: Test ikiwa GNU tar specific base-256 number fields
        # are decoded correctly.
        self.assertEqual(tarfile.nti(b"0000001\x00"), 1)
        self.assertEqual(tarfile.nti(b"7777777\x00"), 0o7777777)
        self.assertEqual(tarfile.nti(b"\x80\x00\x00\x00\x00\x20\x00\x00"),
                         0o10000000)
        self.assertEqual(tarfile.nti(b"\x80\x00\x00\x00\xff\xff\xff\xff"),
                         0xffffffff)
        self.assertEqual(tarfile.nti(b"\xff\xff\xff\xff\xff\xff\xff\xff"),
                         -1)
        self.assertEqual(tarfile.nti(b"\xff\xff\xff\xff\xff\xff\xff\x9c"),
                         -100)
        self.assertEqual(tarfile.nti(b"\xff\x00\x00\x00\x00\x00\x00\x00"),
                         -0x100000000000000)

        # Issue 24514: Test ikiwa empty number fields are converted to zero.
        self.assertEqual(tarfile.nti(b"\0"), 0)
        self.assertEqual(tarfile.nti(b"       \0"), 0)

    eleza test_write_number_fields(self):
        self.assertEqual(tarfile.itn(1), b"0000001\x00")
        self.assertEqual(tarfile.itn(0o7777777), b"7777777\x00")
        self.assertEqual(tarfile.itn(0o10000000, format=tarfile.GNU_FORMAT),
                         b"\x80\x00\x00\x00\x00\x20\x00\x00")
        self.assertEqual(tarfile.itn(0xffffffff, format=tarfile.GNU_FORMAT),
                         b"\x80\x00\x00\x00\xff\xff\xff\xff")
        self.assertEqual(tarfile.itn(-1, format=tarfile.GNU_FORMAT),
                         b"\xff\xff\xff\xff\xff\xff\xff\xff")
        self.assertEqual(tarfile.itn(-100, format=tarfile.GNU_FORMAT),
                         b"\xff\xff\xff\xff\xff\xff\xff\x9c")
        self.assertEqual(tarfile.itn(-0x100000000000000,
                                     format=tarfile.GNU_FORMAT),
                         b"\xff\x00\x00\x00\x00\x00\x00\x00")

        # Issue 32713: Test ikiwa itn() supports float values outside the
        # non-GNU format range
        self.assertEqual(tarfile.itn(-100.0, format=tarfile.GNU_FORMAT),
                         b"\xff\xff\xff\xff\xff\xff\xff\x9c")
        self.assertEqual(tarfile.itn(8 ** 12 + 0.0, format=tarfile.GNU_FORMAT),
                         b"\x80\x00\x00\x10\x00\x00\x00\x00")
        self.assertEqual(tarfile.nti(tarfile.itn(-0.1, format=tarfile.GNU_FORMAT)), 0)

    eleza test_number_field_limits(self):
        with self.assertRaises(ValueError):
            tarfile.itn(-1, 8, tarfile.USTAR_FORMAT)
        with self.assertRaises(ValueError):
            tarfile.itn(0o10000000, 8, tarfile.USTAR_FORMAT)
        with self.assertRaises(ValueError):
            tarfile.itn(-0x10000000001, 6, tarfile.GNU_FORMAT)
        with self.assertRaises(ValueError):
            tarfile.itn(0x10000000000, 6, tarfile.GNU_FORMAT)

    eleza test__all__(self):
        blacklist = {'version', 'grp', 'pwd', 'symlink_exception',
                     'NUL', 'BLOCKSIZE', 'RECORDSIZE', 'GNU_MAGIC',
                     'POSIX_MAGIC', 'LENGTH_NAME', 'LENGTH_LINK',
                     'LENGTH_PREFIX', 'REGTYPE', 'AREGTYPE', 'LNKTYPE',
                     'SYMTYPE', 'CHRTYPE', 'BLKTYPE', 'DIRTYPE', 'FIFOTYPE',
                     'CONTTYPE', 'GNUTYPE_LONGNAME', 'GNUTYPE_LONGLINK',
                     'GNUTYPE_SPARSE', 'XHDTYPE', 'XGLTYPE', 'SOLARIS_XHDTYPE',
                     'SUPPORTED_TYPES', 'REGULAR_TYPES', 'GNU_TYPES',
                     'PAX_FIELDS', 'PAX_NAME_FIELDS', 'PAX_NUMBER_FIELDS',
                     'stn', 'nts', 'nti', 'itn', 'calc_chksums', 'copyfileobj',
                     'filemode',
                     'EmptyHeaderError', 'TruncatedHeaderError',
                     'EOFHeaderError', 'InvalidHeaderError',
                     'SubsequentHeaderError', 'ExFileObject',
                     'main'}
        support.check__all__(self, tarfile, blacklist=blacklist)


kundi CommandLineTest(unittest.TestCase):

    eleza tarfilecmd(self, *args, **kwargs):
        rc, out, err = script_helper.assert_python_ok('-m', 'tarfile', *args,
                                                      **kwargs)
        rudisha out.replace(os.linesep.encode(), b'\n')

    eleza tarfilecmd_failure(self, *args):
        rudisha script_helper.assert_python_failure('-m', 'tarfile', *args)

    eleza make_simple_tarfile(self, tar_name):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        self.addCleanup(support.unlink, tar_name)
        with tarfile.open(tar_name, 'w') as tf:
            for tardata in files:
                tf.add(tardata, arcname=os.path.basename(tardata))

    eleza test_bad_use(self):
        rc, out, err = self.tarfilecmd_failure()
        self.assertEqual(out, b'')
        self.assertIn(b'usage', err.lower())
        self.assertIn(b'error', err.lower())
        self.assertIn(b'required', err.lower())
        rc, out, err = self.tarfilecmd_failure('-l', '')
        self.assertEqual(out, b'')
        self.assertNotEqual(err.strip(), b'')

    eleza test_test_command(self):
        for tar_name in testtarnames:
            for opt in '-t', '--test':
                out = self.tarfilecmd(opt, tar_name)
                self.assertEqual(out, b'')

    eleza test_test_command_verbose(self):
        for tar_name in testtarnames:
            for opt in '-v', '--verbose':
                out = self.tarfilecmd(opt, '-t', tar_name)
                self.assertIn(b'is a tar archive.\n', out)

    eleza test_test_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        rc, out, err = self.tarfilecmd_failure('-t', zipname)
        self.assertIn(b' is not a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)

        for tar_name in testtarnames:
            with self.subTest(tar_name=tar_name):
                with open(tar_name, 'rb') as f:
                    data = f.read()
                try:
                    with open(tmpname, 'wb') as f:
                        f.write(data[:511])
                    rc, out, err = self.tarfilecmd_failure('-t', tmpname)
                    self.assertEqual(out, b'')
                    self.assertEqual(rc, 1)
                finally:
                    support.unlink(tmpname)

    eleza test_list_command(self):
        for tar_name in testtarnames:
            with support.captured_stdout() as t:
                with tarfile.open(tar_name, 'r') as tf:
                    tf.list(verbose=False)
            expected = t.getvalue().encode('ascii', 'backslashreplace')
            for opt in '-l', '--list':
                out = self.tarfilecmd(opt, tar_name,
                                      PYTHONIOENCODING='ascii')
                self.assertEqual(out, expected)

    eleza test_list_command_verbose(self):
        for tar_name in testtarnames:
            with support.captured_stdout() as t:
                with tarfile.open(tar_name, 'r') as tf:
                    tf.list(verbose=True)
            expected = t.getvalue().encode('ascii', 'backslashreplace')
            for opt in '-v', '--verbose':
                out = self.tarfilecmd(opt, '-l', tar_name,
                                      PYTHONIOENCODING='ascii')
                self.assertEqual(out, expected)

    eleza test_list_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        rc, out, err = self.tarfilecmd_failure('-l', zipname)
        self.assertIn(b' is not a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)

    eleza test_create_command(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        for opt in '-c', '--create':
            try:
                out = self.tarfilecmd(opt, tmpname, *files)
                self.assertEqual(out, b'')
                with tarfile.open(tmpname) as tar:
                    tar.getmembers()
            finally:
                support.unlink(tmpname)

    eleza test_create_command_verbose(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        for opt in '-v', '--verbose':
            try:
                out = self.tarfilecmd(opt, '-c', tmpname, *files)
                self.assertIn(b' file created.', out)
                with tarfile.open(tmpname) as tar:
                    tar.getmembers()
            finally:
                support.unlink(tmpname)

    eleza test_create_command_dotless_filename(self):
        files = [support.findfile('tokenize_tests.txt')]
        try:
            out = self.tarfilecmd('-c', dotlessname, *files)
            self.assertEqual(out, b'')
            with tarfile.open(dotlessname) as tar:
                tar.getmembers()
        finally:
            support.unlink(dotlessname)

    eleza test_create_command_dot_started_filename(self):
        tar_name = os.path.join(TEMPDIR, ".testtar")
        files = [support.findfile('tokenize_tests.txt')]
        try:
            out = self.tarfilecmd('-c', tar_name, *files)
            self.assertEqual(out, b'')
            with tarfile.open(tar_name) as tar:
                tar.getmembers()
        finally:
            support.unlink(tar_name)

    eleza test_create_command_compressed(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        for filetype in (GzipTest, Bz2Test, LzmaTest):
            ikiwa not filetype.open:
                continue
            try:
                tar_name = tmpname + '.' + filetype.suffix
                out = self.tarfilecmd('-c', tar_name, *files)
                with filetype.taropen(tar_name) as tar:
                    tar.getmembers()
            finally:
                support.unlink(tar_name)

    eleza test_extract_command(self):
        self.make_simple_tarfile(tmpname)
        for opt in '-e', '--extract':
            try:
                with support.temp_cwd(tarextdir):
                    out = self.tarfilecmd(opt, tmpname)
                self.assertEqual(out, b'')
            finally:
                support.rmtree(tarextdir)

    eleza test_extract_command_verbose(self):
        self.make_simple_tarfile(tmpname)
        for opt in '-v', '--verbose':
            try:
                with support.temp_cwd(tarextdir):
                    out = self.tarfilecmd(opt, '-e', tmpname)
                self.assertIn(b' file is extracted.', out)
            finally:
                support.rmtree(tarextdir)

    eleza test_extract_command_different_directory(self):
        self.make_simple_tarfile(tmpname)
        try:
            with support.temp_cwd(tarextdir):
                out = self.tarfilecmd('-e', tmpname, 'spamdir')
            self.assertEqual(out, b'')
        finally:
            support.rmtree(tarextdir)

    eleza test_extract_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        with support.temp_cwd(tarextdir):
            rc, out, err = self.tarfilecmd_failure('-e', zipname)
        self.assertIn(b' is not a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)


kundi ContextManagerTest(unittest.TestCase):

    eleza test_basic(self):
        with tarfile.open(tarname) as tar:
            self.assertFalse(tar.closed, "closed inside runtime context")
        self.assertTrue(tar.closed, "context manager failed")

    eleza test_closed(self):
        # The __enter__() method is supposed to raise OSError
        # ikiwa the TarFile object is already closed.
        tar = tarfile.open(tarname)
        tar.close()
        with self.assertRaises(OSError):
            with tar:
                pass

    eleza test_exception(self):
        # Test ikiwa the OSError exception is passed through properly.
        with self.assertRaises(Exception) as exc:
            with tarfile.open(tarname) as tar:
                raise OSError
        self.assertIsInstance(exc.exception, OSError,
                              "wrong exception raised in context manager")
        self.assertTrue(tar.closed, "context manager failed")

    eleza test_no_eof(self):
        # __exit__() must not write end-of-archive blocks ikiwa an
        # exception was raised.
        try:
            with tarfile.open(tmpname, "w") as tar:
                raise Exception
        except:
            pass
        self.assertEqual(os.path.getsize(tmpname), 0,
                "context manager wrote an end-of-archive block")
        self.assertTrue(tar.closed, "context manager failed")

    eleza test_eof(self):
        # __exit__() must write end-of-archive blocks, i.e. call
        # TarFile.close() ikiwa there was no error.
        with tarfile.open(tmpname, "w"):
            pass
        self.assertNotEqual(os.path.getsize(tmpname), 0,
                "context manager wrote no end-of-archive block")

    eleza test_fileobj(self):
        # Test that __exit__() did not close the external file
        # object.
        with open(tmpname, "wb") as fobj:
            try:
                with tarfile.open(fileobj=fobj, mode="w") as tar:
                    raise Exception
            except:
                pass
            self.assertFalse(fobj.closed, "external file object was closed")
            self.assertTrue(tar.closed, "context manager failed")


@unittest.skipIf(hasattr(os, "link"), "requires os.link to be missing")
kundi LinkEmulationTest(ReadTest, unittest.TestCase):

    # Test for issue #8741 regression. On platforms that do not support
    # symbolic or hard links tarfile tries to extract these types of members
    # as the regular files they point to.
    eleza _test_link_extraction(self, name):
        self.tar.extract(name, TEMPDIR)
        with open(os.path.join(TEMPDIR, name), "rb") as f:
            data = f.read()
        self.assertEqual(sha256sum(data), sha256_regtype)

    # See issues #1578269, #8879, and #17689 for some history on these skips
    @unittest.skipIf(hasattr(os.path, "islink"),
                     "Skip emulation - has os.path.islink but not os.link")
    eleza test_hardlink_extraction1(self):
        self._test_link_extraction("ustar/lnktype")

    @unittest.skipIf(hasattr(os.path, "islink"),
                     "Skip emulation - has os.path.islink but not os.link")
    eleza test_hardlink_extraction2(self):
        self._test_link_extraction("./ustar/linktest2/lnktype")

    @unittest.skipIf(hasattr(os, "symlink"),
                     "Skip emulation ikiwa symlink exists")
    eleza test_symlink_extraction1(self):
        self._test_link_extraction("ustar/symtype")

    @unittest.skipIf(hasattr(os, "symlink"),
                     "Skip emulation ikiwa symlink exists")
    eleza test_symlink_extraction2(self):
        self._test_link_extraction("./ustar/linktest2/symtype")


kundi Bz2PartialReadTest(Bz2Test, unittest.TestCase):
    # Issue5068: The _BZ2Proxy.read() method loops forever
    # on an empty or partial bzipped file.

    eleza _test_partial_input(self, mode):
        kundi MyBytesIO(io.BytesIO):
            hit_eof = False
            eleza read(self, n):
                ikiwa self.hit_eof:
                    raise AssertionError("infinite loop detected in "
                                         "tarfile.open()")
                self.hit_eof = self.tell() == len(self.getvalue())
                rudisha super(MyBytesIO, self).read(n)
            eleza seek(self, *args):
                self.hit_eof = False
                rudisha super(MyBytesIO, self).seek(*args)

        data = bz2.compress(tarfile.TarInfo("foo").tobuf())
        for x in range(len(data) + 1):
            try:
                tarfile.open(fileobj=MyBytesIO(data[:x]), mode=mode)
            except tarfile.ReadError:
                pass # we have no interest in ReadErrors

    eleza test_partial_input(self):
        self._test_partial_input("r")

    eleza test_partial_input_bz2(self):
        self._test_partial_input("r:bz2")


eleza root_is_uid_gid_0():
    try:
        agiza pwd, grp
    except ImportError:
        rudisha False
    ikiwa pwd.getpwuid(0)[0] != 'root':
        rudisha False
    ikiwa grp.getgrgid(0)[0] != 'root':
        rudisha False
    rudisha True


@unittest.skipUnless(hasattr(os, 'chown'), "missing os.chown")
@unittest.skipUnless(hasattr(os, 'geteuid'), "missing os.geteuid")
kundi NumericOwnerTest(unittest.TestCase):
    # mock the following:
    #  os.chown: so we can test what's being called
    #  os.chmod: so the modes are not actually changed. ikiwa they are, we can't
    #             delete the files/directories
    #  os.geteuid: so we can lie and say we're root (uid = 0)

    @staticmethod
    eleza _make_test_archive(filename_1, dirname_1, filename_2):
        # the file contents to write
        fobj = io.BytesIO(b"content")

        # create a tar file with a file, a directory, and a file within that
        #  directory. Assign various .uid/.gid values to them
        items = [(filename_1, 99, 98, tarfile.REGTYPE, fobj),
                 (dirname_1,  77, 76, tarfile.DIRTYPE, None),
                 (filename_2, 88, 87, tarfile.REGTYPE, fobj),
                 ]
        with tarfile.open(tmpname, 'w') as tarfl:
            for name, uid, gid, typ, contents in items:
                t = tarfile.TarInfo(name)
                t.uid = uid
                t.gid = gid
                t.uname = 'root'
                t.gname = 'root'
                t.type = typ
                tarfl.addfile(t, contents)

        # rudisha the full pathname to the tar file
        rudisha tmpname

    @staticmethod
    @contextmanager
    eleza _setup_test(mock_geteuid):
        mock_geteuid.return_value = 0  # lie and say we're root
        fname = 'numeric-owner-testfile'
        dirname = 'dir'

        # the names we want stored in the tarfile
        filename_1 = fname
        dirname_1 = dirname
        filename_2 = os.path.join(dirname, fname)

        # create the tarfile with the contents we're after
        tar_filename = NumericOwnerTest._make_test_archive(filename_1,
                                                           dirname_1,
                                                           filename_2)

        # open the tarfile for reading. yield it and the names of the items
        #  we stored into the file
        with tarfile.open(tar_filename) as tarfl:
            yield tarfl, filename_1, dirname_1, filename_2

    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    eleza test_extract_with_numeric_owner(self, mock_geteuid, mock_chmod,
                                        mock_chown):
        with self._setup_test(mock_geteuid) as (tarfl, filename_1, _,
                                                filename_2):
            tarfl.extract(filename_1, TEMPDIR, numeric_owner=True)
            tarfl.extract(filename_2 , TEMPDIR, numeric_owner=True)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)
        f_filename_2 = os.path.join(TEMPDIR, filename_2)

        mock_chown.assert_has_calls([unittest.mock.call(f_filename_1, 99, 98),
                                     unittest.mock.call(f_filename_2, 88, 87),
                                     ],
                                    any_order=True)

    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    eleza test_extractall_with_numeric_owner(self, mock_geteuid, mock_chmod,
                                           mock_chown):
        with self._setup_test(mock_geteuid) as (tarfl, filename_1, dirname_1,
                                                filename_2):
            tarfl.extractall(TEMPDIR, numeric_owner=True)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)
        f_dirname_1  = os.path.join(TEMPDIR, dirname_1)
        f_filename_2 = os.path.join(TEMPDIR, filename_2)

        mock_chown.assert_has_calls([unittest.mock.call(f_filename_1, 99, 98),
                                     unittest.mock.call(f_dirname_1, 77, 76),
                                     unittest.mock.call(f_filename_2, 88, 87),
                                     ],
                                    any_order=True)

    # this test requires that uid=0 and gid=0 really be named 'root'. that's
    #  because the uname and gname in the test file are 'root', and extract()
    #  will look them up using pwd and grp to find their uid and gid, which we
    #  test here to be 0.
    @unittest.skipUnless(root_is_uid_gid_0(),
                         'uid=0,gid=0 must be named "root"')
    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    eleza test_extract_without_numeric_owner(self, mock_geteuid, mock_chmod,
                                           mock_chown):
        with self._setup_test(mock_geteuid) as (tarfl, filename_1, _, _):
            tarfl.extract(filename_1, TEMPDIR, numeric_owner=False)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)

        mock_chown.assert_called_with(f_filename_1, 0, 0)

    @unittest.mock.patch('os.geteuid')
    eleza test_keyword_only(self, mock_geteuid):
        with self._setup_test(mock_geteuid) as (tarfl, filename_1, _, _):
            self.assertRaises(TypeError,
                              tarfl.extract, filename_1, TEMPDIR, False, True)


eleza setUpModule():
    support.unlink(TEMPDIR)
    os.makedirs(TEMPDIR)

    global testtarnames
    testtarnames = [tarname]
    with open(tarname, "rb") as fobj:
        data = fobj.read()

    # Create compressed tarfiles.
    for c in GzipTest, Bz2Test, LzmaTest:
        ikiwa c.open:
            support.unlink(c.tarname)
            testtarnames.append(c.tarname)
            with c.open(c.tarname, "wb") as tar:
                tar.write(data)

eleza tearDownModule():
    ikiwa os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)

ikiwa __name__ == "__main__":
    unittest.main()
