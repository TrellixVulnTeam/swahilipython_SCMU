"""Event loop using a proactor and related classes.

A proactor is a "notify-on-completion" multiplexer.  Currently a
proactor is only implemented on Windows with IOCP.
"""

__all__ = 'BaseProactorEventLoop',

agiza io
agiza os
agiza socket
agiza warnings
agiza signal
agiza threading
agiza collections

kutoka . agiza base_events
kutoka . agiza constants
kutoka . agiza futures
kutoka . agiza exceptions
kutoka . agiza protocols
kutoka . agiza sslproto
kutoka . agiza transports
kutoka . agiza trsock
kutoka .log agiza logger


eleza _set_socket_extra(transport, sock):
    transport._extra['socket'] = trsock.TransportSocket(sock)

    try:
        transport._extra['sockname'] = sock.getsockname()
    except socket.error:
        ikiwa transport._loop.get_debug():
            logger.warning(
                "getsockname() failed on %r", sock, exc_info=True)

    ikiwa 'peername' not in transport._extra:
        try:
            transport._extra['peername'] = sock.getpeername()
        except socket.error:
            # UDP sockets may not have a peer name
            transport._extra['peername'] = None


kundi _ProactorBasePipeTransport(transports._FlowControlMixin,
                                 transports.BaseTransport):
    """Base kundi for pipe and socket transports."""

    eleza __init__(self, loop, sock, protocol, waiter=None,
                 extra=None, server=None):
        super().__init__(extra, loop)
        self._set_extra(sock)
        self._sock = sock
        self.set_protocol(protocol)
        self._server = server
        self._buffer = None  # None or bytearray.
        self._read_fut = None
        self._write_fut = None
        self._pending_write = 0
        self._conn_lost = 0
        self._closing = False  # Set when close() called.
        self._eof_written = False
        ikiwa self._server is not None:
            self._server._attach()
        self._loop.call_soon(self._protocol.connection_made, self)
        ikiwa waiter is not None:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(futures._set_result_unless_cancelled,
                                 waiter, None)

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self._sock is None:
            info.append('closed')
        elikiwa self._closing:
            info.append('closing')
        ikiwa self._sock is not None:
            info.append(f'fd={self._sock.fileno()}')
        ikiwa self._read_fut is not None:
            info.append(f'read={self._read_fut!r}')
        ikiwa self._write_fut is not None:
            info.append(f'write={self._write_fut!r}')
        ikiwa self._buffer:
            info.append(f'write_bufsize={len(self._buffer)}')
        ikiwa self._eof_written:
            info.append('EOF written')
        rudisha '<{}>'.format(' '.join(info))

    eleza _set_extra(self, sock):
        self._extra['pipe'] = sock

    eleza set_protocol(self, protocol):
        self._protocol = protocol

    eleza get_protocol(self):
        rudisha self._protocol

    eleza is_closing(self):
        rudisha self._closing

    eleza close(self):
        ikiwa self._closing:
            return
        self._closing = True
        self._conn_lost += 1
        ikiwa not self._buffer and self._write_fut is None:
            self._loop.call_soon(self._call_connection_lost, None)
        ikiwa self._read_fut is not None:
            self._read_fut.cancel()
            self._read_fut = None

    eleza __del__(self, _warn=warnings.warn):
        ikiwa self._sock is not None:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self.close()

    eleza _fatal_error(self, exc, message='Fatal error on pipe transport'):
        try:
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
        finally:
            self._force_close(exc)

    eleza _force_close(self, exc):
        ikiwa self._empty_waiter is not None and not self._empty_waiter.done():
            ikiwa exc is None:
                self._empty_waiter.set_result(None)
            else:
                self._empty_waiter.set_exception(exc)
        ikiwa self._closing:
            return
        self._closing = True
        self._conn_lost += 1
        ikiwa self._write_fut:
            self._write_fut.cancel()
            self._write_fut = None
        ikiwa self._read_fut:
            self._read_fut.cancel()
            self._read_fut = None
        self._pending_write = 0
        self._buffer = None
        self._loop.call_soon(self._call_connection_lost, exc)

    eleza _call_connection_lost(self, exc):
        try:
            self._protocol.connection_lost(exc)
        finally:
            # XXX If there is a pending overlapped read on the other
            # end then it may fail with ERROR_NETNAME_DELETED ikiwa we
            # just close our end.  First calling shutdown() seems to
            # cure it, but maybe using DisconnectEx() would be better.
            ikiwa hasattr(self._sock, 'shutdown'):
                self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            self._sock = None
            server = self._server
            ikiwa server is not None:
                server._detach()
                self._server = None

    eleza get_write_buffer_size(self):
        size = self._pending_write
        ikiwa self._buffer is not None:
            size += len(self._buffer)
        rudisha size


