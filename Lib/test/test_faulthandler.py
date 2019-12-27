kutoka contextlib agiza contextmanager
agiza datetime
agiza faulthandler
agiza os
agiza signal
agiza subprocess
agiza sys
agiza sysconfig
kutoka test agiza support
kutoka test.support agiza script_helper, is_android
agiza tempfile
agiza unittest
kutoka textwrap agiza dedent

try:
    agiza _testcapi
except ImportError:
    _testcapi = None

TIMEOUT = 0.5
MS_WINDOWS = (os.name == 'nt')
_cflags = sysconfig.get_config_var('CFLAGS') or ''
_config_args = sysconfig.get_config_var('CONFIG_ARGS') or ''
UB_SANITIZER = (
    '-fsanitize=undefined' in _cflags or
    '--with-undefined-behavior-sanitizer' in _config_args
)
MEMORY_SANITIZER = (
    '-fsanitize=memory' in _cflags or
    '--with-memory-sanitizer' in _config_args
)


eleza expected_traceback(lineno1, lineno2, header, min_count=1):
    regex = header
    regex += '  File "<string>", line %s in func\n' % lineno1
    regex += '  File "<string>", line %s in <module>' % lineno2
    ikiwa 1 < min_count:
        rudisha '^' + (regex + '\n') * (min_count - 1) + regex
    else:
        rudisha '^' + regex + '$'

eleza skip_segfault_on_android(test):
    # Issue #32138: Raising SIGSEGV on Android may not cause a crash.
    rudisha unittest.skipIf(is_android,
                           'raising SIGSEGV on Android is unreliable')(test)

@contextmanager
eleza temporary_filename():
    filename = tempfile.mktemp()
    try:
        yield filename
    finally:
        support.unlink(filename)

