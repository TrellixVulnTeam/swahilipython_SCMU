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

# Check kila our compression modules.
jaribu:
    agiza gzip
tatizo ImportError:
    gzip = Tupu
jaribu:
    agiza bz2
tatizo ImportError:
    bz2 = Tupu
jaribu:
    agiza lzma
tatizo ImportError:
    lzma = Tupu

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
    open = gzip.GzipFile ikiwa gzip isipokua Tupu
    taropen = tarfile.TarFile.gzopen

@support.requires_bz2
kundi Bz2Test:
    tarname = bz2name
    suffix = 'bz2'
    open = bz2.BZ2File ikiwa bz2 isipokua Tupu
    taropen = tarfile.TarFile.bz2open

@support.requires_lzma
kundi LzmaTest:
    tarname = xzname
    suffix = 'xz'
    open = lzma.LZMAFile ikiwa lzma isipokua Tupu
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
        ukijumuisha self.tar.extractfile(tarinfo) kama fobj:
            data = fobj.read()
            self.assertEqual(len(data), tarinfo.size,
                    "regular file extraction failed")
            self.assertEqual(sha256sum(data), sha256_regtype,
                    "regular file extraction failed")

    eleza test_fileobj_readlines(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        tarinfo = self.tar.getmember("ustar/regtype")
        ukijumuisha open(os.path.join(TEMPDIR, "ustar/regtype"), "r") kama fobj1:
            lines1 = fobj1.readlines()

        ukijumuisha self.tar.extractfile(tarinfo) kama fobj:
            fobj2 = io.TextIOWrapper(fobj)
            lines2 = fobj2.readlines()
            self.assertEqual(lines1, lines2,
                    "fileobj.readlines() failed")
            self.assertEqual(len(lines2), 114,
                    "fileobj.readlines() failed")
            self.assertEqual(lines2[83],
                    "I will gladly admit that Python ni sio the fastest "
                    "running scripting language.\n",
                    "fileobj.readlines() failed")

    eleza test_fileobj_iter(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        tarinfo = self.tar.getmember("ustar/regtype")
        ukijumuisha open(os.path.join(TEMPDIR, "ustar/regtype"), "r") kama fobj1:
            lines1 = fobj1.readlines()
        ukijumuisha self.tar.extractfile(tarinfo) kama fobj2:
            lines2 = list(io.TextIOWrapper(fobj2))
            self.assertEqual(lines1, lines2,
                    "fileobj.__iter__() failed")

    eleza test_fileobj_seek(self):
        self.tar.extract("ustar/regtype", TEMPDIR)
        ukijumuisha open(os.path.join(TEMPDIR, "ustar/regtype"), "rb") kama fobj:
            data = fobj.read()

        tarinfo = self.tar.getmember("ustar/regtype")
        ukijumuisha self.tar.extractfile(tarinfo) kama fobj:
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
                         "read() at file's end did sio rudisha empty string")
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
                         "tell() after seek() na readline() failed")
            fobj.seek(0)
            line = fobj.readline()
            self.assertEqual(fobj.read(), data[len(line):],
                         "read() after readline() failed")

    eleza test_fileobj_text(self):
        ukijumuisha self.tar.extractfile("ustar/regtype") kama fobj:
            fobj = io.TextIOWrapper(fobj)
            data = fobj.read().encode("iso8859-1")
            self.assertEqual(sha256sum(data), sha256_regtype)
            jaribu:
                fobj.seek(100)
            tatizo AttributeError:
                # Issue #13815: seek() complained about a missing
                # flush() method.
                self.fail("seeking failed kwenye text mode")

    # Test ikiwa symbolic na hard links are resolved by extractfile().  The
    # test link members each point to a regular member whose data is
    # supposed to be exported.
    eleza _test_fileobj_link(self, lnktype, regtype):
        ukijumuisha self.tar.extractfile(lnktype) kama a, \
             self.tar.extractfile(regtype) kama b:
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
    pita

kundi Bz2UstarReadTest(Bz2Test, UstarReadTest):
    pita

kundi LzmaUstarReadTest(LzmaTest, UstarReadTest):
    pita


kundi ListTest(ReadTest, unittest.TestCase):

    # Override setUp to use default encoding (UTF-8)
    eleza setUp(self):
        self.tar = tarfile.open(self.tarname, mode=self.mode)

    eleza test_list(self):
        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
        ukijumuisha support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=Uongo)
        out = tio.detach().getvalue()
        self.assertIn(b'ustar/conttype', out)
        self.assertIn(b'ustar/regtype', out)
        self.assertIn(b'ustar/lnktype', out)
        self.assertIn(b'ustar' + (b'/12345' * 40) + b'67/longname', out)
        self.assertIn(b'./ustar/linktest2/symtype', out)
        self.assertIn(b'./ustar/linktest2/lnktype', out)
        # Make sure it puts trailing slash kila directory
        self.assertIn(b'ustar/dirtype/', out)
        self.assertIn(b'ustar/dirtype-with-size/', out)
        # Make sure it ni able to andika unencodable characters
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
        # 'ls -l'-like accessories ikiwa verbose flag ni sio being used
        # ...
        # ustar/conttype
        # ustar/regtype
        # ...
        self.assertRegex(out, br'ustar/conttype ?\r?\n'
                              br'ustar/regtype ?\r?\n')
        # Make sure it does sio andika the source of link without verbose flag
        self.assertNotIn(b'link to', out)
        self.assertNotIn(b'->', out)

    eleza test_list_verbose(self):
        tio = io.TextIOWrapper(io.BytesIO(), 'ascii', newline='\n')
        ukijumuisha support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=Kweli)
        out = tio.detach().getvalue()
        # Make sure it prints files separated by one newline ukijumuisha 'ls -l'-like
        # accessories ikiwa verbose flag ni being used
        # ...
        # ?rw-r--r-- tarfile/tarfile     7011 2003-01-06 07:19:43 ustar/conttype
        # ?rw-r--r-- tarfile/tarfile     7011 2003-01-06 07:19:43 ustar/regtype
        # ...
        self.assertRegex(out, (br'\?rw-r--r-- tarfile/tarfile\s+7011 '
                               br'\d{4}-\d\d-\d\d\s+\d\d:\d\d:\d\d '
                               br'ustar/\w+type ?\r?\n') * 2)
        # Make sure it prints the source of link ukijumuisha verbose flag
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
            kila tarinfo kwenye tar.getmembers():
                ikiwa 'reg' kwenye tarinfo.name:
                    tuma tarinfo
        ukijumuisha support.swap_attr(sys, 'stdout', tio):
            self.tar.list(verbose=Uongo, members=members(self.tar))
        out = tio.detach().getvalue()
        self.assertIn(b'ustar/regtype', out)
        self.assertNotIn(b'ustar/conttype', out)


kundi GzipListTest(GzipTest, ListTest):
    pita


kundi Bz2ListTest(Bz2Test, ListTest):
    pita


kundi LzmaListTest(LzmaTest, ListTest):
    pita


kundi CommonReadTest(ReadTest):

    eleza test_empty_tarfile(self):
        # Test kila issue6123: Allow opening empty archives.
        # This test checks ikiwa tarfile.open() ni able to open an empty tar
        # archive successfully. Note that an empty tar archive ni sio the
        # same kama an empty file!
        ukijumuisha tarfile.open(tmpname, self.mode.replace("r", "w")):
            pita
        jaribu:
            tar = tarfile.open(tmpname, self.mode)
            tar.getnames()
        tatizo tarfile.ReadError:
            self.fail("tarfile.open() failed on empty archive")
        isipokua:
            self.assertListEqual(tar.getmembers(), [])
        mwishowe:
            tar.close()

    eleza test_non_existent_tarfile(self):
        # Test kila issue11513: prevent non-existent gzipped tarfiles raising
        # multiple exceptions.
        ukijumuisha self.assertRaisesRegex(FileNotFoundError, "xxx"):
            tarfile.open("xxx", self.mode)

    eleza test_null_tarfile(self):
        # Test kila issue6123: Allow opening empty archives.
        # This test guarantees that tarfile.open() does sio treat an empty
        # file kama an empty tar archive.
        ukijumuisha open(tmpname, "wb"):
            pita
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname, self.mode)
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname)

    eleza test_ignore_zeros(self):
        # Test TarFile's ignore_zeros option.
        # generate 512 pseudorandom bytes
        data = Random(0).getrandbits(512*8).to_bytes(512, 'big')
        kila char kwenye (b'\0', b'a'):
            # Test ikiwa EOFHeaderError ('\0') na InvalidHeaderError ('a')
            # are ignored correctly.
            ukijumuisha self.open(tmpname, "w") kama fobj:
                fobj.write(char * 1024)
                tarinfo = tarfile.TarInfo("foo")
                tarinfo.size = len(data)
                fobj.write(tarinfo.tobuf())
                fobj.write(data)

            tar = tarfile.open(tmpname, mode="r", ignore_zeros=Kweli)
            jaribu:
                self.assertListEqual(tar.getnames(), ["foo"],
                    "ignore_zeros=Kweli should have skipped the %r-blocks" %
                    char)
            mwishowe:
                tar.close()

    eleza test_premature_end_of_archive(self):
        kila size kwenye (512, 600, 1024, 1200):
            ukijumuisha tarfile.open(tmpname, "w:") kama tar:
                t = tarfile.TarInfo("foo")
                t.size = 1024
                tar.addfile(t, io.BytesIO(b"a" * 1024))

            ukijumuisha open(tmpname, "r+b") kama fobj:
                fobj.truncate(size)

            ukijumuisha tarfile.open(tmpname) kama tar:
                ukijumuisha self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    kila t kwenye tar:
                        pita

            ukijumuisha tarfile.open(tmpname) kama tar:
                t = tar.next()

                ukijumuisha self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    tar.extract(t, TEMPDIR)

                ukijumuisha self.assertRaisesRegex(tarfile.ReadError, "unexpected end of data"):
                    tar.extractfile(t).read()

