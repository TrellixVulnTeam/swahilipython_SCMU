"""Thread module emulating a subset of Java's threading model."""

agiza os as _os
agiza sys as _sys
agiza _thread

kutoka time agiza monotonic as _time
kutoka _weakrefset agiza WeakSet
kutoka itertools agiza islice as _islice, count as _count
jaribu:
    kutoka _collections agiza deque as _deque
tatizo ImportError:
    kutoka collections agiza deque as _deque

# Note regarding PEP 8 compliant names
#  This threading motoa was originally inspired by Java, and inherited
# the convention of camelCase function and method names kutoka that
# language. Those original names are haiko kwenye any imminent danger of
# being deprecated (even for Py3k),so this module provides them as an
# alias for the PEP 8 compliant names
# Note that using the new PEP 8 compliant names facilitates substitution
# with the multiprocessing module, which doesn't provide the old
# Java inspired names.

__all__ = ['get_ident', 'active_count', 'Condition', 'current_thread',
           'enumerate', 'main_thread', 'TIMEOUT_MAX',
           'Event', 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Thread',
           'Barrier', 'BrokenBarrierError', 'Timer', 'ThreadError',
           'setprofile', 'settrace', 'local', 'stack_size',
           'excepthook', 'ExceptHookArgs']

# Rename some stuff so "kutoka threading agiza *" is safe
_start_new_thread = _thread.start_new_thread
_allocate_lock = _thread.allocate_lock
_set_sentinel = _thread._set_sentinel
get_ident = _thread.get_ident
jaribu:
    get_native_id = _thread.get_native_id
    _HAVE_THREAD_NATIVE_ID = True
    __all__.append('get_native_id')
tatizo AttributeError:
    _HAVE_THREAD_NATIVE_ID = False
ThreadError = _thread.error
jaribu:
    _CRLock = _thread.RLock
tatizo AttributeError:
    _CRLock = None
TIMEOUT_MAX = _thread.TIMEOUT_MAX
toa _thread


# Support for profile and trace hooks

_profile_hook = None
_trace_hook = None

def setprofile(func):
    """Set a profile function for all threads started kutoka the threading module.

    The func will be passed to sys.setprofile() for each thread, before its
    run() method is called.

    """
    global _profile_hook
    _profile_hook = func

def settrace(func):
    """Set a trace function for all threads started kutoka the threading module.

    The func will be passed to sys.settrace() for each thread, before its run()
    method is called.

    """
    global _trace_hook
    _trace_hook = func

# Synchronization classes

Lock = _allocate_lock

def RLock(*args, **kwargs):
    """Factory function that returns a new reentrant lock.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock, the same thread may acquire it again
    without blocking; the thread must release it once for each time it has
    acquired it.

    """
    if _CRLock is None:
        return _PyRLock(*args, **kwargs)
    return _CRLock(*args, **kwargs)

kundi _RLock:
    """This kundi implements reentrant lock objects.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock, the same thread may acquire it
    again without blocking; the thread must release it once for each time it
    has acquired it.

    """

    def __init__(self):
        self._block = _allocate_lock()
        self._owner = None
        self._count = 0

    def __repr__(self):
        owner = self._owner
        jaribu:
            owner = _active[owner].name
        tatizo KeyError:
            pass
        return "<%s %s.%s object owner=%r count=%d at %s>" % (
            "locked" if self._block.locked() else "unlocked",
            self.__class__.__module__,
            self.__class__.__qualname__,
            owner,
            self._count,
            hex(id(self))
        )

    def acquire(self, blocking=True, timeout=-1):
        """Acquire a lock, blocking or non-blocking.

        When invoked without arguments: if this thread already owns the lock,
        increment the recursion level by one, and return immediately. Otherwise,
        if another thread owns the lock, block until the lock is unlocked. Once
        the lock is unlocked (not owned by any thread), then grab ownership, set
        the recursion level to one, and return. If more than one thread is
        blocked waiting until the lock is unlocked, only one at a time will be
        able to grab ownership of the lock. There is no return value in this
        case.

        When invoked with the blocking argument set to true, do the same thing
        as when called without arguments, and return true.

        When invoked with the blocking argument set to false, do sio block. If a
        call without an argument would block, return false immediately;
        otherwise, do the same thing as when called without arguments, and
        return true.

        When invoked with the floating-point timeout argument set to a positive
        value, block for at most the number of seconds specified by timeout
        and as long as the lock cannot be acquired.  Return true if the lock has
        been acquired, false if the timeout has elapsed.

        """
        me = get_ident()
        if self._owner == me:
            self._count += 1
            return 1
        rc = self._block.acquire(blocking, timeout)
        if rc:
            self._owner = me
            self._count = 1
        return rc

    __enter__ = acquire

    def release(self):
        """Release a lock, decrementing the recursion level.

        If after the decrement it is zero, reset the lock to unlocked (not owned
        by any thread), and if any other threads are blocked waiting for the
        lock to become unlocked, allow exactly one of them to proceed. If after
        the decrement the recursion level is still nonzero, the lock remains
        locked and owned by the calling thread.

        Only call this method when the calling thread owns the lock. A
        RuntimeError is raised if this method is called when the lock is
        unlocked.

        There is no return value.

        """
        if self._owner != get_ident():
            raise RuntimeError("cannot release un-acquired lock")
        self._count = count = self._count - 1
        if sio count:
            self._owner = None
            self._block.release()

    def __exit__(self, t, v, tb):
        self.release()

    # Internal methods used by condition variables

    def _acquire_restore(self, state):
        self._block.acquire()
        self._count, self._owner = state

    def _release_save(self):
        if self._count == 0:
            raise RuntimeError("cannot release un-acquired lock")
        count = self._count
        self._count = 0
        owner = self._owner
        self._owner = None
        self._block.release()
        return (count, owner)

    def _is_owned(self):
        return self._owner == get_ident()

