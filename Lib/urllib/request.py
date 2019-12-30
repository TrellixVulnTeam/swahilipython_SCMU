"""An extensible library kila opening URLs using a variety of protocols

The simplest way to use this module ni to call the urlopen function,
which accepts a string containing a URL ama a Request object (described
below).  It opens the URL na returns the results kama file-like
object; the returned object has some extra methods described below.

The OpenerDirector manages a collection of Handler objects that do
all the actual work.  Each Handler implements a particular protocol ama
option.  The OpenerDirector ni a composite object that invokes the
Handlers needed to open the requested URL.  For example, the
HTTPHandler performs HTTP GET na POST requests na deals with
non-error returns.  The HTTPRedirectHandler automatically deals with
HTTP 301, 302, 303 na 307 redirect errors, na the HTTPDigestAuthHandler
deals ukijumuisha digest authentication.

urlopen(url, data=Tupu) -- Basic usage ni the same kama original
urllib.  pita the url na optionally data to post to an HTTP URL, na
get a file-like object back.  One difference ni that you can also pita
a Request instance instead of URL.  Raises a URLError (subkundi of
OSError); kila HTTP errors, raises an HTTPError, which can also be
treated kama a valid response.

build_opener -- Function that creates a new OpenerDirector instance.
Will install the default handlers.  Accepts one ama more Handlers as
arguments, either instances ama Handler classes that it will
instantiate.  If one of the argument ni a subkundi of the default
handler, the argument will be installed instead of the default.

install_opener -- Installs a new opener kama the default opener.

objects of interest:

OpenerDirector -- Sets up the User Agent kama the Python-urllib client na manages
the Handler classes, wakati dealing ukijumuisha requests na responses.

Request -- An object that encapsulates the state of a request.  The
state can be kama simple kama the URL.  It can also include extra HTTP
headers, e.g. a User-Agent.

BaseHandler --

internals:
BaseHandler na parent
_call_chain conventions

Example usage:

agiza urllib.request

# set up authentication info
authinfo = urllib.request.HTTPBasicAuthHandler()
authinfo.add_pitaword(realm='PDQ Application',
                      uri='https://mahler:8092/site-updates.py',
                      user='klem',
                      pitawd='geheim$parole')

proxy_support = urllib.request.ProxyHandler({"http" : "http://ahad-haam:3128"})

# build a new opener that adds authentication na caching FTP handlers
opener = urllib.request.build_opener(proxy_support, authinfo,
                                     urllib.request.CacheFTPHandler)

# install it
urllib.request.install_opener(opener)

f = urllib.request.urlopen('http://www.python.org/')
"""

# XXX issues:
# If an authentication error handler that tries to perform
# authentication kila some reason but fails, how should the error be
# signalled?  The client needs to know the HTTP error code.  But if
# the handler knows that the problem was, e.g., that it didn't know
# that hash algo that requested kwenye the challenge, it would be good to
# pita that information along to the client, too.
# ftp errors aren't handled cleanly
# check digest against correct (i.e. non-apache) implementation

# Possible extensions:
# complex proxies  XXX sio sure what exactly was meant by this
# abstract factory kila opener

agiza base64
agiza bisect
agiza email
agiza hashlib
agiza http.client
agiza io
agiza os
agiza posixpath
agiza re
agiza socket
agiza string
agiza sys
agiza time
agiza tempfile
agiza contextlib
agiza warnings


kutoka urllib.error agiza URLError, HTTPError, ContentTooShortError
kutoka urllib.parse agiza (
    urlparse, urlsplit, urljoin, unwrap, quote, unquote,
    _splittype, _splithost, _splitport, _splituser, _splitpitawd,
    _splitattr, _splitquery, _splitvalue, _splittag, _to_bytes,
    unquote_to_bytes, urlunparse)
kutoka urllib.response agiza addinfourl, addclosehook

# check kila SSL
jaribu:
    agiza ssl
tatizo ImportError:
    _have_ssl = Uongo
isipokua:
    _have_ssl = Kweli

__all__ = [
    # Classes
    'Request', 'OpenerDirector', 'BaseHandler', 'HTTPDefaultErrorHandler',
    'HTTPRedirectHandler', 'HTTPCookieProcessor', 'ProxyHandler',
    'HTTPPasswordMgr', 'HTTPPasswordMgrWithDefaultRealm',
    'HTTPPasswordMgrWithPriorAuth', 'AbstractBasicAuthHandler',
    'HTTPBasicAuthHandler', 'ProxyBasicAuthHandler', 'AbstractDigestAuthHandler',
    'HTTPDigestAuthHandler', 'ProxyDigestAuthHandler', 'HTTPHandler',
    'FileHandler', 'FTPHandler', 'CacheFTPHandler', 'DataHandler',
    'UnknownHandler', 'HTTPErrorProcessor',
    # Functions
    'urlopen', 'install_opener', 'build_opener',
    'pathname2url', 'url2pathname', 'getproxies',
    # Legacy interface
    'urlretrieve', 'urlcleanup', 'URLopener', 'FancyURLopener',
]

# used kwenye User-Agent header sent
__version__ = '%d.%d' % sys.version_info[:2]

_opener = Tupu
eleza urlopen(url, data=Tupu, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
            *, cafile=Tupu, capath=Tupu, cadefault=Uongo, context=Tupu):
    '''Open the URL url, which can be either a string ama a Request object.

    *data* must be an object specifying additional data to be sent to
    the server, ama Tupu ikiwa no such data ni needed.  See Request for
    details.

    urllib.request module uses HTTP/1.1 na includes a "Connection:close"
    header kwenye its HTTP requests.

    The optional *timeout* parameter specifies a timeout kwenye seconds for
    blocking operations like the connection attempt (ikiwa sio specified, the
    global default timeout setting will be used). This only works kila HTTP,
    HTTPS na FTP connections.

    If *context* ni specified, it must be a ssl.SSLContext instance describing
    the various SSL options. See HTTPSConnection kila more details.

    The optional *cafile* na *capath* parameters specify a set of trusted CA
    certificates kila HTTPS requests. cafile should point to a single file
    containing a bundle of CA certificates, whereas capath should point to a
    directory of hashed certificate files. More information can be found kwenye
    ssl.SSLContext.load_verify_locations().

    The *cadefault* parameter ni ignored.

    This function always returns an object which can work kama a context
    manager na has methods such as

    * geturl() - rudisha the URL of the resource retrieved, commonly used to
      determine ikiwa a redirect was followed

    * info() - rudisha the meta-information of the page, such kama headers, kwenye the
      form of an email.message_from_string() instance (see Quick Reference to
      HTTP Headers)

    * getcode() - rudisha the HTTP status code of the response.  Raises URLError
      on errors.

    For HTTP na HTTPS URLs, this function returns a http.client.HTTPResponse
    object slightly modified. In addition to the three new methods above, the
    msg attribute contains the same information kama the reason attribute ---
    the reason phrase returned by the server --- instead of the response
    headers kama it ni specified kwenye the documentation kila HTTPResponse.

    For FTP, file, na data URLs na requests explicitly handled by legacy
    URLopener na FancyURLopener classes, this function returns a
    urllib.response.addinfourl object.

    Note that Tupu may be returned ikiwa no handler handles the request (though
    the default installed global OpenerDirector uses UnknownHandler to ensure
    this never happens).

    In addition, ikiwa proxy settings are detected (kila example, when a *_proxy
    environment variable like http_proxy ni set), ProxyHandler ni default
    installed na makes sure the requests are handled through the proxy.

    '''
    global _opener
    ikiwa cafile ama capath ama cadefault:
        agiza warnings
        warnings.warn("cafile, capath na cadefault are deprecated, use a "
                      "custom context instead.", DeprecationWarning, 2)
        ikiwa context ni sio Tupu:
            ashiria ValueError(
                "You can't pita both context na any of cafile, capath, na "
                "cadefault"
            )
        ikiwa sio _have_ssl:
            ashiria ValueError('SSL support sio available')
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                             cafile=cafile,
                                             capath=capath)
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    lasivyo context:
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    lasivyo _opener ni Tupu:
        _opener = opener = build_opener()
    isipokua:
        opener = _opener
    rudisha opener.open(url, data, timeout)

eleza install_opener(opener):
    global _opener
    _opener = opener

_url_tempfiles = []
eleza urlretrieve(url, filename=Tupu, reporthook=Tupu, data=Tupu):
    """
    Retrieve a URL into a temporary location on disk.

    Requires a URL argument. If a filename ni pitaed, it ni used as
    the temporary file location. The reporthook argument should be
    a callable that accepts a block number, a read size, na the
    total file size of the URL target. The data argument should be
    valid URL encoded data.

    If a filename ni pitaed na the URL points to a local resource,
    the result ni a copy kutoka local file to new file.

    Returns a tuple containing the path to the newly created
    data file kama well kama the resulting HTTPMessage object.
    """
    url_type, path = _splittype(url)

    ukijumuisha contextlib.closing(urlopen(url, data)) kama fp:
        headers = fp.info()

        # Just rudisha the local path na the "headers" kila file://
        # URLs. No sense kwenye performing a copy unless requested.
        ikiwa url_type == "file" na sio filename:
            rudisha os.path.normpath(path), headers

        # Handle temporary file setup.
        ikiwa filename:
            tfp = open(filename, 'wb')
        isipokua:
            tfp = tempfile.NamedTemporaryFile(delete=Uongo)
            filename = tfp.name
            _url_tempfiles.append(filename)

        ukijumuisha tfp:
            result = filename, headers
            bs = 1024*8
            size = -1
            read = 0
            blocknum = 0
            ikiwa "content-length" kwenye headers:
                size = int(headers["Content-Length"])

            ikiwa reporthook:
                reporthook(blocknum, bs, size)

            wakati Kweli:
                block = fp.read(bs)
                ikiwa sio block:
                    koma
                read += len(block)
                tfp.write(block)
                blocknum += 1
                ikiwa reporthook:
                    reporthook(blocknum, bs, size)

    ikiwa size >= 0 na read < size:
        ashiria ContentTooShortError(
            "retrieval incomplete: got only %i out of %i bytes"
            % (read, size), result)

    rudisha result

eleza urlcleanup():
    """Clean up temporary files kutoka urlretrieve calls."""
    kila temp_file kwenye _url_tempfiles:
        jaribu:
            os.unlink(temp_file)
        tatizo OSError:
            pita

    toa _url_tempfiles[:]
    global _opener
    ikiwa _opener:
        _opener = Tupu

# copied kutoka cookielib.py
_cut_port_re = re.compile(r":\d+$", re.ASCII)
eleza request_host(request):
    """Return request-host, kama defined by RFC 2965.

    Variation kutoka RFC: returned value ni lowercased, kila convenient
    comparison.

    """
    url = request.full_url
    host = urlparse(url)[1]
    ikiwa host == "":
        host = request.get_header("Host", "")

    # remove port, ikiwa present
    host = _cut_port_re.sub("", host, 1)
    rudisha host.lower()