kundi MiscReadTestBase(CommonReadTest):
    eleza requires_name_attribute(self):
        pita

    eleza test_no_name_argument(self):
        self.requires_name_attribute()
        ukijumuisha open(self.tarname, "rb") kama fobj:
            self.assertIsInstance(fobj.name, str)
            ukijumuisha tarfile.open(fileobj=fobj, mode=self.mode) kama tar:
                self.assertIsInstance(tar.name, str)
                self.assertEqual(tar.name, os.path.abspath(fobj.name))

    eleza test_no_name_attribute(self):
        ukijumuisha open(self.tarname, "rb") kama fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        self.assertRaises(AttributeError, getattr, fobj, "name")
        tar = tarfile.open(fileobj=fobj, mode=self.mode)
        self.assertIsTupu(tar.name)

    eleza test_empty_name_attribute(self):
        ukijumuisha open(self.tarname, "rb") kama fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        fobj.name = ""
        ukijumuisha tarfile.open(fileobj=fobj, mode=self.mode) kama tar:
            self.assertIsTupu(tar.name)

    eleza test_int_name_attribute(self):
        # Issue 21044: tarfile.open() should handle fileobj ukijumuisha an integer
        # 'name' attribute.
        fd = os.open(self.tarname, os.O_RDONLY)
        ukijumuisha open(fd, 'rb') kama fobj:
            self.assertIsInstance(fobj.name, int)
            ukijumuisha tarfile.open(fileobj=fobj, mode=self.mode) kama tar:
                self.assertIsTupu(tar.name)

    eleza test_bytes_name_attribute(self):
        self.requires_name_attribute()
        tarname = os.fsencode(self.tarname)
        ukijumuisha open(tarname, 'rb') kama fobj:
            self.assertIsInstance(fobj.name, bytes)
            ukijumuisha tarfile.open(fileobj=fobj, mode=self.mode) kama tar:
                self.assertIsInstance(tar.name, bytes)
                self.assertEqual(tar.name, os.path.abspath(fobj.name))

    eleza test_pathlike_name(self):
        tarname = pathlib.Path(self.tarname)
        ukijumuisha tarfile.open(tarname, mode=self.mode) kama tar:
            self.assertIsInstance(tar.name, str)
            self.assertEqual(tar.name, os.path.abspath(os.fspath(tarname)))
        ukijumuisha self.taropen(tarname) kama tar:
            self.assertIsInstance(tar.name, str)
            self.assertEqual(tar.name, os.path.abspath(os.fspath(tarname)))
        ukijumuisha tarfile.TarFile.open(tarname, mode=self.mode) kama tar:
            self.assertIsInstance(tar.name, str)
            self.assertEqual(tar.name, os.path.abspath(os.fspath(tarname)))
        ikiwa self.suffix == '':
            ukijumuisha tarfile.TarFile(tarname, mode='r') kama tar:
                self.assertIsInstance(tar.name, str)
                self.assertEqual(tar.name, os.path.abspath(os.fspath(tarname)))

    eleza test_illegal_mode_arg(self):
        ukijumuisha open(tmpname, 'wb'):
            pita
        ukijumuisha self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, 'q')
        ukijumuisha self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, 'rw')
        ukijumuisha self.assertRaisesRegex(ValueError, 'mode must be '):
            tar = self.taropen(tmpname, '')

    eleza test_fileobj_with_offset(self):
        # Skip the first member na store values kutoka the second member
        # of the testtar.
        tar = tarfile.open(self.tarname, mode=self.mode)
        jaribu:
            tar.next()
            t = tar.next()
            name = t.name
            offset = t.offset
            ukijumuisha tar.extractfile(t) kama f:
                data = f.read()
        mwishowe:
            tar.close()

        # Open the testtar na seek to the offset of the second member.
        ukijumuisha self.open(self.tarname) kama fobj:
            fobj.seek(offset)

            # Test ikiwa the tarfile starts ukijumuisha the second member.
            ukijumuisha tar.open(self.tarname, mode="r:", fileobj=fobj) kama tar:
                t = tar.next()
                self.assertEqual(t.name, name)
                # Read to the end of fileobj na test ikiwa seeking back to the
                # beginning works.
                tar.getmembers()
                self.assertEqual(tar.extractfile(t).read(), data,
                        "seek back did sio work")

    eleza test_fail_comp(self):
        # For Gzip na Bz2 Tests: fail ukijumuisha a ReadError on an uncompressed file.
        self.assertRaises(tarfile.ReadError, tarfile.open, tarname, self.mode)
        ukijumuisha open(tarname, "rb") kama fobj:
            self.assertRaises(tarfile.ReadError, tarfile.open,
                              fileobj=fobj, mode=self.mode)

    eleza test_v7_dirtype(self):
        # Test old style dirtype member (bug #1336623):
        # Old V7 tars create directory members using an AREGTYPE
        # header ukijumuisha a "/" appended to the filename field.
        tarinfo = self.tar.getmember("misc/dirtype-old-v7")
        self.assertEqual(tarinfo.type, tarfile.DIRTYPE,
                "v7 dirtype failed")

    eleza test_xstar_type(self):
        # The xstar format stores extra atime na ctime fields inside the
        # space reserved kila the prefix field. The prefix field must be
        # ignored kwenye this case, otherwise it will mess up the name.
        jaribu:
            self.tar.getmember("misc/regtype-xstar")
        tatizo KeyError:
            self.fail("failed to find misc/regtype-xstar (mangled prefix?)")

    eleza test_check_members(self):
        kila tarinfo kwenye self.tar:
            self.assertEqual(int(tarinfo.mtime), 0o7606136617,
                    "wrong mtime kila %s" % tarinfo.name)
            ikiwa sio tarinfo.name.startswith("ustar/"):
                endelea
            self.assertEqual(tarinfo.uname, "tarfile",
                    "wrong uname kila %s" % tarinfo.name)

    eleza test_find_members(self):
        self.assertEqual(self.tar.getmembers()[-1].name, "misc/eof",
                "could sio find all members")

    @unittest.skipUnless(hasattr(os, "link"),
                         "Missing hardlink implementation")
    @support.skip_unless_symlink
    eleza test_extract_hardlink(self):
        # Test hardlink extraction (e.g. bug #857297).
        ukijumuisha tarfile.open(tarname, errorlevel=1, encoding="iso8859-1") kama tar:
            tar.extract("ustar/regtype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/regtype"))

            tar.extract("ustar/lnktype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/lnktype"))
            ukijumuisha open(os.path.join(TEMPDIR, "ustar/lnktype"), "rb") kama f:
                data = f.read()
            self.assertEqual(sha256sum(data), sha256_regtype)

            tar.extract("ustar/symtype", TEMPDIR)
            self.addCleanup(support.unlink, os.path.join(TEMPDIR, "ustar/symtype"))
            ukijumuisha open(os.path.join(TEMPDIR, "ustar/symtype"), "rb") kama f:
                data = f.read()
            self.assertEqual(sha256sum(data), sha256_regtype)

    eleza test_extractall(self):
        # Test ikiwa extractall() correctly restores directory permissions
        # na times (see issue1735).
        tar = tarfile.open(tarname, encoding="iso8859-1")
        DIR = os.path.join(TEMPDIR, "extractall")
        os.mkdir(DIR)
        jaribu:
            directories = [t kila t kwenye tar ikiwa t.isdir()]
            tar.extractall(DIR, directories)
            kila tarinfo kwenye directories:
                path = os.path.join(DIR, tarinfo.name)
                ikiwa sys.platform != "win32":
                    # Win32 has no support kila fine grained permissions.
                    self.assertEqual(tarinfo.mode & 0o777,
                                     os.stat(path).st_mode & 0o777)
                eleza format_mtime(mtime):
                    ikiwa isinstance(mtime, float):
                        rudisha "{} ({})".format(mtime, mtime.hex())
                    isipokua:
                        rudisha "{!r} (int)".format(mtime)
                file_mtime = os.path.getmtime(path)
                errmsg = "tar mtime {0} != file time {1} of path {2!a}".format(
                    format_mtime(tarinfo.mtime),
                    format_mtime(file_mtime),
                    path)
                self.assertEqual(tarinfo.mtime, file_mtime, errmsg)
        mwishowe:
            tar.close()
            support.rmtree(DIR)

    eleza test_extract_directory(self):
        dirtype = "ustar/dirtype"
        DIR = os.path.join(TEMPDIR, "extractdir")
        os.mkdir(DIR)
        jaribu:
            ukijumuisha tarfile.open(tarname, encoding="iso8859-1") kama tar:
                tarinfo = tar.getmember(dirtype)
                tar.extract(tarinfo, path=DIR)
                extracted = os.path.join(DIR, dirtype)
                self.assertEqual(os.path.getmtime(extracted), tarinfo.mtime)
                ikiwa sys.platform != "win32":
                    self.assertEqual(os.stat(extracted).st_mode & 0o777, 0o755)
        mwishowe:
            support.rmtree(DIR)

    eleza test_extractall_pathlike_name(self):
        DIR = pathlib.Path(TEMPDIR) / "extractall"
        ukijumuisha support.temp_dir(DIR), \
             tarfile.open(tarname, encoding="iso8859-1") kama tar:
            directories = [t kila t kwenye tar ikiwa t.isdir()]
            tar.extractall(DIR, directories)
            kila tarinfo kwenye directories:
                path = DIR / tarinfo.name
                self.assertEqual(os.path.getmtime(path), tarinfo.mtime)

    eleza test_extract_pathlike_name(self):
        dirtype = "ustar/dirtype"
        DIR = pathlib.Path(TEMPDIR) / "extractall"
        ukijumuisha support.temp_dir(DIR), \
             tarfile.open(tarname, encoding="iso8859-1") kama tar:
            tarinfo = tar.getmember(dirtype)
            tar.extract(tarinfo, path=DIR)
            extracted = DIR / dirtype
            self.assertEqual(os.path.getmtime(extracted), tarinfo.mtime)

    eleza test_init_close_fobj(self):
        # Issue #7341: Close the internal file object kwenye the TarFile
        # constructor kwenye case of an error. For the test we rely on
        # the fact that opening an empty file raises a ReadError.
        empty = os.path.join(TEMPDIR, "empty")
        ukijumuisha open(empty, "wb") kama fobj:
            fobj.write(b"")

        jaribu:
            tar = object.__new__(tarfile.TarFile)
            jaribu:
                tar.__init__(empty)
            tatizo tarfile.ReadError:
                self.assertKweli(tar.fileobj.closed)
            isipokua:
                self.fail("ReadError sio raised")
        mwishowe:
            support.unlink(empty)

    eleza test_parallel_iteration(self):
        # Issue #16601: Restarting iteration over tarfile endelead
        # kutoka where it left off.
        ukijumuisha tarfile.open(self.tarname) kama tar:
            kila m1, m2 kwenye zip(tar, tar):
                self.assertEqual(m1.offset, m2.offset)
                self.assertEqual(m1.get_info(), m2.get_info())

