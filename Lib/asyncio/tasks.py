"""Support kila tasks, coroutines na the scheduler."""

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
# ni sio thread safe. See bpo-11866 kila a longer explanation.
_task_name_counter = itertools.count(1).__next__


eleza current_task(loop=Tupu):
    """Return a currently executed task."""
    ikiwa loop ni Tupu:
        loop = events.get_running_loop()
    rudisha _current_tasks.get(loop)


eleza all_tasks(loop=Tupu):
    """Return a set of all tasks kila the loop."""
    ikiwa loop ni Tupu:
        loop = events.get_running_loop()
    # Looping over a WeakSet (_all_tasks) isn't safe kama it can be updated kutoka another
    # thread wakati we do so. Therefore we cast it to list prior to filtering. The list
    # cast itself requires iteration, so we repeat it several times ignoring
    # RuntimeErrors (which are sio very likely to occur). See issues 34970 na 36607 for
    # details.
    i = 0
    wakati Kweli:
        jaribu:
            tasks = list(_all_tasks)
        tatizo RuntimeError:
            i += 1
            ikiwa i >= 1000:
                ashiria
        isipokua:
            koma
    rudisha {t kila t kwenye tasks
            ikiwa futures._get_loop(t) ni loop na sio t.done()}


eleza _all_tasks_compat(loop=Tupu):
    # Different kutoka "all_task()" by rudishaing *all* Tasks, including
    # the completed ones.  Used to implement deprecated "Tasks.all_task()"
    # method.
    ikiwa loop ni Tupu:
        loop = events.get_event_loop()
    # Looping over a WeakSet (_all_tasks) isn't safe kama it can be updated kutoka another
    # thread wakati we do so. Therefore we cast it to list prior to filtering. The list
    # cast itself requires iteration, so we repeat it several times ignoring
    # RuntimeErrors (which are sio very likely to occur). See issues 34970 na 36607 for
    # details.
    i = 0
    wakati Kweli:
        jaribu:
            tasks = list(_all_tasks)
        tatizo RuntimeError:
            i += 1
            ikiwa i >= 1000:
                ashiria
        isipokua:
            koma
    rudisha {t kila t kwenye tasks ikiwa futures._get_loop(t) ni loop}


eleza _set_task_name(task, name):
    ikiwa name ni sio Tupu:
        jaribu:
            set_name = task.set_name
        tatizo AttributeError:
            pita
        isipokua:
            set_name(name)


