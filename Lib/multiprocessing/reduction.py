#
# Module which deals with pickling of objects.
#
# multiprocessing/reduction.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

kutoka abc agiza ABCMeta
agiza copyreg
agiza functools
agiza io
agiza os
agiza pickle
agiza socket
agiza sys

kutoka . agiza context

__all__ = ['send_handle', 'recv_handle', 'ForkingPickler', 'register', 'dump']


HAVE_SEND_HANDLE = (sys.platform == 'win32' or
                    (hasattr(socket, 'CMSG_LEN') and
                     hasattr(socket, 'SCM_RIGHTS') and
                     hasattr(socket.socket, 'sendmsg')))

#
# Pickler subclass
#

kundi ForkingPickler(pickle.Pickler):
    '''Pickler subkundi used by multiprocessing.'''
    _extra_reducers = {}
    _copyreg_dispatch_table = copyreg.dispatch_table

    eleza __init__(self, *args):
        super().__init__(*args)
        self.dispatch_table = self._copyreg_dispatch_table.copy()
        self.dispatch_table.update(self._extra_reducers)

    @classmethod
    eleza register(cls, type, reduce):
        '''Register a reduce function for a type.'''
        cls._extra_reducers[type] = reduce

    @classmethod
    eleza dumps(cls, obj, protocol=None):
        buf = io.BytesIO()
        cls(buf, protocol).dump(obj)
        rudisha buf.getbuffer()

    loads = pickle.loads

register = ForkingPickler.register

eleza dump(obj, file, protocol=None):
    '''Replacement for pickle.dump() using ForkingPickler.'''
    ForkingPickler(file, protocol).dump(obj)

#
# Platform specific definitions
#

ikiwa sys.platform == 'win32':
    # Windows
    __all__ += ['DupHandle', 'duplicate', 'steal_handle']
    agiza _winapi

    eleza duplicate(handle, target_process=None, inheritable=False,
                  *, source_process=None):
        '''Duplicate a handle.  (target_process is a handle not a pid!)'''
        current_process = _winapi.GetCurrentProcess()
        ikiwa source_process is None:
            source_process = current_process
        ikiwa target_process is None:
            target_process = current_process
        rudisha _winapi.DuplicateHandle(
            source_process, handle, target_process,
            0, inheritable, _winapi.DUPLICATE_SAME_ACCESS)

    eleza steal_handle(source_pid, handle):
        '''Steal a handle kutoka process identified by source_pid.'''
        source_process_handle = _winapi.OpenProcess(
            _winapi.PROCESS_DUP_HANDLE, False, source_pid)
        try:
            rudisha _winapi.DuplicateHandle(
                source_process_handle, handle,
                _winapi.GetCurrentProcess(), 0, False,
                _winapi.DUPLICATE_SAME_ACCESS | _winapi.DUPLICATE_CLOSE_SOURCE)
        finally:
            _winapi.CloseHandle(source_process_handle)

    eleza send_handle(conn, handle, destination_pid):
        '''Send a handle over a local connection.'''
        dh = DupHandle(handle, _winapi.DUPLICATE_SAME_ACCESS, destination_pid)
        conn.send(dh)

    eleza recv_handle(conn):
        '''Receive a handle over a local connection.'''
        rudisha conn.recv().detach()

    kundi DupHandle(object):
        '''Picklable wrapper for a handle.'''
        eleza __init__(self, handle, access, pid=None):
            ikiwa pid is None:
                # We just duplicate the handle in the current process and
                # let the receiving process steal the handle.
                pid = os.getpid()
            proc = _winapi.OpenProcess(_winapi.PROCESS_DUP_HANDLE, False, pid)
            try:
                self._handle = _winapi.DuplicateHandle(
                    _winapi.GetCurrentProcess(),
                    handle, proc, access, False, 0)
            finally:
                _winapi.CloseHandle(proc)
            self._access = access
            self._pid = pid

        eleza detach(self):
            '''Get the handle.  This should only be called once.'''
            # retrieve handle kutoka process which currently owns it
            ikiwa self._pid == os.getpid():
                # The handle has already been duplicated for this process.
                rudisha self._handle
            # We must steal the handle kutoka the process whose pid is self._pid.
            proc = _winapi.OpenProcess(_winapi.PROCESS_DUP_HANDLE, False,
                                       self._pid)
            try:
                rudisha _winapi.DuplicateHandle(
                    proc, self._handle, _winapi.GetCurrentProcess(),
                    self._access, False, _winapi.DUPLICATE_CLOSE_SOURCE)
            finally:
                _winapi.CloseHandle(proc)

