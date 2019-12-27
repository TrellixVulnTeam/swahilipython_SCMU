"""Event loop using a selector and related classes.

A selector is a "notify-when-ready" multiplexer.  For a subkundi which
also includes support for signal handling, see the unix_events sub-module.
"""

__all__ = 'BaseSelectorEventLoop',

agiza collections
agiza errno
agiza functools
agiza selectors
agiza socket
agiza warnings
agiza weakref
try:
    agiza ssl
except ImportError:  # pragma: no cover
    ssl = None

kutoka . agiza base_events
kutoka . agiza constants
kutoka . agiza events
kutoka . agiza futures
kutoka . agiza protocols
kutoka . agiza sslproto
kutoka . agiza transports
kutoka . agiza trsock
kutoka .log agiza logger


eleza _test_selector_event(selector, fd, event):
    # Test ikiwa the selector is monitoring 'event' events
    # for the file descriptor 'fd'.
    try:
        key = selector.get_key(fd)
    except KeyError:
        rudisha False
    else:
        rudisha bool(key.events & event)


kundi BaseSelectorEventLoop(base_events.BaseEventLoop):
    """Selector event loop.

    See events.EventLoop for API specification.
    """

    eleza __init__(self, selector=None):
        super().__init__()

        ikiwa selector is None:
            selector = selectors.DefaultSelector()
        logger.debug('Using selector: %s', selector.__class__.__name__)
        self._selector = selector
        self._make_self_pipe()
        self._transports = weakref.WeakValueDictionary()

    eleza _make_socket_transport(self, sock, protocol, waiter=None, *,
                               extra=None, server=None):
        rudisha _SelectorSocketTransport(self, sock, protocol, waiter,
                                        extra, server)

    eleza _make_ssl_transport(
            self, rawsock, protocol, sslcontext, waiter=None,
            *, server_side=False, server_hostname=None,
            extra=None, server=None,
            ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT):
        ssl_protocol = sslproto.SSLProtocol(
                self, protocol, sslcontext, waiter,
                server_side, server_hostname,
                ssl_handshake_timeout=ssl_handshake_timeout)
        _SelectorSocketTransport(self, rawsock, ssl_protocol,
                                 extra=extra, server=server)
        rudisha ssl_protocol._app_transport

    eleza _make_datagram_transport(self, sock, protocol,
                                 address=None, waiter=None, extra=None):
        rudisha _SelectorDatagramTransport(self, sock, protocol,
                                          address, waiter, extra)

    eleza close(self):
        ikiwa self.is_running():
            raise RuntimeError("Cannot close a running event loop")
        ikiwa self.is_closed():
            return
        self._close_self_pipe()
        super().close()
        ikiwa self._selector is not None:
            self._selector.close()
            self._selector = None

    eleza _close_self_pipe(self):
        self._remove_reader(self._ssock.fileno())
        self._ssock.close()
        self._ssock = None
        self._csock.close()
        self._csock = None
        self._internal_fds -= 1

    eleza _make_self_pipe(self):
        # A self-socket, really. :-)
        self._ssock, self._csock = socket.socketpair()
        self._ssock.setblocking(False)
        self._csock.setblocking(False)
        self._internal_fds += 1
        self._add_reader(self._ssock.fileno(), self._read_kutoka_self)

    eleza _process_self_data(self, data):
        pass

    eleza _read_kutoka_self(self):
        while True:
            try:
                data = self._ssock.recv(4096)
                ikiwa not data:
                    break
                self._process_self_data(data)
            except InterruptedError:
                continue
            except BlockingIOError:
                break

    eleza _write_to_self(self):
        # This may be called kutoka a different thread, possibly after
        # _close_self_pipe() has been called or even while it is
        # running.  Guard for self._csock being None or closed.  When
        # a socket is closed, send() raises OSError (with errno set to
        # EBADF, but let's not rely on the exact error code).
        csock = self._csock
        ikiwa csock is not None:
            try:
                csock.send(b'\0')
            except OSError:
                ikiwa self._debug:
                    logger.debug("Fail to write a null byte into the "
                                 "self-pipe socket",
                                 exc_info=True)

    eleza _start_serving(self, protocol_factory, sock,
                       sslcontext=None, server=None, backlog=100,
                       ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT):
        self._add_reader(sock.fileno(), self._accept_connection,
                         protocol_factory, sock, sslcontext, server, backlog,
                         ssl_handshake_timeout)

    eleza _accept_connection(
            self, protocol_factory, sock,
            sslcontext=None, server=None, backlog=100,
            ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT):
        # This method is only called once for each event loop tick where the
        # listening socket has triggered an EVENT_READ. There may be multiple
        # connections waiting for an .accept() so it is called in a loop.
        # See https://bugs.python.org/issue27906 for more details.
        for _ in range(backlog):
            try:
                conn, addr = sock.accept()
                ikiwa self._debug:
                    logger.debug("%r got a new connection kutoka %r: %r",
                                 server, addr, conn)
                conn.setblocking(False)
            except (BlockingIOError, InterruptedError, ConnectionAbortedError):
                # Early exit because the socket accept buffer is empty.
                rudisha None
            except OSError as exc:
                # There's nowhere to send the error, so just log it.
                ikiwa exc.errno in (errno.EMFILE, errno.ENFILE,
                                 errno.ENOBUFS, errno.ENOMEM):
                    # Some platforms (e.g. Linux keep reporting the FD as
                    # ready, so we remove the read handler temporarily.
                    # We'll try again in a while.
                    self.call_exception_handler({
                        'message': 'socket.accept() out of system resource',
                        'exception': exc,
                        'socket': trsock.TransportSocket(sock),
                    })
                    self._remove_reader(sock.fileno())
                    self.call_later(constants.ACCEPT_RETRY_DELAY,
                                    self._start_serving,
                                    protocol_factory, sock, sslcontext, server,
                                    backlog, ssl_handshake_timeout)
                else:
                    raise  # The event loop will catch, log and ignore it.
            else:
                extra = {'peername': addr}
                accept = self._accept_connection2(
                    protocol_factory, conn, extra, sslcontext, server,
                    ssl_handshake_timeout)
                self.create_task(accept)

    async eleza _accept_connection2(
            self, protocol_factory, conn, extra,
            sslcontext=None, server=None,
            ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT):
        protocol = None
        transport = None
        try:
            protocol = protocol_factory()
            waiter = self.create_future()
            ikiwa sslcontext:
                transport = self._make_ssl_transport(
                    conn, protocol, sslcontext, waiter=waiter,
                    server_side=True, extra=extra, server=server,
                    ssl_handshake_timeout=ssl_handshake_timeout)
            else:
                transport = self._make_socket_transport(
                    conn, protocol, waiter=waiter, extra=extra,
                    server=server)

            try:
                await waiter
            except BaseException:
                transport.close()
                raise
                # It's now up to the protocol to handle the connection.

        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            ikiwa self._debug:
                context = {
                    'message':
                        'Error on transport creation for incoming connection',
                    'exception': exc,
                }
                ikiwa protocol is not None:
                    context['protocol'] = protocol
                ikiwa transport is not None:
                    context['transport'] = transport
                self.call_exception_handler(context)

    eleza _ensure_fd_no_transport(self, fd):
        fileno = fd
        ikiwa not isinstance(fileno, int):
            try:
                fileno = int(fileno.fileno())
            except (AttributeError, TypeError, ValueError):
                # This code matches selectors._fileobj_to_fd function.
                raise ValueError(f"Invalid file object: {fd!r}") kutoka None
        try:
            transport = self._transports[fileno]
        except KeyError:
            pass
        else:
            ikiwa not transport.is_closing():
                raise RuntimeError(
                    f'File descriptor {fd!r} is used by transport '
                    f'{transport!r}')

    eleza _add_reader(self, fd, callback, *args):
        self._check_closed()
        handle = events.Handle(callback, args, self, None)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_READ,
                                    (handle, None))
        else:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_READ,
                                  (handle, writer))
            ikiwa reader is not None:
                reader.cancel()

    eleza _remove_reader(self, fd):
        ikiwa self.is_closed():
            rudisha False
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            rudisha False
        else:
            mask, (reader, writer) = key.events, key.data
            mask &= ~selectors.EVENT_READ
            ikiwa not mask:
                self._selector.unregister(fd)
            else:
                self._selector.modify(fd, mask, (None, writer))

            ikiwa reader is not None:
                reader.cancel()
                rudisha True
            else:
                rudisha False

    eleza _add_writer(self, fd, callback, *args):
        self._check_closed()
        handle = events.Handle(callback, args, self, None)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_WRITE,
                                    (None, handle))
        else:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_WRITE,
                                  (reader, handle))
            ikiwa writer is not None:
                writer.cancel()

    eleza _remove_writer(self, fd):
        """Remove a writer callback."""
        ikiwa self.is_closed():
            rudisha False
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            rudisha False
        else:
            mask, (reader, writer) = key.events, key.data
            # Remove both writer and connector.
            mask &= ~selectors.EVENT_WRITE
            ikiwa not mask:
                self._selector.unregister(fd)
            else:
                self._selector.modify(fd, mask, (reader, None))

            ikiwa writer is not None:
                writer.cancel()
                rudisha True
            else:
                rudisha False

    eleza add_reader(self, fd, callback, *args):
        """Add a reader callback."""
        self._ensure_fd_no_transport(fd)
        rudisha self._add_reader(fd, callback, *args)

    eleza remove_reader(self, fd):
        """Remove a reader callback."""
        self._ensure_fd_no_transport(fd)
        rudisha self._remove_reader(fd)

    eleza add_writer(self, fd, callback, *args):
        """Add a writer callback.."""
        self._ensure_fd_no_transport(fd)
        rudisha self._add_writer(fd, callback, *args)

    eleza remove_writer(self, fd):
        """Remove a writer callback."""
        self._ensure_fd_no_transport(fd)
        rudisha self._remove_writer(fd)

    async eleza sock_recv(self, sock, n):
        """Receive data kutoka the socket.

        The rudisha value is a bytes object representing the data received.
        The maximum amount of data to be received at once is specified by
        nbytes.
        """
        ikiwa self._debug and sock.gettimeout() != 0:
            raise ValueError("the socket must be non-blocking")
        try:
            rudisha sock.recv(n)
        except (BlockingIOError, InterruptedError):
            pass
        fut = self.create_future()
        fd = sock.fileno()
        self.add_reader(fd, self._sock_recv, fut, sock, n)
        fut.add_done_callback(
            functools.partial(self._sock_read_done, fd))
        rudisha await fut

    eleza _sock_read_done(self, fd, fut):
        self.remove_reader(fd)

    eleza _sock_recv(self, fut, sock, n):
        # _sock_recv() can add itself as an I/O callback ikiwa the operation can't
        # be done immediately. Don't use it directly, call sock_recv().
        ikiwa fut.done():
            return
        try:
            data = sock.recv(n)
        except (BlockingIOError, InterruptedError):
            rudisha  # try again next time
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(data)

    async eleza sock_recv_into(self, sock, buf):
        """Receive data kutoka the socket.

        The received data is written into *buf* (a writable buffer).
        The rudisha value is the number of bytes written.
        """
        ikiwa self._debug and sock.gettimeout() != 0:
            raise ValueError("the socket must be non-blocking")
        try:
            rudisha sock.recv_into(buf)
        except (BlockingIOError, InterruptedError):
            pass
        fut = self.create_future()
        fd = sock.fileno()
        self.add_reader(fd, self._sock_recv_into, fut, sock, buf)
        fut.add_done_callback(
            functools.partial(self._sock_read_done, fd))
        rudisha await fut

    eleza _sock_recv_into(self, fut, sock, buf):
        # _sock_recv_into() can add itself as an I/O callback ikiwa the operation
        # can't be done immediately. Don't use it directly, call
        # sock_recv_into().
        ikiwa fut.done():
            return
        try:
            nbytes = sock.recv_into(buf)
        except (BlockingIOError, InterruptedError):
            rudisha  # try again next time
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(nbytes)

    async eleza sock_sendall(self, sock, data):
        """Send data to the socket.

        The socket must be connected to a remote socket. This method continues
        to send data kutoka data until either all data has been sent or an
        error occurs. None is returned on success. On error, an exception is
        raised, and there is no way to determine how much data, ikiwa any, was
        successfully processed by the receiving end of the connection.
        """
        ikiwa self._debug and sock.gettimeout() != 0:
            raise ValueError("the socket must be non-blocking")
        try:
            n = sock.send(data)
        except (BlockingIOError, InterruptedError):
            n = 0

        ikiwa n == len(data):
            # all data sent
            return

        fut = self.create_future()
        fd = sock.fileno()
        fut.add_done_callback(
            functools.partial(self._sock_write_done, fd))
        # use a trick with a list in closure to store a mutable state
        self.add_writer(fd, self._sock_sendall, fut, sock,
                        memoryview(data), [n])
        rudisha await fut

    eleza _sock_sendall(self, fut, sock, view, pos):
        ikiwa fut.done():
            # Future cancellation can be scheduled on previous loop iteration
            return
        start = pos[0]
        try:
            n = sock.send(view[start:])
        except (BlockingIOError, InterruptedError):
            return
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
            return

        start += n

        ikiwa start == len(view):
            fut.set_result(None)
        else:
            pos[0] = start

    async eleza sock_connect(self, sock, address):
        """Connect to a remote socket at address.

        This method is a coroutine.
        """
        ikiwa self._debug and sock.gettimeout() != 0:
            raise ValueError("the socket must be non-blocking")

        ikiwa not hasattr(socket, 'AF_UNIX') or sock.family != socket.AF_UNIX:
            resolved = await self._ensure_resolved(
                address, family=sock.family, proto=sock.proto, loop=self)
            _, _, _, _, address = resolved[0]

        fut = self.create_future()
        self._sock_connect(fut, sock, address)
        rudisha await fut

    eleza _sock_connect(self, fut, sock, address):
        fd = sock.fileno()
        try:
            sock.connect(address)
        except (BlockingIOError, InterruptedError):
            # Issue #23618: When the C function connect() fails with EINTR, the
            # connection runs in background. We have to wait until the socket
            # becomes writable to be notified when the connection succeed or
            # fails.
            fut.add_done_callback(
                functools.partial(self._sock_write_done, fd))
            self.add_writer(fd, self._sock_connect_cb, fut, sock, address)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(None)

    eleza _sock_write_done(self, fd, fut):
        self.remove_writer(fd)

    eleza _sock_connect_cb(self, fut, sock, address):
        ikiwa fut.done():
            return

        try:
            err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            ikiwa err != 0:
                # Jump to any except clause below.
                raise OSError(err, f'Connect call failed {address}')
        except (BlockingIOError, InterruptedError):
            # socket is still registered, the callback will be retried later
            pass
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(None)

    async eleza sock_accept(self, sock):
        """Accept a connection.

        The socket must be bound to an address and listening for connections.
        The rudisha value is a pair (conn, address) where conn is a new socket
        object usable to send and receive data on the connection, and address
        is the address bound to the socket on the other end of the connection.
        """
        ikiwa self._debug and sock.gettimeout() != 0:
            raise ValueError("the socket must be non-blocking")
        fut = self.create_future()
        self._sock_accept(fut, False, sock)
        rudisha await fut

    eleza _sock_accept(self, fut, registered, sock):
        fd = sock.fileno()
        ikiwa registered:
            self.remove_reader(fd)
        ikiwa fut.done():
            return
        try:
            conn, address = sock.accept()
            conn.setblocking(False)
        except (BlockingIOError, InterruptedError):
            self.add_reader(fd, self._sock_accept, fut, True, sock)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        else:
            fut.set_result((conn, address))

    async eleza _sendfile_native(self, transp, file, offset, count):
        del self._transports[transp._sock_fd]
        resume_reading = transp.is_reading()
        transp.pause_reading()
        await transp._make_empty_waiter()
        try:
            rudisha await self.sock_sendfile(transp._sock, file, offset, count,
                                            fallback=False)
        finally:
            transp._reset_empty_waiter()
            ikiwa resume_reading:
                transp.resume_reading()
            self._transports[transp._sock_fd] = transp

    eleza _process_events(self, event_list):
        for key, mask in event_list:
            fileobj, (reader, writer) = key.fileobj, key.data
            ikiwa mask & selectors.EVENT_READ and reader is not None:
                ikiwa reader._cancelled:
                    self._remove_reader(fileobj)
                else:
                    self._add_callback(reader)
            ikiwa mask & selectors.EVENT_WRITE and writer is not None:
                ikiwa writer._cancelled:
                    self._remove_writer(fileobj)
                else:
                    self._add_callback(writer)

    eleza _stop_serving(self, sock):
        self._remove_reader(sock.fileno())
        sock.close()


