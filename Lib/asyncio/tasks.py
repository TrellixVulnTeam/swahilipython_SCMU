"""Support for tasks, coroutines and the scheduler."""

__all__ = (
    'Task', 'create_task',
    'FIRST_COMPLETED', 'FIRST_EXCEPTION', 'ALL_COMPLETED',
    'wait', 'wait_for', 'as_completed', 'sleep',
    'gather', 'shield', 'ensure_future', 'run_coroutine_threadsafe',
    'current_task', 'all_tasks',
    '_register_task', '_unregister_task', '_enter_task', '_leave_task',
)

agiza concurrent.futures
agiza contextvars
agiza functools
agiza inspect
agiza itertools
agiza types
agiza warnings
agiza weakref

kutoka . agiza base_tasks
kutoka . agiza coroutines
kutoka . agiza events
kutoka . agiza exceptions
kutoka . agiza futures
kutoka .coroutines agiza _is_coroutine

# Helper to generate new task names
# This uses itertools.count() instead of a "+= 1" operation because the latter
# is not thread safe. See bpo-11866 for a longer explanation.
_task_name_counter = itertools.count(1).__next__


eleza current_task(loop=None):
    """Return a currently executed task."""
    ikiwa loop is None:
        loop = events.get_running_loop()
    rudisha _current_tasks.get(loop)


eleza all_tasks(loop=None):
    """Return a set of all tasks for the loop."""
    ikiwa loop is None:
        loop = events.get_running_loop()
    # Looping over a WeakSet (_all_tasks) isn't safe as it can be updated kutoka another
    # thread while we do so. Therefore we cast it to list prior to filtering. The list
    # cast itself requires iteration, so we repeat it several times ignoring
    # RuntimeErrors (which are not very likely to occur). See issues 34970 and 36607 for
    # details.
    i = 0
    while True:
        try:
            tasks = list(_all_tasks)
        except RuntimeError:
            i += 1
            ikiwa i >= 1000:
                raise
        else:
            break
    rudisha {t for t in tasks
            ikiwa futures._get_loop(t) is loop and not t.done()}


eleza _all_tasks_compat(loop=None):
    # Different kutoka "all_task()" by returning *all* Tasks, including
    # the completed ones.  Used to implement deprecated "Tasks.all_task()"
    # method.
    ikiwa loop is None:
        loop = events.get_event_loop()
    # Looping over a WeakSet (_all_tasks) isn't safe as it can be updated kutoka another
    # thread while we do so. Therefore we cast it to list prior to filtering. The list
    # cast itself requires iteration, so we repeat it several times ignoring
    # RuntimeErrors (which are not very likely to occur). See issues 34970 and 36607 for
    # details.
    i = 0
    while True:
        try:
            tasks = list(_all_tasks)
        except RuntimeError:
            i += 1
            ikiwa i >= 1000:
                raise
        else:
            break
    rudisha {t for t in tasks ikiwa futures._get_loop(t) is loop}


eleza _set_task_name(task, name):
    ikiwa name is not None:
        try:
            set_name = task.set_name
        except AttributeError:
            pass
        else:
            set_name(name)


