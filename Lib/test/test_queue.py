# Some simple queue module tests, plus some failure conditions
# to ensure the Queue locks remain stable.
agiza itertools
agiza random
agiza threading
agiza time
agiza unittest
agiza weakref
kutoka test agiza support

py_queue = support.import_fresh_module('queue', blocked=['_queue'])
c_queue = support.import_fresh_module('queue', fresh=['_queue'])
need_c_queue = unittest.skipUnless(c_queue, "No _queue module found")

QUEUE_SIZE = 5

eleza qfull(q):
    rudisha q.maxsize > 0 and q.qsize() == q.maxsize

# A thread to run a function that unclogs a blocked Queue.
kundi _TriggerThread(threading.Thread):
    eleza __init__(self, fn, args):
        self.fn = fn
        self.args = args
        self.startedEvent = threading.Event()
        threading.Thread.__init__(self)

    eleza run(self):
        # The sleep isn't necessary, but is intended to give the blocking
        # function in the main thread a chance at actually blocking before
        # we unclog it.  But ikiwa the sleep is longer than the timeout-based
        # tests wait in their blocking functions, those tests will fail.
        # So we give them much longer timeout values compared to the
        # sleep here (I aimed at 10 seconds for blocking functions --
        # they should never actually wait that long - they should make
        # progress as soon as we call self.fn()).
        time.sleep(0.1)
        self.startedEvent.set()
        self.fn(*self.args)


# Execute a function that blocks, and in a separate thread, a function that
# triggers the release.  Returns the result of the blocking function.  Caution:
# block_func must guarantee to block until trigger_func is called, and
# trigger_func must guarantee to change queue state so that block_func can make
# enough progress to return.  In particular, a block_func that just raises an
# exception regardless of whether trigger_func is called will lead to
# timing-dependent sporadic failures, and one of those went rarely seen but
# undiagnosed for years.  Now block_func must be unexceptional.  If block_func
# is supposed to raise an exception, call do_exceptional_blocking_test()
# instead.

kundi BlockingTestMixin:

    eleza do_blocking_test(self, block_func, block_args, trigger_func, trigger_args):
        thread = _TriggerThread(trigger_func, trigger_args)
        thread.start()
        try:
            self.result = block_func(*block_args)
            # If block_func returned before our thread made the call, we failed!
            ikiwa not thread.startedEvent.is_set():
                self.fail("blocking function %r appeared not to block" %
                          block_func)
            rudisha self.result
        finally:
            support.join_thread(thread, 10) # make sure the thread terminates

    # Call this instead ikiwa block_func is supposed to raise an exception.
    eleza do_exceptional_blocking_test(self,block_func, block_args, trigger_func,
                                   trigger_args, expected_exception_class):
        thread = _TriggerThread(trigger_func, trigger_args)
        thread.start()
        try:
            try:
                block_func(*block_args)
            except expected_exception_class:
                raise
            else:
                self.fail("expected exception of kind %r" %
                                 expected_exception_class)
        finally:
            support.join_thread(thread, 10) # make sure the thread terminates
            ikiwa not thread.startedEvent.is_set():
                self.fail("trigger thread ended but event never set")


