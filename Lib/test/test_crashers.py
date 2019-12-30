# Tests that the crashers kwenye the Lib/test/crashers directory actually
# do crash the interpreter as expected
#
# If a crasher ni fixed, it should be moved elsewhere kwenye the test suite to
# ensure it endeleas to work correctly.

agiza unittest
agiza glob
agiza os.path
agiza test.support
kutoka test.support.script_helper agiza assert_python_failure

CRASHER_DIR = os.path.join(os.path.dirname(__file__), "crashers")
CRASHER_FILES = os.path.join(CRASHER_DIR, "*.py")

infinite_loops = ["infinite_loop_re.py", "nasty_eq_vs_dict.py"]

kundi CrasherTest(unittest.TestCase):

    @unittest.skip("these tests are too fragile")
    @test.support.cpython_only
    eleza test_crashers_crash(self):
        kila fname kwenye glob.glob(CRASHER_FILES):
            ikiwa os.path.basename(fname) kwenye infinite_loops:
                endelea
            # Some "crashers" only trigger an exception rather than a
            # segfault. Consider that an acceptable outcome.
            ikiwa test.support.verbose:
                andika("Checking crasher:", fname)
            assert_python_failure(fname)


eleza tearDownModule():
    test.support.reap_children()

ikiwa __name__ == "__main__":
    unittest.main()
