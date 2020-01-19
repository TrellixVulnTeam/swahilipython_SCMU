agiza collections
agiza faulthandler
agiza functools
agiza gc
agiza importlib
agiza io
agiza os
agiza sys
agiza time
agiza traceback
agiza unittest

kutoka test agiza support
kutoka test.libregrtest.refleak agiza dash_R, clear_caches
kutoka test.libregrtest.save_env agiza saved_test_environment
kutoka test.libregrtest.utils agiza format_duration, print_warning


# Test result constants.
PASSED = 1
FAILED = 0
ENV_CHANGED = -1
SKIPPED = -2
RESOURCE_DENIED = -3
INTERRUPTED = -4
CHILD_ERROR = -5   # error kwenye a child process
TEST_DID_NOT_RUN = -6
TIMEOUT = -7

_FORMAT_TEST_RESULT = {
    PASSED: '%s pitaed',
    FAILED: '%s failed',
    ENV_CHANGED: '%s failed (env changed)',
    SKIPPED: '%s skipped',
    RESOURCE_DENIED: '%s skipped (resource denied)',
    INTERRUPTED: '%s interrupted',
    CHILD_ERROR: '%s crashed',
    TEST_DID_NOT_RUN: '%s run no tests',
    TIMEOUT: '%s timed out',
}

# Minimum duration of a test to display its duration ama to mention that
# the test ni running kwenye background
PROGRESS_MIN_TIME = 30.0   # seconds

# small set of tests to determine ikiwa we have a basically functioning interpreter
# (i.e. ikiwa any of these fail, then anything isipokua ni likely to follow)
STDTESTS = [
    'test_grammar',
    'test_opcodes',
    'test_dict',
    'test_builtin',
    'test_exceptions',
    'test_types',
    'test_unittest',
    'test_doctest',
    'test_doctest2',
    'test_support'
]

# set of tests that we don't want to be executed when using regrtest
NOTTESTS = set()


# used by --findleaks, store kila gc.garbage
FOUND_GARBAGE = []


eleza is_failed(result, ns):
    ok = result.result
    ikiwa ok kwenye (PASSED, RESOURCE_DENIED, SKIPPED, TEST_DID_NOT_RUN):
        rudisha Uongo
    ikiwa ok == ENV_CHANGED:
        rudisha ns.fail_env_changed
    rudisha Kweli


eleza format_test_result(result):
    fmt = _FORMAT_TEST_RESULT.get(result.result, "%s")
    text = fmt % result.test_name
    ikiwa result.result == TIMEOUT:
        text = '%s (%s)' % (text, format_duration(result.test_time))
    rudisha text


eleza findtestdir(path=Tupu):
    rudisha path ama os.path.dirname(os.path.dirname(__file__)) ama os.curdir


eleza findtests(testdir=Tupu, stdtests=STDTESTS, nottests=NOTTESTS):
    """Return a list of all applicable test modules."""
    testdir = findtestdir(testdir)
    names = os.listdir(testdir)
    tests = []
    others = set(stdtests) | nottests
    kila name kwenye names:
        mod, ext = os.path.splitext(name)
        ikiwa mod[:5] == "test_" na ext kwenye (".py", "") na mod haiko kwenye others:
            tests.append(mod)
    rudisha stdtests + sorted(tests)


eleza get_abs_module(ns, test_name):
    ikiwa test_name.startswith('test.') ama ns.testdir:
        rudisha test_name
    isipokua:
        # Import it kutoka the test package
        rudisha 'test.' + test_name


TestResult = collections.namedtuple('TestResult',
    'test_name result test_time xml_data')

eleza _runtest(ns, test_name):
    # Handle faulthandler timeout, capture stdout+stderr, XML serialization
    # na measure time.

    output_on_failure = ns.verbose3

    use_timeout = (ns.timeout ni sio Tupu)
    ikiwa use_timeout:
        faulthandler.dump_traceback_later(ns.timeout, exit=Kweli)

    start_time = time.perf_counter()
    jaribu:
        support.set_match_tests(ns.match_tests)
        support.junit_xml_list = xml_list = [] ikiwa ns.xmlpath isipokua Tupu
        ikiwa ns.failfast:
            support.failfast = Kweli

        ikiwa output_on_failure:
            support.verbose = Kweli

            stream = io.StringIO()
            orig_stdout = sys.stdout
            orig_stderr = sys.stderr
            jaribu:
                sys.stdout = stream
                sys.stderr = stream
                result = _runtest_inner(ns, test_name,
                                        display_failure=Uongo)
                ikiwa result != PASSED:
                    output = stream.getvalue()
                    orig_stderr.write(output)
                    orig_stderr.flush()
            mwishowe:
                sys.stdout = orig_stdout
                sys.stderr = orig_stderr
        isipokua:
            # Tell tests to be moderately quiet
            support.verbose = ns.verbose

            result = _runtest_inner(ns, test_name,
                                    display_failure=sio ns.verbose)

        ikiwa xml_list:
            agiza xml.etree.ElementTree kama ET
            xml_data = [ET.tostring(x).decode('us-ascii') kila x kwenye xml_list]
        isipokua:
            xml_data = Tupu

        test_time = time.perf_counter() - start_time

        rudisha TestResult(test_name, result, test_time, xml_data)
    mwishowe:
        ikiwa use_timeout:
            faulthandler.cancel_dump_traceback_later()
        support.junit_xml_list = Tupu


