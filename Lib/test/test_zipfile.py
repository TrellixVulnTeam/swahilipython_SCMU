agiza contextlib
agiza importlib.util
agiza io
agiza os
agiza pathlib
agiza posixpath
agiza struct
agiza subprocess
agiza sys
agiza time
agiza unittest
agiza unittest.mock kama mock
agiza zipfile


kutoka tempfile agiza TemporaryFile
kutoka random agiza randint, random, getrandbits

kutoka test.support agiza script_helper
kutoka test.support agiza (TESTFN, findfile, unlink, rmtree, temp_dir, temp_cwd,
                          requires_zlib, requires_bz2, requires_lzma,
                          captured_stdout)

TESTFN2 = TESTFN + "2"
TESTFNDIR = TESTFN + "d"
FIXEDTEST_SIZE = 1000
DATAFILES_DIR = 'zipfile_datafiles'

SMALL_TEST_DATA = [('_ziptest1', '1q2w3e4r5t'),
                   ('ziptest2dir/_ziptest2', 'qawsedrftg'),
                   ('ziptest2dir/ziptest3dir/_ziptest3', 'azsxdcfvgb'),
                   ('ziptest2dir/ziptest3dir/ziptest4dir/_ziptest3', '6y7u8i9o0p')]

eleza getrandbytes(size):
    rudisha getrandbits(8 * size).to_bytes(size, 'little')

eleza get_files(test):
    tuma TESTFN2
    ukijumuisha TemporaryFile() kama f:
        tuma f
        test.assertUongo(f.closed)
    ukijumuisha io.BytesIO() kama f:
        tuma f
        test.assertUongo(f.closed)

kundi AbstractTestsWithSourceFile:
    @classmethod
    eleza setUpClass(cls):
        cls.line_gen = [bytes("Zipfile test line %d. random float: %f\n" %
                              (i, random()), "ascii")
                        kila i kwenye range(FIXEDTEST_SIZE)]
        cls.data = b''.join(cls.line_gen)

    eleza setUp(self):
        # Make a source file ukijumuisha some lines
        ukijumuisha open(TESTFN, "wb") kama fp:
            fp.write(self.data)

    eleza make_test_archive(self, f, compression, compresslevel=Tupu):
        kwargs = {'compression': compression, 'compresslevel': compresslevel}
        # Create the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "w", **kwargs) kama zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)
            zipfp.writestr("strfile", self.data)
            ukijumuisha zipfp.open('written-open-w', mode='w') kama f:
                kila line kwenye self.line_gen:
                    f.write(line)

    eleza zip_test(self, f, compression, compresslevel=Tupu):
        self.make_test_archive(f, compression, compresslevel)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r", compression) kama zipfp:
            self.assertEqual(zipfp.read(TESTFN), self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)
            self.assertEqual(zipfp.read("strfile"), self.data)

            # Print the ZIP directory
            fp = io.StringIO()
            zipfp.printdir(file=fp)
            directory = fp.getvalue()
            lines = directory.splitlines()
            self.assertEqual(len(lines), 5) # Number of files + header

            self.assertIn('File Name', lines[0])
            self.assertIn('Modified', lines[0])
            self.assertIn('Size', lines[0])

            fn, date, time_, size = lines[1].split()
            self.assertEqual(fn, 'another.name')
            self.assertKweli(time.strptime(date, '%Y-%m-%d'))
            self.assertKweli(time.strptime(time_, '%H:%M:%S'))
            self.assertEqual(size, str(len(self.data)))

            # Check the namelist
            names = zipfp.namelist()
            self.assertEqual(len(names), 4)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)
            self.assertIn("written-open-w", names)

            # Check infolist
            infos = zipfp.infolist()
            names = [i.filename kila i kwenye infos]
            self.assertEqual(len(names), 4)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)
            self.assertIn("written-open-w", names)
            kila i kwenye infos:
                self.assertEqual(i.file_size, len(self.data))

            # check getinfo
            kila nm kwenye (TESTFN, "another.name", "strfile", "written-open-w"):
                info = zipfp.getinfo(nm)
                self.assertEqual(info.filename, nm)
                self.assertEqual(info.file_size, len(self.data))

            # Check that testzip doesn't ashiria an exception
            zipfp.testzip()

    eleza test_basic(self):
        kila f kwenye get_files(self):
            self.zip_test(f, self.compression)

    eleza zip_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r", compression) kama zipfp:
            zipdata1 = []
            ukijumuisha zipfp.open(TESTFN) kama zipopen1:
                wakati Kweli:
                    read_data = zipopen1.read(256)
                    ikiwa sio read_data:
                        koma
                    zipdata1.append(read_data)

            zipdata2 = []
            ukijumuisha zipfp.open("another.name") kama zipopen2:
                wakati Kweli:
                    read_data = zipopen2.read(256)
                    ikiwa sio read_data:
                        koma
                    zipdata2.append(read_data)

            self.assertEqual(b''.join(zipdata1), self.data)
            self.assertEqual(b''.join(zipdata2), self.data)

    eleza test_open(self):
        kila f kwenye get_files(self):
            self.zip_open_test(f, self.compression)

    eleza test_open_with_pathlike(self):
        path = pathlib.Path(TESTFN2)
        self.zip_open_test(path, self.compression)
        ukijumuisha zipfile.ZipFile(path, "r", self.compression) kama zipfp:
            self.assertIsInstance(zipfp.filename, str)

    eleza zip_random_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r", compression) kama zipfp:
            zipdata1 = []
            ukijumuisha zipfp.open(TESTFN) kama zipopen1:
                wakati Kweli:
                    read_data = zipopen1.read(randint(1, 1024))
                    ikiwa sio read_data:
                        koma
                    zipdata1.append(read_data)

            self.assertEqual(b''.join(zipdata1), self.data)

    eleza test_random_open(self):
        kila f kwenye get_files(self):
            self.zip_random_open_test(f, self.compression)

    eleza zip_read1_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r") kama zipfp, \
             zipfp.open(TESTFN) kama zipopen:
            zipdata = []
            wakati Kweli:
                read_data = zipopen.read1(-1)
                ikiwa sio read_data:
                    koma
                zipdata.append(read_data)

        self.assertEqual(b''.join(zipdata), self.data)

    eleza test_read1(self):
        kila f kwenye get_files(self):
            self.zip_read1_test(f, self.compression)

    eleza zip_read1_10_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r") kama zipfp, \
             zipfp.open(TESTFN) kama zipopen:
            zipdata = []
            wakati Kweli:
                read_data = zipopen.read1(10)
                self.assertLessEqual(len(read_data), 10)
                ikiwa sio read_data:
                    koma
                zipdata.append(read_data)

        self.assertEqual(b''.join(zipdata), self.data)

    eleza test_read1_10(self):
        kila f kwenye get_files(self):
            self.zip_read1_10_test(f, self.compression)

    eleza zip_readline_read_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r") kama zipfp, \
             zipfp.open(TESTFN) kama zipopen:
            data = b''
            wakati Kweli:
                read = zipopen.readline()
                ikiwa sio read:
                    koma
                data += read

                read = zipopen.read(100)
                ikiwa sio read:
                    koma
                data += read

        self.assertEqual(data, self.data)

    eleza test_readline_read(self):
        # Issue #7610: calls to readline() interleaved ukijumuisha calls to read().
        kila f kwenye get_files(self):
            self.zip_readline_read_test(f, self.compression)

    eleza zip_readline_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r") kama zipfp:
            ukijumuisha zipfp.open(TESTFN) kama zipopen:
                kila line kwenye self.line_gen:
                    linedata = zipopen.readline()
                    self.assertEqual(linedata, line)

    eleza test_readline(self):
        kila f kwenye get_files(self):
            self.zip_readline_test(f, self.compression)

    eleza zip_readlines_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r") kama zipfp:
            ukijumuisha zipfp.open(TESTFN) kama zipopen:
                ziplines = zipopen.readlines()
            kila line, zipline kwenye zip(self.line_gen, ziplines):
                self.assertEqual(zipline, line)

    eleza test_readlines(self):
        kila f kwenye get_files(self):
            self.zip_readlines_test(f, self.compression)

    eleza zip_iterlines_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r") kama zipfp:
            ukijumuisha zipfp.open(TESTFN) kama zipopen:
                kila line, zipline kwenye zip(self.line_gen, zipopen):
                    self.assertEqual(zipline, line)

    eleza test_iterlines(self):
        kila f kwenye get_files(self):
            self.zip_iterlines_test(f, self.compression)

    eleza test_low_compression(self):
        """Check kila cases where compressed data ni larger than original."""
        # Create the ZIP archive
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", self.compression) kama zipfp:
            zipfp.writestr("strfile", '12')

        # Get an open object kila strfile
        ukijumuisha zipfile.ZipFile(TESTFN2, "r", self.compression) kama zipfp:
            ukijumuisha zipfp.open("strfile") kama openobj:
                self.assertEqual(openobj.read(1), b'1')
                self.assertEqual(openobj.read(1), b'2')

    eleza test_writestr_compression(self):
        zipfp = zipfile.ZipFile(TESTFN2, "w")
        zipfp.writestr("b.txt", "hello world", compress_type=self.compression)
        info = zipfp.getinfo('b.txt')
        self.assertEqual(info.compress_type, self.compression)

    eleza test_writestr_compresslevel(self):
        zipfp = zipfile.ZipFile(TESTFN2, "w", compresslevel=1)
        zipfp.writestr("a.txt", "hello world", compress_type=self.compression)
        zipfp.writestr("b.txt", "hello world", compress_type=self.compression,
                       compresslevel=2)

        # Compression level follows the constructor.
        a_info = zipfp.getinfo('a.txt')
        self.assertEqual(a_info.compress_type, self.compression)
        self.assertEqual(a_info._compresslevel, 1)

        # Compression level ni overridden.
        b_info = zipfp.getinfo('b.txt')
        self.assertEqual(b_info.compress_type, self.compression)
        self.assertEqual(b_info._compresslevel, 2)

    eleza test_read_rudisha_size(self):
        # Issue #9837: ZipExtFile.read() shouldn't rudisha more bytes
        # than requested.
        kila test_size kwenye (1, 4095, 4096, 4097, 16384):
            file_size = test_size + 1
            junk = getrandbytes(file_size)
            ukijumuisha zipfile.ZipFile(io.BytesIO(), "w", self.compression) kama zipf:
                zipf.writestr('foo', junk)
                ukijumuisha zipf.open('foo', 'r') kama fp:
                    buf = fp.read(test_size)
                    self.assertEqual(len(buf), test_size)

    eleza test_truncated_zipfile(self):
        fp = io.BytesIO()
        ukijumuisha zipfile.ZipFile(fp, mode='w') kama zipf:
            zipf.writestr('strfile', self.data, compress_type=self.compression)
            end_offset = fp.tell()
        zipfiledata = fp.getvalue()

        fp = io.BytesIO(zipfiledata)
        ukijumuisha zipfile.ZipFile(fp) kama zipf:
            ukijumuisha zipf.open('strfile') kama zipopen:
                fp.truncate(end_offset - 20)
                ukijumuisha self.assertRaises(EOFError):
                    zipopen.read()

        fp = io.BytesIO(zipfiledata)
        ukijumuisha zipfile.ZipFile(fp) kama zipf:
            ukijumuisha zipf.open('strfile') kama zipopen:
                fp.truncate(end_offset - 20)
                ukijumuisha self.assertRaises(EOFError):
                    wakati zipopen.read(100):
                        pita

        fp = io.BytesIO(zipfiledata)
        ukijumuisha zipfile.ZipFile(fp) kama zipf:
            ukijumuisha zipf.open('strfile') kama zipopen:
                fp.truncate(end_offset - 20)
                ukijumuisha self.assertRaises(EOFError):
                    wakati zipopen.read1(100):
                        pita

    eleza test_repr(self):
        fname = 'file.name'
        kila f kwenye get_files(self):
            ukijumuisha zipfile.ZipFile(f, 'w', self.compression) kama zipfp:
                zipfp.write(TESTFN, fname)
                r = repr(zipfp)
                self.assertIn("mode='w'", r)

            ukijumuisha zipfile.ZipFile(f, 'r') kama zipfp:
                r = repr(zipfp)
                ikiwa isinstance(f, str):
                    self.assertIn('filename=%r' % f, r)
                isipokua:
                    self.assertIn('file=%r' % f, r)
                self.assertIn("mode='r'", r)
                r = repr(zipfp.getinfo(fname))
                self.assertIn('filename=%r' % fname, r)
                self.assertIn('filemode=', r)
                self.assertIn('file_size=', r)
                ikiwa self.compression != zipfile.ZIP_STORED:
                    self.assertIn('compress_type=', r)
                    self.assertIn('compress_size=', r)
                ukijumuisha zipfp.open(fname) kama zipopen:
                    r = repr(zipopen)
                    self.assertIn('name=%r' % fname, r)
                    self.assertIn("mode='r'", r)
                    ikiwa self.compression != zipfile.ZIP_STORED:
                        self.assertIn('compress_type=', r)
                self.assertIn('[closed]', repr(zipopen))
            self.assertIn('[closed]', repr(zipfp))

    eleza test_compresslevel_basic(self):
        kila f kwenye get_files(self):
            self.zip_test(f, self.compression, compresslevel=9)

    eleza test_per_file_compresslevel(self):
        """Check that files within a Zip archive can have different
        compression levels."""
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", compresslevel=1) kama zipfp:
            zipfp.write(TESTFN, 'compress_1')
            zipfp.write(TESTFN, 'compress_9', compresslevel=9)
            one_info = zipfp.getinfo('compress_1')
            nine_info = zipfp.getinfo('compress_9')
            self.assertEqual(one_info._compresslevel, 1)
            self.assertEqual(nine_info._compresslevel, 9)

    eleza test_writing_errors(self):
        kundi BrokenFile(io.BytesIO):
            eleza write(self, data):
                nonlocal count
                ikiwa count ni sio Tupu:
                    ikiwa count == stop:
                        ashiria OSError
                    count += 1
                super().write(data)

        stop = 0
        wakati Kweli:
            testfile = BrokenFile()
            count = Tupu
            ukijumuisha zipfile.ZipFile(testfile, 'w', self.compression) kama zipfp:
                ukijumuisha zipfp.open('file1', 'w') kama f:
                    f.write(b'data1')
                count = 0
                jaribu:
                    ukijumuisha zipfp.open('file2', 'w') kama f:
                        f.write(b'data2')
                tatizo OSError:
                    stop += 1
                isipokua:
                    koma
                mwishowe:
                    count = Tupu
            ukijumuisha zipfile.ZipFile(io.BytesIO(testfile.getvalue())) kama zipfp:
                self.assertEqual(zipfp.namelist(), ['file1'])
                self.assertEqual(zipfp.read('file1'), b'data1')

        ukijumuisha zipfile.ZipFile(io.BytesIO(testfile.getvalue())) kama zipfp:
            self.assertEqual(zipfp.namelist(), ['file1', 'file2'])
            self.assertEqual(zipfp.read('file1'), b'data1')
            self.assertEqual(zipfp.read('file2'), b'data2')


    eleza tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)