kundi _SelectorTransport(transports._FlowControlMixin,
                         transports.Transport):

    max_size = 256 * 1024  # Buffer size passed to recv().

    _buffer_factory = bytearray  # Constructs initial value for self._buffer.

    # Attribute used in the destructor: it must be set even ikiwa the constructor
    # is not called (see _SelectorSslTransport which may start by raising an
    # exception)
    _sock = None

    eleza __init__(self, loop, sock, protocol, extra=None, server=None):
        super().__init__(extra, loop)
        self._extra['socket'] = trsock.TransportSocket(sock)
        try:
            self._extra['sockname'] = sock.getsockname()
        except OSError:
            self._extra['sockname'] = None
        ikiwa 'peername' not in self._extra:
            try:
                self._extra['peername'] = sock.getpeername()
            except socket.error:
                self._extra['peername'] = None
        self._sock = sock
        self._sock_fd = sock.fileno()

        self._protocol_connected = False
        self.set_protocol(protocol)

        self._server = server
        self._buffer = self._buffer_factory()
        self._conn_lost = 0  # Set when call to connection_lost scheduled.
        self._closing = False  # Set when close() called.
        ikiwa self._server is not None:
            self._server._attach()
        loop._transports[self._sock_fd] = self

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self._sock is None:
            info.append('closed')
        elikiwa self._closing:
            info.append('closing')
        info.append(f'fd={self._sock_fd}')
        # test ikiwa the transport was closed
        ikiwa self._loop is not None and not self._loop.is_closed():
            polling = _test_selector_event(self._loop._selector,
                                           self._sock_fd, selectors.EVENT_READ)
            ikiwa polling:
                info.append('read=polling')
            else:
                info.append('read=idle')

            polling = _test_selector_event(self._loop._selector,
                                           self._sock_fd,
                                           selectors.EVENT_WRITE)
            ikiwa polling:
                state = 'polling'
            else:
                state = 'idle'

            bufsize = self.get_write_buffer_size()
            info.append(f'write=<{state}, bufsize={bufsize}>')
        rudisha '<{}>'.format(' '.join(info))

    eleza abort(self):
        self._force_close(None)

    eleza set_protocol(self, protocol):
        self._protocol = protocol
        self._protocol_connected = True

    eleza get_protocol(self):
        rudisha self._protocol

    eleza is_closing(self):
        rudisha self._closing

    eleza close(self):
        ikiwa self._closing:
            return
        self._closing = True
        self._loop._remove_reader(self._sock_fd)
        ikiwa not self._buffer:
            self._conn_lost += 1
            self._loop._remove_writer(self._sock_fd)
            self._loop.call_soon(self._call_connection_lost, None)

    eleza __del__(self, _warn=warnings.warn):
        ikiwa self._sock is not None:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self._sock.close()

    eleza _fatal_error(self, exc, message='Fatal error on transport'):
        # Should be called kutoka exception handler only.
        ikiwa isinstance(exc, OSError):
            ikiwa self._loop.get_debug():
                logger.debug("%r: %s", self, message, exc_info=True)
        else:
            self._loop.call_exception_handler({
                'message': message,
                'exception': exc,
                'transport': self,
                'protocol': self._protocol,
            })
        self._force_close(exc)

    eleza _force_close(self, exc):
        ikiwa self._conn_lost:
            return
        ikiwa self._buffer:
            self._buffer.clear()
            self._loop._remove_writer(self._sock_fd)
        ikiwa not self._closing:
            self._closing = True
            self._loop._remove_reader(self._sock_fd)
        self._conn_lost += 1
        self._loop.call_soon(self._call_connection_lost, exc)

    eleza _call_connection_lost(self, exc):
        try:
            ikiwa self._protocol_connected:
                self._protocol.connection_lost(exc)
        finally:
            self._sock.close()
            self._sock = None
            self._protocol = None
            self._loop = None
            server = self._server
            ikiwa server is not None:
                server._detach()
                self._server = None

    eleza get_write_buffer_size(self):
        rudisha len(self._buffer)

    eleza _add_reader(self, fd, callback, *args):
        ikiwa self._closing:
            return

        self._loop._add_reader(fd, callback, *args)