kundi MiscReadTest(MiscReadTestBase, unittest.TestCase):
    test_fail_comp = Tupu

kundi GzipMiscReadTest(GzipTest, MiscReadTestBase, unittest.TestCase):
    pita

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
        # caused seeking errors ukijumuisha stream tar files.
        kila tarinfo kwenye self.tar:
            ikiwa sio tarinfo.isreg():
                endelea
            ukijumuisha self.tar.extractfile(tarinfo) kama fobj:
                wakati Kweli:
                    jaribu:
                        buf = fobj.read(512)
                    tatizo tarfile.StreamError:
                        self.fail("simple read-through using "
                                  "TarFile.extractfile() failed")
                    ikiwa sio buf:
                        koma

    eleza test_fileobj_regular_file(self):
        tarinfo = self.tar.next() # get "regtype" (can't use getmember)
        ukijumuisha self.tar.extractfile(tarinfo) kama fobj:
            data = fobj.read()
        self.assertEqual(len(data), tarinfo.size,
                "regular file extraction failed")
        self.assertEqual(sha256sum(data), sha256_regtype,
                "regular file extraction failed")

    eleza test_provoke_stream_error(self):
        tarinfos = self.tar.getmembers()
        ukijumuisha self.tar.extractfile(tarinfos[0]) kama f: # read the first member
            self.assertRaises(tarfile.StreamError, f.read)

    eleza test_compare_members(self):
        tar1 = tarfile.open(tarname, encoding="iso8859-1")
        jaribu:
            tar2 = self.tar

            wakati Kweli:
                t1 = tar1.next()
                t2 = tar2.next()
                ikiwa t1 ni Tupu:
                    koma
                self.assertIsNotTupu(t2, "stream.next() failed.")

                ikiwa t2.islnk() ama t2.issym():
                    ukijumuisha self.assertRaises(tarfile.StreamError):
                        tar2.extractfile(t2)
                    endelea

                v1 = tar1.extractfile(t1)
                v2 = tar2.extractfile(t2)
                ikiwa v1 ni Tupu:
                    endelea
                self.assertIsNotTupu(v2, "stream.extractfile() failed")
                self.assertEqual(v1.read(), v2.read(),
                        "stream extraction failed")
        mwishowe:
            tar1.close()

kundi GzipStreamReadTest(GzipTest, StreamReadTest):
    pita

kundi Bz2StreamReadTest(Bz2Test, StreamReadTest):
    pita

kundi LzmaStreamReadTest(LzmaTest, StreamReadTest):
    pita


kundi DetectReadTest(TarTest, unittest.TestCase):
    eleza _testfunc_file(self, name, mode):
        jaribu:
            tar = tarfile.open(name, mode)
        tatizo tarfile.ReadError kama e:
            self.fail()
        isipokua:
            tar.close()

    eleza _testfunc_fileobj(self, name, mode):
        jaribu:
            ukijumuisha open(name, "rb") kama f:
                tar = tarfile.open(name, mode, fileobj=f)
        tatizo tarfile.ReadError kama e:
            self.fail()
        isipokua:
            tar.close()

    eleza _test_modes(self, testfunc):
        ikiwa self.suffix:
            ukijumuisha self.assertRaises(tarfile.ReadError):
                tarfile.open(tarname, mode="r:" + self.suffix)
            ukijumuisha self.assertRaises(tarfile.ReadError):
                tarfile.open(tarname, mode="r|" + self.suffix)
            ukijumuisha self.assertRaises(tarfile.ReadError):
                tarfile.open(self.tarname, mode="r:")
            ukijumuisha self.assertRaises(tarfile.ReadError):
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
    pita

kundi Bz2DetectReadTest(Bz2Test, DetectReadTest):
    eleza test_detect_stream_bz2(self):
        # Originally, tarfile's stream detection looked kila the string
        # "BZh91" at the start of the file. This ni incorrect because
        # the '9' represents the blocksize (900,000 bytes). If the file was
        # compressed using another blocksize autodetection fails.
        ukijumuisha open(tarname, "rb") kama fobj:
            data = fobj.read()

        # Compress ukijumuisha blocksize 100,000 bytes, the file starts ukijumuisha "BZh11".
        ukijumuisha bz2.BZ2File(tmpname, "wb", compresslevel=1) kama fobj:
            fobj.write(data)

        self._testfunc_file(tmpname, "r|*")

kundi LzmaDetectReadTest(LzmaTest, DetectReadTest):
    pita


kundi MemberReadTest(ReadTest, unittest.TestCase):

    eleza _test_member(self, tarinfo, chksum=Tupu, **kwargs):
        ikiwa chksum ni sio Tupu:
            ukijumuisha self.tar.extractfile(tarinfo) kama f:
                self.assertEqual(sha256sum(f.read()), chksum,
                        "wrong sha256sum kila %s" % tarinfo.name)

        kwargs["mtime"] = 0o7606136617
        kwargs["uid"] = 1000
        kwargs["gid"] = 100
        ikiwa "old-v7" haiko kwenye tarinfo.name:
            # V7 tar can't handle alphabetic owners.
            kwargs["uname"] = "tarfile"
            kwargs["gname"] = "tarfile"
        kila k, v kwenye kwargs.items():
            self.assertEqual(getattr(tarinfo, k), v,
                    "wrong value kwenye %s field of %s" % (k, tarinfo.name))

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
        jaribu:
            tarinfo = self.tar.getmember(longname)
        tatizo KeyError:
            self.fail("longname sio found")
        self.assertNotEqual(tarinfo.type, tarfile.DIRTYPE,
                "read longname kama dirtype")

    eleza test_read_longlink(self):
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        longlink = self.subdir + "/" + "123/" * 125 + "longlink"
        jaribu:
            tarinfo = self.tar.getmember(longlink)
        tatizo KeyError:
            self.fail("longlink sio found")
        self.assertEqual(tarinfo.linkname, longname, "linkname wrong")

    eleza test_truncated_longname(self):
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        tarinfo = self.tar.getmember(longname)
        offset = tarinfo.offset
        self.tar.fileobj.seek(offset)
        fobj = io.BytesIO(self.tar.fileobj.read(3 * 512))
        ukijumuisha self.assertRaises(tarfile.ReadError):
            tarfile.open(name="foo.tar", fileobj=fobj)

    eleza test_header_offset(self):
        # Test ikiwa the start offset of the TarInfo object includes
        # the preceding extended header.
        longname = self.subdir + "/" + "123/" * 125 + "longname"
        offset = self.tar.getmember(longname).offset
        ukijumuisha open(tarname, "rb") kama fobj:
            fobj.seek(offset)
            tarinfo = tarfile.TarInfo.frombuf(fobj.read(512),
                                              "iso8859-1", "strict")
            self.assertEqual(tarinfo.type, self.longnametype)


kundi GNUReadTest(LongnameTest, ReadTest, unittest.TestCase):

    subdir = "gnu"
    longnametype = tarfile.GNUTYPE_LONGNAME

    # Since 3.2 tarfile ni supposed to accurately restore sparse members na
    # produce files ukijumuisha holes. This ni what we actually want to test here.
    # Unfortunately, sio all platforms/filesystems support sparse files, na
    # even on platforms that do it ni non-trivial to make reliable assertions
    # about holes kwenye files. Therefore, we first do one basic test which works
    # an all platforms, na after that a test that will work only on
    # platforms/filesystems that prove to support sparse files.
    eleza _test_sparse_file(self, name):
        self.tar.extract(name, TEMPDIR)
        filename = os.path.join(TEMPDIR, name)
        ukijumuisha open(filename, "rb") kama fobj:
            data = fobj.read()
        self.assertEqual(sha256sum(data), sha256_sparse,
                "wrong sha256sum kila %s" % name)

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
        # Return Kweli ikiwa the platform knows the st_blocks stat attribute na
        # uses st_blocks units of 512 bytes, na ikiwa the filesystem ni able to
        # store holes of 4 KiB kwenye files.
        #
        # The function returns Uongo ikiwa page size ni larger than 4 KiB.
        # For example, ppc64 uses pages of 64 KiB.
        ikiwa sys.platform.startswith("linux"):
            # Linux evidentially has 512 byte st_blocks units.
            name = os.path.join(TEMPDIR, "sparse-test")
            ukijumuisha open(name, "wb") kama fobj:
                # Seek to "punch a hole" of 4 KiB
                fobj.seek(4096)
                fobj.write(b'x' * 4096)
                fobj.truncate()
            s = os.stat(name)
            support.unlink(name)
            rudisha (s.st_blocks * 512 < s.st_size)
        isipokua:
            rudisha Uongo