else:
    # Unix
    __all__ += ['DupFd', 'sendfds', 'recvfds']
    agiza array

    # On MacOSX we should acknowledge receipt of fds -- see Issue14669
    ACKNOWLEDGE = sys.platform == 'darwin'

    eleza sendfds(sock, fds):
        '''Send an array of fds over an AF_UNIX socket.'''
        fds = array.array('i', fds)
        msg = bytes([len(fds) % 256])
        sock.sendmsg([msg], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds)])
        ikiwa ACKNOWLEDGE and sock.recv(1) != b'A':
            raise RuntimeError('did not receive acknowledgement of fd')

    eleza recvfds(sock, size):
        '''Receive an array of fds over an AF_UNIX socket.'''
        a = array.array('i')
        bytes_size = a.itemsize * size
        msg, ancdata, flags, addr = sock.recvmsg(1, socket.CMSG_SPACE(bytes_size))
        ikiwa not msg and not ancdata:
            raise EOFError
        try:
            ikiwa ACKNOWLEDGE:
                sock.send(b'A')
            ikiwa len(ancdata) != 1:
                raise RuntimeError('received %d items of ancdata' %
                                   len(ancdata))
            cmsg_level, cmsg_type, cmsg_data = ancdata[0]
            ikiwa (cmsg_level == socket.SOL_SOCKET and
                cmsg_type == socket.SCM_RIGHTS):
                ikiwa len(cmsg_data) % a.itemsize != 0:
                    raise ValueError
                a.kutokabytes(cmsg_data)
                ikiwa len(a) % 256 != msg[0]:
                    raise AssertionError(
                        "Len is {0:n} but msg[0] is {1!r}".format(
                            len(a), msg[0]))
                rudisha list(a)
        except (ValueError, IndexError):
            pass
        raise RuntimeError('Invalid data received')

    eleza send_handle(conn, handle, destination_pid):
        '''Send a handle over a local connection.'''
        with socket.kutokafd(conn.fileno(), socket.AF_UNIX, socket.SOCK_STREAM) as s:
            sendfds(s, [handle])

    eleza recv_handle(conn):
        '''Receive a handle over a local connection.'''
        with socket.kutokafd(conn.fileno(), socket.AF_UNIX, socket.SOCK_STREAM) as s:
            rudisha recvfds(s, 1)[0]

    eleza DupFd(fd):
        '''Return a wrapper for an fd.'''
        popen_obj = context.get_spawning_popen()
        ikiwa popen_obj is not None:
            rudisha popen_obj.DupFd(popen_obj.duplicate_for_child(fd))
        elikiwa HAVE_SEND_HANDLE:
            kutoka . agiza resource_sharer
            rudisha resource_sharer.DupFd(fd)
        else:
            raise ValueError('SCM_RIGHTS appears not to be available')

#
# Try making some callable types picklable
#

eleza _reduce_method(m):
    ikiwa m.__self__ is None:
        rudisha getattr, (m.__class__, m.__func__.__name__)
    else:
        rudisha getattr, (m.__self__, m.__func__.__name__)
kundi _C:
    eleza f(self):
        pass
register(type(_C().f), _reduce_method)


eleza _reduce_method_descriptor(m):
    rudisha getattr, (m.__objclass__, m.__name__)
register(type(list.append), _reduce_method_descriptor)
register(type(int.__add__), _reduce_method_descriptor)


eleza _reduce_partial(p):
    rudisha _rebuild_partial, (p.func, p.args, p.keywords or {})
eleza _rebuild_partial(func, args, keywords):
    rudisha functools.partial(func, *args, **keywords)
register(functools.partial, _reduce_partial)

#
# Make sockets picklable
#

ikiwa sys.platform == 'win32':
    eleza _reduce_socket(s):
        kutoka .resource_sharer agiza DupSocket
        rudisha _rebuild_socket, (DupSocket(s),)
    eleza _rebuild_socket(ds):
        rudisha ds.detach()
    register(socket.socket, _reduce_socket)

else:
    eleza _reduce_socket(s):
        df = DupFd(s.fileno())
        rudisha _rebuild_socket, (df, s.family, s.type, s.proto)
    eleza _rebuild_socket(df, family, type, proto):
        fd = df.detach()
        rudisha socket.socket(family, type, proto, fileno=fd)
    register(socket.socket, _reduce_socket)


kundi AbstractReducer(metaclass=ABCMeta):
    '''Abstract base kundi for use in implementing a Reduction class
    suitable for use in replacing the standard reduction mechanism
    used in multiprocessing.'''
    ForkingPickler = ForkingPickler
    register = register
    dump = dump
    send_handle = send_handle
    recv_handle = recv_handle

    ikiwa sys.platform == 'win32':
        steal_handle = steal_handle
        duplicate = duplicate
        DupHandle = DupHandle
    else:
        sendfds = sendfds
        recvfds = recvfds
        DupFd = DupFd

    _reduce_method = _reduce_method
    _reduce_method_descriptor = _reduce_method_descriptor
    _rebuild_partial = _rebuild_partial
    _reduce_socket = _reduce_socket
    _rebuild_socket = _rebuild_socket

    eleza __init__(self, *args):
        register(type(_C().f), _reduce_method)
        register(type(list.append), _reduce_method_descriptor)
        register(type(int.__add__), _reduce_method_descriptor)
        register(functools.partial, _reduce_partial)
        register(socket.socket, _reduce_socket)
