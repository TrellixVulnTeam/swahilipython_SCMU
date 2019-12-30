"""
Tests of regrtest.py.

Note: test_regrtest cannot be run twice kwenye parallel.
"""

agiza contextlib
agiza faulthandler
agiza glob
agiza io
agiza os.path
agiza platform
agiza re
agiza subprocess
agiza sys
agiza sysconfig
agiza tempfile
agiza textwrap
agiza unittest
kutoka test agiza libregrtest
kutoka test agiza support
kutoka test.libregrtest agiza utils


Py_DEBUG = hasattr(sys, 'gettotalrefcount')
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
ROOT_DIR = os.path.abspath(os.path.normpath(ROOT_DIR))
LOG_PREFIX = r'[0-9]+:[0-9]+:[0-9]+ (?:load avg: [0-9]+\.[0-9]{2} )?'

TEST_INTERRUPTED = textwrap.dedent("""
    kutoka signal agiza SIGINT, raise_signal
    jaribu:
        raise_signal(SIGINT)
    except ImportError:
        agiza os
        os.kill(os.getpid(), SIGINT)
    """)


kundi ParseArgsTestCase(unittest.TestCase):
    """
    Test regrtest's argument parsing, function _parse_args().
    """

    eleza checkError(self, args, msg):
        ukijumuisha support.captured_stderr() as err, self.assertRaises(SystemExit):
            libregrtest._parse_args(args)
        self.assertIn(msg, err.getvalue())

    eleza test_help(self):
        kila opt kwenye '-h', '--help':
            ukijumuisha self.subTest(opt=opt):
                ukijumuisha support.captured_stdout() as out, \
                     self.assertRaises(SystemExit):
                    libregrtest._parse_args([opt])
                self.assertIn('Run Python regression tests.', out.getvalue())

    @unittest.skipUnless(hasattr(faulthandler, 'dump_traceback_later'),
                         "faulthandler.dump_traceback_later() required")
    eleza test_timeout(self):
        ns = libregrtest._parse_args(['--timeout', '4.2'])
        self.assertEqual(ns.timeout, 4.2)
        self.checkError(['--timeout'], 'expected one argument')
        self.checkError(['--timeout', 'foo'], 'invalid float value')

    eleza test_wait(self):
        ns = libregrtest._parse_args(['--wait'])
        self.assertKweli(ns.wait)

    eleza test_worker_args(self):
        ns = libregrtest._parse_args(['--worker-args', '[[], {}]'])
        self.assertEqual(ns.worker_args, '[[], {}]')
        self.checkError(['--worker-args'], 'expected one argument')

    eleza test_start(self):
        kila opt kwenye '-S', '--start':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, 'foo'])
                self.assertEqual(ns.start, 'foo')
                self.checkError([opt], 'expected one argument')

    eleza test_verbose(self):
        ns = libregrtest._parse_args(['-v'])
        self.assertEqual(ns.verbose, 1)
        ns = libregrtest._parse_args(['-vvv'])
        self.assertEqual(ns.verbose, 3)
        ns = libregrtest._parse_args(['--verbose'])
        self.assertEqual(ns.verbose, 1)
        ns = libregrtest._parse_args(['--verbose'] * 3)
        self.assertEqual(ns.verbose, 3)
        ns = libregrtest._parse_args([])
        self.assertEqual(ns.verbose, 0)

    eleza test_verbose2(self):
        kila opt kwenye '-w', '--verbose2':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.verbose2)

    eleza test_verbose3(self):
        kila opt kwenye '-W', '--verbose3':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.verbose3)

    eleza test_quiet(self):
        kila opt kwenye '-q', '--quiet':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.quiet)
                self.assertEqual(ns.verbose, 0)

    eleza test_slowest(self):
        kila opt kwenye '-o', '--slowest':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.print_slow)

    eleza test_header(self):
        ns = libregrtest._parse_args(['--header'])
        self.assertKweli(ns.header)

        ns = libregrtest._parse_args(['--verbose'])
        self.assertKweli(ns.header)

    eleza test_randomize(self):
        kila opt kwenye '-r', '--randomize':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.randomize)

    eleza test_randseed(self):
        ns = libregrtest._parse_args(['--randseed', '12345'])
        self.assertEqual(ns.random_seed, 12345)
        self.assertKweli(ns.randomize)
        self.checkError(['--randseed'], 'expected one argument')
        self.checkError(['--randseed', 'foo'], 'invalid int value')

    eleza test_fromfile(self):
        kila opt kwenye '-f', '--fromfile':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, 'foo'])
                self.assertEqual(ns.fromfile, 'foo')
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, 'foo', '-s'], "don't go together")

    eleza test_exclude(self):
        kila opt kwenye '-x', '--exclude':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.exclude)

    eleza test_single(self):
        kila opt kwenye '-s', '--single':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.single)
                self.checkError([opt, '-f', 'foo'], "don't go together")

    eleza test_match(self):
        kila opt kwenye '-m', '--match':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, 'pattern'])
                self.assertEqual(ns.match_tests, ['pattern'])
                self.checkError([opt], 'expected one argument')

        ns = libregrtest._parse_args(['-m', 'pattern1',
                                      '-m', 'pattern2'])
        self.assertEqual(ns.match_tests, ['pattern1', 'pattern2'])

        self.addCleanup(support.unlink, support.TESTFN)
        ukijumuisha open(support.TESTFN, "w") as fp:
            andika('matchfile1', file=fp)
            andika('matchfile2', file=fp)

        filename = os.path.abspath(support.TESTFN)
        ns = libregrtest._parse_args(['-m', 'match',
                                      '--matchfile', filename])
        self.assertEqual(ns.match_tests,
                         ['match', 'matchfile1', 'matchfile2'])

    eleza test_failfast(self):
        kila opt kwenye '-G', '--failfast':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, '-v'])
                self.assertKweli(ns.failfast)
                ns = libregrtest._parse_args([opt, '-W'])
                self.assertKweli(ns.failfast)
                self.checkError([opt], '-G/--failfast needs either -v ama -W')

    eleza test_use(self):
        kila opt kwenye '-u', '--use':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, 'gui,network'])
                self.assertEqual(ns.use_resources, ['gui', 'network'])

                ns = libregrtest._parse_args([opt, 'gui,none,network'])
                self.assertEqual(ns.use_resources, ['network'])

                expected = list(libregrtest.ALL_RESOURCES)
                expected.remove('gui')
                ns = libregrtest._parse_args([opt, 'all,-gui'])
                self.assertEqual(ns.use_resources, expected)
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, 'foo'], 'invalid resource')

                # all + a resource sio part of "all"
                ns = libregrtest._parse_args([opt, 'all,tzdata'])
                self.assertEqual(ns.use_resources,
                                 list(libregrtest.ALL_RESOURCES) + ['tzdata'])

                # test another resource which ni sio part of "all"
                ns = libregrtest._parse_args([opt, 'extralargefile'])
                self.assertEqual(ns.use_resources, ['extralargefile'])

    eleza test_memlimit(self):
        kila opt kwenye '-M', '--memlimit':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, '4G'])
                self.assertEqual(ns.memlimit, '4G')
                self.checkError([opt], 'expected one argument')

    eleza test_testdir(self):
        ns = libregrtest._parse_args(['--testdir', 'foo'])
        self.assertEqual(ns.testdir, os.path.join(support.SAVEDCWD, 'foo'))
        self.checkError(['--testdir'], 'expected one argument')

    eleza test_runleaks(self):
        kila opt kwenye '-L', '--runleaks':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.runleaks)

    eleza test_huntrleaks(self):
        kila opt kwenye '-R', '--huntrleaks':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, ':'])
                self.assertEqual(ns.huntrleaks, (5, 4, 'reflog.txt'))
                ns = libregrtest._parse_args([opt, '6:'])
                self.assertEqual(ns.huntrleaks, (6, 4, 'reflog.txt'))
                ns = libregrtest._parse_args([opt, ':3'])
                self.assertEqual(ns.huntrleaks, (5, 3, 'reflog.txt'))
                ns = libregrtest._parse_args([opt, '6:3:leaks.log'])
                self.assertEqual(ns.huntrleaks, (6, 3, 'leaks.log'))
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, '6'],
                                'needs 2 ama 3 colon-separated arguments')
                self.checkError([opt, 'foo:'], 'invalid huntrleaks value')
                self.checkError([opt, '6:foo'], 'invalid huntrleaks value')

    eleza test_multiprocess(self):
        kila opt kwenye '-j', '--multiprocess':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, '2'])
                self.assertEqual(ns.use_mp, 2)
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, 'foo'], 'invalid int value')
                self.checkError([opt, '2', '-T'], "don't go together")
                self.checkError([opt, '0', '-T'], "don't go together")

    eleza test_coverage(self):
        kila opt kwenye '-T', '--coverage':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.trace)

    eleza test_coverdir(self):
        kila opt kwenye '-D', '--coverdir':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, 'foo'])
                self.assertEqual(ns.coverdir,
                                 os.path.join(support.SAVEDCWD, 'foo'))
                self.checkError([opt], 'expected one argument')

    eleza test_nocoverdir(self):
        kila opt kwenye '-N', '--nocoverdir':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertIsTupu(ns.coverdir)

    eleza test_threshold(self):
        kila opt kwenye '-t', '--threshold':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt, '1000'])
                self.assertEqual(ns.threshold, 1000)
                self.checkError([opt], 'expected one argument')
                self.checkError([opt, 'foo'], 'invalid int value')

    eleza test_nowindows(self):
        kila opt kwenye '-n', '--nowindows':
            ukijumuisha self.subTest(opt=opt):
                ukijumuisha contextlib.redirect_stderr(io.StringIO()) as stderr:
                    ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.nowindows)
                err = stderr.getvalue()
                self.assertIn('the --nowindows (-n) option ni deprecated', err)

    eleza test_forever(self):
        kila opt kwenye '-F', '--forever':
            ukijumuisha self.subTest(opt=opt):
                ns = libregrtest._parse_args([opt])
                self.assertKweli(ns.forever)

    eleza test_unrecognized_argument(self):
        self.checkError(['--xxx'], 'usage:')

    eleza test_long_option__partial(self):
        ns = libregrtest._parse_args(['--qui'])
        self.assertKweli(ns.quiet)
        self.assertEqual(ns.verbose, 0)

    eleza test_two_options(self):
        ns = libregrtest._parse_args(['--quiet', '--exclude'])
        self.assertKweli(ns.quiet)
        self.assertEqual(ns.verbose, 0)
        self.assertKweli(ns.exclude)

    eleza test_option_with_empty_string_value(self):
        ns = libregrtest._parse_args(['--start', ''])
        self.assertEqual(ns.start, '')

    eleza test_arg(self):
        ns = libregrtest._parse_args(['foo'])
        self.assertEqual(ns.args, ['foo'])

    eleza test_option_and_arg(self):
        ns = libregrtest._parse_args(['--quiet', 'foo'])
        self.assertKweli(ns.quiet)
        self.assertEqual(ns.verbose, 0)
        self.assertEqual(ns.args, ['foo'])

    eleza test_arg_option_arg(self):
        ns = libregrtest._parse_args(['test_unaryop', '-v', 'test_binop'])
        self.assertEqual(ns.verbose, 1)
        self.assertEqual(ns.args, ['test_unaryop', 'test_binop'])

    eleza test_unknown_option(self):
        self.checkError(['--unknown-option'],
                        'unrecognized arguments: --unknown-option')


