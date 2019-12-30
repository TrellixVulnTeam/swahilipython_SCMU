agiza base64
agiza datetime
agiza decimal
agiza sys
agiza time
agiza unittest
kutoka unittest agiza mock
agiza xmlrpc.client kama xmlrpclib
agiza xmlrpc.server
agiza http.client
agiza http, http.server
agiza socket
agiza threading
agiza re
agiza io
agiza contextlib
kutoka test agiza support

jaribu:
    agiza gzip
tatizo ImportError:
    gzip = Tupu

alist = [{'astring': 'foo@bar.baz.spam',
          'afloat': 7283.43,
          'anint': 2**20,
          'ashortlong': 2,
          'anotherlist': ['.zyx.41'],
          'abase64': xmlrpclib.Binary(b"my dog has fleas"),
          'b64bytes': b"my dog has fleas",
          'b64bytearray': bytearray(b"my dog has fleas"),
          'boolean': Uongo,
          'unicode': '\u4000\u6000\u8000',
          'ukey\u4000': 'regular value',
          'datetime1': xmlrpclib.DateTime('20050210T11:41:23'),
          'datetime2': xmlrpclib.DateTime(
                        (2005, 2, 10, 11, 41, 23, 0, 1, -1)),
          'datetime3': xmlrpclib.DateTime(
                        datetime.datetime(2005, 2, 10, 11, 41, 23)),
          }]

