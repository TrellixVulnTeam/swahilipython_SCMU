# Wrapper module for _ssl, providing some additional facilities
# implemented in Python.  Written by Bill Janssen.

"""This module provides some more Pythonic support for SSL.

Object types:

  SSLSocket -- subtype of socket.socket which does SSL over the socket

Exceptions:

  SSLError -- exception raised for I/O errors

Functions:

  cert_time_to_seconds -- convert time string used for certificate
                          notBefore and notAfter functions to integer
                          seconds past the Epoch (the time values
                          returned kutoka time.time())

  fetch_server_certificate (HOST, PORT) -- fetch the certificate provided
                          by the server running on HOST at port PORT.  No
                          validation of the certificate is performed.

Integer constants:

SSL_ERROR_ZERO_RETURN
SSL_ERROR_WANT_READ
SSL_ERROR_WANT_WRITE
SSL_ERROR_WANT_X509_LOOKUP
SSL_ERROR_SYSCALL
SSL_ERROR_SSL
SSL_ERROR_WANT_CONNECT

SSL_ERROR_EOF
SSL_ERROR_INVALID_ERROR_CODE

The following group define certificate requirements that one side is
allowing/requiring kutoka the other side:

CERT_NONE - no certificates kutoka the other side are required (or will
            be looked at ikiwa provided)
CERT_OPTIONAL - certificates are not required, but ikiwa provided will be
                validated, and ikiwa validation fails, the connection will
                also fail
CERT_REQUIRED - certificates are required, and will be validated, and
                ikiwa validation fails, the connection will also fail

The following constants identify various SSL protocol variants:

PROTOCOL_SSLv2
PROTOCOL_SSLv3
PROTOCOL_SSLv23
PROTOCOL_TLS
PROTOCOL_TLS_CLIENT
PROTOCOL_TLS_SERVER
PROTOCOL_TLSv1
PROTOCOL_TLSv1_1
PROTOCOL_TLSv1_2

The following constants identify various SSL alert message descriptions as per
http://www.iana.org/assignments/tls-parameters/tls-parameters.xml#tls-parameters-6

ALERT_DESCRIPTION_CLOSE_NOTIFY
ALERT_DESCRIPTION_UNEXPECTED_MESSAGE
ALERT_DESCRIPTION_BAD_RECORD_MAC
ALERT_DESCRIPTION_RECORD_OVERFLOW
ALERT_DESCRIPTION_DECOMPRESSION_FAILURE
ALERT_DESCRIPTION_HANDSHAKE_FAILURE
ALERT_DESCRIPTION_BAD_CERTIFICATE
ALERT_DESCRIPTION_UNSUPPORTED_CERTIFICATE
ALERT_DESCRIPTION_CERTIFICATE_REVOKED
ALERT_DESCRIPTION_CERTIFICATE_EXPIRED
ALERT_DESCRIPTION_CERTIFICATE_UNKNOWN
ALERT_DESCRIPTION_ILLEGAL_PARAMETER
ALERT_DESCRIPTION_UNKNOWN_CA
ALERT_DESCRIPTION_ACCESS_DENIED
ALERT_DESCRIPTION_DECODE_ERROR
ALERT_DESCRIPTION_DECRYPT_ERROR
ALERT_DESCRIPTION_PROTOCOL_VERSION
ALERT_DESCRIPTION_INSUFFICIENT_SECURITY
ALERT_DESCRIPTION_INTERNAL_ERROR
ALERT_DESCRIPTION_USER_CANCELLED
ALERT_DESCRIPTION_NO_RENEGOTIATION
ALERT_DESCRIPTION_UNSUPPORTED_EXTENSION
ALERT_DESCRIPTION_CERTIFICATE_UNOBTAINABLE
ALERT_DESCRIPTION_UNRECOGNIZED_NAME
ALERT_DESCRIPTION_BAD_CERTIFICATE_STATUS_RESPONSE
ALERT_DESCRIPTION_BAD_CERTIFICATE_HASH_VALUE
ALERT_DESCRIPTION_UNKNOWN_PSK_IDENTITY
"""

agiza sys
agiza os
kutoka collections agiza namedtuple
kutoka enum agiza Enum as _Enum, IntEnum as _IntEnum, IntFlag as _IntFlag

agiza _ssl             # ikiwa we can't agiza it, let the error propagate

kutoka _ssl agiza OPENSSL_VERSION_NUMBER, OPENSSL_VERSION_INFO, OPENSSL_VERSION
kutoka _ssl agiza _SSLContext, MemoryBIO, SSLSession
kutoka _ssl agiza (
    SSLError, SSLZeroReturnError, SSLWantReadError, SSLWantWriteError,
    SSLSyscallError, SSLEOFError, SSLCertVerificationError
    )
kutoka _ssl agiza txt2obj as _txt2obj, nid2obj as _nid2obj
kutoka _ssl agiza RAND_status, RAND_add, RAND_bytes, RAND_pseudo_bytes
try:
    kutoka _ssl agiza RAND_egd
except ImportError:
    # LibreSSL does not provide RAND_egd
    pass


kutoka _ssl agiza (
    HAS_SNI, HAS_ECDH, HAS_NPN, HAS_ALPN, HAS_SSLv2, HAS_SSLv3, HAS_TLSv1,
    HAS_TLSv1_1, HAS_TLSv1_2, HAS_TLSv1_3
)
kutoka _ssl agiza _DEFAULT_CIPHERS, _OPENSSL_API_VERSION


_IntEnum._convert_(
    '_SSLMethod', __name__,
    lambda name: name.startswith('PROTOCOL_') and name != 'PROTOCOL_SSLv23',
    source=_ssl)

_IntFlag._convert_(
    'Options', __name__,
    lambda name: name.startswith('OP_'),
    source=_ssl)

_IntEnum._convert_(
    'AlertDescription', __name__,
    lambda name: name.startswith('ALERT_DESCRIPTION_'),
    source=_ssl)

_IntEnum._convert_(
    'SSLErrorNumber', __name__,
    lambda name: name.startswith('SSL_ERROR_'),
    source=_ssl)

_IntFlag._convert_(
    'VerifyFlags', __name__,
    lambda name: name.startswith('VERIFY_'),
    source=_ssl)

_IntEnum._convert_(
    'VerifyMode', __name__,
    lambda name: name.startswith('CERT_'),
    source=_ssl)

PROTOCOL_SSLv23 = _SSLMethod.PROTOCOL_SSLv23 = _SSLMethod.PROTOCOL_TLS
_PROTOCOL_NAMES = {value: name for name, value in _SSLMethod.__members__.items()}

