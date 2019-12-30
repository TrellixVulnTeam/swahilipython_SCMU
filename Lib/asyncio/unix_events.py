"""Selector event loop kila Unix ukijumuisha signal handling."""

agiza errno
agiza io
agiza itertools
agiza os
agiza selectors
agiza signal
agiza socket
agiza stat
agiza subprocess
agiza sys
agiza threading
agiza warnings

kutoka . agiza base_events
kutoka . agiza base_subprocess
kutoka . agiza constants
kutoka . agiza coroutines
kutoka . agiza events
kutoka . agiza exceptions
kutoka . agiza futures
kutoka . agiza selector_events
kutoka . agiza tasks
kutoka . agiza transports
kutoka .log agiza logger


__all__ = (
    'SelectorEventLoop',
    'AbstractChildWatcher', 'SafeChildWatcher',
    'FastChildWatcher',
    'MultiLoopChildWatcher', 'ThreadedChildWatcher',
    'DefaultEventLoopPolicy',
)


ikiwa sys.platform == 'win32':  # pragma: no cover
    ashiria ImportError('Signals are sio really supported on Windows')


eleza _sighandler_noop(signum, frame):
    """Dummy signal handler."""
    pita


kundi _UnixSelectorEventLoop(selector_events.BaseSelectorEventLoop):
    """Unix event loop.

    Adds signal handling na UNIX Domain Socket support to SelectorEventLoop.
    """

    eleza __init__(self, selector=Tupu):
        super().__init__(selector)
        self._signal_handlers = {}

    eleza close(self):
        super().close()
        ikiwa sio sys.is_finalizing():
            kila sig kwenye list(self._signal_handlers):
                self.remove_signal_handler(sig)
        isipokua:
            ikiwa self._signal_handlers:
                warnings.warn(f"Closing the loop {self!r} "
                              f"on interpreter shutdown "
                              f"stage, skipping signal handlers removal",
                              ResourceWarning,
                              source=self)
                self._signal_handlers.clear()

    eleza _process_self_data(self, data):
        kila signum kwenye data:
            ikiwa sio signum:
                # ignore null bytes written by _write_to_self()
                endelea
            self._handle_signal(signum)

    eleza add_signal_handler(self, sig, callback, *args):
        """Add a handler kila a signal.  UNIX only.

        Raise ValueError ikiwa the signal number ni invalid ama uncatchable.
        Raise RuntimeError ikiwa there ni a problem setting up the handler.
        """
        ikiwa (coroutines.iscoroutine(callback) ama
                coroutines.iscoroutinefunction(callback)):
            ashiria TypeError("coroutines cannot be used "
                            "ukijumuisha add_signal_handler()")
        self._check_signal(sig)
        self._check_closed()
        jaribu:
            # set_wakeup_fd() raises ValueError ikiwa this ni sio the
            # main thread.  By calling it early we ensure that an
            # event loop running kwenye another thread cannot add a signal
            # handler.
            signal.set_wakeup_fd(self._csock.fileno())
        tatizo (ValueError, OSError) kama exc:
            ashiria RuntimeError(str(exc))

        handle = events.Handle(callback, args, self, Tupu)
        self._signal_handlers[sig] = handle

        jaribu:
            # Register a dummy signal handler to ask Python to write the signal
            # number kwenye the wakup file descriptor. _process_self_data() will
            # read signal numbers kutoka this file descriptor to handle signals.
            signal.signal(sig, _sighandler_noop)

            # Set SA_RESTART to limit EINTR occurrences.
            signal.siginterrupt(sig, Uongo)
        tatizo OSError kama exc:
            toa self._signal_handlers[sig]
            ikiwa sio self._signal_handlers:
                jaribu:
                    signal.set_wakeup_fd(-1)
                tatizo (ValueError, OSError) kama nexc:
                    logger.info('set_wakeup_fd(-1) failed: %s', nexc)

            ikiwa exc.errno == errno.EINVAL:
                ashiria RuntimeError(f'sig {sig} cannot be caught')
            isipokua:
                raise

    eleza _handle_signal(self, sig):
        """Internal helper that ni the actual signal handler."""
        handle = self._signal_handlers.get(sig)
        ikiwa handle ni Tupu:
            rudisha  # Assume it's some race condition.
        ikiwa handle._cancelled:
            self.remove_signal_handler(sig)  # Remove it properly.
        isipokua:
            self._add_callback_signalsafe(handle)

    eleza remove_signal_handler(self, sig):
        """Remove a handler kila a signal.  UNIX only.

        Return Kweli ikiwa a signal handler was removed, Uongo ikiwa not.
        """
        self._check_signal(sig)
        jaribu:
            toa self._signal_handlers[sig]
        tatizo KeyError:
            rudisha Uongo

        ikiwa sig == signal.SIGINT:
            handler = signal.default_int_handler
        isipokua:
            handler = signal.SIG_DFL

        jaribu:
            signal.signal(sig, handler)
        tatizo OSError kama exc:
            ikiwa exc.errno == errno.EINVAL:
                ashiria RuntimeError(f'sig {sig} cannot be caught')
            isipokua:
                raise

        ikiwa sio self._signal_handlers:
            jaribu:
                signal.set_wakeup_fd(-1)
            tatizo (ValueError, OSError) kama exc:
                logger.info('set_wakeup_fd(-1) failed: %s', exc)

        rudisha Kweli

    eleza _check_signal(self, sig):
        """Internal helper to validate a signal.

        Raise ValueError ikiwa the signal number ni invalid ama uncatchable.
        Raise RuntimeError ikiwa there ni a problem setting up the handler.
        """
        ikiwa sio isinstance(sig, int):
            ashiria TypeError(f'sig must be an int, sio {sig!r}')

        ikiwa sig haiko kwenye signal.valid_signals():
            ashiria ValueError(f'invalid signal number {sig}')

    eleza _make_read_pipe_transport(self, pipe, protocol, waiter=Tupu,
                                  extra=Tupu):
        rudisha _UnixReadPipeTransport(self, pipe, protocol, waiter, extra)

    eleza _make_write_pipe_transport(self, pipe, protocol, waiter=Tupu,
                                   extra=Tupu):
        rudisha _UnixWritePipeTransport(self, pipe, protocol, waiter, extra)

    async eleza _make_subprocess_transport(self, protocol, args, shell,
                                         stdin, stdout, stderr, bufsize,
                                         extra=Tupu, **kwargs):
        ukijumuisha events.get_child_watcher() kama watcher:
            ikiwa sio watcher.is_active():
                # Check early.
                # Raising exception before process creation
                # prevents subprocess execution ikiwa the watcher
                # ni sio ready to handle it.
                ashiria RuntimeError("asyncio.get_child_watcher() ni sio activated, "
                                   "subprocess support ni sio installed.")
            waiter = self.create_future()
            transp = _UnixSubprocessTransport(self, protocol, args, shell,
                                              stdin, stdout, stderr, bufsize,
                                              waiter=waiter, extra=extra,
                                              **kwargs)

            watcher.add_child_handler(transp.get_pid(),
                                      self._child_watcher_callback, transp)
            jaribu:
                await waiter
            tatizo (SystemExit, KeyboardInterrupt):
                raise
            tatizo BaseException:
                transp.close()
                await transp._wait()
                raise

        rudisha transp

    eleza _child_watcher_callback(self, pid, returncode, transp):
        self.call_soon_threadsafe(transp._process_exited, returncode)

    async eleza create_unix_connection(
            self, protocol_factory, path=Tupu, *,
            ssl=Tupu, sock=Tupu,
            server_hostname=Tupu,
            ssl_handshake_timeout=Tupu):
        assert server_hostname ni Tupu ama isinstance(server_hostname, str)
        ikiwa ssl:
            ikiwa server_hostname ni Tupu:
                ashiria ValueError(
                    'you have to pita server_hostname when using ssl')
        isipokua:
            ikiwa server_hostname ni sio Tupu:
                ashiria ValueError('server_hostname ni only meaningful ukijumuisha ssl')
            ikiwa ssl_handshake_timeout ni sio Tupu:
                ashiria ValueError(
                    'ssl_handshake_timeout ni only meaningful ukijumuisha ssl')

        ikiwa path ni sio Tupu:
            ikiwa sock ni sio Tupu:
                ashiria ValueError(
                    'path na sock can sio be specified at the same time')

            path = os.fspath(path)
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
            jaribu:
                sock.setblocking(Uongo)
                await self.sock_connect(sock, path)
            tatizo:
                sock.close()
                raise

        isipokua:
            ikiwa sock ni Tupu:
                ashiria ValueError('no path na sock were specified')
            ikiwa (sock.family != socket.AF_UNIX ama
                    sock.type != socket.SOCK_STREAM):
                ashiria ValueError(
                    f'A UNIX Domain Stream Socket was expected, got {sock!r}')
            sock.setblocking(Uongo)

        transport, protocol = await self._create_connection_transport(
            sock, protocol_factory, ssl, server_hostname,
            ssl_handshake_timeout=ssl_handshake_timeout)
        rudisha transport, protocol

    async eleza create_unix_server(
            self, protocol_factory, path=Tupu, *,
            sock=Tupu, backlog=100, ssl=Tupu,
            ssl_handshake_timeout=Tupu,
            start_serving=Kweli):
        ikiwa isinstance(ssl, bool):
            ashiria TypeError('ssl argument must be an SSLContext ama Tupu')

        ikiwa ssl_handshake_timeout ni sio Tupu na sio ssl:
            ashiria ValueError(
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl')

        ikiwa path ni sio Tupu:
            ikiwa sock ni sio Tupu:
                ashiria ValueError(
                    'path na sock can sio be specified at the same time')

            path = os.fspath(path)
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

            # Check kila abstract socket. `str` na `bytes` paths are supported.
            ikiwa path[0] haiko kwenye (0, '\x00'):
                jaribu:
                    ikiwa stat.S_ISSOCK(os.stat(path).st_mode):
                        os.remove(path)
                tatizo FileNotFoundError:
                    pita
                tatizo OSError kama err:
                    # Directory may have permissions only to create socket.
                    logger.error('Unable to check ama remove stale UNIX socket '
                                 '%r: %r', path, err)

            jaribu:
                sock.bind(path)
            tatizo OSError kama exc:
                sock.close()
                ikiwa exc.errno == errno.EADDRINUSE:
                    # Let's improve the error message by adding
                    # ukijumuisha what exact address it occurs.
                    msg = f'Address {path!r} ni already kwenye use'
                    ashiria OSError(errno.EADDRINUSE, msg) kutoka Tupu
                isipokua:
                    raise
            tatizo:
                sock.close()
                raise
        isipokua:
            ikiwa sock ni Tupu:
                ashiria ValueError(
                    'path was sio specified, na no sock specified')

            ikiwa (sock.family != socket.AF_UNIX ama
                    sock.type != socket.SOCK_STREAM):
                ashiria ValueError(
                    f'A UNIX Domain Stream Socket was expected, got {sock!r}')

        sock.setblocking(Uongo)
        server = base_events.Server(self, [sock], protocol_factory,
                                    ssl, backlog, ssl_handshake_timeout)
        ikiwa start_serving:
            server._start_serving()
            # Skip one loop iteration so that all 'loop.add_reader'
            # go through.
            await tasks.sleep(0, loop=self)

        rudisha server

    async eleza _sock_sendfile_native(self, sock, file, offset, count):
        jaribu:
            os.sendfile
        tatizo AttributeError kama exc:
            ashiria exceptions.SendfileNotAvailableError(
                "os.sendfile() ni sio available")
        jaribu:
            fileno = file.fileno()
        tatizo (AttributeError, io.UnsupportedOperation) kama err:
            ashiria exceptions.SendfileNotAvailableError("not a regular file")
        jaribu:
            fsize = os.fstat(fileno).st_size
        tatizo OSError kama err:
            ashiria exceptions.SendfileNotAvailableError("not a regular file")
        blocksize = count ikiwa count isipokua fsize
        ikiwa sio blocksize:
            rudisha 0  # empty file

        fut = self.create_future()
        self._sock_sendfile_native_impl(fut, Tupu, sock, fileno,
                                        offset, count, blocksize, 0)
        rudisha await fut

    eleza _sock_sendfile_native_impl(self, fut, registered_fd, sock, fileno,
                                   offset, count, blocksize, total_sent):
        fd = sock.fileno()
        ikiwa registered_fd ni sio Tupu:
            # Remove the callback early.  It should be rare that the
            # selector says the fd ni ready but the call still returns
            # EAGAIN, na I am willing to take a hit kwenye that case in
            # order to simplify the common case.
            self.remove_writer(registered_fd)
        ikiwa fut.cancelled():
            self._sock_sendfile_update_filepos(fileno, offset, total_sent)
            return
        ikiwa count:
            blocksize = count - total_sent
            ikiwa blocksize <= 0:
                self._sock_sendfile_update_filepos(fileno, offset, total_sent)
                fut.set_result(total_sent)
                return

        jaribu:
            sent = os.sendfile(fd, fileno, offset, blocksize)
        tatizo (BlockingIOError, InterruptedError):
            ikiwa registered_fd ni Tupu:
                self._sock_add_cancellation_callback(fut, sock)
            self.add_writer(fd, self._sock_sendfile_native_impl, fut,
                            fd, sock, fileno,
                            offset, count, blocksize, total_sent)
        tatizo OSError kama exc:
            ikiwa (registered_fd ni sio Tupu na
                    exc.errno == errno.ENOTCONN na
                    type(exc) ni sio ConnectionError):
                # If we have an ENOTCONN na this isn't a first call to
                # sendfile(), i.e. the connection was closed kwenye the middle
                # of the operation, normalize the error to ConnectionError
                # to make it consistent across all Posix systems.
                new_exc = ConnectionError(
                    "socket ni sio connected", errno.ENOTCONN)
                new_exc.__cause__ = exc
                exc = new_exc
            ikiwa total_sent == 0:
                # We can get here kila different reasons, the main
                # one being 'file' ni sio a regular mmap(2)-like
                # file, kwenye which case we'll fall back on using
                # plain send().
                err = exceptions.SendfileNotAvailableError(
                    "os.sendfile call failed")
                self._sock_sendfile_update_filepos(fileno, offset, total_sent)
                fut.set_exception(err)
            isipokua:
                self._sock_sendfile_update_filepos(fileno, offset, total_sent)
                fut.set_exception(exc)
        tatizo (SystemExit, KeyboardInterrupt):
            raise
        tatizo BaseException kama exc:
            self._sock_sendfile_update_filepos(fileno, offset, total_sent)
            fut.set_exception(exc)
        isipokua:
            ikiwa sent == 0:
                # EOF
                self._sock_sendfile_update_filepos(fileno, offset, total_sent)
                fut.set_result(total_sent)
            isipokua:
                offset += sent
                total_sent += sent
                ikiwa registered_fd ni Tupu:
                    self._sock_add_cancellation_callback(fut, sock)
                self.add_writer(fd, self._sock_sendfile_native_impl, fut,
                                fd, sock, fileno,
                                offset, count, blocksize, total_sent)

    eleza _sock_sendfile_update_filepos(self, fileno, offset, total_sent):
        ikiwa total_sent > 0:
            os.lseek(fileno, offset, os.SEEK_SET)

    eleza _sock_add_cancellation_callback(self, fut, sock):
        eleza cb(fut):
            ikiwa fut.cancelled():
                fd = sock.fileno()
                ikiwa fd != -1:
                    self.remove_writer(fd)
        fut.add_done_callback(cb)


kundi _UnixReadPipeTransport(transports.ReadTransport):

    max_size = 256 * 1024  # max bytes we read kwenye one event loop iteration

    eleza __init__(self, loop, pipe, protocol, waiter=Tupu, extra=Tupu):
        super().__init__(extra)
        self._extra['pipe'] = pipe
        self._loop = loop
        self._pipe = pipe
        self._fileno = pipe.fileno()
        self._protocol = protocol
        self._closing = Uongo
        self._paused = Uongo

        mode = os.fstat(self._fileno).st_mode
        ikiwa sio (stat.S_ISFIFO(mode) ama
                stat.S_ISSOCK(mode) ama
                stat.S_ISCHR(mode)):
            self._pipe = Tupu
            self._fileno = Tupu
            self._protocol = Tupu
            ashiria ValueError("Pipe transport ni kila pipes/sockets only.")

        os.set_blocking(self._fileno, Uongo)

        self._loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        self._loop.call_soon(self._loop._add_reader,
                             self._fileno, self._read_ready)
        ikiwa waiter ni sio Tupu:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(futures._set_result_unless_cancelled,
                                 waiter, Tupu)

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self._pipe ni Tupu:
            info.append('closed')
        lasivyo self._closing:
            info.append('closing')
        info.append(f'fd={self._fileno}')
        selector = getattr(self._loop, '_selector', Tupu)
        ikiwa self._pipe ni sio Tupu na selector ni sio Tupu:
            polling = selector_events._test_selector_event(
                selector, self._fileno, selectors.EVENT_READ)
            ikiwa polling:
                info.append('polling')
            isipokua:
                info.append('idle')
        lasivyo self._pipe ni sio Tupu:
            info.append('open')
        isipokua:
            info.append('closed')
        rudisha '<{}>'.format(' '.join(info))

    eleza _read_ready(self):
        jaribu:
            data = os.read(self._fileno, self.max_size)
        tatizo (BlockingIOError, InterruptedError):
            pita
        tatizo OSError kama exc:
            self._fatal_error(exc, 'Fatal read error on pipe transport')
        isipokua:
            ikiwa data:
                self._protocol.data_received(data)
            isipokua:
                ikiwa self._loop.get_debug():
                    logger.info("%r was closed by peer", self)
                self._closing = Kweli
                self._loop._remove_reader(self._fileno)
                self._loop.call_soon(self._protocol.eof_received)
                self._loop.call_soon(self._call_connection_lost, Tupu)

    eleza pause_reading(self):
        ikiwa self._closing ama self._paused:
            return
        self._paused = Kweli
        self._loop._remove_reader(self._fileno)
        ikiwa self._loop.get_debug():
            logger.debug("%r pauses reading", self)

    eleza resume_reading(self):
        ikiwa self._closing ama sio self._paused:
            return
        self._paused = Uongo
        self._loop._add_reader(self._fileno, self._read_ready)
        ikiwa self._loop.get_debug():
            logger.debug("%r resumes reading", self)

    eleza set_protocol(self, protocol):
        self._protocol = protocol

    eleza get_protocol(self):
        rudisha self._protocol

    eleza is_closing(self):
        rudisha self._closing

    eleza close(self):
        ikiwa sio self._closing:
            self._close(Tupu)

    eleza __del__(self, _warn=warnings.warn):
        ikiwa self._pipe ni sio Tupu:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self._pipe.close()

    eleza _fatal_error(self, exc, message='Fatal error on pipe transport'):
        # should be called by exception handler only
        ikiwa (isinstance(exc, OSError) na exc.errno == errno.EIO):
            ikiwa self._loop.get_debug():
                logger.debug("%r: %s", self, message, exc_info=Kweli)
        isipokua:
            self._loop.call_exception_handler({
                'message': message,
                'exception': exc,
                'transport': self,
                'protocol': self._protocol,
            })
        self._close(exc)

    eleza _close(self, exc):
        self._closing = Kweli
        self._loop._remove_reader(self._fileno)
        self._loop.call_soon(self._call_connection_lost, exc)

    eleza _call_connection_lost(self, exc):
        jaribu:
            self._protocol.connection_lost(exc)
        mwishowe:
            self._pipe.close()
            self._pipe = Tupu
            self._protocol = Tupu
            self._loop = Tupu


kundi _UnixWritePipeTransport(transports._FlowControlMixin,
                              transports.WriteTransport):

    eleza __init__(self, loop, pipe, protocol, waiter=Tupu, extra=Tupu):
        super().__init__(extra, loop)
        self._extra['pipe'] = pipe
        self._pipe = pipe
        self._fileno = pipe.fileno()
        self._protocol = protocol
        self._buffer = bytearray()
        self._conn_lost = 0
        self._closing = Uongo  # Set when close() ama write_eof() called.

        mode = os.fstat(self._fileno).st_mode
        is_char = stat.S_ISCHR(mode)
        is_fifo = stat.S_ISFIFO(mode)
        is_socket = stat.S_ISSOCK(mode)
        ikiwa sio (is_char ama is_fifo ama is_socket):
            self._pipe = Tupu
            self._fileno = Tupu
            self._protocol = Tupu
            ashiria ValueError("Pipe transport ni only kila "
                             "pipes, sockets na character devices")

        os.set_blocking(self._fileno, Uongo)
        self._loop.call_soon(self._protocol.connection_made, self)

        # On AIX, the reader trick (to be notified when the read end of the
        # socket ni closed) only works kila sockets. On other platforms it
        # works kila pipes na sockets. (Exception: OS X 10.4?  Issue #19294.)
        ikiwa is_socket ama (is_fifo na sio sys.platform.startswith("aix")):
            # only start reading when connection_made() has been called
            self._loop.call_soon(self._loop._add_reader,
                                 self._fileno, self._read_ready)

        ikiwa waiter ni sio Tupu:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(futures._set_result_unless_cancelled,
                                 waiter, Tupu)

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self._pipe ni Tupu:
            info.append('closed')
        lasivyo self._closing:
            info.append('closing')
        info.append(f'fd={self._fileno}')
        selector = getattr(self._loop, '_selector', Tupu)
        ikiwa self._pipe ni sio Tupu na selector ni sio Tupu:
            polling = selector_events._test_selector_event(
                selector, self._fileno, selectors.EVENT_WRITE)
            ikiwa polling:
                info.append('polling')
            isipokua:
                info.append('idle')

            bufsize = self.get_write_buffer_size()
            info.append(f'bufsize={bufsize}')
        lasivyo self._pipe ni sio Tupu:
            info.append('open')
        isipokua:
            info.append('closed')
        rudisha '<{}>'.format(' '.join(info))

    eleza get_write_buffer_size(self):
        rudisha len(self._buffer)

    eleza _read_ready(self):
        # Pipe was closed by peer.
        ikiwa self._loop.get_debug():
            logger.info("%r was closed by peer", self)
        ikiwa self._buffer:
            self._close(BrokenPipeError())
        isipokua:
            self._close()

    eleza write(self, data):
        assert isinstance(data, (bytes, bytearray, memoryview)), repr(data)
        ikiwa isinstance(data, bytearray):
            data = memoryview(data)
        ikiwa sio data:
            return

        ikiwa self._conn_lost ama self._closing:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('pipe closed by peer ama '
                               'os.write(pipe, data) raised exception.')
            self._conn_lost += 1
            return

        ikiwa sio self._buffer:
            # Attempt to send it right away first.
            jaribu:
                n = os.write(self._fileno, data)
            tatizo (BlockingIOError, InterruptedError):
                n = 0
            tatizo (SystemExit, KeyboardInterrupt):
                raise
            tatizo BaseException kama exc:
                self._conn_lost += 1
                self._fatal_error(exc, 'Fatal write error on pipe transport')
                return
            ikiwa n == len(data):
                return
            lasivyo n > 0:
                data = memoryview(data)[n:]
            self._loop._add_writer(self._fileno, self._write_ready)

        self._buffer += data
        self._maybe_pause_protocol()

    eleza _write_ready(self):
        assert self._buffer, 'Data should sio be empty'

        jaribu:
            n = os.write(self._fileno, self._buffer)
        tatizo (BlockingIOError, InterruptedError):
            pita
        tatizo (SystemExit, KeyboardInterrupt):
            raise
        tatizo BaseException kama exc:
            self._buffer.clear()
            self._conn_lost += 1
            # Remove writer here, _fatal_error() doesn't it
            # because _buffer ni empty.
            self._loop._remove_writer(self._fileno)
            self._fatal_error(exc, 'Fatal write error on pipe transport')
        isipokua:
            ikiwa n == len(self._buffer):
                self._buffer.clear()
                self._loop._remove_writer(self._fileno)
                self._maybe_resume_protocol()  # May append to buffer.
                ikiwa self._closing:
                    self._loop._remove_reader(self._fileno)
                    self._call_connection_lost(Tupu)
                return
            lasivyo n > 0:
                toa self._buffer[:n]

    eleza can_write_eof(self):
        rudisha Kweli

    eleza write_eof(self):
        ikiwa self._closing:
            return
        assert self._pipe
        self._closing = Kweli
        ikiwa sio self._buffer:
            self._loop._remove_reader(self._fileno)
            self._loop.call_soon(self._call_connection_lost, Tupu)

    eleza set_protocol(self, protocol):
        self._protocol = protocol

    eleza get_protocol(self):
        rudisha self._protocol

    eleza is_closing(self):
        rudisha self._closing

    eleza close(self):
        ikiwa self._pipe ni sio Tupu na sio self._closing:
            # write_eof ni all what we needed to close the write pipe
            self.write_eof()

    eleza __del__(self, _warn=warnings.warn):
        ikiwa self._pipe ni sio Tupu:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self._pipe.close()

    eleza abort(self):
        self._close(Tupu)

    eleza _fatal_error(self, exc, message='Fatal error on pipe transport'):
        # should be called by exception handler only
        ikiwa isinstance(exc, OSError):
            ikiwa self._loop.get_debug():
                logger.debug("%r: %s", self, message, exc_info=Kweli)
        isipokua:
            self._loop.call_exception_handler({
                'message': message,
                'exception': exc,
                'transport': self,
                'protocol': self._protocol,
            })
        self._close(exc)

    eleza _close(self, exc=Tupu):
        self._closing = Kweli
        ikiwa self._buffer:
            self._loop._remove_writer(self._fileno)
        self._buffer.clear()
        self._loop._remove_reader(self._fileno)
        self._loop.call_soon(self._call_connection_lost, exc)

    eleza _call_connection_lost(self, exc):
        jaribu:
            self._protocol.connection_lost(exc)
        mwishowe:
            self._pipe.close()
            self._pipe = Tupu
            self._protocol = Tupu
            self._loop = Tupu


kundi _UnixSubprocessTransport(base_subprocess.BaseSubprocessTransport):

    eleza _start(self, args, shell, stdin, stdout, stderr, bufsize, **kwargs):
        stdin_w = Tupu
        ikiwa stdin == subprocess.PIPE:
            # Use a socket pair kila stdin, since sio all platforms
            # support selecting read events on the write end of a
            # socket (which we use kwenye order to detect closing of the
            # other end).  Notably this ni needed on AIX, na works
            # just fine on other platforms.
            stdin, stdin_w = socket.socketpair()
        jaribu:
            self._proc = subprocess.Popen(
                args, shell=shell, stdin=stdin, stdout=stdout, stderr=stderr,
                universal_newlines=Uongo, bufsize=bufsize, **kwargs)
            ikiwa stdin_w ni sio Tupu:
                stdin.close()
                self._proc.stdin = open(stdin_w.detach(), 'wb', buffering=bufsize)
                stdin_w = Tupu
        mwishowe:
            ikiwa stdin_w ni sio Tupu:
                stdin.close()
                stdin_w.close()


kundi AbstractChildWatcher:
    """Abstract base kundi kila monitoring child processes.

    Objects derived kutoka this kundi monitor a collection of subprocesses na
    report their termination ama interruption by a signal.

    New callbacks are registered ukijumuisha .add_child_handler(). Starting a new
    process must be done within a 'with' block to allow the watcher to suspend
    its activity until the new process ikiwa fully registered (this ni needed to
    prevent a race condition kwenye some implementations).

    Example:
        ukijumuisha watcher:
            proc = subprocess.Popen("sleep 1")
            watcher.add_child_handler(proc.pid, callback)

    Notes:
        Implementations of this kundi must be thread-safe.

        Since child watcher objects may catch the SIGCHLD signal na call
        waitpid(-1), there should be only one active object per process.
    """

    eleza add_child_handler(self, pid, callback, *args):
        """Register a new child handler.

        Arrange kila callback(pid, returncode, *args) to be called when
        process 'pid' terminates. Specifying another callback kila the same
        process replaces the previous handler.

        Note: callback() must be thread-safe.
        """
        ashiria NotImplementedError()

    eleza remove_child_handler(self, pid):
        """Removes the handler kila process 'pid'.

        The function returns Kweli ikiwa the handler was successfully removed,
        Uongo ikiwa there was nothing to remove."""

        ashiria NotImplementedError()

    eleza attach_loop(self, loop):
        """Attach the watcher to an event loop.

        If the watcher was previously attached to an event loop, then it is
        first detached before attaching to the new loop.

        Note: loop may be Tupu.
        """
        ashiria NotImplementedError()

    eleza close(self):
        """Close the watcher.

        This must be called to make sure that any underlying resource ni freed.
        """
        ashiria NotImplementedError()

    eleza is_active(self):
        """Return ``Kweli`` ikiwa the watcher ni active na ni used by the event loop.

        Return Kweli ikiwa the watcher ni installed na ready to handle process exit
        notifications.

        """
        ashiria NotImplementedError()

    eleza __enter__(self):
        """Enter the watcher's context na allow starting new processes

        This function must rudisha self"""
        ashiria NotImplementedError()

    eleza __exit__(self, a, b, c):
        """Exit the watcher's context"""
        ashiria NotImplementedError()


eleza _compute_returncode(status):
    ikiwa os.WIFSIGNALED(status):
        # The child process died because of a signal.
        rudisha -os.WTERMSIG(status)
    lasivyo os.WIFEXITED(status):
        # The child process exited (e.g sys.exit()).
        rudisha os.WEXITSTATUS(status)
    isipokua:
        # The child exited, but we don't understand its status.
        # This shouldn't happen, but ikiwa it does, let's just
        # rudisha that status; perhaps that helps debug it.
        rudisha status


kundi BaseChildWatcher(AbstractChildWatcher):

    eleza __init__(self):
        self._loop = Tupu
        self._callbacks = {}

    eleza close(self):
        self.attach_loop(Tupu)

    eleza is_active(self):
        rudisha self._loop ni sio Tupu na self._loop.is_running()

    eleza _do_waitpid(self, expected_pid):
        ashiria NotImplementedError()

    eleza _do_waitpid_all(self):
        ashiria NotImplementedError()

    eleza attach_loop(self, loop):
        assert loop ni Tupu ama isinstance(loop, events.AbstractEventLoop)

        ikiwa self._loop ni sio Tupu na loop ni Tupu na self._callbacks:
            warnings.warn(
                'A loop ni being detached '
                'kutoka a child watcher ukijumuisha pending handlers',
                RuntimeWarning)

        ikiwa self._loop ni sio Tupu:
            self._loop.remove_signal_handler(signal.SIGCHLD)

        self._loop = loop
        ikiwa loop ni sio Tupu:
            loop.add_signal_handler(signal.SIGCHLD, self._sig_chld)

            # Prevent a race condition kwenye case a child terminated
            # during the switch.
            self._do_waitpid_all()

    eleza _sig_chld(self):
        jaribu:
            self._do_waitpid_all()
        tatizo (SystemExit, KeyboardInterrupt):
            raise
        tatizo BaseException kama exc:
            # self._loop should always be available here
            # kama '_sig_chld' ni added kama a signal handler
            # kwenye 'attach_loop'
            self._loop.call_exception_handler({
                'message': 'Unknown exception kwenye SIGCHLD handler',
                'exception': exc,
            })


kundi SafeChildWatcher(BaseChildWatcher):
    """'Safe' child watcher implementation.

    This implementation avoids disrupting other code spawning processes by
    polling explicitly each process kwenye the SIGCHLD handler instead of calling
    os.waitpid(-1).

    This ni a safe solution but it has a significant overhead when handling a
    big number of children (O(n) each time SIGCHLD ni raised)
    """

    eleza close(self):
        self._callbacks.clear()
        super().close()

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, a, b, c):
        pita

    eleza add_child_handler(self, pid, callback, *args):
        self._callbacks[pid] = (callback, args)

        # Prevent a race condition kwenye case the child ni already terminated.
        self._do_waitpid(pid)

    eleza remove_child_handler(self, pid):
        jaribu:
            toa self._callbacks[pid]
            rudisha Kweli
        tatizo KeyError:
            rudisha Uongo

    eleza _do_waitpid_all(self):

        kila pid kwenye list(self._callbacks):
            self._do_waitpid(pid)

    eleza _do_waitpid(self, expected_pid):
        assert expected_pid > 0

        jaribu:
            pid, status = os.waitpid(expected_pid, os.WNOHANG)
        tatizo ChildProcessError:
            # The child process ni already reaped
            # (may happen ikiwa waitpid() ni called elsewhere).
            pid = expected_pid
            returncode = 255
            logger.warning(
                "Unknown child process pid %d, will report returncode 255",
                pid)
        isipokua:
            ikiwa pid == 0:
                # The child process ni still alive.
                return

            returncode = _compute_returncode(status)
            ikiwa self._loop.get_debug():
                logger.debug('process %s exited ukijumuisha returncode %s',
                             expected_pid, returncode)

        jaribu:
            callback, args = self._callbacks.pop(pid)
        tatizo KeyError:  # pragma: no cover
            # May happen ikiwa .remove_child_handler() ni called
            # after os.waitpid() returns.
            ikiwa self._loop.get_debug():
                logger.warning("Child watcher got an unexpected pid: %r",
                               pid, exc_info=Kweli)
        isipokua:
            callback(pid, returncode, *args)


