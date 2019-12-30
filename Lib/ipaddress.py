# Copyright 2007 Google Inc.
#  Licensed to PSF under a Contributor Agreement.

"""A fast, lightweight IPv4/IPv6 manipulation library kwenye Python.

This library ni used to create/poke/manipulate IPv4 na IPv6 addresses
and networks.

"""

__version__ = '1.0'


agiza functools

IPV4LENGTH = 32
IPV6LENGTH = 128

kundi AddressValueError(ValueError):
    """A Value Error related to the address."""


kundi NetmaskValueError(ValueError):
    """A Value Error related to the netmask."""


eleza ip_address(address):
    """Take an IP string/int na rudisha an object of the correct type.

    Args:
        address: A string ama integer, the IP address.  Either IPv4 ama
          IPv6 addresses may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Address ama IPv6Address object.

    Raises:
        ValueError: ikiwa the *address* pitaed isn't either a v4 ama a v6
          address

    """
    jaribu:
        rudisha IPv4Address(address)
    tatizo (AddressValueError, NetmaskValueError):
        pita

    jaribu:
        rudisha IPv6Address(address)
    tatizo (AddressValueError, NetmaskValueError):
        pita

    ashiria ValueError('%r does sio appear to be an IPv4 ama IPv6 address' %
                     address)


eleza ip_network(address, strict=Kweli):
    """Take an IP string/int na rudisha an object of the correct type.

    Args:
        address: A string ama integer, the IP network.  Either IPv4 ama
          IPv6 networks may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Network ama IPv6Network object.

    Raises:
        ValueError: ikiwa the string pitaed isn't either a v4 ama a v6
          address. Or ikiwa the network has host bits set.

    """
    jaribu:
        rudisha IPv4Network(address, strict)
    tatizo (AddressValueError, NetmaskValueError):
        pita

    jaribu:
        rudisha IPv6Network(address, strict)
    tatizo (AddressValueError, NetmaskValueError):
        pita

    ashiria ValueError('%r does sio appear to be an IPv4 ama IPv6 network' %
                     address)


eleza ip_interface(address):
    """Take an IP string/int na rudisha an object of the correct type.

    Args:
        address: A string ama integer, the IP address.  Either IPv4 ama
          IPv6 addresses may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Interface ama IPv6Interface object.

    Raises:
        ValueError: ikiwa the string pitaed isn't either a v4 ama a v6
          address.

    Notes:
        The IPv?Interface classes describe an Address on a particular
        Network, so they're basically a combination of both the Address
        na Network classes.

    """
    jaribu:
        rudisha IPv4Interface(address)
    tatizo (AddressValueError, NetmaskValueError):
        pita

    jaribu:
        rudisha IPv6Interface(address)
    tatizo (AddressValueError, NetmaskValueError):
        pita

    ashiria ValueError('%r does sio appear to be an IPv4 ama IPv6 interface' %
                     address)


eleza v4_int_to_packed(address):
    """Represent an address kama 4 packed bytes kwenye network (big-endian) order.

    Args:
        address: An integer representation of an IPv4 IP address.

    Returns:
        The integer address packed kama 4 bytes kwenye network (big-endian) order.

    Raises:
        ValueError: If the integer ni negative ama too large to be an
          IPv4 IP address.

    """
    jaribu:
        rudisha address.to_bytes(4, 'big')
    tatizo OverflowError:
        ashiria ValueError("Address negative ama too large kila IPv4")


eleza v6_int_to_packed(address):
    """Represent an address kama 16 packed bytes kwenye network (big-endian) order.

    Args:
        address: An integer representation of an IPv6 IP address.

    Returns:
        The integer address packed kama 16 bytes kwenye network (big-endian) order.

    """
    jaribu:
        rudisha address.to_bytes(16, 'big')
    tatizo OverflowError:
        ashiria ValueError("Address negative ama too large kila IPv6")


eleza _split_optional_netmask(address):
    """Helper to split the netmask na ashiria AddressValueError ikiwa needed"""
    addr = str(address).split('/')
    ikiwa len(addr) > 2:
        ashiria AddressValueError("Only one '/' permitted kwenye %r" % address)
    rudisha addr


eleza _find_address_range(addresses):
    """Find a sequence of sorted deduplicated IPv#Address.

    Args:
        addresses: a list of IPv#Address objects.

    Yields:
        A tuple containing the first na last IP addresses kwenye the sequence.

    """
    it = iter(addresses)
    first = last = next(it)
    kila ip kwenye it:
        ikiwa ip._ip != last._ip + 1:
            tuma first, last
            first = ip
        last = ip
    tuma first, last


eleza _count_righthand_zero_bits(number, bits):
    """Count the number of zero bits on the right hand side.

    Args:
        number: an integer.
        bits: maximum number of bits to count.

    Returns:
        The number of zero bits on the right hand side of the number.

    """
    ikiwa number == 0:
        rudisha bits
    rudisha min(bits, (~number & (number-1)).bit_length())


eleza summarize_address_range(first, last):
    """Summarize a network range given the first na last IP addresses.

    Example:
        >>> list(summarize_address_range(IPv4Address('192.0.2.0'),
        ...                              IPv4Address('192.0.2.130')))
        ...                                #doctest: +NORMALIZE_WHITESPACE
        [IPv4Network('192.0.2.0/25'), IPv4Network('192.0.2.128/31'),
         IPv4Network('192.0.2.130/32')]

    Args:
        first: the first IPv4Address ama IPv6Address kwenye the range.
        last: the last IPv4Address ama IPv6Address kwenye the range.

    Returns:
        An iterator of the summarized IPv(4|6) network objects.

    Raise:
        TypeError:
            If the first na last objects are sio IP addresses.
            If the first na last objects are sio the same version.
        ValueError:
            If the last object ni sio greater than the first.
            If the version of the first address ni sio 4 ama 6.

    """
    ikiwa (sio (isinstance(first, _BaseAddress) na
             isinstance(last, _BaseAddress))):
        ashiria TypeError('first na last must be IP addresses, sio networks')
    ikiwa first.version != last.version:
        ashiria TypeError("%s na %s are sio of the same version" % (
                         first, last))
    ikiwa first > last:
        ashiria ValueError('last IP address must be greater than first')

    ikiwa first.version == 4:
        ip = IPv4Network
    lasivyo first.version == 6:
        ip = IPv6Network
    isipokua:
        ashiria ValueError('unknown IP version')

    ip_bits = first._max_prefixlen
    first_int = first._ip
    last_int = last._ip
    wakati first_int <= last_int:
        nbits = min(_count_righthand_zero_bits(first_int, ip_bits),
                    (last_int - first_int + 1).bit_length() - 1)
        net = ip((first_int, ip_bits - nbits))
        tuma net
        first_int += 1 << nbits
        ikiwa first_int - 1 == ip._ALL_ONES:
            koma


eleza _collapse_addresses_internal(addresses):
    """Loops through the addresses, collapsing concurrent netblocks.

    Example:

        ip1 = IPv4Network('192.0.2.0/26')
        ip2 = IPv4Network('192.0.2.64/26')
        ip3 = IPv4Network('192.0.2.128/26')
        ip4 = IPv4Network('192.0.2.192/26')

        _collapse_addresses_internal([ip1, ip2, ip3, ip4]) ->
          [IPv4Network('192.0.2.0/24')]

        This shouldn't be called directly; it ni called via
          collapse_addresses([]).

    Args:
        addresses: A list of IPv4Network's ama IPv6Network's

    Returns:
        A list of IPv4Network's ama IPv6Network's depending on what we were
        pitaed.

    """
    # First merge
    to_merge = list(addresses)
    subnets = {}
    wakati to_merge:
        net = to_merge.pop()
        supernet = net.supernet()
        existing = subnets.get(supernet)
        ikiwa existing ni Tupu:
            subnets[supernet] = net
        lasivyo existing != net:
            # Merge consecutive subnets
            toa subnets[supernet]
            to_merge.append(supernet)
    # Then iterate over resulting networks, skipping subsumed subnets
    last = Tupu
    kila net kwenye sorted(subnets.values()):
        ikiwa last ni sio Tupu:
            # Since they are sorted, last.network_address <= net.network_address
            # ni a given.
            ikiwa last.broadcast_address >= net.broadcast_address:
                endelea
        tuma net
        last = net


