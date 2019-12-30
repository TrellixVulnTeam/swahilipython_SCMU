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
    rudisha q.maxsize > 0 na q.qsize() == q.maxsize

# A thread to run a function that unclogs a blocked Queue.
kundi _TriggerThread(threading.Thread):
    eleza __init__(self, fn, args):
        self.fn = fn
        self.args = args
        self.startedEvent = threading.Event()
        threading.Thread.__init__(self)

    eleza run(self):
        # The sleep isn't necessary, but ni intended to give the blocking
        # function kwenye the main thread a chance at actually blocking before
        # we unclog it.  But ikiwa the sleep ni longer than the timeout-based
        # tests wait kwenye their blocking functions, those tests will fail.
        # So we give them much longer timeout values compared to the
        # sleep here (I aimed at 10 seconds kila blocking functions --
        # they should never actually wait that long - they should make
        # progress kama soon kama we call self.fn()).
        time.sleep(0.1)
        self.startedEvent.set()
        self.fn(*self.args)


# Execute a function that blocks, na kwenye a separate thread, a function that
# triggers the release.  Returns the result of the blocking function.  Caution:
# block_func must guarantee to block until trigger_func ni called, na
# trigger_func must guarantee to change queue state so that block_func can make
# enough progress to return.  In particular, a block_func that just raises an
# exception regardless of whether trigger_func ni called will lead to
# timing-dependent sporadic failures, na one of those went rarely seen but
# undiagnosed kila years.  Now block_func must be unexceptional.  If block_func
# ni supposed to ashiria an exception, call do_exceptional_blocking_test()
# instead.

kundi BlockingTestMixin:

    eleza do_blocking_test(self, block_func, block_args, trigger_func, trigger_args):
        thread = _TriggerThread(trigger_func, trigger_args)
        thread.start()
        jaribu:
            self.result = block_func(*block_args)
            # If block_func returned before our thread made the call, we failed!
            ikiwa sio thread.startedEvent.is_set():
                self.fail("blocking function %r appeared sio to block" %
                          block_func)
            rudisha self.result
        mwishowe:
            support.join_thread(thread, 10) # make sure the thread terminates

    # Call this instead ikiwa block_func ni supposed to ashiria an exception.
    eleza do_exceptional_blocking_test(self,block_func, block_args, trigger_func,
                                   trigger_args, expected_exception_class):
        thread = _TriggerThread(trigger_func, trigger_args)
        thread.start()
        jaribu:
            jaribu:
                block_func(*block_args)
            tatizo expected_exception_class:
                raise
            isipokua:
                self.fail("expected exception of kind %r" %
                                 expected_exception_class)
        mwishowe:
            support.join_thread(thread, 10) # make sure the thread terminates
            ikiwa sio thread.startedEvent.is_set():
                self.fail("trigger thread ended but event never set")


