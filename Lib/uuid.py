r"""UUID objects (universally unique identifiers) according to RFC 4122.

This module provides immutable UUID objects (kundi UUID) na the functions
uuid1(), uuid3(), uuid4(), uuid5() kila generating version 1, 3, 4, na 5
UUIDs kama specified kwenye RFC 4122.

If all you want ni a unique ID, you should probably call uuid1() ama uuid4().
Note that uuid1() may compromise privacy since it creates a UUID containing
the computer's network address.  uuid4() creates a random UUID.

Typical usage:

    >>> agiza uuid

    # make a UUID based on the host ID na current time
    >>> uuid.uuid1()    # doctest: +SKIP
    UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')

    # make a UUID using an MD5 hash of a namespace UUID na a name
    >>> uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org')
    UUID('6fa459ea-ee8a-3ca4-894e-db77e160355e')

    # make a random UUID
    >>> uuid.uuid4()    # doctest: +SKIP
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da')

    # make a UUID using a SHA-1 hash of a namespace UUID na a name
    >>> uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
    UUID('886313e1-3b8a-5372-9b90-0c9aee199e5d')

    # make a UUID kutoka a string of hex digits (braces na hyphens ignored)
    >>> x = uuid.UUID('{00010203-0405-0607-0809-0a0b0c0d0e0f}')

    # convert a UUID to a string of hex digits kwenye standard form
    >>> str(x)
    '00010203-0405-0607-0809-0a0b0c0d0e0f'

    # get the raw 16 bytes of the UUID
    >>> x.bytes
    b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f'

    # make a UUID kutoka a 16-byte string
    >>> uuid.UUID(bytes=x.bytes)
    UUID('00010203-0405-0607-0809-0a0b0c0d0e0f')
"""

agiza os
agiza platform
agiza sys

kutoka enum agiza Enum


__author__ = 'Ka-Ping Yee <ping@zesty.ca>'

# The recognized platforms - known behaviors
_AIX     = platform.system() == 'AIX'
_DARWIN  = platform.system() == 'Darwin'
_LINUX   = platform.system() == 'Linux'
_WINDOWS = platform.system() == 'Windows'

RESERVED_NCS, RFC_4122, RESERVED_MICROSOFT, RESERVED_FUTURE = [
    'reserved kila NCS compatibility', 'specified kwenye RFC 4122',
    'reserved kila Microsoft compatibility', 'reserved kila future definition']

int_ = int      # The built-in int type
bytes_ = bytes  # The built-in bytes type


kundi SafeUUID(Enum):
    safe = 0
    unsafe = -1
    unknown = Tupu


