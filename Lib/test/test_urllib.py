"""Regression tests kila what was kwenye Python 2's "urllib" module"""

agiza urllib.parse
agiza urllib.request
agiza urllib.error
agiza http.client
agiza email.message
agiza io
agiza unittest
kutoka unittest.mock agiza patch
kutoka test agiza support
agiza os
jaribu:
    agiza ssl
tatizo ImportError:
    ssl = Tupu
agiza sys
agiza tempfile
kutoka nturl2path agiza url2pathname, pathname2url

kutoka base64 agiza b64encode
agiza collections


eleza hexescape(char):
    """Escape char kama RFC 2396 specifies"""
    hex_repr = hex(ord(char))[2:].upper()
    ikiwa len(hex_repr) == 1:
        hex_repr = "0%s" % hex_repr
    rudisha "%" + hex_repr

# Shortcut kila testing FancyURLopener
_urlopener = Tupu


eleza urlopen(url, data=Tupu, proxies=Tupu):
    """urlopen(url [, data]) -> open file-like object"""
    global _urlopener
    ikiwa proxies ni sio Tupu:
        opener = urllib.request.FancyURLopener(proxies=proxies)
    lasivyo sio _urlopener:
        opener = FancyURLopener()
        _urlopener = opener
    isipokua:
        opener = _urlopener
    ikiwa data ni Tupu:
        rudisha opener.open(url)
    isipokua:
        rudisha opener.open(url, data)


eleza FancyURLopener():
    ukijumuisha support.check_warnings(
            ('FancyURLopener style of invoking requests ni deprecated.',
            DeprecationWarning)):
        rudisha urllib.request.FancyURLopener()


eleza fakehttp(fakedata, mock_close=Uongo):
    kundi FakeSocket(io.BytesIO):
        io_refs = 1

        eleza sendall(self, data):
            FakeHTTPConnection.buf = data

        eleza makefile(self, *args, **kwds):
            self.io_refs += 1
            rudisha self

        eleza read(self, amt=Tupu):
            ikiwa self.closed:
                rudisha b""
            rudisha io.BytesIO.read(self, amt)

        eleza readline(self, length=Tupu):
            ikiwa self.closed:
                rudisha b""
            rudisha io.BytesIO.readline(self, length)

        eleza close(self):
            self.io_refs -= 1
            ikiwa self.io_refs == 0:
                io.BytesIO.close(self)

    kundi FakeHTTPConnection(http.client.HTTPConnection):

        # buffer to store data kila verification kwenye urlopen tests.
        buf = Tupu

        eleza connect(self):
            self.sock = FakeSocket(self.fakedata)
            type(self).fakesock = self.sock

        ikiwa mock_close:
            # bpo-36918: HTTPConnection destructor calls close() which calls
            # flush(). Problem: flush() calls self.fp.flush() which ashirias
            # "ValueError: I/O operation on closed file" which ni logged kama an
            # "Exception ignored in". Override close() to silence this error.
            eleza close(self):
                pita
    FakeHTTPConnection.fakedata = fakedata

    rudisha FakeHTTPConnection


kundi FakeHTTPMixin(object):
    eleza fakehttp(self, fakedata, mock_close=Uongo):
        fake_http_kundi = fakehttp(fakedata, mock_close=mock_close)
        self._connection_kundi = http.client.HTTPConnection
        http.client.HTTPConnection = fake_http_class

    eleza unfakehttp(self):
        http.client.HTTPConnection = self._connection_class


kundi FakeFTPMixin(object):
    eleza fakeftp(self):
        kundi FakeFtpWrapper(object):
            eleza __init__(self,  user, pitawd, host, port, dirs, timeout=Tupu,
                     persistent=Kweli):
                pita

            eleza retrfile(self, file, type):
                rudisha io.BytesIO(), 0

            eleza close(self):
                pita

        self._ftpwrapper_kundi = urllib.request.ftpwrapper
        urllib.request.ftpwrapper = FakeFtpWrapper

    eleza unfakeftp(self):
        urllib.request.ftpwrapper = self._ftpwrapper_class


kundi urlopen_FileTests(unittest.TestCase):
    """Test urlopen() opening a temporary file.

    Try to test kama much functionality kama possible so kama to cut down on reliance
    on connecting to the Net kila testing.

    """

    eleza setUp(self):
        # Create a temp file to use kila testing
        self.text = bytes("test_urllib: %s\n" % self.__class__.__name__,
                          "ascii")
        f = open(support.TESTFN, 'wb')
        jaribu:
            f.write(self.text)
        mwishowe:
            f.close()
        self.pathname = support.TESTFN
        self.rudishaed_obj = urlopen("file:%s" % self.pathname)

    eleza tearDown(self):
        """Shut down the open object"""
        self.rudishaed_obj.close()
        os.remove(support.TESTFN)

    eleza test_interface(self):
        # Make sure object rudishaed by urlopen() has the specified methods
        kila attr kwenye ("read", "readline", "readlines", "fileno",
                     "close", "info", "geturl", "getcode", "__iter__"):
            self.assertKweli(hasattr(self.rudishaed_obj, attr),
                         "object rudishaed by urlopen() lacks %s attribute" %
                         attr)

    eleza test_read(self):
        self.assertEqual(self.text, self.rudishaed_obj.read())

    eleza test_readline(self):
        self.assertEqual(self.text, self.rudishaed_obj.readline())
        self.assertEqual(b'', self.rudishaed_obj.readline(),
                         "calling readline() after exhausting the file did not"
                         " rudisha an empty string")

    eleza test_readlines(self):
        lines_list = self.rudishaed_obj.readlines()
        self.assertEqual(len(lines_list), 1,
                         "readlines() rudishaed the wrong number of lines")
        self.assertEqual(lines_list[0], self.text,
                         "readlines() rudishaed improper text")

    eleza test_fileno(self):
        file_num = self.rudishaed_obj.fileno()
        self.assertIsInstance(file_num, int, "fileno() did sio rudisha an int")
        self.assertEqual(os.read(file_num, len(self.text)), self.text,
                         "Reading on the file descriptor rudishaed by fileno() "
                         "did sio rudisha the expected text")

    eleza test_close(self):
        # Test close() by calling it here na then having it be called again
        # by the tearDown() method kila the test
        self.rudishaed_obj.close()

    eleza test_info(self):
        self.assertIsInstance(self.rudishaed_obj.info(), email.message.Message)

    eleza test_geturl(self):
        self.assertEqual(self.rudishaed_obj.geturl(), self.pathname)

    eleza test_getcode(self):
        self.assertIsTupu(self.rudishaed_obj.getcode())

    eleza test_iter(self):
        # Test iterator
        # Don't need to count number of iterations since test would fail the
        # instant it rudishaed anything beyond the first line kutoka the
        # comparison.
        # Use the iterator kwenye the usual implicit way to test kila ticket #4608.
        kila line kwenye self.rudishaed_obj:
            self.assertEqual(line, self.text)

    eleza test_relativelocalfile(self):
        self.assertRaises(ValueError,urllib.request.urlopen,'./' + self.pathname)


kundi ProxyTests(unittest.TestCase):

    eleza setUp(self):
        # Records changes to env vars
        self.env = support.EnvironmentVarGuard()
        # Delete all proxy related env vars
        kila k kwenye list(os.environ):
            ikiwa 'proxy' kwenye k.lower():
                self.env.unset(k)

    eleza tearDown(self):
        # Restore all proxy related env vars
        self.env.__exit__()
        toa self.env

    eleza test_getproxies_environment_keep_no_proxies(self):
        self.env.set('NO_PROXY', 'localhost')
        proxies = urllib.request.getproxies_environment()
        # getproxies_environment use lowered case truncated (no '_proxy') keys
        self.assertEqual('localhost', proxies['no'])
        # List of no_proxies ukijumuisha space.
        self.env.set('NO_PROXY', 'localhost, anotherdomain.com, newdomain.com:1234')
        self.assertKweli(urllib.request.proxy_bypita_environment('anotherdomain.com'))
        self.assertKweli(urllib.request.proxy_bypita_environment('anotherdomain.com:8888'))
        self.assertKweli(urllib.request.proxy_bypita_environment('newdomain.com:1234'))

    eleza test_proxy_cgi_ignore(self):
        jaribu:
            self.env.set('HTTP_PROXY', 'http://somewhere:3128')
            proxies = urllib.request.getproxies_environment()
            self.assertEqual('http://somewhere:3128', proxies['http'])
            self.env.set('REQUEST_METHOD', 'GET')
            proxies = urllib.request.getproxies_environment()
            self.assertNotIn('http', proxies)
        mwishowe:
            self.env.unset('REQUEST_METHOD')
            self.env.unset('HTTP_PROXY')

    eleza test_proxy_bypita_environment_host_match(self):
        bypita = urllib.request.proxy_bypita_environment
        self.env.set('NO_PROXY',
                     'localhost, anotherdomain.com, newdomain.com:1234, .d.o.t')
        self.assertKweli(bypita('localhost'))
        self.assertKweli(bypita('LocalHost'))                 # MixedCase
        self.assertKweli(bypita('LOCALHOST'))                 # UPPERCASE
        self.assertKweli(bypita('newdomain.com:1234'))
        self.assertKweli(bypita('foo.d.o.t'))                 # issue 29142
        self.assertKweli(bypita('anotherdomain.com:8888'))
        self.assertKweli(bypita('www.newdomain.com:1234'))
        self.assertUongo(bypita('prelocalhost'))
        self.assertUongo(bypita('newdomain.com'))            # no port
        self.assertUongo(bypita('newdomain.com:1235'))       # wrong port


