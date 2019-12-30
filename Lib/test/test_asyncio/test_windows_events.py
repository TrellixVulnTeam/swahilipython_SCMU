agiza os
agiza signal
agiza socket
agiza sys
agiza time
agiza threading
agiza unittest
kutoka unittest agiza mock

ikiwa sys.platform != 'win32':
     ashiria unittest.SkipTest('Windows only')

agiza _overlapped
agiza _winapi

agiza asyncio
kutoka asyncio agiza windows_events
kutoka test.test_asyncio agiza utils as test_utils


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi UpperProto(asyncio.Protocol):
    eleza __init__(self):
        self.buf = []

    eleza connection_made(self, trans):
        self.trans = trans

    eleza data_received(self, data):
        self.buf.append(data)
        ikiwa b'\n' kwenye data:
            self.trans.write(b''.join(self.buf).upper())
            self.trans.close()


kundi ProactorLoopCtrlC(test_utils.TestCase):

    eleza test_ctrl_c(self):

        eleza SIGINT_after_delay():
            time.sleep(0.1)
            signal.raise_signal(signal.SIGINT)

        thread = threading.Thread(target=SIGINT_after_delay)
        loop = asyncio.get_event_loop()
        jaribu:
            # only start the loop once the event loop ni running
            loop.call_soon(thread.start)
            loop.run_forever()
            self.fail("should sio fall through 'run_forever'")
        except KeyboardInterrupt:
            pass
        mwishowe:
            self.close_loop(loop)
        thread.join()


kundi ProactorMultithreading(test_utils.TestCase):
    eleza test_run_from_nonmain_thread(self):
        finished = Uongo

        async eleza coro():
            await asyncio.sleep(0)

        eleza func():
            nonlocal finished
            loop = asyncio.new_event_loop()
            loop.run_until_complete(coro())
            finished = Kweli

        thread = threading.Thread(target=func)
        thread.start()
        thread.join()
        self.assertKweli(finished)


