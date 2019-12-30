# Wrapper module kila _ssl, providing some additional facilities
# implemented kwenye Python.  Written by Bill Janssen.

"""This module provides some more Pythonic support kila SSL.

Object types:

  SSLSocket -- subtype of socket.socket which does SSL over the socket

Exceptions:

  SSLError -- exception raised kila I/O errors

Functions:

  cert_time_to_seconds -- convert time string used kila certificate
                          notBefore na notAfter functions to integer
                          seconds past the Epoch (the time values
                          returned kutoka time.time())

  fetch_server_certificate (HOST, PORT) -- fetch the certificate provided
                          by the server running on HOST at port PORT.  No
                          validation of the certificate ni performed.

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
CERT_OPTIONAL - certificates are sio required, but ikiwa provided will be
                validated, na ikiwa validation fails, the connection will
                also fail
CERT_REQUIRED - certificates are required, na will be validated, and
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
jaribu:
    kutoka _ssl agiza RAND_egd
except ImportError:
    # LibreSSL does sio provide RAND_egd
    pass


kutoka _ssl agiza (
    HAS_SNI, HAS_ECDH, HAS_NPN, HAS_ALPN, HAS_SSLv2, HAS_SSLv3, HAS_TLSv1,
    HAS_TLSv1_1, HAS_TLSv1_2, HAS_TLSv1_3
)
kutoka _ssl agiza _DEFAULT_CIPHERS, _OPENSSL_API_VERSION


_IntEnum._convert_(
    '_SSLMethod', __name__,
    lambda name: name.startswith('PROTOCOL_') na name != 'PROTOCOL_SSLv23',
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
_PROTOCOL_NAMES = {value: name kila name, value kwenye _SSLMethod.__members__.items()}

_SSLv2_IF_EXISTS = getattr(_SSLMethod, 'PROTOCOL_SSLv2', Tupu)


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
    """Alert types kila TLSContentType.ALERT messages

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
agiza base64        # kila DER-to-PEM translation
agiza errno
agiza warnings


socket_error = OSError  # keep that public name kwenye module namespace

CHANNEL_BINDING_TYPES = ['tls-unique']

HAS_NEVER_CHECK_COMMON_NAME = hasattr(_ssl, 'HOSTFLAG_NEVER_CHECK_SUBJECT')


_RESTRICTED_SERVER_CIPHERS = _DEFAULT_CIPHERS

CertificateError = SSLCertVerificationError


eleza _dnsname_match(dn, hostname):
    """Matching according to RFC 6125, section 6.4.3

    - Hostnames are compared lower case.
    - For IDNA, both dn na hostname must be encoded as IDN A-label (ACE).
    - Partial wildcards like 'www*.example.org', multiple wildcards, sole
      wildcard ama wildcards kwenye labels other then the left-most label are not
      supported na a CertificateError ni raised.
    - A wildcard must match at least one character.
    """
    ikiwa sio dn:
        rudisha Uongo

    wildcards = dn.count('*')
    # speed up common case w/o wildcards
    ikiwa sio wildcards:
        rudisha dn.lower() == hostname.lower()

    ikiwa wildcards > 1:
         ashiria CertificateError(
            "too many wildcards kwenye certificate DNS name: {!r}.".format(dn))

    dn_leftmost, sep, dn_remainder = dn.partition('.')

    ikiwa '*' kwenye dn_remainder:
        # Only match wildcard kwenye leftmost segment.
         ashiria CertificateError(
            "wildcard can only be present kwenye the leftmost label: "
            "{!r}.".format(dn))

    ikiwa sio sep:
        # no right side
         ashiria CertificateError(
            "sole wildcard without additional labels are sio support: "
            "{!r}.".format(dn))

    ikiwa dn_leftmost != '*':
        # no partial wildcard matching
         ashiria CertificateError(
            "partial wildcards kwenye leftmost label are sio supported: "
            "{!r}.".format(dn))

    hostname_leftmost, sep, hostname_remainder = hostname.partition('.')
    ikiwa sio hostname_leftmost ama sio sep:
        # wildcard must match at least one char
        rudisha Uongo
    rudisha dn_remainder.lower() == hostname_remainder.lower()


eleza _inet_paton(ipname):
    """Try to convert an IP address to packed binary form

    Supports IPv4 addresses on all platforms na IPv6 on platforms ukijumuisha IPv6
    support.
    """
    # inet_aton() also accepts strings like '1', '127.1', some also trailing
    # data like '127.0.0.1 whatever'.
    jaribu:
        addr = _socket.inet_aton(ipname)
    except OSError:
        # sio an IPv4 address
        pass
    isipokua:
        ikiwa _socket.inet_ntoa(addr) == ipname:
            # only accept injective ipnames
            rudisha addr
        isipokua:
            # refuse kila short IPv4 notation na additional trailing data
             ashiria ValueError(
                "{!r} ni sio a quad-dotted IPv4 address.".format(ipname)
            )

    jaribu:
        rudisha _socket.inet_pton(_socket.AF_INET6, ipname)
    except OSError:
         ashiria ValueError("{!r} ni neither an IPv4 nor an IP6 "
                         "address.".format(ipname))
    except AttributeError:
        # AF_INET6 sio available
        pass

     ashiria ValueError("{!r} ni sio an IPv4 address.".format(ipname))


