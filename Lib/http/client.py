r"""HTTP/1.1 client library

<intro stuff goes here>
<other stuff, too>

HTTPConnection goes through a number of "states", which define when a client
may legally make another request ama fetch the response kila a particular
request. This diagram details these state transitions:

    (null)
      |
      | HTTPConnection()
      v
    Idle
      |
      | putrequest()
      v
    Request-started
      |
      | ( putheader() )*  endheaders()
      v
    Request-sent
      |\_____________________________
      |                              | getresponse() raises
      | response = getresponse()     | ConnectionError
      v                              v
    Unread-response                Idle
    [Response-headers-read]
      |\____________________
      |                     |
      | response.read()     | putrequest()
      v                     v
    Idle                  Req-started-unread-response
                     ______/|
                   /        |
   response.read() |        | ( putheader() )*  endheaders()
                   v        v
       Request-started    Req-sent-unread-response
                            |
                            | response.read()
                            v
                          Request-sent

This diagram presents the following rules:
  -- a second request may sio be started until {response-headers-read}
  -- a response [object] cansio be retrieved until {request-sent}
  -- there ni no differentiation between an unread response body na a
     partially read response body

Note: this enforcement ni applied by the HTTPConnection class. The
      HTTPResponse kundi does sio enforce this state machine, which
      implies sophisticated clients may accelerate the request/response
      pipeline. Caution should be taken, though: accelerating the states
      beyond the above pattern may imply knowledge of the server's
      connection-close behavior kila certain requests. For example, it
      ni impossible to tell whether the server will close the connection
      UNTIL the response headers have been read; this means that further
      requests cansio be placed into the pipeline until it ni known that
      the server will NOT be closing the connection.

Logical State                  __state            __response
-------------                  -------            ----------
Idle                           _CS_IDLE           Tupu
Request-started                _CS_REQ_STARTED    Tupu
Request-sent                   _CS_REQ_SENT       Tupu
Unread-response                _CS_IDLE           <response_class>
Req-started-unread-response    _CS_REQ_STARTED    <response_class>
Req-sent-unread-response       _CS_REQ_SENT       <response_class>
"""

agiza email.parser
agiza email.message
agiza http
agiza io
agiza re
agiza socket
agiza collections.abc
kutoka urllib.parse agiza urlsplit

# HTTPMessage, parse_headers(), na the HTTP status code constants are
# intentionally omitted kila simplicity
__all__ = ["HTTPResponse", "HTTPConnection",
           "HTTPException", "NotConnected", "UnknownProtocol",
           "UnknownTransferEncoding", "UnimplementedFileMode",
           "IncompleteRead", "InvalidURL", "ImproperConnectionState",
           "CannotSendRequest", "CannotSendHeader", "ResponseNotReady",
           "BadStatusLine", "LineTooLong", "RemoteDisconnected", "error",
           "responses"]

HTTP_PORT = 80
HTTPS_PORT = 443

_UNKNOWN = 'UNKNOWN'

# connection states
_CS_IDLE = 'Idle'
_CS_REQ_STARTED = 'Request-started'
_CS_REQ_SENT = 'Request-sent'


# hack to maintain backwards compatibility
globals().update(http.HTTPStatus.__members__)

# another hack to maintain backwards compatibility
# Mapping status codes to official W3C names
responses = {v: v.phrase kila v kwenye http.HTTPStatus.__members__.values()}

# maximal line length when calling readline().
_MAXLINE = 65536
_MAXHEADERS = 100

# Header name/value ABNF (http://tools.ietf.org/html/rfc7230#section-3.2)
#
# VCHAR          = %x21-7E
# obs-text       = %x80-FF
# header-field   = field-name ":" OWS field-value OWS
# field-name     = token
# field-value    = *( field-content / obs-fold )
# field-content  = field-vchar [ 1*( SP / HTAB ) field-vchar ]
# field-vchar    = VCHAR / obs-text
#
# obs-fold       = CRLF 1*( SP / HTAB )
#                ; obsolete line folding
#                ; see Section 3.2.4

# token          = 1*tchar
#
# tchar          = "!" / "#" / "$" / "%" / "&" / "'" / "*"
#                / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~"
#                / DIGIT / ALPHA
#                ; any VCHAR, tatizo delimiters
#
# VCHAR defined kwenye http://tools.ietf.org/html/rfc5234#appendix-B.1

# the patterns kila both name na value are more lenient than RFC
# definitions to allow kila backwards compatibility
_is_legal_header_name = re.compile(rb'[^:\s][^:\r\n]*').fullmatch
_is_illegal_header_value = re.compile(rb'\n(?![ \t])|\r(?![ \t\n])').search

# These characters are sio allowed within HTTP URL paths.
#  See https://tools.ietf.org/html/rfc3986#section-3.3 na the
#  https://tools.ietf.org/html/rfc3986#appendix-A pchar definition.
# Prevents CVE-2019-9740.  Includes control characters such kama \r\n.
# We don't restrict chars above \x7f kama putrequest() limits us to ASCII.
_contains_disallowed_url_pchar_re = re.compile('[\x00-\x20\x7f]')
# Arguably only these _should_ allowed:
#  _is_allowed_url_pchars_re = re.compile(r"^[/!$&'()*+,;=:@%a-zA-Z0-9._~-]+$")
# We are more lenient kila assumed real world compatibility purposes.

# We always set the Content-Length header kila these methods because some
# servers will otherwise respond ukijumuisha a 411
_METHODS_EXPECTING_BODY = {'PATCH', 'POST', 'PUT'}


eleza _encode(data, name='data'):
    """Call data.encode("latin-1") but show a better error message."""
    jaribu:
        rudisha data.encode("latin-1")
    tatizo UnicodeEncodeError kama err:
        ashiria UnicodeEncodeError(
            err.encoding,
            err.object,
            err.start,
            err.end,
            "%s (%.20r) ni sio valid Latin-1. Use %s.encode('utf-8') "
            "ikiwa you want to send it encoded kwenye UTF-8." %
            (name.title(), data[err.start:err.end], name)) kutoka Tupu


