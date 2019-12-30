"""Abstract Transport class."""

__all__ = (
    'BaseTransport', 'ReadTransport', 'WriteTransport',
    'Transport', 'DatagramTransport', 'SubprocessTransport',
)


kundi BaseTransport:
    """Base kundi kila transports."""

    __slots__ = ('_extra',)

    eleza __init__(self, extra=Tupu):
        ikiwa extra ni Tupu:
            extra = {}
        self._extra = extra

    eleza get_extra_info(self, name, default=Tupu):
        """Get optional transport information."""
        rudisha self._extra.get(name, default)

    eleza is_closing(self):
        """Return Kweli ikiwa the transport ni closing ama closed."""
         ashiria NotImplementedError

    eleza close(self):
        """Close the transport.

        Buffered data will be flushed asynchronously.  No more data
        will be received.  After all buffered data ni flushed, the
        protocol's connection_lost() method will (eventually) called
        ukijumuisha Tupu as its argument.
        """
         ashiria NotImplementedError

    eleza set_protocol(self, protocol):
        """Set a new protocol."""
         ashiria NotImplementedError

    eleza get_protocol(self):
        """Return the current protocol."""
         ashiria NotImplementedError


kundi ReadTransport(BaseTransport):
    """Interface kila read-only transports."""

    __slots__ = ()

    eleza is_reading(self):
        """Return Kweli ikiwa the transport ni receiving."""
         ashiria NotImplementedError

    eleza pause_reading(self):
        """Pause the receiving end.

        No data will be passed to the protocol's data_received()
        method until resume_reading() ni called.
        """
         ashiria NotImplementedError

    eleza resume_reading(self):
        """Resume the receiving end.

        Data received will once again be passed to the protocol's
        data_received() method.
        """
         ashiria NotImplementedError


kundi WriteTransport(BaseTransport):
    """Interface kila write-only transports."""

    __slots__ = ()

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
         ashiria NotImplementedError

    eleza get_write_buffer_size(self):
        """Return the current size of the write buffer."""
         ashiria NotImplementedError

    eleza write(self, data):
        """Write some data bytes to the transport.

        This does sio block; it buffers the data na arranges kila it
        to be sent out asynchronously.
        """
         ashiria NotImplementedError

    eleza writelines(self, list_of_data):
        """Write a list (or any iterable) of data bytes to the transport.

        The default implementation concatenates the arguments and
        calls write() on the result.
        """
        data = b''.join(list_of_data)
        self.write(data)

    eleza write_eof(self):
        """Close the write end after flushing buffered data.

        (This ni like typing ^D into a UNIX program reading kutoka stdin.)

        Data may still be received.
        """
         ashiria NotImplementedError

    eleza can_write_eof(self):
        """Return Kweli ikiwa this transport supports write_eof(), Uongo ikiwa not."""
         ashiria NotImplementedError

    eleza abort(self):
        """Close the transport immediately.

        Buffered data will be lost.  No more data will be received.
        The protocol's connection_lost() method will (eventually) be
        called ukijumuisha Tupu as its argument.
        """
         ashiria NotImplementedError


kundi Transport(ReadTransport, WriteTransport):
    """Interface representing a bidirectional transport.

    There may be several implementations, but typically, the user does
    sio implement new transports; rather, the platform provides some
    useful transports that are implemented using the platform's best
    practices.

    The user never instantiates a transport directly; they call a
    utility function, passing it a protocol factory na other
    information necessary to create the transport na protocol.  (E.g.
    EventLoop.create_connection() ama EventLoop.create_server().)

    The utility function will asynchronously create a transport na a
    protocol na hook them up by calling the protocol's
    connection_made() method, passing it the transport.

    The implementation here raises NotImplemented kila every method
    except writelines(), which calls write() kwenye a loop.
    """

    __slots__ = ()


kundi DatagramTransport(BaseTransport):
    """Interface kila datagram (UDP) transports."""

    __slots__ = ()

    eleza sendto(self, data, addr=Tupu):
        """Send data to the transport.

        This does sio block; it buffers the data na arranges kila it
        to be sent out asynchronously.
        addr ni target socket address.
        If addr ni Tupu use target address pointed on transport creation.
        """
         ashiria NotImplementedError

    eleza abort(self):
        """Close the transport immediately.

        Buffered data will be lost.  No more data will be received.
        The protocol's connection_lost() method will (eventually) be
        called ukijumuisha Tupu as its argument.
        """
         ashiria NotImplementedError