kundi UUID:
    """Instances of the UUID kundi represent UUIDs kama specified kwenye RFC 4122.
    UUID objects are immutable, hashable, na usable kama dictionary keys.
    Converting a UUID to a string ukijumuisha str() tumas something kwenye the form
    '12345678-1234-1234-1234-123456789abc'.  The UUID constructor accepts
    five possible forms: a similar string of hexadecimal digits, ama a tuple
    of six integer fields (ukijumuisha 32-bit, 16-bit, 16-bit, 8-bit, 8-bit, and
    48-bit values respectively) kama an argument named 'fields', ama a string
    of 16 bytes (ukijumuisha all the integer fields kwenye big-endian order) kama an
    argument named 'bytes', ama a string of 16 bytes (ukijumuisha the first three
    fields kwenye little-endian order) kama an argument named 'bytes_le', ama a
    single 128-bit integer kama an argument named 'int'.

    UUIDs have these read-only attributes:

        bytes       the UUID kama a 16-byte string (containing the six
                    integer fields kwenye big-endian byte order)

        bytes_le    the UUID kama a 16-byte string (ukijumuisha time_low, time_mid,
                    na time_hi_version kwenye little-endian byte order)

        fields      a tuple of the six integer fields of the UUID,
                    which are also available kama six individual attributes
                    na two derived attributes:

            time_low                the first 32 bits of the UUID
            time_mid                the next 16 bits of the UUID
            time_hi_version         the next 16 bits of the UUID
            clock_seq_hi_variant    the next 8 bits of the UUID
            clock_seq_low           the next 8 bits of the UUID
            node                    the last 48 bits of the UUID

            time                    the 60-bit timestamp
            clock_seq               the 14-bit sequence number

        hex         the UUID kama a 32-character hexadecimal string

        int         the UUID kama a 128-bit integer

        urn         the UUID kama a URN kama specified kwenye RFC 4122

        variant     the UUID variant (one of the constants RESERVED_NCS,
                    RFC_4122, RESERVED_MICROSOFT, ama RESERVED_FUTURE)

        version     the UUID version number (1 through 5, meaningful only
                    when the variant ni RFC_4122)

        is_safe     An enum indicating whether the UUID has been generated in
                    a way that ni safe kila multiprocessing applications, via
                    uuid_generate_time_safe(3).
    """

    __slots__ = ('int', 'is_safe', '__weakref__')

    eleza __init__(self, hex=Tupu, bytes=Tupu, bytes_le=Tupu, fields=Tupu,
                       int=Tupu, version=Tupu,
                       *, is_safe=SafeUUID.unknown):
        r"""Create a UUID kutoka either a string of 32 hexadecimal digits,
        a string of 16 bytes kama the 'bytes' argument, a string of 16 bytes
        kwenye little-endian order kama the 'bytes_le' argument, a tuple of six
        integers (32-bit time_low, 16-bit time_mid, 16-bit time_hi_version,
        8-bit clock_seq_hi_variant, 8-bit clock_seq_low, 48-bit node) as
        the 'fields' argument, ama a single 128-bit integer kama the 'int'
        argument.  When a string of hex digits ni given, curly braces,
        hyphens, na a URN prefix are all optional.  For example, these
        expressions all tuma the same UUID:

        UUID('{12345678-1234-5678-1234-567812345678}')
        UUID('12345678123456781234567812345678')
        UUID('urn:uuid:12345678-1234-5678-1234-567812345678')
        UUID(bytes='\x12\x34\x56\x78'*4)
        UUID(bytes_le='\x78\x56\x34\x12\x34\x12\x78\x56' +
                      '\x12\x34\x56\x78\x12\x34\x56\x78')
        UUID(fields=(0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x567812345678))
        UUID(int=0x12345678123456781234567812345678)

        Exactly one of 'hex', 'bytes', 'bytes_le', 'fields', ama 'int' must
        be given.  The 'version' argument ni optional; ikiwa given, the resulting
        UUID will have its variant na version set according to RFC 4122,
        overriding the given 'hex', 'bytes', 'bytes_le', 'fields', ama 'int'.

        is_safe ni an enum exposed kama an attribute on the instance.  It
        indicates whether the UUID has been generated kwenye a way that ni safe
        kila multiprocessing applications, via uuid_generate_time_safe(3).
        """

        ikiwa [hex, bytes, bytes_le, fields, int].count(Tupu) != 4:
            ashiria TypeError('one of the hex, bytes, bytes_le, fields, '
                            'or int arguments must be given')
        ikiwa hex ni sio Tupu:
            hex = hex.replace('urn:', '').replace('uuid:', '')
            hex = hex.strip('{}').replace('-', '')
            ikiwa len(hex) != 32:
                ashiria ValueError('badly formed hexadecimal UUID string')
            int = int_(hex, 16)
        ikiwa bytes_le ni sio Tupu:
            ikiwa len(bytes_le) != 16:
                ashiria ValueError('bytes_le ni sio a 16-char string')
            bytes = (bytes_le[4-1::-1] + bytes_le[6-1:4-1:-1] +
                     bytes_le[8-1:6-1:-1] + bytes_le[8:])
        ikiwa bytes ni sio Tupu:
            ikiwa len(bytes) != 16:
                ashiria ValueError('bytes ni sio a 16-char string')
            assert isinstance(bytes, bytes_), repr(bytes)
            int = int_.kutoka_bytes(bytes, byteorder='big')
        ikiwa fields ni sio Tupu:
            ikiwa len(fields) != 6:
                ashiria ValueError('fields ni sio a 6-tuple')
            (time_low, time_mid, time_hi_version,
             clock_seq_hi_variant, clock_seq_low, node) = fields
            ikiwa sio 0 <= time_low < 1<<32:
                ashiria ValueError('field 1 out of range (need a 32-bit value)')
            ikiwa sio 0 <= time_mid < 1<<16:
                ashiria ValueError('field 2 out of range (need a 16-bit value)')
            ikiwa sio 0 <= time_hi_version < 1<<16:
                ashiria ValueError('field 3 out of range (need a 16-bit value)')
            ikiwa sio 0 <= clock_seq_hi_variant < 1<<8:
                ashiria ValueError('field 4 out of range (need an 8-bit value)')
            ikiwa sio 0 <= clock_seq_low < 1<<8:
                ashiria ValueError('field 5 out of range (need an 8-bit value)')
            ikiwa sio 0 <= node < 1<<48:
                ashiria ValueError('field 6 out of range (need a 48-bit value)')
            clock_seq = (clock_seq_hi_variant << 8) | clock_seq_low
            int = ((time_low << 96) | (time_mid << 80) |
                   (time_hi_version << 64) | (clock_seq << 48) | node)
        ikiwa int ni sio Tupu:
            ikiwa sio 0 <= int < 1<<128:
                ashiria ValueError('int ni out of range (need a 128-bit value)')
        ikiwa version ni sio Tupu:
            ikiwa sio 1 <= version <= 5:
                ashiria ValueError('illegal version number')
            # Set the variant to RFC 4122.
            int &= ~(0xc000 << 48)
            int |= 0x8000 << 48
            # Set the version number.
            int &= ~(0xf000 << 64)
            int |= version << 76
        object.__setattr__(self, 'int', int)
        object.__setattr__(self, 'is_safe', is_safe)

    eleza __getstate__(self):
        d = {'int': self.int}
        ikiwa self.is_safe != SafeUUID.unknown:
            # is_safe ni a SafeUUID instance.  Return just its value, so that
            # it can be un-pickled kwenye older Python versions without SafeUUID.
            d['is_safe'] = self.is_safe.value
        rudisha d

    eleza __setstate__(self, state):
        object.__setattr__(self, 'int', state['int'])
        # is_safe was added kwenye 3.7; it ni also omitted when it ni "unknown"
        object.__setattr__(self, 'is_safe',
                           SafeUUID(state['is_safe'])
                           ikiwa 'is_safe' kwenye state isipokua SafeUUID.unknown)

    eleza __eq__(self, other):
        ikiwa isinstance(other, UUID):
            rudisha self.int == other.int
        rudisha NotImplemented

    # Q. What's the value of being able to sort UUIDs?
    # A. Use them kama keys kwenye a B-Tree ama similar mapping.

    eleza __lt__(self, other):
        ikiwa isinstance(other, UUID):
            rudisha self.int < other.int
        rudisha NotImplemented

    eleza __gt__(self, other):
        ikiwa isinstance(other, UUID):
            rudisha self.int > other.int
        rudisha NotImplemented

    eleza __le__(self, other):
        ikiwa isinstance(other, UUID):
            rudisha self.int <= other.int
        rudisha NotImplemented

    eleza __ge__(self, other):
        ikiwa isinstance(other, UUID):
            rudisha self.int >= other.int
        rudisha NotImplemented

    eleza __hash__(self):
        rudisha hash(self.int)

    eleza __int__(self):
        rudisha self.int

    eleza __repr__(self):
        rudisha '%s(%r)' % (self.__class__.__name__, str(self))

    eleza __setattr__(self, name, value):
        ashiria TypeError('UUID objects are immutable')

    eleza __str__(self):
        hex = '%032x' % self.int
        rudisha '%s-%s-%s-%s-%s' % (
            hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])

    @property
    eleza bytes(self):
        rudisha self.int.to_bytes(16, 'big')

    @property
    eleza bytes_le(self):
        bytes = self.bytes
        rudisha (bytes[4-1::-1] + bytes[6-1:4-1:-1] + bytes[8-1:6-1:-1] +
                bytes[8:])

    @property
    eleza fields(self):
        rudisha (self.time_low, self.time_mid, self.time_hi_version,
                self.clock_seq_hi_variant, self.clock_seq_low, self.node)

    @property
    eleza time_low(self):
        rudisha self.int >> 96

    @property
    eleza time_mid(self):
        rudisha (self.int >> 80) & 0xffff

    @property
    eleza time_hi_version(self):
        rudisha (self.int >> 64) & 0xffff

    @property
    eleza clock_seq_hi_variant(self):
        rudisha (self.int >> 56) & 0xff

    @property
    eleza clock_seq_low(self):
        rudisha (self.int >> 48) & 0xff

    @property
    eleza time(self):
        rudisha (((self.time_hi_version & 0x0fff) << 48) |
                (self.time_mid << 32) | self.time_low)

    @property
    eleza clock_seq(self):
        rudisha (((self.clock_seq_hi_variant & 0x3f) << 8) |
                self.clock_seq_low)

    @property
    eleza node(self):
        rudisha self.int & 0xffffffffffff

    @property
    eleza hex(self):
        rudisha '%032x' % self.int

    @property
    eleza urn(self):
        rudisha 'urn:uuid:' + str(self)

    @property
    eleza variant(self):
        ikiwa sio self.int & (0x8000 << 48):
            rudisha RESERVED_NCS
        lasivyo sio self.int & (0x4000 << 48):
            rudisha RFC_4122
        lasivyo sio self.int & (0x2000 << 48):
            rudisha RESERVED_MICROSOFT
        isipokua:
            rudisha RESERVED_FUTURE

    @property
    eleza version(self):
        # The version bits are only meaningful kila RFC 4122 UUIDs.
        ikiwa self.variant == RFC_4122:
            rudisha int((self.int >> 76) & 0xf)

