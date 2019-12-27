# Wrapper module for _socket, providing some additional facilities
# implemented in Python.

"""\
This module provides socket operations and some related functions.
On Unix, it supports IP (Internet Protocol) and Unix domain sockets.
On other systems, it only supports IP. Functions specific for a
socket are available as methods of the socket object.

Functions:

socket() -- create a new socket object
socketpair() -- create a pair of new socket objects [*]
kutokafd() -- create a socket object kutoka an open file descriptor [*]
kutokashare() -- create a socket object kutoka data received kutoka socket.share() [*]
gethostname() -- rudisha the current hostname
gethostbyname() -- map a hostname to its IP number
gethostbyaddr() -- map an IP number or hostname to DNS info
getservbyname() -- map a service name and a protocol name to a port number
getprotobyname() -- map a protocol name (e.g. 'tcp') to a number
ntohs(), ntohl() -- convert 16, 32 bit int kutoka network to host byte order
htons(), htonl() -- convert 16, 32 bit int kutoka host to network byte order
inet_aton() -- convert IP addr string (123.45.67.89) to 32-bit packed format
inet_ntoa() -- convert 32-bit packed format IP to string (123.45.67.89)
socket.getdefaulttimeout() -- get the default timeout value
socket.setdefaulttimeout() -- set the default timeout value
create_connection() -- connects to an address, with an optional timeout and
                       optional source address.

 [*] not available on all platforms!

Special objects:

SocketType -- type object for socket objects
error -- exception raised for I/O errors
has_ipv6 -- boolean value indicating ikiwa IPv6 is supported

IntEnum constants:

AF_INET, AF_UNIX -- socket domains (first argument to socket() call)
SOCK_STREAM, SOCK_DGRAM, SOCK_RAW -- socket types (second argument)

Integer constants:

Many other constants may be defined; these may be used in calls to
the setsockopt() and getsockopt() methods.
"""

agiza _socket
kutoka _socket agiza *

agiza os, sys, io, selectors
kutoka enum agiza IntEnum, IntFlag

try:
    agiza errno
except ImportError:
    errno = None
EBADF = getattr(errno, 'EBADF', 9)
EAGAIN = getattr(errno, 'EAGAIN', 11)
EWOULDBLOCK = getattr(errno, 'EWOULDBLOCK', 11)

__all__ = ["kutokafd", "getfqdn", "create_connection", "create_server",
           "has_dualstack_ipv6", "AddressFamily", "SocketKind"]
__all__.extend(os._get_exports_list(_socket))

# Set up the socket.AF_* socket.SOCK_* constants as members of IntEnums for
# nicer string representations.
# Note that _socket only knows about the integer values. The public interface
# in this module understands the enums and translates them back kutoka integers
# where needed (e.g. .family property of a socket object).

IntEnum._convert_(
        'AddressFamily',
        __name__,
        lambda C: C.isupper() and C.startswith('AF_'))

IntEnum._convert_(
        'SocketKind',
        __name__,
        lambda C: C.isupper() and C.startswith('SOCK_'))

IntFlag._convert_(
        'MsgFlag',
        __name__,
        lambda C: C.isupper() and C.startswith('MSG_'))

IntFlag._convert_(
        'AddressInfo',
        __name__,
        lambda C: C.isupper() and C.startswith('AI_'))

_LOCALHOST    = '127.0.0.1'
_LOCALHOST_V6 = '::1'


eleza _intenum_converter(value, enum_klass):
    """Convert a numeric family value to an IntEnum member.

    If it's not a known member, rudisha the numeric value itself.
    """
    try:
        rudisha enum_klass(value)
    except ValueError:
        rudisha value

_realsocket = socket

