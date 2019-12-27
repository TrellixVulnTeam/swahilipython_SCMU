"""An extensible library for opening URLs using a variety of protocols

The simplest way to use this module is to call the urlopen function,
which accepts a string containing a URL or a Request object (described
below).  It opens the URL and returns the results as file-like
object; the returned object has some extra methods described below.

The OpenerDirector manages a collection of Handler objects that do
all the actual work.  Each Handler implements a particular protocol or
option.  The OpenerDirector is a composite object that invokes the
Handlers needed to open the requested URL.  For example, the
HTTPHandler performs HTTP GET and POST requests and deals with
non-error returns.  The HTTPRedirectHandler automatically deals with
HTTP 301, 302, 303 and 307 redirect errors, and the HTTPDigestAuthHandler
deals with digest authentication.

urlopen(url, data=None) -- Basic usage is the same as original
urllib.  pass the url and optionally data to post to an HTTP URL, and
get a file-like object back.  One difference is that you can also pass
a Request instance instead of URL.  Raises a URLError (subkundi of
OSError); for HTTP errors, raises an HTTPError, which can also be
treated as a valid response.

build_opener -- Function that creates a new OpenerDirector instance.
Will install the default handlers.  Accepts one or more Handlers as
arguments, either instances or Handler classes that it will
instantiate.  If one of the argument is a subkundi of the default
handler, the argument will be installed instead of the default.

install_opener -- Installs a new opener as the default opener.

objects of interest:

OpenerDirector -- Sets up the User Agent as the Python-urllib client and manages
the Handler classes, while dealing with requests and responses.

Request -- An object that encapsulates the state of a request.  The
state can be as simple as the URL.  It can also include extra HTTP
headers, e.g. a User-Agent.

BaseHandler --

internals:
BaseHandler and parent
_call_chain conventions

Example usage:

agiza urllib.request

# set up authentication info
authinfo = urllib.request.HTTPBasicAuthHandler()
authinfo.add_password(realm='PDQ Application',
                      uri='https://mahler:8092/site-updates.py',
                      user='klem',
                      passwd='geheim$parole')

proxy_support = urllib.request.ProxyHandler({"http" : "http://ahad-haam:3128"})

# build a new opener that adds authentication and caching FTP handlers
opener = urllib.request.build_opener(proxy_support, authinfo,
                                     urllib.request.CacheFTPHandler)

# install it
urllib.request.install_opener(opener)

f = urllib.request.urlopen('http://www.python.org/')
"""

# XXX issues:
# If an authentication error handler that tries to perform
# authentication for some reason but fails, how should the error be
# signalled?  The client needs to know the HTTP error code.  But if
# the handler knows that the problem was, e.g., that it didn't know
# that hash algo that requested in the challenge, it would be good to
# pass that information along to the client, too.
# ftp errors aren't handled cleanly
# check digest against correct (i.e. non-apache) implementation

# Possible extensions:
# complex proxies  XXX not sure what exactly was meant by this
# abstract factory for opener

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
    _splittype, _splithost, _splitport, _splituser, _splitpasswd,
    _splitattr, _splitquery, _splitvalue, _splittag, _to_bytes,
    unquote_to_bytes, urlunparse)
kutoka urllib.response agiza addinfourl, addclosehook

# check for SSL
try:
    agiza ssl
except ImportError:
    _have_ssl = False
else:
    _have_ssl = True

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

# used in User-Agent header sent
__version__ = '%d.%d' % sys.version_info[:2]

_opener = None
eleza urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
            *, cafile=None, capath=None, cadefault=False, context=None):
    '''Open the URL url, which can be either a string or a Request object.

    *data* must be an object specifying additional data to be sent to
    the server, or None ikiwa no such data is needed.  See Request for
    details.

    urllib.request module uses HTTP/1.1 and includes a "Connection:close"
    header in its HTTP requests.

    The optional *timeout* parameter specifies a timeout in seconds for
    blocking operations like the connection attempt (ikiwa not specified, the
    global default timeout setting will be used). This only works for HTTP,
    HTTPS and FTP connections.

    If *context* is specified, it must be a ssl.SSLContext instance describing
    the various SSL options. See HTTPSConnection for more details.

    The optional *cafile* and *capath* parameters specify a set of trusted CA
    certificates for HTTPS requests. cafile should point to a single file
    containing a bundle of CA certificates, whereas capath should point to a
    directory of hashed certificate files. More information can be found in
    ssl.SSLContext.load_verify_locations().

    The *cadefault* parameter is ignored.

    This function always returns an object which can work as a context
    manager and has methods such as

    * geturl() - rudisha the URL of the resource retrieved, commonly used to
      determine ikiwa a redirect was followed

    * info() - rudisha the meta-information of the page, such as headers, in the
      form of an email.message_kutoka_string() instance (see Quick Reference to
      HTTP Headers)

    * getcode() - rudisha the HTTP status code of the response.  Raises URLError
      on errors.

    For HTTP and HTTPS URLs, this function returns a http.client.HTTPResponse
    object slightly modified. In addition to the three new methods above, the
    msg attribute contains the same information as the reason attribute ---
    the reason phrase returned by the server --- instead of the response
    headers as it is specified in the documentation for HTTPResponse.

    For FTP, file, and data URLs and requests explicitly handled by legacy
    URLopener and FancyURLopener classes, this function returns a
    urllib.response.addinfourl object.

    Note that None may be returned ikiwa no handler handles the request (though
    the default installed global OpenerDirector uses UnknownHandler to ensure
    this never happens).

    In addition, ikiwa proxy settings are detected (for example, when a *_proxy
    environment variable like http_proxy is set), ProxyHandler is default
    installed and makes sure the requests are handled through the proxy.

    '''
    global _opener
    ikiwa cafile or capath or cadefault:
        agiza warnings
        warnings.warn("cafile, capath and cadefault are deprecated, use a "
                      "custom context instead.", DeprecationWarning, 2)
        ikiwa context is not None:
            raise ValueError(
                "You can't pass both context and any of cafile, capath, and "
                "cadefault"
            )
        ikiwa not _have_ssl:
            raise ValueError('SSL support not available')
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                             cafile=cafile,
                                             capath=capath)
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    elikiwa context:
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    elikiwa _opener is None:
        _opener = opener = build_opener()
    else:
        opener = _opener
    rudisha opener.open(url, data, timeout)

eleza install_opener(opener):
    global _opener
    _opener = opener

_url_tempfiles = []
eleza urlretrieve(url, filename=None, reporthook=None, data=None):
    """
    Retrieve a URL into a temporary location on disk.

    Requires a URL argument. If a filename is passed, it is used as
    the temporary file location. The reporthook argument should be
    a callable that accepts a block number, a read size, and the
    total file size of the URL target. The data argument should be
    valid URL encoded data.

    If a filename is passed and the URL points to a local resource,
    the result is a copy kutoka local file to new file.

    Returns a tuple containing the path to the newly created
    data file as well as the resulting HTTPMessage object.
    """
    url_type, path = _splittype(url)

    with contextlib.closing(urlopen(url, data)) as fp:
        headers = fp.info()

        # Just rudisha the local path and the "headers" for file://
        # URLs. No sense in performing a copy unless requested.
        ikiwa url_type == "file" and not filename:
            rudisha os.path.normpath(path), headers

        # Handle temporary file setup.
        ikiwa filename:
            tfp = open(filename, 'wb')
        else:
            tfp = tempfile.NamedTemporaryFile(delete=False)
            filename = tfp.name
            _url_tempfiles.append(filename)

        with tfp:
            result = filename, headers
            bs = 1024*8
            size = -1
            read = 0
            blocknum = 0
            ikiwa "content-length" in headers:
                size = int(headers["Content-Length"])

            ikiwa reporthook:
                reporthook(blocknum, bs, size)

            while True:
                block = fp.read(bs)
                ikiwa not block:
                    break
                read += len(block)
                tfp.write(block)
                blocknum += 1
                ikiwa reporthook:
                    reporthook(blocknum, bs, size)

    ikiwa size >= 0 and read < size:
        raise ContentTooShortError(
            "retrieval incomplete: got only %i out of %i bytes"
            % (read, size), result)

    rudisha result

eleza urlcleanup():
    """Clean up temporary files kutoka urlretrieve calls."""
    for temp_file in _url_tempfiles:
        try:
            os.unlink(temp_file)
        except OSError:
            pass

    del _url_tempfiles[:]
    global _opener
    ikiwa _opener:
        _opener = None

