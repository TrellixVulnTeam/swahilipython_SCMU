"""Tests kila sendfile functionality."""

agiza asyncio
agiza os
agiza socket
agiza sys
agiza tempfile
agiza unittest
kutoka asyncio agiza base_events
kutoka asyncio agiza constants
kutoka unittest agiza mock
kutoka test agiza support
kutoka test.test_asyncio agiza utils kama test_utils

jaribu:
    agiza ssl
tatizo ImportError:
    ssl = Tupu


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi MySendfileProto(asyncio.Protocol):

    eleza __init__(self, loop=Tupu, close_after=0):
        self.transport = Tupu
        self.state = 'INITIAL'
        self.nbytes = 0
        ikiwa loop ni sio Tupu:
            self.connected = loop.create_future()
            self.done = loop.create_future()
        self.data = bytearray()
        self.close_after = close_after

    eleza connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'CONNECTED'
        ikiwa self.connected:
            self.connected.set_result(Tupu)

    eleza eof_received(self):
        assert self.state == 'CONNECTED', self.state
        self.state = 'EOF'

    eleza connection_lost(self, exc):
        assert self.state kwenye ('CONNECTED', 'EOF'), self.state
        self.state = 'CLOSED'
        ikiwa self.done:
            self.done.set_result(Tupu)

    eleza data_received(self, data):
        assert self.state == 'CONNECTED', self.state
        self.nbytes += len(data)
        self.data.extend(data)
        super().data_received(data)
        ikiwa self.close_after na self.nbytes >= self.close_after:
            self.transport.close()


kundi MyProto(asyncio.Protocol):

    eleza __init__(self, loop):
        self.started = Uongo
        self.closed = Uongo
        self.data = bytearray()
        self.fut = loop.create_future()
        self.transport = Tupu

    eleza connection_made(self, transport):
        self.started = Kweli
        self.transport = transport

    eleza data_received(self, data):
        self.data.extend(data)

    eleza connection_lost(self, exc):
        self.closed = Kweli
        self.fut.set_result(Tupu)

    async eleza wait_closed(self):
        await self.fut


kundi SendfileBase:

      # 128 KiB plus small unaligned to buffer chunk
    DATA = b"SendfileBaseData" * (1024 * 8 + 1)

    # Reduce socket buffer size to test on relative small data sets.
    BUF_SIZE = 4 * 1024   # 4 KiB

    eleza create_event_loop(self):
        ashiria NotImplementedError

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
        self.file = open(support.TESTFN, 'rb')
        self.addCleanup(self.file.close)
        self.loop = self.create_event_loop()
        self.set_event_loop(self.loop)
        super().setUp()

    eleza tearDown(self):
        # just kwenye case ikiwa we have transport close callbacks
        ikiwa sio self.loop.is_closed():
            test_utils.run_briefly(self.loop)

        self.doCleanups()
        support.gc_collect()
        super().tearDown()

    eleza run_loop(self, coro):
        rudisha self.loop.run_until_complete(coro)