kundi Task(futures._PyFuture):  # Inherit Python Task implementation
                                # kutoka a Python Future implementation.

    """A coroutine wrapped kwenye a Future."""

    # An agizaant invariant maintained wakati a Task sio done:
    #
    # - Either _fut_waiter ni Tupu, na _step() ni scheduled;
    # - ama _fut_waiter ni some Future, na _step() ni *not* scheduled.
    #
    # The only transition kutoka the latter to the former ni through
    # _wakeup().  When _fut_waiter ni sio Tupu, one of its callbacks
    # must be _wakeup().

    # If Uongo, don't log a message ikiwa the task ni destroyed whereas its
    # status ni still pending
    _log_destroy_pending = Kweli

    @classmethod
    eleza current_task(cls, loop=Tupu):
        """Return the currently running task kwenye an event loop ama Tupu.

        By default the current task kila the current event loop ni rudishaed.

        Tupu ni rudishaed when called haiko kwenye the context of a Task.
        """
        warnings.warn("Task.current_task() ni deprecated since Python 3.7, "
                      "use asyncio.current_task() instead",
                      DeprecationWarning,
                      stacklevel=2)
        ikiwa loop ni Tupu:
            loop = events.get_event_loop()
        rudisha current_task(loop)

    @classmethod
    eleza all_tasks(cls, loop=Tupu):
        """Return a set of all tasks kila an event loop.

        By default all tasks kila the current event loop are rudishaed.
        """
        warnings.warn("Task.all_tasks() ni deprecated since Python 3.7, "
                      "use asyncio.all_tasks() instead",
                      DeprecationWarning,
                      stacklevel=2)
        rudisha _all_tasks_compat(loop)

    eleza __init__(self, coro, *, loop=Tupu, name=Tupu):
        super().__init__(loop=loop)
        ikiwa self._source_traceback:
            toa self._source_traceback[-1]
        ikiwa sio coroutines.iscoroutine(coro):
            # ashiria after Future.__init__(), attrs are required kila __del__
            # prevent logging kila pending task kwenye __del__
            self._log_destroy_pending = Uongo
            ashiria TypeError(f"a coroutine was expected, got {coro!r}")

        ikiwa name ni Tupu:
            self._name = f'Task-{_task_name_counter()}'
        isipokua:
            self._name = str(name)

        self._must_cancel = Uongo
        self._fut_waiter = Tupu
        self._coro = coro
        self._context = contextvars.copy_context()

        self._loop.call_soon(self.__step, context=self._context)
        _register_task(self)

    eleza __del__(self):
        ikiwa self._state == futures._PENDING na self._log_destroy_pending:
            context = {
                'task': self,
                'message': 'Task was destroyed but it ni pending!',
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
        ashiria RuntimeError('Task does sio support set_result operation')

    eleza set_exception(self, exception):
        ashiria RuntimeError('Task does sio support set_exception operation')

    eleza get_stack(self, *, limit=Tupu):
        """Return the list of stack frames kila this task's coroutine.

        If the coroutine ni sio done, this rudishas the stack where it is
        suspended.  If the coroutine has completed successfully ama was
        cancelled, this rudishas an empty list.  If the coroutine was
        terminated by an exception, this rudishas the list of traceback
        frames.

        The frames are always ordered kutoka oldest to newest.

        The optional limit gives the maximum number of frames to
        rudisha; by default all available frames are rudishaed.  Its
        meaning differs depending on whether a stack ama a traceback is
        rudishaed: the newest frames of a stack are rudishaed, but the
        oldest frames of a traceback are rudishaed.  (This matches the
        behavior of the traceback module.)

        For reasons beyond our control, only one stack frame is
        rudishaed kila a suspended coroutine.
        """
        rudisha base_tasks._task_get_stack(self, limit)

    eleza print_stack(self, *, limit=Tupu, file=Tupu):
        """Print the stack ama traceback kila this task's coroutine.

        This produces output similar to that of the traceback module,
        kila the frames retrieved by get_stack().  The limit argument
        ni pitaed to get_stack().  The file argument ni an I/O stream
        to which the output ni written; by default output ni written
        to sys.stderr.
        """
        rudisha base_tasks._task_print_stack(self, limit, file)

    eleza cancel(self):
        """Request that this task cancel itself.

        This arranges kila a CancelledError to be thrown into the
        wrapped coroutine on the next cycle through the event loop.
        The coroutine then has a chance to clean up ama even deny
        the request using try/except/finally.

        Unlike Future.cancel, this does sio guarantee that the
        task will be cancelled: the exception might be caught and
        acted upon, delaying cancellation of the task ama preventing
        cancellation completely.  The task may also rudisha a value or
        ashiria a different exception.

        Immediately after this method ni called, Task.cancelled() will
        sio rudisha Kweli (unless the task was already cancelled).  A
        task will be marked kama cancelled when the wrapped coroutine
        terminates ukijumuisha a CancelledError exception (even ikiwa cancel()
        was sio called).
        """
        self._log_traceback = Uongo
        ikiwa self.done():
            rudisha Uongo
        ikiwa self._fut_waiter ni sio Tupu:
            ikiwa self._fut_waiter.cancel():
                # Leave self._fut_waiter; it may be a Task that
                # catches na ignores the cancellation so we may have
                # to cancel it again later.
                rudisha Kweli
        # It must be the case that self.__step ni already scheduled.
        self._must_cancel = Kweli
        rudisha Kweli

    eleza __step(self, exc=Tupu):
        ikiwa self.done():
            ashiria exceptions.InvalidStateError(
                f'_step(): already done: {self!r}, {exc!r}')
        ikiwa self._must_cancel:
            ikiwa sio isinstance(exc, exceptions.CancelledError):
                exc = exceptions.CancelledError()
            self._must_cancel = Uongo
        coro = self._coro
        self._fut_waiter = Tupu

        _enter_task(self._loop, self)
        # Call either coro.throw(exc) ama coro.send(Tupu).
        jaribu:
            ikiwa exc ni Tupu:
                # We use the `send` method directly, because coroutines
                # don't have `__iter__` na `__next__` methods.
                result = coro.send(Tupu)
            isipokua:
                result = coro.throw(exc)
        tatizo StopIteration kama exc:
            ikiwa self._must_cancel:
                # Task ni cancelled right before coro stops.
                self._must_cancel = Uongo
                super().cancel()
            isipokua:
                super().set_result(exc.value)
        tatizo exceptions.CancelledError:
            super().cancel()  # I.e., Future.cancel(self).
        tatizo (KeyboardInterrupt, SystemExit) kama exc:
            super().set_exception(exc)
            ashiria
        tatizo BaseException kama exc:
            super().set_exception(exc)
        isipokua:
            blocking = getattr(result, '_asyncio_future_blocking', Tupu)
            ikiwa blocking ni sio Tupu:
                # Yielded Future must come kutoka Future.__iter__().
                ikiwa futures._get_loop(result) ni sio self._loop:
                    new_exc = RuntimeError(
                        f'Task {self!r} got Future '
                        f'{result!r} attached to a different loop')
                    self._loop.call_soon(
                        self.__step, new_exc, context=self._context)
                lasivyo blocking:
                    ikiwa result ni self:
                        new_exc = RuntimeError(
                            f'Task cannot await on itself: {self!r}')
                        self._loop.call_soon(
                            self.__step, new_exc, context=self._context)
                    isipokua:
                        result._asyncio_future_blocking = Uongo
                        result.add_done_callback(
                            self.__wakeup, context=self._context)
                        self._fut_waiter = result
                        ikiwa self._must_cancel:
                            ikiwa self._fut_waiter.cancel():
                                self._must_cancel = Uongo
                isipokua:
                    new_exc = RuntimeError(
                        f'tuma was used instead of tuma kutoka '
                        f'in task {self!r} ukijumuisha {result!r}')
                    self._loop.call_soon(
                        self.__step, new_exc, context=self._context)

            lasivyo result ni Tupu:
                # Bare tuma relinquishes control kila one event loop iteration.
                self._loop.call_soon(self.__step, context=self._context)
            lasivyo inspect.isgenerator(result):
                # Yielding a generator ni just wrong.
                new_exc = RuntimeError(
                    f'tuma was used instead of tuma kutoka kila '
                    f'generator kwenye task {self!r} ukijumuisha {result!r}')
                self._loop.call_soon(
                    self.__step, new_exc, context=self._context)
            isipokua:
                # Yielding something isipokua ni an error.
                new_exc = RuntimeError(f'Task got bad tuma: {result!r}')
                self._loop.call_soon(
                    self.__step, new_exc, context=self._context)
        mwishowe:
            _leave_task(self._loop, self)
            self = Tupu  # Needed to koma cycles when an exception occurs.

    eleza __wakeup(self, future):
        jaribu:
            future.result()
        tatizo BaseException kama exc:
            # This may also be a cancellation.
            self.__step(exc)
        isipokua:
            # Don't pita the value of `future.result()` explicitly,
            # kama `Future.__iter__` na `Future.__await__` don't need it.
            # If we call `_step(value, Tupu)` instead of `_step()`,
            # Python eval loop would use `.send(value)` method call,
            # instead of `__next__()`, which ni slower kila futures
            # that rudisha non-generator iterators kutoka their `__iter__`.
            self.__step()
        self = Tupu  # Needed to koma cycles when an exception occurs.


_PyTask = Task


jaribu:
    agiza _asyncio
tatizo ImportError:
    pita
isipokua:
    # _CTask ni needed kila tests.
    Task = _CTask = _asyncio.Task


eleza create_task(coro, *, name=Tupu):
    """Schedule the execution of a coroutine object kwenye a spawn task.

    Return a Task object.
    """
    loop = events.get_running_loop()
    task = loop.create_task(coro)
    _set_task_name(task, name)
    rudisha task


# wait() na as_completed() similar to those kwenye PEP 3148.

FIRST_COMPLETED = concurrent.futures.FIRST_COMPLETED
FIRST_EXCEPTION = concurrent.futures.FIRST_EXCEPTION
ALL_COMPLETED = concurrent.futures.ALL_COMPLETED


async eleza wait(fs, *, loop=Tupu, timeout=Tupu, rudisha_when=ALL_COMPLETED):
    """Wait kila the Futures na coroutines given by fs to complete.

    The sequence futures must sio be empty.

    Coroutines will be wrapped kwenye Tasks.

    Returns two sets of Future: (done, pending).

    Usage:

        done, pending = await asyncio.wait(fs)

    Note: This does sio ashiria TimeoutError! Futures that aren't done
    when the timeout occurs are rudishaed kwenye the second set.
    """
    ikiwa futures.isfuture(fs) ama coroutines.iscoroutine(fs):
        ashiria TypeError(f"expect a list of futures, sio {type(fs).__name__}")
    ikiwa sio fs:
        ashiria ValueError('Set of coroutines/Futures ni empty.')
    ikiwa rudisha_when haiko kwenye (FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED):
        ashiria ValueError(f'Invalid rudisha_when value: {rudisha_when}')

    ikiwa loop ni Tupu:
        loop = events.get_running_loop()
    isipokua:
        warnings.warn("The loop argument ni deprecated since Python 3.8, "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning, stacklevel=2)

    fs = {ensure_future(f, loop=loop) kila f kwenye set(fs)}

    rudisha await _wait(fs, timeout, rudisha_when, loop)


eleza _release_waiter(waiter, *args):
    ikiwa sio waiter.done():
        waiter.set_result(Tupu)


async eleza wait_for(fut, timeout, *, loop=Tupu):
    """Wait kila the single Future ama coroutine to complete, ukijumuisha timeout.

    Coroutine will be wrapped kwenye Task.

    Returns result of the Future ama coroutine.  When a timeout occurs,
    it cancels the task na ashirias TimeoutError.  To avoid the task
    cancellation, wrap it kwenye shield().

    If the wait ni cancelled, the task ni also cancelled.

    This function ni a coroutine.
    """
    ikiwa loop ni Tupu:
        loop = events.get_running_loop()
    isipokua:
        warnings.warn("The loop argument ni deprecated since Python 3.8, "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning, stacklevel=2)

    ikiwa timeout ni Tupu:
        rudisha await fut

    ikiwa timeout <= 0:
        fut = ensure_future(fut, loop=loop)

        ikiwa fut.done():
            rudisha fut.result()

        fut.cancel()
        ashiria exceptions.TimeoutError()

    waiter = loop.create_future()
    timeout_handle = loop.call_later(timeout, _release_waiter, waiter)
    cb = functools.partial(_release_waiter, waiter)

    fut = ensure_future(fut, loop=loop)
    fut.add_done_callback(cb)

    jaribu:
        # wait until the future completes ama the timeout
        jaribu:
            await waiter
        tatizo exceptions.CancelledError:
            fut.remove_done_callback(cb)
            fut.cancel()
            ashiria

        ikiwa fut.done():
            rudisha fut.result()
        isipokua:
            fut.remove_done_callback(cb)
            # We must ensure that the task ni sio running
            # after wait_for() rudishas.
            # See https://bugs.python.org/issue32751
            await _cancel_and_wait(fut, loop=loop)
            ashiria exceptions.TimeoutError()
    mwishowe:
        timeout_handle.cancel()


async eleza _wait(fs, timeout, rudisha_when, loop):
    """Internal helper kila wait().

    The fs argument must be a collection of Futures.
    """
    assert fs, 'Set of Futures ni empty.'
    waiter = loop.create_future()
    timeout_handle = Tupu
    ikiwa timeout ni sio Tupu:
        timeout_handle = loop.call_later(timeout, _release_waiter, waiter)
    counter = len(fs)

    eleza _on_completion(f):
        nonlocal counter
        counter -= 1
        ikiwa (counter <= 0 or
            rudisha_when == FIRST_COMPLETED or
            rudisha_when == FIRST_EXCEPTION na (not f.cancelled() and
                                                f.exception() ni sio Tupu)):
            ikiwa timeout_handle ni sio Tupu:
                timeout_handle.cancel()
            ikiwa sio waiter.done():
                waiter.set_result(Tupu)

    kila f kwenye fs:
        f.add_done_callback(_on_completion)

    jaribu:
        await waiter
    mwishowe:
        ikiwa timeout_handle ni sio Tupu:
            timeout_handle.cancel()
        kila f kwenye fs:
            f.remove_done_callback(_on_completion)

    done, pending = set(), set()
    kila f kwenye fs:
        ikiwa f.done():
            done.add(f)
        isipokua:
            pending.add(f)
    rudisha done, pending


async eleza _cancel_and_wait(fut, loop):
    """Cancel the *fut* future ama task na wait until it completes."""

    waiter = loop.create_future()
    cb = functools.partial(_release_waiter, waiter)
    fut.add_done_callback(cb)

    jaribu:
        fut.cancel()
        # We cannot wait on *fut* directly to make
        # sure _cancel_and_wait itself ni reliably cancellable.
        await waiter
    mwishowe:
        fut.remove_done_callback(cb)


# This ni *not* a @coroutine!  It ni just an iterator (tumaing Futures).
eleza as_completed(fs, *, loop=Tupu, timeout=Tupu):
    """Return an iterator whose values are coroutines.

    When waiting kila the tumaed coroutines you'll get the results (or
    exceptions!) of the original Futures (or coroutines), kwenye the order
    kwenye which na kama soon kama they complete.

    This differs kutoka PEP 3148; the proper way to use this is:

        kila f kwenye as_completed(fs):
            result = await f  # The 'await' may ashiria.
            # Use result.

    If a timeout ni specified, the 'await' will ashiria
    TimeoutError when the timeout occurs before all Futures are done.

    Note: The futures 'f' are sio necessarily members of fs.
    """
    ikiwa futures.isfuture(fs) ama coroutines.iscoroutine(fs):
        ashiria TypeError(f"expect a list of futures, sio {type(fs).__name__}")

    kutoka .queues agiza Queue  # Import here to avoid circular agiza problem.
    done = Queue(loop=loop)

    ikiwa loop ni Tupu:
        loop = events.get_event_loop()
    isipokua:
        warnings.warn("The loop argument ni deprecated since Python 3.8, "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning, stacklevel=2)
    todo = {ensure_future(f, loop=loop) kila f kwenye set(fs)}
    timeout_handle = Tupu

    eleza _on_timeout():
        kila f kwenye todo:
            f.remove_done_callback(_on_completion)
            done.put_nowait(Tupu)  # Queue a dummy value kila _wait_for_one().
        todo.clear()  # Can't do todo.remove(f) kwenye the loop.

    eleza _on_completion(f):
        ikiwa sio todo:
            rudisha  # _on_timeout() was here first.
        todo.remove(f)
        done.put_nowait(f)
        ikiwa sio todo na timeout_handle ni sio Tupu:
            timeout_handle.cancel()

    async eleza _wait_for_one():
        f = await done.get()
        ikiwa f ni Tupu:
            # Dummy value kutoka _on_timeout().
            ashiria exceptions.TimeoutError
        rudisha f.result()  # May ashiria f.exception().

    kila f kwenye todo:
        f.add_done_callback(_on_completion)
    ikiwa todo na timeout ni sio Tupu:
        timeout_handle = loop.call_later(timeout, _on_timeout)
    kila _ kwenye range(len(todo)):
        tuma _wait_for_one()


@types.coroutine
eleza __sleep0():
    """Skip one event loop run cycle.

    This ni a private helper kila 'asyncio.sleep()', used
    when the 'delay' ni set to 0.  It uses a bare 'tuma'
    expression (which Task.__step knows how to handle)
    instead of creating a Future object.
    """
    tuma


async eleza sleep(delay, result=Tupu, *, loop=Tupu):
    """Coroutine that completes after a given time (in seconds)."""
    ikiwa delay <= 0:
        await __sleep0()
        rudisha result

    ikiwa loop ni Tupu:
        loop = events.get_running_loop()
    isipokua:
        warnings.warn("The loop argument ni deprecated since Python 3.8, "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning, stacklevel=2)

    future = loop.create_future()
    h = loop.call_later(delay,
                        futures._set_result_unless_cancelled,
                        future, result)
    jaribu:
        rudisha await future
    mwishowe:
        h.cancel()


eleza ensure_future(coro_or_future, *, loop=Tupu):
    """Wrap a coroutine ama an awaitable kwenye a future.

    If the argument ni a Future, it ni rudishaed directly.
    """
    ikiwa coroutines.iscoroutine(coro_or_future):
        ikiwa loop ni Tupu:
            loop = events.get_event_loop()
        task = loop.create_task(coro_or_future)
        ikiwa task._source_traceback:
            toa task._source_traceback[-1]
        rudisha task
    lasivyo futures.isfuture(coro_or_future):
        ikiwa loop ni sio Tupu na loop ni sio futures._get_loop(coro_or_future):
            ashiria ValueError('The future belongs to a different loop than '
                             'the one specified kama the loop argument')
        rudisha coro_or_future
    lasivyo inspect.isawaitable(coro_or_future):
        rudisha ensure_future(_wrap_awaitable(coro_or_future), loop=loop)
    isipokua:
        ashiria TypeError('An asyncio.Future, a coroutine ama an awaitable ni '
                        'required')


@types.coroutine
eleza _wrap_awaitable(awaitable):
    """Helper kila asyncio.ensure_future().

    Wraps awaitable (an object ukijumuisha __await__) into a coroutine
    that will later be wrapped kwenye a Task by ensure_future().
    """
    rudisha (tuma kutoka awaitable.__await__())

_wrap_awaitable._is_coroutine = _is_coroutine


kundi _GatheringFuture(futures.Future):
    """Helper kila gather().

    This overrides cancel() to cancel all the children na act more
    like Task.cancel(), which doesn't immediately mark itself as
    cancelled.
    """

    eleza __init__(self, children, *, loop=Tupu):
        super().__init__(loop=loop)
        self._children = children
        self._cancel_requested = Uongo

    eleza cancel(self):
        ikiwa self.done():
            rudisha Uongo
        ret = Uongo
        kila child kwenye self._children:
            ikiwa child.cancel():
                ret = Kweli
        ikiwa ret:
            # If any child tasks were actually cancelled, we should
            # propagate the cancellation request regardless of
            # *return_exceptions* argument.  See issue 32684.
            self._cancel_requested = Kweli
        rudisha ret


eleza gather(*coros_or_futures, loop=Tupu, return_exceptions=Uongo):
    """Return a future aggregating results kutoka the given coroutines/futures.

    Coroutines will be wrapped kwenye a future na scheduled kwenye the event
    loop. They will sio necessarily be scheduled kwenye the same order as
    pitaed in.

    All futures must share the same event loop.  If all the tasks are
    done successfully, the rudishaed future's result ni the list of
    results (in the order of the original sequence, sio necessarily
    the order of results arrival).  If *return_exceptions* ni Kweli,
    exceptions kwenye the tasks are treated the same kama successful
    results, na gathered kwenye the result list; otherwise, the first
    ashiriad exception will be immediately propagated to the rudishaed
    future.

    Cancellation: ikiwa the outer Future ni cancelled, all children (that
    have sio completed yet) are also cancelled.  If any child is
    cancelled, this ni treated kama ikiwa it ashiriad CancelledError --
    the outer Future ni *not* cancelled kwenye this case.  (This ni to
    prevent the cancellation of one child to cause other children to
    be cancelled.)
    """
    ikiwa sio coros_or_futures:
        ikiwa loop ni Tupu:
            loop = events.get_event_loop()
        isipokua:
            warnings.warn("The loop argument ni deprecated since Python 3.8, "
                          "and scheduled kila removal kwenye Python 3.10.",
                          DeprecationWarning, stacklevel=2)
        outer = loop.create_future()
        outer.set_result([])
        rudisha outer

    eleza _done_callback(fut):
        nonlocal nfinished
        nfinished += 1

        ikiwa outer.done():
            ikiwa sio fut.cancelled():
                # Mark exception retrieved.
                fut.exception()
            rudisha

        ikiwa sio return_exceptions:
            ikiwa fut.cancelled():
                # Check ikiwa 'fut' ni cancelled first, as
                # 'fut.exception()' will *ashiria* a CancelledError
                # instead of rudishaing it.
                exc = exceptions.CancelledError()
                outer.set_exception(exc)
                rudisha
            isipokua:
                exc = fut.exception()
                ikiwa exc ni sio Tupu:
                    outer.set_exception(exc)
                    rudisha

        ikiwa nfinished == nfuts:
            # All futures are done; create a list of results
            # na set it to the 'outer' future.
            results = []

            kila fut kwenye children:
                ikiwa fut.cancelled():
                    # Check ikiwa 'fut' ni cancelled first, as
                    # 'fut.exception()' will *ashiria* a CancelledError
                    # instead of rudishaing it.
                    res = exceptions.CancelledError()
                isipokua:
                    res = fut.exception()
                    ikiwa res ni Tupu:
                        res = fut.result()
                results.append(res)

            ikiwa outer._cancel_requested:
                # If gather ni being cancelled we must propagate the
                # cancellation regardless of *return_exceptions* argument.
                # See issue 32684.
                outer.set_exception(exceptions.CancelledError())
            isipokua:
                outer.set_result(results)

    arg_to_fut = {}
    children = []
    nfuts = 0
    nfinished = 0
    kila arg kwenye coros_or_futures:
        ikiwa arg haiko kwenye arg_to_fut:
            fut = ensure_future(arg, loop=loop)
            ikiwa loop ni Tupu:
                loop = futures._get_loop(fut)
            ikiwa fut ni sio arg:
                # 'arg' was sio a Future, therefore, 'fut' ni a new
                # Future created specifically kila 'arg'.  Since the caller
                # can't control it, disable the "destroy pending task"
                # warning.
                fut._log_destroy_pending = Uongo

            nfuts += 1
            arg_to_fut[arg] = fut
            fut.add_done_callback(_done_callback)

        isipokua:
            # There's a duplicate Future object kwenye coros_or_futures.
            fut = arg_to_fut[arg]

        children.append(fut)

    outer = _GatheringFuture(children, loop=loop)
    rudisha outer


eleza shield(arg, *, loop=Tupu):
    """Wait kila a future, shielding it kutoka cancellation.

    The statement

        res = await shield(something())

    ni exactly equivalent to the statement

        res = await something()

    *except* that ikiwa the coroutine containing it ni cancelled, the
    task running kwenye something() ni sio cancelled.  From the POV of
    something(), the cancellation did sio happen.  But its caller is
    still cancelled, so the tuma-kutoka expression still ashirias
    CancelledError.  Note: If something() ni cancelled by other means
    this will still cancel shield().

    If you want to completely ignore cancellation (not recommended)
    you can combine shield() ukijumuisha a try/tatizo clause, kama follows:

        jaribu:
            res = await shield(something())
        tatizo CancelledError:
            res = Tupu
    """
    ikiwa loop ni sio Tupu:
        warnings.warn("The loop argument ni deprecated since Python 3.8, "
                      "and scheduled kila removal kwenye Python 3.10.",
                      DeprecationWarning, stacklevel=2)
    inner = ensure_future(arg, loop=loop)
    ikiwa inner.done():
        # Shortcut.
        rudisha inner
    loop = futures._get_loop(inner)
    outer = loop.create_future()

    eleza _inner_done_callback(inner):
        ikiwa outer.cancelled():
            ikiwa sio inner.cancelled():
                # Mark inner's result kama retrieved.
                inner.exception()
            rudisha

        ikiwa inner.cancelled():
            outer.cancel()
        isipokua:
            exc = inner.exception()
            ikiwa exc ni sio Tupu:
                outer.set_exception(exc)
            isipokua:
                outer.set_result(inner.result())


    eleza _outer_done_callback(outer):
        ikiwa sio inner.done():
            inner.remove_done_callback(_inner_done_callback)

    inner.add_done_callback(_inner_done_callback)
    outer.add_done_callback(_outer_done_callback)
    rudisha outer


eleza run_coroutine_threadsafe(coro, loop):
    """Submit a coroutine object to a given event loop.

    Return a concurrent.futures.Future to access the result.
    """
    ikiwa sio coroutines.iscoroutine(coro):
        ashiria TypeError('A coroutine object ni required')
    future = concurrent.futures.Future()

    eleza callback():
        jaribu:
            futures._chain_future(ensure_future(coro, loop=loop), future)
        tatizo (SystemExit, KeyboardInterrupt):
            ashiria
        tatizo BaseException kama exc:
            ikiwa future.set_running_or_notify_cancel():
                future.set_exception(exc)
            ashiria

    loop.call_soon_threadsafe(callback)
    rudisha future


# WeakSet containing all alive tasks.
_all_tasks = weakref.WeakSet()

# Dictionary containing tasks that are currently active in
# all running event loops.  {EventLoop: Task}
_current_tasks = {}


eleza _register_task(task):
    """Register a new task kwenye asyncio kama executed by loop."""
    _all_tasks.add(task)


eleza _enter_task(loop, task):
    current_task = _current_tasks.get(loop)
    ikiwa current_task ni sio Tupu:
        ashiria RuntimeError(f"Cannot enter into task {task!r} wakati another "
                           f"task {current_task!r} ni being executed.")
    _current_tasks[loop] = task


eleza _leave_task(loop, task):
    current_task = _current_tasks.get(loop)
    ikiwa current_task ni sio task:
        ashiria RuntimeError(f"Leaving task {task!r} does sio match "
                           f"the current task {current_task!r}.")
    toa _current_tasks[loop]


eleza _unregister_task(task):
    """Unregister a task."""
    _all_tasks.discard(task)


_py_register_task = _register_task
_py_unregister_task = _unregister_task
_py_enter_task = _enter_task
_py_leave_task = _leave_task


jaribu:
    kutoka _asyncio agiza (_register_task, _unregister_task,
                          _enter_task, _leave_task,
                          _all_tasks, _current_tasks)
tatizo ImportError:
    pita
isipokua:
    _c_register_task = _register_task
    _c_unregister_task = _unregister_task
    _c_enter_task = _enter_task
    _c_leave_task = _leave_task
