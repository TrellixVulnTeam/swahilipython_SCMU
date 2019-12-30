kutoka unittest agiza mock
kutoka test agiza support
kutoka test.test_httpservers agiza NoLogRequestHandler
kutoka unittest agiza TestCase
kutoka wsgiref.util agiza setup_testing_defaults
kutoka wsgiref.headers agiza Headers
kutoka wsgiref.handlers agiza BaseHandler, BaseCGIHandler, SimpleHandler
kutoka wsgiref agiza util
kutoka wsgiref.validate agiza validator
kutoka wsgiref.simple_server agiza WSGIServer, WSGIRequestHandler
kutoka wsgiref.simple_server agiza make_server
kutoka http.client agiza HTTPConnection
kutoka io agiza StringIO, BytesIO, BufferedReader
kutoka socketserver agiza BaseServer
kutoka platform agiza python_implementation

agiza os
agiza re
agiza signal
agiza sys
agiza threading
agiza unittest


kundi MockServer(WSGIServer):
    """Non-socket HTTP server"""

    eleza __init__(self, server_address, RequestHandlerClass):
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.server_bind()

    eleza server_bind(self):
        host, port = self.server_address
        self.server_name = host
        self.server_port = port
        self.setup_environ()


kundi MockHandler(WSGIRequestHandler):
    """Non-socket HTTP handler"""
    eleza setup(self):
        self.connection = self.request
        self.rfile, self.wfile = self.connection

    eleza finish(self):
        pita


eleza hello_app(environ,start_response):
    start_response("200 OK", [
        ('Content-Type','text/plain'),
        ('Date','Mon, 05 Jun 2006 18:49:54 GMT')
    ])
    rudisha [b"Hello, world!"]


eleza header_app(environ, start_response):
    start_response("200 OK", [
        ('Content-Type', 'text/plain'),
        ('Date', 'Mon, 05 Jun 2006 18:49:54 GMT')
    ])
    rudisha [';'.join([
        environ['HTTP_X_TEST_HEADER'], environ['QUERY_STRING'],
        environ['PATH_INFO']
    ]).encode('iso-8859-1')]


eleza run_amock(app=hello_app, data=b"GET / HTTP/1.0\n\n"):
    server = make_server("", 80, app, MockServer, MockHandler)
    inp = BufferedReader(BytesIO(data))
    out = BytesIO()
    olderr = sys.stderr
    err = sys.stderr = StringIO()

    jaribu:
        server.finish_request((inp, out), ("127.0.0.1",8888))
    mwishowe:
        sys.stderr = olderr

    rudisha out.getvalue(), err.getvalue()

eleza compare_generic_iter(make_it,match):
    """Utility to compare a generic 2.1/2.2+ iterator ukijumuisha an iterable

    If running under Python 2.2+, this tests the iterator using iter()/next(),
    kama well kama __getitem__.  'make_it' must be a function returning a fresh
    iterator to be tested (since this may test the iterator twice)."""

    it = make_it()
    n = 0
    kila item kwenye match:
        ikiwa sio it[n]==item: ashiria AssertionError
        n+=1
    jaribu:
        it[n]
    tatizo IndexError:
        pita
    isipokua:
        ashiria AssertionError("Too many items kutoka __getitem__",it)

    jaribu:
        iter, StopIteration
    tatizo NameError:
        pita
    isipokua:
        # Only test iter mode under 2.2+
        it = make_it()
        ikiwa sio iter(it) ni it: ashiria AssertionError
        kila item kwenye match:
            ikiwa sio next(it) == item: ashiria AssertionError
        jaribu:
            next(it)
        tatizo StopIteration:
            pita
        isipokua:
            ashiria AssertionError("Too many items kutoka .__next__()", it)


