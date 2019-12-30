"""Thread module emulating a subset of Java's threading model."""

agiza os kama _os
agiza sys kama _sys
agiza _thread

kutoka time agiza monotonic kama _time
kutoka _weakrefset agiza WeakSet
kutoka itertools agiza islice kama _islice, count kama _count
jaribu:
    kutoka _collections agiza deque kama _deque
tatizo ImportError:
    kutoka collections agiza deque kama _deque

# Note regarding PEP 8 compliant names
#  This threading motoa was originally inspired by Java, na inherited
# the convention of camelCase function na method names kutoka that
# language. Those original names are haiko kwenye any imminent danger of
# being deprecated (even kila Py3k),so this module provides them kama an
# alias kila the PEP 8 compliant names
# Note that using the new PEP 8 compliant names facilitates substitution
# ukijumuisha the multiprocessing module, which doesn't provide the old
# Java inspired names.

__all__ = ['get_ident', 'active_count', 'Condition', 'current_thread',
           'enumerate', 'main_thread', 'TIMEOUT_MAX',
           'Event', 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Thread',
           'Barrier', 'BrokenBarrierError', 'Timer', 'ThreadError',
           'setprofile', 'settrace', 'local', 'stack_size',
           'excepthook', 'ExceptHookArgs']

# Rename some stuff so "kutoka threading agiza *" ni safe
_start_new_thread = _thread.start_new_thread
_allocate_lock = _thread.allocate_lock
_set_sentinel = _thread._set_sentinel
get_ident = _thread.get_ident
jaribu:
    get_native_id = _thread.get_native_id
    _HAVE_THREAD_NATIVE_ID = Kweli
    __all__.append('get_native_id')
tatizo AttributeError:
    _HAVE_THREAD_NATIVE_ID = Uongo
ThreadError = _thread.error
jaribu:
    _CRLock = _thread.RLock
tatizo AttributeError:
    _CRLock = Tupu
TIMEOUT_MAX = _thread.TIMEOUT_MAX
toa _thread


# Support kila profile na trace hooks

_profile_hook = Tupu
_trace_hook = Tupu

eleza setprofile(func):
    """Set a profile function kila all threads started kutoka the threading module.

    The func will be pitaed to sys.setprofile() kila each thread, before its
    run() method ni called.

    """
    global _profile_hook
    _profile_hook = func

eleza settrace(func):
    """Set a trace function kila all threads started kutoka the threading module.

    The func will be pitaed to sys.settrace() kila each thread, before its run()
    method ni called.

    """
    global _trace_hook
    _trace_hook = func

# Synchronization classes

Lock = _allocate_lock

eleza RLock(*args, **kwargs):
    """Factory function that returns a new reentrant lock.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock, the same thread may acquire it again
    without blocking; the thread must release it once kila each time it has
    acquired it.

    """
    ikiwa _CRLock ni Tupu:
        rudisha _PyRLock(*args, **kwargs)
    rudisha _CRLock(*args, **kwargs)

kundi _RLock:
    """This kundi implements reentrant lock objects.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock, the same thread may acquire it
    again without blocking; the thread must release it once kila each time it
    has acquired it.

    """

    eleza __init__(self):
        self._block = _allocate_lock()
        self._owner = Tupu
        self._count = 0

    eleza __repr__(self):
        owner = self._owner
        jaribu:
            owner = _active[owner].name
        tatizo KeyError:
            pita
        rudisha "<%s %s.%s object owner=%r count=%d at %s>" % (
            "locked" ikiwa self._block.locked() isipokua "unlocked",
            self.__class__.__module__,
            self.__class__.__qualname__,
            owner,
            self._count,
            hex(id(self))
        )

    eleza acquire(self, blocking=Kweli, timeout=-1):
        """Acquire a lock, blocking ama non-blocking.

        When invoked without arguments: ikiwa this thread already owns the lock,
        increment the recursion level by one, na rudisha immediately. Otherwise,
        ikiwa another thread owns the lock, block until the lock ni unlocked. Once
        the lock ni unlocked (sio owned by any thread), then grab ownership, set
        the recursion level to one, na return. If more than one thread is
        blocked waiting until the lock ni unlocked, only one at a time will be
        able to grab ownership of the lock. There ni no rudisha value kwenye this
        case.

        When invoked ukijumuisha the blocking argument set to true, do the same thing
        kama when called without arguments, na rudisha true.

        When invoked ukijumuisha the blocking argument set to false, do sio block. If a
        call without an argument would block, rudisha false immediately;
        otherwise, do the same thing kama when called without arguments, na
        rudisha true.

        When invoked ukijumuisha the floating-point timeout argument set to a positive
        value, block kila at most the number of seconds specified by timeout
        na kama long kama the lock cannot be acquired.  Return true ikiwa the lock has
        been acquired, false ikiwa the timeout has elapsed.

        """
        me = get_ident()
        ikiwa self._owner == me:
            self._count += 1
            rudisha 1
        rc = self._block.acquire(blocking, timeout)
        ikiwa rc:
            self._owner = me
            self._count = 1
        rudisha rc

    __enter__ = acquire

    eleza release(self):
        """Release a lock, decrementing the recursion level.

        If after the decrement it ni zero, reset the lock to unlocked (sio owned
        by any thread), na ikiwa any other threads are blocked waiting kila the
        lock to become unlocked, allow exactly one of them to proceed. If after
        the decrement the recursion level ni still nonzero, the lock remains
        locked na owned by the calling thread.

        Only call this method when the calling thread owns the lock. A
        RuntimeError ni raised ikiwa this method ni called when the lock is
        unlocked.

        There ni no rudisha value.

        """
        ikiwa self._owner != get_ident():
            ashiria RuntimeError("cannot release un-acquired lock")
        self._count = count = self._count - 1
        ikiwa sio count:
            self._owner = Tupu
            self._block.release()

    eleza __exit__(self, t, v, tb):
        self.release()

    # Internal methods used by condition variables

    eleza _acquire_restore(self, state):
        self._block.acquire()
        self._count, self._owner = state

    eleza _release_save(self):
        ikiwa self._count == 0:
            ashiria RuntimeError("cannot release un-acquired lock")
        count = self._count
        self._count = 0
        owner = self._owner
        self._owner = Tupu
        self._block.release()
        rudisha (count, owner)

    eleza _is_owned(self):
        rudisha self._owner == get_ident()