# WSA error codes
ikiwa sys.platform.lower().startswith("win"):
    errorTab = {}
    errorTab[6] = "Specified event object handle is invalid."
    errorTab[8] = "Insufficient memory available."
    errorTab[87] = "One or more parameters are invalid."
    errorTab[995] = "Overlapped operation aborted."
    errorTab[996] = "Overlapped I/O event object not in signaled state."
    errorTab[997] = "Overlapped operation will complete later."
    errorTab[10004] = "The operation was interrupted."
    errorTab[10009] = "A bad file handle was passed."
    errorTab[10013] = "Permission denied."
    errorTab[10014] = "A fault occurred on the network??"  # WSAEFAULT
    errorTab[10022] = "An invalid operation was attempted."
    errorTab[10024] = "Too many open files."
    errorTab[10035] = "The socket operation would block"
    errorTab[10036] = "A blocking operation is already in progress."
    errorTab[10037] = "Operation already in progress."
    errorTab[10038] = "Socket operation on nonsocket."
    errorTab[10039] = "Destination address required."
    errorTab[10040] = "Message too long."
    errorTab[10041] = "Protocol wrong type for socket."
    errorTab[10042] = "Bad protocol option."
    errorTab[10043] = "Protocol not supported."
    errorTab[10044] = "Socket type not supported."
    errorTab[10045] = "Operation not supported."
    errorTab[10046] = "Protocol family not supported."
    errorTab[10047] = "Address family not supported by protocol family."
    errorTab[10048] = "The network address is in use."
    errorTab[10049] = "Cannot assign requested address."
    errorTab[10050] = "Network is down."
    errorTab[10051] = "Network is unreachable."
    errorTab[10052] = "Network dropped connection on reset."
    errorTab[10053] = "Software caused connection abort."
    errorTab[10054] = "The connection has been reset."
    errorTab[10055] = "No buffer space available."
    errorTab[10056] = "Socket is already connected."
    errorTab[10057] = "Socket is not connected."
    errorTab[10058] = "The network has been shut down."
    errorTab[10059] = "Too many references."
    errorTab[10060] = "The operation timed out."
    errorTab[10061] = "Connection refused."
    errorTab[10062] = "Cannot translate name."
    errorTab[10063] = "The name is too long."
    errorTab[10064] = "The host is down."
    errorTab[10065] = "The host is unreachable."
    errorTab[10066] = "Directory not empty."
    errorTab[10067] = "Too many processes."
    errorTab[10068] = "User quota exceeded."
    errorTab[10069] = "Disk quota exceeded."
    errorTab[10070] = "Stale file handle reference."
    errorTab[10071] = "Item is remote."
    errorTab[10091] = "Network subsystem is unavailable."
    errorTab[10092] = "Winsock.dll version out of range."
    errorTab[10093] = "Successful WSAStartup not yet performed."
    errorTab[10101] = "Graceful shutdown in progress."
    errorTab[10102] = "No more results kutoka WSALookupServiceNext."
    errorTab[10103] = "Call has been canceled."
    errorTab[10104] = "Procedure call table is invalid."
    errorTab[10105] = "Service provider is invalid."
    errorTab[10106] = "Service provider failed to initialize."
    errorTab[10107] = "System call failure."
    errorTab[10108] = "Service not found."
    errorTab[10109] = "Class type not found."
    errorTab[10110] = "No more results kutoka WSALookupServiceNext."
    errorTab[10111] = "Call was canceled."
    errorTab[10112] = "Database query was refused."
    errorTab[11001] = "Host not found."
    errorTab[11002] = "Nonauthoritative host not found."
    errorTab[11003] = "This is a nonrecoverable error."
    errorTab[11004] = "Valid name, no data record requested type."
    errorTab[11005] = "QoS receivers."
    errorTab[11006] = "QoS senders."
    errorTab[11007] = "No QoS senders."
    errorTab[11008] = "QoS no receivers."
    errorTab[11009] = "QoS request confirmed."
    errorTab[11010] = "QoS admission error."
    errorTab[11011] = "QoS policy failure."
    errorTab[11012] = "QoS bad style."
    errorTab[11013] = "QoS bad object."
    errorTab[11014] = "QoS traffic control error."
    errorTab[11015] = "QoS generic error."
    errorTab[11016] = "QoS service type error."
    errorTab[11017] = "QoS flowspec error."
    errorTab[11018] = "Invalid QoS provider buffer."
    errorTab[11019] = "Invalid QoS filter style."
    errorTab[11020] = "Invalid QoS filter style."
    errorTab[11021] = "Incorrect QoS filter count."
    errorTab[11022] = "Invalid QoS object length."
    errorTab[11023] = "Incorrect QoS flow count."
    errorTab[11024] = "Unrecognized QoS object."
    errorTab[11025] = "Invalid QoS policy object."
    errorTab[11026] = "Invalid QoS flow descriptor."
    errorTab[11027] = "Invalid QoS provider-specific flowspec."
    errorTab[11028] = "Invalid QoS provider-specific filterspec."
    errorTab[11029] = "Invalid QoS shape discard mode object."
    errorTab[11030] = "Invalid QoS shaping rate object."
    errorTab[11031] = "Reserved policy QoS element type."
    __all__.append("errorTab")


