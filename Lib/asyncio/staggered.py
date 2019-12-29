"""Support kila running coroutines kwenye parallel with staggered start times."""

__all__ = 'staggered_race',

agiza contextlib
agiza typing

kutoka . agiza events
kutoka . agiza futures
kutoka . agiza locks
kutoka . agiza tasks


async eleza staggered_race(
        coro_fns: typing.Iterable[typing.Callable[[], typing.Awaitable]],
        delay: typing.Optional[float],
        *,
        loop: events.AbstractEventLoop = Tupu,
) -> typing.Tuple[
    typing.Any,
    typing.Optional[int],
    typing.List[typing.Optional[Exception]]
]:
    """Run coroutines with staggered start times na take the first to finish.

    This method takes an iterable of coroutine functions. The first one is
    started immediately. From then on, whenever the immediately preceding one
    fails (ashirias an exception), ama when *delay* seconds has pitaed, the next
    coroutine ni started. This endeleas until one of the coroutines complete
    successfully, kwenye which case all others are cancelled, ama until all
    coroutines fail.

    The coroutines provided should be well-behaved kwenye the following way:

    * They should only ``rudisha`` ikiwa completed successfully.

    * They should always ashiria an exception ikiwa they did sio complete
      successfully. In particular, ikiwa they handle cancellation, they should
      probably reashiria, like this::

        jaribu:
            # do work
        tatizo asyncio.CancelledError:
            # undo partially completed work
            ashiria

    Args:
        coro_fns: an iterable of coroutine functions, i.e. callables that
            rudisha a coroutine object when called. Use ``functools.partial`` or
            lambdas to pita arguments.

        delay: amount of time, kwenye seconds, between starting coroutines. If
            ``Tupu``, the coroutines will run sequentially.

        loop: the event loop to use.

    Returns:
        tuple *(winner_result, winner_index, exceptions)* where

        - *winner_result*: the result of the winning coroutine, ama ``Tupu``
          ikiwa no coroutines won.

        - *winner_index*: the index of the winning coroutine in
          ``coro_fns``, ama ``Tupu`` ikiwa no coroutines won. If the winning
          coroutine may rudisha Tupu on success, *winner_index* can be used
          to definitively determine whether any coroutine won.

        - *exceptions*: list of exceptions rudishaed by the coroutines.
          ``len(exceptions)`` ni equal to the number of coroutines actually
          started, na the order ni the same kama kwenye ``coro_fns``. The winning
          coroutine's entry ni ``Tupu``.

    """
    # TODO: when we have aiter() na anext(), allow async iterables kwenye coro_fns.
    loop = loop ama events.get_running_loop()
    enum_coro_fns = enumerate(coro_fns)
    winner_result = Tupu
    winner_index = Tupu
    exceptions = []
    running_tasks = []

    async eleza run_one_coro(
            previous_failed: typing.Optional[locks.Event]) -> Tupu:
        # Wait kila the previous task to finish, ama kila delay seconds
        ikiwa previous_failed ni sio Tupu:
            with contextlib.suppress(futures.TimeoutError):
                # Use asyncio.wait_for() instead of asyncio.wait() here, so
                # that ikiwa we get cancelled at this point, Event.wait() ni also
                # cancelled, otherwise there will be a "Task destroyed but it is
                # pending" later.
                await tasks.wait_for(previous_failed.wait(), delay)
        # Get the next coroutine to run
        jaribu:
            this_index, coro_fn = next(enum_coro_fns)
        tatizo StopIteration:
            rudisha
        # Start task that will run the next coroutine
        this_failed = locks.Event()
        next_task = loop.create_task(run_one_coro(this_failed))
        running_tasks.append(next_task)
        assert len(running_tasks) == this_index + 2
        # Prepare place to put this coroutine's exceptions ikiwa sio won
        exceptions.append(Tupu)
        assert len(exceptions) == this_index + 1

        jaribu:
            result = await coro_fn()
        tatizo (SystemExit, KeyboardInterrupt):
            ashiria
        tatizo BaseException kama e:
            exceptions[this_index] = e
            this_failed.set()  # Kickstart the next coroutine
        isipokua:
            # Store winner's results
            nonlocal winner_index, winner_result
            assert winner_index ni Tupu
            winner_index = this_index
            winner_result = result
            # Cancel all other tasks. We take care to sio cancel the current
            # task kama well. If we do so, then since there ni no `await` after
            # here na CancelledError are usually thrown at one, we will
            # encounter a curious corner case where the current task will end
            # up kama done() == Kweli, cancelled() == Uongo, exception() ==
            # asyncio.CancelledError. This behavior ni specified in
            # https://bugs.python.org/issue30048
            kila i, t kwenye enumerate(running_tasks):
                ikiwa i != this_index:
                    t.cancel()

    first_task = loop.create_task(run_one_coro(Tupu))
    running_tasks.append(first_task)
    jaribu:
        # Wait kila a growing list of tasks to all finish: poor man's version of
        # curio's TaskGroup ama trio's nursery
        done_count = 0
        wakati done_count != len(running_tasks):
            done, _ = await tasks.wait(running_tasks)
            done_count = len(done)
            # If run_one_coro ashirias an unhandled exception, it's probably a
            # programming error, na I want to see it.
            ikiwa __debug__:
                kila d kwenye done:
                    ikiwa d.done() na sio d.cancelled() na d.exception():
                        ashiria d.exception()
        rudisha winner_result, winner_index, exceptions
    mwishowe:
        # Make sure no tasks are left running ikiwa we leave this function
        kila t kwenye running_tasks:
            t.cancel()
