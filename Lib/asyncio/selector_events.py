"""Event loop using a selector na related classes.

A selector ni a "notify-when-ready" multiplexer.  For a subkundi which
also includes support kila signal handling, see the unix_events sub-module.
"""

__all__ = 'BaseSelectorEventLoop',

agiza collections
agiza errno
agiza functools
agiza selectors
agiza socket
agiza warnings
agiza weakref
jaribu:
    agiza ssl
except ImportError:  # pragma: no cover
    ssl = Tupu

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
    # Test ikiwa the selector ni monitoring 'event' events
    # kila the file descriptor 'fd'.
    jaribu:
        key = selector.get_key(fd)
    except KeyError:
        rudisha Uongo
    isipokua:
        rudisha bool(key.events & event)


kundi BaseSelectorEventLoop(base_events.BaseEventLoop):
    """Selector event loop.

    See events.EventLoop kila API specification.
    """

    eleza __init__(self, selector=Tupu):
        super().__init__()

        ikiwa selector ni Tupu:
            selector = selectors.DefaultSelector()
        logger.debug('Using selector: %s', selector.__class__.__name__)
        self._selector = selector
        self._make_self_pipe()
        self._transports = weakref.WeakValueDictionary()

    eleza _make_socket_transport(self, sock, protocol, waiter=Tupu, *,
                               extra=Tupu, server=Tupu):
        rudisha _SelectorSocketTransport(self, sock, protocol, waiter,
                                        extra, server)

    eleza _make_ssl_transport(
            self, rawsock, protocol, sslcontext, waiter=Tupu,
            *, server_side=Uongo, server_hostname=Tupu,
            extra=Tupu, server=Tupu,
            ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT):
        ssl_protocol = sslproto.SSLProtocol(
                self, protocol, sslcontext, waiter,
                server_side, server_hostname,
                ssl_handshake_timeout=ssl_handshake_timeout)
        _SelectorSocketTransport(self, rawsock, ssl_protocol,
                                 extra=extra, server=server)
        rudisha ssl_protocol._app_transport

    eleza _make_datagram_transport(self, sock, protocol,
                                 address=Tupu, waiter=Tupu, extra=Tupu):
        rudisha _SelectorDatagramTransport(self, sock, protocol,
                                          address, waiter, extra)

    eleza close(self):
        ikiwa self.is_running():
             ashiria RuntimeError("Cannot close a running event loop")
        ikiwa self.is_closed():
            return
        self._close_self_pipe()
        super().close()
        ikiwa self._selector ni sio Tupu:
            self._selector.close()
            self._selector = Tupu

    eleza _close_self_pipe(self):
        self._remove_reader(self._ssock.fileno())
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
        self._add_reader(self._ssock.fileno(), self._read_from_self)

    eleza _process_self_data(self, data):
        pass

    eleza _read_from_self(self):
        wakati Kweli:
            jaribu:
                data = self._ssock.recv(4096)
                ikiwa sio data:
                    koma
                self._process_self_data(data)
            except InterruptedError:
                endelea
            except BlockingIOError:
                koma

    eleza _write_to_self(self):
        # This may be called kutoka a different thread, possibly after
        # _close_self_pipe() has been called ama even wakati it is
        # running.  Guard kila self._csock being Tupu ama closed.  When
        # a socket ni closed, send() raises OSError (ukijumuisha errno set to
        # EBADF, but let's sio rely on the exact error code).
        csock = self._csock
        ikiwa csock ni sio Tupu:
            jaribu:
                csock.send(b'\0')
            except OSError:
                ikiwa self._debug:
                    logger.debug("Fail to write a null byte into the "
                                 "self-pipe socket",
                                 exc_info=Kweli)

    eleza _start_serving(self, protocol_factory, sock,
                       sslcontext=Tupu, server=Tupu, backlog=100,
                       ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT):
        self._add_reader(sock.fileno(), self._accept_connection,
                         protocol_factory, sock, sslcontext, server, backlog,
                         ssl_handshake_timeout)

    eleza _accept_connection(
            self, protocol_factory, sock,
            sslcontext=Tupu, server=Tupu, backlog=100,
            ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT):
        # This method ni only called once kila each event loop tick where the
        # listening socket has triggered an EVENT_READ. There may be multiple
        # connections waiting kila an .accept() so it ni called kwenye a loop.
        # See https://bugs.python.org/issue27906 kila more details.
        kila _ kwenye range(backlog):
            jaribu:
                conn, addr = sock.accept()
                ikiwa self._debug:
                    logger.debug("%r got a new connection kutoka %r: %r",
                                 server, addr, conn)
                conn.setblocking(Uongo)
            except (BlockingIOError, InterruptedError, ConnectionAbortedError):
                # Early exit because the socket accept buffer ni empty.
                rudisha Tupu
            except OSError as exc:
                # There's nowhere to send the error, so just log it.
                ikiwa exc.errno kwenye (errno.EMFILE, errno.ENFILE,
                                 errno.ENOBUFS, errno.ENOMEM):
                    # Some platforms (e.g. Linux keep reporting the FD as
                    # ready, so we remove the read handler temporarily.
                    # We'll try again kwenye a while.
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
                isipokua:
                     ashiria  # The event loop will catch, log na ignore it.
            isipokua:
                extra = {'peername': addr}
                accept = self._accept_connection2(
                    protocol_factory, conn, extra, sslcontext, server,
                    ssl_handshake_timeout)
                self.create_task(accept)

    async eleza _accept_connection2(
            self, protocol_factory, conn, extra,
            sslcontext=Tupu, server=Tupu,
            ssl_handshake_timeout=constants.SSL_HANDSHAKE_TIMEOUT):
        protocol = Tupu
        transport = Tupu
        jaribu:
            protocol = protocol_factory()
            waiter = self.create_future()
            ikiwa sslcontext:
                transport = self._make_ssl_transport(
                    conn, protocol, sslcontext, waiter=waiter,
                    server_side=Kweli, extra=extra, server=server,
                    ssl_handshake_timeout=ssl_handshake_timeout)
            isipokua:
                transport = self._make_socket_transport(
                    conn, protocol, waiter=waiter, extra=extra,
                    server=server)

            jaribu:
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
                        'Error on transport creation kila incoming connection',
                    'exception': exc,
                }
                ikiwa protocol ni sio Tupu:
                    context['protocol'] = protocol
                ikiwa transport ni sio Tupu:
                    context['transport'] = transport
                self.call_exception_handler(context)

    eleza _ensure_fd_no_transport(self, fd):
        fileno = fd
        ikiwa sio isinstance(fileno, int):
            jaribu:
                fileno = int(fileno.fileno())
            except (AttributeError, TypeError, ValueError):
                # This code matches selectors._fileobj_to_fd function.
                 ashiria ValueError(f"Invalid file object: {fd!r}") kutoka Tupu
        jaribu:
            transport = self._transports[fileno]
        except KeyError:
            pass
        isipokua:
            ikiwa sio transport.is_closing():
                 ashiria RuntimeError(
                    f'File descriptor {fd!r} ni used by transport '
                    f'{transport!r}')

    eleza _add_reader(self, fd, callback, *args):
        self._check_closed()
        handle = events.Handle(callback, args, self, Tupu)
        jaribu:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_READ,
                                    (handle, Tupu))
        isipokua:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_READ,
                                  (handle, writer))
            ikiwa reader ni sio Tupu:
                reader.cancel()

    eleza _remove_reader(self, fd):
        ikiwa self.is_closed():
            rudisha Uongo
        jaribu:
            key = self._selector.get_key(fd)
        except KeyError:
            rudisha Uongo
        isipokua:
            mask, (reader, writer) = key.events, key.data
            mask &= ~selectors.EVENT_READ
            ikiwa sio mask:
                self._selector.unregister(fd)
            isipokua:
                self._selector.modify(fd, mask, (Tupu, writer))

            ikiwa reader ni sio Tupu:
                reader.cancel()
                rudisha Kweli
            isipokua:
                rudisha Uongo

    eleza _add_writer(self, fd, callback, *args):
        self._check_closed()
        handle = events.Handle(callback, args, self, Tupu)
        jaribu:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_WRITE,
                                    (Tupu, handle))
        isipokua:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_WRITE,
                                  (reader, handle))
            ikiwa writer ni sio Tupu:
                writer.cancel()

    eleza _remove_writer(self, fd):
        """Remove a writer callback."""
        ikiwa self.is_closed():
            rudisha Uongo
        jaribu:
            key = self._selector.get_key(fd)
        except KeyError:
            rudisha Uongo
        isipokua:
            mask, (reader, writer) = key.events, key.data
            # Remove both writer na connector.
            mask &= ~selectors.EVENT_WRITE
            ikiwa sio mask:
                self._selector.unregister(fd)
            isipokua:
                self._selector.modify(fd, mask, (reader, Tupu))

            ikiwa writer ni sio Tupu:
                writer.cancel()
                rudisha Kweli
            isipokua:
                rudisha Uongo

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

        The rudisha value ni a bytes object representing the data received.
        The maximum amount of data to be received at once ni specified by
        nbytes.
        """
        ikiwa self._debug na sock.gettimeout() != 0:
             ashiria ValueError("the socket must be non-blocking")
        jaribu:
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
        jaribu:
            data = sock.recv(n)
        except (BlockingIOError, InterruptedError):
            rudisha  # try again next time
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        isipokua:
            fut.set_result(data)

    async eleza sock_recv_into(self, sock, buf):
        """Receive data kutoka the socket.

        The received data ni written into *buf* (a writable buffer).
        The rudisha value ni the number of bytes written.
        """
        ikiwa self._debug na sock.gettimeout() != 0:
             ashiria ValueError("the socket must be non-blocking")
        jaribu:
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
        jaribu:
            nbytes = sock.recv_into(buf)
        except (BlockingIOError, InterruptedError):
            rudisha  # try again next time
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        isipokua:
            fut.set_result(nbytes)

    async eleza sock_sendall(self, sock, data):
        """Send data to the socket.

        The socket must be connected to a remote socket. This method endeleas
        to send data kutoka data until either all data has been sent ama an
        error occurs. Tupu ni returned on success. On error, an exception is
        raised, na there ni no way to determine how much data, ikiwa any, was
        successfully processed by the receiving end of the connection.
        """
        ikiwa self._debug na sock.gettimeout() != 0:
             ashiria ValueError("the socket must be non-blocking")
        jaribu:
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
        # use a trick ukijumuisha a list kwenye closure to store a mutable state
        self.add_writer(fd, self._sock_sendall, fut, sock,
                        memoryview(data), [n])
        rudisha await fut

    eleza _sock_sendall(self, fut, sock, view, pos):
        ikiwa fut.done():
            # Future cancellation can be scheduled on previous loop iteration
            return
        start = pos[0]
        jaribu:
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
            fut.set_result(Tupu)
        isipokua:
            pos[0] = start

    async eleza sock_connect(self, sock, address):
        """Connect to a remote socket at address.

        This method ni a coroutine.
        """
        ikiwa self._debug na sock.gettimeout() != 0:
             ashiria ValueError("the socket must be non-blocking")

        ikiwa sio hasattr(socket, 'AF_UNIX') ama sock.family != socket.AF_UNIX:
            resolved = await self._ensure_resolved(
                address, family=sock.family, proto=sock.proto, loop=self)
            _, _, _, _, address = resolved[0]

        fut = self.create_future()
        self._sock_connect(fut, sock, address)
        rudisha await fut

    eleza _sock_connect(self, fut, sock, address):
        fd = sock.fileno()
        jaribu:
            sock.connect(address)
        except (BlockingIOError, InterruptedError):
            # Issue #23618: When the C function connect() fails ukijumuisha EINTR, the
            # connection runs kwenye background. We have to wait until the socket
            # becomes writable to be notified when the connection succeed or
            # fails.
            fut.add_done_callback(
                functools.partial(self._sock_write_done, fd))
            self.add_writer(fd, self._sock_connect_cb, fut, sock, address)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        isipokua:
            fut.set_result(Tupu)

    eleza _sock_write_done(self, fd, fut):
        self.remove_writer(fd)

    eleza _sock_connect_cb(self, fut, sock, address):
        ikiwa fut.done():
            return

        jaribu:
            err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            ikiwa err != 0:
                # Jump to any except clause below.
                 ashiria OSError(err, f'Connect call failed {address}')
        except (BlockingIOError, InterruptedError):
            # socket ni still registered, the callback will be retried later
            pass
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        isipokua:
            fut.set_result(Tupu)

    async eleza sock_accept(self, sock):
        """Accept a connection.

        The socket must be bound to an address na listening kila connections.
        The rudisha value ni a pair (conn, address) where conn ni a new socket
        object usable to send na receive data on the connection, na address
        ni the address bound to the socket on the other end of the connection.
        """
        ikiwa self._debug na sock.gettimeout() != 0:
             ashiria ValueError("the socket must be non-blocking")
        fut = self.create_future()
        self._sock_accept(fut, Uongo, sock)
        rudisha await fut

    eleza _sock_accept(self, fut, registered, sock):
        fd = sock.fileno()
        ikiwa registered:
            self.remove_reader(fd)
        ikiwa fut.done():
            return
        jaribu:
            conn, address = sock.accept()
            conn.setblocking(Uongo)
        except (BlockingIOError, InterruptedError):
            self.add_reader(fd, self._sock_accept, fut, Kweli, sock)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            fut.set_exception(exc)
        isipokua:
            fut.set_result((conn, address))

    async eleza _sendfile_native(self, transp, file, offset, count):
        toa self._transports[transp._sock_fd]
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
            self._transports[transp._sock_fd] = transp

    eleza _process_events(self, event_list):
        kila key, mask kwenye event_list:
            fileobj, (reader, writer) = key.fileobj, key.data
            ikiwa mask & selectors.EVENT_READ na reader ni sio Tupu:
                ikiwa reader._cancelled:
                    self._remove_reader(fileobj)
                isipokua:
                    self._add_callback(reader)
            ikiwa mask & selectors.EVENT_WRITE na writer ni sio Tupu:
                ikiwa writer._cancelled:
                    self._remove_writer(fileobj)
                isipokua:
                    self._add_callback(writer)

    eleza _stop_serving(self, sock):
        self._remove_reader(sock.fileno())
        sock.close()


kundi _SelectorTransport(transports._FlowControlMixin,
                         transports.Transport):

    max_size = 256 * 1024  # Buffer size passed to recv().

    _buffer_factory = bytearray  # Constructs initial value kila self._buffer.

    # Attribute used kwenye the destructor: it must be set even ikiwa the constructor
    # ni sio called (see _SelectorSslTransport which may start by raising an
    # exception)
    _sock = Tupu

    eleza __init__(self, loop, sock, protocol, extra=Tupu, server=Tupu):
        super().__init__(extra, loop)
        self._extra['socket'] = trsock.TransportSocket(sock)
        jaribu:
            self._extra['sockname'] = sock.getsockname()
        except OSError:
            self._extra['sockname'] = Tupu
        ikiwa 'peername' sio kwenye self._extra:
            jaribu:
                self._extra['peername'] = sock.getpeername()
            except socket.error:
                self._extra['peername'] = Tupu
        self._sock = sock
        self._sock_fd = sock.fileno()

        self._protocol_connected = Uongo
        self.set_protocol(protocol)

        self._server = server
        self._buffer = self._buffer_factory()
        self._conn_lost = 0  # Set when call to connection_lost scheduled.
        self._closing = Uongo  # Set when close() called.
        ikiwa self._server ni sio Tupu:
            self._server._attach()
        loop._transports[self._sock_fd] = self

    eleza __repr__(self):
        info = [self.__class__.__name__]
        ikiwa self._sock ni Tupu:
            info.append('closed')
        elikiwa self._closing:
            info.append('closing')
        info.append(f'fd={self._sock_fd}')
        # test ikiwa the transport was closed
        ikiwa self._loop ni sio Tupu na sio self._loop.is_closed():
            polling = _test_selector_event(self._loop._selector,
                                           self._sock_fd, selectors.EVENT_READ)
            ikiwa polling:
                info.append('read=polling')
            isipokua:
                info.append('read=idle')

            polling = _test_selector_event(self._loop._selector,
                                           self._sock_fd,
                                           selectors.EVENT_WRITE)
            ikiwa polling:
                state = 'polling'
            isipokua:
                state = 'idle'

            bufsize = self.get_write_buffer_size()
            info.append(f'write=<{state}, bufsize={bufsize}>')
        rudisha '<{}>'.format(' '.join(info))

    eleza abort(self):
        self._force_close(Tupu)

    eleza set_protocol(self, protocol):
        self._protocol = protocol
        self._protocol_connected = Kweli

    eleza get_protocol(self):
        rudisha self._protocol

    eleza is_closing(self):
        rudisha self._closing

    eleza close(self):
        ikiwa self._closing:
            return
        self._closing = Kweli
        self._loop._remove_reader(self._sock_fd)
        ikiwa sio self._buffer:
            self._conn_lost += 1
            self._loop._remove_writer(self._sock_fd)
            self._loop.call_soon(self._call_connection_lost, Tupu)

    eleza __del__(self, _warn=warnings.warn):
        ikiwa self._sock ni sio Tupu:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self._sock.close()

    eleza _fatal_error(self, exc, message='Fatal error on transport'):
        # Should be called kutoka exception handler only.
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
        self._force_close(exc)

    eleza _force_close(self, exc):
        ikiwa self._conn_lost:
            return
        ikiwa self._buffer:
            self._buffer.clear()
            self._loop._remove_writer(self._sock_fd)
        ikiwa sio self._closing:
            self._closing = Kweli
            self._loop._remove_reader(self._sock_fd)
        self._conn_lost += 1
        self._loop.call_soon(self._call_connection_lost, exc)

    eleza _call_connection_lost(self, exc):
        jaribu:
            ikiwa self._protocol_connected:
                self._protocol.connection_lost(exc)
        mwishowe:
            self._sock.close()
            self._sock = Tupu
            self._protocol = Tupu
            self._loop = Tupu
            server = self._server
            ikiwa server ni sio Tupu:
                server._detach()
                self._server = Tupu

    eleza get_write_buffer_size(self):
        rudisha len(self._buffer)

    eleza _add_reader(self, fd, callback, *args):
        ikiwa self._closing:
            return

        self._loop._add_reader(fd, callback, *args)


kundi _SelectorSocketTransport(_SelectorTransport):

    _start_tls_compatible = Kweli
    _sendfile_compatible = constants._SendfileMode.TRY_NATIVE

    eleza __init__(self, loop, sock, protocol, waiter=Tupu,
                 extra=Tupu, server=Tupu):

        self._read_ready_cb = Tupu
        super().__init__(loop, sock, protocol, extra, server)
        self._eof = Uongo
        self._paused = Uongo
        self._empty_waiter = Tupu

        # Disable the Nagle algorithm -- small writes will be
        # sent without waiting kila the TCP ACK.  This generally
        # decreases the latency (in some cases significantly.)
        base_events._set_nodelay(self._sock)

        self._loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        self._loop.call_soon(self._add_reader,
                             self._sock_fd, self._read_ready)
        ikiwa waiter ni sio Tupu:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(futures._set_result_unless_cancelled,
                                 waiter, Tupu)

    eleza set_protocol(self, protocol):
        ikiwa isinstance(protocol, protocols.BufferedProtocol):
            self._read_ready_cb = self._read_ready__get_buffer
        isipokua:
            self._read_ready_cb = self._read_ready__data_received

        super().set_protocol(protocol)

    eleza is_reading(self):
        rudisha sio self._paused na sio self._closing

    eleza pause_reading(self):
        ikiwa self._closing ama self._paused:
            return
        self._paused = Kweli
        self._loop._remove_reader(self._sock_fd)
        ikiwa self._loop.get_debug():
            logger.debug("%r pauses reading", self)

    eleza resume_reading(self):
        ikiwa self._closing ama sio self._paused:
            return
        self._paused = Uongo
        self._add_reader(self._sock_fd, self._read_ready)
        ikiwa self._loop.get_debug():
            logger.debug("%r resumes reading", self)

    eleza _read_ready(self):
        self._read_ready_cb()

    eleza _read_ready__get_buffer(self):
        ikiwa self._conn_lost:
            return

        jaribu:
            buf = self._protocol.get_buffer(-1)
            ikiwa sio len(buf):
                 ashiria RuntimeError('get_buffer() returned an empty buffer')
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.get_buffer() call failed.')
            return

        jaribu:
            nbytes = self._sock.recv_into(buf)
        except (BlockingIOError, InterruptedError):
            return
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(exc, 'Fatal read error on socket transport')
            return

        ikiwa sio nbytes:
            self._read_ready__on_eof()
            return

        jaribu:
            self._protocol.buffer_updated(nbytes)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.buffer_updated() call failed.')

    eleza _read_ready__data_received(self):
        ikiwa self._conn_lost:
            return
        jaribu:
            data = self._sock.recv(self.max_size)
        except (BlockingIOError, InterruptedError):
            return
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(exc, 'Fatal read error on socket transport')
            return

        ikiwa sio data:
            self._read_ready__on_eof()
            return

        jaribu:
            self._protocol.data_received(data)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.data_received() call failed.')

    eleza _read_ready__on_eof(self):
        ikiwa self._loop.get_debug():
            logger.debug("%r received EOF", self)

        jaribu:
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
        isipokua:
            self.close()

    eleza write(self, data):
        ikiwa sio isinstance(data, (bytes, bytearray, memoryview)):
             ashiria TypeError(f'data argument must be a bytes-like object, '
                            f'not {type(data).__name__!r}')
        ikiwa self._eof:
             ashiria RuntimeError('Cannot call write() after write_eof()')
        ikiwa self._empty_waiter ni sio Tupu:
             ashiria RuntimeError('unable to write; sendfile ni kwenye progress')
        ikiwa sio data:
            return

        ikiwa self._conn_lost:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() raised exception.')
            self._conn_lost += 1
            return

        ikiwa sio self._buffer:
            # Optimization: try to send now.
            jaribu:
                n = self._sock.send(data)
            except (BlockingIOError, InterruptedError):
                pass
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                self._fatal_error(exc, 'Fatal write error on socket transport')
                return
            isipokua:
                data = data[n:]
                ikiwa sio data:
                    return
            # Not all was written; register write handler.
            self._loop._add_writer(self._sock_fd, self._write_ready)

        # Add it to the buffer.
        self._buffer.extend(data)
        self._maybe_pause_protocol()

    eleza _write_ready(self):
        assert self._buffer, 'Data should sio be empty'

        ikiwa self._conn_lost:
            return
        jaribu:
            n = self._sock.send(self._buffer)
        except (BlockingIOError, InterruptedError):
            pass
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._loop._remove_writer(self._sock_fd)
            self._buffer.clear()
            self._fatal_error(exc, 'Fatal write error on socket transport')
            ikiwa self._empty_waiter ni sio Tupu:
                self._empty_waiter.set_exception(exc)
        isipokua:
            ikiwa n:
                toa self._buffer[:n]
            self._maybe_resume_protocol()  # May append to buffer.
            ikiwa sio self._buffer:
                self._loop._remove_writer(self._sock_fd)
                ikiwa self._empty_waiter ni sio Tupu:
                    self._empty_waiter.set_result(Tupu)
                ikiwa self._closing:
                    self._call_connection_lost(Tupu)
                elikiwa self._eof:
                    self._sock.shutdown(socket.SHUT_WR)

    eleza write_eof(self):
        ikiwa self._closing ama self._eof:
            return
        self._eof = Kweli
        ikiwa sio self._buffer:
            self._sock.shutdown(socket.SHUT_WR)

    eleza can_write_eof(self):
        rudisha Kweli

    eleza _call_connection_lost(self, exc):
        super()._call_connection_lost(exc)
        ikiwa self._empty_waiter ni sio Tupu:
            self._empty_waiter.set_exception(
                ConnectionError("Connection ni closed by peer"))

    eleza _make_empty_waiter(self):
        ikiwa self._empty_waiter ni sio Tupu:
             ashiria RuntimeError("Empty waiter ni already set")
        self._empty_waiter = self._loop.create_future()
        ikiwa sio self._buffer:
            self._empty_waiter.set_result(Tupu)
        rudisha self._empty_waiter

    eleza _reset_empty_waiter(self):
        self._empty_waiter = Tupu


kundi _SelectorDatagramTransport(_SelectorTransport):

    _buffer_factory = collections.deque

    eleza __init__(self, loop, sock, protocol, address=Tupu,
                 waiter=Tupu, extra=Tupu):
        super().__init__(loop, sock, protocol, extra)
        self._address = address
        self._loop.call_soon(self._protocol.connection_made, self)
        # only start reading when connection_made() has been called
        self._loop.call_soon(self._add_reader,
                             self._sock_fd, self._read_ready)
        ikiwa waiter ni sio Tupu:
            # only wake up the waiter when connection_made() has been called
            self._loop.call_soon(futures._set_result_unless_cancelled,
                                 waiter, Tupu)

    eleza get_write_buffer_size(self):
        rudisha sum(len(data) kila data, _ kwenye self._buffer)

    eleza _read_ready(self):
        ikiwa self._conn_lost:
            return
        jaribu:
            data, addr = self._sock.recvfrom(self.max_size)
        except (BlockingIOError, InterruptedError):
            pass
        except OSError as exc:
            self._protocol.error_received(exc)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            self._fatal_error(exc, 'Fatal read error on datagram transport')
        isipokua:
            self._protocol.datagram_received(data, addr)

    eleza sendto(self, data, addr=Tupu):
        ikiwa sio isinstance(data, (bytes, bytearray, memoryview)):
             ashiria TypeError(f'data argument must be a bytes-like object, '
                            f'not {type(data).__name__!r}')
        ikiwa sio data:
            return

        ikiwa self._address:
            ikiwa addr sio kwenye (Tupu, self._address):
                 ashiria ValueError(
                    f'Invalid address: must be Tupu ama {self._address}')
            addr = self._address

        ikiwa self._conn_lost na self._address:
            ikiwa self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('socket.send() raised exception.')
            self._conn_lost += 1
            return

        ikiwa sio self._buffer:
            # Attempt to send it right away first.
            jaribu:
                ikiwa self._extra['peername']:
                    self._sock.send(data)
                isipokua:
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

        # Ensure that what we buffer ni immutable.
        self._buffer.append((bytes(data), addr))
        self._maybe_pause_protocol()

    eleza _sendto_ready(self):
        wakati self._buffer:
            data, addr = self._buffer.popleft()
            jaribu:
                ikiwa self._extra['peername']:
                    self._sock.send(data)
                isipokua:
                    self._sock.sendto(data, addr)
            except (BlockingIOError, InterruptedError):
                self._buffer.appendleft((data, addr))  # Try again later.
                koma
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
        ikiwa sio self._buffer:
            self._loop._remove_writer(self._sock_fd)
            ikiwa self._closing:
                self._call_connection_lost(Tupu)
