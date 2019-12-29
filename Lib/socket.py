# Wrapper module kila _socket, providing some additional facilities
# implemented kwenye Python.

"""\
This module provides socket operations na some related functions.
On Unix, it supports IP (Internet Protocol) na Unix domain sockets.
On other systems, it only supports IP. Functions specific kila a
socket are available kama methods of the socket object.

Functions:

socket() -- create a new socket object
socketpair() -- create a pair of new socket objects [*]
kutokafd() -- create a socket object kutoka an open file descriptor [*]
kutokashare() -- create a socket object kutoka data received kutoka socket.share() [*]
gethostname() -- rudisha the current hostname
gethostbyname() -- map a hostname to its IP number
gethostbyaddr() -- map an IP number ama hostname to DNS info
getservbyname() -- map a service name na a protocol name to a port number
getprotobyname() -- map a protocol name (e.g. 'tcp') to a number
ntohs(), ntohl() -- convert 16, 32 bit int kutoka network to host byte order
htons(), htonl() -- convert 16, 32 bit int kutoka host to network byte order
inet_aton() -- convert IP addr string (123.45.67.89) to 32-bit packed format
inet_ntoa() -- convert 32-bit packed format IP to string (123.45.67.89)
socket.getdefaulttimeout() -- get the default timeout value
socket.setdefaulttimeout() -- set the default timeout value
create_connection() -- connects to an address, with an optional timeout and
                       optional source address.

 [*] sio available on all platforms!

Special objects:

SocketType -- type object kila socket objects
error -- exception ashiriad kila I/O errors
has_ipv6 -- boolean value indicating ikiwa IPv6 ni supported

IntEnum constants:

AF_INET, AF_UNIX -- socket domains (first argument to socket() call)
SOCK_STREAM, SOCK_DGRAM, SOCK_RAW -- socket types (second argument)

Integer constants:

Many other constants may be defined; these may be used kwenye calls to
the setsockopt() na getsockopt() methods.
"""

agiza _socket
kutoka _socket agiza *

agiza os, sys, io, selectors
kutoka enum agiza IntEnum, IntFlag

jaribu:
    agiza errno
tatizo ImportError:
    errno = Tupu
EBADF = getattr(errno, 'EBADF', 9)
EAGAIN = getattr(errno, 'EAGAIN', 11)
EWOULDBLOCK = getattr(errno, 'EWOULDBLOCK', 11)

__all__ = ["kutokafd", "getfqdn", "create_connection", "create_server",
           "has_dualstack_ipv6", "AddressFamily", "SocketKind"]
__all__.extend(os._get_exports_list(_socket))

# Set up the socket.AF_* socket.SOCK_* constants kama members of IntEnums for
# nicer string representations.
# Note that _socket only knows about the integer values. The public interface
# kwenye this module understands the enums na translates them back kutoka integers
# where needed (e.g. .family property of a socket object).

IntEnum._convert_(
        'AddressFamily',
        __name__,
        lambda C: C.isupper() na C.startswith('AF_'))

IntEnum._convert_(
        'SocketKind',
        __name__,
        lambda C: C.isupper() na C.startswith('SOCK_'))

IntFlag._convert_(
        'MsgFlag',
        __name__,
        lambda C: C.isupper() na C.startswith('MSG_'))

IntFlag._convert_(
        'AddressInfo',
        __name__,
        lambda C: C.isupper() na C.startswith('AI_'))

_LOCALHOST    = '127.0.0.1'
_LOCALHOST_V6 = '::1'


eleza _intenum_converter(value, enum_klass):
    """Convert a numeric family value to an IntEnum member.

    If it's sio a known member, rudisha the numeric value itself.
    """
    jaribu:
        rudisha enum_klass(value)
    tatizo ValueError:
        rudisha value

_realsocket = socket

