"""Tests kila streams.py."""

agiza gc
agiza os
agiza queue
agiza pickle
agiza socket
agiza sys
agiza threading
agiza unittest
kutoka unittest agiza mock
kutoka test agiza support
jaribu:
    agiza ssl
tatizo ImportError:
    ssl = Tupu

agiza asyncio
kutoka test.test_asyncio agiza utils kama test_utils


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi StreamTests(test_utils.TestCase):

    DATA = b'line1\nline2\nline3\n'

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    eleza tearDown(self):
        # just kwenye case ikiwa we have transport close callbacks
        test_utils.run_briefly(self.loop)

        self.loop.close()
        gc.collect()
        super().tearDown()

    @mock.patch('asyncio.streams.events')
    eleza test_ctor_global_loop(self, m_events):
        stream = asyncio.StreamReader()
        self.assertIs(stream._loop, m_events.get_event_loop.return_value)

    eleza _basetest_open_connection(self, open_connection_fut):
        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))
        ukijumuisha self.assertWarns(DeprecationWarning):
            reader, writer = self.loop.run_until_complete(open_connection_fut)
        writer.write(b'GET / HTTP/1.0\r\n\r\n')
        f = reader.readline()
        data = self.loop.run_until_complete(f)
        self.assertEqual(data, b'HTTP/1.0 200 OK\r\n')
        f = reader.read()
        data = self.loop.run_until_complete(f)
        self.assertKweli(data.endswith(b'\r\n\r\nTest message'))
        writer.close()
        self.assertEqual(messages, [])

    eleza test_open_connection(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            conn_fut = asyncio.open_connection(*httpd.address,
                                               loop=self.loop)
            self._basetest_open_connection(conn_fut)

    @support.skip_unless_bind_unix_socket
    eleza test_open_unix_connection(self):
        ukijumuisha test_utils.run_test_unix_server() kama httpd:
            conn_fut = asyncio.open_unix_connection(httpd.address,
                                                    loop=self.loop)
            self._basetest_open_connection(conn_fut)

    eleza _basetest_open_connection_no_loop_ssl(self, open_connection_fut):
        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))
        jaribu:
            ukijumuisha self.assertWarns(DeprecationWarning):
                reader, writer = self.loop.run_until_complete(open_connection_fut)
        mwishowe:
            asyncio.set_event_loop(Tupu)
        writer.write(b'GET / HTTP/1.0\r\n\r\n')
        f = reader.read()
        data = self.loop.run_until_complete(f)
        self.assertKweli(data.endswith(b'\r\n\r\nTest message'))

        writer.close()
        self.assertEqual(messages, [])

    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_open_connection_no_loop_ssl(self):
        ukijumuisha test_utils.run_test_server(use_ssl=Kweli) kama httpd:
            conn_fut = asyncio.open_connection(
                *httpd.address,
                ssl=test_utils.dummy_ssl_context(),
                loop=self.loop)

            self._basetest_open_connection_no_loop_ssl(conn_fut)

    @support.skip_unless_bind_unix_socket
    @unittest.skipIf(ssl ni Tupu, 'No ssl module')
    eleza test_open_unix_connection_no_loop_ssl(self):
        ukijumuisha test_utils.run_test_unix_server(use_ssl=Kweli) kama httpd:
            conn_fut = asyncio.open_unix_connection(
                httpd.address,
                ssl=test_utils.dummy_ssl_context(),
                server_hostname='',
                loop=self.loop)

            self._basetest_open_connection_no_loop_ssl(conn_fut)

    eleza _basetest_open_connection_error(self, open_connection_fut):
        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))
        ukijumuisha self.assertWarns(DeprecationWarning):
            reader, writer = self.loop.run_until_complete(open_connection_fut)
        writer._protocol.connection_lost(ZeroDivisionError())
        f = reader.read()
        ukijumuisha self.assertRaises(ZeroDivisionError):
            self.loop.run_until_complete(f)
        writer.close()
        test_utils.run_briefly(self.loop)
        self.assertEqual(messages, [])

    eleza test_open_connection_error(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            conn_fut = asyncio.open_connection(*httpd.address,
                                               loop=self.loop)
            self._basetest_open_connection_error(conn_fut)

    @support.skip_unless_bind_unix_socket
    eleza test_open_unix_connection_error(self):
        ukijumuisha test_utils.run_test_unix_server() kama httpd:
            conn_fut = asyncio.open_unix_connection(httpd.address,
                                                    loop=self.loop)
            self._basetest_open_connection_error(conn_fut)

    eleza test_feed_empty_data(self):
        stream = asyncio.StreamReader(loop=self.loop)

        stream.feed_data(b'')
        self.assertEqual(b'', stream._buffer)

    eleza test_feed_nonempty_data(self):
        stream = asyncio.StreamReader(loop=self.loop)

        stream.feed_data(self.DATA)
        self.assertEqual(self.DATA, stream._buffer)

    eleza test_read_zero(self):
        # Read zero bytes.
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(self.DATA)

        data = self.loop.run_until_complete(stream.read(0))
        self.assertEqual(b'', data)
        self.assertEqual(self.DATA, stream._buffer)

    eleza test_read(self):
        # Read bytes.
        stream = asyncio.StreamReader(loop=self.loop)
        read_task = self.loop.create_task(stream.read(30))

        eleza cb():
            stream.feed_data(self.DATA)
        self.loop.call_soon(cb)

        data = self.loop.run_until_complete(read_task)
        self.assertEqual(self.DATA, data)
        self.assertEqual(b'', stream._buffer)

    eleza test_read_line_komas(self):
        # Read bytes without line komas.
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'line1')
        stream.feed_data(b'line2')

        data = self.loop.run_until_complete(stream.read(5))

        self.assertEqual(b'line1', data)
        self.assertEqual(b'line2', stream._buffer)

    eleza test_read_eof(self):
        # Read bytes, stop at eof.
        stream = asyncio.StreamReader(loop=self.loop)
        read_task = self.loop.create_task(stream.read(1024))

        eleza cb():
            stream.feed_eof()
        self.loop.call_soon(cb)

        data = self.loop.run_until_complete(read_task)
        self.assertEqual(b'', data)
        self.assertEqual(b'', stream._buffer)

    eleza test_read_until_eof(self):
        # Read all bytes until eof.
        stream = asyncio.StreamReader(loop=self.loop)
        read_task = self.loop.create_task(stream.read(-1))

        eleza cb():
            stream.feed_data(b'chunk1\n')
            stream.feed_data(b'chunk2')
            stream.feed_eof()
        self.loop.call_soon(cb)

        data = self.loop.run_until_complete(read_task)

        self.assertEqual(b'chunk1\nchunk2', data)
        self.assertEqual(b'', stream._buffer)

    eleza test_read_exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'line\n')

        data = self.loop.run_until_complete(stream.read(2))
        self.assertEqual(b'li', data)

        stream.set_exception(ValueError())
        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.read(2))

    eleza test_invalid_limit(self):
        ukijumuisha self.assertRaisesRegex(ValueError, 'imit'):
            asyncio.StreamReader(limit=0, loop=self.loop)

        ukijumuisha self.assertRaisesRegex(ValueError, 'imit'):
            asyncio.StreamReader(limit=-1, loop=self.loop)

    eleza test_read_limit(self):
        stream = asyncio.StreamReader(limit=3, loop=self.loop)
        stream.feed_data(b'chunk')
        data = self.loop.run_until_complete(stream.read(5))
        self.assertEqual(b'chunk', data)
        self.assertEqual(b'', stream._buffer)

    eleza test_readline(self):
        # Read one line. 'readline' will need to wait kila the data
        # to come kutoka 'cb'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'chunk1 ')
        read_task = self.loop.create_task(stream.readline())

        eleza cb():
            stream.feed_data(b'chunk2 ')
            stream.feed_data(b'chunk3 ')
            stream.feed_data(b'\n chunk4')
        self.loop.call_soon(cb)

        line = self.loop.run_until_complete(read_task)
        self.assertEqual(b'chunk1 chunk2 chunk3 \n', line)
        self.assertEqual(b' chunk4', stream._buffer)

    eleza test_readline_limit_with_existing_data(self):
        # Read one line. The data ni kwenye StreamReader's buffer
        # before the event loop ni run.

        stream = asyncio.StreamReader(limit=3, loop=self.loop)
        stream.feed_data(b'li')
        stream.feed_data(b'ne1\nline2\n')

        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        # The buffer should contain the remaining data after exception
        self.assertEqual(b'line2\n', stream._buffer)

        stream = asyncio.StreamReader(limit=3, loop=self.loop)
        stream.feed_data(b'li')
        stream.feed_data(b'ne1')
        stream.feed_data(b'li')

        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        # No b'\n' at the end. The 'limit' ni set to 3. So before
        # waiting kila the new data kwenye buffer, 'readline' will consume
        # the entire buffer, na since the length of the consumed data
        # ni more than 3, it will ashiria a ValueError. The buffer is
        # expected to be empty now.
        self.assertEqual(b'', stream._buffer)

    eleza test_at_eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        self.assertUongo(stream.at_eof())

        stream.feed_data(b'some data\n')
        self.assertUongo(stream.at_eof())

        self.loop.run_until_complete(stream.readline())
        self.assertUongo(stream.at_eof())

        stream.feed_data(b'some data\n')
        stream.feed_eof()
        self.loop.run_until_complete(stream.readline())
        self.assertKweli(stream.at_eof())

    eleza test_readline_limit(self):
        # Read one line. StreamReaders are fed ukijumuisha data after
        # their 'readline' methods are called.

        stream = asyncio.StreamReader(limit=7, loop=self.loop)
        eleza cb():
            stream.feed_data(b'chunk1')
            stream.feed_data(b'chunk2')
            stream.feed_data(b'chunk3\n')
            stream.feed_eof()
        self.loop.call_soon(cb)

        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        # The buffer had just one line of data, na after raising
        # a ValueError it should be empty.
        self.assertEqual(b'', stream._buffer)

        stream = asyncio.StreamReader(limit=7, loop=self.loop)
        eleza cb():
            stream.feed_data(b'chunk1')
            stream.feed_data(b'chunk2\n')
            stream.feed_data(b'chunk3\n')
            stream.feed_eof()
        self.loop.call_soon(cb)

        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        self.assertEqual(b'chunk3\n', stream._buffer)

        # check strictness of the limit
        stream = asyncio.StreamReader(limit=7, loop=self.loop)
        stream.feed_data(b'1234567\n')
        line = self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'1234567\n', line)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'12345678\n')
        ukijumuisha self.assertRaises(ValueError) kama cm:
            self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'12345678')
        ukijumuisha self.assertRaises(ValueError) kama cm:
            self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'', stream._buffer)

    eleza test_readline_nolimit_nowait(self):
        # All needed data kila the first 'readline' call will be
        # kwenye the buffer.
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(self.DATA[:6])
        stream.feed_data(self.DATA[6:])

        line = self.loop.run_until_complete(stream.readline())

        self.assertEqual(b'line1\n', line)
        self.assertEqual(b'line2\nline3\n', stream._buffer)

    eleza test_readline_eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'some data')
        stream.feed_eof()

        line = self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'some data', line)

    eleza test_readline_empty_eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_eof()

        line = self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'', line)

    eleza test_readline_read_byte_count(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(self.DATA)

        self.loop.run_until_complete(stream.readline())

        data = self.loop.run_until_complete(stream.read(7))

        self.assertEqual(b'line2\nl', data)
        self.assertEqual(b'ine3\n', stream._buffer)

    eleza test_readline_exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'line\n')

        data = self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'line\n', data)

        stream.set_exception(ValueError())
        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        self.assertEqual(b'', stream._buffer)

    eleza test_readuntil_separator(self):
        stream = asyncio.StreamReader(loop=self.loop)
        ukijumuisha self.assertRaisesRegex(ValueError, 'Separator should be'):
            self.loop.run_until_complete(stream.readuntil(separator=b''))

    eleza test_readuntil_multi_chunks(self):
        stream = asyncio.StreamReader(loop=self.loop)

        stream.feed_data(b'lineAAA')
        data = self.loop.run_until_complete(stream.readuntil(separator=b'AAA'))
        self.assertEqual(b'lineAAA', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'lineAAA')
        data = self.loop.run_until_complete(stream.readuntil(b'AAA'))
        self.assertEqual(b'lineAAA', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'lineAAAxxx')
        data = self.loop.run_until_complete(stream.readuntil(b'AAA'))
        self.assertEqual(b'lineAAA', data)
        self.assertEqual(b'xxx', stream._buffer)

    eleza test_readuntil_multi_chunks_1(self):
        stream = asyncio.StreamReader(loop=self.loop)

        stream.feed_data(b'QWEaa')
        stream.feed_data(b'XYaa')
        stream.feed_data(b'a')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'QWEaaXYaaa', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'QWEaa')
        stream.feed_data(b'XYa')
        stream.feed_data(b'aa')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'QWEaaXYaaa', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'aaa')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'aaa', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'Xaaa')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'Xaaa', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'XXX')
        stream.feed_data(b'a')
        stream.feed_data(b'a')
        stream.feed_data(b'a')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'XXXaaa', data)
        self.assertEqual(b'', stream._buffer)

    eleza test_readuntil_eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'some dataAA')
        stream.feed_eof()

        ukijumuisha self.assertRaises(asyncio.IncompleteReadError) kama cm:
            self.loop.run_until_complete(stream.readuntil(b'AAA'))
        self.assertEqual(cm.exception.partial, b'some dataAA')
        self.assertIsTupu(cm.exception.expected)
        self.assertEqual(b'', stream._buffer)

    eleza test_readuntil_limit_found_sep(self):
        stream = asyncio.StreamReader(loop=self.loop, limit=3)
        stream.feed_data(b'some dataAA')
        ukijumuisha self.assertRaisesRegex(asyncio.LimitOverrunError,
                                    'sio found') kama cm:
            self.loop.run_until_complete(stream.readuntil(b'AAA'))

        self.assertEqual(b'some dataAA', stream._buffer)

        stream.feed_data(b'A')
        ukijumuisha self.assertRaisesRegex(asyncio.LimitOverrunError,
                                    'is found') kama cm:
            self.loop.run_until_complete(stream.readuntil(b'AAA'))

        self.assertEqual(b'some dataAAA', stream._buffer)

    eleza test_readexactly_zero_or_less(self):
        # Read exact number of bytes (zero ama less).
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(self.DATA)

        data = self.loop.run_until_complete(stream.readexactly(0))
        self.assertEqual(b'', data)
        self.assertEqual(self.DATA, stream._buffer)

        ukijumuisha self.assertRaisesRegex(ValueError, 'less than zero'):
            self.loop.run_until_complete(stream.readexactly(-1))
        self.assertEqual(self.DATA, stream._buffer)

    eleza test_readexactly(self):
        # Read exact number of bytes.
        stream = asyncio.StreamReader(loop=self.loop)

        n = 2 * len(self.DATA)
        read_task = self.loop.create_task(stream.readexactly(n))

        eleza cb():
            stream.feed_data(self.DATA)
            stream.feed_data(self.DATA)
            stream.feed_data(self.DATA)
        self.loop.call_soon(cb)

        data = self.loop.run_until_complete(read_task)
        self.assertEqual(self.DATA + self.DATA, data)
        self.assertEqual(self.DATA, stream._buffer)

    eleza test_readexactly_limit(self):
        stream = asyncio.StreamReader(limit=3, loop=self.loop)
        stream.feed_data(b'chunk')
        data = self.loop.run_until_complete(stream.readexactly(5))
        self.assertEqual(b'chunk', data)
        self.assertEqual(b'', stream._buffer)

    eleza test_readexactly_eof(self):
        # Read exact number of bytes (eof).
        stream = asyncio.StreamReader(loop=self.loop)
        n = 2 * len(self.DATA)
        read_task = self.loop.create_task(stream.readexactly(n))

        eleza cb():
            stream.feed_data(self.DATA)
            stream.feed_eof()
        self.loop.call_soon(cb)

        ukijumuisha self.assertRaises(asyncio.IncompleteReadError) kama cm:
            self.loop.run_until_complete(read_task)
        self.assertEqual(cm.exception.partial, self.DATA)
        self.assertEqual(cm.exception.expected, n)
        self.assertEqual(str(cm.exception),
                         '18 bytes read on a total of 36 expected bytes')
        self.assertEqual(b'', stream._buffer)

    eleza test_readexactly_exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'line\n')

        data = self.loop.run_until_complete(stream.readexactly(2))
        self.assertEqual(b'li', data)

        stream.set_exception(ValueError())
        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readexactly(2))

    eleza test_exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        self.assertIsTupu(stream.exception())

        exc = ValueError()
        stream.set_exception(exc)
        self.assertIs(stream.exception(), exc)

    eleza test_exception_waiter(self):
        stream = asyncio.StreamReader(loop=self.loop)

        async eleza set_err():
            stream.set_exception(ValueError())

        t1 = self.loop.create_task(stream.readline())
        t2 = self.loop.create_task(set_err())

        self.loop.run_until_complete(asyncio.wait([t1, t2]))

        self.assertRaises(ValueError, t1.result)

    eleza test_exception_cancel(self):
        stream = asyncio.StreamReader(loop=self.loop)

        t = self.loop.create_task(stream.readline())
        test_utils.run_briefly(self.loop)
        t.cancel()
        test_utils.run_briefly(self.loop)
        # The following line fails ikiwa set_exception() isn't careful.
        stream.set_exception(RuntimeError('message'))
        test_utils.run_briefly(self.loop)
        self.assertIs(stream._waiter, Tupu)

    eleza test_start_server(self):

        kundi MyServer:

            eleza __init__(self, loop):
                self.server = Tupu
                self.loop = loop

            async eleza handle_client(self, client_reader, client_writer):
                data = await client_reader.readline()
                client_writer.write(data)
                await client_writer.drain()
                client_writer.close()
                await client_writer.wait_closed()

            eleza start(self):
                sock = socket.create_server(('127.0.0.1', 0))
                self.server = self.loop.run_until_complete(
                    asyncio.start_server(self.handle_client,
                                         sock=sock,
                                         loop=self.loop))
                rudisha sock.getsockname()

            eleza handle_client_callback(self, client_reader, client_writer):
                self.loop.create_task(self.handle_client(client_reader,
                                                         client_writer))

            eleza start_callback(self):
                sock = socket.create_server(('127.0.0.1', 0))
                addr = sock.getsockname()
                sock.close()
                self.server = self.loop.run_until_complete(
                    asyncio.start_server(self.handle_client_callback,
                                         host=addr[0], port=addr[1],
                                         loop=self.loop))
                rudisha addr

            eleza stop(self):
                ikiwa self.server ni sio Tupu:
                    self.server.close()
                    self.loop.run_until_complete(self.server.wait_closed())
                    self.server = Tupu

        async eleza client(addr):
            ukijumuisha self.assertWarns(DeprecationWarning):
                reader, writer = await asyncio.open_connection(
                    *addr, loop=self.loop)
            # send a line
            writer.write(b"hello world!\n")
            # read it back
            msgback = await reader.readline()
            writer.close()
            await writer.wait_closed()
            rudisha msgback

        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        # test the server variant ukijumuisha a coroutine kama client handler
        server = MyServer(self.loop)
        ukijumuisha self.assertWarns(DeprecationWarning):
            addr = server.start()
        msg = self.loop.run_until_complete(self.loop.create_task(client(addr)))
        server.stop()
        self.assertEqual(msg, b"hello world!\n")

        # test the server variant ukijumuisha a callback kama client handler
        server = MyServer(self.loop)
        ukijumuisha self.assertWarns(DeprecationWarning):
            addr = server.start_callback()
        msg = self.loop.run_until_complete(self.loop.create_task(client(addr)))
        server.stop()
        self.assertEqual(msg, b"hello world!\n")

        self.assertEqual(messages, [])

    @support.skip_unless_bind_unix_socket
    eleza test_start_unix_server(self):

        kundi MyServer:

            eleza __init__(self, loop, path):
                self.server = Tupu
                self.loop = loop
                self.path = path

            async eleza handle_client(self, client_reader, client_writer):
                data = await client_reader.readline()
                client_writer.write(data)
                await client_writer.drain()
                client_writer.close()
                await client_writer.wait_closed()

            eleza start(self):
                self.server = self.loop.run_until_complete(
                    asyncio.start_unix_server(self.handle_client,
                                              path=self.path,
                                              loop=self.loop))

            eleza handle_client_callback(self, client_reader, client_writer):
                self.loop.create_task(self.handle_client(client_reader,
                                                         client_writer))

            eleza start_callback(self):
                start = asyncio.start_unix_server(self.handle_client_callback,
                                                  path=self.path,
                                                  loop=self.loop)
                self.server = self.loop.run_until_complete(start)

            eleza stop(self):
                ikiwa self.server ni sio Tupu:
                    self.server.close()
                    self.loop.run_until_complete(self.server.wait_closed())
                    self.server = Tupu

        async eleza client(path):
            ukijumuisha self.assertWarns(DeprecationWarning):
                reader, writer = await asyncio.open_unix_connection(
                    path, loop=self.loop)
            # send a line
            writer.write(b"hello world!\n")
            # read it back
            msgback = await reader.readline()
            writer.close()
            await writer.wait_closed()
            rudisha msgback

        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        # test the server variant ukijumuisha a coroutine kama client handler
        ukijumuisha test_utils.unix_socket_path() kama path:
            server = MyServer(self.loop, path)
            ukijumuisha self.assertWarns(DeprecationWarning):
                server.start()
            msg = self.loop.run_until_complete(
                self.loop.create_task(client(path)))
            server.stop()
            self.assertEqual(msg, b"hello world!\n")

        # test the server variant ukijumuisha a callback kama client handler
        ukijumuisha test_utils.unix_socket_path() kama path:
            server = MyServer(self.loop, path)
            ukijumuisha self.assertWarns(DeprecationWarning):
                server.start_callback()
            msg = self.loop.run_until_complete(
                self.loop.create_task(client(path)))
            server.stop()
            self.assertEqual(msg, b"hello world!\n")

        self.assertEqual(messages, [])

    @unittest.skipIf(sys.platform == 'win32', "Don't have pipes")
    eleza test_read_all_from_pipe_reader(self):
        # See asyncio issue 168.  This test ni derived kutoka the example
        # subprocess_attach_read_pipe.py, but we configure the
        # StreamReader's limit so that twice it ni less than the size
        # of the data writter.  Also we must explicitly attach a child
        # watcher to the event loop.

        code = """\
agiza os, sys
fd = int(sys.argv[1])
os.write(fd, b'data')
os.close(fd)
"""
        rfd, wfd = os.pipe()
        args = [sys.executable, '-c', code, str(wfd)]

        pipe = open(rfd, 'rb', 0)
        reader = asyncio.StreamReader(loop=self.loop, limit=1)
        protocol = asyncio.StreamReaderProtocol(reader, loop=self.loop)
        transport, _ = self.loop.run_until_complete(
            self.loop.connect_read_pipe(lambda: protocol, pipe))

        watcher = asyncio.SafeChildWatcher()
        watcher.attach_loop(self.loop)
        jaribu:
            asyncio.set_child_watcher(watcher)
            create = asyncio.create_subprocess_exec(
                *args,
                pita_fds={wfd},
            )
            proc = self.loop.run_until_complete(create)
            self.loop.run_until_complete(proc.wait())
        mwishowe:
            asyncio.set_child_watcher(Tupu)

        os.close(wfd)
        data = self.loop.run_until_complete(reader.read(-1))
        self.assertEqual(data, b'data')

    eleza test_streamreader_constructor(self):
        self.addCleanup(asyncio.set_event_loop, Tupu)
        asyncio.set_event_loop(self.loop)

        # asyncio issue #184: Ensure that StreamReaderProtocol constructor
        # retrieves the current loop ikiwa the loop parameter ni sio set
        reader = asyncio.StreamReader()
        self.assertIs(reader._loop, self.loop)

    eleza test_streamreaderprotocol_constructor(self):
        self.addCleanup(asyncio.set_event_loop, Tupu)
        asyncio.set_event_loop(self.loop)

        # asyncio issue #184: Ensure that StreamReaderProtocol constructor
        # retrieves the current loop ikiwa the loop parameter ni sio set
        reader = mock.Mock()
        protocol = asyncio.StreamReaderProtocol(reader)
        self.assertIs(protocol._loop, self.loop)

    eleza test_drain_raises(self):
        # See http://bugs.python.org/issue25441

        # This test should sio use asyncio kila the mock server; the
        # whole point of the test ni to test kila a bug kwenye drain()
        # where it never gives up the event loop but the socket is
        # closed on the  server side.

        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))
        q = queue.Queue()

        eleza server():
            # Runs kwenye a separate thread.
            ukijumuisha socket.create_server(('localhost', 0)) kama sock:
                addr = sock.getsockname()
                q.put(addr)
                clt, _ = sock.accept()
                clt.close()

        async eleza client(host, port):
            ukijumuisha self.assertWarns(DeprecationWarning):
                reader, writer = await asyncio.open_connection(
                    host, port, loop=self.loop)

            wakati Kweli:
                writer.write(b"foo\n")
                await writer.drain()

        # Start the server thread na wait kila it to be listening.
        thread = threading.Thread(target=server)
        thread.setDaemon(Kweli)
        thread.start()
        addr = q.get()

        # Should sio be stuck kwenye an infinite loop.
        ukijumuisha self.assertRaises((ConnectionResetError, ConnectionAbortedError,
                                BrokenPipeError)):
            self.loop.run_until_complete(client(*addr))

        # Clean up the thread.  (Only on success; on failure, it may
        # be stuck kwenye accept().)
        thread.join()
        self.assertEqual([], messages)

    eleza test___repr__(self):
        stream = asyncio.StreamReader(loop=self.loop)
        self.assertEqual("<StreamReader>", repr(stream))

    eleza test___repr__nondefault_limit(self):
        stream = asyncio.StreamReader(loop=self.loop, limit=123)
        self.assertEqual("<StreamReader limit=123>", repr(stream))

    eleza test___repr__eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_eof()
        self.assertEqual("<StreamReader eof>", repr(stream))

    eleza test___repr__data(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'data')
        self.assertEqual("<StreamReader 4 bytes>", repr(stream))

    eleza test___repr__exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        exc = RuntimeError()
        stream.set_exception(exc)
        self.assertEqual("<StreamReader exception=RuntimeError()>",
                         repr(stream))

    eleza test___repr__waiter(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream._waiter = asyncio.Future(loop=self.loop)
        self.assertRegex(
            repr(stream),
            r"<StreamReader waiter=<Future pending[\S ]*>>")
        stream._waiter.set_result(Tupu)
        self.loop.run_until_complete(stream._waiter)
        stream._waiter = Tupu
        self.assertEqual("<StreamReader>", repr(stream))

    eleza test___repr__transport(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream._transport = mock.Mock()
        stream._transport.__repr__ = mock.Mock()
        stream._transport.__repr__.return_value = "<Transport>"
        self.assertEqual("<StreamReader transport=<Transport>>", repr(stream))

    eleza test_IncompleteReadError_pickleable(self):
        e = asyncio.IncompleteReadError(b'abc', 10)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(pickle_protocol=proto):
                e2 = pickle.loads(pickle.dumps(e, protocol=proto))
                self.assertEqual(str(e), str(e2))
                self.assertEqual(e.partial, e2.partial)
                self.assertEqual(e.expected, e2.expected)

    eleza test_LimitOverrunError_pickleable(self):
        e = asyncio.LimitOverrunError('message', 10)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(pickle_protocol=proto):
                e2 = pickle.loads(pickle.dumps(e, protocol=proto))
                self.assertEqual(str(e), str(e2))
                self.assertEqual(e.consumed, e2.consumed)

    eleza test_wait_closed_on_close(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            ukijumuisha self.assertWarns(DeprecationWarning):
                rd, wr = self.loop.run_until_complete(
                    asyncio.open_connection(*httpd.address, loop=self.loop))

            wr.write(b'GET / HTTP/1.0\r\n\r\n')
            f = rd.readline()
            data = self.loop.run_until_complete(f)
            self.assertEqual(data, b'HTTP/1.0 200 OK\r\n')
            f = rd.read()
            data = self.loop.run_until_complete(f)
            self.assertKweli(data.endswith(b'\r\n\r\nTest message'))
            self.assertUongo(wr.is_closing())
            wr.close()
            self.assertKweli(wr.is_closing())
            self.loop.run_until_complete(wr.wait_closed())

    eleza test_wait_closed_on_close_with_unread_data(self):
        ukijumuisha test_utils.run_test_server() kama httpd:
            ukijumuisha self.assertWarns(DeprecationWarning):
                rd, wr = self.loop.run_until_complete(
                    asyncio.open_connection(*httpd.address, loop=self.loop))

            wr.write(b'GET / HTTP/1.0\r\n\r\n')
            f = rd.readline()
            data = self.loop.run_until_complete(f)
            self.assertEqual(data, b'HTTP/1.0 200 OK\r\n')
            wr.close()
            self.loop.run_until_complete(wr.wait_closed())

    eleza test_del_stream_before_sock_closing(self):
        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        ukijumuisha test_utils.run_test_server() kama httpd:
            ukijumuisha self.assertWarns(DeprecationWarning):
                rd, wr = self.loop.run_until_complete(
                    asyncio.open_connection(*httpd.address, loop=self.loop))
            sock = wr.get_extra_info('socket')
            self.assertNotEqual(sock.fileno(), -1)

            wr.write(b'GET / HTTP/1.0\r\n\r\n')
            f = rd.readline()
            data = self.loop.run_until_complete(f)
            self.assertEqual(data, b'HTTP/1.0 200 OK\r\n')

            # drop refs to reader/writer
            toa rd
            toa wr
            gc.collect()
            # make a chance to close the socket
            test_utils.run_briefly(self.loop)

            self.assertEqual(1, len(messages))
            self.assertEqual(sock.fileno(), -1)

        self.assertEqual(1, len(messages))
        self.assertEqual('An open stream object ni being garbage '
                         'collected; call "stream.close()" explicitly.',
                         messages[0]['message'])

    eleza test_del_stream_before_connection_made(self):
        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        ukijumuisha test_utils.run_test_server() kama httpd:
            rd = asyncio.StreamReader(loop=self.loop)
            pr = asyncio.StreamReaderProtocol(rd, loop=self.loop)
            toa rd
            gc.collect()
            tr, _ = self.loop.run_until_complete(
                self.loop.create_connection(
                    lambda: pr, *httpd.address))

            sock = tr.get_extra_info('socket')
            self.assertEqual(sock.fileno(), -1)

        self.assertEqual(1, len(messages))
        self.assertEqual('An open stream was garbage collected prior to '
                         'establishing network connection; '
                         'call "stream.close()" explicitly.',
                         messages[0]['message'])

    eleza test_async_writer_api(self):
        async eleza inner(httpd):
            rd, wr = await asyncio.open_connection(*httpd.address)

            wr.write(b'GET / HTTP/1.0\r\n\r\n')
            data = await rd.readline()
            self.assertEqual(data, b'HTTP/1.0 200 OK\r\n')
            data = await rd.read()
            self.assertKweli(data.endswith(b'\r\n\r\nTest message'))
            wr.close()
            await wr.wait_closed()

        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        ukijumuisha test_utils.run_test_server() kama httpd:
            self.loop.run_until_complete(inner(httpd))

        self.assertEqual(messages, [])

    eleza test_async_writer_api_exception_after_close(self):
        async eleza inner(httpd):
            rd, wr = await asyncio.open_connection(*httpd.address)

            wr.write(b'GET / HTTP/1.0\r\n\r\n')
            data = await rd.readline()
            self.assertEqual(data, b'HTTP/1.0 200 OK\r\n')
            data = await rd.read()
            self.assertKweli(data.endswith(b'\r\n\r\nTest message'))
            wr.close()
            ukijumuisha self.assertRaises(ConnectionResetError):
                wr.write(b'data')
                await wr.drain()

        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        ukijumuisha test_utils.run_test_server() kama httpd:
            self.loop.run_until_complete(inner(httpd))

        self.assertEqual(messages, [])

    eleza test_eof_feed_when_closing_writer(self):
        # See http://bugs.python.org/issue35065
        messages = []
        self.loop.set_exception_handler(lambda loop, ctx: messages.append(ctx))

        ukijumuisha test_utils.run_test_server() kama httpd:
            ukijumuisha self.assertWarns(DeprecationWarning):
                rd, wr = self.loop.run_until_complete(
                    asyncio.open_connection(*httpd.address,
                                            loop=self.loop))

            wr.close()
            f = wr.wait_closed()
            self.loop.run_until_complete(f)
            assert rd.at_eof()
            f = rd.read()
            data = self.loop.run_until_complete(f)
            assert data == b''

        self.assertEqual(messages, [])


ikiwa __name__ == '__main__':
    unittest.main()
