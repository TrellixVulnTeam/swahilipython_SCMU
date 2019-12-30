# test asynchat

kutoka test agiza support

agiza asynchat
agiza asyncore
agiza errno
agiza socket
agiza sys
agiza threading
agiza time
agiza unittest
agiza unittest.mock

HOST = support.HOST
SERVER_QUIT = b'QUIT\n'
TIMEOUT = 3.0


kundi echo_server(threading.Thread):
    # parameter to determine the number of bytes pitaed back to the
    # client each send
    chunk_size = 1

    eleza __init__(self, event):
        threading.Thread.__init__(self)
        self.event = event
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = support.bind_port(self.sock)
        # This will be set ikiwa the client wants us to wait before echoing
        # data back.
        self.start_resend_event = Tupu

    eleza run(self):
        self.sock.listen()
        self.event.set()
        conn, client = self.sock.accept()
        self.buffer = b""
        # collect data until quit message ni seen
        wakati SERVER_QUIT haiko kwenye self.buffer:
            data = conn.recv(1)
            ikiwa sio data:
                koma
            self.buffer = self.buffer + data

        # remove the SERVER_QUIT message
        self.buffer = self.buffer.replace(SERVER_QUIT, b'')

        ikiwa self.start_resend_event:
            self.start_resend_event.wait()

        # re-send entire set of collected data
        jaribu:
            # this may fail on some tests, such kama test_close_when_done,
            # since the client closes the channel when it's done sending
            wakati self.buffer:
                n = conn.send(self.buffer[:self.chunk_size])
                time.sleep(0.001)
                self.buffer = self.buffer[n:]
        tatizo:
            pita

        conn.close()
        self.sock.close()

kundi echo_client(asynchat.async_chat):

    eleza __init__(self, terminator, server_port):
        asynchat.async_chat.__init__(self)
        self.contents = []
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((HOST, server_port))
        self.set_terminator(terminator)
        self.buffer = b""

        eleza handle_connect(self):
            pita

        ikiwa sys.platform == 'darwin':
            # select.poll rudishas a select.POLLHUP at the end of the tests
            # on darwin, so just ignore it
            eleza handle_expt(self):
                pita

    eleza collect_incoming_data(self, data):
        self.buffer += data

    eleza found_terminator(self):
        self.contents.append(self.buffer)
        self.buffer = b""

eleza start_echo_server():
    event = threading.Event()
    s = echo_server(event)
    s.start()
    event.wait()
    event.clear()
    time.sleep(0.01)   # Give server time to start accepting.
    rudisha s, event