# WSA error codes
ikiwa sys.platform.lower().startswith("win"):
    errorTab = {}
    errorTab[6] = "Specified event object handle ni invalid."
    errorTab[8] = "Insufficient memory available."
    errorTab[87] = "One ama more parameters are invalid."
    errorTab[995] = "Overlapped operation aborted."
    errorTab[996] = "Overlapped I/O event object haiko kwenye signaled state."
    errorTab[997] = "Overlapped operation will complete later."
    errorTab[10004] = "The operation was interrupted."
    errorTab[10009] = "A bad file handle was pitaed."
    errorTab[10013] = "Permission denied."
    errorTab[10014] = "A fault occurred on the network??"  # WSAEFAULT
    errorTab[10022] = "An invalid operation was attempted."
    errorTab[10024] = "Too many open files."
    errorTab[10035] = "The socket operation would block"
    errorTab[10036] = "A blocking operation ni already kwenye progress."
    errorTab[10037] = "Operation already kwenye progress."
    errorTab[10038] = "Socket operation on nonsocket."
    errorTab[10039] = "Destination address required."
    errorTab[10040] = "Message too long."
    errorTab[10041] = "Protocol wrong type kila socket."
    errorTab[10042] = "Bad protocol option."
    errorTab[10043] = "Protocol sio supported."
    errorTab[10044] = "Socket type sio supported."
    errorTab[10045] = "Operation sio supported."
    errorTab[10046] = "Protocol family sio supported."
    errorTab[10047] = "Address family sio supported by protocol family."
    errorTab[10048] = "The network address ni kwenye use."
    errorTab[10049] = "Cannot assign requested address."
    errorTab[10050] = "Network ni down."
    errorTab[10051] = "Network ni unreachable."
    errorTab[10052] = "Network dropped connection on reset."
    errorTab[10053] = "Software caused connection abort."
    errorTab[10054] = "The connection has been reset."
    errorTab[10055] = "No buffer space available."
    errorTab[10056] = "Socket ni already connected."
    errorTab[10057] = "Socket ni sio connected."
    errorTab[10058] = "The network has been shut down."
    errorTab[10059] = "Too many references."
    errorTab[10060] = "The operation timed out."
    errorTab[10061] = "Connection refused."
    errorTab[10062] = "Cannot translate name."
    errorTab[10063] = "The name ni too long."
    errorTab[10064] = "The host ni down."
    errorTab[10065] = "The host ni unreachable."
    errorTab[10066] = "Directory sio empty."
    errorTab[10067] = "Too many processes."
    errorTab[10068] = "User quota exceeded."
    errorTab[10069] = "Disk quota exceeded."
    errorTab[10070] = "Stale file handle reference."
    errorTab[10071] = "Item ni remote."
    errorTab[10091] = "Network subsystem ni unavailable."
    errorTab[10092] = "Winsock.dll version out of range."
    errorTab[10093] = "Successful WSAStartup sio yet performed."
    errorTab[10101] = "Graceful shutdown kwenye progress."
    errorTab[10102] = "No more results kutoka WSALookupServiceNext."
    errorTab[10103] = "Call has been canceled."
    errorTab[10104] = "Procedure call table ni invalid."
    errorTab[10105] = "Service provider ni invalid."
    errorTab[10106] = "Service provider failed to initialize."
    errorTab[10107] = "System call failure."
    errorTab[10108] = "Service sio found."
    errorTab[10109] = "Class type sio found."
    errorTab[10110] = "No more results kutoka WSALookupServiceNext."
    errorTab[10111] = "Call was canceled."
    errorTab[10112] = "Database query was refused."
    errorTab[11001] = "Host sio found."
    errorTab[11002] = "Nonauthoritative host sio found."
    errorTab[11003] = "This ni a nonrecoverable error."
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


kundi _GiveupOnSendfile(Exception): pita


