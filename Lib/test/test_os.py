# As a test suite kila the os module, this ni woefully inadequate, but this
# does add tests kila a few functions which have been determined to be more
# portable than they had been thought to be.

agiza asynchat
agiza asyncore
agiza codecs
agiza contextlib
agiza decimal
agiza errno
agiza fnmatch
agiza fractions
agiza itertools
agiza locale
agiza mmap
agiza os
agiza pickle
agiza shutil
agiza signal
agiza socket
agiza stat
agiza subprocess
agiza sys
agiza sysconfig
agiza tempfile
agiza threading
agiza time
agiza unittest
agiza uuid
agiza warnings
kutoka test agiza support
kutoka platform agiza win32_is_iot

jaribu:
    agiza resource
tatizo ImportError:
    resource = Tupu
jaribu:
    agiza fcntl
tatizo ImportError:
    fcntl = Tupu
jaribu:
    agiza _winapi
tatizo ImportError:
    _winapi = Tupu
jaribu:
    agiza pwd
    all_users = [u.pw_uid kila u kwenye pwd.getpwall()]
tatizo (ImportError, AttributeError):
    all_users = []
jaribu:
    kutoka _testcapi agiza INT_MAX, PY_SSIZE_T_MAX
tatizo ImportError:
    INT_MAX = PY_SSIZE_T_MAX = sys.maxsize

kutoka test.support.script_helper agiza assert_python_ok
kutoka test.support agiza unix_shell, FakePath


root_in_posix = Uongo
ikiwa hasattr(os, 'geteuid'):
    root_in_posix = (os.geteuid() == 0)

# Detect whether we're on a Linux system that uses the (now outdated
# na unmaintained) linuxthreads threading library.  There's an issue
# when combining linuxthreads with a failed execv call: see
# http://bugs.python.org/issue4970.
ikiwa hasattr(sys, 'thread_info') na sys.thread_info.version:
    USING_LINUXTHREADS = sys.thread_info.version.startswith("linuxthreads")
isipokua:
    USING_LINUXTHREADS = Uongo

# Issue #14110: Some tests fail on FreeBSD ikiwa the user ni kwenye the wheel group.
HAVE_WHEEL_GROUP = sys.platform.startswith('freebsd') na os.getgid() == 0


eleza requires_os_func(name):
    rudisha unittest.skipUnless(hasattr(os, name), 'requires os.%s' % name)


eleza create_file(filename, content=b'content'):
    with open(filename, "xb", 0) kama fp:
        fp.write(content)


kundi MiscTests(unittest.TestCase):
    eleza test_getcwd(self):
        cwd = os.getcwd()
        self.assertIsInstance(cwd, str)

    eleza test_getcwd_long_path(self):
        # bpo-37412: On Linux, PATH_MAX ni usually around 4096 bytes. On
        # Windows, MAX_PATH ni defined kama 260 characters, but Windows supports
        # longer path ikiwa longer paths support ni enabled. Internally, the os
        # module uses MAXPATHLEN which ni at least 1024.
        #
        # Use a directory name of 200 characters to fit into Windows MAX_PATH
        # limit.
        #
        # On Windows, the test can stop when trying to create a path longer
        # than MAX_PATH ikiwa long paths support ni disabled:
        # see RtlAreLongPathsEnabled().
        min_len = 2000   # characters
        dirlen = 200     # characters
        dirname = 'python_test_dir_'
        dirname = dirname + ('a' * (dirlen - len(dirname)))

        with tempfile.TemporaryDirectory() kama tmpdir:
            with support.change_cwd(tmpdir) kama path:
                expected = path

                wakati Kweli:
                    cwd = os.getcwd()
                    self.assertEqual(cwd, expected)

                    need = min_len - (len(cwd) + len(os.path.sep))
                    ikiwa need <= 0:
                        koma
                    ikiwa len(dirname) > need na need > 0:
                        dirname = dirname[:need]

                    path = os.path.join(path, dirname)
                    jaribu:
                        os.mkdir(path)
                        # On Windows, chdir() can fail
                        # even ikiwa mkdir() succeeded
                        os.chdir(path)
                    tatizo FileNotFoundError:
                        # On Windows, catch ERROR_PATH_NOT_FOUND (3) and
                        # ERROR_FILENAME_EXCED_RANGE (206) errors
                        # ("The filename ama extension ni too long")
                        koma
                    tatizo OSError kama exc:
                        ikiwa exc.errno == errno.ENAMETOOLONG:
                            koma
                        isipokua:
                            ashiria

                    expected = path

                ikiwa support.verbose:
                    andika(f"Tested current directory length: {len(cwd)}")

    eleza test_getcwdb(self):
        cwd = os.getcwdb()
        self.assertIsInstance(cwd, bytes)
        self.assertEqual(os.fsdecode(cwd), os.getcwd())


# Tests creating TESTFN
kundi FileTests(unittest.TestCase):
    eleza setUp(self):
        ikiwa os.path.lexists(support.TESTFN):
            os.unlink(support.TESTFN)
    tearDown = setUp

    eleza test_access(self):
        f = os.open(support.TESTFN, os.O_CREAT|os.O_RDWR)
        os.close(f)
        self.assertKweli(os.access(support.TESTFN, os.W_OK))

    eleza test_closerange(self):
        first = os.open(support.TESTFN, os.O_CREAT|os.O_RDWR)
        # We must allocate two consecutive file descriptors, otherwise
        # it will mess up other file descriptors (perhaps even the three
        # standard ones).
        second = os.dup(first)
        jaribu:
            retries = 0
            wakati second != first + 1:
                os.close(first)
                retries += 1
                ikiwa retries > 10:
                    # XXX test skipped
                    self.skipTest("couldn't allocate two consecutive fds")
                first, second = second, os.dup(second)
        mwishowe:
            os.close(second)
        # close a fd that ni open, na one that isn't
        os.closerange(first, first + 2)
        self.assertRaises(OSError, os.write, first, b"a")

    @support.cpython_only
    eleza test_rename(self):
        path = support.TESTFN
        old = sys.getrefcount(path)
        self.assertRaises(TypeError, os.rename, path, 0)
        new = sys.getrefcount(path)
        self.assertEqual(old, new)

    eleza test_read(self):
        with open(support.TESTFN, "w+b") kama fobj:
            fobj.write(b"spam")
            fobj.flush()
            fd = fobj.fileno()
            os.lseek(fd, 0, 0)
            s = os.read(fd, 4)
            self.assertEqual(type(s), bytes)
            self.assertEqual(s, b"spam")

    @support.cpython_only
    # Skip the test on 32-bit platforms: the number of bytes must fit kwenye a
    # Py_ssize_t type
    @unittest.skipUnless(INT_MAX < PY_SSIZE_T_MAX,
                         "needs INT_MAX < PY_SSIZE_T_MAX")
    @support.bigmemtest(size=INT_MAX + 10, memuse=1, dry_run=Uongo)
    eleza test_large_read(self, size):
        self.addCleanup(support.unlink, support.TESTFN)
        create_file(support.TESTFN, b'test')

        # Issue #21932: Make sure that os.read() does sio ashiria an
        # OverflowError kila size larger than INT_MAX
        with open(support.TESTFN, "rb") kama fp:
            data = os.read(fp.fileno(), size)

        # The test does sio try to read more than 2 GiB at once because the
        # operating system ni free to rudisha less bytes than requested.
        self.assertEqual(data, b'test')

    eleza test_write(self):
        # os.write() accepts bytes- na buffer-like objects but sio strings
        fd = os.open(support.TESTFN, os.O_CREAT | os.O_WRONLY)
        self.assertRaises(TypeError, os.write, fd, "beans")
        os.write(fd, b"bacon\n")
        os.write(fd, bytearray(b"eggs\n"))
        os.write(fd, memoryview(b"spam\n"))
        os.close(fd)
        with open(support.TESTFN, "rb") kama fobj:
            self.assertEqual(fobj.read().splitlines(),
                [b"bacon", b"eggs", b"spam"])

    eleza write_windows_console(self, *args):
        retcode = subprocess.call(args,
            # use a new console to sio flood the test output
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            # use a shell to hide the console window (SW_HIDE)
            shell=Kweli)
        self.assertEqual(retcode, 0)

    @unittest.skipUnless(sys.platform == 'win32',
                         'test specific to the Windows console')
    eleza test_write_windows_console(self):
        # Issue #11395: the Windows console rudishas an error (12: sio enough
        # space error) on writing into stdout ikiwa stdout mode ni binary na the
        # length ni greater than 66,000 bytes (or less, depending on heap
        # usage).
        code = "andika('x' * 100000)"
        self.write_windows_console(sys.executable, "-c", code)
        self.write_windows_console(sys.executable, "-u", "-c", code)

    eleza fdopen_helper(self, *args):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        f = os.fdopen(fd, *args)
        f.close()

    eleza test_fdopen(self):
        fd = os.open(support.TESTFN, os.O_CREAT|os.O_RDWR)
        os.close(fd)

        self.fdopen_helper()
        self.fdopen_helper('r')
        self.fdopen_helper('r', 100)

    eleza test_replace(self):
        TESTFN2 = support.TESTFN + ".2"
        self.addCleanup(support.unlink, support.TESTFN)
        self.addCleanup(support.unlink, TESTFN2)

        create_file(support.TESTFN, b"1")
        create_file(TESTFN2, b"2")

        os.replace(support.TESTFN, TESTFN2)
        self.assertRaises(FileNotFoundError, os.stat, support.TESTFN)
        with open(TESTFN2, 'r') kama f:
            self.assertEqual(f.read(), "1")

    eleza test_open_keywords(self):
        f = os.open(path=__file__, flags=os.O_RDONLY, mode=0o777,
            dir_fd=Tupu)
        os.close(f)

    eleza test_symlink_keywords(self):
        symlink = support.get_attribute(os, "symlink")
        jaribu:
            symlink(src='target', dst=support.TESTFN,
                target_is_directory=Uongo, dir_fd=Tupu)
        tatizo (NotImplementedError, OSError):
            pita  # No OS support ama unprivileged user

    @unittest.skipUnless(hasattr(os, 'copy_file_range'), 'test needs os.copy_file_range()')
    eleza test_copy_file_range_invalid_values(self):
        with self.assertRaises(ValueError):
            os.copy_file_range(0, 1, -10)

    @unittest.skipUnless(hasattr(os, 'copy_file_range'), 'test needs os.copy_file_range()')
    eleza test_copy_file_range(self):
        TESTFN2 = support.TESTFN + ".3"
        data = b'0123456789'

        create_file(support.TESTFN, data)
        self.addCleanup(support.unlink, support.TESTFN)

        in_file = open(support.TESTFN, 'rb')
        self.addCleanup(in_file.close)
        in_fd = in_file.fileno()

        out_file = open(TESTFN2, 'w+b')
        self.addCleanup(support.unlink, TESTFN2)
        self.addCleanup(out_file.close)
        out_fd = out_file.fileno()

        jaribu:
            i = os.copy_file_range(in_fd, out_fd, 5)
        tatizo OSError kama e:
            # Handle the case kwenye which Python was compiled
            # kwenye a system with the syscall but without support
            # kwenye the kernel.
            ikiwa e.errno != errno.ENOSYS:
                ashiria
            self.skipTest(e)
        isipokua:
            # The number of copied bytes can be less than
            # the number of bytes originally requested.
            self.assertIn(i, range(0, 6));

            with open(TESTFN2, 'rb') kama in_file:
                self.assertEqual(in_file.read(), data[:i])

    @unittest.skipUnless(hasattr(os, 'copy_file_range'), 'test needs os.copy_file_range()')
    eleza test_copy_file_range_offset(self):
        TESTFN4 = support.TESTFN + ".4"
        data = b'0123456789'
        bytes_to_copy = 6
        in_skip = 3
        out_seek = 5

        create_file(support.TESTFN, data)
        self.addCleanup(support.unlink, support.TESTFN)

        in_file = open(support.TESTFN, 'rb')
        self.addCleanup(in_file.close)
        in_fd = in_file.fileno()

        out_file = open(TESTFN4, 'w+b')
        self.addCleanup(support.unlink, TESTFN4)
        self.addCleanup(out_file.close)
        out_fd = out_file.fileno()

        jaribu:
            i = os.copy_file_range(in_fd, out_fd, bytes_to_copy,
                                   offset_src=in_skip,
                                   offset_dst=out_seek)
        tatizo OSError kama e:
            # Handle the case kwenye which Python was compiled
            # kwenye a system with the syscall but without support
            # kwenye the kernel.
            ikiwa e.errno != errno.ENOSYS:
                ashiria
            self.skipTest(e)
        isipokua:
            # The number of copied bytes can be less than
            # the number of bytes originally requested.
            self.assertIn(i, range(0, bytes_to_copy+1));

            with open(TESTFN4, 'rb') kama in_file:
                read = in_file.read()
            # seeked bytes (5) are zero'ed
            self.assertEqual(read[:out_seek], b'\x00'*out_seek)
            # 012 are skipped (in_skip)
            # 345678 are copied kwenye the file (in_skip + bytes_to_copy)
            self.assertEqual(read[out_seek:],
                             data[in_skip:in_skip+i])

# Test attributes on rudisha values kutoka os.*stat* family.
kundi StatAttributeTests(unittest.TestCase):
    eleza setUp(self):
        self.fname = support.TESTFN
        self.addCleanup(support.unlink, self.fname)
        create_file(self.fname, b"ABC")

    eleza check_stat_attributes(self, fname):
        result = os.stat(fname)

        # Make sure direct access works
        self.assertEqual(result[stat.ST_SIZE], 3)
        self.assertEqual(result.st_size, 3)

        # Make sure all the attributes are there
        members = dir(result)
        kila name kwenye dir(stat):
            ikiwa name[:3] == 'ST_':
                attr = name.lower()
                ikiwa name.endswith("TIME"):
                    eleza trunc(x): rudisha int(x)
                isipokua:
                    eleza trunc(x): rudisha x
                self.assertEqual(trunc(getattr(result, attr)),
                                  result[getattr(stat, name)])
                self.assertIn(attr, members)

        # Make sure that the st_?time na st_?time_ns fields roughly agree
        # (they should always agree up to around tens-of-microseconds)
        kila name kwenye 'st_atime st_mtime st_ctime'.split():
            floaty = int(getattr(result, name) * 100000)
            nanosecondy = getattr(result, name + "_ns") // 10000
            self.assertAlmostEqual(floaty, nanosecondy, delta=2)

        jaribu:
            result[200]
            self.fail("No exception ashiriad")
        tatizo IndexError:
            pita

        # Make sure that assignment fails
        jaribu:
            result.st_mode = 1
            self.fail("No exception ashiriad")
        tatizo AttributeError:
            pita

        jaribu:
            result.st_rdev = 1
            self.fail("No exception ashiriad")
        tatizo (AttributeError, TypeError):
            pita

        jaribu:
            result.parrot = 1
            self.fail("No exception ashiriad")
        tatizo AttributeError:
            pita

        # Use the stat_result constructor with a too-short tuple.
        jaribu:
            result2 = os.stat_result((10,))
            self.fail("No exception ashiriad")
        tatizo TypeError:
            pita

        # Use the constructor with a too-long tuple.
        jaribu:
            result2 = os.stat_result((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14))
        tatizo TypeError:
            pita

    eleza test_stat_attributes(self):
        self.check_stat_attributes(self.fname)

    eleza test_stat_attributes_bytes(self):
        jaribu:
            fname = self.fname.encode(sys.getfilesystemencoding())
        tatizo UnicodeEncodeError:
            self.skipTest("cannot encode %a kila the filesystem" % self.fname)
        self.check_stat_attributes(fname)

    eleza test_stat_result_pickle(self):
        result = os.stat(self.fname)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(result, proto)
            self.assertIn(b'stat_result', p)
            ikiwa proto < 4:
                self.assertIn(b'cos\nstat_result\n', p)
            unpickled = pickle.loads(p)
            self.assertEqual(result, unpickled)

    @unittest.skipUnless(hasattr(os, 'statvfs'), 'test needs os.statvfs()')
    eleza test_statvfs_attributes(self):
        result = os.statvfs(self.fname)

        # Make sure direct access works
        self.assertEqual(result.f_bfree, result[3])

        # Make sure all the attributes are there.
        members = ('bsize', 'frsize', 'blocks', 'bfree', 'bavail', 'files',
                    'ffree', 'favail', 'flag', 'namemax')
        kila value, member kwenye enumerate(members):
            self.assertEqual(getattr(result, 'f_' + member), result[value])

        self.assertKweli(isinstance(result.f_fsid, int))

        # Test that the size of the tuple doesn't change
        self.assertEqual(len(result), 10)

        # Make sure that assignment really fails
        jaribu:
            result.f_bfree = 1
            self.fail("No exception ashiriad")
        tatizo AttributeError:
            pita

        jaribu:
            result.parrot = 1
            self.fail("No exception ashiriad")
        tatizo AttributeError:
            pita

        # Use the constructor with a too-short tuple.
        jaribu:
            result2 = os.statvfs_result((10,))
            self.fail("No exception ashiriad")
        tatizo TypeError:
            pita

        # Use the constructor with a too-long tuple.
        jaribu:
            result2 = os.statvfs_result((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14))
        tatizo TypeError:
            pita

    @unittest.skipUnless(hasattr(os, 'statvfs'),
                         "need os.statvfs()")
    eleza test_statvfs_result_pickle(self):
        result = os.statvfs(self.fname)

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            p = pickle.dumps(result, proto)
            self.assertIn(b'statvfs_result', p)
            ikiwa proto < 4:
                self.assertIn(b'cos\nstatvfs_result\n', p)
            unpickled = pickle.loads(p)
            self.assertEqual(result, unpickled)

    @unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
    eleza test_1686475(self):
        # Verify that an open file can be stat'ed
        jaribu:
            os.stat(r"c:\pagefile.sys")
        tatizo FileNotFoundError:
            self.skipTest(r'c:\pagefile.sys does sio exist')
        tatizo OSError kama e:
            self.fail("Could sio stat pagefile.sys")

    @unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
    @unittest.skipUnless(hasattr(os, "pipe"), "requires os.pipe()")
    eleza test_15261(self):
        # Verify that stat'ing a closed fd does sio cause crash
        r, w = os.pipe()
        jaribu:
            os.stat(r)          # should sio ashiria error
        mwishowe:
            os.close(r)
            os.close(w)
        with self.assertRaises(OSError) kama ctx:
            os.stat(r)
        self.assertEqual(ctx.exception.errno, errno.EBADF)

    eleza check_file_attributes(self, result):
        self.assertKweli(hasattr(result, 'st_file_attributes'))
        self.assertKweli(isinstance(result.st_file_attributes, int))
        self.assertKweli(0 <= result.st_file_attributes <= 0xFFFFFFFF)

    @unittest.skipUnless(sys.platform == "win32",
                         "st_file_attributes ni Win32 specific")
    eleza test_file_attributes(self):
        # test file st_file_attributes (FILE_ATTRIBUTE_DIRECTORY sio set)
        result = os.stat(self.fname)
        self.check_file_attributes(result)
        self.assertEqual(
            result.st_file_attributes & stat.FILE_ATTRIBUTE_DIRECTORY,
            0)

        # test directory st_file_attributes (FILE_ATTRIBUTE_DIRECTORY set)
        dirname = support.TESTFN + "dir"
        os.mkdir(dirname)
        self.addCleanup(os.rmdir, dirname)

        result = os.stat(dirname)
        self.check_file_attributes(result)
        self.assertEqual(
            result.st_file_attributes & stat.FILE_ATTRIBUTE_DIRECTORY,
            stat.FILE_ATTRIBUTE_DIRECTORY)

    @unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
    eleza test_access_denied(self):
        # Default to FindFirstFile WIN32_FIND_DATA when access is
        # denied. See issue 28075.
        # os.environ['TEMP'] should be located on a volume that
        # supports file ACLs.
        fname = os.path.join(os.environ['TEMP'], self.fname)
        self.addCleanup(support.unlink, fname)
        create_file(fname, b'ABC')
        # Deny the right to [S]YNCHRONIZE on the file to
        # force CreateFile to fail with ERROR_ACCESS_DENIED.
        DETACHED_PROCESS = 8
        subprocess.check_call(
            # bpo-30584: Use security identifier *S-1-5-32-545 instead
            # of localized "Users" to sio depend on the locale.
            ['icacls.exe', fname, '/deny', '*S-1-5-32-545:(S)'],
            creationflags=DETACHED_PROCESS
        )
        result = os.stat(fname)
        self.assertNotEqual(result.st_size, 0)

    @unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
    eleza test_stat_block_device(self):
        # bpo-38030: os.stat fails kila block devices
        # Test a filename like "//./C:"
        fname = "//./" + os.path.splitdrive(os.getcwd())[0]
        result = os.stat(fname)
        self.assertEqual(result.st_mode, stat.S_IFBLK)


