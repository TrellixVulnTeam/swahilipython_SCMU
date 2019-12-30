"""Utilities shared by tests."""

agiza asyncio
agiza collections
agiza contextlib
agiza io
agiza logging
agiza os
agiza re
agiza selectors
agiza socket
agiza socketserver
agiza sys
agiza tempfile
agiza threading
agiza time
agiza unittest
agiza weakref

kutoka unittest agiza mock

kutoka http.server agiza HTTPServer
kutoka wsgiref.simple_server agiza WSGIRequestHandler, WSGIServer

jaribu:
    agiza ssl
except ImportError:  # pragma: no cover
    ssl = Tupu

kutoka asyncio agiza base_events
kutoka asyncio agiza events
kutoka asyncio agiza format_helpers
kutoka asyncio agiza futures
kutoka asyncio agiza tasks
kutoka asyncio.log agiza logger
kutoka test agiza support


eleza data_file(filename):
    ikiwa hasattr(support, 'TEST_HOME_DIR'):
        fullname = os.path.join(support.TEST_HOME_DIR, filename)
        ikiwa os.path.isfile(fullname):
            rudisha fullname
    fullname = os.path.join(os.path.dirname(__file__), '..', filename)
    ikiwa os.path.isfile(fullname):
        rudisha fullname
     ashiria FileNotFoundError(filename)


ONLYCERT = data_file('ssl_cert.pem')
ONLYKEY = data_file('ssl_key.pem')
SIGNED_CERTFILE = data_file('keycert3.pem')
SIGNING_CA = data_file('pycacert.pem')
PEERCERT = {
    'OCSP': ('http://testca.pythontest.net/testca/ocsp/',),
    'caIssuers': ('http://testca.pythontest.net/testca/pycacert.cer',),
    'crlDistributionPoints': ('http://testca.pythontest.net/testca/revocation.crl',),
    'issuer': ((('countryName', 'XY'),),
            (('organizationName', 'Python Software Foundation CA'),),
            (('commonName', 'our-ca-server'),)),
    'notAfter': 'Jul  7 14:23:16 2028 GMT',
    'notBefore': 'Aug 29 14:23:16 2018 GMT',
    'serialNumber': 'CB2D80995A69525C',
    'subject': ((('countryName', 'XY'),),
             (('localityName', 'Castle Anthrax'),),
             (('organizationName', 'Python Software Foundation'),),
             (('commonName', 'localhost'),)),
    'subjectAltName': (('DNS', 'localhost'),),
    'version': 3
}


eleza simple_server_sslcontext():
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(ONLYCERT, ONLYKEY)
    server_context.check_hostname = Uongo
    server_context.verify_mode = ssl.CERT_NONE
    rudisha server_context


eleza simple_client_sslcontext(*, disable_verify=Kweli):
    client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client_context.check_hostname = Uongo
    ikiwa disable_verify:
        client_context.verify_mode = ssl.CERT_NONE
    rudisha client_context


eleza dummy_ssl_context():
    ikiwa ssl ni Tupu:
        rudisha Tupu
    isipokua:
        rudisha ssl.SSLContext(ssl.PROTOCOL_TLS)


eleza run_briefly(loop):
    async eleza once():
        pass
    gen = once()
    t = loop.create_task(gen)
    # Don't log a warning ikiwa the task ni sio done after run_until_complete().
    # It occurs ikiwa the loop ni stopped ama ikiwa a task raises a BaseException.
    t._log_destroy_pending = Uongo
    jaribu:
        loop.run_until_complete(t)
    mwishowe:
        gen.close()


eleza run_until(loop, pred, timeout=30):
    deadline = time.monotonic() + timeout
    wakati sio pred():
        ikiwa timeout ni sio Tupu:
            timeout = deadline - time.monotonic()
            ikiwa timeout <= 0:
                 ashiria futures.TimeoutError()
        loop.run_until_complete(tasks.sleep(0.001))


eleza run_once(loop):
    """Legacy API to run once through the event loop.

    This ni the recommended pattern kila test code.  It will poll the
    selector once na run all callbacks scheduled kwenye response to I/O
    events.
    """
    loop.call_soon(loop.stop)
    loop.run_forever()


kundi SilentWSGIRequestHandler(WSGIRequestHandler):

    eleza get_stderr(self):
        rudisha io.StringIO()

    eleza log_message(self, format, *args):
        pass


