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

jaribu:
    agiza _testcapi
tatizo ImportError:
    _testcapi = Tupu

TIMEOUT = 0.5
MS_WINDOWS = (os.name == 'nt')
_cflags = sysconfig.get_config_var('CFLAGS') ama ''
_config_args = sysconfig.get_config_var('CONFIG_ARGS') ama ''
UB_SANITIZER = (
    '-fsanitize=undefined' kwenye _cflags ama
    '--with-undefined-behavior-sanitizer' kwenye _config_args
)
MEMORY_SANITIZER = (
    '-fsanitize=memory' kwenye _cflags ama
    '--with-memory-sanitizer' kwenye _config_args
)


eleza expected_traceback(lineno1, lineno2, header, min_count=1):
    regex = header
    regex += '  File "<string>", line %s kwenye func\n' % lineno1
    regex += '  File "<string>", line %s kwenye <module>' % lineno2
    ikiwa 1 < min_count:
        rudisha '^' + (regex + '\n') * (min_count - 1) + regex
    isipokua:
        rudisha '^' + regex + '$'

eleza skip_segfault_on_android(test):
    # Issue #32138: Raising SIGSEGV on Android may sio cause a crash.
    rudisha unittest.skipIf(is_android,
                           'raising SIGSEGV on Android ni unreliable')(test)

@contextmanager
eleza temporary_filename():
    filename = tempfile.mktemp()
    jaribu:
        tuma filename
    mwishowe:
        support.unlink(filename)

