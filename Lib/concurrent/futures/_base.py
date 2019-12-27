# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

agiza collections
agiza logging
agiza threading
agiza time

FIRST_COMPLETED = 'FIRST_COMPLETED'
FIRST_EXCEPTION = 'FIRST_EXCEPTION'
ALL_COMPLETED = 'ALL_COMPLETED'
_AS_COMPLETED = '_AS_COMPLETED'

# Possible future states (for internal use by the futures package).
PENDING = 'PENDING'
RUNNING = 'RUNNING'
# The future was cancelled by the user...
CANCELLED = 'CANCELLED'
# ...and _Waiter.add_cancelled() was called by a worker.
CANCELLED_AND_NOTIFIED = 'CANCELLED_AND_NOTIFIED'
FINISHED = 'FINISHED'

_FUTURE_STATES = [
    PENDING,
    RUNNING,
    CANCELLED,
    CANCELLED_AND_NOTIFIED,
    FINISHED
]

_STATE_TO_DESCRIPTION_MAP = {
    PENDING: "pending",
    RUNNING: "running",
    CANCELLED: "cancelled",
    CANCELLED_AND_NOTIFIED: "cancelled",
    FINISHED: "finished"
}

# Logger for internal use by the futures package.
LOGGER = logging.getLogger("concurrent.futures")

kundi Error(Exception):
    """Base kundi for all future-related exceptions."""
    pass

kundi CancelledError(Error):
    """The Future was cancelled."""
    pass

kundi TimeoutError(Error):
    """The operation exceeded the given deadline."""
    pass

kundi InvalidStateError(Error):
    """The operation is not allowed in this state."""
    pass

kundi _Waiter(object):
    """Provides the event that wait() and as_completed() block on."""
    eleza __init__(self):
        self.event = threading.Event()
        self.finished_futures = []

    eleza add_result(self, future):
        self.finished_futures.append(future)

    eleza add_exception(self, future):
        self.finished_futures.append(future)

    eleza add_cancelled(self, future):
        self.finished_futures.append(future)

kundi _AsCompletedWaiter(_Waiter):
    """Used by as_completed()."""

    eleza __init__(self):
        super(_AsCompletedWaiter, self).__init__()
        self.lock = threading.Lock()

    eleza add_result(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_result(future)
            self.event.set()

    eleza add_exception(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_exception(future)
            self.event.set()

    eleza add_cancelled(self, future):
        with self.lock:
            super(_AsCompletedWaiter, self).add_cancelled(future)
            self.event.set()

kundi _FirstCompletedWaiter(_Waiter):
    """Used by wait(return_when=FIRST_COMPLETED)."""

    eleza add_result(self, future):
        super().add_result(future)
        self.event.set()

    eleza add_exception(self, future):
        super().add_exception(future)
        self.event.set()

    eleza add_cancelled(self, future):
        super().add_cancelled(future)
        self.event.set()

kundi _AllCompletedWaiter(_Waiter):
    """Used by wait(return_when=FIRST_EXCEPTION and ALL_COMPLETED)."""

    eleza __init__(self, num_pending_calls, stop_on_exception):
        self.num_pending_calls = num_pending_calls
        self.stop_on_exception = stop_on_exception
        self.lock = threading.Lock()
        super().__init__()

    eleza _decrement_pending_calls(self):
        with self.lock:
            self.num_pending_calls -= 1
            ikiwa not self.num_pending_calls:
                self.event.set()

    eleza add_result(self, future):
        super().add_result(future)
        self._decrement_pending_calls()

    eleza add_exception(self, future):
        super().add_exception(future)
        ikiwa self.stop_on_exception:
            self.event.set()
        else:
            self._decrement_pending_calls()

    eleza add_cancelled(self, future):
        super().add_cancelled(future)
        self._decrement_pending_calls()

kundi _AcquireFutures(object):
    """A context manager that does an ordered acquire of Future conditions."""

    eleza __init__(self, futures):
        self.futures = sorted(futures, key=id)

    eleza __enter__(self):
        for future in self.futures:
            future._condition.acquire()

    eleza __exit__(self, *args):
        for future in self.futures:
            future._condition.release()

eleza _create_and_install_waiters(fs, return_when):
    ikiwa return_when == _AS_COMPLETED:
        waiter = _AsCompletedWaiter()
    elikiwa return_when == FIRST_COMPLETED:
        waiter = _FirstCompletedWaiter()
    else:
        pending_count = sum(
                f._state not in [CANCELLED_AND_NOTIFIED, FINISHED] for f in fs)

        ikiwa return_when == FIRST_EXCEPTION:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=True)
        elikiwa return_when == ALL_COMPLETED:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=False)
        else:
            raise ValueError("Invalid rudisha condition: %r" % return_when)

    for f in fs:
        f._waiters.append(waiter)

    rudisha waiter


