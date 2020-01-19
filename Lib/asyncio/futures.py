"""A Future kundi similar to the one kwenye PEP 3148."""

__all__ = (
    'Future', 'wrap_future', 'isfuture',
)

agiza concurrent.futures
agiza contextvars
agiza logging
agiza sys

kutoka . agiza base_futures
kutoka . agiza events
kutoka . agiza exceptions
kutoka . agiza format_helpers


isfuture = base_futures.isfuture


_PENDING = base_futures._PENDING
_CANCELLED = base_futures._CANCELLED
_FINISHED = base_futures._FINISHED


STACK_DEBUG = logging.DEBUG - 1  # heavy-duty debugging


kundi Future:
    """This kundi ni *almost* compatible ukijumuisha concurrent.futures.Future.

    Differences:

    - This kundi ni sio thread-safe.

    - result() na exception() do sio take a timeout argument na
      ashiria an exception when the future isn't done yet.

    - Callbacks registered ukijumuisha add_done_callback() are always called
      via the event loop's call_soon().

    - This kundi ni sio compatible ukijumuisha the wait() na as_completed()
      methods kwenye the concurrent.futures package.

    (In Python 3.4 ama later we may be able to unify the implementations.)
    """

    # Class variables serving kama defaults kila instance variables.
    _state = _PENDING
    _result = Tupu
    _exception = Tupu
    _loop = Tupu
    _source_traceback = Tupu

    # This field ni used kila a dual purpose:
    # - Its presence ni a marker to declare that a kundi implements
    #   the Future protocol (i.e. ni intended to be duck-type compatible).
    #   The value must also be not-Tupu, to enable a subkundi to declare
    #   that it ni sio compatible by setting this to Tupu.
    # - It ni set by __iter__() below so that Task._step() can tell
    #   the difference between
    #   `await Future()` or`tuma kutoka Future()` (correct) vs.
    #   `tuma Future()` (incorrect).
    _asyncio_future_blocking = Uongo

    __log_traceback = Uongo

    eleza __init__(self, *, loop=Tupu):
        """Initialize the future.

        The optional event_loop argument allows explicitly setting the event
        loop object used by the future. If it's sio provided, the future uses
        the default event loop.
        """
        ikiwa loop ni Tupu:
            self._loop = events.get_event_loop()
        isipokua:
            self._loop = loop
        self._callbacks = []
        ikiwa self._loop.get_debug():
            self._source_traceback = format_helpers.extract_stack(
                sys._getframe(1))

    _repr_info = base_futures._future_repr_info

    eleza __repr__(self):
        rudisha '<{} {}>'.format(self.__class__.__name__,
                                ' '.join(self._repr_info()))

    eleza __del__(self):
        ikiwa sio self.__log_traceback:
            # set_exception() was sio called, ama result() ama exception()
            # has consumed the exception
            rudisha
        exc = self._exception
        context = {
            'message':
                f'{self.__class__.__name__} exception was never retrieved',
            'exception': exc,
            'future': self,
        }
        ikiwa self._source_traceback:
            context['source_traceback'] = self._source_traceback
        self._loop.call_exception_handler(context)

    @property
    eleza _log_traceback(self):
        rudisha self.__log_traceback

    @_log_traceback.setter
    eleza _log_traceback(self, val):
        ikiwa bool(val):
            ashiria ValueError('_log_traceback can only be set to Uongo')
        self.__log_traceback = Uongo

    eleza get_loop(self):
        """Return the event loop the Future ni bound to."""
        rudisha self._loop

    eleza cancel(self):
        """Cancel the future na schedule callbacks.

        If the future ni already done ama cancelled, rudisha Uongo.  Otherwise,
        change the future's state to cancelled, schedule the callbacks na
        rudisha Kweli.
        """
        self.__log_traceback = Uongo
        ikiwa self._state != _PENDING:
            rudisha Uongo
        self._state = _CANCELLED
        self.__schedule_callbacks()
        rudisha Kweli

    eleza __schedule_callbacks(self):
        """Internal: Ask the event loop to call all callbacks.

        The callbacks are scheduled to be called kama soon kama possible. Also
        clears the callback list.
        """
        callbacks = self._callbacks[:]
        ikiwa sio callbacks:
            rudisha

        self._callbacks[:] = []
        kila callback, ctx kwenye callbacks:
            self._loop.call_soon(callback, self, context=ctx)

    eleza cancelled(self):
        """Return Kweli ikiwa the future was cancelled."""
        rudisha self._state == _CANCELLED

    # Don't implement running(); see http://bugs.python.org/issue18699

    eleza done(self):
        """Return Kweli ikiwa the future ni done.

        Done means either that a result / exception are available, ama that the
        future was cancelled.
        """
        rudisha self._state != _PENDING

    eleza result(self):
        """Return the result this future represents.

        If the future has been cancelled, raises CancelledError.  If the
        future's result isn't yet available, raises InvalidStateError.  If
        the future ni done na has an exception set, this exception ni raised.
        """
        ikiwa self._state == _CANCELLED:
            ashiria exceptions.CancelledError
        ikiwa self._state != _FINISHED:
            ashiria exceptions.InvalidStateError('Result ni sio ready.')
        self.__log_traceback = Uongo
        ikiwa self._exception ni sio Tupu:
            ashiria self._exception
        rudisha self._result

    eleza exception(self):
        """Return the exception that was set on this future.

        The exception (or Tupu ikiwa no exception was set) ni returned only if
        the future ni done.  If the future has been cancelled, raises
        CancelledError.  If the future isn't done yet, raises
        InvalidStateError.
        """
        ikiwa self._state == _CANCELLED:
            ashiria exceptions.CancelledError
        ikiwa self._state != _FINISHED:
            ashiria exceptions.InvalidStateError('Exception ni sio set.')
        self.__log_traceback = Uongo
        rudisha self._exception

    eleza add_done_callback(self, fn, *, context=Tupu):
        """Add a callback to be run when the future becomes done.

        The callback ni called ukijumuisha a single argument - the future object. If
        the future ni already done when this ni called, the callback is
        scheduled ukijumuisha call_soon.
        """
        ikiwa self._state != _PENDING:
            self._loop.call_soon(fn, self, context=context)
        isipokua:
            ikiwa context ni Tupu:
                context = contextvars.copy_context()
            self._callbacks.append((fn, context))

    # New method haiko kwenye PEP 3148.

    eleza remove_done_callback(self, fn):
        """Remove all instances of a callback kutoka the "call when done" list.

        Returns the number of callbacks removed.
        """
        filtered_callbacks = [(f, ctx)
                              kila (f, ctx) kwenye self._callbacks
                              ikiwa f != fn]
        removed_count = len(self._callbacks) - len(filtered_callbacks)
        ikiwa removed_count:
            self._callbacks[:] = filtered_callbacks
        rudisha removed_count

    # So-called internal methods (note: no set_running_or_notify_cancel()).

    eleza set_result(self, result):
        """Mark the future done na set its result.

        If the future ni already done when this method ni called, raises
        InvalidStateError.
        """
        ikiwa self._state != _PENDING:
            ashiria exceptions.InvalidStateError(f'{self._state}: {self!r}')
        self._result = result
        self._state = _FINISHED
        self.__schedule_callbacks()

    eleza set_exception(self, exception):
        """Mark the future done na set an exception.

        If the future ni already done when this method ni called, raises
        InvalidStateError.
        """
        ikiwa self._state != _PENDING:
            ashiria exceptions.InvalidStateError(f'{self._state}: {self!r}')
        ikiwa isinstance(exception, type):
            exception = exception()
        ikiwa type(exception) ni StopIteration:
            ashiria TypeError("StopIteration interacts badly ukijumuisha generators "
                            "and cannot be raised into a Future")
        self._exception = exception
        self._state = _FINISHED
        self.__schedule_callbacks()
        self.__log_traceback = Kweli

    eleza __await__(self):
        ikiwa sio self.done():
            self._asyncio_future_blocking = Kweli
            tuma self  # This tells Task to wait kila completion.
        ikiwa sio self.done():
            ashiria RuntimeError("await wasn't used ukijumuisha future")
        rudisha self.result()  # May ashiria too.

    __iter__ = __await__  # make compatible ukijumuisha 'tuma from'.


