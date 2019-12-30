"""Tests kila proactor_events.py"""

agiza io
agiza socket
agiza unittest
agiza sys
kutoka unittest agiza mock

agiza asyncio
kutoka asyncio.proactor_events agiza BaseProactorEventLoop
kutoka asyncio.proactor_events agiza _ProactorSocketTransport
kutoka asyncio.proactor_events agiza _ProactorWritePipeTransport
kutoka asyncio.proactor_events agiza _ProactorDuplexPipeTransport
kutoka asyncio.proactor_events agiza _ProactorDatagramTransport
kutoka test agiza support
kutoka test.test_asyncio agiza utils kama test_utils


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


eleza close_transport(transport):
    # Don't call transport.close() because the event loop na the IOCP proactor
    # are mocked
    ikiwa transport._sock ni Tupu:
        rudisha
    transport._sock.close()
    transport._sock = Tupu


kundi ProactorSocketTransportTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.addCleanup(self.loop.close)
        self.proactor = mock.Mock()
        self.loop._proactor = self.proactor
        self.protocol = test_utils.make_test_protocol(asyncio.Protocol)
        self.sock = mock.Mock(socket.socket)

    eleza socket_transport(self, waiter=Tupu):
        transport = _ProactorSocketTransport(self.loop, self.sock,
                                             self.protocol, waiter=waiter)
        self.addCleanup(close_transport, transport)
        rudisha transport

    eleza test_ctor(self):
        fut = self.loop.create_future()
        tr = self.socket_transport(waiter=fut)
        test_utils.run_briefly(self.loop)
        self.assertIsTupu(fut.result())
        self.protocol.connection_made(tr)
        self.proactor.recv.assert_called_with(self.sock, 32768)

    eleza test_loop_reading(self):
        tr = self.socket_transport()
        tr._loop_reading()
        self.loop._proactor.recv.assert_called_with(self.sock, 32768)
        self.assertUongo(self.protocol.data_received.called)
        self.assertUongo(self.protocol.eof_received.called)

    eleza test_loop_reading_data(self):
        res = self.loop.create_future()
        res.set_result(b'data')

        tr = self.socket_transport()
        tr._read_fut = res
        tr._loop_reading(res)
        self.loop._proactor.recv.assert_called_with(self.sock, 32768)
        self.protocol.data_received.assert_called_with(b'data')

    eleza test_loop_reading_no_data(self):
        res = self.loop.create_future()
        res.set_result(b'')

        tr = self.socket_transport()
        self.assertRaises(AssertionError, tr._loop_reading, res)

        tr.close = mock.Mock()
        tr._read_fut = res
        tr._loop_reading(res)
        self.assertUongo(self.loop._proactor.recv.called)
        self.assertKweli(self.protocol.eof_received.called)
        self.assertKweli(tr.close.called)

    eleza test_loop_reading_aborted(self):
        err = self.loop._proactor.recv.side_effect = ConnectionAbortedError()

        tr = self.socket_transport()
        tr._fatal_error = mock.Mock()
        tr._loop_reading()
        tr._fatal_error.assert_called_with(
                            err,
                            'Fatal read error on pipe transport')

    eleza test_loop_reading_aborted_closing(self):
        self.loop._proactor.recv.side_effect = ConnectionAbortedError()

        tr = self.socket_transport()
        tr._closing = Kweli
        tr._fatal_error = mock.Mock()
        tr._loop_reading()
        self.assertUongo(tr._fatal_error.called)

    eleza test_loop_reading_aborted_is_fatal(self):
        self.loop._proactor.recv.side_effect = ConnectionAbortedError()
        tr = self.socket_transport()
        tr._closing = Uongo
        tr._fatal_error = mock.Mock()
        tr._loop_reading()
        self.assertKweli(tr._fatal_error.called)

    eleza test_loop_reading_conn_reset_lost(self):
        err = self.loop._proactor.recv.side_effect = ConnectionResetError()

        tr = self.socket_transport()
        tr._closing = Uongo
        tr._fatal_error = mock.Mock()
        tr._force_close = mock.Mock()
        tr._loop_reading()
        self.assertUongo(tr._fatal_error.called)
        tr._force_close.assert_called_with(err)

    eleza test_loop_reading_exception(self):
        err = self.loop._proactor.recv.side_effect = (OSError())

        tr = self.socket_transport()
        tr._fatal_error = mock.Mock()
        tr._loop_reading()
        tr._fatal_error.assert_called_with(
                            err,
                            'Fatal read error on pipe transport')

    eleza test_write(self):
        tr = self.socket_transport()
        tr._loop_writing = mock.Mock()
        tr.write(b'data')
        self.assertEqual(tr._buffer, Tupu)
        tr._loop_writing.assert_called_with(data=b'data')

    eleza test_write_no_data(self):
        tr = self.socket_transport()
        tr.write(b'')
        self.assertUongo(tr._buffer)

    eleza test_write_more(self):
        tr = self.socket_transport()
        tr._write_fut = mock.Mock()
        tr._loop_writing = mock.Mock()
        tr.write(b'data')
        self.assertEqual(tr._buffer, b'data')
        self.assertUongo(tr._loop_writing.called)

    eleza test_loop_writing(self):
        tr = self.socket_transport()
        tr._buffer = bytearray(b'data')
        tr._loop_writing()
        self.loop._proactor.send.assert_called_with(self.sock, b'data')
        self.loop._proactor.send.return_value.add_done_callback.\
            assert_called_with(tr._loop_writing)

    @mock.patch('asyncio.proactor_events.logger')
    eleza test_loop_writing_err(self, m_log):
        err = self.loop._proactor.send.side_effect = OSError()
        tr = self.socket_transport()
        tr._fatal_error = mock.Mock()
        tr._buffer = [b'da', b'ta']
        tr._loop_writing()
        tr._fatal_error.assert_called_with(
                            err,
                            'Fatal write error on pipe transport')
        tr._conn_lost = 1

        tr.write(b'data')
        tr.write(b'data')
        tr.write(b'data')
        tr.write(b'data')
        tr.write(b'data')
        self.assertEqual(tr._buffer, Tupu)
        m_log.warning.assert_called_with('socket.send() raised exception.')

    eleza test_loop_writing_stop(self):
        fut = self.loop.create_future()
        fut.set_result(b'data')

        tr = self.socket_transport()
        tr._write_fut = fut
        tr._loop_writing(fut)
        self.assertIsTupu(tr._write_fut)

    eleza test_loop_writing_closing(self):
        fut = self.loop.create_future()
        fut.set_result(1)

        tr = self.socket_transport()
        tr._write_fut = fut
        tr.close()
        tr._loop_writing(fut)
        self.assertIsTupu(tr._write_fut)
        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(Tupu)

    eleza test_abort(self):
        tr = self.socket_transport()
        tr._force_close = mock.Mock()
        tr.abort()
        tr._force_close.assert_called_with(Tupu)

    eleza test_close(self):
        tr = self.socket_transport()
        tr.close()
        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(Tupu)
        self.assertKweli(tr.is_closing())
        self.assertEqual(tr._conn_lost, 1)

        self.protocol.connection_lost.reset_mock()
        tr.close()
        test_utils.run_briefly(self.loop)
        self.assertUongo(self.protocol.connection_lost.called)

    eleza test_close_write_fut(self):
        tr = self.socket_transport()
        tr._write_fut = mock.Mock()
        tr.close()
        test_utils.run_briefly(self.loop)
        self.assertUongo(self.protocol.connection_lost.called)

    eleza test_close_buffer(self):
        tr = self.socket_transport()
        tr._buffer = [b'data']
        tr.close()
        test_utils.run_briefly(self.loop)
        self.assertUongo(self.protocol.connection_lost.called)

    @mock.patch('asyncio.base_events.logger')
    eleza test_fatal_error(self, m_logging):
        tr = self.socket_transport()
        tr._force_close = mock.Mock()
        tr._fatal_error(Tupu)
        self.assertKweli(tr._force_close.called)
        self.assertKweli(m_logging.error.called)

    eleza test_force_close(self):
        tr = self.socket_transport()
        tr._buffer = [b'data']
        read_fut = tr._read_fut = mock.Mock()
        write_fut = tr._write_fut = mock.Mock()
        tr._force_close(Tupu)

        read_fut.cancel.assert_called_with()
        write_fut.cancel.assert_called_with()
        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(Tupu)
        self.assertEqual(Tupu, tr._buffer)
        self.assertEqual(tr._conn_lost, 1)

    eleza test_loop_writing_force_close(self):
        exc_handler = mock.Mock()
        self.loop.set_exception_handler(exc_handler)
        fut = self.loop.create_future()
        fut.set_result(1)
        self.proactor.send.return_value = fut

        tr = self.socket_transport()
        tr.write(b'data')
        tr._force_close(Tupu)
        test_utils.run_briefly(self.loop)
        exc_handler.assert_not_called()

    eleza test_force_close_idempotent(self):
        tr = self.socket_transport()
        tr._closing = Kweli
        tr._force_close(Tupu)
        test_utils.run_briefly(self.loop)
        self.assertUongo(self.protocol.connection_lost.called)

    eleza test_fatal_error_2(self):
        tr = self.socket_transport()
        tr._buffer = [b'data']
        tr._force_close(Tupu)

        test_utils.run_briefly(self.loop)
        self.protocol.connection_lost.assert_called_with(Tupu)
        self.assertEqual(Tupu, tr._buffer)

    eleza test_call_connection_lost(self):
        tr = self.socket_transport()
        tr._call_connection_lost(Tupu)
        self.assertKweli(self.protocol.connection_lost.called)
        self.assertKweli(self.sock.close.called)

    eleza test_write_eof(self):
        tr = self.socket_transport()
        self.assertKweli(tr.can_write_eof())
        tr.write_eof()
        self.sock.shutdown.assert_called_with(socket.SHUT_WR)
        tr.write_eof()
        self.assertEqual(self.sock.shutdown.call_count, 1)
        tr.close()

    eleza test_write_eof_buffer(self):
        tr = self.socket_transport()
        f = self.loop.create_future()
        tr._loop._proactor.send.return_value = f
        tr.write(b'data')
        tr.write_eof()
        self.assertKweli(tr._eof_written)
        self.assertUongo(self.sock.shutdown.called)
        tr._loop._proactor.send.assert_called_with(self.sock, b'data')
        f.set_result(4)
        self.loop._run_once()
        self.sock.shutdown.assert_called_with(socket.SHUT_WR)
        tr.close()

    eleza test_write_eof_write_pipe(self):
        tr = _ProactorWritePipeTransport(
            self.loop, self.sock, self.protocol)
        self.assertKweli(tr.can_write_eof())
        tr.write_eof()
        self.assertKweli(tr.is_closing())
        self.loop._run_once()
        self.assertKweli(self.sock.close.called)
        tr.close()

    eleza test_write_eof_buffer_write_pipe(self):
        tr = _ProactorWritePipeTransport(self.loop, self.sock, self.protocol)
        f = self.loop.create_future()
        tr._loop._proactor.send.return_value = f
        tr.write(b'data')
        tr.write_eof()
        self.assertKweli(tr.is_closing())
        self.assertUongo(self.sock.shutdown.called)
        tr._loop._proactor.send.assert_called_with(self.sock, b'data')
        f.set_result(4)
        self.loop._run_once()
        self.loop._run_once()
        self.assertKweli(self.sock.close.called)
        tr.close()

    eleza test_write_eof_duplex_pipe(self):
        tr = _ProactorDuplexPipeTransport(
            self.loop, self.sock, self.protocol)
        self.assertUongo(tr.can_write_eof())
        ukijumuisha self.assertRaises(NotImplementedError):
            tr.write_eof()
        close_transport(tr)

    eleza test_pause_resume_reading(self):
        tr = self.socket_transport()
        futures = []
        kila msg kwenye [b'data1', b'data2', b'data3', b'data4', b'data5', b'']:
            f = self.loop.create_future()
            f.set_result(msg)
            futures.append(f)

        self.loop._proactor.recv.side_effect = futures
        self.loop._run_once()
        self.assertUongo(tr._paused)
        self.assertKweli(tr.is_reading())
        self.loop._run_once()
        self.protocol.data_received.assert_called_with(b'data1')
        self.loop._run_once()
        self.protocol.data_received.assert_called_with(b'data2')

        tr.pause_reading()
        tr.pause_reading()
        self.assertKweli(tr._paused)
        self.assertUongo(tr.is_reading())
        kila i kwenye range(10):
            self.loop._run_once()
        self.protocol.data_received.assert_called_with(b'data2')

        tr.resume_reading()
        tr.resume_reading()
        self.assertUongo(tr._paused)
        self.assertKweli(tr.is_reading())
        self.loop._run_once()
        self.protocol.data_received.assert_called_with(b'data3')
        self.loop._run_once()
        self.protocol.data_received.assert_called_with(b'data4')

        tr.pause_reading()
        tr.resume_reading()
        self.loop.call_exception_handler = mock.Mock()
        self.loop._run_once()
        self.loop.call_exception_handler.assert_not_called()
        self.protocol.data_received.assert_called_with(b'data5')
        tr.close()

        self.assertUongo(tr.is_reading())


    eleza pause_writing_transport(self, high):
        tr = self.socket_transport()
        tr.set_write_buffer_limits(high=high)

        self.assertEqual(tr.get_write_buffer_size(), 0)
        self.assertUongo(self.protocol.pause_writing.called)
        self.assertUongo(self.protocol.resume_writing.called)
        rudisha tr

    eleza test_pause_resume_writing(self):
        tr = self.pause_writing_transport(high=4)

        # write a large chunk, must pause writing
        fut = self.loop.create_future()
        self.loop._proactor.send.return_value = fut
        tr.write(b'large data')
        self.loop._run_once()
        self.assertKweli(self.protocol.pause_writing.called)

        # flush the buffer
        fut.set_result(Tupu)
        self.loop._run_once()
        self.assertEqual(tr.get_write_buffer_size(), 0)
        self.assertKweli(self.protocol.resume_writing.called)

    eleza test_pause_writing_2write(self):
        tr = self.pause_writing_transport(high=4)

        # first short write, the buffer ni sio full (3 <= 4)
        fut1 = self.loop.create_future()
        self.loop._proactor.send.return_value = fut1
        tr.write(b'123')
        self.loop._run_once()
        self.assertEqual(tr.get_write_buffer_size(), 3)
        self.assertUongo(self.protocol.pause_writing.called)

        # fill the buffer, must pause writing (6 > 4)
        tr.write(b'abc')
        self.loop._run_once()
        self.assertEqual(tr.get_write_buffer_size(), 6)
        self.assertKweli(self.protocol.pause_writing.called)

    eleza test_pause_writing_3write(self):
        tr = self.pause_writing_transport(high=4)

        # first short write, the buffer ni sio full (1 <= 4)
        fut = self.loop.create_future()
        self.loop._proactor.send.return_value = fut
        tr.write(b'1')
        self.loop._run_once()
        self.assertEqual(tr.get_write_buffer_size(), 1)
        self.assertUongo(self.protocol.pause_writing.called)

        # second short write, the buffer ni sio full (3 <= 4)
        tr.write(b'23')
        self.loop._run_once()
        self.assertEqual(tr.get_write_buffer_size(), 3)
        self.assertUongo(self.protocol.pause_writing.called)

        # fill the buffer, must pause writing (6 > 4)
        tr.write(b'abc')
        self.loop._run_once()
        self.assertEqual(tr.get_write_buffer_size(), 6)
        self.assertKweli(self.protocol.pause_writing.called)

    eleza test_dont_pause_writing(self):
        tr = self.pause_writing_transport(high=4)

        # write a large chunk which completes immediately,
        # it should sio pause writing
        fut = self.loop.create_future()
        fut.set_result(Tupu)
        self.loop._proactor.send.return_value = fut
        tr.write(b'very large data')
        self.loop._run_once()
        self.assertEqual(tr.get_write_buffer_size(), 0)
        self.assertUongo(self.protocol.pause_writing.called)


