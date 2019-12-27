agiza unittest
kutoka test agiza support
kutoka test.test_urllib2 agiza sanepathname2url

agiza os
agiza socket
agiza urllib.error
agiza urllib.request
agiza sys

support.requires("network")

TIMEOUT = 60  # seconds


eleza _retry_thrice(func, exc, *args, **kwargs):
    for i in range(3):
        try:
            rudisha func(*args, **kwargs)
        except exc as e:
            last_exc = e
            continue
    raise last_exc

eleza _wrap_with_retry_thrice(func, exc):
    eleza wrapped(*args, **kwargs):
        rudisha _retry_thrice(func, exc, *args, **kwargs)
    rudisha wrapped

# bpo-35411: FTP tests of test_urllib2net randomly fail
# with "425 Security: Bad IP connecting" on Travis CI
skip_ftp_test_on_travis = unittest.skipIf('TRAVIS' in os.environ,
                                          'bpo-35411: skip FTP test '
                                          'on Travis CI')


# Connecting to remote hosts is flaky.  Make it more robust by retrying
# the connection several times.
_urlopen_with_retry = _wrap_with_retry_thrice(urllib.request.urlopen,
                                              urllib.error.URLError)


kundi AuthTests(unittest.TestCase):
    """Tests urllib2 authentication features."""

## Disabled at the moment since there is no page under python.org which
## could be used to HTTP authentication.
#
#    eleza test_basic_auth(self):
#        agiza http.client
#
#        test_url = "http://www.python.org/test/test_urllib2/basic_auth"
#        test_hostport = "www.python.org"
#        test_realm = 'Test Realm'
#        test_user = 'test.test_urllib2net'
#        test_password = 'blah'
#
#        # failure
#        try:
#            _urlopen_with_retry(test_url)
#        except urllib2.HTTPError, exc:
#            self.assertEqual(exc.code, 401)
#        else:
#            self.fail("urlopen() should have failed with 401")
#
#        # success
#        auth_handler = urllib2.HTTPBasicAuthHandler()
#        auth_handler.add_password(test_realm, test_hostport,
#                                  test_user, test_password)
#        opener = urllib2.build_opener(auth_handler)
#        f = opener.open('http://localhost/')
#        response = _urlopen_with_retry("http://www.python.org/")
#
#        # The 'userinfo' URL component is deprecated by RFC 3986 for security
#        # reasons, let's not implement it!  (it's already implemented for proxy
#        # specification strings (that is, URLs or authorities specifying a
#        # proxy), so we must keep that)
#        self.assertRaises(http.client.InvalidURL,
#                          urllib2.urlopen, "http://evil:thing@example.com")


kundi CloseSocketTest(unittest.TestCase):

    eleza test_close(self):
        # calling .close() on urllib2's response objects should close the
        # underlying socket
        url = support.TEST_HTTP_URL
        with support.transient_internet(url):
            response = _urlopen_with_retry(url)
            sock = response.fp
            self.assertFalse(sock.closed)
            response.close()
            self.assertTrue(sock.closed)

kundi OtherNetworkTests(unittest.TestCase):
    eleza setUp(self):
        ikiwa 0:  # for debugging
            agiza logging
            logger = logging.getLogger("test_urllib2net")
            logger.addHandler(logging.StreamHandler())

    # XXX The rest of these tests aren't very good -- they don't check much.
    # They do sometimes catch some major disasters, though.

    @skip_ftp_test_on_travis
    eleza test_ftp(self):
        urls = [
            'ftp://www.pythontest.net/README',
            ('ftp://www.pythontest.net/non-existent-file',
             None, urllib.error.URLError),
            ]
        self._test_urls(urls, self._extra_handlers())

    eleza test_file(self):
        TESTFN = support.TESTFN
        f = open(TESTFN, 'w')
        try:
            f.write('hi there\n')
            f.close()
            urls = [
                'file:' + sanepathname2url(os.path.abspath(TESTFN)),
                ('file:///nonsensename/etc/passwd', None,
                 urllib.error.URLError),
                ]
            self._test_urls(urls, self._extra_handlers(), retry=True)
        finally:
            os.remove(TESTFN)

        self.assertRaises(ValueError, urllib.request.urlopen,'./relative_path/to/file')

    # XXX Following test depends on machine configurations that are internal
    # to CNRI.  Need to set up a public server with the right authentication
    # configuration for test purposes.

