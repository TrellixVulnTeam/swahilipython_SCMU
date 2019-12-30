agiza socket
agiza selectors
agiza telnetlib
agiza threading
agiza contextlib

kutoka test agiza support
agiza unittest

HOST = support.HOST

eleza server(evt, serv):
    serv.listen()
    evt.set()
    jaribu:
        conn, addr = serv.accept()
        conn.close()
    tatizo socket.timeout:
        pita
    mwishowe:
        serv.close()

kundi GeneralTests(unittest.TestCase):

    eleza setUp(self):
        self.evt = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(60)  # Safety net. Look issue 11812
        self.port = support.bind_port(self.sock)
        self.thread = threading.Thread(target=server, args=(self.evt,self.sock))
        self.thread.setDaemon(Kweli)
        self.thread.start()
        self.evt.wait()

    eleza tearDown(self):
        self.thread.join()
        toa self.thread  # Clear out any dangling Thread objects.

    eleza testBasic(self):
        # connects
        telnet = telnetlib.Telnet(HOST, self.port)
        telnet.sock.close()

    eleza testContextManager(self):
        ukijumuisha telnetlib.Telnet(HOST, self.port) kama tn:
            self.assertIsNotTupu(tn.get_socket())
        self.assertIsTupu(tn.get_socket())

    eleza testTimeoutDefault(self):
        self.assertKweli(socket.getdefaulttimeout() ni Tupu)
        socket.setdefaulttimeout(30)
        jaribu:
            telnet = telnetlib.Telnet(HOST, self.port)
        mwishowe:
            socket.setdefaulttimeout(Tupu)
        self.assertEqual(telnet.sock.gettimeout(), 30)
        telnet.sock.close()

    eleza testTimeoutTupu(self):
        # Tupu, having other default
        self.assertKweli(socket.getdefaulttimeout() ni Tupu)
        socket.setdefaulttimeout(30)
        jaribu:
            telnet = telnetlib.Telnet(HOST, self.port, timeout=Tupu)
        mwishowe:
            socket.setdefaulttimeout(Tupu)
        self.assertKweli(telnet.sock.gettimeout() ni Tupu)
        telnet.sock.close()

    eleza testTimeoutValue(self):
        telnet = telnetlib.Telnet(HOST, self.port, timeout=30)
        self.assertEqual(telnet.sock.gettimeout(), 30)
        telnet.sock.close()

    eleza testTimeoutOpen(self):
        telnet = telnetlib.Telnet()
        telnet.open(HOST, self.port, timeout=30)
        self.assertEqual(telnet.sock.gettimeout(), 30)
        telnet.sock.close()

    eleza testGetters(self):
        # Test telnet getter methods
        telnet = telnetlib.Telnet(HOST, self.port, timeout=30)
        t_sock = telnet.sock
        self.assertEqual(telnet.get_socket(), t_sock)
        self.assertEqual(telnet.fileno(), t_sock.fileno())
        telnet.sock.close()

kundi SocketStub(object):
    ''' a socket proxy that re-defines sendall() '''
    eleza __init__(self, reads=()):
        self.reads = list(reads)  # Intentionally make a copy.
        self.writes = []
        self.block = Uongo
    eleza sendall(self, data):
        self.writes.append(data)
    eleza recv(self, size):
        out = b''
        wakati self.reads na len(out) < size:
            out += self.reads.pop(0)
        ikiwa len(out) > size:
            self.reads.insert(0, out[size:])
            out = out[:size]
        rudisha out

kundi TelnetAlike(telnetlib.Telnet):
    eleza fileno(self):
        ashiria NotImplementedError()
    eleza close(self): pita
    eleza sock_avail(self):
        rudisha (sio self.sock.block)
    eleza msg(self, msg, *args):
        ukijumuisha support.captured_stdout() kama out:
            telnetlib.Telnet.msg(self, msg, *args)
        self._messages += out.getvalue()
        rudisha

kundi MockSelector(selectors.BaseSelector):

    eleza __init__(self):
        self.keys = {}

    @property
    eleza resolution(self):
        rudisha 1e-3

    eleza register(self, fileobj, events, data=Tupu):
        key = selectors.SelectorKey(fileobj, 0, events, data)
        self.keys[fileobj] = key
        rudisha key

    eleza unregister(self, fileobj):
        rudisha self.keys.pop(fileobj)

    eleza select(self, timeout=Tupu):
        block = Uongo
        kila fileobj kwenye self.keys:
            ikiwa isinstance(fileobj, TelnetAlike):
                block = fileobj.sock.block
                koma
        ikiwa block:
            rudisha []
        isipokua:
            rudisha [(key, key.events) kila key kwenye self.keys.values()]

    eleza get_map(self):
        rudisha self.keys


