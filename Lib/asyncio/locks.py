"""Synchronization primitives."""

__all__ = ('Lock', 'Event', 'Condition', 'Semaphore', 'BoundedSemaphore')

agiza collections
agiza types
agiza warnings

kutoka . agiza events
kutoka . agiza futures
kutoka . agiza exceptions
kutoka .agiza coroutines


kundi _ContextManager:
    """Context manager.

    This enables the following idiom for acquiring and releasing a
    lock around a block:

        with (yield kutoka lock):
            <block>

    while failing loudly when accidentally using:

        with lock:
            <block>

    Deprecated, use 'async with' statement:
        async with lock:
            <block>
    """

    eleza __init__(self, lock):
        self._lock = lock

    eleza __enter__(self):
        # We have no use for the "as ..."  clause in the with
        # statement for locks.
        rudisha None

    eleza __exit__(self, *args):
        try:
            self._lock.release()
        finally:
            self._lock = None  # Crudely prevent reuse.


kundi _ContextManagerMixin:
    eleza __enter__(self):
        raise RuntimeError(
            '"yield kutoka" should be used as context manager expression')

    eleza __exit__(self, *args):
        # This must exist because __enter__ exists, even though that
        # always raises; that's how the with-statement works.
        pass

    @types.coroutine
    eleza __iter__(self):
        # This is not a coroutine.  It is meant to enable the idiom:
        #
        #     with (yield kutoka lock):
        #         <block>
        #
        # as an alternative to:
        #
        #     yield kutoka lock.acquire()
        #     try:
        #         <block>
        #     finally:
        #         lock.release()
        # Deprecated, use 'async with' statement:
        #     async with lock:
        #         <block>
        warnings.warn("'with (yield kutoka lock)' is deprecated "
                      "use 'async with lock' instead",
                      DeprecationWarning, stacklevel=2)
        yield kutoka self.acquire()
        rudisha _ContextManager(self)

    # The flag is needed for legacy asyncio.iscoroutine()
    __iter__._is_coroutine = coroutines._is_coroutine

    async eleza __acquire_ctx(self):
        await self.acquire()
        rudisha _ContextManager(self)

    eleza __await__(self):
        warnings.warn("'with await lock' is deprecated "
                      "use 'async with lock' instead",
                      DeprecationWarning, stacklevel=2)
        # To make "with await lock" work.
        rudisha self.__acquire_ctx().__await__()

    async eleza __aenter__(self):
        await self.acquire()
        # We have no use for the "as ..."  clause in the with
        # statement for locks.
        rudisha None

    async eleza __aexit__(self, exc_type, exc, tb):
        self.release()


kundi Lock(_ContextManagerMixin):
    """Primitive lock objects.

    A primitive lock is a synchronization primitive that is not owned
    by a particular coroutine when locked.  A primitive lock is in one
    of two states, 'locked' or 'unlocked'.

    It is created in the unlocked state.  It has two basic methods,
    acquire() and release().  When the state is unlocked, acquire()
    changes the state to locked and returns immediately.  When the
    state is locked, acquire() blocks until a call to release() in
    another coroutine changes it to unlocked, then the acquire() call
    resets it to locked and returns.  The release() method should only
    be called in the locked state; it changes the state to unlocked
    and returns immediately.  If an attempt is made to release an
    unlocked lock, a RuntimeError will be raised.

    When more than one coroutine is blocked in acquire() waiting for
    the state to turn to unlocked, only one coroutine proceeds when a
    release() call resets the state to unlocked; first coroutine which
    is blocked in acquire() is being processed.

    acquire() is a coroutine and should be called with 'await'.

    Locks also support the asynchronous context management protocol.
    'async with lock' statement should be used.

    Usage:

        lock = Lock()
        ...
        await lock.acquire()
        try:
            ...
        finally:
            lock.release()

    Context manager usage:

        lock = Lock()
        ...
        async with lock:
             ...

    Lock objects can be tested for locking state:

        ikiwa not lock.locked():
           await lock.acquire()
        else:
           # lock is acquired
           ...

    """

    eleza __init__(self, *, loop=None):
        self._waiters = None
        self._locked = False
        ikiwa loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)

    eleza __repr__(self):
        res = super().__repr__()
        extra = 'locked' ikiwa self._locked else 'unlocked'
        ikiwa self._waiters:
            extra = f'{extra}, waiters:{len(self._waiters)}'
        rudisha f'<{res[1:-1]} [{extra}]>'

    eleza locked(self):
        """Return True ikiwa lock is acquired."""
        rudisha self._locked

    async eleza acquire(self):
        """Acquire a lock.

        This method blocks until the lock is unlocked, then sets it to
        locked and returns True.
        """
        ikiwa (not self._locked and (self._waiters is None or
                all(w.cancelled() for w in self._waiters))):
            self._locked = True
            rudisha True

        ikiwa self._waiters is None:
            self._waiters = collections.deque()
        fut = self._loop.create_future()
        self._waiters.append(fut)

        # Finally block should be called before the CancelledError
        # handling as we don't want CancelledError to call
        # _wake_up_first() and attempt to wake up itself.
        try:
            try:
                await fut
            finally:
                self._waiters.remove(fut)
        except exceptions.CancelledError:
            ikiwa not self._locked:
                self._wake_up_first()
            raise

        self._locked = True
        rudisha True

    eleza release(self):
        """Release a lock.

        When the lock is locked, reset it to unlocked, and return.
        If any other coroutines are blocked waiting for the lock to become
        unlocked, allow exactly one of them to proceed.

        When invoked on an unlocked lock, a RuntimeError is raised.

        There is no rudisha value.
        """
        ikiwa self._locked:
            self._locked = False
            self._wake_up_first()
        else:
            raise RuntimeError('Lock is not acquired.')

    eleza _wake_up_first(self):
        """Wake up the first waiter ikiwa it isn't done."""
        ikiwa not self._waiters:
            return
        try:
            fut = next(iter(self._waiters))
        except StopIteration:
            return

        # .done() necessarily means that a waiter will wake up later on and
        # either take the lock, or, ikiwa it was cancelled and lock wasn't
        # taken already, will hit this again and wake up a new waiter.
        ikiwa not fut.done():
            fut.set_result(True)


