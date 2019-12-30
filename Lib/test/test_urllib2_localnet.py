agiza base64
agiza os
agiza email
agiza urllib.parse
agiza urllib.request
agiza http.server
agiza threading
agiza unittest
agiza hashlib

kutoka test agiza support

jaribu:
    agiza ssl
except ImportError:
    ssl = Tupu

here = os.path.dirname(__file__)
# Self-signed cert file kila 'localhost'
CERT_localhost = os.path.join(here, 'keycert.pem')
# Self-signed cert file kila 'fakehostname'
CERT_fakehostname = os.path.join(here, 'keycert2.pem')


# Loopback http server infrastructure

kundi LoopbackHttpServer(http.server.HTTPServer):
    """HTTP server w/ a few modifications that make it useful for
    loopback testing purposes.
    """

    eleza __init__(self, server_address, RequestHandlerClass):
        http.server.HTTPServer.__init__(self,
                                        server_address,
                                        RequestHandlerClass)

        # Set the timeout of our listening socket really low so
        # that we can stop the server easily.
        self.socket.settimeout(0.1)

    eleza get_request(self):
        """HTTPServer method, overridden."""

        request, client_address = self.socket.accept()

        # It's a loopback connection, so setting the timeout
        # really low shouldn't affect anything, but should make
        # deadlocks less likely to occur.
        request.settimeout(10.0)

        rudisha (request, client_address)

kundi LoopbackHttpServerThread(threading.Thread):
    """Stoppable thread that runs a loopback http server."""

    eleza __init__(self, request_handler):
        threading.Thread.__init__(self)
        self._stop_server = Uongo
        self.ready = threading.Event()
        request_handler.protocol_version = "HTTP/1.0"
        self.httpd = LoopbackHttpServer(("127.0.0.1", 0),
                                        request_handler)
        self.port = self.httpd.server_port

    eleza stop(self):
        """Stops the webserver ikiwa it's currently running."""

        self._stop_server = Kweli

        self.join()
        self.httpd.server_close()

    eleza run(self):
        self.ready.set()
        wakati sio self._stop_server:
            self.httpd.handle_request()

# Authentication infrastructure

kundi DigestAuthHandler:
    """Handler kila performing digest authentication."""

    eleza __init__(self):
        self._request_num = 0
        self._nonces = []
        self._users = {}
        self._realm_name = "Test Realm"
        self._qop = "auth"

    eleza set_qop(self, qop):
        self._qop = qop

    eleza set_users(self, users):
        assert isinstance(users, dict)
        self._users = users

    eleza set_realm(self, realm):
        self._realm_name = realm

    eleza _generate_nonce(self):
        self._request_num += 1
        nonce = hashlib.md5(str(self._request_num).encode("ascii")).hexdigest()
        self._nonces.append(nonce)
        rudisha nonce

    eleza _create_auth_dict(self, auth_str):
        first_space_index = auth_str.find(" ")
        auth_str = auth_str[first_space_index+1:]

        parts = auth_str.split(",")

        auth_dict = {}
        kila part kwenye parts:
            name, value = part.split("=")
            name = name.strip()
            ikiwa value[0] == '"' na value[-1] == '"':
                value = value[1:-1]
            isipokua:
                value = value.strip()
            auth_dict[name] = value
        rudisha auth_dict

    eleza _validate_auth(self, auth_dict, password, method, uri):
        final_dict = {}
        final_dict.update(auth_dict)
        final_dict["password"] = password
        final_dict["method"] = method
        final_dict["uri"] = uri
        HA1_str = "%(username)s:%(realm)s:%(password)s" % final_dict
        HA1 = hashlib.md5(HA1_str.encode("ascii")).hexdigest()
        HA2_str = "%(method)s:%(uri)s" % final_dict
        HA2 = hashlib.md5(HA2_str.encode("ascii")).hexdigest()
        final_dict["HA1"] = HA1
        final_dict["HA2"] = HA2
        response_str = "%(HA1)s:%(nonce)s:%(nc)s:" \
                       "%(cnonce)s:%(qop)s:%(HA2)s" % final_dict
        response = hashlib.md5(response_str.encode("ascii")).hexdigest()

        rudisha response == auth_dict["response"]

    eleza _return_auth_challenge(self, request_handler):
        request_handler.send_response(407, "Proxy Authentication Required")
        request_handler.send_header("Content-Type", "text/html")
        request_handler.send_header(
            'Proxy-Authenticate', 'Digest realm="%s", '
            'qop="%s",'
            'nonce="%s", ' % \
            (self._realm_name, self._qop, self._generate_nonce()))
        # XXX: Not sure ikiwa we're supposed to add this next header or
        # not.
        #request_handler.send_header('Connection', 'close')
        request_handler.end_headers()
        request_handler.wfile.write(b"Proxy Authentication Required.")
        rudisha Uongo

    eleza handle_request(self, request_handler):
        """Performs digest authentication on the given HTTP request
        handler.  Returns Kweli ikiwa authentication was successful, Uongo
        otherwise.

        If no users have been set, then digest auth ni effectively
        disabled na this method will always rudisha Kweli.
        """

        ikiwa len(self._users) == 0:
            rudisha Kweli

        ikiwa "Proxy-Authorization" sio kwenye request_handler.headers:
            rudisha self._return_auth_challenge(request_handler)
        isipokua:
            auth_dict = self._create_auth_dict(
                request_handler.headers["Proxy-Authorization"]
                )
            ikiwa auth_dict["username"] kwenye self._users:
                password = self._users[ auth_dict["username"] ]
            isipokua:
                rudisha self._return_auth_challenge(request_handler)
            ikiwa sio auth_dict.get("nonce") kwenye self._nonces:
                rudisha self._return_auth_challenge(request_handler)
            isipokua:
                self._nonces.remove(auth_dict["nonce"])

            auth_validated = Uongo

            # MSIE uses short_path kwenye its validation, but Python's
            # urllib.request uses the full path, so we're going to see if
            # either of them works here.

            kila path kwenye [request_handler.path, request_handler.short_path]:
                ikiwa self._validate_auth(auth_dict,
                                       password,
                                       request_handler.command,
                                       path):
                    auth_validated = Kweli

            ikiwa sio auth_validated:
                rudisha self._return_auth_challenge(request_handler)
            rudisha Kweli