_SSLv2_IF_EXISTS = getattr(_SSLMethod, 'PROTOCOL_SSLv2', None)


kundi TLSVersion(_IntEnum):
    MINIMUM_SUPPORTED = _ssl.PROTO_MINIMUM_SUPPORTED
    SSLv3 = _ssl.PROTO_SSLv3
    TLSv1 = _ssl.PROTO_TLSv1
    TLSv1_1 = _ssl.PROTO_TLSv1_1
    TLSv1_2 = _ssl.PROTO_TLSv1_2
    TLSv1_3 = _ssl.PROTO_TLSv1_3
    MAXIMUM_SUPPORTED = _ssl.PROTO_MAXIMUM_SUPPORTED


kundi _TLSContentType(_IntEnum):
    """Content types (record layer)

    See RFC 8446, section B.1
    """
    CHANGE_CIPHER_SPEC = 20
    ALERT = 21
    HANDSHAKE = 22
    APPLICATION_DATA = 23
    # pseudo content types
    HEADER = 0x100
    INNER_CONTENT_TYPE = 0x101


kundi _TLSAlertType(_IntEnum):
    """Alert types for TLSContentType.ALERT messages

    See RFC 8466, section B.2
    """
    CLOSE_NOTIFY = 0
    UNEXPECTED_MESSAGE = 10
    BAD_RECORD_MAC = 20
    DECRYPTION_FAILED = 21
    RECORD_OVERFLOW = 22
    DECOMPRESSION_FAILURE = 30
    HANDSHAKE_FAILURE = 40
    NO_CERTIFICATE = 41
    BAD_CERTIFICATE = 42
    UNSUPPORTED_CERTIFICATE = 43
    CERTIFICATE_REVOKED = 44
    CERTIFICATE_EXPIRED = 45
    CERTIFICATE_UNKNOWN = 46
    ILLEGAL_PARAMETER = 47
    UNKNOWN_CA = 48
    ACCESS_DENIED = 49
    DECODE_ERROR = 50
    DECRYPT_ERROR = 51
    EXPORT_RESTRICTION = 60
    PROTOCOL_VERSION = 70
    INSUFFICIENT_SECURITY = 71
    INTERNAL_ERROR = 80
    INAPPROPRIATE_FALLBACK = 86
    USER_CANCELED = 90
    NO_RENEGOTIATION = 100
    MISSING_EXTENSION = 109
    UNSUPPORTED_EXTENSION = 110
    CERTIFICATE_UNOBTAINABLE = 111
    UNRECOGNIZED_NAME = 112
    BAD_CERTIFICATE_STATUS_RESPONSE = 113
    BAD_CERTIFICATE_HASH_VALUE = 114
    UNKNOWN_PSK_IDENTITY = 115
    CERTIFICATE_REQUIRED = 116
    NO_APPLICATION_PROTOCOL = 120


kundi _TLSMessageType(_IntEnum):
    """Message types (handshake protocol)

    See RFC 8446, section B.3
    """
    HELLO_REQUEST = 0
    CLIENT_HELLO = 1
    SERVER_HELLO = 2
    HELLO_VERIFY_REQUEST = 3
    NEWSESSION_TICKET = 4
    END_OF_EARLY_DATA = 5
    HELLO_RETRY_REQUEST = 6
    ENCRYPTED_EXTENSIONS = 8
    CERTIFICATE = 11
    SERVER_KEY_EXCHANGE = 12
    CERTIFICATE_REQUEST = 13
    SERVER_DONE = 14
    CERTIFICATE_VERIFY = 15
    CLIENT_KEY_EXCHANGE = 16
    FINISHED = 20
    CERTIFICATE_URL = 21
    CERTIFICATE_STATUS = 22
    SUPPLEMENTAL_DATA = 23
    KEY_UPDATE = 24
    NEXT_PROTO = 67
    MESSAGE_HASH = 254
    CHANGE_CIPHER_SPEC = 0x0101


ikiwa sys.platform == "win32":
    kutoka _ssl agiza enum_certificates, enum_crls

kutoka socket agiza socket, AF_INET, SOCK_STREAM, create_connection
kutoka socket agiza SOL_SOCKET, SO_TYPE
agiza socket as _socket
agiza base64        # for DER-to-PEM translation
agiza errno
agiza warnings


socket_error = OSError  # keep that public name in module namespace

CHANNEL_BINDING_TYPES = ['tls-unique']

HAS_NEVER_CHECK_COMMON_NAME = hasattr(_ssl, 'HOSTFLAG_NEVER_CHECK_SUBJECT')


_RESTRICTED_SERVER_CIPHERS = _DEFAULT_CIPHERS

CertificateError = SSLCertVerificationError


eleza _dnsname_match(dn, hostname):
    """Matching according to RFC 6125, section 6.4.3

    - Hostnames are compared lower case.
    - For IDNA, both dn and hostname must be encoded as IDN A-label (ACE).
    - Partial wildcards like 'www*.example.org', multiple wildcards, sole
      wildcard or wildcards in labels other then the left-most label are not
      supported and a CertificateError is raised.
    - A wildcard must match at least one character.
    """
    ikiwa not dn:
        rudisha False

    wildcards = dn.count('*')
    # speed up common case w/o wildcards
    ikiwa not wildcards:
        rudisha dn.lower() == hostname.lower()

    ikiwa wildcards > 1:
        raise CertificateError(
            "too many wildcards in certificate DNS name: {!r}.".format(dn))

    dn_leftmost, sep, dn_remainder = dn.partition('.')

    ikiwa '*' in dn_remainder:
        # Only match wildcard in leftmost segment.
        raise CertificateError(
            "wildcard can only be present in the leftmost label: "
            "{!r}.".format(dn))

    ikiwa not sep:
        # no right side
        raise CertificateError(
            "sole wildcard without additional labels are not support: "
            "{!r}.".format(dn))

    ikiwa dn_leftmost != '*':
        # no partial wildcard matching
        raise CertificateError(
            "partial wildcards in leftmost label are not supported: "
            "{!r}.".format(dn))

    hostname_leftmost, sep, hostname_remainder = hostname.partition('.')
    ikiwa not hostname_leftmost or not sep:
        # wildcard must match at least one char
        rudisha False
    rudisha dn_remainder.lower() == hostname_remainder.lower()


