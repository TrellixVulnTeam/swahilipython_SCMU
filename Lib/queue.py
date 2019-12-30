'''A multi-producer, multi-consumer queue.'''

agiza threading
kutoka collections agiza deque
kutoka heapq agiza heappush, heappop
kutoka time agiza monotonic kama time
jaribu:
    kutoka _queue agiza SimpleQueue
tatizo ImportError:
    SimpleQueue = Tupu

__all__ = ['Empty', 'Full', 'Queue', 'PriorityQueue', 'LifoQueue', 'SimpleQueue']


jaribu:
    kutoka _queue agiza Empty
tatizo ImportError:
    kundi Empty(Exception):
        'Exception ashiriad by Queue.get(block=0)/get_nowait().'
        pita

kundi Full(Exception):
    'Exception ashiriad by Queue.put(block=0)/put_nowait().'
    pita


kundi Queue:
    '''Create a queue object ukijumuisha a given maximum size.

    If maxsize ni <= 0, the queue size ni infinite.
    '''

    eleza __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)

        # mutex must be held whenever the queue ni mutating.  All methods
        # that acquire mutex must release it before rudishaing.  mutex
        # ni shared between the three conditions, so acquiring na
        # releasing the conditions also acquires na releases mutex.
        self.mutex = threading.Lock()

        # Notify not_empty whenever an item ni added to the queue; a
        # thread waiting to get ni notified then.
        self.not_empty = threading.Condition(self.mutex)

        # Notify not_full whenever an item ni removed kutoka the queue;
        # a thread waiting to put ni notified then.
        self.not_full = threading.Condition(self.mutex)

        # Notify all_tasks_done whenever the number of unfinished tasks
        # drops to zero; thread waiting to join() ni notified to resume
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    eleza task_done(self):
        '''Indicate that a formerly enqueued task ni complete.

        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task ni complete.

        If a join() ni currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        kila every item that had been put() into the queue).

        Raises a ValueError ikiwa called more times than there were items
        placed kwenye the queue.
        '''
        ukijumuisha self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            ikiwa unfinished <= 0:
                ikiwa unfinished < 0:
                    ashiria ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    eleza join(self):
        '''Blocks until all items kwenye the Queue have been gotten na processed.

        The count of unfinished tasks goes up whenever an item ni added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved na all work on it ni complete.

        When the count of unfinished tasks drops to zero, join() unblocks.
        '''
        ukijumuisha self.all_tasks_done:
            wakati self.unfinished_tasks:
                self.all_tasks_done.wait()

    eleza qsize(self):
        '''Return the approximate size of the queue (sio reliable!).'''
        ukijumuisha self.mutex:
            rudisha self._qsize()

    eleza empty(self):
        '''Return Kweli ikiwa the queue ni empty, Uongo otherwise (sio reliable!).

        This method ni likely to be removed at some point.  Use qsize() == 0
        kama a direct substitute, but be aware that either approach risks a race
        condition where a queue can grow before the result of empty() ama
        qsize() can be used.

        To create code that needs to wait kila all queued tasks to be
        completed, the preferred technique ni to use the join() method.
        '''
        ukijumuisha self.mutex:
            rudisha sio self._qsize()

    eleza full(self):
        '''Return Kweli ikiwa the queue ni full, Uongo otherwise (sio reliable!).

        This method ni likely to be removed at some point.  Use qsize() >= n
        kama a direct substitute, but be aware that either approach risks a race
        condition where a queue can shrink before the result of full() ama
        qsize() can be used.
        '''
        ukijumuisha self.mutex:
            rudisha 0 < self.maxsize <= self._qsize()

    eleza put(self, item, block=Kweli, timeout=Tupu):
        '''Put an item into the queue.

        If optional args 'block' ni true na 'timeout' ni Tupu (the default),
        block ikiwa necessary until a free slot ni available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds na ashirias
        the Full exception ikiwa no free slot was available within that time.
        Otherwise ('block' ni false), put an item on the queue ikiwa a free slot
        ni immediately available, isipokua ashiria the Full exception ('timeout'
        ni ignored kwenye that case).
        '''
        ukijumuisha self.not_full:
            ikiwa self.maxsize > 0:
                ikiwa sio block:
                    ikiwa self._qsize() >= self.maxsize:
                        ashiria Full
                lasivyo timeout ni Tupu:
                    wakati self._qsize() >= self.maxsize:
                        self.not_full.wait()
                lasivyo timeout < 0:
                    ashiria ValueError("'timeout' must be a non-negative number")
                isipokua:
                    endtime = time() + timeout
                    wakati self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        ikiwa remaining <= 0.0:
                            ashiria Full
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    eleza get(self, block=Kweli, timeout=Tupu):
        '''Remove na rudisha an item kutoka the queue.

        If optional args 'block' ni true na 'timeout' ni Tupu (the default),
        block ikiwa necessary until an item ni available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds na ashirias
        the Empty exception ikiwa no item was available within that time.
        Otherwise ('block' ni false), rudisha an item ikiwa one ni immediately
        available, isipokua ashiria the Empty exception ('timeout' ni ignored
        kwenye that case).
        '''
        ukijumuisha self.not_empty:
            ikiwa sio block:
                ikiwa sio self._qsize():
                    ashiria Empty
            lasivyo timeout ni Tupu:
                wakati sio self._qsize():
                    self.not_empty.wait()
            lasivyo timeout < 0:
                ashiria ValueError("'timeout' must be a non-negative number")
            isipokua:
                endtime = time() + timeout
                wakati sio self._qsize():
                    remaining = endtime - time()
                    ikiwa remaining <= 0.0:
                        ashiria Empty
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            rudisha item

    eleza put_nowait(self, item):
        '''Put an item into the queue without blocking.

        Only enqueue the item ikiwa a free slot ni immediately available.
        Otherwise ashiria the Full exception.
        '''
        rudisha self.put(item, block=Uongo)

    eleza get_nowait(self):
        '''Remove na rudisha an item kutoka the queue without blocking.

        Only get an item ikiwa one ni immediately available. Otherwise
        ashiria the Empty exception.
        '''
        rudisha self.get(block=Uongo)

    # Override these methods to implement other queue organizations
    # (e.g. stack ama priority queue).
    # These will only be called ukijumuisha appropriate locks held

    # Initialize the queue representation
    eleza _init(self, maxsize):
        self.queue = deque()

    eleza _qsize(self):
        rudisha len(self.queue)

    # Put a new item kwenye the queue
    eleza _put(self, item):
        self.queue.append(item)

    # Get an item kutoka the queue
    eleza _get(self):
        rudisha self.queue.popleft()


