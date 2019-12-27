agiza os
agiza sys
agiza ssl
agiza pprint
agiza threading
agiza urllib.parse
# Rename HTTPServer to _HTTPServer so as to avoid confusion with HTTPSServer.
kutoka http.server agiza (HTTPServer as _HTTPServer,
    SimpleHTTPRequestHandler, BaseHTTPRequestHandler)

kutoka test agiza support

here = os.path.dirname(__file__)

HOST = support.HOST
CERTFILE = os.path.join(here, 'keycert.pem')

# This one's based on HTTPServer, which is based on socketserver

kundi HTTPSServer(_HTTPServer):

    eleza __init__(self, server_address, handler_class, context):
        _HTTPServer.__init__(self, server_address, handler_class)
        self.context = context

    eleza __str__(self):
        rudisha ('<%s %s:%s>' %
                (self.__class__.__name__,
                 self.server_name,
                 self.server_port))

    eleza get_request(self):
        # override this to wrap socket with SSL
        try:
            sock, addr = self.socket.accept()
            sslconn = self.context.wrap_socket(sock, server_side=True)
        except OSError as e:
            # socket errors are silenced by the caller, print them here
            ikiwa support.verbose:
                sys.stderr.write("Got an error:\n%s\n" % e)
            raise
        rudisha sslconn, addr

kundi RootedHTTPRequestHandler(SimpleHTTPRequestHandler):
    # need to override translate_path to get a known root,
    # instead of using os.curdir, since the test could be
    # run kutoka anywhere

    server_version = "TestHTTPS/1.0"
    root = here
    # Avoid hanging when a request gets interrupted by the client
    timeout = 5

    eleza translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = urllib.parse.urlparse(path)[2]
        path = os.path.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.root
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            path = os.path.join(path, word)
        rudisha path

    eleza log_message(self, format, *args):
        # we override this to suppress logging unless "verbose"
        ikiwa support.verbose:
            sys.stdout.write(" server (%s:%d %s):\n   [%s] %s\n" %
                             (self.server.server_address,
                              self.server.server_port,
                              self.request.cipher(),
                              self.log_date_time_string(),
                              format%args))


kundi StatsRequestHandler(BaseHTTPRequestHandler):
    """Example HTTP request handler which returns SSL statistics on GET
    requests.
    """

    server_version = "StatsHTTPS/1.0"

    eleza do_GET(self, send_body=True):
        """Serve a GET request."""
        sock = self.rfile.raw._sock
        context = sock.context
        stats = {
            'session_cache': context.session_stats(),
            'cipher': sock.cipher(),
            'compression': sock.compression(),
            }
        body = pprint.pformat(stats)
        body = body.encode('utf-8')
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        ikiwa send_body:
            self.wfile.write(body)

    eleza do_HEAD(self):
        """Serve a HEAD request."""
        self.do_GET(send_body=False)

    eleza log_request(self, format, *args):
        ikiwa support.verbose:
            BaseHTTPRequestHandler.log_request(self, format, *args)


kundi HTTPSServerThread(threading.Thread):

    eleza __init__(self, context, host=HOST, handler_class=None):
        self.flag = None
        self.server = HTTPSServer((host, 0),
                                  handler_kundi or RootedHTTPRequestHandler,
                                  context)
        self.port = self.server.server_port
        threading.Thread.__init__(self)
        self.daemon = True

    eleza __str__(self):
        rudisha "<%s %s>" % (self.__class__.__name__, self.server)

    eleza start(self, flag=None):
        self.flag = flag
        threading.Thread.start(self)

    eleza run(self):
        ikiwa self.flag:
            self.flag.set()
        try:
            self.server.serve_forever(0.05)
        finally:
            self.server.server_close()

    eleza stop(self):
        self.server.shutdown()


eleza make_https_server(case, *, context=None, certfile=CERTFILE,
                      host=HOST, handler_class=None):
    ikiwa context is None:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # We assume the certfile contains both private key and certificate
    context.load_cert_chain(certfile)
    server = HTTPSServerThread(context, host, handler_class)
    flag = threading.Event()
    server.start(flag)
    flag.wait()
    eleza cleanup():
        ikiwa support.verbose:
            sys.stdout.write('stopping HTTPS server\n')
        server.stop()
        ikiwa support.verbose:
            sys.stdout.write('joining HTTPS thread\n')
        server.join()
    case.addCleanup(cleanup)
    rudisha server


ikiwa __name__ == "__main__":
    agiza argparse
    parser = argparse.ArgumentParser(
        description='Run a test HTTPS server. '
                    'By default, the current directory is served.')
    parser.add_argument('-p', '--port', type=int, default=4433,
                        help='port to listen on (default: %(default)s)')
    parser.add_argument('-q', '--quiet', dest='verbose', default=True,
                        action='store_false', help='be less verbose')
    parser.add_argument('-s', '--stats', dest='use_stats_handler', default=False,
                        action='store_true', help='always rudisha stats page')
    parser.add_argument('--curve-name', dest='curve_name', type=str,
                        action='store',
                        help='curve name for EC-based Diffie-Hellman')
    parser.add_argument('--ciphers', dest='ciphers', type=str,
                        help='allowed cipher list')
    parser.add_argument('--dh', dest='dh_file', type=str, action='store',
                        help='PEM file containing DH parameters')
    args = parser.parse_args()

    support.verbose = args.verbose
    ikiwa args.use_stats_handler:
        handler_kundi = StatsRequestHandler
    else:
        handler_kundi = RootedHTTPRequestHandler
        handler_class.root = os.getcwd()
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(CERTFILE)
    ikiwa args.curve_name:
        context.set_ecdh_curve(args.curve_name)
    ikiwa args.dh_file:
        context.load_dh_params(args.dh_file)
    ikiwa args.ciphers:
        context.set_ciphers(args.ciphers)

    server = HTTPSServer(("", args.port), handler_class, context)
    ikiwa args.verbose:
        andika("Listening on https://localhost:{0.port}".format(args))
    server.serve_forever(0.1)