eleza _inet_paton(ipname):
    """Try to convert an IP address to packed binary form

    Supports IPv4 addresses on all platforms and IPv6 on platforms with IPv6
    support.
    """
    # inet_aton() also accepts strings like '1', '127.1', some also trailing
    # data like '127.0.0.1 whatever'.
    try:
        addr = _socket.inet_aton(ipname)
    except OSError:
        # not an IPv4 address
        pass
    else:
        ikiwa _socket.inet_ntoa(addr) == ipname:
            # only accept injective ipnames
            rudisha addr
        else:
            # refuse for short IPv4 notation and additional trailing data
            raise ValueError(
                "{!r} is not a quad-dotted IPv4 address.".format(ipname)
            )

    try:
        rudisha _socket.inet_pton(_socket.AF_INET6, ipname)
    except OSError:
        raise ValueError("{!r} is neither an IPv4 nor an IP6 "
                         "address.".format(ipname))
    except AttributeError:
        # AF_INET6 not available
        pass

    raise ValueError("{!r} is not an IPv4 address.".format(ipname))


eleza _ipaddress_match(cert_ipaddress, host_ip):
    """Exact matching of IP addresses.

    RFC 6125 explicitly doesn't define an algorithm for this
    (section 1.7.2 - "Out of Scope").
    """
    # OpenSSL may add a trailing newline to a subjectAltName's IP address,
    # commonly woth IPv6 addresses. Strip off trailing \n.
    ip = _inet_paton(cert_ipaddress.rstrip())
    rudisha ip == host_ip


eleza match_hostname(cert, hostname):
    """Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 and RFC 6125
    rules are followed.

    The function matches IP addresses rather than dNSNames ikiwa hostname is a
    valid ipaddress string. IPv4 addresses are supported on all platforms.
    IPv6 addresses are supported on platforms with IPv6 support (AF_INET6
    and inet_pton).

    CertificateError is raised on failure. On success, the function
    returns nothing.
    """
    ikiwa not cert:
        raise ValueError("empty or no certificate, match_hostname needs a "
                         "SSL socket or SSL context with either "
                         "CERT_OPTIONAL or CERT_REQUIRED")
    try:
        host_ip = _inet_paton(hostname)
    except ValueError:
        # Not an IP address (common case)
        host_ip = None
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        ikiwa key == 'DNS':
            ikiwa host_ip is None and _dnsname_match(value, hostname):
                return
            dnsnames.append(value)
        elikiwa key == 'IP Address':
            ikiwa host_ip is not None and _ipaddress_match(value, host_ip):
                return
            dnsnames.append(value)
    ikiwa not dnsnames:
        # The subject is only checked when there is no dNSName entry
        # in subjectAltName
        for sub in cert.get('subject', ()):
            for key, value in sub:
                # XXX according to RFC 2818, the most specific Common Name
                # must be used.
                ikiwa key == 'commonName':
                    ikiwa _dnsname_match(value, hostname):
                        return
                    dnsnames.append(value)
    ikiwa len(dnsnames) > 1:
        raise CertificateError("hostname %r "
            "doesn't match either of %s"
            % (hostname, ', '.join(map(repr, dnsnames))))
    elikiwa len(dnsnames) == 1:
        raise CertificateError("hostname %r "
            "doesn't match %r"
            % (hostname, dnsnames[0]))
    else:
        raise CertificateError("no appropriate commonName or "
            "subjectAltName fields were found")


DefaultVerifyPaths = namedtuple("DefaultVerifyPaths",
    "cafile capath openssl_cafile_env openssl_cafile openssl_capath_env "
    "openssl_capath")

eleza get_default_verify_paths():
    """Return paths to default cafile and capath.
    """
    parts = _ssl.get_default_verify_paths()

    # environment vars shadow paths
    cafile = os.environ.get(parts[0], parts[1])
    capath = os.environ.get(parts[2], parts[3])

    rudisha DefaultVerifyPaths(cafile ikiwa os.path.isfile(cafile) else None,
                              capath ikiwa os.path.isdir(capath) else None,
                              *parts)


kundi _ASN1Object(namedtuple("_ASN1Object", "nid shortname longname oid")):
    """ASN.1 object identifier lookup
    """
    __slots__ = ()

    eleza __new__(cls, oid):
        rudisha super().__new__(cls, *_txt2obj(oid, name=False))

    @classmethod
    eleza kutokanid(cls, nid):
        """Create _ASN1Object kutoka OpenSSL numeric ID
        """
        rudisha super().__new__(cls, *_nid2obj(nid))

    @classmethod
    eleza kutokaname(cls, name):
        """Create _ASN1Object kutoka short name, long name or OID
        """
        rudisha super().__new__(cls, *_txt2obj(name, name=True))


kundi Purpose(_ASN1Object, _Enum):
    """SSLContext purpose flags with X509v3 Extended Key Usage objects
    """
    SERVER_AUTH = '1.3.6.1.5.5.7.3.1'
    CLIENT_AUTH = '1.3.6.1.5.5.7.3.2'