@contextlib.contextmanager
eleza test_socket(reads):
    eleza new_conn(*ignored):
        rudisha SocketStub(reads)
    jaribu:
        old_conn = socket.create_connection
        socket.create_connection = new_conn
        tuma Tupu
    mwishowe:
        socket.create_connection = old_conn
    rudisha

eleza test_telnet(reads=(), cls=TelnetAlike):
    ''' rudisha a telnetlib.Telnet object that uses a SocketStub with
        reads queued up to be read '''
    kila x kwenye reads:
        assert type(x) ni bytes, x
    ukijumuisha test_socket(reads):
        telnet = cls('dummy', 0)
        telnet._messages = '' # debuglevel output
    rudisha telnet

kundi ExpectAndReadTestCase(unittest.TestCase):
    eleza setUp(self):
        self.old_selector = telnetlib._TelnetSelector
        telnetlib._TelnetSelector = MockSelector
    eleza tearDown(self):
        telnetlib._TelnetSelector = self.old_selector

kundi ReadTests(ExpectAndReadTestCase):
    eleza test_read_until(self):
        """
        read_until(expected, timeout=Tupu)
        test the blocking version of read_util
        """
        want = [b'xxxmatchyyy']
        telnet = test_telnet(want)
        data = telnet.read_until(b'match')
        self.assertEqual(data, b'xxxmatch', msg=(telnet.cookedq, telnet.rawq, telnet.sock.reads))

        reads = [b'x' * 50, b'match', b'y' * 50]
        expect = b''.join(reads[:-1])
        telnet = test_telnet(reads)
        data = telnet.read_until(b'match')
        self.assertEqual(data, expect)


    eleza test_read_all(self):
        """
        read_all()
          Read all data until EOF; may block.
        """
        reads = [b'x' * 500, b'y' * 500, b'z' * 500]
        expect = b''.join(reads)
        telnet = test_telnet(reads)
        data = telnet.read_all()
        self.assertEqual(data, expect)
        rudisha

    eleza test_read_some(self):
        """
        read_some()
          Read at least one byte ama EOF; may block.
        """
        # test 'at least one byte'
        telnet = test_telnet([b'x' * 500])
        data = telnet.read_some()
        self.assertKweli(len(data) >= 1)
        # test EOF
        telnet = test_telnet()
        data = telnet.read_some()
        self.assertEqual(b'', data)

    eleza _read_eager(self, func_name):
        """
        read_*_eager()
          Read all data available already queued ama on the socket,
          without blocking.
        """
        want = b'x' * 100
        telnet = test_telnet([want])
        func = getattr(telnet, func_name)
        telnet.sock.block = Kweli
        self.assertEqual(b'', func())
        telnet.sock.block = Uongo
        data = b''
        wakati Kweli:
            jaribu:
                data += func()
            tatizo EOFError:
                koma
        self.assertEqual(data, want)

    eleza test_read_eager(self):
        # read_eager na read_very_eager make the same guarantees
        # (they behave differently but we only test the guarantees)
        self._read_eager('read_eager')
        self._read_eager('read_very_eager')
        # NB -- we need to test the IAC block which ni mentioned kwenye the
        # docstring but haiko kwenye the module docs

    eleza read_very_lazy(self):
        want = b'x' * 100
        telnet = test_telnet([want])
        self.assertEqual(b'', telnet.read_very_lazy())
        wakati telnet.sock.reads:
            telnet.fill_rawq()
        data = telnet.read_very_lazy()
        self.assertEqual(want, data)
        self.assertRaises(EOFError, telnet.read_very_lazy)

    eleza test_read_lazy(self):
        want = b'x' * 100
        telnet = test_telnet([want])
        self.assertEqual(b'', telnet.read_lazy())
        data = b''
        wakati Kweli:
            jaribu:
                read_data = telnet.read_lazy()
                data += read_data
                ikiwa sio read_data:
                    telnet.fill_rawq()
            tatizo EOFError:
                koma
            self.assertKweli(want.startswith(data))
        self.assertEqual(data, want)

kundi nego_collector(object):
    eleza __init__(self, sb_getter=Tupu):
        self.seen = b''
        self.sb_getter = sb_getter
        self.sb_seen = b''

    eleza do_nego(self, sock, cmd, opt):
        self.seen += cmd + opt
        ikiwa cmd == tl.SE na self.sb_getter:
            sb_data = self.sb_getter()
            self.sb_seen += sb_data

tl = telnetlib

kundi WriteTests(unittest.TestCase):
    '''The only thing that write does ni replace each tl.IAC for
    tl.IAC+tl.IAC'''

    eleza test_write(self):
        data_sample = [b'data sample without IAC',
                       b'data sample with' + tl.IAC + b' one IAC',
                       b'a few' + tl.IAC + tl.IAC + b' iacs' + tl.IAC,
                       tl.IAC,
                       b'']
        kila data kwenye data_sample:
            telnet = test_telnet()
            telnet.write(data)
            written = b''.join(telnet.sock.writes)
            self.assertEqual(data.replace(tl.IAC,tl.IAC+tl.IAC), written)

