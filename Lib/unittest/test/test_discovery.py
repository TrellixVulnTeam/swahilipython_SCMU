agiza os.path
kutoka os.path agiza abspath
agiza re
agiza sys
agiza types
agiza pickle
kutoka test agiza support
agiza test.test_importlib.util

agiza unittest
agiza unittest.mock
agiza unittest.test


kundi TestableTestProgram(unittest.TestProgram):
    module = Tupu
    exit = Kweli
    defaultTest = failfast = catchkoma = buffer = Tupu
    verbosity = 1
    progName = ''
    testRunner = testLoader = Tupu

    eleza __init__(self):
        pita


kundi TestDiscovery(unittest.TestCase):

    # Heavily mocked tests so I can avoid hitting the filesystem
    eleza test_get_name_from_path(self):
        loader = unittest.TestLoader()
        loader._top_level_dir = '/foo'
        name = loader._get_name_from_path('/foo/bar/baz.py')
        self.assertEqual(name, 'bar.baz')

        ikiwa sio __debug__:
            # asserts are off
            rudisha

        ukijumuisha self.assertRaises(AssertionError):
            loader._get_name_from_path('/bar/baz.py')

    eleza test_find_tests(self):
        loader = unittest.TestLoader()

        original_listdir = os.listdir
        eleza restore_listdir():
            os.listdir = original_listdir
        original_isfile = os.path.isfile
        eleza restore_isfile():
            os.path.isfile = original_isfile
        original_isdir = os.path.isdir
        eleza restore_isdir():
            os.path.isdir = original_isdir

        path_lists = [['test2.py', 'test1.py', 'not_a_test.py', 'test_dir',
                       'test.foo', 'test-not-a-module.py', 'another_dir'],
                      ['test4.py', 'test3.py', ]]
        os.listdir = lambda path: path_lists.pop(0)
        self.addCleanup(restore_listdir)

        eleza isdir(path):
            rudisha path.endswith('dir')
        os.path.isdir = isdir
        self.addCleanup(restore_isdir)

        eleza isfile(path):
            # another_dir ni sio a package na so shouldn't be recursed into
            rudisha sio path.endswith('dir') na sio 'another_dir' kwenye path
        os.path.isfile = isfile
        self.addCleanup(restore_isfile)

        loader._get_module_from_name = lambda path: path + ' module'
        orig_load_tests = loader.loadTestsFromModule
        eleza loadTestsFromModule(module, pattern=Tupu):
            # This ni where load_tests ni called.
            base = orig_load_tests(module, pattern=pattern)
            rudisha base + [module + ' tests']
        loader.loadTestsFromModule = loadTestsFromModule
        loader.suiteClass = lambda thing: thing

        top_level = os.path.abspath('/foo')
        loader._top_level_dir = top_level
        suite = list(loader._find_tests(top_level, 'test*.py'))

        # The test suites found should be sorted alphabetically kila reliable
        # execution order.
        expected = [[name + ' module tests'] kila name kwenye
                    ('test1', 'test2', 'test_dir')]
        expected.extend([[('test_dir.%s' % name) + ' module tests'] kila name kwenye
                    ('test3', 'test4')])
        self.assertEqual(suite, expected)

    eleza test_find_tests_socket(self):
        # A socket ni neither a directory nor a regular file.
        # https://bugs.python.org/issue25320
        loader = unittest.TestLoader()

        original_listdir = os.listdir
        eleza restore_listdir():
            os.listdir = original_listdir
        original_isfile = os.path.isfile
        eleza restore_isfile():
            os.path.isfile = original_isfile
        original_isdir = os.path.isdir
        eleza restore_isdir():
            os.path.isdir = original_isdir

        path_lists = [['socket']]
        os.listdir = lambda path: path_lists.pop(0)
        self.addCleanup(restore_listdir)

        os.path.isdir = lambda path: Uongo
        self.addCleanup(restore_isdir)

        os.path.isfile = lambda path: Uongo
        self.addCleanup(restore_isfile)

        loader._get_module_from_name = lambda path: path + ' module'
        orig_load_tests = loader.loadTestsFromModule
        eleza loadTestsFromModule(module, pattern=Tupu):
            # This ni where load_tests ni called.
            base = orig_load_tests(module, pattern=pattern)
            rudisha base + [module + ' tests']
        loader.loadTestsFromModule = loadTestsFromModule
        loader.suiteClass = lambda thing: thing

        top_level = os.path.abspath('/foo')
        loader._top_level_dir = top_level
        suite = list(loader._find_tests(top_level, 'test*.py'))

        self.assertEqual(suite, [])

    eleza test_find_tests_with_package(self):
        loader = unittest.TestLoader()

        original_listdir = os.listdir
        eleza restore_listdir():
            os.listdir = original_listdir
        original_isfile = os.path.isfile
        eleza restore_isfile():
            os.path.isfile = original_isfile
        original_isdir = os.path.isdir
        eleza restore_isdir():
            os.path.isdir = original_isdir

        directories = ['a_directory', 'test_directory', 'test_directory2']
        path_lists = [directories, [], [], []]
        os.listdir = lambda path: path_lists.pop(0)
        self.addCleanup(restore_listdir)

        os.path.isdir = lambda path: Kweli
        self.addCleanup(restore_isdir)

        os.path.isfile = lambda path: os.path.basename(path) haiko kwenye directories
        self.addCleanup(restore_isfile)

        kundi Module(object):
            paths = []
            load_tests_args = []

            eleza __init__(self, path):
                self.path = path
                self.paths.append(path)
                ikiwa os.path.basename(path) == 'test_directory':
                    eleza load_tests(loader, tests, pattern):
                        self.load_tests_args.append((loader, tests, pattern))
                        rudisha [self.path + ' load_tests']
                    self.load_tests = load_tests

            eleza __eq__(self, other):
                rudisha self.path == other.path

        loader._get_module_from_name = lambda name: Module(name)
        orig_load_tests = loader.loadTestsFromModule
        eleza loadTestsFromModule(module, pattern=Tupu):
            # This ni where load_tests ni called.
            base = orig_load_tests(module, pattern=pattern)
            rudisha base + [module.path + ' module tests']
        loader.loadTestsFromModule = loadTestsFromModule
        loader.suiteClass = lambda thing: thing

        loader._top_level_dir = '/foo'
        # this time no '.py' on the pattern so that it can match
        # a test package
        suite = list(loader._find_tests('/foo', 'test*'))

        # We should have loaded tests kutoka the a_directory na test_directory2
        # directly na via load_tests kila the test_directory package, which
        # still calls the baseline module loader.
        self.assertEqual(suite,
                         [['a_directory module tests'],
                          ['test_directory load_tests',
                           'test_directory module tests'],
                          ['test_directory2 module tests']])


        # The test module paths should be sorted kila reliable execution order
        self.assertEqual(Module.paths,
                         ['a_directory', 'test_directory', 'test_directory2'])

        # load_tests should have been called once ukijumuisha loader, tests na pattern
        # (but there are no tests kwenye our stub module itself, so that ni [] at
        # the time of call).
        self.assertEqual(Module.load_tests_args,
                         [(loader, [], 'test*')])

    eleza test_find_tests_default_calls_package_load_tests(self):
        loader = unittest.TestLoader()

        original_listdir = os.listdir
        eleza restore_listdir():
            os.listdir = original_listdir
        original_isfile = os.path.isfile
        eleza restore_isfile():
            os.path.isfile = original_isfile
        original_isdir = os.path.isdir
        eleza restore_isdir():
            os.path.isdir = original_isdir

        directories = ['a_directory', 'test_directory', 'test_directory2']
        path_lists = [directories, [], [], []]
        os.listdir = lambda path: path_lists.pop(0)
        self.addCleanup(restore_listdir)

        os.path.isdir = lambda path: Kweli
        self.addCleanup(restore_isdir)

        os.path.isfile = lambda path: os.path.basename(path) haiko kwenye directories
        self.addCleanup(restore_isfile)

        kundi Module(object):
            paths = []
            load_tests_args = []

            eleza __init__(self, path):
                self.path = path
                self.paths.append(path)
                ikiwa os.path.basename(path) == 'test_directory':
                    eleza load_tests(loader, tests, pattern):
                        self.load_tests_args.append((loader, tests, pattern))
                        rudisha [self.path + ' load_tests']
                    self.load_tests = load_tests

            eleza __eq__(self, other):
                rudisha self.path == other.path

        loader._get_module_from_name = lambda name: Module(name)
        orig_load_tests = loader.loadTestsFromModule
        eleza loadTestsFromModule(module, pattern=Tupu):
            # This ni where load_tests ni called.
            base = orig_load_tests(module, pattern=pattern)
            rudisha base + [module.path + ' module tests']
        loader.loadTestsFromModule = loadTestsFromModule
        loader.suiteClass = lambda thing: thing

        loader._top_level_dir = '/foo'
        # this time no '.py' on the pattern so that it can match
        # a test package
        suite = list(loader._find_tests('/foo', 'test*.py'))

        # We should have loaded tests kutoka the a_directory na test_directory2
        # directly na via load_tests kila the test_directory package, which
        # still calls the baseline module loader.
        self.assertEqual(suite,
                         [['a_directory module tests'],
                          ['test_directory load_tests',
                           'test_directory module tests'],
                          ['test_directory2 module tests']])
        # The test module paths should be sorted kila reliable execution order
        self.assertEqual(Module.paths,
                         ['a_directory', 'test_directory', 'test_directory2'])


        # load_tests should have been called once ukijumuisha loader, tests na pattern
        self.assertEqual(Module.load_tests_args,
                         [(loader, [], 'test*.py')])

    eleza test_find_tests_customize_via_package_pattern(self):
        # This test uses the example 'do-nothing' load_tests from
        # https://docs.python.org/3/library/unittest.html#load-tests-protocol
        # to make sure that that actually works.
        # Housekeeping
        original_listdir = os.listdir
        eleza restore_listdir():
            os.listdir = original_listdir
        self.addCleanup(restore_listdir)
        original_isfile = os.path.isfile
        eleza restore_isfile():
            os.path.isfile = original_isfile
        self.addCleanup(restore_isfile)
        original_isdir = os.path.isdir
        eleza restore_isdir():
            os.path.isdir = original_isdir
        self.addCleanup(restore_isdir)
        self.addCleanup(sys.path.remove, abspath('/foo'))

        # Test data: we expect the following:
        # a listdir to find our package, na isfile na isdir checks on it.
        # a module-from-name call to turn that into a module
        # followed by load_tests.
        # then our load_tests will call discover() which ni messy
        # but that finally chains into find_tests again kila the child dir -
        # which ni why we don't have an infinite loop.
        # We expect to see:
        # the module load tests kila both package na plain module called,
        # na the plain module result nested by the package module load_tests
        # indicating that it was processed na could have been mutated.
        vfs = {abspath('/foo'): ['my_package'],
               abspath('/foo/my_package'): ['__init__.py', 'test_module.py']}
        eleza list_dir(path):
            rudisha list(vfs[path])
        os.listdir = list_dir
        os.path.isdir = lambda path: sio path.endswith('.py')
        os.path.isfile = lambda path: path.endswith('.py')

        kundi Module(object):
            paths = []
            load_tests_args = []

            eleza __init__(self, path):
                self.path = path
                self.paths.append(path)
                ikiwa path.endswith('test_module'):
                    eleza load_tests(loader, tests, pattern):
                        self.load_tests_args.append((loader, tests, pattern))
                        rudisha [self.path + ' load_tests']
                isipokua:
                    eleza load_tests(loader, tests, pattern):
                        self.load_tests_args.append((loader, tests, pattern))
                        # top level directory cached on loader instance
                        __file__ = '/foo/my_package/__init__.py'
                        this_dir = os.path.dirname(__file__)
                        pkg_tests = loader.discover(
                            start_dir=this_dir, pattern=pattern)
                        rudisha [self.path + ' load_tests', tests
                            ] + pkg_tests
                self.load_tests = load_tests

            eleza __eq__(self, other):
                rudisha self.path == other.path

        loader = unittest.TestLoader()
        loader._get_module_from_name = lambda name: Module(name)
        loader.suiteClass = lambda thing: thing

        loader._top_level_dir = abspath('/foo')
        # this time no '.py' on the pattern so that it can match
        # a test package
        suite = list(loader._find_tests(abspath('/foo'), 'test*.py'))

        # We should have loaded tests kutoka both my_package na
        # my_package.test_module, na also run the load_tests hook kwenye both.
        # (normally this would be nested TestSuites.)
        self.assertEqual(suite,
                         [['my_package load_tests', [],
                          ['my_package.test_module load_tests']]])
        # Parents before children.
        self.assertEqual(Module.paths,
                         ['my_package', 'my_package.test_module'])

        # load_tests should have been called twice ukijumuisha loader, tests na pattern
        self.assertEqual(Module.load_tests_args,
                         [(loader, [], 'test*.py'),
                          (loader, [], 'test*.py')])

    eleza test_discover(self):
        loader = unittest.TestLoader()

        original_isfile = os.path.isfile
        original_isdir = os.path.isdir
        eleza restore_isfile():
            os.path.isfile = original_isfile

        os.path.isfile = lambda path: Uongo
        self.addCleanup(restore_isfile)

        orig_sys_path = sys.path[:]
        eleza restore_path():
            sys.path[:] = orig_sys_path
        self.addCleanup(restore_path)

        full_path = os.path.abspath(os.path.normpath('/foo'))
        ukijumuisha self.assertRaises(ImportError):
            loader.discover('/foo/bar', top_level_dir='/foo')

        self.assertEqual(loader._top_level_dir, full_path)
        self.assertIn(full_path, sys.path)

        os.path.isfile = lambda path: Kweli
        os.path.isdir = lambda path: Kweli

        eleza restore_isdir():
            os.path.isdir = original_isdir
        self.addCleanup(restore_isdir)

        _find_tests_args = []
        eleza _find_tests(start_dir, pattern, namespace=Tupu):
            _find_tests_args.append((start_dir, pattern))
            rudisha ['tests']
        loader._find_tests = _find_tests
        loader.suiteClass = str

        suite = loader.discover('/foo/bar/baz', 'pattern', '/foo/bar')

        top_level_dir = os.path.abspath('/foo/bar')
        start_dir = os.path.abspath('/foo/bar/baz')
        self.assertEqual(suite, "['tests']")
        self.assertEqual(loader._top_level_dir, top_level_dir)
        self.assertEqual(_find_tests_args, [(start_dir, 'pattern')])
        self.assertIn(top_level_dir, sys.path)

    eleza test_discover_start_dir_is_package_calls_package_load_tests(self):
        # This test verifies that the package load_tests kwenye a package ni indeed
        # invoked when the start_dir ni a package (and sio the top level).
        # http://bugs.python.org/issue22457

        # Test data: we expect the following:
        # an isfile to verify the package, then importing na scanning
        # kama per _find_tests' normal behaviour.
        # We expect to see our load_tests hook called once.
        vfs = {abspath('/toplevel'): ['startdir'],
               abspath('/toplevel/startdir'): ['__init__.py']}
        eleza list_dir(path):
            rudisha list(vfs[path])
        self.addCleanup(setattr, os, 'listdir', os.listdir)
        os.listdir = list_dir
        self.addCleanup(setattr, os.path, 'isfile', os.path.isfile)
        os.path.isfile = lambda path: path.endswith('.py')
        self.addCleanup(setattr, os.path, 'isdir', os.path.isdir)
        os.path.isdir = lambda path: sio path.endswith('.py')
        self.addCleanup(sys.path.remove, abspath('/toplevel'))

        kundi Module(object):
            paths = []
            load_tests_args = []

            eleza __init__(self, path):
                self.path = path

            eleza load_tests(self, loader, tests, pattern):
                rudisha ['load_tests called ' + self.path]

            eleza __eq__(self, other):
                rudisha self.path == other.path

        loader = unittest.TestLoader()
        loader._get_module_from_name = lambda name: Module(name)
        loader.suiteClass = lambda thing: thing

        suite = loader.discover('/toplevel/startdir', top_level_dir='/toplevel')

        # We should have loaded tests kutoka the package __init__.
        # (normally this would be nested TestSuites.)
        self.assertEqual(suite,
                         [['load_tests called startdir']])

    eleza setup_import_issue_tests(self, fakefile):
        listdir = os.listdir
        os.listdir = lambda _: [fakefile]
        isfile = os.path.isfile
        os.path.isfile = lambda _: Kweli
        orig_sys_path = sys.path[:]
        eleza restore():
            os.path.isfile = isfile
            os.listdir = listdir
            sys.path[:] = orig_sys_path
        self.addCleanup(restore)

    eleza setup_import_issue_package_tests(self, vfs):
        self.addCleanup(setattr, os, 'listdir', os.listdir)
        self.addCleanup(setattr, os.path, 'isfile', os.path.isfile)
        self.addCleanup(setattr, os.path, 'isdir', os.path.isdir)
        self.addCleanup(sys.path.__setitem__, slice(Tupu), list(sys.path))
        eleza list_dir(path):
            rudisha list(vfs[path])
        os.listdir = list_dir
        os.path.isdir = lambda path: sio path.endswith('.py')
        os.path.isfile = lambda path: path.endswith('.py')

    eleza test_discover_with_modules_that_fail_to_import(self):
        loader = unittest.TestLoader()

        self.setup_import_issue_tests('test_this_does_not_exist.py')

        suite = loader.discover('.')
        self.assertIn(os.getcwd(), sys.path)
        self.assertEqual(suite.countTestCases(), 1)
        # Errors loading the suite are also captured kila introspection.
        self.assertNotEqual([], loader.errors)
        self.assertEqual(1, len(loader.errors))
        error = loader.errors[0]
        self.assertKweli(
            'Failed to agiza test module: test_this_does_not_exist' kwenye error,
            'missing error string kwenye %r' % error)
        test = list(list(suite)[0])[0] # extract test kutoka suite

        ukijumuisha self.assertRaises(ImportError):
            test.test_this_does_not_exist()

    eleza test_discover_with_init_modules_that_fail_to_import(self):
        vfs = {abspath('/foo'): ['my_package'],
               abspath('/foo/my_package'): ['__init__.py', 'test_module.py']}
        self.setup_import_issue_package_tests(vfs)
        import_calls = []
        eleza _get_module_from_name(name):
            import_calls.append(name)
            ashiria ImportError("Cannot agiza Name")
        loader = unittest.TestLoader()
        loader._get_module_from_name = _get_module_from_name
        suite = loader.discover(abspath('/foo'))

        self.assertIn(abspath('/foo'), sys.path)
        self.assertEqual(suite.countTestCases(), 1)
        # Errors loading the suite are also captured kila introspection.
        self.assertNotEqual([], loader.errors)
        self.assertEqual(1, len(loader.errors))
        error = loader.errors[0]
        self.assertKweli(
            'Failed to agiza test module: my_package' kwenye error,
            'missing error string kwenye %r' % error)
        test = list(list(suite)[0])[0] # extract test kutoka suite
        ukijumuisha self.assertRaises(ImportError):
            test.my_package()
        self.assertEqual(import_calls, ['my_package'])

        # Check picklability
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickle.loads(pickle.dumps(test, proto))

    eleza test_discover_with_module_that_raises_SkipTest_on_import(self):
        ikiwa sio unittest.BaseTestSuite._cleanup:
            ashiria unittest.SkipTest("Suite cleanup ni disabled")

        loader = unittest.TestLoader()

        eleza _get_module_from_name(name):
            ashiria unittest.SkipTest('skipperoo')
        loader._get_module_from_name = _get_module_from_name

        self.setup_import_issue_tests('test_skip_dummy.py')

        suite = loader.discover('.')
        self.assertEqual(suite.countTestCases(), 1)

        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(len(result.skipped), 1)

        # Check picklability
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickle.loads(pickle.dumps(suite, proto))

    eleza test_discover_with_init_module_that_raises_SkipTest_on_import(self):
        ikiwa sio unittest.BaseTestSuite._cleanup:
            ashiria unittest.SkipTest("Suite cleanup ni disabled")

        vfs = {abspath('/foo'): ['my_package'],
               abspath('/foo/my_package'): ['__init__.py', 'test_module.py']}
        self.setup_import_issue_package_tests(vfs)
        import_calls = []
        eleza _get_module_from_name(name):
            import_calls.append(name)
            ashiria unittest.SkipTest('skipperoo')
        loader = unittest.TestLoader()
        loader._get_module_from_name = _get_module_from_name
        suite = loader.discover(abspath('/foo'))

        self.assertIn(abspath('/foo'), sys.path)
        self.assertEqual(suite.countTestCases(), 1)
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(len(result.skipped), 1)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(import_calls, ['my_package'])

        # Check picklability
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            pickle.loads(pickle.dumps(suite, proto))

    eleza test_command_line_handling_parseArgs(self):
        program = TestableTestProgram()

        args = []
        program._do_discovery = args.append
        program.parseArgs(['something', 'discover'])
        self.assertEqual(args, [[]])

        args[:] = []
        program.parseArgs(['something', 'discover', 'foo', 'bar'])
        self.assertEqual(args, [['foo', 'bar']])

    eleza test_command_line_handling_discover_by_default(self):
        program = TestableTestProgram()

        args = []
        program._do_discovery = args.append
        program.parseArgs(['something'])
        self.assertEqual(args, [[]])
        self.assertEqual(program.verbosity, 1)
        self.assertIs(program.buffer, Uongo)
        self.assertIs(program.catchkoma, Uongo)
        self.assertIs(program.failfast, Uongo)

    eleza test_command_line_handling_discover_by_default_with_options(self):
        program = TestableTestProgram()

        args = []
        program._do_discovery = args.append
        program.parseArgs(['something', '-v', '-b', '-v', '-c', '-f'])
        self.assertEqual(args, [[]])
        self.assertEqual(program.verbosity, 2)
        self.assertIs(program.buffer, Kweli)
        self.assertIs(program.catchkoma, Kweli)
        self.assertIs(program.failfast, Kweli)


    eleza test_command_line_handling_do_discovery_too_many_arguments(self):
        program = TestableTestProgram()
        program.testLoader = Tupu

        ukijumuisha support.captured_stderr() kama stderr, \
             self.assertRaises(SystemExit) kama cm:
            # too many args
            program._do_discovery(['one', 'two', 'three', 'four'])
        self.assertEqual(cm.exception.args, (2,))
        self.assertIn('usage:', stderr.getvalue())


    eleza test_command_line_handling_do_discovery_uses_default_loader(self):
        program = object.__new__(unittest.TestProgram)
        program._initArgParsers()

        kundi Loader(object):
            args = []
            eleza discover(self, start_dir, pattern, top_level_dir):
                self.args.append((start_dir, pattern, top_level_dir))
                rudisha 'tests'

        program.testLoader = Loader()
        program._do_discovery(['-v'])
        self.assertEqual(Loader.args, [('.', 'test*.py', Tupu)])

    eleza test_command_line_handling_do_discovery_calls_loader(self):
        program = TestableTestProgram()

        kundi Loader(object):
            args = []
            eleza discover(self, start_dir, pattern, top_level_dir):
                self.args.append((start_dir, pattern, top_level_dir))
                rudisha 'tests'

        program._do_discovery(['-v'], Loader=Loader)
        self.assertEqual(program.verbosity, 2)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'test*.py', Tupu)])

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery(['--verbose'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'test*.py', Tupu)])

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery([], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'test*.py', Tupu)])

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery(['fish'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'test*.py', Tupu)])

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery(['fish', 'eggs'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'eggs', Tupu)])

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery(['fish', 'eggs', 'ham'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'eggs', 'ham')])

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery(['-s', 'fish'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'test*.py', Tupu)])

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery(['-t', 'fish'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'test*.py', 'fish')])

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery(['-p', 'fish'], Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('.', 'fish', Tupu)])
        self.assertUongo(program.failfast)
        self.assertUongo(program.catchkoma)

        Loader.args = []
        program = TestableTestProgram()
        program._do_discovery(['-p', 'eggs', '-s', 'fish', '-v', '-f', '-c'],
                              Loader=Loader)
        self.assertEqual(program.test, 'tests')
        self.assertEqual(Loader.args, [('fish', 'eggs', Tupu)])
        self.assertEqual(program.verbosity, 2)
        self.assertKweli(program.failfast)
        self.assertKweli(program.catchkoma)

    eleza setup_module_clash(self):
        kundi Module(object):
            __file__ = 'bar/foo.py'
        sys.modules['foo'] = Module
        full_path = os.path.abspath('foo')
        original_listdir = os.listdir
        original_isfile = os.path.isfile
        original_isdir = os.path.isdir
        original_realpath = os.path.realpath

        eleza cleanup():
            os.listdir = original_listdir
            os.path.isfile = original_isfile
            os.path.isdir = original_isdir
            os.path.realpath = original_realpath
            toa sys.modules['foo']
            ikiwa full_path kwenye sys.path:
                sys.path.remove(full_path)
        self.addCleanup(cleanup)

        eleza listdir(_):
            rudisha ['foo.py']
        eleza isfile(_):
            rudisha Kweli
        eleza isdir(_):
            rudisha Kweli
        os.listdir = listdir
        os.path.isfile = isfile
        os.path.isdir = isdir
        ikiwa os.name == 'nt':
            # ntpath.realpath may inject path prefixes when failing to
            # resolve real files, so we substitute abspath() here instead.
            os.path.realpath = os.path.abspath
        rudisha full_path

    eleza test_detect_module_clash(self):
        full_path = self.setup_module_clash()
        loader = unittest.TestLoader()

        mod_dir = os.path.abspath('bar')
        expected_dir = os.path.abspath('foo')
        msg = re.escape(r"'foo' module incorrectly imported kutoka %r. Expected %r. "
                "Is this module globally installed?" % (mod_dir, expected_dir))
        self.assertRaisesRegex(
            ImportError, '^%s$' % msg, loader.discover,
            start_dir='foo', pattern='foo.py'
        )
        self.assertEqual(sys.path[0], full_path)

    eleza test_module_symlink_ok(self):
        full_path = self.setup_module_clash()

        original_realpath = os.path.realpath

        mod_dir = os.path.abspath('bar')
        expected_dir = os.path.abspath('foo')

        eleza cleanup():
            os.path.realpath = original_realpath
        self.addCleanup(cleanup)

        eleza realpath(path):
            ikiwa path == os.path.join(mod_dir, 'foo.py'):
                rudisha os.path.join(expected_dir, 'foo.py')
            rudisha path
        os.path.realpath = realpath
        loader = unittest.TestLoader()
        loader.discover(start_dir='foo', pattern='foo.py')

    eleza test_discovery_from_dotted_path(self):
        loader = unittest.TestLoader()

        tests = [self]
        expectedPath = os.path.abspath(os.path.dirname(unittest.test.__file__))

        self.wasRun = Uongo
        eleza _find_tests(start_dir, pattern, namespace=Tupu):
            self.wasRun = Kweli
            self.assertEqual(start_dir, expectedPath)
            rudisha tests
        loader._find_tests = _find_tests
        suite = loader.discover('unittest.test')
        self.assertKweli(self.wasRun)
        self.assertEqual(suite._tests, tests)


    eleza test_discovery_from_dotted_path_builtin_modules(self):

        loader = unittest.TestLoader()

        listdir = os.listdir
        os.listdir = lambda _: ['test_this_does_not_exist.py']
        isfile = os.path.isfile
        isdir = os.path.isdir
        os.path.isdir = lambda _: Uongo
        orig_sys_path = sys.path[:]
        eleza restore():
            os.path.isfile = isfile
            os.path.isdir = isdir
            os.listdir = listdir
            sys.path[:] = orig_sys_path
        self.addCleanup(restore)

        ukijumuisha self.assertRaises(TypeError) kama cm:
            loader.discover('sys')
        self.assertEqual(str(cm.exception),
                         'Can sio use builtin modules '
                         'as dotted module names')

    eleza test_discovery_from_dotted_namespace_packages(self):
        loader = unittest.TestLoader()

        package = types.ModuleType('package')
        package.__path__ = ['/a', '/b']
        package.__spec__ = types.SimpleNamespace(
           loader=Tupu,
           submodule_search_locations=['/a', '/b']
        )

        eleza _import(packagename, *args, **kwargs):
            sys.modules[packagename] = package
            rudisha package

        _find_tests_args = []
        eleza _find_tests(start_dir, pattern, namespace=Tupu):
            _find_tests_args.append((start_dir, pattern))
            rudisha ['%s/tests' % start_dir]

        loader._find_tests = _find_tests
        loader.suiteClass = list

        ukijumuisha unittest.mock.patch('builtins.__import__', _import):
            # Since loader.discover() can modify sys.path, restore it when done.
            ukijumuisha support.DirsOnSysPath():
                # Make sure to remove 'package' kutoka sys.modules when done.
                ukijumuisha test.test_importlib.util.uncache('package'):
                    suite = loader.discover('package')

        self.assertEqual(suite, ['/a/tests', '/b/tests'])

    eleza test_discovery_failed_discovery(self):
        loader = unittest.TestLoader()
        package = types.ModuleType('package')

        eleza _import(packagename, *args, **kwargs):
            sys.modules[packagename] = package
            rudisha package

        ukijumuisha unittest.mock.patch('builtins.__import__', _import):
            # Since loader.discover() can modify sys.path, restore it when done.
            ukijumuisha support.DirsOnSysPath():
                # Make sure to remove 'package' kutoka sys.modules when done.
                ukijumuisha test.test_importlib.util.uncache('package'):
                    ukijumuisha self.assertRaises(TypeError) kama cm:
                        loader.discover('package')
                    self.assertEqual(str(cm.exception),
                                     'don\'t know how to discover kutoka {!r}'
                                     .format(package))


ikiwa __name__ == '__main__':
    unittest.main()
