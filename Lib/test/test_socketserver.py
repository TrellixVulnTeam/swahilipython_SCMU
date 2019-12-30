"""
Test suite kila socketserver.
"""

agiza contextlib
agiza io
agiza os
agiza select
agiza signal
agiza socket
agiza tempfile
agiza threading
agiza unittest
agiza socketserver

agiza test.support
kutoka test.support agiza reap_children, reap_threads, verbose


test.support.requires("network")

TEST_STR = b"hello world\n"
HOST = test.support.HOST

HAVE_UNIX_SOCKETS = hasattr(socket, "AF_UNIX")
requires_unix_sockets = unittest.skipUnless(HAVE_UNIX_SOCKETS,
                                            'requires Unix sockets')
HAVE_FORKING = hasattr(os, "fork")
requires_forking = unittest.skipUnless(HAVE_FORKING, 'requires forking')

eleza signal_alarm(n):
    """Call signal.alarm when it exists (i.e. sio on Windows)."""
    ikiwa hasattr(signal, 'alarm'):
        signal.alarm(n)

# Remember real select() to avoid interferences ukijumuisha mocking
_real_select = select.select

eleza receive(sock, n, timeout=20):
    r, w, x = _real_select([sock], [], [], timeout)
    ikiwa sock kwenye r:
        rudisha sock.recv(n)
    isipokua:
         ashiria RuntimeError("timed out on %r" % (sock,))

ikiwa HAVE_UNIX_SOCKETS na HAVE_FORKING:
    kundi ForkingUnixStreamServer(socketserver.ForkingMixIn,
                                  socketserver.UnixStreamServer):
        pass

    kundi ForkingUnixDatagramServer(socketserver.ForkingMixIn,
                                    socketserver.UnixDatagramServer):
        pass


@contextlib.contextmanager
eleza simple_subprocess(testcase):
    """Tests that a custom child process ni sio waited on (Issue 1540386)"""
    pid = os.fork()
    ikiwa pid == 0:
        # Don't  ashiria an exception; it would be caught by the test harness.
        os._exit(72)
    jaribu:
        tuma Tupu
    tatizo:
        raise
    mwishowe:
        pid2, status = os.waitpid(pid, 0)
        testcase.assertEqual(pid2, pid)
        testcase.assertEqual(72 << 8, status)


