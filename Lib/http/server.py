"""HTTP server classes.

Note: BaseHTTPRequestHandler doesn't implement any HTTP request; see
SimpleHTTPRequestHandler kila simple implementations of GET, HEAD na POST,
and CGIHTTPRequestHandler kila CGI scripts.

It does, however, optionally implement HTTP/1.1 persistent connections,
as of version 0.3.

Notes on CGIHTTPRequestHandler
------------------------------

This kundi implements GET na POST requests to cgi-bin scripts.

If the os.fork() function ni sio present (e.g. on Windows),
subprocess.Popen() ni used kama a fallback, ukijumuisha slightly altered semantics.

In all cases, the implementation ni intentionally naive -- all
requests are executed synchronously.

SECURITY WARNING: DON'T USE THIS CODE UNLESS YOU ARE INSIDE A FIREWALL
-- it may execute arbitrary Python code ama external programs.

Note that status code 200 ni sent prior to execution of a CGI script, so
scripts cannot send other status codes such kama 302 (redirect).

XXX To do:

- log requests even later (to capture byte count)
- log user-agent header na other interesting goodies
- send error log to separate file
"""


# See also:
#
# HTTP Working Group                                        T. Berners-Lee
# INTERNET-DRAFT                                            R. T. Fielding
# <draft-ietf-http-v10-spec-00.txt>                     H. Frystyk Nielsen
# Expires September 8, 1995                                  March 8, 1995
#
# URL: http://www.ics.uci.edu/pub/ietf/http/draft-ietf-http-v10-spec-00.txt
#
# na
#
# Network Working Group                                      R. Fielding
# Request kila Comments: 2616                                       et al
# Obsoletes: 2068                                              June 1999
# Category: Standards Track
#
# URL: http://www.faqs.org/rfcs/rfc2616.html

# Log files
# ---------
#
# Here's a quote kutoka the NCSA httpd docs about log file format.
#
# | The logfile format ni kama follows. Each line consists of:
# |
# | host rfc931 authuser [DD/Mon/YYYY:hh:mm:ss] "request" ddd bbbb
# |
# |        host: Either the DNS name ama the IP number of the remote client
# |        rfc931: Any information rudishaed by identd kila this person,
# |                - otherwise.
# |        authuser: If user sent a userid kila authentication, the user name,
# |                  - otherwise.
# |        DD: Day
# |        Mon: Month (calendar name)
# |        YYYY: Year
# |        hh: hour (24-hour format, the machine's timezone)
# |        mm: minutes
# |        ss: seconds
# |        request: The first line of the HTTP request kama sent by the client.
# |        ddd: the status code rudishaed by the server, - ikiwa sio available.
# |        bbbb: the total number of bytes sent,
# |              *not including the HTTP/1.0 header*, - ikiwa sio available
# |
# | You can determine the name of the file accessed through request.
#
# (Actually, the latter ni only true ikiwa you know the server configuration
# at the time the request was made!)

__version__ = "0.6"

__all__ = [
    "HTTPServer", "ThreadingHTTPServer", "BaseHTTPRequestHandler",
    "SimpleHTTPRequestHandler", "CGIHTTPRequestHandler",
]

agiza copy
agiza datetime
agiza email.utils
agiza html
agiza http.client
agiza io
agiza mimetypes
agiza os
agiza posixpath
agiza select
agiza shutil
agiza socket # For gethostbyaddr()
agiza socketserver
agiza sys
agiza time
agiza urllib.parse
kutoka functools agiza partial

kutoka http agiza HTTPStatus


# Default error message template
DEFAULT_ERROR_MESSAGE = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: %(code)d</p>
        <p>Message: %(message)s.</p>
        <p>Error code explanation: %(code)s - %(explain)s.</p>
    </body>