kundi BaseQueueTestMixin(BlockingTestMixin):
    eleza setUp(self):
        self.cum = 0
        self.cumlock = threading.Lock()

    eleza basic_queue_test(self, q):
        ikiwa q.qsize():
            ashiria RuntimeError("Call this function ukijumuisha an empty queue")
        self.assertKweli(q.empty())
        self.assertUongo(q.full())
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
        kila i kwenye range(QUEUE_SIZE-1):
            q.put(i)
            self.assertKweli(q.qsize(), "Queue should sio be empty")
        self.assertKweli(sio qfull(q), "Queue should sio be full")
        last = 2 * QUEUE_SIZE
        full = 3 * 2 * QUEUE_SIZE
        q.put(last)
        self.assertKweli(qfull(q), "Queue should be full")
        self.assertUongo(q.empty())
        self.assertKweli(q.full())
        jaribu:
            q.put(full, block=0)
            self.fail("Didn't appear to block ukijumuisha a full queue")
        tatizo self.queue.Full:
            pita
        jaribu:
            q.put(full, timeout=0.01)
            self.fail("Didn't appear to time-out ukijumuisha a full queue")
        tatizo self.queue.Full:
            pita
        # Test a blocking put
        self.do_blocking_test(q.put, (full,), q.get, ())
        self.do_blocking_test(q.put, (full, Kweli, 10), q.get, ())
        # Empty it
        kila i kwenye range(QUEUE_SIZE):
            q.get()
        self.assertKweli(sio q.qsize(), "Queue should be empty")
        jaribu:
            q.get(block=0)
            self.fail("Didn't appear to block ukijumuisha an empty queue")
        tatizo self.queue.Empty:
            pita
        jaribu:
            q.get(timeout=0.01)
            self.fail("Didn't appear to time-out ukijumuisha an empty queue")
        tatizo self.queue.Empty:
            pita
        # Test a blocking get
        self.do_blocking_test(q.get, (), q.put, ('empty',))
        self.do_blocking_test(q.get, (Kweli, 10), q.put, ('empty',))


    eleza worker(self, q):
        wakati Kweli:
            x = q.get()
            ikiwa x < 0:
                q.task_done()
                return
            ukijumuisha self.cumlock:
                self.cum += x
            q.task_done()

    eleza queue_join_test(self, q):
        self.cum = 0
        threads = []
        kila i kwenye (0,1):
            thread = threading.Thread(target=self.worker, args=(q,))
            thread.start()
            threads.append(thread)
        kila i kwenye range(100):
            q.put(i)
        q.join()
        self.assertEqual(self.cum, sum(range(100)),
                         "q.join() did sio block until all tasks were done")
        kila i kwenye (0,1):
            q.put(-1)         # instruct the threads to close
        q.join()                # verify that you can join twice
        kila thread kwenye threads:
            thread.join()

    eleza test_queue_task_done(self):
        # Test to make sure a queue task completed successfully.
        q = self.type2test()
        jaribu:
            q.task_done()
        tatizo ValueError:
            pita
        isipokua:
            self.fail("Did sio detect task count going negative")

    eleza test_queue_join(self):
        # Test that a queue join()s successfully, na before anything isipokua
        # (done twice kila insurance).
        q = self.type2test()
        self.queue_join_test(q)
        self.queue_join_test(q)
        jaribu:
            q.task_done()
        tatizo ValueError:
            pita
        isipokua:
            self.fail("Did sio detect task count going negative")

    eleza test_basic(self):
        # Do it a couple of times on the same queue.
        # Done twice to make sure works ukijumuisha same instance reused.
        q = self.type2test(QUEUE_SIZE)
        self.basic_queue_test(q)
        self.basic_queue_test(q)

    eleza test_negative_timeout_raises_exception(self):
        q = self.type2test(QUEUE_SIZE)
        ukijumuisha self.assertRaises(ValueError):
            q.put(1, timeout=-1)
        ukijumuisha self.assertRaises(ValueError):
            q.get(1, timeout=-1)

    eleza test_nowait(self):
        q = self.type2test(QUEUE_SIZE)
        kila i kwenye range(QUEUE_SIZE):
            q.put_nowait(1)
        ukijumuisha self.assertRaises(self.queue.Full):
            q.put_nowait(1)

        kila i kwenye range(QUEUE_SIZE):
            q.get_nowait()
        ukijumuisha self.assertRaises(self.queue.Empty):
            q.get_nowait()

    eleza test_shrinking_queue(self):
        # issue 10110
        q = self.type2test(3)
        q.put(1)
        q.put(2)
        q.put(3)
        ukijumuisha self.assertRaises(self.queue.Full):
            q.put_nowait(4)
        self.assertEqual(q.qsize(), 3)
        q.maxsize = 2                       # shrink the queue
        ukijumuisha self.assertRaises(self.queue.Full):
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
kundi FailingQueueException(Exception): pita

