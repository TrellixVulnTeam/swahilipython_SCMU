agiza unittest
kutoka test agiza support

agiza errno
agiza io
agiza itertools
agiza socket
agiza select
agiza tempfile
agiza time
agiza traceback
agiza queue
agiza sys
agiza os
agiza platform
agiza array
agiza contextlib
kutoka weakref agiza proxy
agiza signal
agiza math
agiza pickle
agiza struct
agiza random
agiza shutil
agiza string
agiza _thread kama thread
agiza threading
jaribu:
    agiza multiprocessing
tatizo ImportError:
    multiprocessing = Uongo
jaribu:
    agiza fcntl
tatizo ImportError:
    fcntl = Tupu

HOST = support.HOST
# test unicode string na carriage rudisha
MSG = 'Michael Gilfix was here\u1234\r\n'.encode('utf-8')
MAIN_TIMEOUT = 60.0

VSOCKPORT = 1234
AIX = platform.system() == "AIX"

jaribu:
    agiza _socket
tatizo ImportError:
    _socket = Tupu

eleza get_cid():
    ikiwa fcntl ni Tupu:
        rudisha Tupu
    jaribu:
        ukijumuisha open("/dev/vsock", "rb") kama f:
            r = fcntl.ioctl(f, socket.IOCTL_VM_SOCKETS_GET_LOCAL_CID, "    ")
    tatizo OSError:
        rudisha Tupu
    isipokua:
        rudisha struct.unpack("I", r)[0]

eleza _have_socket_can():
    """Check whether CAN sockets are supported on this host."""
    jaribu:
        s = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    tatizo (AttributeError, OSError):
        rudisha Uongo
    isipokua:
        s.close()
    rudisha Kweli

eleza _have_socket_can_isotp():
    """Check whether CAN ISOTP sockets are supported on this host."""
    jaribu:
        s = socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_ISOTP)
    tatizo (AttributeError, OSError):
        rudisha Uongo
    isipokua:
        s.close()
    rudisha Kweli

eleza _have_socket_rds():
    """Check whether RDS sockets are supported on this host."""
    jaribu:
        s = socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0)
    tatizo (AttributeError, OSError):
        rudisha Uongo
    isipokua:
        s.close()
    rudisha Kweli

eleza _have_socket_alg():
    """Check whether AF_ALG sockets are supported on this host."""
    jaribu:
        s = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
    tatizo (AttributeError, OSError):
        rudisha Uongo
    isipokua:
        s.close()
    rudisha Kweli

eleza _have_socket_qipcrtr():
    """Check whether AF_QIPCRTR sockets are supported on this host."""
    jaribu:
        s = socket.socket(socket.AF_QIPCRTR, socket.SOCK_DGRAM, 0)
    tatizo (AttributeError, OSError):
        rudisha Uongo
    isipokua:
        s.close()
    rudisha Kweli

eleza _have_socket_vsock():
    """Check whether AF_VSOCK sockets are supported on this host."""
    ret = get_cid() ni sio Tupu
    rudisha ret


@contextlib.contextmanager
eleza socket_setdefaulttimeout(timeout):
    old_timeout = socket.getdefaulttimeout()
    jaribu:
        socket.setdefaulttimeout(timeout)
        tuma
    mwishowe:
        socket.setdefaulttimeout(old_timeout)


HAVE_SOCKET_CAN = _have_socket_can()

HAVE_SOCKET_CAN_ISOTP = _have_socket_can_isotp()

HAVE_SOCKET_RDS = _have_socket_rds()

HAVE_SOCKET_ALG = _have_socket_alg()

HAVE_SOCKET_QIPCRTR = _have_socket_qipcrtr()

HAVE_SOCKET_VSOCK = _have_socket_vsock()

# Size kwenye bytes of the int type
SIZEOF_INT = array.array("i").itemsize

kundi SocketTCPTest(unittest.TestCase):

    eleza setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = support.bind_port(self.serv)
        self.serv.listen()

    eleza tearDown(self):
        self.serv.close()
        self.serv = Tupu

kundi SocketUDPTest(unittest.TestCase):

    eleza setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = support.bind_port(self.serv)

    eleza tearDown(self):
        self.serv.close()
        self.serv = Tupu

kundi ThreadSafeCleanupTestCase(unittest.TestCase):
    """Subkundi of unittest.TestCase ukijumuisha thread-safe cleanup methods.

    This subkundi protects the addCleanup() na doCleanups() methods
    ukijumuisha a recursive lock.
    """

    eleza __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cleanup_lock = threading.RLock()

    eleza addCleanup(self, *args, **kwargs):
        ukijumuisha self._cleanup_lock:
            rudisha super().addCleanup(*args, **kwargs)

    eleza doCleanups(self, *args, **kwargs):
        ukijumuisha self._cleanup_lock:
            rudisha super().doCleanups(*args, **kwargs)

kundi SocketCANTest(unittest.TestCase):

    """To be able to run this test, a `vcan0` CAN interface can be created with
    the following commands:
    # modprobe vcan
    # ip link add dev vcan0 type vcan
    # ifconfig vcan0 up
    """
    interface = 'vcan0'
    bufsize = 128

    """The CAN frame structure ni defined kwenye <linux/can.h>:

    struct can_frame {
        canid_t can_id;  /* 32 bit CAN_ID + EFF/RTR/ERR flags */
        __u8    can_dlc; /* data length code: 0 .. 8 */
        __u8    data[8] __attribute__((aligned(8)));
    };
    """
    can_frame_fmt = "=IB3x8s"
    can_frame_size = struct.calcsize(can_frame_fmt)

    """The Broadcast Management Command frame structure ni defined
    kwenye <linux/can/bcm.h>:

    struct bcm_msg_head {
        __u32 opcode;
        __u32 flags;
        __u32 count;
        struct timeval ival1, ival2;
        canid_t can_id;
        __u32 nframes;
        struct can_frame frames[0];
    }

    `bcm_msg_head` must be 8 bytes aligned because of the `frames` member (see
    `struct can_frame` definition). Must use native sio standard types kila packing.
    """
    bcm_cmd_msg_fmt = "@3I4l2I"
    bcm_cmd_msg_fmt += "x" * (struct.calcsize(bcm_cmd_msg_fmt) % 8)

    eleza setUp(self):
        self.s = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.addCleanup(self.s.close)
        jaribu:
            self.s.bind((self.interface,))
        tatizo OSError:
            self.skipTest('network interface `%s` does sio exist' %
                           self.interface)


kundi SocketRDSTest(unittest.TestCase):

    """To be able to run this test, the `rds` kernel module must be loaded:
    # modprobe rds
    """
    bufsize = 8192

    eleza setUp(self):
        self.serv = socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0)
        self.addCleanup(self.serv.close)
        jaribu:
            self.port = support.bind_port(self.serv)
        tatizo OSError:
            self.skipTest('unable to bind RDS socket')


kundi ThreadableTest:
    """Threadable Test class

    The ThreadableTest kundi makes it easy to create a threaded
    client/server pair kutoka an existing unit test. To create a
    new threaded kundi kutoka an existing unit test, use multiple
    inheritance:

        kundi NewClass (OldClass, ThreadableTest):
            pita

    This kundi defines two new fixture functions ukijumuisha obvious
    purposes kila overriding:

        clientSetUp ()
        clientTearDown ()

    Any new test functions within the kundi must then define
    tests kwenye pairs, where the test name ni preceded ukijumuisha a
    '_' to indicate the client portion of the test. Ex:

        eleza testFoo(self):
            # Server portion

        eleza _testFoo(self):
            # Client portion

    Any exceptions ashiriad by the clients during their tests
    are caught na transferred to the main thread to alert
    the testing framework.

    Note, the server setup function cannot call any blocking
    functions that rely on the client thread during setup,
    unless serverExplicitReady() ni called just before
    the blocking call (such kama kwenye setting up a client/server
    connection na performing the accept() kwenye setUp().
    """

    eleza __init__(self):
        # Swap the true setup function
        self.__setUp = self.setUp
        self.__tearDown = self.tearDown
        self.setUp = self._setUp
        self.tearDown = self._tearDown

    eleza serverExplicitReady(self):
        """This method allows the server to explicitly indicate that
        it wants the client thread to proceed. This ni useful ikiwa the
        server ni about to execute a blocking routine that is
        dependent upon the client thread during its setup routine."""
        self.server_ready.set()

    eleza _setUp(self):
        self.wait_threads = support.wait_threads_exit()
        self.wait_threads.__enter__()

        self.server_ready = threading.Event()
        self.client_ready = threading.Event()
        self.done = threading.Event()
        self.queue = queue.Queue(1)
        self.server_crashed = Uongo

        # Do some munging to start the client test.
        methodname = self.id()
        i = methodname.rfind('.')
        methodname = methodname[i+1:]
        test_method = getattr(self, '_' + methodname)
        self.client_thread = thread.start_new_thread(
            self.clientRun, (test_method,))

        jaribu:
            self.__setUp()
        except:
            self.server_crashed = Kweli
            ashiria
        mwishowe:
            self.server_ready.set()
        self.client_ready.wait()

    eleza _tearDown(self):
        self.__tearDown()
        self.done.wait()
        self.wait_threads.__exit__(Tupu, Tupu, Tupu)

        ikiwa self.queue.qsize():
            exc = self.queue.get()
            ashiria exc

    eleza clientRun(self, test_func):
        self.server_ready.wait()
        jaribu:
            self.clientSetUp()
        tatizo BaseException kama e:
            self.queue.put(e)
            self.clientTearDown()
            rudisha
        mwishowe:
            self.client_ready.set()
        ikiwa self.server_crashed:
            self.clientTearDown()
            rudisha
        ikiwa sio hasattr(test_func, '__call__'):
            ashiria TypeError("test_func must be a callable function")
        jaribu:
            test_func()
        tatizo BaseException kama e:
            self.queue.put(e)
        mwishowe:
            self.clientTearDown()

    eleza clientSetUp(self):
        ashiria NotImplementedError("clientSetUp must be implemented.")

    eleza clientTearDown(self):
        self.done.set()
        thread.exit()

kundi ThreadedTCPSocketTest(SocketTCPTest, ThreadableTest):

    eleza __init__(self, methodName='runTest'):
        SocketTCPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    eleza clientSetUp(self):
        self.cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    eleza clientTearDown(self):
        self.cli.close()
        self.cli = Tupu
        ThreadableTest.clientTearDown(self)

kundi ThreadedUDPSocketTest(SocketUDPTest, ThreadableTest):

    eleza __init__(self, methodName='runTest'):
        SocketUDPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    eleza clientSetUp(self):
        self.cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    eleza clientTearDown(self):
        self.cli.close()
        self.cli = Tupu
        ThreadableTest.clientTearDown(self)

kundi ThreadedCANSocketTest(SocketCANTest, ThreadableTest):

    eleza __init__(self, methodName='runTest'):
        SocketCANTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    eleza clientSetUp(self):
        self.cli = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        jaribu:
            self.cli.bind((self.interface,))
        tatizo OSError:
            # skipTest should sio be called here, na will be called kwenye the
            # server instead
            pita

    eleza clientTearDown(self):
        self.cli.close()
        self.cli = Tupu
        ThreadableTest.clientTearDown(self)

kundi ThreadedRDSSocketTest(SocketRDSTest, ThreadableTest):

    eleza __init__(self, methodName='runTest'):
        SocketRDSTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    eleza clientSetUp(self):
        self.cli = socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0)
        jaribu:
            # RDS sockets must be bound explicitly to send ama receive data
            self.cli.bind((HOST, 0))
            self.cli_addr = self.cli.getsockname()
        tatizo OSError:
            # skipTest should sio be called here, na will be called kwenye the
            # server instead
            pita

    eleza clientTearDown(self):
        self.cli.close()
        self.cli = Tupu
        ThreadableTest.clientTearDown(self)

@unittest.skipIf(fcntl ni Tupu, "need fcntl")
@unittest.skipUnless(HAVE_SOCKET_VSOCK,
          'VSOCK sockets required kila this test.')
@unittest.skipUnless(get_cid() != 2,
          "This test can only be run on a virtual guest.")
kundi ThreadedVSOCKSocketStreamTest(unittest.TestCase, ThreadableTest):

    eleza __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    eleza setUp(self):
        self.serv = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        self.addCleanup(self.serv.close)
        self.serv.bind((socket.VMADDR_CID_ANY, VSOCKPORT))
        self.serv.listen()
        self.serverExplicitReady()
        self.conn, self.connaddr = self.serv.accept()
        self.addCleanup(self.conn.close)

    eleza clientSetUp(self):
        time.sleep(0.1)
        self.cli = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        self.addCleanup(self.cli.close)
        cid = get_cid()
        self.cli.connect((cid, VSOCKPORT))

    eleza testStream(self):
        msg = self.conn.recv(1024)
        self.assertEqual(msg, MSG)

    eleza _testStream(self):
        self.cli.send(MSG)
        self.cli.close()

kundi SocketConnectedTest(ThreadedTCPSocketTest):
    """Socket tests kila client-server connection.

    self.cli_conn ni a client socket connected to the server.  The
    setUp() method guarantees that it ni connected to the server.
    """

    eleza __init__(self, methodName='runTest'):
        ThreadedTCPSocketTest.__init__(self, methodName=methodName)

    eleza setUp(self):
        ThreadedTCPSocketTest.setUp(self)
        # Indicate explicitly we're ready kila the client thread to
        # proceed na then perform the blocking call to accept
        self.serverExplicitReady()
        conn, addr = self.serv.accept()
        self.cli_conn = conn

    eleza tearDown(self):
        self.cli_conn.close()
        self.cli_conn = Tupu
        ThreadedTCPSocketTest.tearDown(self)

    eleza clientSetUp(self):
        ThreadedTCPSocketTest.clientSetUp(self)
        self.cli.connect((HOST, self.port))
        self.serv_conn = self.cli

    eleza clientTearDown(self):
        self.serv_conn.close()
        self.serv_conn = Tupu
        ThreadedTCPSocketTest.clientTearDown(self)

kundi SocketPairTest(unittest.TestCase, ThreadableTest):

    eleza __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    eleza setUp(self):
        self.serv, self.cli = socket.socketpair()

    eleza tearDown(self):
        self.serv.close()
        self.serv = Tupu

    eleza clientSetUp(self):
        pita

    eleza clientTearDown(self):
        self.cli.close()
        self.cli = Tupu
        ThreadableTest.clientTearDown(self)


# The following classes are used by the sendmsg()/recvmsg() tests.
# Combining, kila instance, ConnectedStreamTestMixin na TCPTestBase
# gives a drop-in replacement kila SocketConnectedTest, but different
# address families can be used, na the attributes serv_addr and
# cli_addr will be set to the addresses of the endpoints.

kundi SocketTestBase(unittest.TestCase):
    """A base kundi kila socket tests.

    Subclasses must provide methods newSocket() to rudisha a new socket
    na bindSock(sock) to bind it to an unused address.

    Creates a socket self.serv na sets self.serv_addr to its address.
    """

    eleza setUp(self):
        self.serv = self.newSocket()
        self.bindServer()

    eleza bindServer(self):
        """Bind server socket na set self.serv_addr to its address."""
        self.bindSock(self.serv)
        self.serv_addr = self.serv.getsockname()

    eleza tearDown(self):
        self.serv.close()
        self.serv = Tupu


kundi SocketListeningTestMixin(SocketTestBase):
    """Mixin to listen on the server socket."""

    eleza setUp(self):
        super().setUp()
        self.serv.listen()


kundi ThreadedSocketTestMixin(ThreadSafeCleanupTestCase, SocketTestBase,
                              ThreadableTest):
    """Mixin to add client socket na allow client/server tests.

    Client socket ni self.cli na its address ni self.cli_addr.  See
    ThreadableTest kila usage information.
    """

    eleza __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ThreadableTest.__init__(self)

    eleza clientSetUp(self):
        self.cli = self.newClientSocket()
        self.bindClient()

    eleza newClientSocket(self):
        """Return a new socket kila use kama client."""
        rudisha self.newSocket()

    eleza bindClient(self):
        """Bind client socket na set self.cli_addr to its address."""
        self.bindSock(self.cli)
        self.cli_addr = self.cli.getsockname()

    eleza clientTearDown(self):
        self.cli.close()
        self.cli = Tupu
        ThreadableTest.clientTearDown(self)


kundi ConnectedStreamTestMixin(SocketListeningTestMixin,
                               ThreadedSocketTestMixin):
    """Mixin to allow client/server stream tests ukijumuisha connected client.

    Server's socket representing connection to client ni self.cli_conn
    na client's connection to server ni self.serv_conn.  (Based on
    SocketConnectedTest.)
    """

    eleza setUp(self):
        super().setUp()
        # Indicate explicitly we're ready kila the client thread to
        # proceed na then perform the blocking call to accept
        self.serverExplicitReady()
        conn, addr = self.serv.accept()
        self.cli_conn = conn

    eleza tearDown(self):
        self.cli_conn.close()
        self.cli_conn = Tupu
        super().tearDown()

    eleza clientSetUp(self):
        super().clientSetUp()
        self.cli.connect(self.serv_addr)
        self.serv_conn = self.cli

    eleza clientTearDown(self):
        jaribu:
            self.serv_conn.close()
            self.serv_conn = Tupu
        tatizo AttributeError:
            pita
        super().clientTearDown()


kundi UnixSocketTestBase(SocketTestBase):
    """Base kundi kila Unix-domain socket tests."""

    # This kundi ni used kila file descriptor pitaing tests, so we
    # create the sockets kwenye a private directory so that other users
    # can't send anything that might be problematic kila a privileged
    # user running the tests.

    eleza setUp(self):
        self.dir_path = tempfile.mkdtemp()
        self.addCleanup(os.rmdir, self.dir_path)
        super().setUp()

    eleza bindSock(self, sock):
        path = tempfile.mktemp(dir=self.dir_path)
        support.bind_unix_socket(sock, path)
        self.addCleanup(support.unlink, path)

kundi UnixStreamBase(UnixSocketTestBase):
    """Base kundi kila Unix-domain SOCK_STREAM tests."""

    eleza newSocket(self):
        rudisha socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)


kundi InetTestBase(SocketTestBase):
    """Base kundi kila IPv4 socket tests."""

    host = HOST

    eleza setUp(self):
        super().setUp()
        self.port = self.serv_addr[1]

    eleza bindSock(self, sock):
        support.bind_port(sock, host=self.host)

kundi TCPTestBase(InetTestBase):
    """Base kundi kila TCP-over-IPv4 tests."""

    eleza newSocket(self):
        rudisha socket.socket(socket.AF_INET, socket.SOCK_STREAM)

kundi UDPTestBase(InetTestBase):
    """Base kundi kila UDP-over-IPv4 tests."""

    eleza newSocket(self):
        rudisha socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

kundi SCTPStreamBase(InetTestBase):
    """Base kundi kila SCTP tests kwenye one-to-one (SOCK_STREAM) mode."""

    eleza newSocket(self):
        rudisha socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                             socket.IPPROTO_SCTP)


kundi Inet6TestBase(InetTestBase):
    """Base kundi kila IPv6 socket tests."""

    host = support.HOSTv6

kundi UDP6TestBase(Inet6TestBase):
    """Base kundi kila UDP-over-IPv6 tests."""

    eleza newSocket(self):
        rudisha socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)


# Test-skipping decorators kila use ukijumuisha ThreadableTest.

eleza skipWithClientIf(condition, reason):
    """Skip decorated test ikiwa condition ni true, add client_skip decorator.

    If the decorated object ni sio a class, sets its attribute
    "client_skip" to a decorator which will rudisha an empty function
    ikiwa the test ni to be skipped, ama the original function ikiwa it is
    not.  This can be used to avoid running the client part of a
    skipped test when using ThreadableTest.
    """
    eleza client_pita(*args, **kwargs):
        pita
    eleza skipdec(obj):
        retval = unittest.skip(reason)(obj)
        ikiwa sio isinstance(obj, type):
            retval.client_skip = lambda f: client_pita
        rudisha retval
    eleza noskipdec(obj):
        ikiwa sio (isinstance(obj, type) ama hasattr(obj, "client_skip")):
            obj.client_skip = lambda f: f
        rudisha obj
    rudisha skipdec ikiwa condition isipokua noskipdec


eleza requireAttrs(obj, *attributes):
    """Skip decorated test ikiwa obj ni missing any of the given attributes.

    Sets client_skip attribute kama skipWithClientIf() does.
    """
    missing = [name kila name kwenye attributes ikiwa sio hasattr(obj, name)]
    rudisha skipWithClientIf(
        missing, "don't have " + ", ".join(name kila name kwenye missing))


eleza requireSocket(*args):
    """Skip decorated test ikiwa a socket cannot be created ukijumuisha given arguments.

    When an argument ni given kama a string, will use the value of that
    attribute of the socket module, ama skip the test ikiwa it doesn't
    exist.  Sets client_skip attribute kama skipWithClientIf() does.
    """
    err = Tupu
    missing = [obj kila obj kwenye args if
               isinstance(obj, str) na sio hasattr(socket, obj)]
    ikiwa missing:
        err = "don't have " + ", ".join(name kila name kwenye missing)
    isipokua:
        callargs = [getattr(socket, obj) ikiwa isinstance(obj, str) isipokua obj
                    kila obj kwenye args]
        jaribu:
            s = socket.socket(*callargs)
        tatizo OSError kama e:
            # XXX: check errno?
            err = str(e)
        isipokua:
            s.close()
    rudisha skipWithClientIf(
        err ni sio Tupu,
        "can't create socket({0}): {1}".format(
            ", ".join(str(o) kila o kwenye args), err))


#######################################################################
## Begin Tests

