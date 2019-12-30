"""Tests kila queues.py"""

agiza unittest
kutoka unittest agiza mock

agiza asyncio
kutoka test.test_asyncio agiza utils kama test_utils


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi _QueueTestBase(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()


kundi QueueBasicTests(_QueueTestBase):

    eleza _test_repr_or_str(self, fn, expect_id):
        """Test Queue's repr ama str.

        fn ni repr ama str. expect_id ni Kweli ikiwa we expect the Queue's id to
        appear kwenye fn(Queue()).
        """
        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.1, when)
            when = tuma 0.1
            self.assertAlmostEqual(0.2, when)
            tuma 0.1

        loop = self.new_test_loop(gen)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=loop)
        self.assertKweli(fn(q).startswith('<Queue'), fn(q))
        id_is_present = hex(id(q)) kwenye fn(q)
        self.assertEqual(expect_id, id_is_present)

        async eleza add_getter():
            q = asyncio.Queue(loop=loop)
            # Start a task that waits to get.
            loop.create_task(q.get())
            # Let it start waiting.
            await asyncio.sleep(0.1)
            self.assertKweli('_getters[1]' kwenye fn(q))
            # resume q.get coroutine to finish generator
            q.put_nowait(0)

        ukijumuisha self.assertWarns(DeprecationWarning):
            loop.run_until_complete(add_getter())

        async eleza add_putter():
            q = asyncio.Queue(maxsize=1, loop=loop)
            q.put_nowait(1)
            # Start a task that waits to put.
            loop.create_task(q.put(2))
            # Let it start waiting.
            await asyncio.sleep(0.1)
            self.assertKweli('_putters[1]' kwenye fn(q))
            # resume q.put coroutine to finish generator
            q.get_nowait()

        ukijumuisha self.assertWarns(DeprecationWarning):
            loop.run_until_complete(add_putter())
            q = asyncio.Queue(loop=loop)
        q.put_nowait(1)
        self.assertKweli('_queue=[1]' kwenye fn(q))

    eleza test_ctor_loop(self):
        loop = mock.Mock()
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=loop)
        self.assertIs(q._loop, loop)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        self.assertIs(q._loop, self.loop)

    eleza test_ctor_noloop(self):
        asyncio.set_event_loop(self.loop)
        q = asyncio.Queue()
        self.assertIs(q._loop, self.loop)

    eleza test_repr(self):
        self._test_repr_or_str(repr, Kweli)

    eleza test_str(self):
        self._test_repr_or_str(str, Uongo)

    eleza test_empty(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        self.assertKweli(q.empty())
        q.put_nowait(1)
        self.assertUongo(q.empty())
        self.assertEqual(1, q.get_nowait())
        self.assertKweli(q.empty())

    eleza test_full(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        self.assertUongo(q.full())

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(maxsize=1, loop=self.loop)
        q.put_nowait(1)
        self.assertKweli(q.full())

    eleza test_order(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        kila i kwenye [1, 3, 2]:
            q.put_nowait(i)

        items = [q.get_nowait() kila _ kwenye range(3)]
        self.assertEqual([1, 3, 2], items)

    eleza test_maxsize(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.01, when)
            when = tuma 0.01
            self.assertAlmostEqual(0.02, when)
            tuma 0.01

        loop = self.new_test_loop(gen)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(maxsize=2, loop=loop)
        self.assertEqual(2, q.maxsize)
        have_been_put = []

        async eleza putter():
            kila i kwenye range(3):
                await q.put(i)
                have_been_put.append(i)
            rudisha Kweli

        async eleza test():
            t = loop.create_task(putter())
            await asyncio.sleep(0.01)

            # The putter ni blocked after putting two items.
            self.assertEqual([0, 1], have_been_put)
            self.assertEqual(0, q.get_nowait())

            # Let the putter resume na put last item.
            await asyncio.sleep(0.01)
            self.assertEqual([0, 1, 2], have_been_put)
            self.assertEqual(1, q.get_nowait())
            self.assertEqual(2, q.get_nowait())

            self.assertKweli(t.done())
            self.assertKweli(t.result())

        loop.run_until_complete(test())
        self.assertAlmostEqual(0.02, loop.time())


kundi QueueGetTests(_QueueTestBase):

    eleza test_blocking_get(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        q.put_nowait(1)

        async eleza queue_get():
            rudisha await q.get()

        res = self.loop.run_until_complete(queue_get())
        self.assertEqual(1, res)

    eleza test_get_with_putters(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(1, loop=self.loop)
        q.put_nowait(1)

        waiter = self.loop.create_future()
        q._putters.append(waiter)

        res = self.loop.run_until_complete(q.get())
        self.assertEqual(1, res)
        self.assertKweli(waiter.done())
        self.assertIsTupu(waiter.result())

    eleza test_blocking_get_wait(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.01, when)
            tuma 0.01

        loop = self.new_test_loop(gen)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=loop)
            started = asyncio.Event(loop=loop)
        finished = Uongo

        async eleza queue_get():
            nonlocal finished
            started.set()
            res = await q.get()
            finished = Kweli
            rudisha res

        async eleza queue_put():
            loop.call_later(0.01, q.put_nowait, 1)
            queue_get_task = loop.create_task(queue_get())
            await started.wait()
            self.assertUongo(finished)
            res = await queue_get_task
            self.assertKweli(finished)
            rudisha res

        res = loop.run_until_complete(queue_put())
        self.assertEqual(1, res)
        self.assertAlmostEqual(0.01, loop.time())

    eleza test_nonblocking_get(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        q.put_nowait(1)
        self.assertEqual(1, q.get_nowait())

    eleza test_nonblocking_get_exception(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        self.assertRaises(asyncio.QueueEmpty, q.get_nowait)

    eleza test_get_cancelled(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.01, when)
            when = tuma 0.01
            self.assertAlmostEqual(0.061, when)
            tuma 0.05

        loop = self.new_test_loop(gen)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=loop)

        async eleza queue_get():
            rudisha await asyncio.wait_for(q.get(), 0.051)

        async eleza test():
            get_task = loop.create_task(queue_get())
            await asyncio.sleep(0.01)  # let the task start
            q.put_nowait(1)
            rudisha await get_task

        self.assertEqual(1, loop.run_until_complete(test()))
        self.assertAlmostEqual(0.06, loop.time())

    eleza test_get_cancelled_race(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)

        t1 = self.loop.create_task(q.get())
        t2 = self.loop.create_task(q.get())

        test_utils.run_briefly(self.loop)
        t1.cancel()
        test_utils.run_briefly(self.loop)
        self.assertKweli(t1.done())
        q.put_nowait('a')
        test_utils.run_briefly(self.loop)
        self.assertEqual(t2.result(), 'a')

    eleza test_get_with_waiting_putters(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop, maxsize=1)
        self.loop.create_task(q.put('a'))
        self.loop.create_task(q.put('b'))
        test_utils.run_briefly(self.loop)
        self.assertEqual(self.loop.run_until_complete(q.get()), 'a')
        self.assertEqual(self.loop.run_until_complete(q.get()), 'b')

    eleza test_why_are_getters_waiting(self):
        # From issue #268.

        async eleza consumer(queue, num_expected):
            kila _ kwenye range(num_expected):
                await queue.get()

        async eleza producer(queue, num_items):
            kila i kwenye range(num_items):
                await queue.put(i)

        queue_size = 1
        producer_num_items = 5

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(queue_size, loop=self.loop)

        self.loop.run_until_complete(
            asyncio.gather(producer(q, producer_num_items),
                           consumer(q, producer_num_items),
                           loop=self.loop),
            )

    eleza test_cancelled_getters_not_being_held_in_self_getters(self):
        eleza a_generator():
            tuma 0.1
            tuma 0.2

        self.loop = self.new_test_loop(a_generator)

        async eleza consumer(queue):
            jaribu:
                item = await asyncio.wait_for(queue.get(), 0.1)
            tatizo asyncio.TimeoutError:
                pita

        ukijumuisha self.assertWarns(DeprecationWarning):
            queue = asyncio.Queue(loop=self.loop, maxsize=5)
        self.loop.run_until_complete(self.loop.create_task(consumer(queue)))
        self.assertEqual(len(queue._getters), 0)


kundi QueuePutTests(_QueueTestBase):

    eleza test_blocking_put(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)

        async eleza queue_put():
            # No maxsize, won't block.
            await q.put(1)

        self.loop.run_until_complete(queue_put())

    eleza test_blocking_put_wait(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.01, when)
            tuma 0.01

        loop = self.new_test_loop(gen)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(maxsize=1, loop=loop)
            started = asyncio.Event(loop=loop)
        finished = Uongo

        async eleza queue_put():
            nonlocal finished
            started.set()
            await q.put(1)
            await q.put(2)
            finished = Kweli

        async eleza queue_get():
            loop.call_later(0.01, q.get_nowait)
            queue_put_task = loop.create_task(queue_put())
            await started.wait()
            self.assertUongo(finished)
            await queue_put_task
            self.assertKweli(finished)

        loop.run_until_complete(queue_get())
        self.assertAlmostEqual(0.01, loop.time())

    eleza test_nonblocking_put(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        q.put_nowait(1)
        self.assertEqual(1, q.get_nowait())

    eleza test_get_cancel_drop_one_pending_reader(self):
        eleza gen():
            tuma 0.01
            tuma 0.1

        loop = self.new_test_loop(gen)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=loop)

        reader = loop.create_task(q.get())

        loop.run_until_complete(asyncio.sleep(0.01))

        q.put_nowait(1)
        q.put_nowait(2)
        reader.cancel()

        jaribu:
            loop.run_until_complete(reader)
        tatizo asyncio.CancelledError:
            # try again
            reader = loop.create_task(q.get())
            loop.run_until_complete(reader)

        result = reader.result()
        # ikiwa we get 2, it means 1 got dropped!
        self.assertEqual(1, result)

    eleza test_get_cancel_drop_many_pending_readers(self):
        eleza gen():
            tuma 0.01
            tuma 0.1

        loop = self.new_test_loop(gen)
        loop.set_debug(Kweli)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=loop)

        reader1 = loop.create_task(q.get())
        reader2 = loop.create_task(q.get())
        reader3 = loop.create_task(q.get())

        loop.run_until_complete(asyncio.sleep(0.01))

        q.put_nowait(1)
        q.put_nowait(2)
        reader1.cancel()

        jaribu:
            loop.run_until_complete(reader1)
        tatizo asyncio.CancelledError:
            pita

        loop.run_until_complete(reader3)

        # It ni undefined kwenye which order concurrent readers receive results.
        self.assertEqual({reader2.result(), reader3.result()}, {1, 2})

    eleza test_put_cancel_drop(self):

        eleza gen():
            tuma 0.01
            tuma 0.1

        loop = self.new_test_loop(gen)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(1, loop=loop)

        q.put_nowait(1)

        # putting a second item kwenye the queue has to block (qsize=1)
        writer = loop.create_task(q.put(2))
        loop.run_until_complete(asyncio.sleep(0.01))

        value1 = q.get_nowait()
        self.assertEqual(value1, 1)

        writer.cancel()
        jaribu:
            loop.run_until_complete(writer)
        tatizo asyncio.CancelledError:
            # try again
            writer = loop.create_task(q.put(2))
            loop.run_until_complete(writer)

        value2 = q.get_nowait()
        self.assertEqual(value2, 2)
        self.assertEqual(q.qsize(), 0)

    eleza test_nonblocking_put_exception(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(maxsize=1, loop=self.loop)
        q.put_nowait(1)
        self.assertRaises(asyncio.QueueFull, q.put_nowait, 2)

    eleza test_float_maxsize(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(maxsize=1.3, loop=self.loop)
        q.put_nowait(1)
        q.put_nowait(2)
        self.assertKweli(q.full())
        self.assertRaises(asyncio.QueueFull, q.put_nowait, 3)

        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(maxsize=1.3, loop=self.loop)

        async eleza queue_put():
            await q.put(1)
            await q.put(2)
            self.assertKweli(q.full())
        self.loop.run_until_complete(queue_put())

    eleza test_put_cancelled(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)

        async eleza queue_put():
            await q.put(1)
            rudisha Kweli

        async eleza test():
            rudisha await q.get()

        t = self.loop.create_task(queue_put())
        self.assertEqual(1, self.loop.run_until_complete(test()))
        self.assertKweli(t.done())
        self.assertKweli(t.result())

    eleza test_put_cancelled_race(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop, maxsize=1)

        put_a = self.loop.create_task(q.put('a'))
        put_b = self.loop.create_task(q.put('b'))
        put_c = self.loop.create_task(q.put('X'))

        test_utils.run_briefly(self.loop)
        self.assertKweli(put_a.done())
        self.assertUongo(put_b.done())

        put_c.cancel()
        test_utils.run_briefly(self.loop)
        self.assertKweli(put_c.done())
        self.assertEqual(q.get_nowait(), 'a')
        test_utils.run_briefly(self.loop)
        self.assertEqual(q.get_nowait(), 'b')

        self.loop.run_until_complete(put_b)

    eleza test_put_with_waiting_getters(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.Queue(loop=self.loop)
        t = self.loop.create_task(q.get())
        test_utils.run_briefly(self.loop)
        self.loop.run_until_complete(q.put('a'))
        self.assertEqual(self.loop.run_until_complete(t), 'a')

    eleza test_why_are_putters_waiting(self):
        # From issue #265.

        ukijumuisha self.assertWarns(DeprecationWarning):
            queue = asyncio.Queue(2, loop=self.loop)

        async eleza putter(item):
            await queue.put(item)

        async eleza getter():
            await asyncio.sleep(0)
            num = queue.qsize()
            kila _ kwenye range(num):
                item = queue.get_nowait()

        t0 = putter(0)
        t1 = putter(1)
        t2 = putter(2)
        t3 = putter(3)
        self.loop.run_until_complete(
            asyncio.gather(getter(), t0, t1, t2, t3, loop=self.loop))

    eleza test_cancelled_puts_not_being_held_in_self_putters(self):
        eleza a_generator():
            tuma 0.01
            tuma 0.1

        loop = self.new_test_loop(a_generator)

        # Full queue.
        ukijumuisha self.assertWarns(DeprecationWarning):
            queue = asyncio.Queue(loop=loop, maxsize=1)
        queue.put_nowait(1)

        # Task waiting kila space to put an item kwenye the queue.
        put_task = loop.create_task(queue.put(1))
        loop.run_until_complete(asyncio.sleep(0.01))

        # Check that the putter ni correctly removed kutoka queue._putters when
        # the task ni canceled.
        self.assertEqual(len(queue._putters), 1)
        put_task.cancel()
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            loop.run_until_complete(put_task)
        self.assertEqual(len(queue._putters), 0)

    eleza test_cancelled_put_silence_value_error_exception(self):
        eleza gen():
            tuma 0.01
            tuma 0.1

        loop = self.new_test_loop(gen)

        # Full Queue.
        ukijumuisha self.assertWarns(DeprecationWarning):
            queue = asyncio.Queue(1, loop=loop)
        queue.put_nowait(1)

        # Task waiting kila space to put a item kwenye the queue.
        put_task = loop.create_task(queue.put(1))
        loop.run_until_complete(asyncio.sleep(0.01))

        # get_nowait() remove the future of put_task kutoka queue._putters.
        queue.get_nowait()
        # When canceled, queue.put ni going to remove its future from
        # self._putters but it was removed previously by queue.get_nowait().
        put_task.cancel()

        # The ValueError exception triggered by queue._putters.remove(putter)
        # inside queue.put should be silenced.
        # If the ValueError ni silenced we should catch a CancelledError.
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            loop.run_until_complete(put_task)


kundi LifoQueueTests(_QueueTestBase):

    eleza test_order(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.LifoQueue(loop=self.loop)
        kila i kwenye [1, 3, 2]:
            q.put_nowait(i)

        items = [q.get_nowait() kila _ kwenye range(3)]
        self.assertEqual([2, 3, 1], items)


kundi PriorityQueueTests(_QueueTestBase):

    eleza test_order(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = asyncio.PriorityQueue(loop=self.loop)
        kila i kwenye [1, 3, 2]:
            q.put_nowait(i)

        items = [q.get_nowait() kila _ kwenye range(3)]
        self.assertEqual([1, 2, 3], items)


kundi _QueueJoinTestMixin:

    q_class = Tupu

    eleza test_task_done_underflow(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = self.q_class(loop=self.loop)
        self.assertRaises(ValueError, q.task_done)

    eleza test_task_done(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = self.q_class(loop=self.loop)
        kila i kwenye range(100):
            q.put_nowait(i)

        accumulator = 0

        # Two workers get items kutoka the queue na call task_done after each.
        # Join the queue na assert all items have been processed.
        running = Kweli

        async eleza worker():
            nonlocal accumulator

            wakati running:
                item = await q.get()
                accumulator += item
                q.task_done()

        async eleza test():
            tasks = [self.loop.create_task(worker())
                     kila index kwenye range(2)]

            await q.join()
            rudisha tasks

        tasks = self.loop.run_until_complete(test())
        self.assertEqual(sum(range(100)), accumulator)

        # close running generators
        running = Uongo
        kila i kwenye range(len(tasks)):
            q.put_nowait(0)
        self.loop.run_until_complete(asyncio.wait(tasks))

    eleza test_join_empty_queue(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = self.q_class(loop=self.loop)

        # Test that a queue join()s successfully, na before anything isipokua
        # (done twice kila insurance).

        async eleza join():
            await q.join()
            await q.join()

        self.loop.run_until_complete(join())

    eleza test_format(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            q = self.q_class(loop=self.loop)
        self.assertEqual(q._format(), 'maxsize=0')

        q._unfinished_tasks = 2
        self.assertEqual(q._format(), 'maxsize=0 tasks=2')


kundi QueueJoinTests(_QueueJoinTestMixin, _QueueTestBase):
    q_class = asyncio.Queue


kundi LifoQueueJoinTests(_QueueJoinTestMixin, _QueueTestBase):
    q_class = asyncio.LifoQueue


kundi PriorityQueueJoinTests(_QueueJoinTestMixin, _QueueTestBase):
    q_class = asyncio.PriorityQueue


ikiwa __name__ == '__main__':
    unittest.main()
