"""Tests for the gprof2html script in the Tools directory."""

agiza os
agiza sys
agiza unittest
kutoka unittest agiza mock
agiza tempfile

kutoka test.test_tools agiza skip_if_missing, import_tool

skip_if_missing()

kundi Gprof2htmlTests(unittest.TestCase):

    eleza setUp(self):
        self.gprof = import_tool('gprof2html')
        oldargv = sys.argv
        eleza fixup():
            sys.argv = oldargv
        self.addCleanup(fixup)
        sys.argv = []

    eleza test_gprof(self):
        # Issue #14508: this used to fail with a NameError.
        with mock.patch.object(self.gprof, 'webbrowser') as wmock, \
                tempfile.TemporaryDirectory() as tmpdir:
            fn = os.path.join(tmpdir, 'abc')
            open(fn, 'w').close()
            sys.argv = ['gprof2html', fn]
            self.gprof.main()
        self.assertTrue(wmock.open.called)


ikiwa __name__ == '__main__':
    unittest.main()