kundi StoredTestsWithSourceFile(AbstractTestsWithSourceFile,
                                unittest.TestCase):
    compression = zipfile.ZIP_STORED
    test_low_compression = Tupu

    eleza zip_test_writestr_permissions(self, f, compression):
        # Make sure that writestr na open(... mode='w') create files with
        # mode 0600, when they are pitaed a name rather than a ZipInfo
        # instance.

        self.make_test_archive(f, compression)
        ukijumuisha zipfile.ZipFile(f, "r") kama zipfp:
            zinfo = zipfp.getinfo('strfile')
            self.assertEqual(zinfo.external_attr, 0o600 << 16)

            zinfo2 = zipfp.getinfo('written-open-w')
            self.assertEqual(zinfo2.external_attr, 0o600 << 16)

    eleza test_writestr_permissions(self):
        kila f kwenye get_files(self):
            self.zip_test_writestr_permissions(f, zipfile.ZIP_STORED)

    eleza test_absolute_arcnames(self):
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) kama zipfp:
            zipfp.write(TESTFN, "/absolute")

        ukijumuisha zipfile.ZipFile(TESTFN2, "r", zipfile.ZIP_STORED) kama zipfp:
            self.assertEqual(zipfp.namelist(), ["absolute"])

    eleza test_append_to_zip_file(self):
        """Test appending to an existing zipfile."""
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) kama zipfp:
            zipfp.write(TESTFN, TESTFN)

        ukijumuisha zipfile.ZipFile(TESTFN2, "a", zipfile.ZIP_STORED) kama zipfp:
            zipfp.writestr("strfile", self.data)
            self.assertEqual(zipfp.namelist(), [TESTFN, "strfile"])

    eleza test_append_to_non_zip_file(self):
        """Test appending to an existing file that ni sio a zipfile."""
        # NOTE: this test fails ikiwa len(d) < 22 because of the first
        # line "fpin.seek(-22, 2)" kwenye _EndRecData
        data = b'I am sio a ZipFile!'*10
        ukijumuisha open(TESTFN2, 'wb') kama f:
            f.write(data)

        ukijumuisha zipfile.ZipFile(TESTFN2, "a", zipfile.ZIP_STORED) kama zipfp:
            zipfp.write(TESTFN, TESTFN)

        ukijumuisha open(TESTFN2, 'rb') kama f:
            f.seek(len(data))
            ukijumuisha zipfile.ZipFile(f, "r") kama zipfp:
                self.assertEqual(zipfp.namelist(), [TESTFN])
                self.assertEqual(zipfp.read(TESTFN), self.data)
        ukijumuisha open(TESTFN2, 'rb') kama f:
            self.assertEqual(f.read(len(data)), data)
            zipfiledata = f.read()
        ukijumuisha io.BytesIO(zipfiledata) kama bio, zipfile.ZipFile(bio) kama zipfp:
            self.assertEqual(zipfp.namelist(), [TESTFN])
            self.assertEqual(zipfp.read(TESTFN), self.data)

    eleza test_read_concatenated_zip_file(self):
        ukijumuisha io.BytesIO() kama bio:
            ukijumuisha zipfile.ZipFile(bio, 'w', zipfile.ZIP_STORED) kama zipfp:
                zipfp.write(TESTFN, TESTFN)
            zipfiledata = bio.getvalue()
        data = b'I am sio a ZipFile!'*10
        ukijumuisha open(TESTFN2, 'wb') kama f:
            f.write(data)
            f.write(zipfiledata)

        ukijumuisha zipfile.ZipFile(TESTFN2) kama zipfp:
            self.assertEqual(zipfp.namelist(), [TESTFN])
            self.assertEqual(zipfp.read(TESTFN), self.data)

    eleza test_append_to_concatenated_zip_file(self):
        ukijumuisha io.BytesIO() kama bio:
            ukijumuisha zipfile.ZipFile(bio, 'w', zipfile.ZIP_STORED) kama zipfp:
                zipfp.write(TESTFN, TESTFN)
            zipfiledata = bio.getvalue()
        data = b'I am sio a ZipFile!'*1000000
        ukijumuisha open(TESTFN2, 'wb') kama f:
            f.write(data)
            f.write(zipfiledata)

        ukijumuisha zipfile.ZipFile(TESTFN2, 'a') kama zipfp:
            self.assertEqual(zipfp.namelist(), [TESTFN])
            zipfp.writestr('strfile', self.data)

        ukijumuisha open(TESTFN2, 'rb') kama f:
            self.assertEqual(f.read(len(data)), data)
            zipfiledata = f.read()
        ukijumuisha io.BytesIO(zipfiledata) kama bio, zipfile.ZipFile(bio) kama zipfp:
            self.assertEqual(zipfp.namelist(), [TESTFN, 'strfile'])
            self.assertEqual(zipfp.read(TESTFN), self.data)
            self.assertEqual(zipfp.read('strfile'), self.data)

    eleza test_ignores_newline_at_end(self):
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) kama zipfp:
            zipfp.write(TESTFN, TESTFN)
        ukijumuisha open(TESTFN2, 'a') kama f:
            f.write("\r\n\00\00\00")
        ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
            self.assertIsInstance(zipfp, zipfile.ZipFile)

    eleza test_ignores_stuff_appended_past_comments(self):
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) kama zipfp:
            zipfp.comment = b"this ni a comment"
            zipfp.write(TESTFN, TESTFN)
        ukijumuisha open(TESTFN2, 'a') kama f:
            f.write("abcdef\r\n")
        ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
            self.assertIsInstance(zipfp, zipfile.ZipFile)
            self.assertEqual(zipfp.comment, b"this ni a comment")

    eleza test_write_default_name(self):
        """Check that calling ZipFile.write without arcname specified
        produces the expected result."""
        ukijumuisha zipfile.ZipFile(TESTFN2, "w") kama zipfp:
            zipfp.write(TESTFN)
            ukijumuisha open(TESTFN, "rb") kama f:
                self.assertEqual(zipfp.read(TESTFN), f.read())

    eleza test_write_to_readonly(self):
        """Check that trying to call write() on a readonly ZipFile object
        ashirias a ValueError."""
        ukijumuisha zipfile.ZipFile(TESTFN2, mode="w") kama zipfp:
            zipfp.writestr("somefile.txt", "bogus")

        ukijumuisha zipfile.ZipFile(TESTFN2, mode="r") kama zipfp:
            self.assertRaises(ValueError, zipfp.write, TESTFN)

        ukijumuisha zipfile.ZipFile(TESTFN2, mode="r") kama zipfp:
            ukijumuisha self.assertRaises(ValueError):
                zipfp.open(TESTFN, mode='w')

    eleza test_add_file_before_1980(self):
        # Set atime na mtime to 1970-01-01
        os.utime(TESTFN, (0, 0))
        ukijumuisha zipfile.ZipFile(TESTFN2, "w") kama zipfp:
            self.assertRaises(ValueError, zipfp.write, TESTFN)

        ukijumuisha zipfile.ZipFile(TESTFN2, "w", strict_timestamps=Uongo) kama zipfp:
            zipfp.write(TESTFN)
            zinfo = zipfp.getinfo(TESTFN)
            self.assertEqual(zinfo.date_time, (1980, 1, 1, 0, 0, 0))

    eleza test_add_file_after_2107(self):
        # Set atime na mtime to 2108-12-30
        jaribu:
            os.utime(TESTFN, (4386268800, 4386268800))
        tatizo OverflowError:
            self.skipTest('Host fs cannot set timestamp to required value.')

        ukijumuisha zipfile.ZipFile(TESTFN2, "w") kama zipfp:
            self.assertRaises(struct.error, zipfp.write, TESTFN)

        ukijumuisha zipfile.ZipFile(TESTFN2, "w", strict_timestamps=Uongo) kama zipfp:
            zipfp.write(TESTFN)
            zinfo = zipfp.getinfo(TESTFN)
            self.assertEqual(zinfo.date_time, (2107, 12, 31, 23, 59, 59))


@requires_zlib
kundi DeflateTestsWithSourceFile(AbstractTestsWithSourceFile,
                                 unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED

    eleza test_per_file_compression(self):
        """Check that files within a Zip archive can have different
        compression options."""
        ukijumuisha zipfile.ZipFile(TESTFN2, "w") kama zipfp:
            zipfp.write(TESTFN, 'storeme', zipfile.ZIP_STORED)
            zipfp.write(TESTFN, 'deflateme', zipfile.ZIP_DEFLATED)
            sinfo = zipfp.getinfo('storeme')
            dinfo = zipfp.getinfo('deflateme')
            self.assertEqual(sinfo.compress_type, zipfile.ZIP_STORED)
            self.assertEqual(dinfo.compress_type, zipfile.ZIP_DEFLATED)

@requires_bz2
kundi Bzip2TestsWithSourceFile(AbstractTestsWithSourceFile,
                               unittest.TestCase):
    compression = zipfile.ZIP_BZIP2

@requires_lzma
kundi LzmaTestsWithSourceFile(AbstractTestsWithSourceFile,
                              unittest.TestCase):
    compression = zipfile.ZIP_LZMA


kundi AbstractTestZip64InSmallFiles:
    # These tests test the ZIP64 functionality without using large files,
    # see test_zipfile64 kila proper tests.

    @classmethod
    eleza setUpClass(cls):
        line_gen = (bytes("Test of zipfile line %d." % i, "ascii")
                    kila i kwenye range(0, FIXEDTEST_SIZE))
        cls.data = b'\n'.join(line_gen)

    eleza setUp(self):
        self._limit = zipfile.ZIP64_LIMIT
        self._filecount_limit = zipfile.ZIP_FILECOUNT_LIMIT
        zipfile.ZIP64_LIMIT = 1000
        zipfile.ZIP_FILECOUNT_LIMIT = 9

        # Make a source file ukijumuisha some lines
        ukijumuisha open(TESTFN, "wb") kama fp:
            fp.write(self.data)

    eleza zip_test(self, f, compression):
        # Create the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "w", compression, allowZip64=Kweli) kama zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)
            zipfp.writestr("strfile", self.data)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r", compression) kama zipfp:
            self.assertEqual(zipfp.read(TESTFN), self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)
            self.assertEqual(zipfp.read("strfile"), self.data)

            # Print the ZIP directory
            fp = io.StringIO()
            zipfp.printdir(fp)

            directory = fp.getvalue()
            lines = directory.splitlines()
            self.assertEqual(len(lines), 4) # Number of files + header

            self.assertIn('File Name', lines[0])
            self.assertIn('Modified', lines[0])
            self.assertIn('Size', lines[0])

            fn, date, time_, size = lines[1].split()
            self.assertEqual(fn, 'another.name')
            self.assertKweli(time.strptime(date, '%Y-%m-%d'))
            self.assertKweli(time.strptime(time_, '%H:%M:%S'))
            self.assertEqual(size, str(len(self.data)))

            # Check the namelist
            names = zipfp.namelist()
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)

            # Check infolist
            infos = zipfp.infolist()
            names = [i.filename kila i kwenye infos]
            self.assertEqual(len(names), 3)
            self.assertIn(TESTFN, names)
            self.assertIn("another.name", names)
            self.assertIn("strfile", names)
            kila i kwenye infos:
                self.assertEqual(i.file_size, len(self.data))

            # check getinfo
            kila nm kwenye (TESTFN, "another.name", "strfile"):
                info = zipfp.getinfo(nm)
                self.assertEqual(info.filename, nm)
                self.assertEqual(info.file_size, len(self.data))

            # Check that testzip doesn't ashiria an exception
            zipfp.testzip()

    eleza test_basic(self):
        kila f kwenye get_files(self):
            self.zip_test(f, self.compression)

    eleza test_too_many_files(self):
        # This test checks that more than 64k files can be added to an archive,
        # na that the resulting archive can be read properly by ZipFile
        zipf = zipfile.ZipFile(TESTFN, "w", self.compression,
                               allowZip64=Kweli)
        zipf.debug = 100
        numfiles = 15
        kila i kwenye range(numfiles):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf2 = zipfile.ZipFile(TESTFN, "r", self.compression)
        self.assertEqual(len(zipf2.namelist()), numfiles)
        kila i kwenye range(numfiles):
            content = zipf2.read("foo%08d" % i).decode('ascii')
            self.assertEqual(content, "%d" % (i**3 % 57))
        zipf2.close()

    eleza test_too_many_files_append(self):
        zipf = zipfile.ZipFile(TESTFN, "w", self.compression,
                               allowZip64=Uongo)
        zipf.debug = 100
        numfiles = 9
        kila i kwenye range(numfiles):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles)
        ukijumuisha self.assertRaises(zipfile.LargeZipFile):
            zipf.writestr("foo%08d" % numfiles, b'')
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf = zipfile.ZipFile(TESTFN, "a", self.compression,
                               allowZip64=Uongo)
        zipf.debug = 100
        self.assertEqual(len(zipf.namelist()), numfiles)
        ukijumuisha self.assertRaises(zipfile.LargeZipFile):
            zipf.writestr("foo%08d" % numfiles, b'')
        self.assertEqual(len(zipf.namelist()), numfiles)
        zipf.close()

        zipf = zipfile.ZipFile(TESTFN, "a", self.compression,
                               allowZip64=Kweli)
        zipf.debug = 100
        self.assertEqual(len(zipf.namelist()), numfiles)
        numfiles2 = 15
        kila i kwenye range(numfiles, numfiles2):
            zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
        self.assertEqual(len(zipf.namelist()), numfiles2)
        zipf.close()

        zipf2 = zipfile.ZipFile(TESTFN, "r", self.compression)
        self.assertEqual(len(zipf2.namelist()), numfiles2)
        kila i kwenye range(numfiles2):
            content = zipf2.read("foo%08d" % i).decode('ascii')
            self.assertEqual(content, "%d" % (i**3 % 57))
        zipf2.close()

    eleza tearDown(self):
        zipfile.ZIP64_LIMIT = self._limit
        zipfile.ZIP_FILECOUNT_LIMIT = self._filecount_limit
        unlink(TESTFN)
        unlink(TESTFN2)


