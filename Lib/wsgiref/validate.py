# (c) 2005 Ian Bicking na contributors; written kila Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Also licenced under the Apache License, 2.0: http://opensource.org/licenses/apache2.0.php
# Licensed to PSF under a Contributor Agreement
"""
Middleware to check kila obedience to the WSGI specification.

Some of the things this checks:

* Signature of the application na start_response (including that
  keyword arguments are sio used).

* Environment checks:

  - Environment ni a dictionary (and sio a subclass).

  - That all the required keys are kwenye the environment: REQUEST_METHOD,
    SERVER_NAME, SERVER_PORT, wsgi.version, wsgi.input, wsgi.errors,
    wsgi.multithread, wsgi.multiprocess, wsgi.run_once

  - That HTTP_CONTENT_TYPE na HTTP_CONTENT_LENGTH are haiko kwenye the
    environment (these headers should appear kama CONTENT_LENGTH na
    CONTENT_TYPE).

  - Warns ikiwa QUERY_STRING ni missing, kama the cgi module acts
    unpredictably kwenye that case.

  - That CGI-style variables (that don't contain a .) have
    (non-unicode) string values

  - That wsgi.version ni a tuple

  - That wsgi.url_scheme ni 'http' ama 'https' (@@: ni this too
    restrictive?)

  - Warns ikiwa the REQUEST_METHOD ni sio known (@@: probably too
    restrictive).

  - That SCRIPT_NAME na PATH_INFO are empty ama start ukijumuisha /

  - That at least one of SCRIPT_NAME ama PATH_INFO are set.

  - That CONTENT_LENGTH ni a positive integer.

  - That SCRIPT_NAME ni sio '/' (it should be '', na PATH_INFO should
    be '/').

  - That wsgi.input has the methods read, readline, readlines, na
    __iter__

  - That wsgi.errors has the methods flush, write, writelines

* The status ni a string, contains a space, starts ukijumuisha an integer,
  na that integer ni kwenye range (> 100).

* That the headers ni a list (sio a subclass, sio another kind of
  sequence).

* That the items of the headers are tuples of strings.

* That there ni no 'status' header (that ni used kwenye CGI, but sio in
  WSGI).

* That the headers don't contain newlines ama colons, end kwenye _ ama -, ama
  contain characters codes below 037.

* That Content-Type ni given ikiwa there ni content (CGI often has a
  default content type, but WSGI does not).

* That no Content-Type ni given when there ni no content (@@: ni this
  too restrictive?)

* That the exc_info argument to start_response ni a tuple ama Tupu.

* That all calls to the writer are ukijumuisha strings, na no other methods
  on the writer are accessed.

* That wsgi.input ni used properly:

  - .read() ni called ukijumuisha exactly one argument

  - That it returns a string

  - That readline, readlines, na __iter__ rudisha strings

  - That .close() ni sio called

  - No other methods are provided

* That wsgi.errors ni used properly:

  - .write() na .writelines() ni called ukijumuisha a string

  - That .close() ni sio called, na no other methods are provided.

* The response iterator:

  - That it ni sio a string (it should be a list of a single string; a
    string will work, but perform horribly).

  - That .__next__() returns a string

  - That the iterator ni sio iterated over until start_response has
    been called (that can signal either a server ama application
    error).

  - That .close() ni called (doesn't ashiria exception, only prints to
    sys.stderr, because we only know it isn't called when the object
    ni garbage collected).
"""
__all__ = ['validator']


agiza re
agiza sys
agiza warnings

header_re = re.compile(r'^[a-zA-Z][a-zA-Z0-9\-_]*$')
bad_header_value_re = re.compile(r'[\000-\037]')

kundi WSGIWarning(Warning):
    """
    Raised kwenye response to WSGI-spec-related warnings
    """

eleza assert_(cond, *args):
    ikiwa sio cond:
        ashiria AssertionError(*args)

