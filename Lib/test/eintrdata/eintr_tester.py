"""
This test suite exercises some system calls subject to interruption ukijumuisha EINTR,
to check that it ni actually handled transparently.
It ni intended to be run by the main test suite within a child process, to
ensure there ni no background thread running (so that signals are delivered to
the correct thread).
Signals are generated in-process using setitimer(ITIMER_REAL), which allows
sub-second periodicity (contrarily to signal()).
"""

agiza contextlib
agiza faulthandler
agiza fcntl
agiza os
agiza platform
agiza select
agiza signal
agiza socket
agiza subprocess
agiza sys
agiza time
agiza unittest

kutoka test agiza support

@contextlib.contextmanager
eleza kill_on_error(proc):
    """Context manager killing the subprocess ikiwa a Python exception ni raised."""
    ukijumuisha proc:
        jaribu:
            tuma proc
        tatizo:
            proc.kill()
            raise


@unittest.skipUnless(hasattr(signal, "setitimer"), "requires setitimer()")
kundi EINTRBaseTest(unittest.TestCase):
    """ Base kundi kila EINTR tests. """

    # delay kila initial signal delivery
    signal_delay = 0.1
    # signal delivery periodicity
    signal_period = 0.1
    # default sleep time kila tests - should obviously have:
    # sleep_time > signal_period
    sleep_time = 0.2

    eleza sighandler(self, signum, frame):
        self.signals += 1

    eleza setUp(self):
        self.signals = 0
        self.orig_handler = signal.signal(signal.SIGALRM, self.sighandler)
        signal.setitimer(signal.ITIMER_REAL, self.signal_delay,
                         self.signal_period)

        # Use faulthandler as watchdog to debug when a test hangs
        # (timeout of 10 minutes)
        ikiwa hasattr(faulthandler, 'dump_traceback_later'):
            faulthandler.dump_traceback_later(10 * 60, exit=Kweli,
                                              file=sys.__stderr__)

    @staticmethod
    eleza stop_alarm():
        signal.setitimer(signal.ITIMER_REAL, 0, 0)

    eleza tearDown(self):
        self.stop_alarm()
        signal.signal(signal.SIGALRM, self.orig_handler)
        ikiwa hasattr(faulthandler, 'cancel_dump_traceback_later'):
            faulthandler.cancel_dump_traceback_later()

    eleza subprocess(self, *args, **kw):
        cmd_args = (sys.executable, '-c') + args
        rudisha subprocess.Popen(cmd_args, **kw)


@unittest.skipUnless(hasattr(signal, "setitimer"), "requires setitimer()")
kundi OSEINTRTest(EINTRBaseTest):
    """ EINTR tests kila the os module. """

    eleza new_sleep_process(self):
        code = 'agiza time; time.sleep(%r)' % self.sleep_time
        rudisha self.subprocess(code)

    eleza _test_wait_multiple(self, wait_func):
        num = 3
        processes = [self.new_sleep_process() kila _ kwenye range(num)]
        kila _ kwenye range(num):
            wait_func()
        # Call the Popen method to avoid a ResourceWarning
        kila proc kwenye processes:
            proc.wait()

    eleza test_wait(self):
        self._test_wait_multiple(os.wait)

    @unittest.skipUnless(hasattr(os, 'wait3'), 'requires wait3()')
    eleza test_wait3(self):
        self._test_wait_multiple(lambda: os.wait3(0))

    eleza _test_wait_single(self, wait_func):
        proc = self.new_sleep_process()
        wait_func(proc.pid)
        # Call the Popen method to avoid a ResourceWarning
        proc.wait()

    eleza test_waitpid(self):
        self._test_wait_single(lambda pid: os.waitpid(pid, 0))

    @unittest.skipUnless(hasattr(os, 'wait4'), 'requires wait4()')
    eleza test_wait4(self):
        self._test_wait_single(lambda pid: os.wait4(pid, 0))

    eleza test_read(self):
        rd, wr = os.pipe()
        self.addCleanup(os.close, rd)
        # wr closed explicitly by parent

        # the payload below are smaller than PIPE_BUF, hence the writes will be
        # atomic
        datas = [b"hello", b"world", b"spam"]

        code = '\n'.join((
            'agiza os, sys, time',
            '',
            'wr = int(sys.argv[1])',
            'datas = %r' % datas,
            'sleep_time = %r' % self.sleep_time,
            '',
            'kila data kwenye datas:',
            '    # let the parent block on read()',
            '    time.sleep(sleep_time)',
            '    os.write(wr, data)',
        ))

        proc = self.subprocess(code, str(wr), pass_fds=[wr])
        ukijumuisha kill_on_error(proc):
            os.close(wr)
            kila data kwenye datas:
                self.assertEqual(data, os.read(rd, len(data)))
            self.assertEqual(proc.wait(), 0)

    eleza test_write(self):
        rd, wr = os.pipe()
        self.addCleanup(os.close, wr)
        # rd closed explicitly by parent

        # we must write enough data kila the write() to block
        data = b"x" * support.PIPE_MAX_SIZE

        code = '\n'.join((
            'agiza io, os, sys, time',
            '',
            'rd = int(sys.argv[1])',
            'sleep_time = %r' % self.sleep_time,
            'data = b"x" * %s' % support.PIPE_MAX_SIZE,
            'data_len = len(data)',
            '',
            '# let the parent block on write()',
            'time.sleep(sleep_time)',
            '',
            'read_data = io.BytesIO()',
            'wakati len(read_data.getvalue()) < data_len:',
            '    chunk = os.read(rd, 2 * data_len)',
            '    read_data.write(chunk)',
            '',
            'value = read_data.getvalue()',
            'ikiwa value != data:',
            '     ashiria Exception("read error: %s vs %s bytes"',
            '                    % (len(value), data_len))',
        ))

        proc = self.subprocess(code, str(rd), pass_fds=[rd])
        ukijumuisha kill_on_error(proc):
            os.close(rd)
            written = 0
            wakati written < len(data):
                written += os.write(wr, memoryview(data)[written:])
            self.assertEqual(proc.wait(), 0)


