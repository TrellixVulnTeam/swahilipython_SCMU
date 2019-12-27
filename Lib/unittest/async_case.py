agiza asyncio
agiza inspect

kutoka .case agiza TestCase



kundi IsolatedAsyncioTestCase(TestCase):
    # Names intentionally have a long prefix
    # to reduce a chance of clashing with user-defined attributes
    # kutoka inherited test case
    #
    # The kundi doesn't call loop.run_until_complete(self.setUp()) and family
    # but uses a different approach:
    # 1. create a long-running task that reads self.setUp()
    #    awaitable kutoka queue along with a future
    # 2. await the awaitable object passing in and set the result
    #    into the future object
    # 3. Outer code puts the awaitable and the future object into a queue
    #    with waiting for the future
    # The trick is necessary because every run_until_complete() call
    # creates a new task with embedded ContextVar context.
    # To share contextvars between setUp(), test and tearDown() we need to execute
    # them inside the same task.

    # Note: the test case modifies event loop policy ikiwa the policy was not instantiated
    # yet.
    # asyncio.get_event_loop_policy() creates a default policy on demand but never
    # returns None
    # I believe this is not an issue in user level tests but python itself for testing
    # should reset a policy in every test module
    # by calling asyncio.set_event_loop_policy(None) in tearDownModule()

    eleza __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self._asyncioTestLoop = None
        self._asyncioCallsQueue = None

    async eleza asyncSetUp(self):
        pass

    async eleza asyncTearDown(self):
        pass

    eleza addAsyncCleanup(self, func, /, *args, **kwargs):
        # A trivial trampoline to addCleanup()
        # the function exists because it has a different semantics
        # and signature:
        # addCleanup() accepts regular functions
        # but addAsyncCleanup() accepts coroutines
        #
        # We intentionally don't add inspect.iscoroutinefunction() check
        # for func argument because there is no way
        # to check for async function reliably:
        # 1. It can be "async eleza func()" iself
        # 2. Class can implement "async eleza __call__()" method
        # 3. Regular "eleza func()" that returns awaitable object
        self.addCleanup(*(func, *args), **kwargs)

    eleza _callSetUp(self):
        self.setUp()
        self._callAsync(self.asyncSetUp)

    eleza _callTestMethod(self, method):
        self._callMaybeAsync(method)

    eleza _callTearDown(self):
        self._callAsync(self.asyncTearDown)
        self.tearDown()

    eleza _callCleanup(self, function, *args, **kwargs):
        self._callMaybeAsync(function, *args, **kwargs)

    eleza _callAsync(self, func, /, *args, **kwargs):
        assert self._asyncioTestLoop is not None
        ret = func(*args, **kwargs)
        assert inspect.isawaitable(ret)
        fut = self._asyncioTestLoop.create_future()
        self._asyncioCallsQueue.put_nowait((fut, ret))
        rudisha self._asyncioTestLoop.run_until_complete(fut)

    eleza _callMaybeAsync(self, func, /, *args, **kwargs):
        assert self._asyncioTestLoop is not None
        ret = func(*args, **kwargs)
        ikiwa inspect.isawaitable(ret):
            fut = self._asyncioTestLoop.create_future()
            self._asyncioCallsQueue.put_nowait((fut, ret))
            rudisha self._asyncioTestLoop.run_until_complete(fut)
        else:
            rudisha ret

    async eleza _asyncioLoopRunner(self, fut):
        self._asyncioCallsQueue = queue = asyncio.Queue()
        fut.set_result(None)
        while True:
            query = await queue.get()
            queue.task_done()
            ikiwa query is None:
                return
            fut, awaitable = query
            try:
                ret = await awaitable
                ikiwa not fut.cancelled():
                    fut.set_result(ret)
            except asyncio.CancelledError:
                raise
            except Exception as ex:
                ikiwa not fut.cancelled():
                    fut.set_exception(ex)

    eleza _setupAsyncioLoop(self):
        assert self._asyncioTestLoop is None
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(True)
        self._asyncioTestLoop = loop
        fut = loop.create_future()
        self._asyncioCallsTask = loop.create_task(self._asyncioLoopRunner(fut))
        loop.run_until_complete(fut)

    eleza _tearDownAsyncioLoop(self):
        assert self._asyncioTestLoop is not None
        loop = self._asyncioTestLoop
        self._asyncioTestLoop = None
        self._asyncioCallsQueue.put_nowait(None)
        loop.run_until_complete(self._asyncioCallsQueue.join())

        try:
            # cancel all tasks
            to_cancel = asyncio.all_tasks(loop)
            ikiwa not to_cancel:
                return

            for task in to_cancel:
                task.cancel()

            loop.run_until_complete(
                asyncio.gather(*to_cancel, loop=loop, return_exceptions=True))

            for task in to_cancel:
                ikiwa task.cancelled():
                    continue
                ikiwa task.exception() is not None:
                    loop.call_exception_handler({
                        'message': 'unhandled exception during test shutdown',
                        'exception': task.exception(),
                        'task': task,
                    })
            # shutdown asyncgens
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()

    eleza run(self, result=None):
        self._setupAsyncioLoop()
        try:
            rudisha super().run(result)
        finally:
            self._tearDownAsyncioLoop()