eleza collapse_addresses(addresses):
    """Collapse a list of IP objects.

    Example:
        collapse_addresses([IPv4Network('192.0.2.0/25'),
                            IPv4Network('192.0.2.128/25')]) ->
                           [IPv4Network('192.0.2.0/24')]

    Args:
        addresses: An iterator of IPv4Network ama IPv6Network objects.

    Returns:
        An iterator of the collapsed IPv(4|6)Network objects.

    Raises:
        TypeError: If pitaed a list of mixed version objects.

    """
    addrs = []
    ips = []
    nets = []

    # split IP addresses na networks
    kila ip kwenye addresses:
        ikiwa isinstance(ip, _BaseAddress):
            ikiwa ips na ips[-1]._version != ip._version:
                ashiria TypeError("%s na %s are sio of the same version" % (
                                 ip, ips[-1]))
            ips.append(ip)
        lasivyo ip._prefixlen == ip._max_prefixlen:
            ikiwa ips na ips[-1]._version != ip._version:
                ashiria TypeError("%s na %s are sio of the same version" % (
                                 ip, ips[-1]))
            jaribu:
                ips.append(ip.ip)
            tatizo AttributeError:
                ips.append(ip.network_address)
        isipokua:
            ikiwa nets na nets[-1]._version != ip._version:
                ashiria TypeError("%s na %s are sio of the same version" % (
                                 ip, nets[-1]))
            nets.append(ip)

    # sort na dedup
    ips = sorted(set(ips))

    # find consecutive address ranges kwenye the sorted sequence na summarize them
    ikiwa ips:
        kila first, last kwenye _find_address_range(ips):
            addrs.extend(summarize_address_range(first, last))

    rudisha _collapse_addresses_internal(addrs + nets)


eleza get_mixed_type_key(obj):
    """Return a key suitable kila sorting between networks na addresses.

    Address na Network objects are sio sortable by default; they're
    fundamentally different so the expression

        IPv4Address('192.0.2.0') <= IPv4Network('192.0.2.0/24')

    doesn't make any sense.  There are some times however, where you may wish
    to have ipaddress sort these kila you anyway. If you need to do this, you
    can use this function kama the key= argument to sorted().

    Args:
      obj: either a Network ama Address object.
    Returns:
      appropriate key.

    """
    ikiwa isinstance(obj, _BaseNetwork):
        rudisha obj._get_networks_key()
    lasivyo isinstance(obj, _BaseAddress):
        rudisha obj._get_address_key()
    rudisha NotImplemented


kundi _IPAddressBase:

    """The mother class."""

    __slots__ = ()

    @property
    eleza exploded(self):
        """Return the longhand version of the IP address kama a string."""
        rudisha self._explode_shorthand_ip_string()

    @property
    eleza compressed(self):
        """Return the shorthand version of the IP address kama a string."""
        rudisha str(self)

    @property
    eleza reverse_pointer(self):
        """The name of the reverse DNS pointer kila the IP address, e.g.:
            >>> ipaddress.ip_address("127.0.0.1").reverse_pointer
            '1.0.0.127.in-addr.arpa'
            >>> ipaddress.ip_address("2001:db8::1").reverse_pointer
            '1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'

        """
        rudisha self._reverse_pointer()

    @property
    eleza version(self):
        msg = '%200s has no version specified' % (type(self),)
        ashiria NotImplementedError(msg)

    eleza _check_int_address(self, address):
        ikiwa address < 0:
            msg = "%d (< 0) ni sio permitted kama an IPv%d address"
            ashiria AddressValueError(msg % (address, self._version))
        ikiwa address > self._ALL_ONES:
            msg = "%d (>= 2**%d) ni sio permitted kama an IPv%d address"
            ashiria AddressValueError(msg % (address, self._max_prefixlen,
                                           self._version))

    eleza _check_packed_address(self, address, expected_len):
        address_len = len(address)
        ikiwa address_len != expected_len:
            msg = "%r (len %d != %d) ni sio permitted kama an IPv%d address"
            ashiria AddressValueError(msg % (address, address_len,
                                           expected_len, self._version))

    @classmethod
    eleza _ip_int_from_prefix(cls, prefixlen):
        """Turn the prefix length into a bitwise netmask

        Args:
            prefixlen: An integer, the prefix length.

        Returns:
            An integer.

        """
        rudisha cls._ALL_ONES ^ (cls._ALL_ONES >> prefixlen)

    @classmethod
    eleza _prefix_from_ip_int(cls, ip_int):
        """Return prefix length kutoka the bitwise netmask.

        Args:
            ip_int: An integer, the netmask kwenye expanded bitwise format

        Returns:
            An integer, the prefix length.

        Raises:
            ValueError: If the input intermingles zeroes & ones
        """
        trailing_zeroes = _count_righthand_zero_bits(ip_int,
                                                     cls._max_prefixlen)
        prefixlen = cls._max_prefixlen - trailing_zeroes
        leading_ones = ip_int >> trailing_zeroes
        all_ones = (1 << prefixlen) - 1
        ikiwa leading_ones != all_ones:
            byteslen = cls._max_prefixlen // 8
            details = ip_int.to_bytes(byteslen, 'big')
            msg = 'Netmask pattern %r mixes zeroes & ones'
            ashiria ValueError(msg % details)
        rudisha prefixlen

    @classmethod
    eleza _report_invalid_netmask(cls, netmask_str):
        msg = '%r ni sio a valid netmask' % netmask_str
        ashiria NetmaskValueError(msg) kutoka Tupu

    @classmethod
    eleza _prefix_from_prefix_string(cls, prefixlen_str):
        """Return prefix length kutoka a numeric string

        Args:
            prefixlen_str: The string to be converted

        Returns:
            An integer, the prefix length.

        Raises:
            NetmaskValueError: If the input ni sio a valid netmask
        """
        # int allows a leading +/- kama well kama surrounding whitespace,
        # so we ensure that isn't the case
        ikiwa sio (prefixlen_str.isascii() na prefixlen_str.isdigit()):
            cls._report_invalid_netmask(prefixlen_str)
        jaribu:
            prefixlen = int(prefixlen_str)
        tatizo ValueError:
            cls._report_invalid_netmask(prefixlen_str)
        ikiwa sio (0 <= prefixlen <= cls._max_prefixlen):
            cls._report_invalid_netmask(prefixlen_str)
        rudisha prefixlen

    @classmethod
    eleza _prefix_from_ip_string(cls, ip_str):
        """Turn a netmask/hostmask string into a prefix length

        Args:
            ip_str: The netmask/hostmask to be converted

        Returns:
            An integer, the prefix length.

        Raises:
            NetmaskValueError: If the input ni sio a valid netmask/hostmask
        """
        # Parse the netmask/hostmask like an IP address.
        jaribu:
            ip_int = cls._ip_int_from_string(ip_str)
        tatizo AddressValueError:
            cls._report_invalid_netmask(ip_str)

        # Try matching a netmask (this would be /1*0*/ kama a bitwise regexp).
        # Note that the two ambiguous cases (all-ones na all-zeroes) are
        # treated kama netmasks.
        jaribu:
            rudisha cls._prefix_from_ip_int(ip_int)
        tatizo ValueError:
            pita

        # Invert the bits, na try matching a /0+1+/ hostmask instead.
        ip_int ^= cls._ALL_ONES
        jaribu:
            rudisha cls._prefix_from_ip_int(ip_int)
        tatizo ValueError:
            cls._report_invalid_netmask(ip_str)

    @classmethod
    eleza _split_addr_prefix(cls, address):
        """Helper function to parse address of Network/Interface.

        Arg:
            address: Argument of Network/Interface.

        Returns:
            (addr, prefix) tuple.
        """
        # a packed address ama integer
        ikiwa isinstance(address, (bytes, int)):
            rudisha address, cls._max_prefixlen

        ikiwa sio isinstance(address, tuple):
            # Assume input argument to be string ama any object representation
            # which converts into a formatted IP prefix string.
            address = _split_optional_netmask(address)

        # Constructing kutoka a tuple (addr, [mask])
        ikiwa len(address) > 1:
            rudisha address
        rudisha address[0], cls._max_prefixlen

    eleza __reduce__(self):
        rudisha self.__class__, (str(self),)