kundi Request:

    eleza __init__(self, url, data=Tupu, headers={},
                 origin_req_host=Tupu, unverifiable=Uongo,
                 method=Tupu):
        self.full_url = url
        self.headers = {}
        self.unredirected_hdrs = {}
        self._data = Tupu
        self.data = data
        self._tunnel_host = Tupu
        kila key, value kwenye headers.items():
            self.add_header(key, value)
        ikiwa origin_req_host ni Tupu:
            origin_req_host = request_host(self)
        self.origin_req_host = origin_req_host
        self.unverifiable = unverifiable
        ikiwa method:
            self.method = method

    @property
    eleza full_url(self):
        ikiwa self.fragment:
            rudisha '{}#{}'.format(self._full_url, self.fragment)
        rudisha self._full_url

    @full_url.setter
    eleza full_url(self, url):
        # unwrap('<URL:type://host/path>') --> 'type://host/path'
        self._full_url = unwrap(url)
        self._full_url, self.fragment = _splittag(self._full_url)
        self._parse()

    @full_url.deleter
    eleza full_url(self):
        self._full_url = Tupu
        self.fragment = Tupu
        self.selector = ''

    @property
    eleza data(self):
        rudisha self._data

    @data.setter
    eleza data(self, data):
        ikiwa data != self._data:
            self._data = data
            # issue 16464
            # ikiwa we change data we need to remove content-length header
            # (cause it's most probably calculated kila previous value)
            ikiwa self.has_header("Content-length"):
                self.remove_header("Content-length")

    @data.deleter
    eleza data(self):
        self.data = Tupu

    eleza _parse(self):
        self.type, rest = _splittype(self._full_url)
        ikiwa self.type ni Tupu:
            ashiria ValueError("unknown url type: %r" % self.full_url)
        self.host, self.selector = _splithost(rest)
        ikiwa self.host:
            self.host = unquote(self.host)

    eleza get_method(self):
        """Return a string indicating the HTTP request method."""
        default_method = "POST" ikiwa self.data ni sio Tupu isipokua "GET"
        rudisha getattr(self, 'method', default_method)

    eleza get_full_url(self):
        rudisha self.full_url

    eleza set_proxy(self, host, type):
        ikiwa self.type == 'https' na sio self._tunnel_host:
            self._tunnel_host = self.host
        isipokua:
            self.type= type
            self.selector = self.full_url
        self.host = host

    eleza has_proxy(self):
        rudisha self.selector == self.full_url

    eleza add_header(self, key, val):
        # useful kila something like authentication
        self.headers[key.capitalize()] = val

    eleza add_unredirected_header(self, key, val):
        # will sio be added to a redirected request
        self.unredirected_hdrs[key.capitalize()] = val

    eleza has_header(self, header_name):
        rudisha (header_name kwenye self.headers ama
                header_name kwenye self.unredirected_hdrs)

    eleza get_header(self, header_name, default=Tupu):
        rudisha self.headers.get(
            header_name,
            self.unredirected_hdrs.get(header_name, default))

    eleza remove_header(self, header_name):
        self.headers.pop(header_name, Tupu)
        self.unredirected_hdrs.pop(header_name, Tupu)

    eleza header_items(self):
        hdrs = {**self.unredirected_hdrs, **self.headers}
        rudisha list(hdrs.items())

