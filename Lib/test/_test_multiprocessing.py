#
# Unit tests kila the multiprocessing package
#

agiza unittest
agiza unittest.mock
agiza queue as pyqueue
agiza time
agiza io
agiza itertools
agiza sys
agiza os
agiza gc
agiza errno
agiza signal
agiza array
agiza socket
agiza random
agiza logging
agiza subprocess
agiza struct
agiza operator
agiza pickle
agiza weakref
agiza warnings
agiza test.support
agiza test.support.script_helper
kutoka test agiza support


# Skip tests ikiwa _multiprocessing wasn't built.
_multiprocessing = test.support.import_module('_multiprocessing')
# Skip tests ikiwa sem_open implementation ni broken.
test.support.import_module('multiprocessing.synchronize')
agiza threading

agiza multiprocessing.connection
agiza multiprocessing.dummy
agiza multiprocessing.heap
agiza multiprocessing.managers
agiza multiprocessing.pool
agiza multiprocessing.queues

kutoka multiprocessing agiza util

jaribu:
    kutoka multiprocessing agiza reduction
    HAS_REDUCTION = reduction.HAVE_SEND_HANDLE
except ImportError:
    HAS_REDUCTION = Uongo

jaribu:
    kutoka multiprocessing.sharedctypes agiza Value, copy
    HAS_SHAREDCTYPES = Kweli
except ImportError:
    HAS_SHAREDCTYPES = Uongo

jaribu:
    kutoka multiprocessing agiza shared_memory
    HAS_SHMEM = Kweli
except ImportError:
    HAS_SHMEM = Uongo

jaribu:
    agiza msvcrt
except ImportError:
    msvcrt = Tupu

#
#
#

# Timeout to wait until a process completes
TIMEOUT = 60.0 # seconds

eleza latin(s):
    rudisha s.encode('latin')


eleza close_queue(queue):
    ikiwa isinstance(queue, multiprocessing.queues.Queue):
        queue.close()
        queue.join_thread()


eleza join_process(process):
    # Since multiprocessing.Process has the same API than threading.Thread
    # (join() na is_alive(), the support function can be reused
    support.join_thread(process, timeout=TIMEOUT)


ikiwa os.name == "posix":
    kutoka multiprocessing agiza resource_tracker

    eleza _resource_unlink(name, rtype):
        resource_tracker._CLEANUP_FUNCS[rtype](name)


#
# Constants
#

LOG_LEVEL = util.SUBWARNING
#LOG_LEVEL = logging.DEBUG

DELTA = 0.1
CHECK_TIMINGS = Uongo     # making true makes tests take a lot longer
                          # na can sometimes cause some non-serious
                          # failures because some calls block a bit
                          # longer than expected
ikiwa CHECK_TIMINGS:
    TIMEOUT1, TIMEOUT2, TIMEOUT3 = 0.82, 0.35, 1.4
isipokua:
    TIMEOUT1, TIMEOUT2, TIMEOUT3 = 0.1, 0.1, 0.1

HAVE_GETVALUE = sio getattr(_multiprocessing,
                            'HAVE_BROKEN_SEM_GETVALUE', Uongo)

WIN32 = (sys.platform == "win32")

kutoka multiprocessing.connection agiza wait

eleza wait_for_handle(handle, timeout):
    ikiwa timeout ni sio Tupu na timeout < 0.0:
        timeout = Tupu
    rudisha wait([handle], timeout)

jaribu:
    MAXFD = os.sysconf("SC_OPEN_MAX")
tatizo:
    MAXFD = 256

# To speed up tests when using the forkserver, we can preload these:
PRELOAD = ['__main__', 'test.test_multiprocessing_forkserver']

#
# Some tests require ctypes
#

jaribu:
    kutoka ctypes agiza Structure, c_int, c_double, c_longlong
except ImportError:
    Structure = object
    c_int = c_double = c_longlong = Tupu


eleza check_enough_semaphores():
    """Check that the system supports enough semaphores to run the test."""
    # minimum number of semaphores available according to POSIX
    nsems_min = 256
    jaribu:
        nsems = os.sysconf("SC_SEM_NSEMS_MAX")
    except (AttributeError, ValueError):
        # sysconf sio available ama setting sio available
        return
    ikiwa nsems == -1 ama nsems >= nsems_min:
        return
     ashiria unittest.SkipTest("The OS doesn't support enough semaphores "
                            "to run the test (required: %d)." % nsems_min)


#
# Creates a wrapper kila a function which records the time it takes to finish
#

kundi TimingWrapper(object):

    eleza __init__(self, func):
        self.func = func
        self.elapsed = Tupu

    eleza __call__(self, *args, **kwds):
        t = time.monotonic()
        jaribu:
            rudisha self.func(*args, **kwds)
        mwishowe:
            self.elapsed = time.monotonic() - t

#
# Base kundi kila test cases
#

kundi BaseTestCase(object):

    ALLOWED_TYPES = ('processes', 'manager', 'threads')

    eleza assertTimingAlmostEqual(self, a, b):
        ikiwa CHECK_TIMINGS:
            self.assertAlmostEqual(a, b, 1)

    eleza assertReturnsIfImplemented(self, value, func, *args):
        jaribu:
            res = func(*args)
        except NotImplementedError:
            pass
        isipokua:
            rudisha self.assertEqual(value, res)

    # For the sanity of Windows users, rather than crashing ama freezing in
    # multiple ways.
    eleza __reduce__(self, *args):
         ashiria NotImplementedError("shouldn't try to pickle a test case")

    __reduce_ex__ = __reduce__

#
# Return the value of a semaphore
#

eleza get_value(self):
    jaribu:
        rudisha self.get_value()
    except AttributeError:
        jaribu:
            rudisha self._Semaphore__value
        except AttributeError:
            jaribu:
                rudisha self._value
            except AttributeError:
                 ashiria NotImplementedError

#
# Testcases
#

kundi DummyCallable:
    eleza __call__(self, q, c):
        assert isinstance(c, DummyCallable)
        q.put(5)


kundi _TestProcess(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    eleza test_current(self):
        ikiwa self.TYPE == 'threads':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        current = self.current_process()
        authkey = current.authkey

        self.assertKweli(current.is_alive())
        self.assertKweli(not current.daemon)
        self.assertIsInstance(authkey, bytes)
        self.assertKweli(len(authkey) > 0)
        self.assertEqual(current.ident, os.getpid())
        self.assertEqual(current.exitcode, Tupu)

    eleza test_daemon_argument(self):
        ikiwa self.TYPE == "threads":
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        # By default uses the current process's daemon flag.
        proc0 = self.Process(target=self._test)
        self.assertEqual(proc0.daemon, self.current_process().daemon)
        proc1 = self.Process(target=self._test, daemon=Kweli)
        self.assertKweli(proc1.daemon)
        proc2 = self.Process(target=self._test, daemon=Uongo)
        self.assertUongo(proc2.daemon)

    @classmethod
    eleza _test(cls, q, *args, **kwds):
        current = cls.current_process()
        q.put(args)
        q.put(kwds)
        q.put(current.name)
        ikiwa cls.TYPE != 'threads':
            q.put(bytes(current.authkey))
            q.put(current.pid)

    eleza test_parent_process_attributes(self):
        ikiwa self.TYPE == "threads":
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        self.assertIsTupu(self.parent_process())

        rconn, wconn = self.Pipe(duplex=Uongo)
        p = self.Process(target=self._test_send_parent_process, args=(wconn,))
        p.start()
        p.join()
        parent_pid, parent_name = rconn.recv()
        self.assertEqual(parent_pid, self.current_process().pid)
        self.assertEqual(parent_pid, os.getpid())
        self.assertEqual(parent_name, self.current_process().name)

    @classmethod
    eleza _test_send_parent_process(cls, wconn):
        kutoka multiprocessing.process agiza parent_process
        wconn.send([parent_process().pid, parent_process().name])

    eleza test_parent_process(self):
        ikiwa self.TYPE == "threads":
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        # Launch a child process. Make it launch a grandchild process. Kill the
        # child process na make sure that the grandchild notices the death of
        # its parent (a.k.a the child process).
        rconn, wconn = self.Pipe(duplex=Uongo)
        p = self.Process(
            target=self._test_create_grandchild_process, args=(wconn, ))
        p.start()

        ikiwa sio rconn.poll(timeout=60):
             ashiria AssertionError("Could sio communicate ukijumuisha child process")
        parent_process_status = rconn.recv()
        self.assertEqual(parent_process_status, "alive")

        p.terminate()
        p.join()

        ikiwa sio rconn.poll(timeout=60):
             ashiria AssertionError("Could sio communicate ukijumuisha child process")
        parent_process_status = rconn.recv()
        self.assertEqual(parent_process_status, "not alive")

    @classmethod
    eleza _test_create_grandchild_process(cls, wconn):
        p = cls.Process(target=cls._test_report_parent_status, args=(wconn, ))
        p.start()
        time.sleep(300)

    @classmethod
    eleza _test_report_parent_status(cls, wconn):
        kutoka multiprocessing.process agiza parent_process
        wconn.send("alive" ikiwa parent_process().is_alive() isipokua "not alive")
        parent_process().join(timeout=5)
        wconn.send("alive" ikiwa parent_process().is_alive() isipokua "not alive")

    eleza test_process(self):
        q = self.Queue(1)
        e = self.Event()
        args = (q, 1, 2)
        kwargs = {'hello':23, 'bye':2.54}
        name = 'SomeProcess'
        p = self.Process(
            target=self._test, args=args, kwargs=kwargs, name=name
            )
        p.daemon = Kweli
        current = self.current_process()

        ikiwa self.TYPE != 'threads':
            self.assertEqual(p.authkey, current.authkey)
        self.assertEqual(p.is_alive(), Uongo)
        self.assertEqual(p.daemon, Kweli)
        self.assertNotIn(p, self.active_children())
        self.assertKweli(type(self.active_children()) ni list)
        self.assertEqual(p.exitcode, Tupu)

        p.start()

        self.assertEqual(p.exitcode, Tupu)
        self.assertEqual(p.is_alive(), Kweli)
        self.assertIn(p, self.active_children())

        self.assertEqual(q.get(), args[1:])
        self.assertEqual(q.get(), kwargs)
        self.assertEqual(q.get(), p.name)
        ikiwa self.TYPE != 'threads':
            self.assertEqual(q.get(), current.authkey)
            self.assertEqual(q.get(), p.pid)

        p.join()

        self.assertEqual(p.exitcode, 0)
        self.assertEqual(p.is_alive(), Uongo)
        self.assertNotIn(p, self.active_children())
        close_queue(q)

    @classmethod
    eleza _sleep_some(cls):
        time.sleep(100)

    @classmethod
    eleza _test_sleep(cls, delay):
        time.sleep(delay)

    eleza _kill_process(self, meth):
        ikiwa self.TYPE == 'threads':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        p = self.Process(target=self._sleep_some)
        p.daemon = Kweli
        p.start()

        self.assertEqual(p.is_alive(), Kweli)
        self.assertIn(p, self.active_children())
        self.assertEqual(p.exitcode, Tupu)

        join = TimingWrapper(p.join)

        self.assertEqual(join(0), Tupu)
        self.assertTimingAlmostEqual(join.elapsed, 0.0)
        self.assertEqual(p.is_alive(), Kweli)

        self.assertEqual(join(-1), Tupu)
        self.assertTimingAlmostEqual(join.elapsed, 0.0)
        self.assertEqual(p.is_alive(), Kweli)

        # XXX maybe terminating too soon causes the problems on Gentoo...
        time.sleep(1)

        meth(p)

        ikiwa hasattr(signal, 'alarm'):
            # On the Gentoo buildbot waitpid() often seems to block forever.
            # We use alarm() to interrupt it ikiwa it blocks kila too long.
            eleza handler(*args):
                 ashiria RuntimeError('join took too long: %s' % p)
            old_handler = signal.signal(signal.SIGALRM, handler)
            jaribu:
                signal.alarm(10)
                self.assertEqual(join(), Tupu)
            mwishowe:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        isipokua:
            self.assertEqual(join(), Tupu)

        self.assertTimingAlmostEqual(join.elapsed, 0.0)

        self.assertEqual(p.is_alive(), Uongo)
        self.assertNotIn(p, self.active_children())

        p.join()

        rudisha p.exitcode

    eleza test_terminate(self):
        exitcode = self._kill_process(multiprocessing.Process.terminate)
        ikiwa os.name != 'nt':
            self.assertEqual(exitcode, -signal.SIGTERM)

    eleza test_kill(self):
        exitcode = self._kill_process(multiprocessing.Process.kill)
        ikiwa os.name != 'nt':
            self.assertEqual(exitcode, -signal.SIGKILL)

    eleza test_cpu_count(self):
        jaribu:
            cpus = multiprocessing.cpu_count()
        except NotImplementedError:
            cpus = 1
        self.assertKweli(type(cpus) ni int)
        self.assertKweli(cpus >= 1)

    eleza test_active_children(self):
        self.assertEqual(type(self.active_children()), list)

        p = self.Process(target=time.sleep, args=(DELTA,))
        self.assertNotIn(p, self.active_children())

        p.daemon = Kweli
        p.start()
        self.assertIn(p, self.active_children())

        p.join()
        self.assertNotIn(p, self.active_children())

    @classmethod
    eleza _test_recursion(cls, wconn, id):
        wconn.send(id)
        ikiwa len(id) < 2:
            kila i kwenye range(2):
                p = cls.Process(
                    target=cls._test_recursion, args=(wconn, id+[i])
                    )
                p.start()
                p.join()

    eleza test_recursion(self):
        rconn, wconn = self.Pipe(duplex=Uongo)
        self._test_recursion(wconn, [])

        time.sleep(DELTA)
        result = []
        wakati rconn.poll():
            result.append(rconn.recv())

        expected = [
            [],
              [0],
                [0, 0],
                [0, 1],
              [1],
                [1, 0],
                [1, 1]
            ]
        self.assertEqual(result, expected)

    @classmethod
    eleza _test_sentinel(cls, event):
        event.wait(10.0)

    eleza test_sentinel(self):
        ikiwa self.TYPE == "threads":
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))
        event = self.Event()
        p = self.Process(target=self._test_sentinel, args=(event,))
        ukijumuisha self.assertRaises(ValueError):
            p.sentinel
        p.start()
        self.addCleanup(p.join)
        sentinel = p.sentinel
        self.assertIsInstance(sentinel, int)
        self.assertUongo(wait_for_handle(sentinel, timeout=0.0))
        event.set()
        p.join()
        self.assertKweli(wait_for_handle(sentinel, timeout=1))

    @classmethod
    eleza _test_close(cls, rc=0, q=Tupu):
        ikiwa q ni sio Tupu:
            q.get()
        sys.exit(rc)

    eleza test_close(self):
        ikiwa self.TYPE == "threads":
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))
        q = self.Queue()
        p = self.Process(target=self._test_close, kwargs={'q': q})
        p.daemon = Kweli
        p.start()
        self.assertEqual(p.is_alive(), Kweli)
        # Child ni still alive, cannot close
        ukijumuisha self.assertRaises(ValueError):
            p.close()

        q.put(Tupu)
        p.join()
        self.assertEqual(p.is_alive(), Uongo)
        self.assertEqual(p.exitcode, 0)
        p.close()
        ukijumuisha self.assertRaises(ValueError):
            p.is_alive()
        ukijumuisha self.assertRaises(ValueError):
            p.join()
        ukijumuisha self.assertRaises(ValueError):
            p.terminate()
        p.close()

        wr = weakref.ref(p)
        toa p
        gc.collect()
        self.assertIs(wr(), Tupu)

        close_queue(q)

    eleza test_many_processes(self):
        ikiwa self.TYPE == 'threads':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        sm = multiprocessing.get_start_method()
        N = 5 ikiwa sm == 'spawn' isipokua 100

        # Try to overwhelm the forkserver loop ukijumuisha events
        procs = [self.Process(target=self._test_sleep, args=(0.01,))
                 kila i kwenye range(N)]
        kila p kwenye procs:
            p.start()
        kila p kwenye procs:
            join_process(p)
        kila p kwenye procs:
            self.assertEqual(p.exitcode, 0)

        procs = [self.Process(target=self._sleep_some)
                 kila i kwenye range(N)]
        kila p kwenye procs:
            p.start()
        time.sleep(0.001)  # let the children start...
        kila p kwenye procs:
            p.terminate()
        kila p kwenye procs:
            join_process(p)
        ikiwa os.name != 'nt':
            exitcodes = [-signal.SIGTERM]
            ikiwa sys.platform == 'darwin':
                # bpo-31510: On macOS, killing a freshly started process with
                # SIGTERM sometimes kills the process ukijumuisha SIGKILL.
                exitcodes.append(-signal.SIGKILL)
            kila p kwenye procs:
                self.assertIn(p.exitcode, exitcodes)

    eleza test_lose_target_ref(self):
        c = DummyCallable()
        wr = weakref.ref(c)
        q = self.Queue()
        p = self.Process(target=c, args=(q, c))
        toa c
        p.start()
        p.join()
        self.assertIs(wr(), Tupu)
        self.assertEqual(q.get(), 5)
        close_queue(q)

    @classmethod
    eleza _test_child_fd_inflation(self, evt, q):
        q.put(test.support.fd_count())
        evt.wait()

    eleza test_child_fd_inflation(self):
        # Number of fds kwenye child processes should sio grow ukijumuisha the
        # number of running children.
        ikiwa self.TYPE == 'threads':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        sm = multiprocessing.get_start_method()
        ikiwa sm == 'fork':
            # The fork method by design inherits all fds kutoka the parent,
            # trying to go against it ni a lost battle
            self.skipTest('test sio appropriate kila {}'.format(sm))

        N = 5
        evt = self.Event()
        q = self.Queue()

        procs = [self.Process(target=self._test_child_fd_inflation, args=(evt, q))
                 kila i kwenye range(N)]
        kila p kwenye procs:
            p.start()

        jaribu:
            fd_counts = [q.get() kila i kwenye range(N)]
            self.assertEqual(len(set(fd_counts)), 1, fd_counts)

        mwishowe:
            evt.set()
            kila p kwenye procs:
                p.join()
            close_queue(q)

    @classmethod
    eleza _test_wait_for_threads(self, evt):
        eleza func1():
            time.sleep(0.5)
            evt.set()

        eleza func2():
            time.sleep(20)
            evt.clear()

        threading.Thread(target=func1).start()
        threading.Thread(target=func2, daemon=Kweli).start()

    eleza test_wait_for_threads(self):
        # A child process should wait kila non-daemonic threads to end
        # before exiting
        ikiwa self.TYPE == 'threads':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        evt = self.Event()
        proc = self.Process(target=self._test_wait_for_threads, args=(evt,))
        proc.start()
        proc.join()
        self.assertKweli(evt.is_set())

    @classmethod
    eleza _test_error_on_stdio_flush(self, evt, koma_std_streams={}):
        kila stream_name, action kwenye koma_std_streams.items():
            ikiwa action == 'close':
                stream = io.StringIO()
                stream.close()
            isipokua:
                assert action == 'remove'
                stream = Tupu
            setattr(sys, stream_name, Tupu)
        evt.set()

    eleza test_error_on_stdio_flush_1(self):
        # Check that Process works ukijumuisha broken standard streams
        streams = [io.StringIO(), Tupu]
        streams[0].close()
        kila stream_name kwenye ('stdout', 'stderr'):
            kila stream kwenye streams:
                old_stream = getattr(sys, stream_name)
                setattr(sys, stream_name, stream)
                jaribu:
                    evt = self.Event()
                    proc = self.Process(target=self._test_error_on_stdio_flush,
                                        args=(evt,))
                    proc.start()
                    proc.join()
                    self.assertKweli(evt.is_set())
                    self.assertEqual(proc.exitcode, 0)
                mwishowe:
                    setattr(sys, stream_name, old_stream)

    eleza test_error_on_stdio_flush_2(self):
        # Same as test_error_on_stdio_flush_1(), but standard streams are
        # broken by the child process
        kila stream_name kwenye ('stdout', 'stderr'):
            kila action kwenye ('close', 'remove'):
                old_stream = getattr(sys, stream_name)
                jaribu:
                    evt = self.Event()
                    proc = self.Process(target=self._test_error_on_stdio_flush,
                                        args=(evt, {stream_name: action}))
                    proc.start()
                    proc.join()
                    self.assertKweli(evt.is_set())
                    self.assertEqual(proc.exitcode, 0)
                mwishowe:
                    setattr(sys, stream_name, old_stream)

    @classmethod
    eleza _sleep_and_set_event(self, evt, delay=0.0):
        time.sleep(delay)
        evt.set()

    eleza check_forkserver_death(self, signum):
        # bpo-31308: ikiwa the forkserver process has died, we should still
        # be able to create na run new Process instances (the forkserver
        # ni implicitly restarted).
        ikiwa self.TYPE == 'threads':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))
        sm = multiprocessing.get_start_method()
        ikiwa sm != 'forkserver':
            # The fork method by design inherits all fds kutoka the parent,
            # trying to go against it ni a lost battle
            self.skipTest('test sio appropriate kila {}'.format(sm))

        kutoka multiprocessing.forkserver agiza _forkserver
        _forkserver.ensure_running()

        # First process sleeps 500 ms
        delay = 0.5

        evt = self.Event()
        proc = self.Process(target=self._sleep_and_set_event, args=(evt, delay))
        proc.start()

        pid = _forkserver._forkserver_pid
        os.kill(pid, signum)
        # give time to the fork server to die na time to proc to complete
        time.sleep(delay * 2.0)

        evt2 = self.Event()
        proc2 = self.Process(target=self._sleep_and_set_event, args=(evt2,))
        proc2.start()
        proc2.join()
        self.assertKweli(evt2.is_set())
        self.assertEqual(proc2.exitcode, 0)

        proc.join()
        self.assertKweli(evt.is_set())
        self.assertIn(proc.exitcode, (0, 255))

    eleza test_forkserver_sigint(self):
        # Catchable signal
        self.check_forkserver_death(signal.SIGINT)

    eleza test_forkserver_sigkill(self):
        # Uncatchable signal
        ikiwa os.name != 'nt':
            self.check_forkserver_death(signal.SIGKILL)


#
#
#

kundi _UpperCaser(multiprocessing.Process):

    eleza __init__(self):
        multiprocessing.Process.__init__(self)
        self.child_conn, self.parent_conn = multiprocessing.Pipe()

    eleza run(self):
        self.parent_conn.close()
        kila s kwenye iter(self.child_conn.recv, Tupu):
            self.child_conn.send(s.upper())
        self.child_conn.close()

    eleza submit(self, s):
        assert type(s) ni str
        self.parent_conn.send(s)
        rudisha self.parent_conn.recv()

    eleza stop(self):
        self.parent_conn.send(Tupu)
        self.parent_conn.close()
        self.child_conn.close()

