"""Selector na proactor event loops kila Windows."""

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

# Initial delay kwenye seconds kila connect_pipe() before retrying to connect
CONNECT_PIPE_INIT_DELAY = 0.001

# Maximum delay kwenye seconds kila connect_pipe() before retrying to connect
CONNECT_PIPE_MAX_DELAY = 0.100


kundi _OverlappedFuture(futures.Future):
    """Subkundi of Future which represents an overlapped operation.

    Cancelling it will immediately cancel the overlapped operation.
    """

    eleza __init__(self, ov, *, loop=Tupu):
        super().__init__(loop=loop)
        ikiwa self._source_traceback:
            toa self._source_traceback[-1]
        self._ov = ov

    eleza _repr_info(self):
        info = super()._repr_info()
        ikiwa self._ov ni sio Tupu:
            state = 'pending' ikiwa self._ov.pending isipokua 'completed'
            info.insert(1, f'overlapped=<{state}, {self._ov.address:#x}>')
        rudisha info

    eleza _cancel_overlapped(self):
        ikiwa self._ov ni Tupu:
            rudisha
        jaribu:
            self._ov.cancel()
        tatizo OSError kama exc:
            context = {
                'message': 'Cancelling an overlapped future failed',
                'exception': exc,
                'future': self,
            }
            ikiwa self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)
        self._ov = Tupu

    eleza cancel(self):
        self._cancel_overlapped()
        rudisha super().cancel()

    eleza set_exception(self, exception):
        super().set_exception(exception)
        self._cancel_overlapped()

    eleza set_result(self, result):
        super().set_result(result)
        self._ov = Tupu


kundi _BaseWaitHandleFuture(futures.Future):
    """Subkundi of Future which represents a wait handle."""

    eleza __init__(self, ov, handle, wait_handle, *, loop=Tupu):
        super().__init__(loop=loop)
        ikiwa self._source_traceback:
            toa self._source_traceback[-1]
        # Keep a reference to the Overlapped object to keep it alive until the
        # wait ni unregistered
        self._ov = ov
        self._handle = handle
        self._wait_handle = wait_handle

        # Should we call UnregisterWaitEx() ikiwa the wait completes
        # ama ni cancelled?
        self._registered = Kweli

    eleza _poll(self):
        # non-blocking wait: use a timeout of 0 millisecond
        rudisha (_winapi.WaitForSingleObject(self._handle, 0) ==
                _winapi.WAIT_OBJECT_0)

    eleza _repr_info(self):
        info = super()._repr_info()
        info.append(f'handle={self._handle:#x}')
        ikiwa self._handle ni sio Tupu:
            state = 'signaled' ikiwa self._poll() isipokua 'waiting'
            info.append(state)
        ikiwa self._wait_handle ni sio Tupu:
            info.append(f'wait_handle={self._wait_handle:#x}')
        rudisha info

    eleza _unregister_wait_cb(self, fut):
        # The wait was unregistered: it's sio safe to destroy the Overlapped
        # object
        self._ov = Tupu

    eleza _unregister_wait(self):
        ikiwa sio self._registered:
            rudisha
        self._registered = Uongo

        wait_handle = self._wait_handle
        self._wait_handle = Tupu
        jaribu:
            _overlapped.UnregisterWait(wait_handle)
        tatizo OSError kama exc:
            ikiwa exc.winerror != _overlapped.ERROR_IO_PENDING:
                context = {
                    'message': 'Failed to unregister the wait handle',
                    'exception': exc,
                    'future': self,
                }
                ikiwa self._source_traceback:
                    context['source_traceback'] = self._source_traceback
                self._loop.call_exception_handler(context)
                rudisha
            # ERROR_IO_PENDING means that the unregister ni pending

        self._unregister_wait_cb(Tupu)

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
    """Subkundi of Future which represents a wait kila the cancellation of a
    _WaitHandleFuture using an event.
    """

    eleza __init__(self, ov, event, wait_handle, *, loop=Tupu):
        super().__init__(ov, event, wait_handle, loop=loop)

        self._done_callback = Tupu

    eleza cancel(self):
        ashiria RuntimeError("_WaitCancelFuture must sio be cancelled")

    eleza set_result(self, result):
        super().set_result(result)
        ikiwa self._done_callback ni sio Tupu:
            self._done_callback(self)

    eleza set_exception(self, exception):
        super().set_exception(exception)
        ikiwa self._done_callback ni sio Tupu:
            self._done_callback(self)