@functools.total_ordering
kundi _BaseAddress(_IPAddressBase):

    """A generic IP object.

    This IP kundi contains the version independent methods which are
    used by single IP addresses.
    """

    __slots__ = ()

    eleza __int__(self):
        rudisha self._ip

    eleza __eq__(self, other):
        jaribu:
            rudisha (self._ip == other._ip
                    na self._version == other._version)
        tatizo AttributeError:
            rudisha NotImplemented

    eleza __lt__(self, other):
        ikiwa sio isinstance(other, _BaseAddress):
            rudisha NotImplemented
        ikiwa self._version != other._version:
            ashiria TypeError('%s na %s are sio of the same version' % (
                             self, other))
        ikiwa self._ip != other._ip:
            rudisha self._ip < other._ip
        rudisha Uongo

    # Shorthand kila Integer addition na subtraction. This ni sio
    # meant to ever support addition/subtraction of addresses.
    eleza __add__(self, other):
        ikiwa sio isinstance(other, int):
            rudisha NotImplemented
        rudisha self.__class__(int(self) + other)

    eleza __sub__(self, other):
        ikiwa sio isinstance(other, int):
            rudisha NotImplemented
        rudisha self.__class__(int(self) - other)

    eleza __repr__(self):
        rudisha '%s(%r)' % (self.__class__.__name__, str(self))

    eleza __str__(self):
        rudisha str(self._string_from_ip_int(self._ip))

    eleza __hash__(self):
        rudisha hash(hex(int(self._ip)))

    eleza _get_address_key(self):
        rudisha (self._version, self)

    eleza __reduce__(self):
        rudisha self.__class__, (self._ip,)


@functools.total_ordering
kundi _BaseNetwork(_IPAddressBase):
    """A generic IP network object.

    This IP kundi contains the version independent methods which are
    used by networks.
    """

    eleza __repr__(self):
        rudisha '%s(%r)' % (self.__class__.__name__, str(self))

    eleza __str__(self):
        rudisha '%s/%d' % (self.network_address, self.prefixlen)

    eleza hosts(self):
        """Generate Iterator over usable hosts kwenye a network.

        This ni like __iter__ tatizo it doesn't rudisha the network
        ama broadcast addresses.

        """
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        kila x kwenye range(network + 1, broadcast):
            tuma self._address_class(x)

    eleza __iter__(self):
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        kila x kwenye range(network, broadcast + 1):
            tuma self._address_class(x)

    eleza __getitem__(self, n):
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        ikiwa n >= 0:
            ikiwa network + n > broadcast:
                ashiria IndexError('address out of range')
            rudisha self._address_class(network + n)
        isipokua:
            n += 1
            ikiwa broadcast + n < network:
                ashiria IndexError('address out of range')
            rudisha self._address_class(broadcast + n)

    eleza __lt__(self, other):
        ikiwa sio isinstance(other, _BaseNetwork):
            rudisha NotImplemented
        ikiwa self._version != other._version:
            ashiria TypeError('%s na %s are sio of the same version' % (
                             self, other))
        ikiwa self.network_address != other.network_address:
            rudisha self.network_address < other.network_address
        ikiwa self.netmask != other.netmask:
            rudisha self.netmask < other.netmask
        rudisha Uongo

    eleza __eq__(self, other):
        jaribu:
            rudisha (self._version == other._version na
                    self.network_address == other.network_address na
                    int(self.netmask) == int(other.netmask))
        tatizo AttributeError:
            rudisha NotImplemented

    eleza __hash__(self):
        rudisha hash(int(self.network_address) ^ int(self.netmask))

    eleza __contains__(self, other):
        # always false ikiwa one ni v4 na the other ni v6.
        ikiwa self._version != other._version:
            rudisha Uongo
        # dealing ukijumuisha another network.
        ikiwa isinstance(other, _BaseNetwork):
            rudisha Uongo
        # dealing ukijumuisha another address
        isipokua:
            # address
            rudisha other._ip & self.netmask._ip == self.network_address._ip

    eleza overlaps(self, other):
        """Tell ikiwa self ni partly contained kwenye other."""
        rudisha self.network_address kwenye other ama (
            self.broadcast_address kwenye other ama (
                other.network_address kwenye self ama (
                    other.broadcast_address kwenye self)))

    @functools.cached_property
    eleza broadcast_address(self):
        rudisha self._address_class(int(self.network_address) |
                                   int(self.hostmask))

    @functools.cached_property
    eleza hostmask(self):
        rudisha self._address_class(int(self.netmask) ^ self._ALL_ONES)

    @property
    eleza with_prefixlen(self):
        rudisha '%s/%d' % (self.network_address, self._prefixlen)

    @property
    eleza with_netmask(self):
        rudisha '%s/%s' % (self.network_address, self.netmask)

    @property
    eleza with_hostmask(self):
        rudisha '%s/%s' % (self.network_address, self.hostmask)

    @property
    eleza num_addresses(self):
        """Number of hosts kwenye the current subnet."""
        rudisha int(self.broadcast_address) - int(self.network_address) + 1

    @property
    eleza _address_class(self):
        # Returning bare address objects (rather than interfaces) allows for
        # more consistent behaviour across the network address, broadcast
        # address na individual host addresses.
        msg = '%200s has no associated address class' % (type(self),)
        ashiria NotImplementedError(msg)

    @property
    eleza prefixlen(self):
        rudisha self._prefixlen

    eleza address_exclude(self, other):
        """Remove an address kutoka a larger block.

        For example:

            addr1 = ip_network('192.0.2.0/28')
            addr2 = ip_network('192.0.2.1/32')
            list(addr1.address_exclude(addr2)) =
                [IPv4Network('192.0.2.0/32'), IPv4Network('192.0.2.2/31'),
                 IPv4Network('192.0.2.4/30'), IPv4Network('192.0.2.8/29')]

        ama IPv6:

            addr1 = ip_network('2001:db8::1/32')
            addr2 = ip_network('2001:db8::1/128')
            list(addr1.address_exclude(addr2)) =
                [ip_network('2001:db8::1/128'),
                 ip_network('2001:db8::2/127'),
                 ip_network('2001:db8::4/126'),
                 ip_network('2001:db8::8/125'),
                 ...
                 ip_network('2001:db8:8000::/33')]

        Args:
            other: An IPv4Network ama IPv6Network object of the same type.

        Returns:
            An iterator of the IPv(4|6)Network objects which ni self
            minus other.

        Raises:
            TypeError: If self na other are of differing address
              versions, ama ikiwa other ni sio a network object.
            ValueError: If other ni sio completely contained by self.

        """
        ikiwa sio self._version == other._version:
            ashiria TypeError("%s na %s are sio of the same version" % (
                             self, other))

        ikiwa sio isinstance(other, _BaseNetwork):
            ashiria TypeError("%s ni sio a network object" % other)

        ikiwa sio other.subnet_of(self):
            ashiria ValueError('%s sio contained kwenye %s' % (other, self))
        ikiwa other == self:
            rudisha

        # Make sure we're comparing the network of other.
        other = other.__class__('%s/%s' % (other.network_address,
                                           other.prefixlen))

        s1, s2 = self.subnets()
        wakati s1 != other na s2 != other:
            ikiwa other.subnet_of(s1):
                tuma s2
                s1, s2 = s1.subnets()
            lasivyo other.subnet_of(s2):
                tuma s1
                s1, s2 = s2.subnets()
            isipokua:
                # If we got here, there's a bug somewhere.
                ashiria AssertionError('Error performing exclusion: '
                                     's1: %s s2: %s other: %s' %
                                     (s1, s2, other))
        ikiwa s1 == other:
            tuma s2
        lasivyo s2 == other:
            tuma s1
        isipokua:
            # If we got here, there's a bug somewhere.
            ashiria AssertionError('Error performing exclusion: '
                                 's1: %s s2: %s other: %s' %
                                 (s1, s2, other))

    eleza compare_networks(self, other):
        """Compare two IP objects.

        This ni only concerned about the comparison of the integer
        representation of the network addresses.  This means that the
        host bits aren't considered at all kwenye this method.  If you want
        to compare host bits, you can easily enough do a
        'HostA._ip < HostB._ip'

        Args:
            other: An IP object.

        Returns:
            If the IP versions of self na other are the same, returns:

            -1 ikiwa self < other:
              eg: IPv4Network('192.0.2.0/25') < IPv4Network('192.0.2.128/25')
              IPv6Network('2001:db8::1000/124') <
                  IPv6Network('2001:db8::2000/124')
            0 ikiwa self == other
              eg: IPv4Network('192.0.2.0/24') == IPv4Network('192.0.2.0/24')
              IPv6Network('2001:db8::1000/124') ==
                  IPv6Network('2001:db8::1000/124')
            1 ikiwa self > other
              eg: IPv4Network('192.0.2.128/25') > IPv4Network('192.0.2.0/25')
                  IPv6Network('2001:db8::2000/124') >
                      IPv6Network('2001:db8::1000/124')

          Raises:
              TypeError ikiwa the IP versions are different.

        """
        # does this need to ashiria a ValueError?
        ikiwa self._version != other._version:
            ashiria TypeError('%s na %s are sio of the same type' % (
                             self, other))
        # self._version == other._version below here:
        ikiwa self.network_address < other.network_address:
            rudisha -1
        ikiwa self.network_address > other.network_address:
            rudisha 1
        # self.network_address == other.network_address below here:
        ikiwa self.netmask < other.netmask:
            rudisha -1
        ikiwa self.netmask > other.netmask:
            rudisha 1
        rudisha 0

    eleza _get_networks_key(self):
        """Network-only key function.

        Returns an object that identifies this address' network na
        netmask. This function ni a suitable "key" argument kila sorted()
        na list.sort().

        """
        rudisha (self._version, self.network_address, self.netmask)

    eleza subnets(self, prefixlen_diff=1, new_prefix=Tupu):
        """The subnets which join to make the current subnet.

        In the case that self contains only one IP
        (self._prefixlen == 32 kila IPv4 ama self._prefixlen == 128
        kila IPv6), tuma an iterator ukijumuisha just ourself.

        Args:
            prefixlen_diff: An integer, the amount the prefix length
              should be increased by. This should sio be set if
              new_prefix ni also set.
            new_prefix: The desired new prefix length. This must be a
              larger number (smaller prefix) than the existing prefix.
              This should sio be set ikiwa prefixlen_diff ni also set.

        Returns:
            An iterator of IPv(4|6) objects.

        Raises:
            ValueError: The prefixlen_diff ni too small ama too large.
                OR
            prefixlen_diff na new_prefix are both set ama new_prefix
              ni a smaller number than the current prefix (smaller
              number means a larger network)

        """
        ikiwa self._prefixlen == self._max_prefixlen:
            tuma self
            rudisha

        ikiwa new_prefix ni sio Tupu:
            ikiwa new_prefix < self._prefixlen:
                ashiria ValueError('new prefix must be longer')
            ikiwa prefixlen_diff != 1:
                ashiria ValueError('cansio set prefixlen_diff na new_prefix')
            prefixlen_diff = new_prefix - self._prefixlen

        ikiwa prefixlen_diff < 0:
            ashiria ValueError('prefix length diff must be > 0')
        new_prefixlen = self._prefixlen + prefixlen_diff

        ikiwa new_prefixlen > self._max_prefixlen:
            ashiria ValueError(
                'prefix length diff %d ni invalid kila netblock %s' % (
                    new_prefixlen, self))

        start = int(self.network_address)
        end = int(self.broadcast_address) + 1
        step = (int(self.hostmask) + 1) >> prefixlen_diff
        kila new_addr kwenye range(start, end, step):
            current = self.__class__((new_addr, new_prefixlen))
            tuma current

    eleza supernet(self, prefixlen_diff=1, new_prefix=Tupu):
        """The supernet containing the current network.

        Args:
            prefixlen_diff: An integer, the amount the prefix length of
              the network should be decreased by.  For example, given a
              /24 network na a prefixlen_diff of 3, a supernet ukijumuisha a
              /21 netmask ni returned.

        Returns:
            An IPv4 network object.

        Raises:
            ValueError: If self.prefixlen - prefixlen_diff < 0. I.e., you have
              a negative prefix length.
                OR
            If prefixlen_diff na new_prefix are both set ama new_prefix ni a
              larger number than the current prefix (larger number means a
              smaller network)

        """
        ikiwa self._prefixlen == 0:
            rudisha self

        ikiwa new_prefix ni sio Tupu:
            ikiwa new_prefix > self._prefixlen:
                ashiria ValueError('new prefix must be shorter')
            ikiwa prefixlen_diff != 1:
                ashiria ValueError('cansio set prefixlen_diff na new_prefix')
            prefixlen_diff = self._prefixlen - new_prefix

        new_prefixlen = self.prefixlen - prefixlen_diff
        ikiwa new_prefixlen < 0:
            ashiria ValueError(
                'current prefixlen ni %d, cansio have a prefixlen_diff of %d' %
                (self.prefixlen, prefixlen_diff))
        rudisha self.__class__((
            int(self.network_address) & (int(self.netmask) << prefixlen_diff),
            new_prefixlen
            ))

    @property
    eleza is_multicast(self):
        """Test ikiwa the address ni reserved kila multicast use.

        Returns:
            A boolean, Kweli ikiwa the address ni a multicast address.
            See RFC 2373 2.7 kila details.

        """
        rudisha (self.network_address.is_multicast na
                self.broadcast_address.is_multicast)

    @staticmethod
    eleza _is_subnet_of(a, b):
        jaribu:
            # Always false ikiwa one ni v4 na the other ni v6.
            ikiwa a._version != b._version:
                ashiria TypeError(f"{a} na {b} are sio of the same version")
            rudisha (b.network_address <= a.network_address na
                    b.broadcast_address >= a.broadcast_address)
        tatizo AttributeError:
            ashiria TypeError(f"Unable to test subnet containment "
                            f"between {a} na {b}")

    eleza subnet_of(self, other):
        """Return Kweli ikiwa this network ni a subnet of other."""
        rudisha self._is_subnet_of(self, other)

    eleza supernet_of(self, other):
        """Return Kweli ikiwa this network ni a supernet of other."""
        rudisha self._is_subnet_of(other, self)

    @property
    eleza is_reserved(self):
        """Test ikiwa the address ni otherwise IETF reserved.

        Returns:
            A boolean, Kweli ikiwa the address ni within one of the
            reserved IPv6 Network ranges.

        """
        rudisha (self.network_address.is_reserved na
                self.broadcast_address.is_reserved)

    @property
    eleza is_link_local(self):
        """Test ikiwa the address ni reserved kila link-local.

        Returns:
            A boolean, Kweli ikiwa the address ni reserved per RFC 4291.

        """
        rudisha (self.network_address.is_link_local na
                self.broadcast_address.is_link_local)

    @property
    eleza is_private(self):
        """Test ikiwa this address ni allocated kila private networks.

        Returns:
            A boolean, Kweli ikiwa the address ni reserved per
            iana-ipv4-special-registry ama iana-ipv6-special-registry.

        """
        rudisha (self.network_address.is_private na
                self.broadcast_address.is_private)

    @property
    eleza is_global(self):
        """Test ikiwa this address ni allocated kila public networks.

        Returns:
            A boolean, Kweli ikiwa the address ni sio reserved per
            iana-ipv4-special-registry ama iana-ipv6-special-registry.

        """
        rudisha sio self.is_private

    @property
    eleza is_unspecified(self):
        """Test ikiwa the address ni unspecified.

        Returns:
            A boolean, Kweli ikiwa this ni the unspecified address kama defined kwenye
            RFC 2373 2.5.2.

        """
        rudisha (self.network_address.is_unspecified na
                self.broadcast_address.is_unspecified)

    @property
    eleza is_loopback(self):
        """Test ikiwa the address ni a loopback address.

        Returns:
            A boolean, Kweli ikiwa the address ni a loopback address kama defined kwenye
            RFC 2373 2.5.3.

        """
        rudisha (self.network_address.is_loopback na
                self.broadcast_address.is_loopback)


