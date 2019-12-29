# Copyright 2007 Google Inc.
#  Licensed to PSF under a Contributor Agreement.

"""Unittest kila ipaddress module."""


agiza unittest
agiza re
agiza contextlib
agiza functools
agiza operator
agiza pickle
agiza ipaddress
agiza weakref
kutoka test.support agiza LARGEST, SMALLEST


kundi BaseTestCase(unittest.TestCase):
    # One big change kwenye ipaddress over the original ipaddr module is
    # error reporting that tries to assume users *don't know the rules*
    # kila what constitutes an RFC compliant IP address

    # Ensuring these errors are emitted correctly kwenye all relevant cases
    # meant moving to a more systematic test structure that allows the
    # test structure to map more directly to the module structure

    # Note that ikiwa the constructors are refactored so that addresses with
    # multiple problems get classified differently, that's OK - just
    # move the affected examples to the newly appropriate test case.

    # There ni some duplication between the original relatively ad hoc
    # test suite na the new systematic tests. While some redundancy in
    # testing ni considered preferable to accidentally deleting a valid
    # test, the original test suite will likely be reduced over time as
    # redundant tests are identified.

    @property
    eleza factory(self):
        ashiria NotImplementedError

    @contextlib.contextmanager
    eleza assertCleanError(self, exc_type, details, *args):
        """
        Ensure exception does sio display a context by default

        Wraps unittest.TestCase.assertRaisesRegex
        """
        ikiwa args:
            details = details % args
        cm = self.assertRaisesRegex(exc_type, details)
        ukijumuisha cm kama exc:
            tuma exc
        # Ensure we produce clean tracebacks on failure
        ikiwa exc.exception.__context__ ni sio Tupu:
            self.assertKweli(exc.exception.__suppress_context__)

    eleza assertAddressError(self, details, *args):
        """Ensure a clean AddressValueError"""
        rudisha self.assertCleanError(ipaddress.AddressValueError,
                                     details, *args)

    eleza assertNetmaskError(self, details, *args):
        """Ensure a clean NetmaskValueError"""
        rudisha self.assertCleanError(ipaddress.NetmaskValueError,
                                     details, *args)

    eleza assertInstancesEqual(self, lhs, rhs):
        """Check constructor arguments produce equivalent instances"""
        self.assertEqual(self.factory(lhs), self.factory(rhs))


kundi CommonTestMixin:

    eleza test_empty_address(self):
        ukijumuisha self.assertAddressError("Address cannot be empty"):
            self.factory("")

    eleza test_floats_rejected(self):
        ukijumuisha self.assertAddressError(re.escape(repr("1.0"))):
            self.factory(1.0)

    eleza test_not_an_index_issue15559(self):
        # Implementing __index__ makes kila a very nasty interaction ukijumuisha the
        # bytes constructor. Thus, we disallow implicit use kama an integer
        self.assertRaises(TypeError, operator.index, self.factory(1))
        self.assertRaises(TypeError, hex, self.factory(1))
        self.assertRaises(TypeError, bytes, self.factory(1))

    eleza pickle_test(self, addr):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.subTest(proto=proto):
                x = self.factory(addr)
                y = pickle.loads(pickle.dumps(x, proto))
                self.assertEqual(y, x)


kundi CommonTestMixin_v4(CommonTestMixin):

    eleza test_leading_zeros(self):
        self.assertInstancesEqual("000.000.000.000", "0.0.0.0")
        self.assertInstancesEqual("192.168.000.001", "192.168.0.1")
        self.assertInstancesEqual("016.016.016.016", "16.16.16.16")
        self.assertInstancesEqual("001.000.008.016", "1.0.8.16")

    eleza test_int(self):
        self.assertInstancesEqual(0, "0.0.0.0")
        self.assertInstancesEqual(3232235521, "192.168.0.1")

    eleza test_packed(self):
        self.assertInstancesEqual(bytes.kutokahex("00000000"), "0.0.0.0")
        self.assertInstancesEqual(bytes.kutokahex("c0a80001"), "192.168.0.1")

    eleza test_negative_ints_rejected(self):
        msg = "-1 (< 0) ni sio permitted kama an IPv4 address"
        ukijumuisha self.assertAddressError(re.escape(msg)):
            self.factory(-1)

    eleza test_large_ints_rejected(self):
        msg = "%d (>= 2**32) ni sio permitted kama an IPv4 address"
        ukijumuisha self.assertAddressError(re.escape(msg % 2**32)):
            self.factory(2**32)

    eleza test_bad_packed_length(self):
        eleza assertBadLength(length):
            addr = b'\0' * length
            msg = "%r (len %d != 4) ni sio permitted kama an IPv4 address"
            ukijumuisha self.assertAddressError(re.escape(msg % (addr, length))):
                self.factory(addr)

        assertBadLength(3)
        assertBadLength(5)


kundi CommonTestMixin_v6(CommonTestMixin):

    eleza test_leading_zeros(self):
        self.assertInstancesEqual("0000::0000", "::")
        self.assertInstancesEqual("000::c0a8:0001", "::c0a8:1")

    eleza test_int(self):
        self.assertInstancesEqual(0, "::")
        self.assertInstancesEqual(3232235521, "::c0a8:1")

    eleza test_packed(self):
        addr = b'\0'*12 + bytes.kutokahex("00000000")
        self.assertInstancesEqual(addr, "::")
        addr = b'\0'*12 + bytes.kutokahex("c0a80001")
        self.assertInstancesEqual(addr, "::c0a8:1")
        addr = bytes.kutokahex("c0a80001") + b'\0'*12
        self.assertInstancesEqual(addr, "c0a8:1::")

    eleza test_negative_ints_rejected(self):
        msg = "-1 (< 0) ni sio permitted kama an IPv6 address"
        ukijumuisha self.assertAddressError(re.escape(msg)):
            self.factory(-1)

    eleza test_large_ints_rejected(self):
        msg = "%d (>= 2**128) ni sio permitted kama an IPv6 address"
        ukijumuisha self.assertAddressError(re.escape(msg % 2**128)):
            self.factory(2**128)

    eleza test_bad_packed_length(self):
        eleza assertBadLength(length):
            addr = b'\0' * length
            msg = "%r (len %d != 16) ni sio permitted kama an IPv6 address"
            ukijumuisha self.assertAddressError(re.escape(msg % (addr, length))):
                self.factory(addr)
                self.factory(addr)

        assertBadLength(15)
        assertBadLength(17)


kundi AddressTestCase_v4(BaseTestCase, CommonTestMixin_v4):
    factory = ipaddress.IPv4Address

    eleza test_network_pitaed_as_address(self):
        addr = "127.0.0.1/24"
        ukijumuisha self.assertAddressError("Unexpected '/' kwenye %r", addr):
            ipaddress.IPv4Address(addr)

    eleza test_bad_address_split(self):
        eleza assertBadSplit(addr):
            ukijumuisha self.assertAddressError("Expected 4 octets kwenye %r", addr):
                ipaddress.IPv4Address(addr)

        assertBadSplit("127.0.1")
        assertBadSplit("42.42.42.42.42")
        assertBadSplit("42.42.42")
        assertBadSplit("42.42")
        assertBadSplit("42")
        assertBadSplit("42..42.42.42")
        assertBadSplit("42.42.42.42.")
        assertBadSplit("42.42.42.42...")
        assertBadSplit(".42.42.42.42")
        assertBadSplit("...42.42.42.42")
        assertBadSplit("016.016.016")
        assertBadSplit("016.016")
        assertBadSplit("016")
        assertBadSplit("000")
        assertBadSplit("0x0a.0x0a.0x0a")
        assertBadSplit("0x0a.0x0a")
        assertBadSplit("0x0a")
        assertBadSplit(".")
        assertBadSplit("bogus")
        assertBadSplit("bogus.com")
        assertBadSplit("1000")
        assertBadSplit("1000000000000000")
        assertBadSplit("192.168.0.1.com")

    eleza test_empty_octet(self):
        eleza assertBadOctet(addr):
            ukijumuisha self.assertAddressError("Empty octet sio permitted kwenye %r",
                                         addr):
                ipaddress.IPv4Address(addr)

        assertBadOctet("42..42.42")
        assertBadOctet("...")

    eleza test_invalid_characters(self):
        eleza assertBadOctet(addr, octet):
            msg = "Only decimal digits permitted kwenye %r kwenye %r" % (octet, addr)
            ukijumuisha self.assertAddressError(re.escape(msg)):
                ipaddress.IPv4Address(addr)

        assertBadOctet("0x0a.0x0a.0x0a.0x0a", "0x0a")
        assertBadOctet("0xa.0x0a.0x0a.0x0a", "0xa")
        assertBadOctet("42.42.42.-0", "-0")
        assertBadOctet("42.42.42.+0", "+0")
        assertBadOctet("42.42.42.-42", "-42")
        assertBadOctet("+1.+2.+3.4", "+1")
        assertBadOctet("1.2.3.4e0", "4e0")
        assertBadOctet("1.2.3.4::", "4::")
        assertBadOctet("1.a.2.3", "a")

    eleza test_octet_length(self):
        eleza assertBadOctet(addr, octet):
            msg = "At most 3 characters permitted kwenye %r kwenye %r"
            ukijumuisha self.assertAddressError(re.escape(msg % (octet, addr))):
                ipaddress.IPv4Address(addr)

        assertBadOctet("0000.000.000.000", "0000")
        assertBadOctet("12345.67899.-54321.-98765", "12345")

    eleza test_octet_limit(self):
        eleza assertBadOctet(addr, octet):
            msg = "Octet %d (> 255) sio permitted kwenye %r" % (octet, addr)
            ukijumuisha self.assertAddressError(re.escape(msg)):
                ipaddress.IPv4Address(addr)

        assertBadOctet("257.0.0.0", 257)
        assertBadOctet("192.168.0.999", 999)

    eleza test_pickle(self):
        self.pickle_test('192.0.2.1')

    eleza test_weakref(self):
        weakref.ref(self.factory('192.0.2.1'))


