agiza collections
agiza warnings
jaribu:
    agiza ssl
except ImportError:  # pragma: no cover
    ssl = Tupu

kutoka . agiza base_events
kutoka . agiza constants
kutoka . agiza protocols
kutoka . agiza transports
kutoka .log agiza logger


eleza _create_transport_context(server_side, server_hostname):
    ikiwa server_side:
         ashiria ValueError('Server side SSL needs a valid SSLContext')

    # Client side may pass ssl=Kweli to use a default
    # context; kwenye that case the sslcontext passed ni Tupu.
    # The default ni secure kila client connections.
    # Python 3.4+: use up-to-date strong settings.
    sslcontext = ssl.create_default_context()
    ikiwa sio server_hostname:
        sslcontext.check_hostname = Uongo
    rudisha sslcontext


# States of an _SSLPipe.
_UNWRAPPED = "UNWRAPPED"
_DO_HANDSHAKE = "DO_HANDSHAKE"
_WRAPPED = "WRAPPED"
_SHUTDOWN = "SHUTDOWN"


kundi _SSLPipe(object):
    """An SSL "Pipe".

    An SSL pipe allows you to communicate ukijumuisha an SSL/TLS protocol instance
    through memory buffers. It can be used to implement a security layer kila an
    existing connection where you don't have access to the connection's file
    descriptor, ama kila some reason you don't want to use it.

    An SSL pipe can be kwenye "wrapped" na "unwrapped" mode. In unwrapped mode,
    data ni passed through untransformed. In wrapped mode, application level
    data ni encrypted to SSL record level data na vice versa. The SSL record
    level ni the lowest level kwenye the SSL protocol suite na ni what travels
    as-is over the wire.

    An SslPipe initially ni kwenye "unwrapped" mode. To start SSL, call
    do_handshake(). To shutdown SSL again, call unwrap().
    """

    max_size = 256 * 1024   # Buffer size passed to read()

    eleza __init__(self, context, server_side, server_hostname=Tupu):
        """
        The *context* argument specifies the ssl.SSLContext to use.

        The *server_side* argument indicates whether this ni a server side or
        client side transport.

        The optional *server_hostname* argument can be used to specify the
        hostname you are connecting to. You may only specify this parameter if
        the _ssl module supports Server Name Indication (SNI).
        """
        self._context = context
        self._server_side = server_side
        self._server_hostname = server_hostname
        self._state = _UNWRAPPED
        self._incoming = ssl.MemoryBIO()
        self._outgoing = ssl.MemoryBIO()
        self._sslobj = Tupu
        self._need_ssldata = Uongo
        self._handshake_cb = Tupu
        self._shutdown_cb = Tupu

    @property
    eleza context(self):
        """The SSL context passed to the constructor."""
        rudisha self._context

    @property
    eleza ssl_object(self):
        """The internal ssl.SSLObject instance.

        Return Tupu ikiwa the pipe ni sio wrapped.
        """
        rudisha self._sslobj

    @property
    eleza need_ssldata(self):
        """Whether more record level data ni needed to complete a handshake
        that ni currently kwenye progress."""
        rudisha self._need_ssldata

    @property
    eleza wrapped(self):
        """
        Whether a security layer ni currently kwenye effect.

        Return Uongo during handshake.
        """
        rudisha self._state == _WRAPPED

    eleza do_handshake(self, callback=Tupu):
        """Start the SSL handshake.

        Return a list of ssldata. A ssldata element ni a list of buffers

        The optional *callback* argument can be used to install a callback that
        will be called when the handshake ni complete. The callback will be
        called ukijumuisha Tupu ikiwa successful, isipokua an exception instance.
        """
        ikiwa self._state != _UNWRAPPED:
             ashiria RuntimeError('handshake kwenye progress ama completed')
        self._sslobj = self._context.wrap_bio(
            self._incoming, self._outgoing,
            server_side=self._server_side,
            server_hostname=self._server_hostname)
        self._state = _DO_HANDSHAKE
        self._handshake_cb = callback
        ssldata, appdata = self.feed_ssldata(b'', only_handshake=Kweli)
        assert len(appdata) == 0
        rudisha ssldata

    eleza shutdown(self, callback=Tupu):
        """Start the SSL shutdown sequence.

        Return a list of ssldata. A ssldata element ni a list of buffers

        The optional *callback* argument can be used to install a callback that
        will be called when the shutdown ni complete. The callback will be
        called without arguments.
        """
        ikiwa self._state == _UNWRAPPED:
             ashiria RuntimeError('no security layer present')
        ikiwa self._state == _SHUTDOWN:
             ashiria RuntimeError('shutdown kwenye progress')
        assert self._state kwenye (_WRAPPED, _DO_HANDSHAKE)
        self._state = _SHUTDOWN
        self._shutdown_cb = callback
        ssldata, appdata = self.feed_ssldata(b'')
        assert appdata == [] ama appdata == [b'']
        rudisha ssldata

    eleza feed_eof(self):
        """Send a potentially "ragged" EOF.

        This method will  ashiria an SSL_ERROR_EOF exception ikiwa the EOF is
        unexpected.
        """
        self._incoming.write_eof()
        ssldata, appdata = self.feed_ssldata(b'')
        assert appdata == [] ama appdata == [b'']

    eleza feed_ssldata(self, data, only_handshake=Uongo):
        """Feed SSL record level data into the pipe.

        The data must be a bytes instance. It ni OK to send an empty bytes
        instance. This can be used to get ssldata kila a handshake initiated by
        this endpoint.

        Return a (ssldata, appdata) tuple. The ssldata element ni a list of
        buffers containing SSL data that needs to be sent to the remote SSL.

        The appdata element ni a list of buffers containing plaintext data that
        needs to be forwarded to the application. The appdata list may contain
        an empty buffer indicating an SSL "close_notify" alert. This alert must
        be acknowledged by calling shutdown().
        """
        ikiwa self._state == _UNWRAPPED:
            # If unwrapped, pass plaintext data straight through.
            ikiwa data:
                appdata = [data]
            isipokua:
                appdata = []
            rudisha ([], appdata)

        self._need_ssldata = Uongo
        ikiwa data:
            self._incoming.write(data)

        ssldata = []
        appdata = []
        jaribu:
            ikiwa self._state == _DO_HANDSHAKE:
                # Call do_handshake() until it doesn't  ashiria anymore.
                self._sslobj.do_handshake()
                self._state = _WRAPPED
                ikiwa self._handshake_cb:
                    self._handshake_cb(Tupu)
                ikiwa only_handshake:
                    rudisha (ssldata, appdata)
                # Handshake done: execute the wrapped block

            ikiwa self._state == _WRAPPED:
                # Main state: read data kutoka SSL until close_notify
                wakati Kweli:
                    chunk = self._sslobj.read(self.max_size)
                    appdata.append(chunk)
                    ikiwa sio chunk:  # close_notify
                        koma

            elikiwa self._state == _SHUTDOWN:
                # Call shutdown() until it doesn't  ashiria anymore.
                self._sslobj.unwrap()
                self._sslobj = Tupu
                self._state = _UNWRAPPED
                ikiwa self._shutdown_cb:
                    self._shutdown_cb()

            elikiwa self._state == _UNWRAPPED:
                # Drain possible plaintext data after close_notify.
                appdata.append(self._incoming.read())
        except (ssl.SSLError, ssl.CertificateError) as exc:
            exc_errno = getattr(exc, 'errno', Tupu)
            ikiwa exc_errno sio kwenye (
                    ssl.SSL_ERROR_WANT_READ, ssl.SSL_ERROR_WANT_WRITE,
                    ssl.SSL_ERROR_SYSCALL):
                ikiwa self._state == _DO_HANDSHAKE na self._handshake_cb:
                    self._handshake_cb(exc)
                raise
            self._need_ssldata = (exc_errno == ssl.SSL_ERROR_WANT_READ)

        # Check kila record level data that needs to be sent back.
        # Happens kila the initial handshake na renegotiations.
        ikiwa self._outgoing.pending:
            ssldata.append(self._outgoing.read())
        rudisha (ssldata, appdata)

    eleza feed_appdata(self, data, offset=0):
        """Feed plaintext data into the pipe.

        Return an (ssldata, offset) tuple. The ssldata element ni a list of
        buffers containing record level data that needs to be sent to the
        remote SSL instance. The offset ni the number of plaintext bytes that
        were processed, which may be less than the length of data.

        NOTE: In case of short writes, this call MUST be retried ukijumuisha the SAME
        buffer passed into the *data* argument (i.e. the id() must be the
        same). This ni an OpenSSL requirement. A further particularity ni that
        a short write will always have offset == 0, because the _ssl module
        does sio enable partial writes. And even though the offset ni zero,
        there will still be encrypted data kwenye ssldata.
        """
        assert 0 <= offset <= len(data)
        ikiwa self._state == _UNWRAPPED:
            # pass through data kwenye unwrapped mode
            ikiwa offset < len(data):
                ssldata = [data[offset:]]
            isipokua:
                ssldata = []
            rudisha (ssldata, len(data))

        ssldata = []
        view = memoryview(data)
        wakati Kweli:
            self._need_ssldata = Uongo
            jaribu:
                ikiwa offset < len(view):
                    offset += self._sslobj.write(view[offset:])
            except ssl.SSLError as exc:
                # It ni sio allowed to call write() after unwrap() until the
                # close_notify ni acknowledged. We rudisha the condition to the
                # caller as a short write.
                exc_errno = getattr(exc, 'errno', Tupu)
                ikiwa exc.reason == 'PROTOCOL_IS_SHUTDOWN':
                    exc_errno = exc.errno = ssl.SSL_ERROR_WANT_READ
                ikiwa exc_errno sio kwenye (ssl.SSL_ERROR_WANT_READ,
                                     ssl.SSL_ERROR_WANT_WRITE,
                                     ssl.SSL_ERROR_SYSCALL):
                    raise
                self._need_ssldata = (exc_errno == ssl.SSL_ERROR_WANT_READ)

            # See ikiwa there's any record level data back kila us.
            ikiwa self._outgoing.pending:
                ssldata.append(self._outgoing.read())
            ikiwa offset == len(view) ama self._need_ssldata:
                koma
        rudisha (ssldata, offset)