</html>
"""

DEFAULT_ERROR_CONTENT_TYPE = "text/html;charset=utf-8"

kundi HTTPServer(socketserver.TCPServer):

    allow_reuse_address = 1    # Seems to make sense kwenye testing environment

    eleza server_bind(self):
        """Override server_bind to store the server name."""
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port


kundi ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = Kweli


kundi BaseHTTPRequestHandler(socketserver.StreamRequestHandler):

    """HTTP request handler base class.

    The following explanation of HTTP serves to guide you through the
    code kama well kama to expose any misunderstandings I may have about
    HTTP (so you don't need to read the code to figure out I'm wrong
    :-).

    HTTP (HyperText Transfer Protocol) ni an extensible protocol on
    top of a reliable stream transport (e.g. TCP/IP).  The protocol
    recognizes three parts to a request:

    1. One line identifying the request type na path
    2. An optional set of RFC-822-style headers
    3. An optional data part

    The headers na data are separated by a blank line.

    The first line of the request has the form

    <command> <path> <version>

    where <command> ni a (case-sensitive) keyword such kama GET ama POST,
    <path> ni a string containing path information kila the request,
    na <version> should be the string "HTTP/1.0" ama "HTTP/1.1".
    <path> ni encoded using the URL encoding scheme (using %xx to signify
    the ASCII character ukijumuisha hex code xx).

    The specification specifies that lines are separated by CRLF but
    kila compatibility ukijumuisha the widest range of clients recommends
    servers also handle LF.  Similarly, whitespace kwenye the request line
    ni treated sensibly (allowing multiple spaces between components
    na allowing trailing whitespace).

    Similarly, kila output, lines ought to be separated by CRLF pairs
    but most clients grok LF characters just fine.

    If the first line of the request has the form

    <command> <path>

    (i.e. <version> ni left out) then this ni assumed to be an HTTP
    0.9 request; this form has no optional headers na data part na
    the reply consists of just the data.

    The reply form of the HTTP 1.x protocol again has three parts:

    1. One line giving the response code
    2. An optional set of RFC-822-style headers
    3. The data

    Again, the headers na data are separated by a blank line.

    The response code line has the form

    <version> <responsecode> <responsestring>

    where <version> ni the protocol version ("HTTP/1.0" ama "HTTP/1.1"),
    <responsecode> ni a 3-digit response code indicating success ama
    failure of the request, na <responsestring> ni an optional
    human-readable string explaining what the response code means.

    This server parses the request na the headers, na then calls a
    function specific to the request type (<command>).  Specifically,
    a request SPAM will be handled by a method do_SPAM().  If no
    such method exists the server sends an error response to the
    client.  If it exists, it ni called ukijumuisha no arguments:

    do_SPAM()

    Note that the request name ni case sensitive (i.e. SPAM na spam
    are different requests).

    The various request details are stored kwenye instance variables:

    - client_address ni the client IP address kwenye the form (host,
    port);

    - command, path na version are the broken-down request line;

    - headers ni an instance of email.message.Message (or a derived
    class) containing the header information;

    - rfile ni a file object open kila reading positioned at the
    start of the optional input data part;

    - wfile ni a file object open kila writing.

    IT IS IMPORTANT TO ADHERE TO THE PROTOCOL FOR WRITING!

    The first thing to be written must be the response line.  Then
    follow 0 ama more header lines, then a blank line, na then the
    actual data (ikiwa any).  The meaning of the header lines depends on
    the command executed by the server; kwenye most cases, when data is
    rudishaed, there should be at least one header line of the form

    Content-type: <type>/<subtype>

    where <type> na <subtype> should be registered MIME types,
    e.g. "text/html" ama "text/plain".

    """

    # The Python system version, truncated to its first component.
    sys_version = "Python/" + sys.version.split()[0]

    # The server software version.  You may want to override this.
    # The format ni multiple whitespace-separated strings,
    # where each string ni of the form name[/version].
    server_version = "BaseHTTP/" + __version__

    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE

    # The default request version.  This only affects responses up until
    # the point where the request line ni parsed, so it mainly decides what
    # the client gets back when sending a malformed request line.
    # Most web servers default to HTTP 0.9, i.e. don't send a status line.
    default_request_version = "HTTP/0.9"

    eleza parse_request(self):
        """Parse a request (internal).

        The request should be stored kwenye self.raw_requestline; the results
        are kwenye self.command, self.path, self.request_version na
        self.headers.

        Return Kweli kila success, Uongo kila failure; on failure, any relevant
        error response has already been sent back.

        """
        self.command = Tupu  # set kwenye case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = Kweli
        requestline = str(self.raw_requestline, 'iso-8859-1')
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()
        ikiwa len(words) == 0:
            rudisha Uongo

        ikiwa len(words) >= 3:  # Enough to determine protocol version
            version = words[-1]
            jaribu:
                ikiwa sio version.startswith('HTTP/'):
                    ashiria ValueError
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split(".")
                # RFC 2145 section 3.1 says there can be only one "." na
                #   - major na minor numbers MUST be treated as
                #      separate integers;
                #   - HTTP/2.4 ni a lower version than HTTP/2.13, which in
                #      turn ni lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                ikiwa len(version_number) != 2:
                    ashiria ValueError
                version_number = int(version_number[0]), int(version_number[1])
            tatizo (ValueError, IndexError):
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad request version (%r)" % version)
                rudisha Uongo
            ikiwa version_number >= (1, 1) na self.protocol_version >= "HTTP/1.1":
                self.close_connection = Uongo
            ikiwa version_number >= (2, 0):
                self.send_error(
                    HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    "Invalid HTTP version (%s)" % base_version_number)
                rudisha Uongo
            self.request_version = version

        ikiwa sio 2 <= len(words) <= 3:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Bad request syntax (%r)" % requestline)
            rudisha Uongo
        command, path = words[:2]
        ikiwa len(words) == 2:
            self.close_connection = Kweli
            ikiwa command != 'GET':
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad HTTP/0.9 request type (%r)" % command)
                rudisha Uongo
        self.command, self.path = command, path

        # Examine the headers na look kila a Connection directive.
        jaribu:
            self.headers = http.client.parse_headers(self.rfile,
                                                     _class=self.MessageClass)
        tatizo http.client.LineTooLong kama err:
            self.send_error(
                HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                "Line too long",
                str(err))
            rudisha Uongo
        tatizo http.client.HTTPException kama err:
            self.send_error(
                HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                "Too many headers",
                str(err)
            )
            rudisha Uongo

        conntype = self.headers.get('Connection', "")
        ikiwa conntype.lower() == 'close':
            self.close_connection = Kweli
        lasivyo (conntype.lower() == 'keep-alive' na
              self.protocol_version >= "HTTP/1.1"):
            self.close_connection = Uongo
        # Examine the headers na look kila an Expect directive
        expect = self.headers.get('Expect', "")
        ikiwa (expect.lower() == "100-endelea" na
                self.protocol_version >= "HTTP/1.1" na
                self.request_version >= "HTTP/1.1"):
            ikiwa sio self.handle_expect_100():
                rudisha Uongo
        rudisha Kweli

    eleza handle_expect_100(self):
        """Decide what to do ukijumuisha an "Expect: 100-endelea" header.

        If the client ni expecting a 100 Continue response, we must
        respond ukijumuisha either a 100 Continue ama a final response before
        waiting kila the request body. The default ni to always respond
        ukijumuisha a 100 Continue. You can behave differently (kila example,
        reject unauthorized requests) by overriding this method.

        This method should either rudisha Kweli (possibly after sending
        a 100 Continue response) ama send an error response na rudisha
        Uongo.

        """
        self.send_response_only(HTTPStatus.CONTINUE)
        self.end_headers()
        rudisha Kweli

    eleza handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string kila information on how to handle specific HTTP
        commands such kama GET na POST.

        """
        jaribu:
            self.raw_requestline = self.rfile.readline(65537)
            ikiwa len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                rudisha
            ikiwa sio self.raw_requestline:
                self.close_connection = Kweli
                rudisha
            ikiwa sio self.parse_request():
                # An error code has been sent, just exit
                rudisha
            mname = 'do_' + self.command
            ikiwa sio hasattr(self, mname):
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Unsupported method (%r)" % self.command)
                rudisha
            method = getattr(self, mname)
            method()
            self.wfile.flush() #actually send the response ikiwa sio already done.
        tatizo socket.timeout kama e:
            #a read ama a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = Kweli
            rudisha

    eleza handle(self):
        """Handle multiple requests ikiwa necessary."""
        self.close_connection = Kweli

        self.handle_one_request()
        wakati sio self.close_connection:
            self.handle_one_request()

    eleza send_error(self, code, message=Tupu, explain=Tupu):
        """Send na log an error reply.

        Arguments are
        * code:    an HTTP error code
                   3 digits
        * message: a simple optional 1 line reason phrase.
                   *( HTAB / SP / VCHAR / %x80-FF )
                   defaults to short entry matching the response code
        * explain: a detailed message defaults to the long entry
                   matching the response code.

        This sends an error response (so it must be called before any
        output has been generated), logs the error, na finally sends
        a piece of HTML explaining the error to the user.

        """

        jaribu:
            shortmsg, longmsg = self.responses[code]
        tatizo KeyError:
            shortmsg, longmsg = '???', '???'
        ikiwa message ni Tupu:
            message = shortmsg
        ikiwa explain ni Tupu:
            explain = longmsg
        self.log_error("code %d, message %s", code, message)
        self.send_response(code, message)
        self.send_header('Connection', 'close')

        # Message body ni omitted kila cases described in:
        #  - RFC7230: 3.3. 1xx, 204(No Content), 304(Not Modified)
        #  - RFC7231: 6.3.6. 205(Reset Content)
        body = Tupu
        ikiwa (code >= 200 na
            code haiko kwenye (HTTPStatus.NO_CONTENT,
                         HTTPStatus.RESET_CONTENT,
                         HTTPStatus.NOT_MODIFIED)):
            # HTML encode to prevent Cross Site Scripting attacks
            # (see bug #1100201)
            content = (self.error_message_format % {
                'code': code,
                'message': html.escape(message, quote=Uongo),
                'explain': html.escape(explain, quote=Uongo)
            })
            body = content.encode('UTF-8', 'replace')
            self.send_header("Content-Type", self.error_content_type)
            self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        ikiwa self.command != 'HEAD' na body:
            self.wfile.write(body)

    eleza send_response(self, code, message=Tupu):
        """Add the response header to the headers buffer na log the
        response code.

        Also send two standard headers ukijumuisha the server software
        version na the current date.

        """
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    eleza send_response_only(self, code, message=Tupu):
        """Send the response header only."""
        ikiwa self.request_version != 'HTTP/0.9':
            ikiwa message ni Tupu:
                ikiwa code kwenye self.responses:
                    message = self.responses[code][0]
                isipokua:
                    message = ''
            ikiwa sio hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(("%s %d %s\r\n" %
                    (self.protocol_version, code, message)).encode(
                        'latin-1', 'strict'))

    eleza send_header(self, keyword, value):
        """Send a MIME header to the headers buffer."""
        ikiwa self.request_version != 'HTTP/0.9':
            ikiwa sio hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(
                ("%s: %s\r\n" % (keyword, value)).encode('latin-1', 'strict'))

        ikiwa keyword.lower() == 'connection':
            ikiwa value.lower() == 'close':
                self.close_connection = Kweli
            lasivyo value.lower() == 'keep-alive':
                self.close_connection = Uongo

    eleza end_headers(self):
        """Send the blank line ending the MIME headers."""
        ikiwa self.request_version != 'HTTP/0.9':
            self._headers_buffer.append(b"\r\n")
            self.flush_headers()

    eleza flush_headers(self):
        ikiwa hasattr(self, '_headers_buffer'):
            self.wfile.write(b"".join(self._headers_buffer))
            self._headers_buffer = []

    eleza log_request(self, code='-', size='-'):
        """Log an accepted request.

        This ni called by send_response().

        """
        ikiwa isinstance(code, HTTPStatus):
            code = code.value
        self.log_message('"%s" %s %s',
                         self.requestline, str(code), str(size))

    eleza log_error(self, format, *args):
        """Log an error.

        This ni called when a request cannot be fulfilled.  By
        default it pitaes the message on to log_message().

        Arguments are the same kama kila log_message().

        XXX This should go to the separate error log.

        """

        self.log_message(format, *args)

    eleza log_message(self, format, *args):
        """Log an arbitrary message.

        This ni used by all other logging functions.  Override
        it ikiwa you have specific logging wishes.

        The first argument, FORMAT, ni a format string kila the
        message to be logged.  If the format string contains
        any % escapes requiring parameters, they should be
        specified kama subsequent arguments (it's just like
        printf!).

        The client ip na current date/time are prefixed to
        every message.

        """

        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

    eleza version_string(self):
        """Return the server software version string."""
        rudisha self.server_version + ' ' + self.sys_version

    eleza date_time_string(self, timestamp=Tupu):
        """Return the current date na time formatted kila a message header."""
        ikiwa timestamp ni Tupu:
            timestamp = time.time()
        rudisha email.utils.formatdate(timestamp, usegmt=Kweli)

    eleza log_date_time_string(self):
        """Return the current time formatted kila logging."""
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (
                day, self.monthname[month], year, hh, mm, ss)
        rudisha s

    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [Tupu,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    eleza address_string(self):
        """Return the client address."""

        rudisha self.client_address[0]

    # Essentially static kundi variables

    # The version of the HTTP protocol we support.
    # Set this to HTTP/1.1 to enable automatic keepalive
    protocol_version = "HTTP/1.0"

    # MessageClass used to parse headers
    MessageClass = http.client.HTTPMessage

    # hack to maintain backwards compatibility
    responses = {
        v: (v.phrase, v.description)
        kila v kwenye HTTPStatus.__members__.values()
    }


kundi SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    """Simple HTTP request handler ukijumuisha GET na HEAD commands.

    This serves files kutoka the current directory na any of its
    subdirectories.  The MIME type kila files ni determined by
    calling the .guess_type() method.

    The GET na HEAD requests are identical tatizo that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "SimpleHTTP/" + __version__

    eleza __init__(self, *args, directory=Tupu, **kwargs):
        ikiwa directory ni Tupu:
            directory = os.getcwd()
        self.directory = directory
        super().__init__(*args, **kwargs)

    eleza do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        ikiwa f:
            jaribu:
                self.copyfile(f, self.wfile)
            mwishowe:
                f.close()

    eleza do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        ikiwa f:
            f.close()

    eleza send_head(self):
        """Common code kila GET na HEAD commands.

        This sends the response code na MIME headers.

        Return value ni either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        na must be closed by the caller under all circumstances), ama
        Tupu, kwenye which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = Tupu
        ikiwa os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            ikiwa sio parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                rudisha Tupu
            kila index kwenye "index.html", "index.htm":
                index = os.path.join(path, index)
                ikiwa os.path.exists(index):
                    path = index
                    koma
            isipokua:
                rudisha self.list_directory(path)
        ctype = self.guess_type(path)
        # check kila trailing "/" which should rudisha 404. See Issue17324
        # The test kila this was added kwenye test_httpserver.py
        # However, some OS platforms accept a trailingSlash kama a filename
        # See discussion on python-dev na Issue34711 regarding
        # parseing na rejection of filenames ukijumuisha a trailing slash
        ikiwa path.endswith("/"):
            self.send_error(HTTPStatus.NOT_FOUND, "File sio found")
            rudisha Tupu
        jaribu:
            f = open(path, 'rb')
        tatizo OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File sio found")
            rudisha Tupu

        jaribu:
            fs = os.fstat(f.fileno())
            # Use browser cache ikiwa possible
            ikiwa ("If-Modified-Since" kwenye self.headers
                    na "If-Tupu-Match" haiko kwenye self.headers):
                # compare If-Modified-Since na time of last file modification
                jaribu:
                    ims = email.utils.parsedate_to_datetime(
                        self.headers["If-Modified-Since"])
                tatizo (TypeError, IndexError, OverflowError, ValueError):
                    # ignore ill-formed values
                    pita
                isipokua:
                    ikiwa ims.tzinfo ni Tupu:
                        # obsolete format ukijumuisha no timezone, cf.
                        # https://tools.ietf.org/html/rfc7231#section-7.1.1.1
                        ims = ims.replace(tzinfo=datetime.timezone.utc)
                    ikiwa ims.tzinfo ni datetime.timezone.utc:
                        # compare to UTC datetime of last modification
                        last_modikiwa = datetime.datetime.kutokatimestamp(
                            fs.st_mtime, datetime.timezone.utc)
                        # remove microseconds, like kwenye If-Modified-Since
                        last_modikiwa = last_modif.replace(microsecond=0)

                        ikiwa last_modikiwa <= ims:
                            self.send_response(HTTPStatus.NOT_MODIFIED)
                            self.end_headers()
                            f.close()
                            rudisha Tupu

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified",
                self.date_time_string(fs.st_mtime))
            self.end_headers()
            rudisha f
        tatizo:
            f.close()
            ashiria

    eleza list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value ni either a file object, ama Tupu (indicating an
        error).  In either case, the headers are sent, making the
        interface the same kama kila send_head().

        """
        jaribu:
            list = os.listdir(path)
        tatizo OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No permission to list directory")
            rudisha Tupu
        list.sort(key=lambda a: a.lower())
        r = []
        jaribu:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepita')
        tatizo UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=Uongo)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing kila %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<ul>')
        kila name kwenye list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / kila directories ama @ kila symbolic links
            ikiwa os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            ikiwa os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays ukijumuisha @ na links ukijumuisha /
            r.append('<li><a href="%s">%s</a></li>'
                    % (urllib.parse.quote(linkname,
                                          errors='surrogatepita'),
                       html.escape(displayname, quote=Uongo)))
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        rudisha f

    eleza translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive ama directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        jaribu:
            path = urllib.parse.unquote(path, errors='surrogatepita')
        tatizo UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(Tupu, words)
        path = self.directory
        kila word kwenye words:
            ikiwa os.path.dirname(word) ama word kwenye (os.curdir, os.pardir):
                # Ignore components that are sio a simple file/directory name
                endelea
            path = os.path.join(path, word)
        ikiwa trailing_slash:
            path += '/'
        rudisha path

    eleza copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument ni a file object open kila reading
        (or anything ukijumuisha a read() method) na the DESTINATION
        argument ni a file object open kila writing (or
        anything ukijumuisha a write() method).

        The only reason kila overriding this would be to change
        the block size ama perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data kama well.

        """
        shutil.copyfileobj(source, outputfile)

    eleza guess_type(self, path):
        """Guess the type of a file.

        Argument ni a PATH (a filename).

        Return value ni a string of the form type/subtype,
        usable kila a MIME Content-type header.

        The default implementation looks the file's extension
        up kwenye the table self.extensions_map, using application/octet-stream
        kama a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        ikiwa ext kwenye self.extensions_map:
            rudisha self.extensions_map[ext]
        ext = ext.lower()
        ikiwa ext kwenye self.extensions_map:
            rudisha self.extensions_map[ext]
        isipokua:
            rudisha self.extensions_map['']

    ikiwa sio mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


# Utilities kila CGIHTTPRequestHandler

eleza _url_collapse_path(path):
    """
    Given a URL path, remove extra '/'s na '.' path elements na collapse
    any '..' references na rudishas a collapsed path.

    Implements something akin to RFC-2396 5.2 step 6 to parse relative paths.
    The utility of this function ni limited to is_cgi method na helps
    preventing some security attacks.

    Returns: The reconstituted URL, which will always start ukijumuisha a '/'.

    Raises: IndexError ikiwa too many '..' occur within the path.

    """
    # Query component should sio be involved.
    path, _, query = path.partition('?')
    path = urllib.parse.unquote(path)

    # Similar to os.path.split(os.path.normpath(path)) but specific to URL
    # path semantics rather than local operating system semantics.
    path_parts = path.split('/')
    head_parts = []
    kila part kwenye path_parts[:-1]:
        ikiwa part == '..':
            head_parts.pop() # IndexError ikiwa more '..' than prior parts
        lasivyo part na part != '.':
            head_parts.append( part )
    ikiwa path_parts:
        tail_part = path_parts.pop()
        ikiwa tail_part:
            ikiwa tail_part == '..':
                head_parts.pop()
                tail_part = ''
            lasivyo tail_part == '.':
                tail_part = ''
    isipokua:
        tail_part = ''

    ikiwa query:
        tail_part = '?'.join((tail_part, query))

    splitpath = ('/' + '/'.join(head_parts), tail_part)
    collapsed_path = "/".join(splitpath)

    rudisha collapsed_path



nobody = Tupu

eleza nobody_uid():
    """Internal routine to get nobody's uid"""
    global nobody
    ikiwa nobody:
        rudisha nobody
    jaribu:
        agiza pwd
    tatizo ImportError:
        rudisha -1
    jaribu:
        nobody = pwd.getpwnam('nobody')[2]
    tatizo KeyError:
        nobody = 1 + max(x[2] kila x kwenye pwd.getpwall())
    rudisha nobody