kundi _BaseV4:

    """Base IPv4 object.

    The following methods are used by IPv4 objects kwenye both single IP
    addresses na networks.

    """

    __slots__ = ()
    _version = 4
    # Equivalent to 255.255.255.255 ama 32 bits of 1's.
    _ALL_ONES = (2**IPV4LENGTH) - 1

    _max_prefixlen = IPV4LENGTH
    # There are only a handful of valid v4 netmasks, so we cache them all
    # when constructed (see _make_netmask()).
    _netmask_cache = {}

    eleza _explode_shorthand_ip_string(self):
        rudisha str(self)

    @classmethod
    eleza _make_netmask(cls, arg):
        """Make a (netmask, prefix_len) tuple kutoka the given argument.

        Argument can be:
        - an integer (the prefix length)
        - a string representing the prefix length (e.g. "24")
        - a string representing the prefix netmask (e.g. "255.255.255.0")
        """
        ikiwa arg haiko kwenye cls._netmask_cache:
            ikiwa isinstance(arg, int):
                prefixlen = arg
                ikiwa sio (0 <= prefixlen <= cls._max_prefixlen):
                    cls._report_invalid_netmask(prefixlen)
            isipokua:
                jaribu:
                    # Check kila a netmask kwenye prefix length form
                    prefixlen = cls._prefix_from_prefix_string(arg)
                tatizo NetmaskValueError:
                    # Check kila a netmask ama hostmask kwenye dotted-quad form.
                    # This may ashiria NetmaskValueError.
                    prefixlen = cls._prefix_from_ip_string(arg)
            netmask = IPv4Address(cls._ip_int_from_prefix(prefixlen))
            cls._netmask_cache[arg] = netmask, prefixlen
        rudisha cls._netmask_cache[arg]

    @classmethod
    eleza _ip_int_from_string(cls, ip_str):
        """Turn the given IP string into an integer kila comparison.

        Args:
            ip_str: A string, the IP ip_str.

        Returns:
            The IP ip_str kama an integer.

        Raises:
            AddressValueError: ikiwa ip_str isn't a valid IPv4 Address.

        """
        ikiwa sio ip_str:
            ashiria AddressValueError('Address cansio be empty')

        octets = ip_str.split('.')
        ikiwa len(octets) != 4:
            ashiria AddressValueError("Expected 4 octets kwenye %r" % ip_str)

        jaribu:
            rudisha int.from_bytes(map(cls._parse_octet, octets), 'big')
        tatizo ValueError kama exc:
            ashiria AddressValueError("%s kwenye %r" % (exc, ip_str)) kutoka Tupu

    @classmethod
    eleza _parse_octet(cls, octet_str):
        """Convert a decimal octet into an integer.

        Args:
            octet_str: A string, the number to parse.

        Returns:
            The octet kama an integer.

        Raises:
            ValueError: ikiwa the octet isn't strictly a decimal kutoka [0..255].

        """
        ikiwa sio octet_str:
            ashiria ValueError("Empty octet sio permitted")
        # Whitelist the characters, since int() allows a lot of bizarre stuff.
        ikiwa sio (octet_str.isascii() na octet_str.isdigit()):
            msg = "Only decimal digits permitted kwenye %r"
            ashiria ValueError(msg % octet_str)
        # We do the length check second, since the invalid character error
        # ni likely to be more informative kila the user
        ikiwa len(octet_str) > 3:
            msg = "At most 3 characters permitted kwenye %r"
            ashiria ValueError(msg % octet_str)
        # Convert to integer (we know digits are legal)
        octet_int = int(octet_str, 10)
        ikiwa octet_int > 255:
            ashiria ValueError("Octet %d (> 255) sio permitted" % octet_int)
        rudisha octet_int

    @classmethod
    eleza _string_from_ip_int(cls, ip_int):
        """Turns a 32-bit integer into dotted decimal notation.

        Args:
            ip_int: An integer, the IP address.

        Returns:
            The IP address kama a string kwenye dotted decimal notation.

        """
        rudisha '.'.join(map(str, ip_int.to_bytes(4, 'big')))

    eleza _reverse_pointer(self):
        """Return the reverse DNS pointer name kila the IPv4 address.

        This implements the method described kwenye RFC1035 3.5.

        """
        reverse_octets = str(self).split('.')[::-1]
        rudisha '.'.join(reverse_octets) + '.in-addr.arpa'

    @property
    eleza max_prefixlen(self):
        rudisha self._max_prefixlen

    @property
    eleza version(self):
        rudisha self._version