##     eleza test_cnri(self):
##         ikiwa socket.gethostname() == 'bitdiddle':
##             localhost = 'bitdiddle.cnri.reston.va.us'
##         elikiwa socket.gethostname() == 'bitdiddle.concentric.net':
##             localhost = 'localhost'
##         else:
##             localhost = None
##         ikiwa localhost is not None:
##             urls = [
##                 'file://%s/etc/passwd' % localhost,
##                 'http://%s/simple/' % localhost,
##                 'http://%s/digest/' % localhost,
##                 'http://%s/not/found.h' % localhost,
##                 ]

##             bauth = HTTPBasicAuthHandler()
##             bauth.add_password('basic_test_realm', localhost, 'jhylton',
##                                'password')
##             dauth = HTTPDigestAuthHandler()
##             dauth.add_password('digest_test_realm', localhost, 'jhylton',
##                                'password')

##             self._test_urls(urls, self._extra_handlers()+[bauth, dauth])

    eleza test_urlwithfrag(self):
        urlwith_frag = "http://www.pythontest.net/index.html#frag"
        with support.transient_internet(urlwith_frag):
            req = urllib.request.Request(urlwith_frag)
            res = urllib.request.urlopen(req)
            self.assertEqual(res.geturl(),
                    "http://www.pythontest.net/index.html#frag")

    eleza test_redirect_url_withfrag(self):
        redirect_url_with_frag = "http://www.pythontest.net/redir/with_frag/"
        with support.transient_internet(redirect_url_with_frag):
            req = urllib.request.Request(redirect_url_with_frag)
            res = urllib.request.urlopen(req)
            self.assertEqual(res.geturl(),
                    "http://www.pythontest.net/elsewhere/#frag")

    eleza test_custom_headers(self):
        url = support.TEST_HTTP_URL
        with support.transient_internet(url):
            opener = urllib.request.build_opener()
            request = urllib.request.Request(url)
            self.assertFalse(request.header_items())
            opener.open(request)
            self.assertTrue(request.header_items())
            self.assertTrue(request.has_header('User-agent'))
            request.add_header('User-Agent','Test-Agent')
            opener.open(request)
            self.assertEqual(request.get_header('User-agent'),'Test-Agent')

    @unittest.skip('XXX: http://www.imdb.com is gone')
    eleza test_sites_no_connection_close(self):
        # Some sites do not send Connection: close header.
        # Verify that those work properly. (#issue12576)

        URL = 'http://www.imdb.com' # mangles Connection:close

        with support.transient_internet(URL):
            try:
                with urllib.request.urlopen(URL) as res:
                    pass
            except ValueError as e:
                self.fail("urlopen failed for site not sending \
                           Connection:close")
            else:
                self.assertTrue(res)

            req = urllib.request.urlopen(URL)
            res = req.read()
            self.assertTrue(res)

    eleza _test_urls(self, urls, handlers, retry=True):
        agiza time
        agiza logging
        debug = logging.getLogger("test_urllib2").debug

        urlopen = urllib.request.build_opener(*handlers).open
        ikiwa retry:
            urlopen = _wrap_with_retry_thrice(urlopen, urllib.error.URLError)

        for url in urls:
            with self.subTest(url=url):
                ikiwa isinstance(url, tuple):
                    url, req, expected_err = url
                else:
                    req = expected_err = None

                with support.transient_internet(url):
                    try:
                        f = urlopen(url, req, TIMEOUT)
                    # urllib.error.URLError is a subkundi of OSError
                    except OSError as err:
                        ikiwa expected_err:
                            msg = ("Didn't get expected error(s) %s for %s %s, got %s: %s" %
                                   (expected_err, url, req, type(err), err))
                            self.assertIsInstance(err, expected_err, msg)
                        else:
                            raise
                    else:
                        try:
                            with support.time_out, \
                                 support.socket_peer_reset, \
                                 support.ioerror_peer_reset:
                                buf = f.read()
                                debug("read %d bytes" % len(buf))
                        except socket.timeout:
                            andika("<timeout: %s>" % url, file=sys.stderr)
                        f.close()
                time.sleep(0.1)

    eleza _extra_handlers(self):
        handlers = []

        cfh = urllib.request.CacheFTPHandler()
        self.addCleanup(cfh.clear_cache)
        cfh.setTimeout(1)
        handlers.append(cfh)

        rudisha handlers