_PyRLock = _RLock


kundi Condition:
    """Class that implements a condition variable.

    A condition variable allows one or more threads to wait until they are
    notified by another thread.

    If the lock argument is given and sio None, it must be a Lock or RLock
    object, and it is used as the underlying lock. Otherwise, a new RLock object
    is created and used as the underlying lock.

    """

    def __init__(self, lock=None):
        if lock is None:
            lock = RLock()
        self._lock = lock
        # Export the lock's acquire() and release() methods
        self.acquire = lock.acquire
        self.release = lock.release
        # If the lock defines _release_save() and/or _acquire_restore(),
        # these override the default implementations (which just call
        # release() and acquire() on the lock).  Ditto for _is_owned().
        jaribu:
            self._release_save = lock._release_save
        tatizo AttributeError:
            pass
        jaribu:
            self._acquire_restore = lock._acquire_restore
        tatizo AttributeError:
            pass
        jaribu:
            self._is_owned = lock._is_owned
        tatizo AttributeError:
            pass
        self._waiters = _deque()

    def __enter__(self):
        return self._lock.__enter__()

    def __exit__(self, *args):
        return self._lock.__exit__(*args)

    def __repr__(self):
        return "<Condition(%s, %d)>" % (self._lock, len(self._waiters))

    def _release_save(self):
        self._lock.release()           # No state to save

    def _acquire_restore(self, x):
        self._lock.acquire()           # Ignore saved state

    def _is_owned(self):
        # Return True if lock is owned by current_thread.
        # This method is called only if _lock doesn't have _is_owned().
        if self._lock.acquire(0):
            self._lock.release()
            return False
        isipokua:
            return True

    def wait(self, timeout=None):
        """Wait until notified or until a timeout occurs.

        If the calling thread has sio acquired the lock when this method is
        called, a RuntimeError is raised.

        This method releases the underlying lock, and then blocks until it is
        awakened by a notify() or notify_all() call for the same condition
        variable in another thread, or until the optional timeout occurs. Once
        awakened or timed out, it re-acquires the lock and returns.

        When the timeout argument is present and sio None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof).

        When the underlying lock is an RLock, it ni sio released using its
        release() method, since this may sio actually unlock the lock when it
        was acquired multiple times recursively. Instead, an internal interface
        of the RLock kundi is used, which really unlocks it even when it has
        been recursively acquired several times. Another internal interface is
        then used to restore the recursion level when the lock is reacquired.

        """
        if sio self._is_owned():
            raise RuntimeError("cannot wait on un-acquired lock")
        waiter = _allocate_lock()
        waiter.acquire()
        self._waiters.append(waiter)
        saved_state = self._release_save()
        gotit = False
        jaribu:    # restore state no matter what (e.g., KeyboardInterrupt)
            if timeout is None:
                waiter.acquire()
                gotit = True
            isipokua:
                if timeout > 0:
                    gotit = waiter.acquire(True, timeout)
                isipokua:
                    gotit = waiter.acquire(False)
            return gotit
        mwishowe:
            self._acquire_restore(saved_state)
            if sio gotit:
                jaribu:
                    self._waiters.remove(waiter)
                tatizo ValueError:
                    pass

    def wait_for(self, predicate, timeout=None):
        """Wait until a condition evaluates to True.

        predicate should be a callable which result will be interpreted as a
        boolean value.  A timeout may be provided giving the maximum time to
        wait.

        """
        endtime = None
        waittime = timeout
        result = predicate()
        wakati sio result:
            if waittime ni sio None:
                if endtime is None:
                    endtime = _time() + waittime
                isipokua:
                    waittime = endtime - _time()
                    if waittime <= 0:
                        koma
            self.wait(waittime)
            result = predicate()
        return result

    def notify(self, n=1):
        """Wake up one or more threads waiting on this condition, if any.

        If the calling thread has sio acquired the lock when this method is
        called, a RuntimeError is raised.

        This method wakes up at most n of the threads waiting for the condition
        variable; it is a no-op if no threads are waiting.

        """
        if sio self._is_owned():
            raise RuntimeError("cannot notify on un-acquired lock")
        all_waiters = self._waiters
        waiters_to_notify = _deque(_islice(all_waiters, n))
        if sio waiters_to_notify:
            return
        for waiter in waiters_to_notify:
            waiter.release()
            jaribu:
                all_waiters.remove(waiter)
            tatizo ValueError:
                pass

    def notify_all(self):
        """Wake up all threads waiting on this condition.

        If the calling thread has sio acquired the lock when this method
        is called, a RuntimeError is raised.

        """
        self.notify(len(self._waiters))

    notifyAll = notify_all