kundi _GiveupOnSendfile(Exception): pass


kundi socket(_socket.socket):

    """A subkundi of _socket.socket adding the makefile() method."""

    __slots__ = ["__weakref__", "_io_refs", "_closed"]

    eleza __init__(self, family=-1, type=-1, proto=-1, fileno=None):
        # For user code address family and type values are IntEnum members, but
        # for the underlying _socket.socket they're just integers. The
        # constructor of _socket.socket converts the given argument to an
        # integer automatically.
        ikiwa fileno is None:
            ikiwa family == -1:
                family = AF_INET
            ikiwa type == -1:
                type = SOCK_STREAM
            ikiwa proto == -1:
                proto = 0
        _socket.socket.__init__(self, family, type, proto, fileno)
        self._io_refs = 0
        self._closed = False

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        ikiwa not self._closed:
            self.close()

    eleza __repr__(self):
        """Wrap __repr__() to reveal the real kundi name and socket
        address(es).
        """
        closed = getattr(self, '_closed', False)
        s = "<%s.%s%s fd=%i, family=%s, type=%s, proto=%i" \
            % (self.__class__.__module__,
               self.__class__.__qualname__,
               " [closed]" ikiwa closed else "",
               self.fileno(),
               self.family,
               self.type,
               self.proto)
        ikiwa not closed:
            try:
                laddr = self.getsockname()
                ikiwa laddr:
                    s += ", laddr=%s" % str(laddr)
            except error:
                pass
            try:
                raddr = self.getpeername()
                ikiwa raddr:
                    s += ", raddr=%s" % str(raddr)
            except error:
                pass
        s += '>'
        rudisha s

    eleza __getstate__(self):
        raise TypeError(f"cannot pickle {self.__class__.__name__!r} object")

    eleza dup(self):
        """dup() -> socket object

        Duplicate the socket. Return a new socket object connected to the same
        system resource. The new socket is non-inheritable.
        """
        fd = dup(self.fileno())
        sock = self.__class__(self.family, self.type, self.proto, fileno=fd)
        sock.settimeout(self.gettimeout())
        rudisha sock

    eleza accept(self):
        """accept() -> (socket object, address info)

        Wait for an incoming connection.  Return a new socket
        representing the connection, and the address of the client.
        For IP sockets, the address info is a pair (hostaddr, port).
        """
        fd, addr = self._accept()
        sock = socket(self.family, self.type, self.proto, fileno=fd)
        # Issue #7995: ikiwa no default timeout is set and the listening
        # socket had a (non-zero) timeout, force the new socket in blocking
        # mode to override platform-specific socket flags inheritance.
        ikiwa getdefaulttimeout() is None and self.gettimeout():
            sock.setblocking(True)
        rudisha sock, addr

    eleza makefile(self, mode="r", buffering=None, *,
                 encoding=None, errors=None, newline=None):
        """makefile(...) -> an I/O stream connected to the socket

        The arguments are as for io.open() after the filename, except the only
        supported mode values are 'r' (default), 'w' and 'b'.
        """
        # XXX refactor to share code?
        ikiwa not set(mode) <= {"r", "w", "b"}:
            raise ValueError("invalid mode %r (only r, w, b allowed)" % (mode,))
        writing = "w" in mode
        reading = "r" in mode or not writing
        assert reading or writing
        binary = "b" in mode
        rawmode = ""
        ikiwa reading:
            rawmode += "r"
        ikiwa writing:
            rawmode += "w"
        raw = SocketIO(self, rawmode)
        self._io_refs += 1
        ikiwa buffering is None:
            buffering = -1
        ikiwa buffering < 0:
            buffering = io.DEFAULT_BUFFER_SIZE
        ikiwa buffering == 0:
            ikiwa not binary:
                raise ValueError("unbuffered streams must be binary")
            rudisha raw
        ikiwa reading and writing:
            buffer = io.BufferedRWPair(raw, raw, buffering)
        elikiwa reading:
            buffer = io.BufferedReader(raw, buffering)
        else:
            assert writing
            buffer = io.BufferedWriter(raw, buffering)
        ikiwa binary:
            rudisha buffer
        text = io.TextIOWrapper(buffer, encoding, errors, newline)
        text.mode = mode
        rudisha text

    ikiwa hasattr(os, 'sendfile'):

        eleza _sendfile_use_sendfile(self, file, offset=0, count=None):
            self._check_sendfile_params(file, offset, count)
            sockno = self.fileno()
            try:
                fileno = file.fileno()
            except (AttributeError, io.UnsupportedOperation) as err:
                raise _GiveupOnSendfile(err)  # not a regular file
            try:
                fsize = os.fstat(fileno).st_size
            except OSError as err:
                raise _GiveupOnSendfile(err)  # not a regular file
            ikiwa not fsize:
                rudisha 0  # empty file
            # Truncate to 1GiB to avoid OverflowError, see bpo-38319.
            blocksize = min(count or fsize, 2 ** 30)
            timeout = self.gettimeout()
            ikiwa timeout == 0:
                raise ValueError("non-blocking sockets are not supported")
            # poll/select have the advantage of not requiring any
            # extra file descriptor, contrarily to epoll/kqueue
            # (also, they require a single syscall).
            ikiwa hasattr(selectors, 'PollSelector'):
                selector = selectors.PollSelector()
            else:
                selector = selectors.SelectSelector()
            selector.register(sockno, selectors.EVENT_WRITE)

            total_sent = 0
            # localize variable access to minimize overhead
            selector_select = selector.select
            os_sendfile = os.sendfile
            try:
                while True:
                    ikiwa timeout and not selector_select(timeout):
                        raise _socket.timeout('timed out')
                    ikiwa count:
                        blocksize = count - total_sent
                        ikiwa blocksize <= 0:
                            break
                    try:
                        sent = os_sendfile(sockno, fileno, offset, blocksize)
                    except BlockingIOError:
                        ikiwa not timeout:
                            # Block until the socket is ready to send some
                            # data; avoids hogging CPU resources.
                            selector_select()
                        continue
                    except OSError as err:
                        ikiwa total_sent == 0:
                            # We can get here for different reasons, the main
                            # one being 'file' is not a regular mmap(2)-like
                            # file, in which case we'll fall back on using
                            # plain send().
                            raise _GiveupOnSendfile(err)
                        raise err kutoka None
                    else:
                        ikiwa sent == 0:
                            break  # EOF
                        offset += sent
                        total_sent += sent
                rudisha total_sent
            finally:
                ikiwa total_sent > 0 and hasattr(file, 'seek'):
                    file.seek(offset)
    else:
        eleza _sendfile_use_sendfile(self, file, offset=0, count=None):
            raise _GiveupOnSendfile(
                "os.sendfile() not available on this platform")

    eleza _sendfile_use_send(self, file, offset=0, count=None):
        self._check_sendfile_params(file, offset, count)
        ikiwa self.gettimeout() == 0:
            raise ValueError("non-blocking sockets are not supported")
        ikiwa offset:
            file.seek(offset)
        blocksize = min(count, 8192) ikiwa count else 8192
        total_sent = 0
        # localize variable access to minimize overhead
        file_read = file.read
        sock_send = self.send
        try:
            while True:
                ikiwa count:
                    blocksize = min(count - total_sent, blocksize)
                    ikiwa blocksize <= 0:
                        break
                data = memoryview(file_read(blocksize))
                ikiwa not data:
                    break  # EOF
                while True:
                    try:
                        sent = sock_send(data)
                    except BlockingIOError:
                        continue
                    else:
                        total_sent += sent
                        ikiwa sent < len(data):
                            data = data[sent:]
                        else:
                            break
            rudisha total_sent
        finally:
            ikiwa total_sent > 0 and hasattr(file, 'seek'):
                file.seek(offset + total_sent)

    eleza _check_sendfile_params(self, file, offset, count):
        ikiwa 'b' not in getattr(file, 'mode', 'b'):
            raise ValueError("file should be opened in binary mode")
        ikiwa not self.type & SOCK_STREAM:
            raise ValueError("only SOCK_STREAM type sockets are supported")
        ikiwa count is not None:
            ikiwa not isinstance(count, int):
                raise TypeError(
                    "count must be a positive integer (got {!r})".format(count))
            ikiwa count <= 0:
                raise ValueError(
                    "count must be a positive integer (got {!r})".format(count))

    eleza sendfile(self, file, offset=0, count=None):
        """sendfile(file[, offset[, count]]) -> sent

        Send a file until EOF is reached by using high-performance
        os.sendfile() and rudisha the total number of bytes which
        were sent.
        *file* must be a regular file object opened in binary mode.
        If os.sendfile() is not available (e.g. Windows) or file is
        not a regular file socket.send() will be used instead.
        *offset* tells kutoka where to start reading the file.
        If specified, *count* is the total number of bytes to transmit
        as opposed to sending the file until EOF is reached.
        File position is updated on rudisha or also in case of error in
        which case file.tell() can be used to figure out the number of
        bytes which were sent.
        The socket must be of SOCK_STREAM type.
        Non-blocking sockets are not supported.
        """
        try:
            rudisha self._sendfile_use_sendfile(file, offset, count)
        except _GiveupOnSendfile:
            rudisha self._sendfile_use_send(file, offset, count)

    eleza _decref_socketios(self):
        ikiwa self._io_refs > 0:
            self._io_refs -= 1
        ikiwa self._closed:
            self.close()

    eleza _real_close(self, _ss=_socket.socket):
        # This function should not reference any globals. See issue #808164.
        _ss.close(self)

    eleza close(self):
        # This function should not reference any globals. See issue #808164.
        self._closed = True
        ikiwa self._io_refs <= 0:
            self._real_close()

    eleza detach(self):
        """detach() -> file descriptor

        Close the socket object without closing the underlying file descriptor.
        The object cannot be used after this call, but the file descriptor
        can be reused for other purposes.  The file descriptor is returned.
        """
        self._closed = True
        rudisha super().detach()

    @property
    eleza family(self):
        """Read-only access to the address family for this socket.
        """
        rudisha _intenum_converter(super().family, AddressFamily)

    @property
    eleza type(self):
        """Read-only access to the socket type.
        """
        rudisha _intenum_converter(super().type, SocketKind)

    ikiwa os.name == 'nt':
        eleza get_inheritable(self):
            rudisha os.get_handle_inheritable(self.fileno())
        eleza set_inheritable(self, inheritable):
            os.set_handle_inheritable(self.fileno(), inheritable)
    else:
        eleza get_inheritable(self):
            rudisha os.get_inheritable(self.fileno())
        eleza set_inheritable(self, inheritable):
            os.set_inheritable(self.fileno(), inheritable)
    get_inheritable.__doc__ = "Get the inheritable flag of the socket"
    set_inheritable.__doc__ = "Set the inheritable flag of the socket"