eleza check_string_type(value, title):
    ikiwa type (value) ni str:
        rudisha value
    ashiria AssertionError(
        "{0} must be of type str (got {1})".format(title, repr(value)))

eleza validator(application):

    """
    When applied between a WSGI server na a WSGI application, this
    middleware will check kila WSGI compliancy on a number of levels.
    This middleware does sio modify the request ama response kwenye any
    way, but will ashiria an AssertionError ikiwa anything seems off
    (tatizo kila a failure to close the application iterator, which
    will be printed to stderr -- there's no way to ashiria an exception
    at that point).
    """

    eleza lint_app(*args, **kw):
        assert_(len(args) == 2, "Two arguments required")
        assert_(sio kw, "No keyword arguments allowed")
        environ, start_response = args

        check_environ(environ)

        # We use this to check ikiwa the application returns without
        # calling start_response:
        start_response_started = []

        eleza start_response_wrapper(*args, **kw):
            assert_(len(args) == 2 ama len(args) == 3, (
                "Invalid number of arguments: %s" % (args,)))
            assert_(sio kw, "No keyword arguments allowed")
            status = args[0]
            headers = args[1]
            ikiwa len(args) == 3:
                exc_info = args[2]
            isipokua:
                exc_info = Tupu

            check_status(status)
            check_headers(headers)
            check_content_type(status, headers)
            check_exc_info(exc_info)

            start_response_started.append(Tupu)
            rudisha WriteWrapper(start_response(*args))

        environ['wsgi.input'] = InputWrapper(environ['wsgi.input'])
        environ['wsgi.errors'] = ErrorWrapper(environ['wsgi.errors'])

        iterator = application(environ, start_response_wrapper)
        assert_(iterator ni sio Tupu na iterator != Uongo,
            "The application must rudisha an iterator, ikiwa only an empty list")

        check_iterator(iterator)

        rudisha IteratorWrapper(iterator, start_response_started)

    rudisha lint_app

kundi InputWrapper:

    eleza __init__(self, wsgi_input):
        self.input = wsgi_input

    eleza read(self, *args):
        assert_(len(args) == 1)
        v = self.input.read(*args)
        assert_(type(v) ni bytes)
        rudisha v

    eleza readline(self, *args):
        assert_(len(args) <= 1)
        v = self.input.readline(*args)
        assert_(type(v) ni bytes)
        rudisha v

    eleza readlines(self, *args):
        assert_(len(args) <= 1)
        lines = self.input.readlines(*args)
        assert_(type(lines) ni list)
        kila line kwenye lines:
            assert_(type(line) ni bytes)
        rudisha lines

    eleza __iter__(self):
        wakati 1:
            line = self.readline()
            ikiwa sio line:
                return
            tuma line

    eleza close(self):
        assert_(0, "input.close() must sio be called")

kundi ErrorWrapper:

    eleza __init__(self, wsgi_errors):
        self.errors = wsgi_errors

    eleza write(self, s):
        assert_(type(s) ni str)
        self.errors.write(s)

    eleza flush(self):
        self.errors.flush()

    eleza writelines(self, seq):
        kila line kwenye seq:
            self.write(line)

    eleza close(self):
        assert_(0, "errors.close() must sio be called")

kundi WriteWrapper:

    eleza __init__(self, wsgi_writer):
        self.writer = wsgi_writer

    eleza __call__(self, s):
        assert_(type(s) ni bytes)
        self.writer(s)

kundi PartialIteratorWrapper:

    eleza __init__(self, wsgi_iterator):
        self.iterator = wsgi_iterator

    eleza __iter__(self):
        # We want to make sure __iter__ ni called
        rudisha IteratorWrapper(self.iterator, Tupu)