kundi HTTPMessage(email.message.Message):
    # XXX The only usage of this method ni kwenye
    # http.server.CGIHTTPRequestHandler.  Maybe move the code there so
    # that it doesn't need to be part of the public API.  The API has
    # never been defined so this could cause backwards compatibility
    # issues.

    eleza getallmatchingheaders(self, name):
        """Find all header lines matching a given header name.

        Look through the list of headers na find all lines matching a given
        header name (and their continuation lines).  A list of the lines is
        returned, without interpretation.  If the header does sio occur, an
        empty list ni returned.  If the header occurs multiple times, all
        occurrences are returned.  Case ni sio important kwenye the header name.

        """
        name = name.lower() + ':'
        n = len(name)
        lst = []
        hit = 0
        kila line kwenye self.keys():
            ikiwa line[:n].lower() == name:
                hit = 1
            lasivyo sio line[:1].isspace():
                hit = 0
            ikiwa hit:
                lst.append(line)
        rudisha lst

eleza parse_headers(fp, _class=HTTPMessage):
    """Parses only RFC2822 headers kutoka a file pointer.

    email Parser wants to see strings rather than bytes.
    But a TextIOWrapper around self.rfile would buffer too many bytes
    kutoka the stream, bytes which we later need to read kama bytes.
    So we read the correct bytes here, kama bytes, kila email Parser
    to parse.

    """
    headers = []
    wakati Kweli:
        line = fp.readline(_MAXLINE + 1)
        ikiwa len(line) > _MAXLINE:
            ashiria LineTooLong("header line")
        headers.append(line)
        ikiwa len(headers) > _MAXHEADERS:
            ashiria HTTPException("got more than %d headers" % _MAXHEADERS)
        ikiwa line kwenye (b'\r\n', b'\n', b''):
            koma
    hstring = b''.join(headers).decode('iso-8859-1')
    rudisha email.parser.Parser(_class=_class).parsestr(hstring)