kundi _SelectorSocketTransport(_SelectorTransport):

    _start_tls_compatible = True
    _sendfile_compatible = constants._SendfileMode.TRY_NATIVE

    eleza __init__(self, loop, sock, protocol, waiter=None,
                 extra=None, server=None):

        self._read_ready_cb = None
        super().__init__(loop, sock, protocol, extra, server)
        self._eof = False
        self._paused = False
        self._empty_waiter = None

        # Disable the Nagle algorithm -- small writes will be
        # sent without waiting for the TCP ACK.  This generally
        # decreases the latency (in some cases significantly.)
        base_events._set_nodelay(self._sock)

        self._loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        self._loop.call_soon(self._add_reader,
                             self._sock_fd, self._read_ready)
        ikiwa waiter is not None:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(futures._set_result_unless_cancelled,
                                 waiter, None)

    eleza set_protocol(self, protocol):
        ikiwa isinstance(protocol, protocols.BufferedProtocol):
            self._read_ready_cb = self._read_ready__get_buffer
        else:
            self._read_ready_cb = self._read_ready__data_received

        super().set_protocol(protocol)

    eleza is_reading(self):
        rudisha not self._paused and not self._closing

    eleza pause_reading(self):
        ikiwa self._closing or self._paused:
            return
        self._paused = True
        self._loop._remove_reader(self._sock_fd)
        ikiwa self._loop.get_debug():
            logger.debug("%r pauses reading", self)

    eleza resume_reading(self):
        ikiwa self._closing or not self._paused:
            return
        self._paused = False
        self._add_reader(self._sock_fd, self._read_ready)
        ikiwa self._loop.get_debug():
            logger.debug("%r resumes reading", self)

    eleza _read_ready(self):
        self._read_ready_cb()

    eleza _read_ready__get_buffer(self):
        ikiwa self._conn_lost:
            return

        try:
            buf = self._protocol.get_buffer(-1)
            ikiwa not len(buf):
                raise RuntimeError('get_buffer() returned an empty buffer')
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.get_buffer() call failed.')
            return

        try:
            nbytes = self._sock.recv_into(buf)
        except (BlockingIOError, InterruptedError):
            return
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(exc, 'Fatal read error on socket transport')
            return

        ikiwa not nbytes:
            self._read_ready__on_eof()
            return

        try:
            self._protocol.buffer_updated(nbytes)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.buffer_updated() call failed.')

    eleza _read_ready__data_received(self):
        ikiwa self._conn_lost:
            return
        try:
            data = self._sock.recv(self.max_size)
        except (BlockingIOError, InterruptedError):
            return
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(exc, 'Fatal read error on socket transport')
            return

        ikiwa not data:
            self._read_ready__on_eof()
            return

        try:
            self._protocol.data_received(data)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.data_received() call failed.')

    eleza _read_ready__on_eof(self):
        ikiwa self._loop.get_debug():
            logger.debug("%r received EOF", self)

        try:
            keep_open = self._protocol.eof_received()
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.eof_received() call failed.')
            return

        ikiwa keep_open:
            # We're keeping the connection open so the
            # protocol can write more, but we still can't
            # receive more, so remove the reader callback.
            self._loop._remove_reader(self._sock_fd)
        else:
            self.close()

    eleza write(self, data):
        ikiwa not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(f'data argument must be a bytes-like object, '
                            f'not {type(data).__name__!r}')
        ikiwa self._eof:
            raise RuntimeError('Cannot call write() after write_eof()')
        ikiwa self._empty_waiter is not None:
            raise RuntimeError('unable to write; sendfile is in progress')
        ikiwa not data:
            return

        ikiwa self._conn_lost:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() raised exception.')
            self._conn_lost += 1
            return

        ikiwa not self._buffer:
            # Optimization: try to send now.
            try:
                n = self._sock.send(data)
            except (BlockingIOError, InterruptedError):
                pass
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                self._fatal_error(exc, 'Fatal write error on socket transport')
                return
            else:
                data = data[n:]
                ikiwa not data:
                    return
            # Not all was written; register write handler.
            self._loop._add_writer(self._sock_fd, self._write_ready)

        # Add it to the buffer.
        self._buffer.extend(data)
        self._maybe_pause_protocol()

    eleza _write_ready(self):
        assert self._buffer, 'Data should not be empty'

        ikiwa self._conn_lost:
            return
        try:
            n = self._sock.send(self._buffer)
        except (BlockingIOError, InterruptedError):
            pass
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._loop._remove_writer(self._sock_fd)
            self._buffer.clear()
            self._fatal_error(exc, 'Fatal write error on socket transport')
            ikiwa self._empty_waiter is not None:
                self._empty_waiter.set_exception(exc)
        else:
            ikiwa n:
                del self._buffer[:n]
            self._maybe_resume_protocol()  # May append to buffer.
            ikiwa not self._buffer:
                self._loop._remove_writer(self._sock_fd)
                ikiwa self._empty_waiter is not None:
                    self._empty_waiter.set_result(None)
                ikiwa self._closing:
                    self._call_connection_lost(None)
                elikiwa self._eof:
                    self._sock.shutdown(socket.SHUT_WR)

    eleza write_eof(self):
        ikiwa self._closing or self._eof:
            return
        self._eof = True
        ikiwa not self._buffer:
            self._sock.shutdown(socket.SHUT_WR)

    eleza can_write_eof(self):
        rudisha True

    eleza _call_connection_lost(self, exc):
        super()._call_connection_lost(exc)
        ikiwa self._empty_waiter is not None:
            self._empty_waiter.set_exception(
                ConnectionError("Connection is closed by peer"))

    eleza _make_empty_waiter(self):
        ikiwa self._empty_waiter is not None:
            raise RuntimeError("Empty waiter is already set")
        self._empty_waiter = self._loop.create_future()
        ikiwa not self._buffer:
            self._empty_waiter.set_result(None)
        rudisha self._empty_waiter

    eleza _reset_empty_waiter(self):
        self._empty_waiter = None