kundi BaseQueueTestMixin(BlockingTestMixin):
    eleza setUp(self):
        self.cum = 0
        self.cumlock = threading.Lock()

    eleza basic_queue_test(self, q):
        ikiwa q.qsize():
            raise RuntimeError("Call this function with an empty queue")
        self.assertTrue(q.empty())
        self.assertFalse(q.full())
        # I guess we better check things actually queue correctly a little :)
        q.put(111)
        q.put(333)
        q.put(222)
        target_order = dict(Queue = [111, 333, 222],
                            LifoQueue = [222, 333, 111],
                            PriorityQueue = [111, 222, 333])
        actual_order = [q.get(), q.get(), q.get()]
        self.assertEqual(actual_order, target_order[q.__class__.__name__],
                         "Didn't seem to queue the correct data!")
        for i in range(QUEUE_SIZE-1):
            q.put(i)
            self.assertTrue(q.qsize(), "Queue should not be empty")
        self.assertTrue(not qfull(q), "Queue should not be full")
        last = 2 * QUEUE_SIZE
        full = 3 * 2 * QUEUE_SIZE
        q.put(last)
        self.assertTrue(qfull(q), "Queue should be full")
        self.assertFalse(q.empty())
        self.assertTrue(q.full())
        try:
            q.put(full, block=0)
            self.fail("Didn't appear to block with a full queue")
        except self.queue.Full:
            pass
        try:
            q.put(full, timeout=0.01)
            self.fail("Didn't appear to time-out with a full queue")
        except self.queue.Full:
            pass
        # Test a blocking put
        self.do_blocking_test(q.put, (full,), q.get, ())
        self.do_blocking_test(q.put, (full, True, 10), q.get, ())
        # Empty it
        for i in range(QUEUE_SIZE):
            q.get()
        self.assertTrue(not q.qsize(), "Queue should be empty")
        try:
            q.get(block=0)
            self.fail("Didn't appear to block with an empty queue")
        except self.queue.Empty:
            pass
        try:
            q.get(timeout=0.01)
            self.fail("Didn't appear to time-out with an empty queue")
        except self.queue.Empty:
            pass
        # Test a blocking get
        self.do_blocking_test(q.get, (), q.put, ('empty',))
        self.do_blocking_test(q.get, (True, 10), q.put, ('empty',))


    eleza worker(self, q):
        while True:
            x = q.get()
            ikiwa x < 0:
                q.task_done()
                return
            with self.cumlock:
                self.cum += x
            q.task_done()

    eleza queue_join_test(self, q):
        self.cum = 0
        threads = []
        for i in (0,1):
            thread = threading.Thread(target=self.worker, args=(q,))
            thread.start()
            threads.append(thread)
        for i in range(100):
            q.put(i)
        q.join()
        self.assertEqual(self.cum, sum(range(100)),
                         "q.join() did not block until all tasks were done")
        for i in (0,1):
            q.put(-1)         # instruct the threads to close
        q.join()                # verify that you can join twice
        for thread in threads:
            thread.join()

    eleza test_queue_task_done(self):
        # Test to make sure a queue task completed successfully.
        q = self.type2test()
        try:
            q.task_done()
        except ValueError:
            pass
        else:
            self.fail("Did not detect task count going negative")

    eleza test_queue_join(self):
        # Test that a queue join()s successfully, and before anything else
        # (done twice for insurance).
        q = self.type2test()
        self.queue_join_test(q)
        self.queue_join_test(q)
        try:
            q.task_done()
        except ValueError:
            pass
        else:
            self.fail("Did not detect task count going negative")

    eleza test_basic(self):
        # Do it a couple of times on the same queue.
        # Done twice to make sure works with same instance reused.
        q = self.type2test(QUEUE_SIZE)
        self.basic_queue_test(q)
        self.basic_queue_test(q)

    eleza test_negative_timeout_raises_exception(self):
        q = self.type2test(QUEUE_SIZE)
        with self.assertRaises(ValueError):
            q.put(1, timeout=-1)
        with self.assertRaises(ValueError):
            q.get(1, timeout=-1)

    eleza test_nowait(self):
        q = self.type2test(QUEUE_SIZE)
        for i in range(QUEUE_SIZE):
            q.put_nowait(1)
        with self.assertRaises(self.queue.Full):
            q.put_nowait(1)

        for i in range(QUEUE_SIZE):
            q.get_nowait()
        with self.assertRaises(self.queue.Empty):
            q.get_nowait()

    eleza test_shrinking_queue(self):
        # issue 10110
        q = self.type2test(3)
        q.put(1)
        q.put(2)
        q.put(3)
        with self.assertRaises(self.queue.Full):
            q.put_nowait(4)
        self.assertEqual(q.qsize(), 3)
        q.maxsize = 2                       # shrink the queue
        with self.assertRaises(self.queue.Full):
            q.put_nowait(4)

