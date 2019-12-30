"""Basic tests kila os.popen()

  Particularly useful kila platforms that fake popen.
"""

agiza unittest
kutoka test agiza support
agiza os, sys

# Test that command-lines get down kama we expect.
# To do this we execute:
#    python -c "agiza sys;andika(sys.argv)" {rest_of_commandline}
# This results kwenye Python being spawned na printing the sys.argv list.
# We can then eval() the result of this, na see what each argv was.
python = sys.executable
ikiwa ' ' kwenye python:
    python = '"' + python + '"'     # quote embedded space kila cmdline

kundi PopenTest(unittest.TestCase):

    eleza _do_test_commandline(self, cmdline, expected):
        cmd = '%s -c "agiza sys; andika(sys.argv)" %s'
        cmd = cmd % (python, cmdline)
        ukijumuisha os.popen(cmd) kama p:
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
            'foo "spam na eggs" "silly walk"',
            ["foo", "spam na eggs", "silly walk"]
        )
        self._do_test_commandline(
            'foo "a \\"quoted\\" arg" bar',
            ["foo", 'a "quoted" arg', "bar"]
        )
        support.reap_children()

    eleza test_return_code(self):
        self.assertEqual(os.popen("exit 0").close(), Tupu)
        ikiwa os.name == 'nt':
            self.assertEqual(os.popen("exit 42").close(), 42)
        isipokua:
            self.assertEqual(os.popen("exit 42").close(), 42 << 8)

    eleza test_contextmanager(self):
        ukijumuisha os.popen("echo hello") kama f:
            self.assertEqual(f.read(), "hello\n")

    eleza test_iterating(self):
        ukijumuisha os.popen("echo hello") kama f:
            self.assertEqual(list(f), ["hello\n"])

    eleza test_keywords(self):
        ukijumuisha os.popen(cmd="exit 0", mode="w", buffering=-1):
            pita

ikiwa __name__ == "__main__":
    unittest.main()
