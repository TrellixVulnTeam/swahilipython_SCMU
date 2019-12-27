"""A Future kundi similar to the one in PEP 3148."""

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
    """This kundi is *almost* compatible with concurrent.futures.Future.

    Differences:

    - This kundi is not thread-safe.

    - result() and exception() do not take a timeout argument and
      raise an exception when the future isn't done yet.

    - Callbacks registered with add_done_callback() are always called
      via the event loop's call_soon().

    - This kundi is not compatible with the wait() and as_completed()
      methods in the concurrent.futures package.

    (In Python 3.4 or later we may be able to unify the implementations.)
    """

    # Class variables serving as defaults for instance variables.
    _state = _PENDING
    _result = None
    _exception = None
    _loop = None
    _source_traceback = None

    # This field is used for a dual purpose:
    # - Its presence is a marker to declare that a kundi implements
    #   the Future protocol (i.e. is intended to be duck-type compatible).
    #   The value must also be not-None, to enable a subkundi to declare
    #   that it is not compatible by setting this to None.
    # - It is set by __iter__() below so that Task._step() can tell
    #   the difference between
    #   `await Future()` or`yield kutoka Future()` (correct) vs.
    #   `yield Future()` (incorrect).
    _asyncio_future_blocking = False

    __log_traceback = False

    eleza __init__(self, *, loop=None):
        """Initialize the future.

        The optional event_loop argument allows explicitly setting the event
        loop object used by the future. If it's not provided, the future uses
        the default event loop.
        """
        ikiwa loop is None:
            self._loop = events.get_event_loop()
        else:
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
        ikiwa not self.__log_traceback:
            # set_exception() was not called, or result() or exception()
            # has consumed the exception
            return
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
            raise ValueError('_log_traceback can only be set to False')
        self.__log_traceback = False

    eleza get_loop(self):
        """Return the event loop the Future is bound to."""
        rudisha self._loop

    eleza cancel(self):
        """Cancel the future and schedule callbacks.

        If the future is already done or cancelled, rudisha False.  Otherwise,
        change the future's state to cancelled, schedule the callbacks and
        rudisha True.
        """
        self.__log_traceback = False
        ikiwa self._state != _PENDING:
            rudisha False
        self._state = _CANCELLED
        self.__schedule_callbacks()
        rudisha True

    eleza __schedule_callbacks(self):
        """Internal: Ask the event loop to call all callbacks.

        The callbacks are scheduled to be called as soon as possible. Also
        clears the callback list.
        """
        callbacks = self._callbacks[:]
        ikiwa not callbacks:
            return

        self._callbacks[:] = []
        for callback, ctx in callbacks:
            self._loop.call_soon(callback, self, context=ctx)

    eleza cancelled(self):
        """Return True ikiwa the future was cancelled."""
        rudisha self._state == _CANCELLED

    # Don't implement running(); see http://bugs.python.org/issue18699

    eleza done(self):
        """Return True ikiwa the future is done.

        Done means either that a result / exception are available, or that the
        future was cancelled.
        """
        rudisha self._state != _PENDING

    eleza result(self):
        """Return the result this future represents.

        If the future has been cancelled, raises CancelledError.  If the
        future's result isn't yet available, raises InvalidStateError.  If
        the future is done and has an exception set, this exception is raised.
        """
        ikiwa self._state == _CANCELLED:
            raise exceptions.CancelledError
        ikiwa self._state != _FINISHED:
            raise exceptions.InvalidStateError('Result is not ready.')
        self.__log_traceback = False
        ikiwa self._exception is not None:
            raise self._exception
        rudisha self._result

    eleza exception(self):
        """Return the exception that was set on this future.

        The exception (or None ikiwa no exception was set) is returned only if
        the future is done.  If the future has been cancelled, raises
        CancelledError.  If the future isn't done yet, raises
        InvalidStateError.
        """
        ikiwa self._state == _CANCELLED:
            raise exceptions.CancelledError
        ikiwa self._state != _FINISHED:
            raise exceptions.InvalidStateError('Exception is not set.')
        self.__log_traceback = False
        rudisha self._exception

    eleza add_done_callback(self, fn, *, context=None):
        """Add a callback to be run when the future becomes done.

        The callback is called with a single argument - the future object. If
        the future is already done when this is called, the callback is
        scheduled with call_soon.
        """
        ikiwa self._state != _PENDING:
            self._loop.call_soon(fn, self, context=context)
        else:
            ikiwa context is None:
                context = contextvars.copy_context()
            self._callbacks.append((fn, context))

    # New method not in PEP 3148.

    eleza remove_done_callback(self, fn):
        """Remove all instances of a callback kutoka the "call when done" list.

        Returns the number of callbacks removed.
        """
        filtered_callbacks = [(f, ctx)
                              for (f, ctx) in self._callbacks
                              ikiwa f != fn]
        removed_count = len(self._callbacks) - len(filtered_callbacks)
        ikiwa removed_count:
            self._callbacks[:] = filtered_callbacks
        rudisha removed_count

    # So-called internal methods (note: no set_running_or_notify_cancel()).

    eleza set_result(self, result):
        """Mark the future done and set its result.

        If the future is already done when this method is called, raises
        InvalidStateError.
        """
        ikiwa self._state != _PENDING:
            raise exceptions.InvalidStateError(f'{self._state}: {self!r}')
        self._result = result
        self._state = _FINISHED
        self.__schedule_callbacks()

    eleza set_exception(self, exception):
        """Mark the future done and set an exception.

        If the future is already done when this method is called, raises
        InvalidStateError.
        """
        ikiwa self._state != _PENDING:
            raise exceptions.InvalidStateError(f'{self._state}: {self!r}')
        ikiwa isinstance(exception, type):
            exception = exception()
        ikiwa type(exception) is StopIteration:
            raise TypeError("StopIteration interacts badly with generators "
                            "and cannot be raised into a Future")
        self._exception = exception
        self._state = _FINISHED
        self.__schedule_callbacks()
        self.__log_traceback = True

    eleza __await__(self):
        ikiwa not self.done():
            self._asyncio_future_blocking = True
            yield self  # This tells Task to wait for completion.
        ikiwa not self.done():
            raise RuntimeError("await wasn't used with future")
        rudisha self.result()  # May raise too.

    __iter__ = __await__  # make compatible with 'yield kutoka'.


