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


async eleza open_connection(host=None, port=None, *,
                          loop=None, limit=_DEFAULT_LIMIT, **kwds):
    """A wrapper for create_connection() returning a (reader, writer) pair.

    The reader returned is a StreamReader instance; the writer is a
    StreamWriter instance.

    The arguments are all the usual arguments to create_connection()
    except protocol_factory; most common are positional host and port,
    with various optional keyword arguments following.

    Additional optional keyword arguments are loop (to set the event loop
    instance to use) and limit (to set the buffer limit passed to the
    StreamReader).

    (If you want to customize the StreamReader and/or
    StreamReaderProtocol classes, just copy the code -- there's
    really nothing special here except some convenience.)
    """
    ikiwa loop is None:
        loop = events.get_event_loop()
    else:
        warnings.warn("The loop argument is deprecated since Python 3.8, "
                      "and scheduled for removal in Python 3.10.",
                      DeprecationWarning, stacklevel=2)
    reader = StreamReader(limit=limit, loop=loop)
    protocol = StreamReaderProtocol(reader, loop=loop)
    transport, _ = await loop.create_connection(
        lambda: protocol, host, port, **kwds)
    writer = StreamWriter(transport, protocol, reader, loop)
    rudisha reader, writer


async eleza start_server(client_connected_cb, host=None, port=None, *,
                       loop=None, limit=_DEFAULT_LIMIT, **kwds):
    """Start a socket server, call back for each client connected.

    The first parameter, `client_connected_cb`, takes two parameters:
    client_reader, client_writer.  client_reader is a StreamReader
    object, while client_writer is a StreamWriter object.  This
    parameter can either be a plain callback function or a coroutine;
    ikiwa it is a coroutine, it will be automatically converted into a
    Task.

    The rest of the arguments are all the usual arguments to
    loop.create_server() except protocol_factory; most common are
    positional host and port, with various optional keyword arguments
    following.  The rudisha value is the same as loop.create_server().

    Additional optional keyword arguments are loop (to set the event loop
    instance to use) and limit (to set the buffer limit passed to the
    StreamReader).

    The rudisha value is the same as loop.create_server(), i.e. a
    Server object which can be used to stop the service.
    """
    ikiwa loop is None:
        loop = events.get_event_loop()
    else:
        warnings.warn("The loop argument is deprecated since Python 3.8, "
                      "and scheduled for removal in Python 3.10.",
                      DeprecationWarning, stacklevel=2)

    eleza factory():
        reader = StreamReader(limit=limit, loop=loop)
        protocol = StreamReaderProtocol(reader, client_connected_cb,
                                        loop=loop)
        rudisha protocol

    rudisha await loop.create_server(factory, host, port, **kwds)


ikiwa hasattr(socket, 'AF_UNIX'):
    # UNIX Domain Sockets are supported on this platform

    async eleza open_unix_connection(path=None, *,
                                   loop=None, limit=_DEFAULT_LIMIT, **kwds):
        """Similar to `open_connection` but works with UNIX Domain Sockets."""
        ikiwa loop is None:
            loop = events.get_event_loop()
        else:
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)
        reader = StreamReader(limit=limit, loop=loop)
        protocol = StreamReaderProtocol(reader, loop=loop)
        transport, _ = await loop.create_unix_connection(
            lambda: protocol, path, **kwds)
        writer = StreamWriter(transport, protocol, reader, loop)
        rudisha reader, writer

    async eleza start_unix_server(client_connected_cb, path=None, *,
                                loop=None, limit=_DEFAULT_LIMIT, **kwds):
        """Similar to `start_server` but works with UNIX Domain Sockets."""
        ikiwa loop is None:
            loop = events.get_event_loop()
        else:
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)

        eleza factory():
            reader = StreamReader(limit=limit, loop=loop)
            protocol = StreamReaderProtocol(reader, client_connected_cb,
                                            loop=loop)
            rudisha protocol

        rudisha await loop.create_unix_server(factory, path, **kwds)


