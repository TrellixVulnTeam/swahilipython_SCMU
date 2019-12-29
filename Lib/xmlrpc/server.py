r"""XML-RPC Servers.

This module can be used to create simple XML-RPC servers
by creating a server na either installing functions, a
kundi instance, ama by extending the SimpleXMLRPCServer
class.

It can also be used to handle XML-RPC requests kwenye a CGI
environment using CGIXMLRPCRequestHandler.

The Doc* classes can be used to create XML-RPC servers that
serve pydoc-style documentation kwenye response to HTTP
GET requests. This documentation ni dynamically generated
based on the functions na methods registered ukijumuisha the
server.

A list of possible usage patterns follows:

1. Install functions:

server = SimpleXMLRPCServer(("localhost", 8000))
server.register_function(pow)
server.register_function(lambda x,y: x+y, 'add')
server.serve_forever()

2. Install an instance:

kundi MyFuncs:
    eleza __init__(self):
        # make all of the sys functions available through sys.func_name
        agiza sys
        self.sys = sys
    eleza _listMethods(self):
        # implement this method so that system.listMethods
        # knows to advertise the sys methods
        rudisha list_public_methods(self) + \
                ['sys.' + method kila method kwenye list_public_methods(self.sys)]
    eleza pow(self, x, y): rudisha pow(x, y)
    eleza add(self, x, y) : rudisha x + y

server = SimpleXMLRPCServer(("localhost", 8000))
server.register_introspection_functions()
server.register_instance(MyFuncs())
server.serve_forever()

3. Install an instance ukijumuisha custom dispatch method:

kundi Math:
    eleza _listMethods(self):
        # this method must be present kila system.listMethods
        # to work
        rudisha ['add', 'pow']
    eleza _methodHelp(self, method):
        # this method must be present kila system.methodHelp
        # to work
        ikiwa method == 'add':
            rudisha "add(2,3) => 5"
        lasivyo method == 'pow':
            rudisha "pow(x, y[, z]) => number"
        isipokua:
            # By convention, rudisha empty
            # string ikiwa no help ni available
            rudisha ""
    eleza _dispatch(self, method, params):
        ikiwa method == 'pow':
            rudisha pow(*params)
        lasivyo method == 'add':
            rudisha params[0] + params[1]
        isipokua:
            ashiria ValueError('bad method')

server = SimpleXMLRPCServer(("localhost", 8000))
server.register_introspection_functions()
server.register_instance(Math())
server.serve_forever()

4. Subkundi SimpleXMLRPCServer:

kundi MathServer(SimpleXMLRPCServer):
    eleza _dispatch(self, method, params):
        jaribu:
            # We are forcing the 'export_' prefix on methods that are
            # callable through XML-RPC to prevent potential security
            # problems
            func = getattr(self, 'export_' + method)
        tatizo AttributeError:
            ashiria Exception('method "%s" ni sio supported' % method)
        isipokua:
            rudisha func(*params)

    eleza export_add(self, x, y):
        rudisha x + y

server = MathServer(("localhost", 8000))
server.serve_forever()

5. CGI script:

server = CGIXMLRPCRequestHandler()
server.register_function(pow)
server.handle_request()
"""

# Written by Brian Quinlan (brian@sweetapp.com).
# Based on code written by Fredrik Lundh.

kutoka xmlrpc.client agiza Fault, dumps, loads, gzip_encode, gzip_decode
kutoka http.server agiza BaseHTTPRequestHandler
kutoka functools agiza partial
kutoka inspect agiza signature
agiza html
agiza http.server
agiza socketserver
agiza sys
agiza os
agiza re
agiza pydoc
agiza traceback
jaribu:
    agiza fcntl
tatizo ImportError:
    fcntl = Tupu

