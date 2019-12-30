"""Unit tests kila socket timeout feature."""

agiza functools
agiza unittest
kutoka test agiza support

# This requires the 'network' resource kama given on the regrtest command line.
skip_expected = sio support.is_resource_enabled('network')

agiza time
agiza errno
agiza socket


@functools.lru_cache()
eleza resolve_address(host, port):
    """Resolve an (host, port) to an address.

    We must perform name resolution before timeout tests, otherwise it will be
    performed by connect().
    """
    ukijumuisha support.transient_internet(host):
        rudisha socket.getaddrinfo(host, port, socket.AF_INET,
                                  socket.SOCK_STREAM)[0][4]


kundi CreationTestCase(unittest.TestCase):
    """Test case kila socket.gettimeout() na socket.settimeout()"""

    eleza setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    eleza tearDown(self):
        self.sock.close()

    eleza testObjectCreation(self):
        # Test Socket creation
        self.assertEqual(self.sock.gettimeout(), Tupu,
                         "timeout sio disabled by default")

    eleza testFloatReturnValue(self):
        # Test rudisha value of gettimeout()
        self.sock.settimeout(7.345)
        self.assertEqual(self.sock.gettimeout(), 7.345)

        self.sock.settimeout(3)
        self.assertEqual(self.sock.gettimeout(), 3)

        self.sock.settimeout(Tupu)
        self.assertEqual(self.sock.gettimeout(), Tupu)

    eleza testReturnType(self):
        # Test rudisha type of gettimeout()
        self.sock.settimeout(1)
        self.assertEqual(type(self.sock.gettimeout()), type(1.0))

        self.sock.settimeout(3.9)
        self.assertEqual(type(self.sock.gettimeout()), type(1.0))

    eleza testTypeCheck(self):
        # Test type checking by settimeout()
        self.sock.settimeout(0)
        self.sock.settimeout(0)
        self.sock.settimeout(0.0)
        self.sock.settimeout(Tupu)
        self.assertRaises(TypeError, self.sock.settimeout, "")
        self.assertRaises(TypeError, self.sock.settimeout, "")
        self.assertRaises(TypeError, self.sock.settimeout, ())
        self.assertRaises(TypeError, self.sock.settimeout, [])
        self.assertRaises(TypeError, self.sock.settimeout, {})
        self.assertRaises(TypeError, self.sock.settimeout, 0j)

    eleza testRangeCheck(self):
        # Test range checking by settimeout()
        self.assertRaises(ValueError, self.sock.settimeout, -1)
        self.assertRaises(ValueError, self.sock.settimeout, -1)
        self.assertRaises(ValueError, self.sock.settimeout, -1.0)

    eleza testTimeoutThenBlocking(self):
        # Test settimeout() followed by setblocking()
        self.sock.settimeout(10)
        self.sock.setblocking(1)
        self.assertEqual(self.sock.gettimeout(), Tupu)
        self.sock.setblocking(0)
        self.assertEqual(self.sock.gettimeout(), 0.0)

        self.sock.settimeout(10)
        self.sock.setblocking(0)
        self.assertEqual(self.sock.gettimeout(), 0.0)
        self.sock.setblocking(1)
        self.assertEqual(self.sock.gettimeout(), Tupu)

    eleza testBlockingThenTimeout(self):
        # Test setblocking() followed by settimeout()
        self.sock.setblocking(0)
        self.sock.settimeout(1)
        self.assertEqual(self.sock.gettimeout(), 1)

        self.sock.setblocking(1)
        self.sock.settimeout(1)
        self.assertEqual(self.sock.gettimeout(), 1)


kundi TimeoutTestCase(unittest.TestCase):
    # There are a number of tests here trying to make sure that an operation
    # doesn't take too much longer than expected.  But competing machine
    # activity makes it inevitable that such tests will fail at times.
    # When fuzz was at 1.0, I (tim) routinely saw bogus failures on Win2K
    # na Win98SE.  Boosting it to 2.0 helped a lot, but isn't a real
    # solution.
    fuzz = 2.0

    localhost = support.HOST

    eleza setUp(self):
        ashiria NotImplementedError()

    tearDown = setUp

    eleza _sock_operation(self, count, timeout, method, *args):
        """
        Test the specified socket method.

        The method ni run at most `count` times na must ashiria a socket.timeout
        within `timeout` + self.fuzz seconds.
        """
        self.sock.settimeout(timeout)
        method = getattr(self.sock, method)
        kila i kwenye range(count):
            t1 = time.monotonic()
            jaribu:
                method(*args)
            tatizo socket.timeout kama e:
                delta = time.monotonic() - t1
                koma
        isipokua:
            self.fail('socket.timeout was sio raised')
        # These checks should account kila timing unprecision
        self.assertLess(delta, timeout + self.fuzz)
        self.assertGreater(delta, timeout - 1.0)