kundi IPv4Address(_BaseV4, _BaseAddress):

    """Represent na manipulate single IPv4 Addresses."""

    __slots__ = ('_ip', '__weakref__')

    eleza __init__(self, address):

        """
        Args:
            address: A string ama integer representing the IP

              Additionally, an integer can be pitaed, so
              IPv4Address('192.0.2.1') == IPv4Address(3221225985).
              or, more generally
              IPv4Address(int(IPv4Address('192.0.2.1'))) ==
                IPv4Address('192.0.2.1')

        Raises:
            AddressValueError: If ipaddress isn't a valid IPv4 address.

        """
        # Efficient constructor kutoka integer.
        ikiwa isinstance(address, int):
            self._check_int_address(address)
            self._ip = address
            rudisha

        # Constructing kutoka a packed address
        ikiwa isinstance(address, bytes):
            self._check_packed_address(address, 4)
            self._ip = int.from_bytes(address, 'big')
            rudisha

        # Assume input argument to be string ama any object representation
        # which converts into a formatted IP string.
        addr_str = str(address)
        ikiwa '/' kwenye addr_str:
            ashiria AddressValueError("Unexpected '/' kwenye %r" % address)
        self._ip = self._ip_int_from_string(addr_str)

    @property
    eleza packed(self):
        """The binary representation of this address."""
        rudisha v4_int_to_packed(self._ip)

    @property
    eleza is_reserved(self):
        """Test ikiwa the address ni otherwise IETF reserved.

         Returns:
             A boolean, Kweli ikiwa the address ni within the
             reserved IPv4 Network range.

        """
        rudisha self kwenye self._constants._reserved_network

    @property
    @functools.lru_cache()
    eleza is_private(self):
        """Test ikiwa this address ni allocated kila private networks.

        Returns:
            A boolean, Kweli ikiwa the address ni reserved per
            iana-ipv4-special-registry.

        """
        rudisha any(self kwenye net kila net kwenye self._constants._private_networks)

    @property
    @functools.lru_cache()
    eleza is_global(self):
        rudisha self haiko kwenye self._constants._public_network na sio self.is_private

    @property
    eleza is_multicast(self):
        """Test ikiwa the address ni reserved kila multicast use.

        Returns:
            A boolean, Kweli ikiwa the address ni multicast.
            See RFC 3171 kila details.

        """
        rudisha self kwenye self._constants._multicast_network

    @property
    eleza is_unspecified(self):
        """Test ikiwa the address ni unspecified.

        Returns:
            A boolean, Kweli ikiwa this ni the unspecified address kama defined kwenye
            RFC 5735 3.

        """
        rudisha self == self._constants._unspecified_address

    @property
    eleza is_loopback(self):
        """Test ikiwa the address ni a loopback address.

        Returns:
            A boolean, Kweli ikiwa the address ni a loopback per RFC 3330.

        """
        rudisha self kwenye self._constants._loopback_network

    @property
    eleza is_link_local(self):
        """Test ikiwa the address ni reserved kila link-local.

        Returns:
            A boolean, Kweli ikiwa the address ni link-local per RFC 3927.

        """
        rudisha self kwenye self._constants._linklocal_network


kundi IPv4Interface(IPv4Address):

    eleza __init__(self, address):
        addr, mask = self._split_addr_prefix(address)

        IPv4Address.__init__(self, addr)
        self.network = IPv4Network((addr, mask), strict=Uongo)
        self.netmask = self.network.netmask
        self._prefixlen = self.network._prefixlen

    @functools.cached_property
    eleza hostmask(self):
        rudisha self.network.hostmask

    eleza __str__(self):
        rudisha '%s/%d' % (self._string_from_ip_int(self._ip),
                          self._prefixlen)

    eleza __eq__(self, other):
        address_equal = IPv4Address.__eq__(self, other)
        ikiwa sio address_equal ama address_equal ni NotImplemented:
            rudisha address_equal
        jaribu:
            rudisha self.network == other.network
        tatizo AttributeError:
            # An interface ukijumuisha an associated network ni NOT the
            # same kama an unassociated address. That's why the hash
            # takes the extra info into account.
            rudisha Uongo

    eleza __lt__(self, other):
        address_less = IPv4Address.__lt__(self, other)
        ikiwa address_less ni NotImplemented:
            rudisha NotImplemented
        jaribu:
            rudisha (self.network < other.network ama
                    self.network == other.network na address_less)
        tatizo AttributeError:
            # We *do* allow addresses na interfaces to be sorted. The
            # unassociated address ni considered less than all interfaces.
            rudisha Uongo

    eleza __hash__(self):
        rudisha self._ip ^ self._prefixlen ^ int(self.network.network_address)

    __reduce__ = _IPAddressBase.__reduce__

    @property
    eleza ip(self):
        rudisha IPv4Address(self._ip)

    @property
    eleza with_prefixlen(self):
        rudisha '%s/%s' % (self._string_from_ip_int(self._ip),
                          self._prefixlen)

    @property
    eleza with_netmask(self):
        rudisha '%s/%s' % (self._string_from_ip_int(self._ip),
                          self.netmask)

    @property
    eleza with_hostmask(self):
        rudisha '%s/%s' % (self._string_from_ip_int(self._ip),
                          self.hostmask)


