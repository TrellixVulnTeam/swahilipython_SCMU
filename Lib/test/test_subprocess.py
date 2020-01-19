agiza unittest
kutoka unittest agiza mock
kutoka test agiza support
agiza subprocess
agiza sys
agiza signal
agiza io
agiza itertools
agiza os
agiza errno
agiza tempfile
agiza time
agiza traceback
agiza selectors
agiza sysconfig
agiza select
agiza shutil
agiza threading
agiza gc
agiza textwrap
kutoka test.support agiza FakePath

jaribu:
    agiza _testcapi
tatizo ImportError:
    _testcapi = Tupu


ikiwa support.PGO:
    ashiria unittest.SkipTest("test ni sio helpful kila PGO")

mswindows = (sys.platform == "win32")

#
# Depends on the following external programs: Python
#

ikiwa mswindows:
    SETBINARY = ('agiza msvcrt; msvcrt.setmode(sys.stdout.fileno(), '
                                                'os.O_BINARY);')
isipokua:
    SETBINARY = ''

NONEXISTING_CMD = ('nonexisting_i_hope',)
# Ignore errors that indicate the command was sio found
NONEXISTING_ERRORS = (FileNotFoundError, NotADirectoryError, PermissionError)


kundi BaseTestCase(unittest.TestCase):
    eleza setUp(self):
        # Try to minimize the number of children we have so this test
        # doesn't crash on some buildbots (Alphas kwenye particular).
        support.reap_children()

    eleza tearDown(self):
        ikiwa sio mswindows:
            # subprocess._active ni sio used on Windows na ni set to Tupu.
            kila inst kwenye subprocess._active:
                inst.wait()
            subprocess._cleanup()
            self.assertUongo(
                subprocess._active, "subprocess._active sio empty"
            )
        self.doCleanups()
        support.reap_children()

    eleza assertStderrEqual(self, stderr, expected, msg=Tupu):
        # In a debug build, stuff like "[6580 refs]" ni printed to stderr at
        # shutdown time.  That frustrates tests trying to check stderr produced
        # kutoka a spawned Python process.
        actual = support.strip_python_stderr(stderr)
        # strip_python_stderr also strips whitespace, so we do too.
        expected = expected.strip()
        self.assertEqual(actual, expected, msg)


kundi PopenTestException(Exception):
    pita


kundi PopenExecuteChildRaises(subprocess.Popen):
    """Popen subkundi kila testing cleanup of subprocess.PIPE filehandles when
    _execute_child fails.
    """
    eleza _execute_child(self, *args, **kwargs):
        ashiria PopenTestException("Forced Exception kila Test")