kundi ProxyTests_withOrderedEnv(unittest.TestCase):

    eleza setUp(self):
        # We need to test conditions, where variable order _is_ significant
        self._saved_env = os.environ
        # Monkey patch os.environ, start ukijumuisha empty fake environment
        os.environ = collections.OrderedDict()

    eleza tearDown(self):
        os.environ = self._saved_env

    eleza test_getproxies_environment_prefer_lowercase(self):
        # Test lowercase preference ukijumuisha removal
        os.environ['no_proxy'] = ''
        os.environ['No_Proxy'] = 'localhost'
        self.assertUongo(urllib.request.proxy_bypita_environment('localhost'))
        self.assertUongo(urllib.request.proxy_bypita_environment('arbitrary'))
        os.environ['http_proxy'] = ''
        os.environ['HTTP_PROXY'] = 'http://somewhere:3128'
        proxies = urllib.request.getproxies_environment()
        self.assertEqual({}, proxies)
        # Test lowercase preference of proxy bypita na correct matching including ports
        os.environ['no_proxy'] = 'localhost, noproxy.com, my.proxy:1234'
        os.environ['No_Proxy'] = 'xyz.com'
        self.assertKweli(urllib.request.proxy_bypita_environment('localhost'))
        self.assertKweli(urllib.request.proxy_bypita_environment('noproxy.com:5678'))
        self.assertKweli(urllib.request.proxy_bypita_environment('my.proxy:1234'))
        self.assertUongo(urllib.request.proxy_bypita_environment('my.proxy'))
        self.assertUongo(urllib.request.proxy_bypita_environment('arbitrary'))
        # Test lowercase preference ukijumuisha replacement
        os.environ['http_proxy'] = 'http://somewhere:3128'
        os.environ['Http_Proxy'] = 'http://somewhereisipokua:3128'
        proxies = urllib.request.getproxies_environment()
        self.assertEqual('http://somewhere:3128', proxies['http'])