kundi HTTPResponse(io.BufferedIOBase):

    # See RFC 2616 sec 19.6 na RFC 1945 sec 6 kila details.

    # The bytes kutoka the socket object are iso-8859-1 strings.
    # See RFC 2616 sec 2.2 which notes an exception kila MIME-encoded
    # text following RFC 2047.  The basic status line parsing only
    # accepts iso-8859-1.

    eleza __init__(self, sock, debuglevel=0, method=Tupu, url=Tupu):
        # If the response includes a content-length header, we need to
        # make sure that the client doesn't read more than the
        # specified number of bytes.  If it does, it will block until
        # the server times out na closes the connection.  This will
        # happen ikiwa a self.fp.read() ni done (without a size) whether
        # self.fp ni buffered ama not.  So, no self.fp.read() by
        # clients unless they know what they are doing.
        self.fp = sock.makefile("rb")
        self.debuglevel = debuglevel
        self._method = method

        # The HTTPResponse object ni returned via urllib.  The clients
        # of http na urllib expect different attributes kila the
        # headers.  headers ni used here na supports urllib.  msg is
        # provided kama a backwards compatibility layer kila http
        # clients.

        self.headers = self.msg = Tupu

        # kutoka the Status-Line of the response
        self.version = _UNKNOWN # HTTP-Version
        self.status = _UNKNOWN  # Status-Code
        self.reason = _UNKNOWN  # Reason-Phrase

        self.chunked = _UNKNOWN         # ni "chunked" being used?
        self.chunk_left = _UNKNOWN      # bytes left to read kwenye current chunk
        self.length = _UNKNOWN          # number of bytes left kwenye response
        self.will_close = _UNKNOWN      # conn will close at end of response

    eleza _read_status(self):
        line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
        ikiwa len(line) > _MAXLINE:
            ashiria LineTooLong("status line")
        ikiwa self.debuglevel > 0:
            andika("reply:", repr(line))
        ikiwa sio line:
            # Presumably, the server closed the connection before
            # sending a valid response.
            ashiria RemoteDisconnected("Remote end closed connection without"
                                     " response")
        jaribu:
            version, status, reason = line.split(Tupu, 2)
        tatizo ValueError:
            jaribu:
                version, status = line.split(Tupu, 1)
                reason = ""
            tatizo ValueError:
                # empty version will cause next test to fail.
                version = ""
        ikiwa sio version.startswith("HTTP/"):
            self._close_conn()
            ashiria BadStatusLine(line)

        # The status code ni a three-digit number
        jaribu:
            status = int(status)
            ikiwa status < 100 ama status > 999:
                ashiria BadStatusLine(line)
        tatizo ValueError:
            ashiria BadStatusLine(line)
        rudisha version, status, reason

    eleza begin(self):
        ikiwa self.headers ni sio Tupu:
            # we've already started reading the response
            rudisha

        # read until we get a non-100 response
        wakati Kweli:
            version, status, reason = self._read_status()
            ikiwa status != CONTINUE:
                koma
            # skip the header kutoka the 100 response
            wakati Kweli:
                skip = self.fp.readline(_MAXLINE + 1)
                ikiwa len(skip) > _MAXLINE:
                    ashiria LineTooLong("header line")
                skip = skip.strip()
                ikiwa sio skip:
                    koma
                ikiwa self.debuglevel > 0:
                    andika("header:", skip)

        self.code = self.status = status
        self.reason = reason.strip()
        ikiwa version kwenye ("HTTP/1.0", "HTTP/0.9"):
            # Some servers might still rudisha "0.9", treat it kama 1.0 anyway
            self.version = 10
        lasivyo version.startswith("HTTP/1."):
            self.version = 11   # use HTTP/1.1 code kila HTTP/1.x where x>=1
        isipokua:
            ashiria UnknownProtocol(version)

        self.headers = self.msg = parse_headers(self.fp)

        ikiwa self.debuglevel > 0:
            kila hdr, val kwenye self.headers.items():
                andika("header:", hdr + ":", val)

        # are we using the chunked-style of transfer encoding?
        tr_enc = self.headers.get("transfer-encoding")
        ikiwa tr_enc na tr_enc.lower() == "chunked":
            self.chunked = Kweli
            self.chunk_left = Tupu
        isipokua:
            self.chunked = Uongo

        # will the connection close at the end of the response?
        self.will_close = self._check_close()

        # do we have a Content-Length?
        # NOTE: RFC 2616, S4.4, #3 says we ignore this ikiwa tr_enc ni "chunked"
        self.length = Tupu
        length = self.headers.get("content-length")

         # are we using the chunked-style of transfer encoding?
        tr_enc = self.headers.get("transfer-encoding")
        ikiwa length na sio self.chunked:
            jaribu:
                self.length = int(length)
            tatizo ValueError:
                self.length = Tupu
            isipokua:
                ikiwa self.length < 0:  # ignore nonsensical negative lengths
                    self.length = Tupu
        isipokua:
            self.length = Tupu

        # does the body have a fixed length? (of zero)
        ikiwa (status == NO_CONTENT ama status == NOT_MODIFIED ama
            100 <= status < 200 ama      # 1xx codes
            self._method == "HEAD"):
            self.length = 0

        # ikiwa the connection remains open, na we aren't using chunked, na
        # a content-length was sio provided, then assume that the connection
        # WILL close.
        ikiwa (sio self.will_close na
            sio self.chunked na
            self.length ni Tupu):
            self.will_close = Kweli

    eleza _check_close(self):
        conn = self.headers.get("connection")
        ikiwa self.version == 11:
            # An HTTP/1.1 proxy ni assumed to stay open unless
            # explicitly closed.
            ikiwa conn na "close" kwenye conn.lower():
                rudisha Kweli
            rudisha Uongo

        # Some HTTP/1.0 implementations have support kila persistent
        # connections, using rules different than HTTP/1.1.

        # For older HTTP, Keep-Alive indicates persistent connection.
        ikiwa self.headers.get("keep-alive"):
            rudisha Uongo

        # At least Akamai returns a "Connection: Keep-Alive" header,
        # which was supposed to be sent by the client.
        ikiwa conn na "keep-alive" kwenye conn.lower():
            rudisha Uongo

        # Proxy-Connection ni a netscape hack.
        pconn = self.headers.get("proxy-connection")
        ikiwa pconn na "keep-alive" kwenye pconn.lower():
            rudisha Uongo

        # otherwise, assume it will close
        rudisha Kweli

    eleza _close_conn(self):
        fp = self.fp
        self.fp = Tupu
        fp.close()

    eleza close(self):
        jaribu:
            super().close() # set "closed" flag
        mwishowe:
            ikiwa self.fp:
                self._close_conn()

    # These implementations are kila the benefit of io.BufferedReader.

    # XXX This kundi should probably be revised to act more like
    # the "raw stream" that BufferedReader expects.

    eleza flush(self):
        super().flush()
        ikiwa self.fp:
            self.fp.flush()

    eleza readable(self):
        """Always returns Kweli"""
        rudisha Kweli

    # End of "raw stream" methods

    eleza isclosed(self):
        """Kweli ikiwa the connection ni closed."""
        # NOTE: it ni possible that we will sio ever call self.close(). This
        #       case occurs when will_close ni TRUE, length ni Tupu, na we
        #       read up to the last byte, but NOT past it.
        #
        # IMPLIES: ikiwa will_close ni FALSE, then self.close() will ALWAYS be
        #          called, meaning self.isclosed() ni meaningful.
        rudisha self.fp ni Tupu

    eleza read(self, amt=Tupu):
        ikiwa self.fp ni Tupu:
            rudisha b""

        ikiwa self._method == "HEAD":
            self._close_conn()
            rudisha b""

        ikiwa amt ni sio Tupu:
            # Amount ni given, implement using readinto
            b = bytearray(amt)
            n = self.readinto(b)
            rudisha memoryview(b)[:n].tobytes()
        isipokua:
            # Amount ni sio given (unbounded read) so we must check self.length
            # na self.chunked

            ikiwa self.chunked:
                rudisha self._readall_chunked()

            ikiwa self.length ni Tupu:
                s = self.fp.read()
            isipokua:
                jaribu:
                    s = self._safe_read(self.length)
                tatizo IncompleteRead:
                    self._close_conn()
                    raise
                self.length = 0
            self._close_conn()        # we read everything
            rudisha s

    eleza readinto(self, b):
        """Read up to len(b) bytes into bytearray b na rudisha the number
        of bytes read.
        """

        ikiwa self.fp ni Tupu:
            rudisha 0

        ikiwa self._method == "HEAD":
            self._close_conn()
            rudisha 0

        ikiwa self.chunked:
            rudisha self._readinto_chunked(b)

        ikiwa self.length ni sio Tupu:
            ikiwa len(b) > self.length:
                # clip the read to the "end of response"
                b = memoryview(b)[0:self.length]

        # we do sio use _safe_read() here because this may be a .will_close
        # connection, na the user ni reading more bytes than will be provided
        # (kila example, reading kwenye 1k chunks)
        n = self.fp.readinto(b)
        ikiwa sio n na b:
            # Ideally, we would ashiria IncompleteRead ikiwa the content-length
            # wasn't satisfied, but it might koma compatibility.
            self._close_conn()
        lasivyo self.length ni sio Tupu:
            self.length -= n
            ikiwa sio self.length:
                self._close_conn()
        rudisha n

    eleza _read_next_chunk_size(self):
        # Read the next chunk size kutoka the file
        line = self.fp.readline(_MAXLINE + 1)
        ikiwa len(line) > _MAXLINE:
            ashiria LineTooLong("chunk size")
        i = line.find(b";")
        ikiwa i >= 0:
            line = line[:i] # strip chunk-extensions
        jaribu:
            rudisha int(line, 16)
        tatizo ValueError:
            # close the connection kama protocol synchronisation is
            # probably lost
            self._close_conn()
            raise

    eleza _read_and_discard_trailer(self):
        # read na discard trailer up to the CRLF terminator
        ### note: we shouldn't have any trailers!
        wakati Kweli:
            line = self.fp.readline(_MAXLINE + 1)
            ikiwa len(line) > _MAXLINE:
                ashiria LineTooLong("trailer line")
            ikiwa sio line:
                # a vanishingly small number of sites EOF without
                # sending the trailer
                koma
            ikiwa line kwenye (b'\r\n', b'\n', b''):
                koma

    eleza _get_chunk_left(self):
        # rudisha self.chunk_left, reading a new chunk ikiwa necessary.
        # chunk_left == 0: at the end of the current chunk, need to close it
        # chunk_left == Tupu: No current chunk, should read next.
        # This function returns non-zero ama Tupu ikiwa the last chunk has
        # been read.
        chunk_left = self.chunk_left
        ikiwa sio chunk_left: # Can be 0 ama Tupu
            ikiwa chunk_left ni sio Tupu:
                # We are at the end of chunk, discard chunk end
                self._safe_read(2)  # toss the CRLF at the end of the chunk
            jaribu:
                chunk_left = self._read_next_chunk_size()
            tatizo ValueError:
                ashiria IncompleteRead(b'')
            ikiwa chunk_left == 0:
                # last chunk: 1*("0") [ chunk-extension ] CRLF
                self._read_and_discard_trailer()
                # we read everything; close the "file"
                self._close_conn()
                chunk_left = Tupu
            self.chunk_left = chunk_left
        rudisha chunk_left

    eleza _readall_chunked(self):
        assert self.chunked != _UNKNOWN
        value = []
        jaribu:
            wakati Kweli:
                chunk_left = self._get_chunk_left()
                ikiwa chunk_left ni Tupu:
                    koma
                value.append(self._safe_read(chunk_left))
                self.chunk_left = 0
            rudisha b''.join(value)
        tatizo IncompleteRead:
            ashiria IncompleteRead(b''.join(value))

    eleza _readinto_chunked(self, b):
        assert self.chunked != _UNKNOWN
        total_bytes = 0
        mvb = memoryview(b)
        jaribu:
            wakati Kweli:
                chunk_left = self._get_chunk_left()
                ikiwa chunk_left ni Tupu:
                    rudisha total_bytes

                ikiwa len(mvb) <= chunk_left:
                    n = self._safe_readinto(mvb)
                    self.chunk_left = chunk_left - n
                    rudisha total_bytes + n

                temp_mvb = mvb[:chunk_left]
                n = self._safe_readinto(temp_mvb)
                mvb = mvb[n:]
                total_bytes += n
                self.chunk_left = 0

        tatizo IncompleteRead:
            ashiria IncompleteRead(bytes(b[0:total_bytes]))

    eleza _safe_read(self, amt):
        """Read the number of bytes requested.

        This function should be used when <amt> bytes "should" be present for
        reading. If the bytes are truly sio available (due to EOF), then the
        IncompleteRead exception can be used to detect the problem.
        """
        data = self.fp.read(amt)
        ikiwa len(data) < amt:
            ashiria IncompleteRead(data, amt-len(data))
        rudisha data

    eleza _safe_readinto(self, b):
        """Same kama _safe_read, but kila reading into a buffer."""
        amt = len(b)
        n = self.fp.readinto(b)
        ikiwa n < amt:
            ashiria IncompleteRead(bytes(b[:n]), amt-n)
        rudisha n

    eleza read1(self, n=-1):
        """Read ukijumuisha at most one underlying system call.  If at least one
        byte ni buffered, rudisha that instead.
        """
        ikiwa self.fp ni Tupu ama self._method == "HEAD":
            rudisha b""
        ikiwa self.chunked:
            rudisha self._read1_chunked(n)
        ikiwa self.length ni sio Tupu na (n < 0 ama n > self.length):
            n = self.length
        result = self.fp.read1(n)
        ikiwa sio result na n:
            self._close_conn()
        lasivyo self.length ni sio Tupu:
            self.length -= len(result)
        rudisha result

    eleza peek(self, n=-1):
        # Having this enables IOBase.readline() to read more than one
        # byte at a time
        ikiwa self.fp ni Tupu ama self._method == "HEAD":
            rudisha b""
        ikiwa self.chunked:
            rudisha self._peek_chunked(n)
        rudisha self.fp.peek(n)

    eleza readline(self, limit=-1):
        ikiwa self.fp ni Tupu ama self._method == "HEAD":
            rudisha b""
        ikiwa self.chunked:
            # Fallback to IOBase readline which uses peek() na read()
            rudisha super().readline(limit)
        ikiwa self.length ni sio Tupu na (limit < 0 ama limit > self.length):
            limit = self.length
        result = self.fp.readline(limit)
        ikiwa sio result na limit:
            self._close_conn()
        lasivyo self.length ni sio Tupu:
            self.length -= len(result)
        rudisha result

    eleza _read1_chunked(self, n):
        # Strictly speaking, _get_chunk_left() may cause more than one read,
        # but that ni ok, since that ni to satisfy the chunked protocol.
        chunk_left = self._get_chunk_left()
        ikiwa chunk_left ni Tupu ama n == 0:
            rudisha b''
        ikiwa sio (0 <= n <= chunk_left):
            n = chunk_left # ikiwa n ni negative ama larger than chunk_left
        read = self.fp.read1(n)
        self.chunk_left -= len(read)
        ikiwa sio read:
            ashiria IncompleteRead(b"")
        rudisha read

    eleza _peek_chunked(self, n):
        # Strictly speaking, _get_chunk_left() may cause more than one read,
        # but that ni ok, since that ni to satisfy the chunked protocol.
        jaribu:
            chunk_left = self._get_chunk_left()
        tatizo IncompleteRead:
            rudisha b'' # peek doesn't worry about protocol
        ikiwa chunk_left ni Tupu:
            rudisha b'' # eof
        # peek ni allowed to rudisha more than requested.  Just request the
        # entire chunk, na truncate what we get.
        rudisha self.fp.peek(chunk_left)[:chunk_left]

    eleza fileno(self):
        rudisha self.fp.fileno()

    eleza getheader(self, name, default=Tupu):
        '''Returns the value of the header matching *name*.

        If there are multiple matching headers, the values are
        combined into a single string separated by commas na spaces.

        If no matching header ni found, returns *default* ama Tupu if
        the *default* ni sio specified.

        If the headers are unknown, raises http.client.ResponseNotReady.

        '''
        ikiwa self.headers ni Tupu:
            ashiria ResponseNotReady()
        headers = self.headers.get_all(name) ama default
        ikiwa isinstance(headers, str) ama sio hasattr(headers, '__iter__'):
            rudisha headers
        isipokua:
            rudisha ', '.join(headers)

    eleza getheaders(self):
        """Return list of (header, value) tuples."""
        ikiwa self.headers ni Tupu:
            ashiria ResponseNotReady()
        rudisha list(self.headers.items())

    # We override IOBase.__iter__ so that it doesn't check kila closed-ness

    eleza __iter__(self):
        rudisha self

    # For compatibility ukijumuisha old-style urllib responses.

    eleza info(self):
        '''Returns an instance of the kundi mimetools.Message containing
        meta-information associated ukijumuisha the URL.

        When the method ni HTTP, these headers are those returned by
        the server at the head of the retrieved HTML page (including
        Content-Length na Content-Type).

        When the method ni FTP, a Content-Length header will be
        present ikiwa (as ni now usual) the server pitaed back a file
        length kwenye response to the FTP retrieval request. A
        Content-Type header will be present ikiwa the MIME type can be
        guessed.

        When the method ni local-file, returned headers will include
        a Date representing the file's last-modified time, a
        Content-Length giving file size, na a Content-Type
        containing a guess at the file's type. See also the
        description of the mimetools module.

        '''
        rudisha self.headers

    eleza geturl(self):
        '''Return the real URL of the page.

        In some cases, the HTTP server redirects a client to another
        URL. The urlopen() function handles this transparently, but kwenye
        some cases the caller needs to know which URL the client was
        redirected to. The geturl() method can be used to get at this
        redirected URL.

        '''
        rudisha self.url

    eleza getcode(self):
        '''Return the HTTP status code that was sent ukijumuisha the response,
        ama Tupu ikiwa the URL ni sio an HTTP URL.

        '''
        rudisha self.status

