"""
Various tests kila synchronization primitives.
"""

agiza sys
agiza time
kutoka _thread agiza start_new_thread, TIMEOUT_MAX
agiza threading
agiza unittest
agiza weakref

kutoka test agiza support


eleza _wait():
    # A crude wait/tuma function sio relying on synchronization primitives.
    time.sleep(0.01)

kundi Bunch(object):
    """
    A bunch of threads.
    """
    eleza __init__(self, f, n, wait_before_exit=Uongo):
        """
        Construct a bunch of `n` threads running the same function `f`.
        If `wait_before_exit` ni Kweli, the threads won't terminate until
        do_finish() ni called.
        """
        self.f = f
        self.n = n
        self.started = []
        self.finished = []
        self._can_exit = sio wait_before_exit
        self.wait_thread = support.wait_threads_exit()
        self.wait_thread.__enter__()

        eleza task():
            tid = threading.get_ident()
            self.started.append(tid)
            jaribu:
                f()
            mwishowe:
                self.finished.append(tid)
                wakati sio self._can_exit:
                    _wait()

        jaribu:
            kila i kwenye range(n):
                start_new_thread(task, ())
        tatizo:
            self._can_exit = Kweli
            raise

    eleza wait_for_started(self):
        wakati len(self.started) < self.n:
            _wait()

    eleza wait_for_finished(self):
        wakati len(self.finished) < self.n:
            _wait()
        # Wait kila threads exit
        self.wait_thread.__exit__(Tupu, Tupu, Tupu)

    eleza do_finish(self):
        self._can_exit = Kweli


kundi BaseTestCase(unittest.TestCase):
    eleza setUp(self):
        self._threads = support.threading_setup()

    eleza tearDown(self):
        support.threading_cleanup(*self._threads)
        support.reap_children()

    eleza assertTimeout(self, actual, expected):
        # The waiting and/or time.monotonic() can be imprecise, which
        # ni why comparing to the expected value would sometimes fail
        # (especially under Windows).
        self.assertGreaterEqual(actual, expected * 0.6)
        # Test nothing insane happened
        self.assertLess(actual, expected * 10.0)