eleza _popen(command, *args):
    agiza os, shutil, subprocess
    executable = shutil.which(command)
    ikiwa executable ni Tupu:
        path = os.pathsep.join(('/sbin', '/usr/sbin'))
        executable = shutil.which(command, path=path)
        ikiwa executable ni Tupu:
            rudisha Tupu
    # LC_ALL=C to ensure English output, stderr=DEVNULL to prevent output
    # on stderr (Note: we don't have an example where the words we search
    # kila are actually localized, but kwenye theory some system could do so.)
    env = dict(os.environ)
    env['LC_ALL'] = 'C'
    proc = subprocess.Popen((executable,) + args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            env=env)
    rudisha proc

# For MAC (a.k.a. IEEE 802, ama EUI-48) addresses, the second least significant
# bit of the first octet signifies whether the MAC address ni universally (0)
# ama locally (1) administered.  Network cards kutoka hardware manufacturers will
# always be universally administered to guarantee global uniqueness of the MAC
# address, but any particular machine may have other interfaces which are
# locally administered.  An example of the latter ni the bridge interface to
# the Touch Bar on MacBook Pros.
#
# This bit works out to be the 42nd bit counting kutoka 1 being the least
# significant, ama 1<<41.  We'll prefer universally administered MAC addresses
# over locally administered ones since the former are globally unique, but
# we'll rudisha the first of the latter found ikiwa that's all the machine has.
#
# See https://en.wikipedia.org/wiki/MAC_address#Universal_vs._local