kundi _WaitHandleFuture(_BaseWaitHandleFuture):
    eleza __init__(self, ov, handle, wait_handle, proactor, *, loop=Tupu):
        super().__init__(ov, handle, wait_handle, loop=loop)
        self._proactor = proactor
        self._unregister_proactor = Kweli
        self._event = _overlapped.CreateEvent(Tupu, Kweli, Uongo, Tupu)
        self._event_fut = Tupu

    eleza _unregister_wait_cb(self, fut):
        ikiwa self._event ni sio Tupu:
            _winapi.CloseHandle(self._event)
            self._event = Tupu
            self._event_fut = Tupu

        # If the wait was cancelled, the wait may never be signalled, so
        # it's required to unregister it. Otherwise, IocpProactor.close() will
        # wait forever kila an event which will never come.
        #
        # If the IocpProactor already received the event, it's safe to call
        # _unregister() because we kept a reference to the Overlapped object
        # which ni used kama a unique key.
        self._proactor._unregister(self._ov)
        self._proactor = Tupu

        super()._unregister_wait_cb(fut)

    eleza _unregister_wait(self):
        ikiwa sio self._registered:
            rudisha
        self._registered = Uongo

        wait_handle = self._wait_handle
        self._wait_handle = Tupu
        jaribu:
            _overlapped.UnregisterWaitEx(wait_handle, self._event)
        tatizo OSError kama exc:
            ikiwa exc.winerror != _overlapped.ERROR_IO_PENDING:
                context = {
                    'message': 'Failed to unregister the wait handle',
                    'exception': exc,
                    'future': self,
                }
                ikiwa self._source_traceback:
                    context['source_traceback'] = self._source_traceback
                self._loop.call_exception_handler(context)
                rudisha
            # ERROR_IO_PENDING ni sio an error, the wait was unregistered

        self._event_fut = self._proactor._wait_cancel(self._event,
                                                      self._unregister_wait_cb)


kundi PipeServer(object):
    """Class representing a pipe server.

    This ni much like a bound, listening socket.
    """
    eleza __init__(self, address):
        self._address = address
        self._free_instances = weakref.WeakSet()
        # initialize the pipe attribute before calling _server_pipe_handle()
        # because this function can ashiria an exception na the destructor calls
        # the close() method
        self._pipe = Tupu
        self._accept_pipe_future = Tupu
        self._pipe = self._server_pipe_handle(Kweli)

    eleza _get_unconnected_pipe(self):
        # Create new instance na rudisha previous one.  This ensures
        # that (until the server ni closed) there ni always at least
        # one pipe handle kila address.  Therefore ikiwa a client attempt
        # to connect it will sio fail ukijumuisha FileNotFoundError.
        tmp, self._pipe = self._pipe, self._server_pipe_handle(Uongo)
        rudisha tmp

    eleza _server_pipe_handle(self, first):
        # Return a wrapper kila a new pipe handle.
        ikiwa self.closed():
            rudisha Tupu
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
        rudisha (self._address ni Tupu)

    eleza close(self):
        ikiwa self._accept_pipe_future ni sio Tupu:
            self._accept_pipe_future.cancel()
            self._accept_pipe_future = Tupu
        # Close all instances which have sio been connected to by a client.
        ikiwa self._address ni sio Tupu:
            kila pipe kwenye self._free_instances:
                pipe.close()
            self._pipe = Tupu
            self._address = Tupu
            self._free_instances.clear()

    __del__ = close


kundi _WindowsSelectorEventLoop(selector_events.BaseSelectorEventLoop):
    """Windows version of selector event loop."""