kundi ProcessTestCase(BaseTestCase):

    eleza test_io_buffered_by_default(self):
        p = subprocess.Popen([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        jaribu:
            self.assertIsInstance(p.stdin, io.BufferedIOBase)
            self.assertIsInstance(p.stdout, io.BufferedIOBase)
            self.assertIsInstance(p.stderr, io.BufferedIOBase)
        mwishowe:
            p.stdin.close()
            p.stdout.close()
            p.stderr.close()
            p.wait()

    eleza test_io_unbuffered_works(self):
        p = subprocess.Popen([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=0)
        jaribu:
            self.assertIsInstance(p.stdin, io.RawIOBase)
            self.assertIsInstance(p.stdout, io.RawIOBase)
            self.assertIsInstance(p.stderr, io.RawIOBase)
        mwishowe:
            p.stdin.close()
            p.stdout.close()
            p.stderr.close()
            p.wait()

    eleza test_call_seq(self):
        # call() function ukijumuisha sequence argument
        rc = subprocess.call([sys.executable, "-c",
                              "agiza sys; sys.exit(47)"])
        self.assertEqual(rc, 47)

    eleza test_call_timeout(self):
        # call() function ukijumuisha timeout argument; we want to test that the child
        # process gets killed when the timeout expires.  If the child isn't
        # killed, this call will deadlock since subprocess.call waits kila the
        # child.
        self.assertRaises(subprocess.TimeoutExpired, subprocess.call,
                          [sys.executable, "-c", "wakati Kweli: pita"],
                          timeout=0.1)

    eleza test_check_call_zero(self):
        # check_call() function ukijumuisha zero rudisha code
        rc = subprocess.check_call([sys.executable, "-c",
                                    "agiza sys; sys.exit(0)"])
        self.assertEqual(rc, 0)

    eleza test_check_call_nonzero(self):
        # check_call() function ukijumuisha non-zero rudisha code
        ukijumuisha self.assertRaises(subprocess.CalledProcessError) kama c:
            subprocess.check_call([sys.executable, "-c",
                                   "agiza sys; sys.exit(47)"])
        self.assertEqual(c.exception.returncode, 47)

    eleza test_check_output(self):
        # check_output() function ukijumuisha zero rudisha code
        output = subprocess.check_output(
                [sys.executable, "-c", "andika('BDFL')"])
        self.assertIn(b'BDFL', output)

    eleza test_check_output_nonzero(self):
        # check_call() function ukijumuisha non-zero rudisha code
        ukijumuisha self.assertRaises(subprocess.CalledProcessError) kama c:
            subprocess.check_output(
                    [sys.executable, "-c", "agiza sys; sys.exit(5)"])
        self.assertEqual(c.exception.returncode, 5)

    eleza test_check_output_stderr(self):
        # check_output() function stderr redirected to stdout
        output = subprocess.check_output(
                [sys.executable, "-c", "agiza sys; sys.stderr.write('BDFL')"],
                stderr=subprocess.STDOUT)
        self.assertIn(b'BDFL', output)

    eleza test_check_output_stdin_arg(self):
        # check_output() can be called ukijumuisha stdin set to a file
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b'pear')
        tf.seek(0)
        output = subprocess.check_output(
                [sys.executable, "-c",
                 "agiza sys; sys.stdout.write(sys.stdin.read().upper())"],
                stdin=tf)
        self.assertIn(b'PEAR', output)

    eleza test_check_output_input_arg(self):
        # check_output() can be called ukijumuisha input set to a string
        output = subprocess.check_output(
                [sys.executable, "-c",
                 "agiza sys; sys.stdout.write(sys.stdin.read().upper())"],
                input=b'pear')
        self.assertIn(b'PEAR', output)

    eleza test_check_output_stdout_arg(self):
        # check_output() refuses to accept 'stdout' argument
        ukijumuisha self.assertRaises(ValueError) kama c:
            output = subprocess.check_output(
                    [sys.executable, "-c", "andika('will sio be run')"],
                    stdout=sys.stdout)
            self.fail("Expected ValueError when stdout arg supplied.")
        self.assertIn('stdout', c.exception.args[0])

    eleza test_check_output_stdin_with_input_arg(self):
        # check_output() refuses to accept 'stdin' ukijumuisha 'input'
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b'pear')
        tf.seek(0)
        ukijumuisha self.assertRaises(ValueError) kama c:
            output = subprocess.check_output(
                    [sys.executable, "-c", "andika('will sio be run')"],
                    stdin=tf, input=b'hare')
            self.fail("Expected ValueError when stdin na input args supplied.")
        self.assertIn('stdin', c.exception.args[0])
        self.assertIn('input', c.exception.args[0])

    eleza test_check_output_timeout(self):
        # check_output() function ukijumuisha timeout arg
        ukijumuisha self.assertRaises(subprocess.TimeoutExpired) kama c:
            output = subprocess.check_output(
                    [sys.executable, "-c",
                     "agiza sys, time\n"
                     "sys.stdout.write('BDFL')\n"
                     "sys.stdout.flush()\n"
                     "time.sleep(3600)"],
                    # Some heavily loaded buildbots (sparc Debian 3.x) require
                    # this much time to start na print.
                    timeout=3)
            self.fail("Expected TimeoutExpired.")
        self.assertEqual(c.exception.output, b'BDFL')

    eleza test_call_kwargs(self):
        # call() function ukijumuisha keyword args
        newenv = os.environ.copy()
        newenv["FRUIT"] = "banana"
        rc = subprocess.call([sys.executable, "-c",
                              'agiza sys, os;'
                              'sys.exit(os.getenv("FRUIT")=="banana")'],
                             env=newenv)
        self.assertEqual(rc, 1)

    eleza test_invalid_args(self):
        # Popen() called ukijumuisha invalid arguments should ashiria TypeError
        # but Popen.__del__ should sio complain (issue #12085)
        ukijumuisha support.captured_stderr() kama s:
            self.assertRaises(TypeError, subprocess.Popen, invalid_arg_name=1)
            argcount = subprocess.Popen.__init__.__code__.co_argcount
            too_many_args = [0] * (argcount + 1)
            self.assertRaises(TypeError, subprocess.Popen, *too_many_args)
        self.assertEqual(s.getvalue(), '')

    eleza test_stdin_none(self):
        # .stdin ni Tupu when sio redirected
        p = subprocess.Popen([sys.executable, "-c", 'andika("banana")'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        p.wait()
        self.assertEqual(p.stdin, Tupu)

    eleza test_stdout_none(self):
        # .stdout ni Tupu when sio redirected, na the child's stdout will
        # be inherited kutoka the parent.  In order to test this we run a
        # subprocess kwenye a subprocess:
        # this_test
        #   \-- subprocess created by this test (parent)
        #          \-- subprocess created by the parent subprocess (child)
        # The parent doesn't specify stdout, so the child will use the
        # parent's stdout.  This test checks that the message printed by the
        # child goes to the parent stdout.  The parent also checks that the
        # child's stdout ni Tupu.  See #11963.
        code = ('agiza sys; kutoka subprocess agiza Popen, PIPE;'
                'p = Popen([sys.executable, "-c", "andika(\'test_stdout_none\')"],'
                '          stdin=PIPE, stderr=PIPE);'
                'p.wait(); assert p.stdout ni Tupu;')
        p = subprocess.Popen([sys.executable, "-c", code],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0, err)
        self.assertEqual(out.rstrip(), b'test_stdout_none')

    eleza test_stderr_none(self):
        # .stderr ni Tupu when sio redirected
        p = subprocess.Popen([sys.executable, "-c", 'andika("banana")'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stdin.close)
        p.wait()
        self.assertEqual(p.stderr, Tupu)

    eleza _assert_python(self, pre_args, **kwargs):
        # We include sys.exit() to prevent the test runner kutoka hanging
        # whenever python ni found.
        args = pre_args + ["agiza sys; sys.exit(47)"]
        p = subprocess.Popen(args, **kwargs)
        p.wait()
        self.assertEqual(47, p.returncode)

    eleza test_executable(self):
        # Check that the executable argument works.
        #
        # On Unix (non-Mac na non-Windows), Python looks at args[0] to
        # determine where its standard library is, so we need the directory
        # of args[0] to be valid kila the Popen() call to Python to succeed.
        # See also issue #16170 na issue #7774.
        doesnotexist = os.path.join(os.path.dirname(sys.executable),
                                    "doesnotexist")
        self._assert_python([doesnotexist, "-c"], executable=sys.executable)

    eleza test_bytes_executable(self):
        doesnotexist = os.path.join(os.path.dirname(sys.executable),
                                    "doesnotexist")
        self._assert_python([doesnotexist, "-c"],
                            executable=os.fsencode(sys.executable))

    eleza test_pathlike_executable(self):
        doesnotexist = os.path.join(os.path.dirname(sys.executable),
                                    "doesnotexist")
        self._assert_python([doesnotexist, "-c"],
                            executable=FakePath(sys.executable))

    eleza test_executable_takes_precedence(self):
        # Check that the executable argument takes precedence over args[0].
        #
        # Verify first that the call succeeds without the executable arg.
        pre_args = [sys.executable, "-c"]
        self._assert_python(pre_args)
        self.assertRaises(NONEXISTING_ERRORS,
                          self._assert_python, pre_args,
                          executable=NONEXISTING_CMD[0])

    @unittest.skipIf(mswindows, "executable argument replaces shell")
    eleza test_executable_replaces_shell(self):
        # Check that the executable argument replaces the default shell
        # when shell=Kweli.
        self._assert_python([], executable=sys.executable, shell=Kweli)

    @unittest.skipIf(mswindows, "executable argument replaces shell")
    eleza test_bytes_executable_replaces_shell(self):
        self._assert_python([], executable=os.fsencode(sys.executable),
                            shell=Kweli)

    @unittest.skipIf(mswindows, "executable argument replaces shell")
    eleza test_pathlike_executable_replaces_shell(self):
        self._assert_python([], executable=FakePath(sys.executable),
                            shell=Kweli)

    # For use kwenye the test_cwd* tests below.
    eleza _normalize_cwd(self, cwd):
        # Normalize an expected cwd (kila Tru64 support).
        # We can't use os.path.realpath since it doesn't expand Tru64 {memb}
        # strings.  See bug #1063571.
        ukijumuisha support.change_cwd(cwd):
            rudisha os.getcwd()

    # For use kwenye the test_cwd* tests below.
    eleza _split_python_path(self):
        # Return normalized (python_dir, python_base).
        python_path = os.path.realpath(sys.executable)
        rudisha os.path.split(python_path)

    # For use kwenye the test_cwd* tests below.
    eleza _assert_cwd(self, expected_cwd, python_arg, **kwargs):
        # Invoke Python via Popen, na assert that (1) the call succeeds,
        # na that (2) the current working directory of the child process
        # matches *expected_cwd*.
        p = subprocess.Popen([python_arg, "-c",
                              "agiza os, sys; "
                              "sys.stdout.write(os.getcwd()); "
                              "sys.exit(47)"],
                              stdout=subprocess.PIPE,
                              **kwargs)
        self.addCleanup(p.stdout.close)
        p.wait()
        self.assertEqual(47, p.returncode)
        normcase = os.path.normcase
        self.assertEqual(normcase(expected_cwd),
                         normcase(p.stdout.read().decode("utf-8")))

    eleza test_cwd(self):
        # Check that cwd changes the cwd kila the child process.
        temp_dir = tempfile.gettempdir()
        temp_dir = self._normalize_cwd(temp_dir)
        self._assert_cwd(temp_dir, sys.executable, cwd=temp_dir)

    eleza test_cwd_with_bytes(self):
        temp_dir = tempfile.gettempdir()
        temp_dir = self._normalize_cwd(temp_dir)
        self._assert_cwd(temp_dir, sys.executable, cwd=os.fsencode(temp_dir))

    eleza test_cwd_with_pathlike(self):
        temp_dir = tempfile.gettempdir()
        temp_dir = self._normalize_cwd(temp_dir)
        self._assert_cwd(temp_dir, sys.executable, cwd=FakePath(temp_dir))

    @unittest.skipIf(mswindows, "pending resolution of issue #15533")
    eleza test_cwd_with_relative_arg(self):
        # Check that Popen looks kila args[0] relative to cwd ikiwa args[0]
        # ni relative.
        python_dir, python_base = self._split_python_path()
        rel_python = os.path.join(os.curdir, python_base)
        ukijumuisha support.temp_cwd() kama wrong_dir:
            # Before calling ukijumuisha the correct cwd, confirm that the call fails
            # without cwd na ukijumuisha the wrong cwd.
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [rel_python])
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [rel_python], cwd=wrong_dir)
            python_dir = self._normalize_cwd(python_dir)
            self._assert_cwd(python_dir, rel_python, cwd=python_dir)

    @unittest.skipIf(mswindows, "pending resolution of issue #15533")
    eleza test_cwd_with_relative_executable(self):
        # Check that Popen looks kila executable relative to cwd ikiwa executable
        # ni relative (and that executable takes precedence over args[0]).
        python_dir, python_base = self._split_python_path()
        rel_python = os.path.join(os.curdir, python_base)
        doesntexist = "somethingyoudonthave"
        ukijumuisha support.temp_cwd() kama wrong_dir:
            # Before calling ukijumuisha the correct cwd, confirm that the call fails
            # without cwd na ukijumuisha the wrong cwd.
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [doesntexist], executable=rel_python)
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [doesntexist], executable=rel_python,
                              cwd=wrong_dir)
            python_dir = self._normalize_cwd(python_dir)
            self._assert_cwd(python_dir, doesntexist, executable=rel_python,
                             cwd=python_dir)

    eleza test_cwd_with_absolute_arg(self):
        # Check that Popen can find the executable when the cwd ni wrong
        # ikiwa args[0] ni an absolute path.
        python_dir, python_base = self._split_python_path()
        abs_python = os.path.join(python_dir, python_base)
        rel_python = os.path.join(os.curdir, python_base)
        ukijumuisha support.temp_dir() kama wrong_dir:
            # Before calling ukijumuisha an absolute path, confirm that using a
            # relative path fails.
            self.assertRaises(FileNotFoundError, subprocess.Popen,
                              [rel_python], cwd=wrong_dir)
            wrong_dir = self._normalize_cwd(wrong_dir)
            self._assert_cwd(wrong_dir, abs_python, cwd=wrong_dir)

    @unittest.skipIf(sys.base_prefix != sys.prefix,
                     'Test ni sio venv-compatible')
    eleza test_executable_with_cwd(self):
        python_dir, python_base = self._split_python_path()
        python_dir = self._normalize_cwd(python_dir)
        self._assert_cwd(python_dir, "somethingyoudonthave",
                         executable=sys.executable, cwd=python_dir)

    @unittest.skipIf(sys.base_prefix != sys.prefix,
                     'Test ni sio venv-compatible')
    @unittest.skipIf(sysconfig.is_python_build(),
                     "need an installed Python. See #7774")
    eleza test_executable_without_cwd(self):
        # For a normal installation, it should work without 'cwd'
        # argument.  For test runs kwenye the build directory, see #7774.
        self._assert_cwd(os.getcwd(), "somethingyoudonthave",
                         executable=sys.executable)

    eleza test_stdin_pipe(self):
        # stdin redirection
        p = subprocess.Popen([sys.executable, "-c",
                         'agiza sys; sys.exit(sys.stdin.read() == "pear")'],
                        stdin=subprocess.PIPE)
        p.stdin.write(b"pear")
        p.stdin.close()
        p.wait()
        self.assertEqual(p.returncode, 1)

    eleza test_stdin_filedes(self):
        # stdin ni set to open file descriptor
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        d = tf.fileno()
        os.write(d, b"pear")
        os.lseek(d, 0, 0)
        p = subprocess.Popen([sys.executable, "-c",
                         'agiza sys; sys.exit(sys.stdin.read() == "pear")'],
                         stdin=d)
        p.wait()
        self.assertEqual(p.returncode, 1)

    eleza test_stdin_fileobj(self):
        # stdin ni set to open file object
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b"pear")
        tf.seek(0)
        p = subprocess.Popen([sys.executable, "-c",
                         'agiza sys; sys.exit(sys.stdin.read() == "pear")'],
                         stdin=tf)
        p.wait()
        self.assertEqual(p.returncode, 1)

    eleza test_stdout_pipe(self):
        # stdout redirection
        p = subprocess.Popen([sys.executable, "-c",
                          'agiza sys; sys.stdout.write("orange")'],
                         stdout=subprocess.PIPE)
        ukijumuisha p:
            self.assertEqual(p.stdout.read(), b"orange")

    eleza test_stdout_filedes(self):
        # stdout ni set to open file descriptor
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        d = tf.fileno()
        p = subprocess.Popen([sys.executable, "-c",
                          'agiza sys; sys.stdout.write("orange")'],
                         stdout=d)
        p.wait()
        os.lseek(d, 0, 0)
        self.assertEqual(os.read(d, 1024), b"orange")

    eleza test_stdout_fileobj(self):
        # stdout ni set to open file object
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        p = subprocess.Popen([sys.executable, "-c",
                          'agiza sys; sys.stdout.write("orange")'],
                         stdout=tf)
        p.wait()
        tf.seek(0)
        self.assertEqual(tf.read(), b"orange")

    eleza test_stderr_pipe(self):
        # stderr redirection
        p = subprocess.Popen([sys.executable, "-c",
                          'agiza sys; sys.stderr.write("strawberry")'],
                         stderr=subprocess.PIPE)
        ukijumuisha p:
            self.assertStderrEqual(p.stderr.read(), b"strawberry")

    eleza test_stderr_filedes(self):
        # stderr ni set to open file descriptor
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        d = tf.fileno()
        p = subprocess.Popen([sys.executable, "-c",
                          'agiza sys; sys.stderr.write("strawberry")'],
                         stderr=d)
        p.wait()
        os.lseek(d, 0, 0)
        self.assertStderrEqual(os.read(d, 1024), b"strawberry")

    eleza test_stderr_fileobj(self):
        # stderr ni set to open file object
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        p = subprocess.Popen([sys.executable, "-c",
                          'agiza sys; sys.stderr.write("strawberry")'],
                         stderr=tf)
        p.wait()
        tf.seek(0)
        self.assertStderrEqual(tf.read(), b"strawberry")

    eleza test_stderr_redirect_with_no_stdout_redirect(self):
        # test stderr=STDOUT wakati stdout=Tupu (sio set)

        # - grandchild prints to stderr
        # - child redirects grandchild's stderr to its stdout
        # - the parent should get grandchild's stderr kwenye child's stdout
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys, subprocess;'
                              'rc = subprocess.call([sys.executable, "-c",'
                              '    "agiza sys;"'
                              '    "sys.stderr.write(\'42\')"],'
                              '    stderr=subprocess.STDOUT);'
                              'sys.exit(rc)'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        #NOTE: stdout should get stderr kutoka grandchild
        self.assertStderrEqual(stdout, b'42')
        self.assertStderrEqual(stderr, b'') # should be empty
        self.assertEqual(p.returncode, 0)

    eleza test_stdout_stderr_pipe(self):
        # capture stdout na stderr to the same pipe
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys;'
                              'sys.stdout.write("apple");'
                              'sys.stdout.flush();'
                              'sys.stderr.write("orange")'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        ukijumuisha p:
            self.assertStderrEqual(p.stdout.read(), b"appleorange")

    eleza test_stdout_stderr_file(self):
        # capture stdout na stderr to the same open file
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys;'
                              'sys.stdout.write("apple");'
                              'sys.stdout.flush();'
                              'sys.stderr.write("orange")'],
                             stdout=tf,
                             stderr=tf)
        p.wait()
        tf.seek(0)
        self.assertStderrEqual(tf.read(), b"appleorange")

    eleza test_stdout_filedes_of_stdout(self):
        # stdout ni set to 1 (#1531862).
        # To avoid printing the text on stdout, we do something similar to
        # test_stdout_none (see above).  The parent subprocess calls the child
        # subprocess pitaing stdout=1, na this test uses stdout=PIPE kwenye
        # order to capture na check the output of the parent. See #11963.
        code = ('agiza sys, subprocess; '
                'rc = subprocess.call([sys.executable, "-c", '
                '    "agiza os, sys; sys.exit(os.write(sys.stdout.fileno(), '
                     'b\'test ukijumuisha stdout=1\'))"], stdout=1); '
                'assert rc == 18')
        p = subprocess.Popen([sys.executable, "-c", code],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        out, err = p.communicate()
        self.assertEqual(p.returncode, 0, err)
        self.assertEqual(out.rstrip(), b'test ukijumuisha stdout=1')

    eleza test_stdout_devnull(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'kila i kwenye range(10240):'
                              'andika("x" * 1024)'],
                              stdout=subprocess.DEVNULL)
        p.wait()
        self.assertEqual(p.stdout, Tupu)

    eleza test_stderr_devnull(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys\n'
                              'kila i kwenye range(10240):'
                              'sys.stderr.write("x" * 1024)'],
                              stderr=subprocess.DEVNULL)
        p.wait()
        self.assertEqual(p.stderr, Tupu)

    eleza test_stdin_devnull(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys;'
                              'sys.stdin.read(1)'],
                              stdin=subprocess.DEVNULL)
        p.wait()
        self.assertEqual(p.stdin, Tupu)

    eleza test_env(self):
        newenv = os.environ.copy()
        newenv["FRUIT"] = "orange"
        ukijumuisha subprocess.Popen([sys.executable, "-c",
                               'agiza sys,os;'
                               'sys.stdout.write(os.getenv("FRUIT"))'],
                              stdout=subprocess.PIPE,
                              env=newenv) kama p:
            stdout, stderr = p.communicate()
            self.assertEqual(stdout, b"orange")

    # Windows requires at least the SYSTEMROOT environment variable to start
    # Python
    @unittest.skipIf(sys.platform == 'win32',
                     'cannot test an empty env on Windows')
    @unittest.skipIf(sysconfig.get_config_var('Py_ENABLE_SHARED') == 1,
                     'The Python shared library cannot be loaded '
                     'ukijumuisha an empty environment.')
    eleza test_empty_env(self):
        """Verify that env={} ni kama empty kama possible."""

        eleza is_env_var_to_ignore(n):
            """Determine ikiwa an environment variable ni under our control."""
            # This excludes some __CF_* na VERSIONER_* keys MacOS insists
            # on adding even when the environment kwenye exec ni empty.
            # Gentoo sandboxes also force LD_PRELOAD na SANDBOX_* to exist.
            rudisha ('VERSIONER' kwenye n ama '__CF' kwenye n ama  # MacOS
                    '__PYVENV_LAUNCHER__' kwenye n ama # MacOS framework build
                    n == 'LD_PRELOAD' ama n.startswith('SANDBOX') ama # Gentoo
                    n == 'LC_CTYPE') # Locale coercion triggered

        ukijumuisha subprocess.Popen([sys.executable, "-c",
                               'agiza os; andika(list(os.environ.keys()))'],
                              stdout=subprocess.PIPE, env={}) kama p:
            stdout, stderr = p.communicate()
            child_env_names = eval(stdout.strip())
            self.assertIsInstance(child_env_names, list)
            child_env_names = [k kila k kwenye child_env_names
                               ikiwa sio is_env_var_to_ignore(k)]
            self.assertEqual(child_env_names, [])

    eleza test_invalid_cmd(self):
        # null character kwenye the command name
        cmd = sys.executable + '\0'
        ukijumuisha self.assertRaises(ValueError):
            subprocess.Popen([cmd, "-c", "pita"])

        # null character kwenye the command argument
        ukijumuisha self.assertRaises(ValueError):
            subprocess.Popen([sys.executable, "-c", "pita#\0"])

    eleza test_invalid_env(self):
        # null character kwenye the environment variable name
        newenv = os.environ.copy()
        newenv["FRUIT\0VEGETABLE"] = "cabbage"
        ukijumuisha self.assertRaises(ValueError):
            subprocess.Popen([sys.executable, "-c", "pita"], env=newenv)

        # null character kwenye the environment variable value
        newenv = os.environ.copy()
        newenv["FRUIT"] = "orange\0VEGETABLE=cabbage"
        ukijumuisha self.assertRaises(ValueError):
            subprocess.Popen([sys.executable, "-c", "pita"], env=newenv)

        # equal character kwenye the environment variable name
        newenv = os.environ.copy()
        newenv["FRUIT=ORANGE"] = "lemon"
        ukijumuisha self.assertRaises(ValueError):
            subprocess.Popen([sys.executable, "-c", "pita"], env=newenv)

        # equal character kwenye the environment variable value
        newenv = os.environ.copy()
        newenv["FRUIT"] = "orange=lemon"
        ukijumuisha subprocess.Popen([sys.executable, "-c",
                               'agiza sys, os;'
                               'sys.stdout.write(os.getenv("FRUIT"))'],
                              stdout=subprocess.PIPE,
                              env=newenv) kama p:
            stdout, stderr = p.communicate()
            self.assertEqual(stdout, b"orange=lemon")

    eleza test_communicate_stdin(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys;'
                              'sys.exit(sys.stdin.read() == "pear")'],
                             stdin=subprocess.PIPE)
        p.communicate(b"pear")
        self.assertEqual(p.returncode, 1)

    eleza test_communicate_stdout(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys; sys.stdout.write("pineapple")'],
                             stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, b"pineapple")
        self.assertEqual(stderr, Tupu)

    eleza test_communicate_stderr(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys; sys.stderr.write("pineapple")'],
                             stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, Tupu)
        self.assertStderrEqual(stderr, b"pineapple")

    eleza test_communicate(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os;'
                              'sys.stderr.write("pineapple");'
                              'sys.stdout.write(sys.stdin.read())'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        (stdout, stderr) = p.communicate(b"banana")
        self.assertEqual(stdout, b"banana")
        self.assertStderrEqual(stderr, b"pineapple")

    eleza test_communicate_timeout(self):
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os,time;'
                              'sys.stderr.write("pineapple\\n");'
                              'time.sleep(1);'
                              'sys.stderr.write("pear\\n");'
                              'sys.stdout.write(sys.stdin.read())'],
                             universal_newlines=Kweli,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.assertRaises(subprocess.TimeoutExpired, p.communicate, "banana",
                          timeout=0.3)
        # Make sure we can keep waiting kila it, na that we get the whole output
        # after it completes.
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, "banana")
        self.assertStderrEqual(stderr.encode(), b"pineapple\npear\n")

    eleza test_communicate_timeout_large_output(self):
        # Test an expiring timeout wakati the child ni outputting lots of data.
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os,time;'
                              'sys.stdout.write("a" * (64 * 1024));'
                              'time.sleep(0.2);'
                              'sys.stdout.write("a" * (64 * 1024));'
                              'time.sleep(0.2);'
                              'sys.stdout.write("a" * (64 * 1024));'
                              'time.sleep(0.2);'
                              'sys.stdout.write("a" * (64 * 1024));'],
                             stdout=subprocess.PIPE)
        self.assertRaises(subprocess.TimeoutExpired, p.communicate, timeout=0.4)
        (stdout, _) = p.communicate()
        self.assertEqual(len(stdout), 4 * 64 * 1024)

    # Test kila the fd leak reported kwenye http://bugs.python.org/issue2791.
    eleza test_communicate_pipe_fd_leak(self):
        kila stdin_pipe kwenye (Uongo, Kweli):
            kila stdout_pipe kwenye (Uongo, Kweli):
                kila stderr_pipe kwenye (Uongo, Kweli):
                    options = {}
                    ikiwa stdin_pipe:
                        options['stdin'] = subprocess.PIPE
                    ikiwa stdout_pipe:
                        options['stdout'] = subprocess.PIPE
                    ikiwa stderr_pipe:
                        options['stderr'] = subprocess.PIPE
                    ikiwa sio options:
                        endelea
                    p = subprocess.Popen((sys.executable, "-c", "pita"), **options)
                    p.communicate()
                    ikiwa p.stdin ni sio Tupu:
                        self.assertKweli(p.stdin.closed)
                    ikiwa p.stdout ni sio Tupu:
                        self.assertKweli(p.stdout.closed)
                    ikiwa p.stderr ni sio Tupu:
                        self.assertKweli(p.stderr.closed)

    eleza test_communicate_returns(self):
        # communicate() should rudisha Tupu ikiwa no redirection ni active
        p = subprocess.Popen([sys.executable, "-c",
                              "agiza sys; sys.exit(47)"])
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout, Tupu)
        self.assertEqual(stderr, Tupu)

    eleza test_communicate_pipe_buf(self):
        # communicate() ukijumuisha writes larger than pipe_buf
        # This test will probably deadlock rather than fail, if
        # communicate() does sio work properly.
        x, y = os.pipe()
        os.close(x)
        os.close(y)
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os;'
                              'sys.stdout.write(sys.stdin.read(47));'
                              'sys.stderr.write("x" * %d);'
                              'sys.stdout.write(sys.stdin.read())' %
                              support.PIPE_MAX_SIZE],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        string_to_write = b"a" * support.PIPE_MAX_SIZE
        (stdout, stderr) = p.communicate(string_to_write)
        self.assertEqual(stdout, string_to_write)

    eleza test_writes_before_communicate(self):
        # stdin.write before communicate()
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os;'
                              'sys.stdout.write(sys.stdin.read())'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        p.stdin.write(b"banana")
        (stdout, stderr) = p.communicate(b"split")
        self.assertEqual(stdout, b"bananasplit")
        self.assertStderrEqual(stderr, b"")

    eleza test_universal_newlines_and_text(self):
        args = [
            sys.executable, "-c",
            'agiza sys,os;' + SETBINARY +
            'buf = sys.stdout.buffer;'
            'buf.write(sys.stdin.readline().encode());'
            'buf.flush();'
            'buf.write(b"line2\\n");'
            'buf.flush();'
            'buf.write(sys.stdin.read().encode());'
            'buf.flush();'
            'buf.write(b"line4\\n");'
            'buf.flush();'
            'buf.write(b"line5\\r\\n");'
            'buf.flush();'
            'buf.write(b"line6\\r");'
            'buf.flush();'
            'buf.write(b"\\nline7");'
            'buf.flush();'
            'buf.write(b"\\nline8");']

        kila extra_kwarg kwenye ('universal_newlines', 'text'):
            p = subprocess.Popen(args, **{'stdin': subprocess.PIPE,
                                          'stdout': subprocess.PIPE,
                                          extra_kwarg: Kweli})
            ukijumuisha p:
                p.stdin.write("line1\n")
                p.stdin.flush()
                self.assertEqual(p.stdout.readline(), "line1\n")
                p.stdin.write("line3\n")
                p.stdin.close()
                self.addCleanup(p.stdout.close)
                self.assertEqual(p.stdout.readline(),
                                 "line2\n")
                self.assertEqual(p.stdout.read(6),
                                 "line3\n")
                self.assertEqual(p.stdout.read(),
                                 "line4\nline5\nline6\nline7\nline8")

    eleza test_universal_newlines_communicate(self):
        # universal newlines through communicate()
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os;' + SETBINARY +
                              'buf = sys.stdout.buffer;'
                              'buf.write(b"line2\\n");'
                              'buf.flush();'
                              'buf.write(b"line4\\n");'
                              'buf.flush();'
                              'buf.write(b"line5\\r\\n");'
                              'buf.flush();'
                              'buf.write(b"line6\\r");'
                              'buf.flush();'
                              'buf.write(b"\\nline7");'
                              'buf.flush();'
                              'buf.write(b"\\nline8");'],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=1)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        (stdout, stderr) = p.communicate()
        self.assertEqual(stdout,
                         "line2\nline4\nline5\nline6\nline7\nline8")

    eleza test_universal_newlines_communicate_stdin(self):
        # universal newlines through communicate(), ukijumuisha only stdin
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os;' + SETBINARY + textwrap.dedent('''
                               s = sys.stdin.readline()
                               assert s == "line1\\n", repr(s)
                               s = sys.stdin.read()
                               assert s == "line3\\n", repr(s)
                              ''')],
                             stdin=subprocess.PIPE,
                             universal_newlines=1)
        (stdout, stderr) = p.communicate("line1\nline3\n")
        self.assertEqual(p.returncode, 0)

    eleza test_universal_newlines_communicate_input_none(self):
        # Test communicate(input=Tupu) ukijumuisha universal newlines.
        #
        # We set stdout to PIPE because, kama of this writing, a different
        # code path ni tested when the number of pipes ni zero ama one.
        p = subprocess.Popen([sys.executable, "-c", "pita"],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=Kweli)
        p.communicate()
        self.assertEqual(p.returncode, 0)

    eleza test_universal_newlines_communicate_stdin_stdout_stderr(self):
        # universal newlines through communicate(), ukijumuisha stdin, stdout, stderr
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os;' + SETBINARY + textwrap.dedent('''
                               s = sys.stdin.buffer.readline()
                               sys.stdout.buffer.write(s)
                               sys.stdout.buffer.write(b"line2\\r")
                               sys.stderr.buffer.write(b"eline2\\n")
                               s = sys.stdin.buffer.read()
                               sys.stdout.buffer.write(s)
                               sys.stdout.buffer.write(b"line4\\n")
                               sys.stdout.buffer.write(b"line5\\r\\n")
                               sys.stderr.buffer.write(b"eline6\\r")
                               sys.stderr.buffer.write(b"eline7\\r\\nz")
                              ''')],
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=Kweli)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        (stdout, stderr) = p.communicate("line1\nline3\n")
        self.assertEqual(p.returncode, 0)
        self.assertEqual("line1\nline2\nline3\nline4\nline5\n", stdout)
        # Python debug build push something like "[42442 refs]\n"
        # to stderr at exit of subprocess.
        # Don't use assertStderrEqual because it strips CR na LF kutoka output.
        self.assertKweli(stderr.startswith("eline2\neline6\neline7\n"))

    eleza test_universal_newlines_communicate_encodings(self):
        # Check that universal newlines mode works kila various encodings,
        # kwenye particular kila encodings kwenye the UTF-16 na UTF-32 families.
        # See issue #15595.
        #
        # UTF-16 na UTF-32-BE are sufficient to check both ukijumuisha BOM na
        # without, na UTF-16 na UTF-32.
        kila encoding kwenye ['utf-16', 'utf-32-be']:
            code = ("agiza sys; "
                    r"sys.stdout.buffer.write('1\r\n2\r3\n4'.encode('%s'))" %
                    encoding)
            args = [sys.executable, '-c', code]
            # We set stdin to be non-Tupu because, kama of this writing,
            # a different code path ni used when the number of pipes is
            # zero ama one.
            popen = subprocess.Popen(args,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     encoding=encoding)
            stdout, stderr = popen.communicate(input='')
            self.assertEqual(stdout, '1\n2\n3\n4')

    eleza test_communicate_errors(self):
        kila errors, expected kwenye [
            ('ignore', ''),
            ('replace', '\ufffd\ufffd'),
            ('surrogateescape', '\udc80\udc80'),
            ('backslashreplace', '\\x80\\x80'),
        ]:
            code = ("agiza sys; "
                    r"sys.stdout.buffer.write(b'[\x80\x80]')")
            args = [sys.executable, '-c', code]
            # We set stdin to be non-Tupu because, kama of this writing,
            # a different code path ni used when the number of pipes is
            # zero ama one.
            popen = subprocess.Popen(args,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     encoding='utf-8',
                                     errors=errors)
            stdout, stderr = popen.communicate(input='')
            self.assertEqual(stdout, '[{}]'.format(expected))

    eleza test_no_leaking(self):
        # Make sure we leak no resources
        ikiwa sio mswindows:
            max_handles = 1026 # too much kila most UNIX systems
        isipokua:
            max_handles = 2050 # too much kila (at least some) Windows setups
        handles = []
        tmpdir = tempfile.mkdtemp()
        jaribu:
            kila i kwenye range(max_handles):
                jaribu:
                    tmpfile = os.path.join(tmpdir, support.TESTFN)
                    handles.append(os.open(tmpfile, os.O_WRONLY|os.O_CREAT))
                tatizo OSError kama e:
                    ikiwa e.errno != errno.EMFILE:
                        raise
                    koma
            isipokua:
                self.skipTest("failed to reach the file descriptor limit "
                    "(tried %d)" % max_handles)
            # Close a couple of them (should be enough kila a subprocess)
            kila i kwenye range(10):
                os.close(handles.pop())
            # Loop creating some subprocesses. If one of them leaks some fds,
            # the next loop iteration will fail by reaching the max fd limit.
            kila i kwenye range(15):
                p = subprocess.Popen([sys.executable, "-c",
                                      "agiza sys;"
                                      "sys.stdout.write(sys.stdin.read())"],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                data = p.communicate(b"lime")[0]
                self.assertEqual(data, b"lime")
        mwishowe:
            kila h kwenye handles:
                os.close(h)
            shutil.rmtree(tmpdir)

    eleza test_list2cmdline(self):
        self.assertEqual(subprocess.list2cmdline(['a b c', 'd', 'e']),
                         '"a b c" d e')
        self.assertEqual(subprocess.list2cmdline(['ab"c', '\\', 'd']),
                         'ab\\"c \\ d')
        self.assertEqual(subprocess.list2cmdline(['ab"c', ' \\', 'd']),
                         'ab\\"c " \\\\" d')
        self.assertEqual(subprocess.list2cmdline(['a\\\\\\b', 'de fg', 'h']),
                         'a\\\\\\b "de fg" h')
        self.assertEqual(subprocess.list2cmdline(['a\\"b', 'c', 'd']),
                         'a\\\\\\"b c d')
        self.assertEqual(subprocess.list2cmdline(['a\\\\b c', 'd', 'e']),
                         '"a\\\\b c" d e')
        self.assertEqual(subprocess.list2cmdline(['a\\\\b\\ c', 'd', 'e']),
                         '"a\\\\b\\ c" d e')
        self.assertEqual(subprocess.list2cmdline(['ab', '']),
                         'ab ""')

    eleza test_poll(self):
        p = subprocess.Popen([sys.executable, "-c",
                              "agiza os; os.read(0, 1)"],
                             stdin=subprocess.PIPE)
        self.addCleanup(p.stdin.close)
        self.assertIsTupu(p.poll())
        os.write(p.stdin.fileno(), b'A')
        p.wait()
        # Subsequent invocations should just rudisha the returncode
        self.assertEqual(p.poll(), 0)

    eleza test_wait(self):
        p = subprocess.Popen([sys.executable, "-c", "pita"])
        self.assertEqual(p.wait(), 0)
        # Subsequent invocations should just rudisha the returncode
        self.assertEqual(p.wait(), 0)

    eleza test_wait_timeout(self):
        p = subprocess.Popen([sys.executable,
                              "-c", "agiza time; time.sleep(0.3)"])
        ukijumuisha self.assertRaises(subprocess.TimeoutExpired) kama c:
            p.wait(timeout=0.0001)
        self.assertIn("0.0001", str(c.exception))  # For coverage of __str__.
        # Some heavily loaded buildbots (sparc Debian 3.x) require this much
        # time to start.
        self.assertEqual(p.wait(timeout=3), 0)

    eleza test_invalid_bufsize(self):
        # an invalid type of the bufsize argument should raise
        # TypeError.
        ukijumuisha self.assertRaises(TypeError):
            subprocess.Popen([sys.executable, "-c", "pita"], "orange")

    eleza test_bufsize_is_none(self):
        # bufsize=Tupu should be the same kama bufsize=0.
        p = subprocess.Popen([sys.executable, "-c", "pita"], Tupu)
        self.assertEqual(p.wait(), 0)
        # Again ukijumuisha keyword arg
        p = subprocess.Popen([sys.executable, "-c", "pita"], bufsize=Tupu)
        self.assertEqual(p.wait(), 0)

    eleza _test_bufsize_equal_one(self, line, expected, universal_newlines):
        # subprocess may deadlock ukijumuisha bufsize=1, see issue #21332
        ukijumuisha subprocess.Popen([sys.executable, "-c", "agiza sys;"
                               "sys.stdout.write(sys.stdin.readline());"
                               "sys.stdout.flush()"],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,
                              bufsize=1,
                              universal_newlines=universal_newlines) kama p:
            p.stdin.write(line) # expect that it flushes the line kwenye text mode
            os.close(p.stdin.fileno()) # close it without flushing the buffer
            read_line = p.stdout.readline()
            ukijumuisha support.SuppressCrashReport():
                jaribu:
                    p.stdin.close()
                tatizo OSError:
                    pita
            p.stdin = Tupu
        self.assertEqual(p.returncode, 0)
        self.assertEqual(read_line, expected)

    eleza test_bufsize_equal_one_text_mode(self):
        # line ni flushed kwenye text mode ukijumuisha bufsize=1.
        # we should get the full line kwenye rudisha
        line = "line\n"
        self._test_bufsize_equal_one(line, line, universal_newlines=Kweli)

    eleza test_bufsize_equal_one_binary_mode(self):
        # line ni sio flushed kwenye binary mode ukijumuisha bufsize=1.
        # we should get empty response
        line = b'line' + os.linesep.encode() # assume ascii-based locale
        ukijumuisha self.assertWarnsRegex(RuntimeWarning, 'line buffering'):
            self._test_bufsize_equal_one(line, b'', universal_newlines=Uongo)

    eleza test_leaking_fds_on_error(self):
        # see bug #5179: Popen leaks file descriptors to PIPEs if
        # the child fails to execute; this will eventually exhaust
        # the maximum number of open fds. 1024 seems a very common
        # value kila that limit, but Windows has 2048, so we loop
        # 1024 times (each call leaked two fds).
        kila i kwenye range(1024):
            ukijumuisha self.assertRaises(NONEXISTING_ERRORS):
                subprocess.Popen(NONEXISTING_CMD,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

    eleza test_nonexisting_with_pipes(self):
        # bpo-30121: Popen ukijumuisha pipes must close properly pipes on error.
        # Previously, os.close() was called ukijumuisha a Windows handle which ni sio
        # a valid file descriptor.
        #
        # Run the test kwenye a subprocess to control how the CRT reports errors
        # na to get stderr content.
        jaribu:
            agiza msvcrt
            msvcrt.CrtSetReportMode
        tatizo (AttributeError, ImportError):
            self.skipTest("need msvcrt.CrtSetReportMode")

        code = textwrap.dedent(f"""
            agiza msvcrt
            agiza subprocess

            cmd = {NONEXISTING_CMD!r}

            kila report_type kwenye [msvcrt.CRT_WARN,
                                msvcrt.CRT_ERROR,
                                msvcrt.CRT_ASSERT]:
                msvcrt.CrtSetReportMode(report_type, msvcrt.CRTDBG_MODE_FILE)
                msvcrt.CrtSetReportFile(report_type, msvcrt.CRTDBG_FILE_STDERR)

            jaribu:
                subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            tatizo OSError:
                pita
        """)
        cmd = [sys.executable, "-c", code]
        proc = subprocess.Popen(cmd,
                                stderr=subprocess.PIPE,
                                universal_newlines=Kweli)
        ukijumuisha proc:
            stderr = proc.communicate()[1]
        self.assertEqual(stderr, "")
        self.assertEqual(proc.returncode, 0)

    eleza test_double_close_on_error(self):
        # Issue #18851
        fds = []
        eleza open_fds():
            kila i kwenye range(20):
                fds.extend(os.pipe())
                time.sleep(0.001)
        t = threading.Thread(target=open_fds)
        t.start()
        jaribu:
            ukijumuisha self.assertRaises(EnvironmentError):
                subprocess.Popen(NONEXISTING_CMD,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        mwishowe:
            t.join()
            exc = Tupu
            kila fd kwenye fds:
                # If a double close occurred, some of those fds will
                # already have been closed by mistake, na os.close()
                # here will raise.
                jaribu:
                    os.close(fd)
                tatizo OSError kama e:
                    exc = e
            ikiwa exc ni sio Tupu:
                ashiria exc

    eleza test_threadsafe_wait(self):
        """Issue21291: Popen.wait() needs to be threadsafe kila returncode."""
        proc = subprocess.Popen([sys.executable, '-c',
                                 'agiza time; time.sleep(12)'])
        self.assertEqual(proc.returncode, Tupu)
        results = []

        eleza kill_proc_timer_thread():
            results.append(('thread-start-poll-result', proc.poll()))
            # terminate it kutoka the thread na wait kila the result.
            proc.kill()
            proc.wait()
            results.append(('thread-after-kill-and-wait', proc.returncode))
            # this wait should be a no-op given the above.
            proc.wait()
            results.append(('thread-after-second-wait', proc.returncode))

        # This ni a timing sensitive test, the failure mode is
        # triggered when both the main thread na this thread are kwenye
        # the wait() call at once.  The delay here ni to allow the
        # main thread to most likely be blocked kwenye its wait() call.
        t = threading.Timer(0.2, kill_proc_timer_thread)
        t.start()

        ikiwa mswindows:
            expected_errorcode = 1
        isipokua:
            # Should be -9 because of the proc.kill() kutoka the thread.
            expected_errorcode = -9

        # Wait kila the process to finish; the thread should kill it
        # long before it finishes on its own.  Supplying a timeout
        # triggers a different code path kila better coverage.
        proc.wait(timeout=20)
        self.assertEqual(proc.returncode, expected_errorcode,
                         msg="unexpected result kwenye wait kutoka main thread")

        # This should be a no-op ukijumuisha no change kwenye returncode.
        proc.wait()
        self.assertEqual(proc.returncode, expected_errorcode,
                         msg="unexpected result kwenye second main wait.")

        t.join()
        # Ensure that all of the thread results are kama expected.
        # When a race condition occurs kwenye wait(), the returncode could
        # be set by the wrong thread that doesn't actually have it
        # leading to an incorrect value.
        self.assertEqual([('thread-start-poll-result', Tupu),
                          ('thread-after-kill-and-wait', expected_errorcode),
                          ('thread-after-second-wait', expected_errorcode)],
                         results)

    eleza test_issue8780(self):
        # Ensure that stdout ni inherited kutoka the parent
        # ikiwa stdout=PIPE ni sio used
        code = ';'.join((
            'agiza subprocess, sys',
            'retcode = subprocess.call('
                "[sys.executable, '-c', 'andika(\"Hello World!\")'])",
            'assert retcode == 0'))
        output = subprocess.check_output([sys.executable, '-c', code])
        self.assertKweli(output.startswith(b'Hello World!'), ascii(output))

    eleza test_handles_closed_on_exception(self):
        # If CreateProcess exits ukijumuisha an error, ensure the
        # duplicate output handles are released
        ifhandle, ifname = tempfile.mkstemp()
        ofhandle, ofname = tempfile.mkstemp()
        efhandle, efname = tempfile.mkstemp()
        jaribu:
            subprocess.Popen (["*"], stdin=ifhandle, stdout=ofhandle,
              stderr=efhandle)
        tatizo OSError:
            os.close(ifhandle)
            os.remove(ifname)
            os.close(ofhandle)
            os.remove(ofname)
            os.close(efhandle)
            os.remove(efname)
        self.assertUongo(os.path.exists(ifname))
        self.assertUongo(os.path.exists(ofname))
        self.assertUongo(os.path.exists(efname))

    eleza test_communicate_epipe(self):
        # Issue 10963: communicate() should hide EPIPE
        p = subprocess.Popen([sys.executable, "-c", 'pita'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        self.addCleanup(p.stdin.close)
        p.communicate(b"x" * 2**20)

    eleza test_communicate_epipe_only_stdin(self):
        # Issue 10963: communicate() should hide EPIPE
        p = subprocess.Popen([sys.executable, "-c", 'pita'],
                             stdin=subprocess.PIPE)
        self.addCleanup(p.stdin.close)
        p.wait()
        p.communicate(b"x" * 2**20)

    @unittest.skipUnless(hasattr(signal, 'SIGUSR1'),
                         "Requires signal.SIGUSR1")
    @unittest.skipUnless(hasattr(os, 'kill'),
                         "Requires os.kill")
    @unittest.skipUnless(hasattr(os, 'getppid'),
                         "Requires os.getppid")
    eleza test_communicate_eintr(self):
        # Issue #12493: communicate() should handle EINTR
        eleza handler(signum, frame):
            pita
        old_handler = signal.signal(signal.SIGUSR1, handler)
        self.addCleanup(signal.signal, signal.SIGUSR1, old_handler)

        args = [sys.executable, "-c",
                'agiza os, signal;'
                'os.kill(os.getppid(), signal.SIGUSR1)']
        kila stream kwenye ('stdout', 'stderr'):
            kw = {stream: subprocess.PIPE}
            ukijumuisha subprocess.Popen(args, **kw) kama process:
                # communicate() will be interrupted by SIGUSR1
                process.communicate()


    # This test ni Linux-ish specific kila simplicity to at least have
    # some coverage.  It ni sio a platform specific bug.
    @unittest.skipUnless(os.path.isdir('/proc/%d/fd' % os.getpid()),
                         "Linux specific")
    eleza test_failed_child_execute_fd_leak(self):
        """Test kila the fork() failure fd leak reported kwenye issue16327."""
        fd_directory = '/proc/%d/fd' % os.getpid()
        fds_before_popen = os.listdir(fd_directory)
        ukijumuisha self.assertRaises(PopenTestException):
            PopenExecuteChildRaises(
                    [sys.executable, '-c', 'pita'], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # NOTE: This test doesn't verify that the real _execute_child
        # does sio close the file descriptors itself on the way out
        # during an exception.  Code inspection has confirmed that.

        fds_after_exception = os.listdir(fd_directory)
        self.assertEqual(fds_before_popen, fds_after_exception)

    @unittest.skipIf(mswindows, "behavior currently sio supported on Windows")
    eleza test_file_not_found_includes_filename(self):
        ukijumuisha self.assertRaises(FileNotFoundError) kama c:
            subprocess.call(['/opt/nonexistent_binary', 'with', 'some', 'args'])
        self.assertEqual(c.exception.filename, '/opt/nonexistent_binary')

    @unittest.skipIf(mswindows, "behavior currently sio supported on Windows")
    eleza test_file_not_found_with_bad_cwd(self):
        ukijumuisha self.assertRaises(FileNotFoundError) kama c:
            subprocess.Popen(['exit', '0'], cwd='/some/nonexistent/directory')
        self.assertEqual(c.exception.filename, '/some/nonexistent/directory')


kundi RunFuncTestCase(BaseTestCase):
    eleza run_python(self, code, **kwargs):
        """Run Python code kwenye a subprocess using subprocess.run"""
        argv = [sys.executable, "-c", code]
        rudisha subprocess.run(argv, **kwargs)

    eleza test_returncode(self):
        # call() function ukijumuisha sequence argument
        cp = self.run_python("agiza sys; sys.exit(47)")
        self.assertEqual(cp.returncode, 47)
        ukijumuisha self.assertRaises(subprocess.CalledProcessError):
            cp.check_returncode()

    eleza test_check(self):
        ukijumuisha self.assertRaises(subprocess.CalledProcessError) kama c:
            self.run_python("agiza sys; sys.exit(47)", check=Kweli)
        self.assertEqual(c.exception.returncode, 47)

    eleza test_check_zero(self):
        # check_returncode shouldn't ashiria when returncode ni zero
        cp = self.run_python("agiza sys; sys.exit(0)", check=Kweli)
        self.assertEqual(cp.returncode, 0)

    eleza test_timeout(self):
        # run() function ukijumuisha timeout argument; we want to test that the child
        # process gets killed when the timeout expires.  If the child isn't
        # killed, this call will deadlock since subprocess.run waits kila the
        # child.
        ukijumuisha self.assertRaises(subprocess.TimeoutExpired):
            self.run_python("wakati Kweli: pita", timeout=0.0001)

    eleza test_capture_stdout(self):
        # capture stdout ukijumuisha zero rudisha code
        cp = self.run_python("andika('BDFL')", stdout=subprocess.PIPE)
        self.assertIn(b'BDFL', cp.stdout)

    eleza test_capture_stderr(self):
        cp = self.run_python("agiza sys; sys.stderr.write('BDFL')",
                             stderr=subprocess.PIPE)
        self.assertIn(b'BDFL', cp.stderr)

    eleza test_check_output_stdin_arg(self):
        # run() can be called ukijumuisha stdin set to a file
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b'pear')
        tf.seek(0)
        cp = self.run_python(
                 "agiza sys; sys.stdout.write(sys.stdin.read().upper())",
                stdin=tf, stdout=subprocess.PIPE)
        self.assertIn(b'PEAR', cp.stdout)

    eleza test_check_output_input_arg(self):
        # check_output() can be called ukijumuisha input set to a string
        cp = self.run_python(
                "agiza sys; sys.stdout.write(sys.stdin.read().upper())",
                input=b'pear', stdout=subprocess.PIPE)
        self.assertIn(b'PEAR', cp.stdout)

    eleza test_check_output_stdin_with_input_arg(self):
        # run() refuses to accept 'stdin' ukijumuisha 'input'
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        tf.write(b'pear')
        tf.seek(0)
        ukijumuisha self.assertRaises(ValueError,
              msg="Expected ValueError when stdin na input args supplied.") kama c:
            output = self.run_python("andika('will sio be run')",
                                     stdin=tf, input=b'hare')
        self.assertIn('stdin', c.exception.args[0])
        self.assertIn('input', c.exception.args[0])

    eleza test_check_output_timeout(self):
        ukijumuisha self.assertRaises(subprocess.TimeoutExpired) kama c:
            cp = self.run_python((
                     "agiza sys, time\n"
                     "sys.stdout.write('BDFL')\n"
                     "sys.stdout.flush()\n"
                     "time.sleep(3600)"),
                    # Some heavily loaded buildbots (sparc Debian 3.x) require
                    # this much time to start na print.
                    timeout=3, stdout=subprocess.PIPE)
        self.assertEqual(c.exception.output, b'BDFL')
        # output ni aliased to stdout
        self.assertEqual(c.exception.stdout, b'BDFL')

    eleza test_run_kwargs(self):
        newenv = os.environ.copy()
        newenv["FRUIT"] = "banana"
        cp = self.run_python(('agiza sys, os;'
                      'sys.exit(33 ikiwa os.getenv("FRUIT")=="banana" isipokua 31)'),
                             env=newenv)
        self.assertEqual(cp.returncode, 33)

    eleza test_run_with_pathlike_path(self):
        # bpo-31961: test run(pathlike_object)
        # the name of a command that can be run without
        # any argumenets that exit fast
        prog = 'tree.com' ikiwa mswindows isipokua 'ls'
        path = shutil.which(prog)
        ikiwa path ni Tupu:
            self.skipTest(f'{prog} required kila this test')
        path = FakePath(path)
        res = subprocess.run(path, stdout=subprocess.DEVNULL)
        self.assertEqual(res.returncode, 0)
        ukijumuisha self.assertRaises(TypeError):
            subprocess.run(path, stdout=subprocess.DEVNULL, shell=Kweli)

    eleza test_run_with_bytes_path_and_arguments(self):
        # bpo-31961: test run([bytes_object, b'additional arguments'])
        path = os.fsencode(sys.executable)
        args = [path, '-c', b'agiza sys; sys.exit(57)']
        res = subprocess.run(args)
        self.assertEqual(res.returncode, 57)

    eleza test_run_with_pathlike_path_and_arguments(self):
        # bpo-31961: test run([pathlike_object, 'additional arguments'])
        path = FakePath(sys.executable)
        args = [path, '-c', 'agiza sys; sys.exit(57)']
        res = subprocess.run(args)
        self.assertEqual(res.returncode, 57)

    eleza test_capture_output(self):
        cp = self.run_python(("agiza sys;"
                              "sys.stdout.write('BDFL'); "
                              "sys.stderr.write('FLUFL')"),
                             capture_output=Kweli)
        self.assertIn(b'BDFL', cp.stdout)
        self.assertIn(b'FLUFL', cp.stderr)

    eleza test_stdout_with_capture_output_arg(self):
        # run() refuses to accept 'stdout' ukijumuisha 'capture_output'
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        ukijumuisha self.assertRaises(ValueError,
            msg=("Expected ValueError when stdout na capture_output "
                 "args supplied.")) kama c:
            output = self.run_python("andika('will sio be run')",
                                      capture_output=Kweli, stdout=tf)
        self.assertIn('stdout', c.exception.args[0])
        self.assertIn('capture_output', c.exception.args[0])

    eleza test_stderr_with_capture_output_arg(self):
        # run() refuses to accept 'stderr' ukijumuisha 'capture_output'
        tf = tempfile.TemporaryFile()
        self.addCleanup(tf.close)
        ukijumuisha self.assertRaises(ValueError,
            msg=("Expected ValueError when stderr na capture_output "
                 "args supplied.")) kama c:
            output = self.run_python("andika('will sio be run')",
                                      capture_output=Kweli, stderr=tf)
        self.assertIn('stderr', c.exception.args[0])
        self.assertIn('capture_output', c.exception.args[0])

    # This test _might_ wind up a bit fragile on loaded build+test machines
    # kama it depends on the timing ukijumuisha wide enough margins kila normal situations
    # but does assert that it happened "soon enough" to believe the right thing
    # happened.
    @unittest.skipIf(mswindows, "requires posix like 'sleep' shell command")
    eleza test_run_with_shell_timeout_and_capture_output(self):
        """Output capturing after a timeout mustn't hang forever on open filehandles."""
        before_secs = time.monotonic()
        jaribu:
            subprocess.run('sleep 3', shell=Kweli, timeout=0.1,
                           capture_output=Kweli)  # New session unspecified.
        tatizo subprocess.TimeoutExpired kama exc:
            after_secs = time.monotonic()
            stacks = traceback.format_exc()  # assertRaises doesn't give this.
        isipokua:
            self.fail("TimeoutExpired sio raised.")
        self.assertLess(after_secs - before_secs, 1.5,
                        msg="TimeoutExpired was delayed! Bad traceback:\n```\n"
                        f"{stacks}```")


@unittest.skipIf(mswindows, "POSIX specific tests")
kundi POSIXProcessTestCase(BaseTestCase):

    eleza setUp(self):
        super().setUp()
        self._nonexistent_dir = "/_this/pa.th/does/not/exist"

    eleza _get_chdir_exception(self):
        jaribu:
            os.chdir(self._nonexistent_dir)
        tatizo OSError kama e:
            # This avoids hard coding the errno value ama the OS perror()
            # string na instead capture the exception that we want to see
            # below kila comparison.
            desired_exception = e
        isipokua:
            self.fail("chdir to nonexistent directory %s succeeded." %
                      self._nonexistent_dir)
        rudisha desired_exception

    eleza test_exception_cwd(self):
        """Test error kwenye the child raised kwenye the parent kila a bad cwd."""
        desired_exception = self._get_chdir_exception()
        jaribu:
            p = subprocess.Popen([sys.executable, "-c", ""],
                                 cwd=self._nonexistent_dir)
        tatizo OSError kama e:
            # Test that the child process chdir failure actually makes
            # it up to the parent process kama the correct exception.
            self.assertEqual(desired_exception.errno, e.errno)
            self.assertEqual(desired_exception.strerror, e.strerror)
            self.assertEqual(desired_exception.filename, e.filename)
        isipokua:
            self.fail("Expected OSError: %s" % desired_exception)

    eleza test_exception_bad_executable(self):
        """Test error kwenye the child raised kwenye the parent kila a bad executable."""
        desired_exception = self._get_chdir_exception()
        jaribu:
            p = subprocess.Popen([sys.executable, "-c", ""],
                                 executable=self._nonexistent_dir)
        tatizo OSError kama e:
            # Test that the child process exec failure actually makes
            # it up to the parent process kama the correct exception.
            self.assertEqual(desired_exception.errno, e.errno)
            self.assertEqual(desired_exception.strerror, e.strerror)
            self.assertEqual(desired_exception.filename, e.filename)
        isipokua:
            self.fail("Expected OSError: %s" % desired_exception)

    eleza test_exception_bad_args_0(self):
        """Test error kwenye the child raised kwenye the parent kila a bad args[0]."""
        desired_exception = self._get_chdir_exception()
        jaribu:
            p = subprocess.Popen([self._nonexistent_dir, "-c", ""])
        tatizo OSError kama e:
            # Test that the child process exec failure actually makes
            # it up to the parent process kama the correct exception.
            self.assertEqual(desired_exception.errno, e.errno)
            self.assertEqual(desired_exception.strerror, e.strerror)
            self.assertEqual(desired_exception.filename, e.filename)
        isipokua:
            self.fail("Expected OSError: %s" % desired_exception)

    # We mock the __del__ method kila Popen kwenye the next two tests
    # because it does cleanup based on the pid returned by fork_exec
    # along ukijumuisha issuing a resource warning ikiwa it still exists. Since
    # we don't actually spawn a process kwenye these tests we can forego
    # the destructor. An alternative would be to set _child_created to
    # Uongo before the destructor ni called but there ni no easy way
    # to do that
    kundi PopenNoDestructor(subprocess.Popen):
        eleza __del__(self):
            pita

    @mock.patch("subprocess._posixsubprocess.fork_exec")
    eleza test_exception_errpipe_normal(self, fork_exec):
        """Test error pitaing done through errpipe_write kwenye the good case"""
        eleza proper_error(*args):
            errpipe_write = args[13]
            # Write the hex kila the error code EISDIR: 'is a directory'
            err_code = '{:x}'.format(errno.EISDIR).encode()
            os.write(errpipe_write, b"OSError:" + err_code + b":")
            rudisha 0

        fork_exec.side_effect = proper_error

        ukijumuisha mock.patch("subprocess.os.waitpid",
                        side_effect=ChildProcessError):
            ukijumuisha self.assertRaises(IsADirectoryError):
                self.PopenNoDestructor(["non_existent_command"])

    @mock.patch("subprocess._posixsubprocess.fork_exec")
    eleza test_exception_errpipe_bad_data(self, fork_exec):
        """Test error pitaing done through errpipe_write where its sio
        kwenye the expected format"""
        error_data = b"\xFF\x00\xDE\xAD"
        eleza bad_error(*args):
            errpipe_write = args[13]
            # Anything can be kwenye the pipe, no assumptions should
            # be made about its encoding, so we'll write some
            # arbitrary hex bytes to test it out
            os.write(errpipe_write, error_data)
            rudisha 0

        fork_exec.side_effect = bad_error

        ukijumuisha mock.patch("subprocess.os.waitpid",
                        side_effect=ChildProcessError):
            ukijumuisha self.assertRaises(subprocess.SubprocessError) kama e:
                self.PopenNoDestructor(["non_existent_command"])

        self.assertIn(repr(error_data), str(e.exception))

    @unittest.skipIf(sio os.path.exists('/proc/self/status'),
                     "need /proc/self/status")
    eleza test_restore_signals(self):
        # Blindly assume that cat exists on systems ukijumuisha /proc/self/status...
        default_proc_status = subprocess.check_output(
                ['cat', '/proc/self/status'],
                restore_signals=Uongo)
        kila line kwenye default_proc_status.splitlines():
            ikiwa line.startswith(b'SigIgn'):
                default_sig_ign_mask = line
                koma
        isipokua:
            self.skipTest("SigIgn sio found kwenye /proc/self/status.")
        restored_proc_status = subprocess.check_output(
                ['cat', '/proc/self/status'],
                restore_signals=Kweli)
        kila line kwenye restored_proc_status.splitlines():
            ikiwa line.startswith(b'SigIgn'):
                restored_sig_ign_mask = line
                koma
        self.assertNotEqual(default_sig_ign_mask, restored_sig_ign_mask,
                            msg="restore_signals=Kweli should've unblocked "
                            "SIGPIPE na friends.")

    eleza test_start_new_session(self):
        # For code coverage of calling setsid().  We don't care ikiwa we get an
        # EPERM error kutoka it depending on the test execution environment, that
        # still indicates that it was called.
        jaribu:
            output = subprocess.check_output(
                    [sys.executable, "-c", "agiza os; andika(os.getsid(0))"],
                    start_new_session=Kweli)
        tatizo OSError kama e:
            ikiwa e.errno != errno.EPERM:
                raise
        isipokua:
            parent_sid = os.getsid(0)
            child_sid = int(output)
            self.assertNotEqual(parent_sid, child_sid)

    eleza test_run_abort(self):
        # returncode handles signal termination
        ukijumuisha support.SuppressCrashReport():
            p = subprocess.Popen([sys.executable, "-c",
                                  'agiza os; os.abort()'])
            p.wait()
        self.assertEqual(-p.returncode, signal.SIGABRT)

    eleza test_CalledProcessError_str_signal(self):
        err = subprocess.CalledProcessError(-int(signal.SIGABRT), "fake cmd")
        error_string = str(err)
        # We're relying on the repr() of the signal.Signals intenum to provide
        # the word signal, the signal name na the numeric value.
        self.assertIn("signal", error_string.lower())
        # We're sio being specific about the signal name kama some signals have
        # multiple names na which name ni revealed can vary.
        self.assertIn("SIG", error_string)
        self.assertIn(str(signal.SIGABRT), error_string)

    eleza test_CalledProcessError_str_unknown_signal(self):
        err = subprocess.CalledProcessError(-9876543, "fake cmd")
        error_string = str(err)
        self.assertIn("unknown signal 9876543.", error_string)

    eleza test_CalledProcessError_str_non_zero(self):
        err = subprocess.CalledProcessError(2, "fake cmd")
        error_string = str(err)
        self.assertIn("non-zero exit status 2.", error_string)

    eleza test_preexec(self):
        # DISCLAIMER: Setting environment variables ni *not* a good use
        # of a preexec_fn.  This ni merely a test.
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys,os;'
                              'sys.stdout.write(os.getenv("FRUIT"))'],
                             stdout=subprocess.PIPE,
                             preexec_fn=lambda: os.putenv("FRUIT", "apple"))
        ukijumuisha p:
            self.assertEqual(p.stdout.read(), b"apple")

    eleza test_preexec_exception(self):
        eleza raise_it():
            ashiria ValueError("What ikiwa two swallows carried a coconut?")
        jaribu:
            p = subprocess.Popen([sys.executable, "-c", ""],
                                 preexec_fn=raise_it)
        tatizo subprocess.SubprocessError kama e:
            self.assertKweli(
                    subprocess._posixsubprocess,
                    "Expected a ValueError kutoka the preexec_fn")
        tatizo ValueError kama e:
            self.assertIn("coconut", e.args[0])
        isipokua:
            self.fail("Exception raised by preexec_fn did sio make it "
                      "to the parent process.")

    kundi _TestExecuteChildPopen(subprocess.Popen):
        """Used to test behavior at the end of _execute_child."""
        eleza __init__(self, testcase, *args, **kwargs):
            self._testcase = testcase
            subprocess.Popen.__init__(self, *args, **kwargs)

        eleza _execute_child(self, *args, **kwargs):
            jaribu:
                subprocess.Popen._execute_child(self, *args, **kwargs)
            mwishowe:
                # Open a bunch of file descriptors na verify that
                # none of them are the same kama the ones the Popen
                # instance ni using kila stdin/stdout/stderr.
                devzero_fds = [os.open("/dev/zero", os.O_RDONLY)
                               kila _ kwenye range(8)]
                jaribu:
                    kila fd kwenye devzero_fds:
                        self._testcase.assertNotIn(
                                fd, (self.stdin.fileno(), self.stdout.fileno(),
                                     self.stderr.fileno()),
                                msg="At least one fd was closed early.")
                mwishowe:
                    kila fd kwenye devzero_fds:
                        os.close(fd)

    @unittest.skipIf(sio os.path.exists("/dev/zero"), "/dev/zero required.")
    eleza test_preexec_errpipe_does_not_double_close_pipes(self):
        """Issue16140: Don't double close pipes on preexec error."""

        eleza raise_it():
            ashiria subprocess.SubprocessError(
                    "force the _execute_child() errpipe_data path.")

        ukijumuisha self.assertRaises(subprocess.SubprocessError):
            self._TestExecuteChildPopen(
                        self, [sys.executable, "-c", "pita"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, preexec_fn=raise_it)

    eleza test_preexec_gc_module_failure(self):
        # This tests the code that disables garbage collection ikiwa the child
        # process will execute any Python.
        eleza raise_runtime_error():
            ashiria RuntimeError("this shouldn't escape")
        enabled = gc.isenabled()
        orig_gc_disable = gc.disable
        orig_gc_isenabled = gc.isenabled
        jaribu:
            gc.disable()
            self.assertUongo(gc.isenabled())
            subprocess.call([sys.executable, '-c', ''],
                            preexec_fn=lambda: Tupu)
            self.assertUongo(gc.isenabled(),
                             "Popen enabled gc when it shouldn't.")

            gc.enable()
            self.assertKweli(gc.isenabled())
            subprocess.call([sys.executable, '-c', ''],
                            preexec_fn=lambda: Tupu)
            self.assertKweli(gc.isenabled(), "Popen left gc disabled.")

            gc.disable = raise_runtime_error
            self.assertRaises(RuntimeError, subprocess.Popen,
                              [sys.executable, '-c', ''],
                              preexec_fn=lambda: Tupu)

            toa gc.isenabled  # force an AttributeError
            self.assertRaises(AttributeError, subprocess.Popen,
                              [sys.executable, '-c', ''],
                              preexec_fn=lambda: Tupu)
        mwishowe:
            gc.disable = orig_gc_disable
            gc.isenabled = orig_gc_isenabled
            ikiwa sio enabled:
                gc.disable()

    @unittest.skipIf(
        sys.platform == 'darwin', 'setrlimit() seems to fail on OS X')
    eleza test_preexec_fork_failure(self):
        # The internal code did sio preserve the previous exception when
        # re-enabling garbage collection
        jaribu:
            kutoka resource agiza getrlimit, setrlimit, RLIMIT_NPROC
        tatizo ImportError kama err:
            self.skipTest(err)  # RLIMIT_NPROC ni specific to Linux na BSD
        limits = getrlimit(RLIMIT_NPROC)
        [_, hard] = limits
        setrlimit(RLIMIT_NPROC, (0, hard))
        self.addCleanup(setrlimit, RLIMIT_NPROC, limits)
        jaribu:
            subprocess.call([sys.executable, '-c', ''],
                            preexec_fn=lambda: Tupu)
        tatizo BlockingIOError:
            # Forking should ashiria EAGAIN, translated to BlockingIOError
            pita
        isipokua:
            self.skipTest('RLIMIT_NPROC had no effect; probably superuser')

    eleza test_args_string(self):
        # args ni a string
        fd, fname = tempfile.mkstemp()
        # reopen kwenye text mode
        ukijumuisha open(fd, "w", errors="surrogateescape") kama fobj:
            fobj.write("#!%s\n" % support.unix_shell)
            fobj.write("exec '%s' -c 'agiza sys; sys.exit(47)'\n" %
                       sys.executable)
        os.chmod(fname, 0o700)
        p = subprocess.Popen(fname)
        p.wait()
        os.remove(fname)
        self.assertEqual(p.returncode, 47)

    eleza test_invalid_args(self):
        # invalid arguments should ashiria ValueError
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "agiza sys; sys.exit(47)"],
                          startupinfo=47)
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "agiza sys; sys.exit(47)"],
                          creationflags=47)

    eleza test_shell_sequence(self):
        # Run command through the shell (sequence)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "apple"
        p = subprocess.Popen(["echo $FRUIT"], shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        ukijumuisha p:
            self.assertEqual(p.stdout.read().strip(b" \t\r\n\f"), b"apple")

    eleza test_shell_string(self):
        # Run command through the shell (string)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "apple"
        p = subprocess.Popen("echo $FRUIT", shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        ukijumuisha p:
            self.assertEqual(p.stdout.read().strip(b" \t\r\n\f"), b"apple")

    eleza test_call_string(self):
        # call() function ukijumuisha string argument on UNIX
        fd, fname = tempfile.mkstemp()
        # reopen kwenye text mode
        ukijumuisha open(fd, "w", errors="surrogateescape") kama fobj:
            fobj.write("#!%s\n" % support.unix_shell)
            fobj.write("exec '%s' -c 'agiza sys; sys.exit(47)'\n" %
                       sys.executable)
        os.chmod(fname, 0o700)
        rc = subprocess.call(fname)
        os.remove(fname)
        self.assertEqual(rc, 47)

    eleza test_specific_shell(self):
        # Issue #9265: Incorrect name pitaed kama arg[0].
        shells = []
        kila prefix kwenye ['/bin', '/usr/bin/', '/usr/local/bin']:
            kila name kwenye ['bash', 'ksh']:
                sh = os.path.join(prefix, name)
                ikiwa os.path.isfile(sh):
                    shells.append(sh)
        ikiwa sio shells: # Will probably work kila any shell but csh.
            self.skipTest("bash ama ksh required kila this test")
        sh = '/bin/sh'
        ikiwa os.path.isfile(sh) na sio os.path.islink(sh):
            # Test will fail ikiwa /bin/sh ni a symlink to csh.
            shells.append(sh)
        kila sh kwenye shells:
            p = subprocess.Popen("echo $0", executable=sh, shell=Kweli,
                                 stdout=subprocess.PIPE)
            ukijumuisha p:
                self.assertEqual(p.stdout.read().strip(), bytes(sh, 'ascii'))

    eleza _kill_process(self, method, *args):
        # Do sio inerit file handles kutoka the parent.
        # It should fix failures on some platforms.
        # Also set the SIGINT handler to the default to make sure it's sio
        # being ignored (some tests rely on that.)
        old_handler = signal.signal(signal.SIGINT, signal.default_int_handler)
        jaribu:
            p = subprocess.Popen([sys.executable, "-c", """ikiwa 1:
                                 agiza sys, time
                                 sys.stdout.write('x\\n')
                                 sys.stdout.flush()
                                 time.sleep(30)
                                 """],
                                 close_fds=Kweli,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        mwishowe:
            signal.signal(signal.SIGINT, old_handler)
        # Wait kila the interpreter to be completely initialized before
        # sending any signal.
        p.stdout.read(1)
        getattr(p, method)(*args)
        rudisha p

    @unittest.skipIf(sys.platform.startswith(('netbsd', 'openbsd')),
                     "Due to known OS bug (issue #16762)")
    eleza _kill_dead_process(self, method, *args):
        # Do sio inerit file handles kutoka the parent.
        # It should fix failures on some platforms.
        p = subprocess.Popen([sys.executable, "-c", """ikiwa 1:
                             agiza sys, time
                             sys.stdout.write('x\\n')
                             sys.stdout.flush()
                             """],
                             close_fds=Kweli,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        # Wait kila the interpreter to be completely initialized before
        # sending any signal.
        p.stdout.read(1)
        # The process should end after this
        time.sleep(1)
        # This shouldn't ashiria even though the child ni now dead
        getattr(p, method)(*args)
        p.communicate()

    eleza test_send_signal(self):
        p = self._kill_process('send_signal', signal.SIGINT)
        _, stderr = p.communicate()
        self.assertIn(b'KeyboardInterrupt', stderr)
        self.assertNotEqual(p.wait(), 0)

    eleza test_kill(self):
        p = self._kill_process('kill')
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, b'')
        self.assertEqual(p.wait(), -signal.SIGKILL)

    eleza test_terminate(self):
        p = self._kill_process('terminate')
        _, stderr = p.communicate()
        self.assertStderrEqual(stderr, b'')
        self.assertEqual(p.wait(), -signal.SIGTERM)

    eleza test_send_signal_dead(self):
        # Sending a signal to a dead process
        self._kill_dead_process('send_signal', signal.SIGINT)

    eleza test_kill_dead(self):
        # Killing a dead process
        self._kill_dead_process('kill')

    eleza test_terminate_dead(self):
        # Terminating a dead process
        self._kill_dead_process('terminate')

    eleza _save_fds(self, save_fds):
        fds = []
        kila fd kwenye save_fds:
            inheritable = os.get_inheritable(fd)
            saved = os.dup(fd)
            fds.append((fd, saved, inheritable))
        rudisha fds

    eleza _restore_fds(self, fds):
        kila fd, saved, inheritable kwenye fds:
            os.dup2(saved, fd, inheritable=inheritable)
            os.close(saved)

    eleza check_close_std_fds(self, fds):
        # Issue #9905: test that subprocess pipes still work properly with
        # some standard fds closed
        stdin = 0
        saved_fds = self._save_fds(fds)
        kila fd, saved, inheritable kwenye saved_fds:
            ikiwa fd == 0:
                stdin = saved
                koma
        jaribu:
            kila fd kwenye fds:
                os.close(fd)
            out, err = subprocess.Popen([sys.executable, "-c",
                              'agiza sys;'
                              'sys.stdout.write("apple");'
                              'sys.stdout.flush();'
                              'sys.stderr.write("orange")'],
                       stdin=stdin,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE).communicate()
            err = support.strip_python_stderr(err)
            self.assertEqual((out, err), (b'apple', b'orange'))
        mwishowe:
            self._restore_fds(saved_fds)

    eleza test_close_fd_0(self):
        self.check_close_std_fds([0])

    eleza test_close_fd_1(self):
        self.check_close_std_fds([1])

    eleza test_close_fd_2(self):
        self.check_close_std_fds([2])

    eleza test_close_fds_0_1(self):
        self.check_close_std_fds([0, 1])

    eleza test_close_fds_0_2(self):
        self.check_close_std_fds([0, 2])

    eleza test_close_fds_1_2(self):
        self.check_close_std_fds([1, 2])

    eleza test_close_fds_0_1_2(self):
        # Issue #10806: test that subprocess pipes still work properly with
        # all standard fds closed.
        self.check_close_std_fds([0, 1, 2])

    eleza test_small_errpipe_write_fd(self):
        """Issue #15798: Popen should work when stdio fds are available."""
        new_stdin = os.dup(0)
        new_stdout = os.dup(1)
        jaribu:
            os.close(0)
            os.close(1)

            # Side test: ikiwa errpipe_write fails to have its CLOEXEC
            # flag set this should cause the parent to think the exec
            # failed.  Extremely unlikely: everyone supports CLOEXEC.
            subprocess.Popen([
                    sys.executable, "-c",
                    "andika('AssertionError:0:CLOEXEC failure.')"]).wait()
        mwishowe:
            # Restore original stdin na stdout
            os.dup2(new_stdin, 0)
            os.dup2(new_stdout, 1)
            os.close(new_stdin)
            os.close(new_stdout)

    eleza test_remapping_std_fds(self):
        # open up some temporary files
        temps = [tempfile.mkstemp() kila i kwenye range(3)]
        jaribu:
            temp_fds = [fd kila fd, fname kwenye temps]

            # unlink the files -- we won't need to reopen them
            kila fd, fname kwenye temps:
                os.unlink(fname)

            # write some data to what will become stdin, na rewind
            os.write(temp_fds[1], b"STDIN")
            os.lseek(temp_fds[1], 0, 0)

            # move the standard file descriptors out of the way
            saved_fds = self._save_fds(range(3))
            jaribu:
                # duplicate the file objects over the standard fd's
                kila fd, temp_fd kwenye enumerate(temp_fds):
                    os.dup2(temp_fd, fd)

                # now use those files kwenye the "wrong" order, so that subprocess
                # has to rearrange them kwenye the child
                p = subprocess.Popen([sys.executable, "-c",
                    'agiza sys; got = sys.stdin.read();'
                    'sys.stdout.write("got %s"%got); sys.stderr.write("err")'],
                    stdin=temp_fds[1],
                    stdout=temp_fds[2],
                    stderr=temp_fds[0])
                p.wait()
            mwishowe:
                self._restore_fds(saved_fds)

            kila fd kwenye temp_fds:
                os.lseek(fd, 0, 0)

            out = os.read(temp_fds[2], 1024)
            err = support.strip_python_stderr(os.read(temp_fds[0], 1024))
            self.assertEqual(out, b"got STDIN")
            self.assertEqual(err, b"err")

        mwishowe:
            kila fd kwenye temp_fds:
                os.close(fd)

    eleza check_swap_fds(self, stdin_no, stdout_no, stderr_no):
        # open up some temporary files
        temps = [tempfile.mkstemp() kila i kwenye range(3)]
        temp_fds = [fd kila fd, fname kwenye temps]
        jaribu:
            # unlink the files -- we won't need to reopen them
            kila fd, fname kwenye temps:
                os.unlink(fname)

            # save a copy of the standard file descriptors
            saved_fds = self._save_fds(range(3))
            jaribu:
                # duplicate the temp files over the standard fd's 0, 1, 2
                kila fd, temp_fd kwenye enumerate(temp_fds):
                    os.dup2(temp_fd, fd)

                # write some data to what will become stdin, na rewind
                os.write(stdin_no, b"STDIN")
                os.lseek(stdin_no, 0, 0)

                # now use those files kwenye the given order, so that subprocess
                # has to rearrange them kwenye the child
                p = subprocess.Popen([sys.executable, "-c",
                    'agiza sys; got = sys.stdin.read();'
                    'sys.stdout.write("got %s"%got); sys.stderr.write("err")'],
                    stdin=stdin_no,
                    stdout=stdout_no,
                    stderr=stderr_no)
                p.wait()

                kila fd kwenye temp_fds:
                    os.lseek(fd, 0, 0)

                out = os.read(stdout_no, 1024)
                err = support.strip_python_stderr(os.read(stderr_no, 1024))
            mwishowe:
                self._restore_fds(saved_fds)

            self.assertEqual(out, b"got STDIN")
            self.assertEqual(err, b"err")

        mwishowe:
            kila fd kwenye temp_fds:
                os.close(fd)

    # When duping fds, ikiwa there arises a situation where one of the fds is
    # either 0, 1 ama 2, it ni possible that it ni overwritten (#12607).
    # This tests all combinations of this.
    eleza test_swap_fds(self):
        self.check_swap_fds(0, 1, 2)
        self.check_swap_fds(0, 2, 1)
        self.check_swap_fds(1, 0, 2)
        self.check_swap_fds(1, 2, 0)
        self.check_swap_fds(2, 0, 1)
        self.check_swap_fds(2, 1, 0)

    eleza _check_swap_std_fds_with_one_closed(self, from_fds, to_fds):
        saved_fds = self._save_fds(range(3))
        jaribu:
            kila from_fd kwenye from_fds:
                ukijumuisha tempfile.TemporaryFile() kama f:
                    os.dup2(f.fileno(), from_fd)

            fd_to_close = (set(range(3)) - set(from_fds)).pop()
            os.close(fd_to_close)

            arg_names = ['stdin', 'stdout', 'stderr']
            kwargs = {}
            kila from_fd, to_fd kwenye zip(from_fds, to_fds):
                kwargs[arg_names[to_fd]] = from_fd

            code = textwrap.dedent(r'''
                agiza os, sys
                skipped_fd = int(sys.argv[1])
                kila fd kwenye range(3):
                    ikiwa fd != skipped_fd:
                        os.write(fd, str(fd).encode('ascii'))
            ''')

            skipped_fd = (set(range(3)) - set(to_fds)).pop()

            rc = subprocess.call([sys.executable, '-c', code, str(skipped_fd)],
                                 **kwargs)
            self.assertEqual(rc, 0)

            kila from_fd, to_fd kwenye zip(from_fds, to_fds):
                os.lseek(from_fd, 0, os.SEEK_SET)
                read_bytes = os.read(from_fd, 1024)
                read_fds = list(map(int, read_bytes.decode('ascii')))
                msg = textwrap.dedent(f"""
                    When testing {from_fds} to {to_fds} redirection,
                    parent descriptor {from_fd} got redirected
                    to descriptor(s) {read_fds} instead of descriptor {to_fd}.
                """)
                self.assertEqual([to_fd], read_fds, msg)
        mwishowe:
            self._restore_fds(saved_fds)

    # Check that subprocess can remap std fds correctly even
    # ikiwa one of them ni closed (#32844).
    eleza test_swap_std_fds_with_one_closed(self):
        kila from_fds kwenye itertools.combinations(range(3), 2):
            kila to_fds kwenye itertools.permutations(range(3), 2):
                self._check_swap_std_fds_with_one_closed(from_fds, to_fds)

    eleza test_surrogates_error_message(self):
        eleza prepare():
            ashiria ValueError("surrogate:\uDCff")

        jaribu:
            subprocess.call(
                [sys.executable, "-c", "pita"],
                preexec_fn=prepare)
        tatizo ValueError kama err:
            # Pure Python implementations keeps the message
            self.assertIsTupu(subprocess._posixsubprocess)
            self.assertEqual(str(err), "surrogate:\uDCff")
        tatizo subprocess.SubprocessError kama err:
            # _posixsubprocess uses a default message
            self.assertIsNotTupu(subprocess._posixsubprocess)
            self.assertEqual(str(err), "Exception occurred kwenye preexec_fn.")
        isipokua:
            self.fail("Expected ValueError ama subprocess.SubprocessError")

    eleza test_undecodable_env(self):
        kila key, value kwenye (('test', 'abc\uDCFF'), ('test\uDCFF', '42')):
            encoded_value = value.encode("ascii", "surrogateescape")

            # test str ukijumuisha surrogates
            script = "agiza os; andika(ascii(os.getenv(%s)))" % repr(key)
            env = os.environ.copy()
            env[key] = value
            # Use C locale to get ASCII kila the locale encoding to force
            # surrogate-escaping of \xFF kwenye the child process
            env['LC_ALL'] = 'C'
            decoded_value = value
            stdout = subprocess.check_output(
                [sys.executable, "-c", script],
                env=env)
            stdout = stdout.rstrip(b'\n\r')
            self.assertEqual(stdout.decode('ascii'), ascii(decoded_value))

            # test bytes
            key = key.encode("ascii", "surrogateescape")
            script = "agiza os; andika(ascii(os.getenvb(%s)))" % repr(key)
            env = os.environ.copy()
            env[key] = encoded_value
            stdout = subprocess.check_output(
                [sys.executable, "-c", script],
                env=env)
            stdout = stdout.rstrip(b'\n\r')
            self.assertEqual(stdout.decode('ascii'), ascii(encoded_value))

    eleza test_bytes_program(self):
        abs_program = os.fsencode(sys.executable)
        path, program = os.path.split(sys.executable)
        program = os.fsencode(program)

        # absolute bytes path
        exitcode = subprocess.call([abs_program, "-c", "pita"])
        self.assertEqual(exitcode, 0)

        # absolute bytes path kama a string
        cmd = b"'" + abs_program + b"' -c pita"
        exitcode = subprocess.call(cmd, shell=Kweli)
        self.assertEqual(exitcode, 0)

        # bytes program, unicode PATH
        env = os.environ.copy()
        env["PATH"] = path
        exitcode = subprocess.call([program, "-c", "pita"], env=env)
        self.assertEqual(exitcode, 0)

        # bytes program, bytes PATH
        envb = os.environb.copy()
        envb[b"PATH"] = os.fsencode(path)
        exitcode = subprocess.call([program, "-c", "pita"], env=envb)
        self.assertEqual(exitcode, 0)

    eleza test_pipe_cloexec(self):
        sleeper = support.findfile("input_reader.py", subdir="subprocessdata")
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        p1 = subprocess.Popen([sys.executable, sleeper],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, close_fds=Uongo)

        self.addCleanup(p1.communicate, b'')

        p2 = subprocess.Popen([sys.executable, fd_status],
                              stdout=subprocess.PIPE, close_fds=Uongo)

        output, error = p2.communicate()
        result_fds = set(map(int, output.split(b',')))
        unwanted_fds = set([p1.stdin.fileno(), p1.stdout.fileno(),
                            p1.stderr.fileno()])

        self.assertUongo(result_fds & unwanted_fds,
                         "Expected no fds kutoka %r to be open kwenye child, "
                         "found %r" %
                              (unwanted_fds, result_fds & unwanted_fds))

    eleza test_pipe_cloexec_real_tools(self):
        qcat = support.findfile("qcat.py", subdir="subprocessdata")
        qgrep = support.findfile("qgrep.py", subdir="subprocessdata")

        subdata = b'zxcvbn'
        data = subdata * 4 + b'\n'

        p1 = subprocess.Popen([sys.executable, qcat],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              close_fds=Uongo)

        p2 = subprocess.Popen([sys.executable, qgrep, subdata],
                              stdin=p1.stdout, stdout=subprocess.PIPE,
                              close_fds=Uongo)

        self.addCleanup(p1.wait)
        self.addCleanup(p2.wait)
        eleza kill_p1():
            jaribu:
                p1.terminate()
            tatizo ProcessLookupError:
                pita
        eleza kill_p2():
            jaribu:
                p2.terminate()
            tatizo ProcessLookupError:
                pita
        self.addCleanup(kill_p1)
        self.addCleanup(kill_p2)

        p1.stdin.write(data)
        p1.stdin.close()

        readfiles, ignored1, ignored2 = select.select([p2.stdout], [], [], 10)

        self.assertKweli(readfiles, "The child hung")
        self.assertEqual(p2.stdout.read(), data)

        p1.stdout.close()
        p2.stdout.close()

    eleza test_close_fds(self):
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        fds = os.pipe()
        self.addCleanup(os.close, fds[0])
        self.addCleanup(os.close, fds[1])

        open_fds = set(fds)
        # add a bunch more fds
        kila _ kwenye range(9):
            fd = os.open(os.devnull, os.O_RDONLY)
            self.addCleanup(os.close, fd)
            open_fds.add(fd)

        kila fd kwenye open_fds:
            os.set_inheritable(fd, Kweli)

        p = subprocess.Popen([sys.executable, fd_status],
                             stdout=subprocess.PIPE, close_fds=Uongo)
        output, ignored = p.communicate()
        remaining_fds = set(map(int, output.split(b',')))

        self.assertEqual(remaining_fds & open_fds, open_fds,
                         "Some fds were closed")

        p = subprocess.Popen([sys.executable, fd_status],
                             stdout=subprocess.PIPE, close_fds=Kweli)
        output, ignored = p.communicate()
        remaining_fds = set(map(int, output.split(b',')))

        self.assertUongo(remaining_fds & open_fds,
                         "Some fds were left open")
        self.assertIn(1, remaining_fds, "Subprocess failed")

        # Keep some of the fd's we opened open kwenye the subprocess.
        # This tests _posixsubprocess.c's proper handling of fds_to_keep.
        fds_to_keep = set(open_fds.pop() kila _ kwenye range(8))
        p = subprocess.Popen([sys.executable, fd_status],
                             stdout=subprocess.PIPE, close_fds=Kweli,
                             pita_fds=fds_to_keep)
        output, ignored = p.communicate()
        remaining_fds = set(map(int, output.split(b',')))

        self.assertUongo((remaining_fds - fds_to_keep) & open_fds,
                         "Some fds haiko kwenye pita_fds were left open")
        self.assertIn(1, remaining_fds, "Subprocess failed")


    @unittest.skipIf(sys.platform.startswith("freebsd") na
                     os.stat("/dev").st_dev == os.stat("/dev/fd").st_dev,
                     "Requires fdescfs mounted on /dev/fd on FreeBSD.")
    eleza test_close_fds_when_max_fd_is_lowered(self):
        """Confirm that issue21618 ni fixed (may fail under valgrind)."""
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        # This launches the meat of the test kwenye a child process to
        # avoid messing ukijumuisha the larger unittest processes maximum
        # number of file descriptors.
        #  This process launches:
        #  +--> Process that lowers its RLIMIT_NOFILE aftr setting up
        #    a bunch of high open fds above the new lower rlimit.
        #    Those are reported via stdout before launching a new
        #    process ukijumuisha close_fds=Uongo to run the actual test:
        #    +--> The TEST: This one launches a fd_status.py
        #      subprocess ukijumuisha close_fds=Kweli so we can find out if
        #      any of the fds above the lowered rlimit are still open.
        p = subprocess.Popen([sys.executable, '-c', textwrap.dedent(
        '''
        agiza os, resource, subprocess, sys, textwrap
        open_fds = set()
        # Add a bunch more fds to pita down.
        kila _ kwenye range(40):
            fd = os.open(os.devnull, os.O_RDONLY)
            open_fds.add(fd)

        # Leave a two pairs of low ones available kila use by the
        # internal child error pipe na the stdout pipe.
        # We also leave 10 more open kama some Python buildbots run into
        # "too many open files" errors during the test ikiwa we do not.
        kila fd kwenye sorted(open_fds)[:14]:
            os.close(fd)
            open_fds.remove(fd)

        kila fd kwenye open_fds:
            #self.addCleanup(os.close, fd)
            os.set_inheritable(fd, Kweli)

        max_fd_open = max(open_fds)

        # Communicate the open_fds to the parent unittest.TestCase process.
        andika(','.join(map(str, sorted(open_fds))))
        sys.stdout.flush()

        rlim_cur, rlim_max = resource.getrlimit(resource.RLIMIT_NOFILE)
        jaribu:
            # 29 ni lower than the highest fds we are leaving open.
            resource.setrlimit(resource.RLIMIT_NOFILE, (29, rlim_max))
            # Launch a new Python interpreter ukijumuisha our low fd rlim_cur that
            # inherits open fds above that limit.  It then uses subprocess
            # ukijumuisha close_fds=Kweli to get a report of open fds kwenye the child.
            # An explicit list of fds to check ni pitaed to fd_status.py as
            # letting fd_status rely on its default logic would miss the
            # fds above rlim_cur kama it normally only checks up to that limit.
            subprocess.Popen(
                [sys.executable, '-c',
                 textwrap.dedent("""
                     agiza subprocess, sys
                     subprocess.Popen([sys.executable, %r] +
                                      [str(x) kila x kwenye range({max_fd})],
                                      close_fds=Kweli).wait()
                     """.format(max_fd=max_fd_open+1))],
                close_fds=Uongo).wait()
        mwishowe:
            resource.setrlimit(resource.RLIMIT_NOFILE, (rlim_cur, rlim_max))
        ''' % fd_status)], stdout=subprocess.PIPE)

        output, unused_stderr = p.communicate()
        output_lines = output.splitlines()
        self.assertEqual(len(output_lines), 2,
                         msg="expected exactly two lines of output:\n%r" % output)
        opened_fds = set(map(int, output_lines[0].strip().split(b',')))
        remaining_fds = set(map(int, output_lines[1].strip().split(b',')))

        self.assertUongo(remaining_fds & opened_fds,
                         msg="Some fds were left open.")


    # Mac OS X Tiger (10.4) has a kernel bug: sometimes, the file
    # descriptor of a pipe closed kwenye the parent process ni valid kwenye the
    # child process according to fstat(), but the mode of the file
    # descriptor ni invalid, na read ama write ashiria an error.
    @support.requires_mac_ver(10, 5)
    eleza test_pita_fds(self):
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        open_fds = set()

        kila x kwenye range(5):
            fds = os.pipe()
            self.addCleanup(os.close, fds[0])
            self.addCleanup(os.close, fds[1])
            os.set_inheritable(fds[0], Kweli)
            os.set_inheritable(fds[1], Kweli)
            open_fds.update(fds)

        kila fd kwenye open_fds:
            p = subprocess.Popen([sys.executable, fd_status],
                                 stdout=subprocess.PIPE, close_fds=Kweli,
                                 pita_fds=(fd, ))
            output, ignored = p.communicate()

            remaining_fds = set(map(int, output.split(b',')))
            to_be_closed = open_fds - {fd}

            self.assertIn(fd, remaining_fds, "fd to be pitaed sio pitaed")
            self.assertUongo(remaining_fds & to_be_closed,
                             "fd to be closed pitaed")

            # pita_fds overrides close_fds ukijumuisha a warning.
            ukijumuisha self.assertWarns(RuntimeWarning) kama context:
                self.assertUongo(subprocess.call(
                        [sys.executable, "-c", "agiza sys; sys.exit(0)"],
                        close_fds=Uongo, pita_fds=(fd, )))
            self.assertIn('overriding close_fds', str(context.warning))

    eleza test_pita_fds_inheritable(self):
        script = support.findfile("fd_status.py", subdir="subprocessdata")

        inheritable, non_inheritable = os.pipe()
        self.addCleanup(os.close, inheritable)
        self.addCleanup(os.close, non_inheritable)
        os.set_inheritable(inheritable, Kweli)
        os.set_inheritable(non_inheritable, Uongo)
        pita_fds = (inheritable, non_inheritable)
        args = [sys.executable, script]
        args += list(map(str, pita_fds))

        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE, close_fds=Kweli,
                             pita_fds=pita_fds)
        output, ignored = p.communicate()
        fds = set(map(int, output.split(b',')))

        # the inheritable file descriptor must be inherited, so its inheritable
        # flag must be set kwenye the child process after fork() na before exec()
        self.assertEqual(fds, set(pita_fds), "output=%a" % output)

        # inheritable flag must sio be changed kwenye the parent process
        self.assertEqual(os.get_inheritable(inheritable), Kweli)
        self.assertEqual(os.get_inheritable(non_inheritable), Uongo)


    # bpo-32270: Ensure that descriptors specified kwenye pita_fds
    # are inherited even ikiwa they are used kwenye redirections.
    # Contributed by @izbyshev.
    eleza test_pita_fds_redirected(self):
        """Regression test kila https://bugs.python.org/issue32270."""
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")
        pita_fds = []
        kila _ kwenye range(2):
            fd = os.open(os.devnull, os.O_RDWR)
            self.addCleanup(os.close, fd)
            pita_fds.append(fd)

        stdout_r, stdout_w = os.pipe()
        self.addCleanup(os.close, stdout_r)
        self.addCleanup(os.close, stdout_w)
        pita_fds.insert(1, stdout_w)

        ukijumuisha subprocess.Popen([sys.executable, fd_status],
                              stdin=pita_fds[0],
                              stdout=pita_fds[1],
                              stderr=pita_fds[2],
                              close_fds=Kweli,
                              pita_fds=pita_fds):
            output = os.read(stdout_r, 1024)
        fds = {int(num) kila num kwenye output.split(b',')}

        self.assertEqual(fds, {0, 1, 2} | frozenset(pita_fds), f"output={output!a}")


    eleza test_stdout_stdin_are_single_inout_fd(self):
        ukijumuisha io.open(os.devnull, "r+") kama inout:
            p = subprocess.Popen([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                                 stdout=inout, stdin=inout)
            p.wait()

    eleza test_stdout_stderr_are_single_inout_fd(self):
        ukijumuisha io.open(os.devnull, "r+") kama inout:
            p = subprocess.Popen([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                                 stdout=inout, stderr=inout)
            p.wait()

    eleza test_stderr_stdin_are_single_inout_fd(self):
        ukijumuisha io.open(os.devnull, "r+") kama inout:
            p = subprocess.Popen([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                                 stderr=inout, stdin=inout)
            p.wait()

    eleza test_wait_when_sigchild_ignored(self):
        # NOTE: sigchild_ignore.py may sio be an effective test on all OSes.
        sigchild_ignore = support.findfile("sigchild_ignore.py",
                                           subdir="subprocessdata")
        p = subprocess.Popen([sys.executable, sigchild_ignore],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        self.assertEqual(0, p.returncode, "sigchild_ignore.py exited"
                         " non-zero ukijumuisha this error:\n%s" %
                         stderr.decode('utf-8'))

    eleza test_select_unbuffered(self):
        # Issue #11459: bufsize=0 should really set the pipes as
        # unbuffered (and therefore let select() work properly).
        select = support.import_module("select")
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys;'
                              'sys.stdout.write("apple")'],
                             stdout=subprocess.PIPE,
                             bufsize=0)
        f = p.stdout
        self.addCleanup(f.close)
        jaribu:
            self.assertEqual(f.read(4), b"appl")
            self.assertIn(f, select.select([f], [], [], 0.0)[0])
        mwishowe:
            p.wait()

    eleza test_zombie_fast_process_del(self):
        # Issue #12650: on Unix, ikiwa Popen.__del__() was called before the
        # process exited, it wouldn't be added to subprocess._active, na would
        # remain a zombie.
        # spawn a Popen, na delete its reference before it exits
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza sys, time;'
                              'time.sleep(0.2)'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        ident = id(p)
        pid = p.pid
        ukijumuisha support.check_warnings(('', ResourceWarning)):
            p = Tupu

        ikiwa mswindows:
            # subprocess._active ni sio used on Windows na ni set to Tupu.
            self.assertIsTupu(subprocess._active)
        isipokua:
            # check that p ni kwenye the active processes list
            self.assertIn(ident, [id(o) kila o kwenye subprocess._active])

    eleza test_leak_fast_process_del_killed(self):
        # Issue #12650: on Unix, ikiwa Popen.__del__() was called before the
        # process exited, na the process got killed by a signal, it would never
        # be removed kutoka subprocess._active, which triggered a FD na memory
        # leak.
        # spawn a Popen, delete its reference na kill it
        p = subprocess.Popen([sys.executable, "-c",
                              'agiza time;'
                              'time.sleep(3)'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.addCleanup(p.stdout.close)
        self.addCleanup(p.stderr.close)
        ident = id(p)
        pid = p.pid
        ukijumuisha support.check_warnings(('', ResourceWarning)):
            p = Tupu

        os.kill(pid, signal.SIGKILL)
        ikiwa mswindows:
            # subprocess._active ni sio used on Windows na ni set to Tupu.
            self.assertIsTupu(subprocess._active)
        isipokua:
            # check that p ni kwenye the active processes list
            self.assertIn(ident, [id(o) kila o kwenye subprocess._active])

        # let some time kila the process to exit, na create a new Popen: this
        # should trigger the wait() of p
        time.sleep(0.2)
        ukijumuisha self.assertRaises(OSError):
            ukijumuisha subprocess.Popen(NONEXISTING_CMD,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) kama proc:
                pita
        # p should have been wait()ed on, na removed kutoka the _active list
        self.assertRaises(OSError, os.waitpid, pid, 0)
        ikiwa mswindows:
            # subprocess._active ni sio used on Windows na ni set to Tupu.
            self.assertIsTupu(subprocess._active)
        isipokua:
            self.assertNotIn(ident, [id(o) kila o kwenye subprocess._active])

    eleza test_close_fds_after_preexec(self):
        fd_status = support.findfile("fd_status.py", subdir="subprocessdata")

        # this FD ni used kama dup2() target by preexec_fn, na should be closed
        # kwenye the child process
        fd = os.dup(1)
        self.addCleanup(os.close, fd)

        p = subprocess.Popen([sys.executable, fd_status],
                             stdout=subprocess.PIPE, close_fds=Kweli,
                             preexec_fn=lambda: os.dup2(1, fd))
        output, ignored = p.communicate()

        remaining_fds = set(map(int, output.split(b',')))

        self.assertNotIn(fd, remaining_fds)

    @support.cpython_only
    eleza test_fork_exec(self):
        # Issue #22290: fork_exec() must sio crash on memory allocation failure
        # ama other errors
        agiza _posixsubprocess
        gc_enabled = gc.isenabled()
        jaribu:
            # Use a preexec function na enable the garbage collector
            # to force fork_exec() to re-enable the garbage collector
            # on error.
            func = lambda: Tupu
            gc.enable()

            kila args, exe_list, cwd, env_list kwenye (
                (123,      [b"exe"], Tupu, [b"env"]),
                ([b"arg"], 123,      Tupu, [b"env"]),
                ([b"arg"], [b"exe"], 123,  [b"env"]),
                ([b"arg"], [b"exe"], Tupu, 123),
            ):
                ukijumuisha self.assertRaises(TypeError):
                    _posixsubprocess.fork_exec(
                        args, exe_list,
                        Kweli, (), cwd, env_list,
                        -1, -1, -1, -1,
                        1, 2, 3, 4,
                        Kweli, Kweli, func)
        mwishowe:
            ikiwa sio gc_enabled:
                gc.disable()

    @support.cpython_only
    eleza test_fork_exec_sorted_fd_sanity_check(self):
        # Issue #23564: sanity check the fork_exec() fds_to_keep sanity check.
        agiza _posixsubprocess
        kundi BadInt:
            first = Kweli
            eleza __init__(self, value):
                self.value = value
            eleza __int__(self):
                ikiwa self.first:
                    self.first = Uongo
                    rudisha self.value
                ashiria ValueError

        gc_enabled = gc.isenabled()
        jaribu:
            gc.enable()

            kila fds_to_keep kwenye (
                (-1, 2, 3, 4, 5),  # Negative number.
                ('str', 4),  # Not an int.
                (18, 23, 42, 2**63),  # Out of range.
                (5, 4),  # Not sorted.
                (6, 7, 7, 8),  # Duplicate.
                (BadInt(1), BadInt(2)),
            ):
                ukijumuisha self.assertRaises(
                        ValueError,
                        msg='fds_to_keep={}'.format(fds_to_keep)) kama c:
                    _posixsubprocess.fork_exec(
                        [b"false"], [b"false"],
                        Kweli, fds_to_keep, Tupu, [b"env"],
                        -1, -1, -1, -1,
                        1, 2, 3, 4,
                        Kweli, Kweli, Tupu)
                self.assertIn('fds_to_keep', str(c.exception))
        mwishowe:
            ikiwa sio gc_enabled:
                gc.disable()

    eleza test_communicate_BrokenPipeError_stdin_close(self):
        # By sio setting stdout ama stderr ama a timeout we force the fast path
        # that just calls _stdin_write() internally due to our mock.
        proc = subprocess.Popen([sys.executable, '-c', 'pita'])
        ukijumuisha proc, mock.patch.object(proc, 'stdin') kama mock_proc_stdin:
            mock_proc_stdin.close.side_effect = BrokenPipeError
            proc.communicate()  # Should swallow BrokenPipeError kutoka close.
            mock_proc_stdin.close.assert_called_with()

    eleza test_communicate_BrokenPipeError_stdin_write(self):
        # By sio setting stdout ama stderr ama a timeout we force the fast path
        # that just calls _stdin_write() internally due to our mock.
        proc = subprocess.Popen([sys.executable, '-c', 'pita'])
        ukijumuisha proc, mock.patch.object(proc, 'stdin') kama mock_proc_stdin:
            mock_proc_stdin.write.side_effect = BrokenPipeError
            proc.communicate(b'stuff')  # Should swallow the BrokenPipeError.
            mock_proc_stdin.write.assert_called_once_with(b'stuff')
            mock_proc_stdin.close.assert_called_once_with()

    eleza test_communicate_BrokenPipeError_stdin_flush(self):
        # Setting stdin na stdout forces the ._communicate() code path.
        # python -h exits faster than python -c pita (but spams stdout).
        proc = subprocess.Popen([sys.executable, '-h'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        ukijumuisha proc, mock.patch.object(proc, 'stdin') kama mock_proc_stdin, \
                open(os.devnull, 'wb') kama dev_null:
            mock_proc_stdin.flush.side_effect = BrokenPipeError
            # because _communicate registers a selector using proc.stdin...
            mock_proc_stdin.fileno.return_value = dev_null.fileno()
            # _communicate() should swallow BrokenPipeError kutoka flush.
            proc.communicate(b'stuff')
            mock_proc_stdin.flush.assert_called_once_with()

    eleza test_communicate_BrokenPipeError_stdin_close_with_timeout(self):
        # Setting stdin na stdout forces the ._communicate() code path.
        # python -h exits faster than python -c pita (but spams stdout).
        proc = subprocess.Popen([sys.executable, '-h'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        ukijumuisha proc, mock.patch.object(proc, 'stdin') kama mock_proc_stdin:
            mock_proc_stdin.close.side_effect = BrokenPipeError
            # _communicate() should swallow BrokenPipeError kutoka close.
            proc.communicate(timeout=999)
            mock_proc_stdin.close.assert_called_once_with()

    @unittest.skipUnless(_testcapi ni sio Tupu
                         na hasattr(_testcapi, 'W_STOPCODE'),
                         'need _testcapi.W_STOPCODE')
    eleza test_stopped(self):
        """Test wait() behavior when waitpid returns WIFSTOPPED; issue29335."""
        args = [sys.executable, '-c', 'pita']
        proc = subprocess.Popen(args)

        # Wait until the real process completes to avoid zombie process
        pid = proc.pid
        pid, status = os.waitpid(pid, 0)
        self.assertEqual(status, 0)

        status = _testcapi.W_STOPCODE(3)
        ukijumuisha mock.patch('subprocess.os.waitpid', return_value=(pid, status)):
            returncode = proc.wait()

        self.assertEqual(returncode, -3)


@unittest.skipUnless(mswindows, "Windows specific tests")
kundi Win32ProcessTestCase(BaseTestCase):

    eleza test_startupinfo(self):
        # startupinfo argument
        # We uses hardcoded constants, because we do sio want to
        # depend on win32all.
        STARTF_USESHOWWINDOW = 1
        SW_MAXIMIZE = 3
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = SW_MAXIMIZE
        # Since Python ni a console process, it won't be affected
        # by wShowWindow, but the argument should be silently
        # ignored
        subprocess.call([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                        startupinfo=startupinfo)

    eleza test_startupinfo_keywords(self):
        # startupinfo argument
        # We use hardcoded constants, because we do sio want to
        # depend on win32all.
        STARTF_USERSHOWWINDOW = 1
        SW_MAXIMIZE = 3
        startupinfo = subprocess.STARTUPINFO(
            dwFlags=STARTF_USERSHOWWINDOW,
            wShowWindow=SW_MAXIMIZE
        )
        # Since Python ni a console process, it won't be affected
        # by wShowWindow, but the argument should be silently
        # ignored
        subprocess.call([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                        startupinfo=startupinfo)

    eleza test_startupinfo_copy(self):
        # bpo-34044: Popen must sio modify input STARTUPINFO structure
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        # Call Popen() twice ukijumuisha the same startupinfo object to make sure
        # that it's sio modified
        kila _ kwenye range(2):
            cmd = [sys.executable, "-c", "pita"]
            ukijumuisha open(os.devnull, 'w') kama null:
                proc = subprocess.Popen(cmd,
                                        stdout=null,
                                        stderr=subprocess.STDOUT,
                                        startupinfo=startupinfo)
                ukijumuisha proc:
                    proc.communicate()
                self.assertEqual(proc.returncode, 0)

            self.assertEqual(startupinfo.dwFlags,
                             subprocess.STARTF_USESHOWWINDOW)
            self.assertIsTupu(startupinfo.hStdInput)
            self.assertIsTupu(startupinfo.hStdOutput)
            self.assertIsTupu(startupinfo.hStdError)
            self.assertEqual(startupinfo.wShowWindow, subprocess.SW_HIDE)
            self.assertEqual(startupinfo.lpAttributeList, {"handle_list": []})

    eleza test_creationflags(self):
        # creationflags argument
        CREATE_NEW_CONSOLE = 16
        sys.stderr.write("    a DOS box should flash briefly ...\n")
        subprocess.call(sys.executable +
                        ' -c "agiza time; time.sleep(0.25)"',
                        creationflags=CREATE_NEW_CONSOLE)

    eleza test_invalid_args(self):
        # invalid arguments should ashiria ValueError
        self.assertRaises(ValueError, subprocess.call,
                          [sys.executable, "-c",
                           "agiza sys; sys.exit(47)"],
                          preexec_fn=lambda: 1)

    @support.cpython_only
    eleza test_issue31471(self):
        # There shouldn't be an assertion failure kwenye Popen() kwenye case the env
        # argument has a bad keys() method.
        kundi BadEnv(dict):
            keys = Tupu
        ukijumuisha self.assertRaises(TypeError):
            subprocess.Popen([sys.executable, "-c", "pita"], env=BadEnv())

    eleza test_close_fds(self):
        # close file descriptors
        rc = subprocess.call([sys.executable, "-c",
                              "agiza sys; sys.exit(47)"],
                              close_fds=Kweli)
        self.assertEqual(rc, 47)

    eleza test_close_fds_with_stdio(self):
        agiza msvcrt

        fds = os.pipe()
        self.addCleanup(os.close, fds[0])
        self.addCleanup(os.close, fds[1])

        handles = []
        kila fd kwenye fds:
            os.set_inheritable(fd, Kweli)
            handles.append(msvcrt.get_osfhandle(fd))

        p = subprocess.Popen([sys.executable, "-c",
                              "agiza msvcrt; andika(msvcrt.open_osfhandle({}, 0))".format(handles[0])],
                             stdout=subprocess.PIPE, close_fds=Uongo)
        stdout, stderr = p.communicate()
        self.assertEqual(p.returncode, 0)
        int(stdout.strip())  # Check that stdout ni an integer

        p = subprocess.Popen([sys.executable, "-c",
                              "agiza msvcrt; andika(msvcrt.open_osfhandle({}, 0))".format(handles[0])],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=Kweli)
        stdout, stderr = p.communicate()
        self.assertEqual(p.returncode, 1)
        self.assertIn(b"OSError", stderr)

        # The same kama the previous call, but ukijumuisha an empty handle_list
        handle_list = []
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.lpAttributeList = {"handle_list": handle_list}
        p = subprocess.Popen([sys.executable, "-c",
                              "agiza msvcrt; andika(msvcrt.open_osfhandle({}, 0))".format(handles[0])],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             startupinfo=startupinfo, close_fds=Kweli)
        stdout, stderr = p.communicate()
        self.assertEqual(p.returncode, 1)
        self.assertIn(b"OSError", stderr)

        # Check kila a warning due to using handle_list na close_fds=Uongo
        ukijumuisha support.check_warnings((".*overriding close_fds", RuntimeWarning)):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.lpAttributeList = {"handle_list": handles[:]}
            p = subprocess.Popen([sys.executable, "-c",
                                  "agiza msvcrt; andika(msvcrt.open_osfhandle({}, 0))".format(handles[0])],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 startupinfo=startupinfo, close_fds=Uongo)
            stdout, stderr = p.communicate()
            self.assertEqual(p.returncode, 0)

    eleza test_empty_attribute_list(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.lpAttributeList = {}
        subprocess.call([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                        startupinfo=startupinfo)

    eleza test_empty_handle_list(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.lpAttributeList = {"handle_list": []}
        subprocess.call([sys.executable, "-c", "agiza sys; sys.exit(0)"],
                        startupinfo=startupinfo)

    eleza test_shell_sequence(self):
        # Run command through the shell (sequence)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "physalis"
        p = subprocess.Popen(["set"], shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        ukijumuisha p:
            self.assertIn(b"physalis", p.stdout.read())

    eleza test_shell_string(self):
        # Run command through the shell (string)
        newenv = os.environ.copy()
        newenv["FRUIT"] = "physalis"
        p = subprocess.Popen("set", shell=1,
                             stdout=subprocess.PIPE,
                             env=newenv)
        ukijumuisha p:
            self.assertIn(b"physalis", p.stdout.read())

    eleza test_shell_encodings(self):
        # Run command through the shell (string)
        kila enc kwenye ['ansi', 'oem']:
            newenv = os.environ.copy()
            newenv["FRUIT"] = "physalis"
            p = subprocess.Popen("set", shell=1,
                                 stdout=subprocess.PIPE,
                                 env=newenv,
                                 encoding=enc)
            ukijumuisha p:
                self.assertIn("physalis", p.stdout.read(), enc)

    eleza test_call_string(self):
        # call() function ukijumuisha string argument on Windows
        rc = subprocess.call(sys.executable +
                             ' -c "agiza sys; sys.exit(47)"')
        self.assertEqual(rc, 47)

    eleza _kill_process(self, method, *args):
        # Some win32 buildbot raises EOFError ikiwa stdin ni inherited
        p = subprocess.Popen([sys.executable, "-c", """ikiwa 1:
                             agiza sys, time
                             sys.stdout.write('x\\n')
                             sys.stdout.flush()
                             time.sleep(30)
                             """],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        ukijumuisha p:
            # Wait kila the interpreter to be completely initialized before
            # sending any signal.
            p.stdout.read(1)
            getattr(p, method)(*args)
            _, stderr = p.communicate()
            self.assertStderrEqual(stderr, b'')
            returncode = p.wait()
        self.assertNotEqual(returncode, 0)

    eleza _kill_dead_process(self, method, *args):
        p = subprocess.Popen([sys.executable, "-c", """ikiwa 1:
                             agiza sys, time
                             sys.stdout.write('x\\n')
                             sys.stdout.flush()
                             sys.exit(42)
                             """],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        ukijumuisha p:
            # Wait kila the interpreter to be completely initialized before
            # sending any signal.
            p.stdout.read(1)
            # The process should end after this
            time.sleep(1)
            # This shouldn't ashiria even though the child ni now dead
            getattr(p, method)(*args)
            _, stderr = p.communicate()
            self.assertStderrEqual(stderr, b'')
            rc = p.wait()
        self.assertEqual(rc, 42)

    eleza test_send_signal(self):
        self._kill_process('send_signal', signal.SIGTERM)

    eleza test_kill(self):
        self._kill_process('kill')

    eleza test_terminate(self):
        self._kill_process('terminate')

    eleza test_send_signal_dead(self):
        self._kill_dead_process('send_signal', signal.SIGTERM)

    eleza test_kill_dead(self):
        self._kill_dead_process('kill')

    eleza test_terminate_dead(self):
        self._kill_dead_process('terminate')

kundi MiscTests(unittest.TestCase):

    kundi RecordingPopen(subprocess.Popen):
        """A Popen that saves a reference to each instance kila testing."""
        instances_created = []

        eleza __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.instances_created.append(self)

    @mock.patch.object(subprocess.Popen, "_communicate")
    eleza _test_keyboardinterrupt_no_kill(self, popener, mock__communicate,
                                        **kwargs):
        """Fake a SIGINT happening during Popen._communicate() na ._wait().

        This avoids the need to actually try na get test environments to send
        na receive signals reliably across platforms.  The net effect of a ^C
        happening during a blocking subprocess execution which we want to clean
        up kutoka ni a KeyboardInterrupt coming out of communicate() ama wait().
        """

        mock__communicate.side_effect = KeyboardInterrupt
        jaribu:
            ukijumuisha mock.patch.object(subprocess.Popen, "_wait") kama mock__wait:
                # We patch out _wait() kama no signal was involved so the
                # child process isn't actually going to exit rapidly.
                mock__wait.side_effect = KeyboardInterrupt
                ukijumuisha mock.patch.object(subprocess, "Popen",
                                       self.RecordingPopen):
                    ukijumuisha self.assertRaises(KeyboardInterrupt):
                        popener([sys.executable, "-c",
                                 "agiza time\ntime.sleep(9)\nagiza sys\n"
                                 "sys.stderr.write('\\n!runaway child!\\n')"],
                                stdout=subprocess.DEVNULL, **kwargs)
                kila call kwenye mock__wait.call_args_list[1:]:
                    self.assertNotEqual(
                            call, mock.call(timeout=Tupu),
                            "no open-ended wait() after the first allowed: "
                            f"{mock__wait.call_args_list}")
                sigint_calls = []
                kila call kwenye mock__wait.call_args_list:
                    ikiwa call == mock.call(timeout=0.25):  # kutoka Popen.__init__
                        sigint_calls.append(call)
                self.assertLessEqual(mock__wait.call_count, 2,
                                     msg=mock__wait.call_args_list)
                self.assertEqual(len(sigint_calls), 1,
                                 msg=mock__wait.call_args_list)
        mwishowe:
            # cleanup the forgotten (due to our mocks) child process
            process = self.RecordingPopen.instances_created.pop()
            process.kill()
            process.wait()
            self.assertEqual([], self.RecordingPopen.instances_created)

    eleza test_call_keyboardinterrupt_no_kill(self):
        self._test_keyboardinterrupt_no_kill(subprocess.call, timeout=6.282)

    eleza test_run_keyboardinterrupt_no_kill(self):
        self._test_keyboardinterrupt_no_kill(subprocess.run, timeout=6.282)

    eleza test_context_manager_keyboardinterrupt_no_kill(self):
        eleza popen_via_context_manager(*args, **kwargs):
            ukijumuisha subprocess.Popen(*args, **kwargs) kama unused_process:
                ashiria KeyboardInterrupt  # Test how __exit__ handles ^C.
        self._test_keyboardinterrupt_no_kill(popen_via_context_manager)

    eleza test_getoutput(self):
        self.assertEqual(subprocess.getoutput('echo xyzzy'), 'xyzzy')
        self.assertEqual(subprocess.getstatusoutput('echo xyzzy'),
                         (0, 'xyzzy'))

        # we use mkdtemp kwenye the next line to create an empty directory
        # under our exclusive control; kutoka that, we can invent a pathname
        # that we _know_ won't exist.  This ni guaranteed to fail.
        dir = Tupu
        jaribu:
            dir = tempfile.mkdtemp()
            name = os.path.join(dir, "foo")
            status, output = subprocess.getstatusoutput(
                ("type " ikiwa mswindows isipokua "cat ") + name)
            self.assertNotEqual(status, 0)
        mwishowe:
            ikiwa dir ni sio Tupu:
                os.rmdir(dir)

    eleza test__all__(self):
        """Ensure that __all__ ni populated properly."""
        intentionally_excluded = {"list2cmdline", "Handle"}
        exported = set(subprocess.__all__)
        possible_exports = set()
        agiza types
        kila name, value kwenye subprocess.__dict__.items():
            ikiwa name.startswith('_'):
                endelea
            ikiwa isinstance(value, (types.ModuleType,)):
                endelea
            possible_exports.add(name)
        self.assertEqual(exported, possible_exports - intentionally_excluded)


@unittest.skipUnless(hasattr(selectors, 'PollSelector'),
                     "Test needs selectors.PollSelector")
kundi ProcessTestCaseNoPoll(ProcessTestCase):
    eleza setUp(self):
        self.orig_selector = subprocess._PopenSelector
        subprocess._PopenSelector = selectors.SelectSelector
        ProcessTestCase.setUp(self)

    eleza tearDown(self):
        subprocess._PopenSelector = self.orig_selector
        ProcessTestCase.tearDown(self)


@unittest.skipUnless(mswindows, "Windows-specific tests")
kundi CommandsWithSpaces (BaseTestCase):

    eleza setUp(self):
        super().setUp()
        f, fname = tempfile.mkstemp(".py", "te st")
        self.fname = fname.lower ()
        os.write(f, b"agiza sys;"
                    b"sys.stdout.write('%d %s' % (len(sys.argv), [a.lower () kila a kwenye sys.argv]))"
        )
        os.close(f)

    eleza tearDown(self):
        os.remove(self.fname)
        super().tearDown()

    eleza with_spaces(self, *args, **kwargs):
        kwargs['stdout'] = subprocess.PIPE
        p = subprocess.Popen(*args, **kwargs)
        ukijumuisha p:
            self.assertEqual(
              p.stdout.read ().decode("mbcs"),
              "2 [%r, 'ab cd']" % self.fname
            )

    eleza test_shell_string_with_spaces(self):
        # call() function ukijumuisha string argument ukijumuisha spaces on Windows
        self.with_spaces('"%s" "%s" "%s"' % (sys.executable, self.fname,
                                             "ab cd"), shell=1)

    eleza test_shell_sequence_with_spaces(self):
        # call() function ukijumuisha sequence argument ukijumuisha spaces on Windows
        self.with_spaces([sys.executable, self.fname, "ab cd"], shell=1)

    eleza test_noshell_string_with_spaces(self):
        # call() function ukijumuisha string argument ukijumuisha spaces on Windows
        self.with_spaces('"%s" "%s" "%s"' % (sys.executable, self.fname,
                             "ab cd"))

    eleza test_noshell_sequence_with_spaces(self):
        # call() function ukijumuisha sequence argument ukijumuisha spaces on Windows
        self.with_spaces([sys.executable, self.fname, "ab cd"])


kundi ContextManagerTests(BaseTestCase):

    eleza test_pipe(self):
        ukijumuisha subprocess.Popen([sys.executable, "-c",
                               "agiza sys;"
                               "sys.stdout.write('stdout');"
                               "sys.stderr.write('stderr');"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) kama proc:
            self.assertEqual(proc.stdout.read(), b"stdout")
            self.assertStderrEqual(proc.stderr.read(), b"stderr")

        self.assertKweli(proc.stdout.closed)
        self.assertKweli(proc.stderr.closed)

    eleza test_returncode(self):
        ukijumuisha subprocess.Popen([sys.executable, "-c",
                               "agiza sys; sys.exit(100)"]) kama proc:
            pita
        # __exit__ calls wait(), so the returncode should be set
        self.assertEqual(proc.returncode, 100)

    eleza test_communicate_stdin(self):
        ukijumuisha subprocess.Popen([sys.executable, "-c",
                              "agiza sys;"
                              "sys.exit(sys.stdin.read() == 'context')"],
                             stdin=subprocess.PIPE) kama proc:
            proc.communicate(b"context")
            self.assertEqual(proc.returncode, 1)

    eleza test_invalid_args(self):
        ukijumuisha self.assertRaises(NONEXISTING_ERRORS):
            ukijumuisha subprocess.Popen(NONEXISTING_CMD,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) kama proc:
                pita

    eleza test_broken_pipe_cleanup(self):
        """Broken pipe error should sio prevent wait() (Issue 21619)"""
        proc = subprocess.Popen([sys.executable, '-c', 'pita'],
                                stdin=subprocess.PIPE,
                                bufsize=support.PIPE_MAX_SIZE*2)
        proc = proc.__enter__()
        # Prepare to send enough data to overflow any OS pipe buffering na
        # guarantee a broken pipe error. Data ni held kwenye BufferedWriter
        # buffer until closed.
        proc.stdin.write(b'x' * support.PIPE_MAX_SIZE)
        self.assertIsTupu(proc.returncode)
        # EPIPE expected under POSIX; EINVAL under Windows
        self.assertRaises(OSError, proc.__exit__, Tupu, Tupu, Tupu)
        self.assertEqual(proc.returncode, 0)
        self.assertKweli(proc.stdin.closed)


ikiwa __name__ == "__main__":
    unittest.main()