kundi SSLContext(_SSLContext):
    """An SSLContext holds various SSL-related configuration options and
    data, such as certificates and possibly a private key."""
    _windows_cert_stores = ("CA", "ROOT")

    sslsocket_kundi = None  # SSLSocket is assigned later.
    sslobject_kundi = None  # SSLObject is assigned later.

    eleza __new__(cls, protocol=PROTOCOL_TLS, *args, **kwargs):
        self = _SSLContext.__new__(cls, protocol)
        rudisha self

    eleza _encode_hostname(self, hostname):
        ikiwa hostname is None:
            rudisha None
        elikiwa isinstance(hostname, str):
            rudisha hostname.encode('idna').decode('ascii')
        else:
            rudisha hostname.decode('ascii')

    eleza wrap_socket(self, sock, server_side=False,
                    do_handshake_on_connect=True,
                    suppress_ragged_eofs=True,
                    server_hostname=None, session=None):
        # SSLSocket kundi handles server_hostname encoding before it calls
        # ctx._wrap_socket()
        rudisha self.sslsocket_class._create(
            sock=sock,
            server_side=server_side,
            do_handshake_on_connect=do_handshake_on_connect,
            suppress_ragged_eofs=suppress_ragged_eofs,
            server_hostname=server_hostname,
            context=self,
            session=session
        )

    eleza wrap_bio(self, incoming, outgoing, server_side=False,
                 server_hostname=None, session=None):
        # Need to encode server_hostname here because _wrap_bio() can only
        # handle ASCII str.
        rudisha self.sslobject_class._create(
            incoming, outgoing, server_side=server_side,
            server_hostname=self._encode_hostname(server_hostname),
            session=session, context=self,
        )

    eleza set_npn_protocols(self, npn_protocols):
        protos = bytearray()
        for protocol in npn_protocols:
            b = bytes(protocol, 'ascii')
            ikiwa len(b) == 0 or len(b) > 255:
                raise SSLError('NPN protocols must be 1 to 255 in length')
            protos.append(len(b))
            protos.extend(b)

        self._set_npn_protocols(protos)

    eleza set_servername_callback(self, server_name_callback):
        ikiwa server_name_callback is None:
            self.sni_callback = None
        else:
            ikiwa not callable(server_name_callback):
                raise TypeError("not a callable object")

            eleza shim_cb(sslobj, servername, sslctx):
                servername = self._encode_hostname(servername)
                rudisha server_name_callback(sslobj, servername, sslctx)

            self.sni_callback = shim_cb

    eleza set_alpn_protocols(self, alpn_protocols):
        protos = bytearray()
        for protocol in alpn_protocols:
            b = bytes(protocol, 'ascii')
            ikiwa len(b) == 0 or len(b) > 255:
                raise SSLError('ALPN protocols must be 1 to 255 in length')
            protos.append(len(b))
            protos.extend(b)

        self._set_alpn_protocols(protos)

    eleza _load_windows_store_certs(self, storename, purpose):
        certs = bytearray()
        try:
            for cert, encoding, trust in enum_certificates(storename):
                # CA certs are never PKCS#7 encoded
                ikiwa encoding == "x509_asn":
                    ikiwa trust is True or purpose.oid in trust:
                        certs.extend(cert)
        except PermissionError:
            warnings.warn("unable to enumerate Windows certificate store")
        ikiwa certs:
            self.load_verify_locations(cadata=certs)
        rudisha certs

    eleza load_default_certs(self, purpose=Purpose.SERVER_AUTH):
        ikiwa not isinstance(purpose, _ASN1Object):
            raise TypeError(purpose)
        ikiwa sys.platform == "win32":
            for storename in self._windows_cert_stores:
                self._load_windows_store_certs(storename, purpose)
        self.set_default_verify_paths()

    ikiwa hasattr(_SSLContext, 'minimum_version'):
        @property
        eleza minimum_version(self):
            rudisha TLSVersion(super().minimum_version)

        @minimum_version.setter
        eleza minimum_version(self, value):
            ikiwa value == TLSVersion.SSLv3:
                self.options &= ~Options.OP_NO_SSLv3
            super(SSLContext, SSLContext).minimum_version.__set__(self, value)

        @property
        eleza maximum_version(self):
            rudisha TLSVersion(super().maximum_version)

        @maximum_version.setter
        eleza maximum_version(self, value):
            super(SSLContext, SSLContext).maximum_version.__set__(self, value)

    @property
    eleza options(self):
        rudisha Options(super().options)

    @options.setter
    eleza options(self, value):
        super(SSLContext, SSLContext).options.__set__(self, value)

    ikiwa hasattr(_ssl, 'HOSTFLAG_NEVER_CHECK_SUBJECT'):
        @property
        eleza hostname_checks_common_name(self):
            ncs = self._host_flags & _ssl.HOSTFLAG_NEVER_CHECK_SUBJECT
            rudisha ncs != _ssl.HOSTFLAG_NEVER_CHECK_SUBJECT

        @hostname_checks_common_name.setter
        eleza hostname_checks_common_name(self, value):
            ikiwa value:
                self._host_flags &= ~_ssl.HOSTFLAG_NEVER_CHECK_SUBJECT
            else:
                self._host_flags |= _ssl.HOSTFLAG_NEVER_CHECK_SUBJECT
    else:
        @property
        eleza hostname_checks_common_name(self):
            rudisha True

    @property
    eleza _msg_callback(self):
        """TLS message callback

        The message callback provides a debugging hook to analyze TLS
        connections. The callback is called for any TLS protocol message
        (header, handshake, alert, and more), but not for application data.
        Due to technical  limitations, the callback can't be used to filter
        traffic or to abort a connection. Any exception raised in the
        callback is delayed until the handshake, read, or write operation
        has been performed.

        eleza msg_cb(conn, direction, version, content_type, msg_type, data):
            pass

        conn
            :class:`SSLSocket` or :class:`SSLObject` instance
        direction
            ``read`` or ``write``
        version
            :class:`TLSVersion` enum member or int for unknown version. For a
            frame header, it's the header version.
        content_type
            :class:`_TLSContentType` enum member or int for unsupported
            content type.
        msg_type
            Either a :class:`_TLSContentType` enum number for a header
            message, a :class:`_TLSAlertType` enum member for an alert
            message, a :class:`_TLSMessageType` enum member for other
            messages, or int for unsupported message types.
        data
            Raw, decrypted message content as bytes
        """
        inner = super()._msg_callback
        ikiwa inner is not None:
            rudisha inner.user_function
        else:
            rudisha None

    @_msg_callback.setter
    eleza _msg_callback(self, callback):
        ikiwa callback is None:
            super(SSLContext, SSLContext)._msg_callback.__set__(self, None)
            return

        ikiwa not hasattr(callback, '__call__'):
            raise TypeError(f"{callback} is not callable.")

        eleza inner(conn, direction, version, content_type, msg_type, data):
            try:
                version = TLSVersion(version)
            except ValueError:
                pass

            try:
                content_type = _TLSContentType(content_type)
            except ValueError:
                pass

            ikiwa content_type == _TLSContentType.HEADER:
                msg_enum = _TLSContentType
            elikiwa content_type == _TLSContentType.ALERT:
                msg_enum = _TLSAlertType
            else:
                msg_enum = _TLSMessageType
            try:
                msg_type = msg_enum(msg_type)
            except ValueError:
                pass

            rudisha callback(conn, direction, version,
                            content_type, msg_type, data)

        inner.user_function = callback

        super(SSLContext, SSLContext)._msg_callback.__set__(self, inner)

    @property
    eleza protocol(self):
        rudisha _SSLMethod(super().protocol)

    @property
    eleza verify_flags(self):
        rudisha VerifyFlags(super().verify_flags)

    @verify_flags.setter
    eleza verify_flags(self, value):
        super(SSLContext, SSLContext).verify_flags.__set__(self, value)

    @property
    eleza verify_mode(self):
        value = super().verify_mode
        try:
            rudisha VerifyMode(value)
        except ValueError:
            rudisha value

    @verify_mode.setter
    eleza verify_mode(self, value):
        super(SSLContext, SSLContext).verify_mode.__set__(self, value)