kundi PaxReadTest(LongnameTest, ReadTest, unittest.TestCase):

    subdir = "pax"
    longnametype = tarfile.XHDTYPE

    eleza test_pax_global_headers(self):
        tar = tarfile.open(tarname, encoding="iso8859-1")
        jaribu:
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
        mwishowe:
            tar.close()

    eleza test_pax_number_fields(self):
        # All following number fields are read kutoka the pax header.
        tar = tarfile.open(tarname, encoding="iso8859-1")
        jaribu:
            tarinfo = tar.getmember("pax/regtype4")
            self.assertEqual(tarinfo.size, 7011)
            self.assertEqual(tarinfo.uid, 123)
            self.assertEqual(tarinfo.gid, 123)
            self.assertEqual(tarinfo.mtime, 1041808783.0)
            self.assertEqual(type(tarinfo.mtime), float)
            self.assertEqual(float(tarinfo.pax_headers["atime"]), 1041808783.0)
            self.assertEqual(float(tarinfo.pax_headers["ctime"]), 1041808783.0)
        mwishowe:
            tar.close()


kundi WriteTestBase(TarTest):
    # Put all write tests kwenye here that are supposed to be tested
    # kwenye all possible mode combinations.

    eleza test_fileobj_no_close(self):
        fobj = io.BytesIO()
        ukijumuisha tarfile.open(fileobj=fobj, mode=self.mode) kama tar:
            tar.addfile(tarfile.TarInfo("foo"))
        self.assertUongo(fobj.closed, "external fileobjs must never closed")
        # Issue #20238: Incomplete gzip output ukijumuisha mode="w:gz"
        data = fobj.getvalue()
        toa tar
        support.gc_collect()
        self.assertUongo(fobj.closed)
        self.assertEqual(data, fobj.getvalue())

    eleza test_eof_marker(self):
        # Make sure an end of archive marker ni written (two zero blocks).
        # tarfile insists on aligning archives to a 20 * 512 byte recordsize.
        # So, we create an archive that has exactly 10240 bytes without the
        # marker, na has 20480 bytes once the marker ni written.
        ukijumuisha tarfile.open(tmpname, self.mode) kama tar:
            t = tarfile.TarInfo("foo")
            t.size = tarfile.RECORDSIZE - tarfile.BLOCKSIZE
            tar.addfile(t, io.BytesIO(b"a" * t.size))

        ukijumuisha self.open(tmpname, "rb") kama fobj:
            self.assertEqual(len(fobj.read()), tarfile.RECORDSIZE * 2)


kundi WriteTest(WriteTestBase, unittest.TestCase):

    prefix = "w:"

    eleza test_100_char_name(self):
        # The name field kwenye a tar header stores strings of at most 100 chars.
        # If a string ni shorter than 100 chars it has to be padded ukijumuisha '\0',
        # which implies that a string of exactly 100 chars ni stored without
        # a trailing '\0'.
        name = "0123456789" * 10
        tar = tarfile.open(tmpname, self.mode)
        jaribu:
            t = tarfile.TarInfo(name)
            tar.addfile(t)
        mwishowe:
            tar.close()

        tar = tarfile.open(tmpname)
        jaribu:
            self.assertEqual(tar.getnames()[0], name,
                    "failed to store 100 char filename")
        mwishowe:
            tar.close()

    eleza test_tar_size(self):
        # Test kila bug #1013882.
        tar = tarfile.open(tmpname, self.mode)
        jaribu:
            path = os.path.join(TEMPDIR, "file")
            ukijumuisha open(path, "wb") kama fobj:
                fobj.write(b"aaa")
            tar.add(path)
        mwishowe:
            tar.close()
        self.assertGreater(os.path.getsize(tmpname), 0,
                "tarfile ni empty")

    # The test_*_size tests test kila bug #1167128.
    eleza test_file_size(self):
        tar = tarfile.open(tmpname, self.mode)
        jaribu:
            path = os.path.join(TEMPDIR, "file")
            ukijumuisha open(path, "wb"):
                pita
            tarinfo = tar.gettarinfo(path)
            self.assertEqual(tarinfo.size, 0)

            ukijumuisha open(path, "wb") kama fobj:
                fobj.write(b"aaa")
            tarinfo = tar.gettarinfo(path)
            self.assertEqual(tarinfo.size, 3)
        mwishowe:
            tar.close()

    eleza test_directory_size(self):
        path = os.path.join(TEMPDIR, "directory")
        os.mkdir(path)
        jaribu:
            tar = tarfile.open(tmpname, self.mode)
            jaribu:
                tarinfo = tar.gettarinfo(path)
                self.assertEqual(tarinfo.size, 0)
            mwishowe:
                tar.close()
        mwishowe:
            support.rmdir(path)

    # mock the following:
    #  os.listdir: so we know that files are kwenye the wrong order
    eleza test_ordered_recursion(self):
        path = os.path.join(TEMPDIR, "directory")
        os.mkdir(path)
        open(os.path.join(path, "1"), "a").close()
        open(os.path.join(path, "2"), "a").close()
        jaribu:
            tar = tarfile.open(tmpname, self.mode)
            jaribu:
                ukijumuisha unittest.mock.patch('os.listdir') kama mock_listdir:
                    mock_listdir.return_value = ["2", "1"]
                    tar.add(path)
                paths = []
                kila m kwenye tar.getmembers():
                    paths.append(os.path.split(m.name)[-1])
                self.assertEqual(paths, ["directory", "1", "2"]);
            mwishowe:
                tar.close()
        mwishowe:
            support.unlink(os.path.join(path, "1"))
            support.unlink(os.path.join(path, "2"))
            support.rmdir(path)

    eleza test_gettarinfo_pathlike_name(self):
        ukijumuisha tarfile.open(tmpname, self.mode) kama tar:
            path = pathlib.Path(TEMPDIR) / "file"
            ukijumuisha open(path, "wb") kama fobj:
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
        ukijumuisha open(target, "wb") kama fobj:
            fobj.write(b"aaa")
        jaribu:
            os.link(target, link)
        tatizo PermissionError kama e:
            self.skipTest('os.link(): %s' % e)
        jaribu:
            tar = tarfile.open(tmpname, self.mode)
            jaribu:
                # Record the link target kwenye the inodes list.
                tar.gettarinfo(target)
                tarinfo = tar.gettarinfo(link)
                self.assertEqual(tarinfo.size, 0)
            mwishowe:
                tar.close()
        mwishowe:
            support.unlink(target)
            support.unlink(link)

    @support.skip_unless_symlink
    eleza test_symlink_size(self):
        path = os.path.join(TEMPDIR, "symlink")
        os.symlink("link_target", path)
        jaribu:
            tar = tarfile.open(tmpname, self.mode)
            jaribu:
                tarinfo = tar.gettarinfo(path)
                self.assertEqual(tarinfo.size, 0)
            mwishowe:
                tar.close()
        mwishowe:
            support.unlink(path)

    eleza test_add_self(self):
        # Test kila #1257255.
        dstname = os.path.abspath(tmpname)
        tar = tarfile.open(tmpname, self.mode)
        jaribu:
            self.assertEqual(tar.name, dstname,
                    "archive name must be absolute")
            tar.add(dstname)
            self.assertEqual(tar.getnames(), [],
                    "added the archive to itself")

            ukijumuisha support.change_cwd(TEMPDIR):
                tar.add(dstname)
            self.assertEqual(tar.getnames(), [],
                    "added the archive to itself")
        mwishowe:
            tar.close()

    eleza test_filter(self):
        tempdir = os.path.join(TEMPDIR, "filter")
        os.mkdir(tempdir)
        jaribu:
            kila name kwenye ("foo", "bar", "baz"):
                name = os.path.join(tempdir, name)
                support.create_empty_file(name)

            eleza filter(tarinfo):
                ikiwa os.path.basename(tarinfo.name) == "bar":
                    rudisha
                tarinfo.uid = 123
                tarinfo.uname = "foo"
                rudisha tarinfo

            tar = tarfile.open(tmpname, self.mode, encoding="iso8859-1")
            jaribu:
                tar.add(tempdir, arcname="empty_dir", filter=filter)
            mwishowe:
                tar.close()

            # Verify that filter ni a keyword-only argument
            ukijumuisha self.assertRaises(TypeError):
                tar.add(tempdir, "empty_dir", Kweli, Tupu, filter)

            tar = tarfile.open(tmpname, "r")
            jaribu:
                kila tarinfo kwenye tar:
                    self.assertEqual(tarinfo.uid, 123)
                    self.assertEqual(tarinfo.uname, "foo")
                self.assertEqual(len(tar.getmembers()), 3)
            mwishowe:
                tar.close()
        mwishowe:
            support.rmtree(tempdir)

    # Guarantee that stored pathnames are sio modified. Don't
    # remove ./ ama ../ ama double slashes. Still make absolute
    # pathnames relative.
    # For details see bug #6054.
    eleza _test_pathname(self, path, cmp_path=Tupu, dir=Uongo):
        # Create a tarfile ukijumuisha an empty member named path
        # na compare the stored name ukijumuisha the original.
        foo = os.path.join(TEMPDIR, "foo")
        ikiwa sio dir:
            support.create_empty_file(foo)
        isipokua:
            os.mkdir(foo)

        tar = tarfile.open(tmpname, self.mode)
        jaribu:
            tar.add(foo, arcname=path)
        mwishowe:
            tar.close()

        tar = tarfile.open(tmpname, "r")
        jaribu:
            t = tar.next()
        mwishowe:
            tar.close()

        ikiwa sio dir:
            support.unlink(foo)
        isipokua:
            support.rmdir(foo)

        self.assertEqual(t.name, cmp_path ama path.replace(os.sep, "/"))


    @support.skip_unless_symlink
    eleza test_extractall_symlinks(self):
        # Test ikiwa extractall works properly when tarfile contains symlinks
        tempdir = os.path.join(TEMPDIR, "testsymlinks")
        temparchive = os.path.join(TEMPDIR, "testsymlinks.tar")
        os.mkdir(tempdir)
        jaribu:
            source_file = os.path.join(tempdir,'source')
            target_file = os.path.join(tempdir,'symlink')
            ukijumuisha open(source_file,'w') kama f:
                f.write('something\n')
            os.symlink(source_file, target_file)
            ukijumuisha tarfile.open(temparchive, 'w') kama tar:
                tar.add(source_file)
                tar.add(target_file)
            # Let's extract it to the location which contains the symlink
            ukijumuisha tarfile.open(temparchive) kama tar:
                # this should sio ashiria OSError: [Errno 17] File exists
                jaribu:
                    tar.extractall(path=tempdir)
                tatizo OSError:
                    self.fail("extractall failed ukijumuisha symlinked files")
        mwishowe:
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
        self._test_pathname("foo" + os.sep + os.sep, "foo", dir=Kweli)

    eleza test_abs_pathnames(self):
        ikiwa sys.platform == "win32":
            self._test_pathname("C:\\foo", "foo")
        isipokua:
            self._test_pathname("/foo", "foo")
            self._test_pathname("///foo", "foo")

    eleza test_cwd(self):
        # Test adding the current working directory.
        ukijumuisha support.change_cwd(TEMPDIR):
            tar = tarfile.open(tmpname, self.mode)
            jaribu:
                tar.add(".")
            mwishowe:
                tar.close()

            tar = tarfile.open(tmpname, "r")
            jaribu:
                kila t kwenye tar:
                    ikiwa t.name != ".":
                        self.assertKweli(t.name.startswith("./"), t.name)
            mwishowe:
                tar.close()

    eleza test_open_nonwritable_fileobj(self):
        kila exctype kwenye OSError, EOFError, RuntimeError:
            kundi BadFile(io.BytesIO):
                first = Kweli
                eleza write(self, data):
                    ikiwa self.first:
                        self.first = Uongo
                        ashiria exctype

            f = BadFile()
            ukijumuisha self.assertRaises(exctype):
                tar = tarfile.open(tmpname, self.mode, fileobj=f,
                                   format=tarfile.PAX_FORMAT,
                                   pax_headers={'non': 'empty'})
            self.assertUongo(f.closed)