kundi HTTPConnection:

    _http_vsn = 11
    _http_vsn_str = 'HTTP/1.1'

    response_class = HTTPResponse
    default_port = HTTP_PORT
    auto_open = 1
    debuglevel = 0

    @staticmethod
    eleza _is_textIO(stream):
        """Test whether a file-like object ni a text ama a binary stream.
        """
        rudisha isinstance(stream, io.TextIOBase)

    @staticmethod
    eleza _get_content_length(body, method):
        """Get the content-length based on the body.

        If the body ni Tupu, we set Content-Length: 0 kila methods that expect
        a body (RFC 7230, Section 3.3.2). We also set the Content-Length for
        any method ikiwa the body ni a str ama bytes-like object na sio a file.
        """
        ikiwa body ni Tupu:
            # do an explicit check kila sio Tupu here to distinguish
            # between unset na set but empty
            ikiwa method.upper() kwenye _METHODS_EXPECTING_BODY:
                rudisha 0
            isipokua:
                rudisha Tupu

        ikiwa hasattr(body, 'read'):
            # file-like object.
            rudisha Tupu

        jaribu:
            # does it implement the buffer protocol (bytes, bytearray, array)?
            mv = memoryview(body)
            rudisha mv.nbytes
        tatizo TypeError:
            pita

        ikiwa isinstance(body, str):
            rudisha len(body)

        rudisha Tupu

    eleza __init__(self, host, port=Tupu, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=Tupu, blocksize=8192):
        self.timeout = timeout
        self.source_address = source_address
        self.blocksize = blocksize
        self.sock = Tupu
        self._buffer = []
        self.__response = Tupu
        self.__state = _CS_IDLE
        self._method = Tupu
        self._tunnel_host = Tupu
        self._tunnel_port = Tupu
        self._tunnel_headers = {}

        (self.host, self.port) = self._get_hostport(host, port)

        # This ni stored kama an instance variable to allow unit
        # tests to replace it ukijumuisha a suitable mockup
        self._create_connection = socket.create_connection

    eleza set_tunnel(self, host, port=Tupu, headers=Tupu):
        """Set up host na port kila HTTP CONNECT tunnelling.

        In a connection that uses HTTP CONNECT tunneling, the host pitaed to the
        constructor ni used kama a proxy server that relays all communication to
        the endpoint pitaed to `set_tunnel`. This done by sending an HTTP
        CONNECT request to the proxy server when the connection ni established.

        This method must be called before the HTML connection has been
        established.

        The headers argument should be a mapping of extra HTTP headers to send
        ukijumuisha the CONNECT request.
        """

        ikiwa self.sock:
            ashiria RuntimeError("Can't set up tunnel kila established connection")

        self._tunnel_host, self._tunnel_port = self._get_hostport(host, port)
        ikiwa headers:
            self._tunnel_headers = headers
        isipokua:
            self._tunnel_headers.clear()

    eleza _get_hostport(self, host, port):
        ikiwa port ni Tupu:
            i = host.rfind(':')
            j = host.rfind(']')         # ipv6 addresses have [...]
            ikiwa i > j:
                jaribu:
                    port = int(host[i+1:])
                tatizo ValueError:
                    ikiwa host[i+1:] == "": # http://foo.com:/ == http://foo.com/
                        port = self.default_port
                    isipokua:
                        ashiria InvalidURL("nonnumeric port: '%s'" % host[i+1:])
                host = host[:i]
            isipokua:
                port = self.default_port
            ikiwa host na host[0] == '[' na host[-1] == ']':
                host = host[1:-1]

        rudisha (host, port)

    eleza set_debuglevel(self, level):
        self.debuglevel = level

    eleza _tunnel(self):
        connect_str = "CONNECT %s:%d HTTP/1.0\r\n" % (self._tunnel_host,
            self._tunnel_port)
        connect_bytes = connect_str.encode("ascii")
        self.send(connect_bytes)
        kila header, value kwenye self._tunnel_headers.items():
            header_str = "%s: %s\r\n" % (header, value)
            header_bytes = header_str.encode("latin-1")
            self.send(header_bytes)
        self.send(b'\r\n')

        response = self.response_class(self.sock, method=self._method)
        (version, code, message) = response._read_status()

        ikiwa code != http.HTTPStatus.OK:
            self.close()
            ashiria OSError("Tunnel connection failed: %d %s" % (code,
                                                               message.strip()))
        wakati Kweli:
            line = response.fp.readline(_MAXLINE + 1)
            ikiwa len(line) > _MAXLINE:
                ashiria LineTooLong("header line")
            ikiwa sio line:
                # kila sites which EOF without sending a trailer
                koma
            ikiwa line kwenye (b'\r\n', b'\n', b''):
                koma

            ikiwa self.debuglevel > 0:
                andika('header:', line.decode())

    eleza connect(self):
        """Connect to the host na port specified kwenye __init__."""
        self.sock = self._create_connection(
            (self.host,self.port), self.timeout, self.source_address)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        ikiwa self._tunnel_host:
            self._tunnel()

    eleza close(self):
        """Close the connection to the HTTP server."""
        self.__state = _CS_IDLE
        jaribu:
            sock = self.sock
            ikiwa sock:
                self.sock = Tupu
                sock.close()   # close it manually... there may be other refs
        mwishowe:
            response = self.__response
            ikiwa response:
                self.__response = Tupu
                response.close()

    eleza send(self, data):
        """Send `data' to the server.
        ``data`` can be a string object, a bytes object, an array object, a
        file-like object that supports a .read() method, ama an iterable object.
        """

        ikiwa self.sock ni Tupu:
            ikiwa self.auto_open:
                self.connect()
            isipokua:
                ashiria NotConnected()

        ikiwa self.debuglevel > 0:
            andika("send:", repr(data))
        ikiwa hasattr(data, "read") :
            ikiwa self.debuglevel > 0:
                andika("sendIng a read()able")
            encode = self._is_textIO(data)
            ikiwa encode na self.debuglevel > 0:
                andika("encoding file using iso-8859-1")
            wakati 1:
                datablock = data.read(self.blocksize)
                ikiwa sio datablock:
                    koma
                ikiwa encode:
                    datablock = datablock.encode("iso-8859-1")
                self.sock.sendall(datablock)
            rudisha
        jaribu:
            self.sock.sendall(data)
        tatizo TypeError:
            ikiwa isinstance(data, collections.abc.Iterable):
                kila d kwenye data:
                    self.sock.sendall(d)
            isipokua:
                ashiria TypeError("data should be a bytes-like object "
                                "or an iterable, got %r" % type(data))

    eleza _output(self, s):
        """Add a line of output to the current request buffer.

        Assumes that the line does *not* end ukijumuisha \\r\\n.
        """
        self._buffer.append(s)

    eleza _read_readable(self, readable):
        ikiwa self.debuglevel > 0:
            andika("sendIng a read()able")
        encode = self._is_textIO(readable)
        ikiwa encode na self.debuglevel > 0:
            andika("encoding file using iso-8859-1")
        wakati Kweli:
            datablock = readable.read(self.blocksize)
            ikiwa sio datablock:
                koma
            ikiwa encode:
                datablock = datablock.encode("iso-8859-1")
            tuma datablock

    eleza _send_output(self, message_body=Tupu, encode_chunked=Uongo):
        """Send the currently buffered request na clear the buffer.

        Appends an extra \\r\\n to the buffer.
        A message_body may be specified, to be appended to the request.
        """
        self._buffer.extend((b"", b""))
        msg = b"\r\n".join(self._buffer)
        toa self._buffer[:]
        self.send(msg)

        ikiwa message_body ni sio Tupu:

            # create a consistent interface to message_body
            ikiwa hasattr(message_body, 'read'):
                # Let file-like take precedence over byte-like.  This
                # ni needed to allow the current position of mmap'ed
                # files to be taken into account.
                chunks = self._read_readable(message_body)
            isipokua:
                jaribu:
                    # this ni solely to check to see ikiwa message_body
                    # implements the buffer API.  it /would/ be easier
                    # to capture ikiwa PyObject_CheckBuffer was exposed
                    # to Python.
                    memoryview(message_body)
                tatizo TypeError:
                    jaribu:
                        chunks = iter(message_body)
                    tatizo TypeError:
                        ashiria TypeError("message_body should be a bytes-like "
                                        "object ama an iterable, got %r"
                                        % type(message_body))
                isipokua:
                    # the object implements the buffer interface na
                    # can be pitaed directly into socket methods
                    chunks = (message_body,)

            kila chunk kwenye chunks:
                ikiwa sio chunk:
                    ikiwa self.debuglevel > 0:
                        andika('Zero length chunk ignored')
                    endelea

                ikiwa encode_chunked na self._http_vsn == 11:
                    # chunked encoding
                    chunk = f'{len(chunk):X}\r\n'.encode('ascii') + chunk \
                        + b'\r\n'
                self.send(chunk)

            ikiwa encode_chunked na self._http_vsn == 11:
                # end chunked transfer
                self.send(b'0\r\n\r\n')

    eleza putrequest(self, method, url, skip_host=Uongo,
                   skip_accept_encoding=Uongo):
        """Send a request to the server.

        `method' specifies an HTTP request method, e.g. 'GET'.
        `url' specifies the object being requested, e.g. '/index.html'.
        `skip_host' ikiwa Kweli does sio add automatically a 'Host:' header
        `skip_accept_encoding' ikiwa Kweli does sio add automatically an
           'Accept-Encoding:' header
        """

        # ikiwa a prior response has been completed, then forget about it.
        ikiwa self.__response na self.__response.isclosed():
            self.__response = Tupu


        # kwenye certain cases, we cansio issue another request on this connection.
        # this occurs when:
        #   1) we are kwenye the process of sending a request.   (_CS_REQ_STARTED)
        #   2) a response to a previous request has signalled that it ni going
        #      to close the connection upon completion.
        #   3) the headers kila the previous response have sio been read, thus
        #      we cansio determine whether point (2) ni true.   (_CS_REQ_SENT)
        #
        # ikiwa there ni no prior response, then we can request at will.
        #
        # ikiwa point (2) ni true, then we will have pitaed the socket to the
        # response (effectively meaning, "there ni no prior response"), na
        # will open a new one when a new request ni made.
        #
        # Note: ikiwa a prior response exists, then we *can* start a new request.
        #       We are sio allowed to begin fetching the response to this new
        #       request, however, until that prior response ni complete.
        #
        ikiwa self.__state == _CS_IDLE:
            self.__state = _CS_REQ_STARTED
        isipokua:
            ashiria CannotSendRequest(self.__state)

        # Save the method kila use later kwenye the response phase
        self._method = method

        url = url ama '/'
        self._validate_path(url)

        request = '%s %s %s' % (method, url, self._http_vsn_str)

        self._output(self._encode_request(request))

        ikiwa self._http_vsn == 11:
            # Issue some standard headers kila better HTTP/1.1 compliance

            ikiwa sio skip_host:
                # this header ni issued *only* kila HTTP/1.1
                # connections. more specifically, this means it is
                # only issued when the client uses the new
                # HTTPConnection() class. backwards-compat clients
                # will be using HTTP/1.0 na those clients may be
                # issuing this header themselves. we should NOT issue
                # it twice; some web servers (such kama Apache) barf
                # when they see two Host: headers

                # If we need a non-standard port,include it kwenye the
                # header.  If the request ni going through a proxy,
                # but the host of the actual URL, sio the host of the
                # proxy.

                netloc = ''
                ikiwa url.startswith('http'):
                    nil, netloc, nil, nil, nil = urlsplit(url)

                ikiwa netloc:
                    jaribu:
                        netloc_enc = netloc.encode("ascii")
                    tatizo UnicodeEncodeError:
                        netloc_enc = netloc.encode("idna")
                    self.putheader('Host', netloc_enc)
                isipokua:
                    ikiwa self._tunnel_host:
                        host = self._tunnel_host
                        port = self._tunnel_port
                    isipokua:
                        host = self.host
                        port = self.port

                    jaribu:
                        host_enc = host.encode("ascii")
                    tatizo UnicodeEncodeError:
                        host_enc = host.encode("idna")

                    # As per RFC 273, IPv6 address should be wrapped ukijumuisha []
                    # when used kama Host header

                    ikiwa host.find(':') >= 0:
                        host_enc = b'[' + host_enc + b']'

                    ikiwa port == self.default_port:
                        self.putheader('Host', host_enc)
                    isipokua:
                        host_enc = host_enc.decode("ascii")
                        self.putheader('Host', "%s:%s" % (host_enc, port))

            # note: we are assuming that clients will sio attempt to set these
            #       headers since *this* library must deal ukijumuisha the
            #       consequences. this also means that when the supporting
            #       libraries are updated to recognize other forms, then this
            #       code should be changed (removed ama updated).

            # we only want a Content-Encoding of "identity" since we don't
            # support encodings such kama x-gzip ama x-deflate.
            ikiwa sio skip_accept_encoding:
                self.putheader('Accept-Encoding', 'identity')

            # we can accept "chunked" Transfer-Encodings, but no others
            # NOTE: no TE header implies *only* "chunked"
            #self.putheader('TE', 'chunked')

            # ikiwa TE ni supplied kwenye the header, then it must appear kwenye a
            # Connection header.
            #self.putheader('Connection', 'TE')

        isipokua:
            # For HTTP/1.0, the server will assume "sio chunked"
            pita

    eleza _encode_request(self, request):
        # ASCII also helps prevent CVE-2019-9740.
        rudisha request.encode('ascii')

    eleza _validate_path(self, url):
        """Validate a url kila putrequest."""
        # Prevent CVE-2019-9740.
        match = _contains_disallowed_url_pchar_re.search(url)
        ikiwa match:
            ashiria InvalidURL(f"URL can't contain control characters. {url!r} "
                             f"(found at least {match.group()!r})")

    eleza putheader(self, header, *values):
        """Send a request header line to the server.

        For example: h.putheader('Accept', 'text/html')
        """
        ikiwa self.__state != _CS_REQ_STARTED:
            ashiria CannotSendHeader()

        ikiwa hasattr(header, 'encode'):
            header = header.encode('ascii')

        ikiwa sio _is_legal_header_name(header):
            ashiria ValueError('Invalid header name %r' % (header,))

        values = list(values)
        kila i, one_value kwenye enumerate(values):
            ikiwa hasattr(one_value, 'encode'):
                values[i] = one_value.encode('latin-1')
            lasivyo isinstance(one_value, int):
                values[i] = str(one_value).encode('ascii')

            ikiwa _is_illegal_header_value(values[i]):
                ashiria ValueError('Invalid header value %r' % (values[i],))

        value = b'\r\n\t'.join(values)
        header = header + b': ' + value
        self._output(header)

    eleza endheaders(self, message_body=Tupu, *, encode_chunked=Uongo):
        """Indicate that the last header line has been sent to the server.

        This method sends the request to the server.  The optional message_body
        argument can be used to pita a message body associated ukijumuisha the
        request.
        """
        ikiwa self.__state == _CS_REQ_STARTED:
            self.__state = _CS_REQ_SENT
        isipokua:
            ashiria CannotSendHeader()
        self._send_output(message_body, encode_chunked=encode_chunked)

    eleza request(self, method, url, body=Tupu, headers={}, *,
                encode_chunked=Uongo):
        """Send a complete request to the server."""
        self._send_request(method, url, body, headers, encode_chunked)

    eleza _send_request(self, method, url, body, headers, encode_chunked):
        # Honor explicitly requested Host: na Accept-Encoding: headers.
        header_names = frozenset(k.lower() kila k kwenye headers)
        skips = {}
        ikiwa 'host' kwenye header_names:
            skips['skip_host'] = 1
        ikiwa 'accept-encoding' kwenye header_names:
            skips['skip_accept_encoding'] = 1

        self.putrequest(method, url, **skips)

        # chunked encoding will happen ikiwa HTTP/1.1 ni used na either
        # the caller pitaes encode_chunked=Kweli ama the following
        # conditions hold:
        # 1. content-length has sio been explicitly set
        # 2. the body ni a file ama iterable, but sio a str ama bytes-like
        # 3. Transfer-Encoding has NOT been explicitly set by the caller

        ikiwa 'content-length' haiko kwenye header_names:
            # only chunk body ikiwa sio explicitly set kila backwards
            # compatibility, assuming the client code ni already handling the
            # chunking
            ikiwa 'transfer-encoding' haiko kwenye header_names:
                # ikiwa content-length cansio be automatically determined, fall
                # back to chunked encoding
                encode_chunked = Uongo
                content_length = self._get_content_length(body, method)
                ikiwa content_length ni Tupu:
                    ikiwa body ni sio Tupu:
                        ikiwa self.debuglevel > 0:
                            andika('Unable to determine size of %r' % body)
                        encode_chunked = Kweli
                        self.putheader('Transfer-Encoding', 'chunked')
                isipokua:
                    self.putheader('Content-Length', str(content_length))
        isipokua:
            encode_chunked = Uongo

        kila hdr, value kwenye headers.items():
            self.putheader(hdr, value)
        ikiwa isinstance(body, str):
            # RFC 2616 Section 3.7.1 says that text default has a
            # default charset of iso-8859-1.
            body = _encode(body, 'body')
        self.endheaders(body, encode_chunked=encode_chunked)

    eleza getresponse(self):
        """Get the response kutoka the server.

        If the HTTPConnection ni kwenye the correct state, returns an
        instance of HTTPResponse ama of whatever object ni returned by
        the response_class variable.

        If a request has sio been sent ama ikiwa a previous response has
        sio be handled, ResponseNotReady ni raised.  If the HTTP
        response indicates that the connection should be closed, then
        it will be closed before the response ni returned.  When the
        connection ni closed, the underlying socket ni closed.
        """

        # ikiwa a prior response has been completed, then forget about it.
        ikiwa self.__response na self.__response.isclosed():
            self.__response = Tupu

        # ikiwa a prior response exists, then it must be completed (otherwise, we
        # cansio read this response's header to determine the connection-close
        # behavior)
        #
        # note: ikiwa a prior response existed, but was connection-close, then the
        # socket na response were made independent of this HTTPConnection
        # object since a new request requires that we open a whole new
        # connection
        #
        # this means the prior response had one of two states:
        #   1) will_close: this connection was reset na the prior socket na
        #                  response operate independently
        #   2) persistent: the response was retained na we await its
        #                  isclosed() status to become true.
        #
        ikiwa self.__state != _CS_REQ_SENT ama self.__response:
            ashiria ResponseNotReady(self.__state)

        ikiwa self.debuglevel > 0:
            response = self.response_class(self.sock, self.debuglevel,
                                           method=self._method)
        isipokua:
            response = self.response_class(self.sock, method=self._method)

        jaribu:
            jaribu:
                response.begin()
            tatizo ConnectionError:
                self.close()
                raise
            assert response.will_close != _UNKNOWN
            self.__state = _CS_IDLE

            ikiwa response.will_close:
                # this effectively pitaes the connection to the response
                self.close()
            isipokua:
                # remember this, so we can tell when it ni complete
                self.__response = response

            rudisha response
        tatizo:
            response.close()
            raise