kundi FlowControlMixin(protocols.Protocol):
    """Reusable flow control logic for StreamWriter.drain().

    This implements the protocol methods pause_writing(),
    resume_writing() and connection_lost().  If the subkundi overrides
    these it must call the super methods.

    StreamWriter.drain() must wait for _drain_helper() coroutine.
    """

    eleza __init__(self, loop=None):
        ikiwa loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop
        self._paused = False
        self._drain_waiter = None
        self._connection_lost = False

    eleza pause_writing(self):
        assert not self._paused
        self._paused = True
        ikiwa self._loop.get_debug():
            logger.debug("%r pauses writing", self)

    eleza resume_writing(self):
        assert self._paused
        self._paused = False
        ikiwa self._loop.get_debug():
            logger.debug("%r resumes writing", self)

        waiter = self._drain_waiter
        ikiwa waiter is not None:
            self._drain_waiter = None
            ikiwa not waiter.done():
                waiter.set_result(None)

    eleza connection_lost(self, exc):
        self._connection_lost = True
        # Wake up the writer ikiwa currently paused.
        ikiwa not self._paused:
            return
        waiter = self._drain_waiter
        ikiwa waiter is None:
            return
        self._drain_waiter = None
        ikiwa waiter.done():
            return
        ikiwa exc is None:
            waiter.set_result(None)
        else:
            waiter.set_exception(exc)

    async eleza _drain_helper(self):
        ikiwa self._connection_lost:
            raise ConnectionResetError('Connection lost')
        ikiwa not self._paused:
            return
        waiter = self._drain_waiter
        assert waiter is None or waiter.cancelled()
        waiter = self._loop.create_future()
        self._drain_waiter = waiter
        await waiter

    eleza _get_close_waiter(self, stream):
        raise NotImplementedError


kundi StreamReaderProtocol(FlowControlMixin, protocols.Protocol):
    """Helper kundi to adapt between Protocol and StreamReader.

    (This is a helper kundi instead of making StreamReader itself a
    Protocol subclass, because the StreamReader has other potential
    uses, and to prevent the user of the StreamReader to accidentally
    call inappropriate methods of the protocol.)
    """

    _source_traceback = None

    eleza __init__(self, stream_reader, client_connected_cb=None, loop=None):
        super().__init__(loop=loop)
        ikiwa stream_reader is not None:
            self._stream_reader_wr = weakref.ref(stream_reader,
                                                 self._on_reader_gc)
            self._source_traceback = stream_reader._source_traceback
        else:
            self._stream_reader_wr = None
        ikiwa client_connected_cb is not None:
            # This is a stream created by the `create_server()` function.
            # Keep a strong reference to the reader until a connection
            # is established.
            self._strong_reader = stream_reader
        self._reject_connection = False
        self._stream_writer = None
        self._transport = None
        self._client_connected_cb = client_connected_cb
        self._over_ssl = False
        self._closed = self._loop.create_future()

    eleza _on_reader_gc(self, wr):
        transport = self._transport
        ikiwa transport is not None:
            # connection_made was called
            context = {
                'message': ('An open stream object is being garbage '
                            'collected; call "stream.close()" explicitly.')
            }
            ikiwa self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)
            transport.abort()
        else:
            self._reject_connection = True
        self._stream_reader_wr = None

    @property
    eleza _stream_reader(self):
        ikiwa self._stream_reader_wr is None:
            rudisha None
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
            return
        self._transport = transport
        reader = self._stream_reader
        ikiwa reader is not None:
            reader.set_transport(transport)
        self._over_ssl = transport.get_extra_info('sslcontext') is not None
        ikiwa self._client_connected_cb is not None:
            self._stream_writer = StreamWriter(transport, self,
                                               reader,
                                               self._loop)
            res = self._client_connected_cb(reader,
                                            self._stream_writer)
            ikiwa coroutines.iscoroutine(res):
                self._loop.create_task(res)
            self._strong_reader = None

    eleza connection_lost(self, exc):
        reader = self._stream_reader
        ikiwa reader is not None:
            ikiwa exc is None:
                reader.feed_eof()
            else:
                reader.set_exception(exc)
        ikiwa not self._closed.done():
            ikiwa exc is None:
                self._closed.set_result(None)
            else:
                self._closed.set_exception(exc)
        super().connection_lost(exc)
        self._stream_reader_wr = None
        self._stream_writer = None
        self._transport = None

    eleza data_received(self, data):
        reader = self._stream_reader
        ikiwa reader is not None:
            reader.feed_data(data)

    eleza eof_received(self):
        reader = self._stream_reader
        ikiwa reader is not None:
            reader.feed_eof()
        ikiwa self._over_ssl:
            # Prevent a warning in SSLProtocol.eof_received:
            # "returning true kutoka eof_received()
            # has no effect when using ssl"
            rudisha False
        rudisha True

    eleza _get_close_waiter(self, stream):
        rudisha self._closed

    eleza __del__(self):
        # Prevent reports about unhandled exceptions.
        # Better than self._closed._log_traceback = False hack
        closed = self._closed
        ikiwa closed.done() and not closed.cancelled():
            closed.exception()


