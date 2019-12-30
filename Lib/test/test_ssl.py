# Test the support kila SSL na sockets

agiza sys
agiza unittest
agiza unittest.mock
kutoka test agiza support
agiza socket
agiza select
agiza time
agiza datetime
agiza gc
agiza os
agiza errno
agiza pprint
agiza urllib.request
agiza threading
agiza traceback
agiza asyncore
agiza weakref
agiza platform
agiza sysconfig
agiza functools
jaribu:
    agiza ctypes
tatizo ImportError:
    ctypes = Tupu

ssl = support.import_module("ssl")

kutoka ssl agiza TLSVersion, _TLSContentType, _TLSMessageType

PROTOCOLS = sorted(ssl._PROTOCOL_NAMES)
HOST = support.HOST
IS_LIBRESSL = ssl.OPENSSL_VERSION.startswith('LibreSSL')
IS_OPENSSL_1_1_0 = sio IS_LIBRESSL na ssl.OPENSSL_VERSION_INFO >= (1, 1, 0)
IS_OPENSSL_1_1_1 = sio IS_LIBRESSL na ssl.OPENSSL_VERSION_INFO >= (1, 1, 1)
PY_SSL_DEFAULT_CIPHERS = sysconfig.get_config_var('PY_SSL_DEFAULT_CIPHERS')

PROTOCOL_TO_TLS_VERSION = {}
kila proto, ver kwenye (
    ("PROTOCOL_SSLv23", "SSLv3"),
    ("PROTOCOL_TLSv1", "TLSv1"),
    ("PROTOCOL_TLSv1_1", "TLSv1_1"),
):
    jaribu:
        proto = getattr(ssl, proto)
        ver = getattr(ssl.TLSVersion, ver)
    tatizo AttributeError:
        endelea
    PROTOCOL_TO_TLS_VERSION[proto] = ver

eleza data_file(*name):
    rudisha os.path.join(os.path.dirname(__file__), *name)

# The custom key na certificate files used kwenye test_ssl are generated
# using Lib/test/make_ssl_certs.py.
# Other certificates are simply fetched kutoka the Internet servers they
# are meant to authenticate.

CERTFILE = data_file("keycert.pem")
BYTES_CERTFILE = os.fsencode(CERTFILE)
ONLYCERT = data_file("ssl_cert.pem")
ONLYKEY = data_file("ssl_key.pem")
BYTES_ONLYCERT = os.fsencode(ONLYCERT)
BYTES_ONLYKEY = os.fsencode(ONLYKEY)
CERTFILE_PROTECTED = data_file("keycert.pitawd.pem")
ONLYKEY_PROTECTED = data_file("ssl_key.pitawd.pem")
KEY_PASSWORD = "somepita"
CAPATH = data_file("capath")
BYTES_CAPATH = os.fsencode(CAPATH)
CAFILE_NEURONIO = data_file("capath", "4e1295a3.0")
CAFILE_CACERT = data_file("capath", "5ed36f99.0")

CERTFILE_INFO = {
    'issuer': ((('countryName', 'XY'),),
               (('localityName', 'Castle Anthrax'),),
               (('organizationName', 'Python Software Foundation'),),
               (('commonName', 'localhost'),)),
    'notAfter': 'Aug 26 14:23:15 2028 GMT',
    'notBefore': 'Aug 29 14:23:15 2018 GMT',
    'serialNumber': '98A7CF88C74A32ED',
    'subject': ((('countryName', 'XY'),),
             (('localityName', 'Castle Anthrax'),),
             (('organizationName', 'Python Software Foundation'),),
             (('commonName', 'localhost'),)),
    'subjectAltName': (('DNS', 'localhost'),),
    'version': 3
}

# empty CRL
CRLFILE = data_file("revocation.crl")

# Two keys na certs signed by the same CA (kila SNI tests)
SIGNED_CERTFILE = data_file("keycert3.pem")
SIGNED_CERTFILE_HOSTNAME = 'localhost'

SIGNED_CERTFILE_INFO = {
    'OCSP': ('http://testca.pythontest.net/testca/ocsp/',),
    'caIssuers': ('http://testca.pythontest.net/testca/pycacert.cer',),
    'crlDistributionPoints': ('http://testca.pythontest.net/testca/revocation.crl',),
    'issuer': ((('countryName', 'XY'),),
            (('organizationName', 'Python Software Foundation CA'),),
            (('commonName', 'our-ca-server'),)),
    'notAfter': 'Jul  7 14:23:16 2028 GMT',
    'notBefore': 'Aug 29 14:23:16 2018 GMT',
    'serialNumber': 'CB2D80995A69525C',
    'subject': ((('countryName', 'XY'),),
             (('localityName', 'Castle Anthrax'),),
             (('organizationName', 'Python Software Foundation'),),
             (('commonName', 'localhost'),)),
    'subjectAltName': (('DNS', 'localhost'),),
    'version': 3
}

SIGNED_CERTFILE2 = data_file("keycert4.pem")
SIGNED_CERTFILE2_HOSTNAME = 'fakehostname'
SIGNED_CERTFILE_ECC = data_file("keycertecc.pem")
SIGNED_CERTFILE_ECC_HOSTNAME = 'localhost-ecc'

# Same certificate kama pycacert.pem, but without extra text kwenye file
SIGNING_CA = data_file("capath", "ceff1710.0")
# cert ukijumuisha all kinds of subject alt names
ALLSANFILE = data_file("allsans.pem")
IDNSANSFILE = data_file("idnsans.pem")

REMOTE_HOST = "self-signed.pythontest.net"

EMPTYCERT = data_file("nullcert.pem")
BADCERT = data_file("badcert.pem")
NONEXISTINGCERT = data_file("XXXnonexisting.pem")
BADKEY = data_file("badkey.pem")
NOKIACERT = data_file("nokia.pem")
NULLBYTECERT = data_file("nullbytecert.pem")
TALOS_INVALID_CRLDP = data_file("talos-2019-0758.pem")

DHFILE = data_file("ffdh3072.pem")
BYTES_DHFILE = os.fsencode(DHFILE)

# Not defined kwenye all versions of OpenSSL
OP_NO_COMPRESSION = getattr(ssl, "OP_NO_COMPRESSION", 0)
OP_SINGLE_DH_USE = getattr(ssl, "OP_SINGLE_DH_USE", 0)
OP_SINGLE_ECDH_USE = getattr(ssl, "OP_SINGLE_ECDH_USE", 0)
OP_CIPHER_SERVER_PREFERENCE = getattr(ssl, "OP_CIPHER_SERVER_PREFERENCE", 0)
OP_ENABLE_MIDDLEBOX_COMPAT = getattr(ssl, "OP_ENABLE_MIDDLEBOX_COMPAT", 0)


eleza has_tls_protocol(protocol):
    """Check ikiwa a TLS protocol ni available na enabled

    :param protocol: enum ssl._SSLMethod member ama name
    :return: bool
    """
    ikiwa isinstance(protocol, str):
        assert protocol.startswith('PROTOCOL_')
        protocol = getattr(ssl, protocol, Tupu)
        ikiwa protocol ni Tupu:
            rudisha Uongo
    ikiwa protocol kwenye {
        ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLS_SERVER,
        ssl.PROTOCOL_TLS_CLIENT
    }:
        # auto-negotiate protocols are always available
        rudisha Kweli
    name = protocol.name
    rudisha has_tls_version(name[len('PROTOCOL_'):])


@functools.lru_cache
eleza has_tls_version(version):
    """Check ikiwa a TLS/SSL version ni enabled

    :param version: TLS version name ama ssl.TLSVersion member
    :return: bool
    """
    ikiwa version == "SSLv2":
        # never supported na sio even kwenye TLSVersion enum
        rudisha Uongo

    ikiwa isinstance(version, str):
        version = ssl.TLSVersion.__members__[version]

    # check compile time flags like ssl.HAS_TLSv1_2
    ikiwa sio getattr(ssl, f'HAS_{version.name}'):
        rudisha Uongo

    # check runtime na dynamic crypto policy settings. A TLS version may
    # be compiled kwenye but disabled by a policy ama config option.
    ctx = ssl.SSLContext()
    ikiwa (
            hasattr(ctx, 'minimum_version') na
            ctx.minimum_version != ssl.TLSVersion.MINIMUM_SUPPORTED na
            version < ctx.minimum_version
    ):
        rudisha Uongo
    ikiwa (
        hasattr(ctx, 'maximum_version') na
        ctx.maximum_version != ssl.TLSVersion.MAXIMUM_SUPPORTED na
        version > ctx.maximum_version
    ):
        rudisha Uongo

    rudisha Kweli


eleza requires_tls_version(version):
    """Decorator to skip tests when a required TLS version ni sio available

    :param version: TLS version name ama ssl.TLSVersion member
    :return:
    """
    eleza decorator(func):
        @functools.wraps(func)
        eleza wrapper(*args, **kw):
            ikiwa sio has_tls_version(version):
                ashiria unittest.SkipTest(f"{version} ni sio available.")
            isipokua:
                rudisha func(*args, **kw)
        rudisha wrapper
    rudisha decorator


requires_minimum_version = unittest.skipUnless(
    hasattr(ssl.SSLContext, 'minimum_version'),
    "required OpenSSL >= 1.1.0g"
)


eleza handle_error(prefix):
    exc_format = ' '.join(traceback.format_exception(*sys.exc_info()))
    ikiwa support.verbose:
        sys.stdout.write(prefix + exc_format)

eleza can_clear_options():
    # 0.9.8m ama higher
    rudisha ssl._OPENSSL_API_VERSION >= (0, 9, 8, 13, 15)

eleza no_sslv2_implies_sslv3_hello():
    # 0.9.7h ama higher
    rudisha ssl.OPENSSL_VERSION_INFO >= (0, 9, 7, 8, 15)

eleza have_verify_flags():
    # 0.9.8 ama higher
    rudisha ssl.OPENSSL_VERSION_INFO >= (0, 9, 8, 0, 15)

eleza _have_secp_curves():
    ikiwa sio ssl.HAS_ECDH:
        rudisha Uongo
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    jaribu:
        ctx.set_ecdh_curve("secp384r1")
    tatizo ValueError:
        rudisha Uongo
    isipokua:
        rudisha Kweli


HAVE_SECP_CURVES = _have_secp_curves()


eleza utc_offset(): #NOTE: ignore issues like #1647654
    # local time = utc time + utc offset
    ikiwa time.daylight na time.localtime().tm_isdst > 0:
        rudisha -time.altzone  # seconds
    rudisha -time.timezone

eleza asn1time(cert_time):
    # Some versions of OpenSSL ignore seconds, see #18207
    # 0.9.8.i
    ikiwa ssl._OPENSSL_API_VERSION == (0, 9, 8, 9, 15):
        fmt = "%b %d %H:%M:%S %Y GMT"
        dt = datetime.datetime.strptime(cert_time, fmt)
        dt = dt.replace(second=0)
        cert_time = dt.strftime(fmt)
        # %d adds leading zero but ASN1_TIME_andika() uses leading space
        ikiwa cert_time[4] == "0":
            cert_time = cert_time[:4] + " " + cert_time[5:]

    rudisha cert_time

needs_sni = unittest.skipUnless(ssl.HAS_SNI, "SNI support needed kila this test")


eleza test_wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS, *,
                     cert_reqs=ssl.CERT_NONE, ca_certs=Tupu,
                     ciphers=Tupu, certfile=Tupu, keyfile=Tupu,
                     **kwargs):
    context = ssl.SSLContext(ssl_version)
    ikiwa cert_reqs ni sio Tupu:
        ikiwa cert_reqs == ssl.CERT_NONE:
            context.check_hostname = Uongo
        context.verify_mode = cert_reqs
    ikiwa ca_certs ni sio Tupu:
        context.load_verify_locations(ca_certs)
    ikiwa certfile ni sio Tupu ama keyfile ni sio Tupu:
        context.load_cert_chain(certfile, keyfile)
    ikiwa ciphers ni sio Tupu:
        context.set_ciphers(ciphers)
    rudisha context.wrap_socket(sock, **kwargs)


eleza testing_context(server_cert=SIGNED_CERTFILE):
    """Create context

    client_context, server_context, hostname = testing_context()
    """
    ikiwa server_cert == SIGNED_CERTFILE:
        hostname = SIGNED_CERTFILE_HOSTNAME
    lasivyo server_cert == SIGNED_CERTFILE2:
        hostname = SIGNED_CERTFILE2_HOSTNAME
    isipokua:
        ashiria ValueError(server_cert)

    client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client_context.load_verify_locations(SIGNING_CA)

    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(server_cert)
    server_context.load_verify_locations(SIGNING_CA)

    rudisha client_context, server_context, hostname


