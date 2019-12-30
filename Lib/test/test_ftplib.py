"""Test script kila ftplib module."""

# Modified by Giampaolo Rodola' to test FTP class, IPv6 na TLS
# environment

agiza ftplib
agiza asyncore
agiza asynchat
agiza socket
agiza io
agiza errno
agiza os
agiza threading
agiza time
jaribu:
    agiza ssl
tatizo ImportError:
    ssl = Tupu

kutoka unittest agiza TestCase, skipUnless
kutoka test agiza support
kutoka test.support agiza HOST, HOSTv6

TIMEOUT = 3
# the dummy data returned by server over the data channel when
# RETR, LIST, NLST, MLSD commands are issued
RETR_DATA = 'abcde12345\r\n' * 1000
LIST_DATA = 'foo\r\nbar\r\n'
NLST_DATA = 'foo\r\nbar\r\n'
MLSD_DATA = ("type=cdir;perm=el;unique==keVO1+ZF4; test\r\n"
             "type=pdir;perm=e;unique==keVO1+d?3; ..\r\n"
             "type=OS.unix=slink:/foobar;perm=;unique==keVO1+4G4; foobar\r\n"
             "type=OS.unix=chr-13/29;perm=;unique==keVO1+5G4; device\r\n"
             "type=OS.unix=blk-11/108;perm=;unique==keVO1+6G4; block\r\n"
             "type=file;perm=awr;unique==keVO1+8G4; writable\r\n"
             "type=dir;perm=cpmel;unique==keVO1+7G4; promiscuous\r\n"
             "type=dir;perm=;unique==keVO1+1t2; no-exec\r\n"
             "type=file;perm=r;unique==keVO1+EG4; two words\r\n"
             "type=file;perm=r;unique==keVO1+IH4;  leading space\r\n"
             "type=file;perm=r;unique==keVO1+1G4; file1\r\n"
             "type=dir;perm=cpmel;unique==keVO1+7G4; incoming\r\n"
             "type=file;perm=r;unique==keVO1+1G4; file2\r\n"
             "type=file;perm=r;unique==keVO1+1G4; file3\r\n"
             "type=file;perm=r;unique==keVO1+1G4; file4\r\n")


kundi DummyDTPHandler(asynchat.async_chat):
    dtp_conn_closed = Uongo

    eleza __init__(self, conn, baseclass):
        asynchat.async_chat.__init__(self, conn)
        self.basekundi = baseclass
        self.baseclass.last_received_data = ''

    eleza handle_read(self):
        self.baseclass.last_received_data += self.recv(1024).decode('ascii')

    eleza handle_close(self):
        # XXX: this method can be called many times kwenye a row kila a single
        # connection, including kwenye clear-text (non-TLS) mode.
        # (behaviour witnessed ukijumuisha test_data_connection)
        ikiwa sio self.dtp_conn_closed:
            self.baseclass.push('226 transfer complete')
            self.close()
            self.dtp_conn_closed = Kweli

    eleza push(self, what):
        ikiwa self.baseclass.next_data ni sio Tupu:
            what = self.baseclass.next_data
            self.baseclass.next_data = Tupu
        ikiwa sio what:
            rudisha self.close_when_done()
        super(DummyDTPHandler, self).push(what.encode('ascii'))

    eleza handle_error(self):
        ashiria Exception


