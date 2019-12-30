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

# Workers are created kama daemon threads. This ni done to allow the interpreter
# to exit when there are still idle threads kwenye a ThreadPoolExecutor's thread
# pool (i.e. shutdown() was sio called). However, allowing workers to die with
# the interpreter has two undesirable properties:
#   - The workers would still be running during interpreter shutdown,
#     meaning that they would fail kwenye unpredictable ways.
#   - The workers could be killed wakati evaluating a work item, which could
#     be bad ikiwa the callable being evaluated has external side-effects e.g.
#     writing to a file.
#
# To work around this problem, an exit handler ni installed which tells the
# workers to exit when their work queues are empty na then waits until the
# threads finish.

_threads_queues = weakref.WeakKeyDictionary()
_shutdown = Uongo

eleza _python_exit():
    global _shutdown
    _shutdown = Kweli
    items = list(_threads_queues.items())
    kila t, q kwenye items:
        q.put(Tupu)
    kila t, q kwenye items:
        t.join()

atexit.register(_python_exit)


kundi _WorkItem(object):
    eleza __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    eleza run(self):
        ikiwa sio self.future.set_running_or_notify_cancel():
            rudisha

        jaribu:
            result = self.fn(*self.args, **self.kwargs)
        tatizo BaseException kama exc:
            self.future.set_exception(exc)
            # Break a reference cycle ukijumuisha the exception 'exc'
            self = Tupu
        isipokua:
            self.future.set_result(result)


eleza _worker(executor_reference, work_queue, initializer, initargs):
    ikiwa initializer ni sio Tupu:
        jaribu:
            initializer(*initargs)
        tatizo BaseException:
            _base.LOGGER.critical('Exception kwenye initializer:', exc_info=Kweli)
            executor = executor_reference()
            ikiwa executor ni sio Tupu:
                executor._initializer_failed()
            rudisha
    jaribu:
        wakati Kweli:
            work_item = work_queue.get(block=Kweli)
            ikiwa work_item ni sio Tupu:
                work_item.run()
                # Delete references to object. See issue16284
                toa work_item

                # attempt to increment idle count
                executor = executor_reference()
                ikiwa executor ni sio Tupu:
                    executor._idle_semaphore.release()
                toa executor
                endelea

            executor = executor_reference()
            # Exit if:
            #   - The interpreter ni shutting down OR
            #   - The executor that owns the worker has been collected OR
            #   - The executor that owns the worker has been shutdown.
            ikiwa _shutdown ama executor ni Tupu ama executor._shutdown:
                # Flag the executor kama shutting down kama early kama possible ikiwa it
                # ni sio gc-ed yet.
                ikiwa executor ni sio Tupu:
                    executor._shutdown = Kweli
                # Notice other workers
                work_queue.put(Tupu)
                rudisha
            toa executor
    tatizo BaseException:
        _base.LOGGER.critical('Exception kwenye worker', exc_info=Kweli)


kundi BrokenThreadPool(_base.BrokenExecutor):
    """
    Raised when a worker thread kwenye a ThreadPoolExecutor failed initializing.
    """


kundi ThreadPoolExecutor(_base.Executor):

    # Used to assign unique thread names when thread_name_prefix ni sio supplied.
    _counter = itertools.count().__next__

    eleza __init__(self, max_workers=Tupu, thread_name_prefix='',
                 initializer=Tupu, initargs=()):
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
            thread_name_prefix: An optional name prefix to give our threads.
            initializer: A callable used to initialize worker threads.
            initargs: A tuple of arguments to pita to the initializer.
        """
        ikiwa max_workers ni Tupu:
            # ThreadPoolExecutor ni often used to:
            # * CPU bound task which releases GIL
            # * I/O bound task (which releases GIL, of course)
            #
            # We use cpu_count + 4 kila both types of tasks.
            # But we limit it to 32 to avoid consuming surprisingly large resource
            # on many core machine.
            max_workers = min(32, (os.cpu_count() ama 1) + 4)
        ikiwa max_workers <= 0:
            ashiria ValueError("max_workers must be greater than 0")

        ikiwa initializer ni sio Tupu na sio callable(initializer):
            ashiria TypeError("initializer must be a callable")

        self._max_workers = max_workers
        self._work_queue = queue.SimpleQueue()
        self._idle_semaphore = threading.Semaphore(0)
        self._threads = set()
        self._broken = Uongo
        self._shutdown = Uongo
        self._shutdown_lock = threading.Lock()
        self._thread_name_prefix = (thread_name_prefix ama
                                    ("ThreadPoolExecutor-%d" % self._counter()))
        self._initializer = initializer
        self._initargs = initargs

    eleza submit(*args, **kwargs):
        ikiwa len(args) >= 2:
            self, fn, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor 'submit' of 'ThreadPoolExecutor' object "
                            "needs an argument")
        lasivyo 'fn' kwenye kwargs:
            fn = kwargs.pop('fn')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'fn' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError('submit expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        ukijumuisha self._shutdown_lock:
            ikiwa self._broken:
                ashiria BrokenThreadPool(self._broken)

            ikiwa self._shutdown:
                ashiria RuntimeError('cannot schedule new futures after shutdown')
            ikiwa _shutdown:
                ashiria RuntimeError('cannot schedule new futures after '
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
            rudisha

        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        eleza weakref_cb(_, q=self._work_queue):
            q.put(Tupu)

        num_threads = len(self._threads)
        ikiwa num_threads < self._max_workers:
            thread_name = '%s_%d' % (self._thread_name_prefix ama self,
                                     num_threads)
            t = threading.Thread(name=thread_name, target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue,
                                       self._initializer,
                                       self._initargs))
            t.daemon = Kweli
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue

    eleza _initializer_failed(self):
        ukijumuisha self._shutdown_lock:
            self._broken = ('A thread initializer failed, the thread pool '
                            'is sio usable anymore')
            # Drain work queue na mark pending futures failed
            wakati Kweli:
                jaribu:
                    work_item = self._work_queue.get_nowait()
                tatizo queue.Empty:
                    koma
                ikiwa work_item ni sio Tupu:
                    work_item.future.set_exception(BrokenThreadPool(self._broken))

    eleza shutdown(self, wait=Kweli):
        ukijumuisha self._shutdown_lock:
            self._shutdown = Kweli
            self._work_queue.put(Tupu)
        ikiwa wait:
            kila t kwenye self._threads:
                t.join()
    shutdown.__doc__ = _base.Executor.shutdown.__doc__