eleza kutokafd(fd, family, type, proto=0):
    """ kutokafd(fd, family, type[, proto]) -> socket object

    Create a socket object kutoka a duplicate of the given file
    descriptor.  The remaining arguments are the same as for socket().
    """
    nfd = dup(fd)
    rudisha socket(family, type, proto, nfd)

ikiwa hasattr(_socket.socket, "share"):
    eleza kutokashare(info):
        """ kutokashare(info) -> socket object

        Create a socket object kutoka the bytes object returned by
        socket.share(pid).
        """
        rudisha socket(0, 0, 0, info)
    __all__.append("kutokashare")

ikiwa hasattr(_socket, "socketpair"):

    eleza socketpair(family=None, type=SOCK_STREAM, proto=0):
        """socketpair([family[, type[, proto]]]) -> (socket object, socket object)

        Create a pair of socket objects kutoka the sockets returned by the platform
        socketpair() function.
        The arguments are the same as for socket() except the default family is
        AF_UNIX ikiwa defined on the platform; otherwise, the default is AF_INET.
        """
        ikiwa family is None:
            try:
                family = AF_UNIX
            except NameError:
                family = AF_INET
        a, b = _socket.socketpair(family, type, proto)
        a = socket(family, type, proto, a.detach())
        b = socket(family, type, proto, b.detach())
        rudisha a, b