eleza resolve_dotted_attribute(obj, attr, allow_dotted_names=Kweli):
    """resolve_dotted_attribute(a, 'b.c.d') => a.b.c.d

    Resolves a dotted attribute name to an object.  Raises
    an AttributeError ikiwa any attribute kwenye the chain starts ukijumuisha a '_'.

    If the optional allow_dotted_names argument ni false, dots are not
    supported na this function operates similar to getattr(obj, attr).
    """

    ikiwa allow_dotted_names:
        attrs = attr.split('.')
    isipokua:
        attrs = [attr]

    kila i kwenye attrs:
        ikiwa i.startswith('_'):
            ashiria AttributeError(
                'attempt to access private attribute "%s"' % i
                )
        isipokua:
            obj = getattr(obj,i)
    rudisha obj

eleza list_public_methods(obj):
    """Returns a list of attribute strings, found kwenye the specified
    object, which represent callable attributes"""

    rudisha [member kila member kwenye dir(obj)
                ikiwa sio member.startswith('_') and
                    callable(getattr(obj, member))]

kundi SimpleXMLRPCDispatcher:
    """Mix-in kundi that dispatches XML-RPC requests.

    This kundi ni used to register XML-RPC method handlers
    na then to dispatch them. This kundi doesn't need to be
    instanced directly when used by SimpleXMLRPCServer but it
    can be instanced when used by the MultiPathXMLRPCServer
    """

    eleza __init__(self, allow_none=Uongo, encoding=Tupu,
                 use_builtin_types=Uongo):
        self.funcs = {}
        self.instance = Tupu
        self.allow_none = allow_none
        self.encoding = encoding ama 'utf-8'
        self.use_builtin_types = use_builtin_types

    eleza register_instance(self, instance, allow_dotted_names=Uongo):
        """Registers an instance to respond to XML-RPC requests.

        Only one instance can be installed at a time.

        If the registered instance has a _dispatch method then that
        method will be called ukijumuisha the name of the XML-RPC method and
        its parameters kama a tuple
        e.g. instance._dispatch('add',(2,3))

        If the registered instance does sio have a _dispatch method
        then the instance will be searched to find a matching method
        and, ikiwa found, will be called. Methods beginning ukijumuisha an '_'
        are considered private na will sio be called by
        SimpleXMLRPCServer.

        If a registered function matches an XML-RPC request, then it
        will be called instead of the registered instance.

        If the optional allow_dotted_names argument ni true na the
        instance does sio have a _dispatch method, method names
        containing dots are supported na resolved, kama long kama none of
        the name segments start ukijumuisha an '_'.

            *** SECURITY WARNING: ***

            Enabling the allow_dotted_names options allows intruders
            to access your module's global variables na may allow
            intruders to execute arbitrary code on your machine.  Only
            use this option on a secure, closed network.

        """

        self.instance = instance
        self.allow_dotted_names = allow_dotted_names

    eleza register_function(self, function=Tupu, name=Tupu):
        """Registers a function to respond to XML-RPC requests.

        The optional name argument can be used to set a Unicode name
        kila the function.
        """
        # decorator factory
        ikiwa function ni Tupu:
            rudisha partial(self.register_function, name=name)

        ikiwa name ni Tupu:
            name = function.__name__
        self.funcs[name] = function

        rudisha function

    eleza register_introspection_functions(self):
        """Registers the XML-RPC introspection methods kwenye the system
        namespace.

        see http://xmlrpc.usefulinc.com/doc/reserved.html
        """

        self.funcs.update({'system.listMethods' : self.system_listMethods,
                      'system.methodSignature' : self.system_methodSignature,
                      'system.methodHelp' : self.system_methodHelp})

    eleza register_multicall_functions(self):
        """Registers the XML-RPC multicall method kwenye the system
        namespace.

        see http://www.xmlrpc.com/discuss/msgReader$1208"""

        self.funcs.update({'system.multicall' : self.system_multicall})

    eleza _marshaled_dispatch(self, data, dispatch_method = Tupu, path = Tupu):
        """Dispatches an XML-RPC method kutoka marshalled (XML) data.

        XML-RPC methods are dispatched kutoka the marshalled (XML) data
        using the _dispatch method na the result ni rudishaed as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided kama an argument (see comment in
        SimpleXMLRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing ni the preferred means
        of changing method dispatch behavior.
        """

        jaribu:
            params, method = loads(data, use_builtin_types=self.use_builtin_types)

            # generate response
            ikiwa dispatch_method ni sio Tupu:
                response = dispatch_method(method, params)
            isipokua:
                response = self._dispatch(method, params)
            # wrap response kwenye a singleton tuple
            response = (response,)
            response = dumps(response, methodresponse=1,
                             allow_none=self.allow_none, encoding=self.encoding)
        tatizo Fault kama fault:
            response = dumps(fault, allow_none=self.allow_none,
                             encoding=self.encoding)
        except:
            # report exception back to server
            exc_type, exc_value, exc_tb = sys.exc_info()
            jaribu:
                response = dumps(
                    Fault(1, "%s:%s" % (exc_type, exc_value)),
                    encoding=self.encoding, allow_none=self.allow_none,
                    )
            mwishowe:
                # Break reference cycle
                exc_type = exc_value = exc_tb = Tupu

        rudisha response.encode(self.encoding, 'xmlcharrefreplace')

    eleza system_listMethods(self):
        """system.listMethods() => ['add', 'subtract', 'multiple']

        Returns a list of the methods supported by the server."""

        methods = set(self.funcs.keys())
        ikiwa self.instance ni sio Tupu:
            # Instance can implement _listMethod to rudisha a list of
            # methods
            ikiwa hasattr(self.instance, '_listMethods'):
                methods |= set(self.instance._listMethods())
            # ikiwa the instance has a _dispatch method then we
            # don't have enough information to provide a list
            # of methods
            lasivyo sio hasattr(self.instance, '_dispatch'):
                methods |= set(list_public_methods(self.instance))
        rudisha sorted(methods)

    eleza system_methodSignature(self, method_name):
        """system.methodSignature('add') => [double, int, int]

        Returns a list describing the signature of the method. In the
        above example, the add method takes two integers kama arguments
        na rudishas a double result.

        This server does NOT support system.methodSignature."""

        # See http://xmlrpc.usefulinc.com/doc/sysmethodsig.html

        rudisha 'signatures sio supported'

    eleza system_methodHelp(self, method_name):
        """system.methodHelp('add') => "Adds two integers together"

        Returns a string containing documentation kila the specified method."""

        method = Tupu
        ikiwa method_name kwenye self.funcs:
            method = self.funcs[method_name]
        lasivyo self.instance ni sio Tupu:
            # Instance can implement _methodHelp to rudisha help kila a method
            ikiwa hasattr(self.instance, '_methodHelp'):
                rudisha self.instance._methodHelp(method_name)
            # ikiwa the instance has a _dispatch method then we
            # don't have enough information to provide help
            lasivyo sio hasattr(self.instance, '_dispatch'):
                jaribu:
                    method = resolve_dotted_attribute(
                                self.instance,
                                method_name,
                                self.allow_dotted_names
                                )
                tatizo AttributeError:
                    pita

        # Note that we aren't checking that the method actually
        # be a callable object of some kind
        ikiwa method ni Tupu:
            rudisha ""
        isipokua:
            rudisha pydoc.getdoc(method)

    eleza system_multicall(self, call_list):
        """system.multicall([{'methodName': 'add', 'params': [2, 2]}, ...]) => \
[[4], ...]

        Allows the caller to package multiple XML-RPC calls into a single
        request.

        See http://www.xmlrpc.com/discuss/msgReader$1208
        """

        results = []
        kila call kwenye call_list:
            method_name = call['methodName']
            params = call['params']

            jaribu:
                # XXX A marshalling error kwenye any response will fail the entire
                # multicall. If someone cares they should fix this.
                results.append([self._dispatch(method_name, params)])
            tatizo Fault kama fault:
                results.append(
                    {'faultCode' : fault.faultCode,
                     'faultString' : fault.faultString}
                    )
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                jaribu:
                    results.append(
                        {'faultCode' : 1,
                         'faultString' : "%s:%s" % (exc_type, exc_value)}
                        )
                mwishowe:
                    # Break reference cycle
                    exc_type = exc_value = exc_tb = Tupu
        rudisha results

    eleza _dispatch(self, method, params):
        """Dispatches the XML-RPC method.

        XML-RPC calls are forwarded to a registered function that
        matches the called XML-RPC method name. If no such function
        exists then the call ni forwarded to the registered instance,
        ikiwa available.

        If the registered instance has a _dispatch method then that
        method will be called ukijumuisha the name of the XML-RPC method and
        its parameters kama a tuple
        e.g. instance._dispatch('add',(2,3))

        If the registered instance does sio have a _dispatch method
        then the instance will be searched to find a matching method
        and, ikiwa found, will be called.

        Methods beginning ukijumuisha an '_' are considered private na will
        sio be called.
        """

        jaribu:
            # call the matching registered function
            func = self.funcs[method]
        tatizo KeyError:
            pita
        isipokua:
            ikiwa func ni sio Tupu:
                rudisha func(*params)
            ashiria Exception('method "%s" ni sio supported' % method)

        ikiwa self.instance ni sio Tupu:
            ikiwa hasattr(self.instance, '_dispatch'):
                # call the `_dispatch` method on the instance
                rudisha self.instance._dispatch(method, params)

            # call the instance's method directly
            jaribu:
                func = resolve_dotted_attribute(
                    self.instance,
                    method,
                    self.allow_dotted_names
                )
            tatizo AttributeError:
                pita
            isipokua:
                ikiwa func ni sio Tupu:
                    rudisha func(*params)

        ashiria Exception('method "%s" ni sio supported' % method)