kundi urlopen_HttpTests(unittest.TestCase, FakeHTTPMixin, FakeFTPMixin):
    """Test urlopen() opening a fake http connection."""

    eleza check_read(self, ver):
        self.fakehttp(b"HTTP/" + ver + b" 200 OK\r\n\r\nHello!")
        jaribu:
            fp = urlopen("http://python.org/")
            self.assertEqual(fp.readline(), b"Hello!")
            self.assertEqual(fp.readline(), b"")
            self.assertEqual(fp.geturl(), 'http://python.org/')
            self.assertEqual(fp.getcode(), 200)
        mwishowe:
            self.unfakehttp()

    eleza test_url_fragment(self):
        # Issue #11703: geturl() omits fragments kwenye the original URL.
        url = 'http://docs.python.org/library/urllib.html#OK'
        self.fakehttp(b"HTTP/1.1 200 OK\r\n\r\nHello!")
        jaribu:
            fp = urllib.request.urlopen(url)
            self.assertEqual(fp.geturl(), url)
        mwishowe:
            self.unfakehttp()

    eleza test_willclose(self):
        self.fakehttp(b"HTTP/1.1 200 OK\r\n\r\nHello!")
        jaribu:
            resp = urlopen("http://www.python.org")
            self.assertKweli(resp.fp.will_close)
        mwishowe:
            self.unfakehttp()

    @unittest.skipUnless(ssl, "ssl module required")
    eleza test_url_with_control_char_rejected(self):
        kila char_no kwenye list(range(0, 0x21)) + [0x7f]:
            char = chr(char_no)
            schemeless_url = f"//localhost:7777/test{char}/"
            self.fakehttp(b"HTTP/1.1 200 OK\r\n\r\nHello.")
            jaribu:
                # We explicitly test urllib.request.urlopen() instead of the top
                # level 'eleza urlopen()' function defined kwenye this... (quite ugly)
                # test suite.  They use different url opening codepaths.  Plain
                # urlopen uses FancyURLOpener which goes via a codepath that
                # calls urllib.parse.quote() on the URL which makes all of the
                # above attempts at injection within the url _path_ safe.
                escaped_char_repr = repr(char).replace('\\', r'\\')
                InvalidURL = http.client.InvalidURL
                ukijumuisha self.assertRaisesRegex(
                    InvalidURL, f"contain control.*{escaped_char_repr}"):
                    urllib.request.urlopen(f"http:{schemeless_url}")
                ukijumuisha self.assertRaisesRegex(
                    InvalidURL, f"contain control.*{escaped_char_repr}"):
                    urllib.request.urlopen(f"https:{schemeless_url}")
                # This code path quotes the URL so there ni no injection.
                resp = urlopen(f"http:{schemeless_url}")
                self.assertNotIn(char, resp.geturl())
            mwishowe:
                self.unfakehttp()

    @unittest.skipUnless(ssl, "ssl module required")
    eleza test_url_with_newline_header_injection_rejected(self):
        self.fakehttp(b"HTTP/1.1 200 OK\r\n\r\nHello.")
        host = "localhost:7777?a=1 HTTP/1.1\r\nX-injected: header\r\nTEST: 123"
        schemeless_url = "//" + host + ":8080/test/?test=a"
        jaribu:
            # We explicitly test urllib.request.urlopen() instead of the top
            # level 'eleza urlopen()' function defined kwenye this... (quite ugly)
            # test suite.  They use different url opening codepaths.  Plain
            # urlopen uses FancyURLOpener which goes via a codepath that
            # calls urllib.parse.quote() on the URL which makes all of the
            # above attempts at injection within the url _path_ safe.
            InvalidURL = http.client.InvalidURL
            ukijumuisha self.assertRaisesRegex(
                InvalidURL, r"contain control.*\\r.*(found at least . .)"):
                urllib.request.urlopen(f"http:{schemeless_url}")
            ukijumuisha self.assertRaisesRegex(InvalidURL, r"contain control.*\\n"):
                urllib.request.urlopen(f"https:{schemeless_url}")
            # This code path quotes the URL so there ni no injection.
            resp = urlopen(f"http:{schemeless_url}")
            self.assertNotIn(' ', resp.geturl())
            self.assertNotIn('\r', resp.geturl())
            self.assertNotIn('\n', resp.geturl())
        mwishowe:
            self.unfakehttp()

    eleza test_read_0_9(self):
        # "0.9" response accepted (but sio "simple responses" without
        # a status line)
        self.check_read(b"0.9")

    eleza test_read_1_0(self):
        self.check_read(b"1.0")

    eleza test_read_1_1(self):
        self.check_read(b"1.1")

    eleza test_read_bogus(self):
        # urlopen() should ashiria OSError kila many error codes.
        self.fakehttp(b'''HTTP/1.1 401 Authentication Required
Date: Wed, 02 Jan 2008 03:03:54 GMT
Server: Apache/1.3.33 (Debian GNU/Linux) mod_ssl/2.8.22 OpenSSL/0.9.7e
Connection: close
Content-Type: text/html; charset=iso-8859-1
''', mock_close=Kweli)
        jaribu:
            self.assertRaises(OSError, urlopen, "http://python.org/")
        mwishowe:
            self.unfakehttp()

    eleza test_invalid_redirect(self):
        # urlopen() should ashiria OSError kila many error codes.
        self.fakehttp(b'''HTTP/1.1 302 Found
Date: Wed, 02 Jan 2008 03:03:54 GMT
Server: Apache/1.3.33 (Debian GNU/Linux) mod_ssl/2.8.22 OpenSSL/0.9.7e
Location: file://guidocomputer.athome.com:/python/license
Connection: close
Content-Type: text/html; charset=iso-8859-1
''', mock_close=Kweli)
        jaribu:
            msg = "Redirection to url 'file:"
            ukijumuisha self.assertRaisesRegex(urllib.error.HTTPError, msg):
                urlopen("http://python.org/")
        mwishowe:
            self.unfakehttp()

    eleza test_redirect_limit_independent(self):
        # Ticket #12923: make sure independent requests each use their
        # own retry limit.
        kila i kwenye range(FancyURLopener().maxtries):
            self.fakehttp(b'''HTTP/1.1 302 Found
Location: file://guidocomputer.athome.com:/python/license
Connection: close
''', mock_close=Kweli)
            jaribu:
                self.assertRaises(urllib.error.HTTPError, urlopen,
                    "http://something")
            mwishowe:
                self.unfakehttp()

    eleza test_empty_socket(self):
        # urlopen() ashirias OSError ikiwa the underlying socket does sio send any
        # data. (#1680230)
        self.fakehttp(b'')
        jaribu:
            self.assertRaises(OSError, urlopen, "http://something")
        mwishowe:
            self.unfakehttp()

    eleza test_missing_localfile(self):
        # Test kila #10836
        ukijumuisha self.assertRaises(urllib.error.URLError) kama e:
            urlopen('file://localhost/a/file/which/doesnot/exists.py')
        self.assertKweli(e.exception.filename)
        self.assertKweli(e.exception.reason)

    eleza test_file_notexists(self):
        fd, tmp_file = tempfile.mkstemp()
        tmp_fileurl = 'file://localhost/' + tmp_file.replace(os.path.sep, '/')
        jaribu:
            self.assertKweli(os.path.exists(tmp_file))
            ukijumuisha urlopen(tmp_fileurl) kama fobj:
                self.assertKweli(fobj)
        mwishowe:
            os.close(fd)
            os.unlink(tmp_file)
        self.assertUongo(os.path.exists(tmp_file))
        ukijumuisha self.assertRaises(urllib.error.URLError):
            urlopen(tmp_fileurl)

    eleza test_ftp_nohost(self):
        test_ftp_url = 'ftp:///path'
        ukijumuisha self.assertRaises(urllib.error.URLError) kama e:
            urlopen(test_ftp_url)
        self.assertUongo(e.exception.filename)
        self.assertKweli(e.exception.reason)

    eleza test_ftp_nonexisting(self):
        ukijumuisha self.assertRaises(urllib.error.URLError) kama e:
            urlopen('ftp://localhost/a/file/which/doesnot/exists.py')
        self.assertUongo(e.exception.filename)
        self.assertKweli(e.exception.reason)

    @patch.object(urllib.request, 'MAXFTPCACHE', 0)
    eleza test_ftp_cache_pruning(self):
        self.fakeftp()
        jaribu:
            urllib.request.ftpcache['test'] = urllib.request.ftpwrapper('user', 'pita', 'localhost', 21, [])
            urlopen('ftp://localhost')
        mwishowe:
            self.unfakeftp()

    eleza test_userpita_inurl(self):
        self.fakehttp(b"HTTP/1.0 200 OK\r\n\r\nHello!")
        jaribu:
            fp = urlopen("http://user:pita@python.org/")
            self.assertEqual(fp.readline(), b"Hello!")
            self.assertEqual(fp.readline(), b"")
            self.assertEqual(fp.geturl(), 'http://user:pita@python.org/')
            self.assertEqual(fp.getcode(), 200)
        mwishowe:
            self.unfakehttp()

    eleza test_userpita_inurl_w_spaces(self):
        self.fakehttp(b"HTTP/1.0 200 OK\r\n\r\nHello!")
        jaribu:
            userpita = "a b:c d"
            url = "http://{}@python.org/".format(userpita)
            fakehttp_wrapper = http.client.HTTPConnection
            authorization = ("Authorization: Basic %s\r\n" %
                             b64encode(userpita.encode("ASCII")).decode("ASCII"))
            fp = urlopen(url)
            # The authorization header must be kwenye place
            self.assertIn(authorization, fakehttp_wrapper.buf.decode("UTF-8"))
            self.assertEqual(fp.readline(), b"Hello!")
            self.assertEqual(fp.readline(), b"")
            # the spaces are quoted kwenye URL so no match
            self.assertNotEqual(fp.geturl(), url)
            self.assertEqual(fp.getcode(), 200)
        mwishowe:
            self.unfakehttp()

    eleza test_URLopener_deprecation(self):
        ukijumuisha support.check_warnings(('',DeprecationWarning)):
            urllib.request.URLopener()

    @unittest.skipUnless(ssl, "ssl module required")
    eleza test_cafile_and_context(self):
        context = ssl.create_default_context()
        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            ukijumuisha self.assertRaises(ValueError):
                urllib.request.urlopen(
                    "https://localhost", cafile="/nonexistent/path", context=context
                )


kundi urlopen_DataTests(unittest.TestCase):
    """Test urlopen() opening a data URL."""

    eleza setUp(self):
        # text containing URL special- na unicode-characters
        self.text = "test data URLs :;,%=& \u00f6 \u00c4 "
        # 2x1 pixel RGB PNG image ukijumuisha one black na one white pixel
        self.image = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00'
            b'\x01\x08\x02\x00\x00\x00{@\xe8\xdd\x00\x00\x00\x01sRGB\x00\xae'
            b'\xce\x1c\xe9\x00\x00\x00\x0fIDAT\x08\xd7c```\xf8\xff\xff?\x00'
            b'\x06\x01\x02\xfe\no/\x1e\x00\x00\x00\x00IEND\xaeB`\x82')

        self.text_url = (
            "data:text/plain;charset=UTF-8,test%20data%20URLs%20%3A%3B%2C%25%3"
            "D%26%20%C3%B6%20%C3%84%20")
        self.text_url_base64 = (
            "data:text/plain;charset=ISO-8859-1;base64,dGVzdCBkYXRhIFVSTHMgOjs"
            "sJT0mIPYgxCA%3D")
        # base64 encoded data URL that contains ignorable spaces,
        # such kama "\n", " ", "%0A", na "%20".
        self.image_url = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAIAAAB7\n"
            "QOjdAAAAAXNSR0IArs4c6QAAAA9JREFUCNdj%0AYGBg%2BP//PwAGAQL%2BCm8 "
            "vHgAAAABJRU5ErkJggg%3D%3D%0A%20")

        self.text_url_resp = urllib.request.urlopen(self.text_url)
        self.text_url_base64_resp = urllib.request.urlopen(
            self.text_url_base64)
        self.image_url_resp = urllib.request.urlopen(self.image_url)

    eleza test_interface(self):
        # Make sure object rudishaed by urlopen() has the specified methods
        kila attr kwenye ("read", "readline", "readlines",
                     "close", "info", "geturl", "getcode", "__iter__"):
            self.assertKweli(hasattr(self.text_url_resp, attr),
                         "object rudishaed by urlopen() lacks %s attribute" %
                         attr)

    eleza test_info(self):
        self.assertIsInstance(self.text_url_resp.info(), email.message.Message)
        self.assertEqual(self.text_url_base64_resp.info().get_params(),
            [('text/plain', ''), ('charset', 'ISO-8859-1')])
        self.assertEqual(self.image_url_resp.info()['content-length'],
            str(len(self.image)))
        self.assertEqual(urllib.request.urlopen("data:,").info().get_params(),
            [('text/plain', ''), ('charset', 'US-ASCII')])

    eleza test_geturl(self):
        self.assertEqual(self.text_url_resp.geturl(), self.text_url)
        self.assertEqual(self.text_url_base64_resp.geturl(),
            self.text_url_base64)
        self.assertEqual(self.image_url_resp.geturl(), self.image_url)

    eleza test_read_text(self):
        self.assertEqual(self.text_url_resp.read().decode(
            dict(self.text_url_resp.info().get_params())['charset']), self.text)

    eleza test_read_text_base64(self):
        self.assertEqual(self.text_url_base64_resp.read().decode(
            dict(self.text_url_base64_resp.info().get_params())['charset']),
            self.text)

    eleza test_read_image(self):
        self.assertEqual(self.image_url_resp.read(), self.image)

    eleza test_missing_comma(self):
        self.assertRaises(ValueError,urllib.request.urlopen,'data:text/plain')

    eleza test_invalid_base64_data(self):
        # missing padding character
        self.assertRaises(ValueError,urllib.request.urlopen,'data:;base64,Cg=')