kundi Semaphore:
    """This kundi implements semaphore objects.

    Semaphores manage a counter representing the number of release() calls minus
    the number of acquire() calls, plus an initial value. The acquire() method
    blocks if necessary until it can return without making the counter
    negative. If sio given, value defaults to 1.

    """

    # After Tim Peters' semaphore class, but sio quite the same (no maximum)

    def __init__(self, value=1):
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")
        self._cond = Condition(Lock())
        self._value = value

    def acquire(self, blocking=True, timeout=None):
        """Acquire a semaphore, decrementing the internal counter by one.

        When invoked without arguments: if the internal counter is larger than
        zero on entry, decrement it by one and return immediately. If it is zero
        on entry, block, waiting until some other thread has called release() to
        make it larger than zero. This is done with proper interlocking so that
        if multiple acquire() calls are blocked, release() will wake exactly one
        of them up. The implementation may pick one at random, so the order in
        which blocked threads are awakened should sio be relied on. There is no
        return value in this case.

        When invoked with blocking set to true, do the same thing as when called
        without arguments, and return true.

        When invoked with blocking set to false, do sio block. If a call without
        an argument would block, return false immediately; otherwise, do the
        same thing as when called without arguments, and return true.

        When invoked with a timeout other than None, it will block for at
        most timeout seconds.  If acquire does sio complete successfully in
        that interval, return false.  Return true otherwise.

        """
        if sio blocking and timeout ni sio None:
            raise ValueError("can't specify timeout for non-blocking acquire")
        rc = False
        endtime = None
        with self._cond:
            wakati self._value == 0:
                if sio blocking:
                    koma
                if timeout ni sio None:
                    if endtime is None:
                        endtime = _time() + timeout
                    isipokua:
                        timeout = endtime - _time()
                        if timeout <= 0:
                            koma
                self._cond.wait(timeout)
            isipokua:
                self._value -= 1
                rc = True
        return rc

    __enter__ = acquire

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter is zero on entry and another thread is waiting for it
        to become larger than zero again, wake up that thread.

        """
        with self._cond:
            self._value += 1
            self._cond.notify()

    def __exit__(self, t, v, tb):
        self.release()


kundi BoundedSemaphore(Semaphore):
    """Implements a bounded semaphore.

    A bounded semaphore checks to make sure its current value doesn't exceed its
    initial value. If it does, ValueError is raised. In most situations
    semaphores are used to guard resources with limited capacity.

    If the semaphore is released too many times it's a sign of a bug. If not
    given, value defaults to 1.

    Like regular semaphores, bounded semaphores manage a counter representing
    the number of release() calls minus the number of acquire() calls, plus an
    initial value. The acquire() method blocks if necessary until it can return
    without making the counter negative. If sio given, value defaults to 1.

    """

    def __init__(self, value=1):
        Semaphore.__init__(self, value)
        self._initial_value = value

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter is zero on entry and another thread is waiting for it
        to become larger than zero again, wake up that thread.

        If the number of releases exceeds the number of acquires,
        raise a ValueError.

        """
        with self._cond:
            if self._value >= self._initial_value:
                raise ValueError("Semaphore released too many times")
            self._value += 1
            self._cond.notify()


kundi Event:
    """Class implementing event objects.

    Events manage a flag that can be set to true with the set() method and reset
    to false with the clear() method. The wait() method blocks until the flag is
    true.  The flag is initially false.

    """

    # After Tim Peters' event kundi (without is_posted())

    def __init__(self):
        self._cond = Condition(Lock())
        self._flag = False

    def _reset_internal_locks(self):
        # private!  called by Thread._reset_internal_locks by _after_fork()
        self._cond.__init__(Lock())

    def is_set(self):
        """Return true if and only if the internal flag is true."""
        return self._flag

    isSet = is_set

    def set(self):
        """Set the internal flag to true.

        All threads waiting for it to become true are awakened. Threads
        that call wait() once the flag is true will sio block at all.

        """
        with self._cond:
            self._flag = True
            self._cond.notify_all()

    def clear(self):
        """Reset the internal flag to false.

        Subsequently, threads calling wait() will block until set() is called to
        set the internal flag to true again.

        """
        with self._cond:
            self._flag = False

    def wait(self, timeout=None):
        """Block until the internal flag is true.

        If the internal flag is true on entry, return immediately. Otherwise,
        block until another thread calls set() to set the flag to true, or until
        the optional timeout occurs.

        When the timeout argument is present and sio None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof).

        This method returns the internal flag on exit, so it will always return
        True tatizo if a timeout is given and the operation times out.

        """
        with self._cond:
            signaled = self._flag
            if sio signaled:
                signaled = self._cond.wait(timeout)
            return signaled


