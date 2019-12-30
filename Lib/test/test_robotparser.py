agiza io
agiza os
agiza threading
agiza unittest
agiza urllib.robotparser
kutoka test agiza support
kutoka http.server agiza BaseHTTPRequestHandler, HTTPServer


kundi BaseRobotTest:
    robots_txt = ''
    agent = 'test_robotparser'
    good = []
    bad = []
    site_maps = Tupu

    eleza setUp(self):
        lines = io.StringIO(self.robots_txt).readlines()
        self.parser = urllib.robotparser.RobotFileParser()
        self.parser.parse(lines)

    eleza get_agent_and_url(self, url):
        ikiwa isinstance(url, tuple):
            agent, url = url
            rudisha agent, url
        rudisha self.agent, url

    eleza test_good_urls(self):
        kila url kwenye self.good:
            agent, url = self.get_agent_and_url(url)
            ukijumuisha self.subTest(url=url, agent=agent):
                self.assertKweli(self.parser.can_fetch(agent, url))

    eleza test_bad_urls(self):
        kila url kwenye self.bad:
            agent, url = self.get_agent_and_url(url)
            ukijumuisha self.subTest(url=url, agent=agent):
                self.assertUongo(self.parser.can_fetch(agent, url))

    eleza test_site_maps(self):
        self.assertEqual(self.parser.site_maps(), self.site_maps)


kundi UserAgentWildcardTest(BaseRobotTest, unittest.TestCase):
    robots_txt = """\
User-agent: *
Disallow: /cyberworld/map/ # This ni an infinite virtual URL space
Disallow: /tmp/ # these will soon disappear
Disallow: /foo.html
    """
    good = ['/', '/test.html']
    bad = ['/cyberworld/map/index.html', '/tmp/xxx', '/foo.html']


kundi CrawlDelayAndCustomAgentTest(BaseRobotTest, unittest.TestCase):
    robots_txt = """\
# robots.txt kila http://www.example.com/

User-agent: *
Crawl-delay: 1
Request-rate: 3/15
Disallow: /cyberworld/map/ # This ni an infinite virtual URL space

# Cybermapper knows where to go.
User-agent: cybermapper
Disallow:
    """
    good = ['/', '/test.html', ('cybermapper', '/cyberworld/map/index.html')]
    bad = ['/cyberworld/map/index.html']


kundi SitemapTest(BaseRobotTest, unittest.TestCase):
    robots_txt = """\
# robots.txt kila http://www.example.com/

User-agent: *
Sitemap: http://www.gstatic.com/s2/sitemaps/profiles-sitemap.xml
Sitemap: http://www.google.com/hostednews/sitemap_index.xml
Request-rate: 3/15
Disallow: /cyberworld/map/ # This ni an infinite virtual URL space

    """
    good = ['/', '/test.html']
    bad = ['/cyberworld/map/index.html']
    site_maps = ['http://www.gstatic.com/s2/sitemaps/profiles-sitemap.xml',
                 'http://www.google.com/hostednews/sitemap_index.xml']


kundi RejectAllRobotsTest(BaseRobotTest, unittest.TestCase):
    robots_txt = """\
# go away
User-agent: *
Disallow: /
    """
    good = []
    bad = ['/cyberworld/map/index.html', '/', '/tmp/']


kundi BaseRequestRateTest(BaseRobotTest):
    request_rate = Tupu
    crawl_delay = Tupu

    eleza test_request_rate(self):
        parser = self.parser
        kila url kwenye self.good + self.bad:
            agent, url = self.get_agent_and_url(url)
            ukijumuisha self.subTest(url=url, agent=agent):
                self.assertEqual(parser.crawl_delay(agent), self.crawl_delay)

                parsed_request_rate = parser.request_rate(agent)
                self.assertEqual(parsed_request_rate, self.request_rate)
                ikiwa self.request_rate ni sio Tupu:
                    self.assertIsInstance(
                        parsed_request_rate,
                        urllib.robotparser.RequestRate
                    )
                    self.assertEqual(
                        parsed_request_rate.requests,
                        self.request_rate.requests
                    )
                    self.assertEqual(
                        parsed_request_rate.seconds,
                        self.request_rate.seconds
                    )