# copied kutoka cookielib.py
_cut_port_re = re.compile(r":\d+$", re.ASCII)
eleza request_host(request):
    """Return request-host, as defined by RFC 2965.

    Variation kutoka RFC: returned value is lowercased, for convenient
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

    eleza __init__(self, url, data=None, headers={},
                 origin_req_host=None, unverifiable=False,
                 method=None):
        self.full_url = url
        self.headers = {}
        self.unredirected_hdrs = {}
        self._data = None
        self.data = data
        self._tunnel_host = None
        for key, value in headers.items():
            self.add_header(key, value)
        ikiwa origin_req_host is None:
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
        self._full_url = None
        self.fragment = None
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
            # (cause it's most probably calculated for previous value)
            ikiwa self.has_header("Content-length"):
                self.remove_header("Content-length")

    @data.deleter
    eleza data(self):
        self.data = None

    eleza _parse(self):
        self.type, rest = _splittype(self._full_url)
        ikiwa self.type is None:
            raise ValueError("unknown url type: %r" % self.full_url)
        self.host, self.selector = _splithost(rest)
        ikiwa self.host:
            self.host = unquote(self.host)

    eleza get_method(self):
        """Return a string indicating the HTTP request method."""
        default_method = "POST" ikiwa self.data is not None else "GET"
        rudisha getattr(self, 'method', default_method)

    eleza get_full_url(self):
        rudisha self.full_url

    eleza set_proxy(self, host, type):
        ikiwa self.type == 'https' and not self._tunnel_host:
            self._tunnel_host = self.host
        else:
            self.type= type
            self.selector = self.full_url
        self.host = host

    eleza has_proxy(self):
        rudisha self.selector == self.full_url

    eleza add_header(self, key, val):
        # useful for something like authentication
        self.headers[key.capitalize()] = val

    eleza add_unredirected_header(self, key, val):
        # will not be added to a redirected request
        self.unredirected_hdrs[key.capitalize()] = val

    eleza has_header(self, header_name):
        rudisha (header_name in self.headers or
                header_name in self.unredirected_hdrs)

    eleza get_header(self, header_name, default=None):
        rudisha self.headers.get(
            header_name,
            self.unredirected_hdrs.get(header_name, default))

    eleza remove_header(self, header_name):
        self.headers.pop(header_name, None)
        self.unredirected_hdrs.pop(header_name, None)

    eleza header_items(self):
        hdrs = {**self.unredirected_hdrs, **self.headers}
        rudisha list(hdrs.items())

kundi OpenerDirector:
    eleza __init__(self):
        client_version = "Python-urllib/%s" % __version__
        self.addheaders = [('User-agent', client_version)]
        # self.handlers is retained only for backward compatibility
        self.handlers = []
        # manage the individual handlers
        self.handle_open = {}
        self.handle_error = {}
        self.process_response = {}
        self.process_request = {}

    eleza add_handler(self, handler):
        ikiwa not hasattr(handler, "add_parent"):
            raise TypeError("expected BaseHandler instance, got %r" %
                            type(handler))

        added = False
        for meth in dir(handler):
            ikiwa meth in ["redirect_request", "do_open", "proxy_open"]:
                # oops, coincidental match
                continue

            i = meth.find("_")
            protocol = meth[:i]
            condition = meth[i+1:]

            ikiwa condition.startswith("error"):
                j = condition.find("_") + i + 1
                kind = meth[j+1:]
                try:
                    kind = int(kind)
                except ValueError:
                    pass
                lookup = self.handle_error.get(protocol, {})
                self.handle_error[protocol] = lookup
            elikiwa condition == "open":
                kind = protocol
                lookup = self.handle_open
            elikiwa condition == "response":
                kind = protocol
                lookup = self.process_response
            elikiwa condition == "request":
                kind = protocol
                lookup = self.process_request
            else:
                continue

            handlers = lookup.setdefault(kind, [])
            ikiwa handlers:
                bisect.insort(handlers, handler)
            else:
                handlers.append(handler)
            added = True

        ikiwa added:
            bisect.insort(self.handlers, handler)
            handler.add_parent(self)

    eleza close(self):
        # Only exists for backwards compatibility.
        pass

    eleza _call_chain(self, chain, kind, meth_name, *args):
        # Handlers raise an exception ikiwa no one else should try to handle
        # the request, or rudisha None ikiwa they can't but another handler
        # could.  Otherwise, they rudisha the response.
        handlers = chain.get(kind, ())
        for handler in handlers:
            func = getattr(handler, meth_name)
            result = func(*args)
            ikiwa result is not None:
                rudisha result

    eleza open(self, fullurl, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        # accept a URL or a Request object
        ikiwa isinstance(fullurl, str):
            req = Request(fullurl, data)
        else:
            req = fullurl
            ikiwa data is not None:
                req.data = data

        req.timeout = timeout
        protocol = req.type

        # pre-process request
        meth_name = protocol+"_request"
        for processor in self.process_request.get(protocol, []):
            meth = getattr(processor, meth_name)
            req = meth(req)

        sys.audit('urllib.Request', req.full_url, req.data, req.headers, req.get_method())
        response = self._open(req, data)

        # post-process response
        meth_name = protocol+"_response"
        for processor in self.process_response.get(protocol, []):
            meth = getattr(processor, meth_name)
            response = meth(req, response)

        rudisha response

    eleza _open(self, req, data=None):
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
        ikiwa proto in ('http', 'https'):
            # XXX http[s] protocols are special-cased
            dict = self.handle_error['http'] # https is not different than http
            proto = args[2]  # YUCK!
            meth_name = 'http_error_%s' % proto
            http_err = 1
            orig_args = args
        else:
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
# sense to skip a superkundi in favor of a subkundi and when it might
# make sense to include both

eleza build_opener(*handlers):
    """Create an opener object kutoka a list of handlers.

    The opener will use several default handlers, including support
    for HTTP, FTP and when applicable HTTPS.

    If any of the handlers passed as arguments are subclasses of the
    default handlers, the default handlers will not be used.
    """
    opener = OpenerDirector()
    default_classes = [ProxyHandler, UnknownHandler, HTTPHandler,
                       HTTPDefaultErrorHandler, HTTPRedirectHandler,
                       FTPHandler, FileHandler, HTTPErrorProcessor,
                       DataHandler]
    ikiwa hasattr(http.client, "HTTPSConnection"):
        default_classes.append(HTTPSHandler)
    skip = set()
    for klass in default_classes:
        for check in handlers:
            ikiwa isinstance(check, type):
                ikiwa issubclass(check, klass):
                    skip.add(klass)
            elikiwa isinstance(check, klass):
                skip.add(klass)
    for klass in skip:
        default_classes.remove(klass)

    for klass in default_classes:
        opener.add_handler(klass())

    for h in handlers:
        ikiwa isinstance(h, type):
            h = h()
        opener.add_handler(h)
    rudisha opener

kundi BaseHandler:
    handler_order = 500

    eleza add_parent(self, parent):
        self.parent = parent

    eleza close(self):
        # Only exists for backwards compatibility
        pass

    eleza __lt__(self, other):
        ikiwa not hasattr(other, "handler_order"):
            # Try to preserve the old behavior of having custom classes
            # inserted after default ones (works only for custom user
            # classes which are not aware of handler_order).
            rudisha True
        rudisha self.handler_order < other.handler_order


kundi HTTPErrorProcessor(BaseHandler):
    """Process HTTP error responses."""
    handler_order = 1000  # after all other processing

    eleza http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, and accepted.
        ikiwa not (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)

        rudisha response

    https_response = http_response

kundi HTTPDefaultErrorHandler(BaseHandler):
    eleza http_error_default(self, req, fp, code, msg, hdrs):
        raise HTTPError(req.full_url, code, msg, hdrs, fp)

kundi HTTPRedirectHandler(BaseHandler):
    # maximum number of redirections to any single URL
    # this is needed because of the state that cookies introduce
    max_repeats = 4
    # maximum total number of redirections (regardless of URL) before
    # assuming we're in a loop
    max_redirections = 10

    eleza redirect_request(self, req, fp, code, msg, headers, newurl):
        """Return a Request or None in response to a redirect.

        This is called by the http_error_30x methods when a
        redirection response is received.  If a redirection should
        take place, rudisha a new Request to allow http_error_30x to
        perform the redirect.  Otherwise, raise HTTPError ikiwa no-one
        else should try to handle this url.  Return None ikiwa you can't
        but another Handler might.
        """
        m = req.get_method()
        ikiwa (not (code in (301, 302, 303, 307) and m in ("GET", "HEAD")
            or code in (301, 302, 303) and m == "POST")):
            raise HTTPError(req.full_url, code, msg, headers, fp)

        # Strictly (according to RFC 2616), 301 or 302 in response to
        # a POST MUST NOT cause a redirection without confirmation
        # kutoka the user (of urllib.request, in this case).  In practice,
        # essentially all clients do redirect in this case, so we do
        # the same.

        # Be conciliant with URIs containing a space.  This is mainly
        # redundant with the more complete encoding done in http_error_302(),
        # but it is kept for compatibility with other callers.
        newurl = newurl.replace(' ', '%20')

        CONTENT_HEADERS = ("content-length", "content-type")
        newheaders = {k: v for k, v in req.headers.items()
                      ikiwa k.lower() not in CONTENT_HEADERS}
        rudisha Request(newurl,
                       headers=newheaders,
                       origin_req_host=req.origin_req_host,
                       unverifiable=True)

    # Implementation note: To avoid the server sending us into an
    # infinite loop, the request object needs to track what URLs we
    # have already seen.  Do this by adding a handler-specific
    # attribute to the Request object.
    eleza http_error_302(self, req, fp, code, msg, headers):
        # Some servers (incorrectly) rudisha multiple Location headers
        # (so probably same goes for URI).  Use first header.
        ikiwa "location" in headers:
            newurl = headers["location"]
        elikiwa "uri" in headers:
            newurl = headers["uri"]
        else:
            return

        # fix a possible malformed URL
        urlparts = urlparse(newurl)

        # For security reasons we don't allow redirection to anything other
        # than http, https or ftp.

        ikiwa urlparts.scheme not in ('http', 'https', 'ftp', ''):
            raise HTTPError(
                newurl, code,
                "%s - Redirection to url '%s' is not allowed" % (msg, newurl),
                headers, fp)

        ikiwa not urlparts.path and urlparts.netloc:
            urlparts = list(urlparts)
            urlparts[2] = "/"
        newurl = urlunparse(urlparts)

        # http.client.parse_headers() decodes as ISO-8859-1.  Recover the
        # original bytes and percent-encode non-ASCII bytes, and any special
        # characters such as the space.
        newurl = quote(
            newurl, encoding="iso-8859-1", safe=string.punctuation)
        newurl = urljoin(req.full_url, newurl)

        # XXX Probably want to forget about the state of the current
        # request, although that might interact poorly with other
        # handlers that also use handler-specific request attributes
        new = self.redirect_request(req, fp, code, msg, headers, newurl)
        ikiwa new is None:
            return

        # loop detection
        # .redirect_dict has a key url ikiwa url was previously visited.
        ikiwa hasattr(req, 'redirect_dict'):
            visited = new.redirect_dict = req.redirect_dict
            ikiwa (visited.get(newurl, 0) >= self.max_repeats or
                len(visited) >= self.max_redirections):
                raise HTTPError(req.full_url, code,
                                self.inf_msg + msg, headers, fp)
        else:
            visited = new.redirect_dict = req.redirect_dict = {}
        visited[newurl] = visited.get(newurl, 0) + 1

        # Don't close the fp until we are sure that we won't use it
        # with HTTPError.
        fp.read()
        fp.close()

        rudisha self.parent.open(new, timeout=req.timeout)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

    inf_msg = "The HTTP server returned a redirect error that would " \
              "lead to an infinite loop.\n" \
              "The last 30x error message was:\n"


eleza _parse_proxy(proxy):
    """Return (scheme, user, password, host/port) given a URL or an authority.

    If a URL is supplied, it must have an authority (host:port) component.
    According to RFC 3986, having an authority component means the URL must
    have two slashes after the scheme.
    """
    scheme, r_scheme = _splittype(proxy)
    ikiwa not r_scheme.startswith("/"):
        # authority
        scheme = None
        authority = proxy
    else:
        # URL
        ikiwa not r_scheme.startswith("//"):
            raise ValueError("proxy URL with no authority: %r" % proxy)
        # We have an authority, so for RFC 3986-compliant URLs (by ss 3.
        # and 3.3.), path is empty or starts with '/'
        end = r_scheme.find("/", 2)
        ikiwa end == -1:
            end = None
        authority = r_scheme[2:end]
    userinfo, hostport = _splituser(authority)
    ikiwa userinfo is not None:
        user, password = _splitpasswd(userinfo)
    else:
        user = password = None
    rudisha scheme, user, password, hostport

kundi ProxyHandler(BaseHandler):
    # Proxies must be in front
    handler_order = 100

    eleza __init__(self, proxies=None):
        ikiwa proxies is None:
            proxies = getproxies()
        assert hasattr(proxies, 'keys'), "proxies must be a mapping"
        self.proxies = proxies
        for type, url in proxies.items():
            type = type.lower()
            setattr(self, '%s_open' % type,
                    lambda r, proxy=url, type=type, meth=self.proxy_open:
                        meth(r, proxy, type))

    eleza proxy_open(self, req, proxy, type):
        orig_type = req.type
        proxy_type, user, password, hostport = _parse_proxy(proxy)
        ikiwa proxy_type is None:
            proxy_type = orig_type

        ikiwa req.host and proxy_bypass(req.host):
            rudisha None

        ikiwa user and password:
            user_pass = '%s:%s' % (unquote(user),
                                   unquote(password))
            creds = base64.b64encode(user_pass.encode()).decode("ascii")
            req.add_header('Proxy-authorization', 'Basic ' + creds)
        hostport = unquote(hostport)
        req.set_proxy(hostport, proxy_type)
        ikiwa orig_type == proxy_type or orig_type == 'https':
            # let other handlers take care of it
            rudisha None
        else:
            # need to start over, because the other handlers don't
            # grok the proxy's URL type
            # e.g. ikiwa we have a constructor arg proxies like so:
            # {'http': 'ftp://proxy.example.com'}, we may end up turning
            # a request for http://acme.example.com/a into one for
            # ftp://proxy.example.com/a
            rudisha self.parent.open(req, timeout=req.timeout)

kundi HTTPPasswordMgr:

    eleza __init__(self):
        self.passwd = {}

    eleza add_password(self, realm, uri, user, passwd):
        # uri could be a single URI or a sequence
        ikiwa isinstance(uri, str):
            uri = [uri]
        ikiwa realm not in self.passwd:
            self.passwd[realm] = {}
        for default_port in True, False:
            reduced_uri = tuple(
                self.reduce_uri(u, default_port) for u in uri)
            self.passwd[realm][reduced_uri] = (user, passwd)

    eleza find_user_password(self, realm, authuri):
        domains = self.passwd.get(realm, {})
        for default_port in True, False:
            reduced_authuri = self.reduce_uri(authuri, default_port)
            for uris, authinfo in domains.items():
                for uri in uris:
                    ikiwa self.is_suburi(uri, reduced_authuri):
                        rudisha authinfo
        rudisha None, None

    eleza reduce_uri(self, uri, default_port=True):
        """Accept authority or URI and extract only the authority and path."""
        # note HTTP URLs do not have a userinfo component
        parts = urlsplit(uri)
        ikiwa parts[1]:
            # URI
            scheme = parts[0]
            authority = parts[1]
            path = parts[2] or '/'
        else:
            # host or host:port
            scheme = None
            authority = uri
            path = '/'
        host, port = _splitport(authority)
        ikiwa default_port and port is None and scheme is not None:
            dport = {"http": 80,
                     "https": 443,
                     }.get(scheme)
            ikiwa dport is not None:
                authority = "%s:%d" % (host, dport)
        rudisha authority, path

    eleza is_suburi(self, base, test):
        """Check ikiwa test is below base in a URI tree

        Both args must be URIs in reduced form.
        """
        ikiwa base == test:
            rudisha True
        ikiwa base[0] != test[0]:
            rudisha False
        common = posixpath.commonprefix((base[1], test[1]))
        ikiwa len(common) == len(base[1]):
            rudisha True
        rudisha False


kundi HTTPPasswordMgrWithDefaultRealm(HTTPPasswordMgr):

    eleza find_user_password(self, realm, authuri):
        user, password = HTTPPasswordMgr.find_user_password(self, realm,
                                                            authuri)
        ikiwa user is not None:
            rudisha user, password
        rudisha HTTPPasswordMgr.find_user_password(self, None, authuri)


kundi HTTPPasswordMgrWithPriorAuth(HTTPPasswordMgrWithDefaultRealm):

    eleza __init__(self, *args, **kwargs):
        self.authenticated = {}
        super().__init__(*args, **kwargs)

    eleza add_password(self, realm, uri, user, passwd, is_authenticated=False):
        self.update_authenticated(uri, is_authenticated)
        # Add a default for prior auth requests
        ikiwa realm is not None:
            super().add_password(None, uri, user, passwd)
        super().add_password(realm, uri, user, passwd)

    eleza update_authenticated(self, uri, is_authenticated=False):
        # uri could be a single URI or a sequence
        ikiwa isinstance(uri, str):
            uri = [uri]

        for default_port in True, False:
            for u in uri:
                reduced_uri = self.reduce_uri(u, default_port)
                self.authenticated[reduced_uri] = is_authenticated

    eleza is_authenticated(self, authuri):
        for default_port in True, False:
            reduced_authuri = self.reduce_uri(authuri, default_port)
            for uri in self.authenticated:
                ikiwa self.is_suburi(uri, reduced_authuri):
                    rudisha self.authenticated[uri]


kundi AbstractBasicAuthHandler:

    # XXX this allows for multiple auth-schemes, but will stupidly pick
    # the last one with a realm specified.

    # allow for double- and single-quoted realm values
    # (single quotes are a violation of the RFC, but appear in the wild)
    rx = re.compile('(?:.*,)*[ \t]*([^ \t]+)[ \t]+'
                    'realm=(["\']?)([^"\']*)\\2', re.I)

    # XXX could pre-emptively send auth info already accepted (RFC 2617,
    # end of section 2, and section 1.2 immediately after "credentials"
    # production).

    eleza __init__(self, password_mgr=None):
        ikiwa password_mgr is None:
            password_mgr = HTTPPasswordMgr()
        self.passwd = password_mgr
        self.add_password = self.passwd.add_password

    eleza http_error_auth_reqed(self, authreq, host, req, headers):
        # host may be an authority (without userinfo) or a URL with an
        # authority
        # XXX could be multiple headers
        authreq = headers.get(authreq, None)

        ikiwa authreq:
            scheme = authreq.split()[0]
            ikiwa scheme.lower() != 'basic':
                raise ValueError("AbstractBasicAuthHandler does not"
                                 " support the following scheme: '%s'" %
                                 scheme)
            else:
                mo = AbstractBasicAuthHandler.rx.search(authreq)
                ikiwa mo:
                    scheme, quote, realm = mo.groups()
                    ikiwa quote not in ['"',"'"]:
                        warnings.warn("Basic Auth Realm was unquoted",
                                      UserWarning, 2)
                    ikiwa scheme.lower() == 'basic':
                        rudisha self.retry_http_basic_auth(host, req, realm)

    eleza retry_http_basic_auth(self, host, req, realm):
        user, pw = self.passwd.find_user_password(realm, host)
        ikiwa pw is not None:
            raw = "%s:%s" % (user, pw)
            auth = "Basic " + base64.b64encode(raw.encode()).decode("ascii")
            ikiwa req.get_header(self.auth_header, None) == auth:
                rudisha None
            req.add_unredirected_header(self.auth_header, auth)
            rudisha self.parent.open(req, timeout=req.timeout)
        else:
            rudisha None

    eleza http_request(self, req):
        ikiwa (not hasattr(self.passwd, 'is_authenticated') or
           not self.passwd.is_authenticated(req.full_url)):
            rudisha req

        ikiwa not req.has_header('Authorization'):
            user, passwd = self.passwd.find_user_password(None, req.full_url)
            credentials = '{0}:{1}'.format(user, passwd).encode()
            auth_str = base64.standard_b64encode(credentials).decode()
            req.add_unredirected_header('Authorization',
                                        'Basic {}'.format(auth_str.strip()))
        rudisha req

    eleza http_response(self, req, response):
        ikiwa hasattr(self.passwd, 'is_authenticated'):
            ikiwa 200 <= response.code < 300:
                self.passwd.update_authenticated(req.full_url, True)
            else:
                self.passwd.update_authenticated(req.full_url, False)
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
        # http_error_auth_reqed requires that there is no userinfo component in
        # authority.  Assume there isn't one, since urllib.request does not (and
        # should not, RFC 3986 s. 3.2.1) support requests for URLs containing
        # userinfo.
        authority = req.host
        response = self.http_error_auth_reqed('proxy-authenticate',
                                          authority, req, headers)
        rudisha response


# Return n random bytes.
_randombytes = os.urandom


kundi AbstractDigestAuthHandler:
    # Digest authentication is specified in RFC 2617.

    # XXX The client does not inspect the Authentication-Info header
    # in a successful response.

    # XXX It should be possible to test this implementation against
    # a mock server that just generates a static set of challenges.

    # XXX qop="auth-int" supports is shaky

    eleza __init__(self, passwd=None):
        ikiwa passwd is None:
            passwd = HTTPPasswordMgr()
        self.passwd = passwd
        self.add_password = self.passwd.add_password
        self.retried = 0
        self.nonce_count = 0
        self.last_nonce = None

    eleza reset_retry_count(self):
        self.retried = 0

    eleza http_error_auth_reqed(self, auth_header, host, req, headers):
        authreq = headers.get(auth_header, None)
        ikiwa self.retried > 5:
            # Don't fail endlessly - ikiwa we failed once, we'll probably
            # fail a second time. Hm. Unless the Password Manager is
            # prompting for the information. Crap. This isn't great
            # but it's better than the current 'repeat until recursion
            # depth exceeded' approach <wink>
            raise HTTPError(req.full_url, 401, "digest auth failed",
                            headers, None)
        else:
            self.retried += 1
        ikiwa authreq:
            scheme = authreq.split()[0]
            ikiwa scheme.lower() == 'digest':
                rudisha self.retry_http_digest_auth(req, authreq)
            elikiwa scheme.lower() != 'basic':
                raise ValueError("AbstractDigestAuthHandler does not support"
                                 " the following scheme: '%s'" % scheme)

    eleza retry_http_digest_auth(self, req, auth):
        token, challenge = auth.split(' ', 1)
        chal = parse_keqv_list(filter(None, parse_http_list(challenge)))
        auth = self.get_authorization(req, chal)
        ikiwa auth:
            auth_val = 'Digest %s' % auth
            ikiwa req.headers.get(self.auth_header, None) == auth_val:
                rudisha None
            req.add_unredirected_header(self.auth_header, auth_val)
            resp = self.parent.open(req, timeout=req.timeout)
            rudisha resp

    eleza get_cnonce(self, nonce):
        # The cnonce-value is an opaque
        # quoted string value provided by the client and used by both client
        # and server to avoid chosen plaintext attacks, to provide mutual
        # authentication, and to provide some message integrity protection.
        # This isn't a fabulous effort, but it's probably Good Enough.
        s = "%s:%s:%s:" % (self.nonce_count, nonce, time.ctime())
        b = s.encode("ascii") + _randombytes(8)
        dig = hashlib.sha1(b).hexdigest()
        rudisha dig[:16]

    eleza get_authorization(self, req, chal):
        try:
            realm = chal['realm']
            nonce = chal['nonce']
            qop = chal.get('qop')
            algorithm = chal.get('algorithm', 'MD5')
            # mod_digest doesn't send an opaque, even though it isn't
            # supposed to be optional
            opaque = chal.get('opaque', None)
        except KeyError:
            rudisha None

        H, KD = self.get_algorithm_impls(algorithm)
        ikiwa H is None:
            rudisha None

        user, pw = self.passwd.find_user_password(realm, req.full_url)
        ikiwa user is None:
            rudisha None

        # XXX not implemented yet
        ikiwa req.data is not None:
            entdig = self.get_entity_digest(req.data, chal)
        else:
            entdig = None

        A1 = "%s:%s:%s" % (user, realm, pw)
        A2 = "%s:%s" % (req.get_method(),
                        # XXX selector: what about proxies and full urls
                        req.selector)
        ikiwa qop == 'auth':
            ikiwa nonce == self.last_nonce:
                self.nonce_count += 1
            else:
                self.nonce_count = 1
                self.last_nonce = nonce
            ncvalue = '%08x' % self.nonce_count
            cnonce = self.get_cnonce(nonce)
            noncebit = "%s:%s:%s:%s:%s" % (nonce, ncvalue, cnonce, qop, H(A2))
            respdig = KD(H(A1), noncebit)
        elikiwa qop is None:
            respdig = KD(H(A1), "%s:%s" % (nonce, H(A2)))
        else:
            # XXX handle auth-int.
            raise URLError("qop '%s' is not supported." % qop)

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
        elikiwa algorithm == 'SHA':
            H = lambda x: hashlib.sha1(x.encode("ascii")).hexdigest()
        # XXX MD5-sess
        else:
            raise ValueError("Unsupported digest authentication "
                             "algorithm %r" % algorithm)
        KD = lambda s, d: H("%s:%s" % (s, d))
        rudisha H, KD

    eleza get_entity_digest(self, data, chal):
        # XXX not implemented yet
        rudisha None


kundi HTTPDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    """An authentication protocol defined by RFC 2069

    Digest authentication improves on basic authentication because it
    does not transmit passwords in the clear.
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
        ikiwa not host:
            raise URLError('no host given')

        ikiwa request.data is not None:  # POST
            data = request.data
            ikiwa isinstance(data, str):
                msg = "POST data should be bytes, an iterable of bytes, " \
                      "or a file object. It cannot be of type str."
                raise TypeError(msg)
            ikiwa not request.has_header('Content-type'):
                request.add_unredirected_header(
                    'Content-type',
                    'application/x-www-form-urlencoded')
            ikiwa (not request.has_header('Content-length')
                    and not request.has_header('Transfer-encoding')):
                content_length = self._get_content_length(request)
                ikiwa content_length is not None:
                    request.add_unredirected_header(
                            'Content-length', str(content_length))
                else:
                    request.add_unredirected_header(
                            'Transfer-encoding', 'chunked')

        sel_host = host
        ikiwa request.has_proxy():
            scheme, sel = _splittype(request.selector)
            sel_host, sel_path = _splithost(sel)
        ikiwa not request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            ikiwa not request.has_header(name):
                request.add_unredirected_header(name, value)

        rudisha request

    eleza do_open(self, http_class, req, **http_conn_args):
        """Return an HTTPResponse object for the request, using http_class.

        http_kundi must implement the HTTPConnection API kutoka http.client.
        """
        host = req.host
        ikiwa not host:
            raise URLError('no host given')

        # will parse host:port
        h = http_class(host, timeout=req.timeout, **http_conn_args)
        h.set_debuglevel(self._debuglevel)

        headers = dict(req.unredirected_hdrs)
        headers.update({k: v for k, v in req.headers.items()
                        ikiwa k not in headers})

        # TODO(jhylton): Should this be redesigned to handle
        # persistent connections?

        # We want to make an HTTP/1.1 request, but the addinfourl
        # kundi isn't prepared to deal with a persistent connection.
        # It will try to read all remaining data kutoka the socket,
        # which will block while the server waits for the next request.
        # So make sure the connection gets closed after the (only)
        # request.
        headers["Connection"] = "close"
        headers = {name.title(): val for name, val in headers.items()}

        ikiwa req._tunnel_host:
            tunnel_headers = {}
            proxy_auth_hdr = "Proxy-Authorization"
            ikiwa proxy_auth_hdr in headers:
                tunnel_headers[proxy_auth_hdr] = headers[proxy_auth_hdr]
                # Proxy-Authorization should not be sent to origin
                # server.
                del headers[proxy_auth_hdr]
            h.set_tunnel(req._tunnel_host, headers=tunnel_headers)

        try:
            try:
                h.request(req.get_method(), req.selector, req.data, headers,
                          encode_chunked=req.has_header('Transfer-encoding'))
            except OSError as err: # timeout error
                raise URLError(err)
            r = h.getresponse()
        except:
            h.close()
            raise

        # If the server does not send us a 'Connection: close' header,
        # HTTPConnection assumes the socket should be left open. Manually
        # mark the socket to be closed when this response object goes away.
        ikiwa h.sock:
            h.sock.close()
            h.sock = None

        r.url = req.get_full_url()
        # This line replaces the .msg attribute of the HTTPResponse
        # with .headers, because urllib clients expect the response to
        # have the reason in .msg.  It would be good to mark this
        # attribute is deprecated and get then to use info() or
        # .headers.
        r.msg = r.reason
        rudisha r


