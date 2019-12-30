"""Tests kila scripts kwenye the Tools directory.

This file contains regression tests kila some of the scripts found kwenye the
Tools directory of a Python checkout ama tarball, such kama reindent.py.
"""

agiza os
agiza unittest
kutoka test.support.script_helper agiza assert_python_ok
kutoka test.support agiza findfile

kutoka test.test_tools agiza scriptsdir, skip_if_missing

skip_if_missing()

kundi ReindentTests(unittest.TestCase):
    script = os.path.join(scriptsdir, 'reindent.py')

    eleza test_noargs(self):
        assert_python_ok(self.script)

    eleza test_help(self):
        rc, out, err = assert_python_ok(self.script, '-h')
        self.assertEqual(out, b'')
        self.assertGreater(err, b'')

    eleza test_reindent_file_with_bad_encoding(self):
        bad_coding_path = findfile('bad_coding.py')
        rc, out, err = assert_python_ok(self.script, '-r', bad_coding_path)
        self.assertEqual(out, b'')
        self.assertNotEqual(err, b'')


ikiwa __name__ == '__main__':
    unittest.main()
