"""Tests kila selector_events.py"""

agiza selectors
agiza socket
agiza unittest
kutoka unittest agiza mock
jaribu:
    agiza ssl
except ImportError:
    ssl = Tupu

agiza asyncio
kutoka asyncio.selector_events agiza BaseSelectorEventLoop
kutoka asyncio.selector_events agiza _SelectorTransport
kutoka asyncio.selector_events agiza _SelectorSocketTransport
kutoka asyncio.selector_events agiza _SelectorDatagramTransport
kutoka test.test_asyncio agiza utils as test_utils


MOCK_ANY = mock.ANY


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi TestBaseSelectorEventLoop(BaseSelectorEventLoop):

    eleza _make_self_pipe(self):
        self._ssock = mock.Mock()
        self._csock = mock.Mock()
        self._internal_fds += 1

    eleza _close_self_pipe(self):
        pass


eleza list_to_buffer(l=()):
    rudisha bytearray().join(l)


eleza close_transport(transport):
    # Don't call transport.close() because the event loop na the selector
    # are mocked
    ikiwa transport._sock ni Tupu:
        return
    transport._sock.close()
    transport._sock = Tupu


kundi BaseSelectorEventLoopTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.selector = mock.Mock()
        self.selector.select.return_value = []
        self.loop = TestBaseSelectorEventLoop(self.selector)
        self.set_event_loop(self.loop)

    eleza test_make_socket_transport(self):
        m = mock.Mock()
        self.loop.add_reader = mock.Mock()
        self.loop.add_reader._is_coroutine = Uongo
        transport = self.loop._make_socket_transport(m, asyncio.Protocol())
        self.assertIsInstance(transport, _SelectorSocketTransport)

        # Calling repr() must sio fail when the event loop ni closed
        self.loop.close()
        repr(transport)

        close_transport(transport)

    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_make_ssl_transport(self):
        m = mock.Mock()
        self.loop._add_reader = mock.Mock()
        self.loop._add_reader._is_coroutine = Uongo
        self.loop._add_writer = mock.Mock()
        self.loop._remove_reader = mock.Mock()
        self.loop._remove_writer = mock.Mock()
        waiter = self.loop.create_future()
        ukijumuisha test_utils.disable_logger():
            transport = self.loop._make_ssl_transport(
                m, asyncio.Protocol(), m, waiter)

            ukijumuisha self.assertRaisesRegex(RuntimeError,
                                        r'SSL transport.*not.*initialized'):
                transport.is_reading()

            # execute the handshake wakati the logger ni disabled
            # to ignore SSL handshake failure
            test_utils.run_briefly(self.loop)

        self.assertKweli(transport.is_reading())
        transport.pause_reading()
        transport.pause_reading()
        self.assertUongo(transport.is_reading())
        transport.resume_reading()
        transport.resume_reading()
        self.assertKweli(transport.is_reading())

        # Sanity check
        class_name = transport.__class__.__name__
        self.assertIn("ssl", class_name.lower())
        self.assertIn("transport", class_name.lower())

        transport.close()
        # execute pending callbacks to close the socket transport
        test_utils.run_briefly(self.loop)

    @mock.patch('asyncio.selector_events.ssl', Tupu)
    @mock.patch('asyncio.sslproto.ssl', Tupu)
    eleza test_make_ssl_transport_without_ssl_error(self):
        m = mock.Mock()
        self.loop.add_reader = mock.Mock()
        self.loop.add_writer = mock.Mock()
        self.loop.remove_reader = mock.Mock()
        self.loop.remove_writer = mock.Mock()
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop._make_ssl_transport(m, m, m, m)

    eleza test_close(self):
        kundi EventLoop(BaseSelectorEventLoop):
            eleza _make_self_pipe(self):
                self._ssock = mock.Mock()
                self._csock = mock.Mock()
                self._internal_fds += 1

        self.loop = EventLoop(self.selector)
        self.set_event_loop(self.loop)

        ssock = self.loop._ssock
        ssock.fileno.return_value = 7
        csock = self.loop._csock
        csock.fileno.return_value = 1
        remove_reader = self.loop._remove_reader = mock.Mock()

        self.loop._selector.close()
        self.loop._selector = selector = mock.Mock()
        self.assertUongo(self.loop.is_closed())

        self.loop.close()
        self.assertKweli(self.loop.is_closed())
        self.assertIsTupu(self.loop._selector)
        self.assertIsTupu(self.loop._csock)
        self.assertIsTupu(self.loop._ssock)
        selector.close.assert_called_with()
        ssock.close.assert_called_with()
        csock.close.assert_called_with()
        remove_reader.assert_called_with(7)

        # it should be possible to call close() more than once
        self.loop.close()
        self.loop.close()

        # operation blocked when the loop ni closed
        f = self.loop.create_future()
        self.assertRaises(RuntimeError, self.loop.run_forever)
        self.assertRaises(RuntimeError, self.loop.run_until_complete, f)
        fd = 0
        eleza callback():
            pass
        self.assertRaises(RuntimeError, self.loop.add_reader, fd, callback)
        self.assertRaises(RuntimeError, self.loop.add_writer, fd, callback)

    eleza test_close_no_selector(self):
        self.loop.remove_reader = mock.Mock()
        self.loop._selector.close()
        self.loop._selector = Tupu
        self.loop.close()
        self.assertIsTupu(self.loop._selector)

    eleza test_read_from_self_tryagain(self):
        self.loop._ssock.recv.side_effect = BlockingIOError
        self.assertIsTupu(self.loop._read_from_self())

    eleza test_read_from_self_exception(self):
        self.loop._ssock.recv.side_effect = OSError
        self.assertRaises(OSError, self.loop._read_from_self)

    eleza test_write_to_self_tryagain(self):
        self.loop._csock.send.side_effect = BlockingIOError
        ukijumuisha test_utils.disable_logger():
            self.assertIsTupu(self.loop._write_to_self())

    eleza test_write_to_self_exception(self):
        # _write_to_self() swallows OSError
        self.loop._csock.send.side_effect = RuntimeError()
        self.assertRaises(RuntimeError, self.loop._write_to_self)

    eleza test_add_reader(self):
        self.loop._selector.get_key.side_effect = KeyError
        cb = lambda: Kweli
        self.loop.add_reader(1, cb)

        self.assertKweli(self.loop._selector.register.called)
        fd, mask, (r, w) = self.loop._selector.register.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_READ, mask)
        self.assertEqual(cb, r._callback)
        self.assertIsTupu(w)

    eleza test_add_reader_existing(self):
        reader = mock.Mock()
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_WRITE, (reader, writer))
        cb = lambda: Kweli
        self.loop.add_reader(1, cb)

        self.assertKweli(reader.cancel.called)
        self.assertUongo(self.loop._selector.register.called)
        self.assertKweli(self.loop._selector.modify.called)
        fd, mask, (r, w) = self.loop._selector.modify.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_WRITE | selectors.EVENT_READ, mask)
        self.assertEqual(cb, r._callback)
        self.assertEqual(writer, w)

    eleza test_add_reader_existing_writer(self):
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_WRITE, (Tupu, writer))
        cb = lambda: Kweli
        self.loop.add_reader(1, cb)

        self.assertUongo(self.loop._selector.register.called)
        self.assertKweli(self.loop._selector.modify.called)
        fd, mask, (r, w) = self.loop._selector.modify.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_WRITE | selectors.EVENT_READ, mask)
        self.assertEqual(cb, r._callback)
        self.assertEqual(writer, w)

    eleza test_remove_reader(self):
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_READ, (Tupu, Tupu))
        self.assertUongo(self.loop.remove_reader(1))

        self.assertKweli(self.loop._selector.unregister.called)

    eleza test_remove_reader_read_write(self):
        reader = mock.Mock()
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_READ | selectors.EVENT_WRITE,
            (reader, writer))
        self.assertKweli(
            self.loop.remove_reader(1))

        self.assertUongo(self.loop._selector.unregister.called)
        self.assertEqual(
            (1, selectors.EVENT_WRITE, (Tupu, writer)),
            self.loop._selector.modify.call_args[0])

    eleza test_remove_reader_unknown(self):
        self.loop._selector.get_key.side_effect = KeyError
        self.assertUongo(
            self.loop.remove_reader(1))

    eleza test_add_writer(self):
        self.loop._selector.get_key.side_effect = KeyError
        cb = lambda: Kweli
        self.loop.add_writer(1, cb)

        self.assertKweli(self.loop._selector.register.called)
        fd, mask, (r, w) = self.loop._selector.register.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_WRITE, mask)
        self.assertIsTupu(r)
        self.assertEqual(cb, w._callback)

    eleza test_add_writer_existing(self):
        reader = mock.Mock()
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_READ, (reader, writer))
        cb = lambda: Kweli
        self.loop.add_writer(1, cb)

        self.assertKweli(writer.cancel.called)
        self.assertUongo(self.loop._selector.register.called)
        self.assertKweli(self.loop._selector.modify.called)
        fd, mask, (r, w) = self.loop._selector.modify.call_args[0]
        self.assertEqual(1, fd)
        self.assertEqual(selectors.EVENT_WRITE | selectors.EVENT_READ, mask)
        self.assertEqual(reader, r)
        self.assertEqual(cb, w._callback)

    eleza test_remove_writer(self):
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_WRITE, (Tupu, Tupu))
        self.assertUongo(self.loop.remove_writer(1))

        self.assertKweli(self.loop._selector.unregister.called)

    eleza test_remove_writer_read_write(self):
        reader = mock.Mock()
        writer = mock.Mock()
        self.loop._selector.get_key.return_value = selectors.SelectorKey(
            1, 1, selectors.EVENT_READ | selectors.EVENT_WRITE,
            (reader, writer))
        self.assertKweli(
            self.loop.remove_writer(1))

        self.assertUongo(self.loop._selector.unregister.called)
        self.assertEqual(
            (1, selectors.EVENT_READ, (reader, Tupu)),
            self.loop._selector.modify.call_args[0])

    eleza test_remove_writer_unknown(self):
        self.loop._selector.get_key.side_effect = KeyError
        self.assertUongo(
            self.loop.remove_writer(1))

    eleza test_process_events_read(self):
        reader = mock.Mock()
        reader._cancelled = Uongo

        self.loop._add_callback = mock.Mock()
        self.loop._process_events(
            [(selectors.SelectorKey(
                1, 1, selectors.EVENT_READ, (reader, Tupu)),
              selectors.EVENT_READ)])
        self.assertKweli(self.loop._add_callback.called)
        self.loop._add_callback.assert_called_with(reader)

    eleza test_process_events_read_cancelled(self):
        reader = mock.Mock()
        reader.cancelled = Kweli

        self.loop._remove_reader = mock.Mock()
        self.loop._process_events(
            [(selectors.SelectorKey(
                1, 1, selectors.EVENT_READ, (reader, Tupu)),
             selectors.EVENT_READ)])
        self.loop._remove_reader.assert_called_with(1)

    eleza test_process_events_write(self):
        writer = mock.Mock()
        writer._cancelled = Uongo

        self.loop._add_callback = mock.Mock()
        self.loop._process_events(
            [(selectors.SelectorKey(1, 1, selectors.EVENT_WRITE,
                                    (Tupu, writer)),
              selectors.EVENT_WRITE)])
        self.loop._add_callback.assert_called_with(writer)

    eleza test_process_events_write_cancelled(self):
        writer = mock.Mock()
        writer.cancelled = Kweli
        self.loop._remove_writer = mock.Mock()

        self.loop._process_events(
            [(selectors.SelectorKey(1, 1, selectors.EVENT_WRITE,
                                    (Tupu, writer)),
              selectors.EVENT_WRITE)])
        self.loop._remove_writer.assert_called_with(1)

    eleza test_accept_connection_multiple(self):
        sock = mock.Mock()
        sock.accept.return_value = (mock.Mock(), mock.Mock())
        backlog = 100
        # Mock the coroutine generation kila a connection to prevent
        # warnings related to un-awaited coroutines. _accept_connection2
        # ni an async function that ni patched ukijumuisha AsyncMock. create_task
        # creates a task out of coroutine returned by AsyncMock, so use
        # asyncio.sleep(0) to ensure created tasks are complete to avoid
        # task pending warnings.
        mock_obj = mock.patch.object
        ukijumuisha mock_obj(self.loop, '_accept_connection2') as accept2_mock:
            self.loop._accept_connection(
                mock.Mock(), sock, backlog=backlog)
        self.loop.run_until_complete(asyncio.sleep(0))
        self.assertEqual(sock.accept.call_count, backlog)


