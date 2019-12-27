agiza inspect
agiza types
agiza unittest

kutoka test.support agiza import_module
asyncio = import_module("asyncio")


kundi AwaitException(Exception):
    pass


@types.coroutine
eleza awaitable(*, throw=False):
    ikiwa throw:
        yield ('throw',)
    else:
        yield ('result',)


eleza run_until_complete(coro):
    exc = False
    while True:
        try:
            ikiwa exc:
                exc = False
                fut = coro.throw(AwaitException)
            else:
                fut = coro.send(None)
        except StopIteration as ex:
            rudisha ex.args[0]

        ikiwa fut == ('throw',):
            exc = True


eleza to_list(gen):
    async eleza iterate():
        res = []
        async for i in gen:
            res.append(i)
        rudisha res

    rudisha run_until_complete(iterate())


kundi AsyncGenSyntaxTest(unittest.TestCase):

    eleza test_async_gen_syntax_01(self):
        code = '''async eleza foo():
            await abc
            yield kutoka 123
        '''

        with self.assertRaisesRegex(SyntaxError, 'yield kutoka.*inside async'):
            exec(code, {}, {})

    eleza test_async_gen_syntax_02(self):
        code = '''async eleza foo():
            yield kutoka 123
        '''

        with self.assertRaisesRegex(SyntaxError, 'yield kutoka.*inside async'):
            exec(code, {}, {})

    eleza test_async_gen_syntax_03(self):
        code = '''async eleza foo():
            await abc
            yield
            rudisha 123
        '''

        with self.assertRaisesRegex(SyntaxError, 'return.*value.*async gen'):
            exec(code, {}, {})

    eleza test_async_gen_syntax_04(self):
        code = '''async eleza foo():
            yield
            rudisha 123
        '''

        with self.assertRaisesRegex(SyntaxError, 'return.*value.*async gen'):
            exec(code, {}, {})

    eleza test_async_gen_syntax_05(self):
        code = '''async eleza foo():
            ikiwa 0:
                yield
            rudisha 12
        '''

        with self.assertRaisesRegex(SyntaxError, 'return.*value.*async gen'):
            exec(code, {}, {})


