__all__ = (
    'StreamReader', 'StreamWriter', 'StreamReaderProtocol',
    'open_connection', 'start_server')

agiza socket
agiza sys
agiza warnings
agiza weakref

ikiwa hasattr(socket, 'AF_UNIX'):
    __all__ += ('open_unix_connection', 'start_unix_server')

kutoka . agiza coroutines
kutoka . agiza events
kutoka . agiza exceptions
kutoka . agiza format_helpers
kutoka . agiza protocols
kutoka .log agiza logger
kutoka .tasks agiza sleep


_DEFAULT_LIMIT = 2 ** 16  # 64 KiB


async eleza open_connection(host=Tupu, port=Tupu, *,
                          loop=Tupu, limit=_DEFAULT_LIMIT, **kwds):
    """A wrapper kila create_connection() returning a (reader, writer) pair.

    The reader returned ni a StreamReader instance; the writer ni a
    StreamWriter instance.

    The arguments are all the usual arguments to create_connection()
    tatizo protocol_factory; most common are positional host na port,
    ukijumuisha various optional keyword arguments following.

    Additional optional keyword arguments are loop (to set the event loop
    instance to use) na limit (to set the buffer limit pitaed to the
    StreamReader).

    (If you want to customize the StreamReader and/or
    StreamReaderProtocol classes, just copy the code -- there's
    really nothing special here tatizo some convenience.)
    """
    ikiwa loop ni Tupu:
        loop = events.get_event_loop()
    isipokua:
        warnings.warn("The loop argument ni deprecated since Python 3.8, "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning, stacklevel=2)
    reader = StreamReader(limit=limit, loop=loop)
    protocol = StreamReaderProtocol(reader, loop=loop)
    transport, _ = await loop.create_connection(
        lambda: protocol, host, port, **kwds)
    writer = StreamWriter(transport, protocol, reader, loop)
    rudisha reader, writer


async eleza start_server(client_connected_cb, host=Tupu, port=Tupu, *,
                       loop=Tupu, limit=_DEFAULT_LIMIT, **kwds):
    """Start a socket server, call back kila each client connected.

    The first parameter, `client_connected_cb`, takes two parameters:
    client_reader, client_writer.  client_reader ni a StreamReader
    object, wakati client_writer ni a StreamWriter object.  This
    parameter can either be a plain callback function ama a coroutine;
    ikiwa it ni a coroutine, it will be automatically converted into a
    Task.

    The rest of the arguments are all the usual arguments to
    loop.create_server() tatizo protocol_factory; most common are
    positional host na port, ukijumuisha various optional keyword arguments
    following.  The rudisha value ni the same kama loop.create_server().

    Additional optional keyword arguments are loop (to set the event loop
    instance to use) na limit (to set the buffer limit pitaed to the
    StreamReader).

    The rudisha value ni the same kama loop.create_server(), i.e. a
    Server object which can be used to stop the service.
    """
    ikiwa loop ni Tupu:
        loop = events.get_event_loop()
    isipokua:
        warnings.warn("The loop argument ni deprecated since Python 3.8, "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning, stacklevel=2)

    eleza factory():
        reader = StreamReader(limit=limit, loop=loop)
        protocol = StreamReaderProtocol(reader, client_connected_cb,
                                        loop=loop)
        rudisha protocol

    rudisha await loop.create_server(factory, host, port, **kwds)


ikiwa hasattr(socket, 'AF_UNIX'):
    # UNIX Domain Sockets are supported on this platform

    async eleza open_unix_connection(path=Tupu, *,
                                   loop=Tupu, limit=_DEFAULT_LIMIT, **kwds):
        """Similar to `open_connection` but works ukijumuisha UNIX Domain Sockets."""
        ikiwa loop ni Tupu:
            loop = events.get_event_loop()
        isipokua:
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
                          DeprecationWarning, stacklevel=2)
        reader = StreamReader(limit=limit, loop=loop)
        protocol = StreamReaderProtocol(reader, loop=loop)
        transport, _ = await loop.create_unix_connection(
            lambda: protocol, path, **kwds)
        writer = StreamWriter(transport, protocol, reader, loop)
        rudisha reader, writer

    async eleza start_unix_server(client_connected_cb, path=Tupu, *,
                                loop=Tupu, limit=_DEFAULT_LIMIT, **kwds):
        """Similar to `start_server` but works ukijumuisha UNIX Domain Sockets."""
        ikiwa loop ni Tupu:
            loop = events.get_event_loop()
        isipokua:
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
                          DeprecationWarning, stacklevel=2)

        eleza factory():
            reader = StreamReader(limit=limit, loop=loop)
            protocol = StreamReaderProtocol(reader, client_connected_cb,
                                            loop=loop)
            rudisha protocol

        rudisha await loop.create_unix_server(factory, path, **kwds)