kundi SimpleXMLRPCRequestHandler(BaseHTTPRequestHandler):
    """Simple XML-RPC request handler class.

    Handles all HTTP POST requests na attempts to decode them as
    XML-RPC requests.
    """

    # Class attribute listing the accessible path components;
    # paths sio on this list will result kwenye a 404 error.
    rpc_paths = ('/', '/RPC2')

    #ikiwa sio Tupu, encode responses larger than this, ikiwa possible
    encode_threshold = 1400 #a common MTU

    #Override form StreamRequestHandler: full buffering of output
    #and no Nagle.
    wbufsize = -1
    disable_nagle_algorithm = Kweli

    # a re to match a gzip Accept-Encoding
    aepattern = re.compile(r"""
                            \s* ([^\s;]+) \s*            #content-coding
                            (;\s* q \s*=\s* ([0-9\.]+))? #q
                            """, re.VERBOSE | re.IGNORECASE)

    eleza accept_encodings(self):
        r = {}
        ae = self.headers.get("Accept-Encoding", "")
        kila e kwenye ae.split(","):
            match = self.aepattern.match(e)
            ikiwa match:
                v = match.group(3)
                v = float(v) ikiwa v isipokua 1.0
                r[match.group(1)] = v
        rudisha r

    eleza is_rpc_path_valid(self):
        ikiwa self.rpc_paths:
            rudisha self.path kwenye self.rpc_paths
        isipokua:
            # If .rpc_paths ni empty, just assume all paths are legal
            rudisha Kweli

    eleza do_POST(self):
        """Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests kama XML-RPC calls,
        which are forwarded to the server's _dispatch method kila handling.
        """

        # Check that the path ni legal
        ikiwa sio self.is_rpc_path_valid():
            self.report_404()
            rudisha

        jaribu:
            # Get arguments by reading body of request.
            # We read this kwenye chunks to avoid straining
            # socket.read(); around the 10 ama 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10*1024*1024
            size_remaining = int(self.headers["content-length"])
            L = []
            wakati size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                chunk = self.rfile.read(chunk_size)
                ikiwa sio chunk:
                    koma
                L.append(chunk)
                size_remaining -= len(L[-1])
            data = b''.join(L)

            data = self.decode_request_content(data)
            ikiwa data ni Tupu:
                rudisha #response has been sent

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden kwenye this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see ikiwa a subkundi implements _dispatch na dispatch
            # using that method ikiwa present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', Tupu), self.path
                )
        tatizo Exception kama e: # This should only happen ikiwa the module ni buggy
            # internal error, report kama HTTP server error
            self.send_response(500)

            # Send information about the exception ikiwa requested
            ikiwa hasattr(self.server, '_send_traceback_header') na \
                    self.server._send_traceback_header:
                self.send_header("X-exception", str(e))
                trace = traceback.format_exc()
                trace = str(trace.encode('ASCII', 'backslashreplace'), 'ASCII')
                self.send_header("X-traceback", trace)

            self.send_header("Content-length", "0")
            self.end_headers()
        isipokua:
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            ikiwa self.encode_threshold ni sio Tupu:
                ikiwa len(response) > self.encode_threshold:
                    q = self.accept_encodings().get("gzip", 0)
                    ikiwa q:
                        jaribu:
                            response = gzip_encode(response)
                            self.send_header("Content-Encoding", "gzip")
                        tatizo NotImplementedError:
                            pita
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

    eleza decode_request_content(self, data):
        #support gzip encoding of request
        encoding = self.headers.get("content-encoding", "identity").lower()
        ikiwa encoding == "identity":
            rudisha data
        ikiwa encoding == "gzip":
            jaribu:
                rudisha gzip_decode(data)
            tatizo NotImplementedError:
                self.send_response(501, "encoding %r sio supported" % encoding)
            tatizo ValueError:
                self.send_response(400, "error decoding gzip content")
        isipokua:
            self.send_response(501, "encoding %r sio supported" % encoding)
        self.send_header("Content-length", "0")
        self.end_headers()

    eleza report_404 (self):
            # Report a 404 error
        self.send_response(404)
        response = b'No such page'
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    eleza log_request(self, code='-', size='-'):
        """Selectively log an accepted request."""

        ikiwa self.server.logRequests:
            BaseHTTPRequestHandler.log_request(self, code, size)