kundi _TestSubclassingProcess(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    eleza test_subclassing(self):
        uppercaser = _UpperCaser()
        uppercaser.daemon = Kweli
        uppercaser.start()
        self.assertEqual(uppercaser.submit('hello'), 'HELLO')
        self.assertEqual(uppercaser.submit('world'), 'WORLD')
        uppercaser.stop()
        uppercaser.join()

    eleza test_stderr_flush(self):
        # sys.stderr ni flushed at process shutdown (issue #13812)
        ikiwa self.TYPE == "threads":
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        testfn = test.support.TESTFN
        self.addCleanup(test.support.unlink, testfn)
        proc = self.Process(target=self._test_stderr_flush, args=(testfn,))
        proc.start()
        proc.join()
        ukijumuisha open(testfn, 'r') as f:
            err = f.read()
            # The whole traceback was printed
            self.assertIn("ZeroDivisionError", err)
            self.assertIn("test_multiprocessing.py", err)
            self.assertIn("1/0 # MARKER", err)

    @classmethod
    eleza _test_stderr_flush(cls, testfn):
        fd = os.open(testfn, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        sys.stderr = open(fd, 'w', closefd=Uongo)
        1/0 # MARKER


    @classmethod
    eleza _test_sys_exit(cls, reason, testfn):
        fd = os.open(testfn, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        sys.stderr = open(fd, 'w', closefd=Uongo)
        sys.exit(reason)

    eleza test_sys_exit(self):
        # See Issue 13854
        ikiwa self.TYPE == 'threads':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        testfn = test.support.TESTFN
        self.addCleanup(test.support.unlink, testfn)

        kila reason kwenye (
            [1, 2, 3],
            'ignore this',
        ):
            p = self.Process(target=self._test_sys_exit, args=(reason, testfn))
            p.daemon = Kweli
            p.start()
            join_process(p)
            self.assertEqual(p.exitcode, 1)

            ukijumuisha open(testfn, 'r') as f:
                content = f.read()
            self.assertEqual(content.rstrip(), str(reason))

            os.unlink(testfn)

        kila reason kwenye (Kweli, Uongo, 8):
            p = self.Process(target=sys.exit, args=(reason,))
            p.daemon = Kweli
            p.start()
            join_process(p)
            self.assertEqual(p.exitcode, reason)

#
#
#

eleza queue_empty(q):
    ikiwa hasattr(q, 'empty'):
        rudisha q.empty()
    isipokua:
        rudisha q.qsize() == 0

eleza queue_full(q, maxsize):
    ikiwa hasattr(q, 'full'):
        rudisha q.full()
    isipokua:
        rudisha q.qsize() == maxsize


kundi _TestQueue(BaseTestCase):


    @classmethod
    eleza _test_put(cls, queue, child_can_start, parent_can_endelea):
        child_can_start.wait()
        kila i kwenye range(6):
            queue.get()
        parent_can_endelea.set()

    eleza test_put(self):
        MAXSIZE = 6
        queue = self.Queue(maxsize=MAXSIZE)
        child_can_start = self.Event()
        parent_can_endelea = self.Event()

        proc = self.Process(
            target=self._test_put,
            args=(queue, child_can_start, parent_can_endelea)
            )
        proc.daemon = Kweli
        proc.start()

        self.assertEqual(queue_empty(queue), Kweli)
        self.assertEqual(queue_full(queue, MAXSIZE), Uongo)

        queue.put(1)
        queue.put(2, Kweli)
        queue.put(3, Kweli, Tupu)
        queue.put(4, Uongo)
        queue.put(5, Uongo, Tupu)
        queue.put_nowait(6)

        # the values may be kwenye buffer but sio yet kwenye pipe so sleep a bit
        time.sleep(DELTA)

        self.assertEqual(queue_empty(queue), Uongo)
        self.assertEqual(queue_full(queue, MAXSIZE), Kweli)

        put = TimingWrapper(queue.put)
        put_nowait = TimingWrapper(queue.put_nowait)

        self.assertRaises(pyqueue.Full, put, 7, Uongo)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(pyqueue.Full, put, 7, Uongo, Tupu)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(pyqueue.Full, put_nowait, 7)
        self.assertTimingAlmostEqual(put_nowait.elapsed, 0)

        self.assertRaises(pyqueue.Full, put, 7, Kweli, TIMEOUT1)
        self.assertTimingAlmostEqual(put.elapsed, TIMEOUT1)

        self.assertRaises(pyqueue.Full, put, 7, Uongo, TIMEOUT2)
        self.assertTimingAlmostEqual(put.elapsed, 0)

        self.assertRaises(pyqueue.Full, put, 7, Kweli, timeout=TIMEOUT3)
        self.assertTimingAlmostEqual(put.elapsed, TIMEOUT3)

        child_can_start.set()
        parent_can_endelea.wait()

        self.assertEqual(queue_empty(queue), Kweli)
        self.assertEqual(queue_full(queue, MAXSIZE), Uongo)

        proc.join()
        close_queue(queue)

    @classmethod
    eleza _test_get(cls, queue, child_can_start, parent_can_endelea):
        child_can_start.wait()
        #queue.put(1)
        queue.put(2)
        queue.put(3)
        queue.put(4)
        queue.put(5)
        parent_can_endelea.set()

    eleza test_get(self):
        queue = self.Queue()
        child_can_start = self.Event()
        parent_can_endelea = self.Event()

        proc = self.Process(
            target=self._test_get,
            args=(queue, child_can_start, parent_can_endelea)
            )
        proc.daemon = Kweli
        proc.start()

        self.assertEqual(queue_empty(queue), Kweli)

        child_can_start.set()
        parent_can_endelea.wait()

        time.sleep(DELTA)
        self.assertEqual(queue_empty(queue), Uongo)

        # Hangs unexpectedly, remove kila now
        #self.assertEqual(queue.get(), 1)
        self.assertEqual(queue.get(Kweli, Tupu), 2)
        self.assertEqual(queue.get(Kweli), 3)
        self.assertEqual(queue.get(timeout=1), 4)
        self.assertEqual(queue.get_nowait(), 5)

        self.assertEqual(queue_empty(queue), Kweli)

        get = TimingWrapper(queue.get)
        get_nowait = TimingWrapper(queue.get_nowait)

        self.assertRaises(pyqueue.Empty, get, Uongo)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(pyqueue.Empty, get, Uongo, Tupu)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(pyqueue.Empty, get_nowait)
        self.assertTimingAlmostEqual(get_nowait.elapsed, 0)

        self.assertRaises(pyqueue.Empty, get, Kweli, TIMEOUT1)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT1)

        self.assertRaises(pyqueue.Empty, get, Uongo, TIMEOUT2)
        self.assertTimingAlmostEqual(get.elapsed, 0)

        self.assertRaises(pyqueue.Empty, get, timeout=TIMEOUT3)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT3)

        proc.join()
        close_queue(queue)

    @classmethod
    eleza _test_fork(cls, queue):
        kila i kwenye range(10, 20):
            queue.put(i)
        # note that at this point the items may only be buffered, so the
        # process cannot shutdown until the feeder thread has finished
        # pushing items onto the pipe.

    eleza test_fork(self):
        # Old versions of Queue would fail to create a new feeder
        # thread kila a forked process ikiwa the original process had its
        # own feeder thread.  This test checks that this no longer
        # happens.

        queue = self.Queue()

        # put items on queue so that main process starts a feeder thread
        kila i kwenye range(10):
            queue.put(i)

        # wait to make sure thread starts before we fork a new process
        time.sleep(DELTA)

        # fork process
        p = self.Process(target=self._test_fork, args=(queue,))
        p.daemon = Kweli
        p.start()

        # check that all expected items are kwenye the queue
        kila i kwenye range(20):
            self.assertEqual(queue.get(), i)
        self.assertRaises(pyqueue.Empty, queue.get, Uongo)

        p.join()
        close_queue(queue)

    eleza test_qsize(self):
        q = self.Queue()
        jaribu:
            self.assertEqual(q.qsize(), 0)
        except NotImplementedError:
            self.skipTest('qsize method sio implemented')
        q.put(1)
        self.assertEqual(q.qsize(), 1)
        q.put(5)
        self.assertEqual(q.qsize(), 2)
        q.get()
        self.assertEqual(q.qsize(), 1)
        q.get()
        self.assertEqual(q.qsize(), 0)
        close_queue(q)

    @classmethod
    eleza _test_task_done(cls, q):
        kila obj kwenye iter(q.get, Tupu):
            time.sleep(DELTA)
            q.task_done()

    eleza test_task_done(self):
        queue = self.JoinableQueue()

        workers = [self.Process(target=self._test_task_done, args=(queue,))
                   kila i kwenye range(4)]

        kila p kwenye workers:
            p.daemon = Kweli
            p.start()

        kila i kwenye range(10):
            queue.put(i)

        queue.join()

        kila p kwenye workers:
            queue.put(Tupu)

        kila p kwenye workers:
            p.join()
        close_queue(queue)

    eleza test_no_import_lock_contention(self):
        ukijumuisha test.support.temp_cwd():
            module_name = 'imported_by_an_imported_module'
            ukijumuisha open(module_name + '.py', 'w') as f:
                f.write("""ikiwa 1:
                    agiza multiprocessing

                    q = multiprocessing.Queue()
                    q.put('knock knock')
                    q.get(timeout=3)
                    q.close()
                    toa q
                """)

            ukijumuisha test.support.DirsOnSysPath(os.getcwd()):
                jaribu:
                    __import__(module_name)
                except pyqueue.Empty:
                    self.fail("Probable regression on agiza lock contention;"
                              " see Issue #22853")

    eleza test_timeout(self):
        q = multiprocessing.Queue()
        start = time.monotonic()
        self.assertRaises(pyqueue.Empty, q.get, Kweli, 0.200)
        delta = time.monotonic() - start
        # bpo-30317: Tolerate a delta of 100 ms because of the bad clock
        # resolution on Windows (usually 15.6 ms). x86 Windows7 3.x once
        # failed because the delta was only 135.8 ms.
        self.assertGreaterEqual(delta, 0.100)
        close_queue(q)

    eleza test_queue_feeder_donot_stop_onexc(self):
        # bpo-30414: verify feeder handles exceptions correctly
        ikiwa self.TYPE != 'processes':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        kundi NotSerializable(object):
            eleza __reduce__(self):
                 ashiria AttributeError
        ukijumuisha test.support.captured_stderr():
            q = self.Queue()
            q.put(NotSerializable())
            q.put(Kweli)
            self.assertKweli(q.get(timeout=TIMEOUT))
            close_queue(q)

        ukijumuisha test.support.captured_stderr():
            # bpo-33078: verify that the queue size ni correctly handled
            # on errors.
            q = self.Queue(maxsize=1)
            q.put(NotSerializable())
            q.put(Kweli)
            jaribu:
                self.assertEqual(q.qsize(), 1)
            except NotImplementedError:
                # qsize ni sio available on all platform as it
                # relies on sem_getvalue
                pass
            # bpo-30595: use a timeout of 1 second kila slow buildbots
            self.assertKweli(q.get(timeout=1.0))
            # Check that the size of the queue ni correct
            self.assertKweli(q.empty())
            close_queue(q)

    eleza test_queue_feeder_on_queue_feeder_error(self):
        # bpo-30006: verify feeder handles exceptions using the
        # _on_queue_feeder_error hook.
        ikiwa self.TYPE != 'processes':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        kundi NotSerializable(object):
            """Mock unserializable object"""
            eleza __init__(self):
                self.reduce_was_called = Uongo
                self.on_queue_feeder_error_was_called = Uongo

            eleza __reduce__(self):
                self.reduce_was_called = Kweli
                 ashiria AttributeError

        kundi SafeQueue(multiprocessing.queues.Queue):
            """Queue ukijumuisha overloaded _on_queue_feeder_error hook"""
            @staticmethod
            eleza _on_queue_feeder_error(e, obj):
                ikiwa (isinstance(e, AttributeError) and
                        isinstance(obj, NotSerializable)):
                    obj.on_queue_feeder_error_was_called = Kweli

        not_serializable_obj = NotSerializable()
        # The captured_stderr reduces the noise kwenye the test report
        ukijumuisha test.support.captured_stderr():
            q = SafeQueue(ctx=multiprocessing.get_context())
            q.put(not_serializable_obj)

            # Verify that q ni still functioning correctly
            q.put(Kweli)
            self.assertKweli(q.get(timeout=1.0))

        # Assert that the serialization na the hook have been called correctly
        self.assertKweli(not_serializable_obj.reduce_was_called)
        self.assertKweli(not_serializable_obj.on_queue_feeder_error_was_called)

    eleza test_closed_queue_put_get_exceptions(self):
        kila q kwenye multiprocessing.Queue(), multiprocessing.JoinableQueue():
            q.close()
            ukijumuisha self.assertRaisesRegex(ValueError, 'is closed'):
                q.put('foo')
            ukijumuisha self.assertRaisesRegex(ValueError, 'is closed'):
                q.get()
#
#
#

kundi _TestLock(BaseTestCase):

    eleza test_lock(self):
        lock = self.Lock()
        self.assertEqual(lock.acquire(), Kweli)
        self.assertEqual(lock.acquire(Uongo), Uongo)
        self.assertEqual(lock.release(), Tupu)
        self.assertRaises((ValueError, threading.ThreadError), lock.release)

    eleza test_rlock(self):
        lock = self.RLock()
        self.assertEqual(lock.acquire(), Kweli)
        self.assertEqual(lock.acquire(), Kweli)
        self.assertEqual(lock.acquire(), Kweli)
        self.assertEqual(lock.release(), Tupu)
        self.assertEqual(lock.release(), Tupu)
        self.assertEqual(lock.release(), Tupu)
        self.assertRaises((AssertionError, RuntimeError), lock.release)

    eleza test_lock_context(self):
        ukijumuisha self.Lock():
            pass


kundi _TestSemaphore(BaseTestCase):

    eleza _test_semaphore(self, sem):
        self.assertReturnsIfImplemented(2, get_value, sem)
        self.assertEqual(sem.acquire(), Kweli)
        self.assertReturnsIfImplemented(1, get_value, sem)
        self.assertEqual(sem.acquire(), Kweli)
        self.assertReturnsIfImplemented(0, get_value, sem)
        self.assertEqual(sem.acquire(Uongo), Uongo)
        self.assertReturnsIfImplemented(0, get_value, sem)
        self.assertEqual(sem.release(), Tupu)
        self.assertReturnsIfImplemented(1, get_value, sem)
        self.assertEqual(sem.release(), Tupu)
        self.assertReturnsIfImplemented(2, get_value, sem)

    eleza test_semaphore(self):
        sem = self.Semaphore(2)
        self._test_semaphore(sem)
        self.assertEqual(sem.release(), Tupu)
        self.assertReturnsIfImplemented(3, get_value, sem)
        self.assertEqual(sem.release(), Tupu)
        self.assertReturnsIfImplemented(4, get_value, sem)

    eleza test_bounded_semaphore(self):
        sem = self.BoundedSemaphore(2)
        self._test_semaphore(sem)
        # Currently fails on OS/X
        #ikiwa HAVE_GETVALUE:
        #    self.assertRaises(ValueError, sem.release)
        #    self.assertReturnsIfImplemented(2, get_value, sem)

    eleza test_timeout(self):
        ikiwa self.TYPE != 'processes':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        sem = self.Semaphore(0)
        acquire = TimingWrapper(sem.acquire)

        self.assertEqual(acquire(Uongo), Uongo)
        self.assertTimingAlmostEqual(acquire.elapsed, 0.0)

        self.assertEqual(acquire(Uongo, Tupu), Uongo)
        self.assertTimingAlmostEqual(acquire.elapsed, 0.0)

        self.assertEqual(acquire(Uongo, TIMEOUT1), Uongo)
        self.assertTimingAlmostEqual(acquire.elapsed, 0)

        self.assertEqual(acquire(Kweli, TIMEOUT2), Uongo)
        self.assertTimingAlmostEqual(acquire.elapsed, TIMEOUT2)

        self.assertEqual(acquire(timeout=TIMEOUT3), Uongo)
        self.assertTimingAlmostEqual(acquire.elapsed, TIMEOUT3)


kundi _TestCondition(BaseTestCase):

    @classmethod
    eleza f(cls, cond, sleeping, woken, timeout=Tupu):
        cond.acquire()
        sleeping.release()
        cond.wait(timeout)
        woken.release()
        cond.release()

    eleza assertReachesEventually(self, func, value):
        kila i kwenye range(10):
            jaribu:
                ikiwa func() == value:
                    koma
            except NotImplementedError:
                koma
            time.sleep(DELTA)
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(value, func)

    eleza check_invariant(self, cond):
        # this ni only supposed to succeed when there are no sleepers
        ikiwa self.TYPE == 'processes':
            jaribu:
                sleepers = (cond._sleeping_count.get_value() -
                            cond._woken_count.get_value())
                self.assertEqual(sleepers, 0)
                self.assertEqual(cond._wait_semaphore.get_value(), 0)
            except NotImplementedError:
                pass

    eleza test_notify(self):
        cond = self.Condition()
        sleeping = self.Semaphore(0)
        woken = self.Semaphore(0)

        p = self.Process(target=self.f, args=(cond, sleeping, woken))
        p.daemon = Kweli
        p.start()
        self.addCleanup(p.join)

        p = threading.Thread(target=self.f, args=(cond, sleeping, woken))
        p.daemon = Kweli
        p.start()
        self.addCleanup(p.join)

        # wait kila both children to start sleeping
        sleeping.acquire()
        sleeping.acquire()

        # check no process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(0, get_value, woken)

        # wake up one process/thread
        cond.acquire()
        cond.notify()
        cond.release()

        # check one process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(1, get_value, woken)

        # wake up another
        cond.acquire()
        cond.notify()
        cond.release()

        # check other has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(2, get_value, woken)

        # check state ni sio mucked up
        self.check_invariant(cond)
        p.join()

    eleza test_notify_all(self):
        cond = self.Condition()
        sleeping = self.Semaphore(0)
        woken = self.Semaphore(0)

        # start some threads/processes which will timeout
        kila i kwenye range(3):
            p = self.Process(target=self.f,
                             args=(cond, sleeping, woken, TIMEOUT1))
            p.daemon = Kweli
            p.start()
            self.addCleanup(p.join)

            t = threading.Thread(target=self.f,
                                 args=(cond, sleeping, woken, TIMEOUT1))
            t.daemon = Kweli
            t.start()
            self.addCleanup(t.join)

        # wait kila them all to sleep
        kila i kwenye range(6):
            sleeping.acquire()

        # check they have all timed out
        kila i kwenye range(6):
            woken.acquire()
        self.assertReturnsIfImplemented(0, get_value, woken)

        # check state ni sio mucked up
        self.check_invariant(cond)

        # start some more threads/processes
        kila i kwenye range(3):
            p = self.Process(target=self.f, args=(cond, sleeping, woken))
            p.daemon = Kweli
            p.start()
            self.addCleanup(p.join)

            t = threading.Thread(target=self.f, args=(cond, sleeping, woken))
            t.daemon = Kweli
            t.start()
            self.addCleanup(t.join)

        # wait kila them to all sleep
        kila i kwenye range(6):
            sleeping.acquire()

        # check no process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(0, get_value, woken)

        # wake them all up
        cond.acquire()
        cond.notify_all()
        cond.release()

        # check they have all woken
        self.assertReachesEventually(lambda: get_value(woken), 6)

        # check state ni sio mucked up
        self.check_invariant(cond)

    eleza test_notify_n(self):
        cond = self.Condition()
        sleeping = self.Semaphore(0)
        woken = self.Semaphore(0)

        # start some threads/processes
        kila i kwenye range(3):
            p = self.Process(target=self.f, args=(cond, sleeping, woken))
            p.daemon = Kweli
            p.start()
            self.addCleanup(p.join)

            t = threading.Thread(target=self.f, args=(cond, sleeping, woken))
            t.daemon = Kweli
            t.start()
            self.addCleanup(t.join)

        # wait kila them to all sleep
        kila i kwenye range(6):
            sleeping.acquire()

        # check no process/thread has woken up
        time.sleep(DELTA)
        self.assertReturnsIfImplemented(0, get_value, woken)

        # wake some of them up
        cond.acquire()
        cond.notify(n=2)
        cond.release()

        # check 2 have woken
        self.assertReachesEventually(lambda: get_value(woken), 2)

        # wake the rest of them
        cond.acquire()
        cond.notify(n=4)
        cond.release()

        self.assertReachesEventually(lambda: get_value(woken), 6)

        # doesn't do anything more
        cond.acquire()
        cond.notify(n=3)
        cond.release()

        self.assertReturnsIfImplemented(6, get_value, woken)

        # check state ni sio mucked up
        self.check_invariant(cond)

    eleza test_timeout(self):
        cond = self.Condition()
        wait = TimingWrapper(cond.wait)
        cond.acquire()
        res = wait(TIMEOUT1)
        cond.release()
        self.assertEqual(res, Uongo)
        self.assertTimingAlmostEqual(wait.elapsed, TIMEOUT1)

    @classmethod
    eleza _test_waitfor_f(cls, cond, state):
        ukijumuisha cond:
            state.value = 0
            cond.notify()
            result = cond.wait_for(lambda : state.value==4)
            ikiwa sio result ama state.value != 4:
                sys.exit(1)

    @unittest.skipUnless(HAS_SHAREDCTYPES, 'needs sharedctypes')
    eleza test_waitfor(self):
        # based on test kwenye test/lock_tests.py
        cond = self.Condition()
        state = self.Value('i', -1)

        p = self.Process(target=self._test_waitfor_f, args=(cond, state))
        p.daemon = Kweli
        p.start()

        ukijumuisha cond:
            result = cond.wait_for(lambda : state.value==0)
            self.assertKweli(result)
            self.assertEqual(state.value, 0)

        kila i kwenye range(4):
            time.sleep(0.01)
            ukijumuisha cond:
                state.value += 1
                cond.notify()

        join_process(p)
        self.assertEqual(p.exitcode, 0)

    @classmethod
    eleza _test_waitfor_timeout_f(cls, cond, state, success, sem):
        sem.release()
        ukijumuisha cond:
            expected = 0.1
            dt = time.monotonic()
            result = cond.wait_for(lambda : state.value==4, timeout=expected)
            dt = time.monotonic() - dt
            # borrow logic kwenye assertTimeout() kutoka test/lock_tests.py
            ikiwa sio result na expected * 0.6 < dt < expected * 10.0:
                success.value = Kweli

    @unittest.skipUnless(HAS_SHAREDCTYPES, 'needs sharedctypes')
    eleza test_waitfor_timeout(self):
        # based on test kwenye test/lock_tests.py
        cond = self.Condition()
        state = self.Value('i', 0)
        success = self.Value('i', Uongo)
        sem = self.Semaphore(0)

        p = self.Process(target=self._test_waitfor_timeout_f,
                         args=(cond, state, success, sem))
        p.daemon = Kweli
        p.start()
        self.assertKweli(sem.acquire(timeout=TIMEOUT))

        # Only increment 3 times, so state == 4 ni never reached.
        kila i kwenye range(3):
            time.sleep(0.01)
            ukijumuisha cond:
                state.value += 1
                cond.notify()

        join_process(p)
        self.assertKweli(success.value)

    @classmethod
    eleza _test_wait_result(cls, c, pid):
        ukijumuisha c:
            c.notify()
        time.sleep(1)
        ikiwa pid ni sio Tupu:
            os.kill(pid, signal.SIGINT)

    eleza test_wait_result(self):
        ikiwa isinstance(self, ProcessesMixin) na sys.platform != 'win32':
            pid = os.getpid()
        isipokua:
            pid = Tupu

        c = self.Condition()
        ukijumuisha c:
            self.assertUongo(c.wait(0))
            self.assertUongo(c.wait(0.1))

            p = self.Process(target=self._test_wait_result, args=(c, pid))
            p.start()

            self.assertKweli(c.wait(60))
            ikiwa pid ni sio Tupu:
                self.assertRaises(KeyboardInterrupt, c.wait, 60)

            p.join()


kundi _TestEvent(BaseTestCase):

    @classmethod
    eleza _test_event(cls, event):
        time.sleep(TIMEOUT2)
        event.set()

    eleza test_event(self):
        event = self.Event()
        wait = TimingWrapper(event.wait)

        # Removed temporarily, due to API shear, this does not
        # work ukijumuisha threading._Event objects. is_set == isSet
        self.assertEqual(event.is_set(), Uongo)

        # Removed, threading.Event.wait() will rudisha the value of the __flag
        # instead of Tupu. API Shear ukijumuisha the semaphore backed mp.Event
        self.assertEqual(wait(0.0), Uongo)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        self.assertEqual(wait(TIMEOUT1), Uongo)
        self.assertTimingAlmostEqual(wait.elapsed, TIMEOUT1)

        event.set()

        # See note above on the API differences
        self.assertEqual(event.is_set(), Kweli)
        self.assertEqual(wait(), Kweli)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        self.assertEqual(wait(TIMEOUT1), Kweli)
        self.assertTimingAlmostEqual(wait.elapsed, 0.0)
        # self.assertEqual(event.is_set(), Kweli)

        event.clear()

        #self.assertEqual(event.is_set(), Uongo)

        p = self.Process(target=self._test_event, args=(event,))
        p.daemon = Kweli
        p.start()
        self.assertEqual(wait(), Kweli)
        p.join()

#
# Tests kila Barrier - adapted kutoka tests kwenye test/lock_tests.py
#

# Many of the tests kila threading.Barrier use a list as an atomic
# counter: a value ni appended to increment the counter, na the
# length of the list gives the value.  We use the kundi DummyList
# kila the same purpose.

kundi _DummyList(object):

    eleza __init__(self):
        wrapper = multiprocessing.heap.BufferWrapper(struct.calcsize('i'))
        lock = multiprocessing.Lock()
        self.__setstate__((wrapper, lock))
        self._lengthbuf[0] = 0

    eleza __setstate__(self, state):
        (self._wrapper, self._lock) = state
        self._lengthbuf = self._wrapper.create_memoryview().cast('i')

    eleza __getstate__(self):
        rudisha (self._wrapper, self._lock)

    eleza append(self, _):
        ukijumuisha self._lock:
            self._lengthbuf[0] += 1

    eleza __len__(self):
        ukijumuisha self._lock:
            rudisha self._lengthbuf[0]

eleza _wait():
    # A crude wait/tuma function sio relying on synchronization primitives.
    time.sleep(0.01)


kundi Bunch(object):
    """
    A bunch of threads.
    """
    eleza __init__(self, namespace, f, args, n, wait_before_exit=Uongo):
        """
        Construct a bunch of `n` threads running the same function `f`.
        If `wait_before_exit` ni Kweli, the threads won't terminate until
        do_finish() ni called.
        """
        self.f = f
        self.args = args
        self.n = n
        self.started = namespace.DummyList()
        self.finished = namespace.DummyList()
        self._can_exit = namespace.Event()
        ikiwa sio wait_before_exit:
            self._can_exit.set()

        threads = []
        kila i kwenye range(n):
            p = namespace.Process(target=self.task)
            p.daemon = Kweli
            p.start()
            threads.append(p)

        eleza finalize(threads):
            kila p kwenye threads:
                p.join()

        self._finalizer = weakref.finalize(self, finalize, threads)

    eleza task(self):
        pid = os.getpid()
        self.started.append(pid)
        jaribu:
            self.f(*self.args)
        mwishowe:
            self.finished.append(pid)
            self._can_exit.wait(30)
            assert self._can_exit.is_set()

    eleza wait_for_started(self):
        wakati len(self.started) < self.n:
            _wait()

    eleza wait_for_finished(self):
        wakati len(self.finished) < self.n:
            _wait()

    eleza do_finish(self):
        self._can_exit.set()

    eleza close(self):
        self._finalizer()


kundi AppendKweli(object):
    eleza __init__(self, obj):
        self.obj = obj
    eleza __call__(self):
        self.obj.append(Kweli)


kundi _TestBarrier(BaseTestCase):
    """
    Tests kila Barrier objects.
    """
    N = 5
    defaultTimeout = 30.0  # XXX Slow Windows buildbots need generous timeout

    eleza setUp(self):
        self.barrier = self.Barrier(self.N, timeout=self.defaultTimeout)

    eleza tearDown(self):
        self.barrier.abort()
        self.barrier = Tupu

    eleza DummyList(self):
        ikiwa self.TYPE == 'threads':
            rudisha []
        elikiwa self.TYPE == 'manager':
            rudisha self.manager.list()
        isipokua:
            rudisha _DummyList()

    eleza run_threads(self, f, args):
        b = Bunch(self, f, args, self.N-1)
        jaribu:
            f(*args)
            b.wait_for_finished()
        mwishowe:
            b.close()

    @classmethod
    eleza multipass(cls, barrier, results, n):
        m = barrier.parties
        assert m == cls.N
        kila i kwenye range(n):
            results[0].append(Kweli)
            assert len(results[1]) == i * m
            barrier.wait()
            results[1].append(Kweli)
            assert len(results[0]) == (i + 1) * m
            barrier.wait()
        jaribu:
            assert barrier.n_waiting == 0
        except NotImplementedError:
            pass
        assert sio barrier.broken

    eleza test_barrier(self, passes=1):
        """
        Test that a barrier ni passed kwenye lockstep
        """
        results = [self.DummyList(), self.DummyList()]
        self.run_threads(self.multipass, (self.barrier, results, passes))

    eleza test_barrier_10(self):
        """
        Test that a barrier works kila 10 consecutive runs
        """
        rudisha self.test_barrier(10)

    @classmethod
    eleza _test_wait_return_f(cls, barrier, queue):
        res = barrier.wait()
        queue.put(res)

    eleza test_wait_return(self):
        """
        test the rudisha value kutoka barrier.wait
        """
        queue = self.Queue()
        self.run_threads(self._test_wait_return_f, (self.barrier, queue))
        results = [queue.get() kila i kwenye range(self.N)]
        self.assertEqual(results.count(0), 1)
        close_queue(queue)

    @classmethod
    eleza _test_action_f(cls, barrier, results):
        barrier.wait()
        ikiwa len(results) != 1:
             ashiria RuntimeError

    eleza test_action(self):
        """
        Test the 'action' callback
        """
        results = self.DummyList()
        barrier = self.Barrier(self.N, action=AppendKweli(results))
        self.run_threads(self._test_action_f, (barrier, results))
        self.assertEqual(len(results), 1)

    @classmethod
    eleza _test_abort_f(cls, barrier, results1, results2):
        jaribu:
            i = barrier.wait()
            ikiwa i == cls.N//2:
                 ashiria RuntimeError
            barrier.wait()
            results1.append(Kweli)
        except threading.BrokenBarrierError:
            results2.append(Kweli)
        except RuntimeError:
            barrier.abort()

    eleza test_abort(self):
        """
        Test that an abort will put the barrier kwenye a broken state
        """
        results1 = self.DummyList()
        results2 = self.DummyList()
        self.run_threads(self._test_abort_f,
                         (self.barrier, results1, results2))
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertKweli(self.barrier.broken)

    @classmethod
    eleza _test_reset_f(cls, barrier, results1, results2, results3):
        i = barrier.wait()
        ikiwa i == cls.N//2:
            # Wait until the other threads are all kwenye the barrier.
            wakati barrier.n_waiting < cls.N-1:
                time.sleep(0.001)
            barrier.reset()
        isipokua:
            jaribu:
                barrier.wait()
                results1.append(Kweli)
            except threading.BrokenBarrierError:
                results2.append(Kweli)
        # Now, pass the barrier again
        barrier.wait()
        results3.append(Kweli)

    eleza test_reset(self):
        """
        Test that a 'reset' on a barrier frees the waiting threads
        """
        results1 = self.DummyList()
        results2 = self.DummyList()
        results3 = self.DummyList()
        self.run_threads(self._test_reset_f,
                         (self.barrier, results1, results2, results3))
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertEqual(len(results3), self.N)

    @classmethod
    eleza _test_abort_and_reset_f(cls, barrier, barrier2,
                                results1, results2, results3):
        jaribu:
            i = barrier.wait()
            ikiwa i == cls.N//2:
                 ashiria RuntimeError
            barrier.wait()
            results1.append(Kweli)
        except threading.BrokenBarrierError:
            results2.append(Kweli)
        except RuntimeError:
            barrier.abort()
        # Synchronize na reset the barrier.  Must synchronize first so
        # that everyone has left it when we reset, na after so that no
        # one enters it before the reset.
        ikiwa barrier2.wait() == cls.N//2:
            barrier.reset()
        barrier2.wait()
        barrier.wait()
        results3.append(Kweli)

    eleza test_abort_and_reset(self):
        """
        Test that a barrier can be reset after being broken.
        """
        results1 = self.DummyList()
        results2 = self.DummyList()
        results3 = self.DummyList()
        barrier2 = self.Barrier(self.N)

        self.run_threads(self._test_abort_and_reset_f,
                         (self.barrier, barrier2, results1, results2, results3))
        self.assertEqual(len(results1), 0)
        self.assertEqual(len(results2), self.N-1)
        self.assertEqual(len(results3), self.N)

    @classmethod
    eleza _test_timeout_f(cls, barrier, results):
        i = barrier.wait()
        ikiwa i == cls.N//2:
            # One thread ni late!
            time.sleep(1.0)
        jaribu:
            barrier.wait(0.5)
        except threading.BrokenBarrierError:
            results.append(Kweli)

    eleza test_timeout(self):
        """
        Test wait(timeout)
        """
        results = self.DummyList()
        self.run_threads(self._test_timeout_f, (self.barrier, results))
        self.assertEqual(len(results), self.barrier.parties)

    @classmethod
    eleza _test_default_timeout_f(cls, barrier, results):
        i = barrier.wait(cls.defaultTimeout)
        ikiwa i == cls.N//2:
            # One thread ni later than the default timeout
            time.sleep(1.0)
        jaribu:
            barrier.wait()
        except threading.BrokenBarrierError:
            results.append(Kweli)

    eleza test_default_timeout(self):
        """
        Test the barrier's default timeout
        """
        barrier = self.Barrier(self.N, timeout=0.5)
        results = self.DummyList()
        self.run_threads(self._test_default_timeout_f, (barrier, results))
        self.assertEqual(len(results), barrier.parties)

    eleza test_single_thread(self):
        b = self.Barrier(1)
        b.wait()
        b.wait()

    @classmethod
    eleza _test_thousand_f(cls, barrier, passes, conn, lock):
        kila i kwenye range(passes):
            barrier.wait()
            ukijumuisha lock:
                conn.send(i)

    eleza test_thousand(self):
        ikiwa self.TYPE == 'manager':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))
        passes = 1000
        lock = self.Lock()
        conn, child_conn = self.Pipe(Uongo)
        kila j kwenye range(self.N):
            p = self.Process(target=self._test_thousand_f,
                           args=(self.barrier, passes, child_conn, lock))
            p.start()
            self.addCleanup(p.join)

        kila i kwenye range(passes):
            kila j kwenye range(self.N):
                self.assertEqual(conn.recv(), i)