kundi FaultHandlerTests(unittest.TestCase):
    eleza get_output(self, code, filename=Tupu, fd=Tupu):
        """
        Run the specified code kwenye Python (in a new child process) na read the
        output kutoka the standard error ama kutoka a file (ikiwa filename ni set).
        Return the output lines kama a list.

        Strip the reference count kutoka the standard error kila Python debug
        build, na replace "Current thread 0x00007f8d8fbd9700" by "Current
        thread XXX".
        """
        code = dedent(code).strip()
        pita_fds = []
        ikiwa fd ni sio Tupu:
            pita_fds.append(fd)
        ukijumuisha support.SuppressCrashReport():
            process = script_helper.spawn_python('-c', code, pita_fds=pita_fds)
            ukijumuisha process:
                stdout, stderr = process.communicate()
                exitcode = process.wait()
        output = support.strip_python_stderr(stdout)
        output = output.decode('ascii', 'backslashreplace')
        ikiwa filename:
            self.assertEqual(output, '')
            ukijumuisha open(filename, "rb") kama fp:
                output = fp.read()
            output = output.decode('ascii', 'backslashreplace')
        lasivyo fd ni sio Tupu:
            self.assertEqual(output, '')
            os.lseek(fd, os.SEEK_SET, 0)
            ukijumuisha open(fd, "rb", closefd=Uongo) kama fp:
                output = fp.read()
            output = output.decode('ascii', 'backslashreplace')
        rudisha output.splitlines(), exitcode

    eleza check_error(self, code, line_number, fatal_error, *,
                    filename=Tupu, all_threads=Kweli, other_regex=Tupu,
                    fd=Tupu, know_current_thread=Kweli,
                    py_fatal_error=Uongo):
        """
        Check that the fault handler kila fatal errors ni enabled na check the
        traceback kutoka the child process output.

        Raise an error ikiwa the output doesn't match the expected format.
        """
        ikiwa all_threads:
            ikiwa know_current_thread:
                header = 'Current thread 0x[0-9a-f]+'
            isipokua:
                header = 'Thread 0x[0-9a-f]+'
        isipokua:
            header = 'Stack'
        regex = r"""
            (?m)^{fatal_error}

            {header} \(most recent call first\):
              File "<string>", line {lineno} kwenye <module>
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
                     "the first page of memory ni a mapped read-only on AIX")
    eleza test_read_null(self):
        ikiwa sio MS_WINDOWS:
            self.check_fatal_error("""
                agiza faulthandler
                faulthandler.enable()
                faulthandler._read_null()
                """,
                3,
                # Issue #12700: Read NULL ashirias SIGILL on Mac OS X Lion
                '(?:Segmentation fault'
                    '|Bus error'
                    '|Illegal instruction)')
        isipokua:
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
            know_current_thread=Uongo,
            py_fatal_error=Kweli)

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

    @unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
    @unittest.skipUnless(hasattr(signal, 'SIGBUS'), 'need signal.SIGBUS')
    @skip_segfault_on_android
    eleza test_sigbus(self):
        self.check_fatal_error("""
            agiza faulthandler
            agiza signal

            faulthandler.enable()
            signal.ashiria_signal(signal.SIGBUS)
            """,
            5,
            'Bus error')

    @unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
    @unittest.skipUnless(hasattr(signal, 'SIGILL'), 'need signal.SIGILL')
    @skip_segfault_on_android
    eleza test_sigill(self):
        self.check_fatal_error("""
            agiza faulthandler
            agiza signal

            faulthandler.enable()
            signal.ashiria_signal(signal.SIGILL)
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
            py_fatal_error=Kweli)

    eleza test_fatal_error_without_gil(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler._fatal_error(b'xyz', Kweli)
            """,
            2,
            'xyz',
            py_fatal_error=Kweli)

    @unittest.skipIf(sys.platform.startswith('openbsd'),
                     "Issue #12868: sigaltstack() doesn't work on "
                     "OpenBSD ikiwa Python ni compiled ukijumuisha pthread")
    @unittest.skipIf(sio hasattr(faulthandler, '_stack_overflow'),
                     'need faulthandler._stack_overflow()')
    eleza test_stack_overflow(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler._stack_overflow()
            """,
            3,
            '(?:Segmentation fault|Bus error)',
            other_regex='unable to ashiria a stack overflow')

    @skip_segfault_on_android
    eleza test_gil_released(self):
        self.check_fatal_error("""
            agiza faulthandler
            faulthandler.enable()
            faulthandler._sigsegv(Kweli)
            """,
            3,
            'Segmentation fault')

    @unittest.skipIf(UB_SANITIZER ama MEMORY_SANITIZER,
                     "sanitizer builds change crashing process output.")
    @skip_segfault_on_android
    eleza test_enable_file(self):
        ukijumuisha temporary_filename() kama filename:
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
                     "subprocess doesn't support pita_fds on Windows")
    @unittest.skipIf(UB_SANITIZER ama MEMORY_SANITIZER,
                     "sanitizer builds change crashing process output.")
    @skip_segfault_on_android
    eleza test_enable_fd(self):
        ukijumuisha tempfile.TemporaryFile('wb+') kama fp:
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
            faulthandler.enable(all_threads=Uongo)
            faulthandler._sigsegv()
            """,
            3,
            'Segmentation fault',
            all_threads=Uongo)

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
        self.assertKweli(not_expected haiko kwenye stderr,
                     "%r ni present kwenye %r" % (not_expected, stderr))
        self.assertNotEqual(exitcode, 0)

    eleza test_is_enabled(self):
        orig_stderr = sys.stderr
        jaribu:
            # regrtest may replace sys.stderr by io.StringIO object, but
            # faulthandler.enable() requires that sys.stderr has a fileno()
            # method
            sys.stderr = sys.__stderr__

            was_enabled = faulthandler.is_enabled()
            jaribu:
                faulthandler.enable()
                self.assertKweli(faulthandler.is_enabled())
                faulthandler.disable()
                self.assertUongo(faulthandler.is_enabled())
            mwishowe:
                ikiwa was_enabled:
                    faulthandler.enable()
                isipokua:
                    faulthandler.disable()
        mwishowe:
            sys.stderr = orig_stderr

    eleza test_disabled_by_default(self):
        # By default, the module should be disabled
        code = "agiza faulthandler; andika(faulthandler.is_enabled())"
        args = (sys.executable, "-E", "-c", code)
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args)
        self.assertEqual(output.rstrip(), b"Uongo")

    eleza test_sys_xoptions(self):
        # Test python -X faulthandler
        code = "agiza faulthandler; andika(faulthandler.is_enabled())"
        args = filter(Tupu, (sys.executable,
                             "-E" ikiwa sys.flags.ignore_environment isipokua "",
                             "-X", "faulthandler", "-c", code))
        env = os.environ.copy()
        env.pop("PYTHONFAULTHANDLER", Tupu)
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"Kweli")

    eleza test_env_var(self):
        # empty env var
        code = "agiza faulthandler; andika(faulthandler.is_enabled())"
        args = (sys.executable, "-c", code)
        env = dict(os.environ)
        env['PYTHONFAULTHANDLER'] = ''
        env['PYTHONDEVMODE'] = ''
        # don't use assert_python_ok() because it always enables faulthandler
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"Uongo")

        # non-empty env var
        env = dict(os.environ)
        env['PYTHONFAULTHANDLER'] = '1'
        env['PYTHONDEVMODE'] = ''
        output = subprocess.check_output(args, env=env)
        self.assertEqual(output.rstrip(), b"Kweli")

    eleza check_dump_traceback(self, *, filename=Tupu, fd=Tupu):
        """
        Explicitly call dump_traceback() function na check its output.
        Raise an error ikiwa the output doesn't match the expected format.
        """
        code = """
            agiza faulthandler

            filename = {filename!r}
            fd = {fd}

            eleza funcB():
                ikiwa filename:
                    ukijumuisha open(filename, "wb") kama fp:
                        faulthandler.dump_traceback(fp, all_threads=Uongo)
                lasivyo fd ni sio Tupu:
                    faulthandler.dump_traceback(fd,
                                                all_threads=Uongo)
                isipokua:
                    faulthandler.dump_traceback(all_threads=Uongo)

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
        lasivyo fd ni sio Tupu:
            lineno = 11
        isipokua:
            lineno = 14
        expected = [
            'Stack (most recent call first):',
            '  File "<string>", line %s kwenye funcB' % lineno,
            '  File "<string>", line 17 kwenye funcA',
            '  File "<string>", line 19 kwenye <module>'
        ]
        trace, exitcode = self.get_output(code, filename, fd)
        self.assertEqual(trace, expected)
        self.assertEqual(exitcode, 0)

    eleza test_dump_traceback(self):
        self.check_dump_traceback()

    eleza test_dump_traceback_file(self):
        ukijumuisha temporary_filename() kama filename:
            self.check_dump_traceback(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support pita_fds on Windows")
    eleza test_dump_traceback_fd(self):
        ukijumuisha tempfile.TemporaryFile('wb+') kama fp:
            self.check_dump_traceback(fd=fp.fileno())

    eleza test_truncate(self):
        maxlen = 500
        func_name = 'x' * (maxlen + 50)
        truncated = 'x' * maxlen + '...'
        code = """
            agiza faulthandler

            eleza {func_name}():
                faulthandler.dump_traceback(all_threads=Uongo)

            {func_name}()
            """
        code = code.format(
            func_name=func_name,
        )
        expected = [
            'Stack (most recent call first):',
            '  File "<string>", line 4 kwenye %s' % truncated,
            '  File "<string>", line 6 kwenye <module>'
        ]
        trace, exitcode = self.get_output(code)
        self.assertEqual(trace, expected)
        self.assertEqual(exitcode, 0)

    eleza check_dump_traceback_threads(self, filename):
        """
        Call explicitly dump_traceback(all_threads=Kweli) na check the output.
        Raise an error ikiwa the output doesn't match the expected format.
        """
        code = """
            agiza faulthandler
            kutoka threading agiza Thread, Event
            agiza time

            eleza dump():
                ikiwa {filename}:
                    ukijumuisha open({filename}, "wb") kama fp:
                        faulthandler.dump_traceback(fp, all_threads=Kweli)
                isipokua:
                    faulthandler.dump_traceback(all_threads=Kweli)

            kundi Waiter(Thread):
                # avoid blocking ikiwa the main thread ashirias an exception.
                daemon = Kweli

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
        isipokua:
            lineno = 10
        regex = r"""
            ^Thread 0x[0-9a-f]+ \(most recent call first\):
            (?:  File ".*threading.py", line [0-9]+ kwenye [_a-z]+
            ){{1,3}}  File "<string>", line 23 kwenye run
              File ".*threading.py", line [0-9]+ kwenye _bootstrap_inner
              File ".*threading.py", line [0-9]+ kwenye _bootstrap

            Current thread 0x[0-9a-f]+ \(most recent call first\):
              File "<string>", line {lineno} kwenye dump
              File "<string>", line 28 kwenye <module>$
            """
        regex = dedent(regex.format(lineno=lineno)).strip()
        self.assertRegex(output, regex)
        self.assertEqual(exitcode, 0)

    eleza test_dump_traceback_threads(self):
        self.check_dump_traceback_threads(Tupu)

    eleza test_dump_traceback_threads_file(self):
        ukijumuisha temporary_filename() kama filename:
            self.check_dump_traceback_threads(filename)

    @unittest.skipIf(sio hasattr(faulthandler, 'dump_traceback_later'),
                     'need faulthandler.dump_traceback_later()')
    eleza check_dump_traceback_later(self, repeat=Uongo, cancel=Uongo, loops=1,
                                   *, filename=Tupu, fd=Tupu):
        """
        Check how many times the traceback ni written kwenye timeout x 2.5 seconds,
        ama timeout x 3.5 seconds ikiwa cancel ni Kweli: 1, 2 ama 3 times depending
        on repeat na cancel options.

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
                kila loop kwenye range(loops):
                    faulthandler.dump_traceback_later(timeout, repeat=repeat, file=file)
                    ikiwa cancel:
                        faulthandler.cancel_dump_traceback_later()
                    time.sleep(timeout * 5)
                    faulthandler.cancel_dump_traceback_later()

            ikiwa filename:
                file = open(filename, "wb")
            lasivyo fd ni sio Tupu:
                file = sys.stderr.fileno()
            isipokua:
                file = Tupu
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

        ikiwa sio cancel:
            count = loops
            ikiwa repeat:
                count *= 2
            header = r'Timeout \(%s\)!\nThread 0x[0-9a-f]+ \(most recent call first\):\n' % timeout_str
            regex = expected_traceback(17, 26, header, min_count=count)
            self.assertRegex(trace, regex)
        isipokua:
            self.assertEqual(trace, '')
        self.assertEqual(exitcode, 0)

    eleza test_dump_traceback_later(self):
        self.check_dump_traceback_later()

    eleza test_dump_traceback_later_repeat(self):
        self.check_dump_traceback_later(repeat=Kweli)

    eleza test_dump_traceback_later_cancel(self):
        self.check_dump_traceback_later(cancel=Kweli)

    eleza test_dump_traceback_later_file(self):
        ukijumuisha temporary_filename() kama filename:
            self.check_dump_traceback_later(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support pita_fds on Windows")
    eleza test_dump_traceback_later_fd(self):
        ukijumuisha tempfile.TemporaryFile('wb+') kama fp:
            self.check_dump_traceback_later(fd=fp.fileno())

    eleza test_dump_traceback_later_twice(self):
        self.check_dump_traceback_later(loops=2)

    @unittest.skipIf(sio hasattr(faulthandler, "register"),
                     "need faulthandler.register")
    eleza check_register(self, filename=Uongo, all_threads=Uongo,
                       unregister=Uongo, chain=Uongo, fd=Tupu):
        """
        Register a handler displaying the traceback on a user signal. Raise the
        signal na check the written traceback.

        If chain ni Kweli, check that the previous signal handler ni called.

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
                handler.called = Kweli
            handler.called = Uongo

            ikiwa filename:
                file = open(filename, "wb")
            lasivyo fd ni sio Tupu:
                file = sys.stderr.fileno()
            isipokua:
                file = Tupu
            ikiwa chain:
                signal.signal(signum, handler)
            faulthandler.register(signum, file=file,
                                  all_threads=all_threads, chain={chain})
            ikiwa unregister:
                faulthandler.unregister(signum)
            func(signum)
            ikiwa chain na sio handler.called:
                ikiwa file ni sio Tupu:
                    output = file
                isipokua:
                    output = sys.stderr
                andika("Error: signal handler sio called!", file=output)
                exitcode = 1
            isipokua:
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
        ikiwa sio unregister:
            ikiwa all_threads:
                regex = r'Current thread 0x[0-9a-f]+ \(most recent call first\):\n'
            isipokua:
                regex = r'Stack \(most recent call first\):\n'
            regex = expected_traceback(14, 32, regex)
            self.assertRegex(trace, regex)
        isipokua:
            self.assertEqual(trace, '')
        ikiwa unregister:
            self.assertNotEqual(exitcode, 0)
        isipokua:
            self.assertEqual(exitcode, 0)

    eleza test_register(self):
        self.check_register()

    eleza test_unregister(self):
        self.check_register(unregister=Kweli)

    eleza test_register_file(self):
        ukijumuisha temporary_filename() kama filename:
            self.check_register(filename=filename)

    @unittest.skipIf(sys.platform == "win32",
                     "subprocess doesn't support pita_fds on Windows")
    eleza test_register_fd(self):
        ukijumuisha tempfile.TemporaryFile('wb+') kama fp:
            self.check_register(fd=fp.fileno())

    eleza test_register_threads(self):
        self.check_register(all_threads=Kweli)

    eleza test_register_chain(self):
        self.check_register(chain=Kweli)

    @contextmanager
    eleza check_stderr_none(self):
        stderr = sys.stderr
        jaribu:
            sys.stderr = Tupu
            ukijumuisha self.assertRaises(RuntimeError) kama cm:
                tuma
            self.assertEqual(str(cm.exception), "sys.stderr ni Tupu")
        mwishowe:
            sys.stderr = stderr

    eleza test_stderr_Tupu(self):
        # Issue #21497: provide a helpful error ikiwa sys.stderr ni Tupu,
        # instead of just an attribute error: "Tupu has no attribute fileno".
        ukijumuisha self.check_stderr_none():
            faulthandler.enable()
        ukijumuisha self.check_stderr_none():
            faulthandler.dump_traceback()
        ikiwa hasattr(faulthandler, 'dump_traceback_later'):
            ukijumuisha self.check_stderr_none():
                faulthandler.dump_traceback_later(1e-3)
        ikiwa hasattr(faulthandler, "register"):
            ukijumuisha self.check_stderr_none():
                faulthandler.register(signal.SIGUSR1)

    @unittest.skipUnless(MS_WINDOWS, 'specific to Windows')
    eleza test_ashiria_exception(self):
        kila exc, name kwenye (
            ('EXCEPTION_ACCESS_VIOLATION', 'access violation'),
            ('EXCEPTION_INT_DIVIDE_BY_ZERO', 'int divide by zero'),
            ('EXCEPTION_STACK_OVERFLOW', 'stack overflow'),
        ):
            self.check_windows_exception(f"""
                agiza faulthandler
                faulthandler.enable()
                faulthandler._ashiria_exception(faulthandler._{exc})
                """,
                3,
                name)

    @unittest.skipUnless(MS_WINDOWS, 'specific to Windows')
    eleza test_ignore_exception(self):
        kila exc_code kwenye (
            0xE06D7363,   # MSC exception ("Emsc")
            0xE0434352,   # COM Callable Runtime exception ("ECCR")
        ):
            code = f"""
                    agiza faulthandler
                    faulthandler.enable()
                    faulthandler._ashiria_exception({exc_code})
                    """
            code = dedent(code)
            output, exitcode = self.get_output(code)
            self.assertEqual(output, [])
            self.assertEqual(exitcode, exc_code)

    @unittest.skipUnless(MS_WINDOWS, 'specific to Windows')
    eleza test_ashiria_nonfatal_exception(self):
        # These exceptions are sio strictly errors. Letting
        # faulthandler display the traceback when they are
        # ashiriad ni likely to result kwenye noise. However, they
        # may still terminate the process ikiwa there ni no
        # handler installed kila them (which there typically
        # is, e.g. kila debug messages).
        kila exc kwenye (
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
                faulthandler._ashiria_exception(0x{exc:x})
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
            faulthandler._ashiria_exception(code)
        """)
        output, exitcode = self.get_output(code)
        self.assertEqual(output, [])
        self.assertEqual(exitcode, 0xC0000005)


ikiwa __name__ == "__main__":
    unittest.main()
