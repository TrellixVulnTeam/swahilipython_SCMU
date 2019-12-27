# Copyright 2007 Google Inc.
#  Licensed to PSF under a Contributor Agreement.

"""A fast, lightweight IPv4/IPv6 manipulation library in Python.

This library is used to create/poke/manipulate IPv4 and IPv6 addresses
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
    """Take an IP string/int and rudisha an object of the correct type.

    Args:
        address: A string or integer, the IP address.  Either IPv4 or
          IPv6 addresses may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Address or IPv6Address object.

    Raises:
        ValueError: ikiwa the *address* passed isn't either a v4 or a v6
          address

    """
    try:
        rudisha IPv4Address(address)
    except (AddressValueError, NetmaskValueError):
        pass

    try:
        rudisha IPv6Address(address)
    except (AddressValueError, NetmaskValueError):
        pass

    raise ValueError('%r does not appear to be an IPv4 or IPv6 address' %
                     address)


eleza ip_network(address, strict=True):
    """Take an IP string/int and rudisha an object of the correct type.

    Args:
        address: A string or integer, the IP network.  Either IPv4 or
          IPv6 networks may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Network or IPv6Network object.

    Raises:
        ValueError: ikiwa the string passed isn't either a v4 or a v6
          address. Or ikiwa the network has host bits set.

    """
    try:
        rudisha IPv4Network(address, strict)
    except (AddressValueError, NetmaskValueError):
        pass

    try:
        rudisha IPv6Network(address, strict)
    except (AddressValueError, NetmaskValueError):
        pass

    raise ValueError('%r does not appear to be an IPv4 or IPv6 network' %
                     address)


eleza ip_interface(address):
    """Take an IP string/int and rudisha an object of the correct type.

    Args:
        address: A string or integer, the IP address.  Either IPv4 or
          IPv6 addresses may be supplied; integers less than 2**32 will
          be considered to be IPv4 by default.

    Returns:
        An IPv4Interface or IPv6Interface object.

    Raises:
        ValueError: ikiwa the string passed isn't either a v4 or a v6
          address.

    Notes:
        The IPv?Interface classes describe an Address on a particular
        Network, so they're basically a combination of both the Address
        and Network classes.

    """
    try:
        rudisha IPv4Interface(address)
    except (AddressValueError, NetmaskValueError):
        pass

    try:
        rudisha IPv6Interface(address)
    except (AddressValueError, NetmaskValueError):
        pass

    raise ValueError('%r does not appear to be an IPv4 or IPv6 interface' %
                     address)


eleza v4_int_to_packed(address):
    """Represent an address as 4 packed bytes in network (big-endian) order.

    Args:
        address: An integer representation of an IPv4 IP address.

    Returns:
        The integer address packed as 4 bytes in network (big-endian) order.

    Raises:
        ValueError: If the integer is negative or too large to be an
          IPv4 IP address.

    """
    try:
        rudisha address.to_bytes(4, 'big')
    except OverflowError:
        raise ValueError("Address negative or too large for IPv4")


eleza v6_int_to_packed(address):
    """Represent an address as 16 packed bytes in network (big-endian) order.

    Args:
        address: An integer representation of an IPv6 IP address.

    Returns:
        The integer address packed as 16 bytes in network (big-endian) order.

    """
    try:
        rudisha address.to_bytes(16, 'big')
    except OverflowError:
        raise ValueError("Address negative or too large for IPv6")


eleza _split_optional_netmask(address):
    """Helper to split the netmask and raise AddressValueError ikiwa needed"""
    addr = str(address).split('/')
    ikiwa len(addr) > 2:
        raise AddressValueError("Only one '/' permitted in %r" % address)
    rudisha addr


eleza _find_address_range(addresses):
    """Find a sequence of sorted deduplicated IPv#Address.

    Args:
        addresses: a list of IPv#Address objects.

    Yields:
        A tuple containing the first and last IP addresses in the sequence.

    """
    it = iter(addresses)
    first = last = next(it)
    for ip in it:
        ikiwa ip._ip != last._ip + 1:
            yield first, last
            first = ip
        last = ip
    yield first, last


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
    """Summarize a network range given the first and last IP addresses.

    Example:
        >>> list(summarize_address_range(IPv4Address('192.0.2.0'),
        ...                              IPv4Address('192.0.2.130')))
        ...                                #doctest: +NORMALIZE_WHITESPACE
        [IPv4Network('192.0.2.0/25'), IPv4Network('192.0.2.128/31'),
         IPv4Network('192.0.2.130/32')]

    Args:
        first: the first IPv4Address or IPv6Address in the range.
        last: the last IPv4Address or IPv6Address in the range.

    Returns:
        An iterator of the summarized IPv(4|6) network objects.

    Raise:
        TypeError:
            If the first and last objects are not IP addresses.
            If the first and last objects are not the same version.
        ValueError:
            If the last object is not greater than the first.
            If the version of the first address is not 4 or 6.

    """
    ikiwa (not (isinstance(first, _BaseAddress) and
             isinstance(last, _BaseAddress))):
        raise TypeError('first and last must be IP addresses, not networks')
    ikiwa first.version != last.version:
        raise TypeError("%s and %s are not of the same version" % (
                         first, last))
    ikiwa first > last:
        raise ValueError('last IP address must be greater than first')

    ikiwa first.version == 4:
        ip = IPv4Network
    elikiwa first.version == 6:
        ip = IPv6Network
    else:
        raise ValueError('unknown IP version')

    ip_bits = first._max_prefixlen
    first_int = first._ip
    last_int = last._ip
    while first_int <= last_int:
        nbits = min(_count_righthand_zero_bits(first_int, ip_bits),
                    (last_int - first_int + 1).bit_length() - 1)
        net = ip((first_int, ip_bits - nbits))
        yield net
        first_int += 1 << nbits
        ikiwa first_int - 1 == ip._ALL_ONES:
            break


eleza _collapse_addresses_internal(addresses):
    """Loops through the addresses, collapsing concurrent netblocks.

    Example:

        ip1 = IPv4Network('192.0.2.0/26')
        ip2 = IPv4Network('192.0.2.64/26')
        ip3 = IPv4Network('192.0.2.128/26')
        ip4 = IPv4Network('192.0.2.192/26')

        _collapse_addresses_internal([ip1, ip2, ip3, ip4]) ->
          [IPv4Network('192.0.2.0/24')]

        This shouldn't be called directly; it is called via
          collapse_addresses([]).

    Args:
        addresses: A list of IPv4Network's or IPv6Network's

    Returns:
        A list of IPv4Network's or IPv6Network's depending on what we were
        passed.

    """
    # First merge
    to_merge = list(addresses)
    subnets = {}
    while to_merge:
        net = to_merge.pop()
        supernet = net.supernet()
        existing = subnets.get(supernet)
        ikiwa existing is None:
            subnets[supernet] = net
        elikiwa existing != net:
            # Merge consecutive subnets
            del subnets[supernet]
            to_merge.append(supernet)
    # Then iterate over resulting networks, skipping subsumed subnets
    last = None
    for net in sorted(subnets.values()):
        ikiwa last is not None:
            # Since they are sorted, last.network_address <= net.network_address
            # is a given.
            ikiwa last.broadcast_address >= net.broadcast_address:
                continue
        yield net
        last = net


eleza collapse_addresses(addresses):
    """Collapse a list of IP objects.

    Example:
        collapse_addresses([IPv4Network('192.0.2.0/25'),
                            IPv4Network('192.0.2.128/25')]) ->
                           [IPv4Network('192.0.2.0/24')]

    Args:
        addresses: An iterator of IPv4Network or IPv6Network objects.

    Returns:
        An iterator of the collapsed IPv(4|6)Network objects.

    Raises:
        TypeError: If passed a list of mixed version objects.

    """
    addrs = []
    ips = []
    nets = []

    # split IP addresses and networks
    for ip in addresses:
        ikiwa isinstance(ip, _BaseAddress):
            ikiwa ips and ips[-1]._version != ip._version:
                raise TypeError("%s and %s are not of the same version" % (
                                 ip, ips[-1]))
            ips.append(ip)
        elikiwa ip._prefixlen == ip._max_prefixlen:
            ikiwa ips and ips[-1]._version != ip._version:
                raise TypeError("%s and %s are not of the same version" % (
                                 ip, ips[-1]))
            try:
                ips.append(ip.ip)
            except AttributeError:
                ips.append(ip.network_address)
        else:
            ikiwa nets and nets[-1]._version != ip._version:
                raise TypeError("%s and %s are not of the same version" % (
                                 ip, nets[-1]))
            nets.append(ip)

    # sort and dedup
    ips = sorted(set(ips))

    # find consecutive address ranges in the sorted sequence and summarize them
    ikiwa ips:
        for first, last in _find_address_range(ips):
            addrs.extend(summarize_address_range(first, last))

    rudisha _collapse_addresses_internal(addrs + nets)


eleza get_mixed_type_key(obj):
    """Return a key suitable for sorting between networks and addresses.

    Address and Network objects are not sortable by default; they're
    fundamentally different so the expression

        IPv4Address('192.0.2.0') <= IPv4Network('192.0.2.0/24')

    doesn't make any sense.  There are some times however, where you may wish
    to have ipaddress sort these for you anyway. If you need to do this, you
    can use this function as the key= argument to sorted().

    Args:
      obj: either a Network or Address object.
    Returns:
      appropriate key.

    """
    ikiwa isinstance(obj, _BaseNetwork):
        rudisha obj._get_networks_key()
    elikiwa isinstance(obj, _BaseAddress):
        rudisha obj._get_address_key()
    rudisha NotImplemented


kundi _IPAddressBase:

    """The mother class."""

    __slots__ = ()

    @property
    eleza exploded(self):
        """Return the longhand version of the IP address as a string."""
        rudisha self._explode_shorthand_ip_string()

    @property
    eleza compressed(self):
        """Return the shorthand version of the IP address as a string."""
        rudisha str(self)

    @property
    eleza reverse_pointer(self):
        """The name of the reverse DNS pointer for the IP address, e.g.:
            >>> ipaddress.ip_address("127.0.0.1").reverse_pointer
            '1.0.0.127.in-addr.arpa'
            >>> ipaddress.ip_address("2001:db8::1").reverse_pointer
            '1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'

        """
        rudisha self._reverse_pointer()

    @property
    eleza version(self):
        msg = '%200s has no version specified' % (type(self),)
        raise NotImplementedError(msg)

    eleza _check_int_address(self, address):
        ikiwa address < 0:
            msg = "%d (< 0) is not permitted as an IPv%d address"
            raise AddressValueError(msg % (address, self._version))
        ikiwa address > self._ALL_ONES:
            msg = "%d (>= 2**%d) is not permitted as an IPv%d address"
            raise AddressValueError(msg % (address, self._max_prefixlen,
                                           self._version))

    eleza _check_packed_address(self, address, expected_len):
        address_len = len(address)
        ikiwa address_len != expected_len:
            msg = "%r (len %d != %d) is not permitted as an IPv%d address"
            raise AddressValueError(msg % (address, address_len,
                                           expected_len, self._version))

    @classmethod
    eleza _ip_int_kutoka_prefix(cls, prefixlen):
        """Turn the prefix length into a bitwise netmask

        Args:
            prefixlen: An integer, the prefix length.

        Returns:
            An integer.

        """
        rudisha cls._ALL_ONES ^ (cls._ALL_ONES >> prefixlen)

    @classmethod
    eleza _prefix_kutoka_ip_int(cls, ip_int):
        """Return prefix length kutoka the bitwise netmask.

        Args:
            ip_int: An integer, the netmask in expanded bitwise format

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
            raise ValueError(msg % details)
        rudisha prefixlen

    @classmethod
    eleza _report_invalid_netmask(cls, netmask_str):
        msg = '%r is not a valid netmask' % netmask_str
        raise NetmaskValueError(msg) kutoka None

    @classmethod
    eleza _prefix_kutoka_prefix_string(cls, prefixlen_str):
        """Return prefix length kutoka a numeric string

        Args:
            prefixlen_str: The string to be converted

        Returns:
            An integer, the prefix length.

        Raises:
            NetmaskValueError: If the input is not a valid netmask
        """
        # int allows a leading +/- as well as surrounding whitespace,
        # so we ensure that isn't the case
        ikiwa not (prefixlen_str.isascii() and prefixlen_str.isdigit()):
            cls._report_invalid_netmask(prefixlen_str)
        try:
            prefixlen = int(prefixlen_str)
        except ValueError:
            cls._report_invalid_netmask(prefixlen_str)
        ikiwa not (0 <= prefixlen <= cls._max_prefixlen):
            cls._report_invalid_netmask(prefixlen_str)
        rudisha prefixlen

    @classmethod
    eleza _prefix_kutoka_ip_string(cls, ip_str):
        """Turn a netmask/hostmask string into a prefix length

        Args:
            ip_str: The netmask/hostmask to be converted

        Returns:
            An integer, the prefix length.

        Raises:
            NetmaskValueError: If the input is not a valid netmask/hostmask
        """
        # Parse the netmask/hostmask like an IP address.
        try:
            ip_int = cls._ip_int_kutoka_string(ip_str)
        except AddressValueError:
            cls._report_invalid_netmask(ip_str)

        # Try matching a netmask (this would be /1*0*/ as a bitwise regexp).
        # Note that the two ambiguous cases (all-ones and all-zeroes) are
        # treated as netmasks.
        try:
            rudisha cls._prefix_kutoka_ip_int(ip_int)
        except ValueError:
            pass

        # Invert the bits, and try matching a /0+1+/ hostmask instead.
        ip_int ^= cls._ALL_ONES
        try:
            rudisha cls._prefix_kutoka_ip_int(ip_int)
        except ValueError:
            cls._report_invalid_netmask(ip_str)

    @classmethod
    eleza _split_addr_prefix(cls, address):
        """Helper function to parse address of Network/Interface.

        Arg:
            address: Argument of Network/Interface.

        Returns:
            (addr, prefix) tuple.
        """
        # a packed address or integer
        ikiwa isinstance(address, (bytes, int)):
            rudisha address, cls._max_prefixlen

        ikiwa not isinstance(address, tuple):
            # Assume input argument to be string or any object representation
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
        try:
            rudisha (self._ip == other._ip
                    and self._version == other._version)
        except AttributeError:
            rudisha NotImplemented

    eleza __lt__(self, other):
        ikiwa not isinstance(other, _BaseAddress):
            rudisha NotImplemented
        ikiwa self._version != other._version:
            raise TypeError('%s and %s are not of the same version' % (
                             self, other))
        ikiwa self._ip != other._ip:
            rudisha self._ip < other._ip
        rudisha False

    # Shorthand for Integer addition and subtraction. This is not
    # meant to ever support addition/subtraction of addresses.
    eleza __add__(self, other):
        ikiwa not isinstance(other, int):
            rudisha NotImplemented
        rudisha self.__class__(int(self) + other)

    eleza __sub__(self, other):
        ikiwa not isinstance(other, int):
            rudisha NotImplemented
        rudisha self.__class__(int(self) - other)

    eleza __repr__(self):
        rudisha '%s(%r)' % (self.__class__.__name__, str(self))

    eleza __str__(self):
        rudisha str(self._string_kutoka_ip_int(self._ip))

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
        """Generate Iterator over usable hosts in a network.

        This is like __iter__ except it doesn't rudisha the network
        or broadcast addresses.

        """
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        for x in range(network + 1, broadcast):
            yield self._address_class(x)

    eleza __iter__(self):
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        for x in range(network, broadcast + 1):
            yield self._address_class(x)

    eleza __getitem__(self, n):
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        ikiwa n >= 0:
            ikiwa network + n > broadcast:
                raise IndexError('address out of range')
            rudisha self._address_class(network + n)
        else:
            n += 1
            ikiwa broadcast + n < network:
                raise IndexError('address out of range')
            rudisha self._address_class(broadcast + n)

    eleza __lt__(self, other):
        ikiwa not isinstance(other, _BaseNetwork):
            rudisha NotImplemented
        ikiwa self._version != other._version:
            raise TypeError('%s and %s are not of the same version' % (
                             self, other))
        ikiwa self.network_address != other.network_address:
            rudisha self.network_address < other.network_address
        ikiwa self.netmask != other.netmask:
            rudisha self.netmask < other.netmask
        rudisha False

    eleza __eq__(self, other):
        try:
            rudisha (self._version == other._version and
                    self.network_address == other.network_address and
                    int(self.netmask) == int(other.netmask))
        except AttributeError:
            rudisha NotImplemented

    eleza __hash__(self):
        rudisha hash(int(self.network_address) ^ int(self.netmask))

    eleza __contains__(self, other):
        # always false ikiwa one is v4 and the other is v6.
        ikiwa self._version != other._version:
            rudisha False
        # dealing with another network.
        ikiwa isinstance(other, _BaseNetwork):
            rudisha False
        # dealing with another address
        else:
            # address
            rudisha other._ip & self.netmask._ip == self.network_address._ip

    eleza overlaps(self, other):
        """Tell ikiwa self is partly contained in other."""
        rudisha self.network_address in other or (
            self.broadcast_address in other or (
                other.network_address in self or (
                    other.broadcast_address in self)))

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
        """Number of hosts in the current subnet."""
        rudisha int(self.broadcast_address) - int(self.network_address) + 1

    @property
    eleza _address_class(self):
        # Returning bare address objects (rather than interfaces) allows for
        # more consistent behaviour across the network address, broadcast
        # address and individual host addresses.
        msg = '%200s has no associated address class' % (type(self),)
        raise NotImplementedError(msg)

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

        or IPv6:

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
            other: An IPv4Network or IPv6Network object of the same type.

        Returns:
            An iterator of the IPv(4|6)Network objects which is self
            minus other.

        Raises:
            TypeError: If self and other are of differing address
              versions, or ikiwa other is not a network object.
            ValueError: If other is not completely contained by self.

        """
        ikiwa not self._version == other._version:
            raise TypeError("%s and %s are not of the same version" % (
                             self, other))

        ikiwa not isinstance(other, _BaseNetwork):
            raise TypeError("%s is not a network object" % other)

        ikiwa not other.subnet_of(self):
            raise ValueError('%s not contained in %s' % (other, self))
        ikiwa other == self:
            return

        # Make sure we're comparing the network of other.
        other = other.__class__('%s/%s' % (other.network_address,
                                           other.prefixlen))

        s1, s2 = self.subnets()
        while s1 != other and s2 != other:
            ikiwa other.subnet_of(s1):
                yield s2
                s1, s2 = s1.subnets()
            elikiwa other.subnet_of(s2):
                yield s1
                s1, s2 = s2.subnets()
            else:
                # If we got here, there's a bug somewhere.
                raise AssertionError('Error performing exclusion: '
                                     's1: %s s2: %s other: %s' %
                                     (s1, s2, other))
        ikiwa s1 == other:
            yield s2
        elikiwa s2 == other:
            yield s1
        else:
            # If we got here, there's a bug somewhere.
            raise AssertionError('Error performing exclusion: '
                                 's1: %s s2: %s other: %s' %
                                 (s1, s2, other))

    eleza compare_networks(self, other):
        """Compare two IP objects.

        This is only concerned about the comparison of the integer
        representation of the network addresses.  This means that the
        host bits aren't considered at all in this method.  If you want
        to compare host bits, you can easily enough do a
        'HostA._ip < HostB._ip'

        Args:
            other: An IP object.

        Returns:
            If the IP versions of self and other are the same, returns:

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
        # does this need to raise a ValueError?
        ikiwa self._version != other._version:
            raise TypeError('%s and %s are not of the same type' % (
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

        Returns an object that identifies this address' network and
        netmask. This function is a suitable "key" argument for sorted()
        and list.sort().

        """
        rudisha (self._version, self.network_address, self.netmask)

    eleza subnets(self, prefixlen_diff=1, new_prefix=None):
        """The subnets which join to make the current subnet.

        In the case that self contains only one IP
        (self._prefixlen == 32 for IPv4 or self._prefixlen == 128
        for IPv6), yield an iterator with just ourself.

        Args:
            prefixlen_diff: An integer, the amount the prefix length
              should be increased by. This should not be set if
              new_prefix is also set.
            new_prefix: The desired new prefix length. This must be a
              larger number (smaller prefix) than the existing prefix.
              This should not be set ikiwa prefixlen_diff is also set.

        Returns:
            An iterator of IPv(4|6) objects.

        Raises:
            ValueError: The prefixlen_diff is too small or too large.
                OR
            prefixlen_diff and new_prefix are both set or new_prefix
              is a smaller number than the current prefix (smaller
              number means a larger network)

        """
        ikiwa self._prefixlen == self._max_prefixlen:
            yield self
            return

        ikiwa new_prefix is not None:
            ikiwa new_prefix < self._prefixlen:
                raise ValueError('new prefix must be longer')
            ikiwa prefixlen_diff != 1:
                raise ValueError('cannot set prefixlen_diff and new_prefix')
            prefixlen_diff = new_prefix - self._prefixlen

        ikiwa prefixlen_diff < 0:
            raise ValueError('prefix length diff must be > 0')
        new_prefixlen = self._prefixlen + prefixlen_diff

        ikiwa new_prefixlen > self._max_prefixlen:
            raise ValueError(
                'prefix length diff %d is invalid for netblock %s' % (
                    new_prefixlen, self))

        start = int(self.network_address)
        end = int(self.broadcast_address) + 1
        step = (int(self.hostmask) + 1) >> prefixlen_diff
        for new_addr in range(start, end, step):
            current = self.__class__((new_addr, new_prefixlen))
            yield current

    eleza supernet(self, prefixlen_diff=1, new_prefix=None):
        """The supernet containing the current network.

        Args:
            prefixlen_diff: An integer, the amount the prefix length of
              the network should be decreased by.  For example, given a
              /24 network and a prefixlen_diff of 3, a supernet with a
              /21 netmask is returned.

        Returns:
            An IPv4 network object.

        Raises:
            ValueError: If self.prefixlen - prefixlen_diff < 0. I.e., you have
              a negative prefix length.
                OR
            If prefixlen_diff and new_prefix are both set or new_prefix is a
              larger number than the current prefix (larger number means a
              smaller network)

        """
        ikiwa self._prefixlen == 0:
            rudisha self

        ikiwa new_prefix is not None:
            ikiwa new_prefix > self._prefixlen:
                raise ValueError('new prefix must be shorter')
            ikiwa prefixlen_diff != 1:
                raise ValueError('cannot set prefixlen_diff and new_prefix')
            prefixlen_diff = self._prefixlen - new_prefix

        new_prefixlen = self.prefixlen - prefixlen_diff
        ikiwa new_prefixlen < 0:
            raise ValueError(
                'current prefixlen is %d, cannot have a prefixlen_diff of %d' %
                (self.prefixlen, prefixlen_diff))
        rudisha self.__class__((
            int(self.network_address) & (int(self.netmask) << prefixlen_diff),
            new_prefixlen
            ))

    @property
    eleza is_multicast(self):
        """Test ikiwa the address is reserved for multicast use.

        Returns:
            A boolean, True ikiwa the address is a multicast address.
            See RFC 2373 2.7 for details.

        """
        rudisha (self.network_address.is_multicast and
                self.broadcast_address.is_multicast)

    @staticmethod
    eleza _is_subnet_of(a, b):
        try:
            # Always false ikiwa one is v4 and the other is v6.
            ikiwa a._version != b._version:
                raise TypeError(f"{a} and {b} are not of the same version")
            rudisha (b.network_address <= a.network_address and
                    b.broadcast_address >= a.broadcast_address)
        except AttributeError:
            raise TypeError(f"Unable to test subnet containment "
                            f"between {a} and {b}")

    eleza subnet_of(self, other):
        """Return True ikiwa this network is a subnet of other."""
        rudisha self._is_subnet_of(self, other)

    eleza supernet_of(self, other):
        """Return True ikiwa this network is a supernet of other."""
        rudisha self._is_subnet_of(other, self)

    @property
    eleza is_reserved(self):
        """Test ikiwa the address is otherwise IETF reserved.

        Returns:
            A boolean, True ikiwa the address is within one of the
            reserved IPv6 Network ranges.

        """
        rudisha (self.network_address.is_reserved and
                self.broadcast_address.is_reserved)

    @property
    eleza is_link_local(self):
        """Test ikiwa the address is reserved for link-local.

        Returns:
            A boolean, True ikiwa the address is reserved per RFC 4291.

        """
        rudisha (self.network_address.is_link_local and
                self.broadcast_address.is_link_local)

    @property
    eleza is_private(self):
        """Test ikiwa this address is allocated for private networks.

        Returns:
            A boolean, True ikiwa the address is reserved per
            iana-ipv4-special-registry or iana-ipv6-special-registry.

        """
        rudisha (self.network_address.is_private and
                self.broadcast_address.is_private)

    @property
    eleza is_global(self):
        """Test ikiwa this address is allocated for public networks.

        Returns:
            A boolean, True ikiwa the address is not reserved per
            iana-ipv4-special-registry or iana-ipv6-special-registry.

        """
        rudisha not self.is_private

    @property
    eleza is_unspecified(self):
        """Test ikiwa the address is unspecified.

        Returns:
            A boolean, True ikiwa this is the unspecified address as defined in
            RFC 2373 2.5.2.

        """
        rudisha (self.network_address.is_unspecified and
                self.broadcast_address.is_unspecified)

    @property
    eleza is_loopback(self):
        """Test ikiwa the address is a loopback address.

        Returns:
            A boolean, True ikiwa the address is a loopback address as defined in
            RFC 2373 2.5.3.

        """
        rudisha (self.network_address.is_loopback and
                self.broadcast_address.is_loopback)


kundi _BaseV4:

    """Base IPv4 object.

    The following methods are used by IPv4 objects in both single IP
    addresses and networks.

    """

    __slots__ = ()
    _version = 4
    # Equivalent to 255.255.255.255 or 32 bits of 1's.
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
        ikiwa arg not in cls._netmask_cache:
            ikiwa isinstance(arg, int):
                prefixlen = arg
                ikiwa not (0 <= prefixlen <= cls._max_prefixlen):
                    cls._report_invalid_netmask(prefixlen)
            else:
                try:
                    # Check for a netmask in prefix length form
                    prefixlen = cls._prefix_kutoka_prefix_string(arg)
                except NetmaskValueError:
                    # Check for a netmask or hostmask in dotted-quad form.
                    # This may raise NetmaskValueError.
                    prefixlen = cls._prefix_kutoka_ip_string(arg)
            netmask = IPv4Address(cls._ip_int_kutoka_prefix(prefixlen))
            cls._netmask_cache[arg] = netmask, prefixlen
        rudisha cls._netmask_cache[arg]

    @classmethod
    eleza _ip_int_kutoka_string(cls, ip_str):
        """Turn the given IP string into an integer for comparison.

        Args:
            ip_str: A string, the IP ip_str.

        Returns:
            The IP ip_str as an integer.

        Raises:
            AddressValueError: ikiwa ip_str isn't a valid IPv4 Address.

        """
        ikiwa not ip_str:
            raise AddressValueError('Address cannot be empty')

        octets = ip_str.split('.')
        ikiwa len(octets) != 4:
            raise AddressValueError("Expected 4 octets in %r" % ip_str)

        try:
            rudisha int.kutoka_bytes(map(cls._parse_octet, octets), 'big')
        except ValueError as exc:
            raise AddressValueError("%s in %r" % (exc, ip_str)) kutoka None

    @classmethod
    eleza _parse_octet(cls, octet_str):
        """Convert a decimal octet into an integer.

        Args:
            octet_str: A string, the number to parse.

        Returns:
            The octet as an integer.

        Raises:
            ValueError: ikiwa the octet isn't strictly a decimal kutoka [0..255].

        """
        ikiwa not octet_str:
            raise ValueError("Empty octet not permitted")
        # Whitelist the characters, since int() allows a lot of bizarre stuff.
        ikiwa not (octet_str.isascii() and octet_str.isdigit()):
            msg = "Only decimal digits permitted in %r"
            raise ValueError(msg % octet_str)
        # We do the length check second, since the invalid character error
        # is likely to be more informative for the user
        ikiwa len(octet_str) > 3:
            msg = "At most 3 characters permitted in %r"
            raise ValueError(msg % octet_str)
        # Convert to integer (we know digits are legal)
        octet_int = int(octet_str, 10)
        ikiwa octet_int > 255:
            raise ValueError("Octet %d (> 255) not permitted" % octet_int)
        rudisha octet_int

    @classmethod
    eleza _string_kutoka_ip_int(cls, ip_int):
        """Turns a 32-bit integer into dotted decimal notation.

        Args:
            ip_int: An integer, the IP address.

        Returns:
            The IP address as a string in dotted decimal notation.

        """
        rudisha '.'.join(map(str, ip_int.to_bytes(4, 'big')))

    eleza _reverse_pointer(self):
        """Return the reverse DNS pointer name for the IPv4 address.

        This implements the method described in RFC1035 3.5.

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

    """Represent and manipulate single IPv4 Addresses."""

    __slots__ = ('_ip', '__weakref__')

    eleza __init__(self, address):

        """
        Args:
            address: A string or integer representing the IP

              Additionally, an integer can be passed, so
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
            return

        # Constructing kutoka a packed address
        ikiwa isinstance(address, bytes):
            self._check_packed_address(address, 4)
            self._ip = int.kutoka_bytes(address, 'big')
            return

        # Assume input argument to be string or any object representation
        # which converts into a formatted IP string.
        addr_str = str(address)
        ikiwa '/' in addr_str:
            raise AddressValueError("Unexpected '/' in %r" % address)
        self._ip = self._ip_int_kutoka_string(addr_str)

    @property
    eleza packed(self):
        """The binary representation of this address."""
        rudisha v4_int_to_packed(self._ip)

    @property
    eleza is_reserved(self):
        """Test ikiwa the address is otherwise IETF reserved.

         Returns:
             A boolean, True ikiwa the address is within the
             reserved IPv4 Network range.

        """
        rudisha self in self._constants._reserved_network

    @property
    @functools.lru_cache()
    eleza is_private(self):
        """Test ikiwa this address is allocated for private networks.

        Returns:
            A boolean, True ikiwa the address is reserved per
            iana-ipv4-special-registry.

        """
        rudisha any(self in net for net in self._constants._private_networks)

    @property
    @functools.lru_cache()
    eleza is_global(self):
        rudisha self not in self._constants._public_network and not self.is_private

    @property
    eleza is_multicast(self):
        """Test ikiwa the address is reserved for multicast use.

        Returns:
            A boolean, True ikiwa the address is multicast.
            See RFC 3171 for details.

        """
        rudisha self in self._constants._multicast_network

    @property
    eleza is_unspecified(self):
        """Test ikiwa the address is unspecified.

        Returns:
            A boolean, True ikiwa this is the unspecified address as defined in
            RFC 5735 3.

        """
        rudisha self == self._constants._unspecified_address

    @property
    eleza is_loopback(self):
        """Test ikiwa the address is a loopback address.

        Returns:
            A boolean, True ikiwa the address is a loopback per RFC 3330.

        """
        rudisha self in self._constants._loopback_network

    @property
    eleza is_link_local(self):
        """Test ikiwa the address is reserved for link-local.

        Returns:
            A boolean, True ikiwa the address is link-local per RFC 3927.

        """
        rudisha self in self._constants._linklocal_network


kundi IPv4Interface(IPv4Address):

    eleza __init__(self, address):
        addr, mask = self._split_addr_prefix(address)

        IPv4Address.__init__(self, addr)
        self.network = IPv4Network((addr, mask), strict=False)
        self.netmask = self.network.netmask
        self._prefixlen = self.network._prefixlen

    @functools.cached_property
    eleza hostmask(self):
        rudisha self.network.hostmask

    eleza __str__(self):
        rudisha '%s/%d' % (self._string_kutoka_ip_int(self._ip),
                          self._prefixlen)

    eleza __eq__(self, other):
        address_equal = IPv4Address.__eq__(self, other)
        ikiwa not address_equal or address_equal is NotImplemented:
            rudisha address_equal
        try:
            rudisha self.network == other.network
        except AttributeError:
            # An interface with an associated network is NOT the
            # same as an unassociated address. That's why the hash
            # takes the extra info into account.
            rudisha False

    eleza __lt__(self, other):
        address_less = IPv4Address.__lt__(self, other)
        ikiwa address_less is NotImplemented:
            rudisha NotImplemented
        try:
            rudisha (self.network < other.network or
                    self.network == other.network and address_less)
        except AttributeError:
            # We *do* allow addresses and interfaces to be sorted. The
            # unassociated address is considered less than all interfaces.
            rudisha False

    eleza __hash__(self):
        rudisha self._ip ^ self._prefixlen ^ int(self.network.network_address)

    __reduce__ = _IPAddressBase.__reduce__

    @property
    eleza ip(self):
        rudisha IPv4Address(self._ip)

    @property
    eleza with_prefixlen(self):
        rudisha '%s/%s' % (self._string_kutoka_ip_int(self._ip),
                          self._prefixlen)

    @property
    eleza with_netmask(self):
        rudisha '%s/%s' % (self._string_kutoka_ip_int(self._ip),
                          self.netmask)

    @property
    eleza with_hostmask(self):
        rudisha '%s/%s' % (self._string_kutoka_ip_int(self._ip),
                          self.hostmask)


kundi IPv4Network(_BaseV4, _BaseNetwork):

    """This kundi represents and manipulates 32-bit IPv4 network + addresses..

    Attributes: [examples for IPv4Network('192.0.2.0/27')]
        .network_address: IPv4Address('192.0.2.0')
        .hostmask: IPv4Address('0.0.0.31')
        .broadcast_address: IPv4Address('192.0.2.32')
        .netmask: IPv4Address('255.255.255.224')
        .prefixlen: 27

    """
    # Class to use when creating address objects
    _address_kundi = IPv4Address

    eleza __init__(self, address, strict=True):
        """Instantiate a new IPv4 network object.

        Args:
            address: A string or integer representing the IP [& network].
              '192.0.2.0/24'
              '192.0.2.0/255.255.255.0'
              '192.0.0.2/0.0.0.255'
              are all functionally the same in IPv4. Similarly,
              '192.0.2.1'
              '192.0.2.1/255.255.255.255'
              '192.0.2.1/32'
              are also functionally equivalent. That is to say, failing to
              provide a subnetmask will create an object with a mask of /32.

              If the mask (portion after the / in the argument) is given in
              dotted quad form, it is treated as a netmask ikiwa it starts with a
              non-zero field (e.g. /255.0.0.0 == /8) and as a hostmask ikiwa it
              starts with a zero field (e.g. 0.255.255.255 == /8), with the
              single exception of an all-zero mask which is treated as a
              netmask == /0. If no mask is given, a default of /32 is used.

              Additionally, an integer can be passed, so
              IPv4Network('192.0.2.1') == IPv4Network(3221225985)
              or, more generally
              IPv4Interface(int(IPv4Interface('192.0.2.1'))) ==
                IPv4Interface('192.0.2.1')

        Raises:
            AddressValueError: If ipaddress isn't a valid IPv4 address.
            NetmaskValueError: If the netmask isn't valid for
              an IPv4 address.
            ValueError: If strict is True and a network address is not
              supplied.
        """
        addr, mask = self._split_addr_prefix(address)

        self.network_address = IPv4Address(addr)
        self.netmask, self._prefixlen = self._make_netmask(mask)
        packed = int(self.network_address)
        ikiwa packed & int(self.netmask) != packed:
            ikiwa strict:
                raise ValueError('%s has host bits set' % self)
            else:
                self.network_address = IPv4Address(packed &
                                                   int(self.netmask))

        ikiwa self._prefixlen == (self._max_prefixlen - 1):
            self.hosts = self.__iter__

    @property
    @functools.lru_cache()
    eleza is_global(self):
        """Test ikiwa this address is allocated for public networks.

        Returns:
            A boolean, True ikiwa the address is not reserved per
            iana-ipv4-special-registry.

        """
        rudisha (not (self.network_address in IPv4Network('100.64.0.0/10') and
                    self.broadcast_address in IPv4Network('100.64.0.0/10')) and
                not self.is_private)


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

    The following methods are used by IPv6 objects in both single IP
    addresses and networks.

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
        ikiwa arg not in cls._netmask_cache:
            ikiwa isinstance(arg, int):
                prefixlen = arg
                ikiwa not (0 <= prefixlen <= cls._max_prefixlen):
                    cls._report_invalid_netmask(prefixlen)
            else:
                prefixlen = cls._prefix_kutoka_prefix_string(arg)
            netmask = IPv6Address(cls._ip_int_kutoka_prefix(prefixlen))
            cls._netmask_cache[arg] = netmask, prefixlen
        rudisha cls._netmask_cache[arg]

    @classmethod
    eleza _ip_int_kutoka_string(cls, ip_str):
        """Turn an IPv6 ip_str into an integer.

        Args:
            ip_str: A string, the IPv6 ip_str.

        Returns:
            An int, the IPv6 address

        Raises:
            AddressValueError: ikiwa ip_str isn't a valid IPv6 Address.

        """
        ikiwa not ip_str:
            raise AddressValueError('Address cannot be empty')

        parts = ip_str.split(':')

        # An IPv6 address needs at least 2 colons (3 parts).
        _min_parts = 3
        ikiwa len(parts) < _min_parts:
            msg = "At least %d parts expected in %r" % (_min_parts, ip_str)
            raise AddressValueError(msg)

        # If the address has an IPv4-style suffix, convert it to hexadecimal.
        ikiwa '.' in parts[-1]:
            try:
                ipv4_int = IPv4Address(parts.pop())._ip
            except AddressValueError as exc:
                raise AddressValueError("%s in %r" % (exc, ip_str)) kutoka None
            parts.append('%x' % ((ipv4_int >> 16) & 0xFFFF))
            parts.append('%x' % (ipv4_int & 0xFFFF))

        # An IPv6 address can't have more than 8 colons (9 parts).
        # The extra colon comes kutoka using the "::" notation for a single
        # leading or trailing zero part.
        _max_parts = cls._HEXTET_COUNT + 1
        ikiwa len(parts) > _max_parts:
            msg = "At most %d colons permitted in %r" % (_max_parts-1, ip_str)
            raise AddressValueError(msg)

        # Disregarding the endpoints, find '::' with nothing in between.
        # This indicates that a run of zeroes has been skipped.
        skip_index = None
        for i in range(1, len(parts) - 1):
            ikiwa not parts[i]:
                ikiwa skip_index is not None:
                    # Can't have more than one '::'
                    msg = "At most one '::' permitted in %r" % ip_str
                    raise AddressValueError(msg)
                skip_index = i

        # parts_hi is the number of parts to copy kutoka above/before the '::'
        # parts_lo is the number of parts to copy kutoka below/after the '::'
        ikiwa skip_index is not None:
            # If we found a '::', then check ikiwa it also covers the endpoints.
            parts_hi = skip_index
            parts_lo = len(parts) - skip_index - 1
            ikiwa not parts[0]:
                parts_hi -= 1
                ikiwa parts_hi:
                    msg = "Leading ':' only permitted as part of '::' in %r"
                    raise AddressValueError(msg % ip_str)  # ^: requires ^::
            ikiwa not parts[-1]:
                parts_lo -= 1
                ikiwa parts_lo:
                    msg = "Trailing ':' only permitted as part of '::' in %r"
                    raise AddressValueError(msg % ip_str)  # :$ requires ::$
            parts_skipped = cls._HEXTET_COUNT - (parts_hi + parts_lo)
            ikiwa parts_skipped < 1:
                msg = "Expected at most %d other parts with '::' in %r"
                raise AddressValueError(msg % (cls._HEXTET_COUNT-1, ip_str))
        else:
            # Otherwise, allocate the entire address to parts_hi.  The
            # endpoints could still be empty, but _parse_hextet() will check
            # for that.
            ikiwa len(parts) != cls._HEXTET_COUNT:
                msg = "Exactly %d parts expected without '::' in %r"
                raise AddressValueError(msg % (cls._HEXTET_COUNT, ip_str))
            ikiwa not parts[0]:
                msg = "Leading ':' only permitted as part of '::' in %r"
                raise AddressValueError(msg % ip_str)  # ^: requires ^::
            ikiwa not parts[-1]:
                msg = "Trailing ':' only permitted as part of '::' in %r"
                raise AddressValueError(msg % ip_str)  # :$ requires ::$
            parts_hi = len(parts)
            parts_lo = 0
            parts_skipped = 0

        try:
            # Now, parse the hextets into a 128-bit integer.
            ip_int = 0
            for i in range(parts_hi):
                ip_int <<= 16
                ip_int |= cls._parse_hextet(parts[i])
            ip_int <<= 16 * parts_skipped
            for i in range(-parts_lo, 0):
                ip_int <<= 16
                ip_int |= cls._parse_hextet(parts[i])
            rudisha ip_int
        except ValueError as exc:
            raise AddressValueError("%s in %r" % (exc, ip_str)) kutoka None

    @classmethod
    eleza _parse_hextet(cls, hextet_str):
        """Convert an IPv6 hextet string into an integer.

        Args:
            hextet_str: A string, the number to parse.

        Returns:
            The hextet as an integer.

        Raises:
            ValueError: ikiwa the input isn't strictly a hex number kutoka
              [0..FFFF].

        """
        # Whitelist the characters, since int() allows a lot of bizarre stuff.
        ikiwa not cls._HEX_DIGITS.issuperset(hextet_str):
            raise ValueError("Only hex digits permitted in %r" % hextet_str)
        # We do the length check second, since the invalid character error
        # is likely to be more informative for the user
        ikiwa len(hextet_str) > 4:
            msg = "At most 4 characters permitted in %r"
            raise ValueError(msg % hextet_str)
        # Length check means we can skip checking the integer value
        rudisha int(hextet_str, 16)

    @classmethod
    eleza _compress_hextets(cls, hextets):
        """Compresses a list of hextets.

        Compresses a list of strings, replacing the longest continuous
        sequence of "0" in the list with "" and adding empty strings at
        the beginning or at the end of the string such that subsequently
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
        for index, hextet in enumerate(hextets):
            ikiwa hextet == '0':
                doublecolon_len += 1
                ikiwa doublecolon_start == -1:
                    # Start of a sequence of zeros.
                    doublecolon_start = index
                ikiwa doublecolon_len > best_doublecolon_len:
                    # This is the longest sequence of zeros so far.
                    best_doublecolon_len = doublecolon_len
                    best_doublecolon_start = doublecolon_start
            else:
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
    eleza _string_kutoka_ip_int(cls, ip_int=None):
        """Turns a 128-bit integer into hexadecimal notation.

        Args:
            ip_int: An integer, the IP address.

        Returns:
            A string, the hexadecimal representation of the address.

        Raises:
            ValueError: The address is bigger than 128 bits of all ones.

        """
        ikiwa ip_int is None:
            ip_int = int(cls._ip)

        ikiwa ip_int > cls._ALL_ONES:
            raise ValueError('IPv6 address is too large')

        hex_str = '%032x' % ip_int
        hextets = ['%x' % int(hex_str[x:x+4], 16) for x in range(0, 32, 4)]

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
        elikiwa isinstance(self, IPv6Interface):
            ip_str = str(self.ip)
        else:
            ip_str = str(self)

        ip_int = self._ip_int_kutoka_string(ip_str)
        hex_str = '%032x' % ip_int
        parts = [hex_str[x:x+4] for x in range(0, 32, 4)]
        ikiwa isinstance(self, (_BaseNetwork, IPv6Interface)):
            rudisha '%s/%d' % (':'.join(parts), self._prefixlen)
        rudisha ':'.join(parts)

    eleza _reverse_pointer(self):
        """Return the reverse DNS pointer name for the IPv6 address.

        This implements the method described in RFC3596 2.5.

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

    """Represent and manipulate single IPv6 Addresses."""

    __slots__ = ('_ip', '__weakref__')

    eleza __init__(self, address):
        """Instantiate a new IPv6 address object.

        Args:
            address: A string or integer representing the IP

              Additionally, an integer can be passed, so
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
            return

        # Constructing kutoka a packed address
        ikiwa isinstance(address, bytes):
            self._check_packed_address(address, 16)
            self._ip = int.kutoka_bytes(address, 'big')
            return

        # Assume input argument to be string or any object representation
        # which converts into a formatted IP string.
        addr_str = str(address)
        ikiwa '/' in addr_str:
            raise AddressValueError("Unexpected '/' in %r" % address)
        self._ip = self._ip_int_kutoka_string(addr_str)

    @property
    eleza packed(self):
        """The binary representation of this address."""
        rudisha v6_int_to_packed(self._ip)

    @property
    eleza is_multicast(self):
        """Test ikiwa the address is reserved for multicast use.

        Returns:
            A boolean, True ikiwa the address is a multicast address.
            See RFC 2373 2.7 for details.

        """
        rudisha self in self._constants._multicast_network

    @property
    eleza is_reserved(self):
        """Test ikiwa the address is otherwise IETF reserved.

        Returns:
            A boolean, True ikiwa the address is within one of the
            reserved IPv6 Network ranges.

        """
        rudisha any(self in x for x in self._constants._reserved_networks)

    @property
    eleza is_link_local(self):
        """Test ikiwa the address is reserved for link-local.

        Returns:
            A boolean, True ikiwa the address is reserved per RFC 4291.

        """
        rudisha self in self._constants._linklocal_network

    @property
    eleza is_site_local(self):
        """Test ikiwa the address is reserved for site-local.

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test ikiwa this address is in the space of unique local
        addresses as defined by RFC 4193.

        Returns:
            A boolean, True ikiwa the address is reserved per RFC 3513 2.5.6.

        """
        rudisha self in self._constants._sitelocal_network

    @property
    @functools.lru_cache()
    eleza is_private(self):
        """Test ikiwa this address is allocated for private networks.

        Returns:
            A boolean, True ikiwa the address is reserved per
            iana-ipv6-special-registry.

        """
        rudisha any(self in net for net in self._constants._private_networks)

    @property
    eleza is_global(self):
        """Test ikiwa this address is allocated for public networks.

        Returns:
            A boolean, true ikiwa the address is not reserved per
            iana-ipv6-special-registry.

        """
        rudisha not self.is_private

    @property
    eleza is_unspecified(self):
        """Test ikiwa the address is unspecified.

        Returns:
            A boolean, True ikiwa this is the unspecified address as defined in
            RFC 2373 2.5.2.

        """
        rudisha self._ip == 0

    @property
    eleza is_loopback(self):
        """Test ikiwa the address is a loopback address.

        Returns:
            A boolean, True ikiwa the address is a loopback address as defined in
            RFC 2373 2.5.3.

        """
        rudisha self._ip == 1

    @property
    eleza ipv4_mapped(self):
        """Return the IPv4 mapped address.

        Returns:
            If the IPv6 address is a v4 mapped address, rudisha the
            IPv4 mapped address. Return None otherwise.

        """
        ikiwa (self._ip >> 32) != 0xFFFF:
            rudisha None
        rudisha IPv4Address(self._ip & 0xFFFFFFFF)

    @property
    eleza teredo(self):
        """Tuple of embedded teredo IPs.

        Returns:
            Tuple of the (server, client) IPs or None ikiwa the address
            doesn't appear to be a teredo address (doesn't start with
            2001::/32)

        """
        ikiwa (self._ip >> 96) != 0x20010000:
            rudisha None
        rudisha (IPv4Address((self._ip >> 64) & 0xFFFFFFFF),
                IPv4Address(~self._ip & 0xFFFFFFFF))

    @property
    eleza sixtofour(self):
        """Return the IPv4 6to4 embedded address.

        Returns:
            The IPv4 6to4-embedded address ikiwa present or None ikiwa the
            address doesn't appear to contain a 6to4 embedded address.

        """
        ikiwa (self._ip >> 112) != 0x2002:
            rudisha None
        rudisha IPv4Address((self._ip >> 80) & 0xFFFFFFFF)


kundi IPv6Interface(IPv6Address):

    eleza __init__(self, address):
        addr, mask = self._split_addr_prefix(address)

        IPv6Address.__init__(self, addr)
        self.network = IPv6Network((addr, mask), strict=False)
        self.netmask = self.network.netmask
        self._prefixlen = self.network._prefixlen

    @functools.cached_property
    eleza hostmask(self):
        rudisha self.network.hostmask

    eleza __str__(self):
        rudisha '%s/%d' % (self._string_kutoka_ip_int(self._ip),
                          self._prefixlen)

    eleza __eq__(self, other):
        address_equal = IPv6Address.__eq__(self, other)
        ikiwa not address_equal or address_equal is NotImplemented:
            rudisha address_equal
        try:
            rudisha self.network == other.network
        except AttributeError:
            # An interface with an associated network is NOT the
            # same as an unassociated address. That's why the hash
            # takes the extra info into account.
            rudisha False

    eleza __lt__(self, other):
        address_less = IPv6Address.__lt__(self, other)
        ikiwa address_less is NotImplemented:
            rudisha NotImplemented
        try:
            rudisha (self.network < other.network or
                    self.network == other.network and address_less)
        except AttributeError:
            # We *do* allow addresses and interfaces to be sorted. The
            # unassociated address is considered less than all interfaces.
            rudisha False

    eleza __hash__(self):
        rudisha self._ip ^ self._prefixlen ^ int(self.network.network_address)

    __reduce__ = _IPAddressBase.__reduce__

    @property
    eleza ip(self):
        rudisha IPv6Address(self._ip)

    @property
    eleza with_prefixlen(self):
        rudisha '%s/%s' % (self._string_kutoka_ip_int(self._ip),
                          self._prefixlen)

    @property
    eleza with_netmask(self):
        rudisha '%s/%s' % (self._string_kutoka_ip_int(self._ip),
                          self.netmask)

    @property
    eleza with_hostmask(self):
        rudisha '%s/%s' % (self._string_kutoka_ip_int(self._ip),
                          self.hostmask)

    @property
    eleza is_unspecified(self):
        rudisha self._ip == 0 and self.network.is_unspecified

    @property
    eleza is_loopback(self):
        rudisha self._ip == 1 and self.network.is_loopback


kundi IPv6Network(_BaseV6, _BaseNetwork):

    """This kundi represents and manipulates 128-bit IPv6 networks.

    Attributes: [examples for IPv6('2001:db8::1000/124')]
        .network_address: IPv6Address('2001:db8::1000')
        .hostmask: IPv6Address('::f')
        .broadcast_address: IPv6Address('2001:db8::100f')
        .netmask: IPv6Address('ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0')
        .prefixlen: 124

    """

    # Class to use when creating address objects
    _address_kundi = IPv6Address

    eleza __init__(self, address, strict=True):
        """Instantiate a new IPv6 Network object.

        Args:
            address: A string or integer representing the IPv6 network or the
              IP and prefix/netmask.
              '2001:db8::/128'
              '2001:db8:0000:0000:0000:0000:0000:0000/128'
              '2001:db8::'
              are all functionally the same in IPv6.  That is to say,
              failing to provide a subnetmask will create an object with
              a mask of /128.

              Additionally, an integer can be passed, so
              IPv6Network('2001:db8::') ==
                IPv6Network(42540766411282592856903984951653826560)
              or, more generally
              IPv6Network(int(IPv6Network('2001:db8::'))) ==
                IPv6Network('2001:db8::')

            strict: A boolean. If true, ensure that we have been passed
              A true network address, eg, 2001:db8::1000/124 and not an
              IP address on a network, eg, 2001:db8::1/124.

        Raises:
            AddressValueError: If address isn't a valid IPv6 address.
            NetmaskValueError: If the netmask isn't valid for
              an IPv6 address.
            ValueError: If strict was True and a network address was not
              supplied.
        """
        addr, mask = self._split_addr_prefix(address)

        self.network_address = IPv6Address(addr)
        self.netmask, self._prefixlen = self._make_netmask(mask)
        packed = int(self.network_address)
        ikiwa packed & int(self.netmask) != packed:
            ikiwa strict:
                raise ValueError('%s has host bits set' % self)
            else:
                self.network_address = IPv6Address(packed &
                                                   int(self.netmask))

        ikiwa self._prefixlen == (self._max_prefixlen - 1):
            self.hosts = self.__iter__

    eleza hosts(self):
        """Generate Iterator over usable hosts in a network.

          This is like __iter__ except it doesn't rudisha the
          Subnet-Router anycast address.

        """
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        for x in range(network + 1, broadcast + 1):
            yield self._address_class(x)

    @property
    eleza is_site_local(self):
        """Test ikiwa the address is reserved for site-local.

        Note that the site-local address space has been deprecated by RFC 3879.
        Use is_private to test ikiwa this address is in the space of unique local
        addresses as defined by RFC 4193.

        Returns:
            A boolean, True ikiwa the address is reserved per RFC 3513 2.5.6.

        """
        rudisha (self.network_address.is_site_local and
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
