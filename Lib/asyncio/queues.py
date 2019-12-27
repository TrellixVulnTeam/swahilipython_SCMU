__all__ = ('Queue', 'PriorityQueue', 'LifoQueue', 'QueueFull', 'QueueEmpty')

agiza collections
agiza heapq
agiza warnings

kutoka . agiza events
kutoka . agiza locks


kundi QueueEmpty(Exception):
    """Raised when Queue.get_nowait() is called on an empty Queue."""
    pass


kundi QueueFull(Exception):
    """Raised when the Queue.put_nowait() method is called on a full Queue."""
    pass


kundi Queue:
    """A queue, useful for coordinating producer and consumer coroutines.

    If maxsize is less than or equal to zero, the queue size is infinite. If it
    is an integer greater than 0, then "await put()" will block when the
    queue reaches maxsize, until an item is removed by get().

    Unlike the standard library Queue, you can reliably know this Queue's size
    with qsize(), since your single-threaded asyncio application won't be
    interrupted between calling qsize() and doing an operation on the Queue.
    """

    eleza __init__(self, maxsize=0, *, loop=None):
        ikiwa loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)
        self._maxsize = maxsize

        # Futures.
        self._getters = collections.deque()
        # Futures.
        self._putters = collections.deque()
        self._unfinished_tasks = 0
        self._finished = locks.Event(loop=loop)
        self._finished.set()
        self._init(maxsize)

    # These three are overridable in subclasses.

    eleza _init(self, maxsize):
        self._queue = collections.deque()

    eleza _get(self):
        rudisha self._queue.popleft()

    eleza _put(self, item):
        self._queue.append(item)

    # End of the overridable methods.

    eleza _wakeup_next(self, waiters):
        # Wake up the next waiter (ikiwa any) that isn't cancelled.
        while waiters:
            waiter = waiters.popleft()
            ikiwa not waiter.done():
                waiter.set_result(None)
                break

    eleza __repr__(self):
        rudisha f'<{type(self).__name__} at {id(self):#x} {self._format()}>'

    eleza __str__(self):
        rudisha f'<{type(self).__name__} {self._format()}>'

    eleza _format(self):
        result = f'maxsize={self._maxsize!r}'
        ikiwa getattr(self, '_queue', None):
            result += f' _queue={list(self._queue)!r}'
        ikiwa self._getters:
            result += f' _getters[{len(self._getters)}]'
        ikiwa self._putters:
            result += f' _putters[{len(self._putters)}]'
        ikiwa self._unfinished_tasks:
            result += f' tasks={self._unfinished_tasks}'
        rudisha result

    eleza qsize(self):
        """Number of items in the queue."""
        rudisha len(self._queue)

    @property
    eleza maxsize(self):
        """Number of items allowed in the queue."""
        rudisha self._maxsize

    eleza empty(self):
        """Return True ikiwa the queue is empty, False otherwise."""
        rudisha not self._queue

    eleza full(self):
        """Return True ikiwa there are maxsize items in the queue.

        Note: ikiwa the Queue was initialized with maxsize=0 (the default),
        then full() is never True.
        """
        ikiwa self._maxsize <= 0:
            rudisha False
        else:
            rudisha self.qsize() >= self._maxsize

    async eleza put(self, item):
        """Put an item into the queue.

        Put an item into the queue. If the queue is full, wait until a free
        slot is available before adding item.
        """
        while self.full():
            putter = self._loop.create_future()
            self._putters.append(putter)
            try:
                await putter
            except:
                putter.cancel()  # Just in case putter is not done yet.
                try:
                    # Clean self._putters kutoka canceled putters.
                    self._putters.remove(putter)
                except ValueError:
                    # The putter could be removed kutoka self._putters by a
                    # previous get_nowait call.
                    pass
                ikiwa not self.full() and not putter.cancelled():
                    # We were woken up by get_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._putters)
                raise
        rudisha self.put_nowait(item)

    eleza put_nowait(self, item):
        """Put an item into the queue without blocking.

        If no free slot is immediately available, raise QueueFull.
        """
        ikiwa self.full():
            raise QueueFull
        self._put(item)
        self._unfinished_tasks += 1
        self._finished.clear()
        self._wakeup_next(self._getters)

    async eleza get(self):
        """Remove and rudisha an item kutoka the queue.

        If queue is empty, wait until an item is available.
        """
        while self.empty():
            getter = self._loop.create_future()
            self._getters.append(getter)
            try:
                await getter
            except:
                getter.cancel()  # Just in case getter is not done yet.
                try:
                    # Clean self._getters kutoka canceled getters.
                    self._getters.remove(getter)
                except ValueError:
                    # The getter could be removed kutoka self._getters by a
                    # previous put_nowait call.
                    pass
                ikiwa not self.empty() and not getter.cancelled():
                    # We were woken up by put_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._getters)
                raise
        rudisha self.get_nowait()

    eleza get_nowait(self):
        """Remove and rudisha an item kutoka the queue.

        Return an item ikiwa one is immediately available, else raise QueueEmpty.
        """
        ikiwa self.empty():
            raise QueueEmpty
        item = self._get()
        self._wakeup_next(self._putters)
        rudisha item

    eleza task_done(self):
        """Indicate that a formerly enqueued task is complete.

        Used by queue consumers. For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items have
        been processed (meaning that a task_done() call was received for every
        item that had been put() into the queue).

        Raises ValueError ikiwa called more times than there were items placed in
        the queue.
        """
        ikiwa self._unfinished_tasks <= 0:
            raise ValueError('task_done() called too many times')
        self._unfinished_tasks -= 1
        ikiwa self._unfinished_tasks == 0:
            self._finished.set()

    async eleza join(self):
        """Block until all items in the queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer calls task_done() to
        indicate that the item was retrieved and all work on it is complete.
        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        ikiwa self._unfinished_tasks > 0:
            await self._finished.wait()


kundi PriorityQueue(Queue):
    """A subkundi of Queue; retrieves entries in priority order (lowest first).

    Entries are typically tuples of the form: (priority number, data).
    """

    eleza _init(self, maxsize):
        self._queue = []

    eleza _put(self, item, heappush=heapq.heappush):
        heappush(self._queue, item)

    eleza _get(self, heappop=heapq.heappop):
        rudisha heappop(self._queue)


kundi LifoQueue(Queue):
    """A subkundi of Queue that retrieves most recently added entries first."""

    eleza _init(self, maxsize):
        self._queue = []

    eleza _put(self, item):
        self._queue.append(item)

    eleza _get(self):
        rudisha self._queue.pop()