kundi IntegrationTests(TestCase):

    eleza check_hello(self, out, has_length=Kweli):
        pyver = (python_implementation() + "/" +
                sys.version.split()[0])
        self.assertEqual(out,
            ("HTTP/1.0 200 OK\r\n"
            "Server: WSGIServer/0.2 " + pyver +"\r\n"
            "Content-Type: text/plain\r\n"
            "Date: Mon, 05 Jun 2006 18:49:54 GMT\r\n" +
            (has_length na  "Content-Length: 13\r\n" ama "") +
            "\r\n"
            "Hello, world!").encode("iso-8859-1")
        )

    eleza test_plain_hello(self):
        out, err = run_amock()
        self.check_hello(out)

    eleza test_environ(self):
        request = (
            b"GET /p%61th/?query=test HTTP/1.0\n"
            b"X-Test-Header: Python test \n"
            b"X-Test-Header: Python test 2\n"
            b"Content-Length: 0\n\n"
        )
        out, err = run_amock(header_app, request)
        self.assertEqual(
            out.splitlines()[-1],
            b"Python test,Python test 2;query=test;/path/"
        )

    eleza test_request_length(self):
        out, err = run_amock(data=b"GET " + (b"x" * 65537) + b" HTTP/1.0\n\n")
        self.assertEqual(out.splitlines()[0],
                         b"HTTP/1.0 414 Request-URI Too Long")

    eleza test_validated_hello(self):
        out, err = run_amock(validator(hello_app))
        # the middleware doesn't support len(), so content-length isn't there
        self.check_hello(out, has_length=Uongo)

    eleza test_simple_validation_error(self):
        eleza bad_app(environ,start_response):
            start_response("200 OK", ('Content-Type','text/plain'))
            rudisha ["Hello, world!"]
        out, err = run_amock(validator(bad_app))
        self.assertKweli(out.endswith(
            b"A server error occurred.  Please contact the administrator."
        ))
        self.assertEqual(
            err.splitlines()[-2],
            "AssertionError: Headers (('Content-Type', 'text/plain')) must"
            " be of type list: <kundi 'tuple'>"
        )

    eleza test_status_validation_errors(self):
        eleza create_bad_app(status):
            eleza bad_app(environ, start_response):
                start_response(status, [("Content-Type", "text/plain; charset=utf-8")])
                rudisha [b"Hello, world!"]
            rudisha bad_app

        tests = [
            ('200', 'AssertionError: Status must be at least 4 characters'),
            ('20X OK', 'AssertionError: Status message must begin w/3-digit code'),
            ('200OK', 'AssertionError: Status message must have a space after code'),
        ]

        kila status, exc_message kwenye tests:
            ukijumuisha self.subTest(status=status):
                out, err = run_amock(create_bad_app(status))
                self.assertKweli(out.endswith(
                    b"A server error occurred.  Please contact the administrator."
                ))
                self.assertEqual(err.splitlines()[-2], exc_message)

    eleza test_wsgi_uliza(self):
        eleza bad_app(e,s):
            e["wsgi.input"].read()
            s("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
            rudisha [b"data"]
        out, err = run_amock(validator(bad_app))
        self.assertKweli(out.endswith(
            b"A server error occurred.  Please contact the administrator."
        ))
        self.assertEqual(
            err.splitlines()[-2], "AssertionError"
        )

    eleza test_bytes_validation(self):
        eleza app(e, s):
            s("200 OK", [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Date", "Wed, 24 Dec 2008 13:29:32 GMT"),
                ])
            rudisha [b"data"]
        out, err = run_amock(validator(app))
        self.assertKweli(err.endswith('"GET / HTTP/1.0" 200 4\n'))
        ver = sys.version.split()[0].encode('ascii')
        py  = python_implementation().encode('ascii')
        pyver = py + b"/" + ver
        self.assertEqual(
                b"HTTP/1.0 200 OK\r\n"
                b"Server: WSGIServer/0.2 "+ pyver + b"\r\n"
                b"Content-Type: text/plain; charset=utf-8\r\n"
                b"Date: Wed, 24 Dec 2008 13:29:32 GMT\r\n"
                b"\r\n"
                b"data",
                out)

    eleza test_cp1252_url(self):
        eleza app(e, s):
            s("200 OK", [
                ("Content-Type", "text/plain"),
                ("Date", "Wed, 24 Dec 2008 13:29:32 GMT"),
                ])
            # PEP3333 says environ variables are decoded kama latin1.
            # Encode kama latin1 to get original bytes
            rudisha [e["PATH_INFO"].encode("latin1")]

        out, err = run_amock(
            validator(app), data=b"GET /\x80%80 HTTP/1.0")
        self.assertEqual(
            [
                b"HTTP/1.0 200 OK",
                mock.ANY,
                b"Content-Type: text/plain",
                b"Date: Wed, 24 Dec 2008 13:29:32 GMT",
                b"",
                b"/\x80\x80",
            ],
            out.splitlines())

    eleza test_interrupted_write(self):
        # BaseHandler._write() na _flush() have to write all data, even if
        # it takes multiple send() calls.  Test this by interrupting a send()
        # call ukijumuisha a Unix signal.
        pthread_kill = support.get_attribute(signal, "pthread_kill")

        eleza app(environ, start_response):
            start_response("200 OK", [])
            rudisha [b'\0' * support.SOCK_MAX_SIZE]

        kundi WsgiHandler(NoLogRequestHandler, WSGIRequestHandler):
            pita

        server = make_server(support.HOST, 0, app, handler_class=WsgiHandler)
        self.addCleanup(server.server_close)
        interrupted = threading.Event()

        eleza signal_handler(signum, frame):
            interrupted.set()

        original = signal.signal(signal.SIGUSR1, signal_handler)
        self.addCleanup(signal.signal, signal.SIGUSR1, original)
        received = Tupu
        main_thread = threading.get_ident()

        eleza run_client():
            http = HTTPConnection(*server.server_address)
            http.request("GET", "/")
            ukijumuisha http.getresponse() kama response:
                response.read(100)
                # The main thread should now be blocking kwenye a send() system
                # call.  But kwenye theory, it could get interrupted by other
                # signals, na then retried.  So keep sending the signal kwenye a
                # loop, kwenye case an earlier signal happens to be delivered at
                # an inconvenient moment.
                wakati Kweli:
                    pthread_kill(main_thread, signal.SIGUSR1)
                    ikiwa interrupted.wait(timeout=float(1)):
                        koma
                nonlocal received
                received = len(response.read())
            http.close()

        background = threading.Thread(target=run_client)
        background.start()
        server.handle_request()
        background.join()
        self.assertEqual(received, support.SOCK_MAX_SIZE - 100)


kundi UtilityTests(TestCase):

    eleza checkShift(self,sn_in,pi_in,part,sn_out,pi_out):
        env = {'SCRIPT_NAME':sn_in,'PATH_INFO':pi_in}
        util.setup_testing_defaults(env)
        self.assertEqual(util.shift_path_info(env),part)
        self.assertEqual(env['PATH_INFO'],pi_out)
        self.assertEqual(env['SCRIPT_NAME'],sn_out)
        rudisha env

    eleza checkDefault(self, key, value, alt=Tupu):
        # Check defaulting when empty
        env = {}
        util.setup_testing_defaults(env)
        ikiwa isinstance(value, StringIO):
            self.assertIsInstance(env[key], StringIO)
        lasivyo isinstance(value,BytesIO):
            self.assertIsInstance(env[key],BytesIO)
        isipokua:
            self.assertEqual(env[key], value)

        # Check existing value
        env = {key:alt}
        util.setup_testing_defaults(env)
        self.assertIs(env[key], alt)

    eleza checkCrossDefault(self,key,value,**kw):
        util.setup_testing_defaults(kw)
        self.assertEqual(kw[key],value)

    eleza checkAppURI(self,uri,**kw):
        util.setup_testing_defaults(kw)
        self.assertEqual(util.application_uri(kw),uri)

    eleza checkReqURI(self,uri,query=1,**kw):
        util.setup_testing_defaults(kw)
        self.assertEqual(util.request_uri(kw,query),uri)

    @support.ignore_warnings(category=DeprecationWarning)
    eleza checkFW(self,text,size,match):

        eleza make_it(text=text,size=size):
            rudisha util.FileWrapper(StringIO(text),size)

        compare_generic_iter(make_it,match)

        it = make_it()
        self.assertUongo(it.filelike.closed)

        kila item kwenye it:
            pita

        self.assertUongo(it.filelike.closed)

        it.close()
        self.assertKweli(it.filelike.closed)

    eleza test_filewrapper_getitem_deprecation(self):
        wrapper = util.FileWrapper(StringIO('foobar'), 3)
        ukijumuisha self.assertWarnsRegex(DeprecationWarning,
                                   r'Use iterator protocol instead'):
            # This should have returned 'bar'.
            self.assertEqual(wrapper[1], 'foo')

    eleza testSimpleShifts(self):
        self.checkShift('','/', '', '/', '')
        self.checkShift('','/x', 'x', '/x', '')
        self.checkShift('/','', Tupu, '/', '')
        self.checkShift('/a','/x/y', 'x', '/a/x', '/y')
        self.checkShift('/a','/x/',  'x', '/a/x', '/')

    eleza testNormalizedShifts(self):
        self.checkShift('/a/b', '/../y', '..', '/a', '/y')
        self.checkShift('', '/../y', '..', '', '/y')
        self.checkShift('/a/b', '//y', 'y', '/a/b/y', '')
        self.checkShift('/a/b', '//y/', 'y', '/a/b/y', '/')
        self.checkShift('/a/b', '/./y', 'y', '/a/b/y', '')
        self.checkShift('/a/b', '/./y/', 'y', '/a/b/y', '/')
        self.checkShift('/a/b', '///./..//y/.//', '..', '/a', '/y/')
        self.checkShift('/a/b', '///', '', '/a/b/', '')
        self.checkShift('/a/b', '/.//', '', '/a/b/', '')
        self.checkShift('/a/b', '/x//', 'x', '/a/b/x', '/')
        self.checkShift('/a/b', '/.', Tupu, '/a/b', '')

    eleza testDefaults(self):
        kila key, value kwenye [
            ('SERVER_NAME','127.0.0.1'),
            ('SERVER_PORT', '80'),
            ('SERVER_PROTOCOL','HTTP/1.0'),
            ('HTTP_HOST','127.0.0.1'),
            ('REQUEST_METHOD','GET'),
            ('SCRIPT_NAME',''),
            ('PATH_INFO','/'),
            ('wsgi.version', (1,0)),
            ('wsgi.run_once', 0),
            ('wsgi.multithread', 0),
            ('wsgi.multiprocess', 0),
            ('wsgi.input', BytesIO()),
            ('wsgi.errors', StringIO()),
            ('wsgi.url_scheme','http'),
        ]:
            self.checkDefault(key,value)

    eleza testCrossDefaults(self):
        self.checkCrossDefault('HTTP_HOST',"foo.bar",SERVER_NAME="foo.bar")
        self.checkCrossDefault('wsgi.url_scheme',"https",HTTPS="on")
        self.checkCrossDefault('wsgi.url_scheme',"https",HTTPS="1")
        self.checkCrossDefault('wsgi.url_scheme',"https",HTTPS="yes")
        self.checkCrossDefault('wsgi.url_scheme',"http",HTTPS="foo")
        self.checkCrossDefault('SERVER_PORT',"80",HTTPS="foo")
        self.checkCrossDefault('SERVER_PORT',"443",HTTPS="on")

    eleza testGuessScheme(self):
        self.assertEqual(util.guess_scheme({}), "http")
        self.assertEqual(util.guess_scheme({'HTTPS':"foo"}), "http")
        self.assertEqual(util.guess_scheme({'HTTPS':"on"}), "https")
        self.assertEqual(util.guess_scheme({'HTTPS':"yes"}), "https")
        self.assertEqual(util.guess_scheme({'HTTPS':"1"}), "https")

    eleza testAppURIs(self):
        self.checkAppURI("http://127.0.0.1/")
        self.checkAppURI("http://127.0.0.1/spam", SCRIPT_NAME="/spam")
        self.checkAppURI("http://127.0.0.1/sp%E4m", SCRIPT_NAME="/sp\xe4m")
        self.checkAppURI("http://spam.example.com:2071/",
            HTTP_HOST="spam.example.com:2071", SERVER_PORT="2071")
        self.checkAppURI("http://spam.example.com/",
            SERVER_NAME="spam.example.com")
        self.checkAppURI("http://127.0.0.1/",
            HTTP_HOST="127.0.0.1", SERVER_NAME="spam.example.com")
        self.checkAppURI("https://127.0.0.1/", HTTPS="on")
        self.checkAppURI("http://127.0.0.1:8000/", SERVER_PORT="8000",
            HTTP_HOST=Tupu)

    eleza testReqURIs(self):
        self.checkReqURI("http://127.0.0.1/")
        self.checkReqURI("http://127.0.0.1/spam", SCRIPT_NAME="/spam")
        self.checkReqURI("http://127.0.0.1/sp%E4m", SCRIPT_NAME="/sp\xe4m")
        self.checkReqURI("http://127.0.0.1/spammity/spam",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam")
        self.checkReqURI("http://127.0.0.1/spammity/sp%E4m",
            SCRIPT_NAME="/spammity", PATH_INFO="/sp\xe4m")
        self.checkReqURI("http://127.0.0.1/spammity/spam;ham",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam;ham")
        self.checkReqURI("http://127.0.0.1/spammity/spam;cookie=1234,5678",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam;cookie=1234,5678")
        self.checkReqURI("http://127.0.0.1/spammity/spam?say=ni",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam",QUERY_STRING="say=ni")
        self.checkReqURI("http://127.0.0.1/spammity/spam?s%E4y=ni",
            SCRIPT_NAME="/spammity", PATH_INFO="/spam",QUERY_STRING="s%E4y=ni")
        self.checkReqURI("http://127.0.0.1/spammity/spam", 0,
            SCRIPT_NAME="/spammity", PATH_INFO="/spam",QUERY_STRING="say=ni")

    eleza testFileWrapper(self):
        self.checkFW("xyz"*50, 120, ["xyz"*40,"xyz"*10])

    eleza testHopByHop(self):
        kila hop kwenye (
            "Connection Keep-Alive Proxy-Authenticate Proxy-Authorization "
            "TE Trailers Transfer-Encoding Upgrade"
        ).split():
            kila alt kwenye hop, hop.title(), hop.upper(), hop.lower():
                self.assertKweli(util.is_hop_by_hop(alt))

        # Not comprehensive, just a few random header names
        kila hop kwenye (
            "Accept Cache-Control Date Pragma Trailer Via Warning"
        ).split():
            kila alt kwenye hop, hop.title(), hop.upper(), hop.lower():
                self.assertUongo(util.is_hop_by_hop(alt))

kundi HeaderTests(TestCase):

    eleza testMappingInterface(self):
        test = [('x','y')]
        self.assertEqual(len(Headers()), 0)
        self.assertEqual(len(Headers([])),0)
        self.assertEqual(len(Headers(test[:])),1)
        self.assertEqual(Headers(test[:]).keys(), ['x'])
        self.assertEqual(Headers(test[:]).values(), ['y'])
        self.assertEqual(Headers(test[:]).items(), test)
        self.assertIsNot(Headers(test).items(), test)  # must be copy!

        h = Headers()
        toa h['foo']   # should sio ashiria an error

        h['Foo'] = 'bar'
        kila m kwenye h.__contains__, h.get, h.get_all, h.__getitem__:
            self.assertKweli(m('foo'))
            self.assertKweli(m('Foo'))
            self.assertKweli(m('FOO'))
            self.assertUongo(m('bar'))

        self.assertEqual(h['foo'],'bar')
        h['foo'] = 'baz'
        self.assertEqual(h['FOO'],'baz')
        self.assertEqual(h.get_all('foo'),['baz'])

        self.assertEqual(h.get("foo","whee"), "baz")
        self.assertEqual(h.get("zoo","whee"), "whee")
        self.assertEqual(h.setdefault("foo","whee"), "baz")
        self.assertEqual(h.setdefault("zoo","whee"), "whee")
        self.assertEqual(h["foo"],"baz")
        self.assertEqual(h["zoo"],"whee")

    eleza testRequireList(self):
        self.assertRaises(TypeError, Headers, "foo")

    eleza testExtras(self):
        h = Headers()
        self.assertEqual(str(h),'\r\n')

        h.add_header('foo','bar',baz="spam")
        self.assertEqual(h['foo'], 'bar; baz="spam"')
        self.assertEqual(str(h),'foo: bar; baz="spam"\r\n\r\n')

        h.add_header('Foo','bar',cheese=Tupu)
        self.assertEqual(h.get_all('foo'),
            ['bar; baz="spam"', 'bar; cheese'])

        self.assertEqual(str(h),
            'foo: bar; baz="spam"\r\n'
            'Foo: bar; cheese\r\n'
            '\r\n'
        )

kundi ErrorHandler(BaseCGIHandler):
    """Simple handler subkundi kila testing BaseHandler"""

    # BaseHandler records the OS environment at agiza time, but envvars
    # might have been changed later by other tests, which trips up
    # HandlerTests.testEnviron().
    os_environ = dict(os.environ.items())

    eleza __init__(self,**kw):
        setup_testing_defaults(kw)
        BaseCGIHandler.__init__(
            self, BytesIO(), BytesIO(), StringIO(), kw,
            multithread=Kweli, multiprocess=Kweli
        )

kundi TestHandler(ErrorHandler):
    """Simple handler subkundi kila testing BaseHandler, w/error pitathru"""

    eleza handle_error(self):
        ashiria   # kila testing, we want to see what's happening


kundi HandlerTests(TestCase):
    # testEnviron() can produce long error message
    maxDiff = 80 * 50

    eleza testEnviron(self):
        os_environ = {
            # very basic environment
            'HOME': '/my/home',
            'PATH': '/my/path',
            'LANG': 'fr_FR.UTF-8',

            # set some WSGI variables
            'SCRIPT_NAME': 'test_script_name',
            'SERVER_NAME': 'test_server_name',
        }

        ukijumuisha support.swap_attr(TestHandler, 'os_environ', os_environ):
            # override X na HOME variables
            handler = TestHandler(X="Y", HOME="/override/home")
            handler.setup_environ()

        # Check that wsgi_xxx attributes are copied to wsgi.xxx variables
        # of handler.environ
        kila attr kwenye ('version', 'multithread', 'multiprocess', 'run_once',
                     'file_wrapper'):
            self.assertEqual(getattr(handler, 'wsgi_' + attr),
                             handler.environ['wsgi.' + attr])

        # Test handler.environ kama a dict
        expected = {}
        setup_testing_defaults(expected)
        # Handler inherits os_environ variables which are sio overriden
        # by SimpleHandler.add_cgi_vars() (SimpleHandler.base_env)
        kila key, value kwenye os_environ.items():
            ikiwa key haiko kwenye expected:
                expected[key] = value
        expected.update({
            # X doesn't exist kwenye os_environ
            "X": "Y",
            # HOME ni overridden by TestHandler
            'HOME': "/override/home",

            # overridden by setup_testing_defaults()
            "SCRIPT_NAME": "",
            "SERVER_NAME": "127.0.0.1",

            # set by BaseHandler.setup_environ()
            'wsgi.input': handler.get_stdin(),
            'wsgi.errors': handler.get_stderr(),
            'wsgi.version': (1, 0),
            'wsgi.run_once': Uongo,
            'wsgi.url_scheme': 'http',
            'wsgi.multithread': Kweli,
            'wsgi.multiprocess': Kweli,
            'wsgi.file_wrapper': util.FileWrapper,
        })
        self.assertDictEqual(handler.environ, expected)

    eleza testCGIEnviron(self):
        h = BaseCGIHandler(Tupu,Tupu,Tupu,{})
        h.setup_environ()
        kila key kwenye 'wsgi.url_scheme', 'wsgi.input', 'wsgi.errors':
            self.assertIn(key, h.environ)

    eleza testScheme(self):
        h=TestHandler(HTTPS="on"); h.setup_environ()
        self.assertEqual(h.environ['wsgi.url_scheme'],'https')
        h=TestHandler(); h.setup_environ()
        self.assertEqual(h.environ['wsgi.url_scheme'],'http')

    eleza testAbstractMethods(self):
        h = BaseHandler()
        kila name kwenye [
            '_flush','get_stdin','get_stderr','add_cgi_vars'
        ]:
            self.assertRaises(NotImplementedError, getattr(h,name))
        self.assertRaises(NotImplementedError, h._write, "test")

    eleza testContentLength(self):
        # Demo one reason iteration ni better than write()...  ;)

        eleza trivial_app1(e,s):
            s('200 OK',[])
            rudisha [e['wsgi.url_scheme'].encode('iso-8859-1')]

        eleza trivial_app2(e,s):
            s('200 OK',[])(e['wsgi.url_scheme'].encode('iso-8859-1'))
            rudisha []

        eleza trivial_app3(e,s):
            s('200 OK',[])
            rudisha ['\u0442\u0435\u0441\u0442'.encode("utf-8")]

        eleza trivial_app4(e,s):
            # Simulate a response to a HEAD request
            s('200 OK',[('Content-Length', '12345')])
            rudisha []

        h = TestHandler()
        h.run(trivial_app1)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: 200 OK\r\n"
            "Content-Length: 4\r\n"
            "\r\n"
            "http").encode("iso-8859-1"))

        h = TestHandler()
        h.run(trivial_app2)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: 200 OK\r\n"
            "\r\n"
            "http").encode("iso-8859-1"))

        h = TestHandler()
        h.run(trivial_app3)
        self.assertEqual(h.stdout.getvalue(),
            b'Status: 200 OK\r\n'
            b'Content-Length: 8\r\n'
            b'\r\n'
            b'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82')

        h = TestHandler()
        h.run(trivial_app4)
        self.assertEqual(h.stdout.getvalue(),
            b'Status: 200 OK\r\n'
            b'Content-Length: 12345\r\n'
            b'\r\n')

    eleza testBasicErrorOutput(self):

        eleza non_error_app(e,s):
            s('200 OK',[])
            rudisha []

        eleza error_app(e,s):
            ashiria AssertionError("This should be caught by handler")

        h = ErrorHandler()
        h.run(non_error_app)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: 200 OK\r\n"
            "Content-Length: 0\r\n"
            "\r\n").encode("iso-8859-1"))
        self.assertEqual(h.stderr.getvalue(),"")

        h = ErrorHandler()
        h.run(error_app)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: %s\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: %d\r\n"
            "\r\n" % (h.error_status,len(h.error_body))).encode('iso-8859-1')
            + h.error_body)

        self.assertIn("AssertionError", h.stderr.getvalue())

    eleza testErrorAfterOutput(self):
        MSG = b"Some output has been sent"
        eleza error_app(e,s):
            s("200 OK",[])(MSG)
            ashiria AssertionError("This should be caught by handler")

        h = ErrorHandler()
        h.run(error_app)
        self.assertEqual(h.stdout.getvalue(),
            ("Status: 200 OK\r\n"
            "\r\n".encode("iso-8859-1")+MSG))
        self.assertIn("AssertionError", h.stderr.getvalue())

    eleza testHeaderFormats(self):

        eleza non_error_app(e,s):
            s('200 OK',[])
            rudisha []

        stdpat = (
            r"HTTP/%s 200 OK\r\n"
            r"Date: \w{3}, [ 0123]\d \w{3} \d{4} \d\d:\d\d:\d\d GMT\r\n"
            r"%s" r"Content-Length: 0\r\n" r"\r\n"
        )
        shortpat = (
            "Status: 200 OK\r\n" "Content-Length: 0\r\n" "\r\n"
        ).encode("iso-8859-1")

        kila ssw kwenye "FooBar/1.0", Tupu:
            sw = ssw na "Server: %s\r\n" % ssw ama ""

            kila version kwenye "1.0", "1.1":
                kila proto kwenye "HTTP/0.9", "HTTP/1.0", "HTTP/1.1":

                    h = TestHandler(SERVER_PROTOCOL=proto)
                    h.origin_server = Uongo
                    h.http_version = version
                    h.server_software = ssw
                    h.run(non_error_app)
                    self.assertEqual(shortpat,h.stdout.getvalue())

                    h = TestHandler(SERVER_PROTOCOL=proto)
                    h.origin_server = Kweli
                    h.http_version = version
                    h.server_software = ssw
                    h.run(non_error_app)
                    ikiwa proto=="HTTP/0.9":
                        self.assertEqual(h.stdout.getvalue(),b"")
                    isipokua:
                        self.assertKweli(
                            re.match((stdpat%(version,sw)).encode("iso-8859-1"),
                                h.stdout.getvalue()),
                            ((stdpat%(version,sw)).encode("iso-8859-1"),
                                h.stdout.getvalue())
                        )

    eleza testBytesData(self):
        eleza app(e, s):
            s("200 OK", [
                ("Content-Type", "text/plain; charset=utf-8"),
                ])
            rudisha [b"data"]

        h = TestHandler()
        h.run(app)
        self.assertEqual(b"Status: 200 OK\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"Content-Length: 4\r\n"
            b"\r\n"
            b"data",
            h.stdout.getvalue())

    eleza testCloseOnError(self):
        side_effects = {'close_called': Uongo}
        MSG = b"Some output has been sent"
        eleza error_app(e,s):
            s("200 OK",[])(MSG)
            kundi CrashyIterable(object):
                eleza __iter__(self):
                    wakati Kweli:
                        tuma b'blah'
                        ashiria AssertionError("This should be caught by handler")
                eleza close(self):
                    side_effects['close_called'] = Kweli
            rudisha CrashyIterable()

        h = ErrorHandler()
        h.run(error_app)
        self.assertEqual(side_effects['close_called'], Kweli)

    eleza testPartialWrite(self):
        written = bytearray()

        kundi PartialWriter:
            eleza write(self, b):
                partial = b[:7]
                written.extend(partial)
                rudisha len(partial)

            eleza flush(self):
                pita

        environ = {"SERVER_PROTOCOL": "HTTP/1.0"}
        h = SimpleHandler(BytesIO(), PartialWriter(), sys.stderr, environ)
        msg = "should sio do partial writes"
        ukijumuisha self.assertWarnsRegex(DeprecationWarning, msg):
            h.run(hello_app)
        self.assertEqual(b"HTTP/1.0 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Date: Mon, 05 Jun 2006 18:49:54 GMT\r\n"
            b"Content-Length: 13\r\n"
            b"\r\n"
            b"Hello, world!",
            written)

    eleza testClientConnectionTerminations(self):
        environ = {"SERVER_PROTOCOL": "HTTP/1.0"}
        kila exception kwenye (
            ConnectionAbortedError,
            BrokenPipeError,
            ConnectionResetError,
        ):
            ukijumuisha self.subTest(exception=exception):
                kundi AbortingWriter:
                    eleza write(self, b):
                        ashiria exception

                stderr = StringIO()
                h = SimpleHandler(BytesIO(), AbortingWriter(), stderr, environ)
                h.run(hello_app)

                self.assertUongo(stderr.getvalue())

    eleza testDontResetInternalStateOnException(self):
        kundi CustomException(ValueError):
            pita

        # We are raising CustomException here to trigger an exception
        # during the execution of SimpleHandler.finish_response(), so
        # we can easily test that the internal state of the handler is
        # preserved kwenye case of an exception.
        kundi AbortingWriter:
            eleza write(self, b):
                ashiria CustomException

        stderr = StringIO()
        environ = {"SERVER_PROTOCOL": "HTTP/1.0"}
        h = SimpleHandler(BytesIO(), AbortingWriter(), stderr, environ)
        h.run(hello_app)

        self.assertIn("CustomException", stderr.getvalue())

        # Test that the internal state of the handler ni preserved.
        self.assertIsNotTupu(h.result)
        self.assertIsNotTupu(h.headers)
        self.assertIsNotTupu(h.status)
        self.assertIsNotTupu(h.environ)


ikiwa __name__ == "__main__":
    unittest.main()