kundi SocketServerTest(unittest.TestCase):
    """Test all socket servers."""

    eleza setUp(self):
        signal_alarm(60)  # Kill deadlocks after 60 seconds.
        self.port_seed = 0
        self.test_files = []

    eleza tearDown(self):
        signal_alarm(0)  # Didn't deadlock.
        reap_children()

        kila fn kwenye self.test_files:
            jaribu:
                os.remove(fn)
            except OSError:
                pass
        self.test_files[:] = []

    eleza pickaddr(self, proto):
        ikiwa proto == socket.AF_INET:
            rudisha (HOST, 0)
        isipokua:
            # XXX: We need a way to tell AF_UNIX to pick its own name
            # like AF_INET provides port==0.
            dir = Tupu
            fn = tempfile.mktemp(prefix='unix_socket.', dir=dir)
            self.test_files.append(fn)
            rudisha fn

    eleza make_server(self, addr, svrcls, hdlrbase):
        kundi MyServer(svrcls):
            eleza handle_error(self, request, client_address):
                self.close_request(request)
                raise

        kundi MyHandler(hdlrbase):
            eleza handle(self):
                line = self.rfile.readline()
                self.wfile.write(line)

        ikiwa verbose: andika("creating server")
        jaribu:
            server = MyServer(addr, MyHandler)
        except PermissionError as e:
            # Issue 29184: cannot bind() a Unix socket on Android.
            self.skipTest('Cannot create server (%s, %s): %s' %
                          (svrcls, addr, e))
        self.assertEqual(server.server_address, server.socket.getsockname())
        rudisha server

    @reap_threads
    eleza run_server(self, svrcls, hdlrbase, testfunc):
        server = self.make_server(self.pickaddr(svrcls.address_family),
                                  svrcls, hdlrbase)
        # We had the OS pick a port, so pull the real address out of
        # the server.
        addr = server.server_address
        ikiwa verbose:
            andika("ADDR =", addr)
            andika("CLASS =", svrcls)

        t = threading.Thread(
            name='%s serving' % svrcls,
            target=server.serve_forever,
            # Short poll interval to make the test finish quickly.
            # Time between requests ni short enough that we won't wake
            # up spuriously too many times.
            kwargs={'poll_interval':0.01})
        t.daemon = Kweli  # In case this function raises.
        t.start()
        ikiwa verbose: andika("server running")
        kila i kwenye range(3):
            ikiwa verbose: andika("test client", i)
            testfunc(svrcls.address_family, addr)
        ikiwa verbose: andika("waiting kila server")
        server.shutdown()
        t.join()
        server.server_close()
        self.assertEqual(-1, server.socket.fileno())
        ikiwa HAVE_FORKING na isinstance(server, socketserver.ForkingMixIn):
            # bpo-31151: Check that ForkingMixIn.server_close() waits until
            # all children completed
            self.assertUongo(server.active_children)
        ikiwa verbose: andika("done")

    eleza stream_examine(self, proto, addr):
        ukijumuisha socket.socket(proto, socket.SOCK_STREAM) as s:
            s.connect(addr)
            s.sendall(TEST_STR)
            buf = data = receive(s, 100)
            wakati data na b'\n' sio kwenye buf:
                data = receive(s, 100)
                buf += data
            self.assertEqual(buf, TEST_STR)

    eleza dgram_examine(self, proto, addr):
        ukijumuisha socket.socket(proto, socket.SOCK_DGRAM) as s:
            ikiwa HAVE_UNIX_SOCKETS na proto == socket.AF_UNIX:
                s.bind(self.pickaddr(proto))
            s.sendto(TEST_STR, addr)
            buf = data = receive(s, 100)
            wakati data na b'\n' sio kwenye buf:
                data = receive(s, 100)
                buf += data
            self.assertEqual(buf, TEST_STR)

    eleza test_TCPServer(self):
        self.run_server(socketserver.TCPServer,
                        socketserver.StreamRequestHandler,
                        self.stream_examine)

    eleza test_ThreadingTCPServer(self):
        self.run_server(socketserver.ThreadingTCPServer,
                        socketserver.StreamRequestHandler,
                        self.stream_examine)

    @requires_forking
    eleza test_ForkingTCPServer(self):
        ukijumuisha simple_subprocess(self):
            self.run_server(socketserver.ForkingTCPServer,
                            socketserver.StreamRequestHandler,
                            self.stream_examine)

    @requires_unix_sockets
    eleza test_UnixStreamServer(self):
        self.run_server(socketserver.UnixStreamServer,
                        socketserver.StreamRequestHandler,
                        self.stream_examine)

    @requires_unix_sockets
    eleza test_ThreadingUnixStreamServer(self):
        self.run_server(socketserver.ThreadingUnixStreamServer,
                        socketserver.StreamRequestHandler,
                        self.stream_examine)

    @requires_unix_sockets
    @requires_forking
    eleza test_ForkingUnixStreamServer(self):
        ukijumuisha simple_subprocess(self):
            self.run_server(ForkingUnixStreamServer,
                            socketserver.StreamRequestHandler,
                            self.stream_examine)

    eleza test_UDPServer(self):
        self.run_server(socketserver.UDPServer,
                        socketserver.DatagramRequestHandler,
                        self.dgram_examine)

    eleza test_ThreadingUDPServer(self):
        self.run_server(socketserver.ThreadingUDPServer,
                        socketserver.DatagramRequestHandler,
                        self.dgram_examine)

    @requires_forking
    eleza test_ForkingUDPServer(self):
        ukijumuisha simple_subprocess(self):
            self.run_server(socketserver.ForkingUDPServer,
                            socketserver.DatagramRequestHandler,
                            self.dgram_examine)

    @requires_unix_sockets
    eleza test_UnixDatagramServer(self):
        self.run_server(socketserver.UnixDatagramServer,
                        socketserver.DatagramRequestHandler,
                        self.dgram_examine)

    @requires_unix_sockets
    eleza test_ThreadingUnixDatagramServer(self):
        self.run_server(socketserver.ThreadingUnixDatagramServer,
                        socketserver.DatagramRequestHandler,
                        self.dgram_examine)

    @requires_unix_sockets
    @requires_forking
    eleza test_ForkingUnixDatagramServer(self):
        self.run_server(ForkingUnixDatagramServer,
                        socketserver.DatagramRequestHandler,
                        self.dgram_examine)

    @reap_threads
    eleza test_shutdown(self):
        # Issue #2302: shutdown() should always succeed kwenye making an
        # other thread leave serve_forever().
        kundi MyServer(socketserver.TCPServer):
            pass

        kundi MyHandler(socketserver.StreamRequestHandler):
            pass

        threads = []
        kila i kwenye range(20):
            s = MyServer((HOST, 0), MyHandler)
            t = threading.Thread(
                name='MyServer serving',
                target=s.serve_forever,
                kwargs={'poll_interval':0.01})
            t.daemon = Kweli  # In case this function raises.
            threads.append((t, s))
        kila t, s kwenye threads:
            t.start()
            s.shutdown()
        kila t, s kwenye threads:
            t.join()
            s.server_close()

    eleza test_tcpserver_bind_leak(self):
        # Issue #22435: the server socket wouldn't be closed ikiwa bind()/listen()
        # failed.
        # Create many servers kila which bind() will fail, to see ikiwa this result
        # kwenye FD exhaustion.
        kila i kwenye range(1024):
            ukijumuisha self.assertRaises(OverflowError):
                socketserver.TCPServer((HOST, -1),
                                       socketserver.StreamRequestHandler)

    eleza test_context_manager(self):
        ukijumuisha socketserver.TCPServer((HOST, 0),
                                    socketserver.StreamRequestHandler) as server:
            pass
        self.assertEqual(-1, server.socket.fileno())