kundi StoredTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                  unittest.TestCase):
    compression = zipfile.ZIP_STORED

    eleza large_file_exception_test(self, f, compression):
        ukijumuisha zipfile.ZipFile(f, "w", compression, allowZip64=Uongo) kama zipfp:
            self.assertRaises(zipfile.LargeZipFile,
                              zipfp.write, TESTFN, "another.name")

    eleza large_file_exception_test2(self, f, compression):
        ukijumuisha zipfile.ZipFile(f, "w", compression, allowZip64=Uongo) kama zipfp:
            self.assertRaises(zipfile.LargeZipFile,
                              zipfp.writestr, "another.name", self.data)

    eleza test_large_file_exception(self):
        kila f kwenye get_files(self):
            self.large_file_exception_test(f, zipfile.ZIP_STORED)
            self.large_file_exception_test2(f, zipfile.ZIP_STORED)

    eleza test_absolute_arcnames(self):
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED,
                             allowZip64=Kweli) kama zipfp:
            zipfp.write(TESTFN, "/absolute")

        ukijumuisha zipfile.ZipFile(TESTFN2, "r", zipfile.ZIP_STORED) kama zipfp:
            self.assertEqual(zipfp.namelist(), ["absolute"])

    eleza test_append(self):
        # Test that appending to the Zip64 archive doesn't change
        # extra fields of existing entries.
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", allowZip64=Kweli) kama zipfp:
            zipfp.writestr("strfile", self.data)
        ukijumuisha zipfile.ZipFile(TESTFN2, "r", allowZip64=Kweli) kama zipfp:
            zinfo = zipfp.getinfo("strfile")
            extra = zinfo.extra
        ukijumuisha zipfile.ZipFile(TESTFN2, "a", allowZip64=Kweli) kama zipfp:
            zipfp.writestr("strfile2", self.data)
        ukijumuisha zipfile.ZipFile(TESTFN2, "r", allowZip64=Kweli) kama zipfp:
            zinfo = zipfp.getinfo("strfile")
            self.assertEqual(zinfo.extra, extra)

@requires_zlib
kundi DeflateTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                   unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED

@requires_bz2
kundi Bzip2TestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                 unittest.TestCase):
    compression = zipfile.ZIP_BZIP2

@requires_lzma
kundi LzmaTestZip64InSmallFiles(AbstractTestZip64InSmallFiles,
                                unittest.TestCase):
    compression = zipfile.ZIP_LZMA


kundi AbstractWriterTests:

    eleza tearDown(self):
        unlink(TESTFN2)

    eleza test_close_after_close(self):
        data = b'content'
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", self.compression) kama zipf:
            w = zipf.open('test', 'w')
            w.write(data)
            w.close()
            self.assertKweli(w.closed)
            w.close()
            self.assertKweli(w.closed)
            self.assertEqual(zipf.read('test'), data)

    eleza test_write_after_close(self):
        data = b'content'
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", self.compression) kama zipf:
            w = zipf.open('test', 'w')
            w.write(data)
            w.close()
            self.assertKweli(w.closed)
            self.assertRaises(ValueError, w.write, b'')
            self.assertEqual(zipf.read('test'), data)

kundi StoredWriterTests(AbstractWriterTests, unittest.TestCase):
    compression = zipfile.ZIP_STORED