kundi QueueTest(BaseQueueTestMixin):

    eleza setUp(self):
        self.type2test = self.queue.Queue
        super().setUp()

kundi PyQueueTest(QueueTest, unittest.TestCase):
    queue = py_queue


@need_c_queue
kundi CQueueTest(QueueTest, unittest.TestCase):
    queue = c_queue


kundi LifoQueueTest(BaseQueueTestMixin):

    eleza setUp(self):
        self.type2test = self.queue.LifoQueue
        super().setUp()


kundi PyLifoQueueTest(LifoQueueTest, unittest.TestCase):
    queue = py_queue


@need_c_queue
kundi CLifoQueueTest(LifoQueueTest, unittest.TestCase):
    queue = c_queue


kundi PriorityQueueTest(BaseQueueTestMixin):

    eleza setUp(self):
        self.type2test = self.queue.PriorityQueue
        super().setUp()


kundi PyPriorityQueueTest(PriorityQueueTest, unittest.TestCase):
    queue = py_queue


@need_c_queue
kundi CPriorityQueueTest(PriorityQueueTest, unittest.TestCase):
    queue = c_queue


# A Queue subkundi that can provoke failure at a moment's notice :)
kundi FailingQueueException(Exception): pass

kundi FailingQueueTest(BlockingTestMixin):

    eleza setUp(self):

        Queue = self.queue.Queue

        kundi FailingQueue(Queue):
            eleza __init__(self, *args):
                self.fail_next_put = False
                self.fail_next_get = False
                Queue.__init__(self, *args)
            eleza _put(self, item):
                ikiwa self.fail_next_put:
                    self.fail_next_put = False
                    raise FailingQueueException("You Lose")
                rudisha Queue._put(self, item)
            eleza _get(self):
                ikiwa self.fail_next_get:
                    self.fail_next_get = False
                    raise FailingQueueException("You Lose")
                rudisha Queue._get(self)

        self.FailingQueue = FailingQueue

        super().setUp()

    eleza failing_queue_test(self, q):
        ikiwa q.qsize():
            raise RuntimeError("Call this function with an empty queue")
        for i in range(QUEUE_SIZE-1):
            q.put(i)
        # Test a failing non-blocking put.
        q.fail_next_put = True
        try:
            q.put("oops", block=0)
            self.fail("The queue didn't fail when it should have")
        except FailingQueueException:
            pass
        q.fail_next_put = True
        try:
            q.put("oops", timeout=0.1)
            self.fail("The queue didn't fail when it should have")
        except FailingQueueException:
            pass
        q.put("last")
        self.assertTrue(qfull(q), "Queue should be full")
        # Test a failing blocking put
        q.fail_next_put = True
        try:
            self.do_blocking_test(q.put, ("full",), q.get, ())
            self.fail("The queue didn't fail when it should have")
        except FailingQueueException:
            pass
        # Check the Queue isn't damaged.
        # put failed, but get succeeded - re-add
        q.put("last")
        # Test a failing timeout put
        q.fail_next_put = True
        try:
            self.do_exceptional_blocking_test(q.put, ("full", True, 10), q.get, (),
                                              FailingQueueException)
            self.fail("The queue didn't fail when it should have")
        except FailingQueueException:
            pass
        # Check the Queue isn't damaged.
        # put failed, but get succeeded - re-add
        q.put("last")
        self.assertTrue(qfull(q), "Queue should be full")
        q.get()
        self.assertTrue(not qfull(q), "Queue should not be full")
        q.put("last")
        self.assertTrue(qfull(q), "Queue should be full")
        # Test a blocking put
        self.do_blocking_test(q.put, ("full",), q.get, ())
        # Empty it
        for i in range(QUEUE_SIZE):
            q.get()
        self.assertTrue(not q.qsize(), "Queue should be empty")
        q.put("first")
        q.fail_next_get = True
        try:
            q.get()
            self.fail("The queue didn't fail when it should have")
        except FailingQueueException:
            pass
        self.assertTrue(q.qsize(), "Queue should not be empty")
        q.fail_next_get = True
        try:
            q.get(timeout=0.1)
            self.fail("The queue didn't fail when it should have")
        except FailingQueueException:
            pass
        self.assertTrue(q.qsize(), "Queue should not be empty")
        q.get()
        self.assertTrue(not q.qsize(), "Queue should be empty")
        q.fail_next_get = True
        try:
            self.do_exceptional_blocking_test(q.get, (), q.put, ('empty',),
                                              FailingQueueException)
            self.fail("The queue didn't fail when it should have")
        except FailingQueueException:
            pass
        # put succeeded, but get failed.
        self.assertTrue(q.qsize(), "Queue should not be empty")
        q.get()
        self.assertTrue(not q.qsize(), "Queue should be empty")

    eleza test_failing_queue(self):

        # Test to make sure a queue is functioning correctly.
        # Done twice to the same instance.
        q = self.FailingQueue(QUEUE_SIZE)
        self.failing_queue_test(q)
        self.failing_queue_test(q)