kundi SimpleXMLRPCServer(socketserver.TCPServer,
                         SimpleXMLRPCDispatcher):
    """Simple XML-RPC server.

    Simple XML-RPC server that allows functions na a single instance
    to be installed to handle requests. The default implementation
    attempts to dispatch XML-RPC calls to the functions ama instance
    installed kwenye the server. Override the _dispatch method inherited
    kutoka SimpleXMLRPCDispatcher to change this behavior.
    """

    allow_reuse_address = Kweli

    # Warning: this ni kila debugging purposes only! Never set this to Kweli in
    # production code, kama will be sending out sensitive information (exception
    # na stack trace details) when exceptions are ashiriad inside
    # SimpleXMLRPCRequestHandler.do_POST
    _send_traceback_header = Uongo

    eleza __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=Kweli, allow_none=Uongo, encoding=Tupu,
                 bind_and_activate=Kweli, use_builtin_types=Uongo):
        self.logRequests = logRequests

        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding, use_builtin_types)
        socketserver.TCPServer.__init__(self, addr, requestHandler, bind_and_activate)


kundi MultiPathXMLRPCServer(SimpleXMLRPCServer):
    """Multipath XML-RPC Server
    This specialization of SimpleXMLRPCServer allows the user to create
    multiple Dispatcher instances na assign them to different
    HTTP request paths.  This makes it possible to run two ama more
    'virtual XML-RPC servers' at the same port.
    Make sure that the requestHandler accepts the paths kwenye question.
    """
    eleza __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=Kweli, allow_none=Uongo, encoding=Tupu,
                 bind_and_activate=Kweli, use_builtin_types=Uongo):

        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests, allow_none,
                                    encoding, bind_and_activate, use_builtin_types)
        self.dispatchers = {}
        self.allow_none = allow_none
        self.encoding = encoding ama 'utf-8'

    eleza add_dispatcher(self, path, dispatcher):
        self.dispatchers[path] = dispatcher
        rudisha dispatcher

    eleza get_dispatcher(self, path):
        rudisha self.dispatchers[path]

    eleza _marshaled_dispatch(self, data, dispatch_method = Tupu, path = Tupu):
        jaribu:
            response = self.dispatchers[path]._marshaled_dispatch(
               data, dispatch_method, path)
        except:
            # report low level exception back to server
            # (each dispatcher should have handled their own
            # exceptions)
            exc_type, exc_value = sys.exc_info()[:2]
            jaribu:
                response = dumps(
                    Fault(1, "%s:%s" % (exc_type, exc_value)),
                    encoding=self.encoding, allow_none=self.allow_none)
                response = response.encode(self.encoding, 'xmlcharrefreplace')
            mwishowe:
                # Break reference cycle
                exc_type = exc_value = Tupu
        rudisha response

