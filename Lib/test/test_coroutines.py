agiza contextlib
agiza copy
agiza inspect
agiza pickle
agiza sys
agiza types
agiza unittest
agiza warnings
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok


kundi AsyncYieldFrom:
    eleza __init__(self, obj):
        self.obj = obj

    eleza __await__(self):
        yield kutoka self.obj


kundi AsyncYield:
    eleza __init__(self, value):
        self.value = value

    eleza __await__(self):
        yield self.value


eleza run_async(coro):
    assert coro.__class__ in {types.GeneratorType, types.CoroutineType}

    buffer = []
    result = None
    while True:
        try:
            buffer.append(coro.send(None))
        except StopIteration as ex:
            result = ex.args[0] ikiwa ex.args else None
            break
    rudisha buffer, result


eleza run_async__await__(coro):
    assert coro.__class__ is types.CoroutineType
    aw = coro.__await__()
    buffer = []
    result = None
    i = 0
    while True:
        try:
            ikiwa i % 2:
                buffer.append(next(aw))
            else:
                buffer.append(aw.send(None))
            i += 1
        except StopIteration as ex:
            result = ex.args[0] ikiwa ex.args else None
            break
    rudisha buffer, result


@contextlib.contextmanager
eleza silence_coro_gc():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield
        support.gc_collect()


kundi AsyncBadSyntaxTest(unittest.TestCase):

    eleza test_badsyntax_1(self):
        samples = [
            """eleza foo():
                await something()
            """,

            """await something()""",

            """async eleza foo():
                yield kutoka []
            """,

            """async eleza foo():
                await await fut
            """,

            """async eleza foo(a=await something()):
                pass
            """,

            """async eleza foo(a:await something()):
                pass
            """,

            """async eleza foo():
                eleza bar():
                 [i async for i in els]
            """,

            """async eleza foo():
                eleza bar():
                 [await i for i in els]
            """,

            """async eleza foo():
                eleza bar():
                 [i for i in els
                    async for b in els]
            """,

            """async eleza foo():
                eleza bar():
                 [i for i in els
                    for c in b
                    async for b in els]
            """,

            """async eleza foo():
                eleza bar():
                 [i for i in els
                    async for b in els
                    for c in b]
            """,

            """async eleza foo():
                eleza bar():
                 [i for i in els
                    for b in await els]
            """,

            """async eleza foo():
                eleza bar():
                 [i for i in els
                    for b in els
                        ikiwa await b]
            """,

            """async eleza foo():
                eleza bar():
                 [i for i in await els]
            """,

            """async eleza foo():
                eleza bar():
                 [i for i in els ikiwa await i]
            """,

            """eleza bar():
                 [i async for i in els]
            """,

            """eleza bar():
                 {i: i async for i in els}
            """,

            """eleza bar():
                 {i async for i in els}
            """,

            """eleza bar():
                 [await i for i in els]
            """,

            """eleza bar():
                 [i for i in els
                    async for b in els]
            """,

            """eleza bar():
                 [i for i in els
                    for c in b
                    async for b in els]
            """,

            """eleza bar():
                 [i for i in els
                    async for b in els
                    for c in b]
            """,

            """eleza bar():
                 [i for i in els
                    for b in await els]
            """,

            """eleza bar():
                 [i for i in els
                    for b in els
                        ikiwa await b]
            """,

            """eleza bar():
                 [i for i in await els]
            """,

            """eleza bar():
                 [i for i in els ikiwa await i]
            """,

            """async eleza foo():
                await
            """,

            """async eleza foo():
                   eleza bar(): pass
                   await = 1
            """,

            """async eleza foo():

                   eleza bar(): pass
                   await = 1
            """,

            """async eleza foo():
                   eleza bar(): pass
                   ikiwa 1:
                       await = 1
            """,

            """eleza foo():
                   async eleza bar(): pass
                   ikiwa 1:
                       await a
            """,

            """eleza foo():
                   async eleza bar(): pass
                   await a
            """,

            """eleza foo():
                   eleza baz(): pass
                   async eleza bar(): pass
                   await a
            """,

            """eleza foo():
                   eleza baz(): pass
                   # 456
                   async eleza bar(): pass
                   # 123
                   await a
            """,

            """async eleza foo():
                   eleza baz(): pass
                   # 456
                   async eleza bar(): pass
                   # 123
                   await = 2
            """,

            """eleza foo():

                   eleza baz(): pass

                   async eleza bar(): pass

                   await a
            """,

            """async eleza foo():

                   eleza baz(): pass

                   async eleza bar(): pass

                   await = 2
            """,

            """async eleza foo():
                   eleza async(): pass
            """,

            """async eleza foo():
                   eleza await(): pass
            """,

            """async eleza foo():
                   eleza bar():
                       await
            """,

            """async eleza foo():
                   rudisha lambda async: await
            """,

            """async eleza foo():
                   rudisha lambda a: await
            """,

            """await a()""",

            """async eleza foo(a=await b):
                   pass
            """,

            """async eleza foo(a:await b):
                   pass
            """,

            """eleza baz():
                   async eleza foo(a=await b):
                       pass
            """,

            """async eleza foo(async):
                   pass
            """,

            """async eleza foo():
                   eleza bar():
                        eleza baz():
                            async = 1
            """,

            """async eleza foo():
                   eleza bar():
                        eleza baz():
                            pass
                        async = 1
            """,

            """eleza foo():
                   async eleza bar():

                        async eleza baz():
                            pass

                        eleza baz():
                            42

                        async = 1
            """,

            """async eleza foo():
                   eleza bar():
                        eleza baz():
                            pass\nawait foo()
            """,

            """eleza foo():
                   eleza bar():
                        async eleza baz():
                            pass\nawait foo()
            """,

            """async eleza foo(await):
                   pass
            """,

            """eleza foo():

                   async eleza bar(): pass

                   await a
            """,

            """eleza foo():
                   async eleza bar():
                        pass\nawait a
            """,
            """eleza foo():
                   async for i in arange(2):
                       pass
            """,
            """eleza foo():
                   async with resource:
                       pass
            """,
            """async with resource:
                   pass
            """,
            """async for i in arange(2):
                   pass
            """,
            ]

        for code in samples:
            with self.subTest(code=code), self.assertRaises(SyntaxError):
                compile(code, "<test>", "exec")

    eleza test_badsyntax_2(self):
        samples = [
            """eleza foo():
                await = 1
            """,

            """kundi Bar:
                eleza async(): pass
            """,

            """kundi Bar:
                async = 1
            """,

            """kundi async:
                pass
            """,

            """kundi await:
                pass
            """,

            """agiza math as await""",

            """eleza async():
                pass""",

            """eleza foo(*, await=1):
                pass"""

            """async = 1""",

            """andika(await=1)"""
        ]

        for code in samples:
            with self.subTest(code=code), self.assertRaises(SyntaxError):
                compile(code, "<test>", "exec")

    eleza test_badsyntax_3(self):
        with self.assertRaises(SyntaxError):
            compile("async = 1", "<test>", "exec")

    eleza test_badsyntax_4(self):
        samples = [
            '''eleza foo(await):
                async eleza foo(): pass
                async eleza foo():
                    pass
                rudisha await + 1
            ''',

            '''eleza foo(await):
                async eleza foo(): pass
                async eleza foo(): pass
                rudisha await + 1
            ''',

            '''eleza foo(await):

                async eleza foo(): pass

                async eleza foo(): pass

                rudisha await + 1
            ''',

            '''eleza foo(await):
                """spam"""
                async eleza foo(): \
                    pass
                # 123
                async eleza foo(): pass
                # 456
                rudisha await + 1
            ''',

            '''eleza foo(await):
                eleza foo(): pass
                eleza foo(): pass
                async eleza bar(): rudisha await_
                await_ = await
                try:
                    bar().send(None)
                except StopIteration as ex:
                    rudisha ex.args[0] + 1
            '''
        ]

        for code in samples:
            with self.subTest(code=code), self.assertRaises(SyntaxError):
                compile(code, "<test>", "exec")