kundi FlowControlMixin(protocols.Protocol):
    """Reusable flow control logic kila StreamWriter.drain().

    This implements the protocol methods pause_writing(),
    resume_writing() na connection_lost().  If the subkundi overrides
    these it must call the super methods.

    StreamWriter.drain() must wait kila _drain_helper() coroutine.
    """

    eleza __init__(self, loop=Tupu):
        ikiwa loop ni Tupu:
            self._loop = events.get_event_loop()
        isipokua:
            self._loop = loop
        self._paused = Uongo
        self._drain_waiter = Tupu
        self._connection_lost = Uongo

    eleza pause_writing(self):
        assert sio self._paused
        self._paused = Kweli
        ikiwa self._loop.get_debug():
            logger.debug("%r pauses writing", self)

    eleza resume_writing(self):
        assert self._paused
        self._paused = Uongo
        ikiwa self._loop.get_debug():
            logger.debug("%r resumes writing", self)

        waiter = self._drain_waiter
        ikiwa waiter ni sio Tupu:
            self._drain_waiter = Tupu
            ikiwa sio waiter.done():
                waiter.set_result(Tupu)

    eleza connection_lost(self, exc):
        self._connection_lost = Kweli
        # Wake up the writer ikiwa currently paused.
        ikiwa sio self._paused:
            rudisha
        waiter = self._drain_waiter
        ikiwa waiter ni Tupu:
            rudisha
        self._drain_waiter = Tupu
        ikiwa waiter.done():
            rudisha
        ikiwa exc ni Tupu:
            waiter.set_result(Tupu)
        isipokua:
            waiter.set_exception(exc)

    async eleza _drain_helper(self):
        ikiwa self._connection_lost:
            ashiria ConnectionResetError('Connection lost')
        ikiwa sio self._paused:
            rudisha
        waiter = self._drain_waiter
        assert waiter ni Tupu ama waiter.cancelled()
        waiter = self._loop.create_future()
        self._drain_waiter = waiter
        await waiter

    eleza _get_close_waiter(self, stream):
        ashiria NotImplementedError