kundi _ProactorReadPipeTransport(_ProactorBasePipeTransport,
                                 transports.ReadTransport):
    """Transport for read pipes."""

    eleza __init__(self, loop, sock, protocol, waiter=None,
                 extra=None, server=None):
        self._pending_data = None
        self._paused = True
        super().__init__(loop, sock, protocol, waiter, extra, server)

        self._loop.call_soon(self._loop_reading)
        self._paused = False

    eleza is_reading(self):
        rudisha not self._paused and not self._closing

    eleza pause_reading(self):
        ikiwa self._closing or self._paused:
            return
        self._paused = True

        # bpo-33694: Don't cancel self._read_fut because cancelling an
        # overlapped WSASend() loss silently data with the current proactor
        # implementation.
        #
        # If CancelIoEx() fails with ERROR_NOT_FOUND, it means that WSASend()
        # completed (even ikiwa HasOverlappedIoCompleted() returns 0), but
        # Overlapped.cancel() currently silently ignores the ERROR_NOT_FOUND
        # error. Once the overlapped is ignored, the IOCP loop will ignores the
        # completion I/O event and so not read the result of the overlapped
        # WSARecv().

        ikiwa self._loop.get_debug():
            logger.debug("%r pauses reading", self)

    eleza resume_reading(self):
        ikiwa self._closing or not self._paused:
            return

        self._paused = False
        ikiwa self._read_fut is None:
            self._loop.call_soon(self._loop_reading, None)

        data = self._pending_data
        self._pending_data = None
        ikiwa data is not None:
            # Call the protocol methode after calling _loop_reading(),
            # since the protocol can decide to pause reading again.
            self._loop.call_soon(self._data_received, data)

        ikiwa self._loop.get_debug():
            logger.debug("%r resumes reading", self)

    eleza _eof_received(self):
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

        ikiwa not keep_open:
            self.close()

    eleza _data_received(self, data):
        ikiwa self._paused:
            # Don't call any protocol method while reading is paused.
            # The protocol will be called on resume_reading().
            assert self._pending_data is None
            self._pending_data = data
            return

        ikiwa not data:
            self._eof_received()
            return

        ikiwa isinstance(self._protocol, protocols.BufferedProtocol):
            try:
                protocols._feed_data_to_buffered_proto(self._protocol, data)
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                self._fatal_error(exc,
                                  'Fatal error: protocol.buffer_updated() '
                                  'call failed.')
                return
        else:
            self._protocol.data_received(data)

    eleza _loop_reading(self, fut=None):
        data = None
        try:
            ikiwa fut is not None:
                assert self._read_fut is fut or (self._read_fut is None and
                                                 self._closing)
                self._read_fut = None
                ikiwa fut.done():
                    # deliver data later in "finally" clause
                    data = fut.result()
                else:
                    # the future will be replaced by next proactor.recv call
                    fut.cancel()

            ikiwa self._closing:
                # since close() has been called we ignore any read data
                data = None
                return

            ikiwa data == b'':
                # we got end-of-file so no need to reschedule a new read
                return

            # bpo-33694: buffer_updated() has currently no fast path because of
            # a data loss issue caused by overlapped WSASend() cancellation.

            ikiwa not self._paused:
                # reschedule a new read
                self._read_fut = self._loop._proactor.recv(self._sock, 32768)
        except ConnectionAbortedError as exc:
            ikiwa not self._closing:
                self._fatal_error(exc, 'Fatal read error on pipe transport')
            elikiwa self._loop.get_debug():
                logger.debug("Read error on pipe transport while closing",
                             exc_info=True)
        except ConnectionResetError as exc:
            self._force_close(exc)
        except OSError as exc:
            self._fatal_error(exc, 'Fatal read error on pipe transport')
        except exceptions.CancelledError:
            ikiwa not self._closing:
                raise
        else:
            ikiwa not self._paused:
                self._read_fut.add_done_callback(self._loop_reading)
        finally:
            ikiwa data is not None:
                self._data_received(data)


