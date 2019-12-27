# This is a variant of the very old (early 90's) file
# Demo/threads/bug.py.  It simply provokes a number of threads into
# trying to agiza the same module "at the same time".
# There are no pleasant failure modes -- most likely is that Python
# complains several times about module random having no attribute
# randrange, and then Python hangs.

agiza _imp as imp
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

def task(N, done, done_tasks, errors):
    try:
        # We don't use modulefinder but still agiza it in order to stress
        # agizaing of different modules kutoka several threads.
        if len(done_tasks) % 2:
            agiza modulefinder
            agiza random
        else:
            agiza random
            agiza modulefinder
        # This will fail if random is not completely initialized
        x = random.randrange(1, 3)
    except Exception as e:
        errors.append(e.with_traceback(None))
    finally:
        done_tasks.append(threading.get_ident())
        finished = len(done_tasks) == N
        if finished:
            done.set()

def mock_register_at_fork(func):
    # bpo-30599: Mock os.register_at_fork() when agizaing the random module,
    # since this function doesn't allow to unregister callbacks and would leak
    # memory.
    return mock.patch('os.register_at_fork', create=True)(func)

# Create a circular agiza structure: A -> C -> B -> D -> A
# NOTE: `time` is already loaded and therefore doesn't threaten to deadlock.

circular_agizas_modules = {
    'A': """if 1:
        agiza time
        time.sleep(%(delay)s)
        x = 'a'
        agiza C
        """,
    'B': """if 1:
        agiza time
        time.sleep(%(delay)s)
        x = 'b'
        agiza D
        """,
    'C': """agiza B""",
    'D': """agiza A""",
}

class Finder:
    """A dummy finder to detect concurrent access to its find_spec()
    method."""

    def __init__(self):
        self.numcalls = 0
        self.x = 0
        self.lock = threading.Lock()

    def find_spec(self, name, path=None, target=None):
        # Simulate some thread-unsafe behaviour. If calls to find_spec()
        # are properly serialized, `x` will end up the same as `numcalls`.
        # Otherwise not.
        assert imp.lock_held()
        with self.lock:
            self.numcalls += 1
        x = self.x
        time.sleep(0.01)
        self.x = x + 1

class FlushingFinder:
    """A dummy finder which flushes sys.path_importer_cache when it gets
    called."""

    def find_spec(self, name, path=None, target=None):
        sys.path_importer_cache.clear()


