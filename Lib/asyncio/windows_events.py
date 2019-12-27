"""Selector and proactor event loops for Windows."""

agiza _overlapped
agiza _winapi
agiza errno
agiza math
agiza msvcrt
agiza socket
agiza struct
agiza time
agiza weakref

kutoka . agiza events
kutoka . agiza base_subprocess
kutoka . agiza futures
kutoka . agiza exceptions
kutoka . agiza proactor_events
kutoka . agiza selector_events
kutoka . agiza tasks
kutoka . agiza windows_utils
kutoka .log agiza logger


__all__ = (
    'SelectorEventLoop', 'ProactorEventLoop', 'IocpProactor',
    'DefaultEventLoopPolicy', 'WindowsSelectorEventLoopPolicy',
    'WindowsProactorEventLoopPolicy',
)


NULL = 0
INFINITE = 0xffffffff
ERROR_CONNECTION_REFUSED = 1225
ERROR_CONNECTION_ABORTED = 1236

# Initial delay in seconds for connect_pipe() before retrying to connect
CONNECT_PIPE_INIT_DELAY = 0.001

# Maximum delay in seconds for connect_pipe() before retrying to connect
CONNECT_PIPE_MAX_DELAY = 0.100


kundi _OverlappedFuture(futures.Future):
    """Subkundi of Future which represents an overlapped operation.

    Cancelling it will immediately cancel the overlapped operation.
    """

    eleza __init__(self, ov, *, loop=None):
        super().__init__(loop=loop)
        ikiwa self._source_traceback:
            del self._source_traceback[-1]
        self._ov = ov

    eleza _repr_info(self):
        info = super()._repr_info()
        ikiwa self._ov is not None:
            state = 'pending' ikiwa self._ov.pending else 'completed'
            info.insert(1, f'overlapped=<{state}, {self._ov.address:#x}>')
        rudisha info

    eleza _cancel_overlapped(self):
        ikiwa self._ov is None:
            return
        try:
            self._ov.cancel()
        except OSError as exc:
            context = {
                'message': 'Cancelling an overlapped future failed',
                'exception': exc,
                'future': self,
            }
            ikiwa self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)
        self._ov = None

    eleza cancel(self):
        self._cancel_overlapped()
        rudisha super().cancel()

    eleza set_exception(self, exception):
        super().set_exception(exception)
        self._cancel_overlapped()

    eleza set_result(self, result):
        super().set_result(result)
        self._ov = None


kundi _BaseWaitHandleFuture(futures.Future):
    """Subkundi of Future which represents a wait handle."""

    eleza __init__(self, ov, handle, wait_handle, *, loop=None):
        super().__init__(loop=loop)
        ikiwa self._source_traceback:
            del self._source_traceback[-1]
        # Keep a reference to the Overlapped object to keep it alive until the
        # wait is unregistered
        self._ov = ov
        self._handle = handle
        self._wait_handle = wait_handle

        # Should we call UnregisterWaitEx() ikiwa the wait completes
        # or is cancelled?
        self._registered = True

    eleza _poll(self):
        # non-blocking wait: use a timeout of 0 millisecond
        rudisha (_winapi.WaitForSingleObject(self._handle, 0) ==
                _winapi.WAIT_OBJECT_0)

    eleza _repr_info(self):
        info = super()._repr_info()
        info.append(f'handle={self._handle:#x}')
        ikiwa self._handle is not None:
            state = 'signaled' ikiwa self._poll() else 'waiting'
            info.append(state)
        ikiwa self._wait_handle is not None:
            info.append(f'wait_handle={self._wait_handle:#x}')
        rudisha info

    eleza _unregister_wait_cb(self, fut):
        # The wait was unregistered: it's not safe to destroy the Overlapped
        # object
        self._ov = None

    eleza _unregister_wait(self):
        ikiwa not self._registered:
            return
        self._registered = False

        wait_handle = self._wait_handle
        self._wait_handle = None
        try:
            _overlapped.UnregisterWait(wait_handle)
        except OSError as exc:
            ikiwa exc.winerror != _overlapped.ERROR_IO_PENDING:
                context = {
                    'message': 'Failed to unregister the wait handle',
                    'exception': exc,
                    'future': self,
                }
                ikiwa self._source_traceback:
                    context['source_traceback'] = self._source_traceback
                self._loop.call_exception_handler(context)
                return
            # ERROR_IO_PENDING means that the unregister is pending

        self._unregister_wait_cb(None)

    eleza cancel(self):
        self._unregister_wait()
        rudisha super().cancel()

    eleza set_exception(self, exception):
        self._unregister_wait()
        super().set_exception(exception)

    eleza set_result(self, result):
        self._unregister_wait()
        super().set_result(result)