else:

    # Origin: https://gist.github.com/4325783, by Geert Jansen.  Public domain.
    eleza socketpair(family=AF_INET, type=SOCK_STREAM, proto=0):
        ikiwa family == AF_INET:
            host = _LOCALHOST
        elikiwa family == AF_INET6:
            host = _LOCALHOST_V6
        else:
            raise ValueError("Only AF_INET and AF_INET6 socket address families "
                             "are supported")
        ikiwa type != SOCK_STREAM:
            raise ValueError("Only SOCK_STREAM socket type is supported")
        ikiwa proto != 0:
            raise ValueError("Only protocol zero is supported")

        # We create a connected TCP socket. Note the trick with
        # setblocking(False) that prevents us kutoka having to create a thread.
        lsock = socket(family, type, proto)
        try:
            lsock.bind((host, 0))
            lsock.listen()
            # On IPv6, ignore flow_info and scope_id
            addr, port = lsock.getsockname()[:2]
            csock = socket(family, type, proto)
            try:
                csock.setblocking(False)
                try:
                    csock.connect((addr, port))
                except (BlockingIOError, InterruptedError):
                    pass
                csock.setblocking(True)
                ssock, _ = lsock.accept()
            except:
                csock.close()
                raise
        finally:
            lsock.close()
        rudisha (ssock, csock)
    __all__.append("socketpair")

