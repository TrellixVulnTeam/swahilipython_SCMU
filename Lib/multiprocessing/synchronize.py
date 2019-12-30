#
# Module implementing synchronization primitives
#
# multiprocessing/synchronize.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

__all__ = [
    'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition', 'Event'
    ]

agiza threading
agiza sys
agiza tempfile
agiza _multiprocessing
agiza time

kutoka . agiza context
kutoka . agiza process
kutoka . agiza util

# Try to agiza the mp.synchronize module cleanly, ikiwa it fails
# ashiria ImportError kila platforms lacking a working sem_open implementation.
# See issue 3770
jaribu:
    kutoka _multiprocessing agiza SemLock, sem_unlink
tatizo (ImportError):
    ashiria ImportError("This platform lacks a functioning sem_open" +
                      " implementation, therefore, the required" +
                      " synchronization primitives needed will not" +
                      " function, see issue 3770.")

#
# Constants
#

RECURSIVE_MUTEX, SEMAPHORE = list(range(2))
SEM_VALUE_MAX = _multiprocessing.SemLock.SEM_VALUE_MAX

#
# Base kundi kila semaphores na mutexes; wraps `_multiprocessing.SemLock`
#

kundi SemLock(object):

    _rand = tempfile._RandomNameSequence()

    eleza __init__(self, kind, value, maxvalue, *, ctx):
        ikiwa ctx ni Tupu:
            ctx = context._default_context.get_context()
        name = ctx.get_start_method()
        unlink_now = sys.platform == 'win32' ama name == 'fork'
        kila i kwenye range(100):
            jaribu:
                sl = self._semlock = _multiprocessing.SemLock(
                    kind, value, maxvalue, self._make_name(),
                    unlink_now)
            tatizo FileExistsError:
                pita
            isipokua:
                koma
        isipokua:
            ashiria FileExistsError('cannot find name kila semaphore')

        util.debug('created semlock ukijumuisha handle %s' % sl.handle)
        self._make_methods()

        ikiwa sys.platform != 'win32':
            eleza _after_fork(obj):
                obj._semlock._after_fork()
            util.register_after_fork(self, _after_fork)

        ikiwa self._semlock.name ni sio Tupu:
            # We only get here ikiwa we are on Unix ukijumuisha forking
            # disabled.  When the object ni garbage collected ama the
            # process shuts down we unlink the semaphore name
            kutoka .resource_tracker agiza register
            register(self._semlock.name, "semaphore")
            util.Finalize(self, SemLock._cleanup, (self._semlock.name,),
                          exitpriority=0)

    @staticmethod
    eleza _cleanup(name):
        kutoka .resource_tracker agiza unregister
        sem_unlink(name)
        unregister(name, "semaphore")

    eleza _make_methods(self):
        self.acquire = self._semlock.acquire
        self.release = self._semlock.release

    eleza __enter__(self):
        rudisha self._semlock.__enter__()

    eleza __exit__(self, *args):
        rudisha self._semlock.__exit__(*args)

    eleza __getstate__(self):
        context.assert_spawning(self)
        sl = self._semlock
        ikiwa sys.platform == 'win32':
            h = context.get_spawning_popen().duplicate_for_child(sl.handle)
        isipokua:
            h = sl.handle
        rudisha (h, sl.kind, sl.maxvalue, sl.name)

    eleza __setstate__(self, state):
        self._semlock = _multiprocessing.SemLock._rebuild(*state)
        util.debug('recreated blocker ukijumuisha handle %r' % state[0])
        self._make_methods()

    @staticmethod
    eleza _make_name():
        rudisha '%s-%s' % (process.current_process()._config['semprefix'],
                          next(SemLock._rand))

#
# Semaphore
#