kundi SilentWSGIServer(WSGIServer):

    request_timeout = 2

    eleza get_request(self):
        request, client_addr = super().get_request()
        request.settimeout(self.request_timeout)
        rudisha request, client_addr

    eleza handle_error(self, request, client_address):
        pass


kundi SSLWSGIServerMixin:

    eleza finish_request(self, request, client_address):
        # The relative location of our test directory (which
        # contains the ssl key na certificate files) differs
        # between the stdlib na stand-alone asyncio.
        # Prefer our own ikiwa we can find it.
        context = ssl.SSLContext()
        context.load_cert_chain(ONLYCERT, ONLYKEY)

        ssock = context.wrap_socket(request, server_side=Kweli)
        jaribu:
            self.RequestHandlerClass(ssock, client_address, self)
            ssock.close()
        except OSError:
            # maybe socket has been closed by peer
            pass


kundi SSLWSGIServer(SSLWSGIServerMixin, SilentWSGIServer):
    pass


eleza _run_test_server(*, address, use_ssl=Uongo, server_cls, server_ssl_cls):

    eleza loop(environ):
        size = int(environ['CONTENT_LENGTH'])
        wakati size:
            data = environ['wsgi.input'].read(min(size, 0x10000))
            tuma data
            size -= len(data)

    eleza app(environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        ikiwa environ['PATH_INFO'] == '/loop':
            rudisha loop(environ)
        isipokua:
            rudisha [b'Test message']

    # Run the test WSGI server kwenye a separate thread kwenye order sio to
    # interfere ukijumuisha event handling kwenye the main thread
    server_kundi = server_ssl_cls ikiwa use_ssl isipokua server_cls
    httpd = server_class(address, SilentWSGIRequestHandler)
    httpd.set_app(app)
    httpd.address = httpd.server_address
    server_thread = threading.Thread(
        target=lambda: httpd.serve_forever(poll_interval=0.05))
    server_thread.start()
    jaribu:
        tuma httpd
    mwishowe:
        httpd.shutdown()
        httpd.server_close()
        server_thread.join()


ikiwa hasattr(socket, 'AF_UNIX'):

    kundi UnixHTTPServer(socketserver.UnixStreamServer, HTTPServer):

        eleza server_bind(self):
            socketserver.UnixStreamServer.server_bind(self)
            self.server_name = '127.0.0.1'
            self.server_port = 80


    kundi UnixWSGIServer(UnixHTTPServer, WSGIServer):

        request_timeout = 2

        eleza server_bind(self):
            UnixHTTPServer.server_bind(self)
            self.setup_environ()

        eleza get_request(self):
            request, client_addr = super().get_request()
            request.settimeout(self.request_timeout)
            # Code kwenye the stdlib expects that get_request
            # will rudisha a socket na a tuple (host, port).
            # However, this isn't true kila UNIX sockets,
            # as the second rudisha value will be a path;
            # hence we rudisha some fake data sufficient
            # to get the tests going
            rudisha request, ('127.0.0.1', '')


    kundi SilentUnixWSGIServer(UnixWSGIServer):

        eleza handle_error(self, request, client_address):
            pass


    kundi UnixSSLWSGIServer(SSLWSGIServerMixin, SilentUnixWSGIServer):
        pass


    eleza gen_unix_socket_path():
        ukijumuisha tempfile.NamedTemporaryFile() as file:
            rudisha file.name


    @contextlib.contextmanager
    eleza unix_socket_path():
        path = gen_unix_socket_path()
        jaribu:
            tuma path
        mwishowe:
            jaribu:
                os.unlink(path)
            except OSError:
                pass


    @contextlib.contextmanager
    eleza run_test_unix_server(*, use_ssl=Uongo):
        ukijumuisha unix_socket_path() as path:
            tuma kutoka _run_test_server(address=path, use_ssl=use_ssl,
                                        server_cls=SilentUnixWSGIServer,
                                        server_ssl_cls=UnixSSLWSGIServer)


@contextlib.contextmanager
eleza run_test_server(*, host='127.0.0.1', port=0, use_ssl=Uongo):
    tuma kutoka _run_test_server(address=(host, port), use_ssl=use_ssl,
                                server_cls=SilentWSGIServer,
                                server_ssl_cls=SSLWSGIServer)


eleza make_test_protocol(base):
    dct = {}
    kila name kwenye dir(base):
        ikiwa name.startswith('__') na name.endswith('__'):
            # skip magic names
            endelea
        dct[name] = MockCallback(return_value=Tupu)
    rudisha type('TestProtocol', (base,) + base.__bases__, dct)()


kundi TestSelector(selectors.BaseSelector):

    eleza __init__(self):
        self.keys = {}

    eleza register(self, fileobj, events, data=Tupu):
        key = selectors.SelectorKey(fileobj, 0, events, data)
        self.keys[fileobj] = key
        rudisha key

    eleza unregister(self, fileobj):
        rudisha self.keys.pop(fileobj)

    eleza select(self, timeout):
        rudisha []

    eleza get_map(self):
        rudisha self.keys


kundi TestLoop(base_events.BaseEventLoop):
    """Loop kila unittests.

    It manages self time directly.
    If something scheduled to be executed later then
    on next loop iteration after all ready handlers done
    generator passed to __init__ ni calling.

    Generator should be like this:

        eleza gen():
            ...
            when = tuma ...
            ... = tuma time_advance

    Value returned by tuma ni absolute time of next scheduled handler.
    Value passed to tuma ni time advance to move loop's time forward.
    """

    eleza __init__(self, gen=Tupu):
        super().__init__()

        ikiwa gen ni Tupu:
            eleza gen():
                yield
            self._check_on_close = Uongo
        isipokua:
            self._check_on_close = Kweli

        self._gen = gen()
        next(self._gen)
        self._time = 0
        self._clock_resolution = 1e-9
        self._timers = []
        self._selector = TestSelector()

        self.readers = {}
        self.writers = {}
        self.reset_counters()

        self._transports = weakref.WeakValueDictionary()

    eleza time(self):
        rudisha self._time

    eleza advance_time(self, advance):
        """Move test time forward."""
        ikiwa advance:
            self._time += advance

    eleza close(self):
        super().close()
        ikiwa self._check_on_close:
            jaribu:
                self._gen.send(0)
            except StopIteration:
                pass
            isipokua:  # pragma: no cover
                 ashiria AssertionError("Time generator ni sio finished")

    eleza _add_reader(self, fd, callback, *args):
        self.readers[fd] = events.Handle(callback, args, self, Tupu)

    eleza _remove_reader(self, fd):
        self.remove_reader_count[fd] += 1
        ikiwa fd kwenye self.readers:
            toa self.readers[fd]
            rudisha Kweli
        isipokua:
            rudisha Uongo

    eleza assert_reader(self, fd, callback, *args):
        ikiwa fd sio kwenye self.readers:
             ashiria AssertionError(f'fd {fd} ni sio registered')
        handle = self.readers[fd]
        ikiwa handle._callback != callback:
             ashiria AssertionError(
                f'unexpected callback: {handle._callback} != {callback}')
        ikiwa handle._args != args:
             ashiria AssertionError(
                f'unexpected callback args: {handle._args} != {args}')

    eleza assert_no_reader(self, fd):
        ikiwa fd kwenye self.readers:
             ashiria AssertionError(f'fd {fd} ni registered')

    eleza _add_writer(self, fd, callback, *args):
        self.writers[fd] = events.Handle(callback, args, self, Tupu)

    eleza _remove_writer(self, fd):
        self.remove_writer_count[fd] += 1
        ikiwa fd kwenye self.writers:
            toa self.writers[fd]
            rudisha Kweli
        isipokua:
            rudisha Uongo

    eleza assert_writer(self, fd, callback, *args):
        assert fd kwenye self.writers, 'fd {} ni sio registered'.format(fd)
        handle = self.writers[fd]
        assert handle._callback == callback, '{!r} != {!r}'.format(
            handle._callback, callback)
        assert handle._args == args, '{!r} != {!r}'.format(
            handle._args, args)

    eleza _ensure_fd_no_transport(self, fd):
        ikiwa sio isinstance(fd, int):
            jaribu:
                fd = int(fd.fileno())
            except (AttributeError, TypeError, ValueError):
                # This code matches selectors._fileobj_to_fd function.
                 ashiria ValueError("Invalid file object: "
                                 "{!r}".format(fd)) kutoka Tupu
        jaribu:
            transport = self._transports[fd]
        except KeyError:
            pass
        isipokua:
             ashiria RuntimeError(
                'File descriptor {!r} ni used by transport {!r}'.format(
                    fd, transport))

    eleza add_reader(self, fd, callback, *args):
        """Add a reader callback."""
        self._ensure_fd_no_transport(fd)
        rudisha self._add_reader(fd, callback, *args)

    eleza remove_reader(self, fd):
        """Remove a reader callback."""
        self._ensure_fd_no_transport(fd)
        rudisha self._remove_reader(fd)

    eleza add_writer(self, fd, callback, *args):
        """Add a writer callback.."""
        self._ensure_fd_no_transport(fd)
        rudisha self._add_writer(fd, callback, *args)

    eleza remove_writer(self, fd):
        """Remove a writer callback."""
        self._ensure_fd_no_transport(fd)
        rudisha self._remove_writer(fd)

    eleza reset_counters(self):
        self.remove_reader_count = collections.defaultdict(int)
        self.remove_writer_count = collections.defaultdict(int)

    eleza _run_once(self):
        super()._run_once()
        kila when kwenye self._timers:
            advance = self._gen.send(when)
            self.advance_time(advance)
        self._timers = []

    eleza call_at(self, when, callback, *args, context=Tupu):
        self._timers.append(when)
        rudisha super().call_at(when, callback, *args, context=context)

    eleza _process_events(self, event_list):
        return

    eleza _write_to_self(self):
        pass


eleza MockCallback(**kwargs):
    rudisha mock.Mock(spec=['__call__'], **kwargs)


kundi MockPattern(str):
    """A regex based str ukijumuisha a fuzzy __eq__.

    Use this helper ukijumuisha 'mock.assert_called_with', ama anywhere
    where a regex comparison between strings ni needed.

    For instance:
       mock_call.assert_called_with(MockPattern('spam.*ham'))
    """
    eleza __eq__(self, other):
        rudisha bool(re.search(str(self), other, re.S))


kundi MockInstanceOf:
    eleza __init__(self, type):
        self._type = type

    eleza __eq__(self, other):
        rudisha isinstance(other, self._type)


eleza get_function_source(func):
    source = format_helpers._get_function_source(func)
    ikiwa source ni Tupu:
         ashiria ValueError("unable to get the source of %r" % (func,))
    rudisha source


kundi TestCase(unittest.TestCase):
    @staticmethod
    eleza close_loop(loop):
        executor = loop._default_executor
        ikiwa executor ni sio Tupu:
            executor.shutdown(wait=Kweli)
        loop.close()
        policy = support.maybe_get_event_loop_policy()
        ikiwa policy ni sio Tupu:
            jaribu:
                watcher = policy.get_child_watcher()
            except NotImplementedError:
                # watcher ni sio implemented by EventLoopPolicy, e.g. Windows
                pass
            isipokua:
                ikiwa isinstance(watcher, asyncio.ThreadedChildWatcher):
                    threads = list(watcher._threads.values())
                    kila thread kwenye threads:
                        thread.join()

    eleza set_event_loop(self, loop, *, cleanup=Kweli):
        assert loop ni sio Tupu
        # ensure that the event loop ni passed explicitly kwenye asyncio
        events.set_event_loop(Tupu)
        ikiwa cleanup:
            self.addCleanup(self.close_loop, loop)

    eleza new_test_loop(self, gen=Tupu):
        loop = TestLoop(gen)
        self.set_event_loop(loop)
        rudisha loop

    eleza unpatch_get_running_loop(self):
        events._get_running_loop = self._get_running_loop

    eleza setUp(self):
        self._get_running_loop = events._get_running_loop
        events._get_running_loop = lambda: Tupu
        self._thread_cleanup = support.threading_setup()

    eleza tearDown(self):
        self.unpatch_get_running_loop()

        events.set_event_loop(Tupu)

        # Detect CPython bug #23353: ensure that yield/yield-kutoka ni sio used
        # kwenye an except block of a generator
        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

        self.doCleanups()
        support.threading_cleanup(*self._thread_cleanup)
        support.reap_children()


@contextlib.contextmanager
eleza disable_logger():
    """Context manager to disable asyncio logger.

    For example, it can be used to ignore warnings kwenye debug mode.
    """
    old_level = logger.level
    jaribu:
        logger.setLevel(logging.CRITICAL+1)
        yield
    mwishowe:
        logger.setLevel(old_level)


eleza mock_nonblocking_socket(proto=socket.IPPROTO_TCP, type=socket.SOCK_STREAM,
                            family=socket.AF_INET):
    """Create a mock of a non-blocking socket."""
    sock = mock.MagicMock(socket.socket)
    sock.proto = proto
    sock.type = type
    sock.family = family
    sock.gettimeout.return_value = 0.0
    rudisha sock
