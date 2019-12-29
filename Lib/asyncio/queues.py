__all__ = ('Queue', 'PriorityQueue', 'LifoQueue', 'QueueFull', 'QueueEmpty')

agiza collections
agiza heapq
agiza warnings

kutoka . agiza events
kutoka . agiza locks


kundi QueueEmpty(Exception):
    """Raised when Queue.get_nowait() ni called on an empty Queue."""
    pita


kundi QueueFull(Exception):
    """Raised when the Queue.put_nowait() method ni called on a full Queue."""
    pita


kundi Queue:
    """A queue, useful kila coordinating producer na consumer coroutines.

    If maxsize ni less than ama equal to zero, the queue size ni infinite. If it
    ni an integer greater than 0, then "await put()" will block when the
    queue reaches maxsize, until an item ni removed by get().

    Unlike the standard library Queue, you can reliably know this Queue's size
    ukijumuisha qsize(), since your single-threaded asyncio application won't be
    interrupted between calling qsize() na doing an operation on the Queue.
    """

    eleza __init__(self, maxsize=0, *, loop=Tupu):
        ikiwa loop ni Tupu:
            self._loop = events.get_event_loop()
        isipokua:
            self._loop = loop
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
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

    # These three are overridable kwenye subclasses.

    eleza _init(self, maxsize):
        self._queue = collections.deque()

    eleza _get(self):
        rudisha self._queue.popleft()

    eleza _put(self, item):
        self._queue.append(item)

    # End of the overridable methods.

    eleza _wakeup_next(self, waiters):
        # Wake up the next waiter (ikiwa any) that isn't cancelled.
        wakati waiters:
            waiter = waiters.popleft()
            ikiwa sio waiter.done():
                waiter.set_result(Tupu)
                koma

    eleza __repr__(self):
        rudisha f'<{type(self).__name__} at {id(self):#x} {self._format()}>'

    eleza __str__(self):
        rudisha f'<{type(self).__name__} {self._format()}>'

    eleza _format(self):
        result = f'maxsize={self._maxsize!r}'
        ikiwa getattr(self, '_queue', Tupu):
            result += f' _queue={list(self._queue)!r}'
        ikiwa self._getters:
            result += f' _getters[{len(self._getters)}]'
        ikiwa self._putters:
            result += f' _putters[{len(self._putters)}]'
        ikiwa self._unfinished_tasks:
            result += f' tasks={self._unfinished_tasks}'
        rudisha result

    eleza qsize(self):
        """Number of items kwenye the queue."""
        rudisha len(self._queue)

    @property
    eleza maxsize(self):
        """Number of items allowed kwenye the queue."""
        rudisha self._maxsize

    eleza empty(self):
        """Return Kweli ikiwa the queue ni empty, Uongo otherwise."""
        rudisha sio self._queue

    eleza full(self):
        """Return Kweli ikiwa there are maxsize items kwenye the queue.

        Note: ikiwa the Queue was initialized ukijumuisha maxsize=0 (the default),
        then full() ni never Kweli.
        """
        ikiwa self._maxsize <= 0:
            rudisha Uongo
        isipokua:
            rudisha self.qsize() >= self._maxsize

    async eleza put(self, item):
        """Put an item into the queue.

        Put an item into the queue. If the queue ni full, wait until a free
        slot ni available before adding item.
        """
        wakati self.full():
            putter = self._loop.create_future()
            self._putters.append(putter)
            jaribu:
                await putter
            except:
                putter.cancel()  # Just kwenye case putter ni sio done yet.
                jaribu:
                    # Clean self._putters kutoka canceled putters.
                    self._putters.remove(putter)
                tatizo ValueError:
                    # The putter could be removed kutoka self._putters by a
                    # previous get_nowait call.
                    pita
                ikiwa sio self.full() na sio putter.cancelled():
                    # We were woken up by get_nowait(), but can't take
                    # the call.  Wake up the next kwenye line.
                    self._wakeup_next(self._putters)
                ashiria
        rudisha self.put_nowait(item)

    eleza put_nowait(self, item):
        """Put an item into the queue without blocking.

        If no free slot ni immediately available, ashiria QueueFull.
        """
        ikiwa self.full():
            ashiria QueueFull
        self._put(item)
        self._unfinished_tasks += 1
        self._finished.clear()
        self._wakeup_next(self._getters)

    async eleza get(self):
        """Remove na rudisha an item kutoka the queue.

        If queue ni empty, wait until an item ni available.
        """
        wakati self.empty():
            getter = self._loop.create_future()
            self._getters.append(getter)
            jaribu:
                await getter
            except:
                getter.cancel()  # Just kwenye case getter ni sio done yet.
                jaribu:
                    # Clean self._getters kutoka canceled getters.
                    self._getters.remove(getter)
                tatizo ValueError:
                    # The getter could be removed kutoka self._getters by a
                    # previous put_nowait call.
                    pita
                ikiwa sio self.empty() na sio getter.cancelled():
                    # We were woken up by put_nowait(), but can't take
                    # the call.  Wake up the next kwenye line.
                    self._wakeup_next(self._getters)
                ashiria
        rudisha self.get_nowait()

    eleza get_nowait(self):
        """Remove na rudisha an item kutoka the queue.

        Return an item ikiwa one ni immediately available, isipokua ashiria QueueEmpty.
        """
        ikiwa self.empty():
            ashiria QueueEmpty
        item = self._get()
        self._wakeup_next(self._putters)
        rudisha item

    eleza task_done(self):
        """Indicate that a formerly enqueued task ni complete.

        Used by queue consumers. For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task ni complete.

        If a join() ni currently blocking, it will resume when all items have
        been processed (meaning that a task_done() call was received kila every
        item that had been put() into the queue).

        Raises ValueError ikiwa called more times than there were items placed in
        the queue.
        """
        ikiwa self._unfinished_tasks <= 0:
            ashiria ValueError('task_done() called too many times')
        self._unfinished_tasks -= 1
        ikiwa self._unfinished_tasks == 0:
            self._finished.set()

    async eleza join(self):
        """Block until all items kwenye the queue have been gotten na processed.

        The count of unfinished tasks goes up whenever an item ni added to the
        queue. The count goes down whenever a consumer calls task_done() to
        indicate that the item was retrieved na all work on it ni complete.
        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        ikiwa self._unfinished_tasks > 0:
            await self._finished.wait()


kundi PriorityQueue(Queue):
    """A subkundi of Queue; retrieves entries kwenye priority order (lowest first).

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