kundi IteratorWrapper:

    eleza __init__(self, wsgi_iterator, check_start_response):
        self.original_iterator = wsgi_iterator
        self.iterator = iter(wsgi_iterator)
        self.closed = Uongo
        self.check_start_response = check_start_response

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        assert_(sio self.closed,
            "Iterator read after closed")
        v = next(self.iterator)
        ikiwa type(v) ni sio bytes:
            assert_(Uongo, "Iterator tumaed non-bytestring (%r)" % (v,))
        ikiwa self.check_start_response ni sio Tupu:
            assert_(self.check_start_response,
                "The application returns na we started iterating over its body, but start_response has sio yet been called")
            self.check_start_response = Tupu
        rudisha v

    eleza close(self):
        self.closed = Kweli
        ikiwa hasattr(self.original_iterator, 'close'):
            self.original_iterator.close()

    eleza __del__(self):
        ikiwa sio self.closed:
            sys.stderr.write(
                "Iterator garbage collected without being closed")
        assert_(self.closed,
            "Iterator garbage collected without being closed")

eleza check_environ(environ):
    assert_(type(environ) ni dict,
        "Environment ni sio of the right type: %r (environment: %r)"
        % (type(environ), environ))

    kila key kwenye ['REQUEST_METHOD', 'SERVER_NAME', 'SERVER_PORT',
                'wsgi.version', 'wsgi.input', 'wsgi.errors',
                'wsgi.multithread', 'wsgi.multiprocess',
                'wsgi.run_once']:
        assert_(key kwenye environ,
            "Environment missing required key: %r" % (key,))

    kila key kwenye ['HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH']:
        assert_(key haiko kwenye environ,
            "Environment should sio have the key: %s "
            "(use %s instead)" % (key, key[5:]))

    ikiwa 'QUERY_STRING' haiko kwenye environ:
        warnings.warn(
            'QUERY_STRING ni haiko kwenye the WSGI environment; the cgi '
            'module will use sys.argv when this variable ni missing, '
            'so application errors are more likely',
            WSGIWarning)

    kila key kwenye environ.keys():
        ikiwa '.' kwenye key:
            # Extension, we don't care about its type
            endelea
        assert_(type(environ[key]) ni str,
            "Environmental variable %s ni sio a string: %r (value: %r)"
            % (key, type(environ[key]), environ[key]))

    assert_(type(environ['wsgi.version']) ni tuple,
        "wsgi.version should be a tuple (%r)" % (environ['wsgi.version'],))
    assert_(environ['wsgi.url_scheme'] kwenye ('http', 'https'),
        "wsgi.url_scheme unknown: %r" % environ['wsgi.url_scheme'])

    check_uliza(environ['wsgi.input'])
    check_errors(environ['wsgi.errors'])

    # @@: these need filling out:
    ikiwa environ['REQUEST_METHOD'] haiko kwenye (
        'GET', 'HEAD', 'POST', 'OPTIONS', 'PATCH', 'PUT', 'DELETE', 'TRACE'):
        warnings.warn(
            "Unknown REQUEST_METHOD: %r" % environ['REQUEST_METHOD'],
            WSGIWarning)

    assert_(sio environ.get('SCRIPT_NAME')
            ama environ['SCRIPT_NAME'].startswith('/'),
        "SCRIPT_NAME doesn't start ukijumuisha /: %r" % environ['SCRIPT_NAME'])
    assert_(sio environ.get('PATH_INFO')
            ama environ['PATH_INFO'].startswith('/'),
        "PATH_INFO doesn't start ukijumuisha /: %r" % environ['PATH_INFO'])
    ikiwa environ.get('CONTENT_LENGTH'):
        assert_(int(environ['CONTENT_LENGTH']) >= 0,
            "Invalid CONTENT_LENGTH: %r" % environ['CONTENT_LENGTH'])

    ikiwa sio environ.get('SCRIPT_NAME'):
        assert_('PATH_INFO' kwenye environ,
            "One of SCRIPT_NAME ama PATH_INFO are required (PATH_INFO "
            "should at least be '/' ikiwa SCRIPT_NAME ni empty)")
    assert_(environ.get('SCRIPT_NAME') != '/',
        "SCRIPT_NAME cannot be '/'; it should instead be '', na "
        "PATH_INFO should be '/'")

