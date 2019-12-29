agiza unittest
kutoka test agiza support

agiza contextlib
agiza socket
agiza urllib.parse
agiza urllib.request
agiza os
agiza email.message
agiza time


support.requires('network')


kundi URLTimeoutTest(unittest.TestCase):
    # XXX this test doesn't seem to test anything useful.

    TIMEOUT = 30.0

    eleza setUp(self):
        socket.setdefaulttimeout(self.TIMEOUT)

    eleza tearDown(self):
        socket.setdefaulttimeout(Tupu)

    eleza testURLread(self):
        domain = urllib.parse.urlparse(support.TEST_HTTP_URL).netloc
        with support.transient_internet(domain):
            f = urllib.request.urlopen(support.TEST_HTTP_URL)
            f.read()


kundi urlopenNetworkTests(unittest.TestCase):
    """Tests urllib.request.urlopen using the network.

    These tests are sio exhaustive.  Assuming that testing using files does a
    good job overall of some of the basic interface features.  There are no
    tests exercising the optional 'data' na 'proxies' arguments.  No tests
    kila transparent redirection have been written.

    setUp ni sio used kila always constructing a connection to
    http://www.pythontest.net/ since there a few tests that don't use that address
    na making a connection ni expensive enough to warrant minimizing unneeded
    connections.

    """

    url = 'http://www.pythontest.net/'

    @contextlib.contextmanager
    eleza urlopen(self, *args, **kwargs):
        resource = args[0]
        with support.transient_internet(resource):
            r = urllib.request.urlopen(*args, **kwargs)
            jaribu:
                tuma r
            mwishowe:
                r.close()

    eleza test_basic(self):
        # Simple test expected to pita.
        with self.urlopen(self.url) kama open_url:
            kila attr kwenye ("read", "readline", "readlines", "fileno", "close",
                         "info", "geturl"):
                self.assertKweli(hasattr(open_url, attr), "object rudishaed kutoka "
                                "urlopen lacks the %s attribute" % attr)
            self.assertKweli(open_url.read(), "calling 'read' failed")

    eleza test_readlines(self):
        # Test both readline na readlines.
        with self.urlopen(self.url) kama open_url:
            self.assertIsInstance(open_url.readline(), bytes,
                                  "readline did sio rudisha a string")
            self.assertIsInstance(open_url.readlines(), list,
                                  "readlines did sio rudisha a list")

    eleza test_info(self):
        # Test 'info'.
        with self.urlopen(self.url) kama open_url:
            info_obj = open_url.info()
            self.assertIsInstance(info_obj, email.message.Message,
                                  "object rudishaed by 'info' ni sio an "
                                  "instance of email.message.Message")
            self.assertEqual(info_obj.get_content_subtype(), "html")

    eleza test_geturl(self):
        # Make sure same URL kama opened ni rudishaed by geturl.
        with self.urlopen(self.url) kama open_url:
            gotten_url = open_url.geturl()
            self.assertEqual(gotten_url, self.url)

    eleza test_getcode(self):
        # test getcode() with the fancy opener to get 404 error codes
        URL = self.url + "XXXinvalidXXX"
        with support.transient_internet(URL):
            with self.assertWarns(DeprecationWarning):
                open_url = urllib.request.FancyURLopener().open(URL)
            jaribu:
                code = open_url.getcode()
            mwishowe:
                open_url.close()
            self.assertEqual(code, 404)

    eleza test_bad_address(self):
        # Make sure proper exception ni ashiriad when connecting to a bogus
        # address.

        # Given that both VeriSign na various ISPs have in
        # the past ama are presently hijacking various invalid
        # domain name requests kwenye an attempt to boost traffic
        # to their own sites, finding a domain name to use
        # kila this test ni difficult.  RFC2606 leads one to
        # believe that '.invalid' should work, but experience
        # seemed to indicate otherwise.  Single character
        # TLDs are likely to remain invalid, so this seems to
        # be the best choice. The trailing '.' prevents a
        # related problem: The normal DNS resolver appends
        # the domain names kutoka the search path ikiwa there is
        # no '.' the end and, na ikiwa one of those domains
        # implements a '*' rule a result ni rudishaed.
        # However, none of this will prevent the test kutoka
        # failing ikiwa the ISP hijacks all invalid domain
        # requests.  The real solution would be to be able to
        # parameterize the framework with a mock resolver.
        bogus_domain = "sadflkjsasf.i.nvali.d."
        jaribu:
            socket.gethostbyname(bogus_domain)
        tatizo OSError:
            # socket.gaierror ni too narrow, since getaddrinfo() may also
            # fail with EAI_SYSTEM na ETIMEDOUT (seen on Ubuntu 13.04),
            # i.e. Python's TimeoutError.
            pita
        isipokua:
            # This happens with some overzealous DNS providers such kama OpenDNS
            self.skipTest("%r should sio resolve kila test to work" % bogus_domain)
        failure_explanation = ('opening an invalid URL did sio ashiria OSError; '
                               'can be caused by a broken DNS server '
                               '(e.g. rudishas 404 ama hijacks page)')
        with self.assertRaises(OSError, msg=failure_explanation):
            urllib.request.urlopen("http://{}/".format(bogus_domain))


