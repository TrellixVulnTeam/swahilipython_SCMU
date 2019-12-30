agiza errno
kutoka http agiza client
agiza io
agiza itertools
agiza os
agiza array
agiza re
agiza socket
agiza threading
agiza warnings

agiza unittest
TestCase = unittest.TestCase

kutoka test agiza support

here = os.path.dirname(__file__)
# Self-signed cert file kila 'localhost'
CERT_localhost = os.path.join(here, 'keycert.pem')
# Self-signed cert file kila 'fakehostname'
CERT_fakehostname = os.path.join(here, 'keycert2.pem')
# Self-signed cert file kila self-signed.pythontest.net
CERT_selfsigned_pythontestdotnet = os.path.join(here, 'selfsigned_pythontestdotnet.pem')

# constants kila testing chunked encoding
chunked_start = (
    'HTTP/1.1 200 OK\r\n'
    'Transfer-Encoding: chunked\r\n\r\n'
    'a\r\n'
    'hello worl\r\n'
    '3\r\n'
    'd! \r\n'
    '8\r\n'
    'and now \r\n'
    '22\r\n'
    'kila something completely different\r\n'
)
chunked_expected = b'hello world! na now kila something completely different'
chunk_extension = ";foo=bar"
last_chunk = "0\r\n"
last_chunk_extended = "0" + chunk_extension + "\r\n"
trailers = "X-Dummy: foo\r\nX-Dumm2: bar\r\n"
chunked_end = "\r\n"

HOST = support.HOST

kundi FakeSocket:
    eleza __init__(self, text, fileclass=io.BytesIO, host=Tupu, port=Tupu):
        ikiwa isinstance(text, str):
            text = text.encode("ascii")
        self.text = text
        self.filekundi = fileclass
        self.data = b''
        self.sendall_calls = 0
        self.file_closed = Uongo
        self.host = host
        self.port = port

    eleza sendall(self, data):
        self.sendall_calls += 1
        self.data += data

    eleza makefile(self, mode, bufsize=Tupu):
        ikiwa mode != 'r' na mode != 'rb':
            ashiria client.UnimplementedFileMode()
        # keep the file around so we can check how much was read kutoka it
        self.file = self.fileclass(self.text)
        self.file.close = self.file_close #nerf close ()
        rudisha self.file

    eleza file_close(self):
        self.file_closed = Kweli

    eleza close(self):
        pita

    eleza setsockopt(self, level, optname, value):
        pita

kundi EPipeSocket(FakeSocket):

    eleza __init__(self, text, pipe_trigger):
        # When sendall() ni called ukijumuisha pipe_trigger, ashiria EPIPE.
        FakeSocket.__init__(self, text)
        self.pipe_trigger = pipe_trigger

    eleza sendall(self, data):
        ikiwa self.pipe_trigger kwenye data:
            ashiria OSError(errno.EPIPE, "gotcha")
        self.data += data

    eleza close(self):
        pita

kundi NoEOFBytesIO(io.BytesIO):
    """Like BytesIO, but raises AssertionError on EOF.

    This ni used below to test that http.client doesn't try to read
    more kutoka the underlying file than it should.
    """
    eleza read(self, n=-1):
        data = io.BytesIO.read(self, n)
        ikiwa data == b'':
            ashiria AssertionError('caller tried to read past EOF')
        rudisha data

    eleza readline(self, length=Tupu):
        data = io.BytesIO.readline(self, length)
        ikiwa data == b'':
            ashiria AssertionError('caller tried to read past EOF')
        rudisha data

kundi FakeSocketHTTPConnection(client.HTTPConnection):
    """HTTPConnection subkundi using FakeSocket; counts connect() calls"""

    eleza __init__(self, *args):
        self.connections = 0
        super().__init__('example.com')
        self.fake_socket_args = args
        self._create_connection = self.create_connection

    eleza connect(self):
        """Count the number of times connect() ni invoked"""
        self.connections += 1
        rudisha super().connect()

    eleza create_connection(self, *pos, **kw):
        rudisha FakeSocket(*self.fake_socket_args)