kundi CGIXMLRPCRequestHandler(SimpleXMLRPCDispatcher):
    """Simple handler kila XML-RPC data pitaed through CGI."""

    eleza __init__(self, allow_none=Uongo, encoding=Tupu, use_builtin_types=Uongo):
        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding, use_builtin_types)

    eleza handle_xmlrpc(self, request_text):
        """Handle a single XML-RPC request"""

        response = self._marshaled_dispatch(request_text)

        andika('Content-Type: text/xml')
        andika('Content-Length: %d' % len(response))
        andika()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    eleza handle_get(self):
        """Handle a single HTTP GET request.

        Default implementation indicates an error because
        XML-RPC uses the POST method.
        """

        code = 400
        message, explain = BaseHTTPRequestHandler.responses[code]

        response = http.server.DEFAULT_ERROR_MESSAGE % \
            {
             'code' : code,
             'message' : message,
             'explain' : explain
            }
        response = response.encode('utf-8')
        andika('Status: %d %s' % (code, message))
        andika('Content-Type: %s' % http.server.DEFAULT_ERROR_CONTENT_TYPE)
        andika('Content-Length: %d' % len(response))
        andika()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    eleza handle_request(self, request_text=Tupu):
        """Handle a single XML-RPC request pitaed through a CGI post method.

        If no XML data ni given then it ni read kutoka stdin. The resulting
        XML-RPC response ni printed to stdout along ukijumuisha the correct HTTP
        headers.
        """

        ikiwa request_text ni Tupu na \
            os.environ.get('REQUEST_METHOD', Tupu) == 'GET':
            self.handle_get()
        isipokua:
            # POST data ni normally available through stdin
            jaribu:
                length = int(os.environ.get('CONTENT_LENGTH', Tupu))
            tatizo (ValueError, TypeError):
                length = -1
            ikiwa request_text ni Tupu:
                request_text = sys.stdin.read(length)

            self.handle_xmlrpc(request_text)