kundi socket(_socket.socket):

    """A subkundi of _socket.socket adding the makefile() method."""

    __slots__ = ["__weakref__", "_io_refs", "_closed"]

    eleza __init__(self, family=-1, type=-1, proto=-1, fileno=Tupu):
        # For user code address family na type values are IntEnum members, but
        # kila the underlying _socket.socket they're just integers. The
        # constructor of _socket.socket converts the given argument to an
        # integer automatically.
        ikiwa fileno ni Tupu:
            ikiwa family == -1:
                family = AF_INET
            ikiwa type == -1:
                type = SOCK_STREAM
            ikiwa proto == -1:
                proto = 0
        _socket.socket.__init__(self, family, type, proto, fileno)
        self._io_refs = 0
        self._closed = Uongo

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        ikiwa sio self._closed:
            self.close()

    eleza __repr__(self):
        """Wrap __repr__() to reveal the real kundi name na socket
        address(es).
        """
        closed = getattr(self, '_closed', Uongo)
        s = "<%s.%s%s fd=%i, family=%s, type=%s, proto=%i" \
            % (self.__class__.__module__,
               self.__class__.__qualname__,
               " [closed]" ikiwa closed else "",
               self.fileno(),
               self.family,
               self.type,
               self.proto)
        ikiwa sio closed:
            jaribu:
                laddr = self.getsockname()
                ikiwa laddr:
                    s += ", laddr=%s" % str(laddr)
            tatizo error:
                pita
            jaribu:
                raddr = self.getpeername()
                ikiwa raddr:
                    s += ", raddr=%s" % str(raddr)
            tatizo error:
                pita
        s += '>'
        rudisha s

    eleza __getstate__(self):
        ashiria TypeError(f"cannot pickle {self.__class__.__name__!r} object")

    eleza dup(self):
        """dup() -> socket object

        Duplicate the socket. Return a new socket object connected to the same
        system resource. The new socket ni non-inheritable.
        """
        fd = dup(self.fileno())
        sock = self.__class__(self.family, self.type, self.proto, fileno=fd)
        sock.settimeout(self.gettimeout())
        rudisha sock

    eleza accept(self):
        """accept() -> (socket object, address info)

        Wait kila an incoming connection.  Return a new socket
        representing the connection, na the address of the client.
        For IP sockets, the address info ni a pair (hostaddr, port).
        """
        fd, addr = self._accept()
        sock = socket(self.family, self.type, self.proto, fileno=fd)
        # Issue #7995: ikiwa no default timeout ni set na the listening
        # socket had a (non-zero) timeout, force the new socket kwenye blocking
        # mode to override platform-specific socket flags inheritance.
        ikiwa getdefaulttimeout() ni Tupu na self.gettimeout():
            sock.setblocking(Kweli)
        rudisha sock, addr

    eleza makefile(self, mode="r", buffering=Tupu, *,
                 encoding=Tupu, errors=Tupu, newline=Tupu):
        """makefile(...) -> an I/O stream connected to the socket

        The arguments are kama kila io.open() after the filename, tatizo the only
        supported mode values are 'r' (default), 'w' na 'b'.
        """
        # XXX refactor to share code?
        ikiwa sio set(mode) <= {"r", "w", "b"}:
            ashiria ValueError("invalid mode %r (only r, w, b allowed)" % (mode,))
        writing = "w" kwenye mode
        reading = "r" kwenye mode ama sio writing
        assert reading ama writing
        binary = "b" kwenye mode
        rawmode = ""
        ikiwa reading:
            rawmode += "r"
        ikiwa writing:
            rawmode += "w"
        raw = SocketIO(self, rawmode)
        self._io_refs += 1
        ikiwa buffering ni Tupu:
            buffering = -1
        ikiwa buffering < 0:
            buffering = io.DEFAULT_BUFFER_SIZE
        ikiwa buffering == 0:
            ikiwa sio binary:
                ashiria ValueError("unbuffered streams must be binary")
            rudisha raw
        ikiwa reading na writing:
            buffer = io.BufferedRWPair(raw, raw, buffering)
        elikiwa reading:
            buffer = io.BufferedReader(raw, buffering)
        isipokua:
            assert writing
            buffer = io.BufferedWriter(raw, buffering)
        ikiwa binary:
            rudisha buffer
        text = io.TextIOWrapper(buffer, encoding, errors, newline)
        text.mode = mode
        rudisha text

    ikiwa hasattr(os, 'sendfile'):

        eleza _sendfile_use_sendfile(self, file, offset=0, count=Tupu):
            self._check_sendfile_params(file, offset, count)
            sockno = self.fileno()
            jaribu:
                fileno = file.fileno()
            tatizo (AttributeError, io.UnsupportedOperation) kama err:
                ashiria _GiveupOnSendfile(err)  # sio a regular file
            jaribu:
                fsize = os.fstat(fileno).st_size
            tatizo OSError kama err:
                ashiria _GiveupOnSendfile(err)  # sio a regular file
            ikiwa sio fsize:
                rudisha 0  # empty file
            # Truncate to 1GiB to avoid OverflowError, see bpo-38319.
            blocksize = min(count ama fsize, 2 ** 30)
            timeout = self.gettimeout()
            ikiwa timeout == 0:
                ashiria ValueError("non-blocking sockets are sio supported")
            # poll/select have the advantage of sio requiring any
            # extra file descriptor, contrarily to epoll/kqueue
            # (also, they require a single syscall).
            ikiwa hasattr(selectors, 'PollSelector'):
                selector = selectors.PollSelector()
            isipokua:
                selector = selectors.SelectSelector()
            selector.register(sockno, selectors.EVENT_WRITE)

            total_sent = 0
            # localize variable access to minimize overhead
            selector_select = selector.select
            os_sendfile = os.sendfile
            jaribu:
                wakati Kweli:
                    ikiwa timeout na sio selector_select(timeout):
                        ashiria _socket.timeout('timed out')
                    ikiwa count:
                        blocksize = count - total_sent
                        ikiwa blocksize <= 0:
                            koma
                    jaribu:
                        sent = os_sendfile(sockno, fileno, offset, blocksize)
                    tatizo BlockingIOError:
                        ikiwa sio timeout:
                            # Block until the socket ni ready to send some
                            # data; avoids hogging CPU resources.
                            selector_select()
                        endelea
                    tatizo OSError kama err:
                        ikiwa total_sent == 0:
                            # We can get here kila different reasons, the main
                            # one being 'file' ni sio a regular mmap(2)-like
                            # file, kwenye which case we'll fall back on using
                            # plain send().
                            ashiria _GiveupOnSendfile(err)
                        ashiria err kutoka Tupu
                    isipokua:
                        ikiwa sent == 0:
                            koma  # EOF
                        offset += sent
                        total_sent += sent
                rudisha total_sent
            mwishowe:
                ikiwa total_sent > 0 na hasattr(file, 'seek'):
                    file.seek(offset)
    isipokua:
        eleza _sendfile_use_sendfile(self, file, offset=0, count=Tupu):
            ashiria _GiveupOnSendfile(
                "os.sendfile() sio available on this platform")

    eleza _sendfile_use_send(self, file, offset=0, count=Tupu):
        self._check_sendfile_params(file, offset, count)
        ikiwa self.gettimeout() == 0:
            ashiria ValueError("non-blocking sockets are sio supported")
        ikiwa offset:
            file.seek(offset)
        blocksize = min(count, 8192) ikiwa count else 8192
        total_sent = 0
        # localize variable access to minimize overhead
        file_read = file.read
        sock_send = self.send
        jaribu:
            wakati Kweli:
                ikiwa count:
                    blocksize = min(count - total_sent, blocksize)
                    ikiwa blocksize <= 0:
                        koma
                data = memoryview(file_read(blocksize))
                ikiwa sio data:
                    koma  # EOF
                wakati Kweli:
                    jaribu:
                        sent = sock_send(data)
                    tatizo BlockingIOError:
                        endelea
                    isipokua:
                        total_sent += sent
                        ikiwa sent < len(data):
                            data = data[sent:]
                        isipokua:
                            koma
            rudisha total_sent
        mwishowe:
            ikiwa total_sent > 0 na hasattr(file, 'seek'):
                file.seek(offset + total_sent)

    eleza _check_sendfile_params(self, file, offset, count):
        ikiwa 'b' haiko kwenye getattr(file, 'mode', 'b'):
            ashiria ValueError("file should be opened kwenye binary mode")
        ikiwa sio self.type & SOCK_STREAM:
            ashiria ValueError("only SOCK_STREAM type sockets are supported")
        ikiwa count ni sio Tupu:
            ikiwa sio isinstance(count, int):
                ashiria TypeError(
                    "count must be a positive integer (got {!r})".format(count))
            ikiwa count <= 0:
                ashiria ValueError(
                    "count must be a positive integer (got {!r})".format(count))

    eleza sendfile(self, file, offset=0, count=Tupu):
        """sendfile(file[, offset[, count]]) -> sent

        Send a file until EOF ni reached by using high-performance
        os.sendfile() na rudisha the total number of bytes which
        were sent.
        *file* must be a regular file object opened kwenye binary mode.
        If os.sendfile() ni sio available (e.g. Windows) ama file is
        sio a regular file socket.send() will be used instead.
        *offset* tells kutoka where to start reading the file.
        If specified, *count* ni the total number of bytes to transmit
        kama opposed to sending the file until EOF ni reached.
        File position ni updated on rudisha ama also kwenye case of error in
        which case file.tell() can be used to figure out the number of
        bytes which were sent.
        The socket must be of SOCK_STREAM type.
        Non-blocking sockets are sio supported.
        """
        jaribu:
            rudisha self._sendfile_use_sendfile(file, offset, count)
        tatizo _GiveupOnSendfile:
            rudisha self._sendfile_use_send(file, offset, count)

    eleza _decref_socketios(self):
        ikiwa self._io_refs > 0:
            self._io_refs -= 1
        ikiwa self._closed:
            self.close()

    eleza _real_close(self, _ss=_socket.socket):
        # This function should sio reference any globals. See issue #808164.
        _ss.close(self)

    eleza close(self):
        # This function should sio reference any globals. See issue #808164.
        self._closed = Kweli
        ikiwa self._io_refs <= 0:
            self._real_close()

    eleza detach(self):
        """detach() -> file descriptor

        Close the socket object without closing the underlying file descriptor.
        The object cannot be used after this call, but the file descriptor
        can be reused kila other purposes.  The file descriptor ni rudishaed.
        """
        self._closed = Kweli
        rudisha super().detach()

    @property
    eleza family(self):
        """Read-only access to the address family kila this socket.
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
    isipokua:
        eleza get_inheritable(self):
            rudisha os.get_inheritable(self.fileno())
        eleza set_inheritable(self, inheritable):
            os.set_inheritable(self.fileno(), inheritable)
    get_inheritable.__doc__ = "Get the inheritable flag of the socket"
    set_inheritable.__doc__ = "Set the inheritable flag of the socket"

eleza kutokafd(fd, family, type, proto=0):
    """ kutokafd(fd, family, type[, proto]) -> socket object

    Create a socket object kutoka a duplicate of the given file
    descriptor.  The remaining arguments are the same kama kila socket().
    """
    nfd = dup(fd)
    rudisha socket(family, type, proto, nfd)

ikiwa hasattr(_socket.socket, "share"):
    eleza kutokashare(info):
        """ kutokashare(info) -> socket object

        Create a socket object kutoka the bytes object rudishaed by
        socket.share(pid).
        """
        rudisha socket(0, 0, 0, info)
    __all__.append("kutokashare")

ikiwa hasattr(_socket, "socketpair"):

    eleza socketpair(family=Tupu, type=SOCK_STREAM, proto=0):
        """socketpair([family[, type[, proto]]]) -> (socket object, socket object)

        Create a pair of socket objects kutoka the sockets rudishaed by the platform
        socketpair() function.
        The arguments are the same kama kila socket() tatizo the default family is
        AF_UNIX ikiwa defined on the platform; otherwise, the default ni AF_INET.
        """
        ikiwa family ni Tupu:
            jaribu:
                family = AF_UNIX
            tatizo NameError:
                family = AF_INET
        a, b = _socket.socketpair(family, type, proto)
        a = socket(family, type, proto, a.detach())
        b = socket(family, type, proto, b.detach())
        rudisha a, b

isipokua:

    # Origin: https://gist.github.com/4325783, by Geert Jansen.  Public domain.
    eleza socketpair(family=AF_INET, type=SOCK_STREAM, proto=0):
        ikiwa family == AF_INET:
            host = _LOCALHOST
        elikiwa family == AF_INET6:
            host = _LOCALHOST_V6
        isipokua:
            ashiria ValueError("Only AF_INET na AF_INET6 socket address families "
                             "are supported")
        ikiwa type != SOCK_STREAM:
            ashiria ValueError("Only SOCK_STREAM socket type ni supported")
        ikiwa proto != 0:
            ashiria ValueError("Only protocol zero ni supported")

        # We create a connected TCP socket. Note the trick with
        # setblocking(Uongo) that prevents us kutoka having to create a thread.
        lsock = socket(family, type, proto)
        jaribu:
            lsock.bind((host, 0))
            lsock.listen()
            # On IPv6, ignore flow_info na scope_id
            addr, port = lsock.getsockname()[:2]
            csock = socket(family, type, proto)
            jaribu:
                csock.setblocking(Uongo)
                jaribu:
                    csock.connect((addr, port))
                tatizo (BlockingIOError, InterruptedError):
                    pita
                csock.setblocking(Kweli)
                ssock, _ = lsock.accept()
            except:
                csock.close()
                ashiria
        mwishowe:
            lsock.close()
        rudisha (ssock, csock)
    __all__.append("socketpair")

socketpair.__doc__ = """socketpair([family[, type[, proto]]]) -> (socket object, socket object)
Create a pair of socket objects kutoka the sockets rudishaed by the platform
socketpair() function.
The arguments are the same kama kila socket() tatizo the default family ni AF_UNIX
ikiwa defined on the platform; otherwise, the default ni AF_INET.
"""

_blocking_errnos = { EAGAIN, EWOULDBLOCK }

kundi SocketIO(io.RawIOBase):

    """Raw I/O implementation kila stream sockets.

    This kundi supports the makefile() method on sockets.  It provides
    the raw I/O interface on top of a socket object.
    """

    # One might wonder why sio let FileIO do the job instead.  There are two
    # main reasons why FileIO ni sio adapted:
    # - it wouldn't work under Windows (where you can't used read() and
    #   write() on a socket handle)
    # - it wouldn't work with socket timeouts (FileIO would ignore the
    #   timeout na consider the socket non-blocking)

    # XXX More docs

    eleza __init__(self, sock, mode):
        ikiwa mode haiko kwenye ("r", "w", "rw", "rb", "wb", "rwb"):
            ashiria ValueError("invalid mode: %r" % mode)
        io.RawIOBase.__init__(self)
        self._sock = sock
        ikiwa "b" haiko kwenye mode:
            mode += "b"
        self._mode = mode
        self._reading = "r" kwenye mode
        self._writing = "w" kwenye mode
        self._timeout_occurred = Uongo

    eleza readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* na rudisha
        the number of bytes read.  If the socket ni non-blocking na no bytes
        are available, Tupu ni rudishaed.

        If *b* ni non-empty, a 0 rudisha value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        ikiwa self._timeout_occurred:
            ashiria OSError("cannot read kutoka timed out object")
        wakati Kweli:
            jaribu:
                rudisha self._sock.recv_into(b)
            tatizo timeout:
                self._timeout_occurred = Kweli
                ashiria
            tatizo error kama e:
                ikiwa e.args[0] kwenye _blocking_errnos:
                    rudisha Tupu
                ashiria

    eleza write(self, b):
        """Write the given bytes ama bytearray object *b* to the socket
        na rudisha the number of bytes written.  This can be less than
        len(b) ikiwa sio all data could be written.  If the socket is
        non-blocking na no bytes could be written Tupu ni rudishaed.
        """
        self._checkClosed()
        self._checkWritable()
        jaribu:
            rudisha self._sock.send(b)
        tatizo error kama e:
            # XXX what about EINTR?
            ikiwa e.args[0] kwenye _blocking_errnos:
                rudisha Tupu
            ashiria

    eleza readable(self):
        """Kweli ikiwa the SocketIO ni open kila reading.
        """
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed socket.")
        rudisha self._reading

    eleza writable(self):
        """Kweli ikiwa the SocketIO ni open kila writing.
        """
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed socket.")
        rudisha self._writing

    eleza seekable(self):
        """Kweli ikiwa the SocketIO ni open kila seeking.
        """
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed socket.")
        rudisha super().seekable()

    eleza fileno(self):
        """Return the file descriptor of the underlying socket.
        """
        self._checkClosed()
        rudisha self._sock.fileno()

    @property
    eleza name(self):
        ikiwa sio self.closed:
            rudisha self.fileno()
        isipokua:
            rudisha -1

    @property
    eleza mode(self):
        rudisha self._mode

    eleza close(self):
        """Close the SocketIO object.  This doesn't close the underlying
        socket, tatizo ikiwa all references to it have disappeared.
        """
        ikiwa self.closed:
            rudisha
        io.RawIOBase.close(self)
        self._sock._decref_socketios()
        self._sock = Tupu


eleza getfqdn(name=''):
    """Get fully qualified domain name kutoka name.

    An empty argument ni interpreted kama meaning the local host.

    First the hostname rudishaed by gethostbyaddr() ni checked, then
    possibly existing aliases. In case no FQDN ni available, hostname
    kutoka gethostname() ni rudishaed.
    """
    name = name.strip()
    ikiwa sio name ama name == '0.0.0.0':
        name = gethostname()
    jaribu:
        hostname, aliases, ipaddrs = gethostbyaddr(name)
    tatizo error:
        pita
    isipokua:
        aliases.insert(0, hostname)
        kila name kwenye aliases:
            ikiwa '.' kwenye name:
                koma
        isipokua:
            name = hostname
    rudisha name


_GLOBAL_DEFAULT_TIMEOUT = object()

eleza create_connection(address, timeout=_GLOBAL_DEFAULT_TIMEOUT,
                      source_address=Tupu):
    """Connect to *address* na rudisha the socket object.

    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) na rudisha the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* ni supplied, the
    global default timeout setting rudishaed by :func:`getdefaulttimeout`
    ni used.  If *source_address* ni set it must be a tuple of (host, port)
    kila the socket to bind kama a source address before making the connection.
    A host of '' ama port 0 tells the OS to use the default.
    """

    host, port = address
    err = Tupu
    kila res kwenye getaddrinfo(host, port, 0, SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = Tupu
        jaribu:
            sock = socket(af, socktype, proto)
            ikiwa timeout ni sio _GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            ikiwa source_address:
                sock.bind(source_address)
            sock.connect(sa)
            # Break explicitly a reference cycle
            err = Tupu
            rudisha sock

        tatizo error kama _:
            err = _
            ikiwa sock ni sio Tupu:
                sock.close()

    ikiwa err ni sio Tupu:
        ashiria err
    isipokua:
        ashiria error("getaddrinfo rudishas an empty list")


eleza has_dualstack_ipv6():
    """Return Kweli ikiwa the platform supports creating a SOCK_STREAM socket
    which can handle both AF_INET na AF_INET6 (IPv4 / IPv6) connections.
    """
    ikiwa sio has_ipv6 \
            ama sio hasattr(_socket, 'IPPROTO_IPV6') \
            ama sio hasattr(_socket, 'IPV6_V6ONLY'):
        rudisha Uongo
    jaribu:
        with socket(AF_INET6, SOCK_STREAM) kama sock:
            sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)
            rudisha Kweli
    tatizo error:
        rudisha Uongo


eleza create_server(address, *, family=AF_INET, backlog=Tupu, reuse_port=Uongo,
                  dualstack_ipv6=Uongo):
    """Convenience function which creates a SOCK_STREAM type socket
    bound to *address* (a 2-tuple (host, port)) na rudisha the socket
    object.

    *family* should be either AF_INET ama AF_INET6.
    *backlog* ni the queue size pitaed to socket.listen().
    *reuse_port* dictates whether to use the SO_REUSEPORT socket option.
    *dualstack_ipv6*: ikiwa true na the platform supports it, it will
    create an AF_INET6 socket able to accept both IPv4 ama IPv6
    connections. When false it will explicitly disable this option on
    platforms that enable it by default (e.g. Linux).

    >>> with create_server((Tupu, 8000)) kama server:
    ...     wakati Kweli:
    ...         conn, addr = server.accept()
    ...         # handle new connection
    """
    ikiwa reuse_port na sio hasattr(_socket, "SO_REUSEPORT"):
        ashiria ValueError("SO_REUSEPORT sio supported on this platform")
    ikiwa dualstack_ipv6:
        ikiwa sio has_dualstack_ipv6():
            ashiria ValueError("dualstack_ipv6 sio supported on this platform")
        ikiwa family != AF_INET6:
            ashiria ValueError("dualstack_ipv6 requires AF_INET6 family")
    sock = socket(family, SOCK_STREAM)
    jaribu:
        # Note about Windows. We don't set SO_REUSEADDR because:
        # 1) It's unnecessary: bind() will succeed even kwenye case of a
        # previous closed socket on the same address na still in
        # TIME_WAIT state.
        # 2) If set, another socket ni free to bind() on the same
        # address, effectively preventing this one kutoka accepting
        # connections. Also, it may set the process kwenye a state where
        # it'll no longer respond to any signals ama graceful kills.
        # See: msdn2.microsoft.com/en-us/library/ms740621(VS.85).aspx
        ikiwa os.name haiko kwenye ('nt', 'cygwin') na \
                hasattr(_socket, 'SO_REUSEADDR'):
            jaribu:
                sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            tatizo error:
                # Fail later on bind(), kila platforms which may not
                # support this option.
                pita
        ikiwa reuse_port:
            sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        ikiwa has_ipv6 na family == AF_INET6:
            ikiwa dualstack_ipv6:
                sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)
            elikiwa hasattr(_socket, "IPV6_V6ONLY") na \
                    hasattr(_socket, "IPPROTO_IPV6"):
                sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 1)
        jaribu:
            sock.bind(address)
        tatizo error kama err:
            msg = '%s (wakati attempting to bind on address %r)' % \
                (err.strerror, address)
            ashiria error(err.errno, msg) kutoka Tupu
        ikiwa backlog ni Tupu:
            sock.listen()
        isipokua:
            sock.listen(backlog)
        rudisha sock
    tatizo error:
        sock.close()
        ashiria


eleza getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """Resolve host na port into list of address info entries.

    Translate the host/port argument into a sequence of 5-tuples that contain
    all the necessary arguments kila creating a socket connected to that service.
    host ni a domain name, a string representation of an IPv4/v6 address or
    Tupu. port ni a string service name such kama 'http', a numeric port number or
    Tupu. By pitaing Tupu kama the value of host na port, you can pita NULL to
    the underlying C API.

    The family, type na proto arguments can be optionally specified kwenye order to
    narrow the list of addresses rudishaed. Passing zero kama a value kila each of
    these arguments selects the full range of results.
    """
    # We override this function since we want to translate the numeric family
    # na socket type values to enum constants.
    addrlist = []
    kila res kwenye _socket.getaddrinfo(host, port, family, type, proto, flags):
        af, socktype, proto, canonname, sa = res
        addrlist.append((_intenum_converter(af, AddressFamily),
                         _intenum_converter(socktype, SocketKind),
                         proto, canonname, sa))
    rudisha addrlist