kundi BaseLockTests(BaseTestCase):
    """
    Tests kila both recursive na non-recursive locks.
    """

    eleza test_constructor(self):
        lock = self.locktype()
        toa lock

    eleza test_repr(self):
        lock = self.locktype()
        self.assertRegex(repr(lock), "<unlocked .* object (.*)?at .*>")
        toa lock

    eleza test_locked_repr(self):
        lock = self.locktype()
        lock.acquire()
        self.assertRegex(repr(lock), "<locked .* object (.*)?at .*>")
        toa lock

    eleza test_acquire_destroy(self):
        lock = self.locktype()
        lock.acquire()
        toa lock

    eleza test_acquire_release(self):
        lock = self.locktype()
        lock.acquire()
        lock.release()
        toa lock

    eleza test_try_acquire(self):
        lock = self.locktype()
        self.assertKweli(lock.acquire(Uongo))
        lock.release()

    eleza test_try_acquire_contended(self):
        lock = self.locktype()
        lock.acquire()
        result = []
        eleza f():
            result.append(lock.acquire(Uongo))
        Bunch(f, 1).wait_for_finished()
        self.assertUongo(result[0])
        lock.release()

    eleza test_acquire_contended(self):
        lock = self.locktype()
        lock.acquire()
        N = 5
        eleza f():
            lock.acquire()
            lock.release()

        b = Bunch(f, N)
        b.wait_for_started()
        _wait()
        self.assertEqual(len(b.finished), 0)
        lock.release()
        b.wait_for_finished()
        self.assertEqual(len(b.finished), N)

    eleza test_with(self):
        lock = self.locktype()
        eleza f():
            lock.acquire()
            lock.release()
        eleza _with(err=Tupu):
            ukijumuisha lock:
                ikiwa err ni sio Tupu:
                    ashiria err
        _with()
        # Check the lock ni unacquired
        Bunch(f, 1).wait_for_finished()
        self.assertRaises(TypeError, _with, TypeError)
        # Check the lock ni unacquired
        Bunch(f, 1).wait_for_finished()

    eleza test_thread_leak(self):
        # The lock shouldn't leak a Thread instance when used kutoka a foreign
        # (non-threading) thread.
        lock = self.locktype()
        eleza f():
            lock.acquire()
            lock.release()
        n = len(threading.enumerate())
        # We run many threads kwenye the hope that existing threads ids won't
        # be recycled.
        Bunch(f, 15).wait_for_finished()
        ikiwa len(threading.enumerate()) != n:
            # There ni a small window during which a Thread instance's
            # target function has finished running, but the Thread ni still
            # alive na registered.  Avoid spurious failures by waiting a
            # bit more (seen on a buildbot).
            time.sleep(0.4)
            self.assertEqual(n, len(threading.enumerate()))

    eleza test_timeout(self):
        lock = self.locktype()
        # Can't set timeout ikiwa sio blocking
        self.assertRaises(ValueError, lock.acquire, 0, 1)
        # Invalid timeout values
        self.assertRaises(ValueError, lock.acquire, timeout=-100)
        self.assertRaises(OverflowError, lock.acquire, timeout=1e100)
        self.assertRaises(OverflowError, lock.acquire, timeout=TIMEOUT_MAX + 1)
        # TIMEOUT_MAX ni ok
        lock.acquire(timeout=TIMEOUT_MAX)
        lock.release()
        t1 = time.monotonic()
        self.assertKweli(lock.acquire(timeout=5))
        t2 = time.monotonic()
        # Just a sanity test that it didn't actually wait kila the timeout.
        self.assertLess(t2 - t1, 5)
        results = []
        eleza f():
            t1 = time.monotonic()
            results.append(lock.acquire(timeout=0.5))
            t2 = time.monotonic()
            results.append(t2 - t1)
        Bunch(f, 1).wait_for_finished()
        self.assertUongo(results[0])
        self.assertTimeout(results[1], 0.5)

    eleza test_weakref_exists(self):
        lock = self.locktype()
        ref = weakref.ref(lock)
        self.assertIsNotTupu(ref())

    eleza test_weakref_deleted(self):
        lock = self.locktype()
        ref = weakref.ref(lock)
        toa lock
        self.assertIsTupu(ref())


kundi LockTests(BaseLockTests):
    """
    Tests kila non-recursive, weak locks
    (which can be acquired na released kutoka different threads).
    """
    eleza test_reacquire(self):
        # Lock needs to be released before re-acquiring.
        lock = self.locktype()
        phase = []

        eleza f():
            lock.acquire()
            phase.append(Tupu)
            lock.acquire()
            phase.append(Tupu)

        ukijumuisha support.wait_threads_exit():
            start_new_thread(f, ())
            wakati len(phase) == 0:
                _wait()
            _wait()
            self.assertEqual(len(phase), 1)
            lock.release()
            wakati len(phase) == 1:
                _wait()
            self.assertEqual(len(phase), 2)

    eleza test_different_thread(self):
        # Lock can be released kutoka a different thread.
        lock = self.locktype()
        lock.acquire()
        eleza f():
            lock.release()
        b = Bunch(f, 1)
        b.wait_for_finished()
        lock.acquire()
        lock.release()

    eleza test_state_after_timeout(self):
        # Issue #11618: check that lock ni kwenye a proper state after a
        # (non-zero) timeout.
        lock = self.locktype()
        lock.acquire()
        self.assertUongo(lock.acquire(timeout=0.01))
        lock.release()
        self.assertUongo(lock.locked())
        self.assertKweli(lock.acquire(blocking=Uongo))