kundi _SelectorDatagramTransport(_SelectorTransport):

    _buffer_factory = collections.deque

    eleza __init__(self, loop, sock, protocol, address=None,
                 waiter=None, extra=None):
        super().__init__(loop, sock, protocol, extra)
        self._address = address
        self._loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        self._loop.call_soon(self._add_reader,
                             self._sock_fd, self._read_ready)
        ikiwa waiter is not None:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(futures._set_result_unless_cancelled,
                                 waiter, None)

    eleza get_write_buffer_size(self):
        rudisha sum(len(data) for data, _ in self._buffer)

    eleza _read_ready(self):
        ikiwa self._conn_lost:
            return
        try:
            data, addr = self._sock.recvkutoka(self.max_size)
        except (BlockingIOError, InterruptedError):
            pass
        except OSError as exc:
            self._protocol.error_received(exc)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(exc, 'Fatal read error on datagram transport')
        else:
            self._protocol.datagram_received(data, addr)

    eleza sendto(self, data, addr=None):
        ikiwa not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(f'data argument must be a bytes-like object, '
                            f'not {type(data).__name__!r}')
        ikiwa not data:
            return

        ikiwa self._address:
            ikiwa addr not in (None, self._address):
                raise ValueError(
                    f'Invalid address: must be None or {self._address}')
            addr = self._address

        ikiwa self._conn_lost and self._address:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() raised exception.')
            self._conn_lost += 1
            return

        ikiwa not self._buffer:
            # Attempt to send it right away first.
            try:
                ikiwa self._extra['peername']:
                    self._sock.send(data)
                else:
                    self._sock.sendto(data, addr)
                return
            except (BlockingIOError, InterruptedError):
                self._loop._add_writer(self._sock_fd, self._sendto_ready)
            except OSError as exc:
                self._protocol.error_received(exc)
                return
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                self._fatal_error(
                    exc, 'Fatal write error on datagram transport')
                return

        # Ensure that what we buffer is immutable.
        self._buffer.append((bytes(data), addr))
        self._maybe_pause_protocol()

    eleza _sendto_ready(self):
        while self._buffer:
            data, addr = self._buffer.popleft()
            try:
                ikiwa self._extra['peername']:
                    self._sock.send(data)
                else:
                    self._sock.sendto(data, addr)
            except (BlockingIOError, InterruptedError):
                self._buffer.appendleft((data, addr))  # Try again later.
                break
            except OSError as exc:
                self._protocol.error_received(exc)
                return
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                self._fatal_error(
                    exc, 'Fatal write error on datagram transport')
                return

        self._maybe_resume_protocol()  # May append to buffer.
        ikiwa not self._buffer:
            self._loop._remove_writer(self._sock_fd)
            ikiwa self._closing:
                self._call_connection_lost(None)