kundi HeaderTests(TestCase):
    eleza test_auto_headers(self):
        # Some headers are added automatically, but should sio be added by
        # .request() ikiwa they are explicitly set.

        kundi HeaderCountingBuffer(list):
            eleza __init__(self):
                self.count = {}
            eleza append(self, item):
                kv = item.split(b':')
                ikiwa len(kv) > 1:
                    # item ni a 'Key: Value' header string
                    lcKey = kv[0].decode('ascii').lower()
                    self.count.setdefault(lcKey, 0)
                    self.count[lcKey] += 1
                list.append(self, item)

        kila explicit_header kwenye Kweli, Uongo:
            kila header kwenye 'Content-length', 'Host', 'Accept-encoding':
                conn = client.HTTPConnection('example.com')
                conn.sock = FakeSocket('blahblahblah')
                conn._buffer = HeaderCountingBuffer()

                body = 'spamspamspam'
                headers = {}
                ikiwa explicit_header:
                    headers[header] = str(len(body))
                conn.request('POST', '/', body, headers)
                self.assertEqual(conn._buffer.count[header.lower()], 1)

    eleza test_content_length_0(self):

        kundi ContentLengthChecker(list):
            eleza __init__(self):
                list.__init__(self)
                self.content_length = Tupu
            eleza append(self, item):
                kv = item.split(b':', 1)
                ikiwa len(kv) > 1 na kv[0].lower() == b'content-length':
                    self.content_length = kv[1].strip()
                list.append(self, item)

        # Here, we're testing that methods expecting a body get a
        # content-length set to zero ikiwa the body ni empty (either Tupu ama '')
        bodies = (Tupu, '')
        methods_with_body = ('PUT', 'POST', 'PATCH')
        kila method, body kwenye itertools.product(methods_with_body, bodies):
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(Tupu)
            conn._buffer = ContentLengthChecker()
            conn.request(method, '/', body)
            self.assertEqual(
                conn._buffer.content_length, b'0',
                'Header Content-Length incorrect on {}'.format(method)
            )

        # For these methods, we make sure that content-length ni sio set when
        # the body ni Tupu because it might cause unexpected behaviour on the
        # server.
        methods_without_body = (
             'GET', 'CONNECT', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE',
        )
        kila method kwenye methods_without_body:
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(Tupu)
            conn._buffer = ContentLengthChecker()
            conn.request(method, '/', Tupu)
            self.assertEqual(
                conn._buffer.content_length, Tupu,
                'Header Content-Length set kila empty body on {}'.format(method)
            )

        # If the body ni set to '', that's considered to be "present but
        # empty" rather than "missing", so content length would be set, even
        # kila methods that don't expect a body.
        kila method kwenye methods_without_body:
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(Tupu)
            conn._buffer = ContentLengthChecker()
            conn.request(method, '/', '')
            self.assertEqual(
                conn._buffer.content_length, b'0',
                'Header Content-Length incorrect on {}'.format(method)
            )

        # If the body ni set, make sure Content-Length ni set.
        kila method kwenye itertools.chain(methods_without_body, methods_with_body):
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(Tupu)
            conn._buffer = ContentLengthChecker()
            conn.request(method, '/', ' ')
            self.assertEqual(
                conn._buffer.content_length, b'1',
                'Header Content-Length incorrect on {}'.format(method)
            )

    eleza test_putheader(self):
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket(Tupu)
        conn.putrequest('GET','/')
        conn.putheader('Content-length', 42)
        self.assertIn(b'Content-length: 42', conn._buffer)

        conn.putheader('Foo', ' bar ')
        self.assertIn(b'Foo:  bar ', conn._buffer)
        conn.putheader('Bar', '\tbaz\t')
        self.assertIn(b'Bar: \tbaz\t', conn._buffer)
        conn.putheader('Authorization', 'Bearer mytoken')
        self.assertIn(b'Authorization: Bearer mytoken', conn._buffer)
        conn.putheader('IterHeader', 'IterA', 'IterB')
        self.assertIn(b'IterHeader: IterA\r\n\tIterB', conn._buffer)
        conn.putheader('LatinHeader', b'\xFF')
        self.assertIn(b'LatinHeader: \xFF', conn._buffer)
        conn.putheader('Utf8Header', b'\xc3\x80')
        self.assertIn(b'Utf8Header: \xc3\x80', conn._buffer)
        conn.putheader('C1-Control', b'next\x85line')
        self.assertIn(b'C1-Control: next\x85line', conn._buffer)
        conn.putheader('Embedded-Fold-Space', 'is\r\n allowed')
        self.assertIn(b'Embedded-Fold-Space: is\r\n allowed', conn._buffer)
        conn.putheader('Embedded-Fold-Tab', 'is\r\n\tallowed')
        self.assertIn(b'Embedded-Fold-Tab: is\r\n\tallowed', conn._buffer)
        conn.putheader('Key Space', 'value')
        self.assertIn(b'Key Space: value', conn._buffer)
        conn.putheader('KeySpace ', 'value')
        self.assertIn(b'KeySpace : value', conn._buffer)
        conn.putheader(b'Nonkoma\xa0Space', 'value')
        self.assertIn(b'Nonkoma\xa0Space: value', conn._buffer)
        conn.putheader(b'\xa0NonkomaSpace', 'value')
        self.assertIn(b'\xa0NonkomaSpace: value', conn._buffer)

    eleza test_ipv6host_header(self):
        # Default host header on IPv6 transaction should be wrapped by [] if
        # it ni an IPv6 address
        expected = b'GET /foo HTTP/1.1\r\nHost: [2001::]:81\r\n' \
                   b'Accept-Encoding: identity\r\n\r\n'
        conn = client.HTTPConnection('[2001::]:81')
        sock = FakeSocket('')
        conn.sock = sock
        conn.request('GET', '/foo')
        self.assertKweli(sock.data.startswith(expected))

        expected = b'GET /foo HTTP/1.1\r\nHost: [2001:102A::]\r\n' \
                   b'Accept-Encoding: identity\r\n\r\n'
        conn = client.HTTPConnection('[2001:102A::]')
        sock = FakeSocket('')
        conn.sock = sock
        conn.request('GET', '/foo')
        self.assertKweli(sock.data.startswith(expected))

    eleza test_malformed_headers_coped_with(self):
        # Issue 19996
        body = "HTTP/1.1 200 OK\r\nFirst: val\r\n: nval\r\nSecond: val\r\n\r\n"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()

        self.assertEqual(resp.getheader('First'), 'val')
        self.assertEqual(resp.getheader('Second'), 'val')

    eleza test_parse_all_octets(self):
        # Ensure no valid header field octet komas the parser
        body = (
            b'HTTP/1.1 200 OK\r\n'
            b"!#$%&'*+-.^_`|~: value\r\n"  # Special token characters
            b'VCHAR: ' + bytes(range(0x21, 0x7E + 1)) + b'\r\n'
            b'obs-text: ' + bytes(range(0x80, 0xFF + 1)) + b'\r\n'
            b'obs-fold: text\r\n'
            b' folded ukijumuisha space\r\n'
            b'\tfolded ukijumuisha tab\r\n'
            b'Content-Length: 0\r\n'
            b'\r\n'
        )
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.getheader('Content-Length'), '0')
        self.assertEqual(resp.msg['Content-Length'], '0')
        self.assertEqual(resp.getheader("!#$%&'*+-.^_`|~"), 'value')
        self.assertEqual(resp.msg["!#$%&'*+-.^_`|~"], 'value')
        vchar = ''.join(map(chr, range(0x21, 0x7E + 1)))
        self.assertEqual(resp.getheader('VCHAR'), vchar)
        self.assertEqual(resp.msg['VCHAR'], vchar)
        self.assertIsNotTupu(resp.getheader('obs-text'))
        self.assertIn('obs-text', resp.msg)
        kila folded kwenye (resp.getheader('obs-fold'), resp.msg['obs-fold']):
            self.assertKweli(folded.startswith('text'))
            self.assertIn(' folded ukijumuisha space', folded)
            self.assertKweli(folded.endswith('folded ukijumuisha tab'))

    eleza test_invalid_headers(self):
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket('')
        conn.putrequest('GET', '/')

        # http://tools.ietf.org/html/rfc7230#section-3.2.4, whitespace ni no
        # longer allowed kwenye header names
        cases = (
            (b'Invalid\r\nName', b'ValidValue'),
            (b'Invalid\rName', b'ValidValue'),
            (b'Invalid\nName', b'ValidValue'),
            (b'\r\nInvalidName', b'ValidValue'),
            (b'\rInvalidName', b'ValidValue'),
            (b'\nInvalidName', b'ValidValue'),
            (b' InvalidName', b'ValidValue'),
            (b'\tInvalidName', b'ValidValue'),
            (b'Invalid:Name', b'ValidValue'),
            (b':InvalidName', b'ValidValue'),
            (b'ValidName', b'Invalid\r\nValue'),
            (b'ValidName', b'Invalid\rValue'),
            (b'ValidName', b'Invalid\nValue'),
            (b'ValidName', b'InvalidValue\r\n'),
            (b'ValidName', b'InvalidValue\r'),
            (b'ValidName', b'InvalidValue\n'),
        )
        kila name, value kwenye cases:
            ukijumuisha self.subTest((name, value)):
                ukijumuisha self.assertRaisesRegex(ValueError, 'Invalid header'):
                    conn.putheader(name, value)

    eleza test_headers_debuglevel(self):
        body = (
            b'HTTP/1.1 200 OK\r\n'
            b'First: val\r\n'
            b'Second: val1\r\n'
            b'Second: val2\r\n'
        )
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock, debuglevel=1)
        ukijumuisha support.captured_stdout() kama output:
            resp.begin()
        lines = output.getvalue().splitlines()
        self.assertEqual(lines[0], "reply: 'HTTP/1.1 200 OK\\r\\n'")
        self.assertEqual(lines[1], "header: First: val")
        self.assertEqual(lines[2], "header: Second: val1")
        self.assertEqual(lines[3], "header: Second: val2")


kundi TransferEncodingTest(TestCase):
    expected_body = b"It's just a flesh wound"

    eleza test_endheaders_chunked(self):
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket(b'')
        conn.putrequest('POST', '/')
        conn.endheaders(self._make_body(), encode_chunked=Kweli)

        _, _, body = self._parse_request(conn.sock.data)
        body = self._parse_chunked(body)
        self.assertEqual(body, self.expected_body)

    eleza test_explicit_headers(self):
        # explicit chunked
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket(b'')
        # this shouldn't actually be automatically chunk-encoded because the
        # calling code has explicitly stated that it's taking care of it
        conn.request(
            'POST', '/', self._make_body(), {'Transfer-Encoding': 'chunked'})

        _, headers, body = self._parse_request(conn.sock.data)
        self.assertNotIn('content-length', [k.lower() kila k kwenye headers.keys()])
        self.assertEqual(headers['Transfer-Encoding'], 'chunked')
        self.assertEqual(body, self.expected_body)

        # explicit chunked, string body
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket(b'')
        conn.request(
            'POST', '/', self.expected_body.decode('latin-1'),
            {'Transfer-Encoding': 'chunked'})

        _, headers, body = self._parse_request(conn.sock.data)
        self.assertNotIn('content-length', [k.lower() kila k kwenye headers.keys()])
        self.assertEqual(headers['Transfer-Encoding'], 'chunked')
        self.assertEqual(body, self.expected_body)

        # User-specified TE, but request() does the chunk encoding
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket(b'')
        conn.request('POST', '/',
            headers={'Transfer-Encoding': 'gzip, chunked'},
            encode_chunked=Kweli,
            body=self._make_body())
        _, headers, body = self._parse_request(conn.sock.data)
        self.assertNotIn('content-length', [k.lower() kila k kwenye headers])
        self.assertEqual(headers['Transfer-Encoding'], 'gzip, chunked')
        self.assertEqual(self._parse_chunked(body), self.expected_body)

    eleza test_request(self):
        kila empty_lines kwenye (Uongo, Kweli,):
            conn = client.HTTPConnection('example.com')
            conn.sock = FakeSocket(b'')
            conn.request(
                'POST', '/', self._make_body(empty_lines=empty_lines))

            _, headers, body = self._parse_request(conn.sock.data)
            body = self._parse_chunked(body)
            self.assertEqual(body, self.expected_body)
            self.assertEqual(headers['Transfer-Encoding'], 'chunked')

            # Content-Length na Transfer-Encoding SHOULD sio be sent kwenye the
            # same request
            self.assertNotIn('content-length', [k.lower() kila k kwenye headers])

    eleza test_empty_body(self):
        # Zero-length iterable should be treated like any other iterable
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket(b'')
        conn.request('POST', '/', ())
        _, headers, body = self._parse_request(conn.sock.data)
        self.assertEqual(headers['Transfer-Encoding'], 'chunked')
        self.assertNotIn('content-length', [k.lower() kila k kwenye headers])
        self.assertEqual(body, b"0\r\n\r\n")

    eleza _make_body(self, empty_lines=Uongo):
        lines = self.expected_body.split(b' ')
        kila idx, line kwenye enumerate(lines):
            # kila testing handling empty lines
            ikiwa empty_lines na idx % 2:
                tuma b''
            ikiwa idx < len(lines) - 1:
                tuma line + b' '
            isipokua:
                tuma line

    eleza _parse_request(self, data):
        lines = data.split(b'\r\n')
        request = lines[0]
        headers = {}
        n = 1
        wakati n < len(lines) na len(lines[n]) > 0:
            key, val = lines[n].split(b':')
            key = key.decode('latin-1').strip()
            headers[key] = val.decode('latin-1').strip()
            n += 1

        rudisha request, headers, b'\r\n'.join(lines[n + 1:])

    eleza _parse_chunked(self, data):
        body = []
        trailers = {}
        n = 0
        lines = data.split(b'\r\n')
        # parse body
        wakati Kweli:
            size, chunk = lines[n:n+2]
            size = int(size, 16)

            ikiwa size == 0:
                n += 1
                koma

            self.assertEqual(size, len(chunk))
            body.append(chunk)

            n += 2
            # we /should/ hit the end chunk, but check against the size of
            # lines so we're sio stuck kwenye an infinite loop should we get
            # malformed data
            ikiwa n > len(lines):
                koma

        rudisha b''.join(body)


