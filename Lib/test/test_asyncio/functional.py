agiza asyncio
agiza asyncio.events
agiza contextlib
agiza os
agiza pprint
agiza select
agiza socket
agiza tempfile
agiza threading


kundi FunctionalTestCaseMixin:

    eleza new_loop(self):
        rudisha asyncio.new_event_loop()

    eleza run_loop_briefly(self, *, delay=0.01):
        self.loop.run_until_complete(asyncio.sleep(delay))

    eleza loop_exception_handler(self, loop, context):
        self.__unhandled_exceptions.append(context)
        self.loop.default_exception_handler(context)

    eleza setUp(self):
        self.loop = self.new_loop()
        asyncio.set_event_loop(Tupu)

        self.loop.set_exception_handler(self.loop_exception_handler)
        self.__unhandled_exceptions = []

        # Disable `_get_running_loop`.
        self._old_get_running_loop = asyncio.events._get_running_loop
        asyncio.events._get_running_loop = lambda: Tupu

    eleza tearDown(self):
        jaribu:
            self.loop.close()

            ikiwa self.__unhandled_exceptions:
                andika('Unexpected calls to loop.call_exception_handler():')
                pprint.pandika(self.__unhandled_exceptions)
                self.fail('unexpected calls to loop.call_exception_handler()')

        mwishowe:
            asyncio.events._get_running_loop = self._old_get_running_loop
            asyncio.set_event_loop(Tupu)
            self.loop = Tupu

    eleza tcp_server(self, server_prog, *,
                   family=socket.AF_INET,
                   addr=Tupu,
                   timeout=5,
                   backlog=1,
                   max_clients=10):

        ikiwa addr ni Tupu:
            ikiwa hasattr(socket, 'AF_UNIX') na family == socket.AF_UNIX:
                ukijumuisha tempfile.NamedTemporaryFile() kama tmp:
                    addr = tmp.name
            isipokua:
                addr = ('127.0.0.1', 0)

        sock = socket.create_server(addr, family=family, backlog=backlog)
        ikiwa timeout ni Tupu:
            ashiria RuntimeError('timeout ni required')
        ikiwa timeout <= 0:
            ashiria RuntimeError('only blocking sockets are supported')
        sock.settimeout(timeout)

        rudisha TestThreadedServer(
            self, sock, server_prog, timeout, max_clients)

    eleza tcp_client(self, client_prog,
                   family=socket.AF_INET,
                   timeout=10):

        sock = socket.socket(family, socket.SOCK_STREAM)

        ikiwa timeout ni Tupu:
            ashiria RuntimeError('timeout ni required')
        ikiwa timeout <= 0:
            ashiria RuntimeError('only blocking sockets are supported')
        sock.settimeout(timeout)

        rudisha TestThreadedClient(
            self, sock, client_prog, timeout)

    eleza unix_server(self, *args, **kwargs):
        ikiwa sio hasattr(socket, 'AF_UNIX'):
            ashiria NotImplementedError
        rudisha self.tcp_server(*args, family=socket.AF_UNIX, **kwargs)

    eleza unix_client(self, *args, **kwargs):
        ikiwa sio hasattr(socket, 'AF_UNIX'):
            ashiria NotImplementedError
        rudisha self.tcp_client(*args, family=socket.AF_UNIX, **kwargs)

    @contextlib.contextmanager
    eleza unix_sock_name(self):
        ukijumuisha tempfile.TemporaryDirectory() kama td:
            fn = os.path.join(td, 'sock')
            jaribu:
                tuma fn
            mwishowe:
                jaribu:
                    os.unlink(fn)
                tatizo OSError:
                    pita

    eleza _abort_socket_test(self, ex):
        jaribu:
            self.loop.stop()
        mwishowe:
            self.fail(ex)


##############################################################################
# Socket Testing Utilities
##############################################################################


kundi TestSocketWrapper:

    eleza __init__(self, sock):
        self.__sock = sock

    eleza recv_all(self, n):
        buf = b''
        wakati len(buf) < n:
            data = self.recv(n - len(buf))
            ikiwa data == b'':
                ashiria ConnectionAbortedError
            buf += data
        rudisha buf

    eleza start_tls(self, ssl_context, *,
                  server_side=Uongo,
                  server_hostname=Tupu):

        ssl_sock = ssl_context.wrap_socket(
            self.__sock, server_side=server_side,
            server_hostname=server_hostname,
            do_handshake_on_connect=Uongo)

        jaribu:
            ssl_sock.do_handshake()
        tatizo:
            ssl_sock.close()
            raise
        mwishowe:
            self.__sock.close()

        self.__sock = ssl_sock

    eleza __getattr__(self, name):
        rudisha getattr(self.__sock, name)

    eleza __repr__(self):
        rudisha '<{} {!r}>'.format(type(self).__name__, self.__sock)


kundi SocketThread(threading.Thread):

    eleza stop(self):
        self._active = Uongo
        self.join()

    eleza __enter__(self):
        self.start()
        rudisha self

    eleza __exit__(self, *exc):
        self.stop()


kundi TestThreadedClient(SocketThread):

    eleza __init__(self, test, sock, prog, timeout):
        threading.Thread.__init__(self, Tupu, Tupu, 'test-client')
        self.daemon = Kweli

        self._timeout = timeout
        self._sock = sock
        self._active = Kweli
        self._prog = prog
        self._test = test

    eleza run(self):
        jaribu:
            self._prog(TestSocketWrapper(self._sock))
        tatizo Exception kama ex:
            self._test._abort_socket_test(ex)


kundi TestThreadedServer(SocketThread):

    eleza __init__(self, test, sock, prog, timeout, max_clients):
        threading.Thread.__init__(self, Tupu, Tupu, 'test-server')
        self.daemon = Kweli

        self._clients = 0
        self._finished_clients = 0
        self._max_clients = max_clients
        self._timeout = timeout
        self._sock = sock
        self._active = Kweli

        self._prog = prog

        self._s1, self._s2 = socket.socketpair()
        self._s1.setblocking(Uongo)

        self._test = test

    eleza stop(self):
        jaribu:
            ikiwa self._s2 na self._s2.fileno() != -1:
                jaribu:
                    self._s2.send(b'stop')
                tatizo OSError:
                    pita
        mwishowe:
            super().stop()

    eleza run(self):
        jaribu:
            ukijumuisha self._sock:
                self._sock.setblocking(0)
                self._run()
        mwishowe:
            self._s1.close()
            self._s2.close()

    eleza _run(self):
        wakati self._active:
            ikiwa self._clients >= self._max_clients:
                return

            r, w, x = select.select(
                [self._sock, self._s1], [], [], self._timeout)

            ikiwa self._s1 kwenye r:
                return

            ikiwa self._sock kwenye r:
                jaribu:
                    conn, addr = self._sock.accept()
                tatizo BlockingIOError:
                    endelea
                tatizo socket.timeout:
                    ikiwa sio self._active:
                        return
                    isipokua:
                        raise
                isipokua:
                    self._clients += 1
                    conn.settimeout(self._timeout)
                    jaribu:
                        ukijumuisha conn:
                            self._handle_client(conn)
                    tatizo Exception kama ex:
                        self._active = Uongo
                        jaribu:
                            raise
                        mwishowe:
                            self._test._abort_socket_test(ex)

    eleza _handle_client(self, sock):
        self._prog(TestSocketWrapper(sock))

    @property
    eleza addr(self):
        rudisha self._sock.getsockname()