kundi OpenerDirector:
    eleza __init__(self):
        client_version = "Python-urllib/%s" % __version__
        self.addheaders = [('User-agent', client_version)]
        # self.handlers ni retained only kila backward compatibility
        self.handlers = []
        # manage the individual handlers
        self.handle_open = {}
        self.handle_error = {}
        self.process_response = {}
        self.process_request = {}

    eleza add_handler(self, handler):
        ikiwa sio hasattr(handler, "add_parent"):
            ashiria TypeError("expected BaseHandler instance, got %r" %
                            type(handler))

        added = Uongo
        kila meth kwenye dir(handler):
            ikiwa meth kwenye ["redirect_request", "do_open", "proxy_open"]:
                # oops, coincidental match
                endelea

            i = meth.find("_")
            protocol = meth[:i]
            condition = meth[i+1:]

            ikiwa condition.startswith("error"):
                j = condition.find("_") + i + 1
                kind = meth[j+1:]
                jaribu:
                    kind = int(kind)
                tatizo ValueError:
                    pita
                lookup = self.handle_error.get(protocol, {})
                self.handle_error[protocol] = lookup
            lasivyo condition == "open":
                kind = protocol
                lookup = self.handle_open
            lasivyo condition == "response":
                kind = protocol
                lookup = self.process_response
            lasivyo condition == "request":
                kind = protocol
                lookup = self.process_request
            isipokua:
                endelea

            handlers = lookup.setdefault(kind, [])
            ikiwa handlers:
                bisect.insort(handlers, handler)
            isipokua:
                handlers.append(handler)
            added = Kweli

        ikiwa added:
            bisect.insort(self.handlers, handler)
            handler.add_parent(self)

    eleza close(self):
        # Only exists kila backwards compatibility.
        pita

    eleza _call_chain(self, chain, kind, meth_name, *args):
        # Handlers ashiria an exception ikiwa no one isipokua should try to handle
        # the request, ama rudisha Tupu ikiwa they can't but another handler
        # could.  Otherwise, they rudisha the response.
        handlers = chain.get(kind, ())
        kila handler kwenye handlers:
            func = getattr(handler, meth_name)
            result = func(*args)
            ikiwa result ni sio Tupu:
                rudisha result

    eleza open(self, fullurl, data=Tupu, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        # accept a URL ama a Request object
        ikiwa isinstance(fullurl, str):
            req = Request(fullurl, data)
        isipokua:
            req = fullurl
            ikiwa data ni sio Tupu:
                req.data = data

        req.timeout = timeout
        protocol = req.type

        # pre-process request
        meth_name = protocol+"_request"
        kila processor kwenye self.process_request.get(protocol, []):
            meth = getattr(processor, meth_name)
            req = meth(req)

        sys.audit('urllib.Request', req.full_url, req.data, req.headers, req.get_method())
        response = self._open(req, data)

        # post-process response
        meth_name = protocol+"_response"
        kila processor kwenye self.process_response.get(protocol, []):
            meth = getattr(processor, meth_name)
            response = meth(req, response)

        rudisha response

    eleza _open(self, req, data=Tupu):
        result = self._call_chain(self.handle_open, 'default',
                                  'default_open', req)
        ikiwa result:
            rudisha result

        protocol = req.type
        result = self._call_chain(self.handle_open, protocol, protocol +
                                  '_open', req)
        ikiwa result:
            rudisha result

        rudisha self._call_chain(self.handle_open, 'unknown',
                                'unknown_open', req)

    eleza error(self, proto, *args):
        ikiwa proto kwenye ('http', 'https'):
            # XXX http[s] protocols are special-cased
            dict = self.handle_error['http'] # https ni sio different than http
            proto = args[2]  # YUCK!
            meth_name = 'http_error_%s' % proto
            http_err = 1
            orig_args = args
        isipokua:
            dict = self.handle_error
            meth_name = proto + '_error'
            http_err = 0
        args = (dict, proto, meth_name) + args
        result = self._call_chain(*args)
        ikiwa result:
            rudisha result

        ikiwa http_err:
            args = (dict, 'default', 'http_error_default') + orig_args
            rudisha self._call_chain(*args)

# XXX probably also want an abstract factory that knows when it makes
# sense to skip a superkundi kwenye favor of a subkundi na when it might
# make sense to include both

eleza build_opener(*handlers):
    """Create an opener object kutoka a list of handlers.

    The opener will use several default handlers, including support
    kila HTTP, FTP na when applicable HTTPS.

    If any of the handlers pitaed kama arguments are subclasses of the
    default handlers, the default handlers will sio be used.
    """
    opener = OpenerDirector()
    default_classes = [ProxyHandler, UnknownHandler, HTTPHandler,
                       HTTPDefaultErrorHandler, HTTPRedirectHandler,
                       FTPHandler, FileHandler, HTTPErrorProcessor,
                       DataHandler]
    ikiwa hasattr(http.client, "HTTPSConnection"):
        default_classes.append(HTTPSHandler)
    skip = set()
    kila klass kwenye default_classes:
        kila check kwenye handlers:
            ikiwa isinstance(check, type):
                ikiwa issubclass(check, klass):
                    skip.add(klass)
            lasivyo isinstance(check, klass):
                skip.add(klass)
    kila klass kwenye skip:
        default_classes.remove(klass)

    kila klass kwenye default_classes:
        opener.add_handler(klass())

    kila h kwenye handlers:
        ikiwa isinstance(h, type):
            h = h()
        opener.add_handler(h)
    rudisha opener

kundi BaseHandler:
    handler_order = 500

    eleza add_parent(self, parent):
        self.parent = parent

    eleza close(self):
        # Only exists kila backwards compatibility
        pita

    eleza __lt__(self, other):
        ikiwa sio hasattr(other, "handler_order"):
            # Try to preserve the old behavior of having custom classes
            # inserted after default ones (works only kila custom user
            # classes which are sio aware of handler_order).
            rudisha Kweli
        rudisha self.handler_order < other.handler_order


kundi HTTPErrorProcessor(BaseHandler):
    """Process HTTP error responses."""
    handler_order = 1000  # after all other processing

    eleza http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, na accepted.
        ikiwa sio (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)

        rudisha response

    https_response = http_response

kundi HTTPDefaultErrorHandler(BaseHandler):
    eleza http_error_default(self, req, fp, code, msg, hdrs):
        ashiria HTTPError(req.full_url, code, msg, hdrs, fp)

kundi HTTPRedirectHandler(BaseHandler):
    # maximum number of redirections to any single URL
    # this ni needed because of the state that cookies introduce
    max_repeats = 4
    # maximum total number of redirections (regardless of URL) before
    # assuming we're kwenye a loop
    max_redirections = 10

    eleza redirect_request(self, req, fp, code, msg, headers, newurl):
        """Return a Request ama Tupu kwenye response to a redirect.

        This ni called by the http_error_30x methods when a
        redirection response ni received.  If a redirection should
        take place, rudisha a new Request to allow http_error_30x to
        perform the redirect.  Otherwise, ashiria HTTPError ikiwa no-one
        isipokua should try to handle this url.  Return Tupu ikiwa you can't
        but another Handler might.
        """
        m = req.get_method()
        ikiwa (sio (code kwenye (301, 302, 303, 307) na m kwenye ("GET", "HEAD")
            ama code kwenye (301, 302, 303) na m == "POST")):
            ashiria HTTPError(req.full_url, code, msg, headers, fp)

        # Strictly (according to RFC 2616), 301 ama 302 kwenye response to
        # a POST MUST NOT cause a redirection without confirmation
        # kutoka the user (of urllib.request, kwenye this case).  In practice,
        # essentially all clients do redirect kwenye this case, so we do
        # the same.

        # Be conciliant ukijumuisha URIs containing a space.  This ni mainly
        # redundant ukijumuisha the more complete encoding done kwenye http_error_302(),
        # but it ni kept kila compatibility ukijumuisha other callers.
        newurl = newurl.replace(' ', '%20')

        CONTENT_HEADERS = ("content-length", "content-type")
        newheaders = {k: v kila k, v kwenye req.headers.items()
                      ikiwa k.lower() haiko kwenye CONTENT_HEADERS}
        rudisha Request(newurl,
                       headers=newheaders,
                       origin_req_host=req.origin_req_host,
                       unverifiable=Kweli)

    # Implementation note: To avoid the server sending us into an
    # infinite loop, the request object needs to track what URLs we
    # have already seen.  Do this by adding a handler-specific
    # attribute to the Request object.
    eleza http_error_302(self, req, fp, code, msg, headers):
        # Some servers (incorrectly) rudisha multiple Location headers
        # (so probably same goes kila URI).  Use first header.
        ikiwa "location" kwenye headers:
            newurl = headers["location"]
        lasivyo "uri" kwenye headers:
            newurl = headers["uri"]
        isipokua:
            rudisha

        # fix a possible malformed URL
        urlparts = urlparse(newurl)

        # For security reasons we don't allow redirection to anything other
        # than http, https ama ftp.

        ikiwa urlparts.scheme haiko kwenye ('http', 'https', 'ftp', ''):
            ashiria HTTPError(
                newurl, code,
                "%s - Redirection to url '%s' ni sio allowed" % (msg, newurl),
                headers, fp)

        ikiwa sio urlparts.path na urlparts.netloc:
            urlparts = list(urlparts)
            urlparts[2] = "/"
        newurl = urlunparse(urlparts)

        # http.client.parse_headers() decodes kama ISO-8859-1.  Recover the
        # original bytes na percent-encode non-ASCII bytes, na any special
        # characters such kama the space.
        newurl = quote(
            newurl, encoding="iso-8859-1", safe=string.punctuation)
        newurl = urljoin(req.full_url, newurl)

        # XXX Probably want to forget about the state of the current
        # request, although that might interact poorly ukijumuisha other
        # handlers that also use handler-specific request attributes
        new = self.redirect_request(req, fp, code, msg, headers, newurl)
        ikiwa new ni Tupu:
            rudisha

        # loop detection
        # .redirect_dict has a key url ikiwa url was previously visited.
        ikiwa hasattr(req, 'redirect_dict'):
            visited = new.redirect_dict = req.redirect_dict
            ikiwa (visited.get(newurl, 0) >= self.max_repeats ama
                len(visited) >= self.max_redirections):
                ashiria HTTPError(req.full_url, code,
                                self.inf_msg + msg, headers, fp)
        isipokua:
            visited = new.redirect_dict = req.redirect_dict = {}
        visited[newurl] = visited.get(newurl, 0) + 1

        # Don't close the fp until we are sure that we won't use it
        # ukijumuisha HTTPError.
        fp.read()
        fp.close()

        rudisha self.parent.open(new, timeout=req.timeout)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

    inf_msg = "The HTTP server returned a redirect error that would " \
              "lead to an infinite loop.\n" \
              "The last 30x error message was:\n"


eleza _parse_proxy(proxy):
    """Return (scheme, user, pitaword, host/port) given a URL ama an authority.

    If a URL ni supplied, it must have an authority (host:port) component.
    According to RFC 3986, having an authority component means the URL must
    have two slashes after the scheme.
    """
    scheme, r_scheme = _splittype(proxy)
    ikiwa sio r_scheme.startswith("/"):
        # authority
        scheme = Tupu
        authority = proxy
    isipokua:
        # URL
        ikiwa sio r_scheme.startswith("//"):
            ashiria ValueError("proxy URL ukijumuisha no authority: %r" % proxy)
        # We have an authority, so kila RFC 3986-compliant URLs (by ss 3.
        # na 3.3.), path ni empty ama starts ukijumuisha '/'
        end = r_scheme.find("/", 2)
        ikiwa end == -1:
            end = Tupu
        authority = r_scheme[2:end]
    userinfo, hostport = _splituser(authority)
    ikiwa userinfo ni sio Tupu:
        user, pitaword = _splitpitawd(userinfo)
    isipokua:
        user = pitaword = Tupu
    rudisha scheme, user, pitaword, hostport

kundi ProxyHandler(BaseHandler):
    # Proxies must be kwenye front
    handler_order = 100

    eleza __init__(self, proxies=Tupu):
        ikiwa proxies ni Tupu:
            proxies = getproxies()
        assert hasattr(proxies, 'keys'), "proxies must be a mapping"
        self.proxies = proxies
        kila type, url kwenye proxies.items():
            type = type.lower()
            setattr(self, '%s_open' % type,
                    lambda r, proxy=url, type=type, meth=self.proxy_open:
                        meth(r, proxy, type))

    eleza proxy_open(self, req, proxy, type):
        orig_type = req.type
        proxy_type, user, pitaword, hostport = _parse_proxy(proxy)
        ikiwa proxy_type ni Tupu:
            proxy_type = orig_type

        ikiwa req.host na proxy_bypita(req.host):
            rudisha Tupu

        ikiwa user na pitaword:
            user_pita = '%s:%s' % (unquote(user),
                                   unquote(pitaword))
            creds = base64.b64encode(user_pita.encode()).decode("ascii")
            req.add_header('Proxy-authorization', 'Basic ' + creds)
        hostport = unquote(hostport)
        req.set_proxy(hostport, proxy_type)
        ikiwa orig_type == proxy_type ama orig_type == 'https':
            # let other handlers take care of it
            rudisha Tupu
        isipokua:
            # need to start over, because the other handlers don't
            # grok the proxy's URL type
            # e.g. ikiwa we have a constructor arg proxies like so:
            # {'http': 'ftp://proxy.example.com'}, we may end up turning
            # a request kila http://acme.example.com/a into one for
            # ftp://proxy.example.com/a
            rudisha self.parent.open(req, timeout=req.timeout)

kundi HTTPPasswordMgr:

    eleza __init__(self):
        self.pitawd = {}

    eleza add_pitaword(self, realm, uri, user, pitawd):
        # uri could be a single URI ama a sequence
        ikiwa isinstance(uri, str):
            uri = [uri]
        ikiwa realm haiko kwenye self.pitawd:
            self.pitawd[realm] = {}
        kila default_port kwenye Kweli, Uongo:
            reduced_uri = tuple(
                self.reduce_uri(u, default_port) kila u kwenye uri)
            self.pitawd[realm][reduced_uri] = (user, pitawd)

    eleza find_user_pitaword(self, realm, authuri):
        domains = self.pitawd.get(realm, {})
        kila default_port kwenye Kweli, Uongo:
            reduced_authuri = self.reduce_uri(authuri, default_port)
            kila uris, authinfo kwenye domains.items():
                kila uri kwenye uris:
                    ikiwa self.is_suburi(uri, reduced_authuri):
                        rudisha authinfo
        rudisha Tupu, Tupu

    eleza reduce_uri(self, uri, default_port=Kweli):
        """Accept authority ama URI na extract only the authority na path."""
        # note HTTP URLs do sio have a userinfo component
        parts = urlsplit(uri)
        ikiwa parts[1]:
            # URI
            scheme = parts[0]
            authority = parts[1]
            path = parts[2] ama '/'
        isipokua:
            # host ama host:port
            scheme = Tupu
            authority = uri
            path = '/'
        host, port = _splitport(authority)
        ikiwa default_port na port ni Tupu na scheme ni sio Tupu:
            dport = {"http": 80,
                     "https": 443,
                     }.get(scheme)
            ikiwa dport ni sio Tupu:
                authority = "%s:%d" % (host, dport)
        rudisha authority, path

    eleza is_suburi(self, base, test):
        """Check ikiwa test ni below base kwenye a URI tree

        Both args must be URIs kwenye reduced form.
        """
        ikiwa base == test:
            rudisha Kweli
        ikiwa base[0] != test[0]:
            rudisha Uongo
        common = posixpath.commonprefix((base[1], test[1]))
        ikiwa len(common) == len(base[1]):
            rudisha Kweli
        rudisha Uongo


kundi HTTPPasswordMgrWithDefaultRealm(HTTPPasswordMgr):

    eleza find_user_pitaword(self, realm, authuri):
        user, pitaword = HTTPPasswordMgr.find_user_pitaword(self, realm,
                                                            authuri)
        ikiwa user ni sio Tupu:
            rudisha user, pitaword
        rudisha HTTPPasswordMgr.find_user_pitaword(self, Tupu, authuri)


kundi HTTPPasswordMgrWithPriorAuth(HTTPPasswordMgrWithDefaultRealm):

    eleza __init__(self, *args, **kwargs):
        self.authenticated = {}
        super().__init__(*args, **kwargs)

    eleza add_pitaword(self, realm, uri, user, pitawd, is_authenticated=Uongo):
        self.update_authenticated(uri, is_authenticated)
        # Add a default kila prior auth requests
        ikiwa realm ni sio Tupu:
            super().add_pitaword(Tupu, uri, user, pitawd)
        super().add_pitaword(realm, uri, user, pitawd)

    eleza update_authenticated(self, uri, is_authenticated=Uongo):
        # uri could be a single URI ama a sequence
        ikiwa isinstance(uri, str):
            uri = [uri]

        kila default_port kwenye Kweli, Uongo:
            kila u kwenye uri:
                reduced_uri = self.reduce_uri(u, default_port)
                self.authenticated[reduced_uri] = is_authenticated

    eleza is_authenticated(self, authuri):
        kila default_port kwenye Kweli, Uongo:
            reduced_authuri = self.reduce_uri(authuri, default_port)
            kila uri kwenye self.authenticated:
                ikiwa self.is_suburi(uri, reduced_authuri):
                    rudisha self.authenticated[uri]


kundi AbstractBasicAuthHandler:

    # XXX this allows kila multiple auth-schemes, but will stupidly pick
    # the last one ukijumuisha a realm specified.

    # allow kila double- na single-quoted realm values
    # (single quotes are a violation of the RFC, but appear kwenye the wild)
    rx = re.compile('(?:.*,)*[ \t]*([^ \t]+)[ \t]+'
                    'realm=(["\']?)([^"\']*)\\2', re.I)

    # XXX could pre-emptively send auth info already accepted (RFC 2617,
    # end of section 2, na section 1.2 immediately after "credentials"
    # production).

    eleza __init__(self, pitaword_mgr=Tupu):
        ikiwa pitaword_mgr ni Tupu:
            pitaword_mgr = HTTPPasswordMgr()
        self.pitawd = pitaword_mgr
        self.add_pitaword = self.pitawd.add_pitaword

    eleza http_error_auth_reqed(self, authreq, host, req, headers):
        # host may be an authority (without userinfo) ama a URL ukijumuisha an
        # authority
        # XXX could be multiple headers
        authreq = headers.get(authreq, Tupu)

        ikiwa authreq:
            scheme = authreq.split()[0]
            ikiwa scheme.lower() != 'basic':
                ashiria ValueError("AbstractBasicAuthHandler does not"
                                 " support the following scheme: '%s'" %
                                 scheme)
            isipokua:
                mo = AbstractBasicAuthHandler.rx.search(authreq)
                ikiwa mo:
                    scheme, quote, realm = mo.groups()
                    ikiwa quote haiko kwenye ['"',"'"]:
                        warnings.warn("Basic Auth Realm was unquoted",
                                      UserWarning, 2)
                    ikiwa scheme.lower() == 'basic':
                        rudisha self.retry_http_basic_auth(host, req, realm)

    eleza retry_http_basic_auth(self, host, req, realm):
        user, pw = self.pitawd.find_user_pitaword(realm, host)
        ikiwa pw ni sio Tupu:
            raw = "%s:%s" % (user, pw)
            auth = "Basic " + base64.b64encode(raw.encode()).decode("ascii")
            ikiwa req.get_header(self.auth_header, Tupu) == auth:
                rudisha Tupu
            req.add_unredirected_header(self.auth_header, auth)
            rudisha self.parent.open(req, timeout=req.timeout)
        isipokua:
            rudisha Tupu

    eleza http_request(self, req):
        ikiwa (sio hasattr(self.pitawd, 'is_authenticated') ama
           sio self.pitawd.is_authenticated(req.full_url)):
            rudisha req

        ikiwa sio req.has_header('Authorization'):
            user, pitawd = self.pitawd.find_user_pitaword(Tupu, req.full_url)
            credentials = '{0}:{1}'.format(user, pitawd).encode()
            auth_str = base64.standard_b64encode(credentials).decode()
            req.add_unredirected_header('Authorization',
                                        'Basic {}'.format(auth_str.strip()))
        rudisha req

    eleza http_response(self, req, response):
        ikiwa hasattr(self.pitawd, 'is_authenticated'):
            ikiwa 200 <= response.code < 300:
                self.pitawd.update_authenticated(req.full_url, Kweli)
            isipokua:
                self.pitawd.update_authenticated(req.full_url, Uongo)
        rudisha response

    https_request = http_request
    https_response = http_response



kundi HTTPBasicAuthHandler(AbstractBasicAuthHandler, BaseHandler):

    auth_header = 'Authorization'

    eleza http_error_401(self, req, fp, code, msg, headers):
        url = req.full_url
        response = self.http_error_auth_reqed('www-authenticate',
                                          url, req, headers)
        rudisha response


kundi ProxyBasicAuthHandler(AbstractBasicAuthHandler, BaseHandler):

    auth_header = 'Proxy-authorization'

    eleza http_error_407(self, req, fp, code, msg, headers):
        # http_error_auth_reqed requires that there ni no userinfo component kwenye
        # authority.  Assume there isn't one, since urllib.request does sio (and
        # should not, RFC 3986 s. 3.2.1) support requests kila URLs containing
        # userinfo.
        authority = req.host
        response = self.http_error_auth_reqed('proxy-authenticate',
                                          authority, req, headers)
        rudisha response


# Return n random bytes.
_randombytes = os.urandom


kundi AbstractDigestAuthHandler:
    # Digest authentication ni specified kwenye RFC 2617.

    # XXX The client does sio inpect the Authentication-Info header
    # kwenye a successful response.

    # XXX It should be possible to test this implementation against
    # a mock server that just generates a static set of challenges.

    # XXX qop="auth-int" supports ni shaky

    eleza __init__(self, pitawd=Tupu):
        ikiwa pitawd ni Tupu:
            pitawd = HTTPPasswordMgr()
        self.pitawd = pitawd
        self.add_pitaword = self.pitawd.add_pitaword
        self.retried = 0
        self.nonce_count = 0
        self.last_nonce = Tupu

    eleza reset_retry_count(self):
        self.retried = 0

    eleza http_error_auth_reqed(self, auth_header, host, req, headers):
        authreq = headers.get(auth_header, Tupu)
        ikiwa self.retried > 5:
            # Don't fail endlessly - ikiwa we failed once, we'll probably
            # fail a second time. Hm. Unless the Password Manager is
            # prompting kila the information. Crap. This isn't great
            # but it's better than the current 'repeat until recursion
            # depth exceeded' approach <wink>
            ashiria HTTPError(req.full_url, 401, "digest auth failed",
                            headers, Tupu)
        isipokua:
            self.retried += 1
        ikiwa authreq:
            scheme = authreq.split()[0]
            ikiwa scheme.lower() == 'digest':
                rudisha self.retry_http_digest_auth(req, authreq)
            lasivyo scheme.lower() != 'basic':
                ashiria ValueError("AbstractDigestAuthHandler does sio support"
                                 " the following scheme: '%s'" % scheme)

    eleza retry_http_digest_auth(self, req, auth):
        token, challenge = auth.split(' ', 1)
        chal = parse_keqv_list(filter(Tupu, parse_http_list(challenge)))
        auth = self.get_authorization(req, chal)
        ikiwa auth:
            auth_val = 'Digest %s' % auth
            ikiwa req.headers.get(self.auth_header, Tupu) == auth_val:
                rudisha Tupu
            req.add_unredirected_header(self.auth_header, auth_val)
            resp = self.parent.open(req, timeout=req.timeout)
            rudisha resp

    eleza get_cnonce(self, nonce):
        # The cnonce-value ni an opaque
        # quoted string value provided by the client na used by both client
        # na server to avoid chosen plaintext attacks, to provide mutual
        # authentication, na to provide some message integrity protection.
        # This isn't a fabulous effort, but it's probably Good Enough.
        s = "%s:%s:%s:" % (self.nonce_count, nonce, time.ctime())
        b = s.encode("ascii") + _randombytes(8)
        dig = hashlib.sha1(b).hexdigest()
        rudisha dig[:16]

    eleza get_authorization(self, req, chal):
        jaribu:
            realm = chal['realm']
            nonce = chal['nonce']
            qop = chal.get('qop')
            algorithm = chal.get('algorithm', 'MD5')
            # mod_digest doesn't send an opaque, even though it isn't
            # supposed to be optional
            opaque = chal.get('opaque', Tupu)
        tatizo KeyError:
            rudisha Tupu

        H, KD = self.get_algorithm_impls(algorithm)
        ikiwa H ni Tupu:
            rudisha Tupu

        user, pw = self.pitawd.find_user_pitaword(realm, req.full_url)
        ikiwa user ni Tupu:
            rudisha Tupu

        # XXX sio implemented yet
        ikiwa req.data ni sio Tupu:
            entdig = self.get_entity_digest(req.data, chal)
        isipokua:
            entdig = Tupu

        A1 = "%s:%s:%s" % (user, realm, pw)
        A2 = "%s:%s" % (req.get_method(),
                        # XXX selector: what about proxies na full urls
                        req.selector)
        ikiwa qop == 'auth':
            ikiwa nonce == self.last_nonce:
                self.nonce_count += 1
            isipokua:
                self.nonce_count = 1
                self.last_nonce = nonce
            ncvalue = '%08x' % self.nonce_count
            cnonce = self.get_cnonce(nonce)
            noncebit = "%s:%s:%s:%s:%s" % (nonce, ncvalue, cnonce, qop, H(A2))
            respdig = KD(H(A1), noncebit)
        lasivyo qop ni Tupu:
            respdig = KD(H(A1), "%s:%s" % (nonce, H(A2)))
        isipokua:
            # XXX handle auth-int.
            ashiria URLError("qop '%s' ni sio supported." % qop)

        # XXX should the partial digests be encoded too?

        base = 'username="%s", realm="%s", nonce="%s", uri="%s", ' \
               'response="%s"' % (user, realm, nonce, req.selector,
                                  respdig)
        ikiwa opaque:
            base += ', opaque="%s"' % opaque
        ikiwa entdig:
            base += ', digest="%s"' % entdig
        base += ', algorithm="%s"' % algorithm
        ikiwa qop:
            base += ', qop=auth, nc=%s, cnonce="%s"' % (ncvalue, cnonce)
        rudisha base

    eleza get_algorithm_impls(self, algorithm):
        # lambdas assume digest modules are imported at the top level
        ikiwa algorithm == 'MD5':
            H = lambda x: hashlib.md5(x.encode("ascii")).hexdigest()
        lasivyo algorithm == 'SHA':
            H = lambda x: hashlib.sha1(x.encode("ascii")).hexdigest()
        # XXX MD5-sess
        isipokua:
            ashiria ValueError("Unsupported digest authentication "
                             "algorithm %r" % algorithm)
        KD = lambda s, d: H("%s:%s" % (s, d))
        rudisha H, KD

    eleza get_entity_digest(self, data, chal):
        # XXX sio implemented yet
        rudisha Tupu


kundi HTTPDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    """An authentication protocol defined by RFC 2069

    Digest authentication improves on basic authentication because it
    does sio transmit pitawords kwenye the clear.
    """

    auth_header = 'Authorization'
    handler_order = 490  # before Basic auth

    eleza http_error_401(self, req, fp, code, msg, headers):
        host = urlparse(req.full_url)[1]
        retry = self.http_error_auth_reqed('www-authenticate',
                                           host, req, headers)
        self.reset_retry_count()
        rudisha retry


kundi ProxyDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):

    auth_header = 'Proxy-Authorization'
    handler_order = 490  # before Basic auth

    eleza http_error_407(self, req, fp, code, msg, headers):
        host = req.host
        retry = self.http_error_auth_reqed('proxy-authenticate',
                                           host, req, headers)
        self.reset_retry_count()
        rudisha retry

