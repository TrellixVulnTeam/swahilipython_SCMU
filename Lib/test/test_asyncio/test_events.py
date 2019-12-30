"""Tests kila events.py."""

agiza collections.abc
agiza concurrent.futures
agiza functools
agiza io
agiza os
agiza platform
agiza re
agiza signal
agiza socket
jaribu:
    agiza ssl
tatizo ImportError:
    ssl = Tupu
agiza subprocess
agiza sys
agiza threading
agiza time
agiza errno
agiza unittest
kutoka unittest agiza mock
agiza weakref

ikiwa sys.platform != 'win32':
    agiza tty

agiza asyncio
kutoka asyncio agiza coroutines
kutoka asyncio agiza events
kutoka asyncio agiza proactor_events
kutoka asyncio agiza selector_events
kutoka test.test_asyncio agiza utils kama test_utils
kutoka test agiza support


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


eleza broken_unix_getsockname():
    """Return Kweli ikiwa the platform ni Mac OS 10.4 ama older."""
    ikiwa sys.platform.startswith("aix"):
        rudisha Kweli
    lasivyo sys.platform != 'darwin':
        rudisha Uongo
    version = platform.mac_ver()[0]
    version = tuple(map(int, version.split('.')))
    rudisha version < (10, 5)


eleza _test_get_event_loop_new_process__sub_proc():
    async eleza doit():
        rudisha 'hello'

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    rudisha loop.run_until_complete(doit())


kundi CoroLike:
    eleza send(self, v):
        pita

    eleza throw(self, *exc):
        pita

    eleza close(self):
        pita

    eleza __await__(self):
        pita


kundi MyBaseProto(asyncio.Protocol):
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


kundi MyProto(MyBaseProto):
    eleza connection_made(self, transport):
        super().connection_made(transport)
        transport.write(b'GET / HTTP/1.0\r\nHost: example.com\r\n\r\n')


kundi MyDatagramProto(asyncio.DatagramProtocol):
    done = Tupu

    eleza __init__(self, loop=Tupu):
        self.state = 'INITIAL'
        self.nbytes = 0
        ikiwa loop ni sio Tupu:
            self.done = loop.create_future()

    eleza connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'INITIALIZED'

    eleza datagram_received(self, data, addr):
        assert self.state == 'INITIALIZED', self.state
        self.nbytes += len(data)

    eleza error_received(self, exc):
        assert self.state == 'INITIALIZED', self.state

    eleza connection_lost(self, exc):
        assert self.state == 'INITIALIZED', self.state
        self.state = 'CLOSED'
        ikiwa self.done:
            self.done.set_result(Tupu)


kundi MyReadPipeProto(asyncio.Protocol):
    done = Tupu

    eleza __init__(self, loop=Tupu):
        self.state = ['INITIAL']
        self.nbytes = 0
        self.transport = Tupu
        ikiwa loop ni sio Tupu:
            self.done = loop.create_future()

    eleza connection_made(self, transport):
        self.transport = transport
        assert self.state == ['INITIAL'], self.state
        self.state.append('CONNECTED')

    eleza data_received(self, data):
        assert self.state == ['INITIAL', 'CONNECTED'], self.state
        self.nbytes += len(data)

    eleza eof_received(self):
        assert self.state == ['INITIAL', 'CONNECTED'], self.state
        self.state.append('EOF')

    eleza connection_lost(self, exc):
        ikiwa 'EOF' haiko kwenye self.state:
            self.state.append('EOF')  # It ni okay ikiwa EOF ni missed.
        assert self.state == ['INITIAL', 'CONNECTED', 'EOF'], self.state
        self.state.append('CLOSED')
        ikiwa self.done:
            self.done.set_result(Tupu)


kundi MyWritePipeProto(asyncio.BaseProtocol):
    done = Tupu

    eleza __init__(self, loop=Tupu):
        self.state = 'INITIAL'
        self.transport = Tupu
        ikiwa loop ni sio Tupu:
            self.done = loop.create_future()

    eleza connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'CONNECTED'

    eleza connection_lost(self, exc):
        assert self.state == 'CONNECTED', self.state
        self.state = 'CLOSED'
        ikiwa self.done:
            self.done.set_result(Tupu)


kundi MySubprocessProtocol(asyncio.SubprocessProtocol):

    eleza __init__(self, loop):
        self.state = 'INITIAL'
        self.transport = Tupu
        self.connected = loop.create_future()
        self.completed = loop.create_future()
        self.disconnects = {fd: loop.create_future() kila fd kwenye range(3)}
        self.data = {1: b'', 2: b''}
        self.returncode = Tupu
        self.got_data = {1: asyncio.Event(loop=loop),
                         2: asyncio.Event(loop=loop)}

    eleza connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'CONNECTED'
        self.connected.set_result(Tupu)

    eleza connection_lost(self, exc):
        assert self.state == 'CONNECTED', self.state
        self.state = 'CLOSED'
        self.completed.set_result(Tupu)

    eleza pipe_data_received(self, fd, data):
        assert self.state == 'CONNECTED', self.state
        self.data[fd] += data
        self.got_data[fd].set()

    eleza pipe_connection_lost(self, fd, exc):
        assert self.state == 'CONNECTED', self.state
        ikiwa exc:
            self.disconnects[fd].set_exception(exc)
        isipokua:
            self.disconnects[fd].set_result(exc)

    eleza process_exited(self):
        assert self.state == 'CONNECTED', self.state
        self.returncode = self.transport.get_returncode()


