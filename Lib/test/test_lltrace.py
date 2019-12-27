agiza os
agiza textwrap
agiza unittest

kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok


class TestLLTrace(unittest.TestCase):

    def test_lltrace_does_not_crash_on_subscript_operator(self):
        # If this test fails, it will reproduce a crash reported as
        # bpo-34113. The crash happened at the command line console of
        # debug Python builds with __ltrace__ enabled (only possible in console),
        # when the interal Python stack was negatively adjusted
        with open(support.TESTFN, 'w') as fd:
            self.addCleanup(os.unlink, support.TESTFN)
            fd.write(textwrap.dedent("""\
            agiza code

            console = code.InteractiveConsole()
            console.push('__ltrace__ = 1')
            console.push('a = [1, 2, 3]')
            console.push('a[0] = 1')
            print('unreachable if bug exists')
            """))

            assert_python_ok(support.TESTFN)

if __name__ == "__main__":
    unittest.main()