kundi Task(futures._PyFuture):  # Inherit Python Task implementation
                                # kutoka a Python Future implementation.

    """A coroutine wrapped in a Future."""

    # An agizaant invariant maintained while a Task not done:
    #
    # - Either _fut_waiter is None, and _step() is scheduled;
    # - or _fut_waiter is some Future, and _step() is *not* scheduled.
    #
    # The only transition kutoka the latter to the former is through
    # _wakeup().  When _fut_waiter is not None, one of its callbacks
    # must be _wakeup().

    # If False, don't log a message ikiwa the task is destroyed whereas its
    # status is still pending
    _log_destroy_pending = True

    @classmethod
    eleza current_task(cls, loop=None):
        """Return the currently running task in an event loop or None.

        By default the current task for the current event loop is returned.

        None is returned when called not in the context of a Task.
        """
        warnings.warn("Task.current_task() is deprecated since Python 3.7, "
                      "use asyncio.current_task() instead",
                      DeprecationWarning,
                      stacklevel=2)
        ikiwa loop is None:
            loop = events.get_event_loop()
        rudisha current_task(loop)

    @classmethod
    eleza all_tasks(cls, loop=None):
        """Return a set of all tasks for an event loop.

        By default all tasks for the current event loop are returned.
        """
        warnings.warn("Task.all_tasks() is deprecated since Python 3.7, "
                      "use asyncio.all_tasks() instead",
                      DeprecationWarning,
                      stacklevel=2)
        rudisha _all_tasks_compat(loop)

    eleza __init__(self, coro, *, loop=None, name=None):
        super().__init__(loop=loop)
        ikiwa self._source_traceback:
            del self._source_traceback[-1]
        ikiwa not coroutines.iscoroutine(coro):
            # raise after Future.__init__(), attrs are required for __del__
            # prevent logging for pending task in __del__
            self._log_destroy_pending = False
            raise TypeError(f"a coroutine was expected, got {coro!r}")

        ikiwa name is None:
            self._name = f'Task-{_task_name_counter()}'
        else:
            self._name = str(name)

        self._must_cancel = False
        self._fut_waiter = None
        self._coro = coro
        self._context = contextvars.copy_context()

        self._loop.call_soon(self.__step, context=self._context)
        _register_task(self)

    eleza __del__(self):
        ikiwa self._state == futures._PENDING and self._log_destroy_pending:
            context = {
                'task': self,
                'message': 'Task was destroyed but it is pending!',
            }
            ikiwa self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)
        super().__del__()

    eleza _repr_info(self):
        rudisha base_tasks._task_repr_info(self)

    eleza get_coro(self):
        rudisha self._coro

    eleza get_name(self):
        rudisha self._name

    eleza set_name(self, value):
        self._name = str(value)

    eleza set_result(self, result):
        raise RuntimeError('Task does not support set_result operation')

    eleza set_exception(self, exception):
        raise RuntimeError('Task does not support set_exception operation')

    eleza get_stack(self, *, limit=None):
        """Return the list of stack frames for this task's coroutine.

        If the coroutine is not done, this returns the stack where it is
        suspended.  If the coroutine has completed successfully or was
        cancelled, this returns an empty list.  If the coroutine was
        terminated by an exception, this returns the list of traceback
        frames.

        The frames are always ordered kutoka oldest to newest.

        The optional limit gives the maximum number of frames to
        return; by default all available frames are returned.  Its
        meaning differs depending on whether a stack or a traceback is
        returned: the newest frames of a stack are returned, but the
        oldest frames of a traceback are returned.  (This matches the
        behavior of the traceback module.)

        For reasons beyond our control, only one stack frame is
        returned for a suspended coroutine.
        """
        rudisha base_tasks._task_get_stack(self, limit)

    eleza print_stack(self, *, limit=None, file=None):
        """Print the stack or traceback for this task's coroutine.

        This produces output similar to that of the traceback module,
        for the frames retrieved by get_stack().  The limit argument
        is passed to get_stack().  The file argument is an I/O stream
        to which the output is written; by default output is written
        to sys.stderr.
        """
        rudisha base_tasks._task_print_stack(self, limit, file)

    eleza cancel(self):
        """Request that this task cancel itself.

        This arranges for a CancelledError to be thrown into the
        wrapped coroutine on the next cycle through the event loop.
        The coroutine then has a chance to clean up or even deny
        the request using try/except/finally.

        Unlike Future.cancel, this does not guarantee that the
        task will be cancelled: the exception might be caught and
        acted upon, delaying cancellation of the task or preventing
        cancellation completely.  The task may also rudisha a value or
        raise a different exception.

        Immediately after this method is called, Task.cancelled() will
        not rudisha True (unless the task was already cancelled).  A
        task will be marked as cancelled when the wrapped coroutine
        terminates with a CancelledError exception (even ikiwa cancel()
        was not called).
        """
        self._log_traceback = False
        ikiwa self.done():
            rudisha False
        ikiwa self._fut_waiter is not None:
            ikiwa self._fut_waiter.cancel():
                # Leave self._fut_waiter; it may be a Task that
                # catches and ignores the cancellation so we may have
                # to cancel it again later.
                rudisha True
        # It must be the case that self.__step is already scheduled.
        self._must_cancel = True
        rudisha True

    eleza __step(self, exc=None):
        ikiwa self.done():
            raise exceptions.InvalidStateError(
                f'_step(): already done: {self!r}, {exc!r}')
        ikiwa self._must_cancel:
            ikiwa not isinstance(exc, exceptions.CancelledError):
                exc = exceptions.CancelledError()
            self._must_cancel = False
        coro = self._coro
        self._fut_waiter = None

        _enter_task(self._loop, self)
        # Call either coro.throw(exc) or coro.send(None).
        try:
            ikiwa exc is None:
                # We use the `send` method directly, because coroutines
                # don't have `__iter__` and `__next__` methods.
                result = coro.send(None)
            else:
                result = coro.throw(exc)
        except StopIteration as exc:
            ikiwa self._must_cancel:
                # Task is cancelled right before coro stops.
                self._must_cancel = False
                super().cancel()
            else:
                super().set_result(exc.value)
        except exceptions.CancelledError:
            super().cancel()  # I.e., Future.cancel(self).
        except (KeyboardInterrupt, SystemExit) as exc:
            super().set_exception(exc)
            raise
        except BaseException as exc:
            super().set_exception(exc)
        else:
            blocking = getattr(result, '_asyncio_future_blocking', None)
            ikiwa blocking is not None:
                # Yielded Future must come kutoka Future.__iter__().
                ikiwa futures._get_loop(result) is not self._loop:
                    new_exc = RuntimeError(
                        f'Task {self!r} got Future '
                        f'{result!r} attached to a different loop')
                    self._loop.call_soon(
                        self.__step, new_exc, context=self._context)
                elikiwa blocking:
                    ikiwa result is self:
                        new_exc = RuntimeError(
                            f'Task cannot await on itself: {self!r}')
                        self._loop.call_soon(
                            self.__step, new_exc, context=self._context)
                    else:
                        result._asyncio_future_blocking = False
                        result.add_done_callback(
                            self.__wakeup, context=self._context)
                        self._fut_waiter = result
                        ikiwa self._must_cancel:
                            ikiwa self._fut_waiter.cancel():
                                self._must_cancel = False
                else:
                    new_exc = RuntimeError(
                        f'yield was used instead of yield kutoka '
                        f'in task {self!r} with {result!r}')
                    self._loop.call_soon(
                        self.__step, new_exc, context=self._context)

            elikiwa result is None:
                # Bare yield relinquishes control for one event loop iteration.
                self._loop.call_soon(self.__step, context=self._context)
            elikiwa inspect.isgenerator(result):
                # Yielding a generator is just wrong.
                new_exc = RuntimeError(
                    f'yield was used instead of yield kutoka for '
                    f'generator in task {self!r} with {result!r}')
                self._loop.call_soon(
                    self.__step, new_exc, context=self._context)
            else:
                # Yielding something else is an error.
                new_exc = RuntimeError(f'Task got bad yield: {result!r}')
                self._loop.call_soon(
                    self.__step, new_exc, context=self._context)
        finally:
            _leave_task(self._loop, self)
            self = None  # Needed to break cycles when an exception occurs.

    eleza __wakeup(self, future):
        try:
            future.result()
        except BaseException as exc:
            # This may also be a cancellation.
            self.__step(exc)
        else:
            # Don't pass the value of `future.result()` explicitly,
            # as `Future.__iter__` and `Future.__await__` don't need it.
            # If we call `_step(value, None)` instead of `_step()`,
            # Python eval loop would use `.send(value)` method call,
            # instead of `__next__()`, which is slower for futures
            # that rudisha non-generator iterators kutoka their `__iter__`.
            self.__step()
        self = None  # Needed to break cycles when an exception occurs.