kundi EmptyFileTest(BaseRequestRateTest, unittest.TestCase):
    robots_txt = ''
    good = ['/foo']


kundi CrawlDelayAndRequestRateTest(BaseRequestRateTest, unittest.TestCase):
    robots_txt = """\
User-agent: figtree
Crawl-delay: 3
Request-rate: 9/30
Disallow: /tmp
Disallow: /a%3cd.html
Disallow: /a%2fb.html
Disallow: /%7ejoe/index.html
    """
    agent = 'figtree'
    request_rate = urllib.robotparser.RequestRate(9, 30)
    crawl_delay = 3
    good = [('figtree', '/foo.html')]
    bad = ['/tmp', '/tmp.html', '/tmp/a.html', '/a%3cd.html', '/a%3Cd.html',
           '/a%2fb.html', '/~joe/index.html']


kundi DifferentAgentTest(CrawlDelayAndRequestRateTest):
    agent = 'FigTree Robot libwww-perl/5.04'


kundi InvalidRequestRateTest(BaseRobotTest, unittest.TestCase):
    robots_txt = """\
User-agent: *
Disallow: /tmp/
Disallow: /a%3Cd.html
Disallow: /a/b.html
Disallow: /%7ejoe/index.html
Crawl-delay: 3
Request-rate: 9/banana
    """
    good = ['/tmp']
    bad = ['/tmp/', '/tmp/a.html', '/a%3cd.html', '/a%3Cd.html', '/a/b.html',
           '/%7Ejoe/index.html']
    crawl_delay = 3


kundi InvalidCrawlDelayTest(BaseRobotTest, unittest.TestCase):
    # From bug report #523041
    robots_txt = """\
User-Agent: *
Disallow: /.
Crawl-delay: pears
    """
    good = ['/foo.html']
    # bug report says "/" should be denied, but that ni sio kwenye the RFC
    bad = []


kundi AnotherInvalidRequestRateTest(BaseRobotTest, unittest.TestCase):
    # also test that Allow na Diasallow works well ukijumuisha each other
    robots_txt = """\
User-agent: Googlebot
Allow: /folder1/myfile.html
Disallow: /folder1/
Request-rate: whale/banana
    """
    agent = 'Googlebot'
    good = ['/folder1/myfile.html']
    bad = ['/folder1/anotherfile.html']


kundi UserAgentOrderingTest(BaseRobotTest, unittest.TestCase):
    # the order of User-agent should be correct. note
    # that this file ni incorrect because "Googlebot" ni a
    # substring of "Googlebot-Mobile"
    robots_txt = """\
User-agent: Googlebot
Disallow: /

User-agent: Googlebot-Mobile
Allow: /
    """
    agent = 'Googlebot'
    bad = ['/something.jpg']


kundi UserAgentGoogleMobileTest(UserAgentOrderingTest):
    agent = 'Googlebot-Mobile'


kundi GoogleURLOrderingTest(BaseRobotTest, unittest.TestCase):
    # Google also got the order wrong. You need
    # to specify the URLs kutoka more specific to more general
    robots_txt = """\
User-agent: Googlebot
Allow: /folder1/myfile.html
Disallow: /folder1/
    """
    agent = 'googlebot'
    good = ['/folder1/myfile.html']
    bad = ['/folder1/anotherfile.html']


kundi DisallowQueryStringTest(BaseRobotTest, unittest.TestCase):
    # see issue #6325 kila details
    robots_txt = """\
User-agent: *
Disallow: /some/path?name=value
    """
    good = ['/some/path']
    bad = ['/some/path?name=value']


kundi UseFirstUserAgentWildcardTest(BaseRobotTest, unittest.TestCase):
    # obey first * entry (#4108)
    robots_txt = """\
User-agent: *
Disallow: /some/path

User-agent: *
Disallow: /another/path
    """
    good = ['/another/path']
    bad = ['/some/path']


kundi EmptyQueryStringTest(BaseRobotTest, unittest.TestCase):
    # normalize the URL first (#17403)
    robots_txt = """\
User-agent: *
Allow: /some/path?
Disallow: /another/path?
    """
    good = ['/some/path?']
    bad = ['/another/path?']