kundi EventLoopTestsMixin:

    eleza setUp(self):
        super().setUp()
        self.loop = self.create_event_loop()
        self.set_event_loop(self.loop)

    eleza tearDown(self):
        # just kwenye case ikiwa we have transport close callbacks
        ikiwa sio self.loop.is_closed():
            test_utils.run_briefly(self.loop)

        self.doCleanups()
        support.gc_collect()
        super().tearDown()

    eleza test_run_until_complete_nesting(self):
        async eleza coro1():
            await asyncio.sleep(0)

        async eleza coro2():
            self.assertKweli(self.loop.is_running())
            self.loop.run_until_complete(coro1())

        self.assertRaises(
            RuntimeError, self.loop.run_until_complete, coro2())

    # Note: because of the default Windows timing granularity of
    # 15.6 msec, we use fairly long sleep times here (~100 msec).

    eleza test_run_until_complete(self):
        t0 = self.loop.time()
        self.loop.run_until_complete(asyncio.sleep(0.1))
        t1 = self.loop.time()
        self.assertKweli(0.08 <= t1-t0 <= 0.8, t1-t0)

    eleza test_run_until_complete_stopped(self):

        async eleza cb():
            self.loop.stop()
            await asyncio.sleep(0.1)
        task = cb()
        self.assertRaises(RuntimeError,
                          self.loop.run_until_complete, task)

    eleza test_call_later(self):
        results = []

        eleza callback(arg):
            results.append(arg)
            self.loop.stop()

        self.loop.call_later(0.1, callback, 'hello world')
        t0 = time.monotonic()
        self.loop.run_forever()
        t1 = time.monotonic()
        self.assertEqual(results, ['hello world'])
        self.assertKweli(0.08 <= t1-t0 <= 0.8, t1-t0)

    eleza test_call_soon(self):
        results = []

        eleza callback(arg1, arg2):
            results.append((arg1, arg2))
            self.loop.stop()

        self.loop.call_soon(callback, 'hello', 'world')
        self.loop.run_forever()
        self.assertEqual(results, [('hello', 'world')])

    eleza test_call_soon_threadsafe(self):
        results = []
        lock = threading.Lock()

        eleza callback(arg):
            results.append(arg)
            ikiwa len(results) >= 2:
                self.loop.stop()

        eleza run_in_thread():
            self.loop.call_soon_threadsafe(callback, 'hello')
            lock.release()

        lock.acquire()
        t = threading.Thread(target=run_in_thread)
        t.start()

        ukijumuisha lock:
            self.loop.call_soon(callback, 'world')
            self.loop.run_forever()
        t.join()
        self.assertEqual(results, ['hello', 'world'])

    eleza test_call_soon_threadsafe_same_thread(self):
        results = []

        eleza callback(arg):
            results.append(arg)
            ikiwa len(results) >= 2:
                self.loop.stop()

        self.loop.call_soon_threadsafe(callback, 'hello')
        self.loop.call_soon(callback, 'world')
        self.loop.run_forever()
        self.assertEqual(results, ['hello', 'world'])

    eleza test_run_in_executor(self):
        eleza run(arg):
            rudisha (arg, threading.get_ident())
        f2 = self.loop.run_in_executor(Tupu, run, 'yo')
        res, thread_id = self.loop.run_until_complete(f2)
        self.assertEqual(res, 'yo')
        self.assertNotEqual(thread_id, threading.get_ident())

    eleza test_run_in_executor_cancel(self):
        called = Uongo

        eleza patched_call_soon(*args):
            nonlocal called
            called = Kweli

        eleza run():
            time.sleep(0.05)

        f2 = self.loop.run_in_executor(Tupu, run)
        f2.cancel()
        self.loop.close()
        self.loop.call_soon = patched_call_soon
        self.loop.call_soon_threadsafe = patched_call_soon
        time.sleep(0.4)
        self.assertUongo(called)

    eleza test_reader_callback(self):
        r, w = socket.socketpair()
        r.setblocking(Uongo)
        bytes_read = bytearray()

        eleza reader():
            jaribu:
                data = r.recv(1024)
            tatizo BlockingIOError:
                # Spurious readiness notifications are possible
                # at least on Linux -- see man select.
                rudisha
            ikiwa data:
                bytes_read.extend(data)
            isipokua:
                self.assertKweli(self.loop.remove_reader(r.fileno()))
                r.close()

        self.loop.add_reader(r.fileno(), reader)
        self.loop.call_soon(w.send, b'abc')
        test_utils.run_until(self.loop, lambda: len(bytes_read) >= 3)
        self.loop.call_soon(w.send, b'def')
        test_utils.run_until(self.loop, lambda: len(bytes_read) >= 6)
        self.loop.call_soon(w.close)
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self.assertEqual(bytes_read, b'abcdef')

    eleza test_writer_callback(self):
        r, w = socket.socketpair()
        w.setblocking(Uongo)

        eleza writer(data):
            w.send(data)
            self.loop.stop()

        data = b'x' * 1024
        self.loop.add_writer(w.fileno(), writer, data)
        self.loop.run_forever()

        self.assertKweli(self.loop.remove_writer(w.fileno()))
        self.assertUongo(self.loop.remove_writer(w.fileno()))

        w.close()
        read = r.recv(len(data) * 2)
        r.close()
        self.assertEqual(read, data)

    @unittest.skipUnless(hasattr(signal, 'SIGKILL'), 'No SIGKILL')
    eleza test_add_signal_handler(self):
        caught = 0

        eleza my_handler():
            nonlocal caught
            caught += 1

        # Check error behavior first.
        self.assertRaises(
            TypeError, self.loop.add_signal_handler, 'boom', my_handler)
        self.assertRaises(
            TypeError, self.loop.remove_signal_handler, 'boom')
        self.assertRaises(
            ValueError, self.loop.add_signal_handler, signal.NSIG+1,
            my_handler)
        self.assertRaises(
            ValueError, self.loop.remove_signal_handler, signal.NSIG+1)
        self.assertRaises(
            ValueError, self.loop.add_signal_handler, 0, my_handler)
        self.assertRaises(
            ValueError, self.loop.remove_signal_handler, 0)
        self.assertRaises(
            ValueError, self.loop.add_signal_handler, -1, my_handler)
        self.assertRaises(
            ValueError, self.loop.remove_signal_handler, -1)
        self.assertRaises(
            RuntimeError, self.loop.add_signal_handler, signal.SIGKILL,
            my_handler)
        # Removing SIGKILL doesn't raise, since we don't call signal().
        self.assertUongo(self.loop.remove_signal_handler(signal.SIGKILL))
        # Now set a handler na handle it.
        self.loop.add_signal_handler(signal.SIGINT, my_handler)

        os.kill(os.getpid(), signal.SIGINT)
        test_utils.run_until(self.loop, lambda: caught)

        # Removing it should restore the default handler.
        self.assertKweli(self.loop.remove_signal_handler(signal.SIGINT))
        self.assertEqual(signal.getsignal(signal.SIGINT),
                         signal.default_int_handler)
        # Removing again returns Uongo.
        self.assertUongo(self.loop.remove_signal_handler(signal.SIGINT))

    @unittest.skipUnless(hasattr(signal, 'SIGALRM'), 'No SIGALRM')
    eleza test_signal_handling_while_selecting(self):
        # Test ukijumuisha a signal actually arriving during a select() call.
        caught = 0

        eleza my_handler():
            nonlocal caught
            caught += 1
            self.loop.stop()

        self.loop.add_signal_handler(signal.SIGALRM, my_handler)

        signal.setitimer(signal.ITIMER_REAL, 0.01, 0)  # Send SIGALRM once.
        self.loop.call_later(60, self.loop.stop)
        self.loop.run_forever()
        self.assertEqual(caught, 1)

    @unittest.skipUnless(hasattr(signal, 'SIGALRM'), 'No SIGALRM')
    eleza test_signal_handling_args(self):
        some_args = (42,)
        caught = 0

        eleza my_handler(*args):
            nonlocal caught
            caught += 1
            self.assertEqual(args, some_args)
            self.loop.stop()

        self.loop.add_signal_handler(signal.SIGALRM, my_handler, *some_args)

        signal.setitimer(signal.ITIMER_REAL, 0.1, 0)  # Send SIGALRM once.
        self.loop.call_later(60, self.loop.stop)
        self.loop.run_forever()
        self.assertEqual(caught, 1)

    eleza _basetest_create_connection(self, connection_fut, check_sockname=Kweli):
        tr, pr = self.loop.run_until_complete(connection_fut)
        self.assertIsInstance(tr, asyncio.Transport)
        self.assertIsInstance(pr, asyncio.Protocol)
        self.assertIs(pr.transport, tr)
        ikiwa check_sockname:
            self.assertIsNotTupu(tr.get_extra_info('sockname'))
        self.loop.run_until_complete(pr.done)
        self.assertGreater(pr.nbytes, 0)
        tr.close()

    eleza test_create_connection(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            conn_fut = self.loop.create_connection(
                lambda: MyProto(loop=self.loop), *httpd.address)
            self._basetest_create_connection(conn_fut)

    @support.skip_unless_bind_unix_socket
    eleza test_create_unix_connection(self):
        # Issue #20682: On Mac OS X Tiger, getsockname() returns a
        # zero-length address kila UNIX socket.
        check_sockname = sio broken_unix_getsockname()

        ukijumuisha test_utils.run_test_unix_server() kama httpd:
            conn_fut = self.loop.create_unix_connection(
                lambda: MyProto(loop=self.loop), httpd.address)
            self._basetest_create_connection(conn_fut, check_sockname)

    eleza check_ssl_extra_info(self, client, check_sockname=Kweli,
                             peername=Tupu, peercert={}):
        ikiwa check_sockname:
            self.assertIsNotTupu(client.get_extra_info('sockname'))
        ikiwa peername:
            self.assertEqual(peername,
                             client.get_extra_info('peername'))
        isipokua:
            self.assertIsNotTupu(client.get_extra_info('peername'))
        self.assertEqual(peercert,
                         client.get_extra_info('peercert'))

        # test SSL cipher
        cipher = client.get_extra_info('cipher')
        self.assertIsInstance(cipher, tuple)
        self.assertEqual(len(cipher), 3, cipher)
        self.assertIsInstance(cipher[0], str)
        self.assertIsInstance(cipher[1], str)
        self.assertIsInstance(cipher[2], int)

        # test SSL object
        sslobj = client.get_extra_info('ssl_object')
        self.assertIsNotTupu(sslobj)
        self.assertEqual(sslobj.compression(),
                         client.get_extra_info('compression'))
        self.assertEqual(sslobj.cipher(),
                         client.get_extra_info('cipher'))
        self.assertEqual(sslobj.getpeercert(),
                         client.get_extra_info('peercert'))
        self.assertEqual(sslobj.compression(),
                         client.get_extra_info('compression'))

    eleza _basetest_create_ssl_connection(self, connection_fut,
                                        check_sockname=Kweli,
                                        peername=Tupu):
        tr, pr = self.loop.run_until_complete(connection_fut)
        self.assertIsInstance(tr, asyncio.Transport)
        self.assertIsInstance(pr, asyncio.Protocol)
        self.assertKweli('ssl' kwenye tr.__class__.__name__.lower())
        self.check_ssl_extra_info(tr, check_sockname, peername)
        self.loop.run_until_complete(pr.done)
        self.assertGreater(pr.nbytes, 0)
        tr.close()

    eleza _test_create_ssl_connection(self, httpd, create_connection,
                                    check_sockname=Kweli, peername=Tupu):
        conn_fut = create_connection(ssl=test_utils.dummy_ssl_context())
        self._basetest_create_ssl_connection(conn_fut, check_sockname,
                                             peername)

        # ssl.Purpose was introduced kwenye Python 3.4
        ikiwa hasattr(ssl, 'Purpose'):
            eleza _dummy_ssl_create_context(purpose=ssl.Purpose.SERVER_AUTH, *,
                                          cafile=Tupu, capath=Tupu,
                                          cadata=Tupu):
                """
                A ssl.create_default_context() replacement that doesn't enable
                cert validation.
                """
                self.assertEqual(purpose, ssl.Purpose.SERVER_AUTH)
                rudisha test_utils.dummy_ssl_context()

            # With ssl=Kweli, ssl.create_default_context() should be called
            ukijumuisha mock.patch('ssl.create_default_context',
                            side_effect=_dummy_ssl_create_context) kama m:
                conn_fut = create_connection(ssl=Kweli)
                self._basetest_create_ssl_connection(conn_fut, check_sockname,
                                                     peername)
                self.assertEqual(m.call_count, 1)

        # With the real ssl.create_default_context(), certificate
        # validation will fail
        ukijumuisha self.assertRaises(ssl.SSLError) kama cm:
            conn_fut = create_connection(ssl=Kweli)
            # Ignore the "SSL handshake failed" log kwenye debug mode
            ukijumuisha test_utils.disable_logger():
                self._basetest_create_ssl_connection(conn_fut, check_sockname,
                                                     peername)

        self.assertEqual(cm.exception.reason, 'CERTIFICATE_VERIFY_FAILED')

    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_ssl_connection(self):
        ukijumuisha test_utils.run_test_server(use_ssl=Kweli) kama httpd:
            create_connection = functools.partial(
                self.loop.create_connection,
                lambda: MyProto(loop=self.loop),
                *httpd.address)
            self._test_create_ssl_connection(httpd, create_connection,
                                             peername=httpd.address)

    @support.skip_unless_bind_unix_socket
    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_ssl_unix_connection(self):
        # Issue #20682: On Mac OS X Tiger, getsockname() returns a
        # zero-length address kila UNIX socket.
        check_sockname = sio broken_unix_getsockname()

        ukijumuisha test_utils.run_test_unix_server(use_ssl=Kweli) kama httpd:
            create_connection = functools.partial(
                self.loop.create_unix_connection,
                lambda: MyProto(loop=self.loop), httpd.address,
                server_hostname='127.0.0.1')

            self._test_create_ssl_connection(httpd, create_connection,
                                             check_sockname,
                                             peername=httpd.address)

    eleza test_create_connection_local_addr(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            port = support.find_unused_port()
            f = self.loop.create_connection(
                lambda: MyProto(loop=self.loop),
                *httpd.address, local_addr=(httpd.address[0], port))
            tr, pr = self.loop.run_until_complete(f)
            expected = pr.transport.get_extra_info('sockname')[1]
            self.assertEqual(port, expected)
            tr.close()

    eleza test_create_connection_local_addr_in_use(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            f = self.loop.create_connection(
                lambda: MyProto(loop=self.loop),
                *httpd.address, local_addr=httpd.address)
            ukijumuisha self.assertRaises(OSError) kama cm:
                self.loop.run_until_complete(f)
            self.assertEqual(cm.exception.errno, errno.EADDRINUSE)
            self.assertIn(str(httpd.address), cm.exception.strerror)

    eleza test_connect_accepted_socket(self, server_ssl=Tupu, client_ssl=Tupu):
        loop = self.loop

        kundi MyProto(MyBaseProto):

            eleza connection_lost(self, exc):
                super().connection_lost(exc)
                loop.call_soon(loop.stop)

            eleza data_received(self, data):
                super().data_received(data)
                self.transport.write(expected_response)

        lsock = socket.create_server(('127.0.0.1', 0), backlog=1)
        addr = lsock.getsockname()

        message = b'test data'
        response = Tupu
        expected_response = b'roger'

        eleza client():
            nonlocal response
            jaribu:
                csock = socket.socket()
                ikiwa client_ssl ni sio Tupu:
                    csock = client_ssl.wrap_socket(csock)
                csock.connect(addr)
                csock.sendall(message)
                response = csock.recv(99)
                csock.close()
            tatizo Exception kama exc:
                andika(
                    "Failure kwenye client thread kwenye test_connect_accepted_socket",
                    exc)

        thread = threading.Thread(target=client, daemon=Kweli)
        thread.start()

        conn, _ = lsock.accept()
        proto = MyProto(loop=loop)
        proto.loop = loop
        loop.run_until_complete(
            loop.connect_accepted_socket(
                (lambda: proto), conn, ssl=server_ssl))
        loop.run_forever()
        proto.transport.close()
        lsock.close()

        support.join_thread(thread, timeout=1)
        self.assertUongo(thread.is_alive())
        self.assertEqual(proto.state, 'CLOSED')
        self.assertEqual(proto.nbytes, len(message))
        self.assertEqual(response, expected_response)

    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_ssl_connect_accepted_socket(self):
        ikiwa (sys.platform == 'win32' na
            sys.version_info < (3, 5) na
            isinstance(self.loop, proactor_events.BaseProactorEventLoop)
            ):
            ashiria unittest.SkipTest(
                'SSL sio supported ukijumuisha proactor event loops before Python 3.5'
                )

        server_context = test_utils.simple_server_sslcontext()
        client_context = test_utils.simple_client_sslcontext()

        self.test_connect_accepted_socket(server_context, client_context)

    eleza test_connect_accepted_socket_ssl_timeout_for_plain_socket(self):
        sock = socket.socket()
        self.addCleanup(sock.close)
        coro = self.loop.connect_accepted_socket(
            MyProto, sock, ssl_handshake_timeout=1)
        ukijumuisha self.assertRaisesRegex(
                ValueError,
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl'):
            self.loop.run_until_complete(coro)

    @mock.patch('asyncio.base_events.socket')
    eleza create_server_multiple_hosts(self, family, hosts, mock_sock):
        async eleza getaddrinfo(host, port, *args, **kw):
            ikiwa family == socket.AF_INET:
                rudisha [(family, socket.SOCK_STREAM, 6, '', (host, port))]
            isipokua:
                rudisha [(family, socket.SOCK_STREAM, 6, '', (host, port, 0, 0))]

        eleza getaddrinfo_task(*args, **kwds):
            rudisha self.loop.create_task(getaddrinfo(*args, **kwds))

        unique_hosts = set(hosts)

        ikiwa family == socket.AF_INET:
            mock_sock.socket().getsockbyname.side_effect = [
                (host, 80) kila host kwenye unique_hosts]
        isipokua:
            mock_sock.socket().getsockbyname.side_effect = [
                (host, 80, 0, 0) kila host kwenye unique_hosts]
        self.loop.getaddrinfo = getaddrinfo_task
        self.loop._start_serving = mock.Mock()
        self.loop._stop_serving = mock.Mock()
        f = self.loop.create_server(lambda: MyProto(self.loop), hosts, 80)
        server = self.loop.run_until_complete(f)
        self.addCleanup(server.close)
        server_hosts = {sock.getsockbyname()[0] kila sock kwenye server.sockets}
        self.assertEqual(server_hosts, unique_hosts)

    eleza test_create_server_multiple_hosts_ipv4(self):
        self.create_server_multiple_hosts(socket.AF_INET,
                                          ['1.2.3.4', '5.6.7.8', '1.2.3.4'])

    eleza test_create_server_multiple_hosts_ipv6(self):
        self.create_server_multiple_hosts(socket.AF_INET6,
                                          ['::1', '::2', '::1'])

    eleza test_create_server(self):
        proto = MyProto(self.loop)
        f = self.loop.create_server(lambda: proto, '0.0.0.0', 0)
        server = self.loop.run_until_complete(f)
        self.assertEqual(len(server.sockets), 1)
        sock = server.sockets[0]
        host, port = sock.getsockname()
        self.assertEqual(host, '0.0.0.0')
        client = socket.socket()
        client.connect(('127.0.0.1', port))
        client.sendall(b'xxx')

        self.loop.run_until_complete(proto.connected)
        self.assertEqual('CONNECTED', proto.state)

        test_utils.run_until(self.loop, lambda: proto.nbytes > 0)
        self.assertEqual(3, proto.nbytes)

        # extra info ni available
        self.assertIsNotTupu(proto.transport.get_extra_info('sockname'))
        self.assertEqual('127.0.0.1',
                         proto.transport.get_extra_info('peername')[0])

        # close connection
        proto.transport.close()
        self.loop.run_until_complete(proto.done)

        self.assertEqual('CLOSED', proto.state)

        # the client socket must be closed after to avoid ECONNRESET upon
        # recv()/send() on the serving socket
        client.close()

        # close server
        server.close()

    @unittest.skipUnless(hasattr(socket, 'SO_REUSEPORT'), 'No SO_REUSEPORT')
    eleza test_create_server_reuse_port(self):
        proto = MyProto(self.loop)
        f = self.loop.create_server(
            lambda: proto, '0.0.0.0', 0)
        server = self.loop.run_until_complete(f)
        self.assertEqual(len(server.sockets), 1)
        sock = server.sockets[0]
        self.assertUongo(
            sock.getsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEPORT))
        server.close()

        test_utils.run_briefly(self.loop)

        proto = MyProto(self.loop)
        f = self.loop.create_server(
            lambda: proto, '0.0.0.0', 0, reuse_port=Kweli)
        server = self.loop.run_until_complete(f)
        self.assertEqual(len(server.sockets), 1)
        sock = server.sockets[0]
        self.assertKweli(
            sock.getsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEPORT))
        server.close()

    eleza _make_unix_server(self, factory, **kwargs):
        path = test_utils.gen_unix_socket_path()
        self.addCleanup(lambda: os.path.exists(path) na os.unlink(path))

        f = self.loop.create_unix_server(factory, path, **kwargs)
        server = self.loop.run_until_complete(f)

        rudisha server, path

    @support.skip_unless_bind_unix_socket
    eleza test_create_unix_server(self):
        proto = MyProto(loop=self.loop)
        server, path = self._make_unix_server(lambda: proto)
        self.assertEqual(len(server.sockets), 1)

        client = socket.socket(socket.AF_UNIX)
        client.connect(path)
        client.sendall(b'xxx')

        self.loop.run_until_complete(proto.connected)
        self.assertEqual('CONNECTED', proto.state)
        test_utils.run_until(self.loop, lambda: proto.nbytes > 0)
        self.assertEqual(3, proto.nbytes)

        # close connection
        proto.transport.close()
        self.loop.run_until_complete(proto.done)

        self.assertEqual('CLOSED', proto.state)

        # the client socket must be closed after to avoid ECONNRESET upon
        # recv()/send() on the serving socket
        client.close()

        # close server
        server.close()

    @unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'No UNIX Sockets')
    eleza test_create_unix_server_path_socket_error(self):
        proto = MyProto(loop=self.loop)
        sock = socket.socket()
        ukijumuisha sock:
            f = self.loop.create_unix_server(lambda: proto, '/test', sock=sock)
            ukijumuisha self.assertRaisesRegex(ValueError,
                                        'path na sock can sio be specified '
                                        'at the same time'):
                self.loop.run_until_complete(f)

    eleza _create_ssl_context(self, certfile, keyfile=Tupu):
        sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslcontext.options |= ssl.OP_NO_SSLv2
        sslcontext.load_cert_chain(certfile, keyfile)
        rudisha sslcontext

    eleza _make_ssl_server(self, factory, certfile, keyfile=Tupu):
        sslcontext = self._create_ssl_context(certfile, keyfile)

        f = self.loop.create_server(factory, '127.0.0.1', 0, ssl=sslcontext)
        server = self.loop.run_until_complete(f)

        sock = server.sockets[0]
        host, port = sock.getsockname()
        self.assertEqual(host, '127.0.0.1')
        rudisha server, host, port

    eleza _make_ssl_unix_server(self, factory, certfile, keyfile=Tupu):
        sslcontext = self._create_ssl_context(certfile, keyfile)
        rudisha self._make_unix_server(factory, ssl=sslcontext)

    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_server_ssl(self):
        proto = MyProto(loop=self.loop)
        server, host, port = self._make_ssl_server(
            lambda: proto, test_utils.ONLYCERT, test_utils.ONLYKEY)

        f_c = self.loop.create_connection(MyBaseProto, host, port,
                                          ssl=test_utils.dummy_ssl_context())
        client, pr = self.loop.run_until_complete(f_c)

        client.write(b'xxx')
        self.loop.run_until_complete(proto.connected)
        self.assertEqual('CONNECTED', proto.state)

        test_utils.run_until(self.loop, lambda: proto.nbytes > 0)
        self.assertEqual(3, proto.nbytes)

        # extra info ni available
        self.check_ssl_extra_info(client, peername=(host, port))

        # close connection
        proto.transport.close()
        self.loop.run_until_complete(proto.done)
        self.assertEqual('CLOSED', proto.state)

        # the client socket must be closed after to avoid ECONNRESET upon
        # recv()/send() on the serving socket
        client.close()

        # stop serving
        server.close()

    @support.skip_unless_bind_unix_socket
    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_unix_server_ssl(self):
        proto = MyProto(loop=self.loop)
        server, path = self._make_ssl_unix_server(
            lambda: proto, test_utils.ONLYCERT, test_utils.ONLYKEY)

        f_c = self.loop.create_unix_connection(
            MyBaseProto, path, ssl=test_utils.dummy_ssl_context(),
            server_hostname='')

        client, pr = self.loop.run_until_complete(f_c)

        client.write(b'xxx')
        self.loop.run_until_complete(proto.connected)
        self.assertEqual('CONNECTED', proto.state)
        test_utils.run_until(self.loop, lambda: proto.nbytes > 0)
        self.assertEqual(3, proto.nbytes)

        # close connection
        proto.transport.close()
        self.loop.run_until_complete(proto.done)
        self.assertEqual('CLOSED', proto.state)

        # the client socket must be closed after to avoid ECONNRESET upon
        # recv()/send() on the serving socket
        client.close()

        # stop serving
        server.close()

    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_server_ssl_verify_failed(self):
        proto = MyProto(loop=self.loop)
        server, host, port = self._make_ssl_server(
            lambda: proto, test_utils.SIGNED_CERTFILE)

        sslcontext_client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslcontext_client.options |= ssl.OP_NO_SSLv2
        sslcontext_client.verify_mode = ssl.CERT_REQUIRED
        ikiwa hasattr(sslcontext_client, 'check_hostname'):
            sslcontext_client.check_hostname = Kweli


        # no CA loaded
        f_c = self.loop.create_connection(MyProto, host, port,
                                          ssl=sslcontext_client)
        ukijumuisha mock.patch.object(self.loop, 'call_exception_handler'):
            ukijumuisha test_utils.disable_logger():
                ukijumuisha self.assertRaisesRegex(ssl.SSLError,
                                            '(?i)certificate.verify.failed'):
                    self.loop.run_until_complete(f_c)

            # execute the loop to log the connection error
            test_utils.run_briefly(self.loop)

        # close connection
        self.assertIsTupu(proto.transport)
        server.close()

    @support.skip_unless_bind_unix_socket
    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_unix_server_ssl_verify_failed(self):
        proto = MyProto(loop=self.loop)
        server, path = self._make_ssl_unix_server(
            lambda: proto, test_utils.SIGNED_CERTFILE)

        sslcontext_client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslcontext_client.options |= ssl.OP_NO_SSLv2
        sslcontext_client.verify_mode = ssl.CERT_REQUIRED
        ikiwa hasattr(sslcontext_client, 'check_hostname'):
            sslcontext_client.check_hostname = Kweli

        # no CA loaded
        f_c = self.loop.create_unix_connection(MyProto, path,
                                               ssl=sslcontext_client,
                                               server_hostname='invalid')
        ukijumuisha mock.patch.object(self.loop, 'call_exception_handler'):
            ukijumuisha test_utils.disable_logger():
                ukijumuisha self.assertRaisesRegex(ssl.SSLError,
                                            '(?i)certificate.verify.failed'):
                    self.loop.run_until_complete(f_c)

            # execute the loop to log the connection error
            test_utils.run_briefly(self.loop)

        # close connection
        self.assertIsTupu(proto.transport)
        server.close()

    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_server_ssl_match_failed(self):
        proto = MyProto(loop=self.loop)
        server, host, port = self._make_ssl_server(
            lambda: proto, test_utils.SIGNED_CERTFILE)

        sslcontext_client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslcontext_client.options |= ssl.OP_NO_SSLv2
        sslcontext_client.verify_mode = ssl.CERT_REQUIRED
        sslcontext_client.load_verify_locations(
            cafile=test_utils.SIGNING_CA)
        ikiwa hasattr(sslcontext_client, 'check_hostname'):
            sslcontext_client.check_hostname = Kweli

        # incorrect server_hostname
        f_c = self.loop.create_connection(MyProto, host, port,
                                          ssl=sslcontext_client)
        ukijumuisha mock.patch.object(self.loop, 'call_exception_handler'):
            ukijumuisha test_utils.disable_logger():
                ukijumuisha self.assertRaisesRegex(
                        ssl.CertificateError,
                        "IP address mismatch, certificate ni sio valid kila "
                        "'127.0.0.1'"):
                    self.loop.run_until_complete(f_c)

        # close connection
        # transport ni Tupu because TLS ALERT aborted the handshake
        self.assertIsTupu(proto.transport)
        server.close()

    @support.skip_unless_bind_unix_socket
    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_unix_server_ssl_verified(self):
        proto = MyProto(loop=self.loop)
        server, path = self._make_ssl_unix_server(
            lambda: proto, test_utils.SIGNED_CERTFILE)

        sslcontext_client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslcontext_client.options |= ssl.OP_NO_SSLv2
        sslcontext_client.verify_mode = ssl.CERT_REQUIRED
        sslcontext_client.load_verify_locations(cafile=test_utils.SIGNING_CA)
        ikiwa hasattr(sslcontext_client, 'check_hostname'):
            sslcontext_client.check_hostname = Kweli

        # Connection succeeds ukijumuisha correct CA na server hostname.
        f_c = self.loop.create_unix_connection(MyProto, path,
                                               ssl=sslcontext_client,
                                               server_hostname='localhost')
        client, pr = self.loop.run_until_complete(f_c)

        # close connection
        proto.transport.close()
        client.close()
        server.close()
        self.loop.run_until_complete(proto.done)

    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_create_server_ssl_verified(self):
        proto = MyProto(loop=self.loop)
        server, host, port = self._make_ssl_server(
            lambda: proto, test_utils.SIGNED_CERTFILE)

        sslcontext_client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        sslcontext_client.options |= ssl.OP_NO_SSLv2
        sslcontext_client.verify_mode = ssl.CERT_REQUIRED
        sslcontext_client.load_verify_locations(cafile=test_utils.SIGNING_CA)
        ikiwa hasattr(sslcontext_client, 'check_hostname'):
            sslcontext_client.check_hostname = Kweli

        # Connection succeeds ukijumuisha correct CA na server hostname.
        f_c = self.loop.create_connection(MyProto, host, port,
                                          ssl=sslcontext_client,
                                          server_hostname='localhost')
        client, pr = self.loop.run_until_complete(f_c)

        # extra info ni available
        self.check_ssl_extra_info(client, peername=(host, port),
                                  peercert=test_utils.PEERCERT)

        # close connection
        proto.transport.close()
        client.close()
        server.close()
        self.loop.run_until_complete(proto.done)

    eleza test_create_server_sock(self):
        proto = self.loop.create_future()

        kundi TestMyProto(MyProto):
            eleza connection_made(self, transport):
                super().connection_made(transport)
                proto.set_result(self)

        sock_ob = socket.create_server(('0.0.0.0', 0))

        f = self.loop.create_server(TestMyProto, sock=sock_ob)
        server = self.loop.run_until_complete(f)
        sock = server.sockets[0]
        self.assertEqual(sock.fileno(), sock_ob.fileno())

        host, port = sock.getsockname()
        self.assertEqual(host, '0.0.0.0')
        client = socket.socket()
        client.connect(('127.0.0.1', port))
        client.send(b'xxx')
        client.close()
        server.close()

    eleza test_create_server_addr_in_use(self):
        sock_ob = socket.create_server(('0.0.0.0', 0))

        f = self.loop.create_server(MyProto, sock=sock_ob)
        server = self.loop.run_until_complete(f)
        sock = server.sockets[0]
        host, port = sock.getsockname()

        f = self.loop.create_server(MyProto, host=host, port=port)
        ukijumuisha self.assertRaises(OSError) kama cm:
            self.loop.run_until_complete(f)
        self.assertEqual(cm.exception.errno, errno.EADDRINUSE)

        server.close()

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 sio supported ama enabled')
    eleza test_create_server_dual_stack(self):
        f_proto = self.loop.create_future()

        kundi TestMyProto(MyProto):
            eleza connection_made(self, transport):
                super().connection_made(transport)
                f_proto.set_result(self)

        try_count = 0
        wakati Kweli:
            jaribu:
                port = support.find_unused_port()
                f = self.loop.create_server(TestMyProto, host=Tupu, port=port)
                server = self.loop.run_until_complete(f)
            tatizo OSError kama ex:
                ikiwa ex.errno == errno.EADDRINUSE:
                    try_count += 1
                    self.assertGreaterEqual(5, try_count)
                    endelea
                isipokua:
                    raise
            isipokua:
                koma
        client = socket.socket()
        client.connect(('127.0.0.1', port))
        client.send(b'xxx')
        proto = self.loop.run_until_complete(f_proto)
        proto.transport.close()
        client.close()

        f_proto = self.loop.create_future()
        client = socket.socket(socket.AF_INET6)
        client.connect(('::1', port))
        client.send(b'xxx')
        proto = self.loop.run_until_complete(f_proto)
        proto.transport.close()
        client.close()

        server.close()

    eleza test_server_close(self):
        f = self.loop.create_server(MyProto, '0.0.0.0', 0)
        server = self.loop.run_until_complete(f)
        sock = server.sockets[0]
        host, port = sock.getsockname()

        client = socket.socket()
        client.connect(('127.0.0.1', port))
        client.send(b'xxx')
        client.close()

        server.close()

        client = socket.socket()
        self.assertRaises(
            ConnectionRefusedError, client.connect, ('127.0.0.1', port))
        client.close()

    eleza test_create_datagram_endpoint(self):
        kundi TestMyDatagramProto(MyDatagramProto):
            eleza __init__(inner_self):
                super().__init__(loop=self.loop)

            eleza datagram_received(self, data, addr):
                super().datagram_received(data, addr)
                self.transport.sendto(b'resp:'+data, addr)

        coro = self.loop.create_datagram_endpoint(
            TestMyDatagramProto, local_addr=('127.0.0.1', 0))
        s_transport, server = self.loop.run_until_complete(coro)
        host, port = s_transport.get_extra_info('sockname')

        self.assertIsInstance(s_transport, asyncio.Transport)
        self.assertIsInstance(server, TestMyDatagramProto)
        self.assertEqual('INITIALIZED', server.state)
        self.assertIs(server.transport, s_transport)

        coro = self.loop.create_datagram_endpoint(
            lambda: MyDatagramProto(loop=self.loop),
            remote_addr=(host, port))
        transport, client = self.loop.run_until_complete(coro)

        self.assertIsInstance(transport, asyncio.Transport)
        self.assertIsInstance(client, MyDatagramProto)
        self.assertEqual('INITIALIZED', client.state)
        self.assertIs(client.transport, transport)

        transport.sendto(b'xxx')
        test_utils.run_until(self.loop, lambda: server.nbytes)
        self.assertEqual(3, server.nbytes)
        test_utils.run_until(self.loop, lambda: client.nbytes)

        # received
        self.assertEqual(8, client.nbytes)

        # extra info ni available
        self.assertIsNotTupu(transport.get_extra_info('sockname'))

        # close connection
        transport.close()
        self.loop.run_until_complete(client.done)
        self.assertEqual('CLOSED', client.state)
        server.transport.close()

    eleza test_create_datagram_endpoint_sock(self):
        sock = Tupu
        local_address = ('127.0.0.1', 0)
        infos = self.loop.run_until_complete(
            self.loop.getaddrinfo(
                *local_address, type=socket.SOCK_DGRAM))
        kila family, type, proto, cname, address kwenye infos:
            jaribu:
                sock = socket.socket(family=family, type=type, proto=proto)
                sock.setblocking(Uongo)
                sock.bind(address)
            tatizo:
                pita
            isipokua:
                koma
        isipokua:
            assert Uongo, 'Can sio create socket.'

        f = self.loop.create_datagram_endpoint(
            lambda: MyDatagramProto(loop=self.loop), sock=sock)
        tr, pr = self.loop.run_until_complete(f)
        self.assertIsInstance(tr, asyncio.Transport)
        self.assertIsInstance(pr, MyDatagramProto)
        tr.close()
        self.loop.run_until_complete(pr.done)

    eleza test_internal_fds(self):
        loop = self.create_event_loop()
        ikiwa sio isinstance(loop, selector_events.BaseSelectorEventLoop):
            loop.close()
            self.skipTest('loop ni sio a BaseSelectorEventLoop')

        self.assertEqual(1, loop._internal_fds)
        loop.close()
        self.assertEqual(0, loop._internal_fds)
        self.assertIsTupu(loop._csock)
        self.assertIsTupu(loop._ssock)

    @unittest.skipUnless(sys.platform != 'win32',
                         "Don't support pipes kila Windows")
    eleza test_read_pipe(self):
        proto = MyReadPipeProto(loop=self.loop)

        rpipe, wpipe = os.pipe()
        pipeobj = io.open(rpipe, 'rb', 1024)

        async eleza connect():
            t, p = await self.loop.connect_read_pipe(
                lambda: proto, pipeobj)
            self.assertIs(p, proto)
            self.assertIs(t, proto.transport)
            self.assertEqual(['INITIAL', 'CONNECTED'], proto.state)
            self.assertEqual(0, proto.nbytes)

        self.loop.run_until_complete(connect())

        os.write(wpipe, b'1')
        test_utils.run_until(self.loop, lambda: proto.nbytes >= 1)
        self.assertEqual(1, proto.nbytes)

        os.write(wpipe, b'2345')
        test_utils.run_until(self.loop, lambda: proto.nbytes >= 5)
        self.assertEqual(['INITIAL', 'CONNECTED'], proto.state)
        self.assertEqual(5, proto.nbytes)

        os.close(wpipe)
        self.loop.run_until_complete(proto.done)
        self.assertEqual(
            ['INITIAL', 'CONNECTED', 'EOF', 'CLOSED'], proto.state)
        # extra info ni available
        self.assertIsNotTupu(proto.transport.get_extra_info('pipe'))

    @unittest.skipUnless(sys.platform != 'win32',
                         "Don't support pipes kila Windows")
    eleza test_unclosed_pipe_transport(self):
        # This test reproduces the issue #314 on GitHub
        loop = self.create_event_loop()
        read_proto = MyReadPipeProto(loop=loop)
        write_proto = MyWritePipeProto(loop=loop)

        rpipe, wpipe = os.pipe()
        rpipeobj = io.open(rpipe, 'rb', 1024)
        wpipeobj = io.open(wpipe, 'w', 1024)

        async eleza connect():
            read_transport, _ = await loop.connect_read_pipe(
                lambda: read_proto, rpipeobj)
            write_transport, _ = await loop.connect_write_pipe(
                lambda: write_proto, wpipeobj)
            rudisha read_transport, write_transport

        # Run na close the loop without closing the transports
        read_transport, write_transport = loop.run_until_complete(connect())
        loop.close()

        # These 'repr' calls used to ashiria an AttributeError
        # See Issue #314 on GitHub
        self.assertIn('open', repr(read_transport))
        self.assertIn('open', repr(write_transport))

        # Clean up (avoid ResourceWarning)
        rpipeobj.close()
        wpipeobj.close()
        read_transport._pipe = Tupu
        write_transport._pipe = Tupu

    @unittest.skipUnless(sys.platform != 'win32',
                         "Don't support pipes kila Windows")
    eleza test_read_pty_output(self):
        proto = MyReadPipeProto(loop=self.loop)

        master, slave = os.openpty()
        master_read_obj = io.open(master, 'rb', 0)

        async eleza connect():
            t, p = await self.loop.connect_read_pipe(lambda: proto,
                                                     master_read_obj)
            self.assertIs(p, proto)
            self.assertIs(t, proto.transport)
            self.assertEqual(['INITIAL', 'CONNECTED'], proto.state)
            self.assertEqual(0, proto.nbytes)

        self.loop.run_until_complete(connect())

        os.write(slave, b'1')
        test_utils.run_until(self.loop, lambda: proto.nbytes)
        self.assertEqual(1, proto.nbytes)

        os.write(slave, b'2345')
        test_utils.run_until(self.loop, lambda: proto.nbytes >= 5)
        self.assertEqual(['INITIAL', 'CONNECTED'], proto.state)
        self.assertEqual(5, proto.nbytes)

        os.close(slave)
        proto.transport.close()
        self.loop.run_until_complete(proto.done)
        self.assertEqual(
            ['INITIAL', 'CONNECTED', 'EOF', 'CLOSED'], proto.state)
        # extra info ni available
        self.assertIsNotTupu(proto.transport.get_extra_info('pipe'))

    @unittest.skipUnless(sys.platform != 'win32',
                         "Don't support pipes kila Windows")
    eleza test_write_pipe(self):
        rpipe, wpipe = os.pipe()
        pipeobj = io.open(wpipe, 'wb', 1024)

        proto = MyWritePipeProto(loop=self.loop)
        connect = self.loop.connect_write_pipe(lambda: proto, pipeobj)
        transport, p = self.loop.run_until_complete(connect)
        self.assertIs(p, proto)
        self.assertIs(transport, proto.transport)
        self.assertEqual('CONNECTED', proto.state)

        transport.write(b'1')

        data = bytearray()
        eleza reader(data):
            chunk = os.read(rpipe, 1024)
            data += chunk
            rudisha len(data)

        test_utils.run_until(self.loop, lambda: reader(data) >= 1)
        self.assertEqual(b'1', data)

        transport.write(b'2345')
        test_utils.run_until(self.loop, lambda: reader(data) >= 5)
        self.assertEqual(b'12345', data)
        self.assertEqual('CONNECTED', proto.state)

        os.close(rpipe)

        # extra info ni available
        self.assertIsNotTupu(proto.transport.get_extra_info('pipe'))

        # close connection
        proto.transport.close()
        self.loop.run_until_complete(proto.done)
        self.assertEqual('CLOSED', proto.state)

    @unittest.skipUnless(sys.platform != 'win32',
                         "Don't support pipes kila Windows")
    eleza test_write_pipe_disconnect_on_close(self):
        rsock, wsock = socket.socketpair()
        rsock.setblocking(Uongo)
        pipeobj = io.open(wsock.detach(), 'wb', 1024)

        proto = MyWritePipeProto(loop=self.loop)
        connect = self.loop.connect_write_pipe(lambda: proto, pipeobj)
        transport, p = self.loop.run_until_complete(connect)
        self.assertIs(p, proto)
        self.assertIs(transport, proto.transport)
        self.assertEqual('CONNECTED', proto.state)

        transport.write(b'1')
        data = self.loop.run_until_complete(self.loop.sock_recv(rsock, 1024))
        self.assertEqual(b'1', data)

        rsock.close()

        self.loop.run_until_complete(proto.done)
        self.assertEqual('CLOSED', proto.state)

    @unittest.skipUnless(sys.platform != 'win32',
                         "Don't support pipes kila Windows")
    # select, poll na kqueue don't support character devices (PTY) on Mac OS X
    # older than 10.6 (Snow Leopard)
    @support.requires_mac_ver(10, 6)
    eleza test_write_pty(self):
        master, slave = os.openpty()
        slave_write_obj = io.open(slave, 'wb', 0)

        proto = MyWritePipeProto(loop=self.loop)
        connect = self.loop.connect_write_pipe(lambda: proto, slave_write_obj)
        transport, p = self.loop.run_until_complete(connect)
        self.assertIs(p, proto)
        self.assertIs(transport, proto.transport)
        self.assertEqual('CONNECTED', proto.state)

        transport.write(b'1')

        data = bytearray()
        eleza reader(data):
            chunk = os.read(master, 1024)
            data += chunk
            rudisha len(data)

        test_utils.run_until(self.loop, lambda: reader(data) >= 1,
                             timeout=10)
        self.assertEqual(b'1', data)

        transport.write(b'2345')
        test_utils.run_until(self.loop, lambda: reader(data) >= 5,
                             timeout=10)
        self.assertEqual(b'12345', data)
        self.assertEqual('CONNECTED', proto.state)

        os.close(master)

        # extra info ni available
        self.assertIsNotTupu(proto.transport.get_extra_info('pipe'))

        # close connection
        proto.transport.close()
        self.loop.run_until_complete(proto.done)
        self.assertEqual('CLOSED', proto.state)

    @unittest.skipUnless(sys.platform != 'win32',
                         "Don't support pipes kila Windows")
    # select, poll na kqueue don't support character devices (PTY) on Mac OS X
    # older than 10.6 (Snow Leopard)
    @support.requires_mac_ver(10, 6)
    eleza test_bidirectional_pty(self):
        master, read_slave = os.openpty()
        write_slave = os.dup(read_slave)
        tty.setraw(read_slave)

        slave_read_obj = io.open(read_slave, 'rb', 0)
        read_proto = MyReadPipeProto(loop=self.loop)
        read_connect = self.loop.connect_read_pipe(lambda: read_proto,
                                                   slave_read_obj)
        read_transport, p = self.loop.run_until_complete(read_connect)
        self.assertIs(p, read_proto)
        self.assertIs(read_transport, read_proto.transport)
        self.assertEqual(['INITIAL', 'CONNECTED'], read_proto.state)
        self.assertEqual(0, read_proto.nbytes)


        slave_write_obj = io.open(write_slave, 'wb', 0)
        write_proto = MyWritePipeProto(loop=self.loop)
        write_connect = self.loop.connect_write_pipe(lambda: write_proto,
                                                     slave_write_obj)
        write_transport, p = self.loop.run_until_complete(write_connect)
        self.assertIs(p, write_proto)
        self.assertIs(write_transport, write_proto.transport)
        self.assertEqual('CONNECTED', write_proto.state)

        data = bytearray()
        eleza reader(data):
            chunk = os.read(master, 1024)
            data += chunk
            rudisha len(data)

        write_transport.write(b'1')
        test_utils.run_until(self.loop, lambda: reader(data) >= 1, timeout=10)
        self.assertEqual(b'1', data)
        self.assertEqual(['INITIAL', 'CONNECTED'], read_proto.state)
        self.assertEqual('CONNECTED', write_proto.state)

        os.write(master, b'a')
        test_utils.run_until(self.loop, lambda: read_proto.nbytes >= 1,
                             timeout=10)
        self.assertEqual(['INITIAL', 'CONNECTED'], read_proto.state)
        self.assertEqual(1, read_proto.nbytes)
        self.assertEqual('CONNECTED', write_proto.state)

        write_transport.write(b'2345')
        test_utils.run_until(self.loop, lambda: reader(data) >= 5, timeout=10)
        self.assertEqual(b'12345', data)
        self.assertEqual(['INITIAL', 'CONNECTED'], read_proto.state)
        self.assertEqual('CONNECTED', write_proto.state)

        os.write(master, b'bcde')
        test_utils.run_until(self.loop, lambda: read_proto.nbytes >= 5,
                             timeout=10)
        self.assertEqual(['INITIAL', 'CONNECTED'], read_proto.state)
        self.assertEqual(5, read_proto.nbytes)
        self.assertEqual('CONNECTED', write_proto.state)

        os.close(master)

        read_transport.close()
        self.loop.run_until_complete(read_proto.done)
        self.assertEqual(
            ['INITIAL', 'CONNECTED', 'EOF', 'CLOSED'], read_proto.state)

        write_transport.close()
        self.loop.run_until_complete(write_proto.done)
        self.assertEqual('CLOSED', write_proto.state)

    eleza test_prompt_cancellation(self):
        r, w = socket.socketpair()
        r.setblocking(Uongo)
        f = self.loop.create_task(self.loop.sock_recv(r, 1))
        ov = getattr(f, 'ov', Tupu)
        ikiwa ov ni sio Tupu:
            self.assertKweli(ov.pending)

        async eleza main():
            jaribu:
                self.loop.call_soon(f.cancel)
                await f
            tatizo asyncio.CancelledError:
                res = 'cancelled'
            isipokua:
                res = Tupu
            mwishowe:
                self.loop.stop()
            rudisha res

        start = time.monotonic()
        t = self.loop.create_task(main())
        self.loop.run_forever()
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, 0.1)
        self.assertEqual(t.result(), 'cancelled')
        self.assertRaises(asyncio.CancelledError, f.result)
        ikiwa ov ni sio Tupu:
            self.assertUongo(ov.pending)
        self.loop._stop_serving(r)

        r.close()
        w.close()

    eleza test_timeout_rounding(self):
        eleza _run_once():
            self.loop._run_once_counter += 1
            orig_run_once()

        orig_run_once = self.loop._run_once
        self.loop._run_once_counter = 0
        self.loop._run_once = _run_once

        async eleza wait():
            loop = self.loop
            await asyncio.sleep(1e-2)
            await asyncio.sleep(1e-4)
            await asyncio.sleep(1e-6)
            await asyncio.sleep(1e-8)
            await asyncio.sleep(1e-10)

        self.loop.run_until_complete(wait())
        # The ideal number of call ni 12, but on some platforms, the selector
        # may sleep at little bit less than timeout depending on the resolution
        # of the clock used by the kernel. Tolerate a few useless calls on
        # these platforms.
        self.assertLessEqual(self.loop._run_once_counter, 20,
            {'clock_resolution': self.loop._clock_resolution,
             'selector': self.loop._selector.__class__.__name__})

    eleza test_remove_fds_after_closing(self):
        loop = self.create_event_loop()
        callback = lambda: Tupu
        r, w = socket.socketpair()
        self.addCleanup(r.close)
        self.addCleanup(w.close)
        loop.add_reader(r, callback)
        loop.add_writer(w, callback)
        loop.close()
        self.assertUongo(loop.remove_reader(r))
        self.assertUongo(loop.remove_writer(w))

    eleza test_add_fds_after_closing(self):
        loop = self.create_event_loop()
        callback = lambda: Tupu
        r, w = socket.socketpair()
        self.addCleanup(r.close)
        self.addCleanup(w.close)
        loop.close()
        ukijumuisha self.assertRaises(RuntimeError):
            loop.add_reader(r, callback)
        ukijumuisha self.assertRaises(RuntimeError):
            loop.add_writer(w, callback)

    eleza test_close_running_event_loop(self):
        async eleza close_loop(loop):
            self.loop.close()

        coro = close_loop(self.loop)
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.run_until_complete(coro)

    eleza test_close(self):
        self.loop.close()

        async eleza test():
            pita

        func = lambda: Uongo
        coro = test()
        self.addCleanup(coro.close)

        # operation blocked when the loop ni closed
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.run_forever()
        ukijumuisha self.assertRaises(RuntimeError):
            fut = self.loop.create_future()
            self.loop.run_until_complete(fut)
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.call_soon(func)
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.call_soon_threadsafe(func)
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.call_later(1.0, func)
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.call_at(self.loop.time() + .0, func)
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.create_task(coro)
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.add_signal_handler(signal.SIGTERM, func)

        # run_in_executor test ni tricky: the method ni a coroutine,
        # but run_until_complete cansio be called on closed loop.
        # Thus iterate once explicitly.
        ukijumuisha self.assertRaises(RuntimeError):
            it = self.loop.run_in_executor(Tupu, func).__await__()
            next(it)