kundi urlretrieve_FileTests(unittest.TestCase):
    """Test urllib.urlretrieve() on local files"""

    eleza setUp(self):
        # Create a list of temporary files. Each item kwenye the list ni a file
        # name (absolute path ama relative to the current working directory).
        # All files kwenye this list will be deleted kwenye the tearDown method. Note,
        # this only helps to makes sure temporary files get deleted, but it
        # does nothing about trying to close files that may still be open. It
        # ni the responsibility of the developer to properly close files even
        # when exceptional conditions occur.
        self.tempFiles = []

        # Create a temporary file.
        self.registerFileForCleanUp(support.TESTFN)
        self.text = b'testing urllib.urlretrieve'
        jaribu:
            FILE = open(support.TESTFN, 'wb')
            FILE.write(self.text)
            FILE.close()
        mwishowe:
            jaribu: FILE.close()
            except: pita

    eleza tearDown(self):
        # Delete the temporary files.
        kila each kwenye self.tempFiles:
            jaribu: os.remove(each)
            except: pita

    eleza constructLocalFileUrl(self, filePath):
        filePath = os.path.abspath(filePath)
        jaribu:
            filePath.encode("utf-8")
        tatizo UnicodeEncodeError:
            ashiria unittest.SkipTest("filePath ni sio encodable to utf8")
        rudisha "file://%s" % urllib.request.pathname2url(filePath)

    eleza createNewTempFile(self, data=b""):
        """Creates a new temporary file containing the specified data,
        registers the file kila deletion during the test fixture tear down, and
        rudishas the absolute path of the file."""

        newFd, newFilePath = tempfile.mkstemp()
        jaribu:
            self.registerFileForCleanUp(newFilePath)
            newFile = os.fdopen(newFd, "wb")
            newFile.write(data)
            newFile.close()
        mwishowe:
            jaribu: newFile.close()
            except: pita
        rudisha newFilePath

    eleza registerFileForCleanUp(self, fileName):
        self.tempFiles.append(fileName)

    eleza test_basic(self):
        # Make sure that a local file just gets its own location rudishaed and
        # a headers value ni rudishaed.
        result = urllib.request.urlretrieve("file:%s" % support.TESTFN)
        self.assertEqual(result[0], support.TESTFN)
        self.assertIsInstance(result[1], email.message.Message,
                              "did sio get an email.message.Message instance "
                              "as second rudishaed value")

    eleza test_copy(self):
        # Test that setting the filename argument works.
        second_temp = "%s.2" % support.TESTFN
        self.registerFileForCleanUp(second_temp)
        result = urllib.request.urlretrieve(self.constructLocalFileUrl(
            support.TESTFN), second_temp)
        self.assertEqual(second_temp, result[0])
        self.assertKweli(os.path.exists(second_temp), "copy of the file was sio "
                                                  "made")
        FILE = open(second_temp, 'rb')
        jaribu:
            text = FILE.read()
            FILE.close()
        mwishowe:
            jaribu: FILE.close()
            except: pita
        self.assertEqual(self.text, text)

    eleza test_reporthook(self):
        # Make sure that the reporthook works.
        eleza hooktester(block_count, block_read_size, file_size, count_holder=[0]):
            self.assertIsInstance(block_count, int)
            self.assertIsInstance(block_read_size, int)
            self.assertIsInstance(file_size, int)
            self.assertEqual(block_count, count_holder[0])
            count_holder[0] = count_holder[0] + 1
        second_temp = "%s.2" % support.TESTFN
        self.registerFileForCleanUp(second_temp)
        urllib.request.urlretrieve(
            self.constructLocalFileUrl(support.TESTFN),
            second_temp, hooktester)

    eleza test_reporthook_0_bytes(self):
        # Test on zero length file. Should call reporthook only 1 time.
        report = []
        eleza hooktester(block_count, block_read_size, file_size, _report=report):
            _report.append((block_count, block_read_size, file_size))
        srcFileName = self.createNewTempFile()
        urllib.request.urlretrieve(self.constructLocalFileUrl(srcFileName),
            support.TESTFN, hooktester)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0][2], 0)

    eleza test_reporthook_5_bytes(self):
        # Test on 5 byte file. Should call reporthook only 2 times (once when
        # the "network connection" ni established na once when the block is
        # read).
        report = []
        eleza hooktester(block_count, block_read_size, file_size, _report=report):
            _report.append((block_count, block_read_size, file_size))
        srcFileName = self.createNewTempFile(b"x" * 5)
        urllib.request.urlretrieve(self.constructLocalFileUrl(srcFileName),
            support.TESTFN, hooktester)
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0][2], 5)
        self.assertEqual(report[1][2], 5)

    eleza test_reporthook_8193_bytes(self):
        # Test on 8193 byte file. Should call reporthook only 3 times (once
        # when the "network connection" ni established, once kila the next 8192
        # bytes, na once kila the last byte).
        report = []
        eleza hooktester(block_count, block_read_size, file_size, _report=report):
            _report.append((block_count, block_read_size, file_size))
        srcFileName = self.createNewTempFile(b"x" * 8193)
        urllib.request.urlretrieve(self.constructLocalFileUrl(srcFileName),
            support.TESTFN, hooktester)
        self.assertEqual(len(report), 3)
        self.assertEqual(report[0][2], 8193)
        self.assertEqual(report[0][1], 8192)
        self.assertEqual(report[1][1], 8192)
        self.assertEqual(report[2][1], 8192)


kundi urlretrieve_HttpTests(unittest.TestCase, FakeHTTPMixin):
    """Test urllib.urlretrieve() using fake http connections"""

    eleza test_short_content_ashirias_ContentTooShortError(self):
        self.fakehttp(b'''HTTP/1.1 200 OK
Date: Wed, 02 Jan 2008 03:03:54 GMT
Server: Apache/1.3.33 (Debian GNU/Linux) mod_ssl/2.8.22 OpenSSL/0.9.7e
Connection: close
Content-Length: 100
Content-Type: text/html; charset=iso-8859-1

FF
''')

        eleza _reporthook(par1, par2, par3):
            pita

        ukijumuisha self.assertRaises(urllib.error.ContentTooShortError):
            jaribu:
                urllib.request.urlretrieve(support.TEST_HTTP_URL,
                                           reporthook=_reporthook)
            mwishowe:
                self.unfakehttp()

    eleza test_short_content_ashirias_ContentTooShortError_without_reporthook(self):
        self.fakehttp(b'''HTTP/1.1 200 OK
Date: Wed, 02 Jan 2008 03:03:54 GMT
Server: Apache/1.3.33 (Debian GNU/Linux) mod_ssl/2.8.22 OpenSSL/0.9.7e
Connection: close
Content-Length: 100
Content-Type: text/html; charset=iso-8859-1

FF
''')
        ukijumuisha self.assertRaises(urllib.error.ContentTooShortError):
            jaribu:
                urllib.request.urlretrieve(support.TEST_HTTP_URL)
            mwishowe:
                self.unfakehttp()