kundi GeneralModuleTests(unittest.TestCase):

    eleza test_SocketType_is_socketobject(self):
        agiza _socket
        self.assertKweli(socket.SocketType ni _socket.socket)
        s = socket.socket()
        self.assertIsInstance(s, socket.SocketType)
        s.close()

    eleza test_repr(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ukijumuisha s:
            self.assertIn('fd=%i' % s.fileno(), repr(s))
            self.assertIn('family=%s' % socket.AF_INET, repr(s))
            self.assertIn('type=%s' % socket.SOCK_STREAM, repr(s))
            self.assertIn('proto=0', repr(s))
            self.assertNotIn('raddr', repr(s))
            s.bind(('127.0.0.1', 0))
            self.assertIn('laddr', repr(s))
            self.assertIn(str(s.getsockname()), repr(s))
        self.assertIn('[closed]', repr(s))
        self.assertNotIn('laddr', repr(s))

    @unittest.skipUnless(_socket ni sio Tupu, 'need _socket module')
    eleza test_csocket_repr(self):
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        jaribu:
            expected = ('<socket object, fd=%s, family=%s, type=%s, proto=%s>'
                        % (s.fileno(), s.family, s.type, s.proto))
            self.assertEqual(repr(s), expected)
        mwishowe:
            s.close()
        expected = ('<socket object, fd=-1, family=%s, type=%s, proto=%s>'
                    % (s.family, s.type, s.proto))
        self.assertEqual(repr(s), expected)

    eleza test_weakref(self):
        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama s:
            p = proxy(s)
            self.assertEqual(p.fileno(), s.fileno())
        s = Tupu
        jaribu:
            p.fileno()
        tatizo ReferenceError:
            pita
        isipokua:
            self.fail('Socket proxy still exists')

    eleza testSocketError(self):
        # Testing socket module exceptions
        msg = "Error raising socket exception (%s)."
        ukijumuisha self.assertRaises(OSError, msg=msg % 'OSError'):
            ashiria OSError
        ukijumuisha self.assertRaises(OSError, msg=msg % 'socket.herror'):
            ashiria socket.herror
        ukijumuisha self.assertRaises(OSError, msg=msg % 'socket.gaierror'):
            ashiria socket.gaierror

    eleza testSendtoErrors(self):
        # Testing that sendto doesn't mask failures. See #10169.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(s.close)
        s.bind(('', 0))
        sockname = s.getsockname()
        # 2 args
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto('\u2620', sockname)
        self.assertEqual(str(cm.exception),
                         "a bytes-like object ni required, sio 'str'")
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto(5j, sockname)
        self.assertEqual(str(cm.exception),
                         "a bytes-like object ni required, sio 'complex'")
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto(b'foo', Tupu)
        self.assertIn('not TupuType',str(cm.exception))
        # 3 args
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto('\u2620', 0, sockname)
        self.assertEqual(str(cm.exception),
                         "a bytes-like object ni required, sio 'str'")
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto(5j, 0, sockname)
        self.assertEqual(str(cm.exception),
                         "a bytes-like object ni required, sio 'complex'")
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto(b'foo', 0, Tupu)
        self.assertIn('not TupuType', str(cm.exception))
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto(b'foo', 'bar', sockname)
        self.assertIn('an integer ni required', str(cm.exception))
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto(b'foo', Tupu, Tupu)
        self.assertIn('an integer ni required', str(cm.exception))
        # wrong number of args
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto(b'foo')
        self.assertIn('(1 given)', str(cm.exception))
        ukijumuisha self.assertRaises(TypeError) kama cm:
            s.sendto(b'foo', 0, sockname, 4)
        self.assertIn('(4 given)', str(cm.exception))

    eleza testCrucialConstants(self):
        # Testing kila mission critical constants
        socket.AF_INET
        ikiwa socket.has_ipv6:
            socket.AF_INET6
        socket.SOCK_STREAM
        socket.SOCK_DGRAM
        socket.SOCK_RAW
        socket.SOCK_RDM
        socket.SOCK_SEQPACKET
        socket.SOL_SOCKET
        socket.SO_REUSEADDR

    eleza testCrucialIpProtoConstants(self):
        socket.IPPROTO_TCP
        socket.IPPROTO_UDP
        ikiwa socket.has_ipv6:
            socket.IPPROTO_IPV6

    @unittest.skipUnless(os.name == "nt", "Windows specific")
    eleza testWindowsSpecificConstants(self):
        socket.IPPROTO_ICLFXBM
        socket.IPPROTO_ST
        socket.IPPROTO_CBT
        socket.IPPROTO_IGP
        socket.IPPROTO_RDP
        socket.IPPROTO_PGM
        socket.IPPROTO_L2TP
        socket.IPPROTO_SCTP

    eleza testHostnameRes(self):
        # Testing hostname resolution mechanisms
        hostname = socket.gethostname()
        jaribu:
            ip = socket.gethostbyname(hostname)
        tatizo OSError:
            # Probably name lookup wasn't set up right; skip this test
            self.skipTest('name lookup failure')
        self.assertKweli(ip.find('.') >= 0, "Error resolving host to ip.")
        jaribu:
            hname, aliases, ipaddrs = socket.gethostbyaddr(ip)
        tatizo OSError:
            # Probably a similar problem kama above; skip this test
            self.skipTest('name lookup failure')
        all_host_names = [hostname, hname] + aliases
        fqhn = socket.getfqdn(ip)
        ikiwa sio fqhn kwenye all_host_names:
            self.fail("Error testing host resolution mechanisms. (fqdn: %s, all: %s)" % (fqhn, repr(all_host_names)))

    eleza test_host_resolution(self):
        kila addr kwenye [support.HOSTv4, '10.0.0.1', '255.255.255.255']:
            self.assertEqual(socket.gethostbyname(addr), addr)

        # we don't test support.HOSTv6 because there's a chance it doesn't have
        # a matching name entry (e.g. 'ip6-localhost')
        kila host kwenye [support.HOSTv4]:
            self.assertIn(host, socket.gethostbyaddr(host)[2])

    eleza test_host_resolution_bad_address(self):
        # These are all malformed IP addresses na expected sio to resolve to
        # any result.  But some ISPs, e.g. AWS, may successfully resolve these
        # IPs.
        explanation = (
            "resolving an invalid IP address did sio ashiria OSError; "
            "can be caused by a broken DNS server"
        )
        kila addr kwenye ['0.1.1.~1', '1+.1.1.1', '::1q', '::1::2',
                     '1:1:1:1:1:1:1:1:1']:
            ukijumuisha self.assertRaises(OSError, msg=addr):
                socket.gethostbyname(addr)
            ukijumuisha self.assertRaises(OSError, msg=explanation):
                socket.gethostbyaddr(addr)

    @unittest.skipUnless(hasattr(socket, 'sethostname'), "test needs socket.sethostname()")
    @unittest.skipUnless(hasattr(socket, 'gethostname'), "test needs socket.gethostname()")
    eleza test_sethostname(self):
        oldhn = socket.gethostname()
        jaribu:
            socket.sethostname('new')
        tatizo OSError kama e:
            ikiwa e.errno == errno.EPERM:
                self.skipTest("test should be run kama root")
            isipokua:
                ashiria
        jaribu:
            # running test kama root!
            self.assertEqual(socket.gethostname(), 'new')
            # Should work ukijumuisha bytes objects too
            socket.sethostname(b'bar')
            self.assertEqual(socket.gethostname(), 'bar')
        mwishowe:
            socket.sethostname(oldhn)

    @unittest.skipUnless(hasattr(socket, 'if_nameindex'),
                         'socket.if_nameindex() sio available.')
    eleza testInterfaceNameIndex(self):
        interfaces = socket.if_nameindex()
        kila index, name kwenye interfaces:
            self.assertIsInstance(index, int)
            self.assertIsInstance(name, str)
            # interface indices are non-zero integers
            self.assertGreater(index, 0)
            _index = socket.if_nametoindex(name)
            self.assertIsInstance(_index, int)
            self.assertEqual(index, _index)
            _name = socket.if_indextoname(index)
            self.assertIsInstance(_name, str)
            self.assertEqual(name, _name)

    @unittest.skipUnless(hasattr(socket, 'if_indextoname'),
                         'socket.if_indextoname() sio available.')
    eleza testInvalidInterfaceIndexToName(self):
        self.assertRaises(OSError, socket.if_indextoname, 0)
        self.assertRaises(TypeError, socket.if_indextoname, '_DEADBEEF')

    @unittest.skipUnless(hasattr(socket, 'if_nametoindex'),
                         'socket.if_nametoindex() sio available.')
    eleza testInvalidInterfaceNameToIndex(self):
        self.assertRaises(TypeError, socket.if_nametoindex, 0)
        self.assertRaises(OSError, socket.if_nametoindex, '_DEADBEEF')

    @unittest.skipUnless(hasattr(sys, 'getrefcount'),
                         'test needs sys.getrefcount()')
    eleza testRefCountGetNameInfo(self):
        # Testing reference count kila getnameinfo
        jaribu:
            # On some versions, this loses a reference
            orig = sys.getrefcount(__name__)
            socket.getnameinfo(__name__,0)
        tatizo TypeError:
            ikiwa sys.getrefcount(__name__) != orig:
                self.fail("socket.getnameinfo loses a reference")

    eleza testInterpreterCrash(self):
        # Making sure getnameinfo doesn't crash the interpreter
        jaribu:
            # On some versions, this crashes the interpreter.
            socket.getnameinfo(('x', 0, 0, 0), 0)
        tatizo OSError:
            pita

    eleza testNtoH(self):
        # This just checks that htons etc. are their own inverse,
        # when looking at the lower 16 ama 32 bits.
        sizes = {socket.htonl: 32, socket.ntohl: 32,
                 socket.htons: 16, socket.ntohs: 16}
        kila func, size kwenye sizes.items():
            mask = (1<<size) - 1
            kila i kwenye (0, 1, 0xffff, ~0xffff, 2, 0x01234567, 0x76543210):
                self.assertEqual(i & mask, func(func(i&mask)) & mask)

            swapped = func(mask)
            self.assertEqual(swapped & mask, mask)
            self.assertRaises(OverflowError, func, 1<<34)

    @support.cpython_only
    eleza testNtoHErrors(self):
        agiza _testcapi
        s_good_values = [0, 1, 2, 0xffff]
        l_good_values = s_good_values + [0xffffffff]
        l_bad_values = [-1, -2, 1<<32, 1<<1000]
        s_bad_values = l_bad_values + [_testcapi.INT_MIN - 1,
                                       _testcapi.INT_MAX + 1]
        s_deprecated_values = [1<<16, _testcapi.INT_MAX]
        kila k kwenye s_good_values:
            socket.ntohs(k)
            socket.htons(k)
        kila k kwenye l_good_values:
            socket.ntohl(k)
            socket.htonl(k)
        kila k kwenye s_bad_values:
            self.assertRaises(OverflowError, socket.ntohs, k)
            self.assertRaises(OverflowError, socket.htons, k)
        kila k kwenye l_bad_values:
            self.assertRaises(OverflowError, socket.ntohl, k)
            self.assertRaises(OverflowError, socket.htonl, k)
        kila k kwenye s_deprecated_values:
            self.assertWarns(DeprecationWarning, socket.ntohs, k)
            self.assertWarns(DeprecationWarning, socket.htons, k)

    eleza testGetServBy(self):
        eq = self.assertEqual
        # Find one service that exists, then check all the related interfaces.
        # I've ordered this by protocols that have both a tcp na udp
        # protocol, at least kila modern Linuxes.
        ikiwa (sys.platform.startswith(('freebsd', 'netbsd', 'gnukfreebsd'))
            ama sys.platform kwenye ('linux', 'darwin')):
            # avoid the 'echo' service on this platform, kama there ni an
            # assumption komaing non-standard port/protocol entry
            services = ('daytime', 'qotd', 'domain')
        isipokua:
            services = ('echo', 'daytime', 'domain')
        kila service kwenye services:
            jaribu:
                port = socket.getservbyname(service, 'tcp')
                koma
            tatizo OSError:
                pita
        isipokua:
            ashiria OSError
        # Try same call ukijumuisha optional protocol omitted
        # Issue #26936: Android getservbyname() was broken before API 23.
        ikiwa (not hasattr(sys, 'getandroidapilevel') or
                sys.getandroidapilevel() >= 23):
            port2 = socket.getservbyname(service)
            eq(port, port2)
        # Try udp, but don't barf ikiwa it doesn't exist
        jaribu:
            udpport = socket.getservbyname(service, 'udp')
        tatizo OSError:
            udpport = Tupu
        isipokua:
            eq(udpport, port)
        # Now make sure the lookup by port rudishas the same service name
        # Issue #26936: Android getservbyport() ni broken.
        ikiwa sio support.is_android:
            eq(socket.getservbyport(port2), service)
        eq(socket.getservbyport(port, 'tcp'), service)
        ikiwa udpport ni sio Tupu:
            eq(socket.getservbyport(udpport, 'udp'), service)
        # Make sure getservbyport does sio accept out of range ports.
        self.assertRaises(OverflowError, socket.getservbyport, -1)
        self.assertRaises(OverflowError, socket.getservbyport, 65536)

    eleza testDefaultTimeout(self):
        # Testing default timeout
        # The default timeout should initially be Tupu
        self.assertEqual(socket.getdefaulttimeout(), Tupu)
        ukijumuisha socket.socket() kama s:
            self.assertEqual(s.gettimeout(), Tupu)

        # Set the default timeout to 10, na see ikiwa it propagates
        ukijumuisha socket_setdefaulttimeout(10):
            self.assertEqual(socket.getdefaulttimeout(), 10)
            ukijumuisha socket.socket() kama sock:
                self.assertEqual(sock.gettimeout(), 10)

            # Reset the default timeout to Tupu, na see ikiwa it propagates
            socket.setdefaulttimeout(Tupu)
            self.assertEqual(socket.getdefaulttimeout(), Tupu)
            ukijumuisha socket.socket() kama sock:
                self.assertEqual(sock.gettimeout(), Tupu)

        # Check that setting it to an invalid value ashirias ValueError
        self.assertRaises(ValueError, socket.setdefaulttimeout, -1)

        # Check that setting it to an invalid type ashirias TypeError
        self.assertRaises(TypeError, socket.setdefaulttimeout, "spam")

    @unittest.skipUnless(hasattr(socket, 'inet_aton'),
                         'test needs socket.inet_aton()')
    eleza testIPv4_inet_aton_fourbytes(self):
        # Test that issue1008086 na issue767150 are fixed.
        # It must rudisha 4 bytes.
        self.assertEqual(b'\x00'*4, socket.inet_aton('0.0.0.0'))
        self.assertEqual(b'\xff'*4, socket.inet_aton('255.255.255.255'))

    @unittest.skipUnless(hasattr(socket, 'inet_pton'),
                         'test needs socket.inet_pton()')
    eleza testIPv4toString(self):
        kutoka socket agiza inet_aton kama f, inet_pton, AF_INET
        g = lambda a: inet_pton(AF_INET, a)

        assertInvalid = lambda func,a: self.assertRaises(
            (OSError, ValueError), func, a
        )

        self.assertEqual(b'\x00\x00\x00\x00', f('0.0.0.0'))
        self.assertEqual(b'\xff\x00\xff\x00', f('255.0.255.0'))
        self.assertEqual(b'\xaa\xaa\xaa\xaa', f('170.170.170.170'))
        self.assertEqual(b'\x01\x02\x03\x04', f('1.2.3.4'))
        self.assertEqual(b'\xff\xff\xff\xff', f('255.255.255.255'))
        # bpo-29972: inet_pton() doesn't fail on AIX
        ikiwa sio AIX:
            assertInvalid(f, '0.0.0.')
        assertInvalid(f, '300.0.0.0')
        assertInvalid(f, 'a.0.0.0')
        assertInvalid(f, '1.2.3.4.5')
        assertInvalid(f, '::1')

        self.assertEqual(b'\x00\x00\x00\x00', g('0.0.0.0'))
        self.assertEqual(b'\xff\x00\xff\x00', g('255.0.255.0'))
        self.assertEqual(b'\xaa\xaa\xaa\xaa', g('170.170.170.170'))
        self.assertEqual(b'\xff\xff\xff\xff', g('255.255.255.255'))
        assertInvalid(g, '0.0.0.')
        assertInvalid(g, '300.0.0.0')
        assertInvalid(g, 'a.0.0.0')
        assertInvalid(g, '1.2.3.4.5')
        assertInvalid(g, '::1')

    @unittest.skipUnless(hasattr(socket, 'inet_pton'),
                         'test needs socket.inet_pton()')
    eleza testIPv6toString(self):
        jaribu:
            kutoka socket agiza inet_pton, AF_INET6, has_ipv6
            ikiwa sio has_ipv6:
                self.skipTest('IPv6 sio available')
        tatizo ImportError:
            self.skipTest('could sio agiza needed symbols kutoka socket')

        ikiwa sys.platform == "win32":
            jaribu:
                inet_pton(AF_INET6, '::')
            tatizo OSError kama e:
                ikiwa e.winerror == 10022:
                    self.skipTest('IPv6 might sio be supported')

        f = lambda a: inet_pton(AF_INET6, a)
        assertInvalid = lambda a: self.assertRaises(
            (OSError, ValueError), f, a
        )

        self.assertEqual(b'\x00' * 16, f('::'))
        self.assertEqual(b'\x00' * 16, f('0::0'))
        self.assertEqual(b'\x00\x01' + b'\x00' * 14, f('1::'))
        self.assertEqual(
            b'\x45\xef\x76\xcb\x00\x1a\x56\xef\xaf\xeb\x0b\xac\x19\x24\xae\xae',
            f('45ef:76cb:1a:56ef:afeb:bac:1924:aeae')
        )
        self.assertEqual(
            b'\xad\x42\x0a\xbc' + b'\x00' * 4 + b'\x01\x27\x00\x00\x02\x54\x00\x02',
            f('ad42:abc::127:0:254:2')
        )
        self.assertEqual(b'\x00\x12\x00\x0a' + b'\x00' * 12, f('12:a::'))
        assertInvalid('0x20::')
        assertInvalid(':::')
        assertInvalid('::0::')
        assertInvalid('1::abc::')
        assertInvalid('1::abc::def')
        assertInvalid('1:2:3:4:5:6')
        assertInvalid('1:2:3:4:5:6:')
        assertInvalid('1:2:3:4:5:6:7:8:0')
        # bpo-29972: inet_pton() doesn't fail on AIX
        ikiwa sio AIX:
            assertInvalid('1:2:3:4:5:6:7:8:')

        self.assertEqual(b'\x00' * 12 + b'\xfe\x2a\x17\x40',
            f('::254.42.23.64')
        )
        self.assertEqual(
            b'\x00\x42' + b'\x00' * 8 + b'\xa2\x9b\xfe\x2a\x17\x40',
            f('42::a29b:254.42.23.64')
        )
        self.assertEqual(
            b'\x00\x42\xa8\xb9\x00\x00\x00\x02\xff\xff\xa2\x9b\xfe\x2a\x17\x40',
            f('42:a8b9:0:2:ffff:a29b:254.42.23.64')
        )
        assertInvalid('255.254.253.252')
        assertInvalid('1::260.2.3.0')
        assertInvalid('1::0.be.e.0')
        assertInvalid('1:2:3:4:5:6:7:1.2.3.4')
        assertInvalid('::1.2.3.4:0')
        assertInvalid('0.100.200.0:3:4:5:6:7:8')

    @unittest.skipUnless(hasattr(socket, 'inet_ntop'),
                         'test needs socket.inet_ntop()')
    eleza testStringToIPv4(self):
        kutoka socket agiza inet_ntoa kama f, inet_ntop, AF_INET
        g = lambda a: inet_ntop(AF_INET, a)
        assertInvalid = lambda func,a: self.assertRaises(
            (OSError, ValueError), func, a
        )

        self.assertEqual('1.0.1.0', f(b'\x01\x00\x01\x00'))
        self.assertEqual('170.85.170.85', f(b'\xaa\x55\xaa\x55'))
        self.assertEqual('255.255.255.255', f(b'\xff\xff\xff\xff'))
        self.assertEqual('1.2.3.4', f(b'\x01\x02\x03\x04'))
        assertInvalid(f, b'\x00' * 3)
        assertInvalid(f, b'\x00' * 5)
        assertInvalid(f, b'\x00' * 16)
        self.assertEqual('170.85.170.85', f(bytearray(b'\xaa\x55\xaa\x55')))

        self.assertEqual('1.0.1.0', g(b'\x01\x00\x01\x00'))
        self.assertEqual('170.85.170.85', g(b'\xaa\x55\xaa\x55'))
        self.assertEqual('255.255.255.255', g(b'\xff\xff\xff\xff'))
        assertInvalid(g, b'\x00' * 3)
        assertInvalid(g, b'\x00' * 5)
        assertInvalid(g, b'\x00' * 16)
        self.assertEqual('170.85.170.85', g(bytearray(b'\xaa\x55\xaa\x55')))

    @unittest.skipUnless(hasattr(socket, 'inet_ntop'),
                         'test needs socket.inet_ntop()')
    eleza testStringToIPv6(self):
        jaribu:
            kutoka socket agiza inet_ntop, AF_INET6, has_ipv6
            ikiwa sio has_ipv6:
                self.skipTest('IPv6 sio available')
        tatizo ImportError:
            self.skipTest('could sio agiza needed symbols kutoka socket')

        ikiwa sys.platform == "win32":
            jaribu:
                inet_ntop(AF_INET6, b'\x00' * 16)
            tatizo OSError kama e:
                ikiwa e.winerror == 10022:
                    self.skipTest('IPv6 might sio be supported')

        f = lambda a: inet_ntop(AF_INET6, a)
        assertInvalid = lambda a: self.assertRaises(
            (OSError, ValueError), f, a
        )

        self.assertEqual('::', f(b'\x00' * 16))
        self.assertEqual('::1', f(b'\x00' * 15 + b'\x01'))
        self.assertEqual(
            'aef:b01:506:1001:ffff:9997:55:170',
            f(b'\x0a\xef\x0b\x01\x05\x06\x10\x01\xff\xff\x99\x97\x00\x55\x01\x70')
        )
        self.assertEqual('::1', f(bytearray(b'\x00' * 15 + b'\x01')))

        assertInvalid(b'\x12' * 15)
        assertInvalid(b'\x12' * 17)
        assertInvalid(b'\x12' * 4)

    # XXX The following don't test module-level functionality...

    eleza testSockName(self):
        # Testing getsockname()
        port = support.find_unused_port()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        sock.bind(("0.0.0.0", port))
        name = sock.getsockname()
        # XXX(nnorwitz): http://tinyurl.com/os5jz seems to indicate
        # it reasonable to get the host's addr kwenye addition to 0.0.0.0.
        # At least kila eCos.  This ni required kila the S/390 to pita.
        jaribu:
            my_ip_addr = socket.gethostbyname(socket.gethostname())
        tatizo OSError:
            # Probably name lookup wasn't set up right; skip this test
            self.skipTest('name lookup failure')
        self.assertIn(name[0], ("0.0.0.0", my_ip_addr), '%s invalid' % name[0])
        self.assertEqual(name[1], port)

    eleza testGetSockOpt(self):
        # Testing getsockopt()
        # We know a socket should start without reuse==0
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        reuse = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        self.assertUongo(reuse != 0, "initial mode ni reuse")

    eleza testSetSockOpt(self):
        # Testing setsockopt()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        reuse = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        self.assertUongo(reuse == 0, "failed to set reuse mode")

    eleza testSendAfterClose(self):
        # testing send() after close() ukijumuisha timeout
        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama sock:
            sock.settimeout(1)
        self.assertRaises(OSError, sock.send, b"spam")

    eleza testCloseException(self):
        sock = socket.socket()
        sock.bind((socket._LOCALHOST, 0))
        socket.socket(fileno=sock.fileno()).close()
        jaribu:
            sock.close()
        tatizo OSError kama err:
            # Winsock apparently ashirias ENOTSOCK
            self.assertIn(err.errno, (errno.EBADF, errno.ENOTSOCK))
        isipokua:
            self.fail("close() should ashiria EBADF/ENOTSOCK")

    eleza testNewAttributes(self):
        # testing .family, .type na .protocol

        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama sock:
            self.assertEqual(sock.family, socket.AF_INET)
            ikiwa hasattr(socket, 'SOCK_CLOEXEC'):
                self.assertIn(sock.type,
                              (socket.SOCK_STREAM | socket.SOCK_CLOEXEC,
                               socket.SOCK_STREAM))
            isipokua:
                self.assertEqual(sock.type, socket.SOCK_STREAM)
            self.assertEqual(sock.proto, 0)

    eleza test_getsockaddrarg(self):
        sock = socket.socket()
        self.addCleanup(sock.close)
        port = support.find_unused_port()
        big_port = port + 65536
        neg_port = port - 65536
        self.assertRaises(OverflowError, sock.bind, (HOST, big_port))
        self.assertRaises(OverflowError, sock.bind, (HOST, neg_port))
        # Since find_unused_port() ni inherently subject to race conditions, we
        # call it a couple times ikiwa necessary.
        kila i kwenye itertools.count():
            port = support.find_unused_port()
            jaribu:
                sock.bind((HOST, port))
            tatizo OSError kama e:
                ikiwa e.errno != errno.EADDRINUSE ama i == 5:
                    ashiria
            isipokua:
                koma

    @unittest.skipUnless(os.name == "nt", "Windows specific")
    eleza test_sock_ioctl(self):
        self.assertKweli(hasattr(socket.socket, 'ioctl'))
        self.assertKweli(hasattr(socket, 'SIO_RCVALL'))
        self.assertKweli(hasattr(socket, 'RCVALL_ON'))
        self.assertKweli(hasattr(socket, 'RCVALL_OFF'))
        self.assertKweli(hasattr(socket, 'SIO_KEEPALIVE_VALS'))
        s = socket.socket()
        self.addCleanup(s.close)
        self.assertRaises(ValueError, s.ioctl, -1, Tupu)
        s.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 100, 100))

    @unittest.skipUnless(os.name == "nt", "Windows specific")
    @unittest.skipUnless(hasattr(socket, 'SIO_LOOPBACK_FAST_PATH'),
                         'Loopback fast path support required kila this test')
    eleza test_sio_loopback_fast_path(self):
        s = socket.socket()
        self.addCleanup(s.close)
        jaribu:
            s.ioctl(socket.SIO_LOOPBACK_FAST_PATH, Kweli)
        tatizo OSError kama exc:
            WSAEOPNOTSUPP = 10045
            ikiwa exc.winerror == WSAEOPNOTSUPP:
                self.skipTest("SIO_LOOPBACK_FAST_PATH ni defined but "
                              "doesn't implemented kwenye this Windows version")
            ashiria
        self.assertRaises(TypeError, s.ioctl, socket.SIO_LOOPBACK_FAST_PATH, Tupu)

    eleza testGetaddrinfo(self):
        jaribu:
            socket.getaddrinfo('localhost', 80)
        tatizo socket.gaierror kama err:
            ikiwa err.errno == socket.EAI_SERVICE:
                # see http://bugs.python.org/issue1282647
                self.skipTest("buggy libc version")
            ashiria
        # len of every sequence ni supposed to be == 5
        kila info kwenye socket.getaddrinfo(HOST, Tupu):
            self.assertEqual(len(info), 5)
        # host can be a domain name, a string representation of an
        # IPv4/v6 address ama Tupu
        socket.getaddrinfo('localhost', 80)
        socket.getaddrinfo('127.0.0.1', 80)
        socket.getaddrinfo(Tupu, 80)
        ikiwa support.IPV6_ENABLED:
            socket.getaddrinfo('::1', 80)
        # port can be a string service name such kama "http", a numeric
        # port number ama Tupu
        # Issue #26936: Android getaddrinfo() was broken before API level 23.
        ikiwa (not hasattr(sys, 'getandroidapilevel') or
                sys.getandroidapilevel() >= 23):
            socket.getaddrinfo(HOST, "http")
        socket.getaddrinfo(HOST, 80)
        socket.getaddrinfo(HOST, Tupu)
        # test family na socktype filters
        infos = socket.getaddrinfo(HOST, 80, socket.AF_INET, socket.SOCK_STREAM)
        kila family, type, _, _, _ kwenye infos:
            self.assertEqual(family, socket.AF_INET)
            self.assertEqual(str(family), 'AddressFamily.AF_INET')
            self.assertEqual(type, socket.SOCK_STREAM)
            self.assertEqual(str(type), 'SocketKind.SOCK_STREAM')
        infos = socket.getaddrinfo(HOST, Tupu, 0, socket.SOCK_STREAM)
        kila _, socktype, _, _, _ kwenye infos:
            self.assertEqual(socktype, socket.SOCK_STREAM)
        # test proto na flags arguments
        socket.getaddrinfo(HOST, Tupu, 0, 0, socket.SOL_TCP)
        socket.getaddrinfo(HOST, Tupu, 0, 0, 0, socket.AI_PASSIVE)
        # a server willing to support both IPv4 na IPv6 will
        # usually do this
        socket.getaddrinfo(Tupu, 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0,
                           socket.AI_PASSIVE)
        # test keyword arguments
        a = socket.getaddrinfo(HOST, Tupu)
        b = socket.getaddrinfo(host=HOST, port=Tupu)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(HOST, Tupu, socket.AF_INET)
        b = socket.getaddrinfo(HOST, Tupu, family=socket.AF_INET)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(HOST, Tupu, 0, socket.SOCK_STREAM)
        b = socket.getaddrinfo(HOST, Tupu, type=socket.SOCK_STREAM)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(HOST, Tupu, 0, 0, socket.SOL_TCP)
        b = socket.getaddrinfo(HOST, Tupu, proto=socket.SOL_TCP)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(HOST, Tupu, 0, 0, 0, socket.AI_PASSIVE)
        b = socket.getaddrinfo(HOST, Tupu, flags=socket.AI_PASSIVE)
        self.assertEqual(a, b)
        a = socket.getaddrinfo(Tupu, 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0,
                               socket.AI_PASSIVE)
        b = socket.getaddrinfo(host=Tupu, port=0, family=socket.AF_UNSPEC,
                               type=socket.SOCK_STREAM, proto=0,
                               flags=socket.AI_PASSIVE)
        self.assertEqual(a, b)
        # Issue #6697.
        self.assertRaises(UnicodeEncodeError, socket.getaddrinfo, 'localhost', '\uD800')

        # Issue 17269: test workaround kila OS X platform bug segfault
        ikiwa hasattr(socket, 'AI_NUMERICSERV'):
            jaribu:
                # The arguments here are undefined na the call may succeed
                # ama fail.  All we care here ni that it doesn't segfault.
                socket.getaddrinfo("localhost", Tupu, 0, 0, 0,
                                   socket.AI_NUMERICSERV)
            tatizo socket.gaierror:
                pita

    eleza test_getnameinfo(self):
        # only IP addresses are allowed
        self.assertRaises(OSError, socket.getnameinfo, ('mail.python.org',0), 0)

    @unittest.skipUnless(support.is_resource_enabled('network'),
                         'network ni sio enabled')
    eleza test_idna(self):
        # Check kila internet access before running test
        # (issue #12804, issue #25138).
        ukijumuisha support.transient_internet('python.org'):
            socket.gethostbyname('python.org')

        # these should all be successful
        domain = 'испытание.pythontest.net'
        socket.gethostbyname(domain)
        socket.gethostbyname_ex(domain)
        socket.getaddrinfo(domain,0,socket.AF_UNSPEC,socket.SOCK_STREAM)
        # this may sio work ikiwa the forward lookup chooses the IPv6 address, kama that doesn't
        # have a reverse entry yet
        # socket.gethostbyaddr('испытание.python.org')

    eleza check_sendall_interrupted(self, with_timeout):
        # socketpair() ni sio strictly required, but it makes things easier.
        ikiwa sio hasattr(signal, 'alarm') ama sio hasattr(socket, 'socketpair'):
            self.skipTest("signal.alarm na socket.socketpair required kila this test")
        # Our signal handlers clobber the C errno by calling a math function
        # ukijumuisha an invalid domain value.
        eleza ok_handler(*args):
            self.assertRaises(ValueError, math.acosh, 0)
        eleza raising_handler(*args):
            self.assertRaises(ValueError, math.acosh, 0)
            1 // 0
        c, s = socket.socketpair()
        old_alarm = signal.signal(signal.SIGALRM, raising_handler)
        jaribu:
            ikiwa with_timeout:
                # Just above the one second minimum kila signal.alarm
                c.settimeout(1.5)
            ukijumuisha self.assertRaises(ZeroDivisionError):
                signal.alarm(1)
                c.sendall(b"x" * support.SOCK_MAX_SIZE)
            ikiwa with_timeout:
                signal.signal(signal.SIGALRM, ok_handler)
                signal.alarm(1)
                self.assertRaises(socket.timeout, c.sendall,
                                  b"x" * support.SOCK_MAX_SIZE)
        mwishowe:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_alarm)
            c.close()
            s.close()

    eleza test_sendall_interrupted(self):
        self.check_sendall_interrupted(Uongo)

    eleza test_sendall_interrupted_with_timeout(self):
        self.check_sendall_interrupted(Kweli)

    eleza test_dealloc_warn(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        r = repr(sock)
        ukijumuisha self.assertWarns(ResourceWarning) kama cm:
            sock = Tupu
            support.gc_collect()
        self.assertIn(r, str(cm.warning.args[0]))
        # An open socket file object gets dereferenced after the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        f = sock.makefile('rb')
        r = repr(sock)
        sock = Tupu
        support.gc_collect()
        ukijumuisha self.assertWarns(ResourceWarning):
            f = Tupu
            support.gc_collect()

    eleza test_name_closed_socketio(self):
        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama sock:
            fp = sock.makefile("rb")
            fp.close()
            self.assertEqual(repr(fp), "<_io.BufferedReader name=-1>")

    eleza test_unusable_closed_socketio(self):
        ukijumuisha socket.socket() kama sock:
            fp = sock.makefile("rb", buffering=0)
            self.assertKweli(fp.readable())
            self.assertUongo(fp.writable())
            self.assertUongo(fp.seekable())
            fp.close()
            self.assertRaises(ValueError, fp.readable)
            self.assertRaises(ValueError, fp.writable)
            self.assertRaises(ValueError, fp.seekable)

    eleza test_socket_close(self):
        sock = socket.socket()
        jaribu:
            sock.bind((HOST, 0))
            socket.close(sock.fileno())
            ukijumuisha self.assertRaises(OSError):
                sock.listen(1)
        mwishowe:
            ukijumuisha self.assertRaises(OSError):
                # sock.close() fails ukijumuisha EBADF
                sock.close()
        ukijumuisha self.assertRaises(TypeError):
            socket.close(Tupu)
        ukijumuisha self.assertRaises(OSError):
            socket.close(-1)

    eleza test_makefile_mode(self):
        kila mode kwenye 'r', 'rb', 'rw', 'w', 'wb':
            ukijumuisha self.subTest(mode=mode):
                ukijumuisha socket.socket() kama sock:
                    ukijumuisha sock.makefile(mode) kama fp:
                        self.assertEqual(fp.mode, mode)

    eleza test_makefile_invalid_mode(self):
        kila mode kwenye 'rt', 'x', '+', 'a':
            ukijumuisha self.subTest(mode=mode):
                ukijumuisha socket.socket() kama sock:
                    ukijumuisha self.assertRaisesRegex(ValueError, 'invalid mode'):
                        sock.makefile(mode)

    eleza test_pickle(self):
        sock = socket.socket()
        ukijumuisha sock:
            kila protocol kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                self.assertRaises(TypeError, pickle.dumps, sock, protocol)
        kila protocol kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            family = pickle.loads(pickle.dumps(socket.AF_INET, protocol))
            self.assertEqual(family, socket.AF_INET)
            type = pickle.loads(pickle.dumps(socket.SOCK_STREAM, protocol))
            self.assertEqual(type, socket.SOCK_STREAM)

    eleza test_listen_backlog(self):
        kila backlog kwenye 0, -1:
            ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama srv:
                srv.bind((HOST, 0))
                srv.listen(backlog)

        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama srv:
            srv.bind((HOST, 0))
            srv.listen()

    @support.cpython_only
    eleza test_listen_backlog_overflow(self):
        # Issue 15989
        agiza _testcapi
        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama srv:
            srv.bind((HOST, 0))
            self.assertRaises(OverflowError, srv.listen, _testcapi.INT_MAX + 1)

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
    eleza test_flowinfo(self):
        self.assertRaises(OverflowError, socket.getnameinfo,
                          (support.HOSTv6, 0, 0xffffffff), 0)
        ukijumuisha socket.socket(socket.AF_INET6, socket.SOCK_STREAM) kama s:
            self.assertRaises(OverflowError, s.bind, (support.HOSTv6, 0, -10))

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
    eleza test_getaddrinfo_ipv6_basic(self):
        ((*_, sockaddr),) = socket.getaddrinfo(
            'ff02::1de:c0:face:8D',  # Note capital letter `D`.
            1234, socket.AF_INET6,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )
        self.assertEqual(sockaddr, ('ff02::1de:c0:face:8d', 1234, 0, 0))

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
    @unittest.skipIf(sys.platform == 'win32', 'does sio work on Windows')
    @unittest.skipIf(AIX, 'Symbolic scope id does sio work')
    eleza test_getaddrinfo_ipv6_scopeid_symbolic(self):
        # Just pick up any network interface (Linux, Mac OS X)
        (ifindex, test_interface) = socket.if_nameindex()[0]
        ((*_, sockaddr),) = socket.getaddrinfo(
            'ff02::1de:c0:face:8D%' + test_interface,
            1234, socket.AF_INET6,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )
        # Note missing interface name part kwenye IPv6 address
        self.assertEqual(sockaddr, ('ff02::1de:c0:face:8d', 1234, 0, ifindex))

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
    @unittest.skipUnless(
        sys.platform == 'win32',
        'Numeric scope id does sio work ama undocumented')
    eleza test_getaddrinfo_ipv6_scopeid_numeric(self):
        # Also works on Linux na Mac OS X, but ni sio documented (?)
        # Windows, Linux na Max OS X allow nonexistent interface numbers here.
        ifindex = 42
        ((*_, sockaddr),) = socket.getaddrinfo(
            'ff02::1de:c0:face:8D%' + str(ifindex),
            1234, socket.AF_INET6,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )
        # Note missing interface name part kwenye IPv6 address
        self.assertEqual(sockaddr, ('ff02::1de:c0:face:8d', 1234, 0, ifindex))

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
    @unittest.skipIf(sys.platform == 'win32', 'does sio work on Windows')
    @unittest.skipIf(AIX, 'Symbolic scope id does sio work')
    eleza test_getnameinfo_ipv6_scopeid_symbolic(self):
        # Just pick up any network interface.
        (ifindex, test_interface) = socket.if_nameindex()[0]
        sockaddr = ('ff02::1de:c0:face:8D', 1234, 0, ifindex)  # Note capital letter `D`.
        nameinfo = socket.getnameinfo(sockaddr, socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)
        self.assertEqual(nameinfo, ('ff02::1de:c0:face:8d%' + test_interface, '1234'))

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
    @unittest.skipUnless( sys.platform == 'win32',
        'Numeric scope id does sio work ama undocumented')
    eleza test_getnameinfo_ipv6_scopeid_numeric(self):
        # Also works on Linux (undocumented), but does sio work on Mac OS X
        # Windows na Linux allow nonexistent interface numbers here.
        ifindex = 42
        sockaddr = ('ff02::1de:c0:face:8D', 1234, 0, ifindex)  # Note capital letter `D`.
        nameinfo = socket.getnameinfo(sockaddr, socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)
        self.assertEqual(nameinfo, ('ff02::1de:c0:face:8d%' + str(ifindex), '1234'))

    eleza test_str_for_enums(self):
        # Make sure that the AF_* na SOCK_* constants have enum-like string
        # reprs.
        ukijumuisha socket.socket(socket.AF_INET, socket.SOCK_STREAM) kama s:
            self.assertEqual(str(s.family), 'AddressFamily.AF_INET')
            self.assertEqual(str(s.type), 'SocketKind.SOCK_STREAM')

    eleza test_socket_consistent_sock_type(self):
        SOCK_NONBLOCK = getattr(socket, 'SOCK_NONBLOCK', 0)
        SOCK_CLOEXEC = getattr(socket, 'SOCK_CLOEXEC', 0)
        sock_type = socket.SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC

        ukijumuisha socket.socket(socket.AF_INET, sock_type) kama s:
            self.assertEqual(s.type, socket.SOCK_STREAM)
            s.settimeout(1)
            self.assertEqual(s.type, socket.SOCK_STREAM)
            s.settimeout(0)
            self.assertEqual(s.type, socket.SOCK_STREAM)
            s.setblocking(Kweli)
            self.assertEqual(s.type, socket.SOCK_STREAM)
            s.setblocking(Uongo)
            self.assertEqual(s.type, socket.SOCK_STREAM)

    eleza test_unknown_socket_family_repr(self):
        # Test that when created ukijumuisha a family that's sio one of the known
        # AF_*/SOCK_* constants, socket.family just rudishas the number.
        #
        # To do this we fool socket.socket into believing it already has an
        # open fd because on this path it doesn't actually verify the family and
        # type na populates the socket object.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd = sock.detach()
        unknown_family = max(socket.AddressFamily.__members__.values()) + 1

        unknown_type = max(
            kind
            kila name, kind kwenye socket.SocketKind.__members__.items()
            ikiwa name haiko kwenye {'SOCK_NONBLOCK', 'SOCK_CLOEXEC'}
        ) + 1

        ukijumuisha socket.socket(
                family=unknown_family, type=unknown_type, proto=23,
                fileno=fd) kama s:
            self.assertEqual(s.family, unknown_family)
            self.assertEqual(s.type, unknown_type)
            # some OS like macOS ignore proto
            self.assertIn(s.proto, {0, 23})

    @unittest.skipUnless(hasattr(os, 'sendfile'), 'test needs os.sendfile()')
    eleza test__sendfile_use_sendfile(self):
        kundi File:
            eleza __init__(self, fd):
                self.fd = fd

            eleza fileno(self):
                rudisha self.fd
        ukijumuisha socket.socket() kama sock:
            fd = os.open(os.curdir, os.O_RDONLY)
            os.close(fd)
            ukijumuisha self.assertRaises(socket._GiveupOnSendfile):
                sock._sendfile_use_sendfile(File(fd))
            ukijumuisha self.assertRaises(OverflowError):
                sock._sendfile_use_sendfile(File(2**1000))
            ukijumuisha self.assertRaises(TypeError):
                sock._sendfile_use_sendfile(File(Tupu))

    eleza _test_socket_fileno(self, s, family, stype):
        self.assertEqual(s.family, family)
        self.assertEqual(s.type, stype)

        fd = s.fileno()
        s2 = socket.socket(fileno=fd)
        self.addCleanup(s2.close)
        # detach old fd to avoid double close
        s.detach()
        self.assertEqual(s2.family, family)
        self.assertEqual(s2.type, stype)
        self.assertEqual(s2.fileno(), fd)

    eleza test_socket_fileno(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(s.close)
        s.bind((support.HOST, 0))
        self._test_socket_fileno(s, socket.AF_INET, socket.SOCK_STREAM)

        ikiwa hasattr(socket, "SOCK_DGRAM"):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.addCleanup(s.close)
            s.bind((support.HOST, 0))
            self._test_socket_fileno(s, socket.AF_INET, socket.SOCK_DGRAM)

        ikiwa support.IPV6_ENABLED:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.addCleanup(s.close)
            s.bind((support.HOSTv6, 0, 0, 0))
            self._test_socket_fileno(s, socket.AF_INET6, socket.SOCK_STREAM)

        ikiwa hasattr(socket, "AF_UNIX"):
            tmpdir = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, tmpdir)
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.addCleanup(s.close)
            jaribu:
                s.bind(os.path.join(tmpdir, 'socket'))
            tatizo PermissionError:
                pita
            isipokua:
                self._test_socket_fileno(s, socket.AF_UNIX,
                                         socket.SOCK_STREAM)

    eleza test_socket_fileno_rejects_float(self):
        ukijumuisha self.assertRaisesRegex(TypeError, "integer argument expected"):
            socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=42.5)

    eleza test_socket_fileno_rejects_other_types(self):
        ukijumuisha self.assertRaisesRegex(TypeError, "integer ni required"):
            socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno="foo")

    eleza test_socket_fileno_rejects_invalid_socket(self):
        ukijumuisha self.assertRaisesRegex(ValueError, "negative file descriptor"):
            socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=-1)

    @unittest.skipIf(os.name == "nt", "Windows disallows -1 only")
    eleza test_socket_fileno_rejects_negative(self):
        ukijumuisha self.assertRaisesRegex(ValueError, "negative file descriptor"):
            socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=-42)

    eleza test_socket_fileno_requires_valid_fd(self):
        WSAENOTSOCK = 10038
        ukijumuisha self.assertRaises(OSError) kama cm:
            socket.socket(fileno=support.make_bad_fd())
        self.assertIn(cm.exception.errno, (errno.EBADF, WSAENOTSOCK))

        ukijumuisha self.assertRaises(OSError) kama cm:
            socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
                fileno=support.make_bad_fd())
        self.assertIn(cm.exception.errno, (errno.EBADF, WSAENOTSOCK))

    eleza test_socket_fileno_requires_socket_fd(self):
        ukijumuisha tempfile.NamedTemporaryFile() kama afile:
            ukijumuisha self.assertRaises(OSError):
                socket.socket(fileno=afile.fileno())

            ukijumuisha self.assertRaises(OSError) kama cm:
                socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM,
                    fileno=afile.fileno())
            self.assertEqual(cm.exception.errno, errno.ENOTSOCK)


