agiza asyncore
agiza unittest
agiza select
agiza os
agiza socket
agiza sys
agiza time
agiza errno
agiza struct
agiza threading

kutoka test agiza support
kutoka io agiza BytesIO

ikiwa support.PGO:
    ashiria unittest.SkipTest("test ni sio helpful kila PGO")


TIMEOUT = 3
HAS_UNIX_SOCKETS = hasattr(socket, 'AF_UNIX')

kundi dummysocket:
    eleza __init__(self):
        self.closed = Uongo

    eleza close(self):
        self.closed = Kweli

    eleza fileno(self):
        rudisha 42

kundi dummychannel:
    eleza __init__(self):
        self.socket = dummysocket()

    eleza close(self):
        self.socket.close()

kundi exitingdummy:
    eleza __init__(self):
        pita

    eleza handle_read_event(self):
        ashiria asyncore.ExitNow()

    handle_write_event = handle_read_event
    handle_close = handle_read_event
    handle_expt_event = handle_read_event

kundi crashingdummy:
    eleza __init__(self):
        self.error_handled = Uongo

    eleza handle_read_event(self):
        ashiria Exception()

    handle_write_event = handle_read_event
    handle_close = handle_read_event
    handle_expt_event = handle_read_event

    eleza handle_error(self):
        self.error_handled = Kweli

# used when testing senders; just collects what it gets until newline ni sent
eleza capture_server(evt, buf, serv):
    jaribu:
        serv.listen()
        conn, addr = serv.accept()
    tatizo socket.timeout:
        pita
    isipokua:
        n = 200
        start = time.monotonic()
        wakati n > 0 na time.monotonic() - start < 3.0:
            r, w, e = select.select([conn], [], [], 0.1)
            ikiwa r:
                n -= 1
                data = conn.recv(10)
                # keep everything tatizo kila the newline terminator
                buf.write(data.replace(b'\n', b''))
                ikiwa b'\n' kwenye data:
                    koma
            time.sleep(0.01)

        conn.close()
    mwishowe:
        serv.close()
        evt.set()

eleza bind_af_aware(sock, addr):
    """Helper function to bind a socket according to its family."""
    ikiwa HAS_UNIX_SOCKETS na sock.family == socket.AF_UNIX:
        # Make sure the path doesn't exist.
        support.unlink(addr)
        support.bind_unix_socket(sock, addr)
    isipokua:
        sock.bind(addr)