kundi HTTPHandler(AbstractHTTPHandler):

    eleza http_open(self, req):
        rudisha self.do_open(http.client.HTTPConnection, req)

    http_request = AbstractHTTPHandler.do_request_

ikiwa hasattr(http.client, 'HTTPSConnection'):

    kundi HTTPSHandler(AbstractHTTPHandler):

        eleza __init__(self, debuglevel=0, context=None, check_hostname=None):
            AbstractHTTPHandler.__init__(self, debuglevel)
            self._context = context
            self._check_hostname = check_hostname

        eleza https_open(self, req):
            rudisha self.do_open(http.client.HTTPSConnection, req,
                context=self._context, check_hostname=self._check_hostname)

        https_request = AbstractHTTPHandler.do_request_

    __all__.append('HTTPSHandler')

kundi HTTPCookieProcessor(BaseHandler):
    eleza __init__(self, cookiejar=None):
        agiza http.cookiejar
        ikiwa cookiejar is None:
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
        raise URLError('unknown url type: %s' % type)

eleza parse_keqv_list(l):
    """Parse list of key=value strings where keys are not duplicated."""
    parsed = {}
    for elt in l:
        k, v = elt.split('=', 1)
        ikiwa v[0] == '"' and v[-1] == '"':
            v = v[1:-1]
        parsed[k] = v
    rudisha parsed

