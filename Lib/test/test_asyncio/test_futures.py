"""Tests kila futures.py."""

agiza concurrent.futures
agiza gc
agiza re
agiza sys
agiza threading
agiza unittest
kutoka unittest agiza mock

agiza asyncio
kutoka asyncio agiza futures
kutoka test.test_asyncio agiza utils kama test_utils
kutoka test agiza support


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


eleza _fakefunc(f):
    rudisha f


eleza first_cb():
    pita


eleza last_cb():
    pita


kundi DuckFuture:
    # Class that does sio inerit kutoka Future but aims to be duck-type
    # compatible ukijumuisha it.

    _asyncio_future_blocking = Uongo
    __cancelled = Uongo
    __result = Tupu
    __exception = Tupu

    eleza cancel(self):
        ikiwa self.done():
            rudisha Uongo
        self.__cancelled = Kweli
        rudisha Kweli

    eleza cancelled(self):
        rudisha self.__cancelled

    eleza done(self):
        rudisha (self.__cancelled
                ama self.__result ni sio Tupu
                ama self.__exception ni sio Tupu)

    eleza result(self):
        assert sio self.cancelled()
        ikiwa self.__exception ni sio Tupu:
            ashiria self.__exception
        rudisha self.__result

    eleza exception(self):
        assert sio self.cancelled()
        rudisha self.__exception

    eleza set_result(self, result):
        assert sio self.done()
        assert result ni sio Tupu
        self.__result = result

    eleza set_exception(self, exception):
        assert sio self.done()
        assert exception ni sio Tupu
        self.__exception = exception

    eleza __iter__(self):
        ikiwa sio self.done():
            self._asyncio_future_blocking = Kweli
            tuma self
        assert self.done()
        rudisha self.result()


kundi DuckTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.addCleanup(self.loop.close)

    eleza test_wrap_future(self):
        f = DuckFuture()
        g = asyncio.wrap_future(f)
        assert g ni f

    eleza test_ensure_future(self):
        f = DuckFuture()
        g = asyncio.ensure_future(f)
        assert g ni f