eleza _ipaddress_match(cert_ipaddress, host_ip):
    """Exact matching of IP addresses.

    RFC 6125 explicitly doesn't define an algorithm kila this
    (section 1.7.2 - "Out of Scope").
    """
    # OpenSSL may add a trailing newline to a subjectAltName's IP address,
    # commonly woth IPv6 addresses. Strip off trailing \n.
    ip = _inet_paton(cert_ipaddress.rstrip())
    rudisha ip == host_ip


eleza match_hostname(cert, hostname):
    """Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 na RFC 6125
    rules are followed.

    The function matches IP addresses rather than dNSNames ikiwa hostname ni a
    valid ipaddress string. IPv4 addresses are supported on all platforms.
    IPv6 addresses are supported on platforms ukijumuisha IPv6 support (AF_INET6
    na inet_pton).

    CertificateError ni raised on failure. On success, the function
    returns nothing.
    """
    ikiwa sio cert:
         ashiria ValueError("empty ama no certificate, match_hostname needs a "
                         "SSL socket ama SSL context ukijumuisha either "
                         "CERT_OPTIONAL ama CERT_REQUIRED")
    jaribu:
        host_ip = _inet_paton(hostname)
    except ValueError:
        # Not an IP address (common case)
        host_ip = Tupu
    dnsnames = []
    san = cert.get('subjectAltName', ())
    kila key, value kwenye san:
        ikiwa key == 'DNS':
            ikiwa host_ip ni Tupu na _dnsname_match(value, hostname):
                return
            dnsnames.append(value)
        elikiwa key == 'IP Address':
            ikiwa host_ip ni sio Tupu na _ipaddress_match(value, host_ip):
                return
            dnsnames.append(value)
    ikiwa sio dnsnames:
        # The subject ni only checked when there ni no dNSName entry
        # kwenye subjectAltName
        kila sub kwenye cert.get('subject', ()):
            kila key, value kwenye sub:
                # XXX according to RFC 2818, the most specific Common Name
                # must be used.
                ikiwa key == 'commonName':
                    ikiwa _dnsname_match(value, hostname):
                        return
                    dnsnames.append(value)
    ikiwa len(dnsnames) > 1:
         ashiria CertificateError("hostname %r "
            "doesn't match either of %s"
            % (hostname, ', '.join(map(repr, dnsnames))))
    elikiwa len(dnsnames) == 1:
         ashiria CertificateError("hostname %r "
            "doesn't match %r"
            % (hostname, dnsnames[0]))
    isipokua:
         ashiria CertificateError("no appropriate commonName ama "
            "subjectAltName fields were found")


DefaultVerifyPaths = namedtuple("DefaultVerifyPaths",
    "cafile capath openssl_cafile_env openssl_cafile openssl_capath_env "
    "openssl_capath")

eleza get_default_verify_paths():
    """Return paths to default cafile na capath.
    """
    parts = _ssl.get_default_verify_paths()

    # environment vars shadow paths
    cafile = os.environ.get(parts[0], parts[1])
    capath = os.environ.get(parts[2], parts[3])

    rudisha DefaultVerifyPaths(cafile ikiwa os.path.isfile(cafile) isipokua Tupu,
                              capath ikiwa os.path.isdir(capath) isipokua Tupu,
                              *parts)


kundi _ASN1Object(namedtuple("_ASN1Object", "nid shortname longname oid")):
    """ASN.1 object identifier lookup
    """
    __slots__ = ()

    eleza __new__(cls, oid):
        rudisha super().__new__(cls, *_txt2obj(oid, name=Uongo))

    @classmethod
    eleza fromnid(cls, nid):
        """Create _ASN1Object kutoka OpenSSL numeric ID
        """
        rudisha super().__new__(cls, *_nid2obj(nid))

    @classmethod
    eleza fromname(cls, name):
        """Create _ASN1Object kutoka short name, long name ama OID
        """
        rudisha super().__new__(cls, *_txt2obj(name, name=Kweli))


kundi Purpose(_ASN1Object, _Enum):
    """SSLContext purpose flags ukijumuisha X509v3 Extended Key Usage objects
    """
    SERVER_AUTH = '1.3.6.1.5.5.7.3.1'
    CLIENT_AUTH = '1.3.6.1.5.5.7.3.2'