kundi BasicAuthHandler(http.server.BaseHTTPRequestHandler):
    """Handler kila performing basic authentication."""
    # Server side values
    USER = 'testUser'
    PASSWD = 'testPass'
    REALM = 'Test'
    USER_PASSWD = "%s:%s" % (USER, PASSWD)
    ENCODED_AUTH = base64.b64encode(USER_PASSWD.encode('ascii')).decode('ascii')

    eleza __init__(self, *args, **kwargs):
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    eleza log_message(self, format, *args):
        # Suppress console log message
        pass

    eleza do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    eleza do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic realm=\"%s\"" % self.REALM)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    eleza do_GET(self):
        ikiwa sio self.headers.get("Authorization", ""):
            self.do_AUTHHEAD()
            self.wfile.write(b"No Auth header received")
        elikiwa self.headers.get(
                "Authorization", "") == "Basic " + self.ENCODED_AUTH:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"It works")
        isipokua:
            # Request Unauthorized
            self.do_AUTHHEAD()



# Proxy test infrastructure

kundi FakeProxyHandler(http.server.BaseHTTPRequestHandler):
    """This ni a 'fake proxy' that makes it look like the entire
    internet has gone down due to a sudden zombie invasion.  It main
    utility ni kwenye providing us ukijumuisha authentication support for
    testing.
    """

    eleza __init__(self, digest_auth_handler, *args, **kwargs):
        # This has to be set before calling our parent's __init__(), which will
        # try to call do_GET().
        self.digest_auth_handler = digest_auth_handler
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    eleza log_message(self, format, *args):
        # Uncomment the next line kila debugging.
        # sys.stderr.write(format % args)
        pass

    eleza do_GET(self):
        (scm, netloc, path, params, query, fragment) = urllib.parse.urlparse(
            self.path, "http")
        self.short_path = path
        ikiwa self.digest_auth_handler.handle_request(self):
            self.send_response(200, "OK")
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("You've reached %s!<BR>" % self.path,
                                   "ascii"))
            self.wfile.write(b"Our apologies, but our server ni down due to "
                             b"a sudden zombie invasion.")

# Test cases

