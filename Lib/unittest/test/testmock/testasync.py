agiza asyncio
agiza inspect
agiza re
agiza unittest

kutoka unittest.mock agiza (ANY, call, AsyncMock, patch, MagicMock, Mock,
                           create_autospec, sentinel, _CallList)


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi AsyncClass:
    eleza __init__(self):
        pita
    async eleza async_method(self):
        pita
    eleza normal_method(self):
        pita

kundi AwaitableClass:
    eleza __await__(self):
        tuma

async eleza async_func():
    pita

async eleza async_func_args(a, b, *, c):
    pita

eleza normal_func():
    pita

kundi NormalClass(object):
    eleza a(self):
        pita


async_foo_name = f'{__name__}.AsyncClass'
normal_foo_name = f'{__name__}.NormalClass'


kundi AsyncPatchDecoratorTest(unittest.TestCase):
    eleza test_is_coroutine_function_patch(self):
        @patch.object(AsyncClass, 'async_method')
        eleza test_async(mock_method):
            self.assertKweli(asyncio.iscoroutinefunction(mock_method))
        test_async()

    eleza test_is_async_patch(self):
        @patch.object(AsyncClass, 'async_method')
        eleza test_async(mock_method):
            m = mock_method()
            self.assertKweli(inspect.isawaitable(m))
            asyncio.run(m)

        @patch(f'{async_foo_name}.async_method')
        eleza test_no_parent_attribute(mock_method):
            m = mock_method()
            self.assertKweli(inspect.isawaitable(m))
            asyncio.run(m)

        test_async()
        test_no_parent_attribute()

    eleza test_is_AsyncMock_patch(self):
        @patch.object(AsyncClass, 'async_method')
        eleza test_async(mock_method):
            self.assertIsInstance(mock_method, AsyncMock)

        test_async()

    eleza test_async_def_patch(self):
        @patch(f"{__name__}.async_func", AsyncMock())
        async eleza test_async():
            self.assertIsInstance(async_func, AsyncMock)

        asyncio.run(test_async())
        self.assertKweli(inspect.iscoroutinefunction(async_func))


kundi AsyncPatchCMTest(unittest.TestCase):
    eleza test_is_async_function_cm(self):
        eleza test_async():
            ukijumuisha patch.object(AsyncClass, 'async_method') kama mock_method:
                self.assertKweli(asyncio.iscoroutinefunction(mock_method))

        test_async()

    eleza test_is_async_cm(self):
        eleza test_async():
            ukijumuisha patch.object(AsyncClass, 'async_method') kama mock_method:
                m = mock_method()
                self.assertKweli(inspect.isawaitable(m))
                asyncio.run(m)

        test_async()

    eleza test_is_AsyncMock_cm(self):
        eleza test_async():
            ukijumuisha patch.object(AsyncClass, 'async_method') kama mock_method:
                self.assertIsInstance(mock_method, AsyncMock)

        test_async()

    eleza test_async_def_cm(self):
        async eleza test_async():
            ukijumuisha patch(f"{__name__}.async_func", AsyncMock()):
                self.assertIsInstance(async_func, AsyncMock)
            self.assertKweli(inspect.iscoroutinefunction(async_func))

        asyncio.run(test_async())


