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

# Possible future states (kila internal use by the futures package).
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

# Logger kila internal use by the futures package.
LOGGER = logging.getLogger("concurrent.futures")

kundi Error(Exception):
    """Base kundi kila all future-related exceptions."""
    pita

kundi CancelledError(Error):
    """The Future was cancelled."""
    pita

kundi TimeoutError(Error):
    """The operation exceeded the given deadline."""
    pita

kundi InvalidStateError(Error):
    """The operation ni sio allowed kwenye this state."""
    pita

kundi _Waiter(object):
    """Provides the event that wait() na as_completed() block on."""
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
        ukijumuisha self.lock:
            super(_AsCompletedWaiter, self).add_result(future)
            self.event.set()

    eleza add_exception(self, future):
        ukijumuisha self.lock:
            super(_AsCompletedWaiter, self).add_exception(future)
            self.event.set()

    eleza add_cancelled(self, future):
        ukijumuisha self.lock:
            super(_AsCompletedWaiter, self).add_cancelled(future)
            self.event.set()

kundi _FirstCompletedWaiter(_Waiter):
    """Used by wait(rudisha_when=FIRST_COMPLETED)."""

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
    """Used by wait(rudisha_when=FIRST_EXCEPTION na ALL_COMPLETED)."""

    eleza __init__(self, num_pending_calls, stop_on_exception):
        self.num_pending_calls = num_pending_calls
        self.stop_on_exception = stop_on_exception
        self.lock = threading.Lock()
        super().__init__()

    eleza _decrement_pending_calls(self):
        ukijumuisha self.lock:
            self.num_pending_calls -= 1
            ikiwa sio self.num_pending_calls:
                self.event.set()

    eleza add_result(self, future):
        super().add_result(future)
        self._decrement_pending_calls()

    eleza add_exception(self, future):
        super().add_exception(future)
        ikiwa self.stop_on_exception:
            self.event.set()
        isipokua:
            self._decrement_pending_calls()

    eleza add_cancelled(self, future):
        super().add_cancelled(future)
        self._decrement_pending_calls()

kundi _AcquireFutures(object):
    """A context manager that does an ordered acquire of Future conditions."""

    eleza __init__(self, futures):
        self.futures = sorted(futures, key=id)

    eleza __enter__(self):
        kila future kwenye self.futures:
            future._condition.acquire()

    eleza __exit__(self, *args):
        kila future kwenye self.futures:
            future._condition.release()

eleza _create_and_install_waiters(fs, rudisha_when):
    ikiwa rudisha_when == _AS_COMPLETED:
        waiter = _AsCompletedWaiter()
    lasivyo rudisha_when == FIRST_COMPLETED:
        waiter = _FirstCompletedWaiter()
    isipokua:
        pending_count = sum(
                f._state haiko kwenye [CANCELLED_AND_NOTIFIED, FINISHED] kila f kwenye fs)

        ikiwa rudisha_when == FIRST_EXCEPTION:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=Kweli)
        lasivyo rudisha_when == ALL_COMPLETED:
            waiter = _AllCompletedWaiter(pending_count, stop_on_exception=Uongo)
        isipokua:
            ashiria ValueError("Invalid rudisha condition: %r" % rudisha_when)

    kila f kwenye fs:
        f._waiters.append(waiter)

    rudisha waiter


eleza _tuma_finished_futures(fs, waiter, ref_collect):
    """
    Iterate on the list *fs*, tumaing finished futures one by one in
    reverse order.
    Before tumaing a future, *waiter* ni removed kutoka its waiters
    na the future ni removed kutoka each set kwenye the collection of sets
    *ref_collect*.

    The aim of this function ni to avoid keeping stale references after
    the future ni tumaed na before the iterator resumes.
    """
    wakati fs:
        f = fs[-1]
        kila futures_set kwenye ref_collect:
            futures_set.remove(f)
        ukijumuisha f._condition:
            f._waiters.remove(waiter)
        toa f
        # Careful sio to keep a reference to the popped value
        tuma fs.pop()