kundi ProactorDatagramTransportTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.proactor = mock.Mock()
        self.loop._proactor = self.proactor
        self.protocol = test_utils.make_test_protocol(asyncio.DatagramProtocol)
        self.sock = mock.Mock(spec_set=socket.socket)
        self.sock.fileno.return_value = 7

    eleza datagram_transport(self, address=Tupu):
        self.sock.getpeername.side_effect = Tupu ikiwa address isipokua OSError
        transport = _ProactorDatagramTransport(self.loop, self.sock,
                                               self.protocol,
                                               address=address)
        self.addCleanup(close_transport, transport)
        rudisha transport

    eleza test_sendto(self):
        data = b'data'
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertKweli(self.proactor.sendto.called)
        self.proactor.sendto.assert_called_with(
            self.sock, data, addr=('0.0.0.0', 1234))

    eleza test_sendto_bytearray(self):
        data = bytearray(b'data')
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertKweli(self.proactor.sendto.called)
        self.proactor.sendto.assert_called_with(
            self.sock, b'data', addr=('0.0.0.0', 1234))

    eleza test_sendto_memoryview(self):
        data = memoryview(b'data')
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertKweli(self.proactor.sendto.called)
        self.proactor.sendto.assert_called_with(
            self.sock, b'data', addr=('0.0.0.0', 1234))

    eleza test_sendto_no_data(self):
        transport = self.datagram_transport()
        transport._buffer.append((b'data', ('0.0.0.0', 12345)))
        transport.sendto(b'', ())
        self.assertUongo(self.sock.sendto.called)
        self.assertEqual(
            [(b'data', ('0.0.0.0', 12345))], list(transport._buffer))

    eleza test_sendto_buffer(self):
        transport = self.datagram_transport()
        transport._buffer.append((b'data1', ('0.0.0.0', 12345)))
        transport._write_fut = object()
        transport.sendto(b'data2', ('0.0.0.0', 12345))
        self.assertUongo(self.proactor.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))

    eleza test_sendto_buffer_bytearray(self):
        data2 = bytearray(b'data2')
        transport = self.datagram_transport()
        transport._buffer.append((b'data1', ('0.0.0.0', 12345)))
        transport._write_fut = object()
        transport.sendto(data2, ('0.0.0.0', 12345))
        self.assertUongo(self.proactor.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))
        self.assertIsInstance(transport._buffer[1][0], bytes)

    eleza test_sendto_buffer_memoryview(self):
        data2 = memoryview(b'data2')
        transport = self.datagram_transport()
        transport._buffer.append((b'data1', ('0.0.0.0', 12345)))
        transport._write_fut = object()
        transport.sendto(data2, ('0.0.0.0', 12345))
        self.assertUongo(self.proactor.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))
        self.assertIsInstance(transport._buffer[1][0], bytes)

    @mock.patch('asyncio.proactor_events.logger')
    eleza test_sendto_exception(self, m_log):
        data = b'data'
        err = self.proactor.sendto.side_effect = RuntimeError()

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport.sendto(data, ())

        self.assertKweli(transport._fatal_error.called)
        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on datagram transport')
        transport._conn_lost = 1

        transport._address = ('123',)
        transport.sendto(data)
        transport.sendto(data)
        transport.sendto(data)
        transport.sendto(data)
        transport.sendto(data)
        m_log.warning.assert_called_with('socket.sendto() raised exception.')

    eleza test_sendto_error_received(self):
        data = b'data'

        self.sock.sendto.side_effect = ConnectionRefusedError

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport.sendto(data, ())

        self.assertEqual(transport._conn_lost, 0)
        self.assertUongo(transport._fatal_error.called)

    eleza test_sendto_error_received_connected(self):
        data = b'data'

        self.proactor.send.side_effect = ConnectionRefusedError

        transport = self.datagram_transport(address=('0.0.0.0', 1))
        transport._fatal_error = mock.Mock()
        transport.sendto(data)

        self.assertUongo(transport._fatal_error.called)
        self.assertKweli(self.protocol.error_received.called)

    eleza test_sendto_str(self):
        transport = self.datagram_transport()
        self.assertRaises(TypeError, transport.sendto, 'str', ())

    eleza test_sendto_connected_addr(self):
        transport = self.datagram_transport(address=('0.0.0.0', 1))
        self.assertRaises(
            ValueError, transport.sendto, b'str', ('0.0.0.0', 2))

    eleza test_sendto_closing(self):
        transport = self.datagram_transport(address=(1,))
        transport.close()
        self.assertEqual(transport._conn_lost, 1)
        transport.sendto(b'data', (1,))
        self.assertEqual(transport._conn_lost, 2)

    eleza test__loop_writing_closing(self):
        transport = self.datagram_transport()
        transport._closing = Kweli
        transport._loop_writing()
        self.assertIsTupu(transport._write_fut)
        test_utils.run_briefly(self.loop)
        self.sock.close.assert_called_with()
        self.protocol.connection_lost.assert_called_with(Tupu)

    eleza test__loop_writing_exception(self):
        err = self.proactor.sendto.side_effect = RuntimeError()

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._loop_writing()

        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on datagram transport')

    eleza test__loop_writing_error_received(self):
        self.proactor.sendto.side_effect = ConnectionRefusedError

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._loop_writing()

        self.assertUongo(transport._fatal_error.called)

    eleza test__loop_writing_error_received_connection(self):
        self.proactor.send.side_effect = ConnectionRefusedError

        transport = self.datagram_transport(address=('0.0.0.0', 1))
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._loop_writing()

        self.assertUongo(transport._fatal_error.called)
        self.assertKweli(self.protocol.error_received.called)

    @mock.patch('asyncio.base_events.logger.error')
    eleza test_fatal_error_connected(self, m_exc):
        transport = self.datagram_transport(address=('0.0.0.0', 1))
        err = ConnectionRefusedError()
        transport._fatal_error(err)
        self.assertUongo(self.protocol.error_received.called)
        m_exc.assert_not_called()