kundi AbstractHTTPHandler(BaseHandler):

    eleza __init__(self, debuglevel=0):
        self._debuglevel = debuglevel

    eleza set_http_debuglevel(self, level):
        self._debuglevel = level

    eleza _get_content_length(self, request):
        rudisha http.client.HTTPConnection._get_content_length(
            request.data,
            request.get_method())

    eleza do_request_(self, request):
        host = request.host
        ikiwa sio host:
            ashiria URLError('no host given')

        ikiwa request.data ni sio Tupu:  # POST
            data = request.data
            ikiwa isinstance(data, str):
                msg = "POST data should be bytes, an iterable of bytes, " \
                      "or a file object. It cansio be of type str."
                ashiria TypeError(msg)
            ikiwa sio request.has_header('Content-type'):
                request.add_unredirected_header(
                    'Content-type',
                    'application/x-www-form-urlencoded')
            ikiwa (sio request.has_header('Content-length')
                    na sio request.has_header('Transfer-encoding')):
                content_length = self._get_content_length(request)
                ikiwa content_length ni sio Tupu:
                    request.add_unredirected_header(
                            'Content-length', str(content_length))
                isipokua:
                    request.add_unredirected_header(
                            'Transfer-encoding', 'chunked')

        sel_host = host
        ikiwa request.has_proxy():
            scheme, sel = _splittype(request.selector)
            sel_host, sel_path = _splithost(sel)
        ikiwa sio request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        kila name, value kwenye self.parent.addheaders:
            name = name.capitalize()
            ikiwa sio request.has_header(name):
                request.add_unredirected_header(name, value)

        rudisha request

    eleza do_open(self, http_class, req, **http_conn_args):
        """Return an HTTPResponse object kila the request, using http_class.

        http_class must implement the HTTPConnection API kutoka http.client.
        """
        host = req.host
        ikiwa sio host:
            ashiria URLError('no host given')

        # will parse host:port
        h = http_class(host, timeout=req.timeout, **http_conn_args)
        h.set_debuglevel(self._debuglevel)

        headers = dict(req.unredirected_hdrs)
        headers.update({k: v kila k, v kwenye req.headers.items()
                        ikiwa k haiko kwenye headers})

        # TODO(jhylton): Should this be redesigned to handle
        # persistent connections?

        # We want to make an HTTP/1.1 request, but the addinfourl
        # kundi isn't prepared to deal ukijumuisha a persistent connection.
        # It will try to read all remaining data kutoka the socket,
        # which will block wakati the server waits kila the next request.
        # So make sure the connection gets closed after the (only)
        # request.
        headers["Connection"] = "close"
        headers = {name.title(): val kila name, val kwenye headers.items()}

        ikiwa req._tunnel_host:
            tunnel_headers = {}
            proxy_auth_hdr = "Proxy-Authorization"
            ikiwa proxy_auth_hdr kwenye headers:
                tunnel_headers[proxy_auth_hdr] = headers[proxy_auth_hdr]
                # Proxy-Authorization should sio be sent to origin
                # server.
                toa headers[proxy_auth_hdr]
            h.set_tunnel(req._tunnel_host, headers=tunnel_headers)

        jaribu:
            jaribu:
                h.request(req.get_method(), req.selector, req.data, headers,
                          encode_chunked=req.has_header('Transfer-encoding'))
            tatizo OSError kama err: # timeout error
                ashiria URLError(err)
            r = h.getresponse()
        tatizo:
            h.close()
            raise

        # If the server does sio send us a 'Connection: close' header,
        # HTTPConnection assumes the socket should be left open. Manually
        # mark the socket to be closed when this response object goes away.
        ikiwa h.sock:
            h.sock.close()
            h.sock = Tupu

        r.url = req.get_full_url()
        # This line replaces the .msg attribute of the HTTPResponse
        # ukijumuisha .headers, because urllib clients expect the response to
        # have the reason kwenye .msg.  It would be good to mark this
        # attribute ni deprecated na get then to use info() ama
        # .headers.
        r.msg = r.reason
        rudisha r


kundi HTTPHandler(AbstractHTTPHandler):

    eleza http_open(self, req):
        rudisha self.do_open(http.client.HTTPConnection, req)

    http_request = AbstractHTTPHandler.do_request_

ikiwa hasattr(http.client, 'HTTPSConnection'):

    kundi HTTPSHandler(AbstractHTTPHandler):

        eleza __init__(self, debuglevel=0, context=Tupu, check_hostname=Tupu):
            AbstractHTTPHandler.__init__(self, debuglevel)
            self._context = context
            self._check_hostname = check_hostname

        eleza https_open(self, req):
            rudisha self.do_open(http.client.HTTPSConnection, req,
                context=self._context, check_hostname=self._check_hostname)

        https_request = AbstractHTTPHandler.do_request_

    __all__.append('HTTPSHandler')