kundi GzipWriteTest(GzipTest, WriteTest):
    pita

kundi Bz2WriteTest(Bz2Test, WriteTest):
    pita

kundi LzmaWriteTest(LzmaTest, WriteTest):
    pita


kundi StreamWriteTest(WriteTestBase, unittest.TestCase):

    prefix = "w|"
    decompressor = Tupu

    eleza test_stream_padding(self):
        # Test kila bug #1543303.
        tar = tarfile.open(tmpname, self.mode)
        tar.close()
        ikiwa self.decompressor:
            dec = self.decompressor()
            ukijumuisha open(tmpname, "rb") kama fobj:
                data = fobj.read()
            data = dec.decompress(data)
            self.assertUongo(dec.unused_data, "found trailing data")
        isipokua:
            ukijumuisha self.open(tmpname) kama fobj:
                data = fobj.read()
        self.assertEqual(data.count(b"\0"), tarfile.RECORDSIZE,
                        "incorrect zero padding")

    @unittest.skipUnless(sys.platform != "win32" na hasattr(os, "umask"),
                         "Missing umask implementation")
    eleza test_file_mode(self):
        # Test kila issue #8464: Create files ukijumuisha correct
        # permissions.
        ikiwa os.path.exists(tmpname):
            support.unlink(tmpname)

        original_umask = os.umask(0o022)
        jaribu:
            tar = tarfile.open(tmpname, self.mode)
            tar.close()
            mode = os.stat(tmpname).st_mode & 0o777
            self.assertEqual(mode, 0o644, "wrong file permissions")
        mwishowe:
            os.umask(original_umask)

kundi GzipStreamWriteTest(GzipTest, StreamWriteTest):
    pita

kundi Bz2StreamWriteTest(Bz2Test, StreamWriteTest):
    decompressor = bz2.BZ2Decompressor ikiwa bz2 isipokua Tupu

kundi LzmaStreamWriteTest(LzmaTest, StreamWriteTest):
    decompressor = lzma.LZMADecompressor ikiwa lzma isipokua Tupu


kundi GNUWriteTest(unittest.TestCase):
    # This testcase checks kila correct creation of GNU Longname
    # na Longlink extended headers (cp. bug #812325).

    eleza _length(self, s):
        blocks = len(s) // 512 + 1
        rudisha blocks * 512

    eleza _calc_size(self, name, link=Tupu):
        # Initial tar header
        count = 512

        ikiwa len(name) > tarfile.LENGTH_NAME:
            # GNU longname extended header + longname
            count += 512
            count += self._length(name)
        ikiwa link ni sio Tupu na len(link) > tarfile.LENGTH_LINK:
            # GNU longlink extended header + longlink
            count += 512
            count += self._length(link)
        rudisha count

    eleza _test(self, name, link=Tupu):
        tarinfo = tarfile.TarInfo(name)
        ikiwa link:
            tarinfo.linkname = link
            tarinfo.type = tarfile.LNKTYPE

        tar = tarfile.open(tmpname, "w")
        jaribu:
            tar.format = tarfile.GNU_FORMAT
            tar.addfile(tarinfo)

            v1 = self._calc_size(name, link)
            v2 = tar.offset
            self.assertEqual(v1, v2, "GNU longname/longlink creation failed")
        mwishowe:
            tar.close()

        tar = tarfile.open(tmpname)
        jaribu:
            member = tar.next()
            self.assertIsNotTupu(member,
                    "unable to read longname member")
            self.assertEqual(tarinfo.name, member.name,
                    "unable to read longname member")
            self.assertEqual(tarinfo.linkname, member.linkname,
                    "unable to read longname member")
        mwishowe:
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
        ukijumuisha open(cls.file_path, "wb") kama fobj:
            fobj.write(b"aaa")

    @classmethod
    eleza tearDownClass(cls):
        support.unlink(cls.file_path)

    eleza test_create(self):
        ukijumuisha tarfile.open(tmpname, self.mode) kama tobj:
            tobj.add(self.file_path)

        ukijumuisha self.taropen(tmpname) kama tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    eleza test_create_existing(self):
        ukijumuisha tarfile.open(tmpname, self.mode) kama tobj:
            tobj.add(self.file_path)

        ukijumuisha self.assertRaises(FileExistsError):
            tobj = tarfile.open(tmpname, self.mode)

        ukijumuisha self.taropen(tmpname) kama tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    eleza test_create_taropen(self):
        ukijumuisha self.taropen(tmpname, "x") kama tobj:
            tobj.add(self.file_path)

        ukijumuisha self.taropen(tmpname) kama tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    eleza test_create_existing_taropen(self):
        ukijumuisha self.taropen(tmpname, "x") kama tobj:
            tobj.add(self.file_path)

        ukijumuisha self.assertRaises(FileExistsError):
            ukijumuisha self.taropen(tmpname, "x"):
                pita

        ukijumuisha self.taropen(tmpname) kama tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn("spameggs42", names[0])

    eleza test_create_pathlike_name(self):
        ukijumuisha tarfile.open(pathlib.Path(tmpname), self.mode) kama tobj:
            self.assertIsInstance(tobj.name, str)
            self.assertEqual(tobj.name, os.path.abspath(tmpname))
            tobj.add(pathlib.Path(self.file_path))
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

        ukijumuisha self.taropen(tmpname) kama tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

    eleza test_create_taropen_pathlike_name(self):
        ukijumuisha self.taropen(pathlib.Path(tmpname), "x") kama tobj:
            self.assertIsInstance(tobj.name, str)
            self.assertEqual(tobj.name, os.path.abspath(tmpname))
            tobj.add(pathlib.Path(self.file_path))
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])

        ukijumuisha self.taropen(tmpname) kama tobj:
            names = tobj.getnames()
        self.assertEqual(len(names), 1)
        self.assertIn('spameggs42', names[0])


kundi GzipCreateTest(GzipTest, CreateTest):
    pita


kundi Bz2CreateTest(Bz2Test, CreateTest):
    pita


kundi LzmaCreateTest(LzmaTest, CreateTest):
    pita