kundi BasicAuthTests(unittest.TestCase):
    USER = "testUser"
    PASSWD = "testPass"
    INCORRECT_PASSWD = "Incorrect"
    REALM = "Test"

    eleza setUp(self):
        super(BasicAuthTests, self).setUp()
        # With Basic Authentication
        eleza http_server_with_basic_auth_handler(*args, **kwargs):
            rudisha BasicAuthHandler(*args, **kwargs)
        self.server = LoopbackHttpServerThread(http_server_with_basic_auth_handler)
        self.addCleanup(self.stop_server)
        self.server_url = 'http://127.0.0.1:%s' % self.server.port
        self.server.start()
        self.server.ready.wait()

    eleza stop_server(self):
        self.server.stop()
        self.server = Tupu

    eleza tearDown(self):
        super(BasicAuthTests, self).tearDown()

    eleza test_basic_auth_success(self):
        ah = urllib.request.HTTPBasicAuthHandler()
        ah.add_password(self.REALM, self.server_url, self.USER, self.PASSWD)
        urllib.request.install_opener(urllib.request.build_opener(ah))
        jaribu:
            self.assertKweli(urllib.request.urlopen(self.server_url))
        except urllib.error.HTTPError:
            self.fail("Basic auth failed kila the url: %s" % self.server_url)

    eleza test_basic_auth_httperror(self):
        ah = urllib.request.HTTPBasicAuthHandler()
        ah.add_password(self.REALM, self.server_url, self.USER, self.INCORRECT_PASSWD)
        urllib.request.install_opener(urllib.request.build_opener(ah))
        self.assertRaises(urllib.error.HTTPError, urllib.request.urlopen, self.server_url)


kundi ProxyAuthTests(unittest.TestCase):
    URL = "http://localhost"

    USER = "tester"
    PASSWD = "test123"
    REALM = "TestRealm"

    @support.requires_hashdigest("md5")
    eleza setUp(self):
        super(ProxyAuthTests, self).setUp()
        # Ignore proxy bypass settings kwenye the environment.
        eleza restore_environ(old_environ):
            os.environ.clear()
            os.environ.update(old_environ)
        self.addCleanup(restore_environ, os.environ.copy())
        os.environ['NO_PROXY'] = ''
        os.environ['no_proxy'] = ''

        self.digest_auth_handler = DigestAuthHandler()
        self.digest_auth_handler.set_users({self.USER: self.PASSWD})
        self.digest_auth_handler.set_realm(self.REALM)
        # With Digest Authentication.
        eleza create_fake_proxy_handler(*args, **kwargs):
            rudisha FakeProxyHandler(self.digest_auth_handler, *args, **kwargs)

        self.server = LoopbackHttpServerThread(create_fake_proxy_handler)
        self.addCleanup(self.stop_server)
        self.server.start()
        self.server.ready.wait()
        proxy_url = "http://127.0.0.1:%d" % self.server.port
        handler = urllib.request.ProxyHandler({"http" : proxy_url})
        self.proxy_digest_handler = urllib.request.ProxyDigestAuthHandler()
        self.opener = urllib.request.build_opener(
            handler, self.proxy_digest_handler)

    eleza stop_server(self):
        self.server.stop()
        self.server = Tupu

    eleza test_proxy_with_bad_password_raises_httperror(self):
        self.proxy_digest_handler.add_password(self.REALM, self.URL,
                                               self.USER, self.PASSWD+"bad")
        self.digest_auth_handler.set_qop("auth")
        self.assertRaises(urllib.error.HTTPError,
                          self.opener.open,
                          self.URL)

    eleza test_proxy_with_no_password_raises_httperror(self):
        self.digest_auth_handler.set_qop("auth")
        self.assertRaises(urllib.error.HTTPError,
                          self.opener.open,
                          self.URL)

    eleza test_proxy_qop_auth_works(self):
        self.proxy_digest_handler.add_password(self.REALM, self.URL,
                                               self.USER, self.PASSWD)
        self.digest_auth_handler.set_qop("auth")
        ukijumuisha self.opener.open(self.URL) as result:
            wakati result.read():
                pass

    eleza test_proxy_qop_auth_int_works_or_throws_urlerror(self):
        self.proxy_digest_handler.add_password(self.REALM, self.URL,
                                               self.USER, self.PASSWD)
        self.digest_auth_handler.set_qop("auth-int")
        jaribu:
            result = self.opener.open(self.URL)
        except urllib.error.URLError:
            # It's okay ikiwa we don't support auth-int, but we certainly
            # shouldn't receive any kind of exception here other than
            # a URLError.
            pass
        isipokua:
            ukijumuisha result:
                wakati result.read():
                    pass


eleza GetRequestHandler(responses):

    kundi FakeHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

        server_version = "TestHTTP/"
        requests = []
        headers_received = []
        port = 80

        eleza do_GET(self):
            body = self.send_head()
            wakati body:
                done = self.wfile.write(body)
                body = body[done:]

        eleza do_POST(self):
            content_length = self.headers["Content-Length"]
            post_data = self.rfile.read(int(content_length))
            self.do_GET()
            self.requests.append(post_data)

        eleza send_head(self):
            FakeHTTPRequestHandler.headers_received = self.headers
            self.requests.append(self.path)
            response_code, headers, body = responses.pop(0)

            self.send_response(response_code)

            kila (header, value) kwenye headers:
                self.send_header(header, value % {'port':self.port})
            ikiwa body:
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                rudisha body
            self.end_headers()

        eleza log_message(self, *args):
            pass


    rudisha FakeHTTPRequestHandler