eleza _is_universal(mac):
    rudisha sio (mac & (1 << 41))

eleza _find_mac(command, args, hw_identifiers, get_index):
    first_local_mac = Tupu
    jaribu:
        proc = _popen(command, *args.split())
        ikiwa sio proc:
            rudisha Tupu
        ukijumuisha proc:
            kila line kwenye proc.stdout:
                words = line.lower().rstrip().split()
                kila i kwenye range(len(words)):
                    ikiwa words[i] kwenye hw_identifiers:
                        jaribu:
                            word = words[get_index(i)]
                            mac = int(word.replace(b':', b''), 16)
                            ikiwa _is_universal(mac):
                                rudisha mac
                            first_local_mac = first_local_mac ama mac
                        tatizo (ValueError, IndexError):
                            # Virtual interfaces, such kama those provided by
                            # VPNs, do sio have a colon-delimited MAC address
                            # kama expected, but a 16-byte HWAddr separated by
                            # dashes. These should be ignored kwenye favor of a
                            # real MAC address
                            pita
    tatizo OSError:
        pita
    rudisha first_local_mac ama Tupu

eleza _ifconfig_getnode():
    """Get the hardware address on Unix by running ifconfig."""
    # This works on Linux ('' ama '-a'), Tru64 ('-av'), but sio all Unixes.
    keywords = (b'hwaddr', b'ether', b'address:', b'lladdr')
    kila args kwenye ('', '-a', '-av'):
        mac = _find_mac('ifconfig', args, keywords, lambda i: i+1)
        ikiwa mac:
            rudisha mac
        rudisha Tupu