eleza _yield_finished_futures(fs, waiter, ref_collect):
    """
    Iterate on the list *fs*, yielding finished futures one by one in
    reverse order.
    Before yielding a future, *waiter* is removed kutoka its waiters
    and the future is removed kutoka each set in the collection of sets
    *ref_collect*.

    The aim of this function is to avoid keeping stale references after
    the future is yielded and before the iterator resumes.
    """
    while fs:
        f = fs[-1]
        for futures_set in ref_collect:
            futures_set.remove(f)
        with f._condition:
            f._waiters.remove(waiter)
        del f
        # Careful not to keep a reference to the popped value
        yield fs.pop()


eleza as_completed(fs, timeout=None):
    """An iterator over the given futures that yields each as it completes.

    Args:
        fs: The sequence of Futures (possibly created by different Executors) to
            iterate over.
        timeout: The maximum number of seconds to wait. If None, then there
            is no limit on the wait time.

    Returns:
        An iterator that yields the given Futures as they complete (finished or
        cancelled). If any given Futures are duplicated, they will be returned
        once.

    Raises:
        TimeoutError: If the entire result iterator could not be generated
            before the given timeout.
    """
    ikiwa timeout is not None:
        end_time = timeout + time.monotonic()

    fs = set(fs)
    total_futures = len(fs)
    with _AcquireFutures(fs):
        finished = set(
                f for f in fs
                ikiwa f._state in [CANCELLED_AND_NOTIFIED, FINISHED])
        pending = fs - finished
        waiter = _create_and_install_waiters(fs, _AS_COMPLETED)
    finished = list(finished)
    try:
        yield kutoka _yield_finished_futures(finished, waiter,
                                           ref_collect=(fs,))

        while pending:
            ikiwa timeout is None:
                wait_timeout = None
            else:
                wait_timeout = end_time - time.monotonic()
                ikiwa wait_timeout < 0:
                    raise TimeoutError(
                            '%d (of %d) futures unfinished' % (
                            len(pending), total_futures))

            waiter.event.wait(wait_timeout)

            with waiter.lock:
                finished = waiter.finished_futures
                waiter.finished_futures = []
                waiter.event.clear()

            # reverse to keep finishing order
            finished.reverse()
            yield kutoka _yield_finished_futures(finished, waiter,
                                               ref_collect=(fs, pending))

    finally:
        # Remove waiter kutoka unfinished futures
        for f in fs:
            with f._condition:
                f._waiters.remove(waiter)

DoneAndNotDoneFutures = collections.namedtuple(
        'DoneAndNotDoneFutures', 'done not_done')
eleza wait(fs, timeout=None, return_when=ALL_COMPLETED):
    """Wait for the futures in the given sequence to complete.

    Args:
        fs: The sequence of Futures (possibly created by different Executors) to
            wait upon.
        timeout: The maximum number of seconds to wait. If None, then there
            is no limit on the wait time.
        return_when: Indicates when this function should return. The options
            are:

            FIRST_COMPLETED - Return when any future finishes or is
                              cancelled.
            FIRST_EXCEPTION - Return when any future finishes by raising an
                              exception. If no future raises an exception
                              then it is equivalent to ALL_COMPLETED.
            ALL_COMPLETED -   Return when all futures finish or are cancelled.

    Returns:
        A named 2-tuple of sets. The first set, named 'done', contains the
        futures that completed (is finished or cancelled) before the wait
        completed. The second set, named 'not_done', contains uncompleted
        futures.
    """
    with _AcquireFutures(fs):
        done = set(f for f in fs
                   ikiwa f._state in [CANCELLED_AND_NOTIFIED, FINISHED])
        not_done = set(fs) - done

        ikiwa (return_when == FIRST_COMPLETED) and done:
            rudisha DoneAndNotDoneFutures(done, not_done)
        elikiwa (return_when == FIRST_EXCEPTION) and done:
            ikiwa any(f for f in done
                   ikiwa not f.cancelled() and f.exception() is not None):
                rudisha DoneAndNotDoneFutures(done, not_done)

        ikiwa len(done) == len(fs):
            rudisha DoneAndNotDoneFutures(done, not_done)

        waiter = _create_and_install_waiters(fs, return_when)

    waiter.event.wait(timeout)
    for f in fs:
        with f._condition:
            f._waiters.remove(waiter)

    done.update(waiter.finished_futures)
    rudisha DoneAndNotDoneFutures(done, set(fs) - done)

