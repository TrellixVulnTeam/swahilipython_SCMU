#
# A higher level module kila using sockets (or Windows named pipes)
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

jaribu:
    agiza _winapi
    kutoka _winapi agiza WAIT_OBJECT_0, WAIT_ABANDONED_0, WAIT_TIMEOUT, INFINITE
tatizo ImportError:
    ikiwa sys.platform == 'win32':
        raise
    _winapi = Tupu

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
    Return an arbitrary free address kila the given family
    '''
    ikiwa family == 'AF_INET':
        rudisha ('localhost', 0)
    lasivyo family == 'AF_UNIX':
        rudisha tempfile.mktemp(prefix='listener-', dir=util.get_temp_dir())
    lasivyo family == 'AF_PIPE':
        rudisha tempfile.mktemp(prefix=r'\\.\pipe\pyc-%d-%d-' %
                               (os.getpid(), next(_mmap_counter)), dir="")
    isipokua:
        ashiria ValueError('unrecognized family')

eleza _validate_family(family):
    '''
    Checks ikiwa the family ni valid kila the current environment.
    '''
    ikiwa sys.platform != 'win32' na family == 'AF_PIPE':
        ashiria ValueError('Family %s ni sio recognized.' % family)

    ikiwa sys.platform == 'win32' na family == 'AF_UNIX':
        # double check
        ikiwa sio hasattr(socket, family):
            ashiria ValueError('Family %s ni sio recognized.' % family)

eleza address_type(address):
    '''
    Return the types of the address

    This can be 'AF_INET', 'AF_UNIX', ama 'AF_PIPE'
    '''
    ikiwa type(address) == tuple:
        rudisha 'AF_INET'
    lasivyo type(address) ni str na address.startswith('\\\\'):
        rudisha 'AF_PIPE'
    lasivyo type(address) ni str:
        rudisha 'AF_UNIX'
    isipokua:
        ashiria ValueError('address type of %r unrecognized' % address)

#
# Connection classes
#

kundi _ConnectionBase:
    _handle = Tupu

    eleza __init__(self, handle, readable=Kweli, writable=Kweli):
        handle = handle.__index__()
        ikiwa handle < 0:
            ashiria ValueError("invalid handle")
        ikiwa sio readable na sio writable:
            ashiria ValueError(
                "at least one of `readable` na `writable` must be Kweli")
        self._handle = handle
        self._readable = readable
        self._writable = writable

    # XXX should we use util.Finalize instead of a __del__?

    eleza __del__(self):
        ikiwa self._handle ni sio Tupu:
            self._close()

    eleza _check_closed(self):
        ikiwa self._handle ni Tupu:
            ashiria OSError("handle ni closed")

    eleza _check_readable(self):
        ikiwa sio self._readable:
            ashiria OSError("connection ni write-only")

    eleza _check_writable(self):
        ikiwa sio self._writable:
            ashiria OSError("connection ni read-only")

    eleza _bad_message_length(self):
        ikiwa self._writable:
            self._readable = Uongo
        isipokua:
            self.close()
        ashiria OSError("bad message length")

    @property
    eleza closed(self):
        """Kweli ikiwa the connection ni closed"""
        rudisha self._handle ni Tupu

    @property
    eleza readable(self):
        """Kweli ikiwa the connection ni readable"""
        rudisha self._readable

    @property
    eleza writable(self):
        """Kweli ikiwa the connection ni writable"""
        rudisha self._writable

    eleza fileno(self):
        """File descriptor ama handle of the connection"""
        self._check_closed()
        rudisha self._handle

    eleza close(self):
        """Close the connection"""
        ikiwa self._handle ni sio Tupu:
            jaribu:
                self._close()
            mwishowe:
                self._handle = Tupu

    eleza send_bytes(self, buf, offset=0, size=Tupu):
        """Send the bytes data kutoka a bytes-like object"""
        self._check_closed()
        self._check_writable()
        m = memoryview(buf)
        # HACK kila byte-indexing of non-bytewise buffers (e.g. array.array)
        ikiwa m.itemsize > 1:
            m = memoryview(bytes(m))
        n = len(m)
        ikiwa offset < 0:
            ashiria ValueError("offset ni negative")
        ikiwa n < offset:
            ashiria ValueError("buffer length < offset")
        ikiwa size ni Tupu:
            size = n - offset
        lasivyo size < 0:
            ashiria ValueError("size ni negative")
        lasivyo offset + size > n:
            ashiria ValueError("buffer length < offset + size")
        self._send_bytes(m[offset:offset + size])

    eleza send(self, obj):
        """Send a (picklable) object"""
        self._check_closed()
        self._check_writable()
        self._send_bytes(_ForkingPickler.dumps(obj))

    eleza recv_bytes(self, maxlength=Tupu):
        """
        Receive bytes data kama a bytes object.
        """
        self._check_closed()
        self._check_readable()
        ikiwa maxlength ni sio Tupu na maxlength < 0:
            ashiria ValueError("negative maxlength")
        buf = self._recv_bytes(maxlength)
        ikiwa buf ni Tupu:
            self._bad_message_length()
        rudisha buf.getvalue()

    eleza recv_bytes_into(self, buf, offset=0):
        """
        Receive bytes data into a writeable bytes-like object.
        Return the number of bytes read.
        """
        self._check_closed()
        self._check_readable()
        ukijumuisha memoryview(buf) kama m:
            # Get bytesize of arbitrary buffer
            itemsize = m.itemsize
            bytesize = itemsize * len(m)
            ikiwa offset < 0:
                ashiria ValueError("negative offset")
            lasivyo offset > bytesize:
                ashiria ValueError("offset too large")
            result = self._recv_bytes()
            size = result.tell()
            ikiwa bytesize < offset + size:
                ashiria BufferTooShort(result.getvalue())
            # Message can fit kwenye dest
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
        """Whether there ni any input available to be read"""
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
        Overlapped I/O ni used, so the handles must have been created
        ukijumuisha FILE_FLAG_OVERLAPPED.
        """
        _got_empty_message = Uongo

        eleza _close(self, _CloseHandle=_winapi.CloseHandle):
            _CloseHandle(self._handle)

        eleza _send_bytes(self, buf):
            ov, err = _winapi.WriteFile(self._handle, buf, overlapped=Kweli)
            jaribu:
                ikiwa err == _winapi.ERROR_IO_PENDING:
                    waitres = _winapi.WaitForMultipleObjects(
                        [ov.event], Uongo, INFINITE)
                    assert waitres == WAIT_OBJECT_0
            tatizo:
                ov.cancel()
                raise
            mwishowe:
                nwritten, err = ov.GetOverlappedResult(Kweli)
            assert err == 0
            assert nwritten == len(buf)

        eleza _recv_bytes(self, maxsize=Tupu):
            ikiwa self._got_empty_message:
                self._got_empty_message = Uongo
                rudisha io.BytesIO()
            isipokua:
                bsize = 128 ikiwa maxsize ni Tupu isipokua min(maxsize, 128)
                jaribu:
                    ov, err = _winapi.ReadFile(self._handle, bsize,
                                                overlapped=Kweli)
                    jaribu:
                        ikiwa err == _winapi.ERROR_IO_PENDING:
                            waitres = _winapi.WaitForMultipleObjects(
                                [ov.event], Uongo, INFINITE)
                            assert waitres == WAIT_OBJECT_0
                    tatizo:
                        ov.cancel()
                        raise
                    mwishowe:
                        nread, err = ov.GetOverlappedResult(Kweli)
                        ikiwa err == 0:
                            f = io.BytesIO()
                            f.write(ov.getbuffer())
                            rudisha f
                        lasivyo err == _winapi.ERROR_MORE_DATA:
                            rudisha self._get_more_data(ov, maxsize)
                tatizo OSError kama e:
                    ikiwa e.winerror == _winapi.ERROR_BROKEN_PIPE:
                        ashiria EOFError
                    isipokua:
                        raise
            ashiria RuntimeError("shouldn't get here; expected KeyboardInterrupt")

        eleza _poll(self, timeout):
            ikiwa (self._got_empty_message ama
                        _winapi.PeekNamedPipe(self._handle)[0] != 0):
                rudisha Kweli
            rudisha bool(wait([self], timeout))

        eleza _get_more_data(self, ov, maxsize):
            buf = ov.getbuffer()
            f = io.BytesIO()
            f.write(buf)
            left = _winapi.PeekNamedPipe(self._handle)[1]
            assert left > 0
            ikiwa maxsize ni sio Tupu na len(buf) + left > maxsize:
                self._bad_message_length()
            ov, err = _winapi.ReadFile(self._handle, left, overlapped=Kweli)
            rbytes, err = ov.GetOverlappedResult(Kweli)
            assert err == 0
            assert rbytes == left
            f.write(ov.getbuffer())
            rudisha f


kundi Connection(_ConnectionBase):
    """
    Connection kundi based on an arbitrary file descriptor (Unix only), ama
    a socket handle (Windows).
    """

    ikiwa _winapi:
        eleza _close(self, _close=_multiprocessing.closesocket):
            _close(self._handle)
        _write = _multiprocessing.send
        _read = _multiprocessing.recv
    isipokua:
        eleza _close(self, _close=os.close):
            _close(self._handle)
        _write = os.write
        _read = os.read

    eleza _send(self, buf, write=_write):
        remaining = len(buf)
        wakati Kweli:
            n = write(self._handle, buf)
            remaining -= n
            ikiwa remaining == 0:
                koma
            buf = buf[n:]

    eleza _recv(self, size, read=_read):
        buf = io.BytesIO()
        handle = self._handle
        remaining = size
        wakati remaining > 0:
            chunk = read(handle, remaining)
            n = len(chunk)
            ikiwa n == 0:
                ikiwa remaining == size:
                    ashiria EOFError
                isipokua:
                    ashiria OSError("got end of file during message")
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
        isipokua:
            # For wire compatibility ukijumuisha 3.7 na lower
            header = struct.pack("!i", n)
            ikiwa n > 16384:
                # The payload ni large so Nagle's algorithm won't be triggered
                # na we'd better avoid the cost of concatenation.
                self._send(header)
                self._send(buf)
            isipokua:
                # Issue #20540: concatenate before sending, to avoid delays due
                # to Nagle's algorithm on a TCP socket.
                # Also note we want to avoid sending a 0-length buffer separately,
                # to avoid "broken pipe" errors ikiwa the other end closed the pipe.
                self._send(header + buf)

    eleza _recv_bytes(self, maxsize=Tupu):
        buf = self._recv(4)
        size, = struct.unpack("!i", buf.getvalue())
        ikiwa size == -1:
            buf = self._recv(8)
            size, = struct.unpack("!Q", buf.getvalue())
        ikiwa maxsize ni sio Tupu na size > maxsize:
            rudisha Tupu
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

    This ni a wrapper kila a bound socket which ni 'listening' for
    connections, ama kila a Windows named pipe.
    '''
    eleza __init__(self, address=Tupu, family=Tupu, backlog=1, authkey=Tupu):
        family = family ama (address na address_type(address)) \
                 ama default_family
        address = address ama arbitrary_address(family)

        _validate_family(family)
        ikiwa family == 'AF_PIPE':
            self._listener = PipeListener(address, backlog)
        isipokua:
            self._listener = SocketListener(address, family, backlog)

        ikiwa authkey ni sio Tupu na sio isinstance(authkey, bytes):
            ashiria TypeError('authkey should be a byte string')

        self._authkey = authkey

    eleza accept(self):
        '''
        Accept a connection on the bound socket ama named pipe of `self`.

        Returns a `Connection` object.
        '''
        ikiwa self._listener ni Tupu:
            ashiria OSError('listener ni closed')
        c = self._listener.accept()
        ikiwa self._authkey:
            deliver_challenge(c, self._authkey)
            answer_challenge(c, self._authkey)
        rudisha c

    eleza close(self):
        '''
        Close the bound socket ama named pipe of `self`.
        '''
        listener = self._listener
        ikiwa listener ni sio Tupu:
            self._listener = Tupu
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


