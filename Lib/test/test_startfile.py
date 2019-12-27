# Ridiculously simple test of the os.startfile function for Windows.
#
# empty.vbs is an empty file (except for a comment), which does
# nothing when run with cscript or wscript.
#
# A possible improvement would be to have empty.vbs do something that
# we can detect here, to make sure that not only the os.startfile()
# call succeeded, but also the script actually has run.

agiza unittest
kutoka test agiza support
agiza os
agiza platform
agiza sys
kutoka os agiza path

startfile = support.get_attribute(os, 'startfile')


kundi TestCase(unittest.TestCase):
    eleza test_nonexisting(self):
        self.assertRaises(OSError, startfile, "nonexisting.vbs")

    @unittest.skipIf(platform.win32_is_iot(), "starting files is not supported on Windows IoT Core or nanoserver")
    eleza test_empty(self):
        # We need to make sure the child process starts in a directory
        # we're not about to delete. If we're running under -j, that
        # means the test harness provided directory isn't a safe option.
        # See http://bugs.python.org/issue15526 for more details
        with support.change_cwd(path.dirname(sys.executable)):
            empty = path.join(path.dirname(__file__), "empty.vbs")
            startfile(empty)
            startfile(empty, "open")

ikiwa __name__ == "__main__":
    unittest.main()