kundi HTTPCookieProcessor(BaseHandler):
    eleza __init__(self, cookiejar=Tupu):
        agiza http.cookiejar
        ikiwa cookiejar ni Tupu:
            cookiejar = http.cookiejar.CookieJar()
        self.cookiejar = cookiejar

    eleza http_request(self, request):
        self.cookiejar.add_cookie_header(request)
        rudisha request

    eleza http_response(self, request, response):
        self.cookiejar.extract_cookies(response, request)
        rudisha response

    https_request = http_request
    https_response = http_response

kundi UnknownHandler(BaseHandler):
    eleza unknown_open(self, req):
        type = req.type
        ashiria URLError('unknown url type: %s' % type)

eleza parse_keqv_list(l):
    """Parse list of key=value strings where keys are sio duplicated."""
    parsed = {}
    kila elt kwenye l:
        k, v = elt.split('=', 1)
        ikiwa v[0] == '"' na v[-1] == '"':
            v = v[1:-1]
        parsed[k] = v
    rudisha parsed

eleza parse_http_list(s):
    """Parse lists kama described by RFC 2068 Section 2.

    In particular, parse comma-separated lists where the elements of
    the list may include quoted-strings.  A quoted-string could
    contain a comma.  A non-quoted string could have quotes kwenye the
    middle.  Neither commas nor quotes count ikiwa they are escaped.
    Only double-quotes count, sio single-quotes.
    """
    res = []
    part = ''

    escape = quote = Uongo
    kila cur kwenye s:
        ikiwa escape:
            part += cur
            escape = Uongo
            endelea
        ikiwa quote:
            ikiwa cur == '\\':
                escape = Kweli
                endelea
            lasivyo cur == '"':
                quote = Uongo
            part += cur
            endelea

        ikiwa cur == ',':
            res.append(part)
            part = ''
            endelea

        ikiwa cur == '"':
            quote = Kweli

        part += cur

    # append last part
    ikiwa part:
        res.append(part)

    rudisha [part.strip() kila part kwenye res]

kundi FileHandler(BaseHandler):
    # Use local file ama FTP depending on form of URL
    eleza file_open(self, req):
        url = req.selector
        ikiwa url[:2] == '//' na url[2:3] != '/' na (req.host na
                req.host != 'localhost'):
            ikiwa sio req.host kwenye self.get_names():
                ashiria URLError("file:// scheme ni supported only on localhost")
        isipokua:
            rudisha self.open_local_file(req)

    # names kila the localhost
    names = Tupu
    eleza get_names(self):
        ikiwa FileHandler.names ni Tupu:
            jaribu:
                FileHandler.names = tuple(
                    socket.gethostbyname_ex('localhost')[2] +
                    socket.gethostbyname_ex(socket.gethostname())[2])
            tatizo socket.gaierror:
                FileHandler.names = (socket.gethostbyname('localhost'),)
        rudisha FileHandler.names

    # sio entirely sure what the rules are here
    eleza open_local_file(self, req):
        agiza email.utils
        agiza mimetypes
        host = req.host
        filename = req.selector
        localfile = url2pathname(filename)
        jaribu:
            stats = os.stat(localfile)
            size = stats.st_size
            modified = email.utils.formatdate(stats.st_mtime, usegmt=Kweli)
            mtype = mimetypes.guess_type(filename)[0]
            headers = email.message_from_string(
                'Content-type: %s\nContent-length: %d\nLast-modified: %s\n' %
                (mtype ama 'text/plain', size, modified))
            ikiwa host:
                host, port = _splitport(host)
            ikiwa sio host ama \
                (sio port na _safe_gethostbyname(host) kwenye self.get_names()):
                ikiwa host:
                    origurl = 'file://' + host + filename
                isipokua:
                    origurl = 'file://' + filename
                rudisha addinfourl(open(localfile, 'rb'), headers, origurl)
        tatizo OSError kama exp:
            ashiria URLError(exp)
        ashiria URLError('file sio on local host')

eleza _safe_gethostbyname(host):
    jaribu:
        rudisha socket.gethostbyname(host)
    tatizo socket.gaierror:
        rudisha Tupu

kundi FTPHandler(BaseHandler):
    eleza ftp_open(self, req):
        agiza ftplib
        agiza mimetypes
        host = req.host
        ikiwa sio host:
            ashiria URLError('ftp error: no host given')
        host, port = _splitport(host)
        ikiwa port ni Tupu:
            port = ftplib.FTP_PORT
        isipokua:
            port = int(port)

        # username/pitaword handling
        user, host = _splituser(host)
        ikiwa user:
            user, pitawd = _splitpitawd(user)
        isipokua:
            pitawd = Tupu
        host = unquote(host)
        user = user ama ''
        pitawd = pitawd ama ''

        jaribu:
            host = socket.gethostbyname(host)
        tatizo OSError kama msg:
            ashiria URLError(msg)
        path, attrs = _splitattr(req.selector)
        dirs = path.split('/')
        dirs = list(map(unquote, dirs))
        dirs, file = dirs[:-1], dirs[-1]
        ikiwa dirs na sio dirs[0]:
            dirs = dirs[1:]
        jaribu:
            fw = self.connect_ftp(user, pitawd, host, port, dirs, req.timeout)
            type = file na 'I' ama 'D'
            kila attr kwenye attrs:
                attr, value = _splitvalue(attr)
                ikiwa attr.lower() == 'type' na \
                   value kwenye ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
            fp, retrlen = fw.retrfile(file, type)
            headers = ""
            mtype = mimetypes.guess_type(req.full_url)[0]
            ikiwa mtype:
                headers += "Content-type: %s\n" % mtype
            ikiwa retrlen ni sio Tupu na retrlen >= 0:
                headers += "Content-length: %d\n" % retrlen
            headers = email.message_from_string(headers)
            rudisha addinfourl(fp, headers, req.full_url)
        tatizo ftplib.all_errors kama exp:
            exc = URLError('ftp error: %r' % exp)
            ashiria exc.with_traceback(sys.exc_info()[2])

    eleza connect_ftp(self, user, pitawd, host, port, dirs, timeout):
        rudisha ftpwrapper(user, pitawd, host, port, dirs, timeout,
                          persistent=Uongo)

kundi CacheFTPHandler(FTPHandler):
    # XXX would be nice to have pluggable cache strategies
    # XXX this stuff ni definitely sio thread safe
    eleza __init__(self):
        self.cache = {}
        self.timeout = {}
        self.soonest = 0
        self.delay = 60
        self.max_conns = 16

    eleza setTimeout(self, t):
        self.delay = t

    eleza setMaxConns(self, m):
        self.max_conns = m

    eleza connect_ftp(self, user, pitawd, host, port, dirs, timeout):
        key = user, host, port, '/'.join(dirs), timeout
        ikiwa key kwenye self.cache:
            self.timeout[key] = time.time() + self.delay
        isipokua:
            self.cache[key] = ftpwrapper(user, pitawd, host, port,
                                         dirs, timeout)
            self.timeout[key] = time.time() + self.delay
        self.check_cache()
        rudisha self.cache[key]

    eleza check_cache(self):
        # first check kila old ones
        t = time.time()
        ikiwa self.soonest <= t:
            kila k, v kwenye list(self.timeout.items()):
                ikiwa v < t:
                    self.cache[k].close()
                    toa self.cache[k]
                    toa self.timeout[k]
        self.soonest = min(list(self.timeout.values()))

        # then check the size
        ikiwa len(self.cache) == self.max_conns:
            kila k, v kwenye list(self.timeout.items()):
                ikiwa v == self.soonest:
                    toa self.cache[k]
                    toa self.timeout[k]
                    koma
            self.soonest = min(list(self.timeout.values()))

    eleza clear_cache(self):
        kila conn kwenye self.cache.values():
            conn.close()
        self.cache.clear()
        self.timeout.clear()

kundi DataHandler(BaseHandler):
    eleza data_open(self, req):
        # data URLs kama specified kwenye RFC 2397.
        #
        # ignores POSTed data
        #
        # syntax:
        # dataurl   := "data:" [ mediatype ] [ ";base64" ] "," data
        # mediatype := [ type "/" subtype ] *( ";" parameter )
        # data      := *urlchar
        # parameter := attribute "=" value
        url = req.full_url

        scheme, data = url.split(":",1)
        mediatype, data = data.split(",",1)

        # even base64 encoded data URLs might be quoted so unquote kwenye any case:
        data = unquote_to_bytes(data)
        ikiwa mediatype.endswith(";base64"):
            data = base64.decodebytes(data)
            mediatype = mediatype[:-7]

        ikiwa sio mediatype:
            mediatype = "text/plain;charset=US-ASCII"

        headers = email.message_from_string("Content-type: %s\nContent-length: %d\n" %
            (mediatype, len(data)))

        rudisha addinfourl(io.BytesIO(data), headers, url)


# Code move kutoka the old urllib module

MAXFTPCACHE = 10        # Trim the ftp cache beyond this size

# Helper kila non-unix systems
ikiwa os.name == 'nt':
    kutoka nturl2path agiza url2pathname, pathname2url
isipokua:
    eleza url2pathname(pathname):
        """OS-specific conversion kutoka a relative URL of the 'file' scheme
        to a file system path; sio recommended kila general use."""
        rudisha unquote(pathname)

    eleza pathname2url(pathname):
        """OS-specific conversion kutoka a file system path to a relative URL
        of the 'file' scheme; sio recommended kila general use."""
        rudisha quote(pathname)


ftpcache = {}