kundi HelperFunctionTests(unittest.TestCase):
    eleza test_readwriteexc(self):
        # Check exception handling behavior of read, write na _exception

        # check that ExitNow exceptions kwenye the object handler method
        # bubbles all the way up through asyncore read/write/_exception calls
        tr1 = exitingdummy()
        self.assertRaises(asyncore.ExitNow, asyncore.read, tr1)
        self.assertRaises(asyncore.ExitNow, asyncore.write, tr1)
        self.assertRaises(asyncore.ExitNow, asyncore._exception, tr1)

        # check that an exception other than ExitNow kwenye the object handler
        # method causes the handle_error method to get called
        tr2 = crashingdummy()
        asyncore.read(tr2)
        self.assertEqual(tr2.error_handled, Kweli)

        tr2 = crashingdummy()
        asyncore.write(tr2)
        self.assertEqual(tr2.error_handled, Kweli)

        tr2 = crashingdummy()
        asyncore._exception(tr2)
        self.assertEqual(tr2.error_handled, Kweli)

    # asyncore.readwrite uses constants kwenye the select module that
    # are sio present kwenye Windows systems (see this thread:
    # http://mail.python.org/pipermail/python-list/2001-October/109973.html)
    # These constants should be present kama long kama poll ni available

    @unittest.skipUnless(hasattr(select, 'poll'), 'select.poll required')
    eleza test_readwrite(self):
        # Check that correct methods are called by readwrite()

        attributes = ('read', 'expt', 'write', 'closed', 'error_handled')

        expected = (
            (select.POLLIN, 'read'),
            (select.POLLPRI, 'expt'),
            (select.POLLOUT, 'write'),
            (select.POLLERR, 'closed'),
            (select.POLLHUP, 'closed'),
            (select.POLLNVAL, 'closed'),
            )

        kundi testobj:
            eleza __init__(self):
                self.read = Uongo
                self.write = Uongo
                self.closed = Uongo
                self.expt = Uongo
                self.error_handled = Uongo

            eleza handle_read_event(self):
                self.read = Kweli

            eleza handle_write_event(self):
                self.write = Kweli

            eleza handle_close(self):
                self.closed = Kweli

            eleza handle_expt_event(self):
                self.expt = Kweli

            eleza handle_error(self):
                self.error_handled = Kweli

        kila flag, expectedattr kwenye expected:
            tobj = testobj()
            self.assertEqual(getattr(tobj, expectedattr), Uongo)
            asyncore.readwrite(tobj, flag)

            # Only the attribute modified by the routine we expect to be
            # called should be Kweli.
            kila attr kwenye attributes:
                self.assertEqual(getattr(tobj, attr), attr==expectedattr)

            # check that ExitNow exceptions kwenye the object handler method
            # bubbles all the way up through asyncore readwrite call
            tr1 = exitingdummy()
            self.assertRaises(asyncore.ExitNow, asyncore.readwrite, tr1, flag)

            # check that an exception other than ExitNow kwenye the object handler
            # method causes the handle_error method to get called
            tr2 = crashingdummy()
            self.assertEqual(tr2.error_handled, Uongo)
            asyncore.readwrite(tr2, flag)
            self.assertEqual(tr2.error_handled, Kweli)

    eleza test_closeall(self):
        self.closeall_check(Uongo)

    eleza test_closeall_default(self):
        self.closeall_check(Kweli)

    eleza closeall_check(self, usedefault):
        # Check that close_all() closes everything kwenye a given map

        l = []
        testmap = {}
        kila i kwenye range(10):
            c = dummychannel()
            l.append(c)
            self.assertEqual(c.socket.closed, Uongo)
            testmap[i] = c

        ikiwa usedefault:
            socketmap = asyncore.socket_map
            jaribu:
                asyncore.socket_map = testmap
                asyncore.close_all()
            mwishowe:
                testmap, asyncore.socket_map = asyncore.socket_map, socketmap
        isipokua:
            asyncore.close_all(testmap)

        self.assertEqual(len(testmap), 0)

        kila c kwenye l:
            self.assertEqual(c.socket.closed, Kweli)

    eleza test_compact_traceback(self):
        jaribu:
            ashiria Exception("I don't like spam!")
        tatizo:
            real_t, real_v, real_tb = sys.exc_info()
            r = asyncore.compact_traceback()
        isipokua:
            self.fail("Expected exception")

        (f, function, line), t, v, info = r
        self.assertEqual(os.path.split(f)[-1], 'test_asyncore.py')
        self.assertEqual(function, 'test_compact_traceback')
        self.assertEqual(t, real_t)
        self.assertEqual(v, real_v)
        self.assertEqual(info, '[%s|%s|%s]' % (f, function, line))


kundi DispatcherTests(unittest.TestCase):
    eleza setUp(self):
        pita

    eleza tearDown(self):
        asyncore.close_all()

    eleza test_basic(self):
        d = asyncore.dispatcher()
        self.assertEqual(d.readable(), Kweli)
        self.assertEqual(d.writable(), Kweli)

    eleza test_repr(self):
        d = asyncore.dispatcher()
        self.assertEqual(repr(d), '<asyncore.dispatcher at %#x>' % id(d))

    eleza test_log(self):
        d = asyncore.dispatcher()

        # capture output of dispatcher.log() (to stderr)
        l1 = "Lovely spam! Wonderful spam!"
        l2 = "I don't like spam!"
        ukijumuisha support.captured_stderr() kama stderr:
            d.log(l1)
            d.log(l2)

        lines = stderr.getvalue().splitlines()
        self.assertEqual(lines, ['log: %s' % l1, 'log: %s' % l2])

    eleza test_log_info(self):
        d = asyncore.dispatcher()

        # capture output of dispatcher.log_info() (to stdout via print)
        l1 = "Have you got anything without spam?"
        l2 = "Why can't she have egg bacon spam na sausage?"
        l3 = "THAT'S got spam kwenye it!"
        ukijumuisha support.captured_stdout() kama stdout:
            d.log_info(l1, 'EGGS')
            d.log_info(l2)
            d.log_info(l3, 'SPAM')

        lines = stdout.getvalue().splitlines()
        expected = ['EGGS: %s' % l1, 'info: %s' % l2, 'SPAM: %s' % l3]
        self.assertEqual(lines, expected)

    eleza test_unhandled(self):
        d = asyncore.dispatcher()
        d.ignore_log_types = ()

        # capture output of dispatcher.log_info() (to stdout via print)
        ukijumuisha support.captured_stdout() kama stdout:
            d.handle_expt()
            d.handle_read()
            d.handle_write()
            d.handle_connect()

        lines = stdout.getvalue().splitlines()
        expected = ['warning: unhandled incoming priority event',
                    'warning: unhandled read event',
                    'warning: unhandled write event',
                    'warning: unhandled connect event']
        self.assertEqual(lines, expected)

    eleza test_strerror(self):
        # refers to bug #8573
        err = asyncore._strerror(errno.EPERM)
        ikiwa hasattr(os, 'strerror'):
            self.assertEqual(err, os.strerror(errno.EPERM))
        err = asyncore._strerror(-1)
        self.assertKweli(err != "")


