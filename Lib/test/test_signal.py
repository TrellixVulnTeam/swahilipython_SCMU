agiza errno
agiza os
agiza random
agiza signal
agiza socket
agiza statistics
agiza subprocess
agiza sys
agiza time
agiza unittest
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok, spawn_python
jaribu:
    agiza _testcapi
tatizo ImportError:
    _testcapi = Tupu


kundi GenericTests(unittest.TestCase):

    eleza test_enums(self):
        kila name kwenye dir(signal):
            sig = getattr(signal, name)
            ikiwa name kwenye {'SIG_DFL', 'SIG_IGN'}:
                self.assertIsInstance(sig, signal.Handlers)
            lasivyo name kwenye {'SIG_BLOCK', 'SIG_UNBLOCK', 'SIG_SETMASK'}:
                self.assertIsInstance(sig, signal.Sigmasks)
            lasivyo name.startswith('SIG') na sio name.startswith('SIG_'):
                self.assertIsInstance(sig, signal.Signals)
            lasivyo name.startswith('CTRL_'):
                self.assertIsInstance(sig, signal.Signals)
                self.assertEqual(sys.platform, "win32")


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
kundi PosixTests(unittest.TestCase):
    eleza trivial_signal_handler(self, *args):
        pita

    eleza test_out_of_range_signal_number_ashirias_error(self):
        self.assertRaises(ValueError, signal.getsignal, 4242)

        self.assertRaises(ValueError, signal.signal, 4242,
                          self.trivial_signal_handler)

        self.assertRaises(ValueError, signal.strsignal, 4242)

    eleza test_setting_signal_handler_to_none_ashirias_error(self):
        self.assertRaises(TypeError, signal.signal,
                          signal.SIGUSR1, Tupu)

    eleza test_getsignal(self):
        hup = signal.signal(signal.SIGHUP, self.trivial_signal_handler)
        self.assertIsInstance(hup, signal.Handlers)
        self.assertEqual(signal.getsignal(signal.SIGHUP),
                         self.trivial_signal_handler)
        signal.signal(signal.SIGHUP, hup)
        self.assertEqual(signal.getsignal(signal.SIGHUP), hup)

    eleza test_strsignal(self):
        self.assertIn("Interrupt", signal.strsignal(signal.SIGINT))
        self.assertIn("Terminated", signal.strsignal(signal.SIGTERM))
        self.assertIn("Hangup", signal.strsignal(signal.SIGHUP))

    # Issue 3864, unknown ikiwa this affects earlier versions of freebsd also
    eleza test_interprocess_signal(self):
        dirname = os.path.dirname(__file__)
        script = os.path.join(dirname, 'signalinterproctester.py')
        assert_python_ok(script)

    eleza test_valid_signals(self):
        s = signal.valid_signals()
        self.assertIsInstance(s, set)
        self.assertIn(signal.Signals.SIGINT, s)
        self.assertIn(signal.Signals.SIGALRM, s)
        self.assertNotIn(0, s)
        self.assertNotIn(signal.NSIG, s)
        self.assertLess(len(s), signal.NSIG)

    @unittest.skipUnless(sys.executable, "sys.executable required.")
    eleza test_keyboard_interrupt_exit_code(self):
        """KeyboardInterrupt triggers exit via SIGINT."""
        process = subprocess.run(
                [sys.executable, "-c",
                 "agiza os, signal, time\n"
                 "os.kill(os.getpid(), signal.SIGINT)\n"
                 "kila _ kwenye range(999): time.sleep(0.01)"],
                stderr=subprocess.PIPE)
        self.assertIn(b"KeyboardInterrupt", process.stderr)
        self.assertEqual(process.returncode, -signal.SIGINT)
        # Caveat: The exit code ni insufficient to guarantee we actually died
        # via a signal.  POSIX shells do more than look at the 8 bit value.
        # Writing an automation friendly test of an interactive shell
        # to confirm that our process died via a SIGINT proved too complex.


@unittest.skipUnless(sys.platform == "win32", "Windows specific")
kundi WindowsSignalTests(unittest.TestCase):

    eleza test_valid_signals(self):
        s = signal.valid_signals()
        self.assertIsInstance(s, set)
        self.assertGreaterEqual(len(s), 6)
        self.assertIn(signal.Signals.SIGINT, s)
        self.assertNotIn(0, s)
        self.assertNotIn(signal.NSIG, s)
        self.assertLess(len(s), signal.NSIG)

    eleza test_issue9324(self):
        # Updated kila issue #10003, adding SIGBREAK
        handler = lambda x, y: Tupu
        checked = set()
        kila sig kwenye (signal.SIGABRT, signal.SIGBREAK, signal.SIGFPE,
                    signal.SIGILL, signal.SIGINT, signal.SIGSEGV,
                    signal.SIGTERM):
            # Set na then reset a handler kila signals that work on windows.
            # Issue #18396, only kila signals without a C-level handler.
            ikiwa signal.getsignal(sig) ni sio Tupu:
                signal.signal(sig, signal.signal(sig, handler))
                checked.add(sig)
        # Issue #18396: Ensure the above loop at least tested *something*
        self.assertKweli(checked)

        ukijumuisha self.assertRaises(ValueError):
            signal.signal(-1, handler)

        ukijumuisha self.assertRaises(ValueError):
            signal.signal(7, handler)

    @unittest.skipUnless(sys.executable, "sys.executable required.")
    eleza test_keyboard_interrupt_exit_code(self):
        """KeyboardInterrupt triggers an exit using STATUS_CONTROL_C_EXIT."""
        # We don't test via os.kill(os.getpid(), signal.CTRL_C_EVENT) here
        # kama that requires setting up a console control handler kwenye a child
        # kwenye its own process group.  Doable, but quite complicated.  (see
        # @eryksun on https://github.com/python/cpython/pull/11862)
        process = subprocess.run(
                [sys.executable, "-c", "ashiria KeyboardInterrupt"],
                stderr=subprocess.PIPE)
        self.assertIn(b"KeyboardInterrupt", process.stderr)
        STATUS_CONTROL_C_EXIT = 0xC000013A
        self.assertEqual(process.returncode, STATUS_CONTROL_C_EXIT)