@unittest.skipUnless(HAVE_SOCKET_CAN, 'SocketCan required kila this test.')
kundi BasicCANTest(unittest.TestCase):

    eleza testCrucialConstants(self):
        socket.AF_CAN
        socket.PF_CAN
        socket.CAN_RAW

    @unittest.skipUnless(hasattr(socket, "CAN_BCM"),
                         'socket.CAN_BCM required kila this test.')
    eleza testBCMConstants(self):
        socket.CAN_BCM

        # opcodes
        socket.CAN_BCM_TX_SETUP     # create (cyclic) transmission task
        socket.CAN_BCM_TX_DELETE    # remove (cyclic) transmission task
        socket.CAN_BCM_TX_READ      # read properties of (cyclic) transmission task
        socket.CAN_BCM_TX_SEND      # send one CAN frame
        socket.CAN_BCM_RX_SETUP     # create RX content filter subscription
        socket.CAN_BCM_RX_DELETE    # remove RX content filter subscription
        socket.CAN_BCM_RX_READ      # read properties of RX content filter subscription
        socket.CAN_BCM_TX_STATUS    # reply to TX_READ request
        socket.CAN_BCM_TX_EXPIRED   # notification on performed transmissions (count=0)
        socket.CAN_BCM_RX_STATUS    # reply to RX_READ request
        socket.CAN_BCM_RX_TIMEOUT   # cyclic message ni absent
        socket.CAN_BCM_RX_CHANGED   # updated CAN frame (detected content change)

        # flags
        socket.CAN_BCM_SETTIMER
        socket.CAN_BCM_STARTTIMER
        socket.CAN_BCM_TX_COUNTEVT
        socket.CAN_BCM_TX_ANNOUNCE
        socket.CAN_BCM_TX_CP_CAN_ID
        socket.CAN_BCM_RX_FILTER_ID
        socket.CAN_BCM_RX_CHECK_DLC
        socket.CAN_BCM_RX_NO_AUTOTIMER
        socket.CAN_BCM_RX_ANNOUNCE_RESUME
        socket.CAN_BCM_TX_RESET_MULTI_IDX
        socket.CAN_BCM_RX_RTR_FRAME

    eleza testCreateSocket(self):
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) kama s:
            pita

    @unittest.skipUnless(hasattr(socket, "CAN_BCM"),
                         'socket.CAN_BCM required kila this test.')
    eleza testCreateBCMSocket(self):
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_BCM) kama s:
            pita

    eleza testBindAny(self):
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) kama s:
            address = ('', )
            s.bind(address)
            self.assertEqual(s.getsockname(), address)

    eleza testTooLongInterfaceName(self):
        # most systems limit IFNAMSIZ to 16, take 1024 to be sure
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) kama s:
            self.assertRaisesRegex(OSError, 'interface name too long',
                                   s.bind, ('x' * 1024,))

    @unittest.skipUnless(hasattr(socket, "CAN_RAW_LOOPBACK"),
                         'socket.CAN_RAW_LOOPBACK required kila this test.')
    eleza testLoopback(self):
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) kama s:
            kila loopback kwenye (0, 1):
                s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_LOOPBACK,
                             loopback)
                self.assertEqual(loopback,
                    s.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_LOOPBACK))

    @unittest.skipUnless(hasattr(socket, "CAN_RAW_FILTER"),
                         'socket.CAN_RAW_FILTER required kila this test.')
    eleza testFilter(self):
        can_id, can_mask = 0x200, 0x700
        can_filter = struct.pack("=II", can_id, can_mask)
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) kama s:
            s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, can_filter)
            self.assertEqual(can_filter,
                    s.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, 8))
            s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, bytearray(can_filter))


@unittest.skipUnless(HAVE_SOCKET_CAN, 'SocketCan required kila this test.')
kundi CANTest(ThreadedCANSocketTest):

    eleza __init__(self, methodName='runTest'):
        ThreadedCANSocketTest.__init__(self, methodName=methodName)

    @classmethod
    eleza build_can_frame(cls, can_id, data):
        """Build a CAN frame."""
        can_dlc = len(data)
        data = data.ljust(8, b'\x00')
        rudisha struct.pack(cls.can_frame_fmt, can_id, can_dlc, data)

    @classmethod
    eleza dissect_can_frame(cls, frame):
        """Dissect a CAN frame."""
        can_id, can_dlc, data = struct.unpack(cls.can_frame_fmt, frame)
        rudisha (can_id, can_dlc, data[:can_dlc])

    eleza testSendFrame(self):
        cf, addr = self.s.recvkutoka(self.bufsize)
        self.assertEqual(self.cf, cf)
        self.assertEqual(addr[0], self.interface)
        self.assertEqual(addr[1], socket.AF_CAN)

    eleza _testSendFrame(self):
        self.cf = self.build_can_frame(0x00, b'\x01\x02\x03\x04\x05')
        self.cli.send(self.cf)

    eleza testSendMaxFrame(self):
        cf, addr = self.s.recvkutoka(self.bufsize)
        self.assertEqual(self.cf, cf)

    eleza _testSendMaxFrame(self):
        self.cf = self.build_can_frame(0x00, b'\x07' * 8)
        self.cli.send(self.cf)

    eleza testSendMultiFrames(self):
        cf, addr = self.s.recvkutoka(self.bufsize)
        self.assertEqual(self.cf1, cf)

        cf, addr = self.s.recvkutoka(self.bufsize)
        self.assertEqual(self.cf2, cf)

    eleza _testSendMultiFrames(self):
        self.cf1 = self.build_can_frame(0x07, b'\x44\x33\x22\x11')
        self.cli.send(self.cf1)

        self.cf2 = self.build_can_frame(0x12, b'\x99\x22\x33')
        self.cli.send(self.cf2)

    @unittest.skipUnless(hasattr(socket, "CAN_BCM"),
                         'socket.CAN_BCM required kila this test.')
    eleza _testBCM(self):
        cf, addr = self.cli.recvkutoka(self.bufsize)
        self.assertEqual(self.cf, cf)
        can_id, can_dlc, data = self.dissect_can_frame(cf)
        self.assertEqual(self.can_id, can_id)
        self.assertEqual(self.data, data)

    @unittest.skipUnless(hasattr(socket, "CAN_BCM"),
                         'socket.CAN_BCM required kila this test.')
    eleza testBCM(self):
        bcm = socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_BCM)
        self.addCleanup(bcm.close)
        bcm.connect((self.interface,))
        self.can_id = 0x123
        self.data = bytes([0xc0, 0xff, 0xee])
        self.cf = self.build_can_frame(self.can_id, self.data)
        opcode = socket.CAN_BCM_TX_SEND
        flags = 0
        count = 0
        ival1_seconds = ival1_usec = ival2_seconds = ival2_usec = 0
        bcm_can_id = 0x0222
        nframes = 1
        assert len(self.cf) == 16
        header = struct.pack(self.bcm_cmd_msg_fmt,
                    opcode,
                    flags,
                    count,
                    ival1_seconds,
                    ival1_usec,
                    ival2_seconds,
                    ival2_usec,
                    bcm_can_id,
                    nframes,
                    )
        header_plus_frame = header + self.cf
        bytes_sent = bcm.send(header_plus_frame)
        self.assertEqual(bytes_sent, len(header_plus_frame))


@unittest.skipUnless(HAVE_SOCKET_CAN_ISOTP, 'CAN ISOTP required kila this test.')
kundi ISOTPTest(unittest.TestCase):

    eleza __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = "vcan0"

    eleza testCrucialConstants(self):
        socket.AF_CAN
        socket.PF_CAN
        socket.CAN_ISOTP
        socket.SOCK_DGRAM

    eleza testCreateSocket(self):
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) kama s:
            pita

    @unittest.skipUnless(hasattr(socket, "CAN_ISOTP"),
                         'socket.CAN_ISOTP required kila this test.')
    eleza testCreateISOTPSocket(self):
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_ISOTP) kama s:
            pita

    eleza testTooLongInterfaceName(self):
        # most systems limit IFNAMSIZ to 16, take 1024 to be sure
        ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_ISOTP) kama s:
            ukijumuisha self.assertRaisesRegex(OSError, 'interface name too long'):
                s.bind(('x' * 1024, 1, 2))

    eleza testBind(self):
        jaribu:
            ukijumuisha socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_ISOTP) kama s:
                addr = self.interface, 0x123, 0x456
                s.bind(addr)
                self.assertEqual(s.getsockname(), addr)
        tatizo OSError kama e:
            ikiwa e.errno == errno.ENODEV:
                self.skipTest('network interface `%s` does sio exist' %
                           self.interface)
            isipokua:
                ashiria


@unittest.skipUnless(HAVE_SOCKET_RDS, 'RDS sockets required kila this test.')
kundi BasicRDSTest(unittest.TestCase):

    eleza testCrucialConstants(self):
        socket.AF_RDS
        socket.PF_RDS

    eleza testCreateSocket(self):
        ukijumuisha socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0) kama s:
            pita

    eleza testSocketBufferSize(self):
        bufsize = 16384
        ukijumuisha socket.socket(socket.PF_RDS, socket.SOCK_SEQPACKET, 0) kama s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufsize)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, bufsize)


@unittest.skipUnless(HAVE_SOCKET_RDS, 'RDS sockets required kila this test.')
kundi RDSTest(ThreadedRDSSocketTest):

    eleza __init__(self, methodName='runTest'):
        ThreadedRDSSocketTest.__init__(self, methodName=methodName)

    eleza setUp(self):
        super().setUp()
        self.evt = threading.Event()

    eleza testSendAndRecv(self):
        data, addr = self.serv.recvkutoka(self.bufsize)
        self.assertEqual(self.data, data)
        self.assertEqual(self.cli_addr, addr)

    eleza _testSendAndRecv(self):
        self.data = b'spam'
        self.cli.sendto(self.data, 0, (HOST, self.port))

    eleza testPeek(self):
        data, addr = self.serv.recvkutoka(self.bufsize, socket.MSG_PEEK)
        self.assertEqual(self.data, data)
        data, addr = self.serv.recvkutoka(self.bufsize)
        self.assertEqual(self.data, data)

    eleza _testPeek(self):
        self.data = b'spam'
        self.cli.sendto(self.data, 0, (HOST, self.port))

    @requireAttrs(socket.socket, 'recvmsg')
    eleza testSendAndRecvMsg(self):
        data, ancdata, msg_flags, addr = self.serv.recvmsg(self.bufsize)
        self.assertEqual(self.data, data)

    @requireAttrs(socket.socket, 'sendmsg')
    eleza _testSendAndRecvMsg(self):
        self.data = b'hello ' * 10
        self.cli.sendmsg([self.data], (), 0, (HOST, self.port))

    eleza testSendAndRecvMulti(self):
        data, addr = self.serv.recvkutoka(self.bufsize)
        self.assertEqual(self.data1, data)

        data, addr = self.serv.recvkutoka(self.bufsize)
        self.assertEqual(self.data2, data)

    eleza _testSendAndRecvMulti(self):
        self.data1 = b'bacon'
        self.cli.sendto(self.data1, 0, (HOST, self.port))

        self.data2 = b'egg'
        self.cli.sendto(self.data2, 0, (HOST, self.port))

    eleza testSelect(self):
        r, w, x = select.select([self.serv], [], [], 3.0)
        self.assertIn(self.serv, r)
        data, addr = self.serv.recvkutoka(self.bufsize)
        self.assertEqual(self.data, data)

    eleza _testSelect(self):
        self.data = b'select'
        self.cli.sendto(self.data, 0, (HOST, self.port))

@unittest.skipUnless(HAVE_SOCKET_QIPCRTR,
          'QIPCRTR sockets required kila this test.')
kundi BasicQIPCRTRTest(unittest.TestCase):

    eleza testCrucialConstants(self):
        socket.AF_QIPCRTR

    eleza testCreateSocket(self):
        ukijumuisha socket.socket(socket.AF_QIPCRTR, socket.SOCK_DGRAM) kama s:
            pita

    eleza testUnbound(self):
        ukijumuisha socket.socket(socket.AF_QIPCRTR, socket.SOCK_DGRAM) kama s:
            self.assertEqual(s.getsockname()[1], 0)

    eleza testBindSock(self):
        ukijumuisha socket.socket(socket.AF_QIPCRTR, socket.SOCK_DGRAM) kama s:
            support.bind_port(s, host=s.getsockname()[0])
            self.assertNotEqual(s.getsockname()[1], 0)

    eleza testInvalidBindSock(self):
        ukijumuisha socket.socket(socket.AF_QIPCRTR, socket.SOCK_DGRAM) kama s:
            self.assertRaises(OSError, support.bind_port, s, host=-2)

    eleza testAutoBindSock(self):
        ukijumuisha socket.socket(socket.AF_QIPCRTR, socket.SOCK_DGRAM) kama s:
            s.connect((123, 123))
            self.assertNotEqual(s.getsockname()[1], 0)

@unittest.skipIf(fcntl ni Tupu, "need fcntl")
@unittest.skipUnless(HAVE_SOCKET_VSOCK,
          'VSOCK sockets required kila this test.')
kundi BasicVSOCKTest(unittest.TestCase):

    eleza testCrucialConstants(self):
        socket.AF_VSOCK

    eleza testVSOCKConstants(self):
        socket.SO_VM_SOCKETS_BUFFER_SIZE
        socket.SO_VM_SOCKETS_BUFFER_MIN_SIZE
        socket.SO_VM_SOCKETS_BUFFER_MAX_SIZE
        socket.VMADDR_CID_ANY
        socket.VMADDR_PORT_ANY
        socket.VMADDR_CID_HOST
        socket.VM_SOCKETS_INVALID_VERSION
        socket.IOCTL_VM_SOCKETS_GET_LOCAL_CID

    eleza testCreateSocket(self):
        ukijumuisha socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM) kama s:
            pita

    eleza testSocketBufferSize(self):
        ukijumuisha socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM) kama s:
            orig_max = s.getsockopt(socket.AF_VSOCK,
                                    socket.SO_VM_SOCKETS_BUFFER_MAX_SIZE)
            orig = s.getsockopt(socket.AF_VSOCK,
                                socket.SO_VM_SOCKETS_BUFFER_SIZE)
            orig_min = s.getsockopt(socket.AF_VSOCK,
                                    socket.SO_VM_SOCKETS_BUFFER_MIN_SIZE)

            s.setsockopt(socket.AF_VSOCK,
                         socket.SO_VM_SOCKETS_BUFFER_MAX_SIZE, orig_max * 2)
            s.setsockopt(socket.AF_VSOCK,
                         socket.SO_VM_SOCKETS_BUFFER_SIZE, orig * 2)
            s.setsockopt(socket.AF_VSOCK,
                         socket.SO_VM_SOCKETS_BUFFER_MIN_SIZE, orig_min * 2)

            self.assertEqual(orig_max * 2,
                             s.getsockopt(socket.AF_VSOCK,
                             socket.SO_VM_SOCKETS_BUFFER_MAX_SIZE))
            self.assertEqual(orig * 2,
                             s.getsockopt(socket.AF_VSOCK,
                             socket.SO_VM_SOCKETS_BUFFER_SIZE))
            self.assertEqual(orig_min * 2,
                             s.getsockopt(socket.AF_VSOCK,
                             socket.SO_VM_SOCKETS_BUFFER_MIN_SIZE))