kundi IPv4Network(_BaseV4, _BaseNetwork):

    """This kundi represents na manipulates 32-bit IPv4 network + addresses..

    Attributes: [examples kila IPv4Network('192.0.2.0/27')]
        .network_address: IPv4Address('192.0.2.0')
        .hostmask: IPv4Address('0.0.0.31')
        .broadcast_address: IPv4Address('192.0.2.32')
        .netmask: IPv4Address('255.255.255.224')
        .prefixlen: 27

    """
    # Class to use when creating address objects
    _address_class = IPv4Address

    eleza __init__(self, address, strict=Kweli):
        """Instantiate a new IPv4 network object.

        Args:
            address: A string ama integer representing the IP [& network].
              '192.0.2.0/24'
              '192.0.2.0/255.255.255.0'
              '192.0.0.2/0.0.0.255'
              are all functionally the same kwenye IPv4. Similarly,
              '192.0.2.1'
              '192.0.2.1/255.255.255.255'
              '192.0.2.1/32'
              are also functionally equivalent. That ni to say, failing to
              provide a subnetmask will create an object ukijumuisha a mask of /32.

              If the mask (portion after the / kwenye the argument) ni given kwenye
              dotted quad form, it ni treated kama a netmask ikiwa it starts ukijumuisha a
              non-zero field (e.g. /255.0.0.0 == /8) na kama a hostmask ikiwa it
              starts ukijumuisha a zero field (e.g. 0.255.255.255 == /8), ukijumuisha the
              single exception of an all-zero mask which ni treated kama a
              netmask == /0. If no mask ni given, a default of /32 ni used.

              Additionally, an integer can be pitaed, so
              IPv4Network('192.0.2.1') == IPv4Network(3221225985)
              or, more generally
              IPv4Interface(int(IPv4Interface('192.0.2.1'))) ==
                IPv4Interface('192.0.2.1')

        Raises:
            AddressValueError: If ipaddress isn't a valid IPv4 address.
            NetmaskValueError: If the netmask isn't valid for
              an IPv4 address.
            ValueError: If strict ni Kweli na a network address ni sio
              supplied.
        """
        addr, mask = self._split_addr_prefix(address)

        self.network_address = IPv4Address(addr)
        self.netmask, self._prefixlen = self._make_netmask(mask)
        packed = int(self.network_address)
        ikiwa packed & int(self.netmask) != packed:
            ikiwa strict:
                ashiria ValueError('%s has host bits set' % self)
            isipokua:
                self.network_address = IPv4Address(packed &
                                                   int(self.netmask))

        ikiwa self._prefixlen == (self._max_prefixlen - 1):
            self.hosts = self.__iter__

    @property
    @functools.lru_cache()
    eleza is_global(self):
        """Test ikiwa this address ni allocated kila public networks.

        Returns:
            A boolean, Kweli ikiwa the address ni sio reserved per
            iana-ipv4-special-registry.

        """
        rudisha (sio (self.network_address kwenye IPv4Network('100.64.0.0/10') na
                    self.broadcast_address kwenye IPv4Network('100.64.0.0/10')) na
                sio self.is_private)


kundi _IPv4Constants:
    _linklocal_network = IPv4Network('169.254.0.0/16')

    _loopback_network = IPv4Network('127.0.0.0/8')

    _multicast_network = IPv4Network('224.0.0.0/4')

    _public_network = IPv4Network('100.64.0.0/10')

    _private_networks = [
        IPv4Network('0.0.0.0/8'),
        IPv4Network('10.0.0.0/8'),
        IPv4Network('127.0.0.0/8'),
        IPv4Network('169.254.0.0/16'),
        IPv4Network('172.16.0.0/12'),
        IPv4Network('192.0.0.0/29'),
        IPv4Network('192.0.0.170/31'),
        IPv4Network('192.0.2.0/24'),
        IPv4Network('192.168.0.0/16'),
        IPv4Network('198.18.0.0/15'),
        IPv4Network('198.51.100.0/24'),
        IPv4Network('203.0.113.0/24'),
        IPv4Network('240.0.0.0/4'),
        IPv4Network('255.255.255.255/32'),
        ]

    _reserved_network = IPv4Network('240.0.0.0/4')

    _unspecified_address = IPv4Address('0.0.0.0')


IPv4Address._constants = _IPv4Constants


