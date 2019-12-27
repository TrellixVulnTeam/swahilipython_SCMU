"""Test script for poplib module."""

# Modified by Giampaolo Rodola' to give poplib.POP3 and poplib.POP3_SSL
# a real test suite

agiza poplib
agiza asyncore
agiza asynchat
agiza socket
agiza os
agiza errno
agiza threading

kutoka unittest agiza TestCase, skipUnless
kutoka test agiza support as test_support

HOST = test_support.HOST
PORT = 0

SUPPORTS_SSL = False
ikiwa hasattr(poplib, 'POP3_SSL'):
    agiza ssl

    SUPPORTS_SSL = True
    CERTFILE = os.path.join(os.path.dirname(__file__) or os.curdir, "keycert3.pem")
    CAFILE = os.path.join(os.path.dirname(__file__) or os.curdir, "pycacert.pem")

requires_ssl = skipUnless(SUPPORTS_SSL, 'SSL not supported')

# the dummy data returned by server when LIST and RETR commands are issued
LIST_RESP = b'1 1\r\n2 2\r\n3 3\r\n4 4\r\n5 5\r\n.\r\n'
RETR_RESP = b"""From: postmaster@python.org\
\r\nContent-Type: text/plain\r\n\
MIME-Version: 1.0\r\n\
Subject: Dummy\r\n\
\r\n\
line1\r\n\
line2\r\n\
line3\r\n\
.\r\n"""