#
#
#

kundi _TestValue(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    codes_values = [
        ('i', 4343, 24234),
        ('d', 3.625, -4.25),
        ('h', -232, 234),
        ('q', 2 ** 33, 2 ** 34),
        ('c', latin('x'), latin('y'))
        ]

    eleza setUp(self):
        ikiwa sio HAS_SHAREDCTYPES:
            self.skipTest("requires multiprocessing.sharedctypes")

    @classmethod
    eleza _test(cls, values):
        kila sv, cv kwenye zip(values, cls.codes_values):
            sv.value = cv[2]


    eleza test_value(self, raw=Uongo):
        ikiwa raw:
            values = [self.RawValue(code, value)
                      kila code, value, _ kwenye self.codes_values]
        isipokua:
            values = [self.Value(code, value)
                      kila code, value, _ kwenye self.codes_values]

        kila sv, cv kwenye zip(values, self.codes_values):
            self.assertEqual(sv.value, cv[1])

        proc = self.Process(target=self._test, args=(values,))
        proc.daemon = Kweli
        proc.start()
        proc.join()

        kila sv, cv kwenye zip(values, self.codes_values):
            self.assertEqual(sv.value, cv[2])

    eleza test_rawvalue(self):
        self.test_value(raw=Kweli)

    eleza test_getobj_getlock(self):
        val1 = self.Value('i', 5)
        lock1 = val1.get_lock()
        obj1 = val1.get_obj()

        val2 = self.Value('i', 5, lock=Tupu)
        lock2 = val2.get_lock()
        obj2 = val2.get_obj()

        lock = self.Lock()
        val3 = self.Value('i', 5, lock=lock)
        lock3 = val3.get_lock()
        obj3 = val3.get_obj()
        self.assertEqual(lock, lock3)

        arr4 = self.Value('i', 5, lock=Uongo)
        self.assertUongo(hasattr(arr4, 'get_lock'))
        self.assertUongo(hasattr(arr4, 'get_obj'))

        self.assertRaises(AttributeError, self.Value, 'i', 5, lock='navalue')

        arr5 = self.RawValue('i', 5)
        self.assertUongo(hasattr(arr5, 'get_lock'))
        self.assertUongo(hasattr(arr5, 'get_obj'))


kundi _TestArray(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    @classmethod
    eleza f(cls, seq):
        kila i kwenye range(1, len(seq)):
            seq[i] += seq[i-1]

    @unittest.skipIf(c_int ni Tupu, "requires _ctypes")
    eleza test_array(self, raw=Uongo):
        seq = [680, 626, 934, 821, 150, 233, 548, 982, 714, 831]
        ikiwa raw:
            arr = self.RawArray('i', seq)
        isipokua:
            arr = self.Array('i', seq)

        self.assertEqual(len(arr), len(seq))
        self.assertEqual(arr[3], seq[3])
        self.assertEqual(list(arr[2:7]), list(seq[2:7]))

        arr[4:8] = seq[4:8] = array.array('i', [1, 2, 3, 4])

        self.assertEqual(list(arr[:]), seq)

        self.f(seq)

        p = self.Process(target=self.f, args=(arr,))
        p.daemon = Kweli
        p.start()
        p.join()

        self.assertEqual(list(arr[:]), seq)

    @unittest.skipIf(c_int ni Tupu, "requires _ctypes")
    eleza test_array_from_size(self):
        size = 10
        # Test kila zeroing (see issue #11675).
        # The repetition below strengthens the test by increasing the chances
        # of previously allocated non-zero memory being used kila the new array
        # on the 2nd na 3rd loops.
        kila _ kwenye range(3):
            arr = self.Array('i', size)
            self.assertEqual(len(arr), size)
            self.assertEqual(list(arr), [0] * size)
            arr[:] = range(10)
            self.assertEqual(list(arr), list(range(10)))
            toa arr

    @unittest.skipIf(c_int ni Tupu, "requires _ctypes")
    eleza test_rawarray(self):
        self.test_array(raw=Kweli)

    @unittest.skipIf(c_int ni Tupu, "requires _ctypes")
    eleza test_getobj_getlock_obj(self):
        arr1 = self.Array('i', list(range(10)))
        lock1 = arr1.get_lock()
        obj1 = arr1.get_obj()

        arr2 = self.Array('i', list(range(10)), lock=Tupu)
        lock2 = arr2.get_lock()
        obj2 = arr2.get_obj()

        lock = self.Lock()
        arr3 = self.Array('i', list(range(10)), lock=lock)
        lock3 = arr3.get_lock()
        obj3 = arr3.get_obj()
        self.assertEqual(lock, lock3)

        arr4 = self.Array('i', range(10), lock=Uongo)
        self.assertUongo(hasattr(arr4, 'get_lock'))
        self.assertUongo(hasattr(arr4, 'get_obj'))
        self.assertRaises(AttributeError,
                          self.Array, 'i', range(10), lock='notalock')

        arr5 = self.RawArray('i', range(10))
        self.assertUongo(hasattr(arr5, 'get_lock'))
        self.assertUongo(hasattr(arr5, 'get_obj'))

#
#
#

kundi _TestContainers(BaseTestCase):

    ALLOWED_TYPES = ('manager',)

    eleza test_list(self):
        a = self.list(list(range(10)))
        self.assertEqual(a[:], list(range(10)))

        b = self.list()
        self.assertEqual(b[:], [])

        b.extend(list(range(5)))
        self.assertEqual(b[:], list(range(5)))

        self.assertEqual(b[2], 2)
        self.assertEqual(b[2:10], [2,3,4])

        b *= 2
        self.assertEqual(b[:], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4])

        self.assertEqual(b + [5, 6], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5, 6])

        self.assertEqual(a[:], list(range(10)))

        d = [a, b]
        e = self.list(d)
        self.assertEqual(
            [element[:] kila element kwenye e],
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]]
            )

        f = self.list([a])
        a.append('hello')
        self.assertEqual(f[0][:], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'hello'])

    eleza test_list_iter(self):
        a = self.list(list(range(10)))
        it = iter(a)
        self.assertEqual(list(it), list(range(10)))
        self.assertEqual(list(it), [])  # exhausted
        # list modified during iteration
        it = iter(a)
        a[0] = 100
        self.assertEqual(next(it), 100)

    eleza test_list_proxy_in_list(self):
        a = self.list([self.list(range(3)) kila _i kwenye range(3)])
        self.assertEqual([inner[:] kila inner kwenye a], [[0, 1, 2]] * 3)

        a[0][-1] = 55
        self.assertEqual(a[0][:], [0, 1, 55])
        kila i kwenye range(1, 3):
            self.assertEqual(a[i][:], [0, 1, 2])

        self.assertEqual(a[1].pop(), 2)
        self.assertEqual(len(a[1]), 2)
        kila i kwenye range(0, 3, 2):
            self.assertEqual(len(a[i]), 3)

        toa a

        b = self.list()
        b.append(b)
        toa b

    eleza test_dict(self):
        d = self.dict()
        indices = list(range(65, 70))
        kila i kwenye indices:
            d[i] = chr(i)
        self.assertEqual(d.copy(), dict((i, chr(i)) kila i kwenye indices))
        self.assertEqual(sorted(d.keys()), indices)
        self.assertEqual(sorted(d.values()), [chr(i) kila i kwenye indices])
        self.assertEqual(sorted(d.items()), [(i, chr(i)) kila i kwenye indices])

    eleza test_dict_iter(self):
        d = self.dict()
        indices = list(range(65, 70))
        kila i kwenye indices:
            d[i] = chr(i)
        it = iter(d)
        self.assertEqual(list(it), indices)
        self.assertEqual(list(it), [])  # exhausted
        # dictionary changed size during iteration
        it = iter(d)
        d.clear()
        self.assertRaises(RuntimeError, next, it)

    eleza test_dict_proxy_nested(self):
        pets = self.dict(ferrets=2, hamsters=4)
        supplies = self.dict(water=10, feed=3)
        d = self.dict(pets=pets, supplies=supplies)

        self.assertEqual(supplies['water'], 10)
        self.assertEqual(d['supplies']['water'], 10)

        d['supplies']['blankets'] = 5
        self.assertEqual(supplies['blankets'], 5)
        self.assertEqual(d['supplies']['blankets'], 5)

        d['supplies']['water'] = 7
        self.assertEqual(supplies['water'], 7)
        self.assertEqual(d['supplies']['water'], 7)

        toa pets
        toa supplies
        self.assertEqual(d['pets']['ferrets'], 2)
        d['supplies']['blankets'] = 11
        self.assertEqual(d['supplies']['blankets'], 11)

        pets = d['pets']
        supplies = d['supplies']
        supplies['water'] = 7
        self.assertEqual(supplies['water'], 7)
        self.assertEqual(d['supplies']['water'], 7)

        d.clear()
        self.assertEqual(len(d), 0)
        self.assertEqual(supplies['water'], 7)
        self.assertEqual(pets['hamsters'], 4)

        l = self.list([pets, supplies])
        l[0]['marmots'] = 1
        self.assertEqual(pets['marmots'], 1)
        self.assertEqual(l[0]['marmots'], 1)

        toa pets
        toa supplies
        self.assertEqual(l[0]['marmots'], 1)

        outer = self.list([[88, 99], l])
        self.assertIsInstance(outer[0], list)  # Not a ListProxy
        self.assertEqual(outer[-1][-1]['feed'], 3)

    eleza test_namespace(self):
        n = self.Namespace()
        n.name = 'Bob'
        n.job = 'Builder'
        n._hidden = 'hidden'
        self.assertEqual((n.name, n.job), ('Bob', 'Builder'))
        toa n.job
        self.assertEqual(str(n), "Namespace(name='Bob')")
        self.assertKweli(hasattr(n, 'name'))
        self.assertKweli(not hasattr(n, 'job'))