kundi BaseProactorEventLoopTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()

        self.sock = test_utils.mock_nonblocking_socket()
        self.proactor = mock.Mock()

        self.ssock, self.csock = mock.Mock(), mock.Mock()

        ukijumuisha mock.patch('asyncio.proactor_events.socket.socketpair',
                        return_value=(self.ssock, self.csock)):
            ukijumuisha mock.patch('signal.set_wakeup_fd'):
                self.loop = BaseProactorEventLoop(self.proactor)
        self.set_event_loop(self.loop)

    @mock.patch('asyncio.proactor_events.socket.socketpair')
    eleza test_ctor(self, socketpair):
        ssock, csock = socketpair.return_value = (
            mock.Mock(), mock.Mock())
        ukijumuisha mock.patch('signal.set_wakeup_fd'):
            loop = BaseProactorEventLoop(self.proactor)
        self.assertIs(loop._ssock, ssock)
        self.assertIs(loop._csock, csock)
        self.assertEqual(loop._internal_fds, 1)
        loop.close()

    eleza test_close_self_pipe(self):
        self.loop._close_self_pipe()
        self.assertEqual(self.loop._internal_fds, 0)
        self.assertKweli(self.ssock.close.called)
        self.assertKweli(self.csock.close.called)
        self.assertIsTupu(self.loop._ssock)
        self.assertIsTupu(self.loop._csock)

        # Don't call close(): _close_self_pipe() cansio be called twice
        self.loop._closed = Kweli

    eleza test_close(self):
        self.loop._close_self_pipe = mock.Mock()
        self.loop.close()
        self.assertKweli(self.loop._close_self_pipe.called)
        self.assertKweli(self.proactor.close.called)
        self.assertIsTupu(self.loop._proactor)

        self.loop._close_self_pipe.reset_mock()
        self.loop.close()
        self.assertUongo(self.loop._close_self_pipe.called)

    eleza test_make_socket_transport(self):
        tr = self.loop._make_socket_transport(self.sock, asyncio.Protocol())
        self.assertIsInstance(tr, _ProactorSocketTransport)
        close_transport(tr)

    eleza test_loop_self_reading(self):
        self.loop._loop_self_reading()
        self.proactor.recv.assert_called_with(self.ssock, 4096)
        self.proactor.recv.return_value.add_done_callback.assert_called_with(
            self.loop._loop_self_reading)

    eleza test_loop_self_reading_fut(self):
        fut = mock.Mock()
        self.loop._loop_self_reading(fut)
        self.assertKweli(fut.result.called)
        self.proactor.recv.assert_called_with(self.ssock, 4096)
        self.proactor.recv.return_value.add_done_callback.assert_called_with(
            self.loop._loop_self_reading)

    eleza test_loop_self_reading_exception(self):
        self.loop.call_exception_handler = mock.Mock()
        self.proactor.recv.side_effect = OSError()
        self.loop._loop_self_reading()
        self.assertKweli(self.loop.call_exception_handler.called)

    eleza test_write_to_self(self):
        self.loop._write_to_self()
        self.csock.send.assert_called_with(b'\0')

    eleza test_process_events(self):
        self.loop._process_events([])

    @mock.patch('asyncio.base_events.logger')
    eleza test_create_server(self, m_log):
        pf = mock.Mock()
        call_soon = self.loop.call_soon = mock.Mock()

        self.loop._start_serving(pf, self.sock)
        self.assertKweli(call_soon.called)

        # callback
        loop = call_soon.call_args[0][0]
        loop()
        self.proactor.accept.assert_called_with(self.sock)

        # conn
        fut = mock.Mock()
        fut.result.return_value = (mock.Mock(), mock.Mock())

        make_tr = self.loop._make_socket_transport = mock.Mock()
        loop(fut)
        self.assertKweli(fut.result.called)
        self.assertKweli(make_tr.called)

        # exception
        fut.result.side_effect = OSError()
        loop(fut)
        self.assertKweli(self.sock.close.called)
        self.assertKweli(m_log.error.called)

    eleza test_create_server_cancel(self):
        pf = mock.Mock()
        call_soon = self.loop.call_soon = mock.Mock()

        self.loop._start_serving(pf, self.sock)
        loop = call_soon.call_args[0][0]

        # cancelled
        fut = self.loop.create_future()
        fut.cancel()
        loop(fut)
        self.assertKweli(self.sock.close.called)

    eleza test_stop_serving(self):
        sock1 = mock.Mock()
        future1 = mock.Mock()
        sock2 = mock.Mock()
        future2 = mock.Mock()
        self.loop._accept_futures = {
            sock1.fileno(): future1,
            sock2.fileno(): future2
        }

        self.loop._stop_serving(sock1)
        self.assertKweli(sock1.close.called)
        self.assertKweli(future1.cancel.called)
        self.proactor._stop_serving.assert_called_with(sock1)
        self.assertUongo(sock2.close.called)
        self.assertUongo(future2.cancel.called)

    eleza datagram_transport(self):
        self.protocol = test_utils.make_test_protocol(asyncio.DatagramProtocol)
        rudisha self.loop._make_datagram_transport(self.sock, self.protocol)

    eleza test_make_datagram_transport(self):
        tr = self.datagram_transport()
        self.assertIsInstance(tr, _ProactorDatagramTransport)
        close_transport(tr)

    eleza test_datagram_loop_writing(self):
        tr = self.datagram_transport()
        tr._buffer.appendleft((b'data', ('127.0.0.1', 12068)))
        tr._loop_writing()
        self.loop._proactor.sendto.assert_called_with(self.sock, b'data', addr=('127.0.0.1', 12068))
        self.loop._proactor.sendto.return_value.add_done_callback.\
            assert_called_with(tr._loop_writing)

        close_transport(tr)

    eleza test_datagram_loop_reading(self):
        tr = self.datagram_transport()
        tr._loop_reading()
        self.loop._proactor.recvfrom.assert_called_with(self.sock, 256 * 1024)
        self.assertUongo(self.protocol.datagram_received.called)
        self.assertUongo(self.protocol.error_received.called)
        close_transport(tr)

    eleza test_datagram_loop_reading_data(self):
        res = self.loop.create_future()
        res.set_result((b'data', ('127.0.0.1', 12068)))

        tr = self.datagram_transport()
        tr._read_fut = res
        tr._loop_reading(res)
        self.loop._proactor.recvfrom.assert_called_with(self.sock, 256 * 1024)
        self.protocol.datagram_received.assert_called_with(b'data', ('127.0.0.1', 12068))
        close_transport(tr)

    eleza test_datagram_loop_reading_no_data(self):
        res = self.loop.create_future()
        res.set_result((b'', ('127.0.0.1', 12068)))

        tr = self.datagram_transport()
        self.assertRaises(AssertionError, tr._loop_reading, res)

        tr.close = mock.Mock()
        tr._read_fut = res
        tr._loop_reading(res)
        self.assertKweli(self.loop._proactor.recvfrom.called)
        self.assertUongo(self.protocol.error_received.called)
        self.assertUongo(tr.close.called)
        close_transport(tr)

    eleza test_datagram_loop_reading_aborted(self):
        err = self.loop._proactor.recvfrom.side_effect = ConnectionAbortedError()

        tr = self.datagram_transport()
        tr._fatal_error = mock.Mock()
        tr._protocol.error_received = mock.Mock()
        tr._loop_reading()
        tr._protocol.error_received.assert_called_with(err)
        close_transport(tr)

    eleza test_datagram_loop_writing_aborted(self):
        err = self.loop._proactor.sendto.side_effect = ConnectionAbortedError()

        tr = self.datagram_transport()
        tr._fatal_error = mock.Mock()
        tr._protocol.error_received = mock.Mock()
        tr._buffer.appendleft((b'Hello', ('127.0.0.1', 12068)))
        tr._loop_writing()
        tr._protocol.error_received.assert_called_with(err)
        close_transport(tr)


@unittest.skipIf(sys.platform != 'win32',
                 'Proactor ni supported on Windows only')
kundi ProactorEventLoopUnixSockSendfileTests(test_utils.TestCase):
    DATA = b"12345abcde" * 16 * 1024  # 160 KiB

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
        self.loop = asyncio.ProactorEventLoop()
        self.set_event_loop(self.loop)
        self.addCleanup(self.loop.close)
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
        srv_sock.bind(('127.0.0.1', port))
        server = self.run_loop(self.loop.create_server(
            lambda: proto, sock=srv_sock))
        self.run_loop(self.loop.sock_connect(sock, srv_sock.getsockname()))

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


ikiwa __name__ == '__main__':
    unittest.main()