kundi SelectorTransportTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.Protocol)
        self.sock = mock.Mock(socket.socket)
        self.sock.fileno.return_value = 7

    eleza create_transport(self):
        transport = _SelectorTransport(self.loop, self.sock, self.protocol,
                                       Tupu)
        self.addCleanup(close_transport, transport)
        rudisha transport

    eleza test_ctor(self):
        tr = self.create_transport()
        self.assertIs(tr._loop, self.loop)
        self.assertIs(tr._sock, self.sock)
        self.assertIs(tr._sock_fd, 7)

    eleza test_abort(self):
        tr = self.create_transport()
        tr._force_close = mock.Mock()

        tr.abort()
        tr._force_close.assert_called_with(Tupu)

    eleza test_close(self):
        tr = self.create_transport()
        tr.close()

        self.assertKweli(tr.is_closing())
        self.assertEqual(1, self.loop.remove_reader_count[7])
        self.protocol.connection_lost(Tupu)
        self.assertEqual(tr._conn_lost, 1)

        tr.close()
        self.assertEqual(tr._conn_lost, 1)
        self.assertEqual(1, self.loop.remove_reader_count[7])

    eleza test_close_write_buffer(self):
        tr = self.create_transport()
        tr._buffer.extend(b'data')
        tr.close()

        self.assertUongo(self.loop.readers)
        test_utils.run_briefly(self.loop)
        self.assertUongo(self.protocol.connection_lost.called)

    eleza test_force_close(self):
        tr = self.create_transport()
        tr._buffer.extend(b'1')
        self.loop._add_reader(7, mock.sentinel)
        self.loop._add_writer(7, mock.sentinel)
        tr._force_close(Tupu)

        self.assertKweli(tr.is_closing())
        self.assertEqual(tr._buffer, list_to_buffer())
        self.assertUongo(self.loop.readers)
        self.assertUongo(self.loop.writers)

        # second close should sio remove reader
        tr._force_close(Tupu)
        self.assertUongo(self.loop.readers)
        self.assertEqual(1, self.loop.remove_reader_count[7])

    @mock.patch('asyncio.log.logger.error')
    eleza test_fatal_error(self, m_exc):
        exc = OSError()
        tr = self.create_transport()
        tr._force_close = mock.Mock()
        tr._fatal_error(exc)

        m_exc.assert_not_called()

        tr._force_close.assert_called_with(exc)

    @mock.patch('asyncio.log.logger.error')
    eleza test_fatal_error_custom_exception(self, m_exc):
        kundi MyError(Exception):
            pass
        exc = MyError()
        tr = self.create_transport()
        tr._force_close = mock.Mock()
        tr._fatal_error(exc)

        m_exc.assert_called_with(
            test_utils.MockPattern(
                'Fatal error on transport\nprotocol:.*\ntransport:.*'),
            exc_info=(MyError, MOCK_ANY, MOCK_ANY))

        tr._force_close.assert_called_with(exc)

    eleza test_connection_lost(self):
        exc = OSError()
        tr = self.create_transport()
        self.assertIsNotTupu(tr._protocol)
        self.assertIsNotTupu(tr._loop)
        tr._call_connection_lost(exc)

        self.protocol.connection_lost.assert_called_with(exc)
        self.sock.close.assert_called_with()
        self.assertIsTupu(tr._sock)

        self.assertIsTupu(tr._protocol)
        self.assertIsTupu(tr._loop)

    eleza test__add_reader(self):
        tr = self.create_transport()
        tr._buffer.extend(b'1')
        tr._add_reader(7, mock.sentinel)
        self.assertKweli(self.loop.readers)

        tr._force_close(Tupu)

        self.assertKweli(tr.is_closing())
        self.assertUongo(self.loop.readers)

        # can sio add readers after closing
        tr._add_reader(7, mock.sentinel)
        self.assertUongo(self.loop.readers)