#
#
#

eleza sqr(x, wait=0.0):
    time.sleep(wait)
    rudisha x*x

eleza mul(x, y):
    rudisha x*y

eleza raise_large_valuerror(wait):
    time.sleep(wait)
     ashiria ValueError("x" * 1024**2)

eleza identity(x):
    rudisha x

kundi CountedObject(object):
    n_instances = 0

    eleza __new__(cls):
        cls.n_instances += 1
        rudisha object.__new__(cls)

    eleza __del__(self):
        type(self).n_instances -= 1

kundi SayWhenError(ValueError): pass

eleza exception_throwing_generator(total, when):
    ikiwa when == -1:
         ashiria SayWhenError("Somebody said when")
    kila i kwenye range(total):
        ikiwa i == when:
             ashiria SayWhenError("Somebody said when")
        tuma i


kundi _TestPool(BaseTestCase):

    @classmethod
    eleza setUpClass(cls):
        super().setUpClass()
        cls.pool = cls.Pool(4)

    @classmethod
    eleza tearDownClass(cls):
        cls.pool.terminate()
        cls.pool.join()
        cls.pool = Tupu
        super().tearDownClass()

    eleza test_apply(self):
        papply = self.pool.apply
        self.assertEqual(papply(sqr, (5,)), sqr(5))
        self.assertEqual(papply(sqr, (), {'x':3}), sqr(x=3))

    eleza test_map(self):
        pmap = self.pool.map
        self.assertEqual(pmap(sqr, list(range(10))), list(map(sqr, list(range(10)))))
        self.assertEqual(pmap(sqr, list(range(100)), chunksize=20),
                         list(map(sqr, list(range(100)))))

    eleza test_starmap(self):
        psmap = self.pool.starmap
        tuples = list(zip(range(10), range(9,-1, -1)))
        self.assertEqual(psmap(mul, tuples),
                         list(itertools.starmap(mul, tuples)))
        tuples = list(zip(range(100), range(99,-1, -1)))
        self.assertEqual(psmap(mul, tuples, chunksize=20),
                         list(itertools.starmap(mul, tuples)))

    eleza test_starmap_async(self):
        tuples = list(zip(range(100), range(99,-1, -1)))
        self.assertEqual(self.pool.starmap_async(mul, tuples).get(),
                         list(itertools.starmap(mul, tuples)))

    eleza test_map_async(self):
        self.assertEqual(self.pool.map_async(sqr, list(range(10))).get(),
                         list(map(sqr, list(range(10)))))

    eleza test_map_async_callbacks(self):
        call_args = self.manager.list() ikiwa self.TYPE == 'manager' isipokua []
        self.pool.map_async(int, ['1'],
                            callback=call_args.append,
                            error_callback=call_args.append).wait()
        self.assertEqual(1, len(call_args))
        self.assertEqual([1], call_args[0])
        self.pool.map_async(int, ['a'],
                            callback=call_args.append,
                            error_callback=call_args.append).wait()
        self.assertEqual(2, len(call_args))
        self.assertIsInstance(call_args[1], ValueError)

    eleza test_map_unplicklable(self):
        # Issue #19425 -- failure to pickle should sio cause a hang
        ikiwa self.TYPE == 'threads':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))
        kundi A(object):
            eleza __reduce__(self):
                 ashiria RuntimeError('cannot pickle')
        ukijumuisha self.assertRaises(RuntimeError):
            self.pool.map(sqr, [A()]*10)

    eleza test_map_chunksize(self):
        jaribu:
            self.pool.map_async(sqr, [], chunksize=1).get(timeout=TIMEOUT1)
        except multiprocessing.TimeoutError:
            self.fail("pool.map_async ukijumuisha chunksize stalled on null list")

    eleza test_map_handle_iterable_exception(self):
        ikiwa self.TYPE == 'manager':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        # SayWhenError seen at the very first of the iterable
        ukijumuisha self.assertRaises(SayWhenError):
            self.pool.map(sqr, exception_throwing_generator(1, -1), 1)
        # again, make sure it's reentrant
        ukijumuisha self.assertRaises(SayWhenError):
            self.pool.map(sqr, exception_throwing_generator(1, -1), 1)

        ukijumuisha self.assertRaises(SayWhenError):
            self.pool.map(sqr, exception_throwing_generator(10, 3), 1)

        kundi SpecialIterable:
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                 ashiria SayWhenError
            eleza __len__(self):
                rudisha 1
        ukijumuisha self.assertRaises(SayWhenError):
            self.pool.map(sqr, SpecialIterable(), 1)
        ukijumuisha self.assertRaises(SayWhenError):
            self.pool.map(sqr, SpecialIterable(), 1)

    eleza test_async(self):
        res = self.pool.apply_async(sqr, (7, TIMEOUT1,))
        get = TimingWrapper(res.get)
        self.assertEqual(get(), 49)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT1)

    eleza test_async_timeout(self):
        res = self.pool.apply_async(sqr, (6, TIMEOUT2 + 1.0))
        get = TimingWrapper(res.get)
        self.assertRaises(multiprocessing.TimeoutError, get, timeout=TIMEOUT2)
        self.assertTimingAlmostEqual(get.elapsed, TIMEOUT2)

    eleza test_imap(self):
        it = self.pool.imap(sqr, list(range(10)))
        self.assertEqual(list(it), list(map(sqr, list(range(10)))))

        it = self.pool.imap(sqr, list(range(10)))
        kila i kwenye range(10):
            self.assertEqual(next(it), i*i)
        self.assertRaises(StopIteration, it.__next__)

        it = self.pool.imap(sqr, list(range(1000)), chunksize=100)
        kila i kwenye range(1000):
            self.assertEqual(next(it), i*i)
        self.assertRaises(StopIteration, it.__next__)

    eleza test_imap_handle_iterable_exception(self):
        ikiwa self.TYPE == 'manager':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        # SayWhenError seen at the very first of the iterable
        it = self.pool.imap(sqr, exception_throwing_generator(1, -1), 1)
        self.assertRaises(SayWhenError, it.__next__)
        # again, make sure it's reentrant
        it = self.pool.imap(sqr, exception_throwing_generator(1, -1), 1)
        self.assertRaises(SayWhenError, it.__next__)

        it = self.pool.imap(sqr, exception_throwing_generator(10, 3), 1)
        kila i kwenye range(3):
            self.assertEqual(next(it), i*i)
        self.assertRaises(SayWhenError, it.__next__)

        # SayWhenError seen at start of problematic chunk's results
        it = self.pool.imap(sqr, exception_throwing_generator(20, 7), 2)
        kila i kwenye range(6):
            self.assertEqual(next(it), i*i)
        self.assertRaises(SayWhenError, it.__next__)
        it = self.pool.imap(sqr, exception_throwing_generator(20, 7), 4)
        kila i kwenye range(4):
            self.assertEqual(next(it), i*i)
        self.assertRaises(SayWhenError, it.__next__)

    eleza test_imap_unordered(self):
        it = self.pool.imap_unordered(sqr, list(range(10)))
        self.assertEqual(sorted(it), list(map(sqr, list(range(10)))))

        it = self.pool.imap_unordered(sqr, list(range(1000)), chunksize=100)
        self.assertEqual(sorted(it), list(map(sqr, list(range(1000)))))

    eleza test_imap_unordered_handle_iterable_exception(self):
        ikiwa self.TYPE == 'manager':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        # SayWhenError seen at the very first of the iterable
        it = self.pool.imap_unordered(sqr,
                                      exception_throwing_generator(1, -1),
                                      1)
        self.assertRaises(SayWhenError, it.__next__)
        # again, make sure it's reentrant
        it = self.pool.imap_unordered(sqr,
                                      exception_throwing_generator(1, -1),
                                      1)
        self.assertRaises(SayWhenError, it.__next__)

        it = self.pool.imap_unordered(sqr,
                                      exception_throwing_generator(10, 3),
                                      1)
        expected_values = list(map(sqr, list(range(10))))
        ukijumuisha self.assertRaises(SayWhenError):
            # imap_unordered makes it difficult to anticipate the SayWhenError
            kila i kwenye range(10):
                value = next(it)
                self.assertIn(value, expected_values)
                expected_values.remove(value)

        it = self.pool.imap_unordered(sqr,
                                      exception_throwing_generator(20, 7),
                                      2)
        expected_values = list(map(sqr, list(range(20))))
        ukijumuisha self.assertRaises(SayWhenError):
            kila i kwenye range(20):
                value = next(it)
                self.assertIn(value, expected_values)
                expected_values.remove(value)

    eleza test_make_pool(self):
        expected_error = (RemoteError ikiwa self.TYPE == 'manager'
                          isipokua ValueError)

        self.assertRaises(expected_error, self.Pool, -1)
        self.assertRaises(expected_error, self.Pool, 0)

        ikiwa self.TYPE != 'manager':
            p = self.Pool(3)
            jaribu:
                self.assertEqual(3, len(p._pool))
            mwishowe:
                p.close()
                p.join()

    eleza test_terminate(self):
        result = self.pool.map_async(
            time.sleep, [0.1 kila i kwenye range(10000)], chunksize=1
            )
        self.pool.terminate()
        join = TimingWrapper(self.pool.join)
        join()
        # Sanity check the pool didn't wait kila all tasks to finish
        self.assertLess(join.elapsed, 2.0)

    eleza test_empty_iterable(self):
        # See Issue 12157
        p = self.Pool(1)

        self.assertEqual(p.map(sqr, []), [])
        self.assertEqual(list(p.imap(sqr, [])), [])
        self.assertEqual(list(p.imap_unordered(sqr, [])), [])
        self.assertEqual(p.map_async(sqr, []).get(), [])

        p.close()
        p.join()

    eleza test_context(self):
        ikiwa self.TYPE == 'processes':
            L = list(range(10))
            expected = [sqr(i) kila i kwenye L]
            ukijumuisha self.Pool(2) as p:
                r = p.map_async(sqr, L)
                self.assertEqual(r.get(), expected)
            p.join()
            self.assertRaises(ValueError, p.map_async, sqr, L)

    @classmethod
    eleza _test_traceback(cls):
         ashiria RuntimeError(123) # some comment

    eleza test_traceback(self):
        # We want ensure that the traceback kutoka the child process is
        # contained kwenye the traceback raised kwenye the main process.
        ikiwa self.TYPE == 'processes':
            ukijumuisha self.Pool(1) as p:
                jaribu:
                    p.apply(self._test_traceback)
                except Exception as e:
                    exc = e
                isipokua:
                    self.fail('expected RuntimeError')
            p.join()
            self.assertIs(type(exc), RuntimeError)
            self.assertEqual(exc.args, (123,))
            cause = exc.__cause__
            self.assertIs(type(cause), multiprocessing.pool.RemoteTraceback)
            self.assertIn(' ashiria RuntimeError(123) # some comment', cause.tb)

            ukijumuisha test.support.captured_stderr() as f1:
                jaribu:
                     ashiria exc
                except RuntimeError:
                    sys.excepthook(*sys.exc_info())
            self.assertIn(' ashiria RuntimeError(123) # some comment',
                          f1.getvalue())
            # _helper_reraises_exception should sio make the error
            # a remote exception
            ukijumuisha self.Pool(1) as p:
                jaribu:
                    p.map(sqr, exception_throwing_generator(1, -1), 1)
                except Exception as e:
                    exc = e
                isipokua:
                    self.fail('expected SayWhenError')
                self.assertIs(type(exc), SayWhenError)
                self.assertIs(exc.__cause__, Tupu)
            p.join()

    @classmethod
    eleza _test_wrapped_exception(cls):
         ashiria RuntimeError('foo')

    eleza test_wrapped_exception(self):
        # Issue #20980: Should sio wrap exception when using thread pool
        ukijumuisha self.Pool(1) as p:
            ukijumuisha self.assertRaises(RuntimeError):
                p.apply(self._test_wrapped_exception)
        p.join()

    eleza test_map_no_failfast(self):
        # Issue #23992: the fail-fast behaviour when an exception ni raised
        # during map() would make Pool.join() deadlock, because a worker
        # process would fill the result queue (after the result handler thread
        # terminated, hence sio draining it anymore).

        t_start = time.monotonic()

        ukijumuisha self.assertRaises(ValueError):
            ukijumuisha self.Pool(2) as p:
                jaribu:
                    p.map(raise_large_valuerror, [0, 1])
                mwishowe:
                    time.sleep(0.5)
                    p.close()
                    p.join()

        # check that we indeed waited kila all jobs
        self.assertGreater(time.monotonic() - t_start, 0.9)

    eleza test_release_task_refs(self):
        # Issue #29861: task arguments na results should sio be kept
        # alive after we are done ukijumuisha them.
        objs = [CountedObject() kila i kwenye range(10)]
        refs = [weakref.ref(o) kila o kwenye objs]
        self.pool.map(identity, objs)

        toa objs
        time.sleep(DELTA)  # let threaded cleanup code run
        self.assertEqual(set(wr() kila wr kwenye refs), {Tupu})
        # With a process pool, copies of the objects are returned, check
        # they were released too.
        self.assertEqual(CountedObject.n_instances, 0)

    eleza test_enter(self):
        ikiwa self.TYPE == 'manager':
            self.skipTest("test sio applicable to manager")

        pool = self.Pool(1)
        ukijumuisha pool:
            pass
            # call pool.terminate()
        # pool ni no longer running

        ukijumuisha self.assertRaises(ValueError):
            # bpo-35477: pool.__enter__() fails ikiwa the pool ni sio running
            ukijumuisha pool:
                pass
        pool.join()

    eleza test_resource_warning(self):
        ikiwa self.TYPE == 'manager':
            self.skipTest("test sio applicable to manager")

        pool = self.Pool(1)
        pool.terminate()
        pool.join()

        # force state to RUN to emit ResourceWarning kwenye __del__()
        pool._state = multiprocessing.pool.RUN

        ukijumuisha support.check_warnings(('unclosed running multiprocessing pool',
                                     ResourceWarning)):
            pool = Tupu
            support.gc_collect()

eleza raising():
     ashiria KeyError("key")

eleza unpickleable_result():
    rudisha lambda: 42

kundi _TestPoolWorkerErrors(BaseTestCase):
    ALLOWED_TYPES = ('processes', )

    eleza test_async_error_callback(self):
        p = multiprocessing.Pool(2)

        scratchpad = [Tupu]
        eleza errback(exc):
            scratchpad[0] = exc

        res = p.apply_async(raising, error_callback=errback)
        self.assertRaises(KeyError, res.get)
        self.assertKweli(scratchpad[0])
        self.assertIsInstance(scratchpad[0], KeyError)

        p.close()
        p.join()

    eleza test_unpickleable_result(self):
        kutoka multiprocessing.pool agiza MaybeEncodingError
        p = multiprocessing.Pool(2)

        # Make sure we don't lose pool processes because of encoding errors.
        kila iteration kwenye range(20):

            scratchpad = [Tupu]
            eleza errback(exc):
                scratchpad[0] = exc

            res = p.apply_async(unpickleable_result, error_callback=errback)
            self.assertRaises(MaybeEncodingError, res.get)
            wrapped = scratchpad[0]
            self.assertKweli(wrapped)
            self.assertIsInstance(scratchpad[0], MaybeEncodingError)
            self.assertIsNotTupu(wrapped.exc)
            self.assertIsNotTupu(wrapped.value)

        p.close()
        p.join()

kundi _TestPoolWorkerLifetime(BaseTestCase):
    ALLOWED_TYPES = ('processes', )

    eleza test_pool_worker_lifetime(self):
        p = multiprocessing.Pool(3, maxtasksperchild=10)
        self.assertEqual(3, len(p._pool))
        origworkerpids = [w.pid kila w kwenye p._pool]
        # Run many tasks so each worker gets replaced (hopefully)
        results = []
        kila i kwenye range(100):
            results.append(p.apply_async(sqr, (i, )))
        # Fetch the results na verify we got the right answers,
        # also ensuring all the tasks have completed.
        kila (j, res) kwenye enumerate(results):
            self.assertEqual(res.get(), sqr(j))
        # Refill the pool
        p._repopulate_pool()
        # Wait until all workers are alive
        # (countdown * DELTA = 5 seconds max startup process time)
        countdown = 50
        wakati countdown na sio all(w.is_alive() kila w kwenye p._pool):
            countdown -= 1
            time.sleep(DELTA)
        finalworkerpids = [w.pid kila w kwenye p._pool]
        # All pids should be assigned.  See issue #7805.
        self.assertNotIn(Tupu, origworkerpids)
        self.assertNotIn(Tupu, finalworkerpids)
        # Finally, check that the worker pids have changed
        self.assertNotEqual(sorted(origworkerpids), sorted(finalworkerpids))
        p.close()
        p.join()

    eleza test_pool_worker_lifetime_early_close(self):
        # Issue #10332: closing a pool whose workers have limited lifetimes
        # before all the tasks completed would make join() hang.
        p = multiprocessing.Pool(3, maxtasksperchild=1)
        results = []
        kila i kwenye range(6):
            results.append(p.apply_async(sqr, (i, 0.3)))
        p.close()
        p.join()
        # check the results
        kila (j, res) kwenye enumerate(results):
            self.assertEqual(res.get(), sqr(j))

#
# Test of creating a customized manager class
#

kutoka multiprocessing.managers agiza BaseManager, BaseProxy, RemoteError

kundi FooBar(object):
    eleza f(self):
        rudisha 'f()'
    eleza g(self):
         ashiria ValueError
    eleza _h(self):
        rudisha '_h()'

eleza baz():
    kila i kwenye range(10):
        tuma i*i

kundi IteratorProxy(BaseProxy):
    _exposed_ = ('__next__',)
    eleza __iter__(self):
        rudisha self
    eleza __next__(self):
        rudisha self._callmethod('__next__')

kundi MyManager(BaseManager):
    pass

MyManager.register('Foo', callable=FooBar)
MyManager.register('Bar', callable=FooBar, exposed=('f', '_h'))
MyManager.register('baz', callable=baz, proxytype=IteratorProxy)


kundi _TestMyManager(BaseTestCase):

    ALLOWED_TYPES = ('manager',)

    eleza test_mymanager(self):
        manager = MyManager()
        manager.start()
        self.common(manager)
        manager.shutdown()

        # bpo-30356: BaseManager._finalize_manager() sends SIGTERM
        # to the manager process ikiwa it takes longer than 1 second to stop,
        # which happens on slow buildbots.
        self.assertIn(manager._process.exitcode, (0, -signal.SIGTERM))

    eleza test_mymanager_context(self):
        ukijumuisha MyManager() as manager:
            self.common(manager)
        # bpo-30356: BaseManager._finalize_manager() sends SIGTERM
        # to the manager process ikiwa it takes longer than 1 second to stop,
        # which happens on slow buildbots.
        self.assertIn(manager._process.exitcode, (0, -signal.SIGTERM))

    eleza test_mymanager_context_prestarted(self):
        manager = MyManager()
        manager.start()
        ukijumuisha manager:
            self.common(manager)
        self.assertEqual(manager._process.exitcode, 0)

    eleza common(self, manager):
        foo = manager.Foo()
        bar = manager.Bar()
        baz = manager.baz()

        foo_methods = [name kila name kwenye ('f', 'g', '_h') ikiwa hasattr(foo, name)]
        bar_methods = [name kila name kwenye ('f', 'g', '_h') ikiwa hasattr(bar, name)]

        self.assertEqual(foo_methods, ['f', 'g'])
        self.assertEqual(bar_methods, ['f', '_h'])

        self.assertEqual(foo.f(), 'f()')
        self.assertRaises(ValueError, foo.g)
        self.assertEqual(foo._callmethod('f'), 'f()')
        self.assertRaises(RemoteError, foo._callmethod, '_h')

        self.assertEqual(bar.f(), 'f()')
        self.assertEqual(bar._h(), '_h()')
        self.assertEqual(bar._callmethod('f'), 'f()')
        self.assertEqual(bar._callmethod('_h'), '_h()')

        self.assertEqual(list(baz), [i*i kila i kwenye range(10)])


#
# Test of connecting to a remote server na using xmlrpclib kila serialization
#

_queue = pyqueue.Queue()
eleza get_queue():
    rudisha _queue

kundi QueueManager(BaseManager):
    '''manager kundi used by server process'''
QueueManager.register('get_queue', callable=get_queue)

kundi QueueManager2(BaseManager):
    '''manager kundi which specifies the same interface as QueueManager'''
QueueManager2.register('get_queue')


SERIALIZER = 'xmlrpclib'

kundi _TestRemoteManager(BaseTestCase):

    ALLOWED_TYPES = ('manager',)
    values = ['hello world', Tupu, Kweli, 2.25,
              'hall\xe5 v\xe4rlden',
              '\u043f\u0440\u0438\u0432\u0456\u0442 \u0441\u0432\u0456\u0442',
              b'hall\xe5 v\xe4rlden',
             ]
    result = values[:]

    @classmethod
    eleza _putter(cls, address, authkey):
        manager = QueueManager2(
            address=address, authkey=authkey, serializer=SERIALIZER
            )
        manager.connect()
        queue = manager.get_queue()
        # Note that xmlrpclib will deserialize object as a list sio a tuple
        queue.put(tuple(cls.values))

    eleza test_remote(self):
        authkey = os.urandom(32)

        manager = QueueManager(
            address=(test.support.HOST, 0), authkey=authkey, serializer=SERIALIZER
            )
        manager.start()
        self.addCleanup(manager.shutdown)

        p = self.Process(target=self._putter, args=(manager.address, authkey))
        p.daemon = Kweli
        p.start()

        manager2 = QueueManager2(
            address=manager.address, authkey=authkey, serializer=SERIALIZER
            )
        manager2.connect()
        queue = manager2.get_queue()

        self.assertEqual(queue.get(), self.result)

        # Because we are using xmlrpclib kila serialization instead of
        # pickle this will cause a serialization error.
        self.assertRaises(Exception, queue.put, time.sleep)

        # Make queue finalizer run before the server ni stopped
        toa queue