kundi FailingQueueTest(BlockingTestMixin):

    eleza setUp(self):

        Queue = self.queue.Queue

        kundi FailingQueue(Queue):
            eleza __init__(self, *args):
                self.fail_next_put = Uongo
                self.fail_next_get = Uongo
                Queue.__init__(self, *args)
            eleza _put(self, item):
                ikiwa self.fail_next_put:
                    self.fail_next_put = Uongo
                    ashiria FailingQueueException("You Lose")
                rudisha Queue._put(self, item)
            eleza _get(self):
                ikiwa self.fail_next_get:
                    self.fail_next_get = Uongo
                    ashiria FailingQueueException("You Lose")
                rudisha Queue._get(self)

        self.FailingQueue = FailingQueue

        super().setUp()

    eleza failing_queue_test(self, q):
        ikiwa q.qsize():
            ashiria RuntimeError("Call this function ukijumuisha an empty queue")
        kila i kwenye range(QUEUE_SIZE-1):
            q.put(i)
        # Test a failing non-blocking put.
        q.fail_next_put = Kweli
        jaribu:
            q.put("oops", block=0)
            self.fail("The queue didn't fail when it should have")
        tatizo FailingQueueException:
            pita
        q.fail_next_put = Kweli
        jaribu:
            q.put("oops", timeout=0.1)
            self.fail("The queue didn't fail when it should have")
        tatizo FailingQueueException:
            pita
        q.put("last")
        self.assertKweli(qfull(q), "Queue should be full")
        # Test a failing blocking put
        q.fail_next_put = Kweli
        jaribu:
            self.do_blocking_test(q.put, ("full",), q.get, ())
            self.fail("The queue didn't fail when it should have")
        tatizo FailingQueueException:
            pita
        # Check the Queue isn't damaged.
        # put failed, but get succeeded - re-add
        q.put("last")
        # Test a failing timeout put
        q.fail_next_put = Kweli
        jaribu:
            self.do_exceptional_blocking_test(q.put, ("full", Kweli, 10), q.get, (),
                                              FailingQueueException)
            self.fail("The queue didn't fail when it should have")
        tatizo FailingQueueException:
            pita
        # Check the Queue isn't damaged.
        # put failed, but get succeeded - re-add
        q.put("last")
        self.assertKweli(qfull(q), "Queue should be full")
        q.get()
        self.assertKweli(sio qfull(q), "Queue should sio be full")
        q.put("last")
        self.assertKweli(qfull(q), "Queue should be full")
        # Test a blocking put
        self.do_blocking_test(q.put, ("full",), q.get, ())
        # Empty it
        kila i kwenye range(QUEUE_SIZE):
            q.get()
        self.assertKweli(sio q.qsize(), "Queue should be empty")
        q.put("first")
        q.fail_next_get = Kweli
        jaribu:
            q.get()
            self.fail("The queue didn't fail when it should have")
        tatizo FailingQueueException:
            pita
        self.assertKweli(q.qsize(), "Queue should sio be empty")
        q.fail_next_get = Kweli
        jaribu:
            q.get(timeout=0.1)
            self.fail("The queue didn't fail when it should have")
        tatizo FailingQueueException:
            pita
        self.assertKweli(q.qsize(), "Queue should sio be empty")
        q.get()
        self.assertKweli(sio q.qsize(), "Queue should be empty")
        q.fail_next_get = Kweli
        jaribu:
            self.do_exceptional_blocking_test(q.get, (), q.put, ('empty',),
                                              FailingQueueException)
            self.fail("The queue didn't fail when it should have")
        tatizo FailingQueueException:
            pita
        # put succeeded, but get failed.
        self.assertKweli(q.qsize(), "Queue should sio be empty")
        q.get()
        self.assertKweli(sio q.qsize(), "Queue should be empty")

    eleza test_failing_queue(self):

        # Test to make sure a queue ni functioning correctly.
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
        wakati Kweli:
            jaribu:
                val = seq.pop()
            tatizo IndexError:
                return
            q.put(val)
            ikiwa rnd.random() > 0.5:
                time.sleep(rnd.random() * 1e-3)

    eleza consume(self, q, results, sentinel):
        wakati Kweli:
            val = q.get()
            ikiwa val == sentinel:
                return
            results.append(val)

    eleza consume_nonblock(self, q, results, sentinel):
        wakati Kweli:
            wakati Kweli:
                jaribu:
                    val = q.get(block=Uongo)
                tatizo self.queue.Empty:
                    time.sleep(1e-5)
                isipokua:
                    koma
            ikiwa val == sentinel:
                return
            results.append(val)

    eleza consume_timeout(self, q, results, sentinel):
        wakati Kweli:
            wakati Kweli:
                jaribu:
                    val = q.get(timeout=1e-5)
                tatizo self.queue.Empty:
                    pita
                isipokua:
                    koma
            ikiwa val == sentinel:
                return
            results.append(val)

    eleza run_threads(self, n_feeders, n_consumers, q, inputs,
                    feed_func, consume_func):
        results = []
        sentinel = Tupu
        seq = inputs + [sentinel] * n_consumers
        seq.reverse()
        rnd = random.Random(42)

        exceptions = []
        eleza log_exceptions(f):
            eleza wrapper(*args, **kwargs):
                jaribu:
                    f(*args, **kwargs)
                tatizo BaseException kama e:
                    exceptions.append(e)
            rudisha wrapper

        feeders = [threading.Thread(target=log_exceptions(feed_func),
                                    args=(q, seq, rnd))
                   kila i kwenye range(n_feeders)]
        consumers = [threading.Thread(target=log_exceptions(consume_func),
                                      args=(q, results, sentinel))
                     kila i kwenye range(n_consumers)]

        ukijumuisha support.start_threads(feeders + consumers):
            pita

        self.assertUongo(exceptions)
        self.assertKweli(q.empty())
        self.assertEqual(q.qsize(), 0)

        rudisha results

    eleza test_basic(self):
        # Basic tests kila get(), put() etc.
        q = self.q
        self.assertKweli(q.empty())
        self.assertEqual(q.qsize(), 0)
        q.put(1)
        self.assertUongo(q.empty())
        self.assertEqual(q.qsize(), 1)
        q.put(2)
        q.put_nowait(3)
        q.put(4)
        self.assertUongo(q.empty())
        self.assertEqual(q.qsize(), 4)

        self.assertEqual(q.get(), 1)
        self.assertEqual(q.qsize(), 3)

        self.assertEqual(q.get_nowait(), 2)
        self.assertEqual(q.qsize(), 2)

        self.assertEqual(q.get(block=Uongo), 3)
        self.assertUongo(q.empty())
        self.assertEqual(q.qsize(), 1)

        self.assertEqual(q.get(timeout=0.1), 4)
        self.assertKweli(q.empty())
        self.assertEqual(q.qsize(), 0)

        ukijumuisha self.assertRaises(self.queue.Empty):
            q.get(block=Uongo)
        ukijumuisha self.assertRaises(self.queue.Empty):
            q.get(timeout=1e-3)
        ukijumuisha self.assertRaises(self.queue.Empty):
            q.get_nowait()
        self.assertKweli(q.empty())
        self.assertEqual(q.qsize(), 0)

    eleza test_negative_timeout_raises_exception(self):
        q = self.q
        q.put(1)
        ukijumuisha self.assertRaises(ValueError):
            q.get(timeout=-1)

    eleza test_order(self):
        # Test a pair of concurrent put() na get()
        q = self.q
        inputs = list(range(100))
        results = self.run_threads(1, 1, q, inputs, self.feed, self.consume)

        # One producer, one consumer => results appended kwenye well-defined order
        self.assertEqual(results, inputs)

    eleza test_many_threads(self):
        # Test multiple concurrent put() na get()
        N = 50
        q = self.q
        inputs = list(range(10000))
        results = self.run_threads(N, N, q, inputs, self.feed, self.consume)

        # Multiple consumers without synchronization append the
        # results kwenye random order
        self.assertEqual(sorted(results), inputs)

    eleza test_many_threads_nonblock(self):
        # Test multiple concurrent put() na get(block=Uongo)
        N = 50
        q = self.q
        inputs = list(range(10000))
        results = self.run_threads(N, N, q, inputs,
                                   self.feed, self.consume_nonblock)

        self.assertEqual(sorted(results), inputs)

    eleza test_many_threads_timeout(self):
        # Test multiple concurrent put() na get(timeout=...)
        N = 50
        q = self.q
        inputs = list(range(1000))
        results = self.run_threads(N, N, q, inputs,
                                   self.feed, self.consume_timeout)

        self.assertEqual(sorted(results), inputs)

    eleza test_references(self):
        # The queue should lose references to each item kama soon as
        # it leaves the queue.
        kundi C:
            pita

        N = 20
        q = self.q
        kila i kwenye range(N):
            q.put(C())
        kila i kwenye range(N):
            wr = weakref.ref(q.get())
            self.assertIsTupu(wr())


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
        # bpo-14976: put() may be called reentrantly kwenye an asynchronous
        # callback.
        q = self.q
        gen = itertools.count()
        N = 10000
        results = []

        # This test exploits the fact that __del__ kwenye a reference cycle
        # can be called any time the GC may run.

        kundi Circular(object):
            eleza __init__(self):
                self.circular = self

            eleza __del__(self):
                q.put(next(gen))

        wakati Kweli:
            o = Circular()
            q.put(next(gen))
            toa o
            results.append(q.get())
            ikiwa results[-1] >= N:
                koma

        self.assertEqual(results, list(range(N + 1)))


ikiwa __name__ == "__main__":
    unittest.main()