kundi _BaseV6:

    """Base IPv6 object.

    The following methods are used by IPv6 objects kwenye both single IP
    addresses na networks.

    """

    __slots__ = ()
    _version = 6
    _ALL_ONES = (2**IPV6LENGTH) - 1
    _HEXTET_COUNT = 8
    _HEX_DIGITS = frozenset('0123456789ABCDEFabcdef')
    _max_prefixlen = IPV6LENGTH

    # There are only a bunch of valid v6 netmasks, so we cache them all
    # when constructed (see _make_netmask()).
    _netmask_cache = {}

    @classmethod
    eleza _make_netmask(cls, arg):
        """Make a (netmask, prefix_len) tuple kutoka the given argument.

        Argument can be:
        - an integer (the prefix length)
        - a string representing the prefix length (e.g. "24")
        - a string representing the prefix netmask (e.g. "255.255.255.0")
        """
        ikiwa arg haiko kwenye cls._netmask_cache:
            ikiwa isinstance(arg, int):
                prefixlen = arg
                ikiwa sio (0 <= prefixlen <= cls._max_prefixlen):
                    cls._report_invalid_netmask(prefixlen)
            isipokua:
                prefixlen = cls._prefix_from_prefix_string(arg)
            netmask = IPv6Address(cls._ip_int_from_prefix(prefixlen))
            cls._netmask_cache[arg] = netmask, prefixlen
        rudisha cls._netmask_cache[arg]

    @classmethod
    eleza _ip_int_from_string(cls, ip_str):
        """Turn an IPv6 ip_str into an integer.

        Args:
            ip_str: A string, the IPv6 ip_str.

        Returns:
            An int, the IPv6 address

        Raises:
            AddressValueError: ikiwa ip_str isn't a valid IPv6 Address.

        """
        ikiwa sio ip_str:
            ashiria AddressValueError('Address cansio be empty')

        parts = ip_str.split(':')

        # An IPv6 address needs at least 2 colons (3 parts).
        _min_parts = 3
        ikiwa len(parts) < _min_parts:
            msg = "At least %d parts expected kwenye %r" % (_min_parts, ip_str)
            ashiria AddressValueError(msg)

        # If the address has an IPv4-style suffix, convert it to hexadecimal.
        ikiwa '.' kwenye parts[-1]:
            jaribu:
                ipv4_int = IPv4Address(parts.pop())._ip
            tatizo AddressValueError kama exc:
                ashiria AddressValueError("%s kwenye %r" % (exc, ip_str)) kutoka Tupu
            parts.append('%x' % ((ipv4_int >> 16) & 0xFFFF))
            parts.append('%x' % (ipv4_int & 0xFFFF))

        # An IPv6 address can't have more than 8 colons (9 parts).
        # The extra colon comes kutoka using the "::" notation kila a single
        # leading ama trailing zero part.
        _max_parts = cls._HEXTET_COUNT + 1
        ikiwa len(parts) > _max_parts:
            msg = "At most %d colons permitted kwenye %r" % (_max_parts-1, ip_str)
            ashiria AddressValueError(msg)

        # Disregarding the endpoints, find '::' ukijumuisha nothing kwenye between.
        # This indicates that a run of zeroes has been skipped.
        skip_index = Tupu
        kila i kwenye range(1, len(parts) - 1):
            ikiwa sio parts[i]:
                ikiwa skip_index ni sio Tupu:
                    # Can't have more than one '::'
                    msg = "At most one '::' permitted kwenye %r" % ip_str
                    ashiria AddressValueError(msg)
                skip_index = i

        # parts_hi ni the number of parts to copy kutoka above/before the '::'
        # parts_lo ni the number of parts to copy kutoka below/after the '::'
        ikiwa skip_index ni sio Tupu:
            # If we found a '::', then check ikiwa it also covers the endpoints.
            parts_hi = skip_index
            parts_lo = len(parts) - skip_index - 1
            ikiwa sio parts[0]:
                parts_hi -= 1
                ikiwa parts_hi:
                    msg = "Leading ':' only permitted kama part of '::' kwenye %r"
                    ashiria AddressValueError(msg % ip_str)  # ^: requires ^::
            ikiwa sio parts[-1]:
                parts_lo -= 1
                ikiwa parts_lo:
                    msg = "Trailing ':' only permitted kama part of '::' kwenye %r"
                    ashiria AddressValueError(msg % ip_str)  # :$ requires ::$
            parts_skipped = cls._HEXTET_COUNT - (parts_hi + parts_lo)
            ikiwa parts_skipped < 1:
                msg = "Expected at most %d other parts ukijumuisha '::' kwenye %r"
                ashiria AddressValueError(msg % (cls._HEXTET_COUNT-1, ip_str))
        isipokua:
            # Otherwise, allocate the entire address to parts_hi.  The
            # endpoints could still be empty, but _parse_hextet() will check
            # kila that.
            ikiwa len(parts) != cls._HEXTET_COUNT:
                msg = "Exactly %d parts expected without '::' kwenye %r"
                ashiria AddressValueError(msg % (cls._HEXTET_COUNT, ip_str))
            ikiwa sio parts[0]:
                msg = "Leading ':' only permitted kama part of '::' kwenye %r"
                ashiria AddressValueError(msg % ip_str)  # ^: requires ^::
            ikiwa sio parts[-1]:
                msg = "Trailing ':' only permitted kama part of '::' kwenye %r"
                ashiria AddressValueError(msg % ip_str)  # :$ requires ::$
            parts_hi = len(parts)
            parts_lo = 0
            parts_skipped = 0

        jaribu:
            # Now, parse the hextets into a 128-bit integer.
            ip_int = 0
            kila i kwenye range(parts_hi):
                ip_int <<= 16
                ip_int |= cls._parse_hextet(parts[i])
            ip_int <<= 16 * parts_skipped
            kila i kwenye range(-parts_lo, 0):
                ip_int <<= 16
                ip_int |= cls._parse_hextet(parts[i])
            rudisha ip_int
        tatizo ValueError kama exc:
            ashiria AddressValueError("%s kwenye %r" % (exc, ip_str)) kutoka Tupu

    @classmethod
    eleza _parse_hextet(cls, hextet_str):
        """Convert an IPv6 hextet string into an integer.

        Args:
            hextet_str: A string, the number to parse.

        Returns:
            The hextet kama an integer.

        Raises:
            ValueError: ikiwa the input isn't strictly a hex number from
              [0..FFFF].

        """
        # Whitelist the characters, since int() allows a lot of bizarre stuff.
        ikiwa sio cls._HEX_DIGITS.issuperset(hextet_str):
            ashiria ValueError("Only hex digits permitted kwenye %r" % hextet_str)
        # We do the length check second, since the invalid character error
        # ni likely to be more informative kila the user
        ikiwa len(hextet_str) > 4:
            msg = "At most 4 characters permitted kwenye %r"
            ashiria ValueError(msg % hextet_str)
        # Length check means we can skip checking the integer value
        rudisha int(hextet_str, 16)

    @classmethod
    eleza _compress_hextets(cls, hextets):
        """Compresses a list of hextets.

        Compresses a list of strings, replacing the longest continuous
        sequence of "0" kwenye the list ukijumuisha "" na adding empty strings at
        the beginning ama at the end of the string such that subsequently
        calling ":".join(hextets) will produce the compressed version of
        the IPv6 address.

        Args:
            hextets: A list of strings, the hextets to compress.

        Returns:
            A list of strings.

        """
        best_doublecolon_start = -1
        best_doublecolon_len = 0
        doublecolon_start = -1
        doublecolon_len = 0
        kila index, hextet kwenye enumerate(hextets):
            ikiwa hextet == '0':
                doublecolon_len += 1
                ikiwa doublecolon_start == -1:
                    # Start of a sequence of zeros.
                    doublecolon_start = index
                ikiwa doublecolon_len > best_doublecolon_len:
                    # This ni the longest sequence of zeros so far.
                    best_doublecolon_len = doublecolon_len
                    best_doublecolon_start = doublecolon_start
            isipokua:
                doublecolon_len = 0
                doublecolon_start = -1

        ikiwa best_doublecolon_len > 1:
            best_doublecolon_end = (best_doublecolon_start +
                                    best_doublecolon_len)
            # For zeros at the end of the address.
            ikiwa best_doublecolon_end == len(hextets):
                hextets += ['']
            hextets[best_doublecolon_start:best_doublecolon_end] = ['']
            # For zeros at the beginning of the address.
            ikiwa best_doublecolon_start == 0:
                hextets = [''] + hextets

        rudisha hextets

    @classmethod
    eleza _string_from_ip_int(cls, ip_int=Tupu):
        """Turns a 128-bit integer into hexadecimal notation.

        Args:
            ip_int: An integer, the IP address.

        Returns:
            A string, the hexadecimal representation of the address.

        Raises:
            ValueError: The address ni bigger than 128 bits of all ones.

        """
        ikiwa ip_int ni Tupu:
            ip_int = int(cls._ip)

        ikiwa ip_int > cls._ALL_ONES:
            ashiria ValueError('IPv6 address ni too large')

        hex_str = '%032x' % ip_int
        hextets = ['%x' % int(hex_str[x:x+4], 16) kila x kwenye range(0, 32, 4)]

        hextets = cls._compress_hextets(hextets)
        rudisha ':'.join(hextets)

    eleza _explode_shorthand_ip_string(self):
        """Expand a shortened IPv6 address.

        Args:
            ip_str: A string, the IPv6 address.

        Returns:
            A string, the expanded IPv6 address.

        """
        ikiwa isinstance(self, IPv6Network):
            ip_str = str(self.network_address)
        lasivyo isinstance(self, IPv6Interface):
            ip_str = str(self.ip)
        isipokua:
            ip_str = str(self)

        ip_int = self._ip_int_from_string(ip_str)
        hex_str = '%032x' % ip_int
        parts = [hex_str[x:x+4] kila x kwenye range(0, 32, 4)]
        ikiwa isinstance(self, (_BaseNetwork, IPv6Interface)):
            rudisha '%s/%d' % (':'.join(parts), self._prefixlen)
        rudisha ':'.join(parts)

    eleza _reverse_pointer(self):
        """Return the reverse DNS pointer name kila the IPv6 address.

        This implements the method described kwenye RFC3596 2.5.

        """
        reverse_chars = self.exploded[::-1].replace(':', '')
        rudisha '.'.join(reverse_chars) + '.ip6.arpa'

    @property
    eleza max_prefixlen(self):
        rudisha self._max_prefixlen

    @property
    eleza version(self):
        rudisha self._version


kundi IPv6Address(_BaseV6, _BaseAddress):

    """Represent na manipulate single IPv6 Addresses."""

    __slots__ = ('_ip', '__weakref__')

    eleza __init__(self, address):
        """Instantiate a new IPv6 address object.

        Args:
            address: A string ama integer representing the IP

              Additionally, an integer can be pitaed, so
              IPv6Address('2001:db8::') ==
                IPv6Address(42540766411282592856903984951653826560)
              or, more generally
              IPv6Address(int(IPv6Address('2001:db8::'))) ==
                IPv6Address('2001:db8::')

        Raises:
            AddressValueError: If address isn't a valid IPv6 address.

        """
        # Efficient constructor kutoka integer.
        ikiwa isinstance(address, int):
            self._check_int_address(address)
            self._ip = address
            rudisha

        # Constructing kutoka a packed address
        ikiwa isinstance(address, bytes):
            self._check_packed_address(address, 16)
            self._ip = int.from_bytes(address, 'big')
            rudisha

        # Assume input argument to be string ama any object representation
        # which converts into a formatted IP string.
        addr_str = str(address)
        ikiwa '/' kwenye addr_str:
            ashiria AddressValueError("Unexpected '/' kwenye %r" % address)
        self._ip = self._ip_int_from_string(addr_str)

    @property
    eleza packed(self):
        """The binary representation of this address."""
        rudisha v6_int_to_packed(self._ip)

    @property
    eleza is_multicast(self):
        """Test ikiwa the address ni reserved kila multicast use.

        Returns:
            A boolean, Kweli ikiwa the address ni a multicast address.
            See RFC 2373 2.7 kila details.

        """
        rudisha self kwenye self._constants._multicast_network

    @property
    eleza is_reserved(self):
        """Test ikiwa the address ni otherwise IETF reserved.

        Returns:
            A boolean, Kweli ikiwa the address ni within one of the
            reserved IPv6 Network ranges.

        """
        rudisha any(self kwenye x kila x kwenye self._constants._reserved_networks)

    @property
    eleza is_link_local(self):
        """Test ikiwa the address ni reserved kila link-local.

        Returns:
            A boolean, Kweli ikiwa the address ni reserved per RFC 4291.

        """
        rudisha self kwenye self._constants._linklocal_network

    @property
    eleza is_site_local(self):
        """Test ikiwa the address ni reserved kila site-local.

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test ikiwa this address ni kwenye the space of unique local
        addresses kama defined by RFC 4193.

        Returns:
            A boolean, Kweli ikiwa the address ni reserved per RFC 3513 2.5.6.

        """
        rudisha self kwenye self._constants._sitelocal_network

    @property
    @functools.lru_cache()
    eleza is_private(self):
        """Test ikiwa this address ni allocated kila private networks.

        Returns:
            A boolean, Kweli ikiwa the address ni reserved per
            iana-ipv6-special-registry.

        """
        rudisha any(self kwenye net kila net kwenye self._constants._private_networks)

    @property
    eleza is_global(self):
        """Test ikiwa this address ni allocated kila public networks.

        Returns:
            A boolean, true ikiwa the address ni sio reserved per
            iana-ipv6-special-registry.

        """
        rudisha sio self.is_private

    @property
    eleza is_unspecified(self):
        """Test ikiwa the address ni unspecified.

        Returns:
            A boolean, Kweli ikiwa this ni the unspecified address kama defined kwenye
            RFC 2373 2.5.2.

        """
        rudisha self._ip == 0

    @property
    eleza is_loopback(self):
        """Test ikiwa the address ni a loopback address.

        Returns:
            A boolean, Kweli ikiwa the address ni a loopback address kama defined kwenye
            RFC 2373 2.5.3.

        """
        rudisha self._ip == 1

    @property
    eleza ipv4_mapped(self):
        """Return the IPv4 mapped address.

        Returns:
            If the IPv6 address ni a v4 mapped address, rudisha the
            IPv4 mapped address. Return Tupu otherwise.

        """
        ikiwa (self._ip >> 32) != 0xFFFF:
            rudisha Tupu
        rudisha IPv4Address(self._ip & 0xFFFFFFFF)

    @property
    eleza teredo(self):
        """Tuple of embedded teredo IPs.

        Returns:
            Tuple of the (server, client) IPs ama Tupu ikiwa the address
            doesn't appear to be a teredo address (doesn't start with
            2001::/32)

        """
        ikiwa (self._ip >> 96) != 0x20010000:
            rudisha Tupu
        rudisha (IPv4Address((self._ip >> 64) & 0xFFFFFFFF),
                IPv4Address(~self._ip & 0xFFFFFFFF))

    @property
    eleza sixtofour(self):
        """Return the IPv4 6to4 embedded address.

        Returns:
            The IPv4 6to4-embedded address ikiwa present ama Tupu ikiwa the
            address doesn't appear to contain a 6to4 embedded address.

        """
        ikiwa (self._ip >> 112) != 0x2002:
            rudisha Tupu
        rudisha IPv4Address((self._ip >> 80) & 0xFFFFFFFF)


