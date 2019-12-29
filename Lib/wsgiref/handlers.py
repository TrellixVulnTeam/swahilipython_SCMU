"""Base classes kila server/gateway implementations"""

kutoka .util agiza FileWrapper, guess_scheme, is_hop_by_hop
kutoka .headers agiza Headers

agiza sys, os, time

__all__ = [
    'BaseHandler', 'SimpleHandler', 'BaseCGIHandler', 'CGIHandler',
    'IISCGIHandler', 'read_environ'
]

# Weekday na month names kila HTTP date/time formatting; always English!
_weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_monthname = [Tupu, # Dummy so we can use 1-based month numbers
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

eleza format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    rudisha "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        _weekdayname[wd], day, _monthname[month], year, hh, mm, ss
    )

_is_request = {
    'SCRIPT_NAME', 'PATH_INFO', 'QUERY_STRING', 'REQUEST_METHOD', 'AUTH_TYPE',
    'CONTENT_TYPE', 'CONTENT_LENGTH', 'HTTPS', 'REMOTE_USER', 'REMOTE_IDENT',
}.__contains__

eleza _needs_transcode(k):
    rudisha _is_request(k) ama k.startswith('HTTP_') ama k.startswith('SSL_') \
        ama (k.startswith('REDIRECT_') na _needs_transcode(k[9:]))

eleza read_environ():
    """Read environment, fixing HTTP variables"""
    enc = sys.getfilesystemencoding()
    esc = 'surrogateescape'
    jaribu:
        ''.encode('utf-8', esc)
    tatizo LookupError:
        esc = 'replace'
    environ = {}

    # Take the basic environment kutoka native-unicode os.environ. Attempt to
    # fix up the variables that come kutoka the HTTP request to compensate for
    # the bytes->unicode decoding step that will already have taken place.
    kila k, v kwenye os.environ.items():
        ikiwa _needs_transcode(k):

            # On win32, the os.environ ni natively Unicode. Different servers
            # decode the request bytes using different encodings.
            ikiwa sys.platform == 'win32':
                software = os.environ.get('SERVER_SOFTWARE', '').lower()

                # On IIS, the HTTP request will be decoded kama UTF-8 kama long
                # kama the input ni a valid UTF-8 sequence. Otherwise it is
                # decoded using the system code page (mbcs), ukijumuisha no way to
                # detect this has happened. Because UTF-8 ni the more likely
                # encoding, na mbcs ni inherently unreliable (an mbcs string
                # that happens to be valid UTF-8 will sio be decoded kama mbcs)
                # always recreate the original bytes kama UTF-8.
                ikiwa software.startswith('microsoft-iis/'):
                    v = v.encode('utf-8').decode('iso-8859-1')

                # Apache mod_cgi writes bytes-as-unicode (as ikiwa ISO-8859-1) direct
                # to the Unicode environ. No modification needed.
                lasivyo software.startswith('apache/'):
                    pita

                # Python 3's http.server.CGIHTTPRequestHandler decodes
                # using the urllib.unquote default of UTF-8, amongst other
                # issues.
                lasivyo (
                    software.startswith('simplehttp/')
                    na 'python/3' kwenye software
                ):
                    v = v.encode('utf-8').decode('iso-8859-1')

                # For other servers, guess that they have written bytes to
                # the environ using stdio byte-oriented interfaces, ending up
                # ukijumuisha the system code page.
                isipokua:
                    v = v.encode(enc, 'replace').decode('iso-8859-1')

            # Recover bytes kutoka unicode environ, using surrogate escapes
            # where available (Python 3.1+).
            isipokua:
                v = v.encode(enc, esc).decode('iso-8859-1')

        environ[k] = v
    rudisha environ


