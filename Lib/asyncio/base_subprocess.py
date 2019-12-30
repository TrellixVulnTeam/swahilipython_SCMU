agiza collections
agiza subprocess
agiza warnings

kutoka . agiza protocols
kutoka . agiza transports
kutoka .log agiza logger


kundi BaseSubprocessTransport(transports.SubprocessTransport):

    eleza __init__(self, loop, protocol, args, shell,
                 stdin, stdout, stderr, bufsize,
                 waiter=Tupu, extra=Tupu, **kwargs):
        super().__init__(extra)
        self._closed = Uongo
        self._protocol = protocol
        self._loop = loop
        self._proc = Tupu
        self._pid = Tupu
        self._returncode = Tupu
        self._exit_waiters = []
        self._pending_calls = collections.deque()
        self._pipes = {}
        self._finished = Uongo

        ikiwa stdin == subprocess.PIPE:
            self._pipes[0] = Tupu
        ikiwa stdout == subprocess.PIPE:
            self._pipes[1] = Tupu
        ikiwa stderr == subprocess.PIPE:
            self._pipes[2] = Tupu

        # Create the child process: set the _proc attribute
        jaribu:
            self._start(args=args, shell=shell, stdin=stdin, stdout=stdout,
                        stderr=stderr, bufsize=bufsize, **kwargs)
        tatizo:
            self.close()
            raise

        self._pid = self._proc.pid
        self._extra['subprocess'] = self._proc

        ikiwa self._loop.get_debug():
            ikiwa isinstance(args, (bytes, str)):
                program = args
            isipokua:
                program = args[0]
            logger.debug('process %r created: pid %s',
                         program, self._pid)

        self._loop.create_task(self._connect_pipes(waiter))

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self._closed:
            info.append('closed')
        ikiwa self._pid ni sio Tupu:
            info.append(f'pid={self._pid}')
        ikiwa self._returncode ni sio Tupu:
            info.append(f'returncode={self._returncode}')
        lasivyo self._pid ni sio Tupu:
            info.append('running')
        isipokua:
            info.append('not started')

        stdin = self._pipes.get(0)
        ikiwa stdin ni sio Tupu:
            info.append(f'stdin={stdin.pipe}')

        stdout = self._pipes.get(1)
        stderr = self._pipes.get(2)
        ikiwa stdout ni sio Tupu na stderr ni stdout:
            info.append(f'stdout=stderr={stdout.pipe}')
        isipokua:
            ikiwa stdout ni sio Tupu:
                info.append(f'stdout={stdout.pipe}')
            ikiwa stderr ni sio Tupu:
                info.append(f'stderr={stderr.pipe}')

        rudisha '<{}>'.format(' '.join(info))

    eleza _start(self, args, shell, stdin, stdout, stderr, bufsize, **kwargs):
        ashiria NotImplementedError

    eleza set_protocol(self, protocol):
        self._protocol = protocol

    eleza get_protocol(self):
        rudisha self._protocol

    eleza is_closing(self):
        rudisha self._closed

    eleza close(self):
        ikiwa self._closed:
            rudisha
        self._closed = Kweli

        kila proto kwenye self._pipes.values():
            ikiwa proto ni Tupu:
                endelea
            proto.pipe.close()

        ikiwa (self._proc ni sio Tupu na
                # has the child process finished?
                self._returncode ni Tupu na
                # the child process has finished, but the
                # transport hasn't been notified yet?
                self._proc.poll() ni Tupu):

            ikiwa self._loop.get_debug():
                logger.warning('Close running child process: kill %r', self)

            jaribu:
                self._proc.kill()
            tatizo ProcessLookupError:
                pita

            # Don't clear the _proc reference yet: _post_init() may still run

    eleza __del__(self, _warn=warnings.warn):
        ikiwa sio self._closed:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self.close()

    eleza get_pid(self):
        rudisha self._pid

    eleza get_returncode(self):
        rudisha self._returncode

    eleza get_pipe_transport(self, fd):
        ikiwa fd kwenye self._pipes:
            rudisha self._pipes[fd].pipe
        isipokua:
            rudisha Tupu

    eleza _check_proc(self):
        ikiwa self._proc ni Tupu:
            ashiria ProcessLookupError()

    eleza send_signal(self, signal):
        self._check_proc()
        self._proc.send_signal(signal)

    eleza terminate(self):
        self._check_proc()
        self._proc.terminate()

    eleza kill(self):
        self._check_proc()
        self._proc.kill()

    async eleza _connect_pipes(self, waiter):
        jaribu:
            proc = self._proc
            loop = self._loop

            ikiwa proc.stdin ni sio Tupu:
                _, pipe = await loop.connect_write_pipe(
                    lambda: WriteSubprocessPipeProto(self, 0),
                    proc.stdin)
                self._pipes[0] = pipe

            ikiwa proc.stdout ni sio Tupu:
                _, pipe = await loop.connect_read_pipe(
                    lambda: ReadSubprocessPipeProto(self, 1),
                    proc.stdout)
                self._pipes[1] = pipe

            ikiwa proc.stderr ni sio Tupu:
                _, pipe = await loop.connect_read_pipe(
                    lambda: ReadSubprocessPipeProto(self, 2),
                    proc.stderr)
                self._pipes[2] = pipe

            assert self._pending_calls ni sio Tupu

            loop.call_soon(self._protocol.connection_made, self)
            kila callback, data kwenye self._pending_calls:
                loop.call_soon(callback, *data)
            self._pending_calls = Tupu
        tatizo (SystemExit, KeyboardInterrupt):
            raise
        tatizo BaseException kama exc:
            ikiwa waiter ni sio Tupu na sio waiter.cancelled():
                waiter.set_exception(exc)
        isipokua:
            ikiwa waiter ni sio Tupu na sio waiter.cancelled():
                waiter.set_result(Tupu)

    eleza _call(self, cb, *data):
        ikiwa self._pending_calls ni sio Tupu:
            self._pending_calls.append((cb, data))
        isipokua:
            self._loop.call_soon(cb, *data)

    eleza _pipe_connection_lost(self, fd, exc):
        self._call(self._protocol.pipe_connection_lost, fd, exc)
        self._try_finish()

    eleza _pipe_data_received(self, fd, data):
        self._call(self._protocol.pipe_data_received, fd, data)

    eleza _process_exited(self, returncode):
        assert returncode ni sio Tupu, returncode
        assert self._returncode ni Tupu, self._returncode
        ikiwa self._loop.get_debug():
            logger.info('%r exited ukijumuisha rudisha code %r', self, returncode)
        self._returncode = returncode
        ikiwa self._proc.returncode ni Tupu:
            # asyncio uses a child watcher: copy the status into the Popen
            # object. On Python 3.6, it ni required to avoid a ResourceWarning.
            self._proc.returncode = returncode
        self._call(self._protocol.process_exited)
        self._try_finish()

        # wake up futures waiting kila wait()
        kila waiter kwenye self._exit_waiters:
            ikiwa sio waiter.cancelled():
                waiter.set_result(returncode)
        self._exit_waiters = Tupu

    async eleza _wait(self):
        """Wait until the process exit na rudisha the process rudisha code.

        This method ni a coroutine."""
        ikiwa self._returncode ni sio Tupu:
            rudisha self._returncode

        waiter = self._loop.create_future()
        self._exit_waiters.append(waiter)
        rudisha await waiter

    eleza _try_finish(self):
        assert sio self._finished
        ikiwa self._returncode ni Tupu:
            rudisha
        ikiwa all(p ni sio Tupu na p.disconnected
               kila p kwenye self._pipes.values()):
            self._finished = Kweli
            self._call(self._call_connection_lost, Tupu)

    eleza _call_connection_lost(self, exc):
        jaribu:
            self._protocol.connection_lost(exc)
        mwishowe:
            self._loop = Tupu
            self._proc = Tupu
            self._protocol = Tupu


kundi WriteSubprocessPipeProto(protocols.BaseProtocol):

    eleza __init__(self, proc, fd):
        self.proc = proc
        self.fd = fd
        self.pipe = Tupu
        self.disconnected = Uongo

    eleza connection_made(self, transport):
        self.pipe = transport

    eleza __repr__(self):
        rudisha f'<{self.__class__.__name__} fd={self.fd} pipe={self.pipe!r}>'

    eleza connection_lost(self, exc):
        self.disconnected = Kweli
        self.proc._pipe_connection_lost(self.fd, exc)
        self.proc = Tupu

    eleza pause_writing(self):
        self.proc._protocol.pause_writing()

    eleza resume_writing(self):
        self.proc._protocol.resume_writing()


kundi ReadSubprocessPipeProto(WriteSubprocessPipeProto,
                              protocols.Protocol):

    eleza data_received(self, data):
        self.proc._pipe_data_received(self.fd, data)