kundi BasicTest(TestCase):
    eleza test_status_lines(self):
        # Test HTTP status lines

        body = "HTTP/1.1 200 Ok\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(0), b'')  # Issue #20007
        self.assertUongo(resp.isclosed())
        self.assertUongo(resp.closed)
        self.assertEqual(resp.read(), b"Text")
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

        body = "HTTP/1.1 400.100 Not Ok\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        self.assertRaises(client.BadStatusLine, resp.begin)

    eleza test_bad_status_repr(self):
        exc = client.BadStatusLine('')
        self.assertEqual(repr(exc), '''BadStatusLine("''")''')

    eleza test_partial_reads(self):
        # ikiwa we have Content-Length, HTTPResponse knows when to close itself,
        # the same behaviour kama when we read the whole thing ukijumuisha read()
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 4\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(2), b'Te')
        self.assertUongo(resp.isclosed())
        self.assertEqual(resp.read(2), b'xt')
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

    eleza test_mixed_reads(self):
        # readline() should update the remaining length, so that read() knows
        # how much data ni left na does sio ashiria IncompleteRead
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 13\r\n\r\nText\r\nAnother"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.readline(), b'Text\r\n')
        self.assertUongo(resp.isclosed())
        self.assertEqual(resp.read(), b'Another')
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

    eleza test_partial_readintos(self):
        # ikiwa we have Content-Length, HTTPResponse knows when to close itself,
        # the same behaviour kama when we read the whole thing ukijumuisha read()
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 4\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        b = bytearray(2)
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'Te')
        self.assertUongo(resp.isclosed())
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'xt')
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

    eleza test_partial_reads_no_content_length(self):
        # when no length ni present, the socket should be gracefully closed when
        # all data was read
        body = "HTTP/1.1 200 Ok\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(2), b'Te')
        self.assertUongo(resp.isclosed())
        self.assertEqual(resp.read(2), b'xt')
        self.assertEqual(resp.read(1), b'')
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

    eleza test_partial_readintos_no_content_length(self):
        # when no length ni present, the socket should be gracefully closed when
        # all data was read
        body = "HTTP/1.1 200 Ok\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        b = bytearray(2)
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'Te')
        self.assertUongo(resp.isclosed())
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'xt')
        n = resp.readinto(b)
        self.assertEqual(n, 0)
        self.assertKweli(resp.isclosed())

    eleza test_partial_reads_incomplete_body(self):
        # ikiwa the server shuts down the connection before the whole
        # content-length ni delivered, the socket ni gracefully closed
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 10\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(2), b'Te')
        self.assertUongo(resp.isclosed())
        self.assertEqual(resp.read(2), b'xt')
        self.assertEqual(resp.read(1), b'')
        self.assertKweli(resp.isclosed())

    eleza test_partial_readintos_incomplete_body(self):
        # ikiwa the server shuts down the connection before the whole
        # content-length ni delivered, the socket ni gracefully closed
        body = "HTTP/1.1 200 Ok\r\nContent-Length: 10\r\n\r\nText"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        b = bytearray(2)
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'Te')
        self.assertUongo(resp.isclosed())
        n = resp.readinto(b)
        self.assertEqual(n, 2)
        self.assertEqual(bytes(b), b'xt')
        n = resp.readinto(b)
        self.assertEqual(n, 0)
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

    eleza test_host_port(self):
        # Check invalid host_port

        kila hp kwenye ("www.python.org:abc", "user:pitaword@www.python.org"):
            self.assertRaises(client.InvalidURL, client.HTTPConnection, hp)

        kila hp, h, p kwenye (("[fe80::207:e9ff:fe9b]:8000",
                          "fe80::207:e9ff:fe9b", 8000),
                         ("www.python.org:80", "www.python.org", 80),
                         ("www.python.org:", "www.python.org", 80),
                         ("www.python.org", "www.python.org", 80),
                         ("[fe80::207:e9ff:fe9b]", "fe80::207:e9ff:fe9b", 80),
                         ("[fe80::207:e9ff:fe9b]:", "fe80::207:e9ff:fe9b", 80)):
            c = client.HTTPConnection(hp)
            self.assertEqual(h, c.host)
            self.assertEqual(p, c.port)

    eleza test_response_headers(self):
        # test response ukijumuisha multiple message headers ukijumuisha the same field name.
        text = ('HTTP/1.1 200 OK\r\n'
                'Set-Cookie: Customer="WILE_E_COYOTE"; '
                'Version="1"; Path="/acme"\r\n'
                'Set-Cookie: Part_Number="Rocket_Launcher_0001"; Version="1";'
                ' Path="/acme"\r\n'
                '\r\n'
                'No body\r\n')
        hdr = ('Customer="WILE_E_COYOTE"; Version="1"; Path="/acme"'
               ', '
               'Part_Number="Rocket_Launcher_0001"; Version="1"; Path="/acme"')
        s = FakeSocket(text)
        r = client.HTTPResponse(s)
        r.begin()
        cookies = r.getheader("Set-Cookie")
        self.assertEqual(cookies, hdr)

    eleza test_read_head(self):
        # Test that the library doesn't attempt to read any data
        # kutoka a HEAD request.  (Tickles SF bug #622042.)
        sock = FakeSocket(
            'HTTP/1.1 200 OK\r\n'
            'Content-Length: 14432\r\n'
            '\r\n',
            NoEOFBytesIO)
        resp = client.HTTPResponse(sock, method="HEAD")
        resp.begin()
        ikiwa resp.read():
            self.fail("Did sio expect response kutoka HEAD request")

    eleza test_readinto_head(self):
        # Test that the library doesn't attempt to read any data
        # kutoka a HEAD request.  (Tickles SF bug #622042.)
        sock = FakeSocket(
            'HTTP/1.1 200 OK\r\n'
            'Content-Length: 14432\r\n'
            '\r\n',
            NoEOFBytesIO)
        resp = client.HTTPResponse(sock, method="HEAD")
        resp.begin()
        b = bytearray(5)
        ikiwa resp.readinto(b) != 0:
            self.fail("Did sio expect response kutoka HEAD request")
        self.assertEqual(bytes(b), b'\x00'*5)

    eleza test_too_many_headers(self):
        headers = '\r\n'.join('Header%d: foo' % i
                              kila i kwenye range(client._MAXHEADERS + 1)) + '\r\n'
        text = ('HTTP/1.1 200 OK\r\n' + headers)
        s = FakeSocket(text)
        r = client.HTTPResponse(s)
        self.assertRaisesRegex(client.HTTPException,
                               r"got more than \d+ headers", r.begin)

    eleza test_send_file(self):
        expected = (b'GET /foo HTTP/1.1\r\nHost: example.com\r\n'
                    b'Accept-Encoding: identity\r\n'
                    b'Transfer-Encoding: chunked\r\n'
                    b'\r\n')

        ukijumuisha open(__file__, 'rb') kama body:
            conn = client.HTTPConnection('example.com')
            sock = FakeSocket(body)
            conn.sock = sock
            conn.request('GET', '/foo', body)
            self.assertKweli(sock.data.startswith(expected), '%r != %r' %
                    (sock.data[:len(expected)], expected))

    eleza test_send(self):
        expected = b'this ni a test this ni only a test'
        conn = client.HTTPConnection('example.com')
        sock = FakeSocket(Tupu)
        conn.sock = sock
        conn.send(expected)
        self.assertEqual(expected, sock.data)
        sock.data = b''
        conn.send(array.array('b', expected))
        self.assertEqual(expected, sock.data)
        sock.data = b''
        conn.send(io.BytesIO(expected))
        self.assertEqual(expected, sock.data)

    eleza test_send_updating_file(self):
        eleza data():
            tuma 'data'
            tuma Tupu
            tuma 'data_two'

        kundi UpdatingFile(io.TextIOBase):
            mode = 'r'
            d = data()
            eleza read(self, blocksize=-1):
                rudisha next(self.d)

        expected = b'data'

        conn = client.HTTPConnection('example.com')
        sock = FakeSocket("")
        conn.sock = sock
        conn.send(UpdatingFile())
        self.assertEqual(sock.data, expected)


    eleza test_send_iter(self):
        expected = b'GET /foo HTTP/1.1\r\nHost: example.com\r\n' \
                   b'Accept-Encoding: identity\r\nContent-Length: 11\r\n' \
                   b'\r\nonetwothree'

        eleza body():
            tuma b"one"
            tuma b"two"
            tuma b"three"

        conn = client.HTTPConnection('example.com')
        sock = FakeSocket("")
        conn.sock = sock
        conn.request('GET', '/foo', body(), {'Content-Length': '11'})
        self.assertEqual(sock.data, expected)

    eleza test_blocksize_request(self):
        """Check that request() respects the configured block size."""
        blocksize = 8  # For easy debugging.
        conn = client.HTTPConnection('example.com', blocksize=blocksize)
        sock = FakeSocket(Tupu)
        conn.sock = sock
        expected = b"a" * blocksize + b"b"
        conn.request("PUT", "/", io.BytesIO(expected), {"Content-Length": "9"})
        self.assertEqual(sock.sendall_calls, 3)
        body = sock.data.split(b"\r\n\r\n", 1)[1]
        self.assertEqual(body, expected)

    eleza test_blocksize_send(self):
        """Check that send() respects the configured block size."""
        blocksize = 8  # For easy debugging.
        conn = client.HTTPConnection('example.com', blocksize=blocksize)
        sock = FakeSocket(Tupu)
        conn.sock = sock
        expected = b"a" * blocksize + b"b"
        conn.send(io.BytesIO(expected))
        self.assertEqual(sock.sendall_calls, 2)
        self.assertEqual(sock.data, expected)

    eleza test_send_type_error(self):
        # See: Issue #12676
        conn = client.HTTPConnection('example.com')
        conn.sock = FakeSocket('')
        ukijumuisha self.assertRaises(TypeError):
            conn.request('POST', 'test', conn)

    eleza test_chunked(self):
        expected = chunked_expected
        sock = FakeSocket(chunked_start + last_chunk + chunked_end)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        resp.close()

        # Various read sizes
        kila n kwenye range(1, 12):
            sock = FakeSocket(chunked_start + last_chunk + chunked_end)
            resp = client.HTTPResponse(sock, method="GET")
            resp.begin()
            self.assertEqual(resp.read(n) + resp.read(n) + resp.read(), expected)
            resp.close()

        kila x kwenye ('', 'foo\r\n'):
            sock = FakeSocket(chunked_start + x)
            resp = client.HTTPResponse(sock, method="GET")
            resp.begin()
            jaribu:
                resp.read()
            tatizo client.IncompleteRead kama i:
                self.assertEqual(i.partial, expected)
                expected_message = 'IncompleteRead(%d bytes read)' % len(expected)
                self.assertEqual(repr(i), expected_message)
                self.assertEqual(str(i), expected_message)
            isipokua:
                self.fail('IncompleteRead expected')
            mwishowe:
                resp.close()

    eleza test_readinto_chunked(self):

        expected = chunked_expected
        nexpected = len(expected)
        b = bytearray(128)

        sock = FakeSocket(chunked_start + last_chunk + chunked_end)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        n = resp.readinto(b)
        self.assertEqual(b[:nexpected], expected)
        self.assertEqual(n, nexpected)
        resp.close()

        # Various read sizes
        kila n kwenye range(1, 12):
            sock = FakeSocket(chunked_start + last_chunk + chunked_end)
            resp = client.HTTPResponse(sock, method="GET")
            resp.begin()
            m = memoryview(b)
            i = resp.readinto(m[0:n])
            i += resp.readinto(m[i:n + i])
            i += resp.readinto(m[i:])
            self.assertEqual(b[:nexpected], expected)
            self.assertEqual(i, nexpected)
            resp.close()

        kila x kwenye ('', 'foo\r\n'):
            sock = FakeSocket(chunked_start + x)
            resp = client.HTTPResponse(sock, method="GET")
            resp.begin()
            jaribu:
                n = resp.readinto(b)
            tatizo client.IncompleteRead kama i:
                self.assertEqual(i.partial, expected)
                expected_message = 'IncompleteRead(%d bytes read)' % len(expected)
                self.assertEqual(repr(i), expected_message)
                self.assertEqual(str(i), expected_message)
            isipokua:
                self.fail('IncompleteRead expected')
            mwishowe:
                resp.close()

    eleza test_chunked_head(self):
        chunked_start = (
            'HTTP/1.1 200 OK\r\n'
            'Transfer-Encoding: chunked\r\n\r\n'
            'a\r\n'
            'hello world\r\n'
            '1\r\n'
            'd\r\n'
        )
        sock = FakeSocket(chunked_start + last_chunk + chunked_end)
        resp = client.HTTPResponse(sock, method="HEAD")
        resp.begin()
        self.assertEqual(resp.read(), b'')
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.reason, 'OK')
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

    eleza test_readinto_chunked_head(self):
        chunked_start = (
            'HTTP/1.1 200 OK\r\n'
            'Transfer-Encoding: chunked\r\n\r\n'
            'a\r\n'
            'hello world\r\n'
            '1\r\n'
            'd\r\n'
        )
        sock = FakeSocket(chunked_start + last_chunk + chunked_end)
        resp = client.HTTPResponse(sock, method="HEAD")
        resp.begin()
        b = bytearray(5)
        n = resp.readinto(b)
        self.assertEqual(n, 0)
        self.assertEqual(bytes(b), b'\x00'*5)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.reason, 'OK')
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

    eleza test_negative_content_length(self):
        sock = FakeSocket(
            'HTTP/1.1 200 OK\r\nContent-Length: -1\r\n\r\nHello\r\n')
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), b'Hello\r\n')
        self.assertKweli(resp.isclosed())

    eleza test_incomplete_read(self):
        sock = FakeSocket('HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\nHello\r\n')
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        jaribu:
            resp.read()
        tatizo client.IncompleteRead kama i:
            self.assertEqual(i.partial, b'Hello\r\n')
            self.assertEqual(repr(i),
                             "IncompleteRead(7 bytes read, 3 more expected)")
            self.assertEqual(str(i),
                             "IncompleteRead(7 bytes read, 3 more expected)")
            self.assertKweli(resp.isclosed())
        isipokua:
            self.fail('IncompleteRead expected')

    eleza test_epipe(self):
        sock = EPipeSocket(
            "HTTP/1.0 401 Authorization Required\r\n"
            "Content-type: text/html\r\n"
            "WWW-Authenticate: Basic realm=\"example\"\r\n",
            b"Content-Length")
        conn = client.HTTPConnection("example.com")
        conn.sock = sock
        self.assertRaises(OSError,
                          lambda: conn.request("PUT", "/url", "body"))
        resp = conn.getresponse()
        self.assertEqual(401, resp.status)
        self.assertEqual("Basic realm=\"example\"",
                         resp.getheader("www-authenticate"))

    # Test lines overflowing the max line size (_MAXLINE kwenye http.client)

    eleza test_overflowing_status_line(self):
        body = "HTTP/1.1 200 Ok" + "k" * 65536 + "\r\n"
        resp = client.HTTPResponse(FakeSocket(body))
        self.assertRaises((client.LineTooLong, client.BadStatusLine), resp.begin)

    eleza test_overflowing_header_line(self):
        body = (
            'HTTP/1.1 200 OK\r\n'
            'X-Foo: bar' + 'r' * 65536 + '\r\n\r\n'
        )
        resp = client.HTTPResponse(FakeSocket(body))
        self.assertRaises(client.LineTooLong, resp.begin)

    eleza test_overflowing_chunked_line(self):
        body = (
            'HTTP/1.1 200 OK\r\n'
            'Transfer-Encoding: chunked\r\n\r\n'
            + '0' * 65536 + 'a\r\n'
            'hello world\r\n'
            '0\r\n'
            '\r\n'
        )
        resp = client.HTTPResponse(FakeSocket(body))
        resp.begin()
        self.assertRaises(client.LineTooLong, resp.read)

    eleza test_early_eof(self):
        # Test httpresponse ukijumuisha no \r\n termination,
        body = "HTTP/1.1 200 Ok"
        sock = FakeSocket(body)
        resp = client.HTTPResponse(sock)
        resp.begin()
        self.assertEqual(resp.read(), b'')
        self.assertKweli(resp.isclosed())
        self.assertUongo(resp.closed)
        resp.close()
        self.assertKweli(resp.closed)

    eleza test_error_leak(self):
        # Test that the socket ni sio leaked ikiwa getresponse() fails
        conn = client.HTTPConnection('example.com')
        response = Tupu
        kundi Response(client.HTTPResponse):
            eleza __init__(self, *pos, **kw):
                nonlocal response
                response = self  # Avoid garbage collector closing the socket
                client.HTTPResponse.__init__(self, *pos, **kw)
        conn.response_class = Response
        conn.sock = FakeSocket('Invalid status line')
        conn.request('GET', '/')
        self.assertRaises(client.BadStatusLine, conn.getresponse)
        self.assertKweli(response.closed)
        self.assertKweli(conn.sock.file_closed)

    eleza test_chunked_extension(self):
        extra = '3;foo=bar\r\n' + 'abc\r\n'
        expected = chunked_expected + b'abc'

        sock = FakeSocket(chunked_start + extra + last_chunk_extended + chunked_end)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        resp.close()

    eleza test_chunked_missing_end(self):
        """some servers may serve up a short chunked encoding stream"""
        expected = chunked_expected
        sock = FakeSocket(chunked_start + last_chunk)  #no terminating crlf
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        resp.close()

    eleza test_chunked_trailers(self):
        """See that trailers are read na ignored"""
        expected = chunked_expected
        sock = FakeSocket(chunked_start + last_chunk + trailers + chunked_end)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        # we should have reached the end of the file
        self.assertEqual(sock.file.read(), b"") #we read to the end
        resp.close()

    eleza test_chunked_sync(self):
        """Check that we don't read past the end of the chunked-encoding stream"""
        expected = chunked_expected
        extradata = "extradata"
        sock = FakeSocket(chunked_start + last_chunk + trailers + chunked_end + extradata)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        # the file should now have our extradata ready to be read
        self.assertEqual(sock.file.read(), extradata.encode("ascii")) #we read to the end
        resp.close()

    eleza test_content_length_sync(self):
        """Check that we don't read past the end of the Content-Length stream"""
        extradata = b"extradata"
        expected = b"Hello123\r\n"
        sock = FakeSocket(b'HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\n' + expected + extradata)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read(), expected)
        # the file should now have our extradata ready to be read
        self.assertEqual(sock.file.read(), extradata) #we read to the end
        resp.close()

    eleza test_readlines_content_length(self):
        extradata = b"extradata"
        expected = b"Hello123\r\n"
        sock = FakeSocket(b'HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\n' + expected + extradata)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.readlines(2000), [expected])
        # the file should now have our extradata ready to be read
        self.assertEqual(sock.file.read(), extradata) #we read to the end
        resp.close()

    eleza test_read1_content_length(self):
        extradata = b"extradata"
        expected = b"Hello123\r\n"
        sock = FakeSocket(b'HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\n' + expected + extradata)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read1(2000), expected)
        # the file should now have our extradata ready to be read
        self.assertEqual(sock.file.read(), extradata) #we read to the end
        resp.close()

    eleza test_readline_bound_content_length(self):
        extradata = b"extradata"
        expected = b"Hello123\r\n"
        sock = FakeSocket(b'HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\n' + expected + extradata)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.readline(10), expected)
        self.assertEqual(resp.readline(10), b"")
        # the file should now have our extradata ready to be read
        self.assertEqual(sock.file.read(), extradata) #we read to the end
        resp.close()

    eleza test_read1_bound_content_length(self):
        extradata = b"extradata"
        expected = b"Hello123\r\n"
        sock = FakeSocket(b'HTTP/1.1 200 OK\r\nContent-Length: 30\r\n\r\n' + expected*3 + extradata)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        self.assertEqual(resp.read1(20), expected*2)
        self.assertEqual(resp.read(), expected)
        # the file should now have our extradata ready to be read
        self.assertEqual(sock.file.read(), extradata) #we read to the end
        resp.close()

    eleza test_response_fileno(self):
        # Make sure fd returned by fileno ni valid.
        serv = socket.create_server((HOST, 0))
        self.addCleanup(serv.close)

        result = Tupu
        eleza run_server():
            [conn, address] = serv.accept()
            ukijumuisha conn, conn.makefile("rb") kama reader:
                # Read the request header until a blank line
                wakati Kweli:
                    line = reader.readline()
                    ikiwa sio line.rstrip(b"\r\n"):
                        koma
                conn.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
                nonlocal result
                result = reader.read()

        thread = threading.Thread(target=run_server)
        thread.start()
        self.addCleanup(thread.join, float(1))
        conn = client.HTTPConnection(*serv.getsockname())
        conn.request("CONNECT", "dummy:1234")
        response = conn.getresponse()
        jaribu:
            self.assertEqual(response.status, client.OK)
            s = socket.socket(fileno=response.fileno())
            jaribu:
                s.sendall(b"proxied data\n")
            mwishowe:
                s.detach()
        mwishowe:
            response.close()
            conn.close()
        thread.join()
        self.assertEqual(result, b"proxied data\n")

    eleza test_putrequest_override_validation(self):
        """
        It should be possible to override the default validation
        behavior kwenye putrequest (bpo-38216).
        """
        kundi UnsafeHTTPConnection(client.HTTPConnection):
            eleza _validate_path(self, url):
                pita

        conn = UnsafeHTTPConnection('example.com')
        conn.sock = FakeSocket('')
        conn.putrequest('GET', '/\x00')

    eleza test_putrequest_override_encoding(self):
        """
        It should be possible to override the default encoding
        to transmit bytes kwenye another encoding even ikiwa invalid
        (bpo-36274).
        """
        kundi UnsafeHTTPConnection(client.HTTPConnection):
            eleza _encode_request(self, str_url):
                rudisha str_url.encode('utf-8')

        conn = UnsafeHTTPConnection('example.com')
        conn.sock = FakeSocket('')
        conn.putrequest('GET', '/☃')