_PyTask = Task


try:
    agiza _asyncio
except ImportError:
    pass
else:
    # _CTask is needed for tests.
    Task = _CTask = _asyncio.Task


eleza create_task(coro, *, name=None):
    """Schedule the execution of a coroutine object in a spawn task.

    Return a Task object.
    """
    loop = events.get_running_loop()
    task = loop.create_task(coro)
    _set_task_name(task, name)
    rudisha task


# wait() and as_completed() similar to those in PEP 3148.

FIRST_COMPLETED = concurrent.futures.FIRST_COMPLETED
FIRST_EXCEPTION = concurrent.futures.FIRST_EXCEPTION
ALL_COMPLETED = concurrent.futures.ALL_COMPLETED


async eleza wait(fs, *, loop=None, timeout=None, return_when=ALL_COMPLETED):
    """Wait for the Futures and coroutines given by fs to complete.

    The sequence futures must not be empty.

    Coroutines will be wrapped in Tasks.

    Returns two sets of Future: (done, pending).

    Usage:

        done, pending = await asyncio.wait(fs)

    Note: This does not raise TimeoutError! Futures that aren't done
    when the timeout occurs are returned in the second set.
    """
    ikiwa futures.isfuture(fs) or coroutines.iscoroutine(fs):
        raise TypeError(f"expect a list of futures, not {type(fs).__name__}")
    ikiwa not fs:
        raise ValueError('Set of coroutines/Futures is empty.')
    ikiwa return_when not in (FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED):
        raise ValueError(f'Invalid return_when value: {return_when}')

    ikiwa loop is None:
        loop = events.get_running_loop()
    else:
        warnings.warn("The loop argument is deprecated since Python 3.8, "
                      "and scheduled for removal in Python 3.10.",
                      DeprecationWarning, stacklevel=2)

    fs = {ensure_future(f, loop=loop) for f in set(fs)}

    rudisha await _wait(fs, timeout, return_when, loop)