eleza executable(path):
    """Test kila executable file."""
    rudisha os.access(path, os.X_OK)


kundi CGIHTTPRequestHandler(SimpleHTTPRequestHandler):

    """Complete HTTP server ukijumuisha GET, HEAD na POST commands.

    GET na HEAD also support running CGI scripts.

    The POST command ni *only* implemented kila CGI scripts.

    """

    # Determine platform specifics
    have_fork = hasattr(os, 'fork')

    # Make rfile unbuffered -- we need to read one line na then pita
    # the rest to a subprocess, so we can't use buffered input.
    rbufsize = 0

    eleza do_POST(self):
        """Serve a POST request.

        This ni only implemented kila CGI scripts.

        """

        ikiwa self.is_cgi():
            self.run_cgi()
        isipokua:
            self.send_error(
                HTTPStatus.NOT_IMPLEMENTED,
                "Can only POST to CGI scripts")

    eleza send_head(self):
        """Version of send_head that support CGI scripts"""
        ikiwa self.is_cgi():
            rudisha self.run_cgi()
        isipokua:
            rudisha SimpleHTTPRequestHandler.send_head(self)

    eleza is_cgi(self):
        """Test whether self.path corresponds to a CGI script.

        Returns Kweli na updates the cgi_info attribute to the tuple
        (dir, rest) ikiwa self.path requires running a CGI script.
        Returns Uongo otherwise.

        If any exception ni ashiriad, the caller should assume that
        self.path was rejected kama invalid na act accordingly.

        The default implementation tests whether the normalized url
        path begins ukijumuisha one of the strings kwenye self.cgi_directories
        (and the next character ni a '/' ama the end of the string).

        """
        collapsed_path = _url_collapse_path(self.path)
        dir_sep = collapsed_path.find('/', 1)
        head, tail = collapsed_path[:dir_sep], collapsed_path[dir_sep+1:]
        ikiwa head kwenye self.cgi_directories:
            self.cgi_info = head, tail
            rudisha Kweli
        rudisha Uongo


    cgi_directories = ['/cgi-bin', '/htbin']

    eleza is_executable(self, path):
        """Test whether argument path ni an executable file."""
        rudisha executable(path)

    eleza is_python(self, path):
        """Test whether argument path ni a Python script."""
        head, tail = os.path.splitext(path)
        rudisha tail.lower() kwenye (".py", ".pyw")

    eleza run_cgi(self):
        """Execute a CGI script."""
        dir, rest = self.cgi_info
        path = dir + '/' + rest
        i = path.find('/', len(dir)+1)
        wakati i >= 0:
            nextdir = path[:i]
            nextrest = path[i+1:]

            scriptdir = self.translate_path(nextdir)
            ikiwa os.path.isdir(scriptdir):
                dir, rest = nextdir, nextrest
                i = path.find('/', len(dir)+1)
            isipokua:
                koma

        # find an explicit query string, ikiwa present.
        rest, _, query = rest.partition('?')

        # dissect the part after the directory name into a script name &
        # a possible additional path, to be stored kwenye PATH_INFO.
        i = rest.find('/')
        ikiwa i >= 0:
            script, rest = rest[:i], rest[i:]
        isipokua:
            script, rest = rest, ''

        scriptname = dir + '/' + script
        scriptfile = self.translate_path(scriptname)
        ikiwa sio os.path.exists(scriptfile):
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No such CGI script (%r)" % scriptname)
            rudisha
        ikiwa sio os.path.isfile(scriptfile):
            self.send_error(
                HTTPStatus.FORBIDDEN,
                "CGI script ni sio a plain file (%r)" % scriptname)
            rudisha
        ispy = self.is_python(scriptname)
        ikiwa self.have_fork ama sio ispy:
            ikiwa sio self.is_executable(scriptfile):
                self.send_error(
                    HTTPStatus.FORBIDDEN,
                    "CGI script ni sio executable (%r)" % scriptname)
                rudisha

        # Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
        # XXX Much of the following could be prepared ahead of time!
        env = copy.deepcopy(os.environ)
        env['SERVER_SOFTWARE'] = self.version_string()
        env['SERVER_NAME'] = self.server.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['SERVER_PORT'] = str(self.server.server_port)
        env['REQUEST_METHOD'] = self.command
        uqrest = urllib.parse.unquote(rest)
        env['PATH_INFO'] = uqrest
        env['PATH_TRANSLATED'] = self.translate_path(uqrest)
        env['SCRIPT_NAME'] = scriptname
        ikiwa query:
            env['QUERY_STRING'] = query
        env['REMOTE_ADDR'] = self.client_address[0]
        authorization = self.headers.get("authorization")
        ikiwa authorization:
            authorization = authorization.split()
            ikiwa len(authorization) == 2:
                agiza base64, binascii
                env['AUTH_TYPE'] = authorization[0]
                ikiwa authorization[0].lower() == "basic":
                    jaribu:
                        authorization = authorization[1].encode('ascii')
                        authorization = base64.decodebytes(authorization).\
                                        decode('ascii')
                    tatizo (binascii.Error, UnicodeError):
                        pita
                    isipokua:
                        authorization = authorization.split(':')
                        ikiwa len(authorization) == 2:
                            env['REMOTE_USER'] = authorization[0]
        # XXX REMOTE_IDENT
        ikiwa self.headers.get('content-type') ni Tupu:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        isipokua:
            env['CONTENT_TYPE'] = self.headers['content-type']
        length = self.headers.get('content-length')
        ikiwa length:
            env['CONTENT_LENGTH'] = length
        referer = self.headers.get('referer')
        ikiwa referer:
            env['HTTP_REFERER'] = referer
        accept = []
        kila line kwenye self.headers.getallmatchingheaders('accept'):
            ikiwa line[:1] kwenye "\t\n\r ":
                accept.append(line.strip())
            isipokua:
                accept = accept + line[7:].split(',')
        env['HTTP_ACCEPT'] = ','.join(accept)
        ua = self.headers.get('user-agent')
        ikiwa ua:
            env['HTTP_USER_AGENT'] = ua
        co = filter(Tupu, self.headers.get_all('cookie', []))
        cookie_str = ', '.join(co)
        ikiwa cookie_str:
            env['HTTP_COOKIE'] = cookie_str
        # XXX Other HTTP_* headers
        # Since we're setting the env kwenye the parent, provide empty
        # values to override previously set values
        kila k kwenye ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH',
                  'HTTP_USER_AGENT', 'HTTP_COOKIE', 'HTTP_REFERER'):
            env.setdefault(k, "")

        self.send_response(HTTPStatus.OK, "Script output follows")
        self.flush_headers()

        decoded_query = query.replace('+', ' ')

        ikiwa self.have_fork:
            # Unix -- fork kama we should
            args = [script]
            ikiwa '=' haiko kwenye decoded_query:
                args.append(decoded_query)
            nobody = nobody_uid()
            self.wfile.flush() # Always flush before forking
            pid = os.fork()
            ikiwa pid != 0:
                # Parent
                pid, sts = os.waitpid(pid, 0)
                # throw away additional data [see bug #427345]
                wakati select.select([self.rfile], [], [], 0)[0]:
                    ikiwa sio self.rfile.read(1):
                        koma
                ikiwa sts:
                    self.log_error("CGI script exit status %#x", sts)
                rudisha
            # Child
            jaribu:
                jaribu:
                    os.setuid(nobody)
                tatizo OSError:
                    pita
                os.dup2(self.rfile.fileno(), 0)
                os.dup2(self.wfile.fileno(), 1)
                os.execve(scriptfile, args, env)
            tatizo:
                self.server.handle_error(self.request, self.client_address)
                os._exit(127)

        isipokua:
            # Non-Unix -- use subprocess
            agiza subprocess
            cmdline = [scriptfile]
            ikiwa self.is_python(scriptfile):
                interp = sys.executable
                ikiwa interp.lower().endswith("w.exe"):
                    # On Windows, use python.exe, sio pythonw.exe
                    interp = interp[:-5] + interp[-4:]
                cmdline = [interp, '-u'] + cmdline
            ikiwa '=' haiko kwenye query:
                cmdline.append(query)
            self.log_message("command: %s", subprocess.list2cmdline(cmdline))
            jaribu:
                nbytes = int(length)
            tatizo (TypeError, ValueError):
                nbytes = 0
            p = subprocess.Popen(cmdline,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env = env
                                 )
            ikiwa self.command.lower() == "post" na nbytes > 0:
                data = self.rfile.read(nbytes)
            isipokua:
                data = Tupu
            # throw away additional data [see bug #427345]
            wakati select.select([self.rfile._sock], [], [], 0)[0]:
                ikiwa sio self.rfile._sock.recv(1):
                    koma
            stdout, stderr = p.communicate(data)
            self.wfile.write(stdout)
            ikiwa stderr:
                self.log_error('%s', stderr)
            p.stderr.close()
            p.stdout.close()
            status = p.returncode
            ikiwa status:
                self.log_error("CGI script exit status %#x", status)
            isipokua:
                self.log_message("CGI script exited OK")