kundi DummyFTPHandler(asynchat.async_chat):

    dtp_handler = DummyDTPHandler

    eleza __init__(self, conn):
        asynchat.async_chat.__init__(self, conn)
        # tells the socket to handle urgent data inline (ABOR command)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_OOBINLINE, 1)
        self.set_terminator(b"\r\n")
        self.in_buffer = []
        self.dtp = Tupu
        self.last_received_cmd = Tupu
        self.last_received_data = ''
        self.next_response = ''
        self.next_data = Tupu
        self.rest = Tupu
        self.next_retr_data = RETR_DATA
        self.push('220 welcome')

    eleza collect_incoming_data(self, data):
        self.in_buffer.append(data)

    eleza found_terminator(self):
        line = b''.join(self.in_buffer).decode('ascii')
        self.in_buffer = []
        ikiwa self.next_response:
            self.push(self.next_response)
            self.next_response = ''
        cmd = line.split(' ')[0].lower()
        self.last_received_cmd = cmd
        space = line.find(' ')
        ikiwa space != -1:
            arg = line[space + 1:]
        isipokua:
            arg = ""
        ikiwa hasattr(self, 'cmd_' + cmd):
            method = getattr(self, 'cmd_' + cmd)
            method(arg)
        isipokua:
            self.push('550 command "%s" sio understood.' %cmd)

    eleza handle_error(self):
        ashiria Exception

    eleza push(self, data):
        asynchat.async_chat.push(self, data.encode('ascii') + b'\r\n')

    eleza cmd_port(self, arg):
        addr = list(map(int, arg.split(',')))
        ip = '%d.%d.%d.%d' %tuple(addr[:4])
        port = (addr[4] * 256) + addr[5]
        s = socket.create_connection((ip, port), timeout=TIMEOUT)
        self.dtp = self.dtp_handler(s, baseclass=self)
        self.push('200 active data connection established')

    eleza cmd_pasv(self, arg):
        ukijumuisha socket.create_server((self.socket.getsockname()[0], 0)) kama sock:
            sock.settimeout(TIMEOUT)
            ip, port = sock.getsockname()[:2]
            ip = ip.replace('.', ','); p1 = port / 256; p2 = port % 256
            self.push('227 entering pitaive mode (%s,%d,%d)' %(ip, p1, p2))
            conn, addr = sock.accept()
            self.dtp = self.dtp_handler(conn, baseclass=self)

    eleza cmd_eprt(self, arg):
        af, ip, port = arg.split(arg[0])[1:-1]
        port = int(port)
        s = socket.create_connection((ip, port), timeout=TIMEOUT)
        self.dtp = self.dtp_handler(s, baseclass=self)
        self.push('200 active data connection established')

    eleza cmd_epsv(self, arg):
        ukijumuisha socket.create_server((self.socket.getsockname()[0], 0),
                                  family=socket.AF_INET6) kama sock:
            sock.settimeout(TIMEOUT)
            port = sock.getsockname()[1]
            self.push('229 entering extended pitaive mode (|||%d|)' %port)
            conn, addr = sock.accept()
            self.dtp = self.dtp_handler(conn, baseclass=self)

    eleza cmd_echo(self, arg):
        # sends back the received string (used by the test suite)
        self.push(arg)

    eleza cmd_noop(self, arg):
        self.push('200 noop ok')

    eleza cmd_user(self, arg):
        self.push('331 username ok')

    eleza cmd_pita(self, arg):
        self.push('230 password ok')

    eleza cmd_acct(self, arg):
        self.push('230 acct ok')

    eleza cmd_rnfr(self, arg):
        self.push('350 rnfr ok')

    eleza cmd_rnto(self, arg):
        self.push('250 rnto ok')

    eleza cmd_dele(self, arg):
        self.push('250 dele ok')

    eleza cmd_cwd(self, arg):
        self.push('250 cwd ok')

    eleza cmd_size(self, arg):
        self.push('250 1000')

    eleza cmd_mkd(self, arg):
        self.push('257 "%s"' %arg)

    eleza cmd_rmd(self, arg):
        self.push('250 rmd ok')

    eleza cmd_pwd(self, arg):
        self.push('257 "pwd ok"')

    eleza cmd_type(self, arg):
        self.push('200 type ok')

    eleza cmd_quit(self, arg):
        self.push('221 quit ok')
        self.close()

    eleza cmd_abor(self, arg):
        self.push('226 abor ok')

    eleza cmd_stor(self, arg):
        self.push('125 stor ok')

    eleza cmd_rest(self, arg):
        self.rest = arg
        self.push('350 rest ok')

    eleza cmd_retr(self, arg):
        self.push('125 retr ok')
        ikiwa self.rest ni sio Tupu:
            offset = int(self.rest)
        isipokua:
            offset = 0
        self.dtp.push(self.next_retr_data[offset:])
        self.dtp.close_when_done()
        self.rest = Tupu

    eleza cmd_list(self, arg):
        self.push('125 list ok')
        self.dtp.push(LIST_DATA)
        self.dtp.close_when_done()

    eleza cmd_nlst(self, arg):
        self.push('125 nlst ok')
        self.dtp.push(NLST_DATA)
        self.dtp.close_when_done()

    eleza cmd_opts(self, arg):
        self.push('200 opts ok')

    eleza cmd_mlsd(self, arg):
        self.push('125 mlsd ok')
        self.dtp.push(MLSD_DATA)
        self.dtp.close_when_done()

    eleza cmd_setlongretr(self, arg):
        # For testing. Next RETR will rudisha long line.
        self.next_retr_data = 'x' * int(arg)
        self.push('125 setlongretr ok')


kundi DummyFTPServer(asyncore.dispatcher, threading.Thread):

    handler = DummyFTPHandler

    eleza __init__(self, address, af=socket.AF_INET):
        threading.Thread.__init__(self)
        asyncore.dispatcher.__init__(self)
        self.daemon = Kweli
        self.create_socket(af, socket.SOCK_STREAM)
        self.bind(address)
        self.listen(5)
        self.active = Uongo
        self.active_lock = threading.Lock()
        self.host, self.port = self.socket.getsockname()[:2]
        self.handler_instance = Tupu

    eleza start(self):
        assert sio self.active
        self.__flag = threading.Event()
        threading.Thread.start(self)
        self.__flag.wait()

    eleza run(self):
        self.active = Kweli
        self.__flag.set()
        wakati self.active na asyncore.socket_map:
            self.active_lock.acquire()
            asyncore.loop(timeout=0.1, count=1)
            self.active_lock.release()
        asyncore.close_all(ignore_all=Kweli)

    eleza stop(self):
        assert self.active
        self.active = Uongo
        self.join()

    eleza handle_accepted(self, conn, addr):
        self.handler_instance = self.handler(conn)

    eleza handle_connect(self):
        self.close()
    handle_read = handle_connect

    eleza writable(self):
        rudisha 0

    eleza handle_error(self):
        ashiria Exception


