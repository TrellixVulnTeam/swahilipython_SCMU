kutoka . agiza util as test_util

init = test_util.import_importlib('importlib')

agiza sys
agiza threading
agiza weakref

kutoka test agiza support
kutoka test agiza lock_tests


kundi ModuleLockAsRLockTests:
    locktype = classmethod(lambda cls: cls.LockType("some_lock"))

    # _is_owned() unsupported
    test__is_owned = None
    # acquire(blocking=False) unsupported
    test_try_acquire = None
    test_try_acquire_contended = None
    # `with` unsupported
    test_with = None
    # acquire(timeout=...) unsupported
    test_timeout = None
    # _release_save() unsupported
    test_release_save_unacquired = None
    # lock status in repr unsupported
    test_repr = None
    test_locked_repr = None

LOCK_TYPES = {kind: splitinit._bootstrap._ModuleLock
              for kind, splitinit in init.items()}

(Frozen_ModuleLockAsRLockTests,
 Source_ModuleLockAsRLockTests
 ) = test_util.test_both(ModuleLockAsRLockTests, lock_tests.RLockTests,
                         LockType=LOCK_TYPES)


kundi DeadlockAvoidanceTests:

    eleza setUp(self):
        try:
            self.old_switchinterval = sys.getswitchinterval()
            support.setswitchinterval(0.000001)
        except AttributeError:
            self.old_switchinterval = None

    eleza tearDown(self):
        ikiwa self.old_switchinterval is not None:
            sys.setswitchinterval(self.old_switchinterval)

    eleza run_deadlock_avoidance_test(self, create_deadlock):
        NLOCKS = 10
        locks = [self.LockType(str(i)) for i in range(NLOCKS)]
        pairs = [(locks[i], locks[(i+1)%NLOCKS]) for i in range(NLOCKS)]
        ikiwa create_deadlock:
            NTHREADS = NLOCKS
        else:
            NTHREADS = NLOCKS - 1
        barrier = threading.Barrier(NTHREADS)
        results = []

        eleza _acquire(lock):
            """Try to acquire the lock. Return True on success,
            False on deadlock."""
            try:
                lock.acquire()
            except self.DeadlockError:
                rudisha False
            else:
                rudisha True

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
        results = self.run_deadlock_avoidance_test(True)
        # At least one of the threads detected a potential deadlock on its
        # second acquire() call.  It may be several of them, because the
        # deadlock avoidance mechanism is conservative.
        nb_deadlocks = results.count((True, False))
        self.assertGreaterEqual(nb_deadlocks, 1)
        self.assertEqual(results.count((True, True)), len(results) - nb_deadlocks)

    eleza test_no_deadlock(self):
        results = self.run_deadlock_avoidance_test(False)
        self.assertEqual(results.count((True, False)), 0)
        self.assertEqual(results.count((True, True)), len(results))


DEADLOCK_ERRORS = {kind: splitinit._bootstrap._DeadlockError
                   for kind, splitinit in init.items()}

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
        del lock
        support.gc_collect()
        self.assertNotIn(name, self.bootstrap._module_locks)
        self.assertIsNone(wr())

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