kundi dispatcherwithsend_noread(asyncore.dispatcher_with_send):
    eleza readable(self):
        rudisha Uongo

    eleza handle_connect(self):
        pita


kundi DispatcherWithSendTests(unittest.TestCase):
    eleza setUp(self):
        pita

    eleza tearDown(self):
        asyncore.close_all()

    @support.reap_threads
    eleza test_send(self):
        evt = threading.Event()
        sock = socket.socket()
        sock.settimeout(3)
        port = support.bind_port(sock)

        cap = BytesIO()
        args = (evt, cap, sock)
        t = threading.Thread(target=capture_server, args=args)
        t.start()
        jaribu:
            # wait a little longer kila the server to initialize (it sometimes
            # refuses connections on slow machines without this wait)
            time.sleep(0.2)

            data = b"Suppose there isn't a 16-ton weight?"
            d = dispatcherwithsend_noread()
            d.create_socket()
            d.connect((support.HOST, port))

            # give time kila socket to connect
            time.sleep(0.1)

            d.send(data)
            d.send(data)
            d.send(b'\n')

            n = 1000
            wakati d.out_buffer na n > 0:
                asyncore.poll()
                n -= 1

            evt.wait()

            self.assertEqual(cap.getvalue(), data*2)
        mwishowe:
            support.join_thread(t, timeout=TIMEOUT)


@unittest.skipUnless(hasattr(asyncore, 'file_wrapper'),
                     'asyncore.file_wrapper required')
kundi FileWrapperTest(unittest.TestCase):
    eleza setUp(self):
        self.d = b"It's sio dead, it's sleeping!"
        ukijumuisha open(support.TESTFN, 'wb') kama file:
            file.write(self.d)

    eleza tearDown(self):
        support.unlink(support.TESTFN)

    eleza test_recv(self):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        w = asyncore.file_wrapper(fd)
        os.close(fd)

        self.assertNotEqual(w.fd, fd)
        self.assertNotEqual(w.fileno(), fd)
        self.assertEqual(w.recv(13), b"It's sio dead")
        self.assertEqual(w.read(6), b", it's")
        w.close()
        self.assertRaises(OSError, w.read, 1)

    eleza test_send(self):
        d1 = b"Come again?"
        d2 = b"I want to buy some cheese."
        fd = os.open(support.TESTFN, os.O_WRONLY | os.O_APPEND)
        w = asyncore.file_wrapper(fd)
        os.close(fd)

        w.write(d1)
        w.send(d2)
        w.close()
        ukijumuisha open(support.TESTFN, 'rb') kama file:
            self.assertEqual(file.read(), self.d + d1 + d2)

    @unittest.skipUnless(hasattr(asyncore, 'file_dispatcher'),
                         'asyncore.file_dispatcher required')
    eleza test_dispatcher(self):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        data = []
        kundi FileDispatcher(asyncore.file_dispatcher):
            eleza handle_read(self):
                data.append(self.recv(29))
        s = FileDispatcher(fd)
        os.close(fd)
        asyncore.loop(timeout=0.01, use_poll=Kweli, count=2)
        self.assertEqual(b"".join(data), self.d)

    eleza test_resource_warning(self):
        # Issue #11453
        fd = os.open(support.TESTFN, os.O_RDONLY)
        f = asyncore.file_wrapper(fd)

        os.close(fd)
        ukijumuisha support.check_warnings(('', ResourceWarning)):
            f = Tupu
            support.gc_collect()

    eleza test_close_twice(self):
        fd = os.open(support.TESTFN, os.O_RDONLY)
        f = asyncore.file_wrapper(fd)
        os.close(fd)

        os.close(f.fd)  # file_wrapper dupped fd
        ukijumuisha self.assertRaises(OSError):
            f.close()

        self.assertEqual(f.fd, -1)
        # calling close twice should sio fail
        f.close()