kundi TestUrlopen(unittest.TestCase):
    """Tests urllib.request.urlopen using the network.

    These tests are sio exhaustive.  Assuming that testing using files does a
    good job overall of some of the basic interface features.  There are no
    tests exercising the optional 'data' na 'proxies' arguments.  No tests
    kila transparent redirection have been written.
    """

    eleza setUp(self):
        super(TestUrlopen, self).setUp()

        # Ignore proxies kila localhost tests.
        eleza restore_environ(old_environ):
            os.environ.clear()
            os.environ.update(old_environ)
        self.addCleanup(restore_environ, os.environ.copy())
        os.environ['NO_PROXY'] = '*'
        os.environ['no_proxy'] = '*'

    eleza urlopen(self, url, data=Tupu, **kwargs):
        l = []
        f = urllib.request.urlopen(url, data, **kwargs)
        jaribu:
            # Exercise various methods
            l.extend(f.readlines(200))
            l.append(f.readline())
            l.append(f.read(1024))
            l.append(f.read())
        mwishowe:
            f.close()
        rudisha b"".join(l)

    eleza stop_server(self):
        self.server.stop()
        self.server = Tupu

    eleza start_server(self, responses=Tupu):
        ikiwa responses ni Tupu:
            responses = [(200, [], b"we don't care")]
        handler = GetRequestHandler(responses)

        self.server = LoopbackHttpServerThread(handler)
        self.addCleanup(self.stop_server)
        self.server.start()
        self.server.ready.wait()
        port = self.server.port
        handler.port = port
        rudisha handler

    eleza start_https_server(self, responses=Tupu, **kwargs):
        ikiwa sio hasattr(urllib.request, 'HTTPSHandler'):
            self.skipTest('ssl support required')
        kutoka test.ssl_servers agiza make_https_server
        ikiwa responses ni Tupu:
            responses = [(200, [], b"we care a bit")]
        handler = GetRequestHandler(responses)
        server = make_https_server(self, handler_class=handler, **kwargs)
        handler.port = server.port
        rudisha handler

    eleza test_redirection(self):
        expected_response = b"We got here..."
        responses = [
            (302, [("Location", "http://localhost:%(port)s/somewhere_else")],
             ""),
            (200, [], expected_response)
        ]

        handler = self.start_server(responses)
        data = self.urlopen("http://localhost:%s/" % handler.port)
        self.assertEqual(data, expected_response)
        self.assertEqual(handler.requests, ["/", "/somewhere_else"])

    eleza test_chunked(self):
        expected_response = b"hello world"
        chunked_start = (
                        b'a\r\n'
                        b'hello worl\r\n'
                        b'1\r\n'
                        b'd\r\n'
                        b'0\r\n'
                        )
        response = [(200, [("Transfer-Encoding", "chunked")], chunked_start)]
        handler = self.start_server(response)
        data = self.urlopen("http://localhost:%s/" % handler.port)
        self.assertEqual(data, expected_response)

    eleza test_404(self):
        expected_response = b"Bad bad bad..."
        handler = self.start_server([(404, [], expected_response)])

        jaribu:
            self.urlopen("http://localhost:%s/weeble" % handler.port)
        except urllib.error.URLError as f:
            data = f.read()
            f.close()
        isipokua:
            self.fail("404 should  ashiria URLError")

        self.assertEqual(data, expected_response)
        self.assertEqual(handler.requests, ["/weeble"])

    eleza test_200(self):
        expected_response = b"pycon 2008..."
        handler = self.start_server([(200, [], expected_response)])
        data = self.urlopen("http://localhost:%s/bizarre" % handler.port)
        self.assertEqual(data, expected_response)
        self.assertEqual(handler.requests, ["/bizarre"])

    eleza test_200_with_parameters(self):
        expected_response = b"pycon 2008..."
        handler = self.start_server([(200, [], expected_response)])
        data = self.urlopen("http://localhost:%s/bizarre" % handler.port,
                             b"get=with_feeling")
        self.assertEqual(data, expected_response)
        self.assertEqual(handler.requests, ["/bizarre", b"get=with_feeling"])

    eleza test_https(self):
        handler = self.start_https_server()
        context = ssl.create_default_context(cafile=CERT_localhost)
        data = self.urlopen("https://localhost:%s/bizarre" % handler.port, context=context)
        self.assertEqual(data, b"we care a bit")

    eleza test_https_with_cafile(self):
        handler = self.start_https_server(certfile=CERT_localhost)
        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            # Good cert
            data = self.urlopen("https://localhost:%s/bizarre" % handler.port,
                                cafile=CERT_localhost)
            self.assertEqual(data, b"we care a bit")
            # Bad cert
            ukijumuisha self.assertRaises(urllib.error.URLError) as cm:
                self.urlopen("https://localhost:%s/bizarre" % handler.port,
                             cafile=CERT_fakehostname)
            # Good cert, but mismatching hostname
            handler = self.start_https_server(certfile=CERT_fakehostname)
            ukijumuisha self.assertRaises(urllib.error.URLError) as cm:
                self.urlopen("https://localhost:%s/bizarre" % handler.port,
                             cafile=CERT_fakehostname)

    eleza test_https_with_cadefault(self):
        handler = self.start_https_server(certfile=CERT_localhost)
        # Self-signed cert should fail verification ukijumuisha system certificate store
        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            ukijumuisha self.assertRaises(urllib.error.URLError) as cm:
                self.urlopen("https://localhost:%s/bizarre" % handler.port,
                             cadefault=Kweli)

    eleza test_https_sni(self):
        ikiwa ssl ni Tupu:
            self.skipTest("ssl module required")
        ikiwa sio ssl.HAS_SNI:
            self.skipTest("SNI support required kwenye OpenSSL")
        sni_name = Tupu
        eleza cb_sni(ssl_sock, server_name, initial_context):
            nonlocal sni_name
            sni_name = server_name
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.set_servername_callback(cb_sni)
        handler = self.start_https_server(context=context, certfile=CERT_localhost)
        context = ssl.create_default_context(cafile=CERT_localhost)
        self.urlopen("https://localhost:%s" % handler.port, context=context)
        self.assertEqual(sni_name, "localhost")

    eleza test_sending_headers(self):
        handler = self.start_server()
        req = urllib.request.Request("http://localhost:%s/" % handler.port,
                                     headers={"Range": "bytes=20-39"})
        ukijumuisha urllib.request.urlopen(req):
            pass
        self.assertEqual(handler.headers_received["Range"], "bytes=20-39")

    eleza test_basic(self):
        handler = self.start_server()
        ukijumuisha urllib.request.urlopen("http://localhost:%s" % handler.port) as open_url:
            kila attr kwenye ("read", "close", "info", "geturl"):
                self.assertKweli(hasattr(open_url, attr), "object returned kutoka "
                             "urlopen lacks the %s attribute" % attr)
            self.assertKweli(open_url.read(), "calling 'read' failed")

    eleza test_info(self):
        handler = self.start_server()
        open_url = urllib.request.urlopen(
            "http://localhost:%s" % handler.port)
        ukijumuisha open_url:
            info_obj = open_url.info()
        self.assertIsInstance(info_obj, email.message.Message,
                              "object returned by 'info' ni sio an "
                              "instance of email.message.Message")
        self.assertEqual(info_obj.get_content_subtype(), "plain")

    eleza test_geturl(self):
        # Make sure same URL as opened ni returned by geturl.
        handler = self.start_server()
        open_url = urllib.request.urlopen("http://localhost:%s" % handler.port)
        ukijumuisha open_url:
            url = open_url.geturl()
        self.assertEqual(url, "http://localhost:%s" % handler.port)

    eleza test_iteration(self):
        expected_response = b"pycon 2008..."
        handler = self.start_server([(200, [], expected_response)])
        data = urllib.request.urlopen("http://localhost:%s" % handler.port)
        kila line kwenye data:
            self.assertEqual(line, expected_response)

    eleza test_line_iteration(self):
        lines = [b"We\n", b"got\n", b"here\n", b"verylong " * 8192 + b"\n"]
        expected_response = b"".join(lines)
        handler = self.start_server([(200, [], expected_response)])
        data = urllib.request.urlopen("http://localhost:%s" % handler.port)
        kila index, line kwenye enumerate(data):
            self.assertEqual(line, lines[index],
                             "Fetched line number %s doesn't match expected:\n"
                             "    Expected length was %s, got %s" %
                             (index, len(lines[index]), len(line)))
        self.assertEqual(index + 1, len(lines))


threads_key = Tupu

eleza setUpModule():
    # Store the threading_setup kwenye a key na ensure that it ni cleaned up
    # kwenye the tearDown
    global threads_key
    threads_key = support.threading_setup()

eleza tearDownModule():
    ikiwa threads_key:
        support.threading_cleanup(*threads_key)

ikiwa __name__ == "__main__":
    unittest.main()
