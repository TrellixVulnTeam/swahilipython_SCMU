"""
Tests kila the threading module.
"""

agiza test.support
kutoka test.support agiza (verbose, import_module, cpython_only,
                          requires_type_collecting)
kutoka test.support.script_helper agiza assert_python_ok, assert_python_failure

agiza random
agiza sys
agiza _thread
agiza threading
agiza time
agiza unittest
agiza weakref
agiza os
agiza subprocess
agiza signal

kutoka test agiza lock_tests
kutoka test agiza support


# Between fork() na exec(), only async-safe functions are allowed (issues
# #12316 na #11870), na fork() kutoka a worker thread ni known to trigger
# problems ukijumuisha some operating systems (issue #3863): skip problematic tests
# on platforms known to behave badly.
platforms_to_skip = ('netbsd5', 'hp-ux11')


# A trivial mutable counter.
kundi Counter(object):
    eleza __init__(self):
        self.value = 0
    eleza inc(self):
        self.value += 1
    eleza dec(self):
        self.value -= 1
    eleza get(self):
        rudisha self.value

kundi TestThread(threading.Thread):
    eleza __init__(self, name, testcase, sema, mutex, nrunning):
        threading.Thread.__init__(self, name=name)
        self.testcase = testcase
        self.sema = sema
        self.mutex = mutex
        self.nrunning = nrunning

    eleza run(self):
        delay = random.random() / 10000.0
        ikiwa verbose:
            andika('task %s will run kila %.1f usec' %
                  (self.name, delay * 1e6))

        ukijumuisha self.sema:
            ukijumuisha self.mutex:
                self.nrunning.inc()
                ikiwa verbose:
                    andika(self.nrunning.get(), 'tasks are running')
                self.testcase.assertLessEqual(self.nrunning.get(), 3)

            time.sleep(delay)
            ikiwa verbose:
                andika('task', self.name, 'done')

            ukijumuisha self.mutex:
                self.nrunning.dec()
                self.testcase.assertGreaterEqual(self.nrunning.get(), 0)
                ikiwa verbose:
                    andika('%s ni finished. %d tasks are running' %
                          (self.name, self.nrunning.get()))


kundi BaseTestCase(unittest.TestCase):
    eleza setUp(self):
        self._threads = test.support.threading_setup()

    eleza tearDown(self):
        test.support.threading_cleanup(*self._threads)
        test.support.reap_children()