kundi Semaphore(SemLock):

    eleza __init__(self, value=1, *, ctx):
        SemLock.__init__(self, SEMAPHORE, value, SEM_VALUE_MAX, ctx=ctx)

    eleza get_value(self):
        rudisha self._semlock._get_value()

    eleza __repr__(self):
        jaribu:
            value = self._semlock._get_value()
        tatizo Exception:
            value = 'unknown'
        rudisha '<%s(value=%s)>' % (self.__class__.__name__, value)

#
# Bounded semaphore
#

kundi BoundedSemaphore(Semaphore):

    eleza __init__(self, value=1, *, ctx):
        SemLock.__init__(self, SEMAPHORE, value, value, ctx=ctx)

    eleza __repr__(self):
        jaribu:
            value = self._semlock._get_value()
        tatizo Exception:
            value = 'unknown'
        rudisha '<%s(value=%s, maxvalue=%s)>' % \
               (self.__class__.__name__, value, self._semlock.maxvalue)

#
# Non-recursive lock
#

kundi Lock(SemLock):

    eleza __init__(self, *, ctx):
        SemLock.__init__(self, SEMAPHORE, 1, 1, ctx=ctx)

    eleza __repr__(self):
        jaribu:
            ikiwa self._semlock._is_mine():
                name = process.current_process().name
                ikiwa threading.current_thread().name != 'MainThread':
                    name += '|' + threading.current_thread().name
            lasivyo self._semlock._get_value() == 1:
                name = 'Tupu'
            lasivyo self._semlock._count() > 0:
                name = 'SomeOtherThread'
            isipokua:
                name = 'SomeOtherProcess'
        tatizo Exception:
            name = 'unknown'
        rudisha '<%s(owner=%s)>' % (self.__class__.__name__, name)

#
# Recursive lock
#

kundi RLock(SemLock):

    eleza __init__(self, *, ctx):
        SemLock.__init__(self, RECURSIVE_MUTEX, 1, 1, ctx=ctx)

    eleza __repr__(self):
        jaribu:
            ikiwa self._semlock._is_mine():
                name = process.current_process().name
                ikiwa threading.current_thread().name != 'MainThread':
                    name += '|' + threading.current_thread().name
                count = self._semlock._count()
            lasivyo self._semlock._get_value() == 1:
                name, count = 'Tupu', 0
            lasivyo self._semlock._count() > 0:
                name, count = 'SomeOtherThread', 'nonzero'
            isipokua:
                name, count = 'SomeOtherProcess', 'nonzero'
        tatizo Exception:
            name, count = 'unknown', 'unknown'
        rudisha '<%s(%s, %s)>' % (self.__class__.__name__, name, count)

#
# Condition variable
#