kundi Event:
    """Asynchronous equivalent to threading.Event.

    Class implementing event objects. An event manages a flag that can be set
    to true with the set() method and reset to false with the clear() method.
    The wait() method blocks until the flag is true. The flag is initially
    false.
    """

    eleza __init__(self, *, loop=None):
        self._waiters = collections.deque()
        self._value = False
        ikiwa loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)

    eleza __repr__(self):
        res = super().__repr__()
        extra = 'set' ikiwa self._value else 'unset'
        ikiwa self._waiters:
            extra = f'{extra}, waiters:{len(self._waiters)}'
        rudisha f'<{res[1:-1]} [{extra}]>'

    eleza is_set(self):
        """Return True ikiwa and only ikiwa the internal flag is true."""
        rudisha self._value

    eleza set(self):
        """Set the internal flag to true. All coroutines waiting for it to
        become true are awakened. Coroutine that call wait() once the flag is
        true will not block at all.
        """
        ikiwa not self._value:
            self._value = True

            for fut in self._waiters:
                ikiwa not fut.done():
                    fut.set_result(True)

    eleza clear(self):
        """Reset the internal flag to false. Subsequently, coroutines calling
        wait() will block until set() is called to set the internal flag
        to true again."""
        self._value = False

    async eleza wait(self):
        """Block until the internal flag is true.

        If the internal flag is true on entry, rudisha True
        immediately.  Otherwise, block until another coroutine calls
        set() to set the flag to true, then rudisha True.
        """
        ikiwa self._value:
            rudisha True

        fut = self._loop.create_future()
        self._waiters.append(fut)
        try:
            await fut
            rudisha True
        finally:
            self._waiters.remove(fut)