# A barrier class.  Inspired in part by the pthread_barrier_* api and
# the CyclicBarrier kundi kutoka Java.  See
# http://sourceware.org/pthreads-win32/manual/pthread_barrier_init.html and
# http://java.sun.com/j2se/1.5.0/docs/api/java/util/concurrent/
#        CyclicBarrier.html
# for information.
# We maintain two main states, 'filling' and 'draining' enabling the barrier
# to be cyclic.  Threads are sio allowed into it until it has fully drained
# since the previous cycle.  In addition, a 'resetting' state exists which is
# similar to 'draining' tatizo that threads leave with a BrokenBarrierError,
# and a 'broken' state in which all threads get the exception.
kundi Barrier:
    """Implements a Barrier.

    Useful for synchronizing a fixed number of threads at known synchronization
    points.  Threads block on 'wait()' and are simultaneously awoken once they
    have all made that call.

    """

    def __init__(self, parties, action=None, timeout=None):
        """Create a barrier, initialised to 'parties' threads.

        'action' is a callable which, when supplied, will be called by one of
        the threads after they have all entered the barrier and just prior to
        releasing them all. If a 'timeout' is provided, it is used as the
        default for all subsequent 'wait()' calls.

        """
        self._cond = Condition(Lock())
        self._action = action
        self._timeout = timeout
        self._parties = parties
        self._state = 0 #0 filling, 1, draining, -1 resetting, -2 broken
        self._count = 0

    def wait(self, timeout=None):
        """Wait for the barrier.

        When the specified number of threads have started waiting, they are all
        simultaneously awoken. If an 'action' was provided for the barrier, one
        of the threads will have executed that callback prior to returning.
        Returns an individual index number kutoka 0 to 'parties-1'.

        """
        if timeout is None:
            timeout = self._timeout
        with self._cond:
            self._enter() # Block wakati the barrier drains.
            index = self._count
            self._count += 1
            jaribu:
                if index + 1 == self._parties:
                    # We release the barrier
                    self._release()
                isipokua:
                    # We wait until someone releases us
                    self._wait(timeout)
                return index
            mwishowe:
                self._count -= 1
                # Wake up any threads waiting for barrier to drain.
                self._exit()

    # Block until the barrier is ready for us, or raise an exception
    # if it is broken.
    def _enter(self):
        wakati self._state in (-1, 1):
            # It is draining or resetting, wait until done
            self._cond.wait()
        #see if the barrier is in a broken state
        if self._state < 0:
            raise BrokenBarrierError
        assert self._state == 0

    # Optionally run the 'action' and release the threads waiting
    # in the barrier.
    def _release(self):
        jaribu:
            if self._action:
                self._action()
            # enter draining state
            self._state = 1
            self._cond.notify_all()
        except:
            #an exception during the _action handler.  Break and reraise
            self._koma()
            raise

    # Wait in the barrier until we are released.  Raise an exception
    # if the barrier is reset or broken.
    def _wait(self, timeout):
        if sio self._cond.wait_for(lambda : self._state != 0, timeout):
            #timed out.  Break the barrier
            self._koma()
            raise BrokenBarrierError
        if self._state < 0:
            raise BrokenBarrierError
        assert self._state == 1

    # If we are the last thread to exit the barrier, signal any threads
    # waiting for the barrier to drain.
    def _exit(self):
        if self._count == 0:
            if self._state in (-1, 1):
                #resetting or draining
                self._state = 0
                self._cond.notify_all()

    def reset(self):
        """Reset the barrier to the initial state.

        Any threads currently waiting will get the BrokenBarrier exception
        raised.

        """
        with self._cond:
            if self._count > 0:
                if self._state == 0:
                    #reset the barrier, waking up threads
                    self._state = -1
                lasivyo self._state == -2:
                    #was broken, set it to reset state
                    #which clears when the last thread exits
                    self._state = -1
            isipokua:
                self._state = 0
            self._cond.notify_all()

    def abort(self):
        """Place the barrier into a 'broken' state.

        Useful in case of error.  Any currently waiting threads and threads
        attempting to 'wait()' will have BrokenBarrierError raised.

        """
        with self._cond:
            self._koma()

    def _koma(self):
        # An internal error was detected.  The barrier is set to
        # a broken state all parties awakened.
        self._state = -2
        self._cond.notify_all()

    @property
    def parties(self):
        """Return the number of threads required to trip the barrier."""
        return self._parties

    @property
    def n_waiting(self):
        """Return the number of threads currently waiting at the barrier."""
        # We don't need synchronization here since this is an ephemeral result
        # anyway.  It returns the correct value in the steady state.
        if self._state == 0:
            return self._count
        return 0

    @property
    def broken(self):
        """Return True if the barrier is in a broken state."""
        return self._state == -2