eleza create_default_context(purpose=Purpose.SERVER_AUTH, *, cafile=None,
                           capath=None, cadata=None):
    """Create a SSLContext object with default settings.

    NOTE: The protocol and settings may change anytime without prior
          deprecation. The values represent a fair balance between maximum
          compatibility and security.
    """
    ikiwa not isinstance(purpose, _ASN1Object):
        raise TypeError(purpose)

    # SSLContext sets OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_COMPRESSION,
    # OP_CIPHER_SERVER_PREFERENCE, OP_SINGLE_DH_USE and OP_SINGLE_ECDH_USE
    # by default.
    context = SSLContext(PROTOCOL_TLS)

    ikiwa purpose == Purpose.SERVER_AUTH:
        # verify certs and host name in client mode
        context.verify_mode = CERT_REQUIRED
        context.check_hostname = True

    ikiwa cafile or capath or cadata:
        context.load_verify_locations(cafile, capath, cadata)
    elikiwa context.verify_mode != CERT_NONE:
        # no explicit cafile, capath or cadata but the verify mode is
        # CERT_OPTIONAL or CERT_REQUIRED. Let's try to load default system
        # root CA certificates for the given purpose. This may fail silently.
        context.load_default_certs(purpose)
    # OpenSSL 1.1.1 keylog file
    ikiwa hasattr(context, 'keylog_filename'):
        keylogfile = os.environ.get('SSLKEYLOGFILE')
        ikiwa keylogfile and not sys.flags.ignore_environment:
            context.keylog_filename = keylogfile
    rudisha context

eleza _create_unverified_context(protocol=PROTOCOL_TLS, *, cert_reqs=CERT_NONE,
                           check_hostname=False, purpose=Purpose.SERVER_AUTH,
                           certfile=None, keyfile=None,
                           cafile=None, capath=None, cadata=None):
    """Create a SSLContext object for Python stdlib modules

    All Python stdlib modules shall use this function to create SSLContext
    objects in order to keep common settings in one place. The configuration
    is less restrict than create_default_context()'s to increase backward
    compatibility.
    """
    ikiwa not isinstance(purpose, _ASN1Object):
        raise TypeError(purpose)

    # SSLContext sets OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_COMPRESSION,
    # OP_CIPHER_SERVER_PREFERENCE, OP_SINGLE_DH_USE and OP_SINGLE_ECDH_USE
    # by default.
    context = SSLContext(protocol)

    ikiwa not check_hostname:
        context.check_hostname = False
    ikiwa cert_reqs is not None:
        context.verify_mode = cert_reqs
    ikiwa check_hostname:
        context.check_hostname = True

    ikiwa keyfile and not certfile:
        raise ValueError("certfile must be specified")
    ikiwa certfile or keyfile:
        context.load_cert_chain(certfile, keyfile)

    # load CA root certs
    ikiwa cafile or capath or cadata:
        context.load_verify_locations(cafile, capath, cadata)
    elikiwa context.verify_mode != CERT_NONE:
        # no explicit cafile, capath or cadata but the verify mode is
        # CERT_OPTIONAL or CERT_REQUIRED. Let's try to load default system
        # root CA certificates for the given purpose. This may fail silently.
        context.load_default_certs(purpose)
    # OpenSSL 1.1.1 keylog file
    ikiwa hasattr(context, 'keylog_filename'):
        keylogfile = os.environ.get('SSLKEYLOGFILE')
        ikiwa keylogfile and not sys.flags.ignore_environment:
            context.keylog_filename = keylogfile
    rudisha context

# Used by http.client ikiwa no context is explicitly passed.
_create_default_https_context = create_default_context


# Backwards compatibility alias, even though it's not a public name.
_create_stdlib_context = _create_unverified_context


kundi SSLObject:
    """This kundi implements an interface on top of a low-level SSL object as
    implemented by OpenSSL. This object captures the state of an SSL connection
    but does not provide any network IO itself. IO needs to be performed
    through separate "BIO" objects which are OpenSSL's IO abstraction layer.

    This kundi does not have a public constructor. Instances are returned by
    ``SSLContext.wrap_bio``. This kundi is typically used by framework authors
    that want to implement asynchronous IO for SSL through memory buffers.

    When compared to ``SSLSocket``, this object lacks the following features:

     * Any form of network IO, including methods such as ``recv`` and ``send``.
     * The ``do_handshake_on_connect`` and ``suppress_ragged_eofs`` machinery.
    """
    eleza __init__(self, *args, **kwargs):
        raise TypeError(
            f"{self.__class__.__name__} does not have a public "
            f"constructor. Instances are returned by SSLContext.wrap_bio()."
        )

    @classmethod
    eleza _create(cls, incoming, outgoing, server_side=False,
                 server_hostname=None, session=None, context=None):
        self = cls.__new__(cls)
        sslobj = context._wrap_bio(
            incoming, outgoing, server_side=server_side,
            server_hostname=server_hostname,
            owner=self, session=session
        )
        self._sslobj = sslobj
        rudisha self

    @property
    eleza context(self):
        """The SSLContext that is currently in use."""
        rudisha self._sslobj.context

    @context.setter
    eleza context(self, ctx):
        self._sslobj.context = ctx

    @property
    eleza session(self):
        """The SSLSession for client socket."""
        rudisha self._sslobj.session

    @session.setter
    eleza session(self, session):
        self._sslobj.session = session

    @property
    eleza session_reused(self):
        """Was the client session reused during handshake"""
        rudisha self._sslobj.session_reused

    @property
    eleza server_side(self):
        """Whether this is a server-side socket."""
        rudisha self._sslobj.server_side

    @property
    eleza server_hostname(self):
        """The currently set server hostname (for SNI), or ``None`` ikiwa no
        server hostname is set."""
        rudisha self._sslobj.server_hostname

    eleza read(self, len=1024, buffer=None):
        """Read up to 'len' bytes kutoka the SSL object and rudisha them.

        If 'buffer' is provided, read into this buffer and rudisha the number of
        bytes read.
        """
        ikiwa buffer is not None:
            v = self._sslobj.read(len, buffer)
        else:
            v = self._sslobj.read(len)
        rudisha v

    eleza write(self, data):
        """Write 'data' to the SSL object and rudisha the number of bytes
        written.

        The 'data' argument must support the buffer interface.
        """
        rudisha self._sslobj.write(data)

    eleza getpeercert(self, binary_form=False):
        """Returns a formatted version of the data in the certificate provided
        by the other end of the SSL channel.

        Return None ikiwa no certificate was provided, {} ikiwa a certificate was
        provided, but not validated.
        """
        rudisha self._sslobj.getpeercert(binary_form)

    eleza selected_npn_protocol(self):
        """Return the currently selected NPN protocol as a string, or ``None``
        ikiwa a next protocol was not negotiated or ikiwa NPN is not supported by one
        of the peers."""
        ikiwa _ssl.HAS_NPN:
            rudisha self._sslobj.selected_npn_protocol()

    eleza selected_alpn_protocol(self):
        """Return the currently selected ALPN protocol as a string, or ``None``
        ikiwa a next protocol was not negotiated or ikiwa ALPN is not supported by one
        of the peers."""
        ikiwa _ssl.HAS_ALPN:
            rudisha self._sslobj.selected_alpn_protocol()

    eleza cipher(self):
        """Return the currently selected cipher as a 3-tuple ``(name,
        ssl_version, secret_bits)``."""
        rudisha self._sslobj.cipher()

    eleza shared_ciphers(self):
        """Return a list of ciphers shared by the client during the handshake or
        None ikiwa this is not a valid server connection.
        """
        rudisha self._sslobj.shared_ciphers()

    eleza compression(self):
        """Return the current compression algorithm in use, or ``None`` if
        compression was not negotiated or not supported by one of the peers."""
        rudisha self._sslobj.compression()

    eleza pending(self):
        """Return the number of bytes that can be read immediately."""
        rudisha self._sslobj.pending()

    eleza do_handshake(self):
        """Start the SSL/TLS handshake."""
        self._sslobj.do_handshake()

    eleza unwrap(self):
        """Start the SSL shutdown handshake."""
        rudisha self._sslobj.shutdown()

    eleza get_channel_binding(self, cb_type="tls-unique"):
        """Get channel binding data for current connection.  Raise ValueError
        ikiwa the requested `cb_type` is not supported.  Return bytes of the data
        or None ikiwa the data is not available (e.g. before the handshake)."""
        rudisha self._sslobj.get_channel_binding(cb_type)

    eleza version(self):
        """Return a string identifying the protocol version used by the
        current SSL channel. """
        rudisha self._sslobj.version()

    eleza verify_client_post_handshake(self):
        rudisha self._sslobj.verify_client_post_handshake()