kundi ExtendedReadTest(TestCase):
    """
    Test peek(), read1(), readline()
    """
    lines = (
        'HTTP/1.1 200 OK\r\n'
        '\r\n'
        'hello world!\n'
        'and now \n'
        'kila something completely different\n'
        'foo'
        )
    lines_expected = lines[lines.find('hello'):].encode("ascii")
    lines_chunked = (
        'HTTP/1.1 200 OK\r\n'
        'Transfer-Encoding: chunked\r\n\r\n'
        'a\r\n'
        'hello worl\r\n'
        '3\r\n'
        'd!\n\r\n'
        '9\r\n'
        'and now \n\r\n'
        '23\r\n'
        'kila something completely different\n\r\n'
        '3\r\n'
        'foo\r\n'
        '0\r\n' # terminating chunk
        '\r\n'  # end of trailers
    )

    eleza setUp(self):
        sock = FakeSocket(self.lines)
        resp = client.HTTPResponse(sock, method="GET")
        resp.begin()
        resp.fp = io.BufferedReader(resp.fp)
        self.resp = resp



    eleza test_peek(self):
        resp = self.resp
        # patch up the buffered peek so that it returns sio too much stuff
        oldpeek = resp.fp.peek
        eleza mypeek(n=-1):
            p = oldpeek(n)
            ikiwa n >= 0:
                rudisha p[:n]
            rudisha p[:10]
        resp.fp.peek = mypeek

        all = []
        wakati Kweli:
            # try a short peek
            p = resp.peek(3)
            ikiwa p:
                self.assertGreater(len(p), 0)
                # then unbounded peek
                p2 = resp.peek()
                self.assertGreaterEqual(len(p2), len(p))
                self.assertKweli(p2.startswith(p))
                next = resp.read(len(p2))
                self.assertEqual(next, p2)
            isipokua:
                next = resp.read()
                self.assertUongo(next)
            all.append(next)
            ikiwa sio next:
                koma
        self.assertEqual(b"".join(all), self.lines_expected)

    eleza test_readline(self):
        resp = self.resp
        self._verify_readline(self.resp.readline, self.lines_expected)

    eleza _verify_readline(self, readline, expected):
        all = []
        wakati Kweli:
            # short readlines
            line = readline(5)
            ikiwa line na line != b"foo":
                ikiwa len(line) < 5:
                    self.assertKweli(line.endswith(b"\n"))
            all.append(line)
            ikiwa sio line:
                koma
        self.assertEqual(b"".join(all), expected)

    eleza test_read1(self):
        resp = self.resp
        eleza r():
            res = resp.read1(4)
            self.assertLessEqual(len(res), 4)
            rudisha res
        readliner = Readliner(r)
        self._verify_readline(readliner.readline, self.lines_expected)

    eleza test_read1_unbounded(self):
        resp = self.resp
        all = []
        wakati Kweli:
            data = resp.read1()
            ikiwa sio data:
                koma
            all.append(data)
        self.assertEqual(b"".join(all), self.lines_expected)

    eleza test_read1_bounded(self):
        resp = self.resp
        all = []
        wakati Kweli:
            data = resp.read1(10)
            ikiwa sio data:
                koma
            self.assertLessEqual(len(data), 10)
            all.append(data)
        self.assertEqual(b"".join(all), self.lines_expected)

    eleza test_read1_0(self):
        self.assertEqual(self.resp.read1(0), b"")

    eleza test_peek_0(self):
        p = self.resp.peek(0)
        self.assertLessEqual(0, len(p))