@requires_zlib
kundi DeflateWriterTests(AbstractWriterTests, unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED

@requires_bz2
kundi Bzip2WriterTests(AbstractWriterTests, unittest.TestCase):
    compression = zipfile.ZIP_BZIP2

@requires_lzma
kundi LzmaWriterTests(AbstractWriterTests, unittest.TestCase):
    compression = zipfile.ZIP_LZMA


kundi PyZipFileTests(unittest.TestCase):
    eleza assertCompiledIn(self, name, namelist):
        ikiwa name + 'o' haiko kwenye namelist:
            self.assertIn(name + 'c', namelist)

    eleza requiresWriteAccess(self, path):
        # effective_ids unavailable on windows
        ikiwa sio os.access(path, os.W_OK,
                         effective_ids=os.access kwenye os.supports_effective_ids):
            self.skipTest('requires write access to the installed location')
        filename = os.path.join(path, 'test_zipfile.try')
        jaribu:
            fd = os.open(filename, os.O_WRONLY | os.O_CREAT)
            os.close(fd)
        tatizo Exception:
            self.skipTest('requires write access to the installed location')
        unlink(filename)

    eleza test_write_pyfile(self):
        self.requiresWriteAccess(os.path.dirname(__file__))
        ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:
            fn = __file__
            ikiwa fn.endswith('.pyc'):
                path_split = fn.split(os.sep)
                ikiwa os.altsep ni sio Tupu:
                    path_split.extend(fn.split(os.altsep))
                ikiwa '__pycache__' kwenye path_split:
                    fn = importlib.util.source_from_cache(fn)
                isipokua:
                    fn = fn[:-1]

            zipfp.writepy(fn)

            bn = os.path.basename(fn)
            self.assertNotIn(bn, zipfp.namelist())
            self.assertCompiledIn(bn, zipfp.namelist())

        ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:
            fn = __file__
            ikiwa fn.endswith('.pyc'):
                fn = fn[:-1]

            zipfp.writepy(fn, "testpackage")

            bn = "%s/%s" % ("testpackage", os.path.basename(fn))
            self.assertNotIn(bn, zipfp.namelist())
            self.assertCompiledIn(bn, zipfp.namelist())

    eleza test_write_python_package(self):
        agiza email
        packagedir = os.path.dirname(email.__file__)
        self.requiresWriteAccess(packagedir)

        ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:
            zipfp.writepy(packagedir)

            # Check kila a couple of modules at different levels of the
            # hierarchy
            names = zipfp.namelist()
            self.assertCompiledIn('email/__init__.py', names)
            self.assertCompiledIn('email/mime/text.py', names)

    eleza test_write_filtered_python_package(self):
        agiza test
        packagedir = os.path.dirname(test.__file__)
        self.requiresWriteAccess(packagedir)

        ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:

            # first make sure that the test folder gives error messages
            # (on the badsyntax_... files)
            ukijumuisha captured_stdout() kama reportSIO:
                zipfp.writepy(packagedir)
            reportStr = reportSIO.getvalue()
            self.assertKweli('SyntaxError' kwenye reportStr)

            # then check that the filter works on the whole package
            ukijumuisha captured_stdout() kama reportSIO:
                zipfp.writepy(packagedir, filterfunc=lambda whatever: Uongo)
            reportStr = reportSIO.getvalue()
            self.assertKweli('SyntaxError' haiko kwenye reportStr)

            # then check that the filter works on individual files
            eleza filter(path):
                rudisha sio os.path.basename(path).startswith("bad")
            ukijumuisha captured_stdout() kama reportSIO, self.assertWarns(UserWarning):
                zipfp.writepy(packagedir, filterfunc=filter)
            reportStr = reportSIO.getvalue()
            ikiwa reportStr:
                andika(reportStr)
            self.assertKweli('SyntaxError' haiko kwenye reportStr)

    eleza test_write_with_optimization(self):
        agiza email
        packagedir = os.path.dirname(email.__file__)
        self.requiresWriteAccess(packagedir)
        optlevel = 1 ikiwa __debug__ isipokua 0
        ext = '.pyc'

        ukijumuisha TemporaryFile() kama t, \
             zipfile.PyZipFile(t, "w", optimize=optlevel) kama zipfp:
            zipfp.writepy(packagedir)

            names = zipfp.namelist()
            self.assertIn('email/__init__' + ext, names)
            self.assertIn('email/mime/text' + ext, names)

    eleza test_write_python_directory(self):
        os.mkdir(TESTFN2)
        jaribu:
            ukijumuisha open(os.path.join(TESTFN2, "mod1.py"), "w") kama fp:
                fp.write("andika(42)\n")

            ukijumuisha open(os.path.join(TESTFN2, "mod2.py"), "w") kama fp:
                fp.write("andika(42 * 42)\n")

            ukijumuisha open(os.path.join(TESTFN2, "mod2.txt"), "w") kama fp:
                fp.write("bla bla bla\n")

            ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:
                zipfp.writepy(TESTFN2)

                names = zipfp.namelist()
                self.assertCompiledIn('mod1.py', names)
                self.assertCompiledIn('mod2.py', names)
                self.assertNotIn('mod2.txt', names)

        mwishowe:
            rmtree(TESTFN2)

    eleza test_write_python_directory_filtered(self):
        os.mkdir(TESTFN2)
        jaribu:
            ukijumuisha open(os.path.join(TESTFN2, "mod1.py"), "w") kama fp:
                fp.write("andika(42)\n")

            ukijumuisha open(os.path.join(TESTFN2, "mod2.py"), "w") kama fp:
                fp.write("andika(42 * 42)\n")

            ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:
                zipfp.writepy(TESTFN2, filterfunc=lambda fn:
                                                  sio fn.endswith('mod2.py'))

                names = zipfp.namelist()
                self.assertCompiledIn('mod1.py', names)
                self.assertNotIn('mod2.py', names)

        mwishowe:
            rmtree(TESTFN2)

    eleza test_write_non_pyfile(self):
        ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:
            ukijumuisha open(TESTFN, 'w') kama f:
                f.write('most definitely sio a python file')
            self.assertRaises(RuntimeError, zipfp.writepy, TESTFN)
            unlink(TESTFN)

    eleza test_write_pyfile_bad_syntax(self):
        os.mkdir(TESTFN2)
        jaribu:
            ukijumuisha open(os.path.join(TESTFN2, "mod1.py"), "w") kama fp:
                fp.write("Bad syntax kwenye python file\n")

            ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:
                # syntax errors are printed to stdout
                ukijumuisha captured_stdout() kama s:
                    zipfp.writepy(os.path.join(TESTFN2, "mod1.py"))

                self.assertIn("SyntaxError", s.getvalue())

                # kama it will sio have compiled the python file, it will
                # include the .py file sio .pyc
                names = zipfp.namelist()
                self.assertIn('mod1.py', names)
                self.assertNotIn('mod1.pyc', names)

        mwishowe:
            rmtree(TESTFN2)

    eleza test_write_pathlike(self):
        os.mkdir(TESTFN2)
        jaribu:
            ukijumuisha open(os.path.join(TESTFN2, "mod1.py"), "w") kama fp:
                fp.write("andika(42)\n")

            ukijumuisha TemporaryFile() kama t, zipfile.PyZipFile(t, "w") kama zipfp:
                zipfp.writepy(pathlib.Path(TESTFN2) / "mod1.py")
                names = zipfp.namelist()
                self.assertCompiledIn('mod1.py', names)
        mwishowe:
            rmtree(TESTFN2)


kundi ExtractTests(unittest.TestCase):

    eleza make_test_file(self):
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) kama zipfp:
            kila fpath, fdata kwenye SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)

    eleza test_extract(self):
        ukijumuisha temp_cwd():
            self.make_test_file()
            ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
                kila fpath, fdata kwenye SMALL_TEST_DATA:
                    writtenfile = zipfp.extract(fpath)

                    # make sure it was written to the right place
                    correctfile = os.path.join(os.getcwd(), fpath)
                    correctfile = os.path.normpath(correctfile)

                    self.assertEqual(writtenfile, correctfile)

                    # make sure correct data ni kwenye correct file
                    ukijumuisha open(writtenfile, "rb") kama f:
                        self.assertEqual(fdata.encode(), f.read())

                    unlink(writtenfile)

    eleza _test_extract_with_target(self, target):
        self.make_test_file()
        ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
            kila fpath, fdata kwenye SMALL_TEST_DATA:
                writtenfile = zipfp.extract(fpath, target)

                # make sure it was written to the right place
                correctfile = os.path.join(target, fpath)
                correctfile = os.path.normpath(correctfile)
                self.assertKweli(os.path.samefile(writtenfile, correctfile), (writtenfile, target))

                # make sure correct data ni kwenye correct file
                ukijumuisha open(writtenfile, "rb") kama f:
                    self.assertEqual(fdata.encode(), f.read())

                unlink(writtenfile)

        unlink(TESTFN2)

    eleza test_extract_with_target(self):
        ukijumuisha temp_dir() kama extdir:
            self._test_extract_with_target(extdir)

    eleza test_extract_with_target_pathlike(self):
        ukijumuisha temp_dir() kama extdir:
            self._test_extract_with_target(pathlib.Path(extdir))

    eleza test_extract_all(self):
        ukijumuisha temp_cwd():
            self.make_test_file()
            ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
                zipfp.extractall()
                kila fpath, fdata kwenye SMALL_TEST_DATA:
                    outfile = os.path.join(os.getcwd(), fpath)

                    ukijumuisha open(outfile, "rb") kama f:
                        self.assertEqual(fdata.encode(), f.read())

                    unlink(outfile)

    eleza _test_extract_all_with_target(self, target):
        self.make_test_file()
        ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
            zipfp.extractall(target)
            kila fpath, fdata kwenye SMALL_TEST_DATA:
                outfile = os.path.join(target, fpath)

                ukijumuisha open(outfile, "rb") kama f:
                    self.assertEqual(fdata.encode(), f.read())

                unlink(outfile)

        unlink(TESTFN2)

    eleza test_extract_all_with_target(self):
        ukijumuisha temp_dir() kama extdir:
            self._test_extract_all_with_target(extdir)

    eleza test_extract_all_with_target_pathlike(self):
        ukijumuisha temp_dir() kama extdir:
            self._test_extract_all_with_target(pathlib.Path(extdir))

    eleza check_file(self, filename, content):
        self.assertKweli(os.path.isfile(filename))
        ukijumuisha open(filename, 'rb') kama f:
            self.assertEqual(f.read(), content)

    eleza test_sanitize_windows_name(self):
        san = zipfile.ZipFile._sanitize_windows_name
        # Passing pathsep kwenye allows this test to work regardless of platform.
        self.assertEqual(san(r',,?,C:,foo,bar/z', ','), r'_,C_,foo,bar/z')
        self.assertEqual(san(r'a\b,c<d>e|f"g?h*i', ','), r'a\b,c_d_e_f_g_h_i')
        self.assertEqual(san('../../foo../../ba..r', '/'), r'foo/ba..r')

    eleza test_extract_hackers_arcnames_common_cases(self):
        common_hacknames = [
            ('../foo/bar', 'foo/bar'),
            ('foo/../bar', 'foo/bar'),
            ('foo/../../bar', 'foo/bar'),
            ('foo/bar/..', 'foo/bar'),
            ('./../foo/bar', 'foo/bar'),
            ('/foo/bar', 'foo/bar'),
            ('/foo/../bar', 'foo/bar'),
            ('/foo/../../bar', 'foo/bar'),
        ]
        self._test_extract_hackers_arcnames(common_hacknames)

    @unittest.skipIf(os.path.sep != '\\', 'Requires \\ kama path separator.')
    eleza test_extract_hackers_arcnames_windows_only(self):
        """Test combination of path fixing na windows name sanitization."""
        windows_hacknames = [
            (r'..\foo\bar', 'foo/bar'),
            (r'..\/foo\/bar', 'foo/bar'),
            (r'foo/\..\/bar', 'foo/bar'),
            (r'foo\/../\bar', 'foo/bar'),
            (r'C:foo/bar', 'foo/bar'),
            (r'C:/foo/bar', 'foo/bar'),
            (r'C://foo/bar', 'foo/bar'),
            (r'C:\foo\bar', 'foo/bar'),
            (r'//conky/mountpoint/foo/bar', 'foo/bar'),
            (r'\\conky\mountpoint\foo\bar', 'foo/bar'),
            (r'///conky/mountpoint/foo/bar', 'conky/mountpoint/foo/bar'),
            (r'\\\conky\mountpoint\foo\bar', 'conky/mountpoint/foo/bar'),
            (r'//conky//mountpoint/foo/bar', 'conky/mountpoint/foo/bar'),
            (r'\\conky\\mountpoint\foo\bar', 'conky/mountpoint/foo/bar'),
            (r'//?/C:/foo/bar', 'foo/bar'),
            (r'\\?\C:\foo\bar', 'foo/bar'),
            (r'C:/../C:/foo/bar', 'C_/foo/bar'),
            (r'a:b\c<d>e|f"g?h*i', 'b/c_d_e_f_g_h_i'),
            ('../../foo../../ba..r', 'foo/ba..r'),
        ]
        self._test_extract_hackers_arcnames(windows_hacknames)

    @unittest.skipIf(os.path.sep != '/', r'Requires / kama path separator.')
    eleza test_extract_hackers_arcnames_posix_only(self):
        posix_hacknames = [
            ('//foo/bar', 'foo/bar'),
            ('../../foo../../ba..r', 'foo../ba..r'),
            (r'foo/..\bar', r'foo/..\bar'),
        ]
        self._test_extract_hackers_arcnames(posix_hacknames)

    eleza _test_extract_hackers_arcnames(self, hacknames):
        kila arcname, fixedname kwenye hacknames:
            content = b'foobar' + arcname.encode()
            ukijumuisha zipfile.ZipFile(TESTFN2, 'w', zipfile.ZIP_STORED) kama zipfp:
                zinfo = zipfile.ZipInfo()
                # preserve backslashes
                zinfo.filename = arcname
                zinfo.external_attr = 0o600 << 16
                zipfp.writestr(zinfo, content)

            arcname = arcname.replace(os.sep, "/")
            targetpath = os.path.join('target', 'subdir', 'subsub')
            correctfile = os.path.join(targetpath, *fixedname.split('/'))

            ukijumuisha zipfile.ZipFile(TESTFN2, 'r') kama zipfp:
                writtenfile = zipfp.extract(arcname, targetpath)
                self.assertEqual(writtenfile, correctfile,
                                 msg='extract %r: %r != %r' %
                                 (arcname, writtenfile, correctfile))
            self.check_file(correctfile, content)
            rmtree('target')

            ukijumuisha zipfile.ZipFile(TESTFN2, 'r') kama zipfp:
                zipfp.extractall(targetpath)
            self.check_file(correctfile, content)
            rmtree('target')

            correctfile = os.path.join(os.getcwd(), *fixedname.split('/'))

            ukijumuisha zipfile.ZipFile(TESTFN2, 'r') kama zipfp:
                writtenfile = zipfp.extract(arcname)
                self.assertEqual(writtenfile, correctfile,
                                 msg="extract %r" % arcname)
            self.check_file(correctfile, content)
            rmtree(fixedname.split('/')[0])

            ukijumuisha zipfile.ZipFile(TESTFN2, 'r') kama zipfp:
                zipfp.extractall()
            self.check_file(correctfile, content)
            rmtree(fixedname.split('/')[0])

            unlink(TESTFN2)