kundi SelectorSocketTransportTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.Protocol)
        self.sock = mock.Mock(socket.socket)
        self.sock_fd = self.sock.fileno.return_value = 7

    eleza socket_transport(self, waiter=Tupu):
        transport = _SelectorSocketTransport(self.loop, self.sock,
                                             self.protocol, waiter=waiter)
        self.addCleanup(close_transport, transport)
        rudisha transport

    eleza test_ctor(self):
        waiter = self.loop.create_future()
        tr = self.socket_transport(waiter=waiter)
        self.loop.run_until_complete(waiter)

        self.loop.assert_reader(7, tr._read_ready)
        test_utils.run_briefly(self.loop)
        self.protocol.connection_made.assert_called_with(tr)

    eleza test_ctor_with_waiter(self):
        waiter = self.loop.create_future()
        self.socket_transport(waiter=waiter)
        self.loop.run_until_complete(waiter)

        self.assertIsTupu(waiter.result())

    eleza test_pause_resume_reading(self):
        tr = self.socket_transport()
        test_utils.run_briefly(self.loop)
        self.assertUongo(tr._paused)
        self.assertKweli(tr.is_reading())
        self.loop.assert_reader(7, tr._read_ready)

        tr.pause_reading()
        tr.pause_reading()
        self.assertKweli(tr._paused)
        self.assertUongo(tr.is_reading())
        self.loop.assert_no_reader(7)

        tr.resume_reading()
        tr.resume_reading()
        self.assertUongo(tr._paused)
        self.assertKweli(tr.is_reading())
        self.loop.assert_reader(7, tr._read_ready)

        tr.close()
        self.assertUongo(tr.is_reading())
        self.loop.assert_no_reader(7)

    eleza test_read_eof_received_error(self):
        transport = self.socket_transport()
        transport.close = mock.Mock()
        transport._fatal_error = mock.Mock()

        self.loop.call_exception_handler = mock.Mock()

        self.protocol.eof_received.side_effect = LookupError()

        self.sock.recv.return_value = b''
        transport._read_ready()

        self.protocol.eof_received.assert_called_with()
        self.assertKweli(transport._fatal_error.called)

    eleza test_data_received_error(self):
        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()

        self.loop.call_exception_handler = mock.Mock()
        self.protocol.data_received.side_effect = LookupError()

        self.sock.recv.return_value = b'data'
        transport._read_ready()

        self.assertKweli(transport._fatal_error.called)
        self.assertKweli(self.protocol.data_received.called)

    eleza test_read_ready(self):
        transport = self.socket_transport()

        self.sock.recv.return_value = b'data'
        transport._read_ready()

        self.protocol.data_received.assert_called_with(b'data')

    eleza test_read_ready_eof(self):
        transport = self.socket_transport()
        transport.close = mock.Mock()

        self.sock.recv.return_value = b''
        transport._read_ready()

        self.protocol.eof_received.assert_called_with()
        transport.close.assert_called_with()

    eleza test_read_ready_eof_keep_open(self):
        transport = self.socket_transport()
        transport.close = mock.Mock()

        self.sock.recv.return_value = b''
        self.protocol.eof_received.return_value = Kweli
        transport._read_ready()

        self.protocol.eof_received.assert_called_with()
        self.assertUongo(transport.close.called)

    @mock.patch('logging.exception')
    eleza test_read_ready_tryagain(self, m_exc):
        self.sock.recv.side_effect = BlockingIOError

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertUongo(transport._fatal_error.called)

    @mock.patch('logging.exception')
    eleza test_read_ready_tryagain_interrupted(self, m_exc):
        self.sock.recv.side_effect = InterruptedError

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertUongo(transport._fatal_error.called)

    @mock.patch('logging.exception')
    eleza test_read_ready_conn_reset(self, m_exc):
        err = self.sock.recv.side_effect = ConnectionResetError()

        transport = self.socket_transport()
        transport._force_close = mock.Mock()
        ukijumuisha test_utils.disable_logger():
            transport._read_ready()
        transport._force_close.assert_called_with(err)

    @mock.patch('logging.exception')
    eleza test_read_ready_err(self, m_exc):
        err = self.sock.recv.side_effect = OSError()

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal read error on socket transport')

    eleza test_write(self):
        data = b'data'
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport.write(data)
        self.sock.send.assert_called_with(data)

    eleza test_write_bytearray(self):
        data = bytearray(b'data')
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport.write(data)
        self.sock.send.assert_called_with(data)
        self.assertEqual(data, bytearray(b'data'))  # Hasn't been mutated.

    eleza test_write_memoryview(self):
        data = memoryview(b'data')
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport.write(data)
        self.sock.send.assert_called_with(data)

    eleza test_write_no_data(self):
        transport = self.socket_transport()
        transport._buffer.extend(b'data')
        transport.write(b'')
        self.assertUongo(self.sock.send.called)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    eleza test_write_buffer(self):
        transport = self.socket_transport()
        transport._buffer.extend(b'data1')
        transport.write(b'data2')
        self.assertUongo(self.sock.send.called)
        self.assertEqual(list_to_buffer([b'data1', b'data2']),
                         transport._buffer)

    eleza test_write_partial(self):
        data = b'data'
        self.sock.send.return_value = 2

        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'ta']), transport._buffer)

    eleza test_write_partial_bytearray(self):
        data = bytearray(b'data')
        self.sock.send.return_value = 2

        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'ta']), transport._buffer)
        self.assertEqual(data, bytearray(b'data'))  # Hasn't been mutated.

    eleza test_write_partial_memoryview(self):
        data = memoryview(b'data')
        self.sock.send.return_value = 2

        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'ta']), transport._buffer)

    eleza test_write_partial_none(self):
        data = b'data'
        self.sock.send.return_value = 0
        self.sock.fileno.return_value = 7

        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    eleza test_write_tryagain(self):
        self.sock.send.side_effect = BlockingIOError

        data = b'data'
        transport = self.socket_transport()
        transport.write(data)

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    @mock.patch('asyncio.selector_events.logger')
    eleza test_write_exception(self, m_log):
        err = self.sock.send.side_effect = OSError()

        data = b'data'
        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport.write(data)
        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on socket transport')
        transport._conn_lost = 1

        self.sock.reset_mock()
        transport.write(data)
        self.assertUongo(self.sock.send.called)
        self.assertEqual(transport._conn_lost, 2)
        transport.write(data)
        transport.write(data)
        transport.write(data)
        transport.write(data)
        m_log.warning.assert_called_with('socket.send() raised exception.')

    eleza test_write_str(self):
        transport = self.socket_transport()
        self.assertRaises(TypeError, transport.write, 'str')

    eleza test_write_closing(self):
        transport = self.socket_transport()
        transport.close()
        self.assertEqual(transport._conn_lost, 1)
        transport.write(b'data')
        self.assertEqual(transport._conn_lost, 2)

    eleza test_write_ready(self):
        data = b'data'
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport._buffer.extend(data)
        self.loop._add_writer(7, transport._write_ready)
        transport._write_ready()
        self.assertKweli(self.sock.send.called)
        self.assertUongo(self.loop.writers)

    eleza test_write_ready_closing(self):
        data = b'data'
        self.sock.send.return_value = len(data)

        transport = self.socket_transport()
        transport._closing = Kweli
        transport._buffer.extend(data)
        self.loop._add_writer(7, transport._write_ready)
        transport._write_ready()
        self.assertKweli(self.sock.send.called)
        self.assertUongo(self.loop.writers)
        self.sock.close.assert_called_with()
        self.protocol.connection_lost.assert_called_with(Tupu)

    eleza test_write_ready_no_data(self):
        transport = self.socket_transport()
        # This ni an internal error.
        self.assertRaises(AssertionError, transport._write_ready)

    eleza test_write_ready_partial(self):
        data = b'data'
        self.sock.send.return_value = 2

        transport = self.socket_transport()
        transport._buffer.extend(data)
        self.loop._add_writer(7, transport._write_ready)
        transport._write_ready()
        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'ta']), transport._buffer)

    eleza test_write_ready_partial_none(self):
        data = b'data'
        self.sock.send.return_value = 0

        transport = self.socket_transport()
        transport._buffer.extend(data)
        self.loop._add_writer(7, transport._write_ready)
        transport._write_ready()
        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'data']), transport._buffer)

    eleza test_write_ready_tryagain(self):
        self.sock.send.side_effect = BlockingIOError

        transport = self.socket_transport()
        transport._buffer = list_to_buffer([b'data1', b'data2'])
        self.loop._add_writer(7, transport._write_ready)
        transport._write_ready()

        self.loop.assert_writer(7, transport._write_ready)
        self.assertEqual(list_to_buffer([b'data1data2']), transport._buffer)

    eleza test_write_ready_exception(self):
        err = self.sock.send.side_effect = OSError()

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._buffer.extend(b'data')
        transport._write_ready()
        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on socket transport')

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
        self.sock.send.side_effect = BlockingIOError
        tr.write(b'data')
        tr.write_eof()
        self.assertEqual(tr._buffer, list_to_buffer([b'data']))
        self.assertKweli(tr._eof)
        self.assertUongo(self.sock.shutdown.called)
        self.sock.send.side_effect = lambda _: 4
        tr._write_ready()
        self.assertKweli(self.sock.send.called)
        self.sock.shutdown.assert_called_with(socket.SHUT_WR)
        tr.close()

    eleza test_write_eof_after_close(self):
        tr = self.socket_transport()
        tr.close()
        self.loop.run_until_complete(asyncio.sleep(0))
        tr.write_eof()

    @mock.patch('asyncio.base_events.logger')
    eleza test_transport_close_remove_writer(self, m_log):
        remove_writer = self.loop._remove_writer = mock.Mock()

        transport = self.socket_transport()
        transport.close()
        remove_writer.assert_called_with(self.sock_fd)