_PyRLock = _RLock


kundi Condition:
    """Class that implements a condition variable.

    A condition variable allows one ama more threads to wait until they are
    notified by another thread.

    If the lock argument ni given na sio Tupu, it must be a Lock ama RLock
    object, na it ni used kama the underlying lock. Otherwise, a new RLock object
    ni created na used kama the underlying lock.

    """

    eleza __init__(self, lock=Tupu):
        ikiwa lock ni Tupu:
            lock = RLock()
        self._lock = lock
        # Export the lock's acquire() na release() methods
        self.acquire = lock.acquire
        self.release = lock.release
        # If the lock defines _release_save() and/or _acquire_restore(),
        # these override the default implementations (which just call
        # release() na acquire() on the lock).  Ditto kila _is_owned().
        jaribu:
            self._release_save = lock._release_save
        tatizo AttributeError:
            pita
        jaribu:
            self._acquire_restore = lock._acquire_restore
        tatizo AttributeError:
            pita
        jaribu:
            self._is_owned = lock._is_owned
        tatizo AttributeError:
            pita
        self._waiters = _deque()

    eleza __enter__(self):
        rudisha self._lock.__enter__()

    eleza __exit__(self, *args):
        rudisha self._lock.__exit__(*args)

    eleza __repr__(self):
        rudisha "<Condition(%s, %d)>" % (self._lock, len(self._waiters))

    eleza _release_save(self):
        self._lock.release()           # No state to save

    eleza _acquire_restore(self, x):
        self._lock.acquire()           # Ignore saved state

    eleza _is_owned(self):
        # Return Kweli ikiwa lock ni owned by current_thread.
        # This method ni called only ikiwa _lock doesn't have _is_owned().
        ikiwa self._lock.acquire(0):
            self._lock.release()
            rudisha Uongo
        isipokua:
            rudisha Kweli

    eleza wait(self, timeout=Tupu):
        """Wait until notified ama until a timeout occurs.

        If the calling thread has sio acquired the lock when this method is
        called, a RuntimeError ni raised.

        This method releases the underlying lock, na then blocks until it is
        awakened by a notify() ama notify_all() call kila the same condition
        variable kwenye another thread, ama until the optional timeout occurs. Once
        awakened ama timed out, it re-acquires the lock na returns.

        When the timeout argument ni present na sio Tupu, it should be a
        floating point number specifying a timeout kila the operation kwenye seconds
        (or fractions thereof).

        When the underlying lock ni an RLock, it ni sio released using its
        release() method, since this may sio actually unlock the lock when it
        was acquired multiple times recursively. Instead, an internal interface
        of the RLock kundi ni used, which really unlocks it even when it has
        been recursively acquired several times. Another internal interface is
        then used to restore the recursion level when the lock ni reacquired.

        """
        ikiwa sio self._is_owned():
            ashiria RuntimeError("cannot wait on un-acquired lock")
        waiter = _allocate_lock()
        waiter.acquire()
        self._waiters.append(waiter)
        saved_state = self._release_save()
        gotit = Uongo
        jaribu:    # restore state no matter what (e.g., KeyboardInterrupt)
            ikiwa timeout ni Tupu:
                waiter.acquire()
                gotit = Kweli
            isipokua:
                ikiwa timeout > 0:
                    gotit = waiter.acquire(Kweli, timeout)
                isipokua:
                    gotit = waiter.acquire(Uongo)
            rudisha gotit
        mwishowe:
            self._acquire_restore(saved_state)
            ikiwa sio gotit:
                jaribu:
                    self._waiters.remove(waiter)
                tatizo ValueError:
                    pita

    eleza wait_for(self, predicate, timeout=Tupu):
        """Wait until a condition evaluates to Kweli.

        predicate should be a callable which result will be interpreted kama a
        boolean value.  A timeout may be provided giving the maximum time to
        wait.

        """
        endtime = Tupu
        waittime = timeout
        result = predicate()
        wakati sio result:
            ikiwa waittime ni sio Tupu:
                ikiwa endtime ni Tupu:
                    endtime = _time() + waittime
                isipokua:
                    waittime = endtime - _time()
                    ikiwa waittime <= 0:
                        koma
            self.wait(waittime)
            result = predicate()
        rudisha result

    eleza notify(self, n=1):
        """Wake up one ama more threads waiting on this condition, ikiwa any.

        If the calling thread has sio acquired the lock when this method is
        called, a RuntimeError ni raised.

        This method wakes up at most n of the threads waiting kila the condition
        variable; it ni a no-op ikiwa no threads are waiting.

        """
        ikiwa sio self._is_owned():
            ashiria RuntimeError("cannot notify on un-acquired lock")
        all_waiters = self._waiters
        waiters_to_notify = _deque(_islice(all_waiters, n))
        ikiwa sio waiters_to_notify:
            rudisha
        kila waiter kwenye waiters_to_notify:
            waiter.release()
            jaribu:
                all_waiters.remove(waiter)
            tatizo ValueError:
                pita

    eleza notify_all(self):
        """Wake up all threads waiting on this condition.

        If the calling thread has sio acquired the lock when this method
        ni called, a RuntimeError ni raised.

        """
        self.notify(len(self._waiters))

    notifyAll = notify_all


