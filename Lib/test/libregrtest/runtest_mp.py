agiza collections
agiza faulthandler
agiza json
agiza os
agiza queue
agiza subprocess
agiza sys
agiza threading
agiza time
agiza traceback
agiza types
kutoka test agiza support

kutoka test.libregrtest.runtest agiza (
    runtest, INTERRUPTED, CHILD_ERROR, PROGRESS_MIN_TIME,
    format_test_result, TestResult, is_failed, TIMEOUT)
kutoka test.libregrtest.setup agiza setup_tests
kutoka test.libregrtest.utils agiza format_duration, print_warning


# Display the running tests ikiwa nothing happened last N seconds
PROGRESS_UPDATE = 30.0   # seconds
assert PROGRESS_UPDATE >= PROGRESS_MIN_TIME

# Kill the main process after 5 minutes. It ni supposed to write an update
# every PROGRESS_UPDATE seconds. Tolerate 5 minutes kila Python slowest
# buildbot workers.
MAIN_PROCESS_TIMEOUT = 5 * 60.0
assert MAIN_PROCESS_TIMEOUT >= PROGRESS_UPDATE

# Time to wait until a worker completes: should be immediate
JOIN_TIMEOUT = 30.0   # seconds


eleza must_stop(result, ns):
    ikiwa result.result == INTERRUPTED:
        rudisha Kweli
    ikiwa ns.failfast na is_failed(result, ns):
        rudisha Kweli
    rudisha Uongo


eleza parse_worker_args(worker_args):
    ns_dict, test_name = json.loads(worker_args)
    ns = types.SimpleNamespace(**ns_dict)
    rudisha (ns, test_name)


eleza run_test_in_subprocess(testname, ns):
    ns_dict = vars(ns)
    worker_args = (ns_dict, testname)
    worker_args = json.dumps(worker_args)

    cmd = [sys.executable, *support.args_from_interpreter_flags(),
           '-u',    # Unbuffered stdout na stderr
           '-m', 'test.regrtest',
           '--worker-args', worker_args]

    # Running the child kutoka the same working directory kama regrtest's original
    # invocation ensures that TEMPDIR kila the child ni the same when
    # sysconfig.is_python_build() ni true. See issue 15300.
    rudisha subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=Kweli,
                            close_fds=(os.name != 'nt'),
                            cwd=support.SAVEDCWD)


eleza run_tests_worker(ns, test_name):
    setup_tests(ns)

    result = runtest(ns, test_name)

    andika()   # Force a newline (just kwenye case)

    # Serialize TestResult kama list kwenye JSON
    andika(json.dumps(list(result)), flush=Kweli)
    sys.exit(0)


# We do sio use a generator so multiple threads can call next().
kundi MultiprocessIterator:

    """A thread-safe iterator over tests kila multiprocess mode."""

    eleza __init__(self, tests_iter):
        self.lock = threading.Lock()
        self.tests_iter = tests_iter

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        ukijumuisha self.lock:
            ikiwa self.tests_iter ni Tupu:
                ashiria StopIteration
            rudisha next(self.tests_iter)

    eleza stop(self):
        ukijumuisha self.lock:
            self.tests_iter = Tupu


MultiprocessResult = collections.namedtuple('MultiprocessResult',
    'result stdout stderr error_msg')

kundi ExitThread(Exception):
    pita


