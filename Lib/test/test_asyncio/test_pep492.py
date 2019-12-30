"""Tests support kila new syntax introduced by PEP 492."""

agiza sys
agiza types
agiza unittest

kutoka unittest agiza mock

agiza asyncio
kutoka test.test_asyncio agiza utils kama test_utils


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


# Test that asyncio.iscoroutine() uses collections.abc.Coroutine
kundi FakeCoro:
    eleza send(self, value):
        pita

    eleza throw(self, typ, val=Tupu, tb=Tupu):
        pita

    eleza close(self):
        pita

    eleza __await__(self):
        tuma


kundi BaseTest(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.BaseEventLoop()
        self.loop._process_events = mock.Mock()
        self.loop._selector = mock.Mock()
        self.loop._selector.select.return_value = ()
        self.set_event_loop(self.loop)


kundi LockTests(BaseTest):

    eleza test_context_manager_async_with(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            primitives = [
                asyncio.Lock(loop=self.loop),
                asyncio.Condition(loop=self.loop),
                asyncio.Semaphore(loop=self.loop),
                asyncio.BoundedSemaphore(loop=self.loop),
            ]

        async eleza test(lock):
            await asyncio.sleep(0.01)
            self.assertUongo(lock.locked())
            async ukijumuisha lock kama _lock:
                self.assertIs(_lock, Tupu)
                self.assertKweli(lock.locked())
                await asyncio.sleep(0.01)
                self.assertKweli(lock.locked())
            self.assertUongo(lock.locked())

        kila primitive kwenye primitives:
            self.loop.run_until_complete(test(primitive))
            self.assertUongo(primitive.locked())

    eleza test_context_manager_with_await(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            primitives = [
                asyncio.Lock(loop=self.loop),
                asyncio.Condition(loop=self.loop),
                asyncio.Semaphore(loop=self.loop),
                asyncio.BoundedSemaphore(loop=self.loop),
            ]

        async eleza test(lock):
            await asyncio.sleep(0.01)
            self.assertUongo(lock.locked())
            ukijumuisha self.assertWarns(DeprecationWarning):
                ukijumuisha await lock kama _lock:
                    self.assertIs(_lock, Tupu)
                    self.assertKweli(lock.locked())
                    await asyncio.sleep(0.01)
                    self.assertKweli(lock.locked())
                self.assertUongo(lock.locked())

        kila primitive kwenye primitives:
            self.loop.run_until_complete(test(primitive))
            self.assertUongo(primitive.locked())


kundi StreamReaderTests(BaseTest):

    eleza test_readline(self):
        DATA = b'line1\nline2\nline3'

        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(DATA)
        stream.feed_eof()

        async eleza reader():
            data = []
            async kila line kwenye stream:
                data.append(line)
            rudisha data

        data = self.loop.run_until_complete(reader())
        self.assertEqual(data, [b'line1\n', b'line2\n', b'line3'])


kundi CoroutineTests(BaseTest):

    eleza test_iscoroutine(self):
        async eleza foo(): pita

        f = foo()
        jaribu:
            self.assertKweli(asyncio.iscoroutine(f))
        mwishowe:
            f.close() # silence warning

        self.assertKweli(asyncio.iscoroutine(FakeCoro()))

    eleza test_iscoroutinefunction(self):
        async eleza foo(): pita
        self.assertKweli(asyncio.iscoroutinefunction(foo))

    eleza test_function_returning_awaitable(self):
        kundi Awaitable:
            eleza __await__(self):
                rudisha ('spam',)

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza func():
                rudisha Awaitable()

        coro = func()
        self.assertEqual(coro.send(Tupu), 'spam')
        coro.close()

    eleza test_async_def_coroutines(self):
        async eleza bar():
            rudisha 'spam'
        async eleza foo():
            rudisha await bar()

        # production mode
        data = self.loop.run_until_complete(foo())
        self.assertEqual(data, 'spam')

        # debug mode
        self.loop.set_debug(Kweli)
        data = self.loop.run_until_complete(foo())
        self.assertEqual(data, 'spam')

    eleza test_debug_mode_manages_coroutine_origin_tracking(self):
        async eleza start():
            self.assertKweli(sys.get_coroutine_origin_tracking_depth() > 0)

        self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 0)
        self.loop.set_debug(Kweli)
        self.loop.run_until_complete(start())
        self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 0)

    eleza test_types_coroutine(self):
        eleza gen():
            tuma kutoka ()
            rudisha 'spam'

        @types.coroutine
        eleza func():
            rudisha gen()

        async eleza coro():
            wrapper = func()
            self.assertIsInstance(wrapper, types._GeneratorWrapper)
            rudisha await wrapper

        data = self.loop.run_until_complete(coro())
        self.assertEqual(data, 'spam')

    eleza test_task_print_stack(self):
        T = Tupu

        async eleza foo():
            f = T.get_stack(limit=1)
            jaribu:
                self.assertEqual(f[0].f_code.co_name, 'foo')
            mwishowe:
                f = Tupu

        async eleza runner():
            nonlocal T
            T = asyncio.ensure_future(foo(), loop=self.loop)
            await T

        self.loop.run_until_complete(runner())

    eleza test_double_await(self):
        async eleza afunc():
            await asyncio.sleep(0.1)

        async eleza runner():
            coro = afunc()
            t = self.loop.create_task(coro)
            jaribu:
                await asyncio.sleep(0)
                await coro
            mwishowe:
                t.cancel()

        self.loop.set_debug(Kweli)
        ukijumuisha self.assertRaises(
                RuntimeError,
                msg='coroutine ni being awaited already'):

            self.loop.run_until_complete(runner())


ikiwa __name__ == '__main__':
    unittest.main()