kundi ProactorEventLoop(proactor_events.BaseProactorEventLoop):
    """Windows version of proactor event loop using IOCP."""

    eleza __init__(self, proactor=Tupu):
        ikiwa proactor ni Tupu:
            proactor = IocpProactor()
        super().__init__(proactor)

    eleza run_forever(self):
        jaribu:
            assert self._self_reading_future ni Tupu
            self.call_soon(self._loop_self_reading)
            super().run_forever()
        mwishowe:
            ikiwa self._self_reading_future ni sio Tupu:
                ov = self._self_reading_future._ov
                self._self_reading_future.cancel()
                # self_reading_future was just cancelled so it will never be signalled
                # Unregister it otherwise IocpProactor.close will wait kila it forever
                ikiwa ov ni sio Tupu:
                    self._proactor._unregister(ov)
                self._self_reading_future = Tupu

    async eleza create_pipe_connection(self, protocol_factory, address):
        f = self._proactor.connect_pipe(address)
        pipe = await f
        protocol = protocol_factory()
        trans = self._make_duplex_pipe_transport(pipe, protocol,
                                                 extra={'addr': address})
        rudisha trans, protocol

    async eleza start_serving_pipe(self, protocol_factory, address):
        server = PipeServer(address)

        eleza loop_accept_pipe(f=Tupu):
            pipe = Tupu
            jaribu:
                ikiwa f:
                    pipe = f.result()
                    server._free_instances.discard(pipe)

                    ikiwa server.closed():
                        # A client connected before the server was closed:
                        # drop the client (close the pipe) na exit
                        pipe.close()
                        rudisha

                    protocol = protocol_factory()
                    self._make_duplex_pipe_transport(
                        pipe, protocol, extra={'addr': address})

                pipe = server._get_unconnected_pipe()
                ikiwa pipe ni Tupu:
                    rudisha

                f = self._proactor.accept_pipe(pipe)
            tatizo OSError kama exc:
                ikiwa pipe na pipe.fileno() != -1:
                    self.call_exception_handler({
                        'message': 'Pipe accept failed',
                        'exception': exc,
                        'pipe': pipe,
                    })
                    pipe.close()
                lasivyo self._debug:
                    logger.warning("Accept pipe failed on pipe %r",
                                   pipe, exc_info=Kweli)
            tatizo exceptions.CancelledError:
                ikiwa pipe:
                    pipe.close()
            isipokua:
                server._accept_pipe_future = f
                f.add_done_callback(loop_accept_pipe)

        self.call_soon(loop_accept_pipe)
        rudisha [server]

    async eleza _make_subprocess_transport(self, protocol, args, shell,
                                         stdin, stdout, stderr, bufsize,
                                         extra=Tupu, **kwargs):
        waiter = self.create_future()
        transp = _WindowsSubprocessTransport(self, protocol, args, shell,
                                             stdin, stdout, stderr, bufsize,
                                             waiter=waiter, extra=extra,
                                             **kwargs)
        jaribu:
            await waiter
        tatizo (SystemExit, KeyboardInterrupt):
            raise
        tatizo BaseException:
            transp.close()
            await transp._wait()
            raise

        rudisha transp


