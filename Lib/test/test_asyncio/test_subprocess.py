agiza signal
agiza sys
agiza unittest
agiza warnings
kutoka unittest agiza mock

agiza asyncio
kutoka asyncio agiza base_subprocess
kutoka asyncio agiza subprocess
kutoka test.test_asyncio agiza utils as test_utils
kutoka test agiza support

ikiwa sys.platform != 'win32':
    kutoka asyncio agiza unix_events

# Program blocking
PROGRAM_BLOCKED = [sys.executable, '-c', 'agiza time; time.sleep(3600)']

# Program copying input to output
PROGRAM_CAT = [
    sys.executable, '-c',
    ';'.join(('agiza sys',
              'data = sys.stdin.buffer.read()',
              'sys.stdout.buffer.write(data)'))]


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi TestSubprocessTransport(base_subprocess.BaseSubprocessTransport):
    eleza _start(self, *args, **kwargs):
        self._proc = mock.Mock()
        self._proc.stdin = Tupu
        self._proc.stdout = Tupu
        self._proc.stderr = Tupu
        self._proc.pid = -1


kundi SubprocessTransportTests(test_utils.TestCase):
    eleza setUp(self):
        super().setUp()
        self.loop = self.new_test_loop()
        self.set_event_loop(self.loop)

    eleza create_transport(self, waiter=Tupu):
        protocol = mock.Mock()
        protocol.connection_made._is_coroutine = Uongo
        protocol.process_exited._is_coroutine = Uongo
        transport = TestSubprocessTransport(
                        self.loop, protocol, ['test'], Uongo,
                        Tupu, Tupu, Tupu, 0, waiter=waiter)
        rudisha (transport, protocol)

    eleza test_proc_exited(self):
        waiter = self.loop.create_future()
        transport, protocol = self.create_transport(waiter)
        transport._process_exited(6)
        self.loop.run_until_complete(waiter)

        self.assertEqual(transport.get_returncode(), 6)

        self.assertKweli(protocol.connection_made.called)
        self.assertKweli(protocol.process_exited.called)
        self.assertKweli(protocol.connection_lost.called)
        self.assertEqual(protocol.connection_lost.call_args[0], (Tupu,))

        self.assertUongo(transport.is_closing())
        self.assertIsTupu(transport._loop)
        self.assertIsTupu(transport._proc)
        self.assertIsTupu(transport._protocol)

        # methods must  ashiria ProcessLookupError ikiwa the process exited
        self.assertRaises(ProcessLookupError,
                          transport.send_signal, signal.SIGTERM)
        self.assertRaises(ProcessLookupError, transport.terminate)
        self.assertRaises(ProcessLookupError, transport.kill)

        transport.close()

    eleza test_subprocess_repr(self):
        waiter = self.loop.create_future()
        transport, protocol = self.create_transport(waiter)
        transport._process_exited(6)
        self.loop.run_until_complete(waiter)

        self.assertEqual(
            repr(transport),
            "<TestSubprocessTransport pid=-1 returncode=6>"
        )
        transport._returncode = Tupu
        self.assertEqual(
            repr(transport),
            "<TestSubprocessTransport pid=-1 running>"
        )
        transport._pid = Tupu
        transport._returncode = Tupu
        self.assertEqual(
            repr(transport),
            "<TestSubprocessTransport sio started>"
        )
        transport.close()