kundi UtimeTests(unittest.TestCase):
    eleza setUp(self):
        self.dirname = support.TESTFN
        self.fname = os.path.join(self.dirname, "f1")

        self.addCleanup(support.rmtree, self.dirname)
        os.mkdir(self.dirname)
        create_file(self.fname)

    eleza support_subsecond(self, filename):
        # Heuristic to check ikiwa the filesystem supports timestamp with
        # subsecond resolution: check ikiwa float na int timestamps are different
        st = os.stat(filename)
        rudisha ((st.st_atime != st[7])
                ama (st.st_mtime != st[8])
                ama (st.st_ctime != st[9]))

    eleza _test_utime(self, set_time, filename=Tupu):
        ikiwa sio filename:
            filename = self.fname

        support_subsecond = self.support_subsecond(filename)
        ikiwa support_subsecond:
            # Timestamp with a resolution of 1 microsecond (10^-6).
            #
            # The resolution of the C internal function used by os.utime()
            # depends on the platform: 1 sec, 1 us, 1 ns. Writing a portable
            # test with a resolution of 1 ns requires more work:
            # see the issue #15745.
            atime_ns = 1002003000   # 1.002003 seconds
            mtime_ns = 4005006000   # 4.005006 seconds
        isipokua:
            # use a resolution of 1 second
            atime_ns = 5 * 10**9
            mtime_ns = 8 * 10**9

        set_time(filename, (atime_ns, mtime_ns))
        st = os.stat(filename)

        ikiwa support_subsecond:
            self.assertAlmostEqual(st.st_atime, atime_ns * 1e-9, delta=1e-6)
            self.assertAlmostEqual(st.st_mtime, mtime_ns * 1e-9, delta=1e-6)
        isipokua:
            self.assertEqual(st.st_atime, atime_ns * 1e-9)
            self.assertEqual(st.st_mtime, mtime_ns * 1e-9)
        self.assertEqual(st.st_atime_ns, atime_ns)
        self.assertEqual(st.st_mtime_ns, mtime_ns)

    eleza test_utime(self):
        eleza set_time(filename, ns):
            # test the ns keyword parameter
            os.utime(filename, ns=ns)
        self._test_utime(set_time)

    @staticmethod
    eleza ns_to_sec(ns):
        # Convert a number of nanosecond (int) to a number of seconds (float).
        # Round towards infinity by adding 0.5 nanosecond to avoid rounding
        # issue, os.utime() rounds towards minus infinity.
        rudisha (ns * 1e-9) + 0.5e-9

    eleza test_utime_by_indexed(self):
        # pita times kama floating point seconds kama the second indexed parameter
        eleza set_time(filename, ns):
            atime_ns, mtime_ns = ns
            atime = self.ns_to_sec(atime_ns)
            mtime = self.ns_to_sec(mtime_ns)
            # test utimensat(timespec), utimes(timeval), utime(utimbuf)
            # ama utime(time_t)
            os.utime(filename, (atime, mtime))
        self._test_utime(set_time)

    eleza test_utime_by_times(self):
        eleza set_time(filename, ns):
            atime_ns, mtime_ns = ns
            atime = self.ns_to_sec(atime_ns)
            mtime = self.ns_to_sec(mtime_ns)
            # test the times keyword parameter
            os.utime(filename, times=(atime, mtime))
        self._test_utime(set_time)

    @unittest.skipUnless(os.utime kwenye os.supports_follow_symlinks,
                         "follow_symlinks support kila utime required "
                         "kila this test.")
    eleza test_utime_nofollow_symlinks(self):
        eleza set_time(filename, ns):
            # use follow_symlinks=Uongo to test utimensat(timespec)
            # ama lutimes(timeval)
            os.utime(filename, ns=ns, follow_symlinks=Uongo)
        self._test_utime(set_time)

    @unittest.skipUnless(os.utime kwenye os.supports_fd,
                         "fd support kila utime required kila this test.")
    eleza test_utime_fd(self):
        eleza set_time(filename, ns):
            with open(filename, 'wb', 0) kama fp:
                # use a file descriptor to test futimens(timespec)
                # ama futimes(timeval)
                os.utime(fp.fileno(), ns=ns)
        self._test_utime(set_time)

    @unittest.skipUnless(os.utime kwenye os.supports_dir_fd,
                         "dir_fd support kila utime required kila this test.")
    eleza test_utime_dir_fd(self):
        eleza set_time(filename, ns):
            dirname, name = os.path.split(filename)
            dirfd = os.open(dirname, os.O_RDONLY)
            jaribu:
                # pita dir_fd to test utimensat(timespec) ama futimesat(timeval)
                os.utime(name, dir_fd=dirfd, ns=ns)
            mwishowe:
                os.close(dirfd)
        self._test_utime(set_time)

    eleza test_utime_directory(self):
        eleza set_time(filename, ns):
            # test calling os.utime() on a directory
            os.utime(filename, ns=ns)
        self._test_utime(set_time, filename=self.dirname)

    eleza _test_utime_current(self, set_time):
        # Get the system clock
        current = time.time()

        # Call os.utime() to set the timestamp to the current system clock
        set_time(self.fname)

        ikiwa sio self.support_subsecond(self.fname):
            delta = 1.0
        isipokua:
            # On Windows, the usual resolution of time.time() ni 15.6 ms.
            # bpo-30649: Tolerate 50 ms kila slow Windows buildbots.
            #
            # x86 Gentoo Refleaks 3.x once failed with dt=20.2 ms. So use
            # also 50 ms on other platforms.
            delta = 0.050
        st = os.stat(self.fname)
        msg = ("st_time=%r, current=%r, dt=%r"
               % (st.st_mtime, current, st.st_mtime - current))
        self.assertAlmostEqual(st.st_mtime, current,
                               delta=delta, msg=msg)

    eleza test_utime_current(self):
        eleza set_time(filename):
            # Set to the current time kwenye the new way
            os.utime(self.fname)
        self._test_utime_current(set_time)

    eleza test_utime_current_old(self):
        eleza set_time(filename):
            # Set to the current time kwenye the old explicit way.
            os.utime(self.fname, Tupu)
        self._test_utime_current(set_time)

    eleza get_file_system(self, path):
        ikiwa sys.platform == 'win32':
            root = os.path.splitdrive(os.path.abspath(path))[0] + '\\'
            agiza ctypes
            kernel32 = ctypes.windll.kernel32
            buf = ctypes.create_unicode_buffer("", 100)
            ok = kernel32.GetVolumeInformationW(root, Tupu, 0,
                                                Tupu, Tupu, Tupu,
                                                buf, len(buf))
            ikiwa ok:
                rudisha buf.value
        # rudisha Tupu ikiwa the filesystem ni unknown

    eleza test_large_time(self):
        # Many filesystems are limited to the year 2038. At least, the test
        # pita with NTFS filesystem.
        ikiwa self.get_file_system(self.dirname) != "NTFS":
            self.skipTest("requires NTFS")

        large = 5000000000   # some day kwenye 2128
        os.utime(self.fname, (large, large))
        self.assertEqual(os.stat(self.fname).st_mtime, large)

    eleza test_utime_invalid_arguments(self):
        # seconds na nanoseconds parameters are mutually exclusive
        with self.assertRaises(ValueError):
            os.utime(self.fname, (5, 5), ns=(5, 5))
        with self.assertRaises(TypeError):
            os.utime(self.fname, [5, 5])
        with self.assertRaises(TypeError):
            os.utime(self.fname, (5,))
        with self.assertRaises(TypeError):
            os.utime(self.fname, (5, 5, 5))
        with self.assertRaises(TypeError):
            os.utime(self.fname, ns=[5, 5])
        with self.assertRaises(TypeError):
            os.utime(self.fname, ns=(5,))
        with self.assertRaises(TypeError):
            os.utime(self.fname, ns=(5, 5, 5))

        ikiwa os.utime haiko kwenye os.supports_follow_symlinks:
            with self.assertRaises(NotImplementedError):
                os.utime(self.fname, (5, 5), follow_symlinks=Uongo)
        ikiwa os.utime haiko kwenye os.supports_fd:
            with open(self.fname, 'wb', 0) kama fp:
                with self.assertRaises(TypeError):
                    os.utime(fp.fileno(), (5, 5))
        ikiwa os.utime haiko kwenye os.supports_dir_fd:
            with self.assertRaises(NotImplementedError):
                os.utime(self.fname, (5, 5), dir_fd=0)

    @support.cpython_only
    eleza test_issue31577(self):
        # The interpreter shouldn't crash kwenye case utime() received a bad
        # ns argument.
        eleza get_bad_int(divmod_ret_val):
            kundi BadInt:
                eleza __divmod__(*args):
                    rudisha divmod_ret_val
            rudisha BadInt()
        with self.assertRaises(TypeError):
            os.utime(self.fname, ns=(get_bad_int(42), 1))
        with self.assertRaises(TypeError):
            os.utime(self.fname, ns=(get_bad_int(()), 1))
        with self.assertRaises(TypeError):
            os.utime(self.fname, ns=(get_bad_int((1, 2, 3)), 1))


kutoka test agiza mapping_tests

kundi EnvironTests(mapping_tests.BasicTestMappingProtocol):
    """check that os.environ object conform to mapping protocol"""
    type2test = Tupu

    eleza setUp(self):
        self.__save = dict(os.environ)
        ikiwa os.supports_bytes_environ:
            self.__saveb = dict(os.environb)
        kila key, value kwenye self._reference().items():
            os.environ[key] = value

    eleza tearDown(self):
        os.environ.clear()
        os.environ.update(self.__save)
        ikiwa os.supports_bytes_environ:
            os.environb.clear()
            os.environb.update(self.__saveb)

    eleza _reference(self):
        rudisha {"KEY1":"VALUE1", "KEY2":"VALUE2", "KEY3":"VALUE3"}

    eleza _empty_mapping(self):
        os.environ.clear()
        rudisha os.environ

    # Bug 1110478
    @unittest.skipUnless(unix_shell na os.path.exists(unix_shell),
                         'requires a shell')
    eleza test_update2(self):
        os.environ.clear()
        os.environ.update(HELLO="World")
        with os.popen("%s -c 'echo $HELLO'" % unix_shell) kama popen:
            value = popen.read().strip()
            self.assertEqual(value, "World")

    @unittest.skipUnless(unix_shell na os.path.exists(unix_shell),
                         'requires a shell')
    eleza test_os_popen_iter(self):
        with os.popen("%s -c 'echo \"line1\nline2\nline3\"'"
                      % unix_shell) kama popen:
            it = iter(popen)
            self.assertEqual(next(it), "line1\n")
            self.assertEqual(next(it), "line2\n")
            self.assertEqual(next(it), "line3\n")
            self.assertRaises(StopIteration, next, it)

    # Verify environ keys na values kutoka the OS are of the
    # correct str type.
    eleza test_keyvalue_types(self):
        kila key, val kwenye os.environ.items():
            self.assertEqual(type(key), str)
            self.assertEqual(type(val), str)

    eleza test_items(self):
        kila key, value kwenye self._reference().items():
            self.assertEqual(os.environ.get(key), value)

    # Issue 7310
    eleza test___repr__(self):
        """Check that the repr() of os.environ looks like environ({...})."""
        env = os.environ
        self.assertEqual(repr(env), 'environ({{{}}})'.format(', '.join(
            '{!r}: {!r}'.format(key, value)
            kila key, value kwenye env.items())))

    eleza test_get_exec_path(self):
        defpath_list = os.defpath.split(os.pathsep)
        test_path = ['/monty', '/python', '', '/flying/circus']
        test_env = {'PATH': os.pathsep.join(test_path)}

        saved_environ = os.environ
        jaribu:
            os.environ = dict(test_env)
            # Test that defaulting to os.environ works.
            self.assertSequenceEqual(test_path, os.get_exec_path())
            self.assertSequenceEqual(test_path, os.get_exec_path(env=Tupu))
        mwishowe:
            os.environ = saved_environ

        # No PATH environment variable
        self.assertSequenceEqual(defpath_list, os.get_exec_path({}))
        # Empty PATH environment variable
        self.assertSequenceEqual(('',), os.get_exec_path({'PATH':''}))
        # Supplied PATH environment variable
        self.assertSequenceEqual(test_path, os.get_exec_path(test_env))

        ikiwa os.supports_bytes_environ:
            # env cannot contain 'PATH' na b'PATH' keys
            jaribu:
                # ignore BytesWarning warning
                with warnings.catch_warnings(record=Kweli):
                    mixed_env = {'PATH': '1', b'PATH': b'2'}
            tatizo BytesWarning:
                # mixed_env cannot be created with python -bb
                pita
            isipokua:
                self.assertRaises(ValueError, os.get_exec_path, mixed_env)

            # bytes key and/or value
            self.assertSequenceEqual(os.get_exec_path({b'PATH': b'abc'}),
                ['abc'])
            self.assertSequenceEqual(os.get_exec_path({b'PATH': 'abc'}),
                ['abc'])
            self.assertSequenceEqual(os.get_exec_path({'PATH': b'abc'}),
                ['abc'])

    @unittest.skipUnless(os.supports_bytes_environ,
                         "os.environb required kila this test.")
    eleza test_environb(self):
        # os.environ -> os.environb
        value = 'euro\u20ac'
        jaribu:
            value_bytes = value.encode(sys.getfilesystemencoding(),
                                       'surrogateescape')
        tatizo UnicodeEncodeError:
            msg = "U+20AC character ni sio encodable to %s" % (
                sys.getfilesystemencoding(),)
            self.skipTest(msg)
        os.environ['unicode'] = value
        self.assertEqual(os.environ['unicode'], value)
        self.assertEqual(os.environb[b'unicode'], value_bytes)

        # os.environb -> os.environ
        value = b'\xff'
        os.environb[b'bytes'] = value
        self.assertEqual(os.environb[b'bytes'], value)
        value_str = value.decode(sys.getfilesystemencoding(), 'surrogateescape')
        self.assertEqual(os.environ['bytes'], value_str)

    # On OS X < 10.6, unsetenv() doesn't rudisha a value (bpo-13415).
    @support.requires_mac_ver(10, 6)
    eleza test_unset_error(self):
        ikiwa sys.platform == "win32":
            # an environment variable ni limited to 32,767 characters
            key = 'x' * 50000
            self.assertRaises(ValueError, os.environ.__delitem__, key)
        isipokua:
            # "=" ni sio allowed kwenye a variable name
            key = 'key='
            self.assertRaises(OSError, os.environ.__delitem__, key)

    eleza test_key_type(self):
        missing = 'missingkey'
        self.assertNotIn(missing, os.environ)

        with self.assertRaises(KeyError) kama cm:
            os.environ[missing]
        self.assertIs(cm.exception.args[0], missing)
        self.assertKweli(cm.exception.__suppress_context__)

        with self.assertRaises(KeyError) kama cm:
            toa os.environ[missing]
        self.assertIs(cm.exception.args[0], missing)
        self.assertKweli(cm.exception.__suppress_context__)

    eleza _test_environ_iteration(self, collection):
        iterator = iter(collection)
        new_key = "__new_key__"

        next(iterator)  # start iteration over os.environ.items

        # add a new key kwenye os.environ mapping
        os.environ[new_key] = "test_environ_iteration"

        jaribu:
            next(iterator)  # force iteration over modified mapping
            self.assertEqual(os.environ[new_key], "test_environ_iteration")
        mwishowe:
            toa os.environ[new_key]

    eleza test_iter_error_when_changing_os_environ(self):
        self._test_environ_iteration(os.environ)

    eleza test_iter_error_when_changing_os_environ_items(self):
        self._test_environ_iteration(os.environ.items())

    eleza test_iter_error_when_changing_os_environ_values(self):
        self._test_environ_iteration(os.environ.values())