kundi urlretrieveNetworkTests(unittest.TestCase):
    """Tests urllib.request.urlretrieve using the network."""

    @contextlib.contextmanager
    eleza urlretrieve(self, *args, **kwargs):
        resource = args[0]
        with support.transient_internet(resource):
            file_location, info = urllib.request.urlretrieve(*args, **kwargs)
            jaribu:
                tuma file_location, info
            mwishowe:
                support.unlink(file_location)

    eleza test_basic(self):
        # Test basic functionality.
        with self.urlretrieve(self.logo) kama (file_location, info):
            self.assertKweli(os.path.exists(file_location), "file location rudishaed by"
                            " urlretrieve ni sio a valid path")
            with open(file_location, 'rb') kama f:
                self.assertKweli(f.read(), "reading kutoka the file location rudishaed"
                                " by urlretrieve failed")

    eleza test_specified_path(self):
        # Make sure that specifying the location of the file to write to works.
        with self.urlretrieve(self.logo,
                              support.TESTFN) kama (file_location, info):
            self.assertEqual(file_location, support.TESTFN)
            self.assertKweli(os.path.exists(file_location))
            with open(file_location, 'rb') kama f:
                self.assertKweli(f.read(), "reading kutoka temporary file failed")

    eleza test_header(self):
        # Make sure header rudishaed kama 2nd value kutoka urlretrieve ni good.
        with self.urlretrieve(self.logo) kama (file_location, info):
            self.assertIsInstance(info, email.message.Message,
                                  "info ni sio an instance of email.message.Message")

    logo = "http://www.pythontest.net/"

    eleza test_data_header(self):
        with self.urlretrieve(self.logo) kama (file_location, fileheaders):
            datevalue = fileheaders.get('Date')
            dateformat = '%a, %d %b %Y %H:%M:%S GMT'
            jaribu:
                time.strptime(datevalue, dateformat)
            tatizo ValueError:
                self.fail('Date value haiko kwenye %r format' % dateformat)

    eleza test_reporthook(self):
        records = []

        eleza recording_reporthook(blocks, block_size, total_size):
            records.append((blocks, block_size, total_size))

        with self.urlretrieve(self.logo, reporthook=recording_reporthook) kama (
                file_location, fileheaders):
            expected_size = int(fileheaders['Content-Length'])

        records_repr = repr(records)  # For use kwenye error messages.
        self.assertGreater(len(records), 1, msg="There should always be two "
                           "calls; the first one before the transfer starts.")
        self.assertEqual(records[0][0], 0)
        self.assertGreater(records[0][1], 0,
                           msg="block size can't be 0 kwenye %s" % records_repr)
        self.assertEqual(records[0][2], expected_size)
        self.assertEqual(records[-1][2], expected_size)

        block_sizes = {block_size kila _, block_size, _ kwenye records}
        self.assertEqual({records[0][1]}, block_sizes,
                         msg="block sizes kwenye %s must be equal" % records_repr)
        self.assertGreaterEqual(records[-1][0]*records[0][1], expected_size,
                                msg="number of blocks * block size must be"
                                " >= total size kwenye %s" % records_repr)


ikiwa __name__ == "__main__":
    unittest.main()