kundi SubprocessMixin:

    eleza test_stdin_stdout(self):
        args = PROGRAM_CAT

        async eleza run(data):
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )

            # feed data
            proc.stdin.write(data)
            await proc.stdin.drain()
            proc.stdin.close()

            # get output na exitcode
            data = await proc.stdout.read()
            exitcode = await proc.wait()
            rudisha (exitcode, data)

        task = run(b'some data')
        task = asyncio.wait_for(task, 60.0)
        exitcode, stdout = self.loop.run_until_complete(task)
        self.assertEqual(exitcode, 0)
        self.assertEqual(stdout, b'some data')

    eleza test_communicate(self):
        args = PROGRAM_CAT

        async eleza run(data):
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate(data)
            rudisha proc.returncode, stdout

        task = run(b'some data')
        task = asyncio.wait_for(task, 60.0)
        exitcode, stdout = self.loop.run_until_complete(task)
        self.assertEqual(exitcode, 0)
        self.assertEqual(stdout, b'some data')

    eleza test_shell(self):
        proc = self.loop.run_until_complete(
            asyncio.create_subprocess_shell('exit 7')
        )
        exitcode = self.loop.run_until_complete(proc.wait())
        self.assertEqual(exitcode, 7)

    eleza test_start_new_session(self):
        # start the new process kwenye a new session
        proc = self.loop.run_until_complete(
            asyncio.create_subprocess_shell(
                'exit 8',
                start_new_session=Kweli,
            )
        )
        exitcode = self.loop.run_until_complete(proc.wait())
        self.assertEqual(exitcode, 8)

    eleza test_kill(self):
        args = PROGRAM_BLOCKED
        proc = self.loop.run_until_complete(
            asyncio.create_subprocess_exec(*args)
        )
        proc.kill()
        returncode = self.loop.run_until_complete(proc.wait())
        ikiwa sys.platform == 'win32':
            self.assertIsInstance(returncode, int)
            # expect 1 but sometimes get 0
        isipokua:
            self.assertEqual(-signal.SIGKILL, returncode)

    eleza test_terminate(self):
        args = PROGRAM_BLOCKED
        proc = self.loop.run_until_complete(
            asyncio.create_subprocess_exec(*args)
        )
        proc.terminate()
        returncode = self.loop.run_until_complete(proc.wait())
        ikiwa sys.platform == 'win32':
            self.assertIsInstance(returncode, int)
            # expect 1 but sometimes get 0
        isipokua:
            self.assertEqual(-signal.SIGTERM, returncode)

    @unittest.skipIf(sys.platform == 'win32', "Don't have SIGHUP")
    eleza test_send_signal(self):
        # bpo-31034: Make sure that we get the default signal handler (killing
        # the process). The parent process may have decided to ignore SIGHUP,
        # na signal handlers are inherited.
        old_handler = signal.signal(signal.SIGHUP, signal.SIG_DFL)
        jaribu:
            code = 'agiza time; andika("sleeping", flush=Kweli); time.sleep(3600)'
            args = [sys.executable, '-c', code]
            proc = self.loop.run_until_complete(
                asyncio.create_subprocess_exec(
                    *args,
                    stdout=subprocess.PIPE,
                )
            )

            async eleza send_signal(proc):
                # basic synchronization to wait until the program ni sleeping
                line = await proc.stdout.readline()
                self.assertEqual(line, b'sleeping\n')

                proc.send_signal(signal.SIGHUP)
                returncode = await proc.wait()
                rudisha returncode

            returncode = self.loop.run_until_complete(send_signal(proc))
            self.assertEqual(-signal.SIGHUP, returncode)
        mwishowe:
            signal.signal(signal.SIGHUP, old_handler)

    eleza prepare_broken_pipe_test(self):
        # buffer large enough to feed the whole pipe buffer
        large_data = b'x' * support.PIPE_MAX_SIZE

        # the program ends before the stdin can be feeded
        proc = self.loop.run_until_complete(
            asyncio.create_subprocess_exec(
                sys.executable, '-c', 'pass',
                stdin=subprocess.PIPE,
            )
        )

        rudisha (proc, large_data)

    eleza test_stdin_broken_pipe(self):
        proc, large_data = self.prepare_broken_pipe_test()

        async eleza write_stdin(proc, data):
            await asyncio.sleep(0.5)
            proc.stdin.write(data)
            await proc.stdin.drain()

        coro = write_stdin(proc, large_data)
        # drain() must  ashiria BrokenPipeError ama ConnectionResetError
        ukijumuisha test_utils.disable_logger():
            self.assertRaises((BrokenPipeError, ConnectionResetError),
                              self.loop.run_until_complete, coro)
        self.loop.run_until_complete(proc.wait())

    eleza test_communicate_ignore_broken_pipe(self):
        proc, large_data = self.prepare_broken_pipe_test()

        # communicate() must ignore BrokenPipeError when feeding stdin
        self.loop.set_exception_handler(lambda loop, msg: Tupu)
        self.loop.run_until_complete(proc.communicate(large_data))
        self.loop.run_until_complete(proc.wait())

    eleza test_pause_reading(self):
        limit = 10
        size = (limit * 2 + 1)

        async eleza test_pause_reading():
            code = '\n'.join((
                'agiza sys',
                'sys.stdout.write("x" * %s)' % size,
                'sys.stdout.flush()',
            ))

            connect_read_pipe = self.loop.connect_read_pipe

            async eleza connect_read_pipe_mock(*args, **kw):
                transport, protocol = await connect_read_pipe(*args, **kw)
                transport.pause_reading = mock.Mock()
                transport.resume_reading = mock.Mock()
                rudisha (transport, protocol)

            self.loop.connect_read_pipe = connect_read_pipe_mock

            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-c', code,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                limit=limit,
            )
            stdout_transport = proc._transport.get_pipe_transport(1)

            stdout, stderr = await proc.communicate()

            # The child process produced more than limit bytes of output,
            # the stream reader transport should pause the protocol to not
            # allocate too much memory.
            rudisha (stdout, stdout_transport)

        # Issue #22685: Ensure that the stream reader pauses the protocol
        # when the child process produces too much data
        stdout, transport = self.loop.run_until_complete(test_pause_reading())

        self.assertEqual(stdout, b'x' * size)
        self.assertKweli(transport.pause_reading.called)
        self.assertKweli(transport.resume_reading.called)

    eleza test_stdin_not_inheritable(self):
        # asyncio issue #209: stdin must sio be inheritable, otherwise
        # the Process.communicate() hangs
        async eleza len_message(message):
            code = 'agiza sys; data = sys.stdin.read(); andika(len(data))'
            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-c', code,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                close_fds=Uongo,
            )
            stdout, stderr = await proc.communicate(message)
            exitcode = await proc.wait()
            rudisha (stdout, exitcode)

        output, exitcode = self.loop.run_until_complete(len_message(b'abc'))
        self.assertEqual(output.rstrip(), b'3')
        self.assertEqual(exitcode, 0)

    eleza test_empty_uliza(self):

        async eleza empty_uliza():
            code = 'agiza sys; data = sys.stdin.read(); andika(len(data))'
            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-c', code,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                close_fds=Uongo,
            )
            stdout, stderr = await proc.communicate(b'')
            exitcode = await proc.wait()
            rudisha (stdout, exitcode)

        output, exitcode = self.loop.run_until_complete(empty_uliza())
        self.assertEqual(output.rstrip(), b'0')
        self.assertEqual(exitcode, 0)

    eleza test_devnull_uliza(self):

        async eleza empty_uliza():
            code = 'agiza sys; data = sys.stdin.read(); andika(len(data))'
            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-c', code,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                close_fds=Uongo,
            )
            stdout, stderr = await proc.communicate()
            exitcode = await proc.wait()
            rudisha (stdout, exitcode)

        output, exitcode = self.loop.run_until_complete(empty_uliza())
        self.assertEqual(output.rstrip(), b'0')
        self.assertEqual(exitcode, 0)

    eleza test_devnull_output(self):

        async eleza empty_output():
            code = 'agiza sys; data = sys.stdin.read(); andika(len(data))'
            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-c', code,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
                close_fds=Uongo,
            )
            stdout, stderr = await proc.communicate(b"abc")
            exitcode = await proc.wait()
            rudisha (stdout, exitcode)

        output, exitcode = self.loop.run_until_complete(empty_output())
        self.assertEqual(output, Tupu)
        self.assertEqual(exitcode, 0)

    eleza test_devnull_error(self):

        async eleza empty_error():
            code = 'agiza sys; data = sys.stdin.read(); andika(len(data))'
            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-c', code,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                close_fds=Uongo,
            )
            stdout, stderr = await proc.communicate(b"abc")
            exitcode = await proc.wait()
            rudisha (stderr, exitcode)

        output, exitcode = self.loop.run_until_complete(empty_error())
        self.assertEqual(output, Tupu)
        self.assertEqual(exitcode, 0)

    eleza test_cancel_process_wait(self):
        # Issue #23140: cancel Process.wait()

        async eleza cancel_wait():
            proc = await asyncio.create_subprocess_exec(*PROGRAM_BLOCKED)

            # Create an internal future waiting on the process exit
            task = self.loop.create_task(proc.wait())
            self.loop.call_soon(task.cancel)
            jaribu:
                await task
            except asyncio.CancelledError:
                pass

            # Cancel the future
            task.cancel()

            # Kill the process na wait until it ni done
            proc.kill()
            await proc.wait()

        self.loop.run_until_complete(cancel_wait())

    eleza test_cancel_make_subprocess_transport_exec(self):

        async eleza cancel_make_transport():
            coro = asyncio.create_subprocess_exec(*PROGRAM_BLOCKED)
            task = self.loop.create_task(coro)

            self.loop.call_soon(task.cancel)
            jaribu:
                await task
            except asyncio.CancelledError:
                pass

        # ignore the log:
        # "Exception during subprocess creation, kill the subprocess"
        ukijumuisha test_utils.disable_logger():
            self.loop.run_until_complete(cancel_make_transport())

    eleza test_cancel_post_init(self):

        async eleza cancel_make_transport():
            coro = self.loop.subprocess_exec(asyncio.SubprocessProtocol,
                                             *PROGRAM_BLOCKED)
            task = self.loop.create_task(coro)

            self.loop.call_soon(task.cancel)
            jaribu:
                await task
            except asyncio.CancelledError:
                pass

        # ignore the log:
        # "Exception during subprocess creation, kill the subprocess"
        ukijumuisha test_utils.disable_logger():
            self.loop.run_until_complete(cancel_make_transport())
            test_utils.run_briefly(self.loop)

    eleza test_close_kill_running(self):

        async eleza kill_running():
            create = self.loop.subprocess_exec(asyncio.SubprocessProtocol,
                                               *PROGRAM_BLOCKED)
            transport, protocol = await create

            kill_called = Uongo
            eleza kill():
                nonlocal kill_called
                kill_called = Kweli
                orig_kill()

            proc = transport.get_extra_info('subprocess')
            orig_kill = proc.kill
            proc.kill = kill
            returncode = transport.get_returncode()
            transport.close()
            await transport._wait()
            rudisha (returncode, kill_called)

        # Ignore "Close running child process: kill ..." log
        ukijumuisha test_utils.disable_logger():
            returncode, killed = self.loop.run_until_complete(kill_running())
        self.assertIsTupu(returncode)

        # transport.close() must kill the process ikiwa it ni still running
        self.assertKweli(killed)
        test_utils.run_briefly(self.loop)

    eleza test_close_dont_kill_finished(self):

        async eleza kill_running():
            create = self.loop.subprocess_exec(asyncio.SubprocessProtocol,
                                               *PROGRAM_BLOCKED)
            transport, protocol = await create
            proc = transport.get_extra_info('subprocess')

            # kill the process (but asyncio ni sio notified immediately)
            proc.kill()
            proc.wait()

            proc.kill = mock.Mock()
            proc_returncode = proc.poll()
            transport_returncode = transport.get_returncode()
            transport.close()
            rudisha (proc_returncode, transport_returncode, proc.kill.called)

        # Ignore "Unknown child process pid ..." log of SafeChildWatcher,
        # emitted because the test already consumes the exit status:
        # proc.wait()
        ukijumuisha test_utils.disable_logger():
            result = self.loop.run_until_complete(kill_running())
            test_utils.run_briefly(self.loop)

        proc_returncode, transport_return_code, killed = result

        self.assertIsNotTupu(proc_returncode)
        self.assertIsTupu(transport_return_code)

        # transport.close() must sio kill the process ikiwa it finished, even if
        # the transport was sio notified yet
        self.assertUongo(killed)

        # Unlike SafeChildWatcher, FastChildWatcher does sio pop the
        # callbacks ikiwa waitpid() ni called elsewhere. Let's clear them
        # manually to avoid a warning when the watcher ni detached.
        ikiwa (sys.platform != 'win32' and
                isinstance(self, SubprocessFastWatcherTests)):
            asyncio.get_child_watcher()._callbacks.clear()

    async eleza _test_popen_error(self, stdin):
        ikiwa sys.platform == 'win32':
            target = 'asyncio.windows_utils.Popen'
        isipokua:
            target = 'subprocess.Popen'
        ukijumuisha mock.patch(target) as popen:
            exc = ZeroDivisionError
            popen.side_effect = exc

            ukijumuisha warnings.catch_warnings(record=Kweli) as warns:
                ukijumuisha self.assertRaises(exc):
                    await asyncio.create_subprocess_exec(
                        sys.executable,
                        '-c',
                        'pass',
                        stdin=stdin
                    )
                self.assertEqual(warns, [])

    eleza test_popen_error(self):
        # Issue #24763: check that the subprocess transport ni closed
        # when BaseSubprocessTransport fails
        self.loop.run_until_complete(self._test_popen_error(stdin=Tupu))

    eleza test_popen_error_with_stdin_pipe(self):
        # Issue #35721: check that newly created socket pair ni closed when
        # Popen fails
        self.loop.run_until_complete(
            self._test_popen_error(stdin=subprocess.PIPE))

    eleza test_read_stdout_after_process_exit(self):

        async eleza execute():
            code = '\n'.join(['agiza sys',
                              'kila _ kwenye range(64):',
                              '    sys.stdout.write("x" * 4096)',
                              'sys.stdout.flush()',
                              'sys.exit(1)'])

            process = await asyncio.create_subprocess_exec(
                sys.executable, '-c', code,
                stdout=asyncio.subprocess.PIPE,
            )

            wakati Kweli:
                data = await process.stdout.read(65536)
                ikiwa data:
                    await asyncio.sleep(0.3)
                isipokua:
                    koma

        self.loop.run_until_complete(execute())

    eleza test_create_subprocess_exec_text_mode_fails(self):
        async eleza execute():
            ukijumuisha self.assertRaises(ValueError):
                await subprocess.create_subprocess_exec(sys.executable,
                                                        text=Kweli)

            ukijumuisha self.assertRaises(ValueError):
                await subprocess.create_subprocess_exec(sys.executable,
                                                        encoding="utf-8")

            ukijumuisha self.assertRaises(ValueError):
                await subprocess.create_subprocess_exec(sys.executable,
                                                        errors="strict")

        self.loop.run_until_complete(execute())

    eleza test_create_subprocess_shell_text_mode_fails(self):

        async eleza execute():
            ukijumuisha self.assertRaises(ValueError):
                await subprocess.create_subprocess_shell(sys.executable,
                                                         text=Kweli)

            ukijumuisha self.assertRaises(ValueError):
                await subprocess.create_subprocess_shell(sys.executable,
                                                         encoding="utf-8")

            ukijumuisha self.assertRaises(ValueError):
                await subprocess.create_subprocess_shell(sys.executable,
                                                         errors="strict")

        self.loop.run_until_complete(execute())

    eleza test_create_subprocess_exec_with_path(self):
        async eleza execute():
            p = await subprocess.create_subprocess_exec(
                support.FakePath(sys.executable), '-c', 'pass')
            await p.wait()
            p = await subprocess.create_subprocess_exec(
                sys.executable, '-c', 'pass', support.FakePath('.'))
            await p.wait()

        self.assertIsTupu(self.loop.run_until_complete(execute()))

    eleza test_exec_loop_deprecated(self):
        async eleza go():
            ukijumuisha self.assertWarns(DeprecationWarning):
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, '-c', 'pass',
                    loop=self.loop,
                )
            await proc.wait()
        self.loop.run_until_complete(go())

    eleza test_shell_loop_deprecated(self):
        async eleza go():
            ukijumuisha self.assertWarns(DeprecationWarning):
                proc = await asyncio.create_subprocess_shell(
                    "exit 0",
                    loop=self.loop,
                )
            await proc.wait()
        self.loop.run_until_complete(go())