kundi _ProactorBaseWritePipeTransport(_ProactorBasePipeTransport,
                                      transports.WriteTransport):
    """Transport for write pipes."""

    _start_tls_compatible = True

    eleza __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._empty_waiter = None

    eleza write(self, data):
        ikiwa not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(
                f"data argument must be a bytes-like object, "
                f"not {type(data).__name__}")
        ikiwa self._eof_written:
            raise RuntimeError('write_eof() already called')
        ikiwa self._empty_waiter is not None:
            raise RuntimeError('unable to write; sendfile is in progress')

        ikiwa not data:
            return

        ikiwa self._conn_lost:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() raised exception.')
            self._conn_lost += 1
            return

        # Observable states:
        # 1. IDLE: _write_fut and _buffer both None
        # 2. WRITING: _write_fut set; _buffer None
        # 3. BACKED UP: _write_fut set; _buffer a bytearray
        # We always copy the data, so the caller can't modify it
        # while we're still waiting for the I/O to happen.
        ikiwa self._write_fut is None:  # IDLE -> WRITING
            assert self._buffer is None
            # Pass a copy, except ikiwa it's already immutable.
            self._loop_writing(data=bytes(data))
        elikiwa not self._buffer:  # WRITING -> BACKED UP
            # Make a mutable copy which we can extend.
            self._buffer = bytearray(data)
            self._maybe_pause_protocol()
        else:  # BACKED UP
            # Append to buffer (also copies).
            self._buffer.extend(data)
            self._maybe_pause_protocol()

    eleza _loop_writing(self, f=None, data=None):
        try:
            ikiwa f is not None and self._write_fut is None and self._closing:
                # XXX most likely self._force_close() has been called, and
                # it has set self._write_fut to None.
                return
            assert f is self._write_fut
            self._write_fut = None
            self._pending_write = 0
            ikiwa f:
                f.result()
            ikiwa data is None:
                data = self._buffer
                self._buffer = None
            ikiwa not data:
                ikiwa self._closing:
                    self._loop.call_soon(self._call_connection_lost, None)
                ikiwa self._eof_written:
                    self._sock.shutdown(socket.SHUT_WR)
                # Now that we've reduced the buffer size, tell the
                # protocol to resume writing ikiwa it was paused.  Note that
                # we do this last since the callback is called immediately
                # and it may add more data to the buffer (even causing the
                # protocol to be paused again).
                self._maybe_resume_protocol()
            else:
                self._write_fut = self._loop._proactor.send(self._sock, data)
                ikiwa not self._write_fut.done():
                    assert self._pending_write == 0
                    self._pending_write = len(data)
                    self._write_fut.add_done_callback(self._loop_writing)
                    self._maybe_pause_protocol()
                else:
                    self._write_fut.add_done_callback(self._loop_writing)
            ikiwa self._empty_waiter is not None and self._write_fut is None:
                self._empty_waiter.set_result(None)
        except ConnectionResetError as exc:
            self._force_close(exc)
        except OSError as exc:
            self._fatal_error(exc, 'Fatal write error on pipe transport')

    eleza can_write_eof(self):
        rudisha True

    eleza write_eof(self):
        self.close()

    eleza abort(self):
        self._force_close(None)

    eleza _make_empty_waiter(self):
        ikiwa self._empty_waiter is not None:
            raise RuntimeError("Empty waiter is already set")
        self._empty_waiter = self._loop.create_future()
        ikiwa self._write_fut is None:
            self._empty_waiter.set_result(None)
        rudisha self._empty_waiter

    eleza _reset_empty_waiter(self):
        self._empty_waiter = None


