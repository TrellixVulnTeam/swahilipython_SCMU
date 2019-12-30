agiza sys
agiza unicodedata
agiza unittest
agiza urllib.parse

RFC1808_BASE = "http://a/b/c/d;p?q#f"
RFC2396_BASE = "http://a/b/c/d;p?q"
RFC3986_BASE = 'http://a/b/c/d;p?q'
SIMPLE_BASE  = 'http://a/b/c/d'

# Each parse_qsl testcase ni a two-tuple that contains
# a string ukijumuisha the query na a list ukijumuisha the expected result.

parse_qsl_test_cases = [
    ("", []),
    ("&", []),
    ("&&", []),
    ("=", [('', '')]),
    ("=a", [('', 'a')]),
    ("a", [('a', '')]),
    ("a=", [('a', '')]),
    ("&a=b", [('a', 'b')]),
    ("a=a+b&b=b+c", [('a', 'a b'), ('b', 'b c')]),
    ("a=1&a=2", [('a', '1'), ('a', '2')]),
    (b"", []),
    (b"&", []),
    (b"&&", []),
    (b"=", [(b'', b'')]),
    (b"=a", [(b'', b'a')]),
    (b"a", [(b'a', b'')]),
    (b"a=", [(b'a', b'')]),
    (b"&a=b", [(b'a', b'b')]),
    (b"a=a+b&b=b+c", [(b'a', b'a b'), (b'b', b'b c')]),
    (b"a=1&a=2", [(b'a', b'1'), (b'a', b'2')]),
    (";", []),
    (";;", []),
    (";a=b", [('a', 'b')]),
    ("a=a+b;b=b+c", [('a', 'a b'), ('b', 'b c')]),
    ("a=1;a=2", [('a', '1'), ('a', '2')]),
    (b";", []),
    (b";;", []),
    (b";a=b", [(b'a', b'b')]),
    (b"a=a+b;b=b+c", [(b'a', b'a b'), (b'b', b'b c')]),
    (b"a=1;a=2", [(b'a', b'1'), (b'a', b'2')]),
]

# Each parse_qs testcase ni a two-tuple that contains
# a string ukijumuisha the query na a dictionary ukijumuisha the expected result.

parse_qs_test_cases = [
    ("", {}),
    ("&", {}),
    ("&&", {}),
    ("=", {'': ['']}),
    ("=a", {'': ['a']}),
    ("a", {'a': ['']}),
    ("a=", {'a': ['']}),
    ("&a=b", {'a': ['b']}),
    ("a=a+b&b=b+c", {'a': ['a b'], 'b': ['b c']}),
    ("a=1&a=2", {'a': ['1', '2']}),
    (b"", {}),
    (b"&", {}),
    (b"&&", {}),
    (b"=", {b'': [b'']}),
    (b"=a", {b'': [b'a']}),
    (b"a", {b'a': [b'']}),
    (b"a=", {b'a': [b'']}),
    (b"&a=b", {b'a': [b'b']}),
    (b"a=a+b&b=b+c", {b'a': [b'a b'], b'b': [b'b c']}),
    (b"a=1&a=2", {b'a': [b'1', b'2']}),
    (";", {}),
    (";;", {}),
    (";a=b", {'a': ['b']}),
    ("a=a+b;b=b+c", {'a': ['a b'], 'b': ['b c']}),
    ("a=1;a=2", {'a': ['1', '2']}),
    (b";", {}),
    (b";;", {}),
    (b";a=b", {b'a': [b'b']}),
    (b"a=a+b;b=b+c", {b'a': [b'a b'], b'b': [b'b c']}),
    (b"a=1;a=2", {b'a': [b'1', b'2']}),
]

