agiza unittest
kutoka test agiza support
kutoka test agiza test_urllib

agiza os
agiza io
agiza socket
agiza array
agiza sys
agiza tempfile
agiza subprocess

agiza urllib.request
# The proxy bypita method imported below has logic specific to the OSX
# proxy config data structure but ni testable on all platforms.
kutoka urllib.request agiza (Request, OpenerDirector, HTTPBasicAuthHandler,
                            HTTPPasswordMgrWithPriorAuth, _parse_proxy,
                            _proxy_bypita_macosx_sysconf,
                            AbstractDigestAuthHandler)
kutoka urllib.parse agiza urlparse
agiza urllib.error
agiza http.client

# XXX
# Request
# CacheFTPHandler (hard to write)
# parse_keqv_list, parse_http_list, HTTPDigestAuthHandler


kundi TrivialTests(unittest.TestCase):

    eleza test___all__(self):
        # Verify which names are exposed
        kila module kwenye 'request', 'response', 'parse', 'error', 'robotparser':
            context = {}
            exec('kutoka urllib.%s agiza *' % module, context)
            toa context['__builtins__']
            ikiwa module == 'request' na os.name == 'nt':
                u, p = context.pop('url2pathname'), context.pop('pathname2url')
                self.assertEqual(u.__module__, 'nturl2path')
                self.assertEqual(p.__module__, 'nturl2path')
            kila k, v kwenye context.items():
                self.assertEqual(v.__module__, 'urllib.%s' % module,
                    "%r ni exposed kwenye 'urllib.%s' but defined kwenye %r" %
                    (k, module, v.__module__))

    eleza test_trivial(self):
        # A couple trivial tests

        self.assertRaises(ValueError, urllib.request.urlopen, 'bogus url')

        # XXX Name hacking to get this to work on Windows.
        fname = os.path.abspath(urllib.request.__file__).replace(os.sep, '/')

        ikiwa os.name == 'nt':
            file_url = "file:///%s" % fname
        isipokua:
            file_url = "file://%s" % fname

        ukijumuisha urllib.request.urlopen(file_url) kama f:
            f.read()

    eleza test_parse_http_list(self):
        tests = [
            ('a,b,c', ['a', 'b', 'c']),
            ('path"o,l"og"i"cal, example', ['path"o,l"og"i"cal', 'example']),
            ('a, b, "c", "d", "e,f", g, h',
             ['a', 'b', '"c"', '"d"', '"e,f"', 'g', 'h']),
            ('a="b\\"c", d="e\\,f", g="h\\\\i"',
             ['a="b"c"', 'd="e,f"', 'g="h\\i"'])]
        kila string, list kwenye tests:
            self.assertEqual(urllib.request.parse_http_list(string), list)

    eleza test_URLError_reasonstr(self):
        err = urllib.error.URLError('reason')
        self.assertIn(err.reason, str(err))


kundi RequestHdrsTests(unittest.TestCase):

    eleza test_request_headers_dict(self):
        """
        The Request.headers dictionary ni sio a documented interface.  It
        should stay that way, because the complete set of headers are only
        accessible through the .get_header(), .has_header(), .header_items()
        interface.  However, .headers pre-dates those methods, na so real code
        will be using the dictionary.

        The introduction kwenye 2.4 of those methods was a mistake kila the same
        reason: code that previously saw all (urllib2 user)-provided headers kwenye
        .headers now sees only a subset.

        """
        url = "http://example.com"
        self.assertEqual(Request(url,
                                 headers={"Spam-eggs": "blah"}
                                 ).headers["Spam-eggs"], "blah")
        self.assertEqual(Request(url,
                                 headers={"spam-EggS": "blah"}
                                 ).headers["Spam-eggs"], "blah")

    eleza test_request_headers_methods(self):
        """
        Note the case normalization of header names here, to
        .capitalize()-case.  This should be preserved for
        backwards-compatibility.  (In the HTTP case, normalization to
        .title()-case ni done by urllib2 before sending headers to
        http.client).

        Note that e.g. r.has_header("spam-EggS") ni currently Uongo, na
        r.get_header("spam-EggS") returns Tupu, but that could be changed kwenye
        future.

        Method r.remove_header should remove items both kutoka r.headers na
        r.unredirected_hdrs dictionaries
        """
        url = "http://example.com"
        req = Request(url, headers={"Spam-eggs": "blah"})
        self.assertKweli(req.has_header("Spam-eggs"))
        self.assertEqual(req.header_items(), [('Spam-eggs', 'blah')])

        req.add_header("Foo-Bar", "baz")
        self.assertEqual(sorted(req.header_items()),
                         [('Foo-bar', 'baz'), ('Spam-eggs', 'blah')])
        self.assertUongo(req.has_header("Not-there"))
        self.assertIsTupu(req.get_header("Not-there"))
        self.assertEqual(req.get_header("Not-there", "default"), "default")

        req.remove_header("Spam-eggs")
        self.assertUongo(req.has_header("Spam-eggs"))

        req.add_unredirected_header("Unredirected-spam", "Eggs")
        self.assertKweli(req.has_header("Unredirected-spam"))

        req.remove_header("Unredirected-spam")
        self.assertUongo(req.has_header("Unredirected-spam"))

    eleza test_pitaword_manager(self):
        mgr = urllib.request.HTTPPasswordMgr()
        add = mgr.add_pitaword
        find_user_pita = mgr.find_user_pitaword

        add("Some Realm", "http://example.com/", "joe", "pitaword")
        add("Some Realm", "http://example.com/ni", "ni", "ni")
        add("Some Realm", "http://c.example.com:3128", "3", "c")
        add("Some Realm", "d.example.com", "4", "d")
        add("Some Realm", "e.example.com:3128", "5", "e")

        # For the same realm, pitaword set the highest path ni the winner.
        self.assertEqual(find_user_pita("Some Realm", "example.com"),
                         ('joe', 'pitaword'))
        self.assertEqual(find_user_pita("Some Realm", "http://example.com/ni"),
                         ('joe', 'pitaword'))
        self.assertEqual(find_user_pita("Some Realm", "http://example.com"),
                         ('joe', 'pitaword'))
        self.assertEqual(find_user_pita("Some Realm", "http://example.com/"),
                         ('joe', 'pitaword'))
        self.assertEqual(find_user_pita("Some Realm",
                                        "http://example.com/spam"),
                         ('joe', 'pitaword'))

        self.assertEqual(find_user_pita("Some Realm",
                                        "http://example.com/spam/spam"),
                         ('joe', 'pitaword'))

        # You can have different pitawords kila different paths.

        add("c", "http://example.com/foo", "foo", "ni")
        add("c", "http://example.com/bar", "bar", "nini")

        self.assertEqual(find_user_pita("c", "http://example.com/foo"),
                         ('foo', 'ni'))

        self.assertEqual(find_user_pita("c", "http://example.com/bar"),
                         ('bar', 'nini'))

        # For the same path, newer pitaword should be considered.

        add("b", "http://example.com/", "first", "blah")
        add("b", "http://example.com/", "second", "spam")

        self.assertEqual(find_user_pita("b", "http://example.com/"),
                         ('second', 'spam'))

        # No special relationship between a.example.com na example.com:

        add("a", "http://example.com", "1", "a")
        self.assertEqual(find_user_pita("a", "http://example.com/"),
                         ('1', 'a'))

        self.assertEqual(find_user_pita("a", "http://a.example.com/"),
                         (Tupu, Tupu))

        # Ports:

        self.assertEqual(find_user_pita("Some Realm", "c.example.com"),
                         (Tupu, Tupu))
        self.assertEqual(find_user_pita("Some Realm", "c.example.com:3128"),
                         ('3', 'c'))
        self.assertEqual(
            find_user_pita("Some Realm", "http://c.example.com:3128"),
            ('3', 'c'))
        self.assertEqual(find_user_pita("Some Realm", "d.example.com"),
                         ('4', 'd'))
        self.assertEqual(find_user_pita("Some Realm", "e.example.com:3128"),
                         ('5', 'e'))

    eleza test_pitaword_manager_default_port(self):
        """
        The point to note here ni that we can't guess the default port if
        there's no scheme.  This applies to both add_pitaword na
        find_user_pitaword.
        """
        mgr = urllib.request.HTTPPasswordMgr()
        add = mgr.add_pitaword
        find_user_pita = mgr.find_user_pitaword
        add("f", "http://g.example.com:80", "10", "j")
        add("g", "http://h.example.com", "11", "k")
        add("h", "i.example.com:80", "12", "l")
        add("i", "j.example.com", "13", "m")
        self.assertEqual(find_user_pita("f", "g.example.com:100"),
                         (Tupu, Tupu))
        self.assertEqual(find_user_pita("f", "g.example.com:80"),
                         ('10', 'j'))
        self.assertEqual(find_user_pita("f", "g.example.com"),
                         (Tupu, Tupu))
        self.assertEqual(find_user_pita("f", "http://g.example.com:100"),
                         (Tupu, Tupu))
        self.assertEqual(find_user_pita("f", "http://g.example.com:80"),
                         ('10', 'j'))
        self.assertEqual(find_user_pita("f", "http://g.example.com"),
                         ('10', 'j'))
        self.assertEqual(find_user_pita("g", "h.example.com"), ('11', 'k'))
        self.assertEqual(find_user_pita("g", "h.example.com:80"), ('11', 'k'))
        self.assertEqual(find_user_pita("g", "http://h.example.com:80"),
                         ('11', 'k'))
        self.assertEqual(find_user_pita("h", "i.example.com"), (Tupu, Tupu))
        self.assertEqual(find_user_pita("h", "i.example.com:80"), ('12', 'l'))
        self.assertEqual(find_user_pita("h", "http://i.example.com:80"),
                         ('12', 'l'))
        self.assertEqual(find_user_pita("i", "j.example.com"), ('13', 'm'))
        self.assertEqual(find_user_pita("i", "j.example.com:80"),
                         (Tupu, Tupu))
        self.assertEqual(find_user_pita("i", "http://j.example.com"),
                         ('13', 'm'))
        self.assertEqual(find_user_pita("i", "http://j.example.com:80"),
                         (Tupu, Tupu))


