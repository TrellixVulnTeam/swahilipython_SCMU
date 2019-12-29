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
        tuma kutoka self.obj


kundi AsyncYield:
    eleza __init__(self, value):
        self.value = value

    eleza __await__(self):
        tuma self.value


eleza run_async(coro):
    assert coro.__class__ kwenye {types.GeneratorType, types.CoroutineType}

    buffer = []
    result = Tupu
    wakati Kweli:
        jaribu:
            buffer.append(coro.send(Tupu))
        tatizo StopIteration kama ex:
            result = ex.args[0] ikiwa ex.args isipokua Tupu
            koma
    rudisha buffer, result


eleza run_async__await__(coro):
    assert coro.__class__ ni types.CoroutineType
    aw = coro.__await__()
    buffer = []
    result = Tupu
    i = 0
    wakati Kweli:
        jaribu:
            ikiwa i % 2:
                buffer.append(next(aw))
            isipokua:
                buffer.append(aw.send(Tupu))
            i += 1
        tatizo StopIteration kama ex:
            result = ex.args[0] ikiwa ex.args isipokua Tupu
            koma
    rudisha buffer, result


@contextlib.contextmanager
eleza silence_coro_gc():
    ukijumuisha warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tuma
        support.gc_collect()


kundi AsyncBadSyntaxTest(unittest.TestCase):

    eleza test_badsyntax_1(self):
        samples = [
            """eleza foo():
                await something()
            """,

            """await something()""",

            """async eleza foo():
                tuma kutoka []
            """,

            """async eleza foo():
                await await fut
            """,

            """async eleza foo(a=await something()):
                pita
            """,

            """async eleza foo(a:await something()):
                pita
            """,

            """async eleza foo():
                eleza bar():
                 [i async kila i kwenye els]
            """,

            """async eleza foo():
                eleza bar():
                 [await i kila i kwenye els]
            """,

            """async eleza foo():
                eleza bar():
                 [i kila i kwenye els
                    async kila b kwenye els]
            """,

            """async eleza foo():
                eleza bar():
                 [i kila i kwenye els
                    kila c kwenye b
                    async kila b kwenye els]
            """,

            """async eleza foo():
                eleza bar():
                 [i kila i kwenye els
                    async kila b kwenye els
                    kila c kwenye b]
            """,

            """async eleza foo():
                eleza bar():
                 [i kila i kwenye els
                    kila b kwenye await els]
            """,

            """async eleza foo():
                eleza bar():
                 [i kila i kwenye els
                    kila b kwenye els
                        ikiwa await b]
            """,

            """async eleza foo():
                eleza bar():
                 [i kila i kwenye await els]
            """,

            """async eleza foo():
                eleza bar():
                 [i kila i kwenye els ikiwa await i]
            """,

            """eleza bar():
                 [i async kila i kwenye els]
            """,

            """eleza bar():
                 {i: i async kila i kwenye els}
            """,

            """eleza bar():
                 {i async kila i kwenye els}
            """,

            """eleza bar():
                 [await i kila i kwenye els]
            """,

            """eleza bar():
                 [i kila i kwenye els
                    async kila b kwenye els]
            """,

            """eleza bar():
                 [i kila i kwenye els
                    kila c kwenye b
                    async kila b kwenye els]
            """,

            """eleza bar():
                 [i kila i kwenye els
                    async kila b kwenye els
                    kila c kwenye b]
            """,

            """eleza bar():
                 [i kila i kwenye els
                    kila b kwenye await els]
            """,

            """eleza bar():
                 [i kila i kwenye els
                    kila b kwenye els
                        ikiwa await b]
            """,

            """eleza bar():
                 [i kila i kwenye await els]
            """,

            """eleza bar():
                 [i kila i kwenye els ikiwa await i]
            """,

            """async eleza foo():
                await
            """,

            """async eleza foo():
                   eleza bar(): pita
                   await = 1
            """,

            """async eleza foo():

                   eleza bar(): pita
                   await = 1
            """,

            """async eleza foo():
                   eleza bar(): pita
                   ikiwa 1:
                       await = 1
            """,

            """eleza foo():
                   async eleza bar(): pita
                   ikiwa 1:
                       await a
            """,

            """eleza foo():
                   async eleza bar(): pita
                   await a
            """,

            """eleza foo():
                   eleza baz(): pita
                   async eleza bar(): pita
                   await a
            """,

            """eleza foo():
                   eleza baz(): pita
                   # 456
                   async eleza bar(): pita
                   # 123
                   await a
            """,

            """async eleza foo():
                   eleza baz(): pita
                   # 456
                   async eleza bar(): pita
                   # 123
                   await = 2
            """,

            """eleza foo():

                   eleza baz(): pita

                   async eleza bar(): pita

                   await a
            """,

            """async eleza foo():

                   eleza baz(): pita

                   async eleza bar(): pita

                   await = 2
            """,

            """async eleza foo():
                   eleza async(): pita
            """,

            """async eleza foo():
                   eleza await(): pita
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
                   pita
            """,

            """async eleza foo(a:await b):
                   pita
            """,

            """eleza baz():
                   async eleza foo(a=await b):
                       pita
            """,

            """async eleza foo(async):
                   pita
            """,

            """async eleza foo():
                   eleza bar():
                        eleza baz():
                            async = 1
            """,

            """async eleza foo():
                   eleza bar():
                        eleza baz():
                            pita
                        async = 1
            """,

            """eleza foo():
                   async eleza bar():

                        async eleza baz():
                            pita

                        eleza baz():
                            42

                        async = 1
            """,

            """async eleza foo():
                   eleza bar():
                        eleza baz():
                            pita\nawait foo()
            """,

            """eleza foo():
                   eleza bar():
                        async eleza baz():
                            pita\nawait foo()
            """,

            """async eleza foo(await):
                   pita
            """,

            """eleza foo():

                   async eleza bar(): pita

                   await a
            """,

            """eleza foo():
                   async eleza bar():
                        pita\nawait a
            """,
            """eleza foo():
                   async kila i kwenye arange(2):
                       pita
            """,
            """eleza foo():
                   async ukijumuisha resource:
                       pita
            """,
            """async ukijumuisha resource:
                   pita
            """,
            """async kila i kwenye arange(2):
                   pita
            """,
            ]

        kila code kwenye samples:
            ukijumuisha self.subTest(code=code), self.assertRaises(SyntaxError):
                compile(code, "<test>", "exec")

    eleza test_badsyntax_2(self):
        samples = [
            """eleza foo():
                await = 1
            """,

            """kundi Bar:
                eleza async(): pita
            """,

            """kundi Bar:
                async = 1
            """,

            """kundi async:
                pita
            """,

            """kundi await:
                pita
            """,

            """agiza math kama await""",

            """eleza async():
                pita""",

            """eleza foo(*, await=1):
                pita"""

            """async = 1""",

            """andika(await=1)"""
        ]

        kila code kwenye samples:
            ukijumuisha self.subTest(code=code), self.assertRaises(SyntaxError):
                compile(code, "<test>", "exec")

    eleza test_badsyntax_3(self):
        ukijumuisha self.assertRaises(SyntaxError):
            compile("async = 1", "<test>", "exec")

    eleza test_badsyntax_4(self):
        samples = [
            '''eleza foo(await):
                async eleza foo(): pita
                async eleza foo():
                    pita
                rudisha await + 1
            ''',

            '''eleza foo(await):
                async eleza foo(): pita
                async eleza foo(): pita
                rudisha await + 1
            ''',

            '''eleza foo(await):

                async eleza foo(): pita

                async eleza foo(): pita

                rudisha await + 1
            ''',

            '''eleza foo(await):
                """spam"""
                async eleza foo(): \
                    pita
                # 123
                async eleza foo(): pita
                # 456
                rudisha await + 1
            ''',

            '''eleza foo(await):
                eleza foo(): pita
                eleza foo(): pita
                async eleza bar(): rudisha await_
                await_ = await
                jaribu:
                    bar().send(Tupu)
                tatizo StopIteration kama ex:
                    rudisha ex.args[0] + 1
            '''
        ]

        kila code kwenye samples:
            ukijumuisha self.subTest(code=code), self.assertRaises(SyntaxError):
                compile(code, "<test>", "exec")


