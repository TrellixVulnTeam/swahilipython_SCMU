# Adapted kutoka test_file.py by Daniel Stutzbach

agiza sys
agiza os
agiza io
agiza errno
agiza unittest
kutoka array agiza array
kutoka weakref agiza proxy
kutoka functools agiza wraps

kutoka test.support agiza (TESTFN, TESTFN_UNICODE, check_warnings, run_unittest,
                          make_bad_fd, cpython_only, swap_attr)
kutoka collections agiza UserList

agiza _io  # C implementation of io
agiza _pyio # Python implementation of io


kundi AutoFileTests:
    # file tests kila which a test file ni automatically set up

    eleza setUp(self):
        self.f = self.FileIO(TESTFN, 'w')

    eleza tearDown(self):
        ikiwa self.f:
            self.f.close()
        os.remove(TESTFN)

    eleza testWeakRefs(self):
        # verify weak references
        p = proxy(self.f)
        p.write(bytes(range(10)))
        self.assertEqual(self.f.tell(), p.tell())
        self.f.close()
        self.f = Tupu
        self.assertRaises(ReferenceError, getattr, p, 'tell')

    eleza testSeekTell(self):
        self.f.write(bytes(range(20)))
        self.assertEqual(self.f.tell(), 20)
        self.f.seek(0)
        self.assertEqual(self.f.tell(), 0)
        self.f.seek(10)
        self.assertEqual(self.f.tell(), 10)
        self.f.seek(5, 1)
        self.assertEqual(self.f.tell(), 15)
        self.f.seek(-5, 1)
        self.assertEqual(self.f.tell(), 10)
        self.f.seek(-5, 2)
        self.assertEqual(self.f.tell(), 15)

    eleza testAttributes(self):
        # verify expected attributes exist
        f = self.f

        self.assertEqual(f.mode, "wb")
        self.assertEqual(f.closed, Uongo)

        # verify the attributes are readonly
        kila attr kwenye 'mode', 'closed':
            self.assertRaises((AttributeError, TypeError),
                              setattr, f, attr, 'oops')

    eleza testBlksize(self):
        # test private _blksize attribute
        blksize = io.DEFAULT_BUFFER_SIZE
        # try to get preferred blksize kutoka stat.st_blksize, ikiwa available
        ikiwa hasattr(os, 'fstat'):
            fst = os.fstat(self.f.fileno())
            blksize = getattr(fst, 'st_blksize', blksize)
        self.assertEqual(self.f._blksize, blksize)

    # verify readinto
    eleza testReadintoByteArray(self):
        self.f.write(bytes([1, 2, 0, 255]))
        self.f.close()

        ba = bytearray(b'abcdefgh')
        ukijumuisha self.FileIO(TESTFN, 'r') kama f:
            n = f.readinto(ba)
        self.assertEqual(ba, b'\x01\x02\x00\xffefgh')
        self.assertEqual(n, 4)

    eleza _testReadintoMemoryview(self):
        self.f.write(bytes([1, 2, 0, 255]))
        self.f.close()

        m = memoryview(bytearray(b'abcdefgh'))
        ukijumuisha self.FileIO(TESTFN, 'r') kama f:
            n = f.readinto(m)
        self.assertEqual(m, b'\x01\x02\x00\xffefgh')
        self.assertEqual(n, 4)

        m = memoryview(bytearray(b'abcdefgh')).cast('H', shape=[2, 2])
        ukijumuisha self.FileIO(TESTFN, 'r') kama f:
            n = f.readinto(m)
        self.assertEqual(bytes(m), b'\x01\x02\x00\xffefgh')
        self.assertEqual(n, 4)

    eleza _testReadintoArray(self):
        self.f.write(bytes([1, 2, 0, 255]))
        self.f.close()

        a = array('B', b'abcdefgh')
        ukijumuisha self.FileIO(TESTFN, 'r') kama f:
            n = f.readinto(a)
        self.assertEqual(a, array('B', [1, 2, 0, 255, 101, 102, 103, 104]))
        self.assertEqual(n, 4)

        a = array('b', b'abcdefgh')
        ukijumuisha self.FileIO(TESTFN, 'r') kama f:
            n = f.readinto(a)
        self.assertEqual(a, array('b', [1, 2, 0, -1, 101, 102, 103, 104]))
        self.assertEqual(n, 4)

        a = array('I', b'abcdefgh')
        ukijumuisha self.FileIO(TESTFN, 'r') kama f:
            n = f.readinto(a)
        self.assertEqual(a, array('I', b'\x01\x02\x00\xffefgh'))
        self.assertEqual(n, 4)

    eleza testWritelinesList(self):
        l = [b'123', b'456']
        self.f.writelines(l)
        self.f.close()
        self.f = self.FileIO(TESTFN, 'rb')
        buf = self.f.read()
        self.assertEqual(buf, b'123456')

    eleza testWritelinesUserList(self):
        l = UserList([b'123', b'456'])
        self.f.writelines(l)
        self.f.close()
        self.f = self.FileIO(TESTFN, 'rb')
        buf = self.f.read()
        self.assertEqual(buf, b'123456')

    eleza testWritelinesError(self):
        self.assertRaises(TypeError, self.f.writelines, [1, 2, 3])
        self.assertRaises(TypeError, self.f.writelines, Tupu)
        self.assertRaises(TypeError, self.f.writelines, "abc")

    eleza test_none_args(self):
        self.f.write(b"hi\nbye\nabc")
        self.f.close()
        self.f = self.FileIO(TESTFN, 'r')
        self.assertEqual(self.f.read(Tupu), b"hi\nbye\nabc")
        self.f.seek(0)
        self.assertEqual(self.f.readline(Tupu), b"hi\n")
        self.assertEqual(self.f.readlines(Tupu), [b"bye\n", b"abc"])

    eleza test_reject(self):
        self.assertRaises(TypeError, self.f.write, "Hello!")

    eleza testRepr(self):
        self.assertEqual(repr(self.f),
                         "<%s.FileIO name=%r mode=%r closefd=Kweli>" %
                         (self.modulename, self.f.name, self.f.mode))
        toa self.f.name
        self.assertEqual(repr(self.f),
                         "<%s.FileIO fd=%r mode=%r closefd=Kweli>" %
                         (self.modulename, self.f.fileno(), self.f.mode))
        self.f.close()
        self.assertEqual(repr(self.f),
                         "<%s.FileIO [closed]>" % (self.modulename,))

    eleza testReprNoCloseFD(self):
        fd = os.open(TESTFN, os.O_RDONLY)
        jaribu:
            ukijumuisha self.FileIO(fd, 'r', closefd=Uongo) kama f:
                self.assertEqual(repr(f),
                                 "<%s.FileIO name=%r mode=%r closefd=Uongo>" %
                                 (self.modulename, f.name, f.mode))
        mwishowe:
            os.close(fd)

    eleza testRecursiveRepr(self):
        # Issue #25455
        ukijumuisha swap_attr(self.f, 'name', self.f):
            ukijumuisha self.assertRaises(RuntimeError):
                repr(self.f)  # Should sio crash

    eleza testErrors(self):
        f = self.f
        self.assertUongo(f.isatty())
        self.assertUongo(f.closed)
        #self.assertEqual(f.name, TESTFN)
        self.assertRaises(ValueError, f.read, 10) # Open kila reading
        f.close()
        self.assertKweli(f.closed)
        f = self.FileIO(TESTFN, 'r')
        self.assertRaises(TypeError, f.readinto, "")
        self.assertUongo(f.closed)
        f.close()
        self.assertKweli(f.closed)

    eleza testMethods(self):
        methods = ['fileno', 'isatty', 'seekable', 'readable', 'writable',
                   'read', 'readall', 'readline', 'readlines',
                   'tell', 'truncate', 'flush']

        self.f.close()
        self.assertKweli(self.f.closed)

        kila methodname kwenye methods:
            method = getattr(self.f, methodname)
            # should ashiria on closed file
            self.assertRaises(ValueError, method)

        self.assertRaises(TypeError, self.f.readinto)
        self.assertRaises(ValueError, self.f.readinto, bytearray(1))
        self.assertRaises(TypeError, self.f.seek)
        self.assertRaises(ValueError, self.f.seek, 0)
        self.assertRaises(TypeError, self.f.write)
        self.assertRaises(ValueError, self.f.write, b'')
        self.assertRaises(TypeError, self.f.writelines)
        self.assertRaises(ValueError, self.f.writelines, b'')

    eleza testOpendir(self):
        # Issue 3703: opening a directory should fill the errno
        # Windows always rudishas "[Errno 13]: Permission denied
        # Unix uses fstat na rudishas "[Errno 21]: Is a directory"
        jaribu:
            self.FileIO('.', 'r')
        tatizo OSError kama e:
            self.assertNotEqual(e.errno, 0)
            self.assertEqual(e.filename, ".")
        isipokua:
            self.fail("Should have ashiriad OSError")

    @unittest.skipIf(os.name == 'nt', "test only works on a POSIX-like system")
    eleza testOpenDirFD(self):
        fd = os.open('.', os.O_RDONLY)
        ukijumuisha self.assertRaises(OSError) kama cm:
            self.FileIO(fd, 'r')
        os.close(fd)
        self.assertEqual(cm.exception.errno, errno.EISDIR)

    #A set of functions testing that we get expected behaviour ikiwa someone has
    #manually closed the internal file descriptor.  First, a decorator:
    eleza ClosedFD(func):
        @wraps(func)
        eleza wrapper(self):
            #forcibly close the fd before invoking the problem function
            f = self.f
            os.close(f.fileno())
            jaribu:
                func(self, f)
            mwishowe:
                jaribu:
                    self.f.close()
                tatizo OSError:
                    pita
        rudisha wrapper

    eleza ClosedFDRaises(func):
        @wraps(func)
        eleza wrapper(self):
            #forcibly close the fd before invoking the problem function
            f = self.f
            os.close(f.fileno())
            jaribu:
                func(self, f)
            tatizo OSError kama e:
                self.assertEqual(e.errno, errno.EBADF)
            isipokua:
                self.fail("Should have ashiriad OSError")
            mwishowe:
                jaribu:
                    self.f.close()
                tatizo OSError:
                    pita
        rudisha wrapper

    @ClosedFDRaises
    eleza testErrnoOnClose(self, f):
        f.close()

    @ClosedFDRaises
    eleza testErrnoOnClosedWrite(self, f):
        f.write(b'a')

    @ClosedFDRaises
    eleza testErrnoOnClosedSeek(self, f):
        f.seek(0)

    @ClosedFDRaises
    eleza testErrnoOnClosedTell(self, f):
        f.tell()

    @ClosedFDRaises
    eleza testErrnoOnClosedTruncate(self, f):
        f.truncate(0)

    @ClosedFD
    eleza testErrnoOnClosedSeekable(self, f):
        f.seekable()

    @ClosedFD
    eleza testErrnoOnClosedReadable(self, f):
        f.readable()

    @ClosedFD
    eleza testErrnoOnClosedWritable(self, f):
        f.writable()

    @ClosedFD
    eleza testErrnoOnClosedFileno(self, f):
        f.fileno()

    @ClosedFD
    eleza testErrnoOnClosedIsatty(self, f):
        self.assertEqual(f.isatty(), Uongo)

    eleza ReopenForRead(self):
        jaribu:
            self.f.close()
        tatizo OSError:
            pita
        self.f = self.FileIO(TESTFN, 'r')
        os.close(self.f.fileno())
        rudisha self.f

    @ClosedFDRaises
    eleza testErrnoOnClosedRead(self, f):
        f = self.ReopenForRead()
        f.read(1)

    @ClosedFDRaises
    eleza testErrnoOnClosedReadall(self, f):
        f = self.ReopenForRead()
        f.readall()

    @ClosedFDRaises
    eleza testErrnoOnClosedReadinto(self, f):
        f = self.ReopenForRead()
        a = array('b', b'x'*10)
        f.readinto(a)