kundi CreateWithXModeTest(CreateTest):

    prefix = "x"

    test_create_taropen = Tupu
    test_create_existing_taropen = Tupu


@unittest.skipUnless(hasattr(os, "link"), "Missing hardlink implementation")
kundi HardlinkTest(unittest.TestCase):
    # Test the creation of LNKTYPE (hardlink) members kwenye an archive.

    eleza setUp(self):
        self.foo = os.path.join(TEMPDIR, "foo")
        self.bar = os.path.join(TEMPDIR, "bar")

        ukijumuisha open(self.foo, "wb") kama fobj:
            fobj.write(b"foo")

        jaribu:
            os.link(self.foo, self.bar)
        tatizo PermissionError kama e:
            self.skipTest('os.link(): %s' % e)

        self.tar = tarfile.open(tmpname, "w")
        self.tar.add(self.foo)

    eleza tearDown(self):
        self.tar.close()
        support.unlink(self.foo)
        support.unlink(self.bar)

    eleza test_add_twice(self):
        # The same name will be added kama a REGTYPE every
        # time regardless of st_nlink.
        tarinfo = self.tar.gettarinfo(self.foo)
        self.assertEqual(tarinfo.type, tarfile.REGTYPE,
                "add file kama regular failed")

    eleza test_add_hardlink(self):
        tarinfo = self.tar.gettarinfo(self.bar)
        self.assertEqual(tarinfo.type, tarfile.LNKTYPE,
                "add file kama hardlink failed")

    eleza test_dereference_hardlink(self):
        self.tar.dereference = Kweli
        tarinfo = self.tar.gettarinfo(self.bar)
        self.assertEqual(tarinfo.type, tarfile.REGTYPE,
                "dereferencing hardlink failed")


kundi PaxWriteTest(GNUWriteTest):

    eleza _test(self, name, link=Tupu):
        # See GNUWriteTest.
        tarinfo = tarfile.TarInfo(name)
        ikiwa link:
            tarinfo.linkname = link
            tarinfo.type = tarfile.LNKTYPE

        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT)
        jaribu:
            tar.addfile(tarinfo)
        mwishowe:
            tar.close()

        tar = tarfile.open(tmpname)
        jaribu:
            ikiwa link:
                l = tar.getmembers()[0].linkname
                self.assertEqual(link, l, "PAX longlink creation failed")
            isipokua:
                n = tar.getmembers()[0].name
                self.assertEqual(name, n, "PAX longname creation failed")
        mwishowe:
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
        jaribu:
            tar.addfile(tarfile.TarInfo("test"))
        mwishowe:
            tar.close()

        # Test ikiwa the global header was written correctly.
        tar = tarfile.open(tmpname, encoding="iso8859-1")
        jaribu:
            self.assertEqual(tar.pax_headers, pax_headers)
            self.assertEqual(tar.getmembers()[0].pax_headers, pax_headers)
            # Test ikiwa all the fields are strings.
            kila key, val kwenye tar.pax_headers.items():
                self.assertIsNot(type(key), bytes)
                self.assertIsNot(type(val), bytes)
                ikiwa key kwenye tarfile.PAX_NUMBER_FIELDS:
                    jaribu:
                        tarfile.PAX_NUMBER_FIELDS[key](val)
                    tatizo (TypeError, ValueError):
                        self.fail("unable to convert pax header field")
        mwishowe:
            tar.close()

    eleza test_pax_extended_header(self):
        # The fields kutoka the pax header have priority over the
        # TarInfo.
        pax_headers = {"path": "foo", "uid": "123"}

        tar = tarfile.open(tmpname, "w", format=tarfile.PAX_FORMAT,
                           encoding="iso8859-1")
        jaribu:
            t = tarfile.TarInfo()
            t.name = "\xe4\xf6\xfc" # non-ASCII
            t.uid = 8**8 # too large
            t.pax_headers = pax_headers
            tar.addfile(t)
        mwishowe:
            tar.close()

        tar = tarfile.open(tmpname, encoding="iso8859-1")
        jaribu:
            t = tar.getmembers()[0]
            self.assertEqual(t.pax_headers, pax_headers)
            self.assertEqual(t.name, "foo")
            self.assertEqual(t.uid, 123)
        mwishowe:
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
        jaribu:
            name = "\xe4\xf6\xfc"
            tar.addfile(tarfile.TarInfo(name))
        mwishowe:
            tar.close()

        tar = tarfile.open(tmpname, encoding=encoding)
        jaribu:
            self.assertEqual(tar.getmembers()[0].name, name)
        mwishowe:
            tar.close()

    eleza test_unicode_filename_error(self):
        tar = tarfile.open(tmpname, "w", format=self.format,
                           encoding="ascii", errors="strict")
        jaribu:
            tarinfo = tarfile.TarInfo()

            tarinfo.name = "\xe4\xf6\xfc"
            self.assertRaises(UnicodeError, tar.addfile, tarinfo)

            tarinfo.name = "foo"
            tarinfo.uname = "\xe4\xf6\xfc"
            self.assertRaises(UnicodeError, tar.addfile, tarinfo)
        mwishowe:
            tar.close()

    eleza test_unicode_argument(self):
        tar = tarfile.open(tarname, "r",
                           encoding="iso8859-1", errors="strict")
        jaribu:
            kila t kwenye tar:
                self.assertIs(type(t.name), str)
                self.assertIs(type(t.linkname), str)
                self.assertIs(type(t.uname), str)
                self.assertIs(type(t.gname), str)
        mwishowe:
            tar.close()

    eleza test_uname_unicode(self):
        t = tarfile.TarInfo("foo")
        t.uname = "\xe4\xf6\xfc"
        t.gname = "\xe4\xf6\xfc"

        tar = tarfile.open(tmpname, mode="w", format=self.format,
                           encoding="iso8859-1")
        jaribu:
            tar.addfile(t)
        mwishowe:
            tar.close()

        tar = tarfile.open(tmpname, encoding="iso8859-1")
        jaribu:
            t = tar.getmember("foo")
            self.assertEqual(t.uname, "\xe4\xf6\xfc")
            self.assertEqual(t.gname, "\xe4\xf6\xfc")

            ikiwa self.format != tarfile.PAX_FORMAT:
                tar.close()
                tar = tarfile.open(tmpname, encoding="ascii")
                t = tar.getmember("foo")
                self.assertEqual(t.uname, "\udce4\udcf6\udcfc")
                self.assertEqual(t.gname, "\udce4\udcf6\udcfc")
        mwishowe:
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

    eleza _test_ustar_name(self, name, exc=Tupu):
        ukijumuisha tarfile.open(tmpname, "w", format=self.format, encoding="utf-8") kama tar:
            t = tarfile.TarInfo(name)
            ikiwa exc ni Tupu:
                tar.addfile(t)
            isipokua:
                self.assertRaises(exc, tar.addfile, t)

        ikiwa exc ni Tupu:
            ukijumuisha tarfile.open(tmpname, "r", encoding="utf-8") kama tar:
                kila t kwenye tar:
                    self.assertEqual(name, t.name)
                    koma

    # Test the same kama above kila the 100 bytes link field.
    eleza test_unicode_link1(self):
        self._test_ustar_link("0123456789" * 10)
        self._test_ustar_link("0123456789" * 10 + "0", ValueError)
        self._test_ustar_link("0123456789" * 9 + "01234567\xff")
        self._test_ustar_link("0123456789" * 9 + "012345678\xff", ValueError)

    eleza test_unicode_link2(self):
        self._test_ustar_link("0123456789" * 9 + "012345\xff\xff")
        self._test_ustar_link("0123456789" * 9 + "0123456\xff\xff", ValueError)

    eleza _test_ustar_link(self, name, exc=Tupu):
        ukijumuisha tarfile.open(tmpname, "w", format=self.format, encoding="utf-8") kama tar:
            t = tarfile.TarInfo("foo")
            t.linkname = name
            ikiwa exc ni Tupu:
                tar.addfile(t)
            isipokua:
                self.assertRaises(exc, tar.addfile, t)

        ikiwa exc ni Tupu:
            ukijumuisha tarfile.open(tmpname, "r", encoding="utf-8") kama tar:
                kila t kwenye tar:
                    self.assertEqual(name, t.linkname)
                    koma


kundi GNUUnicodeTest(UnicodeTest, unittest.TestCase):

    format = tarfile.GNU_FORMAT

    eleza test_bad_pax_header(self):
        # Test kila issue #8633. GNU tar <= 1.23 creates raw binary fields
        # without a hdrcharset=BINARY header.
        kila encoding, name kwenye (
                ("utf-8", "pax/bad-pax-\udce4\udcf6\udcfc"),
                ("iso8859-1", "pax/bad-pax-\xe4\xf6\xfc"),):
            ukijumuisha tarfile.open(tarname, encoding=encoding,
                              errors="surrogateescape") kama tar:
                jaribu:
                    t = tar.getmember(name)
                tatizo KeyError:
                    self.fail("unable to read bad GNU tar pax header")


kundi PAXUnicodeTest(UnicodeTest, unittest.TestCase):

    format = tarfile.PAX_FORMAT

    # PAX_FORMAT ignores encoding kwenye write mode.
    test_unicode_filename_error = Tupu

    eleza test_binary_header(self):
        # Test a POSIX.1-2008 compatible header ukijumuisha a hdrcharset=BINARY field.
        kila encoding, name kwenye (
                ("utf-8", "pax/hdrcharset-\udce4\udcf6\udcfc"),
                ("iso8859-1", "pax/hdrcharset-\xe4\xf6\xfc"),):
            ukijumuisha tarfile.open(tarname, encoding=encoding,
                              errors="surrogateescape") kama tar:
                jaribu:
                    t = tar.getmember(name)
                tatizo KeyError:
                    self.fail("unable to read POSIX.1-2008 binary header")