kundi TokenizerRegrTest(unittest.TestCase):

    eleza test_oneline_defs(self):
        buf = []
        for i in range(500):
            buf.append('eleza i{i}(): rudisha {i}'.format(i=i))
        buf = '\n'.join(buf)

        # Test that 500 consequent, one-line defs is OK
        ns = {}
        exec(buf, ns, ns)
        self.assertEqual(ns['i499'](), 499)

        # Test that 500 consequent, one-line defs *and*
        # one 'async def' following them is OK
        buf += '\nasync eleza foo():\n    return'
        ns = {}
        exec(buf, ns, ns)
        self.assertEqual(ns['i499'](), 499)
        self.assertTrue(inspect.iscoroutinefunction(ns['foo']))


kundi CoroutineTest(unittest.TestCase):

    eleza test_gen_1(self):
        eleza gen(): yield
        self.assertFalse(hasattr(gen, '__await__'))

    eleza test_func_1(self):
        async eleza foo():
            rudisha 10

        f = foo()
        self.assertIsInstance(f, types.CoroutineType)
        self.assertTrue(bool(foo.__code__.co_flags & inspect.CO_COROUTINE))
        self.assertFalse(bool(foo.__code__.co_flags & inspect.CO_GENERATOR))
        self.assertTrue(bool(f.cr_code.co_flags & inspect.CO_COROUTINE))
        self.assertFalse(bool(f.cr_code.co_flags & inspect.CO_GENERATOR))
        self.assertEqual(run_async(f), ([], 10))

        self.assertEqual(run_async__await__(foo()), ([], 10))

        eleza bar(): pass
        self.assertFalse(bool(bar.__code__.co_flags & inspect.CO_COROUTINE))

    eleza test_func_2(self):
        async eleza foo():
            raise StopIteration

        with self.assertRaisesRegex(
                RuntimeError, "coroutine raised StopIteration"):

            run_async(foo())

    eleza test_func_3(self):
        async eleza foo():
            raise StopIteration

        coro = foo()
        self.assertRegex(repr(coro), '^<coroutine object.* at 0x.*>$')
        coro.close()

    eleza test_func_4(self):
        async eleza foo():
            raise StopIteration
        coro = foo()

        check = lambda: self.assertRaisesRegex(
            TypeError, "'coroutine' object is not iterable")

        with check():
            list(coro)

        with check():
            tuple(coro)

        with check():
            sum(coro)

        with check():
            iter(coro)

        with check():
            for i in coro:
                pass

        with check():
            [i for i in coro]

        coro.close()

    eleza test_func_5(self):
        @types.coroutine
        eleza bar():
            yield 1

        async eleza foo():
            await bar()

        check = lambda: self.assertRaisesRegex(
            TypeError, "'coroutine' object is not iterable")

        coro = foo()
        with check():
            for el in coro:
                pass
        coro.close()

        # the following should pass without an error
        for el in bar():
            self.assertEqual(el, 1)
        self.assertEqual([el for el in bar()], [1])
        self.assertEqual(tuple(bar()), (1,))
        self.assertEqual(next(iter(bar())), 1)

    eleza test_func_6(self):
        @types.coroutine
        eleza bar():
            yield 1
            yield 2

        async eleza foo():
            await bar()

        f = foo()
        self.assertEqual(f.send(None), 1)
        self.assertEqual(f.send(None), 2)
        with self.assertRaises(StopIteration):
            f.send(None)

    eleza test_func_7(self):
        async eleza bar():
            rudisha 10
        coro = bar()

        eleza foo():
            yield kutoka coro

        with self.assertRaisesRegex(
                TypeError,
                "cannot 'yield kutoka' a coroutine object in "
                "a non-coroutine generator"):
            list(foo())

        coro.close()

    eleza test_func_8(self):
        @types.coroutine
        eleza bar():
            rudisha (yield kutoka coro)

        async eleza foo():
            rudisha 'spam'

        coro = foo()
        self.assertEqual(run_async(bar()), ([], 'spam'))
        coro.close()

    eleza test_func_9(self):
        async eleza foo():
            pass

        with self.assertWarnsRegex(
                RuntimeWarning,
                r"coroutine '.*test_func_9.*foo' was never awaited"):

            foo()
            support.gc_collect()

        with self.assertWarnsRegex(
                RuntimeWarning,
                r"coroutine '.*test_func_9.*foo' was never awaited"):

            with self.assertRaises(TypeError):
                # See bpo-32703.
                for _ in foo():
                    pass

            support.gc_collect()

    eleza test_func_10(self):
        N = 0

        @types.coroutine
        eleza gen():
            nonlocal N
            try:
                a = yield
                yield (a ** 2)
            except ZeroDivisionError:
                N += 100
                raise
            finally:
                N += 1

        async eleza foo():
            await gen()

        coro = foo()
        aw = coro.__await__()
        self.assertIs(aw, iter(aw))
        next(aw)
        self.assertEqual(aw.send(10), 100)

        self.assertEqual(N, 0)
        aw.close()
        self.assertEqual(N, 1)

        coro = foo()
        aw = coro.__await__()
        next(aw)
        with self.assertRaises(ZeroDivisionError):
            aw.throw(ZeroDivisionError, None, None)
        self.assertEqual(N, 102)

    eleza test_func_11(self):
        async eleza func(): pass
        coro = func()
        # Test that PyCoro_Type and _PyCoroWrapper_Type types were properly
        # initialized
        self.assertIn('__await__', dir(coro))
        self.assertIn('__iter__', dir(coro.__await__()))
        self.assertIn('coroutine_wrapper', repr(coro.__await__()))
        coro.close() # avoid RuntimeWarning

    eleza test_func_12(self):
        async eleza g():
            i = me.send(None)
            await foo
        me = g()
        with self.assertRaisesRegex(ValueError,
                                    "coroutine already executing"):
            me.send(None)

    eleza test_func_13(self):
        async eleza g():
            pass

        coro = g()
        with self.assertRaisesRegex(
                TypeError,
                "can't send non-None value to a just-started coroutine"):
            coro.send('spam')

        coro.close()

    eleza test_func_14(self):
        @types.coroutine
        eleza gen():
            yield
        async eleza coro():
            try:
                await gen()
            except GeneratorExit:
                await gen()
        c = coro()
        c.send(None)
        with self.assertRaisesRegex(RuntimeError,
                                    "coroutine ignored GeneratorExit"):
            c.close()

    eleza test_func_15(self):
        # See http://bugs.python.org/issue25887 for details

        async eleza spammer():
            rudisha 'spam'
        async eleza reader(coro):
            rudisha await coro

        spammer_coro = spammer()

        with self.assertRaisesRegex(StopIteration, 'spam'):
            reader(spammer_coro).send(None)

        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            reader(spammer_coro).send(None)

    eleza test_func_16(self):
        # See http://bugs.python.org/issue25887 for details

        @types.coroutine
        eleza nop():
            yield
        async eleza send():
            await nop()
            rudisha 'spam'
        async eleza read(coro):
            await nop()
            rudisha await coro

        spammer = send()

        reader = read(spammer)
        reader.send(None)
        reader.send(None)
        with self.assertRaisesRegex(Exception, 'ham'):
            reader.throw(Exception('ham'))

        reader = read(spammer)
        reader.send(None)
        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            reader.send(None)

        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            reader.throw(Exception('wat'))

    eleza test_func_17(self):
        # See http://bugs.python.org/issue25887 for details

        async eleza coroutine():
            rudisha 'spam'

        coro = coroutine()
        with self.assertRaisesRegex(StopIteration, 'spam'):
            coro.send(None)

        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            coro.send(None)

        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            coro.throw(Exception('wat'))

        # Closing a coroutine shouldn't raise any exception even ikiwa it's
        # already closed/exhausted (similar to generators)
        coro.close()
        coro.close()

    eleza test_func_18(self):
        # See http://bugs.python.org/issue25887 for details

        async eleza coroutine():
            rudisha 'spam'

        coro = coroutine()
        await_iter = coro.__await__()
        it = iter(await_iter)

        with self.assertRaisesRegex(StopIteration, 'spam'):
            it.send(None)

        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            it.send(None)

        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            # Although the iterator protocol requires iterators to
            # raise another StopIteration here, we don't want to do
            # that.  In this particular case, the iterator will raise
            # a RuntimeError, so that 'yield kutoka' and 'await'
            # expressions will trigger the error, instead of silently
            # ignoring the call.
            next(it)

        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            it.throw(Exception('wat'))

        with self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            it.throw(Exception('wat'))

        # Closing a coroutine shouldn't raise any exception even ikiwa it's
        # already closed/exhausted (similar to generators)
        it.close()
        it.close()

    eleza test_func_19(self):
        CHK = 0

        @types.coroutine
        eleza foo():
            nonlocal CHK
            yield
            try:
                yield
            except GeneratorExit:
                CHK += 1

        async eleza coroutine():
            await foo()

        coro = coroutine()

        coro.send(None)
        coro.send(None)

        self.assertEqual(CHK, 0)
        coro.close()
        self.assertEqual(CHK, 1)

        for _ in range(3):
            # Closing a coroutine shouldn't raise any exception even ikiwa it's
            # already closed/exhausted (similar to generators)
            coro.close()
            self.assertEqual(CHK, 1)

    eleza test_coro_wrapper_send_tuple(self):
        async eleza foo():
            rudisha (10,)

        result = run_async__await__(foo())
        self.assertEqual(result, ([], (10,)))

    eleza test_coro_wrapper_send_stop_iterator(self):
        async eleza foo():
            rudisha StopIteration(10)

        result = run_async__await__(foo())
        self.assertIsInstance(result[1], StopIteration)
        self.assertEqual(result[1].value, 10)

    eleza test_cr_await(self):
        @types.coroutine
        eleza a():
            self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_RUNNING)
            self.assertIsNone(coro_b.cr_await)
            yield
            self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_RUNNING)
            self.assertIsNone(coro_b.cr_await)

        async eleza c():
            await a()

        async eleza b():
            self.assertIsNone(coro_b.cr_await)
            await c()
            self.assertIsNone(coro_b.cr_await)

        coro_b = b()
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_CREATED)
        self.assertIsNone(coro_b.cr_await)

        coro_b.send(None)
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_SUSPENDED)
        self.assertEqual(coro_b.cr_await.cr_await.gi_code.co_name, 'a')

        with self.assertRaises(StopIteration):
            coro_b.send(None)  # complete coroutine
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_CLOSED)
        self.assertIsNone(coro_b.cr_await)

    eleza test_corotype_1(self):
        ct = types.CoroutineType
        self.assertIn('into coroutine', ct.send.__doc__)
        self.assertIn('inside coroutine', ct.close.__doc__)
        self.assertIn('in coroutine', ct.throw.__doc__)
        self.assertIn('of the coroutine', ct.__dict__['__name__'].__doc__)
        self.assertIn('of the coroutine', ct.__dict__['__qualname__'].__doc__)
        self.assertEqual(ct.__name__, 'coroutine')

        async eleza f(): pass
        c = f()
        self.assertIn('coroutine object', repr(c))
        c.close()

    eleza test_await_1(self):

        async eleza foo():
            await 1
        with self.assertRaisesRegex(TypeError, "object int can.t.*await"):
            run_async(foo())

    eleza test_await_2(self):
        async eleza foo():
            await []
        with self.assertRaisesRegex(TypeError, "object list can.t.*await"):
            run_async(foo())

    eleza test_await_3(self):
        async eleza foo():
            await AsyncYieldFrom([1, 2, 3])

        self.assertEqual(run_async(foo()), ([1, 2, 3], None))
        self.assertEqual(run_async__await__(foo()), ([1, 2, 3], None))

    eleza test_await_4(self):
        async eleza bar():
            rudisha 42

        async eleza foo():
            rudisha await bar()

        self.assertEqual(run_async(foo()), ([], 42))

    eleza test_await_5(self):
        kundi Awaitable:
            eleza __await__(self):
                return

        async eleza foo():
            rudisha (await Awaitable())

        with self.assertRaisesRegex(
            TypeError, "__await__.*returned non-iterator of type"):

            run_async(foo())

    eleza test_await_6(self):
        kundi Awaitable:
            eleza __await__(self):
                rudisha iter([52])

        async eleza foo():
            rudisha (await Awaitable())

        self.assertEqual(run_async(foo()), ([52], None))

    eleza test_await_7(self):
        kundi Awaitable:
            eleza __await__(self):
                yield 42
                rudisha 100

        async eleza foo():
            rudisha (await Awaitable())

        self.assertEqual(run_async(foo()), ([42], 100))

    eleza test_await_8(self):
        kundi Awaitable:
            pass

        async eleza foo(): rudisha await Awaitable()

        with self.assertRaisesRegex(
            TypeError, "object Awaitable can't be used in 'await' expression"):

            run_async(foo())

    eleza test_await_9(self):
        eleza wrap():
            rudisha bar

        async eleza bar():
            rudisha 42

        async eleza foo():
            db = {'b':  lambda: wrap}

            kundi DB:
                b = wrap

            rudisha (await bar() + await wrap()() + await db['b']()()() +
                    await bar() * 1000 + await DB.b()())

        async eleza foo2():
            rudisha -await bar()

        self.assertEqual(run_async(foo()), ([], 42168))
        self.assertEqual(run_async(foo2()), ([], -42))

    eleza test_await_10(self):
        async eleza baz():
            rudisha 42

        async eleza bar():
            rudisha baz()

        async eleza foo():
            rudisha await (await bar())

        self.assertEqual(run_async(foo()), ([], 42))

    eleza test_await_11(self):
        eleza ident(val):
            rudisha val

        async eleza bar():
            rudisha 'spam'

        async eleza foo():
            rudisha ident(val=await bar())

        async eleza foo2():
            rudisha await bar(), 'ham'

        self.assertEqual(run_async(foo2()), ([], ('spam', 'ham')))

    eleza test_await_12(self):
        async eleza coro():
            rudisha 'spam'
        c = coro()

        kundi Awaitable:
            eleza __await__(self):
                rudisha c

        async eleza foo():
            rudisha await Awaitable()

        with self.assertRaisesRegex(
                TypeError, r"__await__\(\) returned a coroutine"):
            run_async(foo())

        c.close()

    eleza test_await_13(self):
        kundi Awaitable:
            eleza __await__(self):
                rudisha self

        async eleza foo():
            rudisha await Awaitable()

        with self.assertRaisesRegex(
            TypeError, "__await__.*returned non-iterator of type"):

            run_async(foo())

    eleza test_await_14(self):
        kundi Wrapper:
            # Forces the interpreter to use CoroutineType.__await__
            eleza __init__(self, coro):
                assert coro.__class__ is types.CoroutineType
                self.coro = coro
            eleza __await__(self):
                rudisha self.coro.__await__()

        kundi FutureLike:
            eleza __await__(self):
                rudisha (yield)

        kundi Marker(Exception):
            pass

        async eleza coro1():
            try:
                rudisha await FutureLike()
            except ZeroDivisionError:
                raise Marker
        async eleza coro2():
            rudisha await Wrapper(coro1())

        c = coro2()
        c.send(None)
        with self.assertRaisesRegex(StopIteration, 'spam'):
            c.send('spam')

        c = coro2()
        c.send(None)
        with self.assertRaises(Marker):
            c.throw(ZeroDivisionError)

    eleza test_await_15(self):
        @types.coroutine
        eleza nop():
            yield

        async eleza coroutine():
            await nop()

        async eleza waiter(coro):
            await coro

        coro = coroutine()
        coro.send(None)

        with self.assertRaisesRegex(RuntimeError,
                                    "coroutine is being awaited already"):
            waiter(coro).send(None)

    eleza test_await_16(self):
        # See https://bugs.python.org/issue29600 for details.

        async eleza f():
            rudisha ValueError()

        async eleza g():
            try:
                raise KeyError
            except:
                rudisha await f()

        _, result = run_async(g())
        self.assertIsNone(result.__context__)

    eleza test_with_1(self):
        kundi Manager:
            eleza __init__(self, name):
                self.name = name

            async eleza __aenter__(self):
                await AsyncYieldFrom(['enter-1-' + self.name,
                                      'enter-2-' + self.name])
                rudisha self

            async eleza __aexit__(self, *args):
                await AsyncYieldFrom(['exit-1-' + self.name,
                                      'exit-2-' + self.name])

                ikiwa self.name == 'B':
                    rudisha True


        async eleza foo():
            async with Manager("A") as a, Manager("B") as b:
                await AsyncYieldFrom([('managers', a.name, b.name)])
                1/0

        f = foo()
        result, _ = run_async(f)

        self.assertEqual(
            result, ['enter-1-A', 'enter-2-A', 'enter-1-B', 'enter-2-B',
                     ('managers', 'A', 'B'),
                     'exit-1-B', 'exit-2-B', 'exit-1-A', 'exit-2-A']
        )

        async eleza foo():
            async with Manager("A") as a, Manager("C") as c:
                await AsyncYieldFrom([('managers', a.name, c.name)])
                1/0

        with self.assertRaises(ZeroDivisionError):
            run_async(foo())

    eleza test_with_2(self):
        kundi CM:
            eleza __aenter__(self):
                pass

        async eleza foo():
            async with CM():
                pass

        with self.assertRaisesRegex(AttributeError, '__aexit__'):
            run_async(foo())

    eleza test_with_3(self):
        kundi CM:
            eleza __aexit__(self):
                pass

        async eleza foo():
            async with CM():
                pass

        with self.assertRaisesRegex(AttributeError, '__aenter__'):
            run_async(foo())

    eleza test_with_4(self):
        kundi CM:
            eleza __enter__(self):
                pass

            eleza __exit__(self):
                pass

        async eleza foo():
            async with CM():
                pass

        with self.assertRaisesRegex(AttributeError, '__aexit__'):
            run_async(foo())

    eleza test_with_5(self):
        # While this test doesn't make a lot of sense,
        # it's a regression test for an early bug with opcodes
        # generation

        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            async eleza __aexit__(self, *exc):
                pass

        async eleza func():
            async with CM():
                assert (1, ) == 1

        with self.assertRaises(AssertionError):
            run_async(func())

    eleza test_with_6(self):
        kundi CM:
            eleza __aenter__(self):
                rudisha 123

            eleza __aexit__(self, *e):
                rudisha 456

        async eleza foo():
            async with CM():
                pass

        with self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aenter__ "
                "that does not implement __await__: int"):
            # it's agizaant that __aexit__ wasn't called
            run_async(foo())

    eleza test_with_7(self):
        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            eleza __aexit__(self, *e):
                rudisha 444

        # Exit with exception
        async eleza foo():
            async with CM():
                1/0

        try:
            run_async(foo())
        except TypeError as exc:
            self.assertRegex(
                exc.args[0],
                "'async with' received an object kutoka __aexit__ "
                "that does not implement __await__: int")
            self.assertTrue(exc.__context__ is not None)
            self.assertTrue(isinstance(exc.__context__, ZeroDivisionError))
        else:
            self.fail('invalid asynchronous context manager did not fail')


    eleza test_with_8(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            eleza __aexit__(self, *e):
                rudisha 456

        # Normal exit
        async eleza foo():
            nonlocal CNT
            async with CM():
                CNT += 1
        with self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aexit__ "
                "that does not implement __await__: int"):
            run_async(foo())
        self.assertEqual(CNT, 1)

        # Exit with 'break'
        async eleza foo():
            nonlocal CNT
            for i in range(2):
                async with CM():
                    CNT += 1
                    break
        with self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aexit__ "
                "that does not implement __await__: int"):
            run_async(foo())
        self.assertEqual(CNT, 2)

        # Exit with 'continue'
        async eleza foo():
            nonlocal CNT
            for i in range(2):
                async with CM():
                    CNT += 1
                    continue
        with self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aexit__ "
                "that does not implement __await__: int"):
            run_async(foo())
        self.assertEqual(CNT, 3)

        # Exit with 'return'
        async eleza foo():
            nonlocal CNT
            async with CM():
                CNT += 1
                return
        with self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aexit__ "
                "that does not implement __await__: int"):
            run_async(foo())
        self.assertEqual(CNT, 4)


    eleza test_with_9(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            async eleza __aexit__(self, *e):
                1/0

        async eleza foo():
            nonlocal CNT
            async with CM():
                CNT += 1

        with self.assertRaises(ZeroDivisionError):
            run_async(foo())

        self.assertEqual(CNT, 1)

    eleza test_with_10(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            async eleza __aexit__(self, *e):
                1/0

        async eleza foo():
            nonlocal CNT
            async with CM():
                async with CM():
                    raise RuntimeError

        try:
            run_async(foo())
        except ZeroDivisionError as exc:
            self.assertTrue(exc.__context__ is not None)
            self.assertTrue(isinstance(exc.__context__, ZeroDivisionError))
            self.assertTrue(isinstance(exc.__context__.__context__,
                                       RuntimeError))
        else:
            self.fail('exception kutoka __aexit__ did not propagate')

    eleza test_with_11(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                raise NotImplementedError

            async eleza __aexit__(self, *e):
                1/0

        async eleza foo():
            nonlocal CNT
            async with CM():
                raise RuntimeError

        try:
            run_async(foo())
        except NotImplementedError as exc:
            self.assertTrue(exc.__context__ is None)
        else:
            self.fail('exception kutoka __aenter__ did not propagate')

    eleza test_with_12(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            async eleza __aexit__(self, *e):
                rudisha True

        async eleza foo():
            nonlocal CNT
            async with CM() as cm:
                self.assertIs(cm.__class__, CM)
                raise RuntimeError

        run_async(foo())

    eleza test_with_13(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                1/0

            async eleza __aexit__(self, *e):
                rudisha True

        async eleza foo():
            nonlocal CNT
            CNT += 1
            async with CM():
                CNT += 1000
            CNT += 10000

        with self.assertRaises(ZeroDivisionError):
            run_async(foo())
        self.assertEqual(CNT, 1)

    eleza test_for_1(self):
        aiter_calls = 0

        kundi AsyncIter:
            eleza __init__(self):
                self.i = 0

            eleza __aiter__(self):
                nonlocal aiter_calls
                aiter_calls += 1
                rudisha self

            async eleza __anext__(self):
                self.i += 1

                ikiwa not (self.i % 10):
                    await AsyncYield(self.i * 10)

                ikiwa self.i > 100:
                    raise StopAsyncIteration

                rudisha self.i, self.i


        buffer = []
        async eleza test1():
            async for i1, i2 in AsyncIter():
                buffer.append(i1 + i2)

        yielded, _ = run_async(test1())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 1)
        self.assertEqual(yielded, [i * 100 for i in range(1, 11)])
        self.assertEqual(buffer, [i*2 for i in range(1, 101)])


        buffer = []
        async eleza test2():
            nonlocal buffer
            async for i in AsyncIter():
                buffer.append(i[0])
                ikiwa i[0] == 20:
                    break
            else:
                buffer.append('what?')
            buffer.append('end')

        yielded, _ = run_async(test2())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 2)
        self.assertEqual(yielded, [100, 200])
        self.assertEqual(buffer, [i for i in range(1, 21)] + ['end'])


        buffer = []
        async eleza test3():
            nonlocal buffer
            async for i in AsyncIter():
                ikiwa i[0] > 20:
                    continue
                buffer.append(i[0])
            else:
                buffer.append('what?')
            buffer.append('end')

        yielded, _ = run_async(test3())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 3)
        self.assertEqual(yielded, [i * 100 for i in range(1, 11)])
        self.assertEqual(buffer, [i for i in range(1, 21)] +
                                 ['what?', 'end'])

    eleza test_for_2(self):
        tup = (1, 2, 3)
        refs_before = sys.getrefcount(tup)

        async eleza foo():
            async for i in tup:
                andika('never going to happen')

        with self.assertRaisesRegex(
                TypeError, "async for' requires an object.*__aiter__.*tuple"):

            run_async(foo())

        self.assertEqual(sys.getrefcount(tup), refs_before)

    eleza test_for_3(self):
        kundi I:
            eleza __aiter__(self):
                rudisha self

        aiter = I()
        refs_before = sys.getrefcount(aiter)

        async eleza foo():
            async for i in aiter:
                andika('never going to happen')

        with self.assertRaisesRegex(
                TypeError,
                r"that does not implement __anext__"):

            run_async(foo())

        self.assertEqual(sys.getrefcount(aiter), refs_before)

    eleza test_for_4(self):
        kundi I:
            eleza __aiter__(self):
                rudisha self

            eleza __anext__(self):
                rudisha ()

        aiter = I()
        refs_before = sys.getrefcount(aiter)

        async eleza foo():
            async for i in aiter:
                andika('never going to happen')

        with self.assertRaisesRegex(
                TypeError,
                "async for' received an invalid object.*__anext__.*tuple"):

            run_async(foo())

        self.assertEqual(sys.getrefcount(aiter), refs_before)

    eleza test_for_6(self):
        I = 0

        kundi Manager:
            async eleza __aenter__(self):
                nonlocal I
                I += 10000

            async eleza __aexit__(self, *args):
                nonlocal I
                I += 100000

        kundi Iterable:
            eleza __init__(self):
                self.i = 0

            eleza __aiter__(self):
                rudisha self

            async eleza __anext__(self):
                ikiwa self.i > 10:
                    raise StopAsyncIteration
                self.i += 1
                rudisha self.i

        ##############

        manager = Manager()
        iterable = Iterable()
        mrefs_before = sys.getrefcount(manager)
        irefs_before = sys.getrefcount(iterable)

        async eleza main():
            nonlocal I

            async with manager:
                async for i in iterable:
                    I += 1
            I += 1000

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            # Test that __aiter__ that returns an asynchronous iterator
            # directly does not throw any warnings.
            run_async(main())
        self.assertEqual(I, 111011)

        self.assertEqual(sys.getrefcount(manager), mrefs_before)
        self.assertEqual(sys.getrefcount(iterable), irefs_before)

        ##############

        async eleza main():
            nonlocal I

            async with Manager():
                async for i in Iterable():
                    I += 1
            I += 1000

            async with Manager():
                async for i in Iterable():
                    I += 1
            I += 1000

        run_async(main())
        self.assertEqual(I, 333033)

        ##############

        async eleza main():
            nonlocal I

            async with Manager():
                I += 100
                async for i in Iterable():
                    I += 1
                else:
                    I += 10000000
            I += 1000

            async with Manager():
                I += 100
                async for i in Iterable():
                    I += 1
                else:
                    I += 10000000
            I += 1000

        run_async(main())
        self.assertEqual(I, 20555255)

    eleza test_for_7(self):
        CNT = 0
        kundi AI:
            eleza __aiter__(self):
                1/0
        async eleza foo():
            nonlocal CNT
            async for i in AI():
                CNT += 1
            CNT += 10
        with self.assertRaises(ZeroDivisionError):
            run_async(foo())
        self.assertEqual(CNT, 0)

    eleza test_for_8(self):
        CNT = 0
        kundi AI:
            eleza __aiter__(self):
                1/0
        async eleza foo():
            nonlocal CNT
            async for i in AI():
                CNT += 1
            CNT += 10
        with self.assertRaises(ZeroDivisionError):
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                # Test that ikiwa __aiter__ raises an exception it propagates
                # without any kind of warning.
                run_async(foo())
        self.assertEqual(CNT, 0)

    eleza test_for_11(self):
        kundi F:
            eleza __aiter__(self):
                rudisha self
            eleza __anext__(self):
                rudisha self
            eleza __await__(self):
                1 / 0

        async eleza main():
            async for _ in F():
                pass

        with self.assertRaisesRegex(TypeError,
                                    'an invalid object kutoka __anext__') as c:
            main().send(None)

        err = c.exception
        self.assertIsInstance(err.__cause__, ZeroDivisionError)

    eleza test_for_tuple(self):
        kundi Done(Exception): pass

        kundi AIter(tuple):
            i = 0
            eleza __aiter__(self):
                rudisha self
            async eleza __anext__(self):
                ikiwa self.i >= len(self):
                    raise StopAsyncIteration
                self.i += 1
                rudisha self[self.i - 1]

        result = []
        async eleza foo():
            async for i in AIter([42]):
                result.append(i)
            raise Done

        with self.assertRaises(Done):
            foo().send(None)
        self.assertEqual(result, [42])

    eleza test_for_stop_iteration(self):
        kundi Done(Exception): pass

        kundi AIter(StopIteration):
            i = 0
            eleza __aiter__(self):
                rudisha self
            async eleza __anext__(self):
                ikiwa self.i:
                    raise StopAsyncIteration
                self.i += 1
                rudisha self.value

        result = []
        async eleza foo():
            async for i in AIter(42):
                result.append(i)
            raise Done

        with self.assertRaises(Done):
            foo().send(None)
        self.assertEqual(result, [42])

    eleza test_comp_1(self):
        async eleza f(i):
            rudisha i

        async eleza run_list():
            rudisha [await c for c in [f(1), f(41)]]

        async eleza run_set():
            rudisha {await c for c in [f(1), f(41)]}

        async eleza run_dict1():
            rudisha {await c: 'a' for c in [f(1), f(41)]}

        async eleza run_dict2():
            rudisha {i: await c for i, c in enumerate([f(1), f(41)])}

        self.assertEqual(run_async(run_list()), ([], [1, 41]))
        self.assertEqual(run_async(run_set()), ([], {1, 41}))
        self.assertEqual(run_async(run_dict1()), ([], {1: 'a', 41: 'a'}))
        self.assertEqual(run_async(run_dict2()), ([], {0: 1, 1: 41}))

    eleza test_comp_2(self):
        async eleza f(i):
            rudisha i

        async eleza run_list():
            rudisha [s for c in [f(''), f('abc'), f(''), f(['de', 'fg'])]
                    for s in await c]

        self.assertEqual(
            run_async(run_list()),
            ([], ['a', 'b', 'c', 'de', 'fg']))

        async eleza run_set():
            rudisha {d
                    for c in [f([f([10, 30]),
                                 f([20])])]
                    for s in await c
                    for d in await s}

        self.assertEqual(
            run_async(run_set()),
            ([], {10, 20, 30}))

        async eleza run_set2():
            rudisha {await s
                    for c in [f([f(10), f(20)])]
                    for s in await c}

        self.assertEqual(
            run_async(run_set2()),
            ([], {10, 20}))

    eleza test_comp_3(self):
        async eleza f(it):
            for i in it:
                yield i

        async eleza run_list():
            rudisha [i + 1 async for i in f([10, 20])]
        self.assertEqual(
            run_async(run_list()),
            ([], [11, 21]))

        async eleza run_set():
            rudisha {i + 1 async for i in f([10, 20])}
        self.assertEqual(
            run_async(run_set()),
            ([], {11, 21}))

        async eleza run_dict():
            rudisha {i + 1: i + 2 async for i in f([10, 20])}
        self.assertEqual(
            run_async(run_dict()),
            ([], {11: 12, 21: 22}))

        async eleza run_gen():
            gen = (i + 1 async for i in f([10, 20]))
            rudisha [g + 100 async for g in gen]
        self.assertEqual(
            run_async(run_gen()),
            ([], [111, 121]))

    eleza test_comp_4(self):
        async eleza f(it):
            for i in it:
                yield i

        async eleza run_list():
            rudisha [i + 1 async for i in f([10, 20]) ikiwa i > 10]
        self.assertEqual(
            run_async(run_list()),
            ([], [21]))

        async eleza run_set():
            rudisha {i + 1 async for i in f([10, 20]) ikiwa i > 10}
        self.assertEqual(
            run_async(run_set()),
            ([], {21}))

        async eleza run_dict():
            rudisha {i + 1: i + 2 async for i in f([10, 20]) ikiwa i > 10}
        self.assertEqual(
            run_async(run_dict()),
            ([], {21: 22}))

        async eleza run_gen():
            gen = (i + 1 async for i in f([10, 20]) ikiwa i > 10)
            rudisha [g + 100 async for g in gen]
        self.assertEqual(
            run_async(run_gen()),
            ([], [121]))

    eleza test_comp_4_2(self):
        async eleza f(it):
            for i in it:
                yield i

        async eleza run_list():
            rudisha [i + 10 async for i in f(range(5)) ikiwa 0 < i < 4]
        self.assertEqual(
            run_async(run_list()),
            ([], [11, 12, 13]))

        async eleza run_set():
            rudisha {i + 10 async for i in f(range(5)) ikiwa 0 < i < 4}
        self.assertEqual(
            run_async(run_set()),
            ([], {11, 12, 13}))

        async eleza run_dict():
            rudisha {i + 10: i + 100 async for i in f(range(5)) ikiwa 0 < i < 4}
        self.assertEqual(
            run_async(run_dict()),
            ([], {11: 101, 12: 102, 13: 103}))

        async eleza run_gen():
            gen = (i + 10 async for i in f(range(5)) ikiwa 0 < i < 4)
            rudisha [g + 100 async for g in gen]
        self.assertEqual(
            run_async(run_gen()),
            ([], [111, 112, 113]))

    eleza test_comp_5(self):
        async eleza f(it):
            for i in it:
                yield i

        async eleza run_list():
            rudisha [i + 1 for pair in ([10, 20], [30, 40]) ikiwa pair[0] > 10
                    async for i in f(pair) ikiwa i > 30]
        self.assertEqual(
            run_async(run_list()),
            ([], [41]))

    eleza test_comp_6(self):
        async eleza f(it):
            for i in it:
                yield i

        async eleza run_list():
            rudisha [i + 1 async for seq in f([(10, 20), (30,)])
                    for i in seq]

        self.assertEqual(
            run_async(run_list()),
            ([], [11, 21, 31]))

    eleza test_comp_7(self):
        async eleza f():
            yield 1
            yield 2
            raise Exception('aaa')

        async eleza run_list():
            rudisha [i async for i in f()]

        with self.assertRaisesRegex(Exception, 'aaa'):
            run_async(run_list())

    eleza test_comp_8(self):
        async eleza f():
            rudisha [i for i in [1, 2, 3]]

        self.assertEqual(
            run_async(f()),
            ([], [1, 2, 3]))

    eleza test_comp_9(self):
        async eleza gen():
            yield 1
            yield 2
        async eleza f():
            l = [i async for i in gen()]
            rudisha [i for i in l]

        self.assertEqual(
            run_async(f()),
            ([], [1, 2]))

    eleza test_comp_10(self):
        async eleza f():
            xx = {i for i in [1, 2, 3]}
            rudisha {x: x for x in xx}

        self.assertEqual(
            run_async(f()),
            ([], {1: 1, 2: 2, 3: 3}))

    eleza test_copy(self):
        async eleza func(): pass
        coro = func()
        with self.assertRaises(TypeError):
            copy.copy(coro)

        aw = coro.__await__()
        try:
            with self.assertRaises(TypeError):
                copy.copy(aw)
        finally:
            aw.close()

    eleza test_pickle(self):
        async eleza func(): pass
        coro = func()
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            with self.assertRaises((TypeError, pickle.PicklingError)):
                pickle.dumps(coro, proto)

        aw = coro.__await__()
        try:
            for proto in range(pickle.HIGHEST_PROTOCOL + 1):
                with self.assertRaises((TypeError, pickle.PicklingError)):
                    pickle.dumps(aw, proto)
        finally:
            aw.close()

    eleza test_fatal_coro_warning(self):
        # Issue 27811
        async eleza func(): pass
        with warnings.catch_warnings(), \
             support.catch_unraisable_exception() as cm:
            warnings.filterwarnings("error")
            coro = func()
            # only store repr() to avoid keeping the coroutine alive
            coro_repr = repr(coro)
            coro = None
            support.gc_collect()

            self.assertIn("was never awaited", str(cm.unraisable.exc_value))
            self.assertEqual(repr(cm.unraisable.object), coro_repr)

    eleza test_for_assign_raising_stop_async_iteration(self):
        kundi BadTarget:
            eleza __setitem__(self, key, value):
                raise StopAsyncIteration(42)
        tgt = BadTarget()
        async eleza source():
            yield 10

        async eleza run_for():
            with self.assertRaises(StopAsyncIteration) as cm:
                async for tgt[0] in source():
                    pass
            self.assertEqual(cm.exception.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_for()), ([], 'end'))

        async eleza run_list():
            with self.assertRaises(StopAsyncIteration) as cm:
                rudisha [0 async for tgt[0] in source()]
            self.assertEqual(cm.exception.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_list()), ([], 'end'))

        async eleza run_gen():
            gen = (0 async for tgt[0] in source())
            a = gen.asend(None)
            with self.assertRaises(RuntimeError) as cm:
                await a
            self.assertIsInstance(cm.exception.__cause__, StopAsyncIteration)
            self.assertEqual(cm.exception.__cause__.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_gen()), ([], 'end'))

    eleza test_for_assign_raising_stop_async_iteration_2(self):
        kundi BadIterable:
            eleza __iter__(self):
                raise StopAsyncIteration(42)
        async eleza badpairs():
            yield BadIterable()

        async eleza run_for():
            with self.assertRaises(StopAsyncIteration) as cm:
                async for i, j in badpairs():
                    pass
            self.assertEqual(cm.exception.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_for()), ([], 'end'))

        async eleza run_list():
            with self.assertRaises(StopAsyncIteration) as cm:
                rudisha [0 async for i, j in badpairs()]
            self.assertEqual(cm.exception.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_list()), ([], 'end'))

        async eleza run_gen():
            gen = (0 async for i, j in badpairs())
            a = gen.asend(None)
            with self.assertRaises(RuntimeError) as cm:
                await a
            self.assertIsInstance(cm.exception.__cause__, StopAsyncIteration)
            self.assertEqual(cm.exception.__cause__.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_gen()), ([], 'end'))


