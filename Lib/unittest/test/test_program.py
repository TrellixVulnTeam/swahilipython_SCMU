agiza io

agiza os
agiza sys
agiza subprocess
kutoka test agiza support
agiza unittest
agiza unittest.test


kundi Test_TestProgram(unittest.TestCase):

    eleza test_discovery_from_dotted_path(self):
        loader = unittest.TestLoader()

        tests = [self]
        expectedPath = os.path.abspath(os.path.dirname(unittest.test.__file__))

        self.wasRun = Uongo
        eleza _find_tests(start_dir, pattern):
            self.wasRun = Kweli
            self.assertEqual(start_dir, expectedPath)
            rudisha tests
        loader._find_tests = _find_tests
        suite = loader.discover('unittest.test')
        self.assertKweli(self.wasRun)
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
        unittest.TestProgram.parseArgs = lambda *args: Tupu
        self.addCleanup(restoreParseArgs)

        eleza removeTest():
            toa unittest.TestProgram.test
        unittest.TestProgram.test = test
        self.addCleanup(removeTest)

        program = unittest.TestProgram(testRunner=runner, exit=Uongo, verbosity=2)

        self.assertEqual(program.result, result)
        self.assertEqual(runner.test, test)
        self.assertEqual(program.verbosity, 2)

    kundi FooBar(unittest.TestCase):
        eleza testPass(self):
            assert Kweli
        eleza testFail(self):
            assert Uongo

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
                rudisha Kweli

        old_argv = sys.argv
        sys.argv = ['faketest']
        runner = FakeRunner()
        program = unittest.TestProgram(testRunner=runner, exit=Uongo,
                                       defaultTest='unittest.test',
                                       testLoader=self.FooBarLoader())
        sys.argv = old_argv
        self.assertEqual(('unittest.test',), program.testNames)

    eleza test_defaultTest_with_iterable(self):
        kundi FakeRunner(object):
            eleza run(self, test):
                self.test = test
                rudisha Kweli

        old_argv = sys.argv
        sys.argv = ['faketest']
        runner = FakeRunner()
        program = unittest.TestProgram(
            testRunner=runner, exit=Uongo,
            defaultTest=['unittest.test', 'unittest.test2'],
            testLoader=self.FooBarLoader())
        sys.argv = old_argv
        self.assertEqual(['unittest.test', 'unittest.test2'],
                          program.testNames)

    eleza test_NonExit(self):
        program = unittest.main(exit=Uongo,
                                argv=["foobar"],
                                testRunner=unittest.TextTestRunner(stream=io.StringIO()),
                                testLoader=self.FooBarLoader())
        self.assertKweli(hasattr(program, 'result'))


    eleza test_Exit(self):
        self.assertRaises(
            SystemExit,
            unittest.main,
            argv=["foobar"],
            testRunner=unittest.TextTestRunner(stream=io.StringIO()),
            exit=Kweli,
            testLoader=self.FooBarLoader())


    eleza test_ExitAsDefault(self):
        self.assertRaises(
            SystemExit,
            unittest.main,
            argv=["foobar"],
            testRunner=unittest.TextTestRunner(stream=io.StringIO()),
            testLoader=self.FooBarLoader())


kundi InitialisableProgram(unittest.TestProgram):
    exit = Uongo
    result = Tupu
    verbosity = 1
    defaultTest = Tupu
    tb_locals = Uongo
    testRunner = Tupu
    testLoader = unittest.defaultTestLoader
    module = '__main__'
    progName = 'test'
    test = 'test'
    eleza __init__(self, *args):
        pita

RESULT = object()

kundi FakeRunner(object):
    initArgs = Tupu
    test = Tupu
    raiseError = 0

    eleza __init__(self, **kwargs):
        FakeRunner.initArgs = kwargs
        ikiwa FakeRunner.raiseError:
            FakeRunner.raiseError -= 1
            ashiria TypeError

    eleza run(self, test):
        FakeRunner.test = test
        rudisha RESULT