kundi QuotingTests(unittest.TestCase):
    r"""Tests kila urllib.quote() na urllib.quote_plus()

    According to RFC 3986 (Uniform Resource Identifiers), to escape a
    character you write it kama '%' + <2 character US-ASCII hex value>.
    The Python code of ``'%' + hex(ord(<character>))[2:]`` escapes a
    character properly. Case does sio matter on the hex letters.

    The various character sets specified are:

    Reserved characters : ";/?:@&=+$,"
        Have special meaning kwenye URIs na must be escaped ikiwa sio being used for
        their special meaning
    Data characters : letters, digits, na "-_.!~*'()"
        Unreserved na do sio need to be escaped; can be, though, ikiwa desired
    Control characters : 0x00 - 0x1F, 0x7F
        Have no use kwenye URIs so must be escaped
    space : 0x20
        Must be escaped
    Delimiters : '<>#%"'
        Must be escaped
    Unwise : "{}|\^[]`"
        Must be escaped

    """

    eleza test_never_quote(self):
        # Make sure quote() does sio quote letters, digits, na "_,.-"
        do_not_quote = '' .join(["ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                 "abcdefghijklmnopqrstuvwxyz",
                                 "0123456789",
                                 "_.-~"])
        result = urllib.parse.quote(do_not_quote)
        self.assertEqual(do_not_quote, result,
                         "using quote(): %r != %r" % (do_not_quote, result))
        result = urllib.parse.quote_plus(do_not_quote)
        self.assertEqual(do_not_quote, result,
                        "using quote_plus(): %r != %r" % (do_not_quote, result))

    eleza test_default_safe(self):
        # Test '/' ni default value kila 'safe' parameter
        self.assertEqual(urllib.parse.quote.__defaults__[0], '/')

    eleza test_safe(self):
        # Test setting 'safe' parameter does what it should do
        quote_by_default = "<>"
        result = urllib.parse.quote(quote_by_default, safe=quote_by_default)
        self.assertEqual(quote_by_default, result,
                         "using quote(): %r != %r" % (quote_by_default, result))
        result = urllib.parse.quote_plus(quote_by_default,
                                         safe=quote_by_default)
        self.assertEqual(quote_by_default, result,
                         "using quote_plus(): %r != %r" %
                         (quote_by_default, result))
        # Safe expressed kama bytes rather than str
        result = urllib.parse.quote(quote_by_default, safe=b"<>")
        self.assertEqual(quote_by_default, result,
                         "using quote(): %r != %r" % (quote_by_default, result))
        # "Safe" non-ASCII characters should have no effect
        # (Since URIs are sio allowed to have non-ASCII characters)
        result = urllib.parse.quote("a\xfcb", encoding="latin-1", safe="\xfc")
        expect = urllib.parse.quote("a\xfcb", encoding="latin-1", safe="")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" %
                         (expect, result))
        # Same kama above, but using a bytes rather than str
        result = urllib.parse.quote("a\xfcb", encoding="latin-1", safe=b"\xfc")
        expect = urllib.parse.quote("a\xfcb", encoding="latin-1", safe="")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" %
                         (expect, result))

    eleza test_default_quoting(self):
        # Make sure all characters that should be quoted are by default sans
        # space (separate test kila that).
        should_quote = [chr(num) kila num kwenye range(32)] # For 0x00 - 0x1F
        should_quote.append(r'<>#%"{}|\^[]`')
        should_quote.append(chr(127)) # For 0x7F
        should_quote = ''.join(should_quote)
        kila char kwenye should_quote:
            result = urllib.parse.quote(char)
            self.assertEqual(hexescape(char), result,
                             "using quote(): "
                             "%s should be escaped to %s, sio %s" %
                             (char, hexescape(char), result))
            result = urllib.parse.quote_plus(char)
            self.assertEqual(hexescape(char), result,
                             "using quote_plus(): "
                             "%s should be escapes to %s, sio %s" %
                             (char, hexescape(char), result))
        toa should_quote
        partial_quote = "ab[]cd"
        expected = "ab%5B%5Dcd"
        result = urllib.parse.quote(partial_quote)
        self.assertEqual(expected, result,
                         "using quote(): %r != %r" % (expected, result))
        result = urllib.parse.quote_plus(partial_quote)
        self.assertEqual(expected, result,
                         "using quote_plus(): %r != %r" % (expected, result))

    eleza test_quoting_space(self):
        # Make sure quote() na quote_plus() handle spaces kama specified in
        # their unique way
        result = urllib.parse.quote(' ')
        self.assertEqual(result, hexescape(' '),
                         "using quote(): %r != %r" % (result, hexescape(' ')))
        result = urllib.parse.quote_plus(' ')
        self.assertEqual(result, '+',
                         "using quote_plus(): %r != +" % result)
        given = "a b cd e f"
        expect = given.replace(' ', hexescape(' '))
        result = urllib.parse.quote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        expect = given.replace(' ', '+')
        result = urllib.parse.quote_plus(given)
        self.assertEqual(expect, result,
                         "using quote_plus(): %r != %r" % (expect, result))

    eleza test_quoting_plus(self):
        self.assertEqual(urllib.parse.quote_plus('alpha+beta gamma'),
                         'alpha%2Bbeta+gamma')
        self.assertEqual(urllib.parse.quote_plus('alpha+beta gamma', '+'),
                         'alpha+beta+gamma')
        # Test ukijumuisha bytes
        self.assertEqual(urllib.parse.quote_plus(b'alpha+beta gamma'),
                         'alpha%2Bbeta+gamma')
        # Test ukijumuisha safe bytes
        self.assertEqual(urllib.parse.quote_plus('alpha+beta gamma', b'+'),
                         'alpha+beta+gamma')

    eleza test_quote_bytes(self):
        # Bytes should quote directly to percent-encoded values
        given = b"\xa2\xd8ab\xff"
        expect = "%A2%D8ab%FF"
        result = urllib.parse.quote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Encoding argument should ashiria type error on bytes input
        self.assertRaises(TypeError, urllib.parse.quote, given,
                            encoding="latin-1")
        # quote_kutoka_bytes should work the same
        result = urllib.parse.quote_kutoka_bytes(given)
        self.assertEqual(expect, result,
                         "using quote_kutoka_bytes(): %r != %r"
                         % (expect, result))

    eleza test_quote_with_unicode(self):
        # Characters kwenye Latin-1 range, encoded by default kwenye UTF-8
        given = "\xa2\xd8ab\xff"
        expect = "%C2%A2%C3%98ab%C3%BF"
        result = urllib.parse.quote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters kwenye Latin-1 range, encoded by ukijumuisha Tupu (default)
        result = urllib.parse.quote(given, encoding=Tupu, errors=Tupu)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters kwenye Latin-1 range, encoded ukijumuisha Latin-1
        given = "\xa2\xd8ab\xff"
        expect = "%A2%D8ab%FF"
        result = urllib.parse.quote(given, encoding="latin-1")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters kwenye BMP, encoded by default kwenye UTF-8
        given = "\u6f22\u5b57"              # "Kanji"
        expect = "%E6%BC%A2%E5%AD%97"
        result = urllib.parse.quote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters kwenye BMP, encoded ukijumuisha Latin-1
        given = "\u6f22\u5b57"
        self.assertRaises(UnicodeEncodeError, urllib.parse.quote, given,
                                    encoding="latin-1")
        # Characters kwenye BMP, encoded ukijumuisha Latin-1, ukijumuisha replace error handling
        given = "\u6f22\u5b57"
        expect = "%3F%3F"                   # "??"
        result = urllib.parse.quote(given, encoding="latin-1",
                                    errors="replace")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        # Characters kwenye BMP, Latin-1, ukijumuisha xmlcharref error handling
        given = "\u6f22\u5b57"
        expect = "%26%2328450%3B%26%2323383%3B"     # "&#28450;&#23383;"
        result = urllib.parse.quote(given, encoding="latin-1",
                                    errors="xmlcharrefreplace")
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))

    eleza test_quote_plus_with_unicode(self):
        # Encoding (latin-1) test kila quote_plus
        given = "\xa2\xd8 \xff"
        expect = "%A2%D8+%FF"
        result = urllib.parse.quote_plus(given, encoding="latin-1")
        self.assertEqual(expect, result,
                         "using quote_plus(): %r != %r" % (expect, result))
        # Errors test kila quote_plus
        given = "ab\u6f22\u5b57 cd"
        expect = "ab%3F%3F+cd"
        result = urllib.parse.quote_plus(given, encoding="latin-1",
                                         errors="replace")
        self.assertEqual(expect, result,
                         "using quote_plus(): %r != %r" % (expect, result))


