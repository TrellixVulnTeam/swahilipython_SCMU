agiza inspect
agiza types
agiza unittest

kutoka test.support agiza import_module
asyncio = import_module("asyncio")


kundi AwaitException(Exception):
    pita


@types.coroutine
eleza awaitable(*, throw=Uongo):
    ikiwa throw:
        tuma ('throw',)
    isipokua:
        tuma ('result',)


eleza run_until_complete(coro):
    exc = Uongo
    wakati Kweli:
        jaribu:
            ikiwa exc:
                exc = Uongo
                fut = coro.throw(AwaitException)
            isipokua:
                fut = coro.send(Tupu)
        tatizo StopIteration kama ex:
            rudisha ex.args[0]

        ikiwa fut == ('throw',):
            exc = Kweli


eleza to_list(gen):
    async eleza iterate():
        res = []
        async kila i kwenye gen:
            res.append(i)
        rudisha res

    rudisha run_until_complete(iterate())


kundi AsyncGenSyntaxTest(unittest.TestCase):

    eleza test_async_gen_syntax_01(self):
        code = '''async eleza foo():
            await abc
            tuma kutoka 123
        '''

        ukijumuisha self.assertRaisesRegex(SyntaxError, 'tuma kutoka.*inside async'):
            exec(code, {}, {})

    eleza test_async_gen_syntax_02(self):
        code = '''async eleza foo():
            tuma kutoka 123
        '''

        ukijumuisha self.assertRaisesRegex(SyntaxError, 'tuma kutoka.*inside async'):
            exec(code, {}, {})

    eleza test_async_gen_syntax_03(self):
        code = '''async eleza foo():
            await abc
            tuma
            rudisha 123
        '''

        ukijumuisha self.assertRaisesRegex(SyntaxError, 'rudisha.*value.*async gen'):
            exec(code, {}, {})

    eleza test_async_gen_syntax_04(self):
        code = '''async eleza foo():
            tuma
            rudisha 123
        '''

        ukijumuisha self.assertRaisesRegex(SyntaxError, 'rudisha.*value.*async gen'):
            exec(code, {}, {})

    eleza test_async_gen_syntax_05(self):
        code = '''async eleza foo():
            ikiwa 0:
                tuma
            rudisha 12
        '''

        ukijumuisha self.assertRaisesRegex(SyntaxError, 'rudisha.*value.*async gen'):
            exec(code, {}, {})