kundi SSLContext(_SSLContext):
    """An SSLContext holds various SSL-related configuration options and
    data, such as certificates na possibly a private key."""
    _windows_cert_stores = ("CA", "ROOT")

    sslsocket_kundi = Tupu  # SSLSocket ni assigned later.
    sslobject_kundi = Tupu  # SSLObject ni assigned later.

    eleza __new__(cls, protocol=PROTOCOL_TLS, *args, **kwargs):
        self = _SSLContext.__new__(cls, protocol)
        rudisha self

    eleza _encode_hostname(self, hostname):
        ikiwa hostname ni Tupu:
            rudisha Tupu
        elikiwa isinstance(hostname, str):
            rudisha hostname.encode('idna').decode('ascii')
        isipokua:
            rudisha hostname.decode('ascii')

    eleza wrap_socket(self, sock, server_side=Uongo,
                    do_handshake_on_connect=Kweli,
                    suppress_ragged_eofs=Kweli,
                    server_hostname=Tupu, session=Tupu):
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

    eleza wrap_bio(self, incoming, outgoing, server_side=Uongo,
                 server_hostname=Tupu, session=Tupu):
        # Need to encode server_hostname here because _wrap_bio() can only
        # handle ASCII str.
        rudisha self.sslobject_class._create(
            incoming, outgoing, server_side=server_side,
            server_hostname=self._encode_hostname(server_hostname),
            session=session, context=self,
        )

    eleza set_npn_protocols(self, npn_protocols):
        protos = bytearray()
        kila protocol kwenye npn_protocols:
            b = bytes(protocol, 'ascii')
            ikiwa len(b) == 0 ama len(b) > 255:
                 ashiria SSLError('NPN protocols must be 1 to 255 kwenye length')
            protos.append(len(b))
            protos.extend(b)

        self._set_npn_protocols(protos)

    eleza set_servername_callback(self, server_name_callback):
        ikiwa server_name_callback ni Tupu:
            self.sni_callback = Tupu
        isipokua:
            ikiwa sio callable(server_name_callback):
                 ashiria TypeError("not a callable object")

            eleza shim_cb(sslobj, servername, sslctx):
                servername = self._encode_hostname(servername)
                rudisha server_name_callback(sslobj, servername, sslctx)

            self.sni_callback = shim_cb

    eleza set_alpn_protocols(self, alpn_protocols):
        protos = bytearray()
        kila protocol kwenye alpn_protocols:
            b = bytes(protocol, 'ascii')
            ikiwa len(b) == 0 ama len(b) > 255:
                 ashiria SSLError('ALPN protocols must be 1 to 255 kwenye length')
            protos.append(len(b))
            protos.extend(b)

        self._set_alpn_protocols(protos)

    eleza _load_windows_store_certs(self, storename, purpose):
        certs = bytearray()
        jaribu:
            kila cert, encoding, trust kwenye enum_certificates(storename):
                # CA certs are never PKCS#7 encoded
                ikiwa encoding == "x509_asn":
                    ikiwa trust ni Kweli ama purpose.oid kwenye trust:
                        certs.extend(cert)
        except PermissionError:
            warnings.warn("unable to enumerate Windows certificate store")
        ikiwa certs:
            self.load_verify_locations(cadata=certs)
        rudisha certs

    eleza load_default_certs(self, purpose=Purpose.SERVER_AUTH):
        ikiwa sio isinstance(purpose, _ASN1Object):
             ashiria TypeError(purpose)
        ikiwa sys.platform == "win32":
            kila storename kwenye self._windows_cert_stores:
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
            isipokua:
                self._host_flags |= _ssl.HOSTFLAG_NEVER_CHECK_SUBJECT
    isipokua:
        @property
        eleza hostname_checks_common_name(self):
            rudisha Kweli

    @property
    eleza _msg_callback(self):
        """TLS message callback

        The message callback provides a debugging hook to analyze TLS
        connections. The callback ni called kila any TLS protocol message
        (header, handshake, alert, na more), but sio kila application data.
        Due to technical  limitations, the callback can't be used to filter
        traffic ama to abort a connection. Any exception raised kwenye the
        callback ni delayed until the handshake, read, ama write operation
        has been performed.

        eleza msg_cb(conn, direction, version, content_type, msg_type, data):
            pass

        conn
            :class:`SSLSocket` ama :class:`SSLObject` instance
        direction
            ``read`` ama ``write``
        version
            :class:`TLSVersion` enum member ama int kila unknown version. For a
            frame header, it's the header version.
        content_type
            :class:`_TLSContentType` enum member ama int kila unsupported
            content type.
        msg_type
            Either a :class:`_TLSContentType` enum number kila a header
            message, a :class:`_TLSAlertType` enum member kila an alert
            message, a :class:`_TLSMessageType` enum member kila other
            messages, ama int kila unsupported message types.
        data
            Raw, decrypted message content as bytes
        """
        inner = super()._msg_callback
        ikiwa inner ni sio Tupu:
            rudisha inner.user_function
        isipokua:
            rudisha Tupu

    @_msg_callback.setter
    eleza _msg_callback(self, callback):
        ikiwa callback ni Tupu:
            super(SSLContext, SSLContext)._msg_callback.__set__(self, Tupu)
            return

        ikiwa sio hasattr(callback, '__call__'):
             ashiria TypeError(f"{callback} ni sio callable.")

        eleza inner(conn, direction, version, content_type, msg_type, data):
            jaribu:
                version = TLSVersion(version)
            except ValueError:
                pass

            jaribu:
                content_type = _TLSContentType(content_type)
            except ValueError:
                pass

            ikiwa content_type == _TLSContentType.HEADER:
                msg_enum = _TLSContentType
            elikiwa content_type == _TLSContentType.ALERT:
                msg_enum = _TLSAlertType
            isipokua:
                msg_enum = _TLSMessageType
            jaribu:
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
        jaribu:
            rudisha VerifyMode(value)
        except ValueError:
            rudisha value

    @verify_mode.setter
    eleza verify_mode(self, value):
        super(SSLContext, SSLContext).verify_mode.__set__(self, value)