kundi RLockTests(BaseLockTests):
    """
    Tests kila recursive locks.
    """
    eleza test_reacquire(self):
        lock = self.locktype()
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()

    eleza test_release_unacquired(self):
        # Cannot release an unacquired lock
        lock = self.locktype()
        self.assertRaises(RuntimeError, lock.release)
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()
        self.assertRaises(RuntimeError, lock.release)

    eleza test_release_save_unacquired(self):
        # Cannot _release_save an unacquired lock
        lock = self.locktype()
        self.assertRaises(RuntimeError, lock._release_save)
        lock.acquire()
        lock.acquire()
        lock.release()
        lock.acquire()
        lock.release()
        lock.release()
        self.assertRaises(RuntimeError, lock._release_save)

    eleza test_different_thread(self):
        # Cannot release kutoka a different thread
        lock = self.locktype()
        eleza f():
            lock.acquire()
        b = Bunch(f, 1, Kweli)
        jaribu:
            self.assertRaises(RuntimeError, lock.release)
        mwishowe:
            b.do_finish()
        b.wait_for_finished()

    eleza test__is_owned(self):
        lock = self.locktype()
        self.assertUongo(lock._is_owned())
        lock.acquire()
        self.assertKweli(lock._is_owned())
        lock.acquire()
        self.assertKweli(lock._is_owned())
        result = []
        eleza f():
            result.append(lock._is_owned())
        Bunch(f, 1).wait_for_finished()
        self.assertUongo(result[0])
        lock.release()
        self.assertKweli(lock._is_owned())
        lock.release()
        self.assertUongo(lock._is_owned())


kundi EventTests(BaseTestCase):
    """
    Tests kila Event objects.
    """

    eleza test_is_set(self):
        evt = self.eventtype()
        self.assertUongo(evt.is_set())
        evt.set()
        self.assertKweli(evt.is_set())
        evt.set()
        self.assertKweli(evt.is_set())
        evt.clear()
        self.assertUongo(evt.is_set())
        evt.clear()
        self.assertUongo(evt.is_set())

    eleza _check_notify(self, evt):
        # All threads get notified
        N = 5
        results1 = []
        results2 = []
        eleza f():
            results1.append(evt.wait())
            results2.append(evt.wait())
        b = Bunch(f, N)
        b.wait_for_started()
        _wait()
        self.assertEqual(len(results1), 0)
        evt.set()
        b.wait_for_finished()
        self.assertEqual(results1, [Kweli] * N)
        self.assertEqual(results2, [Kweli] * N)

    eleza test_notify(self):
        evt = self.eventtype()
        self._check_notify(evt)
        # Another time, after an explicit clear()
        evt.set()
        evt.clear()
        self._check_notify(evt)

    eleza test_timeout(self):
        evt = self.eventtype()
        results1 = []
        results2 = []
        N = 5
        eleza f():
            results1.append(evt.wait(0.0))
            t1 = time.monotonic()
            r = evt.wait(0.5)
            t2 = time.monotonic()
            results2.append((r, t2 - t1))
        Bunch(f, N).wait_for_finished()
        self.assertEqual(results1, [Uongo] * N)
        kila r, dt kwenye results2:
            self.assertUongo(r)
            self.assertTimeout(dt, 0.5)
        # The event ni set
        results1 = []
        results2 = []
        evt.set()
        Bunch(f, N).wait_for_finished()
        self.assertEqual(results1, [Kweli] * N)
        kila r, dt kwenye results2:
            self.assertKweli(r)

    eleza test_set_and_clear(self):
        # Issue #13502: check that wait() returns true even when the event is
        # cleared before the waiting thread ni woken up.
        evt = self.eventtype()
        results = []
        timeout = 0.250
        N = 5
        eleza f():
            results.append(evt.wait(timeout * 4))
        b = Bunch(f, N)
        b.wait_for_started()
        time.sleep(timeout)
        evt.set()
        evt.clear()
        b.wait_for_finished()
        self.assertEqual(results, [Kweli] * N)

    eleza test_reset_internal_locks(self):
        # ensure that condition ni still using a Lock after reset
        evt = self.eventtype()
        ukijumuisha evt._cond:
            self.assertUongo(evt._cond.acquire(Uongo))
        evt._reset_internal_locks()
        ukijumuisha evt._cond:
            self.assertUongo(evt._cond.acquire(Uongo))