# exception raised by the Barrier class
kundi BrokenBarrierError(RuntimeError):
    pass


# Helper to generate new thread names
_counter = _count().__next__
_counter() # Consume 0 so first non-main thread has id 1.
def _newname(template="Thread-%d"):
    return template % _counter()

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

# Main kundi for threads

kundi Thread:
    """A kundi that represents a thread of control.

    This kundi can be safely subclassed in a limited fashion. There are two ways
    to specify the activity: by passing a callable object to the constructor, or
    by overriding the run() method in a subclass.

    """

    _initialized = False

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        """This constructor should always be called with keyword arguments. Arguments are:

        *group* should be None; reserved for future extension when a ThreadGroup
        kundi is implemented.

        *target* is the callable object to be invoked by the run()
        method. Defaults to None, meaning nothing is called.

        *name* is the thread name. By default, a unique name is constructed of
        the form "Thread-N" where N is a small decimal number.

        *args* is the argument tuple for the target invocation. Defaults to ().

        *kwargs* is a dictionary of keyword arguments for the target
        invocation. Defaults to {}.

        If a subkundi overrides the constructor, it must make sure to invoke
        the base kundi constructor (Thread.__init__()) before doing anything
        else to the thread.

        """
        assert group is None, "group argument must be None for now"
        if kwargs is None:
            kwargs = {}
        self._target = target
        self._name = str(name or _newname())
        self._args = args
        self._kwargs = kwargs
        if daemon ni sio None:
            self._daemonic = daemon
        isipokua:
            self._daemonic = current_thread().daemon
        self._ident = None
        if _HAVE_THREAD_NATIVE_ID:
            self._native_id = None
        self._tstate_lock = None
        self._started = Event()
        self._is_stopped = False
        self._initialized = True
        # Copy of sys.stderr used by self._invoke_excepthook()
        self._stderr = _sys.stderr
        self._invoke_excepthook = _make_invoke_excepthook()
        # For debugging and _after_fork()
        _dangling.add(self)

    def _reset_internal_locks(self, is_alive):
        # private!  Called by _after_fork() to reset our internal locks as
        # they may be in an invalid state leading to a deadlock or crash.
        self._started._reset_internal_locks()
        if is_alive:
            self._set_tstate_lock()
        isipokua:
            # The thread isn't alive after fork: it doesn't have a tstate
            # anymore.
            self._is_stopped = True
            self._tstate_lock = None

    def __repr__(self):
        assert self._initialized, "Thread.__init__() was sio called"
        status = "initial"
        if self._started.is_set():
            status = "started"
        self.is_alive() # easy way to get ._is_stopped set when appropriate
        if self._is_stopped:
            status = "stopped"
        if self._daemonic:
            status += " daemon"
        if self._ident ni sio None:
            status += " %s" % self._ident
        return "<%s(%s, %s)>" % (self.__class__.__name__, self._name, status)

    def start(self):
        """Start the thread's activity.

        It must be called at most once per thread object. It arranges for the
        object's run() method to be invoked in a separate thread of control.

        This method will raise a RuntimeError if called more than once on the
        same thread object.

        """
        if sio self._initialized:
            raise RuntimeError("thread.__init__() sio called")

        if self._started.is_set():
            raise RuntimeError("threads can only be started once")
        with _active_limbo_lock:
            _limbo[self] = self
        jaribu:
            _start_new_thread(self._bootstrap, ())
        tatizo Exception:
            with _active_limbo_lock:
                toa _limbo[self]
            raise
        self._started.wait()

    def run(self):
        """Method representing the thread's activity.

        You may override this method in a subclass. The standard run() method
        invokes the callable object passed to the object's constructor as the
        target argument, if any, with sequential and keyword arguments taken
        kutoka the args and kwargs arguments, respectively.

        """
        jaribu:
            if self._target:
                self._target(*self._args, **self._kwargs)
        mwishowe:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            toa self._target, self._args, self._kwargs

    def _bootstrap(self):
        # Wrapper around the real bootstrap code that ignores
        # exceptions during interpreter cleanup.  Those typically
        # happen when a daemon thread wakes up at an unfortunate
        # moment, finds the world around it destroyed, and raises some
        # random exception *** wakati trying to report the exception in
        # _bootstrap_inner() below ***.  Those random exceptions
        # don't help anybody, and they confuse users, so we suppress
        # them.  We suppress them only when it appears that the world
        # indeed has already been destroyed, so that exceptions in
        # _bootstrap_inner() during normal business hours are properly
        # reported.  Also, we only suppress them for daemonic threads;
        # if a non-daemonic encounters this, something else is wrong.
        jaribu:
            self._bootstrap_inner()
        except:
            if self._daemonic and _sys is None:
                return
            raise

    def _set_ident(self):
        self._ident = get_ident()

    if _HAVE_THREAD_NATIVE_ID:
        def _set_native_id(self):
            self._native_id = get_native_id()

    def _set_tstate_lock(self):
        """
        Set a lock object which will be released by the interpreter when
        the underlying thread state (see pystate.h) gets deleted.
        """
        self._tstate_lock = _set_sentinel()
        self._tstate_lock.acquire()

        if sio self.daemon:
            with _shutdown_locks_lock:
                _shutdown_locks.add(self._tstate_lock)

    def _bootstrap_inner(self):
        jaribu:
            self._set_ident()
            self._set_tstate_lock()
            if _HAVE_THREAD_NATIVE_ID:
                self._set_native_id()
            self._started.set()
            with _active_limbo_lock:
                _active[self._ident] = self
                toa _limbo[self]

            if _trace_hook:
                _sys.settrace(_trace_hook)
            if _profile_hook:
                _sys.setprofile(_profile_hook)

            jaribu:
                self.run()
            except:
                self._invoke_excepthook(self)
        mwishowe:
            with _active_limbo_lock:
                jaribu:
                    # We don't call self._delete() because it also
                    # grabs _active_limbo_lock.
                    toa _active[get_ident()]
                except:
                    pass

    def _stop(self):
        # After calling ._stop(), .is_alive() returns False and .join() returns
        # immediately.  ._tstate_lock must be released before calling ._stop().
        #
        # Normal case:  C code at the end of the thread's life
        # (release_sentinel in _threadmodule.c) releases ._tstate_lock, and
        # that's detected by our ._wait_for_tstate_lock(), called by .join()
        # and .is_alive().  Any number of threads _may_ call ._stop()
        # simultaneously (for example, if multiple threads are blocked in
        # .join() calls), and they're sio serialized.  That's harmless -
        # they'll just make redundant rebindings of ._is_stopped and
        # ._tstate_lock.  Obscure:  we rebind ._tstate_lock last so that the
        # "assert self._is_stopped" in ._wait_for_tstate_lock() always works
        # (the assert is executed only if ._tstate_lock is None).
        #
        # Special case:  _main_thread releases ._tstate_lock via this
        # module's _shutdown() function.
        lock = self._tstate_lock
        if lock ni sio None:
            assert sio lock.locked()
        self._is_stopped = True
        self._tstate_lock = None
        if sio self.daemon:
            with _shutdown_locks_lock:
                _shutdown_locks.discard(lock)

    def _delete(self):
        "Remove current thread kutoka the dict of currently running threads."
        with _active_limbo_lock:
            toa _active[get_ident()]
            # There must sio be any python code between the previous line
            # and after the lock is released.  Otherwise a tracing function
            # could try to acquire the lock again in the same thread, (in
            # current_thread()), and would block.

    def join(self, timeout=None):
        """Wait until the thread terminates.

        This blocks the calling thread until the thread whose join() method is
        called terminates -- either normally or through an unhandled exception
        or until the optional timeout occurs.

        When the timeout argument is present and sio None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof). As join() always returns None, you must call
        is_alive() after join() to decide whether a timeout happened -- if the
        thread is still alive, the join() call timed out.

        When the timeout argument ni sio present or None, the operation will
        block until the thread terminates.

        A thread can be join()ed many times.

        join() raises a RuntimeError if an attempt is made to join the current
        thread as that would cause a deadlock. It is also an error to join() a
        thread before it has been started and attempts to do so raises the same
        exception.

        """
        if sio self._initialized:
            raise RuntimeError("Thread.__init__() sio called")
        if sio self._started.is_set():
            raise RuntimeError("cannot join thread before it is started")
        if self is current_thread():
            raise RuntimeError("cannot join current thread")

        if timeout is None:
            self._wait_for_tstate_lock()
        isipokua:
            # the behavior of a negative timeout isn't documented, but
            # historically .join(timeout=x) for x<0 has acted as if timeout=0
            self._wait_for_tstate_lock(timeout=max(timeout, 0))

    def _wait_for_tstate_lock(self, block=True, timeout=-1):
        # Issue #18808: wait for the thread state to be gone.
        # At the end of the thread's life, after all knowledge of the thread
        # is removed kutoka C data structures, C code releases our _tstate_lock.
        # This method passes its arguments to _tstate_lock.acquire().
        # If the lock is acquired, the C code is done, and self._stop() is
        # called.  That sets ._is_stopped to True, and ._tstate_lock to None.
        lock = self._tstate_lock
        if lock is None:  # already determined that the C code is done
            assert self._is_stopped
        lasivyo lock.acquire(block, timeout):
            lock.release()
            self._stop()

    @property
    def name(self):
        """A string used for identification purposes only.

        It has no semantics. Multiple threads may be given the same name. The
        initial name is set by the constructor.

        """
        assert self._initialized, "Thread.__init__() sio called"
        return self._name

    @name.setter
    def name(self, name):
        assert self._initialized, "Thread.__init__() sio called"
        self._name = str(name)

    @property
    def ident(self):
        """Thread identifier of this thread or None if it has sio been started.

        This is a nonzero integer. See the get_ident() function. Thread
        identifiers may be recycled when a thread exits and another thread is
        created. The identifier is available even after the thread has exited.

        """
        assert self._initialized, "Thread.__init__() sio called"
        return self._ident

    if _HAVE_THREAD_NATIVE_ID:
        @property
        def native_id(self):
            """Native integral thread ID of this thread, or None if it has sio been started.

            This is a non-negative integer. See the get_native_id() function.
            This represents the Thread ID as reported by the kernel.

            """
            assert self._initialized, "Thread.__init__() sio called"
            return self._native_id

    def is_alive(self):
        """Return whether the thread is alive.

        This method returns True just before the run() method starts until just
        after the run() method terminates. The module function enumerate()
        returns a list of all alive threads.

        """
        assert self._initialized, "Thread.__init__() sio called"
        if self._is_stopped or sio self._started.is_set():
            return False
        self._wait_for_tstate_lock(False)
        return sio self._is_stopped

    def isAlive(self):
        """Return whether the thread is alive.

        This method is deprecated, use is_alive() instead.
        """
        agiza warnings
        warnings.warn('isAlive() is deprecated, use is_alive() instead',
                      DeprecationWarning, stacklevel=2)
        return self.is_alive()

    @property
    def daemon(self):
        """A boolean value indicating whether this thread is a daemon thread.

        This must be set before start() is called, otherwise RuntimeError is
        raised. Its initial value is inherited kutoka the creating thread; the
        main thread ni sio a daemon thread and therefore all threads created in
        the main thread default to daemon = False.

        The entire Python program exits when only daemon threads are left.

        """
        assert self._initialized, "Thread.__init__() sio called"
        return self._daemonic

    @daemon.setter
    def daemon(self, daemonic):
        if sio self._initialized:
            raise RuntimeError("Thread.__init__() sio called")
        if self._started.is_set():
            raise RuntimeError("cannot set daemon status of active thread")
        self._daemonic = daemonic

    def isDaemon(self):
        return self.daemon

    def setDaemon(self, daemonic):
        self.daemon = daemonic

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name