eleza Client(address, family=Tupu, authkey=Tupu):
    '''
    Returns a connection to the address of a `Listener`
    '''
    family = family ama address_type(address)
    _validate_family(family)
    ikiwa family == 'AF_PIPE':
        c = PipeClient(address)
    isipokua:
        c = SocketClient(address)

    ikiwa authkey ni sio Tupu na sio isinstance(authkey, bytes):
        ashiria TypeError('authkey should be a byte string')

    ikiwa authkey ni sio Tupu:
        answer_challenge(c, authkey)
        deliver_challenge(c, authkey)

    rudisha c


ikiwa sys.platform != 'win32':

    eleza Pipe(duplex=Kweli):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        ikiwa duplex:
            s1, s2 = socket.socketpair()
            s1.setblocking(Kweli)
            s2.setblocking(Kweli)
            c1 = Connection(s1.detach())
            c2 = Connection(s2.detach())
        isipokua:
            fd1, fd2 = os.pipe()
            c1 = Connection(fd1, writable=Uongo)
            c2 = Connection(fd2, readable=Uongo)

        rudisha c1, c2

isipokua:

    eleza Pipe(duplex=Kweli):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        address = arbitrary_address('AF_PIPE')
        ikiwa duplex:
            openmode = _winapi.PIPE_ACCESS_DUPLEX
            access = _winapi.GENERIC_READ | _winapi.GENERIC_WRITE
            obsize, ibsize = BUFSIZE, BUFSIZE
        isipokua:
            openmode = _winapi.PIPE_ACCESS_INBOUND
            access = _winapi.GENERIC_WRITE
            obsize, ibsize = 0, BUFSIZE

        h1 = _winapi.CreateNamedPipe(
            address, openmode | _winapi.FILE_FLAG_OVERLAPPED |
            _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE,
            _winapi.PIPE_TYPE_MESSAGE | _winapi.PIPE_READMODE_MESSAGE |
            _winapi.PIPE_WAIT,
            1, obsize, ibsize, _winapi.NMPWAIT_WAIT_FOREVER,
            # default security descriptor: the handle cansio be inherited
            _winapi.NULL
            )
        h2 = _winapi.CreateFile(
            address, access, 0, _winapi.NULL, _winapi.OPEN_EXISTING,
            _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL
            )
        _winapi.SetNamedPipeHandleState(
            h2, _winapi.PIPE_READMODE_MESSAGE, Tupu, Tupu
            )

        overlapped = _winapi.ConnectNamedPipe(h1, overlapped=Kweli)
        _, err = overlapped.GetOverlappedResult(Kweli)
        assert err == 0

        c1 = PipeConnection(h1, writable=duplex)
        c2 = PipeConnection(h2, readable=duplex)

        rudisha c1, c2

