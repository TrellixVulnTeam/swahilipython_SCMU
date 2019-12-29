agiza os
agiza signal
agiza subprocess
agiza sys
agiza unittest

kutoka test agiza support
kutoka test.support agiza script_helper


@unittest.skipUnless(os.name == "posix", "only supported on Unix")
kundi EINTRTests(unittest.TestCase):

    @unittest.skipUnless(hasattr(signal, "setitimer"), "requires setitimer()")
    eleza test_all(self):
        # Run the tester kwenye a sub-process, to make sure there ni only one
        # thread (kila reliable signal delivery).
        tester = support.findfile("eintr_tester.py", subdir="eintrdata")
        # use -u to try to get the full output ikiwa the test hangs ama crash
        args = ["-u", tester, "-v"]
        ikiwa support.verbose:
            andika()
            andika("--- run eintr_tester.py ---", flush=Kweli)
            # In verbose mode, the child process inherit stdout na stdout,
            # to see output kwenye realtime na reduce the risk of losing output.
            args = [sys.executable, "-E", "-X", "faulthandler", *args]
            proc = subprocess.run(args)
            andika(f"--- eintr_tester.py completed: "
                  f"exit code {proc.returncode} ---", flush=Kweli)
            ikiwa proc.returncode:
                self.fail("eintr_tester.py failed")
        isipokua:
            script_helper.assert_python_ok("-u", tester, "-v")


ikiwa __name__ == "__main__":
    unittest.main()
