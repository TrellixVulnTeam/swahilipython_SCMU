agiza os
agiza unittest
agiza random
kutoka test agiza support
agiza _thread as thread
agiza time
agiza weakref

kutoka test agiza lock_tests

NUMTASKS = 10
NUMTRIPS = 3
POLL_SLEEP = 0.010 # seconds = 10 ms

_print_mutex = thread.allocate_lock()

eleza verbose_andika(arg):
    """Helper function for printing out debugging output."""
    ikiwa support.verbose:
        with _print_mutex:
            andika(arg)


kundi BasicThreadTest(unittest.TestCase):

    eleza setUp(self):
        self.done_mutex = thread.allocate_lock()
        self.done_mutex.acquire()
        self.running_mutex = thread.allocate_lock()
        self.random_mutex = thread.allocate_lock()
        self.created = 0
        self.running = 0
        self.next_ident = 0

        key = support.threading_setup()
        self.addCleanup(support.threading_cleanup, *key)


kundi ThreadRunningTests(BasicThreadTest):

    eleza newtask(self):
        with self.running_mutex:
            self.next_ident += 1
            verbose_andika("creating task %s" % self.next_ident)
            thread.start_new_thread(self.task, (self.next_ident,))
            self.created += 1
            self.running += 1

    eleza task(self, ident):
        with self.random_mutex:
            delay = random.random() / 10000.0
        verbose_andika("task %s will run for %sus" % (ident, round(delay*1e6)))
        time.sleep(delay)
        verbose_andika("task %s done" % ident)
        with self.running_mutex:
            self.running -= 1
            ikiwa self.created == NUMTASKS and self.running == 0:
                self.done_mutex.release()

    eleza test_starting_threads(self):
        with support.wait_threads_exit():
            # Basic test for thread creation.
            for i in range(NUMTASKS):
                self.newtask()
            verbose_andika("waiting for tasks to complete...")
            self.done_mutex.acquire()
            verbose_andika("all tasks done")

    eleza test_stack_size(self):
        # Various stack size tests.
        self.assertEqual(thread.stack_size(), 0, "initial stack size is not 0")

        thread.stack_size(0)
        self.assertEqual(thread.stack_size(), 0, "stack_size not reset to default")

    @unittest.skipIf(os.name not in ("nt", "posix"), 'test meant for nt and posix')
    eleza test_nt_and_posix_stack_size(self):
        try:
            thread.stack_size(4096)
        except ValueError:
            verbose_andika("caught expected ValueError setting "
                            "stack_size(4096)")
        except thread.error:
            self.skipTest("platform does not support changing thread stack "
                          "size")

        fail_msg = "stack_size(%d) failed - should succeed"
        for tss in (262144, 0x100000, 0):
            thread.stack_size(tss)
            self.assertEqual(thread.stack_size(), tss, fail_msg % tss)
            verbose_andika("successfully set stack_size(%d)" % tss)

        for tss in (262144, 0x100000):
            verbose_andika("trying stack_size = (%d)" % tss)
            self.next_ident = 0
            self.created = 0
            with support.wait_threads_exit():
                for i in range(NUMTASKS):
                    self.newtask()

                verbose_andika("waiting for all tasks to complete")
                self.done_mutex.acquire()
                verbose_andika("all tasks done")

        thread.stack_size(0)

    eleza test__count(self):
        # Test the _count() function.
        orig = thread._count()
        mut = thread.allocate_lock()
        mut.acquire()
        started = []

        eleza task():
            started.append(None)
            mut.acquire()
            mut.release()

        with support.wait_threads_exit():
            thread.start_new_thread(task, ())
            while not started:
                time.sleep(POLL_SLEEP)
            self.assertEqual(thread._count(), orig + 1)
            # Allow the task to finish.
            mut.release()
            # The only reliable way to be sure that the thread ended kutoka the
            # interpreter's point of view is to wait for the function object to be
            # destroyed.
            done = []
            wr = weakref.ref(task, lambda _: done.append(None))
            del task
            while not done:
                time.sleep(POLL_SLEEP)
            self.assertEqual(thread._count(), orig)

    eleza test_unraisable_exception(self):
        eleza task():
            started.release()
            raise ValueError("task failed")

        started = thread.allocate_lock()
        with support.catch_unraisable_exception() as cm:
            with support.wait_threads_exit():
                started.acquire()
                thread.start_new_thread(task, ())
                started.acquire()

            self.assertEqual(str(cm.unraisable.exc_value), "task failed")
            self.assertIs(cm.unraisable.object, task)
            self.assertEqual(cm.unraisable.err_msg,
                             "Exception ignored in thread started by")
            self.assertIsNotNone(cm.unraisable.exc_traceback)