# -----------------------------------------------------------------------------
# Self documenting XML-RPC Server.

kundi ServerHTMLDoc(pydoc.HTMLDoc):
    """Class used to generate pydoc HTML document kila a server"""

    eleza markup(self, text, escape=Tupu, funcs={}, classes={}, methods={}):
        """Mark up some plain text, given a context of symbols to look for.
        Each context dictionary maps object names to anchor names."""
        escape = escape ama self.escape
        results = []
        here = 0

        # XXX Note that this regular expression does sio allow kila the
        # hyperlinking of arbitrary strings being used kama method
        # names. Only methods ukijumuisha names consisting of word characters
        # na '.'s are hyperlinked.
        pattern = re.compile(r'\b((http|ftp)://\S+[\w/]|'
                                r'RFC[- ]?(\d+)|'
                                r'PEP[- ]?(\d+)|'
                                r'(self\.)?((?:\w|\.)+))\b')
        wakati 1:
            match = pattern.search(text, here)
            ikiwa sio match: koma
            start, end = match.span()
            results.append(escape(text[here:start]))

            all, scheme, rfc, pep, selfdot, name = match.groups()
            ikiwa scheme:
                url = escape(all).replace('"', '&quot;')
                results.append('<a href="%s">%s</a>' % (url, url))
            lasivyo rfc:
                url = 'http://www.rfc-editor.org/rfc/rfc%d.txt' % int(rfc)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            lasivyo pep:
                url = 'http://www.python.org/dev/peps/pep-%04d/' % int(pep)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            lasivyo text[end:end+1] == '(':
                results.append(self.namelink(name, methods, funcs, classes))
            lasivyo selfdot:
                results.append('self.<strong>%s</strong>' % name)
            isipokua:
                results.append(self.namelink(name, classes))
            here = end
        results.append(escape(text[here:]))
        rudisha ''.join(results)

    eleza docroutine(self, object, name, mod=Tupu,
                   funcs={}, classes={}, methods={}, cl=Tupu):
        """Produce HTML documentation kila a function ama method object."""

        anchor = (cl na cl.__name__ ama '') + '-' + name
        note = ''

        title = '<a name="%s"><strong>%s</strong></a>' % (
            self.escape(anchor), self.escape(name))

        ikiwa callable(object):
            argspec = str(signature(object))
        isipokua:
            argspec = '(...)'

        ikiwa isinstance(object, tuple):
            argspec = object[0] ama argspec
            docstring = object[1] ama ""
        isipokua:
            docstring = pydoc.getdoc(object)

        decl = title + argspec + (note na self.grey(
               '<font face="helvetica, arial">%s</font>' % note))

        doc = self.markup(
            docstring, self.preformat, funcs, classes, methods)
        doc = doc na '<dd><tt>%s</tt></dd>' % doc
        rudisha '<dl><dt>%s</dt>%s</dl>\n' % (decl, doc)

    eleza docserver(self, server_name, package_documentation, methods):
        """Produce HTML documentation kila an XML-RPC server."""

        fdict = {}
        kila key, value kwenye methods.items():
            fdict[key] = '#-' + key
            fdict[value] = fdict[key]

        server_name = self.escape(server_name)
        head = '<big><big><strong>%s</strong></big></big>' % server_name
        result = self.heading(head, '#ffffff', '#7799ee')

        doc = self.markup(package_documentation, self.preformat, fdict)
        doc = doc na '<tt>%s</tt>' % doc
        result = result + '<p>%s</p>\n' % doc

        contents = []
        method_items = sorted(methods.items())
        kila key, value kwenye method_items:
            contents.append(self.docroutine(value, key, funcs=fdict))
        result = result + self.bigsection(
            'Methods', '#ffffff', '#eeaa77', ''.join(contents))

        rudisha result

