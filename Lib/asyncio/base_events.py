"""Base implementation of event loop.

The event loop can be broken up into a multiplexer (the part
responsible kila notifying us of I/O events) na the event loop proper,
which wraps a multiplexer ukijumuisha functionality kila scheduling callbacks,
immediately ama at a given time kwenye the future.

Whenever a public API takes a callback, subsequent positional
arguments will be pitaed to the callback if/when it ni called.  This
avoids the proliferation of trivial lambdas implementing closures.
Keyword arguments kila the callback are sio supported; this ni a
conscious design decision, leaving the door open kila keyword arguments
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

jaribu:
    agiza ssl
tatizo ImportError:  # pragma: no cover
    ssl = Tupu

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
# cancelled handles ni performed.
_MIN_SCHEDULED_TIMER_HANDLES = 100

# Minimum fraction of _scheduled timer handles that are cancelled
# before cleanup of cancelled handles ni performed.
_MIN_CANCELLED_TIMER_HANDLES_FRACTION = 0.5


_HAS_IPv6 = hasattr(socket, 'AF_INET6')

# Maximum timeout pitaed to select to avoid OS limitations
MAXIMUM_SELECT_TIMEOUT = 24 * 3600


eleza _format_handle(handle):
    cb = handle._callback
    ikiwa isinstance(getattr(cb, '__self__', Tupu), tasks.Task):
        # format the task
        rudisha repr(cb.__self__)
    isipokua:
        rudisha str(handle)


eleza _format_pipe(fd):
    ikiwa fd == subprocess.PIPE:
        rudisha '<pipe>'
    lasivyo fd == subprocess.STDOUT:
        rudisha '<stdout>'
    isipokua:
        rudisha repr(fd)


eleza _set_reuseport(sock):
    ikiwa sio hasattr(socket, 'SO_REUSEPORT'):
        ashiria ValueError('reuse_port sio supported by socket module')
    isipokua:
        jaribu:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        tatizo OSError:
            ashiria ValueError('reuse_port sio supported by socket module, '
                             'SO_REUSEPORT defined but sio implemented.')


eleza _ipaddr_info(host, port, family, type, proto, flowinfo=0, scopeid=0):
    # Try to skip getaddrinfo ikiwa "host" ni already an IP. Users might have
    # handled name resolution kwenye their own code na pita kwenye resolved IPs.
    ikiwa sio hasattr(socket, 'inet_pton'):
        rudisha

    ikiwa proto haiko kwenye {0, socket.IPPROTO_TCP, socket.IPPROTO_UDP} ama \
            host ni Tupu:
        rudisha Tupu

    ikiwa type == socket.SOCK_STREAM:
        proto = socket.IPPROTO_TCP
    lasivyo type == socket.SOCK_DGRAM:
        proto = socket.IPPROTO_UDP
    isipokua:
        rudisha Tupu

    ikiwa port ni Tupu:
        port = 0
    lasivyo isinstance(port, bytes) na port == b'':
        port = 0
    lasivyo isinstance(port, str) na port == '':
        port = 0
    isipokua:
        # If port's a service name like "http", don't skip getaddrinfo.
        jaribu:
            port = int(port)
        tatizo (TypeError, ValueError):
            rudisha Tupu

    ikiwa family == socket.AF_UNSPEC:
        afs = [socket.AF_INET]
        ikiwa _HAS_IPv6:
            afs.append(socket.AF_INET6)
    isipokua:
        afs = [family]

    ikiwa isinstance(host, bytes):
        host = host.decode('idna')
    ikiwa '%' kwenye host:
        # Linux's inet_pton doesn't accept an IPv6 zone index after host,
        # like '::1%lo0'.
        rudisha Tupu

    kila af kwenye afs:
        jaribu:
            socket.inet_pton(af, host)
            # The host has already been resolved.
            ikiwa _HAS_IPv6 na af == socket.AF_INET6:
                rudisha af, type, proto, '', (host, port, flowinfo, scopeid)
            isipokua:
                rudisha af, type, proto, '', (host, port)
        tatizo OSError:
            pita

    # "host" ni sio an IP address.
    rudisha Tupu


eleza _interleave_addrinfos(addrinfos, first_address_family_count=1):
    """Interleave list of addrinfo tuples by family."""
    # Group addresses by family
    addrinfos_by_family = collections.OrderedDict()
    kila addr kwenye addrinfos:
        family = addr[0]
        ikiwa family haiko kwenye addrinfos_by_family:
            addrinfos_by_family[family] = []
        addrinfos_by_family[family].append(addr)
    addrinfos_lists = list(addrinfos_by_family.values())

    reordered = []
    ikiwa first_address_family_count > 1:
        reordered.extend(addrinfos_lists[0][:first_address_family_count - 1])
        toa addrinfos_lists[0][:first_address_family_count - 1]
    reordered.extend(
        a kila a kwenye itertools.chain.from_iterable(
            itertools.zip_longest(*addrinfos_lists)
        ) ikiwa a ni sio Tupu)
    rudisha reordered


eleza _run_until_complete_cb(fut):
    ikiwa sio fut.cancelled():
        exc = fut.exception()
        ikiwa isinstance(exc, (SystemExit, KeyboardInterrupt)):
            # Issue #22429: run_forever() already finished, no need to
            # stop it.
            rudisha
    futures._get_loop(fut).stop()


ikiwa hasattr(socket, 'TCP_NODELAY'):
    eleza _set_nodelay(sock):
        ikiwa (sock.family kwenye {socket.AF_INET, socket.AF_INET6} na
                sock.type == socket.SOCK_STREAM na
                sock.proto == socket.IPPROTO_TCP):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
isipokua:
    eleza _set_nodelay(sock):
        pita


kundi _SendfileFallbackProtocol(protocols.Protocol):
    eleza __init__(self, transp):
        ikiwa sio isinstance(transp, transports._FlowControlMixin):
            ashiria TypeError("transport should be _FlowControlMixin instance")
        self._transport = transp
        self._proto = transp.get_protocol()
        self._should_resume_reading = transp.is_reading()
        self._should_resume_writing = transp._protocol_paused
        transp.pause_reading()
        transp.set_protocol(self)
        ikiwa self._should_resume_writing:
            self._write_ready_fut = self._transport._loop.create_future()
        isipokua:
            self._write_ready_fut = Tupu

    async eleza drain(self):
        ikiwa self._transport.is_closing():
            ashiria ConnectionError("Connection closed by peer")
        fut = self._write_ready_fut
        ikiwa fut ni Tupu:
            rudisha
        await fut

    eleza connection_made(self, transport):
        ashiria RuntimeError("Invalid state: "
                           "connection should have been established already.")

    eleza connection_lost(self, exc):
        ikiwa self._write_ready_fut ni sio Tupu:
            # Never happens ikiwa peer disconnects after sending the whole content
            # Thus disconnection ni always an exception kutoka user perspective
            ikiwa exc ni Tupu:
                self._write_ready_fut.set_exception(
                    ConnectionError("Connection ni closed by peer"))
            isipokua:
                self._write_ready_fut.set_exception(exc)
        self._proto.connection_lost(exc)

    eleza pause_writing(self):
        ikiwa self._write_ready_fut ni sio Tupu:
            rudisha
        self._write_ready_fut = self._transport._loop.create_future()

    eleza resume_writing(self):
        ikiwa self._write_ready_fut ni Tupu:
            rudisha
        self._write_ready_fut.set_result(Uongo)
        self._write_ready_fut = Tupu

    eleza data_received(self, data):
        ashiria RuntimeError("Invalid state: reading should be paused")

    eleza eof_received(self):
        ashiria RuntimeError("Invalid state: reading should be paused")

    async eleza restore(self):
        self._transport.set_protocol(self._proto)
        ikiwa self._should_resume_reading:
            self._transport.resume_reading()
        ikiwa self._write_ready_fut ni sio Tupu:
            # Cancel the future.
            # Basically it has no effect because protocol ni switched back,
            # no code should wait kila it anymore.
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
        self._serving = Uongo
        self._serving_forever_fut = Tupu

    eleza __repr__(self):
        rudisha f'<{self.__class__.__name__} sockets={self.sockets!r}>'

    eleza _attach(self):
        assert self._sockets ni sio Tupu
        self._active_count += 1

    eleza _detach(self):
        assert self._active_count > 0
        self._active_count -= 1
        ikiwa self._active_count == 0 na self._sockets ni Tupu:
            self._wakeup()

    eleza _wakeup(self):
        waiters = self._waiters
        self._waiters = Tupu
        kila waiter kwenye waiters:
            ikiwa sio waiter.done():
                waiter.set_result(waiter)

    eleza _start_serving(self):
        ikiwa self._serving:
            rudisha
        self._serving = Kweli
        kila sock kwenye self._sockets:
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
        ikiwa self._sockets ni Tupu:
            rudisha ()
        rudisha tuple(trsock.TransportSocket(s) kila s kwenye self._sockets)

    eleza close(self):
        sockets = self._sockets
        ikiwa sockets ni Tupu:
            rudisha
        self._sockets = Tupu

        kila sock kwenye sockets:
            self._loop._stop_serving(sock)

        self._serving = Uongo

        ikiwa (self._serving_forever_fut ni sio Tupu na
                sio self._serving_forever_fut.done()):
            self._serving_forever_fut.cancel()
            self._serving_forever_fut = Tupu

        ikiwa self._active_count == 0:
            self._wakeup()

    async eleza start_serving(self):
        self._start_serving()
        # Skip one loop iteration so that all 'loop.add_reader'
        # go through.
        await tasks.sleep(0, loop=self._loop)

    async eleza serve_forever(self):
        ikiwa self._serving_forever_fut ni sio Tupu:
            ashiria RuntimeError(
                f'server {self!r} ni already being awaited on serve_forever()')
        ikiwa self._sockets ni Tupu:
            ashiria RuntimeError(f'server {self!r} ni closed')

        self._start_serving()
        self._serving_forever_fut = self._loop.create_future()

        jaribu:
            await self._serving_forever_fut
        tatizo exceptions.CancelledError:
            jaribu:
                self.close()
                await self.wait_closed()
            mwishowe:
                raise
        mwishowe:
            self._serving_forever_fut = Tupu

    async eleza wait_closed(self):
        ikiwa self._sockets ni Tupu ama self._waiters ni Tupu:
            rudisha
        waiter = self._loop.create_future()
        self._waiters.append(waiter)
        await waiter


kundi BaseEventLoop(events.AbstractEventLoop):

    eleza __init__(self):
        self._timer_cancelled_count = 0
        self._closed = Uongo
        self._stopping = Uongo
        self._ready = collections.deque()
        self._scheduled = []
        self._default_executor = Tupu
        self._internal_fds = 0
        # Identifier of the thread running the event loop, ama Tupu ikiwa the
        # event loop ni sio running
        self._thread_id = Tupu
        self._clock_resolution = time.get_clock_info('monotonic').resolution
        self._exception_handler = Tupu
        self.set_debug(coroutines._is_debug_mode())
        # In debug mode, ikiwa the execution of a callback ama a step of a task
        # exceed this duration kwenye seconds, the slow callback/task ni logged.
        self.slow_callback_duration = 0.1
        self._current_handle = Tupu
        self._task_factory = Tupu
        self._coroutine_origin_tracking_enabled = Uongo
        self._coroutine_origin_tracking_saved_depth = Tupu

        # A weak set of all asynchronous generators that are
        # being iterated by the loop.
        self._asyncgens = weakref.WeakSet()
        # Set to Kweli when `loop.shutdown_asyncgens` ni called.
        self._asyncgens_shutdown_called = Uongo

    eleza __repr__(self):
        rudisha (
            f'<{self.__class__.__name__} running={self.is_running()} '
            f'closed={self.is_closed()} debug={self.get_debug()}>'
        )

    eleza create_future(self):
        """Create a Future object attached to the loop."""
        rudisha futures.Future(loop=self)

    eleza create_task(self, coro, *, name=Tupu):
        """Schedule a coroutine object.

        Return a task object.
        """
        self._check_closed()
        ikiwa self._task_factory ni Tupu:
            task = tasks.Task(coro, loop=self, name=name)
            ikiwa task._source_traceback:
                toa task._source_traceback[-1]
        isipokua:
            task = self._task_factory(self, coro)
            tasks._set_task_name(task, name)

        rudisha task

    eleza set_task_factory(self, factory):
        """Set a task factory that will be used by loop.create_task().

        If factory ni Tupu the default task factory will be set.

        If factory ni a callable, it should have a signature matching
        '(loop, coro)', where 'loop' will be a reference to the active
        event loop, 'coro' will be a coroutine object.  The callable
        must rudisha a Future.
        """
        ikiwa factory ni sio Tupu na sio callable(factory):
            ashiria TypeError('task factory must be a callable ama Tupu')
        self._task_factory = factory

    eleza get_task_factory(self):
        """Return a task factory, ama Tupu ikiwa the default one ni kwenye use."""
        rudisha self._task_factory

    eleza _make_socket_transport(self, sock, protocol, waiter=Tupu, *,
                               extra=Tupu, server=Tupu):
        """Create socket transport."""
        ashiria NotImplementedError

    eleza _make_ssl_transport(
            self, rawsock, protocol, sslcontext, waiter=Tupu,
            *, server_side=Uongo, server_hostname=Tupu,
            extra=Tupu, server=Tupu,
            ssl_handshake_timeout=Tupu,
            call_connection_made=Kweli):
        """Create SSL transport."""
        ashiria NotImplementedError

    eleza _make_datagram_transport(self, sock, protocol,
                                 address=Tupu, waiter=Tupu, extra=Tupu):
        """Create datagram transport."""
        ashiria NotImplementedError

    eleza _make_read_pipe_transport(self, pipe, protocol, waiter=Tupu,
                                  extra=Tupu):
        """Create read pipe transport."""
        ashiria NotImplementedError

    eleza _make_write_pipe_transport(self, pipe, protocol, waiter=Tupu,
                                   extra=Tupu):
        """Create write pipe transport."""
        ashiria NotImplementedError

    async eleza _make_subprocess_transport(self, protocol, args, shell,
                                         stdin, stdout, stderr, bufsize,
                                         extra=Tupu, **kwargs):
        """Create subprocess transport."""
        ashiria NotImplementedError

    eleza _write_to_self(self):
        """Write a byte to self-pipe, to wake up the event loop.

        This may be called kutoka a different thread.

        The subkundi ni responsible kila implementing the self-pipe.
        """
        ashiria NotImplementedError

    eleza _process_events(self, event_list):
        """Process selector events."""
        ashiria NotImplementedError

    eleza _check_closed(self):
        ikiwa self._closed:
            ashiria RuntimeError('Event loop ni closed')

    eleza _asyncgen_finalizer_hook(self, agen):
        self._asyncgens.discard(agen)
        ikiwa sio self.is_closed():
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
        self._asyncgens_shutdown_called = Kweli

        ikiwa sio len(self._asyncgens):
            # If Python version ni <3.6 ama we don't have any asynchronous
            # generators alive.
            rudisha

        closing_agens = list(self._asyncgens)
        self._asyncgens.clear()

        results = await tasks.gather(
            *[ag.aclose() kila ag kwenye closing_agens],
            return_exceptions=Kweli,
            loop=self)

        kila result, agen kwenye zip(results, closing_agens):
            ikiwa isinstance(result, Exception):
                self.call_exception_handler({
                    'message': f'an error occurred during closing of '
                               f'asynchronous generator {agen!r}',
                    'exception': result,
                    'asyncgen': agen
                })

    eleza run_forever(self):
        """Run until stop() ni called."""
        self._check_closed()
        ikiwa self.is_running():
            ashiria RuntimeError('This event loop ni already running')
        ikiwa events._get_running_loop() ni sio Tupu:
            ashiria RuntimeError(
                'Cannot run the event loop wakati another loop ni running')
        self._set_coroutine_origin_tracking(self._debug)
        self._thread_id = threading.get_ident()

        old_agen_hooks = sys.get_asyncgen_hooks()
        sys.set_asyncgen_hooks(firstiter=self._asyncgen_firstiter_hook,
                               finalizer=self._asyncgen_finalizer_hook)
        jaribu:
            events._set_running_loop(self)
            wakati Kweli:
                self._run_once()
                ikiwa self._stopping:
                    koma
        mwishowe:
            self._stopping = Uongo
            self._thread_id = Tupu
            events._set_running_loop(Tupu)
            self._set_coroutine_origin_tracking(Uongo)
            sys.set_asyncgen_hooks(*old_agen_hooks)

    eleza run_until_complete(self, future):
        """Run until the Future ni done.

        If the argument ni a coroutine, it ni wrapped kwenye a Task.

        WARNING: It would be disastrous to call run_until_complete()
        ukijumuisha the same coroutine twice -- it would wrap it kwenye two
        different Tasks na that can't be good.

        Return the Future's result, ama ashiria its exception.
        """
        self._check_closed()

        new_task = sio futures.isfuture(future)
        future = tasks.ensure_future(future, loop=self)
        ikiwa new_task:
            # An exception ni raised ikiwa the future didn't complete, so there
            # ni no need to log the "destroy pending task" message
            future._log_destroy_pending = Uongo

        future.add_done_callback(_run_until_complete_cb)
        jaribu:
            self.run_forever()
        tatizo:
            ikiwa new_task na future.done() na sio future.cancelled():
                # The coroutine raised a BaseException. Consume the exception
                # to sio log a warning, the caller doesn't have access to the
                # local task.
                future.exception()
            raise
        mwishowe:
            future.remove_done_callback(_run_until_complete_cb)
        ikiwa sio future.done():
            ashiria RuntimeError('Event loop stopped before Future completed.')

        rudisha future.result()

    eleza stop(self):
        """Stop running the event loop.

        Every callback already scheduled will still run.  This simply informs
        run_forever to stop looping after a complete iteration.
        """
        self._stopping = Kweli

    eleza close(self):
        """Close the event loop.

        This clears the queues na shuts down the executor,
        but does sio wait kila the executor to finish.

        The event loop must sio be running.
        """
        ikiwa self.is_running():
            ashiria RuntimeError("Cannot close a running event loop")
        ikiwa self._closed:
            rudisha
        ikiwa self._debug:
            logger.debug("Close %r", self)
        self._closed = Kweli
        self._ready.clear()
        self._scheduled.clear()
        executor = self._default_executor
        ikiwa executor ni sio Tupu:
            self._default_executor = Tupu
            executor.shutdown(wait=Uongo)

    eleza is_closed(self):
        """Returns Kweli ikiwa the event loop was closed."""
        rudisha self._closed

    eleza __del__(self, _warn=warnings.warn):
        ikiwa sio self.is_closed():
            _warn(f"unclosed event loop {self!r}", ResourceWarning, source=self)
            ikiwa sio self.is_running():
                self.close()

    eleza is_running(self):
        """Returns Kweli ikiwa the event loop ni running."""
        rudisha (self._thread_id ni sio Tupu)

    eleza time(self):
        """Return the time according to the event loop's clock.

        This ni a float expressed kwenye seconds since an epoch, but the
        epoch, precision, accuracy na drift are unspecified na may
        differ per event loop.
        """
        rudisha time.monotonic()

    eleza call_later(self, delay, callback, *args, context=Tupu):
        """Arrange kila a callback to be called at a given time.

        Return a Handle: an opaque object ukijumuisha a cancel() method that
        can be used to cancel the call.

        The delay can be an int ama float, expressed kwenye seconds.  It is
        always relative to the current time.

        Each callback will be called exactly once.  If two callbacks
        are scheduled kila exactly the same time, it undefined which
        will be called first.

        Any positional arguments after the callback will be pitaed to
        the callback when it ni called.
        """
        timer = self.call_at(self.time() + delay, callback, *args,
                             context=context)
        ikiwa timer._source_traceback:
            toa timer._source_traceback[-1]
        rudisha timer

    eleza call_at(self, when, callback, *args, context=Tupu):
        """Like call_later(), but uses an absolute time.

        Absolute time corresponds to the event loop's time() method.
        """
        self._check_closed()
        ikiwa self._debug:
            self._check_thread()
            self._check_callback(callback, 'call_at')
        timer = events.TimerHandle(when, callback, args, self, context)
        ikiwa timer._source_traceback:
            toa timer._source_traceback[-1]
        heapq.heappush(self._scheduled, timer)
        timer._scheduled = Kweli
        rudisha timer

    eleza call_soon(self, callback, *args, context=Tupu):
        """Arrange kila a callback to be called kama soon kama possible.

        This operates kama a FIFO queue: callbacks are called kwenye the
        order kwenye which they are registered.  Each callback will be
        called exactly once.

        Any positional arguments after the callback will be pitaed to
        the callback when it ni called.
        """
        self._check_closed()
        ikiwa self._debug:
            self._check_thread()
            self._check_callback(callback, 'call_soon')
        handle = self._call_soon(callback, args, context)
        ikiwa handle._source_traceback:
            toa handle._source_traceback[-1]
        rudisha handle

    eleza _check_callback(self, callback, method):
        ikiwa (coroutines.iscoroutine(callback) ama
                coroutines.iscoroutinefunction(callback)):
            ashiria TypeError(
                f"coroutines cannot be used ukijumuisha {method}()")
        ikiwa sio callable(callback):
            ashiria TypeError(
                f'a callable object was expected by {method}(), '
                f'got {callback!r}')

    eleza _call_soon(self, callback, args, context):
        handle = events.Handle(callback, args, self, context)
        ikiwa handle._source_traceback:
            toa handle._source_traceback[-1]
        self._ready.append(handle)
        rudisha handle

    eleza _check_thread(self):
        """Check that the current thread ni the thread running the event loop.

        Non-thread-safe methods of this kundi make this assumption na will
        likely behave incorrectly when the assumption ni violated.

        Should only be called when (self._debug == Kweli).  The caller is
        responsible kila checking this condition kila performance reasons.
        """
        ikiwa self._thread_id ni Tupu:
            rudisha
        thread_id = threading.get_ident()
        ikiwa thread_id != self._thread_id:
            ashiria RuntimeError(
                "Non-thread-safe operation invoked on an event loop other "
                "than the current one")

    eleza call_soon_threadsafe(self, callback, *args, context=Tupu):
        """Like call_soon(), but thread-safe."""
        self._check_closed()
        ikiwa self._debug:
            self._check_callback(callback, 'call_soon_threadsafe')
        handle = self._call_soon(callback, args, context)
        ikiwa handle._source_traceback:
            toa handle._source_traceback[-1]
        self._write_to_self()
        rudisha handle

    eleza run_in_executor(self, executor, func, *args):
        self._check_closed()
        ikiwa self._debug:
            self._check_callback(func, 'run_in_executor')
        ikiwa executor ni Tupu:
            executor = self._default_executor
            ikiwa executor ni Tupu:
                executor = concurrent.futures.ThreadPoolExecutor()
                self._default_executor = executor
        rudisha futures.wrap_future(
            executor.submit(func, *args), loop=self)

    eleza set_default_executor(self, executor):
        ikiwa sio isinstance(executor, concurrent.futures.ThreadPoolExecutor):
            warnings.warn(
                'Using the default executor that ni sio an instance of '
                'ThreadPoolExecutor ni deprecated na will be prohibited '
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
        isipokua:
            logger.debug(msg)
        rudisha addrinfo

    async eleza getaddrinfo(self, host, port, *,
                          family=0, type=0, proto=0, flags=0):
        ikiwa self._debug:
            getaddr_func = self._getaddrinfo_debug
        isipokua:
            getaddr_func = socket.getaddrinfo

        rudisha await self.run_in_executor(
            Tupu, getaddr_func, host, port, family, type, proto, flags)

    async eleza getnameinfo(self, sockaddr, flags=0):
        rudisha await self.run_in_executor(
            Tupu, socket.getnameinfo, sockaddr, flags)

    async eleza sock_sendfile(self, sock, file, offset=0, count=Tupu,
                            *, fallback=Kweli):
        ikiwa self._debug na sock.gettimeout() != 0:
            ashiria ValueError("the socket must be non-blocking")
        self._check_sendfile_params(sock, file, offset, count)
        jaribu:
            rudisha await self._sock_sendfile_native(sock, file,
                                                    offset, count)
        tatizo exceptions.SendfileNotAvailableError kama exc:
            ikiwa sio fallback:
                raise
        rudisha await self._sock_sendfile_fallback(sock, file,
                                                  offset, count)

    async eleza _sock_sendfile_native(self, sock, file, offset, count):
        # NB: sendfile syscall ni sio supported kila SSL sockets na
        # non-mmap files even ikiwa sendfile ni supported by OS
        ashiria exceptions.SendfileNotAvailableError(
            f"syscall sendfile ni sio available kila socket {sock!r} "
            "and file {file!r} combination")

    async eleza _sock_sendfile_fallback(self, sock, file, offset, count):
        ikiwa offset:
            file.seek(offset)
        blocksize = (
            min(count, constants.SENDFILE_FALLBACK_READBUFFER_SIZE)
            ikiwa count isipokua constants.SENDFILE_FALLBACK_READBUFFER_SIZE
        )
        buf = bytearray(blocksize)
        total_sent = 0
        jaribu:
            wakati Kweli:
                ikiwa count:
                    blocksize = min(count - total_sent, blocksize)
                    ikiwa blocksize <= 0:
                        koma
                view = memoryview(buf)[:blocksize]
                read = await self.run_in_executor(Tupu, file.readinto, view)
                ikiwa sio read:
                    koma  # EOF
                await self.sock_sendall(sock, view[:read])
                total_sent += read
            rudisha total_sent
        mwishowe:
            ikiwa total_sent > 0 na hasattr(file, 'seek'):
                file.seek(offset + total_sent)

    eleza _check_sendfile_params(self, sock, file, offset, count):
        ikiwa 'b' haiko kwenye getattr(file, 'mode', 'b'):
            ashiria ValueError("file should be opened kwenye binary mode")
        ikiwa sio sock.type == socket.SOCK_STREAM:
            ashiria ValueError("only SOCK_STREAM type sockets are supported")
        ikiwa count ni sio Tupu:
            ikiwa sio isinstance(count, int):
                ashiria TypeError(
                    "count must be a positive integer (got {!r})".format(count))
            ikiwa count <= 0:
                ashiria ValueError(
                    "count must be a positive integer (got {!r})".format(count))
        ikiwa sio isinstance(offset, int):
            ashiria TypeError(
                "offset must be a non-negative integer (got {!r})".format(
                    offset))
        ikiwa offset < 0:
            ashiria ValueError(
                "offset must be a non-negative integer (got {!r})".format(
                    offset))

    async eleza _connect_sock(self, exceptions, addr_info, local_addr_infos=Tupu):
        """Create, bind na connect one socket."""
        my_exceptions = []
        exceptions.append(my_exceptions)
        family, type_, proto, _, address = addr_info
        sock = Tupu
        jaribu:
            sock = socket.socket(family=family, type=type_, proto=proto)
            sock.setblocking(Uongo)
            ikiwa local_addr_infos ni sio Tupu:
                kila _, _, _, _, laddr kwenye local_addr_infos:
                    jaribu:
                        sock.bind(laddr)
                        koma
                    tatizo OSError kama exc:
                        msg = (
                            f'error wakati attempting to bind on '
                            f'address {laddr!r}: '
                            f'{exc.strerror.lower()}'
                        )
                        exc = OSError(exc.errno, msg)
                        my_exceptions.append(exc)
                isipokua:  # all bind attempts failed
                    ashiria my_exceptions.pop()
            await self.sock_connect(sock, address)
            rudisha sock
        tatizo OSError kama exc:
            my_exceptions.append(exc)
            ikiwa sock ni sio Tupu:
                sock.close()
            raise
        tatizo:
            ikiwa sock ni sio Tupu:
                sock.close()
            raise

    async eleza create_connection(
            self, protocol_factory, host=Tupu, port=Tupu,
            *, ssl=Tupu, family=0,
            proto=0, flags=0, sock=Tupu,
            local_addr=Tupu, server_hostname=Tupu,
            ssl_handshake_timeout=Tupu,
            happy_eyeballs_delay=Tupu, interleave=Tupu):
        """Connect to a TCP server.

        Create a streaming transport connection to a given Internet host na
        port: socket family AF_INET ama socket.AF_INET6 depending on host (or
        family ikiwa specified), socket type SOCK_STREAM. protocol_factory must be
        a callable returning a protocol instance.

        This method ni a coroutine which will try to establish the connection
        kwenye the background.  When successful, the coroutine returns a
        (transport, protocol) pair.
        """
        ikiwa server_hostname ni sio Tupu na sio ssl:
            ashiria ValueError('server_hostname ni only meaningful ukijumuisha ssl')

        ikiwa server_hostname ni Tupu na ssl:
            # Use host kama default kila server_hostname.  It ni an error
            # ikiwa host ni empty ama sio set, e.g. when an
            # already-connected socket was pitaed ama when only a port
            # ni given.  To avoid this error, you can pita
            # server_hostname='' -- this will bypita the hostname
            # check.  (This also means that ikiwa host ni a numeric
            # IP/IPv6 address, we will attempt to verify that exact
            # address; this will probably fail, but it ni possible to
            # create a certificate kila a specific IP address, so we
            # don't judge it here.)
            ikiwa sio host:
                ashiria ValueError('You must set server_hostname '
                                 'when using ssl without a host')
            server_hostname = host

        ikiwa ssl_handshake_timeout ni sio Tupu na sio ssl:
            ashiria ValueError(
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl')

        ikiwa happy_eyeballs_delay ni sio Tupu na interleave ni Tupu:
            # If using happy eyeballs, default to interleave addresses by family
            interleave = 1

        ikiwa host ni sio Tupu ama port ni sio Tupu:
            ikiwa sock ni sio Tupu:
                ashiria ValueError(
                    'host/port na sock can sio be specified at the same time')

            infos = await self._ensure_resolved(
                (host, port), family=family,
                type=socket.SOCK_STREAM, proto=proto, flags=flags, loop=self)
            ikiwa sio inos:
                ashiria OSError('getaddrinfo() returned empty list')

            ikiwa local_addr ni sio Tupu:
                laddr_infos = await self._ensure_resolved(
                    local_addr, family=family,
                    type=socket.SOCK_STREAM, proto=proto,
                    flags=flags, loop=self)
                ikiwa sio laddr_infos:
                    ashiria OSError('getaddrinfo() returned empty list')
            isipokua:
                laddr_infos = Tupu

            ikiwa interleave:
                infos = _interleave_addrinfos(infos, interleave)

            exceptions = []
            ikiwa happy_eyeballs_delay ni Tupu:
                # sio using happy eyeballs
                kila addrinfo kwenye infos:
                    jaribu:
                        sock = await self._connect_sock(
                            exceptions, addrinfo, laddr_infos)
                        koma
                    tatizo OSError:
                        endelea
            isipokua:  # using happy eyeballs
                sock, _, _ = await staggered.staggered_race(
                    (functools.partial(self._connect_sock,
                                       exceptions, addrinfo, laddr_infos)
                     kila addrinfo kwenye infos),
                    happy_eyeballs_delay, loop=self)

            ikiwa sock ni Tupu:
                exceptions = [exc kila sub kwenye exceptions kila exc kwenye sub]
                ikiwa len(exceptions) == 1:
                    ashiria exceptions[0]
                isipokua:
                    # If they all have the same str(), ashiria one.
                    motoa = str(exceptions[0])
                    ikiwa all(str(exc) == motoa kila exc kwenye exceptions):
                        ashiria exceptions[0]
                    # Raise a combined exception so the user can see all
                    # the various error messages.
                    ashiria OSError('Multiple exceptions: {}'.format(
                        ', '.join(str(exc) kila exc kwenye exceptions)))

        isipokua:
            ikiwa sock ni Tupu:
                ashiria ValueError(
                    'host na port was sio specified na no sock specified')
            ikiwa sock.type != socket.SOCK_STREAM:
                # We allow AF_INET, AF_INET6, AF_UNIX kama long kama they
                # are SOCK_STREAM.
                # We support pitaing AF_UNIX sockets even though we have
                # a dedicated API kila that: create_unix_connection.
                # Disallowing AF_UNIX kwenye this method, komas backwards
                # compatibility.
                ashiria ValueError(
                    f'A Stream Socket was expected, got {sock!r}')

        transport, protocol = await self._create_connection_transport(
            sock, protocol_factory, ssl, server_hostname,
            ssl_handshake_timeout=ssl_handshake_timeout)
        ikiwa self._debug:
            # Get the socket kutoka the transport because SSL transport closes
            # the old socket na creates a new SSL socket
            sock = transport.get_extra_info('socket')
            logger.debug("%r connected to %s:%r: (%r, %r)",
                         sock, host, port, transport, protocol)
        rudisha transport, protocol

    async eleza _create_connection_transport(
            self, sock, protocol_factory, ssl,
            server_hostname, server_side=Uongo,
            ssl_handshake_timeout=Tupu):

        sock.setblocking(Uongo)

        protocol = protocol_factory()
        waiter = self.create_future()
        ikiwa ssl:
            sslcontext = Tupu ikiwa isinstance(ssl, bool) isipokua ssl
            transport = self._make_ssl_transport(
                sock, protocol, sslcontext, waiter,
                server_side=server_side, server_hostname=server_hostname,
                ssl_handshake_timeout=ssl_handshake_timeout)
        isipokua:
            transport = self._make_socket_transport(sock, protocol, waiter)

        jaribu:
            await waiter
        tatizo:
            transport.close()
            raise

        rudisha transport, protocol

    async eleza sendfile(self, transport, file, offset=0, count=Tupu,
                       *, fallback=Kweli):
        """Send a file to transport.

        Return the total number of bytes which were sent.

        The method uses high-performance os.sendfile ikiwa available.

        file must be a regular file object opened kwenye binary mode.

        offset tells kutoka where to start reading the file. If specified,
        count ni the total number of bytes to transmit kama opposed to
        sending the file until EOF ni reached. File position ni updated on
        rudisha ama also kwenye case of error kwenye which case file.tell()
        can be used to figure out the number of bytes
        which were sent.

        fallback set to Kweli makes asyncio to manually read na send
        the file when the platform does sio support the sendfile syscall
        (e.g. Windows ama SSL socket on Unix).

        Raise SendfileNotAvailableError ikiwa the system does sio support
        sendfile syscall na fallback ni Uongo.
        """
        ikiwa transport.is_closing():
            ashiria RuntimeError("Transport ni closing")
        mode = getattr(transport, '_sendfile_compatible',
                       constants._SendfileMode.UNSUPPORTED)
        ikiwa mode ni constants._SendfileMode.UNSUPPORTED:
            ashiria RuntimeError(
                f"sendfile ni sio supported kila transport {transport!r}")
        ikiwa mode ni constants._SendfileMode.TRY_NATIVE:
            jaribu:
                rudisha await self._sendfile_native(transport, file,
                                                   offset, count)
            tatizo exceptions.SendfileNotAvailableError kama exc:
                ikiwa sio fallback:
                    raise

        ikiwa sio fallback:
            ashiria RuntimeError(
                f"fallback ni disabled na native sendfile ni sio "
                f"supported kila transport {transport!r}")

        rudisha await self._sendfile_fallback(transport, file,
                                             offset, count)

    async eleza _sendfile_native(self, transp, file, offset, count):
        ashiria exceptions.SendfileNotAvailableError(
            "sendfile syscall ni sio supported")

    async eleza _sendfile_fallback(self, transp, file, offset, count):
        ikiwa offset:
            file.seek(offset)
        blocksize = min(count, 16384) ikiwa count isipokua 16384
        buf = bytearray(blocksize)
        total_sent = 0
        proto = _SendfileFallbackProtocol(transp)
        jaribu:
            wakati Kweli:
                ikiwa count:
                    blocksize = min(count - total_sent, blocksize)
                    ikiwa blocksize <= 0:
                        rudisha total_sent
                view = memoryview(buf)[:blocksize]
                read = await self.run_in_executor(Tupu, file.readinto, view)
                ikiwa sio read:
                    rudisha total_sent  # EOF
                await proto.drain()
                transp.write(view[:read])
                total_sent += read
        mwishowe:
            ikiwa total_sent > 0 na hasattr(file, 'seek'):
                file.seek(offset + total_sent)
            await proto.restore()

    async eleza start_tls(self, transport, protocol, sslcontext, *,
                        server_side=Uongo,
                        server_hostname=Tupu,
                        ssl_handshake_timeout=Tupu):
        """Upgrade transport to TLS.

        Return a new transport that *protocol* should start using
        immediately.
        """
        ikiwa ssl ni Tupu:
            ashiria RuntimeError('Python ssl module ni sio available')

        ikiwa sio isinstance(sslcontext, ssl.SSLContext):
            ashiria TypeError(
                f'sslcontext ni expected to be an instance of ssl.SSLContext, '
                f'got {sslcontext!r}')

        ikiwa sio getattr(transport, '_start_tls_compatible', Uongo):
            ashiria TypeError(
                f'transport {transport!r} ni sio supported by start_tls()')

        waiter = self.create_future()
        ssl_protocol = sslproto.SSLProtocol(
            self, protocol, sslcontext, waiter,
            server_side, server_hostname,
            ssl_handshake_timeout=ssl_handshake_timeout,
            call_connection_made=Uongo)

        # Pause early so that "ssl_protocol.data_received()" doesn't
        # have a chance to get called before "ssl_protocol.connection_made()".
        transport.pause_reading()

        transport.set_protocol(ssl_protocol)
        conmade_cb = self.call_soon(ssl_protocol.connection_made, transport)
        resume_cb = self.call_soon(transport.resume_reading)

        jaribu:
            await waiter
        tatizo BaseException:
            transport.close()
            conmade_cb.cancel()
            resume_cb.cancel()
            raise

        rudisha ssl_protocol._app_transport

    async eleza create_datagram_endpoint(self, protocol_factory,
                                       local_addr=Tupu, remote_addr=Tupu, *,
                                       family=0, proto=0, flags=0,
                                       reuse_address=Tupu, reuse_port=Tupu,
                                       allow_broadcast=Tupu, sock=Tupu):
        """Create datagram connection."""
        ikiwa sock ni sio Tupu:
            ikiwa sock.type != socket.SOCK_DGRAM:
                ashiria ValueError(
                    f'A UDP Socket was expected, got {sock!r}')
            ikiwa (local_addr ama remote_addr ama
                    family ama proto ama flags ama
                    reuse_address ama reuse_port ama allow_broadcast):
                # show the problematic kwargs kwenye exception msg
                opts = dict(local_addr=local_addr, remote_addr=remote_addr,
                            family=family, proto=proto, flags=flags,
                            reuse_address=reuse_address, reuse_port=reuse_port,
                            allow_broadcast=allow_broadcast)
                problems = ', '.join(f'{k}={v}' kila k, v kwenye opts.items() ikiwa v)
                ashiria ValueError(
                    f'socket modifier keyword arguments can sio be used '
                    f'when sock ni specified. ({problems})')
            sock.setblocking(Uongo)
            r_addr = Tupu
        isipokua:
            ikiwa sio (local_addr ama remote_addr):
                ikiwa family == 0:
                    ashiria ValueError('unexpected address family')
                addr_pairs_info = (((family, proto), (Tupu, Tupu)),)
            lasivyo hasattr(socket, 'AF_UNIX') na family == socket.AF_UNIX:
                kila addr kwenye (local_addr, remote_addr):
                    ikiwa addr ni sio Tupu na sio isinstance(addr, str):
                        ashiria TypeError('string ni expected')

                ikiwa local_addr na local_addr[0] haiko kwenye (0, '\x00'):
                    jaribu:
                        ikiwa stat.S_ISSOCK(os.stat(local_addr).st_mode):
                            os.remove(local_addr)
                    tatizo FileNotFoundError:
                        pita
                    tatizo OSError kama err:
                        # Directory may have permissions only to create socket.
                        logger.error('Unable to check ama remove stale UNIX '
                                     'socket %r: %r',
                                     local_addr, err)

                addr_pairs_info = (((family, proto),
                                    (local_addr, remote_addr)), )
            isipokua:
                # join address by (family, protocol)
                addr_infos = {}  # Using order preserving dict
                kila idx, addr kwenye ((0, local_addr), (1, remote_addr)):
                    ikiwa addr ni sio Tupu:
                        assert isinstance(addr, tuple) na len(addr) == 2, (
                            '2-tuple ni expected')

                        infos = await self._ensure_resolved(
                            addr, family=family, type=socket.SOCK_DGRAM,
                            proto=proto, flags=flags, loop=self)
                        ikiwa sio inos:
                            ashiria OSError('getaddrinfo() returned empty list')

                        kila fam, _, pro, _, address kwenye infos:
                            key = (fam, pro)
                            ikiwa key haiko kwenye addr_infos:
                                addr_infos[key] = [Tupu, Tupu]
                            addr_infos[key][idx] = address

                # each addr has to have info kila each (family, proto) pair
                addr_pairs_info = [
                    (key, addr_pair) kila key, addr_pair kwenye addr_infos.items()
                    ikiwa sio ((local_addr na addr_pair[0] ni Tupu) ama
                            (remote_addr na addr_pair[1] ni Tupu))]

                ikiwa sio addr_pairs_info:
                    ashiria ValueError('can sio get address information')

            exceptions = []

            ikiwa reuse_address ni Tupu:
                reuse_address = os.name == 'posix' na sys.platform != 'cygwin'

            kila ((family, proto),
                 (local_address, remote_address)) kwenye addr_pairs_info:
                sock = Tupu
                r_addr = Tupu
                jaribu:
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
                    sock.setblocking(Uongo)

                    ikiwa local_addr:
                        sock.bind(local_address)
                    ikiwa remote_addr:
                        ikiwa sio allow_broadcast:
                            await self.sock_connect(sock, remote_address)
                        r_addr = remote_address
                tatizo OSError kama exc:
                    ikiwa sock ni sio Tupu:
                        sock.close()
                    exceptions.append(exc)
                tatizo:
                    ikiwa sock ni sio Tupu:
                        sock.close()
                    raise
                isipokua:
                    koma
            isipokua:
                ashiria exceptions[0]

        protocol = protocol_factory()
        waiter = self.create_future()
        transport = self._make_datagram_transport(
            sock, protocol, r_addr, waiter)
        ikiwa self._debug:
            ikiwa local_addr:
                logger.info("Datagram endpoint local_addr=%r remote_addr=%r "
                            "created: (%r, %r)",
                            local_addr, remote_addr, transport, protocol)
            isipokua:
                logger.debug("Datagram endpoint remote_addr=%r created: "
                             "(%r, %r)",
                             remote_addr, transport, protocol)

        jaribu:
            await waiter
        tatizo:
            transport.close()
            raise

        rudisha transport, protocol

    async eleza _ensure_resolved(self, address, *,
                               family=0, type=socket.SOCK_STREAM,
                               proto=0, flags=0, loop):
        host, port = address[:2]
        info = _ipaddr_info(host, port, family, type, proto, *address[2:])
        ikiwa info ni sio Tupu:
            # "host" ni already a resolved IP.
            rudisha [info]
        isipokua:
            rudisha await loop.getaddrinfo(host, port, family=family, type=type,
                                          proto=proto, flags=flags)

    async eleza _create_server_getaddrinfo(self, host, port, family, flags):
        infos = await self._ensure_resolved((host, port), family=family,
                                            type=socket.SOCK_STREAM,
                                            flags=flags, loop=self)
        ikiwa sio inos:
            ashiria OSError(f'getaddrinfo({host!r}) returned empty list')
        rudisha infos

    async eleza create_server(
            self, protocol_factory, host=Tupu, port=Tupu,
            *,
            family=socket.AF_UNSPEC,
            flags=socket.AI_PASSIVE,
            sock=Tupu,
            backlog=100,
            ssl=Tupu,
            reuse_address=Tupu,
            reuse_port=Tupu,
            ssl_handshake_timeout=Tupu,
            start_serving=Kweli):
        """Create a TCP server.

        The host parameter can be a string, kwenye that case the TCP server is
        bound to host na port.

        The host parameter can also be a sequence of strings na kwenye that case
        the TCP server ni bound to all hosts of the sequence. If a host
        appears multiple times (possibly indirectly e.g. when hostnames
        resolve to the same IP address), the server ni only bound once to that
        host.

        Return a Server object which can be used to stop the service.

        This method ni a coroutine.
        """
        ikiwa isinstance(ssl, bool):
            ashiria TypeError('ssl argument must be an SSLContext ama Tupu')

        ikiwa ssl_handshake_timeout ni sio Tupu na ssl ni Tupu:
            ashiria ValueError(
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl')

        ikiwa host ni sio Tupu ama port ni sio Tupu:
            ikiwa sock ni sio Tupu:
                ashiria ValueError(
                    'host/port na sock can sio be specified at the same time')

            ikiwa reuse_address ni Tupu:
                reuse_address = os.name == 'posix' na sys.platform != 'cygwin'
            sockets = []
            ikiwa host == '':
                hosts = [Tupu]
            lasivyo (isinstance(host, str) ama
                  sio isinstance(host, collections.abc.Iterable)):
                hosts = [host]
            isipokua:
                hosts = host

            fs = [self._create_server_getaddrinfo(host, port, family=family,
                                                  flags=flags)
                  kila host kwenye hosts]
            infos = await tasks.gather(*fs, loop=self)
            infos = set(itertools.chain.from_iterable(infos))

            completed = Uongo
            jaribu:
                kila res kwenye infos:
                    af, socktype, proto, canonname, sa = res
                    jaribu:
                        sock = socket.socket(af, socktype, proto)
                    tatizo socket.error:
                        # Assume it's a bad family/type/protocol combination.
                        ikiwa self._debug:
                            logger.warning('create_server() failed to create '
                                           'socket.socket(%r, %r, %r)',
                                           af, socktype, proto, exc_info=Kweli)
                        endelea
                    sockets.append(sock)
                    ikiwa reuse_address:
                        sock.setsockopt(
                            socket.SOL_SOCKET, socket.SO_REUSEADDR, Kweli)
                    ikiwa reuse_port:
                        _set_reuseport(sock)
                    # Disable IPv4/IPv6 dual stack support (enabled by
                    # default on Linux) which makes a single socket
                    # listen on both address families.
                    ikiwa (_HAS_IPv6 na
                            af == socket.AF_INET6 na
                            hasattr(socket, 'IPPROTO_IPV6')):
                        sock.setsockopt(socket.IPPROTO_IPV6,
                                        socket.IPV6_V6ONLY,
                                        Kweli)
                    jaribu:
                        sock.bind(sa)
                    tatizo OSError kama err:
                        ashiria OSError(err.errno, 'error wakati attempting '
                                      'to bind on address %r: %s'
                                      % (sa, err.strerror.lower())) kutoka Tupu
                completed = Kweli
            mwishowe:
                ikiwa sio completed:
                    kila sock kwenye sockets:
                        sock.close()
        isipokua:
            ikiwa sock ni Tupu:
                ashiria ValueError('Neither host/port nor sock were specified')
            ikiwa sock.type != socket.SOCK_STREAM:
                ashiria ValueError(f'A Stream Socket was expected, got {sock!r}')
            sockets = [sock]

        kila sock kwenye sockets:
            sock.setblocking(Uongo)

        server = Server(self, sockets, protocol_factory,
                        ssl, backlog, ssl_handshake_timeout)
        ikiwa start_serving:
            server._start_serving()
            # Skip one loop iteration so that all 'loop.add_reader'
            # go through.
            await tasks.sleep(0, loop=self)

        ikiwa self._debug:
            logger.info("%r ni serving", server)
        rudisha server

    async eleza connect_accepted_socket(
            self, protocol_factory, sock,
            *, ssl=Tupu,
            ssl_handshake_timeout=Tupu):
        """Handle an accepted connection.

        This ni used by servers that accept connections outside of
        asyncio but that use asyncio to handle connections.

        This method ni a coroutine.  When completed, the coroutine
        returns a (transport, protocol) pair.
        """
        ikiwa sock.type != socket.SOCK_STREAM:
            ashiria ValueError(f'A Stream Socket was expected, got {sock!r}')

        ikiwa ssl_handshake_timeout ni sio Tupu na sio ssl:
            ashiria ValueError(
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl')

        transport, protocol = await self._create_connection_transport(
            sock, protocol_factory, ssl, '', server_side=Kweli,
            ssl_handshake_timeout=ssl_handshake_timeout)
        ikiwa self._debug:
            # Get the socket kutoka the transport because SSL transport closes
            # the old socket na creates a new SSL socket
            sock = transport.get_extra_info('socket')
            logger.debug("%r handled: (%r, %r)", sock, transport, protocol)
        rudisha transport, protocol

    async eleza connect_read_pipe(self, protocol_factory, pipe):
        protocol = protocol_factory()
        waiter = self.create_future()
        transport = self._make_read_pipe_transport(pipe, protocol, waiter)

        jaribu:
            await waiter
        tatizo:
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

        jaribu:
            await waiter
        tatizo:
            transport.close()
            raise

        ikiwa self._debug:
            logger.debug('Write pipe %r connected: (%r, %r)',
                         pipe.fileno(), transport, protocol)
        rudisha transport, protocol

    eleza _log_subprocess(self, msg, stdin, stdout, stderr):
        info = [msg]
        ikiwa stdin ni sio Tupu:
            info.append(f'stdin={_format_pipe(stdin)}')
        ikiwa stdout ni sio Tupu na stderr == subprocess.STDOUT:
            info.append(f'stdout=stderr={_format_pipe(stdout)}')
        isipokua:
            ikiwa stdout ni sio Tupu:
                info.append(f'stdout={_format_pipe(stdout)}')
            ikiwa stderr ni sio Tupu:
                info.append(f'stderr={_format_pipe(stderr)}')
        logger.debug(' '.join(info))

    async eleza subprocess_shell(self, protocol_factory, cmd, *,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=Uongo,
                               shell=Kweli, bufsize=0,
                               encoding=Tupu, errors=Tupu, text=Tupu,
                               **kwargs):
        ikiwa sio isinstance(cmd, (bytes, str)):
            ashiria ValueError("cmd must be a string")
        ikiwa universal_newlines:
            ashiria ValueError("universal_newlines must be Uongo")
        ikiwa sio shell:
            ashiria ValueError("shell must be Kweli")
        ikiwa bufsize != 0:
            ashiria ValueError("bufsize must be 0")
        ikiwa text:
            ashiria ValueError("text must be Uongo")
        ikiwa encoding ni sio Tupu:
            ashiria ValueError("encoding must be Tupu")
        ikiwa errors ni sio Tupu:
            ashiria ValueError("errors must be Tupu")

        protocol = protocol_factory()
        debug_log = Tupu
        ikiwa self._debug:
            # don't log parameters: they may contain sensitive information
            # (pitaword) na may be too long
            debug_log = 'run shell command %r' % cmd
            self._log_subprocess(debug_log, stdin, stdout, stderr)
        transport = await self._make_subprocess_transport(
            protocol, cmd, Kweli, stdin, stdout, stderr, bufsize, **kwargs)
        ikiwa self._debug na debug_log ni sio Tupu:
            logger.info('%s: %r', debug_log, transport)
        rudisha transport, protocol

    async eleza subprocess_exec(self, protocol_factory, program, *args,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, universal_newlines=Uongo,
                              shell=Uongo, bufsize=0,
                              encoding=Tupu, errors=Tupu, text=Tupu,
                              **kwargs):
        ikiwa universal_newlines:
            ashiria ValueError("universal_newlines must be Uongo")
        ikiwa shell:
            ashiria ValueError("shell must be Uongo")
        ikiwa bufsize != 0:
            ashiria ValueError("bufsize must be 0")
        ikiwa text:
            ashiria ValueError("text must be Uongo")
        ikiwa encoding ni sio Tupu:
            ashiria ValueError("encoding must be Tupu")
        ikiwa errors ni sio Tupu:
            ashiria ValueError("errors must be Tupu")

        popen_args = (program,) + args
        protocol = protocol_factory()
        debug_log = Tupu
        ikiwa self._debug:
            # don't log parameters: they may contain sensitive information
            # (pitaword) na may be too long
            debug_log = f'execute program {program!r}'
            self._log_subprocess(debug_log, stdin, stdout, stderr)
        transport = await self._make_subprocess_transport(
            protocol, popen_args, Uongo, stdin, stdout, stderr,
            bufsize, **kwargs)
        ikiwa self._debug na debug_log ni sio Tupu:
            logger.info('%s: %r', debug_log, transport)
        rudisha transport, protocol

    eleza get_exception_handler(self):
        """Return an exception handler, ama Tupu ikiwa the default one ni kwenye use.
        """
        rudisha self._exception_handler

    eleza set_exception_handler(self, handler):
        """Set handler kama the new event loop exception handler.

        If handler ni Tupu, the default exception handler will
        be set.

        If handler ni a callable object, it should have a
        signature matching '(loop, context)', where 'loop'
        will be a reference to the active event loop, 'context'
        will be a dict object (see `call_exception_handler()`
        documentation kila details about context).
        """
        ikiwa handler ni sio Tupu na sio callable(handler):
            ashiria TypeError(f'A callable object ama Tupu ni expected, '
                            f'got {handler!r}')
        self._exception_handler = handler

    eleza default_exception_handler(self, context):
        """Default exception handler.

        This ni called when an exception occurs na no exception
        handler ni set, na can be called by a custom exception
        handler that wants to defer to the default behavior.

        This default handler logs the error message na other
        context-dependent information.  In debug mode, a truncated
        stack trace ni also appended showing where the given object
        (e.g. a handle ama future ama task) was created, ikiwa any.

        The context parameter has the same meaning kama in
        `call_exception_handler()`.
        """
        message = context.get('message')
        ikiwa sio message:
            message = 'Unhandled exception kwenye event loop'

        exception = context.get('exception')
        ikiwa exception ni sio Tupu:
            exc_info = (type(exception), exception, exception.__traceback__)
        isipokua:
            exc_info = Uongo

        ikiwa ('source_traceback' haiko kwenye context na
                self._current_handle ni sio Tupu na
                self._current_handle._source_traceback):
            context['handle_traceback'] = \
                self._current_handle._source_traceback

        log_lines = [message]
        kila key kwenye sorted(context):
            ikiwa key kwenye {'message', 'exception'}:
                endelea
            value = context[key]
            ikiwa key == 'source_traceback':
                tb = ''.join(traceback.format_list(value))
                value = 'Object created at (most recent call last):\n'
                value += tb.rstrip()
            lasivyo key == 'handle_traceback':
                tb = ''.join(traceback.format_list(value))
                value = 'Handle created at (most recent call last):\n'
                value += tb.rstrip()
            isipokua:
                value = repr(value)
            log_lines.append(f'{key}: {value}')

        logger.error('\n'.join(log_lines), exc_info=exc_info)

    eleza call_exception_handler(self, context):
        """Call the current event loop's exception handler.

        The context argument ni a dict containing the following keys:

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

        New keys maybe introduced kwenye the future.

        Note: do sio overload this method kwenye an event loop subclass.
        For custom exception handling, use the
        `set_exception_handler()` method.
        """
        ikiwa self._exception_handler ni Tupu:
            jaribu:
                self.default_exception_handler(context)
            tatizo (SystemExit, KeyboardInterrupt):
                raise
            tatizo BaseException:
                # Second protection layer kila unexpected errors
                # kwenye the default implementation, kama well kama kila subclassed
                # event loops ukijumuisha overloaded "default_exception_handler".
                logger.error('Exception kwenye default exception handler',
                             exc_info=Kweli)
        isipokua:
            jaribu:
                self._exception_handler(self, context)
            tatizo (SystemExit, KeyboardInterrupt):
                raise
            tatizo BaseException kama exc:
                # Exception kwenye the user set custom exception handler.
                jaribu:
                    # Let's try default handler.
                    self.default_exception_handler({
                        'message': 'Unhandled error kwenye exception handler',
                        'exception': exc,
                        'context': context,
                    })
                tatizo (SystemExit, KeyboardInterrupt):
                    raise
                tatizo BaseException:
                    # Guard 'default_exception_handler' kwenye case it is
                    # overloaded.
                    logger.error('Exception kwenye default exception handler '
                                 'wakati handling an unexpected error '
                                 'in custom exception handler',
                                 exc_info=Kweli)

    eleza _add_callback(self, handle):
        """Add a Handle to _scheduled (TimerHandle) ama _ready."""
        assert isinstance(handle, events.Handle), 'A Handle ni required here'
        ikiwa handle._cancelled:
            rudisha
        assert sio isinstance(handle, events.TimerHandle)
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

        This calls all currently ready callbacks, polls kila I/O,
        schedules the resulting callbacks, na finally schedules
        'call_later' callbacks.
        """

        sched_count = len(self._scheduled)
        ikiwa (sched_count > _MIN_SCHEDULED_TIMER_HANDLES na
            self._timer_cancelled_count / sched_count >
                _MIN_CANCELLED_TIMER_HANDLES_FRACTION):
            # Remove delayed calls that were cancelled ikiwa their number
            # ni too high
            new_scheduled = []
            kila handle kwenye self._scheduled:
                ikiwa handle._cancelled:
                    handle._scheduled = Uongo
                isipokua:
                    new_scheduled.append(handle)

            heapq.heapify(new_scheduled)
            self._scheduled = new_scheduled
            self._timer_cancelled_count = 0
        isipokua:
            # Remove delayed calls that were cancelled kutoka head of queue.
            wakati self._scheduled na self._scheduled[0]._cancelled:
                self._timer_cancelled_count -= 1
                handle = heapq.heappop(self._scheduled)
                handle._scheduled = Uongo

        timeout = Tupu
        ikiwa self._ready ama self._stopping:
            timeout = 0
        lasivyo self._scheduled:
            # Compute the desired timeout.
            when = self._scheduled[0]._when
            timeout = min(max(0, when - self.time()), MAXIMUM_SELECT_TIMEOUT)

        event_list = self._selector.select(timeout)
        self._process_events(event_list)

        # Handle 'later' callbacks that are ready.
        end_time = self.time() + self._clock_resolution
        wakati self._scheduled:
            handle = self._scheduled[0]
            ikiwa handle._when >= end_time:
                koma
            handle = heapq.heappop(self._scheduled)
            handle._scheduled = Uongo
            self._ready.append(handle)

        # This ni the only place where callbacks are actually *called*.
        # All other places just add them to ready.
        # Note: We run all currently scheduled callbacks, but sio any
        # callbacks scheduled by callbacks run this time around --
        # they will be run the next time (after another I/O poll).
        # Use an idiom that ni thread-safe without using locks.
        ntodo = len(self._ready)
        kila i kwenye range(ntodo):
            handle = self._ready.popleft()
            ikiwa handle._cancelled:
                endelea
            ikiwa self._debug:
                jaribu:
                    self._current_handle = handle
                    t0 = self.time()
                    handle._run()
                    dt = self.time() - t0
                    ikiwa dt >= self.slow_callback_duration:
                        logger.warning('Executing %s took %.3f seconds',
                                       _format_handle(handle), dt)
                mwishowe:
                    self._current_handle = Tupu
            isipokua:
                handle._run()
        handle = Tupu  # Needed to koma cycles when an exception occurs.

    eleza _set_coroutine_origin_tracking(self, enabled):
        ikiwa bool(enabled) == bool(self._coroutine_origin_tracking_enabled):
            rudisha

        ikiwa enabled:
            self._coroutine_origin_tracking_saved_depth = (
                sys.get_coroutine_origin_tracking_depth())
            sys.set_coroutine_origin_tracking_depth(
                constants.DEBUG_STACK_DEPTH)
        isipokua:
            sys.set_coroutine_origin_tracking_depth(
                self._coroutine_origin_tracking_saved_depth)

        self._coroutine_origin_tracking_enabled = enabled

    eleza get_debug(self):
        rudisha self._debug

    eleza set_debug(self, enabled):
        self._debug = enabled

        ikiwa self.is_running():
            self.call_soon_threadsafe(self._set_coroutine_origin_tracking, enabled)