eleza parse_http_list(s):
    """Parse lists as described by RFC 2068 Section 2.

    In particular, parse comma-separated lists where the elements of
    the list may include quoted-strings.  A quoted-string could
    contain a comma.  A non-quoted string could have quotes in the
    middle.  Neither commas nor quotes count ikiwa they are escaped.
    Only double-quotes count, not single-quotes.
    """
    res = []
    part = ''

    escape = quote = False
    for cur in s:
        ikiwa escape:
            part += cur
            escape = False
            continue
        ikiwa quote:
            ikiwa cur == '\\':
                escape = True
                continue
            elikiwa cur == '"':
                quote = False
            part += cur
            continue

        ikiwa cur == ',':
            res.append(part)
            part = ''
            continue

        ikiwa cur == '"':
            quote = True

        part += cur

    # append last part
    ikiwa part:
        res.append(part)

    rudisha [part.strip() for part in res]

kundi FileHandler(BaseHandler):
    # Use local file or FTP depending on form of URL
    eleza file_open(self, req):
        url = req.selector
        ikiwa url[:2] == '//' and url[2:3] != '/' and (req.host and
                req.host != 'localhost'):
            ikiwa not req.host in self.get_names():
                raise URLError("file:// scheme is supported only on localhost")
        else:
            rudisha self.open_local_file(req)

    # names for the localhost
    names = None
    eleza get_names(self):
        ikiwa FileHandler.names is None:
            try:
                FileHandler.names = tuple(
                    socket.gethostbyname_ex('localhost')[2] +
                    socket.gethostbyname_ex(socket.gethostname())[2])
            except socket.gaierror:
                FileHandler.names = (socket.gethostbyname('localhost'),)
        rudisha FileHandler.names

    # not entirely sure what the rules are here
    eleza open_local_file(self, req):
        agiza email.utils
        agiza mimetypes
        host = req.host
        filename = req.selector
        localfile = url2pathname(filename)
        try:
            stats = os.stat(localfile)
            size = stats.st_size
            modified = email.utils.formatdate(stats.st_mtime, usegmt=True)
            mtype = mimetypes.guess_type(filename)[0]
            headers = email.message_kutoka_string(
                'Content-type: %s\nContent-length: %d\nLast-modified: %s\n' %
                (mtype or 'text/plain', size, modified))
            ikiwa host:
                host, port = _splitport(host)
            ikiwa not host or \
                (not port and _safe_gethostbyname(host) in self.get_names()):
                ikiwa host:
                    origurl = 'file://' + host + filename
                else:
                    origurl = 'file://' + filename
                rudisha addinfourl(open(localfile, 'rb'), headers, origurl)
        except OSError as exp:
            raise URLError(exp)
        raise URLError('file not on local host')