kundi AddressTestCase_v6(BaseTestCase, CommonTestMixin_v6):
    factory = ipaddress.IPv6Address

    eleza test_network_pitaed_as_address(self):
        addr = "::1/24"
        ukijumuisha self.assertAddressError("Unexpected '/' kwenye %r", addr):
            ipaddress.IPv6Address(addr)

    eleza test_bad_address_split_v6_not_enough_parts(self):
        eleza assertBadSplit(addr):
            msg = "At least 3 parts expected kwenye %r"
            ukijumuisha self.assertAddressError(msg, addr):
                ipaddress.IPv6Address(addr)

        assertBadSplit(":")
        assertBadSplit(":1")
        assertBadSplit("FEDC:9878")

    eleza test_bad_address_split_v6_too_many_colons(self):
        eleza assertBadSplit(addr):
            msg = "At most 8 colons permitted kwenye %r"
            ukijumuisha self.assertAddressError(msg, addr):
                ipaddress.IPv6Address(addr)

        assertBadSplit("9:8:7:6:5:4:3::2:1")
        assertBadSplit("10:9:8:7:6:5:4:3:2:1")
        assertBadSplit("::8:7:6:5:4:3:2:1")
        assertBadSplit("8:7:6:5:4:3:2:1::")
        # A trailing IPv4 address ni two parts
        assertBadSplit("10:9:8:7:6:5:4:3:42.42.42.42")

    eleza test_bad_address_split_v6_too_many_parts(self):
        eleza assertBadSplit(addr):
            msg = "Exactly 8 parts expected without '::' kwenye %r"
            ukijumuisha self.assertAddressError(msg, addr):
                ipaddress.IPv6Address(addr)

        assertBadSplit("3ffe:0:0:0:0:0:0:0:1")
        assertBadSplit("9:8:7:6:5:4:3:2:1")
        assertBadSplit("7:6:5:4:3:2:1")
        # A trailing IPv4 address ni two parts
        assertBadSplit("9:8:7:6:5:4:3:42.42.42.42")
        assertBadSplit("7:6:5:4:3:42.42.42.42")

    eleza test_bad_address_split_v6_too_many_parts_with_double_colon(self):
        eleza assertBadSplit(addr):
            msg = "Expected at most 7 other parts ukijumuisha '::' kwenye %r"
            ukijumuisha self.assertAddressError(msg, addr):
                ipaddress.IPv6Address(addr)

        assertBadSplit("1:2:3:4::5:6:7:8")

    eleza test_bad_address_split_v6_repeated_double_colon(self):
        eleza assertBadSplit(addr):
            msg = "At most one '::' permitted kwenye %r"
            ukijumuisha self.assertAddressError(msg, addr):
                ipaddress.IPv6Address(addr)

        assertBadSplit("3ffe::1::1")
        assertBadSplit("1::2::3::4:5")
        assertBadSplit("2001::db:::1")
        assertBadSplit("3ffe::1::")
        assertBadSplit("::3ffe::1")
        assertBadSplit(":3ffe::1::1")
        assertBadSplit("3ffe::1::1:")
        assertBadSplit(":3ffe::1::1:")
        assertBadSplit(":::")
        assertBadSplit('2001:db8:::1')

    eleza test_bad_address_split_v6_leading_colon(self):
        eleza assertBadSplit(addr):
            msg = "Leading ':' only permitted kama part of '::' kwenye %r"
            ukijumuisha self.assertAddressError(msg, addr):
                ipaddress.IPv6Address(addr)

        assertBadSplit(":2001:db8::1")
        assertBadSplit(":1:2:3:4:5:6:7")
        assertBadSplit(":1:2:3:4:5:6:")
        assertBadSplit(":6:5:4:3:2:1::")

    eleza test_bad_address_split_v6_trailing_colon(self):
        eleza assertBadSplit(addr):
            msg = "Trailing ':' only permitted kama part of '::' kwenye %r"
            ukijumuisha self.assertAddressError(msg, addr):
                ipaddress.IPv6Address(addr)

        assertBadSplit("2001:db8::1:")
        assertBadSplit("1:2:3:4:5:6:7:")
        assertBadSplit("::1.2.3.4:")
        assertBadSplit("::7:6:5:4:3:2:")

    eleza test_bad_v4_part_in(self):
        eleza assertBadAddressPart(addr, v4_error):
            ukijumuisha self.assertAddressError("%s kwenye %r", v4_error, addr):
                ipaddress.IPv6Address(addr)

        assertBadAddressPart("3ffe::1.net", "Expected 4 octets kwenye '1.net'")
        assertBadAddressPart("3ffe::127.0.1",
                             "Expected 4 octets kwenye '127.0.1'")
        assertBadAddressPart("::1.2.3",
                             "Expected 4 octets kwenye '1.2.3'")
        assertBadAddressPart("::1.2.3.4.5",
                             "Expected 4 octets kwenye '1.2.3.4.5'")
        assertBadAddressPart("3ffe::1.1.1.net",
                             "Only decimal digits permitted kwenye 'net' "
                             "in '1.1.1.net'")

    eleza test_invalid_characters(self):
        eleza assertBadPart(addr, part):
            msg = "Only hex digits permitted kwenye %r kwenye %r" % (part, addr)
            ukijumuisha self.assertAddressError(re.escape(msg)):
                ipaddress.IPv6Address(addr)

        assertBadPart("3ffe::goog", "goog")
        assertBadPart("3ffe::-0", "-0")
        assertBadPart("3ffe::+0", "+0")
        assertBadPart("3ffe::-1", "-1")
        assertBadPart("1.2.3.4::", "1.2.3.4")
        assertBadPart('1234:axy::b', "axy")

    eleza test_part_length(self):
        eleza assertBadPart(addr, part):
            msg = "At most 4 characters permitted kwenye %r kwenye %r"
            ukijumuisha self.assertAddressError(msg, part, addr):
                ipaddress.IPv6Address(addr)

        assertBadPart("::00000", "00000")
        assertBadPart("3ffe::10000", "10000")
        assertBadPart("02001:db8::", "02001")
        assertBadPart('2001:888888::1', "888888")

    eleza test_pickle(self):
        self.pickle_test('2001:db8::')

    eleza test_weakref(self):
        weakref.ref(self.factory('2001:db8::'))


kundi NetmaskTestMixin_v4(CommonTestMixin_v4):
    """Input validation on interfaces na networks ni very similar"""

    eleza test_no_mask(self):
        kila address kwenye ('1.2.3.4', 0x01020304, b'\x01\x02\x03\x04'):
            net = self.factory(address)
            self.assertEqual(str(net), '1.2.3.4/32')
            self.assertEqual(str(net.netmask), '255.255.255.255')
            self.assertEqual(str(net.hostmask), '0.0.0.0')
            # IPv4Network has prefixlen, but IPv4Interface doesn't.
            # Should we add it to IPv4Interface too? (bpo-36392)

    eleza test_split_netmask(self):
        addr = "1.2.3.4/32/24"
        ukijumuisha self.assertAddressError("Only one '/' permitted kwenye %r" % addr):
            self.factory(addr)

    eleza test_address_errors(self):
        eleza assertBadAddress(addr, details):
            ukijumuisha self.assertAddressError(details):
                self.factory(addr)

        assertBadAddress("/", "Address cannot be empty")
        assertBadAddress("/8", "Address cannot be empty")
        assertBadAddress("bogus", "Expected 4 octets")
        assertBadAddress("google.com", "Expected 4 octets")
        assertBadAddress("10/8", "Expected 4 octets")
        assertBadAddress("::1.2.3.4", "Only decimal digits")
        assertBadAddress("1.2.3.256", re.escape("256 (> 255)"))

    eleza test_valid_netmask(self):
        self.assertEqual(str(self.factory('192.0.2.0/255.255.255.0')),
                         '192.0.2.0/24')
        kila i kwenye range(0, 33):
            # Generate na re-parse the CIDR format (trivial).
            net_str = '0.0.0.0/%d' % i
            net = self.factory(net_str)
            self.assertEqual(str(net), net_str)
            # Generate na re-parse the expanded netmask.
            self.assertEqual(
                str(self.factory('0.0.0.0/%s' % net.netmask)), net_str)
            # Zero prefix ni treated kama decimal.
            self.assertEqual(str(self.factory('0.0.0.0/0%d' % i)), net_str)
            # Generate na re-parse the expanded hostmask.  The ambiguous
            # cases (/0 na /32) are treated kama netmasks.
            ikiwa i kwenye (32, 0):
                net_str = '0.0.0.0/%d' % (32 - i)
            self.assertEqual(
                str(self.factory('0.0.0.0/%s' % net.hostmask)), net_str)

    eleza test_netmask_errors(self):
        eleza assertBadNetmask(addr, netmask):
            msg = "%r ni sio a valid netmask" % netmask
            ukijumuisha self.assertNetmaskError(re.escape(msg)):
                self.factory("%s/%s" % (addr, netmask))

        assertBadNetmask("1.2.3.4", "")
        assertBadNetmask("1.2.3.4", "-1")
        assertBadNetmask("1.2.3.4", "+1")
        assertBadNetmask("1.2.3.4", " 1 ")
        assertBadNetmask("1.2.3.4", "0x1")
        assertBadNetmask("1.2.3.4", "33")
        assertBadNetmask("1.2.3.4", "254.254.255.256")
        assertBadNetmask("1.2.3.4", "1.a.2.3")
        assertBadNetmask("1.1.1.1", "254.xyz.2.3")
        assertBadNetmask("1.1.1.1", "240.255.0.0")
        assertBadNetmask("1.1.1.1", "255.254.128.0")
        assertBadNetmask("1.1.1.1", "0.1.127.255")
        assertBadNetmask("1.1.1.1", "pudding")
        assertBadNetmask("1.1.1.1", "::")

    eleza test_netmask_in_tuple_errors(self):
        eleza assertBadNetmask(addr, netmask):
            msg = "%r ni sio a valid netmask" % netmask
            ukijumuisha self.assertNetmaskError(re.escape(msg)):
                self.factory((addr, netmask))
        assertBadNetmask("1.1.1.1", -1)
        assertBadNetmask("1.1.1.1", 33)

    eleza test_pickle(self):
        self.pickle_test('192.0.2.0/27')
        self.pickle_test('192.0.2.0/31')  # IPV4LENGTH - 1
        self.pickle_test('192.0.2.0')     # IPV4LENGTH


kundi InterfaceTestCase_v4(BaseTestCase, NetmaskTestMixin_v4):
    factory = ipaddress.IPv4Interface


kundi NetworkTestCase_v4(BaseTestCase, NetmaskTestMixin_v4):
    factory = ipaddress.IPv4Network

    eleza test_subnet_of(self):
        # containee left of container
        self.assertUongo(
            self.factory('10.0.0.0/30').subnet_of(
                self.factory('10.0.1.0/24')))
        # containee inside container
        self.assertKweli(
            self.factory('10.0.0.0/30').subnet_of(
                self.factory('10.0.0.0/24')))
        # containee right of container
        self.assertUongo(
            self.factory('10.0.0.0/30').subnet_of(
                self.factory('10.0.1.0/24')))
        # containee larger than container
        self.assertUongo(
            self.factory('10.0.1.0/24').subnet_of(
                self.factory('10.0.0.0/30')))

    eleza test_supernet_of(self):
        # containee left of container
        self.assertUongo(
            self.factory('10.0.0.0/30').supernet_of(
                self.factory('10.0.1.0/24')))
        # containee inside container
        self.assertUongo(
            self.factory('10.0.0.0/30').supernet_of(
                self.factory('10.0.0.0/24')))
        # containee right of container
        self.assertUongo(
            self.factory('10.0.0.0/30').supernet_of(
                self.factory('10.0.1.0/24')))
        # containee larger than container
        self.assertKweli(
            self.factory('10.0.0.0/24').supernet_of(
                self.factory('10.0.0.0/30')))

    eleza test_subnet_of_mixed_types(self):
        ukijumuisha self.assertRaises(TypeError):
            ipaddress.IPv4Network('10.0.0.0/30').supernet_of(
                ipaddress.IPv6Network('::1/128'))
        ukijumuisha self.assertRaises(TypeError):
            ipaddress.IPv6Network('::1/128').supernet_of(
                ipaddress.IPv4Network('10.0.0.0/30'))
        ukijumuisha self.assertRaises(TypeError):
            ipaddress.IPv4Network('10.0.0.0/30').subnet_of(
                ipaddress.IPv6Network('::1/128'))
        ukijumuisha self.assertRaises(TypeError):
            ipaddress.IPv6Network('::1/128').subnet_of(
                ipaddress.IPv4Network('10.0.0.0/30'))