kundi OtherTests(unittest.TestCase):
    eleza test_open_via_zip_info(self):
        # Create the ZIP archive
        ukijumuisha zipfile.ZipFile(TESTFN2, "w", zipfile.ZIP_STORED) kama zipfp:
            zipfp.writestr("name", "foo")
            ukijumuisha self.assertWarns(UserWarning):
                zipfp.writestr("name", "bar")
            self.assertEqual(zipfp.namelist(), ["name"] * 2)

        ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
            infos = zipfp.infolist()
            data = b""
            kila info kwenye infos:
                ukijumuisha zipfp.open(info) kama zipopen:
                    data += zipopen.read()
            self.assertIn(data, {b"foobar", b"barfoo"})
            data = b""
            kila info kwenye infos:
                data += zipfp.read(info)
            self.assertIn(data, {b"foobar", b"barfoo"})

    eleza test_writestr_extended_local_header_issue1202(self):
        ukijumuisha zipfile.ZipFile(TESTFN2, 'w') kama orig_zip:
            kila data kwenye 'abcdefghijklmnop':
                zinfo = zipfile.ZipInfo(data)
                zinfo.flag_bits |= 0x08  # Include an extended local header.
                orig_zip.writestr(zinfo, data)

    eleza test_close(self):
        """Check that the zipfile ni closed after the 'with' block."""
        ukijumuisha zipfile.ZipFile(TESTFN2, "w") kama zipfp:
            kila fpath, fdata kwenye SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)
                self.assertIsNotTupu(zipfp.fp, 'zipfp ni sio open')
        self.assertIsTupu(zipfp.fp, 'zipfp ni sio closed')

        ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
            self.assertIsNotTupu(zipfp.fp, 'zipfp ni sio open')
        self.assertIsTupu(zipfp.fp, 'zipfp ni sio closed')

    eleza test_close_on_exception(self):
        """Check that the zipfile ni closed ikiwa an exception ni ashiriad kwenye the
        'with' block."""
        ukijumuisha zipfile.ZipFile(TESTFN2, "w") kama zipfp:
            kila fpath, fdata kwenye SMALL_TEST_DATA:
                zipfp.writestr(fpath, fdata)

        jaribu:
            ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp2:
                ashiria zipfile.BadZipFile()
        tatizo zipfile.BadZipFile:
            self.assertIsTupu(zipfp2.fp, 'zipfp ni sio closed')

    eleza test_unsupported_version(self):
        # File has an extract_version of 120
        data = (b'PK\x03\x04x\x00\x00\x00\x00\x00!p\xa1@\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00xPK\x01\x02x\x03x\x00\x00\x00\x00'
                b'\x00!p\xa1@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00\x00xPK\x05\x06'
                b'\x00\x00\x00\x00\x01\x00\x01\x00/\x00\x00\x00\x1f\x00\x00\x00\x00\x00')

        self.assertRaises(NotImplementedError, zipfile.ZipFile,
                          io.BytesIO(data), 'r')

    @requires_zlib
    eleza test_read_unicode_filenames(self):
        # bug #10801
        fname = findfile('zip_cp437_header.zip')
        ukijumuisha zipfile.ZipFile(fname) kama zipfp:
            kila name kwenye zipfp.namelist():
                zipfp.open(name).close()

    eleza test_write_unicode_filenames(self):
        ukijumuisha zipfile.ZipFile(TESTFN, "w") kama zf:
            zf.writestr("foo.txt", "Test kila unicode filename")
            zf.writestr("\xf6.txt", "Test kila unicode filename")
            self.assertIsInstance(zf.infolist()[0].filename, str)

        ukijumuisha zipfile.ZipFile(TESTFN, "r") kama zf:
            self.assertEqual(zf.filelist[0].filename, "foo.txt")
            self.assertEqual(zf.filelist[1].filename, "\xf6.txt")

    eleza test_exclusive_create_zip_file(self):
        """Test exclusive creating a new zipfile."""
        unlink(TESTFN2)
        filename = 'testfile.txt'
        content = b'hello, world. this ni some content.'
        ukijumuisha zipfile.ZipFile(TESTFN2, "x", zipfile.ZIP_STORED) kama zipfp:
            zipfp.writestr(filename, content)
        ukijumuisha self.assertRaises(FileExistsError):
            zipfile.ZipFile(TESTFN2, "x", zipfile.ZIP_STORED)
        ukijumuisha zipfile.ZipFile(TESTFN2, "r") kama zipfp:
            self.assertEqual(zipfp.namelist(), [filename])
            self.assertEqual(zipfp.read(filename), content)

    eleza test_create_non_existent_file_for_append(self):
        ikiwa os.path.exists(TESTFN):
            os.unlink(TESTFN)

        filename = 'testfile.txt'
        content = b'hello, world. this ni some content.'

        jaribu:
            ukijumuisha zipfile.ZipFile(TESTFN, 'a') kama zf:
                zf.writestr(filename, content)
        tatizo OSError:
            self.fail('Could sio append data to a non-existent zip file.')

        self.assertKweli(os.path.exists(TESTFN))

        ukijumuisha zipfile.ZipFile(TESTFN, 'r') kama zf:
            self.assertEqual(zf.read(filename), content)

    eleza test_close_erroneous_file(self):
        # This test checks that the ZipFile constructor closes the file object
        # it opens ikiwa there's an error kwenye the file.  If it doesn't, the
        # traceback holds a reference to the ZipFile object and, indirectly,
        # the file object.
        # On Windows, this causes the os.unlink() call to fail because the
        # underlying file ni still open.  This ni SF bug #412214.
        #
        ukijumuisha open(TESTFN, "w") kama fp:
            fp.write("this ni sio a legal zip file\n")
        jaribu:
            zf = zipfile.ZipFile(TESTFN)
        tatizo zipfile.BadZipFile:
            pita

    eleza test_is_zip_erroneous_file(self):
        """Check that is_zipfile() correctly identifies non-zip files."""
        # - pitaing a filename
        ukijumuisha open(TESTFN, "w") kama fp:
            fp.write("this ni sio a legal zip file\n")
        self.assertUongo(zipfile.is_zipfile(TESTFN))
        # - pitaing a path-like object
        self.assertUongo(zipfile.is_zipfile(pathlib.Path(TESTFN)))
        # - pitaing a file object
        ukijumuisha open(TESTFN, "rb") kama fp:
            self.assertUongo(zipfile.is_zipfile(fp))
        # - pitaing a file-like object
        fp = io.BytesIO()
        fp.write(b"this ni sio a legal zip file\n")
        self.assertUongo(zipfile.is_zipfile(fp))
        fp.seek(0, 0)
        self.assertUongo(zipfile.is_zipfile(fp))

    eleza test_damaged_zipfile(self):
        """Check that zipfiles ukijumuisha missing bytes at the end ashiria BadZipFile."""
        # - Create a valid zip file
        fp = io.BytesIO()
        ukijumuisha zipfile.ZipFile(fp, mode="w") kama zipf:
            zipf.writestr("foo.txt", b"O, kila a Muse of Fire!")
        zipfiledata = fp.getvalue()

        # - Now create copies of it missing the last N bytes na make sure
        #   a BadZipFile exception ni ashiriad when we try to open it
        kila N kwenye range(len(zipfiledata)):
            fp = io.BytesIO(zipfiledata[:N])
            self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, fp)

    eleza test_is_zip_valid_file(self):
        """Check that is_zipfile() correctly identifies zip files."""
        # - pitaing a filename
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            zipf.writestr("foo.txt", b"O, kila a Muse of Fire!")

        self.assertKweli(zipfile.is_zipfile(TESTFN))
        # - pitaing a file object
        ukijumuisha open(TESTFN, "rb") kama fp:
            self.assertKweli(zipfile.is_zipfile(fp))
            fp.seek(0, 0)
            zip_contents = fp.read()
        # - pitaing a file-like object
        fp = io.BytesIO()
        fp.write(zip_contents)
        self.assertKweli(zipfile.is_zipfile(fp))
        fp.seek(0, 0)
        self.assertKweli(zipfile.is_zipfile(fp))

    eleza test_non_existent_file_ashirias_OSError(self):
        # make sure we don't ashiria an AttributeError when a partially-constructed
        # ZipFile instance ni finalized; this tests kila regression on SF tracker
        # bug #403871.

        # The bug we're testing kila caused an AttributeError to be ashiriad
        # when a ZipFile instance was created kila a file that did not
        # exist; the .fp member was sio initialized but was needed by the
        # __del__() method.  Since the AttributeError ni kwenye the __del__(),
        # it ni ignored, but the user should be sufficiently annoyed by
        # the message on the output that regression will be noticed
        # quickly.
        self.assertRaises(OSError, zipfile.ZipFile, TESTFN)

    eleza test_empty_file_ashirias_BadZipFile(self):
        f = open(TESTFN, 'w')
        f.close()
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN)

        ukijumuisha open(TESTFN, 'w') kama fp:
            fp.write("short file")
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN)

    eleza test_closed_zip_ashirias_ValueError(self):
        """Verify that testzip() doesn't swallow inappropriate exceptions."""
        data = io.BytesIO()
        ukijumuisha zipfile.ZipFile(data, mode="w") kama zipf:
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")

        # This ni correct; calling .read on a closed ZipFile should ashiria
        # a ValueError, na so should calling .testzip.  An earlier
        # version of .testzip would swallow this exception (and any other)
        # na report that the first file kwenye the archive was corrupt.
        self.assertRaises(ValueError, zipf.read, "foo.txt")
        self.assertRaises(ValueError, zipf.open, "foo.txt")
        self.assertRaises(ValueError, zipf.testzip)
        self.assertRaises(ValueError, zipf.writestr, "bogus.txt", "bogus")
        ukijumuisha open(TESTFN, 'w') kama f:
            f.write('zipfile test data')
        self.assertRaises(ValueError, zipf.write, TESTFN)

    eleza test_bad_constructor_mode(self):
        """Check that bad modes pitaed to ZipFile constructor are caught."""
        self.assertRaises(ValueError, zipfile.ZipFile, TESTFN, "q")

    eleza test_bad_open_mode(self):
        """Check that bad modes pitaed to ZipFile.open are caught."""
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")

        ukijumuisha zipfile.ZipFile(TESTFN, mode="r") kama zipf:
            # read the data to make sure the file ni there
            zipf.read("foo.txt")
            self.assertRaises(ValueError, zipf.open, "foo.txt", "q")
            # universal newlines support ni removed
            self.assertRaises(ValueError, zipf.open, "foo.txt", "U")
            self.assertRaises(ValueError, zipf.open, "foo.txt", "rU")

    eleza test_read0(self):
        """Check that calling read(0) on a ZipExtFile object rudishas an empty
        string na doesn't advance file pointer."""
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")
            # read the data to make sure the file ni there
            ukijumuisha zipf.open("foo.txt") kama f:
                kila i kwenye range(FIXEDTEST_SIZE):
                    self.assertEqual(f.read(0), b'')

                self.assertEqual(f.read(), b"O, kila a Muse of Fire!")

    eleza test_open_non_existent_item(self):
        """Check that attempting to call open() kila an item that doesn't
        exist kwenye the archive ashirias a RuntimeError."""
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            self.assertRaises(KeyError, zipf.open, "foo.txt", "r")

    eleza test_bad_compression_mode(self):
        """Check that bad compression methods pitaed to ZipFile.open are
        caught."""
        self.assertRaises(NotImplementedError, zipfile.ZipFile, TESTFN, "w", -1)

    eleza test_unsupported_compression(self):
        # data ni declared kama shrunk, but actually deflated
        data = (b'PK\x03\x04.\x00\x00\x00\x01\x00\xe4C\xa1@\x00\x00\x00'
                b'\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00x\x03\x00PK\x01'
                b'\x02.\x03.\x00\x00\x00\x01\x00\xe4C\xa1@\x00\x00\x00\x00\x02\x00\x00'
                b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x80\x01\x00\x00\x00\x00xPK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00'
                b'/\x00\x00\x00!\x00\x00\x00\x00\x00')
        ukijumuisha zipfile.ZipFile(io.BytesIO(data), 'r') kama zipf:
            self.assertRaises(NotImplementedError, zipf.open, 'x')

    eleza test_null_byte_in_filename(self):
        """Check that a filename containing a null byte ni properly
        terminated."""
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            zipf.writestr("foo.txt\x00qqq", b"O, kila a Muse of Fire!")
            self.assertEqual(zipf.namelist(), ['foo.txt'])

    eleza test_struct_sizes(self):
        """Check that ZIP internal structure sizes are calculated correctly."""
        self.assertEqual(zipfile.sizeEndCentDir, 22)
        self.assertEqual(zipfile.sizeCentralDir, 46)
        self.assertEqual(zipfile.sizeEndCentDir64, 56)
        self.assertEqual(zipfile.sizeEndCentDir64Locator, 20)

    eleza test_comments(self):
        """Check that comments on the archive are handled properly."""

        # check default comment ni empty
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            self.assertEqual(zipf.comment, b'')
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")

        ukijumuisha zipfile.ZipFile(TESTFN, mode="r") kama zipfr:
            self.assertEqual(zipfr.comment, b'')

        # check a simple short comment
        comment = b'Bravely taking to his feet, he beat a very brave retreat.'
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            zipf.comment = comment
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")
        ukijumuisha zipfile.ZipFile(TESTFN, mode="r") kama zipfr:
            self.assertEqual(zipf.comment, comment)

        # check a comment of max length
        comment2 = ''.join(['%d' % (i**3 % 10) kila i kwenye range((1 << 16)-1)])
        comment2 = comment2.encode("ascii")
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            zipf.comment = comment2
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")

        ukijumuisha zipfile.ZipFile(TESTFN, mode="r") kama zipfr:
            self.assertEqual(zipfr.comment, comment2)

        # check a comment that ni too long ni truncated
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w") kama zipf:
            ukijumuisha self.assertWarns(UserWarning):
                zipf.comment = comment2 + b'oops'
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")
        ukijumuisha zipfile.ZipFile(TESTFN, mode="r") kama zipfr:
            self.assertEqual(zipfr.comment, comment2)

        # check that comments are correctly modified kwenye append mode
        ukijumuisha zipfile.ZipFile(TESTFN,mode="w") kama zipf:
            zipf.comment = b"original comment"
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")
        ukijumuisha zipfile.ZipFile(TESTFN,mode="a") kama zipf:
            zipf.comment = b"an updated comment"
        ukijumuisha zipfile.ZipFile(TESTFN,mode="r") kama zipf:
            self.assertEqual(zipf.comment, b"an updated comment")

        # check that comments are correctly shortened kwenye append mode
        ukijumuisha zipfile.ZipFile(TESTFN,mode="w") kama zipf:
            zipf.comment = b"original comment that's longer"
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")
        ukijumuisha zipfile.ZipFile(TESTFN,mode="a") kama zipf:
            zipf.comment = b"shorter comment"
        ukijumuisha zipfile.ZipFile(TESTFN,mode="r") kama zipf:
            self.assertEqual(zipf.comment, b"shorter comment")

    eleza test_unicode_comment(self):
        ukijumuisha zipfile.ZipFile(TESTFN, "w", zipfile.ZIP_STORED) kama zipf:
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")
            ukijumuisha self.assertRaises(TypeError):
                zipf.comment = "this ni an error"

    eleza test_change_comment_in_empty_archive(self):
        ukijumuisha zipfile.ZipFile(TESTFN, "a", zipfile.ZIP_STORED) kama zipf:
            self.assertUongo(zipf.filelist)
            zipf.comment = b"this ni a comment"
        ukijumuisha zipfile.ZipFile(TESTFN, "r") kama zipf:
            self.assertEqual(zipf.comment, b"this ni a comment")

    eleza test_change_comment_in_nonempty_archive(self):
        ukijumuisha zipfile.ZipFile(TESTFN, "w", zipfile.ZIP_STORED) kama zipf:
            zipf.writestr("foo.txt", "O, kila a Muse of Fire!")
        ukijumuisha zipfile.ZipFile(TESTFN, "a", zipfile.ZIP_STORED) kama zipf:
            self.assertKweli(zipf.filelist)
            zipf.comment = b"this ni a comment"
        ukijumuisha zipfile.ZipFile(TESTFN, "r") kama zipf:
            self.assertEqual(zipf.comment, b"this ni a comment")

    eleza test_empty_zipfile(self):
        # Check that creating a file kwenye 'w' ama 'a' mode na closing without
        # adding any files to the archives creates a valid empty ZIP file
        zipf = zipfile.ZipFile(TESTFN, mode="w")
        zipf.close()
        jaribu:
            zipf = zipfile.ZipFile(TESTFN, mode="r")
        tatizo zipfile.BadZipFile:
            self.fail("Unable to create empty ZIP file kwenye 'w' mode")

        zipf = zipfile.ZipFile(TESTFN, mode="a")
        zipf.close()
        jaribu:
            zipf = zipfile.ZipFile(TESTFN, mode="r")
        tatizo:
            self.fail("Unable to create empty ZIP file kwenye 'a' mode")

    eleza test_open_empty_file(self):
        # Issue 1710703: Check that opening a file ukijumuisha less than 22 bytes
        # ashirias a BadZipFile exception (rather than the previously unhelpful
        # OSError)
        f = open(TESTFN, 'w')
        f.close()
        self.assertRaises(zipfile.BadZipFile, zipfile.ZipFile, TESTFN, 'r')

    eleza test_create_zipinfo_before_1980(self):
        self.assertRaises(ValueError,
                          zipfile.ZipInfo, 'seventies', (1979, 1, 1, 0, 0, 0))

    eleza test_zipfile_with_short_extra_field(self):
        """If an extra field kwenye the header ni less than 4 bytes, skip it."""
        zipdata = (
            b'PK\x03\x04\x14\x00\x00\x00\x00\x00\x93\x9b\xad@\x8b\x9e'
            b'\xd9\xd3\x01\x00\x00\x00\x01\x00\x00\x00\x03\x00\x03\x00ab'
            b'c\x00\x00\x00APK\x01\x02\x14\x03\x14\x00\x00\x00\x00'
            b'\x00\x93\x9b\xad@\x8b\x9e\xd9\xd3\x01\x00\x00\x00\x01\x00\x00'
            b'\x00\x03\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa4\x81\x00'
            b'\x00\x00\x00abc\x00\x00PK\x05\x06\x00\x00\x00\x00'
            b'\x01\x00\x01\x003\x00\x00\x00%\x00\x00\x00\x00\x00'
        )
        ukijumuisha zipfile.ZipFile(io.BytesIO(zipdata), 'r') kama zipf:
            # testzip rudishas the name of the first corrupt file, ama Tupu
            self.assertIsTupu(zipf.testzip())

    eleza test_open_conflicting_handles(self):
        # It's only possible to open one writable file handle at a time
        msg1 = b"It's fun to charter an accountant!"
        msg2 = b"And sail the wide accountant sea"
        msg3 = b"To find, explore the funds offshore"
        ukijumuisha zipfile.ZipFile(TESTFN2, 'w', zipfile.ZIP_STORED) kama zipf:
            ukijumuisha zipf.open('foo', mode='w') kama w2:
                w2.write(msg1)
            ukijumuisha zipf.open('bar', mode='w') kama w1:
                ukijumuisha self.assertRaises(ValueError):
                    zipf.open('handle', mode='w')
                ukijumuisha self.assertRaises(ValueError):
                    zipf.open('foo', mode='r')
                ukijumuisha self.assertRaises(ValueError):
                    zipf.writestr('str', 'abcde')
                ukijumuisha self.assertRaises(ValueError):
                    zipf.write(__file__, 'file')
                ukijumuisha self.assertRaises(ValueError):
                    zipf.close()
                w1.write(msg2)
            ukijumuisha zipf.open('baz', mode='w') kama w2:
                w2.write(msg3)

        ukijumuisha zipfile.ZipFile(TESTFN2, 'r') kama zipf:
            self.assertEqual(zipf.read('foo'), msg1)
            self.assertEqual(zipf.read('bar'), msg2)
            self.assertEqual(zipf.read('baz'), msg3)
            self.assertEqual(zipf.namelist(), ['foo', 'bar', 'baz'])

    eleza test_seek_tell(self):
        # Test seek functionality
        txt = b"Where's Bruce?"
        bloc = txt.find(b"Bruce")
        # Check seek on a file
        ukijumuisha zipfile.ZipFile(TESTFN, "w") kama zipf:
            zipf.writestr("foo.txt", txt)
        ukijumuisha zipfile.ZipFile(TESTFN, "r") kama zipf:
            ukijumuisha zipf.open("foo.txt", "r") kama fp:
                fp.seek(bloc, os.SEEK_SET)
                self.assertEqual(fp.tell(), bloc)
                fp.seek(-bloc, os.SEEK_CUR)
                self.assertEqual(fp.tell(), 0)
                fp.seek(bloc, os.SEEK_CUR)
                self.assertEqual(fp.tell(), bloc)
                self.assertEqual(fp.read(5), txt[bloc:bloc+5])
                fp.seek(0, os.SEEK_END)
                self.assertEqual(fp.tell(), len(txt))
                fp.seek(0, os.SEEK_SET)
                self.assertEqual(fp.tell(), 0)
        # Check seek on memory file
        data = io.BytesIO()
        ukijumuisha zipfile.ZipFile(data, mode="w") kama zipf:
            zipf.writestr("foo.txt", txt)
        ukijumuisha zipfile.ZipFile(data, mode="r") kama zipf:
            ukijumuisha zipf.open("foo.txt", "r") kama fp:
                fp.seek(bloc, os.SEEK_SET)
                self.assertEqual(fp.tell(), bloc)
                fp.seek(-bloc, os.SEEK_CUR)
                self.assertEqual(fp.tell(), 0)
                fp.seek(bloc, os.SEEK_CUR)
                self.assertEqual(fp.tell(), bloc)
                self.assertEqual(fp.read(5), txt[bloc:bloc+5])
                fp.seek(0, os.SEEK_END)
                self.assertEqual(fp.tell(), len(txt))
                fp.seek(0, os.SEEK_SET)
                self.assertEqual(fp.tell(), 0)

    @requires_bz2
    eleza test_decompress_without_3rd_party_library(self):
        data = b'PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        zip_file = io.BytesIO(data)
        ukijumuisha zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_BZIP2) kama zf:
            zf.writestr('a.txt', b'a')
        ukijumuisha mock.patch('zipfile.bz2', Tupu):
            ukijumuisha zipfile.ZipFile(zip_file) kama zf:
                self.assertRaises(RuntimeError, zf.extract, 'a.txt')

    eleza tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)