kundi BasicSocketTests(unittest.TestCase):

    eleza test_constants(self):
        ssl.CERT_NONE
        ssl.CERT_OPTIONAL
        ssl.CERT_REQUIRED
        ssl.OP_CIPHER_SERVER_PREFERENCE
        ssl.OP_SINGLE_DH_USE
        ikiwa ssl.HAS_ECDH:
            ssl.OP_SINGLE_ECDH_USE
        ikiwa ssl.OPENSSL_VERSION_INFO >= (1, 0):
            ssl.OP_NO_COMPRESSION
        self.assertIn(ssl.HAS_SNI, {Kweli, Uongo})
        self.assertIn(ssl.HAS_ECDH, {Kweli, Uongo})
        ssl.OP_NO_SSLv2
        ssl.OP_NO_SSLv3
        ssl.OP_NO_TLSv1
        ssl.OP_NO_TLSv1_3
        ikiwa ssl.OPENSSL_VERSION_INFO >= (1, 0, 1):
            ssl.OP_NO_TLSv1_1
            ssl.OP_NO_TLSv1_2
        self.assertEqual(ssl.PROTOCOL_TLS, ssl.PROTOCOL_SSLv23)

    eleza test_private_init(self):
        ukijumuisha self.assertRaisesRegex(TypeError, "public constructor"):
            ukijumuisha socket.socket() kama s:
                ssl.SSLSocket(s)

    eleza test_str_for_enums(self):
        # Make sure that the PROTOCOL_* constants have enum-like string
        # reprs.
        proto = ssl.PROTOCOL_TLS
        self.assertEqual(str(proto), '_SSLMethod.PROTOCOL_TLS')
        ctx = ssl.SSLContext(proto)
        self.assertIs(ctx.protocol, proto)

    eleza test_random(self):
        v = ssl.RAND_status()
        ikiwa support.verbose:
            sys.stdout.write("\n RAND_status ni %d (%s)\n"
                             % (v, (v na "sufficient randomness") ama
                                "insufficient randomness"))

        data, is_cryptographic = ssl.RAND_pseudo_bytes(16)
        self.assertEqual(len(data), 16)
        self.assertEqual(is_cryptographic, v == 1)
        ikiwa v:
            data = ssl.RAND_bytes(16)
            self.assertEqual(len(data), 16)
        isipokua:
            self.assertRaises(ssl.SSLError, ssl.RAND_bytes, 16)

        # negative num ni invalid
        self.assertRaises(ValueError, ssl.RAND_bytes, -5)
        self.assertRaises(ValueError, ssl.RAND_pseudo_bytes, -5)

        ikiwa hasattr(ssl, 'RAND_egd'):
            self.assertRaises(TypeError, ssl.RAND_egd, 1)
            self.assertRaises(TypeError, ssl.RAND_egd, 'foo', 1)
        ssl.RAND_add("this ni a random string", 75.0)
        ssl.RAND_add(b"this ni a random bytes object", 75.0)
        ssl.RAND_add(bytearray(b"this ni a random bytearray object"), 75.0)

    @unittest.skipUnless(os.name == 'posix', 'requires posix')
    eleza test_random_fork(self):
        status = ssl.RAND_status()
        ikiwa sio status:
            self.fail("OpenSSL's PRNG has insufficient randomness")

        rfd, wfd = os.pipe()
        pid = os.fork()
        ikiwa pid == 0:
            jaribu:
                os.close(rfd)
                child_random = ssl.RAND_pseudo_bytes(16)[0]
                self.assertEqual(len(child_random), 16)
                os.write(wfd, child_random)
                os.close(wfd)
            tatizo BaseException:
                os._exit(1)
            isipokua:
                os._exit(0)
        isipokua:
            os.close(wfd)
            self.addCleanup(os.close, rfd)
            _, status = os.waitpid(pid, 0)
            self.assertEqual(status, 0)

            child_random = os.read(rfd, 16)
            self.assertEqual(len(child_random), 16)
            parent_random = ssl.RAND_pseudo_bytes(16)[0]
            self.assertEqual(len(parent_random), 16)

            self.assertNotEqual(child_random, parent_random)

    maxDiff = Tupu

    eleza test_parse_cert(self):
        # note that this uses an 'unofficial' function kwenye _ssl.c,
        # provided solely kila this test, to exercise the certificate
        # parsing code
        self.assertEqual(
            ssl._ssl._test_decode_cert(CERTFILE),
            CERTFILE_INFO
        )
        self.assertEqual(
            ssl._ssl._test_decode_cert(SIGNED_CERTFILE),
            SIGNED_CERTFILE_INFO
        )

        # Issue #13034: the subjectAltName kwenye some certificates
        # (notably projects.developer.nokia.com:443) wasn't parsed
        p = ssl._ssl._test_decode_cert(NOKIACERT)
        ikiwa support.verbose:
            sys.stdout.write("\n" + pprint.pformat(p) + "\n")
        self.assertEqual(p['subjectAltName'],
                         (('DNS', 'projects.developer.nokia.com'),
                          ('DNS', 'projects.forum.nokia.com'))
                        )
        # extra OCSP na AIA fields
        self.assertEqual(p['OCSP'], ('http://ocsp.verisign.com',))
        self.assertEqual(p['caIssuers'],
                         ('http://SVRIntl-G3-aia.verisign.com/SVRIntlG3.cer',))
        self.assertEqual(p['crlDistributionPoints'],
                         ('http://SVRIntl-G3-crl.verisign.com/SVRIntlG3.crl',))

    eleza test_parse_cert_CVE_2019_5010(self):
        p = ssl._ssl._test_decode_cert(TALOS_INVALID_CRLDP)
        ikiwa support.verbose:
            sys.stdout.write("\n" + pprint.pformat(p) + "\n")
        self.assertEqual(
            p,
            {
                'issuer': (
                    (('countryName', 'UK'),), (('commonName', 'cody-ca'),)),
                'notAfter': 'Jun 14 18:00:58 2028 GMT',
                'notBefore': 'Jun 18 18:00:58 2018 GMT',
                'serialNumber': '02',
                'subject': ((('countryName', 'UK'),),
                            (('commonName',
                              'codenomicon-vm-2.test.lal.cisco.com'),)),
                'subjectAltName': (
                    ('DNS', 'codenomicon-vm-2.test.lal.cisco.com'),),
                'version': 3
            }
        )

    eleza test_parse_cert_CVE_2013_4238(self):
        p = ssl._ssl._test_decode_cert(NULLBYTECERT)
        ikiwa support.verbose:
            sys.stdout.write("\n" + pprint.pformat(p) + "\n")
        subject = ((('countryName', 'US'),),
                   (('stateOrProvinceName', 'Oregon'),),
                   (('localityName', 'Beaverton'),),
                   (('organizationName', 'Python Software Foundation'),),
                   (('organizationalUnitName', 'Python Core Development'),),
                   (('commonName', 'null.python.org\x00example.org'),),
                   (('emailAddress', 'python-dev@python.org'),))
        self.assertEqual(p['subject'], subject)
        self.assertEqual(p['issuer'], subject)
        ikiwa ssl._OPENSSL_API_VERSION >= (0, 9, 8):
            san = (('DNS', 'altnull.python.org\x00example.com'),
                   ('email', 'null@python.org\x00user@example.org'),
                   ('URI', 'http://null.python.org\x00http://example.org'),
                   ('IP Address', '192.0.2.1'),
                   ('IP Address', '2001:DB8:0:0:0:0:0:1\n'))
        isipokua:
            # OpenSSL 0.9.7 doesn't support IPv6 addresses kwenye subjectAltName
            san = (('DNS', 'altnull.python.org\x00example.com'),
                   ('email', 'null@python.org\x00user@example.org'),
                   ('URI', 'http://null.python.org\x00http://example.org'),
                   ('IP Address', '192.0.2.1'),
                   ('IP Address', '<invalid>'))

        self.assertEqual(p['subjectAltName'], san)

    eleza test_parse_all_sans(self):
        p = ssl._ssl._test_decode_cert(ALLSANFILE)
        self.assertEqual(p['subjectAltName'],
            (
                ('DNS', 'allsans'),
                ('othername', '<unsupported>'),
                ('othername', '<unsupported>'),
                ('email', 'user@example.org'),
                ('DNS', 'www.example.org'),
                ('DirName',
                    ((('countryName', 'XY'),),
                    (('localityName', 'Castle Anthrax'),),
                    (('organizationName', 'Python Software Foundation'),),
                    (('commonName', 'dirname example'),))),
                ('URI', 'https://www.python.org/'),
                ('IP Address', '127.0.0.1'),
                ('IP Address', '0:0:0:0:0:0:0:1\n'),
                ('Registered ID', '1.2.3.4.5')
            )
        )

    eleza test_DER_to_PEM(self):
        ukijumuisha open(CAFILE_CACERT, 'r') kama f:
            pem = f.read()
        d1 = ssl.PEM_cert_to_DER_cert(pem)
        p2 = ssl.DER_cert_to_PEM_cert(d1)
        d2 = ssl.PEM_cert_to_DER_cert(p2)
        self.assertEqual(d1, d2)
        ikiwa sio p2.startswith(ssl.PEM_HEADER + '\n'):
            self.fail("DER-to-PEM didn't include correct header:\n%r\n" % p2)
        ikiwa sio p2.endswith('\n' + ssl.PEM_FOOTER + '\n'):
            self.fail("DER-to-PEM didn't include correct footer:\n%r\n" % p2)

    eleza test_openssl_version(self):
        n = ssl.OPENSSL_VERSION_NUMBER
        t = ssl.OPENSSL_VERSION_INFO
        s = ssl.OPENSSL_VERSION
        self.assertIsInstance(n, int)
        self.assertIsInstance(t, tuple)
        self.assertIsInstance(s, str)
        # Some sanity checks follow
        # >= 0.9
        self.assertGreaterEqual(n, 0x900000)
        # < 3.0
        self.assertLess(n, 0x30000000)
        major, minor, fix, patch, status = t
        self.assertGreaterEqual(major, 0)
        self.assertLess(major, 3)
        self.assertGreaterEqual(minor, 0)
        self.assertLess(minor, 256)
        self.assertGreaterEqual(fix, 0)
        self.assertLess(fix, 256)
        self.assertGreaterEqual(patch, 0)
        self.assertLessEqual(patch, 63)
        self.assertGreaterEqual(status, 0)
        self.assertLessEqual(status, 15)
        # Version string kama returned by {Open,Libre}SSL, the format might change
        ikiwa IS_LIBRESSL:
            self.assertKweli(s.startswith("LibreSSL {:d}".format(major)),
                            (s, t, hex(n)))
        isipokua:
            self.assertKweli(s.startswith("OpenSSL {:d}.{:d}.{:d}".format(major, minor, fix)),
                            (s, t, hex(n)))

    @support.cpython_only
    eleza test_refcycle(self):
        # Issue #7943: an SSL object doesn't create reference cycles with
        # itself.
        s = socket.socket(socket.AF_INET)
        ss = test_wrap_socket(s)
        wr = weakref.ref(ss)
        ukijumuisha support.check_warnings(("", ResourceWarning)):
            toa ss
        self.assertEqual(wr(), Tupu)

    eleza test_wrapped_unconnected(self):
        # Methods on an unconnected SSLSocket propagate the original
        # OSError ashiria by the underlying socket object.
        s = socket.socket(socket.AF_INET)
        ukijumuisha test_wrap_socket(s) kama ss:
            self.assertRaises(OSError, ss.recv, 1)
            self.assertRaises(OSError, ss.recv_into, bytearray(b'x'))
            self.assertRaises(OSError, ss.recvfrom, 1)
            self.assertRaises(OSError, ss.recvfrom_into, bytearray(b'x'), 1)
            self.assertRaises(OSError, ss.send, b'x')
            self.assertRaises(OSError, ss.sendto, b'x', ('0.0.0.0', 0))
            self.assertRaises(NotImplementedError, ss.dup)
            self.assertRaises(NotImplementedError, ss.sendmsg,
                              [b'x'], (), 0, ('0.0.0.0', 0))
            self.assertRaises(NotImplementedError, ss.recvmsg, 100)
            self.assertRaises(NotImplementedError, ss.recvmsg_into,
                              [bytearray(100)])

    eleza test_timeout(self):
        # Issue #8524: when creating an SSL socket, the timeout of the
        # original socket should be retained.
        kila timeout kwenye (Tupu, 0.0, 5.0):
            s = socket.socket(socket.AF_INET)
            s.settimeout(timeout)
            ukijumuisha test_wrap_socket(s) kama ss:
                self.assertEqual(timeout, ss.gettimeout())

    eleza test_errors_sslwrap(self):
        sock = socket.socket()
        self.assertRaisesRegex(ValueError,
                        "certfile must be specified",
                        ssl.wrap_socket, sock, keyfile=CERTFILE)
        self.assertRaisesRegex(ValueError,
                        "certfile must be specified kila server-side operations",
                        ssl.wrap_socket, sock, server_side=Kweli)
        self.assertRaisesRegex(ValueError,
                        "certfile must be specified kila server-side operations",
                         ssl.wrap_socket, sock, server_side=Kweli, certfile="")
        ukijumuisha ssl.wrap_socket(sock, server_side=Kweli, certfile=CERTFILE) kama s:
            self.assertRaisesRegex(ValueError, "can't connect kwenye server-side mode",
                                     s.connect, (HOST, 8080))
        ukijumuisha self.assertRaises(OSError) kama cm:
            ukijumuisha socket.socket() kama sock:
                ssl.wrap_socket(sock, certfile=NONEXISTINGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        ukijumuisha self.assertRaises(OSError) kama cm:
            ukijumuisha socket.socket() kama sock:
                ssl.wrap_socket(sock,
                    certfile=CERTFILE, keyfile=NONEXISTINGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        ukijumuisha self.assertRaises(OSError) kama cm:
            ukijumuisha socket.socket() kama sock:
                ssl.wrap_socket(sock,
                    certfile=NONEXISTINGCERT, keyfile=NONEXISTINGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    eleza bad_cert_test(self, certfile):
        """Check that trying to use the given client certificate fails"""
        certfile = os.path.join(os.path.dirname(__file__) ama os.curdir,
                                   certfile)
        sock = socket.socket()
        self.addCleanup(sock.close)
        ukijumuisha self.assertRaises(ssl.SSLError):
            test_wrap_socket(sock,
                             certfile=certfile)

    eleza test_empty_cert(self):
        """Wrapping ukijumuisha an empty cert file"""
        self.bad_cert_test("nullcert.pem")

    eleza test_malformed_cert(self):
        """Wrapping ukijumuisha a badly formatted certificate (syntax error)"""
        self.bad_cert_test("badcert.pem")

    eleza test_malformed_key(self):
        """Wrapping ukijumuisha a badly formatted key (syntax error)"""
        self.bad_cert_test("badkey.pem")

    eleza test_match_hostname(self):
        eleza ok(cert, hostname):
            ssl.match_hostname(cert, hostname)
        eleza fail(cert, hostname):
            self.assertRaises(ssl.CertificateError,
                              ssl.match_hostname, cert, hostname)

        # -- Hostname matching --

        cert = {'subject': ((('commonName', 'example.com'),),)}
        ok(cert, 'example.com')
        ok(cert, 'ExAmple.cOm')
        fail(cert, 'www.example.com')
        fail(cert, '.example.com')
        fail(cert, 'example.org')
        fail(cert, 'exampleXcom')

        cert = {'subject': ((('commonName', '*.a.com'),),)}
        ok(cert, 'foo.a.com')
        fail(cert, 'bar.foo.a.com')
        fail(cert, 'a.com')
        fail(cert, 'Xa.com')
        fail(cert, '.a.com')

        # only match wildcards when they are the only thing
        # kwenye left-most segment
        cert = {'subject': ((('commonName', 'f*.com'),),)}
        fail(cert, 'foo.com')
        fail(cert, 'f.com')
        fail(cert, 'bar.com')
        fail(cert, 'foo.a.com')
        fail(cert, 'bar.foo.com')

        # NULL bytes are bad, CVE-2013-4073
        cert = {'subject': ((('commonName',
                              'null.python.org\x00example.org'),),)}
        ok(cert, 'null.python.org\x00example.org') # ama ashiria an error?
        fail(cert, 'example.org')
        fail(cert, 'null.python.org')

        # error cases ukijumuisha wildcards
        cert = {'subject': ((('commonName', '*.*.a.com'),),)}
        fail(cert, 'bar.foo.a.com')
        fail(cert, 'a.com')
        fail(cert, 'Xa.com')
        fail(cert, '.a.com')

        cert = {'subject': ((('commonName', 'a.*.com'),),)}
        fail(cert, 'a.foo.com')
        fail(cert, 'a..com')
        fail(cert, 'a.com')

        # wildcard doesn't match IDNA prefix 'xn--'
        idna = 'püthon.python.org'.encode("idna").decode("ascii")
        cert = {'subject': ((('commonName', idna),),)}
        ok(cert, idna)
        cert = {'subject': ((('commonName', 'x*.python.org'),),)}
        fail(cert, idna)
        cert = {'subject': ((('commonName', 'xn--p*.python.org'),),)}
        fail(cert, idna)

        # wildcard kwenye first fragment na  IDNA A-labels kwenye sequent fragments
        # are supported.
        idna = 'www*.pythön.org'.encode("idna").decode("ascii")
        cert = {'subject': ((('commonName', idna),),)}
        fail(cert, 'www.pythön.org'.encode("idna").decode("ascii"))
        fail(cert, 'www1.pythön.org'.encode("idna").decode("ascii"))
        fail(cert, 'ftp.pythön.org'.encode("idna").decode("ascii"))
        fail(cert, 'pythön.org'.encode("idna").decode("ascii"))

        # Slightly fake real-world example
        cert = {'notAfter': 'Jun 26 21:41:46 2011 GMT',
                'subject': ((('commonName', 'linuxfrz.org'),),),
                'subjectAltName': (('DNS', 'linuxfr.org'),
                                   ('DNS', 'linuxfr.com'),
                                   ('othername', '<unsupported>'))}
        ok(cert, 'linuxfr.org')
        ok(cert, 'linuxfr.com')
        # Not a "DNS" entry
        fail(cert, '<unsupported>')
        # When there ni a subjectAltName, commonName isn't used
        fail(cert, 'linuxfrz.org')

        # A pristine real-world example
        cert = {'notAfter': 'Dec 18 23:59:59 2011 GMT',
                'subject': ((('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'Mountain View'),),
                            (('organizationName', 'Google Inc'),),
                            (('commonName', 'mail.google.com'),))}
        ok(cert, 'mail.google.com')
        fail(cert, 'gmail.com')
        # Only commonName ni considered
        fail(cert, 'California')

        # -- IPv4 matching --
        cert = {'subject': ((('commonName', 'example.com'),),),
                'subjectAltName': (('DNS', 'example.com'),
                                   ('IP Address', '10.11.12.13'),
                                   ('IP Address', '14.15.16.17'),
                                   ('IP Address', '127.0.0.1'))}
        ok(cert, '10.11.12.13')
        ok(cert, '14.15.16.17')
        # socket.inet_ntoa(socket.inet_aton('127.1')) == '127.0.0.1'
        fail(cert, '127.1')
        fail(cert, '14.15.16.17 ')
        fail(cert, '14.15.16.17 extra data')
        fail(cert, '14.15.16.18')
        fail(cert, 'example.net')

        # -- IPv6 matching --
        ikiwa support.IPV6_ENABLED:
            cert = {'subject': ((('commonName', 'example.com'),),),
                    'subjectAltName': (
                        ('DNS', 'example.com'),
                        ('IP Address', '2001:0:0:0:0:0:0:CAFE\n'),
                        ('IP Address', '2003:0:0:0:0:0:0:BABA\n'))}
            ok(cert, '2001::cafe')
            ok(cert, '2003::baba')
            fail(cert, '2003::baba ')
            fail(cert, '2003::baba extra data')
            fail(cert, '2003::bebe')
            fail(cert, 'example.net')

        # -- Miscellaneous --

        # Neither commonName nor subjectAltName
        cert = {'notAfter': 'Dec 18 23:59:59 2011 GMT',
                'subject': ((('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'Mountain View'),),
                            (('organizationName', 'Google Inc'),))}
        fail(cert, 'mail.google.com')

        # No DNS entry kwenye subjectAltName but a commonName
        cert = {'notAfter': 'Dec 18 23:59:59 2099 GMT',
                'subject': ((('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'Mountain View'),),
                            (('commonName', 'mail.google.com'),)),
                'subjectAltName': (('othername', 'blabla'), )}
        ok(cert, 'mail.google.com')

        # No DNS entry subjectAltName na no commonName
        cert = {'notAfter': 'Dec 18 23:59:59 2099 GMT',
                'subject': ((('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'Mountain View'),),
                            (('organizationName', 'Google Inc'),)),
                'subjectAltName': (('othername', 'blabla'),)}
        fail(cert, 'google.com')

        # Empty cert / no cert
        self.assertRaises(ValueError, ssl.match_hostname, Tupu, 'example.com')
        self.assertRaises(ValueError, ssl.match_hostname, {}, 'example.com')

        # Issue #17980: avoid denials of service by refusing more than one
        # wildcard per fragment.
        cert = {'subject': ((('commonName', 'a*b.example.com'),),)}
        ukijumuisha self.assertRaisesRegex(
                ssl.CertificateError,
                "partial wildcards kwenye leftmost label are sio supported"):
            ssl.match_hostname(cert, 'axxb.example.com')

        cert = {'subject': ((('commonName', 'www.*.example.com'),),)}
        ukijumuisha self.assertRaisesRegex(
                ssl.CertificateError,
                "wildcard can only be present kwenye the leftmost label"):
            ssl.match_hostname(cert, 'www.sub.example.com')

        cert = {'subject': ((('commonName', 'a*b*.example.com'),),)}
        ukijumuisha self.assertRaisesRegex(
                ssl.CertificateError,
                "too many wildcards"):
            ssl.match_hostname(cert, 'axxbxxc.example.com')

        cert = {'subject': ((('commonName', '*'),),)}
        ukijumuisha self.assertRaisesRegex(
                ssl.CertificateError,
                "sole wildcard without additional labels are sio support"):
            ssl.match_hostname(cert, 'host')

        cert = {'subject': ((('commonName', '*.com'),),)}
        ukijumuisha self.assertRaisesRegex(
                ssl.CertificateError,
                r"hostname 'com' doesn't match '\*.com'"):
            ssl.match_hostname(cert, 'com')

        # extra checks kila _inet_paton()
        kila invalid kwenye ['1', '', '1.2.3', '256.0.0.1', '127.0.0.1/24']:
            ukijumuisha self.assertRaises(ValueError):
                ssl._inet_paton(invalid)
        kila ipaddr kwenye ['127.0.0.1', '192.168.0.1']:
            self.assertKweli(ssl._inet_paton(ipaddr))
        ikiwa support.IPV6_ENABLED:
            kila ipaddr kwenye ['::1', '2001:db8:85a3::8a2e:370:7334']:
                self.assertKweli(ssl._inet_paton(ipaddr))

    eleza test_server_side(self):
        # server_hostname doesn't work kila server sockets
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ukijumuisha socket.socket() kama sock:
            self.assertRaises(ValueError, ctx.wrap_socket, sock, Kweli,
                              server_hostname="some.hostname")

    eleza test_unknown_channel_binding(self):
        # should ashiria ValueError kila unknown type
        s = socket.create_server(('127.0.0.1', 0))
        c = socket.socket(socket.AF_INET)
        c.connect(s.getsockname())
        ukijumuisha test_wrap_socket(c, do_handshake_on_connect=Uongo) kama ss:
            ukijumuisha self.assertRaises(ValueError):
                ss.get_channel_binding("unknown-type")
        s.close()

    @unittest.skipUnless("tls-unique" kwenye ssl.CHANNEL_BINDING_TYPES,
                         "'tls-unique' channel binding sio available")
    eleza test_tls_unique_channel_binding(self):
        # unconnected should rudisha Tupu kila known type
        s = socket.socket(socket.AF_INET)
        ukijumuisha test_wrap_socket(s) kama ss:
            self.assertIsTupu(ss.get_channel_binding("tls-unique"))
        # the same kila server-side
        s = socket.socket(socket.AF_INET)
        ukijumuisha test_wrap_socket(s, server_side=Kweli, certfile=CERTFILE) kama ss:
            self.assertIsTupu(ss.get_channel_binding("tls-unique"))

    eleza test_dealloc_warn(self):
        ss = test_wrap_socket(socket.socket(socket.AF_INET))
        r = repr(ss)
        ukijumuisha self.assertWarns(ResourceWarning) kama cm:
            ss = Tupu
            support.gc_collect()
        self.assertIn(r, str(cm.warning.args[0]))

    eleza test_get_default_verify_paths(self):
        paths = ssl.get_default_verify_paths()
        self.assertEqual(len(paths), 6)
        self.assertIsInstance(paths, ssl.DefaultVerifyPaths)

        ukijumuisha support.EnvironmentVarGuard() kama env:
            env["SSL_CERT_DIR"] = CAPATH
            env["SSL_CERT_FILE"] = CERTFILE
            paths = ssl.get_default_verify_paths()
            self.assertEqual(paths.cafile, CERTFILE)
            self.assertEqual(paths.capath, CAPATH)

    @unittest.skipUnless(sys.platform == "win32", "Windows specific")
    eleza test_enum_certificates(self):
        self.assertKweli(ssl.enum_certificates("CA"))
        self.assertKweli(ssl.enum_certificates("ROOT"))

        self.assertRaises(TypeError, ssl.enum_certificates)
        self.assertRaises(WindowsError, ssl.enum_certificates, "")

        trust_oids = set()
        kila storename kwenye ("CA", "ROOT"):
            store = ssl.enum_certificates(storename)
            self.assertIsInstance(store, list)
            kila element kwenye store:
                self.assertIsInstance(element, tuple)
                self.assertEqual(len(element), 3)
                cert, enc, trust = element
                self.assertIsInstance(cert, bytes)
                self.assertIn(enc, {"x509_asn", "pkcs_7_asn"})
                self.assertIsInstance(trust, (frozenset, set, bool))
                ikiwa isinstance(trust, (frozenset, set)):
                    trust_oids.update(trust)

        serverAuth = "1.3.6.1.5.5.7.3.1"
        self.assertIn(serverAuth, trust_oids)

    @unittest.skipUnless(sys.platform == "win32", "Windows specific")
    eleza test_enum_crls(self):
        self.assertKweli(ssl.enum_crls("CA"))
        self.assertRaises(TypeError, ssl.enum_crls)
        self.assertRaises(WindowsError, ssl.enum_crls, "")

        crls = ssl.enum_crls("CA")
        self.assertIsInstance(crls, list)
        kila element kwenye crls:
            self.assertIsInstance(element, tuple)
            self.assertEqual(len(element), 2)
            self.assertIsInstance(element[0], bytes)
            self.assertIn(element[1], {"x509_asn", "pkcs_7_asn"})


    eleza test_asn1object(self):
        expected = (129, 'serverAuth', 'TLS Web Server Authentication',
                    '1.3.6.1.5.5.7.3.1')

        val = ssl._ASN1Object('1.3.6.1.5.5.7.3.1')
        self.assertEqual(val, expected)
        self.assertEqual(val.nid, 129)
        self.assertEqual(val.shortname, 'serverAuth')
        self.assertEqual(val.longname, 'TLS Web Server Authentication')
        self.assertEqual(val.oid, '1.3.6.1.5.5.7.3.1')
        self.assertIsInstance(val, ssl._ASN1Object)
        self.assertRaises(ValueError, ssl._ASN1Object, 'serverAuth')

        val = ssl._ASN1Object.fromnid(129)
        self.assertEqual(val, expected)
        self.assertIsInstance(val, ssl._ASN1Object)
        self.assertRaises(ValueError, ssl._ASN1Object.fromnid, -1)
        ukijumuisha self.assertRaisesRegex(ValueError, "unknown NID 100000"):
            ssl._ASN1Object.fromnid(100000)
        kila i kwenye range(1000):
            jaribu:
                obj = ssl._ASN1Object.fromnid(i)
            tatizo ValueError:
                pita
            isipokua:
                self.assertIsInstance(obj.nid, int)
                self.assertIsInstance(obj.shortname, str)
                self.assertIsInstance(obj.longname, str)
                self.assertIsInstance(obj.oid, (str, type(Tupu)))

        val = ssl._ASN1Object.fromname('TLS Web Server Authentication')
        self.assertEqual(val, expected)
        self.assertIsInstance(val, ssl._ASN1Object)
        self.assertEqual(ssl._ASN1Object.fromname('serverAuth'), expected)
        self.assertEqual(ssl._ASN1Object.fromname('1.3.6.1.5.5.7.3.1'),
                         expected)
        ukijumuisha self.assertRaisesRegex(ValueError, "unknown object 'serverauth'"):
            ssl._ASN1Object.fromname('serverauth')

    eleza test_purpose_enum(self):
        val = ssl._ASN1Object('1.3.6.1.5.5.7.3.1')
        self.assertIsInstance(ssl.Purpose.SERVER_AUTH, ssl._ASN1Object)
        self.assertEqual(ssl.Purpose.SERVER_AUTH, val)
        self.assertEqual(ssl.Purpose.SERVER_AUTH.nid, 129)
        self.assertEqual(ssl.Purpose.SERVER_AUTH.shortname, 'serverAuth')
        self.assertEqual(ssl.Purpose.SERVER_AUTH.oid,
                              '1.3.6.1.5.5.7.3.1')

        val = ssl._ASN1Object('1.3.6.1.5.5.7.3.2')
        self.assertIsInstance(ssl.Purpose.CLIENT_AUTH, ssl._ASN1Object)
        self.assertEqual(ssl.Purpose.CLIENT_AUTH, val)
        self.assertEqual(ssl.Purpose.CLIENT_AUTH.nid, 130)
        self.assertEqual(ssl.Purpose.CLIENT_AUTH.shortname, 'clientAuth')
        self.assertEqual(ssl.Purpose.CLIENT_AUTH.oid,
                              '1.3.6.1.5.5.7.3.2')

    eleza test_unsupported_dtls(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(s.close)
        ukijumuisha self.assertRaises(NotImplementedError) kama cx:
            test_wrap_socket(s, cert_reqs=ssl.CERT_NONE)
        self.assertEqual(str(cx.exception), "only stream sockets are supported")
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ukijumuisha self.assertRaises(NotImplementedError) kama cx:
            ctx.wrap_socket(s)
        self.assertEqual(str(cx.exception), "only stream sockets are supported")

    eleza cert_time_ok(self, timestring, timestamp):
        self.assertEqual(ssl.cert_time_to_seconds(timestring), timestamp)

    eleza cert_time_fail(self, timestring):
        ukijumuisha self.assertRaises(ValueError):
            ssl.cert_time_to_seconds(timestring)

    @unittest.skipUnless(utc_offset(),
                         'local time needs to be different kutoka UTC')
    eleza test_cert_time_to_seconds_timezone(self):
        # Issue #19940: ssl.cert_time_to_seconds() returns wrong
        #               results ikiwa local timezone ni sio UTC
        self.cert_time_ok("May  9 00:00:00 2007 GMT", 1178668800.0)
        self.cert_time_ok("Jan  5 09:34:43 2018 GMT", 1515144883.0)

    eleza test_cert_time_to_seconds(self):
        timestring = "Jan  5 09:34:43 2018 GMT"
        ts = 1515144883.0
        self.cert_time_ok(timestring, ts)
        # accept keyword parameter, assert its name
        self.assertEqual(ssl.cert_time_to_seconds(cert_time=timestring), ts)
        # accept both %e na %d (space ama zero generated by strftime)
        self.cert_time_ok("Jan 05 09:34:43 2018 GMT", ts)
        # case-insensitive
        self.cert_time_ok("JaN  5 09:34:43 2018 GmT", ts)
        self.cert_time_fail("Jan  5 09:34 2018 GMT")     # no seconds
        self.cert_time_fail("Jan  5 09:34:43 2018")      # no GMT
        self.cert_time_fail("Jan  5 09:34:43 2018 UTC")  # sio GMT timezone
        self.cert_time_fail("Jan 35 09:34:43 2018 GMT")  # invalid day
        self.cert_time_fail("Jon  5 09:34:43 2018 GMT")  # invalid month
        self.cert_time_fail("Jan  5 24:00:00 2018 GMT")  # invalid hour
        self.cert_time_fail("Jan  5 09:60:43 2018 GMT")  # invalid minute

        newyear_ts = 1230768000.0
        # leap seconds
        self.cert_time_ok("Dec 31 23:59:60 2008 GMT", newyear_ts)
        # same timestamp
        self.cert_time_ok("Jan  1 00:00:00 2009 GMT", newyear_ts)

        self.cert_time_ok("Jan  5 09:34:59 2018 GMT", 1515144899)
        #  allow 60th second (even ikiwa it ni sio a leap second)
        self.cert_time_ok("Jan  5 09:34:60 2018 GMT", 1515144900)
        #  allow 2nd leap second kila compatibility ukijumuisha time.strptime()
        self.cert_time_ok("Jan  5 09:34:61 2018 GMT", 1515144901)
        self.cert_time_fail("Jan  5 09:34:62 2018 GMT")  # invalid seconds

        # no special treatment kila the special value:
        #   99991231235959Z (rfc 5280)
        self.cert_time_ok("Dec 31 23:59:59 9999 GMT", 253402300799.0)

    @support.run_with_locale('LC_ALL', '')
    eleza test_cert_time_to_seconds_locale(self):
        # `cert_time_to_seconds()` should be locale independent

        eleza local_february_name():
            rudisha time.strftime('%b', (1, 2, 3, 4, 5, 6, 0, 0, 0))

        ikiwa local_february_name().lower() == 'feb':
            self.skipTest("locale-specific month name needs to be "
                          "different kutoka C locale")

        # locale-independent
        self.cert_time_ok("Feb  9 00:00:00 2007 GMT", 1170979200.0)
        self.cert_time_fail(local_february_name() + "  9 00:00:00 2007 GMT")

    eleza test_connect_ex_error(self):
        server = socket.socket(socket.AF_INET)
        self.addCleanup(server.close)
        port = support.bind_port(server)  # Reserve port but don't listen
        s = test_wrap_socket(socket.socket(socket.AF_INET),
                            cert_reqs=ssl.CERT_REQUIRED)
        self.addCleanup(s.close)
        rc = s.connect_ex((HOST, port))
        # Issue #19919: Windows machines ama VMs hosted on Windows
        # machines sometimes rudisha EWOULDBLOCK.
        errors = (
            errno.ECONNREFUSED, errno.EHOSTUNREACH, errno.ETIMEDOUT,
            errno.EWOULDBLOCK,
        )
        self.assertIn(rc, errors)


kundi ContextTests(unittest.TestCase):

    eleza test_constructor(self):
        kila protocol kwenye PROTOCOLS:
            ssl.SSLContext(protocol)
        ctx = ssl.SSLContext()
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLS)
        self.assertRaises(ValueError, ssl.SSLContext, -1)
        self.assertRaises(ValueError, ssl.SSLContext, 42)

    eleza test_protocol(self):
        kila proto kwenye PROTOCOLS:
            ctx = ssl.SSLContext(proto)
            self.assertEqual(ctx.protocol, proto)

    eleza test_ciphers(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.set_ciphers("ALL")
        ctx.set_ciphers("DEFAULT")
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "No cipher can be selected"):
            ctx.set_ciphers("^$:,;?*'dorothyx")

    @unittest.skipUnless(PY_SSL_DEFAULT_CIPHERS == 1,
                         "Test applies only to Python default ciphers")
    eleza test_python_ciphers(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ciphers = ctx.get_ciphers()
        kila suite kwenye ciphers:
            name = suite['name']
            self.assertNotIn("PSK", name)
            self.assertNotIn("SRP", name)
            self.assertNotIn("MD5", name)
            self.assertNotIn("RC4", name)
            self.assertNotIn("3DES", name)

    @unittest.skipIf(ssl.OPENSSL_VERSION_INFO < (1, 0, 2, 0, 0), 'OpenSSL too old')
    eleza test_get_ciphers(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.set_ciphers('AESGCM')
        names = set(d['name'] kila d kwenye ctx.get_ciphers())
        self.assertIn('AES256-GCM-SHA384', names)
        self.assertIn('AES128-GCM-SHA256', names)

    eleza test_options(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # OP_ALL | OP_NO_SSLv2 | OP_NO_SSLv3 ni the default value
        default = (ssl.OP_ALL | ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3)
        # SSLContext also enables these by default
        default |= (OP_NO_COMPRESSION | OP_CIPHER_SERVER_PREFERENCE |
                    OP_SINGLE_DH_USE | OP_SINGLE_ECDH_USE |
                    OP_ENABLE_MIDDLEBOX_COMPAT)
        self.assertEqual(default, ctx.options)
        ctx.options |= ssl.OP_NO_TLSv1
        self.assertEqual(default | ssl.OP_NO_TLSv1, ctx.options)
        ikiwa can_clear_options():
            ctx.options = (ctx.options & ~ssl.OP_NO_TLSv1)
            self.assertEqual(default, ctx.options)
            ctx.options = 0
            # Ubuntu has OP_NO_SSLv3 forced on by default
            self.assertEqual(0, ctx.options & ~ssl.OP_NO_SSLv3)
        isipokua:
            ukijumuisha self.assertRaises(ValueError):
                ctx.options = 0

    eleza test_verify_mode_protocol(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        # Default value
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        ctx.verify_mode = ssl.CERT_OPTIONAL
        self.assertEqual(ctx.verify_mode, ssl.CERT_OPTIONAL)
        ctx.verify_mode = ssl.CERT_REQUIRED
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        ctx.verify_mode = ssl.CERT_NONE
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        ukijumuisha self.assertRaises(TypeError):
            ctx.verify_mode = Tupu
        ukijumuisha self.assertRaises(ValueError):
            ctx.verify_mode = 42

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self.assertUongo(ctx.check_hostname)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertKweli(ctx.check_hostname)

    eleza test_hostname_checks_common_name(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertKweli(ctx.hostname_checks_common_name)
        ikiwa ssl.HAS_NEVER_CHECK_COMMON_NAME:
            ctx.hostname_checks_common_name = Kweli
            self.assertKweli(ctx.hostname_checks_common_name)
            ctx.hostname_checks_common_name = Uongo
            self.assertUongo(ctx.hostname_checks_common_name)
            ctx.hostname_checks_common_name = Kweli
            self.assertKweli(ctx.hostname_checks_common_name)
        isipokua:
            ukijumuisha self.assertRaises(AttributeError):
                ctx.hostname_checks_common_name = Kweli

    @requires_minimum_version
    @unittest.skipIf(IS_LIBRESSL, "see bpo-34001")
    eleza test_min_max_version(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # OpenSSL default ni MINIMUM_SUPPORTED, however some vendors like
        # Fedora override the setting to TLS 1.0.
        minimum_range = {
            # stock OpenSSL
            ssl.TLSVersion.MINIMUM_SUPPORTED,
            # Fedora 29 uses TLS 1.0 by default
            ssl.TLSVersion.TLSv1,
            # RHEL 8 uses TLS 1.2 by default
            ssl.TLSVersion.TLSv1_2
        }

        self.assertIn(
            ctx.minimum_version, minimum_range
        )
        self.assertEqual(
            ctx.maximum_version, ssl.TLSVersion.MAXIMUM_SUPPORTED
        )

        ctx.minimum_version = ssl.TLSVersion.TLSv1_1
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
        self.assertEqual(
            ctx.minimum_version, ssl.TLSVersion.TLSv1_1
        )
        self.assertEqual(
            ctx.maximum_version, ssl.TLSVersion.TLSv1_2
        )

        ctx.minimum_version = ssl.TLSVersion.MINIMUM_SUPPORTED
        ctx.maximum_version = ssl.TLSVersion.TLSv1
        self.assertEqual(
            ctx.minimum_version, ssl.TLSVersion.MINIMUM_SUPPORTED
        )
        self.assertEqual(
            ctx.maximum_version, ssl.TLSVersion.TLSv1
        )

        ctx.maximum_version = ssl.TLSVersion.MAXIMUM_SUPPORTED
        self.assertEqual(
            ctx.maximum_version, ssl.TLSVersion.MAXIMUM_SUPPORTED
        )

        ctx.maximum_version = ssl.TLSVersion.MINIMUM_SUPPORTED
        self.assertIn(
            ctx.maximum_version,
            {ssl.TLSVersion.TLSv1, ssl.TLSVersion.SSLv3}
        )

        ctx.minimum_version = ssl.TLSVersion.MAXIMUM_SUPPORTED
        self.assertIn(
            ctx.minimum_version,
            {ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_3}
        )

        ukijumuisha self.assertRaises(ValueError):
            ctx.minimum_version = 42

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_1)

        self.assertIn(
            ctx.minimum_version, minimum_range
        )
        self.assertEqual(
            ctx.maximum_version, ssl.TLSVersion.MAXIMUM_SUPPORTED
        )
        ukijumuisha self.assertRaises(ValueError):
            ctx.minimum_version = ssl.TLSVersion.MINIMUM_SUPPORTED
        ukijumuisha self.assertRaises(ValueError):
            ctx.maximum_version = ssl.TLSVersion.TLSv1


    @unittest.skipUnless(have_verify_flags(),
                         "verify_flags need OpenSSL > 0.9.8")
    eleza test_verify_flags(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # default value
        tf = getattr(ssl, "VERIFY_X509_TRUSTED_FIRST", 0)
        self.assertEqual(ctx.verify_flags, ssl.VERIFY_DEFAULT | tf)
        ctx.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF
        self.assertEqual(ctx.verify_flags, ssl.VERIFY_CRL_CHECK_LEAF)
        ctx.verify_flags = ssl.VERIFY_CRL_CHECK_CHAIN
        self.assertEqual(ctx.verify_flags, ssl.VERIFY_CRL_CHECK_CHAIN)
        ctx.verify_flags = ssl.VERIFY_DEFAULT
        self.assertEqual(ctx.verify_flags, ssl.VERIFY_DEFAULT)
        # supports any value
        ctx.verify_flags = ssl.VERIFY_CRL_CHECK_LEAF | ssl.VERIFY_X509_STRICT
        self.assertEqual(ctx.verify_flags,
                         ssl.VERIFY_CRL_CHECK_LEAF | ssl.VERIFY_X509_STRICT)
        ukijumuisha self.assertRaises(TypeError):
            ctx.verify_flags = Tupu

    eleza test_load_cert_chain(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # Combined key na cert kwenye a single file
        ctx.load_cert_chain(CERTFILE, keyfile=Tupu)
        ctx.load_cert_chain(CERTFILE, keyfile=CERTFILE)
        self.assertRaises(TypeError, ctx.load_cert_chain, keyfile=CERTFILE)
        ukijumuisha self.assertRaises(OSError) kama cm:
            ctx.load_cert_chain(NONEXISTINGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(BADCERT)
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(EMPTYCERT)
        # Separate key na cert
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(ONLYCERT, ONLYKEY)
        ctx.load_cert_chain(certfile=ONLYCERT, keyfile=ONLYKEY)
        ctx.load_cert_chain(certfile=BYTES_ONLYCERT, keyfile=BYTES_ONLYKEY)
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(ONLYCERT)
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(ONLYKEY)
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_cert_chain(certfile=ONLYKEY, keyfile=ONLYCERT)
        # Mismatching key na cert
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "key values mismatch"):
            ctx.load_cert_chain(CAFILE_CACERT, ONLYKEY)
        # Password protected key na cert
        ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=KEY_PASSWORD)
        ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=KEY_PASSWORD.encode())
        ctx.load_cert_chain(CERTFILE_PROTECTED,
                            pitaword=bytearray(KEY_PASSWORD.encode()))
        ctx.load_cert_chain(ONLYCERT, ONLYKEY_PROTECTED, KEY_PASSWORD)
        ctx.load_cert_chain(ONLYCERT, ONLYKEY_PROTECTED, KEY_PASSWORD.encode())
        ctx.load_cert_chain(ONLYCERT, ONLYKEY_PROTECTED,
                            bytearray(KEY_PASSWORD.encode()))
        ukijumuisha self.assertRaisesRegex(TypeError, "should be a string"):
            ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=Kweli)
        ukijumuisha self.assertRaises(ssl.SSLError):
            ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword="badpita")
        ukijumuisha self.assertRaisesRegex(ValueError, "cannot be longer"):
            # openssl has a fixed limit on the pitaword buffer.
            # PEM_BUFSIZE ni generally set to 1kb.
            # Return a string larger than this.
            ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=b'a' * 102400)
        # Password callback
        eleza getpita_unicode():
            rudisha KEY_PASSWORD
        eleza getpita_bytes():
            rudisha KEY_PASSWORD.encode()
        eleza getpita_bytearray():
            rudisha bytearray(KEY_PASSWORD.encode())
        eleza getpita_badpita():
            rudisha "badpita"
        eleza getpita_huge():
            rudisha b'a' * (1024 * 1024)
        eleza getpita_bad_type():
            rudisha 9
        eleza getpita_exception():
            ashiria Exception('getpita error')
        kundi GetPassCallable:
            eleza __call__(self):
                rudisha KEY_PASSWORD
            eleza getpita(self):
                rudisha KEY_PASSWORD
        ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=getpita_unicode)
        ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=getpita_bytes)
        ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=getpita_bytearray)
        ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=GetPassCallable())
        ctx.load_cert_chain(CERTFILE_PROTECTED,
                            pitaword=GetPassCallable().getpita)
        ukijumuisha self.assertRaises(ssl.SSLError):
            ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=getpita_badpita)
        ukijumuisha self.assertRaisesRegex(ValueError, "cannot be longer"):
            ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=getpita_huge)
        ukijumuisha self.assertRaisesRegex(TypeError, "must rudisha a string"):
            ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=getpita_bad_type)
        ukijumuisha self.assertRaisesRegex(Exception, "getpita error"):
            ctx.load_cert_chain(CERTFILE_PROTECTED, pitaword=getpita_exception)
        # Make sure the pitaword function isn't called ikiwa it isn't needed
        ctx.load_cert_chain(CERTFILE, pitaword=getpita_exception)

    eleza test_load_verify_locations(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_verify_locations(CERTFILE)
        ctx.load_verify_locations(cafile=CERTFILE, capath=Tupu)
        ctx.load_verify_locations(BYTES_CERTFILE)
        ctx.load_verify_locations(cafile=BYTES_CERTFILE, capath=Tupu)
        self.assertRaises(TypeError, ctx.load_verify_locations)
        self.assertRaises(TypeError, ctx.load_verify_locations, Tupu, Tupu, Tupu)
        ukijumuisha self.assertRaises(OSError) kama cm:
            ctx.load_verify_locations(NONEXISTINGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "PEM lib"):
            ctx.load_verify_locations(BADCERT)
        ctx.load_verify_locations(CERTFILE, CAPATH)
        ctx.load_verify_locations(CERTFILE, capath=BYTES_CAPATH)

        # Issue #10989: crash ikiwa the second argument type ni invalid
        self.assertRaises(TypeError, ctx.load_verify_locations, Tupu, Kweli)

    eleza test_load_verify_cadata(self):
        # test cadata
        ukijumuisha open(CAFILE_CACERT) kama f:
            cacert_pem = f.read()
        cacert_der = ssl.PEM_cert_to_DER_cert(cacert_pem)
        ukijumuisha open(CAFILE_NEURONIO) kama f:
            neuronio_pem = f.read()
        neuronio_der = ssl.PEM_cert_to_DER_cert(neuronio_pem)

        # test PEM
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 0)
        ctx.load_verify_locations(cadata=cacert_pem)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 1)
        ctx.load_verify_locations(cadata=neuronio_pem)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)
        # cert already kwenye hash table
        ctx.load_verify_locations(cadata=neuronio_pem)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # combined
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        combined = "\n".join((cacert_pem, neuronio_pem))
        ctx.load_verify_locations(cadata=combined)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # ukijumuisha junk around the certs
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        combined = ["head", cacert_pem, "other", neuronio_pem, "again",
                    neuronio_pem, "tail"]
        ctx.load_verify_locations(cadata="\n".join(combined))
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # test DER
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(cadata=cacert_der)
        ctx.load_verify_locations(cadata=neuronio_der)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)
        # cert already kwenye hash table
        ctx.load_verify_locations(cadata=cacert_der)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # combined
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        combined = b"".join((cacert_der, neuronio_der))
        ctx.load_verify_locations(cadata=combined)
        self.assertEqual(ctx.cert_store_stats()["x509_ca"], 2)

        # error cases
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertRaises(TypeError, ctx.load_verify_locations, cadata=object)

        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "no start line"):
            ctx.load_verify_locations(cadata="broken")
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "not enough data"):
            ctx.load_verify_locations(cadata=b"broken")


    eleza test_load_dh_params(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_dh_params(DHFILE)
        ikiwa os.name != 'nt':
            ctx.load_dh_params(BYTES_DHFILE)
        self.assertRaises(TypeError, ctx.load_dh_params)
        self.assertRaises(TypeError, ctx.load_dh_params, Tupu)
        ukijumuisha self.assertRaises(FileNotFoundError) kama cm:
            ctx.load_dh_params(NONEXISTINGCERT)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        ukijumuisha self.assertRaises(ssl.SSLError) kama cm:
            ctx.load_dh_params(CERTFILE)

    eleza test_session_stats(self):
        kila proto kwenye PROTOCOLS:
            ctx = ssl.SSLContext(proto)
            self.assertEqual(ctx.session_stats(), {
                'number': 0,
                'connect': 0,
                'connect_good': 0,
                'connect_renegotiate': 0,
                'accept': 0,
                'accept_good': 0,
                'accept_renegotiate': 0,
                'hits': 0,
                'misses': 0,
                'timeouts': 0,
                'cache_full': 0,
            })

    eleza test_set_default_verify_paths(self):
        # There's sio much we can do to test that it acts kama expected,
        # so just check it doesn't crash ama ashiria an exception.
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.set_default_verify_paths()

    @unittest.skipUnless(ssl.HAS_ECDH, "ECDH disabled on this OpenSSL build")
    eleza test_set_ecdh_curve(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.set_ecdh_curve("prime256v1")
        ctx.set_ecdh_curve(b"prime256v1")
        self.assertRaises(TypeError, ctx.set_ecdh_curve)
        self.assertRaises(TypeError, ctx.set_ecdh_curve, Tupu)
        self.assertRaises(ValueError, ctx.set_ecdh_curve, "foo")
        self.assertRaises(ValueError, ctx.set_ecdh_curve, b"foo")

    @needs_sni
    eleza test_sni_callback(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        # set_servername_callback expects a callable, ama Tupu
        self.assertRaises(TypeError, ctx.set_servername_callback)
        self.assertRaises(TypeError, ctx.set_servername_callback, 4)
        self.assertRaises(TypeError, ctx.set_servername_callback, "")
        self.assertRaises(TypeError, ctx.set_servername_callback, ctx)

        eleza dummycallback(sock, servername, ctx):
            pita
        ctx.set_servername_callback(Tupu)
        ctx.set_servername_callback(dummycallback)

    @needs_sni
    eleza test_sni_callback_refcycle(self):
        # Reference cycles through the servername callback are detected
        # na cleared.
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        eleza dummycallback(sock, servername, ctx, cycle=ctx):
            pita
        ctx.set_servername_callback(dummycallback)
        wr = weakref.ref(ctx)
        toa ctx, dummycallback
        gc.collect()
        self.assertIs(wr(), Tupu)

    eleza test_cert_store_stats(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertEqual(ctx.cert_store_stats(),
            {'x509_ca': 0, 'crl': 0, 'x509': 0})
        ctx.load_cert_chain(CERTFILE)
        self.assertEqual(ctx.cert_store_stats(),
            {'x509_ca': 0, 'crl': 0, 'x509': 0})
        ctx.load_verify_locations(CERTFILE)
        self.assertEqual(ctx.cert_store_stats(),
            {'x509_ca': 0, 'crl': 0, 'x509': 1})
        ctx.load_verify_locations(CAFILE_CACERT)
        self.assertEqual(ctx.cert_store_stats(),
            {'x509_ca': 1, 'crl': 0, 'x509': 2})

    eleza test_get_ca_certs(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertEqual(ctx.get_ca_certs(), [])
        # CERTFILE ni sio flagged kama X509v3 Basic Constraints: CA:TRUE
        ctx.load_verify_locations(CERTFILE)
        self.assertEqual(ctx.get_ca_certs(), [])
        # but CAFILE_CACERT ni a CA cert
        ctx.load_verify_locations(CAFILE_CACERT)
        self.assertEqual(ctx.get_ca_certs(),
            [{'issuer': ((('organizationName', 'Root CA'),),
                         (('organizationalUnitName', 'http://www.cacert.org'),),
                         (('commonName', 'CA Cert Signing Authority'),),
                         (('emailAddress', 'support@cacert.org'),)),
              'notAfter': asn1time('Mar 29 12:29:49 2033 GMT'),
              'notBefore': asn1time('Mar 30 12:29:49 2003 GMT'),
              'serialNumber': '00',
              'crlDistributionPoints': ('https://www.cacert.org/revoke.crl',),
              'subject': ((('organizationName', 'Root CA'),),
                          (('organizationalUnitName', 'http://www.cacert.org'),),
                          (('commonName', 'CA Cert Signing Authority'),),
                          (('emailAddress', 'support@cacert.org'),)),
              'version': 3}])

        ukijumuisha open(CAFILE_CACERT) kama f:
            pem = f.read()
        der = ssl.PEM_cert_to_DER_cert(pem)
        self.assertEqual(ctx.get_ca_certs(Kweli), [der])

    eleza test_load_default_certs(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_default_certs()

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_default_certs(ssl.Purpose.SERVER_AUTH)
        ctx.load_default_certs()

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_default_certs(ssl.Purpose.CLIENT_AUTH)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertRaises(TypeError, ctx.load_default_certs, Tupu)
        self.assertRaises(TypeError, ctx.load_default_certs, 'SERVER_AUTH')

    @unittest.skipIf(sys.platform == "win32", "not-Windows specific")
    @unittest.skipIf(IS_LIBRESSL, "LibreSSL doesn't support env vars")
    eleza test_load_default_certs_env(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env["SSL_CERT_DIR"] = CAPATH
            env["SSL_CERT_FILE"] = CERTFILE
            ctx.load_default_certs()
            self.assertEqual(ctx.cert_store_stats(), {"crl": 0, "x509": 1, "x509_ca": 0})

    @unittest.skipUnless(sys.platform == "win32", "Windows specific")
    @unittest.skipIf(hasattr(sys, "gettotalrefcount"), "Debug build does sio share environment between CRTs")
    eleza test_load_default_certs_env_windows(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_default_certs()
        stats = ctx.cert_store_stats()

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env["SSL_CERT_DIR"] = CAPATH
            env["SSL_CERT_FILE"] = CERTFILE
            ctx.load_default_certs()
            stats["x509"] += 1
            self.assertEqual(ctx.cert_store_stats(), stats)

    eleza _assert_context_options(self, ctx):
        self.assertEqual(ctx.options & ssl.OP_NO_SSLv2, ssl.OP_NO_SSLv2)
        ikiwa OP_NO_COMPRESSION != 0:
            self.assertEqual(ctx.options & OP_NO_COMPRESSION,
                             OP_NO_COMPRESSION)
        ikiwa OP_SINGLE_DH_USE != 0:
            self.assertEqual(ctx.options & OP_SINGLE_DH_USE,
                             OP_SINGLE_DH_USE)
        ikiwa OP_SINGLE_ECDH_USE != 0:
            self.assertEqual(ctx.options & OP_SINGLE_ECDH_USE,
                             OP_SINGLE_ECDH_USE)
        ikiwa OP_CIPHER_SERVER_PREFERENCE != 0:
            self.assertEqual(ctx.options & OP_CIPHER_SERVER_PREFERENCE,
                             OP_CIPHER_SERVER_PREFERENCE)

    eleza test_create_default_context(self):
        ctx = ssl.create_default_context()

        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLS)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertKweli(ctx.check_hostname)
        self._assert_context_options(ctx)

        ukijumuisha open(SIGNING_CA) kama f:
            cadata = f.read()
        ctx = ssl.create_default_context(cafile=SIGNING_CA, capath=CAPATH,
                                         cadata=cadata)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLS)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self._assert_context_options(ctx)

        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLS)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self._assert_context_options(ctx)

    eleza test__create_stdlib_context(self):
        ctx = ssl._create_stdlib_context()
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLS)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self.assertUongo(ctx.check_hostname)
        self._assert_context_options(ctx)

        ctx = ssl._create_stdlib_context(ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self._assert_context_options(ctx)

        ctx = ssl._create_stdlib_context(ssl.PROTOCOL_TLSv1,
                                         cert_reqs=ssl.CERT_REQUIRED,
                                         check_hostname=Kweli)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLSv1)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertKweli(ctx.check_hostname)
        self._assert_context_options(ctx)

        ctx = ssl._create_stdlib_context(purpose=ssl.Purpose.CLIENT_AUTH)
        self.assertEqual(ctx.protocol, ssl.PROTOCOL_TLS)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        self._assert_context_options(ctx)

    eleza test_check_hostname(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.assertUongo(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)

        # Auto set CERT_REQUIRED
        ctx.check_hostname = Kweli
        self.assertKweli(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        ctx.check_hostname = Uongo
        ctx.verify_mode = ssl.CERT_REQUIRED
        self.assertUongo(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)

        # Changing verify_mode does sio affect check_hostname
        ctx.check_hostname = Uongo
        ctx.verify_mode = ssl.CERT_NONE
        ctx.check_hostname = Uongo
        self.assertUongo(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
        # Auto set
        ctx.check_hostname = Kweli
        self.assertKweli(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)

        ctx.check_hostname = Uongo
        ctx.verify_mode = ssl.CERT_OPTIONAL
        ctx.check_hostname = Uongo
        self.assertUongo(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_OPTIONAL)
        # keep CERT_OPTIONAL
        ctx.check_hostname = Kweli
        self.assertKweli(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_OPTIONAL)

        # Cannot set CERT_NONE ukijumuisha check_hostname enabled
        ukijumuisha self.assertRaises(ValueError):
            ctx.verify_mode = ssl.CERT_NONE
        ctx.check_hostname = Uongo
        self.assertUongo(ctx.check_hostname)
        ctx.verify_mode = ssl.CERT_NONE
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)

    eleza test_context_client_server(self):
        # PROTOCOL_TLS_CLIENT has sane defaults
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertKweli(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)

        # PROTOCOL_TLS_SERVER has different but also sane defaults
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.assertUongo(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)

    eleza test_context_custom_class(self):
        kundi MySSLSocket(ssl.SSLSocket):
            pita

        kundi MySSLObject(ssl.SSLObject):
            pita

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.sslsocket_kundi = MySSLSocket
        ctx.sslobject_kundi = MySSLObject

        ukijumuisha ctx.wrap_socket(socket.socket(), server_side=Kweli) kama sock:
            self.assertIsInstance(sock, MySSLSocket)
        obj = ctx.wrap_bio(ssl.MemoryBIO(), ssl.MemoryBIO())
        self.assertIsInstance(obj, MySSLObject)

    @unittest.skipUnless(IS_OPENSSL_1_1_1, "Test requires OpenSSL 1.1.1")
    eleza test_num_tickest(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.assertEqual(ctx.num_tickets, 2)
        ctx.num_tickets = 1
        self.assertEqual(ctx.num_tickets, 1)
        ctx.num_tickets = 0
        self.assertEqual(ctx.num_tickets, 0)
        ukijumuisha self.assertRaises(ValueError):
            ctx.num_tickets = -1
        ukijumuisha self.assertRaises(TypeError):
            ctx.num_tickets = Tupu

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertEqual(ctx.num_tickets, 2)
        ukijumuisha self.assertRaises(ValueError):
            ctx.num_tickets = 1


kundi SSLErrorTests(unittest.TestCase):

    eleza test_str(self):
        # The str() of a SSLError doesn't include the errno
        e = ssl.SSLError(1, "foo")
        self.assertEqual(str(e), "foo")
        self.assertEqual(e.errno, 1)
        # Same kila a subclass
        e = ssl.SSLZeroReturnError(1, "foo")
        self.assertEqual(str(e), "foo")
        self.assertEqual(e.errno, 1)

    eleza test_lib_reason(self):
        # Test the library na reason attributes
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ukijumuisha self.assertRaises(ssl.SSLError) kama cm:
            ctx.load_dh_params(CERTFILE)
        self.assertEqual(cm.exception.library, 'PEM')
        self.assertEqual(cm.exception.reason, 'NO_START_LINE')
        s = str(cm.exception)
        self.assertKweli(s.startswith("[PEM: NO_START_LINE] no start line"), s)

    eleza test_subclass(self):
        # Check that the appropriate SSLError subkundi ni raised
        # (this only tests one of them)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = Uongo
        ctx.verify_mode = ssl.CERT_NONE
        ukijumuisha socket.create_server(("127.0.0.1", 0)) kama s:
            c = socket.create_connection(s.getsockname())
            c.setblocking(Uongo)
            ukijumuisha ctx.wrap_socket(c, Uongo, do_handshake_on_connect=Uongo) kama c:
                ukijumuisha self.assertRaises(ssl.SSLWantReadError) kama cm:
                    c.do_handshake()
                s = str(cm.exception)
                self.assertKweli(s.startswith("The operation did sio complete (read)"), s)
                # For compatibility
                self.assertEqual(cm.exception.errno, ssl.SSL_ERROR_WANT_READ)


    eleza test_bad_server_hostname(self):
        ctx = ssl.create_default_context()
        ukijumuisha self.assertRaises(ValueError):
            ctx.wrap_bio(ssl.MemoryBIO(), ssl.MemoryBIO(),
                         server_hostname="")
        ukijumuisha self.assertRaises(ValueError):
            ctx.wrap_bio(ssl.MemoryBIO(), ssl.MemoryBIO(),
                         server_hostname=".example.org")
        ukijumuisha self.assertRaises(TypeError):
            ctx.wrap_bio(ssl.MemoryBIO(), ssl.MemoryBIO(),
                         server_hostname="example.org\x00evil.com")


kundi MemoryBIOTests(unittest.TestCase):

    eleza test_read_write(self):
        bio = ssl.MemoryBIO()
        bio.write(b'foo')
        self.assertEqual(bio.read(), b'foo')
        self.assertEqual(bio.read(), b'')
        bio.write(b'foo')
        bio.write(b'bar')
        self.assertEqual(bio.read(), b'foobar')
        self.assertEqual(bio.read(), b'')
        bio.write(b'baz')
        self.assertEqual(bio.read(2), b'ba')
        self.assertEqual(bio.read(1), b'z')
        self.assertEqual(bio.read(1), b'')

    eleza test_eof(self):
        bio = ssl.MemoryBIO()
        self.assertUongo(bio.eof)
        self.assertEqual(bio.read(), b'')
        self.assertUongo(bio.eof)
        bio.write(b'foo')
        self.assertUongo(bio.eof)
        bio.write_eof()
        self.assertUongo(bio.eof)
        self.assertEqual(bio.read(2), b'fo')
        self.assertUongo(bio.eof)
        self.assertEqual(bio.read(1), b'o')
        self.assertKweli(bio.eof)
        self.assertEqual(bio.read(), b'')
        self.assertKweli(bio.eof)

    eleza test_pending(self):
        bio = ssl.MemoryBIO()
        self.assertEqual(bio.pending, 0)
        bio.write(b'foo')
        self.assertEqual(bio.pending, 3)
        kila i kwenye range(3):
            bio.read(1)
            self.assertEqual(bio.pending, 3-i-1)
        kila i kwenye range(3):
            bio.write(b'x')
            self.assertEqual(bio.pending, i+1)
        bio.read()
        self.assertEqual(bio.pending, 0)

    eleza test_buffer_types(self):
        bio = ssl.MemoryBIO()
        bio.write(b'foo')
        self.assertEqual(bio.read(), b'foo')
        bio.write(bytearray(b'bar'))
        self.assertEqual(bio.read(), b'bar')
        bio.write(memoryview(b'baz'))
        self.assertEqual(bio.read(), b'baz')

    eleza test_error_types(self):
        bio = ssl.MemoryBIO()
        self.assertRaises(TypeError, bio.write, 'foo')
        self.assertRaises(TypeError, bio.write, Tupu)
        self.assertRaises(TypeError, bio.write, Kweli)
        self.assertRaises(TypeError, bio.write, 1)


kundi SSLObjectTests(unittest.TestCase):
    eleza test_private_init(self):
        bio = ssl.MemoryBIO()
        ukijumuisha self.assertRaisesRegex(TypeError, "public constructor"):
            ssl.SSLObject(bio, bio)

    eleza test_unwrap(self):
        client_ctx, server_ctx, hostname = testing_context()
        c_in = ssl.MemoryBIO()
        c_out = ssl.MemoryBIO()
        s_in = ssl.MemoryBIO()
        s_out = ssl.MemoryBIO()
        client = client_ctx.wrap_bio(c_in, c_out, server_hostname=hostname)
        server = server_ctx.wrap_bio(s_in, s_out, server_side=Kweli)

        # Loop on the handshake kila a bit to get it settled
        kila _ kwenye range(5):
            jaribu:
                client.do_handshake()
            tatizo ssl.SSLWantReadError:
                pita
            ikiwa c_out.pending:
                s_in.write(c_out.read())
            jaribu:
                server.do_handshake()
            tatizo ssl.SSLWantReadError:
                pita
            ikiwa s_out.pending:
                c_in.write(s_out.read())
        # Now the handshakes should be complete (don't ashiria WantReadError)
        client.do_handshake()
        server.do_handshake()

        # Now ikiwa we unwrap one side unilaterally, it should send close-notify
        # na ashiria WantReadError:
        ukijumuisha self.assertRaises(ssl.SSLWantReadError):
            client.unwrap()

        # But server.unwrap() does sio raise, because it reads the client's
        # close-notify:
        s_in.write(c_out.read())
        server.unwrap()

        # And now that the client gets the server's close-notify, it doesn't
        # ashiria either.
        c_in.write(s_out.read())
        client.unwrap()

kundi SimpleBackgroundTests(unittest.TestCase):
    """Tests that connect to a simple server running kwenye the background"""

    eleza setUp(self):
        server = ThreadedEchoServer(SIGNED_CERTFILE)
        self.server_addr = (HOST, server.port)
        server.__enter__()
        self.addCleanup(server.__exit__, Tupu, Tupu, Tupu)

    eleza test_connect(self):
        ukijumuisha test_wrap_socket(socket.socket(socket.AF_INET),
                            cert_reqs=ssl.CERT_NONE) kama s:
            s.connect(self.server_addr)
            self.assertEqual({}, s.getpeercert())
            self.assertUongo(s.server_side)

        # this should succeed because we specify the root cert
        ukijumuisha test_wrap_socket(socket.socket(socket.AF_INET),
                            cert_reqs=ssl.CERT_REQUIRED,
                            ca_certs=SIGNING_CA) kama s:
            s.connect(self.server_addr)
            self.assertKweli(s.getpeercert())
            self.assertUongo(s.server_side)

    eleza test_connect_fail(self):
        # This should fail because we have no verification certs. Connection
        # failure crashes ThreadedEchoServer, so run this kwenye an independent
        # test method.
        s = test_wrap_socket(socket.socket(socket.AF_INET),
                            cert_reqs=ssl.CERT_REQUIRED)
        self.addCleanup(s.close)
        self.assertRaisesRegex(ssl.SSLError, "certificate verify failed",
                               s.connect, self.server_addr)

    eleza test_connect_ex(self):
        # Issue #11326: check connect_ex() implementation
        s = test_wrap_socket(socket.socket(socket.AF_INET),
                            cert_reqs=ssl.CERT_REQUIRED,
                            ca_certs=SIGNING_CA)
        self.addCleanup(s.close)
        self.assertEqual(0, s.connect_ex(self.server_addr))
        self.assertKweli(s.getpeercert())

    eleza test_non_blocking_connect_ex(self):
        # Issue #11326: non-blocking connect_ex() should allow handshake
        # to proceed after the socket gets ready.
        s = test_wrap_socket(socket.socket(socket.AF_INET),
                            cert_reqs=ssl.CERT_REQUIRED,
                            ca_certs=SIGNING_CA,
                            do_handshake_on_connect=Uongo)
        self.addCleanup(s.close)
        s.setblocking(Uongo)
        rc = s.connect_ex(self.server_addr)
        # EWOULDBLOCK under Windows, EINPROGRESS elsewhere
        self.assertIn(rc, (0, errno.EINPROGRESS, errno.EWOULDBLOCK))
        # Wait kila connect to finish
        select.select([], [s], [], 5.0)
        # Non-blocking handshake
        wakati Kweli:
            jaribu:
                s.do_handshake()
                koma
            tatizo ssl.SSLWantReadError:
                select.select([s], [], [], 5.0)
            tatizo ssl.SSLWantWriteError:
                select.select([], [s], [], 5.0)
        # SSL established
        self.assertKweli(s.getpeercert())

    eleza test_connect_with_context(self):
        # Same kama test_connect, but ukijumuisha a separately created context
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ukijumuisha ctx.wrap_socket(socket.socket(socket.AF_INET)) kama s:
            s.connect(self.server_addr)
            self.assertEqual({}, s.getpeercert())
        # Same ukijumuisha a server hostname
        ukijumuisha ctx.wrap_socket(socket.socket(socket.AF_INET),
                            server_hostname="dummy") kama s:
            s.connect(self.server_addr)
        ctx.verify_mode = ssl.CERT_REQUIRED
        # This should succeed because we specify the root cert
        ctx.load_verify_locations(SIGNING_CA)
        ukijumuisha ctx.wrap_socket(socket.socket(socket.AF_INET)) kama s:
            s.connect(self.server_addr)
            cert = s.getpeercert()
            self.assertKweli(cert)

    eleza test_connect_with_context_fail(self):
        # This should fail because we have no verification certs. Connection
        # failure crashes ThreadedEchoServer, so run this kwenye an independent
        # test method.
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.verify_mode = ssl.CERT_REQUIRED
        s = ctx.wrap_socket(socket.socket(socket.AF_INET))
        self.addCleanup(s.close)
        self.assertRaisesRegex(ssl.SSLError, "certificate verify failed",
                                s.connect, self.server_addr)

    eleza test_connect_capath(self):
        # Verify server certificates using the `capath` argument
        # NOTE: the subject hashing algorithm has been changed between
        # OpenSSL 0.9.8n na 1.0.0, kama a result the capath directory must
        # contain both versions of each certificate (same content, different
        # filename) kila this test to be portable across OpenSSL releases.
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(capath=CAPATH)
        ukijumuisha ctx.wrap_socket(socket.socket(socket.AF_INET)) kama s:
            s.connect(self.server_addr)
            cert = s.getpeercert()
            self.assertKweli(cert)

        # Same ukijumuisha a bytes `capath` argument
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(capath=BYTES_CAPATH)
        ukijumuisha ctx.wrap_socket(socket.socket(socket.AF_INET)) kama s:
            s.connect(self.server_addr)
            cert = s.getpeercert()
            self.assertKweli(cert)

    eleza test_connect_cadata(self):
        ukijumuisha open(SIGNING_CA) kama f:
            pem = f.read()
        der = ssl.PEM_cert_to_DER_cert(pem)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(cadata=pem)
        ukijumuisha ctx.wrap_socket(socket.socket(socket.AF_INET)) kama s:
            s.connect(self.server_addr)
            cert = s.getpeercert()
            self.assertKweli(cert)

        # same ukijumuisha DER
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(cadata=der)
        ukijumuisha ctx.wrap_socket(socket.socket(socket.AF_INET)) kama s:
            s.connect(self.server_addr)
            cert = s.getpeercert()
            self.assertKweli(cert)

    @unittest.skipIf(os.name == "nt", "Can't use a socket kama a file under Windows")
    eleza test_makefile_close(self):
        # Issue #5238: creating a file-like object ukijumuisha makefile() shouldn't
        # delay closing the underlying "real socket" (here tested ukijumuisha its
        # file descriptor, hence skipping the test under Windows).
        ss = test_wrap_socket(socket.socket(socket.AF_INET))
        ss.connect(self.server_addr)
        fd = ss.fileno()
        f = ss.makefile()
        f.close()
        # The fd ni still open
        os.read(fd, 0)
        # Closing the SSL socket should close the fd too
        ss.close()
        gc.collect()
        ukijumuisha self.assertRaises(OSError) kama e:
            os.read(fd, 0)
        self.assertEqual(e.exception.errno, errno.EBADF)

    eleza test_non_blocking_handshake(self):
        s = socket.socket(socket.AF_INET)
        s.connect(self.server_addr)
        s.setblocking(Uongo)
        s = test_wrap_socket(s,
                            cert_reqs=ssl.CERT_NONE,
                            do_handshake_on_connect=Uongo)
        self.addCleanup(s.close)
        count = 0
        wakati Kweli:
            jaribu:
                count += 1
                s.do_handshake()
                koma
            tatizo ssl.SSLWantReadError:
                select.select([s], [], [])
            tatizo ssl.SSLWantWriteError:
                select.select([], [s], [])
        ikiwa support.verbose:
            sys.stdout.write("\nNeeded %d calls to do_handshake() to establish session.\n" % count)

    eleza test_get_server_certificate(self):
        _test_get_server_certificate(self, *self.server_addr, cert=SIGNING_CA)

    eleza test_get_server_certificate_fail(self):
        # Connection failure crashes ThreadedEchoServer, so run this kwenye an
        # independent test method
        _test_get_server_certificate_fail(self, *self.server_addr)

    eleza test_ciphers(self):
        ukijumuisha test_wrap_socket(socket.socket(socket.AF_INET),
                             cert_reqs=ssl.CERT_NONE, ciphers="ALL") kama s:
            s.connect(self.server_addr)
        ukijumuisha test_wrap_socket(socket.socket(socket.AF_INET),
                             cert_reqs=ssl.CERT_NONE, ciphers="DEFAULT") kama s:
            s.connect(self.server_addr)
        # Error checking can happen at instantiation ama when connecting
        ukijumuisha self.assertRaisesRegex(ssl.SSLError, "No cipher can be selected"):
            ukijumuisha socket.socket(socket.AF_INET) kama sock:
                s = test_wrap_socket(sock,
                                    cert_reqs=ssl.CERT_NONE, ciphers="^$:,;?*'dorothyx")
                s.connect(self.server_addr)

    eleza test_get_ca_certs_capath(self):
        # capath certs are loaded on request
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(capath=CAPATH)
        self.assertEqual(ctx.get_ca_certs(), [])
        ukijumuisha ctx.wrap_socket(socket.socket(socket.AF_INET),
                             server_hostname='localhost') kama s:
            s.connect(self.server_addr)
            cert = s.getpeercert()
            self.assertKweli(cert)
        self.assertEqual(len(ctx.get_ca_certs()), 1)

    @needs_sni
    eleza test_context_setget(self):
        # Check that the context of a connected socket can be replaced.
        ctx1 = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx1.load_verify_locations(capath=CAPATH)
        ctx2 = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx2.load_verify_locations(capath=CAPATH)
        s = socket.socket(socket.AF_INET)
        ukijumuisha ctx1.wrap_socket(s, server_hostname='localhost') kama ss:
            ss.connect(self.server_addr)
            self.assertIs(ss.context, ctx1)
            self.assertIs(ss._sslobj.context, ctx1)
            ss.context = ctx2
            self.assertIs(ss.context, ctx2)
            self.assertIs(ss._sslobj.context, ctx2)

    eleza ssl_io_loop(self, sock, incoming, outgoing, func, *args, **kwargs):
        # A simple IO loop. Call func(*args) depending on the error we get
        # (WANT_READ ama WANT_WRITE) move data between the socket na the BIOs.
        timeout = kwargs.get('timeout', 10)
        deadline = time.monotonic() + timeout
        count = 0
        wakati Kweli:
            ikiwa time.monotonic() > deadline:
                self.fail("timeout")
            errno = Tupu
            count += 1
            jaribu:
                ret = func(*args)
            tatizo ssl.SSLError kama e:
                ikiwa e.errno haiko kwenye (ssl.SSL_ERROR_WANT_READ,
                                   ssl.SSL_ERROR_WANT_WRITE):
                    raise
                errno = e.errno
            # Get any data kutoka the outgoing BIO irrespective of any error, na
            # send it to the socket.
            buf = outgoing.read()
            sock.sendall(buf)
            # If there's no error, we're done. For WANT_READ, we need to get
            # data kutoka the socket na put it kwenye the incoming BIO.
            ikiwa errno ni Tupu:
                koma
            lasivyo errno == ssl.SSL_ERROR_WANT_READ:
                buf = sock.recv(32768)
                ikiwa buf:
                    incoming.write(buf)
                isipokua:
                    incoming.write_eof()
        ikiwa support.verbose:
            sys.stdout.write("Needed %d calls to complete %s().\n"
                             % (count, func.__name__))
        rudisha ret

    eleza test_bio_handshake(self):
        sock = socket.socket(socket.AF_INET)
        self.addCleanup(sock.close)
        sock.connect(self.server_addr)
        incoming = ssl.MemoryBIO()
        outgoing = ssl.MemoryBIO()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertKweli(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        ctx.load_verify_locations(SIGNING_CA)
        sslobj = ctx.wrap_bio(incoming, outgoing, Uongo,
                              SIGNED_CERTFILE_HOSTNAME)
        self.assertIs(sslobj._sslobj.owner, sslobj)
        self.assertIsTupu(sslobj.cipher())
        self.assertIsTupu(sslobj.version())
        self.assertIsNotTupu(sslobj.shared_ciphers())
        self.assertRaises(ValueError, sslobj.getpeercert)
        ikiwa 'tls-unique' kwenye ssl.CHANNEL_BINDING_TYPES:
            self.assertIsTupu(sslobj.get_channel_binding('tls-unique'))
        self.ssl_io_loop(sock, incoming, outgoing, sslobj.do_handshake)
        self.assertKweli(sslobj.cipher())
        self.assertIsNotTupu(sslobj.shared_ciphers())
        self.assertIsNotTupu(sslobj.version())
        self.assertKweli(sslobj.getpeercert())
        ikiwa 'tls-unique' kwenye ssl.CHANNEL_BINDING_TYPES:
            self.assertKweli(sslobj.get_channel_binding('tls-unique'))
        jaribu:
            self.ssl_io_loop(sock, incoming, outgoing, sslobj.unwrap)
        tatizo ssl.SSLSyscallError:
            # If the server shuts down the TCP connection without sending a
            # secure shutdown message, this ni reported kama SSL_ERROR_SYSCALL
            pita
        self.assertRaises(ssl.SSLError, sslobj.write, b'foo')

    eleza test_bio_read_write_data(self):
        sock = socket.socket(socket.AF_INET)
        self.addCleanup(sock.close)
        sock.connect(self.server_addr)
        incoming = ssl.MemoryBIO()
        outgoing = ssl.MemoryBIO()
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.verify_mode = ssl.CERT_NONE
        sslobj = ctx.wrap_bio(incoming, outgoing, Uongo)
        self.ssl_io_loop(sock, incoming, outgoing, sslobj.do_handshake)
        req = b'FOO\n'
        self.ssl_io_loop(sock, incoming, outgoing, sslobj.write, req)
        buf = self.ssl_io_loop(sock, incoming, outgoing, sslobj.read, 1024)
        self.assertEqual(buf, b'foo\n')
        self.ssl_io_loop(sock, incoming, outgoing, sslobj.unwrap)


kundi NetworkedTests(unittest.TestCase):

    eleza test_timeout_connect_ex(self):
        # Issue #12065: on a timeout, connect_ex() should rudisha the original
        # errno (mimicking the behaviour of non-SSL sockets).
        ukijumuisha support.transient_internet(REMOTE_HOST):
            s = test_wrap_socket(socket.socket(socket.AF_INET),
                                cert_reqs=ssl.CERT_REQUIRED,
                                do_handshake_on_connect=Uongo)
            self.addCleanup(s.close)
            s.settimeout(0.0000001)
            rc = s.connect_ex((REMOTE_HOST, 443))
            ikiwa rc == 0:
                self.skipTest("REMOTE_HOST responded too quickly")
            self.assertIn(rc, (errno.EAGAIN, errno.EWOULDBLOCK))

    @unittest.skipUnless(support.IPV6_ENABLED, 'Needs IPv6')
    eleza test_get_server_certificate_ipv6(self):
        ukijumuisha support.transient_internet('ipv6.google.com'):
            _test_get_server_certificate(self, 'ipv6.google.com', 443)
            _test_get_server_certificate_fail(self, 'ipv6.google.com', 443)


eleza _test_get_server_certificate(test, host, port, cert=Tupu):
    pem = ssl.get_server_certificate((host, port))
    ikiwa sio pem:
        test.fail("No server certificate on %s:%s!" % (host, port))

    pem = ssl.get_server_certificate((host, port), ca_certs=cert)
    ikiwa sio pem:
        test.fail("No server certificate on %s:%s!" % (host, port))
    ikiwa support.verbose:
        sys.stdout.write("\nVerified certificate kila %s:%s is\n%s\n" % (host, port ,pem))

eleza _test_get_server_certificate_fail(test, host, port):
    jaribu:
        pem = ssl.get_server_certificate((host, port), ca_certs=CERTFILE)
    tatizo ssl.SSLError kama x:
        #should fail
        ikiwa support.verbose:
            sys.stdout.write("%s\n" % x)
    isipokua:
        test.fail("Got server certificate %s kila %s:%s!" % (pem, host, port))


kutoka test.ssl_servers agiza make_https_server

kundi ThreadedEchoServer(threading.Thread):

    kundi ConnectionHandler(threading.Thread):

        """A mildly complicated class, because we want it to work both
        ukijumuisha na without the SSL wrapper around the socket connection, so
        that we can test the STARTTLS functionality."""

        eleza __init__(self, server, connsock, addr):
            self.server = server
            self.running = Uongo
            self.sock = connsock
            self.addr = addr
            self.sock.setblocking(1)
            self.sslconn = Tupu
            threading.Thread.__init__(self)
            self.daemon = Kweli

        eleza wrap_conn(self):
            jaribu:
                self.sslconn = self.server.context.wrap_socket(
                    self.sock, server_side=Kweli)
                self.server.selected_npn_protocols.append(self.sslconn.selected_npn_protocol())
                self.server.selected_alpn_protocols.append(self.sslconn.selected_alpn_protocol())
            tatizo (ConnectionResetError, BrokenPipeError, ConnectionAbortedError) kama e:
                # We treat ConnectionResetError kama though it were an
                # SSLError - OpenSSL on Ubuntu abruptly closes the
                # connection when asked to use an unsupported protocol.
                #
                # BrokenPipeError ni raised kwenye TLS 1.3 mode, when OpenSSL
                # tries to send session tickets after handshake.
                # https://github.com/openssl/openssl/issues/6342
                #
                # ConnectionAbortedError ni raised kwenye TLS 1.3 mode, when OpenSSL
                # tries to send session tickets after handshake when using WinSock.
                self.server.conn_errors.append(str(e))
                ikiwa self.server.chatty:
                    handle_error("\n server:  bad connection attempt kutoka " + repr(self.addr) + ":\n")
                self.running = Uongo
                self.close()
                rudisha Uongo
            tatizo (ssl.SSLError, OSError) kama e:
                # OSError may occur ukijumuisha wrong protocols, e.g. both
                # sides use PROTOCOL_TLS_SERVER.
                #
                # XXX Various errors can have happened here, kila example
                # a mismatching protocol version, an invalid certificate,
                # ama a low-level bug. This should be made more discriminating.
                #
                # bpo-31323: Store the exception kama string to prevent
                # a reference leak: server -> conn_errors -> exception
                # -> traceback -> self (ConnectionHandler) -> server
                self.server.conn_errors.append(str(e))
                ikiwa self.server.chatty:
                    handle_error("\n server:  bad connection attempt kutoka " + repr(self.addr) + ":\n")
                self.running = Uongo
                self.server.stop()
                self.close()
                rudisha Uongo
            isipokua:
                self.server.shared_ciphers.append(self.sslconn.shared_ciphers())
                ikiwa self.server.context.verify_mode == ssl.CERT_REQUIRED:
                    cert = self.sslconn.getpeercert()
                    ikiwa support.verbose na self.server.chatty:
                        sys.stdout.write(" client cert ni " + pprint.pformat(cert) + "\n")
                    cert_binary = self.sslconn.getpeercert(Kweli)
                    ikiwa support.verbose na self.server.chatty:
                        sys.stdout.write(" cert binary ni " + str(len(cert_binary)) + " bytes\n")
                cipher = self.sslconn.cipher()
                ikiwa support.verbose na self.server.chatty:
                    sys.stdout.write(" server: connection cipher ni now " + str(cipher) + "\n")
                    sys.stdout.write(" server: selected protocol ni now "
                            + str(self.sslconn.selected_npn_protocol()) + "\n")
                rudisha Kweli

        eleza read(self):
            ikiwa self.sslconn:
                rudisha self.sslconn.read()
            isipokua:
                rudisha self.sock.recv(1024)

        eleza write(self, bytes):
            ikiwa self.sslconn:
                rudisha self.sslconn.write(bytes)
            isipokua:
                rudisha self.sock.send(bytes)

        eleza close(self):
            ikiwa self.sslconn:
                self.sslconn.close()
            isipokua:
                self.sock.close()

        eleza run(self):
            self.running = Kweli
            ikiwa sio self.server.starttls_server:
                ikiwa sio self.wrap_conn():
                    return
            wakati self.running:
                jaribu:
                    msg = self.read()
                    stripped = msg.strip()
                    ikiwa sio stripped:
                        # eof, so quit this handler
                        self.running = Uongo
                        jaribu:
                            self.sock = self.sslconn.unwrap()
                        tatizo OSError:
                            # Many tests shut the TCP connection down
                            # without an SSL shutdown. This causes
                            # unwrap() to ashiria OSError ukijumuisha errno=0!
                            pita
                        isipokua:
                            self.sslconn = Tupu
                        self.close()
                    lasivyo stripped == b'over':
                        ikiwa support.verbose na self.server.connectionchatty:
                            sys.stdout.write(" server: client closed connection\n")
                        self.close()
                        return
                    lasivyo (self.server.starttls_server na
                          stripped == b'STARTTLS'):
                        ikiwa support.verbose na self.server.connectionchatty:
                            sys.stdout.write(" server: read STARTTLS kutoka client, sending OK...\n")
                        self.write(b"OK\n")
                        ikiwa sio self.wrap_conn():
                            return
                    lasivyo (self.server.starttls_server na self.sslconn
                          na stripped == b'ENDTLS'):
                        ikiwa support.verbose na self.server.connectionchatty:
                            sys.stdout.write(" server: read ENDTLS kutoka client, sending OK...\n")
                        self.write(b"OK\n")
                        self.sock = self.sslconn.unwrap()
                        self.sslconn = Tupu
                        ikiwa support.verbose na self.server.connectionchatty:
                            sys.stdout.write(" server: connection ni now unencrypted...\n")
                    lasivyo stripped == b'CB tls-unique':
                        ikiwa support.verbose na self.server.connectionchatty:
                            sys.stdout.write(" server: read CB tls-unique kutoka client, sending our CB data...\n")
                        data = self.sslconn.get_channel_binding("tls-unique")
                        self.write(repr(data).encode("us-ascii") + b"\n")
                    lasivyo stripped == b'PHA':
                        ikiwa support.verbose na self.server.connectionchatty:
                            sys.stdout.write(" server: initiating post handshake auth\n")
                        jaribu:
                            self.sslconn.verify_client_post_handshake()
                        tatizo ssl.SSLError kama e:
                            self.write(repr(e).encode("us-ascii") + b"\n")
                        isipokua:
                            self.write(b"OK\n")
                    lasivyo stripped == b'HASCERT':
                        ikiwa self.sslconn.getpeercert() ni sio Tupu:
                            self.write(b'TRUE\n')
                        isipokua:
                            self.write(b'FALSE\n')
                    lasivyo stripped == b'GETCERT':
                        cert = self.sslconn.getpeercert()
                        self.write(repr(cert).encode("us-ascii") + b"\n")
                    isipokua:
                        ikiwa (support.verbose na
                            self.server.connectionchatty):
                            ctype = (self.sslconn na "encrypted") ama "unencrypted"
                            sys.stdout.write(" server: read %r (%s), sending back %r (%s)...\n"
                                             % (msg, ctype, msg.lower(), ctype))
                        self.write(msg.lower())
                tatizo (ConnectionResetError, ConnectionAbortedError):
                    # XXX: OpenSSL 1.1.1 sometimes raises ConnectionResetError
                    # when connection ni sio shut down gracefully.
                    ikiwa self.server.chatty na support.verbose:
                        sys.stdout.write(
                            " Connection reset by peer: {}\n".format(
                                self.addr)
                        )
                    self.close()
                    self.running = Uongo
                tatizo ssl.SSLError kama err:
                    # On Windows sometimes test_pha_required_nocert receives the
                    # PEER_DID_NOT_RETURN_A_CERTIFICATE exception
                    # before the 'tlsv13 alert certificate required' exception.
                    # If the server ni stopped when PEER_DID_NOT_RETURN_A_CERTIFICATE
                    # ni received test_pha_required_nocert fails ukijumuisha ConnectionResetError
                    # because the underlying socket ni closed
                    ikiwa 'PEER_DID_NOT_RETURN_A_CERTIFICATE' == err.reason:
                        ikiwa self.server.chatty na support.verbose:
                            sys.stdout.write(err.args[1])
                        # test_pha_required_nocert ni expecting this exception
                        ashiria ssl.SSLError('tlsv13 alert certificate required')
                tatizo OSError:
                    ikiwa self.server.chatty:
                        handle_error("Test server failure:\n")
                    self.close()
                    self.running = Uongo

                    # normally, we'd just stop here, but kila the test
                    # harness, we want to stop the server
                    self.server.stop()

    eleza __init__(self, certificate=Tupu, ssl_version=Tupu,
                 certreqs=Tupu, cacerts=Tupu,
                 chatty=Kweli, connectionchatty=Uongo, starttls_server=Uongo,
                 npn_protocols=Tupu, alpn_protocols=Tupu,
                 ciphers=Tupu, context=Tupu):
        ikiwa context:
            self.context = context
        isipokua:
            self.context = ssl.SSLContext(ssl_version
                                          ikiwa ssl_version ni sio Tupu
                                          isipokua ssl.PROTOCOL_TLS_SERVER)
            self.context.verify_mode = (certreqs ikiwa certreqs ni sio Tupu
                                        isipokua ssl.CERT_NONE)
            ikiwa cacerts:
                self.context.load_verify_locations(cacerts)
            ikiwa certificate:
                self.context.load_cert_chain(certificate)
            ikiwa npn_protocols:
                self.context.set_npn_protocols(npn_protocols)
            ikiwa alpn_protocols:
                self.context.set_alpn_protocols(alpn_protocols)
            ikiwa ciphers:
                self.context.set_ciphers(ciphers)
        self.chatty = chatty
        self.connectionchatty = connectionchatty
        self.starttls_server = starttls_server
        self.sock = socket.socket()
        self.port = support.bind_port(self.sock)
        self.flag = Tupu
        self.active = Uongo
        self.selected_npn_protocols = []
        self.selected_alpn_protocols = []
        self.shared_ciphers = []
        self.conn_errors = []
        threading.Thread.__init__(self)
        self.daemon = Kweli

    eleza __enter__(self):
        self.start(threading.Event())
        self.flag.wait()
        rudisha self

    eleza __exit__(self, *args):
        self.stop()
        self.join()

    eleza start(self, flag=Tupu):
        self.flag = flag
        threading.Thread.start(self)

    eleza run(self):
        self.sock.settimeout(0.05)
        self.sock.listen()
        self.active = Kweli
        ikiwa self.flag:
            # signal an event
            self.flag.set()
        wakati self.active:
            jaribu:
                newconn, connaddr = self.sock.accept()
                ikiwa support.verbose na self.chatty:
                    sys.stdout.write(' server:  new connection kutoka '
                                     + repr(connaddr) + '\n')
                handler = self.ConnectionHandler(self, newconn, connaddr)
                handler.start()
                handler.join()
            tatizo socket.timeout:
                pita
            tatizo KeyboardInterrupt:
                self.stop()
            tatizo BaseException kama e:
                ikiwa support.verbose na self.chatty:
                    sys.stdout.write(
                        ' connection handling failed: ' + repr(e) + '\n')

        self.sock.close()

    eleza stop(self):
        self.active = Uongo

kundi AsyncoreEchoServer(threading.Thread):

    # this one's based on asyncore.dispatcher

    kundi EchoServer (asyncore.dispatcher):

        kundi ConnectionHandler(asyncore.dispatcher_with_send):

            eleza __init__(self, conn, certfile):
                self.socket = test_wrap_socket(conn, server_side=Kweli,
                                              certfile=certfile,
                                              do_handshake_on_connect=Uongo)
                asyncore.dispatcher_with_send.__init__(self, self.socket)
                self._ssl_accepting = Kweli
                self._do_ssl_handshake()

            eleza readable(self):
                ikiwa isinstance(self.socket, ssl.SSLSocket):
                    wakati self.socket.pending() > 0:
                        self.handle_read_event()
                rudisha Kweli

            eleza _do_ssl_handshake(self):
                jaribu:
                    self.socket.do_handshake()
                tatizo (ssl.SSLWantReadError, ssl.SSLWantWriteError):
                    return
                tatizo ssl.SSLEOFError:
                    rudisha self.handle_close()
                tatizo ssl.SSLError:
                    raise
                tatizo OSError kama err:
                    ikiwa err.args[0] == errno.ECONNABORTED:
                        rudisha self.handle_close()
                isipokua:
                    self._ssl_accepting = Uongo

            eleza handle_read(self):
                ikiwa self._ssl_accepting:
                    self._do_ssl_handshake()
                isipokua:
                    data = self.recv(1024)
                    ikiwa support.verbose:
                        sys.stdout.write(" server:  read %s kutoka client\n" % repr(data))
                    ikiwa sio data:
                        self.close()
                    isipokua:
                        self.send(data.lower())

            eleza handle_close(self):
                self.close()
                ikiwa support.verbose:
                    sys.stdout.write(" server:  closed connection %s\n" % self.socket)

            eleza handle_error(self):
                raise

        eleza __init__(self, certfile):
            self.certfile = certfile
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.port = support.bind_port(sock, '')
            asyncore.dispatcher.__init__(self, sock)
            self.listen(5)

        eleza handle_accepted(self, sock_obj, addr):
            ikiwa support.verbose:
                sys.stdout.write(" server:  new connection kutoka %s:%s\n" %addr)
            self.ConnectionHandler(sock_obj, self.certfile)

        eleza handle_error(self):
            raise

    eleza __init__(self, certfile):
        self.flag = Tupu
        self.active = Uongo
        self.server = self.EchoServer(certfile)
        self.port = self.server.port
        threading.Thread.__init__(self)
        self.daemon = Kweli

    eleza __str__(self):
        rudisha "<%s %s>" % (self.__class__.__name__, self.server)

    eleza __enter__(self):
        self.start(threading.Event())
        self.flag.wait()
        rudisha self

    eleza __exit__(self, *args):
        ikiwa support.verbose:
            sys.stdout.write(" cleanup: stopping server.\n")
        self.stop()
        ikiwa support.verbose:
            sys.stdout.write(" cleanup: joining server thread.\n")
        self.join()
        ikiwa support.verbose:
            sys.stdout.write(" cleanup: successfully joined.\n")
        # make sure that ConnectionHandler ni removed kutoka socket_map
        asyncore.close_all(ignore_all=Kweli)

    eleza start (self, flag=Tupu):
        self.flag = flag
        threading.Thread.start(self)

    eleza run(self):
        self.active = Kweli
        ikiwa self.flag:
            self.flag.set()
        wakati self.active:
            jaribu:
                asyncore.loop(1)
            tatizo:
                pita

    eleza stop(self):
        self.active = Uongo
        self.server.close()

eleza server_params_test(client_context, server_context, indata=b"FOO\n",
                       chatty=Kweli, connectionchatty=Uongo, sni_name=Tupu,
                       session=Tupu):
    """
    Launch a server, connect a client to it na try various reads
    na writes.
    """
    stats = {}
    server = ThreadedEchoServer(context=server_context,
                                chatty=chatty,
                                connectionchatty=Uongo)
    ukijumuisha server:
        ukijumuisha client_context.wrap_socket(socket.socket(),
                server_hostname=sni_name, session=session) kama s:
            s.connect((HOST, server.port))
            kila arg kwenye [indata, bytearray(indata), memoryview(indata)]:
                ikiwa connectionchatty:
                    ikiwa support.verbose:
                        sys.stdout.write(
                            " client:  sending %r...\n" % indata)
                s.write(arg)
                outdata = s.read()
                ikiwa connectionchatty:
                    ikiwa support.verbose:
                        sys.stdout.write(" client:  read %r\n" % outdata)
                ikiwa outdata != indata.lower():
                    ashiria AssertionError(
                        "bad data <<%r>> (%d) received; expected <<%r>> (%d)\n"
                        % (outdata[:20], len(outdata),
                           indata[:20].lower(), len(indata)))
            s.write(b"over\n")
            ikiwa connectionchatty:
                ikiwa support.verbose:
                    sys.stdout.write(" client:  closing connection.\n")
            stats.update({
                'compression': s.compression(),
                'cipher': s.cipher(),
                'peercert': s.getpeercert(),
                'client_alpn_protocol': s.selected_alpn_protocol(),
                'client_npn_protocol': s.selected_npn_protocol(),
                'version': s.version(),
                'session_reused': s.session_reused,
                'session': s.session,
            })
            s.close()
        stats['server_alpn_protocols'] = server.selected_alpn_protocols
        stats['server_npn_protocols'] = server.selected_npn_protocols
        stats['server_shared_ciphers'] = server.shared_ciphers
    rudisha stats

eleza try_protocol_combo(server_protocol, client_protocol, expect_success,
                       certsreqs=Tupu, server_options=0, client_options=0):
    """
    Try to SSL-connect using *client_protocol* to *server_protocol*.
    If *expect_success* ni true, assert that the connection succeeds,
    ikiwa it's false, assert that the connection fails.
    Also, ikiwa *expect_success* ni a string, assert that it ni the protocol
    version actually used by the connection.
    """
    ikiwa certsreqs ni Tupu:
        certsreqs = ssl.CERT_NONE
    certtype = {
        ssl.CERT_NONE: "CERT_NONE",
        ssl.CERT_OPTIONAL: "CERT_OPTIONAL",
        ssl.CERT_REQUIRED: "CERT_REQUIRED",
    }[certsreqs]
    ikiwa support.verbose:
        formatstr = (expect_success na " %s->%s %s\n") ama " {%s->%s} %s\n"
        sys.stdout.write(formatstr %
                         (ssl.get_protocol_name(client_protocol),
                          ssl.get_protocol_name(server_protocol),
                          certtype))
    client_context = ssl.SSLContext(client_protocol)
    client_context.options |= client_options
    server_context = ssl.SSLContext(server_protocol)
    server_context.options |= server_options

    min_version = PROTOCOL_TO_TLS_VERSION.get(client_protocol, Tupu)
    ikiwa (min_version ni sio Tupu
    # SSLContext.minimum_version ni only available on recent OpenSSL
    # (setter added kwenye OpenSSL 1.1.0, getter added kwenye OpenSSL 1.1.1)
    na hasattr(server_context, 'minimum_version')
    na server_protocol == ssl.PROTOCOL_TLS
    na server_context.minimum_version > min_version):
        # If OpenSSL configuration ni strict na requires more recent TLS
        # version, we have to change the minimum to test old TLS versions.
        server_context.minimum_version = min_version

    # NOTE: we must enable "ALL" ciphers on the client, otherwise an
    # SSLv23 client will send an SSLv3 hello (rather than SSLv2)
    # starting kutoka OpenSSL 1.0.0 (see issue #8322).
    ikiwa client_context.protocol == ssl.PROTOCOL_TLS:
        client_context.set_ciphers("ALL")

    kila ctx kwenye (client_context, server_context):
        ctx.verify_mode = certsreqs
        ctx.load_cert_chain(SIGNED_CERTFILE)
        ctx.load_verify_locations(SIGNING_CA)
    jaribu:
        stats = server_params_test(client_context, server_context,
                                   chatty=Uongo, connectionchatty=Uongo)
    # Protocol mismatch can result kwenye either an SSLError, ama a
    # "Connection reset by peer" error.
    tatizo ssl.SSLError:
        ikiwa expect_success:
            raise
    tatizo OSError kama e:
        ikiwa expect_success ama e.errno != errno.ECONNRESET:
            raise
    isipokua:
        ikiwa sio expect_success:
            ashiria AssertionError(
                "Client protocol %s succeeded ukijumuisha server protocol %s!"
                % (ssl.get_protocol_name(client_protocol),
                   ssl.get_protocol_name(server_protocol)))
        lasivyo (expect_success ni sio Kweli
              na expect_success != stats['version']):
            ashiria AssertionError("version mismatch: expected %r, got %r"
                                 % (expect_success, stats['version']))


kundi ThreadedTests(unittest.TestCase):

    eleza test_echo(self):
        """Basic test of an SSL client connecting to a server"""
        ikiwa support.verbose:
            sys.stdout.write("\n")
        kila protocol kwenye PROTOCOLS:
            ikiwa protocol kwenye {ssl.PROTOCOL_TLS_CLIENT, ssl.PROTOCOL_TLS_SERVER}:
                endelea
            ikiwa sio has_tls_protocol(protocol):
                endelea
            ukijumuisha self.subTest(protocol=ssl._PROTOCOL_NAMES[protocol]):
                context = ssl.SSLContext(protocol)
                context.load_cert_chain(CERTFILE)
                server_params_test(context, context,
                                   chatty=Kweli, connectionchatty=Kweli)

        client_context, server_context, hostname = testing_context()

        ukijumuisha self.subTest(client=ssl.PROTOCOL_TLS_CLIENT, server=ssl.PROTOCOL_TLS_SERVER):
            server_params_test(client_context=client_context,
                               server_context=server_context,
                               chatty=Kweli, connectionchatty=Kweli,
                               sni_name=hostname)

        client_context.check_hostname = Uongo
        ukijumuisha self.subTest(client=ssl.PROTOCOL_TLS_SERVER, server=ssl.PROTOCOL_TLS_CLIENT):
            ukijumuisha self.assertRaises(ssl.SSLError) kama e:
                server_params_test(client_context=server_context,
                                   server_context=client_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)
            self.assertIn('called a function you should sio call',
                          str(e.exception))

        ukijumuisha self.subTest(client=ssl.PROTOCOL_TLS_SERVER, server=ssl.PROTOCOL_TLS_SERVER):
            ukijumuisha self.assertRaises(ssl.SSLError) kama e:
                server_params_test(client_context=server_context,
                                   server_context=server_context,
                                   chatty=Kweli, connectionchatty=Kweli)
            self.assertIn('called a function you should sio call',
                          str(e.exception))

        ukijumuisha self.subTest(client=ssl.PROTOCOL_TLS_CLIENT, server=ssl.PROTOCOL_TLS_CLIENT):
            ukijumuisha self.assertRaises(ssl.SSLError) kama e:
                server_params_test(client_context=server_context,
                                   server_context=client_context,
                                   chatty=Kweli, connectionchatty=Kweli)
            self.assertIn('called a function you should sio call',
                          str(e.exception))

    eleza test_getpeercert(self):
        ikiwa support.verbose:
            sys.stdout.write("\n")

        client_context, server_context, hostname = testing_context()
        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            do_handshake_on_connect=Uongo,
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                # getpeercert() ashiria ValueError wakati the handshake isn't
                # done.
                ukijumuisha self.assertRaises(ValueError):
                    s.getpeercert()
                s.do_handshake()
                cert = s.getpeercert()
                self.assertKweli(cert, "Can't get peer certificate.")
                cipher = s.cipher()
                ikiwa support.verbose:
                    sys.stdout.write(pprint.pformat(cert) + '\n')
                    sys.stdout.write("Connection cipher ni " + str(cipher) + '.\n')
                ikiwa 'subject' haiko kwenye cert:
                    self.fail("No subject field kwenye certificate: %s." %
                              pprint.pformat(cert))
                ikiwa ((('organizationName', 'Python Software Foundation'),)
                    haiko kwenye cert['subject']):
                    self.fail(
                        "Missing ama invalid 'organizationName' field kwenye certificate subject; "
                        "should be 'Python Software Foundation'.")
                self.assertIn('notBefore', cert)
                self.assertIn('notAfter', cert)
                before = ssl.cert_time_to_seconds(cert['notBefore'])
                after = ssl.cert_time_to_seconds(cert['notAfter'])
                self.assertLess(before, after)

    @unittest.skipUnless(have_verify_flags(),
                        "verify_flags need OpenSSL > 0.9.8")
    eleza test_crl_check(self):
        ikiwa support.verbose:
            sys.stdout.write("\n")

        client_context, server_context, hostname = testing_context()

        tf = getattr(ssl, "VERIFY_X509_TRUSTED_FIRST", 0)
        self.assertEqual(client_context.verify_flags, ssl.VERIFY_DEFAULT | tf)

        # VERIFY_DEFAULT should pita
        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                cert = s.getpeercert()
                self.assertKweli(cert, "Can't get peer certificate.")

        # VERIFY_CRL_CHECK_LEAF without a loaded CRL file fails
        client_context.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF

        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                ukijumuisha self.assertRaisesRegex(ssl.SSLError,
                                            "certificate verify failed"):
                    s.connect((HOST, server.port))

        # now load a CRL file. The CRL file ni signed by the CA.
        client_context.load_verify_locations(CRLFILE)

        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                cert = s.getpeercert()
                self.assertKweli(cert, "Can't get peer certificate.")

    eleza test_check_hostname(self):
        ikiwa support.verbose:
            sys.stdout.write("\n")

        client_context, server_context, hostname = testing_context()

        # correct hostname should verify
        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                cert = s.getpeercert()
                self.assertKweli(cert, "Can't get peer certificate.")

        # incorrect hostname should ashiria an exception
        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname="invalid") kama s:
                ukijumuisha self.assertRaisesRegex(
                        ssl.CertificateError,
                        "Hostname mismatch, certificate ni sio valid kila 'invalid'."):
                    s.connect((HOST, server.port))

        # missing server_hostname arg should cause an exception, too
        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha socket.socket() kama s:
                ukijumuisha self.assertRaisesRegex(ValueError,
                                            "check_hostname requires server_hostname"):
                    client_context.wrap_socket(s)

    eleza test_ecc_cert(self):
        client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client_context.load_verify_locations(SIGNING_CA)
        client_context.set_ciphers('ECDHE:ECDSA:!NULL:!aRSA')
        hostname = SIGNED_CERTFILE_ECC_HOSTNAME

        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # load ECC cert
        server_context.load_cert_chain(SIGNED_CERTFILE_ECC)

        # correct hostname should verify
        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                cert = s.getpeercert()
                self.assertKweli(cert, "Can't get peer certificate.")
                cipher = s.cipher()[0].split('-')
                self.assertKweli(cipher[:2], ('ECDHE', 'ECDSA'))

    eleza test_dual_rsa_ecc(self):
        client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client_context.load_verify_locations(SIGNING_CA)
        # TODO: fix TLSv1.3 once SSLContext can restrict signature
        #       algorithms.
        client_context.options |= ssl.OP_NO_TLSv1_3
        # only ECDSA certs
        client_context.set_ciphers('ECDHE:ECDSA:!NULL:!aRSA')
        hostname = SIGNED_CERTFILE_ECC_HOSTNAME

        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # load ECC na RSA key/cert pairs
        server_context.load_cert_chain(SIGNED_CERTFILE_ECC)
        server_context.load_cert_chain(SIGNED_CERTFILE)

        # correct hostname should verify
        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                cert = s.getpeercert()
                self.assertKweli(cert, "Can't get peer certificate.")
                cipher = s.cipher()[0].split('-')
                self.assertKweli(cipher[:2], ('ECDHE', 'ECDSA'))

    eleza test_check_hostname_idn(self):
        ikiwa support.verbose:
            sys.stdout.write("\n")

        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(IDNSANSFILE)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = Kweli
        context.load_verify_locations(SIGNING_CA)

        # correct hostname should verify, when specified kwenye several
        # different ways
        idn_hostnames = [
            ('könig.idn.pythontest.net',
             'xn--knig-5qa.idn.pythontest.net'),
            ('xn--knig-5qa.idn.pythontest.net',
             'xn--knig-5qa.idn.pythontest.net'),
            (b'xn--knig-5qa.idn.pythontest.net',
             'xn--knig-5qa.idn.pythontest.net'),

            ('königsgäßchen.idna2003.pythontest.net',
             'xn--knigsgsschen-lcb0w.idna2003.pythontest.net'),
            ('xn--knigsgsschen-lcb0w.idna2003.pythontest.net',
             'xn--knigsgsschen-lcb0w.idna2003.pythontest.net'),
            (b'xn--knigsgsschen-lcb0w.idna2003.pythontest.net',
             'xn--knigsgsschen-lcb0w.idna2003.pythontest.net'),

            # ('königsgäßchen.idna2008.pythontest.net',
            #  'xn--knigsgchen-b4a3dun.idna2008.pythontest.net'),
            ('xn--knigsgchen-b4a3dun.idna2008.pythontest.net',
             'xn--knigsgchen-b4a3dun.idna2008.pythontest.net'),
            (b'xn--knigsgchen-b4a3dun.idna2008.pythontest.net',
             'xn--knigsgchen-b4a3dun.idna2008.pythontest.net'),

        ]
        kila server_hostname, expected_hostname kwenye idn_hostnames:
            server = ThreadedEchoServer(context=server_context, chatty=Kweli)
            ukijumuisha server:
                ukijumuisha context.wrap_socket(socket.socket(),
                                         server_hostname=server_hostname) kama s:
                    self.assertEqual(s.server_hostname, expected_hostname)
                    s.connect((HOST, server.port))
                    cert = s.getpeercert()
                    self.assertEqual(s.server_hostname, expected_hostname)
                    self.assertKweli(cert, "Can't get peer certificate.")

        # incorrect hostname should ashiria an exception
        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha context.wrap_socket(socket.socket(),
                                     server_hostname="python.example.org") kama s:
                ukijumuisha self.assertRaises(ssl.CertificateError):
                    s.connect((HOST, server.port))

    eleza test_wrong_cert_tls12(self):
        """Connecting when the server rejects the client's certificate

        Launch a server ukijumuisha CERT_REQUIRED, na check that trying to
        connect to it ukijumuisha a wrong client certificate fails.
        """
        client_context, server_context, hostname = testing_context()
        # load client cert that ni sio signed by trusted CA
        client_context.load_cert_chain(CERTFILE)
        # require TLS client authentication
        server_context.verify_mode = ssl.CERT_REQUIRED
        # TLS 1.3 has different handshake
        client_context.maximum_version = ssl.TLSVersion.TLSv1_2

        server = ThreadedEchoServer(
            context=server_context, chatty=Kweli, connectionchatty=Kweli,
        )

        ukijumuisha server, \
                client_context.wrap_socket(socket.socket(),
                                           server_hostname=hostname) kama s:
            jaribu:
                # Expect either an SSL error about the server rejecting
                # the connection, ama a low-level connection reset (which
                # sometimes happens on Windows)
                s.connect((HOST, server.port))
            tatizo ssl.SSLError kama e:
                ikiwa support.verbose:
                    sys.stdout.write("\nSSLError ni %r\n" % e)
            tatizo OSError kama e:
                ikiwa e.errno != errno.ECONNRESET:
                    raise
                ikiwa support.verbose:
                    sys.stdout.write("\nsocket.error ni %r\n" % e)
            isipokua:
                self.fail("Use of invalid cert should have failed!")

    @requires_tls_version('TLSv1_3')
    eleza test_wrong_cert_tls13(self):
        client_context, server_context, hostname = testing_context()
        # load client cert that ni sio signed by trusted CA
        client_context.load_cert_chain(CERTFILE)
        server_context.verify_mode = ssl.CERT_REQUIRED
        server_context.minimum_version = ssl.TLSVersion.TLSv1_3
        client_context.minimum_version = ssl.TLSVersion.TLSv1_3

        server = ThreadedEchoServer(
            context=server_context, chatty=Kweli, connectionchatty=Kweli,
        )
        ukijumuisha server, \
             client_context.wrap_socket(socket.socket(),
                                        server_hostname=hostname) kama s:
            # TLS 1.3 perform client cert exchange after handshake
            s.connect((HOST, server.port))
            jaribu:
                s.write(b'data')
                s.read(4)
            tatizo ssl.SSLError kama e:
                ikiwa support.verbose:
                    sys.stdout.write("\nSSLError ni %r\n" % e)
            tatizo OSError kama e:
                ikiwa e.errno != errno.ECONNRESET:
                    raise
                ikiwa support.verbose:
                    sys.stdout.write("\nsocket.error ni %r\n" % e)
            isipokua:
                self.fail("Use of invalid cert should have failed!")

    eleza test_rude_shutdown(self):
        """A brutal shutdown of an SSL server should ashiria an OSError
        kwenye the client when attempting handshake.
        """
        listener_ready = threading.Event()
        listener_gone = threading.Event()

        s = socket.socket()
        port = support.bind_port(s, HOST)

        # `listener` runs kwenye a thread.  It sits kwenye an accept() until
        # the main thread connects.  Then it rudely closes the socket,
        # na sets Event `listener_gone` to let the main thread know
        # the socket ni gone.
        eleza listener():
            s.listen()
            listener_ready.set()
            newsock, addr = s.accept()
            newsock.close()
            s.close()
            listener_gone.set()

        eleza connector():
            listener_ready.wait()
            ukijumuisha socket.socket() kama c:
                c.connect((HOST, port))
                listener_gone.wait()
                jaribu:
                    ssl_sock = test_wrap_socket(c)
                tatizo OSError:
                    pita
                isipokua:
                    self.fail('connecting to closed SSL socket should have failed')

        t = threading.Thread(target=listener)
        t.start()
        jaribu:
            connector()
        mwishowe:
            t.join()

    eleza test_ssl_cert_verify_error(self):
        ikiwa support.verbose:
            sys.stdout.write("\n")

        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(SIGNED_CERTFILE)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        server = ThreadedEchoServer(context=server_context, chatty=Kweli)
        ukijumuisha server:
            ukijumuisha context.wrap_socket(socket.socket(),
                                     server_hostname=SIGNED_CERTFILE_HOSTNAME) kama s:
                jaribu:
                    s.connect((HOST, server.port))
                tatizo ssl.SSLError kama e:
                    msg = 'unable to get local issuer certificate'
                    self.assertIsInstance(e, ssl.SSLCertVerificationError)
                    self.assertEqual(e.verify_code, 20)
                    self.assertEqual(e.verify_message, msg)
                    self.assertIn(msg, repr(e))
                    self.assertIn('certificate verify failed', repr(e))

    @requires_tls_version('SSLv2')
    eleza test_protocol_sslv2(self):
        """Connecting to an SSLv2 server ukijumuisha various client options"""
        ikiwa support.verbose:
            sys.stdout.write("\n")
        try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv2, Kweli)
        try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv2, Kweli, ssl.CERT_OPTIONAL)
        try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv2, Kweli, ssl.CERT_REQUIRED)
        try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_TLS, Uongo)
        ikiwa has_tls_version('SSLv3'):
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv3, Uongo)
        try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_TLSv1, Uongo)
        # SSLv23 client ukijumuisha specific SSL options
        ikiwa no_sslv2_implies_sslv3_hello():
            # No SSLv2 => client will use an SSLv3 hello on recent OpenSSLs
            try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_TLS, Uongo,
                               client_options=ssl.OP_NO_SSLv2)
        try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_TLS, Uongo,
                           client_options=ssl.OP_NO_SSLv3)
        try_protocol_combo(ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_TLS, Uongo,
                           client_options=ssl.OP_NO_TLSv1)

    eleza test_PROTOCOL_TLS(self):
        """Connecting to an SSLv23 server ukijumuisha various client options"""
        ikiwa support.verbose:
            sys.stdout.write("\n")
        ikiwa has_tls_version('SSLv2'):
            jaribu:
                try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_SSLv2, Kweli)
            tatizo OSError kama x:
                # this fails on some older versions of OpenSSL (0.9.7l, kila instance)
                ikiwa support.verbose:
                    sys.stdout.write(
                        " SSL2 client to SSL23 server test unexpectedly failed:\n %s\n"
                        % str(x))
        ikiwa has_tls_version('SSLv3'):
            try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_SSLv3, Uongo)
        try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLS, Kweli)
        ikiwa has_tls_version('TLSv1'):
            try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLSv1, 'TLSv1')

        ikiwa has_tls_version('SSLv3'):
            try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_SSLv3, Uongo, ssl.CERT_OPTIONAL)
        try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLS, Kweli, ssl.CERT_OPTIONAL)
        ikiwa has_tls_version('TLSv1'):
            try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLSv1, 'TLSv1', ssl.CERT_OPTIONAL)

        ikiwa has_tls_version('SSLv3'):
            try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_SSLv3, Uongo, ssl.CERT_REQUIRED)
        try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLS, Kweli, ssl.CERT_REQUIRED)
        ikiwa has_tls_version('TLSv1'):
            try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLSv1, 'TLSv1', ssl.CERT_REQUIRED)

        # Server ukijumuisha specific SSL options
        ikiwa has_tls_version('SSLv3'):
            try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_SSLv3, Uongo,
                           server_options=ssl.OP_NO_SSLv3)
        # Will choose TLSv1
        try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLS, Kweli,
                           server_options=ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3)
        ikiwa has_tls_version('TLSv1'):
            try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLSv1, Uongo,
                               server_options=ssl.OP_NO_TLSv1)

    @requires_tls_version('SSLv3')
    eleza test_protocol_sslv3(self):
        """Connecting to an SSLv3 server ukijumuisha various client options"""
        ikiwa support.verbose:
            sys.stdout.write("\n")
        try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv3, 'SSLv3')
        try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv3, 'SSLv3', ssl.CERT_OPTIONAL)
        try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv3, 'SSLv3', ssl.CERT_REQUIRED)
        ikiwa has_tls_version('SSLv2'):
            try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_SSLv2, Uongo)
        try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_TLS, Uongo,
                           client_options=ssl.OP_NO_SSLv3)
        try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_TLSv1, Uongo)
        ikiwa no_sslv2_implies_sslv3_hello():
            # No SSLv2 => client will use an SSLv3 hello on recent OpenSSLs
            try_protocol_combo(ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_TLS,
                               Uongo, client_options=ssl.OP_NO_SSLv2)

    @requires_tls_version('TLSv1')
    eleza test_protocol_tlsv1(self):
        """Connecting to a TLSv1 server ukijumuisha various client options"""
        ikiwa support.verbose:
            sys.stdout.write("\n")
        try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1, 'TLSv1')
        try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1, 'TLSv1', ssl.CERT_OPTIONAL)
        try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1, 'TLSv1', ssl.CERT_REQUIRED)
        ikiwa has_tls_version('SSLv2'):
            try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_SSLv2, Uongo)
        ikiwa has_tls_version('SSLv3'):
            try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_SSLv3, Uongo)
        try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLS, Uongo,
                           client_options=ssl.OP_NO_TLSv1)

    @requires_tls_version('TLSv1_1')
    eleza test_protocol_tlsv1_1(self):
        """Connecting to a TLSv1.1 server ukijumuisha various client options.
           Testing against older TLS versions."""
        ikiwa support.verbose:
            sys.stdout.write("\n")
        try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLSv1_1, 'TLSv1.1')
        ikiwa has_tls_version('SSLv2'):
            try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_SSLv2, Uongo)
        ikiwa has_tls_version('SSLv3'):
            try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_SSLv3, Uongo)
        try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLS, Uongo,
                           client_options=ssl.OP_NO_TLSv1_1)

        try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLSv1_1, 'TLSv1.1')
        try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLSv1_2, Uongo)
        try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_TLSv1_1, Uongo)

    @requires_tls_version('TLSv1_2')
    eleza test_protocol_tlsv1_2(self):
        """Connecting to a TLSv1.2 server ukijumuisha various client options.
           Testing against older TLS versions."""
        ikiwa support.verbose:
            sys.stdout.write("\n")
        try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_TLSv1_2, 'TLSv1.2',
                           server_options=ssl.OP_NO_SSLv3|ssl.OP_NO_SSLv2,
                           client_options=ssl.OP_NO_SSLv3|ssl.OP_NO_SSLv2,)
        ikiwa has_tls_version('SSLv2'):
            try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_SSLv2, Uongo)
        ikiwa has_tls_version('SSLv3'):
            try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_SSLv3, Uongo)
        try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_TLS, Uongo,
                           client_options=ssl.OP_NO_TLSv1_2)

        try_protocol_combo(ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLSv1_2, 'TLSv1.2')
        try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_TLSv1, Uongo)
        try_protocol_combo(ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_2, Uongo)
        try_protocol_combo(ssl.PROTOCOL_TLSv1_2, ssl.PROTOCOL_TLSv1_1, Uongo)
        try_protocol_combo(ssl.PROTOCOL_TLSv1_1, ssl.PROTOCOL_TLSv1_2, Uongo)

    eleza test_starttls(self):
        """Switching kutoka clear text to encrypted na back again."""
        msgs = (b"msg 1", b"MSG 2", b"STARTTLS", b"MSG 3", b"msg 4", b"ENDTLS", b"msg 5", b"msg 6")

        server = ThreadedEchoServer(CERTFILE,
                                    starttls_server=Kweli,
                                    chatty=Kweli,
                                    connectionchatty=Kweli)
        wrapped = Uongo
        ukijumuisha server:
            s = socket.socket()
            s.setblocking(1)
            s.connect((HOST, server.port))
            ikiwa support.verbose:
                sys.stdout.write("\n")
            kila indata kwenye msgs:
                ikiwa support.verbose:
                    sys.stdout.write(
                        " client:  sending %r...\n" % indata)
                ikiwa wrapped:
                    conn.write(indata)
                    outdata = conn.read()
                isipokua:
                    s.send(indata)
                    outdata = s.recv(1024)
                msg = outdata.strip().lower()
                ikiwa indata == b"STARTTLS" na msg.startswith(b"ok"):
                    # STARTTLS ok, switch to secure mode
                    ikiwa support.verbose:
                        sys.stdout.write(
                            " client:  read %r kutoka server, starting TLS...\n"
                            % msg)
                    conn = test_wrap_socket(s)
                    wrapped = Kweli
                lasivyo indata == b"ENDTLS" na msg.startswith(b"ok"):
                    # ENDTLS ok, switch back to clear text
                    ikiwa support.verbose:
                        sys.stdout.write(
                            " client:  read %r kutoka server, ending TLS...\n"
                            % msg)
                    s = conn.unwrap()
                    wrapped = Uongo
                isipokua:
                    ikiwa support.verbose:
                        sys.stdout.write(
                            " client:  read %r kutoka server\n" % msg)
            ikiwa support.verbose:
                sys.stdout.write(" client:  closing connection.\n")
            ikiwa wrapped:
                conn.write(b"over\n")
            isipokua:
                s.send(b"over\n")
            ikiwa wrapped:
                conn.close()
            isipokua:
                s.close()

    eleza test_socketserver(self):
        """Using socketserver to create na manage SSL connections."""
        server = make_https_server(self, certfile=SIGNED_CERTFILE)
        # try to connect
        ikiwa support.verbose:
            sys.stdout.write('\n')
        ukijumuisha open(CERTFILE, 'rb') kama f:
            d1 = f.read()
        d2 = ''
        # now fetch the same data kutoka the HTTPS server
        url = 'https://localhost:%d/%s' % (
            server.port, os.path.split(CERTFILE)[1])
        context = ssl.create_default_context(cafile=SIGNING_CA)
        f = urllib.request.urlopen(url, context=context)
        jaribu:
            dlen = f.info().get("content-length")
            ikiwa dlen na (int(dlen) > 0):
                d2 = f.read(int(dlen))
                ikiwa support.verbose:
                    sys.stdout.write(
                        " client: read %d bytes kutoka remote server '%s'\n"
                        % (len(d2), server))
        mwishowe:
            f.close()
        self.assertEqual(d1, d2)

    eleza test_asyncore_server(self):
        """Check the example asyncore integration."""
        ikiwa support.verbose:
            sys.stdout.write("\n")

        indata = b"FOO\n"
        server = AsyncoreEchoServer(CERTFILE)
        ukijumuisha server:
            s = test_wrap_socket(socket.socket())
            s.connect(('127.0.0.1', server.port))
            ikiwa support.verbose:
                sys.stdout.write(
                    " client:  sending %r...\n" % indata)
            s.write(indata)
            outdata = s.read()
            ikiwa support.verbose:
                sys.stdout.write(" client:  read %r\n" % outdata)
            ikiwa outdata != indata.lower():
                self.fail(
                    "bad data <<%r>> (%d) received; expected <<%r>> (%d)\n"
                    % (outdata[:20], len(outdata),
                       indata[:20].lower(), len(indata)))
            s.write(b"over\n")
            ikiwa support.verbose:
                sys.stdout.write(" client:  closing connection.\n")
            s.close()
            ikiwa support.verbose:
                sys.stdout.write(" client:  connection closed.\n")

    eleza test_recv_send(self):
        """Test recv(), send() na friends."""
        ikiwa support.verbose:
            sys.stdout.write("\n")

        server = ThreadedEchoServer(CERTFILE,
                                    certreqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_TLS_SERVER,
                                    cacerts=CERTFILE,
                                    chatty=Kweli,
                                    connectionchatty=Uongo)
        ukijumuisha server:
            s = test_wrap_socket(socket.socket(),
                                server_side=Uongo,
                                certfile=CERTFILE,
                                ca_certs=CERTFILE,
                                cert_reqs=ssl.CERT_NONE,
                                ssl_version=ssl.PROTOCOL_TLS_CLIENT)
            s.connect((HOST, server.port))
            # helper methods kila standardising recv* method signatures
            eleza _recv_into():
                b = bytearray(b"\0"*100)
                count = s.recv_into(b)
                rudisha b[:count]

            eleza _recvfrom_into():
                b = bytearray(b"\0"*100)
                count, addr = s.recvfrom_into(b)
                rudisha b[:count]

            # (name, method, expect success?, *args, rudisha value func)
            send_methods = [
                ('send', s.send, Kweli, [], len),
                ('sendto', s.sendto, Uongo, ["some.address"], len),
                ('sendall', s.sendall, Kweli, [], lambda x: Tupu),
            ]
            # (name, method, whether to expect success, *args)
            recv_methods = [
                ('recv', s.recv, Kweli, []),
                ('recvfrom', s.recvfrom, Uongo, ["some.address"]),
                ('recv_into', _recv_into, Kweli, []),
                ('recvfrom_into', _recvfrom_into, Uongo, []),
            ]
            data_prefix = "PREFIX_"

            kila (meth_name, send_meth, expect_success, args,
                    ret_val_meth) kwenye send_methods:
                indata = (data_prefix + meth_name).encode('ascii')
                jaribu:
                    ret = send_meth(indata, *args)
                    msg = "sending ukijumuisha {}".format(meth_name)
                    self.assertEqual(ret, ret_val_meth(indata), msg=msg)
                    outdata = s.read()
                    ikiwa outdata != indata.lower():
                        self.fail(
                            "While sending ukijumuisha <<{name:s}>> bad data "
                            "<<{outdata:r}>> ({nout:d}) received; "
                            "expected <<{indata:r}>> ({nin:d})\n".format(
                                name=meth_name, outdata=outdata[:20],
                                nout=len(outdata),
                                indata=indata[:20], nin=len(indata)
                            )
                        )
                tatizo ValueError kama e:
                    ikiwa expect_success:
                        self.fail(
                            "Failed to send ukijumuisha method <<{name:s}>>; "
                            "expected to succeed.\n".format(name=meth_name)
                        )
                    ikiwa sio str(e).startswith(meth_name):
                        self.fail(
                            "Method <<{name:s}>> failed ukijumuisha unexpected "
                            "exception message: {exp:s}\n".format(
                                name=meth_name, exp=e
                            )
                        )

            kila meth_name, recv_meth, expect_success, args kwenye recv_methods:
                indata = (data_prefix + meth_name).encode('ascii')
                jaribu:
                    s.send(indata)
                    outdata = recv_meth(*args)
                    ikiwa outdata != indata.lower():
                        self.fail(
                            "While receiving ukijumuisha <<{name:s}>> bad data "
                            "<<{outdata:r}>> ({nout:d}) received; "
                            "expected <<{indata:r}>> ({nin:d})\n".format(
                                name=meth_name, outdata=outdata[:20],
                                nout=len(outdata),
                                indata=indata[:20], nin=len(indata)
                            )
                        )
                tatizo ValueError kama e:
                    ikiwa expect_success:
                        self.fail(
                            "Failed to receive ukijumuisha method <<{name:s}>>; "
                            "expected to succeed.\n".format(name=meth_name)
                        )
                    ikiwa sio str(e).startswith(meth_name):
                        self.fail(
                            "Method <<{name:s}>> failed ukijumuisha unexpected "
                            "exception message: {exp:s}\n".format(
                                name=meth_name, exp=e
                            )
                        )
                    # consume data
                    s.read()

            # read(-1, buffer) ni supported, even though read(-1) ni not
            data = b"data"
            s.send(data)
            buffer = bytearray(len(data))
            self.assertEqual(s.read(-1, buffer), len(data))
            self.assertEqual(buffer, data)

            # sendall accepts bytes-like objects
            ikiwa ctypes ni sio Tupu:
                ubyte = ctypes.c_ubyte * len(data)
                byteslike = ubyte.from_buffer_copy(data)
                s.sendall(byteslike)
                self.assertEqual(s.read(), data)

            # Make sure sendmsg et al are disallowed to avoid
            # inadvertent disclosure of data and/or corruption
            # of the encrypted data stream
            self.assertRaises(NotImplementedError, s.dup)
            self.assertRaises(NotImplementedError, s.sendmsg, [b"data"])
            self.assertRaises(NotImplementedError, s.recvmsg, 100)
            self.assertRaises(NotImplementedError,
                              s.recvmsg_into, [bytearray(100)])
            s.write(b"over\n")

            self.assertRaises(ValueError, s.recv, -1)
            self.assertRaises(ValueError, s.read, -1)

            s.close()

    eleza test_recv_zero(self):
        server = ThreadedEchoServer(CERTFILE)
        server.__enter__()
        self.addCleanup(server.__exit__, Tupu, Tupu)
        s = socket.create_connection((HOST, server.port))
        self.addCleanup(s.close)
        s = test_wrap_socket(s, suppress_ragged_eofs=Uongo)
        self.addCleanup(s.close)

        # recv/read(0) should rudisha no data
        s.send(b"data")
        self.assertEqual(s.recv(0), b"")
        self.assertEqual(s.read(0), b"")
        self.assertEqual(s.read(), b"data")

        # Should sio block ikiwa the other end sends no data
        s.setblocking(Uongo)
        self.assertEqual(s.recv(0), b"")
        self.assertEqual(s.recv_into(bytearray()), 0)

    eleza test_nonblocking_send(self):
        server = ThreadedEchoServer(CERTFILE,
                                    certreqs=ssl.CERT_NONE,
                                    ssl_version=ssl.PROTOCOL_TLS_SERVER,
                                    cacerts=CERTFILE,
                                    chatty=Kweli,
                                    connectionchatty=Uongo)
        ukijumuisha server:
            s = test_wrap_socket(socket.socket(),
                                server_side=Uongo,
                                certfile=CERTFILE,
                                ca_certs=CERTFILE,
                                cert_reqs=ssl.CERT_NONE,
                                ssl_version=ssl.PROTOCOL_TLS_CLIENT)
            s.connect((HOST, server.port))
            s.setblocking(Uongo)

            # If we keep sending data, at some point the buffers
            # will be full na the call will block
            buf = bytearray(8192)
            eleza fill_buffer():
                wakati Kweli:
                    s.send(buf)
            self.assertRaises((ssl.SSLWantWriteError,
                               ssl.SSLWantReadError), fill_buffer)

            # Now read all the output na discard it
            s.setblocking(Kweli)
            s.close()

    eleza test_handshake_timeout(self):
        # Issue #5103: SSL handshake must respect the socket timeout
        server = socket.socket(socket.AF_INET)
        host = "127.0.0.1"
        port = support.bind_port(server)
        started = threading.Event()
        finish = Uongo

        eleza serve():
            server.listen()
            started.set()
            conns = []
            wakati sio finish:
                r, w, e = select.select([server], [], [], 0.1)
                ikiwa server kwenye r:
                    # Let the socket hang around rather than having
                    # it closed by garbage collection.
                    conns.append(server.accept()[0])
            kila sock kwenye conns:
                sock.close()

        t = threading.Thread(target=serve)
        t.start()
        started.wait()

        jaribu:
            jaribu:
                c = socket.socket(socket.AF_INET)
                c.settimeout(0.2)
                c.connect((host, port))
                # Will attempt handshake na time out
                self.assertRaisesRegex(socket.timeout, "timed out",
                                       test_wrap_socket, c)
            mwishowe:
                c.close()
            jaribu:
                c = socket.socket(socket.AF_INET)
                c = test_wrap_socket(c)
                c.settimeout(0.2)
                # Will attempt handshake na time out
                self.assertRaisesRegex(socket.timeout, "timed out",
                                       c.connect, (host, port))
            mwishowe:
                c.close()
        mwishowe:
            finish = Kweli
            t.join()
            server.close()

    eleza test_server_accept(self):
        # Issue #16357: accept() on a SSLSocket created through
        # SSLContext.wrap_socket().
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(SIGNING_CA)
        context.load_cert_chain(SIGNED_CERTFILE)
        server = socket.socket(socket.AF_INET)
        host = "127.0.0.1"
        port = support.bind_port(server)
        server = context.wrap_socket(server, server_side=Kweli)
        self.assertKweli(server.server_side)

        evt = threading.Event()
        remote = Tupu
        peer = Tupu
        eleza serve():
            nonlocal remote, peer
            server.listen()
            # Block on the accept na wait on the connection to close.
            evt.set()
            remote, peer = server.accept()
            remote.send(remote.recv(4))

        t = threading.Thread(target=serve)
        t.start()
        # Client wait until server setup na perform a connect.
        evt.wait()
        client = context.wrap_socket(socket.socket())
        client.connect((host, port))
        client.send(b'data')
        client.recv()
        client_addr = client.getsockname()
        client.close()
        t.join()
        remote.close()
        server.close()
        # Sanity checks.
        self.assertIsInstance(remote, ssl.SSLSocket)
        self.assertEqual(peer, client_addr)

    eleza test_getpeercert_enotconn(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ukijumuisha context.wrap_socket(socket.socket()) kama sock:
            ukijumuisha self.assertRaises(OSError) kama cm:
                sock.getpeercert()
            self.assertEqual(cm.exception.errno, errno.ENOTCONN)

    eleza test_do_handshake_enotconn(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ukijumuisha context.wrap_socket(socket.socket()) kama sock:
            ukijumuisha self.assertRaises(OSError) kama cm:
                sock.do_handshake()
            self.assertEqual(cm.exception.errno, errno.ENOTCONN)

    eleza test_no_shared_ciphers(self):
        client_context, server_context, hostname = testing_context()
        # OpenSSL enables all TLS 1.3 ciphers, enforce TLS 1.2 kila test
        client_context.options |= ssl.OP_NO_TLSv1_3
        # Force different suites on client na server
        client_context.set_ciphers("AES128")
        server_context.set_ciphers("AES256")
        ukijumuisha ThreadedEchoServer(context=server_context) kama server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                ukijumuisha self.assertRaises(OSError):
                    s.connect((HOST, server.port))
        self.assertIn("no shared cipher", server.conn_errors[0])

    eleza test_version_basic(self):
        """
        Basic tests kila SSLSocket.version().
        More tests are done kwenye the test_protocol_*() methods.
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = Uongo
        context.verify_mode = ssl.CERT_NONE
        ukijumuisha ThreadedEchoServer(CERTFILE,
                                ssl_version=ssl.PROTOCOL_TLS_SERVER,
                                chatty=Uongo) kama server:
            ukijumuisha context.wrap_socket(socket.socket()) kama s:
                self.assertIs(s.version(), Tupu)
                self.assertIs(s._sslobj, Tupu)
                s.connect((HOST, server.port))
                ikiwa IS_OPENSSL_1_1_1 na has_tls_version('TLSv1_3'):
                    self.assertEqual(s.version(), 'TLSv1.3')
                lasivyo ssl.OPENSSL_VERSION_INFO >= (1, 0, 2):
                    self.assertEqual(s.version(), 'TLSv1.2')
                isipokua:  # 0.9.8 to 1.0.1
                    self.assertIn(s.version(), ('TLSv1', 'TLSv1.2'))
            self.assertIs(s._sslobj, Tupu)
            self.assertIs(s.version(), Tupu)

    @requires_tls_version('TLSv1_3')
    eleza test_tls1_3(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_cert_chain(CERTFILE)
        context.options |= (
            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
        )
        ukijumuisha ThreadedEchoServer(context=context) kama server:
            ukijumuisha context.wrap_socket(socket.socket()) kama s:
                s.connect((HOST, server.port))
                self.assertIn(s.cipher()[0], {
                    'TLS_AES_256_GCM_SHA384',
                    'TLS_CHACHA20_POLY1305_SHA256',
                    'TLS_AES_128_GCM_SHA256',
                })
                self.assertEqual(s.version(), 'TLSv1.3')

    @requires_minimum_version
    @requires_tls_version('TLSv1_2')
    eleza test_min_max_version_tlsv1_2(self):
        client_context, server_context, hostname = testing_context()
        # client TLSv1.0 to 1.2
        client_context.minimum_version = ssl.TLSVersion.TLSv1
        client_context.maximum_version = ssl.TLSVersion.TLSv1_2
        # server only TLSv1.2
        server_context.minimum_version = ssl.TLSVersion.TLSv1_2
        server_context.maximum_version = ssl.TLSVersion.TLSv1_2

        ukijumuisha ThreadedEchoServer(context=server_context) kama server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                self.assertEqual(s.version(), 'TLSv1.2')

    @requires_minimum_version
    @requires_tls_version('TLSv1_1')
    eleza test_min_max_version_tlsv1_1(self):
        client_context, server_context, hostname = testing_context()
        # client 1.0 to 1.2, server 1.0 to 1.1
        client_context.minimum_version = ssl.TLSVersion.TLSv1
        client_context.maximum_version = ssl.TLSVersion.TLSv1_2
        server_context.minimum_version = ssl.TLSVersion.TLSv1
        server_context.maximum_version = ssl.TLSVersion.TLSv1_1

        ukijumuisha ThreadedEchoServer(context=server_context) kama server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                self.assertEqual(s.version(), 'TLSv1.1')

    @requires_minimum_version
    @requires_tls_version('TLSv1_2')
    eleza test_min_max_version_mismatch(self):
        client_context, server_context, hostname = testing_context()
        # client 1.0, server 1.2 (mismatch)
        server_context.maximum_version = ssl.TLSVersion.TLSv1_2
        server_context.minimum_version = ssl.TLSVersion.TLSv1_2
        client_context.maximum_version = ssl.TLSVersion.TLSv1
        client_context.minimum_version = ssl.TLSVersion.TLSv1
        ukijumuisha ThreadedEchoServer(context=server_context) kama server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                ukijumuisha self.assertRaises(ssl.SSLError) kama e:
                    s.connect((HOST, server.port))
                self.assertIn("alert", str(e.exception))

    @requires_minimum_version
    @requires_tls_version('SSLv3')
    eleza test_min_max_version_sslv3(self):
        client_context, server_context, hostname = testing_context()
        server_context.minimum_version = ssl.TLSVersion.SSLv3
        client_context.minimum_version = ssl.TLSVersion.SSLv3
        client_context.maximum_version = ssl.TLSVersion.SSLv3
        ukijumuisha ThreadedEchoServer(context=server_context) kama server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                self.assertEqual(s.version(), 'SSLv3')

    @unittest.skipUnless(ssl.HAS_ECDH, "test requires ECDH-enabled OpenSSL")
    eleza test_default_ecdh_curve(self):
        # Issue #21015: elliptic curve-based Diffie Hellman key exchange
        # should be enabled by default on SSL contexts.
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_cert_chain(CERTFILE)
        # TLSv1.3 defaults to PFS key agreement na no longer has KEA in
        # cipher name.
        context.options |= ssl.OP_NO_TLSv1_3
        # Prior to OpenSSL 1.0.0, ECDH ciphers have to be enabled
        # explicitly using the 'ECCdraft' cipher alias.  Otherwise,
        # our default cipher list should prefer ECDH-based ciphers
        # automatically.
        ikiwa ssl.OPENSSL_VERSION_INFO < (1, 0, 0):
            context.set_ciphers("ECCdraft:ECDH")
        ukijumuisha ThreadedEchoServer(context=context) kama server:
            ukijumuisha context.wrap_socket(socket.socket()) kama s:
                s.connect((HOST, server.port))
                self.assertIn("ECDH", s.cipher()[0])

    @unittest.skipUnless("tls-unique" kwenye ssl.CHANNEL_BINDING_TYPES,
                         "'tls-unique' channel binding sio available")
    eleza test_tls_unique_channel_binding(self):
        """Test tls-unique channel binding."""
        ikiwa support.verbose:
            sys.stdout.write("\n")

        client_context, server_context, hostname = testing_context()

        server = ThreadedEchoServer(context=server_context,
                                    chatty=Kweli,
                                    connectionchatty=Uongo)

        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(
                    socket.socket(),
                    server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                # get the data
                cb_data = s.get_channel_binding("tls-unique")
                ikiwa support.verbose:
                    sys.stdout.write(
                        " got channel binding data: {0!r}\n".format(cb_data))

                # check ikiwa it ni sane
                self.assertIsNotTupu(cb_data)
                ikiwa s.version() == 'TLSv1.3':
                    self.assertEqual(len(cb_data), 48)
                isipokua:
                    self.assertEqual(len(cb_data), 12)  # Kweli kila TLSv1

                # na compare ukijumuisha the peers version
                s.write(b"CB tls-unique\n")
                peer_data_repr = s.read().strip()
                self.assertEqual(peer_data_repr,
                                 repr(cb_data).encode("us-ascii"))

            # now, again
            ukijumuisha client_context.wrap_socket(
                    socket.socket(),
                    server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                new_cb_data = s.get_channel_binding("tls-unique")
                ikiwa support.verbose:
                    sys.stdout.write(
                        "got another channel binding data: {0!r}\n".format(
                            new_cb_data)
                    )
                # ni it really unique
                self.assertNotEqual(cb_data, new_cb_data)
                self.assertIsNotTupu(cb_data)
                ikiwa s.version() == 'TLSv1.3':
                    self.assertEqual(len(cb_data), 48)
                isipokua:
                    self.assertEqual(len(cb_data), 12)  # Kweli kila TLSv1
                s.write(b"CB tls-unique\n")
                peer_data_repr = s.read().strip()
                self.assertEqual(peer_data_repr,
                                 repr(new_cb_data).encode("us-ascii"))

    eleza test_compression(self):
        client_context, server_context, hostname = testing_context()
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)
        ikiwa support.verbose:
            sys.stdout.write(" got compression: {!r}\n".format(stats['compression']))
        self.assertIn(stats['compression'], { Tupu, 'ZLIB', 'RLE' })

    @unittest.skipUnless(hasattr(ssl, 'OP_NO_COMPRESSION'),
                         "ssl.OP_NO_COMPRESSION needed kila this test")
    eleza test_compression_disabled(self):
        client_context, server_context, hostname = testing_context()
        client_context.options |= ssl.OP_NO_COMPRESSION
        server_context.options |= ssl.OP_NO_COMPRESSION
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)
        self.assertIs(stats['compression'], Tupu)

    eleza test_dh_params(self):
        # Check we can get a connection ukijumuisha ephemeral Diffie-Hellman
        client_context, server_context, hostname = testing_context()
        # test scenario needs TLS <= 1.2
        client_context.options |= ssl.OP_NO_TLSv1_3
        server_context.load_dh_params(DHFILE)
        server_context.set_ciphers("kEDH")
        server_context.options |= ssl.OP_NO_TLSv1_3
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)
        cipher = stats["cipher"][0]
        parts = cipher.split("-")
        ikiwa "ADH" haiko kwenye parts na "EDH" haiko kwenye parts na "DHE" haiko kwenye parts:
            self.fail("Non-DH cipher: " + cipher[0])

    @unittest.skipUnless(HAVE_SECP_CURVES, "needs secp384r1 curve support")
    @unittest.skipIf(IS_OPENSSL_1_1_1, "TODO: Test doesn't work on 1.1.1")
    eleza test_ecdh_curve(self):
        # server secp384r1, client auto
        client_context, server_context, hostname = testing_context()

        server_context.set_ecdh_curve("secp384r1")
        server_context.set_ciphers("ECDHE:!eNULL:!aNULL")
        server_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)

        # server auto, client secp384r1
        client_context, server_context, hostname = testing_context()
        client_context.set_ecdh_curve("secp384r1")
        server_context.set_ciphers("ECDHE:!eNULL:!aNULL")
        server_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)

        # server / client curve mismatch
        client_context, server_context, hostname = testing_context()
        client_context.set_ecdh_curve("prime256v1")
        server_context.set_ecdh_curve("secp384r1")
        server_context.set_ciphers("ECDHE:!eNULL:!aNULL")
        server_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        jaribu:
            stats = server_params_test(client_context, server_context,
                                       chatty=Kweli, connectionchatty=Kweli,
                                       sni_name=hostname)
        tatizo ssl.SSLError:
            pita
        isipokua:
            # OpenSSL 1.0.2 does sio fail although it should.
            ikiwa IS_OPENSSL_1_1_0:
                self.fail("mismatch curve did sio fail")

    eleza test_selected_alpn_protocol(self):
        # selected_alpn_protocol() ni Tupu unless ALPN ni used.
        client_context, server_context, hostname = testing_context()
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)
        self.assertIs(stats['client_alpn_protocol'], Tupu)

    @unittest.skipUnless(ssl.HAS_ALPN, "ALPN support required")
    eleza test_selected_alpn_protocol_if_server_uses_alpn(self):
        # selected_alpn_protocol() ni Tupu unless ALPN ni used by the client.
        client_context, server_context, hostname = testing_context()
        server_context.set_alpn_protocols(['foo', 'bar'])
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)
        self.assertIs(stats['client_alpn_protocol'], Tupu)

    @unittest.skipUnless(ssl.HAS_ALPN, "ALPN support needed kila this test")
    eleza test_alpn_protocols(self):
        server_protocols = ['foo', 'bar', 'milkshake']
        protocol_tests = [
            (['foo', 'bar'], 'foo'),
            (['bar', 'foo'], 'foo'),
            (['milkshake'], 'milkshake'),
            (['http/3.0', 'http/4.0'], Tupu)
        ]
        kila client_protocols, expected kwenye protocol_tests:
            client_context, server_context, hostname = testing_context()
            server_context.set_alpn_protocols(server_protocols)
            client_context.set_alpn_protocols(client_protocols)

            jaribu:
                stats = server_params_test(client_context,
                                           server_context,
                                           chatty=Kweli,
                                           connectionchatty=Kweli,
                                           sni_name=hostname)
            tatizo ssl.SSLError kama e:
                stats = e

            ikiwa (expected ni Tupu na IS_OPENSSL_1_1_0
                    na ssl.OPENSSL_VERSION_INFO < (1, 1, 0, 6)):
                # OpenSSL 1.1.0 to 1.1.0e raises handshake error
                self.assertIsInstance(stats, ssl.SSLError)
            isipokua:
                msg = "failed trying %s (s) na %s (c).\n" \
                    "was expecting %s, but got %%s kutoka the %%s" \
                        % (str(server_protocols), str(client_protocols),
                            str(expected))
                client_result = stats['client_alpn_protocol']
                self.assertEqual(client_result, expected,
                                 msg % (client_result, "client"))
                server_result = stats['server_alpn_protocols'][-1] \
                    ikiwa len(stats['server_alpn_protocols']) isipokua 'nothing'
                self.assertEqual(server_result, expected,
                                 msg % (server_result, "server"))

    eleza test_selected_npn_protocol(self):
        # selected_npn_protocol() ni Tupu unless NPN ni used
        client_context, server_context, hostname = testing_context()
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli, connectionchatty=Kweli,
                                   sni_name=hostname)
        self.assertIs(stats['client_npn_protocol'], Tupu)

    @unittest.skipUnless(ssl.HAS_NPN, "NPN support needed kila this test")
    eleza test_npn_protocols(self):
        server_protocols = ['http/1.1', 'spdy/2']
        protocol_tests = [
            (['http/1.1', 'spdy/2'], 'http/1.1'),
            (['spdy/2', 'http/1.1'], 'http/1.1'),
            (['spdy/2', 'test'], 'spdy/2'),
            (['abc', 'def'], 'abc')
        ]
        kila client_protocols, expected kwenye protocol_tests:
            client_context, server_context, hostname = testing_context()
            server_context.set_npn_protocols(server_protocols)
            client_context.set_npn_protocols(client_protocols)
            stats = server_params_test(client_context, server_context,
                                       chatty=Kweli, connectionchatty=Kweli,
                                       sni_name=hostname)
            msg = "failed trying %s (s) na %s (c).\n" \
                  "was expecting %s, but got %%s kutoka the %%s" \
                      % (str(server_protocols), str(client_protocols),
                         str(expected))
            client_result = stats['client_npn_protocol']
            self.assertEqual(client_result, expected, msg % (client_result, "client"))
            server_result = stats['server_npn_protocols'][-1] \
                ikiwa len(stats['server_npn_protocols']) isipokua 'nothing'
            self.assertEqual(server_result, expected, msg % (server_result, "server"))

    eleza sni_contexts(self):
        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(SIGNED_CERTFILE)
        other_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        other_context.load_cert_chain(SIGNED_CERTFILE2)
        client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client_context.load_verify_locations(SIGNING_CA)
        rudisha server_context, other_context, client_context

    eleza check_common_name(self, stats, name):
        cert = stats['peercert']
        self.assertIn((('commonName', name),), cert['subject'])

    @needs_sni
    eleza test_sni_callback(self):
        calls = []
        server_context, other_context, client_context = self.sni_contexts()

        client_context.check_hostname = Uongo

        eleza servername_cb(ssl_sock, server_name, initial_context):
            calls.append((server_name, initial_context))
            ikiwa server_name ni sio Tupu:
                ssl_sock.context = other_context
        server_context.set_servername_callback(servername_cb)

        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli,
                                   sni_name='supermessage')
        # The hostname was fetched properly, na the certificate was
        # changed kila the connection.
        self.assertEqual(calls, [("supermessage", server_context)])
        # CERTFILE4 was selected
        self.check_common_name(stats, 'fakehostname')

        calls = []
        # The callback ni called ukijumuisha server_name=Tupu
        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli,
                                   sni_name=Tupu)
        self.assertEqual(calls, [(Tupu, server_context)])
        self.check_common_name(stats, SIGNED_CERTFILE_HOSTNAME)

        # Check disabling the callback
        calls = []
        server_context.set_servername_callback(Tupu)

        stats = server_params_test(client_context, server_context,
                                   chatty=Kweli,
                                   sni_name='notfunny')
        # Certificate didn't change
        self.check_common_name(stats, SIGNED_CERTFILE_HOSTNAME)
        self.assertEqual(calls, [])

    @needs_sni
    eleza test_sni_callback_alert(self):
        # Returning a TLS alert ni reflected to the connecting client
        server_context, other_context, client_context = self.sni_contexts()

        eleza cb_returning_alert(ssl_sock, server_name, initial_context):
            rudisha ssl.ALERT_DESCRIPTION_ACCESS_DENIED
        server_context.set_servername_callback(cb_returning_alert)
        ukijumuisha self.assertRaises(ssl.SSLError) kama cm:
            stats = server_params_test(client_context, server_context,
                                       chatty=Uongo,
                                       sni_name='supermessage')
        self.assertEqual(cm.exception.reason, 'TLSV1_ALERT_ACCESS_DENIED')

    @needs_sni
    eleza test_sni_callback_raising(self):
        # Raising fails the connection ukijumuisha a TLS handshake failure alert.
        server_context, other_context, client_context = self.sni_contexts()

        eleza cb_raising(ssl_sock, server_name, initial_context):
            1/0
        server_context.set_servername_callback(cb_raising)

        ukijumuisha support.catch_unraisable_exception() kama catch:
            ukijumuisha self.assertRaises(ssl.SSLError) kama cm:
                stats = server_params_test(client_context, server_context,
                                           chatty=Uongo,
                                           sni_name='supermessage')

            self.assertEqual(cm.exception.reason,
                             'SSLV3_ALERT_HANDSHAKE_FAILURE')
            self.assertEqual(catch.unraisable.exc_type, ZeroDivisionError)

    @needs_sni
    eleza test_sni_callback_wrong_return_type(self):
        # Returning the wrong rudisha type terminates the TLS connection
        # ukijumuisha an internal error alert.
        server_context, other_context, client_context = self.sni_contexts()

        eleza cb_wrong_return_type(ssl_sock, server_name, initial_context):
            rudisha "foo"
        server_context.set_servername_callback(cb_wrong_return_type)

        ukijumuisha support.catch_unraisable_exception() kama catch:
            ukijumuisha self.assertRaises(ssl.SSLError) kama cm:
                stats = server_params_test(client_context, server_context,
                                           chatty=Uongo,
                                           sni_name='supermessage')


            self.assertEqual(cm.exception.reason, 'TLSV1_ALERT_INTERNAL_ERROR')
            self.assertEqual(catch.unraisable.exc_type, TypeError)

    eleza test_shared_ciphers(self):
        client_context, server_context, hostname = testing_context()
        client_context.set_ciphers("AES128:AES256")
        server_context.set_ciphers("AES256")
        expected_algs = [
            "AES256", "AES-256",
            # TLS 1.3 ciphers are always enabled
            "TLS_CHACHA20", "TLS_AES",
        ]

        stats = server_params_test(client_context, server_context,
                                   sni_name=hostname)
        ciphers = stats['server_shared_ciphers'][0]
        self.assertGreater(len(ciphers), 0)
        kila name, tls_version, bits kwenye ciphers:
            ikiwa sio any(alg kwenye name kila alg kwenye expected_algs):
                self.fail(name)

    eleza test_read_write_after_close_raises_valuerror(self):
        client_context, server_context, hostname = testing_context()
        server = ThreadedEchoServer(context=server_context, chatty=Uongo)

        ukijumuisha server:
            s = client_context.wrap_socket(socket.socket(),
                                           server_hostname=hostname)
            s.connect((HOST, server.port))
            s.close()

            self.assertRaises(ValueError, s.read, 1024)
            self.assertRaises(ValueError, s.write, b'hello')

    eleza test_sendfile(self):
        TEST_DATA = b"x" * 512
        ukijumuisha open(support.TESTFN, 'wb') kama f:
            f.write(TEST_DATA)
        self.addCleanup(support.unlink, support.TESTFN)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(SIGNING_CA)
        context.load_cert_chain(SIGNED_CERTFILE)
        server = ThreadedEchoServer(context=context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha context.wrap_socket(socket.socket()) kama s:
                s.connect((HOST, server.port))
                ukijumuisha open(support.TESTFN, 'rb') kama file:
                    s.sendfile(file)
                    self.assertEqual(s.recv(1024), TEST_DATA)

    eleza test_session(self):
        client_context, server_context, hostname = testing_context()
        # TODO: sessions aren't compatible ukijumuisha TLSv1.3 yet
        client_context.options |= ssl.OP_NO_TLSv1_3

        # first connection without session
        stats = server_params_test(client_context, server_context,
                                   sni_name=hostname)
        session = stats['session']
        self.assertKweli(session.id)
        self.assertGreater(session.time, 0)
        self.assertGreater(session.timeout, 0)
        self.assertKweli(session.has_ticket)
        ikiwa ssl.OPENSSL_VERSION_INFO > (1, 0, 1):
            self.assertGreater(session.ticket_lifetime_hint, 0)
        self.assertUongo(stats['session_reused'])
        sess_stat = server_context.session_stats()
        self.assertEqual(sess_stat['accept'], 1)
        self.assertEqual(sess_stat['hits'], 0)

        # reuse session
        stats = server_params_test(client_context, server_context,
                                   session=session, sni_name=hostname)
        sess_stat = server_context.session_stats()
        self.assertEqual(sess_stat['accept'], 2)
        self.assertEqual(sess_stat['hits'], 1)
        self.assertKweli(stats['session_reused'])
        session2 = stats['session']
        self.assertEqual(session2.id, session.id)
        self.assertEqual(session2, session)
        self.assertIsNot(session2, session)
        self.assertGreaterEqual(session2.time, session.time)
        self.assertGreaterEqual(session2.timeout, session.timeout)

        # another one without session
        stats = server_params_test(client_context, server_context,
                                   sni_name=hostname)
        self.assertUongo(stats['session_reused'])
        session3 = stats['session']
        self.assertNotEqual(session3.id, session.id)
        self.assertNotEqual(session3, session)
        sess_stat = server_context.session_stats()
        self.assertEqual(sess_stat['accept'], 3)
        self.assertEqual(sess_stat['hits'], 1)

        # reuse session again
        stats = server_params_test(client_context, server_context,
                                   session=session, sni_name=hostname)
        self.assertKweli(stats['session_reused'])
        session4 = stats['session']
        self.assertEqual(session4.id, session.id)
        self.assertEqual(session4, session)
        self.assertGreaterEqual(session4.time, session.time)
        self.assertGreaterEqual(session4.timeout, session.timeout)
        sess_stat = server_context.session_stats()
        self.assertEqual(sess_stat['accept'], 4)
        self.assertEqual(sess_stat['hits'], 2)

    eleza test_session_handling(self):
        client_context, server_context, hostname = testing_context()
        client_context2, _, _ = testing_context()

        # TODO: session reuse does sio work ukijumuisha TLSv1.3
        client_context.options |= ssl.OP_NO_TLSv1_3
        client_context2.options |= ssl.OP_NO_TLSv1_3

        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                # session ni Tupu before handshake
                self.assertEqual(s.session, Tupu)
                self.assertEqual(s.session_reused, Tupu)
                s.connect((HOST, server.port))
                session = s.session
                self.assertKweli(session)
                ukijumuisha self.assertRaises(TypeError) kama e:
                    s.session = object
                self.assertEqual(str(e.exception), 'Value ni sio a SSLSession.')

            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                # cannot set session after handshake
                ukijumuisha self.assertRaises(ValueError) kama e:
                    s.session = session
                self.assertEqual(str(e.exception),
                                 'Cannot set session after handshake.')

            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                # can set session before handshake na before the
                # connection was established
                s.session = session
                s.connect((HOST, server.port))
                self.assertEqual(s.session.id, session.id)
                self.assertEqual(s.session, session)
                self.assertEqual(s.session_reused, Kweli)

            ukijumuisha client_context2.wrap_socket(socket.socket(),
                                             server_hostname=hostname) kama s:
                # cannot re-use session ukijumuisha a different SSLContext
                ukijumuisha self.assertRaises(ValueError) kama e:
                    s.session = session
                    s.connect((HOST, server.port))
                self.assertEqual(str(e.exception),
                                 'Session refers to a different SSLContext.')


@unittest.skipUnless(has_tls_version('TLSv1_3'), "Test needs TLS 1.3")
kundi TestPostHandshakeAuth(unittest.TestCase):
    eleza test_pha_setter(self):
        protocols = [
            ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLS_SERVER, ssl.PROTOCOL_TLS_CLIENT
        ]
        kila protocol kwenye protocols:
            ctx = ssl.SSLContext(protocol)
            self.assertEqual(ctx.post_handshake_auth, Uongo)

            ctx.post_handshake_auth = Kweli
            self.assertEqual(ctx.post_handshake_auth, Kweli)

            ctx.verify_mode = ssl.CERT_REQUIRED
            self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
            self.assertEqual(ctx.post_handshake_auth, Kweli)

            ctx.post_handshake_auth = Uongo
            self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
            self.assertEqual(ctx.post_handshake_auth, Uongo)

            ctx.verify_mode = ssl.CERT_OPTIONAL
            ctx.post_handshake_auth = Kweli
            self.assertEqual(ctx.verify_mode, ssl.CERT_OPTIONAL)
            self.assertEqual(ctx.post_handshake_auth, Kweli)

    eleza test_pha_required(self):
        client_context, server_context, hostname = testing_context()
        server_context.post_handshake_auth = Kweli
        server_context.verify_mode = ssl.CERT_REQUIRED
        client_context.post_handshake_auth = Kweli
        client_context.load_cert_chain(SIGNED_CERTFILE)

        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'FALSE\n')
                s.write(b'PHA')
                self.assertEqual(s.recv(1024), b'OK\n')
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'TRUE\n')
                # PHA method just returns true when cert ni already available
                s.write(b'PHA')
                self.assertEqual(s.recv(1024), b'OK\n')
                s.write(b'GETCERT')
                cert_text = s.recv(4096).decode('us-ascii')
                self.assertIn('Python Software Foundation CA', cert_text)

    eleza test_pha_required_nocert(self):
        client_context, server_context, hostname = testing_context()
        server_context.post_handshake_auth = Kweli
        server_context.verify_mode = ssl.CERT_REQUIRED
        client_context.post_handshake_auth = Kweli

        # Ignore expected SSLError kwenye ConnectionHandler of ThreadedEchoServer
        # (it ni only raised sometimes on Windows)
        ukijumuisha support.catch_threading_exception() kama cm:
            server = ThreadedEchoServer(context=server_context, chatty=Uongo)
            ukijumuisha server:
                ukijumuisha client_context.wrap_socket(socket.socket(),
                                                server_hostname=hostname) kama s:
                    s.connect((HOST, server.port))
                    s.write(b'PHA')
                    # receive CertificateRequest
                    self.assertEqual(s.recv(1024), b'OK\n')
                    # send empty Certificate + Finish
                    s.write(b'HASCERT')
                    # receive alert
                    ukijumuisha self.assertRaisesRegex(
                            ssl.SSLError,
                            'tlsv13 alert certificate required'):
                        s.recv(1024)

    eleza test_pha_optional(self):
        ikiwa support.verbose:
            sys.stdout.write("\n")

        client_context, server_context, hostname = testing_context()
        server_context.post_handshake_auth = Kweli
        server_context.verify_mode = ssl.CERT_REQUIRED
        client_context.post_handshake_auth = Kweli
        client_context.load_cert_chain(SIGNED_CERTFILE)

        # check CERT_OPTIONAL
        server_context.verify_mode = ssl.CERT_OPTIONAL
        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'FALSE\n')
                s.write(b'PHA')
                self.assertEqual(s.recv(1024), b'OK\n')
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'TRUE\n')

    eleza test_pha_optional_nocert(self):
        ikiwa support.verbose:
            sys.stdout.write("\n")

        client_context, server_context, hostname = testing_context()
        server_context.post_handshake_auth = Kweli
        server_context.verify_mode = ssl.CERT_OPTIONAL
        client_context.post_handshake_auth = Kweli

        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'FALSE\n')
                s.write(b'PHA')
                self.assertEqual(s.recv(1024), b'OK\n')
                # optional doesn't fail when client does sio have a cert
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'FALSE\n')

    eleza test_pha_no_pha_client(self):
        client_context, server_context, hostname = testing_context()
        server_context.post_handshake_auth = Kweli
        server_context.verify_mode = ssl.CERT_REQUIRED
        client_context.load_cert_chain(SIGNED_CERTFILE)

        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                ukijumuisha self.assertRaisesRegex(ssl.SSLError, 'not server'):
                    s.verify_client_post_handshake()
                s.write(b'PHA')
                self.assertIn(b'extension sio received', s.recv(1024))

    eleza test_pha_no_pha_server(self):
        # server doesn't have PHA enabled, cert ni requested kwenye handshake
        client_context, server_context, hostname = testing_context()
        server_context.verify_mode = ssl.CERT_REQUIRED
        client_context.post_handshake_auth = Kweli
        client_context.load_cert_chain(SIGNED_CERTFILE)

        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'TRUE\n')
                # PHA doesn't fail ikiwa there ni already a cert
                s.write(b'PHA')
                self.assertEqual(s.recv(1024), b'OK\n')
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'TRUE\n')

    eleza test_pha_not_tls13(self):
        # TLS 1.2
        client_context, server_context, hostname = testing_context()
        server_context.verify_mode = ssl.CERT_REQUIRED
        client_context.maximum_version = ssl.TLSVersion.TLSv1_2
        client_context.post_handshake_auth = Kweli
        client_context.load_cert_chain(SIGNED_CERTFILE)

        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                # PHA fails kila TLS != 1.3
                s.write(b'PHA')
                self.assertIn(b'WRONG_SSL_VERSION', s.recv(1024))

    eleza test_bpo37428_pha_cert_none(self):
        # verify that post_handshake_auth does sio implicitly enable cert
        # validation.
        hostname = SIGNED_CERTFILE_HOSTNAME
        client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client_context.post_handshake_auth = Kweli
        client_context.load_cert_chain(SIGNED_CERTFILE)
        # no cert validation na CA on client side
        client_context.check_hostname = Uongo
        client_context.verify_mode = ssl.CERT_NONE

        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(SIGNED_CERTFILE)
        server_context.load_verify_locations(SIGNING_CA)
        server_context.post_handshake_auth = Kweli
        server_context.verify_mode = ssl.CERT_REQUIRED

        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'FALSE\n')
                s.write(b'PHA')
                self.assertEqual(s.recv(1024), b'OK\n')
                s.write(b'HASCERT')
                self.assertEqual(s.recv(1024), b'TRUE\n')
                # server cert has sio been validated
                self.assertEqual(s.getpeercert(), {})


HAS_KEYLOG = hasattr(ssl.SSLContext, 'keylog_filename')
requires_keylog = unittest.skipUnless(
    HAS_KEYLOG, 'test requires OpenSSL 1.1.1 ukijumuisha keylog callback')

kundi TestSSLDebug(unittest.TestCase):

    eleza keylog_lines(self, fname=support.TESTFN):
        ukijumuisha open(fname) kama f:
            rudisha len(list(f))

    @requires_keylog
    eleza test_keylog_defaults(self):
        self.addCleanup(support.unlink, support.TESTFN)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.assertEqual(ctx.keylog_filename, Tupu)

        self.assertUongo(os.path.isfile(support.TESTFN))
        ctx.keylog_filename = support.TESTFN
        self.assertEqual(ctx.keylog_filename, support.TESTFN)
        self.assertKweli(os.path.isfile(support.TESTFN))
        self.assertEqual(self.keylog_lines(), 1)

        ctx.keylog_filename = Tupu
        self.assertEqual(ctx.keylog_filename, Tupu)

        ukijumuisha self.assertRaises((IsADirectoryError, PermissionError)):
            # Windows raises PermissionError
            ctx.keylog_filename = os.path.dirname(
                os.path.abspath(support.TESTFN))

        ukijumuisha self.assertRaises(TypeError):
            ctx.keylog_filename = 1

    @requires_keylog
    eleza test_keylog_filename(self):
        self.addCleanup(support.unlink, support.TESTFN)
        client_context, server_context, hostname = testing_context()

        client_context.keylog_filename = support.TESTFN
        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
        # header, 5 lines kila TLS 1.3
        self.assertEqual(self.keylog_lines(), 6)

        client_context.keylog_filename = Tupu
        server_context.keylog_filename = support.TESTFN
        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
        self.assertGreaterEqual(self.keylog_lines(), 11)

        client_context.keylog_filename = support.TESTFN
        server_context.keylog_filename = support.TESTFN
        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))
        self.assertGreaterEqual(self.keylog_lines(), 21)

        client_context.keylog_filename = Tupu
        server_context.keylog_filename = Tupu

    @requires_keylog
    @unittest.skipIf(sys.flags.ignore_environment,
                     "test ni sio compatible ukijumuisha ignore_environment")
    eleza test_keylog_env(self):
        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha unittest.mock.patch.dict(os.environ):
            os.environ['SSLKEYLOGFILE'] = support.TESTFN
            self.assertEqual(os.environ['SSLKEYLOGFILE'], support.TESTFN)

            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.assertEqual(ctx.keylog_filename, Tupu)

            ctx = ssl.create_default_context()
            self.assertEqual(ctx.keylog_filename, support.TESTFN)

            ctx = ssl._create_stdlib_context()
            self.assertEqual(ctx.keylog_filename, support.TESTFN)

    eleza test_msg_callback(self):
        client_context, server_context, hostname = testing_context()

        eleza msg_cb(conn, direction, version, content_type, msg_type, data):
            pita

        self.assertIs(client_context._msg_callback, Tupu)
        client_context._msg_callback = msg_cb
        self.assertIs(client_context._msg_callback, msg_cb)
        ukijumuisha self.assertRaises(TypeError):
            client_context._msg_callback = object()

    eleza test_msg_callback_tls12(self):
        client_context, server_context, hostname = testing_context()
        client_context.options |= ssl.OP_NO_TLSv1_3

        msg = []

        eleza msg_cb(conn, direction, version, content_type, msg_type, data):
            self.assertIsInstance(conn, ssl.SSLSocket)
            self.assertIsInstance(data, bytes)
            self.assertIn(direction, {'read', 'write'})
            msg.append((direction, version, content_type, msg_type))

        client_context._msg_callback = msg_cb

        server = ThreadedEchoServer(context=server_context, chatty=Uongo)
        ukijumuisha server:
            ukijumuisha client_context.wrap_socket(socket.socket(),
                                            server_hostname=hostname) kama s:
                s.connect((HOST, server.port))

        self.assertIn(
            ("read", TLSVersion.TLSv1_2, _TLSContentType.HANDSHAKE,
             _TLSMessageType.SERVER_KEY_EXCHANGE),
            msg
        )
        self.assertIn(
            ("write", TLSVersion.TLSv1_2, _TLSContentType.CHANGE_CIPHER_SPEC,
             _TLSMessageType.CHANGE_CIPHER_SPEC),
            msg
        )


eleza test_main(verbose=Uongo):
    ikiwa support.verbose:
        plats = {
            'Mac': platform.mac_ver,
            'Windows': platform.win32_ver,
        }
        kila name, func kwenye plats.items():
            plat = func()
            ikiwa plat na plat[0]:
                plat = '%s %r' % (name, plat)
                koma
        isipokua:
            plat = repr(platform.platform())
        andika("test_ssl: testing ukijumuisha %r %r" %
            (ssl.OPENSSL_VERSION, ssl.OPENSSL_VERSION_INFO))
        andika("          under %s" % plat)
        andika("          HAS_SNI = %r" % ssl.HAS_SNI)
        andika("          OP_ALL = 0x%8x" % ssl.OP_ALL)
        jaribu:
            andika("          OP_NO_TLSv1_1 = 0x%8x" % ssl.OP_NO_TLSv1_1)
        tatizo AttributeError:
            pita

    kila filename kwenye [
        CERTFILE, BYTES_CERTFILE,
        ONLYCERT, ONLYKEY, BYTES_ONLYCERT, BYTES_ONLYKEY,
        SIGNED_CERTFILE, SIGNED_CERTFILE2, SIGNING_CA,
        BADCERT, BADKEY, EMPTYCERT]:
        ikiwa sio os.path.exists(filename):
            ashiria support.TestFailed("Can't read certificate file %r" % filename)

    tests = [
        ContextTests, BasicSocketTests, SSLErrorTests, MemoryBIOTests,
        SSLObjectTests, SimpleBackgroundTests, ThreadedTests,
        TestPostHandshakeAuth, TestSSLDebug
    ]

    ikiwa support.is_resource_enabled('network'):
        tests.append(NetworkedTests)

    thread_info = support.threading_setup()
    jaribu:
        support.run_unittest(*tests)
    mwishowe:
        support.threading_cleanup(*thread_info)

ikiwa __name__ == "__main__":
    test_main()