kundi _WaitCancelFuture(_BaseWaitHandleFuture):
    """Subkundi of Future which represents a wait for the cancellation of a
    _WaitHandleFuture using an event.
    """

    eleza __init__(self, ov, event, wait_handle, *, loop=None):
        super().__init__(ov, event, wait_handle, loop=loop)

        self._done_callback = None

    eleza cancel(self):
        raise RuntimeError("_WaitCancelFuture must not be cancelled")

    eleza set_result(self, result):
        super().set_result(result)
        ikiwa self._done_callback is not None:
            self._done_callback(self)

    eleza set_exception(self, exception):
        super().set_exception(exception)
        ikiwa self._done_callback is not None:
            self._done_callback(self)


kundi _WaitHandleFuture(_BaseWaitHandleFuture):
    eleza __init__(self, ov, handle, wait_handle, proactor, *, loop=None):
        super().__init__(ov, handle, wait_handle, loop=loop)
        self._proactor = proactor
        self._unregister_proactor = True
        self._event = _overlapped.CreateEvent(None, True, False, None)
        self._event_fut = None

    eleza _unregister_wait_cb(self, fut):
        ikiwa self._event is not None:
            _winapi.CloseHandle(self._event)
            self._event = None
            self._event_fut = None

        # If the wait was cancelled, the wait may never be signalled, so
        # it's required to unregister it. Otherwise, IocpProactor.close() will
        # wait forever for an event which will never come.
        #
        # If the IocpProactor already received the event, it's safe to call
        # _unregister() because we kept a reference to the Overlapped object
        # which is used as a unique key.
        self._proactor._unregister(self._ov)
        self._proactor = None

        super()._unregister_wait_cb(fut)

    eleza _unregister_wait(self):
        ikiwa not self._registered:
            return
        self._registered = False

        wait_handle = self._wait_handle
        self._wait_handle = None
        try:
            _overlapped.UnregisterWaitEx(wait_handle, self._event)
        except OSError as exc:
            ikiwa exc.winerror != _overlapped.ERROR_IO_PENDING:
                context = {
                    'message': 'Failed to unregister the wait handle',
                    'exception': exc,
                    'future': self,
                }
                ikiwa self._source_traceback:
                    context['source_traceback'] = self._source_traceback
                self._loop.call_exception_handler(context)
                return
            # ERROR_IO_PENDING is not an error, the wait was unregistered

        self._event_fut = self._proactor._wait_cancel(self._event,
                                                      self._unregister_wait_cb)