kundi StreamWriter:
    """Wraps a Transport.

    This exposes write(), writelines(), [can_]write_eof(),
    get_extra_info() and close().  It adds drain() which returns an
    optional Future on which you can wait for flow control.  It also
    adds a transport property which references the Transport
    directly.
    """

    eleza __init__(self, transport, protocol, reader, loop):
        self._transport = transport
        self._protocol = protocol
        # drain() expects that the reader has an exception() method
        assert reader is None or isinstance(reader, StreamReader)
        self._reader = reader
        self._loop = loop
        self._complete_fut = self._loop.create_future()
        self._complete_fut.set_result(None)

    eleza __repr__(self):
        info = [self.__class__.__name__, f'transport={self._transport!r}']
        ikiwa self._reader is not None:
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

    eleza get_extra_info(self, name, default=None):
        rudisha self._transport.get_extra_info(name, default)

    async eleza drain(self):
        """Flush the write buffer.

        The intended use is to write

          w.write(data)
          await w.drain()
        """
        ikiwa self._reader is not None:
            exc = self._reader.exception()
            ikiwa exc is not None:
                raise exc
        ikiwa self._transport.is_closing():
            # Wait for protocol.connection_lost() call
            # Raise connection closing error ikiwa any,
            # ConnectionResetError otherwise
            # Yield to the event loop so connection_lost() may be
            # called.  Without this, _drain_helper() would return
            # immediately, and code that calls
            #     write(...); await drain()
            # in a loop would never call connection_lost(), so it
            # would not see an error when the socket is closed.
            await sleep(0)
        await self._protocol._drain_helper()