kundi StreamReaderProtocol(FlowControlMixin, protocols.Protocol):
    """Helper kundi to adapt between Protocol na StreamReader.

    (This ni a helper kundi instead of making StreamReader itself a
    Protocol subclass, because the StreamReader has other potential
    uses, na to prevent the user of the StreamReader to accidentally
    call inappropriate methods of the protocol.)
    """

    _source_traceback = Tupu

    eleza __init__(self, stream_reader, client_connected_cb=Tupu, loop=Tupu):
        super().__init__(loop=loop)
        ikiwa stream_reader ni sio Tupu:
            self._stream_reader_wr = weakref.ref(stream_reader,
                                                 self._on_reader_gc)
            self._source_traceback = stream_reader._source_traceback
        isipokua:
            self._stream_reader_wr = Tupu
        ikiwa client_connected_cb ni sio Tupu:
            # This ni a stream created by the `create_server()` function.
            # Keep a strong reference to the reader until a connection
            # ni established.
            self._strong_reader = stream_reader
        self._reject_connection = Uongo
        self._stream_writer = Tupu
        self._transport = Tupu
        self._client_connected_cb = client_connected_cb
        self._over_ssl = Uongo
        self._closed = self._loop.create_future()

    eleza _on_reader_gc(self, wr):
        transport = self._transport
        ikiwa transport ni sio Tupu:
            # connection_made was called
            context = {
                'message': ('An open stream object ni being garbage '
                            'collected; call "stream.close()" explicitly.')
            }
            ikiwa self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)
            transport.abort()
        isipokua:
            self._reject_connection = Kweli
        self._stream_reader_wr = Tupu

    @property
    eleza _stream_reader(self):
        ikiwa self._stream_reader_wr ni Tupu:
            rudisha Tupu
        rudisha self._stream_reader_wr()

    eleza connection_made(self, transport):
        ikiwa self._reject_connection:
            context = {
                'message': ('An open stream was garbage collected prior to '
                            'establishing network connection; '
                            'call "stream.close()" explicitly.')
            }
            ikiwa self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)
            transport.abort()
            rudisha
        self._transport = transport
        reader = self._stream_reader
        ikiwa reader ni sio Tupu:
            reader.set_transport(transport)
        self._over_ssl = transport.get_extra_info('sslcontext') ni sio Tupu
        ikiwa self._client_connected_cb ni sio Tupu:
            self._stream_writer = StreamWriter(transport, self,
                                               reader,
                                               self._loop)
            res = self._client_connected_cb(reader,
                                            self._stream_writer)
            ikiwa coroutines.iscoroutine(res):
                self._loop.create_task(res)
            self._strong_reader = Tupu

    eleza connection_lost(self, exc):
        reader = self._stream_reader
        ikiwa reader ni sio Tupu:
            ikiwa exc ni Tupu:
                reader.feed_eof()
            isipokua:
                reader.set_exception(exc)
        ikiwa sio self._closed.done():
            ikiwa exc ni Tupu:
                self._closed.set_result(Tupu)
            isipokua:
                self._closed.set_exception(exc)
        super().connection_lost(exc)
        self._stream_reader_wr = Tupu
        self._stream_writer = Tupu
        self._transport = Tupu

    eleza data_received(self, data):
        reader = self._stream_reader
        ikiwa reader ni sio Tupu:
            reader.feed_data(data)

    eleza eof_received(self):
        reader = self._stream_reader
        ikiwa reader ni sio Tupu:
            reader.feed_eof()
        ikiwa self._over_ssl:
            # Prevent a warning kwenye SSLProtocol.eof_received:
            # "returning true kutoka eof_received()
            # has no effect when using ssl"
            rudisha Uongo
        rudisha Kweli

    eleza _get_close_waiter(self, stream):
        rudisha self._closed

    eleza __del__(self):
        # Prevent reports about unhandled exceptions.
        # Better than self._closed._log_traceback = Uongo hack
        closed = self._closed
        ikiwa closed.done() na sio closed.cancelled():
            closed.exception()


kundi StreamWriter:
    """Wraps a Transport.

    This exposes write(), writelines(), [can_]write_eof(),
    get_extra_info() na close().  It adds drain() which returns an
    optional Future on which you can wait kila flow control.  It also
    adds a transport property which references the Transport
    directly.
    """

    eleza __init__(self, transport, protocol, reader, loop):
        self._transport = transport
        self._protocol = protocol
        # drain() expects that the reader has an exception() method
        assert reader ni Tupu ama isinstance(reader, StreamReader)
        self._reader = reader
        self._loop = loop
        self._complete_fut = self._loop.create_future()
        self._complete_fut.set_result(Tupu)

    eleza __repr__(self):
        info = [self.__class__.__name__, f'transport={self._transport!r}']
        ikiwa self._reader ni sio Tupu:
            info.append(f'reader={self._reader!r}')
        rudisha '<{}>'.format(' '.join(info))

    @property
    eleza transport(self):
        rudisha self._transport

    eleza write(self, data):
        self._transport.write(data)

    eleza writelines(self, data):
        self._transport.writelines(data)

    eleza write_eof(self):
        rudisha self._transport.write_eof()

    eleza can_write_eof(self):
        rudisha self._transport.can_write_eof()

    eleza close(self):
        rudisha self._transport.close()

    eleza is_closing(self):
        rudisha self._transport.is_closing()

    async eleza wait_closed(self):
        await self._protocol._get_close_waiter(self)

    eleza get_extra_info(self, name, default=Tupu):
        rudisha self._transport.get_extra_info(name, default)

    async eleza drain(self):
        """Flush the write buffer.

        The intended use ni to write

          w.write(data)
          await w.drain()
        """
        ikiwa self._reader ni sio Tupu:
            exc = self._reader.exception()
            ikiwa exc ni sio Tupu:
                ashiria exc
        ikiwa self._transport.is_closing():
            # Wait kila protocol.connection_lost() call
            # Raise connection closing error ikiwa any,
            # ConnectionResetError otherwise
            # Yield to the event loop so connection_lost() may be
            # called.  Without this, _drain_helper() would rudisha
            # immediately, na code that calls
            #     write(...); await drain()
            # kwenye a loop would never call connection_lost(), so it
            # would sio see an error when the socket ni closed.
            await sleep(0)
        await self._protocol._drain_helper()