kundi ErrorHandlerTest(unittest.TestCase):
    """Test that the servers pass normal exceptions kutoka the handler to
    handle_error(), na that exiting exceptions like SystemExit and
    KeyboardInterrupt are sio passed."""

    eleza tearDown(self):
        test.support.unlink(test.support.TESTFN)

    eleza test_sync_handled(self):
        BaseErrorTestServer(ValueError)
        self.check_result(handled=Kweli)

    eleza test_sync_not_handled(self):
        ukijumuisha self.assertRaises(SystemExit):
            BaseErrorTestServer(SystemExit)
        self.check_result(handled=Uongo)

    eleza test_threading_handled(self):
        ThreadingErrorTestServer(ValueError)
        self.check_result(handled=Kweli)

    eleza test_threading_not_handled(self):
        ThreadingErrorTestServer(SystemExit)
        self.check_result(handled=Uongo)

    @requires_forking
    eleza test_forking_handled(self):
        ForkingErrorTestServer(ValueError)
        self.check_result(handled=Kweli)

    @requires_forking
    eleza test_forking_not_handled(self):
        ForkingErrorTestServer(SystemExit)
        self.check_result(handled=Uongo)

    eleza check_result(self, handled):
        ukijumuisha open(test.support.TESTFN) as log:
            expected = 'Handler called\n' + 'Error handled\n' * handled
            self.assertEqual(log.read(), expected)


kundi BaseErrorTestServer(socketserver.TCPServer):
    eleza __init__(self, exception):
        self.exception = exception
        super().__init__((HOST, 0), BadHandler)
        ukijumuisha socket.create_connection(self.server_address):
            pass
        jaribu:
            self.handle_request()
        mwishowe:
            self.server_close()
        self.wait_done()

    eleza handle_error(self, request, client_address):
        ukijumuisha open(test.support.TESTFN, 'a') as log:
            log.write('Error handled\n')

    eleza wait_done(self):
        pass


kundi BadHandler(socketserver.BaseRequestHandler):
    eleza handle(self):
        ukijumuisha open(test.support.TESTFN, 'a') as log:
            log.write('Handler called\n')
         ashiria self.server.exception('Test error')


kundi ThreadingErrorTestServer(socketserver.ThreadingMixIn,
        BaseErrorTestServer):
    eleza __init__(self, *pos, **kw):
        self.done = threading.Event()
        super().__init__(*pos, **kw)

    eleza shutdown_request(self, *pos, **kw):
        super().shutdown_request(*pos, **kw)
        self.done.set()

    eleza wait_done(self):
        self.done.wait()


ikiwa HAVE_FORKING:
    kundi ForkingErrorTestServer(socketserver.ForkingMixIn, BaseErrorTestServer):
        pass