# Needed kila testing purposes.
_PyFuture = Future


eleza _get_loop(fut):
    # Tries to call Future.get_loop() ikiwa it's available.
    # Otherwise fallbacks to using the old '_loop' property.
    jaribu:
        get_loop = fut.get_loop
    tatizo AttributeError:
        pita
    isipokua:
        rudisha get_loop()
    rudisha fut._loop


eleza _set_result_unless_cancelled(fut, result):
    """Helper setting the result only ikiwa the future was sio cancelled."""
    ikiwa fut.cancelled():
        rudisha
    fut.set_result(result)


eleza _convert_future_exc(exc):
    exc_class = type(exc)
    ikiwa exc_class ni concurrent.futures.CancelledError:
        rudisha exceptions.CancelledError(*exc.args)
    lasivyo exc_class ni concurrent.futures.TimeoutError:
        rudisha exceptions.TimeoutError(*exc.args)
    lasivyo exc_class ni concurrent.futures.InvalidStateError:
        rudisha exceptions.InvalidStateError(*exc.args)
    isipokua:
        rudisha exc


eleza _set_concurrent_future_state(concurrent, source):
    """Copy state kutoka a future to a concurrent.futures.Future."""
    assert source.done()
    ikiwa source.cancelled():
        concurrent.cancel()
    ikiwa sio concurrent.set_running_or_notify_cancel():
        rudisha
    exception = source.exception()
    ikiwa exception ni sio Tupu:
        concurrent.set_exception(_convert_future_exc(exception))
    isipokua:
        result = source.result()
        concurrent.set_result(result)