kundi UnquotingTests(unittest.TestCase):
    """Tests kila unquote() na unquote_plus()

    See the doc string kila quoting_Tests kila details on quoting na such.

    """

    eleza test_unquoting(self):
        # Make sure unquoting of all ASCII values works
        escape_list = []
        kila num kwenye range(128):
            given = hexescape(chr(num))
            expect = chr(num)
            result = urllib.parse.unquote(given)
            self.assertEqual(expect, result,
                             "using unquote(): %r != %r" % (expect, result))
            result = urllib.parse.unquote_plus(given)
            self.assertEqual(expect, result,
                             "using unquote_plus(): %r != %r" %
                             (expect, result))
            escape_list.append(given)
        escape_string = ''.join(escape_list)
        toa escape_list
        result = urllib.parse.unquote(escape_string)
        self.assertEqual(result.count('%'), 1,
                         "using unquote(): sio all characters escaped: "
                         "%s" % result)
        self.assertRaises((TypeError, AttributeError), urllib.parse.unquote, Tupu)
        self.assertRaises((TypeError, AttributeError), urllib.parse.unquote, ())
        ukijumuisha support.check_warnings(('', BytesWarning), quiet=Kweli):
            self.assertRaises((TypeError, AttributeError), urllib.parse.unquote, b'')

    eleza test_unquoting_badpercent(self):
        # Test unquoting on bad percent-escapes
        given = '%xab'
        expect = given
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result, "using unquote(): %r != %r"
                         % (expect, result))
        given = '%x'
        expect = given
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result, "using unquote(): %r != %r"
                         % (expect, result))
        given = '%'
        expect = given
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result, "using unquote(): %r != %r"
                         % (expect, result))
        # unquote_to_bytes
        given = '%xab'
        expect = bytes(given, 'ascii')
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result, "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        given = '%x'
        expect = bytes(given, 'ascii')
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result, "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        given = '%'
        expect = bytes(given, 'ascii')
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result, "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        self.assertRaises((TypeError, AttributeError), urllib.parse.unquote_to_bytes, Tupu)
        self.assertRaises((TypeError, AttributeError), urllib.parse.unquote_to_bytes, ())

    eleza test_unquoting_mixed_case(self):
        # Test unquoting on mixed-case hex digits kwenye the percent-escapes
        given = '%Ab%eA'
        expect = b'\xab\xea'
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))

    eleza test_unquoting_parts(self):
        # Make sure unquoting works when have non-quoted characters
        # interspersed
        given = 'ab%sd' % hexescape('c')
        expect = "abcd"
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using quote(): %r != %r" % (expect, result))
        result = urllib.parse.unquote_plus(given)
        self.assertEqual(expect, result,
                         "using unquote_plus(): %r != %r" % (expect, result))

    eleza test_unquoting_plus(self):
        # Test difference between unquote() na unquote_plus()
        given = "are+there+spaces..."
        expect = given
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))
        expect = given.replace('+', ' ')
        result = urllib.parse.unquote_plus(given)
        self.assertEqual(expect, result,
                         "using unquote_plus(): %r != %r" % (expect, result))

    eleza test_unquote_to_bytes(self):
        given = 'br%C3%BCckner_sapporo_20050930.doc'
        expect = b'br\xc3\xbcckner_sapporo_20050930.doc'
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        # Test on a string ukijumuisha unescaped non-ASCII characters
        # (Technically an invalid URI; expect those characters to be UTF-8
        # encoded).
        result = urllib.parse.unquote_to_bytes("\u6f22%C3%BC")
        expect = b'\xe6\xbc\xa2\xc3\xbc'    # UTF-8 kila "\u6f22\u00fc"
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        # Test ukijumuisha a bytes kama input
        given = b'%A2%D8ab%FF'
        expect = b'\xa2\xd8ab\xff'
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))
        # Test ukijumuisha a bytes kama input, ukijumuisha unescaped non-ASCII bytes
        # (Technically an invalid URI; expect those bytes to be preserved)
        given = b'%A2\xd8ab%FF'
        expect = b'\xa2\xd8ab\xff'
        result = urllib.parse.unquote_to_bytes(given)
        self.assertEqual(expect, result,
                         "using unquote_to_bytes(): %r != %r"
                         % (expect, result))

    eleza test_unquote_with_unicode(self):
        # Characters kwenye the Latin-1 range, encoded ukijumuisha UTF-8
        given = 'br%C3%BCckner_sapporo_20050930.doc'
        expect = 'br\u00fcckner_sapporo_20050930.doc'
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))
        # Characters kwenye the Latin-1 range, encoded ukijumuisha Tupu (default)
        result = urllib.parse.unquote(given, encoding=Tupu, errors=Tupu)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Characters kwenye the Latin-1 range, encoded ukijumuisha Latin-1
        result = urllib.parse.unquote('br%FCckner_sapporo_20050930.doc',
                                      encoding="latin-1")
        expect = 'br\u00fcckner_sapporo_20050930.doc'
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Characters kwenye BMP, encoded ukijumuisha UTF-8
        given = "%E6%BC%A2%E5%AD%97"
        expect = "\u6f22\u5b57"             # "Kanji"
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Decode ukijumuisha UTF-8, invalid sequence
        given = "%F3%B1"
        expect = "\ufffd"                   # Replacement character
        result = urllib.parse.unquote(given)
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Decode ukijumuisha UTF-8, invalid sequence, replace errors
        result = urllib.parse.unquote(given, errors="replace")
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # Decode ukijumuisha UTF-8, invalid sequence, ignoring errors
        given = "%F3%B1"
        expect = ""
        result = urllib.parse.unquote(given, errors="ignore")
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # A mix of non-ASCII na percent-encoded characters, UTF-8
        result = urllib.parse.unquote("\u6f22%C3%BC")
        expect = '\u6f22\u00fc'
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

        # A mix of non-ASCII na percent-encoded characters, Latin-1
        # (Note, the string contains non-Latin-1-representable characters)
        result = urllib.parse.unquote("\u6f22%FC", encoding="latin-1")
        expect = '\u6f22\u00fc'
        self.assertEqual(expect, result,
                         "using unquote(): %r != %r" % (expect, result))

