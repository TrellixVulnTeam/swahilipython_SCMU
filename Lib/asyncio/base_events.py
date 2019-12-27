"""Base implementation of event loop.

The event loop can be broken up into a multiplexer (the part
responsible for notifying us of I/O events) and the event loop proper,
which wraps a multiplexer with functionality for scheduling callbacks,
immediately or at a given time in the future.

Whenever a public API takes a callback, subsequent positional
arguments will be passed to the callback if/when it is called.  This
avoids the proliferation of trivial lambdas implementing closures.
Keyword arguments for the callback are not supported; this is a
conscious design decision, leaving the door open for keyword arguments
to modify the meaning of the API call itself.
"""

agiza collections
agiza collections.abc
agiza concurrent.futures
agiza functools
agiza heapq
agiza itertools
agiza os
agiza socket
agiza stat
agiza subprocess
agiza threading
agiza time
agiza traceback
agiza sys
agiza warnings
agiza weakref

try:
    agiza ssl
except ImportError:  # pragma: no cover
    ssl = None

kutoka . agiza constants
kutoka . agiza coroutines
kutoka . agiza events
kutoka . agiza exceptions
kutoka . agiza futures
kutoka . agiza protocols
kutoka . agiza sslproto
kutoka . agiza staggered
kutoka . agiza tasks
kutoka . agiza transports
kutoka . agiza trsock
kutoka .log agiza logger


__all__ = 'BaseEventLoop',


# Minimum number of _scheduled timer handles before cleanup of
# cancelled handles is performed.
_MIN_SCHEDULED_TIMER_HANDLES = 100

# Minimum fraction of _scheduled timer handles that are cancelled
# before cleanup of cancelled handles is performed.
_MIN_CANCELLED_TIMER_HANDLES_FRACTION = 0.5


_HAS_IPv6 = hasattr(socket, 'AF_INET6')

# Maximum timeout passed to select to avoid OS limitations
MAXIMUM_SELECT_TIMEOUT = 24 * 3600


eleza _format_handle(handle):
    cb = handle._callback
    ikiwa isinstance(getattr(cb, '__self__', None), tasks.Task):
        # format the task
        rudisha repr(cb.__self__)
    else:
        rudisha str(handle)


eleza _format_pipe(fd):
    ikiwa fd == subprocess.PIPE:
        rudisha '<pipe>'
    elikiwa fd == subprocess.STDOUT:
        rudisha '<stdout>'
    else:
        rudisha repr(fd)


eleza _set_reuseport(sock):
    ikiwa not hasattr(socket, 'SO_REUSEPORT'):
        raise ValueError('reuse_port not supported by socket module')
    else:
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            raise ValueError('reuse_port not supported by socket module, '
                             'SO_REUSEPORT defined but not implemented.')


eleza _ipaddr_info(host, port, family, type, proto, flowinfo=0, scopeid=0):
    # Try to skip getaddrinfo ikiwa "host" is already an IP. Users might have
    # handled name resolution in their own code and pass in resolved IPs.
    ikiwa not hasattr(socket, 'inet_pton'):
        return

    ikiwa proto not in {0, socket.IPPROTO_TCP, socket.IPPROTO_UDP} or \
            host is None:
        rudisha None

    ikiwa type == socket.SOCK_STREAM:
        proto = socket.IPPROTO_TCP
    elikiwa type == socket.SOCK_DGRAM:
        proto = socket.IPPROTO_UDP
    else:
        rudisha None

    ikiwa port is None:
        port = 0
    elikiwa isinstance(port, bytes) and port == b'':
        port = 0
    elikiwa isinstance(port, str) and port == '':
        port = 0
    else:
        # If port's a service name like "http", don't skip getaddrinfo.
        try:
            port = int(port)
        except (TypeError, ValueError):
            rudisha None

    ikiwa family == socket.AF_UNSPEC:
        afs = [socket.AF_INET]
        ikiwa _HAS_IPv6:
            afs.append(socket.AF_INET6)
    else:
        afs = [family]

    ikiwa isinstance(host, bytes):
        host = host.decode('idna')
    ikiwa '%' in host:
        # Linux's inet_pton doesn't accept an IPv6 zone index after host,
        # like '::1%lo0'.
        rudisha None

    for af in afs:
        try:
            socket.inet_pton(af, host)
            # The host has already been resolved.
            ikiwa _HAS_IPv6 and af == socket.AF_INET6:
                rudisha af, type, proto, '', (host, port, flowinfo, scopeid)
            else:
                rudisha af, type, proto, '', (host, port)
        except OSError:
            pass

    # "host" is not an IP address.
    rudisha None


eleza _interleave_addrinfos(addrinfos, first_address_family_count=1):
    """Interleave list of addrinfo tuples by family."""
    # Group addresses by family
    addrinfos_by_family = collections.OrderedDict()
    for addr in addrinfos:
        family = addr[0]
        ikiwa family not in addrinfos_by_family:
            addrinfos_by_family[family] = []
        addrinfos_by_family[family].append(addr)
    addrinfos_lists = list(addrinfos_by_family.values())

    reordered = []
    ikiwa first_address_family_count > 1:
        reordered.extend(addrinfos_lists[0][:first_address_family_count - 1])
        del addrinfos_lists[0][:first_address_family_count - 1]
    reordered.extend(
        a for a in itertools.chain.kutoka_iterable(
            itertools.zip_longest(*addrinfos_lists)
        ) ikiwa a is not None)
    rudisha reordered


eleza _run_until_complete_cb(fut):
    ikiwa not fut.cancelled():
        exc = fut.exception()
        ikiwa isinstance(exc, (SystemExit, KeyboardInterrupt)):
            # Issue #22429: run_forever() already finished, no need to
            # stop it.
            return
    futures._get_loop(fut).stop()


ikiwa hasattr(socket, 'TCP_NODELAY'):
    eleza _set_nodelay(sock):
        ikiwa (sock.family in {socket.AF_INET, socket.AF_INET6} and
                sock.type == socket.SOCK_STREAM and
                sock.proto == socket.IPPROTO_TCP):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
else:
    eleza _set_nodelay(sock):
        pass


kundi _SendfileFallbackProtocol(protocols.Protocol):
    eleza __init__(self, transp):
        ikiwa not isinstance(transp, transports._FlowControlMixin):
            raise TypeError("transport should be _FlowControlMixin instance")
        self._transport = transp
        self._proto = transp.get_protocol()
        self._should_resume_reading = transp.is_reading()
        self._should_resume_writing = transp._protocol_paused
        transp.pause_reading()
        transp.set_protocol(self)
        ikiwa self._should_resume_writing:
            self._write_ready_fut = self._transport._loop.create_future()
        else:
            self._write_ready_fut = None

    async eleza drain(self):
        ikiwa self._transport.is_closing():
            raise ConnectionError("Connection closed by peer")
        fut = self._write_ready_fut
        ikiwa fut is None:
            return
        await fut

    eleza connection_made(self, transport):
        raise RuntimeError("Invalid state: "
                           "connection should have been established already.")

    eleza connection_lost(self, exc):
        ikiwa self._write_ready_fut is not None:
            # Never happens ikiwa peer disconnects after sending the whole content
            # Thus disconnection is always an exception kutoka user perspective
            ikiwa exc is None:
                self._write_ready_fut.set_exception(
                    ConnectionError("Connection is closed by peer"))
            else:
                self._write_ready_fut.set_exception(exc)
        self._proto.connection_lost(exc)

    eleza pause_writing(self):
        ikiwa self._write_ready_fut is not None:
            return
        self._write_ready_fut = self._transport._loop.create_future()

    eleza resume_writing(self):
        ikiwa self._write_ready_fut is None:
            return
        self._write_ready_fut.set_result(False)
        self._write_ready_fut = None

    eleza data_received(self, data):
        raise RuntimeError("Invalid state: reading should be paused")

    eleza eof_received(self):
        raise RuntimeError("Invalid state: reading should be paused")

    async eleza restore(self):
        self._transport.set_protocol(self._proto)
        ikiwa self._should_resume_reading:
            self._transport.resume_reading()
        ikiwa self._write_ready_fut is not None:
            # Cancel the future.
            # Basically it has no effect because protocol is switched back,
            # no code should wait for it anymore.
            self._write_ready_fut.cancel()
        ikiwa self._should_resume_writing:
            self._proto.resume_writing()


