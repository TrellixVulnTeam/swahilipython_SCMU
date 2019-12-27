agiza asyncio
kutoka contextlib agiza asynccontextmanager, AbstractAsyncContextManager, AsyncExitStack
agiza functools
kutoka test agiza support
agiza unittest

kutoka test.test_contextlib agiza TestBaseExitStack


eleza _async_test(func):
    """Decorator to turn an async function into a test case."""
    @functools.wraps(func)
    eleza wrapper(*args, **kwargs):
        coro = func(*args, **kwargs)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            rudisha loop.run_until_complete(coro)
        finally:
            loop.close()
            asyncio.set_event_loop_policy(None)
    rudisha wrapper


kundi TestAbstractAsyncContextManager(unittest.TestCase):

    @_async_test
    async eleza test_enter(self):
        kundi DefaultEnter(AbstractAsyncContextManager):
            async eleza __aexit__(self, *args):
                await super().__aexit__(*args)

        manager = DefaultEnter()
        self.assertIs(await manager.__aenter__(), manager)

        async with manager as context:
            self.assertIs(manager, context)

    @_async_test
    async eleza test_async_gen_propagates_generator_exit(self):
        # A regression test for https://bugs.python.org/issue33786.

        @asynccontextmanager
        async eleza ctx():
            yield

        async eleza gen():
            async with ctx():
                yield 11

        ret = []
        exc = ValueError(22)
        with self.assertRaises(ValueError):
            async with ctx():
                async for val in gen():
                    ret.append(val)
                    raise exc

        self.assertEqual(ret, [11])

    eleza test_exit_is_abstract(self):
        kundi MissingAexit(AbstractAsyncContextManager):
            pass

        with self.assertRaises(TypeError):
            MissingAexit()

    eleza test_structural_subclassing(self):
        kundi ManagerFromScratch:
            async eleza __aenter__(self):
                rudisha self
            async eleza __aexit__(self, exc_type, exc_value, traceback):
                rudisha None

        self.assertTrue(issubclass(ManagerFromScratch, AbstractAsyncContextManager))

        kundi DefaultEnter(AbstractAsyncContextManager):
            async eleza __aexit__(self, *args):
                await super().__aexit__(*args)

        self.assertTrue(issubclass(DefaultEnter, AbstractAsyncContextManager))

        kundi NoneAenter(ManagerFromScratch):
            __aenter__ = None

        self.assertFalse(issubclass(NoneAenter, AbstractAsyncContextManager))

        kundi NoneAexit(ManagerFromScratch):
            __aexit__ = None

        self.assertFalse(issubclass(NoneAexit, AbstractAsyncContextManager))