kundi Condition(object):

    eleza __init__(self, lock=Tupu, *, ctx):
        self._lock = lock ama ctx.RLock()
        self._sleeping_count = ctx.Semaphore(0)
        self._woken_count = ctx.Semaphore(0)
        self._wait_semaphore = ctx.Semaphore(0)
        self._make_methods()

    eleza __getstate__(self):
        context.assert_spawning(self)
        rudisha (self._lock, self._sleeping_count,
                self._woken_count, self._wait_semaphore)

    eleza __setstate__(self, state):
        (self._lock, self._sleeping_count,
         self._woken_count, self._wait_semaphore) = state
        self._make_methods()

    eleza __enter__(self):
        rudisha self._lock.__enter__()

    eleza __exit__(self, *args):
        rudisha self._lock.__exit__(*args)

    eleza _make_methods(self):
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    eleza __repr__(self):
        jaribu:
            num_waiters = (self._sleeping_count._semlock._get_value() -
                           self._woken_count._semlock._get_value())
        tatizo Exception:
            num_waiters = 'unknown'
        rudisha '<%s(%s, %s)>' % (self.__class__.__name__, self._lock, num_waiters)

    eleza wait(self, timeout=Tupu):
        assert self._lock._semlock._is_mine(), \
               'must acquire() condition before using wait()'

        # indicate that this thread ni going to sleep
        self._sleeping_count.release()

        # release lock
        count = self._lock._semlock._count()
        kila i kwenye range(count):
            self._lock.release()

        jaribu:
            # wait kila notification ama timeout
            rudisha self._wait_semaphore.acquire(Kweli, timeout)
        mwishowe:
            # indicate that this thread has woken
            self._woken_count.release()

            # reacquire lock
            kila i kwenye range(count):
                self._lock.acquire()

    eleza notify(self, n=1):
        assert self._lock._semlock._is_mine(), 'lock ni sio owned'
        assert sio self._wait_semaphore.acquire(
            Uongo), ('notify: Should sio have been able to acquire'
                     + '_wait_semaphore')

        # to take account of timeouts since last notify*() we subtract
        # woken_count kutoka sleeping_count na rezero woken_count
        wakati self._woken_count.acquire(Uongo):
            res = self._sleeping_count.acquire(Uongo)
            assert res, ('notify: Bug kwenye sleeping_count.acquire'
                         + '- res should sio be Uongo')

        sleepers = 0
        wakati sleepers < n na self._sleeping_count.acquire(Uongo):
            self._wait_semaphore.release()        # wake up one sleeper
            sleepers += 1

        ikiwa sleepers:
            kila i kwenye range(sleepers):
                self._woken_count.acquire()       # wait kila a sleeper to wake

            # rezero wait_semaphore kwenye case some timeouts just happened
            wakati self._wait_semaphore.acquire(Uongo):
                pita

    eleza notify_all(self):
        self.notify(n=sys.maxsize)

    eleza wait_for(self, predicate, timeout=Tupu):
        result = predicate()
        ikiwa result:
            rudisha result
        ikiwa timeout ni sio Tupu:
            endtime = time.monotonic() + timeout
        isipokua:
            endtime = Tupu
            waittime = Tupu
        wakati sio result:
            ikiwa endtime ni sio Tupu:
                waittime = endtime - time.monotonic()
                ikiwa waittime <= 0:
                    koma
            self.wait(waittime)
            result = predicate()
        rudisha result

#
# Event
#

kundi Event(object):

    eleza __init__(self, *, ctx):
        self._cond = ctx.Condition(ctx.Lock())
        self._flag = ctx.Semaphore(0)

    eleza is_set(self):
        ukijumuisha self._cond:
            ikiwa self._flag.acquire(Uongo):
                self._flag.release()
                rudisha Kweli
            rudisha Uongo

    eleza set(self):
        ukijumuisha self._cond:
            self._flag.acquire(Uongo)
            self._flag.release()
            self._cond.notify_all()

    eleza clear(self):
        ukijumuisha self._cond:
            self._flag.acquire(Uongo)

    eleza wait(self, timeout=Tupu):
        ukijumuisha self._cond:
            ikiwa self._flag.acquire(Uongo):
                self._flag.release()
            isipokua:
                self._cond.wait(timeout)

            ikiwa self._flag.acquire(Uongo):
                self._flag.release()
                rudisha Kweli
            rudisha Uongo

#
# Barrier
#

kundi Barrier(threading.Barrier):

    eleza __init__(self, parties, action=Tupu, timeout=Tupu, *, ctx):
        agiza struct
        kutoka .heap agiza BufferWrapper
        wrapper = BufferWrapper(struct.calcsize('i') * 2)
        cond = ctx.Condition()
        self.__setstate__((parties, action, timeout, cond, wrapper))
        self._state = 0
        self._count = 0

    eleza __setstate__(self, state):
        (self._parties, self._action, self._timeout,
         self._cond, self._wrapper) = state
        self._array = self._wrapper.create_memoryview().cast('i')

    eleza __getstate__(self):
        rudisha (self._parties, self._action, self._timeout,
                self._cond, self._wrapper)

    @property
    eleza _state(self):
        rudisha self._array[0]

    @_state.setter
    eleza _state(self, value):
        self._array[0] = value

    @property
    eleza _count(self):
        rudisha self._array[1]

    @_count.setter
    eleza _count(self, value):
        self._array[1] = value