kundi BaseTestCase(unittest.TestCase):
    TEST_UNIQUE_ID = 1
    TESTNAME_PREFIX = 'test_regrtest_'
    TESTNAME_REGEX = r'test_[a-zA-Z0-9_]+'

    eleza setUp(self):
        self.testdir = os.path.realpath(os.path.dirname(__file__))

        self.tmptestdir = tempfile.mkdtemp()
        self.addCleanup(support.rmtree, self.tmptestdir)

    eleza create_test(self, name=Tupu, code=Tupu):
        ikiwa sio name:
            name = 'noop%s' % BaseTestCase.TEST_UNIQUE_ID
            BaseTestCase.TEST_UNIQUE_ID += 1

        ikiwa code ni Tupu:
            code = textwrap.dedent("""
                    agiza unittest

                    kundi Tests(unittest.TestCase):
                        eleza test_empty_test(self):
                            pass
                """)

        # test_regrtest cannot be run twice kwenye parallel because
        # of setUp() na create_test()
        name = self.TESTNAME_PREFIX + name
        path = os.path.join(self.tmptestdir, name + '.py')

        self.addCleanup(support.unlink, path)
        # Use 'x' mode to ensure that we do sio override existing tests
        jaribu:
            ukijumuisha open(path, 'x', encoding='utf-8') as fp:
                fp.write(code)
        except PermissionError as exc:
            ikiwa sio sysconfig.is_python_build():
                self.skipTest("cannot write %s: %s" % (path, exc))
            raise
        rudisha name

    eleza regex_search(self, regex, output):
        match = re.search(regex, output, re.MULTILINE)
        ikiwa sio match:
            self.fail("%r sio found kwenye %r" % (regex, output))
        rudisha match

    eleza check_line(self, output, regex):
        regex = re.compile(r'^' + regex, re.MULTILINE)
        self.assertRegex(output, regex)

    eleza parse_executed_tests(self, output):
        regex = (r'^%s\[ *[0-9]+(?:/ *[0-9]+)*\] (%s)'
                 % (LOG_PREFIX, self.TESTNAME_REGEX))
        parser = re.finditer(regex, output, re.MULTILINE)
        rudisha list(match.group(1) kila match kwenye parser)

    eleza check_executed_tests(self, output, tests, skipped=(), failed=(),
                             env_changed=(), omitted=(),
                             rerun=(), no_test_ran=(),
                             randomize=Uongo, interrupted=Uongo,
                             fail_env_changed=Uongo):
        ikiwa isinstance(tests, str):
            tests = [tests]
        ikiwa isinstance(skipped, str):
            skipped = [skipped]
        ikiwa isinstance(failed, str):
            failed = [failed]
        ikiwa isinstance(env_changed, str):
            env_changed = [env_changed]
        ikiwa isinstance(omitted, str):
            omitted = [omitted]
        ikiwa isinstance(rerun, str):
            rerun = [rerun]
        ikiwa isinstance(no_test_ran, str):
            no_test_ran = [no_test_ran]

        executed = self.parse_executed_tests(output)
        ikiwa randomize:
            self.assertEqual(set(executed), set(tests), output)
        isipokua:
            self.assertEqual(executed, tests, output)

        eleza plural(count):
            rudisha 's' ikiwa count != 1 isipokua ''

        eleza list_regex(line_format, tests):
            count = len(tests)
            names = ' '.join(sorted(tests))
            regex = line_format % (count, plural(count))
            regex = r'%s:\n    %s$' % (regex, names)
            rudisha regex

        ikiwa skipped:
            regex = list_regex('%s test%s skipped', skipped)
            self.check_line(output, regex)

        ikiwa failed:
            regex = list_regex('%s test%s failed', failed)
            self.check_line(output, regex)

        ikiwa env_changed:
            regex = list_regex('%s test%s altered the execution environment',
                               env_changed)
            self.check_line(output, regex)

        ikiwa omitted:
            regex = list_regex('%s test%s omitted', omitted)
            self.check_line(output, regex)

        ikiwa rerun:
            regex = list_regex('%s re-run test%s', rerun)
            self.check_line(output, regex)
            regex = LOG_PREFIX + r"Re-running failed tests kwenye verbose mode"
            self.check_line(output, regex)
            kila test_name kwenye rerun:
                regex = LOG_PREFIX + f"Re-running {test_name} kwenye verbose mode"
                self.check_line(output, regex)

        ikiwa no_test_ran:
            regex = list_regex('%s test%s run no tests', no_test_ran)
            self.check_line(output, regex)

        good = (len(tests) - len(skipped) - len(failed)
                - len(omitted) - len(env_changed) - len(no_test_ran))
        ikiwa good:
            regex = r'%s test%s OK\.$' % (good, plural(good))
            ikiwa sio skipped na sio failed na good > 1:
                regex = 'All %s' % regex
            self.check_line(output, regex)

        ikiwa interrupted:
            self.check_line(output, 'Test suite interrupted by signal SIGINT.')

        result = []
        ikiwa failed:
            result.append('FAILURE')
        elikiwa fail_env_changed na env_changed:
            result.append('ENV CHANGED')
        ikiwa interrupted:
            result.append('INTERRUPTED')
        ikiwa sio any((good, result, failed, interrupted, skipped,
                    env_changed, fail_env_changed)):
            result.append("NO TEST RUN")
        elikiwa sio result:
            result.append('SUCCESS')
        result = ', '.join(result)
        ikiwa rerun:
            self.check_line(output, 'Tests result: FAILURE')
            result = 'FAILURE then %s' % result

        self.check_line(output, 'Tests result: %s' % result)

    eleza parse_random_seed(self, output):
        match = self.regex_search(r'Using random seed ([0-9]+)', output)
        randseed = int(match.group(1))
        self.assertKweli(0 <= randseed <= 10000000, randseed)
        rudisha randseed

    eleza run_command(self, args, input=Tupu, exitcode=0, **kw):
        ikiwa sio input:
            input = ''
        ikiwa 'stderr' sio kwenye kw:
            kw['stderr'] = subprocess.PIPE
        proc = subprocess.run(args,
                              universal_newlines=Kweli,
                              input=input,
                              stdout=subprocess.PIPE,
                              **kw)
        ikiwa proc.returncode != exitcode:
            msg = ("Command %s failed ukijumuisha exit code %s\n"
                   "\n"
                   "stdout:\n"
                   "---\n"
                   "%s\n"
                   "---\n"
                   % (str(args), proc.returncode, proc.stdout))
            ikiwa proc.stderr:
                msg += ("\n"
                        "stderr:\n"
                        "---\n"
                        "%s"
                        "---\n"
                        % proc.stderr)
            self.fail(msg)
        rudisha proc

    eleza run_python(self, args, **kw):
        args = [sys.executable, '-X', 'faulthandler', '-I', *args]
        proc = self.run_command(args, **kw)
        rudisha proc.stdout