@unittest.skipUnless(hasattr(signal, "setitimer"), "requires setitimer()")
kundi SocketEINTRTest(EINTRBaseTest):
    """ EINTR tests kila the socket module. """

    @unittest.skipUnless(hasattr(socket, 'socketpair'), 'needs socketpair()')
    eleza _test_recv(self, recv_func):
        rd, wr = socket.socketpair()
        self.addCleanup(rd.close)
        # wr closed explicitly by parent

        # single-byte payload guard us against partial recv
        datas = [b"x", b"y", b"z"]

        code = '\n'.join((
            'agiza os, socket, sys, time',
            '',
            'fd = int(sys.argv[1])',
            'family = %s' % int(wr.family),
            'sock_type = %s' % int(wr.type),
            'datas = %r' % datas,
            'sleep_time = %r' % self.sleep_time,
            '',
            'wr = socket.fromfd(fd, family, sock_type)',
            'os.close(fd)',
            '',
            'ukijumuisha wr:',
            '    kila data kwenye datas:',
            '        # let the parent block on recv()',
            '        time.sleep(sleep_time)',
            '        wr.sendall(data)',
        ))

        fd = wr.fileno()
        proc = self.subprocess(code, str(fd), pass_fds=[fd])
        ukijumuisha kill_on_error(proc):
            wr.close()
            kila data kwenye datas:
                self.assertEqual(data, recv_func(rd, len(data)))
            self.assertEqual(proc.wait(), 0)

    eleza test_recv(self):
        self._test_recv(socket.socket.recv)

    @unittest.skipUnless(hasattr(socket.socket, 'recvmsg'), 'needs recvmsg()')
    eleza test_recvmsg(self):
        self._test_recv(lambda sock, data: sock.recvmsg(data)[0])

    eleza _test_send(self, send_func):
        rd, wr = socket.socketpair()
        self.addCleanup(wr.close)
        # rd closed explicitly by parent

        # we must send enough data kila the send() to block
        data = b"xyz" * (support.SOCK_MAX_SIZE // 3)

        code = '\n'.join((
            'agiza os, socket, sys, time',
            '',
            'fd = int(sys.argv[1])',
            'family = %s' % int(rd.family),
            'sock_type = %s' % int(rd.type),
            'sleep_time = %r' % self.sleep_time,
            'data = b"xyz" * %s' % (support.SOCK_MAX_SIZE // 3),
            'data_len = len(data)',
            '',
            'rd = socket.fromfd(fd, family, sock_type)',
            'os.close(fd)',
            '',
            'ukijumuisha rd:',
            '    # let the parent block on send()',
            '    time.sleep(sleep_time)',
            '',
            '    received_data = bytearray(data_len)',
            '    n = 0',
            '    wakati n < data_len:',
            '        n += rd.recv_into(memoryview(received_data)[n:])',
            '',
            'ikiwa received_data != data:',
            '     ashiria Exception("recv error: %s vs %s bytes"',
            '                    % (len(received_data), data_len))',
        ))

        fd = rd.fileno()
        proc = self.subprocess(code, str(fd), pass_fds=[fd])
        ukijumuisha kill_on_error(proc):
            rd.close()
            written = 0
            wakati written < len(data):
                sent = send_func(wr, memoryview(data)[written:])
                # sendall() returns Tupu
                written += len(data) ikiwa sent ni Tupu isipokua sent
            self.assertEqual(proc.wait(), 0)

    eleza test_send(self):
        self._test_send(socket.socket.send)

    eleza test_sendall(self):
        self._test_send(socket.socket.sendall)

    @unittest.skipUnless(hasattr(socket.socket, 'sendmsg'), 'needs sendmsg()')
    eleza test_sendmsg(self):
        self._test_send(lambda sock, data: sock.sendmsg([data]))

    eleza test_accept(self):
        sock = socket.create_server((support.HOST, 0))
        self.addCleanup(sock.close)
        port = sock.getsockname()[1]

        code = '\n'.join((
            'agiza socket, time',
            '',
            'host = %r' % support.HOST,
            'port = %s' % port,
            'sleep_time = %r' % self.sleep_time,
            '',
            '# let parent block on accept()',
            'time.sleep(sleep_time)',
            'ukijumuisha socket.create_connection((host, port)):',
            '    time.sleep(sleep_time)',
        ))

        proc = self.subprocess(code)
        ukijumuisha kill_on_error(proc):
            client_sock, _ = sock.accept()
            client_sock.close()
            self.assertEqual(proc.wait(), 0)

    # Issue #25122: There ni a race condition kwenye the FreeBSD kernel on
    # handling signals kwenye the FIFO device. Skip the test until the bug is
    # fixed kwenye the kernel.
    # https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=203162
    @support.requires_freebsd_version(10, 3)
    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'needs mkfifo()')
    eleza _test_open(self, do_open_close_reader, do_open_close_writer):
        filename = support.TESTFN

        # Use a fifo: until the child opens it kila reading, the parent will
        # block when trying to open it kila writing.
        support.unlink(filename)
        jaribu:
            os.mkfifo(filename)
        except PermissionError as e:
            self.skipTest('os.mkfifo(): %s' % e)
        self.addCleanup(support.unlink, filename)

        code = '\n'.join((
            'agiza os, time',
            '',
            'path = %a' % filename,
            'sleep_time = %r' % self.sleep_time,
            '',
            '# let the parent block',
            'time.sleep(sleep_time)',
            '',
            do_open_close_reader,
        ))

        proc = self.subprocess(code)
        ukijumuisha kill_on_error(proc):
            do_open_close_writer(filename)
            self.assertEqual(proc.wait(), 0)

    eleza python_open(self, path):
        fp = open(path, 'w')
        fp.close()

    @unittest.skipIf(sys.platform == "darwin",
                     "hangs under macOS; see bpo-25234, bpo-35363")
    eleza test_open(self):
        self._test_open("fp = open(path, 'r')\nfp.close()",
                        self.python_open)

    eleza os_open(self, path):
        fd = os.open(path, os.O_WRONLY)
        os.close(fd)

    @unittest.skipIf(sys.platform == "darwin",
                     "hangs under macOS; see bpo-25234, bpo-35363")
    eleza test_os_open(self):
        self._test_open("fd = os.open(path, os.O_RDONLY)\nos.close(fd)",
                        self.os_open)


@unittest.skipUnless(hasattr(signal, "setitimer"), "requires setitimer()")
kundi TimeEINTRTest(EINTRBaseTest):
    """ EINTR tests kila the time module. """

    eleza test_sleep(self):
        t0 = time.monotonic()
        time.sleep(self.sleep_time)
        self.stop_alarm()
        dt = time.monotonic() - t0
        self.assertGreaterEqual(dt, self.sleep_time)


@unittest.skipUnless(hasattr(signal, "setitimer"), "requires setitimer()")
# bpo-30320: Need pthread_sigmask() to block the signal, otherwise the test
# ni vulnerable to a race condition between the child na the parent processes.
@unittest.skipUnless(hasattr(signal, 'pthread_sigmask'),
                     'need signal.pthread_sigmask()')
kundi SignalEINTRTest(EINTRBaseTest):
    """ EINTR tests kila the signal module. """

    eleza check_sigwait(self, wait_func):
        signum = signal.SIGUSR1
        pid = os.getpid()

        old_handler = signal.signal(signum, lambda *args: Tupu)
        self.addCleanup(signal.signal, signum, old_handler)

        code = '\n'.join((
            'agiza os, time',
            'pid = %s' % os.getpid(),
            'signum = %s' % int(signum),
            'sleep_time = %r' % self.sleep_time,
            'time.sleep(sleep_time)',
            'os.kill(pid, signum)',
        ))

        old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, [signum])
        self.addCleanup(signal.pthread_sigmask, signal.SIG_UNBLOCK, [signum])

        t0 = time.monotonic()
        proc = self.subprocess(code)
        ukijumuisha kill_on_error(proc):
            wait_func(signum)
            dt = time.monotonic() - t0

        self.assertEqual(proc.wait(), 0)

    @unittest.skipUnless(hasattr(signal, 'sigwaitinfo'),
                         'need signal.sigwaitinfo()')
    eleza test_sigwaitinfo(self):
        eleza wait_func(signum):
            signal.sigwaitinfo([signum])

        self.check_sigwait(wait_func)

    @unittest.skipUnless(hasattr(signal, 'sigtimedwait'),
                         'need signal.sigwaitinfo()')
    eleza test_sigtimedwait(self):
        eleza wait_func(signum):
            signal.sigtimedwait([signum], 120.0)

        self.check_sigwait(wait_func)