kundi AsyncContextManagerTestCase(unittest.TestCase):

    @_async_test
    async eleza test_contextmanager_plain(self):
        state = []
        @asynccontextmanager
        async eleza woohoo():
            state.append(1)
            yield 42
            state.append(999)
        async with woohoo() as x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
        self.assertEqual(state, [1, 42, 999])

    @_async_test
    async eleza test_contextmanager_finally(self):
        state = []
        @asynccontextmanager
        async eleza woohoo():
            state.append(1)
            try:
                yield 42
            finally:
                state.append(999)
        with self.assertRaises(ZeroDivisionError):
            async with woohoo() as x:
                self.assertEqual(state, [1])
                self.assertEqual(x, 42)
                state.append(x)
                raise ZeroDivisionError()
        self.assertEqual(state, [1, 42, 999])

    @_async_test
    async eleza test_contextmanager_no_reraise(self):
        @asynccontextmanager
        async eleza whee():
            yield
        ctx = whee()
        await ctx.__aenter__()
        # Calling __aexit__ should not result in an exception
        self.assertFalse(await ctx.__aexit__(TypeError, TypeError("foo"), None))

    @_async_test
    async eleza test_contextmanager_trap_yield_after_throw(self):
        @asynccontextmanager
        async eleza whoo():
            try:
                yield
            except:
                yield
        ctx = whoo()
        await ctx.__aenter__()
        with self.assertRaises(RuntimeError):
            await ctx.__aexit__(TypeError, TypeError('foo'), None)

    @_async_test
    async eleza test_contextmanager_trap_no_yield(self):
        @asynccontextmanager
        async eleza whoo():
            ikiwa False:
                yield
        ctx = whoo()
        with self.assertRaises(RuntimeError):
            await ctx.__aenter__()

    @_async_test
    async eleza test_contextmanager_trap_second_yield(self):
        @asynccontextmanager
        async eleza whoo():
            yield
            yield
        ctx = whoo()
        await ctx.__aenter__()
        with self.assertRaises(RuntimeError):
            await ctx.__aexit__(None, None, None)

    @_async_test
    async eleza test_contextmanager_non_normalised(self):
        @asynccontextmanager
        async eleza whoo():
            try:
                yield
            except RuntimeError:
                raise SyntaxError

        ctx = whoo()
        await ctx.__aenter__()
        with self.assertRaises(SyntaxError):
            await ctx.__aexit__(RuntimeError, None, None)

    @_async_test
    async eleza test_contextmanager_except(self):
        state = []
        @asynccontextmanager
        async eleza woohoo():
            state.append(1)
            try:
                yield 42
            except ZeroDivisionError as e:
                state.append(e.args[0])
                self.assertEqual(state, [1, 42, 999])
        async with woohoo() as x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
            raise ZeroDivisionError(999)
        self.assertEqual(state, [1, 42, 999])

    @_async_test
    async eleza test_contextmanager_except_stopiter(self):
        @asynccontextmanager
        async eleza woohoo():
            yield

        for stop_exc in (StopIteration('spam'), StopAsyncIteration('ham')):
            with self.subTest(type=type(stop_exc)):
                try:
                    async with woohoo():
                        raise stop_exc
                except Exception as ex:
                    self.assertIs(ex, stop_exc)
                else:
                    self.fail(f'{stop_exc} was suppressed')

    @_async_test
    async eleza test_contextmanager_wrap_runtimeerror(self):
        @asynccontextmanager
        async eleza woohoo():
            try:
                yield
            except Exception as exc:
                raise RuntimeError(f'caught {exc}') kutoka exc

        with self.assertRaises(RuntimeError):
            async with woohoo():
                1 / 0

        # If the context manager wrapped StopAsyncIteration in a RuntimeError,
        # we also unwrap it, because we can't tell whether the wrapping was
        # done by the generator machinery or by the generator itself.
        with self.assertRaises(StopAsyncIteration):
            async with woohoo():
                raise StopAsyncIteration

    eleza _create_contextmanager_attribs(self):
        eleza attribs(**kw):
            eleza decorate(func):
                for k,v in kw.items():
                    setattr(func,k,v)
                rudisha func
            rudisha decorate
        @asynccontextmanager
        @attribs(foo='bar')
        async eleza baz(spam):
            """Whee!"""
            yield
        rudisha baz

    eleza test_contextmanager_attribs(self):
        baz = self._create_contextmanager_attribs()
        self.assertEqual(baz.__name__,'baz')
        self.assertEqual(baz.foo, 'bar')

    @support.requires_docstrings
    eleza test_contextmanager_doc_attrib(self):
        baz = self._create_contextmanager_attribs()
        self.assertEqual(baz.__doc__, "Whee!")

    @support.requires_docstrings
    @_async_test
    async eleza test_instance_docstring_given_cm_docstring(self):
        baz = self._create_contextmanager_attribs()(None)
        self.assertEqual(baz.__doc__, "Whee!")
        async with baz:
            pass  # suppress warning

    @_async_test
    async eleza test_keywords(self):
        # Ensure no keyword arguments are inhibited
        @asynccontextmanager
        async eleza woohoo(self, func, args, kwds):
            yield (self, func, args, kwds)
        async with woohoo(self=11, func=22, args=33, kwds=44) as target:
            self.assertEqual(target, (11, 22, 33, 44))


