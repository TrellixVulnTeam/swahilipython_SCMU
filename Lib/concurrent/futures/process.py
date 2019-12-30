# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ProcessPoolExecutor.

The following diagram na text describe the data-flow through the system:

|======================= In-process =====================|== Out-of-process ==|

+----------+     +----------+       +--------+     +-----------+    +---------+
|          |  => | Work Ids |       |        |     | Call Q    |    | Process |
|          |     +----------+       |        |     +-----------+    |  Pool   |
|          |     | ...      |       |        |     | ...       |    +---------+
|          |     | 6        |    => |        |  => | 5, call() | => |         |
|          |     | 7        |       |        |     | ...       |    |         |
| Process  |     | ...      |       | Local  |     +-----------+    | Process |
|  Pool    |     +----------+       | Worker |                      |  #1..n  |
| Executor |                        | Thread |                      |         |
|          |     +----------- +     |        |     +-----------+    |         |
|          | <=> | Work Items | <=> |        | <=  | Result Q  | <= |         |
|          |     +------------+     |        |     +-----------+    |         |
|          |     | 6: call()  |     |        |     | ...       |    |         |
|          |     |    future  |     |        |     | 4, result |    |         |
|          |     | ...        |     |        |     | 3, tatizo |    |         |
+----------+     +------------+     +--------+     +-----------+    +---------+

Executor.submit() called:
- creates a uniquely numbered _WorkItem na adds it to the "Work Items" dict
- adds the id of the _WorkItem to the "Work Ids" queue

Local worker thread:
- reads work ids kutoka the "Work Ids" queue na looks up the corresponding
  WorkItem kutoka the "Work Items" dict: ikiwa the work item has been cancelled then
  it ni simply removed kutoka the dict, otherwise it ni repackaged kama a
  _CallItem na put kwenye the "Call Q". New _CallItems are put kwenye the "Call Q"
  until "Call Q" ni full. NOTE: the size of the "Call Q" ni kept small because
  calls placed kwenye the "Call Q" can no longer be cancelled ukijumuisha Future.cancel().
- reads _ResultItems kutoka "Result Q", updates the future stored kwenye the
  "Work Items" dict na deletes the dict entry

Process #1..n:
- reads _CallItems kutoka "Call Q", executes the calls, na puts the resulting
  _ResultItems kwenye "Result Q"