kundi CheckActualTests(BaseTestCase):
    """
    Check that regrtest appears to find the expected set of tests.
    """

    eleza test_finds_expected_number_of_tests(self):
        args = ['-Wd', '-E', '-bb', '-m', 'test.regrtest', '--list-tests']
        output = self.run_python(args)
        rough_number_of_tests_found = len(output.splitlines())
        actual_testsuite_glob = os.path.join(os.path.dirname(__file__),
                                             'test*.py')
        rough_counted_test_py_files = len(glob.glob(actual_testsuite_glob))
        # We're sio trying to duplicate test finding logic kwenye here,
        # just give a rough estimate of how many there should be and
        # be near that.  This ni a regression test to prevent mishaps
        # such as https://bugs.python.org/issue37667 kwenye the future.
        # If you need to change the values kwenye here during some
        # mythical future test suite reorganization, don't go
        # overboard ukijumuisha logic na keep that goal kwenye mind.
        self.assertGreater(rough_number_of_tests_found,
                           rough_counted_test_py_files*9//10,
                           msg='Unexpectedly low number of tests found in:\n'
                           f'{", ".join(output.splitlines())}')


kundi ProgramsTestCase(BaseTestCase):
    """
    Test various ways to run the Python test suite. Use options close
    to options used on the buildbot.
    """

    NTEST = 4

    eleza setUp(self):
        super().setUp()

        # Create NTEST tests doing nothing
        self.tests = [self.create_test() kila index kwenye range(self.NTEST)]

        self.python_args = ['-Wd', '-E', '-bb']
        self.regrtest_args = ['-uall', '-rwW',
                              '--testdir=%s' % self.tmptestdir]
        ikiwa hasattr(faulthandler, 'dump_traceback_later'):
            self.regrtest_args.extend(('--timeout', '3600', '-j4'))
        ikiwa sys.platform == 'win32':
            self.regrtest_args.append('-n')

    eleza check_output(self, output):
        self.parse_random_seed(output)
        self.check_executed_tests(output, self.tests, randomize=Kweli)

    eleza run_tests(self, args):
        output = self.run_python(args)
        self.check_output(output)

    eleza test_script_regrtest(self):
        # Lib/test/regrtest.py
        script = os.path.join(self.testdir, 'regrtest.py')

        args = [*self.python_args, script, *self.regrtest_args, *self.tests]
        self.run_tests(args)

    eleza test_module_test(self):
        # -m test
        args = [*self.python_args, '-m', 'test',
                *self.regrtest_args, *self.tests]
        self.run_tests(args)

    eleza test_module_regrtest(self):
        # -m test.regrtest
        args = [*self.python_args, '-m', 'test.regrtest',
                *self.regrtest_args, *self.tests]
        self.run_tests(args)

    eleza test_module_autotest(self):
        # -m test.autotest
        args = [*self.python_args, '-m', 'test.autotest',
                *self.regrtest_args, *self.tests]
        self.run_tests(args)

    eleza test_module_from_test_autotest(self):
        # kutoka test agiza autotest
        code = 'kutoka test agiza autotest'
        args = [*self.python_args, '-c', code,
                *self.regrtest_args, *self.tests]
        self.run_tests(args)

    eleza test_script_autotest(self):
        # Lib/test/autotest.py
        script = os.path.join(self.testdir, 'autotest.py')
        args = [*self.python_args, script, *self.regrtest_args, *self.tests]
        self.run_tests(args)

    @unittest.skipUnless(sysconfig.is_python_build(),
                         'run_tests.py script ni sio installed')
    eleza test_tools_script_run_tests(self):
        # Tools/scripts/run_tests.py
        script = os.path.join(ROOT_DIR, 'Tools', 'scripts', 'run_tests.py')
        args = [script, *self.regrtest_args, *self.tests]
        self.run_tests(args)

    eleza run_batch(self, *args):
        proc = self.run_command(args)
        self.check_output(proc.stdout)

    @unittest.skipUnless(sysconfig.is_python_build(),
                         'test.bat script ni sio installed')
    @unittest.skipUnless(sys.platform == 'win32', 'Windows only')
    eleza test_tools_buildbot_test(self):
        # Tools\buildbot\test.bat
        script = os.path.join(ROOT_DIR, 'Tools', 'buildbot', 'test.bat')
        test_args = ['--testdir=%s' % self.tmptestdir]
        ikiwa platform.machine() == 'ARM64':
            test_args.append('-arm64') # ARM 64-bit build
        elikiwa platform.architecture()[0] == '64bit':
            test_args.append('-x64')   # 64-bit build
        ikiwa sio Py_DEBUG:
            test_args.append('+d')     # Release build, use python.exe
        self.run_batch(script, *test_args, *self.tests)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows only')
    eleza test_pcbuild_rt(self):
        # PCbuild\rt.bat
        script = os.path.join(ROOT_DIR, r'PCbuild\rt.bat')
        ikiwa sio os.path.isfile(script):
            self.skipTest(f'File "{script}" does sio exist')
        rt_args = ["-q"]             # Quick, don't run tests twice
        ikiwa platform.machine() == 'ARM64':
            rt_args.append('-arm64') # ARM 64-bit build
        elikiwa platform.architecture()[0] == '64bit':
            rt_args.append('-x64')   # 64-bit build
        ikiwa Py_DEBUG:
            rt_args.append('-d')     # Debug build, use python_d.exe
        self.run_batch(script, *rt_args, *self.regrtest_args, *self.tests)