# Needed for testing purposes.
_PyFuture = Future


eleza _get_loop(fut):
    # Tries to call Future.get_loop() ikiwa it's available.
    # Otherwise fallbacks to using the old '_loop' property.
    try:
        get_loop = fut.get_loop
    except AttributeError:
        pass
    else:
        rudisha get_loop()
    rudisha fut._loop


eleza _set_result_unless_cancelled(fut, result):
    """Helper setting the result only ikiwa the future was not cancelled."""
    ikiwa fut.cancelled():
        return
    fut.set_result(result)


eleza _convert_future_exc(exc):
    exc_kundi = type(exc)
    ikiwa exc_kundi is concurrent.futures.CancelledError:
        rudisha exceptions.CancelledError(*exc.args)
    elikiwa exc_kundi is concurrent.futures.TimeoutError:
        rudisha exceptions.TimeoutError(*exc.args)
    elikiwa exc_kundi is concurrent.futures.InvalidStateError:
        rudisha exceptions.InvalidStateError(*exc.args)
    else:
        rudisha exc


eleza _set_concurrent_future_state(concurrent, source):
    """Copy state kutoka a future to a concurrent.futures.Future."""
    assert source.done()
    ikiwa source.cancelled():
        concurrent.cancel()
    ikiwa not concurrent.set_running_or_notify_cancel():
        return
    exception = source.exception()
    ikiwa exception is not None:
        concurrent.set_exception(_convert_future_exc(exception))
    else:
        result = source.result()
        concurrent.set_result(result)


eleza _copy_future_state(source, dest):
    """Internal helper to copy state kutoka another Future.

    The other Future may be a concurrent.futures.Future.
    """
    assert source.done()
    ikiwa dest.cancelled():
        return
    assert not dest.done()
    ikiwa source.cancelled():
        dest.cancel()
    else:
        exception = source.exception()
        ikiwa exception is not None:
            dest.set_exception(_convert_future_exc(exception))
        else:
            result = source.result()
            dest.set_result(result)


eleza _chain_future(source, destination):
    """Chain two futures so that when one completes, so does the other.

    The result (or exception) of source will be copied to destination.
    If destination is cancelled, source gets cancelled too.
    Compatible with both asyncio.Future and concurrent.futures.Future.
    """
    ikiwa not isfuture(source) and not isinstance(source,
                                               concurrent.futures.Future):
        raise TypeError('A future is required for source argument')
    ikiwa not isfuture(destination) and not isinstance(destination,
                                                    concurrent.futures.Future):
        raise TypeError('A future is required for destination argument')
    source_loop = _get_loop(source) ikiwa isfuture(source) else None
    dest_loop = _get_loop(destination) ikiwa isfuture(destination) else None

    eleza _set_state(future, other):
        ikiwa isfuture(future):
            _copy_future_state(other, future)
        else:
            _set_concurrent_future_state(future, other)

    eleza _call_check_cancel(destination):
        ikiwa destination.cancelled():
            ikiwa source_loop is None or source_loop is dest_loop:
                source.cancel()
            else:
                source_loop.call_soon_threadsafe(source.cancel)

    eleza _call_set_state(source):
        ikiwa (destination.cancelled() and
                dest_loop is not None and dest_loop.is_closed()):
            return
        ikiwa dest_loop is None or dest_loop is source_loop:
            _set_state(destination, source)
        else:
            dest_loop.call_soon_threadsafe(_set_state, destination, source)

    destination.add_done_callback(_call_check_cancel)
    source.add_done_callback(_call_set_state)


eleza wrap_future(future, *, loop=None):
    """Wrap concurrent.futures.Future object."""
    ikiwa isfuture(future):
        rudisha future
    assert isinstance(future, concurrent.futures.Future), \
        f'concurrent.futures.Future is expected, got {future!r}'
    ikiwa loop is None:
        loop = events.get_event_loop()
    new_future = loop.create_future()
    _chain_future(future, new_future)
    rudisha new_future


try:
    agiza _asyncio
except ImportError:
    pass
else:
    # _CFuture is needed for tests.
    Future = _CFuture = _asyncio.Future