kundi IPv6Interface(IPv6Address):

    eleza __init__(self, address):
        addr, mask = self._split_addr_prefix(address)

        IPv6Address.__init__(self, addr)
        self.network = IPv6Network((addr, mask), strict=Uongo)
        self.netmask = self.network.netmask
        self._prefixlen = self.network._prefixlen

    @functools.cached_property
    eleza hostmask(self):
        rudisha self.network.hostmask

    eleza __str__(self):
        rudisha '%s/%d' % (self._string_from_ip_int(self._ip),
                          self._prefixlen)

    eleza __eq__(self, other):
        address_equal = IPv6Address.__eq__(self, other)
        ikiwa sio address_equal ama address_equal ni NotImplemented:
            rudisha address_equal
        jaribu:
            rudisha self.network == other.network
        tatizo AttributeError:
            # An interface ukijumuisha an associated network ni NOT the
            # same kama an unassociated address. That's why the hash
            # takes the extra info into account.
            rudisha Uongo

    eleza __lt__(self, other):
        address_less = IPv6Address.__lt__(self, other)
        ikiwa address_less ni NotImplemented:
            rudisha NotImplemented
        jaribu:
            rudisha (self.network < other.network ama
                    self.network == other.network na address_less)
        tatizo AttributeError:
            # We *do* allow addresses na interfaces to be sorted. The
            # unassociated address ni considered less than all interfaces.
            rudisha Uongo

    eleza __hash__(self):
        rudisha self._ip ^ self._prefixlen ^ int(self.network.network_address)

    __reduce__ = _IPAddressBase.__reduce__

    @property
    eleza ip(self):
        rudisha IPv6Address(self._ip)

    @property
    eleza with_prefixlen(self):
        rudisha '%s/%s' % (self._string_from_ip_int(self._ip),
                          self._prefixlen)

    @property
    eleza with_netmask(self):
        rudisha '%s/%s' % (self._string_from_ip_int(self._ip),
                          self.netmask)

    @property
    eleza with_hostmask(self):
        rudisha '%s/%s' % (self._string_from_ip_int(self._ip),
                          self.hostmask)

    @property
    eleza is_unspecified(self):
        rudisha self._ip == 0 na self.network.is_unspecified

    @property
    eleza is_loopback(self):
        rudisha self._ip == 1 na self.network.is_loopback


kundi IPv6Network(_BaseV6, _BaseNetwork):

    """This kundi represents na manipulates 128-bit IPv6 networks.

    Attributes: [examples kila IPv6('2001:db8::1000/124')]
        .network_address: IPv6Address('2001:db8::1000')
        .hostmask: IPv6Address('::f')
        .broadcast_address: IPv6Address('2001:db8::100f')
        .netmask: IPv6Address('ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0')
        .prefixlen: 124

    """

    # Class to use when creating address objects
    _address_class = IPv6Address

    eleza __init__(self, address, strict=Kweli):
        """Instantiate a new IPv6 Network object.

        Args:
            address: A string ama integer representing the IPv6 network ama the
              IP na prefix/netmask.
              '2001:db8::/128'
              '2001:db8:0000:0000:0000:0000:0000:0000/128'
              '2001:db8::'
              are all functionally the same kwenye IPv6.  That ni to say,
              failing to provide a subnetmask will create an object with
              a mask of /128.

              Additionally, an integer can be pitaed, so
              IPv6Network('2001:db8::') ==
                IPv6Network(42540766411282592856903984951653826560)
              or, more generally
              IPv6Network(int(IPv6Network('2001:db8::'))) ==
                IPv6Network('2001:db8::')

            strict: A boolean. If true, ensure that we have been pitaed
              A true network address, eg, 2001:db8::1000/124 na sio an
              IP address on a network, eg, 2001:db8::1/124.

        Raises:
            AddressValueError: If address isn't a valid IPv6 address.
            NetmaskValueError: If the netmask isn't valid for
              an IPv6 address.
            ValueError: If strict was Kweli na a network address was sio
              supplied.
        """
        addr, mask = self._split_addr_prefix(address)

        self.network_address = IPv6Address(addr)
        self.netmask, self._prefixlen = self._make_netmask(mask)
        packed = int(self.network_address)
        ikiwa packed & int(self.netmask) != packed:
            ikiwa strict:
                ashiria ValueError('%s has host bits set' % self)
            isipokua:
                self.network_address = IPv6Address(packed &
                                                   int(self.netmask))

        ikiwa self._prefixlen == (self._max_prefixlen - 1):
            self.hosts = self.__iter__

    eleza hosts(self):
        """Generate Iterator over usable hosts kwenye a network.

          This ni like __iter__ tatizo it doesn't rudisha the
          Subnet-Router anycast address.

        """
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        kila x kwenye range(network + 1, broadcast + 1):
            tuma self._address_class(x)

    @property
    eleza is_site_local(self):
        """Test ikiwa the address ni reserved kila site-local.

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test ikiwa this address ni kwenye the space of unique local
        addresses kama defined by RFC 4193.

        Returns:
            A boolean, Kweli ikiwa the address ni reserved per RFC 3513 2.5.6.

        """
        rudisha (self.network_address.is_site_local na
                self.broadcast_address.is_site_local)


kundi _IPv6Constants:

    _linklocal_network = IPv6Network('fe80::/10')

    _multicast_network = IPv6Network('ff00::/8')

    _private_networks = [
        IPv6Network('::1/128'),
        IPv6Network('::/128'),
        IPv6Network('::ffff:0:0/96'),
        IPv6Network('100::/64'),
        IPv6Network('2001::/23'),
        IPv6Network('2001:2::/48'),
        IPv6Network('2001:db8::/32'),
        IPv6Network('2001:10::/28'),
        IPv6Network('fc00::/7'),
        IPv6Network('fe80::/10'),
        ]

    _reserved_networks = [
        IPv6Network('::/8'), IPv6Network('100::/8'),
        IPv6Network('200::/7'), IPv6Network('400::/6'),
        IPv6Network('800::/5'), IPv6Network('1000::/4'),
        IPv6Network('4000::/3'), IPv6Network('6000::/3'),
        IPv6Network('8000::/3'), IPv6Network('A000::/3'),
        IPv6Network('C000::/3'), IPv6Network('E000::/4'),
        IPv6Network('F000::/5'), IPv6Network('F800::/6'),
        IPv6Network('FE00::/9'),
    ]

    _sitelocal_network = IPv6Network('fec0::/10')


IPv6Address._constants = _IPv6Constants