kundi FaultHandlerTests(unittest.TestCase):
    eleza get_output(self, code, filename=None, fd=None):
        """
        Run the specified code in Python (in a new child process) and read the
        output kutoka the standard error or kutoka a file (ikiwa filename is set).
        Return the output lines as a list.

        Strip the reference count kutoka the standard error for Python debug
        build, and replace "Current thread 0x00007f8d8fbd9700" by "Current
        thread XXX".
        """
        code = dedent(code).strip()
        pass_fds = []
        ikiwa fd is not None:
            pass_fds.append(fd)
        with support.SuppressCrashReport():
            process = script_helper.spawn_python('-c', code, pass_fds=pass_fds)
            with process:
                stdout, stderr = process.communicate()
                exitcode = process.wait()
        output = support.strip_python_stderr(stdout)
        output = output.decode('ascii', 'backslashreplace')
        ikiwa filename:
            self.assertEqual(output, '')
            with open(filename, "rb") as fp:
                output = fp.read()
            output = output.decode('ascii', 'backslashreplace')
        elikiwa fd is not None:
            self.assertEqual(output, '')
            os.lseek(fd, os.SEEK_SET, 0)
            with open(fd, "rb", closefd=False) as fp:
                output = fp.read()
            output = output.decode('ascii', 'backslashreplace')
        rudisha output.splitlines(), exitcode

    eleza check_error(self, code, line_number, fatal_error, *,
                    filename=None, all_threads=True, other_regex=None,
                    fd=None, know_current_thread=True,
                    py_fatal_error=False):
        """
        Check that the fault handler for fatal errors is enabled and check the
        traceback kutoka the child process output.

        Raise an error ikiwa the output doesn't match the expected format.
        """
        ikiwa all_threads:
            ikiwa know_current_thread:
                header = 'Current thread 0x[0-9a-f]+'
            else:
                header = 'Thread 0x[0-9a-f]+'
        else:
            header = 'Stack'
        regex = r"""
            (?m)^{fatal_error}

            {header} \(most recent call first\):
              File "<string>", line {lineno} in <module>
            """
        ikiwa py_fatal_error:
            fatal_error += "\nPython runtime state: initialized"
        regex = dedent(regex).format(
            lineno=line_number,
            fatal_error=fatal_error,
            header=header).strip()
        ikiwa other_regex:
            regex += '|' + other_regex
        output, exitcode = self.get_output(code, filename=filename, fd=fd)
        output = '\n'.join(output)
        self.assertRegex(output, regex)
        self.assertNotEqual(exitcode, 0)

    eleza check_fatal_error(self, code, line_number, name_regex, **kw):
        fatal_error = 'Fatal Python error: %s' % name_regex
        self.check_error(code, line_number, fatal_error, **kw)

    eleza check_windows_exception(self, code, line_number, name_regex, **kw):
        fatal_error = 'Windows fatal exception: %s' % name_regex
        self.check_error(code, line_number, fatal_error, **kw)

    @unittest.skipIf(sys.platform.startswith('aix'),
                     "the first page of memory is a mapped read-only on AIX")
    eleza test_read_null(self):
        ikiwa not MS_WINDOWS:
            self.check_fatal_error("""
                agiza faulthandler
                faulthandler.enable()
                faulthandler._read_null()
                """,
                3,
                # Issue #12700: Read NULL raises SIGILL on Mac OS X Lion
                '(?:Segmentation fault'
                    '|Bus error'
                    '|Illegal instruction)')
        else:
            self.check_windows_exception("""
                agiza faulthandler
                faulthandler.enable()
                faulthandler._read_null()
                """,
                3,
                'access violation')

    @skip_segfault_on_android
    eleza test_sigsegv(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler._sigsegv()
            """,
            3,
            'Segmentation fault')

    eleza test_fatal_error_c_thread(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler._fatal_error_c_thread()
            """,
            3,
            'in new thread',
            know_current_thread=False,
            py_fatal_error=True)

    eleza test_sigabrt(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler._sigabrt()
            """,
            3,
            'Aborted')

    @unittest.skipIf(sys.platform == 'win32',
                     "SIGFPE cannot be caught on Windows")
    eleza test_sigfpe(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler._sigfpe()
            """,
            3,
            'Floating point exception')

    @unittest.skipIf(_testcapi is None, 'need _testcapi')
    @unittest.skipUnless(hasattr(signal, 'SIGBUS'), 'need signal.SIGBUS')
    @skip_segfault_on_android
    eleza test_sigbus(self):
        self.check_fatal_error("""
            agiza faulthandler
            agiza signal

            faulthandler.enable()
            signal.raise_signal(signal.SIGBUS)
            """,
            5,
            'Bus error')

    @unittest.skipIf(_testcapi is None, 'need _testcapi')
    @unittest.skipUnless(hasattr(signal, 'SIGILL'), 'need signal.SIGILL')
    @skip_segfault_on_android
    eleza test_sigill(self):
        self.check_fatal_error("""
            agiza faulthandler
            agiza signal

            faulthandler.enable()
            signal.raise_signal(signal.SIGILL)
            """,
            5,
            'Illegal instruction')

    eleza test_fatal_error(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler._fatal_error(b'xyz')
            """,
            2,
            'xyz',
            py_fatal_error=True)

    eleza test_fatal_error_without_gil(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler._fatal_error(b'xyz', True)
            """,
            2,
            'xyz',
            py_fatal_error=True)

    @unittest.skipIf(sys.platform.startswith('openbsd'),
                     "Issue #12868: sigaltstack() doesn't work on "
                     "OpenBSD ikiwa Python is compiled with pthread")
    @unittest.skipIf(not hasattr(faulthandler, '_stack_overflow'),
                     'need faulthandler._stack_overflow()')
    eleza test_stack_overflow(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler._stack_overflow()
            """,
            3,
            '(?:Segmentation fault|Bus error)',
            other_regex='unable to raise a stack overflow')

    @skip_segfault_on_android
    eleza test_gil_released(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler._sigsegv(True)
            """,
            3,
            'Segmentation fault')

    @unittest.skipIf(UB_SANITIZER or MEMORY_SANITIZER,
                     "sanitizer builds change crashing process output.")
    @skip_segfault_on_android
    eleza test_enable_file(self):
        with temporary_filename() as filename:
            self.check_fatal_error("""
                agiza faulthandler
                output = open({filename}, 'wb')
                faulthandler.enable(output)
                faulthandler._sigsegv()
                """.format(filename=repr(filename)),
                4,
                'Segmentation fault',
                filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support pass_fds on Windows")
    @unittest.skipIf(UB_SANITIZER or MEMORY_SANITIZER,
                     "sanitizer builds change crashing process output.")
    @skip_segfault_on_android
    eleza test_enable_fd(self):
        with tempfile.TemporaryFile('wb+') as fp:
            fd = fp.fileno()
            self.check_fatal_error("""
                agiza faulthandler
                agiza sys
                faulthandler.enable(%s)
                faulthandler._sigsegv()
                """ % fd,
                4,
                'Segmentation fault',
                fd=fd)

    @skip_segfault_on_android
    eleza test_enable_single_thread(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable(all_threads=False)
            faulthandler._sigsegv()
            """,
            3,
            'Segmentation fault',
            all_threads=False)

    @skip_segfault_on_android
    eleza test_disable(self):
        code = """
            agiza faulthandler
            faulthandler.enable()
            faulthandler.disable()
            faulthandler._sigsegv()
            """
        not_expected = 'Fatal Python error'
        stderr, exitcode = self.get_output(code)
        stderr = '\n'.join(stderr)
        self.assertTrue(not_expected not in stderr,
                     "%r is present in %r" % (not_expected, stderr))
        self.assertNotEqual(exitcode, 0)

    eleza test_is_enabled(self):
        orig_stderr = sys.stderr
        try:
            # regrtest may replace sys.stderr by io.StringIO object, but
            # faulthandler.enable() requires that sys.stderr has a fileno()
            # method
            sys.stderr = sys.__stderr__

            was_enabled = faulthandler.is_enabled()
            try:
                faulthandler.enable()
                self.assertTrue(faulthandler.is_enabled())
                faulthandler.disable()
                self.assertFalse(faulthandler.is_enabled())
            finally:
                ikiwa was_enabled:
                    faulthandler.enable()
                else:
                    faulthandler.disable()
        finally:
            sys.stderr = orig_stderr

    eleza test_disabled_by_default(self):
        # By default, the module should be disabled
        code = "agiza faulthandler; andika(faulthandler.is_enabled())"
        args = (sys.executable, "-E", "-c", code)
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args)
        self.assertEqual(output.rstrip(), b"False")

    eleza test_sys_xoptions(self):
        # Test python -X faulthandler
        code = "agiza faulthandler; andika(faulthandler.is_enabled())"
        args = filter(None, (sys.executable,
                             "-E" ikiwa sys.flags.ignore_environment else "",
                             "-X", "faulthandler", "-c", code))
        env = os.environ.copy()
        env.pop("PYTHONFAULTHANDLER", None)
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"True")

    eleza test_env_var(self):
        # empty env var
        code = "agiza faulthandler; andika(faulthandler.is_enabled())"
        args = (sys.executable, "-c", code)
        env = dict(os.environ)
        env['PYTHONFAULTHANDLER'] = ''
        env['PYTHONDEVMODE'] = ''
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"False")

        # non-empty env var
        env = dict(os.environ)
        env['PYTHONFAULTHANDLER'] = '1'
        env['PYTHONDEVMODE'] = ''
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"True")

    eleza check_dump_traceback(self, *, filename=None, fd=None):
        """
        Explicitly call dump_traceback() function and check its output.
        Raise an error ikiwa the output doesn't match the expected format.
        """
        code = """
            agiza faulthandler

            filename = {filename!r}
            fd = {fd}

            eleza funcB():
                ikiwa filename:
                    with open(filename, "wb") as fp:
                        faulthandler.dump_traceback(fp, all_threads=False)
                elikiwa fd is not None:
                    faulthandler.dump_traceback(fd,
                                                all_threads=False)
                else:
                    faulthandler.dump_traceback(all_threads=False)

            eleza funcA():
                funcB()

            funcA()
            """
        code = code.format(
            filename=filename,
            fd=fd,
        )
        ikiwa filename:
            lineno = 9
        elikiwa fd is not None:
            lineno = 11
        else:
            lineno = 14
        expected = [
            'Stack (most recent call first):',
            '  File "<string>", line %s in funcB' % lineno,
            '  File "<string>", line 17 in funcA',
            '  File "<string>", line 19 in <module>'
        ]
        trace, exitcode = self.get_output(code, filename, fd)
        self.assertEqual(trace, expected)
        self.assertEqual(exitcode, 0)

    eleza test_dump_traceback(self):
        self.check_dump_traceback()

    eleza test_dump_traceback_file(self):
        with temporary_filename() as filename:
            self.check_dump_traceback(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support pass_fds on Windows")
    eleza test_dump_traceback_fd(self):
        with tempfile.TemporaryFile('wb+') as fp:
            self.check_dump_traceback(fd=fp.fileno())

    eleza test_truncate(self):
        maxlen = 500
        func_name = 'x' * (maxlen + 50)
        truncated = 'x' * maxlen + '...'
        code = """
            agiza faulthandler

            eleza {func_name}():
                faulthandler.dump_traceback(all_threads=False)

            {func_name}()
            """
        code = code.format(
            func_name=func_name,
        )
        expected = [
            'Stack (most recent call first):',
            '  File "<string>", line 4 in %s' % truncated,
            '  File "<string>", line 6 in <module>'
        ]
        trace, exitcode = self.get_output(code)
        self.assertEqual(trace, expected)
        self.assertEqual(exitcode, 0)

    eleza check_dump_traceback_threads(self, filename):
        """
        Call explicitly dump_traceback(all_threads=True) and check the output.
        Raise an error ikiwa the output doesn't match the expected format.
        """
        code = """
            agiza faulthandler
            kutoka threading agiza Thread, Event
            agiza time

            eleza dump():
                ikiwa {filename}:
                    with open({filename}, "wb") as fp:
                        faulthandler.dump_traceback(fp, all_threads=True)
                else:
                    faulthandler.dump_traceback(all_threads=True)

            kundi Waiter(Thread):
                # avoid blocking ikiwa the main thread raises an exception.
                daemon = True

                eleza __init__(self):
                    Thread.__init__(self)
                    self.running = Event()
                    self.stop = Event()

                eleza run(self):
                    self.running.set()
                    self.stop.wait()

            waiter = Waiter()
            waiter.start()
            waiter.running.wait()
            dump()
            waiter.stop.set()
            waiter.join()
            """
        code = code.format(filename=repr(filename))
        output, exitcode = self.get_output(code, filename)
        output = '\n'.join(output)
        ikiwa filename:
            lineno = 8
        else:
            lineno = 10
        regex = r"""
            ^Thread 0x[0-9a-f]+ \(most recent call first\):
            (?:  File ".*threading.py", line [0-9]+ in [_a-z]+
            ){{1,3}}  File "<string>", line 23 in run
              File ".*threading.py", line [0-9]+ in _bootstrap_inner
              File ".*threading.py", line [0-9]+ in _bootstrap

            Current thread 0x[0-9a-f]+ \(most recent call first\):
              File "<string>", line {lineno} in dump
              File "<string>", line 28 in <module>$
            """
        regex = dedent(regex.format(lineno=lineno)).strip()
        self.assertRegex(output, regex)
        self.assertEqual(exitcode, 0)

    eleza test_dump_traceback_threads(self):
        self.check_dump_traceback_threads(None)

    eleza test_dump_traceback_threads_file(self):
        with temporary_filename() as filename:
            self.check_dump_traceback_threads(filename)

    @unittest.skipIf(not hasattr(faulthandler, 'dump_traceback_later'),
                     'need faulthandler.dump_traceback_later()')
    eleza check_dump_traceback_later(self, repeat=False, cancel=False, loops=1,
                                   *, filename=None, fd=None):
        """
        Check how many times the traceback is written in timeout x 2.5 seconds,
        or timeout x 3.5 seconds ikiwa cancel is True: 1, 2 or 3 times depending
        on repeat and cancel options.

        Raise an error ikiwa the output doesn't match the expect format.
        """
        timeout_str = str(datetime.timedelta(seconds=TIMEOUT))
        code = """
            agiza faulthandler
            agiza time
            agiza sys

            timeout = {timeout}
            repeat = {repeat}
            cancel = {cancel}
            loops = {loops}
            filename = {filename!r}
            fd = {fd}

            eleza func(timeout, repeat, cancel, file, loops):
                for loop in range(loops):
                    faulthandler.dump_traceback_later(timeout, repeat=repeat, file=file)
                    ikiwa cancel:
                        faulthandler.cancel_dump_traceback_later()
                    time.sleep(timeout * 5)
                    faulthandler.cancel_dump_traceback_later()

            ikiwa filename:
                file = open(filename, "wb")
            elikiwa fd is not None:
                file = sys.stderr.fileno()
            else:
                file = None
            func(timeout, repeat, cancel, file, loops)
            ikiwa filename:
                file.close()
            """
        code = code.format(
            timeout=TIMEOUT,
            repeat=repeat,
            cancel=cancel,
            loops=loops,
            filename=filename,
            fd=fd,
        )
        trace, exitcode = self.get_output(code, filename)
        trace = '\n'.join(trace)

        ikiwa not cancel:
            count = loops
            ikiwa repeat:
                count *= 2
            header = r'Timeout \(%s\)!\nThread 0x[0-9a-f]+ \(most recent call first\):\n' % timeout_str
            regex = expected_traceback(17, 26, header, min_count=count)
            self.assertRegex(trace, regex)
        else:
            self.assertEqual(trace, '')
        self.assertEqual(exitcode, 0)

    eleza test_dump_traceback_later(self):
        self.check_dump_traceback_later()

    eleza test_dump_traceback_later_repeat(self):
        self.check_dump_traceback_later(repeat=True)

    eleza test_dump_traceback_later_cancel(self):
        self.check_dump_traceback_later(cancel=True)

    eleza test_dump_traceback_later_file(self):
        with temporary_filename() as filename:
            self.check_dump_traceback_later(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support pass_fds on Windows")
    eleza test_dump_traceback_later_fd(self):
        with tempfile.TemporaryFile('wb+') as fp:
            self.check_dump_traceback_later(fd=fp.fileno())

    eleza test_dump_traceback_later_twice(self):
        self.check_dump_traceback_later(loops=2)

    @unittest.skipIf(not hasattr(faulthandler, "register"),
                     "need faulthandler.register")
    eleza check_register(self, filename=False, all_threads=False,
                       unregister=False, chain=False, fd=None):
        """
        Register a handler displaying the traceback on a user signal. Raise the
        signal and check the written traceback.

        If chain is True, check that the previous signal handler is called.

        Raise an error ikiwa the output doesn't match the expected format.
        """
        signum = signal.SIGUSR1
        code = """
            agiza faulthandler
            agiza os
            agiza signal
            agiza sys

            all_threads = {all_threads}
            signum = {signum}
            unregister = {unregister}
            chain = {chain}
            filename = {filename!r}
            fd = {fd}

            eleza func(signum):
                os.kill(os.getpid(), signum)

            eleza handler(signum, frame):
                handler.called = True
            handler.called = False

            ikiwa filename:
                file = open(filename, "wb")
            elikiwa fd is not None:
                file = sys.stderr.fileno()
            else:
                file = None
            ikiwa chain:
                signal.signal(signum, handler)
            faulthandler.register(signum, file=file,
                                  all_threads=all_threads, chain={chain})
            ikiwa unregister:
                faulthandler.unregister(signum)
            func(signum)
            ikiwa chain and not handler.called:
                ikiwa file is not None:
                    output = file
                else:
                    output = sys.stderr
                andika("Error: signal handler not called!", file=output)
                exitcode = 1
            else:
                exitcode = 0
            ikiwa filename:
                file.close()
            sys.exit(exitcode)
            """
        code = code.format(
            all_threads=all_threads,
            signum=signum,
            unregister=unregister,
            chain=chain,
            filename=filename,
            fd=fd,
        )
        trace, exitcode = self.get_output(code, filename)
        trace = '\n'.join(trace)
        ikiwa not unregister:
            ikiwa all_threads:
                regex = r'Current thread 0x[0-9a-f]+ \(most recent call first\):\n'
            else:
                regex = r'Stack \(most recent call first\):\n'
            regex = expected_traceback(14, 32, regex)
            self.assertRegex(trace, regex)
        else:
            self.assertEqual(trace, '')
        ikiwa unregister:
            self.assertNotEqual(exitcode, 0)
        else:
            self.assertEqual(exitcode, 0)

    eleza test_register(self):
        self.check_register()

    eleza test_unregister(self):
        self.check_register(unregister=True)

    eleza test_register_file(self):
        with temporary_filename() as filename:
            self.check_register(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support pass_fds on Windows")
    eleza test_register_fd(self):
        with tempfile.TemporaryFile('wb+') as fp:
            self.check_register(fd=fp.fileno())

    eleza test_register_threads(self):
        self.check_register(all_threads=True)

    eleza test_register_chain(self):
        self.check_register(chain=True)

    @contextmanager
    eleza check_stderr_none(self):
        stderr = sys.stderr
        try:
            sys.stderr = None
            with self.assertRaises(RuntimeError) as cm:
                yield
            self.assertEqual(str(cm.exception), "sys.stderr is None")
        finally:
            sys.stderr = stderr

    eleza test_stderr_None(self):
        # Issue #21497: provide a helpful error ikiwa sys.stderr is None,
        # instead of just an attribute error: "None has no attribute fileno".
        with self.check_stderr_none():
            faulthandler.enable()
        with self.check_stderr_none():
            faulthandler.dump_traceback()
        ikiwa hasattr(faulthandler, 'dump_traceback_later'):
            with self.check_stderr_none():
                faulthandler.dump_traceback_later(1e-3)
        ikiwa hasattr(faulthandler, "register"):
            with self.check_stderr_none():
                faulthandler.register(signal.SIGUSR1)

    @unittest.skipUnless(MS_WINDOWS, 'specific to Windows')
    eleza test_raise_exception(self):
        for exc, name in (
            ('EXCEPTION_ACCESS_VIOLATION', 'access violation'),
            ('EXCEPTION_INT_DIVIDE_BY_ZERO', 'int divide by zero'),
            ('EXCEPTION_STACK_OVERFLOW', 'stack overflow'),
        ):
            self.check_windows_exception(f"""
                agiza faulthandler
                faulthandler.enable()
                faulthandler._raise_exception(faulthandler._{exc})
                """,
                3,
                name)

    @unittest.skipUnless(MS_WINDOWS, 'specific to Windows')
    eleza test_ignore_exception(self):
        for exc_code in (
            0xE06D7363,   # MSC exception ("Emsc")
            0xE0434352,   # COM Callable Runtime exception ("ECCR")
        ):
            code = f"""
                    agiza faulthandler
                    faulthandler.enable()
                    faulthandler._raise_exception({exc_code})
                    """
            code = dedent(code)
            output, exitcode = self.get_output(code)
            self.assertEqual(output, [])
            self.assertEqual(exitcode, exc_code)

    @unittest.skipUnless(MS_WINDOWS, 'specific to Windows')
    eleza test_raise_nonfatal_exception(self):
        # These exceptions are not strictly errors. Letting
        # faulthandler display the traceback when they are
        # raised is likely to result in noise. However, they
        # may still terminate the process ikiwa there is no
        # handler installed for them (which there typically
        # is, e.g. for debug messages).
        for exc in (
            0x00000000,
            0x34567890,
            0x40000000,
            0x40001000,
            0x70000000,
            0x7FFFFFFF,
        ):
            output, exitcode = self.get_output(f"""
                agiza faulthandler
                faulthandler.enable()
                faulthandler._raise_exception(0x{exc:x})
                """
            )
            self.assertEqual(output, [])
            # On Windows older than 7 SP1, the actual exception code has
            # bit 29 cleared.
            self.assertIn(exitcode,
                          (exc, exc & ~0x10000000))

    @unittest.skipUnless(MS_WINDOWS, 'specific to Windows')
    eleza test_disable_windows_exc_handler(self):
        code = dedent("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler.disable()
            code = faulthandler._EXCEPTION_ACCESS_VIOLATION
            faulthandler._raise_exception(code)
        """)
        output, exitcode = self.get_output(code)
        self.assertEqual(output, [])
        self.assertEqual(exitcode, 0xC0000005)


ikiwa __name__ == "__main__":
    unittest.main()