kundi TokenizerRegrTest(unittest.TestCase):

    eleza test_oneline_defs(self):
        buf = []
        kila i kwenye range(500):
            buf.append('eleza i{i}(): rudisha {i}'.format(i=i))
        buf = '\n'.join(buf)

        # Test that 500 consequent, one-line defs ni OK
        ns = {}
        exec(buf, ns, ns)
        self.assertEqual(ns['i499'](), 499)

        # Test that 500 consequent, one-line defs *and*
        # one 'async def' following them ni OK
        buf += '\nasync eleza foo():\n    rudisha'
        ns = {}
        exec(buf, ns, ns)
        self.assertEqual(ns['i499'](), 499)
        self.assertKweli(inspect.iscoroutinefunction(ns['foo']))


kundi CoroutineTest(unittest.TestCase):

    eleza test_gen_1(self):
        eleza gen(): tuma
        self.assertUongo(hasattr(gen, '__await__'))

    eleza test_func_1(self):
        async eleza foo():
            rudisha 10

        f = foo()
        self.assertIsInstance(f, types.CoroutineType)
        self.assertKweli(bool(foo.__code__.co_flags & inspect.CO_COROUTINE))
        self.assertUongo(bool(foo.__code__.co_flags & inspect.CO_GENERATOR))
        self.assertKweli(bool(f.cr_code.co_flags & inspect.CO_COROUTINE))
        self.assertUongo(bool(f.cr_code.co_flags & inspect.CO_GENERATOR))
        self.assertEqual(run_async(f), ([], 10))

        self.assertEqual(run_async__await__(foo()), ([], 10))

        eleza bar(): pita
        self.assertUongo(bool(bar.__code__.co_flags & inspect.CO_COROUTINE))

    eleza test_func_2(self):
        async eleza foo():
            ashiria StopIteration

        ukijumuisha self.assertRaisesRegex(
                RuntimeError, "coroutine ashiriad StopIteration"):

            run_async(foo())

    eleza test_func_3(self):
        async eleza foo():
            ashiria StopIteration

        coro = foo()
        self.assertRegex(repr(coro), '^<coroutine object.* at 0x.*>$')
        coro.close()

    eleza test_func_4(self):
        async eleza foo():
            ashiria StopIteration
        coro = foo()

        check = lambda: self.assertRaisesRegex(
            TypeError, "'coroutine' object ni sio iterable")

        ukijumuisha check():
            list(coro)

        ukijumuisha check():
            tuple(coro)

        ukijumuisha check():
            sum(coro)

        ukijumuisha check():
            iter(coro)

        ukijumuisha check():
            kila i kwenye coro:
                pita

        ukijumuisha check():
            [i kila i kwenye coro]

        coro.close()

    eleza test_func_5(self):
        @types.coroutine
        eleza bar():
            tuma 1

        async eleza foo():
            await bar()

        check = lambda: self.assertRaisesRegex(
            TypeError, "'coroutine' object ni sio iterable")

        coro = foo()
        ukijumuisha check():
            kila el kwenye coro:
                pita
        coro.close()

        # the following should pita without an error
        kila el kwenye bar():
            self.assertEqual(el, 1)
        self.assertEqual([el kila el kwenye bar()], [1])
        self.assertEqual(tuple(bar()), (1,))
        self.assertEqual(next(iter(bar())), 1)

    eleza test_func_6(self):
        @types.coroutine
        eleza bar():
            tuma 1
            tuma 2

        async eleza foo():
            await bar()

        f = foo()
        self.assertEqual(f.send(Tupu), 1)
        self.assertEqual(f.send(Tupu), 2)
        ukijumuisha self.assertRaises(StopIteration):
            f.send(Tupu)

    eleza test_func_7(self):
        async eleza bar():
            rudisha 10
        coro = bar()

        eleza foo():
            tuma kutoka coro

        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "cannot 'tuma kutoka' a coroutine object kwenye "
                "a non-coroutine generator"):
            list(foo())

        coro.close()

    eleza test_func_8(self):
        @types.coroutine
        eleza bar():
            rudisha (tuma kutoka coro)

        async eleza foo():
            rudisha 'spam'

        coro = foo()
        self.assertEqual(run_async(bar()), ([], 'spam'))
        coro.close()

    eleza test_func_9(self):
        async eleza foo():
            pita

        ukijumuisha self.assertWarnsRegex(
                RuntimeWarning,
                r"coroutine '.*test_func_9.*foo' was never awaited"):

            foo()
            support.gc_collect()

        ukijumuisha self.assertWarnsRegex(
                RuntimeWarning,
                r"coroutine '.*test_func_9.*foo' was never awaited"):

            ukijumuisha self.assertRaises(TypeError):
                # See bpo-32703.
                kila _ kwenye foo():
                    pita

            support.gc_collect()

    eleza test_func_10(self):
        N = 0

        @types.coroutine
        eleza gen():
            nonlocal N
            jaribu:
                a = tuma
                tuma (a ** 2)
            tatizo ZeroDivisionError:
                N += 100
                ashiria
            mwishowe:
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
        ukijumuisha self.assertRaises(ZeroDivisionError):
            aw.throw(ZeroDivisionError, Tupu, Tupu)
        self.assertEqual(N, 102)

    eleza test_func_11(self):
        async eleza func(): pita
        coro = func()
        # Test that PyCoro_Type na _PyCoroWrapper_Type types were properly
        # initialized
        self.assertIn('__await__', dir(coro))
        self.assertIn('__iter__', dir(coro.__await__()))
        self.assertIn('coroutine_wrapper', repr(coro.__await__()))
        coro.close() # avoid RuntimeWarning

    eleza test_func_12(self):
        async eleza g():
            i = me.send(Tupu)
            await foo
        me = g()
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    "coroutine already executing"):
            me.send(Tupu)

    eleza test_func_13(self):
        async eleza g():
            pita

        coro = g()
        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "can't send non-Tupu value to a just-started coroutine"):
            coro.send('spam')

        coro.close()

    eleza test_func_14(self):
        @types.coroutine
        eleza gen():
            tuma
        async eleza coro():
            jaribu:
                await gen()
            tatizo GeneratorExit:
                await gen()
        c = coro()
        c.send(Tupu)
        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    "coroutine ignored GeneratorExit"):
            c.close()

    eleza test_func_15(self):
        # See http://bugs.python.org/issue25887 kila details

        async eleza spammer():
            rudisha 'spam'
        async eleza reader(coro):
            rudisha await coro

        spammer_coro = spammer()

        ukijumuisha self.assertRaisesRegex(StopIteration, 'spam'):
            reader(spammer_coro).send(Tupu)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            reader(spammer_coro).send(Tupu)

    eleza test_func_16(self):
        # See http://bugs.python.org/issue25887 kila details

        @types.coroutine
        eleza nop():
            tuma
        async eleza send():
            await nop()
            rudisha 'spam'
        async eleza read(coro):
            await nop()
            rudisha await coro

        spammer = send()

        reader = read(spammer)
        reader.send(Tupu)
        reader.send(Tupu)
        ukijumuisha self.assertRaisesRegex(Exception, 'ham'):
            reader.throw(Exception('ham'))

        reader = read(spammer)
        reader.send(Tupu)
        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            reader.send(Tupu)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            reader.throw(Exception('wat'))

    eleza test_func_17(self):
        # See http://bugs.python.org/issue25887 kila details

        async eleza coroutine():
            rudisha 'spam'

        coro = coroutine()
        ukijumuisha self.assertRaisesRegex(StopIteration, 'spam'):
            coro.send(Tupu)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            coro.send(Tupu)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            coro.throw(Exception('wat'))

        # Closing a coroutine shouldn't ashiria any exception even ikiwa it's
        # already closed/exhausted (similar to generators)
        coro.close()
        coro.close()

    eleza test_func_18(self):
        # See http://bugs.python.org/issue25887 kila details

        async eleza coroutine():
            rudisha 'spam'

        coro = coroutine()
        await_iter = coro.__await__()
        it = iter(await_iter)

        ukijumuisha self.assertRaisesRegex(StopIteration, 'spam'):
            it.send(Tupu)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            it.send(Tupu)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            # Although the iterator protocol requires iterators to
            # ashiria another StopIteration here, we don't want to do
            # that.  In this particular case, the iterator will ashiria
            # a RuntimeError, so that 'tuma kutoka' na 'await'
            # expressions will trigger the error, instead of silently
            # ignoring the call.
            next(it)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            it.throw(Exception('wat'))

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'cannot reuse already awaited coroutine'):
            it.throw(Exception('wat'))

        # Closing a coroutine shouldn't ashiria any exception even ikiwa it's
        # already closed/exhausted (similar to generators)
        it.close()
        it.close()

    eleza test_func_19(self):
        CHK = 0

        @types.coroutine
        eleza foo():
            nonlocal CHK
            tuma
            jaribu:
                tuma
            tatizo GeneratorExit:
                CHK += 1

        async eleza coroutine():
            await foo()

        coro = coroutine()

        coro.send(Tupu)
        coro.send(Tupu)

        self.assertEqual(CHK, 0)
        coro.close()
        self.assertEqual(CHK, 1)

        kila _ kwenye range(3):
            # Closing a coroutine shouldn't ashiria any exception even ikiwa it's
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
            self.assertIsTupu(coro_b.cr_await)
            tuma
            self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_RUNNING)
            self.assertIsTupu(coro_b.cr_await)

        async eleza c():
            await a()

        async eleza b():
            self.assertIsTupu(coro_b.cr_await)
            await c()
            self.assertIsTupu(coro_b.cr_await)

        coro_b = b()
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_CREATED)
        self.assertIsTupu(coro_b.cr_await)

        coro_b.send(Tupu)
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_SUSPENDED)
        self.assertEqual(coro_b.cr_await.cr_await.gi_code.co_name, 'a')

        ukijumuisha self.assertRaises(StopIteration):
            coro_b.send(Tupu)  # complete coroutine
        self.assertEqual(inspect.getcoroutinestate(coro_b), inspect.CORO_CLOSED)
        self.assertIsTupu(coro_b.cr_await)

    eleza test_corotype_1(self):
        ct = types.CoroutineType
        self.assertIn('into coroutine', ct.send.__doc__)
        self.assertIn('inside coroutine', ct.close.__doc__)
        self.assertIn('in coroutine', ct.throw.__doc__)
        self.assertIn('of the coroutine', ct.__dict__['__name__'].__doc__)
        self.assertIn('of the coroutine', ct.__dict__['__qualname__'].__doc__)
        self.assertEqual(ct.__name__, 'coroutine')

        async eleza f(): pita
        c = f()
        self.assertIn('coroutine object', repr(c))
        c.close()

    eleza test_await_1(self):

        async eleza foo():
            await 1
        ukijumuisha self.assertRaisesRegex(TypeError, "object int can.t.*await"):
            run_async(foo())

    eleza test_await_2(self):
        async eleza foo():
            await []
        ukijumuisha self.assertRaisesRegex(TypeError, "object list can.t.*await"):
            run_async(foo())

    eleza test_await_3(self):
        async eleza foo():
            await AsyncYieldFrom([1, 2, 3])

        self.assertEqual(run_async(foo()), ([1, 2, 3], Tupu))
        self.assertEqual(run_async__await__(foo()), ([1, 2, 3], Tupu))

    eleza test_await_4(self):
        async eleza bar():
            rudisha 42

        async eleza foo():
            rudisha await bar()

        self.assertEqual(run_async(foo()), ([], 42))

    eleza test_await_5(self):
        kundi Awaitable:
            eleza __await__(self):
                rudisha

        async eleza foo():
            rudisha (await Awaitable())

        ukijumuisha self.assertRaisesRegex(
            TypeError, "__await__.*rudishaed non-iterator of type"):

            run_async(foo())

    eleza test_await_6(self):
        kundi Awaitable:
            eleza __await__(self):
                rudisha iter([52])

        async eleza foo():
            rudisha (await Awaitable())

        self.assertEqual(run_async(foo()), ([52], Tupu))

    eleza test_await_7(self):
        kundi Awaitable:
            eleza __await__(self):
                tuma 42
                rudisha 100

        async eleza foo():
            rudisha (await Awaitable())

        self.assertEqual(run_async(foo()), ([42], 100))

    eleza test_await_8(self):
        kundi Awaitable:
            pita

        async eleza foo(): rudisha await Awaitable()

        ukijumuisha self.assertRaisesRegex(
            TypeError, "object Awaitable can't be used kwenye 'await' expression"):

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

        ukijumuisha self.assertRaisesRegex(
                TypeError, r"__await__\(\) rudishaed a coroutine"):
            run_async(foo())

        c.close()

    eleza test_await_13(self):
        kundi Awaitable:
            eleza __await__(self):
                rudisha self

        async eleza foo():
            rudisha await Awaitable()

        ukijumuisha self.assertRaisesRegex(
            TypeError, "__await__.*rudishaed non-iterator of type"):

            run_async(foo())

    eleza test_await_14(self):
        kundi Wrapper:
            # Forces the interpreter to use CoroutineType.__await__
            eleza __init__(self, coro):
                assert coro.__class__ ni types.CoroutineType
                self.coro = coro
            eleza __await__(self):
                rudisha self.coro.__await__()

        kundi FutureLike:
            eleza __await__(self):
                rudisha (tuma)

        kundi Marker(Exception):
            pita

        async eleza coro1():
            jaribu:
                rudisha await FutureLike()
            tatizo ZeroDivisionError:
                ashiria Marker
        async eleza coro2():
            rudisha await Wrapper(coro1())

        c = coro2()
        c.send(Tupu)
        ukijumuisha self.assertRaisesRegex(StopIteration, 'spam'):
            c.send('spam')

        c = coro2()
        c.send(Tupu)
        ukijumuisha self.assertRaises(Marker):
            c.throw(ZeroDivisionError)

    eleza test_await_15(self):
        @types.coroutine
        eleza nop():
            tuma

        async eleza coroutine():
            await nop()

        async eleza waiter(coro):
            await coro

        coro = coroutine()
        coro.send(Tupu)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    "coroutine ni being awaited already"):
            waiter(coro).send(Tupu)

    eleza test_await_16(self):
        # See https://bugs.python.org/issue29600 kila details.

        async eleza f():
            rudisha ValueError()

        async eleza g():
            jaribu:
                ashiria KeyError
            except:
                rudisha await f()

        _, result = run_async(g())
        self.assertIsTupu(result.__context__)

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
                    rudisha Kweli


        async eleza foo():
            async ukijumuisha Manager("A") kama a, Manager("B") kama b:
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
            async ukijumuisha Manager("A") kama a, Manager("C") kama c:
                await AsyncYieldFrom([('managers', a.name, c.name)])
                1/0

        ukijumuisha self.assertRaises(ZeroDivisionError):
            run_async(foo())

    eleza test_with_2(self):
        kundi CM:
            eleza __aenter__(self):
                pita

        async eleza foo():
            async ukijumuisha CM():
                pita

        ukijumuisha self.assertRaisesRegex(AttributeError, '__aexit__'):
            run_async(foo())

    eleza test_with_3(self):
        kundi CM:
            eleza __aexit__(self):
                pita

        async eleza foo():
            async ukijumuisha CM():
                pita

        ukijumuisha self.assertRaisesRegex(AttributeError, '__aenter__'):
            run_async(foo())

    eleza test_with_4(self):
        kundi CM:
            eleza __enter__(self):
                pita

            eleza __exit__(self):
                pita

        async eleza foo():
            async ukijumuisha CM():
                pita

        ukijumuisha self.assertRaisesRegex(AttributeError, '__aexit__'):
            run_async(foo())

    eleza test_with_5(self):
        # While this test doesn't make a lot of sense,
        # it's a regression test kila an early bug ukijumuisha opcodes
        # generation

        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            async eleza __aexit__(self, *exc):
                pita

        async eleza func():
            async ukijumuisha CM():
                assert (1, ) == 1

        ukijumuisha self.assertRaises(AssertionError):
            run_async(func())

    eleza test_with_6(self):
        kundi CM:
            eleza __aenter__(self):
                rudisha 123

            eleza __aexit__(self, *e):
                rudisha 456

        async eleza foo():
            async ukijumuisha CM():
                pita

        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aenter__ "
                "that does sio implement __await__: int"):
            # it's agizaant that __aexit__ wasn't called
            run_async(foo())

    eleza test_with_7(self):
        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            eleza __aexit__(self, *e):
                rudisha 444

        # Exit ukijumuisha exception
        async eleza foo():
            async ukijumuisha CM():
                1/0

        jaribu:
            run_async(foo())
        tatizo TypeError kama exc:
            self.assertRegex(
                exc.args[0],
                "'async with' received an object kutoka __aexit__ "
                "that does sio implement __await__: int")
            self.assertKweli(exc.__context__ ni sio Tupu)
            self.assertKweli(isinstance(exc.__context__, ZeroDivisionError))
        isipokua:
            self.fail('invalid asynchronous context manager did sio fail')


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
            async ukijumuisha CM():
                CNT += 1
        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aexit__ "
                "that does sio implement __await__: int"):
            run_async(foo())
        self.assertEqual(CNT, 1)

        # Exit ukijumuisha 'koma'
        async eleza foo():
            nonlocal CNT
            kila i kwenye range(2):
                async ukijumuisha CM():
                    CNT += 1
                    koma
        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aexit__ "
                "that does sio implement __await__: int"):
            run_async(foo())
        self.assertEqual(CNT, 2)

        # Exit ukijumuisha 'endelea'
        async eleza foo():
            nonlocal CNT
            kila i kwenye range(2):
                async ukijumuisha CM():
                    CNT += 1
                    endelea
        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aexit__ "
                "that does sio implement __await__: int"):
            run_async(foo())
        self.assertEqual(CNT, 3)

        # Exit ukijumuisha 'rudisha'
        async eleza foo():
            nonlocal CNT
            async ukijumuisha CM():
                CNT += 1
                rudisha
        ukijumuisha self.assertRaisesRegex(
                TypeError,
                "'async with' received an object kutoka __aexit__ "
                "that does sio implement __await__: int"):
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
            async ukijumuisha CM():
                CNT += 1

        ukijumuisha self.assertRaises(ZeroDivisionError):
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
            async ukijumuisha CM():
                async ukijumuisha CM():
                    ashiria RuntimeError

        jaribu:
            run_async(foo())
        tatizo ZeroDivisionError kama exc:
            self.assertKweli(exc.__context__ ni sio Tupu)
            self.assertKweli(isinstance(exc.__context__, ZeroDivisionError))
            self.assertKweli(isinstance(exc.__context__.__context__,
                                       RuntimeError))
        isipokua:
            self.fail('exception kutoka __aexit__ did sio propagate')

    eleza test_with_11(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                ashiria NotImplementedError

            async eleza __aexit__(self, *e):
                1/0

        async eleza foo():
            nonlocal CNT
            async ukijumuisha CM():
                ashiria RuntimeError

        jaribu:
            run_async(foo())
        tatizo NotImplementedError kama exc:
            self.assertKweli(exc.__context__ ni Tupu)
        isipokua:
            self.fail('exception kutoka __aenter__ did sio propagate')

    eleza test_with_12(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                rudisha self

            async eleza __aexit__(self, *e):
                rudisha Kweli

        async eleza foo():
            nonlocal CNT
            async ukijumuisha CM() kama cm:
                self.assertIs(cm.__class__, CM)
                ashiria RuntimeError

        run_async(foo())

    eleza test_with_13(self):
        CNT = 0

        kundi CM:
            async eleza __aenter__(self):
                1/0

            async eleza __aexit__(self, *e):
                rudisha Kweli

        async eleza foo():
            nonlocal CNT
            CNT += 1
            async ukijumuisha CM():
                CNT += 1000
            CNT += 10000

        ukijumuisha self.assertRaises(ZeroDivisionError):
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

                ikiwa sio (self.i % 10):
                    await AsyncYield(self.i * 10)

                ikiwa self.i > 100:
                    ashiria StopAsyncIteration

                rudisha self.i, self.i


        buffer = []
        async eleza test1():
            async kila i1, i2 kwenye AsyncIter():
                buffer.append(i1 + i2)

        tumaed, _ = run_async(test1())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 1)
        self.assertEqual(tumaed, [i * 100 kila i kwenye range(1, 11)])
        self.assertEqual(buffer, [i*2 kila i kwenye range(1, 101)])


        buffer = []
        async eleza test2():
            nonlocal buffer
            async kila i kwenye AsyncIter():
                buffer.append(i[0])
                ikiwa i[0] == 20:
                    koma
            isipokua:
                buffer.append('what?')
            buffer.append('end')

        tumaed, _ = run_async(test2())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 2)
        self.assertEqual(tumaed, [100, 200])
        self.assertEqual(buffer, [i kila i kwenye range(1, 21)] + ['end'])


        buffer = []
        async eleza test3():
            nonlocal buffer
            async kila i kwenye AsyncIter():
                ikiwa i[0] > 20:
                    endelea
                buffer.append(i[0])
            isipokua:
                buffer.append('what?')
            buffer.append('end')

        tumaed, _ = run_async(test3())
        # Make sure that __aiter__ was called only once
        self.assertEqual(aiter_calls, 3)
        self.assertEqual(tumaed, [i * 100 kila i kwenye range(1, 11)])
        self.assertEqual(buffer, [i kila i kwenye range(1, 21)] +
                                 ['what?', 'end'])

    eleza test_for_2(self):
        tup = (1, 2, 3)
        refs_before = sys.getrefcount(tup)

        async eleza foo():
            async kila i kwenye tup:
                andika('never going to happen')

        ukijumuisha self.assertRaisesRegex(
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
            async kila i kwenye aiter:
                andika('never going to happen')

        ukijumuisha self.assertRaisesRegex(
                TypeError,
                r"that does sio implement __anext__"):

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
            async kila i kwenye aiter:
                andika('never going to happen')

        ukijumuisha self.assertRaisesRegex(
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
                    ashiria StopAsyncIteration
                self.i += 1
                rudisha self.i

        ##############

        manager = Manager()
        iterable = Iterable()
        mrefs_before = sys.getrefcount(manager)
        irefs_before = sys.getrefcount(iterable)

        async eleza main():
            nonlocal I

            async ukijumuisha manager:
                async kila i kwenye iterable:
                    I += 1
            I += 1000

        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter("error")
            # Test that __aiter__ that rudishas an asynchronous iterator
            # directly does sio throw any warnings.
            run_async(main())
        self.assertEqual(I, 111011)

        self.assertEqual(sys.getrefcount(manager), mrefs_before)
        self.assertEqual(sys.getrefcount(iterable), irefs_before)

        ##############

        async eleza main():
            nonlocal I

            async ukijumuisha Manager():
                async kila i kwenye Iterable():
                    I += 1
            I += 1000

            async ukijumuisha Manager():
                async kila i kwenye Iterable():
                    I += 1
            I += 1000

        run_async(main())
        self.assertEqual(I, 333033)

        ##############

        async eleza main():
            nonlocal I

            async ukijumuisha Manager():
                I += 100
                async kila i kwenye Iterable():
                    I += 1
                isipokua:
                    I += 10000000
            I += 1000

            async ukijumuisha Manager():
                I += 100
                async kila i kwenye Iterable():
                    I += 1
                isipokua:
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
            async kila i kwenye AI():
                CNT += 1
            CNT += 10
        ukijumuisha self.assertRaises(ZeroDivisionError):
            run_async(foo())
        self.assertEqual(CNT, 0)

    eleza test_for_8(self):
        CNT = 0
        kundi AI:
            eleza __aiter__(self):
                1/0
        async eleza foo():
            nonlocal CNT
            async kila i kwenye AI():
                CNT += 1
            CNT += 10
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter("error")
                # Test that ikiwa __aiter__ ashirias an exception it propagates
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
            async kila _ kwenye F():
                pita

        ukijumuisha self.assertRaisesRegex(TypeError,
                                    'an invalid object kutoka __anext__') kama c:
            main().send(Tupu)

        err = c.exception
        self.assertIsInstance(err.__cause__, ZeroDivisionError)

    eleza test_for_tuple(self):
        kundi Done(Exception): pita

        kundi AIter(tuple):
            i = 0
            eleza __aiter__(self):
                rudisha self
            async eleza __anext__(self):
                ikiwa self.i >= len(self):
                    ashiria StopAsyncIteration
                self.i += 1
                rudisha self[self.i - 1]

        result = []
        async eleza foo():
            async kila i kwenye AIter([42]):
                result.append(i)
            ashiria Done

        ukijumuisha self.assertRaises(Done):
            foo().send(Tupu)
        self.assertEqual(result, [42])

    eleza test_for_stop_iteration(self):
        kundi Done(Exception): pita

        kundi AIter(StopIteration):
            i = 0
            eleza __aiter__(self):
                rudisha self
            async eleza __anext__(self):
                ikiwa self.i:
                    ashiria StopAsyncIteration
                self.i += 1
                rudisha self.value

        result = []
        async eleza foo():
            async kila i kwenye AIter(42):
                result.append(i)
            ashiria Done

        ukijumuisha self.assertRaises(Done):
            foo().send(Tupu)
        self.assertEqual(result, [42])

    eleza test_comp_1(self):
        async eleza f(i):
            rudisha i

        async eleza run_list():
            rudisha [await c kila c kwenye [f(1), f(41)]]

        async eleza run_set():
            rudisha {await c kila c kwenye [f(1), f(41)]}

        async eleza run_dict1():
            rudisha {await c: 'a' kila c kwenye [f(1), f(41)]}

        async eleza run_dict2():
            rudisha {i: await c kila i, c kwenye enumerate([f(1), f(41)])}

        self.assertEqual(run_async(run_list()), ([], [1, 41]))
        self.assertEqual(run_async(run_set()), ([], {1, 41}))
        self.assertEqual(run_async(run_dict1()), ([], {1: 'a', 41: 'a'}))
        self.assertEqual(run_async(run_dict2()), ([], {0: 1, 1: 41}))

    eleza test_comp_2(self):
        async eleza f(i):
            rudisha i

        async eleza run_list():
            rudisha [s kila c kwenye [f(''), f('abc'), f(''), f(['de', 'fg'])]
                    kila s kwenye await c]

        self.assertEqual(
            run_async(run_list()),
            ([], ['a', 'b', 'c', 'de', 'fg']))

        async eleza run_set():
            rudisha {d
                    kila c kwenye [f([f([10, 30]),
                                 f([20])])]
                    kila s kwenye await c
                    kila d kwenye await s}

        self.assertEqual(
            run_async(run_set()),
            ([], {10, 20, 30}))

        async eleza run_set2():
            rudisha {await s
                    kila c kwenye [f([f(10), f(20)])]
                    kila s kwenye await c}

        self.assertEqual(
            run_async(run_set2()),
            ([], {10, 20}))

    eleza test_comp_3(self):
        async eleza f(it):
            kila i kwenye it:
                tuma i

        async eleza run_list():
            rudisha [i + 1 async kila i kwenye f([10, 20])]
        self.assertEqual(
            run_async(run_list()),
            ([], [11, 21]))

        async eleza run_set():
            rudisha {i + 1 async kila i kwenye f([10, 20])}
        self.assertEqual(
            run_async(run_set()),
            ([], {11, 21}))

        async eleza run_dict():
            rudisha {i + 1: i + 2 async kila i kwenye f([10, 20])}
        self.assertEqual(
            run_async(run_dict()),
            ([], {11: 12, 21: 22}))

        async eleza run_gen():
            gen = (i + 1 async kila i kwenye f([10, 20]))
            rudisha [g + 100 async kila g kwenye gen]
        self.assertEqual(
            run_async(run_gen()),
            ([], [111, 121]))

    eleza test_comp_4(self):
        async eleza f(it):
            kila i kwenye it:
                tuma i

        async eleza run_list():
            rudisha [i + 1 async kila i kwenye f([10, 20]) ikiwa i > 10]
        self.assertEqual(
            run_async(run_list()),
            ([], [21]))

        async eleza run_set():
            rudisha {i + 1 async kila i kwenye f([10, 20]) ikiwa i > 10}
        self.assertEqual(
            run_async(run_set()),
            ([], {21}))

        async eleza run_dict():
            rudisha {i + 1: i + 2 async kila i kwenye f([10, 20]) ikiwa i > 10}
        self.assertEqual(
            run_async(run_dict()),
            ([], {21: 22}))

        async eleza run_gen():
            gen = (i + 1 async kila i kwenye f([10, 20]) ikiwa i > 10)
            rudisha [g + 100 async kila g kwenye gen]
        self.assertEqual(
            run_async(run_gen()),
            ([], [121]))

    eleza test_comp_4_2(self):
        async eleza f(it):
            kila i kwenye it:
                tuma i

        async eleza run_list():
            rudisha [i + 10 async kila i kwenye f(range(5)) ikiwa 0 < i < 4]
        self.assertEqual(
            run_async(run_list()),
            ([], [11, 12, 13]))

        async eleza run_set():
            rudisha {i + 10 async kila i kwenye f(range(5)) ikiwa 0 < i < 4}
        self.assertEqual(
            run_async(run_set()),
            ([], {11, 12, 13}))

        async eleza run_dict():
            rudisha {i + 10: i + 100 async kila i kwenye f(range(5)) ikiwa 0 < i < 4}
        self.assertEqual(
            run_async(run_dict()),
            ([], {11: 101, 12: 102, 13: 103}))

        async eleza run_gen():
            gen = (i + 10 async kila i kwenye f(range(5)) ikiwa 0 < i < 4)
            rudisha [g + 100 async kila g kwenye gen]
        self.assertEqual(
            run_async(run_gen()),
            ([], [111, 112, 113]))

    eleza test_comp_5(self):
        async eleza f(it):
            kila i kwenye it:
                tuma i

        async eleza run_list():
            rudisha [i + 1 kila pair kwenye ([10, 20], [30, 40]) ikiwa pair[0] > 10
                    async kila i kwenye f(pair) ikiwa i > 30]
        self.assertEqual(
            run_async(run_list()),
            ([], [41]))

    eleza test_comp_6(self):
        async eleza f(it):
            kila i kwenye it:
                tuma i

        async eleza run_list():
            rudisha [i + 1 async kila seq kwenye f([(10, 20), (30,)])
                    kila i kwenye seq]

        self.assertEqual(
            run_async(run_list()),
            ([], [11, 21, 31]))

    eleza test_comp_7(self):
        async eleza f():
            tuma 1
            tuma 2
            ashiria Exception('aaa')

        async eleza run_list():
            rudisha [i async kila i kwenye f()]

        ukijumuisha self.assertRaisesRegex(Exception, 'aaa'):
            run_async(run_list())

    eleza test_comp_8(self):
        async eleza f():
            rudisha [i kila i kwenye [1, 2, 3]]

        self.assertEqual(
            run_async(f()),
            ([], [1, 2, 3]))

    eleza test_comp_9(self):
        async eleza gen():
            tuma 1
            tuma 2
        async eleza f():
            l = [i async kila i kwenye gen()]
            rudisha [i kila i kwenye l]

        self.assertEqual(
            run_async(f()),
            ([], [1, 2]))

    eleza test_comp_10(self):
        async eleza f():
            xx = {i kila i kwenye [1, 2, 3]}
            rudisha {x: x kila x kwenye xx}

        self.assertEqual(
            run_async(f()),
            ([], {1: 1, 2: 2, 3: 3}))

    eleza test_copy(self):
        async eleza func(): pita
        coro = func()
        ukijumuisha self.assertRaises(TypeError):
            copy.copy(coro)

        aw = coro.__await__()
        jaribu:
            ukijumuisha self.assertRaises(TypeError):
                copy.copy(aw)
        mwishowe:
            aw.close()

    eleza test_pickle(self):
        async eleza func(): pita
        coro = func()
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises((TypeError, pickle.PicklingError)):
                pickle.dumps(coro, proto)

        aw = coro.__await__()
        jaribu:
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                ukijumuisha self.assertRaises((TypeError, pickle.PicklingError)):
                    pickle.dumps(aw, proto)
        mwishowe:
            aw.close()

    eleza test_fatal_coro_warning(self):
        # Issue 27811
        async eleza func(): pita
        ukijumuisha warnings.catch_warnings(), \
             support.catch_unraisable_exception() kama cm:
            warnings.filterwarnings("error")
            coro = func()
            # only store repr() to avoid keeping the coroutine alive
            coro_repr = repr(coro)
            coro = Tupu
            support.gc_collect()

            self.assertIn("was never awaited", str(cm.unraisable.exc_value))
            self.assertEqual(repr(cm.unraisable.object), coro_repr)

    eleza test_for_assign_raising_stop_async_iteration(self):
        kundi BadTarget:
            eleza __setitem__(self, key, value):
                ashiria StopAsyncIteration(42)
        tgt = BadTarget()
        async eleza source():
            tuma 10

        async eleza run_for():
            ukijumuisha self.assertRaises(StopAsyncIteration) kama cm:
                async kila tgt[0] kwenye source():
                    pita
            self.assertEqual(cm.exception.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_for()), ([], 'end'))

        async eleza run_list():
            ukijumuisha self.assertRaises(StopAsyncIteration) kama cm:
                rudisha [0 async kila tgt[0] kwenye source()]
            self.assertEqual(cm.exception.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_list()), ([], 'end'))

        async eleza run_gen():
            gen = (0 async kila tgt[0] kwenye source())
            a = gen.asend(Tupu)
            ukijumuisha self.assertRaises(RuntimeError) kama cm:
                await a
            self.assertIsInstance(cm.exception.__cause__, StopAsyncIteration)
            self.assertEqual(cm.exception.__cause__.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_gen()), ([], 'end'))

    eleza test_for_assign_raising_stop_async_iteration_2(self):
        kundi BadIterable:
            eleza __iter__(self):
                ashiria StopAsyncIteration(42)
        async eleza badpairs():
            tuma BadIterable()

        async eleza run_for():
            ukijumuisha self.assertRaises(StopAsyncIteration) kama cm:
                async kila i, j kwenye badpairs():
                    pita
            self.assertEqual(cm.exception.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_for()), ([], 'end'))

        async eleza run_list():
            ukijumuisha self.assertRaises(StopAsyncIteration) kama cm:
                rudisha [0 async kila i, j kwenye badpairs()]
            self.assertEqual(cm.exception.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_list()), ([], 'end'))

        async eleza run_gen():
            gen = (0 async kila i, j kwenye badpairs())
            a = gen.asend(Tupu)
            ukijumuisha self.assertRaises(RuntimeError) kama cm:
                await a
            self.assertIsInstance(cm.exception.__cause__, StopAsyncIteration)
            self.assertEqual(cm.exception.__cause__.args, (42,))
            rudisha 'end'
        self.assertEqual(run_async(run_gen()), ([], 'end'))