kundi ThreadTests(BaseTestCase):

    # Create a bunch of threads, let each do some work, wait until all are
    # done.
    eleza test_various_ops(self):
        # This takes about n/3 seconds to run (about n/3 clumps of tasks,
        # times about 1 second per clump).
        NUMTASKS = 10

        # no more than 3 of the 10 can run at once
        sema = threading.BoundedSemaphore(value=3)
        mutex = threading.RLock()
        numrunning = Counter()

        threads = []

        kila i kwenye range(NUMTASKS):
            t = TestThread("<thread %d>"%i, self, sema, mutex, numrunning)
            threads.append(t)
            self.assertIsTupu(t.ident)
            self.assertRegex(repr(t), r'^<TestThread\(.*, initial\)>$')
            t.start()

        ikiwa hasattr(threading, 'get_native_id'):
            native_ids = set(t.native_id kila t kwenye threads) | {threading.get_native_id()}
            self.assertNotIn(Tupu, native_ids)
            self.assertEqual(len(native_ids), NUMTASKS + 1)

        ikiwa verbose:
            andika('waiting kila all tasks to complete')
        kila t kwenye threads:
            t.join()
            self.assertUongo(t.is_alive())
            self.assertNotEqual(t.ident, 0)
            self.assertIsNotTupu(t.ident)
            self.assertRegex(repr(t), r'^<TestThread\(.*, stopped -?\d+\)>$')
        ikiwa verbose:
            andika('all tasks done')
        self.assertEqual(numrunning.get(), 0)

    eleza test_ident_of_no_threading_threads(self):
        # The ident still must work kila the main thread na dummy threads.
        self.assertIsNotTupu(threading.currentThread().ident)
        eleza f():
            ident.append(threading.currentThread().ident)
            done.set()
        done = threading.Event()
        ident = []
        ukijumuisha support.wait_threads_exit():
            tid = _thread.start_new_thread(f, ())
            done.wait()
            self.assertEqual(ident[0], tid)
        # Kill the "immortal" _DummyThread
        toa threading._active[ident[0]]

    # run ukijumuisha a small(ish) thread stack size (256 KiB)
    eleza test_various_ops_small_stack(self):
        ikiwa verbose:
            andika('ukijumuisha 256 KiB thread stack size...')
        jaribu:
            threading.stack_size(262144)
        tatizo _thread.error:
            ashiria unittest.SkipTest(
                'platform does sio support changing thread stack size')
        self.test_various_ops()
        threading.stack_size(0)

    # run ukijumuisha a large thread stack size (1 MiB)
    eleza test_various_ops_large_stack(self):
        ikiwa verbose:
            andika('ukijumuisha 1 MiB thread stack size...')
        jaribu:
            threading.stack_size(0x100000)
        tatizo _thread.error:
            ashiria unittest.SkipTest(
                'platform does sio support changing thread stack size')
        self.test_various_ops()
        threading.stack_size(0)

    eleza test_foreign_thread(self):
        # Check that a "foreign" thread can use the threading module.
        eleza f(mutex):
            # Calling current_thread() forces an entry kila the foreign
            # thread to get made kwenye the threading._active map.
            threading.current_thread()
            mutex.release()

        mutex = threading.Lock()
        mutex.acquire()
        ukijumuisha support.wait_threads_exit():
            tid = _thread.start_new_thread(f, (mutex,))
            # Wait kila the thread to finish.
            mutex.acquire()
        self.assertIn(tid, threading._active)
        self.assertIsInstance(threading._active[tid], threading._DummyThread)
        #Issue 29376
        self.assertKweli(threading._active[tid].is_alive())
        self.assertRegex(repr(threading._active[tid]), '_DummyThread')
        toa threading._active[tid]

    # PyThreadState_SetAsyncExc() ni a CPython-only gimmick, sio (currently)
    # exposed at the Python level.  This test relies on ctypes to get at it.
    eleza test_PyThreadState_SetAsyncExc(self):
        ctypes = import_module("ctypes")

        set_async_exc = ctypes.pythonapi.PyThreadState_SetAsyncExc
        set_async_exc.argtypes = (ctypes.c_ulong, ctypes.py_object)

        kundi AsyncExc(Exception):
            pita

        exception = ctypes.py_object(AsyncExc)

        # First check it works when setting the exception kutoka the same thread.
        tid = threading.get_ident()
        self.assertIsInstance(tid, int)
        self.assertGreater(tid, 0)

        jaribu:
            result = set_async_exc(tid, exception)
            # The exception ni async, so we might have to keep the VM busy until
            # it notices.
            wakati Kweli:
                pita
        tatizo AsyncExc:
            pita
        isipokua:
            # This code ni unreachable but it reflects the intent. If we wanted
            # to be smarter the above loop wouldn't be infinite.
            self.fail("AsyncExc sio raised")
        jaribu:
            self.assertEqual(result, 1) # one thread state modified
        tatizo UnboundLocalError:
            # The exception was raised too quickly kila us to get the result.
            pita

        # `worker_started` ni set by the thread when it's inside a try/except
        # block waiting to catch the asynchronously set AsyncExc exception.
        # `worker_saw_exception` ni set by the thread upon catching that
        # exception.
        worker_started = threading.Event()
        worker_saw_exception = threading.Event()

        kundi Worker(threading.Thread):
            eleza run(self):
                self.id = threading.get_ident()
                self.finished = Uongo

                jaribu:
                    wakati Kweli:
                        worker_started.set()
                        time.sleep(0.1)
                tatizo AsyncExc:
                    self.finished = Kweli
                    worker_saw_exception.set()

        t = Worker()
        t.daemon = Kweli # so ikiwa this fails, we don't hang Python at shutdown
        t.start()
        ikiwa verbose:
            andika("    started worker thread")

        # Try a thread id that doesn't make sense.
        ikiwa verbose:
            andika("    trying nonsensical thread id")
        result = set_async_exc(-1, exception)
        self.assertEqual(result, 0)  # no thread states modified

        # Now ashiria an exception kwenye the worker thread.
        ikiwa verbose:
            andika("    waiting kila worker thread to get started")
        ret = worker_started.wait()
        self.assertKweli(ret)
        ikiwa verbose:
            andika("    verifying worker hasn't exited")
        self.assertUongo(t.finished)
        ikiwa verbose:
            andika("    attempting to ashiria asynch exception kwenye worker")
        result = set_async_exc(t.id, exception)
        self.assertEqual(result, 1) # one thread state modified
        ikiwa verbose:
            andika("    waiting kila worker to say it caught the exception")
        worker_saw_exception.wait(timeout=10)
        self.assertKweli(t.finished)
        ikiwa verbose:
            andika("    all OK -- joining worker")
        ikiwa t.finished:
            t.join()
        # isipokua the thread ni still running, na we have no way to kill it

    eleza test_limbo_cleanup(self):
        # Issue 7481: Failure to start thread should cleanup the limbo map.
        eleza fail_new_thread(*args):
            ashiria threading.ThreadError()
        _start_new_thread = threading._start_new_thread
        threading._start_new_thread = fail_new_thread
        jaribu:
            t = threading.Thread(target=lambda: Tupu)
            self.assertRaises(threading.ThreadError, t.start)
            self.assertUongo(
                t kwenye threading._limbo,
                "Failed to cleanup _limbo map on failure of Thread.start().")
        mwishowe:
            threading._start_new_thread = _start_new_thread

    eleza test_finalize_runnning_thread(self):
        # Issue 1402: the PyGILState_Ensure / _Release functions may be called
        # very late on python exit: on deallocation of a running thread for
        # example.
        import_module("ctypes")

        rc, out, err = assert_python_failure("-c", """ikiwa 1:
            agiza ctypes, sys, time, _thread

            # This lock ni used kama a simple event variable.
            ready = _thread.allocate_lock()
            ready.acquire()

            # Module globals are cleared before __del__ ni run
            # So we save the functions kwenye kundi dict
            kundi C:
                ensure = ctypes.pythonapi.PyGILState_Ensure
                release = ctypes.pythonapi.PyGILState_Release
                eleza __del__(self):
                    state = self.ensure()
                    self.release(state)

            eleza waitingThread():
                x = C()
                ready.release()
                time.sleep(100)

            _thread.start_new_thread(waitingThread, ())
            ready.acquire()  # Be sure the other thread ni waiting.
            sys.exit(42)
            """)
        self.assertEqual(rc, 42)

    eleza test_finalize_with_trace(self):
        # Issue1733757
        # Avoid a deadlock when sys.settrace steps into threading._shutdown
        assert_python_ok("-c", """ikiwa 1:
            agiza sys, threading

            # A deadlock-killer, to prevent the
            # testsuite to hang forever
            eleza killer():
                agiza os, time
                time.sleep(2)
                andika('program blocked; aborting')
                os._exit(2)
            t = threading.Thread(target=killer)
            t.daemon = Kweli
            t.start()

            # This ni the trace function
            eleza func(frame, event, arg):
                threading.current_thread()
                rudisha func

            sys.settrace(func)
            """)

    eleza test_join_nondaemon_on_shutdown(self):
        # Issue 1722344
        # Raising SystemExit skipped threading._shutdown
        rc, out, err = assert_python_ok("-c", """ikiwa 1:
                agiza threading
                kutoka time agiza sleep

                eleza child():
                    sleep(1)
                    # As a non-daemon thread we SHOULD wake up na nothing
                    # should be torn down yet
                    andika("Woke up, sleep function is:", sleep)

                threading.Thread(target=child).start()
                ashiria SystemExit
            """)
        self.assertEqual(out.strip(),
            b"Woke up, sleep function is: <built-in function sleep>")
        self.assertEqual(err, b"")

    eleza test_enumerate_after_join(self):
        # Try hard to trigger #1703448: a thread ni still returned in
        # threading.enumerate() after it has been join()ed.
        enum = threading.enumerate
        old_interval = sys.getswitchinterval()
        jaribu:
            kila i kwenye range(1, 100):
                sys.setswitchinterval(i * 0.0002)
                t = threading.Thread(target=lambda: Tupu)
                t.start()
                t.join()
                l = enum()
                self.assertNotIn(t, l,
                    "#1703448 triggered after %d trials: %s" % (i, l))
        mwishowe:
            sys.setswitchinterval(old_interval)

    eleza test_no_refcycle_through_target(self):
        kundi RunSelfFunction(object):
            eleza __init__(self, should_raise):
                # The links kwenye this refcycle kutoka Thread back to self
                # should be cleaned up when the thread completes.
                self.should_ashiria = should_raise
                self.thread = threading.Thread(target=self._run,
                                               args=(self,),
                                               kwargs={'yet_another':self})
                self.thread.start()

            eleza _run(self, other_ref, yet_another):
                ikiwa self.should_raise:
                    ashiria SystemExit

        cyclic_object = RunSelfFunction(should_raise=Uongo)
        weak_cyclic_object = weakref.ref(cyclic_object)
        cyclic_object.thread.join()
        toa cyclic_object
        self.assertIsTupu(weak_cyclic_object(),
                         msg=('%d references still around' %
                              sys.getrefcount(weak_cyclic_object())))

        raising_cyclic_object = RunSelfFunction(should_raise=Kweli)
        weak_raising_cyclic_object = weakref.ref(raising_cyclic_object)
        raising_cyclic_object.thread.join()
        toa raising_cyclic_object
        self.assertIsTupu(weak_raising_cyclic_object(),
                         msg=('%d references still around' %
                              sys.getrefcount(weak_raising_cyclic_object())))

    eleza test_old_threading_api(self):
        # Just a quick sanity check to make sure the old method names are
        # still present
        t = threading.Thread()
        t.isDaemon()
        t.setDaemon(Kweli)
        t.getName()
        t.setName("name")
        ukijumuisha self.assertWarnsRegex(DeprecationWarning, 'use is_alive()'):
            t.isAlive()
        e = threading.Event()
        e.isSet()
        threading.activeCount()

    eleza test_repr_daemon(self):
        t = threading.Thread()
        self.assertNotIn('daemon', repr(t))
        t.daemon = Kweli
        self.assertIn('daemon', repr(t))

    eleza test_daemon_param(self):
        t = threading.Thread()
        self.assertUongo(t.daemon)
        t = threading.Thread(daemon=Uongo)
        self.assertUongo(t.daemon)
        t = threading.Thread(daemon=Kweli)
        self.assertKweli(t.daemon)

    @unittest.skipUnless(hasattr(os, 'fork'), 'test needs fork()')
    eleza test_dummy_thread_after_fork(self):
        # Issue #14308: a dummy thread kwenye the active list doesn't mess up
        # the after-fork mechanism.
        code = """ikiwa 1:
            agiza _thread, threading, os, time

            eleza background_thread(evt):
                # Creates na registers the _DummyThread instance
                threading.current_thread()
                evt.set()
                time.sleep(10)

            evt = threading.Event()
            _thread.start_new_thread(background_thread, (evt,))
            evt.wait()
            assert threading.active_count() == 2, threading.active_count()
            ikiwa os.fork() == 0:
                assert threading.active_count() == 1, threading.active_count()
                os._exit(0)
            isipokua:
                os.wait()
        """
        _, out, err = assert_python_ok("-c", code)
        self.assertEqual(out, b'')
        self.assertEqual(err, b'')

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    eleza test_is_alive_after_fork(self):
        # Try hard to trigger #18418: is_alive() could sometimes be Kweli on
        # threads that vanished after a fork.
        old_interval = sys.getswitchinterval()
        self.addCleanup(sys.setswitchinterval, old_interval)

        # Make the bug more likely to manifest.
        test.support.setswitchinterval(1e-6)

        kila i kwenye range(20):
            t = threading.Thread(target=lambda: Tupu)
            t.start()
            pid = os.fork()
            ikiwa pid == 0:
                os._exit(11 ikiwa t.is_alive() isipokua 10)
            isipokua:
                t.join()

                pid, status = os.waitpid(pid, 0)
                self.assertKweli(os.WIFEXITED(status))
                self.assertEqual(10, os.WEXITSTATUS(status))

    eleza test_main_thread(self):
        main = threading.main_thread()
        self.assertEqual(main.name, 'MainThread')
        self.assertEqual(main.ident, threading.current_thread().ident)
        self.assertEqual(main.ident, threading.get_ident())

        eleza f():
            self.assertNotEqual(threading.main_thread().ident,
                                threading.current_thread().ident)
        th = threading.Thread(target=f)
        th.start()
        th.join()

    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    @unittest.skipUnless(hasattr(os, 'waitpid'), "test needs os.waitpid()")
    eleza test_main_thread_after_fork(self):
        code = """ikiwa 1:
            agiza os, threading

            pid = os.fork()
            ikiwa pid == 0:
                main = threading.main_thread()
                andika(main.name)
                andika(main.ident == threading.current_thread().ident)
                andika(main.ident == threading.get_ident())
            isipokua:
                os.waitpid(pid, 0)
        """
        _, out, err = assert_python_ok("-c", code)
        data = out.decode().replace('\r', '')
        self.assertEqual(err, b"")
        self.assertEqual(data, "MainThread\nKweli\nKweli\n")

    @unittest.skipIf(sys.platform kwenye platforms_to_skip, "due to known OS bug")
    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    @unittest.skipUnless(hasattr(os, 'waitpid'), "test needs os.waitpid()")
    eleza test_main_thread_after_fork_from_nonmain_thread(self):
        code = """ikiwa 1:
            agiza os, threading, sys

            eleza f():
                pid = os.fork()
                ikiwa pid == 0:
                    main = threading.main_thread()
                    andika(main.name)
                    andika(main.ident == threading.current_thread().ident)
                    andika(main.ident == threading.get_ident())
                    # stdout ni fully buffered because sio a tty,
                    # we have to flush before exit.
                    sys.stdout.flush()
                isipokua:
                    os.waitpid(pid, 0)

            th = threading.Thread(target=f)
            th.start()
            th.join()
        """
        _, out, err = assert_python_ok("-c", code)
        data = out.decode().replace('\r', '')
        self.assertEqual(err, b"")
        self.assertEqual(data, "Thread-1\nKweli\nKweli\n")

    @requires_type_collecting
    eleza test_main_thread_during_shutdown(self):
        # bpo-31516: current_thread() should still point to the main thread
        # at shutdown
        code = """ikiwa 1:
            agiza gc, threading

            main_thread = threading.current_thread()
            assert main_thread ni threading.main_thread()  # sanity check

            kundi RefCycle:
                eleza __init__(self):
                    self.cycle = self

                eleza __del__(self):
                    andika("GC:",
                          threading.current_thread() ni main_thread,
                          threading.main_thread() ni main_thread,
                          threading.enumerate() == [main_thread])

            RefCycle()
            gc.collect()  # sanity check
            x = RefCycle()
        """
        _, out, err = assert_python_ok("-c", code)
        data = out.decode()
        self.assertEqual(err, b"")
        self.assertEqual(data.splitlines(),
                         ["GC: Kweli Kweli Kweli"] * 2)

    eleza test_finalization_shutdown(self):
        # bpo-36402: Py_Finalize() calls threading._shutdown() which must wait
        # until Python thread states of all non-daemon threads get deleted.
        #
        # Test similar to SubinterpThreadingTests.test_threads_join_2(), but
        # test the finalization of the main interpreter.
        code = """ikiwa 1:
            agiza os
            agiza threading
            agiza time
            agiza random

            eleza random_sleep():
                seconds = random.random() * 0.010
                time.sleep(seconds)

            kundi Sleeper:
                eleza __del__(self):
                    random_sleep()

            tls = threading.local()

            eleza f():
                # Sleep a bit so that the thread ni still running when
                # Py_Finalize() ni called.
                random_sleep()
                tls.x = Sleeper()
                random_sleep()

            threading.Thread(target=f).start()
            random_sleep()
        """
        rc, out, err = assert_python_ok("-c", code)
        self.assertEqual(err, b"")

    eleza test_tstate_lock(self):
        # Test an implementation detail of Thread objects.
        started = _thread.allocate_lock()
        finish = _thread.allocate_lock()
        started.acquire()
        finish.acquire()
        eleza f():
            started.release()
            finish.acquire()
            time.sleep(0.01)
        # The tstate lock ni Tupu until the thread ni started
        t = threading.Thread(target=f)
        self.assertIs(t._tstate_lock, Tupu)
        t.start()
        started.acquire()
        self.assertKweli(t.is_alive())
        # The tstate lock can't be acquired when the thread ni running
        # (or suspended).
        tstate_lock = t._tstate_lock
        self.assertUongo(tstate_lock.acquire(timeout=0), Uongo)
        finish.release()
        # When the thread ends, the state_lock can be successfully
        # acquired.
        self.assertKweli(tstate_lock.acquire(timeout=5), Uongo)
        # But is_alive() ni still Kweli:  we hold _tstate_lock now, which
        # prevents is_alive() kutoka knowing the thread's end-of-life C code
        # ni done.
        self.assertKweli(t.is_alive())
        # Let is_alive() find out the C code ni done.
        tstate_lock.release()
        self.assertUongo(t.is_alive())
        # And verify the thread disposed of _tstate_lock.
        self.assertIsTupu(t._tstate_lock)
        t.join()

    eleza test_repr_stopped(self):
        # Verify that "stopped" shows up kwenye repr(Thread) appropriately.
        started = _thread.allocate_lock()
        finish = _thread.allocate_lock()
        started.acquire()
        finish.acquire()
        eleza f():
            started.release()
            finish.acquire()
        t = threading.Thread(target=f)
        t.start()
        started.acquire()
        self.assertIn("started", repr(t))
        finish.release()
        # "stopped" should appear kwenye the repr kwenye a reasonable amount of time.
        # Implementation detail:  kama of this writing, that's trivially true
        # ikiwa .join() ni called, na almost trivially true ikiwa .is_alive() is
        # called.  The detail we're testing here ni that "stopped" shows up
        # "all on its own".
        LOOKING_FOR = "stopped"
        kila i kwenye range(500):
            ikiwa LOOKING_FOR kwenye repr(t):
                koma
            time.sleep(0.01)
        self.assertIn(LOOKING_FOR, repr(t)) # we waited at least 5 seconds
        t.join()

    eleza test_BoundedSemaphore_limit(self):
        # BoundedSemaphore should ashiria ValueError ikiwa released too often.
        kila limit kwenye range(1, 10):
            bs = threading.BoundedSemaphore(limit)
            threads = [threading.Thread(target=bs.acquire)
                       kila _ kwenye range(limit)]
            kila t kwenye threads:
                t.start()
            kila t kwenye threads:
                t.join()
            threads = [threading.Thread(target=bs.release)
                       kila _ kwenye range(limit)]
            kila t kwenye threads:
                t.start()
            kila t kwenye threads:
                t.join()
            self.assertRaises(ValueError, bs.release)

    @cpython_only
    eleza test_frame_tstate_tracing(self):
        # Issue #14432: Crash when a generator ni created kwenye a C thread that is
        # destroyed wakati the generator ni still used. The issue was that a
        # generator contains a frame, na the frame kept a reference to the
        # Python state of the destroyed C thread. The crash occurs when a trace
        # function ni setup.

        eleza noop_trace(frame, event, arg):
            # no operation
            rudisha noop_trace

        eleza generator():
            wakati 1:
                tuma "generator"

        eleza callback():
            ikiwa callback.gen ni Tupu:
                callback.gen = generator()
            rudisha next(callback.gen)
        callback.gen = Tupu

        old_trace = sys.gettrace()
        sys.settrace(noop_trace)
        jaribu:
            # Install a trace function
            threading.settrace(noop_trace)

            # Create a generator kwenye a C thread which exits after the call
            agiza _testcapi
            _testcapi.call_in_temporary_c_thread(callback)

            # Call the generator kwenye a different Python thread, check that the
            # generator didn't keep a reference to the destroyed thread state
            kila test kwenye range(3):
                # The trace function ni still called here
                callback()
        mwishowe:
            sys.settrace(old_trace)

    @cpython_only
    eleza test_shutdown_locks(self):
        kila daemon kwenye (Uongo, Kweli):
            ukijumuisha self.subTest(daemon=daemon):
                event = threading.Event()
                thread = threading.Thread(target=event.wait, daemon=daemon)

                # Thread.start() must add lock to _shutdown_locks,
                # but only kila non-daemon thread
                thread.start()
                tstate_lock = thread._tstate_lock
                ikiwa sio daemon:
                    self.assertIn(tstate_lock, threading._shutdown_locks)
                isipokua:
                    self.assertNotIn(tstate_lock, threading._shutdown_locks)

                # unblock the thread na join it
                event.set()
                thread.join()

                # Thread._stop() must remove tstate_lock kutoka _shutdown_locks.
                # Daemon threads must never add it to _shutdown_locks.
                self.assertNotIn(tstate_lock, threading._shutdown_locks)