kundi Future(object):
    """Represents the result of an asynchronous computation."""

    eleza __init__(self):
        """Initializes the future. Should not be called by clients."""
        self._condition = threading.Condition()
        self._state = PENDING
        self._result = None
        self._exception = None
        self._waiters = []
        self._done_callbacks = []

    eleza _invoke_callbacks(self):
        for callback in self._done_callbacks:
            try:
                callback(self)
            except Exception:
                LOGGER.exception('exception calling callback for %r', self)

    eleza __repr__(self):
        with self._condition:
            ikiwa self._state == FINISHED:
                ikiwa self._exception:
                    rudisha '<%s at %#x state=%s raised %s>' % (
                        self.__class__.__name__,
                        id(self),
                        _STATE_TO_DESCRIPTION_MAP[self._state],
                        self._exception.__class__.__name__)
                else:
                    rudisha '<%s at %#x state=%s returned %s>' % (
                        self.__class__.__name__,
                        id(self),
                        _STATE_TO_DESCRIPTION_MAP[self._state],
                        self._result.__class__.__name__)
            rudisha '<%s at %#x state=%s>' % (
                    self.__class__.__name__,
                    id(self),
                   _STATE_TO_DESCRIPTION_MAP[self._state])

    eleza cancel(self):
        """Cancel the future ikiwa possible.

        Returns True ikiwa the future was cancelled, False otherwise. A future
        cannot be cancelled ikiwa it is running or has already completed.
        """
        with self._condition:
            ikiwa self._state in [RUNNING, FINISHED]:
                rudisha False

            ikiwa self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                rudisha True

            self._state = CANCELLED
            self._condition.notify_all()

        self._invoke_callbacks()
        rudisha True

    eleza cancelled(self):
        """Return True ikiwa the future was cancelled."""
        with self._condition:
            rudisha self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]

    eleza running(self):
        """Return True ikiwa the future is currently executing."""
        with self._condition:
            rudisha self._state == RUNNING

    eleza done(self):
        """Return True of the future was cancelled or finished executing."""
        with self._condition:
            rudisha self._state in [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]

    eleza __get_result(self):
        ikiwa self._exception:
            raise self._exception
        else:
            rudisha self._result

    eleza add_done_callback(self, fn):
        """Attaches a callable that will be called when the future finishes.

        Args:
            fn: A callable that will be called with this future as its only
                argument when the future completes or is cancelled. The callable
                will always be called by a thread in the same process in which
                it was added. If the future has already completed or been
                cancelled then the callable will be called immediately. These
                callables are called in the order that they were added.
        """
        with self._condition:
            ikiwa self._state not in [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]:
                self._done_callbacks.append(fn)
                return
        try:
            fn(self)
        except Exception:
            LOGGER.exception('exception calling callback for %r', self)

    eleza result(self, timeout=None):
        """Return the result of the call that the future represents.

        Args:
            timeout: The number of seconds to wait for the result ikiwa the future
                isn't done. If None, then there is no limit on the wait time.

        Returns:
            The result of the call that the future represents.

        Raises:
            CancelledError: If the future was cancelled.
            TimeoutError: If the future didn't finish executing before the given
                timeout.
            Exception: If the call raised then that exception will be raised.
        """
        with self._condition:
            ikiwa self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                raise CancelledError()
            elikiwa self._state == FINISHED:
                rudisha self.__get_result()

            self._condition.wait(timeout)

            ikiwa self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                raise CancelledError()
            elikiwa self._state == FINISHED:
                rudisha self.__get_result()
            else:
                raise TimeoutError()

    eleza exception(self, timeout=None):
        """Return the exception raised by the call that the future represents.

        Args:
            timeout: The number of seconds to wait for the exception ikiwa the
                future isn't done. If None, then there is no limit on the wait
                time.

        Returns:
            The exception raised by the call that the future represents or None
            ikiwa the call completed without raising.

        Raises:
            CancelledError: If the future was cancelled.
            TimeoutError: If the future didn't finish executing before the given
                timeout.
        """

        with self._condition:
            ikiwa self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                raise CancelledError()
            elikiwa self._state == FINISHED:
                rudisha self._exception

            self._condition.wait(timeout)

            ikiwa self._state in [CANCELLED, CANCELLED_AND_NOTIFIED]:
                raise CancelledError()
            elikiwa self._state == FINISHED:
                rudisha self._exception
            else:
                raise TimeoutError()

    # The following methods should only be used by Executors and in tests.
    eleza set_running_or_notify_cancel(self):
        """Mark the future as running or process any cancel notifications.

        Should only be used by Executor implementations and unit tests.

        If the future has been cancelled (cancel() was called and returned
        True) then any threads waiting on the future completing (though calls
        to as_completed() or wait()) are notified and False is returned.

        If the future was not cancelled then it is put in the running state
        (future calls to running() will rudisha True) and True is returned.

        This method should be called by Executor implementations before
        executing the work associated with this future. If this method returns
        False then the work should not be executed.

        Returns:
            False ikiwa the Future was cancelled, True otherwise.

        Raises:
            RuntimeError: ikiwa this method was already called or ikiwa set_result()
                or set_exception() was called.
        """
        with self._condition:
            ikiwa self._state == CANCELLED:
                self._state = CANCELLED_AND_NOTIFIED
                for waiter in self._waiters:
                    waiter.add_cancelled(self)
                # self._condition.notify_all() is not necessary because
                # self.cancel() triggers a notification.
                rudisha False
            elikiwa self._state == PENDING:
                self._state = RUNNING
                rudisha True
            else:
                LOGGER.critical('Future %s in unexpected state: %s',
                                id(self),
                                self._state)
                raise RuntimeError('Future in unexpected state')

    eleza set_result(self, result):
        """Sets the rudisha value of work associated with the future.

        Should only be used by Executor implementations and unit tests.
        """
        with self._condition:
            ikiwa self._state in {CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED}:
                raise InvalidStateError('{}: {!r}'.format(self._state, self))
            self._result = result
            self._state = FINISHED
            for waiter in self._waiters:
                waiter.add_result(self)
            self._condition.notify_all()
        self._invoke_callbacks()

    eleza set_exception(self, exception):
        """Sets the result of the future as being the given exception.

        Should only be used by Executor implementations and unit tests.
        """
        with self._condition:
            ikiwa self._state in {CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED}:
                raise InvalidStateError('{}: {!r}'.format(self._state, self))
            self._exception = exception
            self._state = FINISHED
            for waiter in self._waiters:
                waiter.add_exception(self)
            self._condition.notify_all()
        self._invoke_callbacks()