kundi urlencode_Tests(unittest.TestCase):
    """Tests kila urlencode()"""

    eleza help_inputtype(self, given, test_type):
        """Helper method kila testing different input types.

        'given' must lead to only the pairs:
            * 1st, 1
            * 2nd, 2
            * 3rd, 3

        Test cannot assume anything about order.  Docs make no guarantee and
        have possible dictionary input.

        """
        expect_somewhere = ["1st=1", "2nd=2", "3rd=3"]
        result = urllib.parse.urlencode(given)
        kila expected kwenye expect_somewhere:
            self.assertIn(expected, result,
                         "testing %s: %s sio found kwenye %s" %
                         (test_type, expected, result))
        self.assertEqual(result.count('&'), 2,
                         "testing %s: expected 2 '&'s; got %s" %
                         (test_type, result.count('&')))
        amp_location = result.index('&')
        on_amp_left = result[amp_location - 1]
        on_amp_right = result[amp_location + 1]
        self.assertKweli(on_amp_left.isdigit() na on_amp_right.isdigit(),
                     "testing %s: '&' sio located kwenye proper place kwenye %s" %
                     (test_type, result))
        self.assertEqual(len(result), (5 * 3) + 2, #5 chars per thing na amps
                         "testing %s: "
                         "unexpected number of characters: %s != %s" %
                         (test_type, len(result), (5 * 3) + 2))

    eleza test_using_mapping(self):
        # Test pitaing kwenye a mapping object kama an argument.
        self.help_inputtype({"1st":'1', "2nd":'2', "3rd":'3'},
                            "using dict kama input type")

    eleza test_using_sequence(self):
        # Test pitaing kwenye a sequence of two-item sequences kama an argument.
        self.help_inputtype([('1st', '1'), ('2nd', '2'), ('3rd', '3')],
                            "using sequence of two-item tuples kama input")

    eleza test_quoting(self):
        # Make sure keys na values are quoted using quote_plus()
        given = {"&":"="}
        expect = "%s=%s" % (hexescape('&'), hexescape('='))
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)
        given = {"key name":"A bunch of pluses"}
        expect = "key+name=A+bunch+of+pluses"
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)

    eleza test_doseq(self):
        # Test that pitaing Kweli kila 'doseq' parameter works correctly
        given = {'sequence':['1', '2', '3']}
        expect = "sequence=%s" % urllib.parse.quote_plus(str(['1', '2', '3']))
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)
        result = urllib.parse.urlencode(given, Kweli)
        kila value kwenye given["sequence"]:
            expect = "sequence=%s" % value
            self.assertIn(expect, result)
        self.assertEqual(result.count('&'), 2,
                         "Expected 2 '&'s, got %s" % result.count('&'))

    eleza test_empty_sequence(self):
        self.assertEqual("", urllib.parse.urlencode({}))
        self.assertEqual("", urllib.parse.urlencode([]))

    eleza test_nonstring_values(self):
        self.assertEqual("a=1", urllib.parse.urlencode({"a": 1}))
        self.assertEqual("a=Tupu", urllib.parse.urlencode({"a": Tupu}))

    eleza test_nonstring_seq_values(self):
        self.assertEqual("a=1&a=2", urllib.parse.urlencode({"a": [1, 2]}, Kweli))
        self.assertEqual("a=Tupu&a=a",
                         urllib.parse.urlencode({"a": [Tupu, "a"]}, Kweli))
        data = collections.OrderedDict([("a", 1), ("b", 1)])
        self.assertEqual("a=a&a=b",
                         urllib.parse.urlencode({"a": data}, Kweli))

    eleza test_urlencode_encoding(self):
        # ASCII encoding. Expect %3F ukijumuisha errors="replace'
        given = (('\u00a0', '\u00c1'),)
        expect = '%3F=%3F'
        result = urllib.parse.urlencode(given, encoding="ASCII", errors="replace")
        self.assertEqual(expect, result)

        # Default ni UTF-8 encoding.
        given = (('\u00a0', '\u00c1'),)
        expect = '%C2%A0=%C3%81'
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)

        # Latin-1 encoding.
        given = (('\u00a0', '\u00c1'),)
        expect = '%A0=%C1'
        result = urllib.parse.urlencode(given, encoding="latin-1")
        self.assertEqual(expect, result)

    eleza test_urlencode_encoding_doseq(self):
        # ASCII Encoding. Expect %3F ukijumuisha errors="replace'
        given = (('\u00a0', '\u00c1'),)
        expect = '%3F=%3F'
        result = urllib.parse.urlencode(given, doseq=Kweli,
                                        encoding="ASCII", errors="replace")
        self.assertEqual(expect, result)

        # ASCII Encoding. On a sequence of values.
        given = (("\u00a0", (1, "\u00c1")),)
        expect = '%3F=1&%3F=%3F'
        result = urllib.parse.urlencode(given, Kweli,
                                        encoding="ASCII", errors="replace")
        self.assertEqual(expect, result)

        # Utf-8
        given = (("\u00a0", "\u00c1"),)
        expect = '%C2%A0=%C3%81'
        result = urllib.parse.urlencode(given, Kweli)
        self.assertEqual(expect, result)

        given = (("\u00a0", (42, "\u00c1")),)
        expect = '%C2%A0=42&%C2%A0=%C3%81'
        result = urllib.parse.urlencode(given, Kweli)
        self.assertEqual(expect, result)

        # latin-1
        given = (("\u00a0", "\u00c1"),)
        expect = '%A0=%C1'
        result = urllib.parse.urlencode(given, Kweli, encoding="latin-1")
        self.assertEqual(expect, result)

        given = (("\u00a0", (42, "\u00c1")),)
        expect = '%A0=42&%A0=%C1'
        result = urllib.parse.urlencode(given, Kweli, encoding="latin-1")
        self.assertEqual(expect, result)

    eleza test_urlencode_bytes(self):
        given = ((b'\xa0\x24', b'\xc1\x24'),)
        expect = '%A0%24=%C1%24'
        result = urllib.parse.urlencode(given)
        self.assertEqual(expect, result)
        result = urllib.parse.urlencode(given, Kweli)
        self.assertEqual(expect, result)

        # Sequence of values
        given = ((b'\xa0\x24', (42, b'\xc1\x24')),)
        expect = '%A0%24=42&%A0%24=%C1%24'
        result = urllib.parse.urlencode(given, Kweli)
        self.assertEqual(expect, result)

    eleza test_urlencode_encoding_safe_parameter(self):

        # Send '$' (\x24) kama safe character
        # Default utf-8 encoding

        given = ((b'\xa0\x24', b'\xc1\x24'),)
        result = urllib.parse.urlencode(given, safe=":$")
        expect = '%A0$=%C1$'
        self.assertEqual(expect, result)

        given = ((b'\xa0\x24', b'\xc1\x24'),)
        result = urllib.parse.urlencode(given, doseq=Kweli, safe=":$")
        expect = '%A0$=%C1$'
        self.assertEqual(expect, result)

        # Safe parameter kwenye sequence
        given = ((b'\xa0\x24', (b'\xc1\x24', 0xd, 42)),)
        expect = '%A0$=%C1$&%A0$=13&%A0$=42'
        result = urllib.parse.urlencode(given, Kweli, safe=":$")
        self.assertEqual(expect, result)

        # Test all above kwenye latin-1 encoding

        given = ((b'\xa0\x24', b'\xc1\x24'),)
        result = urllib.parse.urlencode(given, safe=":$",
                                        encoding="latin-1")
        expect = '%A0$=%C1$'
        self.assertEqual(expect, result)

        given = ((b'\xa0\x24', b'\xc1\x24'),)
        expect = '%A0$=%C1$'
        result = urllib.parse.urlencode(given, doseq=Kweli, safe=":$",
                                        encoding="latin-1")

        given = ((b'\xa0\x24', (b'\xc1\x24', 0xd, 42)),)
        expect = '%A0$=%C1$&%A0$=13&%A0$=42'
        result = urllib.parse.urlencode(given, Kweli, safe=":$",
                                        encoding="latin-1")
        self.assertEqual(expect, result)

kundi Pathname_Tests(unittest.TestCase):
    """Test pathname2url() na url2pathname()"""

    eleza test_basic(self):
        # Make sure simple tests pita
        expected_path = os.path.join("parts", "of", "a", "path")
        expected_url = "parts/of/a/path"
        result = urllib.request.pathname2url(expected_path)
        self.assertEqual(expected_url, result,
                         "pathname2url() failed; %s != %s" %
                         (result, expected_url))
        result = urllib.request.url2pathname(expected_url)
        self.assertEqual(expected_path, result,
                         "url2pathame() failed; %s != %s" %
                         (result, expected_path))

    eleza test_quoting(self):
        # Test automatic quoting na unquoting works kila pathnam2url() and
        # url2pathname() respectively
        given = os.path.join("needs", "quot=ing", "here")
        expect = "needs/%s/here" % urllib.parse.quote("quot=ing")
        result = urllib.request.pathname2url(given)
        self.assertEqual(expect, result,
                         "pathname2url() failed; %s != %s" %
                         (expect, result))
        expect = given
        result = urllib.request.url2pathname(result)
        self.assertEqual(expect, result,
                         "url2pathname() failed; %s != %s" %
                         (expect, result))
        given = os.path.join("make sure", "using_quote")
        expect = "%s/using_quote" % urllib.parse.quote("make sure")
        result = urllib.request.pathname2url(given)
        self.assertEqual(expect, result,
                         "pathname2url() failed; %s != %s" %
                         (expect, result))
        given = "make+sure/using_unquote"
        expect = os.path.join("make+sure", "using_unquote")
        result = urllib.request.url2pathname(given)
        self.assertEqual(expect, result,
                         "url2pathname() failed; %s != %s" %
                         (expect, result))

    @unittest.skipUnless(sys.platform == 'win32',
                         'test specific to the urllib.url2path function.')
    eleza test_ntpath(self):
        given = ('/C:/', '///C:/', '/C|//')
        expect = 'C:\\'
        kila url kwenye given:
            result = urllib.request.url2pathname(url)
            self.assertEqual(expect, result,
                             'urllib.request..url2pathname() failed; %s != %s' %
                             (expect, result))
        given = '///C|/path'
        expect = 'C:\\path'
        result = urllib.request.url2pathname(given)
        self.assertEqual(expect, result,
                         'urllib.request.url2pathname() failed; %s != %s' %
                         (expect, result))

kundi Utility_Tests(unittest.TestCase):
    """Testcase to test the various utility functions kwenye the urllib."""

    eleza test_thishost(self):
        """Test the urllib.request.thishost utility function rudishas a tuple"""
        self.assertIsInstance(urllib.request.thishost(), tuple)