kundi Semaphore:
    """This kundi implements semaphore objects.

    Semaphores manage a counter representing the number of release() calls minus
    the number of acquire() calls, plus an initial value. The acquire() method
    blocks ikiwa necessary until it can rudisha without making the counter
    negative. If sio given, value defaults to 1.

    """

    # After Tim Peters' semaphore class, but sio quite the same (no maximum)

    eleza __init__(self, value=1):
        ikiwa value < 0:
            ashiria ValueError("semaphore initial value must be >= 0")
        self._cond = Condition(Lock())
        self._value = value

    eleza acquire(self, blocking=Kweli, timeout=Tupu):
        """Acquire a semaphore, decrementing the internal counter by one.

        When invoked without arguments: ikiwa the internal counter ni larger than
        zero on entry, decrement it by one na rudisha immediately. If it ni zero
        on entry, block, waiting until some other thread has called release() to
        make it larger than zero. This ni done ukijumuisha proper interlocking so that
        ikiwa multiple acquire() calls are blocked, release() will wake exactly one
        of them up. The implementation may pick one at random, so the order in
        which blocked threads are awakened should sio be relied on. There ni no
        rudisha value kwenye this case.

        When invoked ukijumuisha blocking set to true, do the same thing kama when called
        without arguments, na rudisha true.

        When invoked ukijumuisha blocking set to false, do sio block. If a call without
        an argument would block, rudisha false immediately; otherwise, do the
        same thing kama when called without arguments, na rudisha true.

        When invoked ukijumuisha a timeout other than Tupu, it will block kila at
        most timeout seconds.  If acquire does sio complete successfully in
        that interval, rudisha false.  Return true otherwise.

        """
        ikiwa sio blocking na timeout ni sio Tupu:
            ashiria ValueError("can't specify timeout kila non-blocking acquire")
        rc = Uongo
        endtime = Tupu
        ukijumuisha self._cond:
            wakati self._value == 0:
                ikiwa sio blocking:
                    koma
                ikiwa timeout ni sio Tupu:
                    ikiwa endtime ni Tupu:
                        endtime = _time() + timeout
                    isipokua:
                        timeout = endtime - _time()
                        ikiwa timeout <= 0:
                            koma
                self._cond.wait(timeout)
            isipokua:
                self._value -= 1
                rc = Kweli
        rudisha rc

    __enter__ = acquire

    eleza release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter ni zero on entry na another thread ni waiting kila it
        to become larger than zero again, wake up that thread.

        """
        ukijumuisha self._cond:
            self._value += 1
            self._cond.notify()

    eleza __exit__(self, t, v, tb):
        self.release()


kundi BoundedSemaphore(Semaphore):
    """Implements a bounded semaphore.

    A bounded semaphore checks to make sure its current value doesn't exceed its
    initial value. If it does, ValueError ni raised. In most situations
    semaphores are used to guard resources ukijumuisha limited capacity.

    If the semaphore ni released too many times it's a sign of a bug. If not
    given, value defaults to 1.

    Like regular semaphores, bounded semaphores manage a counter representing
    the number of release() calls minus the number of acquire() calls, plus an
    initial value. The acquire() method blocks ikiwa necessary until it can rudisha
    without making the counter negative. If sio given, value defaults to 1.

    """

    eleza __init__(self, value=1):
        Semaphore.__init__(self, value)
        self._initial_value = value

    eleza release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter ni zero on entry na another thread ni waiting kila it
        to become larger than zero again, wake up that thread.

        If the number of releases exceeds the number of acquires,
        ashiria a ValueError.

        """
        ukijumuisha self._cond:
            ikiwa self._value >= self._initial_value:
                ashiria ValueError("Semaphore released too many times")
            self._value += 1
            self._cond.notify()


kundi Event:
    """Class implementing event objects.

    Events manage a flag that can be set to true ukijumuisha the set() method na reset
    to false ukijumuisha the clear() method. The wait() method blocks until the flag is
    true.  The flag ni initially false.

    """

    # After Tim Peters' event kundi (without is_posted())

    eleza __init__(self):
        self._cond = Condition(Lock())
        self._flag = Uongo

    eleza _reset_internal_locks(self):
        # private!  called by Thread._reset_internal_locks by _after_fork()
        self._cond.__init__(Lock())

    eleza is_set(self):
        """Return true ikiwa na only ikiwa the internal flag ni true."""
        rudisha self._flag

    isSet = is_set

    eleza set(self):
        """Set the internal flag to true.

        All threads waiting kila it to become true are awakened. Threads
        that call wait() once the flag ni true will sio block at all.

        """
        ukijumuisha self._cond:
            self._flag = Kweli
            self._cond.notify_all()

    eleza clear(self):
        """Reset the internal flag to false.

        Subsequently, threads calling wait() will block until set() ni called to
        set the internal flag to true again.

        """
        ukijumuisha self._cond:
            self._flag = Uongo

    eleza wait(self, timeout=Tupu):
        """Block until the internal flag ni true.

        If the internal flag ni true on entry, rudisha immediately. Otherwise,
        block until another thread calls set() to set the flag to true, ama until
        the optional timeout occurs.

        When the timeout argument ni present na sio Tupu, it should be a
        floating point number specifying a timeout kila the operation kwenye seconds
        (or fractions thereof).

        This method returns the internal flag on exit, so it will always rudisha
        Kweli tatizo ikiwa a timeout ni given na the operation times out.

        """
        ukijumuisha self._cond:
            signaled = self._flag
            ikiwa sio signaled:
                signaled = self._cond.wait(timeout)
            rudisha signaled