eleza _sslcopydoc(func):
    """Copy docstring kutoka SSLObject to SSLSocket"""
    func.__doc__ = getattr(SSLObject, func.__name__).__doc__
    rudisha func


kundi SSLSocket(socket):
    """This kundi implements a subtype of socket.socket that wraps
    the underlying OS socket in an SSL context when necessary, and
    provides read and write methods over that channel. """

    eleza __init__(self, *args, **kwargs):
        raise TypeError(
            f"{self.__class__.__name__} does not have a public "
            f"constructor. Instances are returned by "
            f"SSLContext.wrap_socket()."
        )

    @classmethod
    eleza _create(cls, sock, server_side=False, do_handshake_on_connect=True,
                suppress_ragged_eofs=True, server_hostname=None,
                context=None, session=None):
        ikiwa sock.getsockopt(SOL_SOCKET, SO_TYPE) != SOCK_STREAM:
            raise NotImplementedError("only stream sockets are supported")
        ikiwa server_side:
            ikiwa server_hostname:
                raise ValueError("server_hostname can only be specified "
                                 "in client mode")
            ikiwa session is not None:
                raise ValueError("session can only be specified in "
                                 "client mode")
        ikiwa context.check_hostname and not server_hostname:
            raise ValueError("check_hostname requires server_hostname")

        kwargs = dict(
            family=sock.family, type=sock.type, proto=sock.proto,
            fileno=sock.fileno()
        )
        self = cls.__new__(cls, **kwargs)
        super(SSLSocket, self).__init__(**kwargs)
        self.settimeout(sock.gettimeout())
        sock.detach()

        self._context = context
        self._session = session
        self._closed = False
        self._sslobj = None
        self.server_side = server_side
        self.server_hostname = context._encode_hostname(server_hostname)
        self.do_handshake_on_connect = do_handshake_on_connect
        self.suppress_ragged_eofs = suppress_ragged_eofs

        # See ikiwa we are connected
        try:
            self.getpeername()
        except OSError as e:
            ikiwa e.errno != errno.ENOTCONN:
                raise
            connected = False
        else:
            connected = True

        self._connected = connected
        ikiwa connected:
            # create the SSL object
            try:
                self._sslobj = self._context._wrap_socket(
                    self, server_side, self.server_hostname,
                    owner=self, session=self._session,
                )
                ikiwa do_handshake_on_connect:
                    timeout = self.gettimeout()
                    ikiwa timeout == 0.0:
                        # non-blocking
                        raise ValueError("do_handshake_on_connect should not be specified for non-blocking sockets")
                    self.do_handshake()
            except (OSError, ValueError):
                self.close()
                raise
        rudisha self

    @property
    @_sslcopydoc
    eleza context(self):
        rudisha self._context

    @context.setter
    eleza context(self, ctx):
        self._context = ctx
        self._sslobj.context = ctx

    @property
    @_sslcopydoc
    eleza session(self):
        ikiwa self._sslobj is not None:
            rudisha self._sslobj.session

    @session.setter
    eleza session(self, session):
        self._session = session
        ikiwa self._sslobj is not None:
            self._sslobj.session = session

    @property
    @_sslcopydoc
    eleza session_reused(self):
        ikiwa self._sslobj is not None:
            rudisha self._sslobj.session_reused

    eleza dup(self):
        raise NotImplementedError("Can't dup() %s instances" %
                                  self.__class__.__name__)

    eleza _checkClosed(self, msg=None):
        # raise an exception here ikiwa you wish to check for spurious closes
        pass

    eleza _check_connected(self):
        ikiwa not self._connected:
            # getpeername() will raise ENOTCONN ikiwa the socket is really
            # not connected; note that we can be connected even without
            # _connected being set, e.g. ikiwa connect() first returned
            # EAGAIN.
            self.getpeername()

    eleza read(self, len=1024, buffer=None):
        """Read up to LEN bytes and rudisha them.
        Return zero-length string on EOF."""

        self._checkClosed()
        ikiwa self._sslobj is None:
            raise ValueError("Read on closed or unwrapped SSL socket.")
        try:
            ikiwa buffer is not None:
                rudisha self._sslobj.read(len, buffer)
            else:
                rudisha self._sslobj.read(len)
        except SSLError as x:
            ikiwa x.args[0] == SSL_ERROR_EOF and self.suppress_ragged_eofs:
                ikiwa buffer is not None:
                    rudisha 0
                else:
                    rudisha b''
            else:
                raise

    eleza write(self, data):
        """Write DATA to the underlying SSL channel.  Returns
        number of bytes of DATA actually transmitted."""

        self._checkClosed()
        ikiwa self._sslobj is None:
            raise ValueError("Write on closed or unwrapped SSL socket.")
        rudisha self._sslobj.write(data)

    @_sslcopydoc
    eleza getpeercert(self, binary_form=False):
        self._checkClosed()
        self._check_connected()
        rudisha self._sslobj.getpeercert(binary_form)

    @_sslcopydoc
    eleza selected_npn_protocol(self):
        self._checkClosed()
        ikiwa self._sslobj is None or not _ssl.HAS_NPN:
            rudisha None
        else:
            rudisha self._sslobj.selected_npn_protocol()

    @_sslcopydoc
    eleza selected_alpn_protocol(self):
        self._checkClosed()
        ikiwa self._sslobj is None or not _ssl.HAS_ALPN:
            rudisha None
        else:
            rudisha self._sslobj.selected_alpn_protocol()

    @_sslcopydoc
    eleza cipher(self):
        self._checkClosed()
        ikiwa self._sslobj is None:
            rudisha None
        else:
            rudisha self._sslobj.cipher()

    @_sslcopydoc
    eleza shared_ciphers(self):
        self._checkClosed()
        ikiwa self._sslobj is None:
            rudisha None
        else:
            rudisha self._sslobj.shared_ciphers()

    @_sslcopydoc
    eleza compression(self):
        self._checkClosed()
        ikiwa self._sslobj is None:
            rudisha None
        else:
            rudisha self._sslobj.compression()

    eleza send(self, data, flags=0):
        self._checkClosed()
        ikiwa self._sslobj is not None:
            ikiwa flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to send() on %s" %
                    self.__class__)
            rudisha self._sslobj.write(data)
        else:
            rudisha super().send(data, flags)

    eleza sendto(self, data, flags_or_addr, addr=None):
        self._checkClosed()
        ikiwa self._sslobj is not None:
            raise ValueError("sendto not allowed on instances of %s" %
                             self.__class__)
        elikiwa addr is None:
            rudisha super().sendto(data, flags_or_addr)
        else:
            rudisha super().sendto(data, flags_or_addr, addr)

    eleza sendmsg(self, *args, **kwargs):
        # Ensure programs don't send data unencrypted ikiwa they try to
        # use this method.
        raise NotImplementedError("sendmsg not allowed on instances of %s" %
                                  self.__class__)

    eleza sendall(self, data, flags=0):
        self._checkClosed()
        ikiwa self._sslobj is not None:
            ikiwa flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to sendall() on %s" %
                    self.__class__)
            count = 0
            with memoryview(data) as view, view.cast("B") as byte_view:
                amount = len(byte_view)
                while count < amount:
                    v = self.send(byte_view[count:])
                    count += v
        else:
            rudisha super().sendall(data, flags)

    eleza sendfile(self, file, offset=0, count=None):
        """Send a file, possibly by using os.sendfile() ikiwa this is a
        clear-text socket.  Return the total number of bytes sent.
        """
        ikiwa self._sslobj is not None:
            rudisha self._sendfile_use_send(file, offset, count)
        else:
            # os.sendfile() works with plain sockets only
            rudisha super().sendfile(file, offset, count)

    eleza recv(self, buflen=1024, flags=0):
        self._checkClosed()
        ikiwa self._sslobj is not None:
            ikiwa flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to recv() on %s" %
                    self.__class__)
            rudisha self.read(buflen)
        else:
            rudisha super().recv(buflen, flags)

    eleza recv_into(self, buffer, nbytes=None, flags=0):
        self._checkClosed()
        ikiwa buffer and (nbytes is None):
            nbytes = len(buffer)
        elikiwa nbytes is None:
            nbytes = 1024
        ikiwa self._sslobj is not None:
            ikiwa flags != 0:
                raise ValueError(
                  "non-zero flags not allowed in calls to recv_into() on %s" %
                  self.__class__)
            rudisha self.read(nbytes, buffer)
        else:
            rudisha super().recv_into(buffer, nbytes, flags)

    eleza recvkutoka(self, buflen=1024, flags=0):
        self._checkClosed()
        ikiwa self._sslobj is not None:
            raise ValueError("recvkutoka not allowed on instances of %s" %
                             self.__class__)
        else:
            rudisha super().recvkutoka(buflen, flags)

    eleza recvkutoka_into(self, buffer, nbytes=None, flags=0):
        self._checkClosed()
        ikiwa self._sslobj is not None:
            raise ValueError("recvkutoka_into not allowed on instances of %s" %
                             self.__class__)
        else:
            rudisha super().recvkutoka_into(buffer, nbytes, flags)

    eleza recvmsg(self, *args, **kwargs):
        raise NotImplementedError("recvmsg not allowed on instances of %s" %
                                  self.__class__)

    eleza recvmsg_into(self, *args, **kwargs):
        raise NotImplementedError("recvmsg_into not allowed on instances of "
                                  "%s" % self.__class__)

    @_sslcopydoc
    eleza pending(self):
        self._checkClosed()
        ikiwa self._sslobj is not None:
            rudisha self._sslobj.pending()
        else:
            rudisha 0

    eleza shutdown(self, how):
        self._checkClosed()
        self._sslobj = None
        super().shutdown(how)

    @_sslcopydoc
    eleza unwrap(self):
        ikiwa self._sslobj:
            s = self._sslobj.shutdown()
            self._sslobj = None
            rudisha s
        else:
            raise ValueError("No SSL wrapper around " + str(self))

    @_sslcopydoc
    eleza verify_client_post_handshake(self):
        ikiwa self._sslobj:
            rudisha self._sslobj.verify_client_post_handshake()
        else:
            raise ValueError("No SSL wrapper around " + str(self))

    eleza _real_close(self):
        self._sslobj = None
        super()._real_close()

    @_sslcopydoc
    eleza do_handshake(self, block=False):
        self._check_connected()
        timeout = self.gettimeout()
        try:
            ikiwa timeout == 0.0 and block:
                self.settimeout(None)
            self._sslobj.do_handshake()
        finally:
            self.settimeout(timeout)

    eleza _real_connect(self, addr, connect_ex):
        ikiwa self.server_side:
            raise ValueError("can't connect in server-side mode")
        # Here we assume that the socket is client-side, and not
        # connected at the time of the call.  We connect it, then wrap it.
        ikiwa self._connected or self._sslobj is not None:
            raise ValueError("attempt to connect already-connected SSLSocket!")
        self._sslobj = self.context._wrap_socket(
            self, False, self.server_hostname,
            owner=self, session=self._session
        )
        try:
            ikiwa connect_ex:
                rc = super().connect_ex(addr)
            else:
                rc = None
                super().connect(addr)
            ikiwa not rc:
                self._connected = True
                ikiwa self.do_handshake_on_connect:
                    self.do_handshake()
            rudisha rc
        except (OSError, ValueError):
            self._sslobj = None
            raise

    eleza connect(self, addr):
        """Connects to remote ADDR, and then wraps the connection in
        an SSL channel."""
        self._real_connect(addr, False)

    eleza connect_ex(self, addr):
        """Connects to remote ADDR, and then wraps the connection in
        an SSL channel."""
        rudisha self._real_connect(addr, True)

    eleza accept(self):
        """Accepts a new connection kutoka a remote client, and returns
        a tuple containing that new connection wrapped with a server-side
        SSL channel, and the address of the remote client."""

        newsock, addr = super().accept()
        newsock = self.context.wrap_socket(newsock,
                    do_handshake_on_connect=self.do_handshake_on_connect,
                    suppress_ragged_eofs=self.suppress_ragged_eofs,
                    server_side=True)
        rudisha newsock, addr

    @_sslcopydoc
    eleza get_channel_binding(self, cb_type="tls-unique"):
        ikiwa self._sslobj is not None:
            rudisha self._sslobj.get_channel_binding(cb_type)
        else:
            ikiwa cb_type not in CHANNEL_BINDING_TYPES:
                raise ValueError(
                    "{0} channel binding type not implemented".format(cb_type)
                )
            rudisha None

    @_sslcopydoc
    eleza version(self):
        ikiwa self._sslobj is not None:
            rudisha self._sslobj.version()
        else:
            rudisha None