kundi WakeupFDTests(unittest.TestCase):

    eleza test_invalid_call(self):
        # First parameter ni positional-only
        ukijumuisha self.assertRaises(TypeError):
            signal.set_wakeup_fd(signum=signal.SIGINT)

        # warn_on_full_buffer ni a keyword-only parameter
        ukijumuisha self.assertRaises(TypeError):
            signal.set_wakeup_fd(signal.SIGINT, Uongo)

    eleza test_invalid_fd(self):
        fd = support.make_bad_fd()
        self.assertRaises((ValueError, OSError),
                          signal.set_wakeup_fd, fd)

    eleza test_invalid_socket(self):
        sock = socket.socket()
        fd = sock.fileno()
        sock.close()
        self.assertRaises((ValueError, OSError),
                          signal.set_wakeup_fd, fd)

    eleza test_set_wakeup_fd_result(self):
        r1, w1 = os.pipe()
        self.addCleanup(os.close, r1)
        self.addCleanup(os.close, w1)
        r2, w2 = os.pipe()
        self.addCleanup(os.close, r2)
        self.addCleanup(os.close, w2)

        ikiwa hasattr(os, 'set_blocking'):
            os.set_blocking(w1, Uongo)
            os.set_blocking(w2, Uongo)

        signal.set_wakeup_fd(w1)
        self.assertEqual(signal.set_wakeup_fd(w2), w1)
        self.assertEqual(signal.set_wakeup_fd(-1), w2)
        self.assertEqual(signal.set_wakeup_fd(-1), -1)

    eleza test_set_wakeup_fd_socket_result(self):
        sock1 = socket.socket()
        self.addCleanup(sock1.close)
        sock1.setblocking(Uongo)
        fd1 = sock1.fileno()

        sock2 = socket.socket()
        self.addCleanup(sock2.close)
        sock2.setblocking(Uongo)
        fd2 = sock2.fileno()

        signal.set_wakeup_fd(fd1)
        self.assertEqual(signal.set_wakeup_fd(fd2), fd1)
        self.assertEqual(signal.set_wakeup_fd(-1), fd2)
        self.assertEqual(signal.set_wakeup_fd(-1), -1)

    # On Windows, files are always blocking na Windows does sio provide a
    # function to test ikiwa a socket ni kwenye non-blocking mode.
    @unittest.skipIf(sys.platform == "win32", "tests specific to POSIX")
    eleza test_set_wakeup_fd_blocking(self):
        rfd, wfd = os.pipe()
        self.addCleanup(os.close, rfd)
        self.addCleanup(os.close, wfd)

        # fd must be non-blocking
        os.set_blocking(wfd, Kweli)
        ukijumuisha self.assertRaises(ValueError) kama cm:
            signal.set_wakeup_fd(wfd)
        self.assertEqual(str(cm.exception),
                         "the fd %s must be kwenye non-blocking mode" % wfd)

        # non-blocking ni ok
        os.set_blocking(wfd, Uongo)
        signal.set_wakeup_fd(wfd)
        signal.set_wakeup_fd(-1)


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
kundi WakeupSignalTests(unittest.TestCase):
    @unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
    eleza check_wakeup(self, test_body, *signals, ordered=Kweli):
        # use a subprocess to have only one thread
        code = """ikiwa 1:
        agiza _testcapi
        agiza os
        agiza signal
        agiza struct

        signals = {!r}

        eleza handler(signum, frame):
            pita

        eleza check_signum(signals):
            data = os.read(read, len(signals)+1)
            ashiriad = struct.unpack('%uB' % len(data), data)
            ikiwa sio {!r}:
                ashiriad = set(ashiriad)
                signals = set(signals)
            ikiwa ashiriad != signals:
                ashiria Exception("%r != %r" % (ashiriad, signals))

        {}

        signal.signal(signal.SIGALRM, handler)
        read, write = os.pipe()
        os.set_blocking(write, Uongo)
        signal.set_wakeup_fd(write)

        test()
        check_signum(signals)

        os.close(read)
        os.close(write)
        """.format(tuple(map(int, signals)), ordered, test_body)

        assert_python_ok('-c', code)

    @unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
    eleza test_wakeup_write_error(self):
        # Issue #16105: write() errors kwenye the C signal handler should not
        # pita silently.
        # Use a subprocess to have only one thread.
        code = """ikiwa 1:
        agiza _testcapi
        agiza errno
        agiza os
        agiza signal
        agiza sys
        kutoka test.support agiza captured_stderr

        eleza handler(signum, frame):
            1/0

        signal.signal(signal.SIGALRM, handler)
        r, w = os.pipe()
        os.set_blocking(r, Uongo)

        # Set wakeup_fd a read-only file descriptor to trigger the error
        signal.set_wakeup_fd(r)
        jaribu:
            ukijumuisha captured_stderr() kama err:
                signal.ashiria_signal(signal.SIGALRM)
        tatizo ZeroDivisionError:
            # An ignored exception should have been printed out on stderr
            err = err.getvalue()
            ikiwa ('Exception ignored when trying to write to the signal wakeup fd'
                haiko kwenye err):
                ashiria AssertionError(err)
            ikiwa ('OSError: [Errno %d]' % errno.EBADF) haiko kwenye err:
                ashiria AssertionError(err)
        isipokua:
            ashiria AssertionError("ZeroDivisionError sio ashiriad")

        os.close(r)
        os.close(w)
        """
        r, w = os.pipe()
        jaribu:
            os.write(r, b'x')
        tatizo OSError:
            pita
        isipokua:
            self.skipTest("OS doesn't report write() error on the read end of a pipe")
        mwishowe:
            os.close(r)
            os.close(w)

        assert_python_ok('-c', code)

    eleza test_wakeup_fd_early(self):
        self.check_wakeup("""eleza test():
            agiza select
            agiza time

            TIMEOUT_FULL = 10
            TIMEOUT_HALF = 5

            kundi InterruptSelect(Exception):
                pita

            eleza handler(signum, frame):
                ashiria InterruptSelect
            signal.signal(signal.SIGALRM, handler)

            signal.alarm(1)

            # We attempt to get a signal during the sleep,
            # before select ni called
            jaribu:
                select.select([], [], [], TIMEOUT_FULL)
            tatizo InterruptSelect:
                pita
            isipokua:
                ashiria Exception("select() was sio interrupted")

            before_time = time.monotonic()
            select.select([read], [], [], TIMEOUT_FULL)
            after_time = time.monotonic()
            dt = after_time - before_time
            ikiwa dt >= TIMEOUT_HALF:
                ashiria Exception("%s >= %s" % (dt, TIMEOUT_HALF))
        """, signal.SIGALRM)

    eleza test_wakeup_fd_during(self):
        self.check_wakeup("""eleza test():
            agiza select
            agiza time

            TIMEOUT_FULL = 10
            TIMEOUT_HALF = 5

            kundi InterruptSelect(Exception):
                pita

            eleza handler(signum, frame):
                ashiria InterruptSelect
            signal.signal(signal.SIGALRM, handler)

            signal.alarm(1)
            before_time = time.monotonic()
            # We attempt to get a signal during the select call
            jaribu:
                select.select([read], [], [], TIMEOUT_FULL)
            tatizo InterruptSelect:
                pita
            isipokua:
                ashiria Exception("select() was sio interrupted")
            after_time = time.monotonic()
            dt = after_time - before_time
            ikiwa dt >= TIMEOUT_HALF:
                ashiria Exception("%s >= %s" % (dt, TIMEOUT_HALF))
        """, signal.SIGALRM)

    eleza test_signum(self):
        self.check_wakeup("""eleza test():
            signal.signal(signal.SIGUSR1, handler)
            signal.ashiria_signal(signal.SIGUSR1)
            signal.ashiria_signal(signal.SIGALRM)
        """, signal.SIGUSR1, signal.SIGALRM)

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    eleza test_pending(self):
        self.check_wakeup("""eleza test():
            signum1 = signal.SIGUSR1
            signum2 = signal.SIGUSR2

            signal.signal(signum1, handler)
            signal.signal(signum2, handler)

            signal.pthread_sigmask(signal.SIG_BLOCK, (signum1, signum2))
            signal.ashiria_signal(signum1)
            signal.ashiria_signal(signum2)
            # Unblocking the 2 signals calls the C signal handler twice
            signal.pthread_sigmask(signal.SIG_UNBLOCK, (signum1, signum2))
        """,  signal.SIGUSR1, signal.SIGUSR2, ordered=Uongo)