kundi SocketWriterTest(unittest.TestCase):
    eleza test_basics(self):
        kundi Handler(socketserver.StreamRequestHandler):
            eleza handle(self):
                self.server.wfile = self.wfile
                self.server.wfile_fileno = self.wfile.fileno()
                self.server.request_fileno = self.request.fileno()

        server = socketserver.TCPServer((HOST, 0), Handler)
        self.addCleanup(server.server_close)
        s = socket.socket(
            server.address_family, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        ukijumuisha s:
            s.connect(server.server_address)
        server.handle_request()
        self.assertIsInstance(server.wfile, io.BufferedIOBase)
        self.assertEqual(server.wfile_fileno, server.request_fileno)

    eleza test_write(self):
        # Test that wfile.write() sends data immediately, na that it does
        # sio truncate sends when interrupted by a Unix signal
        pthread_kill = test.support.get_attribute(signal, 'pthread_kill')

        kundi Handler(socketserver.StreamRequestHandler):
            eleza handle(self):
                self.server.sent1 = self.wfile.write(b'write data\n')
                # Should be sent immediately, without requiring flush()
                self.server.received = self.rfile.readline()
                big_chunk = b'\0' * test.support.SOCK_MAX_SIZE
                self.server.sent2 = self.wfile.write(big_chunk)

        server = socketserver.TCPServer((HOST, 0), Handler)
        self.addCleanup(server.server_close)
        interrupted = threading.Event()

        eleza signal_handler(signum, frame):
            interrupted.set()

        original = signal.signal(signal.SIGUSR1, signal_handler)
        self.addCleanup(signal.signal, signal.SIGUSR1, original)
        response1 = Tupu
        received2 = Tupu
        main_thread = threading.get_ident()

        eleza run_client():
            s = socket.socket(server.address_family, socket.SOCK_STREAM,
                socket.IPPROTO_TCP)
            ukijumuisha s, s.makefile('rb') as reader:
                s.connect(server.server_address)
                nonlocal response1
                response1 = reader.readline()
                s.sendall(b'client response\n')

                reader.read(100)
                # The main thread should now be blocking kwenye a send() syscall.
                # But kwenye theory, it could get interrupted by other signals,
                # na then retried. So keep sending the signal kwenye a loop, in
                # case an earlier signal happens to be delivered at an
                # inconvenient moment.
                wakati Kweli:
                    pthread_kill(main_thread, signal.SIGUSR1)
                    ikiwa interrupted.wait(timeout=float(1)):
                        koma
                nonlocal received2
                received2 = len(reader.read())

        background = threading.Thread(target=run_client)
        background.start()
        server.handle_request()
        background.join()
        self.assertEqual(server.sent1, len(response1))
        self.assertEqual(response1, b'write data\n')
        self.assertEqual(server.received, b'client response\n')
        self.assertEqual(server.sent2, test.support.SOCK_MAX_SIZE)
        self.assertEqual(received2, test.support.SOCK_MAX_SIZE - 100)


kundi MiscTestCase(unittest.TestCase):

    eleza test_all(self):
        # objects defined kwenye the module should be kwenye __all__
        expected = []
        kila name kwenye dir(socketserver):
            ikiwa sio name.startswith('_'):
                mod_object = getattr(socketserver, name)
                ikiwa getattr(mod_object, '__module__', Tupu) == 'socketserver':
                    expected.append(name)
        self.assertCountEqual(socketserver.__all__, expected)

    eleza test_shutdown_request_called_if_verify_request_false(self):
        # Issue #26309: BaseServer should call shutdown_request even if
        # verify_request ni Uongo

        kundi MyServer(socketserver.TCPServer):
            eleza verify_request(self, request, client_address):
                rudisha Uongo

            shutdown_called = 0
            eleza shutdown_request(self, request):
                self.shutdown_called += 1
                socketserver.TCPServer.shutdown_request(self, request)

        server = MyServer((HOST, 0), socketserver.StreamRequestHandler)
        s = socket.socket(server.address_family, socket.SOCK_STREAM)
        s.connect(server.server_address)
        s.close()
        server.handle_request()
        self.assertEqual(server.shutdown_called, 1)
        server.server_close()


ikiwa __name__ == "__main__":
    unittest.main()