kundi ExtendedReadTestChunked(ExtendedReadTest):
    """
    Test peek(), read1(), readline() kwenye chunked mode
    """
    lines = (
        'HTTP/1.1 200 OK\r\n'
        'Transfer-Encoding: chunked\r\n\r\n'
        'a\r\n'
        'hello worl\r\n'
        '3\r\n'
        'd!\n\r\n'
        '9\r\n'
        'and now \n\r\n'
        '23\r\n'
        'kila something completely different\n\r\n'
        '3\r\n'
        'foo\r\n'
        '0\r\n' # terminating chunk
        '\r\n'  # end of trailers
    )


kundi Readliner:
    """
    a simple readline kundi that uses an arbitrary read function na buffering
    """
    eleza __init__(self, readfunc):
        self.readfunc = readfunc
        self.remainder = b""

    eleza readline(self, limit):
        data = []
        datalen = 0
        read = self.remainder
        jaribu:
            wakati Kweli:
                idx = read.find(b'\n')
                ikiwa idx != -1:
                    koma
                ikiwa datalen + len(read) >= limit:
                    idx = limit - datalen - 1
                # read more data
                data.append(read)
                read = self.readfunc()
                ikiwa sio read:
                    idx = 0 #eof condition
                    koma
            idx += 1
            data.append(read[:idx])
            self.remainder = read[idx:]
            rudisha b"".join(data)
        tatizo:
            self.remainder = b"".join(data)
            raise