ikiwa ssl ni sio Tupu:

    CERTFILE = os.path.join(os.path.dirname(__file__), "keycert3.pem")
    CAFILE = os.path.join(os.path.dirname(__file__), "pycacert.pem")

    kundi SSLConnection(asyncore.dispatcher):
        """An asyncore.dispatcher subkundi supporting TLS/SSL."""

        _ssl_accepting = Uongo
        _ssl_closing = Uongo

        eleza secure_connection(self):
            context = ssl.SSLContext()
            context.load_cert_chain(CERTFILE)
            socket = context.wrap_socket(self.socket,
                                         suppress_ragged_eofs=Uongo,
                                         server_side=Kweli,
                                         do_handshake_on_connect=Uongo)
            self.del_channel()
            self.set_socket(socket)
            self._ssl_accepting = Kweli

        eleza _do_ssl_handshake(self):
            jaribu:
                self.socket.do_handshake()
            tatizo ssl.SSLError kama err:
                ikiwa err.args[0] kwenye (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    rudisha
                lasivyo err.args[0] == ssl.SSL_ERROR_EOF:
                    rudisha self.handle_close()
                # TODO: SSLError does sio expose alert information
                lasivyo "SSLV3_ALERT_BAD_CERTIFICATE" kwenye err.args[1]:
                    rudisha self.handle_close()
                raise
            tatizo OSError kama err:
                ikiwa err.args[0] == errno.ECONNABORTED:
                    rudisha self.handle_close()
            isipokua:
                self._ssl_accepting = Uongo

        eleza _do_ssl_shutdown(self):
            self._ssl_closing = Kweli
            jaribu:
                self.socket = self.socket.unwrap()
            tatizo ssl.SSLError kama err:
                ikiwa err.args[0] kwenye (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    rudisha
            tatizo OSError kama err:
                # Any "socket error" corresponds to a SSL_ERROR_SYSCALL rudisha
                # kutoka OpenSSL's SSL_shutdown(), corresponding to a
                # closed socket condition. See also:
                # http://www.mail-archive.com/openssl-users@openssl.org/msg60710.html
                pita
            self._ssl_closing = Uongo
            ikiwa getattr(self, '_ccc', Uongo) ni Uongo:
                super(SSLConnection, self).close()
            isipokua:
                pita

        eleza handle_read_event(self):
            ikiwa self._ssl_accepting:
                self._do_ssl_handshake()
            lasivyo self._ssl_closing:
                self._do_ssl_shutdown()
            isipokua:
                super(SSLConnection, self).handle_read_event()

        eleza handle_write_event(self):
            ikiwa self._ssl_accepting:
                self._do_ssl_handshake()
            lasivyo self._ssl_closing:
                self._do_ssl_shutdown()
            isipokua:
                super(SSLConnection, self).handle_write_event()

        eleza send(self, data):
            jaribu:
                rudisha super(SSLConnection, self).send(data)
            tatizo ssl.SSLError kama err:
                ikiwa err.args[0] kwenye (ssl.SSL_ERROR_EOF, ssl.SSL_ERROR_ZERO_RETURN,
                                   ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    rudisha 0
                raise

        eleza recv(self, buffer_size):
            jaribu:
                rudisha super(SSLConnection, self).recv(buffer_size)
            tatizo ssl.SSLError kama err:
                ikiwa err.args[0] kwenye (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    rudisha b''
                ikiwa err.args[0] kwenye (ssl.SSL_ERROR_EOF, ssl.SSL_ERROR_ZERO_RETURN):
                    self.handle_close()
                    rudisha b''
                raise

        eleza handle_error(self):
            ashiria Exception

        eleza close(self):
            ikiwa (isinstance(self.socket, ssl.SSLSocket) na
                    self.socket._sslobj ni sio Tupu):
                self._do_ssl_shutdown()
            isipokua:
                super(SSLConnection, self).close()


    kundi DummyTLS_DTPHandler(SSLConnection, DummyDTPHandler):
        """A DummyDTPHandler subkundi supporting TLS/SSL."""

        eleza __init__(self, conn, baseclass):
            DummyDTPHandler.__init__(self, conn, baseclass)
            ikiwa self.baseclass.secure_data_channel:
                self.secure_connection()


    kundi DummyTLS_FTPHandler(SSLConnection, DummyFTPHandler):
        """A DummyFTPHandler subkundi supporting TLS/SSL."""

        dtp_handler = DummyTLS_DTPHandler

        eleza __init__(self, conn):
            DummyFTPHandler.__init__(self, conn)
            self.secure_data_channel = Uongo
            self._ccc = Uongo

        eleza cmd_auth(self, line):
            """Set up secure control channel."""
            self.push('234 AUTH TLS successful')
            self.secure_connection()

        eleza cmd_ccc(self, line):
            self.push('220 Reverting back to clear-text')
            self._ccc = Kweli
            self._do_ssl_shutdown()

        eleza cmd_pbsz(self, line):
            """Negotiate size of buffer kila secure data transfer.
            For TLS/SSL the only valid value kila the parameter ni '0'.
            Any other value ni accepted but ignored.
            """
            self.push('200 PBSZ=0 successful.')

        eleza cmd_prot(self, line):
            """Setup un/secure data channel."""
            arg = line.upper()
            ikiwa arg == 'C':
                self.push('200 Protection set to Clear')
                self.secure_data_channel = Uongo
            lasivyo arg == 'P':
                self.push('200 Protection set to Private')
                self.secure_data_channel = Kweli
            isipokua:
                self.push("502 Unrecognized PROT type (use C ama P).")


    kundi DummyTLS_FTPServer(DummyFTPServer):
        handler = DummyTLS_FTPHandler


kundi TestFTPClass(TestCase):

    eleza setUp(self):
        self.server = DummyFTPServer((HOST, 0))
        self.server.start()
        self.client = ftplib.FTP(timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)

    eleza tearDown(self):
        self.client.close()
        self.server.stop()
        # Explicitly clear the attribute to prevent dangling thread
        self.server = Tupu
        asyncore.close_all(ignore_all=Kweli)

    eleza check_data(self, received, expected):
        self.assertEqual(len(received), len(expected))
        self.assertEqual(received, expected)

    eleza test_getwelcome(self):
        self.assertEqual(self.client.getwelcome(), '220 welcome')

    eleza test_sanitize(self):
        self.assertEqual(self.client.sanitize('foo'), repr('foo'))
        self.assertEqual(self.client.sanitize('pita 12345'), repr('pita *****'))
        self.assertEqual(self.client.sanitize('PASS 12345'), repr('PASS *****'))

    eleza test_exceptions(self):
        self.assertRaises(ValueError, self.client.sendcmd, 'echo 40\r\n0')
        self.assertRaises(ValueError, self.client.sendcmd, 'echo 40\n0')
        self.assertRaises(ValueError, self.client.sendcmd, 'echo 40\r0')
        self.assertRaises(ftplib.error_temp, self.client.sendcmd, 'echo 400')
        self.assertRaises(ftplib.error_temp, self.client.sendcmd, 'echo 499')
        self.assertRaises(ftplib.error_perm, self.client.sendcmd, 'echo 500')
        self.assertRaises(ftplib.error_perm, self.client.sendcmd, 'echo 599')
        self.assertRaises(ftplib.error_proto, self.client.sendcmd, 'echo 999')

    eleza test_all_errors(self):
        exceptions = (ftplib.error_reply, ftplib.error_temp, ftplib.error_perm,
                      ftplib.error_proto, ftplib.Error, OSError,
                      EOFError)
        kila x kwenye exceptions:
            jaribu:
                ashiria x('exception sio inluded kwenye all_errors set')
            tatizo ftplib.all_errors:
                pita

    eleza test_set_pasv(self):
        # pitaive mode ni supposed to be enabled by default
        self.assertKweli(self.client.pitaiveserver)
        self.client.set_pasv(Kweli)
        self.assertKweli(self.client.pitaiveserver)
        self.client.set_pasv(Uongo)
        self.assertUongo(self.client.pitaiveserver)

    eleza test_voidcmd(self):
        self.client.voidcmd('echo 200')
        self.client.voidcmd('echo 299')
        self.assertRaises(ftplib.error_reply, self.client.voidcmd, 'echo 199')
        self.assertRaises(ftplib.error_reply, self.client.voidcmd, 'echo 300')

    eleza test_login(self):
        self.client.login()

    eleza test_acct(self):
        self.client.acct('pitawd')

    eleza test_rename(self):
        self.client.rename('a', 'b')
        self.server.handler_instance.next_response = '200'
        self.assertRaises(ftplib.error_reply, self.client.rename, 'a', 'b')

    eleza test_delete(self):
        self.client.delete('foo')
        self.server.handler_instance.next_response = '199'
        self.assertRaises(ftplib.error_reply, self.client.delete, 'foo')

    eleza test_size(self):
        self.client.size('foo')

    eleza test_mkd(self):
        dir = self.client.mkd('/foo')
        self.assertEqual(dir, '/foo')

    eleza test_rmd(self):
        self.client.rmd('foo')

    eleza test_cwd(self):
        dir = self.client.cwd('/foo')
        self.assertEqual(dir, '250 cwd ok')

    eleza test_pwd(self):
        dir = self.client.pwd()
        self.assertEqual(dir, 'pwd ok')

    eleza test_quit(self):
        self.assertEqual(self.client.quit(), '221 quit ok')
        # Ensure the connection gets closed; sock attribute should be Tupu
        self.assertEqual(self.client.sock, Tupu)

    eleza test_abort(self):
        self.client.abort()

    eleza test_retrbinary(self):
        eleza callback(data):
            received.append(data.decode('ascii'))
        received = []
        self.client.retrbinary('retr', callback)
        self.check_data(''.join(received), RETR_DATA)

    eleza test_retrbinary_rest(self):
        eleza callback(data):
            received.append(data.decode('ascii'))
        kila rest kwenye (0, 10, 20):
            received = []
            self.client.retrbinary('retr', callback, rest=rest)
            self.check_data(''.join(received), RETR_DATA[rest:])

    eleza test_retrlines(self):
        received = []
        self.client.retrlines('retr', received.append)
        self.check_data(''.join(received), RETR_DATA.replace('\r\n', ''))

    eleza test_storbinary(self):
        f = io.BytesIO(RETR_DATA.encode('ascii'))
        self.client.storbinary('stor', f)
        self.check_data(self.server.handler_instance.last_received_data, RETR_DATA)
        # test new callback arg
        flag = []
        f.seek(0)
        self.client.storbinary('stor', f, callback=lambda x: flag.append(Tupu))
        self.assertKweli(flag)

    eleza test_storbinary_rest(self):
        f = io.BytesIO(RETR_DATA.replace('\r\n', '\n').encode('ascii'))
        kila r kwenye (30, '30'):
            f.seek(0)
            self.client.storbinary('stor', f, rest=r)
            self.assertEqual(self.server.handler_instance.rest, str(r))

    eleza test_storlines(self):
        f = io.BytesIO(RETR_DATA.replace('\r\n', '\n').encode('ascii'))
        self.client.storlines('stor', f)
        self.check_data(self.server.handler_instance.last_received_data, RETR_DATA)
        # test new callback arg
        flag = []
        f.seek(0)
        self.client.storlines('stor foo', f, callback=lambda x: flag.append(Tupu))
        self.assertKweli(flag)

        f = io.StringIO(RETR_DATA.replace('\r\n', '\n'))
        # storlines() expects a binary file, sio a text file
        ukijumuisha support.check_warnings(('', BytesWarning), quiet=Kweli):
            self.assertRaises(TypeError, self.client.storlines, 'stor foo', f)

    eleza test_nlst(self):
        self.client.nlst()
        self.assertEqual(self.client.nlst(), NLST_DATA.split('\r\n')[:-1])

    eleza test_dir(self):
        l = []
        self.client.dir(lambda x: l.append(x))
        self.assertEqual(''.join(l), LIST_DATA.replace('\r\n', ''))

    eleza test_mlsd(self):
        list(self.client.mlsd())
        list(self.client.mlsd(path='/'))
        list(self.client.mlsd(path='/', facts=['size', 'type']))

        ls = list(self.client.mlsd())
        kila name, facts kwenye ls:
            self.assertIsInstance(name, str)
            self.assertIsInstance(facts, dict)
            self.assertKweli(name)
            self.assertIn('type', facts)
            self.assertIn('perm', facts)
            self.assertIn('unique', facts)

        eleza set_data(data):
            self.server.handler_instance.next_data = data

        eleza test_entry(line, type=Tupu, perm=Tupu, unique=Tupu, name=Tupu):
            type = 'type' ikiwa type ni Tupu isipokua type
            perm = 'perm' ikiwa perm ni Tupu isipokua perm
            unique = 'unique' ikiwa unique ni Tupu isipokua unique
            name = 'name' ikiwa name ni Tupu isipokua name
            set_data(line)
            _name, facts = next(self.client.mlsd())
            self.assertEqual(_name, name)
            self.assertEqual(facts['type'], type)
            self.assertEqual(facts['perm'], perm)
            self.assertEqual(facts['unique'], unique)

        # plain
        test_entry('type=type;perm=perm;unique=unique; name\r\n')
        # "=" kwenye fact value
        test_entry('type=ty=pe;perm=perm;unique=unique; name\r\n', type="ty=pe")
        test_entry('type==type;perm=perm;unique=unique; name\r\n', type="=type")
        test_entry('type=t=y=pe;perm=perm;unique=unique; name\r\n', type="t=y=pe")
        test_entry('type=====;perm=perm;unique=unique; name\r\n', type="====")
        # spaces kwenye name
        test_entry('type=type;perm=perm;unique=unique; na me\r\n', name="na me")
        test_entry('type=type;perm=perm;unique=unique; name \r\n', name="name ")
        test_entry('type=type;perm=perm;unique=unique;  name\r\n', name=" name")
        test_entry('type=type;perm=perm;unique=unique; n am  e\r\n', name="n am  e")
        # ";" kwenye name
        test_entry('type=type;perm=perm;unique=unique; na;me\r\n', name="na;me")
        test_entry('type=type;perm=perm;unique=unique; ;name\r\n', name=";name")
        test_entry('type=type;perm=perm;unique=unique; ;name;\r\n', name=";name;")
        test_entry('type=type;perm=perm;unique=unique; ;;;;\r\n', name=";;;;")
        # case sensitiveness
        set_data('Type=type;TyPe=perm;UNIQUE=unique; name\r\n')
        _name, facts = next(self.client.mlsd())
        kila x kwenye facts:
            self.assertKweli(x.islower())
        # no data (directory empty)
        set_data('')
        self.assertRaises(StopIteration, next, self.client.mlsd())
        set_data('')
        kila x kwenye self.client.mlsd():
            self.fail("unexpected data %s" % x)

    eleza test_makeport(self):
        ukijumuisha self.client.makeport():
            # IPv4 ni kwenye use, just make sure send_eprt has sio been used
            self.assertEqual(self.server.handler_instance.last_received_cmd,
                                'port')

    eleza test_makepasv(self):
        host, port = self.client.makepasv()
        conn = socket.create_connection((host, port), timeout=TIMEOUT)
        conn.close()
        # IPv4 ni kwenye use, just make sure send_epsv has sio been used
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'pasv')

    eleza test_with_statement(self):
        self.client.quit()

        eleza is_client_connected():
            ikiwa self.client.sock ni Tupu:
                rudisha Uongo
            jaribu:
                self.client.sendcmd('noop')
            tatizo (OSError, EOFError):
                rudisha Uongo
            rudisha Kweli

        # base test
        ukijumuisha ftplib.FTP(timeout=TIMEOUT) kama self.client:
            self.client.connect(self.server.host, self.server.port)
            self.client.sendcmd('noop')
            self.assertKweli(is_client_connected())
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'quit')
        self.assertUongo(is_client_connected())

        # QUIT sent inside the ukijumuisha block
        ukijumuisha ftplib.FTP(timeout=TIMEOUT) kama self.client:
            self.client.connect(self.server.host, self.server.port)
            self.client.sendcmd('noop')
            self.client.quit()
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'quit')
        self.assertUongo(is_client_connected())

        # force a wrong response code to be sent on QUIT: error_perm
        # ni expected na the connection ni supposed to be closed
        jaribu:
            ukijumuisha ftplib.FTP(timeout=TIMEOUT) kama self.client:
                self.client.connect(self.server.host, self.server.port)
                self.client.sendcmd('noop')
                self.server.handler_instance.next_response = '550 error on quit'
        tatizo ftplib.error_perm kama err:
            self.assertEqual(str(err), '550 error on quit')
        isipokua:
            self.fail('Exception sio raised')
        # needed to give the threaded server some time to set the attribute
        # which otherwise would still be == 'noop'
        time.sleep(0.1)
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'quit')
        self.assertUongo(is_client_connected())

    eleza test_source_address(self):
        self.client.quit()
        port = support.find_unused_port()
        jaribu:
            self.client.connect(self.server.host, self.server.port,
                                source_address=(HOST, port))
            self.assertEqual(self.client.sock.getsockname()[1], port)
            self.client.quit()
        tatizo OSError kama e:
            ikiwa e.errno == errno.EADDRINUSE:
                self.skipTest("couldn't bind to port %d" % port)
            raise

    eleza test_source_address_pitaive_connection(self):
        port = support.find_unused_port()
        self.client.source_address = (HOST, port)
        jaribu:
            ukijumuisha self.client.transfercmd('list') kama sock:
                self.assertEqual(sock.getsockname()[1], port)
        tatizo OSError kama e:
            ikiwa e.errno == errno.EADDRINUSE:
                self.skipTest("couldn't bind to port %d" % port)
            raise

    eleza test_parse257(self):
        self.assertEqual(ftplib.parse257('257 "/foo/bar"'), '/foo/bar')
        self.assertEqual(ftplib.parse257('257 "/foo/bar" created'), '/foo/bar')
        self.assertEqual(ftplib.parse257('257 ""'), '')
        self.assertEqual(ftplib.parse257('257 "" created'), '')
        self.assertRaises(ftplib.error_reply, ftplib.parse257, '250 "/foo/bar"')
        # The 257 response ni supposed to include the directory
        # name na kwenye case it contains embedded double-quotes
        # they must be doubled (see RFC-959, chapter 7, appendix 2).
        self.assertEqual(ftplib.parse257('257 "/foo/b""ar"'), '/foo/b"ar')
        self.assertEqual(ftplib.parse257('257 "/foo/b""ar" created'), '/foo/b"ar')

    eleza test_line_too_long(self):
        self.assertRaises(ftplib.Error, self.client.sendcmd,
                          'x' * self.client.maxline * 2)

    eleza test_retrlines_too_long(self):
        self.client.sendcmd('SETLONGRETR %d' % (self.client.maxline * 2))
        received = []
        self.assertRaises(ftplib.Error,
                          self.client.retrlines, 'retr', received.append)

    eleza test_storlines_too_long(self):
        f = io.BytesIO(b'x' * self.client.maxline * 2)
        self.assertRaises(ftplib.Error, self.client.storlines, 'stor', f)