kundi PipeServer(object):
    """Class representing a pipe server.

    This is much like a bound, listening socket.
    """
    eleza __init__(self, address):
        self._address = address
        self._free_instances = weakref.WeakSet()
        # initialize the pipe attribute before calling _server_pipe_handle()
        # because this function can raise an exception and the destructor calls
        # the close() method
        self._pipe = None
        self._accept_pipe_future = None
        self._pipe = self._server_pipe_handle(True)

    eleza _get_unconnected_pipe(self):
        # Create new instance and rudisha previous one.  This ensures
        # that (until the server is closed) there is always at least
        # one pipe handle for address.  Therefore ikiwa a client attempt
        # to connect it will not fail with FileNotFoundError.
        tmp, self._pipe = self._pipe, self._server_pipe_handle(False)
        rudisha tmp

    eleza _server_pipe_handle(self, first):
        # Return a wrapper for a new pipe handle.
        ikiwa self.closed():
            rudisha None
        flags = _winapi.PIPE_ACCESS_DUPLEX | _winapi.FILE_FLAG_OVERLAPPED
        ikiwa first:
            flags |= _winapi.FILE_FLAG_FIRST_PIPE_INSTANCE
        h = _winapi.CreateNamedPipe(
            self._address, flags,
            _winapi.PIPE_TYPE_MESSAGE | _winapi.PIPE_READMODE_MESSAGE |
            _winapi.PIPE_WAIT,
            _winapi.PIPE_UNLIMITED_INSTANCES,
            windows_utils.BUFSIZE, windows_utils.BUFSIZE,
            _winapi.NMPWAIT_WAIT_FOREVER, _winapi.NULL)
        pipe = windows_utils.PipeHandle(h)
        self._free_instances.add(pipe)
        rudisha pipe

    eleza closed(self):
        rudisha (self._address is None)

    eleza close(self):
        ikiwa self._accept_pipe_future is not None:
            self._accept_pipe_future.cancel()
            self._accept_pipe_future = None
        # Close all instances which have not been connected to by a client.
        ikiwa self._address is not None:
            for pipe in self._free_instances:
                pipe.close()
            self._pipe = None
            self._address = None
            self._free_instances.clear()

    __del__ = close


kundi _WindowsSelectorEventLoop(selector_events.BaseSelectorEventLoop):
    """Windows version of selector event loop."""


kundi ProactorEventLoop(proactor_events.BaseProactorEventLoop):
    """Windows version of proactor event loop using IOCP."""

    eleza __init__(self, proactor=None):
        ikiwa proactor is None:
            proactor = IocpProactor()
        super().__init__(proactor)

    eleza run_forever(self):
        try:
            assert self._self_reading_future is None
            self.call_soon(self._loop_self_reading)
            super().run_forever()
        finally:
            ikiwa self._self_reading_future is not None:
                ov = self._self_reading_future._ov
                self._self_reading_future.cancel()
                # self_reading_future was just cancelled so it will never be signalled
                # Unregister it otherwise IocpProactor.close will wait for it forever
                ikiwa ov is not None:
                    self._proactor._unregister(ov)
                self._self_reading_future = None

    async eleza create_pipe_connection(self, protocol_factory, address):
        f = self._proactor.connect_pipe(address)
        pipe = await f
        protocol = protocol_factory()
        trans = self._make_duplex_pipe_transport(pipe, protocol,
                                                 extra={'addr': address})
        rudisha trans, protocol

    async eleza start_serving_pipe(self, protocol_factory, address):
        server = PipeServer(address)

        eleza loop_accept_pipe(f=None):
            pipe = None
            try:
                ikiwa f:
                    pipe = f.result()
                    server._free_instances.discard(pipe)

                    ikiwa server.closed():
                        # A client connected before the server was closed:
                        # drop the client (close the pipe) and exit
                        pipe.close()
                        return

                    protocol = protocol_factory()
                    self._make_duplex_pipe_transport(
                        pipe, protocol, extra={'addr': address})

                pipe = server._get_unconnected_pipe()
                ikiwa pipe is None:
                    return

                f = self._proactor.accept_pipe(pipe)
            except OSError as exc:
                ikiwa pipe and pipe.fileno() != -1:
                    self.call_exception_handler({
                        'message': 'Pipe accept failed',
                        'exception': exc,
                        'pipe': pipe,
                    })
                    pipe.close()
                elikiwa self._debug:
                    logger.warning("Accept pipe failed on pipe %r",
                                   pipe, exc_info=True)
            except exceptions.CancelledError:
                ikiwa pipe:
                    pipe.close()
            else:
                server._accept_pipe_future = f
                f.add_done_callback(loop_accept_pipe)

        self.call_soon(loop_accept_pipe)
        rudisha [server]

    async eleza _make_subprocess_transport(self, protocol, args, shell,
                                         stdin, stdout, stderr, bufsize,
                                         extra=None, **kwargs):
        waiter = self.create_future()
        transp = _WindowsSubprocessTransport(self, protocol, args, shell,
                                             stdin, stdout, stderr, bufsize,
                                             waiter=waiter, extra=extra,
                                             **kwargs)
        try:
            await waiter
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException:
            transp.close()
            await transp._wait()
            raise

        rudisha transp