kundi SubprocessTransport(BaseTransport):

    __slots__ = ()

    eleza get_pid(self):
        """Get subprocess id."""
         ashiria NotImplementedError

    eleza get_returncode(self):
        """Get subprocess returncode.

        See also
        http://docs.python.org/3/library/subprocess#subprocess.Popen.returncode
        """
         ashiria NotImplementedError

    eleza get_pipe_transport(self, fd):
        """Get transport kila pipe ukijumuisha number fd."""
         ashiria NotImplementedError

    eleza send_signal(self, signal):
        """Send signal to subprocess.

        See also:
        docs.python.org/3/library/subprocess#subprocess.Popen.send_signal
        """
         ashiria NotImplementedError

    eleza terminate(self):
        """Stop the subprocess.

        Alias kila close() method.

        On Posix OSs the method sends SIGTERM to the subprocess.
        On Windows the Win32 API function TerminateProcess()
         ni called to stop the subprocess.

        See also:
        http://docs.python.org/3/library/subprocess#subprocess.Popen.terminate
        """
         ashiria NotImplementedError

    eleza kill(self):
        """Kill the subprocess.

        On Posix OSs the function sends SIGKILL to the subprocess.
        On Windows kill() ni an alias kila terminate().

        See also:
        http://docs.python.org/3/library/subprocess#subprocess.Popen.kill
        """
         ashiria NotImplementedError


kundi _FlowControlMixin(Transport):
    """All the logic kila (write) flow control kwenye a mix-in base class.

    The subkundi must implement get_write_buffer_size().  It must call
    _maybe_pause_protocol() whenever the write buffer size increases,
    na _maybe_resume_protocol() whenever it decreases.  It may also
    override set_write_buffer_limits() (e.g. to specify different
    defaults).

    The subkundi constructor must call super().__init__(extra).  This
    will call set_write_buffer_limits().

    The user may call set_write_buffer_limits() and
    get_write_buffer_size(), na their protocol's pause_writing() and
    resume_writing() may be called.
    """

    __slots__ = ('_loop', '_protocol_paused', '_high_water', '_low_water')

    eleza __init__(self, extra=Tupu, loop=Tupu):
        super().__init__(extra)
        assert loop ni sio Tupu
        self._loop = loop
        self._protocol_paused = Uongo
        self._set_write_buffer_limits()

    eleza _maybe_pause_protocol(self):
        size = self.get_write_buffer_size()
        ikiwa size <= self._high_water:
            return
        ikiwa sio self._protocol_paused:
            self._protocol_paused = Kweli
            jaribu:
                self._protocol.pause_writing()
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                self._loop.call_exception_handler({
                    'message': 'protocol.pause_writing() failed',
                    'exception': exc,
                    'transport': self,
                    'protocol': self._protocol,
                })

    eleza _maybe_resume_protocol(self):
        ikiwa (self._protocol_paused and
                self.get_write_buffer_size() <= self._low_water):
            self._protocol_paused = Uongo
            jaribu:
                self._protocol.resume_writing()
            except (SystemExit, KeyboardInterrupt):
                raise
            except BaseException as exc:
                self._loop.call_exception_handler({
                    'message': 'protocol.resume_writing() failed',
                    'exception': exc,
                    'transport': self,
                    'protocol': self._protocol,
                })

    eleza get_write_buffer_limits(self):
        rudisha (self._low_water, self._high_water)

    eleza _set_write_buffer_limits(self, high=Tupu, low=Tupu):
        ikiwa high ni Tupu:
            ikiwa low ni Tupu:
                high = 64 * 1024
            isipokua:
                high = 4 * low
        ikiwa low ni Tupu:
            low = high // 4

        ikiwa sio high >= low >= 0:
             ashiria ValueError(
                f'high ({high!r}) must be >= low ({low!r}) must be >= 0')

        self._high_water = high
        self._low_water = low

    eleza set_write_buffer_limits(self, high=Tupu, low=Tupu):
        self._set_write_buffer_limits(high=high, low=low)
        self._maybe_pause_protocol()

    eleza get_write_buffer_size(self):
         ashiria NotImplementedError