kundi BasicTCPTest(SocketConnectedTest):

    eleza __init__(self, methodName='runTest'):
        SocketConnectedTest.__init__(self, methodName=methodName)

    eleza testRecv(self):
        # Testing large receive over TCP
        msg = self.cli_conn.recv(1024)
        self.assertEqual(msg, MSG)

    eleza _testRecv(self):
        self.serv_conn.send(MSG)

    eleza testOverFlowRecv(self):
        # Testing receive kwenye chunks over TCP
        seg1 = self.cli_conn.recv(len(MSG) - 3)
        seg2 = self.cli_conn.recv(1024)
        msg = seg1 + seg2
        self.assertEqual(msg, MSG)

    eleza _testOverFlowRecv(self):
        self.serv_conn.send(MSG)

    eleza testRecvFrom(self):
        # Testing large recvkutoka() over TCP
        msg, addr = self.cli_conn.recvkutoka(1024)
        self.assertEqual(msg, MSG)

    eleza _testRecvFrom(self):
        self.serv_conn.send(MSG)

    eleza testOverFlowRecvFrom(self):
        # Testing recvkutoka() kwenye chunks over TCP
        seg1, addr = self.cli_conn.recvkutoka(len(MSG)-3)
        seg2, addr = self.cli_conn.recvkutoka(1024)
        msg = seg1 + seg2
        self.assertEqual(msg, MSG)

    eleza _testOverFlowRecvFrom(self):
        self.serv_conn.send(MSG)

    eleza testSendAll(self):
        # Testing sendall() ukijumuisha a 2048 byte string over TCP
        msg = b''
        wakati 1:
            read = self.cli_conn.recv(1024)
            ikiwa sio read:
                koma
            msg += read
        self.assertEqual(msg, b'f' * 2048)

    eleza _testSendAll(self):
        big_chunk = b'f' * 2048
        self.serv_conn.sendall(big_chunk)

    eleza testFromFd(self):
        # Testing kutokafd()
        fd = self.cli_conn.fileno()
        sock = socket.kutokafd(fd, socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        self.assertIsInstance(sock, socket.socket)
        msg = sock.recv(1024)
        self.assertEqual(msg, MSG)

    eleza _testFromFd(self):
        self.serv_conn.send(MSG)

    eleza testDup(self):
        # Testing dup()
        sock = self.cli_conn.dup()
        self.addCleanup(sock.close)
        msg = sock.recv(1024)
        self.assertEqual(msg, MSG)

    eleza _testDup(self):
        self.serv_conn.send(MSG)

    eleza testShutdown(self):
        # Testing shutdown()
        msg = self.cli_conn.recv(1024)
        self.assertEqual(msg, MSG)
        # wait kila _testShutdown to finish: on OS X, when the server
        # closes the connection the client also becomes disconnected,
        # na the client's shutdown call will fail. (Issue #4397.)
        self.done.wait()

    eleza _testShutdown(self):
        self.serv_conn.send(MSG)
        self.serv_conn.shutdown(2)

    testShutdown_overflow = support.cpython_only(testShutdown)

    @support.cpython_only
    eleza _testShutdown_overflow(self):
        agiza _testcapi
        self.serv_conn.send(MSG)
        # Issue 15989
        self.assertRaises(OverflowError, self.serv_conn.shutdown,
                          _testcapi.INT_MAX + 1)
        self.assertRaises(OverflowError, self.serv_conn.shutdown,
                          2 + (_testcapi.UINT_MAX + 1))
        self.serv_conn.shutdown(2)

    eleza testDetach(self):
        # Testing detach()
        fileno = self.cli_conn.fileno()
        f = self.cli_conn.detach()
        self.assertEqual(f, fileno)
        # cli_conn cannot be used anymore...
        self.assertKweli(self.cli_conn._closed)
        self.assertRaises(OSError, self.cli_conn.recv, 1024)
        self.cli_conn.close()
        # ...but we can create another socket using the (still open)
        # file descriptor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=f)
        self.addCleanup(sock.close)
        msg = sock.recv(1024)
        self.assertEqual(msg, MSG)

    eleza _testDetach(self):
        self.serv_conn.send(MSG)


kundi BasicUDPTest(ThreadedUDPSocketTest):

    eleza __init__(self, methodName='runTest'):
        ThreadedUDPSocketTest.__init__(self, methodName=methodName)

    eleza testSendtoAndRecv(self):
        # Testing sendto() na Recv() over UDP
        msg = self.serv.recv(len(MSG))
        self.assertEqual(msg, MSG)

    eleza _testSendtoAndRecv(self):
        self.cli.sendto(MSG, 0, (HOST, self.port))

    eleza testRecvFrom(self):
        # Testing recvkutoka() over UDP
        msg, addr = self.serv.recvkutoka(len(MSG))
        self.assertEqual(msg, MSG)

    eleza _testRecvFrom(self):
        self.cli.sendto(MSG, 0, (HOST, self.port))

    eleza testRecvFromNegative(self):
        # Negative lengths pitaed to recvkutoka should give ValueError.
        self.assertRaises(ValueError, self.serv.recvkutoka, -1)

    eleza _testRecvFromNegative(self):
        self.cli.sendto(MSG, 0, (HOST, self.port))

# Tests kila the sendmsg()/recvmsg() interface.  Where possible, the
# same test code ni used ukijumuisha different families na types of socket
# (e.g. stream, datagram), na tests using recvmsg() are repeated
# using recvmsg_into().
#
# The generic test classes such kama SendmsgTests and
# RecvmsgGenericTests inherit kutoka SendrecvmsgBase na expect to be
# supplied ukijumuisha sockets cli_sock na serv_sock representing the
# client's na the server's end of the connection respectively, and
# attributes cli_addr na serv_addr holding their (numeric where
# appropriate) addresses.
#
# The final concrete test classes combine these ukijumuisha subclasses of
# SocketTestBase which set up client na server sockets of a specific
# type, na ukijumuisha subclasses of SendrecvmsgBase such as
# SendrecvmsgDgramBase na SendrecvmsgConnectedBase which map these
# sockets to cli_sock na serv_sock na override the methods and
# attributes of SendrecvmsgBase to fill kwenye destination addresses if
# needed when sending, check kila specific flags kwenye msg_flags, etc.
#
# RecvmsgIntoMixin provides a version of doRecvmsg() implemented using
# recvmsg_into().

# XXX: like the other datagram (UDP) tests kwenye this module, the code
# here assumes that datagram delivery on the local machine will be
# reliable.

kundi SendrecvmsgBase(ThreadSafeCleanupTestCase):
    # Base kundi kila sendmsg()/recvmsg() tests.

    # Time kwenye seconds to wait before considering a test failed, or
    # Tupu kila no timeout.  Not all tests actually set a timeout.
    fail_timeout = 3.0

    eleza setUp(self):
        self.misc_event = threading.Event()
        super().setUp()

    eleza sendToServer(self, msg):
        # Send msg to the server.
        rudisha self.cli_sock.send(msg)

    # Tuple of alternative default arguments kila sendmsg() when called
    # via sendmsgToServer() (e.g. to include a destination address).
    sendmsg_to_server_defaults = ()

    eleza sendmsgToServer(self, *args):
        # Call sendmsg() on self.cli_sock ukijumuisha the given arguments,
        # filling kwenye any arguments which are sio supplied ukijumuisha the
        # corresponding items of self.sendmsg_to_server_defaults, if
        # any.
        rudisha self.cli_sock.sendmsg(
            *(args + self.sendmsg_to_server_defaults[len(args):]))

    eleza doRecvmsg(self, sock, bufsize, *args):
        # Call recvmsg() on sock ukijumuisha given arguments na rudisha its
        # result.  Should be used kila tests which can use either
        # recvmsg() ama recvmsg_into() - RecvmsgIntoMixin overrides
        # this method ukijumuisha one which emulates it using recvmsg_into(),
        # thus allowing the same test to be used kila both methods.
        result = sock.recvmsg(bufsize, *args)
        self.registerRecvmsgResult(result)
        rudisha result

    eleza registerRecvmsgResult(self, result):
        # Called by doRecvmsg() ukijumuisha the rudisha value of recvmsg() or
        # recvmsg_into().  Can be overridden to arrange cleanup based
        # on the rudishaed ancillary data, kila instance.
        pita

    eleza checkRecvmsgAddress(self, addr1, addr2):
        # Called to compare the received address ukijumuisha the address of
        # the peer.
        self.assertEqual(addr1, addr2)

    # Flags that are normally unset kwenye msg_flags
    msg_flags_common_unset = 0
    kila name kwenye ("MSG_CTRUNC", "MSG_OOB"):
        msg_flags_common_unset |= getattr(socket, name, 0)

    # Flags that are normally set
    msg_flags_common_set = 0

    # Flags set when a complete record has been received (e.g. MSG_EOR
    # kila SCTP)
    msg_flags_eor_indicator = 0

    # Flags set when a complete record has sio been received
    # (e.g. MSG_TRUNC kila datagram sockets)
    msg_flags_non_eor_indicator = 0

    eleza checkFlags(self, flags, eor=Tupu, checkset=0, checkunset=0, ignore=0):
        # Method to check the value of msg_flags rudishaed by recvmsg[_into]().
        #
        # Checks that all bits kwenye msg_flags_common_set attribute are
        # set kwenye "flags" na all bits kwenye msg_flags_common_unset are
        # unset.
        #
        # The "eor" argument specifies whether the flags should
        # indicate that a full record (or datagram) has been received.
        # If "eor" ni Tupu, no checks are done; otherwise, checks
        # that:
        #
        #  * ikiwa "eor" ni true, all bits kwenye msg_flags_eor_indicator are
        #    set na all bits kwenye msg_flags_non_eor_indicator are unset
        #
        #  * ikiwa "eor" ni false, all bits kwenye msg_flags_non_eor_indicator
        #    are set na all bits kwenye msg_flags_eor_indicator are unset
        #
        # If "checkset" and/or "checkunset" are supplied, they require
        # the given bits to be set ama unset respectively, overriding
        # what the attributes require kila those bits.
        #
        # If any bits are set kwenye "ignore", they will sio be checked,
        # regardless of the other inputs.
        #
        # Will ashiria Exception ikiwa the inputs require a bit to be both
        # set na unset, na it ni sio ignored.

        defaultset = self.msg_flags_common_set
        defaultunset = self.msg_flags_common_unset

        ikiwa eor:
            defaultset |= self.msg_flags_eor_indicator
            defaultunset |= self.msg_flags_non_eor_indicator
        lasivyo eor ni sio Tupu:
            defaultset |= self.msg_flags_non_eor_indicator
            defaultunset |= self.msg_flags_eor_indicator

        # Function arguments override defaults
        defaultset &= ~checkunset
        defaultunset &= ~checkset

        # Merge arguments ukijumuisha remaining defaults, na check kila conflicts
        checkset |= defaultset
        checkunset |= defaultunset
        inboth = checkset & checkunset & ~ignore
        ikiwa inboth:
            ashiria Exception("contradictory set, unset requirements kila flags "
                            "{0:#x}".format(inboth))

        # Compare ukijumuisha given msg_flags value
        mask = (checkset | checkunset) & ~ignore
        self.assertEqual(flags & mask, checkset & mask)


kundi RecvmsgIntoMixin(SendrecvmsgBase):
    # Mixin to implement doRecvmsg() using recvmsg_into().

    eleza doRecvmsg(self, sock, bufsize, *args):
        buf = bytearray(bufsize)
        result = sock.recvmsg_into([buf], *args)
        self.registerRecvmsgResult(result)
        self.assertGreaterEqual(result[0], 0)
        self.assertLessEqual(result[0], bufsize)
        rudisha (bytes(buf[:result[0]]),) + result[1:]


kundi SendrecvmsgDgramFlagsBase(SendrecvmsgBase):
    # Defines flags to be checked kwenye msg_flags kila datagram sockets.

    @property
    eleza msg_flags_non_eor_indicator(self):
        rudisha super().msg_flags_non_eor_indicator | socket.MSG_TRUNC


kundi SendrecvmsgSCTPFlagsBase(SendrecvmsgBase):
    # Defines flags to be checked kwenye msg_flags kila SCTP sockets.

    @property
    eleza msg_flags_eor_indicator(self):
        rudisha super().msg_flags_eor_indicator | socket.MSG_EOR


kundi SendrecvmsgConnectionlessBase(SendrecvmsgBase):
    # Base kundi kila tests on connectionless-mode sockets.  Users must
    # supply sockets on attributes cli na serv to be mapped to
    # cli_sock na serv_sock respectively.

    @property
    eleza serv_sock(self):
        rudisha self.serv

    @property
    eleza cli_sock(self):
        rudisha self.cli

    @property
    eleza sendmsg_to_server_defaults(self):
        rudisha ([], [], 0, self.serv_addr)

    eleza sendToServer(self, msg):
        rudisha self.cli_sock.sendto(msg, self.serv_addr)


kundi SendrecvmsgConnectedBase(SendrecvmsgBase):
    # Base kundi kila tests on connected sockets.  Users must supply
    # sockets on attributes serv_conn na cli_conn (representing the
    # connections *to* the server na the client), to be mapped to
    # cli_sock na serv_sock respectively.

    @property
    eleza serv_sock(self):
        rudisha self.cli_conn

    @property
    eleza cli_sock(self):
        rudisha self.serv_conn

    eleza checkRecvmsgAddress(self, addr1, addr2):
        # Address ni currently "unspecified" kila a connected socket,
        # so we don't examine it
        pita


kundi SendrecvmsgServerTimeoutBase(SendrecvmsgBase):
    # Base kundi to set a timeout on server's socket.

    eleza setUp(self):
        super().setUp()
        self.serv_sock.settimeout(self.fail_timeout)


kundi SendmsgTests(SendrecvmsgServerTimeoutBase):
    # Tests kila sendmsg() which can use any socket type na do not
    # involve recvmsg() ama recvmsg_into().

    eleza testSendmsg(self):
        # Send a simple message ukijumuisha sendmsg().
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    eleza _testSendmsg(self):
        self.assertEqual(self.sendmsgToServer([MSG]), len(MSG))

    eleza testSendmsgDataGenerator(self):
        # Send kutoka buffer obtained kutoka a generator (not a sequence).
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    eleza _testSendmsgDataGenerator(self):
        self.assertEqual(self.sendmsgToServer((o kila o kwenye [MSG])),
                         len(MSG))

    eleza testSendmsgAncillaryGenerator(self):
        # Gather (empty) ancillary data kutoka a generator.
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    eleza _testSendmsgAncillaryGenerator(self):
        self.assertEqual(self.sendmsgToServer([MSG], (o kila o kwenye [])),
                         len(MSG))

    eleza testSendmsgArray(self):
        # Send data kutoka an array instead of the usual bytes object.
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    eleza _testSendmsgArray(self):
        self.assertEqual(self.sendmsgToServer([array.array("B", MSG)]),
                         len(MSG))

    eleza testSendmsgGather(self):
        # Send message data kutoka more than one buffer (gather write).
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    eleza _testSendmsgGather(self):
        self.assertEqual(self.sendmsgToServer([MSG[:3], MSG[3:]]), len(MSG))

    eleza testSendmsgBadArgs(self):
        # Check that sendmsg() rejects invalid arguments.
        self.assertEqual(self.serv_sock.recv(1000), b"done")

    eleza _testSendmsgBadArgs(self):
        self.assertRaises(TypeError, self.cli_sock.sendmsg)
        self.assertRaises(TypeError, self.sendmsgToServer,
                          b"not kwenye an iterable")
        self.assertRaises(TypeError, self.sendmsgToServer,
                          object())
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [object()])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG, object()])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], object())
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [], object())
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [], 0, object())
        self.sendToServer(b"done")

    eleza testSendmsgBadCmsg(self):
        # Check that invalid ancillary data items are rejected.
        self.assertEqual(self.serv_sock.recv(1000), b"done")

    eleza _testSendmsgBadCmsg(self):
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [object()])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(object(), 0, b"data")])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, object(), b"data")])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, 0, object())])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, 0)])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, 0, b"data", 42)])
        self.sendToServer(b"done")

    @requireAttrs(socket, "CMSG_SPACE")
    eleza testSendmsgBadMultiCmsg(self):
        # Check that invalid ancillary data items are rejected when
        # more than one item ni present.
        self.assertEqual(self.serv_sock.recv(1000), b"done")

    @testSendmsgBadMultiCmsg.client_skip
    eleza _testSendmsgBadMultiCmsg(self):
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [0, 0, b""])
        self.assertRaises(TypeError, self.sendmsgToServer,
                          [MSG], [(0, 0, b""), object()])
        self.sendToServer(b"done")

    eleza testSendmsgExcessCmsgReject(self):
        # Check that sendmsg() rejects excess ancillary data items
        # when the number that can be sent ni limited.
        self.assertEqual(self.serv_sock.recv(1000), b"done")

    eleza _testSendmsgExcessCmsgReject(self):
        ikiwa sio hasattr(socket, "CMSG_SPACE"):
            # Can only send one item
            ukijumuisha self.assertRaises(OSError) kama cm:
                self.sendmsgToServer([MSG], [(0, 0, b""), (0, 0, b"")])
            self.assertIsTupu(cm.exception.errno)
        self.sendToServer(b"done")

    eleza testSendmsgAfterClose(self):
        # Check that sendmsg() fails on a closed socket.
        pita

    eleza _testSendmsgAfterClose(self):
        self.cli_sock.close()
        self.assertRaises(OSError, self.sendmsgToServer, [MSG])


kundi SendmsgStreamTests(SendmsgTests):
    # Tests kila sendmsg() which require a stream socket na do not
    # involve recvmsg() ama recvmsg_into().

    eleza testSendmsgExplicitTupuAddr(self):
        # Check that peer address can be specified kama Tupu.
        self.assertEqual(self.serv_sock.recv(len(MSG)), MSG)

    eleza _testSendmsgExplicitTupuAddr(self):
        self.assertEqual(self.sendmsgToServer([MSG], [], 0, Tupu), len(MSG))

    eleza testSendmsgTimeout(self):
        # Check that timeout works ukijumuisha sendmsg().
        self.assertEqual(self.serv_sock.recv(512), b"a"*512)
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))

    eleza _testSendmsgTimeout(self):
        jaribu:
            self.cli_sock.settimeout(0.03)
            jaribu:
                wakati Kweli:
                    self.sendmsgToServer([b"a"*512])
            tatizo socket.timeout:
                pita
            tatizo OSError kama exc:
                ikiwa exc.errno != errno.ENOMEM:
                    ashiria
                # bpo-33937 the test randomly fails on Travis CI with
                # "OSError: [Errno 12] Cannot allocate memory"
            isipokua:
                self.fail("socket.timeout sio ashiriad")
        mwishowe:
            self.misc_event.set()

    # XXX: would be nice to have more tests kila sendmsg flags argument.

    # Linux supports MSG_DONTWAIT when sending, but kwenye general, it
    # only works when receiving.  Could add other platforms ikiwa they
    # support it too.
    @skipWithClientIf(sys.platform haiko kwenye {"linux"},
                      "MSG_DONTWAIT sio known to work on this platform when "
                      "sending")
    eleza testSendmsgDontWait(self):
        # Check that MSG_DONTWAIT kwenye flags causes non-blocking behaviour.
        self.assertEqual(self.serv_sock.recv(512), b"a"*512)
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))

    @testSendmsgDontWait.client_skip
    eleza _testSendmsgDontWait(self):
        jaribu:
            ukijumuisha self.assertRaises(OSError) kama cm:
                wakati Kweli:
                    self.sendmsgToServer([b"a"*512], [], socket.MSG_DONTWAIT)
            # bpo-33937: catch also ENOMEM, the test randomly fails on Travis CI
            # ukijumuisha "OSError: [Errno 12] Cannot allocate memory"
            self.assertIn(cm.exception.errno,
                          (errno.EAGAIN, errno.EWOULDBLOCK, errno.ENOMEM))
        mwishowe:
            self.misc_event.set()


kundi SendmsgConnectionlessTests(SendmsgTests):
    # Tests kila sendmsg() which require a connectionless-mode
    # (e.g. datagram) socket, na do sio involve recvmsg() or
    # recvmsg_into().

    eleza testSendmsgNoDestAddr(self):
        # Check that sendmsg() fails when no destination address is
        # given kila unconnected socket.
        pita

    eleza _testSendmsgNoDestAddr(self):
        self.assertRaises(OSError, self.cli_sock.sendmsg,
                          [MSG])
        self.assertRaises(OSError, self.cli_sock.sendmsg,
                          [MSG], [], 0, Tupu)


kundi RecvmsgGenericTests(SendrecvmsgBase):
    # Tests kila recvmsg() which can also be emulated using
    # recvmsg_into(), na can use any socket type.

    eleza testRecvmsg(self):
        # Receive a simple message ukijumuisha recvmsg[_into]().
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, len(MSG))
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsg(self):
        self.sendToServer(MSG)

    eleza testRecvmsgExplicitDefaults(self):
        # Test recvmsg[_into]() ukijumuisha default arguments provided explicitly.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 0, 0)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgExplicitDefaults(self):
        self.sendToServer(MSG)

    eleza testRecvmsgShorter(self):
        # Receive a message smaller than buffer.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG) + 42)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgShorter(self):
        self.sendToServer(MSG)

    eleza testRecvmsgTrunc(self):
        # Receive part of message, check kila truncation indicators.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG) - 3)
        self.assertEqual(msg, MSG[:-3])
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Uongo)

    eleza _testRecvmsgTrunc(self):
        self.sendToServer(MSG)

    eleza testRecvmsgShortAncillaryBuf(self):
        # Test ancillary data buffer too small to hold any ancillary data.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 1)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgShortAncillaryBuf(self):
        self.sendToServer(MSG)

    eleza testRecvmsgLongAncillaryBuf(self):
        # Test large ancillary data buffer.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 10240)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgLongAncillaryBuf(self):
        self.sendToServer(MSG)

    eleza testRecvmsgAfterClose(self):
        # Check that recvmsg[_into]() fails on a closed socket.
        self.serv_sock.close()
        self.assertRaises(OSError, self.doRecvmsg, self.serv_sock, 1024)

    eleza _testRecvmsgAfterClose(self):
        pita

    eleza testRecvmsgTimeout(self):
        # Check that timeout works.
        jaribu:
            self.serv_sock.settimeout(0.03)
            self.assertRaises(socket.timeout,
                              self.doRecvmsg, self.serv_sock, len(MSG))
        mwishowe:
            self.misc_event.set()

    eleza _testRecvmsgTimeout(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))

    @requireAttrs(socket, "MSG_PEEK")
    eleza testRecvmsgPeek(self):
        # Check that MSG_PEEK kwenye flags enables examination of pending
        # data without consuming it.

        # Receive part of data ukijumuisha MSG_PEEK.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG) - 3, 0,
                                                   socket.MSG_PEEK)
        self.assertEqual(msg, MSG[:-3])
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        # Ignoring MSG_TRUNC here (so this test ni the same kila stream
        # na datagram sockets).  Some wording kwenye POSIX seems to
        # suggest that it needn't be set when peeking, but that may
        # just be a slip.
        self.checkFlags(flags, eor=Uongo,
                        ignore=getattr(socket, "MSG_TRUNC", 0))

        # Receive all data ukijumuisha MSG_PEEK.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 0,
                                                   socket.MSG_PEEK)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

        # Check that the same data can still be received normally.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, len(MSG))
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    @testRecvmsgPeek.client_skip
    eleza _testRecvmsgPeek(self):
        self.sendToServer(MSG)

    @requireAttrs(socket.socket, "sendmsg")
    eleza testRecvmsgFromSendmsg(self):
        # Test receiving ukijumuisha recvmsg[_into]() when message ni sent
        # using sendmsg().
        self.serv_sock.settimeout(self.fail_timeout)
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, len(MSG))
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    @testRecvmsgFromSendmsg.client_skip
    eleza _testRecvmsgFromSendmsg(self):
        self.assertEqual(self.sendmsgToServer([MSG[:3], MSG[3:]]), len(MSG))


kundi RecvmsgGenericStreamTests(RecvmsgGenericTests):
    # Tests which require a stream socket na can use either recvmsg()
    # ama recvmsg_into().

    eleza testRecvmsgEOF(self):
        # Receive end-of-stream indicator (b"", peer socket closed).
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, 1024)
        self.assertEqual(msg, b"")
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Tupu) # Might sio have end-of-record marker

    eleza _testRecvmsgEOF(self):
        self.cli_sock.close()

    eleza testRecvmsgOverflow(self):
        # Receive a message kwenye more than one chunk.
        seg1, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                    len(MSG) - 3)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Uongo)

        seg2, ancdata, flags, addr = self.doRecvmsg(self.serv_sock, 1024)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

        msg = seg1 + seg2
        self.assertEqual(msg, MSG)

    eleza _testRecvmsgOverflow(self):
        self.sendToServer(MSG)


kundi RecvmsgTests(RecvmsgGenericTests):
    # Tests kila recvmsg() which can use any socket type.

    eleza testRecvmsgBadArgs(self):
        # Check that recvmsg() rejects invalid arguments.
        self.assertRaises(TypeError, self.serv_sock.recvmsg)
        self.assertRaises(ValueError, self.serv_sock.recvmsg,
                          -1, 0, 0)
        self.assertRaises(ValueError, self.serv_sock.recvmsg,
                          len(MSG), -1, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg,
                          [bytearray(10)], 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg,
                          object(), 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg,
                          len(MSG), object(), 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg,
                          len(MSG), 0, object())

        msg, ancdata, flags, addr = self.serv_sock.recvmsg(len(MSG), 0, 0)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgBadArgs(self):
        self.sendToServer(MSG)


kundi RecvmsgIntoTests(RecvmsgIntoMixin, RecvmsgGenericTests):
    # Tests kila recvmsg_into() which can use any socket type.

    eleza testRecvmsgIntoBadArgs(self):
        # Check that recvmsg_into() rejects invalid arguments.
        buf = bytearray(len(MSG))
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          len(MSG), 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          buf, 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [object()], 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [b"I'm sio writable"], 0, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [buf, object()], 0, 0)
        self.assertRaises(ValueError, self.serv_sock.recvmsg_into,
                          [buf], -1, 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [buf], object(), 0)
        self.assertRaises(TypeError, self.serv_sock.recvmsg_into,
                          [buf], 0, object())

        nbytes, ancdata, flags, addr = self.serv_sock.recvmsg_into([buf], 0, 0)
        self.assertEqual(nbytes, len(MSG))
        self.assertEqual(buf, bytearray(MSG))
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgIntoBadArgs(self):
        self.sendToServer(MSG)

    eleza testRecvmsgIntoGenerator(self):
        # Receive into buffer obtained kutoka a generator (not a sequence).
        buf = bytearray(len(MSG))
        nbytes, ancdata, flags, addr = self.serv_sock.recvmsg_into(
            (o kila o kwenye [buf]))
        self.assertEqual(nbytes, len(MSG))
        self.assertEqual(buf, bytearray(MSG))
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgIntoGenerator(self):
        self.sendToServer(MSG)

    eleza testRecvmsgIntoArray(self):
        # Receive into an array rather than the usual bytearray.
        buf = array.array("B", [0] * len(MSG))
        nbytes, ancdata, flags, addr = self.serv_sock.recvmsg_into([buf])
        self.assertEqual(nbytes, len(MSG))
        self.assertEqual(buf.tobytes(), MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgIntoArray(self):
        self.sendToServer(MSG)

    eleza testRecvmsgIntoScatter(self):
        # Receive into multiple buffers (scatter write).
        b1 = bytearray(b"----")
        b2 = bytearray(b"0123456789")
        b3 = bytearray(b"--------------")
        nbytes, ancdata, flags, addr = self.serv_sock.recvmsg_into(
            [b1, memoryview(b2)[2:9], b3])
        self.assertEqual(nbytes, len(b"Mary had a little lamb"))
        self.assertEqual(b1, bytearray(b"Mary"))
        self.assertEqual(b2, bytearray(b"01 had a 9"))
        self.assertEqual(b3, bytearray(b"little lamb---"))
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli)

    eleza _testRecvmsgIntoScatter(self):
        self.sendToServer(b"Mary had a little lamb")


kundi CmsgMacroTests(unittest.TestCase):
    # Test the functions CMSG_LEN() na CMSG_SPACE().  Tests
    # assumptions used by sendmsg() na recvmsg[_into](), which share
    # code ukijumuisha these functions.

    # Match the definition kwenye socketmodule.c
    jaribu:
        agiza _testcapi
    tatizo ImportError:
        socklen_t_limit = 0x7fffffff
    isipokua:
        socklen_t_limit = min(0x7fffffff, _testcapi.INT_MAX)

    @requireAttrs(socket, "CMSG_LEN")
    eleza testCMSG_LEN(self):
        # Test CMSG_LEN() ukijumuisha various valid na invalid values,
        # checking the assumptions used by recvmsg() na sendmsg().
        toobig = self.socklen_t_limit - socket.CMSG_LEN(0) + 1
        values = list(range(257)) + list(range(toobig - 257, toobig))

        # struct cmsghdr has at least three members, two of which are ints
        self.assertGreater(socket.CMSG_LEN(0), array.array("i").itemsize * 2)
        kila n kwenye values:
            ret = socket.CMSG_LEN(n)
            # This ni how recvmsg() calculates the data size
            self.assertEqual(ret - socket.CMSG_LEN(0), n)
            self.assertLessEqual(ret, self.socklen_t_limit)

        self.assertRaises(OverflowError, socket.CMSG_LEN, -1)
        # sendmsg() shares code ukijumuisha these functions, na requires
        # that it reject values over the limit.
        self.assertRaises(OverflowError, socket.CMSG_LEN, toobig)
        self.assertRaises(OverflowError, socket.CMSG_LEN, sys.maxsize)

    @requireAttrs(socket, "CMSG_SPACE")
    eleza testCMSG_SPACE(self):
        # Test CMSG_SPACE() ukijumuisha various valid na invalid values,
        # checking the assumptions used by sendmsg().
        toobig = self.socklen_t_limit - socket.CMSG_SPACE(1) + 1
        values = list(range(257)) + list(range(toobig - 257, toobig))

        last = socket.CMSG_SPACE(0)
        # struct cmsghdr has at least three members, two of which are ints
        self.assertGreater(last, array.array("i").itemsize * 2)
        kila n kwenye values:
            ret = socket.CMSG_SPACE(n)
            self.assertGreaterEqual(ret, last)
            self.assertGreaterEqual(ret, socket.CMSG_LEN(n))
            self.assertGreaterEqual(ret, n + socket.CMSG_LEN(0))
            self.assertLessEqual(ret, self.socklen_t_limit)
            last = ret

        self.assertRaises(OverflowError, socket.CMSG_SPACE, -1)
        # sendmsg() shares code ukijumuisha these functions, na requires
        # that it reject values over the limit.
        self.assertRaises(OverflowError, socket.CMSG_SPACE, toobig)
        self.assertRaises(OverflowError, socket.CMSG_SPACE, sys.maxsize)