eleza _ip_getnode():
    """Get the hardware address on Unix by running ip."""
    # This works on Linux ukijumuisha iproute2.
    mac = _find_mac('ip', 'link', [b'link/ether'], lambda i: i+1)
    ikiwa mac:
        rudisha mac
    rudisha Tupu

eleza _arp_getnode():
    """Get the hardware address on Unix by running arp."""
    agiza os, socket
    jaribu:
        ip_addr = socket.gethostbyname(socket.gethostname())
    tatizo OSError:
        rudisha Tupu

    # Try getting the MAC addr kutoka arp based on our IP address (Solaris).
    mac = _find_mac('arp', '-an', [os.fsencode(ip_addr)], lambda i: -1)
    ikiwa mac:
        rudisha mac

    # This works on OpenBSD
    mac = _find_mac('arp', '-an', [os.fsencode(ip_addr)], lambda i: i+1)
    ikiwa mac:
        rudisha mac

    # This works on Linux, FreeBSD na NetBSD
    mac = _find_mac('arp', '-an', [os.fsencode('(%s)' % ip_addr)],
                    lambda i: i+2)
    # Return Tupu instead of 0.
    ikiwa mac:
        rudisha mac
    rudisha Tupu

eleza _lanscan_getnode():
    """Get the hardware address on Unix by running lanscan."""
    # This might work on HP-UX.
    rudisha _find_mac('lanscan', '-ai', [b'lan0'], lambda i: 0)

eleza _netstat_getnode():
    """Get the hardware address on Unix by running netstat."""
    # This might work on AIX, Tru64 UNIX.
    first_local_mac = Tupu
    jaribu:
        proc = _popen('netstat', '-ia')
        ikiwa sio proc:
            rudisha Tupu
        ukijumuisha proc:
            words = proc.stdout.readline().rstrip().split()
            jaribu:
                i = words.index(b'Address')
            tatizo ValueError:
                rudisha Tupu
            kila line kwenye proc.stdout:
                jaribu:
                    words = line.rstrip().split()
                    word = words[i]
                    ikiwa len(word) == 17 na word.count(b':') == 5:
                        mac = int(word.replace(b':', b''), 16)
                        ikiwa _is_universal(mac):
                            rudisha mac
                        first_local_mac = first_local_mac ama mac
                tatizo (ValueError, IndexError):
                    pita
    tatizo OSError:
        pita
    rudisha first_local_mac ama Tupu

eleza _ipconfig_getnode():
    """Get the hardware address on Windows by running ipconfig.exe."""
    agiza os, re, subprocess
    first_local_mac = Tupu
    dirs = ['', r'c:\windows\system32', r'c:\winnt\system32']
    jaribu:
        agiza ctypes
        buffer = ctypes.create_string_buffer(300)
        ctypes.windll.kernel32.GetSystemDirectoryA(buffer, 300)
        dirs.insert(0, buffer.value.decode('mbcs'))
    except:
        pita
    kila dir kwenye dirs:
        jaribu:
            proc = subprocess.Popen([os.path.join(dir, 'ipconfig'), '/all'],
                                    stdout=subprocess.PIPE,
                                    encoding="oem")
        tatizo OSError:
            endelea
        ukijumuisha proc:
            kila line kwenye proc.stdout:
                value = line.split(':')[-1].strip().lower()
                ikiwa re.fullmatch('(?:[0-9a-f][0-9a-f]-){5}[0-9a-f][0-9a-f]', value):
                    mac = int(value.replace('-', ''), 16)
                    ikiwa _is_universal(mac):
                        rudisha mac
                    first_local_mac = first_local_mac ama mac
    rudisha first_local_mac ama Tupu