kundi WalkTests(unittest.TestCase):
    """Tests kila os.walk()."""

    # Wrapper to hide minor differences between os.walk na os.fwalk
    # to tests both functions with the same code base
    eleza walk(self, top, **kwargs):
        ikiwa 'follow_symlinks' kwenye kwargs:
            kwargs['followlinks'] = kwargs.pop('follow_symlinks')
        rudisha os.walk(top, **kwargs)

    eleza setUp(self):
        join = os.path.join
        self.addCleanup(support.rmtree, support.TESTFN)

        # Build:
        #     TESTFN/
        #       TEST1/              a file kid na two directory kids
        #         tmp1
        #         SUB1/             a file kid na a directory kid
        #           tmp2
        #           SUB11/          no kids
        #         SUB2/             a file kid na a dirsymlink kid
        #           tmp3
        #           SUB21/          sio readable
        #             tmp5
        #           link/           a symlink to TESTFN.2
        #           broken_link
        #           broken_link2
        #           broken_link3
        #       TEST2/
        #         tmp4              a lone file
        self.walk_path = join(support.TESTFN, "TEST1")
        self.sub1_path = join(self.walk_path, "SUB1")
        self.sub11_path = join(self.sub1_path, "SUB11")
        sub2_path = join(self.walk_path, "SUB2")
        sub21_path = join(sub2_path, "SUB21")
        tmp1_path = join(self.walk_path, "tmp1")
        tmp2_path = join(self.sub1_path, "tmp2")
        tmp3_path = join(sub2_path, "tmp3")
        tmp5_path = join(sub21_path, "tmp3")
        self.link_path = join(sub2_path, "link")
        t2_path = join(support.TESTFN, "TEST2")
        tmp4_path = join(support.TESTFN, "TEST2", "tmp4")
        broken_link_path = join(sub2_path, "broken_link")
        broken_link2_path = join(sub2_path, "broken_link2")
        broken_link3_path = join(sub2_path, "broken_link3")

        # Create stuff.
        os.makedirs(self.sub11_path)
        os.makedirs(sub2_path)
        os.makedirs(sub21_path)
        os.makedirs(t2_path)

        kila path kwenye tmp1_path, tmp2_path, tmp3_path, tmp4_path, tmp5_path:
            with open(path, "x") kama f:
                f.write("I'm " + path + " na proud of it.  Blame test_os.\n")

        ikiwa support.can_symlink():
            os.symlink(os.path.abspath(t2_path), self.link_path)
            os.symlink('broken', broken_link_path, Kweli)
            os.symlink(join('tmp3', 'broken'), broken_link2_path, Kweli)
            os.symlink(join('SUB21', 'tmp5'), broken_link3_path, Kweli)
            self.sub2_tree = (sub2_path, ["SUB21", "link"],
                              ["broken_link", "broken_link2", "broken_link3",
                               "tmp3"])
        isipokua:
            self.sub2_tree = (sub2_path, ["SUB21"], ["tmp3"])

        os.chmod(sub21_path, 0)
        jaribu:
            os.listdir(sub21_path)
        tatizo PermissionError:
            self.addCleanup(os.chmod, sub21_path, stat.S_IRWXU)
        isipokua:
            os.chmod(sub21_path, stat.S_IRWXU)
            os.unlink(tmp5_path)
            os.rmdir(sub21_path)
            toa self.sub2_tree[1][:1]

    eleza test_walk_topdown(self):
        # Walk top-down.
        all = list(self.walk(self.walk_path))

        self.assertEqual(len(all), 4)
        # We can't know which order SUB1 na SUB2 will appear in.
        # Not flipped:  TESTFN, SUB1, SUB11, SUB2
        #     flipped:  TESTFN, SUB2, SUB1, SUB11
        flipped = all[0][1][0] != "SUB1"
        all[0][1].sort()
        all[3 - 2 * flipped][-1].sort()
        all[3 - 2 * flipped][1].sort()
        self.assertEqual(all[0], (self.walk_path, ["SUB1", "SUB2"], ["tmp1"]))
        self.assertEqual(all[1 + flipped], (self.sub1_path, ["SUB11"], ["tmp2"]))
        self.assertEqual(all[2 + flipped], (self.sub11_path, [], []))
        self.assertEqual(all[3 - 2 * flipped], self.sub2_tree)

    eleza test_walk_prune(self, walk_path=Tupu):
        ikiwa walk_path ni Tupu:
            walk_path = self.walk_path
        # Prune the search.
        all = []
        kila root, dirs, files kwenye self.walk(walk_path):
            all.append((root, dirs, files))
            # Don't descend into SUB1.
            ikiwa 'SUB1' kwenye dirs:
                # Note that this also mutates the dirs we appended to all!
                dirs.remove('SUB1')

        self.assertEqual(len(all), 2)
        self.assertEqual(all[0], (self.walk_path, ["SUB2"], ["tmp1"]))

        all[1][-1].sort()
        all[1][1].sort()
        self.assertEqual(all[1], self.sub2_tree)

    eleza test_file_like_path(self):
        self.test_walk_prune(FakePath(self.walk_path))

    eleza test_walk_bottom_up(self):
        # Walk bottom-up.
        all = list(self.walk(self.walk_path, topdown=Uongo))

        self.assertEqual(len(all), 4, all)
        # We can't know which order SUB1 na SUB2 will appear in.
        # Not flipped:  SUB11, SUB1, SUB2, TESTFN
        #     flipped:  SUB2, SUB11, SUB1, TESTFN
        flipped = all[3][1][0] != "SUB1"
        all[3][1].sort()
        all[2 - 2 * flipped][-1].sort()
        all[2 - 2 * flipped][1].sort()
        self.assertEqual(all[3],
                         (self.walk_path, ["SUB1", "SUB2"], ["tmp1"]))
        self.assertEqual(all[flipped],
                         (self.sub11_path, [], []))
        self.assertEqual(all[flipped + 1],
                         (self.sub1_path, ["SUB11"], ["tmp2"]))
        self.assertEqual(all[2 - 2 * flipped],
                         self.sub2_tree)

    eleza test_walk_symlink(self):
        ikiwa sio support.can_symlink():
            self.skipTest("need symlink support")

        # Walk, following symlinks.
        walk_it = self.walk(self.walk_path, follow_symlinks=Kweli)
        kila root, dirs, files kwenye walk_it:
            ikiwa root == self.link_path:
                self.assertEqual(dirs, [])
                self.assertEqual(files, ["tmp4"])
                koma
        isipokua:
            self.fail("Didn't follow symlink with followlinks=Kweli")

    eleza test_walk_bad_dir(self):
        # Walk top-down.
        errors = []
        walk_it = self.walk(self.walk_path, onerror=errors.append)
        root, dirs, files = next(walk_it)
        self.assertEqual(errors, [])
        dir1 = 'SUB1'
        path1 = os.path.join(root, dir1)
        path1new = os.path.join(root, dir1 + '.new')
        os.rename(path1, path1new)
        jaribu:
            roots = [r kila r, d, f kwenye walk_it]
            self.assertKweli(errors)
            self.assertNotIn(path1, roots)
            self.assertNotIn(path1new, roots)
            kila dir2 kwenye dirs:
                ikiwa dir2 != dir1:
                    self.assertIn(os.path.join(root, dir2), roots)
        mwishowe:
            os.rename(path1new, path1)

    eleza test_walk_many_open_files(self):
        depth = 30
        base = os.path.join(support.TESTFN, 'deep')
        p = os.path.join(base, *(['d']*depth))
        os.makedirs(p)

        iters = [self.walk(base, topdown=Uongo) kila j kwenye range(100)]
        kila i kwenye range(depth + 1):
            expected = (p, ['d'] ikiwa i else [], [])
            kila it kwenye iters:
                self.assertEqual(next(it), expected)
            p = os.path.dirname(p)

        iters = [self.walk(base, topdown=Kweli) kila j kwenye range(100)]
        p = base
        kila i kwenye range(depth + 1):
            expected = (p, ['d'] ikiwa i < depth else [], [])
            kila it kwenye iters:
                self.assertEqual(next(it), expected)
            p = os.path.join(p, 'd')


@unittest.skipUnless(hasattr(os, 'fwalk'), "Test needs os.fwalk()")
kundi FwalkTests(WalkTests):
    """Tests kila os.fwalk()."""

    eleza walk(self, top, **kwargs):
        kila root, dirs, files, root_fd kwenye self.fwalk(top, **kwargs):
            tuma (root, dirs, files)

    eleza fwalk(self, *args, **kwargs):
        rudisha os.fwalk(*args, **kwargs)

    eleza _compare_to_walk(self, walk_kwargs, fwalk_kwargs):
        """
        compare with walk() results.
        """
        walk_kwargs = walk_kwargs.copy()
        fwalk_kwargs = fwalk_kwargs.copy()
        kila topdown, follow_symlinks kwenye itertools.product((Kweli, Uongo), repeat=2):
            walk_kwargs.update(topdown=topdown, followlinks=follow_symlinks)
            fwalk_kwargs.update(topdown=topdown, follow_symlinks=follow_symlinks)

            expected = {}
            kila root, dirs, files kwenye os.walk(**walk_kwargs):
                expected[root] = (set(dirs), set(files))

            kila root, dirs, files, rootfd kwenye self.fwalk(**fwalk_kwargs):
                self.assertIn(root, expected)
                self.assertEqual(expected[root], (set(dirs), set(files)))

    eleza test_compare_to_walk(self):
        kwargs = {'top': support.TESTFN}
        self._compare_to_walk(kwargs, kwargs)

    eleza test_dir_fd(self):
        jaribu:
            fd = os.open(".", os.O_RDONLY)
            walk_kwargs = {'top': support.TESTFN}
            fwalk_kwargs = walk_kwargs.copy()
            fwalk_kwargs['dir_fd'] = fd
            self._compare_to_walk(walk_kwargs, fwalk_kwargs)
        mwishowe:
            os.close(fd)

    eleza test_tumas_correct_dir_fd(self):
        # check rudishaed file descriptors
        kila topdown, follow_symlinks kwenye itertools.product((Kweli, Uongo), repeat=2):
            args = support.TESTFN, topdown, Tupu
            kila root, dirs, files, rootfd kwenye self.fwalk(*args, follow_symlinks=follow_symlinks):
                # check that the FD ni valid
                os.fstat(rootfd)
                # redundant check
                os.stat(rootfd)
                # check that listdir() rudishas consistent information
                self.assertEqual(set(os.listdir(rootfd)), set(dirs) | set(files))

    eleza test_fd_leak(self):
        # Since we're opening a lot of FDs, we must be careful to avoid leaks:
        # we both check that calling fwalk() a large number of times doesn't
        # tuma EMFILE, na that the minimum allocated FD hasn't changed.
        minfd = os.dup(1)
        os.close(minfd)
        kila i kwenye range(256):
            kila x kwenye self.fwalk(support.TESTFN):
                pita
        newfd = os.dup(1)
        self.addCleanup(os.close, newfd)
        self.assertEqual(newfd, minfd)

    # fwalk() keeps file descriptors open
    test_walk_many_open_files = Tupu


kundi BytesWalkTests(WalkTests):
    """Tests kila os.walk() with bytes."""
    eleza walk(self, top, **kwargs):
        ikiwa 'follow_symlinks' kwenye kwargs:
            kwargs['followlinks'] = kwargs.pop('follow_symlinks')
        kila broot, bdirs, bfiles kwenye os.walk(os.fsencode(top), **kwargs):
            root = os.fsdecode(broot)
            dirs = list(map(os.fsdecode, bdirs))
            files = list(map(os.fsdecode, bfiles))
            tuma (root, dirs, files)
            bdirs[:] = list(map(os.fsencode, dirs))
            bfiles[:] = list(map(os.fsencode, files))

@unittest.skipUnless(hasattr(os, 'fwalk'), "Test needs os.fwalk()")
kundi BytesFwalkTests(FwalkTests):
    """Tests kila os.walk() with bytes."""
    eleza fwalk(self, top='.', *args, **kwargs):
        kila broot, bdirs, bfiles, topfd kwenye os.fwalk(os.fsencode(top), *args, **kwargs):
            root = os.fsdecode(broot)
            dirs = list(map(os.fsdecode, bdirs))
            files = list(map(os.fsdecode, bfiles))
            tuma (root, dirs, files, topfd)
            bdirs[:] = list(map(os.fsencode, dirs))
            bfiles[:] = list(map(os.fsencode, files))


kundi MakedirTests(unittest.TestCase):
    eleza setUp(self):
        os.mkdir(support.TESTFN)

    eleza test_makedir(self):
        base = support.TESTFN
        path = os.path.join(base, 'dir1', 'dir2', 'dir3')
        os.makedirs(path)             # Should work
        path = os.path.join(base, 'dir1', 'dir2', 'dir3', 'dir4')
        os.makedirs(path)

        # Try paths with a '.' kwenye them
        self.assertRaises(OSError, os.makedirs, os.curdir)
        path = os.path.join(base, 'dir1', 'dir2', 'dir3', 'dir4', 'dir5', os.curdir)
        os.makedirs(path)
        path = os.path.join(base, 'dir1', os.curdir, 'dir2', 'dir3', 'dir4',
                            'dir5', 'dir6')
        os.makedirs(path)

    eleza test_mode(self):
        with support.temp_umask(0o002):
            base = support.TESTFN
            parent = os.path.join(base, 'dir1')
            path = os.path.join(parent, 'dir2')
            os.makedirs(path, 0o555)
            self.assertKweli(os.path.exists(path))
            self.assertKweli(os.path.isdir(path))
            ikiwa os.name != 'nt':
                self.assertEqual(os.stat(path).st_mode & 0o777, 0o555)
                self.assertEqual(os.stat(parent).st_mode & 0o777, 0o775)

    eleza test_exist_ok_existing_directory(self):
        path = os.path.join(support.TESTFN, 'dir1')
        mode = 0o777
        old_mask = os.umask(0o022)
        os.makedirs(path, mode)
        self.assertRaises(OSError, os.makedirs, path, mode)
        self.assertRaises(OSError, os.makedirs, path, mode, exist_ok=Uongo)
        os.makedirs(path, 0o776, exist_ok=Kweli)
        os.makedirs(path, mode=mode, exist_ok=Kweli)
        os.umask(old_mask)

        # Issue #25583: A drive root could ashiria PermissionError on Windows
        os.makedirs(os.path.abspath('/'), exist_ok=Kweli)

    eleza test_exist_ok_s_isgid_directory(self):
        path = os.path.join(support.TESTFN, 'dir1')
        S_ISGID = stat.S_ISGID
        mode = 0o777
        old_mask = os.umask(0o022)
        jaribu:
            existing_testfn_mode = stat.S_IMODE(
                    os.lstat(support.TESTFN).st_mode)
            jaribu:
                os.chmod(support.TESTFN, existing_testfn_mode | S_ISGID)
            tatizo PermissionError:
                ashiria unittest.SkipTest('Cannot set S_ISGID kila dir.')
            ikiwa (os.lstat(support.TESTFN).st_mode & S_ISGID != S_ISGID):
                ashiria unittest.SkipTest('No support kila S_ISGID dir mode.')
            # The os should apply S_ISGID kutoka the parent dir kila us, but
            # this test need sio depend on that behavior.  Be explicit.
            os.makedirs(path, mode | S_ISGID)
            # http://bugs.python.org/issue14992
            # Should sio fail when the bit ni already set.
            os.makedirs(path, mode, exist_ok=Kweli)
            # remove the bit.
            os.chmod(path, stat.S_IMODE(os.lstat(path).st_mode) & ~S_ISGID)
            # May work even when the bit ni sio already set when demanded.
            os.makedirs(path, mode | S_ISGID, exist_ok=Kweli)
        mwishowe:
            os.umask(old_mask)

    eleza test_exist_ok_existing_regular_file(self):
        base = support.TESTFN
        path = os.path.join(support.TESTFN, 'dir1')
        with open(path, 'w') kama f:
            f.write('abc')
        self.assertRaises(OSError, os.makedirs, path)
        self.assertRaises(OSError, os.makedirs, path, exist_ok=Uongo)
        self.assertRaises(OSError, os.makedirs, path, exist_ok=Kweli)
        os.remove(path)

    eleza tearDown(self):
        path = os.path.join(support.TESTFN, 'dir1', 'dir2', 'dir3',
                            'dir4', 'dir5', 'dir6')
        # If the tests failed, the bottom-most directory ('../dir6')
        # may sio have been created, so we look kila the outermost directory
        # that exists.
        wakati sio os.path.exists(path) na path != support.TESTFN:
            path = os.path.dirname(path)

        os.removedirs(path)