kundi CoroAsyncIOCompatTest(unittest.TestCase):

    eleza test_asyncio_1(self):
        # asyncio cannot be imported when Python ni compiled without thread
        # support
        asyncio = support.import_module('asyncio')

        kundi MyException(Exception):
            pita

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
            async ukijumuisha CM() kama c:
                await asyncio.sleep(0.01)
                ashiria MyException
            buffer.append('unreachable')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        jaribu:
            loop.run_until_complete(f())
        tatizo MyException:
            pita
        mwishowe:
            loop.close()
            asyncio.set_event_loop_policy(Tupu)

        self.assertEqual(buffer, [1, 2, 'MyException'])


kundi OriginTrackingTest(unittest.TestCase):
    eleza here(self):
        info = inspect.getframeinfo(inspect.currentframe().f_back)
        rudisha (info.filename, info.lineno)

    eleza test_origin_tracking(self):
        orig_depth = sys.get_coroutine_origin_tracking_depth()
        jaribu:
            async eleza corofn():
                pita

            sys.set_coroutine_origin_tracking_depth(0)
            self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 0)

            ukijumuisha contextlib.closing(corofn()) kama coro:
                self.assertIsTupu(coro.cr_origin)

            sys.set_coroutine_origin_tracking_depth(1)
            self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 1)

            fname, lineno = self.here()
            ukijumuisha contextlib.closing(corofn()) kama coro:
                self.assertEqual(coro.cr_origin,
                                 ((fname, lineno + 1, "test_origin_tracking"),))

            sys.set_coroutine_origin_tracking_depth(2)
            self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 2)

            eleza nested():
                rudisha (self.here(), corofn())
            fname, lineno = self.here()
            ((nested_fname, nested_lineno), coro) = nested()
            ukijumuisha contextlib.closing(coro):
                self.assertEqual(coro.cr_origin,
                                 ((nested_fname, nested_lineno, "nested"),
                                  (fname, lineno + 1, "test_origin_tracking")))

            # Check we handle running out of frames correctly
            sys.set_coroutine_origin_tracking_depth(1000)
            ukijumuisha contextlib.closing(corofn()) kama coro:
                self.assertKweli(2 < len(coro.cr_origin) < 1000)

            # We can't set depth negative
            ukijumuisha self.assertRaises(ValueError):
                sys.set_coroutine_origin_tracking_depth(-1)
            # And trying leaves it unchanged
            self.assertEqual(sys.get_coroutine_origin_tracking_depth(), 1000)

        mwishowe:
            sys.set_coroutine_origin_tracking_depth(orig_depth)

    eleza test_origin_tracking_warning(self):
        async eleza corofn():
            pita

        a1_filename, a1_lineno = self.here()
        eleza a1():
            rudisha corofn()  # comment kwenye a1
        a1_lineno += 2

        a2_filename, a2_lineno = self.here()
        eleza a2():
            rudisha a1()  # comment kwenye a2
        a2_lineno += 2

        eleza check(depth, msg):
            sys.set_coroutine_origin_tracking_depth(depth)
            ukijumuisha self.assertWarns(RuntimeWarning) kama cm:
                a2()
                support.gc_collect()
            self.assertEqual(msg, str(cm.warning))

        orig_depth = sys.get_coroutine_origin_tracking_depth()
        jaribu:
            msg = check(0, f"coroutine '{corofn.__qualname__}' was never awaited")
            check(1, "".join([
                f"coroutine '{corofn.__qualname__}' was never awaited\n",
                "Coroutine created at (most recent call last)\n",
                f'  File "{a1_filename}", line {a1_lineno}, kwenye a1\n',
                f'    rudisha corofn()  # comment kwenye a1',
            ]))
            check(2, "".join([
                f"coroutine '{corofn.__qualname__}' was never awaited\n",
                "Coroutine created at (most recent call last)\n",
                f'  File "{a2_filename}", line {a2_lineno}, kwenye a2\n',
                f'    rudisha a1()  # comment kwenye a2\n',
                f'  File "{a1_filename}", line {a1_lineno}, kwenye a1\n',
                f'    rudisha corofn()  # comment kwenye a1',
            ]))

        mwishowe:
            sys.set_coroutine_origin_tracking_depth(orig_depth)

    eleza test_unawaited_warning_when_module_broken(self):
        # Make sure we don't blow up too bad if
        # warnings._warn_unawaited_coroutine ni broken somehow (e.g. because
        # of shutdown problems)
        async eleza corofn():
            pita

        orig_wuc = warnings._warn_unawaited_coroutine
        jaribu:
            warnings._warn_unawaited_coroutine = lambda coro: 1/0
            ukijumuisha support.catch_unraisable_exception() kama cm, \
                 support.check_warnings((r'coroutine .* was never awaited',
                                         RuntimeWarning)):
                # only store repr() to avoid keeping the coroutine alive
                coro = corofn()
                coro_repr = repr(coro)

                # clear reference to the coroutine without awaiting kila it
                toa coro
                support.gc_collect()

                self.assertEqual(repr(cm.unraisable.object), coro_repr)
                self.assertEqual(cm.unraisable.exc_type, ZeroDivisionError)

            toa warnings._warn_unawaited_coroutine
            ukijumuisha support.check_warnings((r'coroutine .* was never awaited',
                                         RuntimeWarning)):
                corofn()
                support.gc_collect()

        mwishowe:
            warnings._warn_unawaited_coroutine = orig_wuc