kundi TestAsynchat(unittest.TestCase):
    usepoll = Uongo

    eleza setUp(self):
        self._threads = support.threading_setup()

    eleza tearDown(self):
        support.threading_cleanup(*self._threads)

    eleza line_terminator_check(self, term, server_chunk):
        event = threading.Event()
        s = echo_server(event)
        s.chunk_size = server_chunk
        s.start()
        event.wait()
        event.clear()
        time.sleep(0.01)   # Give server time to start accepting.
        c = echo_client(term, s.port)
        c.push(b"hello ")
        c.push(b"world" + term)
        c.push(b"I'm sio dead yet!" + term)
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        support.join_thread(s, timeout=TIMEOUT)

        self.assertEqual(c.contents, [b"hello world", b"I'm sio dead yet!"])

    # the line terminator tests below check receiving variously-sized
    # chunks back kutoka the server kwenye order to exercise all branches of
    # async_chat.handle_read

    eleza test_line_terminator1(self):
        # test one-character terminator
        kila l kwenye (1, 2, 3):
            self.line_terminator_check(b'\n', l)

    eleza test_line_terminator2(self):
        # test two-character terminator
        kila l kwenye (1, 2, 3):
            self.line_terminator_check(b'\r\n', l)

    eleza test_line_terminator3(self):
        # test three-character terminator
        kila l kwenye (1, 2, 3):
            self.line_terminator_check(b'qqq', l)

    eleza numeric_terminator_check(self, termlen):
        # Try reading a fixed number of bytes
        s, event = start_echo_server()
        c = echo_client(termlen, s.port)
        data = b"hello world, I'm sio dead yet!\n"
        c.push(data)
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        support.join_thread(s, timeout=TIMEOUT)

        self.assertEqual(c.contents, [data[:termlen]])

    eleza test_numeric_terminator1(self):
        # check that ints & longs both work (since type is
        # explicitly checked kwenye async_chat.handle_read)
        self.numeric_terminator_check(1)

    eleza test_numeric_terminator2(self):
        self.numeric_terminator_check(6)

    eleza test_none_terminator(self):
        # Try reading a fixed number of bytes
        s, event = start_echo_server()
        c = echo_client(Tupu, s.port)
        data = b"hello world, I'm sio dead yet!\n"
        c.push(data)
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        support.join_thread(s, timeout=TIMEOUT)

        self.assertEqual(c.contents, [])
        self.assertEqual(c.buffer, data)

    eleza test_simple_producer(self):
        s, event = start_echo_server()
        c = echo_client(b'\n', s.port)
        data = b"hello world\nI'm sio dead yet!\n"
        p = asynchat.simple_producer(data+SERVER_QUIT, buffer_size=8)
        c.push_with_producer(p)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        support.join_thread(s, timeout=TIMEOUT)

        self.assertEqual(c.contents, [b"hello world", b"I'm sio dead yet!"])

    eleza test_string_producer(self):
        s, event = start_echo_server()
        c = echo_client(b'\n', s.port)
        data = b"hello world\nI'm sio dead yet!\n"
        c.push_with_producer(data+SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        support.join_thread(s, timeout=TIMEOUT)

        self.assertEqual(c.contents, [b"hello world", b"I'm sio dead yet!"])

    eleza test_empty_line(self):
        # checks that empty lines are handled correctly
        s, event = start_echo_server()
        c = echo_client(b'\n', s.port)
        c.push(b"hello world\n\nI'm sio dead yet!\n")
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        support.join_thread(s, timeout=TIMEOUT)

        self.assertEqual(c.contents,
                         [b"hello world", b"", b"I'm sio dead yet!"])

    eleza test_close_when_done(self):
        s, event = start_echo_server()
        s.start_resend_event = threading.Event()
        c = echo_client(b'\n', s.port)
        c.push(b"hello world\nI'm sio dead yet!\n")
        c.push(SERVER_QUIT)
        c.close_when_done()
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)

        # Only allow the server to start echoing data back to the client after
        # the client has closed its connection.  This prevents a race condition
        # where the server echoes all of its data before we can check that it
        # got any down below.
        s.start_resend_event.set()
        support.join_thread(s, timeout=TIMEOUT)

        self.assertEqual(c.contents, [])
        # the server might have been able to send a byte ama two back, but this
        # at least checks that it received something na didn't just fail
        # (which could still result kwenye the client sio having received anything)
        self.assertGreater(len(s.buffer), 0)

    eleza test_push(self):
        # Issue #12523: push() should ashiria a TypeError ikiwa it doesn't get
        # a bytes string
        s, event = start_echo_server()
        c = echo_client(b'\n', s.port)
        data = b'bytes\n'
        c.push(data)
        c.push(bytearray(data))
        c.push(memoryview(data))
        self.assertRaises(TypeError, c.push, 10)
        self.assertRaises(TypeError, c.push, 'unicode')
        c.push(SERVER_QUIT)
        asyncore.loop(use_poll=self.usepoll, count=300, timeout=.01)
        support.join_thread(s, timeout=TIMEOUT)
        self.assertEqual(c.contents, [b'bytes', b'bytes', b'bytes'])


kundi TestAsynchat_WithPoll(TestAsynchat):
    usepoll = Kweli


kundi TestAsynchatMocked(unittest.TestCase):
    eleza test_blockingioerror(self):
        # Issue #16133: handle_read() must ignore BlockingIOError
        sock = unittest.mock.Mock()
        sock.recv.side_effect = BlockingIOError(errno.EAGAIN)

        dispatcher = asynchat.async_chat()
        dispatcher.set_socket(sock)
        self.addCleanup(dispatcher.del_channel)

        ukijumuisha unittest.mock.patch.object(dispatcher, 'handle_error') kama error:
            dispatcher.handle_read()
        self.assertUongo(error.called)


kundi TestHelperFunctions(unittest.TestCase):
    eleza test_find_prefix_at_end(self):
        self.assertEqual(asynchat.find_prefix_at_end("qwerty\r", "\r\n"), 1)
        self.assertEqual(asynchat.find_prefix_at_end("qwertydkjf", "\r\n"), 0)


kundi TestNotConnected(unittest.TestCase):
    eleza test_disallow_negative_terminator(self):
        # Issue #11259
        client = asynchat.async_chat()
        self.assertRaises(ValueError, client.set_terminator, -1)



ikiwa __name__ == "__main__":
    unittest.main()