# A barrier class.  Inspired kwenye part by the pthread_barrier_* api na
# the CyclicBarrier kundi kutoka Java.  See
# http://sourceware.org/pthreads-win32/manual/pthread_barrier_init.html na
# http://java.sun.com/j2se/1.5.0/docs/api/java/util/concurrent/
#        CyclicBarrier.html
# kila information.
# We maintain two main states, 'filling' na 'draining' enabling the barrier
# to be cyclic.  Threads are sio allowed into it until it has fully drained
# since the previous cycle.  In addition, a 'resetting' state exists which is
# similar to 'draining' tatizo that threads leave ukijumuisha a BrokenBarrierError,
# na a 'broken' state kwenye which all threads get the exception.
kundi Barrier:
    """Implements a Barrier.

    Useful kila synchronizing a fixed number of threads at known synchronization
    points.  Threads block on 'wait()' na are simultaneously awoken once they
    have all made that call.

    """

    eleza __init__(self, parties, action=Tupu, timeout=Tupu):
        """Create a barrier, initialised to 'parties' threads.

        'action' ni a callable which, when supplied, will be called by one of
        the threads after they have all entered the barrier na just prior to
        releasing them all. If a 'timeout' ni provided, it ni used kama the
        default kila all subsequent 'wait()' calls.

        """
        self._cond = Condition(Lock())
        self._action = action
        self._timeout = timeout
        self._parties = parties
        self._state = 0 #0 filling, 1, draining, -1 resetting, -2 broken
        self._count = 0

    eleza wait(self, timeout=Tupu):
        """Wait kila the barrier.

        When the specified number of threads have started waiting, they are all
        simultaneously awoken. If an 'action' was provided kila the barrier, one
        of the threads will have executed that callback prior to returning.
        Returns an individual index number kutoka 0 to 'parties-1'.

        """
        ikiwa timeout ni Tupu:
            timeout = self._timeout
        ukijumuisha self._cond:
            self._enter() # Block wakati the barrier drains.
            index = self._count
            self._count += 1
            jaribu:
                ikiwa index + 1 == self._parties:
                    # We release the barrier
                    self._release()
                isipokua:
                    # We wait until someone releases us
                    self._wait(timeout)
                rudisha index
            mwishowe:
                self._count -= 1
                # Wake up any threads waiting kila barrier to drain.
                self._exit()

    # Block until the barrier ni ready kila us, ama ashiria an exception
    # ikiwa it ni broken.
    eleza _enter(self):
        wakati self._state kwenye (-1, 1):
            # It ni draining ama resetting, wait until done
            self._cond.wait()
        #see ikiwa the barrier ni kwenye a broken state
        ikiwa self._state < 0:
            ashiria BrokenBarrierError
        assert self._state == 0

    # Optionally run the 'action' na release the threads waiting
    # kwenye the barrier.
    eleza _release(self):
        jaribu:
            ikiwa self._action:
                self._action()
            # enter draining state
            self._state = 1
            self._cond.notify_all()
        tatizo:
            #an exception during the _action handler.  Break na reraise
            self._koma()
            raise

    # Wait kwenye the barrier until we are released.  Raise an exception
    # ikiwa the barrier ni reset ama broken.
    eleza _wait(self, timeout):
        ikiwa sio self._cond.wait_for(lambda : self._state != 0, timeout):
            #timed out.  Break the barrier
            self._koma()
            ashiria BrokenBarrierError
        ikiwa self._state < 0:
            ashiria BrokenBarrierError
        assert self._state == 1

    # If we are the last thread to exit the barrier, signal any threads
    # waiting kila the barrier to drain.
    eleza _exit(self):
        ikiwa self._count == 0:
            ikiwa self._state kwenye (-1, 1):
                #resetting ama draining
                self._state = 0
                self._cond.notify_all()

    eleza reset(self):
        """Reset the barrier to the initial state.

        Any threads currently waiting will get the BrokenBarrier exception
        raised.

        """
        ukijumuisha self._cond:
            ikiwa self._count > 0:
                ikiwa self._state == 0:
                    #reset the barrier, waking up threads
                    self._state = -1
                lasivyo self._state == -2:
                    #was broken, set it to reset state
                    #which clears when the last thread exits
                    self._state = -1
            isipokua:
                self._state = 0
            self._cond.notify_all()

    eleza abort(self):
        """Place the barrier into a 'broken' state.

        Useful kwenye case of error.  Any currently waiting threads na threads
        attempting to 'wait()' will have BrokenBarrierError raised.

        """
        ukijumuisha self._cond:
            self._koma()

    eleza _koma(self):
        # An internal error was detected.  The barrier ni set to
        # a broken state all parties awakened.
        self._state = -2
        self._cond.notify_all()

    @property
    eleza parties(self):
        """Return the number of threads required to trip the barrier."""
        rudisha self._parties

    @property
    eleza n_waiting(self):
        """Return the number of threads currently waiting at the barrier."""
        # We don't need synchronization here since this ni an ephemeral result
        # anyway.  It returns the correct value kwenye the steady state.
        ikiwa self._state == 0:
            rudisha self._count
        rudisha 0

    @property
    eleza broken(self):
        """Return Kweli ikiwa the barrier ni kwenye a broken state."""
        rudisha self._state == -2

# exception raised by the Barrier class
kundi BrokenBarrierError(RuntimeError):
    pita


# Helper to generate new thread names
_counter = _count().__next__
_counter() # Consume 0 so first non-main thread has id 1.
eleza _newname(template="Thread-%d"):
    rudisha template % _counter()

# Active thread administration
_active_limbo_lock = _allocate_lock()
_active = {}    # maps thread id to Thread object
_limbo = {}
_dangling = WeakSet()
# Set of Thread._tstate_lock locks of non-daemon threads used by _shutdown()
# to wait until all Python thread states get deleted:
# see Thread._set_tstate_lock().
_shutdown_locks_lock = _allocate_lock()
_shutdown_locks = set()