kundi OfflineTest(TestCase):
    eleza test_all(self):
        # Documented objects defined kwenye the module should be kwenye __all__
        expected = {"responses"}  # White-list documented dict() object
        # HTTPMessage, parse_headers(), na the HTTP status code constants are
        # intentionally omitted kila simplicity
        blacklist = {"HTTPMessage", "parse_headers"}
        kila name kwenye dir(client):
            ikiwa name.startswith("_") ama name kwenye blacklist:
                endelea
            module_object = getattr(client, name)
            ikiwa getattr(module_object, "__module__", Tupu) == "http.client":
                expected.add(name)
        self.assertCountEqual(client.__all__, expected)

    eleza test_responses(self):
        self.assertEqual(client.responses[client.NOT_FOUND], "Not Found")

    eleza test_client_constants(self):
        # Make sure we don't koma backward compatibility ukijumuisha 3.4
        expected = [
            'CONTINUE',
            'SWITCHING_PROTOCOLS',
            'PROCESSING',
            'OK',
            'CREATED',
            'ACCEPTED',
            'NON_AUTHORITATIVE_INFORMATION',
            'NO_CONTENT',
            'RESET_CONTENT',
            'PARTIAL_CONTENT',
            'MULTI_STATUS',
            'IM_USED',
            'MULTIPLE_CHOICES',
            'MOVED_PERMANENTLY',
            'FOUND',
            'SEE_OTHER',
            'NOT_MODIFIED',
            'USE_PROXY',
            'TEMPORARY_REDIRECT',
            'BAD_REQUEST',
            'UNAUTHORIZED',
            'PAYMENT_REQUIRED',
            'FORBIDDEN',
            'NOT_FOUND',
            'METHOD_NOT_ALLOWED',
            'NOT_ACCEPTABLE',
            'PROXY_AUTHENTICATION_REQUIRED',
            'REQUEST_TIMEOUT',
            'CONFLICT',
            'GONE',
            'LENGTH_REQUIRED',
            'PRECONDITION_FAILED',
            'REQUEST_ENTITY_TOO_LARGE',
            'REQUEST_URI_TOO_LONG',
            'UNSUPPORTED_MEDIA_TYPE',
            'REQUESTED_RANGE_NOT_SATISFIABLE',
            'EXPECTATION_FAILED',
            'MISDIRECTED_REQUEST',
            'UNPROCESSABLE_ENTITY',
            'LOCKED',
            'FAILED_DEPENDENCY',
            'UPGRADE_REQUIRED',
            'PRECONDITION_REQUIRED',
            'TOO_MANY_REQUESTS',
            'REQUEST_HEADER_FIELDS_TOO_LARGE',
            'UNAVAILABLE_FOR_LEGAL_REASONS',
            'INTERNAL_SERVER_ERROR',
            'NOT_IMPLEMENTED',
            'BAD_GATEWAY',
            'SERVICE_UNAVAILABLE',
            'GATEWAY_TIMEOUT',
            'HTTP_VERSION_NOT_SUPPORTED',
            'INSUFFICIENT_STORAGE',
            'NOT_EXTENDED',
            'NETWORK_AUTHENTICATION_REQUIRED',
        ]
        kila const kwenye expected:
            ukijumuisha self.subTest(constant=const):
                self.assertKweli(hasattr(client, const))


kundi SourceAddressTest(TestCase):
    eleza setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = support.bind_port(self.serv)
        self.source_port = support.find_unused_port()
        self.serv.listen()
        self.conn = Tupu

    eleza tearDown(self):
        ikiwa self.conn:
            self.conn.close()
            self.conn = Tupu
        self.serv.close()
        self.serv = Tupu

    eleza testHTTPConnectionSourceAddress(self):
        self.conn = client.HTTPConnection(HOST, self.port,
                source_address=('', self.source_port))
        self.conn.connect()
        self.assertEqual(self.conn.sock.getsockname()[1], self.source_port)

    @unittest.skipIf(sio hasattr(client, 'HTTPSConnection'),
                     'http.client.HTTPSConnection sio defined')
    eleza testHTTPSConnectionSourceAddress(self):
        self.conn = client.HTTPSConnection(HOST, self.port,
                source_address=('', self.source_port))
        # We don't test anything here other than the constructor sio barfing as
        # this code doesn't deal ukijumuisha setting up an active running SSL server
        # kila an ssl_wrapped connect() to actually rudisha from.


