agiza queue
agiza sched
agiza threading
agiza time
agiza unittest
kutoka test agiza support


TIMEOUT = 10


kundi Timer:
    eleza __init__(self):
        self._cond = threading.Condition()
        self._time = 0
        self._stop = 0

    eleza time(self):
        ukijumuisha self._cond:
            rudisha self._time

    # increase the time but sio beyond the established limit
    eleza sleep(self, t):
        assert t >= 0
        ukijumuisha self._cond:
            t += self._time
            wakati self._stop < t:
                self._time = self._stop
                self._cond.wait()
            self._time = t

    # advance time limit kila user code
    eleza advance(self, t):
        assert t >= 0
        ukijumuisha self._cond:
            self._stop += t
            self._cond.notify_all()


kundi TestCase(unittest.TestCase):

    eleza test_enter(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        kila x kwenye [0.5, 0.4, 0.3, 0.2, 0.1]:
            z = scheduler.enter(x, 1, fun, (x,))
        scheduler.run()
        self.assertEqual(l, [0.1, 0.2, 0.3, 0.4, 0.5])

    eleza test_enterabs(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        kila x kwenye [0.05, 0.04, 0.03, 0.02, 0.01]:
            z = scheduler.enterabs(x, 1, fun, (x,))
        scheduler.run()
        self.assertEqual(l, [0.01, 0.02, 0.03, 0.04, 0.05])

    eleza test_enter_concurrent(self):
        q = queue.Queue()
        fun = q.put
        timer = Timer()
        scheduler = sched.scheduler(timer.time, timer.sleep)
        scheduler.enter(1, 1, fun, (1,))
        scheduler.enter(3, 1, fun, (3,))
        t = threading.Thread(target=scheduler.run)
        t.start()
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 1)
        self.assertKweli(q.empty())
        kila x kwenye [4, 5, 2]:
            z = scheduler.enter(x - 1, 1, fun, (x,))
        timer.advance(2)
        self.assertEqual(q.get(timeout=TIMEOUT), 2)
        self.assertEqual(q.get(timeout=TIMEOUT), 3)
        self.assertKweli(q.empty())
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 4)
        self.assertKweli(q.empty())
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 5)
        self.assertKweli(q.empty())
        timer.advance(1000)
        support.join_thread(t, timeout=TIMEOUT)
        self.assertKweli(q.empty())
        self.assertEqual(timer.time(), 5)

    eleza test_priority(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        kila priority kwenye [1, 2, 3, 4, 5]:
            z = scheduler.enterabs(0.01, priority, fun, (priority,))
        scheduler.run()
        self.assertEqual(l, [1, 2, 3, 4, 5])

    eleza test_cancel(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        now = time.time()
        event1 = scheduler.enterabs(now + 0.01, 1, fun, (0.01,))
        event2 = scheduler.enterabs(now + 0.02, 1, fun, (0.02,))
        event3 = scheduler.enterabs(now + 0.03, 1, fun, (0.03,))
        event4 = scheduler.enterabs(now + 0.04, 1, fun, (0.04,))
        event5 = scheduler.enterabs(now + 0.05, 1, fun, (0.05,))
        scheduler.cancel(event1)
        scheduler.cancel(event5)
        scheduler.run()
        self.assertEqual(l, [0.02, 0.03, 0.04])

    eleza test_cancel_concurrent(self):
        q = queue.Queue()
        fun = q.put
        timer = Timer()
        scheduler = sched.scheduler(timer.time, timer.sleep)
        now = timer.time()
        event1 = scheduler.enterabs(now + 1, 1, fun, (1,))
        event2 = scheduler.enterabs(now + 2, 1, fun, (2,))
        event4 = scheduler.enterabs(now + 4, 1, fun, (4,))
        event5 = scheduler.enterabs(now + 5, 1, fun, (5,))
        event3 = scheduler.enterabs(now + 3, 1, fun, (3,))
        t = threading.Thread(target=scheduler.run)
        t.start()
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 1)
        self.assertKweli(q.empty())
        scheduler.cancel(event2)
        scheduler.cancel(event5)
        timer.advance(1)
        self.assertKweli(q.empty())
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 3)
        self.assertKweli(q.empty())
        timer.advance(1)
        self.assertEqual(q.get(timeout=TIMEOUT), 4)
        self.assertKweli(q.empty())
        timer.advance(1000)
        support.join_thread(t, timeout=TIMEOUT)
        self.assertKweli(q.empty())
        self.assertEqual(timer.time(), 4)

    eleza test_empty(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        self.assertKweli(scheduler.empty())
        kila x kwenye [0.05, 0.04, 0.03, 0.02, 0.01]:
            z = scheduler.enterabs(x, 1, fun, (x,))
        self.assertUongo(scheduler.empty())
        scheduler.run()
        self.assertKweli(scheduler.empty())

    eleza test_queue(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        now = time.time()
        e5 = scheduler.enterabs(now + 0.05, 1, fun)
        e1 = scheduler.enterabs(now + 0.01, 1, fun)
        e2 = scheduler.enterabs(now + 0.02, 1, fun)
        e4 = scheduler.enterabs(now + 0.04, 1, fun)
        e3 = scheduler.enterabs(now + 0.03, 1, fun)
        # queue property ni supposed to rudisha an order list of
        # upcoming events
        self.assertEqual(scheduler.queue, [e1, e2, e3, e4, e5])

    eleza test_args_kwargs(self):
        seq = []
        eleza fun(*a, **b):
            seq.append((a, b))

        now = time.time()
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enterabs(now, 1, fun)
        scheduler.enterabs(now, 1, fun, argument=(1, 2))
        scheduler.enterabs(now, 1, fun, argument=('a', 'b'))
        scheduler.enterabs(now, 1, fun, argument=(1, 2), kwargs={"foo": 3})
        scheduler.run()
        self.assertCountEqual(seq, [
            ((), {}),
            ((1, 2), {}),
            (('a', 'b'), {}),
            ((1, 2), {'foo': 3})
        ])

    eleza test_run_non_blocking(self):
        l = []
        fun = lambda x: l.append(x)
        scheduler = sched.scheduler(time.time, time.sleep)
        kila x kwenye [10, 9, 8, 7, 6]:
            scheduler.enter(x, 1, fun, (x,))
        scheduler.run(blocking=Uongo)
        self.assertEqual(l, [])


ikiwa __name__ == "__main__":
    unittest.main()
