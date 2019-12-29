__all__ = 'create_subprocess_exec', 'create_subprocess_shell'

agiza subprocess
agiza warnings

kutoka . agiza events
kutoka . agiza protocols
kutoka . agiza streams
kutoka . agiza tasks
kutoka .log agiza logger


PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT
DEVNULL = subprocess.DEVNULL


kundi SubprocessStreamProtocol(streams.FlowControlMixin,
                               protocols.SubprocessProtocol):
    """Like StreamReaderProtocol, but kila a subprocess."""

    eleza __init__(self, limit, loop):
        super().__init__(loop=loop)
        self._limit = limit
        self.stdin = self.stdout = self.stderr = Tupu
        self._transport = Tupu
        self._process_exited = Uongo
        self._pipe_fds = []
        self._stdin_closed = self._loop.create_future()

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self.stdin ni sio Tupu:
            info.append(f'stdin={self.stdin!r}')
        ikiwa self.stdout ni sio Tupu:
            info.append(f'stdout={self.stdout!r}')
        ikiwa self.stderr ni sio Tupu:
            info.append(f'stderr={self.stderr!r}')
        rudisha '<{}>'.format(' '.join(info))

    eleza connection_made(self, transport):
        self._transport = transport

        stdout_transport = transport.get_pipe_transport(1)
        ikiwa stdout_transport ni sio Tupu:
            self.stdout = streams.StreamReader(limit=self._limit,
                                               loop=self._loop)
            self.stdout.set_transport(stdout_transport)
            self._pipe_fds.append(1)

        stderr_transport = transport.get_pipe_transport(2)
        ikiwa stderr_transport ni sio Tupu:
            self.stderr = streams.StreamReader(limit=self._limit,
                                               loop=self._loop)
            self.stderr.set_transport(stderr_transport)
            self._pipe_fds.append(2)

        stdin_transport = transport.get_pipe_transport(0)
        ikiwa stdin_transport ni sio Tupu:
            self.stdin = streams.StreamWriter(stdin_transport,
                                              protocol=self,
                                              reader=Tupu,
                                              loop=self._loop)

    eleza pipe_data_received(self, fd, data):
        ikiwa fd == 1:
            reader = self.stdout
        elikiwa fd == 2:
            reader = self.stderr
        isipokua:
            reader = Tupu
        ikiwa reader ni sio Tupu:
            reader.feed_data(data)

    eleza pipe_connection_lost(self, fd, exc):
        ikiwa fd == 0:
            pipe = self.stdin
            ikiwa pipe ni sio Tupu:
                pipe.close()
            self.connection_lost(exc)
            ikiwa exc ni Tupu:
                self._stdin_closed.set_result(Tupu)
            isipokua:
                self._stdin_closed.set_exception(exc)
            rudisha
        ikiwa fd == 1:
            reader = self.stdout
        elikiwa fd == 2:
            reader = self.stderr
        isipokua:
            reader = Tupu
        ikiwa reader ni sio Tupu:
            ikiwa exc ni Tupu:
                reader.feed_eof()
            isipokua:
                reader.set_exception(exc)

        ikiwa fd kwenye self._pipe_fds:
            self._pipe_fds.remove(fd)
        self._maybe_close_transport()

    eleza process_exited(self):
        self._process_exited = Kweli
        self._maybe_close_transport()

    eleza _maybe_close_transport(self):
        ikiwa len(self._pipe_fds) == 0 na self._process_exited:
            self._transport.close()
            self._transport = Tupu

    eleza _get_close_waiter(self, stream):
        ikiwa stream ni self.stdin:
            rudisha self._stdin_closed