kundi SubprocessTestsMixin:

    eleza check_terminated(self, returncode):
        ikiwa sys.platform == 'win32':
            self.assertIsInstance(returncode, int)
            # expect 1 but sometimes get 0
        isipokua:
            self.assertEqual(-signal.SIGTERM, returncode)

    eleza check_killed(self, returncode):
        ikiwa sys.platform == 'win32':
            self.assertIsInstance(returncode, int)
            # expect 1 but sometimes get 0
        isipokua:
            self.assertEqual(-signal.SIGKILL, returncode)

    eleza test_subprocess_exec(self):
        prog = os.path.join(os.path.dirname(__file__), 'echo.py')

        connect = self.loop.subprocess_exec(
                        functools.partial(MySubprocessProtocol, self.loop),
                        sys.executable, prog)
        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
            self.assertIsInstance(proto, MySubprocessProtocol)
            self.loop.run_until_complete(proto.connected)
            self.assertEqual('CONNECTED', proto.state)

            stdin = transp.get_pipe_transport(0)
            stdin.write(b'Python The Winner')
            self.loop.run_until_complete(proto.got_data[1].wait())
            ukijumuisha test_utils.disable_logger():
                transp.close()
            self.loop.run_until_complete(proto.completed)
            self.check_killed(proto.returncode)
            self.assertEqual(b'Python The Winner', proto.data[1])

    eleza test_subprocess_interactive(self):
        prog = os.path.join(os.path.dirname(__file__), 'echo.py')

        connect = self.loop.subprocess_exec(
                        functools.partial(MySubprocessProtocol, self.loop),
                        sys.executable, prog)

        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
            self.assertIsInstance(proto, MySubprocessProtocol)
            self.loop.run_until_complete(proto.connected)
            self.assertEqual('CONNECTED', proto.state)

            stdin = transp.get_pipe_transport(0)
            stdin.write(b'Python ')
            self.loop.run_until_complete(proto.got_data[1].wait())
            proto.got_data[1].clear()
            self.assertEqual(b'Python ', proto.data[1])

            stdin.write(b'The Winner')
            self.loop.run_until_complete(proto.got_data[1].wait())
            self.assertEqual(b'Python The Winner', proto.data[1])

            ukijumuisha test_utils.disable_logger():
                transp.close()
            self.loop.run_until_complete(proto.completed)
            self.check_killed(proto.returncode)

    eleza test_subprocess_shell(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            connect = self.loop.subprocess_shell(
                            functools.partial(MySubprocessProtocol, self.loop),
                            'echo Python')
            transp, proto = self.loop.run_until_complete(connect)
            self.assertIsInstance(proto, MySubprocessProtocol)
            self.loop.run_until_complete(proto.connected)

            transp.get_pipe_transport(0).close()
            self.loop.run_until_complete(proto.completed)
            self.assertEqual(0, proto.returncode)
            self.assertKweli(all(f.done() kila f kwenye proto.disconnects.values()))
            self.assertEqual(proto.data[1].rstrip(b'\r\n'), b'Python')
            self.assertEqual(proto.data[2], b'')
            transp.close()

    eleza test_subprocess_exitcode(self):
        connect = self.loop.subprocess_shell(
                        functools.partial(MySubprocessProtocol, self.loop),
                        'exit 7', stdin=Tupu, stdout=Tupu, stderr=Tupu)

        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
        self.assertIsInstance(proto, MySubprocessProtocol)
        self.loop.run_until_complete(proto.completed)
        self.assertEqual(7, proto.returncode)
        transp.close()

    eleza test_subprocess_close_after_finish(self):
        connect = self.loop.subprocess_shell(
                        functools.partial(MySubprocessProtocol, self.loop),
                        'exit 7', stdin=Tupu, stdout=Tupu, stderr=Tupu)
        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
        self.assertIsInstance(proto, MySubprocessProtocol)
        self.assertIsTupu(transp.get_pipe_transport(0))
        self.assertIsTupu(transp.get_pipe_transport(1))
        self.assertIsTupu(transp.get_pipe_transport(2))
        self.loop.run_until_complete(proto.completed)
        self.assertEqual(7, proto.returncode)
        self.assertIsTupu(transp.close())

    eleza test_subprocess_kill(self):
        prog = os.path.join(os.path.dirname(__file__), 'echo.py')

        connect = self.loop.subprocess_exec(
                        functools.partial(MySubprocessProtocol, self.loop),
                        sys.executable, prog)

        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
            self.assertIsInstance(proto, MySubprocessProtocol)
            self.loop.run_until_complete(proto.connected)

            transp.kill()
            self.loop.run_until_complete(proto.completed)
            self.check_killed(proto.returncode)
            transp.close()

    eleza test_subprocess_terminate(self):
        prog = os.path.join(os.path.dirname(__file__), 'echo.py')

        connect = self.loop.subprocess_exec(
                        functools.partial(MySubprocessProtocol, self.loop),
                        sys.executable, prog)

        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
            self.assertIsInstance(proto, MySubprocessProtocol)
            self.loop.run_until_complete(proto.connected)

            transp.terminate()
            self.loop.run_until_complete(proto.completed)
            self.check_terminated(proto.returncode)
            transp.close()

    @unittest.skipIf(sys.platform == 'win32', "Don't have SIGHUP")
    eleza test_subprocess_send_signal(self):
        # bpo-31034: Make sure that we get the default signal handler (killing
        # the process). The parent process may have decided to ignore SIGHUP,
        # na signal handlers are inherited.
        old_handler = signal.signal(signal.SIGHUP, signal.SIG_DFL)
        jaribu:
            prog = os.path.join(os.path.dirname(__file__), 'echo.py')

            connect = self.loop.subprocess_exec(
                            functools.partial(MySubprocessProtocol, self.loop),
                            sys.executable, prog)

            ukijumuisha self.assertWarns(DeprecationWarning):
                transp, proto = self.loop.run_until_complete(connect)
                self.assertIsInstance(proto, MySubprocessProtocol)
                self.loop.run_until_complete(proto.connected)

                transp.send_signal(signal.SIGHUP)
                self.loop.run_until_complete(proto.completed)
                self.assertEqual(-signal.SIGHUP, proto.returncode)
                transp.close()
        mwishowe:
            signal.signal(signal.SIGHUP, old_handler)

    eleza test_subprocess_stderr(self):
        prog = os.path.join(os.path.dirname(__file__), 'echo2.py')

        connect = self.loop.subprocess_exec(
                        functools.partial(MySubprocessProtocol, self.loop),
                        sys.executable, prog)

        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
            self.assertIsInstance(proto, MySubprocessProtocol)
            self.loop.run_until_complete(proto.connected)

            stdin = transp.get_pipe_transport(0)
            stdin.write(b'test')

            self.loop.run_until_complete(proto.completed)

            transp.close()
            self.assertEqual(b'OUT:test', proto.data[1])
            self.assertKweli(proto.data[2].startswith(b'ERR:test'), proto.data[2])
            self.assertEqual(0, proto.returncode)

    eleza test_subprocess_stderr_redirect_to_stdout(self):
        prog = os.path.join(os.path.dirname(__file__), 'echo2.py')

        connect = self.loop.subprocess_exec(
                        functools.partial(MySubprocessProtocol, self.loop),
                        sys.executable, prog, stderr=subprocess.STDOUT)

        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
            self.assertIsInstance(proto, MySubprocessProtocol)
            self.loop.run_until_complete(proto.connected)

            stdin = transp.get_pipe_transport(0)
            self.assertIsNotTupu(transp.get_pipe_transport(1))
            self.assertIsTupu(transp.get_pipe_transport(2))

            stdin.write(b'test')
            self.loop.run_until_complete(proto.completed)
            self.assertKweli(proto.data[1].startswith(b'OUT:testERR:test'),
                            proto.data[1])
            self.assertEqual(b'', proto.data[2])

            transp.close()
            self.assertEqual(0, proto.returncode)

    eleza test_subprocess_close_client_stream(self):
        prog = os.path.join(os.path.dirname(__file__), 'echo3.py')

        connect = self.loop.subprocess_exec(
                        functools.partial(MySubprocessProtocol, self.loop),
                        sys.executable, prog)
        ukijumuisha self.assertWarns(DeprecationWarning):
            transp, proto = self.loop.run_until_complete(connect)
            self.assertIsInstance(proto, MySubprocessProtocol)
            self.loop.run_until_complete(proto.connected)

            stdin = transp.get_pipe_transport(0)
            stdout = transp.get_pipe_transport(1)
            stdin.write(b'test')
            self.loop.run_until_complete(proto.got_data[1].wait())
            self.assertEqual(b'OUT:test', proto.data[1])

            stdout.close()
            self.loop.run_until_complete(proto.disconnects[1])
            stdin.write(b'xxx')
            self.loop.run_until_complete(proto.got_data[2].wait())
            ikiwa sys.platform != 'win32':
                self.assertEqual(b'ERR:BrokenPipeError', proto.data[2])
            isipokua:
                # After closing the read-end of a pipe, writing to the
                # write-end using os.write() fails ukijumuisha errno==EINVAL na
                # GetLastError()==ERROR_INVALID_NAME on Windows!?!  (Using
                # WriteFile() we get ERROR_BROKEN_PIPE kama expected.)
                self.assertEqual(b'ERR:OSError', proto.data[2])
            ukijumuisha test_utils.disable_logger():
                transp.close()
            self.loop.run_until_complete(proto.completed)
            self.check_killed(proto.returncode)

    eleza test_subprocess_wait_no_same_group(self):
        # start the new process kwenye a new session
        connect = self.loop.subprocess_shell(
                        functools.partial(MySubprocessProtocol, self.loop),
                        'exit 7', stdin=Tupu, stdout=Tupu, stderr=Tupu,
                        start_new_session=Kweli)
        _, proto = tuma self.loop.run_until_complete(connect)
        self.assertIsInstance(proto, MySubprocessProtocol)
        self.loop.run_until_complete(proto.completed)
        self.assertEqual(7, proto.returncode)

    eleza test_subprocess_exec_invalid_args(self):
        async eleza connect(**kwds):
            await self.loop.subprocess_exec(
                asyncio.SubprocessProtocol,
                'pwd', **kwds)

        ukijumuisha self.assertRaises(ValueError):
            self.loop.run_until_complete(connect(universal_newlines=Kweli))
        ukijumuisha self.assertRaises(ValueError):
            self.loop.run_until_complete(connect(bufsize=4096))
        ukijumuisha self.assertRaises(ValueError):
            self.loop.run_until_complete(connect(shell=Kweli))

    eleza test_subprocess_shell_invalid_args(self):

        async eleza connect(cmd=Tupu, **kwds):
            ikiwa sio cmd:
                cmd = 'pwd'
            await self.loop.subprocess_shell(
                asyncio.SubprocessProtocol,
                cmd, **kwds)

        ukijumuisha self.assertRaises(ValueError):
            self.loop.run_until_complete(connect(['ls', '-l']))
        ukijumuisha self.assertRaises(ValueError):
            self.loop.run_until_complete(connect(universal_newlines=Kweli))
        ukijumuisha self.assertRaises(ValueError):
            self.loop.run_until_complete(connect(bufsize=4096))
        ukijumuisha self.assertRaises(ValueError):
            self.loop.run_until_complete(connect(shell=Uongo))


ikiwa sys.platform == 'win32':

    kundi SelectEventLoopTests(EventLoopTestsMixin,
                               test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.SelectorEventLoop()

    kundi ProactorEventLoopTests(EventLoopTestsMixin,
                                 SubprocessTestsMixin,
                                 test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.ProactorEventLoop()

        eleza test_reader_callback(self):
            ashiria unittest.SkipTest("IocpEventLoop does sio have add_reader()")

        eleza test_reader_callback_cancel(self):
            ashiria unittest.SkipTest("IocpEventLoop does sio have add_reader()")

        eleza test_writer_callback(self):
            ashiria unittest.SkipTest("IocpEventLoop does sio have add_writer()")

        eleza test_writer_callback_cancel(self):
            ashiria unittest.SkipTest("IocpEventLoop does sio have add_writer()")

        eleza test_remove_fds_after_closing(self):
            ashiria unittest.SkipTest("IocpEventLoop does sio have add_reader()")
isipokua:
    agiza selectors

    kundi UnixEventLoopTestsMixin(EventLoopTestsMixin):
        eleza setUp(self):
            super().setUp()
            watcher = asyncio.SafeChildWatcher()
            watcher.attach_loop(self.loop)
            asyncio.set_child_watcher(watcher)

        eleza tearDown(self):
            asyncio.set_child_watcher(Tupu)
            super().tearDown()


    ikiwa hasattr(selectors, 'KqueueSelector'):
        kundi KqueueEventLoopTests(UnixEventLoopTestsMixin,
                                   SubprocessTestsMixin,
                                   test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(
                    selectors.KqueueSelector())

            # kqueue doesn't support character devices (PTY) on Mac OS X older
            # than 10.9 (Maverick)
            @support.requires_mac_ver(10, 9)
            # Issue #20667: KqueueEventLoopTests.test_read_pty_output()
            # hangs on OpenBSD 5.5
            @unittest.skipIf(sys.platform.startswith('openbsd'),
                             'test hangs on OpenBSD')
            eleza test_read_pty_output(self):
                super().test_read_pty_output()

            # kqueue doesn't support character devices (PTY) on Mac OS X older
            # than 10.9 (Maverick)
            @support.requires_mac_ver(10, 9)
            eleza test_write_pty(self):
                super().test_write_pty()

    ikiwa hasattr(selectors, 'EpollSelector'):
        kundi EPollEventLoopTests(UnixEventLoopTestsMixin,
                                  SubprocessTestsMixin,
                                  test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(selectors.EpollSelector())

    ikiwa hasattr(selectors, 'PollSelector'):
        kundi PollEventLoopTests(UnixEventLoopTestsMixin,
                                 SubprocessTestsMixin,
                                 test_utils.TestCase):

            eleza create_event_loop(self):
                rudisha asyncio.SelectorEventLoop(selectors.PollSelector())

    # Should always exist.
    kundi SelectEventLoopTests(UnixEventLoopTestsMixin,
                               SubprocessTestsMixin,
                               test_utils.TestCase):

        eleza create_event_loop(self):
            rudisha asyncio.SelectorEventLoop(selectors.SelectSelector())


eleza noop(*args, **kwargs):
    pita


kundi HandleTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = mock.Mock()
        self.loop.get_debug.return_value = Kweli

    eleza test_handle(self):
        eleza callback(*args):
            rudisha args

        args = ()
        h = asyncio.Handle(callback, args, self.loop)
        self.assertIs(h._callback, callback)
        self.assertIs(h._args, args)
        self.assertUongo(h.cancelled())

        h.cancel()
        self.assertKweli(h.cancelled())

    eleza test_callback_with_exception(self):
        eleza callback():
            ashiria ValueError()

        self.loop = mock.Mock()
        self.loop.call_exception_handler = mock.Mock()

        h = asyncio.Handle(callback, (), self.loop)
        h._run()

        self.loop.call_exception_handler.assert_called_with({
            'message': test_utils.MockPattern('Exception kwenye callback.*'),
            'exception': mock.ANY,
            'handle': h,
            'source_traceback': h._source_traceback,
        })

    eleza test_handle_weakref(self):
        wd = weakref.WeakValueDictionary()
        h = asyncio.Handle(lambda: Tupu, (), self.loop)
        wd['h'] = h  # Would fail without __weakref__ slot.

    eleza test_handle_repr(self):
        self.loop.get_debug.return_value = Uongo

        # simple function
        h = asyncio.Handle(noop, (1, 2), self.loop)
        filename, lineno = test_utils.get_function_source(noop)
        self.assertEqual(repr(h),
                        '<Handle noop(1, 2) at %s:%s>'
                        % (filename, lineno))

        # cancelled handle
        h.cancel()
        self.assertEqual(repr(h),
                        '<Handle cancelled>')

        # decorated function
        ukijumuisha self.assertWarns(DeprecationWarning):
            cb = asyncio.coroutine(noop)
        h = asyncio.Handle(cb, (), self.loop)
        self.assertEqual(repr(h),
                        '<Handle noop() at %s:%s>'
                        % (filename, lineno))

        # partial function
        cb = functools.partial(noop, 1, 2)
        h = asyncio.Handle(cb, (3,), self.loop)
        regex = (r'^<Handle noop\(1, 2\)\(3\) at %s:%s>$'
                 % (re.escape(filename), lineno))
        self.assertRegex(repr(h), regex)

        # partial function ukijumuisha keyword args
        cb = functools.partial(noop, x=1)
        h = asyncio.Handle(cb, (2, 3), self.loop)
        regex = (r'^<Handle noop\(x=1\)\(2, 3\) at %s:%s>$'
                 % (re.escape(filename), lineno))
        self.assertRegex(repr(h), regex)

        # partial method
        ikiwa sys.version_info >= (3, 4):
            method = HandleTests.test_handle_repr
            cb = functools.partialmethod(method)
            filename, lineno = test_utils.get_function_source(method)
            h = asyncio.Handle(cb, (), self.loop)

            cb_regex = r'<function HandleTests.test_handle_repr .*>'
            cb_regex = (r'functools.partialmethod\(%s, , \)\(\)' % cb_regex)
            regex = (r'^<Handle %s at %s:%s>$'
                     % (cb_regex, re.escape(filename), lineno))
            self.assertRegex(repr(h), regex)

    eleza test_handle_repr_debug(self):
        self.loop.get_debug.return_value = Kweli

        # simple function
        create_filename = __file__
        create_lineno = sys._getframe().f_lineno + 1
        h = asyncio.Handle(noop, (1, 2), self.loop)
        filename, lineno = test_utils.get_function_source(noop)
        self.assertEqual(repr(h),
                        '<Handle noop(1, 2) at %s:%s created at %s:%s>'
                        % (filename, lineno, create_filename, create_lineno))

        # cancelled handle
        h.cancel()
        self.assertEqual(
            repr(h),
            '<Handle cancelled noop(1, 2) at %s:%s created at %s:%s>'
            % (filename, lineno, create_filename, create_lineno))

        # double cancellation won't overwrite _repr
        h.cancel()
        self.assertEqual(
            repr(h),
            '<Handle cancelled noop(1, 2) at %s:%s created at %s:%s>'
            % (filename, lineno, create_filename, create_lineno))

    eleza test_handle_source_traceback(self):
        loop = asyncio.get_event_loop_policy().new_event_loop()
        loop.set_debug(Kweli)
        self.set_event_loop(loop)

        eleza check_source_traceback(h):
            lineno = sys._getframe(1).f_lineno - 1
            self.assertIsInstance(h._source_traceback, list)
            self.assertEqual(h._source_traceback[-1][:3],
                             (__file__,
                              lineno,
                              'test_handle_source_traceback'))

        # call_soon
        h = loop.call_soon(noop)
        check_source_traceback(h)

        # call_soon_threadsafe
        h = loop.call_soon_threadsafe(noop)
        check_source_traceback(h)

        # call_later
        h = loop.call_later(0, noop)
        check_source_traceback(h)

        # call_at
        h = loop.call_later(0, noop)
        check_source_traceback(h)

    @unittest.skipUnless(hasattr(collections.abc, 'Coroutine'),
                         'No collections.abc.Coroutine')
    eleza test_coroutine_like_object_debug_formatting(self):
        # Test that asyncio can format coroutines that are instances of
        # collections.abc.Coroutine, but lack cr_core ama gi_code attributes
        # (such kama ones compiled ukijumuisha Cython).

        coro = CoroLike()
        coro.__name__ = 'AAA'
        self.assertKweli(asyncio.iscoroutine(coro))
        self.assertEqual(coroutines._format_coroutine(coro), 'AAA()')

        coro.__qualname__ = 'BBB'
        self.assertEqual(coroutines._format_coroutine(coro), 'BBB()')

        coro.cr_running = Kweli
        self.assertEqual(coroutines._format_coroutine(coro), 'BBB() running')

        coro.__name__ = coro.__qualname__ = Tupu
        self.assertEqual(coroutines._format_coroutine(coro),
                         '<CoroLike without __name__>() running')

        coro = CoroLike()
        coro.__qualname__ = 'CoroLike'
        # Some coroutines might sio have '__name__', such as
        # built-in async_gen.asend().
        self.assertEqual(coroutines._format_coroutine(coro), 'CoroLike()')

        coro = CoroLike()
        coro.__qualname__ = 'AAA'
        coro.cr_code = Tupu
        self.assertEqual(coroutines._format_coroutine(coro), 'AAA()')


kundi TimerTests(unittest.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = mock.Mock()

    eleza test_hash(self):
        when = time.monotonic()
        h = asyncio.TimerHandle(when, lambda: Uongo, (),
                                mock.Mock())
        self.assertEqual(hash(h), hash(when))

    eleza test_when(self):
        when = time.monotonic()
        h = asyncio.TimerHandle(when, lambda: Uongo, (),
                                mock.Mock())
        self.assertEqual(when, h.when())

    eleza test_timer(self):
        eleza callback(*args):
            rudisha args

        args = (1, 2, 3)
        when = time.monotonic()
        h = asyncio.TimerHandle(when, callback, args, mock.Mock())
        self.assertIs(h._callback, callback)
        self.assertIs(h._args, args)
        self.assertUongo(h.cancelled())

        # cancel
        h.cancel()
        self.assertKweli(h.cancelled())
        self.assertIsTupu(h._callback)
        self.assertIsTupu(h._args)

        # when cansio be Tupu
        self.assertRaises(AssertionError,
                          asyncio.TimerHandle, Tupu, callback, args,
                          self.loop)

    eleza test_timer_repr(self):
        self.loop.get_debug.return_value = Uongo

        # simple function
        h = asyncio.TimerHandle(123, noop, (), self.loop)
        src = test_utils.get_function_source(noop)
        self.assertEqual(repr(h),
                        '<TimerHandle when=123 noop() at %s:%s>' % src)

        # cancelled handle
        h.cancel()
        self.assertEqual(repr(h),
                        '<TimerHandle cancelled when=123>')

    eleza test_timer_repr_debug(self):
        self.loop.get_debug.return_value = Kweli

        # simple function
        create_filename = __file__
        create_lineno = sys._getframe().f_lineno + 1
        h = asyncio.TimerHandle(123, noop, (), self.loop)
        filename, lineno = test_utils.get_function_source(noop)
        self.assertEqual(repr(h),
                        '<TimerHandle when=123 noop() '
                        'at %s:%s created at %s:%s>'
                        % (filename, lineno, create_filename, create_lineno))

        # cancelled handle
        h.cancel()
        self.assertEqual(repr(h),
                        '<TimerHandle cancelled when=123 noop() '
                        'at %s:%s created at %s:%s>'
                        % (filename, lineno, create_filename, create_lineno))


    eleza test_timer_comparison(self):
        eleza callback(*args):
            rudisha args

        when = time.monotonic()

        h1 = asyncio.TimerHandle(when, callback, (), self.loop)
        h2 = asyncio.TimerHandle(when, callback, (), self.loop)
        # TODO: Use assertLess etc.
        self.assertUongo(h1 < h2)
        self.assertUongo(h2 < h1)
        self.assertKweli(h1 <= h2)
        self.assertKweli(h2 <= h1)
        self.assertUongo(h1 > h2)
        self.assertUongo(h2 > h1)
        self.assertKweli(h1 >= h2)
        self.assertKweli(h2 >= h1)
        self.assertKweli(h1 == h2)
        self.assertUongo(h1 != h2)

        h2.cancel()
        self.assertUongo(h1 == h2)

        h1 = asyncio.TimerHandle(when, callback, (), self.loop)
        h2 = asyncio.TimerHandle(when + 10.0, callback, (), self.loop)
        self.assertKweli(h1 < h2)
        self.assertUongo(h2 < h1)
        self.assertKweli(h1 <= h2)
        self.assertUongo(h2 <= h1)
        self.assertUongo(h1 > h2)
        self.assertKweli(h2 > h1)
        self.assertUongo(h1 >= h2)
        self.assertKweli(h2 >= h1)
        self.assertUongo(h1 == h2)
        self.assertKweli(h1 != h2)

        h3 = asyncio.Handle(callback, (), self.loop)
        self.assertIs(NotImplemented, h1.__eq__(h3))
        self.assertIs(NotImplemented, h1.__ne__(h3))


kundi AbstractEventLoopTests(unittest.TestCase):

    eleza test_not_implemented(self):
        f = mock.Mock()
        loop = asyncio.AbstractEventLoop()
        self.assertRaises(
            NotImplementedError, loop.run_forever)
        self.assertRaises(
            NotImplementedError, loop.run_until_complete, Tupu)
        self.assertRaises(
            NotImplementedError, loop.stop)
        self.assertRaises(
            NotImplementedError, loop.is_running)
        self.assertRaises(
            NotImplementedError, loop.is_closed)
        self.assertRaises(
            NotImplementedError, loop.close)
        self.assertRaises(
            NotImplementedError, loop.create_task, Tupu)
        self.assertRaises(
            NotImplementedError, loop.call_later, Tupu, Tupu)
        self.assertRaises(
            NotImplementedError, loop.call_at, f, f)
        self.assertRaises(
            NotImplementedError, loop.call_soon, Tupu)
        self.assertRaises(
            NotImplementedError, loop.time)
        self.assertRaises(
            NotImplementedError, loop.call_soon_threadsafe, Tupu)
        self.assertRaises(
            NotImplementedError, loop.set_default_executor, f)
        self.assertRaises(
            NotImplementedError, loop.add_reader, 1, f)
        self.assertRaises(
            NotImplementedError, loop.remove_reader, 1)
        self.assertRaises(
            NotImplementedError, loop.add_writer, 1, f)
        self.assertRaises(
            NotImplementedError, loop.remove_writer, 1)
        self.assertRaises(
            NotImplementedError, loop.add_signal_handler, 1, f)
        self.assertRaises(
            NotImplementedError, loop.remove_signal_handler, 1)
        self.assertRaises(
            NotImplementedError, loop.remove_signal_handler, 1)
        self.assertRaises(
            NotImplementedError, loop.set_exception_handler, f)
        self.assertRaises(
            NotImplementedError, loop.default_exception_handler, f)
        self.assertRaises(
            NotImplementedError, loop.call_exception_handler, f)
        self.assertRaises(
            NotImplementedError, loop.get_debug)
        self.assertRaises(
            NotImplementedError, loop.set_debug, f)

    eleza test_not_implemented_async(self):

        async eleza inner():
            f = mock.Mock()
            loop = asyncio.AbstractEventLoop()

            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.run_in_executor(f, f)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.getaddrinfo('localhost', 8080)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.getnameinfo(('localhost', 8080))
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.create_connection(f)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.create_server(f)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.create_datagram_endpoint(f)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.sock_recv(f, 10)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.sock_recv_into(f, 10)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.sock_sendall(f, 10)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.sock_connect(f, f)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.sock_accept(f)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.sock_sendfile(f, f)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.sendfile(f, f)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.connect_read_pipe(f, mock.sentinel.pipe)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.connect_write_pipe(f, mock.sentinel.pipe)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.subprocess_shell(f, mock.sentinel)
            ukijumuisha self.assertRaises(NotImplementedError):
                await loop.subprocess_exec(f)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(inner())
        loop.close()


kundi PolicyTests(unittest.TestCase):

    eleza test_event_loop_policy(self):
        policy = asyncio.AbstractEventLoopPolicy()
        self.assertRaises(NotImplementedError, policy.get_event_loop)
        self.assertRaises(NotImplementedError, policy.set_event_loop, object())
        self.assertRaises(NotImplementedError, policy.new_event_loop)
        self.assertRaises(NotImplementedError, policy.get_child_watcher)
        self.assertRaises(NotImplementedError, policy.set_child_watcher,
                          object())

    eleza test_get_event_loop(self):
        policy = asyncio.DefaultEventLoopPolicy()
        self.assertIsTupu(policy._local._loop)

        loop = policy.get_event_loop()
        self.assertIsInstance(loop, asyncio.AbstractEventLoop)

        self.assertIs(policy._local._loop, loop)
        self.assertIs(loop, policy.get_event_loop())
        loop.close()

    eleza test_get_event_loop_calls_set_event_loop(self):
        policy = asyncio.DefaultEventLoopPolicy()

        ukijumuisha mock.patch.object(
                policy, "set_event_loop",
                wraps=policy.set_event_loop) kama m_set_event_loop:

            loop = policy.get_event_loop()

            # policy._local._loop must be set through .set_event_loop()
            # (the unix DefaultEventLoopPolicy needs this call to attach
            # the child watcher correctly)
            m_set_event_loop.assert_called_with(loop)

        loop.close()

    eleza test_get_event_loop_after_set_none(self):
        policy = asyncio.DefaultEventLoopPolicy()
        policy.set_event_loop(Tupu)
        self.assertRaises(RuntimeError, policy.get_event_loop)

    @mock.patch('asyncio.events.threading.current_thread')
    eleza test_get_event_loop_thread(self, m_current_thread):

        eleza f():
            policy = asyncio.DefaultEventLoopPolicy()
            self.assertRaises(RuntimeError, policy.get_event_loop)

        th = threading.Thread(target=f)
        th.start()
        th.join()

    eleza test_new_event_loop(self):
        policy = asyncio.DefaultEventLoopPolicy()

        loop = policy.new_event_loop()
        self.assertIsInstance(loop, asyncio.AbstractEventLoop)
        loop.close()

    eleza test_set_event_loop(self):
        policy = asyncio.DefaultEventLoopPolicy()
        old_loop = policy.get_event_loop()

        self.assertRaises(AssertionError, policy.set_event_loop, object())

        loop = policy.new_event_loop()
        policy.set_event_loop(loop)
        self.assertIs(loop, policy.get_event_loop())
        self.assertIsNot(old_loop, policy.get_event_loop())
        loop.close()
        old_loop.close()

    eleza test_get_event_loop_policy(self):
        policy = asyncio.get_event_loop_policy()
        self.assertIsInstance(policy, asyncio.AbstractEventLoopPolicy)
        self.assertIs(policy, asyncio.get_event_loop_policy())

    eleza test_set_event_loop_policy(self):
        self.assertRaises(
            AssertionError, asyncio.set_event_loop_policy, object())

        old_policy = asyncio.get_event_loop_policy()

        policy = asyncio.DefaultEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        self.assertIs(policy, asyncio.get_event_loop_policy())
        self.assertIsNot(policy, old_policy)


kundi GetEventLoopTestsMixin:

    _get_running_loop_impl = Tupu
    _set_running_loop_impl = Tupu
    get_running_loop_impl = Tupu
    get_event_loop_impl = Tupu

    eleza setUp(self):
        self._get_running_loop_saved = events._get_running_loop
        self._set_running_loop_saved = events._set_running_loop
        self.get_running_loop_saved = events.get_running_loop
        self.get_event_loop_saved = events.get_event_loop

        events._get_running_loop = type(self)._get_running_loop_impl
        events._set_running_loop = type(self)._set_running_loop_impl
        events.get_running_loop = type(self).get_running_loop_impl
        events.get_event_loop = type(self).get_event_loop_impl

        asyncio._get_running_loop = type(self)._get_running_loop_impl
        asyncio._set_running_loop = type(self)._set_running_loop_impl
        asyncio.get_running_loop = type(self).get_running_loop_impl
        asyncio.get_event_loop = type(self).get_event_loop_impl

        super().setUp()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        ikiwa sys.platform != 'win32':
            watcher = asyncio.SafeChildWatcher()
            watcher.attach_loop(self.loop)
            asyncio.set_child_watcher(watcher)

    eleza tearDown(self):
        jaribu:
            ikiwa sys.platform != 'win32':
                asyncio.set_child_watcher(Tupu)

            super().tearDown()
        mwishowe:
            self.loop.close()
            asyncio.set_event_loop(Tupu)

            events._get_running_loop = self._get_running_loop_saved
            events._set_running_loop = self._set_running_loop_saved
            events.get_running_loop = self.get_running_loop_saved
            events.get_event_loop = self.get_event_loop_saved

            asyncio._get_running_loop = self._get_running_loop_saved
            asyncio._set_running_loop = self._set_running_loop_saved
            asyncio.get_running_loop = self.get_running_loop_saved
            asyncio.get_event_loop = self.get_event_loop_saved

    ikiwa sys.platform != 'win32':

        eleza test_get_event_loop_new_process(self):
            # Issue bpo-32126: The multiprocessing module used by
            # ProcessPoolExecutor ni sio functional when the
            # multiprocessing.synchronize module cansio be imported.
            support.import_module('multiprocessing.synchronize')

            async eleza main():
                pool = concurrent.futures.ProcessPoolExecutor()
                result = await self.loop.run_in_executor(
                    pool, _test_get_event_loop_new_process__sub_proc)
                pool.shutdown()
                rudisha result

            self.assertEqual(
                self.loop.run_until_complete(main()),
                'hello')

    eleza test_get_event_loop_returns_running_loop(self):
        kundi TestError(Exception):
            pita

        kundi Policy(asyncio.DefaultEventLoopPolicy):
            eleza get_event_loop(self):
                ashiria TestError

        old_policy = asyncio.get_event_loop_policy()
        jaribu:
            asyncio.set_event_loop_policy(Policy())
            loop = asyncio.new_event_loop()

            ukijumuisha self.assertRaises(TestError):
                asyncio.get_event_loop()
            asyncio.set_event_loop(Tupu)
            ukijumuisha self.assertRaises(TestError):
                asyncio.get_event_loop()

            ukijumuisha self.assertRaisesRegex(RuntimeError, 'no running'):
                self.assertIs(asyncio.get_running_loop(), Tupu)
            self.assertIs(asyncio._get_running_loop(), Tupu)

            async eleza func():
                self.assertIs(asyncio.get_event_loop(), loop)
                self.assertIs(asyncio.get_running_loop(), loop)
                self.assertIs(asyncio._get_running_loop(), loop)

            loop.run_until_complete(func())

            asyncio.set_event_loop(loop)
            ukijumuisha self.assertRaises(TestError):
                asyncio.get_event_loop()

            asyncio.set_event_loop(Tupu)
            ukijumuisha self.assertRaises(TestError):
                asyncio.get_event_loop()

        mwishowe:
            asyncio.set_event_loop_policy(old_policy)
            ikiwa loop ni sio Tupu:
                loop.close()

        ukijumuisha self.assertRaisesRegex(RuntimeError, 'no running'):
            self.assertIs(asyncio.get_running_loop(), Tupu)

        self.assertIs(asyncio._get_running_loop(), Tupu)


kundi TestPyGetEventLoop(GetEventLoopTestsMixin, unittest.TestCase):

    _get_running_loop_impl = events._py__get_running_loop
    _set_running_loop_impl = events._py__set_running_loop
    get_running_loop_impl = events._py_get_running_loop
    get_event_loop_impl = events._py_get_event_loop


jaribu:
    agiza _asyncio  # NoQA
tatizo ImportError:
    pita
isipokua:

    kundi TestCGetEventLoop(GetEventLoopTestsMixin, unittest.TestCase):

        _get_running_loop_impl = events._c__get_running_loop
        _set_running_loop_impl = events._c__set_running_loop
        get_running_loop_impl = events._c_get_running_loop
        get_event_loop_impl = events._c_get_event_loop


kundi TestServer(unittest.TestCase):

    eleza test_get_loop(self):
        loop = asyncio.new_event_loop()
        self.addCleanup(loop.close)
        proto = MyProto(loop)
        server = loop.run_until_complete(loop.create_server(lambda: proto, '0.0.0.0', 0))
        self.assertEqual(server.get_loop(), loop)
        server.close()
        loop.run_until_complete(server.wait_closed())


kundi TestAbstractServer(unittest.TestCase):

    eleza test_close(self):
        ukijumuisha self.assertRaises(NotImplementedError):
            events.AbstractServer().close()

    eleza test_wait_closed(self):
        loop = asyncio.new_event_loop()
        self.addCleanup(loop.close)

        ukijumuisha self.assertRaises(NotImplementedError):
            loop.run_until_complete(events.AbstractServer().wait_closed())

    eleza test_get_loop(self):
        ukijumuisha self.assertRaises(NotImplementedError):
            events.AbstractServer().get_loop()


ikiwa __name__ == '__main__':
    unittest.main()