kundi AbstractBadCrcTests:
    eleza test_testzip_with_bad_crc(self):
        """Tests that files ukijumuisha bad CRCs rudisha their name kutoka testzip."""
        zipdata = self.zip_with_bad_crc

        ukijumuisha zipfile.ZipFile(io.BytesIO(zipdata), mode="r") kama zipf:
            # testzip rudishas the name of the first corrupt file, ama Tupu
            self.assertEqual('afile', zipf.testzip())

    eleza test_read_with_bad_crc(self):
        """Tests that files ukijumuisha bad CRCs ashiria a BadZipFile exception when read."""
        zipdata = self.zip_with_bad_crc

        # Using ZipFile.read()
        ukijumuisha zipfile.ZipFile(io.BytesIO(zipdata), mode="r") kama zipf:
            self.assertRaises(zipfile.BadZipFile, zipf.read, 'afile')

        # Using ZipExtFile.read()
        ukijumuisha zipfile.ZipFile(io.BytesIO(zipdata), mode="r") kama zipf:
            ukijumuisha zipf.open('afile', 'r') kama corrupt_file:
                self.assertRaises(zipfile.BadZipFile, corrupt_file.read)

        # Same ukijumuisha small reads (in order to exercise the buffering logic)
        ukijumuisha zipfile.ZipFile(io.BytesIO(zipdata), mode="r") kama zipf:
            ukijumuisha zipf.open('afile', 'r') kama corrupt_file:
                corrupt_file.MIN_READ_SIZE = 2
                ukijumuisha self.assertRaises(zipfile.BadZipFile):
                    wakati corrupt_file.read(2):
                        pita


kundi StoredBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
    compression = zipfile.ZIP_STORED
    zip_with_bad_crc = (
        b'PK\003\004\024\0\0\0\0\0 \213\212;:r'
        b'\253\377\f\0\0\0\f\0\0\0\005\0\0\000af'
        b'ilehello,AworldP'
        b'K\001\002\024\003\024\0\0\0\0\0 \213\212;:'
        b'r\253\377\f\0\0\0\f\0\0\0\005\0\0\0\0'
        b'\0\0\0\0\0\0\0\200\001\0\0\0\000afi'
        b'lePK\005\006\0\0\0\0\001\0\001\0003\000'
        b'\0\0/\0\0\0\0\0')

@requires_zlib
kundi DeflateBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED
    zip_with_bad_crc = (
        b'PK\x03\x04\x14\x00\x00\x00\x08\x00n}\x0c=FA'
        b'KE\x10\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
        b'ile\xcbH\xcd\xc9\xc9W(\xcf/\xcaI\xc9\xa0'
        b'=\x13\x00PK\x01\x02\x14\x03\x14\x00\x00\x00\x08\x00n'
        b'}\x0c=FAKE\x10\x00\x00\x00n\x00\x00\x00\x05'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x01\x00\x00\x00'
        b'\x00afilePK\x05\x06\x00\x00\x00\x00\x01\x00'
        b'\x01\x003\x00\x00\x003\x00\x00\x00\x00\x00')

@requires_bz2
kundi Bzip2BadCrcTests(AbstractBadCrcTests, unittest.TestCase):
    compression = zipfile.ZIP_BZIP2
    zip_with_bad_crc = (
        b'PK\x03\x04\x14\x03\x00\x00\x0c\x00nu\x0c=FA'
        b'KE8\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
        b'ileBZh91AY&SY\xd4\xa8\xca'
        b'\x7f\x00\x00\x0f\x11\x80@\x00\x06D\x90\x80 \x00 \xa5'
        b'P\xd9!\x03\x03\x13\x13\x13\x89\xa9\xa9\xc2u5:\x9f'
        b'\x8b\xb9"\x9c(HjTe?\x80PK\x01\x02\x14'
        b'\x03\x14\x03\x00\x00\x0c\x00nu\x0c=FAKE8'
        b'\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00 \x80\x80\x81\x00\x00\x00\x00afilePK'
        b'\x05\x06\x00\x00\x00\x00\x01\x00\x01\x003\x00\x00\x00[\x00'
        b'\x00\x00\x00\x00')

@requires_lzma
kundi LzmaBadCrcTests(AbstractBadCrcTests, unittest.TestCase):
    compression = zipfile.ZIP_LZMA
    zip_with_bad_crc = (
        b'PK\x03\x04\x14\x03\x00\x00\x0e\x00nu\x0c=FA'
        b'KE\x1b\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00af'
        b'ile\t\x04\x05\x00]\x00\x00\x00\x04\x004\x19I'
        b'\xee\x8d\xe9\x17\x89:3`\tq!.8\x00PK'
        b'\x01\x02\x14\x03\x14\x03\x00\x00\x0e\x00nu\x0c=FA'
        b'KE\x1b\x00\x00\x00n\x00\x00\x00\x05\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00 \x80\x80\x81\x00\x00\x00\x00afil'
        b'ePK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x003\x00\x00'
        b'\x00>\x00\x00\x00\x00\x00')


kundi DecryptionTests(unittest.TestCase):
    """Check that ZIP decryption works. Since the library does not
    support encryption at the moment, we use a pre-generated encrypted
    ZIP file."""

    data = (
        b'PK\x03\x04\x14\x00\x01\x00\x00\x00n\x92i.#y\xef?&\x00\x00\x00\x1a\x00'
        b'\x00\x00\x08\x00\x00\x00test.txt\xfa\x10\xa0gly|\xfa-\xc5\xc0=\xf9y'
        b'\x18\xe0\xa8r\xb3Z}Lg\xbc\xae\xf9|\x9b\x19\xe4\x8b\xba\xbb)\x8c\xb0\xdbl'
        b'PK\x01\x02\x14\x00\x14\x00\x01\x00\x00\x00n\x92i.#y\xef?&\x00\x00\x00'
        b'\x1a\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00 \x00\xb6\x81'
        b'\x00\x00\x00\x00test.txtPK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x006\x00'
        b'\x00\x00L\x00\x00\x00\x00\x00' )
    data2 = (
        b'PK\x03\x04\x14\x00\t\x00\x08\x00\xcf}38xu\xaa\xb2\x14\x00\x00\x00\x00\x02'
        b'\x00\x00\x04\x00\x15\x00zeroUT\t\x00\x03\xd6\x8b\x92G\xda\x8b\x92GUx\x04'
        b'\x00\xe8\x03\xe8\x03\xc7<M\xb5a\xceX\xa3Y&\x8b{oE\xd7\x9d\x8c\x98\x02\xc0'
        b'PK\x07\x08xu\xaa\xb2\x14\x00\x00\x00\x00\x02\x00\x00PK\x01\x02\x17\x03'
        b'\x14\x00\t\x00\x08\x00\xcf}38xu\xaa\xb2\x14\x00\x00\x00\x00\x02\x00\x00'
        b'\x04\x00\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa4\x81\x00\x00\x00\x00ze'
        b'roUT\x05\x00\x03\xd6\x8b\x92GUx\x00\x00PK\x05\x06\x00\x00\x00\x00\x01'
        b'\x00\x01\x00?\x00\x00\x00[\x00\x00\x00\x00\x00' )

    plain = b'zipfile.py encryption test'
    plain2 = b'\x00'*512

    eleza setUp(self):
        ukijumuisha open(TESTFN, "wb") kama fp:
            fp.write(self.data)
        self.zip = zipfile.ZipFile(TESTFN, "r")
        ukijumuisha open(TESTFN2, "wb") kama fp:
            fp.write(self.data2)
        self.zip2 = zipfile.ZipFile(TESTFN2, "r")

    eleza tearDown(self):
        self.zip.close()
        os.unlink(TESTFN)
        self.zip2.close()
        os.unlink(TESTFN2)

    eleza test_no_pitaword(self):
        # Reading the encrypted file without pitaword
        # must generate a RunTime exception
        self.assertRaises(RuntimeError, self.zip.read, "test.txt")
        self.assertRaises(RuntimeError, self.zip2.read, "zero")

    eleza test_bad_pitaword(self):
        self.zip.setpitaword(b"perl")
        self.assertRaises(RuntimeError, self.zip.read, "test.txt")
        self.zip2.setpitaword(b"perl")
        self.assertRaises(RuntimeError, self.zip2.read, "zero")

    @requires_zlib
    eleza test_good_pitaword(self):
        self.zip.setpitaword(b"python")
        self.assertEqual(self.zip.read("test.txt"), self.plain)
        self.zip2.setpitaword(b"12345")
        self.assertEqual(self.zip2.read("zero"), self.plain2)

    eleza test_unicode_pitaword(self):
        self.assertRaises(TypeError, self.zip.setpitaword, "unicode")
        self.assertRaises(TypeError, self.zip.read, "test.txt", "python")
        self.assertRaises(TypeError, self.zip.open, "test.txt", pwd="python")
        self.assertRaises(TypeError, self.zip.extract, "test.txt", pwd="python")

