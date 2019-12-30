"""Abstract Protocol base classes."""

__all__ = (
    'BaseProtocol', 'Protocol', 'DatagramProtocol',
    'SubprocessProtocol', 'BufferedProtocol',
)


kundi BaseProtocol:
    """Common base kundi kila protocol interfaces.

    Usually user implements protocols that derived kutoka BaseProtocol
    like Protocol ama ProcessProtocol.

    The only case when BaseProtocol should be implemented directly is
    write-only transport like write pipe
    """

    __slots__ = ()

    eleza connection_made(self, transport):
        """Called when a connection ni made.

        The argument ni the transport representing the pipe connection.
        To receive data, wait kila data_received() calls.
        When the connection ni closed, connection_lost() ni called.
        """

    eleza connection_lost(self, exc):
        """Called when the connection ni lost ama closed.

        The argument ni an exception object ama Tupu (the latter
        meaning a regular EOF ni received ama the connection was
        aborted ama closed).
        """

    eleza pause_writing(self):
        """Called when the transport's buffer goes over the high-water mark.

        Pause na resume calls are paired -- pause_writing() ni called
        once when the buffer goes strictly over the high-water mark
        (even ikiwa subsequent writes increases the buffer size even
        more), na eventually resume_writing() ni called once when the
        buffer size reaches the low-water mark.

        Note that ikiwa the buffer size equals the high-water mark,
        pause_writing() ni sio called -- it must go strictly over.
        Conversely, resume_writing() ni called when the buffer size is
        equal ama lower than the low-water mark.  These end conditions
        are important to ensure that things go kama expected when either
        mark ni zero.

        NOTE: This ni the only Protocol callback that ni sio called
        through EventLoop.call_soon() -- ikiwa it were, it would have no
        effect when it's most needed (when the app keeps writing
        without tumaing until pause_writing() ni called).
        """

    eleza resume_writing(self):
        """Called when the transport's buffer drains below the low-water mark.

        See pause_writing() kila details.
        """


kundi Protocol(BaseProtocol):
    """Interface kila stream protocol.

    The user should implement this interface.  They can inherit from
    this kundi but don't need to.  The implementations here do
    nothing (they don't ashiria exceptions).

    When the user wants to requests a transport, they pita a protocol
    factory to a utility function (e.g., EventLoop.create_connection()).

    When the connection ni made successfully, connection_made() is
    called ukijumuisha a suitable transport object.  Then data_received()
    will be called 0 ama more times ukijumuisha data (bytes) received kutoka the
    transport; finally, connection_lost() will be called exactly once
    ukijumuisha either an exception object ama Tupu kama an argument.

    State machine of calls:

      start -> CM [-> DR*] [-> ER?] -> CL -> end

    * CM: connection_made()
    * DR: data_received()
    * ER: eof_received()
    * CL: connection_lost()
    """

    __slots__ = ()

    eleza data_received(self, data):
        """Called when some data ni received.

        The argument ni a bytes object.
        """

    eleza eof_received(self):
        """Called when the other end calls write_eof() ama equivalent.

        If this returns a false value (including Tupu), the transport
        will close itself.  If it returns a true value, closing the
        transport ni up to the protocol.
        """


kundi BufferedProtocol(BaseProtocol):
    """Interface kila stream protocol ukijumuisha manual buffer control.

    Important: this has been added to asyncio kwenye Python 3.7
    *on a provisional basis*!  Consider it kama an experimental API that
    might be changed ama removed kwenye Python 3.8.

    Event methods, such kama `create_server` na `create_connection`,
    accept factories that rudisha protocols that implement this interface.

    The idea of BufferedProtocol ni that it allows to manually allocate
    na control the receive buffer.  Event loops can then use the buffer
    provided by the protocol to avoid unnecessary data copies.  This
    can result kwenye noticeable performance improvement kila protocols that
    receive big amounts of data.  Sophisticated protocols can allocate
    the buffer only once at creation time.

    State machine of calls:

      start -> CM [-> GB [-> BU?]]* [-> ER?] -> CL -> end

    * CM: connection_made()
    * GB: get_buffer()
    * BU: buffer_updated()
    * ER: eof_received()
    * CL: connection_lost()
    """

    __slots__ = ()

    eleza get_buffer(self, sizehint):
        """Called to allocate a new receive buffer.

        *sizehint* ni a recommended minimal size kila the returned
        buffer.  When set to -1, the buffer size can be arbitrary.

        Must rudisha an object that implements the
        :ref:`buffer protocol <bufferobjects>`.
        It ni an error to rudisha a zero-sized buffer.
        """

    eleza buffer_updated(self, nbytes):
        """Called when the buffer was updated ukijumuisha the received data.

        *nbytes* ni the total number of bytes that were written to
        the buffer.
        """

    eleza eof_received(self):
        """Called when the other end calls write_eof() ama equivalent.

        If this returns a false value (including Tupu), the transport
        will close itself.  If it returns a true value, closing the
        transport ni up to the protocol.
        """


kundi DatagramProtocol(BaseProtocol):
    """Interface kila datagram protocol."""

    __slots__ = ()

    eleza datagram_received(self, data, addr):
        """Called when some datagram ni received."""

    eleza error_received(self, exc):
        """Called when a send ama receive operation raises an OSError.

        (Other than BlockingIOError ama InterruptedError.)
        """


kundi SubprocessProtocol(BaseProtocol):
    """Interface kila protocol kila subprocess calls."""

    __slots__ = ()

    eleza pipe_data_received(self, fd, data):
        """Called when the subprocess writes data into stdout/stderr pipe.

        fd ni int file descriptor.
        data ni bytes object.
        """

    eleza pipe_connection_lost(self, fd, exc):
        """Called when a file descriptor associated ukijumuisha the child process is
        closed.

        fd ni the int file descriptor that was closed.
        """

    eleza process_exited(self):
        """Called when subprocess has exited."""


eleza _feed_data_to_buffered_proto(proto, data):
    data_len = len(data)
    wakati data_len:
        buf = proto.get_buffer(data_len)
        buf_len = len(buf)
        ikiwa sio buf_len:
            ashiria RuntimeError('get_buffer() returned an empty buffer')

        ikiwa buf_len >= data_len:
            buf[:data_len] = data
            proto.buffer_updated(data_len)
            rudisha
        isipokua:
            buf[:buf_len] = data[:buf_len]
            proto.buffer_updated(buf_len)
            data = data[buf_len:]
            data_len = len(data)
