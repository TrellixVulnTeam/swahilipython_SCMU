'''A multi-producer, multi-consumer queue.'''

agiza threading
kutoka collections agiza deque
kutoka heapq agiza heappush, heappop
kutoka time agiza monotonic as time
try:
    kutoka _queue agiza SimpleQueue
except ImportError:
    SimpleQueue = None

__all__ = ['Empty', 'Full', 'Queue', 'PriorityQueue', 'LifoQueue', 'SimpleQueue']


try:
    kutoka _queue agiza Empty
except ImportError:
    kundi Empty(Exception):
        'Exception raised by Queue.get(block=0)/get_nowait().'
        pass

kundi Full(Exception):
    'Exception raised by Queue.put(block=0)/put_nowait().'
    pass


kundi Queue:
    '''Create a queue object with a given maximum size.

    If maxsize is <= 0, the queue size is infinite.
    '''

    eleza __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)

        # mutex must be held whenever the queue is mutating.  All methods
        # that acquire mutex must release it before returning.  mutex
        # is shared between the three conditions, so acquiring and
        # releasing the conditions also acquires and releases mutex.
        self.mutex = threading.Lock()

        # Notify not_empty whenever an item is added to the queue; a
        # thread waiting to get is notified then.
        self.not_empty = threading.Condition(self.mutex)

        # Notify not_full whenever an item is removed kutoka the queue;
        # a thread waiting to put is notified then.
        self.not_full = threading.Condition(self.mutex)

        # Notify all_tasks_done whenever the number of unfinished tasks
        # drops to zero; thread waiting to join() is notified to resume
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    eleza task_done(self):
        '''Indicate that a formerly enqueued task is complete.

        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        for every item that had been put() into the queue).

        Raises a ValueError ikiwa called more times than there were items
        placed in the queue.
        '''
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            ikiwa unfinished <= 0:
                ikiwa unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    eleza join(self):
        '''Blocks until all items in the Queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved and all work on it is complete.

        When the count of unfinished tasks drops to zero, join() unblocks.
        '''
        with self.all_tasks_done:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()

    eleza qsize(self):
        '''Return the approximate size of the queue (not reliable!).'''
        with self.mutex:
            rudisha self._qsize()

    eleza empty(self):
        '''Return True ikiwa the queue is empty, False otherwise (not reliable!).

        This method is likely to be removed at some point.  Use qsize() == 0
        as a direct substitute, but be aware that either approach risks a race
        condition where a queue can grow before the result of empty() or
        qsize() can be used.

        To create code that needs to wait for all queued tasks to be
        completed, the preferred technique is to use the join() method.
        '''
        with self.mutex:
            rudisha not self._qsize()

    eleza full(self):
        '''Return True ikiwa the queue is full, False otherwise (not reliable!).

        This method is likely to be removed at some point.  Use qsize() >= n
        as a direct substitute, but be aware that either approach risks a race
        condition where a queue can shrink before the result of full() or
        qsize() can be used.
        '''
        with self.mutex:
            rudisha 0 < self.maxsize <= self._qsize()

    eleza put(self, item, block=True, timeout=None):
        '''Put an item into the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block ikiwa necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception ikiwa no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue ikiwa a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).
        '''
        with self.not_full:
            ikiwa self.maxsize > 0:
                ikiwa not block:
                    ikiwa self._qsize() >= self.maxsize:
                        raise Full
                elikiwa timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elikiwa timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        ikiwa remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    eleza get(self, block=True, timeout=None):
        '''Remove and rudisha an item kutoka the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block ikiwa necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception ikiwa no item was available within that time.
        Otherwise ('block' is false), rudisha an item ikiwa one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        '''
        with self.not_empty:
            ikiwa not block:
                ikiwa not self._qsize():
                    raise Empty
            elikiwa timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elikiwa timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    ikiwa remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            rudisha item

    eleza put_nowait(self, item):
        '''Put an item into the queue without blocking.

        Only enqueue the item ikiwa a free slot is immediately available.
        Otherwise raise the Full exception.
        '''
        rudisha self.put(item, block=False)

    eleza get_nowait(self):
        '''Remove and rudisha an item kutoka the queue without blocking.

        Only get an item ikiwa one is immediately available. Otherwise
        raise the Empty exception.
        '''
        rudisha self.get(block=False)

    # Override these methods to implement other queue organizations
    # (e.g. stack or priority queue).
    # These will only be called with appropriate locks held

    # Initialize the queue representation
    eleza _init(self, maxsize):
        self.queue = deque()

    eleza _qsize(self):
        rudisha len(self.queue)

    # Put a new item in the queue
    eleza _put(self, item):
        self.queue.append(item)

    # Get an item kutoka the queue
    eleza _get(self):
        rudisha self.queue.popleft()


kundi PriorityQueue(Queue):
    '''Variant of Queue that retrieves open entries in priority order (lowest first).

    Entries are typically tuples of the form:  (priority number, data).
    '''

    eleza _init(self, maxsize):
        self.queue = []

    eleza _qsize(self):
        rudisha len(self.queue)

    eleza _put(self, item):
        heappush(self.queue, item)

    eleza _get(self):
        rudisha heappop(self.queue)


kundi LifoQueue(Queue):
    '''Variant of Queue that retrieves most recently added entries first.'''

    eleza _init(self, maxsize):
        self.queue = []

    eleza _qsize(self):
        rudisha len(self.queue)

    eleza _put(self, item):
        self.queue.append(item)

    eleza _get(self):
        rudisha self.queue.pop()


kundi _PySimpleQueue:
    '''Simple, unbounded FIFO queue.

    This pure Python implementation is not reentrant.
    '''
    # Note: while this pure Python version provides fairness
    # (by using a threading.Semaphore which is itself fair, being based
    #  on threading.Condition), fairness is not part of the API contract.
    # This allows the C version to use a different implementation.

    eleza __init__(self):
        self._queue = deque()
        self._count = threading.Semaphore(0)

    eleza put(self, item, block=True, timeout=None):
        '''Put the item on the queue.

        The optional 'block' and 'timeout' arguments are ignored, as this method
        never blocks.  They are provided for compatibility with the Queue class.
        '''
        self._queue.append(item)
        self._count.release()

    eleza get(self, block=True, timeout=None):
        '''Remove and rudisha an item kutoka the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block ikiwa necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception ikiwa no item was available within that time.
        Otherwise ('block' is false), rudisha an item ikiwa one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        '''
        ikiwa timeout is not None and timeout < 0:
            raise ValueError("'timeout' must be a non-negative number")
        ikiwa not self._count.acquire(block, timeout):
            raise Empty
        rudisha self._queue.popleft()

    eleza put_nowait(self, item):
        '''Put an item into the queue without blocking.

        This is exactly equivalent to `put(item)` and is only provided
        for compatibility with the Queue class.
        '''
        rudisha self.put(item, block=False)

    eleza get_nowait(self):
        '''Remove and rudisha an item kutoka the queue without blocking.

        Only get an item ikiwa one is immediately available. Otherwise
        raise the Empty exception.
        '''
        rudisha self.get(block=False)

    eleza empty(self):
        '''Return True ikiwa the queue is empty, False otherwise (not reliable!).'''
        rudisha len(self._queue) == 0

    eleza qsize(self):
        '''Return the approximate size of the queue (not reliable!).'''
        rudisha len(self._queue)


ikiwa SimpleQueue is None:
    SimpleQueue = _PySimpleQueue