@unittest.skipUnless(hasattr(socket, 'socketpair'), 'need socket.socketpair')
kundi WakeupSocketSignalTests(unittest.TestCase):

    @unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
    eleza test_socket(self):
        # use a subprocess to have only one thread
        code = """ikiwa 1:
        agiza signal
        agiza socket
        agiza struct
        agiza _testcapi

        signum = signal.SIGINT
        signals = (signum,)

        eleza handler(signum, frame):
            pita

        signal.signal(signum, handler)

        read, write = socket.socketpair()
        write.setblocking(Uongo)
        signal.set_wakeup_fd(write.fileno())

        signal.ashiria_signal(signum)

        data = read.recv(1)
        ikiwa sio data:
            ashiria Exception("no signum written")
        ashiriad = struct.unpack('B', data)
        ikiwa ashiriad != signals:
            ashiria Exception("%r != %r" % (ashiriad, signals))

        read.close()
        write.close()
        """

        assert_python_ok('-c', code)

    @unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
    eleza test_send_error(self):
        # Use a subprocess to have only one thread.
        ikiwa os.name == 'nt':
            action = 'send'
        isipokua:
            action = 'write'
        code = """ikiwa 1:
        agiza errno
        agiza signal
        agiza socket
        agiza sys
        agiza time
        agiza _testcapi
        kutoka test.support agiza captured_stderr

        signum = signal.SIGINT

        eleza handler(signum, frame):
            pita

        signal.signal(signum, handler)

        read, write = socket.socketpair()
        read.setblocking(Uongo)
        write.setblocking(Uongo)

        signal.set_wakeup_fd(write.fileno())

        # Close sockets: send() will fail
        read.close()
        write.close()

        ukijumuisha captured_stderr() kama err:
            signal.ashiria_signal(signum)

        err = err.getvalue()
        ikiwa ('Exception ignored when trying to {action} to the signal wakeup fd'
            haiko kwenye err):
            ashiria AssertionError(err)
        """.format(action=action)
        assert_python_ok('-c', code)

    @unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
    eleza test_warn_on_full_buffer(self):
        # Use a subprocess to have only one thread.
        ikiwa os.name == 'nt':
            action = 'send'
        isipokua:
            action = 'write'
        code = """ikiwa 1:
        agiza errno
        agiza signal
        agiza socket
        agiza sys
        agiza time
        agiza _testcapi
        kutoka test.support agiza captured_stderr

        signum = signal.SIGINT

        # This handler will be called, but we intentionally won't read kutoka
        # the wakeup fd.
        eleza handler(signum, frame):
            pita

        signal.signal(signum, handler)

        read, write = socket.socketpair()

        # Fill the socketpair buffer
        ikiwa sys.platform == 'win32':
            # bpo-34130: On Windows, sometimes non-blocking send fails to fill
            # the full socketpair buffer, so use a timeout of 50 ms instead.
            write.settimeout(0.050)
        isipokua:
            write.setblocking(Uongo)

        # Start ukijumuisha large chunk size to reduce the
        # number of send needed to fill the buffer.
        written = 0
        kila chunk_size kwenye (2 ** 16, 2 ** 8, 1):
            chunk = b"x" * chunk_size
            jaribu:
                wakati Kweli:
                    write.send(chunk)
                    written += chunk_size
            tatizo (BlockingIOError, socket.timeout):
                pita

        andika(f"%s bytes written into the socketpair" % written, flush=Kweli)

        write.setblocking(Uongo)
        jaribu:
            write.send(b"x")
        tatizo BlockingIOError:
            # The socketpair buffer seems full
            pita
        isipokua:
            ashiria AssertionError("%s bytes failed to fill the socketpair "
                                 "buffer" % written)

        # By default, we get a warning when a signal arrives
        msg = ('Exception ignored when trying to {action} '
               'to the signal wakeup fd')
        signal.set_wakeup_fd(write.fileno())

        ukijumuisha captured_stderr() kama err:
            signal.ashiria_signal(signum)

        err = err.getvalue()
        ikiwa msg haiko kwenye err:
            ashiria AssertionError("first set_wakeup_fd() test failed, "
                                 "stderr: %r" % err)

        # And also ikiwa warn_on_full_buffer=Kweli
        signal.set_wakeup_fd(write.fileno(), warn_on_full_buffer=Kweli)

        ukijumuisha captured_stderr() kama err:
            signal.ashiria_signal(signum)

        err = err.getvalue()
        ikiwa msg haiko kwenye err:
            ashiria AssertionError("set_wakeup_fd(warn_on_full_buffer=Kweli) "
                                 "test failed, stderr: %r" % err)

        # But sio ikiwa warn_on_full_buffer=Uongo
        signal.set_wakeup_fd(write.fileno(), warn_on_full_buffer=Uongo)

        ukijumuisha captured_stderr() kama err:
            signal.ashiria_signal(signum)

        err = err.getvalue()
        ikiwa err != "":
            ashiria AssertionError("set_wakeup_fd(warn_on_full_buffer=Uongo) "
                                 "test failed, stderr: %r" % err)

        # And then check the default again, to make sure warn_on_full_buffer
        # settings don't leak across calls.
        signal.set_wakeup_fd(write.fileno())

        ukijumuisha captured_stderr() kama err:
            signal.ashiria_signal(signum)

        err = err.getvalue()
        ikiwa msg haiko kwenye err:
            ashiria AssertionError("second set_wakeup_fd() test failed, "
                                 "stderr: %r" % err)

        """.format(action=action)
        assert_python_ok('-c', code)


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
kundi SiginterruptTest(unittest.TestCase):

    eleza readpipe_interrupted(self, interrupt):
        """Perform a read during which a signal will arrive.  Return Kweli ikiwa the
        read ni interrupted by the signal na ashirias an exception.  Return Uongo
        ikiwa it rudishas normally.
        """
        # use a subprocess to have only one thread, to have a timeout on the
        # blocking read na to sio touch signal handling kwenye this process
        code = """ikiwa 1:
            agiza errno
            agiza os
            agiza signal
            agiza sys

            interrupt = %r
            r, w = os.pipe()

            eleza handler(signum, frame):
                1 / 0

            signal.signal(signal.SIGALRM, handler)
            ikiwa interrupt ni sio Tupu:
                signal.siginterrupt(signal.SIGALRM, interrupt)

            andika("ready")
            sys.stdout.flush()

            # run the test twice
            jaribu:
                kila loop kwenye range(2):
                    # send a SIGALRM kwenye a second (during the read)
                    signal.alarm(1)
                    jaribu:
                        # blocking call: read kutoka a pipe without data
                        os.read(r, 1)
                    tatizo ZeroDivisionError:
                        pita
                    isipokua:
                        sys.exit(2)
                sys.exit(3)
            mwishowe:
                os.close(r)
                os.close(w)
        """ % (interrupt,)
        ukijumuisha spawn_python('-c', code) kama process:
            jaribu:
                # wait until the child process ni loaded na has started
                first_line = process.stdout.readline()

                stdout, stderr = process.communicate(timeout=5.0)
            tatizo subprocess.TimeoutExpired:
                process.kill()
                rudisha Uongo
            isipokua:
                stdout = first_line + stdout
                exitcode = process.wait()
                ikiwa exitcode haiko kwenye (2, 3):
                    ashiria Exception("Child error (exit code %s): %r"
                                    % (exitcode, stdout))
                rudisha (exitcode == 3)

    eleza test_without_siginterrupt(self):
        # If a signal handler ni installed na siginterrupt ni sio called
        # at all, when that signal arrives, it interrupts a syscall that's in
        # progress.
        interrupted = self.readpipe_interrupted(Tupu)
        self.assertKweli(interrupted)

    eleza test_siginterrupt_on(self):
        # If a signal handler ni installed na siginterrupt ni called with
        # a true value kila the second argument, when that signal arrives, it
        # interrupts a syscall that's kwenye progress.
        interrupted = self.readpipe_interrupted(Kweli)
        self.assertKweli(interrupted)

    eleza test_siginterrupt_off(self):
        # If a signal handler ni installed na siginterrupt ni called with
        # a false value kila the second argument, when that signal arrives, it
        # does sio interrupt a syscall that's kwenye progress.
        interrupted = self.readpipe_interrupted(Uongo)
        self.assertUongo(interrupted)