eleza create_default_context(purpose=Purpose.SERVER_AUTH, *, cafile=Tupu,
                           capath=Tupu, cadata=Tupu):
    """Create a SSLContext object ukijumuisha default settings.

    NOTE: The protocol na settings may change anytime without prior
          deprecation. The values represent a fair balance between maximum
          compatibility na security.
    """
    ikiwa sio isinstance(purpose, _ASN1Object):
         ashiria TypeError(purpose)

    # SSLContext sets OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_COMPRESSION,
    # OP_CIPHER_SERVER_PREFERENCE, OP_SINGLE_DH_USE na OP_SINGLE_ECDH_USE
    # by default.
    context = SSLContext(PROTOCOL_TLS)

    ikiwa purpose == Purpose.SERVER_AUTH:
        # verify certs na host name kwenye client mode
        context.verify_mode = CERT_REQUIRED
        context.check_hostname = Kweli

    ikiwa cafile ama capath ama cadata:
        context.load_verify_locations(cafile, capath, cadata)
    elikiwa context.verify_mode != CERT_NONE:
        # no explicit cafile, capath ama cadata but the verify mode is
        # CERT_OPTIONAL ama CERT_REQUIRED. Let's try to load default system
        # root CA certificates kila the given purpose. This may fail silently.
        context.load_default_certs(purpose)
    # OpenSSL 1.1.1 keylog file
    ikiwa hasattr(context, 'keylog_filename'):
        keylogfile = os.environ.get('SSLKEYLOGFILE')
        ikiwa keylogfile na sio sys.flags.ignore_environment:
            context.keylog_filename = keylogfile
    rudisha context

eleza _create_unverified_context(protocol=PROTOCOL_TLS, *, cert_reqs=CERT_NONE,
                           check_hostname=Uongo, purpose=Purpose.SERVER_AUTH,
                           certfile=Tupu, keyfile=Tupu,
                           cafile=Tupu, capath=Tupu, cadata=Tupu):
    """Create a SSLContext object kila Python stdlib modules

    All Python stdlib modules shall use this function to create SSLContext
    objects kwenye order to keep common settings kwenye one place. The configuration
    ni less restrict than create_default_context()'s to increase backward
    compatibility.
    """
    ikiwa sio isinstance(purpose, _ASN1Object):
         ashiria TypeError(purpose)

    # SSLContext sets OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_COMPRESSION,
    # OP_CIPHER_SERVER_PREFERENCE, OP_SINGLE_DH_USE na OP_SINGLE_ECDH_USE
    # by default.
    context = SSLContext(protocol)

    ikiwa sio check_hostname:
        context.check_hostname = Uongo
    ikiwa cert_reqs ni sio Tupu:
        context.verify_mode = cert_reqs
    ikiwa check_hostname:
        context.check_hostname = Kweli

    ikiwa keyfile na sio certfile:
         ashiria ValueError("certfile must be specified")
    ikiwa certfile ama keyfile:
        context.load_cert_chain(certfile, keyfile)

    # load CA root certs
    ikiwa cafile ama capath ama cadata:
        context.load_verify_locations(cafile, capath, cadata)
    elikiwa context.verify_mode != CERT_NONE:
        # no explicit cafile, capath ama cadata but the verify mode is
        # CERT_OPTIONAL ama CERT_REQUIRED. Let's try to load default system
        # root CA certificates kila the given purpose. This may fail silently.
        context.load_default_certs(purpose)
    # OpenSSL 1.1.1 keylog file
    ikiwa hasattr(context, 'keylog_filename'):
        keylogfile = os.environ.get('SSLKEYLOGFILE')
        ikiwa keylogfile na sio sys.flags.ignore_environment:
            context.keylog_filename = keylogfile
    rudisha context

# Used by http.client ikiwa no context ni explicitly passed.
_create_default_https_context = create_default_context


# Backwards compatibility alias, even though it's sio a public name.
_create_stdlib_context = _create_unverified_context