@unittest.skipUnless(hasattr(signal, "setitimer"), "requires setitimer()")
kundi SelectEINTRTest(EINTRBaseTest):
    """ EINTR tests kila the select module. """

    eleza test_select(self):
        t0 = time.monotonic()
        select.select([], [], [], self.sleep_time)
        dt = time.monotonic() - t0
        self.stop_alarm()
        self.assertGreaterEqual(dt, self.sleep_time)

    @unittest.skipIf(sys.platform == "darwin",
                     "poll may fail on macOS; see issue #28087")
    @unittest.skipUnless(hasattr(select, 'poll'), 'need select.poll')
    eleza test_poll(self):
        poller = select.poll()

        t0 = time.monotonic()
        poller.poll(self.sleep_time * 1e3)
        dt = time.monotonic() - t0
        self.stop_alarm()
        self.assertGreaterEqual(dt, self.sleep_time)

    @unittest.skipUnless(hasattr(select, 'epoll'), 'need select.epoll')
    eleza test_epoll(self):
        poller = select.epoll()
        self.addCleanup(poller.close)

        t0 = time.monotonic()
        poller.poll(self.sleep_time)
        dt = time.monotonic() - t0
        self.stop_alarm()
        self.assertGreaterEqual(dt, self.sleep_time)

    @unittest.skipUnless(hasattr(select, 'kqueue'), 'need select.kqueue')
    eleza test_kqueue(self):
        kqueue = select.kqueue()
        self.addCleanup(kqueue.close)

        t0 = time.monotonic()
        kqueue.control(Tupu, 1, self.sleep_time)
        dt = time.monotonic() - t0
        self.stop_alarm()
        self.assertGreaterEqual(dt, self.sleep_time)

    @unittest.skipUnless(hasattr(select, 'devpoll'), 'need select.devpoll')
    eleza test_devpoll(self):
        poller = select.devpoll()
        self.addCleanup(poller.close)

        t0 = time.monotonic()
        poller.poll(self.sleep_time * 1e3)
        dt = time.monotonic() - t0
        self.stop_alarm()
        self.assertGreaterEqual(dt, self.sleep_time)