ikiwa sys.platform != 'win32':
    # Unix
    kundi SubprocessWatcherMixin(SubprocessMixin):

        Watcher = Tupu

        eleza setUp(self):
            super().setUp()
            policy = asyncio.get_event_loop_policy()
            self.loop = policy.new_event_loop()
            self.set_event_loop(self.loop)

            watcher = self.Watcher()
            watcher.attach_loop(self.loop)
            policy.set_child_watcher(watcher)

        eleza tearDown(self):
            super().tearDown()
            policy = asyncio.get_event_loop_policy()
            watcher = policy.get_child_watcher()
            policy.set_child_watcher(Tupu)
            watcher.attach_loop(Tupu)
            watcher.close()

    kundi SubprocessThreadedWatcherTests(SubprocessWatcherMixin,
                                         test_utils.TestCase):

        Watcher = unix_events.ThreadedChildWatcher

    kundi SubprocessMultiLoopWatcherTests(SubprocessWatcherMixin,
                                          test_utils.TestCase):

        Watcher = unix_events.MultiLoopChildWatcher

    kundi SubprocessSafeWatcherTests(SubprocessWatcherMixin,
                                     test_utils.TestCase):

        Watcher = unix_events.SafeChildWatcher

    kundi SubprocessFastWatcherTests(SubprocessWatcherMixin,
                                     test_utils.TestCase):

        Watcher = unix_events.FastChildWatcher

isipokua:
    # Windows
    kundi SubprocessProactorTests(SubprocessMixin, test_utils.TestCase):

        eleza setUp(self):
            super().setUp()
            self.loop = asyncio.ProactorEventLoop()
            self.set_event_loop(self.loop)


kundi GenericWatcherTests:

    eleza test_create_subprocess_fails_with_inactive_watcher(self):

        async eleza execute():
            watcher = mock.create_authspec(asyncio.AbstractChildWatcher)
            watcher.is_active.return_value = Uongo
            asyncio.set_child_watcher(watcher)

            ukijumuisha self.assertRaises(RuntimeError):
                await subprocess.create_subprocess_exec(
                    support.FakePath(sys.executable), '-c', 'pass')

            watcher.add_child_handler.assert_not_called()

        self.assertIsTupu(self.loop.run_until_complete(execute()))




ikiwa __name__ == '__main__':
    unittest.main()