kundi FastChildWatcher(BaseChildWatcher):
    """'Fast' child watcher implementation.

    This implementation reaps every terminated processes by calling
    os.waitpid(-1) directly, possibly komaing other code spawning processes
    na waiting kila their termination.

    There ni no noticeable overhead when handling a big number of children
    (O(1) each time a child terminates).
    """
    eleza __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._zombies = {}
        self._forks = 0

    eleza close(self):
        self._callbacks.clear()
        self._zombies.clear()
        super().close()

    eleza __enter__(self):
        ukijumuisha self._lock:
            self._forks += 1

            rudisha self

    eleza __exit__(self, a, b, c):
        ukijumuisha self._lock:
            self._forks -= 1

            ikiwa self._forks ama sio self._zombies:
                return

            collateral_victims = str(self._zombies)
            self._zombies.clear()

        logger.warning(
            "Caught subprocesses termination kutoka unknown pids: %s",
            collateral_victims)

    eleza add_child_handler(self, pid, callback, *args):
        assert self._forks, "Must use the context manager"

        ukijumuisha self._lock:
            jaribu:
                returncode = self._zombies.pop(pid)
            tatizo KeyError:
                # The child ni running.
                self._callbacks[pid] = callback, args
                return

        # The child ni dead already. We can fire the callback.
        callback(pid, returncode, *args)

    eleza remove_child_handler(self, pid):
        jaribu:
            toa self._callbacks[pid]
            rudisha Kweli
        tatizo KeyError:
            rudisha Uongo

    eleza _do_waitpid_all(self):
        # Because of signal coalescing, we must keep calling waitpid() as
        # long kama we're able to reap a child.
        wakati Kweli:
            jaribu:
                pid, status = os.waitpid(-1, os.WNOHANG)
            tatizo ChildProcessError:
                # No more child processes exist.
                return
            isipokua:
                ikiwa pid == 0:
                    # A child process ni still alive.
                    return

                returncode = _compute_returncode(status)

            ukijumuisha self._lock:
                jaribu:
                    callback, args = self._callbacks.pop(pid)
                tatizo KeyError:
                    # unknown child
                    ikiwa self._forks:
                        # It may sio be registered yet.
                        self._zombies[pid] = returncode
                        ikiwa self._loop.get_debug():
                            logger.debug('unknown process %s exited '
                                         'ukijumuisha returncode %s',
                                         pid, returncode)
                        endelea
                    callback = Tupu
                isipokua:
                    ikiwa self._loop.get_debug():
                        logger.debug('process %s exited ukijumuisha returncode %s',
                                     pid, returncode)

            ikiwa callback ni Tupu:
                logger.warning(
                    "Caught subprocess termination kutoka unknown pid: "
                    "%d -> %d", pid, returncode)
            isipokua:
                callback(pid, returncode, *args)