kundi _SSLProtocolTransport(transports._FlowControlMixin,
                            transports.Transport):

    _sendfile_compatible = constants._SendfileMode.FALLBACK

    eleza __init__(self, loop, ssl_protocol):
        self._loop = loop
        # SSLProtocol instance
        self._ssl_protocol = ssl_protocol
        self._closed = Uongo

    eleza get_extra_info(self, name, default=Tupu):
        """Get optional transport information."""
        rudisha self._ssl_protocol._get_extra_info(name, default)

    eleza set_protocol(self, protocol):
        self._ssl_protocol._set_app_protocol(protocol)

    eleza get_protocol(self):
        rudisha self._ssl_protocol._app_protocol

    eleza is_closing(self):
        rudisha self._closed

    eleza close(self):
        """Close the transport.

        Buffered data will be flushed asynchronously.  No more data
        will be received.  After all buffered data ni flushed, the
        protocol's connection_lost() method will (eventually) called
        ukijumuisha Tupu as its argument.
        """
        self._closed = Kweli
        self._ssl_protocol._start_shutdown()

    eleza __del__(self, _warn=warnings.warn):
        ikiwa sio self._closed:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self.close()

    eleza is_reading(self):
        tr = self._ssl_protocol._transport
        ikiwa tr ni Tupu:
             ashiria RuntimeError('SSL transport has sio been initialized yet')
        rudisha tr.is_reading()

    eleza pause_reading(self):
        """Pause the receiving end.

        No data will be passed to the protocol's data_received()
        method until resume_reading() ni called.
        """
        self._ssl_protocol._transport.pause_reading()

    eleza resume_reading(self):
        """Resume the receiving end.

        Data received will once again be passed to the protocol's
        data_received() method.
        """
        self._ssl_protocol._transport.resume_reading()

    eleza set_write_buffer_limits(self, high=Tupu, low=Tupu):
        """Set the high- na low-water limits kila write flow control.

        These two values control when to call the protocol's
        pause_writing() na resume_writing() methods.  If specified,
        the low-water limit must be less than ama equal to the
        high-water limit.  Neither value can be negative.

        The defaults are implementation-specific.  If only the
        high-water limit ni given, the low-water limit defaults to an
        implementation-specific value less than ama equal to the
        high-water limit.  Setting high to zero forces low to zero as
        well, na causes pause_writing() to be called whenever the
        buffer becomes non-empty.  Setting low to zero causes
        resume_writing() to be called only once the buffer ni empty.
        Use of zero kila either limit ni generally sub-optimal as it
        reduces opportunities kila doing I/O na computation
        concurrently.
        """
        self._ssl_protocol._transport.set_write_buffer_limits(high, low)

    eleza get_write_buffer_size(self):
        """Return the current size of the write buffer."""
        rudisha self._ssl_protocol._transport.get_write_buffer_size()

    @property
    eleza _protocol_paused(self):
        # Required kila sendfile fallback pause_writing/resume_writing logic
        rudisha self._ssl_protocol._transport._protocol_paused

    eleza write(self, data):
        """Write some data bytes to the transport.

        This does sio block; it buffers the data na arranges kila it
        to be sent out asynchronously.
        """
        ikiwa sio isinstance(data, (bytes, bytearray, memoryview)):
             ashiria TypeError(f"data: expecting a bytes-like instance, "
                            f"got {type(data).__name__}")
        ikiwa sio data:
            return
        self._ssl_protocol._write_appdata(data)

    eleza can_write_eof(self):
        """Return Kweli ikiwa this transport supports write_eof(), Uongo ikiwa not."""
        rudisha Uongo

    eleza abort(self):
        """Close the transport immediately.

        Buffered data will be lost.  No more data will be received.
        The protocol's connection_lost() method will (eventually) be
        called ukijumuisha Tupu as its argument.
        """
        self._ssl_protocol._abort()
        self._closed = Kweli