kundi TimeoutTest(unittest.TestCase):
    eleza test_http_basic(self):
        self.assertIsNone(socket.getdefaulttimeout())
        url = support.TEST_HTTP_URL
        with support.transient_internet(url, timeout=None):
            u = _urlopen_with_retry(url)
            self.addCleanup(u.close)
            self.assertIsNone(u.fp.raw._sock.gettimeout())

    eleza test_http_default_timeout(self):
        self.assertIsNone(socket.getdefaulttimeout())
        url = support.TEST_HTTP_URL
        with support.transient_internet(url):
            socket.setdefaulttimeout(60)
            try:
                u = _urlopen_with_retry(url)
                self.addCleanup(u.close)
            finally:
                socket.setdefaulttimeout(None)
            self.assertEqual(u.fp.raw._sock.gettimeout(), 60)

    eleza test_http_no_timeout(self):
        self.assertIsNone(socket.getdefaulttimeout())
        url = support.TEST_HTTP_URL
        with support.transient_internet(url):
            socket.setdefaulttimeout(60)
            try:
                u = _urlopen_with_retry(url, timeout=None)
                self.addCleanup(u.close)
            finally:
                socket.setdefaulttimeout(None)
            self.assertIsNone(u.fp.raw._sock.gettimeout())

    eleza test_http_timeout(self):
        url = support.TEST_HTTP_URL
        with support.transient_internet(url):
            u = _urlopen_with_retry(url, timeout=120)
            self.addCleanup(u.close)
            self.assertEqual(u.fp.raw._sock.gettimeout(), 120)

    FTP_HOST = 'ftp://www.pythontest.net/'

    @skip_ftp_test_on_travis
    eleza test_ftp_basic(self):
        self.assertIsNone(socket.getdefaulttimeout())
        with support.transient_internet(self.FTP_HOST, timeout=None):
            u = _urlopen_with_retry(self.FTP_HOST)
            self.addCleanup(u.close)
            self.assertIsNone(u.fp.fp.raw._sock.gettimeout())

    @skip_ftp_test_on_travis
    eleza test_ftp_default_timeout(self):
        self.assertIsNone(socket.getdefaulttimeout())
        with support.transient_internet(self.FTP_HOST):
            socket.setdefaulttimeout(60)
            try:
                u = _urlopen_with_retry(self.FTP_HOST)
                self.addCleanup(u.close)
            finally:
                socket.setdefaulttimeout(None)
            self.assertEqual(u.fp.fp.raw._sock.gettimeout(), 60)

    @skip_ftp_test_on_travis
    eleza test_ftp_no_timeout(self):
        self.assertIsNone(socket.getdefaulttimeout())
        with support.transient_internet(self.FTP_HOST):
            socket.setdefaulttimeout(60)
            try:
                u = _urlopen_with_retry(self.FTP_HOST, timeout=None)
                self.addCleanup(u.close)
            finally:
                socket.setdefaulttimeout(None)
            self.assertIsNone(u.fp.fp.raw._sock.gettimeout())

    @skip_ftp_test_on_travis
    eleza test_ftp_timeout(self):
        with support.transient_internet(self.FTP_HOST):
            u = _urlopen_with_retry(self.FTP_HOST, timeout=60)
            self.addCleanup(u.close)
            self.assertEqual(u.fp.fp.raw._sock.gettimeout(), 60)


ikiwa __name__ == "__main__":
    unittest.main()