kundi AsyncGenTest(unittest.TestCase):

    eleza compare_generators(self, sync_gen, async_gen):
        eleza sync_iterate(g):
            res = []
            while True:
                try:
                    res.append(g.__next__())
                except StopIteration:
                    res.append('STOP')
                    break
                except Exception as ex:
                    res.append(str(type(ex)))
            rudisha res

        eleza async_iterate(g):
            res = []
            while True:
                an = g.__anext__()
                try:
                    while True:
                        try:
                            an.__next__()
                        except StopIteration as ex:
                            ikiwa ex.args:
                                res.append(ex.args[0])
                                break
                            else:
                                res.append('EMPTY StopIteration')
                                break
                        except StopAsyncIteration:
                            raise
                        except Exception as ex:
                            res.append(str(type(ex)))
                            break
                except StopAsyncIteration:
                    res.append('STOP')
                    break
            rudisha res

        sync_gen_result = sync_iterate(sync_gen)
        async_gen_result = async_iterate(async_gen)
        self.assertEqual(sync_gen_result, async_gen_result)
        rudisha async_gen_result

    eleza test_async_gen_iteration_01(self):
        async eleza gen():
            await awaitable()
            a = yield 123
            self.assertIs(a, None)
            await awaitable()
            yield 456
            await awaitable()
            yield 789

        self.assertEqual(to_list(gen()), [123, 456, 789])

    eleza test_async_gen_iteration_02(self):
        async eleza gen():
            await awaitable()
            yield 123
            await awaitable()

        g = gen()
        ai = g.__aiter__()

        an = ai.__anext__()
        self.assertEqual(an.__next__(), ('result',))

        try:
            an.__next__()
        except StopIteration as ex:
            self.assertEqual(ex.args[0], 123)
        else:
            self.fail('StopIteration was not raised')

        an = ai.__anext__()
        self.assertEqual(an.__next__(), ('result',))

        try:
            an.__next__()
        except StopAsyncIteration as ex:
            self.assertFalse(ex.args)
        else:
            self.fail('StopAsyncIteration was not raised')

    eleza test_async_gen_exception_03(self):
        async eleza gen():
            await awaitable()
            yield 123
            await awaitable(throw=True)
            yield 456

        with self.assertRaises(AwaitException):
            to_list(gen())

    eleza test_async_gen_exception_04(self):
        async eleza gen():
            await awaitable()
            yield 123
            1 / 0

        g = gen()
        ai = g.__aiter__()
        an = ai.__anext__()
        self.assertEqual(an.__next__(), ('result',))

        try:
            an.__next__()
        except StopIteration as ex:
            self.assertEqual(ex.args[0], 123)
        else:
            self.fail('StopIteration was not raised')

        with self.assertRaises(ZeroDivisionError):
            ai.__anext__().__next__()

    eleza test_async_gen_exception_05(self):
        async eleza gen():
            yield 123
            raise StopAsyncIteration

        with self.assertRaisesRegex(RuntimeError,
                                    'async generator.*StopAsyncIteration'):
            to_list(gen())

    eleza test_async_gen_exception_06(self):
        async eleza gen():
            yield 123
            raise StopIteration

        with self.assertRaisesRegex(RuntimeError,
                                    'async generator.*StopIteration'):
            to_list(gen())

    eleza test_async_gen_exception_07(self):
        eleza sync_gen():
            try:
                yield 1
                1 / 0
            finally:
                yield 2
                yield 3

            yield 100

        async eleza async_gen():
            try:
                yield 1
                1 / 0
            finally:
                yield 2
                yield 3

            yield 100

        self.compare_generators(sync_gen(), async_gen())

    eleza test_async_gen_exception_08(self):
        eleza sync_gen():
            try:
                yield 1
            finally:
                yield 2
                1 / 0
                yield 3

            yield 100

        async eleza async_gen():
            try:
                yield 1
                await awaitable()
            finally:
                await awaitable()
                yield 2
                1 / 0
                yield 3

            yield 100

        self.compare_generators(sync_gen(), async_gen())

    eleza test_async_gen_exception_09(self):
        eleza sync_gen():
            try:
                yield 1
                1 / 0
            finally:
                yield 2
                yield 3

            yield 100

        async eleza async_gen():
            try:
                await awaitable()
                yield 1
                1 / 0
            finally:
                yield 2
                await awaitable()
                yield 3

            yield 100

        self.compare_generators(sync_gen(), async_gen())

    eleza test_async_gen_exception_10(self):
        async eleza gen():
            yield 123
        with self.assertRaisesRegex(TypeError,
                                    "non-None value .* async generator"):
            gen().__anext__().send(100)

    eleza test_async_gen_exception_11(self):
        eleza sync_gen():
            yield 10
            yield 20

        eleza sync_gen_wrapper():
            yield 1
            sg = sync_gen()
            sg.send(None)
            try:
                sg.throw(GeneratorExit())
            except GeneratorExit:
                yield 2
            yield 3

        async eleza async_gen():
            yield 10
            yield 20

        async eleza async_gen_wrapper():
            yield 1
            asg = async_gen()
            await asg.asend(None)
            try:
                await asg.athrow(GeneratorExit())
            except GeneratorExit:
                yield 2
            yield 3

        self.compare_generators(sync_gen_wrapper(), async_gen_wrapper())

    eleza test_async_gen_api_01(self):
        async eleza gen():
            yield 123

        g = gen()

        self.assertEqual(g.__name__, 'gen')
        g.__name__ = '123'
        self.assertEqual(g.__name__, '123')

        self.assertIn('.gen', g.__qualname__)
        g.__qualname__ = '123'
        self.assertEqual(g.__qualname__, '123')

        self.assertIsNone(g.ag_await)
        self.assertIsInstance(g.ag_frame, types.FrameType)
        self.assertFalse(g.ag_running)
        self.assertIsInstance(g.ag_code, types.CodeType)

        self.assertTrue(inspect.isawaitable(g.aclose()))