eleza _release_waiter(waiter, *args):
    ikiwa not waiter.done():
        waiter.set_result(None)


async eleza wait_for(fut, timeout, *, loop=None):
    """Wait for the single Future or coroutine to complete, with timeout.

    Coroutine will be wrapped in Task.

    Returns result of the Future or coroutine.  When a timeout occurs,
    it cancels the task and raises TimeoutError.  To avoid the task
    cancellation, wrap it in shield().

    If the wait is cancelled, the task is also cancelled.

    This function is a coroutine.
    """
    ikiwa loop is None:
        loop = events.get_running_loop()
    else:
        warnings.warn("The loop argument is deprecated since Python 3.8, "
                      "and scheduled for removal in Python 3.10.",
                      DeprecationWarning, stacklevel=2)

    ikiwa timeout is None:
        rudisha await fut

    ikiwa timeout <= 0:
        fut = ensure_future(fut, loop=loop)

        ikiwa fut.done():
            rudisha fut.result()

        fut.cancel()
        raise exceptions.TimeoutError()

    waiter = loop.create_future()
    timeout_handle = loop.call_later(timeout, _release_waiter, waiter)
    cb = functools.partial(_release_waiter, waiter)

    fut = ensure_future(fut, loop=loop)
    fut.add_done_callback(cb)

    try:
        # wait until the future completes or the timeout
        try:
            await waiter
        except exceptions.CancelledError:
            fut.remove_done_callback(cb)
            fut.cancel()
            raise

        ikiwa fut.done():
            rudisha fut.result()
        else:
            fut.remove_done_callback(cb)
            # We must ensure that the task is not running
            # after wait_for() returns.
            # See https://bugs.python.org/issue32751
            await _cancel_and_wait(fut, loop=loop)
            raise exceptions.TimeoutError()
    finally:
        timeout_handle.cancel()


async eleza _wait(fs, timeout, return_when, loop):
    """Internal helper for wait().

    The fs argument must be a collection of Futures.
    """
    assert fs, 'Set of Futures is empty.'
    waiter = loop.create_future()
    timeout_handle = None
    ikiwa timeout is not None:
        timeout_handle = loop.call_later(timeout, _release_waiter, waiter)
    counter = len(fs)

    eleza _on_completion(f):
        nonlocal counter
        counter -= 1
        ikiwa (counter <= 0 or
            return_when == FIRST_COMPLETED or
            return_when == FIRST_EXCEPTION and (not f.cancelled() and
                                                f.exception() is not None)):
            ikiwa timeout_handle is not None:
                timeout_handle.cancel()
            ikiwa not waiter.done():
                waiter.set_result(None)

    for f in fs:
        f.add_done_callback(_on_completion)

    try:
        await waiter
    finally:
        ikiwa timeout_handle is not None:
            timeout_handle.cancel()
        for f in fs:
            f.remove_done_callback(_on_completion)

    done, pending = set(), set()
    for f in fs:
        ikiwa f.done():
            done.add(f)
        else:
            pending.add(f)
    rudisha done, pending