eleza _safe_gethostbyname(host):
    try:
        rudisha socket.gethostbyname(host)
    except socket.gaierror:
        rudisha None

kundi FTPHandler(BaseHandler):
    eleza ftp_open(self, req):
        agiza ftplib
        agiza mimetypes
        host = req.host
        ikiwa not host:
            raise URLError('ftp error: no host given')
        host, port = _splitport(host)
        ikiwa port is None:
            port = ftplib.FTP_PORT
        else:
            port = int(port)

        # username/password handling
        user, host = _splituser(host)
        ikiwa user:
            user, passwd = _splitpasswd(user)
        else:
            passwd = None
        host = unquote(host)
        user = user or ''
        passwd = passwd or ''

        try:
            host = socket.gethostbyname(host)
        except OSError as msg:
            raise URLError(msg)
        path, attrs = _splitattr(req.selector)
        dirs = path.split('/')
        dirs = list(map(unquote, dirs))
        dirs, file = dirs[:-1], dirs[-1]
        ikiwa dirs and not dirs[0]:
            dirs = dirs[1:]
        try:
            fw = self.connect_ftp(user, passwd, host, port, dirs, req.timeout)
            type = file and 'I' or 'D'
            for attr in attrs:
                attr, value = _splitvalue(attr)
                ikiwa attr.lower() == 'type' and \
                   value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
            fp, retrlen = fw.retrfile(file, type)
            headers = ""
            mtype = mimetypes.guess_type(req.full_url)[0]
            ikiwa mtype:
                headers += "Content-type: %s\n" % mtype
            ikiwa retrlen is not None and retrlen >= 0:
                headers += "Content-length: %d\n" % retrlen
            headers = email.message_kutoka_string(headers)
            rudisha addinfourl(fp, headers, req.full_url)
        except ftplib.all_errors as exp:
            exc = URLError('ftp error: %r' % exp)
            raise exc.with_traceback(sys.exc_info()[2])

    eleza connect_ftp(self, user, passwd, host, port, dirs, timeout):
        rudisha ftpwrapper(user, passwd, host, port, dirs, timeout,
                          persistent=False)

kundi CacheFTPHandler(FTPHandler):
    # XXX would be nice to have pluggable cache strategies
    # XXX this stuff is definitely not thread safe
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

    eleza connect_ftp(self, user, passwd, host, port, dirs, timeout):
        key = user, host, port, '/'.join(dirs), timeout
        ikiwa key in self.cache:
            self.timeout[key] = time.time() + self.delay
        else:
            self.cache[key] = ftpwrapper(user, passwd, host, port,
                                         dirs, timeout)
            self.timeout[key] = time.time() + self.delay
        self.check_cache()
        rudisha self.cache[key]

    eleza check_cache(self):
        # first check for old ones
        t = time.time()
        ikiwa self.soonest <= t:
            for k, v in list(self.timeout.items()):
                ikiwa v < t:
                    self.cache[k].close()
                    del self.cache[k]
                    del self.timeout[k]
        self.soonest = min(list(self.timeout.values()))

        # then check the size
        ikiwa len(self.cache) == self.max_conns:
            for k, v in list(self.timeout.items()):
                ikiwa v == self.soonest:
                    del self.cache[k]
                    del self.timeout[k]
                    break
            self.soonest = min(list(self.timeout.values()))

    eleza clear_cache(self):
        for conn in self.cache.values():
            conn.close()
        self.cache.clear()
        self.timeout.clear()

kundi DataHandler(BaseHandler):
    eleza data_open(self, req):
        # data URLs as specified in RFC 2397.
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

        # even base64 encoded data URLs might be quoted so unquote in any case:
        data = unquote_to_bytes(data)
        ikiwa mediatype.endswith(";base64"):
            data = base64.decodebytes(data)
            mediatype = mediatype[:-7]

        ikiwa not mediatype:
            mediatype = "text/plain;charset=US-ASCII"

        headers = email.message_kutoka_string("Content-type: %s\nContent-length: %d\n" %
            (mediatype, len(data)))

        rudisha addinfourl(io.BytesIO(data), headers, url)


# Code move kutoka the old urllib module

MAXFTPCACHE = 10        # Trim the ftp cache beyond this size

# Helper for non-unix systems
ikiwa os.name == 'nt':
    kutoka nturl2path agiza url2pathname, pathname2url
else:
    eleza url2pathname(pathname):
        """OS-specific conversion kutoka a relative URL of the 'file' scheme
        to a file system path; not recommended for general use."""
        rudisha unquote(pathname)

    eleza pathname2url(pathname):
        """OS-specific conversion kutoka a file system path to a relative URL
        of the 'file' scheme; not recommended for general use."""
        rudisha quote(pathname)


ftpcache = {}


