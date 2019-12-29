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
        jaribu:
            rudisha loop.run_until_complete(coro)
        mwishowe:
            loop.close()
            asyncio.set_event_loop_policy(Tupu)
    rudisha wrapper


kundi TestAbstractAsyncContextManager(unittest.TestCase):

    @_async_test
    async eleza test_enter(self):
        kundi DefaultEnter(AbstractAsyncContextManager):
            async eleza __aexit__(self, *args):
                await super().__aexit__(*args)

        manager = DefaultEnter()
        self.assertIs(await manager.__aenter__(), manager)

        async ukijumuisha manager kama context:
            self.assertIs(manager, context)

    @_async_test
    async eleza test_async_gen_propagates_generator_exit(self):
        # A regression test kila https://bugs.python.org/issue33786.

        @asynccontextmanager
        async eleza ctx():
            tuma

        async eleza gen():
            async ukijumuisha ctx():
                tuma 11

        ret = []
        exc = ValueError(22)
        ukijumuisha self.assertRaises(ValueError):
            async ukijumuisha ctx():
                async kila val kwenye gen():
                    ret.append(val)
                    ashiria exc

        self.assertEqual(ret, [11])

    eleza test_exit_is_abstract(self):
        kundi MissingAexit(AbstractAsyncContextManager):
            pita

        ukijumuisha self.assertRaises(TypeError):
            MissingAexit()

    eleza test_structural_subclassing(self):
        kundi ManagerFromScratch:
            async eleza __aenter__(self):
                rudisha self
            async eleza __aexit__(self, exc_type, exc_value, traceback):
                rudisha Tupu

        self.assertKweli(issubclass(ManagerFromScratch, AbstractAsyncContextManager))

        kundi DefaultEnter(AbstractAsyncContextManager):
            async eleza __aexit__(self, *args):
                await super().__aexit__(*args)

        self.assertKweli(issubclass(DefaultEnter, AbstractAsyncContextManager))

        kundi TupuAenter(ManagerFromScratch):
            __aenter__ = Tupu

        self.assertUongo(issubclass(TupuAenter, AbstractAsyncContextManager))

        kundi TupuAexit(ManagerFromScratch):
            __aexit__ = Tupu

        self.assertUongo(issubclass(TupuAexit, AbstractAsyncContextManager))


