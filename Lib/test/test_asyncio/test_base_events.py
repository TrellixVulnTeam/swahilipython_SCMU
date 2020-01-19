"""Tests kila base_events.py"""

agiza concurrent.futures
agiza errno
agiza math
agiza os
agiza socket
agiza sys
agiza threading
agiza time
agiza unittest
kutoka unittest agiza mock

agiza asyncio
kutoka asyncio agiza base_events
kutoka asyncio agiza constants
kutoka test.test_asyncio agiza utils kama test_utils
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok


MOCK_ANY = mock.ANY
PY34 = sys.version_info >= (3, 4)


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


eleza mock_socket_module():
    m_socket = mock.MagicMock(spec=socket)
    kila name kwenye (
        'AF_INET', 'AF_INET6', 'AF_UNSPEC', 'IPPROTO_TCP', 'IPPROTO_UDP',
        'SOCK_STREAM', 'SOCK_DGRAM', 'SOL_SOCKET', 'SO_REUSEADDR', 'inet_pton'
    ):
        ikiwa hasattr(socket, name):
            setattr(m_socket, name, getattr(socket, name))
        isipokua:
            delattr(m_socket, name)

    m_socket.socket = mock.MagicMock()
    m_socket.socket.return_value = test_utils.mock_nonblocking_socket()
    m_socket.getaddrinfo._is_coroutine = Uongo

    rudisha m_socket


eleza patch_socket(f):
    rudisha mock.patch('asyncio.base_events.socket',
                      new_callable=mock_socket_module)(f)


kundi BaseEventTests(test_utils.TestCase):

    eleza test_ipaddr_info(self):
        UNSPEC = socket.AF_UNSPEC
        INET = socket.AF_INET
        INET6 = socket.AF_INET6
        STREAM = socket.SOCK_STREAM
        DGRAM = socket.SOCK_DGRAM
        TCP = socket.IPPROTO_TCP
        UDP = socket.IPPROTO_UDP

        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 1)),
            base_events._ipaddr_info('1.2.3.4', 1, INET, STREAM, TCP))

        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 1)),
            base_events._ipaddr_info(b'1.2.3.4', 1, INET, STREAM, TCP))

        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 1)),
            base_events._ipaddr_info('1.2.3.4', 1, UNSPEC, STREAM, TCP))

        self.assertEqual(
            (INET, DGRAM, UDP, '', ('1.2.3.4', 1)),
            base_events._ipaddr_info('1.2.3.4', 1, UNSPEC, DGRAM, UDP))

        # Socket type STREAM implies TCP protocol.
        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 1)),
            base_events._ipaddr_info('1.2.3.4', 1, UNSPEC, STREAM, 0))

        # Socket type DGRAM implies UDP protocol.
        self.assertEqual(
            (INET, DGRAM, UDP, '', ('1.2.3.4', 1)),
            base_events._ipaddr_info('1.2.3.4', 1, UNSPEC, DGRAM, 0))

        # No socket type.
        self.assertIsTupu(
            base_events._ipaddr_info('1.2.3.4', 1, UNSPEC, 0, 0))

        ikiwa support.IPV6_ENABLED:
            # IPv4 address ukijumuisha family IPv6.
            self.assertIsTupu(
                base_events._ipaddr_info('1.2.3.4', 1, INET6, STREAM, TCP))

            self.assertEqual(
                (INET6, STREAM, TCP, '', ('::3', 1, 0, 0)),
                base_events._ipaddr_info('::3', 1, INET6, STREAM, TCP))

            self.assertEqual(
                (INET6, STREAM, TCP, '', ('::3', 1, 0, 0)),
                base_events._ipaddr_info('::3', 1, UNSPEC, STREAM, TCP))

            # IPv6 address ukijumuisha family IPv4.
            self.assertIsTupu(
                base_events._ipaddr_info('::3', 1, INET, STREAM, TCP))

            # IPv6 address ukijumuisha zone index.
            self.assertIsTupu(
                base_events._ipaddr_info('::3%lo0', 1, INET6, STREAM, TCP))

    eleza test_port_parameter_types(self):
        # Test obscure kinds of arguments kila "port".
        INET = socket.AF_INET
        STREAM = socket.SOCK_STREAM
        TCP = socket.IPPROTO_TCP

        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 0)),
            base_events._ipaddr_info('1.2.3.4', Tupu, INET, STREAM, TCP))

        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 0)),
            base_events._ipaddr_info('1.2.3.4', b'', INET, STREAM, TCP))

        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 0)),
            base_events._ipaddr_info('1.2.3.4', '', INET, STREAM, TCP))

        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 1)),
            base_events._ipaddr_info('1.2.3.4', '1', INET, STREAM, TCP))

        self.assertEqual(
            (INET, STREAM, TCP, '', ('1.2.3.4', 1)),
            base_events._ipaddr_info('1.2.3.4', b'1', INET, STREAM, TCP))

    @patch_socket
    eleza test_ipaddr_info_no_inet_pton(self, m_socket):
        toa m_socket.inet_pton
        self.assertIsTupu(base_events._ipaddr_info('1.2.3.4', 1,
                                                   socket.AF_INET,
                                                   socket.SOCK_STREAM,
                                                   socket.IPPROTO_TCP))