kundi AppendTestBase:
    # Test append mode (cp. patch #1652681).

    eleza setUp(self):
        self.tarname = tmpname
        ikiwa os.path.exists(self.tarname):
            support.unlink(self.tarname)

    eleza _create_testtar(self, mode="w:"):
        ukijumuisha tarfile.open(tarname, encoding="iso8859-1") kama src:
            t = src.getmember("ustar/regtype")
            t.name = "foo"
            ukijumuisha src.extractfile(t) kama f:
                ukijumuisha tarfile.open(self.tarname, mode) kama tar:
                    tar.addfile(t, f)

    eleza test_append_compressed(self):
        self._create_testtar("w:" + self.suffix)
        self.assertRaises(tarfile.ReadError, tarfile.open, tmpname, "a")

kundi AppendTest(AppendTestBase, unittest.TestCase):
    test_append_compressed = Tupu

    eleza _add_testfile(self, fileobj=Tupu):
        ukijumuisha tarfile.open(self.tarname, "a", fileobj=fileobj) kama tar:
            tar.addfile(tarfile.TarInfo("bar"))

    eleza _test(self, names=["bar"], fileobj=Tupu):
        ukijumuisha tarfile.open(self.tarname, fileobj=fileobj) kama tar:
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
        ukijumuisha open(self.tarname, "rb") kama fobj:
            data = fobj.read()
        fobj = io.BytesIO(data)
        self._add_testfile(fobj)
        fobj.seek(0)
        self._test(names=["foo", "bar"], fileobj=fobj)

    eleza test_existing(self):
        self._create_testtar()
        self._add_testfile()
        self._test(names=["foo", "bar"])

    # Append mode ni supposed to fail ikiwa the tarfile to append to
    # does sio end ukijumuisha a zero block.
    eleza _test_error(self, data):
        ukijumuisha open(self.tarname, "wb") kama fobj:
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
    pita

kundi Bz2AppendTest(Bz2Test, AppendTestBase, unittest.TestCase):
    pita

kundi LzmaAppendTest(LzmaTest, AppendTestBase, unittest.TestCase):
    pita