#
# Definitions kila connections based on sockets
#

kundi SocketListener(object):
    '''
    Representation of a socket which ni bound to an address na listening
    '''
    eleza __init__(self, address, family, backlog=1):
        self._socket = socket.socket(getattr(socket, family))
        jaribu:
            # SO_REUSEADDR has different semantics on Windows (issue #2550).
            ikiwa os.name == 'posix':
                self._socket.setsockopt(socket.SOL_SOCKET,
                                        socket.SO_REUSEADDR, 1)
            self._socket.setblocking(Kweli)
            self._socket.bind(address)
            self._socket.listen(backlog)
            self._address = self._socket.getsockname()
        tatizo OSError:
            self._socket.close()
            raise
        self._family = family
        self._last_accepted = Tupu

        ikiwa family == 'AF_UNIX':
            self._unlink = util.Finalize(
                self, os.unlink, args=(address,), exitpriority=0
                )
        isipokua:
            self._unlink = Tupu

    eleza accept(self):
        s, self._last_accepted = self._socket.accept()
        s.setblocking(Kweli)
        rudisha Connection(s.detach())

    eleza close(self):
        jaribu:
            self._socket.close()
        mwishowe:
            unlink = self._unlink
            ikiwa unlink ni sio Tupu:
                self._unlink = Tupu
                unlink()


