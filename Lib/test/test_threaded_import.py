# This ni a variant of the very old (early 90's) file
# Demo/threads/bug.py.  It simply provokes a number of threads into
# trying to agiza the same module "at the same time".
# There are no pleasant failure modes -- most likely ni that Python
# complains several times about module random having no attribute
# randrange, na then Python hangs.

agiza _imp kama imp
agiza os
agiza importlib
agiza sys
agiza time
agiza shutil
agiza threading
agiza unittest
kutoka unittest agiza mock
kutoka test.support agiza (
    verbose, run_unittest, TESTFN, reap_threads,
    forget, unlink, rmtree, start_threads)

eleza task(N, done, done_tasks, errors):
    jaribu:
        # We don't use modulefinder but still agiza it kwenye order to stress
        # agizaing of different modules kutoka several threads.
        ikiwa len(done_tasks) % 2:
            agiza modulefinder
            agiza random
        isipokua:
            agiza random
            agiza modulefinder
        # This will fail ikiwa random ni sio completely initialized
        x = random.randrange(1, 3)
    tatizo Exception kama e:
        errors.append(e.with_traceback(Tupu))
    mwishowe:
        done_tasks.append(threading.get_ident())
        finished = len(done_tasks) == N
        ikiwa finished:
            done.set()

eleza mock_register_at_fork(func):
    # bpo-30599: Mock os.register_at_fork() when agizaing the random module,
    # since this function doesn't allow to unregister callbacks na would leak
    # memory.
    rudisha mock.patch('os.register_at_fork', create=Kweli)(func)

# Create a circular agiza structure: A -> C -> B -> D -> A
# NOTE: `time` ni already loaded na therefore doesn't threaten to deadlock.

circular_agizas_modules = {
    'A': """ikiwa 1:
        agiza time
        time.sleep(%(delay)s)
        x = 'a'
        agiza C
        """,
    'B': """ikiwa 1:
        agiza time
        time.sleep(%(delay)s)
        x = 'b'
        agiza D
        """,
    'C': """agiza B""",
    'D': """agiza A""",
}

kundi Finder:
    """A dummy finder to detect concurrent access to its find_spec()
    method."""

    eleza __init__(self):
        self.numcalls = 0
        self.x = 0
        self.lock = threading.Lock()

    eleza find_spec(self, name, path=Tupu, target=Tupu):
        # Simulate some thread-unsafe behaviour. If calls to find_spec()
        # are properly serialized, `x` will end up the same kama `numcalls`.
        # Otherwise not.
        assert imp.lock_held()
        ukijumuisha self.lock:
            self.numcalls += 1
        x = self.x
        time.sleep(0.01)
        self.x = x + 1

kundi FlushingFinder:
    """A dummy finder which flushes sys.path_importer_cache when it gets
    called."""

    eleza find_spec(self, name, path=Tupu, target=Tupu):
        sys.path_importer_cache.clear()


