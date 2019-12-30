"""Tests kila tasks.py."""

agiza collections
agiza contextlib
agiza contextvars
agiza functools
agiza gc
agiza io
agiza random
agiza re
agiza sys
agiza textwrap
agiza types
agiza unittest
agiza weakref
kutoka unittest agiza mock

agiza asyncio
kutoka asyncio agiza coroutines
kutoka asyncio agiza futures
kutoka asyncio agiza tasks
kutoka test.test_asyncio agiza utils kama test_utils
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


async eleza coroutine_function():
    pita


@contextlib.contextmanager
eleza set_coroutine_debug(enabled):
    coroutines = asyncio.coroutines

    old_debug = coroutines._DEBUG
    jaribu:
        coroutines._DEBUG = enabled
        tuma
    mwishowe:
        coroutines._DEBUG = old_debug


eleza format_coroutine(qualname, state, src, source_traceback, generator=Uongo):
    ikiwa generator:
        state = '%s' % state
    isipokua:
        state = '%s, defined' % state
    ikiwa source_traceback ni sio Tupu:
        frame = source_traceback[-1]
        rudisha ('coro=<%s() %s at %s> created at %s:%s'
                % (qualname, state, src, frame[0], frame[1]))
    isipokua:
        rudisha 'coro=<%s() %s at %s>' % (qualname, state, src)


kundi Dummy:

    eleza __repr__(self):
        rudisha '<Dummy>'

    eleza __call__(self, *args):
        pita


kundi CoroLikeObject:
    eleza send(self, v):
        ashiria StopIteration(42)

    eleza throw(self, *exc):
        pita

    eleza close(self):
        pita

    eleza __await__(self):
        rudisha self