kundi TCPTimeoutTestCase(TimeoutTestCase):
    """TCP test case kila socket.socket() timeout functions"""

    eleza setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr_remote = resolve_address('www.python.org.', 80)

    eleza tearDown(self):
        self.sock.close()

    @unittest.skipIf(Kweli, 'need to replace these hosts; see bpo-35518')
    eleza testConnectTimeout(self):
        # Testing connect timeout ni tricky: we need to have IP connectivity
        # to a host that silently drops our packets.  We can't simulate this
        # kutoka Python because it's a function of the underlying TCP/IP stack.
        # So, the following Snakebite host has been defined:
        blackhole = resolve_address('blackhole.snakebite.net', 56666)

        # Blackhole has been configured to silently drop any incoming packets.
        # No RSTs (kila TCP) ama ICMP UNREACH (kila UDP/ICMP) will be sent back
        # to hosts that attempt to connect to this address: which ni exactly
        # what we need to confidently test connect timeout.

        # However, we want to prevent false positives.  It's sio unreasonable
        # to expect certain hosts may sio be able to reach the blackhole, due
        # to firewalling ama general network configuration.  In order to improve
        # our confidence kwenye testing the blackhole, a corresponding 'whitehole'
        # has also been set up using one port higher:
        whitehole = resolve_address('whitehole.snakebite.net', 56667)

        # This address has been configured to immediately drop any incoming
        # packets kama well, but it does it respectfully ukijumuisha regards to the
        # incoming protocol.  RSTs are sent kila TCP packets, na ICMP UNREACH
        # ni sent kila UDP/ICMP packets.  This means our attempts to connect to
        # it should be met immediately ukijumuisha ECONNREFUSED.  The test case has
        # been structured around this premise: ikiwa we get an ECONNREFUSED from
        # the whitehole, we proceed ukijumuisha testing connect timeout against the
        # blackhole.  If we don't, we skip the test (ukijumuisha a message about sio
        # getting the required RST kutoka the whitehole within the required
        # timeframe).

        # For the records, the whitehole/blackhole configuration has been set
        # up using the 'pf' firewall (available on BSDs), using the following:
        #
        #   ext_if="bge0"
        #
        #   blackhole_ip="35.8.247.6"
        #   whitehole_ip="35.8.247.6"
        #   blackhole_port="56666"
        #   whitehole_port="56667"
        #
        #   block rudisha kwenye log quick on $ext_ikiwa proto { tcp udp } \
        #       kutoka any to $whitehole_ip port $whitehole_port
        #   block drop kwenye log quick on $ext_ikiwa proto { tcp udp } \
        #       kutoka any to $blackhole_ip port $blackhole_port
        #

        skip = Kweli
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Use a timeout of 3 seconds.  Why 3?  Because it's more than 1, na
        # less than 5.  i.e. no particular reason.  Feel free to tweak it if
        # you feel a different value would be more appropriate.
        timeout = 3
        sock.settimeout(timeout)
        jaribu:
            sock.connect((whitehole))
        tatizo socket.timeout:
            pita
        tatizo OSError kama err:
            ikiwa err.errno == errno.ECONNREFUSED:
                skip = Uongo
        mwishowe:
            sock.close()
            toa sock

        ikiwa skip:
            self.skipTest(
                "We didn't receive a connection reset (RST) packet kutoka "
                "{}:{} within {} seconds, so we're unable to test connect "
                "timeout against the corresponding {}:{} (which ni "
                "configured to silently drop packets)."
                    .format(
                        whitehole[0],
                        whitehole[1],
                        timeout,
                        blackhole[0],
                        blackhole[1],
                    )
            )

        # All that hard work just to test ikiwa connect times out kwenye 0.001s ;-)
        self.addr_remote = blackhole
        ukijumuisha support.transient_internet(self.addr_remote[0]):
            self._sock_operation(1, 0.001, 'connect', self.addr_remote)

    eleza testRecvTimeout(self):
        # Test recv() timeout
        ukijumuisha support.transient_internet(self.addr_remote[0]):
            self.sock.connect(self.addr_remote)
            self._sock_operation(1, 1.5, 'recv', 1024)

    eleza testAcceptTimeout(self):
        # Test accept() timeout
        support.bind_port(self.sock, self.localhost)
        self.sock.listen()
        self._sock_operation(1, 1.5, 'accept')

    eleza testSend(self):
        # Test send() timeout
        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama serv:
            support.bind_port(serv, self.localhost)
            serv.listen()
            self.sock.connect(serv.getsockname())
            # Send a lot of data kwenye order to bypita buffering kwenye the TCP stack.
            self._sock_operation(100, 1.5, 'send', b"X" * 200000)

    eleza testSendto(self):
        # Test sendto() timeout
        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama serv:
            support.bind_port(serv, self.localhost)
            serv.listen()
            self.sock.connect(serv.getsockname())
            # The address argument ni ignored since we already connected.
            self._sock_operation(100, 1.5, 'sendto', b"X" * 200000,
                                 serv.getsockname())

    eleza testSendall(self):
        # Test sendall() timeout
        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama serv:
            support.bind_port(serv, self.localhost)
            serv.listen()
            self.sock.connect(serv.getsockname())
            # Send a lot of data kwenye order to bypita buffering kwenye the TCP stack.
            self._sock_operation(100, 1.5, 'sendall', b"X" * 200000)


kundi UDPTimeoutTestCase(TimeoutTestCase):
    """UDP test case kila socket.socket() timeout functions"""

    eleza setUp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    eleza tearDown(self):
        self.sock.close()

    eleza testRecvfromTimeout(self):
        # Test recvfrom() timeout
        # Prevent "Address already kwenye use" socket exceptions
        support.bind_port(self.sock, self.localhost)
        self._sock_operation(1, 1.5, 'recvfrom', 1024)


eleza test_main():
    support.requires('network')
    support.run_unittest(
        CreationTestCase,
        TCPTimeoutTestCase,
        UDPTimeoutTestCase,
    )

ikiwa __name__ == "__main__":
    test_main()