kundi MockOpener:
    addheaders = []

    eleza open(self, req, data=Tupu, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.req, self.data, self.timeout = req, data, timeout

    eleza error(self, proto, *args):
        self.proto, self.args = proto, args


kundi MockFile:
    eleza read(self, count=Tupu):
        pita

    eleza readline(self, count=Tupu):
        pita

    eleza close(self):
        pita


kundi MockHeaders(dict):
    eleza getheaders(self, name):
        rudisha list(self.values())


kundi MockResponse(io.StringIO):
    eleza __init__(self, code, msg, headers, data, url=Tupu):
        io.StringIO.__init__(self, data)
        self.code, self.msg, self.headers, self.url = code, msg, headers, url

    eleza info(self):
        rudisha self.headers

    eleza geturl(self):
        rudisha self.url


kundi MockCookieJar:
    eleza add_cookie_header(self, request):
        self.ach_req = request

    eleza extract_cookies(self, response, request):
        self.ec_req, self.ec_r = request, response


kundi FakeMethod:
    eleza __init__(self, meth_name, action, handle):
        self.meth_name = meth_name
        self.handle = handle
        self.action = action

    eleza __call__(self, *args):
        rudisha self.handle(self.meth_name, self.action, *args)


kundi MockHTTPResponse(io.IOBase):
    eleza __init__(self, fp, msg, status, reason):
        self.fp = fp
        self.msg = msg
        self.status = status
        self.reason = reason
        self.code = 200

    eleza read(self):
        rudisha ''

    eleza info(self):
        rudisha {}

    eleza geturl(self):
        rudisha self.url


kundi MockHTTPClass:
    eleza __init__(self):
        self.level = 0
        self.req_headers = []
        self.data = Tupu
        self.raise_on_endheaders = Uongo
        self.sock = Tupu
        self._tunnel_headers = {}

    eleza __call__(self, host, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host
        self.timeout = timeout
        rudisha self

    eleza set_debuglevel(self, level):
        self.level = level

    eleza set_tunnel(self, host, port=Tupu, headers=Tupu):
        self._tunnel_host = host
        self._tunnel_port = port
        ikiwa headers:
            self._tunnel_headers = headers
        isipokua:
            self._tunnel_headers.clear()

    eleza request(self, method, url, body=Tupu, headers=Tupu, *,
                encode_chunked=Uongo):
        self.method = method
        self.selector = url
        ikiwa headers ni sio Tupu:
            self.req_headers += headers.items()
        self.req_headers.sort()
        ikiwa body:
            self.data = body
        self.encode_chunked = encode_chunked
        ikiwa self.raise_on_endheaders:
            ashiria OSError()

    eleza getresponse(self):
        rudisha MockHTTPResponse(MockFile(), {}, 200, "OK")

    eleza close(self):
        pita


kundi MockHandler:
    # useful kila testing handler machinery
    # see add_ordered_mock_handlers() docstring
    handler_order = 500

    eleza __init__(self, methods):
        self._define_methods(methods)

    eleza _define_methods(self, methods):
        kila spec kwenye methods:
            ikiwa len(spec) == 2:
                name, action = spec
            isipokua:
                name, action = spec, Tupu
            meth = FakeMethod(name, action, self.handle)
            setattr(self.__class__, name, meth)

    eleza handle(self, fn_name, action, *args, **kwds):
        self.parent.calls.append((self, fn_name, args, kwds))
        ikiwa action ni Tupu:
            rudisha Tupu
        lasivyo action == "rudisha self":
            rudisha self
        lasivyo action == "rudisha response":
            res = MockResponse(200, "OK", {}, "")
            rudisha res
        lasivyo action == "rudisha request":
            rudisha Request("http://blah/")
        lasivyo action.startswith("error"):
            code = action[action.rfind(" ")+1:]
            jaribu:
                code = int(code)
            tatizo ValueError:
                pita
            res = MockResponse(200, "OK", {}, "")
            rudisha self.parent.error("http", args[0], res, code, "", {})
        lasivyo action == "raise":
            ashiria urllib.error.URLError("blah")
        assert Uongo

    eleza close(self):
        pita

    eleza add_parent(self, parent):
        self.parent = parent
        self.parent.calls = []

    eleza __lt__(self, other):
        ikiwa sio hasattr(other, "handler_order"):
            # No handler_order, leave kwenye original order.  Yuck.
            rudisha Kweli
        rudisha self.handler_order < other.handler_order


eleza add_ordered_mock_handlers(opener, meth_spec):
    """Create MockHandlers na add them to an OpenerDirector.

    meth_spec: list of lists of tuples na strings defining methods to define
    on handlers.  eg:

    [["http_error", "ftp_open"], ["http_open"]]

    defines methods .http_error() na .ftp_open() on one handler, na
    .http_open() on another.  These methods just record their arguments na
    rudisha Tupu.  Using a tuple instead of a string causes the method to
    perform some action (see MockHandler.handle()), eg:

    [["http_error"], [("http_open", "rudisha request")]]

    defines .http_error() on one handler (which simply returns Tupu), na
    .http_open() on another handler, which returns a Request object.

    """
    handlers = []
    count = 0
    kila meths kwenye meth_spec:
        kundi MockHandlerSubclass(MockHandler):
            pita

        h = MockHandlerSubclass(meths)
        h.handler_order += count
        h.add_parent(opener)
        count = count + 1
        handlers.append(h)
        opener.add_handler(h)
    rudisha handlers


eleza build_test_opener(*handler_instances):
    opener = OpenerDirector()
    kila h kwenye handler_instances:
        opener.add_handler(h)
    rudisha opener


kundi MockHTTPHandler(urllib.request.BaseHandler):
    # useful kila testing redirections na auth
    # sends supplied headers na code kama first response
    # sends 200 OK kama second response
    eleza __init__(self, code, headers):
        self.code = code
        self.headers = headers
        self.reset()

    eleza reset(self):
        self._count = 0
        self.requests = []

    eleza http_open(self, req):
        agiza email, copy
        self.requests.append(copy.deepcopy(req))
        ikiwa self._count == 0:
            self._count = self._count + 1
            name = http.client.responses[self.code]
            msg = email.message_from_string(self.headers)
            rudisha self.parent.error(
                "http", req, MockFile(), self.code, name, msg)
        isipokua:
            self.req = req
            msg = email.message_from_string("\r\n\r\n")
            rudisha MockResponse(200, "OK", msg, "", req.get_full_url())


kundi MockHTTPSHandler(urllib.request.AbstractHTTPHandler):
    # Useful kila testing the Proxy-Authorization request by verifying the
    # properties of httpcon

    eleza __init__(self, debuglevel=0):
        urllib.request.AbstractHTTPHandler.__init__(self, debuglevel=debuglevel)
        self.httpconn = MockHTTPClass()

    eleza https_open(self, req):
        rudisha self.do_open(self.httpconn, req)


kundi MockHTTPHandlerCheckAuth(urllib.request.BaseHandler):
    # useful kila testing auth
    # sends supplied code response
    # checks ikiwa auth header ni specified kwenye request
    eleza __init__(self, code):
        self.code = code
        self.has_auth_header = Uongo

    eleza reset(self):
        self.has_auth_header = Uongo

    eleza http_open(self, req):
        ikiwa req.has_header('Authorization'):
            self.has_auth_header = Kweli
        name = http.client.responses[self.code]
        rudisha MockResponse(self.code, name, MockFile(), "", req.get_full_url())



kundi MockPasswordManager:
    eleza add_pitaword(self, realm, uri, user, pitaword):
        self.realm = realm
        self.url = uri
        self.user = user
        self.pitaword = pitaword

    eleza find_user_pitaword(self, realm, authuri):
        self.target_realm = realm
        self.target_url = authuri
        rudisha self.user, self.pitaword


kundi OpenerDirectorTests(unittest.TestCase):

    eleza test_add_non_handler(self):
        kundi NonHandler(object):
            pita
        self.assertRaises(TypeError,
                          OpenerDirector().add_handler, NonHandler())

    eleza test_badly_named_methods(self):
        # test work-around kila three methods that accidentally follow the
        # naming conventions kila handler methods
        # (*_open() / *_request() / *_response())

        # These used to call the accidentally-named methods, causing a
        # TypeError kwenye real code; here, returning self kutoka these mock
        # methods would either cause no exception, ama AttributeError.

        kutoka urllib.error agiza URLError

        o = OpenerDirector()
        meth_spec = [
            [("do_open", "rudisha self"), ("proxy_open", "rudisha self")],
            [("redirect_request", "rudisha self")],
            ]
        add_ordered_mock_handlers(o, meth_spec)
        o.add_handler(urllib.request.UnknownHandler())
        kila scheme kwenye "do", "proxy", "redirect":
            self.assertRaises(URLError, o.open, scheme+"://example.com/")

    eleza test_handled(self):
        # handler returning non-Tupu means no more handlers will be called
        o = OpenerDirector()
        meth_spec = [
            ["http_open", "ftp_open", "http_error_302"],
            ["ftp_open"],
            [("http_open", "rudisha self")],
            [("http_open", "rudisha self")],
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        req = Request("http://example.com/")
        r = o.open(req)
        # Second .http_open() gets called, third doesn't, since second returned
        # non-Tupu.  Handlers without .http_open() never get any methods called
        # on them.
        # In fact, second mock handler defining .http_open() returns self
        # (instead of response), which becomes the OpenerDirector's rudisha
        # value.
        self.assertEqual(r, handlers[2])
        calls = [(handlers[0], "http_open"), (handlers[2], "http_open")]
        kila expected, got kwenye zip(calls, o.calls):
            handler, name, args, kwds = got
            self.assertEqual((handler, name), expected)
            self.assertEqual(args, (req,))

    eleza test_handler_order(self):
        o = OpenerDirector()
        handlers = []
        kila meths, handler_order kwenye [([("http_open", "rudisha self")], 500),
                                     (["http_open"], 0)]:
            kundi MockHandlerSubclass(MockHandler):
                pita

            h = MockHandlerSubclass(meths)
            h.handler_order = handler_order
            handlers.append(h)
            o.add_handler(h)

        o.open("http://example.com/")
        # handlers called kwenye reverse order, thanks to their sort order
        self.assertEqual(o.calls[0][0], handlers[1])
        self.assertEqual(o.calls[1][0], handlers[0])

    eleza test_raise(self):
        # raising URLError stops processing of request
        o = OpenerDirector()
        meth_spec = [
            [("http_open", "raise")],
            [("http_open", "rudisha self")],
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        req = Request("http://example.com/")
        self.assertRaises(urllib.error.URLError, o.open, req)
        self.assertEqual(o.calls, [(handlers[0], "http_open", (req,), {})])

    eleza test_http_error(self):
        # XXX http_error_default
        # http errors are a special case
        o = OpenerDirector()
        meth_spec = [
            [("http_open", "error 302")],
            [("http_error_400", "raise"), "http_open"],
            [("http_error_302", "rudisha response"), "http_error_303",
             "http_error"],
            [("http_error_302")],
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        kundi Unknown:
            eleza __eq__(self, other):
                rudisha Kweli

        req = Request("http://example.com/")
        o.open(req)
        assert len(o.calls) == 2
        calls = [(handlers[0], "http_open", (req,)),
                 (handlers[2], "http_error_302",
                  (req, Unknown(), 302, "", {}))]
        kila expected, got kwenye zip(calls, o.calls):
            handler, method_name, args = expected
            self.assertEqual((handler, method_name), got[:2])
            self.assertEqual(args, got[2])

    eleza test_processors(self):
        # *_request / *_response methods get called appropriately
        o = OpenerDirector()
        meth_spec = [
            [("http_request", "rudisha request"),
             ("http_response", "rudisha response")],
            [("http_request", "rudisha request"),
             ("http_response", "rudisha response")],
            ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        req = Request("http://example.com/")
        o.open(req)
        # processor methods are called on *all* handlers that define them,
        # sio just the first handler that handles the request
        calls = [
            (handlers[0], "http_request"), (handlers[1], "http_request"),
            (handlers[0], "http_response"), (handlers[1], "http_response")]

        kila i, (handler, name, args, kwds) kwenye enumerate(o.calls):
            ikiwa i < 2:
                # *_request
                self.assertEqual((handler, name), calls[i])
                self.assertEqual(len(args), 1)
                self.assertIsInstance(args[0], Request)
            isipokua:
                # *_response
                self.assertEqual((handler, name), calls[i])
                self.assertEqual(len(args), 2)
                self.assertIsInstance(args[0], Request)
                # response kutoka opener.open ni Tupu, because there's no
                # handler that defines http_open to handle it
                ikiwa args[1] ni sio Tupu:
                    self.assertIsInstance(args[1], MockResponse)


eleza sanepathname2url(path):
    jaribu:
        path.encode("utf-8")
    tatizo UnicodeEncodeError:
        ashiria unittest.SkipTest("path ni sio encodable to utf8")
    urlpath = urllib.request.pathname2url(path)
    ikiwa os.name == "nt" na urlpath.startswith("///"):
        urlpath = urlpath[2:]
    # XXX don't ask me about the mac...
    rudisha urlpath


kundi HandlerTests(unittest.TestCase):

    eleza test_ftp(self):
        kundi MockFTPWrapper:
            eleza __init__(self, data):
                self.data = data

            eleza retrfile(self, filename, filetype):
                self.filename, self.filetype = filename, filetype
                rudisha io.StringIO(self.data), len(self.data)

            eleza close(self):
                pita

        kundi NullFTPHandler(urllib.request.FTPHandler):
            eleza __init__(self, data):
                self.data = data

            eleza connect_ftp(self, user, pitawd, host, port, dirs,
                            timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
                self.user, self.pitawd = user, pitawd
                self.host, self.port = host, port
                self.dirs = dirs
                self.ftpwrapper = MockFTPWrapper(self.data)
                rudisha self.ftpwrapper

        agiza ftplib
        data = "rheum rhaponicum"
        h = NullFTPHandler(data)
        h.parent = MockOpener()

        kila url, host, port, user, pitawd, type_, dirs, filename, mimetype kwenye [
            ("ftp://localhost/foo/bar/baz.html",
             "localhost", ftplib.FTP_PORT, "", "", "I",
             ["foo", "bar"], "baz.html", "text/html"),
            ("ftp://parrot@localhost/foo/bar/baz.html",
             "localhost", ftplib.FTP_PORT, "parrot", "", "I",
             ["foo", "bar"], "baz.html", "text/html"),
            ("ftp://%25parrot@localhost/foo/bar/baz.html",
             "localhost", ftplib.FTP_PORT, "%parrot", "", "I",
             ["foo", "bar"], "baz.html", "text/html"),
            ("ftp://%2542parrot@localhost/foo/bar/baz.html",
             "localhost", ftplib.FTP_PORT, "%42parrot", "", "I",
             ["foo", "bar"], "baz.html", "text/html"),
            ("ftp://localhost:80/foo/bar/",
             "localhost", 80, "", "", "D",
             ["foo", "bar"], "", Tupu),
            ("ftp://localhost/baz.gif;type=a",
             "localhost", ftplib.FTP_PORT, "", "", "A",
             [], "baz.gif", Tupu),  # XXX really this should guess image/gif
            ]:
            req = Request(url)
            req.timeout = Tupu
            r = h.ftp_open(req)
            # ftp authentication sio yet implemented by FTPHandler
            self.assertEqual(h.user, user)
            self.assertEqual(h.pitawd, pitawd)
            self.assertEqual(h.host, socket.gethostbyname(host))
            self.assertEqual(h.port, port)
            self.assertEqual(h.dirs, dirs)
            self.assertEqual(h.ftpwrapper.filename, filename)
            self.assertEqual(h.ftpwrapper.filetype, type_)
            headers = r.info()
            self.assertEqual(headers.get("Content-type"), mimetype)
            self.assertEqual(int(headers["Content-length"]), len(data))

    eleza test_file(self):
        agiza email.utils
        h = urllib.request.FileHandler()
        o = h.parent = MockOpener()

        TESTFN = support.TESTFN
        urlpath = sanepathname2url(os.path.abspath(TESTFN))
        towrite = b"hello, world\n"
        urls = [
            "file://localhost%s" % urlpath,
            "file://%s" % urlpath,
            "file://%s%s" % (socket.gethostbyname('localhost'), urlpath),
            ]
        jaribu:
            localaddr = socket.gethostbyname(socket.gethostname())
        tatizo socket.gaierror:
            localaddr = ''
        ikiwa localaddr:
            urls.append("file://%s%s" % (localaddr, urlpath))

        kila url kwenye urls:
            f = open(TESTFN, "wb")
            jaribu:
                jaribu:
                    f.write(towrite)
                mwishowe:
                    f.close()

                r = h.file_open(Request(url))
                jaribu:
                    data = r.read()
                    headers = r.info()
                    respurl = r.geturl()
                mwishowe:
                    r.close()
                stats = os.stat(TESTFN)
                modified = email.utils.formatdate(stats.st_mtime, usegmt=Kweli)
            mwishowe:
                os.remove(TESTFN)
            self.assertEqual(data, towrite)
            self.assertEqual(headers["Content-type"], "text/plain")
            self.assertEqual(headers["Content-length"], "13")
            self.assertEqual(headers["Last-modified"], modified)
            self.assertEqual(respurl, url)

        kila url kwenye [
            "file://localhost:80%s" % urlpath,
            "file:///file_does_not_exist.txt",
            "file://not-a-local-host.com//dir/file.txt",
            "file://%s:80%s/%s" % (socket.gethostbyname('localhost'),
                                   os.getcwd(), TESTFN),
            "file://somerandomhost.ontheinternet.com%s/%s" %
            (os.getcwd(), TESTFN),
            ]:
            jaribu:
                f = open(TESTFN, "wb")
                jaribu:
                    f.write(towrite)
                mwishowe:
                    f.close()

                self.assertRaises(urllib.error.URLError,
                                  h.file_open, Request(url))
            mwishowe:
                os.remove(TESTFN)

        h = urllib.request.FileHandler()
        o = h.parent = MockOpener()
        # XXXX why does // mean ftp (and /// mean sio ftp!), na where
        #  ni file: scheme specified?  I think this ni really a bug, na
        #  what was intended was to distinguish between URLs like:
        # file:/blah.txt (a file)
        # file://localhost/blah.txt (a file)
        # file:///blah.txt (a file)
        # file://ftp.example.com/blah.txt (an ftp URL)
        kila url, ftp kwenye [
            ("file://ftp.example.com//foo.txt", Uongo),
            ("file://ftp.example.com///foo.txt", Uongo),
            ("file://ftp.example.com/foo.txt", Uongo),
            ("file://somehost//foo/something.txt", Uongo),
            ("file://localhost//foo/something.txt", Uongo),
            ]:
            req = Request(url)
            jaribu:
                h.file_open(req)
            tatizo urllib.error.URLError:
                self.assertUongo(ftp)
            isipokua:
                self.assertIs(o.req, req)
                self.assertEqual(req.type, "ftp")
            self.assertEqual(req.type == "ftp", ftp)

    eleza test_http(self):

        h = urllib.request.AbstractHTTPHandler()
        o = h.parent = MockOpener()

        url = "http://example.com/"
        kila method, data kwenye [("GET", Tupu), ("POST", b"blah")]:
            req = Request(url, data, {"Foo": "bar"})
            req.timeout = Tupu
            req.add_unredirected_header("Spam", "eggs")
            http = MockHTTPClass()
            r = h.do_open(http, req)

            # result attributes
            r.read; r.readline  # wrapped MockFile methods
            r.info; r.geturl  # addinfourl methods
            r.code, r.msg == 200, "OK"  # added kutoka MockHTTPClass.getreply()
            hdrs = r.info()
            hdrs.get; hdrs.__contains__  # r.info() gives dict kutoka .getreply()
            self.assertEqual(r.geturl(), url)

            self.assertEqual(http.host, "example.com")
            self.assertEqual(http.level, 0)
            self.assertEqual(http.method, method)
            self.assertEqual(http.selector, "/")
            self.assertEqual(http.req_headers,
                             [("Connection", "close"),
                              ("Foo", "bar"), ("Spam", "eggs")])
            self.assertEqual(http.data, data)

        # check OSError converted to URLError
        http.raise_on_endheaders = Kweli
        self.assertRaises(urllib.error.URLError, h.do_open, http, req)

        # Check kila TypeError on POST data which ni str.
        req = Request("http://example.com/","badpost")
        self.assertRaises(TypeError, h.do_request_, req)

        # check adding of standard headers
        o.addheaders = [("Spam", "eggs")]
        kila data kwenye b"", Tupu:  # POST, GET
            req = Request("http://example.com/", data)
            r = MockResponse(200, "OK", {}, "")
            newreq = h.do_request_(req)
            ikiwa data ni Tupu:  # GET
                self.assertNotIn("Content-length", req.unredirected_hdrs)
                self.assertNotIn("Content-type", req.unredirected_hdrs)
            isipokua:  # POST
                self.assertEqual(req.unredirected_hdrs["Content-length"], "0")
                self.assertEqual(req.unredirected_hdrs["Content-type"],
                             "application/x-www-form-urlencoded")
            # XXX the details of Host could be better tested
            self.assertEqual(req.unredirected_hdrs["Host"], "example.com")
            self.assertEqual(req.unredirected_hdrs["Spam"], "eggs")

            # don't clobber existing headers
            req.add_unredirected_header("Content-length", "foo")
            req.add_unredirected_header("Content-type", "bar")
            req.add_unredirected_header("Host", "baz")
            req.add_unredirected_header("Spam", "foo")
            newreq = h.do_request_(req)
            self.assertEqual(req.unredirected_hdrs["Content-length"], "foo")
            self.assertEqual(req.unredirected_hdrs["Content-type"], "bar")
            self.assertEqual(req.unredirected_hdrs["Host"], "baz")
            self.assertEqual(req.unredirected_hdrs["Spam"], "foo")

    eleza test_http_body_file(self):
        # A regular file - chunked encoding ni used unless Content Length is
        # already set.

        h = urllib.request.AbstractHTTPHandler()
        o = h.parent = MockOpener()

        file_obj = tempfile.NamedTemporaryFile(mode='w+b', delete=Uongo)
        file_path = file_obj.name
        file_obj.close()
        self.addCleanup(os.unlink, file_path)

        ukijumuisha open(file_path, "rb") kama f:
            req = Request("http://example.com/", f, {})
            newreq = h.do_request_(req)
            te = newreq.get_header('Transfer-encoding')
            self.assertEqual(te, "chunked")
            self.assertUongo(newreq.has_header('Content-length'))

        ukijumuisha open(file_path, "rb") kama f:
            req = Request("http://example.com/", f, {"Content-Length": 30})
            newreq = h.do_request_(req)
            self.assertEqual(int(newreq.get_header('Content-length')), 30)
            self.assertUongo(newreq.has_header("Transfer-encoding"))

    eleza test_http_body_fileobj(self):
        # A file object - chunked encoding ni used
        # unless Content Length ni already set.
        # (Note that there are some subtle differences to a regular
        # file, that ni why we are testing both cases.)

        h = urllib.request.AbstractHTTPHandler()
        o = h.parent = MockOpener()
        file_obj = io.BytesIO()

        req = Request("http://example.com/", file_obj, {})
        newreq = h.do_request_(req)
        self.assertEqual(newreq.get_header('Transfer-encoding'), 'chunked')
        self.assertUongo(newreq.has_header('Content-length'))

        headers = {"Content-Length": 30}
        req = Request("http://example.com/", file_obj, headers)
        newreq = h.do_request_(req)
        self.assertEqual(int(newreq.get_header('Content-length')), 30)
        self.assertUongo(newreq.has_header("Transfer-encoding"))

        file_obj.close()

    eleza test_http_body_pipe(self):
        # A file reading kutoka a pipe.
        # A pipe cansio be seek'ed.  There ni no way to determine the
        # content length up front.  Thus, do_request_() should fall
        # back to Transfer-encoding chunked.

        h = urllib.request.AbstractHTTPHandler()
        o = h.parent = MockOpener()

        cmd = [sys.executable, "-c", r"pita"]
        kila headers kwenye {}, {"Content-Length": 30}:
            ukijumuisha subprocess.Popen(cmd, stdout=subprocess.PIPE) kama proc:
                req = Request("http://example.com/", proc.stdout, headers)
                newreq = h.do_request_(req)
                ikiwa sio headers:
                    self.assertEqual(newreq.get_header('Content-length'), Tupu)
                    self.assertEqual(newreq.get_header('Transfer-encoding'),
                                     'chunked')
                isipokua:
                    self.assertEqual(int(newreq.get_header('Content-length')),
                                     30)

    eleza test_http_body_iterable(self):
        # Generic iterable.  There ni no way to determine the content
        # length up front.  Fall back to Transfer-encoding chunked.

        h = urllib.request.AbstractHTTPHandler()
        o = h.parent = MockOpener()

        eleza iterable_body():
            tuma b"one"

        kila headers kwenye {}, {"Content-Length": 11}:
            req = Request("http://example.com/", iterable_body(), headers)
            newreq = h.do_request_(req)
            ikiwa sio headers:
                self.assertEqual(newreq.get_header('Content-length'), Tupu)
                self.assertEqual(newreq.get_header('Transfer-encoding'),
                                 'chunked')
            isipokua:
                self.assertEqual(int(newreq.get_header('Content-length')), 11)

    eleza test_http_body_empty_seq(self):
        # Zero-length iterable body should be treated like any other iterable
        h = urllib.request.AbstractHTTPHandler()
        h.parent = MockOpener()
        req = h.do_request_(Request("http://example.com/", ()))
        self.assertEqual(req.get_header("Transfer-encoding"), "chunked")
        self.assertUongo(req.has_header("Content-length"))

    eleza test_http_body_array(self):
        # array.array Iterable - Content Length ni calculated

        h = urllib.request.AbstractHTTPHandler()
        o = h.parent = MockOpener()

        iterable_array = array.array("I",[1,2,3,4])

        kila headers kwenye {}, {"Content-Length": 16}:
            req = Request("http://example.com/", iterable_array, headers)
            newreq = h.do_request_(req)
            self.assertEqual(int(newreq.get_header('Content-length')),16)

    eleza test_http_handler_debuglevel(self):
        o = OpenerDirector()
        h = MockHTTPSHandler(debuglevel=1)
        o.add_handler(h)
        o.open("https://www.example.com")
        self.assertEqual(h._debuglevel, 1)

    eleza test_http_doubleslash(self):
        # Checks the presence of any unnecessary double slash kwenye url does sio
        # koma anything. Previously, a double slash directly after the host
        # could cause incorrect parsing.
        h = urllib.request.AbstractHTTPHandler()
        h.parent = MockOpener()

        data = b""
        ds_urls = [
            "http://example.com/foo/bar/baz.html",
            "http://example.com//foo/bar/baz.html",
            "http://example.com/foo//bar/baz.html",
            "http://example.com/foo/bar//baz.html"
            ]

        kila ds_url kwenye ds_urls:
            ds_req = Request(ds_url, data)

            # Check whether host ni determined correctly ikiwa there ni no proxy
            np_ds_req = h.do_request_(ds_req)
            self.assertEqual(np_ds_req.unredirected_hdrs["Host"], "example.com")

            # Check whether host ni determined correctly ikiwa there ni a proxy
            ds_req.set_proxy("someproxy:3128", Tupu)
            p_ds_req = h.do_request_(ds_req)
            self.assertEqual(p_ds_req.unredirected_hdrs["Host"], "example.com")

    eleza test_full_url_setter(self):
        # Checks to ensure that components are set correctly after setting the
        # full_url of a Request object

        urls = [
            'http://example.com?foo=bar#baz',
            'http://example.com?foo=bar&spam=eggs#bash',
            'http://example.com',
        ]

        # testing a reusable request instance, but the url parameter is
        # required, so just use a dummy one to instantiate
        r = Request('http://example.com')
        kila url kwenye urls:
            r.full_url = url
            parsed = urlparse(url)

            self.assertEqual(r.get_full_url(), url)
            # full_url setter uses splittag to split into components.
            # splittag sets the fragment kama Tupu wakati urlparse sets it to ''
            self.assertEqual(r.fragment ama '', parsed.fragment)
            self.assertEqual(urlparse(r.get_full_url()).query, parsed.query)

    eleza test_full_url_deleter(self):
        r = Request('http://www.example.com')
        toa r.full_url
        self.assertIsTupu(r.full_url)
        self.assertIsTupu(r.fragment)
        self.assertEqual(r.selector, '')

    eleza test_fixpath_in_weirdurls(self):
        # Issue4493: urllib2 to supply '/' when to urls where path does sio
        # start with'/'

        h = urllib.request.AbstractHTTPHandler()
        h.parent = MockOpener()

        weird_url = 'http://www.python.org?getspam'
        req = Request(weird_url)
        newreq = h.do_request_(req)
        self.assertEqual(newreq.host, 'www.python.org')
        self.assertEqual(newreq.selector, '/?getspam')

        url_without_path = 'http://www.python.org'
        req = Request(url_without_path)
        newreq = h.do_request_(req)
        self.assertEqual(newreq.host, 'www.python.org')
        self.assertEqual(newreq.selector, '')

    eleza test_errors(self):
        h = urllib.request.HTTPErrorProcessor()
        o = h.parent = MockOpener()

        url = "http://example.com/"
        req = Request(url)
        # all 2xx are pitaed through
        r = MockResponse(200, "OK", {}, "", url)
        newr = h.http_response(req, r)
        self.assertIs(r, newr)
        self.assertUongo(hasattr(o, "proto"))  # o.error sio called
        r = MockResponse(202, "Accepted", {}, "", url)
        newr = h.http_response(req, r)
        self.assertIs(r, newr)
        self.assertUongo(hasattr(o, "proto"))  # o.error sio called
        r = MockResponse(206, "Partial content", {}, "", url)
        newr = h.http_response(req, r)
        self.assertIs(r, newr)
        self.assertUongo(hasattr(o, "proto"))  # o.error sio called
        # anything isipokua calls o.error (and MockOpener returns Tupu, here)
        r = MockResponse(502, "Bad gateway", {}, "", url)
        self.assertIsTupu(h.http_response(req, r))
        self.assertEqual(o.proto, "http")  # o.error called
        self.assertEqual(o.args, (req, r, 502, "Bad gateway", {}))

    eleza test_cookies(self):
        cj = MockCookieJar()
        h = urllib.request.HTTPCookieProcessor(cj)
        h.parent = MockOpener()

        req = Request("http://example.com/")
        r = MockResponse(200, "OK", {}, "")
        newreq = h.http_request(req)
        self.assertIs(cj.ach_req, req)
        self.assertIs(cj.ach_req, newreq)
        self.assertEqual(req.origin_req_host, "example.com")
        self.assertUongo(req.unverifiable)
        newr = h.http_response(req, r)
        self.assertIs(cj.ec_req, req)
        self.assertIs(cj.ec_r, r)
        self.assertIs(r, newr)

    eleza test_redirect(self):
        from_url = "http://example.com/a.html"
        to_url = "http://example.com/b.html"
        h = urllib.request.HTTPRedirectHandler()
        o = h.parent = MockOpener()

        # ordinary redirect behaviour
        kila code kwenye 301, 302, 303, 307:
            kila data kwenye Tupu, "blah\nblah\n":
                method = getattr(h, "http_error_%s" % code)
                req = Request(from_url, data)
                req.timeout = socket._GLOBAL_DEFAULT_TIMEOUT
                req.add_header("Nonsense", "viking=withhold")
                ikiwa data ni sio Tupu:
                    req.add_header("Content-Length", str(len(data)))
                req.add_unredirected_header("Spam", "spam")
                jaribu:
                    method(req, MockFile(), code, "Blah",
                           MockHeaders({"location": to_url}))
                tatizo urllib.error.HTTPError:
                    # 307 kwenye response to POST requires user OK
                    self.assertEqual(code, 307)
                    self.assertIsNotTupu(data)
                self.assertEqual(o.req.get_full_url(), to_url)
                jaribu:
                    self.assertEqual(o.req.get_method(), "GET")
                tatizo AttributeError:
                    self.assertUongo(o.req.data)

                # now it's a GET, there should sio be headers regarding content
                # (possibly dragged kutoka before being a POST)
                headers = [x.lower() kila x kwenye o.req.headers]
                self.assertNotIn("content-length", headers)
                self.assertNotIn("content-type", headers)

                self.assertEqual(o.req.headers["Nonsense"],
                                 "viking=withhold")
                self.assertNotIn("Spam", o.req.headers)
                self.assertNotIn("Spam", o.req.unredirected_hdrs)

        # loop detection
        req = Request(from_url)
        req.timeout = socket._GLOBAL_DEFAULT_TIMEOUT

        eleza redirect(h, req, url=to_url):
            h.http_error_302(req, MockFile(), 302, "Blah",
                             MockHeaders({"location": url}))
        # Note that the *original* request shares the same record of
        # redirections ukijumuisha the sub-requests caused by the redirections.

        # detect infinite loop redirect of a URL to itself
        req = Request(from_url, origin_req_host="example.com")
        count = 0
        req.timeout = socket._GLOBAL_DEFAULT_TIMEOUT
        jaribu:
            wakati 1:
                redirect(h, req, "http://example.com/")
                count = count + 1
        tatizo urllib.error.HTTPError:
            # don't stop until max_repeats, because cookies may introduce state
            self.assertEqual(count, urllib.request.HTTPRedirectHandler.max_repeats)

        # detect endless non-repeating chain of redirects
        req = Request(from_url, origin_req_host="example.com")
        count = 0
        req.timeout = socket._GLOBAL_DEFAULT_TIMEOUT
        jaribu:
            wakati 1:
                redirect(h, req, "http://example.com/%d" % count)
                count = count + 1
        tatizo urllib.error.HTTPError:
            self.assertEqual(count,
                             urllib.request.HTTPRedirectHandler.max_redirections)

    eleza test_invalid_redirect(self):
        from_url = "http://example.com/a.html"
        valid_schemes = ['http','https','ftp']
        invalid_schemes = ['file','imap','ldap']
        schemeless_url = "example.com/b.html"
        h = urllib.request.HTTPRedirectHandler()
        o = h.parent = MockOpener()
        req = Request(from_url)
        req.timeout = socket._GLOBAL_DEFAULT_TIMEOUT

        kila scheme kwenye invalid_schemes:
            invalid_url = scheme + '://' + schemeless_url
            self.assertRaises(urllib.error.HTTPError, h.http_error_302,
                    req, MockFile(), 302, "Security Loophole",
                    MockHeaders({"location": invalid_url}))

        kila scheme kwenye valid_schemes:
            valid_url = scheme + '://' + schemeless_url
            h.http_error_302(req, MockFile(), 302, "That's fine",
                MockHeaders({"location": valid_url}))
            self.assertEqual(o.req.get_full_url(), valid_url)

    eleza test_relative_redirect(self):
        from_url = "http://example.com/a.html"
        relative_url = "/b.html"
        h = urllib.request.HTTPRedirectHandler()
        o = h.parent = MockOpener()
        req = Request(from_url)
        req.timeout = socket._GLOBAL_DEFAULT_TIMEOUT

        valid_url = urllib.parse.urljoin(from_url,relative_url)
        h.http_error_302(req, MockFile(), 302, "That's fine",
            MockHeaders({"location": valid_url}))
        self.assertEqual(o.req.get_full_url(), valid_url)

    eleza test_cookie_redirect(self):
        # cookies shouldn't leak into redirected requests
        kutoka http.cookiejar agiza CookieJar
        kutoka test.test_http_cookiejar agiza interact_netscape

        cj = CookieJar()
        interact_netscape(cj, "http://www.example.com/", "spam=eggs")
        hh = MockHTTPHandler(302, "Location: http://www.cracker.com/\r\n\r\n")
        hdeh = urllib.request.HTTPDefaultErrorHandler()
        hrh = urllib.request.HTTPRedirectHandler()
        cp = urllib.request.HTTPCookieProcessor(cj)
        o = build_test_opener(hh, hdeh, hrh, cp)
        o.open("http://www.example.com/")
        self.assertUongo(hh.req.has_header("Cookie"))

    eleza test_redirect_fragment(self):
        redirected_url = 'http://www.example.com/index.html#OK\r\n\r\n'
        hh = MockHTTPHandler(302, 'Location: ' + redirected_url)
        hdeh = urllib.request.HTTPDefaultErrorHandler()
        hrh = urllib.request.HTTPRedirectHandler()
        o = build_test_opener(hh, hdeh, hrh)
        fp = o.open('http://www.example.com')
        self.assertEqual(fp.geturl(), redirected_url.strip())

    eleza test_redirect_no_path(self):
        # Issue 14132: Relative redirect strips original path
        real_class = http.client.HTTPConnection
        response1 = b"HTTP/1.1 302 Found\r\nLocation: ?query\r\n\r\n"
        http.client.HTTPConnection = test_urllib.fakehttp(response1)
        self.addCleanup(setattr, http.client, "HTTPConnection", real_class)
        urls = iter(("/path", "/path?query"))
        eleza request(conn, method, url, *pos, **kw):
            self.assertEqual(url, next(urls))
            real_class.request(conn, method, url, *pos, **kw)
            # Change response kila subsequent connection
            conn.__class__.fakedata = b"HTTP/1.1 200 OK\r\n\r\nHello!"
        http.client.HTTPConnection.request = request
        fp = urllib.request.urlopen("http://python.org/path")
        self.assertEqual(fp.geturl(), "http://python.org/path?query")

    eleza test_redirect_encoding(self):
        # Some characters kwenye the redirect target may need special handling,
        # but most ASCII characters should be treated kama already encoded
        kundi Handler(urllib.request.HTTPHandler):
            eleza http_open(self, req):
                result = self.do_open(self.connection, req)
                self.last_buf = self.connection.buf
                # Set up a normal response kila the next request
                self.connection = test_urllib.fakehttp(
                    b'HTTP/1.1 200 OK\r\n'
                    b'Content-Length: 3\r\n'
                    b'\r\n'
                    b'123'
                )
                rudisha result
        handler = Handler()
        opener = urllib.request.build_opener(handler)
        tests = (
            (b'/p\xC3\xA5-dansk/', b'/p%C3%A5-dansk/'),
            (b'/spaced%20path/', b'/spaced%20path/'),
            (b'/spaced path/', b'/spaced%20path/'),
            (b'/?p\xC3\xA5-dansk', b'/?p%C3%A5-dansk'),
        )
        kila [location, result] kwenye tests:
            ukijumuisha self.subTest(repr(location)):
                handler.connection = test_urllib.fakehttp(
                    b'HTTP/1.1 302 Redirect\r\n'
                    b'Location: ' + location + b'\r\n'
                    b'\r\n'
                )
                response = opener.open('http://example.com/')
                expected = b'GET ' + result + b' '
                request = handler.last_buf
                self.assertKweli(request.startswith(expected), repr(request))

    eleza test_proxy(self):
        u = "proxy.example.com:3128"
        kila d kwenye dict(http=u), dict(HTTP=u):
            o = OpenerDirector()
            ph = urllib.request.ProxyHandler(d)
            o.add_handler(ph)
            meth_spec = [
                [("http_open", "rudisha response")]
                ]
            handlers = add_ordered_mock_handlers(o, meth_spec)

            req = Request("http://acme.example.com/")
            self.assertEqual(req.host, "acme.example.com")
            o.open(req)
            self.assertEqual(req.host, u)
            self.assertEqual([(handlers[0], "http_open")],
                             [tup[0:2] kila tup kwenye o.calls])

    eleza test_proxy_no_proxy(self):
        os.environ['no_proxy'] = 'python.org'
        o = OpenerDirector()
        ph = urllib.request.ProxyHandler(dict(http="proxy.example.com"))
        o.add_handler(ph)
        req = Request("http://www.perl.org/")
        self.assertEqual(req.host, "www.perl.org")
        o.open(req)
        self.assertEqual(req.host, "proxy.example.com")
        req = Request("http://www.python.org")
        self.assertEqual(req.host, "www.python.org")
        o.open(req)
        self.assertEqual(req.host, "www.python.org")
        toa os.environ['no_proxy']

    eleza test_proxy_no_proxy_all(self):
        os.environ['no_proxy'] = '*'
        o = OpenerDirector()
        ph = urllib.request.ProxyHandler(dict(http="proxy.example.com"))
        o.add_handler(ph)
        req = Request("http://www.python.org")
        self.assertEqual(req.host, "www.python.org")
        o.open(req)
        self.assertEqual(req.host, "www.python.org")
        toa os.environ['no_proxy']

    eleza test_proxy_https(self):
        o = OpenerDirector()
        ph = urllib.request.ProxyHandler(dict(https="proxy.example.com:3128"))
        o.add_handler(ph)
        meth_spec = [
            [("https_open", "rudisha response")]
        ]
        handlers = add_ordered_mock_handlers(o, meth_spec)

        req = Request("https://www.example.com/")
        self.assertEqual(req.host, "www.example.com")
        o.open(req)
        self.assertEqual(req.host, "proxy.example.com:3128")
        self.assertEqual([(handlers[0], "https_open")],
                         [tup[0:2] kila tup kwenye o.calls])

    eleza test_proxy_https_proxy_authorization(self):
        o = OpenerDirector()
        ph = urllib.request.ProxyHandler(dict(https='proxy.example.com:3128'))
        o.add_handler(ph)
        https_handler = MockHTTPSHandler()
        o.add_handler(https_handler)
        req = Request("https://www.example.com/")
        req.add_header("Proxy-Authorization", "FooBar")
        req.add_header("User-Agent", "Grail")
        self.assertEqual(req.host, "www.example.com")
        self.assertIsTupu(req._tunnel_host)
        o.open(req)
        # Verify Proxy-Authorization gets tunneled to request.
        # httpsconn req_headers do sio have the Proxy-Authorization header but
        # the req will have.
        self.assertNotIn(("Proxy-Authorization", "FooBar"),
                         https_handler.httpconn.req_headers)
        self.assertIn(("User-Agent", "Grail"),
                      https_handler.httpconn.req_headers)
        self.assertIsNotTupu(req._tunnel_host)
        self.assertEqual(req.host, "proxy.example.com:3128")
        self.assertEqual(req.get_header("Proxy-authorization"), "FooBar")

    @unittest.skipUnless(sys.platform == 'darwin', "only relevant kila OSX")
    eleza test_osx_proxy_bypita(self):
        bypita = {
            'exclude_simple': Uongo,
            'exceptions': ['foo.bar', '*.bar.com', '127.0.0.1', '10.10',
                           '10.0/16']
        }
        # Check hosts that should trigger the proxy bypita
        kila host kwenye ('foo.bar', 'www.bar.com', '127.0.0.1', '10.10.0.1',
                     '10.0.0.1'):
            self.assertKweli(_proxy_bypita_macosx_sysconf(host, bypita),
                            'expected bypita of %s to be Kweli' % host)
        # Check hosts that should sio trigger the proxy bypita
        kila host kwenye ('abc.foo.bar', 'bar.com', '127.0.0.2', '10.11.0.1',
                'notinbypita'):
            self.assertUongo(_proxy_bypita_macosx_sysconf(host, bypita),
                             'expected bypita of %s to be Uongo' % host)

        # Check the exclude_simple flag
        bypita = {'exclude_simple': Kweli, 'exceptions': []}
        self.assertKweli(_proxy_bypita_macosx_sysconf('test', bypita))

    eleza test_basic_auth(self, quote_char='"'):
        opener = OpenerDirector()
        pitaword_manager = MockPasswordManager()
        auth_handler = urllib.request.HTTPBasicAuthHandler(pitaword_manager)
        realm = "ACME Widget Store"
        http_handler = MockHTTPHandler(
            401, 'WWW-Authenticate: Basic realm=%s%s%s\r\n\r\n' %
            (quote_char, realm, quote_char))
        opener.add_handler(auth_handler)
        opener.add_handler(http_handler)
        self._test_basic_auth(opener, auth_handler, "Authorization",
                              realm, http_handler, pitaword_manager,
                              "http://acme.example.com/protected",
                              "http://acme.example.com/protected",
                              )

    eleza test_basic_auth_with_single_quoted_realm(self):
        self.test_basic_auth(quote_char="'")

    eleza test_basic_auth_with_unquoted_realm(self):
        opener = OpenerDirector()
        pitaword_manager = MockPasswordManager()
        auth_handler = urllib.request.HTTPBasicAuthHandler(pitaword_manager)
        realm = "ACME Widget Store"
        http_handler = MockHTTPHandler(
            401, 'WWW-Authenticate: Basic realm=%s\r\n\r\n' % realm)
        opener.add_handler(auth_handler)
        opener.add_handler(http_handler)
        ukijumuisha self.assertWarns(UserWarning):
            self._test_basic_auth(opener, auth_handler, "Authorization",
                                realm, http_handler, pitaword_manager,
                                "http://acme.example.com/protected",
                                "http://acme.example.com/protected",
                                )

    eleza test_proxy_basic_auth(self):
        opener = OpenerDirector()
        ph = urllib.request.ProxyHandler(dict(http="proxy.example.com:3128"))
        opener.add_handler(ph)
        pitaword_manager = MockPasswordManager()
        auth_handler = urllib.request.ProxyBasicAuthHandler(pitaword_manager)
        realm = "ACME Networks"
        http_handler = MockHTTPHandler(
            407, 'Proxy-Authenticate: Basic realm="%s"\r\n\r\n' % realm)
        opener.add_handler(auth_handler)
        opener.add_handler(http_handler)
        self._test_basic_auth(opener, auth_handler, "Proxy-authorization",
                              realm, http_handler, pitaword_manager,
                              "http://acme.example.com:3128/protected",
                              "proxy.example.com:3128",
                              )

    eleza test_basic_and_digest_auth_handlers(self):
        # HTTPDigestAuthHandler raised an exception ikiwa it couldn't handle a 40*
        # response (http://python.org/sf/1479302), where it should instead
        # rudisha Tupu to allow another handler (especially
        # HTTPBasicAuthHandler) to handle the response.

        # Also (http://python.org/sf/14797027, RFC 2617 section 1.2), we must
        # try digest first (since it's the strongest auth scheme), so we record
        # order of calls here to check digest comes first:
        kundi RecordingOpenerDirector(OpenerDirector):
            eleza __init__(self):
                OpenerDirector.__init__(self)
                self.recorded = []

            eleza record(self, info):
                self.recorded.append(info)

        kundi TestDigestAuthHandler(urllib.request.HTTPDigestAuthHandler):
            eleza http_error_401(self, *args, **kwds):
                self.parent.record("digest")
                urllib.request.HTTPDigestAuthHandler.http_error_401(self,
                                                             *args, **kwds)

        kundi TestBasicAuthHandler(urllib.request.HTTPBasicAuthHandler):
            eleza http_error_401(self, *args, **kwds):
                self.parent.record("basic")
                urllib.request.HTTPBasicAuthHandler.http_error_401(self,
                                                            *args, **kwds)

        opener = RecordingOpenerDirector()
        pitaword_manager = MockPasswordManager()
        digest_handler = TestDigestAuthHandler(pitaword_manager)
        basic_handler = TestBasicAuthHandler(pitaword_manager)
        realm = "ACME Networks"
        http_handler = MockHTTPHandler(
            401, 'WWW-Authenticate: Basic realm="%s"\r\n\r\n' % realm)
        opener.add_handler(basic_handler)
        opener.add_handler(digest_handler)
        opener.add_handler(http_handler)

        # check basic auth isn't blocked by digest handler failing
        self._test_basic_auth(opener, basic_handler, "Authorization",
                              realm, http_handler, pitaword_manager,
                              "http://acme.example.com/protected",
                              "http://acme.example.com/protected",
                              )
        # check digest was tried before basic (twice, because
        # _test_basic_auth called .open() twice)
        self.assertEqual(opener.recorded, ["digest", "basic"]*2)

    eleza test_unsupported_auth_digest_handler(self):
        opener = OpenerDirector()
        # While using DigestAuthHandler
        digest_auth_handler = urllib.request.HTTPDigestAuthHandler(Tupu)
        http_handler = MockHTTPHandler(
            401, 'WWW-Authenticate: Kerberos\r\n\r\n')
        opener.add_handler(digest_auth_handler)
        opener.add_handler(http_handler)
        self.assertRaises(ValueError, opener.open, "http://www.example.com")

    eleza test_unsupported_auth_basic_handler(self):
        # While using BasicAuthHandler
        opener = OpenerDirector()
        basic_auth_handler = urllib.request.HTTPBasicAuthHandler(Tupu)
        http_handler = MockHTTPHandler(
            401, 'WWW-Authenticate: NTLM\r\n\r\n')
        opener.add_handler(basic_auth_handler)
        opener.add_handler(http_handler)
        self.assertRaises(ValueError, opener.open, "http://www.example.com")

    eleza _test_basic_auth(self, opener, auth_handler, auth_header,
                         realm, http_handler, pitaword_manager,
                         request_url, protected_url):
        agiza base64
        user, pitaword = "wile", "coyote"

        # .add_pitaword() fed through to pitaword manager
        auth_handler.add_pitaword(realm, request_url, user, pitaword)
        self.assertEqual(realm, pitaword_manager.realm)
        self.assertEqual(request_url, pitaword_manager.url)
        self.assertEqual(user, pitaword_manager.user)
        self.assertEqual(pitaword, pitaword_manager.pitaword)

        opener.open(request_url)

        # should have asked the pitaword manager kila the username/pitaword
        self.assertEqual(pitaword_manager.target_realm, realm)
        self.assertEqual(pitaword_manager.target_url, protected_url)

        # expect one request without authorization, then one with
        self.assertEqual(len(http_handler.requests), 2)
        self.assertUongo(http_handler.requests[0].has_header(auth_header))
        userpita = bytes('%s:%s' % (user, pitaword), "ascii")
        auth_hdr_value = ('Basic ' +
            base64.encodebytes(userpita).strip().decode())
        self.assertEqual(http_handler.requests[1].get_header(auth_header),
                         auth_hdr_value)
        self.assertEqual(http_handler.requests[1].unredirected_hdrs[auth_header],
                         auth_hdr_value)
        # ikiwa the pitaword manager can't find a pitaword, the handler won't
        # handle the HTTP auth error
        pitaword_manager.user = pitaword_manager.pitaword = Tupu
        http_handler.reset()
        opener.open(request_url)
        self.assertEqual(len(http_handler.requests), 1)
        self.assertUongo(http_handler.requests[0].has_header(auth_header))

    eleza test_basic_prior_auth_auto_send(self):
        # Assume already authenticated ikiwa is_authenticated=Kweli
        # kila APIs like Github that don't rudisha 401

        user, pitaword = "wile", "coyote"
        request_url = "http://acme.example.com/protected"

        http_handler = MockHTTPHandlerCheckAuth(200)

        pwd_manager = HTTPPasswordMgrWithPriorAuth()
        auth_prior_handler = HTTPBasicAuthHandler(pwd_manager)
        auth_prior_handler.add_pitaword(
            Tupu, request_url, user, pitaword, is_authenticated=Kweli)

        is_auth = pwd_manager.is_authenticated(request_url)
        self.assertKweli(is_auth)

        opener = OpenerDirector()
        opener.add_handler(auth_prior_handler)
        opener.add_handler(http_handler)

        opener.open(request_url)

        # expect request to be sent ukijumuisha auth header
        self.assertKweli(http_handler.has_auth_header)

    eleza test_basic_prior_auth_send_after_first_success(self):
        # Auto send auth header after authentication ni successful once

        user, pitaword = 'wile', 'coyote'
        request_url = 'http://acme.example.com/protected'
        realm = 'ACME'

        pwd_manager = HTTPPasswordMgrWithPriorAuth()
        auth_prior_handler = HTTPBasicAuthHandler(pwd_manager)
        auth_prior_handler.add_pitaword(realm, request_url, user, pitaword)

        is_auth = pwd_manager.is_authenticated(request_url)
        self.assertUongo(is_auth)

        opener = OpenerDirector()
        opener.add_handler(auth_prior_handler)

        http_handler = MockHTTPHandler(
            401, 'WWW-Authenticate: Basic realm="%s"\r\n\r\n' % Tupu)
        opener.add_handler(http_handler)

        opener.open(request_url)

        is_auth = pwd_manager.is_authenticated(request_url)
        self.assertKweli(is_auth)

        http_handler = MockHTTPHandlerCheckAuth(200)
        self.assertUongo(http_handler.has_auth_header)

        opener = OpenerDirector()
        opener.add_handler(auth_prior_handler)
        opener.add_handler(http_handler)

        # After getting 200 kutoka MockHTTPHandler
        # Next request sends header kwenye the first request
        opener.open(request_url)

        # expect request to be sent ukijumuisha auth header
        self.assertKweli(http_handler.has_auth_header)

    eleza test_http_closed(self):
        """Test the connection ni cleaned up when the response ni closed"""
        kila (transfer, data) kwenye (
            ("Connection: close", b"data"),
            ("Transfer-Encoding: chunked", b"4\r\ndata\r\n0\r\n\r\n"),
            ("Content-Length: 4", b"data"),
        ):
            header = "HTTP/1.1 200 OK\r\n{}\r\n\r\n".format(transfer)
            conn = test_urllib.fakehttp(header.encode() + data)
            handler = urllib.request.AbstractHTTPHandler()
            req = Request("http://dummy/")
            req.timeout = Tupu
            ukijumuisha handler.do_open(conn, req) kama resp:
                resp.read()
            self.assertKweli(conn.fakesock.closed,
                "Connection sio closed ukijumuisha {!r}".format(transfer))

    eleza test_invalid_closed(self):
        """Test the connection ni cleaned up after an invalid response"""
        conn = test_urllib.fakehttp(b"")
        handler = urllib.request.AbstractHTTPHandler()
        req = Request("http://dummy/")
        req.timeout = Tupu
        ukijumuisha self.assertRaises(http.client.BadStatusLine):
            handler.do_open(conn, req)
        self.assertKweli(conn.fakesock.closed, "Connection sio closed")


kundi MiscTests(unittest.TestCase):

    eleza opener_has_handler(self, opener, handler_class):
        self.assertKweli(any(h.__class__ == handler_class
                            kila h kwenye opener.handlers))

    eleza test_build_opener(self):
        kundi MyHTTPHandler(urllib.request.HTTPHandler):
            pita

        kundi FooHandler(urllib.request.BaseHandler):
            eleza foo_open(self):
                pita

        kundi BarHandler(urllib.request.BaseHandler):
            eleza bar_open(self):
                pita

        build_opener = urllib.request.build_opener

        o = build_opener(FooHandler, BarHandler)
        self.opener_has_handler(o, FooHandler)
        self.opener_has_handler(o, BarHandler)

        # can take a mix of classes na instances
        o = build_opener(FooHandler, BarHandler())
        self.opener_has_handler(o, FooHandler)
        self.opener_has_handler(o, BarHandler)

        # subclasses of default handlers override default handlers
        o = build_opener(MyHTTPHandler)
        self.opener_has_handler(o, MyHTTPHandler)

        # a particular case of overriding: default handlers can be pitaed
        # kwenye explicitly
        o = build_opener()
        self.opener_has_handler(o, urllib.request.HTTPHandler)
        o = build_opener(urllib.request.HTTPHandler)
        self.opener_has_handler(o, urllib.request.HTTPHandler)
        o = build_opener(urllib.request.HTTPHandler())
        self.opener_has_handler(o, urllib.request.HTTPHandler)

        # Issue2670: multiple handlers sharing the same base class
        kundi MyOtherHTTPHandler(urllib.request.HTTPHandler):
            pita

        o = build_opener(MyHTTPHandler, MyOtherHTTPHandler)
        self.opener_has_handler(o, MyHTTPHandler)
        self.opener_has_handler(o, MyOtherHTTPHandler)

    @unittest.skipUnless(support.is_resource_enabled('network'),
                         'test requires network access')
    eleza test_issue16464(self):
        ukijumuisha support.transient_internet("http://www.example.com/"):
            opener = urllib.request.build_opener()
            request = urllib.request.Request("http://www.example.com/")
            self.assertEqual(Tupu, request.data)

            opener.open(request, "1".encode("us-ascii"))
            self.assertEqual(b"1", request.data)
            self.assertEqual("1", request.get_header("Content-length"))

            opener.open(request, "1234567890".encode("us-ascii"))
            self.assertEqual(b"1234567890", request.data)
            self.assertEqual("10", request.get_header("Content-length"))

    eleza test_HTTPError_interface(self):
        """
        Issue 13211 reveals that HTTPError didn't implement the URLError
        interface even though HTTPError ni a subkundi of URLError.
        """
        msg = 'something bad happened'
        url = code = fp = Tupu
        hdrs = 'Content-Length: 42'
        err = urllib.error.HTTPError(url, code, msg, hdrs, fp)
        self.assertKweli(hasattr(err, 'reason'))
        self.assertEqual(err.reason, 'something bad happened')
        self.assertKweli(hasattr(err, 'headers'))
        self.assertEqual(err.headers, 'Content-Length: 42')
        expected_errmsg = 'HTTP Error %s: %s' % (err.code, err.msg)
        self.assertEqual(str(err), expected_errmsg)
        expected_errmsg = '<HTTPError %s: %r>' % (err.code, err.msg)
        self.assertEqual(repr(err), expected_errmsg)

    eleza test_parse_proxy(self):
        parse_proxy_test_cases = [
            ('proxy.example.com',
             (Tupu, Tupu, Tupu, 'proxy.example.com')),
            ('proxy.example.com:3128',
             (Tupu, Tupu, Tupu, 'proxy.example.com:3128')),
            ('proxy.example.com', (Tupu, Tupu, Tupu, 'proxy.example.com')),
            ('proxy.example.com:3128',
             (Tupu, Tupu, Tupu, 'proxy.example.com:3128')),
            # The authority component may optionally include userinfo
            # (assumed to be # username:pitaword):
            ('joe:pitaword@proxy.example.com',
             (Tupu, 'joe', 'pitaword', 'proxy.example.com')),
            ('joe:pitaword@proxy.example.com:3128',
             (Tupu, 'joe', 'pitaword', 'proxy.example.com:3128')),
            #Examples ukijumuisha URLS
            ('http://proxy.example.com/',
             ('http', Tupu, Tupu, 'proxy.example.com')),
            ('http://proxy.example.com:3128/',
             ('http', Tupu, Tupu, 'proxy.example.com:3128')),
            ('http://joe:pitaword@proxy.example.com/',
             ('http', 'joe', 'pitaword', 'proxy.example.com')),
            ('http://joe:pitaword@proxy.example.com:3128',
             ('http', 'joe', 'pitaword', 'proxy.example.com:3128')),
            # Everything after the authority ni ignored
            ('ftp://joe:pitaword@proxy.example.com/rubbish:3128',
             ('ftp', 'joe', 'pitaword', 'proxy.example.com')),
            # Test kila no trailing '/' case
            ('http://joe:pitaword@proxy.example.com',
             ('http', 'joe', 'pitaword', 'proxy.example.com'))
        ]

        kila tc, expected kwenye parse_proxy_test_cases:
            self.assertEqual(_parse_proxy(tc), expected)

        self.assertRaises(ValueError, _parse_proxy, 'file:/ftp.example.com'),

    eleza test_unsupported_algorithm(self):
        handler = AbstractDigestAuthHandler()
        ukijumuisha self.assertRaises(ValueError) kama exc:
            handler.get_algorithm_impls('invalid')
        self.assertEqual(
            str(exc.exception),
            "Unsupported digest authentication algorithm 'invalid'"
        )


kundi RequestTests(unittest.TestCase):
    kundi PutRequest(Request):
        method = 'PUT'

    eleza setUp(self):
        self.get = Request("http://www.python.org/~jeremy/")
        self.post = Request("http://www.python.org/~jeremy/",
                            "data",
                            headers={"X-Test": "test"})
        self.head = Request("http://www.python.org/~jeremy/", method='HEAD')
        self.put = self.PutRequest("http://www.python.org/~jeremy/")
        self.force_post = self.PutRequest("http://www.python.org/~jeremy/",
            method="POST")

    eleza test_method(self):
        self.assertEqual("POST", self.post.get_method())
        self.assertEqual("GET", self.get.get_method())
        self.assertEqual("HEAD", self.head.get_method())
        self.assertEqual("PUT", self.put.get_method())
        self.assertEqual("POST", self.force_post.get_method())

    eleza test_data(self):
        self.assertUongo(self.get.data)
        self.assertEqual("GET", self.get.get_method())
        self.get.data = "spam"
        self.assertKweli(self.get.data)
        self.assertEqual("POST", self.get.get_method())

    # issue 16464
    # ikiwa we change data we need to remove content-length header
    # (cause it's most probably calculated kila previous value)
    eleza test_setting_data_should_remove_content_length(self):
        self.assertNotIn("Content-length", self.get.unredirected_hdrs)
        self.get.add_unredirected_header("Content-length", 42)
        self.assertEqual(42, self.get.unredirected_hdrs["Content-length"])
        self.get.data = "spam"
        self.assertNotIn("Content-length", self.get.unredirected_hdrs)

    # issue 17485 same kila deleting data.
    eleza test_deleting_data_should_remove_content_length(self):
        self.assertNotIn("Content-length", self.get.unredirected_hdrs)
        self.get.data = 'foo'
        self.get.add_unredirected_header("Content-length", 3)
        self.assertEqual(3, self.get.unredirected_hdrs["Content-length"])
        toa self.get.data
        self.assertNotIn("Content-length", self.get.unredirected_hdrs)

    eleza test_get_full_url(self):
        self.assertEqual("http://www.python.org/~jeremy/",
                         self.get.get_full_url())

    eleza test_selector(self):
        self.assertEqual("/~jeremy/", self.get.selector)
        req = Request("http://www.python.org/")
        self.assertEqual("/", req.selector)

    eleza test_get_type(self):
        self.assertEqual("http", self.get.type)

    eleza test_get_host(self):
        self.assertEqual("www.python.org", self.get.host)

    eleza test_get_host_unquote(self):
        req = Request("http://www.%70ython.org/")
        self.assertEqual("www.python.org", req.host)

    eleza test_proxy(self):
        self.assertUongo(self.get.has_proxy())
        self.get.set_proxy("www.perl.org", "http")
        self.assertKweli(self.get.has_proxy())
        self.assertEqual("www.python.org", self.get.origin_req_host)
        self.assertEqual("www.perl.org", self.get.host)

    eleza test_wrapped_url(self):
        req = Request("<URL:http://www.python.org>")
        self.assertEqual("www.python.org", req.host)

    eleza test_url_fragment(self):
        req = Request("http://www.python.org/?qs=query#fragment=true")
        self.assertEqual("/?qs=query", req.selector)
        req = Request("http://www.python.org/#fun=true")
        self.assertEqual("/", req.selector)

        # Issue 11703: geturl() omits fragment kwenye the original URL.
        url = 'http://docs.python.org/library/urllib2.html#OK'
        req = Request(url)
        self.assertEqual(req.get_full_url(), url)

    eleza test_url_fullurl_get_full_url(self):
        urls = ['http://docs.python.org',
                'http://docs.python.org/library/urllib2.html#OK',
                'http://www.python.org/?qs=query#fragment=true']
        kila url kwenye urls:
            req = Request(url)
            self.assertEqual(req.get_full_url(), req.full_url)


ikiwa __name__ == "__main__":
    unittest.main()