kundi XMLRPCTestCase(unittest.TestCase):

    eleza test_dump_load(self):
        dump = xmlrpclib.dumps((alist,))
        load = xmlrpclib.loads(dump)
        self.assertEqual(alist, load[0][0])

    eleza test_dump_bare_datetime(self):
        # This checks that an unwrapped datetime.date object can be handled
        # by the marshalling code.  This can't be done via test_dump_load()
        # since ukijumuisha use_builtin_types set to 1 the unmarshaller would create
        # datetime objects kila the 'datetime[123]' keys kama well
        dt = datetime.datetime(2005, 2, 10, 11, 41, 23)
        self.assertEqual(dt, xmlrpclib.DateTime('20050210T11:41:23'))
        s = xmlrpclib.dumps((dt,))

        result, m = xmlrpclib.loads(s, use_builtin_types=Kweli)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), datetime.datetime)
        self.assertIsTupu(m)

        result, m = xmlrpclib.loads(s, use_builtin_types=Uongo)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), xmlrpclib.DateTime)
        self.assertIsTupu(m)

        result, m = xmlrpclib.loads(s, use_datetime=Kweli)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), datetime.datetime)
        self.assertIsTupu(m)

        result, m = xmlrpclib.loads(s, use_datetime=Uongo)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), xmlrpclib.DateTime)
        self.assertIsTupu(m)


    eleza test_datetime_before_1900(self):
        # same kama before but ukijumuisha a date before 1900
        dt = datetime.datetime(1,  2, 10, 11, 41, 23)
        self.assertEqual(dt, xmlrpclib.DateTime('00010210T11:41:23'))
        s = xmlrpclib.dumps((dt,))

        result, m = xmlrpclib.loads(s, use_builtin_types=Kweli)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), datetime.datetime)
        self.assertIsTupu(m)

        result, m = xmlrpclib.loads(s, use_builtin_types=Uongo)
        (newdt,) = result
        self.assertEqual(newdt, dt)
        self.assertIs(type(newdt), xmlrpclib.DateTime)
        self.assertIsTupu(m)

    eleza test_bug_1164912 (self):
        d = xmlrpclib.DateTime()
        ((new_d,), dummy) = xmlrpclib.loads(xmlrpclib.dumps((d,),
                                            methodresponse=Kweli))
        self.assertIsInstance(new_d.value, str)

        # Check that the output of dumps() ni still an 8-bit string
        s = xmlrpclib.dumps((new_d,), methodresponse=Kweli)
        self.assertIsInstance(s, str)

    eleza test_newstyle_class(self):
        kundi T(object):
            pita
        t = T()
        t.x = 100
        t.y = "Hello"
        ((t2,), dummy) = xmlrpclib.loads(xmlrpclib.dumps((t,)))
        self.assertEqual(t2, t.__dict__)

    eleza test_dump_big_long(self):
        self.assertRaises(OverflowError, xmlrpclib.dumps, (2**99,))

    eleza test_dump_bad_dict(self):
        self.assertRaises(TypeError, xmlrpclib.dumps, ({(1,2,3): 1},))

    eleza test_dump_recursive_seq(self):
        l = [1,2,3]
        t = [3,4,5,l]
        l.append(t)
        self.assertRaises(TypeError, xmlrpclib.dumps, (l,))

    eleza test_dump_recursive_dict(self):
        d = {'1':1, '2':1}
        t = {'3':3, 'd':d}
        d['t'] = t
        self.assertRaises(TypeError, xmlrpclib.dumps, (d,))

    eleza test_dump_big_int(self):
        ikiwa sys.maxsize > 2**31-1:
            self.assertRaises(OverflowError, xmlrpclib.dumps,
                              (int(2**34),))

        xmlrpclib.dumps((xmlrpclib.MAXINT, xmlrpclib.MININT))
        self.assertRaises(OverflowError, xmlrpclib.dumps,
                          (xmlrpclib.MAXINT+1,))
        self.assertRaises(OverflowError, xmlrpclib.dumps,
                          (xmlrpclib.MININT-1,))

        eleza dummy_write(s):
            pita

        m = xmlrpclib.Marshaller()
        m.dump_int(xmlrpclib.MAXINT, dummy_write)
        m.dump_int(xmlrpclib.MININT, dummy_write)
        self.assertRaises(OverflowError, m.dump_int,
                          xmlrpclib.MAXINT+1, dummy_write)
        self.assertRaises(OverflowError, m.dump_int,
                          xmlrpclib.MININT-1, dummy_write)

    eleza test_dump_double(self):
        xmlrpclib.dumps((float(2 ** 34),))
        xmlrpclib.dumps((float(xmlrpclib.MAXINT),
                         float(xmlrpclib.MININT)))
        xmlrpclib.dumps((float(xmlrpclib.MAXINT + 42),
                         float(xmlrpclib.MININT - 42)))

        eleza dummy_write(s):
            pita

        m = xmlrpclib.Marshaller()
        m.dump_double(xmlrpclib.MAXINT, dummy_write)
        m.dump_double(xmlrpclib.MININT, dummy_write)
        m.dump_double(xmlrpclib.MAXINT + 42, dummy_write)
        m.dump_double(xmlrpclib.MININT - 42, dummy_write)

    eleza test_dump_none(self):
        value = alist + [Tupu]
        arg1 = (alist + [Tupu],)
        strg = xmlrpclib.dumps(arg1, allow_none=Kweli)
        self.assertEqual(value,
                          xmlrpclib.loads(strg)[0][0])
        self.assertRaises(TypeError, xmlrpclib.dumps, (arg1,))

    eleza test_dump_encoding(self):
        value = {'key\u20ac\xa4':
                 'value\u20ac\xa4'}
        strg = xmlrpclib.dumps((value,), encoding='iso-8859-15')
        strg = "<?xml version='1.0' encoding='iso-8859-15'?>" + strg
        self.assertEqual(xmlrpclib.loads(strg)[0][0], value)
        strg = strg.encode('iso-8859-15', 'xmlcharrefreplace')
        self.assertEqual(xmlrpclib.loads(strg)[0][0], value)

        strg = xmlrpclib.dumps((value,), encoding='iso-8859-15',
                               methodresponse=Kweli)
        self.assertEqual(xmlrpclib.loads(strg)[0][0], value)
        strg = strg.encode('iso-8859-15', 'xmlcharrefreplace')
        self.assertEqual(xmlrpclib.loads(strg)[0][0], value)

        methodname = 'method\u20ac\xa4'
        strg = xmlrpclib.dumps((value,), encoding='iso-8859-15',
                               methodname=methodname)
        self.assertEqual(xmlrpclib.loads(strg)[0][0], value)
        self.assertEqual(xmlrpclib.loads(strg)[1], methodname)

    eleza test_dump_bytes(self):
        sample = b"my dog has fleas"
        self.assertEqual(sample, xmlrpclib.Binary(sample))
        kila type_ kwenye bytes, bytearray, xmlrpclib.Binary:
            value = type_(sample)
            s = xmlrpclib.dumps((value,))

            result, m = xmlrpclib.loads(s, use_builtin_types=Kweli)
            (newvalue,) = result
            self.assertEqual(newvalue, sample)
            self.assertIs(type(newvalue), bytes)
            self.assertIsTupu(m)

            result, m = xmlrpclib.loads(s, use_builtin_types=Uongo)
            (newvalue,) = result
            self.assertEqual(newvalue, sample)
            self.assertIs(type(newvalue), xmlrpclib.Binary)
            self.assertIsTupu(m)

    eleza test_loads_unsupported(self):
        ResponseError = xmlrpclib.ResponseError
        data = '<params><param><value><spam/></value></param></params>'
        self.assertRaises(ResponseError, xmlrpclib.loads, data)
        data = ('<params><param><value><array>'
                '<value><spam/></value>'
                '</array></value></param></params>')
        self.assertRaises(ResponseError, xmlrpclib.loads, data)
        data = ('<params><param><value><struct>'
                '<member><name>a</name><value><spam/></value></member>'
                '<member><name>b</name><value><spam/></value></member>'
                '</struct></value></param></params>')
        self.assertRaises(ResponseError, xmlrpclib.loads, data)

    eleza check_loads(self, s, value, **kwargs):
        dump = '<params><param><value>%s</value></param></params>' % s
        result, m = xmlrpclib.loads(dump, **kwargs)
        (newvalue,) = result
        self.assertEqual(newvalue, value)
        self.assertIs(type(newvalue), type(value))
        self.assertIsTupu(m)

    eleza test_load_standard_types(self):
        check = self.check_loads
        check('string', 'string')
        check('<string>string</string>', 'string')
        check('<string>𝔘𝔫𝔦𝔠𝔬𝔡𝔢 string</string>', '𝔘𝔫𝔦𝔠𝔬𝔡𝔢 string')
        check('<int>2056183947</int>', 2056183947)
        check('<int>-2056183947</int>', -2056183947)
        check('<i4>2056183947</i4>', 2056183947)
        check('<double>46093.78125</double>', 46093.78125)
        check('<boolean>0</boolean>', Uongo)
        check('<base64>AGJ5dGUgc3RyaW5n/w==</base64>',
              xmlrpclib.Binary(b'\x00byte string\xff'))
        check('<base64>AGJ5dGUgc3RyaW5n/w==</base64>',
              b'\x00byte string\xff', use_builtin_types=Kweli)
        check('<dateTime.iso8601>20050210T11:41:23</dateTime.iso8601>',
              xmlrpclib.DateTime('20050210T11:41:23'))
        check('<dateTime.iso8601>20050210T11:41:23</dateTime.iso8601>',
              datetime.datetime(2005, 2, 10, 11, 41, 23),
              use_builtin_types=Kweli)
        check('<array><data>'
              '<value><int>1</int></value><value><int>2</int></value>'
              '</data></array>', [1, 2])
        check('<struct>'
              '<member><name>b</name><value><int>2</int></value></member>'
              '<member><name>a</name><value><int>1</int></value></member>'
              '</struct>', {'a': 1, 'b': 2})

    eleza test_load_extension_types(self):
        check = self.check_loads
        check('<nil/>', Tupu)
        check('<ex:nil/>', Tupu)
        check('<i1>205</i1>', 205)
        check('<i2>20561</i2>', 20561)
        check('<i8>9876543210</i8>', 9876543210)
        check('<biginteger>98765432100123456789</biginteger>',
              98765432100123456789)
        check('<float>93.78125</float>', 93.78125)
        check('<bigdecimal>9876543210.0123456789</bigdecimal>',
              decimal.Decimal('9876543210.0123456789'))

    eleza test_get_host_info(self):
        # see bug #3613, this raised a TypeError
        transp = xmlrpc.client.Transport()
        self.assertEqual(transp.get_host_info("user@host.tld"),
                          ('host.tld',
                           [('Authorization', 'Basic dXNlcg==')], {}))

    eleza test_ssl_presence(self):
        jaribu:
            agiza ssl
        tatizo ImportError:
            has_ssl = Uongo
        isipokua:
            has_ssl = Kweli
        jaribu:
            xmlrpc.client.ServerProxy('https://localhost:9999').bad_function()
        tatizo NotImplementedError:
            self.assertUongo(has_ssl, "xmlrpc client's error ukijumuisha SSL support")
        tatizo OSError:
            self.assertKweli(has_ssl)

    eleza test_keepalive_disconnect(self):
        kundi RequestHandler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"
            handled = Uongo

            eleza do_POST(self):
                length = int(self.headers.get("Content-Length"))
                self.rfile.read(length)
                ikiwa self.handled:
                    self.close_connection = Kweli
                    rudisha
                response = xmlrpclib.dumps((5,), methodresponse=Kweli)
                response = response.encode()
                self.send_response(http.HTTPStatus.OK)
                self.send_header("Content-Length", len(response))
                self.end_headers()
                self.wfile.write(response)
                self.handled = Kweli
                self.close_connection = Uongo

            eleza log_message(self, format, *args):
                # don't clobber sys.stderr
                pita

        eleza run_server():
            server.socket.settimeout(float(1))  # Don't hang ikiwa client fails
            server.handle_request()  # First request na attempt at second
            server.handle_request()  # Retried second request

        server = http.server.HTTPServer((support.HOST, 0), RequestHandler)
        self.addCleanup(server.server_close)
        thread = threading.Thread(target=run_server)
        thread.start()
        self.addCleanup(thread.join)
        url = "http://{}:{}/".format(*server.server_address)
        ukijumuisha xmlrpclib.ServerProxy(url) kama p:
            self.assertEqual(p.method(), 5)
            self.assertEqual(p.method(), 5)