kundi URLopener:
    """Class to open URLs.
    This is a kundi rather than just a subroutine because we may need
    more than one set of global protocol-specific options.
    Note -- this is a base kundi for those who don't want the
    automatic handling of errors type 302 (relocated) and 401
    (authorization needed)."""

    __tempfiles = None

    version = "Python-urllib/%s" % __version__

    # Constructor
    eleza __init__(self, proxies=None, **x509):
        msg = "%(class)s style of invoking requests is deprecated. " \
              "Use newer urlopen functions/methods" % {'class': self.__class__.__name__}
        warnings.warn(msg, DeprecationWarning, stacklevel=3)
        ikiwa proxies is None:
            proxies = getproxies()
        assert hasattr(proxies, 'keys'), "proxies must be a mapping"
        self.proxies = proxies
        self.key_file = x509.get('key_file')
        self.cert_file = x509.get('cert_file')
        self.addheaders = [('User-Agent', self.version), ('Accept', '*/*')]
        self.__tempfiles = []
        self.__unlink = os.unlink # See cleanup()
        self.tempcache = None
        # Undocumented feature: ikiwa you assign {} to tempcache,
        # it is used to cache files retrieved with
        # self.retrieve().  This is not enabled by default
        # since it does not work for changing documents (and I
        # haven't got the logic to check expiration headers
        # yet).
        self.ftpcache = ftpcache
        # Undocumented feature: you can use a different
        # ftp cache by assigning to the .ftpcache member;
        # in case you want logically independent URL openers
        # XXX This is not threadsafe.  Bah.

    eleza __del__(self):
        self.close()

    eleza close(self):
        self.cleanup()

    eleza cleanup(self):
        # This code sometimes runs when the rest of this module
        # has already been deleted, so it can't use any globals
        # or agiza anything.
        ikiwa self.__tempfiles:
            for file in self.__tempfiles:
                try:
                    self.__unlink(file)
                except OSError:
                    pass
            del self.__tempfiles[:]
        ikiwa self.tempcache:
            self.tempcache.clear()

    eleza addheader(self, *args):
        """Add a header to be used by the HTTP interface only
        e.g. u.addheader('Accept', 'sound/basic')"""
        self.addheaders.append(args)

    # External interface
    eleza open(self, fullurl, data=None):
        """Use URLopener().open(file) instead of open(file, 'r')."""
        fullurl = unwrap(_to_bytes(fullurl))
        fullurl = quote(fullurl, safe="%/:=&?~#+!$,;'@()*[]|")
        ikiwa self.tempcache and fullurl in self.tempcache:
            filename, headers = self.tempcache[fullurl]
            fp = open(filename, 'rb')
            rudisha addinfourl(fp, headers, fullurl)
        urltype, url = _splittype(fullurl)
        ikiwa not urltype:
            urltype = 'file'
        ikiwa urltype in self.proxies:
            proxy = self.proxies[urltype]
            urltype, proxyhost = _splittype(proxy)
            host, selector = _splithost(proxyhost)
            url = (host, fullurl) # Signal special case to open_*()
        else:
            proxy = None
        name = 'open_' + urltype
        self.type = urltype
        name = name.replace('-', '_')
        ikiwa not hasattr(self, name) or name == 'open_local_file':
            ikiwa proxy:
                rudisha self.open_unknown_proxy(proxy, fullurl, data)
            else:
                rudisha self.open_unknown(fullurl, data)
        try:
            ikiwa data is None:
                rudisha getattr(self, name)(url)
            else:
                rudisha getattr(self, name)(url, data)
        except (HTTPError, URLError):
            raise
        except OSError as msg:
            raise OSError('socket error', msg).with_traceback(sys.exc_info()[2])

    eleza open_unknown(self, fullurl, data=None):
        """Overridable interface to open unknown URL type."""
        type, url = _splittype(fullurl)
        raise OSError('url error', 'unknown url type', type)

    eleza open_unknown_proxy(self, proxy, fullurl, data=None):
        """Overridable interface to open unknown URL type."""
        type, url = _splittype(fullurl)
        raise OSError('url error', 'invalid proxy for %s' % type, proxy)

    # External interface
    eleza retrieve(self, url, filename=None, reporthook=None, data=None):
        """retrieve(url) returns (filename, headers) for a local object
        or (tempfilename, headers) for a remote object."""
        url = unwrap(_to_bytes(url))
        ikiwa self.tempcache and url in self.tempcache:
            rudisha self.tempcache[url]
        type, url1 = _splittype(url)
        ikiwa filename is None and (not type or type == 'file'):
            try:
                fp = self.open_local_file(url1)
                hdrs = fp.info()
                fp.close()
                rudisha url2pathname(_splithost(url1)[1]), hdrs
            except OSError as msg:
                pass
        fp = self.open(url, data)
        try:
            headers = fp.info()
            ikiwa filename:
                tfp = open(filename, 'wb')
            else:
                garbage, path = _splittype(url)
                garbage, path = _splithost(path or "")
                path, garbage = _splitquery(path or "")
                path, garbage = _splitattr(path or "")
                suffix = os.path.splitext(path)[1]
                (fd, filename) = tempfile.mkstemp(suffix)
                self.__tempfiles.append(filename)
                tfp = os.fdopen(fd, 'wb')
            try:
                result = filename, headers
                ikiwa self.tempcache is not None:
                    self.tempcache[url] = result
                bs = 1024*8
                size = -1
                read = 0
                blocknum = 0
                ikiwa "content-length" in headers:
                    size = int(headers["Content-Length"])
                ikiwa reporthook:
                    reporthook(blocknum, bs, size)
                while 1:
                    block = fp.read(bs)
                    ikiwa not block:
                        break
                    read += len(block)
                    tfp.write(block)
                    blocknum += 1
                    ikiwa reporthook:
                        reporthook(blocknum, bs, size)
            finally:
                tfp.close()
        finally:
            fp.close()

        # raise exception ikiwa actual size does not match content-length header
        ikiwa size >= 0 and read < size:
            raise ContentTooShortError(
                "retrieval incomplete: got only %i out of %i bytes"
                % (read, size), result)

        rudisha result

    # Each method named open_<type> knows how to open that type of URL

    eleza _open_generic_http(self, connection_factory, url, data):
        """Make an HTTP connection using connection_class.

        This is an internal method that should be called kutoka
        open_http() or open_https().

        Arguments:
        - connection_factory should take a host name and rudisha an
          HTTPConnection instance.
        - url is the url to retrieval or a host, relative-path pair.
        - data is payload for a POST request or None.
        """

        user_passwd = None
        proxy_passwd= None
        ikiwa isinstance(url, str):
            host, selector = _splithost(url)
            ikiwa host:
                user_passwd, host = _splituser(host)
                host = unquote(host)
            realhost = host
        else:
            host, selector = url
            # check whether the proxy contains authorization information
            proxy_passwd, host = _splituser(host)
            # now we proceed with the url we want to obtain
            urltype, rest = _splittype(selector)
            url = rest
            user_passwd = None
            ikiwa urltype.lower() != 'http':
                realhost = None
            else:
                realhost, rest = _splithost(rest)
                ikiwa realhost:
                    user_passwd, realhost = _splituser(realhost)
                ikiwa user_passwd:
                    selector = "%s://%s%s" % (urltype, realhost, rest)
                ikiwa proxy_bypass(realhost):
                    host = realhost

        ikiwa not host: raise OSError('http error', 'no host given')

        ikiwa proxy_passwd:
            proxy_passwd = unquote(proxy_passwd)
            proxy_auth = base64.b64encode(proxy_passwd.encode()).decode('ascii')
        else:
            proxy_auth = None

        ikiwa user_passwd:
            user_passwd = unquote(user_passwd)
            auth = base64.b64encode(user_passwd.encode()).decode('ascii')
        else:
            auth = None
        http_conn = connection_factory(host)
        headers = {}
        ikiwa proxy_auth:
            headers["Proxy-Authorization"] = "Basic %s" % proxy_auth
        ikiwa auth:
            headers["Authorization"] =  "Basic %s" % auth
        ikiwa realhost:
            headers["Host"] = realhost

        # Add Connection:close as we don't support persistent connections yet.
        # This helps in closing the socket and avoiding ResourceWarning

        headers["Connection"] = "close"

        for header, value in self.addheaders:
            headers[header] = value

        ikiwa data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            http_conn.request("POST", selector, data, headers)
        else:
            http_conn.request("GET", selector, headers=headers)

        try:
            response = http_conn.getresponse()
        except http.client.BadStatusLine:
            # something went wrong with the HTTP status line
            raise URLError("http protocol error: bad status line")

        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, and accepted.
        ikiwa 200 <= response.status < 300:
            rudisha addinfourl(response, response.msg, "http:" + url,
                              response.status)
        else:
            rudisha self.http_error(
                url, response.fp,
                response.status, response.reason, response.msg, data)

    eleza open_http(self, url, data=None):
        """Use HTTP protocol."""
        rudisha self._open_generic_http(http.client.HTTPConnection, url, data)

    eleza http_error(self, url, fp, errcode, errmsg, headers, data=None):
        """Handle http errors.

        Derived kundi can override this, or provide specific handlers
        named http_error_DDD where DDD is the 3-digit error code."""
        # First check ikiwa there's a specific handler for this error
        name = 'http_error_%d' % errcode
        ikiwa hasattr(self, name):
            method = getattr(self, name)
            ikiwa data is None:
                result = method(url, fp, errcode, errmsg, headers)
            else:
                result = method(url, fp, errcode, errmsg, headers, data)
            ikiwa result: rudisha result
        rudisha self.http_error_default(url, fp, errcode, errmsg, headers)

    eleza http_error_default(self, url, fp, errcode, errmsg, headers):
        """Default error handler: close the connection and raise OSError."""
        fp.close()
        raise HTTPError(url, errcode, errmsg, headers, None)

    ikiwa _have_ssl:
        eleza _https_connection(self, host):
            rudisha http.client.HTTPSConnection(host,
                                           key_file=self.key_file,
                                           cert_file=self.cert_file)

        eleza open_https(self, url, data=None):
            """Use HTTPS protocol."""
            rudisha self._open_generic_http(self._https_connection, url, data)

    eleza open_file(self, url):
        """Use local file or FTP depending on form of URL."""
        ikiwa not isinstance(url, str):
            raise URLError('file error: proxy support for file protocol currently not implemented')
        ikiwa url[:2] == '//' and url[2:3] != '/' and url[2:12].lower() != 'localhost/':
            raise ValueError("file:// scheme is supported only on localhost")
        else:
            rudisha self.open_local_file(url)

    eleza open_local_file(self, url):
        """Use local file."""
        agiza email.utils
        agiza mimetypes
        host, file = _splithost(url)
        localname = url2pathname(file)
        try:
            stats = os.stat(localname)
        except OSError as e:
            raise URLError(e.strerror, e.filename)
        size = stats.st_size
        modified = email.utils.formatdate(stats.st_mtime, usegmt=True)
        mtype = mimetypes.guess_type(url)[0]
        headers = email.message_kutoka_string(
            'Content-Type: %s\nContent-Length: %d\nLast-modified: %s\n' %
            (mtype or 'text/plain', size, modified))
        ikiwa not host:
            urlfile = file
            ikiwa file[:1] == '/':
                urlfile = 'file://' + file
            rudisha addinfourl(open(localname, 'rb'), headers, urlfile)
        host, port = _splitport(host)
        ikiwa (not port
           and socket.gethostbyname(host) in ((localhost(),) + thishost())):
            urlfile = file
            ikiwa file[:1] == '/':
                urlfile = 'file://' + file
            elikiwa file[:2] == './':
                raise ValueError("local file url may start with / or file:. Unknown url of type: %s" % url)
            rudisha addinfourl(open(localname, 'rb'), headers, urlfile)
        raise URLError('local file error: not on local host')

    eleza open_ftp(self, url):
        """Use FTP protocol."""
        ikiwa not isinstance(url, str):
            raise URLError('ftp error: proxy support for ftp protocol currently not implemented')
        agiza mimetypes
        host, path = _splithost(url)
        ikiwa not host: raise URLError('ftp error: no host given')
        host, port = _splitport(host)
        user, host = _splituser(host)
        ikiwa user: user, passwd = _splitpasswd(user)
        else: passwd = None
        host = unquote(host)
        user = unquote(user or '')
        passwd = unquote(passwd or '')
        host = socket.gethostbyname(host)
        ikiwa not port:
            agiza ftplib
            port = ftplib.FTP_PORT
        else:
            port = int(port)
        path, attrs = _splitattr(path)
        path = unquote(path)
        dirs = path.split('/')
        dirs, file = dirs[:-1], dirs[-1]
        ikiwa dirs and not dirs[0]: dirs = dirs[1:]
        ikiwa dirs and not dirs[0]: dirs[0] = '/'
        key = user, host, port, '/'.join(dirs)
        # XXX thread unsafe!
        ikiwa len(self.ftpcache) > MAXFTPCACHE:
            # Prune the cache, rather arbitrarily
            for k in list(self.ftpcache):
                ikiwa k != key:
                    v = self.ftpcache[k]
                    del self.ftpcache[k]
                    v.close()
        try:
            ikiwa key not in self.ftpcache:
                self.ftpcache[key] = \
                    ftpwrapper(user, passwd, host, port, dirs)
            ikiwa not file: type = 'D'
            else: type = 'I'
            for attr in attrs:
                attr, value = _splitvalue(attr)
                ikiwa attr.lower() == 'type' and \
                   value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
            (fp, retrlen) = self.ftpcache[key].retrfile(file, type)
            mtype = mimetypes.guess_type("ftp:" + url)[0]
            headers = ""
            ikiwa mtype:
                headers += "Content-Type: %s\n" % mtype
            ikiwa retrlen is not None and retrlen >= 0:
                headers += "Content-Length: %d\n" % retrlen
            headers = email.message_kutoka_string(headers)
            rudisha addinfourl(fp, headers, "ftp:" + url)
        except ftperrors() as exp:
            raise URLError('ftp error %r' % exp).with_traceback(sys.exc_info()[2])

    eleza open_data(self, url, data=None):
        """Use "data" URL."""
        ikiwa not isinstance(url, str):
            raise URLError('data error: proxy support for data protocol currently not implemented')
        # ignore POSTed data
        #
        # syntax of data URLs:
        # dataurl   := "data:" [ mediatype ] [ ";base64" ] "," data
        # mediatype := [ type "/" subtype ] *( ";" parameter )
        # data      := *urlchar
        # parameter := attribute "=" value
        try:
            [type, data] = url.split(',', 1)
        except ValueError:
            raise OSError('data error', 'bad data URL')
        ikiwa not type:
            type = 'text/plain;charset=US-ASCII'
        semi = type.rfind(';')
        ikiwa semi >= 0 and '=' not in type[semi:]:
            encoding = type[semi+1:]
            type = type[:semi]
        else:
            encoding = ''
        msg = []
        msg.append('Date: %s'%time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                                            time.gmtime(time.time())))
        msg.append('Content-type: %s' % type)
        ikiwa encoding == 'base64':
            # XXX is this encoding/decoding ok?
            data = base64.decodebytes(data.encode('ascii')).decode('latin-1')
        else:
            data = unquote(data)
        msg.append('Content-Length: %d' % len(data))
        msg.append('')
        msg.append(data)
        msg = '\n'.join(msg)
        headers = email.message_kutoka_string(msg)
        f = io.StringIO(msg)
        #f.fileno = None     # needed for addinfourl
        rudisha addinfourl(f, headers, url)