kundi URLopener:
    """Class to open URLs.
    This ni a kundi rather than just a subroutine because we may need
    more than one set of global protocol-specific options.
    Note -- this ni a base kundi kila those who don't want the
    automatic handling of errors type 302 (relocated) na 401
    (authorization needed)."""

    __tempfiles = Tupu

    version = "Python-urllib/%s" % __version__

    # Constructor
    eleza __init__(self, proxies=Tupu, **x509):
        msg = "%(class)s style of invoking requests ni deprecated. " \
              "Use newer urlopen functions/methods" % {'class': self.__class__.__name__}
        warnings.warn(msg, DeprecationWarning, stacklevel=3)
        ikiwa proxies ni Tupu:
            proxies = getproxies()
        assert hasattr(proxies, 'keys'), "proxies must be a mapping"
        self.proxies = proxies
        self.key_file = x509.get('key_file')
        self.cert_file = x509.get('cert_file')
        self.addheaders = [('User-Agent', self.version), ('Accept', '*/*')]
        self.__tempfiles = []
        self.__unlink = os.unlink # See cleanup()
        self.tempcache = Tupu
        # Undocumented feature: ikiwa you assign {} to tempcache,
        # it ni used to cache files retrieved with
        # self.retrieve().  This ni sio enabled by default
        # since it does sio work kila changing documents (and I
        # haven't got the logic to check expiration headers
        # yet).
        self.ftpcache = ftpcache
        # Undocumented feature: you can use a different
        # ftp cache by assigning to the .ftpcache member;
        # kwenye case you want logically independent URL openers
        # XXX This ni sio threadsafe.  Bah.

    eleza __del__(self):
        self.close()

    eleza close(self):
        self.cleanup()

    eleza cleanup(self):
        # This code sometimes runs when the rest of this module
        # has already been deleted, so it can't use any globals
        # ama agiza anything.
        ikiwa self.__tempfiles:
            kila file kwenye self.__tempfiles:
                jaribu:
                    self.__unlink(file)
                tatizo OSError:
                    pita
            toa self.__tempfiles[:]
        ikiwa self.tempcache:
            self.tempcache.clear()

    eleza addheader(self, *args):
        """Add a header to be used by the HTTP interface only
        e.g. u.addheader('Accept', 'sound/basic')"""
        self.addheaders.append(args)

    # External interface
    eleza open(self, fullurl, data=Tupu):
        """Use URLopener().open(file) instead of open(file, 'r')."""
        fullurl = unwrap(_to_bytes(fullurl))
        fullurl = quote(fullurl, safe="%/:=&?~#+!$,;'@()*[]|")
        ikiwa self.tempcache na fullurl kwenye self.tempcache:
            filename, headers = self.tempcache[fullurl]
            fp = open(filename, 'rb')
            rudisha addinfourl(fp, headers, fullurl)
        urltype, url = _splittype(fullurl)
        ikiwa sio urltype:
            urltype = 'file'
        ikiwa urltype kwenye self.proxies:
            proxy = self.proxies[urltype]
            urltype, proxyhost = _splittype(proxy)
            host, selector = _splithost(proxyhost)
            url = (host, fullurl) # Signal special case to open_*()
        isipokua:
            proxy = Tupu
        name = 'open_' + urltype
        self.type = urltype
        name = name.replace('-', '_')
        ikiwa sio hasattr(self, name) ama name == 'open_local_file':
            ikiwa proxy:
                rudisha self.open_unknown_proxy(proxy, fullurl, data)
            isipokua:
                rudisha self.open_unknown(fullurl, data)
        jaribu:
            ikiwa data ni Tupu:
                rudisha getattr(self, name)(url)
            isipokua:
                rudisha getattr(self, name)(url, data)
        tatizo (HTTPError, URLError):
            raise
        tatizo OSError kama msg:
            ashiria OSError('socket error', msg).with_traceback(sys.exc_info()[2])

    eleza open_unknown(self, fullurl, data=Tupu):
        """Overridable interface to open unknown URL type."""
        type, url = _splittype(fullurl)
        ashiria OSError('url error', 'unknown url type', type)

    eleza open_unknown_proxy(self, proxy, fullurl, data=Tupu):
        """Overridable interface to open unknown URL type."""
        type, url = _splittype(fullurl)
        ashiria OSError('url error', 'invalid proxy kila %s' % type, proxy)

    # External interface
    eleza retrieve(self, url, filename=Tupu, reporthook=Tupu, data=Tupu):
        """retrieve(url) returns (filename, headers) kila a local object
        ama (tempfilename, headers) kila a remote object."""
        url = unwrap(_to_bytes(url))
        ikiwa self.tempcache na url kwenye self.tempcache:
            rudisha self.tempcache[url]
        type, url1 = _splittype(url)
        ikiwa filename ni Tupu na (sio type ama type == 'file'):
            jaribu:
                fp = self.open_local_file(url1)
                hdrs = fp.info()
                fp.close()
                rudisha url2pathname(_splithost(url1)[1]), hdrs
            tatizo OSError kama msg:
                pita
        fp = self.open(url, data)
        jaribu:
            headers = fp.info()
            ikiwa filename:
                tfp = open(filename, 'wb')
            isipokua:
                garbage, path = _splittype(url)
                garbage, path = _splithost(path ama "")
                path, garbage = _splitquery(path ama "")
                path, garbage = _splitattr(path ama "")
                suffix = os.path.splitext(path)[1]
                (fd, filename) = tempfile.mkstemp(suffix)
                self.__tempfiles.append(filename)
                tfp = os.fdopen(fd, 'wb')
            jaribu:
                result = filename, headers
                ikiwa self.tempcache ni sio Tupu:
                    self.tempcache[url] = result
                bs = 1024*8
                size = -1
                read = 0
                blocknum = 0
                ikiwa "content-length" kwenye headers:
                    size = int(headers["Content-Length"])
                ikiwa reporthook:
                    reporthook(blocknum, bs, size)
                wakati 1:
                    block = fp.read(bs)
                    ikiwa sio block:
                        koma
                    read += len(block)
                    tfp.write(block)
                    blocknum += 1
                    ikiwa reporthook:
                        reporthook(blocknum, bs, size)
            mwishowe:
                tfp.close()
        mwishowe:
            fp.close()

        # ashiria exception ikiwa actual size does sio match content-length header
        ikiwa size >= 0 na read < size:
            ashiria ContentTooShortError(
                "retrieval incomplete: got only %i out of %i bytes"
                % (read, size), result)

        rudisha result

    # Each method named open_<type> knows how to open that type of URL

    eleza _open_generic_http(self, connection_factory, url, data):
        """Make an HTTP connection using connection_class.

        This ni an internal method that should be called from
        open_http() ama open_https().

        Arguments:
        - connection_factory should take a host name na rudisha an
          HTTPConnection instance.
        - url ni the url to retrieval ama a host, relative-path pair.
        - data ni payload kila a POST request ama Tupu.
        """

        user_pitawd = Tupu
        proxy_pitawd= Tupu
        ikiwa isinstance(url, str):
            host, selector = _splithost(url)
            ikiwa host:
                user_pitawd, host = _splituser(host)
                host = unquote(host)
            realhost = host
        isipokua:
            host, selector = url
            # check whether the proxy contains authorization information
            proxy_pitawd, host = _splituser(host)
            # now we proceed ukijumuisha the url we want to obtain
            urltype, rest = _splittype(selector)
            url = rest
            user_pitawd = Tupu
            ikiwa urltype.lower() != 'http':
                realhost = Tupu
            isipokua:
                realhost, rest = _splithost(rest)
                ikiwa realhost:
                    user_pitawd, realhost = _splituser(realhost)
                ikiwa user_pitawd:
                    selector = "%s://%s%s" % (urltype, realhost, rest)
                ikiwa proxy_bypita(realhost):
                    host = realhost

        ikiwa sio host: ashiria OSError('http error', 'no host given')

        ikiwa proxy_pitawd:
            proxy_pitawd = unquote(proxy_pitawd)
            proxy_auth = base64.b64encode(proxy_pitawd.encode()).decode('ascii')
        isipokua:
            proxy_auth = Tupu

        ikiwa user_pitawd:
            user_pitawd = unquote(user_pitawd)
            auth = base64.b64encode(user_pitawd.encode()).decode('ascii')
        isipokua:
            auth = Tupu
        http_conn = connection_factory(host)
        headers = {}
        ikiwa proxy_auth:
            headers["Proxy-Authorization"] = "Basic %s" % proxy_auth
        ikiwa auth:
            headers["Authorization"] =  "Basic %s" % auth
        ikiwa realhost:
            headers["Host"] = realhost

        # Add Connection:close kama we don't support persistent connections yet.
        # This helps kwenye closing the socket na avoiding ResourceWarning

        headers["Connection"] = "close"

        kila header, value kwenye self.addheaders:
            headers[header] = value

        ikiwa data ni sio Tupu:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            http_conn.request("POST", selector, data, headers)
        isipokua:
            http_conn.request("GET", selector, headers=headers)

        jaribu:
            response = http_conn.getresponse()
        tatizo http.client.BadStatusLine:
            # something went wrong ukijumuisha the HTTP status line
            ashiria URLError("http protocol error: bad status line")

        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, na accepted.
        ikiwa 200 <= response.status < 300:
            rudisha addinfourl(response, response.msg, "http:" + url,
                              response.status)
        isipokua:
            rudisha self.http_error(
                url, response.fp,
                response.status, response.reason, response.msg, data)

    eleza open_http(self, url, data=Tupu):
        """Use HTTP protocol."""
        rudisha self._open_generic_http(http.client.HTTPConnection, url, data)

    eleza http_error(self, url, fp, errcode, errmsg, headers, data=Tupu):
        """Handle http errors.

        Derived kundi can override this, ama provide specific handlers
        named http_error_DDD where DDD ni the 3-digit error code."""
        # First check ikiwa there's a specific handler kila this error
        name = 'http_error_%d' % errcode
        ikiwa hasattr(self, name):
            method = getattr(self, name)
            ikiwa data ni Tupu:
                result = method(url, fp, errcode, errmsg, headers)
            isipokua:
                result = method(url, fp, errcode, errmsg, headers, data)
            ikiwa result: rudisha result
        rudisha self.http_error_default(url, fp, errcode, errmsg, headers)

    eleza http_error_default(self, url, fp, errcode, errmsg, headers):
        """Default error handler: close the connection na ashiria OSError."""
        fp.close()
        ashiria HTTPError(url, errcode, errmsg, headers, Tupu)

    ikiwa _have_ssl:
        eleza _https_connection(self, host):
            rudisha http.client.HTTPSConnection(host,
                                           key_file=self.key_file,
                                           cert_file=self.cert_file)

        eleza open_https(self, url, data=Tupu):
            """Use HTTPS protocol."""
            rudisha self._open_generic_http(self._https_connection, url, data)

    eleza open_file(self, url):
        """Use local file ama FTP depending on form of URL."""
        ikiwa sio isinstance(url, str):
            ashiria URLError('file error: proxy support kila file protocol currently sio implemented')
        ikiwa url[:2] == '//' na url[2:3] != '/' na url[2:12].lower() != 'localhost/':
            ashiria ValueError("file:// scheme ni supported only on localhost")
        isipokua:
            rudisha self.open_local_file(url)

    eleza open_local_file(self, url):
        """Use local file."""
        agiza email.utils
        agiza mimetypes
        host, file = _splithost(url)
        localname = url2pathname(file)
        jaribu:
            stats = os.stat(localname)
        tatizo OSError kama e:
            ashiria URLError(e.strerror, e.filename)
        size = stats.st_size
        modified = email.utils.formatdate(stats.st_mtime, usegmt=Kweli)
        mtype = mimetypes.guess_type(url)[0]
        headers = email.message_from_string(
            'Content-Type: %s\nContent-Length: %d\nLast-modified: %s\n' %
            (mtype ama 'text/plain', size, modified))
        ikiwa sio host:
            urlfile = file
            ikiwa file[:1] == '/':
                urlfile = 'file://' + file
            rudisha addinfourl(open(localname, 'rb'), headers, urlfile)
        host, port = _splitport(host)
        ikiwa (sio port
           na socket.gethostbyname(host) kwenye ((localhost(),) + thishost())):
            urlfile = file
            ikiwa file[:1] == '/':
                urlfile = 'file://' + file
            lasivyo file[:2] == './':
                ashiria ValueError("local file url may start ukijumuisha / ama file:. Unknown url of type: %s" % url)
            rudisha addinfourl(open(localname, 'rb'), headers, urlfile)
        ashiria URLError('local file error: sio on local host')

    eleza open_ftp(self, url):
        """Use FTP protocol."""
        ikiwa sio isinstance(url, str):
            ashiria URLError('ftp error: proxy support kila ftp protocol currently sio implemented')
        agiza mimetypes
        host, path = _splithost(url)
        ikiwa sio host: ashiria URLError('ftp error: no host given')
        host, port = _splitport(host)
        user, host = _splituser(host)
        ikiwa user: user, pitawd = _splitpitawd(user)
        isipokua: pitawd = Tupu
        host = unquote(host)
        user = unquote(user ama '')
        pitawd = unquote(pitawd ama '')
        host = socket.gethostbyname(host)
        ikiwa sio port:
            agiza ftplib
            port = ftplib.FTP_PORT
        isipokua:
            port = int(port)
        path, attrs = _splitattr(path)
        path = unquote(path)
        dirs = path.split('/')
        dirs, file = dirs[:-1], dirs[-1]
        ikiwa dirs na sio dirs[0]: dirs = dirs[1:]
        ikiwa dirs na sio dirs[0]: dirs[0] = '/'
        key = user, host, port, '/'.join(dirs)
        # XXX thread unsafe!
        ikiwa len(self.ftpcache) > MAXFTPCACHE:
            # Prune the cache, rather arbitrarily
            kila k kwenye list(self.ftpcache):
                ikiwa k != key:
                    v = self.ftpcache[k]
                    toa self.ftpcache[k]
                    v.close()
        jaribu:
            ikiwa key haiko kwenye self.ftpcache:
                self.ftpcache[key] = \
                    ftpwrapper(user, pitawd, host, port, dirs)
            ikiwa sio file: type = 'D'
            isipokua: type = 'I'
            kila attr kwenye attrs:
                attr, value = _splitvalue(attr)
                ikiwa attr.lower() == 'type' na \
                   value kwenye ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
            (fp, retrlen) = self.ftpcache[key].retrfile(file, type)
            mtype = mimetypes.guess_type("ftp:" + url)[0]
            headers = ""
            ikiwa mtype:
                headers += "Content-Type: %s\n" % mtype
            ikiwa retrlen ni sio Tupu na retrlen >= 0:
                headers += "Content-Length: %d\n" % retrlen
            headers = email.message_from_string(headers)
            rudisha addinfourl(fp, headers, "ftp:" + url)
        tatizo ftperrors() kama exp:
            ashiria URLError('ftp error %r' % exp).with_traceback(sys.exc_info()[2])

    eleza open_data(self, url, data=Tupu):
        """Use "data" URL."""
        ikiwa sio isinstance(url, str):
            ashiria URLError('data error: proxy support kila data protocol currently sio implemented')
        # ignore POSTed data
        #
        # syntax of data URLs:
        # dataurl   := "data:" [ mediatype ] [ ";base64" ] "," data
        # mediatype := [ type "/" subtype ] *( ";" parameter )
        # data      := *urlchar
        # parameter := attribute "=" value
        jaribu:
            [type, data] = url.split(',', 1)
        tatizo ValueError:
            ashiria OSError('data error', 'bad data URL')
        ikiwa sio type:
            type = 'text/plain;charset=US-ASCII'
        semi = type.rfind(';')
        ikiwa semi >= 0 na '=' haiko kwenye type[semi:]:
            encoding = type[semi+1:]
            type = type[:semi]
        isipokua:
            encoding = ''
        msg = []
        msg.append('Date: %s'%time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                                            time.gmtime(time.time())))
        msg.append('Content-type: %s' % type)
        ikiwa encoding == 'base64':
            # XXX ni this encoding/decoding ok?
            data = base64.decodebytes(data.encode('ascii')).decode('latin-1')
        isipokua:
            data = unquote(data)
        msg.append('Content-Length: %d' % len(data))
        msg.append('')
        msg.append(data)
        msg = '\n'.join(msg)
        headers = email.message_from_string(msg)
        f = io.StringIO(msg)
        #f.fileno = Tupu     # needed kila addinfourl
        rudisha addinfourl(f, headers, url)