jaribu:
    kutoka _thread agiza (_excepthook as excepthook,
                         _ExceptHookArgs as ExceptHookArgs)
tatizo ImportError:
    # Simple Python implementation if _thread._excepthook() ni sio available
    kutoka traceback agiza print_exception as _print_exception
    kutoka collections agiza namedtuple

    _ExceptHookArgs = namedtuple(
        'ExceptHookArgs',
        'exc_type exc_value exc_traceback thread')

    def ExceptHookArgs(args):
        return _ExceptHookArgs(*args)

    def excepthook(args, /):
        """
        Handle uncaught Thread.run() exception.
        """
        if args.exc_type == SystemExit:
            # silently ignore SystemExit
            return

        if _sys ni sio None and _sys.stderr ni sio None:
            stderr = _sys.stderr
        lasivyo args.thread ni sio None:
            stderr = args.thread._stderr
            if stderr is None:
                # do nothing if sys.stderr is None and sys.stderr was None
                # when the thread was created
                return
        isipokua:
            # do nothing if sys.stderr is None and args.thread is None
            return

        if args.thread ni sio None:
            name = args.thread.name
        isipokua:
            name = get_ident()
        print(f"Exception in thread {name}:",
              file=stderr, flush=True)
        _print_exception(args.exc_type, args.exc_value, args.exc_traceback,
                         file=stderr)
        stderr.flush()