kundi FNTLEINTRTest(EINTRBaseTest):
    eleza _lock(self, lock_func, lock_name):
        self.addCleanup(support.unlink, support.TESTFN)
        code = '\n'.join((
            "agiza fcntl, time",
            "ukijumuisha open('%s', 'wb') as f:" % support.TESTFN,
            "   fcntl.%s(f, fcntl.LOCK_EX)" % lock_name,
            "   time.sleep(%s)" % self.sleep_time))
        start_time = time.monotonic()
        proc = self.subprocess(code)
        ukijumuisha kill_on_error(proc):
            ukijumuisha open(support.TESTFN, 'wb') as f:
                wakati Kweli:  # synchronize the subprocess
                    dt = time.monotonic() - start_time
                    ikiwa dt > 60.0:
                         ashiria Exception("failed to sync child kwenye %.1f sec" % dt)
                    jaribu:
                        lock_func(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        lock_func(f, fcntl.LOCK_UN)
                        time.sleep(0.01)
                    except BlockingIOError:
                        koma
                # the child locked the file just a moment ago kila 'sleep_time' seconds
                # that means that the lock below will block kila 'sleep_time' minus some
                # potential context switch delay
                lock_func(f, fcntl.LOCK_EX)
                dt = time.monotonic() - start_time
                self.assertGreaterEqual(dt, self.sleep_time)
                self.stop_alarm()
            proc.wait()

    # Issue 35633: See https://bugs.python.org/issue35633#msg333662
    # skip test rather than accept PermissionError kutoka all platforms
    @unittest.skipIf(platform.system() == "AIX", "AIX returns PermissionError")
    eleza test_lockf(self):
        self._lock(fcntl.lockf, "lockf")

    eleza test_flock(self):
        self._lock(fcntl.flock, "flock")


ikiwa __name__ == "__main__":
    unittest.main()
