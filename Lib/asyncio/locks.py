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

    This enables the following idiom kila acquiring na releasing a
    lock around a block:

        ukijumuisha (tuma kutoka lock):
            <block>

    wakati failing loudly when accidentally using:

        ukijumuisha lock:
            <block>

    Deprecated, use 'async with' statement:
        async ukijumuisha lock:
            <block>
    """

    eleza __init__(self, lock):
        self._lock = lock

    eleza __enter__(self):
        # We have no use kila the "as ..."  clause kwenye the with
        # statement kila locks.
        rudisha Tupu

    eleza __exit__(self, *args):
        jaribu:
            self._lock.release()
        mwishowe:
            self._lock = Tupu  # Crudely prevent reuse.


kundi _ContextManagerMixin:
    eleza __enter__(self):
        ashiria RuntimeError(
            '"tuma kutoka" should be used kama context manager expression')

    eleza __exit__(self, *args):
        # This must exist because __enter__ exists, even though that
        # always ashirias; that's how the with-statement works.
        pita

    @types.coroutine
    eleza __iter__(self):
        # This ni sio a coroutine.  It ni meant to enable the idiom:
        #
        #     ukijumuisha (tuma kutoka lock):
        #         <block>
        #
        # kama an alternative to:
        #
        #     tuma kutoka lock.acquire()
        #     jaribu:
        #         <block>
        #     mwishowe:
        #         lock.release()
        # Deprecated, use 'async with' statement:
        #     async ukijumuisha lock:
        #         <block>
        warnings.warn("'ukijumuisha (tuma kutoka lock)' ni deprecated "
                      "use 'async ukijumuisha lock' instead",
                      DeprecationWarning, stacklevel=2)
        tuma kutoka self.acquire()
        rudisha _ContextManager(self)

    # The flag ni needed kila legacy asyncio.iscoroutine()
    __iter__._is_coroutine = coroutines._is_coroutine

    async eleza __acquire_ctx(self):
        await self.acquire()
        rudisha _ContextManager(self)

    eleza __await__(self):
        warnings.warn("'ukijumuisha await lock' ni deprecated "
                      "use 'async ukijumuisha lock' instead",
                      DeprecationWarning, stacklevel=2)
        # To make "ukijumuisha await lock" work.
        rudisha self.__acquire_ctx().__await__()

    async eleza __aenter__(self):
        await self.acquire()
        # We have no use kila the "as ..."  clause kwenye the with
        # statement kila locks.
        rudisha Tupu

    async eleza __aexit__(self, exc_type, exc, tb):
        self.release()


kundi Lock(_ContextManagerMixin):
    """Primitive lock objects.

    A primitive lock ni a synchronization primitive that ni sio owned
    by a particular coroutine when locked.  A primitive lock ni kwenye one
    of two states, 'locked' ama 'unlocked'.

    It ni created kwenye the unlocked state.  It has two basic methods,
    acquire() na release().  When the state ni unlocked, acquire()
    changes the state to locked na rudishas immediately.  When the
    state ni locked, acquire() blocks until a call to release() in
    another coroutine changes it to unlocked, then the acquire() call
    resets it to locked na rudishas.  The release() method should only
    be called kwenye the locked state; it changes the state to unlocked
    na rudishas immediately.  If an attempt ni made to release an
    unlocked lock, a RuntimeError will be ashiriad.

    When more than one coroutine ni blocked kwenye acquire() waiting for
    the state to turn to unlocked, only one coroutine proceeds when a
    release() call resets the state to unlocked; first coroutine which
    ni blocked kwenye acquire() ni being processed.

    acquire() ni a coroutine na should be called ukijumuisha 'await'.

    Locks also support the asynchronous context management protocol.
    'async ukijumuisha lock' statement should be used.

    Usage:

        lock = Lock()
        ...
        await lock.acquire()
        jaribu:
            ...
        mwishowe:
            lock.release()

    Context manager usage:

        lock = Lock()
        ...
        async ukijumuisha lock:
             ...

    Lock objects can be tested kila locking state:

        ikiwa sio lock.locked():
           await lock.acquire()
        isipokua:
           # lock ni acquired
           ...

    """

    eleza __init__(self, *, loop=Tupu):
        self._waiters = Tupu
        self._locked = Uongo
        ikiwa loop ni Tupu:
            self._loop = events.get_event_loop()
        isipokua:
            self._loop = loop
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
                          DeprecationWarning, stacklevel=2)

    eleza __repr__(self):
        res = super().__repr__()
        extra = 'locked' ikiwa self._locked isipokua 'unlocked'
        ikiwa self._waiters:
            extra = f'{extra}, waiters:{len(self._waiters)}'
        rudisha f'<{res[1:-1]} [{extra}]>'

    eleza locked(self):
        """Return Kweli ikiwa lock ni acquired."""
        rudisha self._locked

    async eleza acquire(self):
        """Acquire a lock.

        This method blocks until the lock ni unlocked, then sets it to
        locked na rudishas Kweli.
        """
        ikiwa (sio self._locked na (self._waiters ni Tupu ama
                all(w.cancelled() kila w kwenye self._waiters))):
            self._locked = Kweli
            rudisha Kweli

        ikiwa self._waiters ni Tupu:
            self._waiters = collections.deque()
        fut = self._loop.create_future()
        self._waiters.append(fut)

        # Finally block should be called before the CancelledError
        # handling kama we don't want CancelledError to call
        # _wake_up_first() na attempt to wake up itself.
        jaribu:
            jaribu:
                await fut
            mwishowe:
                self._waiters.remove(fut)
        tatizo exceptions.CancelledError:
            ikiwa sio self._locked:
                self._wake_up_first()
            ashiria

        self._locked = Kweli
        rudisha Kweli

    eleza release(self):
        """Release a lock.

        When the lock ni locked, reset it to unlocked, na rudisha.
        If any other coroutines are blocked waiting kila the lock to become
        unlocked, allow exactly one of them to proceed.

        When invoked on an unlocked lock, a RuntimeError ni ashiriad.

        There ni no rudisha value.
        """
        ikiwa self._locked:
            self._locked = Uongo
            self._wake_up_first()
        isipokua:
            ashiria RuntimeError('Lock ni sio acquired.')

    eleza _wake_up_first(self):
        """Wake up the first waiter ikiwa it isn't done."""
        ikiwa sio self._waiters:
            rudisha
        jaribu:
            fut = next(iter(self._waiters))
        tatizo StopIteration:
            rudisha

        # .done() necessarily means that a waiter will wake up later on na
        # either take the lock, or, ikiwa it was cancelled na lock wasn't
        # taken already, will hit this again na wake up a new waiter.
        ikiwa sio fut.done():
            fut.set_result(Kweli)