kundi SimpleXMLRPCDispatcherTestCase(unittest.TestCase):
    kundi DispatchExc(Exception):
        """Raised inside the dispatched functions when checking for
        chained exceptions"""

    eleza test_call_registered_func(self):
        """Calls explicitly registered function"""
        # Makes sure any exception raised inside the function has no other
        # exception chained to it

        exp_params = 1, 2, 3

        eleza dispatched_func(*params):
            ashiria self.DispatchExc(params)

        dispatcher = xmlrpc.server.SimpleXMLRPCDispatcher()
        dispatcher.register_function(dispatched_func)
        ukijumuisha self.assertRaises(self.DispatchExc) kama exc_ctx:
            dispatcher._dispatch('dispatched_func', exp_params)
        self.assertEqual(exc_ctx.exception.args, (exp_params,))
        self.assertIsTupu(exc_ctx.exception.__cause__)
        self.assertIsTupu(exc_ctx.exception.__context__)

    eleza test_call_instance_func(self):
        """Calls a registered instance attribute kama a function"""
        # Makes sure any exception raised inside the function has no other
        # exception chained to it

        exp_params = 1, 2, 3

        kundi DispatchedClass:
            eleza dispatched_func(self, *params):
                ashiria SimpleXMLRPCDispatcherTestCase.DispatchExc(params)

        dispatcher = xmlrpc.server.SimpleXMLRPCDispatcher()
        dispatcher.register_instance(DispatchedClass())
        ukijumuisha self.assertRaises(self.DispatchExc) kama exc_ctx:
            dispatcher._dispatch('dispatched_func', exp_params)
        self.assertEqual(exc_ctx.exception.args, (exp_params,))
        self.assertIsTupu(exc_ctx.exception.__cause__)
        self.assertIsTupu(exc_ctx.exception.__context__)

    eleza test_call_dispatch_func(self):
        """Calls the registered instance's `_dispatch` function"""
        # Makes sure any exception raised inside the function has no other
        # exception chained to it

        exp_method = 'method'
        exp_params = 1, 2, 3

        kundi TestInstance:
            eleza _dispatch(self, method, params):
                ashiria SimpleXMLRPCDispatcherTestCase.DispatchExc(
                    method, params)

        dispatcher = xmlrpc.server.SimpleXMLRPCDispatcher()
        dispatcher.register_instance(TestInstance())
        ukijumuisha self.assertRaises(self.DispatchExc) kama exc_ctx:
            dispatcher._dispatch(exp_method, exp_params)
        self.assertEqual(exc_ctx.exception.args, (exp_method, exp_params))
        self.assertIsTupu(exc_ctx.exception.__cause__)
        self.assertIsTupu(exc_ctx.exception.__context__)

    eleza test_registered_func_is_none(self):
        """Calls explicitly registered function which ni Tupu"""

        dispatcher = xmlrpc.server.SimpleXMLRPCDispatcher()
        dispatcher.register_function(Tupu, name='method')
        ukijumuisha self.assertRaisesRegex(Exception, 'method'):
            dispatcher._dispatch('method', ('param',))

    eleza test_instance_has_no_func(self):
        """Attempts to call nonexistent function on a registered instance"""

        dispatcher = xmlrpc.server.SimpleXMLRPCDispatcher()
        dispatcher.register_instance(object())
        ukijumuisha self.assertRaisesRegex(Exception, 'method'):
            dispatcher._dispatch('method', ('param',))

    eleza test_cannot_locate_func(self):
        """Calls a function that the dispatcher cannot locate"""

        dispatcher = xmlrpc.server.SimpleXMLRPCDispatcher()
        ukijumuisha self.assertRaisesRegex(Exception, 'method'):
            dispatcher._dispatch('method', ('param',))


kundi HelperTestCase(unittest.TestCase):
    eleza test_escape(self):
        self.assertEqual(xmlrpclib.escape("a&b"), "a&amp;b")
        self.assertEqual(xmlrpclib.escape("a<b"), "a&lt;b")
        self.assertEqual(xmlrpclib.escape("a>b"), "a&gt;b")

kundi FaultTestCase(unittest.TestCase):
    eleza test_repr(self):
        f = xmlrpclib.Fault(42, 'Test Fault')
        self.assertEqual(repr(f), "<Fault 42: 'Test Fault'>")
        self.assertEqual(repr(f), str(f))

    eleza test_dump_fault(self):
        f = xmlrpclib.Fault(42, 'Test Fault')
        s = xmlrpclib.dumps((f,))
        (newf,), m = xmlrpclib.loads(s)
        self.assertEqual(newf, {'faultCode': 42, 'faultString': 'Test Fault'})
        self.assertEqual(m, Tupu)

        s = xmlrpclib.Marshaller().dumps(f)
        self.assertRaises(xmlrpclib.Fault, xmlrpclib.loads, s)

    eleza test_dotted_attribute(self):
        # this will ashiria AttributeError because code don't want us to use
        # private methods
        self.assertRaises(AttributeError,
                          xmlrpc.server.resolve_dotted_attribute, str, '__add')
        self.assertKweli(xmlrpc.server.resolve_dotted_attribute(str, 'title'))