kundi ThreadedImportTests(unittest.TestCase):

    eleza setUp(self):
        self.old_random = sys.modules.pop('random', Tupu)

    eleza tearDown(self):
        # If the `random` module was already initialized, we restore the
        # old module at the end so that pickling tests don't fail.
        # See http://bugs.python.org/issue3657#msg110461
        ikiwa self.old_random ni sio Tupu:
            sys.modules['random'] = self.old_random

    @mock_register_at_fork
    eleza check_parallel_module_init(self, mock_os):
        ikiwa imp.lock_held():
            # This triggers on, e.g., kutoka test agiza autotest.
            ashiria unittest.SkipTest("can't run when agiza lock ni held")

        done = threading.Event()
        kila N kwenye (20, 50) * 3:
            ikiwa verbose:
                andika("Trying", N, "threads ...", end=' ')
            # Make sure that random na modulefinder get reimported freshly
            kila modname kwenye ['random', 'modulefinder']:
                jaribu:
                    toa sys.modules[modname]
                tatizo KeyError:
                    pita
            errors = []
            done_tasks = []
            done.clear()
            t0 = time.monotonic()
            ukijumuisha start_threads(threading.Thread(target=task,
                                                args=(N, done, done_tasks, errors,))
                               kila i kwenye range(N)):
                pita
            completed = done.wait(10 * 60)
            dt = time.monotonic() - t0
            ikiwa verbose:
                andika("%.1f ms" % (dt*1e3), flush=Kweli, end=" ")
            dbg_info = 'done: %s/%s' % (len(done_tasks), N)
            self.assertUongo(errors, dbg_info)
            self.assertKweli(completed, dbg_info)
            ikiwa verbose:
                andika("OK.")

    eleza test_parallel_module_init(self):
        self.check_parallel_module_init()

    eleza test_parallel_meta_path(self):
        finder = Finder()
        sys.meta_path.insert(0, finder)
        jaribu:
            self.check_parallel_module_init()
            self.assertGreater(finder.numcalls, 0)
            self.assertEqual(finder.x, finder.numcalls)
        mwishowe:
            sys.meta_path.remove(finder)

    eleza test_parallel_path_hooks(self):
        # Here the Finder instance ni only used to check concurrent calls
        # to path_hook().
        finder = Finder()
        # In order kila our path hook to be called at each agiza, we need
        # to flush the path_importer_cache, which we do by registering a
        # dedicated meta_path entry.
        flushing_finder = FlushingFinder()
        eleza path_hook(path):
            finder.find_spec('')
            ashiria ImportError
        sys.path_hooks.insert(0, path_hook)
        sys.meta_path.append(flushing_finder)
        jaribu:
            # Flush the cache a first time
            flushing_finder.find_spec('')
            numtests = self.check_parallel_module_init()
            self.assertGreater(finder.numcalls, 0)
            self.assertEqual(finder.x, finder.numcalls)
        mwishowe:
            sys.meta_path.remove(flushing_finder)
            sys.path_hooks.remove(path_hook)

    eleza test_import_hangers(self):
        # In case this test ni run again, make sure the helper module
        # gets loaded kutoka scratch again.
        jaribu:
            toa sys.modules['test.threaded_import_hangers']
        tatizo KeyError:
            pita
        agiza test.threaded_import_hangers
        self.assertUongo(test.threaded_import_hangers.errors)

    eleza test_circular_agizas(self):
        # The goal of this test ni to exercise implementations of the agiza
        # lock which use a per-module lock, rather than a global lock.
        # In these implementations, there ni a possible deadlock with
        # circular agizas, kila example:
        # - thread 1 agizas A (grabbing the lock kila A) which agizas B
        # - thread 2 agizas B (grabbing the lock kila B) which agizas A
        # Such implementations should be able to detect such situations na
        # resolve them one way ama the other, without freezing.
        # NOTE: our test constructs a slightly less trivial agiza cycle,
        # kwenye order to better stress the deadlock avoidance mechanism.
        delay = 0.5
        os.mkdir(TESTFN)
        self.addCleanup(shutil.rmtree, TESTFN)
        sys.path.insert(0, TESTFN)
        self.addCleanup(sys.path.remove, TESTFN)
        kila name, contents kwenye circular_agizas_modules.items():
            contents = contents % {'delay': delay}
            ukijumuisha open(os.path.join(TESTFN, name + ".py"), "wb") kama f:
                f.write(contents.encode('utf-8'))
            self.addCleanup(forget, name)

        importlib.invalidate_caches()
        results = []
        eleza import_ab():
            agiza A
            results.append(getattr(A, 'x', Tupu))
        eleza import_ba():
            agiza B
            results.append(getattr(B, 'x', Tupu))
        t1 = threading.Thread(target=import_ab)
        t2 = threading.Thread(target=import_ba)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertEqual(set(results), {'a', 'b'})

    @mock_register_at_fork
    eleza test_side_effect_agiza(self, mock_os):
        code = """ikiwa 1:
            agiza threading
            eleza target():
                agiza random
            t = threading.Thread(target=target)
            t.start()
            t.join()
            t = Tupu"""
        sys.path.insert(0, os.curdir)
        self.addCleanup(sys.path.remove, os.curdir)
        filename = TESTFN + ".py"
        ukijumuisha open(filename, "wb") kama f:
            f.write(code.encode('utf-8'))
        self.addCleanup(unlink, filename)
        self.addCleanup(forget, TESTFN)
        self.addCleanup(rmtree, '__pycache__')
        importlib.invalidate_caches()
        __import__(TESTFN)
        toa sys.modules[TESTFN]


@reap_threads
eleza test_main():
    old_switchinterval = Tupu
    jaribu:
        old_switchinterval = sys.getswitchinterval()
        sys.setswitchinterval(1e-5)
    tatizo AttributeError:
        pita
    jaribu:
        run_unittest(ThreadedImportTests)
    mwishowe:
        ikiwa old_switchinterval ni sio Tupu:
            sys.setswitchinterval(old_switchinterval)

ikiwa __name__ == "__main__":
    test_main()