kundi ConditionTests(BaseTestCase):
    """
    Tests kila condition variables.
    """

    eleza test_acquire(self):
        cond = self.condtype()
        # Be default we have an RLock: the condition can be acquired multiple
        # times.
        cond.acquire()
        cond.acquire()
        cond.release()
        cond.release()
        lock = threading.Lock()
        cond = self.condtype(lock)
        cond.acquire()
        self.assertUongo(lock.acquire(Uongo))
        cond.release()
        self.assertKweli(lock.acquire(Uongo))
        self.assertUongo(cond.acquire(Uongo))
        lock.release()
        ukijumuisha cond:
            self.assertUongo(lock.acquire(Uongo))

    eleza test_unacquired_wait(self):
        cond = self.condtype()
        self.assertRaises(RuntimeError, cond.wait)

    eleza test_unacquired_notify(self):
        cond = self.condtype()
        self.assertRaises(RuntimeError, cond.notify)

    eleza _check_notify(self, cond):
        # Note that this test ni sensitive to timing.  If the worker threads
        # don't execute kwenye a timely fashion, the main thread may think they
        # are further along then they are.  The main thread therefore issues
        # _wait() statements to try to make sure that it doesn't race ahead
        # of the workers.
        # Secondly, this test assumes that condition variables are sio subject
        # to spurious wakeups.  The absence of spurious wakeups ni an implementation
        # detail of Condition Variables kwenye current CPython, but kwenye general, not
        # a guaranteed property of condition variables kama a programming
        # construct.  In particular, it ni possible that this can no longer
        # be conveniently guaranteed should their implementation ever change.
        N = 5
        ready = []
        results1 = []
        results2 = []
        phase_num = 0
        eleza f():
            cond.acquire()
            ready.append(phase_num)
            result = cond.wait()
            cond.release()
            results1.append((result, phase_num))
            cond.acquire()
            ready.append(phase_num)
            result = cond.wait()
            cond.release()
            results2.append((result, phase_num))
        b = Bunch(f, N)
        b.wait_for_started()
        # first wait, to ensure all workers settle into cond.wait() before
        # we endelea. See issues #8799 na #30727.
        wakati len(ready) < 5:
            _wait()
        ready.clear()
        self.assertEqual(results1, [])
        # Notify 3 threads at first
        cond.acquire()
        cond.notify(3)
        _wait()
        phase_num = 1
        cond.release()
        wakati len(results1) < 3:
            _wait()
        self.assertEqual(results1, [(Kweli, 1)] * 3)
        self.assertEqual(results2, [])
        # make sure all awaken workers settle into cond.wait()
        wakati len(ready) < 3:
            _wait()
        # Notify 5 threads: they might be kwenye their first ama second wait
        cond.acquire()
        cond.notify(5)
        _wait()
        phase_num = 2
        cond.release()
        wakati len(results1) + len(results2) < 8:
            _wait()
        self.assertEqual(results1, [(Kweli, 1)] * 3 + [(Kweli, 2)] * 2)
        self.assertEqual(results2, [(Kweli, 2)] * 3)
        # make sure all workers settle into cond.wait()
        wakati len(ready) < 5:
            _wait()
        # Notify all threads: they are all kwenye their second wait
        cond.acquire()
        cond.notify_all()
        _wait()
        phase_num = 3
        cond.release()
        wakati len(results2) < 5:
            _wait()
        self.assertEqual(results1, [(Kweli, 1)] * 3 + [(Kweli,2)] * 2)
        self.assertEqual(results2, [(Kweli, 2)] * 3 + [(Kweli, 3)] * 2)
        b.wait_for_finished()

    eleza test_notify(self):
        cond = self.condtype()
        self._check_notify(cond)
        # A second time, to check internal state ni still ok.
        self._check_notify(cond)

    eleza test_timeout(self):
        cond = self.condtype()
        results = []
        N = 5
        eleza f():
            cond.acquire()
            t1 = time.monotonic()
            result = cond.wait(0.5)
            t2 = time.monotonic()
            cond.release()
            results.append((t2 - t1, result))
        Bunch(f, N).wait_for_finished()
        self.assertEqual(len(results), N)
        kila dt, result kwenye results:
            self.assertTimeout(dt, 0.5)
            # Note that conceptually (that"s the condition variable protocol)
            # a wait() may succeed even ikiwa no one notifies us na before any
            # timeout occurs.  Spurious wakeups can occur.
            # This makes it hard to verify the result value.
            # In practice, this implementation has no spurious wakeups.
            self.assertUongo(result)

    eleza test_waitfor(self):
        cond = self.condtype()
        state = 0
        eleza f():
            ukijumuisha cond:
                result = cond.wait_for(lambda : state==4)
                self.assertKweli(result)
                self.assertEqual(state, 4)
        b = Bunch(f, 1)
        b.wait_for_started()
        kila i kwenye range(4):
            time.sleep(0.01)
            ukijumuisha cond:
                state += 1
                cond.notify()
        b.wait_for_finished()

    eleza test_waitfor_timeout(self):
        cond = self.condtype()
        state = 0
        success = []
        eleza f():
            ukijumuisha cond:
                dt = time.monotonic()
                result = cond.wait_for(lambda : state==4, timeout=0.1)
                dt = time.monotonic() - dt
                self.assertUongo(result)
                self.assertTimeout(dt, 0.1)
                success.append(Tupu)
        b = Bunch(f, 1)
        b.wait_for_started()
        # Only increment 3 times, so state == 4 ni never reached.
        kila i kwenye range(3):
            time.sleep(0.01)
            ukijumuisha cond:
                state += 1
                cond.notify()
        b.wait_for_finished()
        self.assertEqual(len(success), 1)