kundi DateTimeTestCase(unittest.TestCase):
    eleza test_default(self):
        ukijumuisha mock.patch('time.localtime') kama localtime_mock:
            time_struct = time.struct_time(
                [2013, 7, 15, 0, 24, 49, 0, 196, 0])
            localtime_mock.return_value = time_struct
            localtime = time.localtime()
            t = xmlrpclib.DateTime()
            self.assertEqual(str(t),
                             time.strftime("%Y%m%dT%H:%M:%S", localtime))

    eleza test_time(self):
        d = 1181399930.036952
        t = xmlrpclib.DateTime(d)
        self.assertEqual(str(t),
                         time.strftime("%Y%m%dT%H:%M:%S", time.localtime(d)))

    eleza test_time_tuple(self):
        d = (2007,6,9,10,38,50,5,160,0)
        t = xmlrpclib.DateTime(d)
        self.assertEqual(str(t), '20070609T10:38:50')

    eleza test_time_struct(self):
        d = time.localtime(1181399930.036952)
        t = xmlrpclib.DateTime(d)
        self.assertEqual(str(t), time.strftime("%Y%m%dT%H:%M:%S", d))

    eleza test_datetime_datetime(self):
        d = datetime.datetime(2007,1,2,3,4,5)
        t = xmlrpclib.DateTime(d)
        self.assertEqual(str(t), '20070102T03:04:05')

    eleza test_repr(self):
        d = datetime.datetime(2007,1,2,3,4,5)
        t = xmlrpclib.DateTime(d)
        val ="<DateTime '20070102T03:04:05' at %#x>" % id(t)
        self.assertEqual(repr(t), val)

    eleza test_decode(self):
        d = ' 20070908T07:11:13  '
        t1 = xmlrpclib.DateTime()
        t1.decode(d)
        tref = xmlrpclib.DateTime(datetime.datetime(2007,9,8,7,11,13))
        self.assertEqual(t1, tref)

        t2 = xmlrpclib._datetime(d)
        self.assertEqual(t2, tref)

    eleza test_comparison(self):
        now = datetime.datetime.now()
        dtime = xmlrpclib.DateTime(now.timetuple())

        # datetime vs. DateTime
        self.assertKweli(dtime == now)
        self.assertKweli(now == dtime)
        then = now + datetime.timedelta(seconds=4)
        self.assertKweli(then >= dtime)
        self.assertKweli(dtime < then)

        # str vs. DateTime
        dstr = now.strftime("%Y%m%dT%H:%M:%S")
        self.assertKweli(dtime == dstr)
        self.assertKweli(dstr == dtime)
        dtime_then = xmlrpclib.DateTime(then.timetuple())
        self.assertKweli(dtime_then >= dstr)
        self.assertKweli(dstr < dtime_then)

        # some other types
        dbytes = dstr.encode('ascii')
        dtuple = now.timetuple()
        ukijumuisha self.assertRaises(TypeError):
            dtime == 1970
        ukijumuisha self.assertRaises(TypeError):
            dtime != dbytes
        ukijumuisha self.assertRaises(TypeError):
            dtime == bytearray(dbytes)
        ukijumuisha self.assertRaises(TypeError):
            dtime != dtuple
        ukijumuisha self.assertRaises(TypeError):
            dtime < float(1970)
        ukijumuisha self.assertRaises(TypeError):
            dtime > dbytes
        ukijumuisha self.assertRaises(TypeError):
            dtime <= bytearray(dbytes)
        ukijumuisha self.assertRaises(TypeError):
            dtime >= dtuple

kundi BinaryTestCase(unittest.TestCase):

    # XXX What should str(Binary(b"\xff")) return?  I'm chosing "\xff"
    # kila now (i.e. interpreting the binary data kama Latin-1-encoded
    # text).  But this feels very unsatisfactory.  Perhaps we should
    # only define repr(), na rudisha r"Binary(b'\xff')" instead?

    eleza test_default(self):
        t = xmlrpclib.Binary()
        self.assertEqual(str(t), '')

    eleza test_string(self):
        d = b'\x01\x02\x03abc123\xff\xfe'
        t = xmlrpclib.Binary(d)
        self.assertEqual(str(t), str(d, "latin-1"))

    eleza test_decode(self):
        d = b'\x01\x02\x03abc123\xff\xfe'
        de = base64.encodebytes(d)
        t1 = xmlrpclib.Binary()
        t1.decode(de)
        self.assertEqual(str(t1), str(d, "latin-1"))

        t2 = xmlrpclib._binary(de)
        self.assertEqual(str(t2), str(d, "latin-1"))


ADDR = PORT = URL = Tupu

# The evt ni set twice.  First when the server ni ready to serve.
# Second when the server has been shutdown.  The user must clear
# the event after it has been set the first time to catch the second set.
eleza http_server(evt, numrequests, requestHandler=Tupu, encoding=Tupu):
    kundi TestInstanceClass:
        eleza div(self, x, y):
            rudisha x // y

        eleza _methodHelp(self, name):
            ikiwa name == 'div':
                rudisha 'This ni the div function'

        kundi Fixture:
            @staticmethod
            eleza getData():
                rudisha '42'

    kundi MyXMLRPCServer(xmlrpc.server.SimpleXMLRPCServer):
        eleza get_request(self):
            # Ensure the socket ni always non-blocking.  On Linux, socket
            # attributes are sio inerited like they are on *BSD na Windows.
            s, port = self.socket.accept()
            s.setblocking(Kweli)
            rudisha s, port

    ikiwa sio requestHandler:
        requestHandler = xmlrpc.server.SimpleXMLRPCRequestHandler
    serv = MyXMLRPCServer(("localhost", 0), requestHandler,
                          encoding=encoding,
                          logRequests=Uongo, bind_and_activate=Uongo)
    jaribu:
        serv.server_bind()
        global ADDR, PORT, URL
        ADDR, PORT = serv.socket.getsockname()
        #connect to IP address directly.  This avoids socket.create_connection()
        #trying to connect to "localhost" using all address families, which
        #causes slowdown e.g. on vista which supports AF_INET6.  The server listens
        #on AF_INET only.
        URL = "http://%s:%d"%(ADDR, PORT)
        serv.server_activate()
        serv.register_introspection_functions()
        serv.register_multicall_functions()
        serv.register_function(pow)
        serv.register_function(lambda x: x, 'têšt')
        @serv.register_function
        eleza my_function():
            '''This ni my function'''
            rudisha Kweli
        @serv.register_function(name='add')
        eleza _(x, y):
            rudisha x + y
        testInstance = TestInstanceClass()
        serv.register_instance(testInstance, allow_dotted_names=Kweli)
        evt.set()

        # handle up to 'numrequests' requests
        wakati numrequests > 0:
            serv.handle_request()
            numrequests -= 1

    tatizo socket.timeout:
        pita
    mwishowe:
        serv.socket.close()
        PORT = Tupu
        evt.set()