class ThreadedImportTests(unittest.TestCase):

    def setUp(self):
        self.old_random = sys.modules.pop('random', None)

    def tearDown(self):
        # If the `random` module was already initialized, we restore the
        # old module at the end so that pickling tests don't fail.
        # See http://bugs.python.org/issue3657#msg110461
        if self.old_random is not None:
            sys.modules['random'] = self.old_random

    @mock_register_at_fork
    def check_parallel_module_init(self, mock_os):
        if imp.lock_held():
            # This triggers on, e.g., kutoka test agiza autotest.
            raise unittest.SkipTest("can't run when agiza lock is held")

        done = threading.Event()
        for N in (20, 50) * 3:
            if verbose:
                print("Trying", N, "threads ...", end=' ')
            # Make sure that random and modulefinder get reimported freshly
            for modname in ['random', 'modulefinder']:
                try:
                    del sys.modules[modname]
                except KeyError:
                    pass
            errors = []
            done_tasks = []
            done.clear()
            t0 = time.monotonic()
            with start_threads(threading.Thread(target=task,
                                                args=(N, done, done_tasks, errors,))
                               for i in range(N)):
                pass
            completed = done.wait(10 * 60)
            dt = time.monotonic() - t0
            if verbose:
                print("%.1f ms" % (dt*1e3), flush=True, end=" ")
            dbg_info = 'done: %s/%s' % (len(done_tasks), N)
            self.assertFalse(errors, dbg_info)
            self.assertTrue(completed, dbg_info)
            if verbose:
                print("OK.")

    def test_parallel_module_init(self):
        self.check_parallel_module_init()

    def test_parallel_meta_path(self):
        finder = Finder()
        sys.meta_path.insert(0, finder)
        try:
            self.check_parallel_module_init()
            self.assertGreater(finder.numcalls, 0)
            self.assertEqual(finder.x, finder.numcalls)
        finally:
            sys.meta_path.remove(finder)

    def test_parallel_path_hooks(self):
        # Here the Finder instance is only used to check concurrent calls
        # to path_hook().
        finder = Finder()
        # In order for our path hook to be called at each agiza, we need
        # to flush the path_importer_cache, which we do by registering a
        # dedicated meta_path entry.
        flushing_finder = FlushingFinder()
        def path_hook(path):
            finder.find_spec('')
            raise ImportError
        sys.path_hooks.insert(0, path_hook)
        sys.meta_path.append(flushing_finder)
        try:
            # Flush the cache a first time
            flushing_finder.find_spec('')
            numtests = self.check_parallel_module_init()
            self.assertGreater(finder.numcalls, 0)
            self.assertEqual(finder.x, finder.numcalls)
        finally:
            sys.meta_path.remove(flushing_finder)
            sys.path_hooks.remove(path_hook)

    def test_import_hangers(self):
        # In case this test is run again, make sure the helper module
        # gets loaded kutoka scratch again.
        try:
            del sys.modules['test.threaded_import_hangers']
        except KeyError:
            pass
        agiza test.threaded_import_hangers
        self.assertFalse(test.threaded_import_hangers.errors)

    def test_circular_agizas(self):
        # The goal of this test is to exercise implementations of the agiza
        # lock which use a per-module lock, rather than a global lock.
        # In these implementations, there is a possible deadlock with
        # circular agizas, for example:
        # - thread 1 agizas A (grabbing the lock for A) which agizas B
        # - thread 2 agizas B (grabbing the lock for B) which agizas A
        # Such implementations should be able to detect such situations and
        # resolve them one way or the other, without freezing.
        # NOTE: our test constructs a slightly less trivial agiza cycle,
        # in order to better stress the deadlock avoidance mechanism.
        delay = 0.5
        os.mkdir(TESTFN)
        self.addCleanup(shutil.rmtree, TESTFN)
        sys.path.insert(0, TESTFN)
        self.addCleanup(sys.path.remove, TESTFN)
        for name, contents in circular_agizas_modules.items():
            contents = contents % {'delay': delay}
            with open(os.path.join(TESTFN, name + ".py"), "wb") as f:
                f.write(contents.encode('utf-8'))
            self.addCleanup(forget, name)

        importlib.invalidate_caches()
        results = []
        def import_ab():
            agiza A
            results.append(getattr(A, 'x', None))
        def import_ba():
            agiza B
            results.append(getattr(B, 'x', None))
        t1 = threading.Thread(target=import_ab)
        t2 = threading.Thread(target=import_ba)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertEqual(set(results), {'a', 'b'})

    @mock_register_at_fork
    def test_side_effect_agiza(self, mock_os):
        code = """if 1:
            agiza threading
            def target():
                agiza random
            t = threading.Thread(target=target)
            t.start()
            t.join()
            t = None"""
        sys.path.insert(0, os.curdir)
        self.addCleanup(sys.path.remove, os.curdir)
        filename = TESTFN + ".py"
        with open(filename, "wb") as f:
            f.write(code.encode('utf-8'))
        self.addCleanup(unlink, filename)
        self.addCleanup(forget, TESTFN)
        self.addCleanup(rmtree, '__pycache__')
        importlib.invalidate_caches()
        __import__(TESTFN)
        del sys.modules[TESTFN]


@reap_threads
def test_main():
    old_switchinterval = None
    try:
        old_switchinterval = sys.getswitchinterval()
        sys.setswitchinterval(1e-5)
    except AttributeError:
        pass
    try:
        run_unittest(ThreadedImportTests)
    finally:
        if old_switchinterval is not None:
            sys.setswitchinterval(old_switchinterval)

if __name__ == "__main__":
    test_main()