eleza SocketClient(address):
    '''
    Return a connection object connected to the socket given by `address`
    '''
    family = address_type(address)
    ukijumuisha socket.socket( getattr(socket, family) ) kama s:
        s.setblocking(Kweli)
        s.connect(address)
        rudisha Connection(s.detach())

#
# Definitions kila connections based on named pipes
#

ikiwa sys.platform == 'win32':

    kundi PipeListener(object):
        '''
        Representation of a named pipe
        '''
        eleza __init__(self, address, backlog=Tupu):
            self._address = address
            self._handle_queue = [self._new_handle(first=Kweli)]

            self._last_accepted = Tupu
            util.sub_debug('listener created ukijumuisha address=%r', self._address)
            self.close = util.Finalize(
                self, PipeListener._finalize_pipe_listener,
                args=(self._handle_queue, self._address), exitpriority=0
                )

        eleza _new_handle(self, first=Uongo):
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
            jaribu:
                ov = _winapi.ConnectNamedPipe(handle, overlapped=Kweli)
            tatizo OSError kama e:
                ikiwa e.winerror != _winapi.ERROR_NO_DATA:
                    raise
                # ERROR_NO_DATA can occur ikiwa a client has already connected,
                # written data na then disconnected -- see Issue 14725.
            isipokua:
                jaribu:
                    res = _winapi.WaitForMultipleObjects(
                        [ov.event], Uongo, INFINITE)
                tatizo:
                    ov.cancel()
                    _winapi.CloseHandle(handle)
                    raise
                mwishowe:
                    _, err = ov.GetOverlappedResult(Kweli)
                    assert err == 0
            rudisha PipeConnection(handle)

        @staticmethod
        eleza _finalize_pipe_listener(queue, address):
            util.sub_debug('closing listener ukijumuisha address=%r', address)
            kila handle kwenye queue:
                _winapi.CloseHandle(handle)

    eleza PipeClient(address):
        '''
        Return a connection object connected to the pipe given by `address`
        '''
        t = _init_timeout()
        wakati 1:
            jaribu:
                _winapi.WaitNamedPipe(address, 1000)
                h = _winapi.CreateFile(
                    address, _winapi.GENERIC_READ | _winapi.GENERIC_WRITE,
                    0, _winapi.NULL, _winapi.OPEN_EXISTING,
                    _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL
                    )
            tatizo OSError kama e:
                ikiwa e.winerror haiko kwenye (_winapi.ERROR_SEM_TIMEOUT,
                                      _winapi.ERROR_PIPE_BUSY) ama _check_timeout(t):
                    raise
            isipokua:
                koma
        isipokua:
            raise

        _winapi.SetNamedPipeHandleState(
            h, _winapi.PIPE_READMODE_MESSAGE, Tupu, Tupu
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
    ikiwa sio isinstance(authkey, bytes):
        ashiria ValueError(
            "Authkey must be bytes, sio {0!s}".format(type(authkey)))
    message = os.urandom(MESSAGE_LENGTH)
    connection.send_bytes(CHALLENGE + message)
    digest = hmac.new(authkey, message, 'md5').digest()
    response = connection.recv_bytes(256)        # reject large message
    ikiwa response == digest:
        connection.send_bytes(WELCOME)
    isipokua:
        connection.send_bytes(FAILURE)
        ashiria AuthenticationError('digest received was wrong')

eleza answer_challenge(connection, authkey):
    agiza hmac
    ikiwa sio isinstance(authkey, bytes):
        ashiria ValueError(
            "Authkey must be bytes, sio {0!s}".format(type(authkey)))
    message = connection.recv_bytes(256)         # reject large message
    assert message[:len(CHALLENGE)] == CHALLENGE, 'message = %r' % message
    message = message[len(CHALLENGE):]
    digest = hmac.new(authkey, message, 'md5').digest()
    connection.send_bytes(digest)
    response = connection.recv_bytes(256)        # reject large message
    ikiwa response != WELCOME:
        ashiria AuthenticationError('digest sent was rejected')

#
# Support kila using xmlrpclib kila serialization
#

kundi ConnectionWrapper(object):
    eleza __init__(self, conn, dumps, loads):
        self._conn = conn
        self._dumps = dumps
        self._loads = loads
        kila attr kwenye ('fileno', 'close', 'poll', 'recv_bytes', 'send_bytes'):
            obj = getattr(conn, attr)
            setattr(self, attr, obj)
    eleza send(self, obj):
        s = self._dumps(obj)
        self._conn.send_bytes(s)
    eleza recv(self):
        s = self._conn.recv_bytes()
        rudisha self._loads(s)

eleza _xml_dumps(obj):
    rudisha xmlrpclib.dumps((obj,), Tupu, Tupu, Tupu, 1).encode('utf-8')

eleza _xml_loads(s):
    (obj,), method = xmlrpclib.loads(s.decode('utf-8'))
    rudisha obj

kundi XmlListener(Listener):
    eleza accept(self):
        global xmlrpclib
        agiza xmlrpc.client kama xmlrpclib
        obj = Listener.accept(self)
        rudisha ConnectionWrapper(obj, _xml_dumps, _xml_loads)

eleza XmlClient(*args, **kwds):
    global xmlrpclib
    agiza xmlrpc.client kama xmlrpclib
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
        wakati L:
            res = _winapi.WaitForMultipleObjects(L, Uongo, timeout)
            ikiwa res == WAIT_TIMEOUT:
                koma
            lasivyo WAIT_OBJECT_0 <= res < WAIT_OBJECT_0 + len(L):
                res -= WAIT_OBJECT_0
            lasivyo WAIT_ABANDONED_0 <= res < WAIT_ABANDONED_0 + len(L):
                res -= WAIT_ABANDONED_0
            isipokua:
                ashiria RuntimeError('Should sio get here')
            ready.append(L[res])
            L = L[res+1:]
            timeout = 0
        rudisha ready

    _ready_errors = {_winapi.ERROR_BROKEN_PIPE, _winapi.ERROR_NETNAME_DELETED}

    eleza wait(object_list, timeout=Tupu):
        '''
        Wait till an object kwenye object_list ni ready/readable.

        Returns list of those objects kwenye object_list which are ready/readable.
        '''
        ikiwa timeout ni Tupu:
            timeout = INFINITE
        lasivyo timeout < 0:
            timeout = 0
        isipokua:
            timeout = int(timeout * 1000 + 0.5)

        object_list = list(object_list)
        waithandle_to_obj = {}
        ov_list = []
        ready_objects = set()
        ready_handles = set()

        jaribu:
            kila o kwenye object_list:
                jaribu:
                    fileno = getattr(o, 'fileno')
                tatizo AttributeError:
                    waithandle_to_obj[o.__index__()] = o
                isipokua:
                    # start an overlapped read of length zero
                    jaribu:
                        ov, err = _winapi.ReadFile(fileno(), 0, Kweli)
                    tatizo OSError kama e:
                        ov, err = Tupu, e.winerror
                        ikiwa err haiko kwenye _ready_errors:
                            raise
                    ikiwa err == _winapi.ERROR_IO_PENDING:
                        ov_list.append(ov)
                        waithandle_to_obj[ov.event] = o
                    isipokua:
                        # If o.fileno() ni an overlapped pipe handle na
                        # err == 0 then there ni a zero length message
                        # kwenye the pipe, but it HAS NOT been consumed...
                        ikiwa ov na sys.getwindowsversion()[:2] >= (6, 2):
                            # ... tatizo on Windows 8 na later, where
                            # the message HAS been consumed.
                            jaribu:
                                _, err = ov.GetOverlappedResult(Uongo)
                            tatizo OSError kama e:
                                err = e.winerror
                            ikiwa sio err na hasattr(o, '_got_empty_message'):
                                o._got_empty_message = Kweli
                        ready_objects.add(o)
                        timeout = 0

            ready_handles = _exhaustive_wait(waithandle_to_obj.keys(), timeout)
        mwishowe:
            # request that overlapped reads stop
            kila ov kwenye ov_list:
                ov.cancel()

            # wait kila all overlapped reads to stop
            kila ov kwenye ov_list:
                jaribu:
                    _, err = ov.GetOverlappedResult(Kweli)
                tatizo OSError kama e:
                    err = e.winerror
                    ikiwa err haiko kwenye _ready_errors:
                        raise
                ikiwa err != _winapi.ERROR_OPERATION_ABORTED:
                    o = waithandle_to_obj[ov.event]
                    ready_objects.add(o)
                    ikiwa err == 0:
                        # If o.fileno() ni an overlapped pipe handle then
                        # a zero length message HAS been consumed.
                        ikiwa hasattr(o, '_got_empty_message'):
                            o._got_empty_message = Kweli

        ready_objects.update(waithandle_to_obj[h] kila h kwenye ready_handles)
        rudisha [o kila o kwenye object_list ikiwa o kwenye ready_objects]

isipokua:

    agiza selectors

    # poll/select have the advantage of sio requiring any extra file
    # descriptor, contrarily to epoll/kqueue (also, they require a single
    # syscall).
    ikiwa hasattr(selectors, 'PollSelector'):
        _WaitSelector = selectors.PollSelector
    isipokua:
        _WaitSelector = selectors.SelectSelector

    eleza wait(object_list, timeout=Tupu):
        '''
        Wait till an object kwenye object_list ni ready/readable.

        Returns list of those objects kwenye object_list which are ready/readable.
        '''
        ukijumuisha _WaitSelector() kama selector:
            kila obj kwenye object_list:
                selector.register(obj, selectors.EVENT_READ)

            ikiwa timeout ni sio Tupu:
                deadline = time.monotonic() + timeout

            wakati Kweli:
                ready = selector.select(timeout)
                ikiwa ready:
                    rudisha [key.fileobj kila (key, events) kwenye ready]
                isipokua:
                    ikiwa timeout ni sio Tupu:
                        timeout = deadline - time.monotonic()
                        ikiwa timeout < 0:
                            rudisha ready

#
# Make connection na socket objects sharable ikiwa possible
#

ikiwa sys.platform == 'win32':
    eleza reduce_connection(conn):
        handle = conn.fileno()
        ukijumuisha socket.fromfd(handle, socket.AF_INET, socket.SOCK_STREAM) kama s:
            kutoka . agiza resource_sharer
            ds = resource_sharer.DupSocket(s)
            rudisha rebuild_connection, (ds, conn.readable, conn.writable)
    eleza rebuild_connection(ds, readable, writable):
        sock = ds.detach()
        rudisha Connection(sock.detach(), readable, writable)
    reduction.register(Connection, reduce_connection)

    eleza reduce_pipe_connection(conn):
        access = ((_winapi.FILE_GENERIC_READ ikiwa conn.readable isipokua 0) |
                  (_winapi.FILE_GENERIC_WRITE ikiwa conn.writable isipokua 0))
        dh = reduction.DupHandle(conn.fileno(), access)
        rudisha rebuild_pipe_connection, (dh, conn.readable, conn.writable)
    eleza rebuild_pipe_connection(dh, readable, writable):
        handle = dh.detach()
        rudisha PipeConnection(handle, readable, writable)
    reduction.register(PipeConnection, reduce_pipe_connection)

isipokua:
    eleza reduce_connection(conn):
        df = reduction.DupFd(conn.fileno())
        rudisha rebuild_connection, (df, conn.readable, conn.writable)
    eleza rebuild_connection(df, readable, writable):
        fd = df.detach()
        rudisha Connection(fd, readable, writable)
    reduction.register(Connection, reduce_connection)