kundi TestWorkerProcess(threading.Thread):
    eleza __init__(self, worker_id, runner):
        super().__init__()
        self.worker_id = worker_id
        self.pending = runner.pending
        self.output = runner.output
        self.ns = runner.ns
        self.timeout = runner.worker_timeout
        self.regrtest = runner.regrtest
        self.current_test_name = Tupu
        self.start_time = Tupu
        self._popen = Tupu
        self._killed = Uongo
        self._stopped = Uongo

    eleza __repr__(self):
        info = [f'TestWorkerProcess #{self.worker_id}']
        ikiwa self.is_alive():
            info.append("running")
        isipokua:
            info.append('stopped')
        test = self.current_test_name
        ikiwa test:
            info.append(f'test={test}')
        popen = self._popen
        ikiwa popen ni sio Tupu:
            dt = time.monotonic() - self.start_time
            info.extend((f'pid={self._popen.pid}',
                         f'time={format_duration(dt)}'))
        rudisha '<%s>' % ' '.join(info)

    eleza _kill(self):
        popen = self._popen
        ikiwa popen ni Tupu:
            return

        ikiwa self._killed:
            return
        self._killed = Kweli

        andika(f"Kill {self}", file=sys.stderr, flush=Kweli)
        jaribu:
            popen.kill()
        tatizo OSError kama exc:
            print_warning(f"Failed to kill {self}: {exc!r}")

    eleza stop(self):
        # Method called kutoka a different thread to stop this thread
        self._stopped = Kweli
        self._kill()

    eleza mp_result_error(self, test_name, error_type, stdout='', stderr='',
                        err_msg=Tupu):
        test_time = time.monotonic() - self.start_time
        result = TestResult(test_name, error_type, test_time, Tupu)
        rudisha MultiprocessResult(result, stdout, stderr, err_msg)

    eleza _run_process(self, test_name):
        self.start_time = time.monotonic()

        self.current_test_name = test_name
        jaribu:
            popen = run_test_in_subprocess(test_name, self.ns)

            self._killed = Uongo
            self._popen = popen
        tatizo:
            self.current_test_name = Tupu
            raise

        jaribu:
            ikiwa self._stopped:
                # If kill() has been called before self._popen ni set,
                # self._popen ni still running. Call again kill()
                # to ensure that the process ni killed.
                self._kill()
                ashiria ExitThread

            jaribu:
                stdout, stderr = popen.communicate(timeout=self.timeout)
                retcode = popen.returncode
                assert retcode ni sio Tupu
            tatizo subprocess.TimeoutExpired:
                ikiwa self._stopped:
                    # kill() has been called: communicate() fails
                    # on reading closed stdout/stderr
                    ashiria ExitThread

                # On timeout, kill the process
                self._kill()

                # Tupu means TIMEOUT kila the caller
                retcode = Tupu
                # bpo-38207: Don't attempt to call communicate() again: on it
                # can hang until all child processes using stdout na stderr
                # pipes completes.
                stdout = stderr = ''
            tatizo OSError:
                ikiwa self._stopped:
                    # kill() has been called: communicate() fails
                    # on reading closed stdout/stderr
                    ashiria ExitThread
                raise
            isipokua:
                stdout = stdout.strip()
                stderr = stderr.rstrip()

            rudisha (retcode, stdout, stderr)
        tatizo:
            self._kill()
            raise
        mwishowe:
            self._wait_completed()
            self._popen = Tupu
            self.current_test_name = Tupu

    eleza _runtest(self, test_name):
        retcode, stdout, stderr = self._run_process(test_name)

        ikiwa retcode ni Tupu:
            rudisha self.mp_result_error(test_name, TIMEOUT, stdout, stderr)

        err_msg = Tupu
        ikiwa retcode != 0:
            err_msg = "Exit code %s" % retcode
        isipokua:
            stdout, _, result = stdout.rpartition("\n")
            stdout = stdout.rstrip()
            ikiwa sio result:
                err_msg = "Failed to parse worker stdout"
            isipokua:
                jaribu:
                    # deserialize run_tests_worker() output
                    result = json.loads(result)
                    result = TestResult(*result)
                tatizo Exception kama exc:
                    err_msg = "Failed to parse worker JSON: %s" % exc

        ikiwa err_msg ni sio Tupu:
            rudisha self.mp_result_error(test_name, CHILD_ERROR,
                                        stdout, stderr, err_msg)

        rudisha MultiprocessResult(result, stdout, stderr, err_msg)

    eleza run(self):
        wakati sio self._stopped:
            jaribu:
                jaribu:
                    test_name = next(self.pending)
                tatizo StopIteration:
                    koma

                mp_result = self._runtest(test_name)
                self.output.put((Uongo, mp_result))

                ikiwa must_stop(mp_result.result, self.ns):
                    koma
            tatizo ExitThread:
                koma
            tatizo BaseException:
                self.output.put((Kweli, traceback.format_exc()))
                koma

    eleza _wait_completed(self):
        popen = self._popen

        # stdout na stderr must be closed to ensure that communicate()
        # does sio hang
        popen.stdout.close()
        popen.stderr.close()

        jaribu:
            popen.wait(JOIN_TIMEOUT)
        tatizo (subprocess.TimeoutExpired, OSError) kama exc:
            print_warning(f"Failed to wait kila {self} completion "
                          f"(timeout={format_duration(JOIN_TIMEOUT)}): "
                          f"{exc!r}")

    eleza wait_stopped(self, start_time):
        # bpo-38207: MultiprocessTestRunner.stop_workers() called self.stop()
        # which killed the process. Sometimes, killing the process kutoka the
        # main thread does sio interrupt popen.communicate() in
        # TestWorkerProcess thread. This loop ukijumuisha a timeout ni a workaround
        # kila that.
        #
        # Moreover, ikiwa this method fails to join the thread, it ni likely
        # that Python will hang at exit wakati calling threading._shutdown()
        # which tries again to join the blocked thread. Regrtest.main()
        # uses EXIT_TIMEOUT to workaround this second bug.
        wakati Kweli:
            # Write a message every second
            self.join(1.0)
            ikiwa sio self.is_alive():
                koma
            dt = time.monotonic() - start_time
            self.regrtest.log(f"Waiting kila {self} thread "
                              f"kila {format_duration(dt)}")
            ikiwa dt > JOIN_TIMEOUT:
                print_warning(f"Failed to join {self} kwenye {format_duration(dt)}")
                koma