# Python does not support forward declaration of types.
SSLContext.sslsocket_kundi = SSLSocket
SSLContext.sslobject_kundi = SSLObject


eleza wrap_socket(sock, keyfile=None, certfile=None,
                server_side=False, cert_reqs=CERT_NONE,
                ssl_version=PROTOCOL_TLS, ca_certs=None,
                do_handshake_on_connect=True,
                suppress_ragged_eofs=True,
                ciphers=None):

    ikiwa server_side and not certfile:
        raise ValueError("certfile must be specified for server-side "
                         "operations")
    ikiwa keyfile and not certfile:
        raise ValueError("certfile must be specified")
    context = SSLContext(ssl_version)
    context.verify_mode = cert_reqs
    ikiwa ca_certs:
        context.load_verify_locations(ca_certs)
    ikiwa certfile:
        context.load_cert_chain(certfile, keyfile)
    ikiwa ciphers:
        context.set_ciphers(ciphers)
    rudisha context.wrap_socket(
        sock=sock, server_side=server_side,
        do_handshake_on_connect=do_handshake_on_connect,
        suppress_ragged_eofs=suppress_ragged_eofs
    )

# some utility functions

eleza cert_time_to_seconds(cert_time):
    """Return the time in seconds since the Epoch, given the timestring
    representing the "notBefore" or "notAfter" date kutoka a certificate
    in ``"%b %d %H:%M:%S %Y %Z"`` strptime format (C locale).

    "notBefore" or "notAfter" dates must use UTC (RFC 5280).

    Month is one of: Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
    UTC should be specified as GMT (see ASN1_TIME_andika())
    """
    kutoka time agiza strptime
    kutoka calendar agiza timegm

    months = (
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    )
    time_format = ' %d %H:%M:%S %Y GMT' # NOTE: no month, fixed GMT
    try:
        month_number = months.index(cert_time[:3].title()) + 1
    except ValueError:
        raise ValueError('time data %r does not match '
                         'format "%%b%s"' % (cert_time, time_format))
    else:
        # found valid month
        tt = strptime(cert_time[3:], time_format)
        # rudisha an integer, the previous mktime()-based implementation
        # returned a float (fractional seconds are always zero here).
        rudisha timegm((tt[0], month_number) + tt[2:6])

