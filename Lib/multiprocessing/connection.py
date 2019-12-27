#
# A higher level module for using sockets (or Windows named pipes)
#
# multiprocessing/connection.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [ 'Client', 'Listener', 'Pipe', 'wait' ]

agiza io
agiza os
agiza sys
agiza socket
agiza struct
agiza time
agiza tempfile
agiza itertools

agiza _multiprocessing

kutoka . agiza util

kutoka . agiza AuthenticationError, BufferTooShort
kutoka .context agiza reduction
_ForkingPickler = reduction.ForkingPickler

try:
    agiza _winapi
    kutoka _winapi agiza WAIT_OBJECT_0, WAIT_ABANDONED_0, WAIT_TIMEOUT, INFINITE
except ImportError:
    ikiwa sys.platform == 'win32':
        raise
    _winapi = None

#
#
#

BUFSIZE = 8192
# A very generous timeout when it comes to local connections...
CONNECTION_TIMEOUT = 20.

_mmap_counter = itertools.count()

default_family = 'AF_INET'
families = ['AF_INET']

ikiwa hasattr(socket, 'AF_UNIX'):
    default_family = 'AF_UNIX'
    families += ['AF_UNIX']

ikiwa sys.platform == 'win32':
    default_family = 'AF_PIPE'
    families += ['AF_PIPE']


eleza _init_timeout(timeout=CONNECTION_TIMEOUT):
    rudisha time.monotonic() + timeout

eleza _check_timeout(t):
    rudisha time.monotonic() > t

#
#
#

eleza arbitrary_address(family):
    '''
    Return an arbitrary free address for the given family
    '''
    ikiwa family == 'AF_INET':
        rudisha ('localhost', 0)
    elikiwa family == 'AF_UNIX':
        rudisha tempfile.mktemp(prefix='listener-', dir=util.get_temp_dir())
    elikiwa family == 'AF_PIPE':
        rudisha tempfile.mktemp(prefix=r'\\.\pipe\pyc-%d-%d-' %
                               (os.getpid(), next(_mmap_counter)), dir="")
    else:
        raise ValueError('unrecognized family')

eleza _validate_family(family):
    '''
    Checks ikiwa the family is valid for the current environment.
    '''
    ikiwa sys.platform != 'win32' and family == 'AF_PIPE':
        raise ValueError('Family %s is not recognized.' % family)

    ikiwa sys.platform == 'win32' and family == 'AF_UNIX':
        # double check
        ikiwa not hasattr(socket, family):
            raise ValueError('Family %s is not recognized.' % family)

eleza address_type(address):
    '''
    Return the types of the address

    This can be 'AF_INET', 'AF_UNIX', or 'AF_PIPE'
    '''
    ikiwa type(address) == tuple:
        rudisha 'AF_INET'
    elikiwa type(address) is str and address.startswith('\\\\'):
        rudisha 'AF_PIPE'
    elikiwa type(address) is str:
        rudisha 'AF_UNIX'
    else:
        raise ValueError('address type of %r unrecognized' % address)

#
# Connection classes
#