kundi PriorityQueue(Queue):
    '''Variant of Queue that retrieves open entries kwenye priority order (lowest first).

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

    This pure Python implementation ni sio reentrant.
    '''
    # Note: wakati this pure Python version provides fairness
    # (by using a threading.Semaphore which ni itself fair, being based
    #  on threading.Condition), fairness ni sio part of the API contract.
    # This allows the C version to use a different implementation.

    eleza __init__(self):
        self._queue = deque()
        self._count = threading.Semaphore(0)

    eleza put(self, item, block=Kweli, timeout=Tupu):
        '''Put the item on the queue.

        The optional 'block' na 'timeout' arguments are ignored, kama this method
        never blocks.  They are provided kila compatibility ukijumuisha the Queue class.
        '''
        self._queue.append(item)
        self._count.release()

    eleza get(self, block=Kweli, timeout=Tupu):
        '''Remove na rudisha an item kutoka the queue.

        If optional args 'block' ni true na 'timeout' ni Tupu (the default),
        block ikiwa necessary until an item ni available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds na ashirias
        the Empty exception ikiwa no item was available within that time.
        Otherwise ('block' ni false), rudisha an item ikiwa one ni immediately
        available, isipokua ashiria the Empty exception ('timeout' ni ignored
        kwenye that case).
        '''
        ikiwa timeout ni sio Tupu na timeout < 0:
            ashiria ValueError("'timeout' must be a non-negative number")
        ikiwa sio self._count.acquire(block, timeout):
            ashiria Empty
        rudisha self._queue.popleft()

    eleza put_nowait(self, item):
        '''Put an item into the queue without blocking.

        This ni exactly equivalent to `put(item)` na ni only provided
        kila compatibility ukijumuisha the Queue class.
        '''
        rudisha self.put(item, block=Uongo)

    eleza get_nowait(self):
        '''Remove na rudisha an item kutoka the queue without blocking.

        Only get an item ikiwa one ni immediately available. Otherwise
        ashiria the Empty exception.
        '''
        rudisha self.get(block=Uongo)

    eleza empty(self):
        '''Return Kweli ikiwa the queue ni empty, Uongo otherwise (sio reliable!).'''
        rudisha len(self._queue) == 0

    eleza qsize(self):
        '''Return the approximate size of the queue (sio reliable!).'''
        rudisha len(self._queue)


ikiwa SimpleQueue ni Tupu:
    SimpleQueue = _PySimpleQueue