kundi Server(events.AbstractServer):

    eleza __init__(self, loop, sockets, protocol_factory, ssl_context, backlog,
                 ssl_handshake_timeout):
        self._loop = loop
        self._sockets = sockets
        self._active_count = 0
        self._waiters = []
        self._protocol_factory = protocol_factory
        self._backlog = backlog
        self._ssl_context = ssl_context
        self._ssl_handshake_timeout = ssl_handshake_timeout
        self._serving = False
        self._serving_forever_fut = None

    eleza __repr__(self):
        rudisha f'<{self.__class__.__name__} sockets={self.sockets!r}>'

    eleza _attach(self):
        assert self._sockets is not None
        self._active_count += 1

    eleza _detach(self):
        assert self._active_count > 0
        self._active_count -= 1
        ikiwa self._active_count == 0 and self._sockets is None:
            self._wakeup()

    eleza _wakeup(self):
        waiters = self._waiters
        self._waiters = None
        for waiter in waiters:
            ikiwa not waiter.done():
                waiter.set_result(waiter)

    eleza _start_serving(self):
        ikiwa self._serving:
            return
        self._serving = True
        for sock in self._sockets:
            sock.listen(self._backlog)
            self._loop._start_serving(
                self._protocol_factory, sock, self._ssl_context,
                self, self._backlog, self._ssl_handshake_timeout)

    eleza get_loop(self):
        rudisha self._loop

    eleza is_serving(self):
        rudisha self._serving

    @property
    eleza sockets(self):
        ikiwa self._sockets is None:
            rudisha ()
        rudisha tuple(trsock.TransportSocket(s) for s in self._sockets)

    eleza close(self):
        sockets = self._sockets
        ikiwa sockets is None:
            return
        self._sockets = None

        for sock in sockets:
            self._loop._stop_serving(sock)

        self._serving = False

        ikiwa (self._serving_forever_fut is not None and
                not self._serving_forever_fut.done()):
            self._serving_forever_fut.cancel()
            self._serving_forever_fut = None

        ikiwa self._active_count == 0:
            self._wakeup()

    async eleza start_serving(self):
        self._start_serving()
        # Skip one loop iteration so that all 'loop.add_reader'
        # go through.
        await tasks.sleep(0, loop=self._loop)

    async eleza serve_forever(self):
        ikiwa self._serving_forever_fut is not None:
            raise RuntimeError(
                f'server {self!r} is already being awaited on serve_forever()')
        ikiwa self._sockets is None:
            raise RuntimeError(f'server {self!r} is closed')

        self._start_serving()
        self._serving_forever_fut = self._loop.create_future()

        try:
            await self._serving_forever_fut
        except exceptions.CancelledError:
            try:
                self.close()
                await self.wait_closed()
            finally:
                raise
        finally:
            self._serving_forever_fut = None

    async eleza wait_closed(self):
        ikiwa self._sockets is None or self._waiters is None:
            return
        waiter = self._loop.create_future()
        self._waiters.append(waiter)
        await waiter