kundi BaseEventLoopTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = base_events.BaseEventLoop()
        self.loop._selector = mock.Mock()
        self.loop._selector.select.return_value = ()
        self.set_event_loop(self.loop)

    eleza test_not_implemented(self):
        m = mock.Mock()
        self.assertRaises(
            NotImplementedError,
            self.loop._make_socket_transport, m, m)
        self.assertRaises(
            NotImplementedError,
            self.loop._make_ssl_transport, m, m, m, m)
        self.assertRaises(
            NotImplementedError,
            self.loop._make_datagram_transport, m, m)
        self.assertRaises(
            NotImplementedError, self.loop._process_events, [])
        self.assertRaises(
            NotImplementedError, self.loop._write_to_self)
        self.assertRaises(
            NotImplementedError,
            self.loop._make_read_pipe_transport, m, m)
        self.assertRaises(
            NotImplementedError,
            self.loop._make_write_pipe_transport, m, m)
        gen = self.loop._make_subprocess_transport(m, m, m, m, m, m, m)
        ukijumuisha self.assertRaises(NotImplementedError):
            gen.send(Tupu)

    eleza test_close(self):
        self.assertUongo(self.loop.is_closed())
        self.loop.close()
        self.assertKweli(self.loop.is_closed())

        # it should be possible to call close() more than once
        self.loop.close()
        self.loop.close()

        # operation blocked when the loop ni closed
        f = self.loop.create_future()
        self.assertRaises(RuntimeError, self.loop.run_forever)
        self.assertRaises(RuntimeError, self.loop.run_until_complete, f)

    eleza test__add_callback_handle(self):
        h = asyncio.Handle(lambda: Uongo, (), self.loop, Tupu)

        self.loop._add_callback(h)
        self.assertUongo(self.loop._scheduled)
        self.assertIn(h, self.loop._ready)

    eleza test__add_callback_cancelled_handle(self):
        h = asyncio.Handle(lambda: Uongo, (), self.loop, Tupu)
        h.cancel()

        self.loop._add_callback(h)
        self.assertUongo(self.loop._scheduled)
        self.assertUongo(self.loop._ready)

    eleza test_set_default_executor(self):
        kundi DummyExecutor(concurrent.futures.ThreadPoolExecutor):
            eleza submit(self, fn, *args, **kwargs):
                ashiria NotImplementedError(
                    'cannot submit into a dummy executor')

        executor = DummyExecutor()
        self.loop.set_default_executor(executor)
        self.assertIs(executor, self.loop._default_executor)

    eleza test_set_default_executor_deprecation_warnings(self):
        executor = mock.Mock()

        ukijumuisha self.assertWarns(DeprecationWarning):
            self.loop.set_default_executor(executor)

    eleza test_call_soon(self):
        eleza cb():
            pita

        h = self.loop.call_soon(cb)
        self.assertEqual(h._callback, cb)
        self.assertIsInstance(h, asyncio.Handle)
        self.assertIn(h, self.loop._ready)

    eleza test_call_soon_non_callable(self):
        self.loop.set_debug(Kweli)
        ukijumuisha self.assertRaisesRegex(TypeError, 'a callable object'):
            self.loop.call_soon(1)

    eleza test_call_later(self):
        eleza cb():
            pita

        h = self.loop.call_later(10.0, cb)
        self.assertIsInstance(h, asyncio.TimerHandle)
        self.assertIn(h, self.loop._scheduled)
        self.assertNotIn(h, self.loop._ready)

    eleza test_call_later_negative_delays(self):
        calls = []

        eleza cb(arg):
            calls.append(arg)

        self.loop._process_events = mock.Mock()
        self.loop.call_later(-1, cb, 'a')
        self.loop.call_later(-2, cb, 'b')
        test_utils.run_briefly(self.loop)
        self.assertEqual(calls, ['b', 'a'])

    eleza test_time_and_call_at(self):
        eleza cb():
            self.loop.stop()

        self.loop._process_events = mock.Mock()
        delay = 0.1

        when = self.loop.time() + delay
        self.loop.call_at(when, cb)
        t0 = self.loop.time()
        self.loop.run_forever()
        dt = self.loop.time() - t0

        # 50 ms: maximum granularity of the event loop
        self.assertGreaterEqual(dt, delay - 0.050, dt)
        # tolerate a difference of +800 ms because some Python buildbots
        # are really slow
        self.assertLessEqual(dt, 0.9, dt)

    eleza check_thread(self, loop, debug):
        eleza cb():
            pita

        loop.set_debug(debug)
        ikiwa debug:
            msg = ("Non-thread-safe operation invoked on an event loop other "
                   "than the current one")
            ukijumuisha self.assertRaisesRegex(RuntimeError, msg):
                loop.call_soon(cb)
            ukijumuisha self.assertRaisesRegex(RuntimeError, msg):
                loop.call_later(60, cb)
            ukijumuisha self.assertRaisesRegex(RuntimeError, msg):
                loop.call_at(loop.time() + 60, cb)
        isipokua:
            loop.call_soon(cb)
            loop.call_later(60, cb)
            loop.call_at(loop.time() + 60, cb)

    eleza test_check_thread(self):
        eleza check_in_thread(loop, event, debug, create_loop, fut):
            # wait until the event loop ni running
            event.wait()

            jaribu:
                ikiwa create_loop:
                    loop2 = base_events.BaseEventLoop()
                    jaribu:
                        asyncio.set_event_loop(loop2)
                        self.check_thread(loop, debug)
                    mwishowe:
                        asyncio.set_event_loop(Tupu)
                        loop2.close()
                isipokua:
                    self.check_thread(loop, debug)
            tatizo Exception kama exc:
                loop.call_soon_threadsafe(fut.set_exception, exc)
            isipokua:
                loop.call_soon_threadsafe(fut.set_result, Tupu)

        eleza test_thread(loop, debug, create_loop=Uongo):
            event = threading.Event()
            fut = loop.create_future()
            loop.call_soon(event.set)
            args = (loop, event, debug, create_loop, fut)
            thread = threading.Thread(target=check_in_thread, args=args)
            thread.start()
            loop.run_until_complete(fut)
            thread.join()

        self.loop._process_events = mock.Mock()
        self.loop._write_to_self = mock.Mock()

        # ashiria RuntimeError ikiwa the thread has no event loop
        test_thread(self.loop, Kweli)

        # check disabled ikiwa debug mode ni disabled
        test_thread(self.loop, Uongo)

        # ashiria RuntimeError ikiwa the event loop of the thread ni sio the called
        # event loop
        test_thread(self.loop, Kweli, create_loop=Kweli)

        # check disabled ikiwa debug mode ni disabled
        test_thread(self.loop, Uongo, create_loop=Kweli)

    eleza test__run_once(self):
        h1 = asyncio.TimerHandle(time.monotonic() + 5.0, lambda: Kweli, (),
                                 self.loop, Tupu)
        h2 = asyncio.TimerHandle(time.monotonic() + 10.0, lambda: Kweli, (),
                                 self.loop, Tupu)

        h1.cancel()

        self.loop._process_events = mock.Mock()
        self.loop._scheduled.append(h1)
        self.loop._scheduled.append(h2)
        self.loop._run_once()

        t = self.loop._selector.select.call_args[0][0]
        self.assertKweli(9.5 < t < 10.5, t)
        self.assertEqual([h2], self.loop._scheduled)
        self.assertKweli(self.loop._process_events.called)

    eleza test_set_debug(self):
        self.loop.set_debug(Kweli)
        self.assertKweli(self.loop.get_debug())
        self.loop.set_debug(Uongo)
        self.assertUongo(self.loop.get_debug())

    eleza test__run_once_schedule_handle(self):
        handle = Tupu
        processed = Uongo

        eleza cb(loop):
            nonlocal processed, handle
            processed = Kweli
            handle = loop.call_soon(lambda: Kweli)

        h = asyncio.TimerHandle(time.monotonic() - 1, cb, (self.loop,),
                                self.loop, Tupu)

        self.loop._process_events = mock.Mock()
        self.loop._scheduled.append(h)
        self.loop._run_once()

        self.assertKweli(processed)
        self.assertEqual([handle], list(self.loop._ready))

    eleza test__run_once_cancelled_event_cleanup(self):
        self.loop._process_events = mock.Mock()

        self.assertKweli(
            0 < base_events._MIN_CANCELLED_TIMER_HANDLES_FRACTION < 1.0)

        eleza cb():
            pita

        # Set up one "blocking" event that will sio be cancelled to
        # ensure later cancelled events do sio make it to the head
        # of the queue na get cleaned.
        not_cancelled_count = 1
        self.loop.call_later(3000, cb)

        # Add less than threshold (base_events._MIN_SCHEDULED_TIMER_HANDLES)
        # cancelled handles, ensure they aren't removed

        cancelled_count = 2
        kila x kwenye range(2):
            h = self.loop.call_later(3600, cb)
            h.cancel()

        # Add some cancelled events that will be at head na removed
        cancelled_count += 2
        kila x kwenye range(2):
            h = self.loop.call_later(100, cb)
            h.cancel()

        # This test ni invalid ikiwa _MIN_SCHEDULED_TIMER_HANDLES ni too low
        self.assertLessEqual(cancelled_count + not_cancelled_count,
            base_events._MIN_SCHEDULED_TIMER_HANDLES)

        self.assertEqual(self.loop._timer_cancelled_count, cancelled_count)

        self.loop._run_once()

        cancelled_count -= 2

        self.assertEqual(self.loop._timer_cancelled_count, cancelled_count)

        self.assertEqual(len(self.loop._scheduled),
            cancelled_count + not_cancelled_count)

        # Need enough events to pita _MIN_CANCELLED_TIMER_HANDLES_FRACTION
        # so that deletion of cancelled events will occur on next _run_once
        add_cancel_count = int(math.ceil(
            base_events._MIN_SCHEDULED_TIMER_HANDLES *
            base_events._MIN_CANCELLED_TIMER_HANDLES_FRACTION)) + 1

        add_not_cancel_count = max(base_events._MIN_SCHEDULED_TIMER_HANDLES -
            add_cancel_count, 0)

        # Add some events that will sio be cancelled
        not_cancelled_count += add_not_cancel_count
        kila x kwenye range(add_not_cancel_count):
            self.loop.call_later(3600, cb)

        # Add enough cancelled events
        cancelled_count += add_cancel_count
        kila x kwenye range(add_cancel_count):
            h = self.loop.call_later(3600, cb)
            h.cancel()

        # Ensure all handles are still scheduled
        self.assertEqual(len(self.loop._scheduled),
            cancelled_count + not_cancelled_count)

        self.loop._run_once()

        # Ensure cancelled events were removed
        self.assertEqual(len(self.loop._scheduled), not_cancelled_count)

        # Ensure only uncancelled events remain scheduled
        self.assertKweli(all([sio x._cancelled kila x kwenye self.loop._scheduled]))

    eleza test_run_until_complete_type_error(self):
        self.assertRaises(TypeError,
            self.loop.run_until_complete, 'blah')

    eleza test_run_until_complete_loop(self):
        task = self.loop.create_future()
        other_loop = self.new_test_loop()
        self.addCleanup(other_loop.close)
        self.assertRaises(ValueError,
            other_loop.run_until_complete, task)

    eleza test_run_until_complete_loop_orphan_future_close_loop(self):
        kundi ShowStopper(SystemExit):
            pita

        async eleza foo(delay):
            await asyncio.sleep(delay)

        eleza throw():
            ashiria ShowStopper

        self.loop._process_events = mock.Mock()
        self.loop.call_soon(throw)
        ukijumuisha self.assertRaises(ShowStopper):
            self.loop.run_until_complete(foo(0.1))

        # This call fails ikiwa run_until_complete does sio clean up
        # done-callback kila the previous future.
        self.loop.run_until_complete(foo(0.2))

    eleza test_subprocess_exec_invalid_args(self):
        args = [sys.executable, '-c', 'pita']

        # missing program parameter (empty args)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol)

        # expected multiple arguments, sio a list
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, args)

        # program arguments must be strings, haiko kwenye
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, sys.executable, 123)

        # universal_newlines, shell, bufsize must sio be set
        self.assertRaises(TypeError,
        self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, *args, universal_newlines=Kweli)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, *args, shell=Kweli)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_exec,
            asyncio.SubprocessProtocol, *args, bufsize=4096)

    eleza test_subprocess_shell_invalid_args(self):
        # expected a string, sio an int ama a list
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, 123)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, [sys.executable, '-c', 'pita'])

        # universal_newlines, shell, bufsize must sio be set
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, 'exit 0', universal_newlines=Kweli)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, 'exit 0', shell=Kweli)
        self.assertRaises(TypeError,
            self.loop.run_until_complete, self.loop.subprocess_shell,
            asyncio.SubprocessProtocol, 'exit 0', bufsize=4096)

    eleza test_default_exc_handler_callback(self):
        self.loop._process_events = mock.Mock()

        eleza zero_error(fut):
            fut.set_result(Kweli)
            1/0

        # Test call_soon (events.Handle)
        ukijumuisha mock.patch('asyncio.base_events.logger') kama log:
            fut = self.loop.create_future()
            self.loop.call_soon(zero_error, fut)
            fut.add_done_callback(lambda fut: self.loop.stop())
            self.loop.run_forever()
            log.error.assert_called_with(
                test_utils.MockPattern('Exception kwenye callback.*zero'),
                exc_info=(ZeroDivisionError, MOCK_ANY, MOCK_ANY))

        # Test call_later (events.TimerHandle)
        ukijumuisha mock.patch('asyncio.base_events.logger') kama log:
            fut = self.loop.create_future()
            self.loop.call_later(0.01, zero_error, fut)
            fut.add_done_callback(lambda fut: self.loop.stop())
            self.loop.run_forever()
            log.error.assert_called_with(
                test_utils.MockPattern('Exception kwenye callback.*zero'),
                exc_info=(ZeroDivisionError, MOCK_ANY, MOCK_ANY))

    eleza test_default_exc_handler_coro(self):
        self.loop._process_events = mock.Mock()

        async eleza zero_error_coro():
            await asyncio.sleep(0.01)
            1/0

        # Test Future.__del__
        ukijumuisha mock.patch('asyncio.base_events.logger') kama log:
            fut = asyncio.ensure_future(zero_error_coro(), loop=self.loop)
            fut.add_done_callback(lambda *args: self.loop.stop())
            self.loop.run_forever()
            fut = Tupu # Trigger Future.__del__ ama futures._TracebackLogger
            support.gc_collect()
            ikiwa PY34:
                # Future.__del__ kwenye Python 3.4 logs error with
                # an actual exception context
                log.error.assert_called_with(
                    test_utils.MockPattern('.*exception was never retrieved'),
                    exc_info=(ZeroDivisionError, MOCK_ANY, MOCK_ANY))
            isipokua:
                # futures._TracebackLogger logs only textual traceback
                log.error.assert_called_with(
                    test_utils.MockPattern(
                        '.*exception was never retrieved.*ZeroDiv'),
                    exc_info=Uongo)

    eleza test_set_exc_handler_invalid(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'A callable object ama Tupu'):
            self.loop.set_exception_handler('spam')

    eleza test_set_exc_handler_custom(self):
        eleza zero_error():
            1/0

        eleza run_loop():
            handle = self.loop.call_soon(zero_error)
            self.loop._run_once()
            rudisha handle

        self.loop.set_debug(Kweli)
        self.loop._process_events = mock.Mock()

        self.assertIsTupu(self.loop.get_exception_handler())
        mock_handler = mock.Mock()
        self.loop.set_exception_handler(mock_handler)
        self.assertIs(self.loop.get_exception_handler(), mock_handler)
        handle = run_loop()
        mock_handler.assert_called_with(self.loop, {
            'exception': MOCK_ANY,
            'message': test_utils.MockPattern(
                                'Exception kwenye callback.*zero_error'),
            'handle': handle,
            'source_traceback': handle._source_traceback,
        })
        mock_handler.reset_mock()

        self.loop.set_exception_handler(Tupu)
        ukijumuisha mock.patch('asyncio.base_events.logger') kama log:
            run_loop()
            log.error.assert_called_with(
                        test_utils.MockPattern(
                                'Exception kwenye callback.*zero'),
                        exc_info=(ZeroDivisionError, MOCK_ANY, MOCK_ANY))

        assert sio mock_handler.called

    eleza test_set_exc_handler_broken(self):
        eleza run_loop():
            eleza zero_error():
                1/0
            self.loop.call_soon(zero_error)
            self.loop._run_once()

        eleza handler(loop, context):
            ashiria AttributeError('spam')

        self.loop._process_events = mock.Mock()

        self.loop.set_exception_handler(handler)

        ukijumuisha mock.patch('asyncio.base_events.logger') kama log:
            run_loop()
            log.error.assert_called_with(
                test_utils.MockPattern(
                    'Unhandled error kwenye exception handler'),
                exc_info=(AttributeError, MOCK_ANY, MOCK_ANY))

    eleza test_default_exc_handler_broken(self):
        _context = Tupu

        kundi Loop(base_events.BaseEventLoop):

            _selector = mock.Mock()
            _process_events = mock.Mock()

            eleza default_exception_handler(self, context):
                nonlocal _context
                _context = context
                # Simulates custom buggy "default_exception_handler"
                ashiria ValueError('spam')

        loop = Loop()
        self.addCleanup(loop.close)
        asyncio.set_event_loop(loop)

        eleza run_loop():
            eleza zero_error():
                1/0
            loop.call_soon(zero_error)
            loop._run_once()

        ukijumuisha mock.patch('asyncio.base_events.logger') kama log:
            run_loop()
            log.error.assert_called_with(
                'Exception kwenye default exception handler',
                exc_info=Kweli)

        eleza custom_handler(loop, context):
            ashiria ValueError('ham')

        _context = Tupu
        loop.set_exception_handler(custom_handler)
        ukijumuisha mock.patch('asyncio.base_events.logger') kama log:
            run_loop()
            log.error.assert_called_with(
                test_utils.MockPattern('Exception kwenye default exception.*'
                                       'wakati handling.*in custom'),
                exc_info=Kweli)

            # Check that original context was pitaed to default
            # exception handler.
            self.assertIn('context', _context)
            self.assertIs(type(_context['context']['exception']),
                          ZeroDivisionError)

    eleza test_set_task_factory_invalid(self):
        ukijumuisha self.assertRaisesRegex(
            TypeError, 'task factory must be a callable ama Tupu'):

            self.loop.set_task_factory(1)

        self.assertIsTupu(self.loop.get_task_factory())

    eleza test_set_task_factory(self):
        self.loop._process_events = mock.Mock()

        kundi MyTask(asyncio.Task):
            pita

        async eleza coro():
            pita

        factory = lambda loop, coro: MyTask(coro, loop=loop)

        self.assertIsTupu(self.loop.get_task_factory())
        self.loop.set_task_factory(factory)
        self.assertIs(self.loop.get_task_factory(), factory)

        task = self.loop.create_task(coro())
        self.assertKweli(isinstance(task, MyTask))
        self.loop.run_until_complete(task)

        self.loop.set_task_factory(Tupu)
        self.assertIsTupu(self.loop.get_task_factory())

        task = self.loop.create_task(coro())
        self.assertKweli(isinstance(task, asyncio.Task))
        self.assertUongo(isinstance(task, MyTask))
        self.loop.run_until_complete(task)

    eleza test_env_var_debug(self):
        code = '\n'.join((
            'agiza asyncio',
            'loop = asyncio.get_event_loop()',
            'andika(loop.get_debug())'))

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
                                               PYTHONASYNCIODEBUG='1')
        self.assertEqual(stdout.rstrip(), b'Uongo')

        # -X dev
        sts, stdout, stderr = assert_python_ok('-E', '-X', 'dev',
                                               '-c', code)
        self.assertEqual(stdout.rstrip(), b'Kweli')

    eleza test_create_task(self):
        kundi MyTask(asyncio.Task):
            pita

        async eleza test():
            pita

        kundi EventLoop(base_events.BaseEventLoop):
            eleza create_task(self, coro):
                rudisha MyTask(coro, loop=loop)

        loop = EventLoop()
        self.set_event_loop(loop)

        coro = test()
        task = asyncio.ensure_future(coro, loop=loop)
        self.assertIsInstance(task, MyTask)

        # make warnings quiet
        task._log_destroy_pending = Uongo
        coro.close()

    eleza test_create_named_task_with_default_factory(self):
        async eleza test():
            pita

        loop = asyncio.new_event_loop()
        task = loop.create_task(test(), name='test_task')
        jaribu:
            self.assertEqual(task.get_name(), 'test_task')
        mwishowe:
            loop.run_until_complete(task)
            loop.close()

    eleza test_create_named_task_with_custom_factory(self):
        eleza task_factory(loop, coro):
            rudisha asyncio.Task(coro, loop=loop)

        async eleza test():
            pita

        loop = asyncio.new_event_loop()
        loop.set_task_factory(task_factory)
        task = loop.create_task(test(), name='test_task')
        jaribu:
            self.assertEqual(task.get_name(), 'test_task')
        mwishowe:
            loop.run_until_complete(task)
            loop.close()

    eleza test_run_forever_keyboard_interrupt(self):
        # Python issue #22601: ensure that the temporary task created by
        # run_forever() consumes the KeyboardInterrupt na so don't log
        # a warning
        async eleza raise_keyboard_interrupt():
            ashiria KeyboardInterrupt

        self.loop._process_events = mock.Mock()
        self.loop.call_exception_handler = mock.Mock()

        jaribu:
            self.loop.run_until_complete(raise_keyboard_interrupt())
        tatizo KeyboardInterrupt:
            pita
        self.loop.close()
        support.gc_collect()

        self.assertUongo(self.loop.call_exception_handler.called)

    eleza test_run_until_complete_baseexception(self):
        # Python issue #22429: run_until_complete() must sio schedule a pending
        # call to stop() ikiwa the future raised a BaseException
        async eleza raise_keyboard_interrupt():
            ashiria KeyboardInterrupt

        self.loop._process_events = mock.Mock()

        jaribu:
            self.loop.run_until_complete(raise_keyboard_interrupt())
        tatizo KeyboardInterrupt:
            pita

        eleza func():
            self.loop.stop()
            func.called = Kweli
        func.called = Uongo
        jaribu:
            self.loop.call_soon(func)
            self.loop.run_forever()
        tatizo KeyboardInterrupt:
            pita
        self.assertKweli(func.called)

    eleza test_single_selecter_event_callback_after_stopping(self):
        # Python issue #25593: A stopped event loop may cause event callbacks
        # to run more than once.
        event_sentinel = object()
        callcount = 0
        doer = Tupu

        eleza proc_events(event_list):
            nonlocal doer
            ikiwa event_sentinel kwenye event_list:
                doer = self.loop.call_soon(do_event)

        eleza do_event():
            nonlocal callcount
            callcount += 1
            self.loop.call_soon(clear_selector)

        eleza clear_selector():
            doer.cancel()
            self.loop._selector.select.return_value = ()

        self.loop._process_events = proc_events
        self.loop._selector.select.return_value = (event_sentinel,)

        kila i kwenye range(1, 3):
            ukijumuisha self.subTest('Loop %d/2' % i):
                self.loop.call_soon(self.loop.stop)
                self.loop.run_forever()
                self.assertEqual(callcount, 1)

    eleza test_run_once(self):
        # Simple test kila test_utils.run_once().  It may seem strange
        # to have a test kila this (the function isn't even used!) but
        # it's a de-factor standard API kila library tests.  This tests
        # the idiom: loop.call_soon(loop.stop); loop.run_forever().
        count = 0

        eleza callback():
            nonlocal count
            count += 1

        self.loop._process_events = mock.Mock()
        self.loop.call_soon(callback)
        test_utils.run_once(self.loop)
        self.assertEqual(count, 1)

    eleza test_run_forever_pre_stopped(self):
        # Test that the old idiom kila pre-stopping the loop works.
        self.loop._process_events = mock.Mock()
        self.loop.stop()
        self.loop.run_forever()
        self.loop._selector.select.assert_called_once_with(0)

    async eleza leave_unfinalized_asyncgen(self):
        # Create an async generator, iterate it partially, na leave it
        # to be garbage collected.
        # Used kwenye async generator finalization tests.
        # Depends on implementation details of garbage collector. Changes
        # kwenye gc may koma this function.
        status = {'started': Uongo,
                  'stopped': Uongo,
                  'finalized': Uongo}

        async eleza agen():
            status['started'] = Kweli
            jaribu:
                kila item kwenye ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR']:
                    tuma item
            mwishowe:
                status['finalized'] = Kweli

        ag = agen()
        ai = ag.__aiter__()

        async eleza iter_one():
            jaribu:
                item = await ai.__anext__()
            tatizo StopAsyncIteration:
                rudisha
            ikiwa item == 'THREE':
                status['stopped'] = Kweli
                rudisha
            asyncio.create_task(iter_one())

        asyncio.create_task(iter_one())
        rudisha status

    eleza test_asyncgen_finalization_by_gc(self):
        # Async generators should be finalized when garbage collected.
        self.loop._process_events = mock.Mock()
        self.loop._write_to_self = mock.Mock()
        ukijumuisha support.disable_gc():
            status = self.loop.run_until_complete(self.leave_unfinalized_asyncgen())
            wakati sio status['stopped']:
                test_utils.run_briefly(self.loop)
            self.assertKweli(status['started'])
            self.assertKweli(status['stopped'])
            self.assertUongo(status['finalized'])
            support.gc_collect()
            test_utils.run_briefly(self.loop)
            self.assertKweli(status['finalized'])

    eleza test_asyncgen_finalization_by_gc_in_other_thread(self):
        # Python issue 34769: If garbage collector runs kwenye another
        # thread, async generators will sio finalize kwenye debug
        # mode.
        self.loop._process_events = mock.Mock()
        self.loop._write_to_self = mock.Mock()
        self.loop.set_debug(Kweli)
        ukijumuisha support.disable_gc():
            status = self.loop.run_until_complete(self.leave_unfinalized_asyncgen())
            wakati sio status['stopped']:
                test_utils.run_briefly(self.loop)
            self.assertKweli(status['started'])
            self.assertKweli(status['stopped'])
            self.assertUongo(status['finalized'])
            self.loop.run_until_complete(
                self.loop.run_in_executor(Tupu, support.gc_collect))
            test_utils.run_briefly(self.loop)
            self.assertKweli(status['finalized'])