jaribu:
    agiza ssl
tatizo ImportError:
    pita
isipokua:
    kundi HTTPSConnection(HTTPConnection):
        "This kundi allows communication via SSL."

        default_port = HTTPS_PORT

        # XXX Should key_file na cert_file be deprecated kwenye favour of context?

        eleza __init__(self, host, port=Tupu, key_file=Tupu, cert_file=Tupu,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     source_address=Tupu, *, context=Tupu,
                     check_hostname=Tupu, blocksize=8192):
            super(HTTPSConnection, self).__init__(host, port, timeout,
                                                  source_address,
                                                  blocksize=blocksize)
            ikiwa (key_file ni sio Tupu ama cert_file ni sio Tupu ama
                        check_hostname ni sio Tupu):
                agiza warnings
                warnings.warn("key_file, cert_file na check_hostname are "
                              "deprecated, use a custom context instead.",
                              DeprecationWarning, 2)
            self.key_file = key_file
            self.cert_file = cert_file
            ikiwa context ni Tupu:
                context = ssl._create_default_https_context()
                # enable PHA kila TLS 1.3 connections ikiwa available
                ikiwa context.post_handshake_auth ni sio Tupu:
                    context.post_handshake_auth = Kweli
            will_verify = context.verify_mode != ssl.CERT_NONE
            ikiwa check_hostname ni Tupu:
                check_hostname = context.check_hostname
            ikiwa check_hostname na sio will_verify:
                ashiria ValueError("check_hostname needs a SSL context ukijumuisha "
                                 "either CERT_OPTIONAL ama CERT_REQUIRED")
            ikiwa key_file ama cert_file:
                context.load_cert_chain(cert_file, key_file)
                # cert na key file means the user wants to authenticate.
                # enable TLS 1.3 PHA implicitly even kila custom contexts.
                ikiwa context.post_handshake_auth ni sio Tupu:
                    context.post_handshake_auth = Kweli
            self._context = context
            ikiwa check_hostname ni sio Tupu:
                self._context.check_hostname = check_hostname

        eleza connect(self):
            "Connect to a host on a given (SSL) port."

            super().connect()

            ikiwa self._tunnel_host:
                server_hostname = self._tunnel_host
            isipokua:
                server_hostname = self.host

            self.sock = self._context.wrap_socket(self.sock,
                                                  server_hostname=server_hostname)

    __all__.append("HTTPSConnection")