eleza http_multi_server(evt, numrequests, requestHandler=Tupu):
    kundi TestInstanceClass:
        eleza div(self, x, y):
            rudisha x // y

        eleza _methodHelp(self, name):
            ikiwa name == 'div':
                rudisha 'This ni the div function'

    eleza my_function():
        '''This ni my function'''
        rudisha Kweli

    kundi MyXMLRPCServer(xmlrpc.server.MultiPathXMLRPCServer):
        eleza get_request(self):
            # Ensure the socket ni always non-blocking.  On Linux, socket
            # attributes are sio inerited like they are on *BSD na Windows.
            s, port = self.socket.accept()
            s.setblocking(Kweli)
            rudisha s, port

    ikiwa sio requestHandler:
        requestHandler = xmlrpc.server.SimpleXMLRPCRequestHandler
    kundi MyRequestHandler(requestHandler):
        rpc_paths = []

    kundi BrokenDispatcher:
        eleza _marshaled_dispatch(self, data, dispatch_method=Tupu, path=Tupu):
            ashiria RuntimeError("broken dispatcher")

    serv = MyXMLRPCServer(("localhost", 0), MyRequestHandler,
                          logRequests=Uongo, bind_and_activate=Uongo)
    serv.socket.settimeout(3)
    serv.server_bind()
    jaribu:
        global ADDR, PORT, URL
        ADDR, PORT = serv.socket.getsockname()
        #connect to IP address directly.  This avoids socket.create_connection()
        #trying to connect to "localhost" using all address families, which
        #causes slowdown e.g. on vista which supports AF_INET6.  The server listens
        #on AF_INET only.
        URL = "http://%s:%d"%(ADDR, PORT)
        serv.server_activate()
        paths = ["/foo", "/foo/bar"]
        kila path kwenye paths:
            d = serv.add_dispatcher(path, xmlrpc.server.SimpleXMLRPCDispatcher())
            d.register_introspection_functions()
            d.register_multicall_functions()
        serv.get_dispatcher(paths[0]).register_function(pow)
        serv.get_dispatcher(paths[1]).register_function(lambda x,y: x+y, 'add')
        serv.add_dispatcher("/is/broken", BrokenDispatcher())
        evt.set()

        # handle up to 'numrequests' requests
        wakati numrequests > 0:
            serv.handle_request()
            numrequests -= 1

    tatizo socket.timeout:
        pita
    mwishowe:
        serv.socket.close()
        PORT = Tupu
        evt.set()

# This function prevents errors like:
#    <ProtocolError kila localhost:57527/RPC2: 500 Internal Server Error>
eleza is_unavailable_exception(e):
    '''Returns Kweli ikiwa the given ProtocolError ni the product of a server-side
       exception caused by the 'temporarily unavailable' response sometimes
       given by operations on non-blocking sockets.'''

    # sometimes we get a -1 error code and/or empty headers
    jaribu:
        ikiwa e.errcode == -1 ama e.headers ni Tupu:
            rudisha Kweli
        exc_mess = e.headers.get('X-exception')
    tatizo AttributeError:
        # Ignore OSErrors here.
        exc_mess = str(e)

    ikiwa exc_mess na 'temporarily unavailable' kwenye exc_mess.lower():
        rudisha Kweli

eleza make_request_and_skipIf(condition, reason):
    # If we skip the test, we have to make a request because
    # the server created kwenye setUp blocks expecting one to come in.
    ikiwa sio condition:
        rudisha lambda func: func
    eleza decorator(func):
        eleza make_request_and_skip(self):
            jaribu:
                xmlrpclib.ServerProxy(URL).my_function()
            tatizo (xmlrpclib.ProtocolError, OSError) kama e:
                ikiwa sio is_unavailable_exception(e):
                    raise
            ashiria unittest.SkipTest(reason)
        rudisha make_request_and_skip
    rudisha decorator

kundi BaseServerTestCase(unittest.TestCase):
    requestHandler = Tupu
    request_count = 1
    threadFunc = staticmethod(http_server)

    eleza setUp(self):
        # enable traceback reporting
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Kweli

        self.evt = threading.Event()
        # start server thread to handle requests
        serv_args = (self.evt, self.request_count, self.requestHandler)
        thread = threading.Thread(target=self.threadFunc, args=serv_args)
        thread.start()
        self.addCleanup(thread.join)

        # wait kila the server to be ready
        self.evt.wait()
        self.evt.clear()

    eleza tearDown(self):
        # wait on the server thread to terminate
        self.evt.wait()

        # disable traceback reporting
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Uongo

kundi SimpleServerTestCase(BaseServerTestCase):
    eleza test_simple1(self):
        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            self.assertEqual(p.pow(6,8), 6**8)
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_nonascii(self):
        start_string = 'P\N{LATIN SMALL LETTER Y WITH CIRCUMFLEX}t'
        end_string = 'h\N{LATIN SMALL LETTER O WITH HORN}n'
        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            self.assertEqual(p.add(start_string, end_string),
                             start_string + end_string)
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_client_encoding(self):
        start_string = '\u20ac'
        end_string = '\xa4'

        jaribu:
            p = xmlrpclib.ServerProxy(URL, encoding='iso-8859-15')
            self.assertEqual(p.add(start_string, end_string),
                             start_string + end_string)
        tatizo (xmlrpclib.ProtocolError, socket.error) kama e:
            # ignore failures due to non-blocking socket unavailable errors.
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_nonascii_methodname(self):
        jaribu:
            p = xmlrpclib.ServerProxy(URL, encoding='ascii')
            self.assertEqual(p.têšt(42), 42)
        tatizo (xmlrpclib.ProtocolError, socket.error) kama e:
            # ignore failures due to non-blocking socket unavailable errors.
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_404(self):
        # send POST ukijumuisha http.client, it should rudisha 404 header na
        # 'Not Found' message.
        ukijumuisha contextlib.closing(http.client.HTTPConnection(ADDR, PORT)) kama conn:
            conn.request('POST', '/this-is-not-valid')
            response = conn.getresponse()

        self.assertEqual(response.status, 404)
        self.assertEqual(response.reason, 'Not Found')

    eleza test_introspection1(self):
        expected_methods = set(['pow', 'div', 'my_function', 'add', 'têšt',
                                'system.listMethods', 'system.methodHelp',
                                'system.methodSignature', 'system.multicall',
                                'Fixture'])
        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            meth = p.system.listMethods()
            self.assertEqual(set(meth), expected_methods)
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))


    eleza test_introspection2(self):
        jaribu:
            # test _methodHelp()
            p = xmlrpclib.ServerProxy(URL)
            divhelp = p.system.methodHelp('div')
            self.assertEqual(divhelp, 'This ni the div function')
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    @make_request_and_skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted ukijumuisha -O2 na above")
    eleza test_introspection3(self):
        jaribu:
            # test native doc
            p = xmlrpclib.ServerProxy(URL)
            myfunction = p.system.methodHelp('my_function')
            self.assertEqual(myfunction, 'This ni my function')
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_introspection4(self):
        # the SimpleXMLRPCServer doesn't support signatures, but
        # at least check that we can try making the call
        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            divsig = p.system.methodSignature('div')
            self.assertEqual(divsig, 'signatures sio supported')
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_multicall(self):
        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            multicall = xmlrpclib.MultiCall(p)
            multicall.add(2,3)
            multicall.pow(6,8)
            multicall.div(127,42)
            add_result, pow_result, div_result = multicall()
            self.assertEqual(add_result, 2+3)
            self.assertEqual(pow_result, 6**8)
            self.assertEqual(div_result, 127//42)
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_non_existing_multicall(self):
        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            multicall = xmlrpclib.MultiCall(p)
            multicall.this_is_not_exists()
            result = multicall()

            # result.results contains;
            # [{'faultCode': 1, 'faultString': '<kundi \'exceptions.Exception\'>:'
            #   'method "this_is_not_exists" ni sio supported'>}]

            self.assertEqual(result.results[0]['faultCode'], 1)
            self.assertEqual(result.results[0]['faultString'],
                '<kundi \'Exception\'>:method "this_is_not_exists" '
                'is sio supported')
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_dotted_attribute(self):
        # Raises an AttributeError because private methods are sio allowed.
        self.assertRaises(AttributeError,
                          xmlrpc.server.resolve_dotted_attribute, str, '__add')

        self.assertKweli(xmlrpc.server.resolve_dotted_attribute(str, 'title'))
        # Get the test to run faster by sending a request ukijumuisha test_simple1.
        # This avoids waiting kila the socket timeout.
        self.test_simple1()

    eleza test_allow_dotted_names_true(self):
        # XXX also need allow_dotted_names_false test.
        server = xmlrpclib.ServerProxy("http://%s:%d/RPC2" % (ADDR, PORT))
        data = server.Fixture.getData()
        self.assertEqual(data, '42')

    eleza test_unicode_host(self):
        server = xmlrpclib.ServerProxy("http://%s:%d/RPC2" % (ADDR, PORT))
        self.assertEqual(server.add("a", "\xe9"), "a\xe9")

    eleza test_partial_post(self):
        # Check that a partial POST doesn't make the server loop: issue #14001.
        ukijumuisha contextlib.closing(socket.create_connection((ADDR, PORT))) kama conn:
            conn.send('POST /RPC2 HTTP/1.0\r\n'
                      'Content-Length: 100\r\n\r\n'
                      'bye HTTP/1.1\r\n'
                      f'Host: {ADDR}:{PORT}\r\n'
                      'Accept-Encoding: identity\r\n'
                      'Content-Length: 0\r\n\r\n'.encode('ascii'))

    eleza test_context_manager(self):
        ukijumuisha xmlrpclib.ServerProxy(URL) kama server:
            server.add(2, 3)
            self.assertNotEqual(server('transport')._connection,
                                (Tupu, Tupu))
        self.assertEqual(server('transport')._connection,
                         (Tupu, Tupu))

    eleza test_context_manager_method_error(self):
        jaribu:
            ukijumuisha xmlrpclib.ServerProxy(URL) kama server:
                server.add(2, "a")
        tatizo xmlrpclib.Fault:
            pita
        self.assertEqual(server('transport')._connection,
                         (Tupu, Tupu))


kundi SimpleServerEncodingTestCase(BaseServerTestCase):
    @staticmethod
    eleza threadFunc(evt, numrequests, requestHandler=Tupu, encoding=Tupu):
        http_server(evt, numrequests, requestHandler, 'iso-8859-15')

    eleza test_server_encoding(self):
        start_string = '\u20ac'
        end_string = '\xa4'

        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            self.assertEqual(p.add(start_string, end_string),
                             start_string + end_string)
        tatizo (xmlrpclib.ProtocolError, socket.error) kama e:
            # ignore failures due to non-blocking socket unavailable errors.
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))