kundi PyFailingQueueTest(FailingQueueTest, unittest.TestCase):
    queue = py_queue


@need_c_queue
kundi CFailingQueueTest(FailingQueueTest, unittest.TestCase):
    queue = c_queue


kundi BaseSimpleQueueTest:

    eleza setUp(self):
        self.q = self.type2test()

    eleza feed(self, q, seq, rnd):
        while True:
            try:
                val = seq.pop()
            except IndexError:
                return
            q.put(val)
            ikiwa rnd.random() > 0.5:
                time.sleep(rnd.random() * 1e-3)

    eleza consume(self, q, results, sentinel):
        while True:
            val = q.get()
            ikiwa val == sentinel:
                return
            results.append(val)

    eleza consume_nonblock(self, q, results, sentinel):
        while True:
            while True:
                try:
                    val = q.get(block=False)
                except self.queue.Empty:
                    time.sleep(1e-5)
                else:
                    break
            ikiwa val == sentinel:
                return
            results.append(val)

    eleza consume_timeout(self, q, results, sentinel):
        while True:
            while True:
                try:
                    val = q.get(timeout=1e-5)
                except self.queue.Empty:
                    pass
                else:
                    break
            ikiwa val == sentinel:
                return
            results.append(val)

    eleza run_threads(self, n_feeders, n_consumers, q, inputs,
                    feed_func, consume_func):
        results = []
        sentinel = None
        seq = inputs + [sentinel] * n_consumers
        seq.reverse()
        rnd = random.Random(42)

        exceptions = []
        eleza log_exceptions(f):
            eleza wrapper(*args, **kwargs):
                try:
                    f(*args, **kwargs)
                except BaseException as e:
                    exceptions.append(e)
            rudisha wrapper

        feeders = [threading.Thread(target=log_exceptions(feed_func),
                                    args=(q, seq, rnd))
                   for i in range(n_feeders)]
        consumers = [threading.Thread(target=log_exceptions(consume_func),
                                      args=(q, results, sentinel))
                     for i in range(n_consumers)]

        with support.start_threads(feeders + consumers):
            pass

        self.assertFalse(exceptions)
        self.assertTrue(q.empty())
        self.assertEqual(q.qsize(), 0)

        rudisha results

    eleza test_basic(self):
        # Basic tests for get(), put() etc.
        q = self.q
        self.assertTrue(q.empty())
        self.assertEqual(q.qsize(), 0)
        q.put(1)
        self.assertFalse(q.empty())
        self.assertEqual(q.qsize(), 1)
        q.put(2)
        q.put_nowait(3)
        q.put(4)
        self.assertFalse(q.empty())
        self.assertEqual(q.qsize(), 4)

        self.assertEqual(q.get(), 1)
        self.assertEqual(q.qsize(), 3)

        self.assertEqual(q.get_nowait(), 2)
        self.assertEqual(q.qsize(), 2)

        self.assertEqual(q.get(block=False), 3)
        self.assertFalse(q.empty())
        self.assertEqual(q.qsize(), 1)

        self.assertEqual(q.get(timeout=0.1), 4)
        self.assertTrue(q.empty())
        self.assertEqual(q.qsize(), 0)

        with self.assertRaises(self.queue.Empty):
            q.get(block=False)
        with self.assertRaises(self.queue.Empty):
            q.get(timeout=1e-3)
        with self.assertRaises(self.queue.Empty):
            q.get_nowait()
        self.assertTrue(q.empty())
        self.assertEqual(q.qsize(), 0)

    eleza test_negative_timeout_raises_exception(self):
        q = self.q
        q.put(1)
        with self.assertRaises(ValueError):
            q.get(timeout=-1)

    eleza test_order(self):
        # Test a pair of concurrent put() and get()
        q = self.q
        inputs = list(range(100))
        results = self.run_threads(1, 1, q, inputs, self.feed, self.consume)

        # One producer, one consumer => results appended in well-defined order
        self.assertEqual(results, inputs)

    eleza test_many_threads(self):
        # Test multiple concurrent put() and get()
        N = 50
        q = self.q
        inputs = list(range(10000))
        results = self.run_threads(N, N, q, inputs, self.feed, self.consume)

        # Multiple consumers without synchronization append the
        # results in random order
        self.assertEqual(sorted(results), inputs)

    eleza test_many_threads_nonblock(self):
        # Test multiple concurrent put() and get(block=False)
        N = 50
        q = self.q
        inputs = list(range(10000))
        results = self.run_threads(N, N, q, inputs,
                                   self.feed, self.consume_nonblock)

        self.assertEqual(sorted(results), inputs)

    eleza test_many_threads_timeout(self):
        # Test multiple concurrent put() and get(timeout=...)
        N = 50
        q = self.q
        inputs = list(range(1000))
        results = self.run_threads(N, N, q, inputs,
                                   self.feed, self.consume_timeout)

        self.assertEqual(sorted(results), inputs)

    eleza test_references(self):
        # The queue should lose references to each item as soon as
        # it leaves the queue.
        kundi C:
            pass

        N = 20
        q = self.q
        for i in range(N):
            q.put(C())
        for i in range(N):
            wr = weakref.ref(q.get())
            self.assertIsNone(wr())