kundi BaseFutureTests:

    eleza _new_future(self,  *args, **kwargs):
        rudisha self.cls(*args, **kwargs)

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.addCleanup(self.loop.close)

    eleza test_isfuture(self):
        kundi MyFuture:
            _asyncio_future_blocking = Tupu

            eleza __init__(self):
                self._asyncio_future_blocking = Uongo

        self.assertUongo(asyncio.isfuture(MyFuture))
        self.assertKweli(asyncio.isfuture(MyFuture()))
        self.assertUongo(asyncio.isfuture(1))

        # As `isinstance(Mock(), Future)` returns `Uongo`
        self.assertUongo(asyncio.isfuture(mock.Mock()))

        f = self._new_future(loop=self.loop)
        self.assertKweli(asyncio.isfuture(f))
        self.assertUongo(asyncio.isfuture(type(f)))

        # As `isinstance(Mock(Future), Future)` returns `Kweli`
        self.assertKweli(asyncio.isfuture(mock.Mock(type(f))))

        f.cancel()

    eleza test_initial_state(self):
        f = self._new_future(loop=self.loop)
        self.assertUongo(f.cancelled())
        self.assertUongo(f.done())
        f.cancel()
        self.assertKweli(f.cancelled())

    eleza test_init_constructor_default_loop(self):
        asyncio.set_event_loop(self.loop)
        f = self._new_future()
        self.assertIs(f._loop, self.loop)
        self.assertIs(f.get_loop(), self.loop)

    eleza test_constructor_positional(self):
        # Make sure Future doesn't accept a positional argument
        self.assertRaises(TypeError, self._new_future, 42)

    eleza test_uninitialized(self):
        # Test that C Future doesn't crash when Future.__init__()
        # call was skipped.

        fut = self.cls.__new__(self.cls, loop=self.loop)
        self.assertRaises(asyncio.InvalidStateError, fut.result)

        fut = self.cls.__new__(self.cls, loop=self.loop)
        self.assertRaises(asyncio.InvalidStateError, fut.exception)

        fut = self.cls.__new__(self.cls, loop=self.loop)
        ukijumuisha self.assertRaises((RuntimeError, AttributeError)):
            fut.set_result(Tupu)

        fut = self.cls.__new__(self.cls, loop=self.loop)
        ukijumuisha self.assertRaises((RuntimeError, AttributeError)):
            fut.set_exception(Exception)

        fut = self.cls.__new__(self.cls, loop=self.loop)
        ukijumuisha self.assertRaises((RuntimeError, AttributeError)):
            fut.cancel()

        fut = self.cls.__new__(self.cls, loop=self.loop)
        ukijumuisha self.assertRaises((RuntimeError, AttributeError)):
            fut.add_done_callback(lambda f: Tupu)

        fut = self.cls.__new__(self.cls, loop=self.loop)
        ukijumuisha self.assertRaises((RuntimeError, AttributeError)):
            fut.remove_done_callback(lambda f: Tupu)

        fut = self.cls.__new__(self.cls, loop=self.loop)
        jaribu:
            repr(fut)
        tatizo (RuntimeError, AttributeError):
            pita

        fut = self.cls.__new__(self.cls, loop=self.loop)
        jaribu:
            fut.__await__()
        tatizo RuntimeError:
            pita

        fut = self.cls.__new__(self.cls, loop=self.loop)
        jaribu:
            iter(fut)
        tatizo RuntimeError:
            pita

        fut = self.cls.__new__(self.cls, loop=self.loop)
        self.assertUongo(fut.cancelled())
        self.assertUongo(fut.done())

    eleza test_cancel(self):
        f = self._new_future(loop=self.loop)
        self.assertKweli(f.cancel())
        self.assertKweli(f.cancelled())
        self.assertKweli(f.done())
        self.assertRaises(asyncio.CancelledError, f.result)
        self.assertRaises(asyncio.CancelledError, f.exception)
        self.assertRaises(asyncio.InvalidStateError, f.set_result, Tupu)
        self.assertRaises(asyncio.InvalidStateError, f.set_exception, Tupu)
        self.assertUongo(f.cancel())

    eleza test_result(self):
        f = self._new_future(loop=self.loop)
        self.assertRaises(asyncio.InvalidStateError, f.result)

        f.set_result(42)
        self.assertUongo(f.cancelled())
        self.assertKweli(f.done())
        self.assertEqual(f.result(), 42)
        self.assertEqual(f.exception(), Tupu)
        self.assertRaises(asyncio.InvalidStateError, f.set_result, Tupu)
        self.assertRaises(asyncio.InvalidStateError, f.set_exception, Tupu)
        self.assertUongo(f.cancel())

    eleza test_exception(self):
        exc = RuntimeError()
        f = self._new_future(loop=self.loop)
        self.assertRaises(asyncio.InvalidStateError, f.exception)

        # StopIteration cansio be raised into a Future - CPython issue26221
        self.assertRaisesRegex(TypeError, "StopIteration .* cansio be raised",
                               f.set_exception, StopIteration)

        f.set_exception(exc)
        self.assertUongo(f.cancelled())
        self.assertKweli(f.done())
        self.assertRaises(RuntimeError, f.result)
        self.assertEqual(f.exception(), exc)
        self.assertRaises(asyncio.InvalidStateError, f.set_result, Tupu)
        self.assertRaises(asyncio.InvalidStateError, f.set_exception, Tupu)
        self.assertUongo(f.cancel())

    eleza test_exception_class(self):
        f = self._new_future(loop=self.loop)
        f.set_exception(RuntimeError)
        self.assertIsInstance(f.exception(), RuntimeError)

    eleza test_tuma_from_twice(self):
        f = self._new_future(loop=self.loop)

        eleza fixture():
            tuma 'A'
            x = tuma kutoka f
            tuma 'B', x
            y = tuma kutoka f
            tuma 'C', y

        g = fixture()
        self.assertEqual(next(g), 'A')  # tuma 'A'.
        self.assertEqual(next(g), f)  # First tuma kutoka f.
        f.set_result(42)
        self.assertEqual(next(g), ('B', 42))  # tuma 'B', x.
        # The second "tuma kutoka f" does sio tuma f.
        self.assertEqual(next(g), ('C', 42))  # tuma 'C', y.

    eleza test_future_repr(self):
        self.loop.set_debug(Kweli)
        f_pending_debug = self._new_future(loop=self.loop)
        frame = f_pending_debug._source_traceback[-1]
        self.assertEqual(
            repr(f_pending_debug),
            f'<{self.cls.__name__} pending created at {frame[0]}:{frame[1]}>')
        f_pending_debug.cancel()

        self.loop.set_debug(Uongo)
        f_pending = self._new_future(loop=self.loop)
        self.assertEqual(repr(f_pending), f'<{self.cls.__name__} pending>')
        f_pending.cancel()

        f_cancelled = self._new_future(loop=self.loop)
        f_cancelled.cancel()
        self.assertEqual(repr(f_cancelled), f'<{self.cls.__name__} cancelled>')

        f_result = self._new_future(loop=self.loop)
        f_result.set_result(4)
        self.assertEqual(
            repr(f_result), f'<{self.cls.__name__} finished result=4>')
        self.assertEqual(f_result.result(), 4)

        exc = RuntimeError()
        f_exception = self._new_future(loop=self.loop)
        f_exception.set_exception(exc)
        self.assertEqual(
            repr(f_exception),
            f'<{self.cls.__name__} finished exception=RuntimeError()>')
        self.assertIs(f_exception.exception(), exc)

        eleza func_repr(func):
            filename, lineno = test_utils.get_function_source(func)
            text = '%s() at %s:%s' % (func.__qualname__, filename, lineno)
            rudisha re.escape(text)

        f_one_callbacks = self._new_future(loop=self.loop)
        f_one_callbacks.add_done_callback(_fakefunc)
        fake_repr = func_repr(_fakefunc)
        self.assertRegex(
            repr(f_one_callbacks),
            r'<' + self.cls.__name__ + r' pending cb=\[%s\]>' % fake_repr)
        f_one_callbacks.cancel()
        self.assertEqual(repr(f_one_callbacks),
                         f'<{self.cls.__name__} cancelled>')

        f_two_callbacks = self._new_future(loop=self.loop)
        f_two_callbacks.add_done_callback(first_cb)
        f_two_callbacks.add_done_callback(last_cb)
        first_repr = func_repr(first_cb)
        last_repr = func_repr(last_cb)
        self.assertRegex(repr(f_two_callbacks),
                         r'<' + self.cls.__name__ + r' pending cb=\[%s, %s\]>'
                         % (first_repr, last_repr))

        f_many_callbacks = self._new_future(loop=self.loop)
        f_many_callbacks.add_done_callback(first_cb)
        kila i kwenye range(8):
            f_many_callbacks.add_done_callback(_fakefunc)
        f_many_callbacks.add_done_callback(last_cb)
        cb_regex = r'%s, <8 more>, %s' % (first_repr, last_repr)
        self.assertRegex(
            repr(f_many_callbacks),
            r'<' + self.cls.__name__ + r' pending cb=\[%s\]>' % cb_regex)
        f_many_callbacks.cancel()
        self.assertEqual(repr(f_many_callbacks),
                         f'<{self.cls.__name__} cancelled>')

    eleza test_copy_state(self):
        kutoka asyncio.futures agiza _copy_future_state

        f = self._new_future(loop=self.loop)
        f.set_result(10)

        newf = self._new_future(loop=self.loop)
        _copy_future_state(f, newf)
        self.assertKweli(newf.done())
        self.assertEqual(newf.result(), 10)

        f_exception = self._new_future(loop=self.loop)
        f_exception.set_exception(RuntimeError())

        newf_exception = self._new_future(loop=self.loop)
        _copy_future_state(f_exception, newf_exception)
        self.assertKweli(newf_exception.done())
        self.assertRaises(RuntimeError, newf_exception.result)

        f_cancelled = self._new_future(loop=self.loop)
        f_cancelled.cancel()

        newf_cancelled = self._new_future(loop=self.loop)
        _copy_future_state(f_cancelled, newf_cancelled)
        self.assertKweli(newf_cancelled.cancelled())

    eleza test_iter(self):
        fut = self._new_future(loop=self.loop)

        eleza coro():
            tuma kutoka fut

        eleza test():
            arg1, arg2 = coro()

        ukijumuisha self.assertRaisesRegex(RuntimeError, "await wasn't used"):
            test()
        fut.cancel()

    eleza test_log_traceback(self):
        fut = self._new_future(loop=self.loop)
        ukijumuisha self.assertRaisesRegex(ValueError, 'can only be set to Uongo'):
            fut._log_traceback = Kweli

    @mock.patch('asyncio.base_events.logger')
    eleza test_tb_logger_abandoned(self, m_log):
        fut = self._new_future(loop=self.loop)
        toa fut
        self.assertUongo(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    eleza test_tb_logger_not_called_after_cancel(self, m_log):
        fut = self._new_future(loop=self.loop)
        fut.set_exception(Exception())
        fut.cancel()
        toa fut
        self.assertUongo(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    eleza test_tb_logger_result_unretrieved(self, m_log):
        fut = self._new_future(loop=self.loop)
        fut.set_result(42)
        toa fut
        self.assertUongo(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    eleza test_tb_logger_result_retrieved(self, m_log):
        fut = self._new_future(loop=self.loop)
        fut.set_result(42)
        fut.result()
        toa fut
        self.assertUongo(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    eleza test_tb_logger_exception_unretrieved(self, m_log):
        fut = self._new_future(loop=self.loop)
        fut.set_exception(RuntimeError('boom'))
        toa fut
        test_utils.run_briefly(self.loop)
        support.gc_collect()
        self.assertKweli(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    eleza test_tb_logger_exception_retrieved(self, m_log):
        fut = self._new_future(loop=self.loop)
        fut.set_exception(RuntimeError('boom'))
        fut.exception()
        toa fut
        self.assertUongo(m_log.error.called)

    @mock.patch('asyncio.base_events.logger')
    eleza test_tb_logger_exception_result_retrieved(self, m_log):
        fut = self._new_future(loop=self.loop)
        fut.set_exception(RuntimeError('boom'))
        self.assertRaises(RuntimeError, fut.result)
        toa fut
        self.assertUongo(m_log.error.called)

    eleza test_wrap_future(self):

        eleza run(arg):
            rudisha (arg, threading.get_ident())
        ex = concurrent.futures.ThreadPoolExecutor(1)
        f1 = ex.submit(run, 'oi')
        f2 = asyncio.wrap_future(f1, loop=self.loop)
        res, ident = self.loop.run_until_complete(f2)
        self.assertKweli(asyncio.isfuture(f2))
        self.assertEqual(res, 'oi')
        self.assertNotEqual(ident, threading.get_ident())
        ex.shutdown(wait=Kweli)

    eleza test_wrap_future_future(self):
        f1 = self._new_future(loop=self.loop)
        f2 = asyncio.wrap_future(f1)
        self.assertIs(f1, f2)

    eleza test_wrap_future_use_global_loop(self):
        ukijumuisha mock.patch('asyncio.futures.events') kama events:
            events.get_event_loop = lambda: self.loop
            eleza run(arg):
                rudisha (arg, threading.get_ident())
            ex = concurrent.futures.ThreadPoolExecutor(1)
            f1 = ex.submit(run, 'oi')
            f2 = asyncio.wrap_future(f1)
            self.assertIs(self.loop, f2._loop)
            ex.shutdown(wait=Kweli)

    eleza test_wrap_future_cancel(self):
        f1 = concurrent.futures.Future()
        f2 = asyncio.wrap_future(f1, loop=self.loop)
        f2.cancel()
        test_utils.run_briefly(self.loop)
        self.assertKweli(f1.cancelled())
        self.assertKweli(f2.cancelled())

    eleza test_wrap_future_cancel2(self):
        f1 = concurrent.futures.Future()
        f2 = asyncio.wrap_future(f1, loop=self.loop)
        f1.set_result(42)
        f2.cancel()
        test_utils.run_briefly(self.loop)
        self.assertUongo(f1.cancelled())
        self.assertEqual(f1.result(), 42)
        self.assertKweli(f2.cancelled())

    eleza test_future_source_traceback(self):
        self.loop.set_debug(Kweli)

        future = self._new_future(loop=self.loop)
        lineno = sys._getframe().f_lineno - 1
        self.assertIsInstance(future._source_traceback, list)
        self.assertEqual(future._source_traceback[-2][:3],
                         (__file__,
                          lineno,
                          'test_future_source_traceback'))

    @mock.patch('asyncio.base_events.logger')
    eleza check_future_exception_never_retrieved(self, debug, m_log):
        self.loop.set_debug(debug)

        eleza memory_error():
            jaribu:
                ashiria MemoryError()
            tatizo BaseException kama exc:
                rudisha exc
        exc = memory_error()

        future = self._new_future(loop=self.loop)
        future.set_exception(exc)
        future = Tupu
        test_utils.run_briefly(self.loop)
        support.gc_collect()

        ikiwa sys.version_info >= (3, 4):
            regex = f'^{self.cls.__name__} exception was never retrieved\n'
            exc_info = (type(exc), exc, exc.__traceback__)
            m_log.error.assert_called_once_with(mock.ANY, exc_info=exc_info)
        isipokua:
            regex = r'^Future/Task exception was never retrieved\n'
            m_log.error.assert_called_once_with(mock.ANY, exc_info=Uongo)
        message = m_log.error.call_args[0][0]
        self.assertRegex(message, re.compile(regex, re.DOTALL))

    eleza test_future_exception_never_retrieved(self):
        self.check_future_exception_never_retrieved(Uongo)

    eleza test_future_exception_never_retrieved_debug(self):
        self.check_future_exception_never_retrieved(Kweli)

    eleza test_set_result_unless_cancelled(self):
        fut = self._new_future(loop=self.loop)
        fut.cancel()
        futures._set_result_unless_cancelled(fut, 2)
        self.assertKweli(fut.cancelled())

    eleza test_future_stop_iteration_args(self):
        fut = self._new_future(loop=self.loop)
        fut.set_result((1, 2))
        fi = fut.__iter__()
        result = Tupu
        jaribu:
            fi.send(Tupu)
        tatizo StopIteration kama ex:
            result = ex.args[0]
        isipokua:
            self.fail('StopIteration was expected')
        self.assertEqual(result, (1, 2))

    eleza test_future_iter_throw(self):
        fut = self._new_future(loop=self.loop)
        fi = iter(fut)
        self.assertRaises(TypeError, fi.throw,
                          Exception, Exception("elephant"), 32)
        self.assertRaises(TypeError, fi.throw,
                          Exception("elephant"), Exception("elephant"))
        self.assertRaises(TypeError, fi.throw, list)

    eleza test_future_del_collect(self):
        kundi Evil:
            eleza __del__(self):
                gc.collect()

        kila i kwenye range(100):
            fut = self._new_future(loop=self.loop)
            fut.set_result(Evil())


@unittest.skipUnless(hasattr(futures, '_CFuture'),
                     'requires the C _asyncio module')
kundi CFutureTests(BaseFutureTests, test_utils.TestCase):
    jaribu:
        cls = futures._CFuture
    tatizo AttributeError:
        cls = Tupu

    eleza test_future_del_segfault(self):
        fut = self._new_future(loop=self.loop)
        ukijumuisha self.assertRaises(AttributeError):
            toa fut._asyncio_future_blocking
        ukijumuisha self.assertRaises(AttributeError):
            toa fut._log_traceback


@unittest.skipUnless(hasattr(futures, '_CFuture'),
                     'requires the C _asyncio module')
kundi CSubFutureTests(BaseFutureTests, test_utils.TestCase):
    jaribu:
        kundi CSubFuture(futures._CFuture):
            pita

        cls = CSubFuture
    tatizo AttributeError:
        cls = Tupu


kundi PyFutureTests(BaseFutureTests, test_utils.TestCase):
    cls = futures._PyFuture


kundi BaseFutureDoneCallbackTests():

    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()

    eleza run_briefly(self):
        test_utils.run_briefly(self.loop)

    eleza _make_callback(self, bag, thing):
        # Create a callback function that appends thing to bag.
        eleza bag_appender(future):
            bag.append(thing)
        rudisha bag_appender

    eleza _new_future(self):
        ashiria NotImplementedError

    eleza test_callbacks_remove_first_callback(self):
        bag = []
        f = self._new_future()

        cb1 = self._make_callback(bag, 42)
        cb2 = self._make_callback(bag, 17)
        cb3 = self._make_callback(bag, 100)

        f.add_done_callback(cb1)
        f.add_done_callback(cb2)
        f.add_done_callback(cb3)

        f.remove_done_callback(cb1)
        f.remove_done_callback(cb1)

        self.assertEqual(bag, [])
        f.set_result('foo')

        self.run_briefly()

        self.assertEqual(bag, [17, 100])
        self.assertEqual(f.result(), 'foo')

    eleza test_callbacks_remove_first_and_second_callback(self):
        bag = []
        f = self._new_future()

        cb1 = self._make_callback(bag, 42)
        cb2 = self._make_callback(bag, 17)
        cb3 = self._make_callback(bag, 100)

        f.add_done_callback(cb1)
        f.add_done_callback(cb2)
        f.add_done_callback(cb3)

        f.remove_done_callback(cb1)
        f.remove_done_callback(cb2)
        f.remove_done_callback(cb1)

        self.assertEqual(bag, [])
        f.set_result('foo')

        self.run_briefly()

        self.assertEqual(bag, [100])
        self.assertEqual(f.result(), 'foo')

    eleza test_callbacks_remove_third_callback(self):
        bag = []
        f = self._new_future()

        cb1 = self._make_callback(bag, 42)
        cb2 = self._make_callback(bag, 17)
        cb3 = self._make_callback(bag, 100)

        f.add_done_callback(cb1)
        f.add_done_callback(cb2)
        f.add_done_callback(cb3)

        f.remove_done_callback(cb3)
        f.remove_done_callback(cb3)

        self.assertEqual(bag, [])
        f.set_result('foo')

        self.run_briefly()

        self.assertEqual(bag, [42, 17])
        self.assertEqual(f.result(), 'foo')

    eleza test_callbacks_invoked_on_set_result(self):
        bag = []
        f = self._new_future()
        f.add_done_callback(self._make_callback(bag, 42))
        f.add_done_callback(self._make_callback(bag, 17))

        self.assertEqual(bag, [])
        f.set_result('foo')

        self.run_briefly()

        self.assertEqual(bag, [42, 17])
        self.assertEqual(f.result(), 'foo')

    eleza test_callbacks_invoked_on_set_exception(self):
        bag = []
        f = self._new_future()
        f.add_done_callback(self._make_callback(bag, 100))

        self.assertEqual(bag, [])
        exc = RuntimeError()
        f.set_exception(exc)

        self.run_briefly()

        self.assertEqual(bag, [100])
        self.assertEqual(f.exception(), exc)

    eleza test_remove_done_callback(self):
        bag = []
        f = self._new_future()
        cb1 = self._make_callback(bag, 1)
        cb2 = self._make_callback(bag, 2)
        cb3 = self._make_callback(bag, 3)

        # Add one cb1 na one cb2.
        f.add_done_callback(cb1)
        f.add_done_callback(cb2)

        # One instance of cb2 removed. Now there's only one cb1.
        self.assertEqual(f.remove_done_callback(cb2), 1)

        # Never had any cb3 kwenye there.
        self.assertEqual(f.remove_done_callback(cb3), 0)

        # After this there will be 6 instances of cb1 na one of cb2.
        f.add_done_callback(cb2)
        kila i kwenye range(5):
            f.add_done_callback(cb1)

        # Remove all instances of cb1. One cb2 remains.
        self.assertEqual(f.remove_done_callback(cb1), 6)

        self.assertEqual(bag, [])
        f.set_result('foo')

        self.run_briefly()

        self.assertEqual(bag, [2])
        self.assertEqual(f.result(), 'foo')

    eleza test_remove_done_callbacks_list_mutation(self):
        # see http://bugs.python.org/issue28963 kila details

        fut = self._new_future()
        fut.add_done_callback(str)

        kila _ kwenye range(63):
            fut.add_done_callback(id)

        kundi evil:
            eleza __eq__(self, other):
                fut.remove_done_callback(id)
                rudisha Uongo

        fut.remove_done_callback(evil())

    eleza test_schedule_callbacks_list_mutation_1(self):
        # see http://bugs.python.org/issue28963 kila details

        eleza mut(f):
            f.remove_done_callback(str)

        fut = self._new_future()
        fut.add_done_callback(mut)
        fut.add_done_callback(str)
        fut.add_done_callback(str)
        fut.set_result(1)
        test_utils.run_briefly(self.loop)

    eleza test_schedule_callbacks_list_mutation_2(self):
        # see http://bugs.python.org/issue30828 kila details

        fut = self._new_future()
        fut.add_done_callback(str)

        kila _ kwenye range(63):
            fut.add_done_callback(id)

        max_extra_cbs = 100
        extra_cbs = 0

        kundi evil:
            eleza __eq__(self, other):
                nonlocal extra_cbs
                extra_cbs += 1
                ikiwa extra_cbs < max_extra_cbs:
                    fut.add_done_callback(id)
                rudisha Uongo

        fut.remove_done_callback(evil())


@unittest.skipUnless(hasattr(futures, '_CFuture'),
                     'requires the C _asyncio module')
kundi CFutureDoneCallbackTests(BaseFutureDoneCallbackTests,
                               test_utils.TestCase):

    eleza _new_future(self):
        rudisha futures._CFuture(loop=self.loop)


@unittest.skipUnless(hasattr(futures, '_CFuture'),
                     'requires the C _asyncio module')
kundi CSubFutureDoneCallbackTests(BaseFutureDoneCallbackTests,
                                  test_utils.TestCase):

    eleza _new_future(self):
        kundi CSubFuture(futures._CFuture):
            pita
        rudisha CSubFuture(loop=self.loop)


kundi PyFutureDoneCallbackTests(BaseFutureDoneCallbackTests,
                                test_utils.TestCase):

    eleza _new_future(self):
        rudisha futures._PyFuture(loop=self.loop)


ikiwa __name__ == '__main__':
    unittest.main()