kundi FancyURLopener(URLopener):
    """Derived kundi ukijumuisha handlers kila errors we can handle (perhaps)."""

    eleza __init__(self, *args, **kwargs):
        URLopener.__init__(self, *args, **kwargs)
        self.auth_cache = {}
        self.tries = 0
        self.maxtries = 10

    eleza http_error_default(self, url, fp, errcode, errmsg, headers):
        """Default error handling -- don't ashiria an exception."""
        rudisha addinfourl(fp, headers, "http:" + url, errcode)

    eleza http_error_302(self, url, fp, errcode, errmsg, headers, data=Tupu):
        """Error 302 -- relocated (temporarily)."""
        self.tries += 1
        jaribu:
            ikiwa self.maxtries na self.tries >= self.maxtries:
                ikiwa hasattr(self, "http_error_500"):
                    meth = self.http_error_500
                isipokua:
                    meth = self.http_error_default
                rudisha meth(url, fp, 500,
                            "Internal Server Error: Redirect Recursion",
                            headers)
            result = self.redirect_internal(url, fp, errcode, errmsg,
                                            headers, data)
            rudisha result
        mwishowe:
            self.tries = 0

    eleza redirect_internal(self, url, fp, errcode, errmsg, headers, data):
        ikiwa 'location' kwenye headers:
            newurl = headers['location']
        lasivyo 'uri' kwenye headers:
            newurl = headers['uri']
        isipokua:
            rudisha
        fp.close()

        # In case the server sent a relative URL, join ukijumuisha original:
        newurl = urljoin(self.type + ":" + url, newurl)

        urlparts = urlparse(newurl)

        # For security reasons, we don't allow redirection to anything other
        # than http, https na ftp.

        # We are using newer HTTPError ukijumuisha older redirect_internal method
        # This older method will get deprecated kwenye 3.3

        ikiwa urlparts.scheme haiko kwenye ('http', 'https', 'ftp', ''):
            ashiria HTTPError(newurl, errcode,
                            errmsg +
                            " Redirection to url '%s' ni sio allowed." % newurl,
                            headers, fp)

        rudisha self.open(newurl)

    eleza http_error_301(self, url, fp, errcode, errmsg, headers, data=Tupu):
        """Error 301 -- also relocated (permanently)."""
        rudisha self.http_error_302(url, fp, errcode, errmsg, headers, data)

    eleza http_error_303(self, url, fp, errcode, errmsg, headers, data=Tupu):
        """Error 303 -- also relocated (essentially identical to 302)."""
        rudisha self.http_error_302(url, fp, errcode, errmsg, headers, data)

    eleza http_error_307(self, url, fp, errcode, errmsg, headers, data=Tupu):
        """Error 307 -- relocated, but turn POST into error."""
        ikiwa data ni Tupu:
            rudisha self.http_error_302(url, fp, errcode, errmsg, headers, data)
        isipokua:
            rudisha self.http_error_default(url, fp, errcode, errmsg, headers)

    eleza http_error_401(self, url, fp, errcode, errmsg, headers, data=Tupu,
            retry=Uongo):
        """Error 401 -- authentication required.
        This function supports Basic authentication only."""
        ikiwa 'www-authenticate' haiko kwenye headers:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        stuff = headers['www-authenticate']
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        ikiwa sio match:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        scheme, realm = match.groups()
        ikiwa scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        ikiwa sio rejaribu:
            URLopener.http_error_default(self, url, fp, errcode, errmsg,
                    headers)
        name = 'retry_' + self.type + '_basic_auth'
        ikiwa data ni Tupu:
            rudisha getattr(self,name)(url, realm)
        isipokua:
            rudisha getattr(self,name)(url, realm, data)

    eleza http_error_407(self, url, fp, errcode, errmsg, headers, data=Tupu,
            retry=Uongo):
        """Error 407 -- proxy authentication required.
        This function supports Basic authentication only."""
        ikiwa 'proxy-authenticate' haiko kwenye headers:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        stuff = headers['proxy-authenticate']
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        ikiwa sio match:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        scheme, realm = match.groups()
        ikiwa scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        ikiwa sio rejaribu:
            URLopener.http_error_default(self, url, fp, errcode, errmsg,
                    headers)
        name = 'retry_proxy_' + self.type + '_basic_auth'
        ikiwa data ni Tupu:
            rudisha getattr(self,name)(url, realm)
        isipokua:
            rudisha getattr(self,name)(url, realm, data)

    eleza retry_proxy_http_basic_auth(self, url, realm, data=Tupu):
        host, selector = _splithost(url)
        newurl = 'http://' + host + selector
        proxy = self.proxies['http']
        urltype, proxyhost = _splittype(proxy)
        proxyhost, proxyselector = _splithost(proxyhost)
        i = proxyhost.find('@') + 1
        proxyhost = proxyhost[i:]
        user, pitawd = self.get_user_pitawd(proxyhost, realm, i)
        ikiwa sio (user ama pitawd): rudisha Tupu
        proxyhost = "%s:%s@%s" % (quote(user, safe=''),
                                  quote(pitawd, safe=''), proxyhost)
        self.proxies['http'] = 'http://' + proxyhost + proxyselector
        ikiwa data ni Tupu:
            rudisha self.open(newurl)
        isipokua:
            rudisha self.open(newurl, data)

    eleza retry_proxy_https_basic_auth(self, url, realm, data=Tupu):
        host, selector = _splithost(url)
        newurl = 'https://' + host + selector
        proxy = self.proxies['https']
        urltype, proxyhost = _splittype(proxy)
        proxyhost, proxyselector = _splithost(proxyhost)
        i = proxyhost.find('@') + 1
        proxyhost = proxyhost[i:]
        user, pitawd = self.get_user_pitawd(proxyhost, realm, i)
        ikiwa sio (user ama pitawd): rudisha Tupu
        proxyhost = "%s:%s@%s" % (quote(user, safe=''),
                                  quote(pitawd, safe=''), proxyhost)
        self.proxies['https'] = 'https://' + proxyhost + proxyselector
        ikiwa data ni Tupu:
            rudisha self.open(newurl)
        isipokua:
            rudisha self.open(newurl, data)

    eleza retry_http_basic_auth(self, url, realm, data=Tupu):
        host, selector = _splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, pitawd = self.get_user_pitawd(host, realm, i)
        ikiwa sio (user ama pitawd): rudisha Tupu
        host = "%s:%s@%s" % (quote(user, safe=''),
                             quote(pitawd, safe=''), host)
        newurl = 'http://' + host + selector
        ikiwa data ni Tupu:
            rudisha self.open(newurl)
        isipokua:
            rudisha self.open(newurl, data)

    eleza retry_https_basic_auth(self, url, realm, data=Tupu):
        host, selector = _splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, pitawd = self.get_user_pitawd(host, realm, i)
        ikiwa sio (user ama pitawd): rudisha Tupu
        host = "%s:%s@%s" % (quote(user, safe=''),
                             quote(pitawd, safe=''), host)
        newurl = 'https://' + host + selector
        ikiwa data ni Tupu:
            rudisha self.open(newurl)
        isipokua:
            rudisha self.open(newurl, data)

    eleza get_user_pitawd(self, host, realm, clear_cache=0):
        key = realm + '@' + host.lower()
        ikiwa key kwenye self.auth_cache:
            ikiwa clear_cache:
                toa self.auth_cache[key]
            isipokua:
                rudisha self.auth_cache[key]
        user, pitawd = self.prompt_user_pitawd(host, realm)
        ikiwa user ama pitawd: self.auth_cache[key] = (user, pitawd)
        rudisha user, pitawd

    eleza prompt_user_pitawd(self, host, realm):
        """Override this kwenye a GUI environment!"""
        agiza getpita
        jaribu:
            user = uliza("Enter username kila %s at %s: " % (realm, host))
            pitawd = getpita.getpita("Enter pitaword kila %s kwenye %s at %s: " %
                (user, realm, host))
            rudisha user, pitawd
        tatizo KeyboardInterrupt:
            andika()
            rudisha Tupu, Tupu


# Utility functions

_localhost = Tupu
eleza localhost():
    """Return the IP address of the magic hostname 'localhost'."""
    global _localhost
    ikiwa _localhost ni Tupu:
        _localhost = socket.gethostbyname('localhost')
    rudisha _localhost

_thishost = Tupu
eleza thishost():
    """Return the IP addresses of the current host."""
    global _thishost
    ikiwa _thishost ni Tupu:
        jaribu:
            _thishost = tuple(socket.gethostbyname_ex(socket.gethostname())[2])
        tatizo socket.gaierror:
            _thishost = tuple(socket.gethostbyname_ex('localhost')[2])
    rudisha _thishost

_ftperrors = Tupu
eleza ftperrors():
    """Return the set of errors raised by the FTP class."""
    global _ftperrors
    ikiwa _ftperrors ni Tupu:
        agiza ftplib
        _ftperrors = ftplib.all_errors
    rudisha _ftperrors

_noheaders = Tupu
eleza noheaders():
    """Return an empty email Message object."""
    global _noheaders
    ikiwa _noheaders ni Tupu:
        _noheaders = email.message_from_string("")
    rudisha _noheaders


# Utility classes