kundi StreamReader:

    _source_traceback = None

    eleza __init__(self, limit=_DEFAULT_LIMIT, loop=None):
        # The line length limit is  a security feature;
        # it also doubles as half the buffer limit.

        ikiwa limit <= 0:
            raise ValueError('Limit cannot be <= 0')

        self._limit = limit
        ikiwa loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop
        self._buffer = bytearray()
        self._eof = False    # Whether we're done.
        self._waiter = None  # A future used by _wait_for_data()
        self._exception = None
        self._transport = None
        self._paused = False
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
        ikiwa waiter is not None:
            self._waiter = None
            ikiwa not waiter.cancelled():
                waiter.set_exception(exc)

    eleza _wakeup_waiter(self):
        """Wakeup read*() functions waiting for data or EOF."""
        waiter = self._waiter
        ikiwa waiter is not None:
            self._waiter = None
            ikiwa not waiter.cancelled():
                waiter.set_result(None)

    eleza set_transport(self, transport):
        assert self._transport is None, 'Transport already set'
        self._transport = transport

    eleza _maybe_resume_transport(self):
        ikiwa self._paused and len(self._buffer) <= self._limit:
            self._paused = False
            self._transport.resume_reading()

    eleza feed_eof(self):
        self._eof = True
        self._wakeup_waiter()

    eleza at_eof(self):
        """Return True ikiwa the buffer is empty and 'feed_eof' was called."""
        rudisha self._eof and not self._buffer

    eleza feed_data(self, data):
        assert not self._eof, 'feed_data after feed_eof'

        ikiwa not data:
            return

        self._buffer.extend(data)
        self._wakeup_waiter()

        ikiwa (self._transport is not None and
                not self._paused and
                len(self._buffer) > 2 * self._limit):
            try:
                self._transport.pause_reading()
            except NotImplementedError:
                # The transport can't be paused.
                # We'll just have to buffer all data.
                # Forget the transport so we don't keep trying.
                self._transport = None
            else:
                self._paused = True

    async eleza _wait_for_data(self, func_name):
        """Wait until feed_data() or feed_eof() is called.

        If stream was paused, automatically resume it.
        """
        # StreamReader uses a future to link the protocol feed_data() method
        # to a read coroutine. Running two read coroutines at the same time
        # would have an unexpected behaviour. It would not possible to know
        # which coroutine would get the next data.
        ikiwa self._waiter is not None:
            raise RuntimeError(
                f'{func_name}() called while another coroutine is '
                f'already waiting for incoming data')

        assert not self._eof, '_wait_for_data after EOF'

        # Waiting for data while paused will make deadlock, so prevent it.
        # This is essential for readexactly(n) for case when n > self._limit.
        ikiwa self._paused:
            self._paused = False
            self._transport.resume_reading()

        self._waiter = self._loop.create_future()
        try:
            await self._waiter
        finally:
            self._waiter = None

    async eleza readline(self):
        """Read chunk of data kutoka the stream until newline (b'\n') is found.

        On success, rudisha chunk that ends with newline. If only partial
        line can be read due to EOF, rudisha incomplete line without
        terminating newline. When EOF was reached while no bytes read, empty
        bytes object is returned.

        If limit is reached, ValueError will be raised. In that case, if
        newline was found, complete line including newline will be removed
        kutoka internal buffer. Else, internal buffer will be cleared. Limit is
        compared against part of the line without newline.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        sep = b'\n'
        seplen = len(sep)
        try:
            line = await self.readuntil(sep)
        except exceptions.IncompleteReadError as e:
            rudisha e.partial
        except exceptions.LimitOverrunError as e:
            ikiwa self._buffer.startswith(sep, e.consumed):
                del self._buffer[:e.consumed + seplen]
            else:
                self._buffer.clear()
            self._maybe_resume_transport()
            raise ValueError(e.args[0])
        rudisha line

    async eleza readuntil(self, separator=b'\n'):
        """Read data kutoka the stream until ``separator`` is found.

        On success, the data and separator will be removed kutoka the
        internal buffer (consumed). Returned data will include the
        separator at the end.

        Configured stream limit is used to check result. Limit sets the
        maximal length of data that can be returned, not counting the
        separator.

        If an EOF occurs and the complete separator is still not found,
        an IncompleteReadError exception will be raised, and the internal
        buffer will be reset.  The IncompleteReadError.partial attribute
        may contain the separator partially.

        If the data cannot be read because of over limit, a
        LimitOverrunError exception  will be raised, and the data
        will be left in the internal buffer, so it can be read again.
        """
        seplen = len(separator)
        ikiwa seplen == 0:
            raise ValueError('Separator should be at least one-byte string')

        ikiwa self._exception is not None:
            raise self._exception

        # Consume whole buffer except last bytes, which length is
        # one less than seplen. Let's check corner cases with
        # separator='SEPARATOR':
        # * we have received almost complete separator (without last
        #   byte). i.e buffer='some textSEPARATO'. In this case we
        #   can safely consume len(separator) - 1 bytes.
        # * last byte of buffer is first byte of separator, i.e.
        #   buffer='abcdefghijklmnopqrS'. We may safely consume
        #   everything except that last byte, but this require to
        #   analyze bytes of buffer that match partial separator.
        #   This is slow and/or require FSM. For this case our
        #   implementation is not optimal, since require rescanning
        #   of data that is known to not belong to separator. In
        #   real world, separator will not be so long to notice
        #   performance problems. Even when reading MIME-encoded
        #   messages :)

        # `offset` is the number of bytes kutoka the beginning of the buffer
        # where there is no occurrence of `separator`.
        offset = 0

        # Loop until we find `separator` in the buffer, exceed the buffer size,
        # or an EOF has happened.
        while True:
            buflen = len(self._buffer)

            # Check ikiwa we now have enough data in the buffer for `separator` to
            # fit.
            ikiwa buflen - offset >= seplen:
                isep = self._buffer.find(separator, offset)

                ikiwa isep != -1:
                    # `separator` is in the buffer. `isep` will be used later
                    # to retrieve the data.
                    break

                # see upper comment for explanation.
                offset = buflen + 1 - seplen
                ikiwa offset > self._limit:
                    raise exceptions.LimitOverrunError(
                        'Separator is not found, and chunk exceed the limit',
                        offset)

            # Complete message (with full separator) may be present in buffer
            # even when EOF flag is set. This may happen when the last chunk
            # adds data which makes separator be found. That's why we check for
            # EOF *ater* inspecting the buffer.
            ikiwa self._eof:
                chunk = bytes(self._buffer)
                self._buffer.clear()
                raise exceptions.IncompleteReadError(chunk, None)

            # _wait_for_data() will resume reading ikiwa stream was paused.
            await self._wait_for_data('readuntil')

        ikiwa isep > self._limit:
            raise exceptions.LimitOverrunError(
                'Separator is found, but chunk is longer than limit', isep)

        chunk = self._buffer[:isep + seplen]
        del self._buffer[:isep + seplen]
        self._maybe_resume_transport()
        rudisha bytes(chunk)

    async eleza read(self, n=-1):
        """Read up to `n` bytes kutoka the stream.

        If n is not provided, or set to -1, read until EOF and rudisha all read
        bytes. If the EOF was received and the internal buffer is empty, return
        an empty bytes object.

        If n is zero, rudisha empty bytes object immediately.

        If n is positive, this function try to read `n` bytes, and may return
        less or equal bytes than requested, but at least one byte. If EOF was
        received before any byte is read, this function returns empty byte
        object.

        Returned value is not limited with limit, configured at stream
        creation.

        If stream was paused, this function will automatically resume it if
        needed.
        """

        ikiwa self._exception is not None:
            raise self._exception

        ikiwa n == 0:
            rudisha b''

        ikiwa n < 0:
            # This used to just loop creating a new waiter hoping to
            # collect everything in self._buffer, but that would
            # deadlock ikiwa the subprocess sends more than self.limit
            # bytes.  So just call self.read(self._limit) until EOF.
            blocks = []
            while True:
                block = await self.read(self._limit)
                ikiwa not block:
                    break
                blocks.append(block)
            rudisha b''.join(blocks)

        ikiwa not self._buffer and not self._eof:
            await self._wait_for_data('read')

        # This will work right even ikiwa buffer is less than n bytes
        data = bytes(self._buffer[:n])
        del self._buffer[:n]

        self._maybe_resume_transport()
        rudisha data

    async eleza readexactly(self, n):
        """Read exactly `n` bytes.

        Raise an IncompleteReadError ikiwa EOF is reached before `n` bytes can be
        read. The IncompleteReadError.partial attribute of the exception will
        contain the partial read bytes.

        ikiwa n is zero, rudisha empty bytes object.

        Returned value is not limited with limit, configured at stream
        creation.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        ikiwa n < 0:
            raise ValueError('readexactly size can not be less than zero')

        ikiwa self._exception is not None:
            raise self._exception

        ikiwa n == 0:
            rudisha b''

        while len(self._buffer) < n:
            ikiwa self._eof:
                incomplete = bytes(self._buffer)
                self._buffer.clear()
                raise exceptions.IncompleteReadError(incomplete, n)

            await self._wait_for_data('readexactly')

        ikiwa len(self._buffer) == n:
            data = bytes(self._buffer)
            self._buffer.clear()
        else:
            data = bytes(self._buffer[:n])
            del self._buffer[:n]
        self._maybe_resume_transport()
        rudisha data

    eleza __aiter__(self):
        rudisha self

    async eleza __anext__(self):
        val = await self.readline()
        ikiwa val == b'':
            raise StopAsyncIteration
        rudisha val