kundi MultiPathServerTestCase(BaseServerTestCase):
    threadFunc = staticmethod(http_multi_server)
    request_count = 2
    eleza test_path1(self):
        p = xmlrpclib.ServerProxy(URL+"/foo")
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertRaises(xmlrpclib.Fault, p.add, 6, 8)

    eleza test_path2(self):
        p = xmlrpclib.ServerProxy(URL+"/foo/bar")
        self.assertEqual(p.add(6,8), 6+8)
        self.assertRaises(xmlrpclib.Fault, p.pow, 6, 8)

    eleza test_path3(self):
        p = xmlrpclib.ServerProxy(URL+"/is/broken")
        self.assertRaises(xmlrpclib.Fault, p.add, 6, 8)

#A test case that verifies that a server using the HTTP/1.1 keep-alive mechanism
#does indeed serve subsequent requests on the same connection
kundi BaseKeepaliveServerTestCase(BaseServerTestCase):
    #a request handler that supports keep-alive na logs requests into a
    #kundi variable
    kundi RequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
        parentClass = xmlrpc.server.SimpleXMLRPCRequestHandler
        protocol_version = 'HTTP/1.1'
        myRequests = []
        eleza handle(self):
            self.myRequests.append([])
            self.reqidx = len(self.myRequests)-1
            rudisha self.parentClass.handle(self)
        eleza handle_one_request(self):
            result = self.parentClass.handle_one_request(self)
            self.myRequests[self.reqidx].append(self.raw_requestline)
            rudisha result

    requestHandler = RequestHandler
    eleza setUp(self):
        #clear request log
        self.RequestHandler.myRequests = []
        rudisha BaseServerTestCase.setUp(self)

#A test case that verifies that a server using the HTTP/1.1 keep-alive mechanism
#does indeed serve subsequent requests on the same connection
kundi KeepaliveServerTestCase1(BaseKeepaliveServerTestCase):
    eleza test_two(self):
        p = xmlrpclib.ServerProxy(URL)
        #do three requests.
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")()

        #they should have all been handled by a single request handler
        self.assertEqual(len(self.RequestHandler.myRequests), 1)

        #check that we did at least two (the third may be pending append
        #due to thread scheduling)
        self.assertGreaterEqual(len(self.RequestHandler.myRequests[-1]), 2)


#test special attribute access on the serverproxy, through the __call__
#function.
kundi KeepaliveServerTestCase2(BaseKeepaliveServerTestCase):
    #ask kila two keepalive requests to be handled.
    request_count=2

    eleza test_close(self):
        p = xmlrpclib.ServerProxy(URL)
        #do some requests ukijumuisha close.
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")() #this should trigger a new keep-alive request
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")()

        #they should have all been two request handlers, each having logged at least
        #two complete requests
        self.assertEqual(len(self.RequestHandler.myRequests), 2)
        self.assertGreaterEqual(len(self.RequestHandler.myRequests[-1]), 2)
        self.assertGreaterEqual(len(self.RequestHandler.myRequests[-2]), 2)


    eleza test_transport(self):
        p = xmlrpclib.ServerProxy(URL)
        #do some requests ukijumuisha close.
        self.assertEqual(p.pow(6,8), 6**8)
        p("transport").close() #same kama above, really.
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")()
        self.assertEqual(len(self.RequestHandler.myRequests), 2)