@unittest.skipUnless(hasattr(os, 'chown'), "Test needs chown")
kundi ChownFileTests(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        os.mkdir(support.TESTFN)

    eleza test_chown_uid_gid_arguments_must_be_index(self):
        stat = os.stat(support.TESTFN)
        uid = stat.st_uid
        gid = stat.st_gid
        kila value kwenye (-1.0, -1j, decimal.Decimal(-1), fractions.Fraction(-2, 2)):
            self.assertRaises(TypeError, os.chown, support.TESTFN, value, gid)
            self.assertRaises(TypeError, os.chown, support.TESTFN, uid, value)
        self.assertIsTupu(os.chown(support.TESTFN, uid, gid))
        self.assertIsTupu(os.chown(support.TESTFN, -1, -1))

    @unittest.skipUnless(hasattr(os, 'getgroups'), 'need os.getgroups')
    eleza test_chown_gid(self):
        groups = os.getgroups()
        ikiwa len(groups) < 2:
            self.skipTest("test needs at least 2 groups")

        gid_1, gid_2 = groups[:2]
        uid = os.stat(support.TESTFN).st_uid

        os.chown(support.TESTFN, uid, gid_1)
        gid = os.stat(support.TESTFN).st_gid
        self.assertEqual(gid, gid_1)

        os.chown(support.TESTFN, uid, gid_2)
        gid = os.stat(support.TESTFN).st_gid
        self.assertEqual(gid, gid_2)

    @unittest.skipUnless(root_in_posix na len(all_users) > 1,
                         "test needs root privilege na more than one user")
    eleza test_chown_with_root(self):
        uid_1, uid_2 = all_users[:2]
        gid = os.stat(support.TESTFN).st_gid
        os.chown(support.TESTFN, uid_1, gid)
        uid = os.stat(support.TESTFN).st_uid
        self.assertEqual(uid, uid_1)
        os.chown(support.TESTFN, uid_2, gid)
        uid = os.stat(support.TESTFN).st_uid
        self.assertEqual(uid, uid_2)

    @unittest.skipUnless(not root_in_posix na len(all_users) > 1,
                         "test needs non-root account na more than one user")
    eleza test_chown_without_permission(self):
        uid_1, uid_2 = all_users[:2]
        gid = os.stat(support.TESTFN).st_gid
        with self.assertRaises(PermissionError):
            os.chown(support.TESTFN, uid_1, gid)
            os.chown(support.TESTFN, uid_2, gid)

    @classmethod
    eleza tearDownClass(cls):
        os.rmdir(support.TESTFN)


kundi RemoveDirsTests(unittest.TestCase):
    eleza setUp(self):
        os.makedirs(support.TESTFN)

    eleza tearDown(self):
        support.rmtree(support.TESTFN)

    eleza test_remove_all(self):
        dira = os.path.join(support.TESTFN, 'dira')
        os.mkdir(dira)
        dirb = os.path.join(dira, 'dirb')
        os.mkdir(dirb)
        os.removedirs(dirb)
        self.assertUongo(os.path.exists(dirb))
        self.assertUongo(os.path.exists(dira))
        self.assertUongo(os.path.exists(support.TESTFN))

    eleza test_remove_partial(self):
        dira = os.path.join(support.TESTFN, 'dira')
        os.mkdir(dira)
        dirb = os.path.join(dira, 'dirb')
        os.mkdir(dirb)
        create_file(os.path.join(dira, 'file.txt'))
        os.removedirs(dirb)
        self.assertUongo(os.path.exists(dirb))
        self.assertKweli(os.path.exists(dira))
        self.assertKweli(os.path.exists(support.TESTFN))

    eleza test_remove_nothing(self):
        dira = os.path.join(support.TESTFN, 'dira')
        os.mkdir(dira)
        dirb = os.path.join(dira, 'dirb')
        os.mkdir(dirb)
        create_file(os.path.join(dirb, 'file.txt'))
        with self.assertRaises(OSError):
            os.removedirs(dirb)
        self.assertKweli(os.path.exists(dirb))
        self.assertKweli(os.path.exists(dira))
        self.assertKweli(os.path.exists(support.TESTFN))


kundi DevNullTests(unittest.TestCase):
    eleza test_devnull(self):
        with open(os.devnull, 'wb', 0) kama f:
            f.write(b'hello')
            f.close()
        with open(os.devnull, 'rb') kama f:
            self.assertEqual(f.read(), b'')


kundi URandomTests(unittest.TestCase):
    eleza test_urandom_length(self):
        self.assertEqual(len(os.urandom(0)), 0)
        self.assertEqual(len(os.urandom(1)), 1)
        self.assertEqual(len(os.urandom(10)), 10)
        self.assertEqual(len(os.urandom(100)), 100)
        self.assertEqual(len(os.urandom(1000)), 1000)

    eleza test_urandom_value(self):
        data1 = os.urandom(16)
        self.assertIsInstance(data1, bytes)
        data2 = os.urandom(16)
        self.assertNotEqual(data1, data2)

    eleza get_urandom_subprocess(self, count):
        code = '\n'.join((
            'agiza os, sys',
            'data = os.urandom(%s)' % count,
            'sys.stdout.buffer.write(data)',
            'sys.stdout.buffer.flush()'))
        out = assert_python_ok('-c', code)
        stdout = out[1]
        self.assertEqual(len(stdout), count)
        rudisha stdout

    eleza test_urandom_subprocess(self):
        data1 = self.get_urandom_subprocess(16)
        data2 = self.get_urandom_subprocess(16)
        self.assertNotEqual(data1, data2)


@unittest.skipUnless(hasattr(os, 'getrandom'), 'need os.getrandom()')
kundi GetRandomTests(unittest.TestCase):
    @classmethod
    eleza setUpClass(cls):
        jaribu:
            os.getrandom(1)
        tatizo OSError kama exc:
            ikiwa exc.errno == errno.ENOSYS:
                # Python compiled on a more recent Linux version
                # than the current Linux kernel
                ashiria unittest.SkipTest("getrandom() syscall fails with ENOSYS")
            isipokua:
                ashiria

    eleza test_getrandom_type(self):
        data = os.getrandom(16)
        self.assertIsInstance(data, bytes)
        self.assertEqual(len(data), 16)

    eleza test_getrandom0(self):
        empty = os.getrandom(0)
        self.assertEqual(empty, b'')

    eleza test_getrandom_random(self):
        self.assertKweli(hasattr(os, 'GRND_RANDOM'))

        # Don't test os.getrandom(1, os.GRND_RANDOM) to sio consume the rare
        # resource /dev/random

    eleza test_getrandom_nonblock(self):
        # The call must sio fail. Check also that the flag exists
        jaribu:
            os.getrandom(1, os.GRND_NONBLOCK)
        tatizo BlockingIOError:
            # System urandom ni sio initialized yet
            pita

    eleza test_getrandom_value(self):
        data1 = os.getrandom(16)
        data2 = os.getrandom(16)
        self.assertNotEqual(data1, data2)


# os.urandom() doesn't use a file descriptor when it ni implemented with the
# getentropy() function, the getrandom() function ama the getrandom() syscall
OS_URANDOM_DONT_USE_FD = (
    sysconfig.get_config_var('HAVE_GETENTROPY') == 1
    ama sysconfig.get_config_var('HAVE_GETRANDOM') == 1
    ama sysconfig.get_config_var('HAVE_GETRANDOM_SYSCALL') == 1)

@unittest.skipIf(OS_URANDOM_DONT_USE_FD ,
                 "os.random() does sio use a file descriptor")
@unittest.skipIf(sys.platform == "vxworks",
                 "VxWorks can't set RLIMIT_NOFILE to 1")
kundi URandomFDTests(unittest.TestCase):
    @unittest.skipUnless(resource, "test requires the resource module")
    eleza test_urandom_failure(self):
        # Check urandom() failing when it ni sio able to open /dev/random.
        # We spawn a new process to make the test more robust (ikiwa getrlimit()
        # failed to restore the file descriptor limit after this, the whole
        # test suite would crash; this actually happened on the OS X Tiger
        # buildbot).
        code = """ikiwa 1:
            agiza errno
            agiza os
            agiza resource

            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
            resource.setrlimit(resource.RLIMIT_NOFILE, (1, hard_limit))
            jaribu:
                os.urandom(16)
            tatizo OSError kama e:
                assert e.errno == errno.EMFILE, e.errno
            isipokua:
                ashiria AssertionError("OSError sio ashiriad")
            """
        assert_python_ok('-c', code)

    eleza test_urandom_fd_closed(self):
        # Issue #21207: urandom() should reopen its fd to /dev/urandom if
        # closed.
        code = """ikiwa 1:
            agiza os
            agiza sys
            agiza test.support
            os.urandom(4)
            with test.support.SuppressCrashReport():
                os.closerange(3, 256)
            sys.stdout.buffer.write(os.urandom(4))
            """
        rc, out, err = assert_python_ok('-Sc', code)

    eleza test_urandom_fd_reopened(self):
        # Issue #21207: urandom() should detect its fd to /dev/urandom
        # changed to something else, na reopen it.
        self.addCleanup(support.unlink, support.TESTFN)
        create_file(support.TESTFN, b"x" * 256)

        code = """ikiwa 1:
            agiza os
            agiza sys
            agiza test.support
            os.urandom(4)
            with test.support.SuppressCrashReport():
                kila fd kwenye range(3, 256):
                    jaribu:
                        os.close(fd)
                    tatizo OSError:
                        pita
                    isipokua:
                        # Found the urandom fd (XXX hopefully)
                        koma
                os.closerange(3, 256)
            with open({TESTFN!r}, 'rb') kama f:
                new_fd = f.fileno()
                # Issue #26935: posix allows new_fd na fd to be equal but
                # some libc implementations have dup2 rudisha an error kwenye this
                # case.
                ikiwa new_fd != fd:
                    os.dup2(new_fd, fd)
                sys.stdout.buffer.write(os.urandom(4))
                sys.stdout.buffer.write(os.urandom(4))
            """.format(TESTFN=support.TESTFN)
        rc, out, err = assert_python_ok('-Sc', code)
        self.assertEqual(len(out), 8)
        self.assertNotEqual(out[0:4], out[4:8])
        rc, out2, err2 = assert_python_ok('-Sc', code)
        self.assertEqual(len(out2), 8)
        self.assertNotEqual(out2, out)


@contextlib.contextmanager
eleza _execvpe_mockup(defpath=Tupu):
    """
    Stubs out execv na execve functions when used kama context manager.
    Records exec calls. The mock execv na execve functions always ashiria an
    exception kama they would normally never rudisha.
    """
    # A list of tuples containing (function name, first arg, args)
    # of calls to execv ama execve that have been made.
    calls = []

    eleza mock_execv(name, *args):
        calls.append(('execv', name, args))
        ashiria RuntimeError("execv called")

    eleza mock_execve(name, *args):
        calls.append(('execve', name, args))
        ashiria OSError(errno.ENOTDIR, "execve called")

    jaribu:
        orig_execv = os.execv
        orig_execve = os.execve
        orig_defpath = os.defpath
        os.execv = mock_execv
        os.execve = mock_execve
        ikiwa defpath ni sio Tupu:
            os.defpath = defpath
        tuma calls
    mwishowe:
        os.execv = orig_execv
        os.execve = orig_execve
        os.defpath = orig_defpath

@unittest.skipUnless(hasattr(os, 'execv'),
                     "need os.execv()")
kundi ExecTests(unittest.TestCase):
    @unittest.skipIf(USING_LINUXTHREADS,
                     "avoid triggering a linuxthreads bug: see issue #4970")
    eleza test_execvpe_with_bad_program(self):
        self.assertRaises(OSError, os.execvpe, 'no such app-',
                          ['no such app-'], Tupu)

    eleza test_execv_with_bad_arglist(self):
        self.assertRaises(ValueError, os.execv, 'notepad', ())
        self.assertRaises(ValueError, os.execv, 'notepad', [])
        self.assertRaises(ValueError, os.execv, 'notepad', ('',))
        self.assertRaises(ValueError, os.execv, 'notepad', [''])

    eleza test_execvpe_with_bad_arglist(self):
        self.assertRaises(ValueError, os.execvpe, 'notepad', [], Tupu)
        self.assertRaises(ValueError, os.execvpe, 'notepad', [], {})
        self.assertRaises(ValueError, os.execvpe, 'notepad', [''], {})

    @unittest.skipUnless(hasattr(os, '_execvpe'),
                         "No internal os._execvpe function to test.")
    eleza _test_internal_execvpe(self, test_type):
        program_path = os.sep + 'absolutepath'
        ikiwa test_type ni bytes:
            program = b'executable'
            fullpath = os.path.join(os.fsencode(program_path), program)
            native_fullpath = fullpath
            arguments = [b'progname', 'arg1', 'arg2']
        isipokua:
            program = 'executable'
            arguments = ['progname', 'arg1', 'arg2']
            fullpath = os.path.join(program_path, program)
            ikiwa os.name != "nt":
                native_fullpath = os.fsencode(fullpath)
            isipokua:
                native_fullpath = fullpath
        env = {'spam': 'beans'}

        # test os._execvpe() with an absolute path
        with _execvpe_mockup() kama calls:
            self.assertRaises(RuntimeError,
                os._execvpe, fullpath, arguments)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0], ('execv', fullpath, (arguments,)))

        # test os._execvpe() with a relative path:
        # os.get_exec_path() rudishas defpath
        with _execvpe_mockup(defpath=program_path) kama calls:
            self.assertRaises(OSError,
                os._execvpe, program, arguments, env=env)
            self.assertEqual(len(calls), 1)
            self.assertSequenceEqual(calls[0],
                ('execve', native_fullpath, (arguments, env)))

        # test os._execvpe() with a relative path:
        # os.get_exec_path() reads the 'PATH' variable
        with _execvpe_mockup() kama calls:
            env_path = env.copy()
            ikiwa test_type ni bytes:
                env_path[b'PATH'] = program_path
            isipokua:
                env_path['PATH'] = program_path
            self.assertRaises(OSError,
                os._execvpe, program, arguments, env=env_path)
            self.assertEqual(len(calls), 1)
            self.assertSequenceEqual(calls[0],
                ('execve', native_fullpath, (arguments, env_path)))

    eleza test_internal_execvpe_str(self):
        self._test_internal_execvpe(str)
        ikiwa os.name != "nt":
            self._test_internal_execvpe(bytes)

    eleza test_execve_invalid_env(self):
        args = [sys.executable, '-c', 'pita']

        # null character kwenye the environment variable name
        newenv = os.environ.copy()
        newenv["FRUIT\0VEGETABLE"] = "cabbage"
        with self.assertRaises(ValueError):
            os.execve(args[0], args, newenv)

        # null character kwenye the environment variable value
        newenv = os.environ.copy()
        newenv["FRUIT"] = "orange\0VEGETABLE=cabbage"
        with self.assertRaises(ValueError):
            os.execve(args[0], args, newenv)

        # equal character kwenye the environment variable name
        newenv = os.environ.copy()
        newenv["FRUIT=ORANGE"] = "lemon"
        with self.assertRaises(ValueError):
            os.execve(args[0], args, newenv)

    @unittest.skipUnless(sys.platform == "win32", "Win32-specific test")
    eleza test_execve_with_empty_path(self):
        # bpo-32890: Check GetLastError() misuse
        jaribu:
            os.execve('', ['arg'], {})
        tatizo OSError kama e:
            self.assertKweli(e.winerror ni Tupu ama e.winerror != 0)
        isipokua:
            self.fail('No OSError ashiriad')


@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
kundi Win32ErrorTests(unittest.TestCase):
    eleza setUp(self):
        jaribu:
            os.stat(support.TESTFN)
        tatizo FileNotFoundError:
            exists = Uongo
        tatizo OSError kama exc:
            exists = Kweli
            self.fail("file %s must sio exist; os.stat failed with %s"
                      % (support.TESTFN, exc))
        isipokua:
            self.fail("file %s must sio exist" % support.TESTFN)

    eleza test_rename(self):
        self.assertRaises(OSError, os.rename, support.TESTFN, support.TESTFN+".bak")

    eleza test_remove(self):
        self.assertRaises(OSError, os.remove, support.TESTFN)

    eleza test_chdir(self):
        self.assertRaises(OSError, os.chdir, support.TESTFN)

    eleza test_mkdir(self):
        self.addCleanup(support.unlink, support.TESTFN)

        with open(support.TESTFN, "x") kama f:
            self.assertRaises(OSError, os.mkdir, support.TESTFN)

    eleza test_utime(self):
        self.assertRaises(OSError, os.utime, support.TESTFN, Tupu)

    eleza test_chmod(self):
        self.assertRaises(OSError, os.chmod, support.TESTFN, 0)


kundi TestInvalidFD(unittest.TestCase):
    singles = ["fchdir", "dup", "fdopen", "fdatasync", "fstat",
               "fstatvfs", "fsync", "tcgetpgrp", "ttyname"]
    #singles.append("close")
    #We omit close because it doesn't ashiria an exception on some platforms
    eleza get_single(f):
        eleza helper(self):
            ikiwa  hasattr(os, f):
                self.check(getattr(os, f))
        rudisha helper
    kila f kwenye singles:
        locals()["test_"+f] = get_single(f)

    eleza check(self, f, *args):
        jaribu:
            f(support.make_bad_fd(), *args)
        tatizo OSError kama e:
            self.assertEqual(e.errno, errno.EBADF)
        isipokua:
            self.fail("%r didn't ashiria an OSError with a bad file descriptor"
                      % f)

    @unittest.skipUnless(hasattr(os, 'isatty'), 'test needs os.isatty()')
    eleza test_isatty(self):
        self.assertEqual(os.isatty(support.make_bad_fd()), Uongo)

    @unittest.skipUnless(hasattr(os, 'closerange'), 'test needs os.closerange()')
    eleza test_closerange(self):
        fd = support.make_bad_fd()
        # Make sure none of the descriptors we are about to close are
        # currently valid (issue 6542).
        kila i kwenye range(10):
            jaribu: os.fstat(fd+i)
            tatizo OSError:
                pita
            isipokua:
                koma
        ikiwa i < 2:
            ashiria unittest.SkipTest(
                "Unable to acquire a range of invalid file descriptors")
        self.assertEqual(os.closerange(fd, fd + i-1), Tupu)

    @unittest.skipUnless(hasattr(os, 'dup2'), 'test needs os.dup2()')
    eleza test_dup2(self):
        self.check(os.dup2, 20)

    @unittest.skipUnless(hasattr(os, 'fchmod'), 'test needs os.fchmod()')
    eleza test_fchmod(self):
        self.check(os.fchmod, 0)

    @unittest.skipUnless(hasattr(os, 'fchown'), 'test needs os.fchown()')
    eleza test_fchown(self):
        self.check(os.fchown, -1, -1)

    @unittest.skipUnless(hasattr(os, 'fpathconf'), 'test needs os.fpathconf()')
    eleza test_fpathconf(self):
        self.check(os.pathconf, "PC_NAME_MAX")
        self.check(os.fpathconf, "PC_NAME_MAX")

    @unittest.skipUnless(hasattr(os, 'ftruncate'), 'test needs os.ftruncate()')
    eleza test_ftruncate(self):
        self.check(os.truncate, 0)
        self.check(os.ftruncate, 0)

    @unittest.skipUnless(hasattr(os, 'lseek'), 'test needs os.lseek()')
    eleza test_lseek(self):
        self.check(os.lseek, 0, 0)

    @unittest.skipUnless(hasattr(os, 'read'), 'test needs os.read()')
    eleza test_read(self):
        self.check(os.read, 1)

    @unittest.skipUnless(hasattr(os, 'readv'), 'test needs os.readv()')
    eleza test_readv(self):
        buf = bytearray(10)
        self.check(os.readv, [buf])

    @unittest.skipUnless(hasattr(os, 'tcsetpgrp'), 'test needs os.tcsetpgrp()')
    eleza test_tcsetpgrpt(self):
        self.check(os.tcsetpgrp, 0)

    @unittest.skipUnless(hasattr(os, 'write'), 'test needs os.write()')
    eleza test_write(self):
        self.check(os.write, b" ")

    @unittest.skipUnless(hasattr(os, 'writev'), 'test needs os.writev()')
    eleza test_writev(self):
        self.check(os.writev, [b'abc'])

    eleza test_inheritable(self):
        self.check(os.get_inheritable)
        self.check(os.set_inheritable, Kweli)

    @unittest.skipUnless(hasattr(os, 'get_blocking'),
                         'needs os.get_blocking() na os.set_blocking()')
    eleza test_blocking(self):
        self.check(os.get_blocking)
        self.check(os.set_blocking, Kweli)


kundi LinkTests(unittest.TestCase):
    eleza setUp(self):
        self.file1 = support.TESTFN
        self.file2 = os.path.join(support.TESTFN + "2")

    eleza tearDown(self):
        kila file kwenye (self.file1, self.file2):
            ikiwa os.path.exists(file):
                os.unlink(file)

    eleza _test_link(self, file1, file2):
        create_file(file1)

        jaribu:
            os.link(file1, file2)
        tatizo PermissionError kama e:
            self.skipTest('os.link(): %s' % e)
        with open(file1, "r") kama f1, open(file2, "r") kama f2:
            self.assertKweli(os.path.sameopenfile(f1.fileno(), f2.fileno()))

    eleza test_link(self):
        self._test_link(self.file1, self.file2)

    eleza test_link_bytes(self):
        self._test_link(bytes(self.file1, sys.getfilesystemencoding()),
                        bytes(self.file2, sys.getfilesystemencoding()))

    eleza test_unicode_name(self):
        jaribu:
            os.fsencode("\xf1")
        tatizo UnicodeError:
            ashiria unittest.SkipTest("Unable to encode kila this platform.")

        self.file1 += "\xf1"
        self.file2 = self.file1 + "2"
        self._test_link(self.file1, self.file2)