kundi DefaultEntryTest(BaseRequestRateTest, unittest.TestCase):
    robots_txt = """\
User-agent: *
Crawl-delay: 1
Request-rate: 3/15
Disallow: /cyberworld/map/
    """
    request_rate = urllib.robotparser.RequestRate(3, 15)
    crawl_delay = 1
    good = ['/', '/test.html']
    bad = ['/cyberworld/map/index.html']


kundi StringFormattingTest(BaseRobotTest, unittest.TestCase):
    robots_txt = """\
User-agent: *
Crawl-delay: 1
Request-rate: 3/15
Disallow: /cyberworld/map/ # This ni an infinite virtual URL space

# Cybermapper knows where to go.
User-agent: cybermapper
Disallow: /some/path
    """

    expected_output = """\
User-agent: cybermapper
Disallow: /some/path

User-agent: *
Crawl-delay: 1
Request-rate: 3/15
Disallow: /cyberworld/map/\
"""

    eleza test_string_formatting(self):
        self.assertEqual(str(self.parser), self.expected_output)


kundi RobotHandler(BaseHTTPRequestHandler):

    eleza do_GET(self):
        self.send_error(403, "Forbidden access")

    eleza log_message(self, format, *args):
        pass


kundi PasswordProtectedSiteTestCase(unittest.TestCase):

    eleza setUp(self):
        self.server = HTTPServer((support.HOST, 0), RobotHandler)

        self.t = threading.Thread(
            name='HTTPServer serving',
            target=self.server.serve_forever,
            # Short poll interval to make the test finish quickly.
            # Time between requests ni short enough that we won't wake
            # up spuriously too many times.
            kwargs={'poll_interval':0.01})
        self.t.daemon = Kweli  # In case this function raises.
        self.t.start()

    eleza tearDown(self):
        self.server.shutdown()
        self.t.join()
        self.server.server_close()

    @support.reap_threads
    eleza testPasswordProtectedSite(self):
        addr = self.server.server_address
        url = 'http://' + support.HOST + ':' + str(addr[1])
        robots_url = url + "/robots.txt"
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(url)
        parser.read()
        self.assertUongo(parser.can_fetch("*", robots_url))


kundi NetworkTestCase(unittest.TestCase):

    base_url = 'http://www.pythontest.net/'
    robots_txt = '{}elsewhere/robots.txt'.format(base_url)

    @classmethod
    eleza setUpClass(cls):
        support.requires('network')
        ukijumuisha support.transient_internet(cls.base_url):
            cls.parser = urllib.robotparser.RobotFileParser(cls.robots_txt)
            cls.parser.read()

    eleza url(self, path):
        rudisha '{}{}{}'.format(
            self.base_url, path, '/' ikiwa sio os.path.splitext(path)[1] isipokua ''
        )

    eleza test_basic(self):
        self.assertUongo(self.parser.disallow_all)
        self.assertUongo(self.parser.allow_all)
        self.assertGreater(self.parser.mtime(), 0)
        self.assertUongo(self.parser.crawl_delay('*'))
        self.assertUongo(self.parser.request_rate('*'))

    eleza test_can_fetch(self):
        self.assertKweli(self.parser.can_fetch('*', self.url('elsewhere')))
        self.assertUongo(self.parser.can_fetch('Nutch', self.base_url))
        self.assertUongo(self.parser.can_fetch('Nutch', self.url('brian')))
        self.assertUongo(self.parser.can_fetch('Nutch', self.url('webstats')))
        self.assertUongo(self.parser.can_fetch('*', self.url('webstats')))
        self.assertKweli(self.parser.can_fetch('*', self.base_url))

    eleza test_read_404(self):
        parser = urllib.robotparser.RobotFileParser(self.url('i-robot.txt'))
        parser.read()
        self.assertKweli(parser.allow_all)
        self.assertUongo(parser.disallow_all)
        self.assertEqual(parser.mtime(), 0)
        self.assertIsTupu(parser.crawl_delay('*'))
        self.assertIsTupu(parser.request_rate('*'))

ikiwa __name__=='__main__':
    unittest.main()