kundi Event:
    """Asynchronous equivalent to threading.Event.

    Class implementing event objects. An event manages a flag that can be set
    to true ukijumuisha the set() method na reset to false ukijumuisha the clear() method.
    The wait() method blocks until the flag ni true. The flag ni initially
    false.
    """

    eleza __init__(self, *, loop=Tupu):
        self._waiters = collections.deque()
        self._value = Uongo
        ikiwa loop ni Tupu:
            self._loop = events.get_event_loop()
        isipokua:
            self._loop = loop
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
                          DeprecationWarning, stacklevel=2)

    eleza __repr__(self):
        res = super().__repr__()
        extra = 'set' ikiwa self._value isipokua 'unset'
        ikiwa self._waiters:
            extra = f'{extra}, waiters:{len(self._waiters)}'
        rudisha f'<{res[1:-1]} [{extra}]>'

    eleza is_set(self):
        """Return Kweli ikiwa na only ikiwa the internal flag ni true."""
        rudisha self._value

    eleza set(self):
        """Set the internal flag to true. All coroutines waiting kila it to
        become true are awakened. Coroutine that call wait() once the flag is
        true will sio block at all.
        """
        ikiwa sio self._value:
            self._value = Kweli

            kila fut kwenye self._waiters:
                ikiwa sio fut.done():
                    fut.set_result(Kweli)

    eleza clear(self):
        """Reset the internal flag to false. Subsequently, coroutines calling
        wait() will block until set() ni called to set the internal flag
        to true again."""
        self._value = Uongo

    async eleza wait(self):
        """Block until the internal flag ni true.

        If the internal flag ni true on entry, rudisha Kweli
        immediately.  Otherwise, block until another coroutine calls
        set() to set the flag to true, then rudisha Kweli.
        """
        ikiwa self._value:
            rudisha Kweli

        fut = self._loop.create_future()
        self._waiters.append(fut)
        jaribu:
            await fut
            rudisha Kweli
        mwishowe:
            self._waiters.remove(fut)


