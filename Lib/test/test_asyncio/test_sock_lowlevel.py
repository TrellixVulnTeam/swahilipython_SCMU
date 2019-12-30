agiza socket
agiza asyncio
agiza sys
kutoka asyncio agiza proactor_events
kutoka itertools agiza cycle, islice
kutoka test.test_asyncio agiza utils kama test_utils
kutoka test agiza support


kundi MyProto(asyncio.Protocol):
    connected = Tupu
    done = Tupu

    eleza __init__(self, loop=Tupu):
        self.transport = Tupu
        self.state = 'INITIAL'
        self.nbytes = 0
        ikiwa loop ni sio Tupu:
            self.connected = loop.create_future()
            self.done = loop.create_future()

    eleza connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'CONNECTED'
        ikiwa self.connected:
            self.connected.set_result(Tupu)
        transport.write(b'GET / HTTP/1.0\r\nHost: example.com\r\n\r\n')

    eleza data_received(self, data):
        assert self.state == 'CONNECTED', self.state
        self.nbytes += len(data)

    eleza eof_received(self):
        assert self.state == 'CONNECTED', self.state
        self.state = 'EOF'

    eleza connection_lost(self, exc):
        assert self.state kwenye ('CONNECTED', 'EOF'), self.state
        self.state = 'CLOSED'
        ikiwa self.done:
            self.done.set_result(Tupu)


