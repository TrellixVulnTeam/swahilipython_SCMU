kutoka test agiza support

kutoka contextlib agiza contextmanager
agiza imaplib
agiza os.path
agiza socketserver
agiza time
agiza calendar
agiza threading
agiza socket

kutoka test.support agiza (reap_threads, verbose, transient_internet,
                          run_with_tz, run_with_locale, cpython_only,
                          requires_hashdigest)
agiza unittest
kutoka unittest agiza mock
kutoka datetime agiza datetime, timezone, timedelta
jaribu:
    agiza ssl
tatizo ImportError:
    ssl = Tupu

CERTFILE = os.path.join(os.path.dirname(__file__) ama os.curdir, "keycert3.pem")
CAFILE = os.path.join(os.path.dirname(__file__) ama os.curdir, "pycacert.pem")


kundi TestImaplib(unittest.TestCase):

    eleza test_Internaldate2tuple(self):
        t0 = calendar.timegm((2000, 1, 1, 0, 0, 0, -1, -1, -1))
        tt = imaplib.Internaldate2tuple(
            b'25 (INTERNALDATE "01-Jan-2000 00:00:00 +0000")')
        self.assertEqual(time.mktime(tt), t0)
        tt = imaplib.Internaldate2tuple(
            b'25 (INTERNALDATE "01-Jan-2000 11:30:00 +1130")')
        self.assertEqual(time.mktime(tt), t0)
        tt = imaplib.Internaldate2tuple(
            b'25 (INTERNALDATE "31-Dec-1999 12:30:00 -1130")')
        self.assertEqual(time.mktime(tt), t0)

    @run_with_tz('MST+07MDT,M4.1.0,M10.5.0')
    eleza test_Internaldate2tuple_issue10941(self):
        self.assertNotEqual(imaplib.Internaldate2tuple(
            b'25 (INTERNALDATE "02-Apr-2000 02:30:00 +0000")'),
            imaplib.Internaldate2tuple(
                b'25 (INTERNALDATE "02-Apr-2000 03:30:00 +0000")'))

    eleza timevalues(self):
        rudisha [2000000000, 2000000000.0, time.localtime(2000000000),
                (2033, 5, 18, 5, 33, 20, -1, -1, -1),
                (2033, 5, 18, 5, 33, 20, -1, -1, 1),
                datetime.fromtimestamp(2000000000,
                                       timezone(timedelta(0, 2 * 60 * 60))),
                '"18-May-2033 05:33:20 +0200"']

    @run_with_locale('LC_ALL', 'de_DE', 'fr_FR')
    # DST rules included to work around quirk where the Gnu C library may not
    # otherwise restore the previous time zone
    @run_with_tz('STD-1DST,M3.2.0,M11.1.0')
    eleza test_Time2Internaldate(self):
        expected = '"18-May-2033 05:33:20 +0200"'

        kila t kwenye self.timevalues():
            internal = imaplib.Time2Internaldate(t)
            self.assertEqual(internal, expected)

    eleza test_that_Time2Internaldate_returns_a_result(self):
        # Without tzset, we can check only that it successfully
        # produces a result, sio the correctness of the result itself,
        # since the result depends on the timezone the machine ni in.
        kila t kwenye self.timevalues():
            imaplib.Time2Internaldate(t)

    eleza test_imap4_host_default_value(self):
        # Check whether the IMAP4_PORT ni truly unavailable.
        ukijumuisha socket.socket() kama s:
            jaribu:
                s.connect(('', imaplib.IMAP4_PORT))
                self.skipTest(
                    "Cannot run the test ukijumuisha local IMAP server running.")
            tatizo socket.error:
                pita

        # This ni the exception that should be raised.
        expected_errnos = support.get_socket_conn_refused_errs()
        ukijumuisha self.assertRaises(OSError) kama cm:
            imaplib.IMAP4()
        self.assertIn(cm.exception.errno, expected_errnos)


ikiwa ssl:
    kundi SecureTCPServer(socketserver.TCPServer):

        eleza get_request(self):
            newsocket, fromaddr = self.socket.accept()
            context = ssl.SSLContext()
            context.load_cert_chain(CERTFILE)
            connstream = context.wrap_socket(newsocket, server_side=Kweli)
            rudisha connstream, fromaddr

    IMAP4_SSL = imaplib.IMAP4_SSL

isipokua:

    kundi SecureTCPServer:
        pita

    IMAP4_SSL = Tupu