kundi XMLRPCDocGenerator:
    """Generates documentation kila an XML-RPC server.

    This kundi ni designed kama mix-in na should not
    be constructed directly.
    """

    eleza __init__(self):
        # setup variables used kila HTML documentation
        self.server_name = 'XML-RPC Server Documentation'
        self.server_documentation = \
            "This server exports the following methods through the XML-RPC "\
            "protocol."
        self.server_title = 'XML-RPC Server Documentation'

    eleza set_server_title(self, server_title):
        """Set the HTML title of the generated server documentation"""

        self.server_title = server_title

    eleza set_server_name(self, server_name):
        """Set the name of the generated HTML server documentation"""

        self.server_name = server_name

    eleza set_server_documentation(self, server_documentation):
        """Set the documentation string kila the entire server."""

        self.server_documentation = server_documentation

    eleza generate_html_documentation(self):
        """generate_html_documentation() => html documentation kila the server

        Generates HTML documentation kila the server using introspection for
        installed functions na instances that do sio implement the
        _dispatch method. Alternatively, instances can choose to implement
        the _get_method_argstring(method_name) method to provide the
        argument string used kwenye the documentation na the
        _methodHelp(method_name) method to provide the help text used
        kwenye the documentation."""

        methods = {}

        kila method_name kwenye self.system_listMethods():
            ikiwa method_name kwenye self.funcs:
                method = self.funcs[method_name]
            lasivyo self.instance ni sio Tupu:
                method_info = [Tupu, Tupu] # argspec, documentation
                ikiwa hasattr(self.instance, '_get_method_argstring'):
                    method_info[0] = self.instance._get_method_argstring(method_name)
                ikiwa hasattr(self.instance, '_methodHelp'):
                    method_info[1] = self.instance._methodHelp(method_name)

                method_info = tuple(method_info)
                ikiwa method_info != (Tupu, Tupu):
                    method = method_info
                lasivyo sio hasattr(self.instance, '_dispatch'):
                    jaribu:
                        method = resolve_dotted_attribute(
                                    self.instance,
                                    method_name
                                    )
                    tatizo AttributeError:
                        method = method_info
                isipokua:
                    method = method_info
            isipokua:
                assert 0, "Could sio find method kwenye self.functions na no "\
                          "instance installed"

            methods[method_name] = method

        documenter = ServerHTMLDoc()
        documentation = documenter.docserver(
                                self.server_name,
                                self.server_documentation,
                                methods
                            )

        rudisha documenter.page(html.escape(self.server_title), documentation)