kundi Condition(_ContextManagerMixin):
    """Asynchronous equivalent to threading.Condition.

    This kundi implements condition variable objects. A condition variable
    allows one ama more coroutines to wait until they are notified by another
    coroutine.

    A new Lock object ni created na used kama the underlying lock.
    """

    eleza __init__(self, lock=Tupu, *, loop=Tupu):
        ikiwa loop ni Tupu:
            self._loop = events.get_event_loop()
        isipokua:
            self._loop = loop
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
                          DeprecationWarning, stacklevel=2)

        ikiwa lock ni Tupu:
            lock = Lock(loop=loop)
        lasivyo lock._loop ni sio self._loop:
            ashiria ValueError("loop argument must agree ukijumuisha lock")

        self._lock = lock
        # Export the lock's locked(), acquire() na release() methods.
        self.locked = lock.locked
        self.acquire = lock.acquire
        self.release = lock.release

        self._waiters = collections.deque()

    eleza __repr__(self):
        res = super().__repr__()
        extra = 'locked' ikiwa self.locked() isipokua 'unlocked'
        ikiwa self._waiters:
            extra = f'{extra}, waiters:{len(self._waiters)}'
        rudisha f'<{res[1:-1]} [{extra}]>'

    async eleza wait(self):
        """Wait until notified.

        If the calling coroutine has sio acquired the lock when this
        method ni called, a RuntimeError ni ashiriad.

        This method releases the underlying lock, na then blocks
        until it ni awakened by a notify() ama notify_all() call for
        the same condition variable kwenye another coroutine.  Once
        awakened, it re-acquires the lock na rudishas Kweli.
        """
        ikiwa sio self.locked():
            ashiria RuntimeError('cannot wait on un-acquired lock')

        self.release()
        jaribu:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            jaribu:
                await fut
                rudisha Kweli
            mwishowe:
                self._waiters.remove(fut)

        mwishowe:
            # Must reacquire lock even ikiwa wait ni cancelled
            cancelled = Uongo
            wakati Kweli:
                jaribu:
                    await self.acquire()
                    koma
                tatizo exceptions.CancelledError:
                    cancelled = Kweli

            ikiwa cancelled:
                ashiria exceptions.CancelledError

    async eleza wait_for(self, predicate):
        """Wait until a predicate becomes true.

        The predicate should be a callable which result will be
        interpreted kama a boolean value.  The final predicate value is
        the rudisha value.
        """
        result = predicate()
        wakati sio result:
            await self.wait()
            result = predicate()
        rudisha result

    eleza notify(self, n=1):
        """By default, wake up one coroutine waiting on this condition, ikiwa any.
        If the calling coroutine has sio acquired the lock when this method
        ni called, a RuntimeError ni ashiriad.

        This method wakes up at most n of the coroutines waiting kila the
        condition variable; it ni a no-op ikiwa no coroutines are waiting.

        Note: an awakened coroutine does sio actually rudisha kutoka its
        wait() call until it can reacquire the lock. Since notify() does
        sio release the lock, its caller should.
        """
        ikiwa sio self.locked():
            ashiria RuntimeError('cannot notify on un-acquired lock')

        idx = 0
        kila fut kwenye self._waiters:
            ikiwa idx >= n:
                koma

            ikiwa sio fut.done():
                idx += 1
                fut.set_result(Uongo)

    eleza notify_all(self):
        """Wake up all threads waiting on this condition. This method acts
        like notify(), but wakes up all waiting threads instead of one. If the
        calling thread has sio acquired the lock when this method ni called,
        a RuntimeError ni ashiriad.
        """
        self.notify(len(self._waiters))


kundi Semaphore(_ContextManagerMixin):
    """A Semaphore implementation.

    A semaphore manages an internal counter which ni decremented by each
    acquire() call na incremented by each release() call. The counter
    can never go below zero; when acquire() finds that it ni zero, it blocks,
    waiting until some other thread calls release().

    Semaphores also support the context management protocol.

    The optional argument gives the initial value kila the internal
    counter; it defaults to 1. If the value given ni less than 0,
    ValueError ni ashiriad.
    """

    eleza __init__(self, value=1, *, loop=Tupu):
        ikiwa value < 0:
            ashiria ValueError("Semaphore initial value must be >= 0")
        self._value = value
        self._waiters = collections.deque()
        ikiwa loop ni Tupu:
            self._loop = events.get_event_loop()
        isipokua:
            self._loop = loop
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
                          DeprecationWarning, stacklevel=2)

    eleza __repr__(self):
        res = super().__repr__()
        extra = 'locked' ikiwa self.locked() isipokua f'unlocked, value:{self._value}'
        ikiwa self._waiters:
            extra = f'{extra}, waiters:{len(self._waiters)}'
        rudisha f'<{res[1:-1]} [{extra}]>'

    eleza _wake_up_next(self):
        wakati self._waiters:
            waiter = self._waiters.popleft()
            ikiwa sio waiter.done():
                waiter.set_result(Tupu)
                rudisha

    eleza locked(self):
        """Returns Kweli ikiwa semaphore can sio be acquired immediately."""
        rudisha self._value == 0

    async eleza acquire(self):
        """Acquire a semaphore.

        If the internal counter ni larger than zero on entry,
        decrement it by one na rudisha Kweli immediately.  If it is
        zero on entry, block, waiting until some other coroutine has
        called release() to make it larger than 0, na then rudisha
        Kweli.
        """
        wakati self._value <= 0:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            jaribu:
                await fut
            tatizo:
                # See the similar code kwenye Queue.get.
                fut.cancel()
                ikiwa self._value > 0 na sio fut.cancelled():
                    self._wake_up_next()
                ashiria
        self._value -= 1
        rudisha Kweli

    eleza release(self):
        """Release a semaphore, incrementing the internal counter by one.
        When it was zero on entry na another coroutine ni waiting kila it to
        become larger than zero again, wake up that coroutine.
        """
        self._value += 1
        self._wake_up_next()


kundi BoundedSemaphore(Semaphore):
    """A bounded semaphore implementation.

    This ashirias ValueError kwenye release() ikiwa it would increase the value
    above the initial value.
    """

    eleza __init__(self, value=1, *, loop=Tupu):
        ikiwa loop:
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
                          DeprecationWarning, stacklevel=2)

        self._bound_value = value
        super().__init__(value, loop=loop)

    eleza release(self):
        ikiwa self._value >= self._bound_value:
            ashiria ValueError('BoundedSemaphore released too many times')
        super().release()