kundi _TestManagerRestart(BaseTestCase):

    @classmethod
    eleza _putter(cls, address, authkey):
        manager = QueueManager(
            address=address, authkey=authkey, serializer=SERIALIZER)
        manager.connect()
        queue = manager.get_queue()
        queue.put('hello world')

    eleza test_rapid_restart(self):
        authkey = os.urandom(32)
        manager = QueueManager(
            address=(test.support.HOST, 0), authkey=authkey, serializer=SERIALIZER)
        jaribu:
            srvr = manager.get_server()
            addr = srvr.address
            # Close the connection.Listener socket which gets opened as a part
            # of manager.get_server(). It's sio needed kila the test.
            srvr.listener.close()
            manager.start()

            p = self.Process(target=self._putter, args=(manager.address, authkey))
            p.start()
            p.join()
            queue = manager.get_queue()
            self.assertEqual(queue.get(), 'hello world')
            toa queue
        mwishowe:
            ikiwa hasattr(manager, "shutdown"):
                manager.shutdown()

        manager = QueueManager(
            address=addr, authkey=authkey, serializer=SERIALIZER)
        jaribu:
            manager.start()
            self.addCleanup(manager.shutdown)
        except OSError as e:
            ikiwa e.errno != errno.EADDRINUSE:
                raise
            # Retry after some time, kwenye case the old socket was lingering
            # (sporadic failure on buildbots)
            time.sleep(1.0)
            manager = QueueManager(
                address=addr, authkey=authkey, serializer=SERIALIZER)
            ikiwa hasattr(manager, "shutdown"):
                self.addCleanup(manager.shutdown)

#
#
#

SENTINEL = latin('')