@unittest.skipIf(sys.platform == "win32", "Not valid on Windows")
kundi ItimerTest(unittest.TestCase):
    eleza setUp(self):
        self.hndl_called = Uongo
        self.hndl_count = 0
        self.itimer = Tupu
        self.old_alarm = signal.signal(signal.SIGALRM, self.sig_alrm)

    eleza tearDown(self):
        signal.signal(signal.SIGALRM, self.old_alarm)
        ikiwa self.itimer ni sio Tupu: # test_itimer_exc doesn't change this attr
            # just ensure that itimer ni stopped
            signal.setitimer(self.itimer, 0)

    eleza sig_alrm(self, *args):
        self.hndl_called = Kweli

    eleza sig_vtalrm(self, *args):
        self.hndl_called = Kweli

        ikiwa self.hndl_count > 3:
            # it shouldn't be here, because it should have been disabled.
            ashiria signal.ItimerError("setitimer didn't disable ITIMER_VIRTUAL "
                "timer.")
        lasivyo self.hndl_count == 3:
            # disable ITIMER_VIRTUAL, this function shouldn't be called anymore
            signal.setitimer(signal.ITIMER_VIRTUAL, 0)

        self.hndl_count += 1

    eleza sig_prof(self, *args):
        self.hndl_called = Kweli
        signal.setitimer(signal.ITIMER_PROF, 0)

    eleza test_itimer_exc(self):
        # XXX I'm assuming -1 ni an invalid itimer, but maybe some platform
        # defines it ?
        self.assertRaises(signal.ItimerError, signal.setitimer, -1, 0)
        # Negative times are treated kama zero on some platforms.
        ikiwa 0:
            self.assertRaises(signal.ItimerError,
                              signal.setitimer, signal.ITIMER_REAL, -1)

    eleza test_itimer_real(self):
        self.itimer = signal.ITIMER_REAL
        signal.setitimer(self.itimer, 1.0)
        signal.pause()
        self.assertEqual(self.hndl_called, Kweli)

    # Issue 3864, unknown ikiwa this affects earlier versions of freebsd also
    @unittest.skipIf(sys.platform kwenye ('netbsd5',),
        'itimer sio reliable (does sio mix well ukijumuisha threading) on some BSDs.')
    eleza test_itimer_virtual(self):
        self.itimer = signal.ITIMER_VIRTUAL
        signal.signal(signal.SIGVTALRM, self.sig_vtalrm)
        signal.setitimer(self.itimer, 0.3, 0.2)

        start_time = time.monotonic()
        wakati time.monotonic() - start_time < 60.0:
            # use up some virtual time by doing real work
            _ = pow(12345, 67890, 10000019)
            ikiwa signal.getitimer(self.itimer) == (0.0, 0.0):
                koma # sig_vtalrm handler stopped this itimer
        isipokua: # Issue 8424
            self.skipTest("timeout: likely cause: machine too slow ama load too "
                          "high")

        # virtual itimer should be (0.0, 0.0) now
        self.assertEqual(signal.getitimer(self.itimer), (0.0, 0.0))
        # na the handler should have been called
        self.assertEqual(self.hndl_called, Kweli)

    eleza test_itimer_prof(self):
        self.itimer = signal.ITIMER_PROF
        signal.signal(signal.SIGPROF, self.sig_prof)
        signal.setitimer(self.itimer, 0.2, 0.2)

        start_time = time.monotonic()
        wakati time.monotonic() - start_time < 60.0:
            # do some work
            _ = pow(12345, 67890, 10000019)
            ikiwa signal.getitimer(self.itimer) == (0.0, 0.0):
                koma # sig_prof handler stopped this itimer
        isipokua: # Issue 8424
            self.skipTest("timeout: likely cause: machine too slow ama load too "
                          "high")

        # profiling itimer should be (0.0, 0.0) now
        self.assertEqual(signal.getitimer(self.itimer), (0.0, 0.0))
        # na the handler should have been called
        self.assertEqual(self.hndl_called, Kweli)

    eleza test_setitimer_tiny(self):
        # bpo-30807: C setitimer() takes a microsecond-resolution interval.
        # Check that float -> timeval conversion doesn't round
        # the interval down to zero, which would disable the timer.
        self.itimer = signal.ITIMER_REAL
        signal.setitimer(self.itimer, 1e-6)
        time.sleep(1)
        self.assertEqual(self.hndl_called, Kweli)