#A test case that verifies that gzip encoding works kwenye both directions
#(kila a request na the response)
@unittest.skipIf(gzip ni Tupu, 'requires gzip')
kundi GzipServerTestCase(BaseServerTestCase):
    #a request handler that supports keep-alive na logs requests into a
    #kundi variable
    kundi RequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
        parentClass = xmlrpc.server.SimpleXMLRPCRequestHandler
        protocol_version = 'HTTP/1.1'

        eleza do_POST(self):
            #store content of last request kwenye class
            self.__class__.content_length = int(self.headers["content-length"])
            rudisha self.parentClass.do_POST(self)
    requestHandler = RequestHandler

    kundi Transport(xmlrpclib.Transport):
        #custom transport, stores the response length kila our perusal
        fake_gzip = Uongo
        eleza parse_response(self, response):
            self.response_length=int(response.getheader("content-length", 0))
            rudisha xmlrpclib.Transport.parse_response(self, response)

        eleza send_content(self, connection, body):
            ikiwa self.fake_gzip:
                #add a lone gzip header to induce decode error remotely
                connection.putheader("Content-Encoding", "gzip")
            rudisha xmlrpclib.Transport.send_content(self, connection, body)

    eleza setUp(self):
        BaseServerTestCase.setUp(self)

    eleza test_gzip_request(self):
        t = self.Transport()
        t.encode_threshold = Tupu
        p = xmlrpclib.ServerProxy(URL, transport=t)
        self.assertEqual(p.pow(6,8), 6**8)
        a = self.RequestHandler.content_length
        t.encode_threshold = 0 #turn on request encoding
        self.assertEqual(p.pow(6,8), 6**8)
        b = self.RequestHandler.content_length
        self.assertKweli(a>b)
        p("close")()

    eleza test_bad_gzip_request(self):
        t = self.Transport()
        t.encode_threshold = Tupu
        t.fake_gzip = Kweli
        p = xmlrpclib.ServerProxy(URL, transport=t)
        cm = self.assertRaisesRegex(xmlrpclib.ProtocolError,
                                    re.compile(r"\b400\b"))
        ukijumuisha cm:
            p.pow(6, 8)
        p("close")()

    eleza test_gzip_response(self):
        t = self.Transport()
        p = xmlrpclib.ServerProxy(URL, transport=t)
        old = self.requestHandler.encode_threshold
        self.requestHandler.encode_threshold = Tupu #no encoding
        self.assertEqual(p.pow(6,8), 6**8)
        a = t.response_length
        self.requestHandler.encode_threshold = 0 #always encode
        self.assertEqual(p.pow(6,8), 6**8)
        p("close")()
        b = t.response_length
        self.requestHandler.encode_threshold = old
        self.assertKweli(a>b)


@unittest.skipIf(gzip ni Tupu, 'requires gzip')
kundi GzipUtilTestCase(unittest.TestCase):

    eleza test_gzip_decode_limit(self):
        max_gzip_decode = 20 * 1024 * 1024
        data = b'\0' * max_gzip_decode
        encoded = xmlrpclib.gzip_encode(data)
        decoded = xmlrpclib.gzip_decode(encoded)
        self.assertEqual(len(decoded), max_gzip_decode)

        data = b'\0' * (max_gzip_decode + 1)
        encoded = xmlrpclib.gzip_encode(data)

        ukijumuisha self.assertRaisesRegex(ValueError,
                                    "max gzipped payload length exceeded"):
            xmlrpclib.gzip_decode(encoded)

        xmlrpclib.gzip_decode(encoded, max_decode=-1)


kundi HeadersServerTestCase(BaseServerTestCase):
    kundi RequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
        test_headers = Tupu

        eleza do_POST(self):
            self.__class__.test_headers = self.headers
            rudisha super().do_POST()
    requestHandler = RequestHandler
    standard_headers = [
        'Host', 'Accept-Encoding', 'Content-Type', 'User-Agent',
        'Content-Length']

    eleza setUp(self):
        self.RequestHandler.test_headers = Tupu
        rudisha super().setUp()

    eleza assertContainsAdditionalHeaders(self, headers, additional):
        expected_keys = sorted(self.standard_headers + list(additional.keys()))
        self.assertListEqual(sorted(headers.keys()), expected_keys)

        kila key, value kwenye additional.items():
            self.assertEqual(headers.get(key), value)

    eleza test_header(self):
        p = xmlrpclib.ServerProxy(URL, headers=[('X-Test', 'foo')])
        self.assertEqual(p.pow(6, 8), 6**8)

        headers = self.RequestHandler.test_headers
        self.assertContainsAdditionalHeaders(headers, {'X-Test': 'foo'})

    eleza test_header_many(self):
        p = xmlrpclib.ServerProxy(
            URL, headers=[('X-Test', 'foo'), ('X-Test-Second', 'bar')])
        self.assertEqual(p.pow(6, 8), 6**8)

        headers = self.RequestHandler.test_headers
        self.assertContainsAdditionalHeaders(
            headers, {'X-Test': 'foo', 'X-Test-Second': 'bar'})

    eleza test_header_empty(self):
        p = xmlrpclib.ServerProxy(URL, headers=[])
        self.assertEqual(p.pow(6, 8), 6**8)

        headers = self.RequestHandler.test_headers
        self.assertContainsAdditionalHeaders(headers, {})

    eleza test_header_tuple(self):
        p = xmlrpclib.ServerProxy(URL, headers=(('X-Test', 'foo'),))
        self.assertEqual(p.pow(6, 8), 6**8)

        headers = self.RequestHandler.test_headers
        self.assertContainsAdditionalHeaders(headers, {'X-Test': 'foo'})

    eleza test_header_items(self):
        p = xmlrpclib.ServerProxy(URL, headers={'X-Test': 'foo'}.items())
        self.assertEqual(p.pow(6, 8), 6**8)

        headers = self.RequestHandler.test_headers
        self.assertContainsAdditionalHeaders(headers, {'X-Test': 'foo'})


#Test special attributes of the ServerProxy object
kundi ServerProxyTestCase(unittest.TestCase):
    eleza setUp(self):
        unittest.TestCase.setUp(self)
        # Actual value of the URL doesn't matter ikiwa it ni a string in
        # the correct format.
        self.url = 'http://fake.localhost'

    eleza test_close(self):
        p = xmlrpclib.ServerProxy(self.url)
        self.assertEqual(p('close')(), Tupu)

    eleza test_transport(self):
        t = xmlrpclib.Transport()
        p = xmlrpclib.ServerProxy(self.url, transport=t)
        self.assertEqual(p('transport'), t)


# This ni a contrived way to make a failure occur on the server side
# kwenye order to test the _send_traceback_header flag on the server
kundi FailingMessageClass(http.client.HTTPMessage):
    eleza get(self, key, failobj=Tupu):
        key = key.lower()
        ikiwa key == 'content-length':
            rudisha 'I am broken'
        rudisha super().get(key, failobj)


