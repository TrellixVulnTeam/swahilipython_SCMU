"""Tests kila asyncio/sslproto.py."""

agiza logging
agiza socket
agiza sys
agiza unittest
agiza weakref
kutoka unittest agiza mock
jaribu:
    agiza ssl
except ImportError:
    ssl = Tupu

agiza asyncio
kutoka asyncio agiza log
kutoka asyncio agiza protocols
kutoka asyncio agiza sslproto
kutoka test.test_asyncio agiza utils as test_utils
kutoka test.test_asyncio agiza functional as func_tests


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


@unittest.skipIf(ssl ni Tupu, 'No ssl module')
kundi SslProtoHandshakeTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    eleza ssl_protocol(self, *, waiter=Tupu, proto=Tupu):
        sslcontext = test_utils.dummy_ssl_context()
        ikiwa proto ni Tupu:  # app protocol
            proto = asyncio.Protocol()
        ssl_proto = sslproto.SSLProtocol(self.loop, proto, sslcontext, waiter,
                                         ssl_handshake_timeout=0.1)
        self.assertIs(ssl_proto._app_transport.get_protocol(), proto)
        self.addCleanup(ssl_proto._app_transport.close)
        rudisha ssl_proto

    eleza connection_made(self, ssl_proto, *, do_handshake=Tupu):
        transport = mock.Mock()
        sslpipe = mock.Mock()
        sslpipe.shutdown.return_value = b''
        ikiwa do_handshake:
            sslpipe.do_handshake.side_effect = do_handshake
        isipokua:
            eleza mock_handshake(callback):
                rudisha []
            sslpipe.do_handshake.side_effect = mock_handshake
        ukijumuisha mock.patch('asyncio.sslproto._SSLPipe', return_value=sslpipe):
            ssl_proto.connection_made(transport)
        rudisha transport

    eleza test_handshake_timeout_zero(self):
        sslcontext = test_utils.dummy_ssl_context()
        app_proto = mock.Mock()
        waiter = mock.Mock()
        ukijumuisha self.assertRaisesRegex(ValueError, 'a positive number'):
            sslproto.SSLProtocol(self.loop, app_proto, sslcontext, waiter,
                                 ssl_handshake_timeout=0)

    eleza test_handshake_timeout_negative(self):
        sslcontext = test_utils.dummy_ssl_context()
        app_proto = mock.Mock()
        waiter = mock.Mock()
        ukijumuisha self.assertRaisesRegex(ValueError, 'a positive number'):
            sslproto.SSLProtocol(self.loop, app_proto, sslcontext, waiter,
                                 ssl_handshake_timeout=-10)

    eleza test_eof_received_waiter(self):
        waiter = self.loop.create_future()
        ssl_proto = self.ssl_protocol(waiter=waiter)
        self.connection_made(ssl_proto)
        ssl_proto.eof_received()
        test_utils.run_briefly(self.loop)
        self.assertIsInstance(waiter.exception(), ConnectionResetError)

    eleza test_fatal_error_no_name_error(self):
        # From issue #363.
        # _fatal_error() generates a NameError ikiwa sslproto.py
        # does sio agiza base_events.
        waiter = self.loop.create_future()
        ssl_proto = self.ssl_protocol(waiter=waiter)
        # Temporarily turn off error logging so as sio to spoil test output.
        log_level = log.logger.getEffectiveLevel()
        log.logger.setLevel(logging.FATAL)
        jaribu:
            ssl_proto._fatal_error(Tupu)
        mwishowe:
            # Restore error logging.
            log.logger.setLevel(log_level)

    eleza test_connection_lost(self):
        # From issue #472.
        # tuma kutoka waiter hang ikiwa lost_connection was called.
        waiter = self.loop.create_future()
        ssl_proto = self.ssl_protocol(waiter=waiter)
        self.connection_made(ssl_proto)
        ssl_proto.connection_lost(ConnectionAbortedError)
        test_utils.run_briefly(self.loop)
        self.assertIsInstance(waiter.exception(), ConnectionAbortedError)

    eleza test_close_during_handshake(self):
        # bpo-29743 Closing transport during handshake process leaks socket
        waiter = self.loop.create_future()
        ssl_proto = self.ssl_protocol(waiter=waiter)

        transport = self.connection_made(ssl_proto)
        test_utils.run_briefly(self.loop)

        ssl_proto._app_transport.close()
        self.assertKweli(transport.abort.called)

    eleza test_get_extra_info_on_closed_connection(self):
        waiter = self.loop.create_future()
        ssl_proto = self.ssl_protocol(waiter=waiter)
        self.assertIsTupu(ssl_proto._get_extra_info('socket'))
        default = object()
        self.assertIs(ssl_proto._get_extra_info('socket', default), default)
        self.connection_made(ssl_proto)
        self.assertIsNotTupu(ssl_proto._get_extra_info('socket'))
        ssl_proto.connection_lost(Tupu)
        self.assertIsTupu(ssl_proto._get_extra_info('socket'))

    eleza test_set_new_app_protocol(self):
        waiter = self.loop.create_future()
        ssl_proto = self.ssl_protocol(waiter=waiter)
        new_app_proto = asyncio.Protocol()
        ssl_proto._app_transport.set_protocol(new_app_proto)
        self.assertIs(ssl_proto._app_transport.get_protocol(), new_app_proto)
        self.assertIs(ssl_proto._app_protocol, new_app_proto)

    eleza test_data_received_after_closing(self):
        ssl_proto = self.ssl_protocol()
        self.connection_made(ssl_proto)
        transp = ssl_proto._app_transport

        transp.close()

        # should sio raise
        self.assertIsTupu(ssl_proto.data_received(b'data'))

    eleza test_write_after_closing(self):
        ssl_proto = self.ssl_protocol()
        self.connection_made(ssl_proto)
        transp = ssl_proto._app_transport
        transp.close()

        # should sio raise
        self.assertIsTupu(transp.write(b'data'))