kundi CAutoFileTests(AutoFileTests, unittest.TestCase):
    FileIO = _io.FileIO
    modulename = '_io'

kundi PyAutoFileTests(AutoFileTests, unittest.TestCase):
    FileIO = _pyio.FileIO
    modulename = '_pyio'


kundi OtherFileTests:

    eleza testAbles(self):
        jaribu:
            f = self.FileIO(TESTFN, "w")
            self.assertEqual(f.readable(), Uongo)
            self.assertEqual(f.writable(), Kweli)
            self.assertEqual(f.seekable(), Kweli)
            f.close()

            f = self.FileIO(TESTFN, "r")
            self.assertEqual(f.readable(), Kweli)
            self.assertEqual(f.writable(), Uongo)
            self.assertEqual(f.seekable(), Kweli)
            f.close()

            f = self.FileIO(TESTFN, "a+")
            self.assertEqual(f.readable(), Kweli)
            self.assertEqual(f.writable(), Kweli)
            self.assertEqual(f.seekable(), Kweli)
            self.assertEqual(f.isatty(), Uongo)
            f.close()

            ikiwa sys.platform != "win32":
                jaribu:
                    f = self.FileIO("/dev/tty", "a")
                tatizo OSError:
                    # When run kwenye a cron job there just aren't any
                    # ttys, so skip the test.  This also handles other
                    # OS'es that don't support /dev/tty.
                    pita
                isipokua:
                    self.assertEqual(f.readable(), Uongo)
                    self.assertEqual(f.writable(), Kweli)
                    ikiwa sys.platform != "darwin" na \
                       'bsd' haiko kwenye sys.platform na \
                       sio sys.platform.startswith(('sunos', 'aix')):
                        # Somehow /dev/tty appears seekable on some BSDs
                        self.assertEqual(f.seekable(), Uongo)
                    self.assertEqual(f.isatty(), Kweli)
                    f.close()
        mwishowe:
            os.unlink(TESTFN)

    eleza testInvalidModeStrings(self):
        # check invalid mode strings
        kila mode kwenye ("", "aU", "wU+", "rw", "rt"):
            jaribu:
                f = self.FileIO(TESTFN, mode)
            tatizo ValueError:
                pita
            isipokua:
                f.close()
                self.fail('%r ni an invalid file mode' % mode)

    eleza testModeStrings(self):
        # test that the mode attribute ni correct kila various mode strings
        # given kama init args
        jaribu:
            kila modes kwenye [('w', 'wb'), ('wb', 'wb'), ('wb+', 'rb+'),
                          ('w+b', 'rb+'), ('a', 'ab'), ('ab', 'ab'),
                          ('ab+', 'ab+'), ('a+b', 'ab+'), ('r', 'rb'),
                          ('rb', 'rb'), ('rb+', 'rb+'), ('r+b', 'rb+')]:
                # read modes are last so that TESTFN will exist first
                ukijumuisha self.FileIO(TESTFN, modes[0]) kama f:
                    self.assertEqual(f.mode, modes[1])
        mwishowe:
            ikiwa os.path.exists(TESTFN):
                os.unlink(TESTFN)

    eleza testUnicodeOpen(self):
        # verify repr works kila unicode too
        f = self.FileIO(str(TESTFN), "w")
        f.close()
        os.unlink(TESTFN)

    eleza testBytesOpen(self):
        # Opening a bytes filename
        jaribu:
            fn = TESTFN.encode("ascii")
        tatizo UnicodeEncodeError:
            self.skipTest('could sio encode %r to ascii' % TESTFN)
        f = self.FileIO(fn, "w")
        jaribu:
            f.write(b"abc")
            f.close()
            ukijumuisha open(TESTFN, "rb") kama f:
                self.assertEqual(f.read(), b"abc")
        mwishowe:
            os.unlink(TESTFN)

    @unittest.skipIf(sys.getfilesystemencoding() != 'utf-8',
                     "test only works kila utf-8 filesystems")
    eleza testUtf8BytesOpen(self):
        # Opening a UTF-8 bytes filename
        jaribu:
            fn = TESTFN_UNICODE.encode("utf-8")
        tatizo UnicodeEncodeError:
            self.skipTest('could sio encode %r to utf-8' % TESTFN_UNICODE)
        f = self.FileIO(fn, "w")
        jaribu:
            f.write(b"abc")
            f.close()
            ukijumuisha open(TESTFN_UNICODE, "rb") kama f:
                self.assertEqual(f.read(), b"abc")
        mwishowe:
            os.unlink(TESTFN_UNICODE)

    eleza testConstructorHandlesNULChars(self):
        fn_with_NUL = 'foo\0bar'
        self.assertRaises(ValueError, self.FileIO, fn_with_NUL, 'w')
        self.assertRaises(ValueError, self.FileIO, bytes(fn_with_NUL, 'ascii'), 'w')

    eleza testInvalidFd(self):
        self.assertRaises(ValueError, self.FileIO, -10)
        self.assertRaises(OSError, self.FileIO, make_bad_fd())
        ikiwa sys.platform == 'win32':
            agiza msvcrt
            self.assertRaises(OSError, msvcrt.get_osfhandle, make_bad_fd())

    eleza testBadModeArgument(self):
        # verify that we get a sensible error message kila bad mode argument
        bad_mode = "qwerty"
        jaribu:
            f = self.FileIO(TESTFN, bad_mode)
        tatizo ValueError kama msg:
            ikiwa msg.args[0] != 0:
                s = str(msg)
                ikiwa TESTFN kwenye s ama bad_mode haiko kwenye s:
                    self.fail("bad error message kila invalid mode: %s" % s)
            # ikiwa msg.args[0] == 0, we're probably on Windows where there may be
            # no obvious way to discover why open() failed.
        isipokua:
            f.close()
            self.fail("no error kila invalid mode: %s" % bad_mode)

    eleza testTruncate(self):
        f = self.FileIO(TESTFN, 'w')
        f.write(bytes(bytearray(range(10))))
        self.assertEqual(f.tell(), 10)
        f.truncate(5)
        self.assertEqual(f.tell(), 10)
        self.assertEqual(f.seek(0, io.SEEK_END), 5)
        f.truncate(15)
        self.assertEqual(f.tell(), 5)
        self.assertEqual(f.seek(0, io.SEEK_END), 15)
        f.close()

    eleza testTruncateOnWindows(self):
        eleza bug801631():
            # SF bug <http://www.python.org/sf/801631>
            # "file.truncate fault on windows"
            f = self.FileIO(TESTFN, 'w')
            f.write(bytes(range(11)))
            f.close()

            f = self.FileIO(TESTFN,'r+')
            data = f.read(5)
            ikiwa data != bytes(range(5)):
                self.fail("Read on file opened kila update failed %r" % data)
            ikiwa f.tell() != 5:
                self.fail("File pos after read wrong %d" % f.tell())

            f.truncate()
            ikiwa f.tell() != 5:
                self.fail("File pos after ftruncate wrong %d" % f.tell())

            f.close()
            size = os.path.getsize(TESTFN)
            ikiwa size != 5:
                self.fail("File size after ftruncate wrong %d" % size)

        jaribu:
            bug801631()
        mwishowe:
            os.unlink(TESTFN)

    eleza testAppend(self):
        jaribu:
            f = open(TESTFN, 'wb')
            f.write(b'spam')
            f.close()
            f = open(TESTFN, 'ab')
            f.write(b'eggs')
            f.close()
            f = open(TESTFN, 'rb')
            d = f.read()
            f.close()
            self.assertEqual(d, b'spameggs')
        mwishowe:
            jaribu:
                os.unlink(TESTFN)
            except:
                pita

    eleza testInvalidInit(self):
        self.assertRaises(TypeError, self.FileIO, "1", 0, 0)

    eleza testWarnings(self):
        ukijumuisha check_warnings(quiet=Kweli) kama w:
            self.assertEqual(w.warnings, [])
            self.assertRaises(TypeError, self.FileIO, [])
            self.assertEqual(w.warnings, [])
            self.assertRaises(ValueError, self.FileIO, "/some/invalid/name", "rt")
            self.assertEqual(w.warnings, [])

    eleza testUnclosedFDOnException(self):
        kundi MyException(Exception): pita
        kundi MyFileIO(self.FileIO):
            eleza __setattr__(self, name, value):
                ikiwa name == "name":
                    ashiria MyException("blocked setting name")
                rudisha super(MyFileIO, self).__setattr__(name, value)
        fd = os.open(__file__, os.O_RDONLY)
        self.assertRaises(MyException, MyFileIO, fd)
        os.close(fd)  # should sio ashiria OSError(EBADF)