kundi _TestConnection(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    @classmethod
    eleza _echo(cls, conn):
        kila msg kwenye iter(conn.recv_bytes, SENTINEL):
            conn.send_bytes(msg)
        conn.close()

    eleza test_connection(self):
        conn, child_conn = self.Pipe()

        p = self.Process(target=self._echo, args=(child_conn,))
        p.daemon = Kweli
        p.start()

        seq = [1, 2.25, Tupu]
        msg = latin('hello world')
        longmsg = msg * 10
        arr = array.array('i', list(range(4)))

        ikiwa self.TYPE == 'processes':
            self.assertEqual(type(conn.fileno()), int)

        self.assertEqual(conn.send(seq), Tupu)
        self.assertEqual(conn.recv(), seq)

        self.assertEqual(conn.send_bytes(msg), Tupu)
        self.assertEqual(conn.recv_bytes(), msg)

        ikiwa self.TYPE == 'processes':
            buffer = array.array('i', [0]*10)
            expected = list(arr) + [0] * (10 - len(arr))
            self.assertEqual(conn.send_bytes(arr), Tupu)
            self.assertEqual(conn.recv_bytes_into(buffer),
                             len(arr) * buffer.itemsize)
            self.assertEqual(list(buffer), expected)

            buffer = array.array('i', [0]*10)
            expected = [0] * 3 + list(arr) + [0] * (10 - 3 - len(arr))
            self.assertEqual(conn.send_bytes(arr), Tupu)
            self.assertEqual(conn.recv_bytes_into(buffer, 3 * buffer.itemsize),
                             len(arr) * buffer.itemsize)
            self.assertEqual(list(buffer), expected)

            buffer = bytearray(latin(' ' * 40))
            self.assertEqual(conn.send_bytes(longmsg), Tupu)
            jaribu:
                res = conn.recv_bytes_into(buffer)
            except multiprocessing.BufferTooShort as e:
                self.assertEqual(e.args, (longmsg,))
            isipokua:
                self.fail('expected BufferTooShort, got %s' % res)

        poll = TimingWrapper(conn.poll)

        self.assertEqual(poll(), Uongo)
        self.assertTimingAlmostEqual(poll.elapsed, 0)

        self.assertEqual(poll(-1), Uongo)
        self.assertTimingAlmostEqual(poll.elapsed, 0)

        self.assertEqual(poll(TIMEOUT1), Uongo)
        self.assertTimingAlmostEqual(poll.elapsed, TIMEOUT1)

        conn.send(Tupu)
        time.sleep(.1)

        self.assertEqual(poll(TIMEOUT1), Kweli)
        self.assertTimingAlmostEqual(poll.elapsed, 0)

        self.assertEqual(conn.recv(), Tupu)

        really_big_msg = latin('X') * (1024 * 1024 * 16)   # 16Mb
        conn.send_bytes(really_big_msg)
        self.assertEqual(conn.recv_bytes(), really_big_msg)

        conn.send_bytes(SENTINEL)                          # tell child to quit
        child_conn.close()

        ikiwa self.TYPE == 'processes':
            self.assertEqual(conn.readable, Kweli)
            self.assertEqual(conn.writable, Kweli)
            self.assertRaises(EOFError, conn.recv)
            self.assertRaises(EOFError, conn.recv_bytes)

        p.join()

    eleza test_duplex_false(self):
        reader, writer = self.Pipe(duplex=Uongo)
        self.assertEqual(writer.send(1), Tupu)
        self.assertEqual(reader.recv(), 1)
        ikiwa self.TYPE == 'processes':
            self.assertEqual(reader.readable, Kweli)
            self.assertEqual(reader.writable, Uongo)
            self.assertEqual(writer.readable, Uongo)
            self.assertEqual(writer.writable, Kweli)
            self.assertRaises(OSError, reader.send, 2)
            self.assertRaises(OSError, writer.recv)
            self.assertRaises(OSError, writer.poll)

    eleza test_spawn_close(self):
        # We test that a pipe connection can be closed by parent
        # process immediately after child ni spawned.  On Windows this
        # would have sometimes failed on old versions because
        # child_conn would be closed before the child got a chance to
        # duplicate it.
        conn, child_conn = self.Pipe()

        p = self.Process(target=self._echo, args=(child_conn,))
        p.daemon = Kweli
        p.start()
        child_conn.close()    # this might complete before child initializes

        msg = latin('hello')
        conn.send_bytes(msg)
        self.assertEqual(conn.recv_bytes(), msg)

        conn.send_bytes(SENTINEL)
        conn.close()
        p.join()

    eleza test_sendbytes(self):
        ikiwa self.TYPE != 'processes':
            self.skipTest('test sio appropriate kila {}'.format(self.TYPE))

        msg = latin('abcdefghijklmnopqrstuvwxyz')
        a, b = self.Pipe()

        a.send_bytes(msg)
        self.assertEqual(b.recv_bytes(), msg)

        a.send_bytes(msg, 5)
        self.assertEqual(b.recv_bytes(), msg[5:])

        a.send_bytes(msg, 7, 8)
        self.assertEqual(b.recv_bytes(), msg[7:7+8])

        a.send_bytes(msg, 26)
        self.assertEqual(b.recv_bytes(), latin(''))

        a.send_bytes(msg, 26, 0)
        self.assertEqual(b.recv_bytes(), latin(''))

        self.assertRaises(ValueError, a.send_bytes, msg, 27)

        self.assertRaises(ValueError, a.send_bytes, msg, 22, 5)

        self.assertRaises(ValueError, a.send_bytes, msg, 26, 1)

        self.assertRaises(ValueError, a.send_bytes, msg, -1)

        self.assertRaises(ValueError, a.send_bytes, msg, 4, -1)

    @classmethod
    eleza _is_fd_assigned(cls, fd):
        jaribu:
            os.fstat(fd)
        except OSError as e:
            ikiwa e.errno == errno.EBADF:
                rudisha Uongo
            raise
        isipokua:
            rudisha Kweli

    @classmethod
    eleza _writefd(cls, conn, data, create_dummy_fds=Uongo):
        ikiwa create_dummy_fds:
            kila i kwenye range(0, 256):
                ikiwa sio cls._is_fd_assigned(i):
                    os.dup2(conn.fileno(), i)
        fd = reduction.recv_handle(conn)
        ikiwa msvcrt:
            fd = msvcrt.open_osfhandle(fd, os.O_WRONLY)
        os.write(fd, data)
        os.close(fd)

    @unittest.skipUnless(HAS_REDUCTION, "test needs multiprocessing.reduction")
    eleza test_fd_transfer(self):
        ikiwa self.TYPE != 'processes':
            self.skipTest("only makes sense ukijumuisha processes")
        conn, child_conn = self.Pipe(duplex=Kweli)

        p = self.Process(target=self._writefd, args=(child_conn, b"foo"))
        p.daemon = Kweli
        p.start()
        self.addCleanup(test.support.unlink, test.support.TESTFN)
        ukijumuisha open(test.support.TESTFN, "wb") as f:
            fd = f.fileno()
            ikiwa msvcrt:
                fd = msvcrt.get_osfhandle(fd)
            reduction.send_handle(conn, fd, p.pid)
        p.join()
        ukijumuisha open(test.support.TESTFN, "rb") as f:
            self.assertEqual(f.read(), b"foo")

    @unittest.skipUnless(HAS_REDUCTION, "test needs multiprocessing.reduction")
    @unittest.skipIf(sys.platform == "win32",
                     "test semantics don't make sense on Windows")
    @unittest.skipIf(MAXFD <= 256,
                     "largest assignable fd number ni too small")
    @unittest.skipUnless(hasattr(os, "dup2"),
                         "test needs os.dup2()")
    eleza test_large_fd_transfer(self):
        # With fd > 256 (issue #11657)
        ikiwa self.TYPE != 'processes':
            self.skipTest("only makes sense ukijumuisha processes")
        conn, child_conn = self.Pipe(duplex=Kweli)

        p = self.Process(target=self._writefd, args=(child_conn, b"bar", Kweli))
        p.daemon = Kweli
        p.start()
        self.addCleanup(test.support.unlink, test.support.TESTFN)
        ukijumuisha open(test.support.TESTFN, "wb") as f:
            fd = f.fileno()
            kila newfd kwenye range(256, MAXFD):
                ikiwa sio self._is_fd_assigned(newfd):
                    koma
            isipokua:
                self.fail("could sio find an unassigned large file descriptor")
            os.dup2(fd, newfd)
            jaribu:
                reduction.send_handle(conn, newfd, p.pid)
            mwishowe:
                os.close(newfd)
        p.join()
        ukijumuisha open(test.support.TESTFN, "rb") as f:
            self.assertEqual(f.read(), b"bar")

    @classmethod
    eleza _send_data_without_fd(self, conn):
        os.write(conn.fileno(), b"\0")

    @unittest.skipUnless(HAS_REDUCTION, "test needs multiprocessing.reduction")
    @unittest.skipIf(sys.platform == "win32", "doesn't make sense on Windows")
    eleza test_missing_fd_transfer(self):
        # Check that exception ni raised when received data ni not
        # accompanied by a file descriptor kwenye ancillary data.
        ikiwa self.TYPE != 'processes':
            self.skipTest("only makes sense ukijumuisha processes")
        conn, child_conn = self.Pipe(duplex=Kweli)

        p = self.Process(target=self._send_data_without_fd, args=(child_conn,))
        p.daemon = Kweli
        p.start()
        self.assertRaises(RuntimeError, reduction.recv_handle, conn)
        p.join()

    eleza test_context(self):
        a, b = self.Pipe()

        ukijumuisha a, b:
            a.send(1729)
            self.assertEqual(b.recv(), 1729)
            ikiwa self.TYPE == 'processes':
                self.assertUongo(a.closed)
                self.assertUongo(b.closed)

        ikiwa self.TYPE == 'processes':
            self.assertKweli(a.closed)
            self.assertKweli(b.closed)
            self.assertRaises(OSError, a.recv)
            self.assertRaises(OSError, b.recv)

kundi _TestListener(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    eleza test_multiple_bind(self):
        kila family kwenye self.connection.families:
            l = self.connection.Listener(family=family)
            self.addCleanup(l.close)
            self.assertRaises(OSError, self.connection.Listener,
                              l.address, family)

    eleza test_context(self):
        ukijumuisha self.connection.Listener() as l:
            ukijumuisha self.connection.Client(l.address) as c:
                ukijumuisha l.accept() as d:
                    c.send(1729)
                    self.assertEqual(d.recv(), 1729)

        ikiwa self.TYPE == 'processes':
            self.assertRaises(OSError, l.accept)

kundi _TestListenerClient(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    @classmethod
    eleza _test(cls, address):
        conn = cls.connection.Client(address)
        conn.send('hello')
        conn.close()

    eleza test_listener_client(self):
        kila family kwenye self.connection.families:
            l = self.connection.Listener(family=family)
            p = self.Process(target=self._test, args=(l.address,))
            p.daemon = Kweli
            p.start()
            conn = l.accept()
            self.assertEqual(conn.recv(), 'hello')
            p.join()
            l.close()

    eleza test_issue14725(self):
        l = self.connection.Listener()
        p = self.Process(target=self._test, args=(l.address,))
        p.daemon = Kweli
        p.start()
        time.sleep(1)
        # On Windows the client process should by now have connected,
        # written data na closed the pipe handle by now.  This causes
        # ConnectNamdedPipe() to fail ukijumuisha ERROR_NO_DATA.  See Issue
        # 14725.
        conn = l.accept()
        self.assertEqual(conn.recv(), 'hello')
        conn.close()
        p.join()
        l.close()

    eleza test_issue16955(self):
        kila fam kwenye self.connection.families:
            l = self.connection.Listener(family=fam)
            c = self.connection.Client(l.address)
            a = l.accept()
            a.send_bytes(b"hello")
            self.assertKweli(c.poll(1))
            a.close()
            c.close()
            l.close()

kundi _TestPoll(BaseTestCase):

    ALLOWED_TYPES = ('processes', 'threads')

    eleza test_empty_string(self):
        a, b = self.Pipe()
        self.assertEqual(a.poll(), Uongo)
        b.send_bytes(b'')
        self.assertEqual(a.poll(), Kweli)
        self.assertEqual(a.poll(), Kweli)

    @classmethod
    eleza _child_strings(cls, conn, strings):
        kila s kwenye strings:
            time.sleep(0.1)
            conn.send_bytes(s)
        conn.close()

    eleza test_strings(self):
        strings = (b'hello', b'', b'a', b'b', b'', b'bye', b'', b'lop')
        a, b = self.Pipe()
        p = self.Process(target=self._child_strings, args=(b, strings))
        p.start()

        kila s kwenye strings:
            kila i kwenye range(200):
                ikiwa a.poll(0.01):
                    koma
            x = a.recv_bytes()
            self.assertEqual(s, x)

        p.join()

    @classmethod
    eleza _child_boundaries(cls, r):
        # Polling may "pull" a message kwenye to the child process, but we
        # don't want it to pull only part of a message, as that would
        # corrupt the pipe kila any other processes which might later
        # read kutoka it.
        r.poll(5)

    eleza test_boundaries(self):
        r, w = self.Pipe(Uongo)
        p = self.Process(target=self._child_boundaries, args=(r,))
        p.start()
        time.sleep(2)
        L = [b"first", b"second"]
        kila obj kwenye L:
            w.send_bytes(obj)
        w.close()
        p.join()
        self.assertIn(r.recv_bytes(), L)

    @classmethod
    eleza _child_dont_merge(cls, b):
        b.send_bytes(b'a')
        b.send_bytes(b'b')
        b.send_bytes(b'cd')

    eleza test_dont_merge(self):
        a, b = self.Pipe()
        self.assertEqual(a.poll(0.0), Uongo)
        self.assertEqual(a.poll(0.1), Uongo)

        p = self.Process(target=self._child_dont_merge, args=(b,))
        p.start()

        self.assertEqual(a.recv_bytes(), b'a')
        self.assertEqual(a.poll(1.0), Kweli)
        self.assertEqual(a.poll(1.0), Kweli)
        self.assertEqual(a.recv_bytes(), b'b')
        self.assertEqual(a.poll(1.0), Kweli)
        self.assertEqual(a.poll(1.0), Kweli)
        self.assertEqual(a.poll(0.0), Kweli)
        self.assertEqual(a.recv_bytes(), b'cd')

        p.join()

#
# Test of sending connection na socket objects between processes
#

@unittest.skipUnless(HAS_REDUCTION, "test needs multiprocessing.reduction")
kundi _TestPicklingConnections(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    @classmethod
    eleza tearDownClass(cls):
        kutoka multiprocessing agiza resource_sharer
        resource_sharer.stop(timeout=TIMEOUT)

    @classmethod
    eleza _listener(cls, conn, families):
        kila fam kwenye families:
            l = cls.connection.Listener(family=fam)
            conn.send(l.address)
            new_conn = l.accept()
            conn.send(new_conn)
            new_conn.close()
            l.close()

        l = socket.create_server((test.support.HOST, 0))
        conn.send(l.getsockname())
        new_conn, addr = l.accept()
        conn.send(new_conn)
        new_conn.close()
        l.close()

        conn.recv()

    @classmethod
    eleza _remote(cls, conn):
        kila (address, msg) kwenye iter(conn.recv, Tupu):
            client = cls.connection.Client(address)
            client.send(msg.upper())
            client.close()

        address, msg = conn.recv()
        client = socket.socket()
        client.connect(address)
        client.sendall(msg.upper())
        client.close()

        conn.close()

    eleza test_pickling(self):
        families = self.connection.families

        lconn, lconn0 = self.Pipe()
        lp = self.Process(target=self._listener, args=(lconn0, families))
        lp.daemon = Kweli
        lp.start()
        lconn0.close()

        rconn, rconn0 = self.Pipe()
        rp = self.Process(target=self._remote, args=(rconn0,))
        rp.daemon = Kweli
        rp.start()
        rconn0.close()

        kila fam kwenye families:
            msg = ('This connection uses family %s' % fam).encode('ascii')
            address = lconn.recv()
            rconn.send((address, msg))
            new_conn = lconn.recv()
            self.assertEqual(new_conn.recv(), msg.upper())

        rconn.send(Tupu)

        msg = latin('This connection uses a normal socket')
        address = lconn.recv()
        rconn.send((address, msg))
        new_conn = lconn.recv()
        buf = []
        wakati Kweli:
            s = new_conn.recv(100)
            ikiwa sio s:
                koma
            buf.append(s)
        buf = b''.join(buf)
        self.assertEqual(buf, msg.upper())
        new_conn.close()

        lconn.send(Tupu)

        rconn.close()
        lconn.close()

        lp.join()
        rp.join()

    @classmethod
    eleza child_access(cls, conn):
        w = conn.recv()
        w.send('all ni well')
        w.close()

        r = conn.recv()
        msg = r.recv()
        conn.send(msg*2)

        conn.close()

    eleza test_access(self):
        # On Windows, ikiwa we do sio specify a destination pid when
        # using DupHandle then we need to be careful to use the
        # correct access flags kila DuplicateHandle(), ama else
        # DupHandle.detach() will  ashiria PermissionError.  For example,
        # kila a read only pipe handle we should use
        # access=FILE_GENERIC_READ.  (Unfortunately
        # DUPLICATE_SAME_ACCESS does sio work.)
        conn, child_conn = self.Pipe()
        p = self.Process(target=self.child_access, args=(child_conn,))
        p.daemon = Kweli
        p.start()
        child_conn.close()

        r, w = self.Pipe(duplex=Uongo)
        conn.send(w)
        w.close()
        self.assertEqual(r.recv(), 'all ni well')
        r.close()

        r, w = self.Pipe(duplex=Uongo)
        conn.send(r)
        r.close()
        w.send('foobar')
        w.close()
        self.assertEqual(conn.recv(), 'foobar'*2)

        p.join()

#
#
#

kundi _TestHeap(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    eleza setUp(self):
        super().setUp()
        # Make pristine heap kila these tests
        self.old_heap = multiprocessing.heap.BufferWrapper._heap
        multiprocessing.heap.BufferWrapper._heap = multiprocessing.heap.Heap()

    eleza tearDown(self):
        multiprocessing.heap.BufferWrapper._heap = self.old_heap
        super().tearDown()

    eleza test_heap(self):
        iterations = 5000
        maxblocks = 50
        blocks = []

        # get the heap object
        heap = multiprocessing.heap.BufferWrapper._heap
        heap._DISCARD_FREE_SPACE_LARGER_THAN = 0

        # create na destroy lots of blocks of different sizes
        kila i kwenye range(iterations):
            size = int(random.lognormvariate(0, 1) * 1000)
            b = multiprocessing.heap.BufferWrapper(size)
            blocks.append(b)
            ikiwa len(blocks) > maxblocks:
                i = random.randrange(maxblocks)
                toa blocks[i]
            toa b

        # verify the state of the heap
        ukijumuisha heap._lock:
            all = []
            free = 0
            occupied = 0
            kila L kwenye list(heap._len_to_seq.values()):
                # count all free blocks kwenye arenas
                kila arena, start, stop kwenye L:
                    all.append((heap._arenas.index(arena), start, stop,
                                stop-start, 'free'))
                    free += (stop-start)
            kila arena, arena_blocks kwenye heap._allocated_blocks.items():
                # count all allocated blocks kwenye arenas
                kila start, stop kwenye arena_blocks:
                    all.append((heap._arenas.index(arena), start, stop,
                                stop-start, 'occupied'))
                    occupied += (stop-start)

            self.assertEqual(free + occupied,
                             sum(arena.size kila arena kwenye heap._arenas))

            all.sort()

            kila i kwenye range(len(all)-1):
                (arena, start, stop) = all[i][:3]
                (narena, nstart, nstop) = all[i+1][:3]
                ikiwa arena != narena:
                    # Two different arenas
                    self.assertEqual(stop, heap._arenas[arena].size)  # last block
                    self.assertEqual(nstart, 0)         # first block
                isipokua:
                    # Same arena: two adjacent blocks
                    self.assertEqual(stop, nstart)

        # test free'ing all blocks
        random.shuffle(blocks)
        wakati blocks:
            blocks.pop()

        self.assertEqual(heap._n_frees, heap._n_mallocs)
        self.assertEqual(len(heap._pending_free_blocks), 0)
        self.assertEqual(len(heap._arenas), 0)
        self.assertEqual(len(heap._allocated_blocks), 0, heap._allocated_blocks)
        self.assertEqual(len(heap._len_to_seq), 0)

    eleza test_free_from_gc(self):
        # Check that freeing of blocks by the garbage collector doesn't deadlock
        # (issue #12352).
        # Make sure the GC ni enabled, na set lower collection thresholds to
        # make collections more frequent (and increase the probability of
        # deadlock).
        ikiwa sio gc.isenabled():
            gc.enable()
            self.addCleanup(gc.disable)
        thresholds = gc.get_threshold()
        self.addCleanup(gc.set_threshold, *thresholds)
        gc.set_threshold(10)

        # perform numerous block allocations, ukijumuisha cyclic references to make
        # sure objects are collected asynchronously by the gc
        kila i kwenye range(5000):
            a = multiprocessing.heap.BufferWrapper(1)
            b = multiprocessing.heap.BufferWrapper(1)
            # circular references
            a.buddy = b
            b.buddy = a

#
#
#

kundi _Foo(Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_double),
        ('z', c_longlong,)
        ]

kundi _TestSharedCTypes(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    eleza setUp(self):
        ikiwa sio HAS_SHAREDCTYPES:
            self.skipTest("requires multiprocessing.sharedctypes")

    @classmethod
    eleza _double(cls, x, y, z, foo, arr, string):
        x.value *= 2
        y.value *= 2
        z.value *= 2
        foo.x *= 2
        foo.y *= 2
        string.value *= 2
        kila i kwenye range(len(arr)):
            arr[i] *= 2

    eleza test_sharedctypes(self, lock=Uongo):
        x = Value('i', 7, lock=lock)
        y = Value(c_double, 1.0/3.0, lock=lock)
        z = Value(c_longlong, 2 ** 33, lock=lock)
        foo = Value(_Foo, 3, 2, lock=lock)
        arr = self.Array('d', list(range(10)), lock=lock)
        string = self.Array('c', 20, lock=lock)
        string.value = latin('hello')

        p = self.Process(target=self._double, args=(x, y, z, foo, arr, string))
        p.daemon = Kweli
        p.start()
        p.join()

        self.assertEqual(x.value, 14)
        self.assertAlmostEqual(y.value, 2.0/3.0)
        self.assertEqual(z.value, 2 ** 34)
        self.assertEqual(foo.x, 6)
        self.assertAlmostEqual(foo.y, 4.0)
        kila i kwenye range(10):
            self.assertAlmostEqual(arr[i], i*2)
        self.assertEqual(string.value, latin('hellohello'))

    eleza test_synchronize(self):
        self.test_sharedctypes(lock=Kweli)

    eleza test_copy(self):
        foo = _Foo(2, 5.0, 2 ** 33)
        bar = copy(foo)
        foo.x = 0
        foo.y = 0
        foo.z = 0
        self.assertEqual(bar.x, 2)
        self.assertAlmostEqual(bar.y, 5.0)
        self.assertEqual(bar.z, 2 ** 33)


@unittest.skipUnless(HAS_SHMEM, "requires multiprocessing.shared_memory")
kundi _TestSharedMemory(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    @staticmethod
    eleza _attach_existing_shmem_then_write(shmem_name_or_obj, binary_data):
        ikiwa isinstance(shmem_name_or_obj, str):
            local_sms = shared_memory.SharedMemory(shmem_name_or_obj)
        isipokua:
            local_sms = shmem_name_or_obj
        local_sms.buf[:len(binary_data)] = binary_data
        local_sms.close()

    eleza test_shared_memory_basics(self):
        sms = shared_memory.SharedMemory('test01_tsmb', create=Kweli, size=512)
        self.addCleanup(sms.unlink)

        # Verify attributes are readable.
        self.assertEqual(sms.name, 'test01_tsmb')
        self.assertGreaterEqual(sms.size, 512)
        self.assertGreaterEqual(len(sms.buf), sms.size)

        # Modify contents of shared memory segment through memoryview.
        sms.buf[0] = 42
        self.assertEqual(sms.buf[0], 42)

        # Attach to existing shared memory segment.
        also_sms = shared_memory.SharedMemory('test01_tsmb')
        self.assertEqual(also_sms.buf[0], 42)
        also_sms.close()

        # Attach to existing shared memory segment but specify a new size.
        same_sms = shared_memory.SharedMemory('test01_tsmb', size=20*sms.size)
        self.assertLess(same_sms.size, 20*sms.size)  # Size was ignored.
        same_sms.close()

        ikiwa shared_memory._USE_POSIX:
            # Posix Shared Memory can only be unlinked once.  Here we
            # test an implementation detail that ni sio observed across
            # all supported platforms (since WindowsNamedSharedMemory
            # manages unlinking on its own na unlink() does nothing).
            # Kweli release of shared memory segment does sio necessarily
            # happen until process exits, depending on the OS platform.
            ukijumuisha self.assertRaises(FileNotFoundError):
                sms_uno = shared_memory.SharedMemory(
                    'test01_dblunlink',
                    create=Kweli,
                    size=5000
                )

                jaribu:
                    self.assertGreaterEqual(sms_uno.size, 5000)

                    sms_duo = shared_memory.SharedMemory('test01_dblunlink')
                    sms_duo.unlink()  # First shm_unlink() call.
                    sms_duo.close()
                    sms_uno.close()

                mwishowe:
                    sms_uno.unlink()  # A second shm_unlink() call ni bad.

        ukijumuisha self.assertRaises(FileExistsError):
            # Attempting to create a new shared memory segment ukijumuisha a
            # name that ni already kwenye use triggers an exception.
            there_can_only_be_one_sms = shared_memory.SharedMemory(
                'test01_tsmb',
                create=Kweli,
                size=512
            )

        ikiwa shared_memory._USE_POSIX:
            # Requesting creation of a shared memory segment ukijumuisha the option
            # to attach to an existing segment, ikiwa that name ni currently in
            # use, should sio trigger an exception.
            # Note:  Using a smaller size could possibly cause truncation of
            # the existing segment but ni OS platform dependent.  In the
            # case of MacOS/darwin, requesting a smaller size ni disallowed.
            kundi OptionalAttachSharedMemory(shared_memory.SharedMemory):
                _flags = os.O_CREAT | os.O_RDWR
            ok_if_exists_sms = OptionalAttachSharedMemory('test01_tsmb')
            self.assertEqual(ok_if_exists_sms.size, sms.size)
            ok_if_exists_sms.close()

        # Attempting to attach to an existing shared memory segment when
        # no segment exists ukijumuisha the supplied name triggers an exception.
        ukijumuisha self.assertRaises(FileNotFoundError):
            nonexisting_sms = shared_memory.SharedMemory('test01_notthere')
            nonexisting_sms.unlink()  # Error should occur on prior line.

        sms.close()

    eleza test_shared_memory_across_processes(self):
        sms = shared_memory.SharedMemory('test02_tsmap', Kweli, size=512)
        self.addCleanup(sms.unlink)

        # Verify remote attachment to existing block by name ni working.
        p = self.Process(
            target=self._attach_existing_shmem_then_write,
            args=(sms.name, b'howdy')
        )
        p.daemon = Kweli
        p.start()
        p.join()
        self.assertEqual(bytes(sms.buf[:5]), b'howdy')

        # Verify pickling of SharedMemory instance also works.
        p = self.Process(
            target=self._attach_existing_shmem_then_write,
            args=(sms, b'HELLO')
        )
        p.daemon = Kweli
        p.start()
        p.join()
        self.assertEqual(bytes(sms.buf[:5]), b'HELLO')

        sms.close()

    @unittest.skipIf(os.name != "posix", "not feasible kwenye non-posix platforms")
    eleza test_shared_memory_SharedMemoryServer_ignores_sigint(self):
        # bpo-36368: protect SharedMemoryManager server process from
        # KeyboardInterrupt signals.
        smm = multiprocessing.managers.SharedMemoryManager()
        smm.start()

        # make sure the manager works properly at the beginning
        sl = smm.ShareableList(range(10))

        # the manager's server should ignore KeyboardInterrupt signals, and
        # maintain its connection ukijumuisha the current process, na success when
        # asked to deliver memory segments.
        os.kill(smm._process.pid, signal.SIGINT)

        sl2 = smm.ShareableList(range(10))

        # test that the custom signal handler registered kwenye the Manager does
        # sio affect signal handling kwenye the parent process.
        ukijumuisha self.assertRaises(KeyboardInterrupt):
            os.kill(os.getpid(), signal.SIGINT)

        smm.shutdown()

    @unittest.skipIf(os.name != "posix", "resource_tracker ni posix only")
    eleza test_shared_memory_SharedMemoryManager_reuses_resource_tracker(self):
        # bpo-36867: test that a SharedMemoryManager uses the
        # same resource_tracker process as its parent.
        cmd = '''ikiwa 1:
            kutoka multiprocessing.managers agiza SharedMemoryManager


            smm = SharedMemoryManager()
            smm.start()
            sl = smm.ShareableList(range(10))
            smm.shutdown()
        '''
        rc, out, err = test.support.script_helper.assert_python_ok('-c', cmd)

        # Before bpo-36867 was fixed, a SharedMemoryManager sio using the same
        # resource_tracker process as its parent would make the parent's
        # tracker complain about sl being leaked even though smm.shutdown()
        # properly released sl.
        self.assertUongo(err)

    eleza test_shared_memory_SharedMemoryManager_basics(self):
        smm1 = multiprocessing.managers.SharedMemoryManager()
        ukijumuisha self.assertRaises(ValueError):
            smm1.SharedMemory(size=9)  # Fails ikiwa SharedMemoryServer sio started
        smm1.start()
        lol = [ smm1.ShareableList(range(i)) kila i kwenye range(5, 10) ]
        lom = [ smm1.SharedMemory(size=j) kila j kwenye range(32, 128, 16) ]
        doppleganger_list0 = shared_memory.ShareableList(name=lol[0].shm.name)
        self.assertEqual(len(doppleganger_list0), 5)
        doppleganger_shm0 = shared_memory.SharedMemory(name=lom[0].name)
        self.assertGreaterEqual(len(doppleganger_shm0.buf), 32)
        held_name = lom[0].name
        smm1.shutdown()
        ikiwa sys.platform != "win32":
            # Calls to unlink() have no effect on Windows platform; shared
            # memory will only be released once final process exits.
            ukijumuisha self.assertRaises(FileNotFoundError):
                # No longer there to be attached to again.
                absent_shm = shared_memory.SharedMemory(name=held_name)

        ukijumuisha multiprocessing.managers.SharedMemoryManager() as smm2:
            sl = smm2.ShareableList("howdy")
            shm = smm2.SharedMemory(size=128)
            held_name = sl.shm.name
        ikiwa sys.platform != "win32":
            ukijumuisha self.assertRaises(FileNotFoundError):
                # No longer there to be attached to again.
                absent_sl = shared_memory.ShareableList(name=held_name)


    eleza test_shared_memory_ShareableList_basics(self):
        sl = shared_memory.ShareableList(
            ['howdy', b'HoWdY', -273.154, 100, Tupu, Kweli, 42]
        )
        self.addCleanup(sl.shm.unlink)

        # Verify attributes are readable.
        self.assertEqual(sl.format, '8s8sdqxxxxxx?xxxxxxxx?q')

        # Exercise len().
        self.assertEqual(len(sl), 7)

        # Exercise index().
        ukijumuisha warnings.catch_warnings():
            # Suppress BytesWarning when comparing against b'HoWdY'.
            warnings.simplefilter('ignore')
            ukijumuisha self.assertRaises(ValueError):
                sl.index('100')
            self.assertEqual(sl.index(100), 3)

        # Exercise retrieving individual values.
        self.assertEqual(sl[0], 'howdy')
        self.assertEqual(sl[-2], Kweli)

        # Exercise iterability.
        self.assertEqual(
            tuple(sl),
            ('howdy', b'HoWdY', -273.154, 100, Tupu, Kweli, 42)
        )

        # Exercise modifying individual values.
        sl[3] = 42
        self.assertEqual(sl[3], 42)
        sl[4] = 'some'  # Change type at a given position.
        self.assertEqual(sl[4], 'some')
        self.assertEqual(sl.format, '8s8sdq8sxxxxxxx?q')
        ukijumuisha self.assertRaises(ValueError):
            sl[4] = 'far too many'  # Exceeds available storage.
        self.assertEqual(sl[4], 'some')

        # Exercise count().
        ukijumuisha warnings.catch_warnings():
            # Suppress BytesWarning when comparing against b'HoWdY'.
            warnings.simplefilter('ignore')
            self.assertEqual(sl.count(42), 2)
            self.assertEqual(sl.count(b'HoWdY'), 1)
            self.assertEqual(sl.count(b'adios'), 0)

        # Exercise creating a duplicate.
        sl_copy = shared_memory.ShareableList(sl, name='test03_duplicate')
        jaribu:
            self.assertNotEqual(sl.shm.name, sl_copy.shm.name)
            self.assertEqual('test03_duplicate', sl_copy.shm.name)
            self.assertEqual(list(sl), list(sl_copy))
            self.assertEqual(sl.format, sl_copy.format)
            sl_copy[-1] = 77
            self.assertEqual(sl_copy[-1], 77)
            self.assertNotEqual(sl[-1], 77)
            sl_copy.shm.close()
        mwishowe:
            sl_copy.shm.unlink()

        # Obtain a second handle on the same ShareableList.
        sl_tethered = shared_memory.ShareableList(name=sl.shm.name)
        self.assertEqual(sl.shm.name, sl_tethered.shm.name)
        sl_tethered[-1] = 880
        self.assertEqual(sl[-1], 880)
        sl_tethered.shm.close()

        sl.shm.close()

        # Exercise creating an empty ShareableList.
        empty_sl = shared_memory.ShareableList()
        jaribu:
            self.assertEqual(len(empty_sl), 0)
            self.assertEqual(empty_sl.format, '')
            self.assertEqual(empty_sl.count('any'), 0)
            ukijumuisha self.assertRaises(ValueError):
                empty_sl.index(Tupu)
            empty_sl.shm.close()
        mwishowe:
            empty_sl.shm.unlink()

    eleza test_shared_memory_ShareableList_pickling(self):
        sl = shared_memory.ShareableList(range(10))
        self.addCleanup(sl.shm.unlink)

        serialized_sl = pickle.dumps(sl)
        deserialized_sl = pickle.loads(serialized_sl)
        self.assertKweli(
            isinstance(deserialized_sl, shared_memory.ShareableList)
        )
        self.assertKweli(deserialized_sl[-1], 9)
        self.assertUongo(sl ni deserialized_sl)
        deserialized_sl[4] = "changed"
        self.assertEqual(sl[4], "changed")

        # Verify data ni sio being put into the pickled representation.
        name = 'a' * len(sl.shm.name)
        larger_sl = shared_memory.ShareableList(range(400))
        self.addCleanup(larger_sl.shm.unlink)
        serialized_larger_sl = pickle.dumps(larger_sl)
        self.assertKweli(len(serialized_sl) == len(serialized_larger_sl))
        larger_sl.shm.close()

        deserialized_sl.shm.close()
        sl.shm.close()

    eleza test_shared_memory_cleaned_after_process_termination(self):
        cmd = '''ikiwa 1:
            agiza os, time, sys
            kutoka multiprocessing agiza shared_memory

            # Create a shared_memory segment, na send the segment name
            sm = shared_memory.SharedMemory(create=Kweli, size=10)
            sys.stdout.write(sm.name + '\\n')
            sys.stdout.flush()
            time.sleep(100)
        '''
        ukijumuisha subprocess.Popen([sys.executable, '-E', '-c', cmd],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as p:
            name = p.stdout.readline().strip().decode()

            # killing abruptly processes holding reference to a shared memory
            # segment should sio leak the given memory segment.
            p.terminate()
            p.wait()

            deadline = time.monotonic() + 60
            t = 0.1
            wakati time.monotonic() < deadline:
                time.sleep(t)
                t = min(t*2, 5)
                jaribu:
                    smm = shared_memory.SharedMemory(name, create=Uongo)
                except FileNotFoundError:
                    koma
            isipokua:
                 ashiria AssertionError("A SharedMemory segment was leaked after"
                                     " a process was abruptly terminated.")

            ikiwa os.name == 'posix':
                # A warning was emitted by the subprocess' own
                # resource_tracker (on Windows, shared memory segments
                # are released automatically by the OS).
                err = p.stderr.read().decode()
                self.assertIn(
                    "resource_tracker: There appear to be 1 leaked "
                    "shared_memory objects to clean up at shutdown", err)

#
#
#

kundi _TestFinalize(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    eleza setUp(self):
        self.registry_backup = util._finalizer_registry.copy()
        util._finalizer_registry.clear()

    eleza tearDown(self):
        self.assertUongo(util._finalizer_registry)
        util._finalizer_registry.update(self.registry_backup)

    @classmethod
    eleza _test_finalize(cls, conn):
        kundi Foo(object):
            pass

        a = Foo()
        util.Finalize(a, conn.send, args=('a',))
        toa a           # triggers callback kila a

        b = Foo()
        close_b = util.Finalize(b, conn.send, args=('b',))
        close_b()       # triggers callback kila b
        close_b()       # does nothing because callback has already been called
        toa b           # does nothing because callback has already been called

        c = Foo()
        util.Finalize(c, conn.send, args=('c',))

        d10 = Foo()
        util.Finalize(d10, conn.send, args=('d10',), exitpriority=1)

        d01 = Foo()
        util.Finalize(d01, conn.send, args=('d01',), exitpriority=0)
        d02 = Foo()
        util.Finalize(d02, conn.send, args=('d02',), exitpriority=0)
        d03 = Foo()
        util.Finalize(d03, conn.send, args=('d03',), exitpriority=0)

        util.Finalize(Tupu, conn.send, args=('e',), exitpriority=-10)

        util.Finalize(Tupu, conn.send, args=('STOP',), exitpriority=-100)

        # call multiprocessing's cleanup function then exit process without
        # garbage collecting locals
        util._exit_function()
        conn.close()
        os._exit(0)

    eleza test_finalize(self):
        conn, child_conn = self.Pipe()

        p = self.Process(target=self._test_finalize, args=(child_conn,))
        p.daemon = Kweli
        p.start()
        p.join()

        result = [obj kila obj kwenye iter(conn.recv, 'STOP')]
        self.assertEqual(result, ['a', 'b', 'd10', 'd03', 'd02', 'd01', 'e'])

    eleza test_thread_safety(self):
        # bpo-24484: _run_finalizers() should be thread-safe
        eleza cb():
            pass

        kundi Foo(object):
            eleza __init__(self):
                self.ref = self  # create reference cycle
                # insert finalizer at random key
                util.Finalize(self, cb, exitpriority=random.randint(1, 100))

        finish = Uongo
        exc = Tupu

        eleza run_finalizers():
            nonlocal exc
            wakati sio finish:
                time.sleep(random.random() * 1e-1)
                jaribu:
                    # A GC run will eventually happen during this,
                    # collecting stale Foo's na mutating the registry
                    util._run_finalizers()
                except Exception as e:
                    exc = e

        eleza make_finalizers():
            nonlocal exc
            d = {}
            wakati sio finish:
                jaribu:
                    # Old Foo's get gradually replaced na later
                    # collected by the GC (because of the cyclic ref)
                    d[random.getrandbits(5)] = {Foo() kila i kwenye range(10)}
                except Exception as e:
                    exc = e
                    d.clear()

        old_interval = sys.getswitchinterval()
        old_threshold = gc.get_threshold()
        jaribu:
            sys.setswitchinterval(1e-6)
            gc.set_threshold(5, 5, 5)
            threads = [threading.Thread(target=run_finalizers),
                       threading.Thread(target=make_finalizers)]
            ukijumuisha test.support.start_threads(threads):
                time.sleep(4.0)  # Wait a bit to trigger race condition
                finish = Kweli
            ikiwa exc ni sio Tupu:
                 ashiria exc
        mwishowe:
            sys.setswitchinterval(old_interval)
            gc.set_threshold(*old_threshold)
            gc.collect()  # Collect remaining Foo's


#
# Test that kutoka ... agiza * works kila each module
#

kundi _TestImportStar(unittest.TestCase):

    eleza get_module_names(self):
        agiza glob
        folder = os.path.dirname(multiprocessing.__file__)
        pattern = os.path.join(folder, '*.py')
        files = glob.glob(pattern)
        modules = [os.path.splitext(os.path.split(f)[1])[0] kila f kwenye files]
        modules = ['multiprocessing.' + m kila m kwenye modules]
        modules.remove('multiprocessing.__init__')
        modules.append('multiprocessing')
        rudisha modules

    eleza test_import(self):
        modules = self.get_module_names()
        ikiwa sys.platform == 'win32':
            modules.remove('multiprocessing.popen_fork')
            modules.remove('multiprocessing.popen_forkserver')
            modules.remove('multiprocessing.popen_spawn_posix')
        isipokua:
            modules.remove('multiprocessing.popen_spawn_win32')
            ikiwa sio HAS_REDUCTION:
                modules.remove('multiprocessing.popen_forkserver')

        ikiwa c_int ni Tupu:
            # This module requires _ctypes
            modules.remove('multiprocessing.sharedctypes')

        kila name kwenye modules:
            __import__(name)
            mod = sys.modules[name]
            self.assertKweli(hasattr(mod, '__all__'), name)

            kila attr kwenye mod.__all__:
                self.assertKweli(
                    hasattr(mod, attr),
                    '%r does sio have attribute %r' % (mod, attr)
                    )

#
# Quick test that logging works -- does sio test logging output
#

kundi _TestLogging(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    eleza test_enable_logging(self):
        logger = multiprocessing.get_logger()
        logger.setLevel(util.SUBWARNING)
        self.assertKweli(logger ni sio Tupu)
        logger.debug('this will sio be printed')
        logger.info('nor will this')
        logger.setLevel(LOG_LEVEL)

    @classmethod
    eleza _test_level(cls, conn):
        logger = multiprocessing.get_logger()
        conn.send(logger.getEffectiveLevel())

    eleza test_level(self):
        LEVEL1 = 32
        LEVEL2 = 37

        logger = multiprocessing.get_logger()
        root_logger = logging.getLogger()
        root_level = root_logger.level

        reader, writer = multiprocessing.Pipe(duplex=Uongo)

        logger.setLevel(LEVEL1)
        p = self.Process(target=self._test_level, args=(writer,))
        p.start()
        self.assertEqual(LEVEL1, reader.recv())
        p.join()
        p.close()

        logger.setLevel(logging.NOTSET)
        root_logger.setLevel(LEVEL2)
        p = self.Process(target=self._test_level, args=(writer,))
        p.start()
        self.assertEqual(LEVEL2, reader.recv())
        p.join()
        p.close()

        root_logger.setLevel(root_level)
        logger.setLevel(level=LOG_LEVEL)


# kundi _TestLoggingProcessName(BaseTestCase):
#
#     eleza handle(self, record):
#         assert record.processName == multiprocessing.current_process().name
#         self.__handled = Kweli
#
#     eleza test_logging(self):
#         handler = logging.Handler()
#         handler.handle = self.handle
#         self.__handled = Uongo
#         # Bypass getLogger() na side-effects
#         logger = logging.getLoggerClass()(
#                 'multiprocessing.test.TestLoggingProcessName')
#         logger.addHandler(handler)
#         logger.propagate = Uongo
#
#         logger.warn('foo')
#         assert self.__handled

#
# Check that Process.join() retries ikiwa os.waitpid() fails ukijumuisha EINTR
#

kundi _TestPollEintr(BaseTestCase):

    ALLOWED_TYPES = ('processes',)

    @classmethod
    eleza _killer(cls, pid):
        time.sleep(0.1)
        os.kill(pid, signal.SIGUSR1)

    @unittest.skipUnless(hasattr(signal, 'SIGUSR1'), 'requires SIGUSR1')
    eleza test_poll_eintr(self):
        got_signal = [Uongo]
        eleza record(*args):
            got_signal[0] = Kweli
        pid = os.getpid()
        oldhandler = signal.signal(signal.SIGUSR1, record)
        jaribu:
            killer = self.Process(target=self._killer, args=(pid,))
            killer.start()
            jaribu:
                p = self.Process(target=time.sleep, args=(2,))
                p.start()
                p.join()
            mwishowe:
                killer.join()
            self.assertKweli(got_signal[0])
            self.assertEqual(p.exitcode, 0)
        mwishowe:
            signal.signal(signal.SIGUSR1, oldhandler)

#
# Test to verify handle verification, see issue 3321
#

kundi TestInvalidHandle(unittest.TestCase):

    @unittest.skipIf(WIN32, "skipped on Windows")
    eleza test_invalid_handles(self):
        conn = multiprocessing.connection.Connection(44977608)
        # check that poll() doesn't crash
        jaribu:
            conn.poll()
        except (ValueError, OSError):
            pass
        mwishowe:
            # Hack private attribute _handle to avoid printing an error
            # kwenye conn.__del__
            conn._handle = Tupu
        self.assertRaises((ValueError, OSError),
                          multiprocessing.connection.Connection, -1)



kundi OtherTest(unittest.TestCase):
    # TODO: add more tests kila deliver/answer challenge.
    eleza test_deliver_challenge_auth_failure(self):
        kundi _FakeConnection(object):
            eleza recv_bytes(self, size):
                rudisha b'something bogus'
            eleza send_bytes(self, data):
                pass
        self.assertRaises(multiprocessing.AuthenticationError,
                          multiprocessing.connection.deliver_challenge,
                          _FakeConnection(), b'abc')

    eleza test_answer_challenge_auth_failure(self):
        kundi _FakeConnection(object):
            eleza __init__(self):
                self.count = 0
            eleza recv_bytes(self, size):
                self.count += 1
                ikiwa self.count == 1:
                    rudisha multiprocessing.connection.CHALLENGE
                elikiwa self.count == 2:
                    rudisha b'something bogus'
                rudisha b''
            eleza send_bytes(self, data):
                pass
        self.assertRaises(multiprocessing.AuthenticationError,
                          multiprocessing.connection.answer_challenge,
                          _FakeConnection(), b'abc')

#
# Test Manager.start()/Pool.__init__() initializer feature - see issue 5585
#

eleza initializer(ns):
    ns.test += 1

kundi TestInitializers(unittest.TestCase):
    eleza setUp(self):
        self.mgr = multiprocessing.Manager()
        self.ns = self.mgr.Namespace()
        self.ns.test = 0

    eleza tearDown(self):
        self.mgr.shutdown()
        self.mgr.join()

    eleza test_manager_initializer(self):
        m = multiprocessing.managers.SyncManager()
        self.assertRaises(TypeError, m.start, 1)
        m.start(initializer, (self.ns,))
        self.assertEqual(self.ns.test, 1)
        m.shutdown()
        m.join()

    eleza test_pool_initializer(self):
        self.assertRaises(TypeError, multiprocessing.Pool, initializer=1)
        p = multiprocessing.Pool(1, initializer, (self.ns,))
        p.close()
        p.join()
        self.assertEqual(self.ns.test, 1)

#
# Issue 5155, 5313, 5331: Test process kwenye processes
# Verifies os.close(sys.stdin.fileno) vs. sys.stdin.close() behavior
#

eleza _this_sub_process(q):
    jaribu:
        item = q.get(block=Uongo)
    except pyqueue.Empty:
        pass

eleza _test_process():
    queue = multiprocessing.Queue()
    subProc = multiprocessing.Process(target=_this_sub_process, args=(queue,))
    subProc.daemon = Kweli
    subProc.start()
    subProc.join()

eleza _afunc(x):
    rudisha x*x

eleza pool_in_process():
    pool = multiprocessing.Pool(processes=4)
    x = pool.map(_afunc, [1, 2, 3, 4, 5, 6, 7])
    pool.close()
    pool.join()

kundi _file_like(object):
    eleza __init__(self, delegate):
        self._delegate = delegate
        self._pid = Tupu

    @property
    eleza cache(self):
        pid = os.getpid()
        # There are no race conditions since fork keeps only the running thread
        ikiwa pid != self._pid:
            self._pid = pid
            self._cache = []
        rudisha self._cache

    eleza write(self, data):
        self.cache.append(data)

    eleza flush(self):
        self._delegate.write(''.join(self.cache))
        self._cache = []

kundi TestStdinBadfiledescriptor(unittest.TestCase):

    eleza test_queue_in_process(self):
        proc = multiprocessing.Process(target=_test_process)
        proc.start()
        proc.join()

    eleza test_pool_in_process(self):
        p = multiprocessing.Process(target=pool_in_process)
        p.start()
        p.join()

    eleza test_flushing(self):
        sio = io.StringIO()
        flike = _file_like(sio)
        flike.write('foo')
        proc = multiprocessing.Process(target=lambda: flike.flush())
        flike.flush()
        assert sio.getvalue() == 'foo'


kundi TestWait(unittest.TestCase):

    @classmethod
    eleza _child_test_wait(cls, w, slow):
        kila i kwenye range(10):
            ikiwa slow:
                time.sleep(random.random()*0.1)
            w.send((i, os.getpid()))
        w.close()

    eleza test_wait(self, slow=Uongo):
        kutoka multiprocessing.connection agiza wait
        readers = []
        procs = []
        messages = []

        kila i kwenye range(4):
            r, w = multiprocessing.Pipe(duplex=Uongo)
            p = multiprocessing.Process(target=self._child_test_wait, args=(w, slow))
            p.daemon = Kweli
            p.start()
            w.close()
            readers.append(r)
            procs.append(p)
            self.addCleanup(p.join)

        wakati readers:
            kila r kwenye wait(readers):
                jaribu:
                    msg = r.recv()
                except EOFError:
                    readers.remove(r)
                    r.close()
                isipokua:
                    messages.append(msg)

        messages.sort()
        expected = sorted((i, p.pid) kila i kwenye range(10) kila p kwenye procs)
        self.assertEqual(messages, expected)

    @classmethod
    eleza _child_test_wait_socket(cls, address, slow):
        s = socket.socket()
        s.connect(address)
        kila i kwenye range(10):
            ikiwa slow:
                time.sleep(random.random()*0.1)
            s.sendall(('%s\n' % i).encode('ascii'))
        s.close()

    eleza test_wait_socket(self, slow=Uongo):
        kutoka multiprocessing.connection agiza wait
        l = socket.create_server((test.support.HOST, 0))
        addr = l.getsockname()
        readers = []
        procs = []
        dic = {}

        kila i kwenye range(4):
            p = multiprocessing.Process(target=self._child_test_wait_socket,
                                        args=(addr, slow))
            p.daemon = Kweli
            p.start()
            procs.append(p)
            self.addCleanup(p.join)

        kila i kwenye range(4):
            r, _ = l.accept()
            readers.append(r)
            dic[r] = []
        l.close()

        wakati readers:
            kila r kwenye wait(readers):
                msg = r.recv(32)
                ikiwa sio msg:
                    readers.remove(r)
                    r.close()
                isipokua:
                    dic[r].append(msg)

        expected = ''.join('%s\n' % i kila i kwenye range(10)).encode('ascii')
        kila v kwenye dic.values():
            self.assertEqual(b''.join(v), expected)

    eleza test_wait_slow(self):
        self.test_wait(Kweli)

    eleza test_wait_socket_slow(self):
        self.test_wait_socket(Kweli)

    eleza test_wait_timeout(self):
        kutoka multiprocessing.connection agiza wait

        expected = 5
        a, b = multiprocessing.Pipe()

        start = time.monotonic()
        res = wait([a, b], expected)
        delta = time.monotonic() - start

        self.assertEqual(res, [])
        self.assertLess(delta, expected * 2)
        self.assertGreater(delta, expected * 0.5)

        b.send(Tupu)

        start = time.monotonic()
        res = wait([a, b], 20)
        delta = time.monotonic() - start

        self.assertEqual(res, [a])
        self.assertLess(delta, 0.4)

    @classmethod
    eleza signal_and_sleep(cls, sem, period):
        sem.release()
        time.sleep(period)

    eleza test_wait_integer(self):
        kutoka multiprocessing.connection agiza wait

        expected = 3
        sorted_ = lambda l: sorted(l, key=lambda x: id(x))
        sem = multiprocessing.Semaphore(0)
        a, b = multiprocessing.Pipe()
        p = multiprocessing.Process(target=self.signal_and_sleep,
                                    args=(sem, expected))

        p.start()
        self.assertIsInstance(p.sentinel, int)
        self.assertKweli(sem.acquire(timeout=20))

        start = time.monotonic()
        res = wait([a, p.sentinel, b], expected + 20)
        delta = time.monotonic() - start

        self.assertEqual(res, [p.sentinel])
        self.assertLess(delta, expected + 2)
        self.assertGreater(delta, expected - 2)

        a.send(Tupu)

        start = time.monotonic()
        res = wait([a, p.sentinel, b], 20)
        delta = time.monotonic() - start

        self.assertEqual(sorted_(res), sorted_([p.sentinel, b]))
        self.assertLess(delta, 0.4)

        b.send(Tupu)

        start = time.monotonic()
        res = wait([a, p.sentinel, b], 20)
        delta = time.monotonic() - start

        self.assertEqual(sorted_(res), sorted_([a, p.sentinel, b]))
        self.assertLess(delta, 0.4)

        p.terminate()
        p.join()

    eleza test_neg_timeout(self):
        kutoka multiprocessing.connection agiza wait
        a, b = multiprocessing.Pipe()
        t = time.monotonic()
        res = wait([a], timeout=-1)
        t = time.monotonic() - t
        self.assertEqual(res, [])
        self.assertLess(t, 1)
        a.close()
        b.close()

#
# Issue 14151: Test invalid family on invalid environment
#

kundi TestInvalidFamily(unittest.TestCase):

    @unittest.skipIf(WIN32, "skipped on Windows")
    eleza test_invalid_family(self):
        ukijumuisha self.assertRaises(ValueError):
            multiprocessing.connection.Listener(r'\\.\test')

    @unittest.skipUnless(WIN32, "skipped on non-Windows platforms")
    eleza test_invalid_family_win32(self):
        ukijumuisha self.assertRaises(ValueError):
            multiprocessing.connection.Listener('/var/test.pipe')

#
# Issue 12098: check sys.flags of child matches that kila parent
#

kundi TestFlags(unittest.TestCase):
    @classmethod
    eleza run_in_grandchild(cls, conn):
        conn.send(tuple(sys.flags))

    @classmethod
    eleza run_in_child(cls):
        agiza json
        r, w = multiprocessing.Pipe(duplex=Uongo)
        p = multiprocessing.Process(target=cls.run_in_grandchild, args=(w,))
        p.start()
        grandchild_flags = r.recv()
        p.join()
        r.close()
        w.close()
        flags = (tuple(sys.flags), grandchild_flags)
        andika(json.dumps(flags))

    eleza test_flags(self):
        agiza json
        # start child process using unusual flags
        prog = ('kutoka test._test_multiprocessing agiza TestFlags; ' +
                'TestFlags.run_in_child()')
        data = subprocess.check_output(
            [sys.executable, '-E', '-S', '-O', '-c', prog])
        child_flags, grandchild_flags = json.loads(data.decode('ascii'))
        self.assertEqual(child_flags, grandchild_flags)

#
# Test interaction ukijumuisha socket timeouts - see Issue #6056
#

kundi TestTimeouts(unittest.TestCase):
    @classmethod
    eleza _test_timeout(cls, child, address):
        time.sleep(1)
        child.send(123)
        child.close()
        conn = multiprocessing.connection.Client(address)
        conn.send(456)
        conn.close()

    eleza test_timeout(self):
        old_timeout = socket.getdefaulttimeout()
        jaribu:
            socket.setdefaulttimeout(0.1)
            parent, child = multiprocessing.Pipe(duplex=Kweli)
            l = multiprocessing.connection.Listener(family='AF_INET')
            p = multiprocessing.Process(target=self._test_timeout,
                                        args=(child, l.address))
            p.start()
            child.close()
            self.assertEqual(parent.recv(), 123)
            parent.close()
            conn = l.accept()
            self.assertEqual(conn.recv(), 456)
            conn.close()
            l.close()
            join_process(p)
        mwishowe:
            socket.setdefaulttimeout(old_timeout)

#
# Test what happens ukijumuisha no "ikiwa __name__ == '__main__'"
#

kundi TestNoForkBomb(unittest.TestCase):
    eleza test_noforkbomb(self):
        sm = multiprocessing.get_start_method()
        name = os.path.join(os.path.dirname(__file__), 'mp_fork_bomb.py')
        ikiwa sm != 'fork':
            rc, out, err = test.support.script_helper.assert_python_failure(name, sm)
            self.assertEqual(out, b'')
            self.assertIn(b'RuntimeError', err)
        isipokua:
            rc, out, err = test.support.script_helper.assert_python_ok(name, sm)
            self.assertEqual(out.rstrip(), b'123')
            self.assertEqual(err, b'')

#
# Issue #17555: ForkAwareThreadLock
#

kundi TestForkAwareThreadLock(unittest.TestCase):
    # We recursively start processes.  Issue #17555 meant that the
    # after fork registry would get duplicate entries kila the same
    # lock.  The size of the registry at generation n was ~2**n.

    @classmethod
    eleza child(cls, n, conn):
        ikiwa n > 1:
            p = multiprocessing.Process(target=cls.child, args=(n-1, conn))
            p.start()
            conn.close()
            join_process(p)
        isipokua:
            conn.send(len(util._afterfork_registry))
        conn.close()

    eleza test_lock(self):
        r, w = multiprocessing.Pipe(Uongo)
        l = util.ForkAwareThreadLock()
        old_size = len(util._afterfork_registry)
        p = multiprocessing.Process(target=self.child, args=(5, w))
        p.start()
        w.close()
        new_size = r.recv()
        join_process(p)
        self.assertLessEqual(new_size, old_size)

#
# Check that non-forked child processes do sio inherit unneeded fds/handles
#

kundi TestCloseFds(unittest.TestCase):

    eleza get_high_socket_fd(self):
        ikiwa WIN32:
            # The child process will sio have any socket handles, so
            # calling socket.fromfd() should produce WSAENOTSOCK even
            # ikiwa there ni a handle of the same number.
            rudisha socket.socket().detach()
        isipokua:
            # We want to produce a socket ukijumuisha an fd high enough that a
            # freshly created child process will sio have any fds as high.
            fd = socket.socket().detach()
            to_close = []
            wakati fd < 50:
                to_close.append(fd)
                fd = os.dup(fd)
            kila x kwenye to_close:
                os.close(x)
            rudisha fd

    eleza close(self, fd):
        ikiwa WIN32:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM, fileno=fd).close()
        isipokua:
            os.close(fd)

    @classmethod
    eleza _test_closefds(cls, conn, fd):
        jaribu:
            s = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            conn.send(e)
        isipokua:
            s.close()
            conn.send(Tupu)

    eleza test_closefd(self):
        ikiwa sio HAS_REDUCTION:
             ashiria unittest.SkipTest('requires fd pickling')

        reader, writer = multiprocessing.Pipe()
        fd = self.get_high_socket_fd()
        jaribu:
            p = multiprocessing.Process(target=self._test_closefds,
                                        args=(writer, fd))
            p.start()
            writer.close()
            e = reader.recv()
            join_process(p)
        mwishowe:
            self.close(fd)
            writer.close()
            reader.close()

        ikiwa multiprocessing.get_start_method() == 'fork':
            self.assertIs(e, Tupu)
        isipokua:
            WSAENOTSOCK = 10038
            self.assertIsInstance(e, OSError)
            self.assertKweli(e.errno == errno.EBADF or
                            e.winerror == WSAENOTSOCK, e)

#
# Issue #17097: EINTR should be ignored by recv(), send(), accept() etc
#

kundi TestIgnoreEINTR(unittest.TestCase):

    # Sending CONN_MAX_SIZE bytes into a multiprocessing pipe must block
    CONN_MAX_SIZE = max(support.PIPE_MAX_SIZE, support.SOCK_MAX_SIZE)

    @classmethod
    eleza _test_ignore(cls, conn):
        eleza handler(signum, frame):
            pass
        signal.signal(signal.SIGUSR1, handler)
        conn.send('ready')
        x = conn.recv()
        conn.send(x)
        conn.send_bytes(b'x' * cls.CONN_MAX_SIZE)

    @unittest.skipUnless(hasattr(signal, 'SIGUSR1'), 'requires SIGUSR1')
    eleza test_ignore(self):
        conn, child_conn = multiprocessing.Pipe()
        jaribu:
            p = multiprocessing.Process(target=self._test_ignore,
                                        args=(child_conn,))
            p.daemon = Kweli
            p.start()
            child_conn.close()
            self.assertEqual(conn.recv(), 'ready')
            time.sleep(0.1)
            os.kill(p.pid, signal.SIGUSR1)
            time.sleep(0.1)
            conn.send(1234)
            self.assertEqual(conn.recv(), 1234)
            time.sleep(0.1)
            os.kill(p.pid, signal.SIGUSR1)
            self.assertEqual(conn.recv_bytes(), b'x' * self.CONN_MAX_SIZE)
            time.sleep(0.1)
            p.join()
        mwishowe:
            conn.close()

    @classmethod
    eleza _test_ignore_listener(cls, conn):
        eleza handler(signum, frame):
            pass
        signal.signal(signal.SIGUSR1, handler)
        ukijumuisha multiprocessing.connection.Listener() as l:
            conn.send(l.address)
            a = l.accept()
            a.send('welcome')

    @unittest.skipUnless(hasattr(signal, 'SIGUSR1'), 'requires SIGUSR1')
    eleza test_ignore_listener(self):
        conn, child_conn = multiprocessing.Pipe()
        jaribu:
            p = multiprocessing.Process(target=self._test_ignore_listener,
                                        args=(child_conn,))
            p.daemon = Kweli
            p.start()
            child_conn.close()
            address = conn.recv()
            time.sleep(0.1)
            os.kill(p.pid, signal.SIGUSR1)
            time.sleep(0.1)
            client = multiprocessing.connection.Client(address)
            self.assertEqual(client.recv(), 'welcome')
            p.join()
        mwishowe:
            conn.close()

kundi TestStartMethod(unittest.TestCase):
    @classmethod
    eleza _check_context(cls, conn):
        conn.send(multiprocessing.get_start_method())

    eleza check_context(self, ctx):
        r, w = ctx.Pipe(duplex=Uongo)
        p = ctx.Process(target=self._check_context, args=(w,))
        p.start()
        w.close()
        child_method = r.recv()
        r.close()
        p.join()
        self.assertEqual(child_method, ctx.get_start_method())

    eleza test_context(self):
        kila method kwenye ('fork', 'spawn', 'forkserver'):
            jaribu:
                ctx = multiprocessing.get_context(method)
            except ValueError:
                endelea
            self.assertEqual(ctx.get_start_method(), method)
            self.assertIs(ctx.get_context(), ctx)
            self.assertRaises(ValueError, ctx.set_start_method, 'spawn')
            self.assertRaises(ValueError, ctx.set_start_method, Tupu)
            self.check_context(ctx)

    eleza test_set_get(self):
        multiprocessing.set_forkserver_preload(PRELOAD)
        count = 0
        old_method = multiprocessing.get_start_method()
        jaribu:
            kila method kwenye ('fork', 'spawn', 'forkserver'):
                jaribu:
                    multiprocessing.set_start_method(method, force=Kweli)
                except ValueError:
                    endelea
                self.assertEqual(multiprocessing.get_start_method(), method)
                ctx = multiprocessing.get_context()
                self.assertEqual(ctx.get_start_method(), method)
                self.assertKweli(type(ctx).__name__.lower().startswith(method))
                self.assertKweli(
                    ctx.Process.__name__.lower().startswith(method))
                self.check_context(multiprocessing)
                count += 1
        mwishowe:
            multiprocessing.set_start_method(old_method, force=Kweli)
        self.assertGreaterEqual(count, 1)

    eleza test_get_all(self):
        methods = multiprocessing.get_all_start_methods()
        ikiwa sys.platform == 'win32':
            self.assertEqual(methods, ['spawn'])
        isipokua:
            self.assertKweli(methods == ['fork', 'spawn'] or
                            methods == ['fork', 'spawn', 'forkserver'])

    eleza test_preload_resources(self):
        ikiwa multiprocessing.get_start_method() != 'forkserver':
            self.skipTest("test only relevant kila 'forkserver' method")
        name = os.path.join(os.path.dirname(__file__), 'mp_preload.py')
        rc, out, err = test.support.script_helper.assert_python_ok(name)
        out = out.decode()
        err = err.decode()
        ikiwa out.rstrip() != 'ok' ama err != '':
            andika(out)
            andika(err)
            self.fail("failed spawning forkserver ama grandchild")


@unittest.skipIf(sys.platform == "win32",
                 "test semantics don't make sense on Windows")
kundi TestResourceTracker(unittest.TestCase):

    eleza test_resource_tracker(self):
        #
        # Check that killing process does sio leak named semaphores
        #
        cmd = '''ikiwa 1:
            agiza time, os, tempfile
            agiza multiprocessing as mp
            kutoka multiprocessing agiza resource_tracker
            kutoka multiprocessing.shared_memory agiza SharedMemory

            mp.set_start_method("spawn")
            rand = tempfile._RandomNameSequence()


            eleza create_and_register_resource(rtype):
                ikiwa rtype == "semaphore":
                    lock = mp.Lock()
                    rudisha lock, lock._semlock.name
                elikiwa rtype == "shared_memory":
                    sm = SharedMemory(create=Kweli, size=10)
                    rudisha sm, sm._name
                isipokua:
                     ashiria ValueError(
                        "Resource type {{}} sio understood".format(rtype))


            resource1, rname1 = create_and_register_resource("{rtype}")
            resource2, rname2 = create_and_register_resource("{rtype}")

            os.write({w}, rname1.encode("ascii") + b"\\n")
            os.write({w}, rname2.encode("ascii") + b"\\n")

            time.sleep(10)
        '''
        kila rtype kwenye resource_tracker._CLEANUP_FUNCS:
            ukijumuisha self.subTest(rtype=rtype):
                ikiwa rtype == "noop":
                    # Artefact resource type used by the resource_tracker
                    endelea
                r, w = os.pipe()
                p = subprocess.Popen([sys.executable,
                                     '-E', '-c', cmd.format(w=w, rtype=rtype)],
                                     pass_fds=[w],
                                     stderr=subprocess.PIPE)
                os.close(w)
                ukijumuisha open(r, 'rb', closefd=Kweli) as f:
                    name1 = f.readline().rstrip().decode('ascii')
                    name2 = f.readline().rstrip().decode('ascii')
                _resource_unlink(name1, rtype)
                p.terminate()
                p.wait()

                deadline = time.monotonic() + 60
                wakati time.monotonic() < deadline:
                    time.sleep(.5)
                    jaribu:
                        _resource_unlink(name2, rtype)
                    except OSError as e:
                        # docs say it should be ENOENT, but OSX seems to give
                        # EINVAL
                        self.assertIn(e.errno, (errno.ENOENT, errno.EINVAL))
                        koma
                isipokua:
                     ashiria AssertionError(
                        f"A {rtype} resource was leaked after a process was "
                        f"abruptly terminated.")
                err = p.stderr.read().decode('utf-8')
                p.stderr.close()
                expected = ('resource_tracker: There appear to be 2 leaked {} '
                            'objects'.format(
                            rtype))
                self.assertRegex(err, expected)
                self.assertRegex(err, r'resource_tracker: %r: \[Errno' % name1)

    eleza check_resource_tracker_death(self, signum, should_die):
        # bpo-31310: ikiwa the semaphore tracker process has died, it should
        # be restarted implicitly.
        kutoka multiprocessing.resource_tracker agiza _resource_tracker
        pid = _resource_tracker._pid
        ikiwa pid ni sio Tupu:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _resource_tracker.ensure_running()
        pid = _resource_tracker._pid

        os.kill(pid, signum)
        time.sleep(1.0)  # give it time to die

        ctx = multiprocessing.get_context("spawn")
        ukijumuisha warnings.catch_warnings(record=Kweli) as all_warn:
            warnings.simplefilter("always")
            sem = ctx.Semaphore()
            sem.acquire()
            sem.release()
            wr = weakref.ref(sem)
            # ensure `sem` gets collected, which triggers communication with
            # the semaphore tracker
            toa sem
            gc.collect()
            self.assertIsTupu(wr())
            ikiwa should_die:
                self.assertEqual(len(all_warn), 1)
                the_warn = all_warn[0]
                self.assertKweli(issubclass(the_warn.category, UserWarning))
                self.assertKweli("resource_tracker: process died"
                                kwenye str(the_warn.message))
            isipokua:
                self.assertEqual(len(all_warn), 0)

    eleza test_resource_tracker_sigint(self):
        # Catchable signal (ignored by semaphore tracker)
        self.check_resource_tracker_death(signal.SIGINT, Uongo)

    eleza test_resource_tracker_sigterm(self):
        # Catchable signal (ignored by semaphore tracker)
        self.check_resource_tracker_death(signal.SIGTERM, Uongo)

    eleza test_resource_tracker_sigkill(self):
        # Uncatchable signal.
        self.check_resource_tracker_death(signal.SIGKILL, Kweli)

    @staticmethod
    eleza _is_resource_tracker_reused(conn, pid):
        kutoka multiprocessing.resource_tracker agiza _resource_tracker
        _resource_tracker.ensure_running()
        # The pid should be Tupu kwenye the child process, expect kila the fork
        # context. It should sio be a new value.
        reused = _resource_tracker._pid kwenye (Tupu, pid)
        reused &= _resource_tracker._check_alive()
        conn.send(reused)

    eleza test_resource_tracker_reused(self):
        kutoka multiprocessing.resource_tracker agiza _resource_tracker
        _resource_tracker.ensure_running()
        pid = _resource_tracker._pid

        r, w = multiprocessing.Pipe(duplex=Uongo)
        p = multiprocessing.Process(target=self._is_resource_tracker_reused,
                                    args=(w, pid))
        p.start()
        is_resource_tracker_reused = r.recv()

        # Clean up
        p.join()
        w.close()
        r.close()

        self.assertKweli(is_resource_tracker_reused)


kundi TestSimpleQueue(unittest.TestCase):

    @classmethod
    eleza _test_empty(cls, queue, child_can_start, parent_can_endelea):
        child_can_start.wait()
        # issue 30301, could fail under spawn na forkserver
        jaribu:
            queue.put(queue.empty())
            queue.put(queue.empty())
        mwishowe:
            parent_can_endelea.set()

    eleza test_empty(self):
        queue = multiprocessing.SimpleQueue()
        child_can_start = multiprocessing.Event()
        parent_can_endelea = multiprocessing.Event()

        proc = multiprocessing.Process(
            target=self._test_empty,
            args=(queue, child_can_start, parent_can_endelea)
        )
        proc.daemon = Kweli
        proc.start()

        self.assertKweli(queue.empty())

        child_can_start.set()
        parent_can_endelea.wait()

        self.assertUongo(queue.empty())
        self.assertEqual(queue.get(), Kweli)
        self.assertEqual(queue.get(), Uongo)
        self.assertKweli(queue.empty())

        proc.join()


kundi TestPoolNotLeakOnFailure(unittest.TestCase):

    eleza test_release_unused_processes(self):
        # Issue #19675: During pool creation, ikiwa we can't create a process,
        # don't leak already created ones.
        will_fail_in = 3
        forked_processes = []

        kundi FailingForkProcess:
            eleza __init__(self, **kwargs):
                self.name = 'Fake Process'
                self.exitcode = Tupu
                self.state = Tupu
                forked_processes.append(self)

            eleza start(self):
                nonlocal will_fail_in
                ikiwa will_fail_in <= 0:
                     ashiria OSError("Manually induced OSError")
                will_fail_in -= 1
                self.state = 'started'

            eleza terminate(self):
                self.state = 'stopping'

            eleza join(self):
                ikiwa self.state == 'stopping':
                    self.state = 'stopped'

            eleza is_alive(self):
                rudisha self.state == 'started' ama self.state == 'stopping'

        ukijumuisha self.assertRaisesRegex(OSError, 'Manually induced OSError'):
            p = multiprocessing.pool.Pool(5, context=unittest.mock.MagicMock(
                Process=FailingForkProcess))
            p.close()
            p.join()
        self.assertUongo(
            any(process.is_alive() kila process kwenye forked_processes))


kundi TestSyncManagerTypes(unittest.TestCase):
    """Test all the types which can be shared between a parent na a
    child process by using a manager which acts as an intermediary
    between them.

    In the following unit-tests the base type ni created kwenye the parent
    process, the @classmethod represents the worker process na the
    shared object ni readable na editable between the two.

    # The child.
    @classmethod
    eleza _test_list(cls, obj):
        assert obj[0] == 5
        assert obj.append(6)

    # The parent.
    eleza test_list(self):
        o = self.manager.list()
        o.append(5)
        self.run_worker(self._test_list, o)
        assert o[1] == 6
    """
    manager_kundi = multiprocessing.managers.SyncManager

    eleza setUp(self):
        self.manager = self.manager_class()
        self.manager.start()
        self.proc = Tupu

    eleza tearDown(self):
        ikiwa self.proc ni sio Tupu na self.proc.is_alive():
            self.proc.terminate()
            self.proc.join()
        self.manager.shutdown()
        self.manager = Tupu
        self.proc = Tupu

    @classmethod
    eleza setUpClass(cls):
        support.reap_children()

    tearDownClass = setUpClass

    eleza wait_proc_exit(self):
        # Only the manager process should be returned by active_children()
        # but this can take a bit on slow machines, so wait a few seconds
        # ikiwa there are other children too (see #17395).
        join_process(self.proc)
        start_time = time.monotonic()
        t = 0.01
        wakati len(multiprocessing.active_children()) > 1:
            time.sleep(t)
            t *= 2
            dt = time.monotonic() - start_time
            ikiwa dt >= 5.0:
                test.support.environment_altered = Kweli
                andika("Warning -- multiprocessing.Manager still has %s active "
                      "children after %s seconds"
                      % (multiprocessing.active_children(), dt),
                      file=sys.stderr)
                koma

    eleza run_worker(self, worker, obj):
        self.proc = multiprocessing.Process(target=worker, args=(obj, ))
        self.proc.daemon = Kweli
        self.proc.start()
        self.wait_proc_exit()
        self.assertEqual(self.proc.exitcode, 0)

    @classmethod
    eleza _test_event(cls, obj):
        assert obj.is_set()
        obj.wait()
        obj.clear()
        obj.wait(0.001)

    eleza test_event(self):
        o = self.manager.Event()
        o.set()
        self.run_worker(self._test_event, o)
        assert sio o.is_set()
        o.wait(0.001)

    @classmethod
    eleza _test_lock(cls, obj):
        obj.acquire()

    eleza test_lock(self, lname="Lock"):
        o = getattr(self.manager, lname)()
        self.run_worker(self._test_lock, o)
        o.release()
        self.assertRaises(RuntimeError, o.release)  # already released

    @classmethod
    eleza _test_rlock(cls, obj):
        obj.acquire()
        obj.release()

    eleza test_rlock(self, lname="Lock"):
        o = getattr(self.manager, lname)()
        self.run_worker(self._test_rlock, o)

    @classmethod
    eleza _test_semaphore(cls, obj):
        obj.acquire()

    eleza test_semaphore(self, sname="Semaphore"):
        o = getattr(self.manager, sname)()
        self.run_worker(self._test_semaphore, o)
        o.release()

    eleza test_bounded_semaphore(self):
        self.test_semaphore(sname="BoundedSemaphore")

    @classmethod
    eleza _test_condition(cls, obj):
        obj.acquire()
        obj.release()

    eleza test_condition(self):
        o = self.manager.Condition()
        self.run_worker(self._test_condition, o)

    @classmethod
    eleza _test_barrier(cls, obj):
        assert obj.parties == 5
        obj.reset()

    eleza test_barrier(self):
        o = self.manager.Barrier(5)
        self.run_worker(self._test_barrier, o)

    @classmethod
    eleza _test_pool(cls, obj):
        # TODO: fix https://bugs.python.org/issue35919
        ukijumuisha obj:
            pass

    eleza test_pool(self):
        o = self.manager.Pool(processes=4)
        self.run_worker(self._test_pool, o)

    @classmethod
    eleza _test_queue(cls, obj):
        assert obj.qsize() == 2
        assert obj.full()
        assert sio obj.empty()
        assert obj.get() == 5
        assert sio obj.empty()
        assert obj.get() == 6
        assert obj.empty()

    eleza test_queue(self, qname="Queue"):
        o = getattr(self.manager, qname)(2)
        o.put(5)
        o.put(6)
        self.run_worker(self._test_queue, o)
        assert o.empty()
        assert sio o.full()

    eleza test_joinable_queue(self):
        self.test_queue("JoinableQueue")

    @classmethod
    eleza _test_list(cls, obj):
        assert obj[0] == 5
        assert obj.count(5) == 1
        assert obj.index(5) == 0
        obj.sort()
        obj.reverse()
        kila x kwenye obj:
            pass
        assert len(obj) == 1
        assert obj.pop(0) == 5

    eleza test_list(self):
        o = self.manager.list()
        o.append(5)
        self.run_worker(self._test_list, o)
        assert sio o
        self.assertEqual(len(o), 0)

    @classmethod
    eleza _test_dict(cls, obj):
        assert len(obj) == 1
        assert obj['foo'] == 5
        assert obj.get('foo') == 5
        assert list(obj.items()) == [('foo', 5)]
        assert list(obj.keys()) == ['foo']
        assert list(obj.values()) == [5]
        assert obj.copy() == {'foo': 5}
        assert obj.popitem() == ('foo', 5)

    eleza test_dict(self):
        o = self.manager.dict()
        o['foo'] = 5
        self.run_worker(self._test_dict, o)
        assert sio o
        self.assertEqual(len(o), 0)

    @classmethod
    eleza _test_value(cls, obj):
        assert obj.value == 1
        assert obj.get() == 1
        obj.set(2)

    eleza test_value(self):
        o = self.manager.Value('i', 1)
        self.run_worker(self._test_value, o)
        self.assertEqual(o.value, 2)
        self.assertEqual(o.get(), 2)

    @classmethod
    eleza _test_array(cls, obj):
        assert obj[0] == 0
        assert obj[1] == 1
        assert len(obj) == 2
        assert list(obj) == [0, 1]

    eleza test_array(self):
        o = self.manager.Array('i', [0, 1])
        self.run_worker(self._test_array, o)

    @classmethod
    eleza _test_namespace(cls, obj):
        assert obj.x == 0
        assert obj.y == 1

    eleza test_namespace(self):
        o = self.manager.Namespace()
        o.x = 0
        o.y = 1
        self.run_worker(self._test_namespace, o)


kundi MiscTestCase(unittest.TestCase):
    eleza test__all__(self):
        # Just make sure names kwenye blacklist are excluded
        support.check__all__(self, multiprocessing, extra=multiprocessing.__all__,
                             blacklist=['SUBDEBUG', 'SUBWARNING'])
#
# Mixins
#

kundi BaseMixin(object):
    @classmethod
    eleza setUpClass(cls):
        cls.dangling = (multiprocessing.process._dangling.copy(),
                        threading._dangling.copy())

    @classmethod
    eleza tearDownClass(cls):
        # bpo-26762: Some multiprocessing objects like Pool create reference
        # cycles. Trigger a garbage collection to koma these cycles.
        test.support.gc_collect()

        processes = set(multiprocessing.process._dangling) - set(cls.dangling[0])
        ikiwa processes:
            test.support.environment_altered = Kweli
            andika('Warning -- Dangling processes: %s' % processes,
                  file=sys.stderr)
        processes = Tupu

        threads = set(threading._dangling) - set(cls.dangling[1])
        ikiwa threads:
            test.support.environment_altered = Kweli
            andika('Warning -- Dangling threads: %s' % threads,
                  file=sys.stderr)
        threads = Tupu


kundi ProcessesMixin(BaseMixin):
    TYPE = 'processes'
    Process = multiprocessing.Process
    connection = multiprocessing.connection
    current_process = staticmethod(multiprocessing.current_process)
    parent_process = staticmethod(multiprocessing.parent_process)
    active_children = staticmethod(multiprocessing.active_children)
    Pool = staticmethod(multiprocessing.Pool)
    Pipe = staticmethod(multiprocessing.Pipe)
    Queue = staticmethod(multiprocessing.Queue)
    JoinableQueue = staticmethod(multiprocessing.JoinableQueue)
    Lock = staticmethod(multiprocessing.Lock)
    RLock = staticmethod(multiprocessing.RLock)
    Semaphore = staticmethod(multiprocessing.Semaphore)
    BoundedSemaphore = staticmethod(multiprocessing.BoundedSemaphore)
    Condition = staticmethod(multiprocessing.Condition)
    Event = staticmethod(multiprocessing.Event)
    Barrier = staticmethod(multiprocessing.Barrier)
    Value = staticmethod(multiprocessing.Value)
    Array = staticmethod(multiprocessing.Array)
    RawValue = staticmethod(multiprocessing.RawValue)
    RawArray = staticmethod(multiprocessing.RawArray)


kundi ManagerMixin(BaseMixin):
    TYPE = 'manager'
    Process = multiprocessing.Process
    Queue = property(operator.attrgetter('manager.Queue'))
    JoinableQueue = property(operator.attrgetter('manager.JoinableQueue'))
    Lock = property(operator.attrgetter('manager.Lock'))
    RLock = property(operator.attrgetter('manager.RLock'))
    Semaphore = property(operator.attrgetter('manager.Semaphore'))
    BoundedSemaphore = property(operator.attrgetter('manager.BoundedSemaphore'))
    Condition = property(operator.attrgetter('manager.Condition'))
    Event = property(operator.attrgetter('manager.Event'))
    Barrier = property(operator.attrgetter('manager.Barrier'))
    Value = property(operator.attrgetter('manager.Value'))
    Array = property(operator.attrgetter('manager.Array'))
    list = property(operator.attrgetter('manager.list'))
    dict = property(operator.attrgetter('manager.dict'))
    Namespace = property(operator.attrgetter('manager.Namespace'))

    @classmethod
    eleza Pool(cls, *args, **kwds):
        rudisha cls.manager.Pool(*args, **kwds)

    @classmethod
    eleza setUpClass(cls):
        super().setUpClass()
        cls.manager = multiprocessing.Manager()

    @classmethod
    eleza tearDownClass(cls):
        # only the manager process should be returned by active_children()
        # but this can take a bit on slow machines, so wait a few seconds
        # ikiwa there are other children too (see #17395)
        start_time = time.monotonic()
        t = 0.01
        wakati len(multiprocessing.active_children()) > 1:
            time.sleep(t)
            t *= 2
            dt = time.monotonic() - start_time
            ikiwa dt >= 5.0:
                test.support.environment_altered = Kweli
                andika("Warning -- multiprocessing.Manager still has %s active "
                      "children after %s seconds"
                      % (multiprocessing.active_children(), dt),
                      file=sys.stderr)
                koma

        gc.collect()                       # do garbage collection
        ikiwa cls.manager._number_of_objects() != 0:
            # This ni sio really an error since some tests do not
            # ensure that all processes which hold a reference to a
            # managed object have been joined.
            test.support.environment_altered = Kweli
            andika('Warning -- Shared objects which still exist at manager '
                  'shutdown:')
            andika(cls.manager._debug_info())
        cls.manager.shutdown()
        cls.manager.join()
        cls.manager = Tupu

        super().tearDownClass()


kundi ThreadsMixin(BaseMixin):
    TYPE = 'threads'
    Process = multiprocessing.dummy.Process
    connection = multiprocessing.dummy.connection
    current_process = staticmethod(multiprocessing.dummy.current_process)
    active_children = staticmethod(multiprocessing.dummy.active_children)
    Pool = staticmethod(multiprocessing.dummy.Pool)
    Pipe = staticmethod(multiprocessing.dummy.Pipe)
    Queue = staticmethod(multiprocessing.dummy.Queue)
    JoinableQueue = staticmethod(multiprocessing.dummy.JoinableQueue)
    Lock = staticmethod(multiprocessing.dummy.Lock)
    RLock = staticmethod(multiprocessing.dummy.RLock)
    Semaphore = staticmethod(multiprocessing.dummy.Semaphore)
    BoundedSemaphore = staticmethod(multiprocessing.dummy.BoundedSemaphore)
    Condition = staticmethod(multiprocessing.dummy.Condition)
    Event = staticmethod(multiprocessing.dummy.Event)
    Barrier = staticmethod(multiprocessing.dummy.Barrier)
    Value = staticmethod(multiprocessing.dummy.Value)
    Array = staticmethod(multiprocessing.dummy.Array)

#
# Functions used to create test cases kutoka the base ones kwenye this module
#

eleza install_tests_in_module_dict(remote_globs, start_method):
    __module__ = remote_globs['__name__']
    local_globs = globals()
    ALL_TYPES = {'processes', 'threads', 'manager'}

    kila name, base kwenye local_globs.items():
        ikiwa sio isinstance(base, type):
            endelea
        ikiwa issubclass(base, BaseTestCase):
            ikiwa base ni BaseTestCase:
                endelea
            assert set(base.ALLOWED_TYPES) <= ALL_TYPES, base.ALLOWED_TYPES
            kila type_ kwenye base.ALLOWED_TYPES:
                newname = 'With' + type_.capitalize() + name[1:]
                Mixin = local_globs[type_.capitalize() + 'Mixin']
                kundi Temp(base, Mixin, unittest.TestCase):
                    pass
                Temp.__name__ = Temp.__qualname__ = newname
                Temp.__module__ = __module__
                remote_globs[newname] = Temp
        elikiwa issubclass(base, unittest.TestCase):
            kundi Temp(base, object):
                pass
            Temp.__name__ = Temp.__qualname__ = name
            Temp.__module__ = __module__
            remote_globs[name] = Temp

    dangling = [Tupu, Tupu]
    old_start_method = [Tupu]

    eleza setUpModule():
        multiprocessing.set_forkserver_preload(PRELOAD)
        multiprocessing.process._cleanup()
        dangling[0] = multiprocessing.process._dangling.copy()
        dangling[1] = threading._dangling.copy()
        old_start_method[0] = multiprocessing.get_start_method(allow_none=Kweli)
        jaribu:
            multiprocessing.set_start_method(start_method, force=Kweli)
        except ValueError:
             ashiria unittest.SkipTest(start_method +
                                    ' start method sio supported')

        ikiwa sys.platform.startswith("linux"):
            jaribu:
                lock = multiprocessing.RLock()
            except OSError:
                 ashiria unittest.SkipTest("OSError raises on RLock creation, "
                                        "see issue 3111!")
        check_enough_semaphores()
        util.get_temp_dir()     # creates temp directory
        multiprocessing.get_logger().setLevel(LOG_LEVEL)

    eleza tearDownModule():
        need_sleep = Uongo

        # bpo-26762: Some multiprocessing objects like Pool create reference
        # cycles. Trigger a garbage collection to koma these cycles.
        test.support.gc_collect()

        multiprocessing.set_start_method(old_start_method[0], force=Kweli)
        # pause a bit so we don't get warning about dangling threads/processes
        processes = set(multiprocessing.process._dangling) - set(dangling[0])
        ikiwa processes:
            need_sleep = Kweli
            test.support.environment_altered = Kweli
            andika('Warning -- Dangling processes: %s' % processes,
                  file=sys.stderr)
        processes = Tupu

        threads = set(threading._dangling) - set(dangling[1])
        ikiwa threads:
            need_sleep = Kweli
            test.support.environment_altered = Kweli
            andika('Warning -- Dangling threads: %s' % threads,
                  file=sys.stderr)
        threads = Tupu

        # Sleep 500 ms to give time to child processes to complete.
        ikiwa need_sleep:
            time.sleep(0.5)

        multiprocessing.process._cleanup()

        # Stop the ForkServer process ikiwa it's running
        kutoka multiprocessing agiza forkserver
        forkserver._forkserver._stop()

        # bpo-37421: Explicitly call _run_finalizers() to remove immediately
        # temporary directories created by multiprocessing.util.get_temp_dir().
        multiprocessing.util._run_finalizers()
        test.support.gc_collect()

    remote_globs['setUpModule'] = setUpModule
    remote_globs['tearDownModule'] = tearDownModule