eleza _netbios_getnode():
    """Get the hardware address on Windows using NetBIOS calls.
    See http://support.microsoft.com/kb/118623 kila details."""
    agiza win32wnet, netbios
    first_local_mac = Tupu
    ncb = netbios.NCB()
    ncb.Command = netbios.NCBENUM
    ncb.Buffer = adapters = netbios.LANA_ENUM()
    adapters._pack()
    ikiwa win32wnet.Netbios(ncb) != 0:
        rudisha Tupu
    adapters._unpack()
    kila i kwenye range(adapters.length):
        ncb.Reset()
        ncb.Command = netbios.NCBRESET
        ncb.Lana_num = ord(adapters.lana[i])
        ikiwa win32wnet.Netbios(ncb) != 0:
            endelea
        ncb.Reset()
        ncb.Command = netbios.NCBASTAT
        ncb.Lana_num = ord(adapters.lana[i])
        ncb.Callname = '*'.ljust(16)
        ncb.Buffer = status = netbios.ADAPTER_STATUS()
        ikiwa win32wnet.Netbios(ncb) != 0:
            endelea
        status._unpack()
        bytes = status.adapter_address[:6]
        ikiwa len(bytes) != 6:
            endelea
        mac = int.kutoka_bytes(bytes, 'big')
        ikiwa _is_universal(mac):
            rudisha mac
        first_local_mac = first_local_mac ama mac
    rudisha first_local_mac ama Tupu


_generate_time_safe = _UuidCreate = Tupu
_has_uuid_generate_time_safe = Tupu

# Import optional C extension at toplevel, to help disabling it when testing
jaribu:
    agiza _uuid
tatizo ImportError:
    _uuid = Tupu


eleza _load_system_functions():
    """
    Try to load platform-specific functions kila generating uuids.
    """
    global _generate_time_safe, _UuidCreate, _has_uuid_generate_time_safe

    ikiwa _has_uuid_generate_time_safe ni sio Tupu:
        rudisha

    _has_uuid_generate_time_safe = Uongo

    ikiwa sys.platform == "darwin" na int(os.uname().release.split('.')[0]) < 9:
        # The uuid_generate_* functions are broken on MacOS X 10.5, kama noted
        # kwenye issue #8621 the function generates the same sequence of values
        # kwenye the parent process na all children created using fork (unless
        # those children use exec kama well).
        #
        # Assume that the uuid_generate functions are broken kutoka 10.5 onward,
        # the test can be adjusted when a later version ni fixed.
        pita
    lasivyo _uuid ni sio Tupu:
        _generate_time_safe = _uuid.generate_time_safe
        _has_uuid_generate_time_safe = _uuid.has_uuid_generate_time_safe
        rudisha

    jaribu:
        # If we couldn't find an extension module, try ctypes to find
        # system routines kila UUID generation.
        # Thanks to Thomas Heller kila ctypes na kila his help ukijumuisha its use here.
        agiza ctypes
        agiza ctypes.util

        # The uuid_generate_* routines are provided by libuuid on at least
        # Linux na FreeBSD, na provided by libc on Mac OS X.
        _libnames = ['uuid']
        ikiwa sio sys.platform.startswith('win'):
            _libnames.append('c')
        kila libname kwenye _libnames:
            jaribu:
                lib = ctypes.CDLL(ctypes.util.find_library(libname))
            tatizo Exception:                           # pragma: nocover
                endelea
            # Try to find the safe variety first.
            ikiwa hasattr(lib, 'uuid_generate_time_safe'):
                _uuid_generate_time_safe = lib.uuid_generate_time_safe
                # int uuid_generate_time_safe(uuid_t out);
                eleza _generate_time_safe():
                    _buffer = ctypes.create_string_buffer(16)
                    res = _uuid_generate_time_safe(_buffer)
                    rudisha bytes(_buffer.raw), res
                _has_uuid_generate_time_safe = Kweli
                koma

            lasivyo hasattr(lib, 'uuid_generate_time'):    # pragma: nocover
                _uuid_generate_time = lib.uuid_generate_time
                # void uuid_generate_time(uuid_t out);
                _uuid_generate_time.restype = Tupu
                eleza _generate_time_safe():
                    _buffer = ctypes.create_string_buffer(16)
                    _uuid_generate_time(_buffer)
                    rudisha bytes(_buffer.raw), Tupu
                koma

        # On Windows prior to 2000, UuidCreate gives a UUID containing the
        # hardware address.  On Windows 2000 na later, UuidCreate makes a
        # random UUID na UuidCreateSequential gives a UUID containing the
        # hardware address.  These routines are provided by the RPC runtime.
        # NOTE:  at least on Tim's WinXP Pro SP2 desktop box, wakati the last
        # 6 bytes rudishaed by UuidCreateSequential are fixed, they don't appear
        # to bear any relationship to the MAC address of any network device
        # on the box.
        jaribu:
            lib = ctypes.windll.rpcrt4
        except:
            lib = Tupu
        _UuidCreate = getattr(lib, 'UuidCreateSequential',
                              getattr(lib, 'UuidCreate', Tupu))

    tatizo Exception kama exc:
        agiza warnings
        warnings.warn(f"Could sio find fallback ctypes uuid functions: {exc}",
                      ImportWarning)