@skipUnless(support.IPV6_ENABLED, "IPv6 sio enabled")
kundi TestIPv6Environment(TestCase):

    eleza setUp(self):
        self.server = DummyFTPServer((HOSTv6, 0), af=socket.AF_INET6)
        self.server.start()
        self.client = ftplib.FTP(timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)

    eleza tearDown(self):
        self.client.close()
        self.server.stop()
        # Explicitly clear the attribute to prevent dangling thread
        self.server = Tupu
        asyncore.close_all(ignore_all=Kweli)

    eleza test_af(self):
        self.assertEqual(self.client.af, socket.AF_INET6)

    eleza test_makeport(self):
        ukijumuisha self.client.makeport():
            self.assertEqual(self.server.handler_instance.last_received_cmd,
                                'eprt')

    eleza test_makepasv(self):
        host, port = self.client.makepasv()
        conn = socket.create_connection((host, port), timeout=TIMEOUT)
        conn.close()
        self.assertEqual(self.server.handler_instance.last_received_cmd, 'epsv')

    eleza test_transfer(self):
        eleza retr():
            eleza callback(data):
                received.append(data.decode('ascii'))
            received = []
            self.client.retrbinary('retr', callback)
            self.assertEqual(len(''.join(received)), len(RETR_DATA))
            self.assertEqual(''.join(received), RETR_DATA)
        self.client.set_pasv(Kweli)
        retr()
        self.client.set_pasv(Uongo)
        retr()