kundi LimitsTest(unittest.TestCase):

    eleza test_ustar_limits(self):
        # 100 char name
        tarinfo = tarfile.TarInfo("0123456789" * 10)
        tarinfo.tobuf(tarfile.USTAR_FORMAT)

        # 101 char name that cannot be stored
        tarinfo = tarfile.TarInfo("0123456789" * 10 + "0")
        self.assertRaises(ValueError, tarinfo.tobuf, tarfile.USTAR_FORMAT)

        # 256 char name ukijumuisha a slash at pos 156
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
        ukijumuisha self.assertRaises(ValueError):
            tarfile.itn(-1, 8, tarfile.USTAR_FORMAT)
        ukijumuisha self.assertRaises(ValueError):
            tarfile.itn(0o10000000, 8, tarfile.USTAR_FORMAT)
        ukijumuisha self.assertRaises(ValueError):
            tarfile.itn(-0x10000000001, 6, tarfile.GNU_FORMAT)
        ukijumuisha self.assertRaises(ValueError):
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
        ukijumuisha tarfile.open(tar_name, 'w') kama tf:
            kila tardata kwenye files:
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
        kila tar_name kwenye testtarnames:
            kila opt kwenye '-t', '--test':
                out = self.tarfilecmd(opt, tar_name)
                self.assertEqual(out, b'')

    eleza test_test_command_verbose(self):
        kila tar_name kwenye testtarnames:
            kila opt kwenye '-v', '--verbose':
                out = self.tarfilecmd(opt, '-t', tar_name)
                self.assertIn(b'is a tar archive.\n', out)

    eleza test_test_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        rc, out, err = self.tarfilecmd_failure('-t', zipname)
        self.assertIn(b' ni sio a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)

        kila tar_name kwenye testtarnames:
            ukijumuisha self.subTest(tar_name=tar_name):
                ukijumuisha open(tar_name, 'rb') kama f:
                    data = f.read()
                jaribu:
                    ukijumuisha open(tmpname, 'wb') kama f:
                        f.write(data[:511])
                    rc, out, err = self.tarfilecmd_failure('-t', tmpname)
                    self.assertEqual(out, b'')
                    self.assertEqual(rc, 1)
                mwishowe:
                    support.unlink(tmpname)

    eleza test_list_command(self):
        kila tar_name kwenye testtarnames:
            ukijumuisha support.captured_stdout() kama t:
                ukijumuisha tarfile.open(tar_name, 'r') kama tf:
                    tf.list(verbose=Uongo)
            expected = t.getvalue().encode('ascii', 'backslashreplace')
            kila opt kwenye '-l', '--list':
                out = self.tarfilecmd(opt, tar_name,
                                      PYTHONIOENCODING='ascii')
                self.assertEqual(out, expected)

    eleza test_list_command_verbose(self):
        kila tar_name kwenye testtarnames:
            ukijumuisha support.captured_stdout() kama t:
                ukijumuisha tarfile.open(tar_name, 'r') kama tf:
                    tf.list(verbose=Kweli)
            expected = t.getvalue().encode('ascii', 'backslashreplace')
            kila opt kwenye '-v', '--verbose':
                out = self.tarfilecmd(opt, '-l', tar_name,
                                      PYTHONIOENCODING='ascii')
                self.assertEqual(out, expected)

    eleza test_list_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        rc, out, err = self.tarfilecmd_failure('-l', zipname)
        self.assertIn(b' ni sio a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)

    eleza test_create_command(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        kila opt kwenye '-c', '--create':
            jaribu:
                out = self.tarfilecmd(opt, tmpname, *files)
                self.assertEqual(out, b'')
                ukijumuisha tarfile.open(tmpname) kama tar:
                    tar.getmembers()
            mwishowe:
                support.unlink(tmpname)

    eleza test_create_command_verbose(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        kila opt kwenye '-v', '--verbose':
            jaribu:
                out = self.tarfilecmd(opt, '-c', tmpname, *files)
                self.assertIn(b' file created.', out)
                ukijumuisha tarfile.open(tmpname) kama tar:
                    tar.getmembers()
            mwishowe:
                support.unlink(tmpname)

    eleza test_create_command_dotless_filename(self):
        files = [support.findfile('tokenize_tests.txt')]
        jaribu:
            out = self.tarfilecmd('-c', dotlessname, *files)
            self.assertEqual(out, b'')
            ukijumuisha tarfile.open(dotlessname) kama tar:
                tar.getmembers()
        mwishowe:
            support.unlink(dotlessname)

    eleza test_create_command_dot_started_filename(self):
        tar_name = os.path.join(TEMPDIR, ".testtar")
        files = [support.findfile('tokenize_tests.txt')]
        jaribu:
            out = self.tarfilecmd('-c', tar_name, *files)
            self.assertEqual(out, b'')
            ukijumuisha tarfile.open(tar_name) kama tar:
                tar.getmembers()
        mwishowe:
            support.unlink(tar_name)

    eleza test_create_command_compressed(self):
        files = [support.findfile('tokenize_tests.txt'),
                 support.findfile('tokenize_tests-no-coding-cookie-'
                                  'and-utf8-bom-sig-only.txt')]
        kila filetype kwenye (GzipTest, Bz2Test, LzmaTest):
            ikiwa sio filetype.open:
                endelea
            jaribu:
                tar_name = tmpname + '.' + filetype.suffix
                out = self.tarfilecmd('-c', tar_name, *files)
                ukijumuisha filetype.taropen(tar_name) kama tar:
                    tar.getmembers()
            mwishowe:
                support.unlink(tar_name)

    eleza test_extract_command(self):
        self.make_simple_tarfile(tmpname)
        kila opt kwenye '-e', '--extract':
            jaribu:
                ukijumuisha support.temp_cwd(tarextdir):
                    out = self.tarfilecmd(opt, tmpname)
                self.assertEqual(out, b'')
            mwishowe:
                support.rmtree(tarextdir)

    eleza test_extract_command_verbose(self):
        self.make_simple_tarfile(tmpname)
        kila opt kwenye '-v', '--verbose':
            jaribu:
                ukijumuisha support.temp_cwd(tarextdir):
                    out = self.tarfilecmd(opt, '-e', tmpname)
                self.assertIn(b' file ni extracted.', out)
            mwishowe:
                support.rmtree(tarextdir)

    eleza test_extract_command_different_directory(self):
        self.make_simple_tarfile(tmpname)
        jaribu:
            ukijumuisha support.temp_cwd(tarextdir):
                out = self.tarfilecmd('-e', tmpname, 'spamdir')
            self.assertEqual(out, b'')
        mwishowe:
            support.rmtree(tarextdir)

    eleza test_extract_command_invalid_file(self):
        zipname = support.findfile('zipdir.zip')
        ukijumuisha support.temp_cwd(tarextdir):
            rc, out, err = self.tarfilecmd_failure('-e', zipname)
        self.assertIn(b' ni sio a tar archive.', err)
        self.assertEqual(out, b'')
        self.assertEqual(rc, 1)


kundi ContextManagerTest(unittest.TestCase):

    eleza test_basic(self):
        ukijumuisha tarfile.open(tarname) kama tar:
            self.assertUongo(tar.closed, "closed inside runtime context")
        self.assertKweli(tar.closed, "context manager failed")

    eleza test_closed(self):
        # The __enter__() method ni supposed to ashiria OSError
        # ikiwa the TarFile object ni already closed.
        tar = tarfile.open(tarname)
        tar.close()
        ukijumuisha self.assertRaises(OSError):
            ukijumuisha tar:
                pita

    eleza test_exception(self):
        # Test ikiwa the OSError exception ni pitaed through properly.
        ukijumuisha self.assertRaises(Exception) kama exc:
            ukijumuisha tarfile.open(tarname) kama tar:
                ashiria OSError
        self.assertIsInstance(exc.exception, OSError,
                              "wrong exception raised kwenye context manager")
        self.assertKweli(tar.closed, "context manager failed")

    eleza test_no_eof(self):
        # __exit__() must sio write end-of-archive blocks ikiwa an
        # exception was raised.
        jaribu:
            ukijumuisha tarfile.open(tmpname, "w") kama tar:
                ashiria Exception
        tatizo:
            pita
        self.assertEqual(os.path.getsize(tmpname), 0,
                "context manager wrote an end-of-archive block")
        self.assertKweli(tar.closed, "context manager failed")

    eleza test_eof(self):
        # __exit__() must write end-of-archive blocks, i.e. call
        # TarFile.close() ikiwa there was no error.
        ukijumuisha tarfile.open(tmpname, "w"):
            pita
        self.assertNotEqual(os.path.getsize(tmpname), 0,
                "context manager wrote no end-of-archive block")

    eleza test_fileobj(self):
        # Test that __exit__() did sio close the external file
        # object.
        ukijumuisha open(tmpname, "wb") kama fobj:
            jaribu:
                ukijumuisha tarfile.open(fileobj=fobj, mode="w") kama tar:
                    ashiria Exception
            tatizo:
                pita
            self.assertUongo(fobj.closed, "external file object was closed")
            self.assertKweli(tar.closed, "context manager failed")


@unittest.skipIf(hasattr(os, "link"), "requires os.link to be missing")
kundi LinkEmulationTest(ReadTest, unittest.TestCase):

    # Test kila issue #8741 regression. On platforms that do sio support
    # symbolic ama hard links tarfile tries to extract these types of members
    # kama the regular files they point to.
    eleza _test_link_extraction(self, name):
        self.tar.extract(name, TEMPDIR)
        ukijumuisha open(os.path.join(TEMPDIR, name), "rb") kama f:
            data = f.read()
        self.assertEqual(sha256sum(data), sha256_regtype)

    # See issues #1578269, #8879, na #17689 kila some history on these skips
    @unittest.skipIf(hasattr(os.path, "islink"),
                     "Skip emulation - has os.path.islink but sio os.link")
    eleza test_hardlink_extraction1(self):
        self._test_link_extraction("ustar/lnktype")

    @unittest.skipIf(hasattr(os.path, "islink"),
                     "Skip emulation - has os.path.islink but sio os.link")
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
    # on an empty ama partial bzipped file.

    eleza _test_partial_input(self, mode):
        kundi MyBytesIO(io.BytesIO):
            hit_eof = Uongo
            eleza read(self, n):
                ikiwa self.hit_eof:
                    ashiria AssertionError("infinite loop detected kwenye "
                                         "tarfile.open()")
                self.hit_eof = self.tell() == len(self.getvalue())
                rudisha super(MyBytesIO, self).read(n)
            eleza seek(self, *args):
                self.hit_eof = Uongo
                rudisha super(MyBytesIO, self).seek(*args)

        data = bz2.compress(tarfile.TarInfo("foo").tobuf())
        kila x kwenye range(len(data) + 1):
            jaribu:
                tarfile.open(fileobj=MyBytesIO(data[:x]), mode=mode)
            tatizo tarfile.ReadError:
                pita # we have no interest kwenye ReadErrors

    eleza test_partialinput(self):
        self._test_partial_input("r")

    eleza test_partial_input_bz2(self):
        self._test_partial_input("r:bz2")


eleza root_is_uid_gid_0():
    jaribu:
        agiza pwd, grp
    tatizo ImportError:
        rudisha Uongo
    ikiwa pwd.getpwuid(0)[0] != 'root':
        rudisha Uongo
    ikiwa grp.getgrgid(0)[0] != 'root':
        rudisha Uongo
    rudisha Kweli


@unittest.skipUnless(hasattr(os, 'chown'), "missing os.chown")
@unittest.skipUnless(hasattr(os, 'geteuid'), "missing os.geteuid")
kundi NumericOwnerTest(unittest.TestCase):
    # mock the following:
    #  os.chown: so we can test what's being called
    #  os.chmod: so the modes are sio actually changed. ikiwa they are, we can't
    #             delete the files/directories
    #  os.geteuid: so we can lie na say we're root (uid = 0)

    @staticmethod
    eleza _make_test_archive(filename_1, dirname_1, filename_2):
        # the file contents to write
        fobj = io.BytesIO(b"content")

        # create a tar file ukijumuisha a file, a directory, na a file within that
        #  directory. Assign various .uid/.gid values to them
        items = [(filename_1, 99, 98, tarfile.REGTYPE, fobj),
                 (dirname_1,  77, 76, tarfile.DIRTYPE, Tupu),
                 (filename_2, 88, 87, tarfile.REGTYPE, fobj),
                 ]
        ukijumuisha tarfile.open(tmpname, 'w') kama tarfl:
            kila name, uid, gid, typ, contents kwenye items:
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
        mock_geteuid.return_value = 0  # lie na say we're root
        fname = 'numeric-owner-testfile'
        dirname = 'dir'

        # the names we want stored kwenye the tarfile
        filename_1 = fname
        dirname_1 = dirname
        filename_2 = os.path.join(dirname, fname)

        # create the tarfile ukijumuisha the contents we're after
        tar_filename = NumericOwnerTest._make_test_archive(filename_1,
                                                           dirname_1,
                                                           filename_2)

        # open the tarfile kila reading. tuma it na the names of the items
        #  we stored into the file
        ukijumuisha tarfile.open(tar_filename) kama tarfl:
            tuma tarfl, filename_1, dirname_1, filename_2

    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    eleza test_extract_with_numeric_owner(self, mock_geteuid, mock_chmod,
                                        mock_chown):
        ukijumuisha self._setup_test(mock_geteuid) kama (tarfl, filename_1, _,
                                                filename_2):
            tarfl.extract(filename_1, TEMPDIR, numeric_owner=Kweli)
            tarfl.extract(filename_2 , TEMPDIR, numeric_owner=Kweli)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)
        f_filename_2 = os.path.join(TEMPDIR, filename_2)

        mock_chown.assert_has_calls([unittest.mock.call(f_filename_1, 99, 98),
                                     unittest.mock.call(f_filename_2, 88, 87),
                                     ],
                                    any_order=Kweli)

    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    eleza test_extractall_with_numeric_owner(self, mock_geteuid, mock_chmod,
                                           mock_chown):
        ukijumuisha self._setup_test(mock_geteuid) kama (tarfl, filename_1, dirname_1,
                                                filename_2):
            tarfl.extractall(TEMPDIR, numeric_owner=Kweli)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)
        f_dirname_1  = os.path.join(TEMPDIR, dirname_1)
        f_filename_2 = os.path.join(TEMPDIR, filename_2)

        mock_chown.assert_has_calls([unittest.mock.call(f_filename_1, 99, 98),
                                     unittest.mock.call(f_dirname_1, 77, 76),
                                     unittest.mock.call(f_filename_2, 88, 87),
                                     ],
                                    any_order=Kweli)

    # this test requires that uid=0 na gid=0 really be named 'root'. that's
    #  because the uname na gname kwenye the test file are 'root', na extract()
    #  will look them up using pwd na grp to find their uid na gid, which we
    #  test here to be 0.
    @unittest.skipUnless(root_is_uid_gid_0(),
                         'uid=0,gid=0 must be named "root"')
    @unittest.mock.patch('os.chown')
    @unittest.mock.patch('os.chmod')
    @unittest.mock.patch('os.geteuid')
    eleza test_extract_without_numeric_owner(self, mock_geteuid, mock_chmod,
                                           mock_chown):
        ukijumuisha self._setup_test(mock_geteuid) kama (tarfl, filename_1, _, _):
            tarfl.extract(filename_1, TEMPDIR, numeric_owner=Uongo)

        # convert to filesystem paths
        f_filename_1 = os.path.join(TEMPDIR, filename_1)

        mock_chown.assert_called_with(f_filename_1, 0, 0)

    @unittest.mock.patch('os.geteuid')
    eleza test_keyword_only(self, mock_geteuid):
        ukijumuisha self._setup_test(mock_geteuid) kama (tarfl, filename_1, _, _):
            self.assertRaises(TypeError,
                              tarfl.extract, filename_1, TEMPDIR, Uongo, Kweli)


eleza setUpModule():
    support.unlink(TEMPDIR)
    os.makedirs(TEMPDIR)

    global testtarnames
    testtarnames = [tarname]
    ukijumuisha open(tarname, "rb") kama fobj:
        data = fobj.read()

    # Create compressed tarfiles.
    kila c kwenye GzipTest, Bz2Test, LzmaTest:
        ikiwa c.open:
            support.unlink(c.tarname)
            testtarnames.append(c.tarname)
            ukijumuisha c.open(c.tarname, "wb") kama tar:
                tar.write(data)

eleza tearDownModule():
    ikiwa os.path.exists(TEMPDIR):
        support.rmtree(TEMPDIR)

ikiwa __name__ == "__main__":
    unittest.main()