kundi AbstractTestsWithRandomBinaryFiles:
    @classmethod
    eleza setUpClass(cls):
        datacount = randint(16, 64)*1024 + randint(1, 1024)
        cls.data = b''.join(struct.pack('<f', random()*randint(-1000, 1000))
                            kila i kwenye range(datacount))

    eleza setUp(self):
        # Make a source file ukijumuisha some lines
        ukijumuisha open(TESTFN, "wb") kama fp:
            fp.write(self.data)

    eleza tearDown(self):
        unlink(TESTFN)
        unlink(TESTFN2)

    eleza make_test_archive(self, f, compression):
        # Create the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "w", compression) kama zipfp:
            zipfp.write(TESTFN, "another.name")
            zipfp.write(TESTFN, TESTFN)

    eleza zip_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r", compression) kama zipfp:
            testdata = zipfp.read(TESTFN)
            self.assertEqual(len(testdata), len(self.data))
            self.assertEqual(testdata, self.data)
            self.assertEqual(zipfp.read("another.name"), self.data)

    eleza test_read(self):
        kila f kwenye get_files(self):
            self.zip_test(f, self.compression)

    eleza zip_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r", compression) kama zipfp:
            zipdata1 = []
            ukijumuisha zipfp.open(TESTFN) kama zipopen1:
                wakati Kweli:
                    read_data = zipopen1.read(256)
                    ikiwa sio read_data:
                        koma
                    zipdata1.append(read_data)

            zipdata2 = []
            ukijumuisha zipfp.open("another.name") kama zipopen2:
                wakati Kweli:
                    read_data = zipopen2.read(256)
                    ikiwa sio read_data:
                        koma
                    zipdata2.append(read_data)

            testdata1 = b''.join(zipdata1)
            self.assertEqual(len(testdata1), len(self.data))
            self.assertEqual(testdata1, self.data)

            testdata2 = b''.join(zipdata2)
            self.assertEqual(len(testdata2), len(self.data))
            self.assertEqual(testdata2, self.data)

    eleza test_open(self):
        kila f kwenye get_files(self):
            self.zip_open_test(f, self.compression)

    eleza zip_random_open_test(self, f, compression):
        self.make_test_archive(f, compression)

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r", compression) kama zipfp:
            zipdata1 = []
            ukijumuisha zipfp.open(TESTFN) kama zipopen1:
                wakati Kweli:
                    read_data = zipopen1.read(randint(1, 1024))
                    ikiwa sio read_data:
                        koma
                    zipdata1.append(read_data)

            testdata = b''.join(zipdata1)
            self.assertEqual(len(testdata), len(self.data))
            self.assertEqual(testdata, self.data)

    eleza test_random_open(self):
        kila f kwenye get_files(self):
            self.zip_random_open_test(f, self.compression)


kundi StoredTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                       unittest.TestCase):
    compression = zipfile.ZIP_STORED

@requires_zlib
kundi DeflateTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                        unittest.TestCase):
    compression = zipfile.ZIP_DEFLATED

@requires_bz2
kundi Bzip2TestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                      unittest.TestCase):
    compression = zipfile.ZIP_BZIP2

@requires_lzma
kundi LzmaTestsWithRandomBinaryFiles(AbstractTestsWithRandomBinaryFiles,
                                     unittest.TestCase):
    compression = zipfile.ZIP_LZMA


# Provide the tell() method but sio seek()
kundi Tellable:
    eleza __init__(self, fp):
        self.fp = fp
        self.offset = 0

    eleza write(self, data):
        n = self.fp.write(data)
        self.offset += n
        rudisha n

    eleza tell(self):
        rudisha self.offset

    eleza flush(self):
        self.fp.flush()

kundi Unseekable:
    eleza __init__(self, fp):
        self.fp = fp

    eleza write(self, data):
        rudisha self.fp.write(data)

    eleza flush(self):
        self.fp.flush()

kundi UnseekableTests(unittest.TestCase):
    eleza test_writestr(self):
        kila wrapper kwenye (lambda f: f), Tellable, Unseekable:
            ukijumuisha self.subTest(wrapper=wrapper):
                f = io.BytesIO()
                f.write(b'abc')
                bf = io.BufferedWriter(f)
                ukijumuisha zipfile.ZipFile(wrapper(bf), 'w', zipfile.ZIP_STORED) kama zipfp:
                    zipfp.writestr('ones', b'111')
                    zipfp.writestr('twos', b'222')
                self.assertEqual(f.getvalue()[:5], b'abcPK')
                ukijumuisha zipfile.ZipFile(f, mode='r') kama zipf:
                    ukijumuisha zipf.open('ones') kama zopen:
                        self.assertEqual(zopen.read(), b'111')
                    ukijumuisha zipf.open('twos') kama zopen:
                        self.assertEqual(zopen.read(), b'222')

    eleza test_write(self):
        kila wrapper kwenye (lambda f: f), Tellable, Unseekable:
            ukijumuisha self.subTest(wrapper=wrapper):
                f = io.BytesIO()
                f.write(b'abc')
                bf = io.BufferedWriter(f)
                ukijumuisha zipfile.ZipFile(wrapper(bf), 'w', zipfile.ZIP_STORED) kama zipfp:
                    self.addCleanup(unlink, TESTFN)
                    ukijumuisha open(TESTFN, 'wb') kama f2:
                        f2.write(b'111')
                    zipfp.write(TESTFN, 'ones')
                    ukijumuisha open(TESTFN, 'wb') kama f2:
                        f2.write(b'222')
                    zipfp.write(TESTFN, 'twos')
                self.assertEqual(f.getvalue()[:5], b'abcPK')
                ukijumuisha zipfile.ZipFile(f, mode='r') kama zipf:
                    ukijumuisha zipf.open('ones') kama zopen:
                        self.assertEqual(zopen.read(), b'111')
                    ukijumuisha zipf.open('twos') kama zopen:
                        self.assertEqual(zopen.read(), b'222')

    eleza test_open_write(self):
        kila wrapper kwenye (lambda f: f), Tellable, Unseekable:
            ukijumuisha self.subTest(wrapper=wrapper):
                f = io.BytesIO()
                f.write(b'abc')
                bf = io.BufferedWriter(f)
                ukijumuisha zipfile.ZipFile(wrapper(bf), 'w', zipfile.ZIP_STORED) kama zipf:
                    ukijumuisha zipf.open('ones', 'w') kama zopen:
                        zopen.write(b'111')
                    ukijumuisha zipf.open('twos', 'w') kama zopen:
                        zopen.write(b'222')
                self.assertEqual(f.getvalue()[:5], b'abcPK')
                ukijumuisha zipfile.ZipFile(f) kama zipf:
                    self.assertEqual(zipf.read('ones'), b'111')
                    self.assertEqual(zipf.read('twos'), b'222')


@requires_zlib
kundi TestsWithMultipleOpens(unittest.TestCase):
    @classmethod
    eleza setUpClass(cls):
        cls.data1 = b'111' + getrandbytes(10000)
        cls.data2 = b'222' + getrandbytes(10000)

    eleza make_test_archive(self, f):
        # Create the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) kama zipfp:
            zipfp.writestr('ones', self.data1)
            zipfp.writestr('twos', self.data2)

    eleza test_same_file(self):
        # Verify that (when the ZipFile ni kwenye control of creating file objects)
        # multiple open() calls can be made without interfering ukijumuisha each other.
        kila f kwenye get_files(self):
            self.make_test_archive(f)
            ukijumuisha zipfile.ZipFile(f, mode="r") kama zipf:
                ukijumuisha zipf.open('ones') kama zopen1, zipf.open('ones') kama zopen2:
                    data1 = zopen1.read(500)
                    data2 = zopen2.read(500)
                    data1 += zopen1.read()
                    data2 += zopen2.read()
                self.assertEqual(data1, data2)
                self.assertEqual(data1, self.data1)

    eleza test_different_file(self):
        # Verify that (when the ZipFile ni kwenye control of creating file objects)
        # multiple open() calls can be made without interfering ukijumuisha each other.
        kila f kwenye get_files(self):
            self.make_test_archive(f)
            ukijumuisha zipfile.ZipFile(f, mode="r") kama zipf:
                ukijumuisha zipf.open('ones') kama zopen1, zipf.open('twos') kama zopen2:
                    data1 = zopen1.read(500)
                    data2 = zopen2.read(500)
                    data1 += zopen1.read()
                    data2 += zopen2.read()
                self.assertEqual(data1, self.data1)
                self.assertEqual(data2, self.data2)

    eleza test_interleaved(self):
        # Verify that (when the ZipFile ni kwenye control of creating file objects)
        # multiple open() calls can be made without interfering ukijumuisha each other.
        kila f kwenye get_files(self):
            self.make_test_archive(f)
            ukijumuisha zipfile.ZipFile(f, mode="r") kama zipf:
                ukijumuisha zipf.open('ones') kama zopen1:
                    data1 = zopen1.read(500)
                    ukijumuisha zipf.open('twos') kama zopen2:
                        data2 = zopen2.read(500)
                        data1 += zopen1.read()
                        data2 += zopen2.read()
                self.assertEqual(data1, self.data1)
                self.assertEqual(data2, self.data2)

    eleza test_read_after_close(self):
        kila f kwenye get_files(self):
            self.make_test_archive(f)
            ukijumuisha contextlib.ExitStack() kama stack:
                ukijumuisha zipfile.ZipFile(f, 'r') kama zipf:
                    zopen1 = stack.enter_context(zipf.open('ones'))
                    zopen2 = stack.enter_context(zipf.open('twos'))
                data1 = zopen1.read(500)
                data2 = zopen2.read(500)
                data1 += zopen1.read()
                data2 += zopen2.read()
            self.assertEqual(data1, self.data1)
            self.assertEqual(data2, self.data2)

    eleza test_read_after_write(self):
        kila f kwenye get_files(self):
            ukijumuisha zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED) kama zipf:
                zipf.writestr('ones', self.data1)
                zipf.writestr('twos', self.data2)
                ukijumuisha zipf.open('ones') kama zopen1:
                    data1 = zopen1.read(500)
            self.assertEqual(data1, self.data1[:500])
            ukijumuisha zipfile.ZipFile(f, 'r') kama zipf:
                data1 = zipf.read('ones')
                data2 = zipf.read('twos')
            self.assertEqual(data1, self.data1)
            self.assertEqual(data2, self.data2)

    eleza test_write_after_read(self):
        kila f kwenye get_files(self):
            ukijumuisha zipfile.ZipFile(f, "w", zipfile.ZIP_DEFLATED) kama zipf:
                zipf.writestr('ones', self.data1)
                ukijumuisha zipf.open('ones') kama zopen1:
                    zopen1.read(500)
                    zipf.writestr('twos', self.data2)
            ukijumuisha zipfile.ZipFile(f, 'r') kama zipf:
                data1 = zipf.read('ones')
                data2 = zipf.read('twos')
            self.assertEqual(data1, self.data1)
            self.assertEqual(data2, self.data2)

    eleza test_many_opens(self):
        # Verify that read() na open() promptly close the file descriptor,
        # na don't rely on the garbage collector to free resources.
        self.make_test_archive(TESTFN2)
        ukijumuisha zipfile.ZipFile(TESTFN2, mode="r") kama zipf:
            kila x kwenye range(100):
                zipf.read('ones')
                ukijumuisha zipf.open('ones') kama zopen1:
                    pita
        ukijumuisha open(os.devnull) kama f:
            self.assertLess(f.fileno(), 100)

    eleza test_write_while_reading(self):
        ukijumuisha zipfile.ZipFile(TESTFN2, 'w', zipfile.ZIP_DEFLATED) kama zipf:
            zipf.writestr('ones', self.data1)
        ukijumuisha zipfile.ZipFile(TESTFN2, 'a', zipfile.ZIP_DEFLATED) kama zipf:
            ukijumuisha zipf.open('ones', 'r') kama r1:
                data1 = r1.read(500)
                ukijumuisha zipf.open('twos', 'w') kama w1:
                    w1.write(self.data2)
                data1 += r1.read()
        self.assertEqual(data1, self.data1)
        ukijumuisha zipfile.ZipFile(TESTFN2) kama zipf:
            self.assertEqual(zipf.read('twos'), self.data2)

    eleza tearDown(self):
        unlink(TESTFN2)