kundi PendingSignalsTests(unittest.TestCase):
    """
    Test pthread_sigmask(), pthread_kill(), sigpending() na sigwait()
    functions.
    """
    @unittest.skipUnless(hasattr(signal, 'sigpending'),
                         'need signal.sigpending()')
    eleza test_sigpending_empty(self):
        self.assertEqual(signal.sigpending(), set())

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    @unittest.skipUnless(hasattr(signal, 'sigpending'),
                         'need signal.sigpending()')
    eleza test_sigpending(self):
        code = """ikiwa 1:
            agiza os
            agiza signal

            eleza handler(signum, frame):
                1/0

            signum = signal.SIGUSR1
            signal.signal(signum, handler)

            signal.pthread_sigmask(signal.SIG_BLOCK, [signum])
            os.kill(os.getpid(), signum)
            pending = signal.sigpending()
            kila sig kwenye pending:
                assert isinstance(sig, signal.Signals), repr(pending)
            ikiwa pending != {signum}:
                ashiria Exception('%s != {%s}' % (pending, signum))
            jaribu:
                signal.pthread_sigmask(signal.SIG_UNBLOCK, [signum])
            tatizo ZeroDivisionError:
                pita
            isipokua:
                ashiria Exception("ZeroDivisionError sio ashiriad")
        """
        assert_python_ok('-c', code)

    @unittest.skipUnless(hasattr(signal, 'pthread_kill'),
                         'need signal.pthread_kill()')
    eleza test_pthread_kill(self):
        code = """ikiwa 1:
            agiza signal
            agiza threading
            agiza sys

            signum = signal.SIGUSR1

            eleza handler(signum, frame):
                1/0

            signal.signal(signum, handler)

            tid = threading.get_ident()
            jaribu:
                signal.pthread_kill(tid, signum)
            tatizo ZeroDivisionError:
                pita
            isipokua:
                ashiria Exception("ZeroDivisionError sio ashiriad")
        """
        assert_python_ok('-c', code)

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    eleza wait_helper(self, blocked, test):
        """
        test: body of the "eleza test(signum):" function.
        blocked: number of the blocked signal
        """
        code = '''ikiwa 1:
        agiza signal
        agiza sys
        kutoka signal agiza Signals

        eleza handler(signum, frame):
            1/0

        %s

        blocked = %s
        signum = signal.SIGALRM

        # child: block na wait the signal
        jaribu:
            signal.signal(signum, handler)
            signal.pthread_sigmask(signal.SIG_BLOCK, [blocked])

            # Do the tests
            test(signum)

            # The handler must sio be called on unblock
            jaribu:
                signal.pthread_sigmask(signal.SIG_UNBLOCK, [blocked])
            tatizo ZeroDivisionError:
                andika("the signal handler has been called",
                      file=sys.stderr)
                sys.exit(1)
        tatizo BaseException kama err:
            andika("error: {}".format(err), file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)
        ''' % (test.strip(), blocked)

        # sig*wait* must be called ukijumuisha the signal blocked: since the current
        # process might have several threads running, use a subprocess to have
        # a single thread.
        assert_python_ok('-c', code)

    @unittest.skipUnless(hasattr(signal, 'sigwait'),
                         'need signal.sigwait()')
    eleza test_sigwait(self):
        self.wait_helper(signal.SIGALRM, '''
        eleza test(signum):
            signal.alarm(1)
            received = signal.sigwait([signum])
            assert isinstance(received, signal.Signals), received
            ikiwa received != signum:
                ashiria Exception('received %s, sio %s' % (received, signum))
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigwaitinfo'),
                         'need signal.sigwaitinfo()')
    eleza test_sigwaitinfo(self):
        self.wait_helper(signal.SIGALRM, '''
        eleza test(signum):
            signal.alarm(1)
            info = signal.sigwaitinfo([signum])
            ikiwa info.si_signo != signum:
                ashiria Exception("info.si_signo != %s" % signum)
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigtimedwait()')
    eleza test_sigtimedwait(self):
        self.wait_helper(signal.SIGALRM, '''
        eleza test(signum):
            signal.alarm(1)
            info = signal.sigtimedwait([signum], 10.1000)
            ikiwa info.si_signo != signum:
                ashiria Exception('info.si_signo != %s' % signum)
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigtimedwait()')
    eleza test_sigtimedwait_poll(self):
        # check that polling ukijumuisha sigtimedwait works
        self.wait_helper(signal.SIGALRM, '''
        eleza test(signum):
            agiza os
            os.kill(os.getpid(), signum)
            info = signal.sigtimedwait([signum], 0)
            ikiwa info.si_signo != signum:
                ashiria Exception('info.si_signo != %s' % signum)
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigtimedwait()')
    eleza test_sigtimedwait_timeout(self):
        self.wait_helper(signal.SIGALRM, '''
        eleza test(signum):
            received = signal.sigtimedwait([signum], 1.0)
            ikiwa received ni sio Tupu:
                ashiria Exception("received=%r" % (received,))
        ''')

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigtimedwait()')
    eleza test_sigtimedwait_negative_timeout(self):
        signum = signal.SIGALRM
        self.assertRaises(ValueError, signal.sigtimedwait, [signum], -1.0)

    @unittest.skipUnless(hasattr(signal, 'sigwait'),
                         'need signal.sigwait()')
    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    eleza test_sigwait_thread(self):
        # Check that calling sigwait() kutoka a thread doesn't suspend the whole
        # process. A new interpreter ni spawned to avoid problems when mixing
        # threads na fork(): only async-safe functions are allowed between
        # fork() na exec().
        assert_python_ok("-c", """ikiwa Kweli:
            agiza os, threading, sys, time, signal

            # the default handler terminates the process
            signum = signal.SIGUSR1

            eleza kill_later():
                # wait until the main thread ni waiting kwenye sigwait()
                time.sleep(1)
                os.kill(os.getpid(), signum)

            # the signal must be blocked by all the threads
            signal.pthread_sigmask(signal.SIG_BLOCK, [signum])
            killer = threading.Thread(target=kill_later)
            killer.start()
            received = signal.sigwait([signum])
            ikiwa received != signum:
                andika("sigwait() received %s, sio %s" % (received, signum),
                      file=sys.stderr)
                sys.exit(1)
            killer.join()
            # unblock the signal, which should have been cleared by sigwait()
            signal.pthread_sigmask(signal.SIG_UNBLOCK, [signum])
        """)

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    eleza test_pthread_sigmask_arguments(self):
        self.assertRaises(TypeError, signal.pthread_sigmask)
        self.assertRaises(TypeError, signal.pthread_sigmask, 1)
        self.assertRaises(TypeError, signal.pthread_sigmask, 1, 2, 3)
        self.assertRaises(OSError, signal.pthread_sigmask, 1700, [])
        ukijumuisha self.assertRaises(ValueError):
            signal.pthread_sigmask(signal.SIG_BLOCK, [signal.NSIG])
        ukijumuisha self.assertRaises(ValueError):
            signal.pthread_sigmask(signal.SIG_BLOCK, [0])
        ukijumuisha self.assertRaises(ValueError):
            signal.pthread_sigmask(signal.SIG_BLOCK, [1<<1000])

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    eleza test_pthread_sigmask_valid_signals(self):
        s = signal.pthread_sigmask(signal.SIG_BLOCK, signal.valid_signals())
        self.addCleanup(signal.pthread_sigmask, signal.SIG_SETMASK, s)
        # Get current blocked set
        s = signal.pthread_sigmask(signal.SIG_UNBLOCK, signal.valid_signals())
        self.assertLessEqual(s, signal.valid_signals())

    @unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                         'need signal.pthread_sigmask()')
    eleza test_pthread_sigmask(self):
        code = """ikiwa 1:
        agiza signal
        agiza os; agiza threading

        eleza handler(signum, frame):
            1/0

        eleza kill(signum):
            os.kill(os.getpid(), signum)

        eleza check_mask(mask):
            kila sig kwenye mask:
                assert isinstance(sig, signal.Signals), repr(sig)

        eleza read_sigmask():
            sigmask = signal.pthread_sigmask(signal.SIG_BLOCK, [])
            check_mask(sigmask)
            rudisha sigmask

        signum = signal.SIGUSR1

        # Install our signal handler
        old_handler = signal.signal(signum, handler)

        # Unblock SIGUSR1 (and copy the old mask) to test our signal handler
        old_mask = signal.pthread_sigmask(signal.SIG_UNBLOCK, [signum])
        check_mask(old_mask)
        jaribu:
            kill(signum)
        tatizo ZeroDivisionError:
            pita
        isipokua:
            ashiria Exception("ZeroDivisionError sio ashiriad")

        # Block na then ashiria SIGUSR1. The signal ni blocked: the signal
        # handler ni sio called, na the signal ni now pending
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, [signum])
        check_mask(mask)
        kill(signum)

        # Check the new mask
        blocked = read_sigmask()
        check_mask(blocked)
        ikiwa signum haiko kwenye blocked:
            ashiria Exception("%s haiko kwenye %s" % (signum, blocked))
        ikiwa old_mask ^ blocked != {signum}:
            ashiria Exception("%s ^ %s != {%s}" % (old_mask, blocked, signum))

        # Unblock SIGUSR1
        jaribu:
            # unblock the pending signal calls immediately the signal handler
            signal.pthread_sigmask(signal.SIG_UNBLOCK, [signum])
        tatizo ZeroDivisionError:
            pita
        isipokua:
            ashiria Exception("ZeroDivisionError sio ashiriad")
        jaribu:
            kill(signum)
        tatizo ZeroDivisionError:
            pita
        isipokua:
            ashiria Exception("ZeroDivisionError sio ashiriad")

        # Check the new mask
        unblocked = read_sigmask()
        ikiwa signum kwenye unblocked:
            ashiria Exception("%s kwenye %s" % (signum, unblocked))
        ikiwa blocked ^ unblocked != {signum}:
            ashiria Exception("%s ^ %s != {%s}" % (blocked, unblocked, signum))
        ikiwa old_mask != unblocked:
            ashiria Exception("%s != %s" % (old_mask, unblocked))
        """
        assert_python_ok('-c', code)

    @unittest.skipUnless(hasattr(signal, 'pthread_kill'),
                         'need signal.pthread_kill()')
    eleza test_pthread_kill_main_thread(self):
        # Test that a signal can be sent to the main thread ukijumuisha pthread_kill()
        # before any other thread has been created (see issue #12392).
        code = """ikiwa Kweli:
            agiza threading
            agiza signal
            agiza sys

            eleza handler(signum, frame):
                sys.exit(3)

            signal.signal(signal.SIGUSR1, handler)
            signal.pthread_kill(threading.get_ident(), signal.SIGUSR1)
            sys.exit(2)
        """

        ukijumuisha spawn_python('-c', code) kama process:
            stdout, stderr = process.communicate()
            exitcode = process.wait()
            ikiwa exitcode != 3:
                ashiria Exception("Child error (exit code %s): %s" %
                                (exitcode, stdout))


kundi StressTest(unittest.TestCase):
    """
    Stress signal delivery, especially when a signal arrives in
    the middle of recomputing the signal state ama executing
    previously tripped signal handlers.
    """

    eleza setsig(self, signum, handler):
        old_handler = signal.signal(signum, handler)
        self.addCleanup(signal.signal, signum, old_handler)

    eleza measure_itimer_resolution(self):
        N = 20
        times = []

        eleza handler(signum=Tupu, frame=Tupu):
            ikiwa len(times) < N:
                times.append(time.perf_counter())
                # 1 µs ni the smallest possible timer interval,
                # we want to measure what the concrete duration
                # will be on this platform
                signal.setitimer(signal.ITIMER_REAL, 1e-6)

        self.addCleanup(signal.setitimer, signal.ITIMER_REAL, 0)
        self.setsig(signal.SIGALRM, handler)
        handler()
        wakati len(times) < N:
            time.sleep(1e-3)

        durations = [times[i+1] - times[i] kila i kwenye range(len(times) - 1)]
        med = statistics.median(durations)
        ikiwa support.verbose:
            andika("detected median itimer() resolution: %.6f s." % (med,))
        rudisha med

    eleza decide_itimer_count(self):
        # Some systems have poor setitimer() resolution (kila example
        # measured around 20 ms. on FreeBSD 9), so decide on a reasonable
        # number of sequential timers based on that.
        reso = self.measure_itimer_resolution()
        ikiwa reso <= 1e-4:
            rudisha 10000
        lasivyo reso <= 1e-2:
            rudisha 100
        isipokua:
            self.skipTest("detected itimer resolution (%.3f s.) too high "
                          "(> 10 ms.) on this platform (or system too busy)"
                          % (reso,))

    @unittest.skipUnless(hasattr(signal, "setitimer"),
                         "test needs setitimer()")
    eleza test_stress_delivery_dependent(self):
        """
        This test uses dependent signal handlers.
        """
        N = self.decide_itimer_count()
        sigs = []

        eleza first_handler(signum, frame):
            # 1e-6 ni the minimum non-zero value kila `setitimer()`.
            # Choose a random delay so kama to improve chances of
            # triggering a race condition.  Ideally the signal ni received
            # when inside critical signal-handling routines such as
            # Py_MakePendingCalls().
            signal.setitimer(signal.ITIMER_REAL, 1e-6 + random.random() * 1e-5)

        eleza second_handler(signum=Tupu, frame=Tupu):
            sigs.append(signum)

        # Here on Linux, SIGPROF > SIGALRM > SIGUSR1.  By using both
        # ascending na descending sequences (SIGUSR1 then SIGALRM,
        # SIGPROF then SIGALRM), we maximize chances of hitting a bug.
        self.setsig(signal.SIGPROF, first_handler)
        self.setsig(signal.SIGUSR1, first_handler)
        self.setsig(signal.SIGALRM, second_handler)  # kila ITIMER_REAL

        expected_sigs = 0
        deadline = time.monotonic() + 15.0

        wakati expected_sigs < N:
            os.kill(os.getpid(), signal.SIGPROF)
            expected_sigs += 1
            # Wait kila handlers to run to avoid signal coalescing
            wakati len(sigs) < expected_sigs na time.monotonic() < deadline:
                time.sleep(1e-5)

            os.kill(os.getpid(), signal.SIGUSR1)
            expected_sigs += 1
            wakati len(sigs) < expected_sigs na time.monotonic() < deadline:
                time.sleep(1e-5)

        # All ITIMER_REAL signals should have been delivered to the
        # Python handler
        self.assertEqual(len(sigs), N, "Some signals were lost")

    @unittest.skipUnless(hasattr(signal, "setitimer"),
                         "test needs setitimer()")
    eleza test_stress_delivery_simultaneous(self):
        """
        This test uses simultaneous signal handlers.
        """
        N = self.decide_itimer_count()
        sigs = []

        eleza handler(signum, frame):
            sigs.append(signum)

        self.setsig(signal.SIGUSR1, handler)
        self.setsig(signal.SIGALRM, handler)  # kila ITIMER_REAL

        expected_sigs = 0
        deadline = time.monotonic() + 15.0

        wakati expected_sigs < N:
            # Hopefully the SIGALRM will be received somewhere during
            # initial processing of SIGUSR1.
            signal.setitimer(signal.ITIMER_REAL, 1e-6 + random.random() * 1e-5)
            os.kill(os.getpid(), signal.SIGUSR1)

            expected_sigs += 2
            # Wait kila handlers to run to avoid signal coalescing
            wakati len(sigs) < expected_sigs na time.monotonic() < deadline:
                time.sleep(1e-5)

        # All ITIMER_REAL signals should have been delivered to the
        # Python handler
        self.assertEqual(len(sigs), N, "Some signals were lost")

kundi RaiseSignalTest(unittest.TestCase):

    eleza test_sigint(self):
        ukijumuisha self.assertRaises(KeyboardInterrupt):
            signal.ashiria_signal(signal.SIGINT)

    @unittest.skipIf(sys.platform != "win32", "Windows specific test")
    eleza test_invalid_argument(self):
        jaribu:
            SIGHUP = 1 # sio supported on win32
            signal.ashiria_signal(SIGHUP)
            self.fail("OSError (Invalid argument) expected")
        tatizo OSError kama e:
            ikiwa e.errno == errno.EINVAL:
                pita
            isipokua:
                ashiria

    eleza test_handler(self):
        is_ok = Uongo
        eleza handler(a, b):
            nonlocal is_ok
            is_ok = Kweli
        old_signal = signal.signal(signal.SIGINT, handler)
        self.addCleanup(signal.signal, signal.SIGINT, old_signal)

        signal.ashiria_signal(signal.SIGINT)
        self.assertKweli(is_ok)


eleza tearDownModule():
    support.reap_children()

ikiwa __name__ == "__main__":
    unittest.main()