socketpair.__doc__ = """socketpair([family[, type[, proto]]]) -> (socket object, socket object)
Create a pair of socket objects kutoka the sockets returned by the platform
socketpair() function.
The arguments are the same as for socket() except the default family is AF_UNIX
ikiwa defined on the platform; otherwise, the default is AF_INET.
"""

_blocking_errnos = { EAGAIN, EWOULDBLOCK }

kundi SocketIO(io.RawIOBase):

    """Raw I/O implementation for stream sockets.

    This kundi supports the makefile() method on sockets.  It provides
    the raw I/O interface on top of a socket object.
    """

    # One might wonder why not let FileIO do the job instead.  There are two
    # main reasons why FileIO is not adapted:
    # - it wouldn't work under Windows (where you can't used read() and
    #   write() on a socket handle)
    # - it wouldn't work with socket timeouts (FileIO would ignore the
    #   timeout and consider the socket non-blocking)

    # XXX More docs

    eleza __init__(self, sock, mode):
        ikiwa mode not in ("r", "w", "rw", "rb", "wb", "rwb"):
            raise ValueError("invalid mode: %r" % mode)
        io.RawIOBase.__init__(self)
        self._sock = sock
        ikiwa "b" not in mode:
            mode += "b"
        self._mode = mode
        self._reading = "r" in mode
        self._writing = "w" in mode
        self._timeout_occurred = False

    eleza readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.

        If *b* is non-empty, a 0 rudisha value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        ikiwa self._timeout_occurred:
            raise OSError("cannot read kutoka timed out object")
        while True:
            try:
                rudisha self._sock.recv_into(b)
            except timeout:
                self._timeout_occurred = True
                raise
            except error as e:
                ikiwa e.args[0] in _blocking_errnos:
                    rudisha None
                raise

    eleza write(self, b):
        """Write the given bytes or bytearray object *b* to the socket
        and rudisha the number of bytes written.  This can be less than
        len(b) ikiwa not all data could be written.  If the socket is
        non-blocking and no bytes could be written None is returned.
        """
        self._checkClosed()
        self._checkWritable()
        try:
            rudisha self._sock.send(b)
        except error as e:
            # XXX what about EINTR?
            ikiwa e.args[0] in _blocking_errnos:
                rudisha None
            raise

    eleza readable(self):
        """True ikiwa the SocketIO is open for reading.
        """
        ikiwa self.closed:
            raise ValueError("I/O operation on closed socket.")
        rudisha self._reading

    eleza writable(self):
        """True ikiwa the SocketIO is open for writing.
        """
        ikiwa self.closed:
            raise ValueError("I/O operation on closed socket.")
        rudisha self._writing

    eleza seekable(self):
        """True ikiwa the SocketIO is open for seeking.
        """
        ikiwa self.closed:
            raise ValueError("I/O operation on closed socket.")
        rudisha super().seekable()

    eleza fileno(self):
        """Return the file descriptor of the underlying socket.
        """
        self._checkClosed()
        rudisha self._sock.fileno()

    @property
    eleza name(self):
        ikiwa not self.closed:
            rudisha self.fileno()
        else:
            rudisha -1

    @property
    eleza mode(self):
        rudisha self._mode

    eleza close(self):
        """Close the SocketIO object.  This doesn't close the underlying
        socket, except ikiwa all references to it have disappeared.
        """
        ikiwa self.closed:
            return
        io.RawIOBase.close(self)
        self._sock._decref_socketios()
        self._sock = None