kundi Executor(object):
    """This is an abstract base kundi for concrete asynchronous executors."""

    eleza submit(*args, **kwargs):
        """Submits a callable to be executed with the given arguments.

        Schedules the callable to be executed as fn(*args, **kwargs) and returns
        a Future instance representing the execution of the callable.

        Returns:
            A Future representing the given call.
        """
        ikiwa len(args) >= 2:
            pass
        elikiwa not args:
            raise TypeError("descriptor 'submit' of 'Executor' object "
                            "needs an argument")
        elikiwa 'fn' in kwargs:
            agiza warnings
            warnings.warn("Passing 'fn' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            raise TypeError('submit expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        raise NotImplementedError()
    submit.__text_signature__ = '($self, fn, /, *args, **kwargs)'

    eleza map(self, fn, *iterables, timeout=None, chunksize=1):
        """Returns an iterator equivalent to map(fn, iter).

        Args:
            fn: A callable that will take as many arguments as there are
                passed iterables.
            timeout: The maximum number of seconds to wait. If None, then there
                is no limit on the wait time.
            chunksize: The size of the chunks the iterable will be broken into
                before being passed to a child process. This argument is only
                used by ProcessPoolExecutor; it is ignored by
                ThreadPoolExecutor.

        Returns:
            An iterator equivalent to: map(func, *iterables) but the calls may
            be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could not be generated
                before the given timeout.
            Exception: If fn(*args) raises for any values.
        """
        ikiwa timeout is not None:
            end_time = timeout + time.monotonic()

        fs = [self.submit(fn, *args) for args in zip(*iterables)]

        # Yield must be hidden in closure so that the futures are submitted
        # before the first iterator value is required.
        eleza result_iterator():
            try:
                # reverse to keep finishing order
                fs.reverse()
                while fs:
                    # Careful not to keep a reference to the popped future
                    ikiwa timeout is None:
                        yield fs.pop().result()
                    else:
                        yield fs.pop().result(end_time - time.monotonic())
            finally:
                for future in fs:
                    future.cancel()
        rudisha result_iterator()

    eleza shutdown(self, wait=True):
        """Clean-up the resources associated with the Executor.

        It is safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        Args:
            wait: If True then shutdown will not rudisha until all running
                futures have finished executing and the resources used by the
                executor have been reclaimed.
        """
        pass

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True)
        rudisha False


kundi BrokenExecutor(RuntimeError):
    """
    Raised when a executor has become non-functional after a severe failure.
    """