kundi SSLProtocol(protocols.Protocol):
    """SSL protocol.

    Implementation of SSL on top of a socket using incoming na outgoing
    buffers which are ssl.MemoryBIO objects.
    """

    eleza __init__(self, loop, app_protocol, sslcontext, waiter,
                 server_side=Uongo, server_hostname=Tupu,
                 call_connection_made=Kweli,
                 ssl_handshake_timeout=Tupu):
        ikiwa ssl ni Tupu:
             ashiria RuntimeError('stdlib ssl module sio available')

        ikiwa ssl_handshake_timeout ni Tupu:
            ssl_handshake_timeout = constants.SSL_HANDSHAKE_TIMEOUT
        elikiwa ssl_handshake_timeout <= 0:
             ashiria ValueError(
                f"ssl_handshake_timeout should be a positive number, "
                f"got {ssl_handshake_timeout}")

        ikiwa sio sslcontext:
            sslcontext = _create_transport_context(
                server_side, server_hostname)

        self._server_side = server_side
        ikiwa server_hostname na sio server_side:
            self._server_hostname = server_hostname
        isipokua:
            self._server_hostname = Tupu
        self._sslcontext = sslcontext
        # SSL-specific extra info. More info are set when the handshake
        # completes.
        self._extra = dict(sslcontext=sslcontext)

        # App data write buffering
        self._write_backlog = collections.deque()
        self._write_buffer_size = 0

        self._waiter = waiter
        self._loop = loop
        self._set_app_protocol(app_protocol)
        self._app_transport = _SSLProtocolTransport(self._loop, self)
        # _SSLPipe instance (Tupu until the connection ni made)
        self._sslpipe = Tupu
        self._session_established = Uongo
        self._in_handshake = Uongo
        self._in_shutdown = Uongo
        # transport, ex: SelectorSocketTransport
        self._transport = Tupu
        self._call_connection_made = call_connection_made
        self._ssl_handshake_timeout = ssl_handshake_timeout

    eleza _set_app_protocol(self, app_protocol):
        self._app_protocol = app_protocol
        self._app_protocol_is_buffer = \
            isinstance(app_protocol, protocols.BufferedProtocol)

    eleza _wakeup_waiter(self, exc=Tupu):
        ikiwa self._waiter ni Tupu:
            return
        ikiwa sio self._waiter.cancelled():
            ikiwa exc ni sio Tupu:
                self._waiter.set_exception(exc)
            isipokua:
                self._waiter.set_result(Tupu)
        self._waiter = Tupu

    eleza connection_made(self, transport):
        """Called when the low-level connection ni made.

        Start the SSL handshake.
        """
        self._transport = transport
        self._sslpipe = _SSLPipe(self._sslcontext,
                                 self._server_side,
                                 self._server_hostname)
        self._start_handshake()

    eleza connection_lost(self, exc):
        """Called when the low-level connection ni lost ama closed.

        The argument ni an exception object ama Tupu (the latter
        meaning a regular EOF ni received ama the connection was
        aborted ama closed).
        """
        ikiwa self._session_established:
            self._session_established = Uongo
            self._loop.call_soon(self._app_protocol.connection_lost, exc)
        isipokua:
            # Most likely an exception occurred wakati kwenye SSL handshake.
            # Just mark the app transport as closed so that its __del__
            # doesn't complain.
            ikiwa self._app_transport ni sio Tupu:
                self._app_transport._closed = Kweli
        self._transport = Tupu
        self._app_transport = Tupu
        ikiwa getattr(self, '_handshake_timeout_handle', Tupu):
            self._handshake_timeout_handle.cancel()
        self._wakeup_waiter(exc)
        self._app_protocol = Tupu
        self._sslpipe = Tupu

    eleza pause_writing(self):
        """Called when the low-level transport's buffer goes over
        the high-water mark.
        """
        self._app_protocol.pause_writing()

    eleza resume_writing(self):
        """Called when the low-level transport's buffer drains below
        the low-water mark.
        """
        self._app_protocol.resume_writing()

    eleza data_received(self, data):
        """Called when some SSL data ni received.

        The argument ni a bytes object.
        """
        ikiwa self._sslpipe ni Tupu:
            # transport closing, sslpipe ni destroyed
            return

        jaribu:
            ssldata, appdata = self._sslpipe.feed_ssldata(data)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as e:
            self._fatal_error(e, 'SSL error kwenye data received')
            return

        kila chunk kwenye ssldata:
            self._transport.write(chunk)

        kila chunk kwenye appdata:
            ikiwa chunk:
                jaribu:
                    ikiwa self._app_protocol_is_buffer:
                        protocols._feed_data_to_buffered_proto(
                            self._app_protocol, chunk)
                    isipokua:
                        self._app_protocol.data_received(chunk)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except BaseException as ex:
                    self._fatal_error(
                        ex, 'application protocol failed to receive SSL data')
                    return
            isipokua:
                self._start_shutdown()
                koma

    eleza eof_received(self):
        """Called when the other end of the low-level stream
        ni half-closed.

        If this returns a false value (including Tupu), the transport
        will close itself.  If it returns a true value, closing the
        transport ni up to the protocol.
        """
        jaribu:
            ikiwa self._loop.get_debug():
                logger.debug("%r received EOF", self)

            self._wakeup_waiter(ConnectionResetError)

            ikiwa sio self._in_handshake:
                keep_open = self._app_protocol.eof_received()
                ikiwa keep_open:
                    logger.warning('returning true kutoka eof_received() '
                                   'has no effect when using ssl')
        mwishowe:
            self._transport.close()

    eleza _get_extra_info(self, name, default=Tupu):
        ikiwa name kwenye self._extra:
            rudisha self._extra[name]
        elikiwa self._transport ni sio Tupu:
            rudisha self._transport.get_extra_info(name, default)
        isipokua:
            rudisha default

    eleza _start_shutdown(self):
        ikiwa self._in_shutdown:
            return
        ikiwa self._in_handshake:
            self._abort()
        isipokua:
            self._in_shutdown = Kweli
            self._write_appdata(b'')

    eleza _write_appdata(self, data):
        self._write_backlog.append((data, 0))
        self._write_buffer_size += len(data)
        self._process_write_backlog()

    eleza _start_handshake(self):
        ikiwa self._loop.get_debug():
            logger.debug("%r starts SSL handshake", self)
            self._handshake_start_time = self._loop.time()
        isipokua:
            self._handshake_start_time = Tupu
        self._in_handshake = Kweli
        # (b'', 1) ni a special value kwenye _process_write_backlog() to do
        # the SSL handshake
        self._write_backlog.append((b'', 1))
        self._handshake_timeout_handle = \
            self._loop.call_later(self._ssl_handshake_timeout,
                                  self._check_handshake_timeout)
        self._process_write_backlog()

    eleza _check_handshake_timeout(self):
        ikiwa self._in_handshake ni Kweli:
            msg = (
                f"SSL handshake ni taking longer than "
                f"{self._ssl_handshake_timeout} seconds: "
                f"aborting the connection"
            )
            self._fatal_error(ConnectionAbortedError(msg))

    eleza _on_handshake_complete(self, handshake_exc):
        self._in_handshake = Uongo
        self._handshake_timeout_handle.cancel()

        sslobj = self._sslpipe.ssl_object
        jaribu:
            ikiwa handshake_exc ni sio Tupu:
                 ashiria handshake_exc

            peercert = sslobj.getpeercert()
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            ikiwa isinstance(exc, ssl.CertificateError):
                msg = 'SSL handshake failed on verifying the certificate'
            isipokua:
                msg = 'SSL handshake failed'
            self._fatal_error(exc, msg)
            return

        ikiwa self._loop.get_debug():
            dt = self._loop.time() - self._handshake_start_time
            logger.debug("%r: SSL handshake took %.1f ms", self, dt * 1e3)

        # Add extra info that becomes available after handshake.
        self._extra.update(peercert=peercert,
                           cipher=sslobj.cipher(),
                           compression=sslobj.compression(),
                           ssl_object=sslobj,
                           )
        ikiwa self._call_connection_made:
            self._app_protocol.connection_made(self._app_transport)
        self._wakeup_waiter()
        self._session_established = Kweli
        # In case transport.write() was already called. Don't call
        # immediately _process_write_backlog(), but schedule it:
        # _on_handshake_complete() can be called indirectly from
        # _process_write_backlog(), na _process_write_backlog() ni not
        # reentrant.
        self._loop.call_soon(self._process_write_backlog)

    eleza _process_write_backlog(self):
        # Try to make progress on the write backlog.
        ikiwa self._transport ni Tupu ama self._sslpipe ni Tupu:
            return

        jaribu:
            kila i kwenye range(len(self._write_backlog)):
                data, offset = self._write_backlog[0]
                ikiwa data:
                    ssldata, offset = self._sslpipe.feed_appdata(data, offset)
                elikiwa offset:
                    ssldata = self._sslpipe.do_handshake(
                        self._on_handshake_complete)
                    offset = 1
                isipokua:
                    ssldata = self._sslpipe.shutdown(self._finalize)
                    offset = 1

                kila chunk kwenye ssldata:
                    self._transport.write(chunk)

                ikiwa offset < len(data):
                    self._write_backlog[0] = (data, offset)
                    # A short write means that a write ni blocked on a read
                    # We need to enable reading ikiwa it ni paused!
                    assert self._sslpipe.need_ssldata
                    ikiwa self._transport._paused:
                        self._transport.resume_reading()
                    koma

                # An entire chunk kutoka the backlog was processed. We can
                # delete it na reduce the outstanding buffer size.
                toa self._write_backlog[0]
                self._write_buffer_size -= len(data)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            ikiwa self._in_handshake:
                # Exceptions will be re-raised kwenye _on_handshake_complete.
                self._on_handshake_complete(exc)
            isipokua:
                self._fatal_error(exc, 'Fatal error on SSL transport')

    eleza _fatal_error(self, exc, message='Fatal error on transport'):
        ikiwa isinstance(exc, OSError):
            ikiwa self._loop.get_debug():
                logger.debug("%r: %s", self, message, exc_info=Kweli)
        isipokua:
            self._loop.call_exception_handler({
                'message': message,
                'exception': exc,
                'transport': self._transport,
                'protocol': self,
            })
        ikiwa self._transport:
            self._transport._force_close(exc)

    eleza _finalize(self):
        self._sslpipe = Tupu

        ikiwa self._transport ni sio Tupu:
            self._transport.close()

    eleza _abort(self):
        jaribu:
            ikiwa self._transport ni sio Tupu:
                self._transport.abort()
        mwishowe:
            self._finalize()