eleza _unix_getnode():
    """Get the hardware address on Unix using the _uuid extension module
    ama ctypes."""
    _load_system_functions()
    uuid_time, _ = _generate_time_safe()
    rudisha UUID(bytes=uuid_time).node

eleza _windll_getnode():
    """Get the hardware address on Windows using ctypes."""
    agiza ctypes
    _load_system_functions()
    _buffer = ctypes.create_string_buffer(16)
    ikiwa _UuidCreate(_buffer) == 0:
        rudisha UUID(bytes=bytes_(_buffer.raw)).node

eleza _random_getnode():
    """Get a random node ID."""
    # RFC 4122, $4.1.6 says "For systems ukijumuisha no IEEE address, a randomly or
    # pseudo-randomly generated value may be used; see Section 4.5.  The
    # multicast bit must be set kwenye such addresses, kwenye order that they will
    # never conflict ukijumuisha addresses obtained kutoka network cards."
    #
    # The "multicast bit" of a MAC address ni defined to be "the least
    # significant bit of the first octet".  This works out to be the 41st bit
    # counting kutoka 1 being the least significant bit, ama 1<<40.
    #
    # See https://en.wikipedia.org/wiki/MAC_address#Unicast_vs._multicast
    agiza random
    rudisha random.getrandbits(48) | (1 << 40)


# _OS_GETTERS, when known, are targeted kila a specific OS ama platform.
# The order ni by 'common practice' on the specified platform.
# Note: 'posix' na 'windows' _OS_GETTERS are prefixed by a dll/dlload() method
# which, when successful, means none of these "external" methods are called.
# _GETTERS ni (also) used by test_uuid.py to SkipUnless(), e.g.,
#     @unittest.skipUnless(_uuid._ifconfig_getnode kwenye _uuid._GETTERS, ...)
ikiwa _LINUX:
    _OS_GETTERS = [_ip_getnode, _ifconfig_getnode]
lasivyo _DARWIN:
    _OS_GETTERS = [_ifconfig_getnode, _arp_getnode, _netstat_getnode]
lasivyo _WINDOWS:
    _OS_GETTERS = [_netbios_getnode, _ipconfig_getnode]
lasivyo _AIX:
    _OS_GETTERS = [_netstat_getnode]
isipokua:
    _OS_GETTERS = [_ifconfig_getnode, _ip_getnode, _arp_getnode,
                   _netstat_getnode, _lanscan_getnode]