kundi SimpleIMAPHandler(socketserver.StreamRequestHandler):
    timeout = 1
    continuation = Tupu
    capabilities = ''

    eleza setup(self):
        super().setup()
        self.server.logged = Tupu

    eleza _send(self, message):
        ikiwa verbose:
            andika("SENT: %r" % message.strip())
        self.wfile.write(message)

    eleza _send_line(self, message):
        self._send(message + b'\r\n')

    eleza _send_textline(self, message):
        self._send_line(message.encode('ASCII'))

    eleza _send_tagged(self, tag, code, message):
        self._send_textline(' '.join((tag, code, message)))

    eleza handle(self):
        # Send a welcome message.
        self._send_textline('* OK IMAP4rev1')
        wakati 1:
            # Gather up input until we receive a line terminator ama we timeout.
            # Accumulate read(1) because it's simpler to handle the differences
            # between naked sockets na SSL sockets.
            line = b''
            wakati 1:
                jaribu:
                    part = self.rfile.read(1)
                    ikiwa part == b'':
                        # Naked sockets rudisha empty strings..
                        rudisha
                    line += part
                tatizo OSError:
                    # ..but SSLSockets ashiria exceptions.
                    rudisha
                ikiwa line.endswith(b'\r\n'):
                    koma

            ikiwa verbose:
                andika('GOT: %r' % line.strip())
            ikiwa self.continuation:
                jaribu:
                    self.continuation.send(line)
                tatizo StopIteration:
                    self.continuation = Tupu
                endelea
            splitline = line.decode('ASCII').split()
            tag = splitline[0]
            cmd = splitline[1]
            args = splitline[2:]

            ikiwa hasattr(self, 'cmd_' + cmd):
                continuation = getattr(self, 'cmd_' + cmd)(tag, args)
                ikiwa continuation:
                    self.continuation = continuation
                    next(continuation)
            isipokua:
                self._send_tagged(tag, 'BAD', cmd + ' unknown')

    eleza cmd_CAPABILITY(self, tag, args):
        caps = ('IMAP4rev1 ' + self.capabilities
                ikiwa self.capabilities
                isipokua 'IMAP4rev1')
        self._send_textline('* CAPABILITY ' + caps)
        self._send_tagged(tag, 'OK', 'CAPABILITY completed')

    eleza cmd_LOGOUT(self, tag, args):
        self.server.logged = Tupu
        self._send_textline('* BYE IMAP4ref1 Server logging out')
        self._send_tagged(tag, 'OK', 'LOGOUT completed')

    eleza cmd_LOGIN(self, tag, args):
        self.server.logged = args[0]
        self._send_tagged(tag, 'OK', 'LOGIN completed')


