"""Test the interactive interpreter."""

agiza sys
agiza os
agiza unittest
agiza subprocess
kutoka textwrap agiza dedent
kutoka test.support agiza cpython_only, SuppressCrashReport
kutoka test.support.script_helper agiza kill_python

eleza spawn_repl(*args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kw):
    """Run the Python REPL ukijumuisha the given arguments.

    kw ni extra keyword args to pita to subprocess.Popen. Returns a Popen
    object.
    """

    # To run the REPL without using a terminal, spawn python ukijumuisha the command
    # line option '-i' na the process name set to '<stdin>'.
    # The directory of argv[0] must match the directory of the Python
    # executable kila the Popen() call to python to succeed kama the directory
    # path may be used by Py_GetPath() to build the default module search
    # path.
    stdin_fname = os.path.join(os.path.dirname(sys.executable), "<stdin>")
    cmd_line = [stdin_fname, '-E', '-i']
    cmd_line.extend(args)

    # Set TERM=vt100, kila the rationale see the comments kwenye spawn_python() of
    # test.support.script_helper.
    env = kw.setdefault('env', dict(os.environ))
    env['TERM'] = 'vt100'
    rudisha subprocess.Popen(cmd_line, executable=sys.executable,
                            stdin=subprocess.PIPE,
                            stdout=stdout, stderr=stderr,
                            **kw)

kundi TestInteractiveInterpreter(unittest.TestCase):

    @cpython_only
    eleza test_no_memory(self):
        # Issue #30696: Fix the interactive interpreter looping endlessly when
        # no memory. Check also that the fix does sio koma the interactive
        # loop when an exception ni ashiriad.
        user_input = """
            agiza sys, _testcapi
            1/0
            andika('After the exception.')
            _testcapi.set_nomemory(0)
            sys.exit(0)
        """
        user_input = dedent(user_input)
        user_input = user_input.encode()
        p = spawn_repl()
        ukijumuisha SuppressCrashReport():
            p.stdin.write(user_input)
        output = kill_python(p)
        self.assertIn(b'After the exception.', output)
        # Exit code 120: Py_FinalizeEx() failed to flush stdout na stderr.
        self.assertIn(p.returncode, (1, 120))

ikiwa __name__ == "__main__":
    unittest.main()