kundi ThreadJoinOnShutdown(BaseTestCase):

    eleza _run_and_join(self, script):
        script = """ikiwa 1:
            agiza sys, os, time, threading

            # a thread, which waits kila the main program to terminate
            eleza joiningfunc(mainthread):
                mainthread.join()
                andika('end of thread')
                # stdout ni fully buffered because sio a tty, we have to flush
                # before exit.
                sys.stdout.flush()
        \n""" + script

        rc, out, err = assert_python_ok("-c", script)
        data = out.decode().replace('\r', '')
        self.assertEqual(data, "end of main\nend of thread\n")

    eleza test_1_join_on_shutdown(self):
        # The usual case: on exit, wait kila a non-daemon thread
        script = """ikiwa 1:
            agiza os
            t = threading.Thread(target=joiningfunc,
                                 args=(threading.current_thread(),))
            t.start()
            time.sleep(0.1)
            andika('end of main')
            """
        self._run_and_join(script)

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    @unittest.skipIf(sys.platform kwenye platforms_to_skip, "due to known OS bug")
    eleza test_2_join_in_forked_process(self):
        # Like the test above, but kutoka a forked interpreter
        script = """ikiwa 1:
            childpid = os.fork()
            ikiwa childpid != 0:
                os.waitpid(childpid, 0)
                sys.exit(0)

            t = threading.Thread(target=joiningfunc,
                                 args=(threading.current_thread(),))
            t.start()
            andika('end of main')
            """
        self._run_and_join(script)

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    @unittest.skipIf(sys.platform kwenye platforms_to_skip, "due to known OS bug")
    eleza test_3_join_in_forked_from_thread(self):
        # Like the test above, but fork() was called kutoka a worker thread
        # In the forked process, the main Thread object must be marked kama stopped.

        script = """ikiwa 1:
            main_thread = threading.current_thread()
            eleza worker():
                childpid = os.fork()
                ikiwa childpid != 0:
                    os.waitpid(childpid, 0)
                    sys.exit(0)

                t = threading.Thread(target=joiningfunc,
                                     args=(main_thread,))
                andika('end of main')
                t.start()
                t.join() # Should sio block: main_thread ni already stopped

            w = threading.Thread(target=worker)
            w.start()
            """
        self._run_and_join(script)

    @unittest.skipIf(sys.platform kwenye platforms_to_skip, "due to known OS bug")
    eleza test_4_daemon_threads(self):
        # Check that a daemon thread cannot crash the interpreter on shutdown
        # by manipulating internal structures that are being disposed of in
        # the main thread.
        script = """ikiwa Kweli:
            agiza os
            agiza random
            agiza sys
            agiza time
            agiza threading

            thread_has_run = set()

            eleza random_io():
                '''Loop kila a wakati sleeping random tiny amounts na doing some I/O.'''
                wakati Kweli:
                    ukijumuisha open(os.__file__, 'rb') kama in_f:
                        stuff = in_f.read(200)
                        ukijumuisha open(os.devnull, 'wb') kama null_f:
                            null_f.write(stuff)
                            time.sleep(random.random() / 1995)
                    thread_has_run.add(threading.current_thread())

            eleza main():
                count = 0
                kila _ kwenye range(40):
                    new_thread = threading.Thread(target=random_io)
                    new_thread.daemon = Kweli
                    new_thread.start()
                    count += 1
                wakati len(thread_has_run) < count:
                    time.sleep(0.001)
                # Trigger process shutdown
                sys.exit(0)

            main()
            """
        rc, out, err = assert_python_ok('-c', script)
        self.assertUongo(err)

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    @unittest.skipIf(sys.platform kwenye platforms_to_skip, "due to known OS bug")
    eleza test_reinit_tls_after_fork(self):
        # Issue #13817: fork() would deadlock kwenye a multithreaded program with
        # the ad-hoc TLS implementation.

        eleza do_fork_and_wait():
            # just fork a child process na wait it
            pid = os.fork()
            ikiwa pid > 0:
                os.waitpid(pid, 0)
            isipokua:
                os._exit(0)

        # start a bunch of threads that will fork() child processes
        threads = []
        kila i kwenye range(16):
            t = threading.Thread(target=do_fork_and_wait)
            threads.append(t)
            t.start()

        kila t kwenye threads:
            t.join()

    @unittest.skipUnless(hasattr(os, 'fork'), "needs os.fork()")
    eleza test_clear_threads_states_after_fork(self):
        # Issue #17094: check that threads states are cleared after fork()

        # start a bunch of threads
        threads = []
        kila i kwenye range(16):
            t = threading.Thread(target=lambda : time.sleep(0.3))
            threads.append(t)
            t.start()

        pid = os.fork()
        ikiwa pid == 0:
            # check that threads states have been cleared
            ikiwa len(sys._current_frames()) == 1:
                os._exit(0)
            isipokua:
                os._exit(1)
        isipokua:
            _, status = os.waitpid(pid, 0)
            self.assertEqual(0, status)

        kila t kwenye threads:
            t.join()