eleza as_completed(fs, timeout=Tupu):
    """An iterator over the given futures that tumas each kama it completes.

    Args:
        fs: The sequence of Futures (possibly created by different Executors) to
            iterate over.
        timeout: The maximum number of seconds to wait. If Tupu, then there
            ni no limit on the wait time.

    Returns:
        An iterator that tumas the given Futures kama they complete (finished or
        cancelled). If any given Futures are duplicated, they will be rudishaed
        once.

    Raises:
        TimeoutError: If the entire result iterator could sio be generated
            before the given timeout.
    """
    ikiwa timeout ni sio Tupu:
        end_time = timeout + time.monotonic()

    fs = set(fs)
    total_futures = len(fs)
    ukijumuisha _AcquireFutures(fs):
        finished = set(
                f kila f kwenye fs
                ikiwa f._state kwenye [CANCELLED_AND_NOTIFIED, FINISHED])
        pending = fs - finished
        waiter = _create_and_install_waiters(fs, _AS_COMPLETED)
    finished = list(finished)
    jaribu:
        tuma kutoka _tuma_finished_futures(finished, waiter,
                                           ref_collect=(fs,))

        wakati pending:
            ikiwa timeout ni Tupu:
                wait_timeout = Tupu
            isipokua:
                wait_timeout = end_time - time.monotonic()
                ikiwa wait_timeout < 0:
                    ashiria TimeoutError(
                            '%d (of %d) futures unfinished' % (
                            len(pending), total_futures))

            waiter.event.wait(wait_timeout)

            ukijumuisha waiter.lock:
                finished = waiter.finished_futures
                waiter.finished_futures = []
                waiter.event.clear()

            # reverse to keep finishing order
            finished.reverse()
            tuma kutoka _tuma_finished_futures(finished, waiter,
                                               ref_collect=(fs, pending))

    mwishowe:
        # Remove waiter kutoka unfinished futures
        kila f kwenye fs:
            ukijumuisha f._condition:
                f._waiters.remove(waiter)

DoneAndNotDoneFutures = collections.namedtuple(
        'DoneAndNotDoneFutures', 'done not_done')
eleza wait(fs, timeout=Tupu, rudisha_when=ALL_COMPLETED):
    """Wait kila the futures kwenye the given sequence to complete.

    Args:
        fs: The sequence of Futures (possibly created by different Executors) to
            wait upon.
        timeout: The maximum number of seconds to wait. If Tupu, then there
            ni no limit on the wait time.
        rudisha_when: Indicates when this function should rudisha. The options
            are:

            FIRST_COMPLETED - Return when any future finishes ama is
                              cancelled.
            FIRST_EXCEPTION - Return when any future finishes by raising an
                              exception. If no future ashirias an exception
                              then it ni equivalent to ALL_COMPLETED.
            ALL_COMPLETED -   Return when all futures finish ama are cancelled.

    Returns:
        A named 2-tuple of sets. The first set, named 'done', contains the
        futures that completed (is finished ama cancelled) before the wait
        completed. The second set, named 'not_done', contains uncompleted
        futures.
    """
    ukijumuisha _AcquireFutures(fs):
        done = set(f kila f kwenye fs
                   ikiwa f._state kwenye [CANCELLED_AND_NOTIFIED, FINISHED])
        not_done = set(fs) - done

        ikiwa (rudisha_when == FIRST_COMPLETED) na done:
            rudisha DoneAndNotDoneFutures(done, not_done)
        lasivyo (rudisha_when == FIRST_EXCEPTION) na done:
            ikiwa any(f kila f kwenye done
                   ikiwa sio f.cancelled() na f.exception() ni sio Tupu):
                rudisha DoneAndNotDoneFutures(done, not_done)

        ikiwa len(done) == len(fs):
            rudisha DoneAndNotDoneFutures(done, not_done)

        waiter = _create_and_install_waiters(fs, rudisha_when)

    waiter.event.wait(timeout)
    kila f kwenye fs:
        ukijumuisha f._condition:
            f._waiters.remove(waiter)

    done.update(waiter.finished_futures)
    rudisha DoneAndNotDoneFutures(done, set(fs) - done)