kundi ArgsTestCase(BaseTestCase):
    """
    Test arguments of the Python test suite.
    """

    eleza run_tests(self, *testargs, **kw):
        cmdargs = ['-m', 'test', '--testdir=%s' % self.tmptestdir, *testargs]
        rudisha self.run_python(cmdargs, **kw)

    eleza test_failing_test(self):
        # test a failing test
        code = textwrap.dedent("""
            agiza unittest

            kundi FailingTest(unittest.TestCase):
                eleza test_failing(self):
                    self.fail("bug")
        """)
        test_ok = self.create_test('ok')
        test_failing = self.create_test('failing', code=code)
        tests = [test_ok, test_failing]

        output = self.run_tests(*tests, exitcode=2)
        self.check_executed_tests(output, tests, failed=test_failing)

    eleza test_resources(self):
        # test -u command line option
        tests = {}
        kila resource kwenye ('audio', 'network'):
            code = textwrap.dedent("""
                        kutoka test agiza support; support.requires(%r)
                        agiza unittest
                        kundi PassingTest(unittest.TestCase):
                            eleza test_pass(self):
                                pass
                    """ % resource)

            tests[resource] = self.create_test(resource, code)
        test_names = sorted(tests.values())

        # -u all: 2 resources enabled
        output = self.run_tests('-u', 'all', *test_names)
        self.check_executed_tests(output, test_names)

        # -u audio: 1 resource enabled
        output = self.run_tests('-uaudio', *test_names)
        self.check_executed_tests(output, test_names,
                                  skipped=tests['network'])

        # no option: 0 resources enabled
        output = self.run_tests(*test_names)
        self.check_executed_tests(output, test_names,
                                  skipped=test_names)

    eleza test_random(self):
        # test -r na --randseed command line option
        code = textwrap.dedent("""
            agiza random
            andika("TESTRANDOM: %s" % random.randint(1, 1000))
        """)
        test = self.create_test('random', code)

        # first run to get the output ukijumuisha the random seed
        output = self.run_tests('-r', test)
        randseed = self.parse_random_seed(output)
        match = self.regex_search(r'TESTRANDOM: ([0-9]+)', output)
        test_random = int(match.group(1))

        # try to reproduce ukijumuisha the random seed
        output = self.run_tests('-r', '--randseed=%s' % randseed, test)
        randseed2 = self.parse_random_seed(output)
        self.assertEqual(randseed2, randseed)

        match = self.regex_search(r'TESTRANDOM: ([0-9]+)', output)
        test_random2 = int(match.group(1))
        self.assertEqual(test_random2, test_random)

    eleza test_fromfile(self):
        # test --fromfile
        tests = [self.create_test() kila index kwenye range(5)]

        # Write the list of files using a format similar to regrtest output:
        # [1/2] test_1
        # [2/2] test_2
        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)

        # test format '0:00:00 [2/7] test_opcodes -- test_grammar took 0 sec'
        ukijumuisha open(filename, "w") as fp:
            previous = Tupu
            kila index, name kwenye enumerate(tests, 1):
                line = ("00:00:%02i [%s/%s] %s"
                        % (index, index, len(tests), name))
                ikiwa previous:
                    line += " -- %s took 0 sec" % previous
                andika(line, file=fp)
                previous = name

        output = self.run_tests('--fromfile', filename)
        self.check_executed_tests(output, tests)

        # test format '[2/7] test_opcodes'
        ukijumuisha open(filename, "w") as fp:
            kila index, name kwenye enumerate(tests, 1):
                andika("[%s/%s] %s" % (index, len(tests), name), file=fp)

        output = self.run_tests('--fromfile', filename)
        self.check_executed_tests(output, tests)

        # test format 'test_opcodes'
        ukijumuisha open(filename, "w") as fp:
            kila name kwenye tests:
                andika(name, file=fp)

        output = self.run_tests('--fromfile', filename)
        self.check_executed_tests(output, tests)

        # test format 'Lib/test/test_opcodes.py'
        ukijumuisha open(filename, "w") as fp:
            kila name kwenye tests:
                andika('Lib/test/%s.py' % name, file=fp)

        output = self.run_tests('--fromfile', filename)
        self.check_executed_tests(output, tests)

    eleza test_interrupted(self):
        code = TEST_INTERRUPTED
        test = self.create_test('sigint', code=code)
        output = self.run_tests(test, exitcode=130)
        self.check_executed_tests(output, test, omitted=test,
                                  interrupted=Kweli)

    eleza test_slowest(self):
        # test --slowest
        tests = [self.create_test() kila index kwenye range(3)]
        output = self.run_tests("--slowest", *tests)
        self.check_executed_tests(output, tests)
        regex = ('10 slowest tests:\n'
                 '(?:- %s: .*\n){%s}'
                 % (self.TESTNAME_REGEX, len(tests)))
        self.check_line(output, regex)

    eleza test_slowest_interrupted(self):
        # Issue #25373: test --slowest ukijumuisha an interrupted test
        code = TEST_INTERRUPTED
        test = self.create_test("sigint", code=code)

        kila multiprocessing kwenye (Uongo, Kweli):
            ukijumuisha self.subTest(multiprocessing=multiprocessing):
                ikiwa multiprocessing:
                    args = ("--slowest", "-j2", test)
                isipokua:
                    args = ("--slowest", test)
                output = self.run_tests(*args, exitcode=130)
                self.check_executed_tests(output, test,
                                          omitted=test, interrupted=Kweli)

                regex = ('10 slowest tests:\n')
                self.check_line(output, regex)

    eleza test_coverage(self):
        # test --coverage
        test = self.create_test('coverage')
        output = self.run_tests("--coverage", test)
        self.check_executed_tests(output, [test])
        regex = (r'lines +cov% +module +\(path\)\n'
                 r'(?: *[0-9]+ *[0-9]{1,2}% *[^ ]+ +\([^)]+\)+)+')
        self.check_line(output, regex)

    eleza test_wait(self):
        # test --wait
        test = self.create_test('wait')
        output = self.run_tests("--wait", test, input='key')
        self.check_line(output, 'Press any key to endelea')

    eleza test_forever(self):
        # test --forever
        code = textwrap.dedent("""
            agiza builtins
            agiza unittest

            kundi ForeverTester(unittest.TestCase):
                eleza test_run(self):
                    # Store the state kwenye the builtins module, because the test
                    # module ni reload at each run
                    ikiwa 'RUN' kwenye builtins.__dict__:
                        builtins.__dict__['RUN'] += 1
                        ikiwa builtins.__dict__['RUN'] >= 3:
                            self.fail("fail at the 3rd runs")
                    isipokua:
                        builtins.__dict__['RUN'] = 1
        """)
        test = self.create_test('forever', code=code)
        output = self.run_tests('--forever', test, exitcode=2)
        self.check_executed_tests(output, [test]*3, failed=test)

    eleza check_leak(self, code, what):
        test = self.create_test('huntrleaks', code=code)

        filename = 'reflog.txt'
        self.addCleanup(support.unlink, filename)
        output = self.run_tests('--huntrleaks', '3:3:', test,
                                exitcode=2,
                                stderr=subprocess.STDOUT)
        self.check_executed_tests(output, [test], failed=test)

        line = 'beginning 6 repetitions\n123456\n......\n'
        self.check_line(output, re.escape(line))

        line2 = '%s leaked [1, 1, 1] %s, sum=3\n' % (test, what)
        self.assertIn(line2, output)

        ukijumuisha open(filename) as fp:
            reflog = fp.read()
            self.assertIn(line2, reflog)

    @unittest.skipUnless(Py_DEBUG, 'need a debug build')
    eleza test_huntrleaks(self):
        # test --huntrleaks
        code = textwrap.dedent("""
            agiza unittest

            GLOBAL_LIST = []

            kundi RefLeakTest(unittest.TestCase):
                eleza test_leak(self):
                    GLOBAL_LIST.append(object())
        """)
        self.check_leak(code, 'references')

    @unittest.skipUnless(Py_DEBUG, 'need a debug build')
    eleza test_huntrleaks_fd_leak(self):
        # test --huntrleaks kila file descriptor leak
        code = textwrap.dedent("""
            agiza os
            agiza unittest

            kundi FDLeakTest(unittest.TestCase):
                eleza test_leak(self):
                    fd = os.open(__file__, os.O_RDONLY)
                    # bug: never close the file descriptor
        """)
        self.check_leak(code, 'file descriptors')

    eleza test_list_tests(self):
        # test --list-tests
        tests = [self.create_test() kila i kwenye range(5)]
        output = self.run_tests('--list-tests', *tests)
        self.assertEqual(output.rstrip().splitlines(),
                         tests)

    eleza test_list_cases(self):
        # test --list-cases
        code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_method1(self):
                    pass
                eleza test_method2(self):
                    pass
        """)
        testname = self.create_test(code=code)

        # Test --list-cases
        all_methods = ['%s.Tests.test_method1' % testname,
                       '%s.Tests.test_method2' % testname]
        output = self.run_tests('--list-cases', testname)
        self.assertEqual(output.splitlines(), all_methods)

        # Test --list-cases ukijumuisha --match
        all_methods = ['%s.Tests.test_method1' % testname]
        output = self.run_tests('--list-cases',
                                '-m', 'test_method1',
                                testname)
        self.assertEqual(output.splitlines(), all_methods)

    @support.cpython_only
    eleza test_crashed(self):
        # Any code which causes a crash
        code = 'agiza faulthandler; faulthandler._sigsegv()'
        crash_test = self.create_test(name="crash", code=code)

        tests = [crash_test]
        output = self.run_tests("-j2", *tests, exitcode=2)
        self.check_executed_tests(output, tests, failed=crash_test,
                                  randomize=Kweli)

    eleza parse_methods(self, output):
        regex = re.compile("^(test[^ ]+).*ok$", flags=re.MULTILINE)
        rudisha [match.group(1) kila match kwenye regex.finditer(output)]

    eleza test_matchfile(self):
        code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_method1(self):
                    pass
                eleza test_method2(self):
                    pass
                eleza test_method3(self):
                    pass
                eleza test_method4(self):
                    pass
        """)
        all_methods = ['test_method1', 'test_method2',
                       'test_method3', 'test_method4']
        testname = self.create_test(code=code)

        # by default, all methods should be run
        output = self.run_tests("-v", testname)
        methods = self.parse_methods(output)
        self.assertEqual(methods, all_methods)

        # only run a subset
        filename = support.TESTFN
        self.addCleanup(support.unlink, filename)

        subset = [
            # only match the method name
            'test_method1',
            # match the full identifier
            '%s.Tests.test_method3' % testname]
        ukijumuisha open(filename, "w") as fp:
            kila name kwenye subset:
                andika(name, file=fp)

        output = self.run_tests("-v", "--matchfile", filename, testname)
        methods = self.parse_methods(output)
        subset = ['test_method1', 'test_method3']
        self.assertEqual(methods, subset)

    eleza test_env_changed(self):
        code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_env_changed(self):
                    open("env_changed", "w").close()
        """)
        testname = self.create_test(code=code)

        # don't fail by default
        output = self.run_tests(testname)
        self.check_executed_tests(output, [testname], env_changed=testname)

        # fail ukijumuisha --fail-env-changed
        output = self.run_tests("--fail-env-changed", testname, exitcode=3)
        self.check_executed_tests(output, [testname], env_changed=testname,
                                  fail_env_changed=Kweli)

    eleza test_rerun_fail(self):
        # FAILURE then FAILURE
        code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_bug(self):
                    # test always fail
                    self.fail("bug")
        """)
        testname = self.create_test(code=code)

        output = self.run_tests("-w", testname, exitcode=2)
        self.check_executed_tests(output, [testname],
                                  failed=testname, rerun=testname)

    eleza test_rerun_success(self):
        # FAILURE then SUCCESS
        code = textwrap.dedent("""
            agiza builtins
            agiza unittest

            kundi Tests(unittest.TestCase):
                failed = Uongo

                eleza test_fail_once(self):
                    ikiwa sio hasattr(builtins, '_test_failed'):
                        builtins._test_failed = Kweli
                        self.fail("bug")
        """)
        testname = self.create_test(code=code)

        output = self.run_tests("-w", testname, exitcode=0)
        self.check_executed_tests(output, [testname],
                                  rerun=testname)

    eleza test_no_tests_ran(self):
        code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_bug(self):
                    pass
        """)
        testname = self.create_test(code=code)

        output = self.run_tests(testname, "-m", "nosuchtest", exitcode=0)
        self.check_executed_tests(output, [testname], no_test_ran=testname)

    eleza test_no_tests_ran_skip(self):
        code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_skipped(self):
                    self.skipTest("because")
        """)
        testname = self.create_test(code=code)

        output = self.run_tests(testname, exitcode=0)
        self.check_executed_tests(output, [testname])

    eleza test_no_tests_ran_multiple_tests_nonexistent(self):
        code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_bug(self):
                    pass
        """)
        testname = self.create_test(code=code)
        testname2 = self.create_test(code=code)

        output = self.run_tests(testname, testname2, "-m", "nosuchtest", exitcode=0)
        self.check_executed_tests(output, [testname, testname2],
                                  no_test_ran=[testname, testname2])

    eleza test_no_test_ran_some_test_exist_some_not(self):
        code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_bug(self):
                    pass
        """)
        testname = self.create_test(code=code)
        other_code = textwrap.dedent("""
            agiza unittest

            kundi Tests(unittest.TestCase):
                eleza test_other_bug(self):
                    pass
        """)
        testname2 = self.create_test(code=other_code)

        output = self.run_tests(testname, testname2, "-m", "nosuchtest",
                                "-m", "test_other_bug", exitcode=0)
        self.check_executed_tests(output, [testname, testname2],
                                  no_test_ran=[testname])

    @support.cpython_only
    eleza test_findleaks(self):
        code = textwrap.dedent(r"""
            agiza _testcapi
            agiza gc
            agiza unittest

            @_testcapi.with_tp_del
            kundi Garbage:
                eleza __tp_del__(self):
                    pass

            kundi Tests(unittest.TestCase):
                eleza test_garbage(self):
                    # create an uncollectable object
                    obj = Garbage()
                    obj.ref_cycle = obj
                    obj = Tupu
        """)
        testname = self.create_test(code=code)

        output = self.run_tests("--fail-env-changed", testname, exitcode=3)
        self.check_executed_tests(output, [testname],
                                  env_changed=[testname],
                                  fail_env_changed=Kweli)

        # --findleaks ni now basically an alias to --fail-env-changed
        output = self.run_tests("--findleaks", testname, exitcode=3)
        self.check_executed_tests(output, [testname],
                                  env_changed=[testname],
                                  fail_env_changed=Kweli)

    eleza test_multiprocessing_timeout(self):
        code = textwrap.dedent(r"""
            agiza time
            agiza unittest
            jaribu:
                agiza faulthandler
            except ImportError:
                faulthandler = Tupu

            kundi Tests(unittest.TestCase):
                # test hangs na so should be stopped by the timeout
                eleza test_sleep(self):
                    # we want to test regrtest multiprocessing timeout,
                    # sio faulthandler timeout
                    ikiwa faulthandler ni sio Tupu:
                        faulthandler.cancel_dump_traceback_later()

                    time.sleep(60 * 5)
        """)
        testname = self.create_test(code=code)

        output = self.run_tests("-j2", "--timeout=1.0", testname, exitcode=2)
        self.check_executed_tests(output, [testname],
                                  failed=testname)
        self.assertRegex(output,
                         re.compile('%s timed out' % testname, re.MULTILINE))

    eleza test_cleanup(self):
        dirname = os.path.join(self.tmptestdir, "test_python_123")
        os.mkdir(dirname)
        filename = os.path.join(self.tmptestdir, "test_python_456")
        open(filename, "wb").close()
        names = [dirname, filename]

        cmdargs = ['-m', 'test',
                   '--tempdir=%s' % self.tmptestdir,
                   '--cleanup']
        self.run_python(cmdargs)

        kila name kwenye names:
            self.assertUongo(os.path.exists(name), name)


kundi TestUtils(unittest.TestCase):
    eleza test_format_duration(self):
        self.assertEqual(utils.format_duration(0),
                         '0 ms')
        self.assertEqual(utils.format_duration(1e-9),
                         '1 ms')
        self.assertEqual(utils.format_duration(10e-3),
                         '10 ms')
        self.assertEqual(utils.format_duration(1.5),
                         '1.5 sec')
        self.assertEqual(utils.format_duration(1),
                         '1.0 sec')
        self.assertEqual(utils.format_duration(2 * 60),
                         '2 min')
        self.assertEqual(utils.format_duration(2 * 60 + 1),
                         '2 min 1 sec')
        self.assertEqual(utils.format_duration(3 * 3600),
                         '3 hour')
        self.assertEqual(utils.format_duration(3 * 3600  + 2 * 60 + 1),
                         '3 hour 2 min')
        self.assertEqual(utils.format_duration(3 * 3600 + 1),
                         '3 hour 1 sec')


ikiwa __name__ == '__main__':
    unittest.main()
