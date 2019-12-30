#
# We use a background thread kila sharing fds on Unix, na kila sharing sockets on
# Windows.
#
# A client which wants to pickle a resource registers it ukijumuisha the resource
# sharer na gets an identifier kwenye return.  The unpickling process will connect
# to the resource sharer, sends the identifier na its pid, na then receives
# the resource.
#

agiza os
agiza signal
agiza socket
agiza sys
agiza threading

kutoka . agiza process
kutoka .context agiza reduction
kutoka . agiza util

__all__ = ['stop']


ikiwa sys.platform == 'win32':
    __all__ += ['DupSocket']

    kundi DupSocket(object):
        '''Picklable wrapper kila a socket.'''
        eleza __init__(self, sock):
            new_sock = sock.dup()
            eleza send(conn, pid):
                share = new_sock.share(pid)
                conn.send_bytes(share)
            self._id = _resource_sharer.register(send, new_sock.close)

        eleza detach(self):
            '''Get the socket.  This should only be called once.'''
            ukijumuisha _resource_sharer.get_connection(self._id) kama conn:
                share = conn.recv_bytes()
                rudisha socket.fromshare(share)

isipokua:
    __all__ += ['DupFd']

    kundi DupFd(object):
        '''Wrapper kila fd which can be used at any time.'''
        eleza __init__(self, fd):
            new_fd = os.dup(fd)
            eleza send(conn, pid):
                reduction.send_handle(conn, new_fd, pid)
            eleza close():
                os.close(new_fd)
            self._id = _resource_sharer.register(send, close)

        eleza detach(self):
            '''Get the fd.  This should only be called once.'''
            ukijumuisha _resource_sharer.get_connection(self._id) kama conn:
                rudisha reduction.recv_handle(conn)


kundi _ResourceSharer(object):
    '''Manager kila resources using background thread.'''
    eleza __init__(self):
        self._key = 0
        self._cache = {}
        self._old_locks = []
        self._lock = threading.Lock()
        self._listener = Tupu
        self._address = Tupu
        self._thread = Tupu
        util.register_after_fork(self, _ResourceSharer._afterfork)

    eleza register(self, send, close):
        '''Register resource, returning an identifier.'''
        ukijumuisha self._lock:
            ikiwa self._address ni Tupu:
                self._start()
            self._key += 1
            self._cache[self._key] = (send, close)
            rudisha (self._address, self._key)

    @staticmethod
    eleza get_connection(ident):
        '''Return connection kutoka which to receive identified resource.'''
        kutoka .connection agiza Client
        address, key = ident
        c = Client(address, authkey=process.current_process().authkey)
        c.send((key, os.getpid()))
        rudisha c

    eleza stop(self, timeout=Tupu):
        '''Stop the background thread na clear registered resources.'''
        kutoka .connection agiza Client
        ukijumuisha self._lock:
            ikiwa self._address ni sio Tupu:
                c = Client(self._address,
                           authkey=process.current_process().authkey)
                c.send(Tupu)
                c.close()
                self._thread.join(timeout)
                ikiwa self._thread.is_alive():
                    util.sub_warning('_ResourceSharer thread did '
                                     'not stop when asked')
                self._listener.close()
                self._thread = Tupu
                self._address = Tupu
                self._listener = Tupu
                kila key, (send, close) kwenye self._cache.items():
                    close()
                self._cache.clear()

    eleza _afterfork(self):
        kila key, (send, close) kwenye self._cache.items():
            close()
        self._cache.clear()
        # If self._lock was locked at the time of the fork, it may be broken
        # -- see issue 6721.  Replace it without letting it be gc'ed.
        self._old_locks.append(self._lock)
        self._lock = threading.Lock()
        ikiwa self._listener ni sio Tupu:
            self._listener.close()
        self._listener = Tupu
        self._address = Tupu
        self._thread = Tupu

    eleza _start(self):
        kutoka .connection agiza Listener
        assert self._listener ni Tupu, "Already have Listener"
        util.debug('starting listener na thread kila sending handles')
        self._listener = Listener(authkey=process.current_process().authkey)
        self._address = self._listener.address
        t = threading.Thread(target=self._serve)
        t.daemon = Kweli
        t.start()
        self._thread = t

    eleza _serve(self):
        ikiwa hasattr(signal, 'pthread_sigmask'):
            signal.pthread_sigmask(signal.SIG_BLOCK, signal.valid_signals())
        wakati 1:
            jaribu:
                ukijumuisha self._listener.accept() kama conn:
                    msg = conn.recv()
                    ikiwa msg ni Tupu:
                        koma
                    key, destination_pid = msg
                    send, close = self._cache.pop(key)
                    jaribu:
                        send(conn, destination_pid)
                    mwishowe:
                        close()
            tatizo:
                ikiwa sio util.is_exiting():
                    sys.excepthook(*sys.exc_info())


_resource_sharer = _ResourceSharer()
stop = _resource_sharer.stop