"""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

agiza atexit
agiza os
kutoka concurrent.futures agiza _base
agiza queue
kutoka queue agiza Full
agiza multiprocessing kama mp
agiza multiprocessing.connection
kutoka multiprocessing.queues agiza Queue
agiza threading
agiza weakref
kutoka functools agiza partial
agiza itertools
agiza sys
agiza traceback

# Workers are created kama daemon threads na processes. This ni done to allow the
# interpreter to exit when there are still idle processes kwenye a
# ProcessPoolExecutor's process pool (i.e. shutdown() was sio called). However,
# allowing workers to die ukijumuisha the interpreter has two undesirable properties:
#   - The workers would still be running during interpreter shutdown,
#     meaning that they would fail kwenye unpredictable ways.
#   - The workers could be killed wakati evaluating a work item, which could
#     be bad ikiwa the callable being evaluated has external side-effects e.g.
#     writing to a file.
#
# To work around this problem, an exit handler ni installed which tells the
# workers to exit when their work queues are empty na then waits until the
# threads/processes finish.

_threads_wakeups = weakref.WeakKeyDictionary()
_global_shutdown = Uongo


kundi _ThreadWakeup:
    eleza __init__(self):
        self._reader, self._writer = mp.Pipe(duplex=Uongo)

    eleza close(self):
        self._writer.close()
        self._reader.close()

    eleza wakeup(self):
        self._writer.send_bytes(b"")

    eleza clear(self):
        wakati self._reader.poll():
            self._reader.recv_bytes()


eleza _python_exit():
    global _global_shutdown
    _global_shutdown = Kweli
    items = list(_threads_wakeups.items())
    kila _, thread_wakeup kwenye items:
        thread_wakeup.wakeup()
    kila t, _ kwenye items:
        t.join()

# Controls how many more calls than processes will be queued kwenye the call queue.
# A smaller number will mean that processes spend more time idle waiting for
# work wakati a larger number will make Future.cancel() succeed less frequently
# (Futures kwenye the call queue cannot be cancelled).
EXTRA_QUEUED_CALLS = 1


# On Windows, WaitForMultipleObjects ni used to wait kila processes to finish.
# It can wait on, at most, 63 objects. There ni an overhead of two objects:
# - the result queue reader
# - the thread wakeup reader
_MAX_WINDOWS_WORKERS = 63 - 2

# Hack to embed stringification of remote traceback kwenye local traceback

kundi _RemoteTraceback(Exception):
    eleza __init__(self, tb):
        self.tb = tb
    eleza __str__(self):
        rudisha self.tb

kundi _ExceptionWithTraceback:
    eleza __init__(self, exc, tb):
        tb = traceback.format_exception(type(exc), exc, tb)
        tb = ''.join(tb)
        self.exc = exc
        self.tb = '\n"""\n%s"""' % tb
    eleza __reduce__(self):
        rudisha _rebuild_exc, (self.exc, self.tb)

eleza _rebuild_exc(exc, tb):
    exc.__cause__ = _RemoteTraceback(tb)
    rudisha exc

kundi _WorkItem(object):
    eleza __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

kundi _ResultItem(object):
    eleza __init__(self, work_id, exception=Tupu, result=Tupu):
        self.work_id = work_id
        self.exception = exception
        self.result = result

kundi _CallItem(object):
    eleza __init__(self, work_id, fn, args, kwargs):
        self.work_id = work_id
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


kundi _SafeQueue(Queue):
    """Safe Queue set exception to the future object linked to a job"""
    eleza __init__(self, max_size=0, *, ctx, pending_work_items):
        self.pending_work_items = pending_work_items
        super().__init__(max_size, ctx=ctx)

    eleza _on_queue_feeder_error(self, e, obj):
        ikiwa isinstance(obj, _CallItem):
            tb = traceback.format_exception(type(e), e, e.__traceback__)
            e.__cause__ = _RemoteTraceback('\n"""\n{}"""'.format(''.join(tb)))
            work_item = self.pending_work_items.pop(obj.work_id, Tupu)
            # work_item can be Tupu ikiwa another process terminated. In this case,
            # the queue_manager_thread fails all work_items ukijumuisha BrokenProcessPool
            ikiwa work_item ni sio Tupu:
                work_item.future.set_exception(e)
        isipokua:
            super()._on_queue_feeder_error(e, obj)


eleza _get_chunks(*iterables, chunksize):
    """ Iterates over zip()ed iterables kwenye chunks. """
    it = zip(*iterables)
    wakati Kweli:
        chunk = tuple(itertools.islice(it, chunksize))
        ikiwa sio chunk:
            return
        tuma chunk

eleza _process_chunk(fn, chunk):
    """ Processes a chunk of an iterable pitaed to map.

    Runs the function pitaed to map() on a chunk of the
    iterable pitaed to map.

    This function ni run kwenye a separate process.

    """
    rudisha [fn(*args) kila args kwenye chunk]


eleza _sendback_result(result_queue, work_id, result=Tupu, exception=Tupu):
    """Safely send back the given result ama exception"""
    jaribu:
        result_queue.put(_ResultItem(work_id, result=result,
                                     exception=exception))
    tatizo BaseException kama e:
        exc = _ExceptionWithTraceback(e, e.__traceback__)
        result_queue.put(_ResultItem(work_id, exception=exc))


eleza _process_worker(call_queue, result_queue, initializer, initargs):
    """Evaluates calls kutoka call_queue na places the results kwenye result_queue.

    This worker ni run kwenye a separate process.

    Args:
        call_queue: A ctx.Queue of _CallItems that will be read na
            evaluated by the worker.
        result_queue: A ctx.Queue of _ResultItems that will written
            to by the worker.
        initializer: A callable initializer, ama Tupu
        initargs: A tuple of args kila the initializer
    """
    ikiwa initializer ni sio Tupu:
        jaribu:
            initializer(*initargs)
        tatizo BaseException:
            _base.LOGGER.critical('Exception kwenye initializer:', exc_info=Kweli)
            # The parent will notice that the process stopped na
            # mark the pool broken
            return
    wakati Kweli:
        call_item = call_queue.get(block=Kweli)
        ikiwa call_item ni Tupu:
            # Wake up queue management thread
            result_queue.put(os.getpid())
            return
        jaribu:
            r = call_item.fn(*call_item.args, **call_item.kwargs)
        tatizo BaseException kama e:
            exc = _ExceptionWithTraceback(e, e.__traceback__)
            _sendback_result(result_queue, call_item.work_id, exception=exc)
        isipokua:
            _sendback_result(result_queue, call_item.work_id, result=r)
            toa r

        # Liberate the resource kama soon kama possible, to avoid holding onto
        # open files ama shared memory that ni sio needed anymore
        toa call_item


eleza _add_call_item_to_queue(pending_work_items,
                            work_ids,
                            call_queue):
    """Fills call_queue ukijumuisha _WorkItems kutoka pending_work_items.

    This function never blocks.

    Args:
        pending_work_items: A dict mapping work ids to _WorkItems e.g.
            {5: <_WorkItem...>, 6: <_WorkItem...>, ...}
        work_ids: A queue.Queue of work ids e.g. Queue([5, 6, ...]). Work ids
            are consumed na the corresponding _WorkItems from
            pending_work_items are transformed into _CallItems na put in
            call_queue.
        call_queue: A multiprocessing.Queue that will be filled ukijumuisha _CallItems
            derived kutoka _WorkItems.
    """
    wakati Kweli:
        ikiwa call_queue.full():
            return
        jaribu:
            work_id = work_ids.get(block=Uongo)
        tatizo queue.Empty:
            return
        isipokua:
            work_item = pending_work_items[work_id]

            ikiwa work_item.future.set_running_or_notify_cancel():
                call_queue.put(_CallItem(work_id,
                                         work_item.fn,
                                         work_item.args,
                                         work_item.kwargs),
                               block=Kweli)
            isipokua:
                toa pending_work_items[work_id]
                endelea


eleza _queue_management_worker(executor_reference,
                             processes,
                             pending_work_items,
                             work_ids_queue,
                             call_queue,
                             result_queue,
                             thread_wakeup):
    """Manages the communication between this process na the worker processes.

    This function ni run kwenye a local thread.

    Args:
        executor_reference: A weakref.ref to the ProcessPoolExecutor that owns
            this thread. Used to determine ikiwa the ProcessPoolExecutor has been
            garbage collected na that this function can exit.
        process: A list of the ctx.Process instances used as
            workers.
        pending_work_items: A dict mapping work ids to _WorkItems e.g.
            {5: <_WorkItem...>, 6: <_WorkItem...>, ...}
        work_ids_queue: A queue.Queue of work ids e.g. Queue([5, 6, ...]).
        call_queue: A ctx.Queue that will be filled ukijumuisha _CallItems
            derived kutoka _WorkItems kila processing by the process workers.
        result_queue: A ctx.SimpleQueue of _ResultItems generated by the
            process workers.
        thread_wakeup: A _ThreadWakeup to allow waking up the
            queue_manager_thread kutoka the main Thread na avoid deadlocks
            caused by permanently locked queues.
    """
    executor = Tupu

    eleza shutting_down():
        rudisha (_global_shutdown ama executor ni Tupu
                ama executor._shutdown_thread)

    eleza shutdown_worker():
        # This ni an upper bound on the number of children alive.
        n_children_alive = sum(p.is_alive() kila p kwenye processes.values())
        n_children_to_stop = n_children_alive
        n_sentinels_sent = 0
        # Send the right number of sentinels, to make sure all children are
        # properly terminated.
        wakati n_sentinels_sent < n_children_to_stop na n_children_alive > 0:
            kila i kwenye range(n_children_to_stop - n_sentinels_sent):
                jaribu:
                    call_queue.put_nowait(Tupu)
                    n_sentinels_sent += 1
                tatizo Full:
                    koma
            n_children_alive = sum(p.is_alive() kila p kwenye processes.values())

        # Release the queue's resources kama soon kama possible.
        call_queue.close()
        # If .join() ni sio called on the created processes then
        # some ctx.Queue methods may deadlock on Mac OS X.
        kila p kwenye processes.values():
            p.join()

    result_reader = result_queue._reader
    wakeup_reader = thread_wakeup._reader
    readers = [result_reader, wakeup_reader]

    wakati Kweli:
        _add_call_item_to_queue(pending_work_items,
                                work_ids_queue,
                                call_queue)

        # Wait kila a result to be ready kwenye the result_queue wakati checking
        # that all worker processes are still running, ama kila a wake up
        # signal send. The wake up signals come either kutoka new tasks being
        # submitted, kutoka the executor being shutdown/gc-ed, ama kutoka the
        # shutdown of the python interpreter.
        worker_sentinels = [p.sentinel kila p kwenye processes.values()]
        ready = mp.connection.wait(readers + worker_sentinels)

        cause = Tupu
        is_broken = Kweli
        ikiwa result_reader kwenye ready:
            jaribu:
                result_item = result_reader.recv()
                is_broken = Uongo
            tatizo BaseException kama e:
                cause = traceback.format_exception(type(e), e, e.__traceback__)

        lasivyo wakeup_reader kwenye ready:
            is_broken = Uongo
            result_item = Tupu
        thread_wakeup.clear()
        ikiwa is_broken:
            # Mark the process pool broken so that submits fail right now.
            executor = executor_reference()
            ikiwa executor ni sio Tupu:
                executor._broken = ('A child process terminated '
                                    'abruptly, the process pool ni sio '
                                    'usable anymore')
                executor._shutdown_thread = Kweli
                executor = Tupu
            bpe = BrokenProcessPool("A process kwenye the process pool was "
                                    "terminated abruptly wakati the future was "
                                    "running ama pending.")
            ikiwa cause ni sio Tupu:
                bpe.__cause__ = _RemoteTraceback(
                    f"\n'''\n{''.join(cause)}'''")
            # All futures kwenye flight must be marked failed
            kila work_id, work_item kwenye pending_work_items.items():
                work_item.future.set_exception(bpe)
                # Delete references to object. See issue16284
                toa work_item
            pending_work_items.clear()
            # Terminate remaining workers forcibly: the queues ama their
            # locks may be kwenye a dirty state na block forever.
            kila p kwenye processes.values():
                p.terminate()
            shutdown_worker()
            return
        ikiwa isinstance(result_item, int):
            # Clean shutdown of a worker using its PID
            # (avoids marking the executor broken)
            assert shutting_down()
            p = processes.pop(result_item)
            p.join()
            ikiwa sio processes:
                shutdown_worker()
                return
        lasivyo result_item ni sio Tupu:
            work_item = pending_work_items.pop(result_item.work_id, Tupu)
            # work_item can be Tupu ikiwa another process terminated (see above)
            ikiwa work_item ni sio Tupu:
                ikiwa result_item.exception:
                    work_item.future.set_exception(result_item.exception)
                isipokua:
                    work_item.future.set_result(result_item.result)
                # Delete references to object. See issue16284
                toa work_item
            # Delete reference to result_item
            toa result_item

        # Check whether we should start shutting down.
        executor = executor_reference()
        # No more work items can be added if:
        #   - The interpreter ni shutting down OR
        #   - The executor that owns this worker has been collected OR
        #   - The executor that owns this worker has been shutdown.
        ikiwa shutting_down():
            jaribu:
                # Flag the executor kama shutting down kama early kama possible ikiwa it
                # ni sio gc-ed yet.
                ikiwa executor ni sio Tupu:
                    executor._shutdown_thread = Kweli
                # Since no new work items can be added, it ni safe to shutdown
                # this thread ikiwa there are no pending work items.
                ikiwa sio pending_work_items:
                    shutdown_worker()
                    return
            tatizo Full:
                # This ni sio a problem: we will eventually be woken up (in
                # result_queue.get()) na be able to send a sentinel again.
                pita
        executor = Tupu


_system_limits_checked = Uongo
_system_limited = Tupu


eleza _check_system_limits():
    global _system_limits_checked, _system_limited
    ikiwa _system_limits_checked:
        ikiwa _system_limited:
            ashiria NotImplementedError(_system_limited)
    _system_limits_checked = Kweli
    jaribu:
        nsems_max = os.sysconf("SC_SEM_NSEMS_MAX")
    tatizo (AttributeError, ValueError):
        # sysconf sio available ama setting sio available
        return
    ikiwa nsems_max == -1:
        # indetermined limit, assume that limit ni determined
        # by available memory only
        return
    ikiwa nsems_max >= 256:
        # minimum number of semaphores available
        # according to POSIX
        return
    _system_limited = ("system provides too few semaphores (%d"
                       " available, 256 necessary)" % nsems_max)
    ashiria NotImplementedError(_system_limited)


eleza _chain_from_iterable_of_lists(iterable):
    """
    Specialized implementation of itertools.chain.from_iterable.
    Each item kwenye *iterable* should be a list.  This function is
    careful sio to keep references to tumaed objects.
    """
    kila element kwenye iterable:
        element.reverse()
        wakati element:
            tuma element.pop()


kundi BrokenProcessPool(_base.BrokenExecutor):
    """
    Raised when a process kwenye a ProcessPoolExecutor terminated abruptly
    wakati a future was kwenye the running state.
    """


kundi ProcessPoolExecutor(_base.Executor):
    eleza __init__(self, max_workers=Tupu, mp_context=Tupu,
                 initializer=Tupu, initargs=()):
        """Initializes a new ProcessPoolExecutor instance.

        Args:
            max_workers: The maximum number of processes that can be used to
                execute the given calls. If Tupu ama sio given then kama many
                worker processes will be created kama the machine has processors.
            mp_context: A multiprocessing context to launch the workers. This
                object should provide SimpleQueue, Queue na Process.
            initializer: A callable used to initialize worker processes.
            initargs: A tuple of arguments to pita to the initializer.
        """
        _check_system_limits()

        ikiwa max_workers ni Tupu:
            self._max_workers = os.cpu_count() ama 1
            ikiwa sys.platform == 'win32':
                self._max_workers = min(_MAX_WINDOWS_WORKERS,
                                        self._max_workers)
        isipokua:
            ikiwa max_workers <= 0:
                ashiria ValueError("max_workers must be greater than 0")
            lasivyo (sys.platform == 'win32' na
                max_workers > _MAX_WINDOWS_WORKERS):
                ashiria ValueError(
                    f"max_workers must be <= {_MAX_WINDOWS_WORKERS}")

            self._max_workers = max_workers

        ikiwa mp_context ni Tupu:
            mp_context = mp.get_context()
        self._mp_context = mp_context

        ikiwa initializer ni sio Tupu na sio callable(initializer):
            ashiria TypeError("initializer must be a callable")
        self._initializer = initializer
        self._initargs = initargs

        # Management thread
        self._queue_management_thread = Tupu

        # Map of pids to processes
        self._processes = {}

        # Shutdown ni a two-step process.
        self._shutdown_thread = Uongo
        self._shutdown_lock = threading.Lock()
        self._broken = Uongo
        self._queue_count = 0
        self._pending_work_items = {}

        # Create communication channels kila the executor
        # Make the call queue slightly larger than the number of processes to
        # prevent the worker processes kutoka idling. But don't make it too big
        # because futures kwenye the call queue cannot be cancelled.
        queue_size = self._max_workers + EXTRA_QUEUED_CALLS
        self._call_queue = _SafeQueue(
            max_size=queue_size, ctx=self._mp_context,
            pending_work_items=self._pending_work_items)
        # Killed worker processes can produce spurious "broken pipe"
        # tracebacks kwenye the queue's own worker thread. But we detect killed
        # processes anyway, so silence the tracebacks.
        self._call_queue._ignore_epipe = Kweli
        self._result_queue = mp_context.SimpleQueue()
        self._work_ids = queue.Queue()

        # _ThreadWakeup ni a communication channel used to interrupt the wait
        # of the main loop of queue_manager_thread kutoka another thread (e.g.
        # when calling executor.submit ama executor.shutdown). We do sio use the
        # _result_queue to send the wakeup signal to the queue_manager_thread
        # kama it could result kwenye a deadlock ikiwa a worker process dies ukijumuisha the
        # _result_queue write lock still acquired.
        self._queue_management_thread_wakeup = _ThreadWakeup()

    eleza _start_queue_management_thread(self):
        ikiwa self._queue_management_thread ni Tupu:
            # When the executor gets garbarge collected, the weakref callback
            # will wake up the queue management thread so that it can terminate
            # ikiwa there ni no pending work item.
            eleza weakref_cb(_,
                           thread_wakeup=self._queue_management_thread_wakeup):
                mp.util.debug('Executor collected: triggering callback for'
                              ' QueueManager wakeup')
                thread_wakeup.wakeup()
            # Start the processes so that their sentinels are known.
            self._adjust_process_count()
            self._queue_management_thread = threading.Thread(
                target=_queue_management_worker,
                args=(weakref.ref(self, weakref_cb),
                      self._processes,
                      self._pending_work_items,
                      self._work_ids,
                      self._call_queue,
                      self._result_queue,
                      self._queue_management_thread_wakeup),
                name="QueueManagerThread")
            self._queue_management_thread.daemon = Kweli
            self._queue_management_thread.start()
            _threads_wakeups[self._queue_management_thread] = \
                self._queue_management_thread_wakeup

    eleza _adjust_process_count(self):
        kila _ kwenye range(len(self._processes), self._max_workers):
            p = self._mp_context.Process(
                target=_process_worker,
                args=(self._call_queue,
                      self._result_queue,
                      self._initializer,
                      self._initargs))
            p.start()
            self._processes[p.pid] = p

    eleza submit(*args, **kwargs):
        ikiwa len(args) >= 2:
            self, fn, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor 'submit' of 'ProcessPoolExecutor' object "
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
                ashiria BrokenProcessPool(self._broken)
            ikiwa self._shutdown_thread:
                ashiria RuntimeError('cannot schedule new futures after shutdown')
            ikiwa _global_shutdown:
                ashiria RuntimeError('cannot schedule new futures after '
                                   'interpreter shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._pending_work_items[self._queue_count] = w
            self._work_ids.put(self._queue_count)
            self._queue_count += 1
            # Wake up queue management thread
            self._queue_management_thread_wakeup.wakeup()

            self._start_queue_management_thread()
            rudisha f
    submit.__text_signature__ = _base.Executor.submit.__text_signature__
    submit.__doc__ = _base.Executor.submit.__doc__

    eleza map(self, fn, *iterables, timeout=Tupu, chunksize=1):
        """Returns an iterator equivalent to map(fn, iter).

        Args:
            fn: A callable that will take kama many arguments kama there are
                pitaed iterables.
            timeout: The maximum number of seconds to wait. If Tupu, then there
                ni no limit on the wait time.
            chunksize: If greater than one, the iterables will be chopped into
                chunks of size chunksize na submitted to the process pool.
                If set to one, the items kwenye the list will be sent one at a time.

        Returns:
            An iterator equivalent to: map(func, *iterables) but the calls may
            be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could sio be generated
                before the given timeout.
            Exception: If fn(*args) raises kila any values.
        """
        ikiwa chunksize < 1:
            ashiria ValueError("chunksize must be >= 1.")

        results = super().map(partial(_process_chunk, fn),
                              _get_chunks(*iterables, chunksize=chunksize),
                              timeout=timeout)
        rudisha _chain_from_iterable_of_lists(results)

    eleza shutdown(self, wait=Kweli):
        ukijumuisha self._shutdown_lock:
            self._shutdown_thread = Kweli
        ikiwa self._queue_management_thread:
            # Wake up queue management thread
            self._queue_management_thread_wakeup.wakeup()
            ikiwa wait:
                self._queue_management_thread.join()
        # To reduce the risk of opening too many files, remove references to
        # objects that use file descriptors.
        self._queue_management_thread = Tupu
        ikiwa self._call_queue ni sio Tupu:
            self._call_queue.close()
            ikiwa wait:
                self._call_queue.join_thread()
            self._call_queue = Tupu
        self._result_queue = Tupu
        self._processes = Tupu

        ikiwa self._queue_management_thread_wakeup:
            self._queue_management_thread_wakeup.close()
            self._queue_management_thread_wakeup = Tupu

    shutdown.__doc__ = _base.Executor.shutdown.__doc__

atexit.register(_python_exit)