kundi BaseTaskTests:

    Task = Tupu
    Future = Tupu

    eleza new_task(self, loop, coro, name='TestTask'):
        rudisha self.__class__.Task(coro, loop=loop, name=name)

    eleza new_future(self, loop):
        rudisha self.__class__.Future(loop=loop)

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.loop.set_task_factory(self.new_task)
        self.loop.create_future = lambda: self.new_future(self.loop)

    eleza test_task_del_collect(self):
        kundi Evil:
            eleza __del__(self):
                gc.collect()

        async eleza run():
            rudisha Evil()

        self.loop.run_until_complete(
            asyncio.gather(*[
                self.new_task(self.loop, run()) kila _ kwenye range(100)
            ], loop=self.loop))

    eleza test_other_loop_future(self):
        other_loop = asyncio.new_event_loop()
        fut = self.new_future(other_loop)

        async eleza run(fut):
            await fut

        jaribu:
            ukijumuisha self.assertRaisesRegex(RuntimeError,
                                        r'Task .* got Future .* attached'):
                self.loop.run_until_complete(run(fut))
        mwishowe:
            other_loop.close()

    eleza test_task_awaits_on_itself(self):

        async eleza test():
            await task

        task = asyncio.ensure_future(test(), loop=self.loop)

        ukijumuisha self.assertRaisesRegex(RuntimeError,
                                    'Task cansio await on itself'):
            self.loop.run_until_complete(task)

    eleza test_task_class(self):
        async eleza notmuch():
            rudisha 'ok'
        t = self.new_task(self.loop, notmuch())
        self.loop.run_until_complete(t)
        self.assertKweli(t.done())
        self.assertEqual(t.result(), 'ok')
        self.assertIs(t._loop, self.loop)
        self.assertIs(t.get_loop(), self.loop)

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)
        t = self.new_task(loop, notmuch())
        self.assertIs(t._loop, loop)
        loop.run_until_complete(t)
        loop.close()

    eleza test_ensure_future_coroutine(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza notmuch():
                rudisha 'ok'
        t = asyncio.ensure_future(notmuch(), loop=self.loop)
        self.loop.run_until_complete(t)
        self.assertKweli(t.done())
        self.assertEqual(t.result(), 'ok')
        self.assertIs(t._loop, self.loop)

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)
        t = asyncio.ensure_future(notmuch(), loop=loop)
        self.assertIs(t._loop, loop)
        loop.run_until_complete(t)
        loop.close()

    eleza test_ensure_future_future(self):
        f_orig = self.new_future(self.loop)
        f_orig.set_result('ko')

        f = asyncio.ensure_future(f_orig)
        self.loop.run_until_complete(f)
        self.assertKweli(f.done())
        self.assertEqual(f.result(), 'ko')
        self.assertIs(f, f_orig)

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)

        ukijumuisha self.assertRaises(ValueError):
            f = asyncio.ensure_future(f_orig, loop=loop)

        loop.close()

        f = asyncio.ensure_future(f_orig, loop=self.loop)
        self.assertIs(f, f_orig)

    eleza test_ensure_future_task(self):
        async eleza notmuch():
            rudisha 'ok'
        t_orig = self.new_task(self.loop, notmuch())
        t = asyncio.ensure_future(t_orig)
        self.loop.run_until_complete(t)
        self.assertKweli(t.done())
        self.assertEqual(t.result(), 'ok')
        self.assertIs(t, t_orig)

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)

        ukijumuisha self.assertRaises(ValueError):
            t = asyncio.ensure_future(t_orig, loop=loop)

        loop.close()

        t = asyncio.ensure_future(t_orig, loop=self.loop)
        self.assertIs(t, t_orig)

    eleza test_ensure_future_awaitable(self):
        kundi Aw:
            eleza __init__(self, coro):
                self.coro = coro
            eleza __await__(self):
                rudisha (tuma kutoka self.coro)

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro():
                rudisha 'ok'

        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)
        fut = asyncio.ensure_future(Aw(coro()), loop=loop)
        loop.run_until_complete(fut)
        assert fut.result() == 'ok'

    eleza test_ensure_future_neither(self):
        ukijumuisha self.assertRaises(TypeError):
            asyncio.ensure_future('ok')

    eleza test_ensure_future_error_msg(self):
        loop = asyncio.new_event_loop()
        f = self.new_future(self.loop)
        ukijumuisha self.assertRaisesRegex(ValueError, 'The future belongs to a '
                                    'different loop than the one specified kama '
                                    'the loop argument'):
            asyncio.ensure_future(f, loop=loop)
        loop.close()

    eleza test_get_stack(self):
        T = Tupu

        async eleza foo():
            await bar()

        async eleza bar():
            # test get_stack()
            f = T.get_stack(limit=1)
            jaribu:
                self.assertEqual(f[0].f_code.co_name, 'foo')
            mwishowe:
                f = Tupu

            # test print_stack()
            file = io.StringIO()
            T.print_stack(limit=1, file=file)
            file.seek(0)
            tb = file.read()
            self.assertRegex(tb, r'foo\(\) running')

        async eleza runner():
            nonlocal T
            T = asyncio.ensure_future(foo(), loop=self.loop)
            await T

        self.loop.run_until_complete(runner())

    eleza test_task_repr(self):
        self.loop.set_debug(Uongo)

        async eleza notmuch():
            rudisha 'abc'

        # test coroutine function
        self.assertEqual(notmuch.__name__, 'notmuch')
        self.assertRegex(notmuch.__qualname__,
                         r'\w+.test_task_repr.<locals>.notmuch')
        self.assertEqual(notmuch.__module__, __name__)

        filename, lineno = test_utils.get_function_source(notmuch)
        src = "%s:%s" % (filename, lineno)

        # test coroutine object
        gen = notmuch()
        coro_qualname = 'BaseTaskTests.test_task_repr.<locals>.notmuch'
        self.assertEqual(gen.__name__, 'notmuch')
        self.assertEqual(gen.__qualname__, coro_qualname)

        # test pending Task
        t = self.new_task(self.loop, gen)
        t.add_done_callback(Dummy())

        coro = format_coroutine(coro_qualname, 'running', src,
                                t._source_traceback, generator=Kweli)
        self.assertEqual(repr(t),
                         "<Task pending name='TestTask' %s cb=[<Dummy>()]>" % coro)

        # test cancelling Task
        t.cancel()  # Does sio take immediate effect!
        self.assertEqual(repr(t),
                         "<Task cancelling name='TestTask' %s cb=[<Dummy>()]>" % coro)

        # test cancelled Task
        self.assertRaises(asyncio.CancelledError,
                          self.loop.run_until_complete, t)
        coro = format_coroutine(coro_qualname, 'done', src,
                                t._source_traceback)
        self.assertEqual(repr(t),
                         "<Task cancelled name='TestTask' %s>" % coro)

        # test finished Task
        t = self.new_task(self.loop, notmuch())
        self.loop.run_until_complete(t)
        coro = format_coroutine(coro_qualname, 'done', src,
                                t._source_traceback)
        self.assertEqual(repr(t),
                         "<Task finished name='TestTask' %s result='abc'>" % coro)

    eleza test_task_repr_autogenerated(self):
        async eleza notmuch():
            rudisha 123

        t1 = self.new_task(self.loop, notmuch(), Tupu)
        t2 = self.new_task(self.loop, notmuch(), Tupu)
        self.assertNotEqual(repr(t1), repr(t2))

        match1 = re.match(r"^<Task pending name='Task-(\d+)'", repr(t1))
        self.assertIsNotTupu(match1)
        match2 = re.match(r"^<Task pending name='Task-(\d+)'", repr(t2))
        self.assertIsNotTupu(match2)

        # Autogenerated task names should have monotonically increasing numbers
        self.assertLess(int(match1.group(1)), int(match2.group(1)))
        self.loop.run_until_complete(t1)
        self.loop.run_until_complete(t2)

    eleza test_task_repr_name_not_str(self):
        async eleza notmuch():
            rudisha 123

        t = self.new_task(self.loop, notmuch())
        t.set_name({6})
        self.assertEqual(t.get_name(), '{6}')
        self.loop.run_until_complete(t)

    eleza test_task_repr_coro_decorator(self):
        self.loop.set_debug(Uongo)

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza notmuch():
                # notmuch() function doesn't use tuma from: it will be wrapped by
                # @coroutine decorator
                rudisha 123

        # test coroutine function
        self.assertEqual(notmuch.__name__, 'notmuch')
        self.assertRegex(notmuch.__qualname__,
                         r'\w+.test_task_repr_coro_decorator'
                         r'\.<locals>\.notmuch')
        self.assertEqual(notmuch.__module__, __name__)

        # test coroutine object
        gen = notmuch()
        # On Python >= 3.5, generators now inherit the name of the
        # function, kama expected, na have a qualified name (__qualname__
        # attribute).
        coro_name = 'notmuch'
        coro_qualname = ('BaseTaskTests.test_task_repr_coro_decorator'
                         '.<locals>.notmuch')
        self.assertEqual(gen.__name__, coro_name)
        self.assertEqual(gen.__qualname__, coro_qualname)

        # test repr(CoroWrapper)
        ikiwa coroutines._DEBUG:
            # format the coroutine object
            ikiwa coroutines._DEBUG:
                filename, lineno = test_utils.get_function_source(notmuch)
                frame = gen._source_traceback[-1]
                coro = ('%s() running, defined at %s:%s, created at %s:%s'
                        % (coro_qualname, filename, lineno,
                           frame[0], frame[1]))
            isipokua:
                code = gen.gi_code
                coro = ('%s() running at %s:%s'
                        % (coro_qualname, code.co_filename,
                           code.co_firstlineno))

            self.assertEqual(repr(gen), '<CoroWrapper %s>' % coro)

        # test pending Task
        t = self.new_task(self.loop, gen)
        t.add_done_callback(Dummy())

        # format the coroutine object
        ikiwa coroutines._DEBUG:
            src = '%s:%s' % test_utils.get_function_source(notmuch)
        isipokua:
            code = gen.gi_code
            src = '%s:%s' % (code.co_filename, code.co_firstlineno)
        coro = format_coroutine(coro_qualname, 'running', src,
                                t._source_traceback,
                                generator=sio coroutines._DEBUG)
        self.assertEqual(repr(t),
                         "<Task pending name='TestTask' %s cb=[<Dummy>()]>" % coro)
        self.loop.run_until_complete(t)

    eleza test_task_repr_wait_for(self):
        self.loop.set_debug(Uongo)

        async eleza wait_for(fut):
            rudisha await fut

        fut = self.new_future(self.loop)
        task = self.new_task(self.loop, wait_for(fut))
        test_utils.run_briefly(self.loop)
        self.assertRegex(repr(task),
                         '<Task .* wait_for=%s>' % re.escape(repr(fut)))

        fut.set_result(Tupu)
        self.loop.run_until_complete(task)

    eleza test_task_repr_partial_corowrapper(self):
        # Issue #222: repr(CoroWrapper) must sio fail kwenye debug mode ikiwa the
        # coroutine ni a partial function
        ukijumuisha set_coroutine_debug(Kweli):
            self.loop.set_debug(Kweli)

            async eleza func(x, y):
                await asyncio.sleep(0)

            ukijumuisha self.assertWarns(DeprecationWarning):
                partial_func = asyncio.coroutine(functools.partial(func, 1))
            task = self.loop.create_task(partial_func(2))

            # make warnings quiet
            task._log_destroy_pending = Uongo
            self.addCleanup(task._coro.close)

        coro_repr = repr(task._coro)
        expected = (
            r'<coroutine object \w+\.test_task_repr_partial_corowrapper'
            r'\.<locals>\.func at'
        )
        self.assertRegex(coro_repr, expected)

    eleza test_task_basics(self):

        async eleza outer():
            a = await inner1()
            b = await inner2()
            rudisha a+b

        async eleza inner1():
            rudisha 42

        async eleza inner2():
            rudisha 1000

        t = outer()
        self.assertEqual(self.loop.run_until_complete(t), 1042)

    eleza test_cancel(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(10.0, when)
            tuma 0

        loop = self.new_test_loop(gen)

        async eleza task():
            await asyncio.sleep(10.0)
            rudisha 12

        t = self.new_task(loop, task())
        loop.call_soon(t.cancel)
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            loop.run_until_complete(t)
        self.assertKweli(t.done())
        self.assertKweli(t.cancelled())
        self.assertUongo(t.cancel())

    eleza test_cancel_tuma(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza task():
                tuma
                tuma
                rudisha 12

        t = self.new_task(self.loop, task())
        test_utils.run_briefly(self.loop)  # start coro
        t.cancel()
        self.assertRaises(
            asyncio.CancelledError, self.loop.run_until_complete, t)
        self.assertKweli(t.done())
        self.assertKweli(t.cancelled())
        self.assertUongo(t.cancel())

    eleza test_cancel_inner_future(self):
        f = self.new_future(self.loop)

        async eleza task():
            await f
            rudisha 12

        t = self.new_task(self.loop, task())
        test_utils.run_briefly(self.loop)  # start task
        f.cancel()
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(t)
        self.assertKweli(f.cancelled())
        self.assertKweli(t.cancelled())

    eleza test_cancel_both_task_and_inner_future(self):
        f = self.new_future(self.loop)

        async eleza task():
            await f
            rudisha 12

        t = self.new_task(self.loop, task())
        test_utils.run_briefly(self.loop)

        f.cancel()
        t.cancel()

        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(t)

        self.assertKweli(t.done())
        self.assertKweli(f.cancelled())
        self.assertKweli(t.cancelled())

    eleza test_cancel_task_catching(self):
        fut1 = self.new_future(self.loop)
        fut2 = self.new_future(self.loop)

        async eleza task():
            await fut1
            jaribu:
                await fut2
            tatizo asyncio.CancelledError:
                rudisha 42

        t = self.new_task(self.loop, task())
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut1)  # White-box test.
        fut1.set_result(Tupu)
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut2)  # White-box test.
        t.cancel()
        self.assertKweli(fut2.cancelled())
        res = self.loop.run_until_complete(t)
        self.assertEqual(res, 42)
        self.assertUongo(t.cancelled())

    eleza test_cancel_task_ignoring(self):
        fut1 = self.new_future(self.loop)
        fut2 = self.new_future(self.loop)
        fut3 = self.new_future(self.loop)

        async eleza task():
            await fut1
            jaribu:
                await fut2
            tatizo asyncio.CancelledError:
                pita
            res = await fut3
            rudisha res

        t = self.new_task(self.loop, task())
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut1)  # White-box test.
        fut1.set_result(Tupu)
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut2)  # White-box test.
        t.cancel()
        self.assertKweli(fut2.cancelled())
        test_utils.run_briefly(self.loop)
        self.assertIs(t._fut_waiter, fut3)  # White-box test.
        fut3.set_result(42)
        res = self.loop.run_until_complete(t)
        self.assertEqual(res, 42)
        self.assertUongo(fut3.cancelled())
        self.assertUongo(t.cancelled())

    eleza test_cancel_current_task(self):
        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)

        async eleza task():
            t.cancel()
            self.assertKweli(t._must_cancel)  # White-box test.
            # The sleep should be cancelled immediately.
            await asyncio.sleep(100)
            rudisha 12

        t = self.new_task(loop, task())
        self.assertUongo(t.cancelled())
        self.assertRaises(
            asyncio.CancelledError, loop.run_until_complete, t)
        self.assertKweli(t.done())
        self.assertKweli(t.cancelled())
        self.assertUongo(t._must_cancel)  # White-box test.
        self.assertUongo(t.cancel())

    eleza test_cancel_at_end(self):
        """coroutine end right after task ni cancelled"""
        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)

        async eleza task():
            t.cancel()
            self.assertKweli(t._must_cancel)  # White-box test.
            rudisha 12

        t = self.new_task(loop, task())
        self.assertUongo(t.cancelled())
        self.assertRaises(
            asyncio.CancelledError, loop.run_until_complete, t)
        self.assertKweli(t.done())
        self.assertKweli(t.cancelled())
        self.assertUongo(t._must_cancel)  # White-box test.
        self.assertUongo(t.cancel())

    eleza test_cancel_awaited_task(self):
        # This tests kila a relatively rare condition when
        # a task cancellation ni requested kila a task which ni sio
        # currently blocked, such kama a task cancelling itself.
        # In this situation we must ensure that whatever next future
        # ama task the cancelled task blocks on ni cancelled correctly
        # kama well.  See also bpo-34872.
        loop = asyncio.new_event_loop()
        self.addCleanup(lambda: loop.close())

        task = nested_task = Tupu
        fut = self.new_future(loop)

        async eleza nested():
            await fut

        async eleza coro():
            nonlocal nested_task
            # Create a sub-task na wait kila it to run.
            nested_task = self.new_task(loop, nested())
            await asyncio.sleep(0)

            # Request the current task to be cancelled.
            task.cancel()
            # Block on the nested task, which should be immediately
            # cancelled.
            await nested_task

        task = self.new_task(loop, coro())
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            loop.run_until_complete(task)

        self.assertKweli(task.cancelled())
        self.assertKweli(nested_task.cancelled())
        self.assertKweli(fut.cancelled())

    eleza test_stop_while_run_in_complete(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.1, when)
            when = tuma 0.1
            self.assertAlmostEqual(0.2, when)
            when = tuma 0.1
            self.assertAlmostEqual(0.3, when)
            tuma 0.1

        loop = self.new_test_loop(gen)

        x = 0

        async eleza task():
            nonlocal x
            wakati x < 10:
                await asyncio.sleep(0.1)
                x += 1
                ikiwa x == 2:
                    loop.stop()

        t = self.new_task(loop, task())
        ukijumuisha self.assertRaises(RuntimeError) kama cm:
            loop.run_until_complete(t)
        self.assertEqual(str(cm.exception),
                         'Event loop stopped before Future completed.')
        self.assertUongo(t.done())
        self.assertEqual(x, 2)
        self.assertAlmostEqual(0.3, loop.time())

        t.cancel()
        self.assertRaises(asyncio.CancelledError, loop.run_until_complete, t)

    eleza test_log_traceback(self):
        async eleza coro():
            pita

        task = self.new_task(self.loop, coro())
        ukijumuisha self.assertRaisesRegex(ValueError, 'can only be set to Uongo'):
            task._log_traceback = Kweli
        self.loop.run_until_complete(task)

    eleza test_wait_for_timeout_less_then_0_or_0_future_done(self):
        eleza gen():
            when = tuma
            self.assertAlmostEqual(0, when)

        loop = self.new_test_loop(gen)

        fut = self.new_future(loop)
        fut.set_result('done')

        ret = loop.run_until_complete(asyncio.wait_for(fut, 0))

        self.assertEqual(ret, 'done')
        self.assertKweli(fut.done())
        self.assertAlmostEqual(0, loop.time())

    eleza test_wait_for_timeout_less_then_0_or_0_coroutine_do_not_started(self):
        eleza gen():
            when = tuma
            self.assertAlmostEqual(0, when)

        loop = self.new_test_loop(gen)

        foo_started = Uongo

        async eleza foo():
            nonlocal foo_started
            foo_started = Kweli

        ukijumuisha self.assertRaises(asyncio.TimeoutError):
            loop.run_until_complete(asyncio.wait_for(foo(), 0))

        self.assertAlmostEqual(0, loop.time())
        self.assertEqual(foo_started, Uongo)

    eleza test_wait_for_timeout_less_then_0_or_0(self):
        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.2, when)
            when = tuma 0
            self.assertAlmostEqual(0, when)

        kila timeout kwenye [0, -1]:
            ukijumuisha self.subTest(timeout=timeout):
                loop = self.new_test_loop(gen)

                foo_running = Tupu

                async eleza foo():
                    nonlocal foo_running
                    foo_running = Kweli
                    jaribu:
                        await asyncio.sleep(0.2)
                    mwishowe:
                        foo_running = Uongo
                    rudisha 'done'

                fut = self.new_task(loop, foo())

                ukijumuisha self.assertRaises(asyncio.TimeoutError):
                    loop.run_until_complete(asyncio.wait_for(fut, timeout))
                self.assertKweli(fut.done())
                # it should have been cancelled due to the timeout
                self.assertKweli(fut.cancelled())
                self.assertAlmostEqual(0, loop.time())
                self.assertEqual(foo_running, Uongo)

    eleza test_wait_for(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.2, when)
            when = tuma 0
            self.assertAlmostEqual(0.1, when)
            when = tuma 0.1

        loop = self.new_test_loop(gen)

        foo_running = Tupu

        async eleza foo():
            nonlocal foo_running
            foo_running = Kweli
            jaribu:
                await asyncio.sleep(0.2)
            mwishowe:
                foo_running = Uongo
            rudisha 'done'

        fut = self.new_task(loop, foo())

        ukijumuisha self.assertRaises(asyncio.TimeoutError):
            loop.run_until_complete(asyncio.wait_for(fut, 0.1))
        self.assertKweli(fut.done())
        # it should have been cancelled due to the timeout
        self.assertKweli(fut.cancelled())
        self.assertAlmostEqual(0.1, loop.time())
        self.assertEqual(foo_running, Uongo)

    eleza test_wait_for_blocking(self):
        loop = self.new_test_loop()

        async eleza coro():
            rudisha 'done'

        res = loop.run_until_complete(asyncio.wait_for(coro(), timeout=Tupu))
        self.assertEqual(res, 'done')

    eleza test_wait_for_with_global_loop(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.2, when)
            when = tuma 0
            self.assertAlmostEqual(0.01, when)
            tuma 0.01

        loop = self.new_test_loop(gen)

        async eleza foo():
            await asyncio.sleep(0.2)
            rudisha 'done'

        asyncio.set_event_loop(loop)
        jaribu:
            fut = self.new_task(loop, foo())
            ukijumuisha self.assertRaises(asyncio.TimeoutError):
                loop.run_until_complete(asyncio.wait_for(fut, 0.01))
        mwishowe:
            asyncio.set_event_loop(Tupu)

        self.assertAlmostEqual(0.01, loop.time())
        self.assertKweli(fut.done())
        self.assertKweli(fut.cancelled())

    eleza test_wait_for_race_condition(self):

        eleza gen():
            tuma 0.1
            tuma 0.1
            tuma 0.1

        loop = self.new_test_loop(gen)

        fut = self.new_future(loop)
        task = asyncio.wait_for(fut, timeout=0.2)
        loop.call_later(0.1, fut.set_result, "ok")
        res = loop.run_until_complete(task)
        self.assertEqual(res, "ok")

    eleza test_wait_for_waits_for_task_cancellation(self):
        loop = asyncio.new_event_loop()
        self.addCleanup(loop.close)

        task_done = Uongo

        async eleza foo():
            async eleza inner():
                nonlocal task_done
                jaribu:
                    await asyncio.sleep(0.2)
                mwishowe:
                    task_done = Kweli

            inner_task = self.new_task(loop, inner())

            ukijumuisha self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(inner_task, timeout=0.1)

            self.assertKweli(task_done)

        loop.run_until_complete(foo())

    eleza test_wait_for_self_cancellation(self):
        loop = asyncio.new_event_loop()
        self.addCleanup(loop.close)

        async eleza foo():
            async eleza inner():
                jaribu:
                    await asyncio.sleep(0.3)
                tatizo asyncio.CancelledError:
                    jaribu:
                        await asyncio.sleep(0.3)
                    tatizo asyncio.CancelledError:
                        await asyncio.sleep(0.3)

                rudisha 42

            inner_task = self.new_task(loop, inner())

            wait = asyncio.wait_for(inner_task, timeout=0.1)

            # Test that wait_kila itself ni properly cancellable
            # even when the initial task holds up the initial cancellation.
            task = self.new_task(loop, wait)
            await asyncio.sleep(0.2)
            task.cancel()

            ukijumuisha self.assertRaises(asyncio.CancelledError):
                await task

            self.assertEqual(await inner_task, 42)

        loop.run_until_complete(foo())

    eleza test_wait(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.1, when)
            when = tuma 0
            self.assertAlmostEqual(0.15, when)
            tuma 0.15

        loop = self.new_test_loop(gen)

        a = self.new_task(loop, asyncio.sleep(0.1))
        b = self.new_task(loop, asyncio.sleep(0.15))

        async eleza foo():
            done, pending = await asyncio.wait([b, a])
            self.assertEqual(done, set([a, b]))
            self.assertEqual(pending, set())
            rudisha 42

        res = loop.run_until_complete(self.new_task(loop, foo()))
        self.assertEqual(res, 42)
        self.assertAlmostEqual(0.15, loop.time())

        # Doing it again should take no time na exercise a different path.
        res = loop.run_until_complete(self.new_task(loop, foo()))
        self.assertAlmostEqual(0.15, loop.time())
        self.assertEqual(res, 42)

    eleza test_wait_with_global_loop(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.01, when)
            when = tuma 0
            self.assertAlmostEqual(0.015, when)
            tuma 0.015

        loop = self.new_test_loop(gen)

        a = self.new_task(loop, asyncio.sleep(0.01))
        b = self.new_task(loop, asyncio.sleep(0.015))

        async eleza foo():
            done, pending = await asyncio.wait([b, a])
            self.assertEqual(done, set([a, b]))
            self.assertEqual(pending, set())
            rudisha 42

        asyncio.set_event_loop(loop)
        res = loop.run_until_complete(
            self.new_task(loop, foo()))

        self.assertEqual(res, 42)

    eleza test_wait_duplicate_coroutines(self):

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro(s):
                rudisha s
        c = coro('test')

        task =self.new_task(
            self.loop,
            asyncio.wait([c, c, coro('spam')]))

        done, pending = self.loop.run_until_complete(task)

        self.assertUongo(pending)
        self.assertEqual(set(f.result() kila f kwenye done), {'test', 'spam'})

    eleza test_wait_errors(self):
        self.assertRaises(
            ValueError, self.loop.run_until_complete,
            asyncio.wait(set()))

        # -1 ni an invalid return_when value
        sleep_coro = asyncio.sleep(10.0)
        wait_coro = asyncio.wait([sleep_coro], return_when=-1)
        self.assertRaises(ValueError,
                          self.loop.run_until_complete, wait_coro)

        sleep_coro.close()

    eleza test_wait_first_completed(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(10.0, when)
            when = tuma 0
            self.assertAlmostEqual(0.1, when)
            tuma 0.1

        loop = self.new_test_loop(gen)

        a = self.new_task(loop, asyncio.sleep(10.0))
        b = self.new_task(loop, asyncio.sleep(0.1))
        task = self.new_task(
            loop,
            asyncio.wait([b, a], return_when=asyncio.FIRST_COMPLETED))

        done, pending = loop.run_until_complete(task)
        self.assertEqual({b}, done)
        self.assertEqual({a}, pending)
        self.assertUongo(a.done())
        self.assertKweli(b.done())
        self.assertIsTupu(b.result())
        self.assertAlmostEqual(0.1, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b]))

    eleza test_wait_really_done(self):
        # there ni possibility that some tasks kwenye the pending list
        # became done but their callbacks haven't all been called yet

        async eleza coro1():
            await asyncio.sleep(0)

        async eleza coro2():
            await asyncio.sleep(0)
            await asyncio.sleep(0)

        a = self.new_task(self.loop, coro1())
        b = self.new_task(self.loop, coro2())
        task = self.new_task(
            self.loop,
            asyncio.wait([b, a], return_when=asyncio.FIRST_COMPLETED))

        done, pending = self.loop.run_until_complete(task)
        self.assertEqual({a, b}, done)
        self.assertKweli(a.done())
        self.assertIsTupu(a.result())
        self.assertKweli(b.done())
        self.assertIsTupu(b.result())

    eleza test_wait_first_exception(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(10.0, when)
            tuma 0

        loop = self.new_test_loop(gen)

        # first_exception, task already has exception
        a = self.new_task(loop, asyncio.sleep(10.0))

        async eleza exc():
            ashiria ZeroDivisionError('err')

        b = self.new_task(loop, exc())
        task = self.new_task(
            loop,
            asyncio.wait([b, a], return_when=asyncio.FIRST_EXCEPTION))

        done, pending = loop.run_until_complete(task)
        self.assertEqual({b}, done)
        self.assertEqual({a}, pending)
        self.assertAlmostEqual(0, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b]))

    eleza test_wait_first_exception_in_wait(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(10.0, when)
            when = tuma 0
            self.assertAlmostEqual(0.01, when)
            tuma 0.01

        loop = self.new_test_loop(gen)

        # first_exception, exception during waiting
        a = self.new_task(loop, asyncio.sleep(10.0))

        async eleza exc():
            await asyncio.sleep(0.01)
            ashiria ZeroDivisionError('err')

        b = self.new_task(loop, exc())
        task = asyncio.wait([b, a], return_when=asyncio.FIRST_EXCEPTION)

        done, pending = loop.run_until_complete(task)
        self.assertEqual({b}, done)
        self.assertEqual({a}, pending)
        self.assertAlmostEqual(0.01, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b]))

    eleza test_wait_with_exception(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.1, when)
            when = tuma 0
            self.assertAlmostEqual(0.15, when)
            tuma 0.15

        loop = self.new_test_loop(gen)

        a = self.new_task(loop, asyncio.sleep(0.1))

        async eleza sleeper():
            await asyncio.sleep(0.15)
            ashiria ZeroDivisionError('really')

        b = self.new_task(loop, sleeper())

        async eleza foo():
            done, pending = await asyncio.wait([b, a])
            self.assertEqual(len(done), 2)
            self.assertEqual(pending, set())
            errors = set(f kila f kwenye done ikiwa f.exception() ni sio Tupu)
            self.assertEqual(len(errors), 1)

        loop.run_until_complete(self.new_task(loop, foo()))
        self.assertAlmostEqual(0.15, loop.time())

        loop.run_until_complete(self.new_task(loop, foo()))
        self.assertAlmostEqual(0.15, loop.time())

    eleza test_wait_with_timeout(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.1, when)
            when = tuma 0
            self.assertAlmostEqual(0.15, when)
            when = tuma 0
            self.assertAlmostEqual(0.11, when)
            tuma 0.11

        loop = self.new_test_loop(gen)

        a = self.new_task(loop, asyncio.sleep(0.1))
        b = self.new_task(loop, asyncio.sleep(0.15))

        async eleza foo():
            done, pending = await asyncio.wait([b, a], timeout=0.11)
            self.assertEqual(done, set([a]))
            self.assertEqual(pending, set([b]))

        loop.run_until_complete(self.new_task(loop, foo()))
        self.assertAlmostEqual(0.11, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b]))

    eleza test_wait_concurrent_complete(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.1, when)
            when = tuma 0
            self.assertAlmostEqual(0.15, when)
            when = tuma 0
            self.assertAlmostEqual(0.1, when)
            tuma 0.1

        loop = self.new_test_loop(gen)

        a = self.new_task(loop, asyncio.sleep(0.1))
        b = self.new_task(loop, asyncio.sleep(0.15))

        done, pending = loop.run_until_complete(
            asyncio.wait([b, a], timeout=0.1))

        self.assertEqual(done, set([a]))
        self.assertEqual(pending, set([b]))
        self.assertAlmostEqual(0.1, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b]))

    eleza test_as_completed(self):

        eleza gen():
            tuma 0
            tuma 0
            tuma 0.01
            tuma 0

        loop = self.new_test_loop(gen)
        # disable "slow callback" warning
        loop.slow_callback_duration = 1.0
        completed = set()
        time_shifted = Uongo

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza sleeper(dt, x):
                nonlocal time_shifted
                tuma kutoka  asyncio.sleep(dt)
                completed.add(x)
                ikiwa sio time_shifted na 'a' kwenye completed na 'b' kwenye completed:
                    time_shifted = Kweli
                    loop.advance_time(0.14)
                rudisha x

        a = sleeper(0.01, 'a')
        b = sleeper(0.01, 'b')
        c = sleeper(0.15, 'c')

        async eleza foo():
            values = []
            kila f kwenye asyncio.as_completed([b, c, a], loop=loop):
                values.append(await f)
            rudisha values
        ukijumuisha self.assertWarns(DeprecationWarning):
            res = loop.run_until_complete(self.new_task(loop, foo()))
        self.assertAlmostEqual(0.15, loop.time())
        self.assertKweli('a' kwenye res[:2])
        self.assertKweli('b' kwenye res[:2])
        self.assertEqual(res[2], 'c')

        # Doing it again should take no time na exercise a different path.
        ukijumuisha self.assertWarns(DeprecationWarning):
            res = loop.run_until_complete(self.new_task(loop, foo()))
        self.assertAlmostEqual(0.15, loop.time())

    eleza test_as_completed_with_timeout(self):

        eleza gen():
            tuma
            tuma 0
            tuma 0
            tuma 0.1

        loop = self.new_test_loop(gen)

        a = loop.create_task(asyncio.sleep(0.1, 'a'))
        b = loop.create_task(asyncio.sleep(0.15, 'b'))

        async eleza foo():
            values = []
            kila f kwenye asyncio.as_completed([a, b], timeout=0.12, loop=loop):
                ikiwa values:
                    loop.advance_time(0.02)
                jaribu:
                    v = await f
                    values.append((1, v))
                tatizo asyncio.TimeoutError kama exc:
                    values.append((2, exc))
            rudisha values

        ukijumuisha self.assertWarns(DeprecationWarning):
            res = loop.run_until_complete(self.new_task(loop, foo()))
        self.assertEqual(len(res), 2, res)
        self.assertEqual(res[0], (1, 'a'))
        self.assertEqual(res[1][0], 2)
        self.assertIsInstance(res[1][1], asyncio.TimeoutError)
        self.assertAlmostEqual(0.12, loop.time())

        # move forward to close generator
        loop.advance_time(10)
        loop.run_until_complete(asyncio.wait([a, b]))

    eleza test_as_completed_with_unused_timeout(self):

        eleza gen():
            tuma
            tuma 0
            tuma 0.01

        loop = self.new_test_loop(gen)

        a = asyncio.sleep(0.01, 'a')

        async eleza foo():
            kila f kwenye asyncio.as_completed([a], timeout=1, loop=loop):
                v = await f
                self.assertEqual(v, 'a')

        ukijumuisha self.assertWarns(DeprecationWarning):
            loop.run_until_complete(self.new_task(loop, foo()))

    eleza test_as_completed_reverse_wait(self):

        eleza gen():
            tuma 0
            tuma 0.05
            tuma 0

        loop = self.new_test_loop(gen)

        a = asyncio.sleep(0.05, 'a')
        b = asyncio.sleep(0.10, 'b')
        fs = {a, b}

        ukijumuisha self.assertWarns(DeprecationWarning):
            futs = list(asyncio.as_completed(fs, loop=loop))
        self.assertEqual(len(futs), 2)

        x = loop.run_until_complete(futs[1])
        self.assertEqual(x, 'a')
        self.assertAlmostEqual(0.05, loop.time())
        loop.advance_time(0.05)
        y = loop.run_until_complete(futs[0])
        self.assertEqual(y, 'b')
        self.assertAlmostEqual(0.10, loop.time())

    eleza test_as_completed_concurrent(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.05, when)
            when = tuma 0
            self.assertAlmostEqual(0.05, when)
            tuma 0.05

        loop = self.new_test_loop(gen)

        a = asyncio.sleep(0.05, 'a')
        b = asyncio.sleep(0.05, 'b')
        fs = {a, b}
        ukijumuisha self.assertWarns(DeprecationWarning):
            futs = list(asyncio.as_completed(fs, loop=loop))
        self.assertEqual(len(futs), 2)
        waiter = asyncio.wait(futs)
        done, pending = loop.run_until_complete(waiter)
        self.assertEqual(set(f.result() kila f kwenye done), {'a', 'b'})

    eleza test_as_completed_duplicate_coroutines(self):

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro(s):
                rudisha s

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza runner():
                result = []
                c = coro('ham')
                kila f kwenye asyncio.as_completed([c, c, coro('spam')],
                                              loop=self.loop):
                    result.append((tuma kutoka f))
                rudisha result

        ukijumuisha self.assertWarns(DeprecationWarning):
            fut = self.new_task(self.loop, runner())
            self.loop.run_until_complete(fut)
        result = fut.result()
        self.assertEqual(set(result), {'ham', 'spam'})
        self.assertEqual(len(result), 2)

    eleza test_sleep(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.05, when)
            when = tuma 0.05
            self.assertAlmostEqual(0.1, when)
            tuma 0.05

        loop = self.new_test_loop(gen)

        async eleza sleeper(dt, arg):
            await asyncio.sleep(dt/2)
            res = await asyncio.sleep(dt/2, arg)
            rudisha res

        t = self.new_task(loop, sleeper(0.1, 'yeah'))
        loop.run_until_complete(t)
        self.assertKweli(t.done())
        self.assertEqual(t.result(), 'yeah')
        self.assertAlmostEqual(0.1, loop.time())

    eleza test_sleep_cancel(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(10.0, when)
            tuma 0

        loop = self.new_test_loop(gen)

        t = self.new_task(loop, asyncio.sleep(10.0, 'yeah'))

        handle = Tupu
        orig_call_later = loop.call_later

        eleza call_later(delay, callback, *args):
            nonlocal handle
            handle = orig_call_later(delay, callback, *args)
            rudisha handle

        loop.call_later = call_later
        test_utils.run_briefly(loop)

        self.assertUongo(handle._cancelled)

        t.cancel()
        test_utils.run_briefly(loop)
        self.assertKweli(handle._cancelled)

    eleza test_task_cancel_sleeping_task(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(0.1, when)
            when = tuma 0
            self.assertAlmostEqual(5000, when)
            tuma 0.1

        loop = self.new_test_loop(gen)

        async eleza sleep(dt):
            await asyncio.sleep(dt)

        async eleza doit():
            sleeper = self.new_task(loop, sleep(5000))
            loop.call_later(0.1, sleeper.cancel)
            jaribu:
                await sleeper
            tatizo asyncio.CancelledError:
                rudisha 'cancelled'
            isipokua:
                rudisha 'slept in'

        doer = doit()
        self.assertEqual(loop.run_until_complete(doer), 'cancelled')
        self.assertAlmostEqual(0.1, loop.time())

    eleza test_task_cancel_waiter_future(self):
        fut = self.new_future(self.loop)

        async eleza coro():
            await fut

        task = self.new_task(self.loop, coro())
        test_utils.run_briefly(self.loop)
        self.assertIs(task._fut_waiter, fut)

        task.cancel()
        test_utils.run_briefly(self.loop)
        self.assertRaises(
            asyncio.CancelledError, self.loop.run_until_complete, task)
        self.assertIsTupu(task._fut_waiter)
        self.assertKweli(fut.cancelled())

    eleza test_task_set_methods(self):
        async eleza notmuch():
            rudisha 'ko'

        gen = notmuch()
        task = self.new_task(self.loop, gen)

        ukijumuisha self.assertRaisesRegex(RuntimeError, 'sio support set_result'):
            task.set_result('ok')

        ukijumuisha self.assertRaisesRegex(RuntimeError, 'sio support set_exception'):
            task.set_exception(ValueError())

        self.assertEqual(
            self.loop.run_until_complete(task),
            'ko')

    eleza test_step_result(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza notmuch():
                tuma Tupu
                tuma 1
                rudisha 'ko'

        self.assertRaises(
            RuntimeError, self.loop.run_until_complete, notmuch())

    eleza test_step_result_future(self):
        # If coroutine returns future, task waits on this future.

        kundi Fut(asyncio.Future):
            eleza __init__(self, *args, **kwds):
                self.cb_added = Uongo
                super().__init__(*args, **kwds)

            eleza add_done_callback(self, *args, **kwargs):
                self.cb_added = Kweli
                super().add_done_callback(*args, **kwargs)

        fut = Fut(loop=self.loop)
        result = Tupu

        async eleza wait_for_future():
            nonlocal result
            result = await fut

        t = self.new_task(self.loop, wait_for_future())
        test_utils.run_briefly(self.loop)
        self.assertKweli(fut.cb_added)

        res = object()
        fut.set_result(res)
        test_utils.run_briefly(self.loop)
        self.assertIs(res, result)
        self.assertKweli(t.done())
        self.assertIsTupu(t.result())

    eleza test_baseexception_during_cancel(self):

        eleza gen():
            when = tuma
            self.assertAlmostEqual(10.0, when)
            tuma 0

        loop = self.new_test_loop(gen)

        async eleza sleeper():
            await asyncio.sleep(10)

        base_exc = SystemExit()

        async eleza notmutch():
            jaribu:
                await sleeper()
            tatizo asyncio.CancelledError:
                ashiria base_exc

        task = self.new_task(loop, notmutch())
        test_utils.run_briefly(loop)

        task.cancel()
        self.assertUongo(task.done())

        self.assertRaises(SystemExit, test_utils.run_briefly, loop)

        self.assertKweli(task.done())
        self.assertUongo(task.cancelled())
        self.assertIs(task.exception(), base_exc)

    eleza test_iscoroutinefunction(self):
        eleza fn():
            pita

        self.assertUongo(asyncio.iscoroutinefunction(fn))

        eleza fn1():
            tuma
        self.assertUongo(asyncio.iscoroutinefunction(fn1))

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza fn2():
                tuma
        self.assertKweli(asyncio.iscoroutinefunction(fn2))

        self.assertUongo(asyncio.iscoroutinefunction(mock.Mock()))

    eleza test_tuma_vs_tuma_from(self):
        fut = self.new_future(self.loop)

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza wait_for_future():
                tuma fut

        task = wait_for_future()
        ukijumuisha self.assertRaises(RuntimeError):
            self.loop.run_until_complete(task)

        self.assertUongo(fut.done())

    eleza test_tuma_vs_tuma_from_generator(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro():
                tuma

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza wait_for_future():
                gen = coro()
                jaribu:
                    tuma gen
                mwishowe:
                    gen.close()

        task = wait_for_future()
        self.assertRaises(
            RuntimeError,
            self.loop.run_until_complete, task)

    eleza test_coroutine_non_gen_function(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza func():
                rudisha 'test'

        self.assertKweli(asyncio.iscoroutinefunction(func))

        coro = func()
        self.assertKweli(asyncio.iscoroutine(coro))

        res = self.loop.run_until_complete(coro)
        self.assertEqual(res, 'test')

    eleza test_coroutine_non_gen_function_return_future(self):
        fut = self.new_future(self.loop)

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza func():
                rudisha fut

        async eleza coro():
            fut.set_result('test')

        t1 = self.new_task(self.loop, func())
        t2 = self.new_task(self.loop, coro())
        res = self.loop.run_until_complete(t1)
        self.assertEqual(res, 'test')
        self.assertIsTupu(t2.result())


    eleza test_current_task_deprecated(self):
        Task = self.__class__.Task

        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertIsTupu(Task.current_task(loop=self.loop))

        async eleza coro(loop):
            ukijumuisha self.assertWarns(DeprecationWarning):
                self.assertIs(Task.current_task(loop=loop), task)

            # See http://bugs.python.org/issue29271 kila details:
            asyncio.set_event_loop(loop)
            jaribu:
                ukijumuisha self.assertWarns(DeprecationWarning):
                    self.assertIs(Task.current_task(Tupu), task)
                ukijumuisha self.assertWarns(DeprecationWarning):
                    self.assertIs(Task.current_task(), task)
            mwishowe:
                asyncio.set_event_loop(Tupu)

        task = self.new_task(self.loop, coro(self.loop))
        self.loop.run_until_complete(task)
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertIsTupu(Task.current_task(loop=self.loop))

    eleza test_current_task(self):
        self.assertIsTupu(asyncio.current_task(loop=self.loop))

        async eleza coro(loop):
            self.assertIs(asyncio.current_task(loop=loop), task)

            self.assertIs(asyncio.current_task(Tupu), task)
            self.assertIs(asyncio.current_task(), task)

        task = self.new_task(self.loop, coro(self.loop))
        self.loop.run_until_complete(task)
        self.assertIsTupu(asyncio.current_task(loop=self.loop))

    eleza test_current_task_with_interleaving_tasks(self):
        self.assertIsTupu(asyncio.current_task(loop=self.loop))

        fut1 = self.new_future(self.loop)
        fut2 = self.new_future(self.loop)

        async eleza coro1(loop):
            self.assertKweli(asyncio.current_task(loop=loop) ni task1)
            await fut1
            self.assertKweli(asyncio.current_task(loop=loop) ni task1)
            fut2.set_result(Kweli)

        async eleza coro2(loop):
            self.assertKweli(asyncio.current_task(loop=loop) ni task2)
            fut1.set_result(Kweli)
            await fut2
            self.assertKweli(asyncio.current_task(loop=loop) ni task2)

        task1 = self.new_task(self.loop, coro1(self.loop))
        task2 = self.new_task(self.loop, coro2(self.loop))

        self.loop.run_until_complete(asyncio.wait((task1, task2)))
        self.assertIsTupu(asyncio.current_task(loop=self.loop))

    # Some thorough tests kila cancellation propagation through
    # coroutines, tasks na wait().

    eleza test_tuma_future_pitaes_cancel(self):
        # Cancelling outer() cancels inner() cancels waiter.
        proof = 0
        waiter = self.new_future(self.loop)

        async eleza inner():
            nonlocal proof
            jaribu:
                await waiter
            tatizo asyncio.CancelledError:
                proof += 1
                raise
            isipokua:
                self.fail('got past sleep() kwenye inner()')

        async eleza outer():
            nonlocal proof
            jaribu:
                await inner()
            tatizo asyncio.CancelledError:
                proof += 100  # Expect this path.
            isipokua:
                proof += 10

        f = asyncio.ensure_future(outer(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        f.cancel()
        self.loop.run_until_complete(f)
        self.assertEqual(proof, 101)
        self.assertKweli(waiter.cancelled())

    eleza test_tuma_wait_does_not_shield_cancel(self):
        # Cancelling outer() makes wait() rudisha early, leaves inner()
        # running.
        proof = 0
        waiter = self.new_future(self.loop)

        async eleza inner():
            nonlocal proof
            await waiter
            proof += 1

        async eleza outer():
            nonlocal proof
            d, p = await asyncio.wait([inner()])
            proof += 100

        f = asyncio.ensure_future(outer(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        f.cancel()
        self.assertRaises(
            asyncio.CancelledError, self.loop.run_until_complete, f)
        waiter.set_result(Tupu)
        test_utils.run_briefly(self.loop)
        self.assertEqual(proof, 1)

    eleza test_shield_result(self):
        inner = self.new_future(self.loop)
        outer = asyncio.shield(inner)
        inner.set_result(42)
        res = self.loop.run_until_complete(outer)
        self.assertEqual(res, 42)

    eleza test_shield_exception(self):
        inner = self.new_future(self.loop)
        outer = asyncio.shield(inner)
        test_utils.run_briefly(self.loop)
        exc = RuntimeError('expected')
        inner.set_exception(exc)
        test_utils.run_briefly(self.loop)
        self.assertIs(outer.exception(), exc)

    eleza test_shield_cancel_inner(self):
        inner = self.new_future(self.loop)
        outer = asyncio.shield(inner)
        test_utils.run_briefly(self.loop)
        inner.cancel()
        test_utils.run_briefly(self.loop)
        self.assertKweli(outer.cancelled())

    eleza test_shield_cancel_outer(self):
        inner = self.new_future(self.loop)
        outer = asyncio.shield(inner)
        test_utils.run_briefly(self.loop)
        outer.cancel()
        test_utils.run_briefly(self.loop)
        self.assertKweli(outer.cancelled())
        self.assertEqual(0, 0 ikiwa outer._callbacks ni Tupu isipokua len(outer._callbacks))

    eleza test_shield_shortcut(self):
        fut = self.new_future(self.loop)
        fut.set_result(42)
        res = self.loop.run_until_complete(asyncio.shield(fut))
        self.assertEqual(res, 42)

    eleza test_shield_effect(self):
        # Cancelling outer() does sio affect inner().
        proof = 0
        waiter = self.new_future(self.loop)

        async eleza inner():
            nonlocal proof
            await waiter
            proof += 1

        async eleza outer():
            nonlocal proof
            await asyncio.shield(inner())
            proof += 100

        f = asyncio.ensure_future(outer(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        f.cancel()
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(f)
        waiter.set_result(Tupu)
        test_utils.run_briefly(self.loop)
        self.assertEqual(proof, 1)

    eleza test_shield_gather(self):
        child1 = self.new_future(self.loop)
        child2 = self.new_future(self.loop)
        parent = asyncio.gather(child1, child2)
        outer = asyncio.shield(parent)
        test_utils.run_briefly(self.loop)
        outer.cancel()
        test_utils.run_briefly(self.loop)
        self.assertKweli(outer.cancelled())
        child1.set_result(1)
        child2.set_result(2)
        test_utils.run_briefly(self.loop)
        self.assertEqual(parent.result(), [1, 2])

    eleza test_gather_shield(self):
        child1 = self.new_future(self.loop)
        child2 = self.new_future(self.loop)
        inner1 = asyncio.shield(child1)
        inner2 = asyncio.shield(child2)
        parent = asyncio.gather(inner1, inner2)
        test_utils.run_briefly(self.loop)
        parent.cancel()
        # This should cancel inner1 na inner2 but bot child1 na child2.
        test_utils.run_briefly(self.loop)
        self.assertIsInstance(parent.exception(), asyncio.CancelledError)
        self.assertKweli(inner1.cancelled())
        self.assertKweli(inner2.cancelled())
        child1.set_result(1)
        child2.set_result(2)
        test_utils.run_briefly(self.loop)

    eleza test_as_completed_invalid_args(self):
        fut = self.new_future(self.loop)

        # as_completed() expects a list of futures, sio a future instance
        self.assertRaises(TypeError, self.loop.run_until_complete,
            asyncio.as_completed(fut, loop=self.loop))
        coro = coroutine_function()
        self.assertRaises(TypeError, self.loop.run_until_complete,
            asyncio.as_completed(coro, loop=self.loop))
        coro.close()

    eleza test_wait_invalid_args(self):
        fut = self.new_future(self.loop)

        # wait() expects a list of futures, sio a future instance
        self.assertRaises(TypeError, self.loop.run_until_complete,
            asyncio.wait(fut))
        coro = coroutine_function()
        self.assertRaises(TypeError, self.loop.run_until_complete,
            asyncio.wait(coro))
        coro.close()

        # wait() expects at least a future
        self.assertRaises(ValueError, self.loop.run_until_complete,
            asyncio.wait([]))

    eleza test_corowrapper_mocks_generator(self):

        eleza check():
            # A function that asserts various things.
            # Called twice, ukijumuisha different debug flag values.

            ukijumuisha self.assertWarns(DeprecationWarning):
                @asyncio.coroutine
                eleza coro():
                    # The actual coroutine.
                    self.assertKweli(gen.gi_running)
                    tuma kutoka fut

            # A completed Future used to run the coroutine.
            fut = self.new_future(self.loop)
            fut.set_result(Tupu)

            # Call the coroutine.
            gen = coro()

            # Check some properties.
            self.assertKweli(asyncio.iscoroutine(gen))
            self.assertIsInstance(gen.gi_frame, types.FrameType)
            self.assertUongo(gen.gi_running)
            self.assertIsInstance(gen.gi_code, types.CodeType)

            # Run it.
            self.loop.run_until_complete(gen)

            # The frame should have changed.
            self.assertIsTupu(gen.gi_frame)

        # Test ukijumuisha debug flag cleared.
        ukijumuisha set_coroutine_debug(Uongo):
            check()

        # Test ukijumuisha debug flag set.
        ukijumuisha set_coroutine_debug(Kweli):
            check()

    eleza test_tuma_from_corowrapper(self):
        ukijumuisha set_coroutine_debug(Kweli):
            ukijumuisha self.assertWarns(DeprecationWarning):
                @asyncio.coroutine
                eleza t1():
                    rudisha (tuma kutoka t2())

            ukijumuisha self.assertWarns(DeprecationWarning):
                @asyncio.coroutine
                eleza t2():
                    f = self.new_future(self.loop)
                    self.new_task(self.loop, t3(f))
                    rudisha (tuma kutoka f)

            ukijumuisha self.assertWarns(DeprecationWarning):
                @asyncio.coroutine
                eleza t3(f):
                    f.set_result((1, 2, 3))

            task = self.new_task(self.loop, t1())
            val = self.loop.run_until_complete(task)
            self.assertEqual(val, (1, 2, 3))

    eleza test_tuma_from_corowrapper_send(self):
        eleza foo():
            a = tuma
            rudisha a

        eleza call(arg):
            cw = asyncio.coroutines.CoroWrapper(foo())
            cw.send(Tupu)
            jaribu:
                cw.send(arg)
            tatizo StopIteration kama ex:
                rudisha ex.args[0]
            isipokua:
                ashiria AssertionError('StopIteration was expected')

        self.assertEqual(call((1, 2)), (1, 2))
        self.assertEqual(call('spam'), 'spam')

    eleza test_corowrapper_weakref(self):
        wd = weakref.WeakValueDictionary()
        eleza foo(): tuma kutoka []
        cw = asyncio.coroutines.CoroWrapper(foo())
        wd['cw'] = cw  # Would fail without __weakref__ slot.
        cw.gen = Tupu  # Suppress warning kutoka __del__.

    eleza test_corowrapper_throw(self):
        # Issue 429: CoroWrapper.throw must be compatible ukijumuisha gen.throw
        eleza foo():
            value = Tupu
            wakati Kweli:
                jaribu:
                    value = tuma value
                tatizo Exception kama e:
                    value = e

        exception = Exception("foo")
        cw = asyncio.coroutines.CoroWrapper(foo())
        cw.send(Tupu)
        self.assertIs(exception, cw.throw(exception))

        cw = asyncio.coroutines.CoroWrapper(foo())
        cw.send(Tupu)
        self.assertIs(exception, cw.throw(Exception, exception))

        cw = asyncio.coroutines.CoroWrapper(foo())
        cw.send(Tupu)
        exception = cw.throw(Exception, "foo")
        self.assertIsInstance(exception, Exception)
        self.assertEqual(exception.args, ("foo", ))

        cw = asyncio.coroutines.CoroWrapper(foo())
        cw.send(Tupu)
        exception = cw.throw(Exception, "foo", Tupu)
        self.assertIsInstance(exception, Exception)
        self.assertEqual(exception.args, ("foo", ))

    eleza test_all_tasks_deprecated(self):
        Task = self.__class__.Task

        async eleza coro():
            ukijumuisha self.assertWarns(DeprecationWarning):
                assert Task.all_tasks(self.loop) == {t}

        t = self.new_task(self.loop, coro())
        self.loop.run_until_complete(t)

    eleza test_log_destroyed_pending_task(self):
        Task = self.__class__.Task

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza kill_me(loop):
                future = self.new_future(loop)
                tuma kutoka future
                # at this point, the only reference to kill_me() task is
                # the Task._wakeup() method kwenye future._callbacks
                ashiria Exception("code never reached")

        mock_handler = mock.Mock()
        self.loop.set_debug(Kweli)
        self.loop.set_exception_handler(mock_handler)

        # schedule the task
        coro = kill_me(self.loop)
        task = asyncio.ensure_future(coro, loop=self.loop)

        self.assertEqual(asyncio.all_tasks(loop=self.loop), {task})

        # See http://bugs.python.org/issue29271 kila details:
        asyncio.set_event_loop(self.loop)
        jaribu:
            ukijumuisha self.assertWarns(DeprecationWarning):
                self.assertEqual(Task.all_tasks(), {task})
            ukijumuisha self.assertWarns(DeprecationWarning):
                self.assertEqual(Task.all_tasks(Tupu), {task})
        mwishowe:
            asyncio.set_event_loop(Tupu)

        # execute the task so it waits kila future
        self.loop._run_once()
        self.assertEqual(len(self.loop._ready), 0)

        # remove the future used kwenye kill_me(), na references to the task
        toa coro.gi_frame.f_locals['future']
        coro = Tupu
        source_traceback = task._source_traceback
        task = Tupu

        # no more reference to kill_me() task: the task ni destroyed by the GC
        support.gc_collect()

        self.assertEqual(asyncio.all_tasks(loop=self.loop), set())

        mock_handler.assert_called_with(self.loop, {
            'message': 'Task was destroyed but it ni pending!',
            'task': mock.ANY,
            'source_traceback': source_traceback,
        })
        mock_handler.reset_mock()

    @mock.patch('asyncio.base_events.logger')
    eleza test_tb_logger_not_called_after_cancel(self, m_log):
        loop = asyncio.new_event_loop()
        self.set_event_loop(loop)

        async eleza coro():
            ashiria TypeError

        async eleza runner():
            task = self.new_task(loop, coro())
            await asyncio.sleep(0.05)
            task.cancel()
            task = Tupu

        loop.run_until_complete(runner())
        self.assertUongo(m_log.error.called)

    @mock.patch('asyncio.coroutines.logger')
    eleza test_coroutine_never_tumaed(self, m_log):
        ukijumuisha set_coroutine_debug(Kweli):
            ukijumuisha self.assertWarns(DeprecationWarning):
                @asyncio.coroutine
                eleza coro_noop():
                    pita

        tb_filename = __file__
        tb_lineno = sys._getframe().f_lineno + 2
        # create a coroutine object but don't use it
        coro_noop()
        support.gc_collect()

        self.assertKweli(m_log.error.called)
        message = m_log.error.call_args[0][0]
        func_filename, func_lineno = test_utils.get_function_source(coro_noop)

        regex = (r'^<CoroWrapper %s\(?\)? .* at %s:%s, .*> '
                    r'was never tumaed from\n'
                 r'Coroutine object created at \(most recent call last, truncated to \d+ last lines\):\n'
                 r'.*\n'
                 r'  File "%s", line %s, kwenye test_coroutine_never_tumaed\n'
                 r'    coro_noop\(\)$'
                 % (re.escape(coro_noop.__qualname__),
                    re.escape(func_filename), func_lineno,
                    re.escape(tb_filename), tb_lineno))

        self.assertRegex(message, re.compile(regex, re.DOTALL))

    eleza test_return_coroutine_from_coroutine(self):
        """Return of @asyncio.coroutine()-wrapped function generator object
        kutoka @asyncio.coroutine()-wrapped function should have same effect as
        returning generator object ama Future."""
        eleza check():
            ukijumuisha self.assertWarns(DeprecationWarning):
                @asyncio.coroutine
                eleza outer_coro():
                    ukijumuisha self.assertWarns(DeprecationWarning):
                        @asyncio.coroutine
                        eleza inner_coro():
                            rudisha 1

                    rudisha inner_coro()

            result = self.loop.run_until_complete(outer_coro())
            self.assertEqual(result, 1)

        # Test ukijumuisha debug flag cleared.
        ukijumuisha set_coroutine_debug(Uongo):
            check()

        # Test ukijumuisha debug flag set.
        ukijumuisha set_coroutine_debug(Kweli):
            check()

    eleza test_task_source_traceback(self):
        self.loop.set_debug(Kweli)

        task = self.new_task(self.loop, coroutine_function())
        lineno = sys._getframe().f_lineno - 1
        self.assertIsInstance(task._source_traceback, list)
        self.assertEqual(task._source_traceback[-2][:3],
                         (__file__,
                          lineno,
                          'test_task_source_traceback'))
        self.loop.run_until_complete(task)

    eleza _test_cancel_wait_for(self, timeout):
        loop = asyncio.new_event_loop()
        self.addCleanup(loop.close)

        async eleza blocking_coroutine():
            fut = self.new_future(loop)
            # Block: fut result ni never set
            await fut

        task = loop.create_task(blocking_coroutine())

        wait = loop.create_task(asyncio.wait_for(task, timeout))
        loop.call_soon(wait.cancel)

        self.assertRaises(asyncio.CancelledError,
                          loop.run_until_complete, wait)

        # Python issue #23219: cancelling the wait must also cancel the task
        self.assertKweli(task.cancelled())

    eleza test_cancel_blocking_wait_for(self):
        self._test_cancel_wait_for(Tupu)

    eleza test_cancel_wait_for(self):
        self._test_cancel_wait_for(60.0)

    eleza test_cancel_gather_1(self):
        """Ensure that a gathering future refuses to be cancelled once all
        children are done"""
        loop = asyncio.new_event_loop()
        self.addCleanup(loop.close)

        fut = self.new_future(loop)
        # The indirection fut->child_coro ni needed since otherwise the
        # gathering task ni done at the same time kama the child future
        eleza child_coro():
            rudisha (tuma kutoka fut)
        gather_future = asyncio.gather(child_coro(), loop=loop)
        gather_task = asyncio.ensure_future(gather_future, loop=loop)

        cancel_result = Tupu
        eleza cancelling_callback(_):
            nonlocal cancel_result
            cancel_result = gather_task.cancel()
        fut.add_done_callback(cancelling_callback)

        fut.set_result(42) # calls the cancelling_callback after fut ni done()

        # At this point the task should complete.
        loop.run_until_complete(gather_task)

        # Python issue #26923: asyncio.gather drops cancellation
        self.assertEqual(cancel_result, Uongo)
        self.assertUongo(gather_task.cancelled())
        self.assertEqual(gather_task.result(), [42])

    eleza test_cancel_gather_2(self):
        loop = asyncio.new_event_loop()
        self.addCleanup(loop.close)

        async eleza test():
            time = 0
            wakati Kweli:
                time += 0.05
                await asyncio.gather(asyncio.sleep(0.05),
                                     return_exceptions=Kweli,
                                     loop=loop)
                ikiwa time > 1:
                    rudisha

        async eleza main():
            qwe = self.new_task(loop, test())
            await asyncio.sleep(0.2)
            qwe.cancel()
            jaribu:
                await qwe
            tatizo asyncio.CancelledError:
                pita
            isipokua:
                self.fail('gather did sio propagate the cancellation request')

        loop.run_until_complete(main())

    eleza test_exception_traceback(self):
        # See http://bugs.python.org/issue28843

        async eleza foo():
            1 / 0

        async eleza main():
            task = self.new_task(self.loop, foo())
            await asyncio.sleep(0)  # skip one loop iteration
            self.assertIsNotTupu(task.exception().__traceback__)

        self.loop.run_until_complete(main())

    @mock.patch('asyncio.base_events.logger')
    eleza test_error_in_call_soon(self, m_log):
        eleza call_soon(callback, *args, **kwargs):
            ashiria ValueError
        self.loop.call_soon = call_soon

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro():
                pita

        self.assertUongo(m_log.error.called)

        ukijumuisha self.assertRaises(ValueError):
            gen = coro()
            jaribu:
                self.new_task(self.loop, gen)
            mwishowe:
                gen.close()

        self.assertKweli(m_log.error.called)
        message = m_log.error.call_args[0][0]
        self.assertIn('Task was destroyed but it ni pending', message)

        self.assertEqual(asyncio.all_tasks(self.loop), set())

    eleza test_create_task_with_noncoroutine(self):
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    "a coroutine was expected, got 123"):
            self.new_task(self.loop, 123)

        # test it kila the second time to ensure that caching
        # kwenye asyncio.iscoroutine() doesn't koma things.
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    "a coroutine was expected, got 123"):
            self.new_task(self.loop, 123)

    eleza test_create_task_with_oldstyle_coroutine(self):

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro():
                pita

        task = self.new_task(self.loop, coro())
        self.assertIsInstance(task, self.Task)
        self.loop.run_until_complete(task)

        # test it kila the second time to ensure that caching
        # kwenye asyncio.iscoroutine() doesn't koma things.
        task = self.new_task(self.loop, coro())
        self.assertIsInstance(task, self.Task)
        self.loop.run_until_complete(task)

    eleza test_create_task_with_async_function(self):

        async eleza coro():
            pita

        task = self.new_task(self.loop, coro())
        self.assertIsInstance(task, self.Task)
        self.loop.run_until_complete(task)

        # test it kila the second time to ensure that caching
        # kwenye asyncio.iscoroutine() doesn't koma things.
        task = self.new_task(self.loop, coro())
        self.assertIsInstance(task, self.Task)
        self.loop.run_until_complete(task)

    eleza test_create_task_with_asynclike_function(self):
        task = self.new_task(self.loop, CoroLikeObject())
        self.assertIsInstance(task, self.Task)
        self.assertEqual(self.loop.run_until_complete(task), 42)

        # test it kila the second time to ensure that caching
        # kwenye asyncio.iscoroutine() doesn't koma things.
        task = self.new_task(self.loop, CoroLikeObject())
        self.assertIsInstance(task, self.Task)
        self.assertEqual(self.loop.run_until_complete(task), 42)

    eleza test_bare_create_task(self):

        async eleza inner():
            rudisha 1

        async eleza coro():
            task = asyncio.create_task(inner())
            self.assertIsInstance(task, self.Task)
            ret = await task
            self.assertEqual(1, ret)

        self.loop.run_until_complete(coro())

    eleza test_bare_create_named_task(self):

        async eleza coro_noop():
            pita

        async eleza coro():
            task = asyncio.create_task(coro_noop(), name='No-op')
            self.assertEqual(task.get_name(), 'No-op')
            await task

        self.loop.run_until_complete(coro())

    eleza test_context_1(self):
        cvar = contextvars.ContextVar('cvar', default='nope')

        async eleza sub():
            await asyncio.sleep(0.01)
            self.assertEqual(cvar.get(), 'nope')
            cvar.set('something else')

        async eleza main():
            self.assertEqual(cvar.get(), 'nope')
            subtask = self.new_task(loop, sub())
            cvar.set('yes')
            self.assertEqual(cvar.get(), 'yes')
            await subtask
            self.assertEqual(cvar.get(), 'yes')

        loop = asyncio.new_event_loop()
        jaribu:
            task = self.new_task(loop, main())
            loop.run_until_complete(task)
        mwishowe:
            loop.close()

    eleza test_context_2(self):
        cvar = contextvars.ContextVar('cvar', default='nope')

        async eleza main():
            eleza fut_on_done(fut):
                # This change must sio pollute the context
                # of the "main()" task.
                cvar.set('something else')

            self.assertEqual(cvar.get(), 'nope')

            kila j kwenye range(2):
                fut = self.new_future(loop)
                fut.add_done_callback(fut_on_done)
                cvar.set(f'yes{j}')
                loop.call_soon(fut.set_result, Tupu)
                await fut
                self.assertEqual(cvar.get(), f'yes{j}')

                kila i kwenye range(3):
                    # Test that task pitaed its context to add_done_callback:
                    cvar.set(f'yes{i}-{j}')
                    await asyncio.sleep(0.001)
                    self.assertEqual(cvar.get(), f'yes{i}-{j}')

        loop = asyncio.new_event_loop()
        jaribu:
            task = self.new_task(loop, main())
            loop.run_until_complete(task)
        mwishowe:
            loop.close()

        self.assertEqual(cvar.get(), 'nope')

    eleza test_context_3(self):
        # Run 100 Tasks kwenye parallel, each modifying cvar.

        cvar = contextvars.ContextVar('cvar', default=-1)

        async eleza sub(num):
            kila i kwenye range(10):
                cvar.set(num + i)
                await asyncio.sleep(random.uniform(0.001, 0.05))
                self.assertEqual(cvar.get(), num + i)

        async eleza main():
            tasks = []
            kila i kwenye range(100):
                task = loop.create_task(sub(random.randint(0, 10)))
                tasks.append(task)

            await asyncio.gather(*tasks, loop=loop)

        loop = asyncio.new_event_loop()
        jaribu:
            loop.run_until_complete(main())
        mwishowe:
            loop.close()

        self.assertEqual(cvar.get(), -1)

    eleza test_get_coro(self):
        loop = asyncio.new_event_loop()
        coro = coroutine_function()
        jaribu:
            task = self.new_task(loop, coro)
            loop.run_until_complete(task)
            self.assertIs(task.get_coro(), coro)
        mwishowe:
            loop.close()


eleza add_subclass_tests(cls):
    BaseTask = cls.Task
    BaseFuture = cls.Future

    ikiwa BaseTask ni Tupu ama BaseFuture ni Tupu:
        rudisha cls

    kundi CommonFuture:
        eleza __init__(self, *args, **kwargs):
            self.calls = collections.defaultdict(lambda: 0)
            super().__init__(*args, **kwargs)

        eleza add_done_callback(self, *args, **kwargs):
            self.calls['add_done_callback'] += 1
            rudisha super().add_done_callback(*args, **kwargs)

    kundi Task(CommonFuture, BaseTask):
        pita

    kundi Future(CommonFuture, BaseFuture):
        pita

    eleza test_subclasses_ctask_cfuture(self):
        fut = self.Future(loop=self.loop)

        async eleza func():
            self.loop.call_soon(lambda: fut.set_result('spam'))
            rudisha await fut

        task = self.Task(func(), loop=self.loop)

        result = self.loop.run_until_complete(task)

        self.assertEqual(result, 'spam')

        self.assertEqual(
            dict(task.calls),
            {'add_done_callback': 1})

        self.assertEqual(
            dict(fut.calls),
            {'add_done_callback': 1})

    # Add patched Task & Future back to the test case
    cls.Task = Task
    cls.Future = Future

    # Add an extra unit-test
    cls.test_subclasses_ctask_cfuture = test_subclasses_ctask_cfuture

    # Disable the "test_task_source_traceback" test
    # (the test ni hardcoded kila a particular call stack, which
    # ni slightly different kila Task subclasses)
    cls.test_task_source_traceback = Tupu

    rudisha cls


kundi SetMethodsTest:

    eleza test_set_result_causes_invalid_state(self):
        Future = type(self).Future
        self.loop.call_exception_handler = exc_handler = mock.Mock()

        async eleza foo():
            await asyncio.sleep(0.1)
            rudisha 10

        coro = foo()
        task = self.new_task(self.loop, coro)
        Future.set_result(task, 'spam')

        self.assertEqual(
            self.loop.run_until_complete(task),
            'spam')

        exc_handler.assert_called_once()
        exc = exc_handler.call_args[0][0]['exception']
        ukijumuisha self.assertRaisesRegex(asyncio.InvalidStateError,
                                    r'step\(\): already done'):
            ashiria exc

        coro.close()

    eleza test_set_exception_causes_invalid_state(self):
        kundi MyExc(Exception):
            pita

        Future = type(self).Future
        self.loop.call_exception_handler = exc_handler = mock.Mock()

        async eleza foo():
            await asyncio.sleep(0.1)
            rudisha 10

        coro = foo()
        task = self.new_task(self.loop, coro)
        Future.set_exception(task, MyExc())

        ukijumuisha self.assertRaises(MyExc):
            self.loop.run_until_complete(task)

        exc_handler.assert_called_once()
        exc = exc_handler.call_args[0][0]['exception']
        ukijumuisha self.assertRaisesRegex(asyncio.InvalidStateError,
                                    r'step\(\): already done'):
            ashiria exc

        coro.close()


@unittest.skipUnless(hasattr(futures, '_CFuture') na
                     hasattr(tasks, '_CTask'),
                     'requires the C _asyncio module')
kundi CTask_CFuture_Tests(BaseTaskTests, SetMethodsTest,
                          test_utils.TestCase):

    Task = getattr(tasks, '_CTask', Tupu)
    Future = getattr(futures, '_CFuture', Tupu)

    @support.refcount_test
    eleza test_refleaks_in_task___init__(self):
        gettotalrefcount = support.get_attribute(sys, 'gettotalrefcount')
        async eleza coro():
            pita
        task = self.new_task(self.loop, coro())
        self.loop.run_until_complete(task)
        refs_before = gettotalrefcount()
        kila i kwenye range(100):
            task.__init__(coro(), loop=self.loop)
            self.loop.run_until_complete(task)
        self.assertAlmostEqual(gettotalrefcount() - refs_before, 0, delta=10)

    eleza test_del__log_destroy_pending_segfault(self):
        async eleza coro():
            pita
        task = self.new_task(self.loop, coro())
        self.loop.run_until_complete(task)
        ukijumuisha self.assertRaises(AttributeError):
            toa task._log_destroy_pending


@unittest.skipUnless(hasattr(futures, '_CFuture') na
                     hasattr(tasks, '_CTask'),
                     'requires the C _asyncio module')
@add_subclass_tests
kundi CTask_CFuture_SubclassTests(BaseTaskTests, test_utils.TestCase):

    Task = getattr(tasks, '_CTask', Tupu)
    Future = getattr(futures, '_CFuture', Tupu)


@unittest.skipUnless(hasattr(tasks, '_CTask'),
                     'requires the C _asyncio module')
@add_subclass_tests
kundi CTaskSubclass_PyFuture_Tests(BaseTaskTests, test_utils.TestCase):

    Task = getattr(tasks, '_CTask', Tupu)
    Future = futures._PyFuture


@unittest.skipUnless(hasattr(futures, '_CFuture'),
                     'requires the C _asyncio module')
@add_subclass_tests
kundi PyTask_CFutureSubclass_Tests(BaseTaskTests, test_utils.TestCase):

    Future = getattr(futures, '_CFuture', Tupu)
    Task = tasks._PyTask


@unittest.skipUnless(hasattr(tasks, '_CTask'),
                     'requires the C _asyncio module')
kundi CTask_PyFuture_Tests(BaseTaskTests, test_utils.TestCase):

    Task = getattr(tasks, '_CTask', Tupu)
    Future = futures._PyFuture


@unittest.skipUnless(hasattr(futures, '_CFuture'),
                     'requires the C _asyncio module')
kundi PyTask_CFuture_Tests(BaseTaskTests, test_utils.TestCase):

    Task = tasks._PyTask
    Future = getattr(futures, '_CFuture', Tupu)


kundi PyTask_PyFuture_Tests(BaseTaskTests, SetMethodsTest,
                            test_utils.TestCase):

    Task = tasks._PyTask
    Future = futures._PyFuture


@add_subclass_tests
kundi PyTask_PyFuture_SubclassTests(BaseTaskTests, test_utils.TestCase):
    Task = tasks._PyTask
    Future = futures._PyFuture


@unittest.skipUnless(hasattr(tasks, '_CTask'),
                     'requires the C _asyncio module')
kundi CTask_Future_Tests(test_utils.TestCase):

    eleza test_foobar(self):
        kundi Fut(asyncio.Future):
            @property
            eleza get_loop(self):
                ashiria AttributeError

        async eleza coro():
            await fut
            rudisha 'spam'

        self.loop = asyncio.new_event_loop()
        jaribu:
            fut = Fut(loop=self.loop)
            self.loop.call_later(0.1, fut.set_result, 1)
            task = self.loop.create_task(coro())
            res = self.loop.run_until_complete(task)
        mwishowe:
            self.loop.close()

        self.assertEqual(res, 'spam')


kundi BaseTaskIntrospectionTests:
    _register_task = Tupu
    _unregister_task = Tupu
    _enter_task = Tupu
    _leave_task = Tupu

    eleza test__register_task_1(self):
        kundi TaskLike:
            @property
            eleza _loop(self):
                rudisha loop

            eleza done(self):
                rudisha Uongo

        task = TaskLike()
        loop = mock.Mock()

        self.assertEqual(asyncio.all_tasks(loop), set())
        self._register_task(task)
        self.assertEqual(asyncio.all_tasks(loop), {task})
        self._unregister_task(task)

    eleza test__register_task_2(self):
        kundi TaskLike:
            eleza get_loop(self):
                rudisha loop

            eleza done(self):
                rudisha Uongo

        task = TaskLike()
        loop = mock.Mock()

        self.assertEqual(asyncio.all_tasks(loop), set())
        self._register_task(task)
        self.assertEqual(asyncio.all_tasks(loop), {task})
        self._unregister_task(task)

    eleza test__register_task_3(self):
        kundi TaskLike:
            eleza get_loop(self):
                rudisha loop

            eleza done(self):
                rudisha Kweli

        task = TaskLike()
        loop = mock.Mock()

        self.assertEqual(asyncio.all_tasks(loop), set())
        self._register_task(task)
        self.assertEqual(asyncio.all_tasks(loop), set())
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.assertEqual(asyncio.Task.all_tasks(loop), {task})
        self._unregister_task(task)

    eleza test__enter_task(self):
        task = mock.Mock()
        loop = mock.Mock()
        self.assertIsTupu(asyncio.current_task(loop))
        self._enter_task(loop, task)
        self.assertIs(asyncio.current_task(loop), task)
        self._leave_task(loop, task)

    eleza test__enter_task_failure(self):
        task1 = mock.Mock()
        task2 = mock.Mock()
        loop = mock.Mock()
        self._enter_task(loop, task1)
        ukijumuisha self.assertRaises(RuntimeError):
            self._enter_task(loop, task2)
        self.assertIs(asyncio.current_task(loop), task1)
        self._leave_task(loop, task1)

    eleza test__leave_task(self):
        task = mock.Mock()
        loop = mock.Mock()
        self._enter_task(loop, task)
        self._leave_task(loop, task)
        self.assertIsTupu(asyncio.current_task(loop))

    eleza test__leave_task_failure1(self):
        task1 = mock.Mock()
        task2 = mock.Mock()
        loop = mock.Mock()
        self._enter_task(loop, task1)
        ukijumuisha self.assertRaises(RuntimeError):
            self._leave_task(loop, task2)
        self.assertIs(asyncio.current_task(loop), task1)
        self._leave_task(loop, task1)

    eleza test__leave_task_failure2(self):
        task = mock.Mock()
        loop = mock.Mock()
        ukijumuisha self.assertRaises(RuntimeError):
            self._leave_task(loop, task)
        self.assertIsTupu(asyncio.current_task(loop))

    eleza test__unregister_task(self):
        task = mock.Mock()
        loop = mock.Mock()
        task.get_loop = lambda: loop
        self._register_task(task)
        self._unregister_task(task)
        self.assertEqual(asyncio.all_tasks(loop), set())

    eleza test__unregister_task_not_registered(self):
        task = mock.Mock()
        loop = mock.Mock()
        self._unregister_task(task)
        self.assertEqual(asyncio.all_tasks(loop), set())


kundi PyIntrospectionTests(test_utils.TestCase, BaseTaskIntrospectionTests):
    _register_task = staticmethod(tasks._py_register_task)
    _unregister_task = staticmethod(tasks._py_unregister_task)
    _enter_task = staticmethod(tasks._py_enter_task)
    _leave_task = staticmethod(tasks._py_leave_task)


@unittest.skipUnless(hasattr(tasks, '_c_register_task'),
                     'requires the C _asyncio module')
kundi CIntrospectionTests(test_utils.TestCase, BaseTaskIntrospectionTests):
    ikiwa hasattr(tasks, '_c_register_task'):
        _register_task = staticmethod(tasks._c_register_task)
        _unregister_task = staticmethod(tasks._c_unregister_task)
        _enter_task = staticmethod(tasks._c_enter_task)
        _leave_task = staticmethod(tasks._c_leave_task)
    isipokua:
        _register_task = _unregister_task = _enter_task = _leave_task = Tupu


kundi BaseCurrentLoopTests:

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    eleza new_task(self, coro):
        ashiria NotImplementedError

    eleza test_current_task_no_running_loop(self):
        self.assertIsTupu(asyncio.current_task(loop=self.loop))

    eleza test_current_task_no_running_loop_implicit(self):
        ukijumuisha self.assertRaises(RuntimeError):
            asyncio.current_task()

    eleza test_current_task_with_implicit_loop(self):
        async eleza coro():
            self.assertIs(asyncio.current_task(loop=self.loop), task)

            self.assertIs(asyncio.current_task(Tupu), task)
            self.assertIs(asyncio.current_task(), task)

        task = self.new_task(coro())
        self.loop.run_until_complete(task)
        self.assertIsTupu(asyncio.current_task(loop=self.loop))


kundi PyCurrentLoopTests(BaseCurrentLoopTests, test_utils.TestCase):

    eleza new_task(self, coro):
        rudisha tasks._PyTask(coro, loop=self.loop)


@unittest.skipUnless(hasattr(tasks, '_CTask'),
                     'requires the C _asyncio module')
kundi CCurrentLoopTests(BaseCurrentLoopTests, test_utils.TestCase):

    eleza new_task(self, coro):
        rudisha getattr(tasks, '_CTask')(coro, loop=self.loop)


kundi GenericTaskTests(test_utils.TestCase):

    eleza test_future_subclass(self):
        self.assertKweli(issubclass(asyncio.Task, asyncio.Future))

    eleza test_asyncio_module_compiled(self):
        # Because of circular imports it's easy to make _asyncio
        # module non-importable.  This ni a simple test that will
        # fail on systems where C modules were successfully compiled
        # (hence the test kila _functools), but _asyncio somehow didn't.
        jaribu:
            agiza _functools
        tatizo ImportError:
            pita
        isipokua:
            jaribu:
                agiza _asyncio
            tatizo ImportError:
                self.fail('_asyncio module ni missing')


kundi GatherTestsBase:

    eleza setUp(self):
        super().setUp()
        self.one_loop = self.new_test_loop()
        self.other_loop = self.new_test_loop()
        self.set_event_loop(self.one_loop, cleanup=Uongo)

    eleza _run_loop(self, loop):
        wakati loop._ready:
            test_utils.run_briefly(loop)

    eleza _check_success(self, **kwargs):
        a, b, c = [self.one_loop.create_future() kila i kwenye range(3)]
        fut = asyncio.gather(*self.wrap_futures(a, b, c), **kwargs)
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        b.set_result(1)
        a.set_result(2)
        self._run_loop(self.one_loop)
        self.assertEqual(cb.called, Uongo)
        self.assertUongo(fut.done())
        c.set_result(3)
        self._run_loop(self.one_loop)
        cb.assert_called_once_with(fut)
        self.assertEqual(fut.result(), [2, 1, 3])

    eleza test_success(self):
        self._check_success()
        self._check_success(return_exceptions=Uongo)

    eleza test_result_exception_success(self):
        self._check_success(return_exceptions=Kweli)

    eleza test_one_exception(self):
        a, b, c, d, e = [self.one_loop.create_future() kila i kwenye range(5)]
        fut = asyncio.gather(*self.wrap_futures(a, b, c, d, e))
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        exc = ZeroDivisionError()
        a.set_result(1)
        b.set_exception(exc)
        self._run_loop(self.one_loop)
        self.assertKweli(fut.done())
        cb.assert_called_once_with(fut)
        self.assertIs(fut.exception(), exc)
        # Does nothing
        c.set_result(3)
        d.cancel()
        e.set_exception(RuntimeError())
        e.exception()

    eleza test_return_exceptions(self):
        a, b, c, d = [self.one_loop.create_future() kila i kwenye range(4)]
        fut = asyncio.gather(*self.wrap_futures(a, b, c, d),
                             return_exceptions=Kweli)
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        exc = ZeroDivisionError()
        exc2 = RuntimeError()
        b.set_result(1)
        c.set_exception(exc)
        a.set_result(3)
        self._run_loop(self.one_loop)
        self.assertUongo(fut.done())
        d.set_exception(exc2)
        self._run_loop(self.one_loop)
        self.assertKweli(fut.done())
        cb.assert_called_once_with(fut)
        self.assertEqual(fut.result(), [3, 1, exc, exc2])

    eleza test_env_var_debug(self):
        code = '\n'.join((
            'agiza asyncio.coroutines',
            'andika(asyncio.coroutines._DEBUG)'))

        # Test ukijumuisha -E to sio fail ikiwa the unit test was run with
        # PYTHONASYNCIODEBUG set to a non-empty string
        sts, stdout, stderr = assert_python_ok('-E', '-c', code)
        self.assertEqual(stdout.rstrip(), b'Uongo')

        sts, stdout, stderr = assert_python_ok('-c', code,
                                               PYTHONASYNCIODEBUG='',
                                               PYTHONDEVMODE='')
        self.assertEqual(stdout.rstrip(), b'Uongo')

        sts, stdout, stderr = assert_python_ok('-c', code,
                                               PYTHONASYNCIODEBUG='1',
                                               PYTHONDEVMODE='')
        self.assertEqual(stdout.rstrip(), b'Kweli')

        sts, stdout, stderr = assert_python_ok('-E', '-c', code,
                                               PYTHONASYNCIODEBUG='1',
                                               PYTHONDEVMODE='')
        self.assertEqual(stdout.rstrip(), b'Uongo')

        # -X dev
        sts, stdout, stderr = assert_python_ok('-E', '-X', 'dev',
                                               '-c', code)
        self.assertEqual(stdout.rstrip(), b'Kweli')


kundi FutureGatherTests(GatherTestsBase, test_utils.TestCase):

    eleza wrap_futures(self, *futures):
        rudisha futures

    eleza _check_empty_sequence(self, seq_or_iter):
        asyncio.set_event_loop(self.one_loop)
        self.addCleanup(asyncio.set_event_loop, Tupu)
        fut = asyncio.gather(*seq_or_iter)
        self.assertIsInstance(fut, asyncio.Future)
        self.assertIs(fut._loop, self.one_loop)
        self._run_loop(self.one_loop)
        self.assertKweli(fut.done())
        self.assertEqual(fut.result(), [])
        ukijumuisha self.assertWarns(DeprecationWarning):
            fut = asyncio.gather(*seq_or_iter, loop=self.other_loop)
        self.assertIs(fut._loop, self.other_loop)

    eleza test_constructor_empty_sequence(self):
        self._check_empty_sequence([])
        self._check_empty_sequence(())
        self._check_empty_sequence(set())
        self._check_empty_sequence(iter(""))

    eleza test_constructor_heterogenous_futures(self):
        fut1 = self.one_loop.create_future()
        fut2 = self.other_loop.create_future()
        ukijumuisha self.assertRaises(ValueError):
            asyncio.gather(fut1, fut2)
        ukijumuisha self.assertRaises(ValueError):
            asyncio.gather(fut1, loop=self.other_loop)

    eleza test_constructor_homogenous_futures(self):
        children = [self.other_loop.create_future() kila i kwenye range(3)]
        fut = asyncio.gather(*children)
        self.assertIs(fut._loop, self.other_loop)
        self._run_loop(self.other_loop)
        self.assertUongo(fut.done())
        fut = asyncio.gather(*children, loop=self.other_loop)
        self.assertIs(fut._loop, self.other_loop)
        self._run_loop(self.other_loop)
        self.assertUongo(fut.done())

    eleza test_one_cancellation(self):
        a, b, c, d, e = [self.one_loop.create_future() kila i kwenye range(5)]
        fut = asyncio.gather(a, b, c, d, e)
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        a.set_result(1)
        b.cancel()
        self._run_loop(self.one_loop)
        self.assertKweli(fut.done())
        cb.assert_called_once_with(fut)
        self.assertUongo(fut.cancelled())
        self.assertIsInstance(fut.exception(), asyncio.CancelledError)
        # Does nothing
        c.set_result(3)
        d.cancel()
        e.set_exception(RuntimeError())
        e.exception()

    eleza test_result_exception_one_cancellation(self):
        a, b, c, d, e, f = [self.one_loop.create_future()
                            kila i kwenye range(6)]
        fut = asyncio.gather(a, b, c, d, e, f, return_exceptions=Kweli)
        cb = test_utils.MockCallback()
        fut.add_done_callback(cb)
        a.set_result(1)
        zde = ZeroDivisionError()
        b.set_exception(zde)
        c.cancel()
        self._run_loop(self.one_loop)
        self.assertUongo(fut.done())
        d.set_result(3)
        e.cancel()
        rte = RuntimeError()
        f.set_exception(rte)
        res = self.one_loop.run_until_complete(fut)
        self.assertIsInstance(res[2], asyncio.CancelledError)
        self.assertIsInstance(res[4], asyncio.CancelledError)
        res[2] = res[4] = Tupu
        self.assertEqual(res, [1, zde, Tupu, 3, Tupu, rte])
        cb.assert_called_once_with(fut)


kundi CoroutineGatherTests(GatherTestsBase, test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        asyncio.set_event_loop(self.one_loop)

    eleza wrap_futures(self, *futures):
        coros = []
        kila fut kwenye futures:
            async eleza coro(fut=fut):
                rudisha await fut
            coros.append(coro())
        rudisha coros

    eleza test_constructor_loop_selection(self):
        async eleza coro():
            rudisha 'abc'
        gen1 = coro()
        gen2 = coro()
        fut = asyncio.gather(gen1, gen2)
        self.assertIs(fut._loop, self.one_loop)
        self.one_loop.run_until_complete(fut)

        self.set_event_loop(self.other_loop, cleanup=Uongo)
        gen3 = coro()
        gen4 = coro()
        fut2 = asyncio.gather(gen3, gen4, loop=self.other_loop)
        self.assertIs(fut2._loop, self.other_loop)
        self.other_loop.run_until_complete(fut2)

    eleza test_duplicate_coroutines(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro(s):
                rudisha s
        c = coro('abc')
        fut = asyncio.gather(c, c, coro('def'), c, loop=self.one_loop)
        self._run_loop(self.one_loop)
        self.assertEqual(fut.result(), ['abc', 'abc', 'def', 'abc'])

    eleza test_cancellation_broadcast(self):
        # Cancelling outer() cancels all children.
        proof = 0
        waiter = self.one_loop.create_future()

        async eleza inner():
            nonlocal proof
            await waiter
            proof += 1

        child1 = asyncio.ensure_future(inner(), loop=self.one_loop)
        child2 = asyncio.ensure_future(inner(), loop=self.one_loop)
        gatherer = Tupu

        async eleza outer():
            nonlocal proof, gatherer
            gatherer = asyncio.gather(child1, child2, loop=self.one_loop)
            await gatherer
            proof += 100

        f = asyncio.ensure_future(outer(), loop=self.one_loop)
        test_utils.run_briefly(self.one_loop)
        self.assertKweli(f.cancel())
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.one_loop.run_until_complete(f)
        self.assertUongo(gatherer.cancel())
        self.assertKweli(waiter.cancelled())
        self.assertKweli(child1.cancelled())
        self.assertKweli(child2.cancelled())
        test_utils.run_briefly(self.one_loop)
        self.assertEqual(proof, 0)

    eleza test_exception_marking(self):
        # Test kila the first line marked "Mark exception retrieved."

        async eleza inner(f):
            await f
            ashiria RuntimeError('should sio be ignored')

        a = self.one_loop.create_future()
        b = self.one_loop.create_future()

        async eleza outer():
            await asyncio.gather(inner(a), inner(b), loop=self.one_loop)

        f = asyncio.ensure_future(outer(), loop=self.one_loop)
        test_utils.run_briefly(self.one_loop)
        a.set_result(Tupu)
        test_utils.run_briefly(self.one_loop)
        b.set_result(Tupu)
        test_utils.run_briefly(self.one_loop)
        self.assertIsInstance(f.exception(), RuntimeError)


kundi RunCoroutineThreadsafeTests(test_utils.TestCase):
    """Test case kila asyncio.run_coroutine_threadsafe."""

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop) # Will cleanup properly

    async eleza add(self, a, b, fail=Uongo, cancel=Uongo):
        """Wait 0.05 second na rudisha a + b."""
        await asyncio.sleep(0.05)
        ikiwa fail:
            ashiria RuntimeError("Fail!")
        ikiwa cancel:
            asyncio.current_task(self.loop).cancel()
            await asyncio.sleep(0)
        rudisha a + b

    eleza target(self, fail=Uongo, cancel=Uongo, timeout=Tupu,
               advance_coro=Uongo):
        """Run add coroutine kwenye the event loop."""
        coro = self.add(1, 2, fail=fail, cancel=cancel)
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        ikiwa advance_coro:
            # this ni kila test_run_coroutine_threadsafe_task_factory_exception;
            # otherwise it spills errors na komas **other** unittests, since
            # 'target' ni interacting ukijumuisha threads.

            # With this call, `coro` will be advanced, so that
            # CoroWrapper.__del__ won't do anything when asyncio tests run
            # kwenye debug mode.
            self.loop.call_soon_threadsafe(coro.send, Tupu)
        jaribu:
            rudisha future.result(timeout)
        mwishowe:
            future.done() ama future.cancel()

    eleza test_run_coroutine_threadsafe(self):
        """Test coroutine submission kutoka a thread to an event loop."""
        future = self.loop.run_in_executor(Tupu, self.target)
        result = self.loop.run_until_complete(future)
        self.assertEqual(result, 3)

    eleza test_run_coroutine_threadsafe_with_exception(self):
        """Test coroutine submission kutoka a thread to an event loop
        when an exception ni raised."""
        future = self.loop.run_in_executor(Tupu, self.target, Kweli)
        ukijumuisha self.assertRaises(RuntimeError) kama exc_context:
            self.loop.run_until_complete(future)
        self.assertIn("Fail!", exc_context.exception.args)

    eleza test_run_coroutine_threadsafe_with_timeout(self):
        """Test coroutine submission kutoka a thread to an event loop
        when a timeout ni raised."""
        callback = lambda: self.target(timeout=0)
        future = self.loop.run_in_executor(Tupu, callback)
        ukijumuisha self.assertRaises(asyncio.TimeoutError):
            self.loop.run_until_complete(future)
        test_utils.run_briefly(self.loop)
        # Check that there's no pending task (add has been cancelled)
        kila task kwenye asyncio.all_tasks(self.loop):
            self.assertKweli(task.done())

    eleza test_run_coroutine_threadsafe_task_cancelled(self):
        """Test coroutine submission kutoka a tread to an event loop
        when the task ni cancelled."""
        callback = lambda: self.target(cancel=Kweli)
        future = self.loop.run_in_executor(Tupu, callback)
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(future)

    eleza test_run_coroutine_threadsafe_task_factory_exception(self):
        """Test coroutine submission kutoka a tread to an event loop
        when the task factory ashiria an exception."""

        eleza task_factory(loop, coro):
            ashiria NameError

        run = self.loop.run_in_executor(
            Tupu, lambda: self.target(advance_coro=Kweli))

        # Set exception handler
        callback = test_utils.MockCallback()
        self.loop.set_exception_handler(callback)

        # Set corrupted task factory
        self.loop.set_task_factory(task_factory)

        # Run event loop
        ukijumuisha self.assertRaises(NameError) kama exc_context:
            self.loop.run_until_complete(run)

        # Check exceptions
        self.assertEqual(len(callback.call_args_list), 1)
        (loop, context), kwargs = callback.call_args
        self.assertEqual(context['exception'], exc_context.exception)


kundi SleepTests(test_utils.TestCase):
    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    eleza tearDown(self):
        self.loop.close()
        self.loop = Tupu
        super().tearDown()

    eleza test_sleep_zero(self):
        result = 0

        eleza inc_result(num):
            nonlocal result
            result += num

        async eleza coro():
            self.loop.call_soon(inc_result, 1)
            self.assertEqual(result, 0)
            num = await asyncio.sleep(0, result=10)
            self.assertEqual(result, 1) # inc'ed by call_soon
            inc_result(num) # num should be 11

        self.loop.run_until_complete(coro())
        self.assertEqual(result, 11)

    eleza test_loop_argument_is_deprecated(self):
        # Remove test when loop argument ni removed kwenye Python 3.10
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.loop.run_until_complete(asyncio.sleep(0.01, loop=self.loop))


kundi WaitTests(test_utils.TestCase):
    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    eleza tearDown(self):
        self.loop.close()
        self.loop = Tupu
        super().tearDown()

    eleza test_loop_argument_is_deprecated_in_wait(self):
        # Remove test when loop argument ni removed kwenye Python 3.10
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.loop.run_until_complete(
                asyncio.wait([coroutine_function()], loop=self.loop))

    eleza test_loop_argument_is_deprecated_in_wait_for(self):
        # Remove test when loop argument ni removed kwenye Python 3.10
        ukijumuisha self.assertWarns(DeprecationWarning):
            self.loop.run_until_complete(
                asyncio.wait_for(coroutine_function(), 0.01, loop=self.loop))


kundi CompatibilityTests(test_utils.TestCase):
    # Tests kila checking a bridge between old-styled coroutines
    # na async/await syntax

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    eleza tearDown(self):
        self.loop.close()
        self.loop = Tupu
        super().tearDown()

    eleza test_tuma_from_awaitable(self):

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro():
                tuma kutoka asyncio.sleep(0)
                rudisha 'ok'

        result = self.loop.run_until_complete(coro())
        self.assertEqual('ok', result)

    eleza test_await_old_style_coro(self):

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro1():
                rudisha 'ok1'

        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza coro2():
                tuma kutoka asyncio.sleep(0)
                rudisha 'ok2'

        async eleza inner():
            rudisha await asyncio.gather(coro1(), coro2(), loop=self.loop)

        result = self.loop.run_until_complete(inner())
        self.assertEqual(['ok1', 'ok2'], result)

    eleza test_debug_mode_interop(self):
        # https://bugs.python.org/issue32636
        code = textwrap.dedent("""
            agiza asyncio

            async eleza native_coro():
                pita

            @asyncio.coroutine
            eleza old_style_coro():
                tuma kutoka native_coro()

            asyncio.run(old_style_coro())
        """)

        assert_python_ok("-Wignore::DeprecationWarning", "-c", code,
                         PYTHONASYNCIODEBUG="1")


ikiwa __name__ == '__main__':
    unittest.main()