async eleza _cancel_and_wait(fut, loop):
    """Cancel the *fut* future or task and wait until it completes."""

    waiter = loop.create_future()
    cb = functools.partial(_release_waiter, waiter)
    fut.add_done_callback(cb)

    try:
        fut.cancel()
        # We cannot wait on *fut* directly to make
        # sure _cancel_and_wait itself is reliably cancellable.
        await waiter
    finally:
        fut.remove_done_callback(cb)


# This is *not* a @coroutine!  It is just an iterator (yielding Futures).
eleza as_completed(fs, *, loop=None, timeout=None):
    """Return an iterator whose values are coroutines.

    When waiting for the yielded coroutines you'll get the results (or
    exceptions!) of the original Futures (or coroutines), in the order
    in which and as soon as they complete.

    This differs kutoka PEP 3148; the proper way to use this is:

        for f in as_completed(fs):
            result = await f  # The 'await' may raise.
            # Use result.

    If a timeout is specified, the 'await' will raise
    TimeoutError when the timeout occurs before all Futures are done.

    Note: The futures 'f' are not necessarily members of fs.
    """
    ikiwa futures.isfuture(fs) or coroutines.iscoroutine(fs):
        raise TypeError(f"expect a list of futures, not {type(fs).__name__}")

    kutoka .queues agiza Queue  # Import here to avoid circular agiza problem.
    done = Queue(loop=loop)

    ikiwa loop is None:
        loop = events.get_event_loop()
    else:
        warnings.warn("The loop argument is deprecated since Python 3.8, "
                      "and scheduled for removal in Python 3.10.",
                      DeprecationWarning, stacklevel=2)
    todo = {ensure_future(f, loop=loop) for f in set(fs)}
    timeout_handle = None

    eleza _on_timeout():
        for f in todo:
            f.remove_done_callback(_on_completion)
            done.put_nowait(None)  # Queue a dummy value for _wait_for_one().
        todo.clear()  # Can't do todo.remove(f) in the loop.

    eleza _on_completion(f):
        ikiwa not todo:
            rudisha  # _on_timeout() was here first.
        todo.remove(f)
        done.put_nowait(f)
        ikiwa not todo and timeout_handle is not None:
            timeout_handle.cancel()

    async eleza _wait_for_one():
        f = await done.get()
        ikiwa f is None:
            # Dummy value kutoka _on_timeout().
            raise exceptions.TimeoutError
        rudisha f.result()  # May raise f.exception().

    for f in todo:
        f.add_done_callback(_on_completion)
    ikiwa todo and timeout is not None:
        timeout_handle = loop.call_later(timeout, _on_timeout)
    for _ in range(len(todo)):
        yield _wait_for_one()


@types.coroutine
eleza __sleep0():
    """Skip one event loop run cycle.

    This is a private helper for 'asyncio.sleep()', used
    when the 'delay' is set to 0.  It uses a bare 'yield'
    expression (which Task.__step knows how to handle)
    instead of creating a Future object.
    """
    yield


async eleza sleep(delay, result=None, *, loop=None):
    """Coroutine that completes after a given time (in seconds)."""
    ikiwa delay <= 0:
        await __sleep0()
        rudisha result

    ikiwa loop is None:
        loop = events.get_running_loop()
    else:
        warnings.warn("The loop argument is deprecated since Python 3.8, "
                      "and scheduled for removal in Python 3.10.",
                      DeprecationWarning, stacklevel=2)

    future = loop.create_future()
    h = loop.call_later(delay,
                        futures._set_result_unless_cancelled,
                        future, result)
    try:
        rudisha await future
    finally:
        h.cancel()


eleza ensure_future(coro_or_future, *, loop=None):
    """Wrap a coroutine or an awaitable in a future.

    If the argument is a Future, it is returned directly.
    """
    ikiwa coroutines.iscoroutine(coro_or_future):
        ikiwa loop is None:
            loop = events.get_event_loop()
        task = loop.create_task(coro_or_future)
        ikiwa task._source_traceback:
            del task._source_traceback[-1]
        rudisha task
    elikiwa futures.isfuture(coro_or_future):
        ikiwa loop is not None and loop is not futures._get_loop(coro_or_future):
            raise ValueError('The future belongs to a different loop than '
                             'the one specified as the loop argument')
        rudisha coro_or_future
    elikiwa inspect.isawaitable(coro_or_future):
        rudisha ensure_future(_wrap_awaitable(coro_or_future), loop=loop)
    else:
        raise TypeError('An asyncio.Future, a coroutine or an awaitable is '
                        'required')