kundi StreamReader:

    _source_traceback = Tupu

    eleza __init__(self, limit=_DEFAULT_LIMIT, loop=Tupu):
        # The line length limit ni  a security feature;
        # it also doubles kama half the buffer limit.

        ikiwa limit <= 0:
            ashiria ValueError('Limit cansio be <= 0')

        self._limit = limit
        ikiwa loop ni Tupu:
            self._loop = events.get_event_loop()
        isipokua:
            self._loop = loop
        self._buffer = bytearray()
        self._eof = Uongo    # Whether we're done.
        self._waiter = Tupu  # A future used by _wait_for_data()
        self._exception = Tupu
        self._transport = Tupu
        self._paused = Uongo
        ikiwa self._loop.get_debug():
            self._source_traceback = format_helpers.extract_stack(
                sys._getframe(1))

    eleza __repr__(self):
        info = ['StreamReader']
        ikiwa self._buffer:
            info.append(f'{len(self._buffer)} bytes')
        ikiwa self._eof:
            info.append('eof')
        ikiwa self._limit != _DEFAULT_LIMIT:
            info.append(f'limit={self._limit}')
        ikiwa self._waiter:
            info.append(f'waiter={self._waiter!r}')
        ikiwa self._exception:
            info.append(f'exception={self._exception!r}')
        ikiwa self._transport:
            info.append(f'transport={self._transport!r}')
        ikiwa self._paused:
            info.append('paused')
        rudisha '<{}>'.format(' '.join(info))

    eleza exception(self):
        rudisha self._exception

    eleza set_exception(self, exc):
        self._exception = exc

        waiter = self._waiter
        ikiwa waiter ni sio Tupu:
            self._waiter = Tupu
            ikiwa sio waiter.cancelled():
                waiter.set_exception(exc)

    eleza _wakeup_waiter(self):
        """Wakeup read*() functions waiting kila data ama EOF."""
        waiter = self._waiter
        ikiwa waiter ni sio Tupu:
            self._waiter = Tupu
            ikiwa sio waiter.cancelled():
                waiter.set_result(Tupu)

    eleza set_transport(self, transport):
        assert self._transport ni Tupu, 'Transport already set'
        self._transport = transport

    eleza _maybe_resume_transport(self):
        ikiwa self._paused na len(self._buffer) <= self._limit:
            self._paused = Uongo
            self._transport.resume_reading()

    eleza feed_eof(self):
        self._eof = Kweli
        self._wakeup_waiter()

    eleza at_eof(self):
        """Return Kweli ikiwa the buffer ni empty na 'feed_eof' was called."""
        rudisha self._eof na sio self._buffer

    eleza feed_data(self, data):
        assert sio self._eof, 'feed_data after feed_eof'

        ikiwa sio data:
            rudisha

        self._buffer.extend(data)
        self._wakeup_waiter()

        ikiwa (self._transport ni sio Tupu na
                sio self._paused na
                len(self._buffer) > 2 * self._limit):
            jaribu:
                self._transport.pause_reading()
            tatizo NotImplementedError:
                # The transport can't be paused.
                # We'll just have to buffer all data.
                # Forget the transport so we don't keep trying.
                self._transport = Tupu
            isipokua:
                self._paused = Kweli

    async eleza _wait_for_data(self, func_name):
        """Wait until feed_data() ama feed_eof() ni called.

        If stream was paused, automatically resume it.
        """
        # StreamReader uses a future to link the protocol feed_data() method
        # to a read coroutine. Running two read coroutines at the same time
        # would have an unexpected behaviour. It would sio possible to know
        # which coroutine would get the next data.
        ikiwa self._waiter ni sio Tupu:
            ashiria RuntimeError(
                f'{func_name}() called wakati another coroutine ni '
                f'already waiting kila incoming data')

        assert sio self._eof, '_wait_for_data after EOF'

        # Waiting kila data wakati paused will make deadlock, so prevent it.
        # This ni essential kila readexactly(n) kila case when n > self._limit.
        ikiwa self._paused:
            self._paused = Uongo
            self._transport.resume_reading()

        self._waiter = self._loop.create_future()
        jaribu:
            await self._waiter
        mwishowe:
            self._waiter = Tupu

    async eleza readline(self):
        """Read chunk of data kutoka the stream until newline (b'\n') ni found.

        On success, rudisha chunk that ends ukijumuisha newline. If only partial
        line can be read due to EOF, rudisha incomplete line without
        terminating newline. When EOF was reached wakati no bytes read, empty
        bytes object ni returned.

        If limit ni reached, ValueError will be raised. In that case, if
        newline was found, complete line including newline will be removed
        kutoka internal buffer. Else, internal buffer will be cleared. Limit is
        compared against part of the line without newline.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        sep = b'\n'
        seplen = len(sep)
        jaribu:
            line = await self.readuntil(sep)
        tatizo exceptions.IncompleteReadError kama e:
            rudisha e.partial
        tatizo exceptions.LimitOverrunError kama e:
            ikiwa self._buffer.startswith(sep, e.consumed):
                toa self._buffer[:e.consumed + seplen]
            isipokua:
                self._buffer.clear()
            self._maybe_resume_transport()
            ashiria ValueError(e.args[0])
        rudisha line

    async eleza readuntil(self, separator=b'\n'):
        """Read data kutoka the stream until ``separator`` ni found.

        On success, the data na separator will be removed kutoka the
        internal buffer (consumed). Returned data will include the
        separator at the end.

        Configured stream limit ni used to check result. Limit sets the
        maximal length of data that can be returned, sio counting the
        separator.

        If an EOF occurs na the complete separator ni still sio found,
        an IncompleteReadError exception will be raised, na the internal
        buffer will be reset.  The IncompleteReadError.partial attribute
        may contain the separator partially.

        If the data cansio be read because of over limit, a
        LimitOverrunError exception  will be raised, na the data
        will be left kwenye the internal buffer, so it can be read again.
        """
        seplen = len(separator)
        ikiwa seplen == 0:
            ashiria ValueError('Separator should be at least one-byte string')

        ikiwa self._exception ni sio Tupu:
            ashiria self._exception

        # Consume whole buffer tatizo last bytes, which length is
        # one less than seplen. Let's check corner cases with
        # separator='SEPARATOR':
        # * we have received almost complete separator (without last
        #   byte). i.e buffer='some textSEPARATO'. In this case we
        #   can safely consume len(separator) - 1 bytes.
        # * last byte of buffer ni first byte of separator, i.e.
        #   buffer='abcdefghijklmnopqrS'. We may safely consume
        #   everything tatizo that last byte, but this require to
        #   analyze bytes of buffer that match partial separator.
        #   This ni slow and/or require FSM. For this case our
        #   implementation ni sio optimal, since require rescanning
        #   of data that ni known to sio belong to separator. In
        #   real world, separator will sio be so long to notice
        #   performance problems. Even when reading MIME-encoded
        #   messages :)

        # `offset` ni the number of bytes kutoka the beginning of the buffer
        # where there ni no occurrence of `separator`.
        offset = 0

        # Loop until we find `separator` kwenye the buffer, exceed the buffer size,
        # ama an EOF has happened.
        wakati Kweli:
            buflen = len(self._buffer)

            # Check ikiwa we now have enough data kwenye the buffer kila `separator` to
            # fit.
            ikiwa buflen - offset >= seplen:
                isep = self._buffer.find(separator, offset)

                ikiwa isep != -1:
                    # `separator` ni kwenye the buffer. `isep` will be used later
                    # to retrieve the data.
                    koma

                # see upper comment kila explanation.
                offset = buflen + 1 - seplen
                ikiwa offset > self._limit:
                    ashiria exceptions.LimitOverrunError(
                        'Separator ni sio found, na chunk exceed the limit',
                        offset)

            # Complete message (ukijumuisha full separator) may be present kwenye buffer
            # even when EOF flag ni set. This may happen when the last chunk
            # adds data which makes separator be found. That's why we check for
            # EOF *ater* inspecting the buffer.
            ikiwa self._eof:
                chunk = bytes(self._buffer)
                self._buffer.clear()
                ashiria exceptions.IncompleteReadError(chunk, Tupu)

            # _wait_for_data() will resume reading ikiwa stream was paused.
            await self._wait_for_data('readuntil')

        ikiwa isep > self._limit:
            ashiria exceptions.LimitOverrunError(
                'Separator ni found, but chunk ni longer than limit', isep)

        chunk = self._buffer[:isep + seplen]
        toa self._buffer[:isep + seplen]
        self._maybe_resume_transport()
        rudisha bytes(chunk)

    async eleza read(self, n=-1):
        """Read up to `n` bytes kutoka the stream.

        If n ni sio provided, ama set to -1, read until EOF na rudisha all read
        bytes. If the EOF was received na the internal buffer ni empty, rudisha
        an empty bytes object.

        If n ni zero, rudisha empty bytes object immediately.

        If n ni positive, this function try to read `n` bytes, na may rudisha
        less ama equal bytes than requested, but at least one byte. If EOF was
        received before any byte ni read, this function returns empty byte
        object.

        Returned value ni sio limited ukijumuisha limit, configured at stream
        creation.

        If stream was paused, this function will automatically resume it if
        needed.
        """

        ikiwa self._exception ni sio Tupu:
            ashiria self._exception

        ikiwa n == 0:
            rudisha b''

        ikiwa n < 0:
            # This used to just loop creating a new waiter hoping to
            # collect everything kwenye self._buffer, but that would
            # deadlock ikiwa the subprocess sends more than self.limit
            # bytes.  So just call self.read(self._limit) until EOF.
            blocks = []
            wakati Kweli:
                block = await self.read(self._limit)
                ikiwa sio block:
                    koma
                blocks.append(block)
            rudisha b''.join(blocks)

        ikiwa sio self._buffer na sio self._eof:
            await self._wait_for_data('read')

        # This will work right even ikiwa buffer ni less than n bytes
        data = bytes(self._buffer[:n])
        toa self._buffer[:n]

        self._maybe_resume_transport()
        rudisha data

    async eleza readexactly(self, n):
        """Read exactly `n` bytes.

        Raise an IncompleteReadError ikiwa EOF ni reached before `n` bytes can be
        read. The IncompleteReadError.partial attribute of the exception will
        contain the partial read bytes.

        ikiwa n ni zero, rudisha empty bytes object.

        Returned value ni sio limited ukijumuisha limit, configured at stream
        creation.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        ikiwa n < 0:
            ashiria ValueError('readexactly size can sio be less than zero')

        ikiwa self._exception ni sio Tupu:
            ashiria self._exception

        ikiwa n == 0:
            rudisha b''

        wakati len(self._buffer) < n:
            ikiwa self._eof:
                incomplete = bytes(self._buffer)
                self._buffer.clear()
                ashiria exceptions.IncompleteReadError(incomplete, n)

            await self._wait_for_data('readexactly')

        ikiwa len(self._buffer) == n:
            data = bytes(self._buffer)
            self._buffer.clear()
        isipokua:
            data = bytes(self._buffer[:n])
            toa self._buffer[:n]
        self._maybe_resume_transport()
        rudisha data

    eleza __aiter__(self):
        rudisha self

    async eleza __anext__(self):
        val = await self.readline()
        ikiwa val == b'':
            ashiria StopAsyncIteration
        rudisha val
