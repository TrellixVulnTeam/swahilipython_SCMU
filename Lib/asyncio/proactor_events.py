"""Event loop using a proactor na related classes.

A proactor ni a "notify-on-completion" multiplexer.  Currently a
proactor ni only implemented on Windows ukijumuisha IOCP.
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

    jaribu:
        transport._extra['sockname'] = sock.getsockname()
    tatizo socket.error:
        ikiwa transport._loop.get_debug():
            logger.warning(
                "getsockname() failed on %r", sock, exc_info=Kweli)

    ikiwa 'peername' haiko kwenye transport._extra:
        jaribu:
            transport._extra['peername'] = sock.getpeername()
        tatizo socket.error:
            # UDP sockets may sio have a peer name
            transport._extra['peername'] = Tupu


kundi _ProactorBasePipeTransport(transports._FlowControlMixin,
                                 transports.BaseTransport):
    """Base kundi kila pipe na socket transports."""

    eleza __init__(self, loop, sock, protocol, waiter=Tupu,
                 extra=Tupu, server=Tupu):
        super().__init__(extra, loop)
        self._set_extra(sock)
        self._sock = sock
        self.set_protocol(protocol)
        self._server = server
        self._buffer = Tupu  # Tupu ama bytearray.
        self._read_fut = Tupu
        self._write_fut = Tupu
        self._pending_write = 0
        self._conn_lost = 0
        self._closing = Uongo  # Set when close() called.
        self._eof_written = Uongo
        ikiwa self._server ni sio Tupu:
            self._server._attach()
        self._loop.call_soon(self._protocol.connection_made, self)
        ikiwa waiter ni sio Tupu:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(futures._set_result_unless_cancelled,
                                 waiter, Tupu)

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self._sock ni Tupu:
            info.append('closed')
        lasivyo self._closing:
            info.append('closing')
        ikiwa self._sock ni sio Tupu:
            info.append(f'fd={self._sock.fileno()}')
        ikiwa self._read_fut ni sio Tupu:
            info.append(f'read={self._read_fut!r}')
        ikiwa self._write_fut ni sio Tupu:
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
            rudisha
        self._closing = Kweli
        self._conn_lost += 1
        ikiwa sio self._buffer na self._write_fut ni Tupu:
            self._loop.call_soon(self._call_connection_lost, Tupu)
        ikiwa self._read_fut ni sio Tupu:
            self._read_fut.cancel()
            self._read_fut = Tupu

    eleza __del__(self, _warn=warnings.warn):
        ikiwa self._sock ni sio Tupu:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self.close()

    eleza _fatal_error(self, exc, message='Fatal error on pipe transport'):
        jaribu:
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
        mwishowe:
            self._force_close(exc)

    eleza _force_close(self, exc):
        ikiwa self._empty_waiter ni sio Tupu na sio self._empty_waiter.done():
            ikiwa exc ni Tupu:
                self._empty_waiter.set_result(Tupu)
            isipokua:
                self._empty_waiter.set_exception(exc)
        ikiwa self._closing:
            rudisha
        self._closing = Kweli
        self._conn_lost += 1
        ikiwa self._write_fut:
            self._write_fut.cancel()
            self._write_fut = Tupu
        ikiwa self._read_fut:
            self._read_fut.cancel()
            self._read_fut = Tupu
        self._pending_write = 0
        self._buffer = Tupu
        self._loop.call_soon(self._call_connection_lost, exc)

    eleza _call_connection_lost(self, exc):
        jaribu:
            self._protocol.connection_lost(exc)
        mwishowe:
            # XXX If there ni a pending overlapped read on the other
            # end then it may fail ukijumuisha ERROR_NETNAME_DELETED ikiwa we
            # just close our end.  First calling shutdown() seems to
            # cure it, but maybe using DisconnectEx() would be better.
            ikiwa hasattr(self._sock, 'shutdown'):
                self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            self._sock = Tupu
            server = self._server
            ikiwa server ni sio Tupu:
                server._detach()
                self._server = Tupu

    eleza get_write_buffer_size(self):
        size = self._pending_write
        ikiwa self._buffer ni sio Tupu:
            size += len(self._buffer)
        rudisha size


kundi _ProactorReadPipeTransport(_ProactorBasePipeTransport,
                                 transports.ReadTransport):
    """Transport kila read pipes."""

    eleza __init__(self, loop, sock, protocol, waiter=Tupu,
                 extra=Tupu, server=Tupu):
        self._pending_data = Tupu
        self._paused = Kweli
        super().__init__(loop, sock, protocol, waiter, extra, server)

        self._loop.call_soon(self._loop_reading)
        self._paused = Uongo

    eleza is_reading(self):
        rudisha sio self._paused na sio self._closing

    eleza pause_reading(self):
        ikiwa self._closing ama self._paused:
            rudisha
        self._paused = Kweli

        # bpo-33694: Don't cancel self._read_fut because cancelling an
        # overlapped WSASend() loss silently data ukijumuisha the current proactor
        # implementation.
        #
        # If CancelIoEx() fails ukijumuisha ERROR_NOT_FOUND, it means that WSASend()
        # completed (even ikiwa HasOverlappedIoCompleted() rudishas 0), but
        # Overlapped.cancel() currently silently ignores the ERROR_NOT_FOUND
        # error. Once the overlapped ni ignored, the IOCP loop will ignores the
        # completion I/O event na so sio read the result of the overlapped
        # WSARecv().

        ikiwa self._loop.get_debug():
            logger.debug("%r pauses reading", self)

    eleza resume_reading(self):
        ikiwa self._closing ama sio self._paused:
            rudisha

        self._paused = Uongo
        ikiwa self._read_fut ni Tupu:
            self._loop.call_soon(self._loop_reading, Tupu)

        data = self._pending_data
        self._pending_data = Tupu
        ikiwa data ni sio Tupu:
            # Call the protocol methode after calling _loop_reading(),
            # since the protocol can decide to pause reading again.
            self._loop.call_soon(self._data_received, data)

        ikiwa self._loop.get_debug():
            logger.debug("%r resumes reading", self)

    eleza _eof_received(self):
        ikiwa self._loop.get_debug():
            logger.debug("%r received EOF", self)

        jaribu:
            keep_open = self._protocol.eof_received()
        tatizo (SystemExit, KeyboardInterrupt):
            ashiria
        tatizo BaseException kama exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.eof_received() call failed.')
            rudisha

        ikiwa sio keep_open:
            self.close()

    eleza _data_received(self, data):
        ikiwa self._paused:
            # Don't call any protocol method wakati reading ni paused.
            # The protocol will be called on resume_reading().
            assert self._pending_data ni Tupu
            self._pending_data = data
            rudisha

        ikiwa sio data:
            self._eof_received()
            rudisha

        ikiwa isinstance(self._protocol, protocols.BufferedProtocol):
            jaribu:
                protocols._feed_data_to_buffered_proto(self._protocol, data)
            tatizo (SystemExit, KeyboardInterrupt):
                ashiria
            tatizo BaseException kama exc:
                self._fatal_error(exc,
                                  'Fatal error: protocol.buffer_updated() '
                                  'call failed.')
                rudisha
        isipokua:
            self._protocol.data_received(data)

    eleza _loop_reading(self, fut=Tupu):
        data = Tupu
        jaribu:
            ikiwa fut ni sio Tupu:
                assert self._read_fut ni fut ama (self._read_fut ni Tupu and
                                                 self._closing)
                self._read_fut = Tupu
                ikiwa fut.done():
                    # deliver data later kwenye "finally" clause
                    data = fut.result()
                isipokua:
                    # the future will be replaced by next proactor.recv call
                    fut.cancel()

            ikiwa self._closing:
                # since close() has been called we ignore any read data
                data = Tupu
                rudisha

            ikiwa data == b'':
                # we got end-of-file so no need to reschedule a new read
                rudisha

            # bpo-33694: buffer_updated() has currently no fast path because of
            # a data loss issue caused by overlapped WSASend() cancellation.

            ikiwa sio self._paused:
                # reschedule a new read
                self._read_fut = self._loop._proactor.recv(self._sock, 32768)
        tatizo ConnectionAbortedError kama exc:
            ikiwa sio self._closing:
                self._fatal_error(exc, 'Fatal read error on pipe transport')
            lasivyo self._loop.get_debug():
                logger.debug("Read error on pipe transport wakati closing",
                             exc_info=Kweli)
        tatizo ConnectionResetError kama exc:
            self._force_close(exc)
        tatizo OSError kama exc:
            self._fatal_error(exc, 'Fatal read error on pipe transport')
        tatizo exceptions.CancelledError:
            ikiwa sio self._closing:
                ashiria
        isipokua:
            ikiwa sio self._paused:
                self._read_fut.add_done_callback(self._loop_reading)
        mwishowe:
            ikiwa data ni sio Tupu:
                self._data_received(data)


kundi _ProactorBaseWritePipeTransport(_ProactorBasePipeTransport,
                                      transports.WriteTransport):
    """Transport kila write pipes."""

    _start_tls_compatible = Kweli

    eleza __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._empty_waiter = Tupu

    eleza write(self, data):
        ikiwa sio isinstance(data, (bytes, bytearray, memoryview)):
            ashiria TypeError(
                f"data argument must be a bytes-like object, "
                f"not {type(data).__name__}")
        ikiwa self._eof_written:
            ashiria RuntimeError('write_eof() already called')
        ikiwa self._empty_waiter ni sio Tupu:
            ashiria RuntimeError('unable to write; sendfile ni kwenye progress')

        ikiwa sio data:
            rudisha

        ikiwa self._conn_lost:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() ashiriad exception.')
            self._conn_lost += 1
            rudisha

        # Observable states:
        # 1. IDLE: _write_fut na _buffer both Tupu
        # 2. WRITING: _write_fut set; _buffer Tupu
        # 3. BACKED UP: _write_fut set; _buffer a bytearray
        # We always copy the data, so the caller can't modify it
        # wakati we're still waiting kila the I/O to happen.
        ikiwa self._write_fut ni Tupu:  # IDLE -> WRITING
            assert self._buffer ni Tupu
            # Pass a copy, tatizo ikiwa it's already immutable.
            self._loop_writing(data=bytes(data))
        lasivyo sio self._buffer:  # WRITING -> BACKED UP
            # Make a mutable copy which we can extend.
            self._buffer = bytearray(data)
            self._maybe_pause_protocol()
        isipokua:  # BACKED UP
            # Append to buffer (also copies).
            self._buffer.extend(data)
            self._maybe_pause_protocol()

    eleza _loop_writing(self, f=Tupu, data=Tupu):
        jaribu:
            ikiwa f ni sio Tupu na self._write_fut ni Tupu na self._closing:
                # XXX most likely self._force_close() has been called, and
                # it has set self._write_fut to Tupu.
                rudisha
            assert f ni self._write_fut
            self._write_fut = Tupu
            self._pending_write = 0
            ikiwa f:
                f.result()
            ikiwa data ni Tupu:
                data = self._buffer
                self._buffer = Tupu
            ikiwa sio data:
                ikiwa self._closing:
                    self._loop.call_soon(self._call_connection_lost, Tupu)
                ikiwa self._eof_written:
                    self._sock.shutdown(socket.SHUT_WR)
                # Now that we've reduced the buffer size, tell the
                # protocol to resume writing ikiwa it was paused.  Note that
                # we do this last since the callback ni called immediately
                # na it may add more data to the buffer (even causing the
                # protocol to be paused again).
                self._maybe_resume_protocol()
            isipokua:
                self._write_fut = self._loop._proactor.send(self._sock, data)
                ikiwa sio self._write_fut.done():
                    assert self._pending_write == 0
                    self._pending_write = len(data)
                    self._write_fut.add_done_callback(self._loop_writing)
                    self._maybe_pause_protocol()
                isipokua:
                    self._write_fut.add_done_callback(self._loop_writing)
            ikiwa self._empty_waiter ni sio Tupu na self._write_fut ni Tupu:
                self._empty_waiter.set_result(Tupu)
        tatizo ConnectionResetError kama exc:
            self._force_close(exc)
        tatizo OSError kama exc:
            self._fatal_error(exc, 'Fatal write error on pipe transport')

    eleza can_write_eof(self):
        rudisha Kweli

    eleza write_eof(self):
        self.close()

    eleza abort(self):
        self._force_close(Tupu)

    eleza _make_empty_waiter(self):
        ikiwa self._empty_waiter ni sio Tupu:
            ashiria RuntimeError("Empty waiter ni already set")
        self._empty_waiter = self._loop.create_future()
        ikiwa self._write_fut ni Tupu:
            self._empty_waiter.set_result(Tupu)
        rudisha self._empty_waiter

    eleza _reset_empty_waiter(self):
        self._empty_waiter = Tupu


kundi _ProactorWritePipeTransport(_ProactorBaseWritePipeTransport):
    eleza __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._read_fut = self._loop._proactor.recv(self._sock, 16)
        self._read_fut.add_done_callback(self._pipe_closed)

    eleza _pipe_closed(self, fut):
        ikiwa fut.cancelled():
            # the transport has been closed
            rudisha
        assert fut.result() == b''
        ikiwa self._closing:
            assert self._read_fut ni Tupu
            rudisha
        assert fut ni self._read_fut, (fut, self._read_fut)
        self._read_fut = Tupu
        ikiwa self._write_fut ni sio Tupu:
            self._force_close(BrokenPipeError())
        isipokua:
            self.close()


kundi _ProactorDatagramTransport(_ProactorBasePipeTransport):
    max_size = 256 * 1024
    eleza __init__(self, loop, sock, protocol, address=Tupu,
                 waiter=Tupu, extra=Tupu):
        self._address = address
        self._empty_waiter = Tupu
        # We don't need to call _protocol.connection_made() since our base
        # constructor does it kila us.
        super().__init__(loop, sock, protocol, waiter=waiter, extra=extra)

        # The base constructor sets _buffer = Tupu, so we set it here
        self._buffer = collections.deque()
        self._loop.call_soon(self._loop_reading)

    eleza _set_extra(self, sock):
        _set_socket_extra(self, sock)

    eleza get_write_buffer_size(self):
        rudisha sum(len(data) kila data, _ kwenye self._buffer)

    eleza abort(self):
        self._force_close(Tupu)

    eleza sendto(self, data, addr=Tupu):
        ikiwa sio isinstance(data, (bytes, bytearray, memoryview)):
            ashiria TypeError('data argument must be bytes-like object (%r)',
                            type(data))

        ikiwa sio data:
            rudisha

        ikiwa self._address ni sio Tupu na addr haiko kwenye (Tupu, self._address):
            ashiria ValueError(
                f'Invalid address: must be Tupu ama {self._address}')

        ikiwa self._conn_lost na self._address:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.sendto() ashiriad exception.')
            self._conn_lost += 1
            rudisha

        # Ensure that what we buffer ni immutable.
        self._buffer.append((bytes(data), addr))

        ikiwa self._write_fut ni Tupu:
            # No current write operations are active, kick one off
            self._loop_writing()
        # isipokua: A write operation ni already kicked off

        self._maybe_pause_protocol()

    eleza _loop_writing(self, fut=Tupu):
        jaribu:
            ikiwa self._conn_lost:
                rudisha

            assert fut ni self._write_fut
            self._write_fut = Tupu
            ikiwa fut:
                # We are kwenye a _loop_writing() done callback, get the result
                fut.result()

            ikiwa sio self._buffer ama (self._conn_lost na self._address):
                # The connection has been closed
                ikiwa self._closing:
                    self._loop.call_soon(self._call_connection_lost, Tupu)
                rudisha

            data, addr = self._buffer.popleft()
            ikiwa self._address ni sio Tupu:
                self._write_fut = self._loop._proactor.send(self._sock,
                                                            data)
            isipokua:
                self._write_fut = self._loop._proactor.sendto(self._sock,
                                                              data,
                                                              addr=addr)
        tatizo OSError kama exc:
            self._protocol.error_received(exc)
        tatizo Exception kama exc:
            self._fatal_error(exc, 'Fatal write error on datagram transport')
        isipokua:
            self._write_fut.add_done_callback(self._loop_writing)
            self._maybe_resume_protocol()

    eleza _loop_reading(self, fut=Tupu):
        data = Tupu
        jaribu:
            ikiwa self._conn_lost:
                rudisha

            assert self._read_fut ni fut ama (self._read_fut ni Tupu and
                                             self._closing)

            self._read_fut = Tupu
            ikiwa fut ni sio Tupu:
                res = fut.result()

                ikiwa self._closing:
                    # since close() has been called we ignore any read data
                    data = Tupu
                    rudisha

                ikiwa self._address ni sio Tupu:
                    data, addr = res, self._address
                isipokua:
                    data, addr = res

            ikiwa self._conn_lost:
                rudisha
            ikiwa self._address ni sio Tupu:
                self._read_fut = self._loop._proactor.recv(self._sock,
                                                           self.max_size)
            isipokua:
                self._read_fut = self._loop._proactor.recvkutoka(self._sock,
                                                               self.max_size)
        tatizo OSError kama exc:
            self._protocol.error_received(exc)
        tatizo exceptions.CancelledError:
            ikiwa sio self._closing:
                ashiria
        isipokua:
            ikiwa self._read_fut ni sio Tupu:
                self._read_fut.add_done_callback(self._loop_reading)
        mwishowe:
            ikiwa data:
                self._protocol.datagram_received(data, addr)


kundi _ProactorDuplexPipeTransport(_ProactorReadPipeTransport,
                                   _ProactorBaseWritePipeTransport,
                                   transports.Transport):
    """Transport kila duplex pipes."""

    eleza can_write_eof(self):
        rudisha Uongo

    eleza write_eof(self):
        ashiria NotImplementedError


kundi _ProactorSocketTransport(_ProactorReadPipeTransport,
                               _ProactorBaseWritePipeTransport,
                               transports.Transport):
    """Transport kila connected sockets."""

    _sendfile_compatible = constants._SendfileMode.TRY_NATIVE

    eleza __init__(self, loop, sock, protocol, waiter=Tupu,
                 extra=Tupu, server=Tupu):
        super().__init__(loop, sock, protocol, waiter, extra, server)
        base_events._set_nodelay(sock)

    eleza _set_extra(self, sock):
        _set_socket_extra(self, sock)

    eleza can_write_eof(self):
        rudisha Kweli

    eleza write_eof(self):
        ikiwa self._closing ama self._eof_written:
            rudisha
        self._eof_written = Kweli
        ikiwa self._write_fut ni Tupu:
            self._sock.shutdown(socket.SHUT_WR)


kundi BaseProactorEventLoop(base_events.BaseEventLoop):

    eleza __init__(self, proactor):
        super().__init__()
        logger.debug('Using proactor: %s', proactor.__class__.__name__)
        self._proactor = proactor
        self._selector = proactor   # convenient alias
        self._self_reading_future = Tupu
        self._accept_futures = {}   # socket file descriptor => Future
        proactor.set_loop(self)
        self._make_self_pipe()
        self_no = self._csock.fileno()
        ikiwa threading.current_thread() ni threading.main_thread():
            # wakeup fd can only be installed to a file descriptor kutoka the main thread
            signal.set_wakeup_fd(self_no)

    eleza _make_socket_transport(self, sock, protocol, waiter=Tupu,
                               extra=Tupu, server=Tupu):
        rudisha _ProactorSocketTransport(self, sock, protocol, waiter,
                                        extra, server)

    eleza _make_ssl_transport(
            self, rawsock, protocol, sslcontext, waiter=Tupu,
            *, server_side=Uongo, server_hostname=Tupu,
            extra=Tupu, server=Tupu,
            ssl_handshake_timeout=Tupu):
        ssl_protocol = sslproto.SSLProtocol(
                self, protocol, sslcontext, waiter,
                server_side, server_hostname,
                ssl_handshake_timeout=ssl_handshake_timeout)
        _ProactorSocketTransport(self, rawsock, ssl_protocol,
                                 extra=extra, server=server)
        rudisha ssl_protocol._app_transport

    eleza _make_datagram_transport(self, sock, protocol,
                                 address=Tupu, waiter=Tupu, extra=Tupu):
        rudisha _ProactorDatagramTransport(self, sock, protocol, address,
                                          waiter, extra)

    eleza _make_duplex_pipe_transport(self, sock, protocol, waiter=Tupu,
                                    extra=Tupu):
        rudisha _ProactorDuplexPipeTransport(self,
                                            sock, protocol, waiter, extra)

    eleza _make_read_pipe_transport(self, sock, protocol, waiter=Tupu,
                                  extra=Tupu):
        rudisha _ProactorReadPipeTransport(self, sock, protocol, waiter, extra)

    eleza _make_write_pipe_transport(self, sock, protocol, waiter=Tupu,
                                   extra=Tupu):
        # We want connection_lost() to be called when other end closes
        rudisha _ProactorWritePipeTransport(self,
                                           sock, protocol, waiter, extra)

    eleza close(self):
        ikiwa self.is_running():
            ashiria RuntimeError("Cannot close a running event loop")
        ikiwa self.is_closed():
            rudisha

        signal.set_wakeup_fd(-1)
        # Call these methods before closing the event loop (before calling
        # BaseEventLoop.close), because they can schedule callbacks with
        # call_soon(), which ni forbidden when the event loop ni closed.
        self._stop_accept_futures()
        self._close_self_pipe()
        self._proactor.close()
        self._proactor = Tupu
        self._selector = Tupu

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

        blocksize = min(blocksize, 0xffff_ffff)
        end_pos = min(offset + count, fsize) ikiwa count isipokua fsize
        offset = min(offset, fsize)
        total_sent = 0
        jaribu:
            wakati Kweli:
                blocksize = min(end_pos - offset, blocksize)
                ikiwa blocksize <= 0:
                    rudisha total_sent
                await self._proactor.sendfile(sock, file, offset, blocksize)
                offset += blocksize
                total_sent += blocksize
        mwishowe:
            ikiwa total_sent > 0:
                file.seek(offset)

    async eleza _sendfile_native(self, transp, file, offset, count):
        resume_reading = transp.is_reading()
        transp.pause_reading()
        await transp._make_empty_waiter()
        jaribu:
            rudisha await self.sock_sendfile(transp._sock, file, offset, count,
                                            fallback=Uongo)
        mwishowe:
            transp._reset_empty_waiter()
            ikiwa resume_reading:
                transp.resume_reading()

    eleza _close_self_pipe(self):
        ikiwa self._self_reading_future ni sio Tupu:
            self._self_reading_future.cancel()
            self._self_reading_future = Tupu
        self._ssock.close()
        self._ssock = Tupu
        self._csock.close()
        self._csock = Tupu
        self._internal_fds -= 1

    eleza _make_self_pipe(self):
        # A self-socket, really. :-)
        self._ssock, self._csock = socket.socketpair()
        self._ssock.setblocking(Uongo)
        self._csock.setblocking(Uongo)
        self._internal_fds += 1

    eleza _loop_self_reading(self, f=Tupu):
        jaribu:
            ikiwa f ni sio Tupu:
                f.result()  # may ashiria
            f = self._proactor.recv(self._ssock, 4096)
        tatizo exceptions.CancelledError:
            # _close_self_pipe() has been called, stop waiting kila data
            rudisha
        tatizo (SystemExit, KeyboardInterrupt):
            ashiria
        tatizo BaseException kama exc:
            self.call_exception_handler({
                'message': 'Error on reading kutoka the event loop self pipe',
                'exception': exc,
                'loop': self,
            })
        isipokua:
            self._self_reading_future = f
            f.add_done_callback(self._loop_self_reading)

    eleza _write_to_self(self):
        jaribu:
            self._csock.send(b'\0')
        tatizo OSError:
            ikiwa self._debug:
                logger.debug("Fail to write a null byte into the "
                             "self-pipe socket",
                             exc_info=Kweli)

    eleza _start_serving(self, protocol_factory, sock,
                       sslcontext=Tupu, server=Tupu, backlog=100,
                       ssl_handshake_timeout=Tupu):

        eleza loop(f=Tupu):
            jaribu:
                ikiwa f ni sio Tupu:
                    conn, addr = f.result()
                    ikiwa self._debug:
                        logger.debug("%r got a new connection kutoka %r: %r",
                                     server, addr, conn)
                    protocol = protocol_factory()
                    ikiwa sslcontext ni sio Tupu:
                        self._make_ssl_transport(
                            conn, protocol, sslcontext, server_side=Kweli,
                            extra={'peername': addr}, server=server,
                            ssl_handshake_timeout=ssl_handshake_timeout)
                    isipokua:
                        self._make_socket_transport(
                            conn, protocol,
                            extra={'peername': addr}, server=server)
                ikiwa self.is_closed():
                    rudisha
                f = self._proactor.accept(sock)
            tatizo OSError kama exc:
                ikiwa sock.fileno() != -1:
                    self.call_exception_handler({
                        'message': 'Accept failed on a socket',
                        'exception': exc,
                        'socket': trsock.TransportSocket(sock),
                    })
                    sock.close()
                lasivyo self._debug:
                    logger.debug("Accept failed on socket %r",
                                 sock, exc_info=Kweli)
            tatizo exceptions.CancelledError:
                sock.close()
            isipokua:
                self._accept_futures[sock.fileno()] = f
                f.add_done_callback(loop)

        self.call_soon(loop)

    eleza _process_events(self, event_list):
        # Events are processed kwenye the IocpProactor._poll() method
        pita

    eleza _stop_accept_futures(self):
        kila future kwenye self._accept_futures.values():
            future.cancel()
        self._accept_futures.clear()

    eleza _stop_serving(self, sock):
        future = self._accept_futures.pop(sock.fileno(), Tupu)
        ikiwa future:
            future.cancel()
        self._proactor._stop_serving(sock)
        sock.close()