kundi NetmaskTestMixin_v6(CommonTestMixin_v6):
    """Input validation on interfaces na networks ni very similar"""

    eleza test_no_mask(self):
        kila address kwenye ('::1', 1, b'\x00'*15 + b'\x01'):
            net = self.factory(address)
            self.assertEqual(str(net), '::1/128')
            self.assertEqual(str(net.netmask), 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
            self.assertEqual(str(net.hostmask), '::')
            # IPv6Network has prefixlen, but IPv6Interface doesn't.
            # Should we add it to IPv4Interface too? (bpo-36392)

    eleza test_split_netmask(self):
        addr = "cafe:cafe::/128/190"
        ukijumuisha self.assertAddressError("Only one '/' permitted kwenye %r" % addr):
            self.factory(addr)

    eleza test_address_errors(self):
        eleza assertBadAddress(addr, details):
            ukijumuisha self.assertAddressError(details):
                self.factory(addr)

        assertBadAddress("/", "Address cannot be empty")
        assertBadAddress("/8", "Address cannot be empty")
        assertBadAddress("google.com", "At least 3 parts")
        assertBadAddress("1.2.3.4", "At least 3 parts")
        assertBadAddress("10/8", "At least 3 parts")
        assertBadAddress("1234:axy::b", "Only hex digits")

    eleza test_valid_netmask(self):
        # We only support CIDR kila IPv6, because expanded netmasks are not
        # standard notation.
        self.assertEqual(str(self.factory('2001:db8::/32')), '2001:db8::/32')
        kila i kwenye range(0, 129):
            # Generate na re-parse the CIDR format (trivial).
            net_str = '::/%d' % i
            self.assertEqual(str(self.factory(net_str)), net_str)
            # Zero prefix ni treated kama decimal.
            self.assertEqual(str(self.factory('::/0%d' % i)), net_str)

    eleza test_netmask_errors(self):
        eleza assertBadNetmask(addr, netmask):
            msg = "%r ni sio a valid netmask" % netmask
            ukijumuisha self.assertNetmaskError(re.escape(msg)):
                self.factory("%s/%s" % (addr, netmask))

        assertBadNetmask("::1", "")
        assertBadNetmask("::1", "::1")
        assertBadNetmask("::1", "1::")
        assertBadNetmask("::1", "-1")
        assertBadNetmask("::1", "+1")
        assertBadNetmask("::1", " 1 ")
        assertBadNetmask("::1", "0x1")
        assertBadNetmask("::1", "129")
        assertBadNetmask("::1", "1.2.3.4")
        assertBadNetmask("::1", "pudding")
        assertBadNetmask("::", "::")

    eleza test_netmask_in_tuple_errors(self):
        eleza assertBadNetmask(addr, netmask):
            msg = "%r ni sio a valid netmask" % netmask
            ukijumuisha self.assertNetmaskError(re.escape(msg)):
                self.factory((addr, netmask))
        assertBadNetmask("::1", -1)
        assertBadNetmask("::1", 129)

    eleza test_pickle(self):
        self.pickle_test('2001:db8::1000/124')
        self.pickle_test('2001:db8::1000/127')  # IPV6LENGTH - 1
        self.pickle_test('2001:db8::1000')      # IPV6LENGTH


kundi InterfaceTestCase_v6(BaseTestCase, NetmaskTestMixin_v6):
    factory = ipaddress.IPv6Interface


kundi NetworkTestCase_v6(BaseTestCase, NetmaskTestMixin_v6):
    factory = ipaddress.IPv6Network

    eleza test_subnet_of(self):
        # containee left of container
        self.assertUongo(
            self.factory('2000:999::/56').subnet_of(
                self.factory('2000:aaa::/48')))
        # containee inside container
        self.assertKweli(
            self.factory('2000:aaa::/56').subnet_of(
                self.factory('2000:aaa::/48')))
        # containee right of container
        self.assertUongo(
            self.factory('2000:bbb::/56').subnet_of(
                self.factory('2000:aaa::/48')))
        # containee larger than container
        self.assertUongo(
            self.factory('2000:aaa::/48').subnet_of(
                self.factory('2000:aaa::/56')))

    eleza test_supernet_of(self):
        # containee left of container
        self.assertUongo(
            self.factory('2000:999::/56').supernet_of(
                self.factory('2000:aaa::/48')))
        # containee inside container
        self.assertUongo(
            self.factory('2000:aaa::/56').supernet_of(
                self.factory('2000:aaa::/48')))
        # containee right of container
        self.assertUongo(
            self.factory('2000:bbb::/56').supernet_of(
                self.factory('2000:aaa::/48')))
        # containee larger than container
        self.assertKweli(
            self.factory('2000:aaa::/48').supernet_of(
                self.factory('2000:aaa::/56')))


kundi FactoryFunctionErrors(BaseTestCase):

    eleza assertFactoryError(self, factory, kind):
        """Ensure a clean ValueError ukijumuisha the expected message"""
        addr = "camelot"
        msg = '%r does sio appear to be an IPv4 ama IPv6 %s'
        ukijumuisha self.assertCleanError(ValueError, msg, addr, kind):
            factory(addr)

    eleza test_ip_address(self):
        self.assertFactoryError(ipaddress.ip_address, "address")

    eleza test_ip_interface(self):
        self.assertFactoryError(ipaddress.ip_interface, "interface")

    eleza test_ip_network(self):
        self.assertFactoryError(ipaddress.ip_network, "network")


kundi ComparisonTests(unittest.TestCase):

    v4addr = ipaddress.IPv4Address(1)
    v4net = ipaddress.IPv4Network(1)
    v4intf = ipaddress.IPv4Interface(1)
    v6addr = ipaddress.IPv6Address(1)
    v6net = ipaddress.IPv6Network(1)
    v6intf = ipaddress.IPv6Interface(1)

    v4_addresses = [v4addr, v4intf]
    v4_objects = v4_addresses + [v4net]
    v6_addresses = [v6addr, v6intf]
    v6_objects = v6_addresses + [v6net]

    objects = v4_objects + v6_objects

    v4addr2 = ipaddress.IPv4Address(2)
    v4net2 = ipaddress.IPv4Network(2)
    v4intf2 = ipaddress.IPv4Interface(2)
    v6addr2 = ipaddress.IPv6Address(2)
    v6net2 = ipaddress.IPv6Network(2)
    v6intf2 = ipaddress.IPv6Interface(2)

    eleza test_foreign_type_equality(self):
        # __eq__ should never ashiria TypeError directly
        other = object()
        kila obj kwenye self.objects:
            self.assertNotEqual(obj, other)
            self.assertUongo(obj == other)
            self.assertEqual(obj.__eq__(other), NotImplemented)
            self.assertEqual(obj.__ne__(other), NotImplemented)

    eleza test_mixed_type_equality(self):
        # Ensure none of the internal objects accidentally
        # expose the right set of attributes to become "equal"
        kila lhs kwenye self.objects:
            kila rhs kwenye self.objects:
                ikiwa lhs ni rhs:
                    endelea
                self.assertNotEqual(lhs, rhs)

    eleza test_same_type_equality(self):
        kila obj kwenye self.objects:
            self.assertEqual(obj, obj)
            self.assertLessEqual(obj, obj)
            self.assertGreaterEqual(obj, obj)

    eleza test_same_type_ordering(self):
        kila lhs, rhs kwenye (
            (self.v4addr, self.v4addr2),
            (self.v4net, self.v4net2),
            (self.v4intf, self.v4intf2),
            (self.v6addr, self.v6addr2),
            (self.v6net, self.v6net2),
            (self.v6intf, self.v6intf2),
        ):
            self.assertNotEqual(lhs, rhs)
            self.assertLess(lhs, rhs)
            self.assertLessEqual(lhs, rhs)
            self.assertGreater(rhs, lhs)
            self.assertGreaterEqual(rhs, lhs)
            self.assertUongo(lhs > rhs)
            self.assertUongo(rhs < lhs)
            self.assertUongo(lhs >= rhs)
            self.assertUongo(rhs <= lhs)

    eleza test_containment(self):
        kila obj kwenye self.v4_addresses:
            self.assertIn(obj, self.v4net)
        kila obj kwenye self.v6_addresses:
            self.assertIn(obj, self.v6net)
        kila obj kwenye self.v4_objects + [self.v6net]:
            self.assertNotIn(obj, self.v6net)
        kila obj kwenye self.v6_objects + [self.v4net]:
            self.assertNotIn(obj, self.v4net)

    eleza test_mixed_type_ordering(self):
        kila lhs kwenye self.objects:
            kila rhs kwenye self.objects:
                ikiwa isinstance(lhs, type(rhs)) ama isinstance(rhs, type(lhs)):
                    endelea
                self.assertRaises(TypeError, lambda: lhs < rhs)
                self.assertRaises(TypeError, lambda: lhs > rhs)
                self.assertRaises(TypeError, lambda: lhs <= rhs)
                self.assertRaises(TypeError, lambda: lhs >= rhs)

    eleza test_foreign_type_ordering(self):
        other = object()
        kila obj kwenye self.objects:
            ukijumuisha self.assertRaises(TypeError):
                obj < other
            ukijumuisha self.assertRaises(TypeError):
                obj > other
            ukijumuisha self.assertRaises(TypeError):
                obj <= other
            ukijumuisha self.assertRaises(TypeError):
                obj >= other
            self.assertKweli(obj < LARGEST)
            self.assertUongo(obj > LARGEST)
            self.assertKweli(obj <= LARGEST)
            self.assertUongo(obj >= LARGEST)
            self.assertUongo(obj < SMALLEST)
            self.assertKweli(obj > SMALLEST)
            self.assertUongo(obj <= SMALLEST)
            self.assertKweli(obj >= SMALLEST)

    eleza test_mixed_type_key(self):
        # ukijumuisha get_mixed_type_key, you can sort addresses na network.
        v4_ordered = [self.v4addr, self.v4net, self.v4intf]
        v6_ordered = [self.v6addr, self.v6net, self.v6intf]
        self.assertEqual(v4_ordered,
                         sorted(self.v4_objects,
                                key=ipaddress.get_mixed_type_key))
        self.assertEqual(v6_ordered,
                         sorted(self.v6_objects,
                                key=ipaddress.get_mixed_type_key))
        self.assertEqual(v4_ordered + v6_ordered,
                         sorted(self.objects,
                                key=ipaddress.get_mixed_type_key))
        self.assertEqual(NotImplemented, ipaddress.get_mixed_type_key(object))

    eleza test_incompatible_versions(self):
        # These should always ashiria TypeError
        v4addr = ipaddress.ip_address('1.1.1.1')
        v4net = ipaddress.ip_network('1.1.1.1')
        v6addr = ipaddress.ip_address('::1')
        v6net = ipaddress.ip_network('::1')

        self.assertRaises(TypeError, v4addr.__lt__, v6addr)
        self.assertRaises(TypeError, v4addr.__gt__, v6addr)
        self.assertRaises(TypeError, v4net.__lt__, v6net)
        self.assertRaises(TypeError, v4net.__gt__, v6net)

        self.assertRaises(TypeError, v6addr.__lt__, v4addr)
        self.assertRaises(TypeError, v6addr.__gt__, v4addr)
        self.assertRaises(TypeError, v6net.__lt__, v4net)
        self.assertRaises(TypeError, v6net.__gt__, v4net)


kundi IpaddrUnitTest(unittest.TestCase):

    eleza setUp(self):
        self.ipv4_address = ipaddress.IPv4Address('1.2.3.4')
        self.ipv4_interface = ipaddress.IPv4Interface('1.2.3.4/24')
        self.ipv4_network = ipaddress.IPv4Network('1.2.3.0/24')
        #self.ipv4_hostmask = ipaddress.IPv4Interface('10.0.0.1/0.255.255.255')
        self.ipv6_address = ipaddress.IPv6Interface(
            '2001:658:22a:cafe:200:0:0:1')
        self.ipv6_interface = ipaddress.IPv6Interface(
            '2001:658:22a:cafe:200:0:0:1/64')
        self.ipv6_network = ipaddress.IPv6Network('2001:658:22a:cafe::/64')

    eleza testRepr(self):
        self.assertEqual("IPv4Interface('1.2.3.4/32')",
                         repr(ipaddress.IPv4Interface('1.2.3.4')))
        self.assertEqual("IPv6Interface('::1/128')",
                         repr(ipaddress.IPv6Interface('::1')))

    # issue #16531: constructing IPv4Network kutoka an (address, mask) tuple
    eleza testIPv4Tuple(self):
        # /32
        ip = ipaddress.IPv4Address('192.0.2.1')
        net = ipaddress.IPv4Network('192.0.2.1/32')
        self.assertEqual(ipaddress.IPv4Network(('192.0.2.1', 32)), net)
        self.assertEqual(ipaddress.IPv4Network((ip, 32)), net)
        self.assertEqual(ipaddress.IPv4Network((3221225985, 32)), net)
        self.assertEqual(ipaddress.IPv4Network(('192.0.2.1',
                                                '255.255.255.255')), net)
        self.assertEqual(ipaddress.IPv4Network((ip,
                                                '255.255.255.255')), net)
        self.assertEqual(ipaddress.IPv4Network((3221225985,
                                                '255.255.255.255')), net)
        # strict=Kweli na host bits set
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv4Network(('192.0.2.1', 24))
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv4Network((ip, 24))
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv4Network((3221225985, 24))
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv4Network(('192.0.2.1', '255.255.255.0'))
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv4Network((ip, '255.255.255.0'))
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv4Network((3221225985, '255.255.255.0'))
        # strict=Uongo na host bits set
        net = ipaddress.IPv4Network('192.0.2.0/24')
        self.assertEqual(ipaddress.IPv4Network(('192.0.2.1', 24),
                                               strict=Uongo), net)
        self.assertEqual(ipaddress.IPv4Network((ip, 24),
                                               strict=Uongo), net)
        self.assertEqual(ipaddress.IPv4Network((3221225985, 24),
                                               strict=Uongo), net)
        self.assertEqual(ipaddress.IPv4Network(('192.0.2.1',
                                                '255.255.255.0'),
                                               strict=Uongo), net)
        self.assertEqual(ipaddress.IPv4Network((ip,
                                                '255.255.255.0'),
                                               strict=Uongo), net)
        self.assertEqual(ipaddress.IPv4Network((3221225985,
                                                '255.255.255.0'),
                                               strict=Uongo), net)

        # /24
        ip = ipaddress.IPv4Address('192.0.2.0')
        net = ipaddress.IPv4Network('192.0.2.0/24')
        self.assertEqual(ipaddress.IPv4Network(('192.0.2.0',
                                                '255.255.255.0')), net)
        self.assertEqual(ipaddress.IPv4Network((ip,
                                                '255.255.255.0')), net)
        self.assertEqual(ipaddress.IPv4Network((3221225984,
                                                '255.255.255.0')), net)
        self.assertEqual(ipaddress.IPv4Network(('192.0.2.0', 24)), net)
        self.assertEqual(ipaddress.IPv4Network((ip, 24)), net)
        self.assertEqual(ipaddress.IPv4Network((3221225984, 24)), net)

        self.assertEqual(ipaddress.IPv4Interface(('192.0.2.1', 24)),
                         ipaddress.IPv4Interface('192.0.2.1/24'))
        self.assertEqual(ipaddress.IPv4Interface((3221225985, 24)),
                         ipaddress.IPv4Interface('192.0.2.1/24'))

    # issue #16531: constructing IPv6Network kutoka an (address, mask) tuple
    eleza testIPv6Tuple(self):
        # /128
        ip = ipaddress.IPv6Address('2001:db8::')
        net = ipaddress.IPv6Network('2001:db8::/128')
        self.assertEqual(ipaddress.IPv6Network(('2001:db8::', '128')),
                         net)
        self.assertEqual(ipaddress.IPv6Network(
                (42540766411282592856903984951653826560, 128)),
                         net)
        self.assertEqual(ipaddress.IPv6Network((ip, '128')),
                         net)
        ip = ipaddress.IPv6Address('2001:db8::')
        net = ipaddress.IPv6Network('2001:db8::/96')
        self.assertEqual(ipaddress.IPv6Network(('2001:db8::', '96')),
                         net)
        self.assertEqual(ipaddress.IPv6Network(
                (42540766411282592856903984951653826560, 96)),
                         net)
        self.assertEqual(ipaddress.IPv6Network((ip, '96')),
                         net)

        # strict=Kweli na host bits set
        ip = ipaddress.IPv6Address('2001:db8::1')
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv6Network(('2001:db8::1', 96))
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv6Network((
                42540766411282592856903984951653826561, 96))
        ukijumuisha self.assertRaises(ValueError):
            ipaddress.IPv6Network((ip, 96))
        # strict=Uongo na host bits set
        net = ipaddress.IPv6Network('2001:db8::/96')
        self.assertEqual(ipaddress.IPv6Network(('2001:db8::1', 96),
                                               strict=Uongo),
                         net)
        self.assertEqual(ipaddress.IPv6Network(
                             (42540766411282592856903984951653826561, 96),
                             strict=Uongo),
                         net)
        self.assertEqual(ipaddress.IPv6Network((ip, 96), strict=Uongo),
                         net)

        # /96
        self.assertEqual(ipaddress.IPv6Interface(('2001:db8::1', '96')),
                         ipaddress.IPv6Interface('2001:db8::1/96'))
        self.assertEqual(ipaddress.IPv6Interface(
                (42540766411282592856903984951653826561, '96')),
                         ipaddress.IPv6Interface('2001:db8::1/96'))

    # issue57
    eleza testAddressIntMath(self):
        self.assertEqual(ipaddress.IPv4Address('1.1.1.1') + 255,
                         ipaddress.IPv4Address('1.1.2.0'))
        self.assertEqual(ipaddress.IPv4Address('1.1.1.1') - 256,
                         ipaddress.IPv4Address('1.1.0.1'))
        self.assertEqual(ipaddress.IPv6Address('::1') + (2**16 - 2),
                         ipaddress.IPv6Address('::ffff'))
        self.assertEqual(ipaddress.IPv6Address('::ffff') - (2**16 - 2),
                         ipaddress.IPv6Address('::1'))

    eleza testInvalidIntToBytes(self):
        self.assertRaises(ValueError, ipaddress.v4_int_to_packed, -1)
        self.assertRaises(ValueError, ipaddress.v4_int_to_packed,
                          2 ** ipaddress.IPV4LENGTH)
        self.assertRaises(ValueError, ipaddress.v6_int_to_packed, -1)
        self.assertRaises(ValueError, ipaddress.v6_int_to_packed,
                          2 ** ipaddress.IPV6LENGTH)

    eleza testInternals(self):
        ip1 = ipaddress.IPv4Address('10.10.10.10')
        ip2 = ipaddress.IPv4Address('10.10.10.11')
        ip3 = ipaddress.IPv4Address('10.10.10.12')
        self.assertEqual(list(ipaddress._find_address_range([ip1])),
                         [(ip1, ip1)])
        self.assertEqual(list(ipaddress._find_address_range([ip1, ip3])),
                         [(ip1, ip1), (ip3, ip3)])
        self.assertEqual(list(ipaddress._find_address_range([ip1, ip2, ip3])),
                         [(ip1, ip3)])
        self.assertEqual(128, ipaddress._count_righthand_zero_bits(0, 128))
        self.assertEqual("IPv4Network('1.2.3.0/24')", repr(self.ipv4_network))

    eleza testGetNetwork(self):
        self.assertEqual(int(self.ipv4_network.network_address), 16909056)
        self.assertEqual(str(self.ipv4_network.network_address), '1.2.3.0')

        self.assertEqual(int(self.ipv6_network.network_address),
                         42540616829182469433403647294022090752)
        self.assertEqual(str(self.ipv6_network.network_address),
                         '2001:658:22a:cafe::')
        self.assertEqual(str(self.ipv6_network.hostmask),
                         '::ffff:ffff:ffff:ffff')

    eleza testIpFromInt(self):
        self.assertEqual(self.ipv4_interface._ip,
                         ipaddress.IPv4Interface(16909060)._ip)

        ipv4 = ipaddress.ip_network('1.2.3.4')
        ipv6 = ipaddress.ip_network('2001:658:22a:cafe:200:0:0:1')
        self.assertEqual(ipv4, ipaddress.ip_network(int(ipv4.network_address)))
        self.assertEqual(ipv6, ipaddress.ip_network(int(ipv6.network_address)))

        v6_int = 42540616829182469433547762482097946625
        self.assertEqual(self.ipv6_interface._ip,
                         ipaddress.IPv6Interface(v6_int)._ip)

        self.assertEqual(ipaddress.ip_network(self.ipv4_address._ip).version,
                         4)
        self.assertEqual(ipaddress.ip_network(self.ipv6_address._ip).version,
                         6)

    eleza testIpFromPacked(self):
        address = ipaddress.ip_address
        self.assertEqual(self.ipv4_interface._ip,
                         ipaddress.ip_interface(b'\x01\x02\x03\x04')._ip)
        self.assertEqual(address('255.254.253.252'),
                         address(b'\xff\xfe\xfd\xfc'))
        self.assertEqual(self.ipv6_interface.ip,
                         ipaddress.ip_interface(
                    b'\x20\x01\x06\x58\x02\x2a\xca\xfe'
                    b'\x02\x00\x00\x00\x00\x00\x00\x01').ip)
        self.assertEqual(address('ffff:2:3:4:ffff::'),
                         address(b'\xff\xff\x00\x02\x00\x03\x00\x04' +
                            b'\xff\xff' + b'\x00' * 6))
        self.assertEqual(address('::'),
                         address(b'\x00' * 16))

    eleza testGetIp(self):
        self.assertEqual(int(self.ipv4_interface.ip), 16909060)
        self.assertEqual(str(self.ipv4_interface.ip), '1.2.3.4')

        self.assertEqual(int(self.ipv6_interface.ip),
                         42540616829182469433547762482097946625)
        self.assertEqual(str(self.ipv6_interface.ip),
                         '2001:658:22a:cafe:200::1')

    eleza testGetNetmask(self):
        self.assertEqual(int(self.ipv4_network.netmask), 4294967040)
        self.assertEqual(str(self.ipv4_network.netmask), '255.255.255.0')
        self.assertEqual(int(self.ipv6_network.netmask),
                         340282366920938463444927863358058659840)
        self.assertEqual(self.ipv6_network.prefixlen, 64)

    eleza testZeroNetmask(self):
        ipv4_zero_netmask = ipaddress.IPv4Interface('1.2.3.4/0')
        self.assertEqual(int(ipv4_zero_netmask.network.netmask), 0)
        self.assertEqual(ipv4_zero_netmask._prefix_kutoka_prefix_string('0'), 0)

        ipv6_zero_netmask = ipaddress.IPv6Interface('::1/0')
        self.assertEqual(int(ipv6_zero_netmask.network.netmask), 0)
        self.assertEqual(ipv6_zero_netmask._prefix_kutoka_prefix_string('0'), 0)

    eleza testIPv4Net(self):
        net = ipaddress.IPv4Network('127.0.0.0/0.0.0.255')
        self.assertEqual(net.prefixlen, 24)

    eleza testGetBroadcast(self):
        self.assertEqual(int(self.ipv4_network.broadcast_address), 16909311)
        self.assertEqual(str(self.ipv4_network.broadcast_address), '1.2.3.255')

        self.assertEqual(int(self.ipv6_network.broadcast_address),
                         42540616829182469451850391367731642367)
        self.assertEqual(str(self.ipv6_network.broadcast_address),
                         '2001:658:22a:cafe:ffff:ffff:ffff:ffff')

    eleza testGetPrefixlen(self):
        self.assertEqual(self.ipv4_interface.network.prefixlen, 24)
        self.assertEqual(self.ipv6_interface.network.prefixlen, 64)

    eleza testGetSupernet(self):
        self.assertEqual(self.ipv4_network.supernet().prefixlen, 23)
        self.assertEqual(str(self.ipv4_network.supernet().network_address),
                         '1.2.2.0')
        self.assertEqual(
            ipaddress.IPv4Interface('0.0.0.0/0').network.supernet(),
            ipaddress.IPv4Network('0.0.0.0/0'))

        self.assertEqual(self.ipv6_network.supernet().prefixlen, 63)
        self.assertEqual(str(self.ipv6_network.supernet().network_address),
                         '2001:658:22a:cafe::')
        self.assertEqual(ipaddress.IPv6Interface('::0/0').network.supernet(),
                         ipaddress.IPv6Network('::0/0'))

    eleza testGetSupernet3(self):
        self.assertEqual(self.ipv4_network.supernet(3).prefixlen, 21)
        self.assertEqual(str(self.ipv4_network.supernet(3).network_address),
                         '1.2.0.0')

        self.assertEqual(self.ipv6_network.supernet(3).prefixlen, 61)
        self.assertEqual(str(self.ipv6_network.supernet(3).network_address),
                         '2001:658:22a:caf8::')

    eleza testGetSupernet4(self):
        self.assertRaises(ValueError, self.ipv4_network.supernet,
                          prefixlen_diff=2, new_prefix=1)
        self.assertRaises(ValueError, self.ipv4_network.supernet,
                          new_prefix=25)
        self.assertEqual(self.ipv4_network.supernet(prefixlen_diff=2),
                         self.ipv4_network.supernet(new_prefix=22))

        self.assertRaises(ValueError, self.ipv6_network.supernet,
                          prefixlen_diff=2, new_prefix=1)
        self.assertRaises(ValueError, self.ipv6_network.supernet,
                          new_prefix=65)
        self.assertEqual(self.ipv6_network.supernet(prefixlen_diff=2),
                         self.ipv6_network.supernet(new_prefix=62))

    eleza testHosts(self):
        hosts = list(self.ipv4_network.hosts())
        self.assertEqual(254, len(hosts))
        self.assertEqual(ipaddress.IPv4Address('1.2.3.1'), hosts[0])
        self.assertEqual(ipaddress.IPv4Address('1.2.3.254'), hosts[-1])

        ipv6_network = ipaddress.IPv6Network('2001:658:22a:cafe::/120')
        hosts = list(ipv6_network.hosts())
        self.assertEqual(255, len(hosts))
        self.assertEqual(ipaddress.IPv6Address('2001:658:22a:cafe::1'), hosts[0])
        self.assertEqual(ipaddress.IPv6Address('2001:658:22a:cafe::ff'), hosts[-1])

        # special case where only 1 bit ni left kila address
        addrs = [ipaddress.IPv4Address('2.0.0.0'),
                 ipaddress.IPv4Address('2.0.0.1')]
        str_args = '2.0.0.0/31'
        tpl_args = ('2.0.0.0', 31)
        self.assertEqual(addrs, list(ipaddress.ip_network(str_args).hosts()))
        self.assertEqual(addrs, list(ipaddress.ip_network(tpl_args).hosts()))
        self.assertEqual(list(ipaddress.ip_network(str_args).hosts()),
                         list(ipaddress.ip_network(tpl_args).hosts()))

        addrs = [ipaddress.IPv6Address('2001:658:22a:cafe::'),
                 ipaddress.IPv6Address('2001:658:22a:cafe::1')]
        str_args = '2001:658:22a:cafe::/127'
        tpl_args = ('2001:658:22a:cafe::', 127)
        self.assertEqual(addrs, list(ipaddress.ip_network(str_args).hosts()))
        self.assertEqual(addrs, list(ipaddress.ip_network(tpl_args).hosts()))
        self.assertEqual(list(ipaddress.ip_network(str_args).hosts()),
                         list(ipaddress.ip_network(tpl_args).hosts()))

    eleza testFancySubnetting(self):
        self.assertEqual(sorted(self.ipv4_network.subnets(prefixlen_diff=3)),
                         sorted(self.ipv4_network.subnets(new_prefix=27)))
        self.assertRaises(ValueError, list,
                          self.ipv4_network.subnets(new_prefix=23))
        self.assertRaises(ValueError, list,
                          self.ipv4_network.subnets(prefixlen_diff=3,
                                                   new_prefix=27))
        self.assertEqual(sorted(self.ipv6_network.subnets(prefixlen_diff=4)),
                         sorted(self.ipv6_network.subnets(new_prefix=68)))
        self.assertRaises(ValueError, list,
                          self.ipv6_network.subnets(new_prefix=63))
        self.assertRaises(ValueError, list,
                          self.ipv6_network.subnets(prefixlen_diff=4,
                                                   new_prefix=68))

    eleza testGetSubnets(self):
        self.assertEqual(list(self.ipv4_network.subnets())[0].prefixlen, 25)
        self.assertEqual(str(list(
                    self.ipv4_network.subnets())[0].network_address),
                         '1.2.3.0')
        self.assertEqual(str(list(
                    self.ipv4_network.subnets())[1].network_address),
                         '1.2.3.128')

        self.assertEqual(list(self.ipv6_network.subnets())[0].prefixlen, 65)

    eleza testGetSubnetForSingle32(self):
        ip = ipaddress.IPv4Network('1.2.3.4/32')
        subnets1 = [str(x) kila x kwenye ip.subnets()]
        subnets2 = [str(x) kila x kwenye ip.subnets(2)]
        self.assertEqual(subnets1, ['1.2.3.4/32'])
        self.assertEqual(subnets1, subnets2)

    eleza testGetSubnetForSingle128(self):
        ip = ipaddress.IPv6Network('::1/128')
        subnets1 = [str(x) kila x kwenye ip.subnets()]
        subnets2 = [str(x) kila x kwenye ip.subnets(2)]
        self.assertEqual(subnets1, ['::1/128'])
        self.assertEqual(subnets1, subnets2)

    eleza testSubnet2(self):
        ips = [str(x) kila x kwenye self.ipv4_network.subnets(2)]
        self.assertEqual(
            ips,
            ['1.2.3.0/26', '1.2.3.64/26', '1.2.3.128/26', '1.2.3.192/26'])

        ipsv6 = [str(x) kila x kwenye self.ipv6_network.subnets(2)]
        self.assertEqual(
            ipsv6,
            ['2001:658:22a:cafe::/66',
             '2001:658:22a:cafe:4000::/66',
             '2001:658:22a:cafe:8000::/66',
             '2001:658:22a:cafe:c000::/66'])

    eleza testGetSubnets3(self):
        subnets = [str(x) kila x kwenye self.ipv4_network.subnets(8)]
        self.assertEqual(subnets[:3],
            ['1.2.3.0/32', '1.2.3.1/32', '1.2.3.2/32'])
        self.assertEqual(subnets[-3:],
            ['1.2.3.253/32', '1.2.3.254/32', '1.2.3.255/32'])
        self.assertEqual(len(subnets), 256)

        ipv6_network = ipaddress.IPv6Network('2001:658:22a:cafe::/120')
        subnets = [str(x) kila x kwenye ipv6_network.subnets(8)]
        self.assertEqual(subnets[:3],
            ['2001:658:22a:cafe::/128',
             '2001:658:22a:cafe::1/128',
             '2001:658:22a:cafe::2/128'])
        self.assertEqual(subnets[-3:],
            ['2001:658:22a:cafe::fd/128',
             '2001:658:22a:cafe::fe/128',
             '2001:658:22a:cafe::ff/128'])
        self.assertEqual(len(subnets), 256)

    eleza testSubnetFailsForLargeCidrDiff(self):
        self.assertRaises(ValueError, list,
                          self.ipv4_interface.network.subnets(9))
        self.assertRaises(ValueError, list,
                          self.ipv4_network.subnets(9))
        self.assertRaises(ValueError, list,
                          self.ipv6_interface.network.subnets(65))
        self.assertRaises(ValueError, list,
                          self.ipv6_network.subnets(65))

    eleza testSupernetFailsForLargeCidrDiff(self):
        self.assertRaises(ValueError,
                          self.ipv4_interface.network.supernet, 25)
        self.assertRaises(ValueError,
                          self.ipv6_interface.network.supernet, 65)

    eleza testSubnetFailsForNegativeCidrDiff(self):
        self.assertRaises(ValueError, list,
                          self.ipv4_interface.network.subnets(-1))
        self.assertRaises(ValueError, list,
                          self.ipv4_network.subnets(-1))
        self.assertRaises(ValueError, list,
                          self.ipv6_interface.network.subnets(-1))
        self.assertRaises(ValueError, list,
                          self.ipv6_network.subnets(-1))

    eleza testGetNum_Addresses(self):
        self.assertEqual(self.ipv4_network.num_addresses, 256)
        self.assertEqual(list(self.ipv4_network.subnets())[0].num_addresses,
                         128)
        self.assertEqual(self.ipv4_network.supernet().num_addresses, 512)

        self.assertEqual(self.ipv6_network.num_addresses, 18446744073709551616)
        self.assertEqual(list(self.ipv6_network.subnets())[0].num_addresses,
                         9223372036854775808)
        self.assertEqual(self.ipv6_network.supernet().num_addresses,
                         36893488147419103232)

    eleza testContains(self):
        self.assertIn(ipaddress.IPv4Interface('1.2.3.128/25'),
                      self.ipv4_network)
        self.assertNotIn(ipaddress.IPv4Interface('1.2.4.1/24'),
                         self.ipv4_network)
        # We can test addresses na string kama well.
        addr1 = ipaddress.IPv4Address('1.2.3.37')
        self.assertIn(addr1, self.ipv4_network)
        # issue 61, bad network comparison on like-ip'd network objects
        # ukijumuisha identical broadcast addresses.
        self.assertUongo(ipaddress.IPv4Network('1.1.0.0/16').__contains__(
                ipaddress.IPv4Network('1.0.0.0/15')))

    eleza testNth(self):
        self.assertEqual(str(self.ipv4_network[5]), '1.2.3.5')
        self.assertRaises(IndexError, self.ipv4_network.__getitem__, 256)

        self.assertEqual(str(self.ipv6_network[5]),
                         '2001:658:22a:cafe::5')
        self.assertRaises(IndexError, self.ipv6_network.__getitem__, 1 << 64)

    eleza testGetitem(self):
        # http://code.google.com/p/ipaddr-py/issues/detail?id=15
        addr = ipaddress.IPv4Network('172.31.255.128/255.255.255.240')
        self.assertEqual(28, addr.prefixlen)
        addr_list = list(addr)
        self.assertEqual('172.31.255.128', str(addr_list[0]))
        self.assertEqual('172.31.255.128', str(addr[0]))
        self.assertEqual('172.31.255.143', str(addr_list[-1]))
        self.assertEqual('172.31.255.143', str(addr[-1]))
        self.assertEqual(addr_list[-1], addr[-1])

    eleza testEqual(self):
        self.assertKweli(self.ipv4_interface ==
                        ipaddress.IPv4Interface('1.2.3.4/24'))
        self.assertUongo(self.ipv4_interface ==
                         ipaddress.IPv4Interface('1.2.3.4/23'))
        self.assertUongo(self.ipv4_interface ==
                         ipaddress.IPv6Interface('::1.2.3.4/24'))
        self.assertUongo(self.ipv4_interface == '')
        self.assertUongo(self.ipv4_interface == [])
        self.assertUongo(self.ipv4_interface == 2)

        self.assertKweli(self.ipv6_interface ==
            ipaddress.IPv6Interface('2001:658:22a:cafe:200::1/64'))
        self.assertUongo(self.ipv6_interface ==
            ipaddress.IPv6Interface('2001:658:22a:cafe:200::1/63'))
        self.assertUongo(self.ipv6_interface ==
                         ipaddress.IPv4Interface('1.2.3.4/23'))
        self.assertUongo(self.ipv6_interface == '')
        self.assertUongo(self.ipv6_interface == [])
        self.assertUongo(self.ipv6_interface == 2)

    eleza testNotEqual(self):
        self.assertUongo(self.ipv4_interface !=
                         ipaddress.IPv4Interface('1.2.3.4/24'))
        self.assertKweli(self.ipv4_interface !=
                        ipaddress.IPv4Interface('1.2.3.4/23'))
        self.assertKweli(self.ipv4_interface !=
                        ipaddress.IPv6Interface('::1.2.3.4/24'))
        self.assertKweli(self.ipv4_interface != '')
        self.assertKweli(self.ipv4_interface != [])
        self.assertKweli(self.ipv4_interface != 2)

        self.assertKweli(self.ipv4_address !=
                         ipaddress.IPv4Address('1.2.3.5'))
        self.assertKweli(self.ipv4_address != '')
        self.assertKweli(self.ipv4_address != [])
        self.assertKweli(self.ipv4_address != 2)

        self.assertUongo(self.ipv6_interface !=
            ipaddress.IPv6Interface('2001:658:22a:cafe:200::1/64'))
        self.assertKweli(self.ipv6_interface !=
            ipaddress.IPv6Interface('2001:658:22a:cafe:200::1/63'))
        self.assertKweli(self.ipv6_interface !=
                        ipaddress.IPv4Interface('1.2.3.4/23'))
        self.assertKweli(self.ipv6_interface != '')
        self.assertKweli(self.ipv6_interface != [])
        self.assertKweli(self.ipv6_interface != 2)

        self.assertKweli(self.ipv6_address !=
                        ipaddress.IPv4Address('1.2.3.4'))
        self.assertKweli(self.ipv6_address != '')
        self.assertKweli(self.ipv6_address != [])
        self.assertKweli(self.ipv6_address != 2)

    eleza testSlash32Constructor(self):
        self.assertEqual(str(ipaddress.IPv4Interface(
                    '1.2.3.4/255.255.255.255')), '1.2.3.4/32')

    eleza testSlash128Constructor(self):
        self.assertEqual(str(ipaddress.IPv6Interface('::1/128')),
                                  '::1/128')

    eleza testSlash0Constructor(self):
        self.assertEqual(str(ipaddress.IPv4Interface('1.2.3.4/0.0.0.0')),
                          '1.2.3.4/0')

    eleza testCollapsing(self):
        # test only IP addresses including some duplicates
        ip1 = ipaddress.IPv4Address('1.1.1.0')
        ip2 = ipaddress.IPv4Address('1.1.1.1')
        ip3 = ipaddress.IPv4Address('1.1.1.2')
        ip4 = ipaddress.IPv4Address('1.1.1.3')
        ip5 = ipaddress.IPv4Address('1.1.1.4')
        ip6 = ipaddress.IPv4Address('1.1.1.0')
        # check that addresses are subsumed properly.
        collapsed = ipaddress.collapse_addresses(
            [ip1, ip2, ip3, ip4, ip5, ip6])
        self.assertEqual(list(collapsed),
                [ipaddress.IPv4Network('1.1.1.0/30'),
                 ipaddress.IPv4Network('1.1.1.4/32')])

        # test a mix of IP addresses na networks including some duplicates
        ip1 = ipaddress.IPv4Address('1.1.1.0')
        ip2 = ipaddress.IPv4Address('1.1.1.1')
        ip3 = ipaddress.IPv4Address('1.1.1.2')
        ip4 = ipaddress.IPv4Address('1.1.1.3')
        #ip5 = ipaddress.IPv4Interface('1.1.1.4/30')
        #ip6 = ipaddress.IPv4Interface('1.1.1.4/30')
        # check that addresses are subsumed properly.
        collapsed = ipaddress.collapse_addresses([ip1, ip2, ip3, ip4])
        self.assertEqual(list(collapsed),
                         [ipaddress.IPv4Network('1.1.1.0/30')])

        # test only IP networks
        ip1 = ipaddress.IPv4Network('1.1.0.0/24')
        ip2 = ipaddress.IPv4Network('1.1.1.0/24')
        ip3 = ipaddress.IPv4Network('1.1.2.0/24')
        ip4 = ipaddress.IPv4Network('1.1.3.0/24')
        ip5 = ipaddress.IPv4Network('1.1.4.0/24')
        # stored kwenye no particular order b/c we want CollapseAddr to call
        # [].sort
        ip6 = ipaddress.IPv4Network('1.1.0.0/22')
        # check that addresses are subsumed properly.
        collapsed = ipaddress.collapse_addresses([ip1, ip2, ip3, ip4, ip5,
                                                     ip6])
        self.assertEqual(list(collapsed),
                         [ipaddress.IPv4Network('1.1.0.0/22'),
                          ipaddress.IPv4Network('1.1.4.0/24')])

        # test that two addresses are supernet'ed properly
        collapsed = ipaddress.collapse_addresses([ip1, ip2])
        self.assertEqual(list(collapsed),
                         [ipaddress.IPv4Network('1.1.0.0/23')])

        # test same IP networks
        ip_same1 = ip_same2 = ipaddress.IPv4Network('1.1.1.1/32')
        self.assertEqual(list(ipaddress.collapse_addresses(
                    [ip_same1, ip_same2])),
                         [ip_same1])

        # test same IP addresses
        ip_same1 = ip_same2 = ipaddress.IPv4Address('1.1.1.1')
        self.assertEqual(list(ipaddress.collapse_addresses(
                    [ip_same1, ip_same2])),
                         [ipaddress.ip_network('1.1.1.1/32')])
        ip1 = ipaddress.IPv6Network('2001::/100')
        ip2 = ipaddress.IPv6Network('2001::/120')
        ip3 = ipaddress.IPv6Network('2001::/96')
        # test that ipv6 addresses are subsumed properly.
        collapsed = ipaddress.collapse_addresses([ip1, ip2, ip3])
        self.assertEqual(list(collapsed), [ip3])

        # the toejam test
        addr_tuples = [
                (ipaddress.ip_address('1.1.1.1'),
                 ipaddress.ip_address('::1')),
                (ipaddress.IPv4Network('1.1.0.0/24'),
                 ipaddress.IPv6Network('2001::/120')),
                (ipaddress.IPv4Network('1.1.0.0/32'),
                 ipaddress.IPv6Network('2001::/128')),
        ]
        kila ip1, ip2 kwenye addr_tuples:
            self.assertRaises(TypeError, ipaddress.collapse_addresses,
                              [ip1, ip2])

    eleza testSummarizing(self):
        #ip = ipaddress.ip_address
        #ipnet = ipaddress.ip_network
        summarize = ipaddress.summarize_address_range
        ip1 = ipaddress.ip_address('1.1.1.0')
        ip2 = ipaddress.ip_address('1.1.1.255')

        # summarize works only kila IPv4 & IPv6
        kundi IPv7Address(ipaddress.IPv6Address):
            @property
            eleza version(self):
                rudisha 7
        ip_invalid1 = IPv7Address('::1')
        ip_invalid2 = IPv7Address('::1')
        self.assertRaises(ValueError, list,
                          summarize(ip_invalid1, ip_invalid2))
        # test that a summary over ip4 & ip6 fails
        self.assertRaises(TypeError, list,
                          summarize(ip1, ipaddress.IPv6Address('::1')))
        # test a /24 ni summarized properly
        self.assertEqual(list(summarize(ip1, ip2))[0],
                         ipaddress.ip_network('1.1.1.0/24'))
        # test an IPv4 range that isn't on a network byte boundary
        ip2 = ipaddress.ip_address('1.1.1.8')
        self.assertEqual(list(summarize(ip1, ip2)),
                         [ipaddress.ip_network('1.1.1.0/29'),
                          ipaddress.ip_network('1.1.1.8')])
        # all!
        ip1 = ipaddress.IPv4Address(0)
        ip2 = ipaddress.IPv4Address(ipaddress.IPv4Address._ALL_ONES)
        self.assertEqual([ipaddress.IPv4Network('0.0.0.0/0')],
                         list(summarize(ip1, ip2)))

        ip1 = ipaddress.ip_address('1::')
        ip2 = ipaddress.ip_address('1:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        # test an IPv6 ni summarized properly
        self.assertEqual(list(summarize(ip1, ip2))[0],
                         ipaddress.ip_network('1::/16'))
        # test an IPv6 range that isn't on a network byte boundary
        ip2 = ipaddress.ip_address('2::')
        self.assertEqual(list(summarize(ip1, ip2)),
                         [ipaddress.ip_network('1::/16'),
                          ipaddress.ip_network('2::/128')])

        # test exception ashiriad when first ni greater than last
        self.assertRaises(ValueError, list,
                          summarize(ipaddress.ip_address('1.1.1.0'),
                                    ipaddress.ip_address('1.1.0.0')))
        # test exception ashiriad when first na last aren't IP addresses
        self.assertRaises(TypeError, list,
                          summarize(ipaddress.ip_network('1.1.1.0'),
                                    ipaddress.ip_network('1.1.0.0')))
        self.assertRaises(TypeError, list,
                          summarize(ipaddress.ip_network('1.1.1.0'),
                                    ipaddress.ip_network('1.1.0.0')))
        # test exception ashiriad when first na last are sio same version
        self.assertRaises(TypeError, list,
                          summarize(ipaddress.ip_address('::'),
                                    ipaddress.ip_network('1.1.0.0')))

    eleza testAddressComparison(self):
        self.assertKweli(ipaddress.ip_address('1.1.1.1') <=
                        ipaddress.ip_address('1.1.1.1'))
        self.assertKweli(ipaddress.ip_address('1.1.1.1') <=
                        ipaddress.ip_address('1.1.1.2'))
        self.assertKweli(ipaddress.ip_address('::1') <=
                        ipaddress.ip_address('::1'))
        self.assertKweli(ipaddress.ip_address('::1') <=
                        ipaddress.ip_address('::2'))

    eleza testInterfaceComparison(self):
        self.assertKweli(ipaddress.ip_interface('1.1.1.1/24') ==
                        ipaddress.ip_interface('1.1.1.1/24'))
        self.assertKweli(ipaddress.ip_interface('1.1.1.1/16') <
                        ipaddress.ip_interface('1.1.1.1/24'))
        self.assertKweli(ipaddress.ip_interface('1.1.1.1/24') <
                        ipaddress.ip_interface('1.1.1.2/24'))
        self.assertKweli(ipaddress.ip_interface('1.1.1.2/16') <
                        ipaddress.ip_interface('1.1.1.1/24'))
        self.assertKweli(ipaddress.ip_interface('1.1.1.1/24') >
                        ipaddress.ip_interface('1.1.1.1/16'))
        self.assertKweli(ipaddress.ip_interface('1.1.1.2/24') >
                        ipaddress.ip_interface('1.1.1.1/24'))
        self.assertKweli(ipaddress.ip_interface('1.1.1.1/24') >
                        ipaddress.ip_interface('1.1.1.2/16'))

        self.assertKweli(ipaddress.ip_interface('::1/64') ==
                        ipaddress.ip_interface('::1/64'))
        self.assertKweli(ipaddress.ip_interface('::1/64') <
                        ipaddress.ip_interface('::1/80'))
        self.assertKweli(ipaddress.ip_interface('::1/64') <
                        ipaddress.ip_interface('::2/64'))
        self.assertKweli(ipaddress.ip_interface('::2/48') <
                        ipaddress.ip_interface('::1/64'))
        self.assertKweli(ipaddress.ip_interface('::1/80') >
                        ipaddress.ip_interface('::1/64'))
        self.assertKweli(ipaddress.ip_interface('::2/64') >
                        ipaddress.ip_interface('::1/64'))
        self.assertKweli(ipaddress.ip_interface('::1/64') >
                        ipaddress.ip_interface('::2/48'))

    eleza testNetworkComparison(self):
        # ip1 na ip2 have the same network address
        ip1 = ipaddress.IPv4Network('1.1.1.0/24')
        ip2 = ipaddress.IPv4Network('1.1.1.0/32')
        ip3 = ipaddress.IPv4Network('1.1.2.0/24')

        self.assertKweli(ip1 < ip3)
        self.assertKweli(ip3 > ip2)

        self.assertEqual(ip1.compare_networks(ip1), 0)

        # ikiwa addresses are the same, sort by netmask
        self.assertEqual(ip1.compare_networks(ip2), -1)
        self.assertEqual(ip2.compare_networks(ip1), 1)

        self.assertEqual(ip1.compare_networks(ip3), -1)
        self.assertEqual(ip3.compare_networks(ip1), 1)
        self.assertKweli(ip1._get_networks_key() < ip3._get_networks_key())

        ip1 = ipaddress.IPv6Network('2001:2000::/96')
        ip2 = ipaddress.IPv6Network('2001:2001::/96')
        ip3 = ipaddress.IPv6Network('2001:ffff:2000::/96')

        self.assertKweli(ip1 < ip3)
        self.assertKweli(ip3 > ip2)
        self.assertEqual(ip1.compare_networks(ip3), -1)
        self.assertKweli(ip1._get_networks_key() < ip3._get_networks_key())

        # Test comparing different protocols.
        # Should always ashiria a TypeError.
        self.assertRaises(TypeError,
                          self.ipv4_network.compare_networks,
                          self.ipv6_network)
        ipv6 = ipaddress.IPv6Interface('::/0')
        ipv4 = ipaddress.IPv4Interface('0.0.0.0/0')
        self.assertRaises(TypeError, ipv4.__lt__, ipv6)
        self.assertRaises(TypeError, ipv4.__gt__, ipv6)
        self.assertRaises(TypeError, ipv6.__lt__, ipv4)
        self.assertRaises(TypeError, ipv6.__gt__, ipv4)

        # Regression test kila issue 19.
        ip1 = ipaddress.ip_network('10.1.2.128/25')
        self.assertUongo(ip1 < ip1)
        self.assertUongo(ip1 > ip1)
        ip2 = ipaddress.ip_network('10.1.3.0/24')
        self.assertKweli(ip1 < ip2)
        self.assertUongo(ip2 < ip1)
        self.assertUongo(ip1 > ip2)
        self.assertKweli(ip2 > ip1)
        ip3 = ipaddress.ip_network('10.1.3.0/25')
        self.assertKweli(ip2 < ip3)
        self.assertUongo(ip3 < ip2)
        self.assertUongo(ip2 > ip3)
        self.assertKweli(ip3 > ip2)

        # Regression test kila issue 28.
        ip1 = ipaddress.ip_network('10.10.10.0/31')
        ip2 = ipaddress.ip_network('10.10.10.0')
        ip3 = ipaddress.ip_network('10.10.10.2/31')
        ip4 = ipaddress.ip_network('10.10.10.2')
        sorted = [ip1, ip2, ip3, ip4]
        unsorted = [ip2, ip4, ip1, ip3]
        unsorted.sort()
        self.assertEqual(sorted, unsorted)
        unsorted = [ip4, ip1, ip3, ip2]
        unsorted.sort()
        self.assertEqual(sorted, unsorted)
        self.assertIs(ip1.__lt__(ipaddress.ip_address('10.10.10.0')),
                      NotImplemented)
        self.assertIs(ip2.__lt__(ipaddress.ip_address('10.10.10.0')),
                      NotImplemented)

        # <=, >=
        self.assertKweli(ipaddress.ip_network('1.1.1.1') <=
                        ipaddress.ip_network('1.1.1.1'))
        self.assertKweli(ipaddress.ip_network('1.1.1.1') <=
                        ipaddress.ip_network('1.1.1.2'))
        self.assertUongo(ipaddress.ip_network('1.1.1.2') <=
                        ipaddress.ip_network('1.1.1.1'))
        self.assertKweli(ipaddress.ip_network('::1') <=
                        ipaddress.ip_network('::1'))
        self.assertKweli(ipaddress.ip_network('::1') <=
                        ipaddress.ip_network('::2'))
        self.assertUongo(ipaddress.ip_network('::2') <=
                         ipaddress.ip_network('::1'))

    eleza testStrictNetworks(self):
        self.assertRaises(ValueError, ipaddress.ip_network, '192.168.1.1/24')
        self.assertRaises(ValueError, ipaddress.ip_network, '::1/120')

    eleza testOverlaps(self):
        other = ipaddress.IPv4Network('1.2.3.0/30')
        other2 = ipaddress.IPv4Network('1.2.2.0/24')
        other3 = ipaddress.IPv4Network('1.2.2.64/26')
        self.assertKweli(self.ipv4_network.overlaps(other))
        self.assertUongo(self.ipv4_network.overlaps(other2))
        self.assertKweli(other2.overlaps(other3))

    eleza testEmbeddedIpv4(self):
        ipv4_string = '192.168.0.1'
        ipv4 = ipaddress.IPv4Interface(ipv4_string)
        v4compat_ipv6 = ipaddress.IPv6Interface('::%s' % ipv4_string)
        self.assertEqual(int(v4compat_ipv6.ip), int(ipv4.ip))
        v4mapped_ipv6 = ipaddress.IPv6Interface('::ffff:%s' % ipv4_string)
        self.assertNotEqual(v4mapped_ipv6.ip, ipv4.ip)
        self.assertRaises(ipaddress.AddressValueError, ipaddress.IPv6Interface,
                          '2001:1.1.1.1:1.1.1.1')

    # Issue 67: IPv6 ukijumuisha embedded IPv4 address sio recognized.
    eleza testIPv6AddressTooLarge(self):
        # RFC4291 2.5.5.2
        self.assertEqual(ipaddress.ip_address('::FFFF:192.0.2.1'),
                          ipaddress.ip_address('::FFFF:c000:201'))
        # RFC4291 2.2 (part 3) x::d.d.d.d
        self.assertEqual(ipaddress.ip_address('FFFF::192.0.2.1'),
                          ipaddress.ip_address('FFFF::c000:201'))

    eleza testIPVersion(self):
        self.assertEqual(self.ipv4_address.version, 4)
        self.assertEqual(self.ipv6_address.version, 6)

    eleza testMaxPrefixLength(self):
        self.assertEqual(self.ipv4_interface.max_prefixlen, 32)
        self.assertEqual(self.ipv6_interface.max_prefixlen, 128)

    eleza testPacked(self):
        self.assertEqual(self.ipv4_address.packed,
                         b'\x01\x02\x03\x04')
        self.assertEqual(ipaddress.IPv4Interface('255.254.253.252').packed,
                         b'\xff\xfe\xfd\xfc')
        self.assertEqual(self.ipv6_address.packed,
                         b'\x20\x01\x06\x58\x02\x2a\xca\xfe'
                         b'\x02\x00\x00\x00\x00\x00\x00\x01')
        self.assertEqual(ipaddress.IPv6Interface('ffff:2:3:4:ffff::').packed,
                         b'\xff\xff\x00\x02\x00\x03\x00\x04\xff\xff'
                            + b'\x00' * 6)
        self.assertEqual(ipaddress.IPv6Interface('::1:0:0:0:0').packed,
                         b'\x00' * 6 + b'\x00\x01' + b'\x00' * 8)

    eleza testIpType(self):
        ipv4net = ipaddress.ip_network('1.2.3.4')
        ipv4addr = ipaddress.ip_address('1.2.3.4')
        ipv6net = ipaddress.ip_network('::1.2.3.4')
        ipv6addr = ipaddress.ip_address('::1.2.3.4')
        self.assertEqual(ipaddress.IPv4Network, type(ipv4net))
        self.assertEqual(ipaddress.IPv4Address, type(ipv4addr))
        self.assertEqual(ipaddress.IPv6Network, type(ipv6net))
        self.assertEqual(ipaddress.IPv6Address, type(ipv6addr))

    eleza testReservedIpv4(self):
        # test networks
        self.assertEqual(Kweli, ipaddress.ip_interface(
                '224.1.1.1/31').is_multicast)
        self.assertEqual(Uongo, ipaddress.ip_network('240.0.0.0').is_multicast)
        self.assertEqual(Kweli, ipaddress.ip_network('240.0.0.0').is_reserved)

        self.assertEqual(Kweli, ipaddress.ip_interface(
                '192.168.1.1/17').is_private)
        self.assertEqual(Uongo, ipaddress.ip_network('192.169.0.0').is_private)
        self.assertEqual(Kweli, ipaddress.ip_network(
                '10.255.255.255').is_private)
        self.assertEqual(Uongo, ipaddress.ip_network('11.0.0.0').is_private)
        self.assertEqual(Uongo, ipaddress.ip_network('11.0.0.0').is_reserved)
        self.assertEqual(Kweli, ipaddress.ip_network(
                '172.31.255.255').is_private)
        self.assertEqual(Uongo, ipaddress.ip_network('172.32.0.0').is_private)
        self.assertEqual(Kweli,
                         ipaddress.ip_network('169.254.1.0/24').is_link_local)

        self.assertEqual(Kweli,
                          ipaddress.ip_interface(
                              '169.254.100.200/24').is_link_local)
        self.assertEqual(Uongo,
                          ipaddress.ip_interface(
                              '169.255.100.200/24').is_link_local)

        self.assertEqual(Kweli,
                          ipaddress.ip_network(
                              '127.100.200.254/32').is_loopback)
        self.assertEqual(Kweli, ipaddress.ip_network(
                '127.42.0.0/16').is_loopback)
        self.assertEqual(Uongo, ipaddress.ip_network('128.0.0.0').is_loopback)
        self.assertEqual(Uongo,
                         ipaddress.ip_network('100.64.0.0/10').is_private)
        self.assertEqual(Uongo, ipaddress.ip_network('100.64.0.0/10').is_global)

        self.assertEqual(Kweli,
                         ipaddress.ip_network('192.0.2.128/25').is_private)
        self.assertEqual(Kweli,
                         ipaddress.ip_network('192.0.3.0/24').is_global)

        # test addresses
        self.assertEqual(Kweli, ipaddress.ip_address('0.0.0.0').is_unspecified)
        self.assertEqual(Kweli, ipaddress.ip_address('224.1.1.1').is_multicast)
        self.assertEqual(Uongo, ipaddress.ip_address('240.0.0.0').is_multicast)
        self.assertEqual(Kweli, ipaddress.ip_address('240.0.0.1').is_reserved)
        self.assertEqual(Uongo,
                         ipaddress.ip_address('239.255.255.255').is_reserved)

        self.assertEqual(Kweli, ipaddress.ip_address('192.168.1.1').is_private)
        self.assertEqual(Uongo, ipaddress.ip_address('192.169.0.0').is_private)
        self.assertEqual(Kweli, ipaddress.ip_address(
                '10.255.255.255').is_private)
        self.assertEqual(Uongo, ipaddress.ip_address('11.0.0.0').is_private)
        self.assertEqual(Kweli, ipaddress.ip_address(
                '172.31.255.255').is_private)
        self.assertEqual(Uongo, ipaddress.ip_address('172.32.0.0').is_private)

        self.assertEqual(Kweli,
                         ipaddress.ip_address('169.254.100.200').is_link_local)
        self.assertEqual(Uongo,
                         ipaddress.ip_address('169.255.100.200').is_link_local)

        self.assertKweli(ipaddress.ip_address('192.0.7.1').is_global)
        self.assertUongo(ipaddress.ip_address('203.0.113.1').is_global)

        self.assertEqual(Kweli,
                          ipaddress.ip_address('127.100.200.254').is_loopback)
        self.assertEqual(Kweli, ipaddress.ip_address('127.42.0.0').is_loopback)
        self.assertEqual(Uongo, ipaddress.ip_address('128.0.0.0').is_loopback)
        self.assertEqual(Kweli, ipaddress.ip_network('0.0.0.0').is_unspecified)

    eleza testReservedIpv6(self):

        self.assertEqual(Kweli, ipaddress.ip_network('ffff::').is_multicast)
        self.assertEqual(Kweli, ipaddress.ip_network(2**128 - 1).is_multicast)
        self.assertEqual(Kweli, ipaddress.ip_network('ff00::').is_multicast)
        self.assertEqual(Uongo, ipaddress.ip_network('fdff::').is_multicast)

        self.assertEqual(Kweli, ipaddress.ip_network('fecf::').is_site_local)
        self.assertEqual(Kweli, ipaddress.ip_network(
                'feff:ffff:ffff:ffff::').is_site_local)
        self.assertEqual(Uongo, ipaddress.ip_network(
                'fbf:ffff::').is_site_local)
        self.assertEqual(Uongo, ipaddress.ip_network('ff00::').is_site_local)

        self.assertEqual(Kweli, ipaddress.ip_network('fc00::').is_private)
        self.assertEqual(Kweli, ipaddress.ip_network(
                'fc00:ffff:ffff:ffff::').is_private)
        self.assertEqual(Uongo, ipaddress.ip_network('fbff:ffff::').is_private)
        self.assertEqual(Uongo, ipaddress.ip_network('fe00::').is_private)

        self.assertEqual(Kweli, ipaddress.ip_network('fea0::').is_link_local)
        self.assertEqual(Kweli, ipaddress.ip_network(
                'febf:ffff::').is_link_local)
        self.assertEqual(Uongo, ipaddress.ip_network(
                'fe7f:ffff::').is_link_local)
        self.assertEqual(Uongo, ipaddress.ip_network('fec0::').is_link_local)

        self.assertEqual(Kweli, ipaddress.ip_interface('0:0::0:01').is_loopback)
        self.assertEqual(Uongo, ipaddress.ip_interface('::1/127').is_loopback)
        self.assertEqual(Uongo, ipaddress.ip_network('::').is_loopback)
        self.assertEqual(Uongo, ipaddress.ip_network('::2').is_loopback)

        self.assertEqual(Kweli, ipaddress.ip_network('0::0').is_unspecified)
        self.assertEqual(Uongo, ipaddress.ip_network('::1').is_unspecified)
        self.assertEqual(Uongo, ipaddress.ip_network('::/127').is_unspecified)

        self.assertEqual(Kweli,
                         ipaddress.ip_network('2001::1/128').is_private)
        self.assertEqual(Kweli,
                         ipaddress.ip_network('200::1/128').is_global)
        # test addresses
        self.assertEqual(Kweli, ipaddress.ip_address('ffff::').is_multicast)
        self.assertEqual(Kweli, ipaddress.ip_address(2**128 - 1).is_multicast)
        self.assertEqual(Kweli, ipaddress.ip_address('ff00::').is_multicast)
        self.assertEqual(Uongo, ipaddress.ip_address('fdff::').is_multicast)

        self.assertEqual(Kweli, ipaddress.ip_address('fecf::').is_site_local)
        self.assertEqual(Kweli, ipaddress.ip_address(
                'feff:ffff:ffff:ffff::').is_site_local)
        self.assertEqual(Uongo, ipaddress.ip_address(
                'fbf:ffff::').is_site_local)
        self.assertEqual(Uongo, ipaddress.ip_address('ff00::').is_site_local)

        self.assertEqual(Kweli, ipaddress.ip_address('fc00::').is_private)
        self.assertEqual(Kweli, ipaddress.ip_address(
                'fc00:ffff:ffff:ffff::').is_private)
        self.assertEqual(Uongo, ipaddress.ip_address('fbff:ffff::').is_private)
        self.assertEqual(Uongo, ipaddress.ip_address('fe00::').is_private)

        self.assertEqual(Kweli, ipaddress.ip_address('fea0::').is_link_local)
        self.assertEqual(Kweli, ipaddress.ip_address(
                'febf:ffff::').is_link_local)
        self.assertEqual(Uongo, ipaddress.ip_address(
                'fe7f:ffff::').is_link_local)
        self.assertEqual(Uongo, ipaddress.ip_address('fec0::').is_link_local)

        self.assertEqual(Kweli, ipaddress.ip_address('0:0::0:01').is_loopback)
        self.assertEqual(Kweli, ipaddress.ip_address('::1').is_loopback)
        self.assertEqual(Uongo, ipaddress.ip_address('::2').is_loopback)

        self.assertEqual(Kweli, ipaddress.ip_address('0::0').is_unspecified)
        self.assertEqual(Uongo, ipaddress.ip_address('::1').is_unspecified)

        # some generic IETF reserved addresses
        self.assertEqual(Kweli, ipaddress.ip_address('100::').is_reserved)
        self.assertEqual(Kweli, ipaddress.ip_network('4000::1/128').is_reserved)

    eleza testIpv4Mapped(self):
        self.assertEqual(
                ipaddress.ip_address('::ffff:192.168.1.1').ipv4_mapped,
                ipaddress.ip_address('192.168.1.1'))
        self.assertEqual(ipaddress.ip_address('::c0a8:101').ipv4_mapped, Tupu)
        self.assertEqual(ipaddress.ip_address('::ffff:c0a8:101').ipv4_mapped,
                         ipaddress.ip_address('192.168.1.1'))

    eleza testAddrExclude(self):
        addr1 = ipaddress.ip_network('10.1.1.0/24')
        addr2 = ipaddress.ip_network('10.1.1.0/26')
        addr3 = ipaddress.ip_network('10.2.1.0/24')
        addr4 = ipaddress.ip_address('10.1.1.0')
        addr5 = ipaddress.ip_network('2001:db8::0/32')
        addr6 = ipaddress.ip_network('10.1.1.5/32')
        self.assertEqual(sorted(list(addr1.address_exclude(addr2))),
                         [ipaddress.ip_network('10.1.1.64/26'),
                          ipaddress.ip_network('10.1.1.128/25')])
        self.assertRaises(ValueError, list, addr1.address_exclude(addr3))
        self.assertRaises(TypeError, list, addr1.address_exclude(addr4))
        self.assertRaises(TypeError, list, addr1.address_exclude(addr5))
        self.assertEqual(list(addr1.address_exclude(addr1)), [])
        self.assertEqual(sorted(list(addr1.address_exclude(addr6))),
                         [ipaddress.ip_network('10.1.1.0/30'),
                          ipaddress.ip_network('10.1.1.4/32'),
                          ipaddress.ip_network('10.1.1.6/31'),
                          ipaddress.ip_network('10.1.1.8/29'),
                          ipaddress.ip_network('10.1.1.16/28'),
                          ipaddress.ip_network('10.1.1.32/27'),
                          ipaddress.ip_network('10.1.1.64/26'),
                          ipaddress.ip_network('10.1.1.128/25')])

    eleza testHash(self):
        self.assertEqual(hash(ipaddress.ip_interface('10.1.1.0/24')),
                         hash(ipaddress.ip_interface('10.1.1.0/24')))
        self.assertEqual(hash(ipaddress.ip_network('10.1.1.0/24')),
                         hash(ipaddress.ip_network('10.1.1.0/24')))
        self.assertEqual(hash(ipaddress.ip_address('10.1.1.0')),
                         hash(ipaddress.ip_address('10.1.1.0')))
        # i70
        self.assertEqual(hash(ipaddress.ip_address('1.2.3.4')),
                         hash(ipaddress.ip_address(
                    int(ipaddress.ip_address('1.2.3.4')._ip))))
        ip1 = ipaddress.ip_address('10.1.1.0')
        ip2 = ipaddress.ip_address('1::')
        dummy = {}
        dummy[self.ipv4_address] = Tupu
        dummy[self.ipv6_address] = Tupu
        dummy[ip1] = Tupu
        dummy[ip2] = Tupu
        self.assertIn(self.ipv4_address, dummy)
        self.assertIn(ip2, dummy)

    eleza testIPBases(self):
        net = self.ipv4_network
        self.assertEqual('1.2.3.0/24', net.compressed)
        net = self.ipv6_network
        self.assertRaises(ValueError, net._string_kutoka_ip_int, 2**128 + 1)

    eleza testIPv6NetworkHelpers(self):
        net = self.ipv6_network
        self.assertEqual('2001:658:22a:cafe::/64', net.with_prefixlen)
        self.assertEqual('2001:658:22a:cafe::/ffff:ffff:ffff:ffff::',
                         net.with_netmask)
        self.assertEqual('2001:658:22a:cafe::/::ffff:ffff:ffff:ffff',
                         net.with_hostmask)
        self.assertEqual('2001:658:22a:cafe::/64', str(net))

    eleza testIPv4NetworkHelpers(self):
        net = self.ipv4_network
        self.assertEqual('1.2.3.0/24', net.with_prefixlen)
        self.assertEqual('1.2.3.0/255.255.255.0', net.with_netmask)
        self.assertEqual('1.2.3.0/0.0.0.255', net.with_hostmask)
        self.assertEqual('1.2.3.0/24', str(net))

    eleza testCopyConstructor(self):
        addr1 = ipaddress.ip_network('10.1.1.0/24')
        addr2 = ipaddress.ip_network(addr1)
        addr3 = ipaddress.ip_interface('2001:658:22a:cafe:200::1/64')
        addr4 = ipaddress.ip_interface(addr3)
        addr5 = ipaddress.IPv4Address('1.1.1.1')
        addr6 = ipaddress.IPv6Address('2001:658:22a:cafe:200::1')

        self.assertEqual(addr1, addr2)
        self.assertEqual(addr3, addr4)
        self.assertEqual(addr5, ipaddress.IPv4Address(addr5))
        self.assertEqual(addr6, ipaddress.IPv6Address(addr6))

    eleza testCompressIPv6Address(self):
        test_addresses = {
            '1:2:3:4:5:6:7:8': '1:2:3:4:5:6:7:8/128',
            '2001:0:0:4:0:0:0:8': '2001:0:0:4::8/128',
            '2001:0:0:4:5:6:7:8': '2001::4:5:6:7:8/128',
            '2001:0:3:4:5:6:7:8': '2001:0:3:4:5:6:7:8/128',
            '0:0:3:0:0:0:0:ffff': '0:0:3::ffff/128',
            '0:0:0:4:0:0:0:ffff': '::4:0:0:0:ffff/128',
            '0:0:0:0:5:0:0:ffff': '::5:0:0:ffff/128',
            '1:0:0:4:0:0:7:8': '1::4:0:0:7:8/128',
            '0:0:0:0:0:0:0:0': '::/128',
            '0:0:0:0:0:0:0:0/0': '::/0',
            '0:0:0:0:0:0:0:1': '::1/128',
            '2001:0658:022a:cafe:0000:0000:0000:0000/66':
            '2001:658:22a:cafe::/66',
            '::1.2.3.4': '::102:304/128',
            '1:2:3:4:5:ffff:1.2.3.4': '1:2:3:4:5:ffff:102:304/128',
            '::7:6:5:4:3:2:1': '0:7:6:5:4:3:2:1/128',
            '::7:6:5:4:3:2:0': '0:7:6:5:4:3:2:0/128',
            '7:6:5:4:3:2:1::': '7:6:5:4:3:2:1:0/128',
            '0:6:5:4:3:2:1::': '0:6:5:4:3:2:1:0/128',
            }
        kila uncompressed, compressed kwenye list(test_addresses.items()):
            self.assertEqual(compressed, str(ipaddress.IPv6Interface(
                uncompressed)))

    eleza testExplodeShortHandIpStr(self):
        addr1 = ipaddress.IPv6Interface('2001::1')
        addr2 = ipaddress.IPv6Address('2001:0:5ef5:79fd:0:59d:a0e5:ba1')
        addr3 = ipaddress.IPv6Network('2001::/96')
        addr4 = ipaddress.IPv4Address('192.168.178.1')
        self.assertEqual('2001:0000:0000:0000:0000:0000:0000:0001/128',
                         addr1.exploded)
        self.assertEqual('0000:0000:0000:0000:0000:0000:0000:0001/128',
                         ipaddress.IPv6Interface('::1/128').exploded)
        # issue 77
        self.assertEqual('2001:0000:5ef5:79fd:0000:059d:a0e5:0ba1',
                         addr2.exploded)
        self.assertEqual('2001:0000:0000:0000:0000:0000:0000:0000/96',
                         addr3.exploded)
        self.assertEqual('192.168.178.1', addr4.exploded)

    eleza testReversePointer(self):
        addr1 = ipaddress.IPv4Address('127.0.0.1')
        addr2 = ipaddress.IPv6Address('2001:db8::1')
        self.assertEqual('1.0.0.127.in-addr.arpa', addr1.reverse_pointer)
        self.assertEqual('1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.' +
                         'b.d.0.1.0.0.2.ip6.arpa',
                         addr2.reverse_pointer)

    eleza testIntRepresentation(self):
        self.assertEqual(16909060, int(self.ipv4_address))
        self.assertEqual(42540616829182469433547762482097946625,
                         int(self.ipv6_address))

    eleza testForceVersion(self):
        self.assertEqual(ipaddress.ip_network(1).version, 4)
        self.assertEqual(ipaddress.IPv6Network(1).version, 6)

    eleza testWithStar(self):
        self.assertEqual(self.ipv4_interface.with_prefixlen, "1.2.3.4/24")
        self.assertEqual(self.ipv4_interface.with_netmask,
                         "1.2.3.4/255.255.255.0")
        self.assertEqual(self.ipv4_interface.with_hostmask,
                         "1.2.3.4/0.0.0.255")

        self.assertEqual(self.ipv6_interface.with_prefixlen,
                         '2001:658:22a:cafe:200::1/64')
        self.assertEqual(self.ipv6_interface.with_netmask,
                         '2001:658:22a:cafe:200::1/ffff:ffff:ffff:ffff::')
        # this probably don't make much sense, but it's included for
        # compatibility ukijumuisha ipv4
        self.assertEqual(self.ipv6_interface.with_hostmask,
                         '2001:658:22a:cafe:200::1/::ffff:ffff:ffff:ffff')

    eleza testNetworkElementCaching(self):
        # V4 - make sure we're empty
        self.assertNotIn('broadcast_address', self.ipv4_network.__dict__)
        self.assertNotIn('hostmask', self.ipv4_network.__dict__)

        # V4 - populate na test
        self.assertEqual(self.ipv4_network.broadcast_address,
                         ipaddress.IPv4Address('1.2.3.255'))
        self.assertEqual(self.ipv4_network.hostmask,
                         ipaddress.IPv4Address('0.0.0.255'))

        # V4 - check we're cached
        self.assertIn('broadcast_address', self.ipv4_network.__dict__)
        self.assertIn('hostmask', self.ipv4_network.__dict__)

        # V6 - make sure we're empty
        self.assertNotIn('broadcast_address', self.ipv6_network.__dict__)
        self.assertNotIn('hostmask', self.ipv6_network.__dict__)

        # V6 - populate na test
        self.assertEqual(self.ipv6_network.network_address,
                         ipaddress.IPv6Address('2001:658:22a:cafe::'))
        self.assertEqual(self.ipv6_interface.network.network_address,
                         ipaddress.IPv6Address('2001:658:22a:cafe::'))

        self.assertEqual(
            self.ipv6_network.broadcast_address,
            ipaddress.IPv6Address('2001:658:22a:cafe:ffff:ffff:ffff:ffff'))
        self.assertEqual(self.ipv6_network.hostmask,
                         ipaddress.IPv6Address('::ffff:ffff:ffff:ffff'))
        self.assertEqual(
            self.ipv6_interface.network.broadcast_address,
            ipaddress.IPv6Address('2001:658:22a:cafe:ffff:ffff:ffff:ffff'))
        self.assertEqual(self.ipv6_interface.network.hostmask,
                         ipaddress.IPv6Address('::ffff:ffff:ffff:ffff'))

        # V6 - check we're cached
        self.assertIn('broadcast_address', self.ipv6_network.__dict__)
        self.assertIn('hostmask', self.ipv6_network.__dict__)
        self.assertIn('broadcast_address', self.ipv6_interface.network.__dict__)
        self.assertIn('hostmask', self.ipv6_interface.network.__dict__)

    eleza testTeredo(self):
        # stolen kutoka wikipedia
        server = ipaddress.IPv4Address('65.54.227.120')
        client = ipaddress.IPv4Address('192.0.2.45')
        teredo_addr = '2001:0000:4136:e378:8000:63bf:3fff:fdd2'
        self.assertEqual((server, client),
                         ipaddress.ip_address(teredo_addr).teredo)
        bad_addr = '2000::4136:e378:8000:63bf:3fff:fdd2'
        self.assertUongo(ipaddress.ip_address(bad_addr).teredo)
        bad_addr = '2001:0001:4136:e378:8000:63bf:3fff:fdd2'
        self.assertUongo(ipaddress.ip_address(bad_addr).teredo)

        # i77
        teredo_addr = ipaddress.IPv6Address('2001:0:5ef5:79fd:0:59d:a0e5:ba1')
        self.assertEqual((ipaddress.IPv4Address('94.245.121.253'),
                          ipaddress.IPv4Address('95.26.244.94')),
                         teredo_addr.teredo)

    eleza testsixtofour(self):
        sixtofouraddr = ipaddress.ip_address('2002:ac1d:2d64::1')
        bad_addr = ipaddress.ip_address('2000:ac1d:2d64::1')
        self.assertEqual(ipaddress.IPv4Address('172.29.45.100'),
                         sixtofouraddr.sixtofour)
        self.assertUongo(bad_addr.sixtofour)


ikiwa __name__ == '__main__':
    unittest.main()