kundi Future(object):
    """Represents the result of an asynchronous computation."""

    eleza __init__(self):
        """Initializes the future. Should sio be called by clients."""
        self._condition = threading.Condition()
        self._state = PENDING
        self._result = Tupu
        self._exception = Tupu
        self._waiters = []
        self._done_callbacks = []

    eleza _invoke_callbacks(self):
        kila callback kwenye self._done_callbacks:
            jaribu:
                callback(self)
            tatizo Exception:
                LOGGER.exception('exception calling callback kila %r', self)

    eleza __repr__(self):
        ukijumuisha self._condition:
            ikiwa self._state == FINISHED:
                ikiwa self._exception:
                    rudisha '<%s at %#x state=%s ashiriad %s>' % (
                        self.__class__.__name__,
                        id(self),
                        _STATE_TO_DESCRIPTION_MAP[self._state],
                        self._exception.__class__.__name__)
                isipokua:
                    rudisha '<%s at %#x state=%s rudishaed %s>' % (
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

        Returns Kweli ikiwa the future was cancelled, Uongo otherwise. A future
        cannot be cancelled ikiwa it ni running ama has already completed.
        """
        ukijumuisha self._condition:
            ikiwa self._state kwenye [RUNNING, FINISHED]:
                rudisha Uongo

            ikiwa self._state kwenye [CANCELLED, CANCELLED_AND_NOTIFIED]:
                rudisha Kweli

            self._state = CANCELLED
            self._condition.notify_all()

        self._invoke_callbacks()
        rudisha Kweli

    eleza cancelled(self):
        """Return Kweli ikiwa the future was cancelled."""
        ukijumuisha self._condition:
            rudisha self._state kwenye [CANCELLED, CANCELLED_AND_NOTIFIED]

    eleza running(self):
        """Return Kweli ikiwa the future ni currently executing."""
        ukijumuisha self._condition:
            rudisha self._state == RUNNING

    eleza done(self):
        """Return Kweli of the future was cancelled ama finished executing."""
        ukijumuisha self._condition:
            rudisha self._state kwenye [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]

    eleza __get_result(self):
        ikiwa self._exception:
            ashiria self._exception
        isipokua:
            rudisha self._result

    eleza add_done_callback(self, fn):
        """Attaches a callable that will be called when the future finishes.

        Args:
            fn: A callable that will be called ukijumuisha this future kama its only
                argument when the future completes ama ni cancelled. The callable
                will always be called by a thread kwenye the same process kwenye which
                it was added. If the future has already completed ama been
                cancelled then the callable will be called immediately. These
                callables are called kwenye the order that they were added.
        """
        ukijumuisha self._condition:
            ikiwa self._state haiko kwenye [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]:
                self._done_callbacks.append(fn)
                rudisha
        jaribu:
            fn(self)
        tatizo Exception:
            LOGGER.exception('exception calling callback kila %r', self)

    eleza result(self, timeout=Tupu):
        """Return the result of the call that the future represents.

        Args:
            timeout: The number of seconds to wait kila the result ikiwa the future
                isn't done. If Tupu, then there ni no limit on the wait time.

        Returns:
            The result of the call that the future represents.

        Raises:
            CancelledError: If the future was cancelled.
            TimeoutError: If the future didn't finish executing before the given
                timeout.
            Exception: If the call ashiriad then that exception will be ashiriad.
        """
        ukijumuisha self._condition:
            ikiwa self._state kwenye [CANCELLED, CANCELLED_AND_NOTIFIED]:
                ashiria CancelledError()
            lasivyo self._state == FINISHED:
                rudisha self.__get_result()

            self._condition.wait(timeout)

            ikiwa self._state kwenye [CANCELLED, CANCELLED_AND_NOTIFIED]:
                ashiria CancelledError()
            lasivyo self._state == FINISHED:
                rudisha self.__get_result()
            isipokua:
                ashiria TimeoutError()

    eleza exception(self, timeout=Tupu):
        """Return the exception ashiriad by the call that the future represents.

        Args:
            timeout: The number of seconds to wait kila the exception ikiwa the
                future isn't done. If Tupu, then there ni no limit on the wait
                time.

        Returns:
            The exception ashiriad by the call that the future represents ama Tupu
            ikiwa the call completed without raising.

        Raises:
            CancelledError: If the future was cancelled.
            TimeoutError: If the future didn't finish executing before the given
                timeout.
        """

        ukijumuisha self._condition:
            ikiwa self._state kwenye [CANCELLED, CANCELLED_AND_NOTIFIED]:
                ashiria CancelledError()
            lasivyo self._state == FINISHED:
                rudisha self._exception

            self._condition.wait(timeout)

            ikiwa self._state kwenye [CANCELLED, CANCELLED_AND_NOTIFIED]:
                ashiria CancelledError()
            lasivyo self._state == FINISHED:
                rudisha self._exception
            isipokua:
                ashiria TimeoutError()

    # The following methods should only be used by Executors na kwenye tests.
    eleza set_running_or_notify_cancel(self):
        """Mark the future kama running ama process any cancel notifications.

        Should only be used by Executor implementations na unit tests.

        If the future has been cancelled (cancel() was called na rudishaed
        Kweli) then any threads waiting on the future completing (though calls
        to as_completed() ama wait()) are notified na Uongo ni rudishaed.

        If the future was sio cancelled then it ni put kwenye the running state
        (future calls to running() will rudisha Kweli) na Kweli ni rudishaed.

        This method should be called by Executor implementations before
        executing the work associated ukijumuisha this future. If this method rudishas
        Uongo then the work should sio be executed.

        Returns:
            Uongo ikiwa the Future was cancelled, Kweli otherwise.

        Raises:
            RuntimeError: ikiwa this method was already called ama ikiwa set_result()
                ama set_exception() was called.
        """
        ukijumuisha self._condition:
            ikiwa self._state == CANCELLED:
                self._state = CANCELLED_AND_NOTIFIED
                kila waiter kwenye self._waiters:
                    waiter.add_cancelled(self)
                # self._condition.notify_all() ni sio necessary because
                # self.cancel() triggers a notification.
                rudisha Uongo
            lasivyo self._state == PENDING:
                self._state = RUNNING
                rudisha Kweli
            isipokua:
                LOGGER.critical('Future %s kwenye unexpected state: %s',
                                id(self),
                                self._state)
                ashiria RuntimeError('Future kwenye unexpected state')

    eleza set_result(self, result):
        """Sets the rudisha value of work associated ukijumuisha the future.

        Should only be used by Executor implementations na unit tests.
        """
        ukijumuisha self._condition:
            ikiwa self._state kwenye {CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED}:
                ashiria InvalidStateError('{}: {!r}'.format(self._state, self))
            self._result = result
            self._state = FINISHED
            kila waiter kwenye self._waiters:
                waiter.add_result(self)
            self._condition.notify_all()
        self._invoke_callbacks()

    eleza set_exception(self, exception):
        """Sets the result of the future kama being the given exception.

        Should only be used by Executor implementations na unit tests.
        """
        ukijumuisha self._condition:
            ikiwa self._state kwenye {CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED}:
                ashiria InvalidStateError('{}: {!r}'.format(self._state, self))
            self._exception = exception
            self._state = FINISHED
            kila waiter kwenye self._waiters:
                waiter.add_exception(self)
            self._condition.notify_all()
        self._invoke_callbacks()

kundi Executor(object):
    """This ni an abstract base kundi kila concrete asynchronous executors."""

    eleza submit(*args, **kwargs):
        """Submits a callable to be executed ukijumuisha the given arguments.

        Schedules the callable to be executed kama fn(*args, **kwargs) na rudishas
        a Future instance representing the execution of the callable.

        Returns:
            A Future representing the given call.
        """
        ikiwa len(args) >= 2:
            pita
        lasivyo sio args:
            ashiria TypeError("descriptor 'submit' of 'Executor' object "
                            "needs an argument")
        lasivyo 'fn' kwenye kwargs:
            agiza warnings
            warnings.warn("Passing 'fn' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError('submit expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        ashiria NotImplementedError()
    submit.__text_signature__ = '($self, fn, /, *args, **kwargs)'

    eleza map(self, fn, *iterables, timeout=Tupu, chunksize=1):
        """Returns an iterator equivalent to map(fn, iter).

        Args:
            fn: A callable that will take kama many arguments kama there are
                pitaed iterables.
            timeout: The maximum number of seconds to wait. If Tupu, then there
                ni no limit on the wait time.
            chunksize: The size of the chunks the iterable will be broken into
                before being pitaed to a child process. This argument ni only
                used by ProcessPoolExecutor; it ni ignored by
                ThreadPoolExecutor.

        Returns:
            An iterator equivalent to: map(func, *iterables) but the calls may
            be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could sio be generated
                before the given timeout.
            Exception: If fn(*args) ashirias kila any values.
        """
        ikiwa timeout ni sio Tupu:
            end_time = timeout + time.monotonic()

        fs = [self.submit(fn, *args) kila args kwenye zip(*iterables)]

        # Yield must be hidden kwenye closure so that the futures are submitted
        # before the first iterator value ni required.
        eleza result_iterator():
            jaribu:
                # reverse to keep finishing order
                fs.reverse()
                wakati fs:
                    # Careful sio to keep a reference to the popped future
                    ikiwa timeout ni Tupu:
                        tuma fs.pop().result()
                    isipokua:
                        tuma fs.pop().result(end_time - time.monotonic())
            mwishowe:
                kila future kwenye fs:
                    future.cancel()
        rudisha result_iterator()

    eleza shutdown(self, wait=Kweli):
        """Clean-up the resources associated ukijumuisha the Executor.

        It ni safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        Args:
            wait: If Kweli then shutdown will sio rudisha until all running
                futures have finished executing na the resources used by the
                executor have been reclaimed.
        """
        pita

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=Kweli)
        rudisha Uongo


kundi BrokenExecutor(RuntimeError):
    """
    Raised when a executor has become non-functional after a severe failure.
    """