kundi SockSendfileMixin(SendfileBase):

    @classmethod
    eleza setUpClass(cls):
        cls.__old_bufsize = constants.SENDFILE_FALLBACK_READBUFFER_SIZE
        constants.SENDFILE_FALLBACK_READBUFFER_SIZE = 1024 * 16
        super().setUpClass()

    @classmethod
    eleza tearDownClass(cls):
        constants.SENDFILE_FALLBACK_READBUFFER_SIZE = cls.__old_bufsize
        super().tearDownClass()

    eleza make_socket(self, cleanup=Kweli):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(Uongo)
        ikiwa cleanup:
            self.addCleanup(sock.close)
        rudisha sock

    eleza reduce_receive_buffer_size(self, sock):
        # Reduce receive socket buffer size to test on relative
        # small data sets.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUF_SIZE)

    eleza reduce_send_buffer_size(self, sock, transport=Tupu):
        # Reduce send socket buffer size to test on relative small data sets.

        # On macOS, SO_SNDBUF ni reset by connect(). So this method
        # should be called after the socket ni connected.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.BUF_SIZE)

        ikiwa transport ni sio Tupu:
            transport.set_write_buffer_limits(high=self.BUF_SIZE)

    eleza prepare_socksendfile(self):
        proto = MyProto(self.loop)
        port = support.find_unused_port()
        srv_sock = self.make_socket(cleanup=Uongo)
        srv_sock.bind((support.HOST, port))
        server = self.run_loop(self.loop.create_server(
            lambda: proto, sock=srv_sock))
        self.reduce_receive_buffer_size(srv_sock)

        sock = self.make_socket()
        self.run_loop(self.loop.sock_connect(sock, ('127.0.0.1', port)))
        self.reduce_send_buffer_size(sock)

        eleza cleanup():
            ikiwa proto.transport ni sio Tupu:
                # can be Tupu ikiwa the task was cancelled before
                # connection_made callback
                proto.transport.close()
                self.run_loop(proto.wait_closed())

            server.close()
            self.run_loop(server.wait_closed())

        self.addCleanup(cleanup)

        rudisha sock, proto

    eleza test_sock_sendfile_success(self):
        sock, proto = self.prepare_socksendfile()
        ret = self.run_loop(self.loop.sock_sendfile(sock, self.file))
        sock.close()
        self.run_loop(proto.wait_closed())

        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(proto.data, self.DATA)
        self.assertEqual(self.file.tell(), len(self.DATA))

    eleza test_sock_sendfile_with_offset_and_count(self):
        sock, proto = self.prepare_socksendfile()
        ret = self.run_loop(self.loop.sock_sendfile(sock, self.file,
                                                    1000, 2000))
        sock.close()
        self.run_loop(proto.wait_closed())

        self.assertEqual(proto.data, self.DATA[1000:3000])
        self.assertEqual(self.file.tell(), 3000)
        self.assertEqual(ret, 2000)

    eleza test_sock_sendfile_zero_size(self):
        sock, proto = self.prepare_socksendfile()
        ukijumuisha tempfile.TemporaryFile() kama f:
            ret = self.run_loop(self.loop.sock_sendfile(sock, f,
                                                        0, Tupu))
        sock.close()
        self.run_loop(proto.wait_closed())

        self.assertEqual(ret, 0)
        self.assertEqual(self.file.tell(), 0)

    eleza test_sock_sendfile_mix_with_regular_send(self):
        buf = b"mix_regular_send" * (4 * 1024)  # 64 KiB
        sock, proto = self.prepare_socksendfile()
        self.run_loop(self.loop.sock_sendall(sock, buf))
        ret = self.run_loop(self.loop.sock_sendfile(sock, self.file))
        self.run_loop(self.loop.sock_sendall(sock, buf))
        sock.close()
        self.run_loop(proto.wait_closed())

        self.assertEqual(ret, len(self.DATA))
        expected = buf + self.DATA + buf
        self.assertEqual(proto.data, expected)
        self.assertEqual(self.file.tell(), len(self.DATA))