@skipUnless(ssl, "SSL sio available")
kundi TestTLS_FTPClassMixin(TestFTPClass):
    """Repeat TestFTPClass tests starting the TLS layer kila both control
    na data connections first.
    """

    eleza setUp(self):
        self.server = DummyTLS_FTPServer((HOST, 0))
        self.server.start()
        self.client = ftplib.FTP_TLS(timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)
        # enable TLS
        self.client.auth()
        self.client.prot_p()


@skipUnless(ssl, "SSL sio available")
kundi TestTLS_FTPClass(TestCase):
    """Specific TLS_FTP kundi tests."""

    eleza setUp(self):
        self.server = DummyTLS_FTPServer((HOST, 0))
        self.server.start()
        self.client = ftplib.FTP_TLS(timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)

    eleza tearDown(self):
        self.client.close()
        self.server.stop()
        # Explicitly clear the attribute to prevent dangling thread
        self.server = Tupu
        asyncore.close_all(ignore_all=Kweli)

    eleza test_control_connection(self):
        self.assertNotIsInstance(self.client.sock, ssl.SSLSocket)
        self.client.auth()
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)

    eleza test_data_connection(self):
        # clear text
        ukijumuisha self.client.transfercmd('list') kama sock:
            self.assertNotIsInstance(sock, ssl.SSLSocket)
            self.assertEqual(sock.recv(1024), LIST_DATA.encode('ascii'))
        self.assertEqual(self.client.voidresp(), "226 transfer complete")

        # secured, after PROT P
        self.client.prot_p()
        ukijumuisha self.client.transfercmd('list') kama sock:
            self.assertIsInstance(sock, ssl.SSLSocket)
            # consume kutoka SSL socket to finalize handshake na avoid
            # "SSLError [SSL] shutdown wakati kwenye init"
            self.assertEqual(sock.recv(1024), LIST_DATA.encode('ascii'))
        self.assertEqual(self.client.voidresp(), "226 transfer complete")

        # PROT C ni issued, the connection must be kwenye cleartext again
        self.client.prot_c()
        ukijumuisha self.client.transfercmd('list') kama sock:
            self.assertNotIsInstance(sock, ssl.SSLSocket)
            self.assertEqual(sock.recv(1024), LIST_DATA.encode('ascii'))
        self.assertEqual(self.client.voidresp(), "226 transfer complete")

    eleza test_login(self):
        # login() ni supposed to implicitly secure the control connection
        self.assertNotIsInstance(self.client.sock, ssl.SSLSocket)
        self.client.login()
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)
        # make sure that AUTH TLS doesn't get issued again
        self.client.login()

    eleza test_auth_issued_twice(self):
        self.client.auth()
        self.assertRaises(ValueError, self.client.auth)

    eleza test_context(self):
        self.client.quit()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = Uongo
        ctx.verify_mode = ssl.CERT_NONE
        self.assertRaises(ValueError, ftplib.FTP_TLS, keyfile=CERTFILE,
                          context=ctx)
        self.assertRaises(ValueError, ftplib.FTP_TLS, certfile=CERTFILE,
                          context=ctx)
        self.assertRaises(ValueError, ftplib.FTP_TLS, certfile=CERTFILE,
                          keyfile=CERTFILE, context=ctx)

        self.client = ftplib.FTP_TLS(context=ctx, timeout=TIMEOUT)
        self.client.connect(self.server.host, self.server.port)
        self.assertNotIsInstance(self.client.sock, ssl.SSLSocket)
        self.client.auth()
        self.assertIs(self.client.sock.context, ctx)
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)

        self.client.prot_p()
        ukijumuisha self.client.transfercmd('list') kama sock:
            self.assertIs(sock.context, ctx)
            self.assertIsInstance(sock, ssl.SSLSocket)

    eleza test_ccc(self):
        self.assertRaises(ValueError, self.client.ccc)
        self.client.login(secure=Kweli)
        self.assertIsInstance(self.client.sock, ssl.SSLSocket)
        self.client.ccc()
        self.assertRaises(ValueError, self.client.sock.unwrap)

    @skipUnless(Uongo, "FIXME: bpo-32706")
    eleza test_check_hostname(self):
        self.client.quit()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertEqual(ctx.check_hostname, Kweli)
        ctx.load_verify_locations(CAFILE)
        self.client = ftplib.FTP_TLS(context=ctx, timeout=TIMEOUT)

        # 127.0.0.1 doesn't match SAN
        self.client.connect(self.server.host, self.server.port)
        ukijumuisha self.assertRaises(ssl.CertificateError):
            self.client.auth()
        # exception quits connection

        self.client.connect(self.server.host, self.server.port)
        self.client.prot_p()
        ukijumuisha self.assertRaises(ssl.CertificateError):
            ukijumuisha self.client.transfercmd("list") kama sock:
                pita
        self.client.quit()

        self.client.connect("localhost", self.server.port)
        self.client.auth()
        self.client.quit()

        self.client.connect("localhost", self.server.port)
        self.client.prot_p()
        ukijumuisha self.client.transfercmd("list") kama sock:
            pita