kundi PySimpleQueueTest(BaseSimpleQueueTest, unittest.TestCase):

    queue = py_queue
    eleza setUp(self):
        self.type2test = self.queue._PySimpleQueue
        super().setUp()


@need_c_queue
kundi CSimpleQueueTest(BaseSimpleQueueTest, unittest.TestCase):

    queue = c_queue

    eleza setUp(self):
        self.type2test = self.queue.SimpleQueue
        super().setUp()

    eleza test_is_default(self):
        self.assertIs(self.type2test, self.queue.SimpleQueue)
        self.assertIs(self.type2test, self.queue.SimpleQueue)

    eleza test_reentrancy(self):
        # bpo-14976: put() may be called reentrantly in an asynchronous
        # callback.
        q = self.q
        gen = itertools.count()
        N = 10000
        results = []

        # This test exploits the fact that __del__ in a reference cycle
        # can be called any time the GC may run.

        kundi Circular(object):
            eleza __init__(self):
                self.circular = self

            eleza __del__(self):
                q.put(next(gen))

        while True:
            o = Circular()
            q.put(next(gen))
            del o
            results.append(q.get())
            ikiwa results[-1] >= N:
                break

        self.assertEqual(results, list(range(N + 1)))


ikiwa __name__ == "__main__":
    unittest.main()