kundi URLopener_Tests(FakeHTTPMixin, unittest.TestCase):
    """Testcase to test the open method of URLopener class."""

    eleza test_quoted_open(self):
        kundi DummyURLopener(urllib.request.URLopener):
            eleza open_spam(self, url):
                rudisha url
        ukijumuisha support.check_warnings(
                ('DummyURLopener style of invoking requests ni deprecated.',
                DeprecationWarning)):
            self.assertEqual(DummyURLopener().open(
                'spam://example/ /'),'//example/%20/')

            # test the safe characters are sio quoted by urlopen
            self.assertEqual(DummyURLopener().open(
                "spam://c:|windows%/:=&?~#+!$,;'@()*[]|/path/"),
                "//c:|windows%/:=&?~#+!$,;'@()*[]|/path/")

    @support.ignore_warnings(category=DeprecationWarning)
    eleza test_urlopener_retrieve_file(self):
        ukijumuisha support.temp_dir() kama tmpdir:
            fd, tmpfile = tempfile.mkstemp(dir=tmpdir)
            os.close(fd)
            fileurl = "file:" + urllib.request.pathname2url(tmpfile)
            filename, _ = urllib.request.URLopener().retrieve(fileurl)
            # Some buildbots have TEMP folder that uses a lowercase drive letter.
            self.assertEqual(os.path.normcase(filename), os.path.normcase(tmpfile))

    @support.ignore_warnings(category=DeprecationWarning)
    eleza test_urlopener_retrieve_remote(self):
        url = "http://www.python.org/file.txt"
        self.fakehttp(b"HTTP/1.1 200 OK\r\n\r\nHello!")
        self.addCleanup(self.unfakehttp)
        filename, _ = urllib.request.URLopener().retrieve(url)
        self.assertEqual(os.path.splitext(filename)[1], ".txt")

    @support.ignore_warnings(category=DeprecationWarning)
    eleza test_local_file_open(self):
        # bpo-35907, CVE-2019-9948: urllib must reject local_file:// scheme
        kundi DummyURLopener(urllib.request.URLopener):
            eleza open_local_file(self, url):
                rudisha url
        kila url kwenye ('local_file://example', 'local-file://example'):
            self.assertRaises(OSError, urllib.request.urlopen, url)
            self.assertRaises(OSError, urllib.request.URLopener().open, url)
            self.assertRaises(OSError, urllib.request.URLopener().retrieve, url)
            self.assertRaises(OSError, DummyURLopener().open, url)
            self.assertRaises(OSError, DummyURLopener().retrieve, url)


# Just commented them out.
# Can't really tell why keep failing kwenye windows na sparc.
# Everywhere isipokua they work ok, but on those machines, sometimes
# fail kwenye one of the tests, sometimes kwenye other. I have a linux, and
# the tests go ok.
# If anybody has one of the problematic environments, please help!
# .   Facundo
#
# eleza server(evt):
#     agiza socket, time
#     serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     serv.settimeout(3)
#     serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     serv.bind(("", 9093))
#     serv.listen()
#     jaribu:
#         conn, addr = serv.accept()
#         conn.send("1 Hola mundo\n")
#         cantdata = 0
#         wakati cantdata < 13:
#             data = conn.recv(13-cantdata)
#             cantdata += len(data)
#             time.sleep(.3)
#         conn.send("2 No more lines\n")
#         conn.close()
#     tatizo socket.timeout:
#         pita
#     mwishowe:
#         serv.close()
#         evt.set()
#
# kundi FTPWrapperTests(unittest.TestCase):
#
#     eleza setUp(self):
#         agiza ftplib, time, threading
#         ftplib.FTP.port = 9093
#         self.evt = threading.Event()
#         threading.Thread(target=server, args=(self.evt,)).start()
#         time.sleep(.1)
#
#     eleza tearDown(self):
#         self.evt.wait()
#
#     eleza testBasic(self):
#         # connects
#         ftp = urllib.ftpwrapper("myuser", "mypita", "localhost", 9093, [])
#         ftp.close()
#
#     eleza testTimeoutTupu(self):
#         # global default timeout ni ignored
#         agiza socket
#         self.assertIsTupu(socket.getdefaulttimeout())
#         socket.setdefaulttimeout(30)
#         jaribu:
#             ftp = urllib.ftpwrapper("myuser", "mypita", "localhost", 9093, [])
#         mwishowe:
#             socket.setdefaulttimeout(Tupu)
#         self.assertEqual(ftp.ftp.sock.gettimeout(), 30)
#         ftp.close()
#
#     eleza testTimeoutDefault(self):
#         # global default timeout ni used
#         agiza socket
#         self.assertIsTupu(socket.getdefaulttimeout())
#         socket.setdefaulttimeout(30)
#         jaribu:
#             ftp = urllib.ftpwrapper("myuser", "mypita", "localhost", 9093, [])
#         mwishowe:
#             socket.setdefaulttimeout(Tupu)
#         self.assertEqual(ftp.ftp.sock.gettimeout(), 30)
#         ftp.close()
#
#     eleza testTimeoutValue(self):
#         ftp = urllib.ftpwrapper("myuser", "mypita", "localhost", 9093, [],
#                                 timeout=30)
#         self.assertEqual(ftp.ftp.sock.gettimeout(), 30)
#         ftp.close()


kundi RequestTests(unittest.TestCase):
    """Unit tests kila urllib.request.Request."""

    eleza test_default_values(self):
        Request = urllib.request.Request
        request = Request("http://www.python.org")
        self.assertEqual(request.get_method(), 'GET')
        request = Request("http://www.python.org", {})
        self.assertEqual(request.get_method(), 'POST')

    eleza test_with_method_arg(self):
        Request = urllib.request.Request
        request = Request("http://www.python.org", method='HEAD')
        self.assertEqual(request.method, 'HEAD')
        self.assertEqual(request.get_method(), 'HEAD')
        request = Request("http://www.python.org", {}, method='HEAD')
        self.assertEqual(request.method, 'HEAD')
        self.assertEqual(request.get_method(), 'HEAD')
        request = Request("http://www.python.org", method='GET')
        self.assertEqual(request.get_method(), 'GET')
        request.method = 'HEAD'
        self.assertEqual(request.get_method(), 'HEAD')


kundi URL2PathNameTests(unittest.TestCase):

    eleza test_converting_drive_letter(self):
        self.assertEqual(url2pathname("///C|"), 'C:')
        self.assertEqual(url2pathname("///C:"), 'C:')
        self.assertEqual(url2pathname("///C|/"), 'C:\\')

    eleza test_converting_when_no_drive_letter(self):
        # cannot end a raw string kwenye \
        self.assertEqual(url2pathname("///C/test/"), r'\\\C\test' '\\')
        self.assertEqual(url2pathname("////C/test/"), r'\\C\test' '\\')

    eleza test_simple_compare(self):
        self.assertEqual(url2pathname("///C|/foo/bar/spam.foo"),
                         r'C:\foo\bar\spam.foo')

    eleza test_non_ascii_drive_letter(self):
        self.assertRaises(IOError, url2pathname, "///\u00e8|/")

    eleza test_roundtrip_url2pathname(self):
        list_of_paths = ['C:',
                         r'\\\C\test\\',
                         r'C:\foo\bar\spam.foo'
                         ]
        kila path kwenye list_of_paths:
            self.assertEqual(url2pathname(pathname2url(path)), path)

kundi PathName2URLTests(unittest.TestCase):

    eleza test_converting_drive_letter(self):
        self.assertEqual(pathname2url("C:"), '///C:')
        self.assertEqual(pathname2url("C:\\"), '///C:')

    eleza test_converting_when_no_drive_letter(self):
        self.assertEqual(pathname2url(r"\\\folder\test" "\\"),
                         '/////folder/test/')
        self.assertEqual(pathname2url(r"\\folder\test" "\\"),
                         '////folder/test/')
        self.assertEqual(pathname2url(r"\folder\test" "\\"),
                         '/folder/test/')

    eleza test_simple_compare(self):
        self.assertEqual(pathname2url(r'C:\foo\bar\spam.foo'),
                         "///C:/foo/bar/spam.foo" )

    eleza test_long_drive_letter(self):
        self.assertRaises(IOError, pathname2url, "XX:\\")

    eleza test_roundtrip_pathname2url(self):
        list_of_paths = ['///C:',
                         '/////folder/test/',
                         '///C:/foo/bar/spam.foo']
        kila path kwenye list_of_paths:
            self.assertEqual(pathname2url(url2pathname(path)), path)

ikiwa __name__ == '__main__':
    unittest.main()