kundi SubinterpThreadingTests(BaseTestCase):

    eleza test_threads_join(self):
        # Non-daemon threads should be joined at subinterpreter shutdown
        # (issue #18808)
        r, w = os.pipe()
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        code = r"""ikiwa 1:
            agiza os
            agiza random
            agiza threading
            agiza time

            eleza random_sleep():
                seconds = random.random() * 0.010
                time.sleep(seconds)

            eleza f():
                # Sleep a bit so that the thread ni still running when
                # Py_EndInterpreter ni called.
                random_sleep()
                os.write(%d, b"x")

            threading.Thread(target=f).start()
            random_sleep()
            """ % (w,)
        ret = test.support.run_in_subinterp(code)
        self.assertEqual(ret, 0)
        # The thread was joined properly.
        self.assertEqual(os.read(r, 1), b"x")

    eleza test_threads_join_2(self):
        # Same kama above, but a delay gets introduced after the thread's
        # Python code returned but before the thread state ni deleted.
        # To achieve this, we register a thread-local object which sleeps
        # a bit when deallocated.
        r, w = os.pipe()
        self.addCleanup(os.close, r)
        self.addCleanup(os.close, w)
        code = r"""ikiwa 1:
            agiza os
            agiza random
            agiza threading
            agiza time

            eleza random_sleep():
                seconds = random.random() * 0.010
                time.sleep(seconds)

            kundi Sleeper:
                eleza __del__(self):
                    random_sleep()

            tls = threading.local()

            eleza f():
                # Sleep a bit so that the thread ni still running when
                # Py_EndInterpreter ni called.
                random_sleep()
                tls.x = Sleeper()
                os.write(%d, b"x")

            threading.Thread(target=f).start()
            random_sleep()
            """ % (w,)
        ret = test.support.run_in_subinterp(code)
        self.assertEqual(ret, 0)
        # The thread was joined properly.
        self.assertEqual(os.read(r, 1), b"x")

    @cpython_only
    eleza test_daemon_threads_fatal_error(self):
        subinterp_code = r"""ikiwa 1:
            agiza os
            agiza threading
            agiza time

            eleza f():
                # Make sure the daemon thread ni still running when
                # Py_EndInterpreter ni called.
                time.sleep(10)
            threading.Thread(target=f, daemon=Kweli).start()
            """
        script = r"""ikiwa 1:
            agiza _testcapi

            _testcapi.run_in_subinterp(%r)
            """ % (subinterp_code,)
        ukijumuisha test.support.SuppressCrashReport():
            rc, out, err = assert_python_failure("-c", script)
        self.assertIn("Fatal Python error: Py_EndInterpreter: "
                      "not the last thread", err.decode())