kundi COtherFileTests(OtherFileTests, unittest.TestCase):
    FileIO = _io.FileIO
    modulename = '_io'

    @cpython_only
    eleza testInvalidFd_overflow(self):
        # Issue 15989
        agiza _testcapi
        self.assertRaises(TypeError, self.FileIO, _testcapi.INT_MAX + 1)
        self.assertRaises(TypeError, self.FileIO, _testcapi.INT_MIN - 1)

    eleza test_open_code(self):
        # Check that the default behaviour of open_code matches
        # open("rb")
        ukijumuisha self.FileIO(__file__, "rb") kama f:
            expected = f.read()
        ukijumuisha _io.open_code(__file__) kama f:
            actual = f.read()
        self.assertEqual(expected, actual)


kundi PyOtherFileTests(OtherFileTests, unittest.TestCase):
    FileIO = _pyio.FileIO
    modulename = '_pyio'

    eleza test_open_code(self):
        # Check that the default behaviour of open_code matches
        # open("rb")
        ukijumuisha self.FileIO(__file__, "rb") kama f:
            expected = f.read()
        ukijumuisha check_warnings(quiet=Kweli) kama w:
            # Always test _open_code_with_warning
            ukijumuisha _pyio._open_code_with_warning(__file__) kama f:
                actual = f.read()
            self.assertEqual(expected, actual)
            self.assertNotEqual(w.warnings, [])


eleza test_main():
    # Historically, these tests have been sloppy about removing TESTFN.
    # So get rid of it no matter what.
    jaribu:
        run_unittest(CAutoFileTests, PyAutoFileTests,
                     COtherFileTests, PyOtherFileTests)
    mwishowe:
        ikiwa os.path.exists(TESTFN):
            os.unlink(TESTFN)

ikiwa __name__ == '__main__':
    test_main()