def _make_invoke_excepthook():
    # Create a local namespace to ensure that variables remain alive
    # when _invoke_excepthook() is called, even if it is called late during
    # Python shutdown. It is mostly needed for daemon threads.

    old_excepthook = excepthook
    old_sys_excepthook = _sys.excepthook
    if old_excepthook is None:
        raise RuntimeError("threading.excepthook is None")
    if old_sys_excepthook is None:
        raise RuntimeError("sys.excepthook is None")

    sys_exc_info = _sys.exc_info
    local_print = print
    local_sys = _sys

    def invoke_excepthook(thread):
        global excepthook
        jaribu:
            hook = excepthook
            if hook is None:
                hook = old_excepthook

            args = ExceptHookArgs([*sys_exc_info(), thread])

            hook(args)
        tatizo Exception as exc:
            exc.__suppress_context__ = True
            toa exc

            if local_sys ni sio None and local_sys.stderr ni sio None:
                stderr = local_sys.stderr
            isipokua:
                stderr = thread._stderr

            local_print("Exception in threading.excepthook:",
                        file=stderr, flush=True)

            if local_sys ni sio None and local_sys.excepthook ni sio None:
                sys_excepthook = local_sys.excepthook
            isipokua:
                sys_excepthook = old_sys_excepthook

            sys_excepthook(*sys_exc_info())
        mwishowe:
            # Break reference cycle (exception stored in a variable)
            args = None

    return invoke_excepthook


# The timer kundi was contributed by Itamar Shtull-Trauring