kundi ThreadingExceptionTests(BaseTestCase):
    # A RuntimeError should be raised ikiwa Thread.start() ni called
    # multiple times.
    eleza test_start_thread_again(self):
        thread = threading.Thread()
        thread.start()
        self.assertRaises(RuntimeError, thread.start)
        thread.join()

    eleza test_joining_current_thread(self):
        current_thread = threading.current_thread()
        self.assertRaises(RuntimeError, current_thread.join);

    eleza test_joining_inactive_thread(self):
        thread = threading.Thread()
        self.assertRaises(RuntimeError, thread.join)

    eleza test_daemonize_active_thread(self):
        thread = threading.Thread()
        thread.start()
        self.assertRaises(RuntimeError, setattr, thread, "daemon", Kweli)
        thread.join()

    eleza test_releasing_unacquired_lock(self):
        lock = threading.Lock()
        self.assertRaises(RuntimeError, lock.release)

    eleza test_recursion_limit(self):
        # Issue 9670
        # test that excessive recursion within a non-main thread causes
        # an exception rather than crashing the interpreter on platforms
        # like Mac OS X ama FreeBSD which have small default stack sizes
        # kila threads
        script = """ikiwa Kweli:
            agiza threading

            eleza recurse():
                rudisha recurse()

            eleza outer():
                jaribu:
                    recurse()
                tatizo RecursionError:
                    pita

            w = threading.Thread(target=outer)
            w.start()
            w.join()
            andika('end of main thread')
            """
        expected_output = "end of main thread\n"
        p = subprocess.Popen([sys.executable, "-c", script],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        data = stdout.decode().replace('\r', '')
        self.assertEqual(p.returncode, 0, "Unexpected error: " + stderr.decode())
        self.assertEqual(data, expected_output)

    eleza test_print_exception(self):
        script = r"""ikiwa Kweli:
            agiza threading
            agiza time

            running = Uongo
            eleza run():
                global running
                running = Kweli
                wakati running:
                    time.sleep(0.01)
                1/0
            t = threading.Thread(target=run)
            t.start()
            wakati sio running:
                time.sleep(0.01)
            running = Uongo
            t.join()
            """
        rc, out, err = assert_python_ok("-c", script)
        self.assertEqual(out, b'')
        err = err.decode()
        self.assertIn("Exception kwenye thread", err)
        self.assertIn("Traceback (most recent call last):", err)
        self.assertIn("ZeroDivisionError", err)
        self.assertNotIn("Unhandled exception", err)

    @requires_type_collecting
    eleza test_print_exception_stderr_is_none_1(self):
        script = r"""ikiwa Kweli:
            agiza sys
            agiza threading
            agiza time

            running = Uongo
            eleza run():
                global running
                running = Kweli
                wakati running:
                    time.sleep(0.01)
                1/0
            t = threading.Thread(target=run)
            t.start()
            wakati sio running:
                time.sleep(0.01)
            sys.stderr = Tupu
            running = Uongo
            t.join()
            """
        rc, out, err = assert_python_ok("-c", script)
        self.assertEqual(out, b'')
        err = err.decode()
        self.assertIn("Exception kwenye thread", err)
        self.assertIn("Traceback (most recent call last):", err)
        self.assertIn("ZeroDivisionError", err)
        self.assertNotIn("Unhandled exception", err)

    eleza test_print_exception_stderr_is_none_2(self):
        script = r"""ikiwa Kweli:
            agiza sys
            agiza threading
            agiza time

            running = Uongo
            eleza run():
                global running
                running = Kweli
                wakati running:
                    time.sleep(0.01)
                1/0
            sys.stderr = Tupu
            t = threading.Thread(target=run)
            t.start()
            wakati sio running:
                time.sleep(0.01)
            running = Uongo
            t.join()
            """
        rc, out, err = assert_python_ok("-c", script)
        self.assertEqual(out, b'')
        self.assertNotIn("Unhandled exception", err.decode())

    eleza test_bare_raise_in_brand_new_thread(self):
        eleza bare_raise():
            raise

        kundi Issue27558(threading.Thread):
            exc = Tupu

            eleza run(self):
                jaribu:
                    bare_raise()
                tatizo Exception kama exc:
                    self.exc = exc

        thread = Issue27558()
        thread.start()
        thread.join()
        self.assertIsNotTupu(thread.exc)
        self.assertIsInstance(thread.exc, RuntimeError)
        # explicitly koma the reference cycle to sio leak a dangling thread
        thread.exc = Tupu


kundi ThreadRunFail(threading.Thread):
    eleza run(self):
        ashiria ValueError("run failed")


kundi ExceptHookTests(BaseTestCase):
    eleza test_excepthook(self):
        ukijumuisha support.captured_output("stderr") kama stderr:
            thread = ThreadRunFail(name="excepthook thread")
            thread.start()
            thread.join()

        stderr = stderr.getvalue().strip()
        self.assertIn(f'Exception kwenye thread {thread.name}:\n', stderr)
        self.assertIn('Traceback (most recent call last):\n', stderr)
        self.assertIn('  ashiria ValueError("run failed")', stderr)
        self.assertIn('ValueError: run failed', stderr)

    @support.cpython_only
    eleza test_excepthook_thread_Tupu(self):
        # threading.excepthook called ukijumuisha thread=Tupu: log the thread
        # identifier kwenye this case.
        ukijumuisha support.captured_output("stderr") kama stderr:
            jaribu:
                ashiria ValueError("bug")
            tatizo Exception kama exc:
                args = threading.ExceptHookArgs([*sys.exc_info(), Tupu])
                jaribu:
                    threading.excepthook(args)
                mwishowe:
                    # Explicitly koma a reference cycle
                    args = Tupu

        stderr = stderr.getvalue().strip()
        self.assertIn(f'Exception kwenye thread {threading.get_ident()}:\n', stderr)
        self.assertIn('Traceback (most recent call last):\n', stderr)
        self.assertIn('  ashiria ValueError("bug")', stderr)
        self.assertIn('ValueError: bug', stderr)

    eleza test_system_exit(self):
        kundi ThreadExit(threading.Thread):
            eleza run(self):
                sys.exit(1)

        # threading.excepthook() silently ignores SystemExit
        ukijumuisha support.captured_output("stderr") kama stderr:
            thread = ThreadExit()
            thread.start()
            thread.join()

        self.assertEqual(stderr.getvalue(), '')

    eleza test_custom_excepthook(self):
        args = Tupu

        eleza hook(hook_args):
            nonlocal args
            args = hook_args

        jaribu:
            ukijumuisha support.swap_attr(threading, 'excepthook', hook):
                thread = ThreadRunFail()
                thread.start()
                thread.join()

            self.assertEqual(args.exc_type, ValueError)
            self.assertEqual(str(args.exc_value), 'run failed')
            self.assertEqual(args.exc_traceback, args.exc_value.__traceback__)
            self.assertIs(args.thread, thread)
        mwishowe:
            # Break reference cycle
            args = Tupu

    eleza test_custom_excepthook_fail(self):
        eleza threading_hook(args):
            ashiria ValueError("threading_hook failed")

        err_str = Tupu

        eleza sys_hook(exc_type, exc_value, exc_traceback):
            nonlocal err_str
            err_str = str(exc_value)

        ukijumuisha support.swap_attr(threading, 'excepthook', threading_hook), \
             support.swap_attr(sys, 'excepthook', sys_hook), \
             support.captured_output('stderr') kama stderr:
            thread = ThreadRunFail()
            thread.start()
            thread.join()

        self.assertEqual(stderr.getvalue(),
                         'Exception kwenye threading.excepthook:\n')
        self.assertEqual(err_str, 'threading_hook failed')


kundi TimerTests(BaseTestCase):

    eleza setUp(self):
        BaseTestCase.setUp(self)
        self.callback_args = []
        self.callback_event = threading.Event()

    eleza test_init_immutable_default_args(self):
        # Issue 17435: constructor defaults were mutable objects, they could be
        # mutated via the object attributes na affect other Timer objects.
        timer1 = threading.Timer(0.01, self._callback_spy)
        timer1.start()
        self.callback_event.wait()
        timer1.args.append("blah")
        timer1.kwargs["foo"] = "bar"
        self.callback_event.clear()
        timer2 = threading.Timer(0.01, self._callback_spy)
        timer2.start()
        self.callback_event.wait()
        self.assertEqual(len(self.callback_args), 2)
        self.assertEqual(self.callback_args, [((), {}), ((), {})])
        timer1.join()
        timer2.join()

    eleza _callback_spy(self, *args, **kwargs):
        self.callback_args.append((args[:], kwargs.copy()))
        self.callback_event.set()

kundi LockTests(lock_tests.LockTests):
    locktype = staticmethod(threading.Lock)

kundi PyRLockTests(lock_tests.RLockTests):
    locktype = staticmethod(threading._PyRLock)

@unittest.skipIf(threading._CRLock ni Tupu, 'RLock sio implemented kwenye C')
kundi CRLockTests(lock_tests.RLockTests):
    locktype = staticmethod(threading._CRLock)

kundi EventTests(lock_tests.EventTests):
    eventtype = staticmethod(threading.Event)

kundi ConditionAsRLockTests(lock_tests.RLockTests):
    # Condition uses an RLock by default na exports its API.
    locktype = staticmethod(threading.Condition)

kundi ConditionTests(lock_tests.ConditionTests):
    condtype = staticmethod(threading.Condition)

kundi SemaphoreTests(lock_tests.SemaphoreTests):
    semtype = staticmethod(threading.Semaphore)

kundi BoundedSemaphoreTests(lock_tests.BoundedSemaphoreTests):
    semtype = staticmethod(threading.BoundedSemaphore)

kundi BarrierTests(lock_tests.BarrierTests):
    barriertype = staticmethod(threading.Barrier)


kundi MiscTestCase(unittest.TestCase):
    eleza test__all__(self):
        extra = {"ThreadError"}
        blacklist = {'currentThread', 'activeCount'}
        support.check__all__(self, threading, ('threading', '_thread'),
                             extra=extra, blacklist=blacklist)


kundi InterruptMainTests(unittest.TestCase):
    eleza test_interrupt_main_subthread(self):
        # Calling start_new_thread ukijumuisha a function that executes interrupt_main
        # should ashiria KeyboardInterrupt upon completion.
        eleza call_interrupt():
            _thread.interrupt_main()
        t = threading.Thread(target=call_interrupt)
        ukijumuisha self.assertRaises(KeyboardInterrupt):
            t.start()
            t.join()
        t.join()

    eleza test_interrupt_main_mainthread(self):
        # Make sure that ikiwa interrupt_main ni called kwenye main thread that
        # KeyboardInterrupt ni raised instantly.
        ukijumuisha self.assertRaises(KeyboardInterrupt):
            _thread.interrupt_main()

    eleza test_interrupt_main_noerror(self):
        handler = signal.getsignal(signal.SIGINT)
        jaribu:
            # No exception should arise.
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            _thread.interrupt_main()

            signal.signal(signal.SIGINT, signal.SIG_DFL)
            _thread.interrupt_main()
        mwishowe:
            # Restore original handler
            signal.signal(signal.SIGINT, handler)


ikiwa __name__ == "__main__":
    unittest.main()