kundi Condition(_ContextManagerMixin):
    """Asynchronous equivalent to threading.Condition.

    This kundi implements condition variable objects. A condition variable
    allows one or more coroutines to wait until they are notified by another
    coroutine.

    A new Lock object is created and used as the underlying lock.
    """

    eleza __init__(self, lock=None, *, loop=None):
        ikiwa loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)

        ikiwa lock is None:
            lock = Lock(loop=loop)
        elikiwa lock._loop is not self._loop:
            raise ValueError("loop argument must agree with lock")

        self._lock = lock
        # Export the lock's locked(), acquire() and release() methods.
        self.locked = lock.locked
        self.acquire = lock.acquire
        self.release = lock.release

        self._waiters = collections.deque()

    eleza __repr__(self):
        res = super().__repr__()
        extra = 'locked' ikiwa self.locked() else 'unlocked'
        ikiwa self._waiters:
            extra = f'{extra}, waiters:{len(self._waiters)}'
        rudisha f'<{res[1:-1]} [{extra}]>'

    async eleza wait(self):
        """Wait until notified.

        If the calling coroutine has not acquired the lock when this
        method is called, a RuntimeError is raised.

        This method releases the underlying lock, and then blocks
        until it is awakened by a notify() or notify_all() call for
        the same condition variable in another coroutine.  Once
        awakened, it re-acquires the lock and returns True.
        """
        ikiwa not self.locked():
            raise RuntimeError('cannot wait on un-acquired lock')

        self.release()
        try:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            try:
                await fut
                rudisha True
            finally:
                self._waiters.remove(fut)

        finally:
            # Must reacquire lock even ikiwa wait is cancelled
            cancelled = False
            while True:
                try:
                    await self.acquire()
                    break
                except exceptions.CancelledError:
                    cancelled = True

            ikiwa cancelled:
                raise exceptions.CancelledError

    async eleza wait_for(self, predicate):
        """Wait until a predicate becomes true.

        The predicate should be a callable which result will be
        interpreted as a boolean value.  The final predicate value is
        the rudisha value.
        """
        result = predicate()
        while not result:
            await self.wait()
            result = predicate()
        rudisha result

    eleza notify(self, n=1):
        """By default, wake up one coroutine waiting on this condition, ikiwa any.
        If the calling coroutine has not acquired the lock when this method
        is called, a RuntimeError is raised.

        This method wakes up at most n of the coroutines waiting for the
        condition variable; it is a no-op ikiwa no coroutines are waiting.

        Note: an awakened coroutine does not actually rudisha kutoka its
        wait() call until it can reacquire the lock. Since notify() does
        not release the lock, its caller should.
        """
        ikiwa not self.locked():
            raise RuntimeError('cannot notify on un-acquired lock')

        idx = 0
        for fut in self._waiters:
            ikiwa idx >= n:
                break

            ikiwa not fut.done():
                idx += 1
                fut.set_result(False)

    eleza notify_all(self):
        """Wake up all threads waiting on this condition. This method acts
        like notify(), but wakes up all waiting threads instead of one. If the
        calling thread has not acquired the lock when this method is called,
        a RuntimeError is raised.
        """
        self.notify(len(self._waiters))


kundi Semaphore(_ContextManagerMixin):
    """A Semaphore implementation.

    A semaphore manages an internal counter which is decremented by each
    acquire() call and incremented by each release() call. The counter
    can never go below zero; when acquire() finds that it is zero, it blocks,
    waiting until some other thread calls release().

    Semaphores also support the context management protocol.

    The optional argument gives the initial value for the internal
    counter; it defaults to 1. If the value given is less than 0,
    ValueError is raised.
    """

    eleza __init__(self, value=1, *, loop=None):
        ikiwa value < 0:
            raise ValueError("Semaphore initial value must be >= 0")
        self._value = value
        self._waiters = collections.deque()
        ikiwa loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)

    eleza __repr__(self):
        res = super().__repr__()
        extra = 'locked' ikiwa self.locked() else f'unlocked, value:{self._value}'
        ikiwa self._waiters:
            extra = f'{extra}, waiters:{len(self._waiters)}'
        rudisha f'<{res[1:-1]} [{extra}]>'

    eleza _wake_up_next(self):
        while self._waiters:
            waiter = self._waiters.popleft()
            ikiwa not waiter.done():
                waiter.set_result(None)
                return

    eleza locked(self):
        """Returns True ikiwa semaphore can not be acquired immediately."""
        rudisha self._value == 0

    async eleza acquire(self):
        """Acquire a semaphore.

        If the internal counter is larger than zero on entry,
        decrement it by one and rudisha True immediately.  If it is
        zero on entry, block, waiting until some other coroutine has
        called release() to make it larger than 0, and then return
        True.
        """
        while self._value <= 0:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            try:
                await fut
            except:
                # See the similar code in Queue.get.
                fut.cancel()
                ikiwa self._value > 0 and not fut.cancelled():
                    self._wake_up_next()
                raise
        self._value -= 1
        rudisha True

    eleza release(self):
        """Release a semaphore, incrementing the internal counter by one.
        When it was zero on entry and another coroutine is waiting for it to
        become larger than zero again, wake up that coroutine.
        """
        self._value += 1
        self._wake_up_next()


kundi BoundedSemaphore(Semaphore):
    """A bounded semaphore implementation.

    This raises ValueError in release() ikiwa it would increase the value
    above the initial value.
    """

    eleza __init__(self, value=1, *, loop=None):
        ikiwa loop:
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)

        self._bound_value = value
        super().__init__(value, loop=loop)

    eleza release(self):
        ikiwa self._value >= self._bound_value:
            raise ValueError('BoundedSemaphore released too many times')
        super().release()
