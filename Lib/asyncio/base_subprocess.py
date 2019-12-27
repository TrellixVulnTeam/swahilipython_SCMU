agiza collections
agiza subprocess
agiza warnings

kutoka . agiza protocols
kutoka . agiza transports
kutoka .log agiza logger


kundi BaseSubprocessTransport(transports.SubprocessTransport):

    eleza __init__(self, loop, protocol, args, shell,
                 stdin, stdout, stderr, bufsize,
                 waiter=None, extra=None, **kwargs):
        super().__init__(extra)
        self._closed = False
        self._protocol = protocol
        self._loop = loop
        self._proc = None
        self._pid = None
        self._returncode = None
        self._exit_waiters = []
        self._pending_calls = collections.deque()
        self._pipes = {}
        self._finished = False

        ikiwa stdin == subprocess.PIPE:
            self._pipes[0] = None
        ikiwa stdout == subprocess.PIPE:
            self._pipes[1] = None
        ikiwa stderr == subprocess.PIPE:
            self._pipes[2] = None

        # Create the child process: set the _proc attribute
        try:
            self._start(args=args, shell=shell, stdin=stdin, stdout=stdout,
                        stderr=stderr, bufsize=bufsize, **kwargs)
        except:
            self.close()
            raise

        self._pid = self._proc.pid
        self._extra['subprocess'] = self._proc

        ikiwa self._loop.get_debug():
            ikiwa isinstance(args, (bytes, str)):
                program = args
            else:
                program = args[0]
            logger.debug('process %r created: pid %s',
                         program, self._pid)

        self._loop.create_task(self._connect_pipes(waiter))

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self._closed:
            info.append('closed')
        ikiwa self._pid is not None:
            info.append(f'pid={self._pid}')
        ikiwa self._returncode is not None:
            info.append(f'returncode={self._returncode}')
        elikiwa self._pid is not None:
            info.append('running')
        else:
            info.append('not started')

        stdin = self._pipes.get(0)
        ikiwa stdin is not None:
            info.append(f'stdin={stdin.pipe}')

        stdout = self._pipes.get(1)
        stderr = self._pipes.get(2)
        ikiwa stdout is not None and stderr is stdout:
            info.append(f'stdout=stderr={stdout.pipe}')
        else:
            ikiwa stdout is not None:
                info.append(f'stdout={stdout.pipe}')
            ikiwa stderr is not None:
                info.append(f'stderr={stderr.pipe}')

        rudisha '<{}>'.format(' '.join(info))

    eleza _start(self, args, shell, stdin, stdout, stderr, bufsize, **kwargs):
        raise NotImplementedError

    eleza set_protocol(self, protocol):
        self._protocol = protocol

    eleza get_protocol(self):
        rudisha self._protocol

    eleza is_closing(self):
        rudisha self._closed

    eleza close(self):
        ikiwa self._closed:
            return
        self._closed = True

        for proto in self._pipes.values():
            ikiwa proto is None:
                continue
            proto.pipe.close()

        ikiwa (self._proc is not None and
                # has the child process finished?
                self._returncode is None and
                # the child process has finished, but the
                # transport hasn't been notified yet?
                self._proc.poll() is None):

            ikiwa self._loop.get_debug():
                logger.warning('Close running child process: kill %r', self)

            try:
                self._proc.kill()
            except ProcessLookupError:
                pass

            # Don't clear the _proc reference yet: _post_init() may still run

    eleza __del__(self, _warn=warnings.warn):
        ikiwa not self._closed:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self.close()

    eleza get_pid(self):
        rudisha self._pid

    eleza get_returncode(self):
        rudisha self._returncode

    eleza get_pipe_transport(self, fd):
        ikiwa fd in self._pipes:
            rudisha self._pipes[fd].pipe
        else:
            rudisha None

    eleza _check_proc(self):
        ikiwa self._proc is None:
            raise ProcessLookupError()

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
        try:
            proc = self._proc
            loop = self._loop

            ikiwa proc.stdin is not None:
                _, pipe = await loop.connect_write_pipe(
                    lambda: WriteSubprocessPipeProto(self, 0),
                    proc.stdin)
                self._pipes[0] = pipe

            ikiwa proc.stdout is not None:
                _, pipe = await loop.connect_read_pipe(
                    lambda: ReadSubprocessPipeProto(self, 1),
                    proc.stdout)
                self._pipes[1] = pipe

            ikiwa proc.stderr is not None:
                _, pipe = await loop.connect_read_pipe(
                    lambda: ReadSubprocessPipeProto(self, 2),
                    proc.stderr)
                self._pipes[2] = pipe

            assert self._pending_calls is not None

            loop.call_soon(self._protocol.connection_made, self)
            for callback, data in self._pending_calls:
                loop.call_soon(callback, *data)
            self._pending_calls = None
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            ikiwa waiter is not None and not waiter.cancelled():
                waiter.set_exception(exc)
        else:
            ikiwa waiter is not None and not waiter.cancelled():
                waiter.set_result(None)

    eleza _call(self, cb, *data):
        ikiwa self._pending_calls is not None:
            self._pending_calls.append((cb, data))
        else:
            self._loop.call_soon(cb, *data)

    eleza _pipe_connection_lost(self, fd, exc):
        self._call(self._protocol.pipe_connection_lost, fd, exc)
        self._try_finish()

    eleza _pipe_data_received(self, fd, data):
        self._call(self._protocol.pipe_data_received, fd, data)

    eleza _process_exited(self, returncode):
        assert returncode is not None, returncode
        assert self._returncode is None, self._returncode
        ikiwa self._loop.get_debug():
            logger.info('%r exited with rudisha code %r', self, returncode)
        self._returncode = returncode
        ikiwa self._proc.returncode is None:
            # asyncio uses a child watcher: copy the status into the Popen
            # object. On Python 3.6, it is required to avoid a ResourceWarning.
            self._proc.returncode = returncode
        self._call(self._protocol.process_exited)
        self._try_finish()

        # wake up futures waiting for wait()
        for waiter in self._exit_waiters:
            ikiwa not waiter.cancelled():
                waiter.set_result(returncode)
        self._exit_waiters = None

    async eleza _wait(self):
        """Wait until the process exit and rudisha the process rudisha code.

        This method is a coroutine."""
        ikiwa self._returncode is not None:
            rudisha self._returncode

        waiter = self._loop.create_future()
        self._exit_waiters.append(waiter)
        rudisha await waiter

    eleza _try_finish(self):
        assert not self._finished
        ikiwa self._returncode is None:
            return
        ikiwa all(p is not None and p.disconnected
               for p in self._pipes.values()):
            self._finished = True
            self._call(self._call_connection_lost, None)

    eleza _call_connection_lost(self, exc):
        try:
            self._protocol.connection_lost(exc)
        finally:
            self._loop = None
            self._proc = None
            self._protocol = None


kundi WriteSubprocessPipeProto(protocols.BaseProtocol):

    eleza __init__(self, proc, fd):
        self.proc = proc
        self.fd = fd
        self.pipe = None
        self.disconnected = False

    eleza connection_made(self, transport):
        self.pipe = transport

    eleza __repr__(self):
        rudisha f'<{self.__class__.__name__} fd={self.fd} pipe={self.pipe!r}>'

    eleza connection_lost(self, exc):
        self.disconnected = True
        self.proc._pipe_connection_lost(self.fd, exc)
        self.proc = None

    eleza pause_writing(self):
        self.proc._protocol.pause_writing()

    eleza resume_writing(self):
        self.proc._protocol.resume_writing()


kundi ReadSubprocessPipeProto(WriteSubprocessPipeProto,
                              protocols.Protocol):

    eleza data_received(self, data):
        self.proc._pipe_data_received(self.fd, data)
