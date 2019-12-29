kutoka xmlrpc.server agiza DocXMLRPCServer
agiza http.client
agiza re
agiza sys
agiza threading
agiza unittest

eleza make_request_and_skipIf(condition, reason):
    # If we skip the test, we have to make a request because
    # the server created kwenye setUp blocks expecting one to come in.
    ikiwa sio condition:
        rudisha lambda func: func
    eleza decorator(func):
        eleza make_request_and_skip(self):
            self.client.request("GET", "/")
            self.client.getresponse()
            ashiria unittest.SkipTest(reason)
        rudisha make_request_and_skip
    rudisha decorator


eleza make_server():
    serv = DocXMLRPCServer(("localhost", 0), logRequests=Uongo)

    jaribu:
        # Add some documentation
        serv.set_server_title("DocXMLRPCServer Test Documentation")
        serv.set_server_name("DocXMLRPCServer Test Docs")
        serv.set_server_documentation(
            "This ni an XML-RPC server's documentation, but the server "
            "can be used by POSTing to /RPC2. Try self.add, too.")

        # Create na register classes na functions
        kundi TestClass(object):
            eleza test_method(self, arg):
                """Test method's docs. This method truly does very little."""
                self.arg = arg

        serv.register_introspection_functions()
        serv.register_instance(TestClass())

        eleza add(x, y):
            """Add two instances together. This follows PEP008, but has nothing
            to do ukijumuisha RFC1952. Case should matter: pEp008 na rFC1952.  Things
            that start ukijumuisha http na ftp should be auto-linked, too:
            http://google.com.
            """
            rudisha x + y

        eleza annotation(x: int):
            """ Use function annotations. """
            rudisha x

        kundi ClassWithAnnotation:
            eleza method_annotation(self, x: bytes):
                rudisha x.decode()

        serv.register_function(add)
        serv.register_function(lambda x, y: x-y)
        serv.register_function(annotation)
        serv.register_instance(ClassWithAnnotation())
        rudisha serv
    except:
        serv.server_close()
        ashiria

