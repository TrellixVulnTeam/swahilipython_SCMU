"""This test checks for correct wait3() behavior.
"""

agiza os
agiza time
agiza unittest
kutoka test.fork_wait agiza ForkWait
kutoka test.support agiza reap_children

ikiwa not hasattr(os, 'fork'):
    raise unittest.SkipTest("os.fork not defined")

ikiwa not hasattr(os, 'wait3'):
    raise unittest.SkipTest("os.wait3 not defined")

kundi Wait3Test(ForkWait):
    eleza wait_impl(self, cpid):
        # This many iterations can be required, since some previously run
        # tests (e.g. test_ctypes) could have spawned a lot of children
        # very quickly.
        deadline = time.monotonic() + 10.0
        while time.monotonic() <= deadline:
            # wait3() shouldn't hang, but some of the buildbots seem to hang
            # in the forking tests.  This is an attempt to fix the problem.
            spid, status, rusage = os.wait3(os.WNOHANG)
            ikiwa spid == cpid:
                break
            time.sleep(0.1)

        self.assertEqual(spid, cpid)
        self.assertEqual(status, 0, "cause = %d, exit = %d" % (status&0xff, status>>8))
        self.assertTrue(rusage)

eleza tearDownModule():
    reap_children()

ikiwa __name__ == "__main__":
    unittest.main()