kundi MultiLoopChildWatcher(AbstractChildWatcher):
    """A watcher that doesn't require running loop kwenye the main thread.

    This implementation registers a SIGCHLD signal handler on
    instantiation (which may conflict ukijumuisha other code that
    install own handler kila this signal).

    The solution ni safe but it has a significant overhead when
    handling a big number of processes (*O(n)* each time a
    SIGCHLD ni received).
    """

    # Implementation note:
    # The kundi keeps compatibility ukijumuisha AbstractChildWatcher ABC
    # To achieve this it has empty attach_loop() method
    # na doesn't accept explicit loop argument
    # kila add_child_handler()/remove_child_handler()
    # but retrieves the current loop by get_running_loop()

    eleza __init__(self):
        self._callbacks = {}
        self._saved_sighandler = Tupu

    eleza is_active(self):
        rudisha self._saved_sighandler ni sio Tupu

    eleza close(self):
        self._callbacks.clear()
        ikiwa self._saved_sighandler ni sio Tupu:
            handler = signal.getsignal(signal.SIGCHLD)
            ikiwa handler != self._sig_chld:
                logger.warning("SIGCHLD handler was changed by outside code")
            isipokua:
                signal.signal(signal.SIGCHLD, self._saved_sighandler)
            self._saved_sighandler = Tupu

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_val, exc_tb):
        pita

    eleza add_child_handler(self, pid, callback, *args):
        loop = events.get_running_loop()
        self._callbacks[pid] = (loop, callback, args)

        # Prevent a race condition kwenye case the child ni already terminated.
        self._do_waitpid(pid)

    eleza remove_child_handler(self, pid):
        jaribu:
            toa self._callbacks[pid]
            rudisha Kweli
        tatizo KeyError:
            rudisha Uongo

    eleza attach_loop(self, loop):
        # Don't save the loop but initialize itself ikiwa called first time
        # The reason to do it here ni that attach_loop() ni called from
        # unix policy only kila the main thread.
        # Main thread ni required kila subscription on SIGCHLD signal
        ikiwa self._saved_sighandler ni Tupu:
            self._saved_sighandler = signal.signal(signal.SIGCHLD, self._sig_chld)
            ikiwa self._saved_sighandler ni Tupu:
                logger.warning("Previous SIGCHLD handler was set by non-Python code, "
                               "restore to default handler on watcher close.")
                self._saved_sighandler = signal.SIG_DFL

            # Set SA_RESTART to limit EINTR occurrences.
            signal.siginterrupt(signal.SIGCHLD, Uongo)

    eleza _do_waitpid_all(self):
        kila pid kwenye list(self._callbacks):
            self._do_waitpid(pid)

    eleza _do_waitpid(self, expected_pid):
        assert expected_pid > 0

        jaribu:
            pid, status = os.waitpid(expected_pid, os.WNOHANG)
        tatizo ChildProcessError:
            # The child process ni already reaped
            # (may happen ikiwa waitpid() ni called elsewhere).
            pid = expected_pid
            returncode = 255
            logger.warning(
                "Unknown child process pid %d, will report returncode 255",
                pid)
            debug_log = Uongo
        isipokua:
            ikiwa pid == 0:
                # The child process ni still alive.
                return

            returncode = _compute_returncode(status)
            debug_log = Kweli
        jaribu:
            loop, callback, args = self._callbacks.pop(pid)
        tatizo KeyError:  # pragma: no cover
            # May happen ikiwa .remove_child_handler() ni called
            # after os.waitpid() returns.
            logger.warning("Child watcher got an unexpected pid: %r",
                           pid, exc_info=Kweli)
        isipokua:
            ikiwa loop.is_closed():
                logger.warning("Loop %r that handles pid %r ni closed", loop, pid)
            isipokua:
                ikiwa debug_log na loop.get_debug():
                    logger.debug('process %s exited ukijumuisha returncode %s',
                                 expected_pid, returncode)
                loop.call_soon_threadsafe(callback, pid, returncode, *args)

    eleza _sig_chld(self, signum, frame):
        jaribu:
            self._do_waitpid_all()
        tatizo (SystemExit, KeyboardInterrupt):
            raise
        tatizo BaseException:
            logger.warning('Unknown exception kwenye SIGCHLD handler', exc_info=Kweli)