kundi SSLObject:
    """This kundi implements an interface on top of a low-level SSL object as
    implemented by OpenSSL. This object captures the state of an SSL connection
    but does sio provide any network IO itself. IO needs to be performed
    through separate "BIO" objects which are OpenSSL's IO abstraction layer.

    This kundi does sio have a public constructor. Instances are returned by
    ``SSLContext.wrap_bio``. This kundi ni typically used by framework authors
    that want to implement asynchronous IO kila SSL through memory buffers.

    When compared to ``SSLSocket``, this object lacks the following features:

     * Any form of network IO, including methods such as ``recv`` na ``send``.
     * The ``do_handshake_on_connect`` na ``suppress_ragged_eofs`` machinery.
    """
    eleza __init__(self, *args, **kwargs):
         ashiria TypeError(
            f"{self.__class__.__name__} does sio have a public "
            f"constructor. Instances are returned by SSLContext.wrap_bio()."
        )

    @classmethod
    eleza _create(cls, incoming, outgoing, server_side=Uongo,
                 server_hostname=Tupu, session=Tupu, context=Tupu):
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
        """The SSLContext that ni currently kwenye use."""
        rudisha self._sslobj.context

    @context.setter
    eleza context(self, ctx):
        self._sslobj.context = ctx

    @property
    eleza session(self):
        """The SSLSession kila client socket."""
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
        """Whether this ni a server-side socket."""
        rudisha self._sslobj.server_side

    @property
    eleza server_hostname(self):
        """The currently set server hostname (kila SNI), ama ``Tupu`` ikiwa no
        server hostname ni set."""
        rudisha self._sslobj.server_hostname

    eleza read(self, len=1024, buffer=Tupu):
        """Read up to 'len' bytes kutoka the SSL object na rudisha them.

        If 'buffer' ni provided, read into this buffer na rudisha the number of
        bytes read.
        """
        ikiwa buffer ni sio Tupu:
            v = self._sslobj.read(len, buffer)
        isipokua:
            v = self._sslobj.read(len)
        rudisha v

    eleza write(self, data):
        """Write 'data' to the SSL object na rudisha the number of bytes
        written.

        The 'data' argument must support the buffer interface.
        """
        rudisha self._sslobj.write(data)

    eleza getpeercert(self, binary_form=Uongo):
        """Returns a formatted version of the data kwenye the certificate provided
        by the other end of the SSL channel.

        Return Tupu ikiwa no certificate was provided, {} ikiwa a certificate was
        provided, but sio validated.
        """
        rudisha self._sslobj.getpeercert(binary_form)

    eleza selected_npn_protocol(self):
        """Return the currently selected NPN protocol as a string, ama ``Tupu``
        ikiwa a next protocol was sio negotiated ama ikiwa NPN ni sio supported by one
        of the peers."""
        ikiwa _ssl.HAS_NPN:
            rudisha self._sslobj.selected_npn_protocol()

    eleza selected_alpn_protocol(self):
        """Return the currently selected ALPN protocol as a string, ama ``Tupu``
        ikiwa a next protocol was sio negotiated ama ikiwa ALPN ni sio supported by one
        of the peers."""
        ikiwa _ssl.HAS_ALPN:
            rudisha self._sslobj.selected_alpn_protocol()

    eleza cipher(self):
        """Return the currently selected cipher as a 3-tuple ``(name,
        ssl_version, secret_bits)``."""
        rudisha self._sslobj.cipher()

    eleza shared_ciphers(self):
        """Return a list of ciphers shared by the client during the handshake or
        Tupu ikiwa this ni sio a valid server connection.
        """
        rudisha self._sslobj.shared_ciphers()

    eleza compression(self):
        """Return the current compression algorithm kwenye use, ama ``Tupu`` if
        compression was sio negotiated ama sio supported by one of the peers."""
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
        """Get channel binding data kila current connection.  Raise ValueError
        ikiwa the requested `cb_type` ni sio supported.  Return bytes of the data
        ama Tupu ikiwa the data ni sio available (e.g. before the handshake)."""
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
    the underlying OS socket kwenye an SSL context when necessary, and
    provides read na write methods over that channel. """

    eleza __init__(self, *args, **kwargs):
         ashiria TypeError(
            f"{self.__class__.__name__} does sio have a public "
            f"constructor. Instances are returned by "
            f"SSLContext.wrap_socket()."
        )

    @classmethod
    eleza _create(cls, sock, server_side=Uongo, do_handshake_on_connect=Kweli,
                suppress_ragged_eofs=Kweli, server_hostname=Tupu,
                context=Tupu, session=Tupu):
        ikiwa sock.getsockopt(SOL_SOCKET, SO_TYPE) != SOCK_STREAM:
             ashiria NotImplementedError("only stream sockets are supported")
        ikiwa server_side:
            ikiwa server_hostname:
                 ashiria ValueError("server_hostname can only be specified "
                                 "in client mode")
            ikiwa session ni sio Tupu:
                 ashiria ValueError("session can only be specified kwenye "
                                 "client mode")
        ikiwa context.check_hostname na sio server_hostname:
             ashiria ValueError("check_hostname requires server_hostname")

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
        self._closed = Uongo
        self._sslobj = Tupu
        self.server_side = server_side
        self.server_hostname = context._encode_hostname(server_hostname)
        self.do_handshake_on_connect = do_handshake_on_connect
        self.suppress_ragged_eofs = suppress_ragged_eofs

        # See ikiwa we are connected
        jaribu:
            self.getpeername()
        except OSError as e:
            ikiwa e.errno != errno.ENOTCONN:
                raise
            connected = Uongo
        isipokua:
            connected = Kweli

        self._connected = connected
        ikiwa connected:
            # create the SSL object
            jaribu:
                self._sslobj = self._context._wrap_socket(
                    self, server_side, self.server_hostname,
                    owner=self, session=self._session,
                )
                ikiwa do_handshake_on_connect:
                    timeout = self.gettimeout()
                    ikiwa timeout == 0.0:
                        # non-blocking
                         ashiria ValueError("do_handshake_on_connect should sio be specified kila non-blocking sockets")
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
        ikiwa self._sslobj ni sio Tupu:
            rudisha self._sslobj.session

    @session.setter
    eleza session(self, session):
        self._session = session
        ikiwa self._sslobj ni sio Tupu:
            self._sslobj.session = session

    @property
    @_sslcopydoc
    eleza session_reused(self):
        ikiwa self._sslobj ni sio Tupu:
            rudisha self._sslobj.session_reused

    eleza dup(self):
         ashiria NotImplementedError("Can't dup() %s instances" %
                                  self.__class__.__name__)

    eleza _checkClosed(self, msg=Tupu):
        #  ashiria an exception here ikiwa you wish to check kila spurious closes
        pass

    eleza _check_connected(self):
        ikiwa sio self._connected:
            # getpeername() will  ashiria ENOTCONN ikiwa the socket ni really
            # sio connected; note that we can be connected even without
            # _connected being set, e.g. ikiwa connect() first returned
            # EAGAIN.
            self.getpeername()

    eleza read(self, len=1024, buffer=Tupu):
        """Read up to LEN bytes na rudisha them.
        Return zero-length string on EOF."""

        self._checkClosed()
        ikiwa self._sslobj ni Tupu:
             ashiria ValueError("Read on closed ama unwrapped SSL socket.")
        jaribu:
            ikiwa buffer ni sio Tupu:
                rudisha self._sslobj.read(len, buffer)
            isipokua:
                rudisha self._sslobj.read(len)
        except SSLError as x:
            ikiwa x.args[0] == SSL_ERROR_EOF na self.suppress_ragged_eofs:
                ikiwa buffer ni sio Tupu:
                    rudisha 0
                isipokua:
                    rudisha b''
            isipokua:
                raise

    eleza write(self, data):
        """Write DATA to the underlying SSL channel.  Returns
        number of bytes of DATA actually transmitted."""

        self._checkClosed()
        ikiwa self._sslobj ni Tupu:
             ashiria ValueError("Write on closed ama unwrapped SSL socket.")
        rudisha self._sslobj.write(data)

    @_sslcopydoc
    eleza getpeercert(self, binary_form=Uongo):
        self._checkClosed()
        self._check_connected()
        rudisha self._sslobj.getpeercert(binary_form)

    @_sslcopydoc
    eleza selected_npn_protocol(self):
        self._checkClosed()
        ikiwa self._sslobj ni Tupu ama sio _ssl.HAS_NPN:
            rudisha Tupu
        isipokua:
            rudisha self._sslobj.selected_npn_protocol()

    @_sslcopydoc
    eleza selected_alpn_protocol(self):
        self._checkClosed()
        ikiwa self._sslobj ni Tupu ama sio _ssl.HAS_ALPN:
            rudisha Tupu
        isipokua:
            rudisha self._sslobj.selected_alpn_protocol()

    @_sslcopydoc
    eleza cipher(self):
        self._checkClosed()
        ikiwa self._sslobj ni Tupu:
            rudisha Tupu
        isipokua:
            rudisha self._sslobj.cipher()

    @_sslcopydoc
    eleza shared_ciphers(self):
        self._checkClosed()
        ikiwa self._sslobj ni Tupu:
            rudisha Tupu
        isipokua:
            rudisha self._sslobj.shared_ciphers()

    @_sslcopydoc
    eleza compression(self):
        self._checkClosed()
        ikiwa self._sslobj ni Tupu:
            rudisha Tupu
        isipokua:
            rudisha self._sslobj.compression()

    eleza send(self, data, flags=0):
        self._checkClosed()
        ikiwa self._sslobj ni sio Tupu:
            ikiwa flags != 0:
                 ashiria ValueError(
                    "non-zero flags sio allowed kwenye calls to send() on %s" %
                    self.__class__)
            rudisha self._sslobj.write(data)
        isipokua:
            rudisha super().send(data, flags)

    eleza sendto(self, data, flags_or_addr, addr=Tupu):
        self._checkClosed()
        ikiwa self._sslobj ni sio Tupu:
             ashiria ValueError("sendto sio allowed on instances of %s" %
                             self.__class__)
        elikiwa addr ni Tupu:
            rudisha super().sendto(data, flags_or_addr)
        isipokua:
            rudisha super().sendto(data, flags_or_addr, addr)

    eleza sendmsg(self, *args, **kwargs):
        # Ensure programs don't send data unencrypted ikiwa they try to
        # use this method.
         ashiria NotImplementedError("sendmsg sio allowed on instances of %s" %
                                  self.__class__)

    eleza sendall(self, data, flags=0):
        self._checkClosed()
        ikiwa self._sslobj ni sio Tupu:
            ikiwa flags != 0:
                 ashiria ValueError(
                    "non-zero flags sio allowed kwenye calls to sendall() on %s" %
                    self.__class__)
            count = 0
            ukijumuisha memoryview(data) as view, view.cast("B") as byte_view:
                amount = len(byte_view)
                wakati count < amount:
                    v = self.send(byte_view[count:])
                    count += v
        isipokua:
            rudisha super().sendall(data, flags)

    eleza sendfile(self, file, offset=0, count=Tupu):
        """Send a file, possibly by using os.sendfile() ikiwa this ni a
        clear-text socket.  Return the total number of bytes sent.
        """
        ikiwa self._sslobj ni sio Tupu:
            rudisha self._sendfile_use_send(file, offset, count)
        isipokua:
            # os.sendfile() works ukijumuisha plain sockets only
            rudisha super().sendfile(file, offset, count)

    eleza recv(self, buflen=1024, flags=0):
        self._checkClosed()
        ikiwa self._sslobj ni sio Tupu:
            ikiwa flags != 0:
                 ashiria ValueError(
                    "non-zero flags sio allowed kwenye calls to recv() on %s" %
                    self.__class__)
            rudisha self.read(buflen)
        isipokua:
            rudisha super().recv(buflen, flags)

    eleza recv_into(self, buffer, nbytes=Tupu, flags=0):
        self._checkClosed()
        ikiwa buffer na (nbytes ni Tupu):
            nbytes = len(buffer)
        elikiwa nbytes ni Tupu:
            nbytes = 1024
        ikiwa self._sslobj ni sio Tupu:
            ikiwa flags != 0:
                 ashiria ValueError(
                  "non-zero flags sio allowed kwenye calls to recv_into() on %s" %
                  self.__class__)
            rudisha self.read(nbytes, buffer)
        isipokua:
            rudisha super().recv_into(buffer, nbytes, flags)

    eleza recvfrom(self, buflen=1024, flags=0):
        self._checkClosed()
        ikiwa self._sslobj ni sio Tupu:
             ashiria ValueError("recvkutoka sio allowed on instances of %s" %
                             self.__class__)
        isipokua:
            rudisha super().recvfrom(buflen, flags)

    eleza recvfrom_into(self, buffer, nbytes=Tupu, flags=0):
        self._checkClosed()
        ikiwa self._sslobj ni sio Tupu:
             ashiria ValueError("recvfrom_into sio allowed on instances of %s" %
                             self.__class__)
        isipokua:
            rudisha super().recvfrom_into(buffer, nbytes, flags)

    eleza recvmsg(self, *args, **kwargs):
         ashiria NotImplementedError("recvmsg sio allowed on instances of %s" %
                                  self.__class__)

    eleza recvmsg_into(self, *args, **kwargs):
         ashiria NotImplementedError("recvmsg_into sio allowed on instances of "
                                  "%s" % self.__class__)

    @_sslcopydoc
    eleza pending(self):
        self._checkClosed()
        ikiwa self._sslobj ni sio Tupu:
            rudisha self._sslobj.pending()
        isipokua:
            rudisha 0

    eleza shutdown(self, how):
        self._checkClosed()
        self._sslobj = Tupu
        super().shutdown(how)

    @_sslcopydoc
    eleza unwrap(self):
        ikiwa self._sslobj:
            s = self._sslobj.shutdown()
            self._sslobj = Tupu
            rudisha s
        isipokua:
             ashiria ValueError("No SSL wrapper around " + str(self))

    @_sslcopydoc
    eleza verify_client_post_handshake(self):
        ikiwa self._sslobj:
            rudisha self._sslobj.verify_client_post_handshake()
        isipokua:
             ashiria ValueError("No SSL wrapper around " + str(self))

    eleza _real_close(self):
        self._sslobj = Tupu
        super()._real_close()

    @_sslcopydoc
    eleza do_handshake(self, block=Uongo):
        self._check_connected()
        timeout = self.gettimeout()
        jaribu:
            ikiwa timeout == 0.0 na block:
                self.settimeout(Tupu)
            self._sslobj.do_handshake()
        mwishowe:
            self.settimeout(timeout)

    eleza _real_connect(self, addr, connect_ex):
        ikiwa self.server_side:
             ashiria ValueError("can't connect kwenye server-side mode")
        # Here we assume that the socket ni client-side, na not
        # connected at the time of the call.  We connect it, then wrap it.
        ikiwa self._connected ama self._sslobj ni sio Tupu:
             ashiria ValueError("attempt to connect already-connected SSLSocket!")
        self._sslobj = self.context._wrap_socket(
            self, Uongo, self.server_hostname,
            owner=self, session=self._session
        )
        jaribu:
            ikiwa connect_ex:
                rc = super().connect_ex(addr)
            isipokua:
                rc = Tupu
                super().connect(addr)
            ikiwa sio rc:
                self._connected = Kweli
                ikiwa self.do_handshake_on_connect:
                    self.do_handshake()
            rudisha rc
        except (OSError, ValueError):
            self._sslobj = Tupu
            raise

    eleza connect(self, addr):
        """Connects to remote ADDR, na then wraps the connection in
        an SSL channel."""
        self._real_connect(addr, Uongo)

    eleza connect_ex(self, addr):
        """Connects to remote ADDR, na then wraps the connection in
        an SSL channel."""
        rudisha self._real_connect(addr, Kweli)

    eleza accept(self):
        """Accepts a new connection kutoka a remote client, na returns
        a tuple containing that new connection wrapped ukijumuisha a server-side
        SSL channel, na the address of the remote client."""

        newsock, addr = super().accept()
        newsock = self.context.wrap_socket(newsock,
                    do_handshake_on_connect=self.do_handshake_on_connect,
                    suppress_ragged_eofs=self.suppress_ragged_eofs,
                    server_side=Kweli)
        rudisha newsock, addr

    @_sslcopydoc
    eleza get_channel_binding(self, cb_type="tls-unique"):
        ikiwa self._sslobj ni sio Tupu:
            rudisha self._sslobj.get_channel_binding(cb_type)
        isipokua:
            ikiwa cb_type sio kwenye CHANNEL_BINDING_TYPES:
                 ashiria ValueError(
                    "{0} channel binding type sio implemented".format(cb_type)
                )
            rudisha Tupu

    @_sslcopydoc
    eleza version(self):
        ikiwa self._sslobj ni sio Tupu:
            rudisha self._sslobj.version()
        isipokua:
            rudisha Tupu


# Python does sio support forward declaration of types.
SSLContext.sslsocket_kundi = SSLSocket
SSLContext.sslobject_kundi = SSLObject


eleza wrap_socket(sock, keyfile=Tupu, certfile=Tupu,
                server_side=Uongo, cert_reqs=CERT_NONE,
                ssl_version=PROTOCOL_TLS, ca_certs=Tupu,
                do_handshake_on_connect=Kweli,
                suppress_ragged_eofs=Kweli,
                ciphers=Tupu):

    ikiwa server_side na sio certfile:
         ashiria ValueError("certfile must be specified kila server-side "
                         "operations")
    ikiwa keyfile na sio certfile:
         ashiria ValueError("certfile must be specified")
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
    """Return the time kwenye seconds since the Epoch, given the timestring
    representing the "notBefore" ama "notAfter" date kutoka a certificate
    kwenye ``"%b %d %H:%M:%S %Y %Z"`` strptime format (C locale).

    "notBefore" ama "notAfter" dates must use UTC (RFC 5280).

    Month ni one of: Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
    UTC should be specified as GMT (see ASN1_TIME_andika())
    """
    kutoka time agiza strptime
    kutoka calendar agiza timegm

    months = (
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    )
    time_format = ' %d %H:%M:%S %Y GMT' # NOTE: no month, fixed GMT
    jaribu:
        month_number = months.index(cert_time[:3].title()) + 1
    except ValueError:
         ashiria ValueError('time data %r does sio match '
                         'format "%%b%s"' % (cert_time, time_format))
    isipokua:
        # found valid month
        tt = strptime(cert_time[3:], time_format)
        # rudisha an integer, the previous mktime()-based implementation
        # returned a float (fractional seconds are always zero here).
        rudisha timegm((tt[0], month_number) + tt[2:6])

PEM_HEADER = "-----BEGIN CERTIFICATE-----"
PEM_FOOTER = "-----END CERTIFICATE-----"

eleza DER_cert_to_PEM_cert(der_cert_bytes):
    """Takes a certificate kwenye binary DER format na returns the
    PEM version of it as a string."""

    f = str(base64.standard_b64encode(der_cert_bytes), 'ASCII', 'strict')
    ss = [PEM_HEADER]
    ss += [f[i:i+64] kila i kwenye range(0, len(f), 64)]
    ss.append(PEM_FOOTER + '\n')
    rudisha '\n'.join(ss)

eleza PEM_cert_to_DER_cert(pem_cert_string):
    """Takes a certificate kwenye ASCII PEM format na returns the
    DER-encoded version of it as a byte sequence"""

    ikiwa sio pem_cert_string.startswith(PEM_HEADER):
         ashiria ValueError("Invalid PEM encoding; must start ukijumuisha %s"
                         % PEM_HEADER)
    ikiwa sio pem_cert_string.strip().endswith(PEM_FOOTER):
         ashiria ValueError("Invalid PEM encoding; must end ukijumuisha %s"
                         % PEM_FOOTER)
    d = pem_cert_string.strip()[len(PEM_HEADER):-len(PEM_FOOTER)]
    rudisha base64.decodebytes(d.encode('ASCII', 'strict'))

eleza get_server_certificate(addr, ssl_version=PROTOCOL_TLS, ca_certs=Tupu):
    """Retrieve the certificate kutoka the server at the specified address,
    na rudisha it as a PEM-encoded string.
    If 'ca_certs' ni specified, validate the server cert against it.
    If 'ssl_version' ni specified, use it kwenye the connection attempt."""

    host, port = addr
    ikiwa ca_certs ni sio Tupu:
        cert_reqs = CERT_REQUIRED
    isipokua:
        cert_reqs = CERT_NONE
    context = _create_stdlib_context(ssl_version,
                                     cert_reqs=cert_reqs,
                                     cafile=ca_certs)
    ukijumuisha  create_connection(addr) as sock:
        ukijumuisha context.wrap_socket(sock) as sslsock:
            dercert = sslsock.getpeercert(Kweli)
    rudisha DER_cert_to_PEM_cert(dercert)

eleza get_protocol_name(protocol_code):
    rudisha _PROTOCOL_NAMES.get(protocol_code, '<unknown>')