kundi FancyURLopener(URLopener):
    """Derived kundi with handlers for errors we can handle (perhaps)."""

    eleza __init__(self, *args, **kwargs):
        URLopener.__init__(self, *args, **kwargs)
        self.auth_cache = {}
        self.tries = 0
        self.maxtries = 10

    eleza http_error_default(self, url, fp, errcode, errmsg, headers):
        """Default error handling -- don't raise an exception."""
        rudisha addinfourl(fp, headers, "http:" + url, errcode)

    eleza http_error_302(self, url, fp, errcode, errmsg, headers, data=None):
        """Error 302 -- relocated (temporarily)."""
        self.tries += 1
        try:
            ikiwa self.maxtries and self.tries >= self.maxtries:
                ikiwa hasattr(self, "http_error_500"):
                    meth = self.http_error_500
                else:
                    meth = self.http_error_default
                rudisha meth(url, fp, 500,
                            "Internal Server Error: Redirect Recursion",
                            headers)
            result = self.redirect_internal(url, fp, errcode, errmsg,
                                            headers, data)
            rudisha result
        finally:
            self.tries = 0

    eleza redirect_internal(self, url, fp, errcode, errmsg, headers, data):
        ikiwa 'location' in headers:
            newurl = headers['location']
        elikiwa 'uri' in headers:
            newurl = headers['uri']
        else:
            return
        fp.close()

        # In case the server sent a relative URL, join with original:
        newurl = urljoin(self.type + ":" + url, newurl)

        urlparts = urlparse(newurl)

        # For security reasons, we don't allow redirection to anything other
        # than http, https and ftp.

        # We are using newer HTTPError with older redirect_internal method
        # This older method will get deprecated in 3.3

        ikiwa urlparts.scheme not in ('http', 'https', 'ftp', ''):
            raise HTTPError(newurl, errcode,
                            errmsg +
                            " Redirection to url '%s' is not allowed." % newurl,
                            headers, fp)

        rudisha self.open(newurl)

    eleza http_error_301(self, url, fp, errcode, errmsg, headers, data=None):
        """Error 301 -- also relocated (permanently)."""
        rudisha self.http_error_302(url, fp, errcode, errmsg, headers, data)

    eleza http_error_303(self, url, fp, errcode, errmsg, headers, data=None):
        """Error 303 -- also relocated (essentially identical to 302)."""
        rudisha self.http_error_302(url, fp, errcode, errmsg, headers, data)

    eleza http_error_307(self, url, fp, errcode, errmsg, headers, data=None):
        """Error 307 -- relocated, but turn POST into error."""
        ikiwa data is None:
            rudisha self.http_error_302(url, fp, errcode, errmsg, headers, data)
        else:
            rudisha self.http_error_default(url, fp, errcode, errmsg, headers)

    eleza http_error_401(self, url, fp, errcode, errmsg, headers, data=None,
            retry=False):
        """Error 401 -- authentication required.
        This function supports Basic authentication only."""
        ikiwa 'www-authenticate' not in headers:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        stuff = headers['www-authenticate']
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        ikiwa not match:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        scheme, realm = match.groups()
        ikiwa scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        ikiwa not retry:
            URLopener.http_error_default(self, url, fp, errcode, errmsg,
                    headers)
        name = 'retry_' + self.type + '_basic_auth'
        ikiwa data is None:
            rudisha getattr(self,name)(url, realm)
        else:
            rudisha getattr(self,name)(url, realm, data)

    eleza http_error_407(self, url, fp, errcode, errmsg, headers, data=None,
            retry=False):
        """Error 407 -- proxy authentication required.
        This function supports Basic authentication only."""
        ikiwa 'proxy-authenticate' not in headers:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        stuff = headers['proxy-authenticate']
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        ikiwa not match:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        scheme, realm = match.groups()
        ikiwa scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        ikiwa not retry:
            URLopener.http_error_default(self, url, fp, errcode, errmsg,
                    headers)
        name = 'retry_proxy_' + self.type + '_basic_auth'
        ikiwa data is None:
            rudisha getattr(self,name)(url, realm)
        else:
            rudisha getattr(self,name)(url, realm, data)

    eleza retry_proxy_http_basic_auth(self, url, realm, data=None):
        host, selector = _splithost(url)
        newurl = 'http://' + host + selector
        proxy = self.proxies['http']
        urltype, proxyhost = _splittype(proxy)
        proxyhost, proxyselector = _splithost(proxyhost)
        i = proxyhost.find('@') + 1
        proxyhost = proxyhost[i:]
        user, passwd = self.get_user_passwd(proxyhost, realm, i)
        ikiwa not (user or passwd): rudisha None
        proxyhost = "%s:%s@%s" % (quote(user, safe=''),
                                  quote(passwd, safe=''), proxyhost)
        self.proxies['http'] = 'http://' + proxyhost + proxyselector
        ikiwa data is None:
            rudisha self.open(newurl)
        else:
            rudisha self.open(newurl, data)

    eleza retry_proxy_https_basic_auth(self, url, realm, data=None):
        host, selector = _splithost(url)
        newurl = 'https://' + host + selector
        proxy = self.proxies['https']
        urltype, proxyhost = _splittype(proxy)
        proxyhost, proxyselector = _splithost(proxyhost)
        i = proxyhost.find('@') + 1
        proxyhost = proxyhost[i:]
        user, passwd = self.get_user_passwd(proxyhost, realm, i)
        ikiwa not (user or passwd): rudisha None
        proxyhost = "%s:%s@%s" % (quote(user, safe=''),
                                  quote(passwd, safe=''), proxyhost)
        self.proxies['https'] = 'https://' + proxyhost + proxyselector
        ikiwa data is None:
            rudisha self.open(newurl)
        else:
            rudisha self.open(newurl, data)

    eleza retry_http_basic_auth(self, url, realm, data=None):
        host, selector = _splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, passwd = self.get_user_passwd(host, realm, i)
        ikiwa not (user or passwd): rudisha None
        host = "%s:%s@%s" % (quote(user, safe=''),
                             quote(passwd, safe=''), host)
        newurl = 'http://' + host + selector
        ikiwa data is None:
            rudisha self.open(newurl)
        else:
            rudisha self.open(newurl, data)

    eleza retry_https_basic_auth(self, url, realm, data=None):
        host, selector = _splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, passwd = self.get_user_passwd(host, realm, i)
        ikiwa not (user or passwd): rudisha None
        host = "%s:%s@%s" % (quote(user, safe=''),
                             quote(passwd, safe=''), host)
        newurl = 'https://' + host + selector
        ikiwa data is None:
            rudisha self.open(newurl)
        else:
            rudisha self.open(newurl, data)

    eleza get_user_passwd(self, host, realm, clear_cache=0):
        key = realm + '@' + host.lower()
        ikiwa key in self.auth_cache:
            ikiwa clear_cache:
                del self.auth_cache[key]
            else:
                rudisha self.auth_cache[key]
        user, passwd = self.prompt_user_passwd(host, realm)
        ikiwa user or passwd: self.auth_cache[key] = (user, passwd)
        rudisha user, passwd

    eleza prompt_user_passwd(self, host, realm):
        """Override this in a GUI environment!"""
        agiza getpass
        try:
            user = input("Enter username for %s at %s: " % (realm, host))
            passwd = getpass.getpass("Enter password for %s in %s at %s: " %
                (user, realm, host))
            rudisha user, passwd
        except KeyboardInterrupt:
            andika()
            rudisha None, None


# Utility functions

_localhost = None
eleza localhost():
    """Return the IP address of the magic hostname 'localhost'."""
    global _localhost
    ikiwa _localhost is None:
        _localhost = socket.gethostbyname('localhost')
    rudisha _localhost

_thishost = None
eleza thishost():
    """Return the IP addresses of the current host."""
    global _thishost
    ikiwa _thishost is None:
        try:
            _thishost = tuple(socket.gethostbyname_ex(socket.gethostname())[2])
        except socket.gaierror:
            _thishost = tuple(socket.gethostbyname_ex('localhost')[2])
    rudisha _thishost

_ftperrors = None
eleza ftperrors():
    """Return the set of errors raised by the FTP class."""
    global _ftperrors
    ikiwa _ftperrors is None:
        agiza ftplib
        _ftperrors = ftplib.all_errors
    rudisha _ftperrors

_noheaders = None
eleza noheaders():
    """Return an empty email Message object."""
    global _noheaders
    ikiwa _noheaders is None:
        _noheaders = email.message_kutoka_string("")
    rudisha _noheaders


# Utility classes