kundi TimeoutTest(TestCase):
    PORT = Tupu

    eleza setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TimeoutTest.PORT = support.bind_port(self.serv)
        self.serv.listen()

    eleza tearDown(self):
        self.serv.close()
        self.serv = Tupu

    eleza testTimeoutAttribute(self):
        # This will prove that the timeout gets through HTTPConnection
        # na into the socket.

        # default -- use global socket timeout
        self.assertIsTupu(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        jaribu:
            httpConn = client.HTTPConnection(HOST, TimeoutTest.PORT)
            httpConn.connect()
        mwishowe:
            socket.setdefaulttimeout(Tupu)
        self.assertEqual(httpConn.sock.gettimeout(), 30)
        httpConn.close()

        # no timeout -- do sio use global socket default
        self.assertIsTupu(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        jaribu:
            httpConn = client.HTTPConnection(HOST, TimeoutTest.PORT,
                                              timeout=Tupu)
            httpConn.connect()
        mwishowe:
            socket.setdefaulttimeout(Tupu)
        self.assertEqual(httpConn.sock.gettimeout(), Tupu)
        httpConn.close()

        # a value
        httpConn = client.HTTPConnection(HOST, TimeoutTest.PORT, timeout=30)
        httpConn.connect()
        self.assertEqual(httpConn.sock.gettimeout(), 30)
        httpConn.close()


kundi PersistenceTest(TestCase):

    eleza test_reuse_reconnect(self):
        # Should reuse ama reconnect depending on header kutoka server
        tests = (
            ('1.0', '', Uongo),
            ('1.0', 'Connection: keep-alive\r\n', Kweli),
            ('1.1', '', Kweli),
            ('1.1', 'Connection: close\r\n', Uongo),
            ('1.0', 'Connection: keep-ALIVE\r\n', Kweli),
            ('1.1', 'Connection: cloSE\r\n', Uongo),
        )
        kila version, header, reuse kwenye tests:
            ukijumuisha self.subTest(version=version, header=header):
                msg = (
                    'HTTP/{} 200 OK\r\n'
                    '{}'
                    'Content-Length: 12\r\n'
                    '\r\n'
                    'Dummy body\r\n'
                ).format(version, header)
                conn = FakeSocketHTTPConnection(msg)
                self.assertIsTupu(conn.sock)
                conn.request('GET', '/open-connection')
                ukijumuisha conn.getresponse() kama response:
                    self.assertEqual(conn.sock ni Tupu, sio reuse)
                    response.read()
                self.assertEqual(conn.sock ni Tupu, sio reuse)
                self.assertEqual(conn.connections, 1)
                conn.request('GET', '/subsequent-request')
                self.assertEqual(conn.connections, 1 ikiwa reuse isipokua 2)

    eleza test_disconnected(self):

        eleza make_reset_reader(text):
            """Return BufferedReader that raises ECONNRESET at EOF"""
            stream = io.BytesIO(text)
            eleza readinto(buffer):
                size = io.BytesIO.readinto(stream, buffer)
                ikiwa size == 0:
                    ashiria ConnectionResetError()
                rudisha size
            stream.readinto = readinto
            rudisha io.BufferedReader(stream)

        tests = (
            (io.BytesIO, client.RemoteDisconnected),
            (make_reset_reader, ConnectionResetError),
        )
        kila stream_factory, exception kwenye tests:
            ukijumuisha self.subTest(exception=exception):
                conn = FakeSocketHTTPConnection(b'', stream_factory)
                conn.request('GET', '/eof-response')
                self.assertRaises(exception, conn.getresponse)
                self.assertIsTupu(conn.sock)
                # HTTPConnection.connect() should be automatically invoked
                conn.request('GET', '/reconnect')
                self.assertEqual(conn.connections, 2)

    eleza test_100_close(self):
        conn = FakeSocketHTTPConnection(
            b'HTTP/1.1 100 Continue\r\n'
            b'\r\n'
            # Missing final response
        )
        conn.request('GET', '/', headers={'Expect': '100-endelea'})
        self.assertRaises(client.RemoteDisconnected, conn.getresponse)
        self.assertIsTupu(conn.sock)
        conn.request('GET', '/reconnect')
        self.assertEqual(conn.connections, 2)


kundi HTTPSTest(TestCase):

    eleza setUp(self):
        ikiwa sio hasattr(client, 'HTTPSConnection'):
            self.skipTest('ssl support required')

    eleza make_server(self, certfile):
        kutoka test.ssl_servers agiza make_https_server
        rudisha make_https_server(self, certfile=certfile)

    eleza test_attributes(self):
        # simple test to check it's storing the timeout
        h = client.HTTPSConnection(HOST, TimeoutTest.PORT, timeout=30)
        self.assertEqual(h.timeout, 30)

    eleza test_networked(self):
        # Default settings: requires a valid cert kutoka a trusted CA
        agiza ssl
        support.requires('network')
        ukijumuisha support.transient_internet('self-signed.pythontest.net'):
            h = client.HTTPSConnection('self-signed.pythontest.net', 443)
            ukijumuisha self.assertRaises(ssl.SSLError) kama exc_info:
                h.request('GET', '/')
            self.assertEqual(exc_info.exception.reason, 'CERTIFICATE_VERIFY_FAILED')

    eleza test_networked_noverification(self):
        # Switch off cert verification
        agiza ssl
        support.requires('network')
        ukijumuisha support.transient_internet('self-signed.pythontest.net'):
            context = ssl._create_unverified_context()
            h = client.HTTPSConnection('self-signed.pythontest.net', 443,
                                       context=context)
            h.request('GET', '/')
            resp = h.getresponse()
            h.close()
            self.assertIn('nginx', resp.getheader('server'))
            resp.close()

    @support.system_must_validate_cert
    eleza test_networked_trusted_by_default_cert(self):
        # Default settings: requires a valid cert kutoka a trusted CA
        support.requires('network')
        ukijumuisha support.transient_internet('www.python.org'):
            h = client.HTTPSConnection('www.python.org', 443)
            h.request('GET', '/')
            resp = h.getresponse()
            content_type = resp.getheader('content-type')
            resp.close()
            h.close()
            self.assertIn('text/html', content_type)

    eleza test_networked_good_cert(self):
        # We feed the server's cert kama a validating cert
        agiza ssl
        support.requires('network')
        selfsigned_pythontestdotnet = 'self-signed.pythontest.net'
        ukijumuisha support.transient_internet(selfsigned_pythontestdotnet):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
            self.assertEqual(context.check_hostname, Kweli)
            context.load_verify_locations(CERT_selfsigned_pythontestdotnet)
            jaribu:
                h = client.HTTPSConnection(selfsigned_pythontestdotnet, 443,
                                           context=context)
                h.request('GET', '/')
                resp = h.getresponse()
            tatizo ssl.SSLError kama ssl_err:
                ssl_err_str = str(ssl_err)
                # In the error message of [SSL: CERTIFICATE_VERIFY_FAILED] on
                # modern Linux distros (Debian Buster, etc) default OpenSSL
                # configurations it'll fail saying "key too weak" until we
                # address https://bugs.python.org/issue36816 to use a proper
                # key size on self-signed.pythontest.net.
                ikiwa re.search(r'(?i)key.too.weak', ssl_err_str):
                    ashiria unittest.SkipTest(
                        f'Got {ssl_err_str} trying to connect '
                        f'to {selfsigned_pythontestdotnet}. '
                        'See https://bugs.python.org/issue36816.')
                raise
            server_string = resp.getheader('server')
            resp.close()
            h.close()
            self.assertIn('nginx', server_string)

    eleza test_networked_bad_cert(self):
        # We feed a "CA" cert that ni unrelated to the server's cert
        agiza ssl
        support.requires('network')
        ukijumuisha support.transient_internet('self-signed.pythontest.net'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations(CERT_localhost)
            h = client.HTTPSConnection('self-signed.pythontest.net', 443, context=context)
            ukijumuisha self.assertRaises(ssl.SSLError) kama exc_info:
                h.request('GET', '/')
            self.assertEqual(exc_info.exception.reason, 'CERTIFICATE_VERIFY_FAILED')

    eleza test_local_unknown_cert(self):
        # The custom cert isn't known to the default trust bundle
        agiza ssl
        server = self.make_server(CERT_localhost)
        h = client.HTTPSConnection('localhost', server.port)
        ukijumuisha self.assertRaises(ssl.SSLError) kama exc_info:
            h.request('GET', '/')
        self.assertEqual(exc_info.exception.reason, 'CERTIFICATE_VERIFY_FAILED')

    eleza test_local_good_hostname(self):
        # The (valid) cert validates the HTTP hostname
        agiza ssl
        server = self.make_server(CERT_localhost)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(CERT_localhost)
        h = client.HTTPSConnection('localhost', server.port, context=context)
        self.addCleanup(h.close)
        h.request('GET', '/nonexistent')
        resp = h.getresponse()
        self.addCleanup(resp.close)
        self.assertEqual(resp.status, 404)

    eleza test_local_bad_hostname(self):
        # The (valid) cert doesn't validate the HTTP hostname
        agiza ssl
        server = self.make_server(CERT_fakehostname)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(CERT_fakehostname)
        h = client.HTTPSConnection('localhost', server.port, context=context)
        ukijumuisha self.assertRaises(ssl.CertificateError):
            h.request('GET', '/')
        # Same ukijumuisha explicit check_hostname=Kweli
        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            h = client.HTTPSConnection('localhost', server.port,
                                       context=context, check_hostname=Kweli)
        ukijumuisha self.assertRaises(ssl.CertificateError):
            h.request('GET', '/')
        # With check_hostname=Uongo, the mismatching ni ignored
        context.check_hostname = Uongo
        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            h = client.HTTPSConnection('localhost', server.port,
                                       context=context, check_hostname=Uongo)
        h.request('GET', '/nonexistent')
        resp = h.getresponse()
        resp.close()
        h.close()
        self.assertEqual(resp.status, 404)
        # The context's check_hostname setting ni used ikiwa one isn't pitaed to
        # HTTPSConnection.
        context.check_hostname = Uongo
        h = client.HTTPSConnection('localhost', server.port, context=context)
        h.request('GET', '/nonexistent')
        resp = h.getresponse()
        self.assertEqual(resp.status, 404)
        resp.close()
        h.close()
        # Passing check_hostname to HTTPSConnection should override the
        # context's setting.
        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            h = client.HTTPSConnection('localhost', server.port,
                                       context=context, check_hostname=Kweli)
        ukijumuisha self.assertRaises(ssl.CertificateError):
            h.request('GET', '/')

    @unittest.skipIf(sio hasattr(client, 'HTTPSConnection'),
                     'http.client.HTTPSConnection sio available')
    eleza test_host_port(self):
        # Check invalid host_port

        kila hp kwenye ("www.python.org:abc", "user:pitaword@www.python.org"):
            self.assertRaises(client.InvalidURL, client.HTTPSConnection, hp)

        kila hp, h, p kwenye (("[fe80::207:e9ff:fe9b]:8000",
                          "fe80::207:e9ff:fe9b", 8000),
                         ("www.python.org:443", "www.python.org", 443),
                         ("www.python.org:", "www.python.org", 443),
                         ("www.python.org", "www.python.org", 443),
                         ("[fe80::207:e9ff:fe9b]", "fe80::207:e9ff:fe9b", 443),
                         ("[fe80::207:e9ff:fe9b]:", "fe80::207:e9ff:fe9b",
                             443)):
            c = client.HTTPSConnection(hp)
            self.assertEqual(h, c.host)
            self.assertEqual(p, c.port)

    eleza test_tls13_pha(self):
        agiza ssl
        ikiwa sio ssl.HAS_TLSv1_3:
            self.skipTest('TLS 1.3 support required')
        # just check status of PHA flag
        h = client.HTTPSConnection('localhost', 443)
        self.assertKweli(h._context.post_handshake_auth)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertUongo(context.post_handshake_auth)
        h = client.HTTPSConnection('localhost', 443, context=context)
        self.assertIs(h._context, context)
        self.assertUongo(h._context.post_handshake_auth)

        ukijumuisha warnings.catch_warnings():
            warnings.filterwarnings('ignore', 'key_file, cert_file na check_hostname are deprecated',
                                    DeprecationWarning)
            h = client.HTTPSConnection('localhost', 443, context=context,
                                       cert_file=CERT_localhost)
        self.assertKweli(h._context.post_handshake_auth)


kundi RequestBodyTest(TestCase):
    """Test cases where a request includes a message body."""

    eleza setUp(self):
        self.conn = client.HTTPConnection('example.com')
        self.conn.sock = self.sock = FakeSocket("")
        self.conn.sock = self.sock

    eleza get_headers_and_fp(self):
        f = io.BytesIO(self.sock.data)
        f.readline()  # read the request line
        message = client.parse_headers(f)
        rudisha message, f

    eleza test_list_body(self):
        # Note that no content-length ni automatically calculated for
        # an iterable.  The request will fall back to send chunked
        # transfer encoding.
        cases = (
            ([b'foo', b'bar'], b'3\r\nfoo\r\n3\r\nbar\r\n0\r\n\r\n'),
            ((b'foo', b'bar'), b'3\r\nfoo\r\n3\r\nbar\r\n0\r\n\r\n'),
        )
        kila body, expected kwenye cases:
            ukijumuisha self.subTest(body):
                self.conn = client.HTTPConnection('example.com')
                self.conn.sock = self.sock = FakeSocket('')

                self.conn.request('PUT', '/url', body)
                msg, f = self.get_headers_and_fp()
                self.assertNotIn('Content-Type', msg)
                self.assertNotIn('Content-Length', msg)
                self.assertEqual(msg.get('Transfer-Encoding'), 'chunked')
                self.assertEqual(expected, f.read())

    eleza test_manual_content_length(self):
        # Set an incorrect content-length so that we can verify that
        # it will sio be over-ridden by the library.
        self.conn.request("PUT", "/url", "body",
                          {"Content-Length": "42"})
        message, f = self.get_headers_and_fp()
        self.assertEqual("42", message.get("content-length"))
        self.assertEqual(4, len(f.read()))

    eleza test_ascii_body(self):
        self.conn.request("PUT", "/url", "body")
        message, f = self.get_headers_and_fp()
        self.assertEqual("text/plain", message.get_content_type())
        self.assertIsTupu(message.get_charset())
        self.assertEqual("4", message.get("content-length"))
        self.assertEqual(b'body', f.read())

    eleza test_latin1_body(self):
        self.conn.request("PUT", "/url", "body\xc1")
        message, f = self.get_headers_and_fp()
        self.assertEqual("text/plain", message.get_content_type())
        self.assertIsTupu(message.get_charset())
        self.assertEqual("5", message.get("content-length"))
        self.assertEqual(b'body\xc1', f.read())

    eleza test_bytes_body(self):
        self.conn.request("PUT", "/url", b"body\xc1")
        message, f = self.get_headers_and_fp()
        self.assertEqual("text/plain", message.get_content_type())
        self.assertIsTupu(message.get_charset())
        self.assertEqual("5", message.get("content-length"))
        self.assertEqual(b'body\xc1', f.read())

    eleza test_text_file_body(self):
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha open(support.TESTFN, "w") kama f:
            f.write("body")
        ukijumuisha open(support.TESTFN) kama f:
            self.conn.request("PUT", "/url", f)
            message, f = self.get_headers_and_fp()
            self.assertEqual("text/plain", message.get_content_type())
            self.assertIsTupu(message.get_charset())
            # No content-length will be determined kila files; the body
            # will be sent using chunked transfer encoding instead.
            self.assertIsTupu(message.get("content-length"))
            self.assertEqual("chunked", message.get("transfer-encoding"))
            self.assertEqual(b'4\r\nbody\r\n0\r\n\r\n', f.read())

    eleza test_binary_file_body(self):
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha open(support.TESTFN, "wb") kama f:
            f.write(b"body\xc1")
        ukijumuisha open(support.TESTFN, "rb") kama f:
            self.conn.request("PUT", "/url", f)
            message, f = self.get_headers_and_fp()
            self.assertEqual("text/plain", message.get_content_type())
            self.assertIsTupu(message.get_charset())
            self.assertEqual("chunked", message.get("Transfer-Encoding"))
            self.assertNotIn("Content-Length", message)
            self.assertEqual(b'5\r\nbody\xc1\r\n0\r\n\r\n', f.read())


kundi HTTPResponseTest(TestCase):

    eleza setUp(self):
        body = "HTTP/1.1 200 Ok\r\nMy-Header: first-value\r\nMy-Header: \
                second-value\r\n\r\nText"
        sock = FakeSocket(body)
        self.resp = client.HTTPResponse(sock)
        self.resp.begin()

    eleza test_getting_header(self):
        header = self.resp.getheader('My-Header')
        self.assertEqual(header, 'first-value, second-value')

        header = self.resp.getheader('My-Header', 'some default')
        self.assertEqual(header, 'first-value, second-value')

    eleza test_getting_nonexistent_header_with_string_default(self):
        header = self.resp.getheader('No-Such-Header', 'default-value')
        self.assertEqual(header, 'default-value')

    eleza test_getting_nonexistent_header_with_iterable_default(self):
        header = self.resp.getheader('No-Such-Header', ['default', 'values'])
        self.assertEqual(header, 'default, values')

        header = self.resp.getheader('No-Such-Header', ('default', 'values'))
        self.assertEqual(header, 'default, values')

    eleza test_getting_nonexistent_header_without_default(self):
        header = self.resp.getheader('No-Such-Header')
        self.assertEqual(header, Tupu)

    eleza test_getting_header_defaultint(self):
        header = self.resp.getheader('No-Such-Header',default=42)
        self.assertEqual(header, 42)

kundi TunnelTests(TestCase):
    eleza setUp(self):
        response_text = (
            'HTTP/1.0 200 OK\r\n\r\n' # Reply to CONNECT
            'HTTP/1.1 200 OK\r\n' # Reply to HEAD
            'Content-Length: 42\r\n\r\n'
        )
        self.host = 'proxy.com'
        self.conn = client.HTTPConnection(self.host)
        self.conn._create_connection = self._create_connection(response_text)

    eleza tearDown(self):
        self.conn.close()

    eleza _create_connection(self, response_text):
        eleza create_connection(address, timeout=Tupu, source_address=Tupu):
            rudisha FakeSocket(response_text, host=address[0], port=address[1])
        rudisha create_connection

    eleza test_set_tunnel_host_port_headers(self):
        tunnel_host = 'destination.com'
        tunnel_port = 8888
        tunnel_headers = {'User-Agent': 'Mozilla/5.0 (compatible, MSIE 11)'}
        self.conn.set_tunnel(tunnel_host, port=tunnel_port,
                             headers=tunnel_headers)
        self.conn.request('HEAD', '/', '')
        self.assertEqual(self.conn.sock.host, self.host)
        self.assertEqual(self.conn.sock.port, client.HTTP_PORT)
        self.assertEqual(self.conn._tunnel_host, tunnel_host)
        self.assertEqual(self.conn._tunnel_port, tunnel_port)
        self.assertEqual(self.conn._tunnel_headers, tunnel_headers)

    eleza test_disallow_set_tunnel_after_connect(self):
        # Once connected, we shouldn't be able to tunnel anymore
        self.conn.connect()
        self.assertRaises(RuntimeError, self.conn.set_tunnel,
                          'destination.com')

    eleza test_connect_with_tunnel(self):
        self.conn.set_tunnel('destination.com')
        self.conn.request('HEAD', '/', '')
        self.assertEqual(self.conn.sock.host, self.host)
        self.assertEqual(self.conn.sock.port, client.HTTP_PORT)
        self.assertIn(b'CONNECT destination.com', self.conn.sock.data)
        # issue22095
        self.assertNotIn(b'Host: destination.com:Tupu', self.conn.sock.data)
        self.assertIn(b'Host: destination.com', self.conn.sock.data)

        # This test should be removed when CONNECT gets the HTTP/1.1 blessing
        self.assertNotIn(b'Host: proxy.com', self.conn.sock.data)

    eleza test_connect_put_request(self):
        self.conn.set_tunnel('destination.com')
        self.conn.request('PUT', '/', '')
        self.assertEqual(self.conn.sock.host, self.host)
        self.assertEqual(self.conn.sock.port, client.HTTP_PORT)
        self.assertIn(b'CONNECT destination.com', self.conn.sock.data)
        self.assertIn(b'Host: destination.com', self.conn.sock.data)

    eleza test_tunnel_debuglog(self):
        expected_header = 'X-Dummy: 1'
        response_text = 'HTTP/1.0 200 OK\r\n{}\r\n\r\n'.format(expected_header)

        self.conn.set_debuglevel(1)
        self.conn._create_connection = self._create_connection(response_text)
        self.conn.set_tunnel('destination.com')

        ukijumuisha support.captured_stdout() kama output:
            self.conn.request('PUT', '/', '')
        lines = output.getvalue().splitlines()
        self.assertIn('header: {}'.format(expected_header), lines)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