kundi AsyncGenAsyncioTest(unittest.TestCase):

    eleza setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    eleza tearDown(self):
        self.loop.close()
        self.loop = None
        asyncio.set_event_loop_policy(None)

    async eleza to_list(self, gen):
        res = []
        async for i in gen:
            res.append(i)
        rudisha res

    eleza test_async_gen_asyncio_01(self):
        async eleza gen():
            yield 1
            await asyncio.sleep(0.01)
            yield 2
            await asyncio.sleep(0.01)
            return
            yield 3

        res = self.loop.run_until_complete(self.to_list(gen()))
        self.assertEqual(res, [1, 2])

    eleza test_async_gen_asyncio_02(self):
        async eleza gen():
            yield 1
            await asyncio.sleep(0.01)
            yield 2
            1 / 0
            yield 3

        with self.assertRaises(ZeroDivisionError):
            self.loop.run_until_complete(self.to_list(gen()))

    eleza test_async_gen_asyncio_03(self):
        loop = self.loop

        kundi Gen:
            async eleza __aiter__(self):
                yield 1
                await asyncio.sleep(0.01)
                yield 2

        res = loop.run_until_complete(self.to_list(Gen()))
        self.assertEqual(res, [1, 2])

    eleza test_async_gen_asyncio_anext_04(self):
        async eleza foo():
            yield 1
            await asyncio.sleep(0.01)
            try:
                yield 2
                yield 3
            except ZeroDivisionError:
                yield 1000
            await asyncio.sleep(0.01)
            yield 4

        async eleza run1():
            it = foo().__aiter__()

            self.assertEqual(await it.__anext__(), 1)
            self.assertEqual(await it.__anext__(), 2)
            self.assertEqual(await it.__anext__(), 3)
            self.assertEqual(await it.__anext__(), 4)
            with self.assertRaises(StopAsyncIteration):
                await it.__anext__()
            with self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        async eleza run2():
            it = foo().__aiter__()

            self.assertEqual(await it.__anext__(), 1)
            self.assertEqual(await it.__anext__(), 2)
            try:
                it.__anext__().throw(ZeroDivisionError)
            except StopIteration as ex:
                self.assertEqual(ex.args[0], 1000)
            else:
                self.fail('StopIteration was not raised')
            self.assertEqual(await it.__anext__(), 4)
            with self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        self.loop.run_until_complete(run1())
        self.loop.run_until_complete(run2())

    eleza test_async_gen_asyncio_anext_05(self):
        async eleza foo():
            v = yield 1
            v = yield v
            yield v * 100

        async eleza run():
            it = foo().__aiter__()

            try:
                it.__anext__().send(None)
            except StopIteration as ex:
                self.assertEqual(ex.args[0], 1)
            else:
                self.fail('StopIteration was not raised')

            try:
                it.__anext__().send(10)
            except StopIteration as ex:
                self.assertEqual(ex.args[0], 10)
            else:
                self.fail('StopIteration was not raised')

            try:
                it.__anext__().send(12)
            except StopIteration as ex:
                self.assertEqual(ex.args[0], 1200)
            else:
                self.fail('StopIteration was not raised')

            with self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_anext_06(self):
        DONE = 0

        # test synchronous generators
        eleza foo():
            try:
                yield
            except:
                pass
        g = foo()
        g.send(None)
        with self.assertRaises(StopIteration):
            g.send(None)

        # now with asynchronous generators

        async eleza gen():
            nonlocal DONE
            try:
                yield
            except:
                pass
            DONE = 1

        async eleza run():
            nonlocal DONE
            g = gen()
            await g.asend(None)
            with self.assertRaises(StopAsyncIteration):
                await g.asend(None)
            DONE += 10

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 11)

    eleza test_async_gen_asyncio_anext_tuple(self):
        async eleza foo():
            try:
                yield (1,)
            except ZeroDivisionError:
                yield (2,)

        async eleza run():
            it = foo().__aiter__()

            self.assertEqual(await it.__anext__(), (1,))
            with self.assertRaises(StopIteration) as cm:
                it.__anext__().throw(ZeroDivisionError)
            self.assertEqual(cm.exception.args[0], (2,))
            with self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_anext_stopiteration(self):
        async eleza foo():
            try:
                yield StopIteration(1)
            except ZeroDivisionError:
                yield StopIteration(3)

        async eleza run():
            it = foo().__aiter__()

            v = await it.__anext__()
            self.assertIsInstance(v, StopIteration)
            self.assertEqual(v.value, 1)
            with self.assertRaises(StopIteration) as cm:
                it.__anext__().throw(ZeroDivisionError)
            v = cm.exception.args[0]
            self.assertIsInstance(v, StopIteration)
            self.assertEqual(v.value, 3)
            with self.assertRaises(StopAsyncIteration):
                await it.__anext__()

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_aclose_06(self):
        async eleza foo():
            try:
                yield 1
                1 / 0
            finally:
                await asyncio.sleep(0.01)
                yield 12

        async eleza run():
            gen = foo()
            it = gen.__aiter__()
            await it.__anext__()
            await gen.aclose()

        with self.assertRaisesRegex(
                RuntimeError,
                "async generator ignored GeneratorExit"):
            self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_aclose_07(self):
        DONE = 0

        async eleza foo():
            nonlocal DONE
            try:
                yield 1
                1 / 0
            finally:
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
            try:
                yield 1
                await fut
                DONE += 1000
                yield 2
            finally:
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
            try:
                while True:
                    yield 1
            finally:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()
            await g.__anext__()
            await g.__anext__()
            del g

            await asyncio.sleep(0.1)

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_aclose_10(self):
        DONE = 0

        # test synchronous generators
        eleza foo():
            try:
                yield
            except:
                pass
        g = foo()
        g.send(None)
        g.close()

        # now with asynchronous generators

        async eleza gen():
            nonlocal DONE
            try:
                yield
            except:
                pass
            DONE = 1

        async eleza run():
            nonlocal DONE
            g = gen()
            await g.asend(None)
            await g.aclose()
            DONE += 10

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 11)

    eleza test_async_gen_asyncio_aclose_11(self):
        DONE = 0

        # test synchronous generators
        eleza foo():
            try:
                yield
            except:
                pass
            yield
        g = foo()
        g.send(None)
        with self.assertRaisesRegex(RuntimeError, 'ignored GeneratorExit'):
            g.close()

        # now with asynchronous generators

        async eleza gen():
            nonlocal DONE
            try:
                yield
            except:
                pass
            yield
            DONE += 1

        async eleza run():
            nonlocal DONE
            g = gen()
            await g.asend(None)
            with self.assertRaisesRegex(RuntimeError, 'ignored GeneratorExit'):
                await g.aclose()
            DONE += 10

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 10)

    eleza test_async_gen_asyncio_asend_01(self):
        DONE = 0

        # Sanity check:
        eleza sgen():
            v = yield 1
            yield v * 2
        sg = sgen()
        v = sg.send(None)
        self.assertEqual(v, 1)
        v = sg.send(100)
        self.assertEqual(v, 200)

        async eleza gen():
            nonlocal DONE
            try:
                await asyncio.sleep(0.01)
                v = yield 1
                await asyncio.sleep(0.01)
                yield v * 2
                await asyncio.sleep(0.01)
                return
            finally:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(None)
            self.assertEqual(v, 1)

            v = await g.asend(100)
            self.assertEqual(v, 200)

            with self.assertRaises(StopAsyncIteration):
                await g.asend(None)

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_asend_02(self):
        DONE = 0

        async eleza sleep_n_crash(delay):
            await asyncio.sleep(delay)
            1 / 0

        async eleza gen():
            nonlocal DONE
            try:
                await asyncio.sleep(0.01)
                v = yield 1
                await sleep_n_crash(0.01)
                DONE += 1000
                yield v * 2
            finally:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(None)
            self.assertEqual(v, 1)

            await g.asend(100)

        with self.assertRaises(ZeroDivisionError):
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
            try:
                await asyncio.sleep(0.01)
                v = yield 1
                await sleep_n_crash(0.01)
                DONE += 1000
                yield v * 2
            finally:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(None)
            self.assertEqual(v, 1)

            await g.asend(100)

        with self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_athrow_01(self):
        DONE = 0

        kundi FooEr(Exception):
            pass

        # Sanity check:
        eleza sgen():
            try:
                v = yield 1
            except FooEr:
                v = 1000
            yield v * 2
        sg = sgen()
        v = sg.send(None)
        self.assertEqual(v, 1)
        v = sg.throw(FooEr)
        self.assertEqual(v, 2000)
        with self.assertRaises(StopIteration):
            sg.send(None)

        async eleza gen():
            nonlocal DONE
            try:
                await asyncio.sleep(0.01)
                try:
                    v = yield 1
                except FooEr:
                    v = 1000
                    await asyncio.sleep(0.01)
                yield v * 2
                await asyncio.sleep(0.01)
                # return
            finally:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(None)
            self.assertEqual(v, 1)

            v = await g.athrow(FooEr)
            self.assertEqual(v, 2000)

            with self.assertRaises(StopAsyncIteration):
                await g.asend(None)

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_athrow_02(self):
        DONE = 0

        kundi FooEr(Exception):
            pass

        async eleza sleep_n_crash(delay):
            fut = asyncio.ensure_future(asyncio.sleep(delay),
                                        loop=self.loop)
            self.loop.call_later(delay / 2, lambda: fut.cancel())
            rudisha await fut

        async eleza gen():
            nonlocal DONE
            try:
                await asyncio.sleep(0.01)
                try:
                    v = yield 1
                except FooEr:
                    await sleep_n_crash(0.01)
                yield v * 2
                await asyncio.sleep(0.01)
                # return
            finally:
                await asyncio.sleep(0.01)
                await asyncio.sleep(0.01)
                DONE = 1

        async eleza run():
            g = gen()

            v = await g.asend(None)
            self.assertEqual(v, 1)

            try:
                await g.athrow(FooEr)
            except asyncio.CancelledError:
                self.assertEqual(DONE, 1)
                raise
            else:
                self.fail('CancelledError was not raised')

        with self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(run())
        self.assertEqual(DONE, 1)

    eleza test_async_gen_asyncio_athrow_03(self):
        DONE = 0

        # test synchronous generators
        eleza foo():
            try:
                yield
            except:
                pass
        g = foo()
        g.send(None)
        with self.assertRaises(StopIteration):
            g.throw(ValueError)

        # now with asynchronous generators

        async eleza gen():
            nonlocal DONE
            try:
                yield
            except:
                pass
            DONE = 1

        async eleza run():
            nonlocal DONE
            g = gen()
            await g.asend(None)
            with self.assertRaises(StopAsyncIteration):
                await g.athrow(ValueError)
            DONE += 10

        self.loop.run_until_complete(run())
        self.assertEqual(DONE, 11)

    eleza test_async_gen_asyncio_athrow_tuple(self):
        async eleza gen():
            try:
                yield 1
            except ZeroDivisionError:
                yield (2,)

        async eleza run():
            g = gen()
            v = await g.asend(None)
            self.assertEqual(v, 1)
            v = await g.athrow(ZeroDivisionError)
            self.assertEqual(v, (2,))
            with self.assertRaises(StopAsyncIteration):
                await g.asend(None)

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_athrow_stopiteration(self):
        async eleza gen():
            try:
                yield 1
            except ZeroDivisionError:
                yield StopIteration(2)

        async eleza run():
            g = gen()
            v = await g.asend(None)
            self.assertEqual(v, 1)
            v = await g.athrow(ZeroDivisionError)
            self.assertIsInstance(v, StopIteration)
            self.assertEqual(v.value, 2)
            with self.assertRaises(StopAsyncIteration):
                await g.asend(None)

        self.loop.run_until_complete(run())

    eleza test_async_gen_asyncio_shutdown_01(self):
        finalized = 0

        async eleza waiter(timeout):
            nonlocal finalized
            try:
                await asyncio.sleep(timeout)
                yield 1
            finally:
                await asyncio.sleep(0)
                finalized += 1

        async eleza wait():
            async for _ in waiter(1):
                pass

        t1 = self.loop.create_task(wait())
        t2 = self.loop.create_task(wait())

        self.loop.run_until_complete(asyncio.sleep(0.1))

        # Silence warnings
        t1.cancel()
        t2.cancel()

        with self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(t1)
        with self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(t2)

        self.loop.run_until_complete(self.loop.shutdown_asyncgens())

        self.assertEqual(finalized, 2)

    eleza test_async_gen_expression_01(self):
        async eleza arange(n):
            for i in range(n):
                await asyncio.sleep(0.01)
                yield i

        eleza make_arange(n):
            # This syntax is legal starting with Python 3.7
            rudisha (i * 2 async for i in arange(n))

        async eleza run():
            rudisha [i async for i in make_arange(10)]

        res = self.loop.run_until_complete(run())
        self.assertEqual(res, [i * 2 for i in range(10)])

    eleza test_async_gen_expression_02(self):
        async eleza wrap(n):
            await asyncio.sleep(0.01)
            rudisha n

        eleza make_arange(n):
            # This syntax is legal starting with Python 3.7
            rudisha (i * 2 for i in range(n) ikiwa await wrap(i))

        async eleza run():
            rudisha [i async for i in make_arange(10)]

        res = self.loop.run_until_complete(run())
        self.assertEqual(res, [i * 2 for i in range(1, 10)])

    eleza test_asyncgen_nonstarted_hooks_are_cancellable(self):
        # See https://bugs.python.org/issue38013
        messages = []

        eleza exception_handler(loop, context):
            messages.append(context)

        async eleza async_iterate():
            yield 1
            yield 2

        async eleza main():
            loop = asyncio.get_running_loop()
            loop.set_exception_handler(exception_handler)

            async for i in async_iterate():
                break

        asyncio.run(main())

        self.assertEqual([], messages)


ikiwa __name__ == "__main__":
    unittest.main()
