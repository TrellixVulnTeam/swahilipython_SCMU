"Test posix functions"

kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok

# Skip these tests ikiwa there ni no posix module.
posix = support.import_module('posix')

agiza errno
agiza sys
agiza signal
agiza time
agiza os
agiza platform
agiza pwd
agiza stat
agiza tempfile
agiza unittest
agiza warnings
agiza textwrap

_DUMMY_SYMLINK = os.path.join(tempfile.gettempdir(),
                              support.TESTFN + '-dummy-symlink')

requires_32b = unittest.skipUnless(sys.maxsize < 2**32,
        'test ni only meaningful on 32-bit builds')

eleza _supports_sched():
    ikiwa sio hasattr(posix, 'sched_getscheduler'):
        rudisha Uongo
    jaribu:
        posix.sched_getscheduler(0)
    tatizo OSError kama e:
        ikiwa e.errno == errno.ENOSYS:
            rudisha Uongo
    rudisha Kweli

requires_sched = unittest.skipUnless(_supports_sched(), 'requires POSIX scheduler API')

kundi PosixTester(unittest.TestCase):

    eleza setUp(self):
        # create empty file
        fp = open(support.TESTFN, 'w+')
        fp.close()
        self.teardown_files = [ support.TESTFN ]
        self._warnings_manager = support.check_warnings()
        self._warnings_manager.__enter__()
        warnings.filterwarnings('ignore', '.* potential security risk .*',
                                RuntimeWarning)

    eleza tearDown(self):
        kila teardown_file kwenye self.teardown_files:
            support.unlink(teardown_file)
        self._warnings_manager.__exit__(Tupu, Tupu, Tupu)

    eleza testNoArgFunctions(self):
        # test posix functions which take no arguments na have
        # no side-effects which we need to cleanup (e.g., fork, wait, abort)
        NO_ARG_FUNCTIONS = [ "ctermid", "getcwd", "getcwdb", "uname",
                             "times", "getloadavg",
                             "getegid", "geteuid", "getgid", "getgroups",
                             "getpid", "getpgrp", "getppid", "getuid", "sync",
                           ]

        kila name kwenye NO_ARG_FUNCTIONS:
            posix_func = getattr(posix, name, Tupu)
            ikiwa posix_func ni sio Tupu:
                posix_func()
                self.assertRaises(TypeError, posix_func, 1)

    @unittest.skipUnless(hasattr(posix, 'getresuid'),
                         'test needs posix.getresuid()')
    eleza test_getresuid(self):
        user_ids = posix.getresuid()
        self.assertEqual(len(user_ids), 3)
        kila val kwenye user_ids:
            self.assertGreaterEqual(val, 0)

    @unittest.skipUnless(hasattr(posix, 'getresgid'),
                         'test needs posix.getresgid()')
    eleza test_getresgid(self):
        group_ids = posix.getresgid()
        self.assertEqual(len(group_ids), 3)
        kila val kwenye group_ids:
            self.assertGreaterEqual(val, 0)

    @unittest.skipUnless(hasattr(posix, 'setresuid'),
                         'test needs posix.setresuid()')
    eleza test_setresuid(self):
        current_user_ids = posix.getresuid()
        self.assertIsTupu(posix.setresuid(*current_user_ids))
        # -1 means don't change that value.
        self.assertIsTupu(posix.setresuid(-1, -1, -1))

    @unittest.skipUnless(hasattr(posix, 'setresuid'),
                         'test needs posix.setresuid()')
    eleza test_setresuid_exception(self):
        # Don't do this test ikiwa someone ni silly enough to run us kama root.
        current_user_ids = posix.getresuid()
        ikiwa 0 haiko kwenye current_user_ids:
            new_user_ids = (current_user_ids[0]+1, -1, -1)
            self.assertRaises(OSError, posix.setresuid, *new_user_ids)

    @unittest.skipUnless(hasattr(posix, 'setresgid'),
                         'test needs posix.setresgid()')
    eleza test_setresgid(self):
        current_group_ids = posix.getresgid()
        self.assertIsTupu(posix.setresgid(*current_group_ids))
        # -1 means don't change that value.
        self.assertIsTupu(posix.setresgid(-1, -1, -1))

    @unittest.skipUnless(hasattr(posix, 'setresgid'),
                         'test needs posix.setresgid()')
    eleza test_setresgid_exception(self):
        # Don't do this test ikiwa someone ni silly enough to run us kama root.
        current_group_ids = posix.getresgid()
        ikiwa 0 haiko kwenye current_group_ids:
            new_group_ids = (current_group_ids[0]+1, -1, -1)
            self.assertRaises(OSError, posix.setresgid, *new_group_ids)

    @unittest.skipUnless(hasattr(posix, 'initgroups'),
                         "test needs os.initgroups()")
    eleza test_initgroups(self):
        # It takes a string na an integer; check that it raises a TypeError
        # kila other argument lists.
        self.assertRaises(TypeError, posix.initgroups)
        self.assertRaises(TypeError, posix.initgroups, Tupu)
        self.assertRaises(TypeError, posix.initgroups, 3, "foo")
        self.assertRaises(TypeError, posix.initgroups, "foo", 3, object())

        # If a non-privileged user invokes it, it should fail ukijumuisha OSError
        # EPERM.
        ikiwa os.getuid() != 0:
            jaribu:
                name = pwd.getpwuid(posix.getuid()).pw_name
            tatizo KeyError:
                # the current UID may sio have a pwd entry
                ashiria unittest.SkipTest("need a pwd entry")
            jaribu:
                posix.initgroups(name, 13)
            tatizo OSError kama e:
                self.assertEqual(e.errno, errno.EPERM)
            isipokua:
                self.fail("Expected OSError to be raised by initgroups")

    @unittest.skipUnless(hasattr(posix, 'statvfs'),
                         'test needs posix.statvfs()')
    eleza test_statvfs(self):
        self.assertKweli(posix.statvfs(os.curdir))

    @unittest.skipUnless(hasattr(posix, 'fstatvfs'),
                         'test needs posix.fstatvfs()')
    eleza test_fstatvfs(self):
        fp = open(support.TESTFN)
        jaribu:
            self.assertKweli(posix.fstatvfs(fp.fileno()))
            self.assertKweli(posix.statvfs(fp.fileno()))
        mwishowe:
            fp.close()

    @unittest.skipUnless(hasattr(posix, 'ftruncate'),
                         'test needs posix.ftruncate()')
    eleza test_ftruncate(self):
        fp = open(support.TESTFN, 'w+')
        jaribu:
            # we need to have some data to truncate
            fp.write('test')
            fp.flush()
            posix.ftruncate(fp.fileno(), 0)
        mwishowe:
            fp.close()

    @unittest.skipUnless(hasattr(posix, 'truncate'), "test needs posix.truncate()")
    eleza test_truncate(self):
        ukijumuisha open(support.TESTFN, 'w') kama fp:
            fp.write('test')
            fp.flush()
        posix.truncate(support.TESTFN, 0)

    @unittest.skipUnless(getattr(os, 'execve', Tupu) kwenye os.supports_fd, "test needs execve() to support the fd parameter")
    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    @unittest.skipUnless(hasattr(os, 'waitpid'), "test needs os.waitpid()")
    eleza test_fexecve(self):
        fp = os.open(sys.executable, os.O_RDONLY)
        jaribu:
            pid = os.fork()
            ikiwa pid == 0:
                os.chdir(os.path.split(sys.executable)[0])
                posix.execve(fp, [sys.executable, '-c', 'pita'], os.environ)
            isipokua:
                self.assertEqual(os.waitpid(pid, 0), (pid, 0))
        mwishowe:
            os.close(fp)


    @unittest.skipUnless(hasattr(posix, 'waitid'), "test needs posix.waitid()")
    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    eleza test_waitid(self):
        pid = os.fork()
        ikiwa pid == 0:
            os.chdir(os.path.split(sys.executable)[0])
            posix.execve(sys.executable, [sys.executable, '-c', 'pita'], os.environ)
        isipokua:
            res = posix.waitid(posix.P_PID, pid, posix.WEXITED)
            self.assertEqual(pid, res.si_pid)

    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    eleza test_register_at_fork(self):
        ukijumuisha self.assertRaises(TypeError, msg="Positional args sio allowed"):
            os.register_at_fork(lambda: Tupu)
        ukijumuisha self.assertRaises(TypeError, msg="Args must be callable"):
            os.register_at_fork(before=2)
        ukijumuisha self.assertRaises(TypeError, msg="Args must be callable"):
            os.register_at_fork(after_in_child="three")
        ukijumuisha self.assertRaises(TypeError, msg="Args must be callable"):
            os.register_at_fork(after_in_parent=b"Five")
        ukijumuisha self.assertRaises(TypeError, msg="Args must sio be Tupu"):
            os.register_at_fork(before=Tupu)
        ukijumuisha self.assertRaises(TypeError, msg="Args must sio be Tupu"):
            os.register_at_fork(after_in_child=Tupu)
        ukijumuisha self.assertRaises(TypeError, msg="Args must sio be Tupu"):
            os.register_at_fork(after_in_parent=Tupu)
        ukijumuisha self.assertRaises(TypeError, msg="Invalid arg was allowed"):
            # Ensure a combination of valid na invalid ni an error.
            os.register_at_fork(before=Tupu, after_in_parent=lambda: 3)
        ukijumuisha self.assertRaises(TypeError, msg="Invalid arg was allowed"):
            # Ensure a combination of valid na invalid ni an error.
            os.register_at_fork(before=lambda: Tupu, after_in_child='')
        # We test actual registrations kwenye their own process so kama sio to
        # pollute this one.  There ni no way to unregister kila cleanup.
        code = """ikiwa 1:
            agiza os

            r, w = os.pipe()
            fin_r, fin_w = os.pipe()

            os.register_at_fork(before=lambda: os.write(w, b'A'))
            os.register_at_fork(after_in_parent=lambda: os.write(w, b'C'))
            os.register_at_fork(after_in_child=lambda: os.write(w, b'E'))
            os.register_at_fork(before=lambda: os.write(w, b'B'),
                                after_in_parent=lambda: os.write(w, b'D'),
                                after_in_child=lambda: os.write(w, b'F'))

            pid = os.fork()
            ikiwa pid == 0:
                # At this point, after-forkers have already been executed
                os.close(w)
                # Wait kila parent to tell us to exit
                os.read(fin_r, 1)
                os._exit(0)
            isipokua:
                jaribu:
                    os.close(w)
                    ukijumuisha open(r, "rb") kama f:
                        data = f.read()
                        assert len(data) == 6, data
                        # Check before-fork callbacks
                        assert data[:2] == b'BA', data
                        # Check after-fork callbacks
                        assert sorted(data[2:]) == list(b'CDEF'), data
                        assert data.index(b'C') < data.index(b'D'), data
                        assert data.index(b'E') < data.index(b'F'), data
                mwishowe:
                    os.write(fin_w, b'!')
            """
        assert_python_ok('-c', code)

    @unittest.skipUnless(hasattr(posix, 'lockf'), "test needs posix.lockf()")
    eleza test_lockf(self):
        fd = os.open(support.TESTFN, os.O_WRONLY | os.O_CREAT)
        jaribu:
            os.write(fd, b'test')
            os.lseek(fd, 0, os.SEEK_SET)
            posix.lockf(fd, posix.F_LOCK, 4)
            # section ni locked
            posix.lockf(fd, posix.F_ULOCK, 4)
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'pread'), "test needs posix.pread()")
    eleza test_pread(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            os.write(fd, b'test')
            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(b'es', posix.pread(fd, 2, 1))
            # the first pread() shouldn't disturb the file offset
            self.assertEqual(b'te', posix.read(fd, 2))
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'preadv'), "test needs posix.preadv()")
    eleza test_preadv(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            os.write(fd, b'test1tt2t3t5t6t6t8')
            buf = [bytearray(i) kila i kwenye [5, 3, 2]]
            self.assertEqual(posix.preadv(fd, buf, 3), 10)
            self.assertEqual([b't1tt2', b't3t', b'5t'], list(buf))
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'preadv'), "test needs posix.preadv()")
    @unittest.skipUnless(hasattr(posix, 'RWF_HIPRI'), "test needs posix.RWF_HIPRI")
    eleza test_preadv_flags(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            os.write(fd, b'test1tt2t3t5t6t6t8')
            buf = [bytearray(i) kila i kwenye [5, 3, 2]]
            self.assertEqual(posix.preadv(fd, buf, 3, os.RWF_HIPRI), 10)
            self.assertEqual([b't1tt2', b't3t', b'5t'], list(buf))
        tatizo NotImplementedError:
            self.skipTest("preadv2 sio available")
        tatizo OSError kama inst:
            # Is possible that the macro RWF_HIPRI was defined at compilation time
            # but the option ni sio supported by the kernel ama the runtime libc shared
            # library.
            ikiwa inst.errno kwenye {errno.EINVAL, errno.ENOTSUP}:
                ashiria unittest.SkipTest("RWF_HIPRI ni sio supported by the current system")
            isipokua:
                raise
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'preadv'), "test needs posix.preadv()")
    @requires_32b
    eleza test_preadv_overflow_32bits(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            buf = [bytearray(2**16)] * 2**15
            ukijumuisha self.assertRaises(OSError) kama cm:
                os.preadv(fd, buf, 0)
            self.assertEqual(cm.exception.errno, errno.EINVAL)
            self.assertEqual(bytes(buf[0]), b'\0'* 2**16)
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'pwrite'), "test needs posix.pwrite()")
    eleza test_pwrite(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            os.write(fd, b'test')
            os.lseek(fd, 0, os.SEEK_SET)
            posix.pwrite(fd, b'xx', 1)
            self.assertEqual(b'txxt', posix.read(fd, 4))
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'pwritev'), "test needs posix.pwritev()")
    eleza test_pwritev(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            os.write(fd, b"xx")
            os.lseek(fd, 0, os.SEEK_SET)
            n = os.pwritev(fd, [b'test1', b'tt2', b't3'], 2)
            self.assertEqual(n, 10)

            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(b'xxtest1tt2t3', posix.read(fd, 100))
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'pwritev'), "test needs posix.pwritev()")
    @unittest.skipUnless(hasattr(posix, 'os.RWF_SYNC'), "test needs os.RWF_SYNC")
    eleza test_pwritev_flags(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            os.write(fd,b"xx")
            os.lseek(fd, 0, os.SEEK_SET)
            n = os.pwritev(fd, [b'test1', b'tt2', b't3'], 2, os.RWF_SYNC)
            self.assertEqual(n, 10)

            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(b'xxtest1tt2', posix.read(fd, 100))
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'pwritev'), "test needs posix.pwritev()")
    @requires_32b
    eleza test_pwritev_overflow_32bits(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            ukijumuisha self.assertRaises(OSError) kama cm:
                os.pwritev(fd, [b"x" * 2**16] * 2**15, 0)
            self.assertEqual(cm.exception.errno, errno.EINVAL)
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'posix_fallocate'),
        "test needs posix.posix_fallocate()")
    eleza test_posix_fallocate(self):
        fd = os.open(support.TESTFN, os.O_WRONLY | os.O_CREAT)
        jaribu:
            posix.posix_fallocate(fd, 0, 10)
        tatizo OSError kama inst:
            # issue10812, ZFS doesn't appear to support posix_fallocate,
            # so skip Solaris-based since they are likely to have ZFS.
            # issue33655: Also ignore EINVAL on *BSD since ZFS ni also
            # often used there.
            ikiwa inst.errno == errno.EINVAL na sys.platform.startswith(
                ('sunos', 'freebsd', 'netbsd', 'openbsd', 'gnukfreebsd')):
                ashiria unittest.SkipTest("test may fail on ZFS filesystems")
            isipokua:
                raise
        mwishowe:
            os.close(fd)

    # issue31106 - posix_fallocate() does sio set error kwenye errno.
    @unittest.skipUnless(hasattr(posix, 'posix_fallocate'),
        "test needs posix.posix_fallocate()")
    eleza test_posix_fallocate_errno(self):
        jaribu:
            posix.posix_fallocate(-42, 0, 10)
        tatizo OSError kama inst:
            ikiwa inst.errno != errno.EBADF:
                raise

    @unittest.skipUnless(hasattr(posix, 'posix_fadvise'),
        "test needs posix.posix_fadvise()")
    eleza test_posix_fadvise(self):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        jaribu:
            posix.posix_fadvise(fd, 0, 0, posix.POSIX_FADV_WILLNEED)
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'posix_fadvise'),
        "test needs posix.posix_fadvise()")
    eleza test_posix_fadvise_errno(self):
        jaribu:
            posix.posix_fadvise(-42, 0, 0, posix.POSIX_FADV_WILLNEED)
        tatizo OSError kama inst:
            ikiwa inst.errno != errno.EBADF:
                raise

    @unittest.skipUnless(os.utime kwenye os.supports_fd, "test needs fd support kwenye os.utime")
    eleza test_utime_with_fd(self):
        now = time.time()
        fd = os.open(support.TESTFN, os.O_RDONLY)
        jaribu:
            posix.utime(fd)
            posix.utime(fd, Tupu)
            self.assertRaises(TypeError, posix.utime, fd, (Tupu, Tupu))
            self.assertRaises(TypeError, posix.utime, fd, (now, Tupu))
            self.assertRaises(TypeError, posix.utime, fd, (Tupu, now))
            posix.utime(fd, (int(now), int(now)))
            posix.utime(fd, (now, now))
            self.assertRaises(ValueError, posix.utime, fd, (now, now), ns=(now, now))
            self.assertRaises(ValueError, posix.utime, fd, (now, 0), ns=(Tupu, Tupu))
            self.assertRaises(ValueError, posix.utime, fd, (Tupu, Tupu), ns=(now, 0))
            posix.utime(fd, (int(now), int((now - int(now)) * 1e9)))
            posix.utime(fd, ns=(int(now), int((now - int(now)) * 1e9)))

        mwishowe:
            os.close(fd)

    @unittest.skipUnless(os.utime kwenye os.supports_follow_symlinks, "test needs follow_symlinks support kwenye os.utime")
    eleza test_utime_nofollow_symlinks(self):
        now = time.time()
        posix.utime(support.TESTFN, Tupu, follow_symlinks=Uongo)
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (Tupu, Tupu), follow_symlinks=Uongo)
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (now, Tupu), follow_symlinks=Uongo)
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (Tupu, now), follow_symlinks=Uongo)
        posix.utime(support.TESTFN, (int(now), int(now)), follow_symlinks=Uongo)
        posix.utime(support.TESTFN, (now, now), follow_symlinks=Uongo)
        posix.utime(support.TESTFN, follow_symlinks=Uongo)

    @unittest.skipUnless(hasattr(posix, 'writev'), "test needs posix.writev()")
    eleza test_writev(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            n = os.writev(fd, (b'test1', b'tt2', b't3'))
            self.assertEqual(n, 10)

            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(b'test1tt2t3', posix.read(fd, 10))

            # Issue #20113: empty list of buffers should sio crash
            jaribu:
                size = posix.writev(fd, [])
            tatizo OSError:
                # writev(fd, []) raises OSError(22, "Invalid argument")
                # on OpenIndiana
                pita
            isipokua:
                self.assertEqual(size, 0)
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'writev'), "test needs posix.writev()")
    @requires_32b
    eleza test_writev_overflow_32bits(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            ukijumuisha self.assertRaises(OSError) kama cm:
                os.writev(fd, [b"x" * 2**16] * 2**15)
            self.assertEqual(cm.exception.errno, errno.EINVAL)
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'readv'), "test needs posix.readv()")
    eleza test_readv(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            os.write(fd, b'test1tt2t3')
            os.lseek(fd, 0, os.SEEK_SET)
            buf = [bytearray(i) kila i kwenye [5, 3, 2]]
            self.assertEqual(posix.readv(fd, buf), 10)
            self.assertEqual([b'test1', b'tt2', b't3'], [bytes(i) kila i kwenye buf])

            # Issue #20113: empty list of buffers should sio crash
            jaribu:
                size = posix.readv(fd, [])
            tatizo OSError:
                # readv(fd, []) raises OSError(22, "Invalid argument")
                # on OpenIndiana
                pita
            isipokua:
                self.assertEqual(size, 0)
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'readv'), "test needs posix.readv()")
    @requires_32b
    eleza test_readv_overflow_32bits(self):
        fd = os.open(support.TESTFN, os.O_RDWR | os.O_CREAT)
        jaribu:
            buf = [bytearray(2**16)] * 2**15
            ukijumuisha self.assertRaises(OSError) kama cm:
                os.readv(fd, buf)
            self.assertEqual(cm.exception.errno, errno.EINVAL)
            self.assertEqual(bytes(buf[0]), b'\0'* 2**16)
        mwishowe:
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'dup'),
                         'test needs posix.dup()')
    eleza test_dup(self):
        fp = open(support.TESTFN)
        jaribu:
            fd = posix.dup(fp.fileno())
            self.assertIsInstance(fd, int)
            os.close(fd)
        mwishowe:
            fp.close()

    @unittest.skipUnless(hasattr(posix, 'confstr'),
                         'test needs posix.confstr()')
    eleza test_confstr(self):
        self.assertRaises(ValueError, posix.confstr, "CS_garbage")
        self.assertEqual(len(posix.confstr("CS_PATH")) > 0, Kweli)

    @unittest.skipUnless(hasattr(posix, 'dup2'),
                         'test needs posix.dup2()')
    eleza test_dup2(self):
        fp1 = open(support.TESTFN)
        fp2 = open(support.TESTFN)
        jaribu:
            posix.dup2(fp1.fileno(), fp2.fileno())
        mwishowe:
            fp1.close()
            fp2.close()

    @unittest.skipUnless(hasattr(os, 'O_CLOEXEC'), "needs os.O_CLOEXEC")
    @support.requires_linux_version(2, 6, 23)
    eleza test_oscloexec(self):
        fd = os.open(support.TESTFN, os.O_RDONLY|os.O_CLOEXEC)
        self.addCleanup(os.close, fd)
        self.assertUongo(os.get_inheritable(fd))

    @unittest.skipUnless(hasattr(posix, 'O_EXLOCK'),
                         'test needs posix.O_EXLOCK')
    eleza test_osexlock(self):
        fd = os.open(support.TESTFN,
                     os.O_WRONLY|os.O_EXLOCK|os.O_CREAT)
        self.assertRaises(OSError, os.open, support.TESTFN,
                          os.O_WRONLY|os.O_EXLOCK|os.O_NONBLOCK)
        os.close(fd)

        ikiwa hasattr(posix, "O_SHLOCK"):
            fd = os.open(support.TESTFN,
                         os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
            self.assertRaises(OSError, os.open, support.TESTFN,
                              os.O_WRONLY|os.O_EXLOCK|os.O_NONBLOCK)
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'O_SHLOCK'),
                         'test needs posix.O_SHLOCK')
    eleza test_osshlock(self):
        fd1 = os.open(support.TESTFN,
                     os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
        fd2 = os.open(support.TESTFN,
                      os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
        os.close(fd2)
        os.close(fd1)

        ikiwa hasattr(posix, "O_EXLOCK"):
            fd = os.open(support.TESTFN,
                         os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
            self.assertRaises(OSError, os.open, support.TESTFN,
                              os.O_RDONLY|os.O_EXLOCK|os.O_NONBLOCK)
            os.close(fd)

    @unittest.skipUnless(hasattr(posix, 'fstat'),
                         'test needs posix.fstat()')
    eleza test_fstat(self):
        fp = open(support.TESTFN)
        jaribu:
            self.assertKweli(posix.fstat(fp.fileno()))
            self.assertKweli(posix.stat(fp.fileno()))

            self.assertRaisesRegex(TypeError,
                    'should be string, bytes, os.PathLike ama integer, not',
                    posix.stat, float(fp.fileno()))
        mwishowe:
            fp.close()

    eleza test_stat(self):
        self.assertKweli(posix.stat(support.TESTFN))
        self.assertKweli(posix.stat(os.fsencode(support.TESTFN)))

        self.assertWarnsRegex(DeprecationWarning,
                'should be string, bytes, os.PathLike ama integer, not',
                posix.stat, bytearray(os.fsencode(support.TESTFN)))
        self.assertRaisesRegex(TypeError,
                'should be string, bytes, os.PathLike ama integer, not',
                posix.stat, Tupu)
        self.assertRaisesRegex(TypeError,
                'should be string, bytes, os.PathLike ama integer, not',
                posix.stat, list(support.TESTFN))
        self.assertRaisesRegex(TypeError,
                'should be string, bytes, os.PathLike ama integer, not',
                posix.stat, list(os.fsencode(support.TESTFN)))

    @unittest.skipUnless(hasattr(posix, 'mkfifo'), "don't have mkfifo()")
    eleza test_mkfifo(self):
        support.unlink(support.TESTFN)
        jaribu:
            posix.mkfifo(support.TESTFN, stat.S_IRUSR | stat.S_IWUSR)
        tatizo PermissionError kama e:
            self.skipTest('posix.mkfifo(): %s' % e)
        self.assertKweli(stat.S_ISFIFO(posix.stat(support.TESTFN).st_mode))

    @unittest.skipUnless(hasattr(posix, 'mknod') na hasattr(stat, 'S_IFIFO'),
                         "don't have mknod()/S_IFIFO")
    eleza test_mknod(self):
        # Test using mknod() to create a FIFO (the only use specified
        # by POSIX).
        support.unlink(support.TESTFN)
        mode = stat.S_IFIFO | stat.S_IRUSR | stat.S_IWUSR
        jaribu:
            posix.mknod(support.TESTFN, mode, 0)
        tatizo OSError kama e:
            # Some old systems don't allow unprivileged users to use
            # mknod(), ama only support creating device nodes.
            self.assertIn(e.errno, (errno.EPERM, errno.EINVAL, errno.EACCES))
        isipokua:
            self.assertKweli(stat.S_ISFIFO(posix.stat(support.TESTFN).st_mode))

        # Keyword arguments are also supported
        support.unlink(support.TESTFN)
        jaribu:
            posix.mknod(path=support.TESTFN, mode=mode, device=0,
                dir_fd=Tupu)
        tatizo OSError kama e:
            self.assertIn(e.errno, (errno.EPERM, errno.EINVAL, errno.EACCES))

    @unittest.skipUnless(hasattr(posix, 'makedev'), 'test needs posix.makedev()')
    eleza test_makedev(self):
        st = posix.stat(support.TESTFN)
        dev = st.st_dev
        self.assertIsInstance(dev, int)
        self.assertGreaterEqual(dev, 0)

        major = posix.major(dev)
        self.assertIsInstance(major, int)
        self.assertGreaterEqual(major, 0)
        self.assertEqual(posix.major(dev), major)
        self.assertRaises(TypeError, posix.major, float(dev))
        self.assertRaises(TypeError, posix.major)
        self.assertRaises((ValueError, OverflowError), posix.major, -1)

        minor = posix.minor(dev)
        self.assertIsInstance(minor, int)
        self.assertGreaterEqual(minor, 0)
        self.assertEqual(posix.minor(dev), minor)
        self.assertRaises(TypeError, posix.minor, float(dev))
        self.assertRaises(TypeError, posix.minor)
        self.assertRaises((ValueError, OverflowError), posix.minor, -1)

        self.assertEqual(posix.makedev(major, minor), dev)
        self.assertRaises(TypeError, posix.makedev, float(major), minor)
        self.assertRaises(TypeError, posix.makedev, major, float(minor))
        self.assertRaises(TypeError, posix.makedev, major)
        self.assertRaises(TypeError, posix.makedev)

    eleza _test_all_chown_common(self, chown_func, first_param, stat_func):
        """Common code kila chown, fchown na lchown tests."""
        eleza check_stat(uid, gid):
            ikiwa stat_func ni sio Tupu:
                stat = stat_func(first_param)
                self.assertEqual(stat.st_uid, uid)
                self.assertEqual(stat.st_gid, gid)
        uid = os.getuid()
        gid = os.getgid()
        # test a successful chown call
        chown_func(first_param, uid, gid)
        check_stat(uid, gid)
        chown_func(first_param, -1, gid)
        check_stat(uid, gid)
        chown_func(first_param, uid, -1)
        check_stat(uid, gid)

        ikiwa uid == 0:
            # Try an amusingly large uid/gid to make sure we handle
            # large unsigned values.  (chown lets you use any
            # uid/gid you like, even ikiwa they aren't defined.)
            #
            # This problem keeps coming up:
            #   http://bugs.python.org/issue1747858
            #   http://bugs.python.org/issue4591
            #   http://bugs.python.org/issue15301
            # Hopefully the fix kwenye 4591 fixes it kila good!
            #
            # This part of the test only runs when run kama root.
            # Only scary people run their tests kama root.

            big_value = 2**31
            chown_func(first_param, big_value, big_value)
            check_stat(big_value, big_value)
            chown_func(first_param, -1, -1)
            check_stat(big_value, big_value)
            chown_func(first_param, uid, gid)
            check_stat(uid, gid)
        lasivyo platform.system() kwenye ('HP-UX', 'SunOS'):
            # HP-UX na Solaris can allow a non-root user to chown() to root
            # (issue #5113)
            ashiria unittest.SkipTest("Skipping because of non-standard chown() "
                                    "behavior")
        isipokua:
            # non-root cansio chown to root, raises OSError
            self.assertRaises(OSError, chown_func, first_param, 0, 0)
            check_stat(uid, gid)
            self.assertRaises(OSError, chown_func, first_param, 0, -1)
            check_stat(uid, gid)
            ikiwa 0 haiko kwenye os.getgroups():
                self.assertRaises(OSError, chown_func, first_param, -1, 0)
                check_stat(uid, gid)
        # test illegal types
        kila t kwenye str, float:
            self.assertRaises(TypeError, chown_func, first_param, t(uid), gid)
            check_stat(uid, gid)
            self.assertRaises(TypeError, chown_func, first_param, uid, t(gid))
            check_stat(uid, gid)

    @unittest.skipUnless(hasattr(posix, 'chown'), "test needs os.chown()")
    eleza test_chown(self):
        # ashiria an OSError ikiwa the file does sio exist
        os.unlink(support.TESTFN)
        self.assertRaises(OSError, posix.chown, support.TESTFN, -1, -1)

        # re-create the file
        support.create_empty_file(support.TESTFN)
        self._test_all_chown_common(posix.chown, support.TESTFN, posix.stat)

    @unittest.skipUnless(hasattr(posix, 'fchown'), "test needs os.fchown()")
    eleza test_fchown(self):
        os.unlink(support.TESTFN)

        # re-create the file
        test_file = open(support.TESTFN, 'w')
        jaribu:
            fd = test_file.fileno()
            self._test_all_chown_common(posix.fchown, fd,
                                        getattr(posix, 'fstat', Tupu))
        mwishowe:
            test_file.close()

    @unittest.skipUnless(hasattr(posix, 'lchown'), "test needs os.lchown()")
    eleza test_lchown(self):
        os.unlink(support.TESTFN)
        # create a symlink
        os.symlink(_DUMMY_SYMLINK, support.TESTFN)
        self._test_all_chown_common(posix.lchown, support.TESTFN,
                                    getattr(posix, 'lstat', Tupu))

    @unittest.skipUnless(hasattr(posix, 'chdir'), 'test needs posix.chdir()')
    eleza test_chdir(self):
        posix.chdir(os.curdir)
        self.assertRaises(OSError, posix.chdir, support.TESTFN)

    eleza test_listdir(self):
        self.assertIn(support.TESTFN, posix.listdir(os.curdir))

    eleza test_listdir_default(self):
        # When listdir ni called without argument,
        # it's the same kama listdir(os.curdir).
        self.assertIn(support.TESTFN, posix.listdir())

    eleza test_listdir_bytes(self):
        # When listdir ni called ukijumuisha a bytes object,
        # the returned strings are of type bytes.
        self.assertIn(os.fsencode(support.TESTFN), posix.listdir(b'.'))

    eleza test_listdir_bytes_like(self):
        kila cls kwenye bytearray, memoryview:
            ukijumuisha self.assertWarns(DeprecationWarning):
                names = posix.listdir(cls(b'.'))
            self.assertIn(os.fsencode(support.TESTFN), names)
            kila name kwenye names:
                self.assertIs(type(name), bytes)

    @unittest.skipUnless(posix.listdir kwenye os.supports_fd,
                         "test needs fd support kila posix.listdir()")
    eleza test_listdir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        self.addCleanup(posix.close, f)
        self.assertEqual(
            sorted(posix.listdir('.')),
            sorted(posix.listdir(f))
            )
        # Check that the fd offset was reset (issue #13739)
        self.assertEqual(
            sorted(posix.listdir('.')),
            sorted(posix.listdir(f))
            )

    @unittest.skipUnless(hasattr(posix, 'access'), 'test needs posix.access()')
    eleza test_access(self):
        self.assertKweli(posix.access(support.TESTFN, os.R_OK))

    @unittest.skipUnless(hasattr(posix, 'umask'), 'test needs posix.umask()')
    eleza test_umask(self):
        old_mask = posix.umask(0)
        self.assertIsInstance(old_mask, int)
        posix.umask(old_mask)

    @unittest.skipUnless(hasattr(posix, 'strerror'),
                         'test needs posix.strerror()')
    eleza test_strerror(self):
        self.assertKweli(posix.strerror(0))

    @unittest.skipUnless(hasattr(posix, 'pipe'), 'test needs posix.pipe()')
    eleza test_pipe(self):
        reader, writer = posix.pipe()
        os.close(reader)
        os.close(writer)

    @unittest.skipUnless(hasattr(os, 'pipe2'), "test needs os.pipe2()")
    @support.requires_linux_version(2, 6, 27)
    eleza test_pipe2(self):
        self.assertRaises(TypeError, os.pipe2, 'DEADBEEF')
        self.assertRaises(TypeError, os.pipe2, 0, 0)

        # try calling ukijumuisha flags = 0, like os.pipe()
        r, w = os.pipe2(0)
        os.close(r)
        os.close(w)

        # test flags
        r, w = os.pipe2(os.O_CLOEXEC|os.O_NONBLOCK)
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        self.assertUongo(os.get_inheritable(r))
        self.assertUongo(os.get_inheritable(w))
        self.assertUongo(os.get_blocking(r))
        self.assertUongo(os.get_blocking(w))
        # try reading kutoka an empty pipe: this should fail, sio block
        self.assertRaises(OSError, os.read, r, 1)
        # try a write big enough to fill-up the pipe: this should either
        # fail ama perform a partial write, sio block
        jaribu:
            os.write(w, b'x' * support.PIPE_MAX_SIZE)
        tatizo OSError:
            pita

    @support.cpython_only
    @unittest.skipUnless(hasattr(os, 'pipe2'), "test needs os.pipe2()")
    @support.requires_linux_version(2, 6, 27)
    eleza test_pipe2_c_limits(self):
        # Issue 15989
        agiza _testcapi
        self.assertRaises(OverflowError, os.pipe2, _testcapi.INT_MAX + 1)
        self.assertRaises(OverflowError, os.pipe2, _testcapi.UINT_MAX + 1)

    @unittest.skipUnless(hasattr(posix, 'utime'), 'test needs posix.utime()')
    eleza test_utime(self):
        now = time.time()
        posix.utime(support.TESTFN, Tupu)
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (Tupu, Tupu))
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (now, Tupu))
        self.assertRaises(TypeError, posix.utime, support.TESTFN, (Tupu, now))
        posix.utime(support.TESTFN, (int(now), int(now)))
        posix.utime(support.TESTFN, (now, now))

    eleza _test_chflags_regular_file(self, chflags_func, target_file, **kwargs):
        st = os.stat(target_file)
        self.assertKweli(hasattr(st, 'st_flags'))

        # ZFS returns EOPNOTSUPP when attempting to set flag UF_IMMUTABLE.
        flags = st.st_flags | stat.UF_IMMUTABLE
        jaribu:
            chflags_func(target_file, flags, **kwargs)
        tatizo OSError kama err:
            ikiwa err.errno != errno.EOPNOTSUPP:
                raise
            msg = 'chflag UF_IMMUTABLE sio supported by underlying fs'
            self.skipTest(msg)

        jaribu:
            new_st = os.stat(target_file)
            self.assertEqual(st.st_flags | stat.UF_IMMUTABLE, new_st.st_flags)
            jaribu:
                fd = open(target_file, 'w+')
            tatizo OSError kama e:
                self.assertEqual(e.errno, errno.EPERM)
        mwishowe:
            posix.chflags(target_file, st.st_flags)

    @unittest.skipUnless(hasattr(posix, 'chflags'), 'test needs os.chflags()')
    eleza test_chflags(self):
        self._test_chflags_regular_file(posix.chflags, support.TESTFN)

    @unittest.skipUnless(hasattr(posix, 'lchflags'), 'test needs os.lchflags()')
    eleza test_lchflags_regular_file(self):
        self._test_chflags_regular_file(posix.lchflags, support.TESTFN)
        self._test_chflags_regular_file(posix.chflags, support.TESTFN, follow_symlinks=Uongo)

    @unittest.skipUnless(hasattr(posix, 'lchflags'), 'test needs os.lchflags()')
    eleza test_lchflags_symlink(self):
        testfn_st = os.stat(support.TESTFN)

        self.assertKweli(hasattr(testfn_st, 'st_flags'))

        os.symlink(support.TESTFN, _DUMMY_SYMLINK)
        self.teardown_files.append(_DUMMY_SYMLINK)
        dummy_symlink_st = os.lstat(_DUMMY_SYMLINK)

        eleza chflags_nofollow(path, flags):
            rudisha posix.chflags(path, flags, follow_symlinks=Uongo)

        kila fn kwenye (posix.lchflags, chflags_nofollow):
            # ZFS returns EOPNOTSUPP when attempting to set flag UF_IMMUTABLE.
            flags = dummy_symlink_st.st_flags | stat.UF_IMMUTABLE
            jaribu:
                fn(_DUMMY_SYMLINK, flags)
            tatizo OSError kama err:
                ikiwa err.errno != errno.EOPNOTSUPP:
                    raise
                msg = 'chflag UF_IMMUTABLE sio supported by underlying fs'
                self.skipTest(msg)
            jaribu:
                new_testfn_st = os.stat(support.TESTFN)
                new_dummy_symlink_st = os.lstat(_DUMMY_SYMLINK)

                self.assertEqual(testfn_st.st_flags, new_testfn_st.st_flags)
                self.assertEqual(dummy_symlink_st.st_flags | stat.UF_IMMUTABLE,
                                 new_dummy_symlink_st.st_flags)
            mwishowe:
                fn(_DUMMY_SYMLINK, dummy_symlink_st.st_flags)

    eleza test_environ(self):
        ikiwa os.name == "nt":
            item_type = str
        isipokua:
            item_type = bytes
        kila k, v kwenye posix.environ.items():
            self.assertEqual(type(k), item_type)
            self.assertEqual(type(v), item_type)

    @unittest.skipUnless(hasattr(os, "putenv"), "requires os.putenv()")
    eleza test_putenv(self):
        ukijumuisha self.assertRaises(ValueError):
            os.putenv('FRUIT\0VEGETABLE', 'cabbage')
        ukijumuisha self.assertRaises(ValueError):
            os.putenv(b'FRUIT\0VEGETABLE', b'cabbage')
        ukijumuisha self.assertRaises(ValueError):
            os.putenv('FRUIT', 'orange\0VEGETABLE=cabbage')
        ukijumuisha self.assertRaises(ValueError):
            os.putenv(b'FRUIT', b'orange\0VEGETABLE=cabbage')
        ukijumuisha self.assertRaises(ValueError):
            os.putenv('FRUIT=ORANGE', 'lemon')
        ukijumuisha self.assertRaises(ValueError):
            os.putenv(b'FRUIT=ORANGE', b'lemon')

    @unittest.skipUnless(hasattr(posix, 'getcwd'), 'test needs posix.getcwd()')
    eleza test_getcwd_long_pathnames(self):
        dirname = 'getcwd-test-directory-0123456789abcdef-01234567890abcdef'
        curdir = os.getcwd()
        base_path = os.path.abspath(support.TESTFN) + '.getcwd'

        jaribu:
            os.mkdir(base_path)
            os.chdir(base_path)
        tatizo:
            #  Just returning nothing instead of the SkipTest exception, because
            #  the test results kwenye Error kwenye that case.  Is that ok?
            #  ashiria unittest.SkipTest("cansio create directory kila testing")
            rudisha

            eleza _create_and_do_getcwd(dirname, current_path_length = 0):
                jaribu:
                    os.mkdir(dirname)
                tatizo:
                    ashiria unittest.SkipTest("mkdir cansio create directory sufficiently deep kila getcwd test")

                os.chdir(dirname)
                jaribu:
                    os.getcwd()
                    ikiwa current_path_length < 1027:
                        _create_and_do_getcwd(dirname, current_path_length + len(dirname) + 1)
                mwishowe:
                    os.chdir('..')
                    os.rmdir(dirname)

            _create_and_do_getcwd(dirname)

        mwishowe:
            os.chdir(curdir)
            support.rmtree(base_path)

    @unittest.skipUnless(hasattr(posix, 'getgrouplist'), "test needs posix.getgrouplist()")
    @unittest.skipUnless(hasattr(pwd, 'getpwuid'), "test needs pwd.getpwuid()")
    @unittest.skipUnless(hasattr(os, 'getuid'), "test needs os.getuid()")
    eleza test_getgrouplist(self):
        user = pwd.getpwuid(os.getuid())[0]
        group = pwd.getpwuid(os.getuid())[3]
        self.assertIn(group, posix.getgrouplist(user, group))


    @unittest.skipUnless(hasattr(os, 'getegid'), "test needs os.getegid()")
    eleza test_getgroups(self):
        ukijumuisha os.popen('id -G 2>/dev/null') kama idg:
            groups = idg.read().strip()
            ret = idg.close()

        jaribu:
            idg_groups = set(int(g) kila g kwenye groups.split())
        tatizo ValueError:
            idg_groups = set()
        ikiwa ret ni sio Tupu ama sio idg_groups:
            ashiria unittest.SkipTest("need working 'id -G'")

        # Issues 16698: OS X ABIs prior to 10.6 have limits on getgroups()
        ikiwa sys.platform == 'darwin':
            agiza sysconfig
            dt = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET') ama '10.0'
            ikiwa tuple(int(n) kila n kwenye dt.split('.')[0:2]) < (10, 6):
                ashiria unittest.SkipTest("getgroups(2) ni broken prior to 10.6")

        # 'id -G' na 'os.getgroups()' should rudisha the same
        # groups, ignoring order, duplicates, na the effective gid.
        # #10822/#26944 - It ni implementation defined whether
        # posix.getgroups() includes the effective gid.
        symdiff = idg_groups.symmetric_difference(posix.getgroups())
        self.assertKweli(sio symdiff ama symdiff == {posix.getegid()})

    # tests kila the posix *at functions follow

    @unittest.skipUnless(os.access kwenye os.supports_dir_fd, "test needs dir_fd support kila os.access()")
    eleza test_access_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            self.assertKweli(posix.access(support.TESTFN, os.R_OK, dir_fd=f))
        mwishowe:
            posix.close(f)

    @unittest.skipUnless(os.chmod kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.chmod()")
    eleza test_chmod_dir_fd(self):
        os.chmod(support.TESTFN, stat.S_IRUSR)

        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            posix.chmod(support.TESTFN, stat.S_IRUSR | stat.S_IWUSR, dir_fd=f)

            s = posix.stat(support.TESTFN)
            self.assertEqual(s[0] & stat.S_IRWXU, stat.S_IRUSR | stat.S_IWUSR)
        mwishowe:
            posix.close(f)

    @unittest.skipUnless(os.chown kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.chown()")
    eleza test_chown_dir_fd(self):
        support.unlink(support.TESTFN)
        support.create_empty_file(support.TESTFN)

        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            posix.chown(support.TESTFN, os.getuid(), os.getgid(), dir_fd=f)
        mwishowe:
            posix.close(f)

    @unittest.skipUnless(os.stat kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.stat()")
    eleza test_stat_dir_fd(self):
        support.unlink(support.TESTFN)
        ukijumuisha open(support.TESTFN, 'w') kama outfile:
            outfile.write("testline\n")

        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            s1 = posix.stat(support.TESTFN)
            s2 = posix.stat(support.TESTFN, dir_fd=f)
            self.assertEqual(s1, s2)
            s2 = posix.stat(support.TESTFN, dir_fd=Tupu)
            self.assertEqual(s1, s2)
            self.assertRaisesRegex(TypeError, 'should be integer ama Tupu, not',
                    posix.stat, support.TESTFN, dir_fd=posix.getcwd())
            self.assertRaisesRegex(TypeError, 'should be integer ama Tupu, not',
                    posix.stat, support.TESTFN, dir_fd=float(f))
            self.assertRaises(OverflowError,
                    posix.stat, support.TESTFN, dir_fd=10**20)
        mwishowe:
            posix.close(f)

    @unittest.skipUnless(os.utime kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.utime()")
    eleza test_utime_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            now = time.time()
            posix.utime(support.TESTFN, Tupu, dir_fd=f)
            posix.utime(support.TESTFN, dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, now, dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, (Tupu, Tupu), dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, (now, Tupu), dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, (Tupu, now), dir_fd=f)
            self.assertRaises(TypeError, posix.utime, support.TESTFN, (now, "x"), dir_fd=f)
            posix.utime(support.TESTFN, (int(now), int(now)), dir_fd=f)
            posix.utime(support.TESTFN, (now, now), dir_fd=f)
            posix.utime(support.TESTFN,
                    (int(now), int((now - int(now)) * 1e9)), dir_fd=f)
            posix.utime(support.TESTFN, dir_fd=f,
                            times=(int(now), int((now - int(now)) * 1e9)))

            # try dir_fd na follow_symlinks together
            ikiwa os.utime kwenye os.supports_follow_symlinks:
                jaribu:
                    posix.utime(support.TESTFN, follow_symlinks=Uongo, dir_fd=f)
                tatizo ValueError:
                    # whoops!  using both together sio supported on this platform.
                    pita

        mwishowe:
            posix.close(f)

    @unittest.skipUnless(os.link kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.link()")
    eleza test_link_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            posix.link(support.TESTFN, support.TESTFN + 'link', src_dir_fd=f, dst_dir_fd=f)
        tatizo PermissionError kama e:
            self.skipTest('posix.link(): %s' % e)
        isipokua:
            # should have same inodes
            self.assertEqual(posix.stat(support.TESTFN)[1],
                posix.stat(support.TESTFN + 'link')[1])
        mwishowe:
            posix.close(f)
            support.unlink(support.TESTFN + 'link')

    @unittest.skipUnless(os.mkdir kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.mkdir()")
    eleza test_mkdir_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            posix.mkdir(support.TESTFN + 'dir', dir_fd=f)
            posix.stat(support.TESTFN + 'dir') # should sio ashiria exception
        mwishowe:
            posix.close(f)
            support.rmtree(support.TESTFN + 'dir')

    @unittest.skipUnless((os.mknod kwenye os.supports_dir_fd) na hasattr(stat, 'S_IFIFO'),
                         "test requires both stat.S_IFIFO na dir_fd support kila os.mknod()")
    eleza test_mknod_dir_fd(self):
        # Test using mknodat() to create a FIFO (the only use specified
        # by POSIX).
        support.unlink(support.TESTFN)
        mode = stat.S_IFIFO | stat.S_IRUSR | stat.S_IWUSR
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            posix.mknod(support.TESTFN, mode, 0, dir_fd=f)
        tatizo OSError kama e:
            # Some old systems don't allow unprivileged users to use
            # mknod(), ama only support creating device nodes.
            self.assertIn(e.errno, (errno.EPERM, errno.EINVAL, errno.EACCES))
        isipokua:
            self.assertKweli(stat.S_ISFIFO(posix.stat(support.TESTFN).st_mode))
        mwishowe:
            posix.close(f)

    @unittest.skipUnless(os.open kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.open()")
    eleza test_open_dir_fd(self):
        support.unlink(support.TESTFN)
        ukijumuisha open(support.TESTFN, 'w') kama outfile:
            outfile.write("testline\n")
        a = posix.open(posix.getcwd(), posix.O_RDONLY)
        b = posix.open(support.TESTFN, posix.O_RDONLY, dir_fd=a)
        jaribu:
            res = posix.read(b, 9).decode(encoding="utf-8")
            self.assertEqual("testline\n", res)
        mwishowe:
            posix.close(a)
            posix.close(b)

    @unittest.skipUnless(os.readlink kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.readlink()")
    eleza test_readlink_dir_fd(self):
        os.symlink(support.TESTFN, support.TESTFN + 'link')
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            self.assertEqual(posix.readlink(support.TESTFN + 'link'),
                posix.readlink(support.TESTFN + 'link', dir_fd=f))
        mwishowe:
            support.unlink(support.TESTFN + 'link')
            posix.close(f)

    @unittest.skipUnless(os.rename kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.rename()")
    eleza test_rename_dir_fd(self):
        support.unlink(support.TESTFN)
        support.create_empty_file(support.TESTFN + 'ren')
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            posix.rename(support.TESTFN + 'ren', support.TESTFN, src_dir_fd=f, dst_dir_fd=f)
        tatizo:
            posix.rename(support.TESTFN + 'ren', support.TESTFN)
            raise
        isipokua:
            posix.stat(support.TESTFN) # should sio ashiria exception
        mwishowe:
            posix.close(f)

    @unittest.skipUnless(os.symlink kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.symlink()")
    eleza test_symlink_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            posix.symlink(support.TESTFN, support.TESTFN + 'link', dir_fd=f)
            self.assertEqual(posix.readlink(support.TESTFN + 'link'), support.TESTFN)
        mwishowe:
            posix.close(f)
            support.unlink(support.TESTFN + 'link')

    @unittest.skipUnless(os.unlink kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.unlink()")
    eleza test_unlink_dir_fd(self):
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        support.create_empty_file(support.TESTFN + 'del')
        posix.stat(support.TESTFN + 'del') # should sio ashiria exception
        jaribu:
            posix.unlink(support.TESTFN + 'del', dir_fd=f)
        tatizo:
            support.unlink(support.TESTFN + 'del')
            raise
        isipokua:
            self.assertRaises(OSError, posix.stat, support.TESTFN + 'link')
        mwishowe:
            posix.close(f)

    @unittest.skipUnless(os.mkfifo kwenye os.supports_dir_fd, "test needs dir_fd support kwenye os.mkfifo()")
    eleza test_mkfifo_dir_fd(self):
        support.unlink(support.TESTFN)
        f = posix.open(posix.getcwd(), posix.O_RDONLY)
        jaribu:
            jaribu:
                posix.mkfifo(support.TESTFN,
                             stat.S_IRUSR | stat.S_IWUSR, dir_fd=f)
            tatizo PermissionError kama e:
                self.skipTest('posix.mkfifo(): %s' % e)
            self.assertKweli(stat.S_ISFIFO(posix.stat(support.TESTFN).st_mode))
        mwishowe:
            posix.close(f)

    requires_sched_h = unittest.skipUnless(hasattr(posix, 'sched_tuma'),
                                           "don't have scheduling support")
    requires_sched_affinity = unittest.skipUnless(hasattr(posix, 'sched_setaffinity'),
                                                  "don't have sched affinity support")

    @requires_sched_h
    eleza test_sched_tuma(self):
        # This has no error conditions (at least on Linux).
        posix.sched_tuma()

    @requires_sched_h
    @unittest.skipUnless(hasattr(posix, 'sched_get_priority_max'),
                         "requires sched_get_priority_max()")
    eleza test_sched_priority(self):
        # Round-robin usually has interesting priorities.
        pol = posix.SCHED_RR
        lo = posix.sched_get_priority_min(pol)
        hi = posix.sched_get_priority_max(pol)
        self.assertIsInstance(lo, int)
        self.assertIsInstance(hi, int)
        self.assertGreaterEqual(hi, lo)
        # OSX evidently just returns 15 without checking the argument.
        ikiwa sys.platform != "darwin":
            self.assertRaises(OSError, posix.sched_get_priority_min, -23)
            self.assertRaises(OSError, posix.sched_get_priority_max, -23)

    @requires_sched
    eleza test_get_and_set_scheduler_and_param(self):
        possible_schedulers = [sched kila name, sched kwenye posix.__dict__.items()
                               ikiwa name.startswith("SCHED_")]
        mine = posix.sched_getscheduler(0)
        self.assertIn(mine, possible_schedulers)
        jaribu:
            parent = posix.sched_getscheduler(os.getppid())
        tatizo OSError kama e:
            ikiwa e.errno != errno.EPERM:
                raise
        isipokua:
            self.assertIn(parent, possible_schedulers)
        self.assertRaises(OSError, posix.sched_getscheduler, -1)
        self.assertRaises(OSError, posix.sched_getparam, -1)
        param = posix.sched_getparam(0)
        self.assertIsInstance(param.sched_priority, int)

        # POSIX states that calling sched_setparam() ama sched_setscheduler() on
        # a process ukijumuisha a scheduling policy other than SCHED_FIFO ama SCHED_RR
        # ni implementation-defined: NetBSD na FreeBSD can rudisha EINVAL.
        ikiwa sio sys.platform.startswith(('freebsd', 'netbsd')):
            jaribu:
                posix.sched_setscheduler(0, mine, param)
                posix.sched_setparam(0, param)
            tatizo OSError kama e:
                ikiwa e.errno != errno.EPERM:
                    raise
            self.assertRaises(OSError, posix.sched_setparam, -1, param)

        self.assertRaises(OSError, posix.sched_setscheduler, -1, mine, param)
        self.assertRaises(TypeError, posix.sched_setscheduler, 0, mine, Tupu)
        self.assertRaises(TypeError, posix.sched_setparam, 0, 43)
        param = posix.sched_param(Tupu)
        self.assertRaises(TypeError, posix.sched_setparam, 0, param)
        large = 214748364700
        param = posix.sched_param(large)
        self.assertRaises(OverflowError, posix.sched_setparam, 0, param)
        param = posix.sched_param(sched_priority=-large)
        self.assertRaises(OverflowError, posix.sched_setparam, 0, param)

    @unittest.skipUnless(hasattr(posix, "sched_rr_get_interval"), "no function")
    eleza test_sched_rr_get_interval(self):
        jaribu:
            interval = posix.sched_rr_get_interval(0)
        tatizo OSError kama e:
            # This likely means that sched_rr_get_interval ni only valid for
            # processes ukijumuisha the SCHED_RR scheduler kwenye effect.
            ikiwa e.errno != errno.EINVAL:
                raise
            self.skipTest("only works on SCHED_RR processes")
        self.assertIsInstance(interval, float)
        # Reasonable constraints, I think.
        self.assertGreaterEqual(interval, 0.)
        self.assertLess(interval, 1.)

    @requires_sched_affinity
    eleza test_sched_getaffinity(self):
        mask = posix.sched_getaffinity(0)
        self.assertIsInstance(mask, set)
        self.assertGreaterEqual(len(mask), 1)
        self.assertRaises(OSError, posix.sched_getaffinity, -1)
        kila cpu kwenye mask:
            self.assertIsInstance(cpu, int)
            self.assertGreaterEqual(cpu, 0)
            self.assertLess(cpu, 1 << 32)

    @requires_sched_affinity
    eleza test_sched_setaffinity(self):
        mask = posix.sched_getaffinity(0)
        ikiwa len(mask) > 1:
            # Empty masks are forbidden
            mask.pop()
        posix.sched_setaffinity(0, mask)
        self.assertEqual(posix.sched_getaffinity(0), mask)
        self.assertRaises(OSError, posix.sched_setaffinity, 0, [])
        self.assertRaises(ValueError, posix.sched_setaffinity, 0, [-10])
        self.assertRaises(ValueError, posix.sched_setaffinity, 0, map(int, "0X"))
        self.assertRaises(OverflowError, posix.sched_setaffinity, 0, [1<<128])
        self.assertRaises(OSError, posix.sched_setaffinity, -1, mask)

    eleza test_rtld_constants(self):
        # check presence of major RTLD_* constants
        posix.RTLD_LAZY
        posix.RTLD_NOW
        posix.RTLD_GLOBAL
        posix.RTLD_LOCAL

    @unittest.skipUnless(hasattr(os, 'SEEK_HOLE'),
                         "test needs an OS that reports file holes")
    eleza test_fs_holes(self):
        # Even ikiwa the filesystem doesn't report holes,
        # ikiwa the OS supports it the SEEK_* constants
        # will be defined na will have a consistent
        # behaviour:
        # os.SEEK_DATA = current position
        # os.SEEK_HOLE = end of file position
        ukijumuisha open(support.TESTFN, 'r+b') kama fp:
            fp.write(b"hello")
            fp.flush()
            size = fp.tell()
            fno = fp.fileno()
            try :
                kila i kwenye range(size):
                    self.assertEqual(i, os.lseek(fno, i, os.SEEK_DATA))
                    self.assertLessEqual(size, os.lseek(fno, i, os.SEEK_HOLE))
                self.assertRaises(OSError, os.lseek, fno, size, os.SEEK_DATA)
                self.assertRaises(OSError, os.lseek, fno, size, os.SEEK_HOLE)
            tatizo OSError :
                # Some OSs claim to support SEEK_HOLE/SEEK_DATA
                # but it ni sio true.
                # For instance:
                # http://lists.freebsd.org/pipermail/freebsd-amd64/2012-January/014332.html
                ashiria unittest.SkipTest("OSError raised!")

    eleza test_path_error2(self):
        """
        Test functions that call path_error2(), providing two filenames kwenye their exceptions.
        """
        kila name kwenye ("rename", "replace", "link"):
            function = getattr(os, name, Tupu)
            ikiwa function ni Tupu:
                endelea

            kila dst kwenye ("noodly2", support.TESTFN):
                jaribu:
                    function('doesnotexistfilename', dst)
                tatizo OSError kama e:
                    self.assertIn("'doesnotexistfilename' -> '{}'".format(dst), str(e))
                    koma
            isipokua:
                self.fail("No valid path_error2() test kila os." + name)

    eleza test_path_with_null_character(self):
        fn = support.TESTFN
        fn_with_NUL = fn + '\0'
        self.addCleanup(support.unlink, fn)
        support.unlink(fn)
        fd = Tupu
        jaribu:
            ukijumuisha self.assertRaises(ValueError):
                fd = os.open(fn_with_NUL, os.O_WRONLY | os.O_CREAT) # raises
        mwishowe:
            ikiwa fd ni sio Tupu:
                os.close(fd)
        self.assertUongo(os.path.exists(fn))
        self.assertRaises(ValueError, os.mkdir, fn_with_NUL)
        self.assertUongo(os.path.exists(fn))
        open(fn, 'wb').close()
        self.assertRaises(ValueError, os.stat, fn_with_NUL)

    eleza test_path_with_null_byte(self):
        fn = os.fsencode(support.TESTFN)
        fn_with_NUL = fn + b'\0'
        self.addCleanup(support.unlink, fn)
        support.unlink(fn)
        fd = Tupu
        jaribu:
            ukijumuisha self.assertRaises(ValueError):
                fd = os.open(fn_with_NUL, os.O_WRONLY | os.O_CREAT) # raises
        mwishowe:
            ikiwa fd ni sio Tupu:
                os.close(fd)
        self.assertUongo(os.path.exists(fn))
        self.assertRaises(ValueError, os.mkdir, fn_with_NUL)
        self.assertUongo(os.path.exists(fn))
        open(fn, 'wb').close()
        self.assertRaises(ValueError, os.stat, fn_with_NUL)

kundi PosixGroupsTester(unittest.TestCase):

    eleza setUp(self):
        ikiwa posix.getuid() != 0:
            ashiria unittest.SkipTest("sio enough privileges")
        ikiwa sio hasattr(posix, 'getgroups'):
            ashiria unittest.SkipTest("need posix.getgroups")
        ikiwa sys.platform == 'darwin':
            ashiria unittest.SkipTest("getgroups(2) ni broken on OSX")
        self.saved_groups = posix.getgroups()

    eleza tearDown(self):
        ikiwa hasattr(posix, 'setgroups'):
            posix.setgroups(self.saved_groups)
        lasivyo hasattr(posix, 'initgroups'):
            name = pwd.getpwuid(posix.getuid()).pw_name
            posix.initgroups(name, self.saved_groups[0])

    @unittest.skipUnless(hasattr(posix, 'initgroups'),
                         "test needs posix.initgroups()")
    eleza test_initgroups(self):
        # find missing group

        g = max(self.saved_groups ama [0]) + 1
        name = pwd.getpwuid(posix.getuid()).pw_name
        posix.initgroups(name, g)
        self.assertIn(g, posix.getgroups())

    @unittest.skipUnless(hasattr(posix, 'setgroups'),
                         "test needs posix.setgroups()")
    eleza test_setgroups(self):
        kila groups kwenye [[0], list(range(16))]:
            posix.setgroups(groups)
            self.assertListEqual(groups, posix.getgroups())


kundi _PosixSpawnMixin:
    # Program which does nothing na exits ukijumuisha status 0 (success)
    NOOP_PROGRAM = (sys.executable, '-I', '-S', '-c', 'pita')
    spawn_func = Tupu

    eleza python_args(self, *args):
        # Disable site module to avoid side effects. For example,
        # on Fedora 28, ikiwa the HOME environment variable ni sio set,
        # site._getuserbase() calls pwd.getpwuid() which opens
        # /var/lib/sss/mc/pitawd but then leaves the file open which makes
        # test_close_file() to fail.
        rudisha (sys.executable, '-I', '-S', *args)

    eleza test_returns_pid(self):
        pidfile = support.TESTFN
        self.addCleanup(support.unlink, pidfile)
        script = f"""ikiwa 1:
            agiza os
            ukijumuisha open({pidfile!r}, "w") kama pidfile:
                pidfile.write(str(os.getpid()))
            """
        args = self.python_args('-c', script)
        pid = self.spawn_func(args[0], args, os.environ)
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))
        ukijumuisha open(pidfile) kama f:
            self.assertEqual(f.read(), str(pid))

    eleza test_no_such_executable(self):
        no_such_executable = 'no_such_executable'
        jaribu:
            pid = self.spawn_func(no_such_executable,
                                  [no_such_executable],
                                  os.environ)
        # bpo-35794: PermissionError can be raised ikiwa there are
        # directories kwenye the $PATH that are sio accessible.
        tatizo (FileNotFoundError, PermissionError) kama exc:
            self.assertEqual(exc.filename, no_such_executable)
        isipokua:
            pid2, status = os.waitpid(pid, 0)
            self.assertEqual(pid2, pid)
            self.assertNotEqual(status, 0)

    eleza test_specify_environment(self):
        envfile = support.TESTFN
        self.addCleanup(support.unlink, envfile)
        script = f"""ikiwa 1:
            agiza os
            ukijumuisha open({envfile!r}, "w") kama envfile:
                envfile.write(os.environ['foo'])
        """
        args = self.python_args('-c', script)
        pid = self.spawn_func(args[0], args,
                              {**os.environ, 'foo': 'bar'})
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))
        ukijumuisha open(envfile) kama f:
            self.assertEqual(f.read(), 'bar')

    eleza test_none_file_actions(self):
        pid = self.spawn_func(
            self.NOOP_PROGRAM[0],
            self.NOOP_PROGRAM,
            os.environ,
            file_actions=Tupu
        )
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    eleza test_empty_file_actions(self):
        pid = self.spawn_func(
            self.NOOP_PROGRAM[0],
            self.NOOP_PROGRAM,
            os.environ,
            file_actions=[]
        )
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    eleza test_resetids_explicit_default(self):
        pid = self.spawn_func(
            sys.executable,
            [sys.executable, '-c', 'pita'],
            os.environ,
            resetids=Uongo
        )
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    eleza test_resetids(self):
        pid = self.spawn_func(
            sys.executable,
            [sys.executable, '-c', 'pita'],
            os.environ,
            resetids=Kweli
        )
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    eleza test_resetids_wrong_type(self):
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(sys.executable,
                            [sys.executable, "-c", "pita"],
                            os.environ, resetids=Tupu)

    eleza test_setpgroup(self):
        pid = self.spawn_func(
            sys.executable,
            [sys.executable, '-c', 'pita'],
            os.environ,
            setpgroup=os.getpgrp()
        )
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    eleza test_setpgroup_wrong_type(self):
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(sys.executable,
                            [sys.executable, "-c", "pita"],
                            os.environ, setpgroup="023")

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                           'need signal.pthread_sigmask()')
    eleza test_setsigmask(self):
        code = textwrap.dedent("""\
            agiza signal
            signal.raise_signal(signal.SIGUSR1)""")

        pid = self.spawn_func(
            sys.executable,
            [sys.executable, '-c', code],
            os.environ,
            setsigmask=[signal.SIGUSR1]
        )
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    eleza test_setsigmask_wrong_type(self):
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(sys.executable,
                            [sys.executable, "-c", "pita"],
                            os.environ, setsigmask=34)
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(sys.executable,
                            [sys.executable, "-c", "pita"],
                            os.environ, setsigmask=["j"])
        ukijumuisha self.assertRaises(ValueError):
            self.spawn_func(sys.executable,
                            [sys.executable, "-c", "pita"],
                            os.environ, setsigmask=[signal.NSIG,
                                                    signal.NSIG+1])

    eleza test_setsid(self):
        rfd, wfd = os.pipe()
        self.addCleanup(os.close, rfd)
        jaribu:
            os.set_inheritable(wfd, Kweli)

            code = textwrap.dedent(f"""
                agiza os
                fd = {wfd}
                sid = os.getsid(0)
                os.write(fd, str(sid).encode())
            """)

            jaribu:
                pid = self.spawn_func(sys.executable,
                                      [sys.executable, "-c", code],
                                      os.environ, setsid=Kweli)
            tatizo NotImplementedError kama exc:
                self.skipTest(f"setsid ni sio supported: {exc!r}")
            tatizo PermissionError kama exc:
                self.skipTest(f"setsid failed with: {exc!r}")
        mwishowe:
            os.close(wfd)

        self.assertEqual(os.waitpid(pid, 0), (pid, 0))
        output = os.read(rfd, 100)
        child_sid = int(output)
        parent_sid = os.getsid(os.getpid())
        self.assertNotEqual(parent_sid, child_sid)

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    eleza test_setsigdef(self):
        original_handler = signal.signal(signal.SIGUSR1, signal.SIG_IGN)
        code = textwrap.dedent("""\
            agiza signal
            signal.raise_signal(signal.SIGUSR1)""")
        jaribu:
            pid = self.spawn_func(
                sys.executable,
                [sys.executable, '-c', code],
                os.environ,
                setsigdef=[signal.SIGUSR1]
            )
        mwishowe:
            signal.signal(signal.SIGUSR1, original_handler)

        pid2, status = os.waitpid(pid, 0)
        self.assertEqual(pid2, pid)
        self.assertKweli(os.WIFSIGNALED(status), status)
        self.assertEqual(os.WTERMSIG(status), signal.SIGUSR1)

    eleza test_setsigdef_wrong_type(self):
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(sys.executable,
                            [sys.executable, "-c", "pita"],
                            os.environ, setsigdef=34)
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(sys.executable,
                            [sys.executable, "-c", "pita"],
                            os.environ, setsigdef=["j"])
        ukijumuisha self.assertRaises(ValueError):
            self.spawn_func(sys.executable,
                            [sys.executable, "-c", "pita"],
                            os.environ, setsigdef=[signal.NSIG, signal.NSIG+1])

    @requires_sched
    @unittest.skipIf(sys.platform.startswith(('freebsd', 'netbsd')),
                     "bpo-34685: test can fail on BSD")
    eleza test_setscheduler_only_param(self):
        policy = os.sched_getscheduler(0)
        priority = os.sched_get_priority_min(policy)
        code = textwrap.dedent(f"""\
            agiza os, sys
            ikiwa os.sched_getscheduler(0) != {policy}:
                sys.exit(101)
            ikiwa os.sched_getparam(0).sched_priority != {priority}:
                sys.exit(102)""")
        pid = self.spawn_func(
            sys.executable,
            [sys.executable, '-c', code],
            os.environ,
            scheduler=(Tupu, os.sched_param(priority))
        )
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    @requires_sched
    @unittest.skipIf(sys.platform.startswith(('freebsd', 'netbsd')),
                     "bpo-34685: test can fail on BSD")
    eleza test_setscheduler_with_policy(self):
        policy = os.sched_getscheduler(0)
        priority = os.sched_get_priority_min(policy)
        code = textwrap.dedent(f"""\
            agiza os, sys
            ikiwa os.sched_getscheduler(0) != {policy}:
                sys.exit(101)
            ikiwa os.sched_getparam(0).sched_priority != {priority}:
                sys.exit(102)""")
        pid = self.spawn_func(
            sys.executable,
            [sys.executable, '-c', code],
            os.environ,
            scheduler=(policy, os.sched_param(priority))
        )
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    eleza test_multiple_file_actions(self):
        file_actions = [
            (os.POSIX_SPAWN_OPEN, 3, os.path.realpath(__file__), os.O_RDONLY, 0),
            (os.POSIX_SPAWN_CLOSE, 0),
            (os.POSIX_SPAWN_DUP2, 1, 4),
        ]
        pid = self.spawn_func(self.NOOP_PROGRAM[0],
                              self.NOOP_PROGRAM,
                              os.environ,
                              file_actions=file_actions)
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))

    eleza test_bad_file_actions(self):
        args = self.NOOP_PROGRAM
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(args[0], args, os.environ,
                            file_actions=[Tupu])
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(args[0], args, os.environ,
                            file_actions=[()])
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(args[0], args, os.environ,
                            file_actions=[(Tupu,)])
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(args[0], args, os.environ,
                            file_actions=[(12345,)])
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(args[0], args, os.environ,
                            file_actions=[(os.POSIX_SPAWN_CLOSE,)])
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(args[0], args, os.environ,
                            file_actions=[(os.POSIX_SPAWN_CLOSE, 1, 2)])
        ukijumuisha self.assertRaises(TypeError):
            self.spawn_func(args[0], args, os.environ,
                            file_actions=[(os.POSIX_SPAWN_CLOSE, Tupu)])
        ukijumuisha self.assertRaises(ValueError):
            self.spawn_func(args[0], args, os.environ,
                            file_actions=[(os.POSIX_SPAWN_OPEN,
                                           3, __file__ + '\0',
                                           os.O_RDONLY, 0)])

    eleza test_open_file(self):
        outfile = support.TESTFN
        self.addCleanup(support.unlink, outfile)
        script = """ikiwa 1:
            agiza sys
            sys.stdout.write("hello")
            """
        file_actions = [
            (os.POSIX_SPAWN_OPEN, 1, outfile,
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                stat.S_IRUSR | stat.S_IWUSR),
        ]
        args = self.python_args('-c', script)
        pid = self.spawn_func(args[0], args, os.environ,
                              file_actions=file_actions)
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))
        ukijumuisha open(outfile) kama f:
            self.assertEqual(f.read(), 'hello')

    eleza test_close_file(self):
        closefile = support.TESTFN
        self.addCleanup(support.unlink, closefile)
        script = f"""ikiwa 1:
            agiza os
            jaribu:
                os.fstat(0)
            tatizo OSError kama e:
                ukijumuisha open({closefile!r}, 'w') kama closefile:
                    closefile.write('is closed %d' % e.errno)
            """
        args = self.python_args('-c', script)
        pid = self.spawn_func(args[0], args, os.environ,
                              file_actions=[(os.POSIX_SPAWN_CLOSE, 0)])
        self.assertEqual(os.waitpid(pid, 0), (pid, 0))
        ukijumuisha open(closefile) kama f:
            self.assertEqual(f.read(), 'is closed %d' % errno.EBADF)

    eleza test_dup2(self):
        dupfile = support.TESTFN
        self.addCleanup(support.unlink, dupfile)
        script = """ikiwa 1:
            agiza sys
            sys.stdout.write("hello")
            """
        ukijumuisha open(dupfile, "wb") kama childfile:
            file_actions = [
                (os.POSIX_SPAWN_DUP2, childfile.fileno(), 1),
            ]
            args = self.python_args('-c', script)
            pid = self.spawn_func(args[0], args, os.environ,
                                  file_actions=file_actions)
            self.assertEqual(os.waitpid(pid, 0), (pid, 0))
        ukijumuisha open(dupfile) kama f:
            self.assertEqual(f.read(), 'hello')


@unittest.skipUnless(hasattr(os, 'posix_spawn'), "test needs os.posix_spawn")
kundi TestPosixSpawn(unittest.TestCase, _PosixSpawnMixin):
    spawn_func = getattr(posix, 'posix_spawn', Tupu)


@unittest.skipUnless(hasattr(os, 'posix_spawnp'), "test needs os.posix_spawnp")
kundi TestPosixSpawnP(unittest.TestCase, _PosixSpawnMixin):
    spawn_func = getattr(posix, 'posix_spawnp', Tupu)

    @support.skip_unless_symlink
    eleza test_posix_spawnp(self):
        # Use a symlink to create a program kwenye its own temporary directory
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(support.rmtree, temp_dir)

        program = 'posix_spawnp_test_program.exe'
        program_fullpath = os.path.join(temp_dir, program)
        os.symlink(sys.executable, program_fullpath)

        jaribu:
            path = os.pathsep.join((temp_dir, os.environ['PATH']))
        tatizo KeyError:
            path = temp_dir   # PATH ni sio set

        spawn_args = (program, '-I', '-S', '-c', 'pita')
        code = textwrap.dedent("""
            agiza os
            args = %a
            pid = os.posix_spawnp(args[0], args, os.environ)
            pid2, status = os.waitpid(pid, 0)
            ikiwa pid2 != pid:
                ashiria Exception(f"pid {pid2} != {pid}")
            ikiwa status != 0:
                ashiria Exception(f"status {status} != 0")
        """ % (spawn_args,))

        # Use a subprocess to test os.posix_spawnp() ukijumuisha a modified PATH
        # environment variable: posix_spawnp() uses the current environment
        # to locate the program, sio its environment argument.
        args = ('-c', code)
        assert_python_ok(*args, PATH=path)


eleza test_main():
    jaribu:
        support.run_unittest(
            PosixTester,
            PosixGroupsTester,
            TestPosixSpawn,
            TestPosixSpawnP,
        )
    mwishowe:
        support.reap_children()

ikiwa __name__ == '__main__':
    test_main()