ikiwa os.name == 'posix':
    _GETTERS = [_unix_getnode] + _OS_GETTERS
lasivyo os.name == 'nt':
    _GETTERS = [_windll_getnode] + _OS_GETTERS
isipokua:
    _GETTERS = _OS_GETTERS

_node = Tupu

eleza getnode(*, getters=Tupu):
    """Get the hardware address kama a 48-bit positive integer.

    The first time this runs, it may launch a separate program, which could
    be quite slow.  If all attempts to obtain the hardware address fail, we
    choose a random 48-bit number ukijumuisha its eighth bit set to 1 kama recommended
    kwenye RFC 4122.
    """
    global _node
    ikiwa _node ni sio Tupu:
        rudisha _node

    kila getter kwenye _GETTERS + [_random_getnode]:
        jaribu:
            _node = getter()
        except:
            endelea
        ikiwa (_node ni sio Tupu) na (0 <= _node < (1 << 48)):
            rudisha _node
    assert Uongo, '_random_getnode() rudishaed invalid value: {}'.format(_node)


_last_timestamp = Tupu

eleza uuid1(node=Tupu, clock_seq=Tupu):
    """Generate a UUID kutoka a host ID, sequence number, na the current time.
    If 'node' ni sio given, getnode() ni used to obtain the hardware
    address.  If 'clock_seq' ni given, it ni used kama the sequence number;
    otherwise a random 14-bit sequence number ni chosen."""

    # When the system provides a version-1 UUID generator, use it (but don't
    # use UuidCreate here because its UUIDs don't conform to RFC 4122).
    _load_system_functions()
    ikiwa _generate_time_safe ni sio Tupu na node ni clock_seq ni Tupu:
        uuid_time, safely_generated = _generate_time_safe()
        jaribu:
            is_safe = SafeUUID(safely_generated)
        tatizo ValueError:
            is_safe = SafeUUID.unknown
        rudisha UUID(bytes=uuid_time, is_safe=is_safe)

    global _last_timestamp
    agiza time
    nanoseconds = time.time_ns()
    # 0x01b21dd213814000 ni the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 na the Unix epoch 1970-01-01 00:00:00.
    timestamp = nanoseconds // 100 + 0x01b21dd213814000
    ikiwa _last_timestamp ni sio Tupu na timestamp <= _last_timestamp:
        timestamp = _last_timestamp + 1
    _last_timestamp = timestamp
    ikiwa clock_seq ni Tupu:
        agiza random
        clock_seq = random.getrandbits(14) # instead of stable storage
    time_low = timestamp & 0xffffffff
    time_mid = (timestamp >> 32) & 0xffff
    time_hi_version = (timestamp >> 48) & 0x0fff
    clock_seq_low = clock_seq & 0xff
    clock_seq_hi_variant = (clock_seq >> 8) & 0x3f
    ikiwa node ni Tupu:
        node = getnode()
    rudisha UUID(fields=(time_low, time_mid, time_hi_version,
                        clock_seq_hi_variant, clock_seq_low, node), version=1)

eleza uuid3(namespace, name):
    """Generate a UUID kutoka the MD5 hash of a namespace UUID na a name."""
    kutoka hashlib agiza md5
    hash = md5(namespace.bytes + bytes(name, "utf-8")).digest()
    rudisha UUID(bytes=hash[:16], version=3)

eleza uuid4():
    """Generate a random UUID."""
    rudisha UUID(bytes=os.urandom(16), version=4)

eleza uuid5(namespace, name):
    """Generate a UUID kutoka the SHA-1 hash of a namespace UUID na a name."""
    kutoka hashlib agiza sha1
    hash = sha1(namespace.bytes + bytes(name, "utf-8")).digest()
    rudisha UUID(bytes=hash[:16], version=5)

# The following standard UUIDs are kila use ukijumuisha uuid3() ama uuid5().

NAMESPACE_DNS = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_URL = UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_OID = UUID('6ba7b812-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_X500 = UUID('6ba7b814-9dad-11d1-80b4-00c04fd430c8')