kundi CoroAsyncIOCompatTest(unittest.TestCase):

    eleza test_asyncio_1(self):
        # asyncio cannot be imported when Python is compiled without thread
        # support
        asyncio = support.import_module('asyncio')

        kundi MyException(Exception):
            pass

        buffer = []

        kundi CM:
            async eleza __aenter__(self):
                buffer.append(1)
                await asyncio.sleep(0.01)
                buffer.append(2)
                rudisha self

            async eleza __aexit__(self, exc_type, exc_val, exc_tb):
                await asyncio.sleep(0.01)
                buffer.append(exc_type.__name__)

        async eleza f():
            async with CM() as c:
                await asyncio.sleep(0.01)
                raise MyException
            buffer.append('unreachable')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(f())
        except MyException:
            pass
        finally:
            loop.close()
            asyncio.set_event_loop_policy(None)

        self.assertEqual(buffer, [1, 2, 'MyException'])


kundi OriginTrackingTest(unittest.TestCase):
    eleza here(self):
        info = inspect.getframeinfo(inspect.currentframe().f_back)
        rudisha (info.filename, info.lineno)

    eleza test_origin_tracking(self):
        orig_depth = sys.get_coroutine_origin_tracking_depth()
        try:
            async eleza corofn():
                pass

            sys.set_coroutine_origin_tracking_depth(0)
            self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 0)

            with contextlib.closing(corofn()) as coro:
                self.assertIsNone(coro.cr_origin)

            sys.set_coroutine_origin_tracking_depth(1)
            self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 1)

            fname, lineno = self.here()
            with contextlib.closing(corofn()) as coro:
                self.assertEqual(coro.cr_origin,
                                 ((fname, lineno + 1, "test_origin_tracking"),))

            sys.set_coroutine_origin_tracking_depth(2)
            self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 2)

            eleza nested():
                rudisha (self.here(), corofn())
            fname, lineno = self.here()
            ((nested_fname, nested_lineno), coro) = nested()
            with contextlib.closing(coro):
                self.assertEqual(coro.cr_origin,
                                 ((nested_fname, nested_lineno, "nested"),
                                  (fname, lineno + 1, "test_origin_tracking")))

            # Check we handle running out of frames correctly
            sys.set_coroutine_origin_tracking_depth(1000)
            with contextlib.closing(corofn()) as coro:
                self.assertTrue(2 < len(coro.cr_origin) < 1000)

            # We can't set depth negative
            with self.assertRaises(ValueError):
                sys.set_coroutine_origin_tracking_depth(-1)
            # And trying leaves it unchanged
            self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 1000)

        finally:
            sys.set_coroutine_origin_tracking_depth(orig_depth)

    eleza test_origin_tracking_warning(self):
        async eleza corofn():
            pass

        a1_filename, a1_lineno = self.here()
        eleza a1():
            rudisha corofn()  # comment in a1
        a1_lineno += 2

        a2_filename, a2_lineno = self.here()
        eleza a2():
            rudisha a1()  # comment in a2
        a2_lineno += 2

        eleza check(depth, msg):
            sys.set_coroutine_origin_tracking_depth(depth)
            with self.assertWarns(RuntimeWarning) as cm:
                a2()
                support.gc_collect()
            self.assertEqual(msg, str(cm.warning))

        orig_depth = sys.get_coroutine_origin_tracking_depth()
        try:
            msg = check(0, f"coroutine '{corofn.__qualname__}' was never awaited")
            check(1, "".join([
                f"coroutine '{corofn.__qualname__}' was never awaited\n",
                "Coroutine created at (most recent call last)\n",
                f'  File "{a1_filename}", line {a1_lineno}, in a1\n',
                f'    rudisha corofn()  # comment in a1',
            ]))
            check(2, "".join([
                f"coroutine '{corofn.__qualname__}' was never awaited\n",
                "Coroutine created at (most recent call last)\n",
                f'  File "{a2_filename}", line {a2_lineno}, in a2\n',
                f'    rudisha a1()  # comment in a2\n',
                f'  File "{a1_filename}", line {a1_lineno}, in a1\n',
                f'    rudisha corofn()  # comment in a1',
            ]))

        finally:
            sys.set_coroutine_origin_tracking_depth(orig_depth)

    eleza test_unawaited_warning_when_module_broken(self):
        # Make sure we don't blow up too bad if
        # warnings._warn_unawaited_coroutine is broken somehow (e.g. because
        # of shutdown problems)
        async eleza corofn():
            pass

        orig_wuc = warnings._warn_unawaited_coroutine
        try:
            warnings._warn_unawaited_coroutine = lambda coro: 1/0
            with support.catch_unraisable_exception() as cm, \
                 support.check_warnings((r'coroutine .* was never awaited',
                                         RuntimeWarning)):
                # only store repr() to avoid keeping the coroutine alive
                coro = corofn()
                coro_repr = repr(coro)

                # clear reference to the coroutine without awaiting for it
                del coro
                support.gc_collect()

                self.assertEqual(repr(cm.unraisable.object), coro_repr)
                self.assertEqual(cm.unraisable.exc_type, ZeroDivisionError)

            del warnings._warn_unawaited_coroutine
            with support.check_warnings((r'coroutine .* was never awaited',
                                         RuntimeWarning)):
                corofn()
                support.gc_collect()

        finally:
            warnings._warn_unawaited_coroutine = orig_wuc


