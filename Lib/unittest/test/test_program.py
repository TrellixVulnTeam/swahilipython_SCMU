agiza io

agiza os
agiza sys
agiza subprocess
kutoka test agiza support
agiza unittest
agiza unittest.test


kundi Test_TestProgram(unittest.TestCase):

    eleza test_discovery_kutoka_dotted_path(self):
        loader = unittest.TestLoader()

        tests = [self]
        expectedPath = os.path.abspath(os.path.dirname(unittest.test.__file__))

        self.wasRun = False
        eleza _find_tests(start_dir, pattern):
            self.wasRun = True
            self.assertEqual(start_dir, expectedPath)
            rudisha tests
        loader._find_tests = _find_tests
        suite = loader.discover('unittest.test')
        self.assertTrue(self.wasRun)
        self.assertEqual(suite._tests, tests)

    # Horrible white box test
    eleza testNoExit(self):
        result = object()
        test = object()

        kundi FakeRunner(object):
            eleza run(self, test):
                self.test = test
                rudisha result

        runner = FakeRunner()

        oldParseArgs = unittest.TestProgram.parseArgs
        eleza restoreParseArgs():
            unittest.TestProgram.parseArgs = oldParseArgs
        unittest.TestProgram.parseArgs = lambda *args: None
        self.addCleanup(restoreParseArgs)

        eleza removeTest():
            del unittest.TestProgram.test
        unittest.TestProgram.test = test
        self.addCleanup(removeTest)

        program = unittest.TestProgram(testRunner=runner, exit=False, verbosity=2)

        self.assertEqual(program.result, result)
        self.assertEqual(runner.test, test)
        self.assertEqual(program.verbosity, 2)

    kundi FooBar(unittest.TestCase):
        eleza testPass(self):
            assert True
        eleza testFail(self):
            assert False

    kundi FooBarLoader(unittest.TestLoader):
        """Test loader that returns a suite containing FooBar."""
        eleza loadTestsFromModule(self, module):
            rudisha self.suiteClass(
                [self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

        eleza loadTestsFromNames(self, names, module):
            rudisha self.suiteClass(
                [self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

    eleza test_defaultTest_with_string(self):
        kundi FakeRunner(object):
            eleza run(self, test):
                self.test = test
                rudisha True

        old_argv = sys.argv
        sys.argv = ['faketest']
        runner = FakeRunner()
        program = unittest.TestProgram(testRunner=runner, exit=False,
                                       defaultTest='unittest.test',
                                       testLoader=self.FooBarLoader())
        sys.argv = old_argv
        self.assertEqual(('unittest.test',), program.testNames)

    eleza test_defaultTest_with_iterable(self):
        kundi FakeRunner(object):
            eleza run(self, test):
                self.test = test
                rudisha True

        old_argv = sys.argv
        sys.argv = ['faketest']
        runner = FakeRunner()
        program = unittest.TestProgram(
            testRunner=runner, exit=False,
            defaultTest=['unittest.test', 'unittest.test2'],
            testLoader=self.FooBarLoader())
        sys.argv = old_argv
        self.assertEqual(['unittest.test', 'unittest.test2'],
                          program.testNames)

    eleza test_NonExit(self):
        program = unittest.main(exit=False,
                                argv=["foobar"],
                                testRunner=unittest.TextTestRunner(stream=io.StringIO()),
                                testLoader=self.FooBarLoader())
        self.assertTrue(hasattr(program, 'result'))


    eleza test_Exit(self):
        self.assertRaises(
            SystemExit,
            unittest.main,
            argv=["foobar"],
            testRunner=unittest.TextTestRunner(stream=io.StringIO()),
            exit=True,
            testLoader=self.FooBarLoader())


    eleza test_ExitAsDefault(self):
        self.assertRaises(
            SystemExit,
            unittest.main,
            argv=["foobar"],
            testRunner=unittest.TextTestRunner(stream=io.StringIO()),
            testLoader=self.FooBarLoader())


kundi InitialisableProgram(unittest.TestProgram):
    exit = False
    result = None
    verbosity = 1
    defaultTest = None
    tb_locals = False
    testRunner = None
    testLoader = unittest.defaultTestLoader
    module = '__main__'
    progName = 'test'
    test = 'test'
    eleza __init__(self, *args):
        pass

RESULT = object()

kundi FakeRunner(object):
    initArgs = None
    test = None
    raiseError = 0

    eleza __init__(self, **kwargs):
        FakeRunner.initArgs = kwargs
        ikiwa FakeRunner.raiseError:
            FakeRunner.raiseError -= 1
            raise TypeError

    eleza run(self, test):
        FakeRunner.test = test
        rudisha RESULT


kundi TestCommandLineArgs(unittest.TestCase):

    eleza setUp(self):
        self.program = InitialisableProgram()
        self.program.createTests = lambda: None
        FakeRunner.initArgs = None
        FakeRunner.test = None
        FakeRunner.raiseError = 0

    eleza testVerbosity(self):
        program = self.program

        for opt in '-q', '--quiet':
            program.verbosity = 1
            program.parseArgs([None, opt])
            self.assertEqual(program.verbosity, 0)

        for opt in '-v', '--verbose':
            program.verbosity = 1
            program.parseArgs([None, opt])
            self.assertEqual(program.verbosity, 2)

    eleza testBufferCatchFailfast(self):
        program = self.program
        for arg, attr in (('buffer', 'buffer'), ('failfast', 'failfast'),
                      ('catch', 'catchbreak')):
            ikiwa attr == 'catch' and not hasInstallHandler:
                continue

            setattr(program, attr, None)
            program.parseArgs([None])
            self.assertIs(getattr(program, attr), False)

            false = []
            setattr(program, attr, false)
            program.parseArgs([None])
            self.assertIs(getattr(program, attr), false)

            true = [42]
            setattr(program, attr, true)
            program.parseArgs([None])
            self.assertIs(getattr(program, attr), true)

            short_opt = '-%s' % arg[0]
            long_opt = '--%s' % arg
            for opt in short_opt, long_opt:
                setattr(program, attr, None)
                program.parseArgs([None, opt])
                self.assertIs(getattr(program, attr), True)

                setattr(program, attr, False)
                with support.captured_stderr() as stderr, \
                    self.assertRaises(SystemExit) as cm:
                    program.parseArgs([None, opt])
                self.assertEqual(cm.exception.args, (2,))

                setattr(program, attr, True)
                with support.captured_stderr() as stderr, \
                    self.assertRaises(SystemExit) as cm:
                    program.parseArgs([None, opt])
                self.assertEqual(cm.exception.args, (2,))

    eleza testWarning(self):
        """Test the warnings argument"""
        # see #10535
        kundi FakeTP(unittest.TestProgram):
            eleza parseArgs(self, *args, **kw): pass
            eleza runTests(self, *args, **kw): pass
        warnoptions = sys.warnoptions[:]
        try:
            sys.warnoptions[:] = []
            # no warn options, no arg -> default
            self.assertEqual(FakeTP().warnings, 'default')
            # no warn options, w/ arg -> arg value
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
            sys.warnoptions[:] = ['somevalue']
            # warn options, no arg -> None
            # warn options, w/ arg -> arg value
            self.assertEqual(FakeTP().warnings, None)
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
        finally:
            sys.warnoptions[:] = warnoptions

    eleza testRunTestsRunnerClass(self):
        program = self.program

        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.warnings = 'warnings'

        program.runTests()

        self.assertEqual(FakeRunner.initArgs, {'verbosity': 'verbosity',
                                                'failfast': 'failfast',
                                                'buffer': 'buffer',
                                                'tb_locals': False,
                                                'warnings': 'warnings'})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    eleza testRunTestsRunnerInstance(self):
        program = self.program

        program.testRunner = FakeRunner()
        FakeRunner.initArgs = None

        program.runTests()

        # A new FakeRunner should not have been instantiated
        self.assertIsNone(FakeRunner.initArgs)

        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    eleza test_locals(self):
        program = self.program

        program.testRunner = FakeRunner
        program.parseArgs([None, '--locals'])
        self.assertEqual(True, program.tb_locals)
        program.runTests()
        self.assertEqual(FakeRunner.initArgs, {'buffer': False,
                                               'failfast': False,
                                               'tb_locals': True,
                                               'verbosity': 1,
                                               'warnings': None})

    eleza testRunTestsOldRunnerClass(self):
        program = self.program

        # Two TypeErrors are needed to fall all the way back to old-style
        # runners - one to fail tb_locals, one to fail buffer etc.
        FakeRunner.raiseError = 2
        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.test = 'test'

        program.runTests()

        # If initialising raises a type error it should be retried
        # without the new keyword arguments
        self.assertEqual(FakeRunner.initArgs, {})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    eleza testCatchBreakInstallsHandler(self):
        module = sys.modules['unittest.main']
        original = module.installHandler
        eleza restore():
            module.installHandler = original
        self.addCleanup(restore)

        self.installed = False
        eleza fakeInstallHandler():
            self.installed = True
        module.installHandler = fakeInstallHandler

        program = self.program
        program.catchbreak = True

        program.testRunner = FakeRunner

        program.runTests()
        self.assertTrue(self.installed)

    eleza _patch_isfile(self, names, exists=True):
        eleza isfile(path):
            rudisha path in names
        original = os.path.isfile
        os.path.isfile = isfile
        eleza restore():
            os.path.isfile = original
        self.addCleanup(restore)


    eleza testParseArgsFileNames(self):
        # running tests with filenames instead of module names
        program = self.program
        argv = ['progname', 'foo.py', 'bar.Py', 'baz.PY', 'wing.txt']
        self._patch_isfile(argv)

        program.createTests = lambda: None
        program.parseArgs(argv)

        # note that 'wing.txt' is not a Python file so the name should
        # *not* be converted to a module name
        expected = ['foo', 'bar', 'baz', 'wing.txt']
        self.assertEqual(program.testNames, expected)


    eleza testParseArgsFilePaths(self):
        program = self.program
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        self._patch_isfile(argv)

        program.createTests = lambda: None
        program.parseArgs(argv)

        expected = ['foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)


    eleza testParseArgsNonExistentFiles(self):
        program = self.program
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        self._patch_isfile([])

        program.createTests = lambda: None
        program.parseArgs(argv)

        self.assertEqual(program.testNames, argv[1:])

    eleza testParseArgsAbsolutePathsThatCanBeConverted(self):
        cur_dir = os.getcwd()
        program = self.program
        eleza _join(name):
            rudisha os.path.join(cur_dir, name)
        argv = ['progname', _join('foo/bar/baz.py'), _join('green\\red.py')]
        self._patch_isfile(argv)

        program.createTests = lambda: None
        program.parseArgs(argv)

        expected = ['foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)

    eleza testParseArgsAbsolutePathsThatCannotBeConverted(self):
        program = self.program
        # even on Windows '/...' is considered absolute by os.path.abspath
        argv = ['progname', '/foo/bar/baz.py', '/green/red.py']
        self._patch_isfile(argv)

        program.createTests = lambda: None
        program.parseArgs(argv)

        self.assertEqual(program.testNames, argv[1:])

        # it may be better to use platform specific functions to normalise paths
        # rather than accepting '.PY' and '\' as file separator on Linux / Mac
        # it would also be better to check that a filename is a valid module
        # identifier (we have a regex for this in loader.py)
        # for invalid filenames should we raise a useful error rather than
        # leaving the current error message (agiza of filename fails) in place?

    eleza testParseArgsSelectedTestNames(self):
        program = self.program
        argv = ['progname', '-k', 'foo', '-k', 'bar', '-k', '*pat*']

        program.createTests = lambda: None
        program.parseArgs(argv)

        self.assertEqual(program.testNamePatterns, ['*foo*', '*bar*', '*pat*'])

    eleza testSelectedTestNamesFunctionalTest(self):
        eleza run_unittest(args):
            p = subprocess.Popen([sys.executable, '-m', 'unittest'] + args,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, cwd=os.path.dirname(__file__))
            with p:
                _, stderr = p.communicate()
            rudisha stderr.decode()

        t = '_test_warnings'
        self.assertIn('Ran 7 tests', run_unittest([t]))
        self.assertIn('Ran 7 tests', run_unittest(['-k', 'TestWarnings', t]))
        self.assertIn('Ran 7 tests', run_unittest(['discover', '-p', '*_test*', '-k', 'TestWarnings']))
        self.assertIn('Ran 2 tests', run_unittest(['-k', 'f', t]))
        self.assertIn('Ran 7 tests', run_unittest(['-k', 't', t]))
        self.assertIn('Ran 3 tests', run_unittest(['-k', '*t', t]))
        self.assertIn('Ran 7 tests', run_unittest(['-k', '*test_warnings.*Warning*', t]))
        self.assertIn('Ran 1 test', run_unittest(['-k', '*test_warnings.*warning*', t]))


ikiwa __name__ == '__main__':
    unittest.main()