kundi DocXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """XML-RPC na documentation request handler class.

    Handles all HTTP POST requests na attempts to decode them as
    XML-RPC requests.

    Handles all HTTP GET requests na interprets them kama requests
    kila documentation.
    """

    eleza do_GET(self):
        """Handles the HTTP GET request.

        Interpret all HTTP GET requests kama requests kila server
        documentation.
        """
        # Check that the path ni legal
        ikiwa sio self.is_rpc_path_valid():
            self.report_404()
            rudisha

        response = self.server.generate_html_documentation().encode('utf-8')
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

kundi DocXMLRPCServer(  SimpleXMLRPCServer,
                        XMLRPCDocGenerator):
    """XML-RPC na HTML documentation server.

    Adds the ability to serve server documentation to the capabilities
    of SimpleXMLRPCServer.
    """

    eleza __init__(self, addr, requestHandler=DocXMLRPCRequestHandler,
                 logRequests=Kweli, allow_none=Uongo, encoding=Tupu,
                 bind_and_activate=Kweli, use_builtin_types=Uongo):
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests,
                                    allow_none, encoding, bind_and_activate,
                                    use_builtin_types)
        XMLRPCDocGenerator.__init__(self)

kundi DocCGIXMLRPCRequestHandler(   CGIXMLRPCRequestHandler,
                                    XMLRPCDocGenerator):
    """Handler kila XML-RPC data na documentation requests pitaed through
    CGI"""

    eleza handle_get(self):
        """Handles the HTTP GET request.

        Interpret all HTTP GET requests kama requests kila server
        documentation.
        """

        response = self.generate_html_documentation().encode('utf-8')

        andika('Content-Type: text/html')
        andika('Content-Length: %d' % len(response))
        andika()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    eleza __init__(self):
        CGIXMLRPCRequestHandler.__init__(self)
        XMLRPCDocGenerator.__init__(self)


ikiwa __name__ == '__main__':
    agiza datetime

    kundi ExampleService:
        eleza getData(self):
            rudisha '42'

        kundi currentTime:
            @staticmethod
            eleza getCurrentTime():
                rudisha datetime.datetime.now()

    ukijumuisha SimpleXMLRPCServer(("localhost", 8000)) kama server:
        server.register_function(pow)
        server.register_function(lambda x,y: x+y, 'add')
        server.register_instance(ExampleService(), allow_dotted_names=Kweli)
        server.register_multicall_functions()
        andika('Serving XML-RPC on localhost port 8000')
        andika('It ni advisable to run this example server within a secure, closed network.')
        jaribu:
            server.serve_forever()
        tatizo KeyboardInterrupt:
            andika("\nKeyboard interrupt received, exiting.")
            sys.exit(0)