kundi IocpProactor:
    """Proactor implementation using IOCP."""

    eleza __init__(self, concurrency=0xffffffff):
        self._loop = Tupu
        self._results = []
        self._iocp = _overlapped.CreateIoCompletionPort(
            _overlapped.INVALID_HANDLE_VALUE, NULL, 0, concurrency)
        self._cache = {}
        self._registered = weakref.WeakSet()
        self._unregistered = []
        self._stopped_serving = weakref.WeakSet()

    eleza _check_closed(self):
        ikiwa self._iocp ni Tupu:
            ashiria RuntimeError('IocpProactor ni closed')

    eleza __repr__(self):
        info = ['overlapped#=%s' % len(self._cache),
                'result#=%s' % len(self._results)]
        ikiwa self._iocp ni Tupu:
            info.append('closed')
        rudisha '<%s %s>' % (self.__class__.__name__, " ".join(info))

    eleza set_loop(self, loop):
        self._loop = loop

    eleza select(self, timeout=Tupu):
        ikiwa sio self._results:
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
        jaribu:
            ikiwa isinstance(conn, socket.socket):
                ov.WSARecv(conn.fileno(), nbytes, flags)
            isipokua:
                ov.ReadFile(conn.fileno(), nbytes)
        tatizo BrokenPipeError:
            rudisha self._result(b'')

        eleza finish_recv(trans, key, ov):
            jaribu:
                rudisha ov.getresult()
            tatizo OSError kama exc:
                ikiwa exc.winerror kwenye (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    ashiria ConnectionResetError(*exc.args)
                isipokua:
                    raise

        rudisha self._register(ov, conn, finish_recv)

    eleza recv_into(self, conn, buf, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        jaribu:
            ikiwa isinstance(conn, socket.socket):
                ov.WSARecvInto(conn.fileno(), buf, flags)
            isipokua:
                ov.ReadFileInto(conn.fileno(), buf)
        tatizo BrokenPipeError:
            rudisha self._result(b'')

        eleza finish_recv(trans, key, ov):
            jaribu:
                rudisha ov.getresult()
            tatizo OSError kama exc:
                ikiwa exc.winerror kwenye (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    ashiria ConnectionResetError(*exc.args)
                isipokua:
                    raise

        rudisha self._register(ov, conn, finish_recv)

    eleza recvfrom(self, conn, nbytes, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        jaribu:
            ov.WSARecvFrom(conn.fileno(), nbytes, flags)
        tatizo BrokenPipeError:
            rudisha self._result((b'', Tupu))

        eleza finish_recv(trans, key, ov):
            jaribu:
                rudisha ov.getresult()
            tatizo OSError kama exc:
                ikiwa exc.winerror kwenye (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    ashiria ConnectionResetError(*exc.args)
                isipokua:
                    raise

        rudisha self._register(ov, conn, finish_recv)

    eleza sendto(self, conn, buf, flags=0, addr=Tupu):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)

        ov.WSASendTo(conn.fileno(), buf, flags, addr)

        eleza finish_send(trans, key, ov):
            jaribu:
                rudisha ov.getresult()
            tatizo OSError kama exc:
                ikiwa exc.winerror kwenye (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    ashiria ConnectionResetError(*exc.args)
                isipokua:
                    raise

        rudisha self._register(ov, conn, finish_send)

    eleza send(self, conn, buf, flags=0):
        self._register_with_iocp(conn)
        ov = _overlapped.Overlapped(NULL)
        ikiwa isinstance(conn, socket.socket):
            ov.WSASend(conn.fileno(), buf, flags)
        isipokua:
            ov.WriteFile(conn.fileno(), buf)

        eleza finish_send(trans, key, ov):
            jaribu:
                rudisha ov.getresult()
            tatizo OSError kama exc:
                ikiwa exc.winerror kwenye (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    ashiria ConnectionResetError(*exc.args)
                isipokua:
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
            # Coroutine closing the accept socket ikiwa the future ni cancelled
            jaribu:
                await future
            tatizo exceptions.CancelledError:
                conn.close()
                raise

        future = self._register(ov, listener, finish_accept)
        coro = accept_coro(future, conn)
        tasks.ensure_future(coro, loop=self._loop)
        rudisha future

    eleza connect(self, conn, address):
        ikiwa conn.type == socket.SOCK_DGRAM:
            # WSAConnect will complete immediately kila UDP sockets so we don't
            # need to register any IOCP operation
            _overlapped.WSAConnect(conn.fileno(), address)
            fut = self._loop.create_future()
            fut.set_result(Tupu)
            rudisha fut

        self._register_with_iocp(conn)
        # The socket needs to be locally bound before we call ConnectEx().
        jaribu:
            _overlapped.BindLocal(conn.fileno(), conn.family)
        tatizo OSError kama e:
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
            jaribu:
                rudisha ov.getresult()
            tatizo OSError kama exc:
                ikiwa exc.winerror kwenye (_overlapped.ERROR_NETNAME_DELETED,
                                    _overlapped.ERROR_OPERATION_ABORTED):
                    ashiria ConnectionResetError(*exc.args)
                isipokua:
                    raise
        rudisha self._register(ov, sock, finish_sendfile)

    eleza accept_pipe(self, pipe):
        self._register_with_iocp(pipe)
        ov = _overlapped.Overlapped(NULL)
        connected = ov.ConnectNamedPipe(pipe.fileno())

        ikiwa connected:
            # ConnectNamePipe() failed ukijumuisha ERROR_PIPE_CONNECTED which means
            # that the pipe ni connected. There ni no need to wait kila the
            # completion of the connection.
            rudisha self._result(pipe)

        eleza finish_accept_pipe(trans, key, ov):
            ov.getresult()
            rudisha pipe

        rudisha self._register(ov, pipe, finish_accept_pipe)

    async eleza connect_pipe(self, address):
        delay = CONNECT_PIPE_INIT_DELAY
        wakati Kweli:
            # Unfortunately there ni no way to do an overlapped connect to
            # a pipe.  Call CreateFile() kwenye a loop until it doesn't fail with
            # ERROR_PIPE_BUSY.
            jaribu:
                handle = _overlapped.ConnectPipe(address)
                koma
            tatizo OSError kama exc:
                ikiwa exc.winerror != _overlapped.ERROR_PIPE_BUSY:
                    raise

            # ConnectPipe() failed ukijumuisha ERROR_PIPE_BUSY: retry later
            delay = min(delay * 2, CONNECT_PIPE_MAX_DELAY)
            await tasks.sleep(delay)

        rudisha windows_utils.PipeHandle(handle)

    eleza wait_for_handle(self, handle, timeout=Tupu):
        """Wait kila a handle.

        Return a Future object. The result of the future ni Kweli ikiwa the wait
        completed, ama Uongo ikiwa the wait did sio complete (on timeout).
        """
        rudisha self._wait_for_handle(handle, timeout, Uongo)

    eleza _wait_cancel(self, event, done_callback):
        fut = self._wait_for_handle(event, Tupu, Kweli)
        # add_done_callback() cannot be used because the wait may only complete
        # kwenye IocpProactor.close(), wakati the event loop ni sio running.
        fut._done_callback = done_callback
        rudisha fut

    eleza _wait_for_handle(self, handle, timeout, _is_cancel):
        self._check_closed()

        ikiwa timeout ni Tupu:
            ms = _winapi.INFINITE
        isipokua:
            # RegisterWaitForSingleObject() has a resolution of 1 millisecond,
            # round away kutoka zero to wait *at least* timeout seconds.
            ms = math.ceil(timeout * 1e3)

        # We only create ov so we can use ov.address kama a key kila the cache.
        ov = _overlapped.Overlapped(NULL)
        wait_handle = _overlapped.RegisterWaitWithQueue(
            handle, self._iocp, ov.address, ms)
        ikiwa _is_cancel:
            f = _WaitCancelFuture(ov, handle, wait_handle, loop=self._loop)
        isipokua:
            f = _WaitHandleFuture(ov, handle, wait_handle, self,
                                  loop=self._loop)
        ikiwa f._source_traceback:
            toa f._source_traceback[-1]

        eleza finish_wait_for_handle(trans, key, ov):
            # Note that this second wait means that we should only use
            # this ukijumuisha handles types where a successful wait has no
            # effect.  So events ama processes are all right, but locks
            # ama semaphores are not.  Also note ikiwa the handle is
            # signalled na then quickly reset, then we may rudisha
            # Uongo even though we have sio timed out.
            rudisha f._poll()

        self._cache[ov.address] = (f, ov, 0, finish_wait_for_handle)
        rudisha f

    eleza _register_with_iocp(self, obj):
        # To get notifications of finished ops on this objects sent to the
        # completion port, were must register the handle.
        ikiwa obj haiko kwenye self._registered:
            self._registered.add(obj)
            _overlapped.CreateIoCompletionPort(obj.fileno(), self._iocp, 0, 0)
            # XXX We could also use SetFileCompletionNotificationModes()
            # to avoid sending notifications to completion port of ops
            # that succeed immediately.

    eleza _register(self, ov, obj, callback):
        self._check_closed()

        # Return a future which will be set ukijumuisha the result of the
        # operation when it completes.  The future's value ni actually
        # the value returned by callback().
        f = _OverlappedFuture(ov, loop=self._loop)
        ikiwa f._source_traceback:
            toa f._source_traceback[-1]
        ikiwa sio ov.pending:
            # The operation has completed, so no need to postpone the
            # work.  We cannot take this short cut ikiwa we need the
            # NumberOfBytes, CompletionKey values returned by
            # PostQueuedCompletionStatus().
            jaribu:
                value = callback(Tupu, Tupu, ov)
            tatizo OSError kama e:
                f.set_exception(e)
            isipokua:
                f.set_result(value)
            # Even ikiwa GetOverlappedResult() was called, we have to wait kila the
            # notification of the completion kwenye GetQueuedCompletionStatus().
            # Register the overlapped operation to keep a reference to the
            # OVERLAPPED object, otherwise the memory ni freed na Windows may
            # read uninitialized memory.

        # Register the overlapped operation kila later.  Note that
        # we only store obj to prevent it kutoka being garbage
        # collected too early.
        self._cache[ov.address] = (f, ov, obj, callback)
        rudisha f

    eleza _unregister(self, ov):
        """Unregister an overlapped object.

        Call this method when its future has been cancelled. The event can
        already be signalled (pending kwenye the proactor event queue). It ni also
        safe ikiwa the event ni never signalled (because it was cancelled).
        """
        self._check_closed()
        self._unregistered.append(ov)

    eleza _get_accept_socket(self, family):
        s = socket.socket(family)
        s.settimeout(0)
        rudisha s

    eleza _poll(self, timeout=Tupu):
        ikiwa timeout ni Tupu:
            ms = INFINITE
        lasivyo timeout < 0:
            ashiria ValueError("negative timeout")
        isipokua:
            # GetQueuedCompletionStatus() has a resolution of 1 millisecond,
            # round away kutoka zero to wait *at least* timeout seconds.
            ms = math.ceil(timeout * 1e3)
            ikiwa ms >= INFINITE:
                ashiria ValueError("timeout too big")

        wakati Kweli:
            status = _overlapped.GetQueuedCompletionStatus(self._iocp, ms)
            ikiwa status ni Tupu:
                koma
            ms = 0

            err, transferred, key, address = status
            jaribu:
                f, ov, obj, callback = self._cache.pop(address)
            tatizo KeyError:
                ikiwa self._loop.get_debug():
                    self._loop.call_exception_handler({
                        'message': ('GetQueuedCompletionStatus() returned an '
                                    'unexpected event'),
                        'status': ('err=%s transferred=%s key=%#x address=%#x'
                                   % (err, transferred, key, address)),
                    })

                # key ni either zero, ama it ni used to rudisha a pipe
                # handle which should be closed to avoid a leak.
                ikiwa key haiko kwenye (0, _overlapped.INVALID_HANDLE_VALUE):
                    _winapi.CloseHandle(key)
                endelea

            ikiwa obj kwenye self._stopped_serving:
                f.cancel()
            # Don't call the callback ikiwa _register() already read the result ama
            # ikiwa the overlapped has been cancelled
            lasivyo sio f.done():
                jaribu:
                    value = callback(transferred, key, ov)
                tatizo OSError kama e:
                    f.set_exception(e)
                    self._results.append(f)
                isipokua:
                    f.set_result(value)
                    self._results.append(f)

        # Remove unregistered futures
        kila ov kwenye self._unregistered:
            self._cache.pop(ov.address, Tupu)
        self._unregistered.clear()

    eleza _stop_serving(self, obj):
        # obj ni a socket ama pipe handle.  It will be closed in
        # BaseProactorEventLoop._stop_serving() which will make any
        # pending operations fail quickly.
        self._stopped_serving.add(obj)

    eleza close(self):
        ikiwa self._iocp ni Tupu:
            # already closed
            rudisha

        # Cancel remaining registered operations.
        kila address, (fut, ov, obj, callback) kwenye list(self._cache.items()):
            ikiwa fut.cancelled():
                # Nothing to do ukijumuisha cancelled futures
                pita
            lasivyo isinstance(fut, _WaitCancelFuture):
                # _WaitCancelFuture must sio be cancelled
                pita
            isipokua:
                jaribu:
                    fut.cancel()
                tatizo OSError kama exc:
                    ikiwa self._loop ni sio Tupu:
                        context = {
                            'message': 'Cancelling a future failed',
                            'exception': exc,
                            'future': fut,
                        }
                        ikiwa fut._source_traceback:
                            context['source_traceback'] = fut._source_traceback
                        self._loop.call_exception_handler(context)

        # Wait until all cancelled overlapped complete: don't exit ukijumuisha running
        # overlapped to prevent a crash. Display progress every second ikiwa the
        # loop ni still running.
        msg_update = 1.0
        start_time = time.monotonic()
        next_msg = start_time + msg_update
        wakati self._cache:
            ikiwa next_msg <= time.monotonic():
                logger.debug('%r ni running after closing kila %.1f seconds',
                             self, time.monotonic() - start_time)
                next_msg = time.monotonic() + msg_update

            # handle a few events, ama timeout
            self._poll(msg_update)

        self._results = []

        _winapi.CloseHandle(self._iocp)
        self._iocp = Tupu

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