kundi BaseTestHandler(asyncore.dispatcher):

    eleza __init__(self, sock=Tupu):
        asyncore.dispatcher.__init__(self, sock)
        self.flag = Uongo

    eleza handle_accept(self):
        ashiria Exception("handle_accept sio supposed to be called")

    eleza handle_accepted(self):
        ashiria Exception("handle_accepted sio supposed to be called")

    eleza handle_connect(self):
        ashiria Exception("handle_connect sio supposed to be called")

    eleza handle_expt(self):
        ashiria Exception("handle_expt sio supposed to be called")

    eleza handle_close(self):
        ashiria Exception("handle_close sio supposed to be called")

    eleza handle_error(self):
        raise


kundi BaseServer(asyncore.dispatcher):
    """A server which listens on an address na dispatches the
    connection to a handler.
    """

    eleza __init__(self, family, addr, handler=BaseTestHandler):
        asyncore.dispatcher.__init__(self)
        self.create_socket(family)
        self.set_reuse_addr()
        bind_af_aware(self.socket, addr)
        self.listen(5)
        self.handler = handler

    @property
    eleza address(self):
        rudisha self.socket.getsockname()

    eleza handle_accepted(self, sock, addr):
        self.handler(sock)

    eleza handle_error(self):
        raise


kundi BaseClient(BaseTestHandler):

    eleza __init__(self, family, address):
        BaseTestHandler.__init__(self)
        self.create_socket(family)
        self.connect(address)

    eleza handle_connect(self):
        pita