kundi BaseEventLoop(events.AbstractEventLoop):

    eleza __init__(self):
        self._timer_cancelled_count = 0
        self._closed = False
        self._stopping = False
        self._ready = collections.deque()
        self._scheduled = []
        self._default_executor = None
        self._internal_fds = 0
        # Identifier of the thread running the event loop, or None ikiwa the
        # event loop is not running
        self._thread_id = None
        self._clock_resolution = time.get_clock_info('monotonic').resolution
        self._exception_handler = None
        self.set_debug(coroutines._is_debug_mode())
        # In debug mode, ikiwa the execution of a callback or a step of a task
        # exceed this duration in seconds, the slow callback/task is logged.
        self.slow_callback_duration = 0.1
        self._current_handle = None
        self._task_factory = None
        self._coroutine_origin_tracking_enabled = False
        self._coroutine_origin_tracking_saved_depth = None

        # A weak set of all asynchronous generators that are
        # being iterated by the loop.
        self._asyncgens = weakref.WeakSet()
        # Set to True when `loop.shutdown_asyncgens` is called.
        self._asyncgens_shutdown_called = False

    eleza __repr__(self):
        rudisha (
            f'<{self.__class__.__name__} running={self.is_running()} '
            f'closed={self.is_closed()} debug={self.get_debug()}>'
        )

    eleza create_future(self):
        """Create a Future object attached to the loop."""
        rudisha futures.Future(loop=self)

    eleza create_task(self, coro, *, name=None):
        """Schedule a coroutine object.

        Return a task object.
        """
        self._check_closed()
        ikiwa self._task_factory is None:
            task = tasks.Task(coro, loop=self, name=name)
            ikiwa task._source_traceback:
                del task._source_traceback[-1]
        else:
            task = self._task_factory(self, coro)
            tasks._set_task_name(task, name)

        rudisha task

    eleza set_task_factory(self, factory):
        """Set a task factory that will be used by loop.create_task().

        If factory is None the default task factory will be set.

        If factory is a callable, it should have a signature matching
        '(loop, coro)', where 'loop' will be a reference to the active
        event loop, 'coro' will be a coroutine object.  The callable
        must rudisha a Future.
        """
        ikiwa factory is not None and not callable(factory):
            raise TypeError('task factory must be a callable or None')
        self._task_factory = factory

    eleza get_task_factory(self):
        """Return a task factory, or None ikiwa the default one is in use."""
        rudisha self._task_factory

    eleza _make_socket_transport(self, sock, protocol, waiter=None, *,
                               extra=None, server=None):
        """Create socket transport."""
        raise NotImplementedError

    eleza _make_ssl_transport(
            self, rawsock, protocol, sslcontext, waiter=None,
            *, server_side=False, server_hostname=None,
            extra=None, server=None,
            ssl_handshake_timeout=None,
            call_connection_made=True):
        """Create SSL transport."""
        raise NotImplementedError

    eleza _make_datagram_transport(self, sock, protocol,
                                 address=None, waiter=None, extra=None):
        """Create datagram transport."""
        raise NotImplementedError

    eleza _make_read_pipe_transport(self, pipe, protocol, waiter=None,
                                  extra=None):
        """Create read pipe transport."""
        raise NotImplementedError

    eleza _make_write_pipe_transport(self, pipe, protocol, waiter=None,
                                   extra=None):
        """Create write pipe transport."""
        raise NotImplementedError

    async eleza _make_subprocess_transport(self, protocol, args, shell,
                                         stdin, stdout, stderr, bufsize,
                                         extra=None, **kwargs):
        """Create subprocess transport."""
        raise NotImplementedError

    eleza _write_to_self(self):
        """Write a byte to self-pipe, to wake up the event loop.

        This may be called kutoka a different thread.

        The subkundi is responsible for implementing the self-pipe.
        """
        raise NotImplementedError

    eleza _process_events(self, event_list):
        """Process selector events."""
        raise NotImplementedError

    eleza _check_closed(self):
        ikiwa self._closed:
            raise RuntimeError('Event loop is closed')

    eleza _asyncgen_finalizer_hook(self, agen):
        self._asyncgens.discard(agen)
        ikiwa not self.is_closed():
            self.call_soon_threadsafe(self.create_task, agen.aclose())

    eleza _asyncgen_firstiter_hook(self, agen):
        ikiwa self._asyncgens_shutdown_called:
            warnings.warn(
                f"asynchronous generator {agen!r} was scheduled after "
                f"loop.shutdown_asyncgens() call",
                ResourceWarning, source=self)

        self._asyncgens.add(agen)

    async eleza shutdown_asyncgens(self):
        """Shutdown all active asynchronous generators."""
        self._asyncgens_shutdown_called = True

        ikiwa not len(self._asyncgens):
            # If Python version is <3.6 or we don't have any asynchronous
            # generators alive.
            return

        closing_agens = list(self._asyncgens)
        self._asyncgens.clear()

        results = await tasks.gather(
            *[ag.aclose() for ag in closing_agens],
            return_exceptions=True,
            loop=self)

        for result, agen in zip(results, closing_agens):
            ikiwa isinstance(result, Exception):
                self.call_exception_handler({
                    'message': f'an error occurred during closing of '
                               f'asynchronous generator {agen!r}',
                    'exception': result,
                    'asyncgen': agen
                })

    eleza run_forever(self):
        """Run until stop() is called."""
        self._check_closed()
        ikiwa self.is_running():
            raise RuntimeError('This event loop is already running')
        ikiwa events._get_running_loop() is not None:
            raise RuntimeError(
                'Cannot run the event loop while another loop is running')
        self._set_coroutine_origin_tracking(self._debug)
        self._thread_id = threading.get_ident()

        old_agen_hooks = sys.get_asyncgen_hooks()
        sys.set_asyncgen_hooks(firstiter=self._asyncgen_firstiter_hook,
                               finalizer=self._asyncgen_finalizer_hook)
        try:
            events._set_running_loop(self)
            while True:
                self._run_once()
                ikiwa self._stopping:
                    break
        finally:
            self._stopping = False
            self._thread_id = None
            events._set_running_loop(None)
            self._set_coroutine_origin_tracking(False)
            sys.set_asyncgen_hooks(*old_agen_hooks)

    eleza run_until_complete(self, future):
        """Run until the Future is done.

        If the argument is a coroutine, it is wrapped in a Task.

        WARNING: It would be disastrous to call run_until_complete()
        with the same coroutine twice -- it would wrap it in two
        different Tasks and that can't be good.

        Return the Future's result, or raise its exception.
        """
        self._check_closed()

        new_task = not futures.isfuture(future)
        future = tasks.ensure_future(future, loop=self)
        ikiwa new_task:
            # An exception is raised ikiwa the future didn't complete, so there
            # is no need to log the "destroy pending task" message
            future._log_destroy_pending = False

        future.add_done_callback(_run_until_complete_cb)
        try:
            self.run_forever()
        except:
            ikiwa new_task and future.done() and not future.cancelled():
                # The coroutine raised a BaseException. Consume the exception
                # to not log a warning, the caller doesn't have access to the
                # local task.
                future.exception()
            raise
        finally:
            future.remove_done_callback(_run_until_complete_cb)
        ikiwa not future.done():
            raise RuntimeError('Event loop stopped before Future completed.')

        rudisha future.result()

    eleza stop(self):
        """Stop running the event loop.

        Every callback already scheduled will still run.  This simply informs
        run_forever to stop looping after a complete iteration.
        """
        self._stopping = True

    eleza close(self):
        """Close the event loop.

        This clears the queues and shuts down the executor,
        but does not wait for the executor to finish.

        The event loop must not be running.
        """
        ikiwa self.is_running():
            raise RuntimeError("Cannot close a running event loop")
        ikiwa self._closed:
            return
        ikiwa self._debug:
            logger.debug("Close %r", self)
        self._closed = True
        self._ready.clear()
        self._scheduled.clear()
        executor = self._default_executor
        ikiwa executor is not None:
            self._default_executor = None
            executor.shutdown(wait=False)

    eleza is_closed(self):
        """Returns True ikiwa the event loop was closed."""
        rudisha self._closed

    eleza __del__(self, _warn=warnings.warn):
        ikiwa not self.is_closed():
            _warn(f"unclosed event loop {self!r}", ResourceWarning, source=self)
            ikiwa not self.is_running():
                self.close()

    eleza is_running(self):
        """Returns True ikiwa the event loop is running."""
        rudisha (self._thread_id is not None)

    eleza time(self):
        """Return the time according to the event loop's clock.

        This is a float expressed in seconds since an epoch, but the
        epoch, precision, accuracy and drift are unspecified and may
        differ per event loop.
        """
        rudisha time.monotonic()

    eleza call_later(self, delay, callback, *args, context=None):
        """Arrange for a callback to be called at a given time.

        Return a Handle: an opaque object with a cancel() method that
        can be used to cancel the call.

        The delay can be an int or float, expressed in seconds.  It is
        always relative to the current time.

        Each callback will be called exactly once.  If two callbacks
        are scheduled for exactly the same time, it undefined which
        will be called first.

        Any positional arguments after the callback will be passed to
        the callback when it is called.
        """
        timer = self.call_at(self.time() + delay, callback, *args,
                             context=context)
        ikiwa timer._source_traceback:
            del timer._source_traceback[-1]
        rudisha timer

    eleza call_at(self, when, callback, *args, context=None):
        """Like call_later(), but uses an absolute time.

        Absolute time corresponds to the event loop's time() method.
        """
        self._check_closed()
        ikiwa self._debug:
            self._check_thread()
            self._check_callback(callback, 'call_at')
        timer = events.TimerHandle(when, callback, args, self, context)
        ikiwa timer._source_traceback:
            del timer._source_traceback[-1]
        heapq.heappush(self._scheduled, timer)
        timer._scheduled = True
        rudisha timer

    eleza call_soon(self, callback, *args, context=None):
        """Arrange for a callback to be called as soon as possible.

        This operates as a FIFO queue: callbacks are called in the
        order in which they are registered.  Each callback will be
        called exactly once.

        Any positional arguments after the callback will be passed to
        the callback when it is called.
        """
        self._check_closed()
        ikiwa self._debug:
            self._check_thread()
            self._check_callback(callback, 'call_soon')
        handle = self._call_soon(callback, args, context)
        ikiwa handle._source_traceback:
            del handle._source_traceback[-1]
        rudisha handle

    eleza _check_callback(self, callback, method):
        ikiwa (coroutines.iscoroutine(callback) or
                coroutines.iscoroutinefunction(callback)):
            raise TypeError(
                f"coroutines cannot be used with {method}()")
        ikiwa not callable(callback):
            raise TypeError(
                f'a callable object was expected by {method}(), '
                f'got {callback!r}')

    eleza _call_soon(self, callback, args, context):
        handle = events.Handle(callback, args, self, context)
        ikiwa handle._source_traceback:
            del handle._source_traceback[-1]
        self._ready.append(handle)
        rudisha handle

    eleza _check_thread(self):
        """Check that the current thread is the thread running the event loop.

        Non-thread-safe methods of this kundi make this assumption and will
        likely behave incorrectly when the assumption is violated.

        Should only be called when (self._debug == True).  The caller is
        responsible for checking this condition for performance reasons.
        """
        ikiwa self._thread_id is None:
            return
        thread_id = threading.get_ident()
        ikiwa thread_id != self._thread_id:
            raise RuntimeError(
                "Non-thread-safe operation invoked on an event loop other "
                "than the current one")

    eleza call_soon_threadsafe(self, callback, *args, context=None):
        """Like call_soon(), but thread-safe."""
        self._check_closed()
        ikiwa self._debug:
            self._check_callback(callback, 'call_soon_threadsafe')
        handle = self._call_soon(callback, args, context)
        ikiwa handle._source_traceback:
            del handle._source_traceback[-1]
        self._write_to_self()
        rudisha handle

    eleza run_in_executor(self, executor, func, *args):
        self._check_closed()
        ikiwa self._debug:
            self._check_callback(func, 'run_in_executor')
        ikiwa executor is None:
            executor = self._default_executor
            ikiwa executor is None:
                executor = concurrent.futures.ThreadPoolExecutor()
                self._default_executor = executor
        rudisha futures.wrap_future(
            executor.submit(func, *args), loop=self)

    eleza set_default_executor(self, executor):
        ikiwa not isinstance(executor, concurrent.futures.ThreadPoolExecutor):
            warnings.warn(
                'Using the default executor that is not an instance of '
                'ThreadPoolExecutor is deprecated and will be prohibited '
                'in Python 3.9',
                DeprecationWarning, 2)
        self._default_executor = executor

    eleza _getaddrinfo_debug(self, host, port, family, type, proto, flags):
        msg = [f"{host}:{port!r}"]
        ikiwa family:
            msg.append(f'family={family!r}')
        ikiwa type:
            msg.append(f'type={type!r}')
        ikiwa proto:
            msg.append(f'proto={proto!r}')
        ikiwa flags:
            msg.append(f'flags={flags!r}')
        msg = ', '.join(msg)
        logger.debug('Get address info %s', msg)

        t0 = self.time()
        addrinfo = socket.getaddrinfo(host, port, family, type, proto, flags)
        dt = self.time() - t0

        msg = f'Getting address info {msg} took {dt * 1e3:.3f}ms: {addrinfo!r}'
        ikiwa dt >= self.slow_callback_duration:
            logger.info(msg)
        else:
            logger.debug(msg)
        rudisha addrinfo

    async eleza getaddrinfo(self, host, port, *,
                          family=0, type=0, proto=0, flags=0):
        ikiwa self._debug:
            getaddr_func = self._getaddrinfo_debug
        else:
            getaddr_func = socket.getaddrinfo

        rudisha await self.run_in_executor(
            None, getaddr_func, host, port, family, type, proto, flags)

    async eleza getnameinfo(self, sockaddr, flags=0):
        rudisha await self.run_in_executor(
            None, socket.getnameinfo, sockaddr, flags)

    async eleza sock_sendfile(self, sock, file, offset=0, count=None,
                            *, fallback=True):
        ikiwa self._debug and sock.gettimeout() != 0:
            raise ValueError("the socket must be non-blocking")
        self._check_sendfile_params(sock, file, offset, count)
        try:
            rudisha await self._sock_sendfile_native(sock, file,
                                                    offset, count)
        except exceptions.SendfileNotAvailableError as exc:
            ikiwa not fallback:
                raise
        rudisha await self._sock_sendfile_fallback(sock, file,
                                                  offset, count)

    async eleza _sock_sendfile_native(self, sock, file, offset, count):
        # NB: sendfile syscall is not supported for SSL sockets and
        # non-mmap files even ikiwa sendfile is supported by OS
        raise exceptions.SendfileNotAvailableError(
            f"syscall sendfile is not available for socket {sock!r} "
            "and file {file!r} combination")

    async eleza _sock_sendfile_fallback(self, sock, file, offset, count):
        ikiwa offset:
            file.seek(offset)
        blocksize = (
            min(count, constants.SENDFILE_FALLBACK_READBUFFER_SIZE)
            ikiwa count else constants.SENDFILE_FALLBACK_READBUFFER_SIZE
        )
        buf = bytearray(blocksize)
        total_sent = 0
        try:
            while True:
                ikiwa count:
                    blocksize = min(count - total_sent, blocksize)
                    ikiwa blocksize <= 0:
                        break
                view = memoryview(buf)[:blocksize]
                read = await self.run_in_executor(None, file.readinto, view)
                ikiwa not read:
                    break  # EOF
                await self.sock_sendall(sock, view[:read])
                total_sent += read
            rudisha total_sent
        finally:
            ikiwa total_sent > 0 and hasattr(file, 'seek'):
                file.seek(offset + total_sent)

    eleza _check_sendfile_params(self, sock, file, offset, count):
        ikiwa 'b' not in getattr(file, 'mode', 'b'):
            raise ValueError("file should be opened in binary mode")
        ikiwa not sock.type == socket.SOCK_STREAM:
            raise ValueError("only SOCK_STREAM type sockets are supported")
        ikiwa count is not None:
            ikiwa not isinstance(count, int):
                raise TypeError(
                    "count must be a positive integer (got {!r})".format(count))
            ikiwa count <= 0:
                raise ValueError(
                    "count must be a positive integer (got {!r})".format(count))
        ikiwa not isinstance(offset, int):
            raise TypeError(
                "offset must be a non-negative integer (got {!r})".format(
                    offset))
        ikiwa offset < 0:
            raise ValueError(
                "offset must be a non-negative integer (got {!r})".format(
                    offset))

    async eleza _connect_sock(self, exceptions, addr_info, local_addr_infos=None):
        """Create, bind and connect one socket."""
        my_exceptions = []
        exceptions.append(my_exceptions)
        family, type_, proto, _, address = addr_info
        sock = None
        try:
            sock = socket.socket(family=family, type=type_, proto=proto)
            sock.setblocking(False)
            ikiwa local_addr_infos is not None:
                for _, _, _, _, laddr in local_addr_infos:
                    try:
                        sock.bind(laddr)
                        break
                    except OSError as exc:
                        msg = (
                            f'error while attempting to bind on '
                            f'address {laddr!r}: '
                            f'{exc.strerror.lower()}'
                        )
                        exc = OSError(exc.errno, msg)
                        my_exceptions.append(exc)
                else:  # all bind attempts failed
                    raise my_exceptions.pop()
            await self.sock_connect(sock, address)
            rudisha sock
        except OSError as exc:
            my_exceptions.append(exc)
            ikiwa sock is not None:
                sock.close()
            raise
        except:
            ikiwa sock is not None:
                sock.close()
            raise

    async eleza create_connection(
            self, protocol_factory, host=None, port=None,
            *, ssl=None, family=0,
            proto=0, flags=0, sock=None,
            local_addr=None, server_hostname=None,
            ssl_handshake_timeout=None,
            happy_eyeballs_delay=None, interleave=None):
        """Connect to a TCP server.

        Create a streaming transport connection to a given Internet host and
        port: socket family AF_INET or socket.AF_INET6 depending on host (or
        family ikiwa specified), socket type SOCK_STREAM. protocol_factory must be
        a callable returning a protocol instance.

        This method is a coroutine which will try to establish the connection
        in the background.  When successful, the coroutine returns a
        (transport, protocol) pair.
        """
        ikiwa server_hostname is not None and not ssl:
            raise ValueError('server_hostname is only meaningful with ssl')

        ikiwa server_hostname is None and ssl:
            # Use host as default for server_hostname.  It is an error
            # ikiwa host is empty or not set, e.g. when an
            # already-connected socket was passed or when only a port
            # is given.  To avoid this error, you can pass
            # server_hostname='' -- this will bypass the hostname
            # check.  (This also means that ikiwa host is a numeric
            # IP/IPv6 address, we will attempt to verify that exact
            # address; this will probably fail, but it is possible to
            # create a certificate for a specific IP address, so we
            # don't judge it here.)
            ikiwa not host:
                raise ValueError('You must set server_hostname '
                                 'when using ssl without a host')
            server_hostname = host

        ikiwa ssl_handshake_timeout is not None and not ssl:
            raise ValueError(
                'ssl_handshake_timeout is only meaningful with ssl')

        ikiwa happy_eyeballs_delay is not None and interleave is None:
            # If using happy eyeballs, default to interleave addresses by family
            interleave = 1

        ikiwa host is not None or port is not None:
            ikiwa sock is not None:
                raise ValueError(
                    'host/port and sock can not be specified at the same time')

            infos = await self._ensure_resolved(
                (host, port), family=family,
                type=socket.SOCK_STREAM, proto=proto, flags=flags, loop=self)
            ikiwa not infos:
                raise OSError('getaddrinfo() returned empty list')

            ikiwa local_addr is not None:
                laddr_infos = await self._ensure_resolved(
                    local_addr, family=family,
                    type=socket.SOCK_STREAM, proto=proto,
                    flags=flags, loop=self)
                ikiwa not laddr_infos:
                    raise OSError('getaddrinfo() returned empty list')
            else:
                laddr_infos = None

            ikiwa interleave:
                infos = _interleave_addrinfos(infos, interleave)

            exceptions = []
            ikiwa happy_eyeballs_delay is None:
                # not using happy eyeballs
                for addrinfo in infos:
                    try:
                        sock = await self._connect_sock(
                            exceptions, addrinfo, laddr_infos)
                        break
                    except OSError:
                        continue
            else:  # using happy eyeballs
                sock, _, _ = await staggered.staggered_race(
                    (functools.partial(self._connect_sock,
                                       exceptions, addrinfo, laddr_infos)
                     for addrinfo in infos),
                    happy_eyeballs_delay, loop=self)

            ikiwa sock is None:
                exceptions = [exc for sub in exceptions for exc in sub]
                ikiwa len(exceptions) == 1:
                    raise exceptions[0]
                else:
                    # If they all have the same str(), raise one.
                    model = str(exceptions[0])
                    ikiwa all(str(exc) == model for exc in exceptions):
                        raise exceptions[0]
                    # Raise a combined exception so the user can see all
                    # the various error messages.
                    raise OSError('Multiple exceptions: {}'.format(
                        ', '.join(str(exc) for exc in exceptions)))

        else:
            ikiwa sock is None:
                raise ValueError(
                    'host and port was not specified and no sock specified')
            ikiwa sock.type != socket.SOCK_STREAM:
                # We allow AF_INET, AF_INET6, AF_UNIX as long as they
                # are SOCK_STREAM.
                # We support passing AF_UNIX sockets even though we have
                # a dedicated API for that: create_unix_connection.
                # Disallowing AF_UNIX in this method, breaks backwards
                # compatibility.
                raise ValueError(
                    f'A Stream Socket was expected, got {sock!r}')

        transport, protocol = await self._create_connection_transport(
            sock, protocol_factory, ssl, server_hostname,
            ssl_handshake_timeout=ssl_handshake_timeout)
        ikiwa self._debug:
            # Get the socket kutoka the transport because SSL transport closes
            # the old socket and creates a new SSL socket
            sock = transport.get_extra_info('socket')
            logger.debug("%r connected to %s:%r: (%r, %r)",
                         sock, host, port, transport, protocol)
        rudisha transport, protocol

    async eleza _create_connection_transport(
            self, sock, protocol_factory, ssl,
            server_hostname, server_side=False,
            ssl_handshake_timeout=None):

        sock.setblocking(False)

        protocol = protocol_factory()
        waiter = self.create_future()
        ikiwa ssl:
            sslcontext = None ikiwa isinstance(ssl, bool) else ssl
            transport = self._make_ssl_transport(
                sock, protocol, sslcontext, waiter,
                server_side=server_side, server_hostname=server_hostname,
                ssl_handshake_timeout=ssl_handshake_timeout)
        else:
            transport = self._make_socket_transport(sock, protocol, waiter)

        try:
            await waiter
        except:
            transport.close()
            raise

        rudisha transport, protocol

    async eleza sendfile(self, transport, file, offset=0, count=None,
                       *, fallback=True):
        """Send a file to transport.

        Return the total number of bytes which were sent.

        The method uses high-performance os.sendfile ikiwa available.

        file must be a regular file object opened in binary mode.

        offset tells kutoka where to start reading the file. If specified,
        count is the total number of bytes to transmit as opposed to
        sending the file until EOF is reached. File position is updated on
        rudisha or also in case of error in which case file.tell()
        can be used to figure out the number of bytes
        which were sent.

        fallback set to True makes asyncio to manually read and send
        the file when the platform does not support the sendfile syscall
        (e.g. Windows or SSL socket on Unix).

        Raise SendfileNotAvailableError ikiwa the system does not support
        sendfile syscall and fallback is False.
        """
        ikiwa transport.is_closing():
            raise RuntimeError("Transport is closing")
        mode = getattr(transport, '_sendfile_compatible',
                       constants._SendfileMode.UNSUPPORTED)
        ikiwa mode is constants._SendfileMode.UNSUPPORTED:
            raise RuntimeError(
                f"sendfile is not supported for transport {transport!r}")
        ikiwa mode is constants._SendfileMode.TRY_NATIVE:
            try:
                rudisha await self._sendfile_native(transport, file,
                                                   offset, count)
            except exceptions.SendfileNotAvailableError as exc:
                ikiwa not fallback:
                    raise

        ikiwa not fallback:
            raise RuntimeError(
                f"fallback is disabled and native sendfile is not "
                f"supported for transport {transport!r}")

        rudisha await self._sendfile_fallback(transport, file,
                                             offset, count)

    async eleza _sendfile_native(self, transp, file, offset, count):
        raise exceptions.SendfileNotAvailableError(
            "sendfile syscall is not supported")

    async eleza _sendfile_fallback(self, transp, file, offset, count):
        ikiwa offset:
            file.seek(offset)
        blocksize = min(count, 16384) ikiwa count else 16384
        buf = bytearray(blocksize)
        total_sent = 0
        proto = _SendfileFallbackProtocol(transp)
        try:
            while True:
                ikiwa count:
                    blocksize = min(count - total_sent, blocksize)
                    ikiwa blocksize <= 0:
                        rudisha total_sent
                view = memoryview(buf)[:blocksize]
                read = await self.run_in_executor(None, file.readinto, view)
                ikiwa not read:
                    rudisha total_sent  # EOF
                await proto.drain()
                transp.write(view[:read])
                total_sent += read
        finally:
            ikiwa total_sent > 0 and hasattr(file, 'seek'):
                file.seek(offset + total_sent)
            await proto.restore()

    async eleza start_tls(self, transport, protocol, sslcontext, *,
                        server_side=False,
                        server_hostname=None,
                        ssl_handshake_timeout=None):
        """Upgrade transport to TLS.

        Return a new transport that *protocol* should start using
        immediately.
        """
        ikiwa ssl is None:
            raise RuntimeError('Python ssl module is not available')

        ikiwa not isinstance(sslcontext, ssl.SSLContext):
            raise TypeError(
                f'sslcontext is expected to be an instance of ssl.SSLContext, '
                f'got {sslcontext!r}')

        ikiwa not getattr(transport, '_start_tls_compatible', False):
            raise TypeError(
                f'transport {transport!r} is not supported by start_tls()')

        waiter = self.create_future()
        ssl_protocol = sslproto.SSLProtocol(
            self, protocol, sslcontext, waiter,
            server_side, server_hostname,
            ssl_handshake_timeout=ssl_handshake_timeout,
            call_connection_made=False)

        # Pause early so that "ssl_protocol.data_received()" doesn't
        # have a chance to get called before "ssl_protocol.connection_made()".
        transport.pause_reading()

        transport.set_protocol(ssl_protocol)
        conmade_cb = self.call_soon(ssl_protocol.connection_made, transport)
        resume_cb = self.call_soon(transport.resume_reading)

        try:
            await waiter
        except BaseException:
            transport.close()
            conmade_cb.cancel()
            resume_cb.cancel()
            raise

        rudisha ssl_protocol._app_transport

    async eleza create_datagram_endpoint(self, protocol_factory,
                                       local_addr=None, remote_addr=None, *,
                                       family=0, proto=0, flags=0,
                                       reuse_address=None, reuse_port=None,
                                       allow_broadcast=None, sock=None):
        """Create datagram connection."""
        ikiwa sock is not None:
            ikiwa sock.type != socket.SOCK_DGRAM:
                raise ValueError(
                    f'A UDP Socket was expected, got {sock!r}')
            ikiwa (local_addr or remote_addr or
                    family or proto or flags or
                    reuse_address or reuse_port or allow_broadcast):
                # show the problematic kwargs in exception msg
                opts = dict(local_addr=local_addr, remote_addr=remote_addr,
                            family=family, proto=proto, flags=flags,
                            reuse_address=reuse_address, reuse_port=reuse_port,
                            allow_broadcast=allow_broadcast)
                problems = ', '.join(f'{k}={v}' for k, v in opts.items() ikiwa v)
                raise ValueError(
                    f'socket modifier keyword arguments can not be used '
                    f'when sock is specified. ({problems})')
            sock.setblocking(False)
            r_addr = None
        else:
            ikiwa not (local_addr or remote_addr):
                ikiwa family == 0:
                    raise ValueError('unexpected address family')
                addr_pairs_info = (((family, proto), (None, None)),)
            elikiwa hasattr(socket, 'AF_UNIX') and family == socket.AF_UNIX:
                for addr in (local_addr, remote_addr):
                    ikiwa addr is not None and not isinstance(addr, str):
                        raise TypeError('string is expected')

                ikiwa local_addr and local_addr[0] not in (0, '\x00'):
                    try:
                        ikiwa stat.S_ISSOCK(os.stat(local_addr).st_mode):
                            os.remove(local_addr)
                    except FileNotFoundError:
                        pass
                    except OSError as err:
                        # Directory may have permissions only to create socket.
                        logger.error('Unable to check or remove stale UNIX '
                                     'socket %r: %r',
                                     local_addr, err)

                addr_pairs_info = (((family, proto),
                                    (local_addr, remote_addr)), )
            else:
                # join address by (family, protocol)
                addr_infos = {}  # Using order preserving dict
                for idx, addr in ((0, local_addr), (1, remote_addr)):
                    ikiwa addr is not None:
                        assert isinstance(addr, tuple) and len(addr) == 2, (
                            '2-tuple is expected')

                        infos = await self._ensure_resolved(
                            addr, family=family, type=socket.SOCK_DGRAM,
                            proto=proto, flags=flags, loop=self)
                        ikiwa not infos:
                            raise OSError('getaddrinfo() returned empty list')

                        for fam, _, pro, _, address in infos:
                            key = (fam, pro)
                            ikiwa key not in addr_infos:
                                addr_infos[key] = [None, None]
                            addr_infos[key][idx] = address

                # each addr has to have info for each (family, proto) pair
                addr_pairs_info = [
                    (key, addr_pair) for key, addr_pair in addr_infos.items()
                    ikiwa not ((local_addr and addr_pair[0] is None) or
                            (remote_addr and addr_pair[1] is None))]

                ikiwa not addr_pairs_info:
                    raise ValueError('can not get address information')

            exceptions = []

            ikiwa reuse_address is None:
                reuse_address = os.name == 'posix' and sys.platform != 'cygwin'

            for ((family, proto),
                 (local_address, remote_address)) in addr_pairs_info:
                sock = None
                r_addr = None
                try:
                    sock = socket.socket(
                        family=family, type=socket.SOCK_DGRAM, proto=proto)
                    ikiwa reuse_address:
                        sock.setsockopt(
                            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    ikiwa reuse_port:
                        _set_reuseport(sock)
                    ikiwa allow_broadcast:
                        sock.setsockopt(
                            socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.setblocking(False)

                    ikiwa local_addr:
                        sock.bind(local_address)
                    ikiwa remote_addr:
                        ikiwa not allow_broadcast:
                            await self.sock_connect(sock, remote_address)
                        r_addr = remote_address
                except OSError as exc:
                    ikiwa sock is not None:
                        sock.close()
                    exceptions.append(exc)
                except:
                    ikiwa sock is not None:
                        sock.close()
                    raise
                else:
                    break
            else:
                raise exceptions[0]

        protocol = protocol_factory()
        waiter = self.create_future()
        transport = self._make_datagram_transport(
            sock, protocol, r_addr, waiter)
        ikiwa self._debug:
            ikiwa local_addr:
                logger.info("Datagram endpoint local_addr=%r remote_addr=%r "
                            "created: (%r, %r)",
                            local_addr, remote_addr, transport, protocol)
            else:
                logger.debug("Datagram endpoint remote_addr=%r created: "
                             "(%r, %r)",
                             remote_addr, transport, protocol)

        try:
            await waiter
        except:
            transport.close()
            raise

        rudisha transport, protocol

    async eleza _ensure_resolved(self, address, *,
                               family=0, type=socket.SOCK_STREAM,
                               proto=0, flags=0, loop):
        host, port = address[:2]
        info = _ipaddr_info(host, port, family, type, proto, *address[2:])
        ikiwa info is not None:
            # "host" is already a resolved IP.
            rudisha [info]
        else:
            rudisha await loop.getaddrinfo(host, port, family=family, type=type,
                                          proto=proto, flags=flags)

    async eleza _create_server_getaddrinfo(self, host, port, family, flags):
        infos = await self._ensure_resolved((host, port), family=family,
                                            type=socket.SOCK_STREAM,
                                            flags=flags, loop=self)
        ikiwa not infos:
            raise OSError(f'getaddrinfo({host!r}) returned empty list')
        rudisha infos

    async eleza create_server(
            self, protocol_factory, host=None, port=None,
            *,
            family=socket.AF_UNSPEC,
            flags=socket.AI_PASSIVE,
            sock=None,
            backlog=100,
            ssl=None,
            reuse_address=None,
            reuse_port=None,
            ssl_handshake_timeout=None,
            start_serving=True):
        """Create a TCP server.

        The host parameter can be a string, in that case the TCP server is
        bound to host and port.

        The host parameter can also be a sequence of strings and in that case
        the TCP server is bound to all hosts of the sequence. If a host
        appears multiple times (possibly indirectly e.g. when hostnames
        resolve to the same IP address), the server is only bound once to that
        host.

        Return a Server object which can be used to stop the service.

        This method is a coroutine.
        """
        ikiwa isinstance(ssl, bool):
            raise TypeError('ssl argument must be an SSLContext or None')

        ikiwa ssl_handshake_timeout is not None and ssl is None:
            raise ValueError(
                'ssl_handshake_timeout is only meaningful with ssl')

        ikiwa host is not None or port is not None:
            ikiwa sock is not None:
                raise ValueError(
                    'host/port and sock can not be specified at the same time')

            ikiwa reuse_address is None:
                reuse_address = os.name == 'posix' and sys.platform != 'cygwin'
            sockets = []
            ikiwa host == '':
                hosts = [None]
            elikiwa (isinstance(host, str) or
                  not isinstance(host, collections.abc.Iterable)):
                hosts = [host]
            else:
                hosts = host

            fs = [self._create_server_getaddrinfo(host, port, family=family,
                                                  flags=flags)
                  for host in hosts]
            infos = await tasks.gather(*fs, loop=self)
            infos = set(itertools.chain.kutoka_iterable(infos))

            completed = False
            try:
                for res in infos:
                    af, socktype, proto, canonname, sa = res
                    try:
                        sock = socket.socket(af, socktype, proto)
                    except socket.error:
                        # Assume it's a bad family/type/protocol combination.
                        ikiwa self._debug:
                            logger.warning('create_server() failed to create '
                                           'socket.socket(%r, %r, %r)',
                                           af, socktype, proto, exc_info=True)
                        continue
                    sockets.append(sock)
                    ikiwa reuse_address:
                        sock.setsockopt(
                            socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                    ikiwa reuse_port:
                        _set_reuseport(sock)
                    # Disable IPv4/IPv6 dual stack support (enabled by
                    # default on Linux) which makes a single socket
                    # listen on both address families.
                    ikiwa (_HAS_IPv6 and
                            af == socket.AF_INET6 and
                            hasattr(socket, 'IPPROTO_IPV6')):
                        sock.setsockopt(socket.IPPROTO_IPV6,
                                        socket.IPV6_V6ONLY,
                                        True)
                    try:
                        sock.bind(sa)
                    except OSError as err:
                        raise OSError(err.errno, 'error while attempting '
                                      'to bind on address %r: %s'
                                      % (sa, err.strerror.lower())) kutoka None
                completed = True
            finally:
                ikiwa not completed:
                    for sock in sockets:
                        sock.close()
        else:
            ikiwa sock is None:
                raise ValueError('Neither host/port nor sock were specified')
            ikiwa sock.type != socket.SOCK_STREAM:
                raise ValueError(f'A Stream Socket was expected, got {sock!r}')
            sockets = [sock]

        for sock in sockets:
            sock.setblocking(False)

        server = Server(self, sockets, protocol_factory,
                        ssl, backlog, ssl_handshake_timeout)
        ikiwa start_serving:
            server._start_serving()
            # Skip one loop iteration so that all 'loop.add_reader'
            # go through.
            await tasks.sleep(0, loop=self)

        ikiwa self._debug:
            logger.info("%r is serving", server)
        rudisha server

    async eleza connect_accepted_socket(
            self, protocol_factory, sock,
            *, ssl=None,
            ssl_handshake_timeout=None):
        """Handle an accepted connection.

        This is used by servers that accept connections outside of
        asyncio but that use asyncio to handle connections.

        This method is a coroutine.  When completed, the coroutine
        returns a (transport, protocol) pair.
        """
        ikiwa sock.type != socket.SOCK_STREAM:
            raise ValueError(f'A Stream Socket was expected, got {sock!r}')

        ikiwa ssl_handshake_timeout is not None and not ssl:
            raise ValueError(
                'ssl_handshake_timeout is only meaningful with ssl')

        transport, protocol = await self._create_connection_transport(
            sock, protocol_factory, ssl, '', server_side=True,
            ssl_handshake_timeout=ssl_handshake_timeout)
        ikiwa self._debug:
            # Get the socket kutoka the transport because SSL transport closes
            # the old socket and creates a new SSL socket
            sock = transport.get_extra_info('socket')
            logger.debug("%r handled: (%r, %r)", sock, transport, protocol)
        rudisha transport, protocol

    async eleza connect_read_pipe(self, protocol_factory, pipe):
        protocol = protocol_factory()
        waiter = self.create_future()
        transport = self._make_read_pipe_transport(pipe, protocol, waiter)

        try:
            await waiter
        except:
            transport.close()
            raise

        ikiwa self._debug:
            logger.debug('Read pipe %r connected: (%r, %r)',
                         pipe.fileno(), transport, protocol)
        rudisha transport, protocol

    async eleza connect_write_pipe(self, protocol_factory, pipe):
        protocol = protocol_factory()
        waiter = self.create_future()
        transport = self._make_write_pipe_transport(pipe, protocol, waiter)

        try:
            await waiter
        except:
            transport.close()
            raise

        ikiwa self._debug:
            logger.debug('Write pipe %r connected: (%r, %r)',
                         pipe.fileno(), transport, protocol)
        rudisha transport, protocol

    eleza _log_subprocess(self, msg, stdin, stdout, stderr):
        info = [msg]
        ikiwa stdin is not None:
            info.append(f'stdin={_format_pipe(stdin)}')
        ikiwa stdout is not None and stderr == subprocess.STDOUT:
            info.append(f'stdout=stderr={_format_pipe(stdout)}')
        else:
            ikiwa stdout is not None:
                info.append(f'stdout={_format_pipe(stdout)}')
            ikiwa stderr is not None:
                info.append(f'stderr={_format_pipe(stderr)}')
        logger.debug(' '.join(info))

    async eleza subprocess_shell(self, protocol_factory, cmd, *,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=False,
                               shell=True, bufsize=0,
                               encoding=None, errors=None, text=None,
                               **kwargs):
        ikiwa not isinstance(cmd, (bytes, str)):
            raise ValueError("cmd must be a string")
        ikiwa universal_newlines:
            raise ValueError("universal_newlines must be False")
        ikiwa not shell:
            raise ValueError("shell must be True")
        ikiwa bufsize != 0:
            raise ValueError("bufsize must be 0")
        ikiwa text:
            raise ValueError("text must be False")
        ikiwa encoding is not None:
            raise ValueError("encoding must be None")
        ikiwa errors is not None:
            raise ValueError("errors must be None")

        protocol = protocol_factory()
        debug_log = None
        ikiwa self._debug:
            # don't log parameters: they may contain sensitive information
            # (password) and may be too long
            debug_log = 'run shell command %r' % cmd
            self._log_subprocess(debug_log, stdin, stdout, stderr)
        transport = await self._make_subprocess_transport(
            protocol, cmd, True, stdin, stdout, stderr, bufsize, **kwargs)
        ikiwa self._debug and debug_log is not None:
            logger.info('%s: %r', debug_log, transport)
        rudisha transport, protocol

    async eleza subprocess_exec(self, protocol_factory, program, *args,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, universal_newlines=False,
                              shell=False, bufsize=0,
                              encoding=None, errors=None, text=None,
                              **kwargs):
        ikiwa universal_newlines:
            raise ValueError("universal_newlines must be False")
        ikiwa shell:
            raise ValueError("shell must be False")
        ikiwa bufsize != 0:
            raise ValueError("bufsize must be 0")
        ikiwa text:
            raise ValueError("text must be False")
        ikiwa encoding is not None:
            raise ValueError("encoding must be None")
        ikiwa errors is not None:
            raise ValueError("errors must be None")

        popen_args = (program,) + args
        protocol = protocol_factory()
        debug_log = None
        ikiwa self._debug:
            # don't log parameters: they may contain sensitive information
            # (password) and may be too long
            debug_log = f'execute program {program!r}'
            self._log_subprocess(debug_log, stdin, stdout, stderr)
        transport = await self._make_subprocess_transport(
            protocol, popen_args, False, stdin, stdout, stderr,
            bufsize, **kwargs)
        ikiwa self._debug and debug_log is not None:
            logger.info('%s: %r', debug_log, transport)
        rudisha transport, protocol

    eleza get_exception_handler(self):
        """Return an exception handler, or None ikiwa the default one is in use.
        """
        rudisha self._exception_handler

    eleza set_exception_handler(self, handler):
        """Set handler as the new event loop exception handler.

        If handler is None, the default exception handler will
        be set.

        If handler is a callable object, it should have a
        signature matching '(loop, context)', where 'loop'
        will be a reference to the active event loop, 'context'
        will be a dict object (see `call_exception_handler()`
        documentation for details about context).
        """
        ikiwa handler is not None and not callable(handler):
            raise TypeError(f'A callable object or None is expected, '
                            f'got {handler!r}')
        self._exception_handler = handler

    eleza default_exception_handler(self, context):
        """Default exception handler.

        This is called when an exception occurs and no exception
        handler is set, and can be called by a custom exception
        handler that wants to defer to the default behavior.

        This default handler logs the error message and other
        context-dependent information.  In debug mode, a truncated
        stack trace is also appended showing where the given object
        (e.g. a handle or future or task) was created, ikiwa any.

        The context parameter has the same meaning as in
        `call_exception_handler()`.
        """
        message = context.get('message')
        ikiwa not message:
            message = 'Unhandled exception in event loop'

        exception = context.get('exception')
        ikiwa exception is not None:
            exc_info = (type(exception), exception, exception.__traceback__)
        else:
            exc_info = False

        ikiwa ('source_traceback' not in context and
                self._current_handle is not None and
                self._current_handle._source_traceback):
            context['handle_traceback'] = \
                self._current_handle._source_traceback

        log_lines = [message]
        for key in sorted(context):
            ikiwa key in {'message', 'exception'}:
                continue
            value = context[key]
            ikiwa key == 'source_traceback':
                tb = ''.join(traceback.format_list(value))
                value = 'Object created at (most recent call last):\n'
                value += tb.rstrip()
            elikiwa key == 'handle_traceback':
                tb = ''.join(traceback.format_list(value))
                value = 'Handle created at (most recent call last):\n'
                value += tb.rstrip()
            else:
                value = repr(value)
            log_lines.append(f'{key}: {value}')

        logger.error('\n'.join(log_lines), exc_info=exc_info)

    eleza call_exception_handler(self, context):
        """Call the current event loop's exception handler.

        The context argument is a dict containing the following keys:

        - 'message': Error message;
        - 'exception' (optional): Exception object;
        - 'future' (optional): Future instance;
        - 'task' (optional): Task instance;
        - 'handle' (optional): Handle instance;
        - 'protocol' (optional): Protocol instance;
        - 'transport' (optional): Transport instance;
        - 'socket' (optional): Socket instance;
        - 'asyncgen' (optional): Asynchronous generator that caused
                                 the exception.

        New keys maybe introduced in the future.

        Note: do not overload this method in an event loop subclass.
        For custom exception handling, use the
        `set_exception_handler()` method.
        """
        ikiwa self._exception_handler is None:
            try:
                self.default_exception_handler(context)
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException:
                # Second protection layer for unexpected errors
                # in the default implementation, as well as for subclassed
                # event loops with overloaded "default_exception_handler".
                logger.error('Exception in default exception handler',
                             exc_info=True)
        else:
            try:
                self._exception_handler(self, context)
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                # Exception in the user set custom exception handler.
                try:
                    # Let's try default handler.
                    self.default_exception_handler({
                        'message': 'Unhandled error in exception handler',
                        'exception': exc,
                        'context': context,
                    })
                except (SystemExit, KeyboardInterrupt):
                    raise
                except BaseException:
                    # Guard 'default_exception_handler' in case it is
                    # overloaded.
                    logger.error('Exception in default exception handler '
                                 'while handling an unexpected error '
                                 'in custom exception handler',
                                 exc_info=True)

    eleza _add_callback(self, handle):
        """Add a Handle to _scheduled (TimerHandle) or _ready."""
        assert isinstance(handle, events.Handle), 'A Handle is required here'
        ikiwa handle._cancelled:
            return
        assert not isinstance(handle, events.TimerHandle)
        self._ready.append(handle)

    eleza _add_callback_signalsafe(self, handle):
        """Like _add_callback() but called kutoka a signal handler."""
        self._add_callback(handle)
        self._write_to_self()

    eleza _timer_handle_cancelled(self, handle):
        """Notification that a TimerHandle has been cancelled."""
        ikiwa handle._scheduled:
            self._timer_cancelled_count += 1

    eleza _run_once(self):
        """Run one full iteration of the event loop.

        This calls all currently ready callbacks, polls for I/O,
        schedules the resulting callbacks, and finally schedules
        'call_later' callbacks.
        """

        sched_count = len(self._scheduled)
        ikiwa (sched_count > _MIN_SCHEDULED_TIMER_HANDLES and
            self._timer_cancelled_count / sched_count >
                _MIN_CANCELLED_TIMER_HANDLES_FRACTION):
            # Remove delayed calls that were cancelled ikiwa their number
            # is too high
            new_scheduled = []
            for handle in self._scheduled:
                ikiwa handle._cancelled:
                    handle._scheduled = False
                else:
                    new_scheduled.append(handle)

            heapq.heapify(new_scheduled)
            self._scheduled = new_scheduled
            self._timer_cancelled_count = 0
        else:
            # Remove delayed calls that were cancelled kutoka head of queue.
            while self._scheduled and self._scheduled[0]._cancelled:
                self._timer_cancelled_count -= 1
                handle = heapq.heappop(self._scheduled)
                handle._scheduled = False

        timeout = None
        ikiwa self._ready or self._stopping:
            timeout = 0
        elikiwa self._scheduled:
            # Compute the desired timeout.
            when = self._scheduled[0]._when
            timeout = min(max(0, when - self.time()), MAXIMUM_SELECT_TIMEOUT)

        event_list = self._selector.select(timeout)
        self._process_events(event_list)

        # Handle 'later' callbacks that are ready.
        end_time = self.time() + self._clock_resolution
        while self._scheduled:
            handle = self._scheduled[0]
            ikiwa handle._when >= end_time:
                break
            handle = heapq.heappop(self._scheduled)
            handle._scheduled = False
            self._ready.append(handle)

        # This is the only place where callbacks are actually *called*.
        # All other places just add them to ready.
        # Note: We run all currently scheduled callbacks, but not any
        # callbacks scheduled by callbacks run this time around --
        # they will be run the next time (after another I/O poll).
        # Use an idiom that is thread-safe without using locks.
        ntodo = len(self._ready)
        for i in range(ntodo):
            handle = self._ready.popleft()
            ikiwa handle._cancelled:
                continue
            ikiwa self._debug:
                try:
                    self._current_handle = handle
                    t0 = self.time()
                    handle._run()
                    dt = self.time() - t0
                    ikiwa dt >= self.slow_callback_duration:
                        logger.warning('Executing %s took %.3f seconds',
                                       _format_handle(handle), dt)
                finally:
                    self._current_handle = None
            else:
                handle._run()
        handle = None  # Needed to break cycles when an exception occurs.

    eleza _set_coroutine_origin_tracking(self, enabled):
        ikiwa bool(enabled) == bool(self._coroutine_origin_tracking_enabled):
            return

        ikiwa enabled:
            self._coroutine_origin_tracking_saved_depth = (
                sys.get_coroutine_origin_tracking_depth())
            sys.set_coroutine_origin_tracking_depth(
                constants.DEBUG_STACK_DEPTH)
        else:
            sys.set_coroutine_origin_tracking_depth(
                self._coroutine_origin_tracking_saved_depth)

        self._coroutine_origin_tracking_enabled = enabled

    eleza get_debug(self):
        rudisha self._debug

    eleza set_debug(self, enabled):
        self._debug = enabled

        ikiwa self.is_running():
            self.call_soon_threadsafe(self._set_coroutine_origin_tracking, enabled)