eleza getfqdn(name=''):
    """Get fully qualified domain name kutoka name.

    An empty argument is interpreted as meaning the local host.

    First the hostname returned by gethostbyaddr() is checked, then
    possibly existing aliases. In case no FQDN is available, hostname
    kutoka gethostname() is returned.
    """
    name = name.strip()
    ikiwa not name or name == '0.0.0.0':
        name = gethostname()
    try:
        hostname, aliases, ipaddrs = gethostbyaddr(name)
    except error:
        pass
    else:
        aliases.insert(0, hostname)
        for name in aliases:
            ikiwa '.' in name:
                break
        else:
            name = hostname
    rudisha name


_GLOBAL_DEFAULT_TIMEOUT = object()

eleza create_connection(address, timeout=_GLOBAL_DEFAULT_TIMEOUT,
                      source_address=None):
    """Connect to *address* and rudisha the socket object.

    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) and rudisha the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* is supplied, the
    global default timeout setting returned by :func:`getdefaulttimeout`
    is used.  If *source_address* is set it must be a tuple of (host, port)
    for the socket to bind as a source address before making the connection.
    A host of '' or port 0 tells the OS to use the default.
    """

    host, port = address
    err = None
    for res in getaddrinfo(host, port, 0, SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket(af, socktype, proto)
            ikiwa timeout is not _GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            ikiwa source_address:
                sock.bind(source_address)
            sock.connect(sa)
            # Break explicitly a reference cycle
            err = None
            rudisha sock

        except error as _:
            err = _
            ikiwa sock is not None:
                sock.close()

    ikiwa err is not None:
        raise err
    else:
        raise error("getaddrinfo returns an empty list")


eleza has_dualstack_ipv6():
    """Return True ikiwa the platform supports creating a SOCK_STREAM socket
    which can handle both AF_INET and AF_INET6 (IPv4 / IPv6) connections.
    """
    ikiwa not has_ipv6 \
            or not hasattr(_socket, 'IPPROTO_IPV6') \
            or not hasattr(_socket, 'IPV6_V6ONLY'):
        rudisha False
    try:
        with socket(AF_INET6, SOCK_STREAM) as sock:
            sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)
            rudisha True
    except error:
        rudisha False