PEM_HEADER = "-----BEGIN CERTIFICATE-----"
PEM_FOOTER = "-----END CERTIFICATE-----"

eleza DER_cert_to_PEM_cert(der_cert_bytes):
    """Takes a certificate in binary DER format and returns the
    PEM version of it as a string."""

    f = str(base64.standard_b64encode(der_cert_bytes), 'ASCII', 'strict')
    ss = [PEM_HEADER]
    ss += [f[i:i+64] for i in range(0, len(f), 64)]
    ss.append(PEM_FOOTER + '\n')
    rudisha '\n'.join(ss)

eleza PEM_cert_to_DER_cert(pem_cert_string):
    """Takes a certificate in ASCII PEM format and returns the
    DER-encoded version of it as a byte sequence"""

    ikiwa not pem_cert_string.startswith(PEM_HEADER):
        raise ValueError("Invalid PEM encoding; must start with %s"
                         % PEM_HEADER)
    ikiwa not pem_cert_string.strip().endswith(PEM_FOOTER):
        raise ValueError("Invalid PEM encoding; must end with %s"
                         % PEM_FOOTER)
    d = pem_cert_string.strip()[len(PEM_HEADER):-len(PEM_FOOTER)]
    rudisha base64.decodebytes(d.encode('ASCII', 'strict'))

eleza get_server_certificate(addr, ssl_version=PROTOCOL_TLS, ca_certs=None):
    """Retrieve the certificate kutoka the server at the specified address,
    and rudisha it as a PEM-encoded string.
    If 'ca_certs' is specified, validate the server cert against it.
    If 'ssl_version' is specified, use it in the connection attempt."""

    host, port = addr
    ikiwa ca_certs is not None:
        cert_reqs = CERT_REQUIRED
    else:
        cert_reqs = CERT_NONE
    context = _create_stdlib_context(ssl_version,
                                     cert_reqs=cert_reqs,
                                     cafile=ca_certs)
    with  create_connection(addr) as sock:
        with context.wrap_socket(sock) as sslsock:
            dercert = sslsock.getpeercert(True)
    rudisha DER_cert_to_PEM_cert(dercert)

eleza get_protocol_name(protocol_code):
    rudisha _PROTOCOL_NAMES.get(protocol_code, '<unknown>')