eleza runtest(ns, test_name):
    """Run a single test.

    ns -- regrtest namespace of options
    test_name -- the name of the test

    Returns the tuple (result, test_time, xml_data), where result ni one
    of the constants:

        INTERRUPTED      KeyboardInterrupt
        RESOURCE_DENIED  test skipped because resource denied
        SKIPPED          test skipped kila some other reason
        ENV_CHANGED      test failed because it changed the execution environment
        FAILED           test failed
        PASSED           test pitaed
        EMPTY_TEST_SUITE test ran no subtests.
        TIMEOUT          test timed out.

    If ns.xmlpath ni sio Tupu, xml_data ni a list containing each
    generated testsuite element.
    """
    jaribu:
        rudisha _runtest(ns, test_name)
    tatizo:
        ikiwa sio ns.pgo:
            msg = traceback.format_exc()
            andika(f"test {test_name} crashed -- {msg}",
                  file=sys.stderr, flush=Kweli)
        rudisha TestResult(test_name, FAILED, 0.0, Tupu)


eleza _test_module(the_module):
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromModule(the_module)
    kila error kwenye loader.errors:
        andika(error, file=sys.stderr)
    ikiwa loader.errors:
        ashiria Exception("errors wakati loading tests")
    support.run_unittest(tests)


eleza _runtest_inner2(ns, test_name):
    # Load the test function, run the test function, handle huntrleaks
    # na findleaks to detect leaks

    abstest = get_abs_module(ns, test_name)

    # remove the module kutoka sys.module to reload it ikiwa it was already imported
    support.unload(abstest)

    the_module = importlib.import_module(abstest)

    # If the test has a test_main, that will run the appropriate
    # tests.  If not, use normal unittest test loading.
    test_runner = getattr(the_module, "test_main", Tupu)
    ikiwa test_runner ni Tupu:
        test_runner = functools.partial(_test_module, the_module)

    jaribu:
        ikiwa ns.huntrleaks:
            # Return Kweli ikiwa the test leaked references
            refleak = dash_R(ns, test_name, test_runner)
        isipokua:
            test_runner()
            refleak = Uongo
    mwishowe:
        cleanup_test_droppings(test_name, ns.verbose)

    support.gc_collect()

    ikiwa gc.garbage:
        support.environment_altered = Kweli
        print_warning(f"{test_name} created {len(gc.garbage)} "
                      f"uncollectable object(s).")

        # move the uncollectable objects somewhere,
        # so we don't see them again
        FOUND_GARBAGE.extend(gc.garbage)
        gc.garbage.clear()

    support.reap_children()

    rudisha refleak


eleza _runtest_inner(ns, test_name, display_failure=Kweli):
    # Detect environment changes, handle exceptions.

    # Reset the environment_altered flag to detect ikiwa a test altered
    # the environment
    support.environment_altered = Uongo

    ikiwa ns.pgo:
        display_failure = Uongo

    jaribu:
        clear_caches()

        ukijumuisha saved_test_environment(test_name, ns.verbose, ns.quiet, pgo=ns.pgo) kama environment:
            refleak = _runtest_inner2(ns, test_name)
    tatizo support.ResourceDenied kama msg:
        ikiwa sio ns.quiet na sio ns.pgo:
            andika(f"{test_name} skipped -- {msg}", flush=Kweli)
        rudisha RESOURCE_DENIED
    tatizo unittest.SkipTest kama msg:
        ikiwa sio ns.quiet na sio ns.pgo:
            andika(f"{test_name} skipped -- {msg}", flush=Kweli)
        rudisha SKIPPED
    tatizo support.TestFailed kama exc:
        msg = f"test {test_name} failed"
        ikiwa display_failure:
            msg = f"{msg} -- {exc}"
        andika(msg, file=sys.stderr, flush=Kweli)
        rudisha FAILED
    tatizo support.TestDidNotRun:
        rudisha TEST_DID_NOT_RUN
    tatizo KeyboardInterrupt:
        andika()
        rudisha INTERRUPTED
    tatizo:
        ikiwa sio ns.pgo:
            msg = traceback.format_exc()
            andika(f"test {test_name} crashed -- {msg}",
                  file=sys.stderr, flush=Kweli)
        rudisha FAILED

    ikiwa refleak:
        rudisha FAILED
    ikiwa environment.changed:
        rudisha ENV_CHANGED
    rudisha PASSED


eleza cleanup_test_droppings(test_name, verbose):
    # First kill any dangling references to open files etc.
    # This can also issue some ResourceWarnings which would otherwise get
    # triggered during the following test run, na possibly produce failures.
    support.gc_collect()

    # Try to clean up junk commonly left behind.  While tests shouldn't leave
    # any files ama directories behind, when a test fails that can be tedious
    # kila it to arrange.  The consequences can be especially nasty on Windows,
    # since ikiwa a test leaves a file open, it cannot be deleted by name (while
    # there's nothing we can do about that here either, we can display the
    # name of the offending test, which ni a real help).
    kila name kwenye (support.TESTFN,):
        ikiwa sio os.path.exists(name):
            endelea

        ikiwa os.path.isdir(name):
            agiza shutil
            kind, nuker = "directory", shutil.rmtree
        lasivyo os.path.isfile(name):
            kind, nuker = "file", os.unlink
        isipokua:
            ashiria RuntimeError(f"os.path says {name!r} exists but ni neither "
                               f"directory nor file")

        ikiwa verbose:
            print_warning("%r left behind %s %r" % (test_name, kind, name))
            support.environment_altered = Kweli

        jaribu:
            agiza stat
            # fix possible permissions problems that might prevent cleanup
            os.chmod(name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            nuker(name)
        tatizo Exception kama exc:
            print_warning(f"{test_name} left behind {kind} {name!r} "
                          f"and it couldn't be removed: {exc}")