kundi Barrier:
    eleza __init__(self, num_threads):
        self.num_threads = num_threads
        self.waiting = 0
        self.checkin_mutex  = thread.allocate_lock()
        self.checkout_mutex = thread.allocate_lock()
        self.checkout_mutex.acquire()

    eleza enter(self):
        self.checkin_mutex.acquire()
        self.waiting = self.waiting + 1
        ikiwa self.waiting == self.num_threads:
            self.waiting = self.num_threads - 1
            self.checkout_mutex.release()
            return
        self.checkin_mutex.release()

        self.checkout_mutex.acquire()
        self.waiting = self.waiting - 1
        ikiwa self.waiting == 0:
            self.checkin_mutex.release()
            return
        self.checkout_mutex.release()


kundi BarrierTest(BasicThreadTest):

    eleza test_barrier(self):
        with support.wait_threads_exit():
            self.bar = Barrier(NUMTASKS)
            self.running = NUMTASKS
            for i in range(NUMTASKS):
                thread.start_new_thread(self.task2, (i,))
            verbose_andika("waiting for tasks to end")
            self.done_mutex.acquire()
            verbose_andika("tasks done")

    eleza task2(self, ident):
        for i in range(NUMTRIPS):
            ikiwa ident == 0:
                # give it a good chance to enter the next
                # barrier before the others are all out
                # of the current one
                delay = 0
            else:
                with self.random_mutex:
                    delay = random.random() / 10000.0
            verbose_andika("task %s will run for %sus" %
                          (ident, round(delay * 1e6)))
            time.sleep(delay)
            verbose_andika("task %s entering %s" % (ident, i))
            self.bar.enter()
            verbose_andika("task %s leaving barrier" % ident)
        with self.running_mutex:
            self.running -= 1
            # Must release mutex before releasing done, else the main thread can
            # exit and set mutex to None as part of global teardown; then
            # mutex.release() raises AttributeError.
            finished = self.running == 0
        ikiwa finished:
            self.done_mutex.release()

kundi LockTests(lock_tests.LockTests):
    locktype = thread.allocate_lock


kundi TestForkInThread(unittest.TestCase):
    eleza setUp(self):
        self.read_fd, self.write_fd = os.pipe()

    @unittest.skipUnless(hasattr(os, 'fork'), 'need os.fork')
    @support.reap_threads
    eleza test_forkinthread(self):
        status = "not set"

        eleza thread1():
            nonlocal status

            # fork in a thread
            pid = os.fork()
            ikiwa pid == 0:
                # child
                try:
                    os.close(self.read_fd)
                    os.write(self.write_fd, b"OK")
                finally:
                    os._exit(0)
            else:
                # parent
                os.close(self.write_fd)
                pid, status = os.waitpid(pid, 0)

        with support.wait_threads_exit():
            thread.start_new_thread(thread1, ())
            self.assertEqual(os.read(self.read_fd, 2), b"OK",
                             "Unable to fork() in thread")
        self.assertEqual(status, 0)

    eleza tearDown(self):
        try:
            os.close(self.read_fd)
        except OSError:
            pass

        try:
            os.close(self.write_fd)
        except OSError:
            pass


ikiwa __name__ == "__main__":
    unittest.main()