kundi TestAsyncExitStack(TestBaseExitStack, unittest.TestCase):
    kundi SyncAsyncExitStack(AsyncExitStack):
        @staticmethod
        eleza run_coroutine(coro):
            loop = asyncio.get_event_loop()

            f = asyncio.ensure_future(coro)
            f.add_done_callback(lambda f: loop.stop())
            loop.run_forever()

            exc = f.exception()

            ikiwa not exc:
                rudisha f.result()
            else:
                context = exc.__context__

                try:
                    raise exc
                except:
                    exc.__context__ = context
                    raise exc

        eleza close(self):
            rudisha self.run_coroutine(self.aclose())

        eleza __enter__(self):
            rudisha self.run_coroutine(self.__aenter__())

        eleza __exit__(self, *exc_details):
            rudisha self.run_coroutine(self.__aexit__(*exc_details))

    exit_stack = SyncAsyncExitStack

    eleza setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.addCleanup(self.loop.close)
        self.addCleanup(asyncio.set_event_loop_policy, None)

    @_async_test
    async eleza test_async_callback(self):
        expected = [
            ((), {}),
            ((1,), {}),
            ((1,2), {}),
            ((), dict(example=1)),
            ((1,), dict(example=1)),
            ((1,2), dict(example=1)),
        ]
        result = []
        async eleza _exit(*args, **kwds):
            """Test metadata propagation"""
            result.append((args, kwds))

        async with AsyncExitStack() as stack:
            for args, kwds in reversed(expected):
                ikiwa args and kwds:
                    f = stack.push_async_callback(_exit, *args, **kwds)
                elikiwa args:
                    f = stack.push_async_callback(_exit, *args)
                elikiwa kwds:
                    f = stack.push_async_callback(_exit, **kwds)
                else:
                    f = stack.push_async_callback(_exit)
                self.assertIs(f, _exit)
            for wrapper in stack._exit_callbacks:
                self.assertIs(wrapper[1].__wrapped__, _exit)
                self.assertNotEqual(wrapper[1].__name__, _exit.__name__)
                self.assertIsNone(wrapper[1].__doc__, _exit.__doc__)

        self.assertEqual(result, expected)

        result = []
        async with AsyncExitStack() as stack:
            with self.assertRaises(TypeError):
                stack.push_async_callback(arg=1)
            with self.assertRaises(TypeError):
                self.exit_stack.push_async_callback(arg=2)
            with self.assertWarns(DeprecationWarning):
                stack.push_async_callback(callback=_exit, arg=3)
        self.assertEqual(result, [((), {'arg': 3})])

    @_async_test
    async eleza test_async_push(self):
        exc_raised = ZeroDivisionError
        async eleza _expect_exc(exc_type, exc, exc_tb):
            self.assertIs(exc_type, exc_raised)
        async eleza _suppress_exc(*exc_details):
            rudisha True
        async eleza _expect_ok(exc_type, exc, exc_tb):
            self.assertIsNone(exc_type)
            self.assertIsNone(exc)
            self.assertIsNone(exc_tb)
        kundi ExitCM(object):
            eleza __init__(self, check_exc):
                self.check_exc = check_exc
            async eleza __aenter__(self):
                self.fail("Should not be called!")
            async eleza __aexit__(self, *exc_details):
                await self.check_exc(*exc_details)

        async with self.exit_stack() as stack:
            stack.push_async_exit(_expect_ok)
            self.assertIs(stack._exit_callbacks[-1][1], _expect_ok)
            cm = ExitCM(_expect_ok)
            stack.push_async_exit(cm)
            self.assertIs(stack._exit_callbacks[-1][1].__self__, cm)
            stack.push_async_exit(_suppress_exc)
            self.assertIs(stack._exit_callbacks[-1][1], _suppress_exc)
            cm = ExitCM(_expect_exc)
            stack.push_async_exit(cm)
            self.assertIs(stack._exit_callbacks[-1][1].__self__, cm)
            stack.push_async_exit(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1][1], _expect_exc)
            stack.push_async_exit(_expect_exc)
            self.assertIs(stack._exit_callbacks[-1][1], _expect_exc)
            1/0

    @_async_test
    async eleza test_async_enter_context(self):
        kundi TestCM(object):
            async eleza __aenter__(self):
                result.append(1)
            async eleza __aexit__(self, *exc_details):
                result.append(3)

        result = []
        cm = TestCM()

        async with AsyncExitStack() as stack:
            @stack.push_async_callback  # Registered first => cleaned up last
            async eleza _exit():
                result.append(4)
            self.assertIsNotNone(_exit)
            await stack.enter_async_context(cm)
            self.assertIs(stack._exit_callbacks[-1][1].__self__, cm)
            result.append(2)

        self.assertEqual(result, [1, 2, 3, 4])

    @_async_test
    async eleza test_async_exit_exception_chaining(self):
        # Ensure exception chaining matches the reference behaviour
        async eleza raise_exc(exc):
            raise exc

        saved_details = None
        async eleza suppress_exc(*exc_details):
            nonlocal saved_details
            saved_details = exc_details
            rudisha True

        try:
            async with self.exit_stack() as stack:
                stack.push_async_callback(raise_exc, IndexError)
                stack.push_async_callback(raise_exc, KeyError)
                stack.push_async_callback(raise_exc, AttributeError)
                stack.push_async_exit(suppress_exc)
                stack.push_async_callback(raise_exc, ValueError)
                1 / 0
        except IndexError as exc:
            self.assertIsInstance(exc.__context__, KeyError)
            self.assertIsInstance(exc.__context__.__context__, AttributeError)
            # Inner exceptions were suppressed
            self.assertIsNone(exc.__context__.__context__.__context__)
        else:
            self.fail("Expected IndexError, but no exception was raised")
        # Check the inner exceptions
        inner_exc = saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)


ikiwa __name__ == '__main__':
    unittest.main()