# Main kundi kila threads

kundi Thread:
    """A kundi that represents a thread of control.

    This kundi can be safely subclassed kwenye a limited fashion. There are two ways
    to specify the activity: by pitaing a callable object to the constructor, ama
    by overriding the run() method kwenye a subclass.

    """

    _initialized = Uongo

    eleza __init__(self, group=Tupu, target=Tupu, name=Tupu,
                 args=(), kwargs=Tupu, *, daemon=Tupu):
        """This constructor should always be called ukijumuisha keyword arguments. Arguments are:

        *group* should be Tupu; reserved kila future extension when a ThreadGroup
        kundi ni implemented.

        *target* ni the callable object to be invoked by the run()
        method. Defaults to Tupu, meaning nothing ni called.

        *name* ni the thread name. By default, a unique name ni constructed of
        the form "Thread-N" where N ni a small decimal number.

        *args* ni the argument tuple kila the target invocation. Defaults to ().

        *kwargs* ni a dictionary of keyword arguments kila the target
        invocation. Defaults to {}.

        If a subkundi overrides the constructor, it must make sure to invoke
        the base kundi constructor (Thread.__init__()) before doing anything
        isipokua to the thread.

        """
        assert group ni Tupu, "group argument must be Tupu kila now"
        ikiwa kwargs ni Tupu:
            kwargs = {}
        self._target = target
        self._name = str(name ama _newname())
        self._args = args
        self._kwargs = kwargs
        ikiwa daemon ni sio Tupu:
            self._daemonic = daemon
        isipokua:
            self._daemonic = current_thread().daemon
        self._ident = Tupu
        ikiwa _HAVE_THREAD_NATIVE_ID:
            self._native_id = Tupu
        self._tstate_lock = Tupu
        self._started = Event()
        self._is_stopped = Uongo
        self._initialized = Kweli
        # Copy of sys.stderr used by self._invoke_excepthook()
        self._stderr = _sys.stderr
        self._invoke_excepthook = _make_invoke_excepthook()
        # For debugging na _after_fork()
        _dangling.add(self)

    eleza _reset_internal_locks(self, is_alive):
        # private!  Called by _after_fork() to reset our internal locks as
        # they may be kwenye an invalid state leading to a deadlock ama crash.
        self._started._reset_internal_locks()
        ikiwa is_alive:
            self._set_tstate_lock()
        isipokua:
            # The thread isn't alive after fork: it doesn't have a tstate
            # anymore.
            self._is_stopped = Kweli
            self._tstate_lock = Tupu

    eleza __repr__(self):
        assert self._initialized, "Thread.__init__() was sio called"
        status = "initial"
        ikiwa self._started.is_set():
            status = "started"
        self.is_alive() # easy way to get ._is_stopped set when appropriate
        ikiwa self._is_stopped:
            status = "stopped"
        ikiwa self._daemonic:
            status += " daemon"
        ikiwa self._ident ni sio Tupu:
            status += " %s" % self._ident
        rudisha "<%s(%s, %s)>" % (self.__class__.__name__, self._name, status)

    eleza start(self):
        """Start the thread's activity.

        It must be called at most once per thread object. It arranges kila the
        object's run() method to be invoked kwenye a separate thread of control.

        This method will ashiria a RuntimeError ikiwa called more than once on the
        same thread object.

        """
        ikiwa sio self._initialized:
            ashiria RuntimeError("thread.__init__() sio called")

        ikiwa self._started.is_set():
            ashiria RuntimeError("threads can only be started once")
        ukijumuisha _active_limbo_lock:
            _limbo[self] = self
        jaribu:
            _start_new_thread(self._bootstrap, ())
        tatizo Exception:
            ukijumuisha _active_limbo_lock:
                toa _limbo[self]
            raise
        self._started.wait()

    eleza run(self):
        """Method representing the thread's activity.

        You may override this method kwenye a subclass. The standard run() method
        invokes the callable object pitaed to the object's constructor kama the
        target argument, ikiwa any, ukijumuisha sequential na keyword arguments taken
        kutoka the args na kwargs arguments, respectively.

        """
        jaribu:
            ikiwa self._target:
                self._target(*self._args, **self._kwargs)
        mwishowe:
            # Avoid a refcycle ikiwa the thread ni running a function with
            # an argument that has a member that points to the thread.
            toa self._target, self._args, self._kwargs

    eleza _bootstrap(self):
        # Wrapper around the real bootstrap code that ignores
        # exceptions during interpreter cleanup.  Those typically
        # happen when a daemon thread wakes up at an unfortunate
        # moment, finds the world around it destroyed, na raises some
        # random exception *** wakati trying to report the exception in
        # _bootstrap_inner() below ***.  Those random exceptions
        # don't help anybody, na they confuse users, so we suppress
        # them.  We suppress them only when it appears that the world
        # indeed has already been destroyed, so that exceptions in
        # _bootstrap_inner() during normal business hours are properly
        # reported.  Also, we only suppress them kila daemonic threads;
        # ikiwa a non-daemonic encounters this, something isipokua ni wrong.
        jaribu:
            self._bootstrap_inner()
        tatizo:
            ikiwa self._daemonic na _sys ni Tupu:
                rudisha
            raise

    eleza _set_ident(self):
        self._ident = get_ident()

    ikiwa _HAVE_THREAD_NATIVE_ID:
        eleza _set_native_id(self):
            self._native_id = get_native_id()

    eleza _set_tstate_lock(self):
        """
        Set a lock object which will be released by the interpreter when
        the underlying thread state (see pystate.h) gets deleted.
        """
        self._tstate_lock = _set_sentinel()
        self._tstate_lock.acquire()

        ikiwa sio self.daemon:
            ukijumuisha _shutdown_locks_lock:
                _shutdown_locks.add(self._tstate_lock)

    eleza _bootstrap_inner(self):
        jaribu:
            self._set_ident()
            self._set_tstate_lock()
            ikiwa _HAVE_THREAD_NATIVE_ID:
                self._set_native_id()
            self._started.set()
            ukijumuisha _active_limbo_lock:
                _active[self._ident] = self
                toa _limbo[self]

            ikiwa _trace_hook:
                _sys.settrace(_trace_hook)
            ikiwa _profile_hook:
                _sys.setprofile(_profile_hook)

            jaribu:
                self.run()
            tatizo:
                self._invoke_excepthook(self)
        mwishowe:
            ukijumuisha _active_limbo_lock:
                jaribu:
                    # We don't call self._delete() because it also
                    # grabs _active_limbo_lock.
                    toa _active[get_ident()]
                tatizo:
                    pita

    eleza _stop(self):
        # After calling ._stop(), .is_alive() returns Uongo na .join() returns
        # immediately.  ._tstate_lock must be released before calling ._stop().
        #
        # Normal case:  C code at the end of the thread's life
        # (release_sentinel kwenye _threadmodule.c) releases ._tstate_lock, na
        # that's detected by our ._wait_for_tstate_lock(), called by .join()
        # na .is_alive().  Any number of threads _may_ call ._stop()
        # simultaneously (kila example, ikiwa multiple threads are blocked in
        # .join() calls), na they're sio serialized.  That's harmless -
        # they'll just make redundant rebindings of ._is_stopped na
        # ._tstate_lock.  Obscure:  we rebind ._tstate_lock last so that the
        # "assert self._is_stopped" kwenye ._wait_for_tstate_lock() always works
        # (the assert ni executed only ikiwa ._tstate_lock ni Tupu).
        #
        # Special case:  _main_thread releases ._tstate_lock via this
        # module's _shutdown() function.
        lock = self._tstate_lock
        ikiwa lock ni sio Tupu:
            assert sio lock.locked()
        self._is_stopped = Kweli
        self._tstate_lock = Tupu
        ikiwa sio self.daemon:
            ukijumuisha _shutdown_locks_lock:
                _shutdown_locks.discard(lock)

    eleza _delete(self):
        "Remove current thread kutoka the dict of currently running threads."
        ukijumuisha _active_limbo_lock:
            toa _active[get_ident()]
            # There must sio be any python code between the previous line
            # na after the lock ni released.  Otherwise a tracing function
            # could try to acquire the lock again kwenye the same thread, (in
            # current_thread()), na would block.

    eleza join(self, timeout=Tupu):
        """Wait until the thread terminates.

        This blocks the calling thread until the thread whose join() method is
        called terminates -- either normally ama through an unhandled exception
        ama until the optional timeout occurs.

        When the timeout argument ni present na sio Tupu, it should be a
        floating point number specifying a timeout kila the operation kwenye seconds
        (or fractions thereof). As join() always returns Tupu, you must call
        is_alive() after join() to decide whether a timeout happened -- ikiwa the
        thread ni still alive, the join() call timed out.

        When the timeout argument ni sio present ama Tupu, the operation will
        block until the thread terminates.

        A thread can be join()ed many times.

        join() raises a RuntimeError ikiwa an attempt ni made to join the current
        thread kama that would cause a deadlock. It ni also an error to join() a
        thread before it has been started na attempts to do so raises the same
        exception.

        """
        ikiwa sio self._initialized:
            ashiria RuntimeError("Thread.__init__() sio called")
        ikiwa sio self._started.is_set():
            ashiria RuntimeError("cannot join thread before it ni started")
        ikiwa self ni current_thread():
            ashiria RuntimeError("cannot join current thread")

        ikiwa timeout ni Tupu:
            self._wait_for_tstate_lock()
        isipokua:
            # the behavior of a negative timeout isn't documented, but
            # historically .join(timeout=x) kila x<0 has acted kama ikiwa timeout=0
            self._wait_for_tstate_lock(timeout=max(timeout, 0))

    eleza _wait_for_tstate_lock(self, block=Kweli, timeout=-1):
        # Issue #18808: wait kila the thread state to be gone.
        # At the end of the thread's life, after all knowledge of the thread
        # ni removed kutoka C data structures, C code releases our _tstate_lock.
        # This method pitaes its arguments to _tstate_lock.acquire().
        # If the lock ni acquired, the C code ni done, na self._stop() is
        # called.  That sets ._is_stopped to Kweli, na ._tstate_lock to Tupu.
        lock = self._tstate_lock
        ikiwa lock ni Tupu:  # already determined that the C code ni done
            assert self._is_stopped
        lasivyo lock.acquire(block, timeout):
            lock.release()
            self._stop()

    @property
    eleza name(self):
        """A string used kila identification purposes only.

        It has no semantics. Multiple threads may be given the same name. The
        initial name ni set by the constructor.

        """
        assert self._initialized, "Thread.__init__() sio called"
        rudisha self._name

    @name.setter
    eleza name(self, name):
        assert self._initialized, "Thread.__init__() sio called"
        self._name = str(name)

    @property
    eleza ident(self):
        """Thread identifier of this thread ama Tupu ikiwa it has sio been started.

        This ni a nonzero integer. See the get_ident() function. Thread
        identifiers may be recycled when a thread exits na another thread is
        created. The identifier ni available even after the thread has exited.

        """
        assert self._initialized, "Thread.__init__() sio called"
        rudisha self._ident

    ikiwa _HAVE_THREAD_NATIVE_ID:
        @property
        eleza native_id(self):
            """Native integral thread ID of this thread, ama Tupu ikiwa it has sio been started.

            This ni a non-negative integer. See the get_native_id() function.
            This represents the Thread ID kama reported by the kernel.

            """
            assert self._initialized, "Thread.__init__() sio called"
            rudisha self._native_id

    eleza is_alive(self):
        """Return whether the thread ni alive.

        This method returns Kweli just before the run() method starts until just
        after the run() method terminates. The module function enumerate()
        returns a list of all alive threads.

        """
        assert self._initialized, "Thread.__init__() sio called"
        ikiwa self._is_stopped ama sio self._started.is_set():
            rudisha Uongo
        self._wait_for_tstate_lock(Uongo)
        rudisha sio self._is_stopped

    eleza isAlive(self):
        """Return whether the thread ni alive.

        This method ni deprecated, use is_alive() instead.
        """
        agiza warnings
        warnings.warn('isAlive() ni deprecated, use is_alive() instead',
                      DeprecationWarning, stacklevel=2)
        rudisha self.is_alive()

    @property
    eleza daemon(self):
        """A boolean value indicating whether this thread ni a daemon thread.

        This must be set before start() ni called, otherwise RuntimeError is
        raised. Its initial value ni inherited kutoka the creating thread; the
        main thread ni sio a daemon thread na therefore all threads created in
        the main thread default to daemon = Uongo.

        The entire Python program exits when only daemon threads are left.

        """
        assert self._initialized, "Thread.__init__() sio called"
        rudisha self._daemonic

    @daemon.setter
    eleza daemon(self, daemonic):
        ikiwa sio self._initialized:
            ashiria RuntimeError("Thread.__init__() sio called")
        ikiwa self._started.is_set():
            ashiria RuntimeError("cannot set daemon status of active thread")
        self._daemonic = daemonic

    eleza isDaemon(self):
        rudisha self.daemon

    eleza setDaemon(self, daemonic):
        self.daemon = daemonic

    eleza getName(self):
        rudisha self.name

    eleza setName(self, name):
        self.name = name