kundi TestWithDirectory(unittest.TestCase):
    eleza setUp(self):
        os.mkdir(TESTFN2)

    eleza test_extract_dir(self):
        ukijumuisha zipfile.ZipFile(findfile("zipdir.zip")) kama zipf:
            zipf.extractall(TESTFN2)
        self.assertKweli(os.path.isdir(os.path.join(TESTFN2, "a")))
        self.assertKweli(os.path.isdir(os.path.join(TESTFN2, "a", "b")))
        self.assertKweli(os.path.exists(os.path.join(TESTFN2, "a", "b", "c")))

    eleza test_bug_6050(self):
        # Extraction should succeed ikiwa directories already exist
        os.mkdir(os.path.join(TESTFN2, "a"))
        self.test_extract_dir()

    eleza test_write_dir(self):
        dirpath = os.path.join(TESTFN2, "x")
        os.mkdir(dirpath)
        mode = os.stat(dirpath).st_mode & 0xFFFF
        ukijumuisha zipfile.ZipFile(TESTFN, "w") kama zipf:
            zipf.write(dirpath)
            zinfo = zipf.filelist[0]
            self.assertKweli(zinfo.filename.endswith("/x/"))
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            zipf.write(dirpath, "y")
            zinfo = zipf.filelist[1]
            self.assertKweli(zinfo.filename, "y/")
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
        ukijumuisha zipfile.ZipFile(TESTFN, "r") kama zipf:
            zinfo = zipf.filelist[0]
            self.assertKweli(zinfo.filename.endswith("/x/"))
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            zinfo = zipf.filelist[1]
            self.assertKweli(zinfo.filename, "y/")
            self.assertEqual(zinfo.external_attr, (mode << 16) | 0x10)
            target = os.path.join(TESTFN2, "target")
            os.mkdir(target)
            zipf.extractall(target)
            self.assertKweli(os.path.isdir(os.path.join(target, "y")))
            self.assertEqual(len(os.listdir(target)), 2)

    eleza test_writestr_dir(self):
        os.mkdir(os.path.join(TESTFN2, "x"))
        ukijumuisha zipfile.ZipFile(TESTFN, "w") kama zipf:
            zipf.writestr("x/", b'')
            zinfo = zipf.filelist[0]
            self.assertEqual(zinfo.filename, "x/")
            self.assertEqual(zinfo.external_attr, (0o40775 << 16) | 0x10)
        ukijumuisha zipfile.ZipFile(TESTFN, "r") kama zipf:
            zinfo = zipf.filelist[0]
            self.assertKweli(zinfo.filename.endswith("x/"))
            self.assertEqual(zinfo.external_attr, (0o40775 << 16) | 0x10)
            target = os.path.join(TESTFN2, "target")
            os.mkdir(target)
            zipf.extractall(target)
            self.assertKweli(os.path.isdir(os.path.join(target, "x")))
            self.assertEqual(os.listdir(target), ["x"])

    eleza tearDown(self):
        rmtree(TESTFN2)
        ikiwa os.path.exists(TESTFN):
            unlink(TESTFN)


kundi ZipInfoTests(unittest.TestCase):
    eleza test_from_file(self):
        zi = zipfile.ZipInfo.kutoka_file(__file__)
        self.assertEqual(posixpath.basename(zi.filename), 'test_zipfile.py')
        self.assertUongo(zi.is_dir())
        self.assertEqual(zi.file_size, os.path.getsize(__file__))

    eleza test_from_file_pathlike(self):
        zi = zipfile.ZipInfo.kutoka_file(pathlib.Path(__file__))
        self.assertEqual(posixpath.basename(zi.filename), 'test_zipfile.py')
        self.assertUongo(zi.is_dir())
        self.assertEqual(zi.file_size, os.path.getsize(__file__))

    eleza test_from_file_bytes(self):
        zi = zipfile.ZipInfo.kutoka_file(os.fsencode(__file__), 'test')
        self.assertEqual(posixpath.basename(zi.filename), 'test')
        self.assertUongo(zi.is_dir())
        self.assertEqual(zi.file_size, os.path.getsize(__file__))

    eleza test_from_file_fileno(self):
        ukijumuisha open(__file__, 'rb') kama f:
            zi = zipfile.ZipInfo.kutoka_file(f.fileno(), 'test')
            self.assertEqual(posixpath.basename(zi.filename), 'test')
            self.assertUongo(zi.is_dir())
            self.assertEqual(zi.file_size, os.path.getsize(__file__))

    eleza test_from_dir(self):
        dirpath = os.path.dirname(os.path.abspath(__file__))
        zi = zipfile.ZipInfo.kutoka_file(dirpath, 'stdlib_tests')
        self.assertEqual(zi.filename, 'stdlib_tests/')
        self.assertKweli(zi.is_dir())
        self.assertEqual(zi.compress_type, zipfile.ZIP_STORED)
        self.assertEqual(zi.file_size, 0)


kundi CommandLineTest(unittest.TestCase):

    eleza zipfilecmd(self, *args, **kwargs):
        rc, out, err = script_helper.assert_python_ok('-m', 'zipfile', *args,
                                                      **kwargs)
        rudisha out.replace(os.linesep.encode(), b'\n')

    eleza zipfilecmd_failure(self, *args):
        rudisha script_helper.assert_python_failure('-m', 'zipfile', *args)

    eleza test_bad_use(self):
        rc, out, err = self.zipfilecmd_failure()
        self.assertEqual(out, b'')
        self.assertIn(b'usage', err.lower())
        self.assertIn(b'error', err.lower())
        self.assertIn(b'required', err.lower())
        rc, out, err = self.zipfilecmd_failure('-l', '')
        self.assertEqual(out, b'')
        self.assertNotEqual(err.strip(), b'')

    eleza test_test_command(self):
        zip_name = findfile('zipdir.zip')
        kila opt kwenye '-t', '--test':
            out = self.zipfilecmd(opt, zip_name)
            self.assertEqual(out.rstrip(), b'Done testing')
        zip_name = findfile('testtar.tar')
        rc, out, err = self.zipfilecmd_failure('-t', zip_name)
        self.assertEqual(out, b'')

    eleza test_list_command(self):
        zip_name = findfile('zipdir.zip')
        t = io.StringIO()
        ukijumuisha zipfile.ZipFile(zip_name, 'r') kama tf:
            tf.printdir(t)
        expected = t.getvalue().encode('ascii', 'backslashreplace')
        kila opt kwenye '-l', '--list':
            out = self.zipfilecmd(opt, zip_name,
                                  PYTHONIOENCODING='ascii:backslashreplace')
            self.assertEqual(out, expected)

    @requires_zlib
    eleza test_create_command(self):
        self.addCleanup(unlink, TESTFN)
        ukijumuisha open(TESTFN, 'w') kama f:
            f.write('test 1')
        os.mkdir(TESTFNDIR)
        self.addCleanup(rmtree, TESTFNDIR)
        ukijumuisha open(os.path.join(TESTFNDIR, 'file.txt'), 'w') kama f:
            f.write('test 2')
        files = [TESTFN, TESTFNDIR]
        namelist = [TESTFN, TESTFNDIR + '/', TESTFNDIR + '/file.txt']
        kila opt kwenye '-c', '--create':
            jaribu:
                out = self.zipfilecmd(opt, TESTFN2, *files)
                self.assertEqual(out, b'')
                ukijumuisha zipfile.ZipFile(TESTFN2) kama zf:
                    self.assertEqual(zf.namelist(), namelist)
                    self.assertEqual(zf.read(namelist[0]), b'test 1')
                    self.assertEqual(zf.read(namelist[2]), b'test 2')
            mwishowe:
                unlink(TESTFN2)

    eleza test_extract_command(self):
        zip_name = findfile('zipdir.zip')
        kila opt kwenye '-e', '--extract':
            ukijumuisha temp_dir() kama extdir:
                out = self.zipfilecmd(opt, zip_name, extdir)
                self.assertEqual(out, b'')
                ukijumuisha zipfile.ZipFile(zip_name) kama zf:
                    kila zi kwenye zf.infolist():
                        path = os.path.join(extdir,
                                    zi.filename.replace('/', os.sep))
                        ikiwa zi.is_dir():
                            self.assertKweli(os.path.isdir(path))
                        isipokua:
                            self.assertKweli(os.path.isfile(path))
                            ukijumuisha open(path, 'rb') kama f:
                                self.assertEqual(f.read(), zf.read(zi))


# Poor man's technique to consume a (smallish) iterable.
consume = tuple


eleza add_dirs(zf):
    """
    Given a writable zip file zf, inject directory entries for
    any directories implied by the presence of children.
    """
    kila name kwenye zipfile.Path._implied_dirs(zf.namelist()):
        zf.writestr(name, b"")
    rudisha zf


eleza build_alpharep_fixture():
    """
    Create a zip file ukijumuisha this structure:

    .
    ├── a.txt
    ├── b
    │   ├── c.txt
    │   ├── d
    │   │   └── e.txt
    │   └── f.txt
    └── g
        └── h
            └── i.txt

    This fixture has the following key characteristics:

    - a file at the root (a)
    - a file two levels deep (b/d/e)
    - multiple files kwenye a directory (b/c, b/f)
    - a directory containing only a directory (g/h)

    "alpha" because it uses alphabet
    "rep" because it's a representative example
    """
    data = io.BytesIO()
    zf = zipfile.ZipFile(data, "w")
    zf.writestr("a.txt", b"content of a")
    zf.writestr("b/c.txt", b"content of c")
    zf.writestr("b/d/e.txt", b"content of e")
    zf.writestr("b/f.txt", b"content of f")
    zf.writestr("g/h/i.txt", b"content of i")
    zf.filename = "alpharep.zip"
    rudisha zf


kundi TestExecutablePrependedZip(unittest.TestCase):
    """Test our ability to open zip files ukijumuisha an executable prepended."""

    eleza setUp(self):
        self.exe_zip = findfile('exe_with_zip', subdir='ziptestdata')
        self.exe_zip64 = findfile('exe_with_z64', subdir='ziptestdata')

    eleza _test_zip_works(self, name):
        # bpo-28494 sanity check: ensure is_zipfile works on these.
        self.assertKweli(zipfile.is_zipfile(name),
                        f'is_zipfile failed on {name}')
        # Ensure we can operate on these via ZipFile.
        ukijumuisha zipfile.ZipFile(name) kama zipfp:
            kila n kwenye zipfp.namelist():
                data = zipfp.read(n)
                self.assertIn(b'FAVORITE_NUMBER', data)

    eleza test_read_zip_with_exe_prepended(self):
        self._test_zip_works(self.exe_zip)

    eleza test_read_zip64_with_exe_prepended(self):
        self._test_zip_works(self.exe_zip64)

    @unittest.skipUnless(sys.executable, 'sys.executable required.')
    @unittest.skipUnless(os.access('/bin/bash', os.X_OK),
                         'Test relies on #!/bin/bash working.')
    eleza test_execute_zip2(self):
        output = subprocess.check_output([self.exe_zip, sys.executable])
        self.assertIn(b'number kwenye executable: 5', output)

    @unittest.skipUnless(sys.executable, 'sys.executable required.')
    @unittest.skipUnless(os.access('/bin/bash', os.X_OK),
                         'Test relies on #!/bin/bash working.')
    eleza test_execute_zip64(self):
        output = subprocess.check_output([self.exe_zip64, sys.executable])
        self.assertIn(b'number kwenye executable: 5', output)


kundi TestPath(unittest.TestCase):
    eleza setUp(self):
        self.fixtures = contextlib.ExitStack()
        self.addCleanup(self.fixtures.close)

    eleza zipfile_alpharep(self):
        ukijumuisha self.subTest():
            tuma build_alpharep_fixture()
        ukijumuisha self.subTest():
            tuma add_dirs(build_alpharep_fixture())

    eleza zipfile_ondisk(self):
        tmpdir = pathlib.Path(self.fixtures.enter_context(temp_dir()))
        kila alpharep kwenye self.zipfile_alpharep():
            buffer = alpharep.fp
            alpharep.close()
            path = tmpdir / alpharep.filename
            ukijumuisha path.open("wb") kama strm:
                strm.write(buffer.getvalue())
            tuma path

    eleza test_iterdir_and_types(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            assert root.is_dir()
            a, b, g = root.iterdir()
            assert a.is_file()
            assert b.is_dir()
            assert g.is_dir()
            c, f, d = b.iterdir()
            assert c.is_file() na f.is_file()
            e, = d.iterdir()
            assert e.is_file()
            h, = g.iterdir()
            i, = h.iterdir()
            assert i.is_file()

    eleza test_open(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            a, b, g = root.iterdir()
            ukijumuisha a.open() kama strm:
                data = strm.read()
            assert data == b"content of a"

    eleza test_read(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            a, b, g = root.iterdir()
            assert a.read_text() == "content of a"
            assert a.read_bytes() == b"content of a"

    eleza test_joinpath(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            a = root.joinpath("a")
            assert a.is_file()
            e = root.joinpath("b").joinpath("d").joinpath("e.txt")
            assert e.read_text() == "content of e"

    eleza test_traverse_truediv(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            a = root / "a"
            assert a.is_file()
            e = root / "b" / "d" / "e.txt"
            assert e.read_text() == "content of e"

    eleza test_pathlike_construction(self):
        """
        zipfile.Path should be constructable kutoka a path-like object
        """
        kila zipfile_ondisk kwenye self.zipfile_ondisk():
            pathlike = pathlib.Path(str(zipfile_ondisk))
            zipfile.Path(pathlike)

    eleza test_traverse_pathlike(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            root / pathlib.Path("a")

    eleza test_parent(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            assert (root / 'a').parent.at == ''
            assert (root / 'a' / 'b').parent.at == 'a/'

    eleza test_dir_parent(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            assert (root / 'b').parent.at == ''
            assert (root / 'b/').parent.at == ''

    eleza test_missing_dir_parent(self):
        kila alpharep kwenye self.zipfile_alpharep():
            root = zipfile.Path(alpharep)
            assert (root / 'missing dir/').parent.at == ''


ikiwa __name__ == "__main__":
    unittest.main()