eleza _get_best_family(*address):
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    rudisha family, sockaddr


eleza test(HandlerClass=BaseHTTPRequestHandler,
         ServerClass=ThreadingHTTPServer,
         protocol="HTTP/1.0", port=8000, bind=Tupu):
    """Test the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the port argument).

    """
    ServerClass.address_family, addr = _get_best_family(bind, port)

    HandlerClass.protocol_version = protocol
    ukijumuisha ServerClass(addr, HandlerClass) kama httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f'[{host}]' ikiwa ':' kwenye host isipokua host
        andika(
            f"Serving HTTP on {host} port {port} "
            f"(http://{url_host}:{port}/) ..."
        )
        jaribu:
            httpd.serve_forever()
        tatizo KeyboardInterrupt:
            andika("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

ikiwa __name__ == '__main__':
    agiza argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--cgi', action='store_true',
                       help='Run kama CGI Server')
    parser.add_argument('--bind', '-b', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('--directory', '-d', default=os.getcwd(),
                        help='Specify alternative directory '
                        '[default:current directory]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    ikiwa args.cgi:
        handler_kundi = CGIHTTPRequestHandler
    isipokua:
        handler_kundi = partial(SimpleHTTPRequestHandler,
                                directory=args.directory)
    test(HandlerClass=handler_class, port=args.port, bind=args.bind)