kundi UnawaitedWarningDuringShutdownTest(unittest.TestCase):
    # https://bugs.python.org/issue32591#msg310726
    eleza test_unawaited_warning_during_shutdown(self):
        code = ("agiza asyncio\n"
                "async eleza f(): pass\n"
                "asyncio.gather(f())\n")
        assert_python_ok("-c", code)

        code = ("agiza sys\n"
                "async eleza f(): pass\n"
                "sys.coro = f()\n")
        assert_python_ok("-c", code)

        code = ("agiza sys\n"
                "async eleza f(): pass\n"
                "sys.corocycle = [f()]\n"
                "sys.corocycle.append(sys.corocycle)\n")
        assert_python_ok("-c", code)


@support.cpython_only
kundi CAPITest(unittest.TestCase):

    eleza test_tp_await_1(self):
        kutoka _testcapi agiza awaitType as at

        async eleza foo():
            future = at(iter([1]))
            rudisha (await future)

        self.assertEqual(foo().send(None), 1)

    eleza test_tp_await_2(self):
        # Test tp_await to __await__ mapping
        kutoka _testcapi agiza awaitType as at
        future = at(iter([1]))
        self.assertEqual(next(future.__await__()), 1)

    eleza test_tp_await_3(self):
        kutoka _testcapi agiza awaitType as at

        async eleza foo():
            future = at(1)
            rudisha (await future)

        with self.assertRaisesRegex(
                TypeError, "__await__.*returned non-iterator of type 'int'"):
            self.assertEqual(foo().send(None), 1)


ikiwa __name__=="__main__":
    unittest.main()