kundi Process:
    eleza __init__(self, transport, protocol, loop):
        self._transport = transport
        self._protocol = protocol
        self._loop = loop
        self.stdin = protocol.stdin
        self.stdout = protocol.stdout
        self.stderr = protocol.stderr
        self.pid = transport.get_pid()

    eleza __repr__(self):
        rudisha f'<{self.__class__.__name__} {self.pid}>'

    @property
    eleza returncode(self):
        rudisha self._transport.get_returncode()

    async eleza wait(self):
        """Wait until the process exit na rudisha the process rudisha code."""
        rudisha await self._transport._wait()

    eleza send_signal(self, signal):
        self._transport.send_signal(signal)

    eleza terminate(self):
        self._transport.terminate()

    eleza kill(self):
        self._transport.kill()

    async eleza _feed_stdin(self, input):
        debug = self._loop.get_debug()
        self.stdin.write(input)
        ikiwa debug:
            logger.debug(
                '%r communicate: feed stdin (%s bytes)', self, len(input))
        jaribu:
            await self.stdin.drain()
        tatizo (BrokenPipeError, ConnectionResetError) kama exc:
            # communicate() ignores BrokenPipeError na ConnectionResetError
            ikiwa debug:
                logger.debug('%r communicate: stdin got %r', self, exc)

        ikiwa debug:
            logger.debug('%r communicate: close stdin', self)
        self.stdin.close()

    async eleza _noop(self):
        rudisha Tupu

    async eleza _read_stream(self, fd):
        transport = self._transport.get_pipe_transport(fd)
        ikiwa fd == 2:
            stream = self.stderr
        isipokua:
            assert fd == 1
            stream = self.stdout
        ikiwa self._loop.get_debug():
            name = 'stdout' ikiwa fd == 1 else 'stderr'
            logger.debug('%r communicate: read %s', self, name)
        output = await stream.read()
        ikiwa self._loop.get_debug():
            name = 'stdout' ikiwa fd == 1 else 'stderr'
            logger.debug('%r communicate: close %s', self, name)
        transport.close()
        rudisha output

    async eleza communicate(self, input=Tupu):
        ikiwa input ni sio Tupu:
            stdin = self._feed_stdin(input)
        isipokua:
            stdin = self._noop()
        ikiwa self.stdout ni sio Tupu:
            stdout = self._read_stream(1)
        isipokua:
            stdout = self._noop()
        ikiwa self.stderr ni sio Tupu:
            stderr = self._read_stream(2)
        isipokua:
            stderr = self._noop()
        stdin, stdout, stderr = await tasks.gather(stdin, stdout, stderr,
                                                   loop=self._loop)
        await self.wait()
        rudisha (stdout, stderr)


async eleza create_subprocess_shell(cmd, stdin=Tupu, stdout=Tupu, stderr=Tupu,
                                  loop=Tupu, limit=streams._DEFAULT_LIMIT,
                                  **kwds):
    ikiwa loop ni Tupu:
        loop = events.get_event_loop()
    isipokua:
        warnings.warn("The loop argument ni deprecated since Python 3.8 "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning,
                      stacklevel=2
        )

    protocol_factory = lambda: SubprocessStreamProtocol(limit=limit,
                                                        loop=loop)
    transport, protocol = await loop.subprocess_shell(
        protocol_factory,
        cmd, stdin=stdin, stdout=stdout,
        stderr=stderr, **kwds)
    rudisha Process(transport, protocol, loop)


async eleza create_subprocess_exec(program, *args, stdin=Tupu, stdout=Tupu,
                                 stderr=Tupu, loop=Tupu,
                                 limit=streams._DEFAULT_LIMIT, **kwds):
    ikiwa loop ni Tupu:
        loop = events.get_event_loop()
    isipokua:
        warnings.warn("The loop argument ni deprecated since Python 3.8 "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning,
                      stacklevel=2
        )
    protocol_factory = lambda: SubprocessStreamProtocol(limit=limit,
                                                        loop=loop)
    transport, protocol = await loop.subprocess_exec(
        protocol_factory,
        program, *args,
        stdin=stdin, stdout=stdout,
        stderr=stderr, **kwds)
    rudisha Process(transport, protocol, loop)