kundi HTTPException(Exception):
    # Subclasses that define an __init__ must call Exception.__init__
    # ama define self.args.  Otherwise, str() will fail.
    pita

kundi NotConnected(HTTPException):
    pita

kundi InvalidURL(HTTPException):
    pita

kundi UnknownProtocol(HTTPException):
    eleza __init__(self, version):
        self.args = version,
        self.version = version

kundi UnknownTransferEncoding(HTTPException):
    pita

kundi UnimplementedFileMode(HTTPException):
    pita

kundi IncompleteRead(HTTPException):
    eleza __init__(self, partial, expected=Tupu):
        self.args = partial,
        self.partial = partial
        self.expected = expected
    eleza __repr__(self):
        ikiwa self.expected ni sio Tupu:
            e = ', %i more expected' % self.expected
        isipokua:
            e = ''
        rudisha '%s(%i bytes read%s)' % (self.__class__.__name__,
                                        len(self.partial), e)
    __str__ = object.__str__

kundi ImproperConnectionState(HTTPException):
    pita

kundi CannotSendRequest(ImproperConnectionState):
    pita

kundi CannotSendHeader(ImproperConnectionState):
    pita

kundi ResponseNotReady(ImproperConnectionState):
    pita

kundi BadStatusLine(HTTPException):
    eleza __init__(self, line):
        ikiwa sio line:
            line = repr(line)
        self.args = line,
        self.line = line

kundi LineTooLong(HTTPException):
    eleza __init__(self, line_type):
        HTTPException.__init__(self, "got more than %d bytes when reading %s"
                                     % (_MAXLINE, line_type))

kundi RemoteDisconnected(ConnectionResetError, BadStatusLine):
    eleza __init__(self, *pos, **kw):
        BadStatusLine.__init__(self, "")
        ConnectionResetError.__init__(self, *pos, **kw)

# kila backwards compatibility
error = HTTPException
