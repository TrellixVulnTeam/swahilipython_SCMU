agiza datetime
agiza faulthandler
agiza locale
agiza os
agiza platform
agiza random
agiza re
agiza sys
agiza sysconfig
agiza tempfile
agiza time
agiza unittest
kutoka test.libregrtest.cmdline agiza _parse_args
kutoka test.libregrtest.runtest agiza (
    findtests, runtest, get_abs_module,
    STDTESTS, NOTTESTS, PASSED, FAILED, ENV_CHANGED, SKIPPED, RESOURCE_DENIED,
    INTERRUPTED, CHILD_ERROR, TEST_DID_NOT_RUN, TIMEOUT,
    PROGRESS_MIN_TIME, format_test_result, is_failed)
kutoka test.libregrtest.setup agiza setup_tests
kutoka test.libregrtest.pgo agiza setup_pgo_tests
kutoka test.libregrtest.utils agiza removepy, count, format_duration, printlist
kutoka test agiza support


# bpo-38203: Maximum delay kwenye seconds to exit Python (call Py_Finalize()).
# Used to protect against threading._shutdown() hang.
# Must be smaller than buildbot "1200 seconds without output" limit.
EXIT_TIMEOUT = 120.0


kundi Regrtest:
    """Execute a test suite.

    This also parses command-line options na modifies its behavior
    accordingly.

    tests -- a list of strings containing test names (optional)
    testdir -- the directory kwenye which to look kila tests (optional)

    Users other than the Python test suite will certainly want to
    specify testdir; ikiwa it's omitted, the directory containing the
    Python test suite ni searched for.

    If the tests argument ni omitted, the tests listed on the
    command-line will be used.  If that's empty, too, then all *.py
    files beginning ukijumuisha test_ will be used.

    The other default arguments (verbose, quiet, exclude,
    single, randomize, findleaks, use_resources, trace, coverdir,
    print_slow, na random_seed) allow programmers calling main()
    directly to set the values that would normally be set by flags
    on the command line.
    """
    eleza __init__(self):
        # Namespace of command line options
        self.ns = Tupu

        # tests
        self.tests = []
        self.selected = []

        # test results
        self.good = []
        self.bad = []
        self.skipped = []
        self.resource_denieds = []
        self.environment_changed = []
        self.run_no_tests = []
        self.rerun = []
        self.first_result = Tupu
        self.interrupted = Uongo

        # used by --slow
        self.test_times = []

        # used by --coverage, trace.Trace instance
        self.tracer = Tupu

        # used to display the progress bar "[ 3/100]"
        self.start_time = time.monotonic()
        self.test_count = ''
        self.test_count_width = 1

        # used by --single
        self.next_single_test = Tupu
        self.next_single_filename = Tupu

        # used by --junit-xml
        self.testsuite_xml = Tupu

        # misc
        self.win_load_tracker = Tupu
        self.tmp_dir = Tupu
        self.worker_test_name = Tupu

    eleza get_executed(self):
        rudisha (set(self.good) | set(self.bad) | set(self.skipped)
                | set(self.resource_denieds) | set(self.environment_changed)
                | set(self.run_no_tests))

    eleza accumulate_result(self, result, rerun=Uongo):
        test_name = result.test_name
        ok = result.result

        ikiwa ok sio kwenye (CHILD_ERROR, INTERRUPTED) na sio rerun:
            self.test_times.append((result.test_time, test_name))

        ikiwa ok == PASSED:
            self.good.append(test_name)
        elikiwa ok kwenye (FAILED, CHILD_ERROR):
            ikiwa sio rerun:
                self.bad.append(test_name)
        elikiwa ok == ENV_CHANGED:
            self.environment_changed.append(test_name)
        elikiwa ok == SKIPPED:
            self.skipped.append(test_name)
        elikiwa ok == RESOURCE_DENIED:
            self.skipped.append(test_name)
            self.resource_denieds.append(test_name)
        elikiwa ok == TEST_DID_NOT_RUN:
            self.run_no_tests.append(test_name)
        elikiwa ok == INTERRUPTED:
            self.interrupted = Kweli
        elikiwa ok == TIMEOUT:
            self.bad.append(test_name)
        isipokua:
             ashiria ValueError("invalid test result: %r" % ok)

        ikiwa rerun na ok sio kwenye {FAILED, CHILD_ERROR, INTERRUPTED}:
            self.bad.remove(test_name)

        xml_data = result.xml_data
        ikiwa xml_data:
            agiza xml.etree.ElementTree as ET
            kila e kwenye xml_data:
                jaribu:
                    self.testsuite_xml.append(ET.fromstring(e))
                except ET.ParseError:
                    andika(xml_data, file=sys.__stderr__)
                    raise

    eleza log(self, line=''):
        empty = sio line

        # add the system load prefix: "load avg: 1.80 "
        load_avg = self.getloadavg()
        ikiwa load_avg ni sio Tupu:
            line = f"load avg: {load_avg:.2f} {line}"

        # add the timestamp prefix:  "0:01:05 "
        test_time = time.monotonic() - self.start_time
        test_time = datetime.timedelta(seconds=int(test_time))
        line = f"{test_time} {line}"

        ikiwa empty:
            line = line[:-1]

        andika(line, flush=Kweli)

    eleza display_progress(self, test_index, text):
        ikiwa self.ns.quiet:
            return

        # "[ 51/405/1] test_tcl passed"
        line = f"{test_index:{self.test_count_width}}{self.test_count}"
        fails = len(self.bad) + len(self.environment_changed)
        ikiwa fails na sio self.ns.pgo:
            line = f"{line}/{fails}"
        self.log(f"[{line}] {text}")

    eleza parse_args(self, kwargs):
        ns = _parse_args(sys.argv[1:], **kwargs)

        ikiwa ns.xmlpath:
            support.junit_xml_list = self.testsuite_xml = []

        worker_args = ns.worker_args
        ikiwa worker_args ni sio Tupu:
            kutoka test.libregrtest.runtest_mp agiza parse_worker_args
            ns, test_name = parse_worker_args(ns.worker_args)
            ns.worker_args = worker_args
            self.worker_test_name = test_name

        # Strip .py extensions.
        removepy(ns.args)

        ikiwa ns.huntrleaks:
            warmup, repetitions, _ = ns.huntrleaks
            ikiwa warmup < 1 ama repetitions < 1:
                msg = ("Invalid values kila the --huntrleaks/-R parameters. The "
                       "number of warmups na repetitions must be at least 1 "
                       "each (1:1).")
                andika(msg, file=sys.stderr, flush=Kweli)
                sys.exit(2)

        ikiwa ns.tempdir:
            ns.tempdir = os.path.expanduser(ns.tempdir)

        self.ns = ns

    eleza find_tests(self, tests):
        self.tests = tests

        ikiwa self.ns.single:
            self.next_single_filename = os.path.join(self.tmp_dir, 'pynexttest')
            jaribu:
                ukijumuisha open(self.next_single_filename, 'r') as fp:
                    next_test = fp.read().strip()
                    self.tests = [next_test]
            except OSError:
                pass

        ikiwa self.ns.fromfile:
            self.tests = []
            # regex to match 'test_builtin' kwenye line:
            # '0:00:00 [  4/400] test_builtin -- test_dict took 1 sec'
            regex = re.compile(r'\btest_[a-zA-Z0-9_]+\b')
            ukijumuisha open(os.path.join(support.SAVEDCWD, self.ns.fromfile)) as fp:
                kila line kwenye fp:
                    line = line.split('#', 1)[0]
                    line = line.strip()
                    match = regex.search(line)
                    ikiwa match ni sio Tupu:
                        self.tests.append(match.group())

        removepy(self.tests)

        ikiwa self.ns.pgo:
            # add default PGO tests ikiwa no tests are specified
            setup_pgo_tests(self.ns)

        stdtests = STDTESTS[:]
        nottests = NOTTESTS.copy()
        ikiwa self.ns.exclude:
            kila arg kwenye self.ns.args:
                ikiwa arg kwenye stdtests:
                    stdtests.remove(arg)
                nottests.add(arg)
            self.ns.args = []

        # ikiwa testdir ni set, then we are sio running the python tests suite, so
        # don't add default tests to be executed ama skipped (pass empty values)
        ikiwa self.ns.testdir:
            alltests = findtests(self.ns.testdir, list(), set())
        isipokua:
            alltests = findtests(self.ns.testdir, stdtests, nottests)

        ikiwa sio self.ns.fromfile:
            self.selected = self.tests ama self.ns.args ama alltests
        isipokua:
            self.selected = self.tests
        ikiwa self.ns.single:
            self.selected = self.selected[:1]
            jaribu:
                pos = alltests.index(self.selected[0])
                self.next_single_test = alltests[pos + 1]
            except IndexError:
                pass

        # Remove all the selected tests that precede start ikiwa it's set.
        ikiwa self.ns.start:
            jaribu:
                toa self.selected[:self.selected.index(self.ns.start)]
            except ValueError:
                andika("Couldn't find starting test (%s), using all tests"
                      % self.ns.start, file=sys.stderr)

        ikiwa self.ns.randomize:
            ikiwa self.ns.random_seed ni Tupu:
                self.ns.random_seed = random.randrange(10000000)
            random.seed(self.ns.random_seed)
            random.shuffle(self.selected)

    eleza list_tests(self):
        kila name kwenye self.selected:
            andika(name)

    eleza _list_cases(self, suite):
        kila test kwenye suite:
            ikiwa isinstance(test, unittest.loader._FailedTest):
                endelea
            ikiwa isinstance(test, unittest.TestSuite):
                self._list_cases(test)
            elikiwa isinstance(test, unittest.TestCase):
                ikiwa support.match_test(test):
                    andika(test.id())

    eleza list_cases(self):
        support.verbose = Uongo
        support.set_match_tests(self.ns.match_tests)

        kila test_name kwenye self.selected:
            abstest = get_abs_module(self.ns, test_name)
            jaribu:
                suite = unittest.defaultTestLoader.loadTestsFromName(abstest)
                self._list_cases(suite)
            except unittest.SkipTest:
                self.skipped.append(test_name)

        ikiwa self.skipped:
            andika(file=sys.stderr)
            andika(count(len(self.skipped), "test"), "skipped:", file=sys.stderr)
            printlist(self.skipped, file=sys.stderr)

    eleza rerun_failed_tests(self):
        self.ns.verbose = Kweli
        self.ns.failfast = Uongo
        self.ns.verbose3 = Uongo

        self.first_result = self.get_tests_result()

        self.log()
        self.log("Re-running failed tests kwenye verbose mode")
        self.rerun = self.bad[:]
        kila test_name kwenye self.rerun:
            self.log(f"Re-running {test_name} kwenye verbose mode")
            self.ns.verbose = Kweli
            result = runtest(self.ns, test_name)

            self.accumulate_result(result, rerun=Kweli)

            ikiwa result.result == INTERRUPTED:
                koma

        ikiwa self.bad:
            andika(count(len(self.bad), 'test'), "failed again:")
            printlist(self.bad)

        self.display_result()

    eleza display_result(self):
        # If running the test suite kila PGO then no one cares about results.
        ikiwa self.ns.pgo:
            return

        andika()
        andika("== Tests result: %s ==" % self.get_tests_result())

        ikiwa self.interrupted:
            andika("Test suite interrupted by signal SIGINT.")

        omitted = set(self.selected) - self.get_executed()
        ikiwa omitted:
            andika()
            andika(count(len(omitted), "test"), "omitted:")
            printlist(omitted)

        ikiwa self.good na sio self.ns.quiet:
            andika()
            ikiwa (not self.bad
                na sio self.skipped
                na sio self.interrupted
                na len(self.good) > 1):
                andika("All", end=' ')
            andika(count(len(self.good), "test"), "OK.")

        ikiwa self.ns.print_slow:
            self.test_times.sort(reverse=Kweli)
            andika()
            andika("10 slowest tests:")
            kila test_time, test kwenye self.test_times[:10]:
                andika("- %s: %s" % (test, format_duration(test_time)))

        ikiwa self.bad:
            andika()
            andika(count(len(self.bad), "test"), "failed:")
            printlist(self.bad)

        ikiwa self.environment_changed:
            andika()
            andika("{} altered the execution environment:".format(
                     count(len(self.environment_changed), "test")))
            printlist(self.environment_changed)

        ikiwa self.skipped na sio self.ns.quiet:
            andika()
            andika(count(len(self.skipped), "test"), "skipped:")
            printlist(self.skipped)

        ikiwa self.rerun:
            andika()
            andika("%s:" % count(len(self.rerun), "re-run test"))
            printlist(self.rerun)

        ikiwa self.run_no_tests:
            andika()
            andika(count(len(self.run_no_tests), "test"), "run no tests:")
            printlist(self.run_no_tests)

    eleza run_tests_sequential(self):
        ikiwa self.ns.trace:
            agiza trace
            self.tracer = trace.Trace(trace=Uongo, count=Kweli)

        save_modules = sys.modules.keys()

        self.log("Run tests sequentially")

        previous_test = Tupu
        kila test_index, test_name kwenye enumerate(self.tests, 1):
            start_time = time.monotonic()

            text = test_name
            ikiwa previous_test:
                text = '%s -- %s' % (text, previous_test)
            self.display_progress(test_index, text)

            ikiwa self.tracer:
                # If we're tracing code coverage, then we don't exit ukijumuisha status
                # ikiwa on a false rudisha value kutoka main.
                cmd = ('result = runtest(self.ns, test_name); '
                       'self.accumulate_result(result)')
                ns = dict(locals())
                self.tracer.runctx(cmd, globals=globals(), locals=ns)
                result = ns['result']
            isipokua:
                result = runtest(self.ns, test_name)
                self.accumulate_result(result)

            ikiwa result.result == INTERRUPTED:
                koma

            previous_test = format_test_result(result)
            test_time = time.monotonic() - start_time
            ikiwa test_time >= PROGRESS_MIN_TIME:
                previous_test = "%s kwenye %s" % (previous_test, format_duration(test_time))
            elikiwa result.result == PASSED:
                # be quiet: say nothing ikiwa the test passed shortly
                previous_test = Tupu

            # Unload the newly imported modules (best effort finalization)
            kila module kwenye sys.modules.keys():
                ikiwa module sio kwenye save_modules na module.startswith("test."):
                    support.unload(module)

            ikiwa self.ns.failfast na is_failed(result, self.ns):
                koma

        ikiwa previous_test:
            andika(previous_test)

    eleza _test_forever(self, tests):
        wakati Kweli:
            kila test_name kwenye tests:
                tuma test_name
                ikiwa self.bad:
                    return
                ikiwa self.ns.fail_env_changed na self.environment_changed:
                    return

    eleza display_header(self):
        # Print basic platform information
        andika("==", platform.python_implementation(), *sys.version.split())
        andika("==", platform.platform(aliased=Kweli),
                      "%s-endian" % sys.byteorder)
        andika("== cwd:", os.getcwd())
        cpu_count = os.cpu_count()
        ikiwa cpu_count:
            andika("== CPU count:", cpu_count)
        andika("== encodings: locale=%s, FS=%s"
              % (locale.getpreferredencoding(Uongo),
                 sys.getfilesystemencoding()))

    eleza get_tests_result(self):
        result = []
        ikiwa self.bad:
            result.append("FAILURE")
        elikiwa self.ns.fail_env_changed na self.environment_changed:
            result.append("ENV CHANGED")
        elikiwa sio any((self.good, self.bad, self.skipped, self.interrupted,
            self.environment_changed)):
            result.append("NO TEST RUN")

        ikiwa self.interrupted:
            result.append("INTERRUPTED")

        ikiwa sio result:
            result.append("SUCCESS")

        result = ', '.join(result)
        ikiwa self.first_result:
            result = '%s then %s' % (self.first_result, result)
        rudisha result

    eleza run_tests(self):
        # For a partial run, we do sio need to clutter the output.
        ikiwa (self.ns.header
            ama not(self.ns.pgo ama self.ns.quiet ama self.ns.single
                   ama self.tests ama self.ns.args)):
            self.display_header()

        ikiwa self.ns.huntrleaks:
            warmup, repetitions, _ = self.ns.huntrleaks
            ikiwa warmup < 3:
                msg = ("WARNING: Running tests ukijumuisha --huntrleaks/-R na less than "
                        "3 warmup repetitions can give false positives!")
                andika(msg, file=sys.stdout, flush=Kweli)

        ikiwa self.ns.randomize:
            andika("Using random seed", self.ns.random_seed)

        ikiwa self.ns.forever:
            self.tests = self._test_forever(list(self.selected))
            self.test_count = ''
            self.test_count_width = 3
        isipokua:
            self.tests = iter(self.selected)
            self.test_count = '/{}'.format(len(self.selected))
            self.test_count_width = len(self.test_count) - 1

        ikiwa self.ns.use_mp:
            kutoka test.libregrtest.runtest_mp agiza run_tests_multiprocess
            run_tests_multiprocess(self)
        isipokua:
            self.run_tests_sequential()

    eleza finalize(self):
        ikiwa self.next_single_filename:
            ikiwa self.next_single_test:
                ukijumuisha open(self.next_single_filename, 'w') as fp:
                    fp.write(self.next_single_test + '\n')
            isipokua:
                os.unlink(self.next_single_filename)

        ikiwa self.tracer:
            r = self.tracer.results()
            r.write_results(show_missing=Kweli, summary=Kweli,
                            coverdir=self.ns.coverdir)

        andika()
        duration = time.monotonic() - self.start_time
        andika("Total duration: %s" % format_duration(duration))
        andika("Tests result: %s" % self.get_tests_result())

        ikiwa self.ns.runleaks:
            os.system("leaks %d" % os.getpid())

    eleza save_xml_result(self):
        ikiwa sio self.ns.xmlpath na sio self.testsuite_xml:
            return

        agiza xml.etree.ElementTree as ET
        root = ET.Element("testsuites")

        # Manually count the totals kila the overall summary
        totals = {'tests': 0, 'errors': 0, 'failures': 0}
        kila suite kwenye self.testsuite_xml:
            root.append(suite)
            kila k kwenye totals:
                jaribu:
                    totals[k] += int(suite.get(k, 0))
                except ValueError:
                    pass

        kila k, v kwenye totals.items():
            root.set(k, str(v))

        xmlpath = os.path.join(support.SAVEDCWD, self.ns.xmlpath)
        ukijumuisha open(xmlpath, 'wb') as f:
            kila s kwenye ET.tostringlist(root):
                f.write(s)

    eleza set_temp_dir(self):
        ikiwa self.ns.tempdir:
            self.tmp_dir = self.ns.tempdir

        ikiwa sio self.tmp_dir:
            # When tests are run kutoka the Python build directory, it ni best practice
            # to keep the test files kwenye a subfolder.  This eases the cleanup of leftover
            # files using the "make distclean" command.
            ikiwa sysconfig.is_python_build():
                self.tmp_dir = sysconfig.get_config_var('abs_builddir')
                ikiwa self.tmp_dir ni Tupu:
                    # bpo-30284: On Windows, only srcdir ni available. Using
                    # abs_builddir mostly matters on UNIX when building Python
                    # out of the source tree, especially when the source tree
                    # ni read only.
                    self.tmp_dir = sysconfig.get_config_var('srcdir')
                self.tmp_dir = os.path.join(self.tmp_dir, 'build')
            isipokua:
                self.tmp_dir = tempfile.gettempdir()

        self.tmp_dir = os.path.abspath(self.tmp_dir)

    eleza create_temp_dir(self):
        os.makedirs(self.tmp_dir, exist_ok=Kweli)

        # Define a writable temp dir that will be used as cwd wakati running
        # the tests. The name of the dir includes the pid to allow parallel
        # testing (see the -j option).
        pid = os.getpid()
        ikiwa self.worker_test_name ni sio Tupu:
            test_cwd = 'test_python_worker_{}'.format(pid)
        isipokua:
            test_cwd = 'test_python_{}'.format(pid)
        test_cwd = os.path.join(self.tmp_dir, test_cwd)
        rudisha test_cwd

    eleza cleanup(self):
        agiza glob

        path = os.path.join(self.tmp_dir, 'test_python_*')
        andika("Cleanup %s directory" % self.tmp_dir)
        kila name kwenye glob.glob(path):
            ikiwa os.path.isdir(name):
                andika("Remove directory: %s" % name)
                support.rmtree(name)
            isipokua:
                andika("Remove file: %s" % name)
                support.unlink(name)

    eleza main(self, tests=Tupu, **kwargs):
        self.parse_args(kwargs)

        self.set_temp_dir()

        ikiwa self.ns.cleanup:
            self.cleanup()
            sys.exit(0)

        test_cwd = self.create_temp_dir()

        jaribu:
            # Run the tests kwenye a context manager that temporarily changes the CWD
            # to a temporary na writable directory. If it's sio possible to
            # create ama change the CWD, the original CWD will be used.
            # The original CWD ni available kutoka support.SAVEDCWD.
            ukijumuisha support.temp_cwd(test_cwd, quiet=Kweli):
                # When using multiprocessing, worker processes will use test_cwd
                # as their parent temporary directory. So when the main process
                # exit, it removes also subdirectories of worker processes.
                self.ns.tempdir = test_cwd

                self._main(tests, kwargs)
        except SystemExit as exc:
            # bpo-38203: Python can hang at exit kwenye Py_Finalize(), especially
            # on threading._shutdown() call: put a timeout
            faulthandler.dump_traceback_later(EXIT_TIMEOUT, exit=Kweli)

            sys.exit(exc.code)

    eleza getloadavg(self):
        ikiwa self.win_load_tracker ni sio Tupu:
            rudisha self.win_load_tracker.getloadavg()

        ikiwa hasattr(os, 'getloadavg'):
            rudisha os.getloadavg()[0]

        rudisha Tupu

    eleza _main(self, tests, kwargs):
        ikiwa self.worker_test_name ni sio Tupu:
            kutoka test.libregrtest.runtest_mp agiza run_tests_worker
            run_tests_worker(self.ns, self.worker_test_name)

        ikiwa self.ns.wait:
            uliza("Press any key to endelea...")

        support.PGO = self.ns.pgo
        support.PGO_EXTENDED = self.ns.pgo_extended

        setup_tests(self.ns)

        self.find_tests(tests)

        ikiwa self.ns.list_tests:
            self.list_tests()
            sys.exit(0)

        ikiwa self.ns.list_cases:
            self.list_cases()
            sys.exit(0)

        # If we're on windows na this ni the parent runner (not a worker),
        # track the load average.
        ikiwa sys.platform == 'win32' na self.worker_test_name ni Tupu:
            kutoka test.libregrtest.win_utils agiza WindowsLoadTracker

            jaribu:
                self.win_load_tracker = WindowsLoadTracker()
            except FileNotFoundError as error:
                # Windows IoT Core na Windows Nano Server do sio provide
                # typeperf.exe kila x64, x86 ama ARM
                andika(f'Failed to create WindowsLoadTracker: {error}')

        jaribu:
            self.run_tests()
            self.display_result()

            ikiwa self.ns.verbose2 na self.bad:
                self.rerun_failed_tests()
        mwishowe:
            ikiwa self.win_load_tracker ni sio Tupu:
                self.win_load_tracker.close()
                self.win_load_tracker = Tupu

        self.finalize()

        self.save_xml_result()

        ikiwa self.bad:
            sys.exit(2)
        ikiwa self.interrupted:
            sys.exit(130)
        ikiwa self.ns.fail_env_changed na self.environment_changed:
            sys.exit(3)
        sys.exit(0)


eleza main(tests=Tupu, **kwargs):
    """Run the Python suite."""
    Regrtest().main(tests=tests, **kwargs)