kundi BaseSemaphoreTests(BaseTestCase):
    """
    Common tests kila {bounded, unbounded} semaphore objects.
    """

    eleza test_constructor(self):
        self.assertRaises(ValueError, self.semtype, value = -1)
        self.assertRaises(ValueError, self.semtype, value = -sys.maxsize)

    eleza test_acquire(self):
        sem = self.semtype(1)
        sem.acquire()
        sem.release()
        sem = self.semtype(2)
        sem.acquire()
        sem.acquire()
        sem.release()
        sem.release()

    eleza test_acquire_destroy(self):
        sem = self.semtype()
        sem.acquire()
        toa sem

    eleza test_acquire_contended(self):
        sem = self.semtype(7)
        sem.acquire()
        N = 10
        sem_results = []
        results1 = []
        results2 = []
        phase_num = 0
        eleza f():
            sem_results.append(sem.acquire())
            results1.append(phase_num)
            sem_results.append(sem.acquire())
            results2.append(phase_num)
        b = Bunch(f, 10)
        b.wait_for_started()
        wakati len(results1) + len(results2) < 6:
            _wait()
        self.assertEqual(results1 + results2, [0] * 6)
        phase_num = 1
        kila i kwenye range(7):
            sem.release()
        wakati len(results1) + len(results2) < 13:
            _wait()
        self.assertEqual(sorted(results1 + results2), [0] * 6 + [1] * 7)
        phase_num = 2
        kila i kwenye range(6):
            sem.release()
        wakati len(results1) + len(results2) < 19:
            _wait()
        self.assertEqual(sorted(results1 + results2), [0] * 6 + [1] * 7 + [2] * 6)
        # The semaphore ni still locked
        self.assertUongo(sem.acquire(Uongo))
        # Final release, to let the last thread finish
        sem.release()
        b.wait_for_finished()
        self.assertEqual(sem_results, [Kweli] * (6 + 7 + 6 + 1))

    eleza test_try_acquire(self):
        sem = self.semtype(2)
        self.assertKweli(sem.acquire(Uongo))
        self.assertKweli(sem.acquire(Uongo))
        self.assertUongo(sem.acquire(Uongo))
        sem.release()
        self.assertKweli(sem.acquire(Uongo))

    eleza test_try_acquire_contended(self):
        sem = self.semtype(4)
        sem.acquire()
        results = []
        eleza f():
            results.append(sem.acquire(Uongo))
            results.append(sem.acquire(Uongo))
        Bunch(f, 5).wait_for_finished()
        # There can be a thread switch between acquiring the semaphore na
        # appending the result, therefore results will sio necessarily be
        # ordered.
        self.assertEqual(sorted(results), [Uongo] * 7 + [Kweli] *  3 )

    eleza test_acquire_timeout(self):
        sem = self.semtype(2)
        self.assertRaises(ValueError, sem.acquire, Uongo, timeout=1.0)
        self.assertKweli(sem.acquire(timeout=0.005))
        self.assertKweli(sem.acquire(timeout=0.005))
        self.assertUongo(sem.acquire(timeout=0.005))
        sem.release()
        self.assertKweli(sem.acquire(timeout=0.005))
        t = time.monotonic()
        self.assertUongo(sem.acquire(timeout=0.5))
        dt = time.monotonic() - t
        self.assertTimeout(dt, 0.5)

    eleza test_default_value(self):
        # The default initial value ni 1.
        sem = self.semtype()
        sem.acquire()
        eleza f():
            sem.acquire()
            sem.release()
        b = Bunch(f, 1)
        b.wait_for_started()
        _wait()
        self.assertUongo(b.finished)
        sem.release()
        b.wait_for_finished()

    eleza test_with(self):
        sem = self.semtype(2)
        eleza _with(err=Tupu):
            ukijumuisha sem:
                self.assertKweli(sem.acquire(Uongo))
                sem.release()
                ukijumuisha sem:
                    self.assertUongo(sem.acquire(Uongo))
                    ikiwa err:
                        ashiria err
        _with()
        self.assertKweli(sem.acquire(Uongo))
        sem.release()
        self.assertRaises(TypeError, _with, TypeError)
        self.assertKweli(sem.acquire(Uongo))
        sem.release()