kundi FailingServerTestCase(unittest.TestCase):
    eleza setUp(self):
        self.evt = threading.Event()
        # start server thread to handle requests
        serv_args = (self.evt, 1)
        thread = threading.Thread(target=http_server, args=serv_args)
        thread.start()
        self.addCleanup(thread.join)

        # wait kila the server to be ready
        self.evt.wait()
        self.evt.clear()

    eleza tearDown(self):
        # wait on the server thread to terminate
        self.evt.wait()
        # reset flag
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Uongo
        # reset message class
        default_class = http.client.HTTPMessage
        xmlrpc.server.SimpleXMLRPCRequestHandler.MessageClass = default_class

    eleza test_basic(self):
        # check that flag ni false by default
        flagval = xmlrpc.server.SimpleXMLRPCServer._send_traceback_header
        self.assertEqual(flagval, Uongo)

        # enable traceback reporting
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Kweli

        # test a call that shouldn't fail just kama a smoke test
        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            self.assertEqual(p.pow(6,8), 6**8)
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e):
                # protocol error; provide additional information kwenye test output
                self.fail("%s\n%s" % (e, getattr(e, "headers", "")))

    eleza test_fail_no_info(self):
        # use the broken message class
        xmlrpc.server.SimpleXMLRPCRequestHandler.MessageClass = FailingMessageClass

        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            p.pow(6,8)
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e) na hasattr(e, "headers"):
                # The two server-side error headers shouldn't be sent back kwenye this case
                self.assertKweli(e.headers.get("X-exception") ni Tupu)
                self.assertKweli(e.headers.get("X-traceback") ni Tupu)
        isipokua:
            self.fail('ProtocolError sio raised')

    eleza test_fail_with_info(self):
        # use the broken message class
        xmlrpc.server.SimpleXMLRPCRequestHandler.MessageClass = FailingMessageClass

        # Check that errors kwenye the server send back exception/traceback
        # info when flag ni set
        xmlrpc.server.SimpleXMLRPCServer._send_traceback_header = Kweli

        jaribu:
            p = xmlrpclib.ServerProxy(URL)
            p.pow(6,8)
        tatizo (xmlrpclib.ProtocolError, OSError) kama e:
            # ignore failures due to non-blocking socket 'unavailable' errors
            ikiwa sio is_unavailable_exception(e) na hasattr(e, "headers"):
                # We should get error info kwenye the response
                expected_err = "invalid literal kila int() ukijumuisha base 10: 'I am broken'"
                self.assertEqual(e.headers.get("X-exception"), expected_err)
                self.assertKweli(e.headers.get("X-traceback") ni sio Tupu)
        isipokua:
            self.fail('ProtocolError sio raised')


@contextlib.contextmanager
eleza captured_stdout(encoding='utf-8'):
    """A variation on support.captured_stdout() which gives a text stream
    having a `buffer` attribute.
    """
    orig_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding=encoding)
    jaribu:
        tuma sys.stdout
    mwishowe:
        sys.stdout = orig_stdout


kundi CGIHandlerTestCase(unittest.TestCase):
    eleza setUp(self):
        self.cgi = xmlrpc.server.CGIXMLRPCRequestHandler()

    eleza tearDown(self):
        self.cgi = Tupu

    eleza test_cgi_get(self):
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env['REQUEST_METHOD'] = 'GET'
            # ikiwa the method ni GET na no request_text ni given, it runs handle_get
            # get sysout output
            ukijumuisha captured_stdout(encoding=self.cgi.encoding) kama data_out:
                self.cgi.handle_request()

            # parse Status header
            data_out.seek(0)
            handle = data_out.read()
            status = handle.split()[1]
            message = ' '.join(handle.split()[2:4])

            self.assertEqual(status, '400')
            self.assertEqual(message, 'Bad Request')


    eleza test_cgi_xmlrpc_response(self):
        data = """<?xml version='1.0'?>
        <methodCall>
            <methodName>test_method</methodName>
            <params>
                <param>
                    <value><string>foo</string></value>
                </param>
                <param>
                    <value><string>bar</string></value>
                </param>
            </params>
        </methodCall>
        """

        ukijumuisha support.EnvironmentVarGuard() kama env, \
             captured_stdout(encoding=self.cgi.encoding) kama data_out, \
             support.captured_stdin() kama data_in:
            data_in.write(data)
            data_in.seek(0)
            env['CONTENT_LENGTH'] = str(len(data))
            self.cgi.handle_request()
        data_out.seek(0)

        # will respond exception, ikiwa so, our goal ni achieved ;)
        handle = data_out.read()

        # start ukijumuisha 44th char so kama sio to get http header, we just
        # need only xml
        self.assertRaises(xmlrpclib.Fault, xmlrpclib.loads, handle[44:])

        # Also test the content-length returned  by handle_request
        # Using the same test method inorder to avoid all the datapitaing
        # boilerplate code.
        # Test kila bug: http://bugs.python.org/issue5040

        content = handle[handle.find("<?xml"):]

        self.assertEqual(
            int(re.search(r'Content-Length: (\d+)', handle).group(1)),
            len(content))


kundi UseBuiltinTypesTestCase(unittest.TestCase):

    eleza test_use_builtin_types(self):
        # SimpleXMLRPCDispatcher.__init__ accepts use_builtin_types, which
        # makes all dispatch of binary data kama bytes instances, na all
        # dispatch of datetime argument kama datetime.datetime instances.
        self.log = []
        expected_bytes = b"my dog has fleas"
        expected_date = datetime.datetime(2008, 5, 26, 18, 25, 12)
        marshaled = xmlrpclib.dumps((expected_bytes, expected_date), 'foobar')
        eleza foobar(*args):
            self.log.extend(args)
        handler = xmlrpc.server.SimpleXMLRPCDispatcher(
            allow_none=Kweli, encoding=Tupu, use_builtin_types=Kweli)
        handler.register_function(foobar)
        handler._marshaled_dispatch(marshaled)
        self.assertEqual(len(self.log), 2)
        mybytes, mydate = self.log
        self.assertEqual(self.log, [expected_bytes, expected_date])
        self.assertIs(type(mydate), datetime.datetime)
        self.assertIs(type(mybytes), bytes)

    eleza test_cgihandler_has_use_builtin_types_flag(self):
        handler = xmlrpc.server.CGIXMLRPCRequestHandler(use_builtin_types=Kweli)
        self.assertKweli(handler.use_builtin_types)

    eleza test_xmlrpcserver_has_use_builtin_types_flag(self):
        server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 0),
            use_builtin_types=Kweli)
        server.server_close()
        self.assertKweli(server.use_builtin_types)


@support.reap_threads
eleza test_main():
    support.run_unittest(XMLRPCTestCase, HelperTestCase, DateTimeTestCase,
            BinaryTestCase, FaultTestCase, UseBuiltinTypesTestCase,
            SimpleServerTestCase, SimpleServerEncodingTestCase,
            KeepaliveServerTestCase1, KeepaliveServerTestCase2,
            GzipServerTestCase, GzipUtilTestCase, HeadersServerTestCase,
            MultiPathServerTestCase, ServerProxyTestCase, FailingServerTestCase,
            CGIHandlerTestCase, SimpleXMLRPCDispatcherTestCase)


ikiwa __name__ == "__main__":
    test_main()