kundi BaseHandler:
    """Manage the invocation of a WSGI application"""

    # Configuration parameters; can override per-subkundi ama per-instance
    wsgi_version = (1,0)
    wsgi_multithread = Kweli
    wsgi_multiprocess = Kweli
    wsgi_run_once = Uongo

    origin_server = Kweli    # We are transmitting direct to client
    http_version  = "1.0"   # Version that should be used kila response
    server_software = Tupu  # String name of server software, ikiwa any

    # os_environ ni used to supply configuration kutoka the OS environment:
    # by default it's a copy of 'os.environ' kama of agiza time, but you can
    # override this kwenye e.g. your __init__ method.
    os_environ= read_environ()

    # Collaborator classes
    wsgi_file_wrapper = FileWrapper     # set to Tupu to disable
    headers_kundi = Headers             # must be a Headers-like class

    # Error handling (also per-subkundi ama per-instance)
    traceback_limit = Tupu  # Print entire traceback to self.get_stderr()
    error_status = "500 Internal Server Error"
    error_headers = [('Content-Type','text/plain')]
    error_body = b"A server error occurred.  Please contact the administrator."

    # State variables (don't mess ukijumuisha these)
    status = result = Tupu
    headers_sent = Uongo
    headers = Tupu
    bytes_sent = 0

    eleza run(self, application):
        """Invoke the application"""
        # Note to self: don't move the close()!  Asynchronous servers shouldn't
        # call close() kutoka finish_response(), so ikiwa you close() anywhere but
        # the double-error branch here, you'll koma asynchronous servers by
        # prematurely closing.  Async servers must rudisha kutoka 'run()' without
        # closing ikiwa there might still be output to iterate over.
        jaribu:
            self.setup_environ()
            self.result = application(self.environ, self.start_response)
            self.finish_response()
        tatizo (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            # We expect the client to close the connection abruptly kutoka time
            # to time.
            rudisha
        except:
            jaribu:
                self.handle_error()
            except:
                # If we get an error handling an error, just give up already!
                self.close()
                ashiria   # ...and let the actual server figure it out.


    eleza setup_environ(self):
        """Set up the environment kila one request"""

        env = self.environ = self.os_environ.copy()
        self.add_cgi_vars()

        env['wsgi.input']        = self.get_stdin()
        env['wsgi.errors']       = self.get_stderr()
        env['wsgi.version']      = self.wsgi_version
        env['wsgi.run_once']     = self.wsgi_run_once
        env['wsgi.url_scheme']   = self.get_scheme()
        env['wsgi.multithread']  = self.wsgi_multithread
        env['wsgi.multiprocess'] = self.wsgi_multiprocess

        ikiwa self.wsgi_file_wrapper ni sio Tupu:
            env['wsgi.file_wrapper'] = self.wsgi_file_wrapper

        ikiwa self.origin_server na self.server_software:
            env.setdefault('SERVER_SOFTWARE',self.server_software)


    eleza finish_response(self):
        """Send any iterable data, then close self na the iterable

        Subclasses intended kila use kwenye asynchronous servers will
        want to redefine this method, such that it sets up callbacks
        kwenye the event loop to iterate over the data, na to call
        'self.close()' once the response ni finished.
        """
        jaribu:
            ikiwa sio self.result_is_file() ama sio self.sendfile():
                kila data kwenye self.result:
                    self.write(data)
                self.finish_content()
        except:
            # Call close() on the iterable rudishaed by the WSGI application
            # kwenye case of an exception.
            ikiwa hasattr(self.result, 'close'):
                self.result.close()
            ashiria
        isipokua:
            # We only call close() when no exception ni ashiriad, because it
            # will set status, result, headers, na environ fields to Tupu.
            # See bpo-29183 kila more details.
            self.close()


    eleza get_scheme(self):
        """Return the URL scheme being used"""
        rudisha guess_scheme(self.environ)


    eleza set_content_length(self):
        """Compute Content-Length ama switch to chunked encoding ikiwa possible"""
        jaribu:
            blocks = len(self.result)
        tatizo (TypeError,AttributeError,NotImplementedError):
            pita
        isipokua:
            ikiwa blocks==1:
                self.headers['Content-Length'] = str(self.bytes_sent)
                rudisha
        # XXX Try kila chunked encoding ikiwa origin server na client ni 1.1


    eleza cleanup_headers(self):
        """Make any necessary header changes ama defaults

        Subclasses can extend this to add other defaults.
        """
        ikiwa 'Content-Length' haiko kwenye self.headers:
            self.set_content_length()

    eleza start_response(self, status, headers,exc_info=Tupu):
        """'start_response()' callable kama specified by PEP 3333"""

        ikiwa exc_info:
            jaribu:
                ikiwa self.headers_sent:
                    # Re-ashiria original exception ikiwa headers sent
                    ashiria exc_info[0](exc_info[1]).with_traceback(exc_info[2])
            mwishowe:
                exc_info = Tupu        # avoid dangling circular ref
        lasivyo self.headers ni sio Tupu:
            ashiria AssertionError("Headers already set!")

        self.status = status
        self.headers = self.headers_class(headers)
        status = self._convert_string_type(status, "Status")
        assert len(status)>=4,"Status must be at least 4 characters"
        assert status[:3].isdigit(), "Status message must begin w/3-digit code"
        assert status[3]==" ", "Status message must have a space after code"

        ikiwa __debug__:
            kila name, val kwenye headers:
                name = self._convert_string_type(name, "Header name")
                val = self._convert_string_type(val, "Header value")
                assert sio is_hop_by_hop(name),\
                       f"Hop-by-hop header, '{name}: {val}', sio allowed"

        rudisha self.write

    eleza _convert_string_type(self, value, title):
        """Convert/check value type."""
        ikiwa type(value) ni str:
            rudisha value
        ashiria AssertionError(
            "{0} must be of type str (got {1})".format(title, repr(value))
        )

    eleza send_preamble(self):
        """Transmit version/status/date/server, via self._write()"""
        ikiwa self.origin_server:
            ikiwa self.client_is_modern():
                self._write(('HTTP/%s %s\r\n' % (self.http_version,self.status)).encode('iso-8859-1'))
                ikiwa 'Date' haiko kwenye self.headers:
                    self._write(
                        ('Date: %s\r\n' % format_date_time(time.time())).encode('iso-8859-1')
                    )
                ikiwa self.server_software na 'Server' haiko kwenye self.headers:
                    self._write(('Server: %s\r\n' % self.server_software).encode('iso-8859-1'))
        isipokua:
            self._write(('Status: %s\r\n' % self.status).encode('iso-8859-1'))

    eleza write(self, data):
        """'write()' callable kama specified by PEP 3333"""

        assert type(data) ni bytes, \
            "write() argument must be a bytes instance"

        ikiwa sio self.status:
            ashiria AssertionError("write() before start_response()")

        lasivyo sio self.headers_sent:
            # Before the first output, send the stored headers
            self.bytes_sent = len(data)    # make sure we know content-length
            self.send_headers()
        isipokua:
            self.bytes_sent += len(data)

        # XXX check Content-Length na truncate ikiwa too many bytes written?
        self._write(data)
        self._flush()


    eleza sendfile(self):
        """Platform-specific file transmission

        Override this method kwenye subclasses to support platform-specific
        file transmission.  It ni only called ikiwa the application's
        rudisha iterable ('self.result') ni an instance of
        'self.wsgi_file_wrapper'.

        This method should rudisha a true value ikiwa it was able to actually
        transmit the wrapped file-like object using a platform-specific
        approach.  It should rudisha a false value ikiwa normal iteration
        should be used instead.  An exception can be ashiriad to indicate
        that transmission was attempted, but failed.

        NOTE: this method should call 'self.send_headers()' if
        'self.headers_sent' ni false na it ni going to attempt direct
        transmission of the file.
        """
        rudisha Uongo   # No platform-specific transmission by default


    eleza finish_content(self):
        """Ensure headers na content have both been sent"""
        ikiwa sio self.headers_sent:
            # Only zero Content-Length ikiwa sio set by the application (so
            # that HEAD requests can be satisfied properly, see #3839)
            self.headers.setdefault('Content-Length', "0")
            self.send_headers()
        isipokua:
            pita # XXX check ikiwa content-length was too short?

    eleza close(self):
        """Close the iterable (ikiwa needed) na reset all instance vars

        Subclasses may want to also drop the client connection.
        """
        jaribu:
            ikiwa hasattr(self.result,'close'):
                self.result.close()
        mwishowe:
            self.result = self.headers = self.status = self.environ = Tupu
            self.bytes_sent = 0; self.headers_sent = Uongo


    eleza send_headers(self):
        """Transmit headers to the client, via self._write()"""
        self.cleanup_headers()
        self.headers_sent = Kweli
        ikiwa sio self.origin_server ama self.client_is_modern():
            self.send_preamble()
            self._write(bytes(self.headers))


    eleza result_is_file(self):
        """Kweli ikiwa 'self.result' ni an instance of 'self.wsgi_file_wrapper'"""
        wrapper = self.wsgi_file_wrapper
        rudisha wrapper ni sio Tupu na isinstance(self.result,wrapper)


    eleza client_is_modern(self):
        """Kweli ikiwa client can accept status na headers"""
        rudisha self.environ['SERVER_PROTOCOL'].upper() != 'HTTP/0.9'


    eleza log_exception(self,exc_info):
        """Log the 'exc_info' tuple kwenye the server log

        Subclasses may override to retarget the output ama change its format.
        """
        jaribu:
            kutoka traceback agiza print_exception
            stderr = self.get_stderr()
            print_exception(
                exc_info[0], exc_info[1], exc_info[2],
                self.traceback_limit, stderr
            )
            stderr.flush()
        mwishowe:
            exc_info = Tupu

    eleza handle_error(self):
        """Log current error, na send error output to client ikiwa possible"""
        self.log_exception(sys.exc_info())
        ikiwa sio self.headers_sent:
            self.result = self.error_output(self.environ, self.start_response)
            self.finish_response()
        # XXX isipokua: attempt advanced recovery techniques kila HTML ama text?

    eleza error_output(self, environ, start_response):
        """WSGI mini-app to create error output

        By default, this just uses the 'error_status', 'error_headers',
        na 'error_body' attributes to generate an output page.  It can
        be overridden kwenye a subkundi to dynamically generate diagnostics,
        choose an appropriate message kila the user's preferred language, etc.

        Note, however, that it's sio recommended kutoka a security perspective to
        spit out diagnostics to any old user; ideally, you should have to do
        something special to enable diagnostic output, which ni why we don't
        include any here!
        """
        start_response(self.error_status,self.error_headers[:],sys.exc_info())
        rudisha [self.error_body]


    # Pure abstract methods; *must* be overridden kwenye subclasses

    eleza _write(self,data):
        """Override kwenye subkundi to buffer data kila send to client

        It's okay ikiwa this method actually transmits the data; BaseHandler
        just separates write na flush operations kila greater efficiency
        when the underlying system actually has such a distinction.
        """
        ashiria NotImplementedError

    eleza _flush(self):
        """Override kwenye subkundi to force sending of recent '_write()' calls

        It's okay ikiwa this method ni a no-op (i.e., ikiwa '_write()' actually
        sends the data.
        """
        ashiria NotImplementedError

    eleza get_stdin(self):
        """Override kwenye subkundi to rudisha suitable 'wsgi.input'"""
        ashiria NotImplementedError

    eleza get_stderr(self):
        """Override kwenye subkundi to rudisha suitable 'wsgi.errors'"""
        ashiria NotImplementedError

    eleza add_cgi_vars(self):
        """Override kwenye subkundi to insert CGI variables kwenye 'self.environ'"""
        ashiria NotImplementedError


kundi SimpleHandler(BaseHandler):
    """Handler that's just initialized ukijumuisha streams, environment, etc.

    This handler subkundi ni intended kila synchronous HTTP/1.0 origin servers,
    na handles sending the entire response output, given the correct inputs.

    Usage::

        handler = SimpleHandler(
            inp,out,err,env, multithread=Uongo, multiprocess=Kweli
        )
        handler.run(app)"""

    eleza __init__(self,stdin,stdout,stderr,environ,
        multithread=Kweli, multiprocess=Uongo
    ):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.base_env = environ
        self.wsgi_multithread = multithread
        self.wsgi_multiprocess = multiprocess

    eleza get_stdin(self):
        rudisha self.stdin

    eleza get_stderr(self):
        rudisha self.stderr

    eleza add_cgi_vars(self):
        self.environ.update(self.base_env)

    eleza _write(self,data):
        result = self.stdout.write(data)
        ikiwa result ni Tupu ama result == len(data):
            rudisha
        kutoka warnings agiza warn
        warn("SimpleHandler.stdout.write() should sio do partial writes",
            DeprecationWarning)
        wakati Kweli:
            data = data[result:]
            ikiwa sio data:
                koma
            result = self.stdout.write(data)

    eleza _flush(self):
        self.stdout.flush()
        self._flush = self.stdout.flush


kundi BaseCGIHandler(SimpleHandler):

    """CGI-like systems using input/output/error streams na environ mapping

    Usage::

        handler = BaseCGIHandler(inp,out,err,env)
        handler.run(app)

    This handler kundi ni useful kila gateway protocols like ReadyExec and
    FastCGI, that have usable input/output/error streams na an environment
    mapping.  It's also the base kundi kila CGIHandler, which just uses
    sys.stdin, os.environ, na so on.

    The constructor also takes keyword arguments 'multithread' and
    'multiprocess' (defaulting to 'Kweli' na 'Uongo' respectively) to control
    the configuration sent to the application.  It sets 'origin_server' to
    Uongo (to enable CGI-like output), na assumes that 'wsgi.run_once' is
    Uongo.
    """

    origin_server = Uongo


kundi CGIHandler(BaseCGIHandler):

    """CGI-based invocation via sys.stdin/stdout/stderr na os.environ

    Usage::

        CGIHandler().run(app)

    The difference between this kundi na BaseCGIHandler ni that it always
    uses 'wsgi.run_once' of 'Kweli', 'wsgi.multithread' of 'Uongo', and
    'wsgi.multiprocess' of 'Kweli'.  It does sio take any initialization
    parameters, but always uses 'sys.stdin', 'os.environ', na friends.

    If you need to override any of these parameters, use BaseCGIHandler
    instead.
    """

    wsgi_run_once = Kweli
    # Do sio allow os.environ to leak between requests kwenye Google App Engine
    # na other multi-run CGI use cases.  This ni sio easily testable.
    # See http://bugs.python.org/issue7250
    os_environ = {}

    eleza __init__(self):
        BaseCGIHandler.__init__(
            self, sys.stdin.buffer, sys.stdout.buffer, sys.stderr,
            read_environ(), multithread=Uongo, multiprocess=Kweli
        )


kundi IISCGIHandler(BaseCGIHandler):
    """CGI-based invocation ukijumuisha workaround kila IIS path bug

    This handler should be used kwenye preference to CGIHandler when deploying on
    Microsoft IIS without having set the config allowPathInfo option (IIS>=7)
    ama metabase allowPathInfoForScriptMappings (IIS<7).
    """
    wsgi_run_once = Kweli
    os_environ = {}

    # By default, IIS gives a PATH_INFO that duplicates the SCRIPT_NAME at
    # the front, causing problems kila WSGI applications that wish to implement
    # routing. This handler strips any such duplicated path.

    # IIS can be configured to pita the correct PATH_INFO, but this causes
    # another bug where PATH_TRANSLATED ni wrong. Luckily this variable is
    # rarely used na ni sio guaranteed by WSGI. On IIS<7, though, the
    # setting can only be made on a vhost level, affecting all other script
    # mappings, many of which koma when exposed to the PATH_TRANSLATED bug.
    # For this reason IIS<7 ni almost never deployed ukijumuisha the fix. (Even IIS7
    # rarely uses it because there ni still no UI kila it.)

    # There ni no way kila CGI code to tell whether the option was set, so a
    # separate handler kundi ni provided.
    eleza __init__(self):
        environ= read_environ()
        path = environ.get('PATH_INFO', '')
        script = environ.get('SCRIPT_NAME', '')
        ikiwa (path+'/').startswith(script+'/'):
            environ['PATH_INFO'] = path[len(script):]
        BaseCGIHandler.__init__(
            self, sys.stdin.buffer, sys.stdout.buffer, sys.stderr,
            environ, multithread=Uongo, multiprocess=Kweli
        )