kundi _ConnectionBase:
    _handle = None

    eleza __init__(self, handle, readable=True, writable=True):
        handle = handle.__index__()
        ikiwa handle < 0:
            raise ValueError("invalid handle")
        ikiwa not readable and not writable:
            raise ValueError(
                "at least one of `readable` and `writable` must be True")
        self._handle = handle
        self._readable = readable
        self._writable = writable

    # XXX should we use util.Finalize instead of a __del__?

    eleza __del__(self):
        ikiwa self._handle is not None:
            self._close()

    eleza _check_closed(self):
        ikiwa self._handle is None:
            raise OSError("handle is closed")

    eleza _check_readable(self):
        ikiwa not self._readable:
            raise OSError("connection is write-only")

    eleza _check_writable(self):
        ikiwa not self._writable:
            raise OSError("connection is read-only")

    eleza _bad_message_length(self):
        ikiwa self._writable:
            self._readable = False
        else:
            self.close()
        raise OSError("bad message length")

    @property
    eleza closed(self):
        """True ikiwa the connection is closed"""
        rudisha self._handle is None

    @property
    eleza readable(self):
        """True ikiwa the connection is readable"""
        rudisha self._readable

    @property
    eleza writable(self):
        """True ikiwa the connection is writable"""
        rudisha self._writable

    eleza fileno(self):
        """File descriptor or handle of the connection"""
        self._check_closed()
        rudisha self._handle

    eleza close(self):
        """Close the connection"""
        ikiwa self._handle is not None:
            try:
                self._close()
            finally:
                self._handle = None

    eleza send_bytes(self, buf, offset=0, size=None):
        """Send the bytes data kutoka a bytes-like object"""
        self._check_closed()
        self._check_writable()
        m = memoryview(buf)
        # HACK for byte-indexing of non-bytewise buffers (e.g. array.array)
        ikiwa m.itemsize > 1:
            m = memoryview(bytes(m))
        n = len(m)
        ikiwa offset < 0:
            raise ValueError("offset is negative")
        ikiwa n < offset:
            raise ValueError("buffer length < offset")
        ikiwa size is None:
            size = n - offset
        elikiwa size < 0:
            raise ValueError("size is negative")
        elikiwa offset + size > n:
            raise ValueError("buffer length < offset + size")
        self._send_bytes(m[offset:offset + size])

    eleza send(self, obj):
        """Send a (picklable) object"""
        self._check_closed()
        self._check_writable()
        self._send_bytes(_ForkingPickler.dumps(obj))

    eleza recv_bytes(self, maxlength=None):
        """
        Receive bytes data as a bytes object.
        """
        self._check_closed()
        self._check_readable()
        ikiwa maxlength is not None and maxlength < 0:
            raise ValueError("negative maxlength")
        buf = self._recv_bytes(maxlength)
        ikiwa buf is None:
            self._bad_message_length()
        rudisha buf.getvalue()

    eleza recv_bytes_into(self, buf, offset=0):
        """
        Receive bytes data into a writeable bytes-like object.
        Return the number of bytes read.
        """
        self._check_closed()
        self._check_readable()
        with memoryview(buf) as m:
            # Get bytesize of arbitrary buffer
            itemsize = m.itemsize
            bytesize = itemsize * len(m)
            ikiwa offset < 0:
                raise ValueError("negative offset")
            elikiwa offset > bytesize:
                raise ValueError("offset too large")
            result = self._recv_bytes()
            size = result.tell()
            ikiwa bytesize < offset + size:
                raise BufferTooShort(result.getvalue())
            # Message can fit in dest
            result.seek(0)
            result.readinto(m[offset // itemsize :
                              (offset + size) // itemsize])
            rudisha size

    eleza recv(self):
        """Receive a (picklable) object"""
        self._check_closed()
        self._check_readable()
        buf = self._recv_bytes()
        rudisha _ForkingPickler.loads(buf.getbuffer())

    eleza poll(self, timeout=0.0):
        """Whether there is any input available to be read"""
        self._check_closed()
        self._check_readable()
        rudisha self._poll(timeout)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


ikiwa _winapi:

    kundi PipeConnection(_ConnectionBase):
        """
        Connection kundi based on a Windows named pipe.
        Overlapped I/O is used, so the handles must have been created
        with FILE_FLAG_OVERLAPPED.
        """
        _got_empty_message = False

        eleza _close(self, _CloseHandle=_winapi.CloseHandle):
            _CloseHandle(self._handle)

        eleza _send_bytes(self, buf):
            ov, err = _winapi.WriteFile(self._handle, buf, overlapped=True)
            try:
                ikiwa err == _winapi.ERROR_IO_PENDING:
                    waitres = _winapi.WaitForMultipleObjects(
                        [ov.event], False, INFINITE)
                    assert waitres == WAIT_OBJECT_0
            except:
                ov.cancel()
                raise
            finally:
                nwritten, err = ov.GetOverlappedResult(True)
            assert err == 0
            assert nwritten == len(buf)

        eleza _recv_bytes(self, maxsize=None):
            ikiwa self._got_empty_message:
                self._got_empty_message = False
                rudisha io.BytesIO()
            else:
                bsize = 128 ikiwa maxsize is None else min(maxsize, 128)
                try:
                    ov, err = _winapi.ReadFile(self._handle, bsize,
                                                overlapped=True)
                    try:
                        ikiwa err == _winapi.ERROR_IO_PENDING:
                            waitres = _winapi.WaitForMultipleObjects(
                                [ov.event], False, INFINITE)
                            assert waitres == WAIT_OBJECT_0
                    except:
                        ov.cancel()
                        raise
                    finally:
                        nread, err = ov.GetOverlappedResult(True)
                        ikiwa err == 0:
                            f = io.BytesIO()
                            f.write(ov.getbuffer())
                            rudisha f
                        elikiwa err == _winapi.ERROR_MORE_DATA:
                            rudisha self._get_more_data(ov, maxsize)
                except OSError as e:
                    ikiwa e.winerror == _winapi.ERROR_BROKEN_PIPE:
                        raise EOFError
                    else:
                        raise
            raise RuntimeError("shouldn't get here; expected KeyboardInterrupt")

        eleza _poll(self, timeout):
            ikiwa (self._got_empty_message or
                        _winapi.PeekNamedPipe(self._handle)[0] != 0):
                rudisha True
            rudisha bool(wait([self], timeout))

        eleza _get_more_data(self, ov, maxsize):
            buf = ov.getbuffer()
            f = io.BytesIO()
            f.write(buf)
            left = _winapi.PeekNamedPipe(self._handle)[1]
            assert left > 0
            ikiwa maxsize is not None and len(buf) + left > maxsize:
                self._bad_message_length()
            ov, err = _winapi.ReadFile(self._handle, left, overlapped=True)
            rbytes, err = ov.GetOverlappedResult(True)
            assert err == 0
            assert rbytes == left
            f.write(ov.getbuffer())
            rudisha f


kundi Connection(_ConnectionBase):
    """
    Connection kundi based on an arbitrary file descriptor (Unix only), or
    a socket handle (Windows).
    """

    ikiwa _winapi:
        eleza _close(self, _close=_multiprocessing.closesocket):
            _close(self._handle)
        _write = _multiprocessing.send
        _read = _multiprocessing.recv
    else:
        eleza _close(self, _close=os.close):
            _close(self._handle)
        _write = os.write
        _read = os.read

    eleza _send(self, buf, write=_write):
        remaining = len(buf)
        while True:
            n = write(self._handle, buf)
            remaining -= n
            ikiwa remaining == 0:
                break
            buf = buf[n:]

    eleza _recv(self, size, read=_read):
        buf = io.BytesIO()
        handle = self._handle
        remaining = size
        while remaining > 0:
            chunk = read(handle, remaining)
            n = len(chunk)
            ikiwa n == 0:
                ikiwa remaining == size:
                    raise EOFError
                else:
                    raise OSError("got end of file during message")
            buf.write(chunk)
            remaining -= n
        rudisha buf

    eleza _send_bytes(self, buf):
        n = len(buf)
        ikiwa n > 0x7fffffff:
            pre_header = struct.pack("!i", -1)
            header = struct.pack("!Q", n)
            self._send(pre_header)
            self._send(header)
            self._send(buf)
        else:
            # For wire compatibility with 3.7 and lower
            header = struct.pack("!i", n)
            ikiwa n > 16384:
                # The payload is large so Nagle's algorithm won't be triggered
                # and we'd better avoid the cost of concatenation.
                self._send(header)
                self._send(buf)
            else:
                # Issue #20540: concatenate before sending, to avoid delays due
                # to Nagle's algorithm on a TCP socket.
                # Also note we want to avoid sending a 0-length buffer separately,
                # to avoid "broken pipe" errors ikiwa the other end closed the pipe.
                self._send(header + buf)

    eleza _recv_bytes(self, maxsize=None):
        buf = self._recv(4)
        size, = struct.unpack("!i", buf.getvalue())
        ikiwa size == -1:
            buf = self._recv(8)
            size, = struct.unpack("!Q", buf.getvalue())
        ikiwa maxsize is not None and size > maxsize:
            rudisha None
        rudisha self._recv(size)

    eleza _poll(self, timeout):
        r = wait([self], timeout)
        rudisha bool(r)


#
# Public functions
#

kundi Listener(object):
    '''
    Returns a listener object.

    This is a wrapper for a bound socket which is 'listening' for
    connections, or for a Windows named pipe.
    '''
    eleza __init__(self, address=None, family=None, backlog=1, authkey=None):
        family = family or (address and address_type(address)) \
                 or default_family
        address = address or arbitrary_address(family)

        _validate_family(family)
        ikiwa family == 'AF_PIPE':
            self._listener = PipeListener(address, backlog)
        else:
            self._listener = SocketListener(address, family, backlog)

        ikiwa authkey is not None and not isinstance(authkey, bytes):
            raise TypeError('authkey should be a byte string')

        self._authkey = authkey

    eleza accept(self):
        '''
        Accept a connection on the bound socket or named pipe of `self`.

        Returns a `Connection` object.
        '''
        ikiwa self._listener is None:
            raise OSError('listener is closed')
        c = self._listener.accept()
        ikiwa self._authkey:
            deliver_challenge(c, self._authkey)
            answer_challenge(c, self._authkey)
        rudisha c

    eleza close(self):
        '''
        Close the bound socket or named pipe of `self`.
        '''
        listener = self._listener
        ikiwa listener is not None:
            self._listener = None
            listener.close()

    @property
    eleza address(self):
        rudisha self._listener._address

    @property
    eleza last_accepted(self):
        rudisha self._listener._last_accepted

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


eleza Client(address, family=None, authkey=None):
    '''
    Returns a connection to the address of a `Listener`
    '''
    family = family or address_type(address)
    _validate_family(family)
    ikiwa family == 'AF_PIPE':
        c = PipeClient(address)
    else:
        c = SocketClient(address)

    ikiwa authkey is not None and not isinstance(authkey, bytes):
        raise TypeError('authkey should be a byte string')

    ikiwa authkey is not None:
        answer_challenge(c, authkey)
        deliver_challenge(c, authkey)

    rudisha c


ikiwa sys.platform != 'win32':

    eleza Pipe(duplex=True):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        ikiwa duplex:
            s1, s2 = socket.socketpair()
            s1.setblocking(True)
            s2.setblocking(True)
            c1 = Connection(s1.detach())
            c2 = Connection(s2.detach())
        else:
            fd1, fd2 = os.pipe()
            c1 = Connection(fd1, writable=False)
            c2 = Connection(fd2, readable=False)

        rudisha c1, c2

else:

    eleza Pipe(duplex=True):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        address = arbitrary_address('AF_PIPE')
        ikiwa duplex:
            openmode = _winapi.PIPE_ACCESS_DUPLEX
            access = _winapi.GENERIC_READ | _winapi.GENERIC_WRITE
            obsize, ibsize = BUFSIZE, BUFSIZE
        else:
            openmode = _winapi.PIPE_ACCESS_INBOUND
            access = _winapi.GENERIC_WRITE
            obsize, ibsize = 0, BUFSIZE

        h1 = _winapi.CreateNamedPipe(
            address, openmode | _winapi.FILE_FLAG_OVERLAPPED |
            _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE,
            _winapi.PIPE_TYPE_MESSAGE | _winapi.PIPE_READMODE_MESSAGE |
            _winapi.PIPE_WAIT,
            1, obsize, ibsize, _winapi.NMPWAIT_WAIT_FOREVER,
            # default security descriptor: the handle cannot be inherited
            _winapi.NULL
            )
        h2 = _winapi.CreateFile(
            address, access, 0, _winapi.NULL, _winapi.OPEN_EXISTING,
            _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL
            )
        _winapi.SetNamedPipeHandleState(
            h2, _winapi.PIPE_READMODE_MESSAGE, None, None
            )

        overlapped = _winapi.ConnectNamedPipe(h1, overlapped=True)
        _, err = overlapped.GetOverlappedResult(True)
        assert err == 0

        c1 = PipeConnection(h1, writable=duplex)
        c2 = PipeConnection(h2, readable=duplex)

        rudisha c1, c2

#
# Definitions for connections based on sockets
#

kundi SocketListener(object):
    '''
    Representation of a socket which is bound to an address and listening
    '''
    eleza __init__(self, address, family, backlog=1):
        self._socket = socket.socket(getattr(socket, family))
        try:
            # SO_REUSEADDR has different semantics on Windows (issue #2550).
            ikiwa os.name == 'posix':
                self._socket.setsockopt(socket.SOL_SOCKET,
                                        socket.SO_REUSEADDR, 1)
            self._socket.setblocking(True)
            self._socket.bind(address)
            self._socket.listen(backlog)
            self._address = self._socket.getsockname()
        except OSError:
            self._socket.close()
            raise
        self._family = family
        self._last_accepted = None

        ikiwa family == 'AF_UNIX':
            self._unlink = util.Finalize(
                self, os.unlink, args=(address,), exitpriority=0
                )
        else:
            self._unlink = None

    eleza accept(self):
        s, self._last_accepted = self._socket.accept()
        s.setblocking(True)
        rudisha Connection(s.detach())

    eleza close(self):
        try:
            self._socket.close()
        finally:
            unlink = self._unlink
            ikiwa unlink is not None:
                self._unlink = None
                unlink()


eleza SocketClient(address):
    '''
    Return a connection object connected to the socket given by `address`
    '''
    family = address_type(address)
    with socket.socket( getattr(socket, family) ) as s:
        s.setblocking(True)
        s.connect(address)
        rudisha Connection(s.detach())

#
# Definitions for connections based on named pipes
#

ikiwa sys.platform == 'win32':

    kundi PipeListener(object):
        '''
        Representation of a named pipe
        '''
        eleza __init__(self, address, backlog=None):
            self._address = address
            self._handle_queue = [self._new_handle(first=True)]

            self._last_accepted = None
            util.sub_debug('listener created with address=%r', self._address)
            self.close = util.Finalize(
                self, PipeListener._finalize_pipe_listener,
                args=(self._handle_queue, self._address), exitpriority=0
                )

        eleza _new_handle(self, first=False):
            flags = _winapi.PIPE_ACCESS_DUPLEX | _winapi.FILE_FLAG_OVERLAPPED
            ikiwa first:
                flags |= _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE
            rudisha _winapi.CreateNamedPipe(
                self._address, flags,
                _winapi.PIPE_TYPE_MESSAGE | _winapi.PIPE_READMODE_MESSAGE |
                _winapi.PIPE_WAIT,
                _winapi.PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE,
                _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL
                )

        eleza accept(self):
            self._handle_queue.append(self._new_handle())
            handle = self._handle_queue.pop(0)
            try:
                ov = _winapi.ConnectNamedPipe(handle, overlapped=True)
            except OSError as e:
                ikiwa e.winerror != _winapi.ERROR_NO_DATA:
                    raise
                # ERROR_NO_DATA can occur ikiwa a client has already connected,
                # written data and then disconnected -- see Issue 14725.
            else:
                try:
                    res = _winapi.WaitForMultipleObjects(
                        [ov.event], False, INFINITE)
                except:
                    ov.cancel()
                    _winapi.CloseHandle(handle)
                    raise
                finally:
                    _, err = ov.GetOverlappedResult(True)
                    assert err == 0
            rudisha PipeConnection(handle)

        @staticmethod
        eleza _finalize_pipe_listener(queue, address):
            util.sub_debug('closing listener with address=%r', address)
            for handle in queue:
                _winapi.CloseHandle(handle)

    eleza PipeClient(address):
        '''
        Return a connection object connected to the pipe given by `address`
        '''
        t = _init_timeout()
        while 1:
            try:
                _winapi.WaitNamedPipe(address, 1000)
                h = _winapi.CreateFile(
                    address, _winapi.GENERIC_READ | _winapi.GENERIC_WRITE,
                    0, _winapi.NULL, _winapi.OPEN_EXISTING,
                    _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL
                    )
            except OSError as e:
                ikiwa e.winerror not in (_winapi.ERROR_SEM_TIMEOUT,
                                      _winapi.ERROR_PIPE_BUSY) or _check_timeout(t):
                    raise
            else:
                break
        else:
            raise

        _winapi.SetNamedPipeHandleState(
            h, _winapi.PIPE_READMODE_MESSAGE, None, None
            )
        rudisha PipeConnection(h)

#
# Authentication stuff
#

MESSAGE_LENGTH = 20

CHALLENGE = b'#CHALLENGE#'
WELCOME = b'#WELCOME#'
FAILURE = b'#FAILURE#'

eleza deliver_challenge(connection, authkey):
    agiza hmac
    ikiwa not isinstance(authkey, bytes):
        raise ValueError(
            "Authkey must be bytes, not {0!s}".format(type(authkey)))
    message = os.urandom(MESSAGE_LENGTH)
    connection.send_bytes(CHALLENGE + message)
    digest = hmac.new(authkey, message, 'md5').digest()
    response = connection.recv_bytes(256)        # reject large message
    ikiwa response == digest:
        connection.send_bytes(WELCOME)
    else:
        connection.send_bytes(FAILURE)
        raise AuthenticationError('digest received was wrong')

eleza answer_challenge(connection, authkey):
    agiza hmac
    ikiwa not isinstance(authkey, bytes):
        raise ValueError(
            "Authkey must be bytes, not {0!s}".format(type(authkey)))
    message = connection.recv_bytes(256)         # reject large message
    assert message[:len(CHALLENGE)] == CHALLENGE, 'message = %r' % message
    message = message[len(CHALLENGE):]
    digest = hmac.new(authkey, message, 'md5').digest()
    connection.send_bytes(digest)
    response = connection.recv_bytes(256)        # reject large message
    ikiwa response != WELCOME:
        raise AuthenticationError('digest sent was rejected')

#
# Support for using xmlrpclib for serialization
#

kundi ConnectionWrapper(object):
    eleza __init__(self, conn, dumps, loads):
        self._conn = conn
        self._dumps = dumps
        self._loads = loads
        for attr in ('fileno', 'close', 'poll', 'recv_bytes', 'send_bytes'):
            obj = getattr(conn, attr)
            setattr(self, attr, obj)
    eleza send(self, obj):
        s = self._dumps(obj)
        self._conn.send_bytes(s)
    eleza recv(self):
        s = self._conn.recv_bytes()
        rudisha self._loads(s)

eleza _xml_dumps(obj):
    rudisha xmlrpclib.dumps((obj,), None, None, None, 1).encode('utf-8')

eleza _xml_loads(s):
    (obj,), method = xmlrpclib.loads(s.decode('utf-8'))
    rudisha obj

kundi XmlListener(Listener):
    eleza accept(self):
        global xmlrpclib
        agiza xmlrpc.client as xmlrpclib
        obj = Listener.accept(self)
        rudisha ConnectionWrapper(obj, _xml_dumps, _xml_loads)

eleza XmlClient(*args, **kwds):
    global xmlrpclib
    agiza xmlrpc.client as xmlrpclib
    rudisha ConnectionWrapper(Client(*args, **kwds), _xml_dumps, _xml_loads)

#
# Wait
#

ikiwa sys.platform == 'win32':

    eleza _exhaustive_wait(handles, timeout):
        # Return ALL handles which are currently signalled.  (Only
        # returning the first signalled might create starvation issues.)
        L = list(handles)
        ready = []
        while L:
            res = _winapi.WaitForMultipleObjects(L, False, timeout)
            ikiwa res == WAIT_TIMEOUT:
                break
            elikiwa WAIT_OBJECT_0 <= res < WAIT_OBJECT_0 + len(L):
                res -= WAIT_OBJECT_0
            elikiwa WAIT_ABANDONED_0 <= res < WAIT_ABANDONED_0 + len(L):
                res -= WAIT_ABANDONED_0
            else:
                raise RuntimeError('Should not get here')
            ready.append(L[res])
            L = L[res+1:]
            timeout = 0
        rudisha ready

    _ready_errors = {_winapi.ERROR_BROKEN_PIPE, _winapi.ERROR_NETNAME_DELETED}

    eleza wait(object_list, timeout=None):
        '''
        Wait till an object in object_list is ready/readable.

        Returns list of those objects in object_list which are ready/readable.
        '''
        ikiwa timeout is None:
            timeout = INFINITE
        elikiwa timeout < 0:
            timeout = 0
        else:
            timeout = int(timeout * 1000 + 0.5)

        object_list = list(object_list)
        waithandle_to_obj = {}
        ov_list = []
        ready_objects = set()
        ready_handles = set()

        try:
            for o in object_list:
                try:
                    fileno = getattr(o, 'fileno')
                except AttributeError:
                    waithandle_to_obj[o.__index__()] = o
                else:
                    # start an overlapped read of length zero
                    try:
                        ov, err = _winapi.ReadFile(fileno(), 0, True)
                    except OSError as e:
                        ov, err = None, e.winerror
                        ikiwa err not in _ready_errors:
                            raise
                    ikiwa err == _winapi.ERROR_IO_PENDING:
                        ov_list.append(ov)
                        waithandle_to_obj[ov.event] = o
                    else:
                        # If o.fileno() is an overlapped pipe handle and
                        # err == 0 then there is a zero length message
                        # in the pipe, but it HAS NOT been consumed...
                        ikiwa ov and sys.getwindowsversion()[:2] >= (6, 2):
                            # ... except on Windows 8 and later, where
                            # the message HAS been consumed.
                            try:
                                _, err = ov.GetOverlappedResult(False)
                            except OSError as e:
                                err = e.winerror
                            ikiwa not err and hasattr(o, '_got_empty_message'):
                                o._got_empty_message = True
                        ready_objects.add(o)
                        timeout = 0

            ready_handles = _exhaustive_wait(waithandle_to_obj.keys(), timeout)
        finally:
            # request that overlapped reads stop
            for ov in ov_list:
                ov.cancel()

            # wait for all overlapped reads to stop
            for ov in ov_list:
                try:
                    _, err = ov.GetOverlappedResult(True)
                except OSError as e:
                    err = e.winerror
                    ikiwa err not in _ready_errors:
                        raise
                ikiwa err != _winapi.ERROR_OPERATION_ABORTED:
                    o = waithandle_to_obj[ov.event]
                    ready_objects.add(o)
                    ikiwa err == 0:
                        # If o.fileno() is an overlapped pipe handle then
                        # a zero length message HAS been consumed.
                        ikiwa hasattr(o, '_got_empty_message'):
                            o._got_empty_message = True

        ready_objects.update(waithandle_to_obj[h] for h in ready_handles)
        rudisha [o for o in object_list ikiwa o in ready_objects]

else:

    agiza selectors

    # poll/select have the advantage of not requiring any extra file
    # descriptor, contrarily to epoll/kqueue (also, they require a single
    # syscall).
    ikiwa hasattr(selectors, 'PollSelector'):
        _WaitSelector = selectors.PollSelector
    else:
        _WaitSelector = selectors.SelectSelector

    eleza wait(object_list, timeout=None):
        '''
        Wait till an object in object_list is ready/readable.

        Returns list of those objects in object_list which are ready/readable.
        '''
        with _WaitSelector() as selector:
            for obj in object_list:
                selector.register(obj, selectors.EVENT_READ)

            ikiwa timeout is not None:
                deadline = time.monotonic() + timeout

            while True:
                ready = selector.select(timeout)
                ikiwa ready:
                    rudisha [key.fileobj for (key, events) in ready]
                else:
                    ikiwa timeout is not None:
                        timeout = deadline - time.monotonic()
                        ikiwa timeout < 0:
                            rudisha ready

#
# Make connection and socket objects sharable ikiwa possible
#

ikiwa sys.platform == 'win32':
    eleza reduce_connection(conn):
        handle = conn.fileno()
        with socket.kutokafd(handle, socket.AF_INET, socket.SOCK_STREAM) as s:
            kutoka . agiza resource_sharer
            ds = resource_sharer.DupSocket(s)
            rudisha rebuild_connection, (ds, conn.readable, conn.writable)
    eleza rebuild_connection(ds, readable, writable):
        sock = ds.detach()
        rudisha Connection(sock.detach(), readable, writable)
    reduction.register(Connection, reduce_connection)

    eleza reduce_pipe_connection(conn):
        access = ((_winapi.FILE_GENERIC_READ ikiwa conn.readable else 0) |
                  (_winapi.FILE_GENERIC_WRITE ikiwa conn.writable else 0))
        dh = reduction.DupHandle(conn.fileno(), access)
        rudisha rebuild_pipe_connection, (dh, conn.readable, conn.writable)
    eleza rebuild_pipe_connection(dh, readable, writable):
        handle = dh.detach()
        rudisha PipeConnection(handle, readable, writable)
    reduction.register(PipeConnection, reduce_pipe_connection)

else:
    eleza reduce_connection(conn):
        df = reduction.DupFd(conn.fileno())
        rudisha rebuild_connection, (df, conn.readable, conn.writable)
    eleza rebuild_connection(df, readable, writable):
        fd = df.detach()
        rudisha Connection(fd, readable, writable)
    reduction.register(Connection, reduce_connection)