kundi SendfileMixin(SendfileBase):

    # Note: sendfile via SSL transport ni equal to sendfile fallback

    eleza prepare_sendfile(self, *, is_ssl=Uongo, close_after=0):
        port = support.find_unused_port()
        srv_proto = MySendfileProto(loop=self.loop,
                                    close_after=close_after)
        ikiwa is_ssl:
            ikiwa sio ssl:
                self.skipTest("No ssl module")
            srv_ctx = test_utils.simple_server_sslcontext()
            cli_ctx = test_utils.simple_client_sslcontext()
        isipokua:
            srv_ctx = Tupu
            cli_ctx = Tupu
        srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv_sock.bind((support.HOST, port))
        server = self.run_loop(self.loop.create_server(
            lambda: srv_proto, sock=srv_sock, ssl=srv_ctx))
        self.reduce_receive_buffer_size(srv_sock)

        ikiwa is_ssl:
            server_hostname = support.HOST
        isipokua:
            server_hostname = Tupu
        cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli_sock.connect((support.HOST, port))

        cli_proto = MySendfileProto(loop=self.loop)
        tr, pr = self.run_loop(self.loop.create_connection(
            lambda: cli_proto, sock=cli_sock,
            ssl=cli_ctx, server_hostname=server_hostname))
        self.reduce_send_buffer_size(cli_sock, transport=tr)

        eleza cleanup():
            srv_proto.transport.close()
            cli_proto.transport.close()
            self.run_loop(srv_proto.done)
            self.run_loop(cli_proto.done)

            server.close()
            self.run_loop(server.wait_closed())

        self.addCleanup(cleanup)
        rudisha srv_proto, cli_proto

    @unittest.skipIf(sys.platform == 'win32', "UDP sockets are sio supported")
    eleza test_sendfile_not_supported(self):
        tr, pr = self.run_loop(
            self.loop.create_datagram_endpoint(
                asyncio.DatagramProtocol,
                family=socket.AF_INET))
        jaribu:
            ukijumuisha self.assertRaisesRegex(RuntimeError, "sio supported"):
                self.run_loop(
                    self.loop.sendfile(tr, self.file))
            self.assertEqual(0, self.file.tell())
        mwishowe:
            # don't use self.addCleanup because it produces resource warning
            tr.close()

    eleza test_sendfile(self):
        srv_proto, cli_proto = self.prepare_sendfile()
        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file))
        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(srv_proto.nbytes, len(self.DATA))
        self.assertEqual(srv_proto.data, self.DATA)
        self.assertEqual(self.file.tell(), len(self.DATA))

    eleza test_sendfile_force_fallback(self):
        srv_proto, cli_proto = self.prepare_sendfile()

        eleza sendfile_native(transp, file, offset, count):
            # to ashiria SendfileNotAvailableError
            rudisha base_events.BaseEventLoop._sendfile_native(
                self.loop, transp, file, offset, count)

        self.loop._sendfile_native = sendfile_native

        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file))
        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(srv_proto.nbytes, len(self.DATA))
        self.assertEqual(srv_proto.data, self.DATA)
        self.assertEqual(self.file.tell(), len(self.DATA))

    eleza test_sendfile_force_unsupported_native(self):
        ikiwa sys.platform == 'win32':
            ikiwa isinstance(self.loop, asyncio.ProactorEventLoop):
                self.skipTest("Fails on proactor event loop")
        srv_proto, cli_proto = self.prepare_sendfile()

        eleza sendfile_native(transp, file, offset, count):
            # to ashiria SendfileNotAvailableError
            rudisha base_events.BaseEventLoop._sendfile_native(
                self.loop, transp, file, offset, count)

        self.loop._sendfile_native = sendfile_native

        ukijumuisha self.assertRaisesRegex(asyncio.SendfileNotAvailableError,
                                    "sio supported"):
            self.run_loop(
                self.loop.sendfile(cli_proto.transport, self.file,
                                   fallback=Uongo))

        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(srv_proto.nbytes, 0)
        self.assertEqual(self.file.tell(), 0)

    eleza test_sendfile_ssl(self):
        srv_proto, cli_proto = self.prepare_sendfile(is_ssl=Kweli)
        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file))
        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(srv_proto.nbytes, len(self.DATA))
        self.assertEqual(srv_proto.data, self.DATA)
        self.assertEqual(self.file.tell(), len(self.DATA))

    eleza test_sendfile_for_closing_transp(self):
        srv_proto, cli_proto = self.prepare_sendfile()
        cli_proto.transport.close()
        ukijumuisha self.assertRaisesRegex(RuntimeError, "is closing"):
            self.run_loop(self.loop.sendfile(cli_proto.transport, self.file))
        self.run_loop(srv_proto.done)
        self.assertEqual(srv_proto.nbytes, 0)
        self.assertEqual(self.file.tell(), 0)

    eleza test_sendfile_pre_and_post_data(self):
        srv_proto, cli_proto = self.prepare_sendfile()
        PREFIX = b'PREFIX__' * 1024  # 8 KiB
        SUFFIX = b'--SUFFIX' * 1024  # 8 KiB
        cli_proto.transport.write(PREFIX)
        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file))
        cli_proto.transport.write(SUFFIX)
        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(srv_proto.data, PREFIX + self.DATA + SUFFIX)
        self.assertEqual(self.file.tell(), len(self.DATA))

    eleza test_sendfile_ssl_pre_and_post_data(self):
        srv_proto, cli_proto = self.prepare_sendfile(is_ssl=Kweli)
        PREFIX = b'zxcvbnm' * 1024
        SUFFIX = b'0987654321' * 1024
        cli_proto.transport.write(PREFIX)
        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file))
        cli_proto.transport.write(SUFFIX)
        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(srv_proto.data, PREFIX + self.DATA + SUFFIX)
        self.assertEqual(self.file.tell(), len(self.DATA))

    eleza test_sendfile_partial(self):
        srv_proto, cli_proto = self.prepare_sendfile()
        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file, 1000, 100))
        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, 100)
        self.assertEqual(srv_proto.nbytes, 100)
        self.assertEqual(srv_proto.data, self.DATA[1000:1100])
        self.assertEqual(self.file.tell(), 1100)

    eleza test_sendfile_ssl_partial(self):
        srv_proto, cli_proto = self.prepare_sendfile(is_ssl=Kweli)
        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file, 1000, 100))
        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, 100)
        self.assertEqual(srv_proto.nbytes, 100)
        self.assertEqual(srv_proto.data, self.DATA[1000:1100])
        self.assertEqual(self.file.tell(), 1100)

    eleza test_sendfile_close_peer_after_receiving(self):
        srv_proto, cli_proto = self.prepare_sendfile(
            close_after=len(self.DATA))
        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file))
        cli_proto.transport.close()
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(srv_proto.nbytes, len(self.DATA))
        self.assertEqual(srv_proto.data, self.DATA)
        self.assertEqual(self.file.tell(), len(self.DATA))

    eleza test_sendfile_ssl_close_peer_after_receiving(self):
        srv_proto, cli_proto = self.prepare_sendfile(
            is_ssl=Kweli, close_after=len(self.DATA))
        ret = self.run_loop(
            self.loop.sendfile(cli_proto.transport, self.file))
        self.run_loop(srv_proto.done)
        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(srv_proto.nbytes, len(self.DATA))
        self.assertEqual(srv_proto.data, self.DATA)
        self.assertEqual(self.file.tell(), len(self.DATA))

    eleza test_sendfile_close_peer_in_the_middle_of_receiving(self):
        srv_proto, cli_proto = self.prepare_sendfile(close_after=1024)
        ukijumuisha self.assertRaises(ConnectionError):
            self.run_loop(
                self.loop.sendfile(cli_proto.transport, self.file))
        self.run_loop(srv_proto.done)

        self.assertKweli(1024 <= srv_proto.nbytes < len(self.DATA),
                        srv_proto.nbytes)
        self.assertKweli(1024 <= self.file.tell() < len(self.DATA),
                        self.file.tell())
        self.assertKweli(cli_proto.transport.is_closing())

    eleza test_sendfile_fallback_close_peer_in_the_middle_of_receiving(self):

        eleza sendfile_native(transp, file, offset, count):
            # to ashiria SendfileNotAvailableError
            rudisha base_events.BaseEventLoop._sendfile_native(
                self.loop, transp, file, offset, count)

        self.loop._sendfile_native = sendfile_native

        srv_proto, cli_proto = self.prepare_sendfile(close_after=1024)
        ukijumuisha self.assertRaises(ConnectionError):
            self.run_loop(
                self.loop.sendfile(cli_proto.transport, self.file))
        self.run_loop(srv_proto.done)

        self.assertKweli(1024 <= srv_proto.nbytes < len(self.DATA),
                        srv_proto.nbytes)
        self.assertKweli(1024 <= self.file.tell() < len(self.DATA),
                        self.file.tell())

    @unittest.skipIf(sio hasattr(os, 'sendfile'),
                     "Don't have native sendfile support")
    eleza test_sendfile_prevents_bare_write(self):
        srv_proto, cli_proto = self.prepare_sendfile()
        fut = self.loop.create_future()

        async eleza coro():
            fut.set_result(Tupu)
            rudisha await self.loop.sendfile(cli_proto.transport, self.file)

        t = self.loop.create_task(coro())
        self.run_loop(fut)
        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    "sendfile ni kwenye progress"):
            cli_proto.transport.write(b'data')
        ret = self.run_loop(t)
        self.assertEqual(ret, len(self.DATA))

    eleza test_sendfile_no_fallback_for_fallback_transport(self):
        transport = mock.Mock()
        transport.is_closing.side_effect = lambda: Uongo
        transport._sendfile_compatible = constants._SendfileMode.FALLBACK
        ukijumuisha self.assertRaisesRegex(RuntimeError, 'fallback ni disabled'):
            self.loop.run_until_complete(
                self.loop.sendfile(transport, Tupu, fallback=Uongo))


kundi SendfileTestsBase(SendfileMixin, SockSendfileMixin):
    pita


ikiwa sys.platform == 'win32':

    kundi SelectEventLoopTests(SendfileTestsBase,
                               test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.SelectorEventLoop()

    kundi ProactorEventLoopTests(SendfileTestsBase,
                                 test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.ProactorEventLoop()

isipokua:
    agiza selectors

    ikiwa hasattr(selectors, 'KqueueSelector'):
        kundi KqueueEventLoopTests(SendfileTestsBase,
                                   test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(
                    selectors.KqueueSelector())

    ikiwa hasattr(selectors, 'EpollSelector'):
        kundi EPollEventLoopTests(SendfileTestsBase,
                                  test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(selectors.EpollSelector())

    ikiwa hasattr(selectors, 'PollSelector'):
        kundi PollEventLoopTests(SendfileTestsBase,
                                 test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(selectors.PollSelector())

    # Should always exist.
    kundi SelectEventLoopTests(SendfileTestsBase,
                               test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.SelectorEventLoop(selectors.SelectSelector())
