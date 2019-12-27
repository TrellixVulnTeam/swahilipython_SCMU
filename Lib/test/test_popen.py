"""Basic tests for os.popen()

  Particularly useful for platforms that fake popen.
"""

agiza unittest
kutoka test agiza support
agiza os, sys

# Test that command-lines get down as we expect.
# To do this we execute:
#    python -c "agiza sys;andika(sys.argv)" {rest_of_commandline}
# This results in Python being spawned and printing the sys.argv list.
# We can then eval() the result of this, and see what each argv was.
python = sys.executable
ikiwa ' ' in python:
    python = '"' + python + '"'     # quote embedded space for cmdline

kundi PopenTest(unittest.TestCase):

    eleza _do_test_commandline(self, cmdline, expected):
        cmd = '%s -c "agiza sys; andika(sys.argv)" %s'
        cmd = cmd % (python, cmdline)
        with os.popen(cmd) as p:
            data = p.read()
        got = eval(data)[1:] # strip off argv[0]
        self.assertEqual(got, expected)

    eleza test_popen(self):
        self.assertRaises(TypeError, os.popen)
        self._do_test_commandline(
            "foo bar",
            ["foo", "bar"]
        )
        self._do_test_commandline(
            'foo "spam and eggs" "silly walk"',
            ["foo", "spam and eggs", "silly walk"]
        )
        self._do_test_commandline(
            'foo "a \\"quoted\\" arg" bar',
            ["foo", 'a "quoted" arg', "bar"]
        )
        support.reap_children()

    eleza test_return_code(self):
        self.assertEqual(os.popen("exit 0").close(), None)
        ikiwa os.name == 'nt':
            self.assertEqual(os.popen("exit 42").close(), 42)
        else:
            self.assertEqual(os.popen("exit 42").close(), 42 << 8)

    eleza test_contextmanager(self):
        with os.popen("echo hello") as f:
            self.assertEqual(f.read(), "hello\n")

    eleza test_iterating(self):
        with os.popen("echo hello") as f:
            self.assertEqual(list(f), ["hello\n"])

    eleza test_keywords(self):
        with os.popen(cmd="exit 0", mode="w", buffering=-1):
            pass

ikiwa __name__ == "__main__":
    unittest.main()