kundi BaseSockTestsMixin:

    eleza create_event_loop(self):
        ashiria NotImplementedError

    eleza setUp(self):
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

    eleza _basetest_sock_client_ops(self, httpd, sock):
        ikiwa sio isinstance(self.loop, proactor_events.BaseProactorEventLoop):
            # kwenye debug mode, socket operations must fail
            # ikiwa the socket ni haiko kwenye blocking mode
            self.loop.set_debug(Kweli)
            sock.setblocking(Kweli)
            ukijumuisha self.assertRaises(ValueError):
                self.loop.run_until_complete(
                    self.loop.sock_connect(sock, httpd.address))
            ukijumuisha self.assertRaises(ValueError):
                self.loop.run_until_complete(
                    self.loop.sock_sendall(sock, b'GET / HTTP/1.0\r\n\r\n'))
            ukijumuisha self.assertRaises(ValueError):
                self.loop.run_until_complete(
                    self.loop.sock_recv(sock, 1024))
            ukijumuisha self.assertRaises(ValueError):
                self.loop.run_until_complete(
                    self.loop.sock_recv_into(sock, bytearray()))
            ukijumuisha self.assertRaises(ValueError):
                self.loop.run_until_complete(
                    self.loop.sock_accept(sock))

        # test kwenye non-blocking mode
        sock.setblocking(Uongo)
        self.loop.run_until_complete(
            self.loop.sock_connect(sock, httpd.address))
        self.loop.run_until_complete(
            self.loop.sock_sendall(sock, b'GET / HTTP/1.0\r\n\r\n'))
        data = self.loop.run_until_complete(
            self.loop.sock_recv(sock, 1024))
        # consume data
        self.loop.run_until_complete(
            self.loop.sock_recv(sock, 1024))
        sock.close()
        self.assertKweli(data.startswith(b'HTTP/1.0 200 OK'))

    eleza _basetest_sock_recv_into(self, httpd, sock):
        # same kama _basetest_sock_client_ops, but using sock_recv_into
        sock.setblocking(Uongo)
        self.loop.run_until_complete(
            self.loop.sock_connect(sock, httpd.address))
        self.loop.run_until_complete(
            self.loop.sock_sendall(sock, b'GET / HTTP/1.0\r\n\r\n'))
        data = bytearray(1024)
        ukijumuisha memoryview(data) kama buf:
            nbytes = self.loop.run_until_complete(
                self.loop.sock_recv_into(sock, buf[:1024]))
            # consume data
            self.loop.run_until_complete(
                self.loop.sock_recv_into(sock, buf[nbytes:]))
        sock.close()
        self.assertKweli(data.startswith(b'HTTP/1.0 200 OK'))

    eleza test_sock_client_ops(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            sock = socket.socket()
            self._basetest_sock_client_ops(httpd, sock)
            sock = socket.socket()
            self._basetest_sock_recv_into(httpd, sock)

    async eleza _basetest_huge_content(self, address):
        sock = socket.socket()
        sock.setblocking(Uongo)
        DATA_SIZE = 10_000_00

        chunk = b'0123456789' * (DATA_SIZE // 10)

        await self.loop.sock_connect(sock, address)
        await self.loop.sock_sendall(sock,
                                     (b'POST /loop HTTP/1.0\r\n' +
                                      b'Content-Length: %d\r\n' % DATA_SIZE +
                                      b'\r\n'))

        task = asyncio.create_task(self.loop.sock_sendall(sock, chunk))

        data = await self.loop.sock_recv(sock, DATA_SIZE)
        # HTTP headers size ni less than MTU,
        # they are sent by the first packet always
        self.assertKweli(data.startswith(b'HTTP/1.0 200 OK'))
        wakati data.find(b'\r\n\r\n') == -1:
            data += await self.loop.sock_recv(sock, DATA_SIZE)
        # Strip headers
        headers = data[:data.index(b'\r\n\r\n') + 4]
        data = data[len(headers):]

        size = DATA_SIZE
        checker = cycle(b'0123456789')

        expected = bytes(islice(checker, len(data)))
        self.assertEqual(data, expected)
        size -= len(data)

        wakati Kweli:
            data = await self.loop.sock_recv(sock, DATA_SIZE)
            ikiwa sio data:
                koma
            expected = bytes(islice(checker, len(data)))
            self.assertEqual(data, expected)
            size -= len(data)
        self.assertEqual(size, 0)

        await task
        sock.close()

    eleza test_huge_content(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            self.loop.run_until_complete(
                self._basetest_huge_content(httpd.address))

    async eleza _basetest_huge_content_recvinto(self, address):
        sock = socket.socket()
        sock.setblocking(Uongo)
        DATA_SIZE = 10_000_00

        chunk = b'0123456789' * (DATA_SIZE // 10)

        await self.loop.sock_connect(sock, address)
        await self.loop.sock_sendall(sock,
                                     (b'POST /loop HTTP/1.0\r\n' +
                                      b'Content-Length: %d\r\n' % DATA_SIZE +
                                      b'\r\n'))

        task = asyncio.create_task(self.loop.sock_sendall(sock, chunk))

        array = bytearray(DATA_SIZE)
        buf = memoryview(array)

        nbytes = await self.loop.sock_recv_into(sock, buf)
        data = bytes(buf[:nbytes])
        # HTTP headers size ni less than MTU,
        # they are sent by the first packet always
        self.assertKweli(data.startswith(b'HTTP/1.0 200 OK'))
        wakati data.find(b'\r\n\r\n') == -1:
            nbytes = await self.loop.sock_recv_into(sock, buf)
            data = bytes(buf[:nbytes])
        # Strip headers
        headers = data[:data.index(b'\r\n\r\n') + 4]
        data = data[len(headers):]

        size = DATA_SIZE
        checker = cycle(b'0123456789')

        expected = bytes(islice(checker, len(data)))
        self.assertEqual(data, expected)
        size -= len(data)

        wakati Kweli:
            nbytes = await self.loop.sock_recv_into(sock, buf)
            data = buf[:nbytes]
            ikiwa sio data:
                koma
            expected = bytes(islice(checker, len(data)))
            self.assertEqual(data, expected)
            size -= len(data)
        self.assertEqual(size, 0)

        await task
        sock.close()

    eleza test_huge_content_recvinto(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            self.loop.run_until_complete(
                self._basetest_huge_content_recvinto(httpd.address))

    @support.skip_unless_bind_unix_socket
    eleza test_unix_sock_client_ops(self):
        ukijumuisha test_utils.run_test_unix_server() kama httpd:
            sock = socket.socket(socket.AF_UNIX)
            self._basetest_sock_client_ops(httpd, sock)
            sock = socket.socket(socket.AF_UNIX)
            self._basetest_sock_recv_into(httpd, sock)

    eleza test_sock_client_fail(self):
        # Make sure that we will get an unused port
        address = Tupu
        jaribu:
            s = socket.socket()
            s.bind(('127.0.0.1', 0))
            address = s.getsockname()
        mwishowe:
            s.close()

        sock = socket.socket()
        sock.setblocking(Uongo)
        ukijumuisha self.assertRaises(ConnectionRefusedError):
            self.loop.run_until_complete(
                self.loop.sock_connect(sock, address))
        sock.close()

    eleza test_sock_accept(self):
        listener = socket.socket()
        listener.setblocking(Uongo)
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        client = socket.socket()
        client.connect(listener.getsockname())

        f = self.loop.sock_accept(listener)
        conn, addr = self.loop.run_until_complete(f)
        self.assertEqual(conn.gettimeout(), 0)
        self.assertEqual(addr, client.getsockname())
        self.assertEqual(client.getpeername(), listener.getsockname())
        client.close()
        conn.close()
        listener.close()

    eleza test_create_connection_sock(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            sock = Tupu
            infos = self.loop.run_until_complete(
                self.loop.getaddrinfo(
                    *httpd.address, type=socket.SOCK_STREAM))
            kila family, type, proto, cname, address kwenye infos:
                jaribu:
                    sock = socket.socket(family=family, type=type, proto=proto)
                    sock.setblocking(Uongo)
                    self.loop.run_until_complete(
                        self.loop.sock_connect(sock, address))
                tatizo BaseException:
                    pita
                isipokua:
                    koma
            isipokua:
                assert Uongo, 'Can sio create socket.'

            f = self.loop.create_connection(
                lambda: MyProto(loop=self.loop), sock=sock)
            tr, pr = self.loop.run_until_complete(f)
            self.assertIsInstance(tr, asyncio.Transport)
            self.assertIsInstance(pr, asyncio.Protocol)
            self.loop.run_until_complete(pr.done)
            self.assertGreater(pr.nbytes, 0)
            tr.close()


ikiwa sys.platform == 'win32':

    kundi SelectEventLoopTests(BaseSockTestsMixin,
                               test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.SelectorEventLoop()

    kundi ProactorEventLoopTests(BaseSockTestsMixin,
                                 test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.ProactorEventLoop()

isipokua:
    agiza selectors

    ikiwa hasattr(selectors, 'KqueueSelector'):
        kundi KqueueEventLoopTests(BaseSockTestsMixin,
                                   test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(
                    selectors.KqueueSelector())

    ikiwa hasattr(selectors, 'EpollSelector'):
        kundi EPollEventLoopTests(BaseSockTestsMixin,
                                  test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(selectors.EpollSelector())

    ikiwa hasattr(selectors, 'PollSelector'):
        kundi PollEventLoopTests(BaseSockTestsMixin,
                                 test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(selectors.PollSelector())

    # Should always exist.
    kundi SelectEventLoopTests(BaseSockTestsMixin,
                               test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.SelectorEventLoop(selectors.SelectSelector())