eleza _copy_future_state(source, dest):
    """Internal helper to copy state kutoka another Future.

    The other Future may be a concurrent.futures.Future.
    """
    assert source.done()
    ikiwa dest.cancelled():
        rudisha
    assert sio dest.done()
    ikiwa source.cancelled():
        dest.cancel()
    isipokua:
        exception = source.exception()
        ikiwa exception ni sio Tupu:
            dest.set_exception(_convert_future_exc(exception))
        isipokua:
            result = source.result()
            dest.set_result(result)


eleza _chain_future(source, destination):
    """Chain two futures so that when one completes, so does the other.

    The result (or exception) of source will be copied to destination.
    If destination ni cancelled, source gets cancelled too.
    Compatible ukijumuisha both asyncio.Future na concurrent.futures.Future.
    """
    ikiwa sio isfuture(source) na sio isinstance(source,
                                               concurrent.futures.Future):
        ashiria TypeError('A future ni required kila source argument')
    ikiwa sio isfuture(destination) na sio isinstance(destination,
                                                    concurrent.futures.Future):
        ashiria TypeError('A future ni required kila destination argument')
    source_loop = _get_loop(source) ikiwa isfuture(source) isipokua Tupu
    dest_loop = _get_loop(destination) ikiwa isfuture(destination) isipokua Tupu

    eleza _set_state(future, other):
        ikiwa isfuture(future):
            _copy_future_state(other, future)
        isipokua:
            _set_concurrent_future_state(future, other)

    eleza _call_check_cancel(destination):
        ikiwa destination.cancelled():
            ikiwa source_loop ni Tupu ama source_loop ni dest_loop:
                source.cancel()
            isipokua:
                source_loop.call_soon_threadsafe(source.cancel)

    eleza _call_set_state(source):
        ikiwa (destination.cancelled() na
                dest_loop ni sio Tupu na dest_loop.is_closed()):
            rudisha
        ikiwa dest_loop ni Tupu ama dest_loop ni source_loop:
            _set_state(destination, source)
        isipokua:
            dest_loop.call_soon_threadsafe(_set_state, destination, source)

    destination.add_done_callback(_call_check_cancel)
    source.add_done_callback(_call_set_state)


eleza wrap_future(future, *, loop=Tupu):
    """Wrap concurrent.futures.Future object."""
    ikiwa isfuture(future):
        rudisha future
    assert isinstance(future, concurrent.futures.Future), \
        f'concurrent.futures.Future ni expected, got {future!r}'
    ikiwa loop ni Tupu:
        loop = events.get_event_loop()
    new_future = loop.create_future()
    _chain_future(future, new_future)
    rudisha new_future


jaribu:
    agiza _asyncio
tatizo ImportError:
    pita
isipokua:
    # _CFuture ni needed kila tests.
    Future = _CFuture = _asyncio.Future