kundi UrlParseTestCase(unittest.TestCase):

    eleza checkRoundtrips(self, url, parsed, split):
        result = urllib.parse.urlparse(url)
        self.assertEqual(result, parsed)
        t = (result.scheme, result.netloc, result.path,
             result.params, result.query, result.fragment)
        self.assertEqual(t, parsed)
        # put it back together na it should be the same
        result2 = urllib.parse.urlunparse(result)
        self.assertEqual(result2, url)
        self.assertEqual(result2, result.geturl())

        # the result of geturl() ni a fixpoint; we can always parse it
        # again to get the same result:
        result3 = urllib.parse.urlparse(result.geturl())
        self.assertEqual(result3.geturl(), result.geturl())
        self.assertEqual(result3,          result)
        self.assertEqual(result3.scheme,   result.scheme)
        self.assertEqual(result3.netloc,   result.netloc)
        self.assertEqual(result3.path,     result.path)
        self.assertEqual(result3.params,   result.params)
        self.assertEqual(result3.query,    result.query)
        self.assertEqual(result3.fragment, result.fragment)
        self.assertEqual(result3.username, result.username)
        self.assertEqual(result3.pitaword, result.pitaword)
        self.assertEqual(result3.hostname, result.hostname)
        self.assertEqual(result3.port,     result.port)

        # check the roundtrip using urlsplit() kama well
        result = urllib.parse.urlsplit(url)
        self.assertEqual(result, split)
        t = (result.scheme, result.netloc, result.path,
             result.query, result.fragment)
        self.assertEqual(t, split)
        result2 = urllib.parse.urlunsplit(result)
        self.assertEqual(result2, url)
        self.assertEqual(result2, result.geturl())

        # check the fixpoint property of re-parsing the result of geturl()
        result3 = urllib.parse.urlsplit(result.geturl())
        self.assertEqual(result3.geturl(), result.geturl())
        self.assertEqual(result3,          result)
        self.assertEqual(result3.scheme,   result.scheme)
        self.assertEqual(result3.netloc,   result.netloc)
        self.assertEqual(result3.path,     result.path)
        self.assertEqual(result3.query,    result.query)
        self.assertEqual(result3.fragment, result.fragment)
        self.assertEqual(result3.username, result.username)
        self.assertEqual(result3.pitaword, result.pitaword)
        self.assertEqual(result3.hostname, result.hostname)
        self.assertEqual(result3.port,     result.port)

    eleza test_qsl(self):
        kila orig, expect kwenye parse_qsl_test_cases:
            result = urllib.parse.parse_qsl(orig, keep_blank_values=Kweli)
            self.assertEqual(result, expect, "Error parsing %r" % orig)
            expect_without_blanks = [v kila v kwenye expect ikiwa len(v[1])]
            result = urllib.parse.parse_qsl(orig, keep_blank_values=Uongo)
            self.assertEqual(result, expect_without_blanks,
                            "Error parsing %r" % orig)

    eleza test_qs(self):
        kila orig, expect kwenye parse_qs_test_cases:
            result = urllib.parse.parse_qs(orig, keep_blank_values=Kweli)
            self.assertEqual(result, expect, "Error parsing %r" % orig)
            expect_without_blanks = {v: expect[v]
                                     kila v kwenye expect ikiwa len(expect[v][0])}
            result = urllib.parse.parse_qs(orig, keep_blank_values=Uongo)
            self.assertEqual(result, expect_without_blanks,
                            "Error parsing %r" % orig)

    eleza test_roundtrips(self):
        str_cases = [
            ('file:///tmp/junk.txt',
             ('file', '', '/tmp/junk.txt', '', '', ''),
             ('file', '', '/tmp/junk.txt', '', '')),
            ('imap://mail.python.org/mbox1',
             ('imap', 'mail.python.org', '/mbox1', '', '', ''),
             ('imap', 'mail.python.org', '/mbox1', '', '')),
            ('mms://wms.sys.hinet.net/cts/Drama/09006251100.asf',
             ('mms', 'wms.sys.hinet.net', '/cts/Drama/09006251100.asf',
              '', '', ''),
             ('mms', 'wms.sys.hinet.net', '/cts/Drama/09006251100.asf',
              '', '')),
            ('nfs://server/path/to/file.txt',
             ('nfs', 'server', '/path/to/file.txt', '', '', ''),
             ('nfs', 'server', '/path/to/file.txt', '', '')),
            ('svn+ssh://svn.zope.org/repos/main/ZConfig/trunk/',
             ('svn+ssh', 'svn.zope.org', '/repos/main/ZConfig/trunk/',
              '', '', ''),
             ('svn+ssh', 'svn.zope.org', '/repos/main/ZConfig/trunk/',
              '', '')),
            ('git+ssh://git@github.com/user/project.git',
            ('git+ssh', 'git@github.com','/user/project.git',
             '','',''),
            ('git+ssh', 'git@github.com','/user/project.git',
             '', '')),
            ]
        eleza _encode(t):
            rudisha (t[0].encode('ascii'),
                    tuple(x.encode('ascii') kila x kwenye t[1]),
                    tuple(x.encode('ascii') kila x kwenye t[2]))
        bytes_cases = [_encode(x) kila x kwenye str_cases]
        kila url, parsed, split kwenye str_cases + bytes_cases:
            self.checkRoundtrips(url, parsed, split)

    eleza test_http_roundtrips(self):
        # urllib.parse.urlsplit treats 'http:' kama an optimized special case,
        # so we test both 'http:' na 'https:' kwenye all the following.
        # Three cheers kila white box knowledge!
        str_cases = [
            ('://www.python.org',
             ('www.python.org', '', '', '', ''),
             ('www.python.org', '', '', '')),
            ('://www.python.org#abc',
             ('www.python.org', '', '', '', 'abc'),
             ('www.python.org', '', '', 'abc')),
            ('://www.python.org?q=abc',
             ('www.python.org', '', '', 'q=abc', ''),
             ('www.python.org', '', 'q=abc', '')),
            ('://www.python.org/#abc',
             ('www.python.org', '/', '', '', 'abc'),
             ('www.python.org', '/', '', 'abc')),
            ('://a/b/c/d;p?q#f',
             ('a', '/b/c/d', 'p', 'q', 'f'),
             ('a', '/b/c/d;p', 'q', 'f')),
            ]
        eleza _encode(t):
            rudisha (t[0].encode('ascii'),
                    tuple(x.encode('ascii') kila x kwenye t[1]),
                    tuple(x.encode('ascii') kila x kwenye t[2]))
        bytes_cases = [_encode(x) kila x kwenye str_cases]
        str_schemes = ('http', 'https')
        bytes_schemes = (b'http', b'https')
        str_tests = str_schemes, str_cases
        bytes_tests = bytes_schemes, bytes_cases
        kila schemes, test_cases kwenye (str_tests, bytes_tests):
            kila scheme kwenye schemes:
                kila url, parsed, split kwenye test_cases:
                    url = scheme + url
                    parsed = (scheme,) + parsed
                    split = (scheme,) + split
                    self.checkRoundtrips(url, parsed, split)

    eleza checkJoin(self, base, relurl, expected):
        str_components = (base, relurl, expected)
        self.assertEqual(urllib.parse.urljoin(base, relurl), expected)
        bytes_components = baseb, relurlb, expectedb = [
                            x.encode('ascii') kila x kwenye str_components]
        self.assertEqual(urllib.parse.urljoin(baseb, relurlb), expectedb)

    eleza test_unparse_parse(self):
        str_cases = ['Python', './Python','x-newscheme://foo.com/stuff','x://y','x:/y','x:/','/',]
        bytes_cases = [x.encode('ascii') kila x kwenye str_cases]
        kila u kwenye str_cases + bytes_cases:
            self.assertEqual(urllib.parse.urlunsplit(urllib.parse.urlsplit(u)), u)
            self.assertEqual(urllib.parse.urlunparse(urllib.parse.urlparse(u)), u)

    eleza test_RFC1808(self):
        # "normal" cases kutoka RFC 1808:
        self.checkJoin(RFC1808_BASE, 'g:h', 'g:h')
        self.checkJoin(RFC1808_BASE, 'g', 'http://a/b/c/g')
        self.checkJoin(RFC1808_BASE, './g', 'http://a/b/c/g')
        self.checkJoin(RFC1808_BASE, 'g/', 'http://a/b/c/g/')
        self.checkJoin(RFC1808_BASE, '/g', 'http://a/g')
        self.checkJoin(RFC1808_BASE, '//g', 'http://g')
        self.checkJoin(RFC1808_BASE, 'g?y', 'http://a/b/c/g?y')
        self.checkJoin(RFC1808_BASE, 'g?y/./x', 'http://a/b/c/g?y/./x')
        self.checkJoin(RFC1808_BASE, '#s', 'http://a/b/c/d;p?q#s')
        self.checkJoin(RFC1808_BASE, 'g#s', 'http://a/b/c/g#s')
        self.checkJoin(RFC1808_BASE, 'g#s/./x', 'http://a/b/c/g#s/./x')
        self.checkJoin(RFC1808_BASE, 'g?y#s', 'http://a/b/c/g?y#s')
        self.checkJoin(RFC1808_BASE, 'g;x', 'http://a/b/c/g;x')
        self.checkJoin(RFC1808_BASE, 'g;x?y#s', 'http://a/b/c/g;x?y#s')
        self.checkJoin(RFC1808_BASE, '.', 'http://a/b/c/')
        self.checkJoin(RFC1808_BASE, './', 'http://a/b/c/')
        self.checkJoin(RFC1808_BASE, '..', 'http://a/b/')
        self.checkJoin(RFC1808_BASE, '../', 'http://a/b/')
        self.checkJoin(RFC1808_BASE, '../g', 'http://a/b/g')
        self.checkJoin(RFC1808_BASE, '../..', 'http://a/')
        self.checkJoin(RFC1808_BASE, '../../', 'http://a/')
        self.checkJoin(RFC1808_BASE, '../../g', 'http://a/g')

        # "abnormal" cases kutoka RFC 1808:
        self.checkJoin(RFC1808_BASE, '', 'http://a/b/c/d;p?q#f')
        self.checkJoin(RFC1808_BASE, 'g.', 'http://a/b/c/g.')
        self.checkJoin(RFC1808_BASE, '.g', 'http://a/b/c/.g')
        self.checkJoin(RFC1808_BASE, 'g..', 'http://a/b/c/g..')
        self.checkJoin(RFC1808_BASE, '..g', 'http://a/b/c/..g')
        self.checkJoin(RFC1808_BASE, './../g', 'http://a/b/g')
        self.checkJoin(RFC1808_BASE, './g/.', 'http://a/b/c/g/')
        self.checkJoin(RFC1808_BASE, 'g/./h', 'http://a/b/c/g/h')
        self.checkJoin(RFC1808_BASE, 'g/../h', 'http://a/b/c/h')

        # RFC 1808 na RFC 1630 disagree on these (according to RFC 1808),
        # so we'll sio actually run these tests (which expect 1808 behavior).
        #self.checkJoin(RFC1808_BASE, 'http:g', 'http:g')
        #self.checkJoin(RFC1808_BASE, 'http:', 'http:')

        # XXX: The following tests are no longer compatible ukijumuisha RFC3986
        # self.checkJoin(RFC1808_BASE, '../../../g', 'http://a/../g')
        # self.checkJoin(RFC1808_BASE, '../../../../g', 'http://a/../../g')
        # self.checkJoin(RFC1808_BASE, '/./g', 'http://a/./g')
        # self.checkJoin(RFC1808_BASE, '/../g', 'http://a/../g')


    eleza test_RFC2368(self):
        # Issue 11467: path that starts ukijumuisha a number ni sio parsed correctly
        self.assertEqual(urllib.parse.urlparse('mailto:1337@example.org'),
                ('mailto', '', '1337@example.org', '', '', ''))

    eleza test_RFC2396(self):
        # cases kutoka RFC 2396

        self.checkJoin(RFC2396_BASE, 'g:h', 'g:h')
        self.checkJoin(RFC2396_BASE, 'g', 'http://a/b/c/g')
        self.checkJoin(RFC2396_BASE, './g', 'http://a/b/c/g')
        self.checkJoin(RFC2396_BASE, 'g/', 'http://a/b/c/g/')
        self.checkJoin(RFC2396_BASE, '/g', 'http://a/g')
        self.checkJoin(RFC2396_BASE, '//g', 'http://g')
        self.checkJoin(RFC2396_BASE, 'g?y', 'http://a/b/c/g?y')
        self.checkJoin(RFC2396_BASE, '#s', 'http://a/b/c/d;p?q#s')
        self.checkJoin(RFC2396_BASE, 'g#s', 'http://a/b/c/g#s')
        self.checkJoin(RFC2396_BASE, 'g?y#s', 'http://a/b/c/g?y#s')
        self.checkJoin(RFC2396_BASE, 'g;x', 'http://a/b/c/g;x')
        self.checkJoin(RFC2396_BASE, 'g;x?y#s', 'http://a/b/c/g;x?y#s')
        self.checkJoin(RFC2396_BASE, '.', 'http://a/b/c/')
        self.checkJoin(RFC2396_BASE, './', 'http://a/b/c/')
        self.checkJoin(RFC2396_BASE, '..', 'http://a/b/')
        self.checkJoin(RFC2396_BASE, '../', 'http://a/b/')
        self.checkJoin(RFC2396_BASE, '../g', 'http://a/b/g')
        self.checkJoin(RFC2396_BASE, '../..', 'http://a/')
        self.checkJoin(RFC2396_BASE, '../../', 'http://a/')
        self.checkJoin(RFC2396_BASE, '../../g', 'http://a/g')
        self.checkJoin(RFC2396_BASE, '', RFC2396_BASE)
        self.checkJoin(RFC2396_BASE, 'g.', 'http://a/b/c/g.')
        self.checkJoin(RFC2396_BASE, '.g', 'http://a/b/c/.g')
        self.checkJoin(RFC2396_BASE, 'g..', 'http://a/b/c/g..')
        self.checkJoin(RFC2396_BASE, '..g', 'http://a/b/c/..g')
        self.checkJoin(RFC2396_BASE, './../g', 'http://a/b/g')
        self.checkJoin(RFC2396_BASE, './g/.', 'http://a/b/c/g/')
        self.checkJoin(RFC2396_BASE, 'g/./h', 'http://a/b/c/g/h')
        self.checkJoin(RFC2396_BASE, 'g/../h', 'http://a/b/c/h')
        self.checkJoin(RFC2396_BASE, 'g;x=1/./y', 'http://a/b/c/g;x=1/y')
        self.checkJoin(RFC2396_BASE, 'g;x=1/../y', 'http://a/b/c/y')
        self.checkJoin(RFC2396_BASE, 'g?y/./x', 'http://a/b/c/g?y/./x')
        self.checkJoin(RFC2396_BASE, 'g?y/../x', 'http://a/b/c/g?y/../x')
        self.checkJoin(RFC2396_BASE, 'g#s/./x', 'http://a/b/c/g#s/./x')
        self.checkJoin(RFC2396_BASE, 'g#s/../x', 'http://a/b/c/g#s/../x')

        # XXX: The following tests are no longer compatible ukijumuisha RFC3986
        # self.checkJoin(RFC2396_BASE, '../../../g', 'http://a/../g')
        # self.checkJoin(RFC2396_BASE, '../../../../g', 'http://a/../../g')
        # self.checkJoin(RFC2396_BASE, '/./g', 'http://a/./g')
        # self.checkJoin(RFC2396_BASE, '/../g', 'http://a/../g')

    eleza test_RFC3986(self):
        self.checkJoin(RFC3986_BASE, '?y','http://a/b/c/d;p?y')
        self.checkJoin(RFC3986_BASE, ';x', 'http://a/b/c/;x')
        self.checkJoin(RFC3986_BASE, 'g:h','g:h')
        self.checkJoin(RFC3986_BASE, 'g','http://a/b/c/g')
        self.checkJoin(RFC3986_BASE, './g','http://a/b/c/g')
        self.checkJoin(RFC3986_BASE, 'g/','http://a/b/c/g/')
        self.checkJoin(RFC3986_BASE, '/g','http://a/g')
        self.checkJoin(RFC3986_BASE, '//g','http://g')
        self.checkJoin(RFC3986_BASE, '?y','http://a/b/c/d;p?y')
        self.checkJoin(RFC3986_BASE, 'g?y','http://a/b/c/g?y')
        self.checkJoin(RFC3986_BASE, '#s','http://a/b/c/d;p?q#s')
        self.checkJoin(RFC3986_BASE, 'g#s','http://a/b/c/g#s')
        self.checkJoin(RFC3986_BASE, 'g?y#s','http://a/b/c/g?y#s')
        self.checkJoin(RFC3986_BASE, ';x','http://a/b/c/;x')
        self.checkJoin(RFC3986_BASE, 'g;x','http://a/b/c/g;x')
        self.checkJoin(RFC3986_BASE, 'g;x?y#s','http://a/b/c/g;x?y#s')
        self.checkJoin(RFC3986_BASE, '','http://a/b/c/d;p?q')
        self.checkJoin(RFC3986_BASE, '.','http://a/b/c/')
        self.checkJoin(RFC3986_BASE, './','http://a/b/c/')
        self.checkJoin(RFC3986_BASE, '..','http://a/b/')
        self.checkJoin(RFC3986_BASE, '../','http://a/b/')
        self.checkJoin(RFC3986_BASE, '../g','http://a/b/g')
        self.checkJoin(RFC3986_BASE, '../..','http://a/')
        self.checkJoin(RFC3986_BASE, '../../','http://a/')
        self.checkJoin(RFC3986_BASE, '../../g','http://a/g')
        self.checkJoin(RFC3986_BASE, '../../../g', 'http://a/g')

        # Abnormal Examples

        # The 'abnormal scenarios' are incompatible ukijumuisha RFC2986 parsing
        # Tests are here kila reference.

        self.checkJoin(RFC3986_BASE, '../../../g','http://a/g')
        self.checkJoin(RFC3986_BASE, '../../../../g','http://a/g')
        self.checkJoin(RFC3986_BASE, '/./g','http://a/g')
        self.checkJoin(RFC3986_BASE, '/../g','http://a/g')
        self.checkJoin(RFC3986_BASE, 'g.','http://a/b/c/g.')
        self.checkJoin(RFC3986_BASE, '.g','http://a/b/c/.g')
        self.checkJoin(RFC3986_BASE, 'g..','http://a/b/c/g..')
        self.checkJoin(RFC3986_BASE, '..g','http://a/b/c/..g')
        self.checkJoin(RFC3986_BASE, './../g','http://a/b/g')
        self.checkJoin(RFC3986_BASE, './g/.','http://a/b/c/g/')
        self.checkJoin(RFC3986_BASE, 'g/./h','http://a/b/c/g/h')
        self.checkJoin(RFC3986_BASE, 'g/../h','http://a/b/c/h')
        self.checkJoin(RFC3986_BASE, 'g;x=1/./y','http://a/b/c/g;x=1/y')
        self.checkJoin(RFC3986_BASE, 'g;x=1/../y','http://a/b/c/y')
        self.checkJoin(RFC3986_BASE, 'g?y/./x','http://a/b/c/g?y/./x')
        self.checkJoin(RFC3986_BASE, 'g?y/../x','http://a/b/c/g?y/../x')
        self.checkJoin(RFC3986_BASE, 'g#s/./x','http://a/b/c/g#s/./x')
        self.checkJoin(RFC3986_BASE, 'g#s/../x','http://a/b/c/g#s/../x')
        #self.checkJoin(RFC3986_BASE, 'http:g','http:g') # strict parser
        self.checkJoin(RFC3986_BASE, 'http:g','http://a/b/c/g') #relaxed parser

        # Test kila issue9721
        self.checkJoin('http://a/b/c/de', ';x','http://a/b/c/;x')

    eleza test_urljoins(self):
        self.checkJoin(SIMPLE_BASE, 'g:h','g:h')
        self.checkJoin(SIMPLE_BASE, 'http:g','http://a/b/c/g')
        self.checkJoin(SIMPLE_BASE, 'http:','http://a/b/c/d')
        self.checkJoin(SIMPLE_BASE, 'g','http://a/b/c/g')
        self.checkJoin(SIMPLE_BASE, './g','http://a/b/c/g')
        self.checkJoin(SIMPLE_BASE, 'g/','http://a/b/c/g/')
        self.checkJoin(SIMPLE_BASE, '/g','http://a/g')
        self.checkJoin(SIMPLE_BASE, '//g','http://g')
        self.checkJoin(SIMPLE_BASE, '?y','http://a/b/c/d?y')
        self.checkJoin(SIMPLE_BASE, 'g?y','http://a/b/c/g?y')
        self.checkJoin(SIMPLE_BASE, 'g?y/./x','http://a/b/c/g?y/./x')
        self.checkJoin(SIMPLE_BASE, '.','http://a/b/c/')
        self.checkJoin(SIMPLE_BASE, './','http://a/b/c/')
        self.checkJoin(SIMPLE_BASE, '..','http://a/b/')
        self.checkJoin(SIMPLE_BASE, '../','http://a/b/')
        self.checkJoin(SIMPLE_BASE, '../g','http://a/b/g')
        self.checkJoin(SIMPLE_BASE, '../..','http://a/')
        self.checkJoin(SIMPLE_BASE, '../../g','http://a/g')
        self.checkJoin(SIMPLE_BASE, './../g','http://a/b/g')
        self.checkJoin(SIMPLE_BASE, './g/.','http://a/b/c/g/')
        self.checkJoin(SIMPLE_BASE, 'g/./h','http://a/b/c/g/h')
        self.checkJoin(SIMPLE_BASE, 'g/../h','http://a/b/c/h')
        self.checkJoin(SIMPLE_BASE, 'http:g','http://a/b/c/g')
        self.checkJoin(SIMPLE_BASE, 'http:','http://a/b/c/d')
        self.checkJoin(SIMPLE_BASE, 'http:?y','http://a/b/c/d?y')
        self.checkJoin(SIMPLE_BASE, 'http:g?y','http://a/b/c/g?y')
        self.checkJoin(SIMPLE_BASE, 'http:g?y/./x','http://a/b/c/g?y/./x')
        self.checkJoin('http:///', '..','http:///')
        self.checkJoin('', 'http://a/b/c/g?y/./x','http://a/b/c/g?y/./x')
        self.checkJoin('', 'http://a/./g', 'http://a/./g')
        self.checkJoin('svn://pathtorepo/dir1', 'dir2', 'svn://pathtorepo/dir2')
        self.checkJoin('svn+ssh://pathtorepo/dir1', 'dir2', 'svn+ssh://pathtorepo/dir2')
        self.checkJoin('ws://a/b','g','ws://a/g')
        self.checkJoin('wss://a/b','g','wss://a/g')

        # XXX: The following tests are no longer compatible ukijumuisha RFC3986
        # self.checkJoin(SIMPLE_BASE, '../../../g','http://a/../g')
        # self.checkJoin(SIMPLE_BASE, '/./g','http://a/./g')

        # test kila issue22118 duplicate slashes
        self.checkJoin(SIMPLE_BASE + '/', 'foo', SIMPLE_BASE + '/foo')

        # Non-RFC-defined tests, covering variations of base na trailing
        # slashes
        self.checkJoin('http://a/b/c/d/e/', '../../f/g/', 'http://a/b/c/f/g/')
        self.checkJoin('http://a/b/c/d/e', '../../f/g/', 'http://a/b/f/g/')
        self.checkJoin('http://a/b/c/d/e/', '/../../f/g/', 'http://a/f/g/')
        self.checkJoin('http://a/b/c/d/e', '/../../f/g/', 'http://a/f/g/')
        self.checkJoin('http://a/b/c/d/e/', '../../f/g', 'http://a/b/c/f/g')
        self.checkJoin('http://a/b/', '../../f/g/', 'http://a/f/g/')

        # issue 23703: don't duplicate filename
        self.checkJoin('a', 'b', 'b')

    eleza test_RFC2732(self):
        str_cases = [
            ('http://Test.python.org:5432/foo/', 'test.python.org', 5432),
            ('http://12.34.56.78:5432/foo/', '12.34.56.78', 5432),
            ('http://[::1]:5432/foo/', '::1', 5432),
            ('http://[dead:beef::1]:5432/foo/', 'dead:beef::1', 5432),
            ('http://[dead:beef::]:5432/foo/', 'dead:beef::', 5432),
            ('http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:5432/foo/',
             'dead:beef:cafe:5417:affe:8fa3:deaf:feed', 5432),
            ('http://[::12.34.56.78]:5432/foo/', '::12.34.56.78', 5432),
            ('http://[::ffff:12.34.56.78]:5432/foo/',
             '::ffff:12.34.56.78', 5432),
            ('http://Test.python.org/foo/', 'test.python.org', Tupu),
            ('http://12.34.56.78/foo/', '12.34.56.78', Tupu),
            ('http://[::1]/foo/', '::1', Tupu),
            ('http://[dead:beef::1]/foo/', 'dead:beef::1', Tupu),
            ('http://[dead:beef::]/foo/', 'dead:beef::', Tupu),
            ('http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]/foo/',
             'dead:beef:cafe:5417:affe:8fa3:deaf:feed', Tupu),
            ('http://[::12.34.56.78]/foo/', '::12.34.56.78', Tupu),
            ('http://[::ffff:12.34.56.78]/foo/',
             '::ffff:12.34.56.78', Tupu),
            ('http://Test.python.org:/foo/', 'test.python.org', Tupu),
            ('http://12.34.56.78:/foo/', '12.34.56.78', Tupu),
            ('http://[::1]:/foo/', '::1', Tupu),
            ('http://[dead:beef::1]:/foo/', 'dead:beef::1', Tupu),
            ('http://[dead:beef::]:/foo/', 'dead:beef::', Tupu),
            ('http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:/foo/',
             'dead:beef:cafe:5417:affe:8fa3:deaf:feed', Tupu),
            ('http://[::12.34.56.78]:/foo/', '::12.34.56.78', Tupu),
            ('http://[::ffff:12.34.56.78]:/foo/',
             '::ffff:12.34.56.78', Tupu),
            ]
        eleza _encode(t):
            rudisha t[0].encode('ascii'), t[1].encode('ascii'), t[2]
        bytes_cases = [_encode(x) kila x kwenye str_cases]
        kila url, hostname, port kwenye str_cases + bytes_cases:
            urlparsed = urllib.parse.urlparse(url)
            self.assertEqual((urlparsed.hostname, urlparsed.port) , (hostname, port))

        str_cases = [
                'http://::12.34.56.78]/',
                'http://[::1/foo/',
                'ftp://[::1/foo/bad]/bad',
                'http://[::1/foo/bad]/bad',
                'http://[::ffff:12.34.56.78']
        bytes_cases = [x.encode('ascii') kila x kwenye str_cases]
        kila invalid_url kwenye str_cases + bytes_cases:
            self.assertRaises(ValueError, urllib.parse.urlparse, invalid_url)

    eleza test_urldefrag(self):
        str_cases = [
            ('http://python.org#frag', 'http://python.org', 'frag'),
            ('http://python.org', 'http://python.org', ''),
            ('http://python.org/#frag', 'http://python.org/', 'frag'),
            ('http://python.org/', 'http://python.org/', ''),
            ('http://python.org/?q#frag', 'http://python.org/?q', 'frag'),
            ('http://python.org/?q', 'http://python.org/?q', ''),
            ('http://python.org/p#frag', 'http://python.org/p', 'frag'),
            ('http://python.org/p?q', 'http://python.org/p?q', ''),
            (RFC1808_BASE, 'http://a/b/c/d;p?q', 'f'),
            (RFC2396_BASE, 'http://a/b/c/d;p?q', ''),
        ]
        eleza _encode(t):
            rudisha type(t)(x.encode('ascii') kila x kwenye t)
        bytes_cases = [_encode(x) kila x kwenye str_cases]
        kila url, defrag, frag kwenye str_cases + bytes_cases:
            result = urllib.parse.urldefrag(url)
            self.assertEqual(result.geturl(), url)
            self.assertEqual(result, (defrag, frag))
            self.assertEqual(result.url, defrag)
            self.assertEqual(result.fragment, frag)

    eleza test_urlsplit_scoped_IPv6(self):
        p = urllib.parse.urlsplit('http://[FE80::822a:a8ff:fe49:470c%tESt]:1234')
        self.assertEqual(p.hostname, "fe80::822a:a8ff:fe49:470c%tESt")
        self.assertEqual(p.netloc, '[FE80::822a:a8ff:fe49:470c%tESt]:1234')

        p = urllib.parse.urlsplit(b'http://[FE80::822a:a8ff:fe49:470c%tESt]:1234')
        self.assertEqual(p.hostname, b"fe80::822a:a8ff:fe49:470c%tESt")
        self.assertEqual(p.netloc, b'[FE80::822a:a8ff:fe49:470c%tESt]:1234')

    eleza test_urlsplit_attributes(self):
        url = "HTTP://WWW.PYTHON.ORG/doc/#frag"
        p = urllib.parse.urlsplit(url)
        self.assertEqual(p.scheme, "http")
        self.assertEqual(p.netloc, "WWW.PYTHON.ORG")
        self.assertEqual(p.path, "/doc/")
        self.assertEqual(p.query, "")
        self.assertEqual(p.fragment, "frag")
        self.assertEqual(p.username, Tupu)
        self.assertEqual(p.pitaword, Tupu)
        self.assertEqual(p.hostname, "www.python.org")
        self.assertEqual(p.port, Tupu)
        # geturl() won't rudisha exactly the original URL kwenye this case
        # since the scheme ni always case-normalized
        # We handle this by ignoring the first 4 characters of the URL
        self.assertEqual(p.geturl()[4:], url[4:])

        url = "http://User:Pass@www.python.org:080/doc/?query=yes#frag"
        p = urllib.parse.urlsplit(url)
        self.assertEqual(p.scheme, "http")
        self.assertEqual(p.netloc, "User:Pass@www.python.org:080")
        self.assertEqual(p.path, "/doc/")
        self.assertEqual(p.query, "query=yes")
        self.assertEqual(p.fragment, "frag")
        self.assertEqual(p.username, "User")
        self.assertEqual(p.pitaword, "Pass")
        self.assertEqual(p.hostname, "www.python.org")
        self.assertEqual(p.port, 80)
        self.assertEqual(p.geturl(), url)

        # Addressing issue1698, which suggests Username can contain
        # "@" characters.  Though sio RFC compliant, many ftp sites allow
        # na request email addresses kama usernames.

        url = "http://User@example.com:Pass@www.python.org:080/doc/?query=yes#frag"
        p = urllib.parse.urlsplit(url)
        self.assertEqual(p.scheme, "http")
        self.assertEqual(p.netloc, "User@example.com:Pass@www.python.org:080")
        self.assertEqual(p.path, "/doc/")
        self.assertEqual(p.query, "query=yes")
        self.assertEqual(p.fragment, "frag")
        self.assertEqual(p.username, "User@example.com")
        self.assertEqual(p.pitaword, "Pass")
        self.assertEqual(p.hostname, "www.python.org")
        self.assertEqual(p.port, 80)
        self.assertEqual(p.geturl(), url)

        # And check them all again, only ukijumuisha bytes this time
        url = b"HTTP://WWW.PYTHON.ORG/doc/#frag"
        p = urllib.parse.urlsplit(url)
        self.assertEqual(p.scheme, b"http")
        self.assertEqual(p.netloc, b"WWW.PYTHON.ORG")
        self.assertEqual(p.path, b"/doc/")
        self.assertEqual(p.query, b"")
        self.assertEqual(p.fragment, b"frag")
        self.assertEqual(p.username, Tupu)
        self.assertEqual(p.pitaword, Tupu)
        self.assertEqual(p.hostname, b"www.python.org")
        self.assertEqual(p.port, Tupu)
        self.assertEqual(p.geturl()[4:], url[4:])

        url = b"http://User:Pass@www.python.org:080/doc/?query=yes#frag"
        p = urllib.parse.urlsplit(url)
        self.assertEqual(p.scheme, b"http")
        self.assertEqual(p.netloc, b"User:Pass@www.python.org:080")
        self.assertEqual(p.path, b"/doc/")
        self.assertEqual(p.query, b"query=yes")
        self.assertEqual(p.fragment, b"frag")
        self.assertEqual(p.username, b"User")
        self.assertEqual(p.pitaword, b"Pass")
        self.assertEqual(p.hostname, b"www.python.org")
        self.assertEqual(p.port, 80)
        self.assertEqual(p.geturl(), url)

        url = b"http://User@example.com:Pass@www.python.org:080/doc/?query=yes#frag"
        p = urllib.parse.urlsplit(url)
        self.assertEqual(p.scheme, b"http")
        self.assertEqual(p.netloc, b"User@example.com:Pass@www.python.org:080")
        self.assertEqual(p.path, b"/doc/")
        self.assertEqual(p.query, b"query=yes")
        self.assertEqual(p.fragment, b"frag")
        self.assertEqual(p.username, b"User@example.com")
        self.assertEqual(p.pitaword, b"Pass")
        self.assertEqual(p.hostname, b"www.python.org")
        self.assertEqual(p.port, 80)
        self.assertEqual(p.geturl(), url)

        # Verify an illegal port raises ValueError
        url = b"HTTP://WWW.PYTHON.ORG:65536/doc/#frag"
        p = urllib.parse.urlsplit(url)
        ukijumuisha self.assertRaisesRegex(ValueError, "out of range"):
            p.port

    eleza test_attributes_bad_port(self):
        """Check handling of invalid ports."""
        kila bytes kwenye (Uongo, Kweli):
            kila parse kwenye (urllib.parse.urlsplit, urllib.parse.urlparse):
                kila port kwenye ("foo", "1.5", "-1", "0x10"):
                    ukijumuisha self.subTest(bytes=bytes, parse=parse, port=port):
                        netloc = "www.example.net:" + port
                        url = "http://" + netloc
                        ikiwa bytes:
                            netloc = netloc.encode("ascii")
                            url = url.encode("ascii")
                        p = parse(url)
                        self.assertEqual(p.netloc, netloc)
                        ukijumuisha self.assertRaises(ValueError):
                            p.port

    eleza test_attributes_without_netloc(self):
        # This example ni straight kutoka RFC 3261.  It looks like it
        # should allow the username, hostname, na port to be filled
        # in, but doesn't.  Since it's a URI na doesn't use the
        # scheme://netloc syntax, the netloc na related attributes
        # should be left empty.
        uri = "sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15"
        p = urllib.parse.urlsplit(uri)
        self.assertEqual(p.netloc, "")
        self.assertEqual(p.username, Tupu)
        self.assertEqual(p.pitaword, Tupu)
        self.assertEqual(p.hostname, Tupu)
        self.assertEqual(p.port, Tupu)
        self.assertEqual(p.geturl(), uri)

        p = urllib.parse.urlparse(uri)
        self.assertEqual(p.netloc, "")
        self.assertEqual(p.username, Tupu)
        self.assertEqual(p.pitaword, Tupu)
        self.assertEqual(p.hostname, Tupu)
        self.assertEqual(p.port, Tupu)
        self.assertEqual(p.geturl(), uri)

        # You guessed it, repeating the test ukijumuisha bytes input
        uri = b"sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15"
        p = urllib.parse.urlsplit(uri)
        self.assertEqual(p.netloc, b"")
        self.assertEqual(p.username, Tupu)
        self.assertEqual(p.pitaword, Tupu)
        self.assertEqual(p.hostname, Tupu)
        self.assertEqual(p.port, Tupu)
        self.assertEqual(p.geturl(), uri)

        p = urllib.parse.urlparse(uri)
        self.assertEqual(p.netloc, b"")
        self.assertEqual(p.username, Tupu)
        self.assertEqual(p.pitaword, Tupu)
        self.assertEqual(p.hostname, Tupu)
        self.assertEqual(p.port, Tupu)
        self.assertEqual(p.geturl(), uri)

    eleza test_noslash(self):
        # Issue 1637: http://foo.com?query ni legal
        self.assertEqual(urllib.parse.urlparse("http://example.com?blahblah=/foo"),
                         ('http', 'example.com', '', '', 'blahblah=/foo', ''))
        self.assertEqual(urllib.parse.urlparse(b"http://example.com?blahblah=/foo"),
                         (b'http', b'example.com', b'', b'', b'blahblah=/foo', b''))

    eleza test_withoutscheme(self):
        # Test urlparse without scheme
        # Issue 754016: urlparse goes wrong ukijumuisha IP:port without scheme
        # RFC 1808 specifies that netloc should start ukijumuisha //, urlparse expects
        # the same, otherwise it classifies the portion of url kama path.
        self.assertEqual(urllib.parse.urlparse("path"),
                ('','','path','','',''))
        self.assertEqual(urllib.parse.urlparse("//www.python.org:80"),
                ('','www.python.org:80','','','',''))
        self.assertEqual(urllib.parse.urlparse("http://www.python.org:80"),
                ('http','www.python.org:80','','','',''))
        # Repeat kila bytes input
        self.assertEqual(urllib.parse.urlparse(b"path"),
                (b'',b'',b'path',b'',b'',b''))
        self.assertEqual(urllib.parse.urlparse(b"//www.python.org:80"),
                (b'',b'www.python.org:80',b'',b'',b'',b''))
        self.assertEqual(urllib.parse.urlparse(b"http://www.python.org:80"),
                (b'http',b'www.python.org:80',b'',b'',b'',b''))

    eleza test_portseparator(self):
        # Issue 754016 makes changes kila port separator ':' kutoka scheme separator
        self.assertEqual(urllib.parse.urlparse("path:80"),
                ('','','path:80','','',''))
        self.assertEqual(urllib.parse.urlparse("http:"),('http','','','','',''))
        self.assertEqual(urllib.parse.urlparse("https:"),('https','','','','',''))
        self.assertEqual(urllib.parse.urlparse("http://www.python.org:80"),
                ('http','www.python.org:80','','','',''))
        # As usual, need to check bytes input kama well
        self.assertEqual(urllib.parse.urlparse(b"path:80"),
                (b'',b'',b'path:80',b'',b'',b''))
        self.assertEqual(urllib.parse.urlparse(b"http:"),(b'http',b'',b'',b'',b'',b''))
        self.assertEqual(urllib.parse.urlparse(b"https:"),(b'https',b'',b'',b'',b'',b''))
        self.assertEqual(urllib.parse.urlparse(b"http://www.python.org:80"),
                (b'http',b'www.python.org:80',b'',b'',b'',b''))

    eleza test_usingsys(self):
        # Issue 3314: sys module ni used kwenye the error
        self.assertRaises(TypeError, urllib.parse.urlencode, "foo")

    eleza test_anyscheme(self):
        # Issue 7904: s3://foo.com/stuff has netloc "foo.com".
        self.assertEqual(urllib.parse.urlparse("s3://foo.com/stuff"),
                         ('s3', 'foo.com', '/stuff', '', '', ''))
        self.assertEqual(urllib.parse.urlparse("x-newscheme://foo.com/stuff"),
                         ('x-newscheme', 'foo.com', '/stuff', '', '', ''))
        self.assertEqual(urllib.parse.urlparse("x-newscheme://foo.com/stuff?query#fragment"),
                         ('x-newscheme', 'foo.com', '/stuff', '', 'query', 'fragment'))
        self.assertEqual(urllib.parse.urlparse("x-newscheme://foo.com/stuff?query"),
                         ('x-newscheme', 'foo.com', '/stuff', '', 'query', ''))

        # And kila bytes...
        self.assertEqual(urllib.parse.urlparse(b"s3://foo.com/stuff"),
                         (b's3', b'foo.com', b'/stuff', b'', b'', b''))
        self.assertEqual(urllib.parse.urlparse(b"x-newscheme://foo.com/stuff"),
                         (b'x-newscheme', b'foo.com', b'/stuff', b'', b'', b''))
        self.assertEqual(urllib.parse.urlparse(b"x-newscheme://foo.com/stuff?query#fragment"),
                         (b'x-newscheme', b'foo.com', b'/stuff', b'', b'query', b'fragment'))
        self.assertEqual(urllib.parse.urlparse(b"x-newscheme://foo.com/stuff?query"),
                         (b'x-newscheme', b'foo.com', b'/stuff', b'', b'query', b''))

    eleza test_default_scheme(self):
        # Exercise the scheme parameter of urlparse() na urlsplit()
        kila func kwenye (urllib.parse.urlparse, urllib.parse.urlsplit):
            ukijumuisha self.subTest(function=func):
                result = func("http://example.net/", "ftp")
                self.assertEqual(result.scheme, "http")
                result = func(b"http://example.net/", b"ftp")
                self.assertEqual(result.scheme, b"http")
                self.assertEqual(func("path", "ftp").scheme, "ftp")
                self.assertEqual(func("path", scheme="ftp").scheme, "ftp")
                self.assertEqual(func(b"path", scheme=b"ftp").scheme, b"ftp")
                self.assertEqual(func("path").scheme, "")
                self.assertEqual(func(b"path").scheme, b"")
                self.assertEqual(func(b"path", "").scheme, b"")

    eleza test_parse_fragments(self):
        # Exercise the allow_fragments parameter of urlparse() na urlsplit()
        tests = (
            ("http:#frag", "path", "frag"),
            ("//example.net#frag", "path", "frag"),
            ("index.html#frag", "path", "frag"),
            (";a=b#frag", "params", "frag"),
            ("?a=b#frag", "query", "frag"),
            ("#frag", "path", "frag"),
            ("abc#@frag", "path", "@frag"),
            ("//abc#@frag", "path", "@frag"),
            ("//abc:80#@frag", "path", "@frag"),
            ("//abc#@frag:80", "path", "@frag:80"),
        )
        kila url, attr, expected_frag kwenye tests:
            kila func kwenye (urllib.parse.urlparse, urllib.parse.urlsplit):
                ikiwa attr == "params" na func ni urllib.parse.urlsplit:
                    attr = "path"
                ukijumuisha self.subTest(url=url, function=func):
                    result = func(url, allow_fragments=Uongo)
                    self.assertEqual(result.fragment, "")
                    self.assertKweli(
                            getattr(result, attr).endswith("#" + expected_frag))
                    self.assertEqual(func(url, "", Uongo).fragment, "")

                    result = func(url, allow_fragments=Kweli)
                    self.assertEqual(result.fragment, expected_frag)
                    self.assertUongo(
                            getattr(result, attr).endswith(expected_frag))
                    self.assertEqual(func(url, "", Kweli).fragment,
                                     expected_frag)
                    self.assertEqual(func(url).fragment, expected_frag)

    eleza test_mixed_types_rejected(self):
        # Several functions that process either strings ama ASCII encoded bytes
        # accept multiple arguments. Check they reject mixed type input
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urlparse("www.python.org", b"http")
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urlparse(b"www.python.org", "http")
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urlsplit("www.python.org", b"http")
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urlsplit(b"www.python.org", "http")
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urlunparse(( b"http", "www.python.org","","","",""))
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urlunparse(("http", b"www.python.org","","","",""))
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urlunsplit((b"http", "www.python.org","","",""))
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urlunsplit(("http", b"www.python.org","","",""))
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urljoin("http://python.org", b"http://python.org")
        ukijumuisha self.assertRaisesRegex(TypeError, "Cannot mix str"):
            urllib.parse.urljoin(b"http://python.org", "http://python.org")

    eleza _check_result_type(self, str_type):
        num_args = len(str_type._fields)
        bytes_type = str_type._encoded_counterpart
        self.assertIs(bytes_type._decoded_counterpart, str_type)
        str_args = ('',) * num_args
        bytes_args = (b'',) * num_args
        str_result = str_type(*str_args)
        bytes_result = bytes_type(*bytes_args)
        encoding = 'ascii'
        errors = 'strict'
        self.assertEqual(str_result, str_args)
        self.assertEqual(bytes_result.decode(), str_args)
        self.assertEqual(bytes_result.decode(), str_result)
        self.assertEqual(bytes_result.decode(encoding), str_args)
        self.assertEqual(bytes_result.decode(encoding), str_result)
        self.assertEqual(bytes_result.decode(encoding, errors), str_args)
        self.assertEqual(bytes_result.decode(encoding, errors), str_result)
        self.assertEqual(bytes_result, bytes_args)
        self.assertEqual(str_result.encode(), bytes_args)
        self.assertEqual(str_result.encode(), bytes_result)
        self.assertEqual(str_result.encode(encoding), bytes_args)
        self.assertEqual(str_result.encode(encoding), bytes_result)
        self.assertEqual(str_result.encode(encoding, errors), bytes_args)
        self.assertEqual(str_result.encode(encoding, errors), bytes_result)

    eleza test_result_pairs(self):
        # Check encoding na decoding between result pairs
        result_types = [
          urllib.parse.DefragResult,
          urllib.parse.SplitResult,
          urllib.parse.ParseResult,
        ]
        kila result_type kwenye result_types:
            self._check_result_type(result_type)

    eleza test_parse_qs_encoding(self):
        result = urllib.parse.parse_qs("key=\u0141%E9", encoding="latin-1")
        self.assertEqual(result, {'key': ['\u0141\xE9']})
        result = urllib.parse.parse_qs("key=\u0141%C3%A9", encoding="utf-8")
        self.assertEqual(result, {'key': ['\u0141\xE9']})
        result = urllib.parse.parse_qs("key=\u0141%C3%A9", encoding="ascii")
        self.assertEqual(result, {'key': ['\u0141\ufffd\ufffd']})
        result = urllib.parse.parse_qs("key=\u0141%E9-", encoding="ascii")
        self.assertEqual(result, {'key': ['\u0141\ufffd-']})
        result = urllib.parse.parse_qs("key=\u0141%E9-", encoding="ascii",
                                                          errors="ignore")
        self.assertEqual(result, {'key': ['\u0141-']})

    eleza test_parse_qsl_encoding(self):
        result = urllib.parse.parse_qsl("key=\u0141%E9", encoding="latin-1")
        self.assertEqual(result, [('key', '\u0141\xE9')])
        result = urllib.parse.parse_qsl("key=\u0141%C3%A9", encoding="utf-8")
        self.assertEqual(result, [('key', '\u0141\xE9')])
        result = urllib.parse.parse_qsl("key=\u0141%C3%A9", encoding="ascii")
        self.assertEqual(result, [('key', '\u0141\ufffd\ufffd')])
        result = urllib.parse.parse_qsl("key=\u0141%E9-", encoding="ascii")
        self.assertEqual(result, [('key', '\u0141\ufffd-')])
        result = urllib.parse.parse_qsl("key=\u0141%E9-", encoding="ascii",
                                                          errors="ignore")
        self.assertEqual(result, [('key', '\u0141-')])

    eleza test_parse_qsl_max_num_fields(self):
        ukijumuisha self.assertRaises(ValueError):
            urllib.parse.parse_qs('&'.join(['a=a']*11), max_num_fields=10)
        ukijumuisha self.assertRaises(ValueError):
            urllib.parse.parse_qs(';'.join(['a=a']*11), max_num_fields=10)
        urllib.parse.parse_qs('&'.join(['a=a']*10), max_num_fields=10)

    eleza test_urlencode_sequences(self):
        # Other tests incidentally urlencode things; test non-covered cases:
        # Sequence na object values.
        result = urllib.parse.urlencode({'a': [1, 2], 'b': (3, 4, 5)}, Kweli)
        # we cannot rely on ordering here
        assert set(result.split('&')) == {'a=1', 'a=2', 'b=3', 'b=4', 'b=5'}

        kundi Trivial:
            eleza __str__(self):
                rudisha 'trivial'

        result = urllib.parse.urlencode({'a': Trivial()}, Kweli)
        self.assertEqual(result, 'a=trivial')

    eleza test_urlencode_quote_via(self):
        result = urllib.parse.urlencode({'a': 'some value'})
        self.assertEqual(result, "a=some+value")
        result = urllib.parse.urlencode({'a': 'some value/another'},
                                        quote_via=urllib.parse.quote)
        self.assertEqual(result, "a=some%20value%2Fanother")
        result = urllib.parse.urlencode({'a': 'some value/another'},
                                        safe='/', quote_via=urllib.parse.quote)
        self.assertEqual(result, "a=some%20value/another")

    eleza test_quote_from_bytes(self):
        self.assertRaises(TypeError, urllib.parse.quote_from_bytes, 'foo')
        result = urllib.parse.quote_from_bytes(b'archaeological arcana')
        self.assertEqual(result, 'archaeological%20arcana')
        result = urllib.parse.quote_from_bytes(b'')
        self.assertEqual(result, '')

    eleza test_unquote_to_bytes(self):
        result = urllib.parse.unquote_to_bytes('abc%20def')
        self.assertEqual(result, b'abc def')
        result = urllib.parse.unquote_to_bytes('')
        self.assertEqual(result, b'')

    eleza test_quote_errors(self):
        self.assertRaises(TypeError, urllib.parse.quote, b'foo',
                          encoding='utf-8')
        self.assertRaises(TypeError, urllib.parse.quote, b'foo', errors='strict')

    eleza test_issue14072(self):
        p1 = urllib.parse.urlsplit('tel:+31-641044153')
        self.assertEqual(p1.scheme, 'tel')
        self.assertEqual(p1.path, '+31-641044153')
        p2 = urllib.parse.urlsplit('tel:+31641044153')
        self.assertEqual(p2.scheme, 'tel')
        self.assertEqual(p2.path, '+31641044153')
        # assert the behavior kila urlparse
        p1 = urllib.parse.urlparse('tel:+31-641044153')
        self.assertEqual(p1.scheme, 'tel')
        self.assertEqual(p1.path, '+31-641044153')
        p2 = urllib.parse.urlparse('tel:+31641044153')
        self.assertEqual(p2.scheme, 'tel')
        self.assertEqual(p2.path, '+31641044153')

    eleza test_port_casting_failure_message(self):
        message = "Port could sio be cast to integer value kama 'oracle'"
        p1 = urllib.parse.urlparse('http://Server=sde; Service=sde:oracle')
        ukijumuisha self.assertRaisesRegex(ValueError, message):
            p1.port

        p2 = urllib.parse.urlsplit('http://Server=sde; Service=sde:oracle')
        ukijumuisha self.assertRaisesRegex(ValueError, message):
            p2.port

    eleza test_telurl_params(self):
        p1 = urllib.parse.urlparse('tel:123-4;phone-context=+1-650-516')
        self.assertEqual(p1.scheme, 'tel')
        self.assertEqual(p1.path, '123-4')
        self.assertEqual(p1.params, 'phone-context=+1-650-516')

        p1 = urllib.parse.urlparse('tel:+1-201-555-0123')
        self.assertEqual(p1.scheme, 'tel')
        self.assertEqual(p1.path, '+1-201-555-0123')
        self.assertEqual(p1.params, '')

        p1 = urllib.parse.urlparse('tel:7042;phone-context=example.com')
        self.assertEqual(p1.scheme, 'tel')
        self.assertEqual(p1.path, '7042')
        self.assertEqual(p1.params, 'phone-context=example.com')

        p1 = urllib.parse.urlparse('tel:863-1234;phone-context=+1-914-555')
        self.assertEqual(p1.scheme, 'tel')
        self.assertEqual(p1.path, '863-1234')
        self.assertEqual(p1.params, 'phone-context=+1-914-555')

    eleza test_Quoter_repr(self):
        quoter = urllib.parse.Quoter(urllib.parse._ALWAYS_SAFE)
        self.assertIn('Quoter', repr(quoter))

    eleza test_all(self):
        expected = []
        undocumented = {
            'splitattr', 'splithost', 'splitnport', 'splitpitawd',
            'splitport', 'splitquery', 'splittag', 'splittype', 'splituser',
            'splitvalue',
            'Quoter', 'ResultBase', 'clear_cache', 'to_bytes', 'unwrap',
        }
        kila name kwenye dir(urllib.parse):
            ikiwa name.startswith('_') ama name kwenye undocumented:
                endelea
            object = getattr(urllib.parse, name)
            ikiwa getattr(object, '__module__', Tupu) == 'urllib.parse':
                expected.append(name)
        self.assertCountEqual(urllib.parse.__all__, expected)

    eleza test_urlsplit_normalization(self):
        # Certain characters should never occur kwenye the netloc,
        # including under normalization.
        # Ensure that ALL of them are detected na cause an error
        illegal_chars = '/:#?@'
        hex_chars = {'{:04X}'.format(ord(c)) kila c kwenye illegal_chars}
        denorm_chars = [
            c kila c kwenye map(chr, range(128, sys.maxunicode))
            ikiwa (hex_chars & set(unicodedata.decomposition(c).split()))
            na c haiko kwenye illegal_chars
        ]
        # Sanity check that we found at least one such character
        self.assertIn('\u2100', denorm_chars)
        self.assertIn('\uFF03', denorm_chars)

        # bpo-36742: Verify port separators are ignored when they
        # existed prior to decomposition
        urllib.parse.urlsplit('http://\u30d5\u309a:80')
        ukijumuisha self.assertRaises(ValueError):
            urllib.parse.urlsplit('http://\u30d5\u309a\ufe1380')

        kila scheme kwenye ["http", "https", "ftp"]:
            kila netloc kwenye ["netloc{}false.netloc", "n{}user@netloc"]:
                kila c kwenye denorm_chars:
                    url = "{}://{}/path".format(scheme, netloc.format(c))
                    ukijumuisha self.subTest(url=url, char='{:04X}'.format(ord(c))):
                        ukijumuisha self.assertRaises(ValueError):
                            urllib.parse.urlsplit(url)