kundi ftpwrapper:
    """Class used by open_ftp() for cache of open FTP connections."""

    eleza __init__(self, user, passwd, host, port, dirs, timeout=None,
                 persistent=True):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.dirs = dirs
        self.timeout = timeout
        self.refcount = 0
        self.keepalive = persistent
        try:
            self.init()
        except:
            self.close()
            raise

    eleza init(self):
        agiza ftplib
        self.busy = 0
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port, self.timeout)
        self.ftp.login(self.user, self.passwd)
        _target = '/'.join(self.dirs)
        self.ftp.cwd(_target)

    eleza retrfile(self, file, type):
        agiza ftplib
        self.endtransfer()
        ikiwa type in ('d', 'D'): cmd = 'TYPE A'; isdir = 1
        else: cmd = 'TYPE ' + type; isdir = 0
        try:
            self.ftp.voidcmd(cmd)
        except ftplib.all_errors:
            self.init()
            self.ftp.voidcmd(cmd)
        conn = None
        ikiwa file and not isdir:
            # Try to retrieve as a file
            try:
                cmd = 'RETR ' + file
                conn, retrlen = self.ftp.ntransfercmd(cmd)
            except ftplib.error_perm as reason:
                ikiwa str(reason)[:3] != '550':
                    raise URLError('ftp error: %r' % reason).with_traceback(
                        sys.exc_info()[2])
        ikiwa not conn:
            # Set transfer mode to ASCII!
            self.ftp.voidcmd('TYPE A')
            # Try a directory listing. Verify that directory exists.
            ikiwa file:
                pwd = self.ftp.pwd()
                try:
                    try:
                        self.ftp.cwd(file)
                    except ftplib.error_perm as reason:
                        raise URLError('ftp error: %r' % reason) kutoka reason
                finally:
                    self.ftp.cwd(pwd)
                cmd = 'LIST ' + file
            else:
                cmd = 'LIST'
            conn, retrlen = self.ftp.ntransfercmd(cmd)
        self.busy = 1

        ftpobj = addclosehook(conn.makefile('rb'), self.file_close)
        self.refcount += 1
        conn.close()
        # Pass back both a suitably decorated object and a retrieval length
        rudisha (ftpobj, retrlen)

    eleza endtransfer(self):
        self.busy = 0

    eleza close(self):
        self.keepalive = False
        ikiwa self.refcount <= 0:
            self.real_close()

    eleza file_close(self):
        self.endtransfer()
        self.refcount -= 1
        ikiwa self.refcount <= 0 and not self.keepalive:
            self.real_close()

    eleza real_close(self):
        self.endtransfer()
        try:
            self.ftp.close()
        except ftperrors():
            pass

# Proxy handling
eleza getproxies_environment():
    """Return a dictionary of scheme -> proxy server URL mappings.

    Scan the environment for variables named <scheme>_proxy;
    this seems to be the standard convention.  If you need a
    different way, you can pass a proxies dictionary to the
    [Fancy]URLopener constructor.

    """
    proxies = {}
    # in order to prefer lowercase variables, process environment in
    # two passes: first matches any, second pass matches lowercase only
    for name, value in os.environ.items():
        name = name.lower()
        ikiwa value and name[-6:] == '_proxy':
            proxies[name[:-6]] = value
    # CVE-2016-1000110 - If we are running as CGI script, forget HTTP_PROXY
    # (non-all-lowercase) as it may be set kutoka the web server by a "Proxy:"
    # header kutoka the client
    # If "proxy" is lowercase, it will still be used thanks to the next block
    ikiwa 'REQUEST_METHOD' in os.environ:
        proxies.pop('http', None)
    for name, value in os.environ.items():
        ikiwa name[-6:] == '_proxy':
            name = name.lower()
            ikiwa value:
                proxies[name[:-6]] = value
            else:
                proxies.pop(name[:-6], None)
    rudisha proxies

eleza proxy_bypass_environment(host, proxies=None):
    """Test ikiwa proxies should not be used for a particular host.

    Checks the proxy dict for the value of no_proxy, which should
    be a list of comma separated DNS suffixes, or '*' for all hosts.

    """
    ikiwa proxies is None:
        proxies = getproxies_environment()
    # don't bypass, ikiwa no_proxy isn't specified
    try:
        no_proxy = proxies['no']
    except KeyError:
        rudisha 0
    # '*' is special case for always bypass
    ikiwa no_proxy == '*':
        rudisha 1
    # strip port off host
    hostonly, port = _splitport(host)
    # check ikiwa the host ends with any of the DNS suffixes
    no_proxy_list = [proxy.strip() for proxy in no_proxy.split(',')]
    for name in no_proxy_list:
        ikiwa name:
            name = name.lstrip('.')  # ignore leading dots
            name = re.escape(name)
            pattern = r'(.+\.)?%s$' % name
            ikiwa (re.match(pattern, hostonly, re.I)
                    or re.match(pattern, host, re.I)):
                rudisha 1
    # otherwise, don't bypass
    rudisha 0


# This code tests an OSX specific data structure but is testable on all
# platforms
eleza _proxy_bypass_macosx_sysconf(host, proxy_settings):
    """
    Return True iff this host shouldn't be accessed using a proxy

    This function uses the MacOSX framework SystemConfiguration
    to fetch the proxy information.

    proxy_settings come kutoka _scproxy._get_proxy_settings or get mocked ie:
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

    # Check for simple host names:
    ikiwa '.' not in host:
        ikiwa proxy_settings['exclude_simple']:
            rudisha True

    hostIP = None

    for value in proxy_settings.get('exceptions', ()):
        # Items in the list are strings like these: *.local, 169.254/16
        ikiwa not value: continue

        m = re.match(r"(\d+(?:\.\d+)*)(/\d+)?", value)
        ikiwa m is not None:
            ikiwa hostIP is None:
                try:
                    hostIP = socket.gethostbyname(hostonly)
                    hostIP = ip2num(hostIP)
                except OSError:
                    continue

            base = ip2num(m.group(1))
            mask = m.group(2)
            ikiwa mask is None:
                mask = 8 * (m.group(1).count('.') + 1)
            else:
                mask = int(mask[1:])
            mask = 32 - mask

            ikiwa (hostIP >> mask) == (base >> mask):
                rudisha True

        elikiwa fnmatch(host, value):
            rudisha True

    rudisha False


ikiwa sys.platform == 'darwin':
    kutoka _scproxy agiza _get_proxy_settings, _get_proxies

    eleza proxy_bypass_macosx_sysconf(host):
        proxy_settings = _get_proxy_settings()
        rudisha _proxy_bypass_macosx_sysconf(host, proxy_settings)

    eleza getproxies_macosx_sysconf():
        """Return a dictionary of scheme -> proxy server URL mappings.

        This function uses the MacOSX framework SystemConfiguration
        to fetch the proxy information.
        """
        rudisha _get_proxies()



    eleza proxy_bypass(host):
        """Return True, ikiwa host should be bypassed.

        Checks proxy settings gathered kutoka the environment, ikiwa specified,
        or kutoka the MacOSX framework SystemConfiguration.

        """
        proxies = getproxies_environment()
        ikiwa proxies:
            rudisha proxy_bypass_environment(host, proxies)
        else:
            rudisha proxy_bypass_macosx_sysconf(host)

    eleza getproxies():
        rudisha getproxies_environment() or getproxies_macosx_sysconf()


elikiwa os.name == 'nt':
    eleza getproxies_registry():
        """Return a dictionary of scheme -> proxy server URL mappings.

        Win32 uses the registry to store proxies.

        """
        proxies = {}
        try:
            agiza winreg
        except ImportError:
            # Std module, so should be around - but you never know!
            rudisha proxies
        try:
            internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
            proxyEnable = winreg.QueryValueEx(internetSettings,
                                               'ProxyEnable')[0]
            ikiwa proxyEnable:
                # Returned as Unicode but problems ikiwa not converted to ASCII
                proxyServer = str(winreg.QueryValueEx(internetSettings,
                                                       'ProxyServer')[0])
                ikiwa '=' in proxyServer:
                    # Per-protocol settings
                    for p in proxyServer.split(';'):
                        protocol, address = p.split('=', 1)
                        # See ikiwa address has a type:// prefix
                        ikiwa not re.match('^([^/:]+)://', address):
                            address = '%s://%s' % (protocol, address)
                        proxies[protocol] = address
                else:
                    # Use one setting for all protocols
                    ikiwa proxyServer[:5] == 'http:':
                        proxies['http'] = proxyServer
                    else:
                        proxies['http'] = 'http://%s' % proxyServer
                        proxies['https'] = 'https://%s' % proxyServer
                        proxies['ftp'] = 'ftp://%s' % proxyServer
            internetSettings.Close()
        except (OSError, ValueError, TypeError):
            # Either registry key not found etc, or the value in an
            # unexpected format.
            # proxies already set up to be empty so nothing to do
            pass
        rudisha proxies

    eleza getproxies():
        """Return a dictionary of scheme -> proxy server URL mappings.

        Returns settings gathered kutoka the environment, ikiwa specified,
        or the registry.

        """
        rudisha getproxies_environment() or getproxies_registry()

    eleza proxy_bypass_registry(host):
        try:
            agiza winreg
        except ImportError:
            # Std modules, so should be around - but you never know!
            rudisha 0
        try:
            internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
            proxyEnable = winreg.QueryValueEx(internetSettings,
                                               'ProxyEnable')[0]
            proxyOverride = str(winreg.QueryValueEx(internetSettings,
                                                     'ProxyOverride')[0])
            # ^^^^ Returned as Unicode but problems ikiwa not converted to ASCII
        except OSError:
            rudisha 0
        ikiwa not proxyEnable or not proxyOverride:
            rudisha 0
        # try to make a host list kutoka name and IP address.
        rawHost, port = _splitport(host)
        host = [rawHost]
        try:
            addr = socket.gethostbyname(rawHost)
            ikiwa addr != rawHost:
                host.append(addr)
        except OSError:
            pass
        try:
            fqdn = socket.getfqdn(rawHost)
            ikiwa fqdn != rawHost:
                host.append(fqdn)
        except OSError:
            pass
        # make a check value list kutoka the registry entry: replace the
        # '<local>' string by the localhost entry and the corresponding
        # canonical entry.
        proxyOverride = proxyOverride.split(';')
        # now check ikiwa we match one of the registry values.
        for test in proxyOverride:
            ikiwa test == '<local>':
                ikiwa '.' not in rawHost:
                    rudisha 1
            test = test.replace(".", r"\.")     # mask dots
            test = test.replace("*", r".*")     # change glob sequence
            test = test.replace("?", r".")      # change glob char
            for val in host:
                ikiwa re.match(test, val, re.I):
                    rudisha 1
        rudisha 0

    eleza proxy_bypass(host):
        """Return True, ikiwa host should be bypassed.

        Checks proxy settings gathered kutoka the environment, ikiwa specified,
        or the registry.

        """
        proxies = getproxies_environment()
        ikiwa proxies:
            rudisha proxy_bypass_environment(host, proxies)
        else:
            rudisha proxy_bypass_registry(host)

else:
    # By default use environment variables
    getproxies = getproxies_environment
    proxy_bypass = proxy_bypass_environment