kundi SCMRightsTest(SendrecvmsgServerTimeoutBase):
    # Tests kila file descriptor pitaing on Unix-domain sockets.

    # Invalid file descriptor value that's unlikely to evaluate to a
    # real FD even ikiwa one of its bytes ni replaced ukijumuisha a different
    # value (which shouldn't actually happen).
    badfd = -0x5555

    eleza newFDs(self, n):
        # Return a list of n file descriptors kila newly-created files
        # containing their list indices kama ASCII numbers.
        fds = []
        kila i kwenye range(n):
            fd, path = tempfile.mkstemp()
            self.addCleanup(os.unlink, path)
            self.addCleanup(os.close, fd)
            os.write(fd, str(i).encode())
            fds.append(fd)
        rudisha fds

    eleza checkFDs(self, fds):
        # Check that the file descriptors kwenye the given list contain
        # their correct list indices kama ASCII numbers.
        kila n, fd kwenye enumerate(fds):
            os.lseek(fd, 0, os.SEEK_SET)
            self.assertEqual(os.read(fd, 1024), str(n).encode())

    eleza registerRecvmsgResult(self, result):
        self.addCleanup(self.closeRecvmsgFDs, result)

    eleza closeRecvmsgFDs(self, recvmsg_result):
        # Close all file descriptors specified kwenye the ancillary data
        # of the given rudisha value kutoka recvmsg() ama recvmsg_into().
        kila cmsg_level, cmsg_type, cmsg_data kwenye recvmsg_result[1]:
            ikiwa (cmsg_level == socket.SOL_SOCKET and
                    cmsg_type == socket.SCM_RIGHTS):
                fds = array.array("i")
                fds.kutokabytes(cmsg_data[:
                        len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
                kila fd kwenye fds:
                    os.close(fd)

    eleza createAndSendFDs(self, n):
        # Send n new file descriptors created by newFDs() to the
        # server, ukijumuisha the constant MSG kama the non-ancillary data.
        self.assertEqual(
            self.sendmsgToServer([MSG],
                                 [(socket.SOL_SOCKET,
                                   socket.SCM_RIGHTS,
                                   array.array("i", self.newFDs(n)))]),
            len(MSG))

    eleza checkRecvmsgFDs(self, numfds, result, maxcmsgs=1, ignoreflags=0):
        # Check that constant MSG was received ukijumuisha numfds file
        # descriptors kwenye a maximum of maxcmsgs control messages (which
        # must contain only complete integers).  By default, check
        # that MSG_CTRUNC ni unset, but ignore any flags in
        # ignoreflags.
        msg, ancdata, flags, addr = result
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, checkunset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

        self.assertIsInstance(ancdata, list)
        self.assertLessEqual(len(ancdata), maxcmsgs)
        fds = array.array("i")
        kila item kwenye ancdata:
            self.assertIsInstance(item, tuple)
            cmsg_level, cmsg_type, cmsg_data = item
            self.assertEqual(cmsg_level, socket.SOL_SOCKET)
            self.assertEqual(cmsg_type, socket.SCM_RIGHTS)
            self.assertIsInstance(cmsg_data, bytes)
            self.assertEqual(len(cmsg_data) % SIZEOF_INT, 0)
            fds.kutokabytes(cmsg_data)

        self.assertEqual(len(fds), numfds)
        self.checkFDs(fds)

    eleza testFDPassSimple(self):
        # Pass a single FD (array read kutoka bytes object).
        self.checkRecvmsgFDs(1, self.doRecvmsg(self.serv_sock,
                                               len(MSG), 10240))

    eleza _testFDPassSimple(self):
        self.assertEqual(
            self.sendmsgToServer(
                [MSG],
                [(socket.SOL_SOCKET,
                  socket.SCM_RIGHTS,
                  array.array("i", self.newFDs(1)).tobytes())]),
            len(MSG))

    eleza testMultipleFDPass(self):
        # Pass multiple FDs kwenye a single array.
        self.checkRecvmsgFDs(4, self.doRecvmsg(self.serv_sock,
                                               len(MSG), 10240))

    eleza _testMultipleFDPass(self):
        self.createAndSendFDs(4)

    @requireAttrs(socket, "CMSG_SPACE")
    eleza testFDPassCMSG_SPACE(self):
        # Test using CMSG_SPACE() to calculate ancillary buffer size.
        self.checkRecvmsgFDs(
            4, self.doRecvmsg(self.serv_sock, len(MSG),
                              socket.CMSG_SPACE(4 * SIZEOF_INT)))

    @testFDPassCMSG_SPACE.client_skip
    eleza _testFDPassCMSG_SPACE(self):
        self.createAndSendFDs(4)

    eleza testFDPassCMSG_LEN(self):
        # Test using CMSG_LEN() to calculate ancillary buffer size.
        self.checkRecvmsgFDs(1,
                             self.doRecvmsg(self.serv_sock, len(MSG),
                                            socket.CMSG_LEN(4 * SIZEOF_INT)),
                             # RFC 3542 says implementations may set
                             # MSG_CTRUNC ikiwa there isn't enough space
                             # kila trailing padding.
                             ignoreflags=socket.MSG_CTRUNC)

    eleza _testFDPassCMSG_LEN(self):
        self.createAndSendFDs(1)

    @unittest.skipIf(sys.platform == "darwin", "skipping, see issue #12958")
    @unittest.skipIf(AIX, "skipping, see issue #22397")
    @requireAttrs(socket, "CMSG_SPACE")
    eleza testFDPassSeparate(self):
        # Pass two FDs kwenye two separate arrays.  Arrays may be combined
        # into a single control message by the OS.
        self.checkRecvmsgFDs(2,
                             self.doRecvmsg(self.serv_sock, len(MSG), 10240),
                             maxcmsgs=2)

    @testFDPassSeparate.client_skip
    @unittest.skipIf(sys.platform == "darwin", "skipping, see issue #12958")
    @unittest.skipIf(AIX, "skipping, see issue #22397")
    eleza _testFDPassSeparate(self):
        fd0, fd1 = self.newFDs(2)
        self.assertEqual(
            self.sendmsgToServer([MSG], [(socket.SOL_SOCKET,
                                          socket.SCM_RIGHTS,
                                          array.array("i", [fd0])),
                                         (socket.SOL_SOCKET,
                                          socket.SCM_RIGHTS,
                                          array.array("i", [fd1]))]),
            len(MSG))

    @unittest.skipIf(sys.platform == "darwin", "skipping, see issue #12958")
    @unittest.skipIf(AIX, "skipping, see issue #22397")
    @requireAttrs(socket, "CMSG_SPACE")
    eleza testFDPassSeparateMinSpace(self):
        # Pass two FDs kwenye two separate arrays, receiving them into the
        # minimum space kila two arrays.
        num_fds = 2
        self.checkRecvmsgFDs(num_fds,
                             self.doRecvmsg(self.serv_sock, len(MSG),
                                            socket.CMSG_SPACE(SIZEOF_INT) +
                                            socket.CMSG_LEN(SIZEOF_INT * num_fds)),
                             maxcmsgs=2, ignoreflags=socket.MSG_CTRUNC)

    @testFDPassSeparateMinSpace.client_skip
    @unittest.skipIf(sys.platform == "darwin", "skipping, see issue #12958")
    @unittest.skipIf(AIX, "skipping, see issue #22397")
    eleza _testFDPassSeparateMinSpace(self):
        fd0, fd1 = self.newFDs(2)
        self.assertEqual(
            self.sendmsgToServer([MSG], [(socket.SOL_SOCKET,
                                          socket.SCM_RIGHTS,
                                          array.array("i", [fd0])),
                                         (socket.SOL_SOCKET,
                                          socket.SCM_RIGHTS,
                                          array.array("i", [fd1]))]),
            len(MSG))

    eleza sendAncillaryIfPossible(self, msg, ancdata):
        # Try to send msg na ancdata to server, but ikiwa the system
        # call fails, just send msg ukijumuisha no ancillary data.
        jaribu:
            nbytes = self.sendmsgToServer([msg], ancdata)
        tatizo OSError kama e:
            # Check that it was the system call that failed
            self.assertIsInstance(e.errno, int)
            nbytes = self.sendmsgToServer([msg])
        self.assertEqual(nbytes, len(msg))

    @unittest.skipIf(sys.platform == "darwin", "see issue #24725")
    eleza testFDPassEmpty(self):
        # Try to pita an empty FD array.  Can receive either no array
        # ama an empty array.
        self.checkRecvmsgFDs(0, self.doRecvmsg(self.serv_sock,
                                               len(MSG), 10240),
                             ignoreflags=socket.MSG_CTRUNC)

    eleza _testFDPassEmpty(self):
        self.sendAncillaryIfPossible(MSG, [(socket.SOL_SOCKET,
                                            socket.SCM_RIGHTS,
                                            b"")])

    eleza testFDPassPartialInt(self):
        # Try to pita a truncated FD array.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 10240)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, ignore=socket.MSG_CTRUNC)
        self.assertLessEqual(len(ancdata), 1)
        kila cmsg_level, cmsg_type, cmsg_data kwenye ancdata:
            self.assertEqual(cmsg_level, socket.SOL_SOCKET)
            self.assertEqual(cmsg_type, socket.SCM_RIGHTS)
            self.assertLess(len(cmsg_data), SIZEOF_INT)

    eleza _testFDPassPartialInt(self):
        self.sendAncillaryIfPossible(
            MSG,
            [(socket.SOL_SOCKET,
              socket.SCM_RIGHTS,
              array.array("i", [self.badfd]).tobytes()[:-1])])

    @requireAttrs(socket, "CMSG_SPACE")
    eleza testFDPassPartialIntInMiddle(self):
        # Try to pita two FD arrays, the first of which ni truncated.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), 10240)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, ignore=socket.MSG_CTRUNC)
        self.assertLessEqual(len(ancdata), 2)
        fds = array.array("i")
        # Arrays may have been combined kwenye a single control message
        kila cmsg_level, cmsg_type, cmsg_data kwenye ancdata:
            self.assertEqual(cmsg_level, socket.SOL_SOCKET)
            self.assertEqual(cmsg_type, socket.SCM_RIGHTS)
            fds.kutokabytes(cmsg_data[:
                    len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
        self.assertLessEqual(len(fds), 2)
        self.checkFDs(fds)

    @testFDPassPartialIntInMiddle.client_skip
    eleza _testFDPassPartialIntInMiddle(self):
        fd0, fd1 = self.newFDs(2)
        self.sendAncillaryIfPossible(
            MSG,
            [(socket.SOL_SOCKET,
              socket.SCM_RIGHTS,
              array.array("i", [fd0, self.badfd]).tobytes()[:-1]),
             (socket.SOL_SOCKET,
              socket.SCM_RIGHTS,
              array.array("i", [fd1]))])

    eleza checkTruncatedHeader(self, result, ignoreflags=0):
        # Check that no ancillary data items are rudishaed when data is
        # truncated inside the cmsghdr structure.
        msg, ancdata, flags, addr = result
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli, checkset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

    eleza testCmsgTruncNoBufSize(self):
        # Check that no ancillary data ni received when no buffer size
        # ni specified.
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG)),
                                  # BSD seems to set MSG_CTRUNC only
                                  # ikiwa an item has been partially
                                  # received.
                                  ignoreflags=socket.MSG_CTRUNC)

    eleza _testCmsgTruncNoBufSize(self):
        self.createAndSendFDs(1)

    eleza testCmsgTrunc0(self):
        # Check that no ancillary data ni received when buffer size ni 0.
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG), 0),
                                  ignoreflags=socket.MSG_CTRUNC)

    eleza _testCmsgTrunc0(self):
        self.createAndSendFDs(1)

    # Check that no ancillary data ni rudishaed kila various non-zero
    # (but still too small) buffer sizes.

    eleza testCmsgTrunc1(self):
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG), 1))

    eleza _testCmsgTrunc1(self):
        self.createAndSendFDs(1)

    eleza testCmsgTrunc2Int(self):
        # The cmsghdr structure has at least three members, two of
        # which are ints, so we still shouldn't see any ancillary
        # data.
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG),
                                                 SIZEOF_INT * 2))

    eleza _testCmsgTrunc2Int(self):
        self.createAndSendFDs(1)

    eleza testCmsgTruncLen0Minus1(self):
        self.checkTruncatedHeader(self.doRecvmsg(self.serv_sock, len(MSG),
                                                 socket.CMSG_LEN(0) - 1))

    eleza _testCmsgTruncLen0Minus1(self):
        self.createAndSendFDs(1)

    # The following tests try to truncate the control message kwenye the
    # middle of the FD array.

    eleza checkTruncatedArray(self, ancbuf, maxdata, mindata=0):
        # Check that file descriptor data ni truncated to between
        # mindata na maxdata bytes when received ukijumuisha buffer size
        # ancbuf, na that any complete file descriptor numbers are
        # valid.
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), ancbuf)
        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, checkset=socket.MSG_CTRUNC)

        ikiwa mindata == 0 na ancdata == []:
            rudisha
        self.assertEqual(len(ancdata), 1)
        cmsg_level, cmsg_type, cmsg_data = ancdata[0]
        self.assertEqual(cmsg_level, socket.SOL_SOCKET)
        self.assertEqual(cmsg_type, socket.SCM_RIGHTS)
        self.assertGreaterEqual(len(cmsg_data), mindata)
        self.assertLessEqual(len(cmsg_data), maxdata)
        fds = array.array("i")
        fds.kutokabytes(cmsg_data[:
                len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
        self.checkFDs(fds)

    eleza testCmsgTruncLen0(self):
        self.checkTruncatedArray(ancbuf=socket.CMSG_LEN(0), maxdata=0)

    eleza _testCmsgTruncLen0(self):
        self.createAndSendFDs(1)

    eleza testCmsgTruncLen0Plus1(self):
        self.checkTruncatedArray(ancbuf=socket.CMSG_LEN(0) + 1, maxdata=1)

    eleza _testCmsgTruncLen0Plus1(self):
        self.createAndSendFDs(2)

    eleza testCmsgTruncLen1(self):
        self.checkTruncatedArray(ancbuf=socket.CMSG_LEN(SIZEOF_INT),
                                 maxdata=SIZEOF_INT)

    eleza _testCmsgTruncLen1(self):
        self.createAndSendFDs(2)

    eleza testCmsgTruncLen2Minus1(self):
        self.checkTruncatedArray(ancbuf=socket.CMSG_LEN(2 * SIZEOF_INT) - 1,
                                 maxdata=(2 * SIZEOF_INT) - 1)

    eleza _testCmsgTruncLen2Minus1(self):
        self.createAndSendFDs(2)


kundi RFC3542AncillaryTest(SendrecvmsgServerTimeoutBase):
    # Test sendmsg() na recvmsg[_into]() using the ancillary data
    # features of the RFC 3542 Advanced Sockets API kila IPv6.
    # Currently we can only handle certain data items (e.g. traffic
    # class, hop limit, MTU discovery na fragmentation settings)
    # without resorting to unportable means such kama the struct module,
    # but the tests here are aimed at testing the ancillary data
    # handling kwenye sendmsg() na recvmsg() rather than the IPv6 API
    # itself.

    # Test value to use when setting hop limit of packet
    hop_limit = 2

    # Test value to use when setting traffic kundi of packet.
    # -1 means "use kernel default".
    traffic_kundi = -1

    eleza ancillaryMapping(self, ancdata):
        # Given ancillary data list ancdata, rudisha a mapping kutoka
        # pairs (cmsg_level, cmsg_type) to corresponding cmsg_data.
        # Check that no (level, type) pair appears more than once.
        d = {}
        kila cmsg_level, cmsg_type, cmsg_data kwenye ancdata:
            self.assertNotIn((cmsg_level, cmsg_type), d)
            d[(cmsg_level, cmsg_type)] = cmsg_data
        rudisha d

    eleza checkHopLimit(self, ancbufsize, maxhop=255, ignoreflags=0):
        # Receive hop limit into ancbufsize bytes of ancillary data
        # space.  Check that data ni MSG, ancillary data ni not
        # truncated (but ignore any flags kwenye ignoreflags), na hop
        # limit ni between 0 na maxhop inclusive.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), ancbufsize)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, checkunset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

        self.assertEqual(len(ancdata), 1)
        self.assertIsInstance(ancdata[0], tuple)
        cmsg_level, cmsg_type, cmsg_data = ancdata[0]
        self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
        self.assertEqual(cmsg_type, socket.IPV6_HOPLIMIT)
        self.assertIsInstance(cmsg_data, bytes)
        self.assertEqual(len(cmsg_data), SIZEOF_INT)
        a = array.array("i")
        a.kutokabytes(cmsg_data)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], maxhop)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testRecvHopLimit(self):
        # Test receiving the packet hop limit kama ancillary data.
        self.checkHopLimit(ancbufsize=10240)

    @testRecvHopLimit.client_skip
    eleza _testRecvHopLimit(self):
        # Need to wait until server has asked to receive ancillary
        # data, kama implementations are sio required to buffer it
        # otherwise.
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testRecvHopLimitCMSG_SPACE(self):
        # Test receiving hop limit, using CMSG_SPACE to calculate buffer size.
        self.checkHopLimit(ancbufsize=socket.CMSG_SPACE(SIZEOF_INT))

    @testRecvHopLimitCMSG_SPACE.client_skip
    eleza _testRecvHopLimitCMSG_SPACE(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    # Could test receiving into buffer sized using CMSG_LEN, but RFC
    # 3542 says portable applications must provide space kila trailing
    # padding.  Implementations may set MSG_CTRUNC ikiwa there isn't
    # enough space kila the padding.

    @requireAttrs(socket.socket, "sendmsg")
    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testSetHopLimit(self):
        # Test setting hop limit on outgoing packet na receiving it
        # at the other end.
        self.checkHopLimit(ancbufsize=10240, maxhop=self.hop_limit)

    @testSetHopLimit.client_skip
    eleza _testSetHopLimit(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.assertEqual(
            self.sendmsgToServer([MSG],
                                 [(socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT,
                                   array.array("i", [self.hop_limit]))]),
            len(MSG))

    eleza checkTrafficClassAndHopLimit(self, ancbufsize, maxhop=255,
                                     ignoreflags=0):
        # Receive traffic kundi na hop limit into ancbufsize bytes of
        # ancillary data space.  Check that data ni MSG, ancillary
        # data ni sio truncated (but ignore any flags kwenye ignoreflags),
        # na traffic kundi na hop limit are kwenye range (hop limit no
        # more than maxhop).
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVTCLASS, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), ancbufsize)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, checkunset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)
        self.assertEqual(len(ancdata), 2)
        ancmap = self.ancillaryMapping(ancdata)

        tcdata = ancmap[(socket.IPPROTO_IPV6, socket.IPV6_TCLASS)]
        self.assertEqual(len(tcdata), SIZEOF_INT)
        a = array.array("i")
        a.kutokabytes(tcdata)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], 255)

        hldata = ancmap[(socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT)]
        self.assertEqual(len(hldata), SIZEOF_INT)
        a = array.array("i")
        a.kutokabytes(hldata)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], maxhop)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testRecvTrafficClassAndHopLimit(self):
        # Test receiving traffic kundi na hop limit kama ancillary data.
        self.checkTrafficClassAndHopLimit(ancbufsize=10240)

    @testRecvTrafficClassAndHopLimit.client_skip
    eleza _testRecvTrafficClassAndHopLimit(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testRecvTrafficClassAndHopLimitCMSG_SPACE(self):
        # Test receiving traffic kundi na hop limit, using
        # CMSG_SPACE() to calculate buffer size.
        self.checkTrafficClassAndHopLimit(
            ancbufsize=socket.CMSG_SPACE(SIZEOF_INT) * 2)

    @testRecvTrafficClassAndHopLimitCMSG_SPACE.client_skip
    eleza _testRecvTrafficClassAndHopLimitCMSG_SPACE(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket.socket, "sendmsg")
    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testSetTrafficClassAndHopLimit(self):
        # Test setting traffic kundi na hop limit on outgoing packet,
        # na receiving them at the other end.
        self.checkTrafficClassAndHopLimit(ancbufsize=10240,
                                          maxhop=self.hop_limit)

    @testSetTrafficClassAndHopLimit.client_skip
    eleza _testSetTrafficClassAndHopLimit(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.assertEqual(
            self.sendmsgToServer([MSG],
                                 [(socket.IPPROTO_IPV6, socket.IPV6_TCLASS,
                                   array.array("i", [self.traffic_class])),
                                  (socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT,
                                   array.array("i", [self.hop_limit]))]),
            len(MSG))

    @requireAttrs(socket.socket, "sendmsg")
    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testOddCmsgSize(self):
        # Try to send ancillary data ukijumuisha first item one byte too
        # long.  Fall back to sending ukijumuisha correct size ikiwa this fails,
        # na check that second item was handled correctly.
        self.checkTrafficClassAndHopLimit(ancbufsize=10240,
                                          maxhop=self.hop_limit)

    @testOddCmsgSize.client_skip
    eleza _testOddCmsgSize(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        jaribu:
            nbytes = self.sendmsgToServer(
                [MSG],
                [(socket.IPPROTO_IPV6, socket.IPV6_TCLASS,
                  array.array("i", [self.traffic_class]).tobytes() + b"\x00"),
                 (socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT,
                  array.array("i", [self.hop_limit]))])
        tatizo OSError kama e:
            self.assertIsInstance(e.errno, int)
            nbytes = self.sendmsgToServer(
                [MSG],
                [(socket.IPPROTO_IPV6, socket.IPV6_TCLASS,
                  array.array("i", [self.traffic_class])),
                 (socket.IPPROTO_IPV6, socket.IPV6_HOPLIMIT,
                  array.array("i", [self.hop_limit]))])
            self.assertEqual(nbytes, len(MSG))

    # Tests kila proper handling of truncated ancillary data

    eleza checkHopLimitTruncatedHeader(self, ancbufsize, ignoreflags=0):
        # Receive hop limit into ancbufsize bytes of ancillary data
        # space, which should be too small to contain the ancillary
        # data header (ikiwa ancbufsize ni Tupu, pita no second argument
        # to recvmsg()).  Check that data ni MSG, MSG_CTRUNC ni set
        # (unless included kwenye ignoreflags), na no ancillary data is
        # rudishaed.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.misc_event.set()
        args = () ikiwa ancbufsize ni Tupu isipokua (ancbufsize,)
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), *args)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.assertEqual(ancdata, [])
        self.checkFlags(flags, eor=Kweli, checkset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testCmsgTruncNoBufSize(self):
        # Check that no ancillary data ni received when no ancillary
        # buffer size ni provided.
        self.checkHopLimitTruncatedHeader(ancbufsize=Tupu,
                                          # BSD seems to set
                                          # MSG_CTRUNC only ikiwa an item
                                          # has been partially
                                          # received.
                                          ignoreflags=socket.MSG_CTRUNC)

    @testCmsgTruncNoBufSize.client_skip
    eleza _testCmsgTruncNoBufSize(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testSingleCmsgTrunc0(self):
        # Check that no ancillary data ni received when ancillary
        # buffer size ni zero.
        self.checkHopLimitTruncatedHeader(ancbufsize=0,
                                          ignoreflags=socket.MSG_CTRUNC)

    @testSingleCmsgTrunc0.client_skip
    eleza _testSingleCmsgTrunc0(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    # Check that no ancillary data ni rudishaed kila various non-zero
    # (but still too small) buffer sizes.

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testSingleCmsgTrunc1(self):
        self.checkHopLimitTruncatedHeader(ancbufsize=1)

    @testSingleCmsgTrunc1.client_skip
    eleza _testSingleCmsgTrunc1(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testSingleCmsgTrunc2Int(self):
        self.checkHopLimitTruncatedHeader(ancbufsize=2 * SIZEOF_INT)

    @testSingleCmsgTrunc2Int.client_skip
    eleza _testSingleCmsgTrunc2Int(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testSingleCmsgTruncLen0Minus1(self):
        self.checkHopLimitTruncatedHeader(ancbufsize=socket.CMSG_LEN(0) - 1)

    @testSingleCmsgTruncLen0Minus1.client_skip
    eleza _testSingleCmsgTruncLen0Minus1(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT")
    eleza testSingleCmsgTruncInData(self):
        # Test truncation of a control message inside its associated
        # data.  The message may be rudishaed ukijumuisha its data truncated,
        # ama sio rudishaed at all.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(
            self.serv_sock, len(MSG), socket.CMSG_LEN(SIZEOF_INT) - 1)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, checkset=socket.MSG_CTRUNC)

        self.assertLessEqual(len(ancdata), 1)
        ikiwa ancdata:
            cmsg_level, cmsg_type, cmsg_data = ancdata[0]
            self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
            self.assertEqual(cmsg_type, socket.IPV6_HOPLIMIT)
            self.assertLess(len(cmsg_data), SIZEOF_INT)

    @testSingleCmsgTruncInData.client_skip
    eleza _testSingleCmsgTruncInData(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    eleza checkTruncatedSecondHeader(self, ancbufsize, ignoreflags=0):
        # Receive traffic kundi na hop limit into ancbufsize bytes of
        # ancillary data space, which should be large enough to
        # contain the first item, but too small to contain the header
        # of the second.  Check that data ni MSG, MSG_CTRUNC ni set
        # (unless included kwenye ignoreflags), na only one ancillary
        # data item ni rudishaed.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVTCLASS, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(self.serv_sock,
                                                   len(MSG), ancbufsize)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, checkset=socket.MSG_CTRUNC,
                        ignore=ignoreflags)

        self.assertEqual(len(ancdata), 1)
        cmsg_level, cmsg_type, cmsg_data = ancdata[0]
        self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
        self.assertIn(cmsg_type, {socket.IPV6_TCLASS, socket.IPV6_HOPLIMIT})
        self.assertEqual(len(cmsg_data), SIZEOF_INT)
        a = array.array("i")
        a.kutokabytes(cmsg_data)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], 255)

    # Try the above test ukijumuisha various buffer sizes.

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testSecondCmsgTrunc0(self):
        self.checkTruncatedSecondHeader(socket.CMSG_SPACE(SIZEOF_INT),
                                        ignoreflags=socket.MSG_CTRUNC)

    @testSecondCmsgTrunc0.client_skip
    eleza _testSecondCmsgTrunc0(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testSecondCmsgTrunc1(self):
        self.checkTruncatedSecondHeader(socket.CMSG_SPACE(SIZEOF_INT) + 1)

    @testSecondCmsgTrunc1.client_skip
    eleza _testSecondCmsgTrunc1(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testSecondCmsgTrunc2Int(self):
        self.checkTruncatedSecondHeader(socket.CMSG_SPACE(SIZEOF_INT) +
                                        2 * SIZEOF_INT)

    @testSecondCmsgTrunc2Int.client_skip
    eleza _testSecondCmsgTrunc2Int(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testSecondCmsgTruncLen0Minus1(self):
        self.checkTruncatedSecondHeader(socket.CMSG_SPACE(SIZEOF_INT) +
                                        socket.CMSG_LEN(0) - 1)

    @testSecondCmsgTruncLen0Minus1.client_skip
    eleza _testSecondCmsgTruncLen0Minus1(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)

    @requireAttrs(socket, "CMSG_SPACE", "IPV6_RECVHOPLIMIT", "IPV6_HOPLIMIT",
                  "IPV6_RECVTCLASS", "IPV6_TCLASS")
    eleza testSecomdCmsgTruncInData(self):
        # Test truncation of the second of two control messages inside
        # its associated data.
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVHOPLIMIT, 1)
        self.serv_sock.setsockopt(socket.IPPROTO_IPV6,
                                  socket.IPV6_RECVTCLASS, 1)
        self.misc_event.set()
        msg, ancdata, flags, addr = self.doRecvmsg(
            self.serv_sock, len(MSG),
            socket.CMSG_SPACE(SIZEOF_INT) + socket.CMSG_LEN(SIZEOF_INT) - 1)

        self.assertEqual(msg, MSG)
        self.checkRecvmsgAddress(addr, self.cli_addr)
        self.checkFlags(flags, eor=Kweli, checkset=socket.MSG_CTRUNC)

        cmsg_types = {socket.IPV6_TCLASS, socket.IPV6_HOPLIMIT}

        cmsg_level, cmsg_type, cmsg_data = ancdata.pop(0)
        self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
        cmsg_types.remove(cmsg_type)
        self.assertEqual(len(cmsg_data), SIZEOF_INT)
        a = array.array("i")
        a.kutokabytes(cmsg_data)
        self.assertGreaterEqual(a[0], 0)
        self.assertLessEqual(a[0], 255)

        ikiwa ancdata:
            cmsg_level, cmsg_type, cmsg_data = ancdata.pop(0)
            self.assertEqual(cmsg_level, socket.IPPROTO_IPV6)
            cmsg_types.remove(cmsg_type)
            self.assertLess(len(cmsg_data), SIZEOF_INT)

        self.assertEqual(ancdata, [])

    @testSecomdCmsgTruncInData.client_skip
    eleza _testSecomdCmsgTruncInData(self):
        self.assertKweli(self.misc_event.wait(timeout=self.fail_timeout))
        self.sendToServer(MSG)


# Derive concrete test classes kila different socket types.

kundi SendrecvmsgUDPTestBase(SendrecvmsgDgramFlagsBase,
                             SendrecvmsgConnectionlessBase,
                             ThreadedSocketTestMixin, UDPTestBase):
    pita

@requireAttrs(socket.socket, "sendmsg")
kundi SendmsgUDPTest(SendmsgConnectionlessTests, SendrecvmsgUDPTestBase):
    pita

@requireAttrs(socket.socket, "recvmsg")
kundi RecvmsgUDPTest(RecvmsgTests, SendrecvmsgUDPTestBase):
    pita

@requireAttrs(socket.socket, "recvmsg_into")
kundi RecvmsgIntoUDPTest(RecvmsgIntoTests, SendrecvmsgUDPTestBase):
    pita


kundi SendrecvmsgUDP6TestBase(SendrecvmsgDgramFlagsBase,
                              SendrecvmsgConnectionlessBase,
                              ThreadedSocketTestMixin, UDP6TestBase):

    eleza checkRecvmsgAddress(self, addr1, addr2):
        # Called to compare the received address ukijumuisha the address of
        # the peer, ignoring scope ID
        self.assertEqual(addr1[:-1], addr2[:-1])

@requireAttrs(socket.socket, "sendmsg")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
@requireSocket("AF_INET6", "SOCK_DGRAM")
kundi SendmsgUDP6Test(SendmsgConnectionlessTests, SendrecvmsgUDP6TestBase):
    pita

@requireAttrs(socket.socket, "recvmsg")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
@requireSocket("AF_INET6", "SOCK_DGRAM")
kundi RecvmsgUDP6Test(RecvmsgTests, SendrecvmsgUDP6TestBase):
    pita

@requireAttrs(socket.socket, "recvmsg_into")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
@requireSocket("AF_INET6", "SOCK_DGRAM")
kundi RecvmsgIntoUDP6Test(RecvmsgIntoTests, SendrecvmsgUDP6TestBase):
    pita

@requireAttrs(socket.socket, "recvmsg")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
@requireAttrs(socket, "IPPROTO_IPV6")
@requireSocket("AF_INET6", "SOCK_DGRAM")
kundi RecvmsgRFC3542AncillaryUDP6Test(RFC3542AncillaryTest,
                                      SendrecvmsgUDP6TestBase):
    pita

@requireAttrs(socket.socket, "recvmsg_into")
@unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test.')
@requireAttrs(socket, "IPPROTO_IPV6")
@requireSocket("AF_INET6", "SOCK_DGRAM")
kundi RecvmsgIntoRFC3542AncillaryUDP6Test(RecvmsgIntoMixin,
                                          RFC3542AncillaryTest,
                                          SendrecvmsgUDP6TestBase):
    pita


kundi SendrecvmsgTCPTestBase(SendrecvmsgConnectedBase,
                             ConnectedStreamTestMixin, TCPTestBase):
    pita

@requireAttrs(socket.socket, "sendmsg")
kundi SendmsgTCPTest(SendmsgStreamTests, SendrecvmsgTCPTestBase):
    pita

@requireAttrs(socket.socket, "recvmsg")
kundi RecvmsgTCPTest(RecvmsgTests, RecvmsgGenericStreamTests,
                     SendrecvmsgTCPTestBase):
    pita

@requireAttrs(socket.socket, "recvmsg_into")
kundi RecvmsgIntoTCPTest(RecvmsgIntoTests, RecvmsgGenericStreamTests,
                         SendrecvmsgTCPTestBase):
    pita


kundi SendrecvmsgSCTPStreamTestBase(SendrecvmsgSCTPFlagsBase,
                                    SendrecvmsgConnectedBase,
                                    ConnectedStreamTestMixin, SCTPStreamBase):
    pita

@requireAttrs(socket.socket, "sendmsg")
@unittest.skipIf(AIX, "IPPROTO_SCTP: [Errno 62] Protocol sio supported on AIX")
@requireSocket("AF_INET", "SOCK_STREAM", "IPPROTO_SCTP")
kundi SendmsgSCTPStreamTest(SendmsgStreamTests, SendrecvmsgSCTPStreamTestBase):
    pita

@requireAttrs(socket.socket, "recvmsg")
@unittest.skipIf(AIX, "IPPROTO_SCTP: [Errno 62] Protocol sio supported on AIX")
@requireSocket("AF_INET", "SOCK_STREAM", "IPPROTO_SCTP")
kundi RecvmsgSCTPStreamTest(RecvmsgTests, RecvmsgGenericStreamTests,
                            SendrecvmsgSCTPStreamTestBase):

    eleza testRecvmsgEOF(self):
        jaribu:
            super(RecvmsgSCTPStreamTest, self).testRecvmsgEOF()
        tatizo OSError kama e:
            ikiwa e.errno != errno.ENOTCONN:
                ashiria
            self.skipTest("sporadic ENOTCONN (kernel issue?) - see issue #13876")

@requireAttrs(socket.socket, "recvmsg_into")
@unittest.skipIf(AIX, "IPPROTO_SCTP: [Errno 62] Protocol sio supported on AIX")
@requireSocket("AF_INET", "SOCK_STREAM", "IPPROTO_SCTP")
kundi RecvmsgIntoSCTPStreamTest(RecvmsgIntoTests, RecvmsgGenericStreamTests,
                                SendrecvmsgSCTPStreamTestBase):

    eleza testRecvmsgEOF(self):
        jaribu:
            super(RecvmsgIntoSCTPStreamTest, self).testRecvmsgEOF()
        tatizo OSError kama e:
            ikiwa e.errno != errno.ENOTCONN:
                ashiria
            self.skipTest("sporadic ENOTCONN (kernel issue?) - see issue #13876")


kundi SendrecvmsgUnixStreamTestBase(SendrecvmsgConnectedBase,
                                    ConnectedStreamTestMixin, UnixStreamBase):
    pita

@requireAttrs(socket.socket, "sendmsg")
@requireAttrs(socket, "AF_UNIX")
kundi SendmsgUnixStreamTest(SendmsgStreamTests, SendrecvmsgUnixStreamTestBase):
    pita

@requireAttrs(socket.socket, "recvmsg")
@requireAttrs(socket, "AF_UNIX")
kundi RecvmsgUnixStreamTest(RecvmsgTests, RecvmsgGenericStreamTests,
                            SendrecvmsgUnixStreamTestBase):
    pita

@requireAttrs(socket.socket, "recvmsg_into")
@requireAttrs(socket, "AF_UNIX")
kundi RecvmsgIntoUnixStreamTest(RecvmsgIntoTests, RecvmsgGenericStreamTests,
                                SendrecvmsgUnixStreamTestBase):
    pita

@requireAttrs(socket.socket, "sendmsg", "recvmsg")
@requireAttrs(socket, "AF_UNIX", "SOL_SOCKET", "SCM_RIGHTS")
kundi RecvmsgSCMRightsStreamTest(SCMRightsTest, SendrecvmsgUnixStreamTestBase):
    pita

@requireAttrs(socket.socket, "sendmsg", "recvmsg_into")
@requireAttrs(socket, "AF_UNIX", "SOL_SOCKET", "SCM_RIGHTS")
kundi RecvmsgIntoSCMRightsStreamTest(RecvmsgIntoMixin, SCMRightsTest,
                                     SendrecvmsgUnixStreamTestBase):
    pita


# Test interrupting the interruptible send/receive methods ukijumuisha a
# signal when a timeout ni set.  These tests avoid having multiple
# threads alive during the test so that the OS cannot deliver the
# signal to the wrong one.

kundi InterruptedTimeoutBase(unittest.TestCase):
    # Base kundi kila interrupted send/receive tests.  Installs an
    # empty handler kila SIGALRM na removes it on teardown, along with
    # any scheduled alarms.

    eleza setUp(self):
        super().setUp()
        orig_alrm_handler = signal.signal(signal.SIGALRM,
                                          lambda signum, frame: 1 / 0)
        self.addCleanup(signal.signal, signal.SIGALRM, orig_alrm_handler)

    # Timeout kila socket operations
    timeout = 4.0

    # Provide setAlarm() method to schedule delivery of SIGALRM after
    # given number of seconds, ama cancel it ikiwa zero, na an
    # appropriate time value to use.  Use setitimer() ikiwa available.
    ikiwa hasattr(signal, "setitimer"):
        alarm_time = 0.05

        eleza setAlarm(self, seconds):
            signal.setitimer(signal.ITIMER_REAL, seconds)
    isipokua:
        # Old systems may deliver the alarm up to one second early
        alarm_time = 2

        eleza setAlarm(self, seconds):
            signal.alarm(seconds)


# Require siginterrupt() kwenye order to ensure that system calls are
# interrupted by default.
@requireAttrs(signal, "siginterrupt")
@unittest.skipUnless(hasattr(signal, "alarm") ama hasattr(signal, "setitimer"),
                     "Don't have signal.alarm ama signal.setitimer")
kundi InterruptedRecvTimeoutTest(InterruptedTimeoutBase, UDPTestBase):
    # Test interrupting the recv*() methods ukijumuisha signals when a
    # timeout ni set.

    eleza setUp(self):
        super().setUp()
        self.serv.settimeout(self.timeout)

    eleza checkInterruptedRecv(self, func, *args, **kwargs):
        # Check that func(*args, **kwargs) ashirias
        # errno of EINTR when interrupted by a signal.
        jaribu:
            self.setAlarm(self.alarm_time)
            ukijumuisha self.assertRaises(ZeroDivisionError) kama cm:
                func(*args, **kwargs)
        mwishowe:
            self.setAlarm(0)

    eleza testInterruptedRecvTimeout(self):
        self.checkInterruptedRecv(self.serv.recv, 1024)

    eleza testInterruptedRecvIntoTimeout(self):
        self.checkInterruptedRecv(self.serv.recv_into, bytearray(1024))

    eleza testInterruptedRecvkutokaTimeout(self):
        self.checkInterruptedRecv(self.serv.recvkutoka, 1024)

    eleza testInterruptedRecvkutokaIntoTimeout(self):
        self.checkInterruptedRecv(self.serv.recvkutoka_into, bytearray(1024))

    @requireAttrs(socket.socket, "recvmsg")
    eleza testInterruptedRecvmsgTimeout(self):
        self.checkInterruptedRecv(self.serv.recvmsg, 1024)

    @requireAttrs(socket.socket, "recvmsg_into")
    eleza testInterruptedRecvmsgIntoTimeout(self):
        self.checkInterruptedRecv(self.serv.recvmsg_into, [bytearray(1024)])


# Require siginterrupt() kwenye order to ensure that system calls are
# interrupted by default.
@requireAttrs(signal, "siginterrupt")
@unittest.skipUnless(hasattr(signal, "alarm") ama hasattr(signal, "setitimer"),
                     "Don't have signal.alarm ama signal.setitimer")
kundi InterruptedSendTimeoutTest(InterruptedTimeoutBase,
                                 ThreadSafeCleanupTestCase,
                                 SocketListeningTestMixin, TCPTestBase):
    # Test interrupting the interruptible send*() methods ukijumuisha signals
    # when a timeout ni set.

    eleza setUp(self):
        super().setUp()
        self.serv_conn = self.newSocket()
        self.addCleanup(self.serv_conn.close)
        # Use a thread to complete the connection, but wait kila it to
        # terminate before running the test, so that there ni only one
        # thread to accept the signal.
        cli_thread = threading.Thread(target=self.doConnect)
        cli_thread.start()
        self.cli_conn, addr = self.serv.accept()
        self.addCleanup(self.cli_conn.close)
        cli_thread.join()
        self.serv_conn.settimeout(self.timeout)

    eleza doConnect(self):
        self.serv_conn.connect(self.serv_addr)

    eleza checkInterruptedSend(self, func, *args, **kwargs):
        # Check that func(*args, **kwargs), run kwenye a loop, ashirias
        # OSError ukijumuisha an errno of EINTR when interrupted by a
        # signal.
        jaribu:
            ukijumuisha self.assertRaises(ZeroDivisionError) kama cm:
                wakati Kweli:
                    self.setAlarm(self.alarm_time)
                    func(*args, **kwargs)
        mwishowe:
            self.setAlarm(0)

    # Issue #12958: The following tests have problems on OS X prior to 10.7
    @support.requires_mac_ver(10, 7)
    eleza testInterruptedSendTimeout(self):
        self.checkInterruptedSend(self.serv_conn.send, b"a"*512)

    @support.requires_mac_ver(10, 7)
    eleza testInterruptedSendtoTimeout(self):
        # Passing an actual address here kama Python's wrapper for
        # sendto() doesn't allow pitaing a zero-length one; POSIX
        # requires that the address ni ignored since the socket is
        # connection-mode, however.
        self.checkInterruptedSend(self.serv_conn.sendto, b"a"*512,
                                  self.serv_addr)

    @support.requires_mac_ver(10, 7)
    @requireAttrs(socket.socket, "sendmsg")
    eleza testInterruptedSendmsgTimeout(self):
        self.checkInterruptedSend(self.serv_conn.sendmsg, [b"a"*512])


kundi TCPCloserTest(ThreadedTCPSocketTest):

    eleza testClose(self):
        conn, addr = self.serv.accept()
        conn.close()

        sd = self.cli
        read, write, err = select.select([sd], [], [], 1.0)
        self.assertEqual(read, [sd])
        self.assertEqual(sd.recv(1), b'')

        # Calling close() many times should be safe.
        conn.close()
        conn.close()

    eleza _testClose(self):
        self.cli.connect((HOST, self.port))
        time.sleep(1.0)


kundi BasicSocketPairTest(SocketPairTest):

    eleza __init__(self, methodName='runTest'):
        SocketPairTest.__init__(self, methodName=methodName)

    eleza _check_defaults(self, sock):
        self.assertIsInstance(sock, socket.socket)
        ikiwa hasattr(socket, 'AF_UNIX'):
            self.assertEqual(sock.family, socket.AF_UNIX)
        isipokua:
            self.assertEqual(sock.family, socket.AF_INET)
        self.assertEqual(sock.type, socket.SOCK_STREAM)
        self.assertEqual(sock.proto, 0)

    eleza _testDefaults(self):
        self._check_defaults(self.cli)

    eleza testDefaults(self):
        self._check_defaults(self.serv)

    eleza testRecv(self):
        msg = self.serv.recv(1024)
        self.assertEqual(msg, MSG)

    eleza _testRecv(self):
        self.cli.send(MSG)

    eleza testSend(self):
        self.serv.send(MSG)

    eleza _testSend(self):
        msg = self.cli.recv(1024)
        self.assertEqual(msg, MSG)


kundi NonBlockingTCPTests(ThreadedTCPSocketTest):

    eleza __init__(self, methodName='runTest'):
        self.event = threading.Event()
        ThreadedTCPSocketTest.__init__(self, methodName=methodName)

    eleza assert_sock_timeout(self, sock, timeout):
        self.assertEqual(self.serv.gettimeout(), timeout)

        blocking = (timeout != 0.0)
        self.assertEqual(sock.getblocking(), blocking)

        ikiwa fcntl ni sio Tupu:
            # When a Python socket has a non-zero timeout, it's switched
            # internally to a non-blocking mode. Later, sock.sendall(),
            # sock.recv(), na other socket operations use a select() call and
            # handle EWOULDBLOCK/EGAIN on all socket operations. That's how
            # timeouts are enforced.
            fd_blocking = (timeout ni Tupu)

            flag = fcntl.fcntl(sock, fcntl.F_GETFL, os.O_NONBLOCK)
            self.assertEqual(not bool(flag & os.O_NONBLOCK), fd_blocking)

    eleza testSetBlocking(self):
        # Test setblocking() na settimeout() methods
        self.serv.setblocking(Kweli)
        self.assert_sock_timeout(self.serv, Tupu)

        self.serv.setblocking(Uongo)
        self.assert_sock_timeout(self.serv, 0.0)

        self.serv.settimeout(Tupu)
        self.assert_sock_timeout(self.serv, Tupu)

        self.serv.settimeout(0)
        self.assert_sock_timeout(self.serv, 0)

        self.serv.settimeout(10)
        self.assert_sock_timeout(self.serv, 10)

        self.serv.settimeout(0)
        self.assert_sock_timeout(self.serv, 0)

    eleza _testSetBlocking(self):
        pita

    @support.cpython_only
    eleza testSetBlocking_overflow(self):
        # Issue 15989
        agiza _testcapi
        ikiwa _testcapi.UINT_MAX >= _testcapi.ULONG_MAX:
            self.skipTest('needs UINT_MAX < ULONG_MAX')

        self.serv.setblocking(Uongo)
        self.assertEqual(self.serv.gettimeout(), 0.0)

        self.serv.setblocking(_testcapi.UINT_MAX + 1)
        self.assertIsTupu(self.serv.gettimeout())

    _testSetBlocking_overflow = support.cpython_only(_testSetBlocking)

    @unittest.skipUnless(hasattr(socket, 'SOCK_NONBLOCK'),
                         'test needs socket.SOCK_NONBLOCK')
    @support.requires_linux_version(2, 6, 28)
    eleza testInitNonBlocking(self):
        # create a socket ukijumuisha SOCK_NONBLOCK
        self.serv.close()
        self.serv = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        self.assert_sock_timeout(self.serv, 0)

    eleza _testInitNonBlocking(self):
        pita

    eleza testInheritFlagsBlocking(self):
        # bpo-7995: accept() on a listening socket ukijumuisha a timeout na the
        # default timeout ni Tupu, the resulting socket must be blocking.
        ukijumuisha socket_setdefaulttimeout(Tupu):
            self.serv.settimeout(10)
            conn, addr = self.serv.accept()
            self.addCleanup(conn.close)
            self.assertIsTupu(conn.gettimeout())

    eleza _testInheritFlagsBlocking(self):
        self.cli.connect((HOST, self.port))

    eleza testInheritFlagsTimeout(self):
        # bpo-7995: accept() on a listening socket ukijumuisha a timeout na the
        # default timeout ni Tupu, the resulting socket must inherit
        # the default timeout.
        default_timeout = 20.0
        ukijumuisha socket_setdefaulttimeout(default_timeout):
            self.serv.settimeout(10)
            conn, addr = self.serv.accept()
            self.addCleanup(conn.close)
            self.assertEqual(conn.gettimeout(), default_timeout)

    eleza _testInheritFlagsTimeout(self):
        self.cli.connect((HOST, self.port))

    eleza testAccept(self):
        # Testing non-blocking accept
        self.serv.setblocking(0)

        # connect() didn't start: non-blocking accept() fails
        start_time = time.monotonic()
        ukijumuisha self.assertRaises(BlockingIOError):
            conn, addr = self.serv.accept()
        dt = time.monotonic() - start_time
        self.assertLess(dt, 1.0)

        self.event.set()

        read, write, err = select.select([self.serv], [], [], MAIN_TIMEOUT)
        ikiwa self.serv haiko kwenye read:
            self.fail("Error trying to do accept after select.")

        # connect() completed: non-blocking accept() doesn't block
        conn, addr = self.serv.accept()
        self.addCleanup(conn.close)
        self.assertIsTupu(conn.gettimeout())

    eleza _testAccept(self):
        # don't connect before event ni set to check
        # that non-blocking accept() ashirias BlockingIOError
        self.event.wait()

        self.cli.connect((HOST, self.port))

    eleza testRecv(self):
        # Testing non-blocking recv
        conn, addr = self.serv.accept()
        self.addCleanup(conn.close)
        conn.setblocking(0)

        # the server didn't send data yet: non-blocking recv() fails
        ukijumuisha self.assertRaises(BlockingIOError):
            msg = conn.recv(len(MSG))

        self.event.set()

        read, write, err = select.select([conn], [], [], MAIN_TIMEOUT)
        ikiwa conn haiko kwenye read:
            self.fail("Error during select call to non-blocking socket.")

        # the server sent data yet: non-blocking recv() doesn't block
        msg = conn.recv(len(MSG))
        self.assertEqual(msg, MSG)

    eleza _testRecv(self):
        self.cli.connect((HOST, self.port))

        # don't send anything before event ni set to check
        # that non-blocking recv() ashirias BlockingIOError
        self.event.wait()

        # send data: recv() will no longer block
        self.cli.sendall(MSG)


kundi FileObjectClassTestCase(SocketConnectedTest):
    """Unit tests kila the object rudishaed by socket.makefile()

    self.read_file ni the io object rudishaed by makefile() on
    the client connection.  You can read kutoka this file to
    get output kutoka the server.

    self.write_file ni the io object rudishaed by makefile() on the
    server connection.  You can write to this file to send output
    to the client.
    """

    bufsize = -1 # Use default buffer size
    encoding = 'utf-8'
    errors = 'strict'
    newline = Tupu

    read_mode = 'rb'
    read_msg = MSG
    write_mode = 'wb'
    write_msg = MSG

    eleza __init__(self, methodName='runTest'):
        SocketConnectedTest.__init__(self, methodName=methodName)

    eleza setUp(self):
        self.evt1, self.evt2, self.serv_finished, self.cli_finished = [
            threading.Event() kila i kwenye range(4)]
        SocketConnectedTest.setUp(self)
        self.read_file = self.cli_conn.makefile(
            self.read_mode, self.bufsize,
            encoding = self.encoding,
            errors = self.errors,
            newline = self.newline)

    eleza tearDown(self):
        self.serv_finished.set()
        self.read_file.close()
        self.assertKweli(self.read_file.closed)
        self.read_file = Tupu
        SocketConnectedTest.tearDown(self)

    eleza clientSetUp(self):
        SocketConnectedTest.clientSetUp(self)
        self.write_file = self.serv_conn.makefile(
            self.write_mode, self.bufsize,
            encoding = self.encoding,
            errors = self.errors,
            newline = self.newline)

    eleza clientTearDown(self):
        self.cli_finished.set()
        self.write_file.close()
        self.assertKweli(self.write_file.closed)
        self.write_file = Tupu
        SocketConnectedTest.clientTearDown(self)

    eleza testReadAfterTimeout(self):
        # Issue #7322: A file object must disallow further reads
        # after a timeout has occurred.
        self.cli_conn.settimeout(1)
        self.read_file.read(3)
        # First read ashirias a timeout
        self.assertRaises(socket.timeout, self.read_file.read, 1)
        # Second read ni disallowed
        ukijumuisha self.assertRaises(OSError) kama ctx:
            self.read_file.read(1)
        self.assertIn("cannot read kutoka timed out object", str(ctx.exception))

    eleza _testReadAfterTimeout(self):
        self.write_file.write(self.write_msg[0:3])
        self.write_file.flush()
        self.serv_finished.wait()

    eleza testSmallRead(self):
        # Performing small file read test
        first_seg = self.read_file.read(len(self.read_msg)-3)
        second_seg = self.read_file.read(3)
        msg = first_seg + second_seg
        self.assertEqual(msg, self.read_msg)

    eleza _testSmallRead(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    eleza testFullRead(self):
        # read until EOF
        msg = self.read_file.read()
        self.assertEqual(msg, self.read_msg)

    eleza _testFullRead(self):
        self.write_file.write(self.write_msg)
        self.write_file.close()

    eleza testUnbufferedRead(self):
        # Performing unbuffered file read test
        buf = type(self.read_msg)()
        wakati 1:
            char = self.read_file.read(1)
            ikiwa sio char:
                koma
            buf += char
        self.assertEqual(buf, self.read_msg)

    eleza _testUnbufferedRead(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    eleza testReadline(self):
        # Performing file readline test
        line = self.read_file.readline()
        self.assertEqual(line, self.read_msg)

    eleza _testReadline(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    eleza testCloseAfterMakefile(self):
        # The file rudishaed by makefile should keep the socket open.
        self.cli_conn.close()
        # read until EOF
        msg = self.read_file.read()
        self.assertEqual(msg, self.read_msg)

    eleza _testCloseAfterMakefile(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    eleza testMakefileAfterMakefileClose(self):
        self.read_file.close()
        msg = self.cli_conn.recv(len(MSG))
        ikiwa isinstance(self.read_msg, str):
            msg = msg.decode()
        self.assertEqual(msg, self.read_msg)

    eleza _testMakefileAfterMakefileClose(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    eleza testClosedAttr(self):
        self.assertKweli(not self.read_file.closed)

    eleza _testClosedAttr(self):
        self.assertKweli(not self.write_file.closed)

    eleza testAttributes(self):
        self.assertEqual(self.read_file.mode, self.read_mode)
        self.assertEqual(self.read_file.name, self.cli_conn.fileno())

    eleza _testAttributes(self):
        self.assertEqual(self.write_file.mode, self.write_mode)
        self.assertEqual(self.write_file.name, self.serv_conn.fileno())

    eleza testRealClose(self):
        self.read_file.close()
        self.assertRaises(ValueError, self.read_file.fileno)
        self.cli_conn.close()
        self.assertRaises(OSError, self.cli_conn.getsockname)

    eleza _testRealClose(self):
        pita


kundi UnbufferedFileObjectClassTestCase(FileObjectClassTestCase):

    """Repeat the tests kutoka FileObjectClassTestCase ukijumuisha bufsize==0.

    In this case (and kwenye this case only), it should be possible to
    create a file object, read a line kutoka it, create another file
    object, read another line kutoka it, without loss of data kwenye the
    first file object's buffer.  Note that http.client relies on this
    when reading multiple requests kutoka the same socket."""

    bufsize = 0 # Use unbuffered mode

    eleza testUnbufferedReadline(self):
        # Read a line, create a new file object, read another line ukijumuisha it
        line = self.read_file.readline() # first line
        self.assertEqual(line, b"A. " + self.write_msg) # first line
        self.read_file = self.cli_conn.makefile('rb', 0)
        line = self.read_file.readline() # second line
        self.assertEqual(line, b"B. " + self.write_msg) # second line

    eleza _testUnbufferedReadline(self):
        self.write_file.write(b"A. " + self.write_msg)
        self.write_file.write(b"B. " + self.write_msg)
        self.write_file.flush()

    eleza testMakefileClose(self):
        # The file rudishaed by makefile should keep the socket open...
        self.cli_conn.close()
        msg = self.cli_conn.recv(1024)
        self.assertEqual(msg, self.read_msg)
        # ...until the file ni itself closed
        self.read_file.close()
        self.assertRaises(OSError, self.cli_conn.recv, 1024)

    eleza _testMakefileClose(self):
        self.write_file.write(self.write_msg)
        self.write_file.flush()

    eleza testMakefileCloseSocketDestroy(self):
        refcount_before = sys.getrefcount(self.cli_conn)
        self.read_file.close()
        refcount_after = sys.getrefcount(self.cli_conn)
        self.assertEqual(refcount_before - 1, refcount_after)

    eleza _testMakefileCloseSocketDestroy(self):
        pita

    # Non-blocking ops
    # NOTE: to set `read_file` kama non-blocking, we must call
    # `cli_conn.setblocking` na vice-versa (see setUp / clientSetUp).

    eleza testSmallReadNonBlocking(self):
        self.cli_conn.setblocking(Uongo)
        self.assertEqual(self.read_file.readinto(bytearray(10)), Tupu)
        self.assertEqual(self.read_file.read(len(self.read_msg) - 3), Tupu)
        self.evt1.set()
        self.evt2.wait(1.0)
        first_seg = self.read_file.read(len(self.read_msg) - 3)
        ikiwa first_seg ni Tupu:
            # Data sio arrived (can happen under Windows), wait a bit
            time.sleep(0.5)
            first_seg = self.read_file.read(len(self.read_msg) - 3)
        buf = bytearray(10)
        n = self.read_file.readinto(buf)
        self.assertEqual(n, 3)
        msg = first_seg + buf[:n]
        self.assertEqual(msg, self.read_msg)
        self.assertEqual(self.read_file.readinto(bytearray(16)), Tupu)
        self.assertEqual(self.read_file.read(1), Tupu)

    eleza _testSmallReadNonBlocking(self):
        self.evt1.wait(1.0)
        self.write_file.write(self.write_msg)
        self.write_file.flush()
        self.evt2.set()
        # Avoid closing the socket before the server test has finished,
        # otherwise system recv() will rudisha 0 instead of EWOULDBLOCK.
        self.serv_finished.wait(5.0)

    eleza testWriteNonBlocking(self):
        self.cli_finished.wait(5.0)
        # The client thread can't skip directly - the SkipTest exception
        # would appear kama a failure.
        ikiwa self.serv_skipped:
            self.skipTest(self.serv_skipped)

    eleza _testWriteNonBlocking(self):
        self.serv_skipped = Tupu
        self.serv_conn.setblocking(Uongo)
        # Try to saturate the socket buffer pipe ukijumuisha repeated large writes.
        BIG = b"x" * support.SOCK_MAX_SIZE
        LIMIT = 10
        # The first write() succeeds since a chunk of data can be buffered
        n = self.write_file.write(BIG)
        self.assertGreater(n, 0)
        kila i kwenye range(LIMIT):
            n = self.write_file.write(BIG)
            ikiwa n ni Tupu:
                # Succeeded
                koma
            self.assertGreater(n, 0)
        isipokua:
            # Let us know that this test didn't manage to establish
            # the expected conditions. This ni sio a failure kwenye itself but,
            # ikiwa it happens repeatedly, the test should be fixed.
            self.serv_skipped = "failed to saturate the socket buffer"


kundi LineBufferedFileObjectClassTestCase(FileObjectClassTestCase):

    bufsize = 1 # Default-buffered kila reading; line-buffered kila writing


kundi SmallBufferedFileObjectClassTestCase(FileObjectClassTestCase):

    bufsize = 2 # Exercise the buffering code


kundi UnicodeReadFileObjectClassTestCase(FileObjectClassTestCase):
    """Tests kila socket.makefile() kwenye text mode (rather than binary)"""

    read_mode = 'r'
    read_msg = MSG.decode('utf-8')
    write_mode = 'wb'
    write_msg = MSG
    newline = ''


kundi UnicodeWriteFileObjectClassTestCase(FileObjectClassTestCase):
    """Tests kila socket.makefile() kwenye text mode (rather than binary)"""

    read_mode = 'rb'
    read_msg = MSG
    write_mode = 'w'
    write_msg = MSG.decode('utf-8')
    newline = ''


kundi UnicodeReadWriteFileObjectClassTestCase(FileObjectClassTestCase):
    """Tests kila socket.makefile() kwenye text mode (rather than binary)"""

    read_mode = 'r'
    read_msg = MSG.decode('utf-8')
    write_mode = 'w'
    write_msg = MSG.decode('utf-8')
    newline = ''


kundi NetworkConnectionTest(object):
    """Prove network connection."""

    eleza clientSetUp(self):
        # We're inherited below by BasicTCPTest2, which also inherits
        # BasicTCPTest, which defines self.port referenced below.
        self.cli = socket.create_connection((HOST, self.port))
        self.serv_conn = self.cli

kundi BasicTCPTest2(NetworkConnectionTest, BasicTCPTest):
    """Tests that NetworkConnection does sio koma existing TCP functionality.
    """

kundi NetworkConnectionNoServer(unittest.TestCase):

    kundi MockSocket(socket.socket):
        eleza connect(self, *args):
            ashiria socket.timeout('timed out')

    @contextlib.contextmanager
    eleza mocked_socket_module(self):
        """Return a socket which times out on connect"""
        old_socket = socket.socket
        socket.socket = self.MockSocket
        jaribu:
            tuma
        mwishowe:
            socket.socket = old_socket

    eleza test_connect(self):
        port = support.find_unused_port()
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(cli.close)
        ukijumuisha self.assertRaises(OSError) kama cm:
            cli.connect((HOST, port))
        self.assertEqual(cm.exception.errno, errno.ECONNREFUSED)

    eleza test_create_connection(self):
        # Issue #9792: errors ashiriad by create_connection() should have
        # a proper errno attribute.
        port = support.find_unused_port()
        ukijumuisha self.assertRaises(OSError) kama cm:
            socket.create_connection((HOST, port))

        # Issue #16257: create_connection() calls getaddrinfo() against
        # 'localhost'.  This may result kwenye an IPV6 addr being rudishaed
        # kama well kama an IPV4 one:
        #   >>> socket.getaddrinfo('localhost', port, 0, SOCK_STREAM)
        #   >>> [(2,  2, 0, '', ('127.0.0.1', 41230)),
        #        (26, 2, 0, '', ('::1', 41230, 0, 0))]
        #
        # create_connection() enumerates through all the addresses rudishaed
        # na ikiwa it doesn't successfully bind to any of them, it propagates
        # the last exception it encountered.
        #
        # On Solaris, ENETUNREACH ni rudishaed kwenye this circumstance instead
        # of ECONNREFUSED.  So, ikiwa that errno exists, add it to our list of
        # expected errnos.
        expected_errnos = support.get_socket_conn_refused_errs()
        self.assertIn(cm.exception.errno, expected_errnos)

    eleza test_create_connection_timeout(self):
        # Issue #9792: create_connection() should sio recast timeout errors
        # kama generic socket errors.
        ukijumuisha self.mocked_socket_module():
            jaribu:
                socket.create_connection((HOST, 1234))
            tatizo socket.timeout:
                pita
            tatizo OSError kama exc:
                ikiwa support.IPV6_ENABLED ama exc.errno != errno.EAFNOSUPPORT:
                    ashiria
            isipokua:
                self.fail('socket.timeout sio ashiriad')


kundi NetworkConnectionAttributesTest(SocketTCPTest, ThreadableTest):

    eleza __init__(self, methodName='runTest'):
        SocketTCPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    eleza clientSetUp(self):
        self.source_port = support.find_unused_port()

    eleza clientTearDown(self):
        self.cli.close()
        self.cli = Tupu
        ThreadableTest.clientTearDown(self)

    eleza _justAccept(self):
        conn, addr = self.serv.accept()
        conn.close()

    testFamily = _justAccept
    eleza _testFamily(self):
        self.cli = socket.create_connection((HOST, self.port), timeout=30)
        self.addCleanup(self.cli.close)
        self.assertEqual(self.cli.family, 2)

    testSourceAddress = _justAccept
    eleza _testSourceAddress(self):
        self.cli = socket.create_connection((HOST, self.port), timeout=30,
                source_address=('', self.source_port))
        self.addCleanup(self.cli.close)
        self.assertEqual(self.cli.getsockname()[1], self.source_port)
        # The port number being used ni sufficient to show that the bind()
        # call happened.

    testTimeoutDefault = _justAccept
    eleza _testTimeoutDefault(self):
        # pitaing no explicit timeout uses socket's global default
        self.assertKweli(socket.getdefaulttimeout() ni Tupu)
        socket.setdefaulttimeout(42)
        jaribu:
            self.cli = socket.create_connection((HOST, self.port))
            self.addCleanup(self.cli.close)
        mwishowe:
            socket.setdefaulttimeout(Tupu)
        self.assertEqual(self.cli.gettimeout(), 42)

    testTimeoutTupu = _justAccept
    eleza _testTimeoutTupu(self):
        # Tupu timeout means the same kama sock.settimeout(Tupu)
        self.assertKweli(socket.getdefaulttimeout() ni Tupu)
        socket.setdefaulttimeout(30)
        jaribu:
            self.cli = socket.create_connection((HOST, self.port), timeout=Tupu)
            self.addCleanup(self.cli.close)
        mwishowe:
            socket.setdefaulttimeout(Tupu)
        self.assertEqual(self.cli.gettimeout(), Tupu)

    testTimeoutValueNamed = _justAccept
    eleza _testTimeoutValueNamed(self):
        self.cli = socket.create_connection((HOST, self.port), timeout=30)
        self.assertEqual(self.cli.gettimeout(), 30)

    testTimeoutValueNonamed = _justAccept
    eleza _testTimeoutValueNonamed(self):
        self.cli = socket.create_connection((HOST, self.port), 30)
        self.addCleanup(self.cli.close)
        self.assertEqual(self.cli.gettimeout(), 30)


kundi NetworkConnectionBehaviourTest(SocketTCPTest, ThreadableTest):

    eleza __init__(self, methodName='runTest'):
        SocketTCPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    eleza clientSetUp(self):
        pita

    eleza clientTearDown(self):
        self.cli.close()
        self.cli = Tupu
        ThreadableTest.clientTearDown(self)

    eleza testInsideTimeout(self):
        conn, addr = self.serv.accept()
        self.addCleanup(conn.close)
        time.sleep(3)
        conn.send(b"done!")
    testOutsideTimeout = testInsideTimeout

    eleza _testInsideTimeout(self):
        self.cli = sock = socket.create_connection((HOST, self.port))
        data = sock.recv(5)
        self.assertEqual(data, b"done!")

    eleza _testOutsideTimeout(self):
        self.cli = sock = socket.create_connection((HOST, self.port), timeout=1)
        self.assertRaises(socket.timeout, lambda: sock.recv(5))


kundi TCPTimeoutTest(SocketTCPTest):

    eleza testTCPTimeout(self):
        eleza ashiria_timeout(*args, **kwargs):
            self.serv.settimeout(1.0)
            self.serv.accept()
        self.assertRaises(socket.timeout, ashiria_timeout,
                              "Error generating a timeout exception (TCP)")

    eleza testTimeoutZero(self):
        ok = Uongo
        jaribu:
            self.serv.settimeout(0.0)
            foo = self.serv.accept()
        tatizo socket.timeout:
            self.fail("caught timeout instead of error (TCP)")
        tatizo OSError:
            ok = Kweli
        except:
            self.fail("caught unexpected exception (TCP)")
        ikiwa sio ok:
            self.fail("accept() rudishaed success when we did sio expect it")

    @unittest.skipUnless(hasattr(signal, 'alarm'),
                         'test needs signal.alarm()')
    eleza testInterruptedTimeout(self):
        # XXX I don't know how to do this test on MSWindows ama any other
        # platform that doesn't support signal.alarm() ama os.kill(), though
        # the bug should have existed on all platforms.
        self.serv.settimeout(5.0)   # must be longer than alarm
        kundi Alarm(Exception):
            pita
        eleza alarm_handler(signal, frame):
            ashiria Alarm
        old_alarm = signal.signal(signal.SIGALRM, alarm_handler)
        jaribu:
            jaribu:
                signal.alarm(2)    # POSIX allows alarm to be up to 1 second early
                foo = self.serv.accept()
            tatizo socket.timeout:
                self.fail("caught timeout instead of Alarm")
            tatizo Alarm:
                pita
            except:
                self.fail("caught other exception instead of Alarm:"
                          " %s(%s):\n%s" %
                          (sys.exc_info()[:2] + (traceback.format_exc(),)))
            isipokua:
                self.fail("nothing caught")
            mwishowe:
                signal.alarm(0)         # shut off alarm
        tatizo Alarm:
            self.fail("got Alarm kwenye wrong place")
        mwishowe:
            # no alarm can be pending.  Safe to restore old handler.
            signal.signal(signal.SIGALRM, old_alarm)

kundi UDPTimeoutTest(SocketUDPTest):

    eleza testUDPTimeout(self):
        eleza ashiria_timeout(*args, **kwargs):
            self.serv.settimeout(1.0)
            self.serv.recv(1024)
        self.assertRaises(socket.timeout, ashiria_timeout,
                              "Error generating a timeout exception (UDP)")

    eleza testTimeoutZero(self):
        ok = Uongo
        jaribu:
            self.serv.settimeout(0.0)
            foo = self.serv.recv(1024)
        tatizo socket.timeout:
            self.fail("caught timeout instead of error (UDP)")
        tatizo OSError:
            ok = Kweli
        except:
            self.fail("caught unexpected exception (UDP)")
        ikiwa sio ok:
            self.fail("recv() rudishaed success when we did sio expect it")

kundi TestExceptions(unittest.TestCase):

    eleza testExceptionTree(self):
        self.assertKweli(issubclass(OSError, Exception))
        self.assertKweli(issubclass(socket.herror, OSError))
        self.assertKweli(issubclass(socket.gaierror, OSError))
        self.assertKweli(issubclass(socket.timeout, OSError))

    eleza test_setblocking_invalidfd(self):
        # Regression test kila issue #28471

        sock0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM, 0, sock0.fileno())
        sock0.close()
        self.addCleanup(sock.detach)

        ukijumuisha self.assertRaises(OSError):
            sock.setblocking(Uongo)


@unittest.skipUnless(sys.platform == 'linux', 'Linux specific test')
kundi TestLinuxAbstractNamespace(unittest.TestCase):

    UNIX_PATH_MAX = 108

    eleza testLinuxAbstractNamespace(self):
        address = b"\x00python-test-hello\x00\xff"
        ukijumuisha socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) kama s1:
            s1.bind(address)
            s1.listen()
            ukijumuisha socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) kama s2:
                s2.connect(s1.getsockname())
                ukijumuisha s1.accept()[0] kama s3:
                    self.assertEqual(s1.getsockname(), address)
                    self.assertEqual(s2.getpeername(), address)

    eleza testMaxName(self):
        address = b"\x00" + b"h" * (self.UNIX_PATH_MAX - 1)
        ukijumuisha socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) kama s:
            s.bind(address)
            self.assertEqual(s.getsockname(), address)

    eleza testNameOverflow(self):
        address = "\x00" + "h" * self.UNIX_PATH_MAX
        ukijumuisha socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) kama s:
            self.assertRaises(OSError, s.bind, address)

    eleza testStrName(self):
        # Check that an abstract name can be pitaed kama a string.
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        jaribu:
            s.bind("\x00python\x00test\x00")
            self.assertEqual(s.getsockname(), b"\x00python\x00test\x00")
        mwishowe:
            s.close()

    eleza testBytearrayName(self):
        # Check that an abstract name can be pitaed kama a bytearray.
        ukijumuisha socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) kama s:
            s.bind(bytearray(b"\x00python\x00test\x00"))
            self.assertEqual(s.getsockname(), b"\x00python\x00test\x00")

@unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'test needs socket.AF_UNIX')
kundi TestUnixDomain(unittest.TestCase):

    eleza setUp(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    eleza tearDown(self):
        self.sock.close()

    eleza encoded(self, path):
        # Return the given path encoded kwenye the file system encoding,
        # ama skip the test ikiwa this ni sio possible.
        jaribu:
            rudisha os.fsencode(path)
        tatizo UnicodeEncodeError:
            self.skipTest(
                "Pathname {0!a} cannot be represented kwenye file "
                "system encoding {1!r}".format(
                    path, sys.getfilesystemencoding()))

    eleza bind(self, sock, path):
        # Bind the socket
        jaribu:
            support.bind_unix_socket(sock, path)
        tatizo OSError kama e:
            ikiwa str(e) == "AF_UNIX path too long":
                self.skipTest(
                    "Pathname {0!a} ni too long to serve kama an AF_UNIX path"
                    .format(path))
            isipokua:
                ashiria

    eleza testUnbound(self):
        # Issue #30205 (note getsockname() can rudisha Tupu on OS X)
        self.assertIn(self.sock.getsockname(), ('', Tupu))

    eleza testStrAddr(self):
        # Test binding to na retrieving a normal string pathname.
        path = os.path.abspath(support.TESTFN)
        self.bind(self.sock, path)
        self.addCleanup(support.unlink, path)
        self.assertEqual(self.sock.getsockname(), path)

    eleza testBytesAddr(self):
        # Test binding to a bytes pathname.
        path = os.path.abspath(support.TESTFN)
        self.bind(self.sock, self.encoded(path))
        self.addCleanup(support.unlink, path)
        self.assertEqual(self.sock.getsockname(), path)

    eleza testSurrogateescapeBind(self):
        # Test binding to a valid non-ASCII pathname, ukijumuisha the
        # non-ASCII bytes supplied using surrogateescape encoding.
        path = os.path.abspath(support.TESTFN_UNICODE)
        b = self.encoded(path)
        self.bind(self.sock, b.decode("ascii", "surrogateescape"))
        self.addCleanup(support.unlink, path)
        self.assertEqual(self.sock.getsockname(), path)

    eleza testUnencodableAddr(self):
        # Test binding to a pathname that cannot be encoded kwenye the
        # file system encoding.
        ikiwa support.TESTFN_UNENCODABLE ni Tupu:
            self.skipTest("No unencodable filename available")
        path = os.path.abspath(support.TESTFN_UNENCODABLE)
        self.bind(self.sock, path)
        self.addCleanup(support.unlink, path)
        self.assertEqual(self.sock.getsockname(), path)


kundi BufferIOTest(SocketConnectedTest):
    """
    Test the buffer versions of socket.recv() na socket.send().
    """
    eleza __init__(self, methodName='runTest'):
        SocketConnectedTest.__init__(self, methodName=methodName)

    eleza testRecvIntoArray(self):
        buf = array.array("B", [0] * len(MSG))
        nbytes = self.cli_conn.recv_into(buf)
        self.assertEqual(nbytes, len(MSG))
        buf = buf.tobytes()
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    eleza _testRecvIntoArray(self):
        buf = bytes(MSG)
        self.serv_conn.send(buf)

    eleza testRecvIntoBytearray(self):
        buf = bytearray(1024)
        nbytes = self.cli_conn.recv_into(buf)
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    _testRecvIntoBytearray = _testRecvIntoArray

    eleza testRecvIntoMemoryview(self):
        buf = bytearray(1024)
        nbytes = self.cli_conn.recv_into(memoryview(buf))
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    _testRecvIntoMemoryview = _testRecvIntoArray

    eleza testRecvFromIntoArray(self):
        buf = array.array("B", [0] * len(MSG))
        nbytes, addr = self.cli_conn.recvkutoka_into(buf)
        self.assertEqual(nbytes, len(MSG))
        buf = buf.tobytes()
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    eleza _testRecvFromIntoArray(self):
        buf = bytes(MSG)
        self.serv_conn.send(buf)

    eleza testRecvFromIntoBytearray(self):
        buf = bytearray(1024)
        nbytes, addr = self.cli_conn.recvkutoka_into(buf)
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    _testRecvFromIntoBytearray = _testRecvFromIntoArray

    eleza testRecvFromIntoMemoryview(self):
        buf = bytearray(1024)
        nbytes, addr = self.cli_conn.recvkutoka_into(memoryview(buf))
        self.assertEqual(nbytes, len(MSG))
        msg = buf[:len(MSG)]
        self.assertEqual(msg, MSG)

    _testRecvFromIntoMemoryview = _testRecvFromIntoArray

    eleza testRecvFromIntoSmallBuffer(self):
        # See issue #20246.
        buf = bytearray(8)
        self.assertRaises(ValueError, self.cli_conn.recvkutoka_into, buf, 1024)

    eleza _testRecvFromIntoSmallBuffer(self):
        self.serv_conn.send(MSG)

    eleza testRecvFromIntoEmptyBuffer(self):
        buf = bytearray()
        self.cli_conn.recvkutoka_into(buf)
        self.cli_conn.recvkutoka_into(buf, 0)

    _testRecvFromIntoEmptyBuffer = _testRecvFromIntoArray


TIPC_STYPE = 2000
TIPC_LOWER = 200
TIPC_UPPER = 210

eleza isTipcAvailable():
    """Check ikiwa the TIPC module ni loaded

    The TIPC module ni sio loaded automatically on Ubuntu na probably
    other Linux distros.
    """
    ikiwa sio hasattr(socket, "AF_TIPC"):
        rudisha Uongo
    jaribu:
        f = open("/proc/modules")
    tatizo (FileNotFoundError, IsADirectoryError, PermissionError):
        # It's ok ikiwa the file does sio exist, ni a directory ama ikiwa we
        # have sio the permission to read it.
        rudisha Uongo
    ukijumuisha f:
        kila line kwenye f:
            ikiwa line.startswith("tipc "):
                rudisha Kweli
    rudisha Uongo

@unittest.skipUnless(isTipcAvailable(),
                     "TIPC module ni sio loaded, please 'sudo modprobe tipc'")
kundi TIPCTest(unittest.TestCase):
    eleza testRDM(self):
        srv = socket.socket(socket.AF_TIPC, socket.SOCK_RDM)
        cli = socket.socket(socket.AF_TIPC, socket.SOCK_RDM)
        self.addCleanup(srv.close)
        self.addCleanup(cli.close)

        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srvaddr = (socket.TIPC_ADDR_NAMESEQ, TIPC_STYPE,
                TIPC_LOWER, TIPC_UPPER)
        srv.bind(srvaddr)

        sendaddr = (socket.TIPC_ADDR_NAME, TIPC_STYPE,
                TIPC_LOWER + int((TIPC_UPPER - TIPC_LOWER) / 2), 0)
        cli.sendto(MSG, sendaddr)

        msg, recvaddr = srv.recvkutoka(1024)

        self.assertEqual(cli.getsockname(), recvaddr)
        self.assertEqual(msg, MSG)


@unittest.skipUnless(isTipcAvailable(),
                     "TIPC module ni sio loaded, please 'sudo modprobe tipc'")
kundi TIPCThreadableTest(unittest.TestCase, ThreadableTest):
    eleza __init__(self, methodName = 'runTest'):
        unittest.TestCase.__init__(self, methodName = methodName)
        ThreadableTest.__init__(self)

    eleza setUp(self):
        self.srv = socket.socket(socket.AF_TIPC, socket.SOCK_STREAM)
        self.addCleanup(self.srv.close)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srvaddr = (socket.TIPC_ADDR_NAMESEQ, TIPC_STYPE,
                TIPC_LOWER, TIPC_UPPER)
        self.srv.bind(srvaddr)
        self.srv.listen()
        self.serverExplicitReady()
        self.conn, self.connaddr = self.srv.accept()
        self.addCleanup(self.conn.close)

    eleza clientSetUp(self):
        # There ni a hittable race between serverExplicitReady() na the
        # accept() call; sleep a little wakati to avoid it, otherwise
        # we could get an exception
        time.sleep(0.1)
        self.cli = socket.socket(socket.AF_TIPC, socket.SOCK_STREAM)
        self.addCleanup(self.cli.close)
        addr = (socket.TIPC_ADDR_NAME, TIPC_STYPE,
                TIPC_LOWER + int((TIPC_UPPER - TIPC_LOWER) / 2), 0)
        self.cli.connect(addr)
        self.cliaddr = self.cli.getsockname()

    eleza testStream(self):
        msg = self.conn.recv(1024)
        self.assertEqual(msg, MSG)
        self.assertEqual(self.cliaddr, self.connaddr)

    eleza _testStream(self):
        self.cli.send(MSG)
        self.cli.close()


kundi ContextManagersTest(ThreadedTCPSocketTest):

    eleza _testSocketClass(self):
        # base test
        ukijumuisha socket.socket() kama sock:
            self.assertUongo(sock._closed)
        self.assertKweli(sock._closed)
        # close inside ukijumuisha block
        ukijumuisha socket.socket() kama sock:
            sock.close()
        self.assertKweli(sock._closed)
        # exception inside ukijumuisha block
        ukijumuisha socket.socket() kama sock:
            self.assertRaises(OSError, sock.sendall, b'foo')
        self.assertKweli(sock._closed)

    eleza testCreateConnectionBase(self):
        conn, addr = self.serv.accept()
        self.addCleanup(conn.close)
        data = conn.recv(1024)
        conn.sendall(data)

    eleza _testCreateConnectionBase(self):
        address = self.serv.getsockname()
        ukijumuisha socket.create_connection(address) kama sock:
            self.assertUongo(sock._closed)
            sock.sendall(b'foo')
            self.assertEqual(sock.recv(1024), b'foo')
        self.assertKweli(sock._closed)

    eleza testCreateConnectionClose(self):
        conn, addr = self.serv.accept()
        self.addCleanup(conn.close)
        data = conn.recv(1024)
        conn.sendall(data)

    eleza _testCreateConnectionClose(self):
        address = self.serv.getsockname()
        ukijumuisha socket.create_connection(address) kama sock:
            sock.close()
        self.assertKweli(sock._closed)
        self.assertRaises(OSError, sock.sendall, b'foo')


kundi InheritanceTest(unittest.TestCase):
    @unittest.skipUnless(hasattr(socket, "SOCK_CLOEXEC"),
                         "SOCK_CLOEXEC sio defined")
    @support.requires_linux_version(2, 6, 28)
    eleza test_SOCK_CLOEXEC(self):
        ukijumuisha socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM | socket.SOCK_CLOEXEC) kama s:
            self.assertEqual(s.type, socket.SOCK_STREAM)
            self.assertUongo(s.get_inheritable())

    eleza test_default_inheritable(self):
        sock = socket.socket()
        ukijumuisha sock:
            self.assertEqual(sock.get_inheritable(), Uongo)

    eleza test_dup(self):
        sock = socket.socket()
        ukijumuisha sock:
            newsock = sock.dup()
            sock.close()
            ukijumuisha newsock:
                self.assertEqual(newsock.get_inheritable(), Uongo)

    eleza test_set_inheritable(self):
        sock = socket.socket()
        ukijumuisha sock:
            sock.set_inheritable(Kweli)
            self.assertEqual(sock.get_inheritable(), Kweli)

            sock.set_inheritable(Uongo)
            self.assertEqual(sock.get_inheritable(), Uongo)

    @unittest.skipIf(fcntl ni Tupu, "need fcntl")
    eleza test_get_inheritable_cloexec(self):
        sock = socket.socket()
        ukijumuisha sock:
            fd = sock.fileno()
            self.assertEqual(sock.get_inheritable(), Uongo)

            # clear FD_CLOEXEC flag
            flags = fcntl.fcntl(fd, fcntl.F_GETFD)
            flags &= ~fcntl.FD_CLOEXEC
            fcntl.fcntl(fd, fcntl.F_SETFD, flags)

            self.assertEqual(sock.get_inheritable(), Kweli)

    @unittest.skipIf(fcntl ni Tupu, "need fcntl")
    eleza test_set_inheritable_cloexec(self):
        sock = socket.socket()
        ukijumuisha sock:
            fd = sock.fileno()
            self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC,
                             fcntl.FD_CLOEXEC)

            sock.set_inheritable(Kweli)
            self.assertEqual(fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC,
                             0)


    eleza test_socketpair(self):
        s1, s2 = socket.socketpair()
        self.addCleanup(s1.close)
        self.addCleanup(s2.close)
        self.assertEqual(s1.get_inheritable(), Uongo)
        self.assertEqual(s2.get_inheritable(), Uongo)


@unittest.skipUnless(hasattr(socket, "SOCK_NONBLOCK"),
                     "SOCK_NONBLOCK sio defined")
kundi NonblockConstantTest(unittest.TestCase):
    eleza checkNonblock(self, s, nonblock=Kweli, timeout=0.0):
        ikiwa nonblock:
            self.assertEqual(s.type, socket.SOCK_STREAM)
            self.assertEqual(s.gettimeout(), timeout)
            self.assertKweli(
                fcntl.fcntl(s, fcntl.F_GETFL, os.O_NONBLOCK) & os.O_NONBLOCK)
            ikiwa timeout == 0:
                # timeout == 0: means that getblocking() must be Uongo.
                self.assertUongo(s.getblocking())
            isipokua:
                # If timeout > 0, the socket will be kwenye a "blocking" mode
                # kutoka the standpoint of the Python API.  For Python socket
                # object, "blocking" means that operations like 'sock.recv()'
                # will block.  Internally, file descriptors for
                # "blocking" Python sockets *ukijumuisha timeouts* are kwenye a
                # *non-blocking* mode, na 'sock.recv()' uses 'select()'
                # na handles EWOULDBLOCK/EAGAIN to enforce the timeout.
                self.assertKweli(s.getblocking())
        isipokua:
            self.assertEqual(s.type, socket.SOCK_STREAM)
            self.assertEqual(s.gettimeout(), Tupu)
            self.assertUongo(
                fcntl.fcntl(s, fcntl.F_GETFL, os.O_NONBLOCK) & os.O_NONBLOCK)
            self.assertKweli(s.getblocking())

    @support.requires_linux_version(2, 6, 28)
    eleza test_SOCK_NONBLOCK(self):
        # a lot of it seems silly na redundant, but I wanted to test that
        # changing back na forth worked ok
        ukijumuisha socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM | socket.SOCK_NONBLOCK) kama s:
            self.checkNonblock(s)
            s.setblocking(1)
            self.checkNonblock(s, nonblock=Uongo)
            s.setblocking(0)
            self.checkNonblock(s)
            s.settimeout(Tupu)
            self.checkNonblock(s, nonblock=Uongo)
            s.settimeout(2.0)
            self.checkNonblock(s, timeout=2.0)
            s.setblocking(1)
            self.checkNonblock(s, nonblock=Uongo)
        # defaulttimeout
        t = socket.getdefaulttimeout()
        socket.setdefaulttimeout(0.0)
        ukijumuisha socket.socket() kama s:
            self.checkNonblock(s)
        socket.setdefaulttimeout(Tupu)
        ukijumuisha socket.socket() kama s:
            self.checkNonblock(s, Uongo)
        socket.setdefaulttimeout(2.0)
        ukijumuisha socket.socket() kama s:
            self.checkNonblock(s, timeout=2.0)
        socket.setdefaulttimeout(Tupu)
        ukijumuisha socket.socket() kama s:
            self.checkNonblock(s, Uongo)
        socket.setdefaulttimeout(t)