kundi TestCommandLineArgs(unittest.TestCase):

    eleza setUp(self):
        self.program = InitialisableProgram()
        self.program.createTests = lambda: Tupu
        FakeRunner.initArgs = Tupu
        FakeRunner.test = Tupu
        FakeRunner.raiseError = 0

    eleza testVerbosity(self):
        program = self.program

        kila opt kwenye '-q', '--quiet':
            program.verbosity = 1
            program.parseArgs([Tupu, opt])
            self.assertEqual(program.verbosity, 0)

        kila opt kwenye '-v', '--verbose':
            program.verbosity = 1
            program.parseArgs([Tupu, opt])
            self.assertEqual(program.verbosity, 2)

    eleza testBufferCatchFailfast(self):
        program = self.program
        kila arg, attr kwenye (('buffer', 'buffer'), ('failfast', 'failfast'),
                      ('catch', 'catchkoma')):
            ikiwa attr == 'catch' na sio hasInstallHandler:
                endelea

            setattr(program, attr, Tupu)
            program.parseArgs([Tupu])
            self.assertIs(getattr(program, attr), Uongo)

            false = []
            setattr(program, attr, false)
            program.parseArgs([Tupu])
            self.assertIs(getattr(program, attr), false)

            true = [42]
            setattr(program, attr, true)
            program.parseArgs([Tupu])
            self.assertIs(getattr(program, attr), true)

            short_opt = '-%s' % arg[0]
            long_opt = '--%s' % arg
            kila opt kwenye short_opt, long_opt:
                setattr(program, attr, Tupu)
                program.parseArgs([Tupu, opt])
                self.assertIs(getattr(program, attr), Kweli)

                setattr(program, attr, Uongo)
                ukijumuisha support.captured_stderr() kama stderr, \
                    self.assertRaises(SystemExit) kama cm:
                    program.parseArgs([Tupu, opt])
                self.assertEqual(cm.exception.args, (2,))

                setattr(program, attr, Kweli)
                ukijumuisha support.captured_stderr() kama stderr, \
                    self.assertRaises(SystemExit) kama cm:
                    program.parseArgs([Tupu, opt])
                self.assertEqual(cm.exception.args, (2,))

    eleza testWarning(self):
        """Test the warnings argument"""
        # see #10535
        kundi FakeTP(unittest.TestProgram):
            eleza parseArgs(self, *args, **kw): pita
            eleza runTests(self, *args, **kw): pita
        warnoptions = sys.warnoptions[:]
        jaribu:
            sys.warnoptions[:] = []
            # no warn options, no arg -> default
            self.assertEqual(FakeTP().warnings, 'default')
            # no warn options, w/ arg -> arg value
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
            sys.warnoptions[:] = ['somevalue']
            # warn options, no arg -> Tupu
            # warn options, w/ arg -> arg value
            self.assertEqual(FakeTP().warnings, Tupu)
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
        mwishowe:
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
                                                'tb_locals': Uongo,
                                                'warnings': 'warnings'})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    eleza testRunTestsRunnerInstance(self):
        program = self.program

        program.testRunner = FakeRunner()
        FakeRunner.initArgs = Tupu

        program.runTests()

        # A new FakeRunner should sio have been instantiated
        self.assertIsTupu(FakeRunner.initArgs)

        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    eleza test_locals(self):
        program = self.program

        program.testRunner = FakeRunner
        program.parseArgs([Tupu, '--locals'])
        self.assertEqual(Kweli, program.tb_locals)
        program.runTests()
        self.assertEqual(FakeRunner.initArgs, {'buffer': Uongo,
                                               'failfast': Uongo,
                                               'tb_locals': Kweli,
                                               'verbosity': 1,
                                               'warnings': Tupu})

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

        self.installed = Uongo
        eleza fakeInstallHandler():
            self.installed = Kweli
        module.installHandler = fakeInstallHandler

        program = self.program
        program.catchkoma = Kweli

        program.testRunner = FakeRunner

        program.runTests()
        self.assertKweli(self.installed)

    eleza _patch_isfile(self, names, exists=Kweli):
        eleza isfile(path):
            rudisha path kwenye names
        original = os.path.isfile
        os.path.isfile = isfile
        eleza restore():
            os.path.isfile = original
        self.addCleanup(restore)


    eleza testParseArgsFileNames(self):
        # running tests ukijumuisha filenames instead of module names
        program = self.program
        argv = ['progname', 'foo.py', 'bar.Py', 'baz.PY', 'wing.txt']
        self._patch_isfile(argv)

        program.createTests = lambda: Tupu
        program.parseArgs(argv)

        # note that 'wing.txt' ni sio a Python file so the name should
        # *not* be converted to a module name
        expected = ['foo', 'bar', 'baz', 'wing.txt']
        self.assertEqual(program.testNames, expected)


    eleza testParseArgsFilePaths(self):
        program = self.program
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        self._patch_isfile(argv)

        program.createTests = lambda: Tupu
        program.parseArgs(argv)

        expected = ['foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)


    eleza testParseArgsNonExistentFiles(self):
        program = self.program
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        self._patch_isfile([])

        program.createTests = lambda: Tupu
        program.parseArgs(argv)

        self.assertEqual(program.testNames, argv[1:])

    eleza testParseArgsAbsolutePathsThatCanBeConverted(self):
        cur_dir = os.getcwd()
        program = self.program
        eleza _join(name):
            rudisha os.path.join(cur_dir, name)
        argv = ['progname', _join('foo/bar/baz.py'), _join('green\\red.py')]
        self._patch_isfile(argv)

        program.createTests = lambda: Tupu
        program.parseArgs(argv)

        expected = ['foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)

    eleza testParseArgsAbsolutePathsThatCannotBeConverted(self):
        program = self.program
        # even on Windows '/...' ni considered absolute by os.path.abspath
        argv = ['progname', '/foo/bar/baz.py', '/green/red.py']
        self._patch_isfile(argv)

        program.createTests = lambda: Tupu
        program.parseArgs(argv)

        self.assertEqual(program.testNames, argv[1:])

        # it may be better to use platform specific functions to normalise paths
        # rather than accepting '.PY' na '\' kama file separator on Linux / Mac
        # it would also be better to check that a filename ni a valid module
        # identifier (we have a regex kila this kwenye loader.py)
        # kila invalid filenames should we ashiria a useful error rather than
        # leaving the current error message (agiza of filename fails) kwenye place?

    eleza testParseArgsSelectedTestNames(self):
        program = self.program
        argv = ['progname', '-k', 'foo', '-k', 'bar', '-k', '*pat*']

        program.createTests = lambda: Tupu
        program.parseArgs(argv)

        self.assertEqual(program.testNamePatterns, ['*foo*', '*bar*', '*pat*'])

    eleza testSelectedTestNamesFunctionalTest(self):
        eleza run_unittest(args):
            p = subprocess.Popen([sys.executable, '-m', 'unittest'] + args,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, cwd=os.path.dirname(__file__))
            ukijumuisha p:
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