kundi SemaphoreTests(BaseSemaphoreTests):
    """
    Tests kila unbounded semaphores.
    """

    eleza test_release_unacquired(self):
        # Unbounded releases are allowed na increment the semaphore's value
        sem = self.semtype(1)
        sem.release()
        sem.acquire()
        sem.acquire()
        sem.release()


kundi BoundedSemaphoreTests(BaseSemaphoreTests):
    """
    Tests kila bounded semaphores.
    """

    eleza test_release_unacquired(self):
        # Cannot go past the initial value
        sem = self.semtype()
        self.assertRaises(ValueError, sem.release)
        sem.acquire()
        sem.release()
        self.assertRaises(ValueError, sem.release)


kundi BarrierTests(BaseTestCase):
    """
    Tests kila Barrier objects.
    """
    N = 5
    defaultTimeout = 2.0

    eleza setUp(self):
        self.barrier = self.barriertype(self.N, timeout=self.defaultTimeout)
    eleza tearDown(self):
        self.barrier.abort()

    eleza run_threads(self, f):
        b = Bunch(f, self.N-1)
        f()
        b.wait_for_finished()

    eleza multipita(self, results, n):
        m = self.barrier.parties
        self.assertEqual(m, self.N)
        kila i kwenye range(n):
            results[0].append(Kweli)
            self.assertEqual(len(results[1]), i * m)
            self.barrier.wait()
            results[1].append(Kweli)
            self.assertEqual(len(results[0]), (i + 1) * m)
            self.barrier.wait()
        self.assertEqual(self.barrier.n_waiting, 0)
        self.assertUongo(self.barrier.broken)

    eleza test_barrier(self, pitaes=1):
        """
        Test that a barrier ni pitaed kwenye lockstep
        """
        results = [[],[]]
        eleza f():
            self.multipita(results, pitaes)
        self.run_threads(f)

    eleza test_barrier_10(self):
        """
        Test that a barrier works kila 10 consecutive runs
        """
        rudisha self.test_barrier(10)

    eleza test_wait_return(self):
        """
        test the rudisha value kutoka barrier.wait
        """
        results = []
        eleza f():
            r = self.barrier.wait()
            results.append(r)

        self.run_threads(f)
        self.assertEqual(sum(results), sum(range(self.N)))

    eleza test_action(self):
        """
        Test the 'action' callback
        """
        results = []
        eleza action():
            results.append(Kweli)
        barrier = self.barriertype(self.N, action)
        eleza f():
            barrier.wait()
            self.assertEqual(len(results), 1)

        self.run_threads(f)

    eleza test_abort(self):
        """
        Test that an abort will put the barrier kwenye a broken state
        """
        results1 = []
        results2 = []
        eleza f():
            jaribu:
                i = self.barrier.wait()
                ikiwa i == self.N//2:
                    ashiria RuntimeError
                self.barrier.wait()
                results1.append(Kweli)
            tatizo threading.BrokenBarrierError:
                results2.append(Kweli)
            tatizo RuntimeError:
                self.barrier.abort()
                pita

        self.run_threads(f)
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertKweli(self.barrier.broken)

    eleza test_reset(self):
        """
        Test that a 'reset' on a barrier frees the waiting threads
        """
        results1 = []
        results2 = []
        results3 = []
        eleza f():
            i = self.barrier.wait()
            ikiwa i == self.N//2:
                # Wait until the other threads are all kwenye the barrier.
                wakati self.barrier.n_waiting < self.N-1:
                    time.sleep(0.001)
                self.barrier.reset()
            isipokua:
                jaribu:
                    self.barrier.wait()
                    results1.append(Kweli)
                tatizo threading.BrokenBarrierError:
                    results2.append(Kweli)
            # Now, pita the barrier again
            self.barrier.wait()
            results3.append(Kweli)

        self.run_threads(f)
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertEqual(len(results3), self.N)


    eleza test_abort_and_reset(self):
        """
        Test that a barrier can be reset after being broken.
        """
        results1 = []
        results2 = []
        results3 = []
        barrier2 = self.barriertype(self.N)
        eleza f():
            jaribu:
                i = self.barrier.wait()
                ikiwa i == self.N//2:
                    ashiria RuntimeError
                self.barrier.wait()
                results1.append(Kweli)
            tatizo threading.BrokenBarrierError:
                results2.append(Kweli)
            tatizo RuntimeError:
                self.barrier.abort()
                pita
            # Synchronize na reset the barrier.  Must synchronize first so
            # that everyone has left it when we reset, na after so that no
            # one enters it before the reset.
            ikiwa barrier2.wait() == self.N//2:
                self.barrier.reset()
            barrier2.wait()
            self.barrier.wait()
            results3.append(Kweli)

        self.run_threads(f)
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertEqual(len(results3), self.N)

    eleza test_timeout(self):
        """
        Test wait(timeout)
        """
        eleza f():
            i = self.barrier.wait()
            ikiwa i == self.N // 2:
                # One thread ni late!
                time.sleep(1.0)
            # Default timeout ni 2.0, so this ni shorter.
            self.assertRaises(threading.BrokenBarrierError,
                              self.barrier.wait, 0.5)
        self.run_threads(f)

    eleza test_default_timeout(self):
        """
        Test the barrier's default timeout
        """
        # create a barrier ukijumuisha a low default timeout
        barrier = self.barriertype(self.N, timeout=0.3)
        eleza f():
            i = barrier.wait()
            ikiwa i == self.N // 2:
                # One thread ni later than the default timeout of 0.3s.
                time.sleep(1.0)
            self.assertRaises(threading.BrokenBarrierError, barrier.wait)
        self.run_threads(f)

    eleza test_single_thread(self):
        b = self.barriertype(1)
        b.wait()
        b.wait()