kundi ProactorTests(test_utils.TestCase):

    eleza setUp(self):
        super().setUp()
        self.loop = asyncio.ProactorEventLoop()
        self.set_event_loop(self.loop)

    eleza test_close(self):
        a, b = socket.socketpair()
        trans = self.loop._make_socket_transport(a, asyncio.Protocol())
        f = asyncio.ensure_future(self.loop.sock_recv(b, 100), loop=self.loop)
        trans.close()
        self.loop.run_until_complete(f)
        self.assertEqual(f.result(), b'')
        b.close()

    eleza test_double_bind(self):
        ADDRESS = r'\\.\pipe\test_double_bind-%s' % os.getpid()
        server1 = windows_events.PipeServer(ADDRESS)
        ukijumuisha self.assertRaises(PermissionError):
            windows_events.PipeServer(ADDRESS)
        server1.close()

    eleza test_pipe(self):
        res = self.loop.run_until_complete(self._test_pipe())
        self.assertEqual(res, 'done')

    async eleza _test_pipe(self):
        ADDRESS = r'\\.\pipe\_test_pipe-%s' % os.getpid()

        ukijumuisha self.assertRaises(FileNotFoundError):
            await self.loop.create_pipe_connection(
                asyncio.Protocol, ADDRESS)

        [server] = await self.loop.start_serving_pipe(
            UpperProto, ADDRESS)
        self.assertIsInstance(server, windows_events.PipeServer)

        clients = []
        kila i kwenye range(5):
            stream_reader = asyncio.StreamReader(loop=self.loop)
            protocol = asyncio.StreamReaderProtocol(stream_reader,
                                                    loop=self.loop)
            trans, proto = await self.loop.create_pipe_connection(
                lambda: protocol, ADDRESS)
            self.assertIsInstance(trans, asyncio.Transport)
            self.assertEqual(protocol, proto)
            clients.append((stream_reader, trans))

        kila i, (r, w) kwenye enumerate(clients):
            w.write('lower-{}\n'.format(i).encode())

        kila i, (r, w) kwenye enumerate(clients):
            response = await r.readline()
            self.assertEqual(response, 'LOWER-{}\n'.format(i).encode())
            w.close()

        server.close()

        ukijumuisha self.assertRaises(FileNotFoundError):
            await self.loop.create_pipe_connection(
                asyncio.Protocol, ADDRESS)

        rudisha 'done'

    eleza test_connect_pipe_cancel(self):
        exc = OSError()
        exc.winerror = _overlapped.ERROR_PIPE_BUSY
        ukijumuisha mock.patch.object(_overlapped, 'ConnectPipe',
                               side_effect=exc) as connect:
            coro = self.loop._proactor.connect_pipe('pipe_address')
            task = self.loop.create_task(coro)

            # check that it's possible to cancel connect_pipe()
            task.cancel()
            ukijumuisha self.assertRaises(asyncio.CancelledError):
                self.loop.run_until_complete(task)

    eleza test_wait_for_handle(self):
        event = _overlapped.CreateEvent(Tupu, Kweli, Uongo, Tupu)
        self.addCleanup(_winapi.CloseHandle, event)

        # Wait kila unset event ukijumuisha 0.5s timeout;
        # result should be Uongo at timeout
        fut = self.loop._proactor.wait_for_handle(event, 0.5)
        start = self.loop.time()
        done = self.loop.run_until_complete(fut)
        elapsed = self.loop.time() - start

        self.assertEqual(done, Uongo)
        self.assertUongo(fut.result())
        # bpo-31008: Tolerate only 450 ms (at least 500 ms expected),
        # because of bad clock resolution on Windows
        self.assertKweli(0.45 <= elapsed <= 0.9, elapsed)

        _overlapped.SetEvent(event)

        # Wait kila set event;
        # result should be Kweli immediately
        fut = self.loop._proactor.wait_for_handle(event, 10)
        start = self.loop.time()
        done = self.loop.run_until_complete(fut)
        elapsed = self.loop.time() - start

        self.assertEqual(done, Kweli)
        self.assertKweli(fut.result())
        self.assertKweli(0 <= elapsed < 0.3, elapsed)

        # asyncio issue #195: cancelling a done _WaitHandleFuture
        # must sio crash
        fut.cancel()

    eleza test_wait_for_handle_cancel(self):
        event = _overlapped.CreateEvent(Tupu, Kweli, Uongo, Tupu)
        self.addCleanup(_winapi.CloseHandle, event)

        # Wait kila unset event ukijumuisha a cancelled future;
        # CancelledError should be raised immediately
        fut = self.loop._proactor.wait_for_handle(event, 10)
        fut.cancel()
        start = self.loop.time()
        ukijumuisha self.assertRaises(asyncio.CancelledError):
            self.loop.run_until_complete(fut)
        elapsed = self.loop.time() - start
        self.assertKweli(0 <= elapsed < 0.1, elapsed)

        # asyncio issue #195: cancelling a _WaitHandleFuture twice
        # must sio crash
        fut = self.loop._proactor.wait_for_handle(event)
        fut.cancel()
        fut.cancel()


kundi WinPolicyTests(test_utils.TestCase):

    eleza test_selector_win_policy(self):
        async eleza main():
            self.assertIsInstance(
                asyncio.get_running_loop(),
                asyncio.SelectorEventLoop)

        old_policy = asyncio.get_event_loop_policy()
        jaribu:
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(main())
        mwishowe:
            asyncio.set_event_loop_policy(old_policy)

    eleza test_proactor_win_policy(self):
        async eleza main():
            self.assertIsInstance(
                asyncio.get_running_loop(),
                asyncio.ProactorEventLoop)

        old_policy = asyncio.get_event_loop_policy()
        jaribu:
            asyncio.set_event_loop_policy(
                asyncio.WindowsProactorEventLoopPolicy())
            asyncio.run(main())
        mwishowe:
            asyncio.set_event_loop_policy(old_policy)


ikiwa __name__ == '__main__':
    unittest.main()