kundi UnawaitedWarningDuringShutdownTest(unittest.TestCase):
    # https://bugs.python.org/issue32591#msg310726
    eleza test_unawaited_warning_during_shutdown(self):
        code = ("agiza asyncio\n"
                "async eleza f(): pita\n"
                "asyncio.gather(f())\n")
        assert_python_ok("-c", code)

        code = ("agiza sys\n"
                "async eleza f(): pita\n"
                "sys.coro = f()\n")
        assert_python_ok("-c", code)

        code = ("agiza sys\n"
                "async eleza f(): pita\n"
                "sys.corocycle = [f()]\n"
                "sys.corocycle.append(sys.corocycle)\n")
        assert_python_ok("-c", code)


@support.cpython_only
kundi CAPITest(unittest.TestCase):

    eleza test_tp_await_1(self):
        kutoka _testcapi agiza awaitType kama at

        async eleza foo():
            future = at(iter([1]))
            rudisha (await future)

        self.assertEqual(foo().send(Tupu), 1)

    eleza test_tp_await_2(self):
        # Test tp_await to __await__ mapping
        kutoka _testcapi agiza awaitType kama at
        future = at(iter([1]))
        self.assertEqual(next(future.__await__()), 1)

    eleza test_tp_await_3(self):
        kutoka _testcapi agiza awaitType kama at

        async eleza foo():
            future = at(1)
            rudisha (await future)

        ukijumuisha self.assertRaisesRegex(
                TypeError, "__await__.*rudishaed non-iterator of type 'int'"):
            self.assertEqual(foo().send(Tupu), 1)


ikiwa __name__=="__main__":
    unittest.main()