kundi _ProactorWritePipeTransport(_ProactorBaseWritePipeTransport):
    eleza __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._read_fut = self._loop._proactor.recv(self._sock, 16)
        self._read_fut.add_done_callback(self._pipe_closed)

    eleza _pipe_closed(self, fut):
        ikiwa fut.cancelled():
            # the transport has been closed
            return
        assert fut.result() == b''
        ikiwa self._closing:
            assert self._read_fut is None
            return
        assert fut is self._read_fut, (fut, self._read_fut)
        self._read_fut = None
        ikiwa self._write_fut is not None:
            self._force_close(BrokenPipeError())
        else:
            self.close()


kundi _ProactorDatagramTransport(_ProactorBasePipeTransport):
    max_size = 256 * 1024
    eleza __init__(self, loop, sock, protocol, address=None,
                 waiter=None, extra=None):
        self._address = address
        self._empty_waiter = None
        # We don't need to call _protocol.connection_made() since our base
        # constructor does it for us.
        super().__init__(loop, sock, protocol, waiter=waiter, extra=extra)

        # The base constructor sets _buffer = None, so we set it here
        self._buffer = collections.deque()
        self._loop.call_soon(self._loop_reading)

    eleza _set_extra(self, sock):
        _set_socket_extra(self, sock)

    eleza get_write_buffer_size(self):
        rudisha sum(len(data) for data, _ in self._buffer)

    eleza abort(self):
        self._force_close(None)

    eleza sendto(self, data, addr=None):
        ikiwa not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError('data argument must be bytes-like object (%r)',
                            type(data))

        ikiwa not data:
            return

        ikiwa self._address is not None and addr not in (None, self._address):
            raise ValueError(
                f'Invalid address: must be None or {self._address}')

        ikiwa self._conn_lost and self._address:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.sendto() raised exception.')
            self._conn_lost += 1
            return

        # Ensure that what we buffer is immutable.
        self._buffer.append((bytes(data), addr))

        ikiwa self._write_fut is None:
            # No current write operations are active, kick one off
            self._loop_writing()
        # else: A write operation is already kicked off

        self._maybe_pause_protocol()

    eleza _loop_writing(self, fut=None):
        try:
            ikiwa self._conn_lost:
                return

            assert fut is self._write_fut
            self._write_fut = None
            ikiwa fut:
                # We are in a _loop_writing() done callback, get the result
                fut.result()

            ikiwa not self._buffer or (self._conn_lost and self._address):
                # The connection has been closed
                ikiwa self._closing:
                    self._loop.call_soon(self._call_connection_lost, None)
                return

            data, addr = self._buffer.popleft()
            ikiwa self._address is not None:
                self._write_fut = self._loop._proactor.send(self._sock,
                                                            data)
            else:
                self._write_fut = self._loop._proactor.sendto(self._sock,
                                                              data,
                                                              addr=addr)
        except OSError as exc:
            self._protocol.error_received(exc)
        except Exception as exc:
            self._fatal_error(exc, 'Fatal write error on datagram transport')
        else:
            self._write_fut.add_done_callback(self._loop_writing)
            self._maybe_resume_protocol()

    eleza _loop_reading(self, fut=None):
        data = None
        try:
            ikiwa self._conn_lost:
                return

            assert self._read_fut is fut or (self._read_fut is None and
                                             self._closing)

            self._read_fut = None
            ikiwa fut is not None:
                res = fut.result()

                ikiwa self._closing:
                    # since close() has been called we ignore any read data
                    data = None
                    return

                ikiwa self._address is not None:
                    data, addr = res, self._address
                else:
                    data, addr = res

            ikiwa self._conn_lost:
                return
            ikiwa self._address is not None:
                self._read_fut = self._loop._proactor.recv(self._sock,
                                                           self.max_size)
            else:
                self._read_fut = self._loop._proactor.recvkutoka(self._sock,
                                                               self.max_size)
        except OSError as exc:
            self._protocol.error_received(exc)
        except exceptions.CancelledError:
            ikiwa not self._closing:
                raise
        else:
            ikiwa self._read_fut is not None:
                self._read_fut.add_done_callback(self._loop_reading)
        finally:
            ikiwa data:
                self._protocol.datagram_received(data, addr)


