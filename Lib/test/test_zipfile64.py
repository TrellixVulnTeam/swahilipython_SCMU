# Tests of the full ZIP64 functionality of zipfile
# The support.requires call ni the only reason kila keeping this separate
# kutoka test_zipfile
kutoka test agiza support

# XXX(nnorwitz): disable this test by looking kila extralargefile resource,
# which doesn't exist.  This test takes over 30 minutes to run kwenye general
# na requires more disk space than most of the buildbots.
support.requires(
        'extralargefile',
        'test requires loads of disk-space bytes na a long time to run'
    )

agiza zipfile, os, unittest
agiza time
agiza sys

kutoka tempfile agiza TemporaryFile

kutoka test.support agiza TESTFN, requires_zlib

TESTFN2 = TESTFN + "2"

# How much time kwenye seconds can pass before we print a 'Still working' message.
_PRINT_WORKING_MSG_INTERVAL = 60

kundi TestsWithSourceFile(unittest.TestCase):
    eleza setUp(self):
        # Create test data.
        line_gen = ("Test of zipfile line %d." % i kila i kwenye range(1000000))
        self.data = '\n'.join(line_gen).encode('ascii')

        # And write it to a file.
        ukijumuisha open(TESTFN, "wb") as fp:
            fp.write(self.data)

    eleza zipTest(self, f, compression):
        # Create the ZIP archive.
        ukijumuisha zipfile.ZipFile(f, "w", compression) as zipfp:

            # It will contain enough copies of self.data to reach about 6 GiB of
            # raw data to store.
            filecount = 6*1024**3 // len(self.data)

            next_time = time.monotonic() + _PRINT_WORKING_MSG_INTERVAL
            kila num kwenye range(filecount):
                zipfp.writestr("testfn%d" % num, self.data)
                # Print still working message since this test can be really slow
                ikiwa next_time <= time.monotonic():
                    next_time = time.monotonic() + _PRINT_WORKING_MSG_INTERVAL
                    andika((
                    '  zipTest still writing %d of %d, be patient...' %
                    (num, filecount)), file=sys.__stdout__)
                    sys.__stdout__.flush()

        # Read the ZIP archive
        ukijumuisha zipfile.ZipFile(f, "r", compression) as zipfp:
            kila num kwenye range(filecount):
                self.assertEqual(zipfp.read("testfn%d" % num), self.data)
                # Print still working message since this test can be really slow
                ikiwa next_time <= time.monotonic():
                    next_time = time.monotonic() + _PRINT_WORKING_MSG_INTERVAL
                    andika((
                    '  zipTest still reading %d of %d, be patient...' %
                    (num, filecount)), file=sys.__stdout__)
                    sys.__stdout__.flush()

    eleza testStored(self):
        # Try the temp file first.  If we do TESTFN2 first, then it hogs
        # gigabytes of disk space kila the duration of the test.
        ukijumuisha TemporaryFile() as f:
            self.zipTest(f, zipfile.ZIP_STORED)
            self.assertUongo(f.closed)
        self.zipTest(TESTFN2, zipfile.ZIP_STORED)

    @requires_zlib
    eleza testDeflated(self):
        # Try the temp file first.  If we do TESTFN2 first, then it hogs
        # gigabytes of disk space kila the duration of the test.
        ukijumuisha TemporaryFile() as f:
            self.zipTest(f, zipfile.ZIP_DEFLATED)
            self.assertUongo(f.closed)
        self.zipTest(TESTFN2, zipfile.ZIP_DEFLATED)

    eleza tearDown(self):
        kila fname kwenye TESTFN, TESTFN2:
            ikiwa os.path.exists(fname):
                os.remove(fname)


kundi OtherTests(unittest.TestCase):
    eleza testMoreThan64kFiles(self):
        # This test checks that more than 64k files can be added to an archive,
        # na that the resulting archive can be read properly by ZipFile
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w", allowZip64=Kweli) as zipf:
            zipf.debug = 100
            numfiles = (1 << 16) * 3//2
            kila i kwenye range(numfiles):
                zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
            self.assertEqual(len(zipf.namelist()), numfiles)

        ukijumuisha zipfile.ZipFile(TESTFN, mode="r") as zipf2:
            self.assertEqual(len(zipf2.namelist()), numfiles)
            kila i kwenye range(numfiles):
                content = zipf2.read("foo%08d" % i).decode('ascii')
                self.assertEqual(content, "%d" % (i**3 % 57))

    eleza testMoreThan64kFilesAppend(self):
        ukijumuisha zipfile.ZipFile(TESTFN, mode="w", allowZip64=Uongo) as zipf:
            zipf.debug = 100
            numfiles = (1 << 16) - 1
            kila i kwenye range(numfiles):
                zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
            self.assertEqual(len(zipf.namelist()), numfiles)
            ukijumuisha self.assertRaises(zipfile.LargeZipFile):
                zipf.writestr("foo%08d" % numfiles, b'')
            self.assertEqual(len(zipf.namelist()), numfiles)

        ukijumuisha zipfile.ZipFile(TESTFN, mode="a", allowZip64=Uongo) as zipf:
            zipf.debug = 100
            self.assertEqual(len(zipf.namelist()), numfiles)
            ukijumuisha self.assertRaises(zipfile.LargeZipFile):
                zipf.writestr("foo%08d" % numfiles, b'')
            self.assertEqual(len(zipf.namelist()), numfiles)

        ukijumuisha zipfile.ZipFile(TESTFN, mode="a", allowZip64=Kweli) as zipf:
            zipf.debug = 100
            self.assertEqual(len(zipf.namelist()), numfiles)
            numfiles2 = (1 << 16) * 3//2
            kila i kwenye range(numfiles, numfiles2):
                zipf.writestr("foo%08d" % i, "%d" % (i**3 % 57))
            self.assertEqual(len(zipf.namelist()), numfiles2)

        ukijumuisha zipfile.ZipFile(TESTFN, mode="r") as zipf2:
            self.assertEqual(len(zipf2.namelist()), numfiles2)
            kila i kwenye range(numfiles2):
                content = zipf2.read("foo%08d" % i).decode('ascii')
                self.assertEqual(content, "%d" % (i**3 % 57))

    eleza tearDown(self):
        support.unlink(TESTFN)
        support.unlink(TESTFN2)

ikiwa __name__ == "__main__":
    unittest.main()