@unittest.skipIf(sys.platform == "win32", "Posix specific tests")
kundi PosixUidGidTests(unittest.TestCase):
    # uid_t na gid_t are 32-bit unsigned integers on Linux
    UID_OVERFLOW = (1 << 32)
    GID_OVERFLOW = (1 << 32)

    @unittest.skipUnless(hasattr(os, 'setuid'), 'test needs os.setuid()')
    eleza test_setuid(self):
        ikiwa os.getuid() != 0:
            self.assertRaises(OSError, os.setuid, 0)
        self.assertRaises(TypeError, os.setuid, 'not an int')
        self.assertRaises(OverflowError, os.setuid, self.UID_OVERFLOW)

    @unittest.skipUnless(hasattr(os, 'setgid'), 'test needs os.setgid()')
    eleza test_setgid(self):
        ikiwa os.getuid() != 0 na sio HAVE_WHEEL_GROUP:
            self.assertRaises(OSError, os.setgid, 0)
        self.assertRaises(TypeError, os.setgid, 'not an int')
        self.assertRaises(OverflowError, os.setgid, self.GID_OVERFLOW)

    @unittest.skipUnless(hasattr(os, 'seteuid'), 'test needs os.seteuid()')
    eleza test_seteuid(self):
        ikiwa os.getuid() != 0:
            self.assertRaises(OSError, os.seteuid, 0)
        self.assertRaises(TypeError, os.setegid, 'not an int')
        self.assertRaises(OverflowError, os.seteuid, self.UID_OVERFLOW)

    @unittest.skipUnless(hasattr(os, 'setegid'), 'test needs os.setegid()')
    eleza test_setegid(self):
        ikiwa os.getuid() != 0 na sio HAVE_WHEEL_GROUP:
            self.assertRaises(OSError, os.setegid, 0)
        self.assertRaises(TypeError, os.setegid, 'not an int')
        self.assertRaises(OverflowError, os.setegid, self.GID_OVERFLOW)

    @unittest.skipUnless(hasattr(os, 'setreuid'), 'test needs os.setreuid()')
    eleza test_setreuid(self):
        ikiwa os.getuid() != 0:
            self.assertRaises(OSError, os.setreuid, 0, 0)
        self.assertRaises(TypeError, os.setreuid, 'not an int', 0)
        self.assertRaises(TypeError, os.setreuid, 0, 'not an int')
        self.assertRaises(OverflowError, os.setreuid, self.UID_OVERFLOW, 0)
        self.assertRaises(OverflowError, os.setreuid, 0, self.UID_OVERFLOW)

    @unittest.skipUnless(hasattr(os, 'setreuid'), 'test needs os.setreuid()')
    eleza test_setreuid_neg1(self):
        # Needs to accept -1.  We run this kwenye a subprocess to avoid
        # altering the test runner's process state (issue8045).
        subprocess.check_call([
                sys.executable, '-c',
                'agiza os,sys;os.setreuid(-1,-1);sys.exit(0)'])

    @unittest.skipUnless(hasattr(os, 'setregid'), 'test needs os.setregid()')
    eleza test_setregid(self):
        ikiwa os.getuid() != 0 na sio HAVE_WHEEL_GROUP:
            self.assertRaises(OSError, os.setregid, 0, 0)
        self.assertRaises(TypeError, os.setregid, 'not an int', 0)
        self.assertRaises(TypeError, os.setregid, 0, 'not an int')
        self.assertRaises(OverflowError, os.setregid, self.GID_OVERFLOW, 0)
        self.assertRaises(OverflowError, os.setregid, 0, self.GID_OVERFLOW)

    @unittest.skipUnless(hasattr(os, 'setregid'), 'test needs os.setregid()')
    eleza test_setregid_neg1(self):
        # Needs to accept -1.  We run this kwenye a subprocess to avoid
        # altering the test runner's process state (issue8045).
        subprocess.check_call([
                sys.executable, '-c',
                'agiza os,sys;os.setregid(-1,-1);sys.exit(0)'])

@unittest.skipIf(sys.platform == "win32", "Posix specific tests")
kundi Pep383Tests(unittest.TestCase):
    eleza setUp(self):
        ikiwa support.TESTFN_UNENCODABLE:
            self.dir = support.TESTFN_UNENCODABLE
        elikiwa support.TESTFN_NONASCII:
            self.dir = support.TESTFN_NONASCII
        isipokua:
            self.dir = support.TESTFN
        self.bdir = os.fsencode(self.dir)

        bytesfn = []
        eleza add_filename(fn):
            jaribu:
                fn = os.fsencode(fn)
            tatizo UnicodeEncodeError:
                rudisha
            bytesfn.append(fn)
        add_filename(support.TESTFN_UNICODE)
        ikiwa support.TESTFN_UNENCODABLE:
            add_filename(support.TESTFN_UNENCODABLE)
        ikiwa support.TESTFN_NONASCII:
            add_filename(support.TESTFN_NONASCII)
        ikiwa sio bytesfn:
            self.skipTest("couldn't create any non-ascii filename")

        self.unicodefn = set()
        os.mkdir(self.dir)
        jaribu:
            kila fn kwenye bytesfn:
                support.create_empty_file(os.path.join(self.bdir, fn))
                fn = os.fsdecode(fn)
                ikiwa fn kwenye self.unicodefn:
                    ashiria ValueError("duplicate filename")
                self.unicodefn.add(fn)
        except:
            shutil.rmtree(self.dir)
            ashiria

    eleza tearDown(self):
        shutil.rmtree(self.dir)

    eleza test_listdir(self):
        expected = self.unicodefn
        found = set(os.listdir(self.dir))
        self.assertEqual(found, expected)
        # test listdir without arguments
        current_directory = os.getcwd()
        jaribu:
            os.chdir(os.sep)
            self.assertEqual(set(os.listdir()), set(os.listdir(os.sep)))
        mwishowe:
            os.chdir(current_directory)

    eleza test_open(self):
        kila fn kwenye self.unicodefn:
            f = open(os.path.join(self.dir, fn), 'rb')
            f.close()

    @unittest.skipUnless(hasattr(os, 'statvfs'),
                            "need os.statvfs()")
    eleza test_statvfs(self):
        # issue #9645
        kila fn kwenye self.unicodefn:
            # should sio fail with file sio found error
            fullname = os.path.join(self.dir, fn)
            os.statvfs(fullname)

    eleza test_stat(self):
        kila fn kwenye self.unicodefn:
            os.stat(os.path.join(self.dir, fn))