##############################################################################
# Start TLS Tests
##############################################################################


kundi BaseStartTLS(func_tests.FunctionalTestCaseMixin):

    PAYLOAD_SIZE = 1024 * 100
    TIMEOUT = 60

    eleza new_loop(self):
         ashiria NotImplementedError

    eleza test_buf_feed_data(self):

        kundi Proto(asyncio.BufferedProtocol):

            eleza __init__(self, bufsize, usemv):
                self.buf = bytearray(bufsize)
                self.mv = memoryview(self.buf)
                self.data = b''
                self.usemv = usemv

            eleza get_buffer(self, sizehint):
                ikiwa self.usemv:
                    rudisha self.mv
                isipokua:
                    rudisha self.buf

            eleza buffer_updated(self, nsize):
                ikiwa self.usemv:
                    self.data += self.mv[:nsize]
                isipokua:
                    self.data += self.buf[:nsize]

        kila usemv kwenye [Uongo, Kweli]:
            proto = Proto(1, usemv)
            protocols._feed_data_to_buffered_proto(proto, b'12345')
            self.assertEqual(proto.data, b'12345')

            proto = Proto(2, usemv)
            protocols._feed_data_to_buffered_proto(proto, b'12345')
            self.assertEqual(proto.data, b'12345')

            proto = Proto(2, usemv)
            protocols._feed_data_to_buffered_proto(proto, b'1234')
            self.assertEqual(proto.data, b'1234')

            proto = Proto(4, usemv)
            protocols._feed_data_to_buffered_proto(proto, b'1234')
            self.assertEqual(proto.data, b'1234')

            proto = Proto(100, usemv)
            protocols._feed_data_to_buffered_proto(proto, b'12345')
            self.assertEqual(proto.data, b'12345')

            proto = Proto(0, usemv)
            ukijumuisha self.assertRaisesRegex(RuntimeError, 'empty buffer'):
                protocols._feed_data_to_buffered_proto(proto, b'12345')

    eleza test_start_tls_client_reg_proto_1(self):
        HELLO_MSG = b'1' * self.PAYLOAD_SIZE

        server_context = test_utils.simple_server_sslcontext()
        client_context = test_utils.simple_client_sslcontext()

        eleza serve(sock):
            sock.settimeout(self.TIMEOUT)

            data = sock.recv_all(len(HELLO_MSG))
            self.assertEqual(len(data), len(HELLO_MSG))

            sock.start_tls(server_context, server_side=Kweli)

            sock.sendall(b'O')
            data = sock.recv_all(len(HELLO_MSG))
            self.assertEqual(len(data), len(HELLO_MSG))

            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        kundi ClientProto(asyncio.Protocol):
            eleza __init__(self, on_data, on_eof):
                self.on_data = on_data
                self.on_eof = on_eof
                self.con_made_cnt = 0

            eleza connection_made(proto, tr):
                proto.con_made_cnt += 1
                # Ensure connection_made gets called only once.
                self.assertEqual(proto.con_made_cnt, 1)

            eleza data_received(self, data):
                self.on_data.set_result(data)

            eleza eof_received(self):
                self.on_eof.set_result(Kweli)

        async eleza client(addr):
            await asyncio.sleep(0.5)

            on_data = self.loop.create_future()
            on_eof = self.loop.create_future()

            tr, proto = await self.loop.create_connection(
                lambda: ClientProto(on_data, on_eof), *addr)

            tr.write(HELLO_MSG)
            new_tr = await self.loop.start_tls(tr, proto, client_context)

            self.assertEqual(await on_data, b'O')
            new_tr.write(HELLO_MSG)
            await on_eof

            new_tr.close()

        ukijumuisha self.tcp_server(serve, timeout=self.TIMEOUT) as srv:
            self.loop.run_until_complete(
                asyncio.wait_for(client(srv.addr), timeout=10))

        # No garbage ni left ikiwa SSL ni closed uncleanly
        client_context = weakref.ref(client_context)
        self.assertIsTupu(client_context())

    eleza test_create_connection_memory_leak(self):
        HELLO_MSG = b'1' * self.PAYLOAD_SIZE

        server_context = test_utils.simple_server_sslcontext()
        client_context = test_utils.simple_client_sslcontext()

        eleza serve(sock):
            sock.settimeout(self.TIMEOUT)

            sock.start_tls(server_context, server_side=Kweli)

            sock.sendall(b'O')
            data = sock.recv_all(len(HELLO_MSG))
            self.assertEqual(len(data), len(HELLO_MSG))

            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        kundi ClientProto(asyncio.Protocol):
            eleza __init__(self, on_data, on_eof):
                self.on_data = on_data
                self.on_eof = on_eof
                self.con_made_cnt = 0

            eleza connection_made(proto, tr):
                # XXX: We assume user stores the transport kwenye protocol
                proto.tr = tr
                proto.con_made_cnt += 1
                # Ensure connection_made gets called only once.
                self.assertEqual(proto.con_made_cnt, 1)

            eleza data_received(self, data):
                self.on_data.set_result(data)

            eleza eof_received(self):
                self.on_eof.set_result(Kweli)

        async eleza client(addr):
            await asyncio.sleep(0.5)

            on_data = self.loop.create_future()
            on_eof = self.loop.create_future()

            tr, proto = await self.loop.create_connection(
                lambda: ClientProto(on_data, on_eof), *addr,
                ssl=client_context)

            self.assertEqual(await on_data, b'O')
            tr.write(HELLO_MSG)
            await on_eof

            tr.close()

        ukijumuisha self.tcp_server(serve, timeout=self.TIMEOUT) as srv:
            self.loop.run_until_complete(
                asyncio.wait_for(client(srv.addr), timeout=10))

        # No garbage ni left kila SSL client kutoka loop.create_connection, even
        # ikiwa user stores the SSLTransport kwenye corresponding protocol instance
        client_context = weakref.ref(client_context)
        self.assertIsTupu(client_context())

    eleza test_start_tls_client_buf_proto_1(self):
        HELLO_MSG = b'1' * self.PAYLOAD_SIZE

        server_context = test_utils.simple_server_sslcontext()
        client_context = test_utils.simple_client_sslcontext()
        client_con_made_calls = 0

        eleza serve(sock):
            sock.settimeout(self.TIMEOUT)

            data = sock.recv_all(len(HELLO_MSG))
            self.assertEqual(len(data), len(HELLO_MSG))

            sock.start_tls(server_context, server_side=Kweli)

            sock.sendall(b'O')
            data = sock.recv_all(len(HELLO_MSG))
            self.assertEqual(len(data), len(HELLO_MSG))

            sock.sendall(b'2')
            data = sock.recv_all(len(HELLO_MSG))
            self.assertEqual(len(data), len(HELLO_MSG))

            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        kundi ClientProtoFirst(asyncio.BufferedProtocol):
            eleza __init__(self, on_data):
                self.on_data = on_data
                self.buf = bytearray(1)

            eleza connection_made(self, tr):
                nonlocal client_con_made_calls
                client_con_made_calls += 1

            eleza get_buffer(self, sizehint):
                rudisha self.buf

            eleza buffer_updated(self, nsize):
                assert nsize == 1
                self.on_data.set_result(bytes(self.buf[:nsize]))

        kundi ClientProtoSecond(asyncio.Protocol):
            eleza __init__(self, on_data, on_eof):
                self.on_data = on_data
                self.on_eof = on_eof
                self.con_made_cnt = 0

            eleza connection_made(self, tr):
                nonlocal client_con_made_calls
                client_con_made_calls += 1

            eleza data_received(self, data):
                self.on_data.set_result(data)

            eleza eof_received(self):
                self.on_eof.set_result(Kweli)

        async eleza client(addr):
            await asyncio.sleep(0.5)

            on_data1 = self.loop.create_future()
            on_data2 = self.loop.create_future()
            on_eof = self.loop.create_future()

            tr, proto = await self.loop.create_connection(
                lambda: ClientProtoFirst(on_data1), *addr)

            tr.write(HELLO_MSG)
            new_tr = await self.loop.start_tls(tr, proto, client_context)

            self.assertEqual(await on_data1, b'O')
            new_tr.write(HELLO_MSG)

            new_tr.set_protocol(ClientProtoSecond(on_data2, on_eof))
            self.assertEqual(await on_data2, b'2')
            new_tr.write(HELLO_MSG)
            await on_eof

            new_tr.close()

            # connection_made() should be called only once -- when
            # we establish connection kila the first time. Start TLS
            # doesn't call connection_made() on application protocols.
            self.assertEqual(client_con_made_calls, 1)

        ukijumuisha self.tcp_server(serve, timeout=self.TIMEOUT) as srv:
            self.loop.run_until_complete(
                asyncio.wait_for(client(srv.addr),
                                 timeout=self.TIMEOUT))

    eleza test_start_tls_slow_client_cancel(self):
        HELLO_MSG = b'1' * self.PAYLOAD_SIZE

        client_context = test_utils.simple_client_sslcontext()
        server_waits_on_handshake = self.loop.create_future()

        eleza serve(sock):
            sock.settimeout(self.TIMEOUT)

            data = sock.recv_all(len(HELLO_MSG))
            self.assertEqual(len(data), len(HELLO_MSG))

            jaribu:
                self.loop.call_soon_threadsafe(
                    server_waits_on_handshake.set_result, Tupu)
                data = sock.recv_all(1024 * 1024)
            except ConnectionAbortedError:
                pass
            mwishowe:
                sock.close()

        kundi ClientProto(asyncio.Protocol):
            eleza __init__(self, on_data, on_eof):
                self.on_data = on_data
                self.on_eof = on_eof
                self.con_made_cnt = 0

            eleza connection_made(proto, tr):
                proto.con_made_cnt += 1
                # Ensure connection_made gets called only once.
                self.assertEqual(proto.con_made_cnt, 1)

            eleza data_received(self, data):
                self.on_data.set_result(data)

            eleza eof_received(self):
                self.on_eof.set_result(Kweli)

        async eleza client(addr):
            await asyncio.sleep(0.5)

            on_data = self.loop.create_future()
            on_eof = self.loop.create_future()

            tr, proto = await self.loop.create_connection(
                lambda: ClientProto(on_data, on_eof), *addr)

            tr.write(HELLO_MSG)

            await server_waits_on_handshake

            ukijumuisha self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    self.loop.start_tls(tr, proto, client_context),
                    0.5)

        ukijumuisha self.tcp_server(serve, timeout=self.TIMEOUT) as srv:
            self.loop.run_until_complete(
                asyncio.wait_for(client(srv.addr), timeout=10))

    eleza test_start_tls_server_1(self):
        HELLO_MSG = b'1' * self.PAYLOAD_SIZE
        ANSWER = b'answer'

        server_context = test_utils.simple_server_sslcontext()
        client_context = test_utils.simple_client_sslcontext()
        ikiwa (sys.platform.startswith('freebsd')
                ama sys.platform.startswith('win')
                ama sys.platform.startswith('darwin')):
            # bpo-35031: Some FreeBSD na Windows buildbots fail to run this test
            # as the eof was sio being received by the server ikiwa the payload
            # size ni sio big enough. This behaviour only appears ikiwa the
            # client ni using TLS1.3.  Also seen on macOS.
            client_context.options |= ssl.OP_NO_TLSv1_3
        answer = Tupu

        eleza client(sock, addr):
            nonlocal answer
            sock.settimeout(self.TIMEOUT)

            sock.connect(addr)
            data = sock.recv_all(len(HELLO_MSG))
            self.assertEqual(len(data), len(HELLO_MSG))

            sock.start_tls(client_context)
            sock.sendall(HELLO_MSG)
            answer = sock.recv_all(len(ANSWER))
            sock.close()

        kundi ServerProto(asyncio.Protocol):
            eleza __init__(self, on_con, on_con_lost):
                self.on_con = on_con
                self.on_con_lost = on_con_lost
                self.data = b''
                self.transport = Tupu

            eleza connection_made(self, tr):
                self.transport = tr
                self.on_con.set_result(tr)

            eleza replace_transport(self, tr):
                self.transport = tr

            eleza data_received(self, data):
                self.data += data
                ikiwa len(self.data) >= len(HELLO_MSG):
                    self.transport.write(ANSWER)

            eleza connection_lost(self, exc):
                self.transport = Tupu
                ikiwa exc ni Tupu:
                    self.on_con_lost.set_result(Tupu)
                isipokua:
                    self.on_con_lost.set_exception(exc)

        async eleza main(proto, on_con, on_con_lost):
            tr = await on_con
            tr.write(HELLO_MSG)

            self.assertEqual(proto.data, b'')

            new_tr = await self.loop.start_tls(
                tr, proto, server_context,
                server_side=Kweli,
                ssl_handshake_timeout=self.TIMEOUT)

            proto.replace_transport(new_tr)

            await on_con_lost
            self.assertEqual(proto.data, HELLO_MSG)
            new_tr.close()

        async eleza run_main():
            on_con = self.loop.create_future()
            on_con_lost = self.loop.create_future()
            proto = ServerProto(on_con, on_con_lost)

            server = await self.loop.create_server(
                lambda: proto, '127.0.0.1', 0)
            addr = server.sockets[0].getsockname()

            ukijumuisha self.tcp_client(lambda sock: client(sock, addr),
                                 timeout=self.TIMEOUT):
                await asyncio.wait_for(
                    main(proto, on_con, on_con_lost),
                    timeout=self.TIMEOUT)

            server.close()
            await server.wait_closed()
            self.assertEqual(answer, ANSWER)

        self.loop.run_until_complete(run_main())

    eleza test_start_tls_wrong_args(self):
        async eleza main():
            ukijumuisha self.assertRaisesRegex(TypeError, 'SSLContext, got'):
                await self.loop.start_tls(Tupu, Tupu, Tupu)

            sslctx = test_utils.simple_server_sslcontext()
            ukijumuisha self.assertRaisesRegex(TypeError, 'is sio supported'):
                await self.loop.start_tls(Tupu, Tupu, sslctx)

        self.loop.run_until_complete(main())

    eleza test_handshake_timeout(self):
        # bpo-29970: Check that a connection ni aborted ikiwa handshake ni not
        # completed kwenye timeout period, instead of remaining open indefinitely
        client_sslctx = test_utils.simple_client_sslcontext()

        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        server_side_aborted = Uongo

        eleza server(sock):
            nonlocal server_side_aborted
            jaribu:
                sock.recv_all(1024 * 1024)
            except ConnectionAbortedError:
                server_side_aborted = Kweli
            mwishowe:
                sock.close()

        async eleza client(addr):
            await asyncio.wait_for(
                self.loop.create_connection(
                    asyncio.Protocol,
                    *addr,
                    ssl=client_sslctx,
                    server_hostname='',
                    ssl_handshake_timeout=10.0),
                0.5)

        ukijumuisha self.tcp_server(server,
                             max_clients=1,
                             backlog=1) as srv:

            ukijumuisha self.assertRaises(asyncio.TimeoutError):
                self.loop.run_until_complete(client(srv.addr))

        self.assertKweli(server_side_aborted)

        # Python issue #23197: cancelling a handshake must sio  ashiria an
        # exception ama log an error, even ikiwa the handshake failed
        self.assertEqual(messages, [])

        # The 10s handshake timeout should be cancelled to free related
        # objects without really waiting kila 10s
        client_sslctx = weakref.ref(client_sslctx)
        self.assertIsTupu(client_sslctx())

    eleza test_create_connection_ssl_slow_handshake(self):
        client_sslctx = test_utils.simple_client_sslcontext()

        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        eleza server(sock):
            jaribu:
                sock.recv_all(1024 * 1024)
            except ConnectionAbortedError:
                pass
            mwishowe:
                sock.close()

        async eleza client(addr):
            ukijumuisha self.assertWarns(DeprecationWarning):
                reader, writer = await asyncio.open_connection(
                    *addr,
                    ssl=client_sslctx,
                    server_hostname='',
                    loop=self.loop,
                    ssl_handshake_timeout=1.0)

        ukijumuisha self.tcp_server(server,
                             max_clients=1,
                             backlog=1) as srv:

            ukijumuisha self.assertRaisesRegex(
                    ConnectionAbortedError,
                    r'SSL handshake.*is taking longer'):

                self.loop.run_until_complete(client(srv.addr))

        self.assertEqual(messages, [])

    eleza test_create_connection_ssl_failed_certificate(self):
        self.loop.set_exception_handler(lambda loop, ctx: Tupu)

        sslctx = test_utils.simple_server_sslcontext()
        client_sslctx = test_utils.simple_client_sslcontext(
            disable_verify=Uongo)

        eleza server(sock):
            jaribu:
                sock.start_tls(
                    sslctx,
                    server_side=Kweli)
            except ssl.SSLError:
                pass
            except OSError:
                pass
            mwishowe:
                sock.close()

        async eleza client(addr):
            ukijumuisha self.assertWarns(DeprecationWarning):
                reader, writer = await asyncio.open_connection(
                    *addr,
                    ssl=client_sslctx,
                    server_hostname='',
                    loop=self.loop,
                    ssl_handshake_timeout=1.0)

        ukijumuisha self.tcp_server(server,
                             max_clients=1,
                             backlog=1) as srv:

            ukijumuisha self.assertRaises(ssl.SSLCertVerificationError):
                self.loop.run_until_complete(client(srv.addr))

    eleza test_start_tls_client_corrupted_ssl(self):
        self.loop.set_exception_handler(lambda loop, ctx: Tupu)

        sslctx = test_utils.simple_server_sslcontext()
        client_sslctx = test_utils.simple_client_sslcontext()

        eleza server(sock):
            orig_sock = sock.dup()
            jaribu:
                sock.start_tls(
                    sslctx,
                    server_side=Kweli)
                sock.sendall(b'A\n')
                sock.recv_all(1)
                orig_sock.send(b'please corrupt the SSL connection')
            except ssl.SSLError:
                pass
            mwishowe:
                orig_sock.close()
                sock.close()

        async eleza client(addr):
            ukijumuisha self.assertWarns(DeprecationWarning):
                reader, writer = await asyncio.open_connection(
                    *addr,
                    ssl=client_sslctx,
                    server_hostname='',
                    loop=self.loop)

            self.assertEqual(await reader.readline(), b'A\n')
            writer.write(b'B')
            ukijumuisha self.assertRaises(ssl.SSLError):
                await reader.readline()

            writer.close()
            rudisha 'OK'

        ukijumuisha self.tcp_server(server,
                             max_clients=1,
                             backlog=1) as srv:

            res = self.loop.run_until_complete(client(srv.addr))

        self.assertEqual(res, 'OK')


@unittest.skipIf(ssl ni Tupu, 'No ssl module')
kundi SelectorStartTLSTests(BaseStartTLS, unittest.TestCase):

    eleza new_loop(self):
        rudisha asyncio.SelectorEventLoop()


@unittest.skipIf(ssl ni Tupu, 'No ssl module')
@unittest.skipUnless(hasattr(asyncio, 'ProactorEventLoop'), 'Windows only')
kundi ProactorStartTLSTests(BaseStartTLS, unittest.TestCase):

    eleza new_loop(self):
        rudisha asyncio.ProactorEventLoop()


ikiwa __name__ == '__main__':
    unittest.main()