kundi NewIMAPTestsMixin():
    client = Tupu

    eleza _setup(self, imap_handler, connect=Kweli):
        """
        Sets up imap_handler kila tests. imap_handler should inherit kutoka either:
        - SimpleIMAPHandler - kila testing IMAP commands,
        - socketserver.StreamRequestHandler - ikiwa raw access to stream ni needed.
        Returns (client, server).
        """
        kundi TestTCPServer(self.server_class):
            eleza handle_error(self, request, client_address):
                """
                End request na ashiria the error ikiwa one occurs.
                """
                self.close_request(request)
                self.server_close()
                raise

        self.addCleanup(self._cleanup)
        self.server = self.server_class((support.HOST, 0), imap_handler)
        self.thread = threading.Thread(
            name=self._testMethodName+'-server',
            target=self.server.serve_forever,
            # Short poll interval to make the test finish quickly.
            # Time between requests ni short enough that we won't wake
            # up spuriously too many times.
            kwargs={'poll_interval': 0.01})
        self.thread.daemon = Kweli  # In case this function raises.
        self.thread.start()

        ikiwa connect:
            self.client = self.imap_class(*self.server.server_address)

        rudisha self.client, self.server

    eleza _cleanup(self):
        """
        Cleans up the test server. This method should sio be called manually,
        it ni added to the cleanup queue kwenye the _setup method already.
        """
        # ikiwa logout was called already we'd ashiria an exception trying to
        # shutdown the client once again
        ikiwa self.client ni sio Tupu na self.client.state != 'LOGOUT':
            self.client.shutdown()
        # cleanup the server
        self.server.shutdown()
        self.server.server_close()
        support.join_thread(self.thread, 3.0)
        # Explicitly clear the attribute to prevent dangling thread
        self.thread = Tupu

    eleza test_EOF_without_complete_welcome_message(self):
        # http://bugs.python.org/issue5949
        kundi EOFHandler(socketserver.StreamRequestHandler):
            eleza handle(self):
                self.wfile.write(b'* OK')
        _, server = self._setup(EOFHandler, connect=Uongo)
        self.assertRaises(imaplib.IMAP4.abort, self.imap_class,
                          *server.server_address)

    eleza test_line_termination(self):
        kundi BadNewlineHandler(SimpleIMAPHandler):
            eleza cmd_CAPABILITY(self, tag, args):
                self._send(b'* CAPABILITY IMAP4rev1 AUTH\n')
                self._send_tagged(tag, 'OK', 'CAPABILITY completed')
        _, server = self._setup(BadNewlineHandler, connect=Uongo)
        self.assertRaises(imaplib.IMAP4.abort, self.imap_class,
                          *server.server_address)

    eleza test_enable_raises_error_if_not_AUTH(self):
        kundi EnableHandler(SimpleIMAPHandler):
            capabilities = 'AUTH ENABLE UTF8=ACCEPT'
        client, _ = self._setup(EnableHandler)
        self.assertUongo(client.utf8_enabled)
        ukijumuisha self.assertRaisesRegex(imaplib.IMAP4.error, 'ENABLE.*NONAUTH'):
            client.enable('foo')
        self.assertUongo(client.utf8_enabled)

    eleza test_enable_raises_error_if_no_capability(self):
        client, _ = self._setup(SimpleIMAPHandler)
        ukijumuisha self.assertRaisesRegex(imaplib.IMAP4.error,
                'does sio support ENABLE'):
            client.enable('foo')

    eleza test_enable_UTF8_raises_error_if_not_supported(self):
        client, _ = self._setup(SimpleIMAPHandler)
        typ, data = client.login('user', 'pita')
        self.assertEqual(typ, 'OK')
        ukijumuisha self.assertRaisesRegex(imaplib.IMAP4.error,
                'does sio support ENABLE'):
            client.enable('UTF8=ACCEPT')

    eleza test_enable_UTF8_Kweli_append(self):
        kundi UTF8AppendServer(SimpleIMAPHandler):
            capabilities = 'ENABLE UTF8=ACCEPT'
            eleza cmd_ENABLE(self, tag, args):
                self._send_tagged(tag, 'OK', 'ENABLE successful')
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.server.response = tuma
                self._send_tagged(tag, 'OK', 'FAKEAUTH successful')
            eleza cmd_APPEND(self, tag, args):
                self._send_textline('+')
                self.server.response = tuma
                self._send_tagged(tag, 'OK', 'okay')
        client, server = self._setup(UTF8AppendServer)
        self.assertEqual(client._encoding, 'ascii')
        code, _ = client.authenticate('MYAUTH', lambda x: b'fake')
        self.assertEqual(code, 'OK')
        self.assertEqual(server.response, b'ZmFrZQ==\r\n')  # b64 encoded 'fake'
        code, _ = client.enable('UTF8=ACCEPT')
        self.assertEqual(code, 'OK')
        self.assertEqual(client._encoding, 'utf-8')
        msg_string = 'Subject: üñí©öðé'
        typ, data = client.append(Tupu, Tupu, Tupu, msg_string.encode('utf-8'))
        self.assertEqual(typ, 'OK')
        self.assertEqual(server.response,
            ('UTF8 (%s)\r\n' % msg_string).encode('utf-8'))

    eleza test_search_disallows_charset_in_utf8_mode(self):
        kundi UTF8Server(SimpleIMAPHandler):
            capabilities = 'AUTH ENABLE UTF8=ACCEPT'
            eleza cmd_ENABLE(self, tag, args):
                self._send_tagged(tag, 'OK', 'ENABLE successful')
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.server.response = tuma
                self._send_tagged(tag, 'OK', 'FAKEAUTH successful')
        client, _ = self._setup(UTF8Server)
        typ, _ = client.authenticate('MYAUTH', lambda x: b'fake')
        self.assertEqual(typ, 'OK')
        typ, _ = client.enable('UTF8=ACCEPT')
        self.assertEqual(typ, 'OK')
        self.assertKweli(client.utf8_enabled)
        ukijumuisha self.assertRaisesRegex(imaplib.IMAP4.error, 'charset.*UTF8'):
            client.search('foo', 'bar')

    eleza test_bad_auth_name(self):
        kundi MyServer(SimpleIMAPHandler):
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_tagged(tag, 'NO',
                    'unrecognized authentication type {}'.format(args[0]))
        client, _ = self._setup(MyServer)
        ukijumuisha self.assertRaisesRegex(imaplib.IMAP4.error,
                'unrecognized authentication type METHOD'):
            client.authenticate('METHOD', lambda: 1)

    eleza test_invalid_authentication(self):
        kundi MyServer(SimpleIMAPHandler):
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.response = tuma
                self._send_tagged(tag, 'NO', '[AUTHENTICATIONFAILED] invalid')
        client, _ = self._setup(MyServer)
        ukijumuisha self.assertRaisesRegex(imaplib.IMAP4.error,
                r'\[AUTHENTICATIONFAILED\] invalid'):
            client.authenticate('MYAUTH', lambda x: b'fake')

    eleza test_valid_authentication_bytes(self):
        kundi MyServer(SimpleIMAPHandler):
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.server.response = tuma
                self._send_tagged(tag, 'OK', 'FAKEAUTH successful')
        client, server = self._setup(MyServer)
        code, _ = client.authenticate('MYAUTH', lambda x: b'fake')
        self.assertEqual(code, 'OK')
        self.assertEqual(server.response, b'ZmFrZQ==\r\n')  # b64 encoded 'fake'

    eleza test_valid_authentication_plain_text(self):
        kundi MyServer(SimpleIMAPHandler):
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.server.response = tuma
                self._send_tagged(tag, 'OK', 'FAKEAUTH successful')
        client, server = self._setup(MyServer)
        code, _ = client.authenticate('MYAUTH', lambda x: 'fake')
        self.assertEqual(code, 'OK')
        self.assertEqual(server.response, b'ZmFrZQ==\r\n')  # b64 encoded 'fake'

    @requires_hashdigest('md5')
    eleza test_login_cram_md5_bytes(self):
        kundi AuthHandler(SimpleIMAPHandler):
            capabilities = 'LOGINDISABLED AUTH=CRAM-MD5'
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+ PDE4OTYuNjk3MTcwOTUyQHBvc3RvZmZpY2Uucm'
                                    'VzdG9uLm1jaS5uZXQ=')
                r = tuma
                ikiwa (r == b'dGltIGYxY2E2YmU0NjRiOWVmYT'
                         b'FjY2E2ZmZkNmNmMmQ5ZjMy\r\n'):
                    self._send_tagged(tag, 'OK', 'CRAM-MD5 successful')
                isipokua:
                    self._send_tagged(tag, 'NO', 'No access')
        client, _ = self._setup(AuthHandler)
        self.assertKweli('AUTH=CRAM-MD5' kwenye client.capabilities)
        ret, _ = client.login_cram_md5("tim", b"tanstaaftanstaaf")
        self.assertEqual(ret, "OK")

    @requires_hashdigest('md5')
    eleza test_login_cram_md5_plain_text(self):
        kundi AuthHandler(SimpleIMAPHandler):
            capabilities = 'LOGINDISABLED AUTH=CRAM-MD5'
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+ PDE4OTYuNjk3MTcwOTUyQHBvc3RvZmZpY2Uucm'
                                    'VzdG9uLm1jaS5uZXQ=')
                r = tuma
                ikiwa (r == b'dGltIGYxY2E2YmU0NjRiOWVmYT'
                         b'FjY2E2ZmZkNmNmMmQ5ZjMy\r\n'):
                    self._send_tagged(tag, 'OK', 'CRAM-MD5 successful')
                isipokua:
                    self._send_tagged(tag, 'NO', 'No access')
        client, _ = self._setup(AuthHandler)
        self.assertKweli('AUTH=CRAM-MD5' kwenye client.capabilities)
        ret, _ = client.login_cram_md5("tim", "tanstaaftanstaaf")
        self.assertEqual(ret, "OK")

    eleza test_aborted_authentication(self):
        kundi MyServer(SimpleIMAPHandler):
            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.response = tuma
                ikiwa self.response == b'*\r\n':
                    self._send_tagged(
                        tag,
                        'NO',
                        '[AUTHENTICATIONFAILED] aborted')
                isipokua:
                    self._send_tagged(tag, 'OK', 'MYAUTH successful')
        client, _ = self._setup(MyServer)
        ukijumuisha self.assertRaisesRegex(imaplib.IMAP4.error,
                r'\[AUTHENTICATIONFAILED\] aborted'):
            client.authenticate('MYAUTH', lambda x: Tupu)

    @mock.patch('imaplib._MAXLINE', 10)
    eleza test_linetoolong(self):
        kundi TooLongHandler(SimpleIMAPHandler):
            eleza handle(self):
                # send response line longer than the limit set kwenye the next line
                self.wfile.write(b'* OK ' + 11 * b'x' + b'\r\n')
        _, server = self._setup(TooLongHandler, connect=Uongo)
        ukijumuisha self.assertRaisesRegex(imaplib.IMAP4.error,
                'got more than 10 bytes'):
            self.imap_class(*server.server_address)

    eleza test_simple_with_statement(self):
        _, server = self._setup(SimpleIMAPHandler, connect=Uongo)
        ukijumuisha self.imap_class(*server.server_address):
            pita

    eleza test_with_statement(self):
        _, server = self._setup(SimpleIMAPHandler, connect=Uongo)
        ukijumuisha self.imap_class(*server.server_address) kama imap:
            imap.login('user', 'pita')
            self.assertEqual(server.logged, 'user')
        self.assertIsTupu(server.logged)

    eleza test_with_statement_logout(self):
        # It ni legal to log out explicitly inside the ukijumuisha block
        _, server = self._setup(SimpleIMAPHandler, connect=Uongo)
        ukijumuisha self.imap_class(*server.server_address) kama imap:
            imap.login('user', 'pita')
            self.assertEqual(server.logged, 'user')
            imap.logout()
            self.assertIsTupu(server.logged)
        self.assertIsTupu(server.logged)

    # command tests

    eleza test_login(self):
        client, _ = self._setup(SimpleIMAPHandler)
        typ, data = client.login('user', 'pita')
        self.assertEqual(typ, 'OK')
        self.assertEqual(data[0], b'LOGIN completed')
        self.assertEqual(client.state, 'AUTH')

    eleza test_logout(self):
        client, _ = self._setup(SimpleIMAPHandler)
        typ, data = client.login('user', 'pita')
        self.assertEqual(typ, 'OK')
        self.assertEqual(data[0], b'LOGIN completed')
        typ, data = client.logout()
        self.assertEqual(typ, 'BYE', (typ, data))
        self.assertEqual(data[0], b'IMAP4ref1 Server logging out', (typ, data))
        self.assertEqual(client.state, 'LOGOUT')

    eleza test_lsub(self):
        kundi LsubCmd(SimpleIMAPHandler):
            eleza cmd_LSUB(self, tag, args):
                self._send_textline('* LSUB () "." directoryA')
                rudisha self._send_tagged(tag, 'OK', 'LSUB completed')
        client, _ = self._setup(LsubCmd)
        client.login('user', 'pita')
        typ, data = client.lsub()
        self.assertEqual(typ, 'OK')
        self.assertEqual(data[0], b'() "." directoryA')