kundi BaseTestAPI:

    eleza tearDown(self):
        asyncore.close_all(ignore_all=Kweli)

    eleza loop_waiting_for_flag(self, instance, timeout=5):
        timeout = float(timeout) / 100
        count = 100
        wakati asyncore.socket_map na count > 0:
            asyncore.loop(timeout=0.01, count=1, use_poll=self.use_poll)
            ikiwa instance.flag:
                rudisha
            count -= 1
            time.sleep(timeout)
        self.fail("flag sio set")

    eleza test_handle_connect(self):
        # make sure handle_connect ni called on connect()

        kundi TestClient(BaseClient):
            eleza handle_connect(self):
                self.flag = Kweli

        server = BaseServer(self.family, self.addr)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    eleza test_handle_accept(self):
        # make sure handle_accept() ni called when a client connects

        kundi TestListener(BaseTestHandler):

            eleza __init__(self, family, addr):
                BaseTestHandler.__init__(self)
                self.create_socket(family)
                bind_af_aware(self.socket, addr)
                self.listen(5)
                self.address = self.socket.getsockname()

            eleza handle_accept(self):
                self.flag = Kweli

        server = TestListener(self.family, self.addr)
        client = BaseClient(self.family, server.address)
        self.loop_waiting_for_flag(server)

    eleza test_handle_accepted(self):
        # make sure handle_accepted() ni called when a client connects

        kundi TestListener(BaseTestHandler):

            eleza __init__(self, family, addr):
                BaseTestHandler.__init__(self)
                self.create_socket(family)
                bind_af_aware(self.socket, addr)
                self.listen(5)
                self.address = self.socket.getsockname()

            eleza handle_accept(self):
                asyncore.dispatcher.handle_accept(self)

            eleza handle_accepted(self, sock, addr):
                sock.close()
                self.flag = Kweli

        server = TestListener(self.family, self.addr)
        client = BaseClient(self.family, server.address)
        self.loop_waiting_for_flag(server)


    eleza test_handle_read(self):
        # make sure handle_read ni called on data received

        kundi TestClient(BaseClient):
            eleza handle_read(self):
                self.flag = Kweli

        kundi TestHandler(BaseTestHandler):
            eleza __init__(self, conn):
                BaseTestHandler.__init__(self, conn)
                self.send(b'x' * 1024)

        server = BaseServer(self.family, self.addr, TestHandler)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    eleza test_handle_write(self):
        # make sure handle_write ni called

        kundi TestClient(BaseClient):
            eleza handle_write(self):
                self.flag = Kweli

        server = BaseServer(self.family, self.addr)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    eleza test_handle_close(self):
        # make sure handle_close ni called when the other end closes
        # the connection

        kundi TestClient(BaseClient):

            eleza handle_read(self):
                # kwenye order to make handle_close be called we are supposed
                # to make at least one recv() call
                self.recv(1024)

            eleza handle_close(self):
                self.flag = Kweli
                self.close()

        kundi TestHandler(BaseTestHandler):
            eleza __init__(self, conn):
                BaseTestHandler.__init__(self, conn)
                self.close()

        server = BaseServer(self.family, self.addr, TestHandler)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    eleza test_handle_close_after_conn_broken(self):
        # Check that ECONNRESET/EPIPE ni correctly handled (issues #5661 na
        # #11265).

        data = b'\0' * 128

        kundi TestClient(BaseClient):

            eleza handle_write(self):
                self.send(data)

            eleza handle_close(self):
                self.flag = Kweli
                self.close()

            eleza handle_expt(self):
                self.flag = Kweli
                self.close()

        kundi TestHandler(BaseTestHandler):

            eleza handle_read(self):
                self.recv(len(data))
                self.close()

            eleza writable(self):
                rudisha Uongo

        server = BaseServer(self.family, self.addr, TestHandler)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    @unittest.skipIf(sys.platform.startswith("sunos"),
                     "OOB support ni broken on Solaris")
    eleza test_handle_expt(self):
        # Make sure handle_expt ni called on OOB data received.
        # Note: this might fail on some platforms kama OOB data is
        # tenuously supported na rarely used.
        ikiwa HAS_UNIX_SOCKETS na self.family == socket.AF_UNIX:
            self.skipTest("Not applicable to AF_UNIX sockets.")

        ikiwa sys.platform == "darwin" na self.use_poll:
            self.skipTest("poll may fail on macOS; see issue #28087")

        kundi TestClient(BaseClient):
            eleza handle_expt(self):
                self.socket.recv(1024, socket.MSG_OOB)
                self.flag = Kweli

        kundi TestHandler(BaseTestHandler):
            eleza __init__(self, conn):
                BaseTestHandler.__init__(self, conn)
                self.socket.send(bytes(chr(244), 'latin-1'), socket.MSG_OOB)

        server = BaseServer(self.family, self.addr, TestHandler)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    eleza test_handle_error(self):

        kundi TestClient(BaseClient):
            eleza handle_write(self):
                1.0 / 0
            eleza handle_error(self):
                self.flag = Kweli
                jaribu:
                    raise
                tatizo ZeroDivisionError:
                    pita
                isipokua:
                    ashiria Exception("exception sio raised")

        server = BaseServer(self.family, self.addr)
        client = TestClient(self.family, server.address)
        self.loop_waiting_for_flag(client)

    eleza test_connection_attributes(self):
        server = BaseServer(self.family, self.addr)
        client = BaseClient(self.family, server.address)

        # we start disconnected
        self.assertUongo(server.connected)
        self.assertKweli(server.accepting)
        # this can't be taken kila granted across all platforms
        #self.assertUongo(client.connected)
        self.assertUongo(client.accepting)

        # execute some loops so that client connects to server
        asyncore.loop(timeout=0.01, use_poll=self.use_poll, count=100)
        self.assertUongo(server.connected)
        self.assertKweli(server.accepting)
        self.assertKweli(client.connected)
        self.assertUongo(client.accepting)

        # disconnect the client
        client.close()
        self.assertUongo(server.connected)
        self.assertKweli(server.accepting)
        self.assertUongo(client.connected)
        self.assertUongo(client.accepting)

        # stop serving
        server.close()
        self.assertUongo(server.connected)
        self.assertUongo(server.accepting)

    eleza test_create_socket(self):
        s = asyncore.dispatcher()
        s.create_socket(self.family)
        self.assertEqual(s.socket.type, socket.SOCK_STREAM)
        self.assertEqual(s.socket.family, self.family)
        self.assertEqual(s.socket.gettimeout(), 0)
        self.assertUongo(s.socket.get_inheritable())

    eleza test_bind(self):
        ikiwa HAS_UNIX_SOCKETS na self.family == socket.AF_UNIX:
            self.skipTest("Not applicable to AF_UNIX sockets.")
        s1 = asyncore.dispatcher()
        s1.create_socket(self.family)
        s1.bind(self.addr)
        s1.listen(5)
        port = s1.socket.getsockname()[1]

        s2 = asyncore.dispatcher()
        s2.create_socket(self.family)
        # EADDRINUSE indicates the socket was correctly bound
        self.assertRaises(OSError, s2.bind, (self.addr[0], port))

    eleza test_set_reuse_addr(self):
        ikiwa HAS_UNIX_SOCKETS na self.family == socket.AF_UNIX:
            self.skipTest("Not applicable to AF_UNIX sockets.")

        ukijumuisha socket.socket(self.family) kama sock:
            jaribu:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tatizo OSError:
                unittest.skip("SO_REUSEADDR sio supported on this platform")
            isipokua:
                # ikiwa SO_REUSEADDR succeeded kila sock we expect asyncore
                # to do the same
                s = asyncore.dispatcher(socket.socket(self.family))
                self.assertUongo(s.socket.getsockopt(socket.SOL_SOCKET,
                                                     socket.SO_REUSEADDR))
                s.socket.close()
                s.create_socket(self.family)
                s.set_reuse_addr()
                self.assertKweli(s.socket.getsockopt(socket.SOL_SOCKET,
                                                     socket.SO_REUSEADDR))

    @support.reap_threads
    eleza test_quick_connect(self):
        # see: http://bugs.python.org/issue10340
        ikiwa self.family haiko kwenye (socket.AF_INET, getattr(socket, "AF_INET6", object())):
            self.skipTest("test specific to AF_INET na AF_INET6")

        server = BaseServer(self.family, self.addr)
        # run the thread 500 ms: the socket should be connected kwenye 200 ms
        t = threading.Thread(target=lambda: asyncore.loop(timeout=0.1,
                                                          count=5))
        t.start()
        jaribu:
            ukijumuisha socket.socket(self.family, socket.SOCK_STREAM) kama s:
                s.settimeout(.2)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                             struct.pack('ii', 1, 0))

                jaribu:
                    s.connect(server.address)
                tatizo OSError:
                    pita
        mwishowe:
            support.join_thread(t, timeout=TIMEOUT)