kundi AsyncGenTest(unittest.TestCase):

    eleza compare_generators(self, sync_gen, async_gen):
        eleza sync_iterate(g):
            res = []
            wakati Kweli:
                jaribu:
                    res.append(g.__next__())
                tatizo StopIteration:
                    res.append('STOP')
                    koma
                tatizo Exception kama ex:
                    res.append(str(type(ex)))
            rudisha res

        eleza async_iterate(g):
            res = []
            wakati Kweli:
                an = g.__anext__()
                jaribu:
                    wakati Kweli:
                        jaribu:
                            an.__next__()
                        tatizo StopIteration kama ex:
                            ikiwa ex.args:
                                res.append(ex.args[0])
                                koma
                            isipokua:
                                res.append('EMPTY StopIteration')
                                koma
                        tatizo StopAsyncIteration:
                            ashiria
                        tatizo Exception kama ex:
                            res.append(str(type(ex)))
                            koma
                tatizo StopAsyncIteration:
                    res.append('STOP')
                    koma
            rudisha res

        sync_gen_result = sync_iterate(sync_gen)
        async_gen_result = async_iterate(async_gen)
        self.assertEqual(sync_gen_result, async_gen_result)
        rudisha async_gen_result

    eleza test_async_gen_iteration_01(self):
        async eleza gen():
            await awaitable()
            a = tuma 123
            self.assertIs(a, Tupu)
            await awaitable()
            tuma 456
            await awaitable()
            tuma 789

        self.assertEqual(to_list(gen()), [123, 456, 789])

    eleza test_async_gen_iteration_02(self):
        async eleza gen():
            await awaitable()
            tuma 123
            await awaitable()

        g = gen()
        ai = g.__aiter__()

        an = ai.__anext__()
        self.assertEqual(an.__next__(), ('result',))

        jaribu:
            an.__next__()
        tatizo StopIteration kama ex:
            self.assertEqual(ex.args[0], 123)
        isipokua:
            self.fail('StopIteration was sio ashiriad')

        an = ai.__anext__()
        self.assertEqual(an.__next__(), ('result',))

        jaribu:
            an.__next__()
        tatizo StopAsyncIteration kama ex:
            self.assertUongo(ex.args)
        isipokua:
            self.fail('StopAsyncIteration was sio ashiriad')

    eleza test_async_gen_exception_03(self):
        async eleza gen():
            await awaitable()
            tuma 123
            await awaitable(throw=Kweli)
            tuma 456

        ukijumuisha self.assertRaises(AwaitException):
            to_list(gen())

    eleza test_async_gen_exception_04(self):
        async eleza gen():
            await awaitable()
            tuma 123
            1 / 0

        g = gen()
        ai = g.__aiter__()
        an = ai.__anext__()
        self.assertEqual(an.__next__(), ('result',))

        jaribu:
            an.__next__()
        tatizo StopIteration kama ex:
            self.assertEqual(ex.args[0], 123)
        isipokua:
            self.fail('StopIteration was sio ashiriad')

        ukijumuisha self.assertRaises(ZeroDivisionError):
            ai.__anext__().__next__()

    eleza test_async_gen_exception_05(self):
        async eleza gen():
            tuma 123
            ashiria StopAsyncIteration

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'async generator.*StopAsyncIteration'):
            to_list(gen())

    eleza test_async_gen_exception_06(self):
        async eleza gen():
            tuma 123
            ashiria StopIteration

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'async generator.*StopIteration'):
            to_list(gen())

    eleza test_async_gen_exception_07(self):
        eleza sync_gen():
            jaribu:
                tuma 1
                1 / 0
            mwishowe:
                tuma 2
                tuma 3

            tuma 100

        async eleza async_gen():
            jaribu:
                tuma 1
                1 / 0
            mwishowe:
                tuma 2
                tuma 3

            tuma 100

        self.compare_generators(sync_gen(), async_gen())

    eleza test_async_gen_exception_08(self):
        eleza sync_gen():
            jaribu:
                tuma 1
            mwishowe:
                tuma 2
                1 / 0
                tuma 3

            tuma 100

        async eleza async_gen():
            jaribu:
                tuma 1
                await awaitable()
            mwishowe:
                await awaitable()
                tuma 2
                1 / 0
                tuma 3

            tuma 100

        self.compare_generators(sync_gen(), async_gen())

    eleza test_async_gen_exception_09(self):
        eleza sync_gen():
            jaribu:
                tuma 1
                1 / 0
            mwishowe:
                tuma 2
                tuma 3

            tuma 100

        async eleza async_gen():
            jaribu:
                await awaitable()
                tuma 1
                1 / 0
            mwishowe:
                tuma 2
                await awaitable()
                tuma 3

            tuma 100

        self.compare_generators(sync_gen(), async_gen())

    eleza test_async_gen_exception_10(self):
        async eleza gen():
            tuma 123
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    "non-Tupu value .* async generator"):
            gen().__anext__().send(100)

    eleza test_async_gen_exception_11(self):
        eleza sync_gen():
            tuma 10
            tuma 20

        eleza sync_gen_wrapper():
            tuma 1
            sg = sync_gen()
            sg.send(Tupu)
            jaribu:
                sg.throw(GeneratorExit())
            tatizo GeneratorExit:
                tuma 2
            tuma 3

        async eleza async_gen():
            tuma 10
            tuma 20

        async eleza async_gen_wrapper():
            tuma 1
            asg = async_gen()
            await asg.asend(Tupu)
            jaribu:
                await asg.athrow(GeneratorExit())
            tatizo GeneratorExit:
                tuma 2
            tuma 3

        self.compare_generators(sync_gen_wrapper(), async_gen_wrapper())

    eleza test_async_gen_api_01(self):
        async eleza gen():
            tuma 123

        g = gen()

        self.assertEqual(g.__name__, 'gen')
        g.__name__ = '123'
        self.assertEqual(g.__name__, '123')

        self.assertIn('.gen', g.__qualname__)
        g.__qualname__ = '123'
        self.assertEqual(g.__qualname__, '123')

        self.assertIsTupu(g.ag_await)
        self.assertIsInstance(g.ag_frame, types.FrameType)
        self.assertUongo(g.ag_running)
        self.assertIsInstance(g.ag_code, types.CodeType)

        self.assertKweli(inspect.isawaitable(g.aclose()))