kundi NewIMAPTests(NewIMAPTestsMixin, unittest.TestCase):
    imap_class = imaplib.IMAP4
    server_class = socketserver.TCPServer


@unittest.skipUnless(ssl, "SSL sio available")
kundi NewIMAPSSLTests(NewIMAPTestsMixin, unittest.TestCase):
    imap_class = IMAP4_SSL
    server_class = SecureTCPServer

    eleza test_ssl_raises(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertEqual(ssl_context.verify_mode, ssl.CERT_REQUIRED)
        self.assertEqual(ssl_context.check_hostname, Kweli)
        ssl_context.load_verify_locations(CAFILE)

        ukijumuisha self.assertRaisesRegex(ssl.CertificateError,
                "IP address mismatch, certificate ni sio valid kila "
                "'127.0.0.1'"):
            _, server = self._setup(SimpleIMAPHandler)
            client = self.imap_class(*server.server_address,
                                     ssl_context=ssl_context)
            client.shutdown()

    eleza test_ssl_verified(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(CAFILE)

        _, server = self._setup(SimpleIMAPHandler)
        client = self.imap_class("localhost", server.server_address[1],
                                 ssl_context=ssl_context)
        client.shutdown()

    # Mock the private method _connect(), so mark the test kama specific
    # to CPython stdlib
    @cpython_only
    eleza test_certfile_arg_warn(self):
        ukijumuisha support.check_warnings(('', DeprecationWarning)):
            ukijumuisha mock.patch.object(self.imap_class, 'open'):
                ukijumuisha mock.patch.object(self.imap_class, '_connect'):
                    self.imap_class('localhost', 143, certfile=CERTFILE)

kundi ThreadedNetworkedTests(unittest.TestCase):
    server_class = socketserver.TCPServer
    imap_class = imaplib.IMAP4

    eleza make_server(self, addr, hdlr):

        kundi MyServer(self.server_class):
            eleza handle_error(self, request, client_address):
                self.close_request(request)
                self.server_close()
                raise

        ikiwa verbose:
            andika("creating server")
        server = MyServer(addr, hdlr)
        self.assertEqual(server.server_address, server.socket.getsockname())

        ikiwa verbose:
            andika("server created")
            andika("ADDR =", addr)
            andika("CLASS =", self.server_class)
            andika("HDLR =", server.RequestHandlerClass)

        t = threading.Thread(
            name='%s serving' % self.server_class,
            target=server.serve_forever,
            # Short poll interval to make the test finish quickly.
            # Time between requests ni short enough that we won't wake
            # up spuriously too many times.
            kwargs={'poll_interval': 0.01})
        t.daemon = Kweli  # In case this function raises.
        t.start()
        ikiwa verbose:
            andika("server running")
        rudisha server, t

    eleza reap_server(self, server, thread):
        ikiwa verbose:
            andika("waiting kila server")
        server.shutdown()
        server.server_close()
        thread.join()
        ikiwa verbose:
            andika("done")

    @contextmanager
    eleza reaped_server(self, hdlr):
        server, thread = self.make_server((support.HOST, 0), hdlr)
        jaribu:
            tuma server
        mwishowe:
            self.reap_server(server, thread)

    @contextmanager
    eleza reaped_pair(self, hdlr):
        ukijumuisha self.reaped_server(hdlr) kama server:
            client = self.imap_class(*server.server_address)
            jaribu:
                tuma server, client
            mwishowe:
                client.logout()

    @reap_threads
    eleza test_connect(self):
        ukijumuisha self.reaped_server(SimpleIMAPHandler) kama server:
            client = self.imap_class(*server.server_address)
            client.shutdown()

    @reap_threads
    eleza test_bracket_flags(self):

        # This violates RFC 3501, which disallows ']' characters kwenye tag names,
        # but imaplib has allowed producing such tags forever, other programs
        # also produce them (eg: OtherInbox's Organizer app kama of 20140716),
        # na Gmail, kila example, accepts them na produces them.  So we
        # support them.  See issue #21815.

        kundi BracketFlagHandler(SimpleIMAPHandler):

            eleza handle(self):
                self.flags = ['Answered', 'Flagged', 'Deleted', 'Seen', 'Draft']
                super().handle()

            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.server.response = tuma
                self._send_tagged(tag, 'OK', 'FAKEAUTH successful')

            eleza cmd_SELECT(self, tag, args):
                flag_msg = ' \\'.join(self.flags)
                self._send_line(('* FLAGS (%s)' % flag_msg).encode('ascii'))
                self._send_line(b'* 2 EXISTS')
                self._send_line(b'* 0 RECENT')
                msg = ('* OK [PERMANENTFLAGS %s \\*)] Flags permitted.'
                        % flag_msg)
                self._send_line(msg.encode('ascii'))
                self._send_tagged(tag, 'OK', '[READ-WRITE] SELECT completed.')

            eleza cmd_STORE(self, tag, args):
                new_flags = args[2].strip('(').strip(')').split()
                self.flags.extend(new_flags)
                flags_msg = '(FLAGS (%s))' % ' \\'.join(self.flags)
                msg = '* %s FETCH %s' % (args[0], flags_msg)
                self._send_line(msg.encode('ascii'))
                self._send_tagged(tag, 'OK', 'STORE completed.')

        ukijumuisha self.reaped_pair(BracketFlagHandler) kama (server, client):
            code, data = client.authenticate('MYAUTH', lambda x: b'fake')
            self.assertEqual(code, 'OK')
            self.assertEqual(server.response, b'ZmFrZQ==\r\n')
            client.select('test')
            typ, [data] = client.store(b'1', "+FLAGS", "[test]")
            self.assertIn(b'[test]', data)
            client.select('test')
            typ, [data] = client.response('PERMANENTFLAGS')
            self.assertIn(b'[test]', data)

    @reap_threads
    eleza test_issue5949(self):

        kundi EOFHandler(socketserver.StreamRequestHandler):
            eleza handle(self):
                # EOF without sending a complete welcome message.
                self.wfile.write(b'* OK')

        ukijumuisha self.reaped_server(EOFHandler) kama server:
            self.assertRaises(imaplib.IMAP4.abort,
                              self.imap_class, *server.server_address)

    @reap_threads
    eleza test_line_termination(self):

        kundi BadNewlineHandler(SimpleIMAPHandler):

            eleza cmd_CAPABILITY(self, tag, args):
                self._send(b'* CAPABILITY IMAP4rev1 AUTH\n')
                self._send_tagged(tag, 'OK', 'CAPABILITY completed')

        ukijumuisha self.reaped_server(BadNewlineHandler) kama server:
            self.assertRaises(imaplib.IMAP4.abort,
                              self.imap_class, *server.server_address)

    kundi UTF8Server(SimpleIMAPHandler):
        capabilities = 'AUTH ENABLE UTF8=ACCEPT'

        eleza cmd_ENABLE(self, tag, args):
            self._send_tagged(tag, 'OK', 'ENABLE successful')

        eleza cmd_AUTHENTICATE(self, tag, args):
            self._send_textline('+')
            self.server.response = tuma
            self._send_tagged(tag, 'OK', 'FAKEAUTH successful')

    @reap_threads
    eleza test_enable_raises_error_if_not_AUTH(self):
        ukijumuisha self.reaped_pair(self.UTF8Server) kama (server, client):
            self.assertUongo(client.utf8_enabled)
            self.assertRaises(imaplib.IMAP4.error, client.enable, 'foo')
            self.assertUongo(client.utf8_enabled)

    # XXX Also need a test that enable after SELECT raises an error.

    @reap_threads
    eleza test_enable_raises_error_if_no_capability(self):
        kundi NoEnableServer(self.UTF8Server):
            capabilities = 'AUTH'
        ukijumuisha self.reaped_pair(NoEnableServer) kama (server, client):
            self.assertRaises(imaplib.IMAP4.error, client.enable, 'foo')

    @reap_threads
    eleza test_enable_UTF8_raises_error_if_not_supported(self):
        kundi NonUTF8Server(SimpleIMAPHandler):
            pita
        ukijumuisha self.assertRaises(imaplib.IMAP4.error):
            ukijumuisha self.reaped_pair(NonUTF8Server) kama (server, client):
                typ, data = client.login('user', 'pita')
                self.assertEqual(typ, 'OK')
                client.enable('UTF8=ACCEPT')
                pita

    @reap_threads
    eleza test_enable_UTF8_Kweli_append(self):

        kundi UTF8AppendServer(self.UTF8Server):
            eleza cmd_APPEND(self, tag, args):
                self._send_textline('+')
                self.server.response = tuma
                self._send_tagged(tag, 'OK', 'okay')

        ukijumuisha self.reaped_pair(UTF8AppendServer) kama (server, client):
            self.assertEqual(client._encoding, 'ascii')
            code, _ = client.authenticate('MYAUTH', lambda x: b'fake')
            self.assertEqual(code, 'OK')
            self.assertEqual(server.response,
                             b'ZmFrZQ==\r\n')  # b64 encoded 'fake'
            code, _ = client.enable('UTF8=ACCEPT')
            self.assertEqual(code, 'OK')
            self.assertEqual(client._encoding, 'utf-8')
            msg_string = 'Subject: üñí©öðé'
            typ, data = client.append(
                Tupu, Tupu, Tupu, msg_string.encode('utf-8'))
            self.assertEqual(typ, 'OK')
            self.assertEqual(
                server.response,
                ('UTF8 (%s)\r\n' % msg_string).encode('utf-8')
            )

    # XXX also need a test that makes sure that the Literal na Untagged_status
    # regexes uses unicode kwenye UTF8 mode instead of the default ASCII.

    @reap_threads
    eleza test_search_disallows_charset_in_utf8_mode(self):
        ukijumuisha self.reaped_pair(self.UTF8Server) kama (server, client):
            typ, _ = client.authenticate('MYAUTH', lambda x: b'fake')
            self.assertEqual(typ, 'OK')
            typ, _ = client.enable('UTF8=ACCEPT')
            self.assertEqual(typ, 'OK')
            self.assertKweli(client.utf8_enabled)
            self.assertRaises(imaplib.IMAP4.error, client.search, 'foo', 'bar')

    @reap_threads
    eleza test_bad_auth_name(self):

        kundi MyServer(SimpleIMAPHandler):

            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_tagged(tag, 'NO', 'unrecognized authentication '
                                  'type {}'.format(args[0]))

        ukijumuisha self.reaped_pair(MyServer) kama (server, client):
            ukijumuisha self.assertRaises(imaplib.IMAP4.error):
                client.authenticate('METHOD', lambda: 1)

    @reap_threads
    eleza test_invalid_authentication(self):

        kundi MyServer(SimpleIMAPHandler):

            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.response = tuma
                self._send_tagged(tag, 'NO', '[AUTHENTICATIONFAILED] invalid')

        ukijumuisha self.reaped_pair(MyServer) kama (server, client):
            ukijumuisha self.assertRaises(imaplib.IMAP4.error):
                code, data = client.authenticate('MYAUTH', lambda x: b'fake')

    @reap_threads
    eleza test_valid_authentication(self):

        kundi MyServer(SimpleIMAPHandler):

            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.server.response = tuma
                self._send_tagged(tag, 'OK', 'FAKEAUTH successful')

        ukijumuisha self.reaped_pair(MyServer) kama (server, client):
            code, data = client.authenticate('MYAUTH', lambda x: b'fake')
            self.assertEqual(code, 'OK')
            self.assertEqual(server.response,
                             b'ZmFrZQ==\r\n')  # b64 encoded 'fake'

        ukijumuisha self.reaped_pair(MyServer) kama (server, client):
            code, data = client.authenticate('MYAUTH', lambda x: 'fake')
            self.assertEqual(code, 'OK')
            self.assertEqual(server.response,
                             b'ZmFrZQ==\r\n')  # b64 encoded 'fake'

    @reap_threads
    @requires_hashdigest('md5')
    eleza test_login_cram_md5(self):

        kundi AuthHandler(SimpleIMAPHandler):

            capabilities = 'LOGINDISABLED AUTH=CRAM-MD5'

            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+ PDE4OTYuNjk3MTcwOTUyQHBvc3RvZmZpY2Uucm'
                                    'VzdG9uLm1jaS5uZXQ=')
                r = tuma
                ikiwa (r == b'dGltIGYxY2E2YmU0NjRiOWVmYT'
                         b'FjY2E2ZmZkNmNmMmQ5ZjMy\r\n'):
                    self._send_tagged(tag, 'OK', 'CRAM-MD5 successful')
                isipokua:
                    self._send_tagged(tag, 'NO', 'No access')

        ukijumuisha self.reaped_pair(AuthHandler) kama (server, client):
            self.assertKweli('AUTH=CRAM-MD5' kwenye client.capabilities)
            ret, data = client.login_cram_md5("tim", "tanstaaftanstaaf")
            self.assertEqual(ret, "OK")

        ukijumuisha self.reaped_pair(AuthHandler) kama (server, client):
            self.assertKweli('AUTH=CRAM-MD5' kwenye client.capabilities)
            ret, data = client.login_cram_md5("tim", b"tanstaaftanstaaf")
            self.assertEqual(ret, "OK")


    @reap_threads
    eleza test_aborted_authentication(self):

        kundi MyServer(SimpleIMAPHandler):

            eleza cmd_AUTHENTICATE(self, tag, args):
                self._send_textline('+')
                self.response = tuma

                ikiwa self.response == b'*\r\n':
                    self._send_tagged(tag, 'NO', '[AUTHENTICATIONFAILED] aborted')
                isipokua:
                    self._send_tagged(tag, 'OK', 'MYAUTH successful')

        ukijumuisha self.reaped_pair(MyServer) kama (server, client):
            ukijumuisha self.assertRaises(imaplib.IMAP4.error):
                code, data = client.authenticate('MYAUTH', lambda x: Tupu)


    eleza test_linetoolong(self):
        kundi TooLongHandler(SimpleIMAPHandler):
            eleza handle(self):
                # Send a very long response line
                self.wfile.write(b'* OK ' + imaplib._MAXLINE * b'x' + b'\r\n')

        ukijumuisha self.reaped_server(TooLongHandler) kama server:
            self.assertRaises(imaplib.IMAP4.error,
                              self.imap_class, *server.server_address)

    @reap_threads
    eleza test_simple_with_statement(self):
        # simplest call
        ukijumuisha self.reaped_server(SimpleIMAPHandler) kama server:
            ukijumuisha self.imap_class(*server.server_address):
                pita

    @reap_threads
    eleza test_with_statement(self):
        ukijumuisha self.reaped_server(SimpleIMAPHandler) kama server:
            ukijumuisha self.imap_class(*server.server_address) kama imap:
                imap.login('user', 'pita')
                self.assertEqual(server.logged, 'user')
            self.assertIsTupu(server.logged)

    @reap_threads
    eleza test_with_statement_logout(self):
        # what happens ikiwa already logout kwenye the block?
        ukijumuisha self.reaped_server(SimpleIMAPHandler) kama server:
            ukijumuisha self.imap_class(*server.server_address) kama imap:
                imap.login('user', 'pita')
                self.assertEqual(server.logged, 'user')
                imap.logout()
                self.assertIsTupu(server.logged)
            self.assertIsTupu(server.logged)


@unittest.skipUnless(ssl, "SSL sio available")
kundi ThreadedNetworkedTestsSSL(ThreadedNetworkedTests):
    server_class = SecureTCPServer
    imap_class = IMAP4_SSL

    @reap_threads
    eleza test_ssl_verified(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(CAFILE)

        ukijumuisha self.assertRaisesRegex(
                ssl.CertificateError,
                "IP address mismatch, certificate ni sio valid kila "
                "'127.0.0.1'"):
            ukijumuisha self.reaped_server(SimpleIMAPHandler) kama server:
                client = self.imap_class(*server.server_address,
                                         ssl_context=ssl_context)
                client.shutdown()

        ukijumuisha self.reaped_server(SimpleIMAPHandler) kama server:
            client = self.imap_class("localhost", server.server_address[1],
                                     ssl_context=ssl_context)
            client.shutdown()


@unittest.skipUnless(
    support.is_resource_enabled('network'), 'network resource disabled')
kundi RemoteIMAPTest(unittest.TestCase):
    host = 'cyrus.andrew.cmu.edu'
    port = 143
    username = 'anonymous'
    pitaword = 'pita'
    imap_class = imaplib.IMAP4

    eleza setUp(self):
        ukijumuisha transient_internet(self.host):
            self.server = self.imap_class(self.host, self.port)

    eleza tearDown(self):
        ikiwa self.server ni sio Tupu:
            ukijumuisha transient_internet(self.host):
                self.server.logout()

    eleza test_logincapa(self):
        ukijumuisha transient_internet(self.host):
            kila cap kwenye self.server.capabilities:
                self.assertIsInstance(cap, str)
            self.assertIn('LOGINDISABLED', self.server.capabilities)
            self.assertIn('AUTH=ANONYMOUS', self.server.capabilities)
            rs = self.server.login(self.username, self.pitaword)
            self.assertEqual(rs[0], 'OK')

    eleza test_logout(self):
        ukijumuisha transient_internet(self.host):
            rs = self.server.logout()
            self.server = Tupu
            self.assertEqual(rs[0], 'BYE', rs)


@unittest.skipUnless(ssl, "SSL sio available")
@unittest.skipUnless(
    support.is_resource_enabled('network'), 'network resource disabled')
kundi RemoteIMAP_STARTTLSTest(RemoteIMAPTest):

    eleza setUp(self):
        super().setUp()
        ukijumuisha transient_internet(self.host):
            rs = self.server.starttls()
            self.assertEqual(rs[0], 'OK')

    eleza test_logincapa(self):
        kila cap kwenye self.server.capabilities:
            self.assertIsInstance(cap, str)
        self.assertNotIn('LOGINDISABLED', self.server.capabilities)


@unittest.skipUnless(ssl, "SSL sio available")
kundi RemoteIMAP_SSLTest(RemoteIMAPTest):
    port = 993
    imap_class = IMAP4_SSL

    eleza setUp(self):
        pita

    eleza tearDown(self):
        pita

    eleza create_ssl_context(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = Uongo
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.load_cert_chain(CERTFILE)
        rudisha ssl_context

    eleza check_logincapa(self, server):
        jaribu:
            kila cap kwenye server.capabilities:
                self.assertIsInstance(cap, str)
            self.assertNotIn('LOGINDISABLED', server.capabilities)
            self.assertIn('AUTH=PLAIN', server.capabilities)
            rs = server.login(self.username, self.pitaword)
            self.assertEqual(rs[0], 'OK')
        mwishowe:
            server.logout()

    eleza test_logincapa(self):
        ukijumuisha transient_internet(self.host):
            _server = self.imap_class(self.host, self.port)
            self.check_logincapa(_server)

    eleza test_logout(self):
        ukijumuisha transient_internet(self.host):
            _server = self.imap_class(self.host, self.port)
            rs = _server.logout()
            self.assertEqual(rs[0], 'BYE', rs)

    eleza test_ssl_context_certfile_exclusive(self):
        ukijumuisha transient_internet(self.host):
            self.assertRaises(
                ValueError, self.imap_class, self.host, self.port,
                certfile=CERTFILE, ssl_context=self.create_ssl_context())

    eleza test_ssl_context_keyfile_exclusive(self):
        ukijumuisha transient_internet(self.host):
            self.assertRaises(
                ValueError, self.imap_class, self.host, self.port,
                keyfile=CERTFILE, ssl_context=self.create_ssl_context())


ikiwa __name__ == "__main__":
    unittest.main()
