"""Tests kila unix_events.py."""

agiza collections
agiza contextlib
agiza errno
agiza io
agiza os
agiza pathlib
agiza signal
agiza socket
agiza stat
agiza sys
agiza tempfile
agiza threading
agiza unittest
kutoka unittest agiza mock
kutoka test agiza support

ikiwa sys.platform == 'win32':
    ashiria unittest.SkipTest('UNIX only')


agiza asyncio
kutoka asyncio agiza log
kutoka asyncio agiza unix_events
kutoka test.test_asyncio agiza utils kama test_utils


MOCK_ANY = mock.ANY


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


eleza close_pipe_transport(transport):
    # Don't call transport.close() because the event loop na the selector
    # are mocked
    ikiwa transport._pipe ni Tupu:
        rudisha
    transport._pipe.close()
    transport._pipe = Tupu


@unittest.skipUnless(signal, 'Signals are sio supported')
kundi SelectorEventLoopSignalTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.SelectorEventLoop()
        self.set_event_loop(self.loop)

    eleza test_check_signal(self):
        self.assertRaises(
            TypeError, self.loop._check_signal, '1')
        self.assertRaises(
            ValueError, self.loop._check_signal, signal.NSIG + 1)

    eleza test_handle_signal_no_handler(self):
        self.loop._handle_signal(signal.NSIG + 1)

    eleza test_handle_signal_cancelled_handler(self):
        h = asyncio.Handle(mock.Mock(), (),
                           loop=mock.Mock())
        h.cancel()
        self.loop._signal_handlers[signal.NSIG + 1] = h
        self.loop.remove_signal_handler = mock.Mock()
        self.loop._handle_signal(signal.NSIG + 1)
        self.loop.remove_signal_handler.assert_called_with(signal.NSIG + 1)

    @mock.patch('asyncio.unix_events.signal')
    eleza test_add_signal_handler_setup_error(self, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals
        m_signal.set_wakeup_fd.side_effect = ValueError

        self.assertRaises(
            RuntimeError,
            self.loop.add_signal_handler,
            signal.SIGINT, lambda: Kweli)

    @mock.patch('asyncio.unix_events.signal')
    eleza test_add_signal_handler_coroutine_error(self, m_signal):
        m_signal.NSIG = signal.NSIG

        async eleza simple_coroutine():
            pita

        # callback must sio be a coroutine function
        coro_func = simple_coroutine
        coro_obj = coro_func()
        self.addCleanup(coro_obj.close)
        kila func kwenye (coro_func, coro_obj):
            self.assertRaisesRegex(
                TypeError, 'coroutines cannot be used ukijumuisha add_signal_handler',
                self.loop.add_signal_handler,
                signal.SIGINT, func)

    @mock.patch('asyncio.unix_events.signal')
    eleza test_add_signal_handler(self, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals

        cb = lambda: Kweli
        self.loop.add_signal_handler(signal.SIGHUP, cb)
        h = self.loop._signal_handlers.get(signal.SIGHUP)
        self.assertIsInstance(h, asyncio.Handle)
        self.assertEqual(h._callback, cb)

    @mock.patch('asyncio.unix_events.signal')
    eleza test_add_signal_handler_install_error(self, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals

        eleza set_wakeup_fd(fd):
            ikiwa fd == -1:
                ashiria ValueError()
        m_signal.set_wakeup_fd = set_wakeup_fd

        kundi Err(OSError):
            errno = errno.EFAULT
        m_signal.signal.side_effect = Err

        self.assertRaises(
            Err,
            self.loop.add_signal_handler,
            signal.SIGINT, lambda: Kweli)

    @mock.patch('asyncio.unix_events.signal')
    @mock.patch('asyncio.base_events.logger')
    eleza test_add_signal_handler_install_error2(self, m_logging, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals

        kundi Err(OSError):
            errno = errno.EINVAL
        m_signal.signal.side_effect = Err

        self.loop._signal_handlers[signal.SIGHUP] = lambda: Kweli
        self.assertRaises(
            RuntimeError,
            self.loop.add_signal_handler,
            signal.SIGINT, lambda: Kweli)
        self.assertUongo(m_logging.info.called)
        self.assertEqual(1, m_signal.set_wakeup_fd.call_count)

    @mock.patch('asyncio.unix_events.signal')
    @mock.patch('asyncio.base_events.logger')
    eleza test_add_signal_handler_install_error3(self, m_logging, m_signal):
        kundi Err(OSError):
            errno = errno.EINVAL
        m_signal.signal.side_effect = Err
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals

        self.assertRaises(
            RuntimeError,
            self.loop.add_signal_handler,
            signal.SIGINT, lambda: Kweli)
        self.assertUongo(m_logging.info.called)
        self.assertEqual(2, m_signal.set_wakeup_fd.call_count)

    @mock.patch('asyncio.unix_events.signal')
    eleza test_remove_signal_handler(self, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals

        self.loop.add_signal_handler(signal.SIGHUP, lambda: Kweli)

        self.assertKweli(
            self.loop.remove_signal_handler(signal.SIGHUP))
        self.assertKweli(m_signal.set_wakeup_fd.called)
        self.assertKweli(m_signal.signal.called)
        self.assertEqual(
            (signal.SIGHUP, m_signal.SIG_DFL), m_signal.signal.call_args[0])

    @mock.patch('asyncio.unix_events.signal')
    eleza test_remove_signal_handler_2(self, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.SIGINT = signal.SIGINT
        m_signal.valid_signals = signal.valid_signals

        self.loop.add_signal_handler(signal.SIGINT, lambda: Kweli)
        self.loop._signal_handlers[signal.SIGHUP] = object()
        m_signal.set_wakeup_fd.reset_mock()

        self.assertKweli(
            self.loop.remove_signal_handler(signal.SIGINT))
        self.assertUongo(m_signal.set_wakeup_fd.called)
        self.assertKweli(m_signal.signal.called)
        self.assertEqual(
            (signal.SIGINT, m_signal.default_int_handler),
            m_signal.signal.call_args[0])

    @mock.patch('asyncio.unix_events.signal')
    @mock.patch('asyncio.base_events.logger')
    eleza test_remove_signal_handler_cleanup_error(self, m_logging, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals
        self.loop.add_signal_handler(signal.SIGHUP, lambda: Kweli)

        m_signal.set_wakeup_fd.side_effect = ValueError

        self.loop.remove_signal_handler(signal.SIGHUP)
        self.assertKweli(m_logging.info)

    @mock.patch('asyncio.unix_events.signal')
    eleza test_remove_signal_handler_error(self, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals
        self.loop.add_signal_handler(signal.SIGHUP, lambda: Kweli)

        m_signal.signal.side_effect = OSError

        self.assertRaises(
            OSError, self.loop.remove_signal_handler, signal.SIGHUP)

    @mock.patch('asyncio.unix_events.signal')
    eleza test_remove_signal_handler_error2(self, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals
        self.loop.add_signal_handler(signal.SIGHUP, lambda: Kweli)

        kundi Err(OSError):
            errno = errno.EINVAL
        m_signal.signal.side_effect = Err

        self.assertRaises(
            RuntimeError, self.loop.remove_signal_handler, signal.SIGHUP)

    @mock.patch('asyncio.unix_events.signal')
    eleza test_close(self, m_signal):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals

        self.loop.add_signal_handler(signal.SIGHUP, lambda: Kweli)
        self.loop.add_signal_handler(signal.SIGCHLD, lambda: Kweli)

        self.assertEqual(len(self.loop._signal_handlers), 2)

        m_signal.set_wakeup_fd.reset_mock()

        self.loop.close()

        self.assertEqual(len(self.loop._signal_handlers), 0)
        m_signal.set_wakeup_fd.assert_called_once_with(-1)

    @mock.patch('asyncio.unix_events.sys')
    @mock.patch('asyncio.unix_events.signal')
    eleza test_close_on_finalizing(self, m_signal, m_sys):
        m_signal.NSIG = signal.NSIG
        m_signal.valid_signals = signal.valid_signals
        self.loop.add_signal_handler(signal.SIGHUP, lambda: Kweli)

        self.assertEqual(len(self.loop._signal_handlers), 1)
        m_sys.is_finalizing.return_value = Kweli
        m_signal.signal.reset_mock()

        ukijumuisha self.assertWarnsRegex(ResourceWarning,
                                   "skipping signal handlers removal"):
            self.loop.close()

        self.assertEqual(len(self.loop._signal_handlers), 0)
        self.assertUongo(m_signal.signal.called)


@unittest.skipUnless(hasattr(socket, 'AF_UNIX'),
                     'UNIX Sockets are sio supported')
kundi SelectorEventLoopUnixSocketTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.SelectorEventLoop()
        self.set_event_loop(self.loop)

    @support.skip_unless_bind_unix_socket
    eleza test_create_unix_server_existing_path_sock(self):
        ukijumuisha test_utils.unix_socket_path() kama path:
            sock = socket.socket(socket.AF_UNIX)
            sock.bind(path)
            sock.listen(1)
            sock.close()

            coro = self.loop.create_unix_server(lambda: Tupu, path)
            srv = self.loop.run_until_complete(coro)
            srv.close()
            self.loop.run_until_complete(srv.wait_closed())

    @support.skip_unless_bind_unix_socket
    eleza test_create_unix_server_pathlib(self):
        ukijumuisha test_utils.unix_socket_path() kama path:
            path = pathlib.Path(path)
            srv_coro = self.loop.create_unix_server(lambda: Tupu, path)
            srv = self.loop.run_until_complete(srv_coro)
            srv.close()
            self.loop.run_until_complete(srv.wait_closed())

    eleza test_create_unix_connection_pathlib(self):
        ukijumuisha test_utils.unix_socket_path() kama path:
            path = pathlib.Path(path)
            coro = self.loop.create_unix_connection(lambda: Tupu, path)
            ukijumuisha self.assertRaises(FileNotFoundError):
                # If pathlib.Path wasn't supported, the exception would be
                # different.
                self.loop.run_until_complete(coro)

    eleza test_create_unix_server_existing_path_nonsock(self):
        ukijumuisha tempfile.NamedTemporaryFile() kama file:
            coro = self.loop.create_unix_server(lambda: Tupu, file.name)
            ukijumuisha self.assertRaisesRegex(OSError,
                                        'Address.*is already kwenye use'):
                self.loop.run_until_complete(coro)

    eleza test_create_unix_server_ssl_bool(self):
        coro = self.loop.create_unix_server(lambda: Tupu, path='spam',
                                            ssl=Kweli)
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    'ssl argument must be an SSLContext'):
            self.loop.run_until_complete(coro)

    eleza test_create_unix_server_nopath_nosock(self):
        coro = self.loop.create_unix_server(lambda: Tupu, path=Tupu)
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'path was sio specified, na no sock'):
            self.loop.run_until_complete(coro)

    eleza test_create_unix_server_path_inetsock(self):
        sock = socket.socket()
        ukijumuisha sock:
            coro = self.loop.create_unix_server(lambda: Tupu, path=Tupu,
                                                sock=sock)
            ukijumuisha self.assertRaisesRegex(ValueError,
                                        'A UNIX Domain Stream.*was expected'):
                self.loop.run_until_complete(coro)

    eleza test_create_unix_server_path_dgram(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        ukijumuisha sock:
            coro = self.loop.create_unix_server(lambda: Tupu, path=Tupu,
                                                sock=sock)
            ukijumuisha self.assertRaisesRegex(ValueError,
                                        'A UNIX Domain Stream.*was expected'):
                self.loop.run_until_complete(coro)

    @unittest.skipUnless(hasattr(socket, 'SOCK_NONBLOCK'),
                         'no socket.SOCK_NONBLOCK (linux only)')
    @support.skip_unless_bind_unix_socket
    eleza test_create_unix_server_path_stream_bittype(self):
        sock = socket.socket(
            socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        ukijumuisha tempfile.NamedTemporaryFile() kama file:
            fn = file.name
        jaribu:
            ukijumuisha sock:
                sock.bind(fn)
                coro = self.loop.create_unix_server(lambda: Tupu, path=Tupu,
                                                    sock=sock)
                srv = self.loop.run_until_complete(coro)
                srv.close()
                self.loop.run_until_complete(srv.wait_closed())
        mwishowe:
            os.unlink(fn)

    eleza test_create_unix_server_ssl_timeout_with_plain_sock(self):
        coro = self.loop.create_unix_server(lambda: Tupu, path='spam',
                                            ssl_handshake_timeout=1)
        ukijumuisha self.assertRaisesRegex(
                ValueError,
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl'):
            self.loop.run_until_complete(coro)

    eleza test_create_unix_connection_path_inetsock(self):
        sock = socket.socket()
        ukijumuisha sock:
            coro = self.loop.create_unix_connection(lambda: Tupu,
                                                    sock=sock)
            ukijumuisha self.assertRaisesRegex(ValueError,
                                        'A UNIX Domain Stream.*was expected'):
                self.loop.run_until_complete(coro)

    @mock.patch('asyncio.unix_events.socket')
    eleza test_create_unix_server_bind_error(self, m_socket):
        # Ensure that the socket ni closed on any bind error
        sock = mock.Mock()
        m_socket.socket.return_value = sock

        sock.bind.side_effect = OSError
        coro = self.loop.create_unix_server(lambda: Tupu, path="/test")
        ukijumuisha self.assertRaises(OSError):
            self.loop.run_until_complete(coro)
        self.assertKweli(sock.close.called)

        sock.bind.side_effect = MemoryError
        coro = self.loop.create_unix_server(lambda: Tupu, path="/test")
        ukijumuisha self.assertRaises(MemoryError):
            self.loop.run_until_complete(coro)
        self.assertKweli(sock.close.called)

    eleza test_create_unix_connection_path_sock(self):
        coro = self.loop.create_unix_connection(
            lambda: Tupu, os.devnull, sock=object())
        ukijumuisha self.assertRaisesRegex(ValueError, 'path na sock can sio be'):
            self.loop.run_until_complete(coro)

    eleza test_create_unix_connection_nopath_nosock(self):
        coro = self.loop.create_unix_connection(
            lambda: Tupu, Tupu)
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'no path na sock were specified'):
            self.loop.run_until_complete(coro)

    eleza test_create_unix_connection_nossl_serverhost(self):
        coro = self.loop.create_unix_connection(
            lambda: Tupu, os.devnull, server_hostname='spam')
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    'server_hostname ni only meaningful'):
            self.loop.run_until_complete(coro)

    eleza test_create_unix_connection_ssl_noserverhost(self):
        coro = self.loop.create_unix_connection(
            lambda: Tupu, os.devnull, ssl=Kweli)

        ukijumuisha self.assertRaisesRegex(
            ValueError, 'you have to pita server_hostname when using ssl'):

            self.loop.run_until_complete(coro)

    eleza test_create_unix_connection_ssl_timeout_with_plain_sock(self):
        coro = self.loop.create_unix_connection(lambda: Tupu, path='spam',
                                            ssl_handshake_timeout=1)
        ukijumuisha self.assertRaisesRegex(
                ValueError,
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl'):
            self.loop.run_until_complete(coro)


@unittest.skipUnless(hasattr(os, 'sendfile'),
                     'sendfile ni sio supported')
kundi SelectorEventLoopUnixSockSendfileTests(test_utils.TestCase):
    DATA = b"12345abcde" * 16 * 1024  # 160 KiB

    kundi MyProto(asyncio.Protocol):

        eleza __init__(self, loop):
            self.started = Uongo
            self.closed = Uongo
            self.data = bytearray()
            self.fut = loop.create_future()
            self.transport = Tupu
            self._ready = loop.create_future()

        eleza connection_made(self, transport):
            self.started = Kweli
            self.transport = transport
            self._ready.set_result(Tupu)

        eleza data_received(self, data):
            self.data.extend(data)

        eleza connection_lost(self, exc):
            self.closed = Kweli
            self.fut.set_result(Tupu)

        async eleza wait_closed(self):
            await self.fut

    @classmethod
    eleza setUpClass(cls):
        ukijumuisha open(support.TESTFN, 'wb') kama fp:
            fp.write(cls.DATA)
        super().setUpClass()

    @classmethod
    eleza tearDownClass(cls):
        support.unlink(support.TESTFN)
        super().tearDownClass()

    eleza setUp(self):
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)
        self.file = open(support.TESTFN, 'rb')
        self.addCleanup(self.file.close)
        super().setUp()

    eleza make_socket(self, cleanup=Kweli):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(Uongo)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
        ikiwa cleanup:
            self.addCleanup(sock.close)
        rudisha sock

    eleza run_loop(self, coro):
        rudisha self.loop.run_until_complete(coro)

    eleza prepare(self):
        sock = self.make_socket()
        proto = self.MyProto(self.loop)
        port = support.find_unused_port()
        srv_sock = self.make_socket(cleanup=Uongo)
        srv_sock.bind((support.HOST, port))
        server = self.run_loop(self.loop.create_server(
            lambda: proto, sock=srv_sock))
        self.run_loop(self.loop.sock_connect(sock, (support.HOST, port)))
        self.run_loop(proto._ready)

        eleza cleanup():
            proto.transport.close()
            self.run_loop(proto.wait_closed())

            server.close()
            self.run_loop(server.wait_closed())

        self.addCleanup(cleanup)

        rudisha sock, proto

    eleza test_sock_sendfile_not_available(self):
        sock, proto = self.prepare()
        ukijumuisha mock.patch('asyncio.unix_events.os', spec=[]):
            ukijumuisha self.assertRaisesRegex(asyncio.SendfileNotAvailableError,
                                        "os[.]sendfile[(][)] ni sio available"):
                self.run_loop(self.loop._sock_sendfile_native(sock, self.file,
                                                              0, Tupu))
        self.assertEqual(self.file.tell(), 0)

    eleza test_sock_sendfile_not_a_file(self):
        sock, proto = self.prepare()
        f = object()
        ukijumuisha self.assertRaisesRegex(asyncio.SendfileNotAvailableError,
                                    "sio a regular file"):
            self.run_loop(self.loop._sock_sendfile_native(sock, f,
                                                          0, Tupu))
        self.assertEqual(self.file.tell(), 0)

    eleza test_sock_sendfile_iobuffer(self):
        sock, proto = self.prepare()
        f = io.BytesIO()
        ukijumuisha self.assertRaisesRegex(asyncio.SendfileNotAvailableError,
                                    "sio a regular file"):
            self.run_loop(self.loop._sock_sendfile_native(sock, f,
                                                          0, Tupu))
        self.assertEqual(self.file.tell(), 0)

    eleza test_sock_sendfile_not_regular_file(self):
        sock, proto = self.prepare()
        f = mock.Mock()
        f.fileno.return_value = -1
        ukijumuisha self.assertRaisesRegex(asyncio.SendfileNotAvailableError,
                                    "sio a regular file"):
            self.run_loop(self.loop._sock_sendfile_native(sock, f,
                                                          0, Tupu))
        self.assertEqual(self.file.tell(), 0)

    eleza test_sock_sendfile_cancel1(self):
        sock, proto = self.prepare()

        fut = self.loop.create_future()
        fileno = self.file.fileno()
        self.loop._sock_sendfile_native_impl(fut, Tupu, sock, fileno,
                                             0, Tupu, len(self.DATA), 0)
        fut.cancel()
        ukijumuisha contextlib.suppress(asyncio.CancelledError):
            self.run_loop(fut)
        ukijumuisha self.assertRaises(KeyError):
            self.loop._selector.get_key(sock)

    eleza test_sock_sendfile_cancel2(self):
        sock, proto = self.prepare()

        fut = self.loop.create_future()
        fileno = self.file.fileno()
        self.loop._sock_sendfile_native_impl(fut, Tupu, sock, fileno,
                                             0, Tupu, len(self.DATA), 0)
        fut.cancel()
        self.loop._sock_sendfile_native_impl(fut, sock.fileno(), sock, fileno,
                                             0, Tupu, len(self.DATA), 0)
        ukijumuisha self.assertRaises(KeyError):
            self.loop._selector.get_key(sock)

    eleza test_sock_sendfile_blocking_error(self):
        sock, proto = self.prepare()

        fileno = self.file.fileno()
        fut = mock.Mock()
        fut.cancelled.return_value = Uongo
        ukijumuisha mock.patch('os.sendfile', side_effect=BlockingIOError()):
            self.loop._sock_sendfile_native_impl(fut, Tupu, sock, fileno,
                                                 0, Tupu, len(self.DATA), 0)
        key = self.loop._selector.get_key(sock)
        self.assertIsNotTupu(key)
        fut.add_done_callback.assert_called_once_with(mock.ANY)

    eleza test_sock_sendfile_os_error_first_call(self):
        sock, proto = self.prepare()

        fileno = self.file.fileno()
        fut = self.loop.create_future()
        ukijumuisha mock.patch('os.sendfile', side_effect=OSError()):
            self.loop._sock_sendfile_native_impl(fut, Tupu, sock, fileno,
                                                 0, Tupu, len(self.DATA), 0)
        ukijumuisha self.assertRaises(KeyError):
            self.loop._selector.get_key(sock)
        exc = fut.exception()
        self.assertIsInstance(exc, asyncio.SendfileNotAvailableError)
        self.assertEqual(0, self.file.tell())

    eleza test_sock_sendfile_os_error_next_call(self):
        sock, proto = self.prepare()

        fileno = self.file.fileno()
        fut = self.loop.create_future()
        err = OSError()
        ukijumuisha mock.patch('os.sendfile', side_effect=err):
            self.loop._sock_sendfile_native_impl(fut, sock.fileno(),
                                                 sock, fileno,
                                                 1000, Tupu, len(self.DATA),
                                                 1000)
        ukijumuisha self.assertRaises(KeyError):
            self.loop._selector.get_key(sock)
        exc = fut.exception()
        self.assertIs(exc, err)
        self.assertEqual(1000, self.file.tell())

    eleza test_sock_sendfile_exception(self):
        sock, proto = self.prepare()

        fileno = self.file.fileno()
        fut = self.loop.create_future()
        err = asyncio.SendfileNotAvailableError()
        ukijumuisha mock.patch('os.sendfile', side_effect=err):
            self.loop._sock_sendfile_native_impl(fut, sock.fileno(),
                                                 sock, fileno,
                                                 1000, Tupu, len(self.DATA),
                                                 1000)
        ukijumuisha self.assertRaises(KeyError):
            self.loop._selector.get_key(sock)
        exc = fut.exception()
        self.assertIs(exc, err)
        self.assertEqual(1000, self.file.tell())


kundi UnixReadPipeTransportTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.Protocol)
        self.pipe = mock.Mock(spec_set=io.RawIOBase)
        self.pipe.fileno.return_value = 5

        blocking_patcher = mock.patch('os.set_blocking')
        blocking_patcher.start()
        self.addCleanup(blocking_patcher.stop)

        fstat_patcher = mock.patch('os.fstat')
        m_fstat = fstat_patcher.start()
        st = mock.Mock()
        st.st_mode = stat.S_IFIFO
        m_fstat.return_value = st
        self.addCleanup(fstat_patcher.stop)

    eleza read_pipe_transport(self, waiter=Tupu):
        transport = unix_events._UnixReadPipeTransport(self.loop, self.pipe,
                                                       self.protocol,
                                                       waiter=waiter)
        self.addCleanup(close_pipe_transport, transport)
        rudisha transport

    eleza test_ctor(self):
        waiter = self.loop.create_future()
        tr = self.read_pipe_transport(waiter=waiter)
        self.loop.run_until_complete(waiter)

        self.protocol.connection_made.assert_called_with(tr)
        self.loop.assert_reader(5, tr._read_ready)
        self.assertIsTupu(waiter.result())

    @mock.patch('os.read')
    eleza test__read_ready(self, m_read):
        tr = self.read_pipe_transport()
        m_read.return_value = b'data'
        tr._read_ready()

        m_read.assert_called_with(5, tr.max_size)
        self.protocol.data_received.assert_called_with(b'data')

    @mock.patch('os.read')
    eleza test__read_ready_eof(self, m_read):
        tr = self.read_pipe_transport()
        m_read.return_value = b''
        tr._read_ready()

        m_read.assert_called_with(5, tr.max_size)
        self.assertUongo(self.loop.readers)
        test_utils.run_briefly(self.loop)
        self.protocol.eof_received.assert_called_with()
        self.protocol.connection_lost.assert_called_with(Tupu)

    @mock.patch('os.read')
    eleza test__read_ready_blocked(self, m_read):
        tr = self.read_pipe_transport()
        m_read.side_effect = BlockingIOError
        tr._read_ready()

        m_read.assert_called_with(5, tr.max_size)
        test_utils.run_briefly(self.loop)
        self.assertUongo(self.protocol.data_received.called)

    @mock.patch('asyncio.log.logger.error')
    @mock.patch('os.read')
    eleza test__read_ready_error(self, m_read, m_logexc):
        tr = self.read_pipe_transport()
        err = OSError()
        m_read.side_effect = err
        tr._close = mock.Mock()
        tr._read_ready()

        m_read.assert_called_with(5, tr.max_size)
        tr._close.assert_called_with(err)
        m_logexc.assert_called_with(
            test_utils.MockPattern(
                'Fatal read error on pipe transport'
                '\nprotocol:.*\ntransport:.*'),
            exc_info=(OSError, MOCK_ANY, MOCK_ANY))

    @mock.patch('os.read')
    eleza test_pause_reading(self, m_read):
        tr = self.read_pipe_transport()
        m = mock.Mock()
        self.loop.add_reader(5, m)
        tr.pause_reading()
        self.assertUongo(self.loop.readers)

    @mock.patch('os.read')
    eleza test_resume_reading(self, m_read):
        tr = self.read_pipe_transport()
        tr.pause_reading()
        tr.resume_reading()
        self.loop.assert_reader(5, tr._read_ready)

    @mock.patch('os.read')
    eleza test_close(self, m_read):
        tr = self.read_pipe_transport()
        tr._close = mock.Mock()
        tr.close()
        tr._close.assert_called_with(Tupu)

    @mock.patch('os.read')
    eleza test_close_already_closing(self, m_read):
        tr = self.read_pipe_transport()
        tr._closing = Kweli
        tr._close = mock.Mock()
        tr.close()
        self.assertUongo(tr._close.called)

    @mock.patch('os.read')
    eleza test__close(self, m_read):
        tr = self.read_pipe_transport()
        err = object()
        tr._close(err)
        self.assertKweli(tr.is_closing())
        self.assertUongo(self.loop.readers)
        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(err)

    eleza test__call_connection_lost(self):
        tr = self.read_pipe_transport()
        self.assertIsNotTupu(tr._protocol)
        self.assertIsNotTupu(tr._loop)

        err = Tupu
        tr._call_connection_lost(err)
        self.protocol.connection_lost.assert_called_with(err)
        self.pipe.close.assert_called_with()

        self.assertIsTupu(tr._protocol)
        self.assertIsTupu(tr._loop)

    eleza test__call_connection_lost_with_err(self):
        tr = self.read_pipe_transport()
        self.assertIsNotTupu(tr._protocol)
        self.assertIsNotTupu(tr._loop)

        err = OSError()
        tr._call_connection_lost(err)
        self.protocol.connection_lost.assert_called_with(err)
        self.pipe.close.assert_called_with()

        self.assertIsTupu(tr._protocol)
        self.assertIsTupu(tr._loop)

    eleza test_pause_reading_on_closed_pipe(self):
        tr = self.read_pipe_transport()
        tr.close()
        test_utils.run_briefly(self.loop)
        self.assertIsTupu(tr._loop)
        tr.pause_reading()

    eleza test_pause_reading_on_paused_pipe(self):
        tr = self.read_pipe_transport()
        tr.pause_reading()
        # the second call should do nothing
        tr.pause_reading()

    eleza test_resume_reading_on_closed_pipe(self):
        tr = self.read_pipe_transport()
        tr.close()
        test_utils.run_briefly(self.loop)
        self.assertIsTupu(tr._loop)
        tr.resume_reading()

    eleza test_resume_reading_on_paused_pipe(self):
        tr = self.read_pipe_transport()
        # the pipe ni sio paused
        # resuming should do nothing
        tr.resume_reading()


kundi UnixWritePipeTransportTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.BaseProtocol)
        self.pipe = mock.Mock(spec_set=io.RawIOBase)
        self.pipe.fileno.return_value = 5

        blocking_patcher = mock.patch('os.set_blocking')
        blocking_patcher.start()
        self.addCleanup(blocking_patcher.stop)

        fstat_patcher = mock.patch('os.fstat')
        m_fstat = fstat_patcher.start()
        st = mock.Mock()
        st.st_mode = stat.S_IFSOCK
        m_fstat.return_value = st
        self.addCleanup(fstat_patcher.stop)

    eleza write_pipe_transport(self, waiter=Tupu):
        transport = unix_events._UnixWritePipeTransport(self.loop, self.pipe,
                                                        self.protocol,
                                                        waiter=waiter)
        self.addCleanup(close_pipe_transport, transport)
        rudisha transport

    eleza test_ctor(self):
        waiter = self.loop.create_future()
        tr = self.write_pipe_transport(waiter=waiter)
        self.loop.run_until_complete(waiter)

        self.protocol.connection_made.assert_called_with(tr)
        self.loop.assert_reader(5, tr._read_ready)
        self.assertEqual(Tupu, waiter.result())

    eleza test_can_write_eof(self):
        tr = self.write_pipe_transport()
        self.assertKweli(tr.can_write_eof())

    @mock.patch('os.write')
    eleza test_write(self, m_write):
        tr = self.write_pipe_transport()
        m_write.return_value = 4
        tr.write(b'data')
        m_write.assert_called_with(5, b'data')
        self.assertUongo(self.loop.writers)
        self.assertEqual(bytearray(), tr._buffer)

    @mock.patch('os.write')
    eleza test_write_no_data(self, m_write):
        tr = self.write_pipe_transport()
        tr.write(b'')
        self.assertUongo(m_write.called)
        self.assertUongo(self.loop.writers)
        self.assertEqual(bytearray(b''), tr._buffer)

    @mock.patch('os.write')
    eleza test_write_partial(self, m_write):
        tr = self.write_pipe_transport()
        m_write.return_value = 2
        tr.write(b'data')
        self.loop.assert_writer(5, tr._write_ready)
        self.assertEqual(bytearray(b'ta'), tr._buffer)

    @mock.patch('os.write')
    eleza test_write_buffer(self, m_write):
        tr = self.write_pipe_transport()
        self.loop.add_writer(5, tr._write_ready)
        tr._buffer = bytearray(b'previous')
        tr.write(b'data')
        self.assertUongo(m_write.called)
        self.loop.assert_writer(5, tr._write_ready)
        self.assertEqual(bytearray(b'previousdata'), tr._buffer)

    @mock.patch('os.write')
    eleza test_write_again(self, m_write):
        tr = self.write_pipe_transport()
        m_write.side_effect = BlockingIOError()
        tr.write(b'data')
        m_write.assert_called_with(5, bytearray(b'data'))
        self.loop.assert_writer(5, tr._write_ready)
        self.assertEqual(bytearray(b'data'), tr._buffer)

    @mock.patch('asyncio.unix_events.logger')
    @mock.patch('os.write')
    eleza test_write_err(self, m_write, m_log):
        tr = self.write_pipe_transport()
        err = OSError()
        m_write.side_effect = err
        tr._fatal_error = mock.Mock()
        tr.write(b'data')
        m_write.assert_called_with(5, b'data')
        self.assertUongo(self.loop.writers)
        self.assertEqual(bytearray(), tr._buffer)
        tr._fatal_error.assert_called_with(
                            err,
                            'Fatal write error on pipe transport')
        self.assertEqual(1, tr._conn_lost)

        tr.write(b'data')
        self.assertEqual(2, tr._conn_lost)
        tr.write(b'data')
        tr.write(b'data')
        tr.write(b'data')
        tr.write(b'data')
        # This ni a bit overspecified. :-(
        m_log.warning.assert_called_with(
            'pipe closed by peer ama os.write(pipe, data) raised exception.')
        tr.close()

    @mock.patch('os.write')
    eleza test_write_close(self, m_write):
        tr = self.write_pipe_transport()
        tr._read_ready()  # pipe was closed by peer

        tr.write(b'data')
        self.assertEqual(tr._conn_lost, 1)
        tr.write(b'data')
        self.assertEqual(tr._conn_lost, 2)

    eleza test__read_ready(self):
        tr = self.write_pipe_transport()
        tr._read_ready()
        self.assertUongo(self.loop.readers)
        self.assertUongo(self.loop.writers)
        self.assertKweli(tr.is_closing())
        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(Tupu)

    @mock.patch('os.write')
    eleza test__write_ready(self, m_write):
        tr = self.write_pipe_transport()
        self.loop.add_writer(5, tr._write_ready)
        tr._buffer = bytearray(b'data')
        m_write.return_value = 4
        tr._write_ready()
        self.assertUongo(self.loop.writers)
        self.assertEqual(bytearray(), tr._buffer)

    @mock.patch('os.write')
    eleza test__write_ready_partial(self, m_write):
        tr = self.write_pipe_transport()
        self.loop.add_writer(5, tr._write_ready)
        tr._buffer = bytearray(b'data')
        m_write.return_value = 3
        tr._write_ready()
        self.loop.assert_writer(5, tr._write_ready)
        self.assertEqual(bytearray(b'a'), tr._buffer)

    @mock.patch('os.write')
    eleza test__write_ready_again(self, m_write):
        tr = self.write_pipe_transport()
        self.loop.add_writer(5, tr._write_ready)
        tr._buffer = bytearray(b'data')
        m_write.side_effect = BlockingIOError()
        tr._write_ready()
        m_write.assert_called_with(5, bytearray(b'data'))
        self.loop.assert_writer(5, tr._write_ready)
        self.assertEqual(bytearray(b'data'), tr._buffer)

    @mock.patch('os.write')
    eleza test__write_ready_empty(self, m_write):
        tr = self.write_pipe_transport()
        self.loop.add_writer(5, tr._write_ready)
        tr._buffer = bytearray(b'data')
        m_write.return_value = 0
        tr._write_ready()
        m_write.assert_called_with(5, bytearray(b'data'))
        self.loop.assert_writer(5, tr._write_ready)
        self.assertEqual(bytearray(b'data'), tr._buffer)

    @mock.patch('asyncio.log.logger.error')
    @mock.patch('os.write')
    eleza test__write_ready_err(self, m_write, m_logexc):
        tr = self.write_pipe_transport()
        self.loop.add_writer(5, tr._write_ready)
        tr._buffer = bytearray(b'data')
        m_write.side_effect = err = OSError()
        tr._write_ready()
        self.assertUongo(self.loop.writers)
        self.assertUongo(self.loop.readers)
        self.assertEqual(bytearray(), tr._buffer)
        self.assertKweli(tr.is_closing())
        m_logexc.assert_not_called()
        self.assertEqual(1, tr._conn_lost)
        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(err)

    @mock.patch('os.write')
    eleza test__write_ready_closing(self, m_write):
        tr = self.write_pipe_transport()
        self.loop.add_writer(5, tr._write_ready)
        tr._closing = Kweli
        tr._buffer = bytearray(b'data')
        m_write.return_value = 4
        tr._write_ready()
        self.assertUongo(self.loop.writers)
        self.assertUongo(self.loop.readers)
        self.assertEqual(bytearray(), tr._buffer)
        self.protocol.connection_lost.assert_called_with(Tupu)
        self.pipe.close.assert_called_with()

    @mock.patch('os.write')
    eleza test_abort(self, m_write):
        tr = self.write_pipe_transport()
        self.loop.add_writer(5, tr._write_ready)
        self.loop.add_reader(5, tr._read_ready)
        tr._buffer = [b'da', b'ta']
        tr.abort()
        self.assertUongo(m_write.called)
        self.assertUongo(self.loop.readers)
        self.assertUongo(self.loop.writers)
        self.assertEqual([], tr._buffer)
        self.assertKweli(tr.is_closing())
        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(Tupu)

    eleza test__call_connection_lost(self):
        tr = self.write_pipe_transport()
        self.assertIsNotTupu(tr._protocol)
        self.assertIsNotTupu(tr._loop)

        err = Tupu
        tr._call_connection_lost(err)
        self.protocol.connection_lost.assert_called_with(err)
        self.pipe.close.assert_called_with()

        self.assertIsTupu(tr._protocol)
        self.assertIsTupu(tr._loop)

    eleza test__call_connection_lost_with_err(self):
        tr = self.write_pipe_transport()
        self.assertIsNotTupu(tr._protocol)
        self.assertIsNotTupu(tr._loop)

        err = OSError()
        tr._call_connection_lost(err)
        self.protocol.connection_lost.assert_called_with(err)
        self.pipe.close.assert_called_with()

        self.assertIsTupu(tr._protocol)
        self.assertIsTupu(tr._loop)

    eleza test_close(self):
        tr = self.write_pipe_transport()
        tr.write_eof = mock.Mock()
        tr.close()
        tr.write_eof.assert_called_with()

        # closing the transport twice must sio fail
        tr.close()

    eleza test_close_closing(self):
        tr = self.write_pipe_transport()
        tr.write_eof = mock.Mock()
        tr._closing = Kweli
        tr.close()
        self.assertUongo(tr.write_eof.called)

    eleza test_write_eof(self):
        tr = self.write_pipe_transport()
        tr.write_eof()
        self.assertKweli(tr.is_closing())
        self.assertUongo(self.loop.readers)
        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(Tupu)

    eleza test_write_eof_pending(self):
        tr = self.write_pipe_transport()
        tr._buffer = [b'data']
        tr.write_eof()
        self.assertKweli(tr.is_closing())
        self.assertUongo(self.protocol.connection_lost.called)


kundi AbstractChildWatcherTests(unittest.TestCase):

    eleza test_not_implemented(self):
        f = mock.Mock()
        watcher = asyncio.AbstractChildWatcher()
        self.assertRaises(
            NotImplementedError, watcher.add_child_handler, f, f)
        self.assertRaises(
            NotImplementedError, watcher.remove_child_handler, f)
        self.assertRaises(
            NotImplementedError, watcher.attach_loop, f)
        self.assertRaises(
            NotImplementedError, watcher.close)
        self.assertRaises(
            NotImplementedError, watcher.is_active)
        self.assertRaises(
            NotImplementedError, watcher.__enter__)
        self.assertRaises(
            NotImplementedError, watcher.__exit__, f, f, f)


kundi BaseChildWatcherTests(unittest.TestCase):

    eleza test_not_implemented(self):
        f = mock.Mock()
        watcher = unix_events.BaseChildWatcher()
        self.assertRaises(
            NotImplementedError, watcher._do_waitpid, f)


WaitPidMocks = collections.namedtuple("WaitPidMocks",
                                      ("waitpid",
                                       "WIFEXITED",
                                       "WIFSIGNALED",
                                       "WEXITSTATUS",
                                       "WTERMSIG",
                                       ))


kundi ChildWatcherTestsMixin:

    ignore_warnings = mock.patch.object(log.logger, "warning")

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.running = Uongo
        self.zombies = {}

        ukijumuisha mock.patch.object(
                self.loop, "add_signal_handler") kama self.m_add_signal_handler:
            self.watcher = self.create_watcher()
            self.watcher.attach_loop(self.loop)

    eleza waitpid(self, pid, flags):
        ikiwa isinstance(self.watcher, asyncio.SafeChildWatcher) ama pid != -1:
            self.assertGreater(pid, 0)
        jaribu:
            ikiwa pid < 0:
                rudisha self.zombies.popitem()
            isipokua:
                rudisha pid, self.zombies.pop(pid)
        tatizo KeyError:
            pita
        ikiwa self.running:
            rudisha 0, 0
        isipokua:
            ashiria ChildProcessError()

    eleza add_zombie(self, pid, returncode):
        self.zombies[pid] = returncode + 32768

    eleza WIFEXITED(self, status):
        rudisha status >= 32768

    eleza WIFSIGNALED(self, status):
        rudisha 32700 < status < 32768

    eleza WEXITSTATUS(self, status):
        self.assertKweli(self.WIFEXITED(status))
        rudisha status - 32768

    eleza WTERMSIG(self, status):
        self.assertKweli(self.WIFSIGNALED(status))
        rudisha 32768 - status

    eleza test_create_watcher(self):
        self.m_add_signal_handler.assert_called_once_with(
            signal.SIGCHLD, self.watcher._sig_chld)

    eleza waitpid_mocks(func):
        eleza wrapped_func(self):
            eleza patch(target, wrapper):
                rudisha mock.patch(target, wraps=wrapper,
                                  new_callable=mock.Mock)

            ukijumuisha patch('os.WTERMSIG', self.WTERMSIG) kama m_WTERMSIG, \
                 patch('os.WEXITSTATUS', self.WEXITSTATUS) kama m_WEXITSTATUS, \
                 patch('os.WIFSIGNALED', self.WIFSIGNALED) kama m_WIFSIGNALED, \
                 patch('os.WIFEXITED', self.WIFEXITED) kama m_WIFEXITED, \
                 patch('os.waitpid', self.waitpid) kama m_waitpid:
                func(self, WaitPidMocks(m_waitpid,
                                        m_WIFEXITED, m_WIFSIGNALED,
                                        m_WEXITSTATUS, m_WTERMSIG,
                                        ))
        rudisha wrapped_func

    @waitpid_mocks
    eleza test_sigchld(self, m):
        # register a child
        callback = mock.Mock()

        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(42, callback, 9, 10, 14)

        self.assertUongo(callback.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # child ni running
        self.watcher._sig_chld()

        self.assertUongo(callback.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # child terminates (returncode 12)
        self.running = Uongo
        self.add_zombie(42, 12)
        self.watcher._sig_chld()

        self.assertKweli(m.WIFEXITED.called)
        self.assertKweli(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)
        callback.assert_called_once_with(42, 12, 9, 10, 14)

        m.WIFSIGNALED.reset_mock()
        m.WIFEXITED.reset_mock()
        m.WEXITSTATUS.reset_mock()
        callback.reset_mock()

        # ensure that the child ni effectively reaped
        self.add_zombie(42, 13)
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        self.assertUongo(callback.called)
        self.assertUongo(m.WTERMSIG.called)

        m.WIFSIGNALED.reset_mock()
        m.WIFEXITED.reset_mock()
        m.WEXITSTATUS.reset_mock()

        # sigchld called again
        self.zombies.clear()
        self.watcher._sig_chld()

        self.assertUongo(callback.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

    @waitpid_mocks
    eleza test_sigchld_two_children(self, m):
        callback1 = mock.Mock()
        callback2 = mock.Mock()

        # register child 1
        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(43, callback1, 7, 8)

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # register child 2
        ukijumuisha self.watcher:
            self.watcher.add_child_handler(44, callback2, 147, 18)

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # children are running
        self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # child 1 terminates (signal 3)
        self.add_zombie(43, -3)
        self.watcher._sig_chld()

        callback1.assert_called_once_with(43, -3, 7, 8)
        self.assertUongo(callback2.called)
        self.assertKweli(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertKweli(m.WTERMSIG.called)

        m.WIFSIGNALED.reset_mock()
        m.WIFEXITED.reset_mock()
        m.WTERMSIG.reset_mock()
        callback1.reset_mock()

        # child 2 still running
        self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # child 2 terminates (code 108)
        self.add_zombie(44, 108)
        self.running = Uongo
        self.watcher._sig_chld()

        callback2.assert_called_once_with(44, 108, 147, 18)
        self.assertUongo(callback1.called)
        self.assertKweli(m.WIFEXITED.called)
        self.assertKweli(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        m.WIFSIGNALED.reset_mock()
        m.WIFEXITED.reset_mock()
        m.WEXITSTATUS.reset_mock()
        callback2.reset_mock()

        # ensure that the children are effectively reaped
        self.add_zombie(43, 14)
        self.add_zombie(44, 15)
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WTERMSIG.called)

        m.WIFSIGNALED.reset_mock()
        m.WIFEXITED.reset_mock()
        m.WEXITSTATUS.reset_mock()

        # sigchld called again
        self.zombies.clear()
        self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

    @waitpid_mocks
    eleza test_sigchld_two_children_terminating_together(self, m):
        callback1 = mock.Mock()
        callback2 = mock.Mock()

        # register child 1
        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(45, callback1, 17, 8)

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # register child 2
        ukijumuisha self.watcher:
            self.watcher.add_child_handler(46, callback2, 1147, 18)

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # children are running
        self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # child 1 terminates (code 78)
        # child 2 terminates (signal 5)
        self.add_zombie(45, 78)
        self.add_zombie(46, -5)
        self.running = Uongo
        self.watcher._sig_chld()

        callback1.assert_called_once_with(45, 78, 17, 8)
        callback2.assert_called_once_with(46, -5, 1147, 18)
        self.assertKweli(m.WIFSIGNALED.called)
        self.assertKweli(m.WIFEXITED.called)
        self.assertKweli(m.WEXITSTATUS.called)
        self.assertKweli(m.WTERMSIG.called)

        m.WIFSIGNALED.reset_mock()
        m.WIFEXITED.reset_mock()
        m.WTERMSIG.reset_mock()
        m.WEXITSTATUS.reset_mock()
        callback1.reset_mock()
        callback2.reset_mock()

        # ensure that the children are effectively reaped
        self.add_zombie(45, 14)
        self.add_zombie(46, 15)
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WTERMSIG.called)

    @waitpid_mocks
    eleza test_sigchld_race_condition(self, m):
        # register a child
        callback = mock.Mock()

        ukijumuisha self.watcher:
            # child terminates before being registered
            self.add_zombie(50, 4)
            self.watcher._sig_chld()

            self.watcher.add_child_handler(50, callback, 1, 12)

        callback.assert_called_once_with(50, 4, 1, 12)
        callback.reset_mock()

        # ensure that the child ni effectively reaped
        self.add_zombie(50, -1)
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        self.assertUongo(callback.called)

    @waitpid_mocks
    eleza test_sigchld_replace_handler(self, m):
        callback1 = mock.Mock()
        callback2 = mock.Mock()

        # register a child
        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(51, callback1, 19)

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # register the same child again
        ukijumuisha self.watcher:
            self.watcher.add_child_handler(51, callback2, 21)

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # child terminates (signal 8)
        self.running = Uongo
        self.add_zombie(51, -8)
        self.watcher._sig_chld()

        callback2.assert_called_once_with(51, -8, 21)
        self.assertUongo(callback1.called)
        self.assertKweli(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertKweli(m.WTERMSIG.called)

        m.WIFSIGNALED.reset_mock()
        m.WIFEXITED.reset_mock()
        m.WTERMSIG.reset_mock()
        callback2.reset_mock()

        # ensure that the child ni effectively reaped
        self.add_zombie(51, 13)
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(m.WTERMSIG.called)

    @waitpid_mocks
    eleza test_sigchld_remove_handler(self, m):
        callback = mock.Mock()

        # register a child
        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(52, callback, 1984)

        self.assertUongo(callback.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # unregister the child
        self.watcher.remove_child_handler(52)

        self.assertUongo(callback.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # child terminates (code 99)
        self.running = Uongo
        self.add_zombie(52, 99)
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        self.assertUongo(callback.called)

    @waitpid_mocks
    eleza test_sigchld_unknown_status(self, m):
        callback = mock.Mock()

        # register a child
        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(53, callback, -19)

        self.assertUongo(callback.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # terminate ukijumuisha unknown status
        self.zombies[53] = 1178
        self.running = Uongo
        self.watcher._sig_chld()

        callback.assert_called_once_with(53, 1178, -19)
        self.assertKweli(m.WIFEXITED.called)
        self.assertKweli(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        callback.reset_mock()
        m.WIFEXITED.reset_mock()
        m.WIFSIGNALED.reset_mock()

        # ensure that the child ni effectively reaped
        self.add_zombie(53, 101)
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        self.assertUongo(callback.called)

    @waitpid_mocks
    eleza test_remove_child_handler(self, m):
        callback1 = mock.Mock()
        callback2 = mock.Mock()
        callback3 = mock.Mock()

        # register children
        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(54, callback1, 1)
            self.watcher.add_child_handler(55, callback2, 2)
            self.watcher.add_child_handler(56, callback3, 3)

        # remove child handler 1
        self.assertKweli(self.watcher.remove_child_handler(54))

        # remove child handler 2 multiple times
        self.assertKweli(self.watcher.remove_child_handler(55))
        self.assertUongo(self.watcher.remove_child_handler(55))
        self.assertUongo(self.watcher.remove_child_handler(55))

        # all children terminate
        self.add_zombie(54, 0)
        self.add_zombie(55, 1)
        self.add_zombie(56, 2)
        self.running = Uongo
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        callback3.assert_called_once_with(56, 2, 3)

    @waitpid_mocks
    eleza test_sigchld_unhandled_exception(self, m):
        callback = mock.Mock()

        # register a child
        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(57, callback)

        # ashiria an exception
        m.waitpid.side_effect = ValueError

        ukijumuisha mock.patch.object(log.logger,
                               'error') kama m_error:

            self.assertEqual(self.watcher._sig_chld(), Tupu)
            self.assertKweli(m_error.called)

    @waitpid_mocks
    eleza test_sigchld_child_reaped_elsewhere(self, m):
        # register a child
        callback = mock.Mock()

        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(58, callback)

        self.assertUongo(callback.called)
        self.assertUongo(m.WIFEXITED.called)
        self.assertUongo(m.WIFSIGNALED.called)
        self.assertUongo(m.WEXITSTATUS.called)
        self.assertUongo(m.WTERMSIG.called)

        # child terminates
        self.running = Uongo
        self.add_zombie(58, 4)

        # waitpid ni called elsewhere
        os.waitpid(58, os.WNOHANG)

        m.waitpid.reset_mock()

        # sigchld
        ukijumuisha self.ignore_warnings:
            self.watcher._sig_chld()

        ikiwa isinstance(self.watcher, asyncio.FastChildWatcher):
            # here the FastChildWatche enters a deadlock
            # (there ni no way to prevent it)
            self.assertUongo(callback.called)
        isipokua:
            callback.assert_called_once_with(58, 255)

    @waitpid_mocks
    eleza test_sigchld_unknown_pid_during_registration(self, m):
        # register two children
        callback1 = mock.Mock()
        callback2 = mock.Mock()

        ukijumuisha self.ignore_warnings, self.watcher:
            self.running = Kweli
            # child 1 terminates
            self.add_zombie(591, 7)
            # an unknown child terminates
            self.add_zombie(593, 17)

            self.watcher._sig_chld()

            self.watcher.add_child_handler(591, callback1)
            self.watcher.add_child_handler(592, callback2)

        callback1.assert_called_once_with(591, 7)
        self.assertUongo(callback2.called)

    @waitpid_mocks
    eleza test_set_loop(self, m):
        # register a child
        callback = mock.Mock()

        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(60, callback)

        # attach a new loop
        old_loop = self.loop
        self.loop = self.new_test_loop()
        patch = mock.patch.object

        ukijumuisha patch(old_loop, "remove_signal_handler") kama m_old_remove, \
             patch(self.loop, "add_signal_handler") kama m_new_add:

            self.watcher.attach_loop(self.loop)

            m_old_remove.assert_called_once_with(
                signal.SIGCHLD)
            m_new_add.assert_called_once_with(
                signal.SIGCHLD, self.watcher._sig_chld)

        # child terminates
        self.running = Uongo
        self.add_zombie(60, 9)
        self.watcher._sig_chld()

        callback.assert_called_once_with(60, 9)

    @waitpid_mocks
    eleza test_set_loop_race_condition(self, m):
        # register 3 children
        callback1 = mock.Mock()
        callback2 = mock.Mock()
        callback3 = mock.Mock()

        ukijumuisha self.watcher:
            self.running = Kweli
            self.watcher.add_child_handler(61, callback1)
            self.watcher.add_child_handler(62, callback2)
            self.watcher.add_child_handler(622, callback3)

        # detach the loop
        old_loop = self.loop
        self.loop = Tupu

        ukijumuisha mock.patch.object(
                old_loop, "remove_signal_handler") kama m_remove_signal_handler:

            ukijumuisha self.assertWarnsRegex(
                    RuntimeWarning, 'A loop ni being detached'):
                self.watcher.attach_loop(Tupu)

            m_remove_signal_handler.assert_called_once_with(
                signal.SIGCHLD)

        # child 1 & 2 terminate
        self.add_zombie(61, 11)
        self.add_zombie(62, -5)

        # SIGCHLD was sio caught
        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        self.assertUongo(callback3.called)

        # attach a new loop
        self.loop = self.new_test_loop()

        ukijumuisha mock.patch.object(
                self.loop, "add_signal_handler") kama m_add_signal_handler:

            self.watcher.attach_loop(self.loop)

            m_add_signal_handler.assert_called_once_with(
                signal.SIGCHLD, self.watcher._sig_chld)
            callback1.assert_called_once_with(61, 11)  # race condition!
            callback2.assert_called_once_with(62, -5)  # race condition!
            self.assertUongo(callback3.called)

        callback1.reset_mock()
        callback2.reset_mock()

        # child 3 terminates
        self.running = Uongo
        self.add_zombie(622, 19)
        self.watcher._sig_chld()

        self.assertUongo(callback1.called)
        self.assertUongo(callback2.called)
        callback3.assert_called_once_with(622, 19)

    @waitpid_mocks
    eleza test_close(self, m):
        # register two children
        callback1 = mock.Mock()

        ukijumuisha self.watcher:
            self.running = Kweli
            # child 1 terminates
            self.add_zombie(63, 9)
            # other child terminates
            self.add_zombie(65, 18)
            self.watcher._sig_chld()

            self.watcher.add_child_handler(63, callback1)
            self.watcher.add_child_handler(64, callback1)

            self.assertEqual(len(self.watcher._callbacks), 1)
            ikiwa isinstance(self.watcher, asyncio.FastChildWatcher):
                self.assertEqual(len(self.watcher._zombies), 1)

            ukijumuisha mock.patch.object(
                    self.loop,
                    "remove_signal_handler") kama m_remove_signal_handler:

                self.watcher.close()

                m_remove_signal_handler.assert_called_once_with(
                    signal.SIGCHLD)
                self.assertUongo(self.watcher._callbacks)
                ikiwa isinstance(self.watcher, asyncio.FastChildWatcher):
                    self.assertUongo(self.watcher._zombies)


kundi SafeChildWatcherTests (ChildWatcherTestsMixin, test_utils.TestCase):
    eleza create_watcher(self):
        rudisha asyncio.SafeChildWatcher()


kundi FastChildWatcherTests (ChildWatcherTestsMixin, test_utils.TestCase):
    eleza create_watcher(self):
        rudisha asyncio.FastChildWatcher()


kundi PolicyTests(unittest.TestCase):

    eleza create_policy(self):
        rudisha asyncio.DefaultEventLoopPolicy()

    eleza test_get_default_child_watcher(self):
        policy = self.create_policy()
        self.assertIsTupu(policy._watcher)

        watcher = policy.get_child_watcher()
        self.assertIsInstance(watcher, asyncio.ThreadedChildWatcher)

        self.assertIs(policy._watcher, watcher)

        self.assertIs(watcher, policy.get_child_watcher())

    eleza test_get_child_watcher_after_set(self):
        policy = self.create_policy()
        watcher = asyncio.FastChildWatcher()

        policy.set_child_watcher(watcher)
        self.assertIs(policy._watcher, watcher)
        self.assertIs(watcher, policy.get_child_watcher())

    eleza test_get_child_watcher_thread(self):

        eleza f():
            policy.set_event_loop(policy.new_event_loop())

            self.assertIsInstance(policy.get_event_loop(),
                                  asyncio.AbstractEventLoop)
            watcher = policy.get_child_watcher()

            self.assertIsInstance(watcher, asyncio.SafeChildWatcher)
            self.assertIsTupu(watcher._loop)

            policy.get_event_loop().close()

        policy = self.create_policy()
        policy.set_child_watcher(asyncio.SafeChildWatcher())

        th = threading.Thread(target=f)
        th.start()
        th.join()

    eleza test_child_watcher_replace_mainloop_existing(self):
        policy = self.create_policy()
        loop = policy.get_event_loop()

        # Explicitly setup SafeChildWatcher,
        # default ThreadedChildWatcher has no _loop property
        watcher = asyncio.SafeChildWatcher()
        policy.set_child_watcher(watcher)
        watcher.attach_loop(loop)

        self.assertIs(watcher._loop, loop)

        new_loop = policy.new_event_loop()
        policy.set_event_loop(new_loop)

        self.assertIs(watcher._loop, new_loop)

        policy.set_event_loop(Tupu)

        self.assertIs(watcher._loop, Tupu)

        loop.close()
        new_loop.close()


kundi TestFunctional(unittest.TestCase):

    eleza setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    eleza tearDown(self):
        self.loop.close()
        asyncio.set_event_loop(Tupu)

    eleza test_add_reader_invalid_argument(self):
        eleza assert_raises():
            rudisha self.assertRaisesRegex(ValueError, r'Invalid file object')

        cb = lambda: Tupu

        ukijumuisha assert_raises():
            self.loop.add_reader(object(), cb)
        ukijumuisha assert_raises():
            self.loop.add_writer(object(), cb)

        ukijumuisha assert_raises():
            self.loop.remove_reader(object())
        ukijumuisha assert_raises():
            self.loop.remove_writer(object())

    eleza test_add_reader_or_writer_transport_fd(self):
        eleza assert_raises():
            rudisha self.assertRaisesRegex(
                RuntimeError,
                r'File descriptor .* ni used by transport')

        async eleza runner():
            tr, pr = await self.loop.create_connection(
                lambda: asyncio.Protocol(), sock=rsock)

            jaribu:
                cb = lambda: Tupu

                ukijumuisha assert_raises():
                    self.loop.add_reader(rsock, cb)
                ukijumuisha assert_raises():
                    self.loop.add_reader(rsock.fileno(), cb)

                ukijumuisha assert_raises():
                    self.loop.remove_reader(rsock)
                ukijumuisha assert_raises():
                    self.loop.remove_reader(rsock.fileno())

                ukijumuisha assert_raises():
                    self.loop.add_writer(rsock, cb)
                ukijumuisha assert_raises():
                    self.loop.add_writer(rsock.fileno(), cb)

                ukijumuisha assert_raises():
                    self.loop.remove_writer(rsock)
                ukijumuisha assert_raises():
                    self.loop.remove_writer(rsock.fileno())

            mwishowe:
                tr.close()

        rsock, wsock = socket.socketpair()
        jaribu:
            self.loop.run_until_complete(runner())
        mwishowe:
            rsock.close()
            wsock.close()


ikiwa __name__ == '__main__':
    unittest.main()