kundi ThreadedChildWatcher(AbstractChildWatcher):
    """Threaded child watcher implementation.

    The watcher uses a thread per process
    kila waiting kila the process finish.

    It doesn't require subscription on POSIX signal
    but a thread creation ni sio free.

    The watcher has O(1) complexity, its performance doesn't depend
    on amount of spawn processes.
    """

    eleza __init__(self):
        self._pid_counter = itertools.count(0)
        self._threads = {}

    eleza is_active(self):
        rudisha Kweli

    eleza close(self):
        pita

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_val, exc_tb):
        pita

    eleza __del__(self, _warn=warnings.warn):
        threads = [thread kila thread kwenye list(self._threads.values())
                   ikiwa thread.is_alive()]
        ikiwa threads:
            _warn(f"{self.__class__} has registered but sio finished child processes",
                  ResourceWarning,
                  source=self)

    eleza add_child_handler(self, pid, callback, *args):
        loop = events.get_running_loop()
        thread = threading.Thread(target=self._do_waitpid,
                                  name=f"waitpid-{next(self._pid_counter)}",
                                  args=(loop, pid, callback, args),
                                  daemon=Kweli)
        self._threads[pid] = thread
        thread.start()

    eleza remove_child_handler(self, pid):
        # asyncio never calls remove_child_handler() !!!
        # The method ni no-op but ni implemented because
        # abstract base classe requires it
        rudisha Kweli

    eleza attach_loop(self, loop):
        pita

    eleza _do_waitpid(self, loop, expected_pid, callback, args):
        assert expected_pid > 0

        jaribu:
            pid, status = os.waitpid(expected_pid, 0)
        tatizo ChildProcessError:
            # The child process ni already reaped
            # (may happen ikiwa waitpid() ni called elsewhere).
            pid = expected_pid
            returncode = 255
            logger.warning(
                "Unknown child process pid %d, will report returncode 255",
                pid)
        isipokua:
            returncode = _compute_returncode(status)
            ikiwa loop.get_debug():
                logger.debug('process %s exited ukijumuisha returncode %s',
                             expected_pid, returncode)

        ikiwa loop.is_closed():
            logger.warning("Loop %r that handles pid %r ni closed", loop, pid)
        isipokua:
            loop.call_soon_threadsafe(callback, pid, returncode, *args)

        self._threads.pop(expected_pid)