@unittest.skipUnless(os.name == "nt", "Windows specific")
@unittest.skipUnless(multiprocessing, "need multiprocessing")
kundi TestSocketSharing(SocketTCPTest):
    # This must be classmethod na sio staticmethod ama multiprocessing
    # won't be able to bootstrap it.
    @classmethod
    eleza remoteProcessServer(cls, q):
        # Recreate socket kutoka shared data
        sdata = q.get()
        message = q.get()

        s = socket.kutokashare(sdata)
        s2, c = s.accept()

        # Send the message
        s2.sendall(message)
        s2.close()
        s.close()

    eleza testShare(self):
        # Transfer the listening server socket to another process
        # na service it kutoka there.

        # Create process:
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=self.remoteProcessServer, args=(q,))
        p.start()

        # Get the shared socket data
        data = self.serv.share(p.pid)

        # Pass the shared socket to the other process
        addr = self.serv.getsockname()
        self.serv.close()
        q.put(data)

        # The data that the server will send us
        message = b"slapmahfro"
        q.put(message)

        # Connect
        s = socket.create_connection(addr)
        #  listen kila the data
        m = []
        wakati Kweli:
            data = s.recv(100)
            ikiwa sio data:
                koma
            m.append(data)
        s.close()
        received = b"".join(m)
        self.assertEqual(received, message)
        p.join()

    eleza testShareLength(self):
        data = self.serv.share(os.getpid())
        self.assertRaises(ValueError, socket.kutokashare, data[:-1])
        self.assertRaises(ValueError, socket.kutokashare, data+b"foo")

    eleza compareSockets(self, org, other):
        # socket sharing ni expected to work only kila blocking socket
        # since the internal python timeout value isn't transferred.
        self.assertEqual(org.gettimeout(), Tupu)
        self.assertEqual(org.gettimeout(), other.gettimeout())

        self.assertEqual(org.family, other.family)
        self.assertEqual(org.type, other.type)
        # If the user specified "0" kila proto, then
        # internally windows will have picked the correct value.
        # Python introspection on the socket however will still rudisha
        # 0.  For the shared socket, the python value ni recreated
        # kutoka the actual value, so it may sio compare correctly.
        ikiwa org.proto != 0:
            self.assertEqual(org.proto, other.proto)

    eleza testShareLocal(self):
        data = self.serv.share(os.getpid())
        s = socket.kutokashare(data)
        jaribu:
            self.compareSockets(self.serv, s)
        mwishowe:
            s.close()

    eleza testTypes(self):
        families = [socket.AF_INET, socket.AF_INET6]
        types = [socket.SOCK_STREAM, socket.SOCK_DGRAM]
        kila f kwenye families:
            kila t kwenye types:
                jaribu:
                    source = socket.socket(f, t)
                tatizo OSError:
                    endelea # This combination ni sio supported
                jaribu:
                    data = source.share(os.getpid())
                    shared = socket.kutokashare(data)
                    jaribu:
                        self.compareSockets(source, shared)
                    mwishowe:
                        shared.close()
                mwishowe:
                    source.close()