kundi _ProactorDuplexPipeTransport(_ProactorReadPipeTransport,
                                   _ProactorBaseWritePipeTransport,
                                   transports.Transport):
    """Transport for duplex pipes."""

    eleza can_write_eof(self):
        rudisha False

    eleza write_eof(self):
        raise NotImplementedError


kundi _ProactorSocketTransport(_ProactorReadPipeTransport,
                               _ProactorBaseWritePipeTransport,
                               transports.Transport):
    """Transport for connected sockets."""

    _sendfile_compatible = constants._SendfileMode.TRY_NATIVE

    eleza __init__(self, loop, sock, protocol, waiter=None,
                 extra=None, server=None):
        super().__init__(loop, sock, protocol, waiter, extra, server)
        base_events._set_nodelay(sock)

    eleza _set_extra(self, sock):
        _set_socket_extra(self, sock)

    eleza can_write_eof(self):
        rudisha True

    eleza write_eof(self):
        ikiwa self._closing or self._eof_written:
            return
        self._eof_written = True
        ikiwa self._write_fut is None:
            self._sock.shutdown(socket.SHUT_WR)


kundi BaseProactorEventLoop(base_events.BaseEventLoop):

    eleza __init__(self, proactor):
        super().__init__()
        logger.debug('Using proactor: %s', proactor.__class__.__name__)
        self._proactor = proactor
        self._selector = proactor   # convenient alias
        self._self_reading_future = None
        self._accept_futures = {}   # socket file descriptor => Future
        proactor.set_loop(self)
        self._make_self_pipe()
        self_no = self._csock.fileno()
        ikiwa threading.current_thread() is threading.main_thread():
            # wakeup fd can only be installed to a file descriptor kutoka the main thread
            signal.set_wakeup_fd(self_no)

    eleza _make_socket_transport(self, sock, protocol, waiter=None,
                               extra=None, server=None):
        rudisha _ProactorSocketTransport(self, sock, protocol, waiter,
                                        extra, server)

    eleza _make_ssl_transport(
            self, rawsock, protocol, sslcontext, waiter=None,
            *, server_side=False, server_hostname=None,
            extra=None, server=None,
            ssl_handshake_timeout=None):
        ssl_protocol = sslproto.SSLProtocol(
                self, protocol, sslcontext, waiter,
                server_side, server_hostname,
                ssl_handshake_timeout=ssl_handshake_timeout)
        _ProactorSocketTransport(self, rawsock, ssl_protocol,
                                 extra=extra, server=server)
        rudisha ssl_protocol._app_transport

    eleza _make_datagram_transport(self, sock, protocol,
                                 address=None, waiter=None, extra=None):
        rudisha _ProactorDatagramTransport(self, sock, protocol, address,
                                          waiter, extra)

    eleza _make_duplex_pipe_transport(self, sock, protocol, waiter=None,
                                    extra=None):
        rudisha _ProactorDuplexPipeTransport(self,
                                            sock, protocol, waiter, extra)

    eleza _make_read_pipe_transport(self, sock, protocol, waiter=None,
                                  extra=None):
        rudisha _ProactorReadPipeTransport(self, sock, protocol, waiter, extra)

    eleza _make_write_pipe_transport(self, sock, protocol, waiter=None,
                                   extra=None):
        # We want connection_lost() to be called when other end closes
        rudisha _ProactorWritePipeTransport(self,
                                           sock, protocol, waiter, extra)

    eleza close(self):
        ikiwa self.is_running():
            raise RuntimeError("Cannot close a running event loop")
        ikiwa self.is_closed():
            return

        signal.set_wakeup_fd(-1)
        # Call these methods before closing the event loop (before calling
        # BaseEventLoop.close), because they can schedule callbacks with
        # call_soon(), which is forbidden when the event loop is closed.
        self._stop_accept_futures()
        self._close_self_pipe()
        self._proactor.close()
        self._proactor = None
        self._selector = None

        # Close the event loop
        super().close()

    async eleza sock_recv(self, sock, n):
        rudisha await self._proactor.recv(sock, n)

    async eleza sock_recv_into(self, sock, buf):
        rudisha await self._proactor.recv_into(sock, buf)

    async eleza sock_sendall(self, sock, data):
        rudisha await self._proactor.send(sock, data)

    async eleza sock_connect(self, sock, address):
        rudisha await self._proactor.connect(sock, address)

    async eleza sock_accept(self, sock):
        rudisha await self._proactor.accept(sock)

    async eleza _sock_sendfile_native(self, sock, file, offset, count):
        try:
            fileno = file.fileno()
        except (AttributeError, io.UnsupportedOperation) as err:
            raise exceptions.SendfileNotAvailableError("not a regular file")
        try:
            fsize = os.fstat(fileno).st_size
        except OSError as err:
            raise exceptions.SendfileNotAvailableError("not a regular file")
        blocksize = count ikiwa count else fsize
        ikiwa not blocksize:
            rudisha 0  # empty file

        blocksize = min(blocksize, 0xffff_ffff)
        end_pos = min(offset + count, fsize) ikiwa count else fsize
        offset = min(offset, fsize)
        total_sent = 0
        try:
            while True:
                blocksize = min(end_pos - offset, blocksize)
                ikiwa blocksize <= 0:
                    rudisha total_sent
                await self._proactor.sendfile(sock, file, offset, blocksize)
                offset += blocksize
                total_sent += blocksize
        finally:
            ikiwa total_sent > 0:
                file.seek(offset)

    async eleza _sendfile_native(self, transp, file, offset, count):
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

    eleza _close_self_pipe(self):
        ikiwa self._self_reading_future is not None:
            self._self_reading_future.cancel()
            self._self_reading_future = None
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

    eleza _loop_self_reading(self, f=None):
        try:
            ikiwa f is not None:
                f.result()  # may raise
            f = self._proactor.recv(self._ssock, 4096)
        except exceptions.CancelledError:
            # _close_self_pipe() has been called, stop waiting for data
            return
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self.call_exception_handler({
                'message': 'Error on reading kutoka the event loop self pipe',
                'exception': exc,
                'loop': self,
            })
        else:
            self._self_reading_future = f
            f.add_done_callback(self._loop_self_reading)

    eleza _write_to_self(self):
        try:
            self._csock.send(b'\0')
        except OSError:
            ikiwa self._debug:
                logger.debug("Fail to write a null byte into the "
                             "self-pipe socket",
                             exc_info=True)

    eleza _start_serving(self, protocol_factory, sock,
                       sslcontext=None, server=None, backlog=100,
                       ssl_handshake_timeout=None):

        eleza loop(f=None):
            try:
                ikiwa f is not None:
                    conn, addr = f.result()
                    ikiwa self._debug:
                        logger.debug("%r got a new connection kutoka %r: %r",
                                     server, addr, conn)
                    protocol = protocol_factory()
                    ikiwa sslcontext is not None:
                        self._make_ssl_transport(
                            conn, protocol, sslcontext, server_side=True,
                            extra={'peername': addr}, server=server,
                            ssl_handshake_timeout=ssl_handshake_timeout)
                    else:
                        self._make_socket_transport(
                            conn, protocol,
                            extra={'peername': addr}, server=server)
                ikiwa self.is_closed():
                    return
                f = self._proactor.accept(sock)
            except OSError as exc:
                ikiwa sock.fileno() != -1:
                    self.call_exception_handler({
                        'message': 'Accept failed on a socket',
                        'exception': exc,
                        'socket': trsock.TransportSocket(sock),
                    })
                    sock.close()
                elikiwa self._debug:
                    logger.debug("Accept failed on socket %r",
                                 sock, exc_info=True)
            except exceptions.CancelledError:
                sock.close()
            else:
                self._accept_futures[sock.fileno()] = f
                f.add_done_callback(loop)

        self.call_soon(loop)

    eleza _process_events(self, event_list):
        # Events are processed in the IocpProactor._poll() method
        pass

    eleza _stop_accept_futures(self):
        for future in self._accept_futures.values():
            future.cancel()
        self._accept_futures.clear()

    eleza _stop_serving(self, sock):
        future = self._accept_futures.pop(sock.fileno(), None)
        ikiwa future:
            future.cancel()
        self._proactor._stop_serving(sock)
        sock.close()
