"""Test largefile support on system where this makes sense.
"""

agiza os
agiza stat
agiza sys
agiza unittest
kutoka test.support agiza TESTFN, requires, unlink, bigmemtest
agiza io  # C implementation of io
agiza _pyio as pyio # Python implementation of io

# size of file to create (>2 GiB; 2 GiB == 2,147,483,648 bytes)
size = 2_500_000_000

kundi LargeFileTest:
    """Test that each file function works as expected for large
    (i.e. > 2 GiB) files.
    """

    eleza setUp(self):
        ikiwa os.path.exists(TESTFN):
            mode = 'r+b'
        else:
            mode = 'w+b'

        with self.open(TESTFN, mode) as f:
            current_size = os.fstat(f.fileno())[stat.ST_SIZE]
            ikiwa current_size == size+1:
                return

            ikiwa current_size == 0:
                f.write(b'z')

            f.seek(0)
            f.seek(size)
            f.write(b'a')
            f.flush()
            self.assertEqual(os.fstat(f.fileno())[stat.ST_SIZE], size+1)

    @classmethod
    eleza tearDownClass(cls):
        with cls.open(TESTFN, 'wb'):
            pass
        ikiwa not os.stat(TESTFN)[stat.ST_SIZE] == 0:
            raise cls.failureException('File was not truncated by opening '
                                       'with mode "wb"')

    # _pyio.FileIO.readall() uses a temporary bytearray then casted to bytes,
    # so memuse=2 is needed
    @bigmemtest(size=size, memuse=2, dry_run=False)
    eleza test_large_read(self, _size):
        # bpo-24658: Test that a read greater than 2GB does not fail.
        with self.open(TESTFN, "rb") as f:
            self.assertEqual(len(f.read()), size + 1)
            self.assertEqual(f.tell(), size + 1)

    eleza test_osstat(self):
        self.assertEqual(os.stat(TESTFN)[stat.ST_SIZE], size+1)

    eleza test_seek_read(self):
        with self.open(TESTFN, 'rb') as f:
            self.assertEqual(f.tell(), 0)
            self.assertEqual(f.read(1), b'z')
            self.assertEqual(f.tell(), 1)
            f.seek(0)
            self.assertEqual(f.tell(), 0)
            f.seek(0, 0)
            self.assertEqual(f.tell(), 0)
            f.seek(42)
            self.assertEqual(f.tell(), 42)
            f.seek(42, 0)
            self.assertEqual(f.tell(), 42)
            f.seek(42, 1)
            self.assertEqual(f.tell(), 84)
            f.seek(0, 1)
            self.assertEqual(f.tell(), 84)
            f.seek(0, 2)  # seek kutoka the end
            self.assertEqual(f.tell(), size + 1 + 0)
            f.seek(-10, 2)
            self.assertEqual(f.tell(), size + 1 - 10)
            f.seek(-size-1, 2)
            self.assertEqual(f.tell(), 0)
            f.seek(size)
            self.assertEqual(f.tell(), size)
            # the 'a' that was written at the end of file above
            self.assertEqual(f.read(1), b'a')
            f.seek(-size-1, 1)
            self.assertEqual(f.read(1), b'z')
            self.assertEqual(f.tell(), 1)

    eleza test_lseek(self):
        with self.open(TESTFN, 'rb') as f:
            self.assertEqual(os.lseek(f.fileno(), 0, 0), 0)
            self.assertEqual(os.lseek(f.fileno(), 42, 0), 42)
            self.assertEqual(os.lseek(f.fileno(), 42, 1), 84)
            self.assertEqual(os.lseek(f.fileno(), 0, 1), 84)
            self.assertEqual(os.lseek(f.fileno(), 0, 2), size+1+0)
            self.assertEqual(os.lseek(f.fileno(), -10, 2), size+1-10)
            self.assertEqual(os.lseek(f.fileno(), -size-1, 2), 0)
            self.assertEqual(os.lseek(f.fileno(), size, 0), size)
            # the 'a' that was written at the end of file above
            self.assertEqual(f.read(1), b'a')

    eleza test_truncate(self):
        with self.open(TESTFN, 'r+b') as f:
            ikiwa not hasattr(f, 'truncate'):
                raise unittest.SkipTest("open().truncate() not available "
                                        "on this system")
            f.seek(0, 2)
            # else we've lost track of the true size
            self.assertEqual(f.tell(), size+1)
            # Cut it back via seek + truncate with no argument.
            newsize = size - 10
            f.seek(newsize)
            f.truncate()
            self.assertEqual(f.tell(), newsize)  # else pointer moved
            f.seek(0, 2)
            self.assertEqual(f.tell(), newsize)  # else wasn't truncated
            # Ensure that truncate(smaller than true size) shrinks
            # the file.
            newsize -= 1
            f.seek(42)
            f.truncate(newsize)
            self.assertEqual(f.tell(), 42)
            f.seek(0, 2)
            self.assertEqual(f.tell(), newsize)
            # XXX truncate(larger than true size) is ill-defined
            # across platform; cut it waaaaay back
            f.seek(0)
            f.truncate(1)
            self.assertEqual(f.tell(), 0)       # else pointer moved
            f.seek(0)
            self.assertEqual(len(f.read()), 1)  # else wasn't truncated

    eleza test_seekable(self):
        # Issue #5016; seekable() can rudisha False when the current position
        # is negative when truncated to an int.
        for pos in (2**31-1, 2**31, 2**31+1):
            with self.open(TESTFN, 'rb') as f:
                f.seek(pos)
                self.assertTrue(f.seekable())

eleza setUpModule():
    try:
        agiza signal
        # The default handler for SIGXFSZ is to abort the process.
        # By ignoring it, system calls exceeding the file size resource
        # limit will raise OSError instead of crashing the interpreter.
        signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
    except (ImportError, AttributeError):
        pass

    # On Windows and Mac OSX this test consumes large resources; It
    # takes a long time to build the >2 GiB file and takes >2 GiB of disk
    # space therefore the resource must be enabled to run this test.
    # If not, nothing after this line stanza will be executed.
    ikiwa sys.platform[:3] == 'win' or sys.platform == 'darwin':
        requires('largefile',
                 'test requires %s bytes and a long time to run' % str(size))
    else:
        # Only run ikiwa the current filesystem supports large files.
        # (Skip this test on Windows, since we now always support
        # large files.)
        f = open(TESTFN, 'wb', buffering=0)
        try:
            # 2**31 == 2147483648
            f.seek(2147483649)
            # Seeking is not enough of a test: you must write and flush, too!
            f.write(b'x')
            f.flush()
        except (OSError, OverflowError):
            raise unittest.SkipTest("filesystem does not have "
                                    "largefile support")
        finally:
            f.close()
            unlink(TESTFN)


kundi CLargeFileTest(LargeFileTest, unittest.TestCase):
    open = staticmethod(io.open)

kundi PyLargeFileTest(LargeFileTest, unittest.TestCase):
    open = staticmethod(pyio.open)

eleza tearDownModule():
    unlink(TESTFN)

ikiwa __name__ == '__main__':
    unittest.main()