kundi ftpwrapper:
    """Class used by open_ftp() kila cache of open FTP connections."""

    eleza __init__(self, user, pitawd, host, port, dirs, timeout=Tupu,
                 persistent=Kweli):
        self.user = user
        self.pitawd = pitawd
        self.host = host
        self.port = port
        self.dirs = dirs
        self.timeout = timeout
        self.refcount = 0
        self.keepalive = persistent
        jaribu:
            self.init()
        tatizo:
            self.close()
            raise

    eleza init(self):
        agiza ftplib
        self.busy = 0
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port, self.timeout)
        self.ftp.login(self.user, self.pitawd)
        _target = '/'.join(self.dirs)
        self.ftp.cwd(_target)

    eleza retrfile(self, file, type):
        agiza ftplib
        self.endtransfer()
        ikiwa type kwenye ('d', 'D'): cmd = 'TYPE A'; isdir = 1
        isipokua: cmd = 'TYPE ' + type; isdir = 0
        jaribu:
            self.ftp.voidcmd(cmd)
        tatizo ftplib.all_errors:
            self.init()
            self.ftp.voidcmd(cmd)
        conn = Tupu
        ikiwa file na sio isdir:
            # Try to retrieve kama a file
            jaribu:
                cmd = 'RETR ' + file
                conn, retrlen = self.ftp.ntransfercmd(cmd)
            tatizo ftplib.error_perm kama reason:
                ikiwa str(reason)[:3] != '550':
                    ashiria URLError('ftp error: %r' % reason).with_traceback(
                        sys.exc_info()[2])
        ikiwa sio conn:
            # Set transfer mode to ASCII!
            self.ftp.voidcmd('TYPE A')
            # Try a directory listing. Verify that directory exists.
            ikiwa file:
                pwd = self.ftp.pwd()
                jaribu:
                    jaribu:
                        self.ftp.cwd(file)
                    tatizo ftplib.error_perm kama reason:
                        ashiria URLError('ftp error: %r' % reason) kutoka reason
                mwishowe:
                    self.ftp.cwd(pwd)
                cmd = 'LIST ' + file
            isipokua:
                cmd = 'LIST'
            conn, retrlen = self.ftp.ntransfercmd(cmd)
        self.busy = 1

        ftpobj = addclosehook(conn.makefile('rb'), self.file_close)
        self.refcount += 1
        conn.close()
        # Pass back both a suitably decorated object na a retrieval length
        rudisha (ftpobj, retrlen)

    eleza endtransfer(self):
        self.busy = 0

    eleza close(self):
        self.keepalive = Uongo
        ikiwa self.refcount <= 0:
            self.real_close()

    eleza file_close(self):
        self.endtransfer()
        self.refcount -= 1
        ikiwa self.refcount <= 0 na sio self.keepalive:
            self.real_close()

    eleza real_close(self):
        self.endtransfer()
        jaribu:
            self.ftp.close()
        tatizo ftperrors():
            pita

# Proxy handling
eleza getproxies_environment():
    """Return a dictionary of scheme -> proxy server URL mappings.

    Scan the environment kila variables named <scheme>_proxy;
    this seems to be the standard convention.  If you need a
    different way, you can pita a proxies dictionary to the
    [Fancy]URLopener constructor.

    """
    proxies = {}
    # kwenye order to prefer lowercase variables, process environment kwenye
    # two pitaes: first matches any, second pita matches lowercase only
    kila name, value kwenye os.environ.items():
        name = name.lower()
        ikiwa value na name[-6:] == '_proxy':
            proxies[name[:-6]] = value
    # CVE-2016-1000110 - If we are running kama CGI script, forget HTTP_PROXY
    # (non-all-lowercase) kama it may be set kutoka the web server by a "Proxy:"
    # header kutoka the client
    # If "proxy" ni lowercase, it will still be used thanks to the next block
    ikiwa 'REQUEST_METHOD' kwenye os.environ:
        proxies.pop('http', Tupu)
    kila name, value kwenye os.environ.items():
        ikiwa name[-6:] == '_proxy':
            name = name.lower()
            ikiwa value:
                proxies[name[:-6]] = value
            isipokua:
                proxies.pop(name[:-6], Tupu)
    rudisha proxies

eleza proxy_bypita_environment(host, proxies=Tupu):
    """Test ikiwa proxies should sio be used kila a particular host.

    Checks the proxy dict kila the value of no_proxy, which should
    be a list of comma separated DNS suffixes, ama '*' kila all hosts.

    """
    ikiwa proxies ni Tupu:
        proxies = getproxies_environment()
    # don't bypita, ikiwa no_proxy isn't specified
    jaribu:
        no_proxy = proxies['no']
    tatizo KeyError:
        rudisha 0
    # '*' ni special case kila always bypita
    ikiwa no_proxy == '*':
        rudisha 1
    # strip port off host
    hostonly, port = _splitport(host)
    # check ikiwa the host ends ukijumuisha any of the DNS suffixes
    no_proxy_list = [proxy.strip() kila proxy kwenye no_proxy.split(',')]
    kila name kwenye no_proxy_list:
        ikiwa name:
            name = name.lstrip('.')  # ignore leading dots
            name = re.escape(name)
            pattern = r'(.+\.)?%s$' % name
            ikiwa (re.match(pattern, hostonly, re.I)
                    ama re.match(pattern, host, re.I)):
                rudisha 1
    # otherwise, don't bypita
    rudisha 0


# This code tests an OSX specific data structure but ni testable on all
# platforms
eleza _proxy_bypita_macosx_sysconf(host, proxy_settings):
    """
    Return Kweli iff this host shouldn't be accessed using a proxy

    This function uses the MacOSX framework SystemConfiguration
    to fetch the proxy information.

    proxy_settings come kutoka _scproxy._get_proxy_settings ama get mocked ie:
    { 'exclude_simple': bool,
      'exceptions': ['foo.bar', '*.bar.com', '127.0.0.1', '10.1', '10.0/16']
    }
    """
    kutoka fnmatch agiza fnmatch

    hostonly, port = _splitport(host)

    eleza ip2num(ipAddr):
        parts = ipAddr.split('.')
        parts = list(map(int, parts))
        ikiwa len(parts) != 4:
            parts = (parts + [0, 0, 0, 0])[:4]
        rudisha (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

    # Check kila simple host names:
    ikiwa '.' haiko kwenye host:
        ikiwa proxy_settings['exclude_simple']:
            rudisha Kweli

    hostIP = Tupu

    kila value kwenye proxy_settings.get('exceptions', ()):
        # Items kwenye the list are strings like these: *.local, 169.254/16
        ikiwa sio value: endelea

        m = re.match(r"(\d+(?:\.\d+)*)(/\d+)?", value)
        ikiwa m ni sio Tupu:
            ikiwa hostIP ni Tupu:
                jaribu:
                    hostIP = socket.gethostbyname(hostonly)
                    hostIP = ip2num(hostIP)
                tatizo OSError:
                    endelea

            base = ip2num(m.group(1))
            mask = m.group(2)
            ikiwa mask ni Tupu:
                mask = 8 * (m.group(1).count('.') + 1)
            isipokua:
                mask = int(mask[1:])
            mask = 32 - mask

            ikiwa (hostIP >> mask) == (base >> mask):
                rudisha Kweli

        lasivyo fnmatch(host, value):
            rudisha Kweli

    rudisha Uongo


ikiwa sys.platform == 'darwin':
    kutoka _scproxy agiza _get_proxy_settings, _get_proxies

    eleza proxy_bypita_macosx_sysconf(host):
        proxy_settings = _get_proxy_settings()
        rudisha _proxy_bypita_macosx_sysconf(host, proxy_settings)

    eleza getproxies_macosx_sysconf():
        """Return a dictionary of scheme -> proxy server URL mappings.

        This function uses the MacOSX framework SystemConfiguration
        to fetch the proxy information.
        """
        rudisha _get_proxies()



    eleza proxy_bypita(host):
        """Return Kweli, ikiwa host should be bypitaed.

        Checks proxy settings gathered kutoka the environment, ikiwa specified,
        ama kutoka the MacOSX framework SystemConfiguration.

        """
        proxies = getproxies_environment()
        ikiwa proxies:
            rudisha proxy_bypita_environment(host, proxies)
        isipokua:
            rudisha proxy_bypita_macosx_sysconf(host)

    eleza getproxies():
        rudisha getproxies_environment() ama getproxies_macosx_sysconf()


lasivyo os.name == 'nt':
    eleza getproxies_registry():
        """Return a dictionary of scheme -> proxy server URL mappings.

        Win32 uses the registry to store proxies.

        """
        proxies = {}
        jaribu:
            agiza winreg
        tatizo ImportError:
            # Std module, so should be around - but you never know!
            rudisha proxies
        jaribu:
            internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
            proxyEnable = winreg.QueryValueEx(internetSettings,
                                               'ProxyEnable')[0]
            ikiwa proxyEnable:
                # Returned kama Unicode but problems ikiwa sio converted to ASCII
                proxyServer = str(winreg.QueryValueEx(internetSettings,
                                                       'ProxyServer')[0])
                ikiwa '=' kwenye proxyServer:
                    # Per-protocol settings
                    kila p kwenye proxyServer.split(';'):
                        protocol, address = p.split('=', 1)
                        # See ikiwa address has a type:// prefix
                        ikiwa sio re.match('^([^/:]+)://', address):
                            address = '%s://%s' % (protocol, address)
                        proxies[protocol] = address
                isipokua:
                    # Use one setting kila all protocols
                    ikiwa proxyServer[:5] == 'http:':
                        proxies['http'] = proxyServer
                    isipokua:
                        proxies['http'] = 'http://%s' % proxyServer
                        proxies['https'] = 'https://%s' % proxyServer
                        proxies['ftp'] = 'ftp://%s' % proxyServer
            internetSettings.Close()
        tatizo (OSError, ValueError, TypeError):
            # Either registry key sio found etc, ama the value kwenye an
            # unexpected format.
            # proxies already set up to be empty so nothing to do
            pita
        rudisha proxies

    eleza getproxies():
        """Return a dictionary of scheme -> proxy server URL mappings.

        Returns settings gathered kutoka the environment, ikiwa specified,
        ama the registry.

        """
        rudisha getproxies_environment() ama getproxies_registry()

    eleza proxy_bypita_registry(host):
        jaribu:
            agiza winreg
        tatizo ImportError:
            # Std modules, so should be around - but you never know!
            rudisha 0
        jaribu:
            internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
            proxyEnable = winreg.QueryValueEx(internetSettings,
                                               'ProxyEnable')[0]
            proxyOverride = str(winreg.QueryValueEx(internetSettings,
                                                     'ProxyOverride')[0])
            # ^^^^ Returned kama Unicode but problems ikiwa sio converted to ASCII
        tatizo OSError:
            rudisha 0
        ikiwa sio proxyEnable ama sio proxyOverride:
            rudisha 0
        # try to make a host list kutoka name na IP address.
        rawHost, port = _splitport(host)
        host = [rawHost]
        jaribu:
            addr = socket.gethostbyname(rawHost)
            ikiwa addr != rawHost:
                host.append(addr)
        tatizo OSError:
            pita
        jaribu:
            fqdn = socket.getfqdn(rawHost)
            ikiwa fqdn != rawHost:
                host.append(fqdn)
        tatizo OSError:
            pita
        # make a check value list kutoka the registry enjaribu: replace the
        # '<local>' string by the localhost entry na the corresponding
        # canonical entry.
        proxyOverride = proxyOverride.split(';')
        # now check ikiwa we match one of the registry values.
        kila test kwenye proxyOverride:
            ikiwa test == '<local>':
                ikiwa '.' haiko kwenye rawHost:
                    rudisha 1
            test = test.replace(".", r"\.")     # mask dots
            test = test.replace("*", r".*")     # change glob sequence
            test = test.replace("?", r".")      # change glob char
            kila val kwenye host:
                ikiwa re.match(test, val, re.I):
                    rudisha 1
        rudisha 0

    eleza proxy_bypita(host):
        """Return Kweli, ikiwa host should be bypitaed.

        Checks proxy settings gathered kutoka the environment, ikiwa specified,
        ama the registry.

        """
        proxies = getproxies_environment()
        ikiwa proxies:
            rudisha proxy_bypita_environment(host, proxies)
        isipokua:
            rudisha proxy_bypita_registry(host)

isipokua:
    # By default use environment variables
    getproxies = getproxies_environment
    proxy_bypita = proxy_bypita_environment