kundi DocXMLRPCHTTPGETServer(unittest.TestCase):
    eleza setUp(self):
        # Enable server feedback
        DocXMLRPCServer._send_traceback_header = Kweli

        self.serv = make_server()
        self.thread = threading.Thread(target=self.serv.serve_forever)
        self.thread.start()

        PORT = self.serv.server_address[1]
        self.client = http.client.HTTPConnection("localhost:%d" % PORT)

    eleza tearDown(self):
        self.client.close()

        # Disable server feedback
        DocXMLRPCServer._send_traceback_header = Uongo
        self.serv.shutdown()
        self.thread.join()
        self.serv.server_close()

    eleza test_valid_get_response(self):
        self.client.request("GET", "/")
        response = self.client.getresponse()

        self.assertEqual(response.status, 200)
        self.assertEqual(response.getheader("Content-type"), "text/html")

        # Server ashirias an exception ikiwa we don't start to read the data
        response.read()

    eleza test_invalid_get_response(self):
        self.client.request("GET", "/spam")
        response = self.client.getresponse()

        self.assertEqual(response.status, 404)
        self.assertEqual(response.getheader("Content-type"), "text/plain")

        response.read()

    eleza test_lambda(self):
        """Test that lambda functionality stays the same.  The output produced
        currently is, I suspect invalid because of the unencoded brackets kwenye the
        HTML, "<lambda>".

        The subtraction lambda method ni tested.
        """
        self.client.request("GET", "/")
        response = self.client.getresponse()

        self.assertIn((b'<dl><dt><a name="-&lt;lambda&gt;"><strong>'
                       b'&lt;lambda&gt;</strong></a>(x, y)</dt></dl>'),
                      response.read())

    @make_request_and_skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_autolinking(self):
        """Test that the server correctly automatically wraps references to
        PEPS na RFCs ukijumuisha links, na that it linkifies text starting with
        http ama ftp protocol prefixes.

        The documentation kila the "add" method contains the test material.
        """
        self.client.request("GET", "/")
        response = self.client.getresponse().read()

        self.assertIn(
            (b'<dl><dt><a name="-add"><strong>add</strong></a>(x, y)</dt><dd>'
             b'<tt>Add&nbsp;two&nbsp;instances&nbsp;together.&nbsp;This&nbsp;'
             b'follows&nbsp;<a href="http://www.python.org/dev/peps/pep-0008/">'
             b'PEP008</a>,&nbsp;but&nbsp;has&nbsp;nothing<br>\nto&nbsp;do&nbsp;'
             b'with&nbsp;<a href="http://www.rfc-editor.org/rfc/rfc1952.txt">'
             b'RFC1952</a>.&nbsp;Case&nbsp;should&nbsp;matter:&nbsp;pEp008&nbsp;'
             b'and&nbsp;rFC1952.&nbsp;&nbsp;Things<br>\nthat&nbsp;start&nbsp;'
             b'with&nbsp;http&nbsp;and&nbsp;ftp&nbsp;should&nbsp;be&nbsp;'
             b'auto-linked,&nbsp;too:<br>\n<a href="http://google.com">'
             b'http://google.com</a>.</tt></dd></dl>'), response)

    @make_request_and_skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_system_methods(self):
        """Test the presence of three consecutive system.* methods.

        This also tests their use of parameter type recognition na the
        systems related to that process.
        """
        self.client.request("GET", "/")
        response = self.client.getresponse().read()

        self.assertIn(
            (b'<dl><dt><a name="-system.methodHelp"><strong>system.methodHelp'
             b'</strong></a>(method_name)</dt><dd><tt><a href="#-system.method'
             b'Help">system.methodHelp</a>(\'add\')&nbsp;=&gt;&nbsp;"Adds&nbsp;'
             b'two&nbsp;integers&nbsp;together"<br>\n&nbsp;<br>\nReturns&nbsp;a'
             b'&nbsp;string&nbsp;containing&nbsp;documentation&nbsp;for&nbsp;'
             b'the&nbsp;specified&nbsp;method.</tt></dd></dl>\n<dl><dt><a name'
             b'="-system.methodSignature"><strong>system.methodSignature</strong>'
             b'</a>(method_name)</dt><dd><tt><a href="#-system.methodSignature">'
             b'system.methodSignature</a>(\'add\')&nbsp;=&gt;&nbsp;[double,&nbsp;'
             b'int,&nbsp;int]<br>\n&nbsp;<br>\nReturns&nbsp;a&nbsp;list&nbsp;'
             b'describing&nbsp;the&nbsp;signature&nbsp;of&nbsp;the&nbsp;method.'
             b'&nbsp;In&nbsp;the<br>\nabove&nbsp;example,&nbsp;the&nbsp;add&nbsp;'
             b'method&nbsp;takes&nbsp;two&nbsp;integers&nbsp;as&nbsp;arguments'
             b'<br>\nand&nbsp;rudishas&nbsp;a&nbsp;double&nbsp;result.<br>\n&nbsp;'
             b'<br>\nThis&nbsp;server&nbsp;does&nbsp;NOT&nbsp;support&nbsp;system'
             b'.methodSignature.</tt></dd></dl>'), response)

    eleza test_autolink_dotted_methods(self):
        """Test that selfdot values are made strong automatically kwenye the
        documentation."""
        self.client.request("GET", "/")
        response = self.client.getresponse()

        self.assertIn(b"""Try&nbsp;self.<strong>add</strong>,&nbsp;too.""",
                      response.read())

    eleza test_annotations(self):
        """ Test that annotations works kama expected """
        self.client.request("GET", "/")
        response = self.client.getresponse()
        docstring = (b'' ikiwa sys.flags.optimize >= 2 else
                     b'<dd><tt>Use&nbsp;function&nbsp;annotations.</tt></dd>')
        self.assertIn(
            (b'<dl><dt><a name="-annotation"><strong>annotation</strong></a>'
             b'(x: int)</dt>' + docstring + b'</dl>\n'
             b'<dl><dt><a name="-method_annotation"><strong>'
             b'method_annotation</strong></a>(x: bytes)</dt></dl>'),
            response.read())

    eleza test_server_title_escape(self):
        # bpo-38243: Ensure that the server title na documentation
        # are escaped kila HTML.
        self.serv.set_server_title('test_title<script>')
        self.serv.set_server_documentation('test_documentation<script>')
        self.assertEqual('test_title<script>', self.serv.server_title)
        self.assertEqual('test_documentation<script>',
                self.serv.server_documentation)

        generated = self.serv.generate_html_documentation()
        title = re.search(r'<title>(.+?)</title>', generated).group()
        documentation = re.search(r'<p><tt>(.+?)</tt></p>', generated).group()
        self.assertEqual('<title>Python: test_title&lt;script&gt;</title>', title)
        self.assertEqual('<p><tt>test_documentation&lt;script&gt;</tt></p>', documentation)


ikiwa __name__ == '__main__':
    unittest.main()
