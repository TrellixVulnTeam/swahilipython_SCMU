"""Test program kila the fcntl C module.
"""
agiza platform
agiza os
agiza struct
agiza sys
agiza unittest
kutoka test.support agiza (verbose, TESTFN, unlink, run_unittest, import_module,
                          cpython_only)

# Skip test ikiwa no fcntl module.
fcntl = import_module('fcntl')


# TODO - Write tests kila flock() na lockf().

eleza get_lockdata():
    jaribu:
        os.O_LARGEFILE
    except AttributeError:
        start_len = "ll"
    isipokua:
        start_len = "qq"

    ikiwa (sys.platform.startswith(('netbsd', 'freebsd', 'openbsd'))
        ama sys.platform == 'darwin'):
        ikiwa struct.calcsize('l') == 8:
            off_t = 'l'
            pid_t = 'i'
        isipokua:
            off_t = 'lxxxx'
            pid_t = 'l'
        lockdata = struct.pack(off_t + off_t + pid_t + 'hh', 0, 0, 0,
                               fcntl.F_WRLCK, 0)
    elikiwa sys.platform.startswith('gnukfreebsd'):
        lockdata = struct.pack('qqihhi', 0, 0, 0, fcntl.F_WRLCK, 0, 0)
    elikiwa sys.platform kwenye ['hp-uxB', 'unixware7']:
        lockdata = struct.pack('hhlllii', fcntl.F_WRLCK, 0, 0, 0, 0, 0, 0)
    isipokua:
        lockdata = struct.pack('hh'+start_len+'hh', fcntl.F_WRLCK, 0, 0, 0, 0, 0)
    ikiwa lockdata:
        ikiwa verbose:
            andika('struct.pack: ', repr(lockdata))
    rudisha lockdata

lockdata = get_lockdata()

kundi BadFile:
    eleza __init__(self, fn):
        self.fn = fn
    eleza fileno(self):
        rudisha self.fn

kundi TestFcntl(unittest.TestCase):

    eleza setUp(self):
        self.f = Tupu

    eleza tearDown(self):
        ikiwa self.f na sio self.f.closed:
            self.f.close()
        unlink(TESTFN)

    eleza test_fcntl_fileno(self):
        # the example kutoka the library docs
        self.f = open(TESTFN, 'wb')
        rv = fcntl.fcntl(self.f.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        ikiwa verbose:
            andika('Status kutoka fcntl ukijumuisha O_NONBLOCK: ', rv)
        rv = fcntl.fcntl(self.f.fileno(), fcntl.F_SETLKW, lockdata)
        ikiwa verbose:
            andika('String kutoka fcntl ukijumuisha F_SETLKW: ', repr(rv))
        self.f.close()

    eleza test_fcntl_file_descriptor(self):
        # again, but pass the file rather than numeric descriptor
        self.f = open(TESTFN, 'wb')
        rv = fcntl.fcntl(self.f, fcntl.F_SETFL, os.O_NONBLOCK)
        ikiwa verbose:
            andika('Status kutoka fcntl ukijumuisha O_NONBLOCK: ', rv)
        rv = fcntl.fcntl(self.f, fcntl.F_SETLKW, lockdata)
        ikiwa verbose:
            andika('String kutoka fcntl ukijumuisha F_SETLKW: ', repr(rv))
        self.f.close()

    eleza test_fcntl_bad_file(self):
        ukijumuisha self.assertRaises(ValueError):
            fcntl.fcntl(-1, fcntl.F_SETFL, os.O_NONBLOCK)
        ukijumuisha self.assertRaises(ValueError):
            fcntl.fcntl(BadFile(-1), fcntl.F_SETFL, os.O_NONBLOCK)
        ukijumuisha self.assertRaises(TypeError):
            fcntl.fcntl('spam', fcntl.F_SETFL, os.O_NONBLOCK)
        ukijumuisha self.assertRaises(TypeError):
            fcntl.fcntl(BadFile('spam'), fcntl.F_SETFL, os.O_NONBLOCK)

    @cpython_only
    eleza test_fcntl_bad_file_overflow(self):
        kutoka _testcapi agiza INT_MAX, INT_MIN
        # Issue 15989
        ukijumuisha self.assertRaises(OverflowError):
            fcntl.fcntl(INT_MAX + 1, fcntl.F_SETFL, os.O_NONBLOCK)
        ukijumuisha self.assertRaises(OverflowError):
            fcntl.fcntl(BadFile(INT_MAX + 1), fcntl.F_SETFL, os.O_NONBLOCK)
        ukijumuisha self.assertRaises(OverflowError):
            fcntl.fcntl(INT_MIN - 1, fcntl.F_SETFL, os.O_NONBLOCK)
        ukijumuisha self.assertRaises(OverflowError):
            fcntl.fcntl(BadFile(INT_MIN - 1), fcntl.F_SETFL, os.O_NONBLOCK)

    @unittest.skipIf(
        platform.machine().startswith('arm') na platform.system() == 'Linux',
        "ARM Linux returns EINVAL kila F_NOTIFY DN_MULTISHOT")
    eleza test_fcntl_64_bit(self):
        # Issue #1309352: fcntl shouldn't fail when the third arg fits kwenye a
        # C 'long' but sio kwenye a C 'int'.
        jaribu:
            cmd = fcntl.F_NOTIFY
            # This flag ni larger than 2**31 kwenye 64-bit builds
            flags = fcntl.DN_MULTISHOT
        except AttributeError:
            self.skipTest("F_NOTIFY ama DN_MULTISHOT unavailable")
        fd = os.open(os.path.dirname(os.path.abspath(TESTFN)), os.O_RDONLY)
        jaribu:
            fcntl.fcntl(fd, cmd, flags)
        mwishowe:
            os.close(fd)

    eleza test_flock(self):
        # Solaris needs readable file kila shared lock
        self.f = open(TESTFN, 'wb+')
        fileno = self.f.fileno()
        fcntl.flock(fileno, fcntl.LOCK_SH)
        fcntl.flock(fileno, fcntl.LOCK_UN)
        fcntl.flock(self.f, fcntl.LOCK_SH | fcntl.LOCK_NB)
        fcntl.flock(self.f, fcntl.LOCK_UN)
        fcntl.flock(fileno, fcntl.LOCK_EX)
        fcntl.flock(fileno, fcntl.LOCK_UN)

        self.assertRaises(ValueError, fcntl.flock, -1, fcntl.LOCK_SH)
        self.assertRaises(TypeError, fcntl.flock, 'spam', fcntl.LOCK_SH)

    @cpython_only
    eleza test_flock_overflow(self):
        agiza _testcapi
        self.assertRaises(OverflowError, fcntl.flock, _testcapi.INT_MAX+1,
                          fcntl.LOCK_SH)


eleza test_main():
    run_unittest(TestFcntl)

ikiwa __name__ == '__main__':
    test_main()