@types.coroutine
eleza _wrap_awaitable(awaitable):
    """Helper for asyncio.ensure_future().

    Wraps awaitable (an object with __await__) into a coroutine
    that will later be wrapped in a Task by ensure_future().
    """
    rudisha (yield kutoka awaitable.__await__())

_wrap_awaitable._is_coroutine = _is_coroutine


kundi _GatheringFuture(futures.Future):
    """Helper for gather().

    This overrides cancel() to cancel all the children and act more
    like Task.cancel(), which doesn't immediately mark itself as
    cancelled.
    """

    eleza __init__(self, children, *, loop=None):
        super().__init__(loop=loop)
        self._children = children
        self._cancel_requested = False

    eleza cancel(self):
        ikiwa self.done():
            rudisha False
        ret = False
        for child in self._children:
            ikiwa child.cancel():
                ret = True
        ikiwa ret:
            # If any child tasks were actually cancelled, we should
            # propagate the cancellation request regardless of
            # *return_exceptions* argument.  See issue 32684.
            self._cancel_requested = True
        rudisha ret


eleza gather(*coros_or_futures, loop=None, return_exceptions=False):
    """Return a future aggregating results kutoka the given coroutines/futures.

    Coroutines will be wrapped in a future and scheduled in the event
    loop. They will not necessarily be scheduled in the same order as
    passed in.

    All futures must share the same event loop.  If all the tasks are
    done successfully, the returned future's result is the list of
    results (in the order of the original sequence, not necessarily
    the order of results arrival).  If *return_exceptions* is True,
    exceptions in the tasks are treated the same as successful
    results, and gathered in the result list; otherwise, the first
    raised exception will be immediately propagated to the returned
    future.

    Cancellation: ikiwa the outer Future is cancelled, all children (that
    have not completed yet) are also cancelled.  If any child is
    cancelled, this is treated as ikiwa it raised CancelledError --
    the outer Future is *not* cancelled in this case.  (This is to
    prevent the cancellation of one child to cause other children to
    be cancelled.)
    """
    ikiwa not coros_or_futures:
        ikiwa loop is None:
            loop = events.get_event_loop()
        else:
            warnings.warn("The loop argument is deprecated since Python 3.8, "
                          "and scheduled for removal in Python 3.10.",
                          DeprecationWarning, stacklevel=2)
        outer = loop.create_future()
        outer.set_result([])
        rudisha outer

    eleza _done_callback(fut):
        nonlocal nfinished
        nfinished += 1

        ikiwa outer.done():
            ikiwa not fut.cancelled():
                # Mark exception retrieved.
                fut.exception()
            return

        ikiwa not return_exceptions:
            ikiwa fut.cancelled():
                # Check ikiwa 'fut' is cancelled first, as
                # 'fut.exception()' will *raise* a CancelledError
                # instead of returning it.
                exc = exceptions.CancelledError()
                outer.set_exception(exc)
                return
            else:
                exc = fut.exception()
                ikiwa exc is not None:
                    outer.set_exception(exc)
                    return

        ikiwa nfinished == nfuts:
            # All futures are done; create a list of results
            # and set it to the 'outer' future.
            results = []

            for fut in children:
                ikiwa fut.cancelled():
                    # Check ikiwa 'fut' is cancelled first, as
                    # 'fut.exception()' will *raise* a CancelledError
                    # instead of returning it.
                    res = exceptions.CancelledError()
                else:
                    res = fut.exception()
                    ikiwa res is None:
                        res = fut.result()
                results.append(res)

            ikiwa outer._cancel_requested:
                # If gather is being cancelled we must propagate the
                # cancellation regardless of *return_exceptions* argument.
                # See issue 32684.
                outer.set_exception(exceptions.CancelledError())
            else:
                outer.set_result(results)

    arg_to_fut = {}
    children = []
    nfuts = 0
    nfinished = 0
    for arg in coros_or_futures:
        ikiwa arg not in arg_to_fut:
            fut = ensure_future(arg, loop=loop)
            ikiwa loop is None:
                loop = futures._get_loop(fut)
            ikiwa fut is not arg:
                # 'arg' was not a Future, therefore, 'fut' is a new
                # Future created specifically for 'arg'.  Since the caller
                # can't control it, disable the "destroy pending task"
                # warning.
                fut._log_destroy_pending = False

            nfuts += 1
            arg_to_fut[arg] = fut
            fut.add_done_callback(_done_callback)

        else:
            # There's a duplicate Future object in coros_or_futures.
            fut = arg_to_fut[arg]

        children.append(fut)

    outer = _GatheringFuture(children, loop=loop)
    rudisha outer