@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
kundi Win32KillTests(unittest.TestCase):
    eleza _kill(self, sig):
        # Start sys.executable kama a subprocess na communicate kutoka the
        # subprocess to the parent that the interpreter ni ready. When it
        # becomes ready, send *sig* via os.kill to the subprocess na check
        # that the rudisha code ni equal to *sig*.
        agiza ctypes
        kutoka ctypes agiza wintypes
        agiza msvcrt

        # Since we can't access the contents of the process' stdout until the
        # process has exited, use PeekNamedPipe to see what's inside stdout
        # without waiting. This ni done so we can tell that the interpreter
        # ni started na running at a point where it could handle a signal.
        PeekNamedPipe = ctypes.windll.kernel32.PeekNamedPipe
        PeekNamedPipe.restype = wintypes.BOOL
        PeekNamedPipe.argtypes = (wintypes.HANDLE, # Pipe handle
                                  ctypes.POINTER(ctypes.c_char), # stdout buf
                                  wintypes.DWORD, # Buffer size
                                  ctypes.POINTER(wintypes.DWORD), # bytes read
                                  ctypes.POINTER(wintypes.DWORD), # bytes avail
                                  ctypes.POINTER(wintypes.DWORD)) # bytes left
        msg = "running"
        proc = subprocess.Popen([sys.executable, "-c",
                                 "agiza sys;"
                                 "sys.stdout.write('{}');"
                                 "sys.stdout.flush();"
                                 "input()".format(msg)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        self.addCleanup(proc.stdout.close)
        self.addCleanup(proc.stderr.close)
        self.addCleanup(proc.stdin.close)

        count, max = 0, 100
        wakati count < max na proc.poll() ni Tupu:
            # Create a string buffer to store the result of stdout kutoka the pipe
            buf = ctypes.create_string_buffer(len(msg))
            # Obtain the text currently kwenye proc.stdout
            # Bytes read/avail/left are left kama NULL na unused
            rslt = PeekNamedPipe(msvcrt.get_osfhandle(proc.stdout.fileno()),
                                 buf, ctypes.sizeof(buf), Tupu, Tupu, Tupu)
            self.assertNotEqual(rslt, 0, "PeekNamedPipe failed")
            ikiwa buf.value:
                self.assertEqual(msg, buf.value.decode())
                koma
            time.sleep(0.1)
            count += 1
        isipokua:
            self.fail("Did sio receive communication kutoka the subprocess")

        os.kill(proc.pid, sig)
        self.assertEqual(proc.wait(), sig)

    eleza test_kill_sigterm(self):
        # SIGTERM doesn't mean anything special, but make sure it works
        self._kill(signal.SIGTERM)

    eleza test_kill_int(self):
        # os.kill on Windows can take an int which gets set kama the exit code
        self._kill(100)

    eleza _kill_with_event(self, event, name):
        tagname = "test_os_%s" % uuid.uuid1()
        m = mmap.mmap(-1, 1, tagname)
        m[0] = 0
        # Run a script which has console control handling enabled.
        proc = subprocess.Popen([sys.executable,
                   os.path.join(os.path.dirname(__file__),
                                "win_console_handler.py"), tagname],
                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        # Let the interpreter startup before we send signals. See #3137.
        count, max = 0, 100
        wakati count < max na proc.poll() ni Tupu:
            ikiwa m[0] == 1:
                koma
            time.sleep(0.1)
            count += 1
        isipokua:
            # Forcefully kill the process ikiwa we weren't able to signal it.
            os.kill(proc.pid, signal.SIGINT)
            self.fail("Subprocess didn't finish initialization")
        os.kill(proc.pid, event)
        # proc.send_signal(event) could also be done here.
        # Allow time kila the signal to be pitaed na the process to exit.
        time.sleep(0.5)
        ikiwa sio proc.poll():
            # Forcefully kill the process ikiwa we weren't able to signal it.
            os.kill(proc.pid, signal.SIGINT)
            self.fail("subprocess did sio stop on {}".format(name))

    @unittest.skip("subprocesses aren't inheriting Ctrl+C property")
    eleza test_CTRL_C_EVENT(self):
        kutoka ctypes agiza wintypes
        agiza ctypes

        # Make a NULL value by creating a pointer with no argument.
        NULL = ctypes.POINTER(ctypes.c_int)()
        SetConsoleCtrlHandler = ctypes.windll.kernel32.SetConsoleCtrlHandler
        SetConsoleCtrlHandler.argtypes = (ctypes.POINTER(ctypes.c_int),
                                          wintypes.BOOL)
        SetConsoleCtrlHandler.restype = wintypes.BOOL

        # Calling this with NULL na FALSE causes the calling process to
        # handle Ctrl+C, rather than ignore it. This property ni inherited
        # by subprocesses.
        SetConsoleCtrlHandler(NULL, 0)

        self._kill_with_event(signal.CTRL_C_EVENT, "CTRL_C_EVENT")

    eleza test_CTRL_BREAK_EVENT(self):
        self._kill_with_event(signal.CTRL_BREAK_EVENT, "CTRL_BREAK_EVENT")


@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
kundi Win32ListdirTests(unittest.TestCase):
    """Test listdir on Windows."""

    eleza setUp(self):
        self.created_paths = []
        kila i kwenye range(2):
            dir_name = 'SUB%d' % i
            dir_path = os.path.join(support.TESTFN, dir_name)
            file_name = 'FILE%d' % i
            file_path = os.path.join(support.TESTFN, file_name)
            os.makedirs(dir_path)
            with open(file_path, 'w') kama f:
                f.write("I'm %s na proud of it. Blame test_os.\n" % file_path)
            self.created_paths.extend([dir_name, file_name])
        self.created_paths.sort()

    eleza tearDown(self):
        shutil.rmtree(support.TESTFN)

    eleza test_listdir_no_extended_path(self):
        """Test when the path ni sio an "extended" path."""
        # unicode
        self.assertEqual(
                sorted(os.listdir(support.TESTFN)),
                self.created_paths)

        # bytes
        self.assertEqual(
                sorted(os.listdir(os.fsencode(support.TESTFN))),
                [os.fsencode(path) kila path kwenye self.created_paths])

    eleza test_listdir_extended_path(self):
        """Test when the path starts with '\\\\?\\'."""
        # See: http://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx#maxpath
        # unicode
        path = '\\\\?\\' + os.path.abspath(support.TESTFN)
        self.assertEqual(
                sorted(os.listdir(path)),
                self.created_paths)

        # bytes
        path = b'\\\\?\\' + os.fsencode(os.path.abspath(support.TESTFN))
        self.assertEqual(
                sorted(os.listdir(path)),
                [os.fsencode(path) kila path kwenye self.created_paths])


@unittest.skipUnless(hasattr(os, 'readlink'), 'needs os.readlink()')
kundi ReadlinkTests(unittest.TestCase):
    filelink = 'readlinktest'
    filelink_target = os.path.abspath(__file__)
    filelinkb = os.fsencode(filelink)
    filelinkb_target = os.fsencode(filelink_target)

    eleza assertPathEqual(self, left, right):
        left = os.path.normcase(left)
        right = os.path.normcase(right)
        ikiwa sys.platform == 'win32':
            # Bad practice to blindly strip the prefix kama it may be required to
            # correctly refer to the file, but we're only comparing paths here.
            has_prefix = lambda p: p.startswith(
                b'\\\\?\\' ikiwa isinstance(p, bytes) else '\\\\?\\')
            ikiwa has_prefix(left):
                left = left[4:]
            ikiwa has_prefix(right):
                right = right[4:]
        self.assertEqual(left, right)

    eleza setUp(self):
        self.assertKweli(os.path.exists(self.filelink_target))
        self.assertKweli(os.path.exists(self.filelinkb_target))
        self.assertUongo(os.path.exists(self.filelink))
        self.assertUongo(os.path.exists(self.filelinkb))

    eleza test_not_symlink(self):
        filelink_target = FakePath(self.filelink_target)
        self.assertRaises(OSError, os.readlink, self.filelink_target)
        self.assertRaises(OSError, os.readlink, filelink_target)

    eleza test_missing_link(self):
        self.assertRaises(FileNotFoundError, os.readlink, 'missing-link')
        self.assertRaises(FileNotFoundError, os.readlink,
                          FakePath('missing-link'))

    @support.skip_unless_symlink
    eleza test_pathlike(self):
        os.symlink(self.filelink_target, self.filelink)
        self.addCleanup(support.unlink, self.filelink)
        filelink = FakePath(self.filelink)
        self.assertPathEqual(os.readlink(filelink), self.filelink_target)

    @support.skip_unless_symlink
    eleza test_pathlike_bytes(self):
        os.symlink(self.filelinkb_target, self.filelinkb)
        self.addCleanup(support.unlink, self.filelinkb)
        path = os.readlink(FakePath(self.filelinkb))
        self.assertPathEqual(path, self.filelinkb_target)
        self.assertIsInstance(path, bytes)

    @support.skip_unless_symlink
    eleza test_bytes(self):
        os.symlink(self.filelinkb_target, self.filelinkb)
        self.addCleanup(support.unlink, self.filelinkb)
        path = os.readlink(self.filelinkb)
        self.assertPathEqual(path, self.filelinkb_target)
        self.assertIsInstance(path, bytes)


@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
@support.skip_unless_symlink
kundi Win32SymlinkTests(unittest.TestCase):
    filelink = 'filelinktest'
    filelink_target = os.path.abspath(__file__)
    dirlink = 'dirlinktest'
    dirlink_target = os.path.dirname(filelink_target)
    missing_link = 'missing link'

    eleza setUp(self):
        assert os.path.exists(self.dirlink_target)
        assert os.path.exists(self.filelink_target)
        assert sio os.path.exists(self.dirlink)
        assert sio os.path.exists(self.filelink)
        assert sio os.path.exists(self.missing_link)

    eleza tearDown(self):
        ikiwa os.path.exists(self.filelink):
            os.remove(self.filelink)
        ikiwa os.path.exists(self.dirlink):
            os.rmdir(self.dirlink)
        ikiwa os.path.lexists(self.missing_link):
            os.remove(self.missing_link)

    eleza test_directory_link(self):
        os.symlink(self.dirlink_target, self.dirlink)
        self.assertKweli(os.path.exists(self.dirlink))
        self.assertKweli(os.path.isdir(self.dirlink))
        self.assertKweli(os.path.islink(self.dirlink))
        self.check_stat(self.dirlink, self.dirlink_target)

    eleza test_file_link(self):
        os.symlink(self.filelink_target, self.filelink)
        self.assertKweli(os.path.exists(self.filelink))
        self.assertKweli(os.path.isfile(self.filelink))
        self.assertKweli(os.path.islink(self.filelink))
        self.check_stat(self.filelink, self.filelink_target)

    eleza _create_missing_dir_link(self):
        'Create a "directory" link to a non-existent target'
        linkname = self.missing_link
        ikiwa os.path.lexists(linkname):
            os.remove(linkname)
        target = r'c:\\target does sio exist.29r3c740'
        assert sio os.path.exists(target)
        target_is_dir = Kweli
        os.symlink(target, linkname, target_is_dir)

    eleza test_remove_directory_link_to_missing_target(self):
        self._create_missing_dir_link()
        # For compatibility with Unix, os.remove will check the
        #  directory status na call RemoveDirectory ikiwa the symlink
        #  was created with target_is_dir==Kweli.
        os.remove(self.missing_link)

    eleza test_isdir_on_directory_link_to_missing_target(self):
        self._create_missing_dir_link()
        self.assertUongo(os.path.isdir(self.missing_link))

    eleza test_rmdir_on_directory_link_to_missing_target(self):
        self._create_missing_dir_link()
        os.rmdir(self.missing_link)

    eleza check_stat(self, link, target):
        self.assertEqual(os.stat(link), os.stat(target))
        self.assertNotEqual(os.lstat(link), os.stat(link))

        bytes_link = os.fsencode(link)
        self.assertEqual(os.stat(bytes_link), os.stat(target))
        self.assertNotEqual(os.lstat(bytes_link), os.stat(bytes_link))

    eleza test_12084(self):
        level1 = os.path.abspath(support.TESTFN)
        level2 = os.path.join(level1, "level2")
        level3 = os.path.join(level2, "level3")
        self.addCleanup(support.rmtree, level1)

        os.mkdir(level1)
        os.mkdir(level2)
        os.mkdir(level3)

        file1 = os.path.abspath(os.path.join(level1, "file1"))
        create_file(file1)

        orig_dir = os.getcwd()
        jaribu:
            os.chdir(level2)
            link = os.path.join(level2, "link")
            os.symlink(os.path.relpath(file1), "link")
            self.assertIn("link", os.listdir(os.getcwd()))

            # Check os.stat calls kutoka the same dir kama the link
            self.assertEqual(os.stat(file1), os.stat("link"))

            # Check os.stat calls kutoka a dir below the link
            os.chdir(level1)
            self.assertEqual(os.stat(file1),
                             os.stat(os.path.relpath(link)))

            # Check os.stat calls kutoka a dir above the link
            os.chdir(level3)
            self.assertEqual(os.stat(file1),
                             os.stat(os.path.relpath(link)))
        mwishowe:
            os.chdir(orig_dir)

    @unittest.skipUnless(os.path.lexists(r'C:\Users\All Users')
                            na os.path.exists(r'C:\ProgramData'),
                            'Test directories sio found')
    eleza test_29248(self):
        # os.symlink() calls CreateSymbolicLink, which creates
        # the reparse data buffer with the print name stored
        # first, so the offset ni always 0. CreateSymbolicLink
        # stores the "PrintName" DOS path (e.g. "C:\") first,
        # with an offset of 0, followed by the "SubstituteName"
        # NT path (e.g. "\??\C:\"). The "All Users" link, on
        # the other hand, seems to have been created manually
        # with an inverted order.
        target = os.readlink(r'C:\Users\All Users')
        self.assertKweli(os.path.samefile(target, r'C:\ProgramData'))

    eleza test_buffer_overflow(self):
        # Older versions would have a buffer overflow when detecting
        # whether a link source was a directory. This test ensures we
        # no longer crash, but does sio otherwise validate the behavior
        segment = 'X' * 27
        path = os.path.join(*[segment] * 10)
        test_cases = [
            # overflow with absolute src
            ('\\' + path, segment),
            # overflow dest with relative src
            (segment, path),
            # overflow when joining src
            (path[:180], path[:180]),
        ]
        kila src, dest kwenye test_cases:
            jaribu:
                os.symlink(src, dest)
            tatizo FileNotFoundError:
                pita
            isipokua:
                jaribu:
                    os.remove(dest)
                tatizo OSError:
                    pita
            # Also test with bytes, since that ni a separate code path.
            jaribu:
                os.symlink(os.fsencode(src), os.fsencode(dest))
            tatizo FileNotFoundError:
                pita
            isipokua:
                jaribu:
                    os.remove(dest)
                tatizo OSError:
                    pita

    eleza test_appexeclink(self):
        root = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WindowsApps')
        ikiwa sio os.path.isdir(root):
            self.skipTest("test requires a WindowsApps directory")

        aliases = [os.path.join(root, a)
                   kila a kwenye fnmatch.filter(os.listdir(root), '*.exe')]

        kila alias kwenye aliases:
            ikiwa support.verbose:
                andika()
                andika("Testing with", alias)
            st = os.lstat(alias)
            self.assertEqual(st, os.stat(alias))
            self.assertUongo(stat.S_ISLNK(st.st_mode))
            self.assertEqual(st.st_reparse_tag, stat.IO_REPARSE_TAG_APPEXECLINK)
            # testing the first one we see ni sufficient
            koma
        isipokua:
            self.skipTest("test requires an app execution alias")

@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
kundi Win32JunctionTests(unittest.TestCase):
    junction = 'junctiontest'
    junction_target = os.path.dirname(os.path.abspath(__file__))

    eleza setUp(self):
        assert os.path.exists(self.junction_target)
        assert sio os.path.lexists(self.junction)

    eleza tearDown(self):
        ikiwa os.path.lexists(self.junction):
            os.unlink(self.junction)

    eleza test_create_junction(self):
        _winapi.CreateJunction(self.junction_target, self.junction)
        self.assertKweli(os.path.lexists(self.junction))
        self.assertKweli(os.path.exists(self.junction))
        self.assertKweli(os.path.isdir(self.junction))
        self.assertNotEqual(os.stat(self.junction), os.lstat(self.junction))
        self.assertEqual(os.stat(self.junction), os.stat(self.junction_target))

        # bpo-37834: Junctions are sio recognized kama links.
        self.assertUongo(os.path.islink(self.junction))
        self.assertEqual(os.path.normcase("\\\\?\\" + self.junction_target),
                         os.path.normcase(os.readlink(self.junction)))

    eleza test_unlink_removes_junction(self):
        _winapi.CreateJunction(self.junction_target, self.junction)
        self.assertKweli(os.path.exists(self.junction))
        self.assertKweli(os.path.lexists(self.junction))

        os.unlink(self.junction)
        self.assertUongo(os.path.exists(self.junction))

@unittest.skipUnless(sys.platform == "win32", "Win32 specific tests")
kundi Win32NtTests(unittest.TestCase):
    eleza test_getfinalpathname_handles(self):
        nt = support.import_module('nt')
        ctypes = support.import_module('ctypes')
        agiza ctypes.wintypes

        kernel = ctypes.WinDLL('Kernel32.dll', use_last_error=Kweli)
        kernel.GetCurrentProcess.restype = ctypes.wintypes.HANDLE

        kernel.GetProcessHandleCount.restype = ctypes.wintypes.BOOL
        kernel.GetProcessHandleCount.argtypes = (ctypes.wintypes.HANDLE,
                                                 ctypes.wintypes.LPDWORD)

        # This ni a pseudo-handle that doesn't need to be closed
        hproc = kernel.GetCurrentProcess()

        handle_count = ctypes.wintypes.DWORD()
        ok = kernel.GetProcessHandleCount(hproc, ctypes.byref(handle_count))
        self.assertEqual(1, ok)

        before_count = handle_count.value

        # The first two test the error path, __file__ tests the success path
        filenames = [
            r'\\?\C:',
            r'\\?\NUL',
            r'\\?\CONIN',
            __file__,
        ]

        kila _ kwenye range(10):
            kila name kwenye filenames:
                jaribu:
                    nt._getfinalpathname(name)
                tatizo Exception:
                    # Failure ni expected
                    pita
                jaribu:
                    os.stat(name)
                tatizo Exception:
                    pita

        ok = kernel.GetProcessHandleCount(hproc, ctypes.byref(handle_count))
        self.assertEqual(1, ok)

        handle_delta = handle_count.value - before_count

        self.assertEqual(0, handle_delta)

@support.skip_unless_symlink
kundi NonLocalSymlinkTests(unittest.TestCase):

    eleza setUp(self):
        r"""
        Create this structure:

        base
         \___ some_dir
        """
        os.makedirs('base/some_dir')

    eleza tearDown(self):
        shutil.rmtree('base')

    eleza test_directory_link_nonlocal(self):
        """
        The symlink target should resolve relative to the link, sio relative
        to the current directory.

        Then, link base/some_link -> base/some_dir na ensure that some_link
        ni resolved kama a directory.

        In issue13772, it was discovered that directory detection failed if
        the symlink target was sio specified relative to the current
        directory, which was a defect kwenye the implementation.
        """
        src = os.path.join('base', 'some_link')
        os.symlink('some_dir', src)
        assert os.path.isdir(src)


kundi FSEncodingTests(unittest.TestCase):
    eleza test_nop(self):
        self.assertEqual(os.fsencode(b'abc\xff'), b'abc\xff')
        self.assertEqual(os.fsdecode('abc\u0141'), 'abc\u0141')

    eleza test_identity(self):
        # assert fsdecode(fsencode(x)) == x
        kila fn kwenye ('unicode\u0141', 'latin\xe9', 'ascii'):
            jaribu:
                bytesfn = os.fsencode(fn)
            tatizo UnicodeEncodeError:
                endelea
            self.assertEqual(os.fsdecode(bytesfn), fn)



kundi DeviceEncodingTests(unittest.TestCase):

    eleza test_bad_fd(self):
        # Return Tupu when an fd doesn't actually exist.
        self.assertIsTupu(os.device_encoding(123456))

    @unittest.skipUnless(os.isatty(0) na sio win32_is_iot() na (sys.platform.startswith('win') or
            (hasattr(locale, 'nl_langinfo') na hasattr(locale, 'CODESET'))),
            'test requires a tty na either Windows ama nl_langinfo(CODESET)')
    eleza test_device_encoding(self):
        encoding = os.device_encoding(0)
        self.assertIsNotTupu(encoding)
        self.assertKweli(codecs.lookup(encoding))


kundi PidTests(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, 'getppid'), "test needs os.getppid")
    eleza test_getppid(self):
        p = subprocess.Popen([sys.executable, '-c',
                              'agiza os; andika(os.getppid())'],
                             stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        # We are the parent of our subprocess
        self.assertEqual(int(stdout), os.getpid())

    eleza test_waitpid(self):
        args = [sys.executable, '-c', 'pita']
        # Add an implicit test kila PyUnicode_FSConverter().
        pid = os.spawnv(os.P_NOWAIT, FakePath(args[0]), args)
        status = os.waitpid(pid, 0)
        self.assertEqual(status, (pid, 0))


kundi SpawnTests(unittest.TestCase):
    eleza create_args(self, *, with_env=Uongo, use_bytes=Uongo):
        self.exitcode = 17

        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)

        ikiwa sio with_env:
            code = 'agiza sys; sys.exit(%s)' % self.exitcode
        isipokua:
            self.env = dict(os.environ)
            # create an unique key
            self.key = str(uuid.uuid4())
            self.env[self.key] = self.key
            # read the variable kutoka os.environ to check that it exists
            code = ('agiza sys, os; magic = os.environ[%r]; sys.exit(%s)'
                    % (self.key, self.exitcode))

        with open(filename, "w") kama fp:
            fp.write(code)

        args = [sys.executable, filename]
        ikiwa use_bytes:
            args = [os.fsencode(a) kila a kwenye args]
            self.env = {os.fsencode(k): os.fsencode(v)
                        kila k, v kwenye self.env.items()}

        rudisha args

    @requires_os_func('spawnl')
    eleza test_spawnl(self):
        args = self.create_args()
        exitcode = os.spawnl(os.P_WAIT, args[0], *args)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnle')
    eleza test_spawnle(self):
        args = self.create_args(with_env=Kweli)
        exitcode = os.spawnle(os.P_WAIT, args[0], *args, self.env)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnlp')
    eleza test_spawnlp(self):
        args = self.create_args()
        exitcode = os.spawnlp(os.P_WAIT, args[0], *args)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnlpe')
    eleza test_spawnlpe(self):
        args = self.create_args(with_env=Kweli)
        exitcode = os.spawnlpe(os.P_WAIT, args[0], *args, self.env)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnv')
    eleza test_spawnv(self):
        args = self.create_args()
        exitcode = os.spawnv(os.P_WAIT, args[0], args)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnve')
    eleza test_spawnve(self):
        args = self.create_args(with_env=Kweli)
        exitcode = os.spawnve(os.P_WAIT, args[0], args, self.env)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnvp')
    eleza test_spawnvp(self):
        args = self.create_args()
        exitcode = os.spawnvp(os.P_WAIT, args[0], args)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnvpe')
    eleza test_spawnvpe(self):
        args = self.create_args(with_env=Kweli)
        exitcode = os.spawnvpe(os.P_WAIT, args[0], args, self.env)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnv')
    eleza test_nowait(self):
        args = self.create_args()
        pid = os.spawnv(os.P_NOWAIT, args[0], args)
        result = os.waitpid(pid, 0)
        self.assertEqual(result[0], pid)
        status = result[1]
        ikiwa hasattr(os, 'WIFEXITED'):
            self.assertKweli(os.WIFEXITED(status))
            self.assertEqual(os.WEXITSTATUS(status), self.exitcode)
        isipokua:
            self.assertEqual(status, self.exitcode << 8)

    @requires_os_func('spawnve')
    eleza test_spawnve_bytes(self):
        # Test bytes handling kwenye parse_arglist na parse_envlist (#28114)
        args = self.create_args(with_env=Kweli, use_bytes=Kweli)
        exitcode = os.spawnve(os.P_WAIT, args[0], args, self.env)
        self.assertEqual(exitcode, self.exitcode)

    @requires_os_func('spawnl')
    eleza test_spawnl_noargs(self):
        args = self.create_args()
        self.assertRaises(ValueError, os.spawnl, os.P_NOWAIT, args[0])
        self.assertRaises(ValueError, os.spawnl, os.P_NOWAIT, args[0], '')

    @requires_os_func('spawnle')
    eleza test_spawnle_noargs(self):
        args = self.create_args()
        self.assertRaises(ValueError, os.spawnle, os.P_NOWAIT, args[0], {})
        self.assertRaises(ValueError, os.spawnle, os.P_NOWAIT, args[0], '', {})

    @requires_os_func('spawnv')
    eleza test_spawnv_noargs(self):
        args = self.create_args()
        self.assertRaises(ValueError, os.spawnv, os.P_NOWAIT, args[0], ())
        self.assertRaises(ValueError, os.spawnv, os.P_NOWAIT, args[0], [])
        self.assertRaises(ValueError, os.spawnv, os.P_NOWAIT, args[0], ('',))
        self.assertRaises(ValueError, os.spawnv, os.P_NOWAIT, args[0], [''])

    @requires_os_func('spawnve')
    eleza test_spawnve_noargs(self):
        args = self.create_args()
        self.assertRaises(ValueError, os.spawnve, os.P_NOWAIT, args[0], (), {})
        self.assertRaises(ValueError, os.spawnve, os.P_NOWAIT, args[0], [], {})
        self.assertRaises(ValueError, os.spawnve, os.P_NOWAIT, args[0], ('',), {})
        self.assertRaises(ValueError, os.spawnve, os.P_NOWAIT, args[0], [''], {})

    eleza _test_invalid_env(self, spawn):
        args = [sys.executable, '-c', 'pita']

        # null character kwenye the environment variable name
        newenv = os.environ.copy()
        newenv["FRUIT\0VEGETABLE"] = "cabbage"
        jaribu:
            exitcode = spawn(os.P_WAIT, args[0], args, newenv)
        tatizo ValueError:
            pita
        isipokua:
            self.assertEqual(exitcode, 127)

        # null character kwenye the environment variable value
        newenv = os.environ.copy()
        newenv["FRUIT"] = "orange\0VEGETABLE=cabbage"
        jaribu:
            exitcode = spawn(os.P_WAIT, args[0], args, newenv)
        tatizo ValueError:
            pita
        isipokua:
            self.assertEqual(exitcode, 127)

        # equal character kwenye the environment variable name
        newenv = os.environ.copy()
        newenv["FRUIT=ORANGE"] = "lemon"
        jaribu:
            exitcode = spawn(os.P_WAIT, args[0], args, newenv)
        tatizo ValueError:
            pita
        isipokua:
            self.assertEqual(exitcode, 127)

        # equal character kwenye the environment variable value
        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)
        with open(filename, "w") kama fp:
            fp.write('agiza sys, os\n'
                     'ikiwa os.getenv("FRUIT") != "orange=lemon":\n'
                     '    ashiria AssertionError')
        args = [sys.executable, filename]
        newenv = os.environ.copy()
        newenv["FRUIT"] = "orange=lemon"
        exitcode = spawn(os.P_WAIT, args[0], args, newenv)
        self.assertEqual(exitcode, 0)

    @requires_os_func('spawnve')
    eleza test_spawnve_invalid_env(self):
        self._test_invalid_env(os.spawnve)

    @requires_os_func('spawnvpe')
    eleza test_spawnvpe_invalid_env(self):
        self._test_invalid_env(os.spawnvpe)


# The introduction of this TestCase caused at least two different errors on
# *nix buildbots. Temporarily skip this to let the buildbots move along.
@unittest.skip("Skip due to platform/environment differences on *NIX buildbots")
@unittest.skipUnless(hasattr(os, 'getlogin'), "test needs os.getlogin")
kundi LoginTests(unittest.TestCase):
    eleza test_getlogin(self):
        user_name = os.getlogin()
        self.assertNotEqual(len(user_name), 0)


@unittest.skipUnless(hasattr(os, 'getpriority') na hasattr(os, 'setpriority'),
                     "needs os.getpriority na os.setpriority")
kundi ProgramPriorityTests(unittest.TestCase):
    """Tests kila os.getpriority() na os.setpriority()."""

    eleza test_set_get_priority(self):

        base = os.getpriority(os.PRIO_PROCESS, os.getpid())
        os.setpriority(os.PRIO_PROCESS, os.getpid(), base + 1)
        jaribu:
            new_prio = os.getpriority(os.PRIO_PROCESS, os.getpid())
            ikiwa base >= 19 na new_prio <= 19:
                ashiria unittest.SkipTest("unable to reliably test setpriority "
                                        "at current nice level of %s" % base)
            isipokua:
                self.assertEqual(new_prio, base + 1)
        mwishowe:
            jaribu:
                os.setpriority(os.PRIO_PROCESS, os.getpid(), base)
            tatizo OSError kama err:
                ikiwa err.errno != errno.EACCES:
                    ashiria


kundi SendfileTestServer(asyncore.dispatcher, threading.Thread):

    kundi Handler(asynchat.async_chat):

        eleza __init__(self, conn):
            asynchat.async_chat.__init__(self, conn)
            self.in_buffer = []
            self.accumulate = Kweli
            self.closed = Uongo
            self.push(b"220 ready\r\n")

        eleza handle_read(self):
            data = self.recv(4096)
            ikiwa self.accumulate:
                self.in_buffer.append(data)

        eleza get_data(self):
            rudisha b''.join(self.in_buffer)

        eleza handle_close(self):
            self.close()
            self.closed = Kweli

        eleza handle_error(self):
            ashiria

    eleza __init__(self, address):
        threading.Thread.__init__(self)
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.listen(5)
        self.host, self.port = self.socket.getsockname()[:2]
        self.handler_instance = Tupu
        self._active = Uongo
        self._active_lock = threading.Lock()

    # --- public API

    @property
    eleza running(self):
        rudisha self._active

    eleza start(self):
        assert sio self.running
        self.__flag = threading.Event()
        threading.Thread.start(self)
        self.__flag.wait()

    eleza stop(self):
        assert self.running
        self._active = Uongo
        self.join()

    eleza wait(self):
        # wait kila handler connection to be closed, then stop the server
        wakati sio getattr(self.handler_instance, "closed", Uongo):
            time.sleep(0.001)
        self.stop()

    # --- internals

    eleza run(self):
        self._active = Kweli
        self.__flag.set()
        wakati self._active na asyncore.socket_map:
            self._active_lock.acquire()
            asyncore.loop(timeout=0.001, count=1)
            self._active_lock.release()
        asyncore.close_all()

    eleza handle_accept(self):
        conn, addr = self.accept()
        self.handler_instance = self.Handler(conn)

    eleza handle_connect(self):
        self.close()
    handle_read = handle_connect

    eleza writable(self):
        rudisha 0

    eleza handle_error(self):
        ashiria


@unittest.skipUnless(hasattr(os, 'sendfile'), "test needs os.sendfile()")
kundi TestSendfile(unittest.TestCase):

    DATA = b"12345abcde" * 16 * 1024  # 160 KiB
    SUPPORT_HEADERS_TRAILERS = sio sys.platform.startswith("linux") na \
                               sio sys.platform.startswith("solaris") na \
                               sio sys.platform.startswith("sunos")
    requires_headers_trailers = unittest.skipUnless(SUPPORT_HEADERS_TRAILERS,
            'requires headers na trailers support')
    requires_32b = unittest.skipUnless(sys.maxsize < 2**32,
            'test ni only meaningful on 32-bit builds')

    @classmethod
    eleza setUpClass(cls):
        cls.key = support.threading_setup()
        create_file(support.TESTFN, cls.DATA)

    @classmethod
    eleza tearDownClass(cls):
        support.threading_cleanup(*cls.key)
        support.unlink(support.TESTFN)

    eleza setUp(self):
        self.server = SendfileTestServer((support.HOST, 0))
        self.server.start()
        self.client = socket.socket()
        self.client.connect((self.server.host, self.server.port))
        self.client.settimeout(1)
        # synchronize by waiting kila "220 ready" response
        self.client.recv(1024)
        self.sockno = self.client.fileno()
        self.file = open(support.TESTFN, 'rb')
        self.fileno = self.file.fileno()

    eleza tearDown(self):
        self.file.close()
        self.client.close()
        ikiwa self.server.running:
            self.server.stop()
        self.server = Tupu

    eleza sendfile_wrapper(self, *args, **kwargs):
        """A higher level wrapper representing how an application is
        supposed to use sendfile().
        """
        wakati Kweli:
            jaribu:
                rudisha os.sendfile(*args, **kwargs)
            tatizo OSError kama err:
                ikiwa err.errno == errno.ECONNRESET:
                    # disconnected
                    ashiria
                elikiwa err.errno kwenye (errno.EAGAIN, errno.EBUSY):
                    # we have to retry send data
                    endelea
                isipokua:
                    ashiria

    eleza test_send_whole_file(self):
        # normal send
        total_sent = 0
        offset = 0
        nbytes = 4096
        wakati total_sent < len(self.DATA):
            sent = self.sendfile_wrapper(self.sockno, self.fileno, offset, nbytes)
            ikiwa sent == 0:
                koma
            offset += sent
            total_sent += sent
            self.assertKweli(sent <= nbytes)
            self.assertEqual(offset, total_sent)

        self.assertEqual(total_sent, len(self.DATA))
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        self.assertEqual(len(data), len(self.DATA))
        self.assertEqual(data, self.DATA)

    eleza test_send_at_certain_offset(self):
        # start sending a file at a certain offset
        total_sent = 0
        offset = len(self.DATA) // 2
        must_send = len(self.DATA) - offset
        nbytes = 4096
        wakati total_sent < must_send:
            sent = self.sendfile_wrapper(self.sockno, self.fileno, offset, nbytes)
            ikiwa sent == 0:
                koma
            offset += sent
            total_sent += sent
            self.assertKweli(sent <= nbytes)

        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        expected = self.DATA[len(self.DATA) // 2:]
        self.assertEqual(total_sent, len(expected))
        self.assertEqual(len(data), len(expected))
        self.assertEqual(data, expected)

    eleza test_offset_overflow(self):
        # specify an offset > file size
        offset = len(self.DATA) + 4096
        jaribu:
            sent = os.sendfile(self.sockno, self.fileno, offset, 4096)
        tatizo OSError kama e:
            # Solaris can ashiria EINVAL ikiwa offset >= file length, ignore.
            ikiwa e.errno != errno.EINVAL:
                ashiria
        isipokua:
            self.assertEqual(sent, 0)
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        self.assertEqual(data, b'')

    eleza test_invalid_offset(self):
        with self.assertRaises(OSError) kama cm:
            os.sendfile(self.sockno, self.fileno, -1, 4096)
        self.assertEqual(cm.exception.errno, errno.EINVAL)

    eleza test_keywords(self):
        # Keyword arguments should be supported
        os.sendfile(out=self.sockno, offset=0, count=4096,
            **{'in': self.fileno})
        ikiwa self.SUPPORT_HEADERS_TRAILERS:
            os.sendfile(self.sockno, self.fileno, offset=0, count=4096,
                headers=(), trailers=(), flags=0)

    # --- headers / trailers tests

    @requires_headers_trailers
    eleza test_headers(self):
        total_sent = 0
        expected_data = b"x" * 512 + b"y" * 256 + self.DATA[:-1]
        sent = os.sendfile(self.sockno, self.fileno, 0, 4096,
                            headers=[b"x" * 512, b"y" * 256])
        self.assertLessEqual(sent, 512 + 256 + 4096)
        total_sent += sent
        offset = 4096
        wakati total_sent < len(expected_data):
            nbytes = min(len(expected_data) - total_sent, 4096)
            sent = self.sendfile_wrapper(self.sockno, self.fileno,
                                                    offset, nbytes)
            ikiwa sent == 0:
                koma
            self.assertLessEqual(sent, nbytes)
            total_sent += sent
            offset += sent

        self.assertEqual(total_sent, len(expected_data))
        self.client.close()
        self.server.wait()
        data = self.server.handler_instance.get_data()
        self.assertEqual(hash(data), hash(expected_data))

    @requires_headers_trailers
    eleza test_trailers(self):
        TESTFN2 = support.TESTFN + "2"
        file_data = b"abcdef"

        self.addCleanup(support.unlink, TESTFN2)
        create_file(TESTFN2, file_data)

        with open(TESTFN2, 'rb') kama f:
            os.sendfile(self.sockno, f.fileno(), 0, 5,
                        trailers=[b"123456", b"789"])
            self.client.close()
            self.server.wait()
            data = self.server.handler_instance.get_data()
            self.assertEqual(data, b"abcde123456789")

    @requires_headers_trailers
    @requires_32b
    eleza test_headers_overflow_32bits(self):
        self.server.handler_instance.accumulate = Uongo
        with self.assertRaises(OSError) kama cm:
            os.sendfile(self.sockno, self.fileno, 0, 0,
                        headers=[b"x" * 2**16] * 2**15)
        self.assertEqual(cm.exception.errno, errno.EINVAL)

    @requires_headers_trailers
    @requires_32b
    eleza test_trailers_overflow_32bits(self):
        self.server.handler_instance.accumulate = Uongo
        with self.assertRaises(OSError) kama cm:
            os.sendfile(self.sockno, self.fileno, 0, 0,
                        trailers=[b"x" * 2**16] * 2**15)
        self.assertEqual(cm.exception.errno, errno.EINVAL)

    @requires_headers_trailers
    @unittest.skipUnless(hasattr(os, 'SF_NODISKIO'),
                         'test needs os.SF_NODISKIO')
    eleza test_flags(self):
        jaribu:
            os.sendfile(self.sockno, self.fileno, 0, 4096,
                        flags=os.SF_NODISKIO)
        tatizo OSError kama err:
            ikiwa err.errno haiko kwenye (errno.EBUSY, errno.EAGAIN):
                ashiria


eleza supports_extended_attributes():
    ikiwa sio hasattr(os, "setxattr"):
        rudisha Uongo

    jaribu:
        with open(support.TESTFN, "xb", 0) kama fp:
            jaribu:
                os.setxattr(fp.fileno(), b"user.test", b"")
            tatizo OSError:
                rudisha Uongo
    mwishowe:
        support.unlink(support.TESTFN)

    rudisha Kweli


@unittest.skipUnless(supports_extended_attributes(),
                     "no non-broken extended attribute support")
# Kernels < 2.6.39 don't respect setxattr flags.
@support.requires_linux_version(2, 6, 39)
kundi ExtendedAttributeTests(unittest.TestCase):

    eleza _check_xattrs_str(self, s, getxattr, setxattr, removexattr, listxattr, **kwargs):
        fn = support.TESTFN
        self.addCleanup(support.unlink, fn)
        create_file(fn)

        with self.assertRaises(OSError) kama cm:
            getxattr(fn, s("user.test"), **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENODATA)

        init_xattr = listxattr(fn)
        self.assertIsInstance(init_xattr, list)

        setxattr(fn, s("user.test"), b"", **kwargs)
        xattr = set(init_xattr)
        xattr.add("user.test")
        self.assertEqual(set(listxattr(fn)), xattr)
        self.assertEqual(getxattr(fn, b"user.test", **kwargs), b"")
        setxattr(fn, s("user.test"), b"hello", os.XATTR_REPLACE, **kwargs)
        self.assertEqual(getxattr(fn, b"user.test", **kwargs), b"hello")

        with self.assertRaises(OSError) kama cm:
            setxattr(fn, s("user.test"), b"bye", os.XATTR_CREATE, **kwargs)
        self.assertEqual(cm.exception.errno, errno.EEXIST)

        with self.assertRaises(OSError) kama cm:
            setxattr(fn, s("user.test2"), b"bye", os.XATTR_REPLACE, **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENODATA)

        setxattr(fn, s("user.test2"), b"foo", os.XATTR_CREATE, **kwargs)
        xattr.add("user.test2")
        self.assertEqual(set(listxattr(fn)), xattr)
        removexattr(fn, s("user.test"), **kwargs)

        with self.assertRaises(OSError) kama cm:
            getxattr(fn, s("user.test"), **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENODATA)

        xattr.remove("user.test")
        self.assertEqual(set(listxattr(fn)), xattr)
        self.assertEqual(getxattr(fn, s("user.test2"), **kwargs), b"foo")
        setxattr(fn, s("user.test"), b"a"*1024, **kwargs)
        self.assertEqual(getxattr(fn, s("user.test"), **kwargs), b"a"*1024)
        removexattr(fn, s("user.test"), **kwargs)
        many = sorted("user.test{}".format(i) kila i kwenye range(100))
        kila thing kwenye many:
            setxattr(fn, thing, b"x", **kwargs)
        self.assertEqual(set(listxattr(fn)), set(init_xattr) | set(many))

    eleza _check_xattrs(self, *args, **kwargs):
        self._check_xattrs_str(str, *args, **kwargs)
        support.unlink(support.TESTFN)

        self._check_xattrs_str(os.fsencode, *args, **kwargs)
        support.unlink(support.TESTFN)

    eleza test_simple(self):
        self._check_xattrs(os.getxattr, os.setxattr, os.removexattr,
                           os.listxattr)

    eleza test_lpath(self):
        self._check_xattrs(os.getxattr, os.setxattr, os.removexattr,
                           os.listxattr, follow_symlinks=Uongo)

    eleza test_fds(self):
        eleza getxattr(path, *args):
            with open(path, "rb") kama fp:
                rudisha os.getxattr(fp.fileno(), *args)
        eleza setxattr(path, *args):
            with open(path, "wb", 0) kama fp:
                os.setxattr(fp.fileno(), *args)
        eleza removexattr(path, *args):
            with open(path, "wb", 0) kama fp:
                os.removexattr(fp.fileno(), *args)
        eleza listxattr(path, *args):
            with open(path, "rb") kama fp:
                rudisha os.listxattr(fp.fileno(), *args)
        self._check_xattrs(getxattr, setxattr, removexattr, listxattr)


@unittest.skipUnless(hasattr(os, 'get_terminal_size'), "requires os.get_terminal_size")
kundi TermsizeTests(unittest.TestCase):
    eleza test_does_not_crash(self):
        """Check ikiwa get_terminal_size() rudishas a meaningful value.

        There's no easy portable way to actually check the size of the
        terminal, so let's check ikiwa it rudishas something sensible instead.
        """
        jaribu:
            size = os.get_terminal_size()
        tatizo OSError kama e:
            ikiwa sys.platform == "win32" ama e.errno kwenye (errno.EINVAL, errno.ENOTTY):
                # Under win32 a generic OSError can be thrown ikiwa the
                # handle cannot be retrieved
                self.skipTest("failed to query terminal size")
            ashiria

        self.assertGreaterEqual(size.columns, 0)
        self.assertGreaterEqual(size.lines, 0)

    eleza test_stty_match(self):
        """Check ikiwa stty rudishas the same results

        stty actually tests stdin, so get_terminal_size ni invoked on
        stdin explicitly. If stty succeeded, then get_terminal_size()
        should work too.
        """
        jaribu:
            size = subprocess.check_output(['stty', 'size']).decode().split()
        tatizo (FileNotFoundError, subprocess.CalledProcessError,
                PermissionError):
            self.skipTest("stty invocation failed")
        expected = (int(size[1]), int(size[0])) # reversed order

        jaribu:
            actual = os.get_terminal_size(sys.__stdin__.fileno())
        tatizo OSError kama e:
            ikiwa sys.platform == "win32" ama e.errno kwenye (errno.EINVAL, errno.ENOTTY):
                # Under win32 a generic OSError can be thrown ikiwa the
                # handle cannot be retrieved
                self.skipTest("failed to query terminal size")
            ashiria
        self.assertEqual(expected, actual)


@unittest.skipUnless(hasattr(os, 'memfd_create'), 'requires os.memfd_create')
@support.requires_linux_version(3, 17)
kundi MemfdCreateTests(unittest.TestCase):
    eleza test_memfd_create(self):
        fd = os.memfd_create("Hi", os.MFD_CLOEXEC)
        self.assertNotEqual(fd, -1)
        self.addCleanup(os.close, fd)
        self.assertUongo(os.get_inheritable(fd))
        with open(fd, "wb", closefd=Uongo) kama f:
            f.write(b'memfd_create')
            self.assertEqual(f.tell(), 12)

        fd2 = os.memfd_create("Hi")
        self.addCleanup(os.close, fd2)
        self.assertUongo(os.get_inheritable(fd2))


kundi OSErrorTests(unittest.TestCase):
    eleza setUp(self):
        kundi Str(str):
            pita

        self.bytes_filenames = []
        self.unicode_filenames = []
        ikiwa support.TESTFN_UNENCODABLE ni sio Tupu:
            decoded = support.TESTFN_UNENCODABLE
        isipokua:
            decoded = support.TESTFN
        self.unicode_filenames.append(decoded)
        self.unicode_filenames.append(Str(decoded))
        ikiwa support.TESTFN_UNDECODABLE ni sio Tupu:
            encoded = support.TESTFN_UNDECODABLE
        isipokua:
            encoded = os.fsencode(support.TESTFN)
        self.bytes_filenames.append(encoded)
        self.bytes_filenames.append(bytearray(encoded))
        self.bytes_filenames.append(memoryview(encoded))

        self.filenames = self.bytes_filenames + self.unicode_filenames

    eleza test_oserror_filename(self):
        funcs = [
            (self.filenames, os.chdir,),
            (self.filenames, os.chmod, 0o777),
            (self.filenames, os.lstat,),
            (self.filenames, os.open, os.O_RDONLY),
            (self.filenames, os.rmdir,),
            (self.filenames, os.stat,),
            (self.filenames, os.unlink,),
        ]
        ikiwa sys.platform == "win32":
            funcs.extend((
                (self.bytes_filenames, os.rename, b"dst"),
                (self.bytes_filenames, os.replace, b"dst"),
                (self.unicode_filenames, os.rename, "dst"),
                (self.unicode_filenames, os.replace, "dst"),
                (self.unicode_filenames, os.listdir, ),
            ))
        isipokua:
            funcs.extend((
                (self.filenames, os.listdir,),
                (self.filenames, os.rename, "dst"),
                (self.filenames, os.replace, "dst"),
            ))
        ikiwa hasattr(os, "chown"):
            funcs.append((self.filenames, os.chown, 0, 0))
        ikiwa hasattr(os, "lchown"):
            funcs.append((self.filenames, os.lchown, 0, 0))
        ikiwa hasattr(os, "truncate"):
            funcs.append((self.filenames, os.truncate, 0))
        ikiwa hasattr(os, "chflags"):
            funcs.append((self.filenames, os.chflags, 0))
        ikiwa hasattr(os, "lchflags"):
            funcs.append((self.filenames, os.lchflags, 0))
        ikiwa hasattr(os, "chroot"):
            funcs.append((self.filenames, os.chroot,))
        ikiwa hasattr(os, "link"):
            ikiwa sys.platform == "win32":
                funcs.append((self.bytes_filenames, os.link, b"dst"))
                funcs.append((self.unicode_filenames, os.link, "dst"))
            isipokua:
                funcs.append((self.filenames, os.link, "dst"))
        ikiwa hasattr(os, "listxattr"):
            funcs.extend((
                (self.filenames, os.listxattr,),
                (self.filenames, os.getxattr, "user.test"),
                (self.filenames, os.setxattr, "user.test", b'user'),
                (self.filenames, os.removexattr, "user.test"),
            ))
        ikiwa hasattr(os, "lchmod"):
            funcs.append((self.filenames, os.lchmod, 0o777))
        ikiwa hasattr(os, "readlink"):
            funcs.append((self.filenames, os.readlink,))


        kila filenames, func, *func_args kwenye funcs:
            kila name kwenye filenames:
                jaribu:
                    ikiwa isinstance(name, (str, bytes)):
                        func(name, *func_args)
                    isipokua:
                        with self.assertWarnsRegex(DeprecationWarning, 'should be'):
                            func(name, *func_args)
                tatizo OSError kama err:
                    self.assertIs(err.filename, name, str(func))
                tatizo UnicodeDecodeError:
                    pita
                isipokua:
                    self.fail("No exception thrown by {}".format(func))

kundi CPUCountTests(unittest.TestCase):
    eleza test_cpu_count(self):
        cpus = os.cpu_count()
        ikiwa cpus ni sio Tupu:
            self.assertIsInstance(cpus, int)
            self.assertGreater(cpus, 0)
        isipokua:
            self.skipTest("Could sio determine the number of CPUs")


kundi FDInheritanceTests(unittest.TestCase):
    eleza test_get_set_inheritable(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(os.get_inheritable(fd), Uongo)

        os.set_inheritable(fd, Kweli)
        self.assertEqual(os.get_inheritable(fd), Kweli)

    @unittest.skipIf(fcntl ni Tupu, "need fcntl")
    eleza test_get_inheritable_cloexec(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(os.get_inheritable(fd), Uongo)

        # clear FD_CLOEXEC flag
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        flags &= ~fcntl.FD_CLOEXEC
        fcntl.fcntl(fd, fcntl.F_SETFD, flags)

        self.assertEqual(os.get_inheritable(fd), Kweli)

    @unittest.skipIf(fcntl ni Tupu, "need fcntl")
    eleza test_set_inheritable_cloexec(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC,
                         fcntl.FD_CLOEXEC)

        os.set_inheritable(fd, Kweli)
        self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC,
                         0)

    eleza test_open(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(os.get_inheritable(fd), Uongo)

    @unittest.skipUnless(hasattr(os, 'pipe'), "need os.pipe()")
    eleza test_pipe(self):
        rfd, wfd = os.pipe()
        self.addCleanup(os.close, rfd)
        self.addCleanup(os.close, wfd)
        self.assertEqual(os.get_inheritable(rfd), Uongo)
        self.assertEqual(os.get_inheritable(wfd), Uongo)

    eleza test_dup(self):
        fd1 = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd1)

        fd2 = os.dup(fd1)
        self.addCleanup(os.close, fd2)
        self.assertEqual(os.get_inheritable(fd2), Uongo)

    eleza test_dup_standard_stream(self):
        fd = os.dup(1)
        self.addCleanup(os.close, fd)
        self.assertGreater(fd, 0)

    @unittest.skipUnless(sys.platform == 'win32', 'win32-specific test')
    eleza test_dup_nul(self):
        # os.dup() was creating inheritable fds kila character files.
        fd1 = os.open('NUL', os.O_RDONLY)
        self.addCleanup(os.close, fd1)
        fd2 = os.dup(fd1)
        self.addCleanup(os.close, fd2)
        self.assertUongo(os.get_inheritable(fd2))

    @unittest.skipUnless(hasattr(os, 'dup2'), "need os.dup2()")
    eleza test_dup2(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)

        # inheritable by default
        fd2 = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd2)
        self.assertEqual(os.dup2(fd, fd2), fd2)
        self.assertKweli(os.get_inheritable(fd2))

        # force non-inheritable
        fd3 = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd3)
        self.assertEqual(os.dup2(fd, fd3, inheritable=Uongo), fd3)
        self.assertUongo(os.get_inheritable(fd3))

    @unittest.skipUnless(hasattr(os, 'openpty'), "need os.openpty()")
    eleza test_openpty(self):
        master_fd, slave_fd = os.openpty()
        self.addCleanup(os.close, master_fd)
        self.addCleanup(os.close, slave_fd)
        self.assertEqual(os.get_inheritable(master_fd), Uongo)
        self.assertEqual(os.get_inheritable(slave_fd), Uongo)


kundi PathTConverterTests(unittest.TestCase):
    # tuples of (function name, allows fd arguments, additional arguments to
    # function, cleanup function)
    functions = [
        ('stat', Kweli, (), Tupu),
        ('lstat', Uongo, (), Tupu),
        ('access', Uongo, (os.F_OK,), Tupu),
        ('chflags', Uongo, (0,), Tupu),
        ('lchflags', Uongo, (0,), Tupu),
        ('open', Uongo, (0,), getattr(os, 'close', Tupu)),
    ]

    eleza test_path_t_converter(self):
        str_filename = support.TESTFN
        ikiwa os.name == 'nt':
            bytes_fspath = bytes_filename = Tupu
        isipokua:
            bytes_filename = support.TESTFN.encode('ascii')
            bytes_fspath = FakePath(bytes_filename)
        fd = os.open(FakePath(str_filename), os.O_WRONLY|os.O_CREAT)
        self.addCleanup(support.unlink, support.TESTFN)
        self.addCleanup(os.close, fd)

        int_fspath = FakePath(fd)
        str_fspath = FakePath(str_filename)

        kila name, allow_fd, extra_args, cleanup_fn kwenye self.functions:
            with self.subTest(name=name):
                jaribu:
                    fn = getattr(os, name)
                tatizo AttributeError:
                    endelea

                kila path kwenye (str_filename, bytes_filename, str_fspath,
                             bytes_fspath):
                    ikiwa path ni Tupu:
                        endelea
                    with self.subTest(name=name, path=path):
                        result = fn(path, *extra_args)
                        ikiwa cleanup_fn ni sio Tupu:
                            cleanup_fn(result)

                with self.assertRaisesRegex(
                        TypeError, 'to rudisha str ama bytes'):
                    fn(int_fspath, *extra_args)

                ikiwa allow_fd:
                    result = fn(fd, *extra_args)  # should sio fail
                    ikiwa cleanup_fn ni sio Tupu:
                        cleanup_fn(result)
                isipokua:
                    with self.assertRaisesRegex(
                            TypeError,
                            'os.PathLike'):
                        fn(fd, *extra_args)

    eleza test_path_t_converter_and_custom_class(self):
        msg = r'__fspath__\(\) to rudisha str ama bytes, sio %s'
        with self.assertRaisesRegex(TypeError, msg % r'int'):
            os.stat(FakePath(2))
        with self.assertRaisesRegex(TypeError, msg % r'float'):
            os.stat(FakePath(2.34))
        with self.assertRaisesRegex(TypeError, msg % r'object'):
            os.stat(FakePath(object()))


@unittest.skipUnless(hasattr(os, 'get_blocking'),
                     'needs os.get_blocking() na os.set_blocking()')
kundi BlockingTests(unittest.TestCase):
    eleza test_blocking(self):
        fd = os.open(__file__, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertEqual(os.get_blocking(fd), Kweli)

        os.set_blocking(fd, Uongo)
        self.assertEqual(os.get_blocking(fd), Uongo)

        os.set_blocking(fd, Kweli)
        self.assertEqual(os.get_blocking(fd), Kweli)



kundi ExportsTests(unittest.TestCase):
    eleza test_os_all(self):
        self.assertIn('open', os.__all__)
        self.assertIn('walk', os.__all__)


kundi TestScandir(unittest.TestCase):
    check_no_resource_warning = support.check_no_resource_warning

    eleza setUp(self):
        self.path = os.path.realpath(support.TESTFN)
        self.bytes_path = os.fsencode(self.path)
        self.addCleanup(support.rmtree, self.path)
        os.mkdir(self.path)

    eleza create_file(self, name="file.txt"):
        path = self.bytes_path ikiwa isinstance(name, bytes) else self.path
        filename = os.path.join(path, name)
        create_file(filename, b'python')
        rudisha filename

    eleza get_entries(self, names):
        entries = dict((entry.name, entry)
                       kila entry kwenye os.scandir(self.path))
        self.assertEqual(sorted(entries.keys()), names)
        rudisha entries

    eleza assert_stat_equal(self, stat1, stat2, skip_fields):
        ikiwa skip_fields:
            kila attr kwenye dir(stat1):
                ikiwa sio attr.startswith("st_"):
                    endelea
                ikiwa attr kwenye ("st_dev", "st_ino", "st_nlink"):
                    endelea
                self.assertEqual(getattr(stat1, attr),
                                 getattr(stat2, attr),
                                 (stat1, stat2, attr))
        isipokua:
            self.assertEqual(stat1, stat2)

    eleza check_entry(self, entry, name, is_dir, is_file, is_symlink):
        self.assertIsInstance(entry, os.DirEntry)
        self.assertEqual(entry.name, name)
        self.assertEqual(entry.path, os.path.join(self.path, name))
        self.assertEqual(entry.inode(),
                         os.stat(entry.path, follow_symlinks=Uongo).st_ino)

        entry_stat = os.stat(entry.path)
        self.assertEqual(entry.is_dir(),
                         stat.S_ISDIR(entry_stat.st_mode))
        self.assertEqual(entry.is_file(),
                         stat.S_ISREG(entry_stat.st_mode))
        self.assertEqual(entry.is_symlink(),
                         os.path.islink(entry.path))

        entry_lstat = os.stat(entry.path, follow_symlinks=Uongo)
        self.assertEqual(entry.is_dir(follow_symlinks=Uongo),
                         stat.S_ISDIR(entry_lstat.st_mode))
        self.assertEqual(entry.is_file(follow_symlinks=Uongo),
                         stat.S_ISREG(entry_lstat.st_mode))

        self.assert_stat_equal(entry.stat(),
                               entry_stat,
                               os.name == 'nt' na sio is_symlink)
        self.assert_stat_equal(entry.stat(follow_symlinks=Uongo),
                               entry_lstat,
                               os.name == 'nt')

    eleza test_attributes(self):
        link = hasattr(os, 'link')
        symlink = support.can_symlink()

        dirname = os.path.join(self.path, "dir")
        os.mkdir(dirname)
        filename = self.create_file("file.txt")
        ikiwa link:
            jaribu:
                os.link(filename, os.path.join(self.path, "link_file.txt"))
            tatizo PermissionError kama e:
                self.skipTest('os.link(): %s' % e)
        ikiwa symlink:
            os.symlink(dirname, os.path.join(self.path, "symlink_dir"),
                       target_is_directory=Kweli)
            os.symlink(filename, os.path.join(self.path, "symlink_file.txt"))

        names = ['dir', 'file.txt']
        ikiwa link:
            names.append('link_file.txt')
        ikiwa symlink:
            names.extend(('symlink_dir', 'symlink_file.txt'))
        entries = self.get_entries(names)

        entry = entries['dir']
        self.check_entry(entry, 'dir', Kweli, Uongo, Uongo)

        entry = entries['file.txt']
        self.check_entry(entry, 'file.txt', Uongo, Kweli, Uongo)

        ikiwa link:
            entry = entries['link_file.txt']
            self.check_entry(entry, 'link_file.txt', Uongo, Kweli, Uongo)

        ikiwa symlink:
            entry = entries['symlink_dir']
            self.check_entry(entry, 'symlink_dir', Kweli, Uongo, Kweli)

            entry = entries['symlink_file.txt']
            self.check_entry(entry, 'symlink_file.txt', Uongo, Kweli, Kweli)

    eleza get_entry(self, name):
        path = self.bytes_path ikiwa isinstance(name, bytes) else self.path
        entries = list(os.scandir(path))
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry.name, name)
        rudisha entry

    eleza create_file_entry(self, name='file.txt'):
        filename = self.create_file(name=name)
        rudisha self.get_entry(os.path.basename(filename))

    eleza test_current_directory(self):
        filename = self.create_file()
        old_dir = os.getcwd()
        jaribu:
            os.chdir(self.path)

            # call scandir() without parameter: it must list the content
            # of the current directory
            entries = dict((entry.name, entry) kila entry kwenye os.scandir())
            self.assertEqual(sorted(entries.keys()),
                             [os.path.basename(filename)])
        mwishowe:
            os.chdir(old_dir)

    eleza test_repr(self):
        entry = self.create_file_entry()
        self.assertEqual(repr(entry), "<DirEntry 'file.txt'>")

    eleza test_fspath_protocol(self):
        entry = self.create_file_entry()
        self.assertEqual(os.fspath(entry), os.path.join(self.path, 'file.txt'))

    eleza test_fspath_protocol_bytes(self):
        bytes_filename = os.fsencode('bytesfile.txt')
        bytes_entry = self.create_file_entry(name=bytes_filename)
        fspath = os.fspath(bytes_entry)
        self.assertIsInstance(fspath, bytes)
        self.assertEqual(fspath,
                         os.path.join(os.fsencode(self.path),bytes_filename))

    eleza test_removed_dir(self):
        path = os.path.join(self.path, 'dir')

        os.mkdir(path)
        entry = self.get_entry('dir')
        os.rmdir(path)

        # On POSIX, is_dir() result depends ikiwa scandir() filled d_type ama not
        ikiwa os.name == 'nt':
            self.assertKweli(entry.is_dir())
        self.assertUongo(entry.is_file())
        self.assertUongo(entry.is_symlink())
        ikiwa os.name == 'nt':
            self.assertRaises(FileNotFoundError, entry.inode)
            # don't fail
            entry.stat()
            entry.stat(follow_symlinks=Uongo)
        isipokua:
            self.assertGreater(entry.inode(), 0)
            self.assertRaises(FileNotFoundError, entry.stat)
            self.assertRaises(FileNotFoundError, entry.stat, follow_symlinks=Uongo)

    eleza test_removed_file(self):
        entry = self.create_file_entry()
        os.unlink(entry.path)

        self.assertUongo(entry.is_dir())
        # On POSIX, is_dir() result depends ikiwa scandir() filled d_type ama not
        ikiwa os.name == 'nt':
            self.assertKweli(entry.is_file())
        self.assertUongo(entry.is_symlink())
        ikiwa os.name == 'nt':
            self.assertRaises(FileNotFoundError, entry.inode)
            # don't fail
            entry.stat()
            entry.stat(follow_symlinks=Uongo)
        isipokua:
            self.assertGreater(entry.inode(), 0)
            self.assertRaises(FileNotFoundError, entry.stat)
            self.assertRaises(FileNotFoundError, entry.stat, follow_symlinks=Uongo)

    eleza test_broken_symlink(self):
        ikiwa sio support.can_symlink():
            rudisha self.skipTest('cannot create symbolic link')

        filename = self.create_file("file.txt")
        os.symlink(filename,
                   os.path.join(self.path, "symlink.txt"))
        entries = self.get_entries(['file.txt', 'symlink.txt'])
        entry = entries['symlink.txt']
        os.unlink(filename)

        self.assertGreater(entry.inode(), 0)
        self.assertUongo(entry.is_dir())
        self.assertUongo(entry.is_file())  # broken symlink rudishas Uongo
        self.assertUongo(entry.is_dir(follow_symlinks=Uongo))
        self.assertUongo(entry.is_file(follow_symlinks=Uongo))
        self.assertKweli(entry.is_symlink())
        self.assertRaises(FileNotFoundError, entry.stat)
        # don't fail
        entry.stat(follow_symlinks=Uongo)

    eleza test_bytes(self):
        self.create_file("file.txt")

        path_bytes = os.fsencode(self.path)
        entries = list(os.scandir(path_bytes))
        self.assertEqual(len(entries), 1, entries)
        entry = entries[0]

        self.assertEqual(entry.name, b'file.txt')
        self.assertEqual(entry.path,
                         os.fsencode(os.path.join(self.path, 'file.txt')))

    eleza test_bytes_like(self):
        self.create_file("file.txt")

        kila cls kwenye bytearray, memoryview:
            path_bytes = cls(os.fsencode(self.path))
            with self.assertWarns(DeprecationWarning):
                entries = list(os.scandir(path_bytes))
            self.assertEqual(len(entries), 1, entries)
            entry = entries[0]

            self.assertEqual(entry.name, b'file.txt')
            self.assertEqual(entry.path,
                             os.fsencode(os.path.join(self.path, 'file.txt')))
            self.assertIs(type(entry.name), bytes)
            self.assertIs(type(entry.path), bytes)

    @unittest.skipUnless(os.listdir kwenye os.supports_fd,
                         'fd support kila listdir required kila this test.')
    eleza test_fd(self):
        self.assertIn(os.scandir, os.supports_fd)
        self.create_file('file.txt')
        expected_names = ['file.txt']
        ikiwa support.can_symlink():
            os.symlink('file.txt', os.path.join(self.path, 'link'))
            expected_names.append('link')

        fd = os.open(self.path, os.O_RDONLY)
        jaribu:
            with os.scandir(fd) kama it:
                entries = list(it)
            names = [entry.name kila entry kwenye entries]
            self.assertEqual(sorted(names), expected_names)
            self.assertEqual(names, os.listdir(fd))
            kila entry kwenye entries:
                self.assertEqual(entry.path, entry.name)
                self.assertEqual(os.fspath(entry), entry.name)
                self.assertEqual(entry.is_symlink(), entry.name == 'link')
                ikiwa os.stat kwenye os.supports_dir_fd:
                    st = os.stat(entry.name, dir_fd=fd)
                    self.assertEqual(entry.stat(), st)
                    st = os.stat(entry.name, dir_fd=fd, follow_symlinks=Uongo)
                    self.assertEqual(entry.stat(follow_symlinks=Uongo), st)
        mwishowe:
            os.close(fd)

    eleza test_empty_path(self):
        self.assertRaises(FileNotFoundError, os.scandir, '')

    eleza test_consume_iterator_twice(self):
        self.create_file("file.txt")
        iterator = os.scandir(self.path)

        entries = list(iterator)
        self.assertEqual(len(entries), 1, entries)

        # check than consuming the iterator twice doesn't ashiria exception
        entries2 = list(iterator)
        self.assertEqual(len(entries2), 0, entries2)

    eleza test_bad_path_type(self):
        kila obj kwenye [1.234, {}, []]:
            self.assertRaises(TypeError, os.scandir, obj)

    eleza test_close(self):
        self.create_file("file.txt")
        self.create_file("file2.txt")
        iterator = os.scandir(self.path)
        next(iterator)
        iterator.close()
        # multiple closes
        iterator.close()
        with self.check_no_resource_warning():
            toa iterator

    eleza test_context_manager(self):
        self.create_file("file.txt")
        self.create_file("file2.txt")
        with os.scandir(self.path) kama iterator:
            next(iterator)
        with self.check_no_resource_warning():
            toa iterator

    eleza test_context_manager_close(self):
        self.create_file("file.txt")
        self.create_file("file2.txt")
        with os.scandir(self.path) kama iterator:
            next(iterator)
            iterator.close()

    eleza test_context_manager_exception(self):
        self.create_file("file.txt")
        self.create_file("file2.txt")
        with self.assertRaises(ZeroDivisionError):
            with os.scandir(self.path) kama iterator:
                next(iterator)
                1/0
        with self.check_no_resource_warning():
            toa iterator

    eleza test_resource_warning(self):
        self.create_file("file.txt")
        self.create_file("file2.txt")
        iterator = os.scandir(self.path)
        next(iterator)
        with self.assertWarns(ResourceWarning):
            toa iterator
            support.gc_collect()
        # exhausted iterator
        iterator = os.scandir(self.path)
        list(iterator)
        with self.check_no_resource_warning():
            toa iterator


kundi TestPEP519(unittest.TestCase):

    # Abstracted so it can be overridden to test pure Python implementation
    # ikiwa a C version ni provided.
    fspath = staticmethod(os.fspath)

    eleza test_rudisha_bytes(self):
        kila b kwenye b'hello', b'goodbye', b'some/path/and/file':
            self.assertEqual(b, self.fspath(b))

    eleza test_rudisha_string(self):
        kila s kwenye 'hello', 'goodbye', 'some/path/and/file':
            self.assertEqual(s, self.fspath(s))

    eleza test_fsencode_fsdecode(self):
        kila p kwenye "path/like/object", b"path/like/object":
            pathlike = FakePath(p)

            self.assertEqual(p, self.fspath(pathlike))
            self.assertEqual(b"path/like/object", os.fsencode(pathlike))
            self.assertEqual("path/like/object", os.fsdecode(pathlike))

    eleza test_pathlike(self):
        self.assertEqual('#feelthegil', self.fspath(FakePath('#feelthegil')))
        self.assertKweli(issubclass(FakePath, os.PathLike))
        self.assertKweli(isinstance(FakePath('x'), os.PathLike))

    eleza test_garbage_in_exception_out(self):
        vapor = type('blah', (), {})
        kila o kwenye int, type, os, vapor():
            self.assertRaises(TypeError, self.fspath, o)

    eleza test_argument_required(self):
        self.assertRaises(TypeError, self.fspath)

    eleza test_bad_pathlike(self):
        # __fspath__ rudishas a value other than str ama bytes.
        self.assertRaises(TypeError, self.fspath, FakePath(42))
        # __fspath__ attribute that ni sio callable.
        c = type('foo', (), {})
        c.__fspath__ = 1
        self.assertRaises(TypeError, self.fspath, c())
        # __fspath__ ashirias an exception.
        self.assertRaises(ZeroDivisionError, self.fspath,
                          FakePath(ZeroDivisionError()))


kundi TimesTests(unittest.TestCase):
    eleza test_times(self):
        times = os.times()
        self.assertIsInstance(times, os.times_result)

        kila field kwenye ('user', 'system', 'children_user', 'children_system',
                      'elapsed'):
            value = getattr(times, field)
            self.assertIsInstance(value, float)

        ikiwa os.name == 'nt':
            self.assertEqual(times.children_user, 0)
            self.assertEqual(times.children_system, 0)
            self.assertEqual(times.elapsed, 0)


# Only test ikiwa the C version ni provided, otherwise TestPEP519 already tested
# the pure Python implementation.
ikiwa hasattr(os, "_fspath"):
    kundi TestPEP519PurePython(TestPEP519):

        """Explicitly test the pure Python implementation of os.fspath()."""

        fspath = staticmethod(os._fspath)


ikiwa __name__ == "__main__":
    unittest.main()