eleza create_server(address, *, family=AF_INET, backlog=None, reuse_port=False,
                  dualstack_ipv6=False):
    """Convenience function which creates a SOCK_STREAM type socket
    bound to *address* (a 2-tuple (host, port)) and rudisha the socket
    object.

    *family* should be either AF_INET or AF_INET6.
    *backlog* is the queue size passed to socket.listen().
    *reuse_port* dictates whether to use the SO_REUSEPORT socket option.
    *dualstack_ipv6*: ikiwa true and the platform supports it, it will
    create an AF_INET6 socket able to accept both IPv4 or IPv6
    connections. When false it will explicitly disable this option on
    platforms that enable it by default (e.g. Linux).

    >>> with create_server((None, 8000)) as server:
    ...     while True:
    ...         conn, addr = server.accept()
    ...         # handle new connection
    """
    ikiwa reuse_port and not hasattr(_socket, "SO_REUSEPORT"):
        raise ValueError("SO_REUSEPORT not supported on this platform")
    ikiwa dualstack_ipv6:
        ikiwa not has_dualstack_ipv6():
            raise ValueError("dualstack_ipv6 not supported on this platform")
        ikiwa family != AF_INET6:
            raise ValueError("dualstack_ipv6 requires AF_INET6 family")
    sock = socket(family, SOCK_STREAM)
    try:
        # Note about Windows. We don't set SO_REUSEADDR because:
        # 1) It's unnecessary: bind() will succeed even in case of a
        # previous closed socket on the same address and still in
        # TIME_WAIT state.
        # 2) If set, another socket is free to bind() on the same
        # address, effectively preventing this one kutoka accepting
        # connections. Also, it may set the process in a state where
        # it'll no longer respond to any signals or graceful kills.
        # See: msdn2.microsoft.com/en-us/library/ms740621(VS.85).aspx
        ikiwa os.name not in ('nt', 'cygwin') and \
                hasattr(_socket, 'SO_REUSEADDR'):
            try:
                sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            except error:
                # Fail later on bind(), for platforms which may not
                # support this option.
                pass
        ikiwa reuse_port:
            sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        ikiwa has_ipv6 and family == AF_INET6:
            ikiwa dualstack_ipv6:
                sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)
            elikiwa hasattr(_socket, "IPV6_V6ONLY") and \
                    hasattr(_socket, "IPPROTO_IPV6"):
                sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 1)
        try:
            sock.bind(address)
        except error as err:
            msg = '%s (while attempting to bind on address %r)' % \
                (err.strerror, address)
            raise error(err.errno, msg) kutoka None
        ikiwa backlog is None:
            sock.listen()
        else:
            sock.listen(backlog)
        rudisha sock
    except error:
        sock.close()
        raise


eleza getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """Resolve host and port into list of address info entries.

    Translate the host/port argument into a sequence of 5-tuples that contain
    all the necessary arguments for creating a socket connected to that service.
    host is a domain name, a string representation of an IPv4/v6 address or
    None. port is a string service name such as 'http', a numeric port number or
    None. By passing None as the value of host and port, you can pass NULL to
    the underlying C API.

    The family, type and proto arguments can be optionally specified in order to
    narrow the list of addresses returned. Passing zero as a value for each of
    these arguments selects the full range of results.
    """
    # We override this function since we want to translate the numeric family
    # and socket type values to enum constants.
    addrlist = []
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
        af, socktype, proto, canonname, sa = res
        addrlist.append((_intenum_converter(af, AddressFamily),
                         _intenum_converter(socktype, SocketKind),
                         proto, canonname, sa))
    rudisha addrlist