kundi TestTimeouts(TestCase):

    eleza setUp(self):
        self.evt = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(20)
        self.port = support.bind_port(self.sock)
        self.server_thread = threading.Thread(target=self.server)
        self.server_thread.daemon = Kweli
        self.server_thread.start()
        # Wait kila the server to be ready.
        self.evt.wait()
        self.evt.clear()
        self.old_port = ftplib.FTP.port
        ftplib.FTP.port = self.port

    eleza tearDown(self):
        ftplib.FTP.port = self.old_port
        self.server_thread.join()
        # Explicitly clear the attribute to prevent dangling thread
        self.server_thread = Tupu

    eleza server(self):
        # This method sets the evt 3 times:
        #  1) when the connection ni ready to be accepted.
        #  2) when it ni safe kila the caller to close the connection
        #  3) when we have closed the socket
        self.sock.listen()
        # (1) Signal the caller that we are ready to accept the connection.
        self.evt.set()
        jaribu:
            conn, addr = self.sock.accept()
        tatizo socket.timeout:
            pita
        isipokua:
            conn.sendall(b"1 Hola mundo\n")
            conn.shutdown(socket.SHUT_WR)
            # (2) Signal the caller that it ni safe to close the socket.
            self.evt.set()
            conn.close()
        mwishowe:
            self.sock.close()

    eleza testTimeoutDefault(self):
        # default -- use global socket timeout
        self.assertIsTupu(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        jaribu:
            ftp = ftplib.FTP(HOST)
        mwishowe:
            socket.setdefaulttimeout(Tupu)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()

    eleza testTimeoutTupu(self):
        # no timeout -- do sio use global socket timeout
        self.assertIsTupu(socket.getdefaulttimeout())
        socket.setdefaulttimeout(30)
        jaribu:
            ftp = ftplib.FTP(HOST, timeout=Tupu)
        mwishowe:
            socket.setdefaulttimeout(Tupu)
        self.assertIsTupu(ftp.sock.gettimeout())
        self.evt.wait()
        ftp.close()

    eleza testTimeoutValue(self):
        # a value
        ftp = ftplib.FTP(HOST, timeout=30)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()

    eleza testTimeoutConnect(self):
        ftp = ftplib.FTP()
        ftp.connect(HOST, timeout=30)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()

    eleza testTimeoutDifferentOrder(self):
        ftp = ftplib.FTP(timeout=30)
        ftp.connect(HOST)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()

    eleza testTimeoutDirectAccess(self):
        ftp = ftplib.FTP()
        ftp.timeout = 30
        ftp.connect(HOST)
        self.assertEqual(ftp.sock.gettimeout(), 30)
        self.evt.wait()
        ftp.close()


kundi MiscTestCase(TestCase):
    eleza test__all__(self):
        blacklist = {'MSG_OOB', 'FTP_PORT', 'MAXLINE', 'CRLF', 'B_CRLF',
                     'Error', 'parse150', 'parse227', 'parse229', 'parse257',
                     'print_line', 'ftpcp', 'test'}
        support.check__all__(self, ftplib, blacklist=blacklist)


eleza test_main():
    tests = [TestFTPClass, TestTimeouts,
             TestIPv6Environment,
             TestTLS_FTPClassMixin, TestTLS_FTPClass,
             MiscTestCase]

    thread_info = support.threading_setup()
    jaribu:
        support.run_unittest(*tests)
    mwishowe:
        support.threading_cleanup(*thread_info)


ikiwa __name__ == '__main__':
    test_main()