eleza check_uliza(wsgi_input):
    kila attr kwenye ['read', 'readline', 'readlines', '__iter__']:
        assert_(hasattr(wsgi_input, attr),
            "wsgi.input (%r) doesn't have the attribute %s"
            % (wsgi_input, attr))

eleza check_errors(wsgi_errors):
    kila attr kwenye ['flush', 'write', 'writelines']:
        assert_(hasattr(wsgi_errors, attr),
            "wsgi.errors (%r) doesn't have the attribute %s"
            % (wsgi_errors, attr))

eleza check_status(status):
    status = check_string_type(status, "Status")
    # Implicitly check that we can turn it into an integer:
    status_code = status.split(Tupu, 1)[0]
    assert_(len(status_code) == 3,
        "Status codes must be three characters: %r" % status_code)
    status_int = int(status_code)
    assert_(status_int >= 100, "Status code ni invalid: %r" % status_int)
    ikiwa len(status) < 4 ama status[3] != ' ':
        warnings.warn(
            "The status string (%r) should be a three-digit integer "
            "followed by a single space na a status explanation"
            % status, WSGIWarning)

eleza check_headers(headers):
    assert_(type(headers) ni list,
        "Headers (%r) must be of type list: %r"
        % (headers, type(headers)))
    kila item kwenye headers:
        assert_(type(item) ni tuple,
            "Individual headers (%r) must be of type tuple: %r"
            % (item, type(item)))
        assert_(len(item) == 2)
        name, value = item
        name = check_string_type(name, "Header name")
        value = check_string_type(value, "Header value")
        assert_(name.lower() != 'status',
            "The Status header cannot be used; it conflicts ukijumuisha CGI "
            "script, na HTTP status ni sio given through headers "
            "(value: %r)." % value)
        assert_('\n' haiko kwenye name na ':' haiko kwenye name,
            "Header names may sio contain ':' ama '\\n': %r" % name)
        assert_(header_re.search(name), "Bad header name: %r" % name)
        assert_(sio name.endswith('-') na sio name.endswith('_'),
            "Names may sio end kwenye '-' ama '_': %r" % name)
        ikiwa bad_header_value_re.search(value):
            assert_(0, "Bad header value: %r (bad char: %r)"
            % (value, bad_header_value_re.search(value).group(0)))

eleza check_content_type(status, headers):
    status = check_string_type(status, "Status")
    code = int(status.split(Tupu, 1)[0])
    # @@: need one more person to verify this interpretation of RFC 2616
    #     http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    NO_MESSAGE_BODY = (204, 304)
    kila name, value kwenye headers:
        name = check_string_type(name, "Header name")
        ikiwa name.lower() == 'content-type':
            ikiwa code haiko kwenye NO_MESSAGE_BODY:
                return
            assert_(0, ("Content-Type header found kwenye a %s response, "
                        "which must sio rudisha content.") % code)
    ikiwa code haiko kwenye NO_MESSAGE_BODY:
        assert_(0, "No Content-Type header found kwenye headers (%s)" % headers)

eleza check_exc_info(exc_info):
    assert_(exc_info ni Tupu ama type(exc_info) ni tuple,
        "exc_info (%r) ni sio a tuple: %r" % (exc_info, type(exc_info)))
    # More exc_info checks?

eleza check_iterator(iterator):
    # Technically a bytestring ni legal, which ni why it's a really bad
    # idea, because it may cause the response to be returned
    # character-by-character
    assert_(sio isinstance(iterator, (str, bytes)),
        "You should sio rudisha a string kama your application iterator, "
        "instead rudisha a single-item list containing a bytestring.")