eleza shield(arg, *, loop=None):
    """Wait for a future, shielding it kutoka cancellation.

    The statement

        res = await shield(something())

    is exactly equivalent to the statement

        res = await something()

    *except* that ikiwa the coroutine containing it is cancelled, the
    task running in something() is not cancelled.  From the POV of
    something(), the cancellation did not happen.  But its caller is
    still cancelled, so the yield-kutoka expression still raises
    CancelledError.  Note: If something() is cancelled by other means
    this will still cancel shield().

    If you want to completely ignore cancellation (not recommended)
    you can combine shield() with a try/except clause, as follows:

        try:
            res = await shield(something())
        except CancelledError:
            res = None
    """
    ikiwa loop is not None:
        warnings.warn("The loop argument is deprecated since Python 3.8, "
                      "and scheduled for removal in Python 3.10.",
                      DeprecationWarning, stacklevel=2)
    inner = ensure_future(arg, loop=loop)
    ikiwa inner.done():
        # Shortcut.
        rudisha inner
    loop = futures._get_loop(inner)
    outer = loop.create_future()

    eleza _inner_done_callback(inner):
        ikiwa outer.cancelled():
            ikiwa not inner.cancelled():
                # Mark inner's result as retrieved.
                inner.exception()
            return

        ikiwa inner.cancelled():
            outer.cancel()
        else:
            exc = inner.exception()
            ikiwa exc is not None:
                outer.set_exception(exc)
            else:
                outer.set_result(inner.result())


    eleza _outer_done_callback(outer):
        ikiwa not inner.done():
            inner.remove_done_callback(_inner_done_callback)

    inner.add_done_callback(_inner_done_callback)
    outer.add_done_callback(_outer_done_callback)
    rudisha outer


eleza run_coroutine_threadsafe(coro, loop):
    """Submit a coroutine object to a given event loop.

    Return a concurrent.futures.Future to access the result.
    """
    ikiwa not coroutines.iscoroutine(coro):
        raise TypeError('A coroutine object is required')
    future = concurrent.futures.Future()

    eleza callback():
        try:
            futures._chain_future(ensure_future(coro, loop=loop), future)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            ikiwa future.set_running_or_notify_cancel():
                future.set_exception(exc)
            raise

    loop.call_soon_threadsafe(callback)
    rudisha future


# WeakSet containing all alive tasks.
_all_tasks = weakref.WeakSet()

# Dictionary containing tasks that are currently active in
# all running event loops.  {EventLoop: Task}
_current_tasks = {}


eleza _register_task(task):
    """Register a new task in asyncio as executed by loop."""
    _all_tasks.add(task)


eleza _enter_task(loop, task):
    current_task = _current_tasks.get(loop)
    ikiwa current_task is not None:
        raise RuntimeError(f"Cannot enter into task {task!r} while another "
                           f"task {current_task!r} is being executed.")
    _current_tasks[loop] = task


eleza _leave_task(loop, task):
    current_task = _current_tasks.get(loop)
    ikiwa current_task is not task:
        raise RuntimeError(f"Leaving task {task!r} does not match "
                           f"the current task {current_task!r}.")
    del _current_tasks[loop]


eleza _unregister_task(task):
    """Unregister a task."""
    _all_tasks.discard(task)


_py_register_task = _register_task
_py_unregister_task = _unregister_task
_py_enter_task = _enter_task
_py_leave_task = _leave_task


try:
    kutoka _asyncio agiza (_register_task, _unregister_task,
                          _enter_task, _leave_task,
                          _all_tasks, _current_tasks)
except ImportError:
    pass
else:
    _c_register_task = _register_task
    _c_unregister_task = _unregister_task
    _c_enter_task = _enter_task
    _c_leave_task = _leave_task