kundi MyProto(asyncio.Protocol):
    done = Tupu

    eleza __init__(self, create_future=Uongo):
        self.state = 'INITIAL'
        self.nbytes = 0
        ikiwa create_future:
            self.done = asyncio.get_running_loop().create_future()

    eleza connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'CONNECTED'
        transport.write(b'GET / HTTP/1.0\r\nHost: example.com\r\n\r\n')

    eleza data_received(self, data):
        assert self.state == 'CONNECTED', self.state
        self.nbytes += len(data)

    eleza eof_received(self):
        assert self.state == 'CONNECTED', self.state
        self.state = 'EOF'

    eleza connection_lost(self, exc):
        assert self.state kwenye ('CONNECTED', 'EOF'), self.state
        self.state = 'CLOSED'
        ikiwa self.done:
            self.done.set_result(Tupu)


kundi MyDatagramProto(asyncio.DatagramProtocol):
    done = Tupu

    eleza __init__(self, create_future=Uongo, loop=Tupu):
        self.state = 'INITIAL'
        self.nbytes = 0
        ikiwa create_future:
            self.done = loop.create_future()

    eleza connection_made(self, transport):
        self.transport = transport
        assert self.state == 'INITIAL', self.state
        self.state = 'INITIALIZED'

    eleza datagram_received(self, data, addr):
        assert self.state == 'INITIALIZED', self.state
        self.nbytes += len(data)

    eleza error_received(self, exc):
        assert self.state == 'INITIALIZED', self.state

    eleza connection_lost(self, exc):
        assert self.state == 'INITIALIZED', self.state
        self.state = 'CLOSED'
        ikiwa self.done:
            self.done.set_result(Tupu)


kundi BaseEventLoopWithSelectorTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.SelectorEventLoop()
        self.set_event_loop(self.loop)

    @mock.patch('socket.getnameinfo')
    eleza test_getnameinfo(self, m_gai):
        m_gai.side_effect = lambda *args: 42
        r = self.loop.run_until_complete(self.loop.getnameinfo(('abc', 123)))
        self.assertEqual(r, 42)

    @patch_socket
    eleza test_create_connection_multiple_errors(self, m_socket):

        kundi MyProto(asyncio.Protocol):
            pita

        async eleza getaddrinfo(*args, **kw):
            rudisha [(2, 1, 6, '', ('107.6.106.82', 80)),
                    (2, 1, 6, '', ('107.6.106.82', 80))]

        eleza getaddrinfo_task(*args, **kwds):
            rudisha self.loop.create_task(getaddrinfo(*args, **kwds))

        idx = -1
        errors = ['err1', 'err2']

        eleza _socket(*args, **kw):
            nonlocal idx, errors
            idx += 1
            ashiria OSError(errors[idx])

        m_socket.socket = _socket

        self.loop.getaddrinfo = getaddrinfo_task

        coro = self.loop.create_connection(MyProto, 'example.com', 80)
        ukijumuisha self.assertRaises(OSError) kama cm:
            self.loop.run_until_complete(coro)

        self.assertEqual(str(cm.exception), 'Multiple exceptions: err1, err2')

    @patch_socket
    eleza test_create_connection_timeout(self, m_socket):
        # Ensure that the socket ni closed on timeout
        sock = mock.Mock()
        m_socket.socket.return_value = sock

        eleza getaddrinfo(*args, **kw):
            fut = self.loop.create_future()
            addr = (socket.AF_INET, socket.SOCK_STREAM, 0, '',
                    ('127.0.0.1', 80))
            fut.set_result([addr])
            rudisha fut
        self.loop.getaddrinfo = getaddrinfo

        ukijumuisha mock.patch.object(self.loop, 'sock_connect',
                               side_effect=asyncio.TimeoutError):
            coro = self.loop.create_connection(MyProto, '127.0.0.1', 80)
            ukijumuisha self.assertRaises(asyncio.TimeoutError):
                self.loop.run_until_complete(coro)
            self.assertKweli(sock.close.called)

    eleza test_create_connection_host_port_sock(self):
        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, sock=object())
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    eleza test_create_connection_wrong_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ukijumuisha sock:
            coro = self.loop.create_connection(MyProto, sock=sock)
            ukijumuisha self.assertRaisesRegex(ValueError,
                                        'A Stream Socket was expected'):
                self.loop.run_until_complete(coro)

    eleza test_create_server_wrong_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ukijumuisha sock:
            coro = self.loop.create_server(MyProto, sock=sock)
            ukijumuisha self.assertRaisesRegex(ValueError,
                                        'A Stream Socket was expected'):
                self.loop.run_until_complete(coro)

    eleza test_create_server_ssl_timeout_for_plain_socket(self):
        coro = self.loop.create_server(
            MyProto, 'example.com', 80, ssl_handshake_timeout=1)
        ukijumuisha self.assertRaisesRegex(
                ValueError,
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl'):
            self.loop.run_until_complete(coro)

    @unittest.skipUnless(hasattr(socket, 'SOCK_NONBLOCK'),
                         'no socket.SOCK_NONBLOCK (linux only)')
    eleza test_create_server_stream_bittype(self):
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        ukijumuisha sock:
            coro = self.loop.create_server(lambda: Tupu, sock=sock)
            srv = self.loop.run_until_complete(coro)
            srv.close()
            self.loop.run_until_complete(srv.wait_closed())

    @unittest.skipUnless(support.IPV6_ENABLED, 'no IPv6 support')
    eleza test_create_server_ipv6(self):
        async eleza main():
            ukijumuisha self.assertWarns(DeprecationWarning):
                srv = await asyncio.start_server(
                    lambda: Tupu, '::1', 0, loop=self.loop)
            jaribu:
                self.assertGreater(len(srv.sockets), 0)
            mwishowe:
                srv.close()
                await srv.wait_closed()

        jaribu:
            self.loop.run_until_complete(main())
        tatizo OSError kama ex:
            ikiwa (hasattr(errno, 'EADDRNOTAVAIL') na
                    ex.errno == errno.EADDRNOTAVAIL):
                self.skipTest('failed to bind to ::1')
            isipokua:
                raise

    eleza test_create_datagram_endpoint_wrong_sock(self):
        sock = socket.socket(socket.AF_INET)
        ukijumuisha sock:
            coro = self.loop.create_datagram_endpoint(MyProto, sock=sock)
            ukijumuisha self.assertRaisesRegex(ValueError,
                                        'A UDP Socket was expected'):
                self.loop.run_until_complete(coro)

    eleza test_create_connection_no_host_port_sock(self):
        coro = self.loop.create_connection(MyProto)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    eleza test_create_connection_no_getaddrinfo(self):
        async eleza getaddrinfo(*args, **kw):
            rudisha []

        eleza getaddrinfo_task(*args, **kwds):
            rudisha self.loop.create_task(getaddrinfo(*args, **kwds))

        self.loop.getaddrinfo = getaddrinfo_task
        coro = self.loop.create_connection(MyProto, 'example.com', 80)
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    eleza test_create_connection_connect_err(self):
        async eleza getaddrinfo(*args, **kw):
            rudisha [(2, 1, 6, '', ('107.6.106.82', 80))]

        eleza getaddrinfo_task(*args, **kwds):
            rudisha self.loop.create_task(getaddrinfo(*args, **kwds))

        self.loop.getaddrinfo = getaddrinfo_task
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.side_effect = OSError

        coro = self.loop.create_connection(MyProto, 'example.com', 80)
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    eleza test_create_connection_multiple(self):
        async eleza getaddrinfo(*args, **kw):
            rudisha [(2, 1, 6, '', ('0.0.0.1', 80)),
                    (2, 1, 6, '', ('0.0.0.2', 80))]

        eleza getaddrinfo_task(*args, **kwds):
            rudisha self.loop.create_task(getaddrinfo(*args, **kwds))

        self.loop.getaddrinfo = getaddrinfo_task
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.side_effect = OSError

        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, family=socket.AF_INET)
        ukijumuisha self.assertRaises(OSError):
            self.loop.run_until_complete(coro)

    @patch_socket
    eleza test_create_connection_multiple_errors_local_addr(self, m_socket):

        eleza bind(addr):
            ikiwa addr[0] == '0.0.0.1':
                err = OSError('Err')
                err.strerror = 'Err'
                ashiria err

        m_socket.socket.return_value.bind = bind

        async eleza getaddrinfo(*args, **kw):
            rudisha [(2, 1, 6, '', ('0.0.0.1', 80)),
                    (2, 1, 6, '', ('0.0.0.2', 80))]

        eleza getaddrinfo_task(*args, **kwds):
            rudisha self.loop.create_task(getaddrinfo(*args, **kwds))

        self.loop.getaddrinfo = getaddrinfo_task
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.side_effect = OSError('Err2')

        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, family=socket.AF_INET,
            local_addr=(Tupu, 8080))
        ukijumuisha self.assertRaises(OSError) kama cm:
            self.loop.run_until_complete(coro)

        self.assertKweli(str(cm.exception).startswith('Multiple exceptions: '))
        self.assertKweli(m_socket.socket.return_value.close.called)

    eleza _test_create_connection_ip_addr(self, m_socket, allow_inet_pton):
        # Test the fallback code, even ikiwa this system has inet_pton.
        ikiwa sio allow_inet_pton:
            toa m_socket.inet_pton

        m_socket.getaddrinfo = socket.getaddrinfo
        sock = m_socket.socket.return_value

        self.loop._add_reader = mock.Mock()
        self.loop._add_reader._is_coroutine = Uongo
        self.loop._add_writer = mock.Mock()
        self.loop._add_writer._is_coroutine = Uongo

        coro = self.loop.create_connection(asyncio.Protocol, '1.2.3.4', 80)
        t, p = self.loop.run_until_complete(coro)
        jaribu:
            sock.connect.assert_called_with(('1.2.3.4', 80))
            _, kwargs = m_socket.socket.call_args
            self.assertEqual(kwargs['family'], m_socket.AF_INET)
            self.assertEqual(kwargs['type'], m_socket.SOCK_STREAM)
        mwishowe:
            t.close()
            test_utils.run_briefly(self.loop)  # allow transport to close

        ikiwa support.IPV6_ENABLED:
            sock.family = socket.AF_INET6
            coro = self.loop.create_connection(asyncio.Protocol, '::1', 80)
            t, p = self.loop.run_until_complete(coro)
            jaribu:
                # Without inet_pton we use getaddrinfo, which transforms
                # ('::1', 80) to ('::1', 80, 0, 0). The last 0s are flow info,
                # scope id.
                [address] = sock.connect.call_args[0]
                host, port = address[:2]
                self.assertRegex(host, r'::(0\.)*1')
                self.assertEqual(port, 80)
                _, kwargs = m_socket.socket.call_args
                self.assertEqual(kwargs['family'], m_socket.AF_INET6)
                self.assertEqual(kwargs['type'], m_socket.SOCK_STREAM)
            mwishowe:
                t.close()
                test_utils.run_briefly(self.loop)  # allow transport to close

    @unittest.skipUnless(support.IPV6_ENABLED, 'no IPv6 support')
    @unittest.skipIf(sys.platform.startswith('aix'),
                    "bpo-25545: IPv6 scope id na getaddrinfo() behave differently on AIX")
    @patch_socket
    eleza test_create_connection_ipv6_scope(self, m_socket):
        m_socket.getaddrinfo = socket.getaddrinfo
        sock = m_socket.socket.return_value
        sock.family = socket.AF_INET6

        self.loop._add_reader = mock.Mock()
        self.loop._add_reader._is_coroutine = Uongo
        self.loop._add_writer = mock.Mock()
        self.loop._add_writer._is_coroutine = Uongo

        coro = self.loop.create_connection(asyncio.Protocol, 'fe80::1%1', 80)
        t, p = self.loop.run_until_complete(coro)
        jaribu:
            sock.connect.assert_called_with(('fe80::1', 80, 0, 1))
            _, kwargs = m_socket.socket.call_args
            self.assertEqual(kwargs['family'], m_socket.AF_INET6)
            self.assertEqual(kwargs['type'], m_socket.SOCK_STREAM)
        mwishowe:
            t.close()
            test_utils.run_briefly(self.loop)  # allow transport to close

    @patch_socket
    eleza test_create_connection_ip_addr(self, m_socket):
        self._test_create_connection_ip_addr(m_socket, Kweli)

    @patch_socket
    eleza test_create_connection_no_inet_pton(self, m_socket):
        self._test_create_connection_ip_addr(m_socket, Uongo)

    @patch_socket
    eleza test_create_connection_service_name(self, m_socket):
        m_socket.getaddrinfo = socket.getaddrinfo
        sock = m_socket.socket.return_value

        self.loop._add_reader = mock.Mock()
        self.loop._add_reader._is_coroutine = Uongo
        self.loop._add_writer = mock.Mock()
        self.loop._add_writer._is_coroutine = Uongo

        kila service, port kwenye ('http', 80), (b'http', 80):
            coro = self.loop.create_connection(asyncio.Protocol,
                                               '127.0.0.1', service)

            t, p = self.loop.run_until_complete(coro)
            jaribu:
                sock.connect.assert_called_with(('127.0.0.1', port))
                _, kwargs = m_socket.socket.call_args
                self.assertEqual(kwargs['family'], m_socket.AF_INET)
                self.assertEqual(kwargs['type'], m_socket.SOCK_STREAM)
            mwishowe:
                t.close()
                test_utils.run_briefly(self.loop)  # allow transport to close

        kila service kwenye 'nonsense', b'nonsense':
            coro = self.loop.create_connection(asyncio.Protocol,
                                               '127.0.0.1', service)

            ukijumuisha self.assertRaises(OSError):
                self.loop.run_until_complete(coro)

    eleza test_create_connection_no_local_addr(self):
        async eleza getaddrinfo(host, *args, **kw):
            ikiwa host == 'example.com':
                rudisha [(2, 1, 6, '', ('107.6.106.82', 80)),
                        (2, 1, 6, '', ('107.6.106.82', 80))]
            isipokua:
                rudisha []

        eleza getaddrinfo_task(*args, **kwds):
            rudisha self.loop.create_task(getaddrinfo(*args, **kwds))
        self.loop.getaddrinfo = getaddrinfo_task

        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, family=socket.AF_INET,
            local_addr=(Tupu, 8080))
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    @patch_socket
    eleza test_create_connection_bluetooth(self, m_socket):
        # See http://bugs.python.org/issue27136, fallback to getaddrinfo when
        # we can't recognize an address ni resolved, e.g. a Bluetooth address.
        addr = ('00:01:02:03:04:05', 1)

        eleza getaddrinfo(host, port, *args, **kw):
            assert (host, port) == addr
            rudisha [(999, 1, 999, '', (addr, 1))]

        m_socket.getaddrinfo = getaddrinfo
        sock = m_socket.socket()
        coro = self.loop.sock_connect(sock, addr)
        self.loop.run_until_complete(coro)

    eleza test_create_connection_ssl_server_hostname_default(self):
        self.loop.getaddrinfo = mock.Mock()

        eleza mock_getaddrinfo(*args, **kwds):
            f = self.loop.create_future()
            f.set_result([(socket.AF_INET, socket.SOCK_STREAM,
                           socket.SOL_TCP, '', ('1.2.3.4', 80))])
            rudisha f

        self.loop.getaddrinfo.side_effect = mock_getaddrinfo
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.return_value = self.loop.create_future()
        self.loop.sock_connect.return_value.set_result(Tupu)
        self.loop._make_ssl_transport = mock.Mock()

        kundi _SelectorTransportMock:
            _sock = Tupu

            eleza get_extra_info(self, key):
                rudisha mock.Mock()

            eleza close(self):
                self._sock.close()

        eleza mock_make_ssl_transport(sock, protocol, sslcontext, waiter,
                                    **kwds):
            waiter.set_result(Tupu)
            transport = _SelectorTransportMock()
            transport._sock = sock
            rudisha transport

        self.loop._make_ssl_transport.side_effect = mock_make_ssl_transport
        ANY = mock.ANY
        handshake_timeout = object()
        # First try the default server_hostname.
        self.loop._make_ssl_transport.reset_mock()
        coro = self.loop.create_connection(
                MyProto, 'python.org', 80, ssl=Kweli,
                ssl_handshake_timeout=handshake_timeout)
        transport, _ = self.loop.run_until_complete(coro)
        transport.close()
        self.loop._make_ssl_transport.assert_called_with(
            ANY, ANY, ANY, ANY,
            server_side=Uongo,
            server_hostname='python.org',
            ssl_handshake_timeout=handshake_timeout)
        # Next try an explicit server_hostname.
        self.loop._make_ssl_transport.reset_mock()
        coro = self.loop.create_connection(
                MyProto, 'python.org', 80, ssl=Kweli,
                server_hostname='perl.com',
                ssl_handshake_timeout=handshake_timeout)
        transport, _ = self.loop.run_until_complete(coro)
        transport.close()
        self.loop._make_ssl_transport.assert_called_with(
            ANY, ANY, ANY, ANY,
            server_side=Uongo,
            server_hostname='perl.com',
            ssl_handshake_timeout=handshake_timeout)
        # Finally try an explicit empty server_hostname.
        self.loop._make_ssl_transport.reset_mock()
        coro = self.loop.create_connection(
                MyProto, 'python.org', 80, ssl=Kweli,
                server_hostname='',
                ssl_handshake_timeout=handshake_timeout)
        transport, _ = self.loop.run_until_complete(coro)
        transport.close()
        self.loop._make_ssl_transport.assert_called_with(
                ANY, ANY, ANY, ANY,
                server_side=Uongo,
                server_hostname='',
                ssl_handshake_timeout=handshake_timeout)

    eleza test_create_connection_no_ssl_server_hostname_errors(self):
        # When sio using ssl, server_hostname must be Tupu.
        coro = self.loop.create_connection(MyProto, 'python.org', 80,
                                           server_hostname='')
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)
        coro = self.loop.create_connection(MyProto, 'python.org', 80,
                                           server_hostname='python.org')
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    eleza test_create_connection_ssl_server_hostname_errors(self):
        # When using ssl, server_hostname may be Tupu ikiwa host ni non-empty.
        coro = self.loop.create_connection(MyProto, '', 80, ssl=Kweli)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)
        coro = self.loop.create_connection(MyProto, Tupu, 80, ssl=Kweli)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)
        sock = socket.socket()
        coro = self.loop.create_connection(MyProto, Tupu, Tupu,
                                           ssl=Kweli, sock=sock)
        self.addCleanup(sock.close)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    eleza test_create_connection_ssl_timeout_for_plain_socket(self):
        coro = self.loop.create_connection(
            MyProto, 'example.com', 80, ssl_handshake_timeout=1)
        ukijumuisha self.assertRaisesRegex(
                ValueError,
                'ssl_handshake_timeout ni only meaningful ukijumuisha ssl'):
            self.loop.run_until_complete(coro)

    eleza test_create_server_empty_host(self):
        # ikiwa host ni empty string use Tupu instead
        host = object()

        async eleza getaddrinfo(*args, **kw):
            nonlocal host
            host = args[0]
            rudisha []

        eleza getaddrinfo_task(*args, **kwds):
            rudisha self.loop.create_task(getaddrinfo(*args, **kwds))

        self.loop.getaddrinfo = getaddrinfo_task
        fut = self.loop.create_server(MyProto, '', 0)
        self.assertRaises(OSError, self.loop.run_until_complete, fut)
        self.assertIsTupu(host)

    eleza test_create_server_host_port_sock(self):
        fut = self.loop.create_server(
            MyProto, '0.0.0.0', 0, sock=object())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

    eleza test_create_server_no_host_port_sock(self):
        fut = self.loop.create_server(MyProto)
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

    eleza test_create_server_no_getaddrinfo(self):
        getaddrinfo = self.loop.getaddrinfo = mock.Mock()
        getaddrinfo.return_value = self.loop.create_future()
        getaddrinfo.return_value.set_result(Tupu)

        f = self.loop.create_server(MyProto, 'python.org', 0)
        self.assertRaises(OSError, self.loop.run_until_complete, f)

    @patch_socket
    eleza test_create_server_nosoreuseport(self, m_socket):
        m_socket.getaddrinfo = socket.getaddrinfo
        toa m_socket.SO_REUSEPORT
        m_socket.socket.return_value = mock.Mock()

        f = self.loop.create_server(
            MyProto, '0.0.0.0', 0, reuse_port=Kweli)

        self.assertRaises(ValueError, self.loop.run_until_complete, f)

    @patch_socket
    eleza test_create_server_soreuseport_only_defined(self, m_socket):
        m_socket.getaddrinfo = socket.getaddrinfo
        m_socket.socket.return_value = mock.Mock()
        m_socket.SO_REUSEPORT = -1

        f = self.loop.create_server(
            MyProto, '0.0.0.0', 0, reuse_port=Kweli)

        self.assertRaises(ValueError, self.loop.run_until_complete, f)

    @patch_socket
    eleza test_create_server_cant_bind(self, m_socket):

        kundi Err(OSError):
            strerror = 'error'

        m_socket.getaddrinfo.return_value = [
            (2, 1, 6, '', ('127.0.0.1', 10100))]
        m_socket.getaddrinfo._is_coroutine = Uongo
        m_sock = m_socket.socket.return_value = mock.Mock()
        m_sock.bind.side_effect = Err

        fut = self.loop.create_server(MyProto, '0.0.0.0', 0)
        self.assertRaises(OSError, self.loop.run_until_complete, fut)
        self.assertKweli(m_sock.close.called)

    @patch_socket
    eleza test_create_datagram_endpoint_no_addrinfo(self, m_socket):
        m_socket.getaddrinfo.return_value = []
        m_socket.getaddrinfo._is_coroutine = Uongo

        coro = self.loop.create_datagram_endpoint(
            MyDatagramProto, local_addr=('localhost', 0))
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    eleza test_create_datagram_endpoint_addr_error(self):
        coro = self.loop.create_datagram_endpoint(
            MyDatagramProto, local_addr='localhost')
        self.assertRaises(
            AssertionError, self.loop.run_until_complete, coro)
        coro = self.loop.create_datagram_endpoint(
            MyDatagramProto, local_addr=('localhost', 1, 2, 3))
        self.assertRaises(
            AssertionError, self.loop.run_until_complete, coro)

    eleza test_create_datagram_endpoint_connect_err(self):
        self.loop.sock_connect = mock.Mock()
        self.loop.sock_connect.side_effect = OSError

        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, remote_addr=('127.0.0.1', 0))
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    eleza test_create_datagram_endpoint_allow_broadcast(self):
        protocol = MyDatagramProto(create_future=Kweli, loop=self.loop)
        self.loop.sock_connect = sock_connect = mock.Mock()
        sock_connect.return_value = []

        coro = self.loop.create_datagram_endpoint(
            lambda: protocol,
            remote_addr=('127.0.0.1', 0),
            allow_broadcast=Kweli)

        transport, _ = self.loop.run_until_complete(coro)
        self.assertUongo(sock_connect.called)

        transport.close()
        self.loop.run_until_complete(protocol.done)
        self.assertEqual('CLOSED', protocol.state)

    @patch_socket
    eleza test_create_datagram_endpoint_socket_err(self, m_socket):
        m_socket.getaddrinfo = socket.getaddrinfo
        m_socket.socket.side_effect = OSError

        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, family=socket.AF_INET)
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, local_addr=('127.0.0.1', 0))
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)

    @unittest.skipUnless(support.IPV6_ENABLED, 'IPv6 sio supported ama enabled')
    eleza test_create_datagram_endpoint_no_matching_family(self):
        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol,
            remote_addr=('127.0.0.1', 0), local_addr=('::1', 0))
        self.assertRaises(
            ValueError, self.loop.run_until_complete, coro)

    @patch_socket
    eleza test_create_datagram_endpoint_setblk_err(self, m_socket):
        m_socket.socket.return_value.setblocking.side_effect = OSError

        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, family=socket.AF_INET)
        self.assertRaises(
            OSError, self.loop.run_until_complete, coro)
        self.assertKweli(
            m_socket.socket.return_value.close.called)

    eleza test_create_datagram_endpoint_noaddr_nofamily(self):
        coro = self.loop.create_datagram_endpoint(
            asyncio.DatagramProtocol)
        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    @patch_socket
    eleza test_create_datagram_endpoint_cant_bind(self, m_socket):
        kundi Err(OSError):
            pita

        m_socket.getaddrinfo = socket.getaddrinfo
        m_sock = m_socket.socket.return_value = mock.Mock()
        m_sock.bind.side_effect = Err

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto,
            local_addr=('127.0.0.1', 0), family=socket.AF_INET)
        self.assertRaises(Err, self.loop.run_until_complete, fut)
        self.assertKweli(m_sock.close.called)

    eleza test_create_datagram_endpoint_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', 0))
        fut = self.loop.create_datagram_endpoint(
            lambda: MyDatagramProto(create_future=Kweli, loop=self.loop),
            sock=sock)
        transport, protocol = self.loop.run_until_complete(fut)
        transport.close()
        self.loop.run_until_complete(protocol.done)
        self.assertEqual('CLOSED', protocol.state)

    @unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'No UNIX Sockets')
    eleza test_create_datagram_endpoint_sock_unix(self):
        fut = self.loop.create_datagram_endpoint(
            lambda: MyDatagramProto(create_future=Kweli, loop=self.loop),
            family=socket.AF_UNIX)
        transport, protocol = self.loop.run_until_complete(fut)
        assert transport._sock.family == socket.AF_UNIX
        transport.close()
        self.loop.run_until_complete(protocol.done)
        self.assertEqual('CLOSED', protocol.state)

    @unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'No UNIX Sockets')
    eleza test_create_datagram_endpoint_existing_sock_unix(self):
        ukijumuisha test_utils.unix_socket_path() kama path:
            sock = socket.socket(socket.AF_UNIX, type=socket.SOCK_DGRAM)
            sock.bind(path)
            sock.close()

            coro = self.loop.create_datagram_endpoint(
                lambda: MyDatagramProto(create_future=Kweli, loop=self.loop),
                path, family=socket.AF_UNIX)
            transport, protocol = self.loop.run_until_complete(coro)
            transport.close()
            self.loop.run_until_complete(protocol.done)

    eleza test_create_datagram_endpoint_sock_sockopts(self):
        kundi FakeSock:
            type = socket.SOCK_DGRAM

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto, local_addr=('127.0.0.1', 0), sock=FakeSock())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto, remote_addr=('127.0.0.1', 0), sock=FakeSock())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto, family=1, sock=FakeSock())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto, proto=1, sock=FakeSock())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto, flags=1, sock=FakeSock())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto, reuse_address=Kweli, sock=FakeSock())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto, reuse_port=Kweli, sock=FakeSock())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

        fut = self.loop.create_datagram_endpoint(
            MyDatagramProto, allow_broadcast=Kweli, sock=FakeSock())
        self.assertRaises(ValueError, self.loop.run_until_complete, fut)

    eleza test_create_datagram_endpoint_sockopts(self):
        # Socket options should sio be applied unless asked for.
        # SO_REUSEADDR defaults to on kila UNIX.
        # SO_REUSEPORT ni sio available on all platforms.

        coro = self.loop.create_datagram_endpoint(
            lambda: MyDatagramProto(create_future=Kweli, loop=self.loop),
            local_addr=('127.0.0.1', 0))
        transport, protocol = self.loop.run_until_complete(coro)
        sock = transport.get_extra_info('socket')

        reuse_address_default_on = (
            os.name == 'posix' na sys.platform != 'cygwin')
        reuseport_supported = hasattr(socket, 'SO_REUSEPORT')

        ikiwa reuse_address_default_on:
            self.assertKweli(
                sock.getsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR))
        isipokua:
            self.assertUongo(
                sock.getsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR))
        ikiwa reuseport_supported:
            self.assertUongo(
                sock.getsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEPORT))
        self.assertUongo(
            sock.getsockopt(
                socket.SOL_SOCKET, socket.SO_BROADCAST))

        transport.close()
        self.loop.run_until_complete(protocol.done)
        self.assertEqual('CLOSED', protocol.state)

        coro = self.loop.create_datagram_endpoint(
            lambda: MyDatagramProto(create_future=Kweli, loop=self.loop),
            local_addr=('127.0.0.1', 0),
            reuse_address=Kweli,
            reuse_port=reuseport_supported,
            allow_broadcast=Kweli)
        transport, protocol = self.loop.run_until_complete(coro)
        sock = transport.get_extra_info('socket')

        self.assertKweli(
            sock.getsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR))
        ikiwa reuseport_supported:
            self.assertKweli(
                sock.getsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEPORT))
        self.assertKweli(
            sock.getsockopt(
                socket.SOL_SOCKET, socket.SO_BROADCAST))

        transport.close()
        self.loop.run_until_complete(protocol.done)
        self.assertEqual('CLOSED', protocol.state)

    @patch_socket
    eleza test_create_datagram_endpoint_nosoreuseport(self, m_socket):
        toa m_socket.SO_REUSEPORT
        m_socket.socket.return_value = mock.Mock()

        coro = self.loop.create_datagram_endpoint(
            lambda: MyDatagramProto(loop=self.loop),
            local_addr=('127.0.0.1', 0),
            reuse_address=Uongo,
            reuse_port=Kweli)

        self.assertRaises(ValueError, self.loop.run_until_complete, coro)

    @patch_socket
    eleza test_create_datagram_endpoint_ip_addr(self, m_socket):
        eleza getaddrinfo(*args, **kw):
            self.fail('should sio have called getaddrinfo')

        m_socket.getaddrinfo = getaddrinfo
        m_socket.socket.return_value.bind = bind = mock.Mock()
        self.loop._add_reader = mock.Mock()
        self.loop._add_reader._is_coroutine = Uongo

        reuseport_supported = hasattr(socket, 'SO_REUSEPORT')
        coro = self.loop.create_datagram_endpoint(
            lambda: MyDatagramProto(loop=self.loop),
            local_addr=('1.2.3.4', 0),
            reuse_address=Uongo,
            reuse_port=reuseport_supported)

        t, p = self.loop.run_until_complete(coro)
        jaribu:
            bind.assert_called_with(('1.2.3.4', 0))
            m_socket.socket.assert_called_with(family=m_socket.AF_INET,
                                               proto=m_socket.IPPROTO_UDP,
                                               type=m_socket.SOCK_DGRAM)
        mwishowe:
            t.close()
            test_utils.run_briefly(self.loop)  # allow transport to close

    eleza test_accept_connection_retry(self):
        sock = mock.Mock()
        sock.accept.side_effect = BlockingIOError()

        self.loop._accept_connection(MyProto, sock)
        self.assertUongo(sock.close.called)

    @mock.patch('asyncio.base_events.logger')
    eleza test_accept_connection_exception(self, m_log):
        sock = mock.Mock()
        sock.fileno.return_value = 10
        sock.accept.side_effect = OSError(errno.EMFILE, 'Too many open files')
        self.loop._remove_reader = mock.Mock()
        self.loop.call_later = mock.Mock()

        self.loop._accept_connection(MyProto, sock)
        self.assertKweli(m_log.error.called)
        self.assertUongo(sock.close.called)
        self.loop._remove_reader.assert_called_with(10)
        self.loop.call_later.assert_called_with(
            constants.ACCEPT_RETRY_DELAY,
            # self.loop._start_serving
            mock.ANY,
            MyProto, sock, Tupu, Tupu, mock.ANY, mock.ANY)

    eleza test_call_coroutine(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            @asyncio.coroutine
            eleza simple_coroutine():
                pita

        self.loop.set_debug(Kweli)
        coro_func = simple_coroutine
        coro_obj = coro_func()
        self.addCleanup(coro_obj.close)
        kila func kwenye (coro_func, coro_obj):
            ukijumuisha self.assertRaises(TypeError):
                self.loop.call_soon(func)
            ukijumuisha self.assertRaises(TypeError):
                self.loop.call_soon_threadsafe(func)
            ukijumuisha self.assertRaises(TypeError):
                self.loop.call_later(60, func)
            ukijumuisha self.assertRaises(TypeError):
                self.loop.call_at(self.loop.time() + 60, func)
            ukijumuisha self.assertRaises(TypeError):
                self.loop.run_until_complete(
                    self.loop.run_in_executor(Tupu, func))

    @mock.patch('asyncio.base_events.logger')
    eleza test_log_slow_callbacks(self, m_logger):
        eleza stop_loop_cb(loop):
            loop.stop()

        async eleza stop_loop_coro(loop):
            loop.stop()

        asyncio.set_event_loop(self.loop)
        self.loop.set_debug(Kweli)
        self.loop.slow_callback_duration = 0.0

        # slow callback
        self.loop.call_soon(stop_loop_cb, self.loop)
        self.loop.run_forever()
        fmt, *args = m_logger.warning.call_args[0]
        self.assertRegex(fmt % tuple(args),
                         "^Executing <Handle.*stop_loop_cb.*> "
                         "took .* seconds$")

        # slow task
        asyncio.ensure_future(stop_loop_coro(self.loop), loop=self.loop)
        self.loop.run_forever()
        fmt, *args = m_logger.warning.call_args[0]
        self.assertRegex(fmt % tuple(args),
                         "^Executing <Task.*stop_loop_coro.*> "
                         "took .* seconds$")


kundi RunningLoopTests(unittest.TestCase):

    eleza test_running_loop_within_a_loop(self):
        async eleza runner(loop):
            loop.run_forever()

        loop = asyncio.new_event_loop()
        outer_loop = asyncio.new_event_loop()
        jaribu:
            ukijumuisha self.assertRaisesRegex(RuntimeError,
                                        'wakati another loop ni running'):
                outer_loop.run_until_complete(runner(loop))
        mwishowe:
            loop.close()
            outer_loop.close()


kundi BaseLoopSockSendfileTests(test_utils.TestCase):

    DATA = b"12345abcde" * 16 * 1024  # 160 KiB

    kundi MyProto(asyncio.Protocol):

        eleza __init__(self, loop):
            self.started = Uongo
            self.closed = Uongo
            self.data = bytearray()
            self.fut = loop.create_future()
            self.transport = Tupu

        eleza connection_made(self, transport):
            self.started = Kweli
            self.transport = transport

        eleza data_received(self, data):
            self.data.extend(data)

        eleza connection_lost(self, exc):
            self.closed = Kweli
            self.fut.set_result(Tupu)
            self.transport = Tupu

        async eleza wait_closed(self):
            await self.fut

    @classmethod
    eleza setUpClass(cls):
        cls.__old_bufsize = constants.SENDFILE_FALLBACK_READBUFFER_SIZE
        constants.SENDFILE_FALLBACK_READBUFFER_SIZE = 1024 * 16
        ukijumuisha open(support.TESTFN, 'wb') kama fp:
            fp.write(cls.DATA)
        super().setUpClass()

    @classmethod
    eleza tearDownClass(cls):
        constants.SENDFILE_FALLBACK_READBUFFER_SIZE = cls.__old_bufsize
        support.unlink(support.TESTFN)
        super().tearDownClass()

    eleza setUp(self):
        kutoka asyncio.selector_events agiza BaseSelectorEventLoop
        # BaseSelectorEventLoop() has no native implementation
        self.loop = BaseSelectorEventLoop()
        self.set_event_loop(self.loop)
        self.file = open(support.TESTFN, 'rb')
        self.addCleanup(self.file.close)
        super().setUp()

    eleza make_socket(self, blocking=Uongo):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(blocking)
        self.addCleanup(sock.close)
        rudisha sock

    eleza run_loop(self, coro):
        rudisha self.loop.run_until_complete(coro)

    eleza prepare(self):
        sock = self.make_socket()
        proto = self.MyProto(self.loop)
        server = self.run_loop(self.loop.create_server(
            lambda: proto, support.HOST, 0, family=socket.AF_INET))
        addr = server.sockets[0].getsockname()

        kila _ kwenye range(10):
            jaribu:
                self.run_loop(self.loop.sock_connect(sock, addr))
            tatizo OSError:
                self.run_loop(asyncio.sleep(0.5))
                endelea
            isipokua:
                koma
        isipokua:
            # One last try, so we get the exception
            self.run_loop(self.loop.sock_connect(sock, addr))

        eleza cleanup():
            server.close()
            self.run_loop(server.wait_closed())
            sock.close()
            ikiwa proto.transport ni sio Tupu:
                proto.transport.close()
                self.run_loop(proto.wait_closed())

        self.addCleanup(cleanup)

        rudisha sock, proto

    eleza test__sock_sendfile_native_failure(self):
        sock, proto = self.prepare()

        ukijumuisha self.assertRaisesRegex(asyncio.SendfileNotAvailableError,
                                    "sendfile ni sio available"):
            self.run_loop(self.loop._sock_sendfile_native(sock, self.file,
                                                          0, Tupu))

        self.assertEqual(proto.data, b'')
        self.assertEqual(self.file.tell(), 0)

    eleza test_sock_sendfile_no_fallback(self):
        sock, proto = self.prepare()

        ukijumuisha self.assertRaisesRegex(asyncio.SendfileNotAvailableError,
                                    "sendfile ni sio available"):
            self.run_loop(self.loop.sock_sendfile(sock, self.file,
                                                  fallback=Uongo))

        self.assertEqual(self.file.tell(), 0)
        self.assertEqual(proto.data, b'')

    eleza test_sock_sendfile_fallback(self):
        sock, proto = self.prepare()

        ret = self.run_loop(self.loop.sock_sendfile(sock, self.file))
        sock.close()
        self.run_loop(proto.wait_closed())

        self.assertEqual(ret, len(self.DATA))
        self.assertEqual(self.file.tell(), len(self.DATA))
        self.assertEqual(proto.data, self.DATA)

    eleza test_sock_sendfile_fallback_offset_and_count(self):
        sock, proto = self.prepare()

        ret = self.run_loop(self.loop.sock_sendfile(sock, self.file,
                                                    1000, 2000))
        sock.close()
        self.run_loop(proto.wait_closed())

        self.assertEqual(ret, 2000)
        self.assertEqual(self.file.tell(), 3000)
        self.assertEqual(proto.data, self.DATA[1000:3000])

    eleza test_blocking_socket(self):
        self.loop.set_debug(Kweli)
        sock = self.make_socket(blocking=Kweli)
        ukijumuisha self.assertRaisesRegex(ValueError, "must be non-blocking"):
            self.run_loop(self.loop.sock_sendfile(sock, self.file))

    eleza test_nonbinary_file(self):
        sock = self.make_socket()
        ukijumuisha open(support.TESTFN, 'r') kama f:
            ukijumuisha self.assertRaisesRegex(ValueError, "binary mode"):
                self.run_loop(self.loop.sock_sendfile(sock, f))

    eleza test_nonstream_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(Uongo)
        self.addCleanup(sock.close)
        ukijumuisha self.assertRaisesRegex(ValueError, "only SOCK_STREAM type"):
            self.run_loop(self.loop.sock_sendfile(sock, self.file))

    eleza test_notint_count(self):
        sock = self.make_socket()
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    "count must be a positive integer"):
            self.run_loop(self.loop.sock_sendfile(sock, self.file, 0, 'count'))

    eleza test_negative_count(self):
        sock = self.make_socket()
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    "count must be a positive integer"):
            self.run_loop(self.loop.sock_sendfile(sock, self.file, 0, -1))

    eleza test_notint_offset(self):
        sock = self.make_socket()
        ukijumuisha self.assertRaisesRegex(TypeError,
                                    "offset must be a non-negative integer"):
            self.run_loop(self.loop.sock_sendfile(sock, self.file, 'offset'))

    eleza test_negative_offset(self):
        sock = self.make_socket()
        ukijumuisha self.assertRaisesRegex(ValueError,
                                    "offset must be a non-negative integer"):
            self.run_loop(self.loop.sock_sendfile(sock, self.file, -1))


kundi TestSelectorUtils(test_utils.TestCase):
    eleza check_set_nodelay(self, sock):
        opt = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
        self.assertUongo(opt)

        base_events._set_nodelay(sock)

        opt = sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
        self.assertKweli(opt)

    @unittest.skipUnless(hasattr(socket, 'TCP_NODELAY'),
                         'need socket.TCP_NODELAY')
    eleza test_set_nodelay(self):
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM,
                             proto=socket.IPPROTO_TCP)
        ukijumuisha sock:
            self.check_set_nodelay(sock)

        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM,
                             proto=socket.IPPROTO_TCP)
        ukijumuisha sock:
            sock.setblocking(Uongo)
            self.check_set_nodelay(sock)



ikiwa __name__ == '__main__':
    unittest.main()