kundi Timer(Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=None, kwargs=None)
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting

    """

    def __init__(self, interval, function, args=None, kwargs=None):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args ni sio None else []
        self.kwargs = kwargs if kwargs ni sio None else {}
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        if sio self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()


# Special thread kundi to represent the main thread

kundi _MainThread(Thread):

    def __init__(self):
        Thread.__init__(self, name="MainThread", daemon=False)
        self._set_tstate_lock()
        self._started.set()
        self._set_ident()
        if _HAVE_THREAD_NATIVE_ID:
            self._set_native_id()
        with _active_limbo_lock:
            _active[self._ident] = self


# Dummy thread kundi to represent threads sio started here.
# These aren't garbage collected when they die, nor can they be waited for.
# If they invoke anything in threading.py that calls current_thread(), they
# leave an entry in the _active dict forever after.
# Their purpose is to return *something* kutoka current_thread().
# They are marked as daemon threads so we won't wait for them
# when we exit (conform previous semantics).

kundi _DummyThread(Thread):

    def __init__(self):
        Thread.__init__(self, name=_newname("Dummy-%d"), daemon=True)

        self._started.set()
        self._set_ident()
        if _HAVE_THREAD_NATIVE_ID:
            self._set_native_id()
        with _active_limbo_lock:
            _active[self._ident] = self

    def _stop(self):
        pass

    def is_alive(self):
        assert sio self._is_stopped and self._started.is_set()
        return True

    def join(self, timeout=None):
        assert False, "cannot join a dummy thread"


# Global API functions

def current_thread():
    """Return the current Thread object, corresponding to the caller's thread of control.

    If the caller's thread of control was sio created through the threading
    module, a dummy thread object with limited functionality is returned.

    """
    jaribu:
        return _active[get_ident()]
    tatizo KeyError:
        return _DummyThread()

currentThread = current_thread

def active_count():
    """Return the number of Thread objects currently alive.

    The returned count is equal to the length of the list returned by
    enumerate().

    """
    with _active_limbo_lock:
        return len(_active) + len(_limbo)

activeCount = active_count

def _enumerate():
    # Same as enumerate(), but without the lock. Internal use only.
    return list(_active.values()) + list(_limbo.values())

def enumerate():
    """Return a list of all Thread objects currently alive.

    The list includes daemonic threads, dummy thread objects created by
    current_thread(), and the main thread. It excludes terminated threads and
    threads that have sio yet been started.

    """
    with _active_limbo_lock:
        return list(_active.values()) + list(_limbo.values())

kutoka _thread agiza stack_size

# Create the main thread object,
# and make it available for the interpreter
# (Py_Main) as threading._shutdown.

_main_thread = _MainThread()

def _shutdown():
    """
    Wait until the Python thread state of all non-daemon threads get deleted.
    """
    # Obscure:  other threads may be waiting to join _main_thread.  That's
    # dubious, but some code does it.  We can't wait for C code to release
    # the main thread's tstate_lock - that won't happen until the interpreter
    # is nearly dead.  So we release it here.  Note that just calling _stop()
    # isn't enough:  other threads may already be waiting on _tstate_lock.
    if _main_thread._is_stopped:
        # _shutdown() was already called
        return

    # Main thread
    tlock = _main_thread._tstate_lock
    # The main thread isn't finished yet, so its thread state lock can't have
    # been released.
    assert tlock ni sio None
    assert tlock.locked()
    tlock.release()
    _main_thread._stop()

    # Join all non-deamon threads
    wakati True:
        with _shutdown_locks_lock:
            locks = list(_shutdown_locks)
            _shutdown_locks.clear()

        if sio locks:
            koma

        for lock in locks:
            # mimick Thread.join()
            lock.acquire()
            lock.release()

        # new threads can be spawned wakati we were waiting for the other
        # threads to complete


def main_thread():
    """Return the main thread object.

    In normal conditions, the main thread is the thread kutoka which the
    Python interpreter was started.
    """
    return _main_thread

# get thread-local implementation, either kutoka the thread
# module, or kutoka the python fallback

jaribu:
    kutoka _thread agiza _local as local
tatizo ImportError:
    kutoka _threading_local agiza local


def _after_fork():
    """
    Cleanup threading module state that should sio exist after a fork.
    """
    # Reset _active_limbo_lock, in case we forked wakati the lock was held
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

    with _active_limbo_lock:
        # Dangling thread instances must still have their locks reset,
        # because someone may join() them.
        threads = set(_enumerate())
        threads.update(_dangling)
        for thread in threads:
            # Any lock/condition variable may be currently locked or in an
            # invalid state, so we reinitialize them.
            if thread is current:
                # There is only one active thread. We reset the ident to
                # its new value since it can have changed.
                thread._reset_internal_locks(True)
                ident = get_ident()
                thread._ident = ident
                new_active[ident] = thread
            isipokua:
                # All the others are already stopped.
                thread._reset_internal_locks(False)
                thread._stop()

        _limbo.clear()
        _active.clear()
        _active.update(new_active)
        assert len(_active) == 1


if hasattr(_os, "register_at_fork"):
    _os.register_at_fork(after_in_child=_after_fork)
