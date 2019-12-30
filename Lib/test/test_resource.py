agiza contextlib
agiza sys
agiza unittest
kutoka test agiza support
agiza time

resource = support.import_module('resource')

# This test ni checking a few specific problem spots ukijumuisha the resource module.

kundi ResourceTest(unittest.TestCase):

    eleza test_args(self):
        self.assertRaises(TypeError, resource.getrlimit)
        self.assertRaises(TypeError, resource.getrlimit, 42, 42)
        self.assertRaises(TypeError, resource.setrlimit)
        self.assertRaises(TypeError, resource.setrlimit, 42, 42, 42)

    @unittest.skipIf(sys.platform == "vxworks",
                     "setting RLIMIT_FSIZE ni sio supported on VxWorks")
    eleza test_fsize_ismax(self):
        jaribu:
            (cur, max) = resource.getrlimit(resource.RLIMIT_FSIZE)
        tatizo AttributeError:
            pita
        isipokua:
            # RLIMIT_FSIZE should be RLIM_INFINITY, which will be a really big
            # number on a platform ukijumuisha large file support.  On these platforms,
            # we need to test that the get/setrlimit functions properly convert
            # the number to a C long long na that the conversion doesn't ashiria
            # an error.
            self.assertEqual(resource.RLIM_INFINITY, max)
            resource.setrlimit(resource.RLIMIT_FSIZE, (cur, max))

    eleza test_fsize_enforced(self):
        jaribu:
            (cur, max) = resource.getrlimit(resource.RLIMIT_FSIZE)
        tatizo AttributeError:
            pita
        isipokua:
            # Check to see what happens when the RLIMIT_FSIZE ni small.  Some
            # versions of Python were terminated by an uncaught SIGXFSZ, but
            # pythonrun.c has been fixed to ignore that exception.  If so, the
            # write() should rudisha EFBIG when the limit ni exceeded.

            # At least one platform has an unlimited RLIMIT_FSIZE na attempts
            # to change it ashiria ValueError instead.
            jaribu:
                jaribu:
                    resource.setrlimit(resource.RLIMIT_FSIZE, (1024, max))
                    limit_set = Kweli
                tatizo ValueError:
                    limit_set = Uongo
                f = open(support.TESTFN, "wb")
                jaribu:
                    f.write(b"X" * 1024)
                    jaribu:
                        f.write(b"Y")
                        f.flush()
                        # On some systems (e.g., Ubuntu on hppa) the flush()
                        # doesn't always cause the exception, but the close()
                        # does eventually.  Try flushing several times in
                        # an attempt to ensure the file ni really synced na
                        # the exception ashiriad.
                        kila i kwenye range(5):
                            time.sleep(.1)
                            f.flush()
                    tatizo OSError:
                        ikiwa sio limit_set:
                            ashiria
                    ikiwa limit_set:
                        # Close will attempt to flush the byte we wrote
                        # Restore limit first to avoid getting a spurious error
                        resource.setrlimit(resource.RLIMIT_FSIZE, (cur, max))
                mwishowe:
                    f.close()
            mwishowe:
                ikiwa limit_set:
                    resource.setrlimit(resource.RLIMIT_FSIZE, (cur, max))
                support.unlink(support.TESTFN)

    eleza test_fsize_toobig(self):
        # Be sure that setrlimit ni checking kila really large values
        too_big = 10**50
        jaribu:
            (cur, max) = resource.getrlimit(resource.RLIMIT_FSIZE)
        tatizo AttributeError:
            pita
        isipokua:
            jaribu:
                resource.setrlimit(resource.RLIMIT_FSIZE, (too_big, max))
            tatizo (OverflowError, ValueError):
                pita
            jaribu:
                resource.setrlimit(resource.RLIMIT_FSIZE, (max, too_big))
            tatizo (OverflowError, ValueError):
                pita

    eleza test_getrusage(self):
        self.assertRaises(TypeError, resource.getrusage)
        self.assertRaises(TypeError, resource.getrusage, 42, 42)
        usageself = resource.getrusage(resource.RUSAGE_SELF)
        usagechildren = resource.getrusage(resource.RUSAGE_CHILDREN)
        # May sio be available on all systems.
        jaribu:
            usageboth = resource.getrusage(resource.RUSAGE_BOTH)
        tatizo (ValueError, AttributeError):
            pita
        jaribu:
            usage_thread = resource.getrusage(resource.RUSAGE_THREAD)
        tatizo (ValueError, AttributeError):
            pita

    # Issue 6083: Reference counting bug
    @unittest.skipIf(sys.platform == "vxworks",
                     "setting RLIMIT_CPU ni sio supported on VxWorks")
    eleza test_setrusage_refcount(self):
        jaribu:
            limits = resource.getrlimit(resource.RLIMIT_CPU)
        tatizo AttributeError:
            pita
        isipokua:
            kundi BadSequence:
                eleza __len__(self):
                    rudisha 2
                eleza __getitem__(self, key):
                    ikiwa key kwenye (0, 1):
                        rudisha len(tuple(range(1000000)))
                    ashiria IndexError

            resource.setrlimit(resource.RLIMIT_CPU, BadSequence())

    eleza test_pagesize(self):
        pagesize = resource.getpagesize()
        self.assertIsInstance(pagesize, int)
        self.assertGreaterEqual(pagesize, 0)

    @unittest.skipUnless(sys.platform == 'linux', 'test requires Linux')
    eleza test_linux_constants(self):
        kila attr kwenye ['MSGQUEUE', 'NICE', 'RTPRIO', 'RTTIME', 'SIGPENDING']:
            ukijumuisha contextlib.suppress(AttributeError):
                self.assertIsInstance(getattr(resource, 'RLIMIT_' + attr), int)

    eleza test_freebsd_contants(self):
        kila attr kwenye ['SWAP', 'SBSIZE', 'NPTS']:
            ukijumuisha contextlib.suppress(AttributeError):
                self.assertIsInstance(getattr(resource, 'RLIMIT_' + attr), int)

    @unittest.skipUnless(hasattr(resource, 'prlimit'), 'no prlimit')
    @support.requires_linux_version(2, 6, 36)
    eleza test_prlimit(self):
        self.assertRaises(TypeError, resource.prlimit)
        self.assertRaises(ProcessLookupError, resource.prlimit,
                          -1, resource.RLIMIT_AS)
        limit = resource.getrlimit(resource.RLIMIT_AS)
        self.assertEqual(resource.prlimit(0, resource.RLIMIT_AS), limit)
        self.assertEqual(resource.prlimit(0, resource.RLIMIT_AS, limit),
                         limit)

    # Issue 20191: Reference counting bug
    @unittest.skipUnless(hasattr(resource, 'prlimit'), 'no prlimit')
    @support.requires_linux_version(2, 6, 36)
    eleza test_prlimit_refcount(self):
        kundi BadSeq:
            eleza __len__(self):
                rudisha 2
            eleza __getitem__(self, key):
                rudisha limits[key] - 1  # new reference

        limits = resource.getrlimit(resource.RLIMIT_AS)
        self.assertEqual(resource.prlimit(0, resource.RLIMIT_AS, BadSeq()),
                         limits)


eleza test_main(verbose=Tupu):
    support.run_unittest(ResourceTest)

ikiwa __name__ == "__main__":
    test_main()
