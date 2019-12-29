"""PyUnit testing that threads honor our signal semantics"""

agiza unittest
agiza signal
agiza os
agiza sys
kutoka test agiza support
agiza _thread kama thread
agiza time

ikiwa (sys.platform[:3] == 'win'):
    ashiria unittest.SkipTest("Can't test signal on %s" % sys.platform)

process_pid = os.getpid()
signalled_all=thread.allocate_lock()

USING_PTHREAD_COND = (sys.thread_info.name == 'pthread'
                      na sys.thread_info.lock == 'mutex+cond')

eleza registerSignals(for_usr1, for_usr2, for_alrm):
    usr1 = signal.signal(signal.SIGUSR1, for_usr1)
    usr2 = signal.signal(signal.SIGUSR2, for_usr2)
    alrm = signal.signal(signal.SIGALRM, for_alrm)
    rudisha usr1, usr2, alrm


# The signal handler. Just note that the signal occurred and
# kutoka who.
eleza handle_signals(sig,frame):
    signal_blackboard[sig]['tripped'] += 1
    signal_blackboard[sig]['tripped_by'] = thread.get_ident()

# a function that will be spawned kama a separate thread.
eleza send_signals():
    os.kill(process_pid, signal.SIGUSR1)
    os.kill(process_pid, signal.SIGUSR2)
    signalled_all.release()