jaribu:
    kutoka _thread agiza (_excepthook kama excepthook,
                         _ExceptHookArgs kama ExceptHookArgs)
tatizo ImportError:
    # Simple Python implementation ikiwa _thread._excepthook() ni sio available
    kutoka traceback agiza print_exception kama _print_exception
    kutoka collections agiza namedtuple

    _ExceptHookArgs = namedtuple(
        'ExceptHookArgs',
        'exc_type exc_value exc_traceback thread')

    eleza ExceptHookArgs(args):
        rudisha _ExceptHookArgs(*args)

    eleza excepthook(args, /):
        """
        Handle uncaught Thread.run() exception.
        """
        ikiwa args.exc_type == SystemExit:
            # silently ignore SystemExit
            rudisha

        ikiwa _sys ni sio Tupu na _sys.stderr ni sio Tupu:
            stderr = _sys.stderr
        lasivyo args.thread ni sio Tupu:
            stderr = args.thread._stderr
            ikiwa stderr ni Tupu:
                # do nothing ikiwa sys.stderr ni Tupu na sys.stderr was Tupu
                # when the thread was created
                rudisha
        isipokua:
            # do nothing ikiwa sys.stderr ni Tupu na args.thread ni Tupu
            rudisha

        ikiwa args.thread ni sio Tupu:
            name = args.thread.name
        isipokua:
            name = get_ident()
        andika(f"Exception kwenye thread {name}:",
              file=stderr, flush=Kweli)
        _print_exception(args.exc_type, args.exc_value, args.exc_traceback,
                         file=stderr)
        stderr.flush()