kundi TestAPI_UseIPv4Sockets(BaseTestAPI):
    family = socket.AF_INET
    addr = (support.HOST, 0)

@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 support required')
kundi TestAPI_UseIPv6Sockets(BaseTestAPI):
    family = socket.AF_INET6
    addr = (support.HOSTv6, 0)

@unittest.skipUnless(HAS_UNIX_SOCKETS, 'Unix sockets required')
kundi TestAPI_UseUnixSockets(BaseTestAPI):
    ikiwa HAS_UNIX_SOCKETS:
        family = socket.AF_UNIX
    addr = support.TESTFN

    eleza tearDown(self):
        support.unlink(self.addr)
        BaseTestAPI.tearDown(self)

kundi TestAPI_UseIPv4Select(TestAPI_UseIPv4Sockets, unittest.TestCase):
    use_poll = Uongo

@unittest.skipUnless(hasattr(select, 'poll'), 'select.poll required')
kundi TestAPI_UseIPv4Poll(TestAPI_UseIPv4Sockets, unittest.TestCase):
    use_poll = Kweli

kundi TestAPI_UseIPv6Select(TestAPI_UseIPv6Sockets, unittest.TestCase):
    use_poll = Uongo

@unittest.skipUnless(hasattr(select, 'poll'), 'select.poll required')
kundi TestAPI_UseIPv6Poll(TestAPI_UseIPv6Sockets, unittest.TestCase):
    use_poll = Kweli

kundi TestAPI_UseUnixSocketsSelect(TestAPI_UseUnixSockets, unittest.TestCase):
    use_poll = Uongo

@unittest.skipUnless(hasattr(select, 'poll'), 'select.poll required')
kundi TestAPI_UseUnixSocketsPoll(TestAPI_UseUnixSockets, unittest.TestCase):
    use_poll = Kweli

ikiwa __name__ == "__main__":
    unittest.main()