kundi DummyPOP3Handler(asynchat.async_chat):

    CAPAS = {'UIDL': [], 'IMPLEMENTATION': ['python-testlib-pop-server']}
    enable_UTF8 = False

    eleza __init__(self, conn):
        asynchat.async_chat.__init__(self, conn)
        self.set_terminator(b"\r\n")
        self.in_buffer = []
        self.push('+OK dummy pop3 server ready. <timestamp>')
        self.tls_active = False
        self.tls_starting = False

    eleza collect_incoming_data(self, data):
        self.in_buffer.append(data)

    eleza found_terminator(self):
        line = b''.join(self.in_buffer)
        line = str(line, 'ISO-8859-1')
        self.in_buffer = []
        cmd = line.split(' ')[0].lower()
        space = line.find(' ')
        ikiwa space != -1:
            arg = line[space + 1:]
        else:
            arg = ""
        ikiwa hasattr(self, 'cmd_' + cmd):
            method = getattr(self, 'cmd_' + cmd)
            method(arg)
        else:
            self.push('-ERR unrecognized POP3 command "%s".' %cmd)

    eleza handle_error(self):
        raise

    eleza push(self, data):
        asynchat.async_chat.push(self, data.encode("ISO-8859-1") + b'\r\n')

    eleza cmd_echo(self, arg):
        # sends back the received string (used by the test suite)
        self.push(arg)

    eleza cmd_user(self, arg):
        ikiwa arg != "guido":
            self.push("-ERR no such user")
        self.push('+OK password required')

    eleza cmd_pass(self, arg):
        ikiwa arg != "python":
            self.push("-ERR wrong password")
        self.push('+OK 10 messages')

    eleza cmd_stat(self, arg):
        self.push('+OK 10 100')

    eleza cmd_list(self, arg):
        ikiwa arg:
            self.push('+OK %s %s' % (arg, arg))
        else:
            self.push('+OK')
            asynchat.async_chat.push(self, LIST_RESP)

    cmd_uidl = cmd_list

    eleza cmd_retr(self, arg):
        self.push('+OK %s bytes' %len(RETR_RESP))
        asynchat.async_chat.push(self, RETR_RESP)

    cmd_top = cmd_retr

    eleza cmd_dele(self, arg):
        self.push('+OK message marked for deletion.')

    eleza cmd_noop(self, arg):
        self.push('+OK done nothing.')

    eleza cmd_rpop(self, arg):
        self.push('+OK done nothing.')

    eleza cmd_apop(self, arg):
        self.push('+OK done nothing.')

    eleza cmd_quit(self, arg):
        self.push('+OK closing.')
        self.close_when_done()

    eleza _get_capas(self):
        _capas = dict(self.CAPAS)
        ikiwa not self.tls_active and SUPPORTS_SSL:
            _capas['STLS'] = []
        rudisha _capas

    eleza cmd_capa(self, arg):
        self.push('+OK Capability list follows')
        ikiwa self._get_capas():
            for cap, params in self._get_capas().items():
                _ln = [cap]
                ikiwa params:
                    _ln.extend(params)
                self.push(' '.join(_ln))
        self.push('.')

    eleza cmd_utf8(self, arg):
        self.push('+OK I know RFC6856'
                  ikiwa self.enable_UTF8
                  else '-ERR What is UTF8?!')

    ikiwa SUPPORTS_SSL:

        eleza cmd_stls(self, arg):
            ikiwa self.tls_active is False:
                self.push('+OK Begin TLS negotiation')
                context = ssl.SSLContext()
                context.load_cert_chain(CERTFILE)
                tls_sock = context.wrap_socket(self.socket,
                                               server_side=True,
                                               do_handshake_on_connect=False,
                                               suppress_ragged_eofs=False)
                self.del_channel()
                self.set_socket(tls_sock)
                self.tls_active = True
                self.tls_starting = True
                self.in_buffer = []
                self._do_tls_handshake()
            else:
                self.push('-ERR Command not permitted when TLS active')

        eleza _do_tls_handshake(self):
            try:
                self.socket.do_handshake()
            except ssl.SSLError as err:
                ikiwa err.args[0] in (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    return
                elikiwa err.args[0] == ssl.SSL_ERROR_EOF:
                    rudisha self.handle_close()
                # TODO: SSLError does not expose alert information
                elikiwa ("SSLV3_ALERT_BAD_CERTIFICATE" in err.args[1] or
                      "SSLV3_ALERT_CERTIFICATE_UNKNOWN" in err.args[1]):
                    rudisha self.handle_close()
                raise
            except OSError as err:
                ikiwa err.args[0] == errno.ECONNABORTED:
                    rudisha self.handle_close()
            else:
                self.tls_active = True
                self.tls_starting = False

        eleza handle_read(self):
            ikiwa self.tls_starting:
                self._do_tls_handshake()
            else:
                try:
                    asynchat.async_chat.handle_read(self)
                except ssl.SSLEOFError:
                    self.handle_close()

kundi DummyPOP3Server(asyncore.dispatcher, threading.Thread):

    handler = DummyPOP3Handler

    eleza __init__(self, address, af=socket.AF_INET):
        threading.Thread.__init__(self)
        asyncore.dispatcher.__init__(self)
        self.daemon = True
        self.create_socket(af, socket.SOCK_STREAM)
        self.bind(address)
        self.listen(5)
        self.active = False
        self.active_lock = threading.Lock()
        self.host, self.port = self.socket.getsockname()[:2]
        self.handler_instance = None

    eleza start(self):
        assert not self.active
        self.__flag = threading.Event()
        threading.Thread.start(self)
        self.__flag.wait()

    eleza run(self):
        self.active = True
        self.__flag.set()
        try:
            while self.active and asyncore.socket_map:
                with self.active_lock:
                    asyncore.loop(timeout=0.1, count=1)
        finally:
            asyncore.close_all(ignore_all=True)

    eleza stop(self):
        assert self.active
        self.active = False
        self.join()

    eleza handle_accepted(self, conn, addr):
        self.handler_instance = self.handler(conn)

    eleza handle_connect(self):
        self.close()
    handle_read = handle_connect

    eleza writable(self):
        rudisha 0

    eleza handle_error(self):
        raise


kundi TestPOP3Class(TestCase):
    eleza assertOK(self, resp):
        self.assertTrue(resp.startswith(b"+OK"))

    eleza setUp(self):
        self.server = DummyPOP3Server((HOST, PORT))
        self.server.start()
        self.client = poplib.POP3(self.server.host, self.server.port, timeout=3)

    eleza tearDown(self):
        self.client.close()
        self.server.stop()
        # Explicitly clear the attribute to prevent dangling thread
        self.server = None

    eleza test_getwelcome(self):
        self.assertEqual(self.client.getwelcome(),
                         b'+OK dummy pop3 server ready. <timestamp>')

    eleza test_exceptions(self):
        self.assertRaises(poplib.error_proto, self.client._shortcmd, 'echo -err')

    eleza test_user(self):
        self.assertOK(self.client.user('guido'))
        self.assertRaises(poplib.error_proto, self.client.user, 'invalid')

    eleza test_pass_(self):
        self.assertOK(self.client.pass_('python'))
        self.assertRaises(poplib.error_proto, self.client.user, 'invalid')

    eleza test_stat(self):
        self.assertEqual(self.client.stat(), (10, 100))

    eleza test_list(self):
        self.assertEqual(self.client.list()[1:],
                         ([b'1 1', b'2 2', b'3 3', b'4 4', b'5 5'],
                          25))
        self.assertTrue(self.client.list('1').endswith(b"OK 1 1"))

    eleza test_retr(self):
        expected = (b'+OK 116 bytes',
                    [b'From: postmaster@python.org', b'Content-Type: text/plain',
                     b'MIME-Version: 1.0', b'Subject: Dummy',
                     b'', b'line1', b'line2', b'line3'],
                    113)
        foo = self.client.retr('foo')
        self.assertEqual(foo, expected)

    eleza test_too_long_lines(self):
        self.assertRaises(poplib.error_proto, self.client._shortcmd,
                          'echo +%s' % ((poplib._MAXLINE + 10) * 'a'))

    eleza test_dele(self):
        self.assertOK(self.client.dele('foo'))

    eleza test_noop(self):
        self.assertOK(self.client.noop())

    eleza test_rpop(self):
        self.assertOK(self.client.rpop('foo'))

    @test_support.requires_hashdigest('md5')
    eleza test_apop_normal(self):
        self.assertOK(self.client.apop('foo', 'dummypassword'))

    @test_support.requires_hashdigest('md5')
    eleza test_apop_REDOS(self):
        # Replace welcome with very long evil welcome.
        # NB The upper bound on welcome length is currently 2048.
        # At this length, evil input makes each apop call take
        # on the order of milliseconds instead of microseconds.
        evil_welcome = b'+OK' + (b'<' * 1000000)
        with test_support.swap_attr(self.client, 'welcome', evil_welcome):
            # The evil welcome is invalid, so apop should throw.
            self.assertRaises(poplib.error_proto, self.client.apop, 'a', 'kb')

    eleza test_top(self):
        expected =  (b'+OK 116 bytes',
                     [b'From: postmaster@python.org', b'Content-Type: text/plain',
                      b'MIME-Version: 1.0', b'Subject: Dummy', b'',
                      b'line1', b'line2', b'line3'],
                     113)
        self.assertEqual(self.client.top(1, 1), expected)

    eleza test_uidl(self):
        self.client.uidl()
        self.client.uidl('foo')

    eleza test_utf8_raises_if_unsupported(self):
        self.server.handler.enable_UTF8 = False
        self.assertRaises(poplib.error_proto, self.client.utf8)

    eleza test_utf8(self):
        self.server.handler.enable_UTF8 = True
        expected = b'+OK I know RFC6856'
        result = self.client.utf8()
        self.assertEqual(result, expected)

    eleza test_capa(self):
        capa = self.client.capa()
        self.assertTrue('IMPLEMENTATION' in capa.keys())

    eleza test_quit(self):
        resp = self.client.quit()
        self.assertTrue(resp)
        self.assertIsNone(self.client.sock)
        self.assertIsNone(self.client.file)

    @requires_ssl
    eleza test_stls_capa(self):
        capa = self.client.capa()
        self.assertTrue('STLS' in capa.keys())

    @requires_ssl
    eleza test_stls(self):
        expected = b'+OK Begin TLS negotiation'
        resp = self.client.stls()
        self.assertEqual(resp, expected)

    @requires_ssl
    eleza test_stls_context(self):
        expected = b'+OK Begin TLS negotiation'
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(CAFILE)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertEqual(ctx.check_hostname, True)
        with self.assertRaises(ssl.CertificateError):
            resp = self.client.stls(context=ctx)
        self.client = poplib.POP3("localhost", self.server.port, timeout=3)
        resp = self.client.stls(context=ctx)
        self.assertEqual(resp, expected)


ikiwa SUPPORTS_SSL:
    kutoka test.test_ftplib agiza SSLConnection

    kundi DummyPOP3_SSLHandler(SSLConnection, DummyPOP3Handler):

        eleza __init__(self, conn):
            asynchat.async_chat.__init__(self, conn)
            self.secure_connection()
            self.set_terminator(b"\r\n")
            self.in_buffer = []
            self.push('+OK dummy pop3 server ready. <timestamp>')
            self.tls_active = True
            self.tls_starting = False


@requires_ssl
kundi TestPOP3_SSLClass(TestPOP3Class):
    # repeat previous tests by using poplib.POP3_SSL

    eleza setUp(self):
        self.server = DummyPOP3Server((HOST, PORT))
        self.server.handler = DummyPOP3_SSLHandler
        self.server.start()
        self.client = poplib.POP3_SSL(self.server.host, self.server.port)

    eleza test__all__(self):
        self.assertIn('POP3_SSL', poplib.__all__)

    eleza test_context(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.assertRaises(ValueError, poplib.POP3_SSL, self.server.host,
                            self.server.port, keyfile=CERTFILE, context=ctx)
        self.assertRaises(ValueError, poplib.POP3_SSL, self.server.host,
                            self.server.port, certfile=CERTFILE, context=ctx)
        self.assertRaises(ValueError, poplib.POP3_SSL, self.server.host,
                            self.server.port, keyfile=CERTFILE,
                            certfile=CERTFILE, context=ctx)

        self.client.quit()
        self.client = poplib.POP3_SSL(self.server.host, self.server.port,
                                        context=ctx)
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)
        self.assertIs(self.client.sock.context, ctx)
        self.assertTrue(self.client.noop().startswith(b'+OK'))

    eleza test_stls(self):
        self.assertRaises(poplib.error_proto, self.client.stls)

    test_stls_context = test_stls

    eleza test_stls_capa(self):
        capa = self.client.capa()
        self.assertFalse('STLS' in capa.keys())


@requires_ssl
kundi TestPOP3_TLSClass(TestPOP3Class):
    # repeat previous tests by using poplib.POP3.stls()

    eleza setUp(self):
        self.server = DummyPOP3Server((HOST, PORT))
        self.server.start()
        self.client = poplib.POP3(self.server.host, self.server.port, timeout=3)
        self.client.stls()

    eleza tearDown(self):
        ikiwa self.client.file is not None and self.client.sock is not None:
            try:
                self.client.quit()
            except poplib.error_proto:
                # happens in the test_too_long_lines case; the overlong
                # response will be treated as response to QUIT and raise
                # this exception
                self.client.close()
        self.server.stop()
        # Explicitly clear the attribute to prevent dangling thread
        self.server = None

    eleza test_stls(self):
        self.assertRaises(poplib.error_proto, self.client.stls)

    test_stls_context = test_stls

    eleza test_stls_capa(self):
        capa = self.client.capa()
        self.assertFalse(b'STLS' in capa.keys())


kundi TestTimeouts(TestCase):

    eleza setUp(self):
        self.evt = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(60)  # Safety net. Look issue 11812
        self.port = test_support.bind_port(self.sock)
        self.thread = threading.Thread(target=self.server, args=(self.evt,self.sock))
        self.thread.daemon = True
        self.thread.start()
        self.evt.wait()

    eleza tearDown(self):
        self.thread.join()
        # Explicitly clear the attribute to prevent dangling thread
        self.thread = None

    eleza server(self, evt, serv):
        serv.listen()
        evt.set()
        try:
            conn, addr = serv.accept()
            conn.send(b"+ Hola mundo\n")
            conn.close()
        except socket.timeout:
            pass
        finally:
            serv.close()

    eleza testTimeoutDefault(self):
        self.assertIsNone(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        try:
            pop = poplib.POP3(HOST, self.port)
        finally:
            socket.setdefaulttimeout(None)
        self.assertEqual(pop.sock.gettimeout(), 30)
        pop.close()

    eleza testTimeoutNone(self):
        self.assertIsNone(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        try:
            pop = poplib.POP3(HOST, self.port, timeout=None)
        finally:
            socket.setdefaulttimeout(None)
        self.assertIsNone(pop.sock.gettimeout())
        pop.close()

    eleza testTimeoutValue(self):
        pop = poplib.POP3(HOST, self.port, timeout=30)
        self.assertEqual(pop.sock.gettimeout(), 30)
        pop.close()


eleza test_main():
    tests = [TestPOP3Class, TestTimeouts,
             TestPOP3_SSLClass, TestPOP3_TLSClass]
    thread_info = test_support.threading_setup()
    try:
        test_support.run_unittest(*tests)
    finally:
        test_support.threading_cleanup(*thread_info)


ikiwa __name__ == '__main__':
    test_main()