eleza _make_invoke_excepthook():
    # Create a local namespace to ensure that variables remain alive
    # when _invoke_excepthook() ni called, even ikiwa it ni called late during
    # Python shutdown. It ni mostly needed kila daemon threads.

    old_excepthook = excepthook
    old_sys_excepthook = _sys.excepthook
    ikiwa old_excepthook ni Tupu:
        ashiria RuntimeError("threading.excepthook ni Tupu")
    ikiwa old_sys_excepthook ni Tupu:
        ashiria RuntimeError("sys.excepthook ni Tupu")

    sys_exc_info = _sys.exc_info
    local_print = print
    local_sys = _sys

    eleza invoke_excepthook(thread):
        global excepthook
        jaribu:
            hook = excepthook
            ikiwa hook ni Tupu:
                hook = old_excepthook

            args = ExceptHookArgs([*sys_exc_info(), thread])

            hook(args)
        tatizo Exception kama exc:
            exc.__suppress_context__ = Kweli
            toa exc

            ikiwa local_sys ni sio Tupu na local_sys.stderr ni sio Tupu:
                stderr = local_sys.stderr
            isipokua:
                stderr = thread._stderr

            local_andika("Exception kwenye threading.excepthook:",
                        file=stderr, flush=Kweli)

            ikiwa local_sys ni sio Tupu na local_sys.excepthook ni sio Tupu:
                sys_excepthook = local_sys.excepthook
            isipokua:
                sys_excepthook = old_sys_excepthook

            sys_excepthook(*sys_exc_info())
        mwishowe:
            # Break reference cycle (exception stored kwenye a variable)
            args = Tupu

    rudisha invoke_excepthook


# The timer kundi was contributed by Itamar Shtull-Trauring

kundi Timer(Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=Tupu, kwargs=Tupu)
            t.start()
            t.cancel()     # stop the timer's action ikiwa it's still waiting

    """

    eleza __init__(self, interval, function, args=Tupu, kwargs=Tupu):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args ikiwa args ni sio Tupu isipokua []
        self.kwargs = kwargs ikiwa kwargs ni sio Tupu isipokua {}
        self.finished = Event()

    eleza cancel(self):
        """Stop the timer ikiwa it hasn't finished yet."""
        self.finished.set()

    eleza run(self):
        self.finished.wait(self.interval)
        ikiwa sio self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()


# Special thread kundi to represent the main thread