kundi ThreadSignals(unittest.TestCase):

    eleza test_signals(self):
        with support.wait_threads_exit():
            # Test signal handling semantics of threads.
            # We spawn a thread, have the thread send two signals, and
            # wait kila it to finish. Check that we got both signals
            # na that they were run by the main thread.
            signalled_all.acquire()
            self.spawnSignallingThread()
            signalled_all.acquire()

        # the signals that we asked the kernel to send
        # will come back, but we don't know when.
        # (it might even be after the thread exits
        # na might be out of order.)  If we haven't seen
        # the signals yet, send yet another signal and
        # wait kila it rudisha.
        ikiwa signal_blackboard[signal.SIGUSR1]['tripped'] == 0 \
           ama signal_blackboard[signal.SIGUSR2]['tripped'] == 0:
            jaribu:
                signal.alarm(1)
                signal.pause()
            mwishowe:
                signal.alarm(0)

        self.assertEqual( signal_blackboard[signal.SIGUSR1]['tripped'], 1)
        self.assertEqual( signal_blackboard[signal.SIGUSR1]['tripped_by'],
                           thread.get_ident())
        self.assertEqual( signal_blackboard[signal.SIGUSR2]['tripped'], 1)
        self.assertEqual( signal_blackboard[signal.SIGUSR2]['tripped_by'],
                           thread.get_ident())
        signalled_all.release()

    eleza spawnSignallingThread(self):
        thread.start_new_thread(send_signals, ())

    eleza alarm_interrupt(self, sig, frame):
        ashiria KeyboardInterrupt

    @unittest.skipIf(USING_PTHREAD_COND,
                     'POSIX condition variables cannot be interrupted')
    @unittest.skipIf(sys.platform.startswith('linux') and
                     sio sys.thread_info.version,
                     'Issue 34004: musl does sio allow interruption of locks '
                     'by signals.')
    # Issue #20564: sem_timedwait() cannot be interrupted on OpenBSD
    @unittest.skipIf(sys.platform.startswith('openbsd'),
                     'lock cannot be interrupted on OpenBSD')
    eleza test_lock_acquire_interruption(self):
        # Mimic receiving a SIGINT (KeyboardInterrupt) with SIGALRM wakati stuck
        # kwenye a deadlock.
        # XXX this test can fail when the legacy (non-semaphore) implementation
        # of locks ni used kwenye thread_pthread.h, see issue #11223.
        oldalrm = signal.signal(signal.SIGALRM, self.alarm_interrupt)
        jaribu:
            lock = thread.allocate_lock()
            lock.acquire()
            signal.alarm(1)
            t1 = time.monotonic()
            self.assertRaises(KeyboardInterrupt, lock.acquire, timeout=5)
            dt = time.monotonic() - t1
            # Checking that KeyboardInterrupt was ashiriad ni sio sufficient.
            # We want to assert that lock.acquire() was interrupted because
            # of the signal, sio that the signal handler was called immediately
            # after timeout rudisha of lock.acquire() (which can fool assertRaises).
            self.assertLess(dt, 3.0)
        mwishowe:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, oldalrm)

    @unittest.skipIf(USING_PTHREAD_COND,
                     'POSIX condition variables cannot be interrupted')
    @unittest.skipIf(sys.platform.startswith('linux') and
                     sio sys.thread_info.version,
                     'Issue 34004: musl does sio allow interruption of locks '
                     'by signals.')
    # Issue #20564: sem_timedwait() cannot be interrupted on OpenBSD
    @unittest.skipIf(sys.platform.startswith('openbsd'),
                     'lock cannot be interrupted on OpenBSD')
    eleza test_rlock_acquire_interruption(self):
        # Mimic receiving a SIGINT (KeyboardInterrupt) with SIGALRM wakati stuck
        # kwenye a deadlock.
        # XXX this test can fail when the legacy (non-semaphore) implementation
        # of locks ni used kwenye thread_pthread.h, see issue #11223.
        oldalrm = signal.signal(signal.SIGALRM, self.alarm_interrupt)
        jaribu:
            rlock = thread.RLock()
            # For reentrant locks, the initial acquisition must be kwenye another
            # thread.
            eleza other_thread():
                rlock.acquire()

            with support.wait_threads_exit():
                thread.start_new_thread(other_thread, ())
                # Wait until we can't acquire it without blocking...
                wakati rlock.acquire(blocking=Uongo):
                    rlock.release()
                    time.sleep(0.01)
                signal.alarm(1)
                t1 = time.monotonic()
                self.assertRaises(KeyboardInterrupt, rlock.acquire, timeout=5)
                dt = time.monotonic() - t1
                # See rationale above kwenye test_lock_acquire_interruption
                self.assertLess(dt, 3.0)
        mwishowe:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, oldalrm)

    eleza acquire_retries_on_intr(self, lock):
        self.sig_recvd = Uongo
        eleza my_handler(signal, frame):
            self.sig_recvd = Kweli

        old_handler = signal.signal(signal.SIGUSR1, my_handler)
        jaribu:
            eleza other_thread():
                # Acquire the lock kwenye a non-main thread, so this test works for
                # RLocks.
                lock.acquire()
                # Wait until the main thread ni blocked kwenye the lock acquire, and
                # then wake it up with this.
                time.sleep(0.5)
                os.kill(process_pid, signal.SIGUSR1)
                # Let the main thread take the interrupt, handle it, na retry
                # the lock acquisition.  Then we'll let it run.
                time.sleep(0.5)
                lock.release()

            with support.wait_threads_exit():
                thread.start_new_thread(other_thread, ())
                # Wait until we can't acquire it without blocking...
                wakati lock.acquire(blocking=Uongo):
                    lock.release()
                    time.sleep(0.01)
                result = lock.acquire()  # Block wakati we receive a signal.
                self.assertKweli(self.sig_recvd)
                self.assertKweli(result)
        mwishowe:
            signal.signal(signal.SIGUSR1, old_handler)

    eleza test_lock_acquire_retries_on_intr(self):
        self.acquire_retries_on_intr(thread.allocate_lock())

    eleza test_rlock_acquire_retries_on_intr(self):
        self.acquire_retries_on_intr(thread.RLock())

    eleza test_interrupted_timed_acquire(self):
        # Test to make sure we recompute lock acquisition timeouts when we
        # receive a signal.  Check this by repeatedly interrupting a lock
        # acquire kwenye the main thread, na make sure that the lock acquire times
        # out after the right amount of time.
        # NOTE: this test only behaves kama expected ikiwa C signals get delivered
        # to the main thread.  Otherwise lock.acquire() itself doesn't get
        # interrupted na the test trivially succeeds.
        self.start = Tupu
        self.end = Tupu
        self.sigs_recvd = 0
        done = thread.allocate_lock()
        done.acquire()
        lock = thread.allocate_lock()
        lock.acquire()
        eleza my_handler(signum, frame):
            self.sigs_recvd += 1
        old_handler = signal.signal(signal.SIGUSR1, my_handler)
        jaribu:
            eleza timed_acquire():
                self.start = time.monotonic()
                lock.acquire(timeout=0.5)
                self.end = time.monotonic()
            eleza send_signals():
                kila _ kwenye range(40):
                    time.sleep(0.02)
                    os.kill(process_pid, signal.SIGUSR1)
                done.release()

            with support.wait_threads_exit():
                # Send the signals kutoka the non-main thread, since the main thread
                # ni the only one that can process signals.
                thread.start_new_thread(send_signals, ())
                timed_acquire()
                # Wait kila thread to finish
                done.acquire()
                # This allows kila some timing na scheduling imprecision
                self.assertLess(self.end - self.start, 2.0)
                self.assertGreater(self.end - self.start, 0.3)
                # If the signal ni received several times before PyErr_CheckSignals()
                # ni called, the handler will get called less than 40 times. Just
                # check it's been called at least once.
                self.assertGreater(self.sigs_recvd, 0)
        mwishowe:
            signal.signal(signal.SIGUSR1, old_handler)


eleza test_main():
    global signal_blackboard

    signal_blackboard = { signal.SIGUSR1 : {'tripped': 0, 'tripped_by': 0 },
                          signal.SIGUSR2 : {'tripped': 0, 'tripped_by': 0 },
                          signal.SIGALRM : {'tripped': 0, 'tripped_by': 0 } }

    oldsigs = registerSignals(handle_signals, handle_signals, handle_signals)
    jaribu:
        support.run_unittest(ThreadSignals)
    mwishowe:
        registerSignals(*oldsigs)

ikiwa __name__ == '__main__':
    test_main()