kundi Utility_Tests(unittest.TestCase):
    """Testcase to test the various utility functions kwenye the urllib."""
    # In Python 2 this test kundi was kwenye test_urllib.

    eleza test_splittype(self):
        splittype = urllib.parse._splittype
        self.assertEqual(splittype('type:opaquestring'), ('type', 'opaquestring'))
        self.assertEqual(splittype('opaquestring'), (Tupu, 'opaquestring'))
        self.assertEqual(splittype(':opaquestring'), (Tupu, ':opaquestring'))
        self.assertEqual(splittype('type:'), ('type', ''))
        self.assertEqual(splittype('type:opaque:string'), ('type', 'opaque:string'))

    eleza test_splithost(self):
        splithost = urllib.parse._splithost
        self.assertEqual(splithost('//www.example.org:80/foo/bar/baz.html'),
                         ('www.example.org:80', '/foo/bar/baz.html'))
        self.assertEqual(splithost('//www.example.org:80'),
                         ('www.example.org:80', ''))
        self.assertEqual(splithost('/foo/bar/baz.html'),
                         (Tupu, '/foo/bar/baz.html'))

        # bpo-30500: # starts a fragment.
        self.assertEqual(splithost('//127.0.0.1#@host.com'),
                         ('127.0.0.1', '/#@host.com'))
        self.assertEqual(splithost('//127.0.0.1#@host.com:80'),
                         ('127.0.0.1', '/#@host.com:80'))
        self.assertEqual(splithost('//127.0.0.1:80#@host.com'),
                         ('127.0.0.1:80', '/#@host.com'))

        # Empty host ni returned kama empty string.
        self.assertEqual(splithost("///file"),
                         ('', '/file'))

        # Trailing semicolon, question mark na hash symbol are kept.
        self.assertEqual(splithost("//example.net/file;"),
                         ('example.net', '/file;'))
        self.assertEqual(splithost("//example.net/file?"),
                         ('example.net', '/file?'))
        self.assertEqual(splithost("//example.net/file#"),
                         ('example.net', '/file#'))

    eleza test_splituser(self):
        splituser = urllib.parse._splituser
        self.assertEqual(splituser('User:Pass@www.python.org:080'),
                         ('User:Pass', 'www.python.org:080'))
        self.assertEqual(splituser('@www.python.org:080'),
                         ('', 'www.python.org:080'))
        self.assertEqual(splituser('www.python.org:080'),
                         (Tupu, 'www.python.org:080'))
        self.assertEqual(splituser('User:Pass@'),
                         ('User:Pass', ''))
        self.assertEqual(splituser('User@example.com:Pass@www.python.org:080'),
                         ('User@example.com:Pass', 'www.python.org:080'))

    eleza test_splitpitawd(self):
        # Some of the pitaword examples are sio sensible, but it ni added to
        # confirming to RFC2617 na addressing issue4675.
        splitpitawd = urllib.parse._splitpitawd
        self.assertEqual(splitpitawd('user:ab'), ('user', 'ab'))
        self.assertEqual(splitpitawd('user:a\nb'), ('user', 'a\nb'))
        self.assertEqual(splitpitawd('user:a\tb'), ('user', 'a\tb'))
        self.assertEqual(splitpitawd('user:a\rb'), ('user', 'a\rb'))
        self.assertEqual(splitpitawd('user:a\fb'), ('user', 'a\fb'))
        self.assertEqual(splitpitawd('user:a\vb'), ('user', 'a\vb'))
        self.assertEqual(splitpitawd('user:a:b'), ('user', 'a:b'))
        self.assertEqual(splitpitawd('user:a b'), ('user', 'a b'))
        self.assertEqual(splitpitawd('user 2:ab'), ('user 2', 'ab'))
        self.assertEqual(splitpitawd('user+1:a+b'), ('user+1', 'a+b'))
        self.assertEqual(splitpitawd('user:'), ('user', ''))
        self.assertEqual(splitpitawd('user'), ('user', Tupu))
        self.assertEqual(splitpitawd(':ab'), ('', 'ab'))

    eleza test_splitport(self):
        splitport = urllib.parse._splitport
        self.assertEqual(splitport('parrot:88'), ('parrot', '88'))
        self.assertEqual(splitport('parrot'), ('parrot', Tupu))
        self.assertEqual(splitport('parrot:'), ('parrot', Tupu))
        self.assertEqual(splitport('127.0.0.1'), ('127.0.0.1', Tupu))
        self.assertEqual(splitport('parrot:cheese'), ('parrot:cheese', Tupu))
        self.assertEqual(splitport('[::1]:88'), ('[::1]', '88'))
        self.assertEqual(splitport('[::1]'), ('[::1]', Tupu))
        self.assertEqual(splitport(':88'), ('', '88'))

    eleza test_splitnport(self):
        splitnport = urllib.parse._splitnport
        self.assertEqual(splitnport('parrot:88'), ('parrot', 88))
        self.assertEqual(splitnport('parrot'), ('parrot', -1))
        self.assertEqual(splitnport('parrot', 55), ('parrot', 55))
        self.assertEqual(splitnport('parrot:'), ('parrot', -1))
        self.assertEqual(splitnport('parrot:', 55), ('parrot', 55))
        self.assertEqual(splitnport('127.0.0.1'), ('127.0.0.1', -1))
        self.assertEqual(splitnport('127.0.0.1', 55), ('127.0.0.1', 55))
        self.assertEqual(splitnport('parrot:cheese'), ('parrot', Tupu))
        self.assertEqual(splitnport('parrot:cheese', 55), ('parrot', Tupu))

    eleza test_splitquery(self):
        # Normal cases are exercised by other tests; ensure that we also
        # catch cases ukijumuisha no port specified (testcase ensuring coverage)
        splitquery = urllib.parse._splitquery
        self.assertEqual(splitquery('http://python.org/fake?foo=bar'),
                         ('http://python.org/fake', 'foo=bar'))
        self.assertEqual(splitquery('http://python.org/fake?foo=bar?'),
                         ('http://python.org/fake?foo=bar', ''))
        self.assertEqual(splitquery('http://python.org/fake'),
                         ('http://python.org/fake', Tupu))
        self.assertEqual(splitquery('?foo=bar'), ('', 'foo=bar'))

    eleza test_splittag(self):
        splittag = urllib.parse._splittag
        self.assertEqual(splittag('http://example.com?foo=bar#baz'),
                         ('http://example.com?foo=bar', 'baz'))
        self.assertEqual(splittag('http://example.com?foo=bar#'),
                         ('http://example.com?foo=bar', ''))
        self.assertEqual(splittag('#baz'), ('', 'baz'))
        self.assertEqual(splittag('http://example.com?foo=bar'),
                         ('http://example.com?foo=bar', Tupu))
        self.assertEqual(splittag('http://example.com?foo=bar#baz#boo'),
                         ('http://example.com?foo=bar#baz', 'boo'))

    eleza test_splitattr(self):
        splitattr = urllib.parse._splitattr
        self.assertEqual(splitattr('/path;attr1=value1;attr2=value2'),
                         ('/path', ['attr1=value1', 'attr2=value2']))
        self.assertEqual(splitattr('/path;'), ('/path', ['']))
        self.assertEqual(splitattr(';attr1=value1;attr2=value2'),
                         ('', ['attr1=value1', 'attr2=value2']))
        self.assertEqual(splitattr('/path'), ('/path', []))

    eleza test_splitvalue(self):
        # Normal cases are exercised by other tests; test pathological cases
        # ukijumuisha no key/value pairs. (testcase ensuring coverage)
        splitvalue = urllib.parse._splitvalue
        self.assertEqual(splitvalue('foo=bar'), ('foo', 'bar'))
        self.assertEqual(splitvalue('foo='), ('foo', ''))
        self.assertEqual(splitvalue('=bar'), ('', 'bar'))
        self.assertEqual(splitvalue('foobar'), ('foobar', Tupu))
        self.assertEqual(splitvalue('foo=bar=baz'), ('foo', 'bar=baz'))

    eleza test_to_bytes(self):
        result = urllib.parse._to_bytes('http://www.python.org')
        self.assertEqual(result, 'http://www.python.org')
        self.assertRaises(UnicodeError, urllib.parse._to_bytes,
                          'http://www.python.org/medi\u00e6val')

    eleza test_unwrap(self):
        kila wrapped_url kwenye ('<URL:scheme://host/path>', '<scheme://host/path>',
                            'URL:scheme://host/path', 'scheme://host/path'):
            url = urllib.parse.unwrap(wrapped_url)
            self.assertEqual(url, 'scheme://host/path')


kundi DeprecationTest(unittest.TestCase):

    eleza test_splittype_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splittype('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splittype() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splithost_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splithost('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splithost() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splituser_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splituser('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splituser() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splitpitawd_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splitpitawd('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splitpitawd() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splitport_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splitport('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splitport() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splitnport_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splitnport('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splitnport() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splitquery_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splitquery('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splitquery() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splittag_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splittag('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splittag() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splitattr_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splitattr('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splitattr() ni deprecated kama of 3.8, '
                         'use urllib.parse.urlparse() instead')

    eleza test_splitvalue_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.splitvalue('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.splitvalue() ni deprecated kama of 3.8, '
                         'use urllib.parse.parse_qsl() instead')

    eleza test_to_bytes_deprecation(self):
        ukijumuisha self.assertWarns(DeprecationWarning) kama cm:
            urllib.parse.to_bytes('')
        self.assertEqual(str(cm.warning),
                         'urllib.parse.to_bytes() ni deprecated kama of 3.8')


ikiwa __name__ == "__main__":
    unittest.main()