kundi SelectorSocketTransportBufferedProtocolTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()

        self.protocol = test_utils.make_test_protocol(asyncio.BufferedProtocol)
        self.buf = bytearray(1)
        self.protocol.get_buffer.side_effect = lambda hint: self.buf

        self.sock = mock.Mock(socket.socket)
        self.sock_fd = self.sock.fileno.return_value = 7

    eleza socket_transport(self, waiter=Tupu):
        transport = _SelectorSocketTransport(self.loop, self.sock,
                                             self.protocol, waiter=waiter)
        self.addCleanup(close_transport, transport)
        rudisha transport

    eleza test_ctor(self):
        waiter = self.loop.create_future()
        tr = self.socket_transport(waiter=waiter)
        self.loop.run_until_complete(waiter)

        self.loop.assert_reader(7, tr._read_ready)
        test_utils.run_briefly(self.loop)
        self.protocol.connection_made.assert_called_with(tr)

    eleza test_get_buffer_error(self):
        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()

        self.loop.call_exception_handler = mock.Mock()
        self.protocol.get_buffer.side_effect = LookupError()

        transport._read_ready()

        self.assertKweli(transport._fatal_error.called)
        self.assertKweli(self.protocol.get_buffer.called)
        self.assertUongo(self.protocol.buffer_updated.called)

    eleza test_get_buffer_zerosized(self):
        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()

        self.loop.call_exception_handler = mock.Mock()
        self.protocol.get_buffer.side_effect = lambda hint: bytearray(0)

        transport._read_ready()

        self.assertKweli(transport._fatal_error.called)
        self.assertKweli(self.protocol.get_buffer.called)
        self.assertUongo(self.protocol.buffer_updated.called)

    eleza test_proto_type_switch(self):
        self.protocol = test_utils.make_test_protocol(asyncio.Protocol)
        transport = self.socket_transport()

        self.sock.recv.return_value = b'data'
        transport._read_ready()

        self.protocol.data_received.assert_called_with(b'data')

        # switch protocol to a BufferedProtocol

        buf_proto = test_utils.make_test_protocol(asyncio.BufferedProtocol)
        buf = bytearray(4)
        buf_proto.get_buffer.side_effect = lambda hint: buf

        transport.set_protocol(buf_proto)

        self.sock.recv_into.return_value = 10
        transport._read_ready()

        buf_proto.get_buffer.assert_called_with(-1)
        buf_proto.buffer_updated.assert_called_with(10)

    eleza test_buffer_updated_error(self):
        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()

        self.loop.call_exception_handler = mock.Mock()
        self.protocol.buffer_updated.side_effect = LookupError()

        self.sock.recv_into.return_value = 10
        transport._read_ready()

        self.assertKweli(transport._fatal_error.called)
        self.assertKweli(self.protocol.get_buffer.called)
        self.assertKweli(self.protocol.buffer_updated.called)

    eleza test_read_eof_received_error(self):
        transport = self.socket_transport()
        transport.close = mock.Mock()
        transport._fatal_error = mock.Mock()

        self.loop.call_exception_handler = mock.Mock()

        self.protocol.eof_received.side_effect = LookupError()

        self.sock.recv_into.return_value = 0
        transport._read_ready()

        self.protocol.eof_received.assert_called_with()
        self.assertKweli(transport._fatal_error.called)

    eleza test_read_ready(self):
        transport = self.socket_transport()

        self.sock.recv_into.return_value = 10
        transport._read_ready()

        self.protocol.get_buffer.assert_called_with(-1)
        self.protocol.buffer_updated.assert_called_with(10)

    eleza test_read_ready_eof(self):
        transport = self.socket_transport()
        transport.close = mock.Mock()

        self.sock.recv_into.return_value = 0
        transport._read_ready()

        self.protocol.eof_received.assert_called_with()
        transport.close.assert_called_with()

    eleza test_read_ready_eof_keep_open(self):
        transport = self.socket_transport()
        transport.close = mock.Mock()

        self.sock.recv_into.return_value = 0
        self.protocol.eof_received.return_value = Kweli
        transport._read_ready()

        self.protocol.eof_received.assert_called_with()
        self.assertUongo(transport.close.called)

    @mock.patch('logging.exception')
    eleza test_read_ready_tryagain(self, m_exc):
        self.sock.recv_into.side_effect = BlockingIOError

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertUongo(transport._fatal_error.called)

    @mock.patch('logging.exception')
    eleza test_read_ready_tryagain_interrupted(self, m_exc):
        self.sock.recv_into.side_effect = InterruptedError

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertUongo(transport._fatal_error.called)

    @mock.patch('logging.exception')
    eleza test_read_ready_conn_reset(self, m_exc):
        err = self.sock.recv_into.side_effect = ConnectionResetError()

        transport = self.socket_transport()
        transport._force_close = mock.Mock()
        ukijumuisha test_utils.disable_logger():
            transport._read_ready()
        transport._force_close.assert_called_with(err)

    @mock.patch('logging.exception')
    eleza test_read_ready_err(self, m_exc):
        err = self.sock.recv_into.side_effect = OSError()

        transport = self.socket_transport()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal read error on socket transport')