kundi IocpProactor:
    """Proactor implementation using IOCP."""

    eleza __init__(self, concurrency=0xffffffff):
        self._loop = None
        self._results = []
        self._iocp = _overlapped.CreateIoCompletionPort(
            _overlapped.INVALID_HANDLE_VALUE, NULL, 0, concurrency)
        self._cache = {}
        self._registered = weakref.WeakSet()
        self._unregistered = []
        self._stopped_serving = weakref.WeakSet()

    eleza _check_closed(self):
        ikiwa self._iocp is None:
            raise RuntimeError('IocpProactor is closed')

    eleza __repr__(self):
        info = ['overlapped#=%s' % len(self._cache),
                'result#=%s' % len(self._results)]
        ikiwa self._iocp is None:
            info.append('closed')
        rudisha '<%s %s>' % (self.__class__.__name__, " ".join(info))

    eleza set_loop(self, loop):
        self._loop = loop

    eleza select(self, timeout=None):
        ikiwa not self._results:
            self._poll(timeout)
        tmp = self._results
        self._results = []
        rudisha tmp

    eleza _result(self, value):
        fut = self._loop.create_future()
        fut.set_result(value)
        rudisha fut

    eleza recv(self, conn, nbytes, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        try:
            ikiwa isinstance(conn, socket.socket):
                ov.WSARecv(conn.fileno(), nbytes, flags)
            else:
                ov.ReadFile(conn.fileno(), nbytes)
        except BrokenPipeError:
            rudisha self._result(b'')

        eleza finish_recv(trans, key, ov):
            try:
                rudisha ov.getresult()
            except OSError as exc:
                ikiwa exc.winerror in (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    raise ConnectionResetError(*exc.args)
                else:
                    raise

        rudisha self._register(ov, conn, finish_recv)

    eleza recv_into(self, conn, buf, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        try:
            ikiwa isinstance(conn, socket.socket):
                ov.WSARecvInto(conn.fileno(), buf, flags)
            else:
                ov.ReadFileInto(conn.fileno(), buf)
        except BrokenPipeError:
            rudisha self._result(b'')

        eleza finish_recv(trans, key, ov):
            try:
                rudisha ov.getresult()
            except OSError as exc:
                ikiwa exc.winerror in (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    raise ConnectionResetError(*exc.args)
                else:
                    raise

        rudisha self._register(ov, conn, finish_recv)

    eleza recvkutoka(self, conn, nbytes, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        try:
            ov.WSARecvFrom(conn.fileno(), nbytes, flags)
        except BrokenPipeError:
            rudisha self._result((b'', None))

        eleza finish_recv(trans, key, ov):
            try:
                rudisha ov.getresult()
            except OSError as exc:
                ikiwa exc.winerror in (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    raise ConnectionResetError(*exc.args)
                else:
                    raise

        rudisha self._register(ov, conn, finish_recv)

    eleza sendto(self, conn, buf, flags=0, addr=None):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)

        ov.WSASendTo(conn.fileno(), buf, flags, addr)

        eleza finish_send(trans, key, ov):
            try:
                rudisha ov.getresult()
            except OSError as exc:
                ikiwa exc.winerror in (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    raise ConnectionResetError(*exc.args)
                else:
                    raise

        rudisha self._register(ov, conn, finish_send)

    eleza send(self, conn, buf, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        ikiwa isinstance(conn, socket.socket):
            ov.WSASend(conn.fileno(), buf, flags)
        else:
            ov.WriteFile(conn.fileno(), buf)

        eleza finish_send(trans, key, ov):
            try:
                rudisha ov.getresult()
            except OSError as exc:
                ikiwa exc.winerror in (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    raise ConnectionResetError(*exc.args)
                else:
                    raise

        rudisha self._register(ov, conn, finish_send)

    eleza accept(self, listener):
        self._register_with_iocp(listener)
        conn = self._get_accept_socket(listener.family)
        ov = _overlapped.Overlapped(NULL)
        ov.AcceptEx(listener.fileno(), conn.fileno())

        eleza finish_accept(trans, key, ov):
            ov.getresult()
            # Use SO_UPDATE_ACCEPT_CONTEXT so getsockname() etc work.
            buf = struct.pack('@P', listener.fileno())
            conn.setsockopt(socket.SOL_SOCKET,
                            _overlapped.SO_UPDATE_ACCEPT_CONTEXT, buf)
            conn.settimeout(listener.gettimeout())
            rudisha conn, conn.getpeername()

        async eleza accept_coro(future, conn):
            # Coroutine closing the accept socket ikiwa the future is cancelled
            try:
                await future
            except exceptions.CancelledError:
                conn.close()
                raise

        future = self._register(ov, listener, finish_accept)
        coro = accept_coro(future, conn)
        tasks.ensure_future(coro, loop=self._loop)
        rudisha future

    eleza connect(self, conn, address):
        ikiwa conn.type == socket.SOCK_DGRAM:
            # WSAConnect will complete immediately for UDP sockets so we don't
            # need to register any IOCP operation
            _overlapped.WSAConnect(conn.fileno(), address)
            fut = self._loop.create_future()
            fut.set_result(None)
            rudisha fut

        self._register_with_iocp(conn)
        # The socket needs to be locally bound before we call ConnectEx().
        try:
            _overlapped.BindLocal(conn.fileno(), conn.family)
        except OSError as e:
            ikiwa e.winerror != errno.WSAEINVAL:
                raise
            # Probably already locally bound; check using getsockname().
            ikiwa conn.getsockname()[1] == 0:
                raise
        ov = _overlapped.Overlapped(NULL)
        ov.ConnectEx(conn.fileno(), address)

        eleza finish_connect(trans, key, ov):
            ov.getresult()
            # Use SO_UPDATE_CONNECT_CONTEXT so getsockname() etc work.
            conn.setsockopt(socket.SOL_SOCKET,
                            _overlapped.SO_UPDATE_CONNECT_CONTEXT, 0)
            rudisha conn

        rudisha self._register(ov, conn, finish_connect)

    eleza sendfile(self, sock, file, offset, count):
        self._register_with_iocp(sock)
        ov = _overlapped.Overlapped(NULL)
        offset_low = offset & 0xffff_ffff
        offset_high = (offset >> 32) & 0xffff_ffff
        ov.TransmitFile(sock.fileno(),
                        msvcrt.get_osfhandle(file.fileno()),
                        offset_low, offset_high,
                        count, 0, 0)

        eleza finish_sendfile(trans, key, ov):
            try:
                rudisha ov.getresult()
            except OSError as exc:
                ikiwa exc.winerror in (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    raise ConnectionResetError(*exc.args)
                else:
                    raise
        rudisha self._register(ov, sock, finish_sendfile)

    eleza accept_pipe(self, pipe):
        self._register_with_iocp(pipe)
        ov = _overlapped.Overlapped(NULL)
        connected = ov.ConnectNamedPipe(pipe.fileno())

        ikiwa connected:
            # ConnectNamePipe() failed with ERROR_PIPE_CONNECTED which means
            # that the pipe is connected. There is no need to wait for the
            # completion of the connection.
            rudisha self._result(pipe)

        eleza finish_accept_pipe(trans, key, ov):
            ov.getresult()
            rudisha pipe

        rudisha self._register(ov, pipe, finish_accept_pipe)

    async eleza connect_pipe(self, address):
        delay = CONNECT_PIPE_INIT_DELAY
        while True:
            # Unfortunately there is no way to do an overlapped connect to
            # a pipe.  Call CreateFile() in a loop until it doesn't fail with
            # ERROR_PIPE_BUSY.
            try:
                handle = _overlapped.ConnectPipe(address)
                break
            except OSError as exc:
                ikiwa exc.winerror != _overlapped.ERROR_PIPE_BUSY:
                    raise

            # ConnectPipe() failed with ERROR_PIPE_BUSY: retry later
            delay = min(delay * 2, CONNECT_PIPE_MAX_DELAY)
            await tasks.sleep(delay)

        rudisha windows_utils.PipeHandle(handle)

    eleza wait_for_handle(self, handle, timeout=None):
        """Wait for a handle.

        Return a Future object. The result of the future is True ikiwa the wait
        completed, or False ikiwa the wait did not complete (on timeout).
        """
        rudisha self._wait_for_handle(handle, timeout, False)

    eleza _wait_cancel(self, event, done_callback):
        fut = self._wait_for_handle(event, None, True)
        # add_done_callback() cannot be used because the wait may only complete
        # in IocpProactor.close(), while the event loop is not running.
        fut._done_callback = done_callback
        rudisha fut

    eleza _wait_for_handle(self, handle, timeout, _is_cancel):
        self._check_closed()

        ikiwa timeout is None:
            ms = _winapi.INFINITE
        else:
            # RegisterWaitForSingleObject() has a resolution of 1 millisecond,
            # round away kutoka zero to wait *at least* timeout seconds.
            ms = math.ceil(timeout * 1e3)

        # We only create ov so we can use ov.address as a key for the cache.
        ov = _overlapped.Overlapped(NULL)
        wait_handle = _overlapped.RegisterWaitWithQueue(
            handle, self._iocp, ov.address, ms)
        ikiwa _is_cancel:
            f = _WaitCancelFuture(ov, handle, wait_handle, loop=self._loop)
        else:
            f = _WaitHandleFuture(ov, handle, wait_handle, self,
                                  loop=self._loop)
        ikiwa f._source_traceback:
            del f._source_traceback[-1]

        eleza finish_wait_for_handle(trans, key, ov):
            # Note that this second wait means that we should only use
            # this with handles types where a successful wait has no
            # effect.  So events or processes are all right, but locks
            # or semaphores are not.  Also note ikiwa the handle is
            # signalled and then quickly reset, then we may return
            # False even though we have not timed out.
            rudisha f._poll()

        self._cache[ov.address] = (f, ov, 0, finish_wait_for_handle)
        rudisha f

    eleza _register_with_iocp(self, obj):
        # To get notifications of finished ops on this objects sent to the
        # completion port, were must register the handle.
        ikiwa obj not in self._registered:
            self._registered.add(obj)
            _overlapped.CreateIoCompletionPort(obj.fileno(), self._iocp, 0, 0)
            # XXX We could also use SetFileCompletionNotificationModes()
            # to avoid sending notifications to completion port of ops
            # that succeed immediately.

    eleza _register(self, ov, obj, callback):
        self._check_closed()

        # Return a future which will be set with the result of the
        # operation when it completes.  The future's value is actually
        # the value returned by callback().
        f = _OverlappedFuture(ov, loop=self._loop)
        ikiwa f._source_traceback:
            del f._source_traceback[-1]
        ikiwa not ov.pending:
            # The operation has completed, so no need to postpone the
            # work.  We cannot take this short cut ikiwa we need the
            # NumberOfBytes, CompletionKey values returned by
            # PostQueuedCompletionStatus().
            try:
                value = callback(None, None, ov)
            except OSError as e:
                f.set_exception(e)
            else:
                f.set_result(value)
            # Even ikiwa GetOverlappedResult() was called, we have to wait for the
            # notification of the completion in GetQueuedCompletionStatus().
            # Register the overlapped operation to keep a reference to the
            # OVERLAPPED object, otherwise the memory is freed and Windows may
            # read uninitialized memory.

        # Register the overlapped operation for later.  Note that
        # we only store obj to prevent it kutoka being garbage
        # collected too early.
        self._cache[ov.address] = (f, ov, obj, callback)
        rudisha f

    eleza _unregister(self, ov):
        """Unregister an overlapped object.

        Call this method when its future has been cancelled. The event can
        already be signalled (pending in the proactor event queue). It is also
        safe ikiwa the event is never signalled (because it was cancelled).
        """
        self._check_closed()
        self._unregistered.append(ov)

    eleza _get_accept_socket(self, family):
        s = socket.socket(family)
        s.settimeout(0)
        rudisha s

    eleza _poll(self, timeout=None):
        ikiwa timeout is None:
            ms = INFINITE
        elikiwa timeout < 0:
            raise ValueError("negative timeout")
        else:
            # GetQueuedCompletionStatus() has a resolution of 1 millisecond,
            # round away kutoka zero to wait *at least* timeout seconds.
            ms = math.ceil(timeout * 1e3)
            ikiwa ms >= INFINITE:
                raise ValueError("timeout too big")

        while True:
            status = _overlapped.GetQueuedCompletionStatus(self._iocp, ms)
            ikiwa status is None:
                break
            ms = 0

            err, transferred, key, address = status
            try:
                f, ov, obj, callback = self._cache.pop(address)
            except KeyError:
                ikiwa self._loop.get_debug():
                    self._loop.call_exception_handler({
                        'message': ('GetQueuedCompletionStatus() returned an '
                                    'unexpected event'),
                        'status': ('err=%s transferred=%s key=%#x address=%#x'
                                   % (err, transferred, key, address)),
                    })

                # key is either zero, or it is used to rudisha a pipe
                # handle which should be closed to avoid a leak.
                ikiwa key not in (0, _overlapped.INVALID_HANDLE_VALUE):
                    _winapi.CloseHandle(key)
                continue

            ikiwa obj in self._stopped_serving:
                f.cancel()
            # Don't call the callback ikiwa _register() already read the result or
            # ikiwa the overlapped has been cancelled
            elikiwa not f.done():
                try:
                    value = callback(transferred, key, ov)
                except OSError as e:
                    f.set_exception(e)
                    self._results.append(f)
                else:
                    f.set_result(value)
                    self._results.append(f)

        # Remove unregistered futures
        for ov in self._unregistered:
            self._cache.pop(ov.address, None)
        self._unregistered.clear()

    eleza _stop_serving(self, obj):
        # obj is a socket or pipe handle.  It will be closed in
        # BaseProactorEventLoop._stop_serving() which will make any
        # pending operations fail quickly.
        self._stopped_serving.add(obj)

    eleza close(self):
        ikiwa self._iocp is None:
            # already closed
            return

        # Cancel remaining registered operations.
        for address, (fut, ov, obj, callback) in list(self._cache.items()):
            ikiwa fut.cancelled():
                # Nothing to do with cancelled futures
                pass
            elikiwa isinstance(fut, _WaitCancelFuture):
                # _WaitCancelFuture must not be cancelled
                pass
            else:
                try:
                    fut.cancel()
                except OSError as exc:
                    ikiwa self._loop is not None:
                        context = {
                            'message': 'Cancelling a future failed',
                            'exception': exc,
                            'future': fut,
                        }
                        ikiwa fut._source_traceback:
                            context['source_traceback'] = fut._source_traceback
                        self._loop.call_exception_handler(context)

        # Wait until all cancelled overlapped complete: don't exit with running
        # overlapped to prevent a crash. Display progress every second ikiwa the
        # loop is still running.
        msg_update = 1.0
        start_time = time.monotonic()
        next_msg = start_time + msg_update
        while self._cache:
            ikiwa next_msg <= time.monotonic():
                logger.debug('%r is running after closing for %.1f seconds',
                             self, time.monotonic() - start_time)
                next_msg = time.monotonic() + msg_update

            # handle a few events, or timeout
            self._poll(msg_update)

        self._results = []

        _winapi.CloseHandle(self._iocp)
        self._iocp = None

    eleza __del__(self):
        self.close()


kundi _WindowsSubprocessTransport(base_subprocess.BaseSubprocessTransport):

    eleza _start(self, args, shell, stdin, stdout, stderr, bufsize, **kwargs):
        self._proc = windows_utils.Popen(
            args, shell=shell, stdin=stdin, stdout=stdout, stderr=stderr,
            bufsize=bufsize, **kwargs)

        eleza callback(f):
            returncode = self._proc.poll()
            self._process_exited(returncode)

        f = self._loop._proactor.wait_for_handle(int(self._proc._handle))
        f.add_done_callback(callback)


SelectorEventLoop = _WindowsSelectorEventLoop


kundi WindowsSelectorEventLoopPolicy(events.BaseDefaultEventLoopPolicy):
    _loop_factory = SelectorEventLoop


kundi WindowsProactorEventLoopPolicy(events.BaseDefaultEventLoopPolicy):
    _loop_factory = ProactorEventLoop


DefaultEventLoopPolicy = WindowsProactorEventLoopPolicy