kundi AsyncMockTest(unittest.TestCase):
    eleza test_iscoroutinefunction_default(self):
        mock = AsyncMock()
        self.assertKweli(asyncio.iscoroutinefunction(mock))

    eleza test_iscoroutinefunction_function(self):
        async eleza foo(): pita
        mock = AsyncMock(foo)
        self.assertKweli(asyncio.iscoroutinefunction(mock))
        self.assertKweli(inspect.iscoroutinefunction(mock))

    eleza test_isawaitable(self):
        mock = AsyncMock()
        m = mock()
        self.assertKweli(inspect.isawaitable(m))
        asyncio.run(m)
        self.assertIn('assert_awaited', dir(mock))

    eleza test_iscoroutinefunction_normal_function(self):
        eleza foo(): pita
        mock = AsyncMock(foo)
        self.assertKweli(asyncio.iscoroutinefunction(mock))
        self.assertKweli(inspect.iscoroutinefunction(mock))

    eleza test_future_isfuture(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        fut = asyncio.Future()
        loop.stop()
        loop.close()
        mock = AsyncMock(fut)
        self.assertIsInstance(mock, asyncio.Future)


kundi AsyncAutospecTest(unittest.TestCase):
    eleza test_is_AsyncMock_patch(self):
        @patch(async_foo_name, autospec=Kweli)
        eleza test_async(mock_method):
            self.assertIsInstance(mock_method.async_method, AsyncMock)
            self.assertIsInstance(mock_method, MagicMock)

        @patch(async_foo_name, autospec=Kweli)
        eleza test_normal_method(mock_method):
            self.assertIsInstance(mock_method.normal_method, MagicMock)

        test_async()
        test_normal_method()

    eleza test_create_autospec_instance(self):
        ukijumuisha self.assertRaises(RuntimeError):
            create_autospec(async_func, instance=Kweli)

    eleza test_create_autospec_awaitable_class(self):
        awaitable_mock = create_autospec(spec=AwaitableClass())
        self.assertIsInstance(create_autospec(awaitable_mock), AsyncMock)

    eleza test_create_autospec(self):
        spec = create_autospec(async_func_args)
        awaitable = spec(1, 2, c=3)
        async eleza main():
            await awaitable

        self.assertEqual(spec.await_count, 0)
        self.assertIsTupu(spec.await_args)
        self.assertEqual(spec.await_args_list, [])
        spec.assert_not_awaited()

        asyncio.run(main())

        self.assertKweli(asyncio.iscoroutinefunction(spec))
        self.assertKweli(asyncio.iscoroutine(awaitable))
        self.assertEqual(spec.await_count, 1)
        self.assertEqual(spec.await_args, call(1, 2, c=3))
        self.assertEqual(spec.await_args_list, [call(1, 2, c=3)])
        spec.assert_awaited_once()
        spec.assert_awaited_once_with(1, 2, c=3)
        spec.assert_awaited_with(1, 2, c=3)
        spec.assert_awaited()

    eleza test_patch_with_autospec(self):

        async eleza test_async():
            ukijumuisha patch(f"{__name__}.async_func_args", autospec=Kweli) kama mock_method:
                awaitable = mock_method(1, 2, c=3)
                self.assertIsInstance(mock_method.mock, AsyncMock)

                self.assertKweli(asyncio.iscoroutinefunction(mock_method))
                self.assertKweli(asyncio.iscoroutine(awaitable))
                self.assertKweli(inspect.isawaitable(awaitable))

                # Verify the default values during mock setup
                self.assertEqual(mock_method.await_count, 0)
                self.assertEqual(mock_method.await_args_list, [])
                self.assertIsTupu(mock_method.await_args)
                mock_method.assert_not_awaited()

                await awaitable

            self.assertEqual(mock_method.await_count, 1)
            self.assertEqual(mock_method.await_args, call(1, 2, c=3))
            self.assertEqual(mock_method.await_args_list, [call(1, 2, c=3)])
            mock_method.assert_awaited_once()
            mock_method.assert_awaited_once_with(1, 2, c=3)
            mock_method.assert_awaited_with(1, 2, c=3)
            mock_method.assert_awaited()

            mock_method.reset_mock()
            self.assertEqual(mock_method.await_count, 0)
            self.assertIsTupu(mock_method.await_args)
            self.assertEqual(mock_method.await_args_list, [])

        asyncio.run(test_async())


kundi AsyncSpecTest(unittest.TestCase):
    eleza test_spec_normal_methods_on_class(self):
        eleza inner_test(mock_type):
            mock = mock_type(AsyncClass)
            self.assertIsInstance(mock.async_method, AsyncMock)
            self.assertIsInstance(mock.normal_method, MagicMock)

        kila mock_type kwenye [AsyncMock, MagicMock]:
            ukijumuisha self.subTest(f"test method types ukijumuisha {mock_type}"):
                inner_test(mock_type)

    eleza test_spec_normal_methods_on_class_with_mock(self):
        mock = Mock(AsyncClass)
        self.assertIsInstance(mock.async_method, AsyncMock)
        self.assertIsInstance(mock.normal_method, Mock)

    eleza test_spec_mock_type_kw(self):
        eleza inner_test(mock_type):
            async_mock = mock_type(spec=async_func)
            self.assertIsInstance(async_mock, mock_type)
            ukijumuisha self.assertWarns(RuntimeWarning):
                # Will ashiria a warning because never awaited
                self.assertKweli(inspect.isawaitable(async_mock()))

            sync_mock = mock_type(spec=normal_func)
            self.assertIsInstance(sync_mock, mock_type)

        kila mock_type kwenye [AsyncMock, MagicMock, Mock]:
            ukijumuisha self.subTest(f"test spec kwarg ukijumuisha {mock_type}"):
                inner_test(mock_type)

    eleza test_spec_mock_type_positional(self):
        eleza inner_test(mock_type):
            async_mock = mock_type(async_func)
            self.assertIsInstance(async_mock, mock_type)
            ukijumuisha self.assertWarns(RuntimeWarning):
                # Will ashiria a warning because never awaited
                self.assertKweli(inspect.isawaitable(async_mock()))

            sync_mock = mock_type(normal_func)
            self.assertIsInstance(sync_mock, mock_type)

        kila mock_type kwenye [AsyncMock, MagicMock, Mock]:
            ukijumuisha self.subTest(f"test spec positional ukijumuisha {mock_type}"):
                inner_test(mock_type)

    eleza test_spec_as_normal_kw_AsyncMock(self):
        mock = AsyncMock(spec=normal_func)
        self.assertIsInstance(mock, AsyncMock)
        m = mock()
        self.assertKweli(inspect.isawaitable(m))
        asyncio.run(m)

    eleza test_spec_as_normal_positional_AsyncMock(self):
        mock = AsyncMock(normal_func)
        self.assertIsInstance(mock, AsyncMock)
        m = mock()
        self.assertKweli(inspect.isawaitable(m))
        asyncio.run(m)

    eleza test_spec_async_mock(self):
        @patch.object(AsyncClass, 'async_method', spec=Kweli)
        eleza test_async(mock_method):
            self.assertIsInstance(mock_method, AsyncMock)

        test_async()

    eleza test_spec_parent_not_async_attribute_is(self):
        @patch(async_foo_name, spec=Kweli)
        eleza test_async(mock_method):
            self.assertIsInstance(mock_method, MagicMock)
            self.assertIsInstance(mock_method.async_method, AsyncMock)

        test_async()

    eleza test_target_async_spec_not(self):
        @patch.object(AsyncClass, 'async_method', spec=NormalClass.a)
        eleza test_async_attribute(mock_method):
            self.assertIsInstance(mock_method, MagicMock)
            self.assertUongo(inspect.iscoroutine(mock_method))
            self.assertUongo(inspect.isawaitable(mock_method))

        test_async_attribute()

    eleza test_target_not_async_spec_is(self):
        @patch.object(NormalClass, 'a', spec=async_func)
        eleza test_attribute_not_async_spec_is(mock_async_func):
            self.assertIsInstance(mock_async_func, AsyncMock)
        test_attribute_not_async_spec_is()

    eleza test_spec_async_attributes(self):
        @patch(normal_foo_name, spec=AsyncClass)
        eleza test_async_attributes_coroutines(MockNormalClass):
            self.assertIsInstance(MockNormalClass.async_method, AsyncMock)
            self.assertIsInstance(MockNormalClass, MagicMock)

        test_async_attributes_coroutines()


kundi AsyncSpecSetTest(unittest.TestCase):
    eleza test_is_AsyncMock_patch(self):
        @patch.object(AsyncClass, 'async_method', spec_set=Kweli)
        eleza test_async(async_method):
            self.assertIsInstance(async_method, AsyncMock)

    eleza test_is_async_AsyncMock(self):
        mock = AsyncMock(spec_set=AsyncClass.async_method)
        self.assertKweli(asyncio.iscoroutinefunction(mock))
        self.assertIsInstance(mock, AsyncMock)

    eleza test_is_child_AsyncMock(self):
        mock = MagicMock(spec_set=AsyncClass)
        self.assertKweli(asyncio.iscoroutinefunction(mock.async_method))
        self.assertUongo(asyncio.iscoroutinefunction(mock.normal_method))
        self.assertIsInstance(mock.async_method, AsyncMock)
        self.assertIsInstance(mock.normal_method, MagicMock)
        self.assertIsInstance(mock, MagicMock)

    eleza test_magicmock_lambda_spec(self):
        mock_obj = MagicMock()
        mock_obj.mock_func = MagicMock(spec=lambda x: x)

        ukijumuisha patch.object(mock_obj, "mock_func") kama cm:
            self.assertIsInstance(cm, MagicMock)


kundi AsyncArguments(unittest.TestCase):
    eleza test_add_return_value(self):
        async eleza addition(self, var):
            rudisha var + 1

        mock = AsyncMock(addition, return_value=10)
        output = asyncio.run(mock(5))

        self.assertEqual(output, 10)

    eleza test_add_side_effect_exception(self):
        async eleza addition(var):
            rudisha var + 1
        mock = AsyncMock(addition, side_effect=Exception('err'))
        ukijumuisha self.assertRaises(Exception):
            asyncio.run(mock(5))

    eleza test_add_side_effect_function(self):
        async eleza addition(var):
            rudisha var + 1
        mock = AsyncMock(side_effect=addition)
        result = asyncio.run(mock(5))
        self.assertEqual(result, 6)

    eleza test_add_side_effect_iterable(self):
        vals = [1, 2, 3]
        mock = AsyncMock(side_effect=vals)
        kila item kwenye vals:
            self.assertEqual(item, asyncio.run(mock()))

        ukijumuisha self.assertRaises(RuntimeError) kama e:
            asyncio.run(mock())
            self.assertEqual(
                e.exception,
                RuntimeError('coroutine raised StopIteration')
            )

kundi AsyncMagicMethods(unittest.TestCase):
    eleza test_async_magic_methods_return_async_mocks(self):
        m_mock = MagicMock()
        self.assertIsInstance(m_mock.__aenter__, AsyncMock)
        self.assertIsInstance(m_mock.__aexit__, AsyncMock)
        self.assertIsInstance(m_mock.__anext__, AsyncMock)
        # __aiter__ ni actually a synchronous object
        # so should rudisha a MagicMock
        self.assertIsInstance(m_mock.__aiter__, MagicMock)

    eleza test_sync_magic_methods_return_magic_mocks(self):
        a_mock = AsyncMock()
        self.assertIsInstance(a_mock.__enter__, MagicMock)
        self.assertIsInstance(a_mock.__exit__, MagicMock)
        self.assertIsInstance(a_mock.__next__, MagicMock)
        self.assertIsInstance(a_mock.__len__, MagicMock)

    eleza test_magicmock_has_async_magic_methods(self):
        m_mock = MagicMock()
        self.assertKweli(hasattr(m_mock, "__aenter__"))
        self.assertKweli(hasattr(m_mock, "__aexit__"))
        self.assertKweli(hasattr(m_mock, "__anext__"))

    eleza test_asyncmock_has_sync_magic_methods(self):
        a_mock = AsyncMock()
        self.assertKweli(hasattr(a_mock, "__enter__"))
        self.assertKweli(hasattr(a_mock, "__exit__"))
        self.assertKweli(hasattr(a_mock, "__next__"))
        self.assertKweli(hasattr(a_mock, "__len__"))

    eleza test_magic_methods_are_async_functions(self):
        m_mock = MagicMock()
        self.assertIsInstance(m_mock.__aenter__, AsyncMock)
        self.assertIsInstance(m_mock.__aexit__, AsyncMock)
        # AsyncMocks are also coroutine functions
        self.assertKweli(asyncio.iscoroutinefunction(m_mock.__aenter__))
        self.assertKweli(asyncio.iscoroutinefunction(m_mock.__aexit__))

kundi AsyncContextManagerTest(unittest.TestCase):
    kundi WithAsyncContextManager:
        async eleza __aenter__(self, *args, **kwargs):
            self.entered = Kweli
            rudisha self

        async eleza __aexit__(self, *args, **kwargs):
            self.exited = Kweli

    kundi WithSyncContextManager:
        eleza __enter__(self, *args, **kwargs):
            rudisha self

        eleza __exit__(self, *args, **kwargs):
            pita

    kundi ProductionCode:
        # Example real-world(ish) code
        eleza __init__(self):
            self.session = Tupu

        async eleza main(self):
            async ukijumuisha self.session.post('https://python.org') kama response:
                val = await response.json()
                rudisha val

    eleza test_set_return_value_of_aenter(self):
        eleza inner_test(mock_type):
            pc = self.ProductionCode()
            pc.session = MagicMock(name='sessionmock')
            cm = mock_type(name='magic_cm')
            response = AsyncMock(name='response')
            response.json = AsyncMock(return_value={'json': 123})
            cm.__aenter__.return_value = response
            pc.session.post.return_value = cm
            result = asyncio.run(pc.main())
            self.assertEqual(result, {'json': 123})

        kila mock_type kwenye [AsyncMock, MagicMock]:
            ukijumuisha self.subTest(f"test set rudisha value of aenter ukijumuisha {mock_type}"):
                inner_test(mock_type)

    eleza test_mock_supports_async_context_manager(self):
        eleza inner_test(mock_type):
            called = Uongo
            cm = self.WithAsyncContextManager()
            cm_mock = mock_type(cm)

            async eleza use_context_manager():
                nonlocal called
                async ukijumuisha cm_mock kama result:
                    called = Kweli
                rudisha result

            cm_result = asyncio.run(use_context_manager())
            self.assertKweli(called)
            self.assertKweli(cm_mock.__aenter__.called)
            self.assertKweli(cm_mock.__aexit__.called)
            cm_mock.__aenter__.assert_awaited()
            cm_mock.__aexit__.assert_awaited()
            # We mock __aenter__ so it does sio rudisha self
            self.assertIsNot(cm_mock, cm_result)

        kila mock_type kwenye [AsyncMock, MagicMock]:
            ukijumuisha self.subTest(f"test context manager magics ukijumuisha {mock_type}"):
                inner_test(mock_type)

    eleza test_mock_customize_async_context_manager(self):
        instance = self.WithAsyncContextManager()
        mock_instance = MagicMock(instance)

        expected_result = object()
        mock_instance.__aenter__.return_value = expected_result

        async eleza use_context_manager():
            async ukijumuisha mock_instance kama result:
                rudisha result

        self.assertIs(asyncio.run(use_context_manager()), expected_result)

    eleza test_mock_customize_async_context_manager_with_coroutine(self):
        enter_called = Uongo
        exit_called = Uongo

        async eleza enter_coroutine(*args):
            nonlocal enter_called
            enter_called = Kweli

        async eleza exit_coroutine(*args):
            nonlocal exit_called
            exit_called = Kweli

        instance = self.WithAsyncContextManager()
        mock_instance = MagicMock(instance)

        mock_instance.__aenter__ = enter_coroutine
        mock_instance.__aexit__ = exit_coroutine

        async eleza use_context_manager():
            async ukijumuisha mock_instance:
                pita

        asyncio.run(use_context_manager())
        self.assertKweli(enter_called)
        self.assertKweli(exit_called)

    eleza test_context_manager_raise_exception_by_default(self):
        async eleza raise_in(context_manager):
            async ukijumuisha context_manager:
                ashiria TypeError()

        instance = self.WithAsyncContextManager()
        mock_instance = MagicMock(instance)
        ukijumuisha self.assertRaises(TypeError):
            asyncio.run(raise_in(mock_instance))


kundi AsyncIteratorTest(unittest.TestCase):
    kundi WithAsyncIterator(object):
        eleza __init__(self):
            self.items = ["foo", "NormalFoo", "baz"]

        eleza __aiter__(self):
            rudisha self

        async eleza __anext__(self):
            jaribu:
                rudisha self.items.pop()
            tatizo IndexError:
                pita

            ashiria StopAsyncIteration

    eleza test_aiter_set_return_value(self):
        mock_iter = AsyncMock(name="tester")
        mock_iter.__aiter__.return_value = [1, 2, 3]
        async eleza main():
            rudisha [i async kila i kwenye mock_iter]
        result = asyncio.run(main())
        self.assertEqual(result, [1, 2, 3])

    eleza test_mock_aiter_and_anext_asyncmock(self):
        eleza inner_test(mock_type):
            instance = self.WithAsyncIterator()
            mock_instance = mock_type(instance)
            # Check that the mock na the real thing bahave the same
            # __aiter__ ni sio actually async, so sio a coroutinefunction
            self.assertUongo(asyncio.iscoroutinefunction(instance.__aiter__))
            self.assertUongo(asyncio.iscoroutinefunction(mock_instance.__aiter__))
            # __anext__ ni async
            self.assertKweli(asyncio.iscoroutinefunction(instance.__anext__))
            self.assertKweli(asyncio.iscoroutinefunction(mock_instance.__anext__))

        kila mock_type kwenye [AsyncMock, MagicMock]:
            ukijumuisha self.subTest(f"test aiter na anext corourtine ukijumuisha {mock_type}"):
                inner_test(mock_type)


    eleza test_mock_async_for(self):
        async eleza iterate(iterator):
            accumulator = []
            async kila item kwenye iterator:
                accumulator.append(item)

            rudisha accumulator

        expected = ["FOO", "BAR", "BAZ"]
        eleza test_default(mock_type):
            mock_instance = mock_type(self.WithAsyncIterator())
            self.assertEqual(asyncio.run(iterate(mock_instance)), [])


        eleza test_set_return_value(mock_type):
            mock_instance = mock_type(self.WithAsyncIterator())
            mock_instance.__aiter__.return_value = expected[:]
            self.assertEqual(asyncio.run(iterate(mock_instance)), expected)

        eleza test_set_return_value_iter(mock_type):
            mock_instance = mock_type(self.WithAsyncIterator())
            mock_instance.__aiter__.return_value = iter(expected[:])
            self.assertEqual(asyncio.run(iterate(mock_instance)), expected)

        kila mock_type kwenye [AsyncMock, MagicMock]:
            ukijumuisha self.subTest(f"default value ukijumuisha {mock_type}"):
                test_default(mock_type)

            ukijumuisha self.subTest(f"set return_value ukijumuisha {mock_type}"):
                test_set_return_value(mock_type)

            ukijumuisha self.subTest(f"set return_value iterator ukijumuisha {mock_type}"):
                test_set_return_value_iter(mock_type)


kundi AsyncMockAssert(unittest.TestCase):
    eleza setUp(self):
        self.mock = AsyncMock()

    async eleza _runnable_test(self, *args, **kwargs):
        await self.mock(*args, **kwargs)

    async eleza _await_coroutine(self, coroutine):
        rudisha await coroutine

    eleza test_assert_called_but_not_awaited(self):
        mock = AsyncMock(AsyncClass)
        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria a warning because never awaited
            mock.async_method()
        self.assertKweli(asyncio.iscoroutinefunction(mock.async_method))
        mock.async_method.assert_called()
        mock.async_method.assert_called_once()
        mock.async_method.assert_called_once_with()
        ukijumuisha self.assertRaises(AssertionError):
            mock.assert_awaited()
        ukijumuisha self.assertRaises(AssertionError):
            mock.async_method.assert_awaited()

    eleza test_assert_called_then_awaited(self):
        mock = AsyncMock(AsyncClass)
        mock_coroutine = mock.async_method()
        mock.async_method.assert_called()
        mock.async_method.assert_called_once()
        mock.async_method.assert_called_once_with()
        ukijumuisha self.assertRaises(AssertionError):
            mock.async_method.assert_awaited()

        asyncio.run(self._await_coroutine(mock_coroutine))
        # Assert we haven't re-called the function
        mock.async_method.assert_called_once()
        mock.async_method.assert_awaited()
        mock.async_method.assert_awaited_once()
        mock.async_method.assert_awaited_once_with()

    eleza test_assert_called_and_awaited_at_same_time(self):
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited()

        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_called()

        asyncio.run(self._runnable_test())
        self.mock.assert_called_once()
        self.mock.assert_awaited_once()

    eleza test_assert_called_twice_and_awaited_once(self):
        mock = AsyncMock(AsyncClass)
        coroutine = mock.async_method()
        ukijumuisha self.assertWarns(RuntimeWarning):
            # The first call will be awaited so no warning there
            # But this call will never get awaited, so it will warn here
            mock.async_method()
        ukijumuisha self.assertRaises(AssertionError):
            mock.async_method.assert_awaited()
        mock.async_method.assert_called()
        asyncio.run(self._await_coroutine(coroutine))
        mock.async_method.assert_awaited()
        mock.async_method.assert_awaited_once()

    eleza test_assert_called_once_and_awaited_twice(self):
        mock = AsyncMock(AsyncClass)
        coroutine = mock.async_method()
        mock.async_method.assert_called_once()
        asyncio.run(self._await_coroutine(coroutine))
        ukijumuisha self.assertRaises(RuntimeError):
            # Cannot reuse already awaited coroutine
            asyncio.run(self._await_coroutine(coroutine))
        mock.async_method.assert_awaited()

    eleza test_assert_awaited_but_not_called(self):
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited()
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_called()
        ukijumuisha self.assertRaises(TypeError):
            # You cannot await an AsyncMock, it must be a coroutine
            asyncio.run(self._await_coroutine(self.mock))

        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited()
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_called()

    eleza test_assert_has_calls_not_awaits(self):
        kalls = [call('foo')]
        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria a warning because never awaited
            self.mock('foo')
        self.mock.assert_has_calls(kalls)
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_has_awaits(kalls)

    eleza test_assert_has_mock_calls_on_async_mock_no_spec(self):
        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria a warning because never awaited
            self.mock()
        kalls_empty = [('', (), {})]
        self.assertEqual(self.mock.mock_calls, kalls_empty)

        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria a warning because never awaited
            self.mock('foo')
            self.mock('baz')
        mock_kalls = ([call(), call('foo'), call('baz')])
        self.assertEqual(self.mock.mock_calls, mock_kalls)

    eleza test_assert_has_mock_calls_on_async_mock_with_spec(self):
        a_class_mock = AsyncMock(AsyncClass)
        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria a warning because never awaited
            a_class_mock.async_method()
        kalls_empty = [('', (), {})]
        self.assertEqual(a_class_mock.async_method.mock_calls, kalls_empty)
        self.assertEqual(a_class_mock.mock_calls, [call.async_method()])

        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria a warning because never awaited
            a_class_mock.async_method(1, 2, 3, a=4, b=5)
        method_kalls = [call(), call(1, 2, 3, a=4, b=5)]
        mock_kalls = [call.async_method(), call.async_method(1, 2, 3, a=4, b=5)]
        self.assertEqual(a_class_mock.async_method.mock_calls, method_kalls)
        self.assertEqual(a_class_mock.mock_calls, mock_kalls)

    eleza test_async_method_calls_recorded(self):
        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria warnings because never awaited
            self.mock.something(3, fish=Tupu)
            self.mock.something_else.something(6, cake=sentinel.Cake)

        self.assertEqual(self.mock.method_calls, [
            ("something", (3,), {'fish': Tupu}),
            ("something_else.something", (6,), {'cake': sentinel.Cake})
        ],
            "method calls sio recorded correctly")
        self.assertEqual(self.mock.something_else.method_calls,
                         [("something", (6,), {'cake': sentinel.Cake})],
                         "method calls sio recorded correctly")

    eleza test_async_arg_lists(self):
        eleza assert_attrs(mock):
            names = ('call_args_list', 'method_calls', 'mock_calls')
            kila name kwenye names:
                attr = getattr(mock, name)
                self.assertIsInstance(attr, _CallList)
                self.assertIsInstance(attr, list)
                self.assertEqual(attr, [])

        assert_attrs(self.mock)
        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria warnings because never awaited
            self.mock()
            self.mock(1, 2)
            self.mock(a=3)

        self.mock.reset_mock()
        assert_attrs(self.mock)

        a_mock = AsyncMock(AsyncClass)
        ukijumuisha self.assertWarns(RuntimeWarning):
            # Will ashiria warnings because never awaited
            a_mock.async_method()
            a_mock.async_method(1, a=3)

        a_mock.reset_mock()
        assert_attrs(a_mock)

    eleza test_assert_awaited(self):
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited()

        asyncio.run(self._runnable_test())
        self.mock.assert_awaited()

    eleza test_assert_awaited_once(self):
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited_once()

        asyncio.run(self._runnable_test())
        self.mock.assert_awaited_once()

        asyncio.run(self._runnable_test())
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited_once()

    eleza test_assert_awaited_with(self):
        asyncio.run(self._runnable_test())
        msg = 'expected await sio found'
        ukijumuisha self.assertRaisesRegex(AssertionError, msg):
            self.mock.assert_awaited_with('foo')

        asyncio.run(self._runnable_test('foo'))
        self.mock.assert_awaited_with('foo')

        asyncio.run(self._runnable_test('SomethingElse'))
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited_with('foo')

    eleza test_assert_awaited_once_with(self):
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited_once_with('foo')

        asyncio.run(self._runnable_test('foo'))
        self.mock.assert_awaited_once_with('foo')

        asyncio.run(self._runnable_test('foo'))
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_awaited_once_with('foo')

    eleza test_assert_any_wait(self):
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_any_await('foo')

        asyncio.run(self._runnable_test('baz'))
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_any_await('foo')

        asyncio.run(self._runnable_test('foo'))
        self.mock.assert_any_await('foo')

        asyncio.run(self._runnable_test('SomethingElse'))
        self.mock.assert_any_await('foo')

    eleza test_assert_has_awaits_no_order(self):
        calls = [call('foo'), call('baz')]

        ukijumuisha self.assertRaises(AssertionError) kama cm:
            self.mock.assert_has_awaits(calls)
        self.assertEqual(len(cm.exception.args), 1)

        asyncio.run(self._runnable_test('foo'))
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_has_awaits(calls)

        asyncio.run(self._runnable_test('foo'))
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_has_awaits(calls)

        asyncio.run(self._runnable_test('baz'))
        self.mock.assert_has_awaits(calls)

        asyncio.run(self._runnable_test('SomethingElse'))
        self.mock.assert_has_awaits(calls)

    eleza test_assert_has_awaits_ordered(self):
        calls = [call('foo'), call('baz')]
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_has_awaits(calls, any_order=Kweli)

        asyncio.run(self._runnable_test('baz'))
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_has_awaits(calls, any_order=Kweli)

        asyncio.run(self._runnable_test('bamf'))
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_has_awaits(calls, any_order=Kweli)

        asyncio.run(self._runnable_test('foo'))
        self.mock.assert_has_awaits(calls, any_order=Kweli)

        asyncio.run(self._runnable_test('qux'))
        self.mock.assert_has_awaits(calls, any_order=Kweli)

    eleza test_assert_not_awaited(self):
        self.mock.assert_not_awaited()

        asyncio.run(self._runnable_test())
        ukijumuisha self.assertRaises(AssertionError):
            self.mock.assert_not_awaited()

    eleza test_assert_has_awaits_not_matching_spec_error(self):
        async eleza f(x=Tupu): pita

        self.mock = AsyncMock(spec=f)
        asyncio.run(self._runnable_test(1))

        ukijumuisha self.assertRaisesRegex(
                AssertionError,
                '^{}$'.format(
                    re.escape('Awaits sio found.\n'
                              'Expected: [call()]\n'
                              'Actual: [call(1)]'))) kama cm:
            self.mock.assert_has_awaits([call()])
        self.assertIsTupu(cm.exception.__cause__)

        ukijumuisha self.assertRaisesRegex(
                AssertionError,
                '^{}$'.format(
                    re.escape(
                        'Error processing expected awaits.\n'
                        "Errors: [Tupu, TypeError('too many positional "
                        "arguments')]\n"
                        'Expected: [call(), call(1, 2)]\n'
                        'Actual: [call(1)]'))) kama cm:
            self.mock.assert_has_awaits([call(), call(1, 2)])
        self.assertIsInstance(cm.exception.__cause__, TypeError)