kundi SendfileUsingSendTest(ThreadedTCPSocketTest):
    """
    Test the send() implementation of socket.sendfile().
    """

    FILESIZE = (10 * 1024 * 1024)  # 10 MiB
    BUFSIZE = 8192
    FILEDATA = b""
    TIMEOUT = 2

    @classmethod
    eleza setUpClass(cls):
        eleza chunks(total, step):
            assert total >= step
            wakati total > step:
                tuma step
                total -= step
            ikiwa total:
                tuma total

        chunk = b"".join([random.choice(string.ascii_letters).encode()
                          kila i kwenye range(cls.BUFSIZE)])
        ukijumuisha open(support.TESTFN, 'wb') kama f:
            kila csize kwenye chunks(cls.FILESIZE, cls.BUFSIZE):
                f.write(chunk)
        ukijumuisha open(support.TESTFN, 'rb') kama f:
            cls.FILEDATA = f.read()
            assert len(cls.FILEDATA) == cls.FILESIZE

    @classmethod
    eleza tearDownClass(cls):
        support.unlink(support.TESTFN)

    eleza accept_conn(self):
        self.serv.settimeout(MAIN_TIMEOUT)
        conn, addr = self.serv.accept()
        conn.settimeout(self.TIMEOUT)
        self.addCleanup(conn.close)
        rudisha conn

    eleza recv_data(self, conn):
        received = []
        wakati Kweli:
            chunk = conn.recv(self.BUFSIZE)
            ikiwa sio chunk:
                koma
            received.append(chunk)
        rudisha b''.join(received)

    eleza meth_kutoka_sock(self, sock):
        # Depending on the mixin kundi being run rudisha either send()
        # ama sendfile() method implementation.
        rudisha getattr(sock, "_sendfile_use_send")

    # regular file

    eleza _testRegularFile(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        ukijumuisha socket.create_connection(address) kama sock, file kama file:
            meth = self.meth_kutoka_sock(sock)
            sent = meth(file)
            self.assertEqual(sent, self.FILESIZE)
            self.assertEqual(file.tell(), self.FILESIZE)

    eleza testRegularFile(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), self.FILESIZE)
        self.assertEqual(data, self.FILEDATA)

    # non regular file

    eleza _testNonRegularFile(self):
        address = self.serv.getsockname()
        file = io.BytesIO(self.FILEDATA)
        ukijumuisha socket.create_connection(address) kama sock, file kama file:
            sent = sock.sendfile(file)
            self.assertEqual(sent, self.FILESIZE)
            self.assertEqual(file.tell(), self.FILESIZE)
            self.assertRaises(socket._GiveupOnSendfile,
                              sock._sendfile_use_sendfile, file)

    eleza testNonRegularFile(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), self.FILESIZE)
        self.assertEqual(data, self.FILEDATA)

    # empty file

    eleza _testEmptyFileSend(self):
        address = self.serv.getsockname()
        filename = support.TESTFN + "2"
        ukijumuisha open(filename, 'wb'):
            self.addCleanup(support.unlink, filename)
        file = open(filename, 'rb')
        ukijumuisha socket.create_connection(address) kama sock, file kama file:
            meth = self.meth_kutoka_sock(sock)
            sent = meth(file)
            self.assertEqual(sent, 0)
            self.assertEqual(file.tell(), 0)

    eleza testEmptyFileSend(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(data, b"")

    # offset

    eleza _testOffset(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        ukijumuisha socket.create_connection(address) kama sock, file kama file:
            meth = self.meth_kutoka_sock(sock)
            sent = meth(file, offset=5000)
            self.assertEqual(sent, self.FILESIZE - 5000)
            self.assertEqual(file.tell(), self.FILESIZE)

    eleza testOffset(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), self.FILESIZE - 5000)
        self.assertEqual(data, self.FILEDATA[5000:])

    # count

    eleza _testCount(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        ukijumuisha socket.create_connection(address, timeout=2) kama sock, file kama file:
            count = 5000007
            meth = self.meth_kutoka_sock(sock)
            sent = meth(file, count=count)
            self.assertEqual(sent, count)
            self.assertEqual(file.tell(), count)

    eleza testCount(self):
        count = 5000007
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), count)
        self.assertEqual(data, self.FILEDATA[:count])

    # count small

    eleza _testCountSmall(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        ukijumuisha socket.create_connection(address, timeout=2) kama sock, file kama file:
            count = 1
            meth = self.meth_kutoka_sock(sock)
            sent = meth(file, count=count)
            self.assertEqual(sent, count)
            self.assertEqual(file.tell(), count)

    eleza testCountSmall(self):
        count = 1
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), count)
        self.assertEqual(data, self.FILEDATA[:count])

    # count + offset

    eleza _testCountWithOffset(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        ukijumuisha socket.create_connection(address, timeout=2) kama sock, file kama file:
            count = 100007
            meth = self.meth_kutoka_sock(sock)
            sent = meth(file, offset=2007, count=count)
            self.assertEqual(sent, count)
            self.assertEqual(file.tell(), count + 2007)

    eleza testCountWithOffset(self):
        count = 100007
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), count)
        self.assertEqual(data, self.FILEDATA[2007:count+2007])

    # non blocking sockets are sio supposed to work

    eleza _testNonBlocking(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        ukijumuisha socket.create_connection(address) kama sock, file kama file:
            sock.setblocking(Uongo)
            meth = self.meth_kutoka_sock(sock)
            self.assertRaises(ValueError, meth, file)
            self.assertRaises(ValueError, sock.sendfile, file)

    eleza testNonBlocking(self):
        conn = self.accept_conn()
        ikiwa conn.recv(8192):
            self.fail('was sio supposed to receive any data')

    # timeout (non-triggered)

    eleza _testWithTimeout(self):
        address = self.serv.getsockname()
        file = open(support.TESTFN, 'rb')
        ukijumuisha socket.create_connection(address, timeout=2) kama sock, file kama file:
            meth = self.meth_kutoka_sock(sock)
            sent = meth(file)
            self.assertEqual(sent, self.FILESIZE)

    eleza testWithTimeout(self):
        conn = self.accept_conn()
        data = self.recv_data(conn)
        self.assertEqual(len(data), self.FILESIZE)
        self.assertEqual(data, self.FILEDATA)

    # timeout (triggered)

    eleza _testWithTimeoutTriggeredSend(self):
        address = self.serv.getsockname()
        ukijumuisha open(support.TESTFN, 'rb') kama file:
            ukijumuisha socket.create_connection(address) kama sock:
                sock.settimeout(0.01)
                meth = self.meth_kutoka_sock(sock)
                self.assertRaises(socket.timeout, meth, file)

    eleza testWithTimeoutTriggeredSend(self):
        conn = self.accept_conn()
        conn.recv(88192)

    # errors

    eleza _test_errors(self):
        pita

    eleza test_errors(self):
        ukijumuisha open(support.TESTFN, 'rb') kama file:
            ukijumuisha socket.socket(type=socket.SOCK_DGRAM) kama s:
                meth = self.meth_kutoka_sock(s)
                self.assertRaisesRegex(
                    ValueError, "SOCK_STREAM", meth, file)
        ukijumuisha open(support.TESTFN, 'rt') kama file:
            ukijumuisha socket.socket() kama s:
                meth = self.meth_kutoka_sock(s)
                self.assertRaisesRegex(
                    ValueError, "binary mode", meth, file)
        ukijumuisha open(support.TESTFN, 'rb') kama file:
            ukijumuisha socket.socket() kama s:
                meth = self.meth_kutoka_sock(s)
                self.assertRaisesRegex(TypeError, "positive integer",
                                       meth, file, count='2')
                self.assertRaisesRegex(TypeError, "positive integer",
                                       meth, file, count=0.1)
                self.assertRaisesRegex(ValueError, "positive integer",
                                       meth, file, count=0)
                self.assertRaisesRegex(ValueError, "positive integer",
                                       meth, file, count=-1)


@unittest.skipUnless(hasattr(os, "sendfile"),
                     'os.sendfile() required kila this test.')
kundi SendfileUsingSendfileTest(SendfileUsingSendTest):
    """
    Test the sendfile() implementation of socket.sendfile().
    """
    eleza meth_kutoka_sock(self, sock):
        rudisha getattr(sock, "_sendfile_use_sendfile")


@unittest.skipUnless(HAVE_SOCKET_ALG, 'AF_ALG required')
kundi LinuxKernelCryptoAPI(unittest.TestCase):
    # tests kila AF_ALG
    eleza create_alg(self, typ, name):
        sock = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
        jaribu:
            sock.bind((typ, name))
        tatizo FileNotFoundError kama e:
            # type / algorithm ni sio available
            sock.close()
            ashiria unittest.SkipTest(str(e), typ, name)
        isipokua:
            rudisha sock

    # bpo-31705: On kernel older than 4.5, sendto() failed ukijumuisha ENOKEY,
    # at least on ppc64le architecture
    @support.requires_linux_version(4, 5)
    eleza test_sha256(self):
        expected = bytes.kutokahex("ba7816bf8f01cfea414140de5dae2223b00361a396"
                                 "177a9cb410ff61f20015ad")
        ukijumuisha self.create_alg('hash', 'sha256') kama algo:
            op, _ = algo.accept()
            ukijumuisha op:
                op.sendall(b"abc")
                self.assertEqual(op.recv(512), expected)

            op, _ = algo.accept()
            ukijumuisha op:
                op.send(b'a', socket.MSG_MORE)
                op.send(b'b', socket.MSG_MORE)
                op.send(b'c', socket.MSG_MORE)
                op.send(b'')
                self.assertEqual(op.recv(512), expected)

    eleza test_hmac_sha1(self):
        expected = bytes.kutokahex("effcdf6ae5eb2fa2d27416d5f184df9c259a7c79")
        ukijumuisha self.create_alg('hash', 'hmac(sha1)') kama algo:
            algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, b"Jefe")
            op, _ = algo.accept()
            ukijumuisha op:
                op.sendall(b"what do ya want kila nothing?")
                self.assertEqual(op.recv(512), expected)

    # Although it should work ukijumuisha 3.19 na newer the test blocks on
    # Ubuntu 15.10 ukijumuisha Kernel 4.2.0-19.
    @support.requires_linux_version(4, 3)
    eleza test_aes_cbc(self):
        key = bytes.kutokahex('06a9214036b8a15b512e03d534120006')
        iv = bytes.kutokahex('3dafba429d9eb430b422da802c9fac41')
        msg = b"Single block msg"
        ciphertext = bytes.kutokahex('e353779c1079aeb82708942dbe77181a')
        msglen = len(msg)
        ukijumuisha self.create_alg('skcipher', 'cbc(aes)') kama algo:
            algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, key)
            op, _ = algo.accept()
            ukijumuisha op:
                op.sendmsg_afalg(op=socket.ALG_OP_ENCRYPT, iv=iv,
                                 flags=socket.MSG_MORE)
                op.sendall(msg)
                self.assertEqual(op.recv(msglen), ciphertext)

            op, _ = algo.accept()
            ukijumuisha op:
                op.sendmsg_afalg([ciphertext],
                                 op=socket.ALG_OP_DECRYPT, iv=iv)
                self.assertEqual(op.recv(msglen), msg)

            # long message
            multiplier = 1024
            longmsg = [msg] * multiplier
            op, _ = algo.accept()
            ukijumuisha op:
                op.sendmsg_afalg(longmsg,
                                 op=socket.ALG_OP_ENCRYPT, iv=iv)
                enc = op.recv(msglen * multiplier)
            self.assertEqual(len(enc), msglen * multiplier)
            self.assertEqual(enc[:msglen], ciphertext)

            op, _ = algo.accept()
            ukijumuisha op:
                op.sendmsg_afalg([enc],
                                 op=socket.ALG_OP_DECRYPT, iv=iv)
                dec = op.recv(msglen * multiplier)
            self.assertEqual(len(dec), msglen * multiplier)
            self.assertEqual(dec, msg * multiplier)

    @support.requires_linux_version(4, 9)  # see issue29324
    eleza test_aead_aes_gcm(self):
        key = bytes.kutokahex('c939cc13397c1d37de6ae0e1cb7c423c')
        iv = bytes.kutokahex('b3d8cc017cbb89b39e0f67e2')
        plain = bytes.kutokahex('c3b3c41f113a31b73d9a5cd432103069')
        assoc = bytes.kutokahex('24825602bd12a984e0092d3e448eda5f')
        expected_ct = bytes.kutokahex('93fe7d9e9bfd10348a5606e5cafa7354')
        expected_tag = bytes.kutokahex('0032a1dc85f1c9786925a2e71d8272dd')

        taglen = len(expected_tag)
        assoclen = len(assoc)

        ukijumuisha self.create_alg('aead', 'gcm(aes)') kama algo:
            algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, key)
            algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_AEAD_AUTHSIZE,
                            Tupu, taglen)

            # send assoc, plain na tag buffer kwenye separate steps
            op, _ = algo.accept()
            ukijumuisha op:
                op.sendmsg_afalg(op=socket.ALG_OP_ENCRYPT, iv=iv,
                                 assoclen=assoclen, flags=socket.MSG_MORE)
                op.sendall(assoc, socket.MSG_MORE)
                op.sendall(plain)
                res = op.recv(assoclen + len(plain) + taglen)
                self.assertEqual(expected_ct, res[assoclen:-taglen])
                self.assertEqual(expected_tag, res[-taglen:])

            # now ukijumuisha msg
            op, _ = algo.accept()
            ukijumuisha op:
                msg = assoc + plain
                op.sendmsg_afalg([msg], op=socket.ALG_OP_ENCRYPT, iv=iv,
                                 assoclen=assoclen)
                res = op.recv(assoclen + len(plain) + taglen)
                self.assertEqual(expected_ct, res[assoclen:-taglen])
                self.assertEqual(expected_tag, res[-taglen:])

            # create anc data manually
            pack_uint32 = struct.Struct('I').pack
            op, _ = algo.accept()
            ukijumuisha op:
                msg = assoc + plain
                op.sendmsg(
                    [msg],
                    ([socket.SOL_ALG, socket.ALG_SET_OP, pack_uint32(socket.ALG_OP_ENCRYPT)],
                     [socket.SOL_ALG, socket.ALG_SET_IV, pack_uint32(len(iv)) + iv],
                     [socket.SOL_ALG, socket.ALG_SET_AEAD_ASSOCLEN, pack_uint32(assoclen)],
                    )
                )
                res = op.recv(len(msg) + taglen)
                self.assertEqual(expected_ct, res[assoclen:-taglen])
                self.assertEqual(expected_tag, res[-taglen:])

            # decrypt na verify
            op, _ = algo.accept()
            ukijumuisha op:
                msg = assoc + expected_ct + expected_tag
                op.sendmsg_afalg([msg], op=socket.ALG_OP_DECRYPT, iv=iv,
                                 assoclen=assoclen)
                res = op.recv(len(msg) - taglen)
                self.assertEqual(plain, res[assoclen:])

    @support.requires_linux_version(4, 3)  # see test_aes_cbc
    eleza test_drbg_pr_sha256(self):
        # deterministic random bit generator, prediction resistance, sha256
        ukijumuisha self.create_alg('rng', 'drbg_pr_sha256') kama algo:
            extra_seed = os.urandom(32)
            algo.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, extra_seed)
            op, _ = algo.accept()
            ukijumuisha op:
                rn = op.recv(32)
                self.assertEqual(len(rn), 32)

    eleza test_sendmsg_afalg_args(self):
        sock = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
        ukijumuisha sock:
            ukijumuisha self.assertRaises(TypeError):
                sock.sendmsg_afalg()

            ukijumuisha self.assertRaises(TypeError):
                sock.sendmsg_afalg(op=Tupu)

            ukijumuisha self.assertRaises(TypeError):
                sock.sendmsg_afalg(1)

            ukijumuisha self.assertRaises(TypeError):
                sock.sendmsg_afalg(op=socket.ALG_OP_ENCRYPT, assoclen=Tupu)

            ukijumuisha self.assertRaises(TypeError):
                sock.sendmsg_afalg(op=socket.ALG_OP_ENCRYPT, assoclen=-1)

    eleza test_length_restriction(self):
        # bpo-35050, off-by-one error kwenye length check
        sock = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
        self.addCleanup(sock.close)

        # salg_type[14]
        ukijumuisha self.assertRaises(FileNotFoundError):
            sock.bind(("t" * 13, "name"))
        ukijumuisha self.assertRaisesRegex(ValueError, "type too long"):
            sock.bind(("t" * 14, "name"))

        # salg_name[64]
        ukijumuisha self.assertRaises(FileNotFoundError):
            sock.bind(("type", "n" * 63))
        ukijumuisha self.assertRaisesRegex(ValueError, "name too long"):
            sock.bind(("type", "n" * 64))


@unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
kundi TestMSWindowsTCPFlags(unittest.TestCase):
    knownTCPFlags = {
                       # available since long time ago
                       'TCP_MAXSEG',
                       'TCP_NODELAY',
                       # available starting ukijumuisha Windows 10 1607
                       'TCP_FASTOPEN',
                       # available starting ukijumuisha Windows 10 1703
                       'TCP_KEEPCNT',
                       # available starting ukijumuisha Windows 10 1709
                       'TCP_KEEPIDLE',
                       'TCP_KEEPINTVL'
                       }

    eleza test_new_tcp_flags(self):
        provided = [s kila s kwenye dir(socket) ikiwa s.startswith('TCP')]
        unknown = [s kila s kwenye provided ikiwa s haiko kwenye self.knownTCPFlags]

        self.assertEqual([], unknown,
            "New TCP flags were discovered. See bpo-32394 kila more information")


kundi CreateServerTest(unittest.TestCase):

    eleza test_address(self):
        port = support.find_unused_port()
        ukijumuisha socket.create_server(("127.0.0.1", port)) kama sock:
            self.assertEqual(sock.getsockname()[0], "127.0.0.1")
            self.assertEqual(sock.getsockname()[1], port)
        ikiwa support.IPV6_ENABLED:
            ukijumuisha socket.create_server(("::1", port),
                                      family=socket.AF_INET6) kama sock:
                self.assertEqual(sock.getsockname()[0], "::1")
                self.assertEqual(sock.getsockname()[1], port)

    eleza test_family_and_type(self):
        ukijumuisha socket.create_server(("127.0.0.1", 0)) kama sock:
            self.assertEqual(sock.family, socket.AF_INET)
            self.assertEqual(sock.type, socket.SOCK_STREAM)
        ikiwa support.IPV6_ENABLED:
            ukijumuisha socket.create_server(("::1", 0), family=socket.AF_INET6) kama s:
                self.assertEqual(s.family, socket.AF_INET6)
                self.assertEqual(sock.type, socket.SOCK_STREAM)

    eleza test_reuse_port(self):
        ikiwa sio hasattr(socket, "SO_REUSEPORT"):
            ukijumuisha self.assertRaises(ValueError):
                socket.create_server(("localhost", 0), reuse_port=Kweli)
        isipokua:
            ukijumuisha socket.create_server(("localhost", 0)) kama sock:
                opt = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT)
                self.assertEqual(opt, 0)
            ukijumuisha socket.create_server(("localhost", 0), reuse_port=Kweli) kama sock:
                opt = sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT)
                self.assertNotEqual(opt, 0)

    @unittest.skipIf(not hasattr(_socket, 'IPPROTO_IPV6') or
                     sio hasattr(_socket, 'IPV6_V6ONLY'),
                     "IPV6_V6ONLY option sio supported")
    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test')
    eleza test_ipv6_only_default(self):
        ukijumuisha socket.create_server(("::1", 0), family=socket.AF_INET6) kama sock:
            assert sock.getsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY)

    @unittest.skipIf(not socket.has_dualstack_ipv6(),
                     "dualstack_ipv6 sio supported")
    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test')
    eleza test_dualstack_ipv6_family(self):
        ukijumuisha socket.create_server(("::1", 0), family=socket.AF_INET6,
                                  dualstack_ipv6=Kweli) kama sock:
            self.assertEqual(sock.family, socket.AF_INET6)


kundi CreateServerFunctionalTest(unittest.TestCase):
    timeout = 3

    eleza setUp(self):
        self.thread = Tupu

    eleza tearDown(self):
        ikiwa self.thread ni sio Tupu:
            self.thread.join(self.timeout)

    eleza echo_server(self, sock):
        eleza run(sock):
            ukijumuisha sock:
                conn, _ = sock.accept()
                ukijumuisha conn:
                    event.wait(self.timeout)
                    msg = conn.recv(1024)
                    ikiwa sio msg:
                        rudisha
                    conn.sendall(msg)

        event = threading.Event()
        sock.settimeout(self.timeout)
        self.thread = threading.Thread(target=run, args=(sock, ))
        self.thread.start()
        event.set()

    eleza echo_client(self, addr, family):
        ukijumuisha socket.socket(family=family) kama sock:
            sock.settimeout(self.timeout)
            sock.connect(addr)
            sock.sendall(b'foo')
            self.assertEqual(sock.recv(1024), b'foo')

    eleza test_tcp4(self):
        port = support.find_unused_port()
        ukijumuisha socket.create_server(("", port)) kama sock:
            self.echo_server(sock)
            self.echo_client(("127.0.0.1", port), socket.AF_INET)

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test')
    eleza test_tcp6(self):
        port = support.find_unused_port()
        ukijumuisha socket.create_server(("", port),
                                  family=socket.AF_INET6) kama sock:
            self.echo_server(sock)
            self.echo_client(("::1", port), socket.AF_INET6)

    # --- dual stack tests

    @unittest.skipIf(not socket.has_dualstack_ipv6(),
                     "dualstack_ipv6 sio supported")
    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test')
    eleza test_dual_stack_client_v4(self):
        port = support.find_unused_port()
        ukijumuisha socket.create_server(("", port), family=socket.AF_INET6,
                                  dualstack_ipv6=Kweli) kama sock:
            self.echo_server(sock)
            self.echo_client(("127.0.0.1", port), socket.AF_INET)

    @unittest.skipIf(not socket.has_dualstack_ipv6(),
                     "dualstack_ipv6 sio supported")
    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 required kila this test')
    eleza test_dual_stack_client_v6(self):
        port = support.find_unused_port()
        ukijumuisha socket.create_server(("", port), family=socket.AF_INET6,
                                  dualstack_ipv6=Kweli) kama sock:
            self.echo_server(sock)
            self.echo_client(("::1", port), socket.AF_INET6)


eleza test_main():
    tests = [GeneralModuleTests, BasicTCPTest, TCPCloserTest, TCPTimeoutTest,
             TestExceptions, BufferIOTest, BasicTCPTest2, BasicUDPTest,
             UDPTimeoutTest, CreateServerTest, CreateServerFunctionalTest]

    tests.extend([
        NonBlockingTCPTests,
        FileObjectClassTestCase,
        UnbufferedFileObjectClassTestCase,
        LineBufferedFileObjectClassTestCase,
        SmallBufferedFileObjectClassTestCase,
        UnicodeReadFileObjectClassTestCase,
        UnicodeWriteFileObjectClassTestCase,
        UnicodeReadWriteFileObjectClassTestCase,
        NetworkConnectionNoServer,
        NetworkConnectionAttributesTest,
        NetworkConnectionBehaviourTest,
        ContextManagersTest,
        InheritanceTest,
        NonblockConstantTest
    ])
    tests.append(BasicSocketPairTest)
    tests.append(TestUnixDomain)
    tests.append(TestLinuxAbstractNamespace)
    tests.extend([TIPCTest, TIPCThreadableTest])
    tests.extend([BasicCANTest, CANTest])
    tests.extend([BasicRDSTest, RDSTest])
    tests.append(LinuxKernelCryptoAPI)
    tests.append(BasicQIPCRTRTest)
    tests.extend([
        BasicVSOCKTest,
        ThreadedVSOCKSocketStreamTest,
    ])
    tests.extend([
        CmsgMacroTests,
        SendmsgUDPTest,
        RecvmsgUDPTest,
        RecvmsgIntoUDPTest,
        SendmsgUDP6Test,
        RecvmsgUDP6Test,
        RecvmsgRFC3542AncillaryUDP6Test,
        RecvmsgIntoRFC3542AncillaryUDP6Test,
        RecvmsgIntoUDP6Test,
        SendmsgTCPTest,
        RecvmsgTCPTest,
        RecvmsgIntoTCPTest,
        SendmsgSCTPStreamTest,
        RecvmsgSCTPStreamTest,
        RecvmsgIntoSCTPStreamTest,
        SendmsgUnixStreamTest,
        RecvmsgUnixStreamTest,
        RecvmsgIntoUnixStreamTest,
        RecvmsgSCMRightsStreamTest,
        RecvmsgIntoSCMRightsStreamTest,
        # These are slow when setitimer() ni sio available
        InterruptedRecvTimeoutTest,
        InterruptedSendTimeoutTest,
        TestSocketSharing,
        SendfileUsingSendTest,
        SendfileUsingSendfileTest,
    ])
    tests.append(TestMSWindowsTCPFlags)

    thread_info = support.threading_setup()
    support.run_unittest(*tests)
    support.threading_cleanup(*thread_info)

ikiwa __name__ == "__main__":
    test_main()