eleza get_running(workers):
    running = []
    kila worker kwenye workers:
        current_test_name = worker.current_test_name
        ikiwa sio current_test_name:
            endelea
        dt = time.monotonic() - worker.start_time
        ikiwa dt >= PROGRESS_MIN_TIME:
            text = '%s (%s)' % (current_test_name, format_duration(dt))
            running.append(text)
    rudisha running


kundi MultiprocessTestRunner:
    eleza __init__(self, regrtest):
        self.regrtest = regrtest
        self.log = self.regrtest.log
        self.ns = regrtest.ns
        self.output = queue.Queue()
        self.pending = MultiprocessIterator(self.regrtest.tests)
        ikiwa self.ns.timeout ni sio Tupu:
            self.worker_timeout = self.ns.timeout * 1.5
        isipokua:
            self.worker_timeout = Tupu
        self.workers = Tupu

    eleza start_workers(self):
        self.workers = [TestWorkerProcess(index, self)
                        kila index kwenye range(1, self.ns.use_mp + 1)]
        self.log("Run tests kwenye parallel using %s child processes"
                 % len(self.workers))
        kila worker kwenye self.workers:
            worker.start()

    eleza stop_workers(self):
        start_time = time.monotonic()
        kila worker kwenye self.workers:
            worker.stop()
        kila worker kwenye self.workers:
            worker.wait_stopped(start_time)

    eleza _get_result(self):
        ikiwa sio any(worker.is_alive() kila worker kwenye self.workers):
            # all worker threads are done: consume pending results
            jaribu:
                rudisha self.output.get(timeout=0)
            tatizo queue.Empty:
                rudisha Tupu

        use_faulthandler = (self.ns.timeout ni sio Tupu)
        timeout = PROGRESS_UPDATE
        wakati Kweli:
            ikiwa use_faulthandler:
                faulthandler.dump_traceback_later(MAIN_PROCESS_TIMEOUT,
                                                  exit=Kweli)

            # wait kila a thread
            jaribu:
                rudisha self.output.get(timeout=timeout)
            tatizo queue.Empty:
                pita

            # display progress
            running = get_running(self.workers)
            ikiwa running na sio self.ns.pgo:
                self.log('running: %s' % ', '.join(running))

    eleza display_result(self, mp_result):
        result = mp_result.result

        text = format_test_result(result)
        ikiwa mp_result.error_msg ni sio Tupu:
            # CHILD_ERROR
            text += ' (%s)' % mp_result.error_msg
        lasivyo (result.test_time >= PROGRESS_MIN_TIME na sio self.ns.pgo):
            text += ' (%s)' % format_duration(result.test_time)
        running = get_running(self.workers)
        ikiwa running na sio self.ns.pgo:
            text += ' -- running: %s' % ', '.join(running)
        self.regrtest.display_progress(self.test_index, text)

    eleza _process_result(self, item):
        ikiwa item[0]:
            # Thread got an exception
            format_exc = item[1]
            print_warning(f"regrtest worker thread failed: {format_exc}")
            rudisha Kweli

        self.test_index += 1
        mp_result = item[1]
        self.regrtest.accumulate_result(mp_result.result)
        self.display_result(mp_result)

        ikiwa mp_result.stdout:
            andika(mp_result.stdout, flush=Kweli)
        ikiwa mp_result.stderr na sio self.ns.pgo:
            andika(mp_result.stderr, file=sys.stderr, flush=Kweli)

        ikiwa must_stop(mp_result.result, self.ns):
            rudisha Kweli

        rudisha Uongo

    eleza run_tests(self):
        self.start_workers()

        self.test_index = 0
        jaribu:
            wakati Kweli:
                item = self._get_result()
                ikiwa item ni Tupu:
                    koma

                stop = self._process_result(item)
                ikiwa stop:
                    koma
        tatizo KeyboardInterrupt:
            andika()
            self.regrtest.interrupted = Kweli
        mwishowe:
            ikiwa self.ns.timeout ni sio Tupu:
                faulthandler.cancel_dump_traceback_later()

            # Always ensure that all worker processes are no longer
            # worker when we exit this function
            self.pending.stop()
            self.stop_workers()


eleza run_tests_multiprocess(regrtest):
    MultiprocessTestRunner(regrtest).run_tests()