kundi AsyncContextManagerTestCase(unittest.TestCase):

    @_async_test
    async eleza test_contextmanager_plain(self):
        state = []
        @asynccontextmanager
        async eleza woohoo():
            state.append(1)
            tuma 42
            state.append(999)
        async ukijumuisha woohoo() kama x:
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
            jaribu:
                tuma 42
            mwishowe:
                state.append(999)
        ukijumuisha self.assertRaises(ZeroDivisionError):
            async ukijumuisha woohoo() kama x:
                self.assertEqual(state, [1])
                self.assertEqual(x, 42)
                state.append(x)
                ashiria ZeroDivisionError()
        self.assertEqual(state, [1, 42, 999])

    @_async_test
    async eleza test_contextmanager_no_reashiria(self):
        @asynccontextmanager
        async eleza whee():
            tuma
        ctx = whee()
        await ctx.__aenter__()
        # Calling __aexit__ should sio result kwenye an exception
        self.assertUongo(await ctx.__aexit__(TypeError, TypeError("foo"), Tupu))

    @_async_test
    async eleza test_contextmanager_trap_tuma_after_throw(self):
        @asynccontextmanager
        async eleza whoo():
            jaribu:
                tuma
            except:
                tuma
        ctx = whoo()
        await ctx.__aenter__()
        ukijumuisha self.assertRaises(RuntimeError):
            await ctx.__aexit__(TypeError, TypeError('foo'), Tupu)

    @_async_test
    async eleza test_contextmanager_trap_no_tuma(self):
        @asynccontextmanager
        async eleza whoo():
            ikiwa Uongo:
                tuma
        ctx = whoo()
        ukijumuisha self.assertRaises(RuntimeError):
            await ctx.__aenter__()

    @_async_test
    async eleza test_contextmanager_trap_second_tuma(self):
        @asynccontextmanager
        async eleza whoo():
            tuma
            tuma
        ctx = whoo()
        await ctx.__aenter__()
        ukijumuisha self.assertRaises(RuntimeError):
            await ctx.__aexit__(Tupu, Tupu, Tupu)

    @_async_test
    async eleza test_contextmanager_non_normalised(self):
        @asynccontextmanager
        async eleza whoo():
            jaribu:
                tuma
            tatizo RuntimeError:
                ashiria SyntaxError

        ctx = whoo()
        await ctx.__aenter__()
        ukijumuisha self.assertRaises(SyntaxError):
            await ctx.__aexit__(RuntimeError, Tupu, Tupu)

    @_async_test
    async eleza test_contextmanager_except(self):
        state = []
        @asynccontextmanager
        async eleza woohoo():
            state.append(1)
            jaribu:
                tuma 42
            tatizo ZeroDivisionError kama e:
                state.append(e.args[0])
                self.assertEqual(state, [1, 42, 999])
        async ukijumuisha woohoo() kama x:
            self.assertEqual(state, [1])
            self.assertEqual(x, 42)
            state.append(x)
            ashiria ZeroDivisionError(999)
        self.assertEqual(state, [1, 42, 999])

    @_async_test
    async eleza test_contextmanager_except_stopiter(self):
        @asynccontextmanager
        async eleza woohoo():
            tuma

        kila stop_exc kwenye (StopIteration('spam'), StopAsyncIteration('ham')):
            ukijumuisha self.subTest(type=type(stop_exc)):
                jaribu:
                    async ukijumuisha woohoo():
                        ashiria stop_exc
                tatizo Exception kama ex:
                    self.assertIs(ex, stop_exc)
                isipokua:
                    self.fail(f'{stop_exc} was suppressed')

    @_async_test
    async eleza test_contextmanager_wrap_runtimeerror(self):
        @asynccontextmanager
        async eleza woohoo():
            jaribu:
                tuma
            tatizo Exception kama exc:
                ashiria RuntimeError(f'caught {exc}') kutoka exc

        ukijumuisha self.assertRaises(RuntimeError):
            async ukijumuisha woohoo():
                1 / 0

        # If the context manager wrapped StopAsyncIteration kwenye a RuntimeError,
        # we also unwrap it, because we can't tell whether the wrapping was
        # done by the generator machinery ama by the generator itself.
        ukijumuisha self.assertRaises(StopAsyncIteration):
            async ukijumuisha woohoo():
                ashiria StopAsyncIteration

    eleza _create_contextmanager_attribs(self):
        eleza attribs(**kw):
            eleza decorate(func):
                kila k,v kwenye kw.items():
                    setattr(func,k,v)
                rudisha func
            rudisha decorate
        @asynccontextmanager
        @attribs(foo='bar')
        async eleza baz(spam):
            """Whee!"""
            tuma
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
        baz = self._create_contextmanager_attribs()(Tupu)
        self.assertEqual(baz.__doc__, "Whee!")
        async ukijumuisha baz:
            pita  # suppress warning

    @_async_test
    async eleza test_keywords(self):
        # Ensure no keyword arguments are inhibited
        @asynccontextmanager
        async eleza woohoo(self, func, args, kwds):
            tuma (self, func, args, kwds)
        async ukijumuisha woohoo(self=11, func=22, args=33, kwds=44) kama target:
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

            ikiwa sio exc:
                rudisha f.result()
            isipokua:
                context = exc.__context__

                jaribu:
                    ashiria exc
                except:
                    exc.__context__ = context
                    ashiria exc

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
        self.addCleanup(asyncio.set_event_loop_policy, Tupu)

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

        async ukijumuisha AsyncExitStack() kama stack:
            kila args, kwds kwenye reversed(expected):
                ikiwa args na kwds:
                    f = stack.push_async_callback(_exit, *args, **kwds)
                lasivyo args:
                    f = stack.push_async_callback(_exit, *args)
                lasivyo kwds:
                    f = stack.push_async_callback(_exit, **kwds)
                isipokua:
                    f = stack.push_async_callback(_exit)
                self.assertIs(f, _exit)
            kila wrapper kwenye stack._exit_callbacks:
                self.assertIs(wrapper[1].__wrapped__, _exit)
                self.assertNotEqual(wrapper[1].__name__, _exit.__name__)
                self.assertIsTupu(wrapper[1].__doc__, _exit.__doc__)

        self.assertEqual(result, expected)

        result = []
        async ukijumuisha AsyncExitStack() kama stack:
            ukijumuisha self.assertRaises(TypeError):
                stack.push_async_callback(arg=1)
            ukijumuisha self.assertRaises(TypeError):
                self.exit_stack.push_async_callback(arg=2)
            ukijumuisha self.assertWarns(DeprecationWarning):
                stack.push_async_callback(callback=_exit, arg=3)
        self.assertEqual(result, [((), {'arg': 3})])

    @_async_test
    async eleza test_async_push(self):
        exc_ashiriad = ZeroDivisionError
        async eleza _expect_exc(exc_type, exc, exc_tb):
            self.assertIs(exc_type, exc_ashiriad)
        async eleza _suppress_exc(*exc_details):
            rudisha Kweli
        async eleza _expect_ok(exc_type, exc, exc_tb):
            self.assertIsTupu(exc_type)
            self.assertIsTupu(exc)
            self.assertIsTupu(exc_tb)
        kundi ExitCM(object):
            eleza __init__(self, check_exc):
                self.check_exc = check_exc
            async eleza __aenter__(self):
                self.fail("Should sio be called!")
            async eleza __aexit__(self, *exc_details):
                await self.check_exc(*exc_details)

        async ukijumuisha self.exit_stack() kama stack:
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

        async ukijumuisha AsyncExitStack() kama stack:
            @stack.push_async_callback  # Registered first => cleaned up last
            async eleza _exit():
                result.append(4)
            self.assertIsNotTupu(_exit)
            await stack.enter_async_context(cm)
            self.assertIs(stack._exit_callbacks[-1][1].__self__, cm)
            result.append(2)

        self.assertEqual(result, [1, 2, 3, 4])

    @_async_test
    async eleza test_async_exit_exception_chaining(self):
        # Ensure exception chaining matches the reference behaviour
        async eleza ashiria_exc(exc):
            ashiria exc

        saved_details = Tupu
        async eleza suppress_exc(*exc_details):
            nonlocal saved_details
            saved_details = exc_details
            rudisha Kweli

        jaribu:
            async ukijumuisha self.exit_stack() kama stack:
                stack.push_async_callback(ashiria_exc, IndexError)
                stack.push_async_callback(ashiria_exc, KeyError)
                stack.push_async_callback(ashiria_exc, AttributeError)
                stack.push_async_exit(suppress_exc)
                stack.push_async_callback(ashiria_exc, ValueError)
                1 / 0
        tatizo IndexError kama exc:
            self.assertIsInstance(exc.__context__, KeyError)
            self.assertIsInstance(exc.__context__.__context__, AttributeError)
            # Inner exceptions were suppressed
            self.assertIsTupu(exc.__context__.__context__.__context__)
        isipokua:
            self.fail("Expected IndexError, but no exception was ashiriad")
        # Check the inner exceptions
        inner_exc = saved_details[1]
        self.assertIsInstance(inner_exc, ValueError)
        self.assertIsInstance(inner_exc.__context__, ZeroDivisionError)


ikiwa __name__ == '__main__':
    unittest.main()