kundi _MainThread(Thread):

    eleza __init__(self):
        Thread.__init__(self, name="MainThread", daemon=Uongo)
        self._set_tstate_lock()
        self._started.set()
        self._set_ident()
        ikiwa _HAVE_THREAD_NATIVE_ID:
            self._set_native_id()
        ukijumuisha _active_limbo_lock:
            _active[self._ident] = self


# Dummy thread kundi to represent threads sio started here.
# These aren't garbage collected when they die, nor can they be waited for.
# If they invoke anything kwenye threading.py that calls current_thread(), they
# leave an entry kwenye the _active dict forever after.
# Their purpose ni to rudisha *something* kutoka current_thread().
# They are marked kama daemon threads so we won't wait kila them
# when we exit (conform previous semantics).

kundi _DummyThread(Thread):

    eleza __init__(self):
        Thread.__init__(self, name=_newname("Dummy-%d"), daemon=Kweli)

        self._started.set()
        self._set_ident()
        ikiwa _HAVE_THREAD_NATIVE_ID:
            self._set_native_id()
        ukijumuisha _active_limbo_lock:
            _active[self._ident] = self

    eleza _stop(self):
        pita

    eleza is_alive(self):
        assert sio self._is_stopped na self._started.is_set()
        rudisha Kweli

    eleza join(self, timeout=Tupu):
        assert Uongo, "cannot join a dummy thread"


# Global API functions

eleza current_thread():
    """Return the current Thread object, corresponding to the caller's thread of control.

    If the caller's thread of control was sio created through the threading
    module, a dummy thread object ukijumuisha limited functionality ni returned.

    """
    jaribu:
        rudisha _active[get_ident()]
    tatizo KeyError:
        rudisha _DummyThread()

currentThread = current_thread

eleza active_count():
    """Return the number of Thread objects currently alive.

    The returned count ni equal to the length of the list returned by
    enumerate().

    """
    ukijumuisha _active_limbo_lock:
        rudisha len(_active) + len(_limbo)

activeCount = active_count

eleza _enumerate():
    # Same kama enumerate(), but without the lock. Internal use only.
    rudisha list(_active.values()) + list(_limbo.values())

eleza enumerate():
    """Return a list of all Thread objects currently alive.

    The list includes daemonic threads, dummy thread objects created by
    current_thread(), na the main thread. It excludes terminated threads na
    threads that have sio yet been started.

    """
    ukijumuisha _active_limbo_lock:
        rudisha list(_active.values()) + list(_limbo.values())

kutoka _thread agiza stack_size

# Create the main thread object,
# na make it available kila the interpreter
# (Py_Main) kama threading._shutdown.

_main_thread = _MainThread()

eleza _shutdown():
    """
    Wait until the Python thread state of all non-daemon threads get deleted.
    """
    # Obscure:  other threads may be waiting to join _main_thread.  That's
    # dubious, but some code does it.  We can't wait kila C code to release
    # the main thread's tstate_lock - that won't happen until the interpreter
    # ni nearly dead.  So we release it here.  Note that just calling _stop()
    # isn't enough:  other threads may already be waiting on _tstate_lock.
    ikiwa _main_thread._is_stopped:
        # _shutdown() was already called
        rudisha

    # Main thread
    tlock = _main_thread._tstate_lock
    # The main thread isn't finished yet, so its thread state lock can't have
    # been released.
    assert tlock ni sio Tupu
    assert tlock.locked()
    tlock.release()
    _main_thread._stop()

    # Join all non-deamon threads
    wakati Kweli:
        ukijumuisha _shutdown_locks_lock:
            locks = list(_shutdown_locks)
            _shutdown_locks.clear()

        ikiwa sio locks:
            koma

        kila lock kwenye locks:
            # mimick Thread.join()
            lock.acquire()
            lock.release()

        # new threads can be spawned wakati we were waiting kila the other
        # threads to complete


eleza main_thread():
    """Return the main thread object.

    In normal conditions, the main thread ni the thread kutoka which the
    Python interpreter was started.
    """
    rudisha _main_thread

# get thread-local implementation, either kutoka the thread
# module, ama kutoka the python fallback

jaribu:
    kutoka _thread agiza _local kama local
tatizo ImportError:
    kutoka _threading_local agiza local


eleza _after_fork():
    """
    Cleanup threading module state that should sio exist after a fork.
    """
    # Reset _active_limbo_lock, kwenye case we forked wakati the lock was held
    # by another (non-forked) thread.  http://bugs.python.org/issue874900
    global _active_limbo_lock, _main_thread
    global _shutdown_locks_lock, _shutdown_locks
    _active_limbo_lock = _allocate_lock()

    # fork() only copied the current thread; clear references to others.
    new_active = {}
    current = current_thread()
    _main_thread = current

    # reset _shutdown() locks: threads re-register their _tstate_lock below
    _shutdown_locks_lock = _allocate_lock()
    _shutdown_locks = set()

    ukijumuisha _active_limbo_lock:
        # Dangling thread instances must still have their locks reset,
        # because someone may join() them.
        threads = set(_enumerate())
        threads.update(_dangling)
        kila thread kwenye threads:
            # Any lock/condition variable may be currently locked ama kwenye an
            # invalid state, so we reinitialize them.
            ikiwa thread ni current:
                # There ni only one active thread. We reset the ident to
                # its new value since it can have changed.
                thread._reset_internal_locks(Kweli)
                ident = get_ident()
                thread._ident = ident
                new_active[ident] = thread
            isipokua:
                # All the others are already stopped.
                thread._reset_internal_locks(Uongo)
                thread._stop()

        _limbo.clear()
        _active.clear()
        _active.update(new_active)
        assert len(_active) == 1


ikiwa hasattr(_os, "register_at_fork"):
    _os.register_at_fork(after_in_child=_after_fork)