kundi _UnixDefaultEventLoopPolicy(events.BaseDefaultEventLoopPolicy):
    """UNIX event loop policy ukijumuisha a watcher kila child processes."""
    _loop_factory = _UnixSelectorEventLoop

    eleza __init__(self):
        super().__init__()
        self._watcher = Tupu

    eleza _init_watcher(self):
        ukijumuisha events._lock:
            ikiwa self._watcher ni Tupu:  # pragma: no branch
                self._watcher = ThreadedChildWatcher()
                ikiwa isinstance(threading.current_thread(),
                              threading._MainThread):
                    self._watcher.attach_loop(self._local._loop)

    eleza set_event_loop(self, loop):
        """Set the event loop.

        As a side effect, ikiwa a child watcher was set before, then calling
        .set_event_loop() kutoka the main thread will call .attach_loop(loop) on
        the child watcher.
        """

        super().set_event_loop(loop)

        ikiwa (self._watcher ni sio Tupu na
                isinstance(threading.current_thread(), threading._MainThread)):
            self._watcher.attach_loop(loop)

    eleza get_child_watcher(self):
        """Get the watcher kila child processes.

        If sio yet set, a ThreadedChildWatcher object ni automatically created.
        """
        ikiwa self._watcher ni Tupu:
            self._init_watcher()

        rudisha self._watcher

    eleza set_child_watcher(self, watcher):
        """Set the watcher kila child processes."""

        assert watcher ni Tupu ama isinstance(watcher, AbstractChildWatcher)

        ikiwa self._watcher ni sio Tupu:
            self._watcher.close()

        self._watcher = watcher


SelectorEventLoop = _UnixSelectorEventLoop
DefaultEventLoopPolicy = _UnixDefaultEventLoopPolicy
