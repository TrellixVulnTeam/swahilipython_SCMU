agiza functools
agiza sys
agiza types
agiza warnings

agiza unittest

# Decorator used in the deprecation tests to reset the warning registry for
# test isolation and reproducibility.
eleza warningregistry(func):
    eleza wrapper(*args, **kws):
        missing = []
        saved = getattr(warnings, '__warningregistry__', missing).copy()
        try:
            rudisha func(*args, **kws)
        finally:
            ikiwa saved is missing:
                try:
                    del warnings.__warningregistry__
                except AttributeError:
                    pass
            else:
                warnings.__warningregistry__ = saved
    rudisha wrapper


kundi Test_TestLoader(unittest.TestCase):

    ### Basic object tests
    ################################################################

    eleza test___init__(self):
        loader = unittest.TestLoader()
        self.assertEqual([], loader.errors)

    ### Tests for TestLoader.loadTestsFromTestCase
    ################################################################

    # "Return a suite of all test cases contained in the TestCase-derived
    # kundi testCaseClass"
    eleza test_loadTestsFromTestCase(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass

        tests = unittest.TestSuite([Foo('test_1'), Foo('test_2')])

        loader = unittest.TestLoader()
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    # "Return a suite of all test cases contained in the TestCase-derived
    # kundi testCaseClass"
    #
    # Make sure it does the right thing even ikiwa no tests were found
    eleza test_loadTestsFromTestCase__no_matches(self):
        kundi Foo(unittest.TestCase):
            eleza foo_bar(self): pass

        empty_suite = unittest.TestSuite()

        loader = unittest.TestLoader()
        self.assertEqual(loader.loadTestsFromTestCase(Foo), empty_suite)

    # "Return a suite of all test cases contained in the TestCase-derived
    # kundi testCaseClass"
    #
    # What happens ikiwa loadTestsFromTestCase() is given an object
    # that isn't a subkundi of TestCase? Specifically, what happens
    # ikiwa testCaseClass is a subkundi of TestSuite?
    #
    # This is checked for specifically in the code, so we better add a
    # test for it.
    eleza test_loadTestsFromTestCase__TestSuite_subclass(self):
        kundi NotATestCase(unittest.TestSuite):
            pass

        loader = unittest.TestLoader()
        try:
            loader.loadTestsFromTestCase(NotATestCase)
        except TypeError:
            pass
        else:
            self.fail('Should raise TypeError')

    # "Return a suite of all test cases contained in the TestCase-derived
    # kundi testCaseClass"
    #
    # Make sure loadTestsFromTestCase() picks up the default test method
    # name (as specified by TestCase), even though the method name does
    # not match the default TestLoader.testMethodPrefix string
    eleza test_loadTestsFromTestCase__default_method_name(self):
        kundi Foo(unittest.TestCase):
            eleza runTest(self):
                pass

        loader = unittest.TestLoader()
        # This has to be false for the test to succeed
        self.assertFalse('runTest'.startswith(loader.testMethodPrefix))

        suite = loader.loadTestsFromTestCase(Foo)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [Foo('runTest')])

    ################################################################
    ### /Tests for TestLoader.loadTestsFromTestCase

    ### Tests for TestLoader.loadTestsFromModule
    ################################################################

    # "This method searches `module` for classes derived kutoka TestCase"
    eleza test_loadTestsFromModule__TestCase_subclass(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)

        expected = [loader.suiteClass([MyTestCase('test')])]
        self.assertEqual(list(suite), expected)

    # "This method searches `module` for classes derived kutoka TestCase"
    #
    # What happens ikiwa no tests are found (no TestCase instances)?
    eleza test_loadTestsFromModule__no_TestCase_instances(self):
        m = types.ModuleType('m')

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    # "This method searches `module` for classes derived kutoka TestCase"
    #
    # What happens ikiwa no tests are found (TestCases instances, but no tests)?
    eleza test_loadTestsFromModule__no_TestCase_tests(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [loader.suiteClass()])

    # "This method searches `module` for classes derived kutoka TestCase"s
    #
    # What happens ikiwa loadTestsFromModule() is given something other
    # than a module?
    #
    # XXX Currently, it succeeds anyway. This flexibility
    # should either be documented or loadTestsFromModule() should
    # raise a TypeError
    #
    # XXX Certain people are using this behaviour. We'll add a test for it
    eleza test_loadTestsFromModule__not_a_module(self):
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass

        kundi NotAModule(object):
            test_2 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(NotAModule)

        reference = [unittest.TestSuite([MyTestCase('test')])]
        self.assertEqual(list(suite), reference)


    # Check that loadTestsFromModule honors (or not) a module
    # with a load_tests function.
    @warningregistry
    eleza test_loadTestsFromModule__load_tests(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        load_tests_args = []
        eleza load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            rudisha tests
        m.load_tests = load_tests

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertEqual(load_tests_args, [loader, suite, None])
        # With Python 3.5, the undocumented and unofficial use_load_tests is
        # ignored (and deprecated).
        load_tests_args = []
        with warnings.catch_warnings(record=False):
            warnings.simplefilter('ignore')
            suite = loader.loadTestsFromModule(m, use_load_tests=False)
        self.assertEqual(load_tests_args, [loader, suite, None])

    @warningregistry
    eleza test_loadTestsFromModule__use_load_tests_deprecated_positional(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        load_tests_args = []
        eleza load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            rudisha tests
        m.load_tests = load_tests
        # The method still works.
        loader = unittest.TestLoader()
        # use_load_tests=True as a positional argument.
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            suite = loader.loadTestsFromModule(m, False)
        self.assertIsInstance(suite, unittest.TestSuite)
        # load_tests was still called because use_load_tests is deprecated
        # and ignored.
        self.assertEqual(load_tests_args, [loader, suite, None])
        # We got a warning.
        self.assertIs(w[-1].category, DeprecationWarning)
        self.assertEqual(str(w[-1].message),
                             'use_load_tests is deprecated and ignored')

    @warningregistry
    eleza test_loadTestsFromModule__use_load_tests_deprecated_keyword(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        load_tests_args = []
        eleza load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            rudisha tests
        m.load_tests = load_tests
        # The method still works.
        loader = unittest.TestLoader()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            suite = loader.loadTestsFromModule(m, use_load_tests=False)
        self.assertIsInstance(suite, unittest.TestSuite)
        # load_tests was still called because use_load_tests is deprecated
        # and ignored.
        self.assertEqual(load_tests_args, [loader, suite, None])
        # We got a warning.
        self.assertIs(w[-1].category, DeprecationWarning)
        self.assertEqual(str(w[-1].message),
                             'use_load_tests is deprecated and ignored')

    @warningregistry
    eleza test_loadTestsFromModule__too_many_positional_args(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        load_tests_args = []
        eleza load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            rudisha tests
        m.load_tests = load_tests
        loader = unittest.TestLoader()
        with self.assertRaises(TypeError) as cm, \
             warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            loader.loadTestsFromModule(m, False, 'testme.*')
        # We still got the deprecation warning.
        self.assertIs(w[-1].category, DeprecationWarning)
        self.assertEqual(str(w[-1].message),
                                'use_load_tests is deprecated and ignored')
        # We also got a TypeError for too many positional arguments.
        self.assertEqual(type(cm.exception), TypeError)
        self.assertEqual(
            str(cm.exception),
            'loadTestsFromModule() takes 1 positional argument but 3 were given')

    @warningregistry
    eleza test_loadTestsFromModule__use_load_tests_other_bad_keyword(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        load_tests_args = []
        eleza load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            rudisha tests
        m.load_tests = load_tests
        loader = unittest.TestLoader()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with self.assertRaises(TypeError) as cm:
                loader.loadTestsFromModule(
                    m, use_load_tests=False, very_bad=True, worse=False)
        self.assertEqual(type(cm.exception), TypeError)
        # The error message names the first bad argument alphabetically,
        # however use_load_tests (which sorts first) is ignored.
        self.assertEqual(
            str(cm.exception),
            "loadTestsFromModule() got an unexpected keyword argument 'very_bad'")

    eleza test_loadTestsFromModule__pattern(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        load_tests_args = []
        eleza load_tests(loader, tests, pattern):
            self.assertIsInstance(tests, unittest.TestSuite)
            load_tests_args.extend((loader, tests, pattern))
            rudisha tests
        m.load_tests = load_tests

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m, pattern='testme.*')
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertEqual(load_tests_args, [loader, suite, 'testme.*'])

    eleza test_loadTestsFromModule__faulty_load_tests(self):
        m = types.ModuleType('m')

        eleza load_tests(loader, tests, pattern):
            raise TypeError('some failure')
        m.load_tests = load_tests

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(m)
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertEqual(suite.countTestCases(), 1)
        # Errors loading the suite are also captured for introspection.
        self.assertNotEqual([], loader.errors)
        self.assertEqual(1, len(loader.errors))
        error = loader.errors[0]
        self.assertTrue(
            'Failed to call load_tests:' in error,
            'missing error string in %r' % error)
        test = list(suite)[0]

        self.assertRaisesRegex(TypeError, "some failure", test.m)

    ################################################################
    ### /Tests for TestLoader.loadTestsFromModule()

    ### Tests for TestLoader.loadTestsFromName()
    ################################################################

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # Is ValueError raised in response to an empty name?
    eleza test_loadTestsFromName__empty_name(self):
        loader = unittest.TestLoader()

        try:
            loader.loadTestsFromName('')
        except ValueError as e:
            self.assertEqual(str(e), "Empty module name")
        else:
            self.fail("TestLoader.loadTestsFromName failed to raise ValueError")

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # What happens when the name contains invalid characters?
    eleza test_loadTestsFromName__malformed_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('abc () //')
        error, test = self.check_deferred_error(loader, suite)
        expected = "Failed to agiza test module: abc () //"
        expected_regex = r"Failed to agiza test module: abc \(\) //"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(
            ImportError, expected_regex, getattr(test, 'abc () //'))

    # "The specifier name is a ``dotted name'' that may resolve ... to a
    # module"
    #
    # What happens when a module by that name can't be found?
    eleza test_loadTestsFromName__unknown_module_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('sdasfasfasdf')
        expected = "No module named 'sdasfasfasdf'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(ImportError, expected, test.sdasfasfasdf)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # What happens when the module is found, but the attribute isn't?
    eleza test_loadTestsFromName__unknown_attr_name_on_module(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('unittest.loader.sdasfasfasdf')
        expected = "module 'unittest.loader' has no attribute 'sdasfasfasdf'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # What happens when the module is found, but the attribute isn't?
    eleza test_loadTestsFromName__unknown_attr_name_on_package(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('unittest.sdasfasfasdf')
        expected = "No module named 'unittest.sdasfasfasdf'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(ImportError, expected, test.sdasfasfasdf)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # What happens when we provide the module, but the attribute can't be
    # found?
    eleza test_loadTestsFromName__relative_unknown_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('sdasfasfasdf', unittest)
        expected = "module 'unittest' has no attribute 'sdasfasfasdf'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # Does loadTestsFromName raise ValueError when passed an empty
    # name relative to a provided module?
    #
    # XXX Should probably raise a ValueError instead of an AttributeError
    eleza test_loadTestsFromName__relative_empty_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromName('', unittest)
        error, test = self.check_deferred_error(loader, suite)
        expected = "has no attribute ''"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, getattr(test, ''))

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens when an impossible name is given, relative to the provided
    # `module`?
    eleza test_loadTestsFromName__relative_malformed_name(self):
        loader = unittest.TestLoader()

        # XXX Should this raise AttributeError or ValueError?
        suite = loader.loadTestsFromName('abc () //', unittest)
        error, test = self.check_deferred_error(loader, suite)
        expected = "module 'unittest' has no attribute 'abc () //'"
        expected_regex = r"module 'unittest' has no attribute 'abc \(\) //'"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(
            AttributeError, expected_regex, getattr(test, 'abc () //'))

    # "The method optionally resolves name relative to the given module"
    #
    # Does loadTestsFromName raise TypeError when the `module` argument
    # isn't a module object?
    #
    # XXX Accepts the not-a-module object, ignoring the object's type
    # This should raise an exception or the method name should be changed
    #
    # XXX Some people are relying on this, so keep it for now
    eleza test_loadTestsFromName__relative_not_a_module(self):
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass

        kundi NotAModule(object):
            test_2 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('test_2', NotAModule)

        reference = [MyTestCase('test')]
        self.assertEqual(list(suite), reference)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # Does it raise an exception ikiwa the name resolves to an invalid
    # object?
    eleza test_loadTestsFromName__relative_bad_object(self):
        m = types.ModuleType('m')
        m.testcase_1 = object()

        loader = unittest.TestLoader()
        try:
            loader.loadTestsFromName('testcase_1', m)
        except TypeError:
            pass
        else:
            self.fail("Should have raised TypeError")

    # "The specifier name is a ``dotted name'' that may
    # resolve either to ... a test case class"
    eleza test_loadTestsFromName__relative_TestCase_subclass(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('testcase_1', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [MyTestCase('test')])

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    eleza test_loadTestsFromName__relative_TestSuite(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testsuite = unittest.TestSuite([MyTestCase('test')])

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('testsuite', m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [MyTestCase('test')])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a test method within a test case class"
    eleza test_loadTestsFromName__relative_testmethod(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('testcase_1.test', m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [MyTestCase('test')])

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # Does loadTestsFromName() raise the proper exception when trying to
    # resolve "a test method within a test case class" that doesn't exist
    # for the given name (relative to a provided module)?
    eleza test_loadTestsFromName__relative_invalid_testmethod(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('testcase_1.testfoo', m)
        expected = "type object 'MyTestCase' has no attribute 'testfoo'"
        error, test = self.check_deferred_error(loader, suite)
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.testfoo)

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a ... TestSuite instance"
    eleza test_loadTestsFromName__callable__TestSuite(self):
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: None)
        testcase_2 = unittest.FunctionTestCase(lambda: None)
        eleza return_TestSuite():
            rudisha unittest.TestSuite([testcase_1, testcase_2])
        m.return_TestSuite = return_TestSuite

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('return_TestSuite', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1, testcase_2])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase ... instance"
    eleza test_loadTestsFromName__callable__TestCase_instance(self):
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: None)
        eleza return_TestCase():
            rudisha testcase_1
        m.return_TestCase = return_TestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('return_TestCase', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase ... instance"
    #*****************************************************************
    #Override the suiteClass attribute to ensure that the suiteClass
    #attribute is used
    eleza test_loadTestsFromName__callable__TestCase_instance_ProperSuiteClass(self):
        kundi SubTestSuite(unittest.TestSuite):
            pass
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: None)
        eleza return_TestCase():
            rudisha testcase_1
        m.return_TestCase = return_TestCase

        loader = unittest.TestLoader()
        loader.suiteClass = SubTestSuite
        suite = loader.loadTestsFromName('return_TestCase', m)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [testcase_1])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a test method within a test case class"
    #*****************************************************************
    #Override the suiteClass attribute to ensure that the suiteClass
    #attribute is used
    eleza test_loadTestsFromName__relative_testmethod_ProperSuiteClass(self):
        kundi SubTestSuite(unittest.TestSuite):
            pass
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        loader.suiteClass=SubTestSuite
        suite = loader.loadTestsFromName('testcase_1.test', m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [MyTestCase('test')])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase or TestSuite instance"
    #
    # What happens ikiwa the callable returns something else?
    eleza test_loadTestsFromName__callable__wrong_type(self):
        m = types.ModuleType('m')
        eleza return_wrong():
            rudisha 6
        m.return_wrong = return_wrong

        loader = unittest.TestLoader()
        try:
            suite = loader.loadTestsFromName('return_wrong', m)
        except TypeError:
            pass
        else:
            self.fail("TestLoader.loadTestsFromName failed to raise TypeError")

    # "The specifier can refer to modules and packages which have not been
    # imported; they will be imported as a side-effect"
    eleza test_loadTestsFromName__module_not_loaded(self):
        # We're going to try to load this module as a side-effect, so it
        # better not be loaded before we try.
        #
        module_name = 'unittest.test.dummy'
        sys.modules.pop(module_name, None)

        loader = unittest.TestLoader()
        try:
            suite = loader.loadTestsFromName(module_name)

            self.assertIsInstance(suite, loader.suiteClass)
            self.assertEqual(list(suite), [])

            # module should now be loaded, thanks to loadTestsFromName()
            self.assertIn(module_name, sys.modules)
        finally:
            ikiwa module_name in sys.modules:
                del sys.modules[module_name]

    ################################################################
    ### Tests for TestLoader.loadTestsFromName()

    ### Tests for TestLoader.loadTestsFromNames()
    ################################################################

    eleza check_deferred_error(self, loader, suite):
        """Helper function for checking that errors in loading are reported.

        :param loader: A loader with some errors.
        :param suite: A suite that should have a late bound error.
        :return: The first error message kutoka the loader and the test object
            kutoka the suite.
        """
        self.assertIsInstance(suite, unittest.TestSuite)
        self.assertEqual(suite.countTestCases(), 1)
        # Errors loading the suite are also captured for introspection.
        self.assertNotEqual([], loader.errors)
        self.assertEqual(1, len(loader.errors))
        error = loader.errors[0]
        test = list(suite)[0]
        rudisha error, test

    # "Similar to loadTestsFromName(), but takes a sequence of names rather
    # than a single name."
    #
    # What happens ikiwa that sequence of names is empty?
    eleza test_loadTestsFromNames__empty_name_list(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames([])
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    # "Similar to loadTestsFromName(), but takes a sequence of names rather
    # than a single name."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens ikiwa that sequence of names is empty?
    #
    # XXX Should this raise a ValueError or just rudisha an empty TestSuite?
    eleza test_loadTestsFromNames__relative_empty_name_list(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames([], unittest)
        self.assertIsInstance(suite, loader.suiteClass)
        self.assertEqual(list(suite), [])

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # Is ValueError raised in response to an empty name?
    eleza test_loadTestsFromNames__empty_name(self):
        loader = unittest.TestLoader()

        try:
            loader.loadTestsFromNames([''])
        except ValueError as e:
            self.assertEqual(str(e), "Empty module name")
        else:
            self.fail("TestLoader.loadTestsFromNames failed to raise ValueError")

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # What happens when presented with an impossible module name?
    eleza test_loadTestsFromNames__malformed_name(self):
        loader = unittest.TestLoader()

        # XXX Should this raise ValueError or ImportError?
        suite = loader.loadTestsFromNames(['abc () //'])
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "Failed to agiza test module: abc () //"
        expected_regex = r"Failed to agiza test module: abc \(\) //"
        self.assertIn(
            expected,  error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(
            ImportError, expected_regex, getattr(test, 'abc () //'))

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # What happens when no module can be found for the given name?
    eleza test_loadTestsFromNames__unknown_module_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames(['sdasfasfasdf'])
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "Failed to agiza test module: sdasfasfasdf"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(ImportError, expected, test.sdasfasfasdf)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # What happens when the module can be found, but not the attribute?
    eleza test_loadTestsFromNames__unknown_attr_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames(
            ['unittest.loader.sdasfasfasdf', 'unittest.test.dummy'])
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "module 'unittest.loader' has no attribute 'sdasfasfasdf'"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens when given an unknown attribute on a specified `module`
    # argument?
    eleza test_loadTestsFromNames__unknown_name_relative_1(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames(['sdasfasfasdf'], unittest)
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "module 'unittest' has no attribute 'sdasfasfasdf'"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # Do unknown attributes (relative to a provided module) still raise an
    # exception even in the presence of valid attribute names?
    eleza test_loadTestsFromNames__unknown_name_relative_2(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames(['TestCase', 'sdasfasfasdf'], unittest)
        error, test = self.check_deferred_error(loader, list(suite)[1])
        expected = "module 'unittest' has no attribute 'sdasfasfasdf'"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.sdasfasfasdf)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens when faced with the empty string?
    #
    # XXX This currently raises AttributeError, though ValueError is probably
    # more appropriate
    eleza test_loadTestsFromNames__relative_empty_name(self):
        loader = unittest.TestLoader()

        suite = loader.loadTestsFromNames([''], unittest)
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "has no attribute ''"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, getattr(test, ''))

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    # ...
    # "The method optionally resolves name relative to the given module"
    #
    # What happens when presented with an impossible attribute name?
    eleza test_loadTestsFromNames__relative_malformed_name(self):
        loader = unittest.TestLoader()

        # XXX Should this raise AttributeError or ValueError?
        suite = loader.loadTestsFromNames(['abc () //'], unittest)
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "module 'unittest' has no attribute 'abc () //'"
        expected_regex = r"module 'unittest' has no attribute 'abc \(\) //'"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(
            AttributeError, expected_regex, getattr(test, 'abc () //'))

    # "The method optionally resolves name relative to the given module"
    #
    # Does loadTestsFromNames() make sure the provided `module` is in fact
    # a module?
    #
    # XXX This validation is currently not done. This flexibility should
    # either be documented or a TypeError should be raised.
    eleza test_loadTestsFromNames__relative_not_a_module(self):
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass

        kundi NotAModule(object):
            test_2 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['test_2'], NotAModule)

        reference = [unittest.TestSuite([MyTestCase('test')])]
        self.assertEqual(list(suite), reference)

    # "The specifier name is a ``dotted name'' that may resolve either to
    # a module, a test case class, a TestSuite instance, a test method
    # within a test case class, or a callable object which returns a
    # TestCase or TestSuite instance."
    #
    # Does it raise an exception ikiwa the name resolves to an invalid
    # object?
    eleza test_loadTestsFromNames__relative_bad_object(self):
        m = types.ModuleType('m')
        m.testcase_1 = object()

        loader = unittest.TestLoader()
        try:
            loader.loadTestsFromNames(['testcase_1'], m)
        except TypeError:
            pass
        else:
            self.fail("Should have raised TypeError")

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a test case class"
    eleza test_loadTestsFromNames__relative_TestCase_subclass(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        expected = loader.suiteClass([MyTestCase('test')])
        self.assertEqual(list(suite), [expected])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a TestSuite instance"
    eleza test_loadTestsFromNames__relative_TestSuite(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testsuite = unittest.TestSuite([MyTestCase('test')])

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testsuite'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        self.assertEqual(list(suite), [m.testsuite])

    # "The specifier name is a ``dotted name'' that may resolve ... to ... a
    # test method within a test case class"
    eleza test_loadTestsFromNames__relative_testmethod(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1.test'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        ref_suite = unittest.TestSuite([MyTestCase('test')])
        self.assertEqual(list(suite), [ref_suite])

    # #14971: Make sure the dotted name resolution works even ikiwa the actual
    # function doesn't have the same name as is used to find it.
    eleza test_loadTestsFromName__function_with_different_name_than_method(self):
        # lambdas have the name '<lambda>'.
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            test = lambda: 1
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1.test'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        ref_suite = unittest.TestSuite([MyTestCase('test')])
        self.assertEqual(list(suite), [ref_suite])

    # "The specifier name is a ``dotted name'' that may resolve ... to ... a
    # test method within a test case class"
    #
    # Does the method gracefully handle names that initially look like they
    # resolve to "a test method within a test case class" but don't?
    eleza test_loadTestsFromNames__relative_invalid_testmethod(self):
        m = types.ModuleType('m')
        kundi MyTestCase(unittest.TestCase):
            eleza test(self):
                pass
        m.testcase_1 = MyTestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['testcase_1.testfoo'], m)
        error, test = self.check_deferred_error(loader, list(suite)[0])
        expected = "type object 'MyTestCase' has no attribute 'testfoo'"
        self.assertIn(
            expected, error,
            'missing error string in %r' % error)
        self.assertRaisesRegex(AttributeError, expected, test.testfoo)

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a ... TestSuite instance"
    eleza test_loadTestsFromNames__callable__TestSuite(self):
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: None)
        testcase_2 = unittest.FunctionTestCase(lambda: None)
        eleza return_TestSuite():
            rudisha unittest.TestSuite([testcase_1, testcase_2])
        m.return_TestSuite = return_TestSuite

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['return_TestSuite'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        expected = unittest.TestSuite([testcase_1, testcase_2])
        self.assertEqual(list(suite), [expected])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase ... instance"
    eleza test_loadTestsFromNames__callable__TestCase_instance(self):
        m = types.ModuleType('m')
        testcase_1 = unittest.FunctionTestCase(lambda: None)
        eleza return_TestCase():
            rudisha testcase_1
        m.return_TestCase = return_TestCase

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['return_TestCase'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        ref_suite = unittest.TestSuite([testcase_1])
        self.assertEqual(list(suite), [ref_suite])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase or TestSuite instance"
    #
    # Are staticmethods handled correctly?
    eleza test_loadTestsFromNames__callable__call_staticmethod(self):
        m = types.ModuleType('m')
        kundi Test1(unittest.TestCase):
            eleza test(self):
                pass

        testcase_1 = Test1('test')
        kundi Foo(unittest.TestCase):
            @staticmethod
            eleza foo():
                rudisha testcase_1
        m.Foo = Foo

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(['Foo.foo'], m)
        self.assertIsInstance(suite, loader.suiteClass)

        ref_suite = unittest.TestSuite([testcase_1])
        self.assertEqual(list(suite), [ref_suite])

    # "The specifier name is a ``dotted name'' that may resolve ... to
    # ... a callable object which returns a TestCase or TestSuite instance"
    #
    # What happens when the callable returns something else?
    eleza test_loadTestsFromNames__callable__wrong_type(self):
        m = types.ModuleType('m')
        eleza return_wrong():
            rudisha 6
        m.return_wrong = return_wrong

        loader = unittest.TestLoader()
        try:
            suite = loader.loadTestsFromNames(['return_wrong'], m)
        except TypeError:
            pass
        else:
            self.fail("TestLoader.loadTestsFromNames failed to raise TypeError")

    # "The specifier can refer to modules and packages which have not been
    # imported; they will be imported as a side-effect"
    eleza test_loadTestsFromNames__module_not_loaded(self):
        # We're going to try to load this module as a side-effect, so it
        # better not be loaded before we try.
        #
        module_name = 'unittest.test.dummy'
        sys.modules.pop(module_name, None)

        loader = unittest.TestLoader()
        try:
            suite = loader.loadTestsFromNames([module_name])

            self.assertIsInstance(suite, loader.suiteClass)
            self.assertEqual(list(suite), [unittest.TestSuite()])

            # module should now be loaded, thanks to loadTestsFromName()
            self.assertIn(module_name, sys.modules)
        finally:
            ikiwa module_name in sys.modules:
                del sys.modules[module_name]

    ################################################################
    ### /Tests for TestLoader.loadTestsFromNames()

    ### Tests for TestLoader.getTestCaseNames()
    ################################################################

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # Test.foobar is defined to make sure getTestCaseNames() respects
    # loader.testMethodPrefix
    eleza test_getTestCaseNames(self):
        kundi Test(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foobar(self): pass

        loader = unittest.TestLoader()

        self.assertEqual(loader.getTestCaseNames(Test), ['test_1', 'test_2'])

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # Does getTestCaseNames() behave appropriately ikiwa no tests are found?
    eleza test_getTestCaseNames__no_tests(self):
        kundi Test(unittest.TestCase):
            eleza foobar(self): pass

        loader = unittest.TestLoader()

        self.assertEqual(loader.getTestCaseNames(Test), [])

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # Are not-TestCases handled gracefully?
    #
    # XXX This should raise a TypeError, not rudisha a list
    #
    # XXX It's too late in the 2.5 release cycle to fix this, but it should
    # probably be revisited for 2.6
    eleza test_getTestCaseNames__not_a_TestCase(self):
        kundi BadCase(int):
            eleza test_foo(self):
                pass

        loader = unittest.TestLoader()
        names = loader.getTestCaseNames(BadCase)

        self.assertEqual(names, ['test_foo'])

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # Make sure inherited names are handled.
    #
    # TestP.foobar is defined to make sure getTestCaseNames() respects
    # loader.testMethodPrefix
    eleza test_getTestCaseNames__inheritance(self):
        kundi TestP(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foobar(self): pass

        kundi TestC(TestP):
            eleza test_1(self): pass
            eleza test_3(self): pass

        loader = unittest.TestLoader()

        names = ['test_1', 'test_2', 'test_3']
        self.assertEqual(loader.getTestCaseNames(TestC), names)

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # If TestLoader.testNamePatterns is set, only tests that match one of these
    # patterns should be included.
    eleza test_getTestCaseNames__testNamePatterns(self):
        kundi MyTest(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foobar(self): pass

        loader = unittest.TestLoader()

        loader.testNamePatterns = []
        self.assertEqual(loader.getTestCaseNames(MyTest), [])

        loader.testNamePatterns = ['*1']
        self.assertEqual(loader.getTestCaseNames(MyTest), ['test_1'])

        loader.testNamePatterns = ['*1', '*2']
        self.assertEqual(loader.getTestCaseNames(MyTest), ['test_1', 'test_2'])

        loader.testNamePatterns = ['*My*']
        self.assertEqual(loader.getTestCaseNames(MyTest), ['test_1', 'test_2'])

        loader.testNamePatterns = ['*my*']
        self.assertEqual(loader.getTestCaseNames(MyTest), [])

    # "Return a sorted sequence of method names found within testCaseClass"
    #
    # If TestLoader.testNamePatterns is set, only tests that match one of these
    # patterns should be included.
    #
    # For backwards compatibility reasons (see bpo-32071), the check may only
    # touch a TestCase's attribute ikiwa it starts with the test method prefix.
    eleza test_getTestCaseNames__testNamePatterns__attribute_access_regression(self):
        kundi Trap:
            eleza __get__(*ignored):
                self.fail('Non-test attribute accessed')

        kundi MyTest(unittest.TestCase):
            eleza test_1(self): pass
            foobar = Trap()

        loader = unittest.TestLoader()
        self.assertEqual(loader.getTestCaseNames(MyTest), ['test_1'])

        loader = unittest.TestLoader()
        loader.testNamePatterns = []
        self.assertEqual(loader.getTestCaseNames(MyTest), [])

    ################################################################
    ### /Tests for TestLoader.getTestCaseNames()

    ### Tests for TestLoader.testMethodPrefix
    ################################################################

    # "String giving the prefix of method names which will be interpreted as
    # test methods"
    #
    # Implicit in the documentation is that testMethodPrefix is respected by
    # all loadTestsFrom* methods.
    eleza test_testMethodPrefix__loadTestsFromTestCase(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass

        tests_1 = unittest.TestSuite([Foo('foo_bar')])
        tests_2 = unittest.TestSuite([Foo('test_1'), Foo('test_2')])

        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests_1)

        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests_2)

    # "String giving the prefix of method names which will be interpreted as
    # test methods"
    #
    # Implicit in the documentation is that testMethodPrefix is respected by
    # all loadTestsFrom* methods.
    eleza test_testMethodPrefix__loadTestsFromModule(self):
        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass
        m.Foo = Foo

        tests_1 = [unittest.TestSuite([Foo('foo_bar')])]
        tests_2 = [unittest.TestSuite([Foo('test_1'), Foo('test_2')])]

        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests_1)

        loader.testMethodPrefix = 'test'
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests_2)

    # "String giving the prefix of method names which will be interpreted as
    # test methods"
    #
    # Implicit in the documentation is that testMethodPrefix is respected by
    # all loadTestsFrom* methods.
    eleza test_testMethodPrefix__loadTestsFromName(self):
        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass
        m.Foo = Foo

        tests_1 = unittest.TestSuite([Foo('foo_bar')])
        tests_2 = unittest.TestSuite([Foo('test_1'), Foo('test_2')])

        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests_1)

        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests_2)

    # "String giving the prefix of method names which will be interpreted as
    # test methods"
    #
    # Implicit in the documentation is that testMethodPrefix is respected by
    # all loadTestsFrom* methods.
    eleza test_testMethodPrefix__loadTestsFromNames(self):
        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass
        m.Foo = Foo

        tests_1 = unittest.TestSuite([unittest.TestSuite([Foo('foo_bar')])])
        tests_2 = unittest.TestSuite([Foo('test_1'), Foo('test_2')])
        tests_2 = unittest.TestSuite([tests_2])

        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'foo'
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests_1)

        loader.testMethodPrefix = 'test'
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests_2)

    # "The default value is 'test'"
    eleza test_testMethodPrefix__default_value(self):
        loader = unittest.TestLoader()
        self.assertEqual(loader.testMethodPrefix, 'test')

    ################################################################
    ### /Tests for TestLoader.testMethodPrefix

    ### Tests for TestLoader.sortTestMethodsUsing
    ################################################################

    # "Function to be used to compare method names when sorting them in
    # getTestCaseNames() and all the loadTestsFromX() methods"
    eleza test_sortTestMethodsUsing__loadTestsFromTestCase(self):
        eleza reversed_cmp(x, y):
            rudisha -((x > y) - (x < y))

        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        tests = loader.suiteClass([Foo('test_2'), Foo('test_1')])
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    # "Function to be used to compare method names when sorting them in
    # getTestCaseNames() and all the loadTestsFromX() methods"
    eleza test_sortTestMethodsUsing__loadTestsFromModule(self):
        eleza reversed_cmp(x, y):
            rudisha -((x > y) - (x < y))

        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
        m.Foo = Foo

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        tests = [loader.suiteClass([Foo('test_2'), Foo('test_1')])]
        self.assertEqual(list(loader.loadTestsFromModule(m)), tests)

    # "Function to be used to compare method names when sorting them in
    # getTestCaseNames() and all the loadTestsFromX() methods"
    eleza test_sortTestMethodsUsing__loadTestsFromName(self):
        eleza reversed_cmp(x, y):
            rudisha -((x > y) - (x < y))

        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
        m.Foo = Foo

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        tests = loader.suiteClass([Foo('test_2'), Foo('test_1')])
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests)

    # "Function to be used to compare method names when sorting them in
    # getTestCaseNames() and all the loadTestsFromX() methods"
    eleza test_sortTestMethodsUsing__loadTestsFromNames(self):
        eleza reversed_cmp(x, y):
            rudisha -((x > y) - (x < y))

        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
        m.Foo = Foo

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        tests = [loader.suiteClass([Foo('test_2'), Foo('test_1')])]
        self.assertEqual(list(loader.loadTestsFromNames(['Foo'], m)), tests)

    # "Function to be used to compare method names when sorting them in
    # getTestCaseNames()"
    #
    # Does it actually affect getTestCaseNames()?
    eleza test_sortTestMethodsUsing__getTestCaseNames(self):
        eleza reversed_cmp(x, y):
            rudisha -((x > y) - (x < y))

        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = reversed_cmp

        test_names = ['test_2', 'test_1']
        self.assertEqual(loader.getTestCaseNames(Foo), test_names)

    # "The default value is the built-in cmp() function"
    # Since cmp is now defunct, we simply verify that the results
    # occur in the same order as they would with the default sort.
    eleza test_sortTestMethodsUsing__default_value(self):
        loader = unittest.TestLoader()

        kundi Foo(unittest.TestCase):
            eleza test_2(self): pass
            eleza test_3(self): pass
            eleza test_1(self): pass

        test_names = ['test_2', 'test_3', 'test_1']
        self.assertEqual(loader.getTestCaseNames(Foo), sorted(test_names))


    # "it can be set to None to disable the sort."
    #
    # XXX How is this different kutoka reassigning cmp? Are the tests returned
    # in a random order or something? This behaviour should die
    eleza test_sortTestMethodsUsing__None(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass

        loader = unittest.TestLoader()
        loader.sortTestMethodsUsing = None

        test_names = ['test_2', 'test_1']
        self.assertEqual(set(loader.getTestCaseNames(Foo)), set(test_names))

    ################################################################
    ### /Tests for TestLoader.sortTestMethodsUsing

    ### Tests for TestLoader.suiteClass
    ################################################################

    # "Callable object that constructs a test suite kutoka a list of tests."
    eleza test_suiteClass__loadTestsFromTestCase(self):
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass

        tests = [Foo('test_1'), Foo('test_2')]

        loader = unittest.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromTestCase(Foo), tests)

    # It is implicit in the documentation for TestLoader.suiteClass that
    # all TestLoader.loadTestsFrom* methods respect it. Let's make sure
    eleza test_suiteClass__loadTestsFromModule(self):
        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass
        m.Foo = Foo

        tests = [[Foo('test_1'), Foo('test_2')]]

        loader = unittest.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromModule(m), tests)

    # It is implicit in the documentation for TestLoader.suiteClass that
    # all TestLoader.loadTestsFrom* methods respect it. Let's make sure
    eleza test_suiteClass__loadTestsFromName(self):
        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass
        m.Foo = Foo

        tests = [Foo('test_1'), Foo('test_2')]

        loader = unittest.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromName('Foo', m), tests)

    # It is implicit in the documentation for TestLoader.suiteClass that
    # all TestLoader.loadTestsFrom* methods respect it. Let's make sure
    eleza test_suiteClass__loadTestsFromNames(self):
        m = types.ModuleType('m')
        kundi Foo(unittest.TestCase):
            eleza test_1(self): pass
            eleza test_2(self): pass
            eleza foo_bar(self): pass
        m.Foo = Foo

        tests = [[Foo('test_1'), Foo('test_2')]]

        loader = unittest.TestLoader()
        loader.suiteClass = list
        self.assertEqual(loader.loadTestsFromNames(['Foo'], m), tests)

    # "The default value is the TestSuite class"
    eleza test_suiteClass__default_value(self):
        loader = unittest.TestLoader()
        self.assertIs(loader.suiteClass, unittest.TestSuite)


    eleza test_partial_functions(self):
        eleza noop(arg):
            pass

        kundi Foo(unittest.TestCase):
            pass

        setattr(Foo, 'test_partial', functools.partial(noop, None))

        loader = unittest.TestLoader()

        test_names = ['test_partial']
        self.assertEqual(loader.getTestCaseNames(Foo), test_names)


ikiwa __name__ == "__main__":
    unittest.main()
