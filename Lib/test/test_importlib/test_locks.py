kutoka . agiza util kama test_util

init = test_util.import_importlib('importlib')

agiza sys
agiza threading
agiza weakref

kutoka test agiza support
kutoka test agiza lock_tests


kundi ModuleLockAsRLockTests:
    locktype = classmethod(lambda cls: cls.LockType("some_lock"))

    # _is_owned() unsupported
    test__is_owned = Tupu
    # acquire(blocking=Uongo) unsupported
    test_try_acquire = Tupu
    test_try_acquire_contended = Tupu
    # `with` unsupported
    test_ukijumuisha = Tupu
    # acquire(timeout=...) unsupported
    test_timeout = Tupu
    # _release_save() unsupported
    test_release_save_unacquired = Tupu
    # lock status kwenye repr unsupported
    test_repr = Tupu
    test_locked_repr = Tupu

LOCK_TYPES = {kind: splitinit._bootstrap._ModuleLock
              kila kind, splitinit kwenye init.items()}

(Frozen_ModuleLockAsRLockTests,
 Source_ModuleLockAsRLockTests
 ) = test_util.test_both(ModuleLockAsRLockTests, lock_tests.RLockTests,
                         LockType=LOCK_TYPES)


kundi DeadlockAvoidanceTests:

    eleza setUp(self):
        jaribu:
            self.old_switchinterval = sys.getswitchinterval()
            support.setswitchinterval(0.000001)
        tatizo AttributeError:
            self.old_switchinterval = Tupu

    eleza tearDown(self):
        ikiwa self.old_switchinterval ni sio Tupu:
            sys.setswitchinterval(self.old_switchinterval)

    eleza run_deadlock_avoidance_test(self, create_deadlock):
        NLOCKS = 10
        locks = [self.LockType(str(i)) kila i kwenye range(NLOCKS)]
        pairs = [(locks[i], locks[(i+1)%NLOCKS]) kila i kwenye range(NLOCKS)]
        ikiwa create_deadlock:
            NTHREADS = NLOCKS
        isipokua:
            NTHREADS = NLOCKS - 1
        barrier = threading.Barrier(NTHREADS)
        results = []

        eleza _acquire(lock):
            """Try to acquire the lock. Return Kweli on success,
            Uongo on deadlock."""
            jaribu:
                lock.acquire()
            tatizo self.DeadlockError:
                rudisha Uongo
            isipokua:
                rudisha Kweli

        eleza f():
            a, b = pairs.pop()
            ra = _acquire(a)
            barrier.wait()
            rb = _acquire(b)
            results.append((ra, rb))
            ikiwa rb:
                b.release()
            ikiwa ra:
                a.release()
        lock_tests.Bunch(f, NTHREADS).wait_for_finished()
        self.assertEqual(len(results), NTHREADS)
        rudisha results

    eleza test_deadlock(self):
        results = self.run_deadlock_avoidance_test(Kweli)
        # At least one of the threads detected a potential deadlock on its
        # second acquire() call.  It may be several of them, because the
        # deadlock avoidance mechanism ni conservative.
        nb_deadlocks = results.count((Kweli, Uongo))
        self.assertGreaterEqual(nb_deadlocks, 1)
        self.assertEqual(results.count((Kweli, Kweli)), len(results) - nb_deadlocks)

    eleza test_no_deadlock(self):
        results = self.run_deadlock_avoidance_test(Uongo)
        self.assertEqual(results.count((Kweli, Uongo)), 0)
        self.assertEqual(results.count((Kweli, Kweli)), len(results))


DEADLOCK_ERRORS = {kind: splitinit._bootstrap._DeadlockError
                   kila kind, splitinit kwenye init.items()}

(Frozen_DeadlockAvoidanceTests,
 Source_DeadlockAvoidanceTests
 ) = test_util.test_both(DeadlockAvoidanceTests,
                         LockType=LOCK_TYPES,
                         DeadlockError=DEADLOCK_ERRORS)


kundi LifetimeTests:

    @property
    eleza bootstrap(self):
        rudisha self.init._bootstrap

    eleza test_lock_lifetime(self):
        name = "xyzzy"
        self.assertNotIn(name, self.bootstrap._module_locks)
        lock = self.bootstrap._get_module_lock(name)
        self.assertIn(name, self.bootstrap._module_locks)
        wr = weakref.ref(lock)
        toa lock
        support.gc_collect()
        self.assertNotIn(name, self.bootstrap._module_locks)
        self.assertIsTupu(wr())

    eleza test_all_locks(self):
        support.gc_collect()
        self.assertEqual(0, len(self.bootstrap._module_locks),
                         self.bootstrap._module_locks)


(Frozen_LifetimeTests,
 Source_LifetimeTests
 ) = test_util.test_both(LifetimeTests, init=init)


@support.reap_threads
eleza test_main():
    support.run_unittest(Frozen_ModuleLockAsRLockTests,
                         Source_ModuleLockAsRLockTests,
                         Frozen_DeadlockAvoidanceTests,
                         Source_DeadlockAvoidanceTests,
                         Frozen_LifetimeTests,
                         Source_LifetimeTests)


ikiwa __name__ == '__main__':
    test_main()