kundi AsyncGenAsyncioTest(unittest.TestCase):

    eleza setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(Tupu)

    eleza tearDown(self):
        self.loop.close()
        self.loop = Tupu
        asyncio.set_event_loop_policy(Tupu)

    async eleza to_list(self, gen):
        res = []
        async kila i kwenye gen:
            res.append(i)
        rudisha res

    eleza test_async_gen_asyncio_01(self):
        async eleza gen():
            tuma 1
            await asyncio.sleep(0.01)
            tuma 2
            await asyncio.sleep(0.01)
            rudisha
            tuma 3

        res = self.loop.run_until_complete(self.to_list(gen()))
        self.assertEqual(res, [1, 2])

    eleza test_async_gen_asyncio_02(self):
        async eleza gen():
            tuma 1
            await asyncio.sleep(0.01)
            tuma 2
            1 / 0
            tuma 3

        ukijumuisha self.assertRaises(ZeroDivisionError):
            self.loop.run_until_complete(self.to_list(gen()))

    eleza test_async_gen_asyncio_03(self):
        loop = self.loop

        kundi Gen:
            async eleza __aiter__(self):
                tuma 1
                await asyncio.sleep(0.01)
                tuma 2

        res = loop.run_until_complete(self.to_list(Gen()))
        self.assertEqual(res, [1, 2])

    eleza test_async_gen_asyncio_anext_04(self):
        async eleza foo():
            tuma 1
            await asyncio.sleep(0.01)
            jaribu:
                tuma 2
                tuma 3
            tatizo ZeroDivisionError:
                tuma 1000
            await asyncio.sleep(0.01)
            tuma 4

        async eleza run1():
            it = foo().__aiter__()

            self.assertEqual(await it.__anext__(), 1)
            self.assertEqual(await it.__anext__(), 2)
            self.assertEqual(await it.__anext__(), 3)
            self.assertEqual(await it.__anext__(), 4)
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await it.__anext__()
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        async eleza run2():
            it = foo().__aiter__()

            self.assertEqual(await it.__anext__(), 1)
            self.assertEqual(await it.__anext__(), 2)
            jaribu:
                it.__anext__().throw(ZeroDivisionError)
            tatizo StopIteration kama ex:
                self.assertEqual(ex.args[0], 1000)
            isipokua:
                self.fail('StopIteration was sio ashiriad')
            self.assertEqual(await it.__anext__(), 4)
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        self.loop.run_until_complete(run1())
        self.loop.run_until_complete(run2())

    eleza test_async_gen_asyncio_anext_05(self):
        async eleza foo():
            v = tuma 1
            v = tuma v
            tuma v * 100

        async eleza run():
            it = foo().__aiter__()

            jaribu:
                it.__anext__().send(Tupu)
            tatizo StopIteration kama ex:
                self.assertEqual(ex.args[0], 1)
            isipokua:
                self.fail('StopIteration was sio ashiriad')

            jaribu:
                it.__anext__().send(10)
            tatizo StopIteration kama ex:
                self.assertEqual(ex.args[0], 10)
            isipokua:
                self.fail('StopIteration was sio ashiriad')

            jaribu:
                it.__anext__().send(12)
            tatizo StopIteration kama ex:
                self.assertEqual(ex.args[0], 1200)
            isipokua:
                self.fail('StopIteration was sio ashiriad')

            ukijumuisha self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_anext_06(self):
        DONE = 0

        # test synchronous generators
        eleza foo():
            jaribu:
                tuma
            tatizo:
                pita
        g = foo()
        g.send(Tupu)
        ukijumuisha self.assertRaises(StopIteration):
            g.send(Tupu)

        # now ukijumuisha asynchronous generators

        async eleza gen():
            nonlocal DONE
            jaribu:
                tuma
            tatizo:
                pita
            DONE = 1

        async eleza run():
            nonlocal DONE
            g = gen()
            await g.asend(Tupu)
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await g.asend(Tupu)
            DONE += 10

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 11)

    eleza test_async_gen_asyncio_anext_tuple(self):
        async eleza foo():
            jaribu:
                tuma (1,)
            tatizo ZeroDivisionError:
                tuma (2,)

        async eleza run():
            it = foo().__aiter__()

            self.assertEqual(await it.__anext__(), (1,))
            ukijumuisha self.assertRaises(StopIteration) kama cm:
                it.__anext__().throw(ZeroDivisionError)
            self.assertEqual(cm.exception.args[0], (2,))
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_anext_stopiteration(self):
        async eleza foo():
            jaribu:
                tuma StopIteration(1)
            tatizo ZeroDivisionError:
                tuma StopIteration(3)

        async eleza run():
            it = foo().__aiter__()

            v = await it.__anext__()
            self.assertIsInstance(v, StopIteration)
            self.assertEqual(v.value, 1)
            ukijumuisha self.assertRaises(StopIteration) kama cm:
                it.__anext__().throw(ZeroDivisionError)
            v = cm.exception.args[0]
            self.assertIsInstance(v, StopIteration)
            self.assertEqual(v.value, 3)
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_aclose_06(self):
        async eleza foo():
            jaribu:
                tuma 1
                1 / 0
            mwishowe:
                await asyncio.sleep(0.01)
                tuma 12

        async eleza run():
            gen = foo()
            it = gen.__aiter__()
            await it.__anext__()
            await gen.aclose()

        ukijumuisha self.assertRaisesRegex(
                RuntimeError,
                "async generator ignored GeneratorExit"):
            self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_aclose_07(self):
        DONE = 0

        async eleza foo():
            nonlocal DONE
            jaribu:
                tuma 1
                1 / 0
            mwishowe:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE += 1
            DONE += 1000

        async eleza run():
            gen = foo()
            it = gen.__aiter__()
            await it.__anext__()
            await gen.aclose()

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_aclose_08(self):
        DONE = 0

        fut = asyncio.Future(loop=self.loop)

        async eleza foo():
            nonlocal DONE
            jaribu:
                tuma 1
                await fut
                DONE += 1000
                tuma 2
            mwishowe:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE += 1
            DONE += 1000

        async eleza run():
            gen = foo()
            it = gen.__aiter__()
            self.assertEqual(await it.__anext__(), 1)
            await gen.aclose()

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

        # Silence ResourceWarnings
        fut.cancel()
        self.loop.run_until_complete(asyncio.sleep(0.01))

    eleza test_async_gen_asyncio_gc_aclose_09(self):
        DONE = 0

        async eleza gen():
            nonlocal DONE
            jaribu:
                wakati Kweli:
                    tuma 1
            mwishowe:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()
            await g.__anext__()
            await g.__anext__()
            toa g

            await asyncio.sleep(0.1)

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_aclose_10(self):
        DONE = 0

        # test synchronous generators
        eleza foo():
            jaribu:
                tuma
            tatizo:
                pita
        g = foo()
        g.send(Tupu)
        g.close()

        # now ukijumuisha asynchronous generators

        async eleza gen():
            nonlocal DONE
            jaribu:
                tuma
            tatizo:
                pita
            DONE = 1

        async eleza run():
            nonlocal DONE
            g = gen()
            await g.asend(Tupu)
            await g.aclose()
            DONE += 10

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 11)

    eleza test_async_gen_asyncio_aclose_11(self):
        DONE = 0

        # test synchronous generators
        eleza foo():
            jaribu:
                tuma
            tatizo:
                pita
            tuma
        g = foo()
        g.send(Tupu)
        ukijumuisha self.assertRaisesRegex(RuntimeError, 'ignored GeneratorExit'):
            g.close()

        # now ukijumuisha asynchronous generators

        async eleza gen():
            nonlocal DONE
            jaribu:
                tuma
            tatizo:
                pita
            tuma
            DONE += 1

        async eleza run():
            nonlocal DONE
            g = gen()
            await g.asend(Tupu)
            ukijumuisha self.assertRaisesRegex(RuntimeError, 'ignored GeneratorExit'):
                await g.aclose()
            DONE += 10

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 10)

    eleza test_async_gen_asyncio_asend_01(self):
        DONE = 0

        # Sanity check:
        eleza sgen():
            v = tuma 1
            tuma v * 2
        sg = sgen()
        v = sg.send(Tupu)
        self.assertEqual(v, 1)
        v = sg.send(100)
        self.assertEqual(v, 200)

        async eleza gen():
            nonlocal DONE
            jaribu:
                await asyncio.sleep(0.01)
                v = tuma 1
                await asyncio.sleep(0.01)
                tuma v * 2
                await asyncio.sleep(0.01)
                rudisha
            mwishowe:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(Tupu)
            self.assertEqual(v, 1)

            v = await g.asend(100)
            self.assertEqual(v, 200)

            ukijumuisha self.assertRaises(StopAsyncIteration):
                await g.asend(Tupu)

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_asend_02(self):
        DONE = 0

        async eleza sleep_n_crash(delay):
            await asyncio.sleep(delay)
            1 / 0

        async eleza gen():
            nonlocal DONE
            jaribu:
                await asyncio.sleep(0.01)
                v = tuma 1
                await sleep_n_crash(0.01)
                DONE += 1000
                tuma v * 2
            mwishowe:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(Tupu)
            self.assertEqual(v, 1)

            await g.asend(100)

        ukijumuisha self.assertRaises(ZeroDivisionError):
            self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_asend_03(self):
        DONE = 0

        async eleza sleep_n_crash(delay):
            fut = asyncio.ensure_future(asyncio.sleep(delay),
                                        loop=self.loop)
            self.loop.call_later(delay / 2, lambda: fut.cancel())
            rudisha await fut

        async eleza gen():
            nonlocal DONE
            jaribu:
                await asyncio.sleep(0.01)
                v = tuma 1
                await sleep_n_crash(0.01)
                DONE += 1000
                tuma v * 2
            mwishowe:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(Tupu)
            self.assertEqual(v, 1)

            await g.asend(100)

        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_athrow_01(self):
        DONE = 0

        kundi FooEr(Exception):
            pita

        # Sanity check:
        eleza sgen():
            jaribu:
                v = tuma 1
            tatizo FooEr:
                v = 1000
            tuma v * 2
        sg = sgen()
        v = sg.send(Tupu)
        self.assertEqual(v, 1)
        v = sg.throw(FooEr)
        self.assertEqual(v, 2000)
        ukijumuisha self.assertRaises(StopIteration):
            sg.send(Tupu)

        async eleza gen():
            nonlocal DONE
            jaribu:
                await asyncio.sleep(0.01)
                jaribu:
                    v = tuma 1
                tatizo FooEr:
                    v = 1000
                    await asyncio.sleep(0.01)
                tuma v * 2
                await asyncio.sleep(0.01)
                # rudisha
            mwishowe:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(Tupu)
            self.assertEqual(v, 1)

            v = await g.athrow(FooEr)
            self.assertEqual(v, 2000)

            ukijumuisha self.assertRaises(StopAsyncIteration):
                await g.asend(Tupu)

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_athrow_02(self):
        DONE = 0

        kundi FooEr(Exception):
            pita

        async eleza sleep_n_crash(delay):
            fut = asyncio.ensure_future(asyncio.sleep(delay),
                                        loop=self.loop)
            self.loop.call_later(delay / 2, lambda: fut.cancel())
            rudisha await fut

        async eleza gen():
            nonlocal DONE
            jaribu:
                await asyncio.sleep(0.01)
                jaribu:
                    v = tuma 1
                tatizo FooEr:
                    await sleep_n_crash(0.01)
                tuma v * 2
                await asyncio.sleep(0.01)
                # rudisha
            mwishowe:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(Tupu)
            self.assertEqual(v, 1)

            jaribu:
                await g.athrow(FooEr)
            tatizo asyncio.CancelledError:
                self.assertEqual(DONE, 1)
                ashiria
            isipokua:
                self.fail('CancelledError was sio ashiriad')

        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_athrow_03(self):
        DONE = 0

        # test synchronous generators
        eleza foo():
            jaribu:
                tuma
            tatizo:
                pita
        g = foo()
        g.send(Tupu)
        ukijumuisha self.assertRaises(StopIteration):
            g.throw(ValueError)

        # now ukijumuisha asynchronous generators

        async eleza gen():
            nonlocal DONE
            jaribu:
                tuma
            tatizo:
                pita
            DONE = 1

        async eleza run():
            nonlocal DONE
            g = gen()
            await g.asend(Tupu)
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await g.athrow(ValueError)
            DONE += 10

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 11)

    eleza test_async_gen_asyncio_athrow_tuple(self):
        async eleza gen():
            jaribu:
                tuma 1
            tatizo ZeroDivisionError:
                tuma (2,)

        async eleza run():
            g = gen()
            v = await g.asend(Tupu)
            self.assertEqual(v, 1)
            v = await g.athrow(ZeroDivisionError)
            self.assertEqual(v, (2,))
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await g.asend(Tupu)

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_athrow_stopiteration(self):
        async eleza gen():
            jaribu:
                tuma 1
            tatizo ZeroDivisionError:
                tuma StopIteration(2)

        async eleza run():
            g = gen()
            v = await g.asend(Tupu)
            self.assertEqual(v, 1)
            v = await g.athrow(ZeroDivisionError)
            self.assertIsInstance(v, StopIteration)
            self.assertEqual(v.value, 2)
            ukijumuisha self.assertRaises(StopAsyncIteration):
                await g.asend(Tupu)

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_shutdown_01(self):
        finalized = 0

        async eleza waiter(timeout):
            nonlocal finalized
            jaribu:
                await asyncio.sleep(timeout)
                tuma 1
            mwishowe:
                await asyncio.sleep(0)
                finalized += 1

        async eleza wait():
            async kila _ kwenye waiter(1):
                pita

        t1 = self.loop.create_task(wait())
        t2 = self.loop.create_task(wait())

        self.loop.run_until_complete(asyncio.sleep(0.1))

        # Silence warnings
        t1.cancel()
        t2.cancel()

        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(t1)
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(t2)

        self.loop.run_until_complete(self.loop.shutdown_asyncgens())

        self.assertEqual(finalized, 2)

    eleza test_async_gen_expression_01(self):
        async eleza arange(n):
            kila i kwenye range(n):
                await asyncio.sleep(0.01)
                tuma i

        eleza make_arange(n):
            # This syntax ni legal starting ukijumuisha Python 3.7
            rudisha (i * 2 async kila i kwenye arange(n))

        async eleza run():
            rudisha [i async kila i kwenye make_arange(10)]

        res = self.loop.run_until_complete(run())
        self.assertEqual(res, [i * 2 kila i kwenye range(10)])

    eleza test_async_gen_expression_02(self):
        async eleza wrap(n):
            await asyncio.sleep(0.01)
            rudisha n

        eleza make_arange(n):
            # This syntax ni legal starting ukijumuisha Python 3.7
            rudisha (i * 2 kila i kwenye range(n) ikiwa await wrap(i))

        async eleza run():
            rudisha [i async kila i kwenye make_arange(10)]

        res = self.loop.run_until_complete(run())
        self.assertEqual(res, [i * 2 kila i kwenye range(1, 10)])

    eleza test_asyncgen_nonstarted_hooks_are_cancellable(self):
        # See https://bugs.python.org/issue38013
        messages = []

        eleza exception_handler(loop, context):
            messages.append(context)

        async eleza async_iterate():
            tuma 1
            tuma 2

        async eleza main():
            loop = asyncio.get_running_loop()
            loop.set_exception_handler(exception_handler)

            async kila i kwenye async_iterate():
                koma

        asyncio.run(main())

        self.assertEqual([], messages)


ikiwa __name__ == "__main__":
    unittest.main()
