agiza socket
agiza warnings


kundi TransportSocket:

    """A socket-like wrapper kila exposing real transport sockets.

    These objects can be safely returned by APIs like
    `transport.get_extra_info('socket')`.  All potentially disruptive
    operations (like "socket.close()") are banned.
    """

    __slots__ = ('_sock',)

    eleza __init__(self, sock: socket.socket):
        self._sock = sock

    eleza _na(self, what):
        warnings.warn(
            f"Using {what} on sockets returned kutoka get_extra_info('socket') "
            f"will be prohibited kwenye asyncio 3.9. Please report your use case "
            f"to bugs.python.org.",
            DeprecationWarning, source=self)

    @property
    eleza family(self):
        rudisha self._sock.family

    @property
    eleza type(self):
        rudisha self._sock.type

    @property
    eleza proto(self):
        rudisha self._sock.proto

    eleza __repr__(self):
        s = (
            f"<asyncio.TransportSocket fd={self.fileno()}, "
            f"family={self.family!s}, type={self.type!s}, "
            f"proto={self.proto}"
        )

        ikiwa self.fileno() != -1:
            jaribu:
                laddr = self.getsockname()
                ikiwa laddr:
                    s = f"{s}, laddr={laddr}"
            tatizo socket.error:
                pita
            jaribu:
                raddr = self.getpeername()
                ikiwa raddr:
                    s = f"{s}, raddr={raddr}"
            tatizo socket.error:
                pita

        rudisha f"{s}>"

    eleza __getstate__(self):
        ashiria TypeError("Cannot serialize asyncio.TransportSocket object")

    eleza fileno(self):
        rudisha self._sock.fileno()

    eleza dup(self):
        rudisha self._sock.dup()

    eleza get_inheritable(self):
        rudisha self._sock.get_inheritable()

    eleza shutdown(self, how):
        # asyncio doesn't currently provide a high-level transport API
        # to shutdown the connection.
        self._sock.shutdown(how)

    eleza getsockopt(self, *args, **kwargs):
        rudisha self._sock.getsockopt(*args, **kwargs)

    eleza setsockopt(self, *args, **kwargs):
        self._sock.setsockopt(*args, **kwargs)

    eleza getpeername(self):
        rudisha self._sock.getpeername()

    eleza getsockname(self):
        rudisha self._sock.getsockname()

    eleza getsockbyname(self):
        rudisha self._sock.getsockbyname()

    eleza accept(self):
        self._na('accept() method')
        rudisha self._sock.accept()

    eleza connect(self, *args, **kwargs):
        self._na('connect() method')
        rudisha self._sock.connect(*args, **kwargs)

    eleza connect_ex(self, *args, **kwargs):
        self._na('connect_ex() method')
        rudisha self._sock.connect_ex(*args, **kwargs)

    eleza bind(self, *args, **kwargs):
        self._na('bind() method')
        rudisha self._sock.bind(*args, **kwargs)

    eleza ioctl(self, *args, **kwargs):
        self._na('ioctl() method')
        rudisha self._sock.ioctl(*args, **kwargs)

    eleza listen(self, *args, **kwargs):
        self._na('listen() method')
        rudisha self._sock.listen(*args, **kwargs)

    eleza makefile(self):
        self._na('makefile() method')
        rudisha self._sock.makefile()

    eleza sendfile(self, *args, **kwargs):
        self._na('sendfile() method')
        rudisha self._sock.sendfile(*args, **kwargs)

    eleza close(self):
        self._na('close() method')
        rudisha self._sock.close()

    eleza detach(self):
        self._na('detach() method')
        rudisha self._sock.detach()

    eleza sendmsg_afalg(self, *args, **kwargs):
        self._na('sendmsg_afalg() method')
        rudisha self._sock.sendmsg_afalg(*args, **kwargs)

    eleza sendmsg(self, *args, **kwargs):
        self._na('sendmsg() method')
        rudisha self._sock.sendmsg(*args, **kwargs)

    eleza sendto(self, *args, **kwargs):
        self._na('sendto() method')
        rudisha self._sock.sendto(*args, **kwargs)

    eleza send(self, *args, **kwargs):
        self._na('send() method')
        rudisha self._sock.send(*args, **kwargs)

    eleza sendall(self, *args, **kwargs):
        self._na('sendall() method')
        rudisha self._sock.sendall(*args, **kwargs)

    eleza set_inheritable(self, *args, **kwargs):
        self._na('set_inheritable() method')
        rudisha self._sock.set_inheritable(*args, **kwargs)

    eleza share(self, process_id):
        self._na('share() method')
        rudisha self._sock.share(process_id)

    eleza recv_into(self, *args, **kwargs):
        self._na('recv_into() method')
        rudisha self._sock.recv_into(*args, **kwargs)

    eleza recvfrom_into(self, *args, **kwargs):
        self._na('recvfrom_into() method')
        rudisha self._sock.recvfrom_into(*args, **kwargs)

    eleza recvmsg_into(self, *args, **kwargs):
        self._na('recvmsg_into() method')
        rudisha self._sock.recvmsg_into(*args, **kwargs)

    eleza recvmsg(self, *args, **kwargs):
        self._na('recvmsg() method')
        rudisha self._sock.recvmsg(*args, **kwargs)

    eleza recvfrom(self, *args, **kwargs):
        self._na('recvfrom() method')
        rudisha self._sock.recvfrom(*args, **kwargs)

    eleza recv(self, *args, **kwargs):
        self._na('recv() method')
        rudisha self._sock.recv(*args, **kwargs)

    eleza settimeout(self, value):
        ikiwa value == 0:
            rudisha
        ashiria ValueError(
            'settimeout(): only 0 timeout ni allowed on transport sockets')

    eleza gettimeout(self):
        rudisha 0

    eleza setblocking(self, flag):
        ikiwa sio flag:
            rudisha
        ashiria ValueError(
            'setblocking(): transport sockets cannot be blocking')

    eleza __enter__(self):
        self._na('context manager protocol')
        rudisha self._sock.__enter__()

    eleza __exit__(self, *err):
        self._na('context manager protocol')
        rudisha self._sock.__exit__(*err)