kundi OptionTests(unittest.TestCase):
    # RFC 854 commands
    cmds = [tl.AO, tl.AYT, tl.BRK, tl.EC, tl.EL, tl.GA, tl.IP, tl.NOP]

    eleza _test_command(self, data):
        """ helper kila testing IAC + cmd """
        telnet = test_telnet(data)
        data_len = len(b''.join(data))
        nego = nego_collector()
        telnet.set_option_negotiation_callback(nego.do_nego)
        txt = telnet.read_all()
        cmd = nego.seen
        self.assertKweli(len(cmd) > 0) # we expect at least one command
        self.assertIn(cmd[:1], self.cmds)
        self.assertEqual(cmd[1:2], tl.NOOPT)
        self.assertEqual(data_len, len(txt + cmd))
        nego.sb_getter = Tupu # koma the nego => telnet cycle

    eleza test_IAC_commands(self):
        kila cmd kwenye self.cmds:
            self._test_command([tl.IAC, cmd])
            self._test_command([b'x' * 100, tl.IAC, cmd, b'y'*100])
            self._test_command([b'x' * 10, tl.IAC, cmd, b'y'*10])
        # all at once
        self._test_command([tl.IAC + cmd kila (cmd) kwenye self.cmds])

    eleza test_SB_commands(self):
        # RFC 855, subnegotiations portion
        send = [tl.IAC + tl.SB + tl.IAC + tl.SE,
                tl.IAC + tl.SB + tl.IAC + tl.IAC + tl.IAC + tl.SE,
                tl.IAC + tl.SB + tl.IAC + tl.IAC + b'aa' + tl.IAC + tl.SE,
                tl.IAC + tl.SB + b'bb' + tl.IAC + tl.IAC + tl.IAC + tl.SE,
                tl.IAC + tl.SB + b'cc' + tl.IAC + tl.IAC + b'dd' + tl.IAC + tl.SE,
               ]
        telnet = test_telnet(send)
        nego = nego_collector(telnet.read_sb_data)
        telnet.set_option_negotiation_callback(nego.do_nego)
        txt = telnet.read_all()
        self.assertEqual(txt, b'')
        want_sb_data = tl.IAC + tl.IAC + b'aabb' + tl.IAC + b'cc' + tl.IAC + b'dd'
        self.assertEqual(nego.sb_seen, want_sb_data)
        self.assertEqual(b'', telnet.read_sb_data())
        nego.sb_getter = Tupu # koma the nego => telnet cycle

    eleza test_debuglevel_reads(self):
        # test all the various places that self.msg(...) ni called
        given_a_expect_b = [
            # Telnet.fill_rawq
            (b'a', ": recv b''\n"),
            # Telnet.process_rawq
            (tl.IAC + bytes([88]), ": IAC 88 sio recognized\n"),
            (tl.IAC + tl.DO + bytes([1]), ": IAC DO 1\n"),
            (tl.IAC + tl.DONT + bytes([1]), ": IAC DONT 1\n"),
            (tl.IAC + tl.WILL + bytes([1]), ": IAC WILL 1\n"),
            (tl.IAC + tl.WONT + bytes([1]), ": IAC WONT 1\n"),
           ]
        kila a, b kwenye given_a_expect_b:
            telnet = test_telnet([a])
            telnet.set_debuglevel(1)
            txt = telnet.read_all()
            self.assertIn(b, telnet._messages)
        rudisha

    eleza test_debuglevel_write(self):
        telnet = test_telnet()
        telnet.set_debuglevel(1)
        telnet.write(b'xxx')
        expected = "send b'xxx'\n"
        self.assertIn(expected, telnet._messages)

    eleza test_debug_accepts_str_port(self):
        # Issue 10695
        ukijumuisha test_socket([]):
            telnet = TelnetAlike('dummy', '0')
            telnet._messages = ''
        telnet.set_debuglevel(1)
        telnet.msg('test')
        self.assertRegex(telnet._messages, r'0.*test')


kundi ExpectTests(ExpectAndReadTestCase):
    eleza test_expect(self):
        """
        expect(expected, [timeout])
          Read until the expected string has been seen, ama a timeout is
          hit (default ni no timeout); may block.
        """
        want = [b'x' * 10, b'match', b'y' * 10]
        telnet = test_telnet(want)
        (_,_,data) = telnet.expect([b'match'])
        self.assertEqual(data, b''.join(want[:-1]))


ikiwa __name__ == '__main__':
    unittest.main()
