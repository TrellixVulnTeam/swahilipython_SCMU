# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ThreadPoolExecutor."""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

agiza atexit
kutoka concurrent.futures agiza _base
agiza itertools
agiza queue
agiza threading
agiza weakref
agiza os

# Workers are created as daemon threads. This is done to allow the interpreter
# to exit when there are still idle threads in a ThreadPoolExecutor's thread
# pool (i.e. shutdown() was not called). However, allowing workers to die with
# the interpreter has two undesirable properties:
#   - The workers would still be running during interpreter shutdown,
#     meaning that they would fail in unpredictable ways.
#   - The workers could be killed while evaluating a work item, which could
#     be bad ikiwa the callable being evaluated has external side-effects e.g.
#     writing to a file.
#
# To work around this problem, an exit handler is installed which tells the
# workers to exit when their work queues are empty and then waits until the
# threads finish.

_threads_queues = weakref.WeakKeyDictionary()
_shutdown = False

eleza _python_exit():
    global _shutdown
    _shutdown = True
    items = list(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()

atexit.register(_python_exit)


kundi _WorkItem(object):
    eleza __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    eleza run(self):
        ikiwa not self.future.set_running_or_notify_cancel():
            return

        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException as exc:
            self.future.set_exception(exc)
            # Break a reference cycle with the exception 'exc'
            self = None
        else:
            self.future.set_result(result)


eleza _worker(executor_reference, work_queue, initializer, initargs):
    ikiwa initializer is not None:
        try:
            initializer(*initargs)
        except BaseException:
            _base.LOGGER.critical('Exception in initializer:', exc_info=True)
            executor = executor_reference()
            ikiwa executor is not None:
                executor._initializer_failed()
            return
    try:
        while True:
            work_item = work_queue.get(block=True)
            ikiwa work_item is not None:
                work_item.run()
                # Delete references to object. See issue16284
                del work_item

                # attempt to increment idle count
                executor = executor_reference()
                ikiwa executor is not None:
                    executor._idle_semaphore.release()
                del executor
                continue

            executor = executor_reference()
            # Exit if:
            #   - The interpreter is shutting down OR
            #   - The executor that owns the worker has been collected OR
            #   - The executor that owns the worker has been shutdown.
            ikiwa _shutdown or executor is None or executor._shutdown:
                # Flag the executor as shutting down as early as possible ikiwa it
                # is not gc-ed yet.
                ikiwa executor is not None:
                    executor._shutdown = True
                # Notice other workers
                work_queue.put(None)
                return
            del executor
    except BaseException:
        _base.LOGGER.critical('Exception in worker', exc_info=True)


kundi BrokenThreadPool(_base.BrokenExecutor):
    """
    Raised when a worker thread in a ThreadPoolExecutor failed initializing.
    """


kundi ThreadPoolExecutor(_base.Executor):

    # Used to assign unique thread names when thread_name_prefix is not supplied.
    _counter = itertools.count().__next__

    eleza __init__(self, max_workers=None, thread_name_prefix='',
                 initializer=None, initargs=()):
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
            thread_name_prefix: An optional name prefix to give our threads.
            initializer: A callable used to initialize worker threads.
            initargs: A tuple of arguments to pass to the initializer.
        """
        ikiwa max_workers is None:
            # ThreadPoolExecutor is often used to:
            # * CPU bound task which releases GIL
            # * I/O bound task (which releases GIL, of course)
            #
            # We use cpu_count + 4 for both types of tasks.
            # But we limit it to 32 to avoid consuming surprisingly large resource
            # on many core machine.
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        ikiwa max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")

        ikiwa initializer is not None and not callable(initializer):
            raise TypeError("initializer must be a callable")

        self._max_workers = max_workers
        self._work_queue = queue.SimpleQueue()
        self._idle_semaphore = threading.Semaphore(0)
        self._threads = set()
        self._broken = False
        self._shutdown = False
        self._shutdown_lock = threading.Lock()
        self._thread_name_prefix = (thread_name_prefix or
                                    ("ThreadPoolExecutor-%d" % self._counter()))
        self._initializer = initializer
        self._initargs = initargs

    eleza submit(*args, **kwargs):
        ikiwa len(args) >= 2:
            self, fn, *args = args
        elikiwa not args:
            raise TypeError("descriptor 'submit' of 'ThreadPoolExecutor' object "
                            "needs an argument")
        elikiwa 'fn' in kwargs:
            fn = kwargs.pop('fn')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'fn' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            raise TypeError('submit expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        with self._shutdown_lock:
            ikiwa self._broken:
                raise BrokenThreadPool(self._broken)

            ikiwa self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')
            ikiwa _shutdown:
                raise RuntimeError('cannot schedule new futures after '
                                   'interpreter shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._work_queue.put(w)
            self._adjust_thread_count()
            rudisha f
    submit.__text_signature__ = _base.Executor.submit.__text_signature__
    submit.__doc__ = _base.Executor.submit.__doc__

    eleza _adjust_thread_count(self):
        # ikiwa idle threads are available, don't spin new threads
        ikiwa self._idle_semaphore.acquire(timeout=0):
            return

        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        eleza weakref_cb(_, q=self._work_queue):
            q.put(None)

        num_threads = len(self._threads)
        ikiwa num_threads < self._max_workers:
            thread_name = '%s_%d' % (self._thread_name_prefix or self,
                                     num_threads)
            t = threading.Thread(name=thread_name, target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue,
                                       self._initializer,
                                       self._initargs))
            t.daemon = True
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue

    eleza _initializer_failed(self):
        with self._shutdown_lock:
            self._broken = ('A thread initializer failed, the thread pool '
                            'is not usable anymore')
            # Drain work queue and mark pending futures failed
            while True:
                try:
                    work_item = self._work_queue.get_nowait()
                except queue.Empty:
                    break
                ikiwa work_item is not None:
                    work_item.future.set_exception(BrokenThreadPool(self._broken))

    eleza shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown = True
            self._work_queue.put(None)
        ikiwa wait:
            for t in self._threads:
                t.join()
    shutdown.__doc__ = _base.Executor.shutdown.__doc__