kundi SelectorDatagramTransportTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.protocol = test_utils.make_test_protocol(asyncio.DatagramProtocol)
        self.sock = mock.Mock(spec_set=socket.socket)
        self.sock.fileno.return_value = 7

    eleza datagram_transport(self, address=Tupu):
        self.sock.getpeername.side_effect = Tupu ikiwa address isipokua OSError
        transport = _SelectorDatagramTransport(self.loop, self.sock,
                                               self.protocol,
                                               address=address)
        self.addCleanup(close_transport, transport)
        rudisha transport

    eleza test_read_ready(self):
        transport = self.datagram_transport()

        self.sock.recvfrom.return_value = (b'data', ('0.0.0.0', 1234))
        transport._read_ready()

        self.protocol.datagram_received.assert_called_with(
            b'data', ('0.0.0.0', 1234))

    eleza test_read_ready_tryagain(self):
        transport = self.datagram_transport()

        self.sock.recvfrom.side_effect = BlockingIOError
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertUongo(transport._fatal_error.called)

    eleza test_read_ready_err(self):
        transport = self.datagram_transport()

        err = self.sock.recvfrom.side_effect = RuntimeError()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal read error on datagram transport')

    eleza test_read_ready_oserr(self):
        transport = self.datagram_transport()

        err = self.sock.recvfrom.side_effect = OSError()
        transport._fatal_error = mock.Mock()
        transport._read_ready()

        self.assertUongo(transport._fatal_error.called)
        self.protocol.error_received.assert_called_with(err)

    eleza test_sendto(self):
        data = b'data'
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertKweli(self.sock.sendto.called)
        self.assertEqual(
            self.sock.sendto.call_args[0], (data, ('0.0.0.0', 1234)))

    eleza test_sendto_bytearray(self):
        data = bytearray(b'data')
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertKweli(self.sock.sendto.called)
        self.assertEqual(
            self.sock.sendto.call_args[0], (data, ('0.0.0.0', 1234)))

    eleza test_sendto_memoryview(self):
        data = memoryview(b'data')
        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 1234))
        self.assertKweli(self.sock.sendto.called)
        self.assertEqual(
            self.sock.sendto.call_args[0], (data, ('0.0.0.0', 1234)))

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
        transport.sendto(b'data2', ('0.0.0.0', 12345))
        self.assertUongo(self.sock.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))

    eleza test_sendto_buffer_bytearray(self):
        data2 = bytearray(b'data2')
        transport = self.datagram_transport()
        transport._buffer.append((b'data1', ('0.0.0.0', 12345)))
        transport.sendto(data2, ('0.0.0.0', 12345))
        self.assertUongo(self.sock.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))
        self.assertIsInstance(transport._buffer[1][0], bytes)

    eleza test_sendto_buffer_memoryview(self):
        data2 = memoryview(b'data2')
        transport = self.datagram_transport()
        transport._buffer.append((b'data1', ('0.0.0.0', 12345)))
        transport.sendto(data2, ('0.0.0.0', 12345))
        self.assertUongo(self.sock.sendto.called)
        self.assertEqual(
            [(b'data1', ('0.0.0.0', 12345)),
             (b'data2', ('0.0.0.0', 12345))],
            list(transport._buffer))
        self.assertIsInstance(transport._buffer[1][0], bytes)

    eleza test_sendto_tryagain(self):
        data = b'data'

        self.sock.sendto.side_effect = BlockingIOError

        transport = self.datagram_transport()
        transport.sendto(data, ('0.0.0.0', 12345))

        self.loop.assert_writer(7, transport._sendto_ready)
        self.assertEqual(
            [(b'data', ('0.0.0.0', 12345))], list(transport._buffer))

    @mock.patch('asyncio.selector_events.logger')
    eleza test_sendto_exception(self, m_log):
        data = b'data'
        err = self.sock.sendto.side_effect = RuntimeError()

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
        m_log.warning.assert_called_with('socket.send() raised exception.')

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

        self.sock.send.side_effect = ConnectionRefusedError

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

    eleza test_sendto_ready(self):
        data = b'data'
        self.sock.sendto.return_value = len(data)

        transport = self.datagram_transport()
        transport._buffer.append((data, ('0.0.0.0', 12345)))
        self.loop._add_writer(7, transport._sendto_ready)
        transport._sendto_ready()
        self.assertKweli(self.sock.sendto.called)
        self.assertEqual(
            self.sock.sendto.call_args[0], (data, ('0.0.0.0', 12345)))
        self.assertUongo(self.loop.writers)

    eleza test_sendto_ready_closing(self):
        data = b'data'
        self.sock.send.return_value = len(data)

        transport = self.datagram_transport()
        transport._closing = Kweli
        transport._buffer.append((data, ()))
        self.loop._add_writer(7, transport._sendto_ready)
        transport._sendto_ready()
        self.sock.sendto.assert_called_with(data, ())
        self.assertUongo(self.loop.writers)
        self.sock.close.assert_called_with()
        self.protocol.connection_lost.assert_called_with(Tupu)

    eleza test_sendto_ready_no_data(self):
        transport = self.datagram_transport()
        self.loop._add_writer(7, transport._sendto_ready)
        transport._sendto_ready()
        self.assertUongo(self.sock.sendto.called)
        self.assertUongo(self.loop.writers)

    eleza test_sendto_ready_tryagain(self):
        self.sock.sendto.side_effect = BlockingIOError

        transport = self.datagram_transport()
        transport._buffer.extend([(b'data1', ()), (b'data2', ())])
        self.loop._add_writer(7, transport._sendto_ready)
        transport._sendto_ready()

        self.loop.assert_writer(7, transport._sendto_ready)
        self.assertEqual(
            [(b'data1', ()), (b'data2', ())],
            list(transport._buffer))

    eleza test_sendto_ready_exception(self):
        err = self.sock.sendto.side_effect = RuntimeError()

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._sendto_ready()

        transport._fatal_error.assert_called_with(
                                   err,
                                   'Fatal write error on datagram transport')

    eleza test_sendto_ready_error_received(self):
        self.sock.sendto.side_effect = ConnectionRefusedError

        transport = self.datagram_transport()
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._sendto_ready()

        self.assertUongo(transport._fatal_error.called)

    eleza test_sendto_ready_error_received_connection(self):
        self.sock.send.side_effect = ConnectionRefusedError

        transport = self.datagram_transport(address=('0.0.0.0', 1))
        transport._fatal_error = mock.Mock()
        transport._buffer.append((b'data', ()))
        transport._sendto_ready()

        self.assertUongo(transport._fatal_error.called)
        self.assertKweli(self.protocol.error_received.called)

    @mock.patch('asyncio.base_events.logger.error')
    eleza test_fatal_error_connected(self, m_exc):
        transport = self.datagram_transport(address=('0.0.0.0', 1))
        err = ConnectionRefusedError()
        transport._fatal_error(err)
        self.assertUongo(self.protocol.error_received.called)
        m_exc.assert_not_called()

    @mock.patch('asyncio.base_events.logger.error')
    eleza test_fatal_error_connected_custom_error(self, m_exc):
        kundi MyException(Exception):
            pass
        transport = self.datagram_transport(address=('0.0.0.0', 1))
        err = MyException()
        transport._fatal_error(err)
        self.assertUongo(self.protocol.error_received.called)
        m_exc.assert_called_with(
            test_utils.MockPattern(
                'Fatal error on transport\nprotocol:.*\ntransport:.*'),
            exc_info=(MyException, MOCK_ANY, MOCK_ANY))


ikiwa __name__ == '__main__':
    unittest.main()
